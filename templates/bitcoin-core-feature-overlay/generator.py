#!/usr/bin/env python3
"""
PROJECT CUSTOMIZATION REQUIRED.

This file is the Bitcoin Core Feature Overlay core-logic layer.
Keep Bitcoin/project construction here and OS/runtime behavior in tails.sh.
"""

import json
import subprocess
import sys

bitcoin_cli = sys.argv[1] if len(sys.argv) > 1 else None


def fail(message):
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(1)


def command(method, wallet=None):
    if not bitcoin_cli:
        fail("Run this utility through tails.sh.")

    cmd = [bitcoin_cli]
    if wallet:
        cmd.append(f"-rpcwallet={wallet}")
    return cmd + ["-stdin", method]


def rpc(method, *args, wallet=None):
    stdin = "".join(f"{arg}\n" for arg in args)
    output = subprocess.check_output(
        command(method, wallet=wallet),
        input=stdin,
        text=True,
    )
    return json.loads(output)


def main():
    fail(
        "Template generator has not been implemented. "
        "Replace this function with the reviewed project-specific Core logic."
    )


if __name__ == "__main__":
    main()
