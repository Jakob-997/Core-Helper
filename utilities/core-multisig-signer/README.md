# Core Multisig Signer

Use a Bitcoin Core 32.x wallet as one signer in a BIP87 multisig quorum.

The utility creates a blank Core wallet, lets Core generate the HD root, exports the BIP87 account xpub as text and a terminal QR, then imports the completed public multisig descriptor with only this signer's matching account key made private internally.

## Three layers

| Layer | File | Responsibility |
| --- | --- | --- |
| Generator | `core_multisig_signer.py` | Bitcoin Core RPC flow, descriptor validation, private-key substitution, post-import verification |
| Launcher | `run.sh` | Dependency checks and NetworkManager software air gap |
| Human procedure | `GUIDE.md` / `SECURITY.md` | Setup, quorum exchange, backup, test spend, threat model, and limitations |

The generator contains no custom cryptography. Bitcoin Core generates and derives keys, parses descriptors, computes descriptor checksums, stores the wallet, and performs signing.

## Requirements

- Bitcoin Core 32.x
- a running local Bitcoin Core RPC server
- Python 3
- NetworkManager / `nmcli`
- the `qr` command
  - Tails includes `python3-qrcode`, whose command-line name is `qr`

The launcher intentionally refuses to run without `nmcli` because it disables NetworkManager networking before key creation.

## Run

Read [GUIDE.md](GUIDE.md) first.

```bash
chmod +x run.sh
./run.sh
```

The signer key shown to the coordinator has the form:

```text
[fingerprint/87h/0h/0h]xpub...
```

On test networks Core uses coin type 1:

```text
[fingerprint/87h/1h/0h]tpub...
```

The completed quorum descriptor must be native SegWit BIP87 `wsh(sortedmulti(...))` using `/<0;1>/*` receive/change derivation.

## Status

Security-oriented testing and review are still required before using this with meaningful funds. See [SECURITY.md](SECURITY.md).
