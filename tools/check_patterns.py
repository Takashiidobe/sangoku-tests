#!/usr/bin/env python3
import argparse
from collections import defaultdict
import ctypes
import hashlib
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile

from generate import ROOT, generate

SCALARS = {
    "u8": ctypes.c_uint8,
    "u16": ctypes.c_uint16,
    "u32": ctypes.c_uint32,
    "u64": ctypes.c_uint64,
    "i16": ctypes.c_int16,
    "pointer": ctypes.c_void_p,
}


class Pair(ctypes.Structure):
    _fields_ = [("ptr", ctypes.c_void_p), ("len", ctypes.c_uint16)]


def result_type(name):
    if name == "PatternPair":
        return Pair
    if name.startswith("PatternBlob"):
        size = int(name.removeprefix("PatternBlob"))

        class Blob(ctypes.Structure):
            _fields_ = [("bytes", ctypes.c_uint8 * size)]

        return Blob
    return SCALARS[name]


def invoke(function, case, seed):
    rng = random.Random(1741 + seed)
    data = [bytearray(rng.getrandbits(8) for _ in range(512)) for _ in range(4)]
    source, output, other, charset = data
    words = any(
        p["role"] in {"sorted_words", "words_output"} for p in case["parameters"]
    )
    offset = 32 + (seed % 4) * 2 if words else 32 + seed % 8
    out_offset = 64 + (seed % 4) * 2 if words else 64 + seed % 8
    lengths = [0, 1, 2, 3, 4, 7, 8, 15, 16, 17, 31, 32, 63, 64, 127, 128]
    n = lengths[seed % len(lengths)]
    family, op = case["pattern_family"], case["operation"]

    def put(buffer, text, where=offset):
        buffer[where : where + len(text) + 1] = text + b"\0"

    if family == "parsing":
        texts = [
            b"",
            b"0",
            b"1",
            b"123",
            b"4294967295",
            b"  +42tail",
            b"-1",
            b" -42!",
            b"+",
            b"bad",
            b"\t\n123 rest",
            b"000001",
        ]
        if op == "decimal_checked":
            texts += [b"4294967296", b"9999999999999999999999999", b"-4294967296"]
        elif op == "atoi":
            texts = [
                b"",
                b"0",
                b"1",
                b"-1",
                b"32767",
                b"-32768",
                b"  +123end",
                b" -42!",
                b"+",
                b"bad",
            ]
        elif op == "hex_loop":
            texts = [
                b"",
                b"0",
                b"0x",
                b"0x0",
                b"0xdeadbeef!",
                b"FFFFFFFF",
                b"abcdef",
                b"123garbage",
                b"0X12aB",
            ]
        if seed < len(texts) * 2:
            text = texts[seed % len(texts)]
        else:
            value = rng.randrange(32768 if op == "atoi" else 1 << 32)
            text = (
                hex(value)
                if op == "hex_loop"
                else ("-" if seed % 3 == 0 else "+") + str(value)
            ).encode() + b"end"
        put(source, text)
    elif family in {"spans", "substring", "concat"}:
        strings = [
            b"",
            b"a",
            b"abc123,;xyz",
            b"abababac",
            b"prefix suffix",
            bytes([255, 128, 65]),
            b"1234567890",
            b" " * 31,
        ]
        text = (
            strings[seed % len(strings)]
            if seed < 64
            else bytes(rng.randrange(1, 256) for _ in range(seed % 129))
        )
        put(source, text)
        needle = [
            b"",
            text,
            text[1:],
            b"not found",
            b"a",
            b"ab",
            bytes([128]),
            text[:4],
        ][seed % 8]
        put(other, needle)
        put(
            charset,
            [
                b"",
                b"0123456789",
                b",;",
                b"abcxyz",
                bytes([128, 255]),
                b" ",
                text,
                b"abcdefghijklmnopqrstuvwxyz",
            ][seed % 8],
        )
        prefix = b"prefix"[: seed % 7] if seed % 2 else b"x" * (seed % 32)
        put(output, prefix, out_offset)
        if op in {"needle2", "needle4"}:
            size = 2 if op == "needle2" else 4
            if n >= size and seed % 3 != 2:
                index = 0 if seed % 3 == 0 else n - size
                other[offset : offset + size] = source[
                    offset + index : offset + index + size
                ]
    if family == "search_sort":
        for i in range(128):
            source[offset + 2 * i : offset + 2 * i + 2] = (i * 4 + seed % 3).to_bytes(
                2, sys.byteorder
            )
            value = [0, 1, 65535, rng.randrange(65536)][(seed + i) % 4]
            output[out_offset + 2 * i : out_offset + 2 * i + 2] = value.to_bytes(
                2, sys.byteorder
            )
    if family == "dispatch" and op == "parser_state":
        text = [b"0:123,45", b"12,34,56", b" :1,2::3", b"bad\xff", b"65535,99999", b""][
            seed % 6
        ]
        for i in range(n):
            source[offset + i] = text[i % len(text)] if text else 0
    arrays = [
        (ctypes.c_uint8 * len(buffer)).from_buffer_copy(buffer) for buffer in data
    ]
    pointers = {
        "input": ctypes.addressof(arrays[0]) + offset,
        "output": ctypes.addressof(arrays[1]) + out_offset,
        "other": ctypes.addressof(arrays[2]) + offset,
        "set": ctypes.addressof(arrays[3]) + offset,
    }
    pointers["sorted_words"] = pointers["input"]
    pointers["words_output"] = pointers["output"]
    end = ctypes.c_uint16(0x7777)
    pointers["end"] = ctypes.addressof(end)
    arguments = []
    for param in case["parameters"]:
        if param["abi"] == "ptr":
            arguments.append(pointers[param["role"]])
        elif param["role"] in {"length", "capacity"}:
            arguments.append(n)
        else:
            width = int(param["abi"][1:])
            mask = (1 << width) - 1
            edge = [0, 1, 9, 10, 15, 16, 99, 100, mask, mask - 1, 1 << (width - 1)]
            value = (
                seed
                if family in {"ctype", "dispatch"}
                else edge[seed % len(edge)]
                if seed < 64
                else rng.getrandbits(width)
            )
            if (
                family == "search_sort"
                and param["role"] == "value"
                and n
                and seed % 3 == 0
            ):
                value = (seed % n) * 4 + seed % 3
            arguments.append(value)
    result = function(*arguments)
    if case["result"] == "pointer":
        result -= pointers["output"]
    elif case["result"] == "PatternPair":
        result = (result.ptr - pointers["input"], result.len)
    elif case["result"].startswith("PatternBlob"):
        result = bytes(result.bytes)
    return result, end.value, tuple(bytes(a) for a in arrays)


