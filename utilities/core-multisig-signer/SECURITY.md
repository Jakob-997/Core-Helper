# Security Notes

## Trust model

The goal is to keep the project-specific executable surface small and let Bitcoin Core perform Bitcoin-specific operations.

Bitcoin Core is responsible for:

- random HD root generation
- BIP32 derivation
- descriptor parsing and canonicalization
- descriptor checksum calculation
- wallet storage
- PSBT signing

The helper orchestrates those operations and adds fail-closed validation around the expected BIP87 multisig policy.

## Secret handling

The public BIP87 account key is intentionally printed and encoded as a QR.

The private BIP87 account xprv exists briefly as a Python string because current Bitcoin Core descriptor-import behavior requires the signer's private account key to appear in the imported signing descriptor. It is obtained only after the public descriptor has been validated.

The implementation:

- sends RPC arguments through `bitcoin-cli -stdin`, not argv
- never intentionally prints the xprv or private descriptor
- never writes them to a project file
- never sends them to `qr`
- suppresses potentially sensitive RPC error text once private material is involved
- deletes the Python reference as soon as import completes

Python strings cannot be reliably zeroized. A compromised process, OS, Python runtime, Bitcoin Core binary, or host can still recover secrets. This helper does not claim memory-hard isolation.

## Descriptor invariants

Before requesting private key material, the helper requires:

- `wsh(sortedmulti(...))`
- BIP87 account 0
- mainnet coin type 0 or test-network coin type 1
- `/<0;1>/*` derivation
- a ranged and solvable descriptor
- no private keys in user input
- no duplicate signer expressions or account xpubs
- exactly one signer key matching both this signer's fingerprint and account xpub

After substituting this signer's xprv, Bitcoin Core must report that the private form canonicalizes back to the exact same public descriptor and the same multipath expansion.

After import, `gethdkeys active_only=true` must report exactly one private HD key in the active multisig policy and it must correspond to this signer's BIP87 account xpub.

## Tails launcher and air gap

`tails.sh` disables NetworkManager networking with:

```text
nmcli networking off
```

and aborts unless NetworkManager reports `disabled`.

This is defense in depth, not a substitute for physically removing/disabling network hardware when creating a high-value signer.

The launcher does not attempt to install packages or fetch anything from the Internet.

It expects the utility folder to sit directly beside `bitcoin-32.0rc2-x86_64-linux-gnu.tar.gz`. Before execution it checks that archive against the pinned official SHA-256:

```text
0255103718033e6aee15fa944717fc277e047b845bff1e7408af0ea732d8d0c1
```

It then extracts Core into a fresh directory and invokes only that extraction's `bitcoin-cli` and `bitcoind` by absolute path. Core is started with `-networkactive=0 -listen=0`, while its transient HOME/runtime state lives under `/dev/shm`. The persistent signer wallet is written only to the new `signer-wallets/` directory.

The launcher refuses to reuse an existing `signer-wallets/` directory.

## QR dependency

The launcher uses the operating system's installed `qr` executable. On Tails, the package is `python3-qrcode` and the command-line name is `qr`.

Only public signer information is sent to the QR encoder.

## Limitations

- The Tails launcher is pinned to Bitcoin Core v32.0rc2. Another Core build must be reviewed and tested before changing the pin.
- The utility intentionally supports only BIP87 account 0 and native SegWit `wsh(sortedmulti())`.
- Wallet encryption is not implemented in this first version; use the signer only in an environment whose wallet-storage assumptions you understand.
- The helper does not create the coordinator/watch-only wallet.
- The helper does not scan QR input; the public quorum descriptor is pasted as text.
- The helper does not prove the entire M-of-N policy with an end-to-end spend. Perform a real disposable-funds PSBT test before meaningful use.
- This project has not received an independent professional security audit.

## Review target

The main security-critical file is `core_multisig_signer.py`. `tails.sh` should be reviewed separately for archive verification, OS/environment behavior, and Core startup/shutdown. This document plus `GUIDE.md` should be reviewed for procedural assumptions.
