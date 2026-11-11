#!/usr/bin/env python3
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import shutil
import subprocess

from analyze import instructions
from references import body_bytes, choose_reference, dependency_bytes

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


def measurement_pair(row, metric="body"):
    measure = body_bytes if metric == "body" else dependency_bytes
    reference = choose_reference(row, metric)
    return measure(row.get("sangoku", {})), reference.get("bytes")


def comparison_sizes(row, metric="body"):
    sangoku, best = measurement_pair(row, metric)
    text = f"{number(sangoku)} / {number(best)} B"
    if sangoku is not None and best is not None:
        delta = sangoku - best
        text += f" ({delta:+,})" if delta else " (tie)"
    return text


def body_sizes(row):
    return comparison_sizes(row)


def cycle_sizes(sample):
    results = sample["compilers"]
    sangoku = results.get("sangoku", {})
    current = sangoku.get("t_cycles") if sangoku.get("status") == "ok" else None
    references = [
        results[name]["t_cycles"]
        for name in ("sdcc", "llvm_z80")
        if results.get(name, {}).get("status") == "ok"
    ]
    best = min(references) if references else None
    text = f"{number(current)} / {number(best)} T"
    if current is not None and best is not None:
        text += f" ({current - best:+,})" if current != best else " (tie)"
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
    rust = row["sangoku"]
    if rust["status"] != "ok":
        return "Sangoku compilation/measurement failed; inspect the saved diagnostic."
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
        if op == "indirect" and re.search(r"call\s+@\s*\+", rust.get("assembly", "")):
            parts.append("Sangoku synthesizes a return address for `jp hl`")
        frame = stack.get("entry_add_sp_reservation_bytes", 0)
        if frame:
            parts.append(f"leading SP reservation {frame:,} B")
        if row.get("explicit_local_array_bytes"):
            parts.append(
                f"source requires {row['explicit_local_array_bytes']} B array storage"
            )
    if row["kind"] == "string" and op in {"strlen", "strcmp"}:
        loop = by_id.get(row["id"] + "_loop")
        if loop and loop["sangoku"]["status"] == "ok":
            parts.append(
                f"matched-loop body is {loop['sangoku']['function_bytes']:,} B"
            )
    constant = notes.get("constant_lowering", {}).get("evidence")
    if constant:
        parts.append(
            f"variable `{constant['variable_case']}` body is {constant['variable_bytes']:,} B"
        )
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
    if row["kind"] != "call" and rust.get("stack_reference_count"):
        parts.append(f"{rust['stack_reference_count']:,} SP references")
    transfers = helper_summary(rust)
    if transfers:
        parts.append(transfers)
    if not parts:
        if choose_reference(row, "body").get("sangoku_delta") == 0:
            parts.append(
                "same body size; no stack references or named helper transfers"
            )
        else:
            lines = [text for _, text in instructions(rust["assembly"])]
            parts.append(
                "starts with "
                + (
                    "`" + "; ".join(lines[:3]) + "`"
                    if lines
                    else "a direct register-only sequence"
                )
            )
    selected = parts[:4] if row.get("live_values_across_call") else parts[:3]
    if rust.get("inline_machine_code_bytes"):
        selected.append(
            f"{rust['inline_machine_code_bytes']:,} raw `db` bytes are outside source instruction counts"
        )
    return "; ".join(selected) + "."


def case_notes(row, by_id, speed=None):
    parts = [symptoms(row, by_id), investigation(row)]
    body = measurement_pair(row)
    complete = measurement_pair(row, "with_dependencies")
    if complete[1] is not None and (
        complete[1] != body[1] or (complete[0] is not None and complete[0] != body[0])
    ):
        parts.append(
            "With helpers: " + comparison_sizes(row, "with_dependencies") + "."
        )
        if (
            all(value is not None for value in (*body, *complete))
            and (body[0] - body[1]) * (complete[0] - complete[1]) < 0
        ):
            parts.append("Body ranking reverses with helpers.")
    if body[1] is None:
        failed = [
            v
            for name in ("sdcc", "llvm_z80")
            if (v := row.get(name, {})).get("status") == "error"
        ]
        reason = (
            "instruction legalization failed"
            if any("unable to legalize" in v.get("diagnostic", "") for v in failed)
            else "inspect the saved diagnostics"
        )
        parts.append("Reference unavailable; " + reason + ".")
    elif (
        body[0] is not None
        and body[0] < body[1]
        and row["sangoku"].get("external_transfers")
        and complete[0] is None
    ):
        parts.append("Sangoku helper costs are unmeasured.")
    if speed:
        speed_body = measurement_pair(speed)
        speed_complete = measurement_pair(speed, "with_dependencies")
        if speed_body != body:
            parts.append("Speed: " + comparison_sizes(speed) + ".")
        if (
            speed_complete[1] is not None
            and speed_complete != complete
            and speed_complete != speed_body
        ):
            parts.append(
                "Speed with helpers: "
                + comparison_sizes(speed, "with_dependencies")
                + "."
            )
    return " ".join(parts)


