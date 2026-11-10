#!/usr/bin/env python3
import json
from pathlib import Path

from call_cases import generate_calls
from pattern_cases import generate_patterns
from string_cases import generate_strings

ROOT = Path(__file__).resolve().parents[1]


def integer_cases(ty):
    bits = int(ty[1:])
    signed = ty[0] == "i"
    u = f"uint{bits}_t" if bits <= 64 else "unsigned __int128"
    cty = (
        (f"int{bits}_t" if signed else u)
        if bits <= 64
        else ("__int128" if signed else u)
    )
    calc = "uint32_t" if bits < 32 else u
    a, b = f"({calc})({u})a", f"({calc})({u})b"
    for op, token, method in [
        ("add", "+", "wrapping_add"),
        ("sub", "-", "wrapping_sub"),
        ("mul", "*", "wrapping_mul"),
    ]:
        yield (
            op,
            cty,
            f"{cty} a, {cty} b",
            f"a: {ty}, b: {ty}",
            f"return ({cty})({a} {token} {b});",
            f"a.{method}(b)",
            "all bit patterns; result wraps modulo 2^width",
        )
    for op in ["div", "rem"]:
        token = "/" if op == "div" else "%"
        yield (
            op,
            cty,
            f"{cty} a, {cty} b",
            f"a: {ty}, b: {ty}",
            f"return a {token} b;",
            f"unsafe {{ core::intrinsics::unchecked_{op}(a, b) }}",
            "b != 0" + ("; exclude MIN / -1 and MIN % -1" if signed else ""),
        )
    for op, token in [("and", "&"), ("or", "|"), ("xor", "^")]:
        yield (
            op,
            cty,
            f"{cty} a, {cty} b",
            f"a: {ty}, b: {ty}",
            f"return a {token} b;",
            f"a {token} b",
            "all bit patterns",
        )
    for op, token in [
        ("eq", "=="),
        ("ne", "!="),
        ("lt", "<"),
        ("le", "<="),
        ("gt", ">"),
        ("ge", ">="),
    ]:
        yield (
            op,
            "uint8_t",
            f"{cty} a, {cty} b",
            f"a: {ty}, b: {ty}",
            f"return a {token} b;",
            f"(a {token} b) as u8",
            "returns 0 or 1",
        )
    for op in ["min", "max"]:
        token = "<" if op == "min" else ">"
        yield (
            op,
            cty,
            f"{cty} a, {cty} b",
            f"a: {ty}, b: {ty}",
            f"return a {token} b ? a : b;",
            f"if a {token} b {{ a }} else {{ b }}",
            "all bit patterns",
        )
    for op, ce, re in [
        ("not", "~a", "!a"),
        ("neg", f"({cty})(0 - {a})", "a.wrapping_neg()"),
        ("add1", f"({cty})({a} + 1)", "a.wrapping_add(1)"),
        ("mul3", f"({cty})({a} * 3)", "a.wrapping_mul(3)"),
        ("mul10", f"({cty})({a} * 10)", "a.wrapping_mul(10)"),
        ("div3", "a / 3", "a / 3"),
        ("rem10", "a % 10", "a % 10"),
    ]:
        yield (
            op,
            cty,
            f"{cty} a",
            f"a: {ty}",
            f"return {ce};",
            re,
            "all bit patterns; arithmetic wraps where needed",
        )
    for op, token in [("shl", "<<"), ("shr", ">>")]:
        lhs = a if op == "shl" else "a"
        yield (
            op,
            cty,
            f"{cty} a, uint8_t b",
            f"a: {ty}, b: u8",
            f"return ({cty})({lhs} {token} (b & {bits - 1}));",
            f"a.wrapping_{op}(b as u32)",
            "shift count masked to width - 1; signed right shift is arithmetic",
        )
        for count in [1, 7]:
            yield (
                f"{op}{count}",
                cty,
                f"{cty} a",
                f"a: {ty}",
                f"return ({cty})({lhs} {token} {count});",
                f"a.wrapping_{op}({count})",
                "all bit patterns; signed right shift is arithmetic",
            )

    for op, method, left, right in [
        ("rol", "rotate_left", "<<", ">>"),
        ("ror", "rotate_right", ">>", "<<"),
    ]:
        count = f"(b & {bits - 1})"
        other = f"((0u - {count}) & {bits - 1})"
        yield (
            op,
            cty,
            f"{cty} a, uint8_t b",
            f"a: {ty}, b: u8",
            f"return ({cty})(({a} {left} {count}) | ({a} {right} {other}));",
            f"a.{method}(b as u32)",
            "rotates the bit pattern; count masked to width - 1",
        )
    signed_type = f"int{bits}_t" if bits <= 64 else "__int128"
    for op, target_c, target_r in [
        ("as_signed", signed_type, f"i{bits}"),
        ("as_unsigned", u, f"u{bits}"),
    ]:
        yield (
            op,
            target_c,
            f"{cty} a",
            f"a: {ty}",
            f"return ({target_c})a;",
            f"a as {target_r}",
            "two's complement bit-pattern cast",
        )
    if bits > 8:
        target_c = f"uint{bits // 2}_t"
        yield (
            "narrow",
            target_c,
            f"{cty} a",
            f"a: {ty}",
            f"return ({target_c})a;",
            f"a as u{bits // 2}",
            "keeps the low half of the bit pattern",
        )
    if bits < 64:
        target_r = f"{ty[0]}{bits * 2}"
        target_c = f"{'u' if not signed else ''}int{bits * 2}_t"
        yield (
            "widen",
            target_c,
            f"{cty} a",
            f"a: {ty}",
            f"return ({target_c})a;",
            f"a as {target_r}",
            "sign extension for signed inputs; zero extension for unsigned inputs",
        )


