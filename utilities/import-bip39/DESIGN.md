# Import BIP39 - Design

This utility is a downstream Bitcoin Core Feature Overlay derived from the canonical scaffold identified in `UPSTREAM.md`.

## Goal

Fill one narrow workflow gap: Bitcoin Core does not accept BIP39 words directly as wallet seed input, while Core 32.x provides the wallet RPCs needed once a BIP32 master key exists.

The overlay implements only:

- BIP39 English mnemonic checksum validation;
- BIP39 PBKDF2-HMAC-SHA512 seed conversion;
- BIP32 master-key HMAC and xprv serialization;
- orchestration of existing Bitcoin Core wallet RPCs.

Bitcoin Core remains responsible for the wallet, child derivation, descriptors, addresses, key storage, and signing.

## Trust boundaries

`generator.py` uses only the Python standard library and the absolute path to the verified `bitcoin-cli` supplied by the launcher.

Private material handled there includes the mnemonic, optional BIP39 passphrase, BIP39 seed, BIP32 master xprv, and optional Core wallet-encryption passphrase. None is written to the QR output. Sensitive RPC values use Bitcoin Core stdin mechanisms rather than argv.

Python does not provide guaranteed secure memory erasure. `del` shortens ordinary object lifetime but is not claimed as memory wiping. The primary mitigation is short secret lifetime and process separation.

The launcher pins Bitcoin Core 32.0rc2 x86_64 Linux with SHA-256:

`0255103718033e6aee15fa944717fc277e047b845bff1e7408af0ea732d8d0c1`

It disables NetworkManager networking, refuses an existing Core process, verifies the archive, extracts Core into fresh `/dev/shm`, uses a fresh HOME, refuses output reuse, starts Core with `-networkactive=0 -listen=0`, and stops Core before QR rendering.

`render_qr.py` runs as a separate process after `generator.py` exits and Core is stopped. Its input contains only public wallet metadata and descriptors, so the optional third-party `qrcode` dependency is outside the secret-handling process.

## Descriptor policy

The importer asks Core to create standard receive/change descriptors for legacy/BIP44, nested SegWit/BIP49, native SegWit/BIP84, and Taproot/BIP86.

The master xpub returned by `addhdkey` is passed explicitly as `hdkey` to `createwalletdescriptor`, anchoring every descriptor family to the imported master identity.

## Maintenance

Keep the generator small and stable. Put OS/runtime changes in the launcher, public QR behavior in `render_qr.py`, and human procedure in the guides. Review any BIP39/BIP32 logic change as cryptographic code, and never change the Core pin without testing that exact build.
