# Import BIP39 - Audit Record

## Provenance

Canonical Bitcoin Core Feature Overlay revision:

`632648b88cdb867ab6372e2850e8a53d00f58552`

## Current dependency pin

- Bitcoin Core release: `32.0rc2`
- platform: Linux x86_64
- archive: `bitcoin-32.0rc2-x86_64-linux-gnu.tar.gz`
- SHA-256: `0255103718033e6aee15fa944717fc277e047b845bff1e7408af0ea732d8d0c1`

## 2026-10-06 architecture hardening

This revision migrates the importer from a direct standalone script to the Feature Overlay architecture, preserves the existing BIP39/BIP32 conversion logic, moves Core verification/offline runtime setup into the launcher, makes the generator standard-library-only, removes `qrcode` from the secret-handling process, moves QR rendering after generator exit and Core shutdown, and retires the old direct entry point.

Static checks performed during this change:

- Python syntax parsing for the new Python files;
- BIP39 PBKDF2 conversion checked against the standard `abandon ... about` / `TREZOR` vector.

Not yet claimed:

- no independent third-party security audit has been completed for this revision;
- no full Tails + pinned Core end-to-end test is recorded here yet;
- no disposable-funds recovery test is recorded here yet;
- no claim of secure Python memory erasure is made.

Complete `AUDITING.md` and record exact revisions/results here before describing this as production-audited cold-storage software.
