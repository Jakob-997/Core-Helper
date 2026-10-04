# Audit Record

PROJECT CUSTOMIZATION REQUIRED.

Do not claim this template's review applies automatically to a utility copied from it.

Follow [AUDITING.md](AUDITING.md). For each real utility, record:

- canonical Bitcoin Core Feature Overlay commit used;

- exact project commit reviewed;
- exact generator blob/revision reviewed;
- exact launcher blob/revision reviewed;
- exact Bitcoin Core release and commit reviewed;
- review date;
- scope;
- findings and fixes;
- unresolved limitations;
- end-to-end test environment and results;
- upstream Bitcoin Core/BIP references relied upon.

## Feature overlay scaffold baseline

The scaffold preserves these design principles:

- small generator;
- no custom cryptography unless explicitly justified and reviewed;
- sensitive RPC arguments over stdin rather than process argv;
- pinned Core archive verification;
- fresh extraction;
- absolute paths to verified Core binaries;
- NetworkManager shutdown plus Core `-networkactive=0 -listen=0`;
- temporary runtime state under `/dev/shm`;
- separate human backup/restore/test procedure;
- exact-version review.

These are architectural starting points, not an audit of a new utility.

## Final review rule

A copied utility is **unaudited until its project-specific generator, launcher changes, guides, and exact Core dependency are reviewed together**.
