# Import BIP39

Imports an English BIP39 mnemonic into a new Bitcoin Core 32.x descriptor wallet.

## Run

```bash
python3 utilities/import-bip39/import_bip39.py
```

No wallet setup is required beforehand. The utility creates and loads the blank descriptor wallet itself.

The flow is:

1. choose a wallet name
2. optionally enter a Bitcoin Core wallet-encryption passphrase
3. enter the BIP39 mnemonic
4. optionally enter the BIP39 passphrase
5. validate the BIP39 words and checksum
6. derive the BIP32 master xprv
7. create a blank descriptor wallet with private keys enabled
8. if encrypted, unlock it briefly
9. import the master key with Bitcoin Core `addhdkey`
10. pass the returned master xpub explicitly as `hdkey` when creating every descriptor
11. let Bitcoin Core create its standard legacy, nested SegWit, native SegWit, and Taproot descriptors
12. immediately lock an encrypted wallet again
13. print the public receive/change descriptors Core created
14. display each public descriptor as a terminal QR

## Security design

- the mnemonic is visible while typing so it can be reviewed and corrected
- the BIP39 passphrase and wallet-encryption passphrase use hidden terminal input
- the BIP39/BIP32 conversion uses only Python's standard library
- the helper implements only BIP39 seed conversion and the BIP32 master-key step
- Bitcoin Core performs child derivation, descriptor creation, address generation, and signing
- sensitive RPC arguments are sent through Bitcoin Core's stdin mechanisms instead of command-line arguments
- seed words and the optional BIP39 passphrase are never encoded into a QR
- the QR output contains only the public descriptors returned by Bitcoin Core
- the QR is rendered in the terminal; no QR image file or clipboard is used
- an encrypted wallet is created encrypted from the start, rather than importing the key into an unencrypted wallet and encrypting afterward
- no blockchain rescan is performed automatically

If the Bitcoin Core wallet-encryption passphrase is left blank, the new wallet is intentionally unencrypted and Bitcoin Core will store its private-key material accordingly.

The bundled `bip39_english.txt` is the official BIP39 English wordlist.

References: BIP39, BIP32, Bitcoin Core 32.x `createwallet`, `addhdkey`, `createwalletdescriptor`, `walletpassphrase`, and `walletlock`.
