#!/usr/bin/env python3
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any

from analyze import annotate
from compile_cache import SangokuCache, SdccCache
from cycle_cases import subcases
from cycle_runner import DEFAULT_LIBRARY
from generate import ROOT, generate
from libraries import SdccLibrary, measure_rust_link, measure_sdcc_link
from llvm_z80 import LlvmZ80
from references import annotate_references, reference_summary
from rust_z80 import NativeRustZ80
from setup_llvm_z80 import DEFAULT_BIN
from setup_rust_z80 import DEFAULT_RUSTC
from stack_metrics import stack_metrics


def run(command, cwd=ROOT, timeout=180):
    command = [str(arg) for arg in command]
    try:
        p = subprocess.run(
            command, cwd=cwd, capture_output=True, text=True, timeout=timeout
        )
        return {
            "command": command,
            "returncode": p.returncode,
            "stdout": p.stdout,
            "stderr": p.stderr,
        }
    except subprocess.TimeoutExpired as e:
        return {
            "command": command,
            "returncode": None,
            "stdout": "",
            "stderr": f"timeout after {timeout}s: {e}",
        }


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def asm_metrics(assembly):
    histogram = Counter()
    calls = []
    stack_refs = 0
    identity_moves = 0
    inline_bytes = 0
    for raw in assembly.splitlines():
        line = raw.split(";", 1)[0].strip()
        if not line or line.endswith(":") or line.startswith("."):
            continue
        op, *tail = line.split(None, 1)
        op = op.lower()
        args = tail[0] if tail else ""
        if op in {"section", "export", "global", "def"}:
            continue
        if op == "db":
            inline_bytes += len(args.split(","))
            continue
        histogram[op] += 1
        stack_refs += bool(re.search(r"\bsp\b", args))
        if op == "ld":
            operands = [v.strip() for v in args.split(",")]
            identity_moves += len(operands) == 2 and operands[0] == operands[1]
        if op in {"call", "jp", "jr"}:
            target = args.split(",")[-1].strip()
            if re.fullmatch(r"[_A-Za-z][_A-Za-z0-9]*", target) and target not in {
                "hl",
                "de",
                "bc",
            }:
                calls.append({"kind": op, "target": target})
    return {
        "source_instruction_count": sum(histogram.values()),
        "inline_machine_code_bytes": inline_bytes,
        "mnemonics": dict(sorted(histogram.items())),
        "stack_reference_count": stack_refs,
        "push_count": histogram["push"],
        "pop_count": histogram["pop"],
        "identity_move_count": identity_moves,
        "external_transfers": calls,
        "stack": stack_metrics(assembly),
    }


def rust_sections(assembly):
    return re.findall(
        r'^SECTION\s+"([^"]+)"[^\n]*\n(.*?)(?=^SECTION\s|\Z)', assembly, re.M | re.S
    )


def measure_rust(assembly_path, cases, work):
    assembly = assembly_path.read_text()
    ids = {f"__rust_{c['id']}": c["id"] for c in cases}
    measured = []
    bodies = {}
    names = []
    for section, body in rust_sections(assembly):
        measured.append(f'SECTION "{section}", ROM0\n{body}')
        for symbol, name in ids.items():
            if re.search(rf"^{re.escape(symbol)}::?\s*$", body, re.M):
                index = len(names)
                names.append(name)
                bodies[name] = body
                measured.append(f"DEF suite_bytes_{index} EQU @ - {symbol}\n")
    instrumented = work / "measured.asm"
    state = work / "sizes.asm"
    instrumented.write_text("\n".join(measured))
    result = run(
        ["rgbasm", "-s", f"equ:{state}", "-o", work / "measured.o", instrumented]
    )
    if result["returncode"] != 0:
        raise ValueError(f"RGBDS assembly failed: {result['stderr']}")
    sizes = {
        names[int(i)]: int(value.removeprefix("$"), 16)
        if value.startswith("$")
        else int(value)
        for i, value in re.findall(
            r"def suite_bytes_(\d+) equ (\$[0-9a-fA-F]+|\d+)", state.read_text(), re.I
        )
    }
    return {
        name: {
            "function_bytes": sizes[name],
            "assembly": bodies[name],
            **asm_metrics(bodies[name]),
        }
        for name in names
    }


