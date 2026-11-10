from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
C_HEADER = "#include <stdint.h>\n#include <string.h>\n"
RUST_HEADER = "#![no_std]\n"
PARAMETERS = {
    "dst": ("uint8_t *dst", "dst: *mut u8", "0xc100 as *mut u8"),
    "src": ("const uint8_t *src", "src: *const u8", "0xc200 as *const u8"),
    "a": ("const uint8_t *a", "a: *const u8", "0xc100 as *const u8"),
    "b": ("const uint8_t *b", "b: *const u8", "0xc200 as *const u8"),
    "s": ("const uint8_t *s", "s: *const u8", "0xc100 as *const u8"),
    "value": (
        "uint8_t value",
        "value: u8",
        "core::ptr::read_volatile(0xc002 as *const u8)",
    ),
    "n": ("uint16_t n", "n: u16", "core::ptr::read_volatile(0xc000 as *const u16)"),
}


def generate_strings():
    cases = []

    def add(
        op,
        params,
        result,
        cbody,
        rbody,
        scenario,
        note,
        style="library",
        fixed_length=None,
        pointer_offset=0,
        base_operation=None,
    ):
        name = f"strings_{op}"
        cty, rty = {
            "u16": ("uint16_t", "u16"),
            "i8": ("int8_t", "i8"),
            "u8": ("uint8_t", "u8"),
            "pointer": ("uint8_t *", "*mut u8"),
        }[result]
        cfn = (
            f"{cty} {name}({', '.join(PARAMETERS[p][0] for p in params)}) {{ {cbody} }}"
        )
        rfn = f'#[unsafe(no_mangle)]\n#[inline(never)]\npub unsafe extern "C" fn {name}({", ".join(PARAMETERS[p][1] for p in params)}) -> {rty} {{ unsafe {{ {rbody} }} }}'
        call = f"{name}({', '.join(PARAMETERS[p][2] for p in params)})"
        cases.append(
            {
                "id": name,
                "type": "strings",
                "width": 8,
                "kind": "string",
                "signed": None,
                "operation": op,
                "domain": "valid pointers and readable/writable ranges within single allocations; lengths and string lengths <= 32766; no address wrapping; copy ranges do not overlap unless memmove; NUL-terminated strings for unbounded scans",
                "c_source": "cases/strings.c",
                "rust_source": "cases/strings.rs",
                "c_function": cfn,
                "rust_function": rfn,
                "scenario": scenario,
                "parameters": params,
                "result": result,
                "style": style,
                "fixed_length": fixed_length,
                "pointer_offset": pointer_offset,
                "base_operation": base_operation or op,
                "semantic_note": note,
                "link_entry": f"#[unsafe(no_mangle)]\npub fn gbc_main() -> u8 {{ unsafe {{ {call} as "
                + ("usize as u8" if result == "pointer" else "u8")
                + " } }",
            }
        )

    sign_c = "return (int8_t)((v > 0) - (v < 0));"
    sign_r = "match v { core::cmp::Ordering::Less => -1, core::cmp::Ordering::Equal => 0, core::cmp::Ordering::Greater => 1 }"
    cstr = "core::ffi::CStr::from_ptr(s.cast()).to_bytes()"
    add(
        "strlen",
        ["s"],
        "u16",
        "return (uint16_t)strlen((const char *)s);",
        f"{cstr}.len() as u16",
        "length",
        "C strlen versus Rust CStr construction and length; includes the NUL scan",
    )
    add(
        "strlen_loop",
        ["s"],
        "u16",
        "uint16_t n = 0; while (s[n]) ++n; return n;",
        "let mut n = 0u16; while *s.add(n as usize) != 0 { n = n.wrapping_add(1); } n",
        "length",
        "matching indexed byte scans",
        "matched_loop",
    )
    add(
        "strcmp",
        ["a", "b"],
        "i8",
        "int v = strcmp((const char *)a, (const char *)b); " + sign_c,
        "let v = core::ffi::CStr::from_ptr(a.cast()).to_bytes().cmp(core::ffi::CStr::from_ptr(b.cast()).to_bytes()); "
        + sign_r,
        "compare_string",
        "only comparison sign is observable; CStr scans both strings before slice comparison",
    )
    rloop = "let mut i = 0usize; loop { let x = *a.add(i); let y = *b.add(i); if x != y { return (x > y) as i8 - (x < y) as i8; } if x == 0 { return 0; } i += 1; }"
    add(
        "strcmp_loop",
        ["a", "b"],
        "i8",
        "uint16_t i = 0; for (;;) { uint8_t x = a[i], y = b[i]; if (x != y) return (int8_t)((x > y) - (x < y)); if (!x) return 0; ++i; }",
        rloop,
        "compare_string",
        "matching single-pass unsigned-byte comparison; sign normalized",
        "matched_loop",
    )
    add(
        "strncmp",
        ["a", "b", "n"],
        "i8",
        "int v = strncmp((const char *)a, (const char *)b, n); " + sign_c,
        "let mut i = 0usize; while i < n as usize { let x = *a.add(i); let y = *b.add(i); if x != y { return (x > y) as i8 - (x < y) as i8; } if x == 0 { return 0; } i += 1; } 0",
        "compare_string_n",
        "bounded unsigned-byte comparison; sign normalized; stops at NUL",
    )
    for op in ["strchr", "strrchr"]:
        rbody = (
            "let mut i = 0u16; let mut found = u16::MAX; loop { let x = *s.add(i as usize); if x == value { "
            + ("return i;" if op == "strchr" else "found = i;")
            + " } if x == 0 { return "
            + ("u16::MAX" if op == "strchr" else "found")
            + "; } i = i.wrapping_add(1); }"
        )
        add(
            op,
            ["s", "value"],
            "u16",
            f"const char *p = {op}((const char *)s, value); return p ? (uint16_t)((const uint8_t *)p - s) : UINT16_MAX;",
            rbody,
            "search_string",
            "returns byte offset or 65535; searching for NUL returns terminator offset",
        )
    add(
        "strcpy",
        ["dst", "src"],
        "pointer",
        "return (uint8_t *)strcpy((char *)dst, (const char *)src);",
        "let bytes = core::ffi::CStr::from_ptr(src.cast()).to_bytes_with_nul(); core::ptr::copy_nonoverlapping(bytes.as_ptr(), dst, bytes.len()); dst",
        "copy_string",
        "copies NUL too; Rust CStr scan followed by copy is two passes",
    )
    add(
        "strncpy",
        ["dst", "src", "n"],
        "pointer",
        "return (uint8_t *)strncpy((char *)dst, (const char *)src, n);",
        "let mut i = 0usize; while i < n as usize { let x = *src.add(i); if x == 0 { break; } *dst.add(i) = x; i += 1; } while i < n as usize { *dst.add(i) = 0; i += 1; } dst",
        "copy_pad",
        "pads destination with zeros; no terminator required if source length >= n",
    )
    for base in ["memcpy", "memmove", "memset", "memcmp"]:
        for fixed in [None, 0, 1, 2, 3, 4, 7, 8, 15, 16, 17, 31, 32, 63, 64, 127, 128]:
            op = base + (str(fixed) if fixed is not None else "")
            n = str(fixed) if fixed is not None else "n"
            params = (
                ["dst", "value"]
                if base == "memset"
                else ["dst", "src"]
                if base in {"memcpy", "memmove"}
                else ["a", "b"]
            ) + ([] if fixed is not None else ["n"])
            if base in {"memcpy", "memmove"}:
                intrinsic = "copy_nonoverlapping" if base == "memcpy" else "copy"
                add(
                    op,
                    params,
                    "pointer",
                    f"return (uint8_t *){base}(dst, src, {n});",
                    f"core::ptr::{intrinsic}(src, dst, {n} as usize); dst",
                    base,
                    "copy includes original destination pointer return; overlap allowed only for memmove",
                    fixed_length=fixed,
                    base_operation=base,
                )
            elif base == "memset":
                add(
                    op,
                    params,
                    "pointer",
                    f"return (uint8_t *)memset(dst, value, {n});",
                    f"core::ptr::write_bytes(dst, value, {n} as usize); dst",
                    "memset",
                    "fills exactly n bytes and returns original destination",
                    fixed_length=fixed,
                    base_operation=base,
                )
            else:
                add(
                    op,
                    params,
                    "i8",
                    f"int v = memcmp(a, b, {n}); " + sign_c,
                    f"let v = core::slice::from_raw_parts(a, {n} as usize).cmp(core::slice::from_raw_parts(b, {n} as usize)); "
                    + sign_r,
                    "memcmp",
                    "compares unsigned bytes; sign normalized",
                    fixed_length=fixed,
                    base_operation=base,
                )
    add(
        "memeq",
        ["a", "b", "n"],
        "u8",
        "return memcmp(a, b, n) == 0;",
        "(core::slice::from_raw_parts(a, n as usize) == core::slice::from_raw_parts(b, n as usize)) as u8",
        "memeq",
        "byte equality; no lexicographic ordering needed",
    )
    add(
        "memchr",
        ["s", "value", "n"],
        "u16",
        "const uint8_t *p = (const uint8_t *)memchr(s, value, n); return p ? (uint16_t)(p - s) : UINT16_MAX;",
        "let mut i = 0u16; while i < n { if *s.add(i as usize) == value { return i; } i += 1; } u16::MAX",
        "search_memory",
        "search includes embedded zeros; returns byte offset or 65535",
    )
    for offset in [1, 3, 7]:
        add(
            f"memcpy_offset{offset}",
            ["dst", "src", "n"],
            "pointer",
            f"return (uint8_t *)memcpy(dst + {offset}, src + {offset}, n);",
            f"core::ptr::copy_nonoverlapping(src.add({offset}), dst.add({offset}), n as usize); dst.add({offset})",
            "memcpy",
            "computed pointers copy n bytes after an unchanged prefix and return the adjusted destination",
            pointer_offset=offset,
            base_operation="memcpy",
        )
    (ROOT / "cases/strings.c").write_text(
        C_HEADER + "\n" + "\n\n".join(c["c_function"] for c in cases) + "\n"
    )
    (ROOT / "cases/strings.rs").write_text(
        RUST_HEADER + "\n" + "\n\n".join(c["rust_function"] for c in cases) + "\n"
    )
    return cases
