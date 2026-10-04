# Audit Record

**Generator blob:** `7bfdf5b73dbecb32dd40debc20d32b4a5c6a3d3e`  
**Tails launcher blob:** `87a025348e4efa9b3a0fa127df853aaa5c168361`  
**Bitcoin Core version reviewed:** `v32.0rc2`  
**Bitcoin Core commit:** `bc795e60dbb2c6e9c9556949731912429290626a`  
**Review date:** 2026-10-04

This is an AI-assisted source/security review record. It is not an independent professional security audit.

## Scope

The review covered:

- `generator.py`;
- `tails.sh`;
- BIP87 signer derivation;
- public quorum descriptor validation;
- private account-key substitution for signing-wallet import;
- descriptor canonicalization checks;
- `gethdkeys` post-import verification;
- stdin handling for sensitive RPC parameters;
- Tails networking shutdown;
- pinned Bitcoin Core archive verification and fresh extraction;
- QR output boundary;
- backup/restore/test-spend procedure.

## Construction reviewed

The intended construction is:

1. create a blank descriptor wallet with private keys enabled;
2. call `addhdkey` so Core generates/stores a fresh HD root;
3. call `derivehdkey` at BIP87 account 0;
4. export only the public origin+xpub expression;
5. accept only a public `wsh(sortedmulti(...))` BIP87 quorum descriptor;
6. require exactly one match to this signer;
7. derive this signer's account xprv internally;
8. replace only the matching account xpub in memory;
9. require Core to canonicalize the private form to the same public descriptor/multipath expansion;
10. import the signing descriptor;
11. require `gethdkeys active_only=true` to report exactly one active private signer key.

## Security properties reviewed

- No custom cryptographic primitives are implemented.
- Bitcoin Core generates and derives the signer keys.
- Sensitive RPC parameters are sent through `bitcoin-cli -stdin`, not argv.
- The xprv/private descriptor are not intentionally printed, persisted by the helper, copied to clipboard, or QR encoded.
- RPC errors involving private descriptor material suppress potentially sensitive response text.
- The QR receives public signer information only.
- Descriptor input fails closed on wrong structure, network, BIP87 path, duplicate keys, private input, or signer mismatch.
- The launcher disables NetworkManager networking and requires the disabled state.
- Core is additionally started with `-networkactive=0 -listen=0`.
- The launcher verifies the pinned v32.0rc2 archive before extracting and uses only that fresh extraction by absolute path.
- Temporary Core HOME/runtime state is placed under `/dev/shm`.
- Existing `signer-wallets/` output is not reused.

## Issues caught during development

### RPC stdin and regex escaping

An early committed draft contained incorrect Python escaping in the descriptor regexes and RPC stdin newline construction.

Those errors were found during committed-source review and corrected before the utility was placed on `main`.

**Status:** fixed.

### Ambiguous Core binary selection

The first utility launcher expected `bitcoin-cli` on PATH.

The Bitcoin Core Feature Overlay launcher now verifies the adjacent pinned Core archive, freshly extracts it, and passes the exact extracted binary paths to the generator.

**Status:** fixed.

### Documentation/layer drift

The first version used `core_multisig_signer.py`, `GUIDE.md`, and `SECURITY.md`.

The utility has now been rebased onto the Bitcoin Core Feature Overlay:

- `generator.py`;
- `tails.sh`;
- pre/post human guides;
- `DESIGN.md`;
- this `AUDIT.md`.

The wallet construction itself was not changed by that structural refactor.

**Status:** fixed.

## Testing performed

During development:

- Python syntax checking was performed on the generator.
- A mocked `bitcoin-cli` end-to-end flow exercised wallet creation, BIP87 public derivation, public descriptor validation, private account derivation, signer substitution, import, and post-import `gethdkeys` verification.
- The launcher and generator were reviewed against Bitcoin Core v32.0rc2 source behavior for `addhdkey`, `derivehdkey`, and `gethdkeys`.

## Still required before meaningful funds

Perform the complete workflow on the exact intended Tails environment and Bitcoin Core v32.0rc2 archive, preferably first on signet/regtest, including:

1. creation;
2. backup;
3. restore from backup;
4. address agreement with the coordinator;
5. real PSBT signing;
6. threshold completion;
7. testing every signer/recovery path.

## Accepted limitations

- No independent professional audit has been performed.
- Python private strings cannot be reliably zeroized.
- Wallet encryption is not implemented.
- The online coordinator is outside this utility's trust boundary.
- Physical/firmware compromise is outside the helper's ability to detect.
- The Core version pin must not be changed without retesting/review.

## Upstream references

- Bitcoin Core v32.0rc2 source
- Bitcoin Core wallet RPC implementation for `createwallet`, `addhdkey`, `derivehdkey`, and `gethdkeys`
- Bitcoin Core descriptor/import documentation and tests
- BIP32
- BIP87
- BIP129
- BIP174
- BIP380 / BIP382 / BIP383
- bitcoin/bitcoin#35377
- bitcoin/bitcoin#36325

## Maintenance rule

1. Treat the reviewed `generator.py` as frozen.
2. Keep Tails/OS changes in `tails.sh`.
3. Keep human procedure changes in the pre/post guides.
4. Re-review any generator change.
5. Retest and re-review any Bitcoin Core version-pin change.
6. Record new executable blob SHAs after any security-relevant change.
