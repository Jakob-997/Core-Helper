#!/usr/bin/env python3
import getpass
import hashlib
import hmac
import json
from pathlib import Path
import subprocess
import sys
import unicodedata

BASE58 = b"123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
SECP256K1_ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
ADDRESS_TYPES = ("legacy", "p2sh-segwit", "bech32", "bech32m")
TEST_CHAINS = {"test", "testnet4", "signet", "regtest"}


def fail(message):
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(1)


def cli(args, wallet=None, secret=None):
    cmd = ["bitcoin-cli"]
    if wallet:
        cmd.append(f"-rpcwallet={wallet}")
    if secret is not None:
        cmd.append("-stdin")
    cmd += args

    try:
        result = subprocess.run(
            cmd,
            input=None if secret is None else secret + "\n",
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError:
        fail("bitcoin-cli was not found in PATH.")

    if result.returncode:
        fail(result.stderr.strip() or result.stdout.strip() or "bitcoin-cli failed.")
    return result.stdout.strip()


def rpc(args, wallet=None, secret=None):
    try:
        return json.loads(cli(args, wallet, secret))
    except json.JSONDecodeError:
        fail("Unexpected non-JSON response from bitcoin-cli.")


def core_info():
    network = rpc(["getnetworkinfo"])
    version = network.get("version")
    if not isinstance(version, int) or version // 10000 != 32:
        fail(f"This utility requires Bitcoin Core 32.x. Detected: {network.get('subversion', version)}")

    chain = rpc(["getblockchaininfo"]).get("chain")
    if chain != "main" and chain not in TEST_CHAINS:
        fail(f"Unsupported Bitcoin network: {chain}")
    return network.get("subversion", str(version)), chain


def choose_blank_wallet():
    wallets = rpc(["listwallets"])
    candidates = []

    for wallet in wallets:
        info = rpc(["getwalletinfo"], wallet)
        if info.get("descriptors") and info.get("private_keys_enabled") and info.get("blank"):
            candidates.append((wallet, info.get("unlocked_until")))

    if not candidates:
        fail("Load a blank descriptor wallet with private keys enabled, then run this utility again.")

    print("Compatible blank wallets:")
    for i, (wallet, unlocked_until) in enumerate(candidates, 1):
        print(f"  {i}. {wallet}" + (" (locked)" if unlocked_until == 0 else ""))

    while True:
        try:
            selected = candidates[int(input("Select wallet: ")) - 1]
        except (ValueError, IndexError):
            print(f"Enter a number from 1 to {len(candidates)}.")
            continue
        if selected[1] == 0:
            fail("The selected wallet is encrypted and locked. Unlock it in Bitcoin Core first.")
        return selected[0]


def load_wordlist():
    try:
        words = Path(__file__).with_name("bip39_english.txt").read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        fail(f"Could not read BIP39 wordlist: {exc}")
    if len(words) != 2048 or len(set(words)) != 2048:
        fail("The BIP39 English wordlist is invalid.")
    return words


def validate_mnemonic(raw, wordlist):
    words = unicodedata.normalize("NFKD", raw.strip()).split()
    if len(words) not in (12, 15, 18, 21, 24):
        fail("BIP39 mnemonic must contain 12, 15, 18, 21, or 24 words.")

    positions = {word: i for i, word in enumerate(wordlist)}
    try:
        bits = "".join(f"{positions[word]:011b}" for word in words)
    except KeyError as exc:
        fail(f"Not a BIP39 English word: {exc.args[0]}")

    entropy_len = len(bits) * 32 // 33
    checksum_len = len(bits) - entropy_len
    entropy = int(bits[:entropy_len], 2).to_bytes(entropy_len // 8, "big")
    checksum = f"{int.from_bytes(hashlib.sha256(entropy).digest(), 'big'):0256b}"[:checksum_len]

    if bits[entropy_len:] != checksum:
        fail("BIP39 checksum is invalid.")
    return " ".join(words)


def mnemonic_seed(mnemonic, passphrase):
    mnemonic = unicodedata.normalize("NFKD", mnemonic).encode()
    salt = ("mnemonic" + unicodedata.normalize("NFKD", passphrase)).encode()
    return hashlib.pbkdf2_hmac("sha512", mnemonic, salt, 2048, 64)


def base58check(payload):
    data = payload + hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    zeros = len(data) - len(data.lstrip(b"\0"))
    number = int.from_bytes(data, "big")
    out = bytearray()

    while number:
        number, digit = divmod(number, 58)
        out.append(BASE58[digit])

    return (BASE58[:1] * zeros + bytes(reversed(out))).decode()


def master_xprv(seed, chain):
    digest = hmac.new(b"Bitcoin seed", seed, hashlib.sha512).digest()
    key, chain_code = digest[:32], digest[32:]

    if not 0 < int.from_bytes(key, "big") < SECP256K1_ORDER:
        fail("BIP32 produced an invalid master key.")

    version = bytes.fromhex("0488ade4" if chain == "main" else "04358394")
    payload = version + b"\0" + b"\0" * 4 + b"\0" * 4 + chain_code + b"\0" + key
    return base58check(payload)


def import_into_core(wallet, xprv):
    added = rpc(["addhdkey"], wallet, secret=xprv)
    if not isinstance(added, dict) or not isinstance(added.get("xpub"), str):
        fail("Unexpected response from addhdkey.")

    for address_type in ADDRESS_TYPES:
        created = rpc(["createwalletdescriptor", address_type], wallet)
        if not isinstance(created, dict) or not isinstance(created.get("descs"), list):
            fail(f"Unexpected response from createwalletdescriptor ({address_type}).")


def main():
    print("Core Helper - Import BIP39")
    print()

    version, chain = core_info()
    print(f"Bitcoin Core: {version}")
    print(f"Network: {chain}")
    print()

    wallet = choose_blank_wallet()
    wordlist = load_wordlist()

    print()
    mnemonic = validate_mnemonic(getpass.getpass("BIP39 mnemonic (hidden): "), wordlist)
    passphrase = getpass.getpass("BIP39 passphrase (blank if none): ")

    if passphrase:
        confirm = getpass.getpass("Repeat BIP39 passphrase: ")
        if unicodedata.normalize("NFKD", passphrase) != unicodedata.normalize("NFKD", confirm):
            fail("BIP39 passphrases do not match.")

    seed = mnemonic_seed(mnemonic, passphrase)
    xprv = master_xprv(seed, chain)
    import_into_core(wallet, xprv)

    del mnemonic, passphrase, seed, xprv

    print()
    print(f"Imported into wallet: {wallet}")
    print("Created standard Core descriptors: legacy, p2sh-segwit, bech32, bech32m")
    print("No seed words, BIP39 passphrase, or xprv were written to disk or passed in argv.")
    print("Blockchain history was not rescanned.")


if __name__ == "__main__":
    main()
