# Core Helper

Small helper utilities for Bitcoin Core, optimized for security, simplicity, and auditability.

## Export account extended public key

`utilities/export_account_xpub.py` exports a standard account-level extended public key from a loaded Bitcoin Core wallet.

It is intentionally narrow:

- uses only the local `bitcoin-cli` RPC interface for wallet/key operations
- lists loaded wallets only; it never loads, unloads, creates, or modifies wallets
- supports standard account paths for BIP44, BIP49, BIP84, BIP86, and BIP87
- uses coin type `0h` on mainnet and `1h` on testnet, testnet4, signet, and regtest
- asks for the account number instead of silently forcing account `0h`
- prints the full descriptor-ready key expression: `[fingerprint/path]xpub...`
- displays a terminal QR containing exactly that same public string
- never requests an xprv, seed, mnemonic, or wallet passphrase
- does not write keys to disk or use the clipboard
- does not use `shell=True`

The utility targets Bitcoin Core 32.x during the 32.0 release-candidate cycle.

### Requirements

- Python 3
- Bitcoin Core 32.x with `bitcoin-cli` available in `PATH`
- a running local Bitcoin Core RPC server
- `qrencode` for the terminal QR

On Ubuntu:

```bash
sudo apt install qrencode
```

If using Bitcoin Core GUI, start it with RPC server support, for example:

```bash
bitcoin-qt -server
```

### Run

```bash
python3 utilities/export_account_xpub.py
```

The helper detects the Bitcoin network, lists only currently loaded wallets, asks which wallet to use, then offers:

```text
1. Legacy single-sig          BIP44
2. Nested SegWit single-sig  BIP49
3. Native SegWit single-sig  BIP84
4. Taproot single-sig        BIP86
5. Multisig                  BIP87
```

For mainnet account 0, the corresponding account paths are:

```text
m/44h/0h/0h
m/49h/0h/0h
m/84h/0h/0h
m/86h/0h/0h
m/87h/0h/0h
```

The output is the public key expression returned by Bitcoin Core, for example:

```text
[f23a9c4e/87h/0h/0h]xpub...
```

The QR encodes exactly that string.

### Encrypted wallets

Bitcoin Core's `derivehdkey` RPC requires the wallet to be unlocked because hardened derivation uses private key material internally. This helper does **not** accept or request the wallet passphrase.

Unlock the wallet using Bitcoin Core, run the helper, then lock the wallet again as appropriate.

Only the derived extended **public** key is requested and displayed.

### BIP87 multisig account reuse

BIP87 requires the hardened account level to be incremented for each distinct multisig wallet. Do not reuse the same BIP87 account key in separate multisig wallets.

The helper therefore asks for the account number and does not keep hidden state or automatically choose the next account.

### Security design

The helper does not implement BIP32 derivation itself. Bitcoin Core 32.x performs the derivation with `derivehdkey`.

The RPC is called with `private=false` explicitly. The helper also aborts if an `xprv` field is ever returned.

Bitcoin Core decides which eligible wallet HD key to derive from. If Core cannot determine a unique HD key, `derivehdkey` fails rather than the helper guessing.

The QR encoder only receives the already-public `[fingerprint/path]xpub` string. Verify that scanned QR text exactly matches the text printed above it.


## Import BIP39 mnemonic

`utilities/import_bip39.py` imports an English BIP39 mnemonic into an existing blank Bitcoin Core 32.x descriptor wallet.

Run:

```bash
python3 utilities/import_bip39.py
```

Design:

- terminal-only hidden mnemonic/passphrase input
- validates the BIP39 English wordlist and checksum
- uses only Python's standard library for the BIP39/BIP32 conversion
- uses the `qrcode` Python module (`python3-qrcode` on Debian/Tails) only for terminal QR rendering
- converts BIP39 to the BIP32 master extended private key
- passes that key to Bitcoin Core with `bitcoin-cli -stdin`
- Core performs child derivation and creates standard legacy, nested SegWit, native SegWit, and Taproot descriptors
- no mnemonic, passphrase, seed, or private key is written to disk by the helper
- no secret is placed in command-line arguments
- displays a plain-text QR of the mnemonic words in the terminal after a successful import
- the optional BIP39 passphrase is never included in the QR
- uses the terminal alternate-screen buffer for the secret QR and hides it when Enter is pressed
- does not create a QR image file or use the clipboard
- no blockchain rescan is performed automatically

The bundled `utilities/bip39_english.txt` is the official BIP39 English wordlist.

References: BIP39, BIP32, and Bitcoin Core 32.x `addhdkey` / `createwalletdescriptor` wallet RPCs.
