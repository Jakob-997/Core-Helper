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

## Why this format instead of a manual guide?

For a repeatable workflow with several dependent steps, a feature overlay can reduce how much the user must remember, edit and check by hand. The generator can enforce the RPC sequence and verify results; the launcher can enforce the supported environment and exact Core dependency; the guides explain the decisions and physical procedures that still require a person.

A manual guide can describe the same checks, but the reader must carry them out correctly each time. Putting a check in executable code makes it repeatable and gives reviewers a concrete implementation to inspect. That benefit depends on the check actually being implemented, reviewed and tested.

| Format | Where it works well | Tradeoffs compared with a feature overlay |
| --- | --- | --- |
| Manual guide | Learning, explaining choices, or a short procedure performed by an experienced user | The reader owns command order, substitutions, environment checks and verification on every run. A guide remains essential for preparation, backup and recovery. |
| Copy-and-paste commands or snippets | A small, understood operation in a known environment | Commands may depend on earlier shell state or require edits to names and paths. Partial execution and unchecked outputs can be harder to detect. A versioned overlay can make those assumptions explicit and reject unsupported conditions. |
| One-off script | Automating a small task with few environmental assumptions | It can be just as suitable for a simple task. As the workflow grows, separating feature logic, OS enforcement and human instructions gives each concern a clearer review and maintenance boundary. |
| Feature overlay | A small missing Core workflow that benefits from repeatable execution and explicit environment enforcement | Adds code and maintenance obligations. Its advantage is a small, versioned review target with separate responsibilities, while Core supplies the Bitcoin primitives. |
| Full wallet or application | Broad functionality, ongoing interaction and a richer user interface | A larger product may be appropriate, but can introduce more dependencies and behavior to review. An overlay aims to keep a single missing workflow small. |
| Core fork or source patch | A feature that genuinely needs changes inside Core | Requires maintaining and reviewing a modified Core build. An overlay fits only when existing RPCs can provide the required behavior. |
| Native upstream Core feature | Core already supports the required workflow | Prefer the native workflow when it meets the requirements; assess migration and backup compatibility before retiring an existing overlay. |

For example, a guide might ask the reader to select the correct Core archive, start an isolated instance, run several wallet RPCs and inspect the resulting descriptors. An implemented overlay can verify the archive, reject an existing output directory, run the intended sequence and check the resulting wallet state. The user still needs the guides to understand the outputs, prepare the physical environment, make backups and test recovery.

Automation also concentrates trust in the code: a faulty script can repeat a mistake consistently. This format does not make unreviewed code safe, establish a physical air gap, or prove that a backup works. Its value is making the executable steps and their assumptions easier to inspect, reproduce and test together. For a single straightforward command, a clear manual instruction may be enough.

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

## Community

Contributors and participants are expected to follow the [Code of Conduct](CODE_OF_CONDUCT.md).