def investigation(row):
    rust = row["sangoku"]
    reference = choose_reference(row, "body")
    best = row.get(reference.get("compilers", [None])[0], {})
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
        total = choose_reference(row, "with_dependencies")
        if total.get("sangoku_delta") is not None and total["sangoku_delta"] < 0:
            return "Preserve this helper-inclusive size win; measure cycles and helper sharing before changing the strategy."
        if row.get("fixed_length") is not None:
            return "Evaluate inline small-copy/fill/compare lowering against the retained general helper."
        if op == "memeq":
            return "Check equality-only lowering and caller setup against full ordering comparison."
        if op in {"strchr", "strrchr", "memchr"}:
            return "Inspect pointer/counter updates and exit branches; retain NUL and unsigned-byte semantics."
        return "Inspect helper argument setup and loop addressing; compare reachable library bodies."
    if op in {"as_signed", "as_unsigned", "narrow", "widen"}:
        if reference.get("sangoku_delta") == 0:
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
            return "Inspect the f16-to-f32 conversion chain and ABI setup; compare conversion costs with direct arithmetic."
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
    if rust.get("external_transfers") or best.get("external_transfers"):
        return "Compare helper ABI setup and reachable helper bodies before treating a smaller wrapper as a win."
    if reference.get("sangoku_delta") == 0:
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


def rust_only_rows(report, mode):
    return [
        row
        for row in report["runs"][mode]["cases"]
        if row.get("sdcc", {}).get("status") == "unsupported"
    ]


def rust_only_outcomes(rows):
    counts = Counter()
    for row in rows:
        sangoku = body_bytes(row.get("sangoku", {}))
        llvm = body_bytes(row.get("llvm_z80", {}))
        if row.get("llvm_z80", {}).get("status") == "error":
            outcome = "errors"
        elif sangoku is None or llvm is None:
            outcome = "unavailable"
        else:
            outcome = (
                "llvm" if llvm < sangoku else "sangoku" if sangoku < llvm else "tie"
            )
        counts[outcome] += 1
        if (
            outcome == "sangoku"
            and row["sangoku"].get("external_transfers")
            and dependency_bytes(row["sangoku"]) is None
        ):
            counts["unmeasured_helper_wins"] += 1
    return counts


def llvm_diagnostic(result):
    lines = result.get("diagnostic", "").splitlines()
    reason = next((line for line in lines if "error" in line.lower()), None)
    if reason is None:
        reason = next(
            (line for line in lines if line.strip()), result.get("status", "not run")
        )
    return reason[:240] + ("…" if len(reason) > 240 else "")


