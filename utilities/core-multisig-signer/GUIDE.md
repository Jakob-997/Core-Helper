# Core Multisig Signer Guide

This utility turns one Bitcoin Core wallet into one signer in a BIP87 multisig quorum.

## Before starting

Use a clean, verified Tails installation and independently verify the Bitcoin Core v32.0rc2 archive you intend to use.

For a real signer, use dedicated physically air-gapped hardware where practical. The launcher disables NetworkManager networking as defense in depth, but software isolation is not a substitute for removing network capability from a high-value signing device.

Backups created by this process contain private signing material. Treat them like a hardware-wallet seed backup.

## Folder layout

Copy the `core-multisig-signer` folder out of Core-Helper and place it directly beside the Bitcoin Core archive:

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

Do not extract Bitcoin Core yourself for this workflow. `tails.sh` verifies the archive and extracts a fresh copy.

## Create the signer

In Tails, make `tails.sh` executable and run it as a program. From a terminal, the equivalent is:

```bash
chmod +x tails.sh
./tails.sh
```

The launcher:

1. checks for Python 3, Tails' `qr` command, and NetworkManager
2. disables NetworkManager networking
3. verifies NetworkManager reports networking disabled
4. checks `bitcoin-32.0rc2-x86_64-linux-gnu.tar.gz` against the pinned official SHA-256
5. extracts that verified archive into a fresh directory
6. uses only the extracted `bitcoin-cli` and `bitcoind` by absolute path
7. creates temporary Core runtime state under `/dev/shm`
8. creates a new persistent `signer-wallets/` output directory
9. starts Core with `-networkactive=0 -listen=0`
10. runs the minimal Python generator
11. stops Core and removes the temporary runtime state

The launcher refuses to continue if `signer-wallets/` already exists.

The generator then:

1. verifies Bitcoin Core is 32.x
2. detects mainnet or the supported test network
3. creates a blank descriptor wallet with private keys enabled
4. calls `addhdkey`, causing Bitcoin Core to generate and store a new HD root
5. derives the BIP87 account at `m/87h/0h/0h` on mainnet or `m/87h/1h/0h` on test networks
6. prints the complete public key expression and displays it with Tails' installed `qr` command

Example:

```text
[1234abcd/87h/0h/0h]xpub...
```

The QR contains that exact public string only.

## Build the quorum

Collect one BIP87 key expression from every signer and construct the public descriptor on the coordinator.

Example 2-of-3 shape:

```text
wsh(sortedmulti(2,
[aaaaaaaa/87h/0h/0h]xpubA/<0;1>/*,
[bbbbbbbb/87h/0h/0h]xpubB/<0;1>/*,
[cccccccc/87h/0h/0h]xpubC/<0;1>/*
))
```

Remove whitespace/newlines before pasting unless the coordinator already outputs it as a single line.

A descriptor checksum is optional when pasting into the signer utility. Bitcoin Core validates the descriptor and computes the checksum used for import.

## Import the quorum

Paste the complete **public** multisig descriptor when prompted.

The utility rejects descriptors that:

- contain private keys
- are not `wsh(sortedmulti(...))`
- are not ranged/solvable
- do not use BIP87 account 0
- use the wrong coin type/network
- do not use `/<0;1>/*`
- contain duplicate account xpubs
- do not contain this signer exactly once

Only after the public descriptor passes those checks does the helper ask Bitcoin Core for this signer's BIP87 account xprv.

The helper replaces exactly this signer's matching xpub with that xprv **in memory**, asks Bitcoin Core to parse the result, and verifies Core reports the same public descriptor before importing it.

The xprv and private descriptor are never intentionally printed, written to a project file, copied to the clipboard, encoded as a QR, or passed as command-line arguments.

## Back up before funding

After the utility reports `Signer creation complete`, the private Core wallet data is under:

```text
core-multisig-signer/signer-wallets/
```

Before meaningful funding:

1. make a verified backup of the signer wallet
2. store that backup as private signing material
3. verify all quorum participants and the coordinator derive the same first receive address
4. fund only with disposable test funds
5. create a PSBT on the coordinator
6. load the PSBT into this Core signer
7. sign it in Bitcoin Core
8. combine the required signatures and broadcast
9. only then consider using meaningful funds

The utility does not automate the test spend. That is deliberate: the final human verification should happen through the normal Bitcoin Core PSBT workflow.