def measure_sdcc(assembly_path, rel_path, cases):
    assembly = assembly_path.read_text()
    rel = rel_path.read_text()
    code = re.search(r"^A _CODE size ([0-9A-Fa-f]+) ", rel, re.M)
    if not code:
        raise ValueError("SDCC object is missing the _CODE area")
    area = None
    symbols = []
    for line in rel.splitlines():
        if line.startswith("A "):
            area = line.split()[1]
        match = re.fullmatch(r"S (_\w+) Def([0-9A-Fa-f]+)", line)
        if match and area == "_CODE":
            symbols.append((int(match[2], 16), match[1]))
    symbols.sort()
    ends = {
        name: (symbols[i + 1][0] if i + 1 < len(symbols) else int(code[1], 16)) - offset
        for i, (offset, name) in enumerate(symbols)
    }
    result = {}
    for case in cases:
        name = case["id"]
        body = re.search(
            rf"^_{name}::\s*\n(.*?)(?=^_\w+::|^\s*\.area|\Z)", assembly, re.M | re.S
        )
        if body and f"_{name}" in ends:
            text = (
                "\n".join(
                    line
                    for line in body[1].splitlines()
                    if line.strip() and not line.lstrip().startswith(";")
                )
                + "\n"
            )
            result[name] = {
                "function_bytes": ends[f"_{name}"],
                "assembly": text,
                **asm_metrics(text),
            }
    return result


def support_functions(cases, compiler=None):
    return list(
        {
            helper["id"]: helper
            for case in cases
            for helper in case.get("support_functions", [])
            if compiler is None
            or ("rust" if compiler == "sangoku" else "c")
            in helper.get("languages", ["c", "rust"])
        }.values()
    )


def selected_source(source, cases, compiler):
    header = source.read_text().split("\n\n", 1)[0]
    key = "rust_function" if compiler == "sangoku" else "c_function"
    return (
        header
        + "\n\n"
        + "\n\n".join(c[key] for c in support_functions(cases, compiler) + cases)
        + "\n"
    )


def compile_group(compiler, cases, mode, args, directory):
    directory.mkdir(parents=True, exist_ok=True)
    source = ROOT / cases[0]["rust_source" if compiler == "sangoku" else "c_source"]
    if getattr(args, "case", None) or cases[0].get("kind") == "pattern":
        contents = selected_source(source, cases, compiler)
        source = directory / ("selected.rs" if compiler == "sangoku" else "selected.c")
        source.write_text(contents)
    results = {}
    logs = []
    cache = getattr(
        args, "compile_cache" if compiler == "sangoku" else "sdcc_cache", None
    )
    runner = cache.run if cache else run
    if compiler == "sdcc":
        header = source.read_text().split("\n\n", 1)[0]
        probe = directory / "capability.c"
        probe.write_text(cases[0].get("c_capability_source", header + "\n"))
        capability = runner(
            [
                args.sdcc,
                "-msm83",
                "--std-c11",
                "--Werror",
                "--disable-warning",
                "110",
                "-S",
                probe,
                "-o",
                directory / "capability.asm",
            ],
            timeout=args.timeout,
        )
        logs.append(capability)
        if capability["returncode"] != 0:
            return {
                c["id"]: {
                    "status": "error"
                    if capability["returncode"] is None
                    else "unsupported",
                    "diagnostic": capability["stderr"],
                }
                for c in cases
            }, logs

    def compile_one(group, input_path, work):
        work.mkdir(parents=True, exist_ok=True)
        if compiler == "sangoku":
            asm = work / "output.asm"
            command = [
                args.sangoku,
                "asm",
                input_path,
                asm,
                "--opt-level",
                "z" if mode == "size" else "3",
            ]
        else:
            rel = work / "output.rel"
            asm = work / "output.asm"
            command = [
                args.sdcc,
                "-msm83",
                "--std-c11",
                "--Werror",
                "--disable-warning",
                "110",
                "--opt-code-" + mode,
                "-c",
                input_path,
                "-o",
                rel,
            ]
        outcome = runner(command, timeout=args.timeout)
        logs.append(outcome)
        if outcome["returncode"] != 0:
            return None, outcome["stderr"]
        try:
            helpers = support_functions(group, compiler)
            measured_cases = group + helpers
            metrics = (
                measure_rust(asm, measured_cases, work)
                if compiler == "sangoku"
                else measure_sdcc(asm, rel, measured_cases)
            )
        except (ValueError, KeyError, OSError) as e:
            return None, str(e)
        records: dict[str, dict[str, Any]] = {}
        for c in group:
            if c["id"] not in metrics:
                records[c["id"]] = {
                    "status": "error",
                    "diagnostic": "function symbol missing from emitted assembly",
                }
            else:
                records[c["id"]] = {
                    "status": "ok",
                    "assembly_path": str(asm.relative_to(ROOT))
                    if asm.is_relative_to(ROOT)
                    else str(asm),
                    **metrics[c["id"]],
                }
                own_helpers = support_functions([c], compiler)
                if own_helpers:
                    missing = [h["id"] for h in own_helpers if h["id"] not in metrics]
                    if missing:
                        records[c["id"]] = {
                            "status": "error",
                            "diagnostic": "fixture helper symbols missing: "
                            + ", ".join(missing),
                        }
                        continue
                    records[c["id"]]["fixture_helpers"] = {
                        h["id"]: metrics[h["id"]] for h in own_helpers
                    }
                    records[c["id"]]["fixture_helper_bytes"] = sum(
                        metrics[h["id"]]["function_bytes"] for h in own_helpers
                    )
                    records[c["id"]]["function_with_fixture_helpers_bytes"] = (
                        metrics[c["id"]]["function_bytes"]
                        + records[c["id"]]["fixture_helper_bytes"]
                    )
        for c in group:
            record = records[c["id"]]
            if (
                c.get("kind") == "call"
                and c["operation"] != "indirect"
                and record["status"] == "ok"
            ):
                prefix = "__rust_" if compiler == "sangoku" else "_"
                targets = {prefix + h["id"] for h in c.get("support_functions", [])}
                found = sum(
                    t["target"] in targets for t in record["external_transfers"]
                )
                if found != c["expected_fixture_calls"]:
                    records[c["id"]] = {
                        "status": "error",
                        "diagnostic": f"expected {c['expected_fixture_calls']} fixture calls/tail transfers, found {found}",
                    }
        return records, ""

    records, diagnostic = compile_one(cases, source, directory)
    if records is not None:
        return records, logs
    print(f"  {compiler}: group failed; isolating {len(cases)} cases", flush=True)
    for c in cases:
        work = directory / c["id"]
        work.mkdir(parents=True, exist_ok=True)
        isolated = work / ("case.rs" if compiler == "sangoku" else "case.c")
        isolated.write_text(selected_source(source, [c], compiler))
        record, error = compile_one([c], isolated, work)
        results.update(
            record
            or {
                c["id"]: {
                    "status": "error",
                    "diagnostic": error,
                    "group_diagnostic": diagnostic,
                }
            }
        )
    return results, logs


