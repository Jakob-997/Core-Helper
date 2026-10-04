#!/bin/sh
set -eu

here=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
umask 077

if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: python3 was not found." >&2
    exit 1
fi

if ! command -v bitcoin-cli >/dev/null 2>&1; then
    echo "Error: bitcoin-cli was not found in PATH." >&2
    exit 1
fi

if ! command -v qr >/dev/null 2>&1; then
    echo "Error: qr was not found. On Tails it is provided by python3-qrcode." >&2
    exit 1
fi

if ! command -v nmcli >/dev/null 2>&1; then
    echo "Error: nmcli was not found. This launcher requires NetworkManager so it can enforce a software air gap." >&2
    exit 1
fi

nmcli networking off
if [ "$(LC_ALL=C nmcli networking)" != "disabled" ]; then
    echo "Error: failed to disable NetworkManager networking." >&2
    exit 1
fi

bitcoin_cli=$(command -v bitcoin-cli)
qr_bin=$(command -v qr)

exec python3 "$here/core_multisig_signer.py" "$bitcoin_cli" "$qr_bin"
