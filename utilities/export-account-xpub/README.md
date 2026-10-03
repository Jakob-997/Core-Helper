# Export Account XPUB

Exports a standard account-level extended public key from a loaded Bitcoin Core 32.x wallet.

## Run

```bash
python3 utilities/export-account-xpub/export_account_xpub.py
```

Supports BIP44, BIP49, BIP84, BIP86, and BIP87 account paths. It uses Bitcoin Core's `derivehdkey` RPC with `private=false`, prints the descriptor-ready key expression, and can display it as a terminal QR.

Requirements:

- Python 3
- Bitcoin Core 32.x with `bitcoin-cli` in PATH
- a running local Bitcoin Core RPC server
- `qrencode` for QR display

The helper never requests an xprv, seed, mnemonic, or wallet passphrase, and it does not write key material to disk or use the clipboard.
