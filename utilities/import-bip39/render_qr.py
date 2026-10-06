#!/usr/bin/env python3
import json
from pathlib import Path
import sys


def fail(message):
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(1)


def main():
    if len(sys.argv) != 2:
        fail("Usage: render_qr.py PUBLIC-DESCRIPTORS.json")

    path = Path(sys.argv[1])
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"Could not read public descriptor file: {exc}")

    descriptors = payload.get("descriptors")
    if not isinstance(descriptors, list) or not descriptors:
        fail("Public descriptor file has no descriptor list.")

    print()
    print("Public wallet descriptors:")
    print()
    for item in descriptors:
        if not isinstance(item, dict):
            fail("Malformed descriptor entry.")
        label = item.get("label")
        descriptor = item.get("descriptor")
        if not isinstance(label, str) or not isinstance(descriptor, str):
            fail("Malformed descriptor entry.")
        print(label)
        print(descriptor)
        print()

    try:
        import qrcode
    except ImportError:
        print("Python qrcode module not found; descriptors are printed above.")
        print("On Debian/Tails it is provided by python3-qrcode.")
        return

    print("QR codes:")
    for i, item in enumerate(descriptors, 1):
        label = item["label"]
        descriptor = item["descriptor"]
        print()
        print(f"[{i}/{len(descriptors)}] {label}")
        qr = qrcode.QRCode(border=2)
        qr.add_data(descriptor)
        qr.make(fit=True)
        qr.print_ascii(out=sys.stdout, tty=sys.stdout.isatty())
        if i != len(descriptors):
            input("\nPress Enter for next descriptor QR...")


if __name__ == "__main__":
    main()
