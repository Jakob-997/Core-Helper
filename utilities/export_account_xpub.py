#!/usr/bin/env python3
import json
import shutil
import subprocess
import sys
ACCOUNT_TYPES = [
    ("Legacy single-sig", "BIP44", 44),
    ("Nested SegWit single-sig", "BIP49", 49),
    ("Native SegWit single-sig", "BIP84", 84),
    ("Taproot single-sig", "BIP86", 86),
    ("Multisig", "BIP87", 87),
]

TEST_CHAINS = {"test", "testnet4", "signet", "regtest"}


def fail(message):
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(1)


def run_cli(args, wallet=None):
    cmd = ["bitcoin-cli"]
    if wallet is not None:
        cmd.append(f"-rpcwallet={wallet}")
    cmd.extend(args)

    try:
        result = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        fail("bitcoin-cli was not found in PATH.")

    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "bitcoin-cli failed."
        fail(message)

    return result.stdout.strip()


def rpc_json(args, wallet=None):
    out = run_cli(args, wallet=wallet)
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        fail(f"Unexpected non-JSON response from bitcoin-cli: {out}")


def choose(items, prompt):
    while True:
        raw = input(prompt).strip()
        try:
            index = int(raw)
        except ValueError:
            print("Enter a number.")
            continue

        if 1 <= index <= len(items):
            return items[index - 1]

        print(f"Enter a number from 1 to {len(items)}.")


def get_core_version():
    info = rpc_json(["getnetworkinfo"])
    subversion = info.get("subversion", "")
    version = info.get("version")

    if not isinstance(version, int):
        fail("Could not determine Bitcoin Core version.")

    major = version // 10000
    if major != 32:
        fail(f"This utility targets Bitcoin Core 32.x. Detected: {subversion or version}")

    return subversion or str(version)


def get_chain():
    info = rpc_json(["getblockchaininfo"])
    chain = info.get("chain")

    if chain == "main":
        return chain, 0
    if chain in TEST_CHAINS:
        return chain, 1

    fail(f"Unsupported Bitcoin network: {chain}")


def get_loaded_wallets():
    wallets = rpc_json(["listwallets"])
    if not isinstance(wallets, list):
        fail("Unexpected response from listwallets.")
    if not wallets:
        fail("No wallets are currently loaded in Bitcoin Core.")
    return wallets


def get_account_number():
    while True:
        raw = input("Account number [0]: ").strip()
        if raw == "":
            return 0
        try:
            account = int(raw)
        except ValueError:
            print("Enter a non-negative integer.")
            continue

        if 0 <= account < 2**31:
            return account

        print("Account must be between 0 and 2147483647.")


def derive_key(wallet, purpose, coin_type, account):
    path = f"m/{purpose}h/{coin_type}h/{account}h"

    # Explicitly request public output only.
    result = rpc_json(
        [
            "-named",
            "derivehdkey",
            f"path={path}",
            "private=false",
        ],
        wallet=wallet,
    )

    if not isinstance(result, dict):
        fail("Unexpected response from derivehdkey.")

    if "xprv" in result:
        fail("Bitcoin Core returned private key material unexpectedly. Aborting.")

    origin = result.get("origin")
    xpub = result.get("xpub")

    if not isinstance(origin, str) or not origin.startswith("[") or not origin.endswith("]"):
        fail("derivehdkey did not return a valid origin.")
    if not isinstance(xpub, str) or not xpub:
        fail("derivehdkey did not return an xpub.")

    return path, origin + xpub


def show_qr(text):
    qrencode = shutil.which("qrencode")
    if qrencode is None:
        print()
        print("QR unavailable: qrencode is not installed.")
        print("Ubuntu: sudo apt install qrencode")
        return

    print()
    print("QR code:")
    result = subprocess.run(
        [qrencode, "-t", "ANSIUTF8", text],
        check=False,
        text=True,
    )
    if result.returncode != 0:
        fail("qrencode failed.")


def main():
    print("Core Helper - Export Account XPUB")
    print()

    version = get_core_version()
    chain, coin_type = get_chain()

    print(f"Bitcoin Core: {version}")
    print(f"Network: {chain}")
    print()

    wallets = get_loaded_wallets()
    print("Loaded wallets:")
    for i, wallet in enumerate(wallets, 1):
        print(f"  {i}. {wallet}")

    wallet = choose(wallets, "Select wallet: ")
    print()

    print("Select account key type:")
    for i, (label, bip, purpose) in enumerate(ACCOUNT_TYPES, 1):
        print(f"  {i}. {label:<26} {bip}  m/{purpose}h/{coin_type}h/<account>h")

    label, bip, purpose = choose(ACCOUNT_TYPES, "Select type: ")
    account = get_account_number()

    path, key_expression = derive_key(wallet, purpose, coin_type, account)

    print()
    print(f"{label} ({bip})")
    print(f"Path: {path}")
    print()
    print("Public key expression:")
    print(key_expression)
    print()
    print("This contains public key information only.")
    print("Verify that scanned QR text exactly matches the text above.")

    show_qr(key_expression)


if __name__ == "__main__":
    main()
