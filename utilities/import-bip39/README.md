# Import BIP39

A Bitcoin Core Feature Overlay for importing an English BIP39 mnemonic into a new Bitcoin Core descriptor wallet.

The utility does not patch or fork Bitcoin Core. Its generator performs only BIP39 validation/seed conversion and the BIP32 master-key step that Core does not expose from BIP39 words. Bitcoin Core then owns the wallet, child derivation, descriptor construction, address generation, storage, and signing.

## Security boundary

Run the importer through `tails.sh`, not by executing the old importer directly.

The launcher:

1. requires the pinned Bitcoin Core archive below;
2. disables NetworkManager networking and verifies that it is disabled;
3. refuses to run alongside an existing Bitcoin Core process;
4. verifies the exact Core archive SHA-256 before extraction;
5. extracts Core into fresh `/dev/shm` runtime state and invokes it by absolute path;
6. starts Core with `-networkactive=0 -listen=0`;
7. creates a fresh output directory and refuses to overwrite an old run;
8. runs a standard-library-only secret-handling generator;
9. stops Bitcoin Core and exits the generator before loading the optional `qrcode` package;
10. renders QR codes only from public descriptors.

This is defense in depth, not a physical air gap.

## Pinned Bitcoin Core

This revision is pinned to the official Linux x86_64 Bitcoin Core **32.0rc2** archive:

```text
bitcoin-32.0rc2-x86_64-linux-gnu.tar.gz
SHA256: 0255103718033e6aee15fa944717fc277e047b845bff1e7408af0ea732d8d0c1
```

Place that archive in this directory before going offline. The launcher does not download software.

## Run

```bash
chmod +x tails.sh
./tails.sh
```

The fresh output is created at `wallet-output/`. It contains the Bitcoin Core wallet directory plus `public-descriptors.json`, which contains public data only.

## Files

- `generator.py` — minimal secret-handling logic; Python standard library only.
- `launcher.py` — exact Core verification, offline state, fresh runtime, startup/shutdown.
- `tails.sh` — minimal Tails entry point.
- `render_qr.py` — public-data-only QR display process.
- `bip39_english.txt` — BIP39 English wordlist.
- `DESIGN.md`, `AUDITING.md`, `AUDIT.md` — architecture and review record.
- `PRE-CREATION-GUIDE.txt`, `POST-CREATION-GUIDE.txt` — operational procedure.
- `UPSTREAM.md` — Feature Overlay provenance.
- `import_bip39.py` — compatibility stub that refuses the retired direct workflow.

## Important limitations

Python object deletion is not guaranteed secure memory erasure. The design instead minimizes secret lifetime: the generator exits before QR code dependencies run.

The launcher cannot prove firmware, hardware, Tails media, CPU, keyboard, display, or the physical environment are trustworthy. Perform an independent recovery test before relying on the wallet.
