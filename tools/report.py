#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from typing import Any

from compare import summarize
from references import annotate_references, body_bytes, dependency_bytes

ROOT = Path(__file__).resolve().parents[1]


def rust_fixture(row):
    return (
        row["rust_function"],
        row.get("rust_header", "#![no_std]\n"),
        tuple(
            (helper["id"], helper["rust_function"])
            for helper in row.get("support_functions", [])
            if "rust" in helper.get("languages", ["c", "rust"])
        ),
        row.get("link_entry"),
    )


def rust_sizes(result):
    if result["status"] != "ok":
        return {}
    sizes = {"body": result["function_bytes"]}
    if "function_with_fixture_helpers_bytes" in result:
        sizes["body + fixture helpers"] = result["function_with_fixture_helpers_bytes"]
    library = result.get("library", {})
    if library.get("status") == "ok":
        sizes["linked"] = library["total_bytes"]
    return sizes


def cycle_inputs(row):
    return {
        sample["input"]: sample for sample in row.get("cycles", {}).get("samples", [])
    }


def print_baseline(previous, report, modes, args):
    def cases(data, mode):
        return {
            row["id"]: row
            for row in data["runs"].get(mode, {}).get("cases", [])
            if (not args.case or row["id"] == args.case)
            and (not args.kind or row["kind"] == args.kind)
            and (
                not args.rust_only or row.get("sdcc", {}).get("status") == "unsupported"
            )
        }

    failed = False
    compared = 0
    cycle_compared = 0
    for mode in modes:
        before, after = cases(previous, mode), cases(report, mode)
        annotate_references(list(before.values()))
        annotate_references(list(after.values()))
        changes = []
        coverage = []
        losses = 0
        unchanged = 0
        cycle_changes = []
        cycle_losses = 0
        for name in sorted(before.keys() | after.keys()):
            if name not in before:
                coverage.append(f"{name}: new case")
                continue
            if name not in after:
                coverage.append(f"{name}: missing from candidate")
                losses += 1
                cycle_losses += sum(
                    s["compilers"].get("sangoku", {}).get("status") == "ok"
                    for s in cycle_inputs(before[name]).values()
                )
                continue
            if rust_fixture(before[name]) != rust_fixture(after[name]):
                coverage.append(f"{name}: Rust fixture changed; comparison skipped")
                continue
            old, new = before[name]["sangoku"], after[name]["sangoku"]
            old_sizes, new_sizes = rust_sizes(old), rust_sizes(new)
            if old["status"] != new["status"]:
                coverage.append(
                    f"{name}: compile status {old['status']} -> {new['status']}"
                )
            elif old.get("library", {}).get("status") != new.get("library", {}).get(
                "status"
            ):
                coverage.append(f"{name}: linked result changed availability")
            common = old_sizes.keys() & new_sizes.keys()
            if common:
                compared += 1
                unchanged += old_sizes == new_sizes
            for metric in sorted(old_sizes.keys() - new_sizes.keys()):
                coverage.append(f"{name}: lost {metric} measurement")
                losses += 1
            for metric in common:
                start, end = old_sizes[metric], new_sizes[metric]
                if start != end:
                    changes.append((end - start, name, metric, start, end))
            for metric in ("body", "with_dependencies"):
                old_ref = before[name].get("reference", {}).get(metric, {})
                new_ref = after[name].get("reference", {}).get(metric, {})
                if old_ref.get("candidates") != new_ref.get("candidates"):
                    coverage.append(
                        f"{name}: {metric} reference changed; Sangoku deltas above use absolute sizes"
                    )
            old_inputs, new_inputs = (
                cycle_inputs(before[name]),
                cycle_inputs(after[name]),
            )
            for label, old_sample in old_inputs.items():
                new_sample = new_inputs.get(label)
                if new_sample and any(
                    old_sample.get(k) != new_sample.get(k)
                    for k in ("args", "memory", "expected")
                ):
                    coverage.append(f"{name}: timing input changed ({label}); skipped")
                    continue
                old_cycle = old_sample["compilers"].get("sangoku", {})
                new_cycle = (
                    new_sample["compilers"].get("sangoku", {}) if new_sample else {}
                )
                if old_cycle.get("status") == "ok":
                    if new_cycle.get("status") != "ok":
                        coverage.append(f"{name}: lost cycle measurement for {label}")
                        cycle_losses += 1
                    else:
                        cycle_compared += 1
                        if old_cycle["t_cycles"] != new_cycle["t_cycles"]:
                            cycle_changes.append(
                                (
                                    name,
                                    label,
                                    old_cycle["t_cycles"],
                                    new_cycle["t_cycles"],
                                )
                            )

        growth = sum(delta > 0 for delta, *_ in changes)
        savings = len(changes) - growth
        print(
            f"{mode} mode: {growth} larger measurements, {savings} smaller, {unchanged} unchanged cases"
        )
        if changes:
            print(
                f"{'case':<35} {'measurement':<23} {'before':>8} {'after':>8} {'delta B':>8}"
            )
            for delta, name, metric, start, end in sorted(
                changes, key=lambda item: (-item[0], item[1], item[2])
            ):
                print(f"{name:<35} {metric:<23} {start:>8} {end:>8} {delta:>+8}")
                reference_metric = {"body": "body", "linked": "with_dependencies"}.get(
                    metric
                )
                if reference_metric:
                    old_ref = before[name]["reference"][reference_metric]
                    new_ref = after[name]["reference"][reference_metric]
                    if new_ref["status"] == "ok":
                        old_gap, new_gap = (
                            old_ref.get("sangoku_delta"),
                            new_ref["sangoku_delta"],
                        )
                        print(
                            f"  Best observed {reference_metric}: {'/'.join(new_ref['compilers'])} {new_ref['bytes']} B; gap {old_gap} -> {new_gap} B"
                        )
        if cycle_changes:
            print("\nT-cycles per input (including helpers):")
            print(
                f"{'case':<28} {'input':<28} {'before':>8} {'after':>8} {'delta T':>8}"
            )
            for name, label, start, end in cycle_changes:
                print(f"{name:<28} {label:<28} {start:>8} {end:>8} {end - start:>+8}")
        for message in coverage:
            print(f"  {message}")
        if args.max_growth is not None:
            over = sum(delta > args.max_growth for delta, *_ in changes)
            if over or losses:
                print(
                    f"  Budget exceeded: {over} measurements over +{args.max_growth} B, {losses} lost cases or measurements"
                )
                failed = True
        if args.max_cycle_growth is not None:
            over = sum(
                end - start > args.max_cycle_growth
                for _, _, start, end in cycle_changes
            )
            if over or cycle_losses:
                print(
                    f"  Cycle budget exceeded: {over} inputs over +{args.max_cycle_growth} T, {cycle_losses} lost measurements"
                )
                failed = True
    if not compared:
        print("No comparable successful Sangoku cases.")
        failed = True
    if args.max_cycle_growth is not None and not cycle_compared:
        print("No comparable successful timing inputs.")
        failed = True
    return int(failed)


