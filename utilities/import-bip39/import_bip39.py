#!/usr/bin/env python3
import sys

print(
    "Direct execution has been retired. "
    "Run utilities/import-bip39/tails.sh so the importer uses the reviewed "
    "Bitcoin Core Feature Overlay environment.",
    file=sys.stderr,
)
raise SystemExit(1)