def float_cases(ty):
    cty = {"f16": "_Float16", "f32": "float", "f64": "double", "f128": "long double"}[
        ty
    ]
    for op, token in [("add", "+"), ("sub", "-"), ("mul", "*"), ("div", "/")]:
        yield (
            op,
            cty,
            f"{cty} a, {cty} b",
            f"a: {ty}, b: {ty}",
            f"return a {token} b;",
            f"a {token} b",
            "IEEE arithmetic, no fast-math; runtime helper edge behavior not validated",
        )
    for op, token in [
        ("eq", "=="),
        ("ne", "!="),
        ("lt", "<"),
        ("le", "<="),
        ("gt", ">"),
        ("ge", ">="),
    ]:
        yield (
            op,
            "uint8_t",
            f"{cty} a, {cty} b",
            f"a: {ty}, b: {ty}",
            f"return a {token} b;",
            f"(a {token} b) as u8",
            "unordered inequality; NaN returns true"
            if op == "ne"
            else "ordered comparison; NaN returns false",
        )
    yield "neg", cty, f"{cty} a", f"a: {ty}", "return -a;", "-a", "includes signed zero"


def generate():
    manifest = []
    types = [
        f"{sign}{width}" for width in [8, 16, 32, 64, 128] for sign in ["u", "i"]
    ] + ["f16", "f32", "f64", "f128"]
    for ty in types:
        floating = ty.startswith("f")
        bits = int(ty[1:])
        cty = {
            "f16": "_Float16",
            "f32": "float",
            "f64": "double",
            "f128": "long double",
        }.get(ty, f"{'u' if ty[0] == 'u' else ''}int{bits}_t")
        if not floating and bits == 128:
            cty = "unsigned __int128" if ty[0] == "u" else "__int128"
        c = [
            "#include <stdint.h>",
            f'_Static_assert(sizeof({cty}) * 8 == {bits}, "required width: {ty}");',
        ]
        if ty.startswith("i"):
            c += [
                '_Static_assert((-1 >> 1) == -1, "arithmetic signed right shift required");'
            ]
        features = (
            ([ty] if ty in {"f16", "f128"} else []) if floating else ["core_intrinsics"]
        )
        rust = [
            "#![no_std]",
            *([f"#![feature({', '.join(features)})]"] if features else []),
            "#![allow(internal_features, improper_ctypes_definitions)]",
        ]
        for op, ret, cp, rp, cb, rb, domain in (
            float_cases(ty) if floating else integer_cases(ty)
        ):
            name = f"{ty}_{op}"
            type_map = {
                f"{prefix}int{width}_t": f"{sign}{width}"
                for width in [8, 16, 32, 64]
                for prefix, sign in [("u", "u"), ("", "i")]
            }
            type_map.update({"unsigned __int128": "u128", "__int128": "i128"})
            rret = type_map.get(ret, ty)
            cfn = f"{ret} {name}({cp}) {{ {cb} }}"
            unsafety = "unsafe " if not floating and op in {"div", "rem"} else ""
            rfn = f'#[unsafe(no_mangle)]\n#[inline(never)]\npub {unsafety}extern "C" fn {name}({rp}) -> {rret} {{ {rb} }}'
            c += ["", cfn]
            rust += ["", rfn]
            manifest.append(
                {
                    "id": name,
                    "type": ty,
                    "width": bits,
                    "kind": "float" if floating else "integer",
                    "signed": ty.startswith("i") if not floating else None,
                    "operation": op,
                    "result_type": rret,
                    "result_width": int(rret[1:]),
                    "domain": domain,
                    "c_source": f"cases/{ty}.c",
                    "rust_source": f"cases/{ty}.rs",
                    "c_function": cfn,
                    "rust_function": rfn,
                }
            )
        (ROOT / f"cases/{ty}.c").write_text("\n".join(c) + "\n")
        (ROOT / f"cases/{ty}.rs").write_text("\n".join(rust) + "\n")
    manifest.extend(generate_strings())
    manifest.extend(generate_calls())
    manifest.extend(generate_patterns())
    (ROOT / "cases/manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


if __name__ == "__main__":
    print(f"Generated {len(generate())} paired probes")