def main():
    parser = argparse.ArgumentParser(description="Inspect the SM83 comparison report.")
    parser.add_argument(
        "report", nargs="?", type=Path, default=ROOT / "results/comparison.json"
    )
    parser.add_argument(
        "--kind",
        choices=["integer", "float", "string", "call", "pattern"],
        help="Show one probe family",
    )
    parser.add_argument(
        "--mode",
        choices=["size", "speed"],
        help="Optimization mode (default: size, or both with --baseline)",
    )
    parser.add_argument(
        "--case", help="Show source and assembly for a case, e.g. u8_add"
    )
    parser.add_argument(
        "--dependencies",
        action="store_true",
        help="Show reachable helper assembly with --case",
    )
    parser.add_argument(
        "--rust-only",
        action="store_true",
        help="Show fixtures unsupported by SDCC, including native LLVM failures",
    )
    parser.add_argument(
        "--baseline", type=Path, help="Compare Sangoku codegen with an earlier report"
    )
    parser.add_argument(
        "--max-growth",
        type=int,
        metavar="BYTES",
        help="With --baseline, fail if any measured case grows by more than BYTES or loses a result",
    )
    parser.add_argument(
        "--max-cycle-growth",
        type=int,
        metavar="T_CYCLES",
        help="With --baseline, fail on per-input cycle growth above this budget or lost timings",
    )
    args = parser.parse_args()
    report = json.loads(args.report.read_text())
    if args.max_growth is not None and (not args.baseline or args.max_growth < 0):
        parser.error("--max-growth requires --baseline and a nonnegative byte budget")
    if args.max_cycle_growth is not None and (
        not args.baseline or args.max_cycle_growth < 0
    ):
        parser.error(
            "--max-cycle-growth requires --baseline and a nonnegative T-cycle budget"
        )
    if args.baseline:
        previous = json.loads(args.baseline.read_text())
        if report["target"] != previous["target"]:
            parser.error("baseline and report target different architectures")
        modes = (
            [args.mode]
            if args.mode
            else sorted(report["runs"].keys() | previous["runs"].keys())
        )
        if args.mode and any(
            args.mode not in item["runs"] for item in (report, previous)
        ):
            parser.error(f"both reports must contain a {args.mode} run")
        return print_baseline(previous, report, modes, args)
    args.mode = args.mode or "size"
    if args.mode not in report["runs"]:
        parser.error(f"report has no {args.mode} run")
    run: dict[str, Any] = report["runs"][args.mode]
    annotate_references(run["cases"])
    if args.kind or args.rust_only:
        run = {
            **run,
            "cases": [
                r
                for r in run["cases"]
                if (not args.kind or r["kind"] == args.kind)
                and (
                    not args.rust_only
                    or r.get("sdcc", {}).get("status") == "unsupported"
                )
            ],
        }
        run["summary"] = summarize(run["cases"])
    if args.case:
        row = next((r for r in run["cases"] if r["id"] == args.case), None)
        if row is None:
            parser.error(f"unknown case: {args.case}")
        print(f"{row['id']}: {row['domain']}")
        print(row["c_function"])
        print(row["rust_function"])
        if row.get("cycles"):
            print(
                "\nT-cycles per input (entry through return, including helpers; outputs verified):"
            )
            for sample in row["cycles"]["samples"]:
                values = [
                    f"{name}={v['t_cycles']}"
                    if v.get("status") == "ok"
                    else f"{name}={v.get('status', 'unavailable')}"
                    for name, v in sample["compilers"].items()
                ]
                print(
                    f"  {sample['input']} -> {sample['expected']}: " + ", ".join(values)
                )
        if "analysis" in row:
            print("\n" + row["analysis"]["summary"])
            for note in row["analysis"]["notes"]:
                print(
                    f"  [{note['confidence']}] {note['category']}: {note['observation']}"
                )
                if note["evidence"]:
                    print("    " + json.dumps(note["evidence"]))
                if note.get("investigate"):
                    print("    Investigate: " + note["investigate"])
        for metric, reference in row["reference"].items():
            if reference["status"] == "ok":
                delta = reference["sangoku_delta"]
                gap = f"{delta:+} B" if delta is not None else "unavailable"
                print(
                    f"\nBest observed {metric}: {'/'.join(reference['compilers'])}, {reference['bytes']} B; Sangoku gap {gap}"
                )
        for compiler in ["sangoku", "sdcc", "llvm_z80"]:
            result = row.get(compiler, {"status": "not_run"})
            print(
                f"\n{compiler}: {result['status']}, {result.get('function_bytes', '?')} function bytes"
            )
            print(result.get("assembly", result.get("diagnostic", "")))
            if result.get("method"):
                print("Method: " + result["method"])
            if result.get("fixture_helpers"):
                print(
                    f"Fixture helpers: {result['fixture_helper_bytes']} bytes; caller + helpers: {result['function_with_fixture_helpers_bytes']} bytes"
                )
                for name, helper in result["fixture_helpers"].items():
                    print(f"  {name}: {helper['function_bytes']} bytes")
                    if args.dependencies:
                        print(helper["assembly"])
            library = result.get("library", {})
            if library:
                print(
                    f"Dependencies: {library['status']}; {library.get('dependency_bytes', '?')} bytes; total {library.get('total_bytes', '?')} bytes"
                )
                if library.get("diagnostic"):
                    print(library["diagnostic"])
                for item in library.get("sections", []):
                    print(f"  {item['name']}: {item['bytes']} bytes")
                    if args.dependencies and item.get("assembly"):
                        print(item["assembly"])
                for item in library.get("modules", []):
                    print(f"  {item['member']}: {item['code_bytes']} bytes")
                    if args.dependencies and item.get("assembly"):
                        print(item["assembly"])
        return
    summary = run["summary"]
    print(f"{args.mode}: {summary['cases']} cases; {summary['statuses']}")
    print(f"Compiler results: {summary['compiler_statuses']}")
    print(f"Smaller function bodies: {summary['smaller_function_counts']}")
    print(
        "\nBest observed references (external helpers excluded from body; native ABIs):"
    )
    print(
        f"{'case':<32} {'sangoku':>8} {'sdcc':>8} {'llvm-z80':>9} {'best':>8} {'reference':<18} {'S gap':>8}"
    )

    def gap(row):
        return row["reference"]["body"].get("sangoku_delta")

    for row in sorted(
        run["cases"], key=lambda row: (gap(row) is None, -(gap(row) or 0), row["id"])
    ):
        ref = row["reference"]["body"]
        values = [
            body_bytes(row.get(name, {})) for name in ("sangoku", "sdcc", "llvm_z80")
        ]
        values = [str(v) if v is not None else "n/a" for v in values]
        delta = f"{gap(row):+}" if gap(row) is not None else "n/a"
        print(
            f"{row['id']:<32} {values[0]:>8} {values[1]:>8} {values[2]:>9} {ref.get('bytes', 'n/a'):>8} {'/'.join(ref.get('compilers', [])) or 'n/a':<18} {delta:>8}"
        )
    print(
        "\nComplete reference costs (body + transitive dependencies; archive members may include other routines):"
    )
    print(
        f"{'case':<32} {'sangoku':>8} {'sdcc':>8} {'llvm-z80':>9} {'best':>8} {'reference':<18}"
    )
    for row in run["cases"]:
        ref = row["reference"]["with_dependencies"]
        if ref["status"] != "ok":
            continue
        values = [
            dependency_bytes(row.get(name, {}))
            for name in ("sangoku", "sdcc", "llvm_z80")
        ]
        values = [str(v) if v is not None else "n/a" for v in values]
        print(
            f"{row['id']:<32} {values[0]:>8} {values[1]:>8} {values[2]:>9} {ref['bytes']:>8} {'/'.join(ref['compilers']):<18}"
        )
    print("\nLargest function byte gaps (external runtime bodies excluded):")
    print(f"{'case':<18} {'sangoku':>8} {'sdcc':>8} {'delta':>8} {'helpers':>8}")
    for row in summary["largest_byte_gaps"]:
        print(
            f"{row['id']:<18} {row['sangoku_bytes']:>8} {row['sdcc_bytes']:>8} {row['bytes_delta']:>+8} {str(row['helper_dependent']):>8}"
        )
    with_deps = [r for r in run["cases"] if "with_dependencies" in r["comparison"]]
    if with_deps:
        print("\nFunction + reachable dependencies (startup and test entry excluded):")
        print(f"{'case':<24} {'sangoku':>8} {'sdcc':>8} {'delta':>8}")
        for row in with_deps:
            dep = row["comparison"]["with_dependencies"]
            print(
                f"{row['id']:<24} {dep['sangoku_bytes']:>8} {dep['sdcc_bytes']:>8} {dep['bytes_delta']:>+8}"
            )
    call_rows = [r for r in run["cases"] if r["kind"] == "call"]
    if call_rows:
        print(
            "\nCall fixtures: body bytes / leading add-sp reservation / adjacent stack loads+stores"
        )
        print(
            f"{'case':<28} {'S bytes':>8} {'C bytes':>8} {'S reserve':>10} {'C reserve':>10} {'S access':>9} {'C access':>9}"
        )
        for row in call_rows:
            values = []
            for compiler in ["sangoku", "sdcc"]:
                result = row[compiler]
                stack = result.get("stack", {})
                values.append(
                    (
                        result.get("function_bytes", "?"),
                        stack.get("entry_add_sp_reservation_bytes", "?"),
                        stack.get("adjacent_stack_load_count", 0)
                        + stack.get("adjacent_stack_store_count", 0),
                    )
                )
            print(
                f"{row['id']:<28} {values[0][0]:>8} {values[1][0]:>8} {values[0][1]:>10} {values[1][1]:>10} {values[0][2]:>9} {values[1][2]:>9}"
            )
        print(
            "Reservation excludes pushes and alternate frame setup; accesses are lower bounds, not a spill count or peak stack depth."
        )


if __name__ == "__main__":
    raise SystemExit(main())
