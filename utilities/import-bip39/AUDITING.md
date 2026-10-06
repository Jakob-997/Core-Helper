# Auditing Import BIP39

This is review guidance, not evidence of a completed independent audit.

Record the exact Core Helper commit, generator/launcher/renderer/wordlist blob hashes, canonical Feature Overlay commit, Core release/archive hash, Tails version, and hardware used for testing.

Review the generator for BIP39 word/checksum validation, NFKD normalization, PBKDF2-HMAC-SHA512 parameters, BIP32 master HMAC and serialization, secp256k1 scalar validity, Base58Check, wallet postconditions, stdin secret handling, `addhdkey`, explicit master-xpub use in `createwalletdescriptor`, encrypted-wallet relocking, and absence of secret output.

Run published BIP39 and BIP32 test vectors.

Review the launcher for exact archive verification, no downloads, checked network shutdown, refusal of existing Core processes, fresh `/dev/shm` state, absolute verified binary paths, output collision refusal, `-networkactive=0 -listen=0`, cleanup, and Core shutdown before QR rendering.

Confirm `generator.py` imports only standard-library modules. Confirm `render_qr.py` starts only after the generator exits and receives public descriptors only.

For end-to-end recovery, use regtest or disposable funds: import a known mnemonic, compare addresses with an independent implementation, receive/spend, destroy the generated wallet, recreate it from the seed/passphrase, and verify the same descriptors and spending ability. Record observed results in `AUDIT.md`.
