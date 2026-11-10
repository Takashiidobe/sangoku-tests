#!/usr/bin/env python3
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import shutil
import subprocess

from analyze import instructions

ROOT = Path(__file__).resolve().parents[1]
BEGIN = "<!-- begin case catalog -->"
END = "<!-- end case catalog -->"
OPERATIONS = {
    "add": "Wrapping addition",
    "sub": "Wrapping subtraction",
    "mul": "Wrapping multiplication",
    "div": "Division, valid divisors",
    "rem": "Remainder, valid divisors",
    "and": "Bitwise AND",
    "or": "Bitwise OR",
    "xor": "Bitwise XOR",
    "not": "Bitwise complement",
    "neg": "Wrapping negation",
    "eq": "Equal, returns 0/1",
    "ne": "Not equal, returns 0/1",
    "lt": "Less than, returns 0/1",
    "le": "Less or equal, returns 0/1",
    "gt": "Greater than, returns 0/1",
    "ge": "Greater or equal, returns 0/1",
    "min": "Select minimum",
    "max": "Select maximum",
    "add1": "Add constant 1",
    "mul3": "Multiply by 3",
    "mul10": "Multiply by 10",
    "div3": "Divide by 3",
    "rem10": "Remainder modulo 10",
    "shl": "Left shift, masked count",
    "shr": "Right shift, masked count",
    "shl1": "Left shift by 1",
    "shl7": "Left shift by 7",
    "shr1": "Right shift by 1",
    "shr7": "Right shift by 7",
    "rol": "Rotate left, masked count",
    "ror": "Rotate right, masked count",
}
STRING_OPERATIONS = {
    "strlen": "NUL length through CStr/libc",
    "strlen_loop": "NUL length, matching loops",
    "strcmp": "String order through CStr/libc",
    "strcmp_loop": "String order, matching loops",
    "strncmp": "Bounded string order",
    "strchr": "First byte in NUL string",
    "strrchr": "Last byte in NUL string",
    "strcpy": "Copy string including NUL",
    "strncpy": "Bounded copy with zero padding",
    "memcpy": "Copy non-overlapping bytes",
    "memmove": "Copy possibly overlapping bytes",
    "memset": "Fill bytes",
    "memcmp": "Lexicographic byte order",
    "memeq": "Byte equality",
    "memchr": "First byte in bounded memory",
}


def description(row):
    op, kind = row["operation"], row["kind"]
    if kind == "pattern":
        return row["description"]
    if kind == "call":
        fixed = {
            "leaf": "Leaf addition control",
            "tail": "Tail-call candidate",
            "post": "Call then increment",
            "chain": "Two dependent calls",
            "args6": "Forward six arguments",
            "indirect": "Runtime callback",
        }
        if op in fixed:
            return fixed[op]
        if op.startswith("live"):
            match = re.search(r"\d+", op)
            if match is None:
                raise ValueError(f"pressure fixture has no value count: {op}")
            count = match[0]
            return (
                f"{count} loaded values, inline control"
                if op.endswith("_inline")
                else f"{count} values live across call"
            )
        return f"{row['explicit_local_array_bytes']}-byte local array passed to callee"
    if kind == "string":
        base = row.get("base_operation", re.sub(r"(4|16)$", "", op))
        fixed = row.get("fixed_length")
        return (
            STRING_OPERATIONS[base]
            + (f", {fixed} bytes" if fixed is not None else "")
            + (
                f", pointer offset {row['pointer_offset']}"
                if row.get("pointer_offset")
                else ""
            )
        )
    if op in {"as_signed", "as_unsigned", "narrow", "widen"}:
        return f"{row['type']} -> {row['result_type']}: " + (
            "truncate low bits"
            if op == "narrow"
            else "sign extend"
            if op == "widen" and row["signed"]
            else "zero extend"
            if op == "widen"
            else "bit-pattern cast"
        )
    text = OPERATIONS[op]
    if kind == "integer" and op.startswith("shr"):
        text = text.replace(
            "Right shift",
            "Arithmetic right shift" if row["signed"] else "Logical right shift",
        )
    if kind == "float":
        text = text.replace("Wrapping ", "Float ")
        if op in {"div", "rem"}:
            text = "Float " + op
        if op == "ne":
            text += "; NaN is unequal"
    return text


