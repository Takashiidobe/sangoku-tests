import copy
from collections import Counter
import importlib
import json
from pathlib import Path
import re
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
        self.assertIn("/ n/a", readme.body_sizes(row))
        self.assertIn("pattern only", readme.body_sizes(row))
        symptom = readme.symptoms(row, self.rows)
        self.assertIn("C unavailable", symptom)
        self.assertNotRegex(symptom, r"SP references \d[\d,]*/0")

    def test_helper_reversal_and_negative_call_control_delta_survive_summary(self):
        row = copy.deepcopy(self.rows["strings_memmove"])
        row["comparison"].update(
            {
                "smaller": "sdcc",
                "with_dependencies": {
                    "sangoku_bytes": 107,
                    "sdcc_bytes": 245,
                    "smaller": "sangoku",
                },
            }
        )
        text = readme.symptoms(row, self.rows)
        self.assertIn("with helpers 107/245 B", text)
        self.assertIn("body ranking reverses", text)
        row = copy.deepcopy(self.rows["calls_u8_live8"])
        row["comparison"]["call_control"]["sangoku"].update(
            {"caller_bytes_delta": -11, "entry_add_sp_reservation_delta": 2}
        )
        text = readme.symptoms(row, self.rows)
        self.assertIn("caller -11 B, reservation +2 B", text)
        self.assertNotIn("11 spill", text)

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
