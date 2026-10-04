# Core Helper

A collection of small, independent helper utilities for Bitcoin Core, optimized for security, simplicity, and auditability.

## Utilities

- `utilities/export-account-xpub/` — export standard account-level extended public keys from a loaded Bitcoin Core wallet.
- `utilities/import-bip39/` — import an English BIP39 mnemonic into a blank Bitcoin Core descriptor wallet.
- `utilities/core-multisig-signer/` — turn a blank Bitcoin Core 32.x wallet into one BIP87 multisig signer.

Each utility is self-contained in its own folder with its own README and dependencies.

## Bitcoin Core Overlay Scaffold

`templates/bitcoin-core-overlay-scaffold/` is the recommended starting point for new security-sensitive Core Helper utilities.

The idea is to add capabilities **around Bitcoin Core, not inside a large custom wallet stack**:

1. **Generator** — the smallest possible Bitcoin/Core logic.
2. **Launcher** — OS isolation, verified Core selection, runtime setup and cleanup.
3. **Procedure/docs** — preparation, backup, recovery, verification, and testing.

The pattern is designed to keep custom code minimized, responsibilities separated, and exact review targets easy to audit. Bitcoin Core remains responsible for Bitcoin primitives wherever possible.

CoreVault was the first reference implementation this architecture was extracted from, but the reusable pattern is now called the **Bitcoin Core Overlay Scaffold**. CoreVault does not need to be rebased as the scaffold evolves.
