#!/usr/bin/env python3
import atexit
import hashlib
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time

EXPECTED_SHA256 = "0255103718033e6aee15fa944717fc277e047b845bff1e7408af0ea732d8d0c1"
ARCHIVE_NAME = "bitcoin-32.0rc2-x86_64-linux-gnu.tar.gz"


def fail(message):
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(1)


def run(args, **kwargs):
    try:
        return subprocess.run(args, check=True, text=True, **kwargs)
    except (OSError, subprocess.CalledProcessError) as exc:
        fail(str(exc))


def require(name):
    path = shutil.which(name)
    if not path:
        fail(f"Required command not found: {name}")
    return path


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def process_running(name):
    return subprocess.run(
        ["pgrep", "-x", name],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    ).returncode == 0


def main():
    here = Path(__file__).resolve().parent
    archive = here / ARCHIVE_NAME
    output_dir = here / "wallet-output"
    public_output = output_dir / "public-descriptors.json"

    for command in ("nmcli", "pgrep", "tar", "python3"):
        require(command)

    if process_running("bitcoind") or process_running("bitcoin-qt"):
        fail("Another Bitcoin Core process is running. Stop it first.")

    run(["nmcli", "networking", "off"])
    status = subprocess.check_output(
        ["nmcli", "networking"],
        text=True,
        env={**os.environ, "LC_ALL": "C"},
    ).strip()
    if status != "disabled":
        fail("Failed to disable networking.")

    if not archive.is_file():
        fail(f"Missing pinned Core archive: {archive}")
    if sha256_file(archive) != EXPECTED_SHA256:
        fail("Bitcoin Core archive SHA-256 does not match the pinned value.")
    if output_dir.exists():
        fail(f"Refusing to reuse existing output directory: {output_dir}")

    state = Path(tempfile.mkdtemp(prefix="core-helper-import-bip39.", dir="/dev/shm"))
    core_dir = Path(tempfile.mkdtemp(prefix="bitcoin-32.0rc2.", dir="/dev/shm"))
    old_home = os.environ.get("HOME")
    os.environ["HOME"] = str(state)

    bitcoin_cli = core_dir / "bin" / "bitcoin-cli"
    bitcoind = core_dir / "bin" / "bitcoind"
    pidfile = state / "bitcoind.pid"
    cleaned = False

    def cleanup():
        nonlocal cleaned
        if cleaned:
            return
        cleaned = True
        if bitcoin_cli.exists():
            subprocess.run(
                [str(bitcoin_cli), "stop"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        shutil.rmtree(core_dir, ignore_errors=True)
        shutil.rmtree(state, ignore_errors=True)
        if old_home is None:
            os.environ.pop("HOME", None)
        else:
            os.environ["HOME"] = old_home

    def interrupted(_signum, _frame):
        raise KeyboardInterrupt

    atexit.register(cleanup)
    for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
        signal.signal(sig, interrupted)

    run([
        "tar",
        "-xzf",
        str(archive),
        "-C",
        str(core_dir),
        "--strip-components=1",
        "--no-same-owner",
    ])

    if not os.access(bitcoin_cli, os.X_OK) or not os.access(bitcoind, os.X_OK):
        fail("Verified archive did not contain executable Core binaries.")

    output_dir.mkdir(mode=0o700)

    run([
        str(bitcoind),
        "-daemonwait",
        "-networkactive=0",
        "-listen=0",
        f"-walletdir={output_dir}",
        f"-pid={pidfile}",
    ])

    run(["python3", str(here / "generator.py"), str(bitcoin_cli), str(public_output)])

    run([str(bitcoin_cli), "stop"])

    if pidfile.exists():
        try:
            pid = int(pidfile.read_text().strip())
        except (OSError, ValueError):
            pid = None
        if pid:
            for _ in range(30):
                try:
                    os.kill(pid, 0)
                except ProcessLookupError:
                    break
                time.sleep(1)
            else:
                fail("Bitcoin Core did not shut down cleanly.")

    run(["python3", str(here / "render_qr.py"), str(public_output)])
    cleanup()

    print()
    print("Complete. Read POST-CREATION-GUIDE.txt.")


if __name__ == "__main__":
    main()