def compare_case(c, rust, sdcc):
    if rust["status"] != "ok" or sdcc["status"] != "ok":
        return {
            "status": "pattern_only"
            if rust["status"] == "ok" and sdcc["status"] == "unsupported"
            else "unavailable"
        }
    rb, cb = rust["function_bytes"], sdcc["function_bytes"]
    return {
        "status": "compared",
        "bytes_delta": rb - cb,
        "bytes_ratio": rb / cb if cb else None,
        "stack_reference_delta": rust["stack_reference_count"]
        - sdcc["stack_reference_count"],
        "helper_dependent": bool(
            rust["external_transfers"] or sdcc["external_transfers"]
        ),
        "smaller": "tie" if rb == cb else "sangoku" if rb < cb else "sdcc",
    }


def summarize(rows) -> dict[str, Any]:
    counts = Counter(row["comparison"]["status"] for row in rows)
    compared = [r for r in rows if r["comparison"]["status"] == "compared"]
    return {
        "cases": len(rows),
        "statuses": dict(counts),
        "smaller_function_counts": dict(
            Counter(r["comparison"]["smaller"] for r in compared)
        ),
        "dependency_comparisons": sum(
            "with_dependencies" in r["comparison"] for r in compared
        ),
        "dependency_smaller_counts": dict(
            Counter(
                r["comparison"]["with_dependencies"]["smaller"]
                for r in compared
                if "with_dependencies" in r["comparison"]
            )
        ),
        "compiler_statuses": {
            name: dict(Counter(r.get(name, {}).get("status", "not_run") for r in rows))
            for name in ["sangoku", "sdcc", "llvm_z80"]
        },
        "best_observed_references": reference_summary(rows),
        "largest_byte_gaps": [
            {
                "id": r["id"],
                **r["comparison"],
                "sangoku_bytes": r["sangoku"]["function_bytes"],
                "sdcc_bytes": r["sdcc"]["function_bytes"],
            }
            for r in sorted(
                compared, key=lambda r: r["comparison"]["bytes_delta"], reverse=True
            )[:20]
        ],
    }


