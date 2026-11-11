import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def fixture(name, body, linked=None):
    result = {"status": "ok", "function_bytes": body}
    if linked is not None:
        result["library"] = {"status": "ok", "total_bytes": linked}
    return {"id": name, "rust_function": f"fn {name}() {{}}", "sangoku": result}


class BaselineReportTests(unittest.TestCase):
    def test_cycle_growth_is_per_input_and_separate_from_byte_growth(self):
        before = {"size": [fixture("probe", 10)]}
        before["size"][0]["cycles"] = {
            "samples": [
                {
                    "input": "a=0",
                    "args": [0],
                    "expected": 0,
                    "compilers": {"sangoku": {"status": "ok", "t_cycles": 100}},
                },
                {
                    "input": "a=1",
                    "args": [1],
                    "expected": 1,
                    "compilers": {"sangoku": {"status": "ok", "t_cycles": 200}},
                },
            ]
        }
        after = copy.deepcopy(before)
        after["size"][0]["sangoku"]["function_bytes"] = 9
        samples = after["size"][0]["cycles"]["samples"]
        samples[0]["compilers"]["sangoku"]["t_cycles"] = 104
        samples[1]["compilers"]["sangoku"]["t_cycles"] = 180
        byte_only = self.compare(before, after, "--max-growth", "0")
        self.assertEqual(byte_only.returncode, 0, byte_only.stderr)
        strict = self.compare(before, after, "--max-cycle-growth", "0")
        self.assertEqual(strict.returncode, 1, strict.stderr)
        self.assertRegex(strict.stdout, r"probe\s+a=0\s+100\s+104\s+\+4")
        self.assertRegex(strict.stdout, r"probe\s+a=1\s+200\s+180\s+-20")
        allowed = self.compare(before, after, "--max-cycle-growth", "4")
        self.assertEqual(allowed.returncode, 0, allowed.stderr)
        after["size"][0]["cycles"]["samples"] = []
        lost = self.compare(before, after, "--max-cycle-growth", "0")
        self.assertEqual(lost.returncode, 1, lost.stderr)
        self.assertIn("2 lost measurements", lost.stdout)

    def test_rust_only_filter_keeps_native_failures(self):
        report = json.loads((ROOT / "results/comparison.json").read_text())
        rows = [
            r
            for r in report["runs"]["size"]["cases"]
            if r["sdcc"]["status"] == "unsupported"
        ]
        result = subprocess.run(
            [sys.executable, ROOT / "tools/report.py", "--rust-only"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f"size: {len(rows)} cases", result.stdout)
        self.assertIn("f128_add", result.stdout)
        self.assertNotIn("u8_add", result.stdout)

    def compare(self, before, after, *flags):
        with tempfile.TemporaryDirectory() as temp:
            paths = [Path(temp) / f"{label}.json" for label in ("before", "after")]
            for path, modes in zip(paths, (before, after)):
                report = {
                    "target": "sm83",
                    "runs": {mode: {"cases": rows} for mode, rows in modes.items()},
                }
                path.write_text(json.dumps(report))
            return subprocess.run(
                [
                    sys.executable,
                    ROOT / "tools/report.py",
                    paths[1],
                    "--baseline",
                    paths[0],
                    *flags,
                ],
                capture_output=True,
                text=True,
            )

    def test_linked_growth_is_visible_despite_smaller_body_and_other_savings(self):
        before = {
            "size": [fixture("call", 20, 40)],
            "speed": [fixture("arithmetic", 32)],
        }
        after = {
            "size": [fixture("call", 19, 43)],
            "speed": [fixture("arithmetic", 10)],
        }
        strict = self.compare(before, after, "--max-growth", "2")
        self.assertEqual(strict.returncode, 1, strict.stderr)
        self.assertIn("size mode: 1 larger measurements, 1 smaller", strict.stdout)
        self.assertIn("speed mode: 0 larger measurements, 1 smaller", strict.stdout)
        self.assertRegex(strict.stdout, r"call\s+linked\s+40\s+43\s+\+3")
        tolerant = self.compare(before, after, "--max-growth", "3")
        self.assertEqual(tolerant.returncode, 0, tolerant.stdout + tolerant.stderr)

    def test_changed_helpers_are_skipped_and_lost_measurements_fail_budget(self):
        before = {
            "size": [
                fixture("edited", 8),
                fixture("broken", 3, 12),
                fixture("stable", 5),
            ]
        }
        before["size"][0]["support_functions"] = [
            {"id": "helper", "rust_function": "fn helper() { black_box(1); }"}
        ]
        after = copy.deepcopy(before)
        after["size"][0]["support_functions"][0]["rust_function"] = "fn helper() {}"
        after["size"][0]["sangoku"]["function_bytes"] = 100
        after["size"][1]["sangoku"]["library"] = {"status": "error"}
        result = self.compare(before, after, "--max-growth", "0")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("edited: Rust fixture changed", result.stdout)
        self.assertIn("broken: lost linked measurement", result.stdout)
        self.assertIn("0 measurements over +0 B", result.stdout)

    def test_progress_shows_distance_to_the_best_reference(self):
        before = {"size": [fixture("mul3", 15)]}
        before["size"][0].update(
            {
                "sdcc": {"status": "ok", "function_bytes": 9},
                "llvm_z80": {"status": "ok", "function_bytes": 7},
            }
        )
        after = copy.deepcopy(before)
        after["size"][0]["sangoku"]["function_bytes"] = 8
        result = self.compare(before, after)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("llvm_z80 7 B; gap 8 -> 1 B", result.stdout)
        after["size"][0]["llvm_z80"]["function_bytes"] = 6
        changed = self.compare(before, after)
        self.assertIn("body reference changed", changed.stdout)


if __name__ == "__main__":
    unittest.main()
