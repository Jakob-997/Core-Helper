# Upstream provenance

This utility is a downstream adoption of the canonical [Bitcoin Core Feature Overlay](https://github.com/Jakob-997/Bitcoin-Core-Feature-Overlay).

- Upstream revision: `632648b88cdb867ab6372e2850e8a53d00f58552`
- Architecture adopted: minimal generator, offline launcher, human/audit documentation.
- Project-specific additions: BIP39/BIP32 conversion logic, Core wallet import workflow, public-only QR renderer, BIP39 wordlist and importer-specific guides.

The upstream scaffold is a pattern, not an audit. This utility's project-specific generator, launcher, renderer, documentation and exact Core pin require their own review.

Reusable scaffold changes belong in the canonical repository. Importer-specific changes belong here. Updating the canonical scaffold does not automatically update or audit this utility.
