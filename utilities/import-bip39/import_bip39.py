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


def load_qrcode():
    try:
        import qrcode
    except ImportError:
        fail("Python qrcode module not found. On Debian/Tails it is provided by python3-qrcode.")
    return qrcode


def cli(args, wallet=None, secret=None, wallet_passphrase=None):
    if secret is not None and wallet_passphrase is not None:
        fail("Internal error: two stdin secret modes requested.")

    cmd = ["bitcoin-cli"]
    if wallet:
        cmd.append(f"-rpcwallet={wallet}")
    if secret is not None:
        cmd.append("-stdin")
    if wallet_passphrase is not None:
        cmd.append("-stdinwalletpassphrase")
    cmd += args

    stdin_secret = secret if secret is not None else wallet_passphrase

    try:
        result = subprocess.run(
            cmd,
            input=None if stdin_secret is None else stdin_secret + "\n",
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


def get_wallet_name():
    name = input("Wallet name [bip39-import]: ").strip() or "bip39-import"
    if "/" in name or "\\" in name or name in (".", ".."):
        fail("Use a simple wallet name, not a filesystem path.")
    return name


def get_wallet_passphrase():
    passphrase = getpass.getpass(
        "Bitcoin Core wallet encryption passphrase (blank = unencrypted): "
    )
    if not passphrase:
        return ""

    confirm = getpass.getpass("Repeat Bitcoin Core wallet encryption passphrase: ")
    if passphrase != confirm:
        fail("Bitcoin Core wallet encryption passphrases do not match.")
    return passphrase


def create_blank_wallet(name, passphrase):
    args = ["createwallet", name, "false", "true"]
    created = rpc(args, secret=passphrase if passphrase else None)

    if not isinstance(created, dict) or created.get("name") != name:
        fail("Unexpected response from createwallet.")

    info = rpc(["getwalletinfo"], wallet=name)
    if not (
        info.get("descriptors")
        and info.get("private_keys_enabled")
        and info.get("blank")
    ):
        fail("Bitcoin Core did not create the expected blank descriptor wallet.")

    if passphrase:
        cli(
            ["walletpassphrase", "60"],
            wallet=name,
            wallet_passphrase=passphrase,
        )

    return name


def lock_wallet(wallet):
    cli(["walletlock"], wallet=wallet)


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


def show_mnemonic_qr(qrcode, mnemonic):
    qr = qrcode.QRCode(border=2)
    qr.add_data(mnemonic)
    qr.make(fit=True)

    sys.stdout.write("\033[?1049h\033[2J\033[H")
    sys.stdout.flush()
    try:
        print("SECRET - BIP39 mnemonic QR")
        print("This QR contains the mnemonic words only, not the BIP39 passphrase.")
        print()
        qr.print_ascii(out=sys.stdout, tty=sys.stdout.isatty())
        input("\nPress Enter to hide the QR...")
    finally:
        sys.stdout.write("\033[2J\033[H\033[?1049l")
        sys.stdout.flush()


def main():
    print("Core Helper - Import BIP39")
    print()

    version, chain = core_info()
    qrcode = load_qrcode()
    print(f"Bitcoin Core: {version}")
    print(f"Network: {chain}")
    print()

    wordlist = load_wordlist()

    print()
    wallet_name = get_wallet_name()
    wallet_passphrase = get_wallet_passphrase()
    print()

    mnemonic = validate_mnemonic(getpass.getpass("BIP39 mnemonic (hidden): "), wordlist)
    bip39_passphrase = getpass.getpass("BIP39 passphrase (blank if none): ")

    if bip39_passphrase:
        confirm = getpass.getpass("Repeat BIP39 passphrase: ")
        if unicodedata.normalize("NFKD", bip39_passphrase) != unicodedata.normalize("NFKD", confirm):
            fail("BIP39 passphrases do not match.")

    seed = mnemonic_seed(mnemonic, bip39_passphrase)
    xprv = master_xprv(seed, chain)

    wallet = create_blank_wallet(wallet_name, wallet_passphrase)
    try:
        import_into_core(wallet, xprv)
    finally:
        if wallet_passphrase:
            lock_wallet(wallet)

    show_mnemonic_qr(qrcode, mnemonic)

    del mnemonic, bip39_passphrase, wallet_passphrase, seed, xprv

    print()
    print(f"Imported into wallet: {wallet}")
    print("Created standard Core descriptors: legacy, p2sh-segwit, bech32, bech32m")
    print("No seed words, BIP39 passphrase, wallet passphrase, or xprv were passed in argv.")
    print("Blockchain history was not rescanned.")


if __name__ == "__main__":
    main()
