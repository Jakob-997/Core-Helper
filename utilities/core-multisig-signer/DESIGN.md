# Core Multisig Signer Design

This utility follows the [Bitcoin Core Feature Overlay](https://github.com/Jakob-997/Bitcoin-Core-Feature-Overlay), a three-layer pattern originally extracted from CoreVault.

## Trust model

The utility is designed so that project-specific executable logic remains small and Bitcoin-specific behavior is delegated to a pinned Bitcoin Core release.

Bitcoin Core performs:

- random HD-root generation;
- BIP32 derivation;
- descriptor parsing and canonicalization;
- descriptor checksum calculation;
- wallet storage;
- PSBT signing.

The helper orchestrates those operations and validates the expected BIP87 multisig policy.

## Three layers

| Layer | File | Responsibility |
| --- | --- | --- |
| Generator | `generator.py` | Core RPC flow, BIP87 signer export, descriptor validation, private-key substitution, post-import verification |
| Tails launcher | `tails.sh` | Guide display, software air gap, pinned Core verification/extraction, isolated runtime state, Core startup/shutdown |
| Human procedure | `PRE-CREATION-GUIDE.txt` / `POST-CREATION-GUIDE.txt` | Preparation, backup, descriptor/address verification, test spend, restore, storage |

The generator should be treated as frozen after review. OS/Tails changes belong in `tails.sh`. Procedure changes belong in the pre/post guides.

## Wallet construction

Mainnet signer path:

```text
m/87h/0h/0h
```

Supported test networks use coin type 1.

The signer starts as a blank descriptor wallet with private keys enabled. Core creates a fresh HD root with `addhdkey`, then derives the BIP87 account using `derivehdkey`.

The utility exports the public signer expression:

```text
[fingerprint/87h/0h/0h]xpub...
```

The completed quorum must be:

```text
wsh(sortedmulti(M,[origin]xpub/<0;1>/*,...))
```

The user pastes only the public quorum descriptor.

Before requesting any private derived key, the generator requires:

- `wsh(sortedmulti(...))`;
- BIP87 account 0;
- correct coin type/network;
- `/<0;1>/*`;
- ranged and solvable descriptor;
- no private input;
- no duplicate signer expressions/account xpubs;
- exactly one match to this signer's fingerprint and BIP87 account xpub.

## Signing-descriptor import

For Bitcoin Core v32.0rc2, the signing wallet imports the quorum descriptor with only its own BIP87 account xpub replaced by the corresponding account xprv.

The xprv is derived only after the public descriptor passes validation.

The private descriptor is held only in process memory long enough to pass it to Bitcoin Core over `bitcoin-cli -stdin`. It is not intentionally printed, written to disk by the helper, passed in argv, copied to the clipboard, or sent to the QR encoder.

Before import, Bitcoin Core must canonicalize the private form back to the same public descriptor and the same multipath expansion.

After import, `gethdkeys active_only=true` must report exactly one private HD key in the active multisig policy and it must match this signer's account xpub.

## QR output

The launcher uses Tails' installed `qr` command from `python3-qrcode`.

Only the public signer key expression is passed to the QR encoder.

## Bitcoin Core verification

The launcher is pinned to Bitcoin Core v32.0rc2 Linux x86_64.

Pinned archive SHA-256:

```text
0255103718033e6aee15fa944717fc277e047b845bff1e7408af0ea732d8d0c1
```

The archive is freshly extracted and only the absolute paths to that extraction's `bitcoin-cli` and `bitcoind` are used.

Core runs with:

```text
-networkactive=0 -listen=0
```

and temporary HOME/runtime state under `/dev/shm`.

Persistent wallet data is written only to `signer-wallets/`.

The launcher refuses to reuse an existing `signer-wallets/` directory.

## Accepted limitations

- The launcher is tied to Bitcoin Core v32.0rc2 until another exact release is reviewed and tested.
- Python strings containing private descriptor material cannot be reliably zeroized.
- The helper does not create or manage the watch-only coordinator.
- The helper accepts the public quorum descriptor as pasted text rather than scanning it.
- Wallet encryption is not implemented in this version.
- Software networking shutdown is defense in depth, not a replacement for physical isolation.
- A compromised Tails image, Core binary, Python runtime, host firmware, or hardware can still compromise the signer.
- The utility does not replace an end-to-end disposable-funds test.

## Maintenance rule

1. Treat `generator.py` as frozen after review.
2. Keep Tails/environment changes in `tails.sh`.
3. Keep operating procedure changes in the pre/post guides.
4. Do not change the Bitcoin Core version pin without testing that exact release.
5. If Core wallet/HD-key/descriptor behavior requires generator changes, re-review the generator.
6. Preserve exact revisions for external review.