def patterns(rows):
    groups = defaultdict(list)
    for row in rows:
        key = (
            ("signed" if row["signed"] else "unsigned")
            if row["kind"] == "integer"
            else row["kind"]
        )
        groups[(key, row["operation"])].append(row)
    return [
        {
            "family": family,
            "operation": op,
            "widths": [
                {
                    "type": r["type"],
                    "width": r["width"],
                    "comparison": r["comparison"]["status"],
                    **{
                        compiler: {
                            k: r[compiler].get(k)
                            for k in [
                                "status",
                                "function_bytes",
                                "stack_reference_count",
                                "external_transfers",
                            ]
                        }
                        for compiler in ["sangoku", "sdcc"]
                    },
                }
                for r in sorted(group, key=lambda r: r["width"])
            ],
        }
        for (family, op), group in sorted(groups.items())
    ]


def select_cases(cases, types=None, case_ids=None):
    if types and set(types) - {c["type"] for c in cases}:
        raise ValueError(
            "unknown types: "
            + ", ".join(sorted(set(types) - {c["type"] for c in cases}))
        )
    if case_ids and set(case_ids) - {c["id"] for c in cases}:
        raise ValueError(
            "unknown cases: "
            + ", ".join(sorted(set(case_ids) - {c["id"] for c in cases}))
        )
    selected = [
        c
        for c in cases
        if (not types or c["type"] in types) and (not case_ids or c["id"] in case_ids)
    ]
    if not selected:
        raise ValueError("no cases match the selected types and case IDs")
    return selected


