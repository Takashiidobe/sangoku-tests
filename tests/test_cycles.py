import copy
import importlib
from pathlib import Path
import sys
import unittest
from typing import Any


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
runner = importlib.import_module("cycle_runner")
readme = importlib.import_module("update_readme")


@unittest.skipUnless(
    runner.DEFAULT_LIBRARY.is_file(), "requires the SameBoy shared library"
)
class EmulatorCycleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.emulator = runner.SameBoy()

    def rom(self, code, address=0x200):
        image = bytearray(0x8000)
        image[address : address + len(code)] = bytes.fromhex(code)
        return image

    def test_known_straight_line_cycles_and_result(self):
        result = self.emulator.run(
            self.rom("6b 62 29 19 4d 44 c9"), 0x200, registers={"de": 7}
        )
        self.assertEqual(result["t_cycles"], 48)
        self.assertEqual(result["registers"]["bc"], 21)

    def test_branch_inputs_take_different_paths(self):
        image = self.rom("78 b7 28 02 3c c9 af c9")
        zero = self.emulator.run(image, 0x200, registers={"bc": 0})
        one = self.emulator.run(image, 0x200, registers={"bc": 0x100})
        self.assertEqual(zero["t_cycles"], 40)
        self.assertEqual(one["t_cycles"], 36)

    def test_helpers_and_returns_are_included(self):
        image = self.rom("cd 10 02 c9")
        image[0x210:0x212] = bytes.fromhex("03 c9")
        result = self.emulator.run(image, 0x200, registers={"bc": 5})
        self.assertEqual(result["t_cycles"], 64)
        self.assertEqual(result["registers"]["bc"], 6)

    def test_wrapper_setup_and_result_stores_are_excluded(self):
        image = self.rom("01 07 00 cd 20 02 79 ea 80 c1 3e 01 ea a0 c1 c9")
        image[0x220:0x222] = bytes.fromhex("03 c9")
        result = self.emulator.run(
            image,
            0x200,
            measure=0x220,
            done=0xC1A0,
            output=(0xC180, 1),
            expected=b"\x08",
        )
        self.assertEqual(result["t_cycles"], 24)

    def test_bad_results_and_nontermination_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "result mismatch"):
            self.emulator.run(
                self.rom("3e 01 ea 80 c1 c9"),
                0x200,
                output=(0xC180, 1),
                expected=b"\x02",
            )
        with self.assertRaisesRegex(ValueError, "execution limit"):
            self.emulator.run(self.rom("18 fe"), 0x200, limit=10)


class CycleReadmeTests(unittest.TestCase):
    def test_readme_renders_exact_input_subrows_in_each_mode(self):
        import json

        report = json.loads((runner.ROOT / "results/comparison.json").read_text())
        case = next(r for r in report["runs"]["size"]["cases"] if r["id"] == "u16_mul3")
        speed = next(
            r for r in report["runs"]["speed"]["cases"] if r["id"] == "u16_mul3"
        )
        tiny = {
            "generated_at": "test",
            "runs": {"size": {"cases": [case]}, "speed": {"cases": [speed]}},
        }
        case["cycles"] = {
            "samples": [
                {
                    "input": "a=7",
                    "expected": 21,
                    "compilers": {
                        "sangoku": {"status": "ok", "t_cycles": 100},
                        "sdcc": {"status": "ok", "t_cycles": 56},
                        "llvm_z80": {"status": "ok", "t_cycles": 48},
                    },
                }
            ]
        }
        speed["cycles"] = copy.deepcopy(case["cycles"])
        speed["cycles"]["samples"][0]["compilers"]["sangoku"]["t_cycles"] = 80
        speed["cycles"]["samples"][0]["compilers"]["sdcc"]["t_cycles"] = 40
        text = readme.render_catalog(tiny)
        self.assertIn("↳ cycles (size): `a=7` → `21`", text)
        self.assertIn("100 / 48 T (+52)", text)
        self.assertIn("↳ cycles (speed): `a=7` → `21`", text)
        self.assertIn("80 / 40 T (+40)", text)
        self.assertNotIn("median", text.lower())

    def test_each_input_selects_its_fastest_verified_reference(self):
        sample: dict[str, Any] = {
            "input": "a=7",
            "compilers": {
                "sangoku": {"status": "ok", "t_cycles": 100},
                "sdcc": {"status": "ok", "t_cycles": 64},
                "llvm_z80": {"status": "ok", "t_cycles": 72},
            },
        }
        self.assertEqual(readme.cycle_sizes(sample), "100 / 64 T (+36)")
        other = copy.deepcopy(sample)
        other["compilers"]["llvm_z80"]["t_cycles"] = 48
        self.assertEqual(readme.cycle_sizes(other), "100 / 48 T (+52)")
        other["compilers"]["llvm_z80"] = {"status": "error", "t_cycles": 1}
        self.assertEqual(readme.cycle_sizes(other), "100 / 64 T (+36)")
        other["compilers"]["sdcc"] = {"status": "error"}
        self.assertEqual(readme.cycle_sizes(other), "100 / n/a T")


if __name__ == "__main__":
    unittest.main()