def number(value):
    return f"{value:,}" if isinstance(value, int) else "n/a"


def body_sizes(row):
    values = [
        row[name].get("function_bytes") if row[name]["status"] == "ok" else None
        for name in ["sangoku", "sdcc"]
    ]
    text = " / ".join(number(v) for v in values)
    if row["comparison"]["status"] == "compared":
        delta = row["comparison"]["bytes_delta"]
        text += f" ({delta:+,})" if delta else " (tie)"
    else:
        text += (
            " (pattern only)"
            if row["comparison"]["status"] == "pattern_only"
            else " (unavailable)"
        )
    return text


def helper_summary(result):
    transfers = result.get("external_transfers", [])
    counts = Counter((t["kind"], t["target"]) for t in transfers)
    return ", ".join(
        (f"{count}x " if count > 1 else "")
        + ("call " if kind == "call" else "tail ")
        + f"`{target}`"
        for (kind, target), count in counts.items()
    )


def symptoms(row, by_id):
    rust, c = row["sangoku"], row["sdcc"]
    if rust["status"] != "ok":
        return "Rust compilation/measurement failed; inspect the saved diagnostic."
    parts = []
    op = row["operation"]
    notes = {n["category"]: n for n in row.get("analysis", {}).get("notes", [])}
    stack = rust.get("stack", {})
    if row["kind"] == "call":
        control = row["comparison"].get("call_control")
        if control and row.get("live_values_across_call"):
            changes = control["sangoku"]
            parts.append(
                f"vs inline control: caller {changes['caller_bytes_delta']:+,} B, reservation {changes['entry_add_sp_reservation_delta']:+,} B"
            )
        if op == "tail":
            parts.append("S: " + helper_summary(rust) + "; C: " + helper_summary(c))
        elif op == "indirect":
            if re.search(r"call\s+@\s*\+", rust.get("assembly", "")):
                text = "S synthesizes a return address for `jp hl`"
                trampoline = next(
                    (
                        t["target"]
                        for t in c.get("external_transfers", [])
                        if "call_hl" in t["target"]
                    ),
                    None,
                )
                if trampoline:
                    text += f"; C calls `{trampoline}`"
                parts.append(text)
        frame = stack.get("entry_add_sp_reservation_bytes", 0)
        other = c.get("stack", {}).get("entry_add_sp_reservation_bytes", 0)
        if frame or other:
            parts.append(f"leading SP reservation {frame:,}/{other:,} B")
        if row.get("explicit_local_array_bytes"):
            parts.append(
                f"source requires {row['explicit_local_array_bytes']} B array storage"
            )
    total = row["comparison"].get("with_dependencies")
    if total:
        text = f"with helpers {total['sangoku_bytes']:,}/{total['sdcc_bytes']:,} B"
        if total["smaller"] != row["comparison"]["smaller"]:
            text += "; body ranking reverses"
        parts.append(text)
    if row["kind"] == "string" and op in {"strlen", "strcmp"}:
        loop = by_id.get(row["id"] + "_loop")
        if loop and loop["sangoku"]["status"] == "ok":
            parts.append(
                f"Rust matched-loop body is {loop['sangoku']['function_bytes']:,} B"
            )
    constant = notes.get("constant_lowering", {}).get("evidence")
    if constant:
        parts.append(
            f"variable `{constant['variable_case']}` body is {constant['variable_bytes']:,} B"
        )
        if op in {"div3", "rem10"} and any(
            "mul" in t["target"] for t in rust.get("external_transfers", [])
        ):
            parts.append("S: " + helper_summary(rust))
    moves = notes.get("redundant_moves", {}).get("evidence", {})
    reloads = moves.get("immediate_reloads", {})
    identities = moves.get("identity_moves", {})
    if reloads.get("count"):
        example = "; ".join(reloads["examples"][0]["instructions"])
        parts.append(f"{reloads['count']} immediate reload(s), e.g. `{example}`")
    elif identities.get("count"):
        parts.append(
            f"{identities['count']} self-copy/copies, e.g. `{identities['examples'][0]['instruction']}`"
        )
    if row["kind"] != "call" and (
        rust.get("stack_reference_count") or c.get("stack_reference_count")
    ):
        parts.append(
            f"SP references {rust['stack_reference_count']:,}/{c['stack_reference_count']:,}"
            if c["status"] == "ok"
            else f"S has {rust['stack_reference_count']:,} SP references; C unavailable"
        )
    transfers = helper_summary(rust)
    if (
        transfers
        and "S: " + transfers not in parts
        and not (row["kind"] == "call" and op == "tail")
    ):
        parts.append("S: " + transfers)
    elif not transfers and c.get("external_transfers"):
        parts.append("S has no named helper transfers; C: " + helper_summary(c))
    if rust.get("inline_machine_code_bytes"):
        parts.append(f"{rust['inline_machine_code_bytes']:,} B emitted through `db`")
    if not parts:
        if row["comparison"].get("smaller") == "tie":
            parts.append(
                "Same body size; no stack references or named helper transfers"
            )
        else:
            lines = [text for _, text in instructions(rust["assembly"])]
            parts.append(
                "S starts with "
                + (
                    "`" + "; ".join(lines[:3]) + "`"
                    if lines
                    else "a direct register-only sequence"
                )
            )
    selected = parts[:4] if row.get("live_values_across_call") else parts[:3]
    if rust.get("inline_machine_code_bytes") and not any("`db`" in p for p in selected):
        selected.append(
            f"{rust['inline_machine_code_bytes']:,} raw `db` bytes are outside source instruction counts"
        )
    if c["status"] != "ok":
        selected.append(
            (
                "No SDCC baseline for this feature"
                if row.get("c_capability_source")
                else "No SDCC baseline at this width"
            )
            if c["status"] == "unsupported"
            else "SDCC measurement unavailable"
        )
    return "; ".join(selected) + "."