def render_rust_only_summary(report, catalog="", level=3):
    modes = [mode for mode in ("size", "speed") if mode in report["runs"]]
    lines = [
        "#" * level + " Rust-only reference coverage",
        "",
        "These fixtures are unsupported by SDCC. Body sizes exclude runtime helpers and constant data and include native ABI costs. LLVM errors remain visible; unavailable results never count as zero or as a win.",
        "",
        "| Mode | Family | Cases | LLVM smaller | Sangoku smaller | Tied | LLVM errors | Unavailable |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    failures = {}
    states = {}
    paired = []
    caveats = []
    for mode in modes:
        rows = rust_only_rows(report, mode)
        groups = {}
        for row in rows:
            family = (
                "aggregate returns"
                if row["type"].startswith("aggregate_return")
                else row["type"]
            )
            groups.setdefault(family, []).append(row)
            llvm = row.get("llvm_z80", {})
            states.setdefault(row["id"], {})[mode] = llvm.get("status", "not run")
            if llvm.get("status") == "error":
                failures.setdefault(
                    row["id"], {"type": row["type"], "reason": llvm_diagnostic(llvm)}
                )
            sangoku_total = dependency_bytes(row.get("sangoku", {}))
            llvm_total = dependency_bytes(llvm)
            if sangoku_total is not None and llvm_total is not None:
                paired.append((mode, row, sangoku_total, llvm_total))
        for family, members in [*groups.items(), ("Total", rows)]:
            counts = rust_only_outcomes(members)
            values = [
                mode,
                family,
                len(members),
                *(
                    counts[k]
                    for k in ("llvm", "sangoku", "tie", "errors", "unavailable")
                ),
            ]
            lines.append("| " + " | ".join(cell(v) for v in values) + " |")
        counts = rust_only_outcomes(rows)
        if counts["unmeasured_helper_wins"]:
            caveats.append(
                f"{mode}: {counts['unmeasured_helper_wins']} of {counts['sangoku']} Sangoku body wins call runtime helpers whose complete costs are unavailable."
            )
    if caveats:
        lines += [
            "",
            " ".join(caveats)
            + " These body wins do not establish smaller complete implementations.",
        ]
    if paired:
        lines += [
            "",
            "#" * (level + 1) + " Rust-only complete-cost comparisons",
            "",
            "Only cases with complete measurements from both compilers appear here. Missing Sangoku integer/float helper totals are not inferred from body sizes.",
            "",
            "| Mode | Case | Sangoku complete | LLVM complete | S minus LLVM |",
            "| --- | --- | ---: | ---: | ---: |",
        ]
        for mode, row, sangoku, llvm in paired:
            link = f"[`{row['id']}`]({catalog}#{row['type']})"
            lines.append(
                f"| {mode} | {link} | {number(sangoku)} B | {number(llvm)} B | {sangoku - llvm:+,} B |"
            )
    if failures:
        lines += [
            "",
            "#" * (level + 1) + " Rust-only LLVM failures",
            "",
            "| Case | " + " | ".join(modes) + " | Diagnostic |",
            "| --- | " + " | ".join("---" for _ in modes) + " | --- |",
        ]
        for name, failure in failures.items():
            link = f"[`{name}`]({catalog}#{failure['type']})"
            delimiter = "`" * (
                max((len(s) for s in re.findall(r"`+", failure["reason"])), default=0)
                + 1
            )
            values = [
                link,
                *(states[name].get(mode, "not run") for mode in modes),
                f"{delimiter} {failure['reason']} {delimiter}",
            ]
            lines.append("| " + " | ".join(cell(v) for v in values) + " |")
    lines += [
        "",
        "Inspect a probe with `python3 tools/report.py --case CASE --dependencies`, or show this subset with `python3 tools/report.py --rust-only`.",
        "",
    ]
    return "\n".join(lines)


def render_rust_only_report(report):
    lines = [
        "# Rust-only codegen comparison",
        "",
        f"Snapshot: `{report['generated_at']}`. Generated by `python3 tools/update_readme.py`; do not edit this snapshot by hand.",
        "",
        render_rust_only_summary(report, "../README.md", level=2),
        "Complete costs include reachable code and constant data; native LLVM ELF totals also include section padding. These are static sizes, without target execution or cycle measurements.",
        "",
    ]
    for mode in ("size", "speed"):
        if mode not in report["runs"]:
            continue
        lines += [
            f"## Every Rust-only probe, {mode} mode",
            "",
            "| Probe | Sangoku body | LLVM body | S minus LLVM | Sangoku complete | LLVM complete | S calls helpers |",
            "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
        for row in rust_only_rows(report, mode):
            sangoku, llvm = row.get("sangoku", {}), row.get("llvm_z80", {})
            sangoku_body, llvm_body = body_bytes(sangoku), body_bytes(llvm)
            link = f"[`{row['id']}`](../README.md#{row['type']})"
            values = [
                link,
                number(sangoku_body),
                number(llvm_body)
                if llvm_body is not None
                else llvm.get("status", "not run"),
                f"{sangoku_body - llvm_body:+,}"
                if sangoku_body is not None and llvm_body is not None
                else "n/a",
                number(dependency_bytes(sangoku)),
                number(dependency_bytes(llvm)),
                "yes" if sangoku.get("external_transfers") else "no",
            ]
            lines.append("| " + " | ".join(cell(v) for v in values) + " |")
        lines.append("")
    return "\n".join(lines)


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
        f"Snapshot: `{report['generated_at']}`. Each of the {len(rows)} fixtures has its own row below.",
        "",
        "Sangoku vs best gives size-mode function-body bytes as Sangoku / best (Sangoku minus best). Best is the smallest measured reference, not a proof of optimality. Reference compiler details are in the full report.",
        "",
        "Body sizes exclude external helpers and constant data and include native ABI costs. Notes show complete costs and speed-mode sizes when they differ. Missing measurements are n/a, never zero; standalone Sangoku integer/float helper totals remain unavailable.",
        "",
        "Cycle subcases show each exact input and expected output, followed by Sangoku / best T-cycles. Timings include the function's return and all executed helpers; caller setup and result checking are excluded. Size and speed builds are measured separately. The fastest verified reference is selected per input, independently of the size reference. Untimed cases have no cycle subrows.",
        "",
        "Notes describe Sangoku's assembly and give an investigation lead, not an established optimizer root cause or timing result. SP reservations exclude pushes and return addresses; SP references are not spill counts. Raw `db` bytes count toward size but not source instruction counts.",
        "",
        "Inspect source, assembly and compiler details with `python3 tools/report.py --case CASE --dependencies`.",
        "",
        "Jump to a group: "
        + ", ".join(f"[{group}](#{group})" for group in groups)
        + ".",
        "",
    ]
    for group, members in groups.items():
        counts = Counter()
        for row in members:
            delta = choose_reference(row, "body").get("sangoku_delta")
            label = (
                "unavailable"
                if delta is None
                else "sangoku"
                if delta < 0
                else "tie"
                if delta == 0
                else "best"
            )
            counts[label] += 1
        summary = ", ".join(f"{count} {label}" for label, count in counts.items())
        lines += [
            f"### {group}",
            "",
            "<details>",
            f"<summary>{len(members)} fixtures; body outcomes: {summary}. Expand the case-by-case notes.</summary>",
            "",
            "| Case (Rust source) | Sangoku vs best | Notes |",
            "| --- | ---: | --- |",
        ]
        for row in members:
            values = [
                source_link(row, root),
                body_sizes(row),
                case_notes(row, by_id, speed.get(row["id"])),
            ]
            lines.append("| " + " | ".join(cell(value) for value in values) + " |")
            for mode, measured in [("size", row), ("speed", speed.get(row["id"], {}))]:
                for sample in measured.get("cycles", {}).get("samples", []):
                    label = f"↳ cycles ({mode}): `{sample['input']}` → `{sample['expected']}`"
                    current = sample["compilers"].get("sangoku", {})
                    problems = []
                    if current.get("status") != "ok":
                        problems.append(
                            "Sangoku timing failed: "
                            + current.get("diagnostic", "not measured")
                        )
                    if not any(
                        sample["compilers"].get(name, {}).get("status") == "ok"
                        for name in ("sdcc", "llvm_z80")
                    ):
                        problems.append(
                            "Reference timing unavailable; inspect saved diagnostics."
                        )
                    values = [
                        label,
                        cycle_sizes(sample),
                        " ".join(problems) or "Output verified.",
                    ]
                    lines.append(
                        "| " + " | ".join(cell(value) for value in values) + " |"
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
        "--rust-only-output",
        type=Path,
        help="Generated Rust-only report (default: results/rust-only.md beside the README)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check README and Rust-only report freshness without writing",
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

    def format_markdown(markdown):
        return subprocess.run(
            [
                prettier,
                "--parser",
                "markdown",
                "--prose-wrap",
                "always",
                "--print-width",
                "80",
            ],
            input=markdown,
            capture_output=True,
            text=True,
            check=True,
        ).stdout

    formatted = format_markdown(render_catalog(report))
    rust_only_path = (
        args.rust_only_output or args.readme.parent / "results/rust-only.md"
    )
    rust_only = format_markdown(render_rust_only_report(report))
    original = args.readme.read_text()
    updated = replace_catalog(original, formatted)
    if args.check:
        stale = []
        if updated != original:
            stale.append(str(args.readme))
        if not rust_only_path.is_file() or rust_only_path.read_text() != rust_only:
            stale.append(str(rust_only_path))
        if stale:
            print(
                "Generated reports are stale: "
                + ", ".join(stale)
                + "; run python3 tools/update_readme.py"
            )
            return 1
        print(f"README and Rust-only report are current: {len(actual)} fixtures")
        return 0
    args.readme.write_text(updated)
    rust_only_path.parent.mkdir(parents=True, exist_ok=True)
    rust_only_path.write_text(rust_only)
    print(f"Updated {len(actual)} case summaries in {args.readme}")
    print(f"Updated Rust-only comparisons in {rust_only_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
