# Core Multisig Signer Guide

This utility turns one Bitcoin Core wallet into one signer in a BIP87 multisig quorum.

## Before starting

Use a clean, verified operating system and a clean, verified Bitcoin Core 32.x installation. For an offline signer, physically disconnect networking where practical. The launcher also disables NetworkManager networking as defense in depth.

Start Bitcoin Core locally with RPC available before running the utility. The helper talks only to the local `bitcoin-cli`; it does not make network requests.

Backups created by this process contain private signing material. Treat them like a hardware-wallet seed backup.

## Create the signer

Run:

```bash
chmod +x run.sh
./run.sh
```

The launcher:

1. checks for Python 3, `bitcoin-cli`, `qr`, and `nmcli`
2. disables NetworkManager networking
3. verifies NetworkManager reports networking disabled
4. passes absolute paths for `bitcoin-cli` and `qr` to the generator

The generator then:

1. verifies Bitcoin Core is 32.x
2. detects mainnet or the supported test network
3. creates a blank descriptor wallet with private keys enabled
4. calls `addhdkey`, causing Bitcoin Core to generate and store a new HD root
5. derives the BIP87 account at `m/87h/0h/0h` on mainnet or `m/87h/1h/0h` on test networks
6. prints the complete public key expression and displays it with the installed `qr` command

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

The xprv and private descriptor are never intentionally printed, written to a file, copied to the clipboard, encoded as a QR, or passed as command-line arguments.

## Back up before funding

After the utility reports `Signer ready`:

1. stop creating or modifying the wallet
2. make a Bitcoin Core wallet backup using your normal verified backup procedure
3. store that backup as private signing material
4. verify all quorum participants and the coordinator derive the same first receive address
5. fund only with disposable test funds
6. create a PSBT on the coordinator
7. load the PSBT into this Core signer
8. sign it in Bitcoin Core
9. combine the required signatures and broadcast
10. only then consider using meaningful funds

The utility does not automate the test spend. That is deliberate: the final human verification should happen through the normal Bitcoin Core PSBT workflow.
