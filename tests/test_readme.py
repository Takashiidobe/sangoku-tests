import copy
from collections import Counter
import importlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
readme = importlib.import_module("update_readme")


class ReadmeCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads((ROOT / "results/comparison.json").read_text())
        cls.rows = {r["id"]: r for r in cls.report["runs"]["size"]["cases"]}

    def test_each_case_is_listed_once_and_source_links_match_functions(self):
        text = readme.render_catalog(self.report)
        matches = re.findall(r"\[`([^`]+)`\]\((cases/[^#)]+)#L(\d+)\)", text)
        self.assertEqual(
            Counter(name for name, _, _ in matches),
            Counter({name: 1 for name in self.rows}),
        )
        sources = {}
        for name, path, line in matches:
            if path not in sources:
                sources[path] = (ROOT / path).read_text().splitlines()
            self.assertIn("fn " + name + "(", sources[path][int(line) - 1])
        self.assertEqual(text.count("<details>"), text.count("</details>"))

    def test_unsupported_c_width_has_no_fictitious_zero_baseline(self):
        row = self.rows["u128_as_unsigned"]
        self.assertIn(
            f"/ {row['llvm_z80']['function_bytes']} B", readme.body_sizes(row)
        )
        self.assertNotIn("n/a", readme.body_sizes(row))
        symptom = readme.symptoms(row, self.rows)
        self.assertNotIn("C unavailable", symptom)
        self.assertNotRegex(symptom, r"SP references \d[\d,]*/0")
        unavailable = self.rows["f128_add"]
        self.assertIn("/ n/a", readme.body_sizes(unavailable))
        self.assertIn(
            "instruction legalization failed", readme.case_notes(unavailable, self.rows)
        )

    def test_catalog_uses_three_columns_and_anonymous_best_measurements(self):
        text = readme.render_catalog(self.report)
        self.assertIn("| Case (Rust source) | Sangoku vs best | Notes |", text)
        for obsolete in [
            "Exercises",
            "LLVM-Z80 body",
            "Outward symptoms",
            "First investigation lead",
            "llvm_z80",
            "SDCC",
            "C unavailable",
        ]:
            self.assertNotIn(obsolete, text)
        row = next(
            line
            for line in text.splitlines()
            if line.startswith("| [`aggregate_return8_value`]")
        )
        self.assertIn("| 255 / 122 B (+133) |", row)
        self.assertIn("Speed: 255 / 126 B (+129)", row)
        self.assertEqual(row.count("|"), 4)

    def test_best_body_selection_tracks_either_reference_and_outlined_code(self):
        row = {
            "sangoku": {"status": "ok", "function_bytes": 15},
            "sdcc": {"status": "ok", "function_bytes": 9},
            "llvm_z80": {"status": "ok", "function_bytes": 7},
        }
        self.assertEqual(readme.body_sizes(row), "15 / 7 B (+8)")
        row["sdcc"]["function_bytes"] = 6
        self.assertEqual(readme.body_sizes(row), "15 / 6 B (+9)")
        row["sdcc"]["function_bytes"] = 9
        row["llvm_z80"]["outlined_helper_bytes"] = 3
        self.assertEqual(readme.body_sizes(row), "15 / 9 B (+6)")
        row["sangoku"]["function_bytes"] = 9
        self.assertEqual(readme.body_sizes(row), "9 / 9 B (tie)")

    def test_helper_reversal_and_negative_call_control_delta_survive_summary(self):
        row = copy.deepcopy(self.rows["strings_memmove"])
        for compiler, body, total in [
            ("sangoku", 20, 107),
            ("sdcc", 10, 245),
            ("llvm_z80", 10, 245),
        ]:
            row[compiler]["function_bytes"] = body
            row[compiler]["library"] = {"status": "ok", "total_bytes": total}
        text = readme.case_notes(row, self.rows)
        self.assertIn("With helpers: 107 / 245 B (-138)", text)
        self.assertIn("Body ranking reverses", text)
        row = copy.deepcopy(self.rows["calls_u8_live8"])
        row["comparison"]["call_control"]["sangoku"].update(
            {"caller_bytes_delta": -11, "entry_add_sp_reservation_delta": 2}
        )
        text = readme.symptoms(row, self.rows)
        self.assertIn("caller -11 B, reservation +2 B", text)
        self.assertNotIn("11 spill", text)

    def test_rust_only_summary_uses_measurements_and_preserves_failures(self):
        def row(name, sangoku, llvm):
            return {
                "id": name,
                "type": "u128",
                "sdcc": {"status": "unsupported"},
                "sangoku": sangoku,
                "llvm_z80": llvm,
            }

        def result(body, total=None):
            data = {"status": "ok", "function_bytes": body}
            if total is not None:
                data["library"] = {"status": "ok", "total_bytes": total}
            return data

        helper_win = row("helper", result(4), result(8, 8))
        helper_win["sangoku"]["external_transfers"] = [
            {"kind": "call", "target": "runtime"}
        ]
        paired = row("complete", result(12, 20), result(7, 11))
        failed = row(
            "failed",
            result(6),
            {
                "status": "error",
                "diagnostic": "warning: preliminary\nrustc-LLVM ERROR: unable to legalize instruction",
            },
        )
        unsupported = row("unsupported", result(2), {"status": "unsupported"})
        cases = [helper_win, paired, failed, unsupported]
        report = {
            "generated_at": "snapshot",
            "runs": {"size": {"cases": cases}, "speed": {"cases": [paired]}},
        }
        summary = readme.render_rust_only_summary(report)
        self.assertIn("| size | Total | 4 | 1 | 1 | 0 | 1 | 1 |", summary)
        self.assertIn("| speed | Total | 1 | 1 | 0 | 0 | 0 | 0 |", summary)
        self.assertIn("1 of 1 Sangoku body wins", summary)
        self.assertIn("| size | [`complete`](#u128) | 20 B | 11 B | +9 B |", summary)
        self.assertIn("| [`failed`](#u128) | error | not run |", summary)
        self.assertIn("unable to legalize instruction", summary)
        self.assertNotIn("warning: preliminary", summary)
        self.assertNotIn("[`helper`](#u128)", summary)
        detailed = readme.render_rust_only_report(report)
        self.assertIn(
            "| [`helper`](../README.md#u128) | 4 | 8 | -4 | n/a | 8 | yes |", detailed
        )
        self.assertIn("Every Rust-only probe, speed mode", detailed)

    @unittest.skipUnless(shutil.which("prettier"), "requires Prettier")
    def test_refresh_and_check_cover_both_generated_documents(self):
        with tempfile.TemporaryDirectory() as temp:
            work = Path(temp)
            document = work / "README.md"
            companion = work / "results/rust-only.md"
            document.write_text(
                "manual before\n\n"
                + readme.BEGIN
                + "\nstale\n"
                + readme.END
                + "\nmanual after\n"
            )
            command = [
                sys.executable,
                str(ROOT / "tools/update_readme.py"),
                "--readme",
                str(document),
            ]

            def run(*flags):
                return subprocess.run(
                    [*command, *flags], capture_output=True, text=True
                )

            stale = run("--check")
            self.assertEqual(stale.returncode, 1, stale.stderr)
            self.assertFalse(companion.exists())
            self.assertIn("stale", document.read_text())
            refreshed = run()
            self.assertEqual(refreshed.returncode, 0, refreshed.stderr)
            self.assertIn("Sangoku vs best", document.read_text())
            self.assertIn("Every Rust-only probe, speed mode", companion.read_text())
            self.assertTrue(document.read_text().endswith("manual after\n"))
            current = run("--check")
            self.assertEqual(current.returncode, 0, current.stdout + current.stderr)
            original = document.read_text()
            companion.write_text("stale companion\n")
            stale = run("--check")
            self.assertEqual(stale.returncode, 1, stale.stderr)
            self.assertIn(str(companion), stale.stdout)
            self.assertEqual(document.read_text(), original)
            self.assertEqual(companion.read_text(), "stale companion\n")

    def test_refresh_preserves_manual_content_and_rejects_bad_markers(self):
        source = (
            "manual before\n\n"
            + readme.BEGIN
            + "\nold\n"
            + readme.END
            + "\nmanual after\n"
        )
        updated = readme.replace_catalog(source, "new\n")
        self.assertTrue(updated.startswith("manual before\n\n"))
        self.assertTrue(updated.endswith("\nmanual after\n"))
        self.assertEqual(readme.replace_catalog(updated, "new\n"), updated)
        for malformed in [
            readme.BEGIN,
            readme.END,
            readme.END + readme.BEGIN,
            readme.BEGIN + readme.BEGIN + readme.END,
        ]:
            with self.assertRaises(ValueError):
                readme.replace_catalog(malformed, "new")

    def test_partial_report_cannot_erase_catalog(self):
        with tempfile.TemporaryDirectory() as temp:
            work = Path(temp)
            report = work / "partial.json"
            document = work / "README.md"
            report.write_text(
                json.dumps({"runs": {"size": {"cases": [self.rows["u8_add"]]}}})
            )
            document.write_text("preserve this README\n")
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools/update_readme.py"),
                    "--report",
                    str(report),
                    "--readme",
                    str(document),
                ],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("use a full report", result.stderr)
            self.assertEqual(document.read_text(), "preserve this README\n")


if __name__ == "__main__":
    unittest.main()
