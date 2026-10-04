# Bitcoin Core Feature Overlay Design

The Bitcoin Core Feature Overlay is a reusable pattern for implementing small Bitcoin Core features and workflows that are not yet merged upstream, using existing Core RPCs without forking or modifying Core.

Canonical source: [Bitcoin Core Feature Overlay](https://github.com/Jakob-997/Bitcoin-Core-Feature-Overlay). Core Helper carries a downstream snapshot; reusable changes belong upstream. The architecture was originally extracted from CoreVault.

## Trust model

The utility should not be trusted because of who wrote it. The executable surface should be small enough that another person can inspect exactly what will run.

Prefer delegating Bitcoin-specific operations to a pinned Bitcoin Core release rather than reimplementing cryptography or wallet behavior.

## Three layers

| Layer | File | Responsibility |
| --- | --- | --- |
| Generator | `generator.py` | Minimal feature-specific logic using Bitcoin Core RPCs |
| Tails launcher | `tails.sh` | Network shutdown, pinned Core verification/extraction, isolated runtime state, Core startup/shutdown |
| Human procedure | pre/post guides | Preparation, backup, verification, testing, recovery, storage |

The generator should be treated as frozen after review. OS changes belong in the launcher. Procedure changes belong in the guides.

## Bitcoin Core verification baseline

The current scaffold baseline uses Bitcoin Core v32.0rc2 and pins the official Linux x86_64 archive SHA-256:

```text
0255103718033e6aee15fa944717fc277e047b845bff1e7408af0ea732d8d0c1
```

This inherited pin is not evidence that this scaffold has been audited. A new utility may retain that exact baseline after review or deliberately move to another release, but a pin change requires testing and review against that exact Core version.

## Project-specific design

PROJECT CUSTOMIZATION REQUIRED.

Document here:

- the missing upstream feature/workflow and relevant upstream proposals, if any;
- why existing Core RPCs are sufficient without modifying Core;
- what the utility creates or changes;
- every wallet type and key path;
- every descriptor form;
- what private material exists and where;
- what Core RPCs are relied upon;
- what the generator validates itself vs what Core validates;
- backup/recovery assumptions;
- online/offline boundary;
- accepted architectural risks;
- criteria for retiring the overlay when Core offers the workflow, including migration and backup compatibility.

## Maintenance rule

1. Freeze the reviewed generator when possible.
2. Keep Tails/OS changes in `tails.sh`.
3. Keep procedural changes in the guides.
4. Do not change the Core version pin without testing that exact release.
5. If Core behavior requires generator changes, re-review the generator.
6. Preserve exact commit hashes for external review.

CoreVault is the original reference implementation this scaffold was extracted from. Scaffold evolution does not require rebasing CoreVault.
