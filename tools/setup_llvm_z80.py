#!/usr/bin/env python3
import argparse
import hashlib
from pathlib import Path
import platform
import subprocess
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
RELEASE = "llvmz80-23.1.4-r1"
PACKAGE = "LLVM-Z80-23.1.4-r1-Linux-X64"
SHA256 = "b6b95f749eec9eca727c0554185c98c8076ec504f522f397ec41eaf9a5d2ccef"
URL = (
    f"https://github.com/llvm-z80/llvm-z80/releases/download/{RELEASE}/{PACKAGE}.tar.xz"
)
DEFAULT_BIN = ROOT / "build/llvm-z80" / PACKAGE / "bin"


def main():
    parser = argparse.ArgumentParser(
        description="Install the pinned LLVM-Z80 reference tools."
    )
    parser.add_argument("--directory", type=Path, default=DEFAULT_BIN.parent.parent)
    parser.add_argument(
        "--archive", type=Path, help="Use an already downloaded release archive"
    )
    args = parser.parse_args()
    if (platform.system(), platform.machine()) != ("Linux", "x86_64"):
        parser.error(
            "the pinned package requires Linux x86_64; pass your own tools to compare.py --llvm-z80"
        )
    args.directory.mkdir(parents=True, exist_ok=True)
    archive = args.archive or args.directory / (PACKAGE + ".tar.xz")
    if not archive.is_file():
        print(f"Downloading {URL}", flush=True)
        temporary = archive.with_suffix(".download")
        urllib.request.urlretrieve(URL, temporary)
        temporary.replace(archive)
    with archive.open("rb") as source:
        digest = hashlib.sha256()
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    if digest.hexdigest() != SHA256:
        parser.error(f"SHA-256 mismatch: {archive}; remove it and retry")
    subprocess.run(
        ["tar", "-xf", str(archive.resolve()), "-C", str(args.directory.resolve())],
        check=True,
    )
    print(args.directory.resolve() / PACKAGE / "bin")
    print("Frontend: rustup toolchain install nightly-2026-10-25 --profile minimal")


if __name__ == "__main__":
    main()