def main():
    parser = argparse.ArgumentParser(
        description="Validate libc-style pattern pairs against host Clang."
    )
    parser.add_argument("--cc", default="clang")
    parser.add_argument("--rustc", default="rustc")
    parser.add_argument("--case", nargs="+")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.output is None:
        filename = (
            (
                args.case[0] + "-semantics.json"
                if len(args.case) == 1
                else "selected-pattern-semantics.json"
            )
            if args.case
            else "pattern-semantics.json"
        )
        args.output = ROOT / "results" / filename
    cases = [c for c in generate() if c["kind"] == "pattern"]
    if args.case:
        missing = set(args.case) - {c["id"] for c in cases}
        if missing:
            parser.error("unknown pattern cases: " + ", ".join(sorted(missing)))
        cases = [c for c in cases if c["id"] in args.case]
    groups = defaultdict(list)
    for case in cases:
        groups[case["type"]].append(case)
    results, commands = [], []
    with tempfile.TemporaryDirectory(prefix="sangoku-pattern-check-") as temp:
        work = Path(temp)
        for group, members in groups.items():
            cpath = ROOT / members[0]["c_source"]
            rpath = work / f"{group}.rs"
            rpath.write_text(
                (ROOT / members[0]["rust_source"])
                .read_text()
                .replace("#![no_std]\n", "")
            )
            build_commands = [
                [
                    args.cc,
                    "-std=c11",
                    "-O2",
                    "-shared",
                    "-fPIC",
                    str(cpath),
                    "-o",
                    str(work / f"{group}-c.so"),
                ],
                [
                    args.rustc,
                    "--edition=2024",
                    "--crate-type=cdylib",
                    "-Copt-level=2",
                    str(rpath),
                    "-o",
                    str(work / f"{group}-rust.so"),
                ],
            ]
            for command in build_commands:
                outcome = subprocess.run(command, capture_output=True, text=True)
                if outcome.returncode:
                    raise RuntimeError(outcome.stderr)
            commands.extend(build_commands)
            libraries = [
                ctypes.CDLL(str(work / f"{group}-{lang}.so")) for lang in ["c", "rust"]
            ]
            for case in members:
                functions = [getattr(lib, case["id"]) for lib in libraries]
                for function in functions:
                    function.argtypes = [
                        ctypes.c_void_p if p["abi"] == "ptr" else SCALARS[p["abi"]]
                        for p in case["parameters"]
                    ]
                    function.restype = result_type(case["result"])
                for seed in range(256):
                    expected, actual = [
                        invoke(function, case, seed) for function in functions
                    ]
                    if expected != actual:
                        raise AssertionError(
                            f"{case['id']} vector {seed}: C result {expected[:2]}, Rust {actual[:2]}, buffers equal {expected[2] == actual[2]}"
                        )
                results.append({"id": case["id"], "vectors": 256, "status": "passed"})
            print(f"checked {group}: {len(members)} cases", flush=True)
    report = {
        "status": "passed",
        "reference": "Clang and host libc",
        "tools": {
            "clang": subprocess.run(
                [args.cc, "--version"], check=True, capture_output=True, text=True
            ).stdout,
            "rustc": subprocess.run(
                [args.rustc, "-Vv"], check=True, capture_output=True, text=True
            ).stdout,
        },
        "scope": "host source equivalence of scalar/aggregate results, end offsets and complete buffers; not SM83 execution",
        "cases": results,
        "vectors_per_language": sum(r["vectors"] for r in results),
        "source_sha256": {
            p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
            for p in sorted(
                {c[key] for c in cases for key in ["c_source", "rust_source"]}
            )
        },
        "commands": commands,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(
        f"Passed {report['vectors_per_language']} vectors per language across {len(cases)} pattern cases"
    )


if __name__ == "__main__":
    main()
