from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
C_HEADER = "#include <stdint.h>\n#include <stddef.h>\n#include <string.h>\n#include <stdlib.h>\n#include <stdio.h>\n#include <ctype.h>\n#if defined(__SDCC)\n#define NOINLINE\n#else\n#define NOINLINE __attribute__((noinline))\n#endif\n"
RUST_HEADER = "#![no_std]\n#![allow(unused_unsafe, improper_ctypes_definitions)]\n"
PARAMS = {
    "dst": ("uint8_t *dst", "dst: *mut u8", "ptr", "output"),
    "src": ("const uint8_t *src", "src: *const u8", "ptr", "input"),
    "other": ("const uint8_t *other", "other: *const u8", "ptr", "other"),
    "set": ("const uint8_t *set", "set: *const u8", "ptr", "set"),
    "end": ("uint16_t *end", "end: *mut u16", "ptr", "end"),
    "n": ("uint16_t n", "n: u16", "u16", "length"),
    "limit": ("uint16_t limit", "limit: u16", "u16", "capacity"),
}
for _bits in [8, 16, 32, 64]:
    PARAMS[f"value{_bits}"] = (
        f"uint{_bits}_t value",
        f"value: u{_bits}",
        f"u{_bits}",
        "value",
    )
RETURNS = {f"u{bits}": (f"uint{bits}_t", f"u{bits}") for bits in [8, 16, 32, 64]}
RETURNS.update({"i16": ("int16_t", "i16"), "pointer": ("uint8_t *", "*mut u8")})


