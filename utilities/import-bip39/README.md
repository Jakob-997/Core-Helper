# Import BIP39

Imports an English BIP39 mnemonic into an existing blank Bitcoin Core 32.x descriptor wallet.

## Run

```bash
python3 utilities/import-bip39/import_bip39.py
```

The utility:

- accepts the mnemonic and optional BIP39 passphrase through hidden terminal input
- validates the official BIP39 English wordlist and checksum
- performs the BIP39 seed conversion and BIP32 master-key step
- passes the master xprv to Bitcoin Core through `bitcoin-cli -stdin`
- lets Bitcoin Core create its standard legacy, nested SegWit, native SegWit, and Taproot descriptors
- displays a terminal QR of the mnemonic words after import
- never includes the optional BIP39 passphrase in the QR
- does not intentionally write the mnemonic, passphrase, seed, or xprv to disk or place them in command-line arguments
- does not automatically rescan the blockchain

The bundled `bip39_english.txt` is the official BIP39 English wordlist.

The BIP39/BIP32 conversion uses only Python's standard library. QR rendering uses the Python `qrcode` module (`python3-qrcode` on Debian/Tails).

References: BIP39, BIP32, and Bitcoin Core 32.x `addhdkey` / `createwalletdescriptor` RPCs.
