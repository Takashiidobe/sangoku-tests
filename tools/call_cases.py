from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
C_HEADER = "#include <stdint.h>\n#if defined(__SDCC)\n#define NOINLINE\n#else\n#define NOINLINE __attribute__((noinline))\n#endif\n"
RUST_HEADER = "#![no_std]\n"


def generate_calls():
    cases = []
    for width in [8, 16, 32, 64]:
        ty, cty = f"u{width}", f"uint{width}_t"
        group = f"calls_{ty}"
        leaf = f"fixture_leaf_{ty}"
        six = f"fixture_six_{ty}"
        touch = f"fixture_touch_{ty}"
        support = {
            leaf: {
                "id": leaf,
                "c_function": f"NOINLINE {cty} {leaf}({cty} a, {cty} b) {{ return ({cty})(a + b); }}",
                "rust_function": f'#[unsafe(no_mangle)]\n#[inline(never)]\npub extern "C" fn {leaf}(a: {ty}, b: {ty}) -> {ty} {{ a.wrapping_add(b) }}',
            },
            six: {
                "id": six,
                "c_function": f"NOINLINE {cty} {six}({', '.join(f'{cty} {p}' for p in 'abcdef')}) {{ return ({cty})(a ^ b ^ c ^ d ^ e ^ f); }}",
                "rust_function": f'#[unsafe(no_mangle)]\n#[inline(never)]\npub extern "C" fn {six}({", ".join(f"{p}: {ty}" for p in "abcdef")}) -> {ty} {{ a ^ b ^ c ^ d ^ e ^ f }}',
            },
            touch: {
                "id": touch,
                "c_function": f"NOINLINE {cty} {touch}(uint8_t *p, {cty} a) {{ p[0] ^= (uint8_t)a; p[7] = (uint8_t)(p[7] + 1u); return ({cty})p[7]; }}",
                "rust_function": f'#[unsafe(no_mangle)]\n#[inline(never)]\npub unsafe extern "C" fn {touch}(p: *mut u8, a: {ty}) -> {ty} {{ unsafe {{ *p ^= a as u8; *p.add(7) = (*p.add(7)).wrapping_add(1); *p.add(7) as {ty} }} }}',
            },
        }

        def add(op, cp, rp, cb, rb, helpers, expected_calls, note, live=0, frame=0):
            name = f"{group}_{op}"
            cases.append(
                {
                    "id": name,
                    "type": group,
                    "kind": "call",
                    "width": width,
                    "signed": False,
                    "operation": op,
                    "domain": "unsigned wrapping arithmetic; pointer probes require valid aligned arrays; callbacks use the matching C ABI",
                    "c_source": f"cases/{group}.c",
                    "rust_source": f"cases/{group}.rs",
                    "c_function": f"{cty} {name}({cp}) {{ {cb} }}",
                    "rust_function": f'#[unsafe(no_mangle)]\n#[inline(never)]\npub unsafe extern "C" fn {name}({rp}) -> {ty} {{ unsafe {{ {rb} }} }}',
                    "support_functions": [support[h] for h in helpers],
                    "expected_fixture_calls": expected_calls,
                    "live_values_across_call": live,
                    "explicit_local_array_bytes": frame,
                    "semantic_note": note,
                    "result_type": ty,
                    "result_width": width,
                }
            )

        cp = f"{cty} a, {cty} b"
        rp = f"a: {ty}, b: {ty}"
        add(
            "leaf",
            cp,
            rp,
            f"return ({cty})(a + b);",
            "a.wrapping_add(b)",
            [],
            0,
            "leaf control with identical arithmetic and no fixture call",
        )
        add(
            "tail",
            cp,
            rp,
            f"return {leaf}(a, b);",
            f"{leaf}(a, b)",
            [leaf],
            1,
            "tail-call candidate; caller has no work after the callee returns",
        )
        add(
            "post",
            cp,
            rp,
            f"return ({cty})({leaf}(a, b) + 1u);",
            f"{leaf}(a, b).wrapping_add(1)",
            [leaf],
            1,
            "post-call arithmetic prevents a simple tail transfer",
        )
        add(
            "chain",
            cp + f", {cty} c",
            rp + f", c: {ty}",
            f"{cty} x = {leaf}(a, b); return {leaf}(x, c);",
            f"let x = {leaf}(a, b); {leaf}(x, c)",
            [leaf],
            2,
            "two dependent calls; c stays live across the first call",
        )
        add(
            "args6",
            ", ".join(f"{cty} {p}" for p in "abcdef"),
            ", ".join(f"{p}: {ty}" for p in "abcdef"),
            f"return {six}(a, b, c, d, e, f);",
            f"{six}(a, b, c, d, e, f)",
            [six],
            1,
            "six arguments expose register/stack argument placement and wide returns",
        )
        add(
            "indirect",
            f"{cty} (*f)({cty}, {cty}), " + cp,
            f'f: extern "C" fn({ty}, {ty}) -> {ty}, ' + rp,
            "return f(a, b);",
            "f(a, b)",
            [],
            1,
            "runtime function pointer prevents devirtualization; includes ABI trampoline overhead",
        )
        for count in [2, 4, 8]:
            loads_c = " ".join(f"{cty} v{i} = p[{i}];" for i in range(count))
            loads_r = " ".join(
                f"let v{i} = core::ptr::read_volatile(p.add({i}));"
                for i in range(count)
            )
            fold_c = " ".join(
                f"r = ({cty})((r ^ v{i}) + (r >> 1));" for i in range(count)
            )
            fold_r = " ".join(
                f"r = (r ^ v{i}).wrapping_add(r >> 1);" for i in range(count)
            )
            add(
                f"live{count}",
                f"const volatile {cty} *p, " + cp,
                f"p: *const {ty}, " + rp,
                f"{loads_c} {cty} r = {leaf}(a, b); {fold_c} return r;",
                f"{loads_r} let mut r = {leaf}(a, b); {fold_r} r",
                [leaf],
                1,
                "volatile loads occur before the call; dependent nonlinear folding uses each value afterward and prevents a simple reduction before the call",
                live=count,
            )
            add(
                f"live{count}_inline",
                f"const volatile {cty} *p, " + cp,
                f"p: *const {ty}, " + rp,
                f"{loads_c} {cty} r = ({cty})(a + b); {fold_c} return r;",
                f"{loads_r} let mut r = a.wrapping_add(b); {fold_r} r",
                [],
                0,
                "matching pressure control with the leaf arithmetic written inline; scheduling may differ because there is no call clobber",
                live=0,
            )
        for size in [8, 32]:
            add(
                f"local{size}",
                cp,
                rp,
                f"uint8_t p[{size}]; for (uint8_t i = 0; i < {size}; ++i) p[i] = (uint8_t)(a + i); {cty} r = {touch}(p, b); return ({cty})(r + ({cty})p[0] + ({cty})p[{size - 1}]);",
                f"let mut storage = core::mem::MaybeUninit::<[u8; {size}]>::uninit(); let p = storage.as_mut_ptr().cast::<u8>(); for i in 0..{size} {{ *p.add(i) = (a as u8).wrapping_add(i as u8); }} let r = {touch}(p, b); r.wrapping_add(*p as {ty}).wrapping_add(*p.add({size - 1}) as {ty})",
                [touch],
                1,
                "callee receives a fully initialized local buffer address; Rust uses MaybeUninit to avoid extra zero-filling; distinguishes required stack storage from allocator spills",
                frame=size,
            )
        group_cases = [c for c in cases if c["type"] == group]
        cbody = (
            C_HEADER
            + "\n"
            + "\n\n".join(h["c_function"] for h in support.values())
            + "\n\n"
            + "\n\n".join(c["c_function"] for c in group_cases)
            + "\n"
        )
        rbody = (
            RUST_HEADER
            + "\n"
            + "\n\n".join(h["rust_function"] for h in support.values())
            + "\n\n"
            + "\n\n".join(c["rust_function"] for c in group_cases)
            + "\n"
        )
        (ROOT / f"cases/{group}.c").write_text(cbody)
        (ROOT / f"cases/{group}.rs").write_text(rbody)
    return cases
