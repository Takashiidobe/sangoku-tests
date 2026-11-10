import importlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
compare = importlib.import_module("compare")
readme = importlib.import_module("update_readme")
libraries = importlib.import_module("libraries")


class PatternFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = json.loads((ROOT / "cases/manifest.json").read_text())

    def test_every_requested_pattern_family_has_concrete_pairs(self):
        patterns = [c for c in self.cases if c["kind"] == "pattern"]
        self.assertEqual(
            {c["pattern_family"] for c in patterns},
            {
                "formatting",
                "parsing",
                "ctype",
                "spans",
                "substring",
                "concat",
                "aggregates",
                "slices",
                "search_sort",
                "packing_checksum",
                "dispatch",
            },
        )
        for case in patterns:
            self.assertIn(case["id"] + "(", case["c_function"])
            self.assertIn(case["id"] + "(", case["rust_function"])
            self.assertEqual(readme.description(case), case["description"])
        ids = {c["id"] for c in patterns}
        for size in [3, 5, 8, 12]:
            self.assertIn(f"aggregate_copy{size}_assign", ids)
            self.assertIn(f"aggregate_return{size}_value", ids)
            self.assertIn(f"aggregate_out{size}_call", ids)
        self.assertIn("spans_tokenize_loop", ids)
        self.assertIn("spans_strtok_library", ids)

    def test_memory_thresholds_and_offset_controls_are_present(self):
        strings = [c for c in self.cases if c["kind"] == "string"]
        expected = {0, 1, 2, 3, 4, 7, 8, 15, 16, 17, 31, 32, 63, 64, 127, 128}
        for operation in ["memcpy", "memmove", "memset", "memcmp"]:
            self.assertEqual(
                {
                    c["fixed_length"]
                    for c in strings
                    if c["base_operation"] == operation
                    and c["fixed_length"] is not None
                },
                expected,
            )
        self.assertEqual(
            {c["pointer_offset"] for c in strings if c["pointer_offset"]}, {1, 3, 7}
        )

    def test_c_only_comparators_are_not_charged_to_rust(self):
        case = next(c for c in self.cases if c["id"] == "search_bsearch_library")
        self.assertEqual(compare.support_functions([case], "sangoku"), [])
        self.assertEqual(len(compare.support_functions([case], "sdcc")), 1)
        generated = compare.selected_source(
            ROOT / case["rust_source"], [case], "sangoku"
        )
        self.assertNotIn("fn fixture_cmp_words(", generated)
        self.assertIn("binary_search", generated)

    @unittest.skipUnless(shutil.which("sdcc"), "requires SDCC")
    def test_capability_probe_preserves_diagnostics_without_compiling_body(self):
        with tempfile.TemporaryDirectory() as temp:
            work = Path(temp)
            source = work / "feature.c"
            function = "unsigned char feature(void) { return 0; }"
            source.write_text("#include <stdint.h>\n\n" + function)
            case = {
                "id": "feature",
                "kind": "pattern",
                "c_source": str(source),
                "c_function": function,
                "c_capability_source": "#error aggregate_feature_unavailable\n",
            }
            result, logs = compare.compile_group(
                "sdcc",
                [case],
                "size",
                SimpleNamespace(sdcc="sdcc", timeout=10),
                work / "out",
            )
            self.assertEqual(result["feature"]["status"], "unsupported")
            self.assertIn(
                "aggregate_feature_unavailable", result["feature"]["diagnostic"]
            )
            self.assertEqual(len(logs), 1)

    def test_helper_disassembly_includes_home_and_excludes_ram(self):
        with tempfile.TemporaryDirectory() as temp:
            work = Path(temp)
            rel = work / "mixed.rel"
            rel.write_text(
                "XL4\nA _CODE size 2 flags 0 addr 0\nS _code Def00000000\nA _HOME size 3 flags 0 addr 0\nS _home Def00000000\nA _DATA size 2 flags 0 addr 0\nS _errno Def00000000\n"
            )
            ram = work / "ram.rel"
            ram.write_text(
                "XL4\nA _CODE size 0 flags 0 addr 0\nA _DATA size 2 flags 0 addr 0\nS _errno Def00000000\n"
            )
            modules = [
                {
                    **libraries.parse_rel(path.read_text()),
                    "member": path.name,
                    "object_path": str(path),
                }
                for path in [rel, ram]
            ]
            mapping = "  00000200 _code\n  00000800 _home\n  0000c000 _errno\n"
            memory = {0x200: 0xAF, 0x201: 0xC9, 0x800: 0x3E, 0x801: 1, 0x802: 0xC9}
            decoded = libraries.disassemble_sdcc_modules(modules, mapping, memory)
            self.assertEqual(
                {area["area"] for area in decoded[0]["disassembly_areas"]},
                {"_CODE", "_HOME"},
            )
            self.assertEqual(decoded[0]["code_bytes"], 5)
            self.assertIn("ld a, $01", decoded[0]["assembly"])
            self.assertFalse(decoded[0]["unresolved_rom_areas"])
            self.assertTrue(decoded[1]["data_only"])
            self.assertEqual(decoded[1]["code_bytes"], 0)
            self.assertNotIn("assembly", decoded[1])


if __name__ == "__main__":
    unittest.main()