def generate_patterns():
    cases = []
    headers = {}

    def add(
        group,
        op,
        result,
        params,
        cb,
        rb,
        family,
        title,
        note,
        style="matched_loop",
        support=(),
        cextra="",
        rextra="",
        capability=None,
    ):
        name = f"{group}_{op}"
        cty, rty = RETURNS.get(result, (result, result))
        details = [PARAMS[p] for p in params]
        cfn = f"{cty} {name}({', '.join(p[0] for p in details) or 'void'}) {{ {cb} }}"
        rfn = f'#[unsafe(no_mangle)]\n#[inline(never)]\npub unsafe extern "C" fn {name}({", ".join(p[1] for p in details)}) -> {rty} {{ unsafe {{ {rb} }} }}'
        ch, rh = C_HEADER + cextra, RUST_HEADER + rextra
        if group in headers and headers[group] != (ch, rh):
            raise ValueError(f"conflicting headers for {group}")
        headers[group] = (ch, rh)
        sample = []
        for p, meta in zip(params, details):
            if meta[3] == "value":
                sample.append(
                    f"core::ptr::read_volatile(0xc000 as *const {meta[1].split(': ')[1]})"
                )
            elif meta[2] != "ptr":
                sample.append("core::ptr::read_volatile(0xc010 as *const u16)")
            else:
                address = {
                    "output": "0xc100",
                    "input": "0xc300",
                    "other": "0xc500",
                    "set": "0xc600",
                    "end": "0xc700",
                    "sorted_words": "0xc300",
                    "words_output": "0xc100",
                }[meta[3]]
                sample.append(f"{address} as {meta[1].split(': ')[1]}")
        call = f"{name}({', '.join(sample)})"
        value = call + (
            ".bytes[0]"
            if result.startswith("PatternBlob")
            else ".len as u8"
            if result == "PatternPair"
            else " as usize as u8"
            if result == "pointer"
            else " as u8"
        )
        case = {
            "id": name,
            "type": group,
            "kind": "pattern",
            "width": 8,
            "signed": False,
            "operation": op,
            "pattern_family": family,
            "description": title,
            "semantic_note": note,
            "style": style,
            "domain": "valid non-overlapping allocations unless overlap is explicit; lengths <= 128; NUL strings fit their allocations; output buffers have at least 256 bytes; unsigned arithmetic wraps; parse library variants exclude overflow",
            "c_source": f"cases/{group}.c",
            "rust_source": f"cases/{group}.rs",
            "c_function": cfn,
            "rust_function": rfn,
            "c_header": ch,
            "rust_header": rh,
            "parameters": [
                {"name": p, "abi": meta[2], "role": meta[3]}
                for p, meta in zip(params, details)
            ],
            "result": result,
            "support_functions": list(support),
            "link_entry": f"#[unsafe(no_mangle)]\npub fn gbc_main() -> u8 {{ unsafe {{ {value} }} }}",
        }
        if capability:
            case["c_capability_source"] = ch + "\n" + capability
        cases.append(case)

    writer = "struct PatternWriter { dst: *mut u8, len: usize }\nimpl core::fmt::Write for PatternWriter { fn write_str(&mut self, s: &str) -> core::fmt::Result { unsafe { core::ptr::copy_nonoverlapping(s.as_ptr(), self.dst.add(self.len), s.len()); } self.len += s.len(); Ok(()) } }\n"
    for bits in [16, 32, 64]:
        ty, ct = f"u{bits}", f"uint{bits}_t"
        group = f"format_{ty}"
        for op in ["decimal_divmod", "decimal_derived", "hex"]:
            base = 16 if op == "hex" else 10
            qc = "value >> 4" if base == 16 else "value / 10"
            qr = "value >> 4" if base == 16 else "value / 10"
            rc = (
                "(uint8_t)(value & 15)"
                if base == 16
                else "(uint8_t)(value % 10)"
                if op.endswith("divmod")
                else "(uint8_t)(value - q * 10)"
            )
            rr = (
                "(value & 15) as u8"
                if base == 16
                else "(value % 10) as u8"
                if op.endswith("divmod")
                else "value.wrapping_sub(q.wrapping_mul(10)) as u8"
            )
            digitc = "(uint8_t)(d < 10 ? '0' + d : 'a' + d - 10)"
            digitr = "if d < 10 { b'0' + d } else { b'a' + d - 10 }"
            cb = f"uint8_t tmp[20], i = 0; do {{ {ct} q = {qc}; uint8_t d = {rc}; tmp[i++] = {digitc}; value = q; }} while (value); for (uint8_t j = 0; j < i; ++j) dst[j] = tmp[i - 1 - j]; dst[i] = 0; return i;"
            rb = f"let mut storage = core::mem::MaybeUninit::<[u8; 20]>::uninit(); let tmp = storage.as_mut_ptr().cast::<u8>(); let mut i = 0usize; loop {{ let q = {qr}; let d = {rr}; *tmp.add(i) = {digitr}; i += 1; value = q; if value == 0 {{ break; }} }} for j in 0..i {{ *dst.add(j) = *tmp.add(i - 1 - j); }} *dst.add(i) = 0; i as u16"
            rp = PARAMS[f"value{bits}"]
            PARAMS[f"format_value{bits}"] = (
                rp[0],
                rp[1].replace("value:", "mut value:"),
                rp[2],
                rp[3],
            )
            add(
                group,
                op,
                "u16",
                ["dst", f"format_value{bits}"],
                cb,
                rb,
                "formatting",
                f"{ty} to {'hexadecimal' if base == 16 else 'decimal'}, {op.split('_')[-1]}",
                "NUL-terminated output; count excludes NUL; temporary is fully initialized before reads; separate div/mod and derived remainder forms expose quotient reuse",
                rextra=writer,
            )
        if bits <= 32:
            conversion = "%u" if bits == 16 else "%lu"
            cast = "unsigned int" if bits == 16 else "unsigned long"
            add(
                group,
                "decimal_library",
                "u16",
                ["dst", f"value{bits}"],
                f'return (uint16_t)sprintf((char *)dst, "{conversion}", ({cast})value);',
                'let mut w = PatternWriter { dst, len: 0 }; let _ = core::fmt::write(&mut w, format_args!("{}", value)); *dst.add(w.len) = 0; w.len as u16',
                "formatting",
                f"{ty} decimal through sprintf/core::fmt",
                "same decimal text and terminator; library formatting machinery differs and must be charged separately",
                style="library",
                rextra=writer,
            )

    decimal_c = "uint16_t i = 0; uint32_t value = 0; while (src[i] == ' ' || (src[i] >= 9 && src[i] <= 13)) ++i; uint8_t minus = src[i] == '-'; if (minus || src[i] == '+') ++i; uint16_t first = i; while (src[i] >= '0' && src[i] <= '9') { value = value * 10u + (uint32_t)(src[i] - '0'); ++i; } *end = i == first ? 0 : i; return minus ? (uint32_t)(0u - value) : value;"
    decimal_r = "let mut i = 0usize; let mut value = 0u32; while *src.add(i) == b' ' || (9..=13).contains(&*src.add(i)) { i += 1; } let minus = *src.add(i) == b'-'; if minus || *src.add(i) == b'+' { i += 1; } let first = i; while *src.add(i) >= b'0' && *src.add(i) <= b'9' { value = value.wrapping_mul(10).wrapping_add((*src.add(i) - b'0') as u32); i += 1; } *end = if i == first { 0 } else { i as u16 }; if minus { value.wrapping_neg() } else { value }"
    add(
        "parse",
        "decimal_loop",
        "u32",
        ["src", "end"],
        decimal_c,
        decimal_r,
        "parsing",
        "Parse decimal prefix and end offset",
        "ASCII whitespace and optional sign; wraps the unsigned accumulator; no digits means end offset zero",
    )
    add(
        "parse",
        "strtoul_decimal",
        "u32",
        ["src", "end"],
        "char *last; uint32_t value = (uint32_t)strtoul((const char *)src, &last, 10); *end = (uint16_t)(last - (const char *)src); return value;",
        decimal_r,
        "parsing",
        "Decimal strtoul versus matched scanner",
        "library variant excludes overflow; end-pointer behavior and optional signs match; errno is outside this contract",
        style="library",
    )
    checked_c = (
        decimal_c.replace(
            "value = value * 10u + (uint32_t)(src[i] - '0');",
            "uint32_t d = (uint32_t)(src[i] - '0'); if (value > (UINT32_MAX - d) / 10u) { overflow = 1; value = UINT32_MAX; } else if (!overflow) value = value * 10u + d;",
        )
        .replace("uint32_t value = 0;", "uint32_t value = 0; uint8_t overflow = 0;")
        .replace(
            "*end = i == first ? 0 : i;",
            "*end = (uint16_t)((i == first ? 0 : i) | (overflow ? 0x8000u : 0));",
        )
    )
    checked_r = (
        decimal_r.replace(
            "let mut value = 0u32;", "let mut value = 0u32; let mut overflow = false;"
        )
        .replace(
            "value = value.wrapping_mul(10).wrapping_add((*src.add(i) - b'0') as u32);",
            "let d = (*src.add(i) - b'0') as u32; if value > (u32::MAX - d) / 10 { overflow = true; value = u32::MAX; } else if !overflow { value = value * 10 + d; }",
        )
        .replace(
            "*end = if i == first { 0 } else { i as u16 };",
            "*end = (if i == first { 0 } else { i as u16 }) | if overflow { 0x8000 } else { 0 };",
        )
    )
    add(
        "parse",
        "decimal_checked",
        "u32",
        ["src", "end"],
        checked_c,
        checked_r,
        "parsing",
        "Checked decimal accumulation",
        "saturates magnitude at UINT32_MAX; end bit 15 flags overflow; optional minus is applied modulo 2^32 after saturation",
    )
    hex_c = "uint16_t i = 0; uint32_t value = 0; if (src[0] == '0' && (src[1] == 'x' || src[1] == 'X')) i = 2; uint16_t first = i; for (;;) { uint8_t c = src[i]; uint8_t d = c >= '0' && c <= '9' ? c - '0' : c >= 'a' && c <= 'f' ? c - 'a' + 10 : c >= 'A' && c <= 'F' ? c - 'A' + 10 : 255; if (d == 255) break; value = (value << 4) | d; ++i; } *end = i == first ? 0 : i; return value;"
    hex_r = "let mut i = 0usize; let mut value = 0u32; if *src == b'0' && (*src.add(1) == b'x' || *src.add(1) == b'X') { i = 2; } let first = i; loop { let c = *src.add(i); let d = if c >= b'0' && c <= b'9' { c - b'0' } else if c >= b'a' && c <= b'f' { c - b'a' + 10 } else if c >= b'A' && c <= b'F' { c - b'A' + 10 } else { 255 }; if d == 255 { break; } value = (value << 4) | d as u32; i += 1; } *end = if i == first { 0 } else { i as u16 }; value"
    add(
        "parse",
        "hex_loop",
        "u32",
        ["src", "end"],
        hex_c,
        hex_r,
        "parsing",
        "Parse hexadecimal prefix",
        "optional 0x prefix; unsigned wrapping accumulator; no digits means offset zero",
    )
    add(
        "parse",
        "atoi",
        "i16",
        ["src"],
        "return (int16_t)atoi((const char *)src);",
        decimal_r.replace(
            "*end = if i == first { 0 } else { i as u16 };", "let _ = first;"
        ).replace(
            "if minus { value.wrapping_neg() } else { value }",
            "(if minus { value.wrapping_neg() } else { value }) as i16",
        ),
        "parsing",
        "Restricted atoi",
        "input value must fit int16; ignores trailing non-digit bytes; whitespace and optional sign supported",
        style="library",
    )

    for op in ["isdigit", "isalpha", "isspace", "tolower", "toupper"]:
        expressions = {
            "isdigit": (
                "value >= '0' && value <= '9'",
                "value >= b'0' && value <= b'9'",
                "value.is_ascii_digit() as u8",
            ),
            "isalpha": (
                "(value >= 'A' && value <= 'Z') || (value >= 'a' && value <= 'z')",
                "(value >= b'A' && value <= b'Z') || (value >= b'a' && value <= b'z')",
                "value.is_ascii_alphabetic() as u8",
            ),
            "isspace": (
                "value == ' ' || (value >= 9 && value <= 13)",
                "value == b' ' || (value >= 9 && value <= 13)",
                "(value == b' ' || (9..=13).contains(&value)) as u8",
            ),
            "tolower": (
                "value >= 'A' && value <= 'Z' ? value + ('a' - 'A') : value",
                "if value >= b'A' && value <= b'Z' { value + (b'a' - b'A') } else { value }",
                "value.to_ascii_lowercase()",
            ),
            "toupper": (
                "value >= 'a' && value <= 'z' ? value - ('a' - 'A') : value",
                "if value >= b'a' && value <= b'z' { value - (b'a' - b'A') } else { value }",
                "value.to_ascii_uppercase()",
            ),
        }
        ce, re, idiomatic = expressions[op]
        predicate = op.startswith("is")
        add(
            "ctype",
            op + "_loop",
            "u8",
            ["value8"],
            f"return (uint8_t)({ce});",
            f"({re}) as u8",
            "ctype",
            f"ASCII {op}, explicit ranges",
            "all 256 byte values; classifications return 0/1; case conversions leave non-ASCII bytes unchanged",
        )
        lib = (
            f"value < 128 && {op}(value) != 0"
            if predicate
            else f"value < 128 ? {op}(value) : value"
        )
        add(
            "ctype",
            op + "_library",
            "u8",
            ["value8"],
            f"return (uint8_t)({lib});",
            idiomatic,
            "ctype",
            f"ASCII {op}, libc/core API",
            "explicit ASCII guard makes classification/case mapping independent of locale; includes high-bit bytes",
            style="library",
        )

    for op in ["strspn", "strcspn", "strpbrk"]:
        accept = op == "strspn"
        c_loop = (
            f"uint16_t i = 0; while (src[i]) {{ uint16_t j = 0; while (set[j] && set[j] != src[i]) ++j; uint8_t found = set[j] != 0; if ({'!found' if accept else 'found'}) break; ++i; }} return "
            + ("src[i] ? i : UINT16_MAX;" if op == "strpbrk" else "i;")
        )
        r_loop = (
            f"let mut i = 0usize; while *src.add(i) != 0 {{ let mut j = 0usize; while *set.add(j) != 0 && *set.add(j) != *src.add(i) {{ j += 1; }} let found = *set.add(j) != 0; if {'!found' if accept else 'found'} {{ break; }} i += 1; }} "
            + (
                "if *src.add(i) == 0 { u16::MAX } else { i as u16 }"
                if op == "strpbrk"
                else "i as u16"
            )
        )
        add(
            "spans",
            op + "_loop",
            "u16",
            ["src", "set"],
            c_loop,
            r_loop,
            "spans",
            f"{op}, nested byte scans",
            "NUL-terminated input and byte set; empty sets and high-bit bytes included; strpbrk returns offset or 65535",
        )
        c_lib = (
            f"return (uint16_t){op}((const char *)src, (const char *)set);"
            if op != "strpbrk"
            else "const char *p = strpbrk((const char *)src, (const char *)set); return p ? (uint16_t)((const uint8_t *)p - src) : UINT16_MAX;"
        )
        expr = (
            "a.iter().take_while(|x| b.contains(x)).count() as u16"
            if accept
            else "a.iter().position(|x| b.contains(x)).map_or("
            + ("u16::MAX" if op == "strpbrk" else "a.len() as u16")
            + ", |i| i as u16)"
        )
        r_lib = (
            "let a = core::ffi::CStr::from_ptr(src.cast()).to_bytes(); let b = core::ffi::CStr::from_ptr(set.cast()).to_bytes(); "
            + expr
        )
        add(
            "spans",
            op + "_library",
            "u16",
            ["src", "set"],
            c_lib,
            r_lib,
            "spans",
            f"{op}, libc versus CStr/iterators",
            "same result contract; Rust constructs both CStr slices before membership scanning",
            style="library",
        )

    tokenize_c = "uint16_t i = 0, count = 0; while (src[i]) { uint16_t j = 0; while (set[j] && set[j] != src[i]) ++j; if (set[j]) { ++i; continue; } uint16_t start = i; do { ++i; j = 0; while (set[j] && set[j] != src[i]) ++j; } while (src[i] && !set[j]); dst[2 * count] = (uint8_t)start; dst[2 * count + 1] = (uint8_t)(i - start); ++count; } return count;"
    tokenize_r = "let mut i = 0usize; let mut count = 0usize; while *src.add(i) != 0 { let mut j = 0usize; while *set.add(j) != 0 && *set.add(j) != *src.add(i) { j += 1; } if *set.add(j) != 0 { i += 1; continue; } let start = i; loop { i += 1; j = 0; while *set.add(j) != 0 && *set.add(j) != *src.add(i) { j += 1; } if *src.add(i) == 0 || *set.add(j) != 0 { break; } } *dst.add(2 * count) = start as u8; *dst.add(2 * count + 1) = (i - start) as u8; count += 1; } count as u16"
    add(
        "spans",
        "tokenize_loop",
        "u16",
        ["dst", "src", "set"],
        tokenize_c,
        tokenize_r,
        "spans",
        "Tokenizer producing start/length pairs",
        "non-mutating strtok-like scanner; output pairs are byte offsets and lengths; input strings are at most 128 bytes",
    )
    strtok_c = "strcpy((char *)dst, (const char *)src); uint16_t count = 0; char *token = strtok((char *)dst, (const char *)set); while (token) { ++count; token = strtok(NULL, (const char *)set); } return count;"
    strtok_r = "let bytes = core::ffi::CStr::from_ptr(src.cast()).to_bytes_with_nul(); core::ptr::copy_nonoverlapping(bytes.as_ptr(), dst, bytes.len()); let delimiters = core::ffi::CStr::from_ptr(set.cast()).to_bytes(); let mut i = 0usize; let mut count = 0u16; loop { while *dst.add(i) != 0 && delimiters.contains(&*dst.add(i)) { i += 1; } if *dst.add(i) == 0 { break; } count += 1; while *dst.add(i) != 0 && !delimiters.contains(&*dst.add(i)) { i += 1; } if *dst.add(i) == 0 { break; } *dst.add(i) = 0; i += 1; } count"
    add(
        "spans",
        "strtok_library",
        "u16",
        ["dst", "src", "set"],
        strtok_c,
        strtok_r,
        "spans",
        "strtok on a writable copy",
        "returns token count and observes the entire modified copy; each call resets libc strtok state; leading and repeated delimiters remain as specified",
        style="library",
    )

    strstr_c = "if (!other[0]) return 0; uint16_t i = 0; while (src[i]) { uint16_t j = 0; while (other[j] && src[i + j] == other[j]) ++j; if (!other[j]) return i; ++i; } return UINT16_MAX;"
    strstr_r = "if *other == 0 { return 0; } let mut i = 0usize; while *src.add(i) != 0 { let mut j = 0usize; while *other.add(j) != 0 && *src.add(i + j) == *other.add(j) { j += 1; } if *other.add(j) == 0 { return i as u16; } i += 1; } u16::MAX"
    add(
        "substring",
        "strstr_loop",
        "u16",
        ["src", "other"],
        strstr_c,
        strstr_r,
        "substring",
        "Substring search, nested loops",
        "NUL strings; empty needle returns zero; not found returns 65535",
    )
    add(
        "substring",
        "strstr_library",
        "u16",
        ["src", "other"],
        "const char *p = strstr((const char *)src, (const char *)other); return p ? (uint16_t)((const uint8_t *)p - src) : UINT16_MAX;",
        "let a = core::ffi::CStr::from_ptr(src.cast()).to_bytes(); let b = core::ffi::CStr::from_ptr(other.cast()).to_bytes(); if b.is_empty() { 0 } else { a.windows(b.len()).position(|w| w == b).map_or(u16::MAX, |i| i as u16) }",
        "substring",
        "strstr versus slice windows",
        "same substring result contract; Rust determines both lengths first and uses windows",
        style="library",
    )
    for size in [2, 4]:
        tests = " && ".join(f"src[i + {j}] == other[{j}]" for j in range(size))
        add(
            "substring",
            f"needle{size}",
            "u16",
            ["src", "other", "n"],
            f"if (n < {size}) return UINT16_MAX; for (uint16_t i = 0; i <= n - {size}; ++i) if ({tests}) return i; return UINT16_MAX;",
            f"let a = core::slice::from_raw_parts(src, n as usize); let b = core::slice::from_raw_parts(other, {size}); a.windows({size}).position(|w| w == b).map_or(u16::MAX, |i| i as u16)",
            "substring",
            f"Find fixed {size}-byte needle",
            "binary input includes zeros; needle always has the specified readable byte count",
            style="idiomatic",
        )

    strcat_c = "uint16_t i = 0, j = 0; while (dst[i]) ++i; do { dst[i] = src[j]; ++i; } while (src[j++]); return dst;"
    strcat_r = "let mut i = 0usize; let mut j = 0usize; while *dst.add(i) != 0 { i += 1; } loop { let x = *src.add(j); *dst.add(i) = x; i += 1; j += 1; if x == 0 { break; } } dst"
    add(
        "concat",
        "strcat_loop",
        "pointer",
        ["dst", "src"],
        strcat_c,
        strcat_r,
        "concat",
        "Concatenate, fused byte copy",
        "destination initially contains a NUL string and has room for the entire source",
    )
    add(
        "concat",
        "strcat_library",
        "pointer",
        ["dst", "src"],
        "return (uint8_t *)strcat((char *)dst, (const char *)src);",
        "let i = core::ffi::CStr::from_ptr(dst.cast()).to_bytes().len(); let s = core::ffi::CStr::from_ptr(src.cast()).to_bytes_with_nul(); core::ptr::copy_nonoverlapping(s.as_ptr(), dst.add(i), s.len()); dst",
        "concat",
        "strcat versus CStr scan/copy",
        "Rust scans both lengths then copies; library algorithm may fuse source scan and copy",
        style="library",
    )
    strncat_c = "uint16_t i = 0, j = 0; while (dst[i]) ++i; while (j < n && src[j]) { dst[i++] = src[j++]; } dst[i] = 0; return dst;"
    strncat_r = "let mut i = 0usize; let mut j = 0usize; while *dst.add(i) != 0 { i += 1; } while j < n as usize && *src.add(j) != 0 { *dst.add(i) = *src.add(j); i += 1; j += 1; } *dst.add(i) = 0; dst"
    add(
        "concat",
        "strncat_loop",
        "pointer",
        ["dst", "src", "n"],
        strncat_c,
        strncat_r,
        "concat",
        "Append at most n source bytes",
        "n limits source bytes, not destination capacity; always terminates and does not zero-pad",
    )
    add(
        "concat",
        "strncat_library",
        "pointer",
        ["dst", "src", "n"],
        "return (uint8_t *)strncat((char *)dst, (const char *)src, n);",
        strncat_r,
        "concat",
        "strncat library versus byte loop",
        "same bounded concatenation contract; destination has sufficient space",
        style="library",
    )
    add(
        "concat",
        "append_bounded",
        "u16",
        ["dst", "src", "limit"],
        "uint16_t i = 0, j = 0; while (i < limit && dst[i]) ++i; if (i == limit) return UINT16_MAX; while (i + 1 < limit && src[j]) dst[i++] = src[j++]; dst[i] = 0; return i;",
        "let mut i = 0usize; let mut j = 0usize; while i < limit as usize && *dst.add(i) != 0 { i += 1; } if i == limit as usize { return u16::MAX; } while i + 1 < limit as usize && *src.add(j) != 0 { *dst.add(i) = *src.add(j); i += 1; j += 1; } *dst.add(i) = 0; i as u16",
        "concat",
        "Capacity-checked append",
        "zero capacity or missing destination NUL within capacity returns 65535 without writing; otherwise truncates and terminates",
    )

    for size in [3, 5, 8, 12]:
        blob = f"PatternBlob{size}"
        ch = f"typedef struct {{ uint8_t bytes[{size}]; }} {blob};\n"
        rh = f"#[repr(C)]\n#[derive(Clone, Copy)]\npub struct {blob} {{ pub bytes: [u8; {size}] }}\n"
        add(
            f"aggregate_copy{size}",
            "assign",
            "pointer",
            ["dst", "src"],
            f"*({blob} *)dst = *(const {blob} *)src; return dst;",
            f"let value = core::ptr::read_unaligned(src.cast::<{blob}>()); core::ptr::write_unaligned(dst.cast::<{blob}>(), value); dst",
            "aggregates",
            f"Assign a {size}-byte struct",
            "byte-only repr(C) aggregate; no padding; disjoint source and destination",
            cextra=ch,
            rextra=rh,
        )
        cfn = f"{blob} probe(const uint8_t *src) {{ return *(const {blob} *)src; }}"
        add(
            f"aggregate_return{size}",
            "value",
            blob,
            ["src"],
            f"return *(const {blob} *)src;",
            f"core::ptr::read_unaligned(src.cast::<{blob}>())",
            "aggregates",
            f"Return a {size}-byte struct by value",
            "host C and Rust use matching repr(C); target aggregate-return support is feature-probed, with compiler diagnostics retained",
            cextra=ch,
            rextra=rh,
            capability=cfn,
        )
        helper = {
            "id": f"fixture_blob{size}_out",
            "c_function": f"NOINLINE void fixture_blob{size}_out({blob} *dst, const {blob} *src) {{ *dst = *src; }}",
            "rust_function": f'#[unsafe(no_mangle)]\n#[inline(never)]\npub unsafe extern "C" fn fixture_blob{size}_out(dst: *mut {blob}, src: *const {blob}) {{ unsafe {{ core::ptr::write_unaligned(dst, core::ptr::read_unaligned(src)); }} }}',
        }
        add(
            f"aggregate_out{size}",
            "call",
            "u16",
            ["dst", "src"],
            f"{blob} tmp; fixture_blob{size}_out(&tmp, (const {blob} *)src); *({blob} *)dst = tmp; return {size};",
            f"let mut tmp = core::mem::MaybeUninit::<{blob}>::uninit(); fixture_blob{size}_out(tmp.as_mut_ptr(), src.cast()); core::ptr::write_unaligned(dst.cast::<{blob}>(), tmp.assume_init()); {size}",
            "aggregates",
            f"{size}-byte out-parameter call and local",
            "callee writes an uninitialized local completely; no implicit zero-fill; caller then copies the aggregate to output",
            support=[helper],
            cextra=ch,
            rextra=rh,
        )
    pair_c = "typedef struct { const uint8_t *ptr; uint16_t len; } PatternPair;\n"
    pair_r = "#[repr(C)]\npub struct PatternPair { pub ptr: *const u8, pub len: u16 }\n"
    add(
        "aggregate_pair",
        "return",
        "PatternPair",
        ["src", "n"],
        "PatternPair result = { src, n }; return result;",
        "PatternPair { ptr: src, len: n }",
        "aggregates",
        "Return pointer plus length",
        "host ABI layout is platform-specific but matched repr(C); target return feature is probed",
        cextra=pair_c,
        rextra=pair_r,
        capability="PatternPair probe(const uint8_t *src) { PatternPair r = { src, 1 }; return r; }",
    )

    sum_c = "uint16_t value = 0; for (uint16_t i = 0; i < n; ++i) value = (uint16_t)(value + src[i]); return value;"
    for op, rb in [
        (
            "sum_index",
            "let s = core::slice::from_raw_parts(src, n as usize); let mut value = 0u16; for i in 0..s.len() { value = value.wrapping_add(s[i] as u16); } value",
        ),
        (
            "sum_iter",
            "core::slice::from_raw_parts(src, n as usize).iter().fold(0u16, |a, &b| a.wrapping_add(b as u16))",
        ),
        (
            "sum_raw",
            "let mut value = 0u16; for i in 0..n as usize { value = value.wrapping_add(*src.add(i) as u16); } value",
        ),
    ]:
        add(
            "slices",
            op,
            "u16",
            ["src", "n"],
            sum_c,
            rb,
            "slices",
            op.replace("_", " "),
            "valid input slice; same wrapping sum; indexed, iterator and raw-pointer forms isolate bounds/metadata costs",
            style="idiomatic" if op != "sum_raw" else "matched_loop",
        )
    add(
        "slices",
        "sum_pointer",
        "u16",
        ["src", "n"],
        "uint16_t value = 0; const uint8_t *last = src + n; while (src != last) value = (uint16_t)(value + *src++); return value;",
        "let mut value = 0u16; let last = src.add(n as usize); let mut p = src; while p != last { value = value.wrapping_add(*p as u16); p = p.add(1); } value",
        "slices",
        "Sum with pointer induction",
        "matched end-pointer loops versus indexed controls",
    )
    add(
        "slices",
        "sum_countdown",
        "u16",
        ["src", "n"],
        "uint16_t value = 0; while (n) { value = (uint16_t)(value + *src++); --n; } return value;",
        "let mut value = 0u16; let mut p = src; let mut count = n; while count != 0 { value = value.wrapping_add(*p as u16); p = p.add(1); count -= 1; } value",
        "slices",
        "Sum with remaining-count loop",
        "matched countdown and pointer-bump induction",
    )
    add(
        "slices",
        "copy_from_slice",
        "pointer",
        ["dst", "src", "n"],
        "memcpy(dst, src, n); return dst;",
        "let a = core::slice::from_raw_parts_mut(dst, n as usize); let b = core::slice::from_raw_parts(src, n as usize); a.copy_from_slice(b); dst",
        "slices",
        "Safe copy_from_slice",
        "equal lengths by construction; non-overlapping slices; tests bounds/panic elimination",
        style="idiomatic",
    )
    add(
        "slices",
        "copy_within",
        "pointer",
        ["dst", "n"],
        "uint16_t half = n / 2; memmove(dst + n - half, dst, half); return dst;",
        "let s = core::slice::from_raw_parts_mut(dst, n as usize); let half = s.len() / 2; s.copy_within(0..half, s.len() - half); dst",
        "slices",
        "Safe overlapping slice copy",
        "source and destination ranges are constructed within the same slice; zero and odd lengths included",
        style="idiomatic",
    )
    add(
        "slices",
        "fill",
        "pointer",
        ["dst", "n", "value8"],
        "memset(dst, value, n); return dst;",
        "core::slice::from_raw_parts_mut(dst, n as usize).fill(value); dst",
        "slices",
        "Safe slice fill",
        "same n-byte fill through safe slice versus libc",
        style="idiomatic",
    )
    add(
        "slices",
        "chunks_exact",
        "u16",
        ["src", "n"],
        "uint16_t value = 0; for (uint16_t i = 0; i + 1 < n; i += 2) value = (uint16_t)(value + src[i] + ((uint16_t)src[i + 1] << 8)); return value;",
        "core::slice::from_raw_parts(src, n as usize).chunks_exact(2).fold(0u16, |a, c| a.wrapping_add(u16::from_le_bytes([c[0], c[1]])))",
        "slices",
        "Sum little-endian pairs through chunks",
        "ignores one odd trailing byte; unsigned wrapping word sum",
        style="idiomatic",
    )

    PARAMS["words"] = ("const uint16_t *src", "src: *const u16", "ptr", "sorted_words")
    PARAMS["words_mut"] = ("uint16_t *dst", "dst: *mut u16", "ptr", "words_output")
    cmp = {
        "id": "fixture_cmp_words",
        "languages": ["c"],
        "c_function": "NOINLINE int fixture_cmp_words(const void *a, const void *b) { uint16_t x = *(const uint16_t *)a, y = *(const uint16_t *)b; return (x > y) - (x < y); }",
        "rust_function": '#[unsafe(no_mangle)]\n#[inline(never)]\npub unsafe extern "C" fn fixture_cmp_words(a: *const core::ffi::c_void, b: *const core::ffi::c_void) -> core::ffi::c_int { unsafe { let x = *a.cast::<u16>(); let y = *b.cast::<u16>(); (x > y) as core::ffi::c_int - (x < y) as core::ffi::c_int } }',
    }
    binary_c = "uint16_t low = 0, high = n; while (low < high) { uint16_t mid = low + (high - low) / 2; if (src[mid] < value) low = mid + 1; else if (src[mid] > value) high = mid; else return mid; } return UINT16_MAX;"
    binary_r = "let mut low = 0usize; let mut high = n as usize; while low < high { let mid = low + (high - low) / 2; let x = *src.add(mid); if x < value { low = mid + 1; } else if x > value { high = mid; } else { return mid as u16; } } u16::MAX"
    add(
        "search",
        "binary_loop",
        "u16",
        ["words", "n", "value16"],
        binary_c,
        binary_r,
        "search_sort",
        "Typed binary search",
        "strictly increasing u16 keys; returns index or 65535",
    )
    add(
        "search",
        "bsearch_library",
        "u16",
        ["words", "n", "value16"],
        "const uint16_t *p = (const uint16_t *)bsearch(&value, src, n, sizeof(uint16_t), fixture_cmp_words); return p ? (uint16_t)(p - src) : UINT16_MAX;",
        "core::slice::from_raw_parts(src, n as usize).binary_search(&value).map_or(u16::MAX, |i| i as u16)",
        "search_sort",
        "bsearch callback versus typed slice",
        "strictly increasing keys avoid unspecified duplicate-match choices; generic callback cost differs from monomorphized Rust comparison",
        style="library",
        support=[cmp],
    )
    sort_c = "for (uint16_t i = 1; i < n; ++i) { uint16_t value = dst[i], j = i; while (j && dst[j - 1] > value) { dst[j] = dst[j - 1]; --j; } dst[j] = value; } return (uint8_t *)dst;"
    sort_r = "for i in 1..n as usize { let value = *dst.add(i); let mut j = i; while j != 0 && *dst.add(j - 1) > value { *dst.add(j) = *dst.add(j - 1); j -= 1; } *dst.add(j) = value; } dst.cast::<u8>()"
    add(
        "search",
        "insertion_sort",
        "pointer",
        ["words_mut", "n"],
        sort_c,
        sort_r,
        "search_sort",
        "Matched insertion sort",
        "in-place unsigned u16 order; duplicates, empty and one-element arrays included",
    )
    add(
        "search",
        "qsort_library",
        "pointer",
        ["words_mut", "n"],
        "qsort(dst, n, sizeof(uint16_t), fixture_cmp_words); return (uint8_t *)dst;",
        "core::slice::from_raw_parts_mut(dst, n as usize).sort_unstable(); dst.cast::<u8>()",
        "search_sort",
        "qsort versus typed unstable sort",
        "same sorted output but algorithms differ; compare with matched insertion-sort control before attributing size to codegen",
        style="library",
        support=[cmp],
    )

    for bits in [16, 32, 64]:
        count = bits // 8
        for endian in ["le", "be"]:
            terms = " | ".join(
                f"((uint{bits}_t)src[{i}] << {8 * (i if endian == 'le' else count - 1 - i)})"
                for i in range(count)
            )
            add(
                "packing",
                f"load_{endian}{bits}",
                f"u{bits}",
                ["src"],
                f"return {terms};",
                f"u{bits}::from_{endian}_bytes(core::ptr::read_unaligned(src.cast::<[u8; {count}]>()))",
                "packing_checksum",
                f"Load unaligned {endian}-endian u{bits}",
                "byte input may be unaligned; no native word access assumed",
                style="idiomatic",
            )
            stores = " ".join(
                f"dst[{i}] = (uint8_t)(value >> {8 * (i if endian == 'le' else count - 1 - i)});"
                for i in range(count)
            )
            add(
                "packing",
                f"store_{endian}{bits}",
                "pointer",
                ["dst", f"value{bits}"],
                stores + " return dst;",
                f"let b = value.to_{endian}_bytes(); core::ptr::copy_nonoverlapping(b.as_ptr(), dst, {count}); dst",
                "packing_checksum",
                f"Store unaligned {endian}-endian u{bits}",
                "only the word-sized output span is changed",
                style="idiomatic",
            )
    add(
        "checksum",
        "sum8",
        "u8",
        ["src", "n"],
        "uint8_t value = 0; for (uint16_t i = 0; i < n; ++i) value = (uint8_t)(value + src[i]); return value;",
        "let mut value = 0u8; for i in 0..n as usize { value = value.wrapping_add(*src.add(i)); } value",
        "packing_checksum",
        "Wrapping byte checksum",
        "all byte values and empty buffers",
    )
    add(
        "checksum",
        "sum16",
        "u16",
        ["src", "n"],
        sum_c,
        "let mut value = 0u16; for i in 0..n as usize { value = value.wrapping_add(*src.add(i) as u16); } value",
        "packing_checksum",
        "Wrapping word checksum",
        "sum of bytes modulo 65536",
    )
    add(
        "checksum",
        "crc16",
        "u16",
        ["src", "n", "value16"],
        "for (uint16_t i = 0; i < n; ++i) { value ^= (uint16_t)src[i] << 8; for (uint8_t j = 0; j < 8; ++j) value = (uint16_t)((value << 1) ^ ((value & 0x8000u) ? 0x1021u : 0)); } return value;",
        "let mut crc = value; for i in 0..n as usize { crc ^= (*src.add(i) as u16) << 8; for _ in 0..8 { crc = (crc << 1) ^ if crc & 0x8000 != 0 { 0x1021 } else { 0 }; } } crc",
        "packing_checksum",
        "CRC16-CCITT bit loop",
        "caller-supplied seed, polynomial 0x1021, no reflection or final XOR",
    )
    dense = [7, 0, 99, 2, 1, 17, 31, 6]
    c_cases = " ".join(f"case {i}: return {v};" for i, v in enumerate(dense))
    r_cases = ", ".join(f"{i} => {v}" for i, v in enumerate(dense))
    add(
        "dispatch",
        "dense",
        "u16",
        ["value8"],
        "switch (value) { " + c_cases + " default: return 65535; }",
        "match value { " + r_cases + ", _ => u16::MAX }",
        "dispatch",
        "Dense switch/match",
        "nonlinear result constants prevent simple affine folding; default included",
    )
    sparse = [(0, 7), (1, 11), (7, 3), (31, 13), (128, 5), (255, 17)]
    add(
        "dispatch",
        "sparse",
        "u16",
        ["value8"],
        "switch (value) { "
        + " ".join(f"case {i}: return {v};" for i, v in sparse)
        + " default: return 0; }",
        "match value { " + ", ".join(f"{i} => {v}" for i, v in sparse) + ", _ => 0 }",
        "dispatch",
        "Sparse switch/match",
        "covers gaps and high-bit discriminator values",
    )
    add(
        "dispatch",
        "parser_state",
        "u16",
        ["src", "n"],
        "uint16_t acc = 0, total = 0; uint8_t state = 0; for (uint16_t i = 0; i < n; ++i) { uint8_t c = src[i]; switch (c) { case ':': state ^= 1; break; case ',': total = (uint16_t)(total + acc); acc = 0; break; default: if (c >= '0' && c <= '9') acc = (uint16_t)(acc * 10u + c - '0'); else if (c != ' ') state = 2; break; } } return (uint16_t)(total ^ acc ^ state);",
        "let mut acc = 0u16; let mut total = 0u16; let mut state = 0u8; for i in 0..n as usize { let c = *src.add(i); match c { b':' => state ^= 1, b',' => { total = total.wrapping_add(acc); acc = 0; }, _ => { if c >= b'0' && c <= b'9' { acc = acc.wrapping_mul(10).wrapping_add((c - b'0') as u16); } else if c != b' ' { state = 2; } } } } total ^ acc ^ state as u16",
        "dispatch",
        "Parser state-machine loop",
        "same state transitions and wrapping decimal accumulator; shared exits and loop-carried state",
    )

    for group, (ch, rh) in headers.items():
        members = [c for c in cases if c["type"] == group]
        helpers = {h["id"]: h for c in members for h in c["support_functions"]}
        for lang, header in [("c", ch), ("rust", rh)]:
            key = lang + "_function"
            extension = "rs" if lang == "rust" else "c"
            (ROOT / f"cases/{group}.{extension}").write_text(
                header
                + "\n"
                + "\n\n".join(
                    c[key]
                    for c in list(helpers.values()) + members
                    if lang in c.get("languages", ["c", "rust"])
                )
                + "\n"
            )
    return cases
