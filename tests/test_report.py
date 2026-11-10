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


if __name__ == "__main__":
    unittest.main()
