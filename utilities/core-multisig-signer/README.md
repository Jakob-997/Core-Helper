# Core Multisig Signer

**Use Bitcoin Core as one signer in a BIP87 multisig quorum.**

Built using the [Bitcoin Core Feature Overlay](https://github.com/Jakob-997/Bitcoin-Core-Feature-Overlay): minimal Core-facing logic, a separate Tails launcher, and separate human/audit documentation.

The utility creates one blank Core signer wallet, exports its public BIP87 account key as text + QR, then imports the completed multisig policy so the wallet can sign PSBTs as one member of the quorum.

## Quick start

> **For a real signer:** use dedicated hardware that is physically air-gapped where practical. The launcher's software networking shutdown is defense in depth.

```text
1. Verify Tails and Bitcoin Core v32.0rc2.
2. Put the core-multisig-signer folder next to:
   bitcoin-32.0rc2-x86_64-linux-gnu.tar.gz
3. Read PRE-CREATION-GUIDE.txt.
4. In Tails, make tails.sh executable and choose "Run as a Program".
5. Add the displayed BIP87 key to your multisig quorum.
6. Paste the completed public quorum descriptor into the signer.
7. Follow POST-CREATION-GUIDE.txt to back up, restore, verify, and test it.
```

Expected layout:

```text
your-folder/
├── bitcoin-32.0rc2-x86_64-linux-gnu.tar.gz
└── core-multisig-signer/
    ├── tails.sh
    ├── generator.py
    ├── PRE-CREATION-GUIDE.txt
    ├── POST-CREATION-GUIDE.txt
    ├── DESIGN.md
    ├── AUDIT.md
    └── README.md
```

Use **Bitcoin Core v32.0rc2 exactly**. Another release must be tested and reviewed before changing the pin.

## Design at a glance

- Bitcoin Core generates, derives, validates, and stores the keys.
- The signer uses BIP87 account 0.
- The quorum is native SegWit `wsh(sortedmulti())`.
- Only this signer's account key becomes private inside its imported multisig descriptor.
- The public signer key is displayed with Tails' installed `qr` command.
- The helper contains no custom cryptography.

## Three layers

| Layer | File | Responsibility |
| --- | --- | --- |
| Generator | [generator.py](generator.py) | Core RPC flow and signer construction |
| Tails launcher | [tails.sh](tails.sh) | Network shutdown, pinned Core verification/extraction, isolated runtime |
| Human procedure | [PRE-CREATION-GUIDE.txt](PRE-CREATION-GUIDE.txt) / [POST-CREATION-GUIDE.txt](POST-CREATION-GUIDE.txt) | Preparation, backup, restore, verification, test spend |

The generator is the primary executable review target. Tails/environment changes belong in the launcher; operating procedure changes belong in the guides.

## Signer key

The public key shown to the coordinator is:

```text
[fingerprint/87h/0h/0h]xpub...
```

Supported test networks use coin type 1.

The completed descriptor must have the form:

```text
wsh(sortedmulti(M,[origin]xpub/<0;1>/*,...))
```

## Read more

- [DESIGN.md](DESIGN.md) — architecture, trust model, descriptor construction, private-key boundary
- [AUDIT.md](AUDIT.md) — exact reviewed executable revisions, findings, limitations
- [PRE-CREATION-GUIDE.txt](PRE-CREATION-GUIDE.txt) — preparation checklist
- [POST-CREATION-GUIDE.txt](POST-CREATION-GUIDE.txt) — backup, restore, address verification, PSBT test

**This utility has received AI-assisted review but no independent professional security audit.**
