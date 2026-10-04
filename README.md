# Core Helper

A collection of small, independent helper utilities for Bitcoin Core, optimized for security, simplicity, and auditability.

## Utilities

- `utilities/export-account-xpub/` — export standard account-level extended public keys from a loaded Bitcoin Core wallet.
- `utilities/import-bip39/` — import an English BIP39 mnemonic into a blank Bitcoin Core descriptor wallet.
- `utilities/core-multisig-signer/` — turn a blank Bitcoin Core 32.x wallet into one BIP87 multisig signer.

Each utility is self-contained in its own folder with its own README and dependencies.

## Bitcoin Core Feature Overlay

[Bitcoin Core Feature Overlay](https://github.com/Jakob-997/Bitcoin-Core-Feature-Overlay) is the canonical reusable pattern for implementing small Bitcoin Core features and workflows that are not yet merged upstream, without forking or modifying Bitcoin Core.

1. **Generator** — minimal feature logic using existing Core RPCs.
2. **Launcher** — OS isolation, dependencies, verified Core version enforcement, runtime setup and cleanup.
3. **Human/audit docs** — preparation, backup, recovery, testing, design assumptions and exact review records.

Bitcoin Core remains responsible for Bitcoin primitives. The overlay supplies the missing workflow and can be retired when Core provides equivalent functionality.

Start new features from the [canonical upstream repository](https://github.com/Jakob-997/Bitcoin-Core-Feature-Overlay). [`templates/bitcoin-core-feature-overlay/`](templates/bitcoin-core-feature-overlay/) is a downstream snapshot for convenience, not the canonical source. Its `UPSTREAM.md` records provenance and the update procedure. Propose reusable scaffold changes upstream and review each downstream adoption explicitly.

The architecture originated in CoreVault. Maintaining this pattern does not require modifying or rebasing CoreVault.