def main():
    parser = argparse.ArgumentParser(
        description="Generate paired SM83 probes and compare assembled function bodies."
    )
    parser.add_argument(
        "--sangoku", type=Path, default=ROOT.parent / "sangoku/target/release/sangoku"
    )
    parser.add_argument("--sdcc", default="sdcc")
    parser.add_argument(
        "--cycles",
        action="store_true",
        help="Measure declared input subcases in SameBoy, including helpers",
    )
    parser.add_argument("--sameboy-library", type=Path, default=DEFAULT_LIBRARY)
    parser.add_argument("--llvm-z80", type=Path, default=DEFAULT_BIN, metavar="BIN_DIR")
    parser.add_argument(
        "--llvm-rustc",
        type=Path,
        default=DEFAULT_RUSTC,
        help="Native Rust-Z80 compiler",
    )
    parser.add_argument(
        "--llvm-frontend",
        choices=["native", "ir"],
        default="native",
        help="Native Rust-Z80, or the experimental scalar IR adapter",
    )
    parser.add_argument(
        "--without-llvm-z80", action="store_true", help="Run only Sangoku and SDCC"
    )
    parser.add_argument(
        "--llvm-rust-toolchain",
        default="nightly-2026-10-25",
        help="Rust frontend for the experimental scalar LLVM reference",
    )
    parser.add_argument(
        "--kind",
        choices=["integer", "float", "string", "call", "pattern"],
        help="Select a fixture family",
    )
    parser.add_argument(
        "--modes", nargs="+", choices=["size", "speed"], default=["size", "speed"]
    )
    parser.add_argument(
        "--types", nargs="+", help="Select types, e.g. u8 i16 f32 u128 strings"
    )
    parser.add_argument(
        "--case",
        nargs="+",
        help="Compile only these exact case IDs, e.g. u8_add strings_memmove",
    )
    parser.add_argument(
        "--list", action="store_true", help="List matching case IDs without compiling"
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Compile without reading or writing compiler caches",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=ROOT / "build/sangoku-cache",
        help="Persistent compiler artifact cache",
    )
    args = parser.parse_args()
    try:
        all_cases = generate()
        cases = select_cases(all_cases, args.types, args.case)
        if args.kind:
            cases = [c for c in cases if c["kind"] == args.kind]
            if not cases:
                raise ValueError("no cases match the selected kind")
    except ValueError as error:
        parser.error(str(error))
    if args.list:
        print("\n".join(c["id"] for c in cases))
        return 0
    if args.cycles:
        if args.without_llvm_z80 or args.llvm_frontend != "native":
            parser.error("--cycles requires the native reference toolchain")
        if not any(subcases(case) for case in cases):
            parser.error(
                "no timing subcases are declared for the selected fixtures; add them in tools/cycle_cases.py"
            )
        if not args.sameboy_library.is_file():
            parser.error(
                "SameBoy library missing; build SameBoy with make lib and pass --sameboy-library PATH"
            )
        args.cycle_case = None
    if args.output is None:
        name = (
            cases[0]["id"]
            if args.case and len(cases) == 1
            else "selected"
            if args.case
            else args.kind + "s"
            if args.kind
            else "comparison"
        )
        args.output = ROOT / "results" / f"{name}.json"
    args.sangoku = args.sangoku.resolve()
    for executable in [str(args.sangoku), args.sdcc, "rgbasm", "sdar"]:
        if not shutil.which(executable):
            parser.error(f"executable not found: {executable}")
    try:
        args.compile_cache = (
            None if args.no_cache else SangokuCache(args.cache_dir, args.sangoku, run)
        )
        args.sdcc_cache = (
            None
            if args.no_cache
            else SdccCache(args.cache_dir / "sdcc", args.sdcc, run)
        )
    except (ValueError, OSError) as error:
        parser.error(str(error))
    groups = defaultdict(list)
    for c in cases:
        groups[c["type"]].append(c)
    work = (
        ROOT
        / "build"
        / ("run-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f"))
    )
    try:
        llvm = None
        if not args.without_llvm_z80:
            llvm = (
                NativeRustZ80(args.llvm_z80, args.llvm_rustc, run, args.timeout)
                if args.llvm_frontend == "native"
                else LlvmZ80(args.llvm_z80, args.llvm_rust_toolchain, run, args.timeout)
            )
    except (ValueError, OSError) as error:
        parser.error(str(error))
    sdcc_library = SdccLibrary(args.sdcc, work / "sdcc-library")
    report: dict[str, Any] = {
        "schema_version": 3,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "target": "sm83 / LR35902",
        "methodology": {
            "metric": "assembled function-body bytes, including prologue/epilogue; external helper bodies excluded",
            "rust_measurement": "RGBDS section-relative EQU differences",
            "c_measurement": "SDCC relocatable object _CODE symbol offsets",
            "abi": "native compiler calling conventions; extern C does not make the two ABIs identical",
            "integer_division": "Rust unchecked intrinsics match the C valid-input domain; no Rust panic guards",
            "signed_c_arithmetic": "unsigned intermediates and casts; two-complement conversion and arithmetic right shift required",
            "float_widths": "C sizeof assertions prevent double/long double silently becoming f32",
            "instruction_counts": "source mnemonics only; inline db machine code reported separately",
            "scope": "static codegen comparison; no cycle estimates or target runtime equivalence checks",
            "library_cost": "SDCC archive dependency bytes for all supported cases; isolated linked reachable ROM sections for Rust string cases; no startup, entry harness or alignment padding",
            "llvm_z80": llvm.metadata["method"] + "; machine outlining disabled"
            if llvm
            else "disabled",
            "reference": "best observed SDCC/LLVM-Z80 size per metric; body excludes external helpers, with_dependencies requires complete transitive dependency measurements; not a proof of optimality or speed",
        },
        "tools": {},
        "sources": {},
        "runs": {},
        "commands": [],
    }
    for name, cmd in {
        "sdcc": [args.sdcc, "--version"],
        "sangoku": [args.sangoku, "--help"],
        "rgbasm": ["rgbasm", "--version"],
        "rustc": ["rustc", "+gbc-lr35902", "-Vv"],
    }.items():
        outcome = run(cmd)
        report["tools"][name] = {
            "command": outcome["command"],
            "version": outcome["stdout"] + outcome["stderr"],
        }
    report["tools"]["sangoku"]["binary_sha256"] = digest(args.sangoku)
    if llvm:
        report["tools"]["llvm_z80"] = llvm.metadata
        report["commands"] += [
            {"compiler": "llvm_z80", "phase": "setup", **log} for log in llvm.logs
        ]
    repo = ROOT.parent / "sangoku"
    if (repo / ".git").exists():
        report["tools"]["sangoku"]["checkout_commit"] = run(
            ["git", "rev-parse", "HEAD"], cwd=repo
        )["stdout"].strip()
        report["tools"]["sangoku"]["checkout_status"] = run(
            ["git", "status", "--porcelain", "--untracked-files=no"], cwd=repo
        )["stdout"]
    for c in cases:
        for key in ["c_source", "rust_source"]:
            report["sources"][c[key]] = digest(ROOT / c[key])
    failed = False
    for mode in dict.fromkeys(args.modes):
        rows = []
        for ty, group in groups.items():
            print(f"{mode}: {ty} ({len(group)} cases)", flush=True)
            results: dict[str, dict[str, Any]] = {}
            for compiler in ["sangoku", "sdcc"]:
                results[compiler], logs = compile_group(
                    compiler, group, mode, args, work / mode / ty / compiler
                )
                report["commands"] += [
                    {"compiler": compiler, "mode": mode, "type": ty, **log}
                    for log in logs
                ]
            if llvm:
                results["llvm_z80"], logs = llvm.compile_group(
                    group, mode, work / mode / ty / "llvm_z80"
                )
                report["commands"] += [
                    {"compiler": "llvm_z80", "mode": mode, "type": ty, **log}
                    for log in logs
                ]
            else:
                results["llvm_z80"] = {
                    c["id"]: {
                        "status": "not_run",
                        "diagnostic": "disabled with --without-llvm-z80",
                    }
                    for c in group
                }
            for c in group:
                r, s = results["sangoku"][c["id"]], results["sdcc"][c["id"]]
                if s["status"] == "ok":
                    fixture_symbols = {
                        "_" + name for name in s.get("fixture_helpers", {})
                    }
                    transfers = s["external_transfers"] + [
                        t
                        for h in s.get("fixture_helpers", {}).values()
                        for t in h["external_transfers"]
                    ]
                    s["library"] = sdcc_library.resolve(
                        t["target"]
                        for t in transfers
                        if t["target"] not in fixture_symbols
                    )
                    if s["library"]["status"] == "ok":
                        s["library"]["total_bytes"] = (
                            s["function_bytes"]
                            + s.get("fixture_helper_bytes", 0)
                            + s["library"]["dependency_bytes"]
                        )
                if c["kind"] in {"string", "pattern"} and s["status"] == "ok":
                    s["library"], link_logs = measure_sdcc_link(
                        c,
                        mode,
                        args,
                        work / mode / ty / "sdcc-linked" / c["id"],
                        s["library"],
                        args.sdcc_cache.run if args.sdcc_cache else run,
                    )
                    report["commands"] += [
                        {
                            "compiler": "sdcc",
                            "phase": "link",
                            "mode": mode,
                            "case": c["id"],
                            **log,
                        }
                        for log in link_logs
                    ]
                    failed |= s["library"]["status"] == "error"
                if c["kind"] in {"string", "pattern"} and r["status"] == "ok":
                    r["library"], link_log = measure_rust_link(
                        c,
                        mode,
                        args,
                        work / mode / ty / "linked" / c["id"],
                        args.compile_cache.run if args.compile_cache else run,
                    )
                    report["commands"].append(
                        {
                            "compiler": "sangoku",
                            "phase": "link",
                            "mode": mode,
                            "case": c["id"],
                            **link_log,
                        }
                    )
                    failed |= r["library"]["status"] == "error"
                failed |= r["status"] == "error" or s["status"] == "error"
                failed |= results["llvm_z80"][c["id"]]["status"] == "error"
                rows.append(
                    {
                        **c,
                        "sangoku": r,
                        "sdcc": s,
                        "llvm_z80": results["llvm_z80"][c["id"]],
                        "comparison": compare_case(c, r, s),
                    }
                )
        annotate(rows)
        annotate_references(rows)
        report["runs"][mode] = {
            "summary": summarize(rows),
            "patterns": patterns(rows),
            "cases": rows,
        }
        print(
            json.dumps(report["runs"][mode]["summary"]["compiler_statuses"]), flush=True
        )
    backend = (
        repo
        / "third_party/rustc_codegen_cranelift/target/release/librustc_codegen_cranelift.so"
    )
    if backend.is_file():
        report["tools"]["sangoku"]["backend_sha256"] = digest(backend)
    if args.cycles:
        from measure_cycles import add_cycles

        failed |= add_cycles(report, args)
    args.output = args.output.resolve()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.compile_cache and args.sdcc_cache:
        report["cache"] = {
            "hits": args.compile_cache.hits,
            "misses": args.compile_cache.misses,
            "sdcc": {
                "hits": args.sdcc_cache.hits,
                "misses": args.sdcc_cache.misses,
                "compile_seconds": args.sdcc_cache.seconds,
            },
        }
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    if args.compile_cache:
        print(
            f"Sangoku cache: {args.compile_cache.hits} hits, {args.compile_cache.misses} misses"
        )
    if args.sdcc_cache:
        print(
            f"SDCC cache: {args.sdcc_cache.hits} hits, {args.sdcc_cache.misses} misses ({args.sdcc_cache.seconds:.3f}s compiling)"
        )
    print(f"Wrote {args.output}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
