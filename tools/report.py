#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from compare import summarize

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


def print_baseline(previous, report, modes, args):
    def cases(data, mode):
        return {
            row["id"]: row
            for row in data["runs"].get(mode, {}).get("cases", [])
            if (not args.case or row["id"] == args.case)
            and (not args.kind or row["kind"] == args.kind)
        }

    failed = False
    compared = 0
    for mode in modes:
        before, after = cases(previous, mode), cases(report, mode)
        changes = []
        coverage = []
        losses = 0
        unchanged = 0
        for name in sorted(before.keys() | after.keys()):
            if name not in before:
                coverage.append(f"{name}: new case")
                continue
            if name not in after:
                coverage.append(f"{name}: missing from candidate")
                losses += 1
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
        for message in coverage:
            print(f"  {message}")
        if args.max_growth is not None:
            over = sum(delta > args.max_growth for delta, *_ in changes)
            if over or losses:
                print(
                    f"  Budget exceeded: {over} measurements over +{args.max_growth} B, {losses} lost cases or measurements"
                )
                failed = True
    if not compared:
        print("No comparable successful Sangoku cases.")
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
        "--baseline", type=Path, help="Compare Sangoku codegen with an earlier report"
    )
    parser.add_argument(
        "--max-growth",
        type=int,
        metavar="BYTES",
        help="With --baseline, fail if any measured case grows by more than BYTES or loses a result",
    )
    args = parser.parse_args()
    report = json.loads(args.report.read_text())
    if args.max_growth is not None and (not args.baseline or args.max_growth < 0):
        parser.error("--max-growth requires --baseline and a nonnegative byte budget")
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
    run = report["runs"][args.mode]
    if args.kind:
        run = {**run, "cases": [r for r in run["cases"] if r["kind"] == args.kind]}
        run["summary"] = summarize(run["cases"])
    if args.case:
        row = next((r for r in run["cases"] if r["id"] == args.case), None)
        if row is None:
            parser.error(f"unknown case: {args.case}")
        print(f"{row['id']}: {row['domain']}")
        print(row["c_function"])
        print(row["rust_function"])
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
        for compiler in ["sangoku", "sdcc"]:
            result = row[compiler]
            print(
                f"\n{compiler}: {result['status']}, {result.get('function_bytes', '?')} function bytes"
            )
            print(result.get("assembly", result.get("diagnostic", "")))
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
    print(f"Smaller function bodies: {summary['smaller_function_counts']}")
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
