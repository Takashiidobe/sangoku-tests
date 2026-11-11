#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path
import platform
import subprocess


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "https://github.com/llvm-z80/rust-z80.git"
COMMIT = "eb0fd89a09b213daaeb4c86a8e4417f4b56067ca"
HOST = "x86_64-unknown-linux-gnu"
TARGET = "sm83-nintendo-none-elf"
DEFAULT_SOURCE = ROOT / "build/rust-z80-src"
DEFAULT_BUILD = ROOT / "build/rust-z80-build"
DEFAULT_RUSTC = DEFAULT_BUILD / HOST / "stage1/bin/rustc"


def run(command, cwd=None):
    subprocess.run(list(map(str, command)), cwd=cwd, check=True)


def checkout(directory):
    if not (directory / ".git").exists():
        directory.mkdir(parents=True, exist_ok=True)
        run(["git", "init", directory])
        run(["git", "remote", "add", "origin", REPOSITORY], directory)
        run(["git", "fetch", "--depth", "1", "origin", COMMIT], directory)
        run(["git", "checkout", "--detach", "FETCH_HEAD"], directory)
    actual = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=directory, text=True
    ).strip()
    if actual != COMMIT:
        raise ValueError(
            f"{directory} is at {actual}; use a separate --source for the pinned {COMMIT}"
        )
    run(
        ["git", "submodule", "update", "--init", "--depth", "1", "src/llvm-project"],
        directory,
    )


def configuration(build, jobs):
    return f'''[build]
build-dir = {json.dumps(str(build))}
target = ["{HOST}", "{TARGET}"]
docs = false
extended = false
jobs = {jobs}
ccache = true

[llvm]
download-ci-llvm = false
targets = "X86"
experimental-targets = "Z80"
assertions = false
link-shared = true
link-jobs = 1
ldflags = "-fuse-ld=lld"

[rust]
download-rustc = false
deny-warnings = false
lld = true
debuginfo-level = 0
codegen-units = 16

[target.{HOST}]
cc = "clang"
cxx = "clang++"

[target.{TARGET}]
optimized-compiler-builtins = false
rustflags = ["-Cllvm-args=-z80-warn-stack-align-padding=0"]
'''


def main():
    parser = argparse.ArgumentParser(
        description="Build the pinned native Rust-Z80 reference compiler and SM83 core/alloc."
    )
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--build", type=Path, default=DEFAULT_BUILD)
    parser.add_argument("--jobs", type=int, default=min(os.cpu_count() or 1, 8))
    args = parser.parse_args()
    if (platform.system(), platform.machine()) != ("Linux", "x86_64"):
        parser.error(
            "this build configuration requires Linux x86_64; pass an existing compiler with --llvm-rustc"
        )
    if args.jobs < 1:
        parser.error("--jobs must be positive")
    args.source, args.build = args.source.resolve(), args.build.resolve()
    checkout(args.source)
    args.build.mkdir(parents=True, exist_ok=True)
    config = args.build.parent / (args.build.name + "-bootstrap.toml")
    config.write_text(configuration(args.build, args.jobs))
    for paths, targets in [
        (["compiler/rustc"], HOST),
        (["library/core", "library/alloc"], TARGET),
    ]:
        run(
            [
                args.source / "x",
                "build",
                "--config",
                config,
                "--stage",
                "1",
                "--target",
                targets,
                *paths,
            ],
            args.source,
        )
    rustc = args.build / HOST / "stage1/bin/rustc"
    run([rustc, "-Vv"])
    metadata = {
        "repository": REPOSITORY,
        "commit": COMMIT,
        "llvm_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=args.source / "src/llvm-project",
            text=True,
        ).strip(),
        "config": config.read_text(),
        "rustc": str(rustc),
    }
    (args.build / "toolchain.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(f"Native reference compiler: {rustc}")


if __name__ == "__main__":
    main()
