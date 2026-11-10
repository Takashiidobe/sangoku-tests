#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path
import random
import subprocess
import tempfile

from generate import ROOT, generate


def signed(value, width):
    return value - (1 << width) if value & (1 << (width - 1)) else value


def vectors(case):
    width = case["width"]
    mask = (1 << width) - 1
    edges = [
        0,
        1,
        2,
        3,
        7,
        width - 1,
        width,
        width + 1,
        mask,
        mask - 1,
        1 << (width - 1),
        (1 << (width - 1)) - 1,
    ]
    rng = random.Random(617 + width)
    pairs = [(a, b) for a in edges for b in edges] + [
        (rng.getrandbits(width), rng.getrandbits(width)) for _ in range(32)
    ]
    unary = "b:" not in case["rust_function"]
    if unary:
        pairs = list(dict.fromkeys((a, 0) for a, _ in pairs))
    for a, b in pairs:
        sa, sb = (signed(a, width), signed(b, width)) if case["signed"] else (a, b)
        if case["operation"] in {"div", "rem"} and (
            sb == 0 or (case["signed"] and sa == -(1 << (width - 1)) and sb == -1)
        ):
            continue
        yield a, b


def c_literal(value):
    return f"(((unsigned __int128)0x{value >> 64:x}ULL << 64) | 0x{value & ((1 << 64) - 1):x}ULL)"


def main():
    parser = argparse.ArgumentParser(
        description="Compare host Rust integer results with a compiled C reference."
    )
    parser.add_argument("--cc", default="clang")
    parser.add_argument("--rustc", default="rustc")
    parser.add_argument("--output", type=Path, default=ROOT / "results/semantics.json")
    args = parser.parse_args()
    cases = [c for c in generate() if c["kind"] == "integer"]
    csrc = ["#include <stdint.h>", "#include <stdio.h>"]
    rsrc = [
        "#![feature(core_intrinsics)]",
        "#![allow(internal_features, improper_ctypes_definitions)]",
    ]
    csrc += [c["c_function"] for c in cases]
    rsrc += [c["rust_function"] for c in cases]
    csrc += ["int main(void) {"]
    rsrc += ["fn main() {"]
    vector_count = 0
    for case in cases:
        ty, width, op, name = case["type"], case["width"], case["operation"], case["id"]
        cty = (
            (f"int{width}_t" if case["signed"] else f"uint{width}_t")
            if width <= 64
            else ("__int128" if case["signed"] else "unsigned __int128")
        )
        output_width = case.get("result_width", width)
        uty = f"uint{output_width}_t" if output_width <= 64 else "unsigned __int128"
        unary = "b:" not in case["rust_function"]
        bty = "u8" if op in {"shl", "shr", "rol", "ror"} else ty
        cbty = "uint8_t" if op in {"shl", "shr", "rol", "ror"} else cty
        values = list(vectors(case))
        csrc += [
            "{ struct { unsigned __int128 a, b; } pairs[] = {",
            ",\n".join(f"{{{c_literal(a)}, {c_literal(b)}}}" for a, b in values),
            "};",
            "for (unsigned i = 0; i < sizeof(pairs)/sizeof(pairs[0]); ++i) {",
        ]
        cargs = f"({cty})pairs[i].a" + ("" if unary else f", ({cbty})pairs[i].b")
        csrc += [
            f"unsigned __int128 v = ({uty}){name}({cargs});",
            f'printf("{name}:%u:%016llx%016llx\\n", i, (unsigned long long)(v >> 64), (unsigned long long)v);',
            "}}",
        ]
        rsrc += [
            "{ let pairs: &[(u128, u128)] = &[",
            ",\n".join(f"({a}, {b})" for a, b in values),
            "];",
            "for (i, &(a, b)) in pairs.iter().enumerate() {",
        ]
        rargs = f"a as {ty}" + ("" if unary else f", b as {bty}")
        expr = f"{name}({rargs})"
        if op in {"div", "rem"}:
            expr = f"unsafe {{ {expr} }}"
        rsrc += [
            f"let v = ({expr}) as u{output_width} as u128;",
            f'println!("{name}:{{i}}:{{v:032x}}");',
            "}}",
        ]
        vector_count += len(values)
    csrc += ["return 0; }"]
    rsrc += ["}"]
    with tempfile.TemporaryDirectory(prefix="sangoku-semantics-") as temp:
        work = Path(temp)
        (work / "check.c").write_text("\n".join(csrc))
        (work / "check.rs").write_text("\n".join(rsrc))
        commands = [
            [
                args.cc,
                "-std=c11",
                "-O1",
                "-fsanitize=undefined",
                "-fno-sanitize-recover=all",
                str(work / "check.c"),
                "-o",
                str(work / "c"),
            ],
            [
                args.rustc,
                "--edition=2024",
                "-Copt-level=1",
                "-Awarnings",
                str(work / "check.rs"),
                "-o",
                str(work / "rust"),
            ],
        ]
        for command in commands:
            subprocess.run(command, check=True, capture_output=True, text=True)
        expected = subprocess.run(
            [work / "c"], check=True, capture_output=True, text=True
        ).stdout.splitlines()
        actual = subprocess.run(
            [work / "rust"], check=True, capture_output=True, text=True
        ).stdout.splitlines()
        if len(expected) != vector_count or actual != expected:
            mismatch = next(
                ((a, b) for a, b in zip(actual, expected) if a != b),
                (len(actual), len(expected)),
            )
            raise AssertionError(f"Rust/C mismatch (Rust, C reference): {mismatch}")
    report = {
        "status": "passed",
        "source_sha256": {
            path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
            for path in sorted(
                {c[key] for c in cases for key in ["c_source", "rust_source"]}
            )
        },
        "tools": {
            "c": subprocess.run(
                [args.cc, "--version"], check=True, capture_output=True, text=True
            ).stdout,
            "rust": subprocess.run(
                [args.rustc, "-Vv"], check=True, capture_output=True, text=True
            ).stdout,
        },
        "integer_cases": len(cases),
        "vectors_per_language": len(expected),
        "reference": "compiled host C program",
        "reference_compiler": args.cc,
        "c_undefined_behavior_sanitizer": True,
        "scope": "host C/Rust source equivalence; does not execute SM83 code or validate floating-point runtime helpers",
        "commands": commands,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(
        f"Passed {len(expected)} vectors for each language across {len(cases)} integer cases"
    )


if __name__ == "__main__":
    main()