def investigation(row):
    rust, c = row["sangoku"], row["sdcc"]
    if rust["status"] != "ok":
        return "Resolve the compiler/measurement failure before judging size."
    kind, op = row["kind"], row["operation"]
    if kind == "pattern":
        leads = {
            "formatting": "Inspect quotient/remainder sharing, temporary digit buffers and formatting-library setup; compare matched decimal/hex loops.",
            "parsing": "Inspect digit classification, multiply-add chains, overflow handling and end-pointer stores; preserve the declared parse contract.",
            "ctype": "Compare range checks with libc/core ASCII APIs; inspect integer promotions and boolean/case materialization.",
            "spans": "Inspect nested membership scans, tokenizer state and repeated CStr construction; compare loop and library variants.",
            "substring": "Inspect restart pointers, short-needle matching and window/slice metadata; preserve empty-needle handling.",
            "concat": "Inspect destination rescans, source scan/copy fusion and capacity checks; distinguish source bounds from destination capacity.",
            "aggregates": "Compare aggregate assignment, by-value return and out-parameter controls; separate required ABI copies from temporary storage.",
            "slices": "Compare raw/indexed/iterator forms; inspect bounds-check elimination, metadata and memory-intrinsic selection.",
            "search_sort": "Compare matched loops before library algorithms; inspect scaled addressing, comparator callbacks and sort recursion.",
            "packing_checksum": "Inspect byte-to-word assembly, endian transforms, carry/shift selection and loop-carried state.",
            "dispatch": "Inspect compare chains versus tables, shared exits and loop-carried parser state.",
        }
        return leads[row["pattern_family"]]
    if kind == "call":
        if op == "tail":
            return "Check tail-call eligibility and ABI cleanup before replacing call/return."
        if op == "indirect":
            return "Inspect return-address synthesis, callback trampoline, and argument shuffles."
        if op.startswith("local"):
            return f"Separate the required {row['explicit_local_array_bytes']}-byte array from other temporaries; inspect loop/address lowering."
        if op.startswith("live"):
            return (
                "Use as the no-call pressure baseline; inspect scheduling and live ranges."
                if op.endswith("_inline")
                else "Compare with its inline control; classify live ranges and save/reload traffic before calling it spills."
            )
        return {
            "leaf": "Keep as an ABI/arithmetic control for the calling fixtures.",
            "args6": "Inspect argument shuffles, outgoing stack slots, and return-value placement.",
            "post": "Inspect preserving the call result and doing the increment without extra moves.",
            "chain": "Inspect preservation of the third argument across the first call and reuse of the return registers.",
        }[op]
    if kind == "string":
        if op in {"strlen", "strcmp"}:
            return (
                "Compare the matched loop; inspect materialized CStr/slice temporaries"
                + (
                    " and the separate NUL scans before comparison."
                    if op == "strcmp"
                    else " around the length helper."
                )
            )
        if op == "strcpy":
            return "Separate the scan-then-copy algorithm from marshaling cost; compare a fused NUL-copy loop."
        if op in {"strlen_loop", "strcmp_loop"}:
            return "Inspect native register-pair arithmetic, compare lowering, and short branch layout."
        total = row["comparison"].get("with_dependencies")
        if total and total["smaller"] == "sangoku":
            return "Preserve this helper-inclusive size win; measure cycles and helper sharing before changing the strategy."
        if row.get("fixed_length") is not None:
            return "Evaluate inline small-copy/fill/compare lowering against the retained general helper."
        if op == "memeq":
            return "Check equality-only lowering and caller setup against full ordering comparison."
        if op in {"strchr", "strrchr", "memchr"}:
            return "Inspect pointer/counter updates and exit branches; retain NUL and unsigned-byte semantics."
        return "Inspect helper argument setup and loop addressing; compare reachable library bodies."
    if op in {"as_signed", "as_unsigned", "narrow", "widen"}:
        if row["comparison"].get("smaller") == "tie":
            return "Keep as a cast/ABI regression control; preserve the result width and extension semantics."
        return "Inspect unchanged-byte forwarding, sign/zero extension, and ABI return copies."
    targets = [t["target"] for t in rust.get("external_transfers", [])]
    if op in {"div3", "rem10"}:
        if any("mul" in t for t in targets):
            return "Check reciprocal-multiply expansion and its size cost against division/remainder helpers; confirm in intermediate IR."
        return (
            "Compare constant lowering with the variable form, including helper bodies."
        )
    if op in {"mul3", "mul10"}:
        return "Compare shift/add strength reduction with multiplication-helper setup and total helper cost."
    if kind == "float":
        if row["width"] == 16 and any("f16tof32" in t for t in targets):
            return "Inspect the f16-to-f32 conversion chain and ABI setup; this is a Rust-only pattern, not an SDCC loss."
        if op == "neg":
            return "Inspect sign-bit manipulation and return movement without changing signed-zero/NaN behavior."
        return "Inspect soft-float helper marshaling and boolean materialization; validate edge behavior before replacing helpers."
    if op in {"eq", "ne", "lt", "le", "gt", "ge"}:
        return "Inspect compare and 0/1 materialization; decode raw bytes before counting branches."
    if op in {"min", "max"}:
        return "Inspect compare-plus-select lowering and preservation of the selected value."
    if op.startswith(("shl", "shr")) or op in {"rol", "ror"}:
        return "Inspect count masking, constant-shift/rotate selection, and helper marshaling; preserve shift semantics."
    moves = next(
        (
            n
            for n in row.get("analysis", {}).get("notes", [])
            if n["category"] == "redundant_moves"
        ),
        None,
    )
    if moves:
        return "Start with post-allocation copy cleanup, then inspect pair arithmetic and stack traffic."
    if rust.get("external_transfers") or c.get("external_transfers"):
        return "Compare helper ABI setup and reachable helper bodies before treating a smaller wrapper as a win."
    if row["comparison"].get("smaller") == "tie":
        return "Keep as a size regression control; equal bytes do not establish equal runtime."
    return "Inspect register-pair/carry lowering and return placement; separate ABI costs from avoidable copies."


