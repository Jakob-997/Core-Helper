# Bitcoin Core Feature Overlay

**A reusable pattern for implementing small Bitcoin Core features and workflows that are not yet merged upstream, without forking or modifying Bitcoin Core.**

An overlay supplies the missing workflow glue through Core's existing RPCs. Bitcoin Core remains responsible for key generation, BIP32 derivation, descriptors, wallet storage, PSBTs, signing, and validation wherever its RPCs support the feature. This is a scaffold for a small feature, not another wallet implementation or a patch to Core's source or binaries.

The canonical pattern and scaffold live in [Jakob-997/Bitcoin-Core-Feature-Overlay](https://github.com/Jakob-997/Bitcoin-Core-Feature-Overlay). Propose reusable architecture and scaffold changes there; downstream utilities retain their own reviewed revisions.

## Three layers

| Layer | Files | Responsibility |
| --- | --- | --- |
| Minimal generator | `generator.py` | Only feature-specific logic using Bitcoin Core RPCs; validate inputs and postconditions |
| OS launcher | `tails.sh` | OS isolation, dependency checks, exact Core version/archive enforcement, runtime setup and cleanup |
| Human and audit documentation | pre/post guides, `DESIGN.md`, `AUDITING.md`, `AUDIT.md` | Preparation, backup, recovery, testing, trust assumptions, review method and exact review records |

Keep OS behavior out of the generator and human procedures in separate documents. The included launcher is a Tails/offline starting point; the pattern can support other environments through separately reviewed launchers.

## When to use it

Use an overlay when existing Core RPCs provide the primitives but a small feature or workflow is missing upstream. A multisig signer setup procedure is one example: Core owns the wallet and Bitcoin operations, while the overlay coordinates the missing steps.

Document the precise upstream gap and any relevant proposal or pull request. An overlay does not imply that Bitcoin Core endorses the feature or plans to merge it. If implementing the feature requires changes inside Core or substantial custom wallet/cryptographic code, reconsider whether this pattern fits.

The overlay is a temporary, auditable bridge to upstream functionality. When Core provides an equivalent workflow, evaluate retiring the overlay and document how users verify and migrate existing outputs and backups.

## Start a feature

1. Copy this scaffold from a specific canonical repository commit and record that commit in your project's `AUDIT.md`.
2. Define the missing feature, supported environment, inputs, outputs and invariants in `DESIGN.md`.
3. Implement only the necessary Core RPC procedure in `generator.py`.
4. Customize `tails.sh` for the environment, dependencies, output paths and exact verified Core release.
5. Replace both human guides with the feature's preparation, backup, recovery and verification procedure.
6. Follow [AUDITING.md](AUDITING.md), record the actual review and test results in [AUDIT.md](AUDIT.md), and test the full workflow with disposable funds where applicable.

**The supplied generator and launcher intentionally fail until their project placeholders are replaced.** They are not a finished feature or an audited wallet. The inherited Core archive pin is a baseline to review, not a claim of current support or completed review.

## Design and maintenance rules

- Delegate Bitcoin primitives to Core and avoid custom cryptography.
- Send sensitive RPC material over stdin rather than process arguments.
- Pin and verify the exact Core build; review and test every dependency change.
- Use explicit, fresh runtime state and fail closed on unexpected conditions.
- Verify postconditions rather than assuming RPC success is sufficient.
- Keep reviewed generator logic stable; review changes to it explicitly.
- Keep OS changes in the launcher and procedure changes in the documents.
- Record exact project, generator, launcher and Core revisions for each review.
- Review downstream updates deliberately; an upstream scaffold update does not confer an audit on an existing utility.

See [DESIGN.md](DESIGN.md) for architecture and trust boundaries and [AUDITING.md](AUDITING.md) for review guidance.

## Origin

The three-layer architecture was extracted from CoreVault. Bitcoin Core Feature Overlay is now the independently maintained reusable pattern. Its evolution does not require changes to or rebasing CoreVault.
