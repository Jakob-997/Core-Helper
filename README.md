# Core Helper

A collection of small, independent helper utilities for Bitcoin Core, optimized for security, simplicity, and auditability.

## Utilities

- `utilities/export-account-xpub/` — export standard account-level extended public keys from a loaded Bitcoin Core wallet.
- `utilities/import-bip39/` — Bitcoin Core Feature Overlay for importing an English BIP39 mnemonic into a fresh descriptor wallet using a pinned, verified Core build and isolated offline launcher.
- [Bitcoin Core Descriptor Signer](https://github.com/Jakob-997/Bitcoin-Core-Multisig-Quorum-Signer) — standalone Feature Overlay that creates one offline Bitcoin Core signer and attaches it to any public descriptor accepted by the pinned Core version, provided the descriptor contains that signer's exact account identity.

The utilities hosted here are self-contained in their own folders with their own READMEs and dependencies. Bitcoin Core Descriptor Signer is maintained in the standalone repository linked above.

## Bitcoin Core Feature Overlay

[Bitcoin Core Feature Overlay](https://github.com/Jakob-997/Bitcoin-Core-Feature-Overlay) is the canonical reusable pattern for implementing small Bitcoin Core features and workflows that are not yet merged upstream, without forking or modifying Bitcoin Core.

1. **Generator** — minimal feature logic using existing Core RPCs.
2. **Launcher** — OS isolation, dependencies, verified Core version enforcement, runtime setup and cleanup.
3. **Human/audit docs** — preparation, backup, recovery, testing, design assumptions and exact review records.

Bitcoin Core remains responsible for Bitcoin primitives. The overlay supplies the missing workflow and can be retired when Core provides equivalent functionality.

Start new features from the canonical upstream repository. `templates/bitcoin-core-feature-overlay/` is a downstream snapshot for convenience, not the canonical source.

The BIP39 importer is now a project-specific downstream adoption of this architecture; its `UPSTREAM.md` and `AUDIT.md` record provenance and review status.

The architecture originated in CoreVault. Maintaining this pattern does not require modifying or rebasing CoreVault.
