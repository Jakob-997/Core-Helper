# Bitcoin Core Overlay Scaffold

A standard scaffold for building **small, auditable extensions on top of Bitcoin Core without forking or modifying Core itself**.

The goal is to keep each extension easy to reason about and easy to review by separating it into three layers:

| Layer | File | Owns |
| --- | --- | --- |
| Core logic | `generator.py` | The smallest possible project-specific Bitcoin Core RPC/construction logic |
| OS launcher | `tails.sh` | Tails/network isolation, pinned Core verification, runtime setup and cleanup |
| Human procedure | `PRE-CREATION-GUIDE.txt` / `POST-CREATION-GUIDE.txt` | Preparation, backup, verification, recovery, and testing |

Supporting review documents:

- `DESIGN.md` — architecture, trust model, invariants, and boundaries
- `AUDIT.md` — exact reviewed revisions, findings, test coverage, and upstream references

## Why use this pattern?

Bitcoin Core already implements the difficult Bitcoin primitives: key generation, BIP32 derivation, descriptors, wallets, PSBTs, signing, and transaction validation.

An overlay should add only the missing workflow or policy glue.

That gives a much smaller review target than building another wallet application or embedding Bitcoin logic into a large launcher:

- **minimize custom code** — delegate Bitcoin behavior to Core whenever possible;
- **separate concerns** — Bitcoin logic, operating-system enforcement, and human procedure do not get mixed together;
- **freeze reviewed logic** — after review, keep the generator stable whenever possible;
- **make audits durable** — record exact generator, launcher, and Core revisions;
- **make failures obvious** — launchers and generators should fail closed rather than silently improvise;
- **keep dependencies visible** — pin the Core build and avoid unnecessary libraries;
- **make extensions disposable** — the overlay can remain small because Core stays the actual wallet/node implementation.

This is the recommended structure for new security-sensitive utilities in Core Helper.

## What "overlay" means

This scaffold does **not** patch Bitcoin Core source code.

It layers a small procedure around a verified Core release:

```text
human procedure
      │
      ▼
OS / launcher enforcement
      │
      ▼
minimal generator logic
      │
      ▼
Bitcoin Core RPCs
```

The extension should ask Core to perform Bitcoin operations rather than reimplementing them.

## Start a new utility

Copy this entire folder, rename it for the utility, and then change only the layer that owns each concern.

1. Implement the smallest possible Bitcoin/Core procedure in `generator.py`.
2. Change only project/environment-specific launcher behavior in `tails.sh`.
3. Rewrite the pre/post guides for the exact human workflow.
4. Document architecture and trust assumptions in `DESIGN.md`.
5. Replace the placeholder audit record in `AUDIT.md` after review.
6. Test the complete workflow with disposable funds before meaningful use.

The template intentionally fails until its project placeholders are replaced.

## Design rules

A good Core overlay should generally:

- use Bitcoin Core as the source of truth;
- avoid custom cryptography;
- pass sensitive RPC material through stdin rather than argv;
- pin and verify the exact Core release it was reviewed against;
- use fresh, explicit runtime state;
- keep OS-specific behavior out of the generator;
- keep procedural instructions out of executable code;
- verify postconditions instead of assuming RPC success;
- preserve a small, stable generator that can be audited line-by-line.

## Origin

This scaffold was extracted from the architecture used by **CoreVault**, which served as the first reference implementation of the pattern.

CoreVault does not need to be rebased whenever this scaffold evolves. The scaffold now has its own name and should be treated as the reusable standard for new Core Helper utilities.

## Maintenance rule

- freeze the reviewed generator whenever possible;
- keep Tails / OS changes in `tails.sh`;
- keep operating-procedure changes in the guides;
- change the pinned Bitcoin Core release only after testing that exact release;
- if Core behavior forces a generator change, re-review the generator;
- preserve exact Git revisions for every external review.
