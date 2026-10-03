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