def source_link(row, root):
    path = row["rust_source"]
    source = root / path
    line = None
    if source.is_file():
        match = re.search(
            rf"^pub .*?fn {re.escape(row['id'])}\(", source.read_text(), re.M
        )
        if match:
            line = source.read_text()[: match.start()].count("\n") + 1
    return f"[`{row['id']}`]({path}" + (f"#L{line}" if line else "") + ")"


def cell(text):
    return str(text).replace("|", "\\|").replace("\n", " ")


def render_catalog(report, root=ROOT):
    rows = report["runs"]["size"]["cases"]
    by_id = {row["id"]: row for row in rows}
    if len(rows) != len(by_id):
        raise ValueError("duplicate case IDs in size report")
    speed = {row["id"]: row for row in report["runs"].get("speed", {}).get("cases", [])}
    groups = {}
    for row in rows:
        groups.setdefault(row["type"], []).append(row)
    lines = [
        "## Per-case codegen catalog",
        "",
        f"Snapshot: `{report['generated_at']}`. Each of the {len(rows)} fixtures has its own row below. S means sangoku; C means SDCC.",
        "",
        "Body sizes use size mode (`z` versus `--opt-code-size`); a signed delta is S minus C. A speed-mode value appears only when body or measured dependency sizes differ.",
        "",
        "These are static symptoms, not established optimizer root causes or timing results. Body bytes exclude helpers and include native ABI costs. String/memory and libc-style pattern rows also give isolated helper-inclusive totals.",
        "",
        "Standalone integer/float Rust helper totals are unavailable. Call fixture callees are measured separately; their callees and runtime helpers are not included in caller body bytes.",
        "",
        "SP reservations exclude pushes, return addresses, callee frames, and alternate frame setup. SP references count source instructions, not spills.",
        "",
        "Raw `db` bytes contribute to size but not source mnemonic/branch counts. Unsupported SDCC widths or features are pattern-only cases. An investigation lead is a hypothesis to test against assembly/IR and the relevant control.",
        "",
        "Start with one small control, make one change, then rerun the case and its control before expanding the comparison:",
        "",
        "| Starting point | Visible symptom | First experiment |",
        "| --- | --- | --- |",
        "",
        "Reproduce one row without rebuilding the suite:",
        "",
        "```bash",
        "python3 tools/compare.py --case u8_add --modes size",
        "python3 tools/report.py results/u8_add.json --case u8_add",
        "```",
        "",
        "Jump to a group: "
        + ", ".join(f"[{group}](#{group})" for group in groups)
        + ".",
        "",
    ]
    priority_rows = []
    for name in [
        "u8_add",
        "calls_u8_tail",
        "strings_strlen",
        "u16_div3",
        "calls_u64_live8",
    ]:
        if name in by_id:
            row = by_id[name]
            priority_rows.append(
                "| "
                + " | ".join(
                    cell(value)
                    for value in [
                        f"[`{name}`](#{row['type']})",
                        symptoms(row, by_id),
                        investigation(row),
                    ]
                )
                + " |"
            )
    position = lines.index("| --- | --- | --- |") + 1
    lines[position:position] = priority_rows
    for group, members in groups.items():
        counts = Counter(
            row["comparison"].get("smaller", row["comparison"]["status"])
            for row in members
        )
        summary = ", ".join(f"{count} {label}" for label, count in counts.items())
        lines += [
            f"### {group}",
            "",
            "<details>",
            f"<summary>{len(members)} fixtures; body outcomes: {summary}. Expand the case-by-case notes.</summary>",
            "",
            "| Case (Rust source) | Exercises | Body bytes S / C (delta) | Outward symptoms | First investigation lead |",
            "| --- | --- | ---: | --- | --- |",
        ]
        for row in members:
            visible = symptoms(row, by_id)
            other = speed.get(row["id"])
            if other and any(
                other[k].get("function_bytes") != row[k].get("function_bytes")
                for k in ["sangoku", "sdcc"]
            ):
                visible += (
                    " Speed body: "
                    + " / ".join(
                        number(other[k].get("function_bytes"))
                        for k in ["sangoku", "sdcc"]
                    )
                    + " B."
                )
            deps, other_deps = (
                row["comparison"].get("with_dependencies"),
                other["comparison"].get("with_dependencies") if other else None,
            )
            if (
                deps
                and other_deps
                and any(
                    deps[k] != other_deps[k] for k in ["sangoku_bytes", "sdcc_bytes"]
                )
            ):
                visible += f" Speed with helpers: {other_deps['sangoku_bytes']:,}/{other_deps['sdcc_bytes']:,} B."
            lines.append(
                "| "
                + " | ".join(
                    cell(value)
                    for value in [
                        source_link(row, root),
                        description(row),
                        body_sizes(row),
                        visible,
                        investigation(row),
                    ]
                )
                + " |"
            )
        lines += ["", "</details>", ""]
    return "\n".join(lines).strip() + "\n"


