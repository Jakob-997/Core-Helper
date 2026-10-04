# CoreVault-Style Three-Layer Template

A reusable starting point for small security-sensitive Bitcoin Core utilities.

This template is **derived from CoreVault's architecture**. CoreVault is the reference design; it does not need to be rebased onto this template when the template changes.

## The three layers

| Layer | File | Owns |
| --- | --- | --- |
| Core logic | `generator.py` | Bitcoin Core RPC flow and project-specific construction logic |
| OS launcher | `tails.sh` | Tails/network isolation, pinned Core verification, runtime setup and cleanup |
| Human procedure | `PRE-CREATION-GUIDE.txt` / `POST-CREATION-GUIDE.txt` | Preparation, backup, verification, recovery, and testing |

Supporting review documents:

- `DESIGN.md` — architecture and trust model
- `AUDIT.md` — exact reviewed revisions, findings, upstream references

## Start a new utility

Copy this entire folder, rename it for the utility, and then make changes only in the layer that owns them.

1. Implement the Bitcoin-specific procedure in `generator.py`.
2. Change only the marked project-specific values in `tails.sh`.
3. Rewrite the pre/post guides for the actual workflow.
4. Update `DESIGN.md` so it describes the real construction.
5. Replace the placeholder audit record in `AUDIT.md` after review.
6. Test the complete workflow with disposable funds before meaningful use.

The template intentionally fails until its project placeholders are replaced.

## Maintenance rule

Use the same rule as CoreVault:

- freeze the reviewed generator whenever possible;
- keep Tails / OS changes in `tails.sh`;
- keep operating procedure changes in the guides;
- change the pinned Bitcoin Core release only after testing that exact release;
- if Core behavior forces a generator change, re-review the generator;
- preserve an exact Git commit for every external review.

Do **not** mechanically sync future template edits back into CoreVault. If CoreVault itself needs a change, review that change on its own merits.
