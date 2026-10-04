# Core Multisig Signer

Use a Bitcoin Core wallet as one signer in a BIP87 multisig quorum.

The utility creates a blank Core wallet, lets Core generate the HD root, exports the BIP87 account xpub as text and a terminal QR, then imports the completed public multisig descriptor with only this signer's matching account key made private internally.

## Quick start

> **For a real signer:** use a dedicated computer, preferably a laptop, that is physically air-gapped with its network hardware removed and never reconnected afterward. The software networking shutdown is defense in depth.

```text
1. Verify Tails and Bitcoin Core v32.0rc2.
2. Copy the core-multisig-signer folder out of this repository.
3. Put that folder next to:
   bitcoin-32.0rc2-x86_64-linux-gnu.tar.gz
4. Read GUIDE.md.
5. In Tails, make tails.sh executable and choose "Run as a Program".
6. Add the displayed BIP87 key to your multisig quorum.
7. Paste the completed public quorum descriptor back into the signer.
8. Back up signer-wallets and test the quorum with disposable funds.
```

The expected layout is:

```text
your-folder/
├── bitcoin-32.0rc2-x86_64-linux-gnu.tar.gz
└── core-multisig-signer/
    ├── tails.sh
    ├── core_multisig_signer.py
    ├── GUIDE.md
    ├── README.md
    └── SECURITY.md
```

Use **Bitcoin Core v32.0rc2 exactly**. The launcher pins and verifies that archive before extracting or running it.

## Three layers

| Layer | File | Responsibility |
| --- | --- | --- |
| Generator | `core_multisig_signer.py` | Bitcoin Core RPC flow, descriptor validation, private-key substitution, post-import verification |
| Tails launcher | `tails.sh` | Disable networking, verify/extract the pinned Core archive, isolate runtime state, start/stop Core |
| Human procedure | `GUIDE.md` / `SECURITY.md` | Quorum exchange, backup, test spend, threat model, and limitations |

The generator contains no custom cryptography. Bitcoin Core generates and derives keys, parses descriptors, computes descriptor checksums, stores the wallet, and performs signing.

## What it outputs

The signer key shown to the coordinator has the form:

```text
[fingerprint/87h/0h/0h]xpub...
```

On supported test networks Core uses coin type 1:

```text
[fingerprint/87h/1h/0h]tpub...
```

The completed quorum descriptor must be native SegWit BIP87 `wsh(sortedmulti(...))` using `/<0;1>/*` receive/change derivation.

The private Core wallet is created under:

```text
core-multisig-signer/signer-wallets/
```

The launcher aborts if that directory already exists rather than reusing an old signer.

## Status

Security-oriented testing and review are still required before using this with meaningful funds. See [SECURITY.md](SECURITY.md).