def replace_catalog(readme, catalog):
    if BEGIN not in readme and END not in readme:
        return (
            readme.rstrip()
            + "\n\n"
            + BEGIN
            + "\n\n"
            + catalog.rstrip()
            + "\n\n"
            + END
            + "\n"
        )
    if (
        readme.count(BEGIN) != 1
        or readme.count(END) != 1
        or readme.index(BEGIN) >= readme.index(END)
    ):
        raise ValueError("README must have exactly one ordered pair of catalog markers")
    before, rest = readme.split(BEGIN, 1)
    _, after = rest.split(END, 1)
    return before + BEGIN + "\n\n" + catalog.rstrip() + "\n\n" + END + after


def main():
    parser = argparse.ArgumentParser(
        description="Refresh every README case summary from an existing comparison report; does not compile fixtures."
    )
    parser.add_argument("--report", type=Path, default=ROOT / "results/comparison.json")
    parser.add_argument("--readme", type=Path, default=ROOT / "README.md")
    parser.add_argument(
        "--check", action="store_true", help="Check catalog freshness without writing"
    )
    args = parser.parse_args()
    report = json.loads(args.report.read_text())
    expected = {c["id"] for c in json.loads((ROOT / "cases/manifest.json").read_text())}
    actual = {c["id"] for c in report["runs"]["size"]["cases"]}
    if expected != actual:
        parser.error(
            f"use a full report matching the current manifest; missing {len(expected - actual)}, extra {len(actual - expected)} cases"
        )
    prettier = shutil.which("prettier")
    if not prettier:
        parser.error("prettier is required to format the README catalog")
    catalog = render_catalog(report)
    formatted = subprocess.run(
        [
            prettier,
            "--parser",
            "markdown",
            "--prose-wrap",
            "always",
            "--print-width",
            "80",
        ],
        input=catalog,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    original = args.readme.read_text()
    updated = replace_catalog(original, formatted)
    if args.check:
        if updated != original:
            print("README case catalog is stale; run python3 tools/update_readme.py")
            return 1
        print(f"README case catalog is current: {len(actual)} fixtures")
        return 0
    args.readme.write_text(updated)
    print(f"Updated {len(actual)} case summaries in {args.readme}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
