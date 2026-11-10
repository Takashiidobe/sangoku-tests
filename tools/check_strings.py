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


def invoke(function, case, seed):
    rng = random.Random(seed)
    a = bytearray(rng.getrandbits(8) for _ in range(512))
    b = bytearray(rng.getrandbits(8) for _ in range(512))
    scenario = case["scenario"]
    lengths = [0, 1, 2, 3, 4, 7, 8, 15, 16, 17, 31, 32, 63, 64, 127, 128]
    n = lengths[seed % len(lengths)]
    fixed = case.get("fixed_length")
    if fixed is not None:
        n = fixed
    left_offset, right_offset = 32 + seed % 8, 32 + (seed // 8) % 8
    if scenario in {
        "length",
        "compare_string",
        "compare_string_n",
        "search_string",
        "copy_string",
        "copy_pad",
    }:
        length = [0, 1, 2, 7, 16, 31, 63][seed % 7]
        text = bytes(rng.randrange(1, 256) for _ in range(length))
        other = (
            text
            if seed % 3 == 0
            else text[:-1]
            if seed % 3 == 1
            else bytes(rng.randrange(1, 256) for _ in range(length))
        )
        a[left_offset : left_offset + len(text) + 1] = text + b"\0"
        b[right_offset : right_offset + len(other) + 1] = other + b"\0"
    elif seed % 3 == 0:
        b[right_offset : right_offset + 128] = a[left_offset : left_offset + 128]
    array = ctypes.c_uint8 * 512
    left, right = array.from_buffer_copy(a), array.from_buffer_copy(b)
    base_left, base_right = ctypes.addressof(left), ctypes.addressof(right)
    addresses = {
        "a": base_left + left_offset,
        "b": base_right + right_offset,
        "s": base_left + left_offset,
        "src": base_left + left_offset,
        "dst": base_right + 192 + seed % 8,
    }
    if scenario == "memmove":
        src_offset, dst_offset = [(64, 66), (66, 64), (64, 64), (16, 128)][seed % 4]
        addresses["src"] = base_left + src_offset + seed % 8
        addresses["dst"] = base_left + dst_offset + seed % 8
    value = [0, 1, 127, 128, 255, left[left_offset]][seed % 6]
    arguments = [
        n if p == "n" else value if p == "value" else addresses[p]
        for p in case["parameters"]
    ]
    result = function(*arguments)
    if case["result"] == "pointer":
        result -= addresses["dst"]
    return result, bytes(left), bytes(right)


def main():
    parser = argparse.ArgumentParser(
        description="Compare Rust string/memory probes against Clang and host libc."
    )
    parser.add_argument("--cc", default="clang")
    parser.add_argument("--rustc", default="rustc")
    parser.add_argument(
        "--output", type=Path, default=ROOT / "results/string-semantics.json"
    )
    args = parser.parse_args()
    cases = [c for c in generate() if c["kind"] == "string"]
    results = []
    with tempfile.TemporaryDirectory(prefix="sangoku-string-check-") as temp:
        work = Path(temp)
        csource = ROOT / "cases/strings.c"
        rsource = work / "strings.rs"
        rsource.write_text(
            (ROOT / "cases/strings.rs").read_text().replace("#![no_std]\n", "")
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
            outcome = subprocess.run(command, capture_output=True, text=True)
            if outcome.returncode:
                raise RuntimeError(outcome.stderr)
        libraries = [
            ctypes.CDLL(str(work / "c.so")),
            ctypes.CDLL(str(work / "rust.so")),
        ]
        for case in cases:
            functions = [getattr(library, case["id"]) for library in libraries]
            for function in functions:
                function.argtypes = [
                    ctypes.c_uint16
                    if p == "n"
                    else ctypes.c_uint8
                    if p == "value"
                    else ctypes.c_void_p
                    for p in case["parameters"]
                ]
                function.restype = {
                    "pointer": ctypes.c_void_p,
                    "u16": ctypes.c_uint16,
                    "u8": ctypes.c_uint8,
                    "i8": ctypes.c_int8,
                }[case["result"]]
            for seed in range(192):
                expected, actual = [invoke(f, case, seed) for f in functions]
                if actual != expected:
                    raise AssertionError(
                        f"{case['id']}: seed {seed}, Rust result {actual[0]}, C reference {expected[0]}, buffers equal: {actual[1:] == expected[1:]}"
                    )
            results.append({"id": case["id"], "vectors": 192, "status": "passed"})
    report = {
        "status": "passed",
        "reference": "Clang-compiled C and host libc",
        "scope": "host source equivalence; entire buffers and relative return pointers checked; not SM83 execution",
        "source_sha256": {
            path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
            for path in ["cases/strings.c", "cases/strings.rs"]
        },
        "tools": {
            name: subprocess.run(
                command, check=True, capture_output=True, text=True
            ).stdout
            for name, command in [
                ("clang", [args.cc, "--version"]),
                ("rustc", [args.rustc, "-Vv"]),
            ]
        },
        "cases": results,
        "vectors_per_language": sum(r["vectors"] for r in results),
        "commands": commands,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(
        f"Passed {report['vectors_per_language']} vectors per language across {len(cases)} string/memory cases"
    )


if __name__ == "__main__":
    main()
