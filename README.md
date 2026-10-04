# Core Helper

A collection of small, independent helper utilities for Bitcoin Core, optimized for security, simplicity, and auditability.

## Utilities

- `utilities/export-account-xpub/` — export standard account-level extended public keys from a loaded Bitcoin Core wallet.
- `utilities/import-bip39/` — import an English BIP39 mnemonic into a blank Bitcoin Core descriptor wallet.\n- `utilities/core-multisig-signer/` — turn a blank Bitcoin Core 32.x wallet into one BIP87 multisig signer.

Each utility is self-contained in its own folder with its own README and dependencies.


## Templates

- `templates/corevault-three-layer/` — reusable three-layer scaffold extracted from CoreVault: minimal Core generator, Tails launcher, and separate pre/post procedure + review docs.

CoreVault remains the reference implementation. New utilities should start from the template; CoreVault does not need to be rebased when the template evolves.
