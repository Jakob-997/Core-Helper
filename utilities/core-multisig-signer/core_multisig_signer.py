#!/usr/bin/env python3
import json
import re
import subprocess
import sys

TEST_CHAINS = {"test", "testnet4", "signet", "regtest"}
ACCOUNT = 0
PURPOSE = 87

KEY_RE = re.compile(
    r"^\\[([0-9a-fA-F]{8})/87(?:h|H|')/([01])(?:h|H|')/0(?:h|H|')\\]"
    r"([1-9A-HJ-NP-Za-km-z]+)/<0;1>/\\*$"
)
ORIGIN_RE = re.compile(
    r"^\\[([0-9a-fA-F]{8})/87(?:h|H|')/([01])(?:h|H|')/0(?:h|H|')\\]$"
)


class RpcError(Exception):
    pass


class DescriptorError(Exception):
    pass


def fail(message):
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(1)


def rpc(bitcoin_cli, method, *args, wallet=None, sensitive=False):
    cmd = [bitcoin_cli]
    if wallet is not None:
        cmd.append(f"-rpcwallet={wallet}")
    cmd.extend(["-stdin", method])
    stdin = "".join(f"{arg}\\n" for arg in args)

    try:
        result = subprocess.run(
            cmd,
            input=stdin,
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError:
        raise RpcError("bitcoin-cli was not found.")

    if result.returncode != 0:
        if sensitive:
            raise RpcError(
                f"{method} failed. Sensitive descriptor material was not printed."
            )
        message = result.stderr.strip() or result.stdout.strip() or f"{method} failed."
        raise RpcError(message)

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        if sensitive:
            raise RpcError(
                f"{method} returned an unexpected response. Sensitive material was not printed."
            )
        raise RpcError(f"Unexpected non-JSON response from {method}.")


def core_info(bitcoin_cli):
    network = rpc(bitcoin_cli, "getnetworkinfo")
    version = network.get("version")
    if not isinstance(version, int) or version // 10000 != 32:
        fail(
            "This utility requires Bitcoin Core 32.x. "
            f"Detected: {network.get('subversion', version)}"
        )

    chain = rpc(bitcoin_cli, "getblockchaininfo").get("chain")
    if chain == "main":
        return network.get("subversion", str(version)), chain, 0
    if chain in TEST_CHAINS:
        return network.get("subversion", str(version)), chain, 1
    fail(f"Unsupported Bitcoin network: {chain}")


def get_wallet_name():
    name = input("Signer wallet name [core-multisig-signer]: ").strip()
    name = name or "core-multisig-signer"
    if not re.fullmatch(r"[A-Za-z0-9._-]{1,64}", name) or name in {".", ".."}:
        fail("Use a simple wallet name containing only letters, numbers, '.', '_', or '-'.")
    return name


def create_blank_wallet(bitcoin_cli, wallet):
    created = rpc(bitcoin_cli, "createwallet", wallet, "false", "true")
    if not isinstance(created, dict) or created.get("name") != wallet:
        fail("Unexpected response from createwallet.")

    info = rpc(bitcoin_cli, "getwalletinfo", wallet=wallet)
    if not (
        info.get("descriptors")
        and info.get("private_keys_enabled")
        and info.get("blank")
    ):
        fail("Bitcoin Core did not create the expected blank private-key descriptor wallet.")


def add_root_and_derive_public(bitcoin_cli, wallet, coin_type):
    added = rpc(bitcoin_cli, "addhdkey", wallet=wallet)
    root_xpub = added.get("xpub") if isinstance(added, dict) else None
    if not isinstance(root_xpub, str) or not root_xpub:
        fail("Unexpected response from addhdkey.")

    path = f"m/{PURPOSE}h/{coin_type}h/{ACCOUNT}h"
    options = json.dumps(
        {"hdkey": root_xpub, "private": False},
        separators=(",", ":"),
    )
    derived = rpc(bitcoin_cli, "derivehdkey", path, options, wallet=wallet)

    if not isinstance(derived, dict) or "xprv" in derived:
        fail("Unexpected response from derivehdkey.")

    origin = derived.get("origin")
    account_xpub = derived.get("xpub")
    if not isinstance(origin, str) or not isinstance(account_xpub, str):
        fail("derivehdkey did not return the expected public key data.")

    match = ORIGIN_RE.fullmatch(origin)
    if not match or int(match.group(2)) != coin_type:
        fail("Bitcoin Core returned an unexpected BIP87 key origin.")

    expected_prefix = "xpub" if coin_type == 0 else "tpub"
    if not account_xpub.startswith(expected_prefix):
        fail("Bitcoin Core returned an extended public key for the wrong network.")

    return root_xpub, path, origin, account_xpub


def show_qr(qr_bin, text):
    print()
    print("QR code:")
    result = subprocess.run([qr_bin, "--ascii", text], check=False)
    if result.returncode != 0:
        fail("The qr command failed.")


def descriptor_body(raw):
    if raw.count("#") > 1:
        raise DescriptorError("Descriptor contains more than one checksum separator.")
    return raw.split("#", 1)[0]


def parse_policy(body, coin_type, own_origin, own_xpub):
    prefix = "wsh(sortedmulti("
    if not body.startswith(prefix) or not body.endswith("))"):
        raise DescriptorError(
            "Descriptor must be a native SegWit wsh(sortedmulti(...)) descriptor."
        )

    inner = body[len(prefix):-2]
    fields = inner.split(",")
    if len(fields) < 3:
        raise DescriptorError(
            "Descriptor must contain a threshold and at least two signer keys."
        )

    try:
        threshold = int(fields[0])
    except ValueError:
        raise DescriptorError("Invalid multisig threshold.")

    keys = fields[1:]
    if not 1 <= threshold <= len(keys):
        raise DescriptorError("Multisig threshold is outside the signer count.")
    if len(set(keys)) != len(keys):
        raise DescriptorError("Descriptor contains a duplicate signer key.")

    own_origin_match = ORIGIN_RE.fullmatch(own_origin)
    if not own_origin_match:
        fail("Internal error: unexpected signer origin.")
    own_fingerprint = own_origin_match.group(1).lower()

    expected_prefix = "xpub" if coin_type == 0 else "tpub"
    parsed = []
    for key in keys:
        match = KEY_RE.fullmatch(key)
        if not match:
            raise DescriptorError(
                "Every signer must use [fingerprint/87h/coin_typeh/0h]"
                "xpub/<0;1>/*."
            )
        fingerprint, key_coin, xpub = match.groups()
        if int(key_coin) != coin_type:
            raise DescriptorError(
                "Descriptor contains a signer from the wrong BIP87 coin type."
            )
        if not xpub.startswith(expected_prefix):
            raise DescriptorError(
                "Descriptor contains an extended public key for the wrong network."
            )
        parsed.append((fingerprint.lower(), xpub, key))

    if len({xpub for _, xpub, _ in parsed}) != len(parsed):
        raise DescriptorError("Descriptor contains a duplicate account xpub.")

    matches = [
        key
        for fingerprint, xpub, key in parsed
        if fingerprint == own_fingerprint and xpub == own_xpub
    ]
    if len(matches) != 1:
        raise DescriptorError(
            "The descriptor must contain this signer exactly once "
            "(matching fingerprint and BIP87 account xpub)."
        )

    return threshold, keys, matches[0]


def validate_public_descriptor(bitcoin_cli, raw, coin_type, own_origin, own_xpub):
    info = rpc(bitcoin_cli, "getdescriptorinfo", raw)
    if not isinstance(info, dict):
        fail("Unexpected response from getdescriptorinfo.")
    if info.get("hasprivatekeys"):
        raise DescriptorError(
            "Paste a public multisig descriptor only; private keys are not accepted."
        )
    if not info.get("isrange") or not info.get("issolvable"):
        raise DescriptorError("Descriptor must be ranged and solvable.")

    body = descriptor_body(raw)
    threshold, keys, own_key = parse_policy(
        body, coin_type, own_origin, own_xpub
    )
    return info, body, threshold, keys, own_key


def derive_private_account(
    bitcoin_cli, wallet, root_xpub, path, origin, account_xpub
):
    options = json.dumps(
        {"hdkey": root_xpub, "private": True},
        separators=(",", ":"),
    )
    derived = rpc(
        bitcoin_cli,
        "derivehdkey",
        path,
        options,
        wallet=wallet,
        sensitive=True,
    )
    if not isinstance(derived, dict):
        fail("Unexpected response from private derivehdkey.")

    if derived.get("origin") != origin or derived.get("xpub") != account_xpub:
        fail("Private derivation did not match the previously exported signer key.")

    xprv = derived.get("xprv")
    if not isinstance(xprv, str) or not xprv:
        fail("Bitcoin Core did not return the expected private account key.")
    return xprv


def import_signing_descriptor(
    bitcoin_cli,
    wallet,
    public_info,
    threshold,
    keys,
    own_key,
    account_xpub,
    xprv,
):
    private_keys = []
    replaced = 0
    for key in keys:
        if key == own_key:
            if key.count(account_xpub) != 1:
                fail("Internal error while locating the signer account xpub.")
            private_keys.append(key.replace(account_xpub, xprv, 1))
            replaced += 1
        else:
            private_keys.append(key)

    if replaced != 1:
        fail("Internal error while constructing the signing descriptor.")

    private_body = (
        "wsh(sortedmulti("
        + str(threshold)
        + ","
        + ",".join(private_keys)
        + "))"
    )

    private_info = rpc(
        bitcoin_cli,
        "getdescriptorinfo",
        private_body,
        sensitive=True,
    )
    if not isinstance(private_info, dict) or not private_info.get("hasprivatekeys"):
        fail("Bitcoin Core did not recognize the private signing descriptor.")

    if private_info.get("descriptor") != public_info.get("descriptor"):
        fail("Private-key substitution changed the public descriptor.")
    if (
        private_info.get("multipath_expansion")
        != public_info.get("multipath_expansion")
    ):
        fail("Private-key substitution changed the multipath descriptor expansion.")

    checksum = private_info.get("checksum")
    if not isinstance(checksum, str) or not checksum:
        fail("Bitcoin Core did not return a descriptor checksum.")

    private_descriptor = f"{private_body}#{checksum}"
    request = json.dumps(
        [{"desc": private_descriptor, "active": True, "timestamp": "now"}],
        separators=(",", ":"),
    )
    result = rpc(
        bitcoin_cli,
        "importdescriptors",
        request,
        wallet=wallet,
        sensitive=True,
    )

    if (
        not isinstance(result, list)
        or len(result) != 1
        or not isinstance(result[0], dict)
    ):
        fail("Unexpected response from importdescriptors.")
    if not result[0].get("success"):
        code = result[0].get("error", {}).get("code")
        suffix = f" (code {code})" if code is not None else ""
        fail(
            f"importdescriptors failed{suffix}. "
            "Sensitive descriptor material was not printed."
        )


def verify_signer(bitcoin_cli, wallet, account_xpub):
    options = json.dumps({"active_only": True}, separators=(",", ":"))
    keys = rpc(bitcoin_cli, "gethdkeys", options, wallet=wallet)
    if not isinstance(keys, list):
        fail("Unexpected response from gethdkeys.")

    private_keys = [item for item in keys if item.get("has_private") is True]
    if len(private_keys) != 1:
        fail("Expected exactly one private HD key in the active multisig descriptor.")

    own = [item for item in keys if item.get("xpub") == account_xpub]
    if len(own) != 1 or own[0].get("has_private") is not True:
        fail("Bitcoin Core does not report this BIP87 account xpub as signable.")

    descriptors = own[0].get("descriptors")
    if not isinstance(descriptors, list) or not any(
        isinstance(item, dict) and item.get("active") is True
        for item in descriptors
    ):
        fail("The signer's multisig descriptor is not active.")


def main():
    if len(sys.argv) != 3:
        fail("Run this utility through run.sh.")

    bitcoin_cli = sys.argv[1]
    qr_bin = sys.argv[2]

    print("Core Helper - Multisig Signer")
    print()

    version, chain, coin_type = core_info(bitcoin_cli)
    print(f"Bitcoin Core: {version}")
    print(f"Network: {chain}")
    print()

    wallet = get_wallet_name()
    create_blank_wallet(bitcoin_cli, wallet)
    root_xpub, path, origin, account_xpub = add_root_and_derive_public(
        bitcoin_cli, wallet, coin_type
    )
    key_expression = origin + account_xpub

    print()
    print("BIP87 multisig key:")
    print(key_expression)
    print()
    print("This is public information. Add it to the multisig quorum.")
    print("Verify that the scanned QR text exactly matches the text above.")
    show_qr(qr_bin, key_expression)

    print()
    print(
        "Build the complete public wsh(sortedmulti(...)) descriptor "
        "on the coordinator."
    )
    print("Paste it here when ready. A checksum is optional.")
    print()

    while True:
        raw = input("Public multisig descriptor: ").strip()
        if not raw:
            print("Descriptor cannot be blank.")
            continue
        try:
            public_info, _body, threshold, keys, own_key = (
                validate_public_descriptor(
                    bitcoin_cli, raw, coin_type, origin, account_xpub
                )
            )
            break
        except (DescriptorError, RpcError) as exc:
            print(f"Descriptor rejected: {exc}")
            print(
                "Try again, or press Ctrl-C to stop without importing a descriptor."
            )
            print()

    xprv = derive_private_account(
        bitcoin_cli, wallet, root_xpub, path, origin, account_xpub
    )
    try:
        import_signing_descriptor(
            bitcoin_cli,
            wallet,
            public_info,
            threshold,
            keys,
            own_key,
            account_xpub,
            xprv,
        )
    finally:
        # Python strings cannot be reliably zeroized. Keep the private value's
        # lifetime as short as practical and never print, persist, or pass it in argv.
        del xprv

    verify_signer(bitcoin_cli, wallet, account_xpub)

    print()
    print("Signer ready.")
    print(f"Wallet: {wallet}")
    print(f"BIP87 path: {path}")
    print(
        "Bitcoin Core reports exactly one private key "
        "in the active multisig descriptor."
    )
    print(
        "Back up the wallet before funding the quorum, "
        "then test with disposable funds."
    )


if __name__ == "__main__":
    try:
        main()
    except RpcError as exc:
        fail(str(exc))
