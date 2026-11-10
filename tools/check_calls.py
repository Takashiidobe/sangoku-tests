#!/usr/bin/env python3
import argparse
import ctypes
import hashlib
import json
from pathlib import Path
import random
import subprocess
import tempfile

from generate import ROOT, generate


def main():
    parser = argparse.ArgumentParser(
        description="Compare function-call and register-pressure fixtures against host Clang."
    )
    parser.add_argument("--cc", default="clang")
    parser.add_argument("--rustc", default="rustc")
    parser.add_argument(
        "--output", type=Path, default=ROOT / "results/call-semantics.json"
    )
    args = parser.parse_args()
    cases = [c for c in generate() if c["kind"] == "call"]
    cpaths = sorted({c["c_source"] for c in cases})
    rpaths = sorted({c["rust_source"] for c in cases})
    results = []
    with tempfile.TemporaryDirectory(prefix="sangoku-call-check-") as temp:
        work = Path(temp)
        csource, rsource = work / "calls.c", work / "calls.rs"
        csource.write_text("\n".join((ROOT / p).read_text() for p in cpaths))
        rsource.write_text(
            "#![allow(unused_unsafe)]\n"
            + "\n".join(
                (ROOT / p).read_text().replace("#![no_std]\n", "") for p in rpaths
            )
        )
        commands = [
            [
                args.cc,
                "-std=c11",
                "-O2",
                "-shared",
                "-fPIC",
                str(csource),
                "-o",
                str(work / "c.so"),
            ],
            [
                args.rustc,
                "--edition=2024",
                "--crate-type=cdylib",
                "-Copt-level=2",
                str(rsource),
                "-o",
                str(work / "rust.so"),
            ],
        ]
        for command in commands:
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode:
                raise RuntimeError(result.stderr)
        libraries = [
            ctypes.CDLL(str(work / "c.so")),
            ctypes.CDLL(str(work / "rust.so")),
        ]
        for case in cases:
            scalar = {
                8: ctypes.c_uint8,
                16: ctypes.c_uint16,
                32: ctypes.c_uint32,
                64: ctypes.c_uint64,
            }[case["width"]]
            functions = [getattr(lib, case["id"]) for lib in libraries]
            op = case["operation"]
            for function in functions:
                function.argtypes = (
                    [ctypes.c_void_p, scalar, scalar]
                    if op.startswith("live") or op == "indirect"
                    else [scalar] * (6 if op == "args6" else 3 if op == "chain" else 2)
                )
                function.restype = scalar
            mask = (1 << case["width"]) - 1
            rng = random.Random(975 + case["width"])
            for index in range(128):
                edge = [0, 1, 2, mask, mask - 1, 1 << (case["width"] - 1)]
                values = [
                    edge[(index + j) % len(edge)]
                    if index < 12
                    else rng.getrandbits(case["width"])
                    for j in range(8)
                ]
                outcomes = []
                for lib, function in zip(libraries, functions):
                    array = (scalar * 8)(*values)
                    if op == "indirect":
                        helper = getattr(lib, "fixture_leaf_u" + str(case["width"]))
                        call_args = [
                            ctypes.cast(helper, ctypes.c_void_p),
                            values[0],
                            values[1],
                        ]
                    elif op.startswith("live"):
                        call_args = [ctypes.addressof(array), values[0], values[1]]
                    else:
                        call_args = values[
                            : 6 if op == "args6" else 3 if op == "chain" else 2
                        ]
                    outcomes.append((function(*call_args), list(array)))
                if outcomes[0] != outcomes[1]:
                    raise AssertionError(
                        f"{case['id']} vector {index}: C {outcomes[0]}, Rust {outcomes[1]}"
                    )
            results.append({"id": case["id"], "status": "passed", "vectors": 128})
    report = {
        "status": "passed",
        "reference": "Clang-compiled C",
        "scope": "host result and unchanged input-array equivalence; not SM83 execution or stack-depth measurement",
        "cases": results,
        "vectors_per_language": sum(c["vectors"] for c in results),
        "source_sha256": {
            p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
            for p in cpaths + rpaths
        },
        "commands": commands,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(
        f"Passed {report['vectors_per_language']} vectors per language across {len(cases)} call fixtures"
    )


if __name__ == "__main__":
    main()
