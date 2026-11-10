import importlib
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
compare = importlib.import_module("compare")
semantics = importlib.import_module("check_semantics")
analysis = importlib.import_module("analyze")
libraries = importlib.import_module("libraries")
sm83 = importlib.import_module("sm83")


class HarnessTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("rgbasm"), "requires RGBDS")
    def test_rust_sizes_include_raw_bytes_and_relocations(self):
        with tempfile.TemporaryDirectory() as temp:
            work = Path(temp)
            source = work / "probe.asm"
            source.write_text(
                'SECTION "a", ROM0\n__rust_a::\n ld a, b\n db $00, $00\n call external_helper\n ret\nSECTION "b", ROM0\n__rust_b::\n ld hl, $1234\n ret\n'
            )
            result = compare.measure_rust(source, [{"id": "a"}, {"id": "b"}], work)
            self.assertEqual(result["a"]["function_bytes"], 7)
            self.assertEqual(result["b"]["function_bytes"], 4)
            self.assertEqual(result["a"]["inline_machine_code_bytes"], 2)
            self.assertEqual(result["a"]["source_instruction_count"], 3)
            self.assertEqual(
                result["a"]["external_transfers"],
                [{"kind": "call", "target": "external_helper"}],
            )

    @unittest.skipUnless(shutil.which("rgbasm"), "requires RGBDS")
    def test_invalid_rust_assembly_fails_measurement(self):
        with tempfile.TemporaryDirectory() as temp:
            work = Path(temp)
            source = work / "probe.asm"
            source.write_text('SECTION "a", ROM0\n__rust_a::\n invalid_instruction\n')
            with self.assertRaisesRegex(ValueError, "assembly failed"):
                compare.measure_rust(source, [{"id": "a"}], work)

    @unittest.skipUnless(shutil.which("sdcc"), "requires SDCC")
    def test_sdcc_object_symbol_measurement(self):
        with tempfile.TemporaryDirectory() as temp:
            work = Path(temp)
            source = work / "probe.c"
            source.write_text(
                "unsigned char a(unsigned char x, unsigned char y) { return x+y; }\nunsigned char b(unsigned char x) { return x; }\n"
            )
            subprocess.run(
                ["sdcc", "-msm83", "-c", str(source), "-o", str(work / "probe.rel")],
                check=True,
                capture_output=True,
            )
            result = compare.measure_sdcc(
                work / "probe.asm", work / "probe.rel", [{"id": "a"}, {"id": "b"}]
            )
            self.assertEqual(result["a"]["function_bytes"], 2)
            self.assertEqual(result["b"]["function_bytes"], 1)
            self.assertEqual(result["a"]["source_instruction_count"], 2)
            self.assertNotIn("; Function", result["a"]["assembly"])

    @unittest.skipUnless(shutil.which("sdcc"), "requires SDCC")
    def test_sdcc_width_warning_is_unsupported(self):
        with tempfile.TemporaryDirectory() as temp:
            work = Path(temp)
            source = work / "probe.c"
            source.write_text(
                '_Static_assert(sizeof(double) == 8, "required width");\n\ndouble a(double x) { return x; }\n'
            )
            case = {"id": "a", "c_source": str(source)}
            args = SimpleNamespace(sdcc="sdcc", timeout=10)
            results, logs = compare.compile_group(
                "sdcc", [case], "size", args, work / "out"
            )
            self.assertEqual(results["a"]["status"], "unsupported")
            self.assertIn("required width", results["a"]["diagnostic"])
            self.assertEqual(len(logs), 1)

    @unittest.skipUnless(shutil.which("sdcc"), "requires SDCC")
    def test_codegen_error_is_preserved_after_isolation(self):
        with tempfile.TemporaryDirectory() as temp:
            work = Path(temp)
            source = work / "probe.c"
            source.write_text(
                "#include <stdint.h>\n\nuint8_t a(void) { syntax error }\n"
            )
            case = {
                "id": "a",
                "c_source": str(source),
                "c_function": "uint8_t a(void) { syntax error }",
            }
            args = SimpleNamespace(sdcc="sdcc", timeout=10)
            results, logs = compare.compile_group(
                "sdcc", [case], "size", args, work / "out"
            )
            self.assertEqual(results["a"]["status"], "error")
            self.assertTrue(results["a"]["diagnostic"])
            self.assertEqual(len(logs), 3)

    def test_missing_comparison_is_not_zero_bytes(self):
        result = compare.compare_case(
            {}, {"status": "ok", "function_bytes": 20}, {"status": "unsupported"}
        )
        self.assertEqual(result, {"status": "pattern_only"})
        result = compare.compare_case({}, {"status": "error"}, {"status": "ok"})
        self.assertEqual(result, {"status": "unavailable"})

    def test_vectors_exclude_undefined_signed_division(self):
        case = {
            "width": 8,
            "signed": True,
            "operation": "div",
            "rust_function": "fn div(a: i8, b: i8)",
        }
        pairs = list(semantics.vectors(case))
        self.assertTrue(pairs)
        self.assertTrue(all(b != 0 for _, b in pairs))
        self.assertNotIn((128, 255), pairs)
        self.assertIn((128, 1), pairs)
        self.assertIn((255, 255), pairs)

    def test_move_analysis_respects_incoming_block_edges(self):
        result = analysis.move_evidence("ld h, a\nld a, h\nld b, b\n")
        self.assertEqual(len(result["immediate_reloads"]), 1)
        self.assertEqual(len(result["identity_moves"]), 1)
        result = analysis.move_evidence("ld h, a\n.block2:\nld a, h\n")
        self.assertEqual(result["immediate_reloads"], [])

    def test_rel_sizes_do_not_double_count_aliases_or_ram(self):
        result = libraries.parse_rel(
            "XL4\nS _dep Ref00000000\nA _CODE size 10 flags 0 addr 0\nS _a Def00000000\nS _alias Def00000000\nA _DATA size 20 flags 0 addr 0\nA _INITIALIZER size 2 flags 0 addr 0\n"
        )
        self.assertEqual(result["code_bytes"], 18)
        self.assertEqual(result["definitions"], ["_a", "_alias"])
        self.assertEqual(result["references"], ["_dep"])

    def test_rust_map_excludes_non_rom_sections(self):
        text = 'ROM0 bank #0:\n SECTION: $0100-$014f ($0050 bytes) ["header"]\nROMX bank #1:\n SECTION: $4000-$4000 ($0001 byte) ["code"]\nWRAM0 bank #0:\n SECTION: $c000-$c003 ($0004 bytes) ["data"]\n'
        self.assertEqual(
            libraries.rust_map_sections(text),
            [{"name": "header", "bytes": 80}, {"name": "code", "bytes": 1}],
        )

    def test_analysis_exposes_dependency_ranking_reversal(self):
        def result(size, dependency):
            return {
                "status": "ok",
                "function_bytes": size,
                "assembly": "ret\n",
                **compare.asm_metrics("ret\n"),
                "library": {
                    "status": "ok",
                    "total_bytes": size + dependency,
                    "dependency_bytes": dependency,
                },
            }

        row = {
            "id": "strings_memmove",
            "kind": "string",
            "operation": "memmove",
            "type": "strings",
            "width": 8,
            "signed": None,
            "semantic_note": "overlap allowed",
            "style": "library",
            "sangoku": result(51, 56),
            "sdcc": result(24, 221),
        }
        row["comparison"] = compare.compare_case(row, row["sangoku"], row["sdcc"])
        analysis.annotate([row])
        self.assertEqual(row["comparison"]["smaller"], "sdcc")
        self.assertEqual(row["comparison"]["with_dependencies"]["smaller"], "sangoku")
        self.assertTrue(
            any("reverses" in n["observation"] for n in row["analysis"]["notes"])
        )

    @unittest.skipUnless(shutil.which("sdcc") and shutil.which("sdar"), "requires SDCC")
    def test_archive_closure_matches_actual_memmove_link(self):
        with tempfile.TemporaryDirectory() as temp:
            work = Path(temp)
            archive = libraries.SdccLibrary("sdcc", work / "archive")
            estimate = archive.resolve(["_memmove"])
            self.assertEqual(estimate["status"], "ok")
            self.assertGreaterEqual(len(estimate["modules"]), 2)
            case = {
                "c_function": "uint8_t *probe(uint8_t *d, const uint8_t *s, uint16_t n) { return memmove(d, s, n); }"
            }
            result, _ = libraries.measure_sdcc_link(
                case,
                "size",
                SimpleNamespace(sdcc="sdcc", timeout=10),
                work / "linked",
                estimate,
                compare.run,
            )
            self.assertEqual(result["status"], "ok")
            self.assertTrue(result["archive_estimate_verified"])
            self.assertTrue(all(module.get("assembly") for module in result["modules"]))
            self.assertEqual(
                result["total_bytes"],
                result["root_function_bytes"] + estimate["dependency_bytes"],
            )

    @unittest.skipUnless(
        shutil.which("rgbasm") and shutil.which("rgblink"), "requires RGBDS"
    )
    def test_disassembly_roundtrips_all_base_and_cb_opcodes(self):
        origin = 0x200
        expected = bytearray()
        source = ['SECTION "roundtrip", ROM0[$200]']
        for prefix, code in [(False, code) for code in range(256)] + [
            (True, code) for code in range(256)
        ]:
            data = (
                bytes([0xCB, code])
                if prefix
                else bytes([code, 0 if code == 0x10 else 0x42, 0x13])
            )
            size, text = sm83.decode(data, 0, origin + len(expected))
            source.append(text)
            expected.extend(data[:size])
        with tempfile.TemporaryDirectory() as temp:
            work = Path(temp)
            (work / "input.asm").write_text("\n".join(source))
            outcome = compare.run(
                ["rgbasm", "-o", work / "input.o", work / "input.asm"]
            )
            self.assertEqual(outcome["returncode"], 0, outcome["stderr"])
            outcome = compare.run(
                ["rgblink", "-x", "-o", work / "input.gb", work / "input.o"]
            )
            self.assertEqual(outcome["returncode"], 0, outcome["stderr"])
            self.assertEqual((work / "input.gb").read_bytes()[origin:], expected)

    def test_hex_checksum_and_truncated_disassembly(self):
        memory = sm83.read_ihx(":040200002134122A69\n:00000001FF\n")
        self.assertEqual(
            bytes(memory[i] for i in range(0x200, 0x204)), bytes.fromhex("2134122a")
        )
        with self.assertRaisesRegex(ValueError, "checksum"):
            sm83.read_ihx(":040200002134122A68\n")
        self.assertEqual(
            sm83.disassemble(bytes([0x21]), 0x200)[0]["instruction"], "db $21"
        )

    def test_case_selection_is_exact_and_rejects_empty_intersections(self):
        cases = [
            {"id": "u8_add", "type": "u8"},
            {"id": "u8_add1", "type": "u8"},
            {"id": "i16_add", "type": "i16"},
        ]
        self.assertEqual(compare.select_cases(cases, case_ids=["u8_add"]), cases[:1])
        self.assertEqual(compare.select_cases(cases, types=["i16"]), cases[2:])
        with self.assertRaisesRegex(ValueError, "unknown cases"):
            compare.select_cases(cases, case_ids=["u8_ad"])
        with self.assertRaisesRegex(ValueError, "no cases match"):
            compare.select_cases(cases, types=["i16"], case_ids=["u8_add"])

    @unittest.skipUnless(shutil.which("sdcc"), "requires SDCC")
    def test_single_case_compiles_only_selected_source(self):
        with tempfile.TemporaryDirectory() as temp:
            work = Path(temp)
            source = work / "group.c"
            function = "unsigned char a(unsigned char x) { return x; }"
            source.write_text(
                "#include <stdint.h>\n\n"
                + function
                + "\nunsigned char unwanted(void) { return 42; }\n"
            )
            case = {"id": "a", "c_source": str(source), "c_function": function}
            args = SimpleNamespace(sdcc="sdcc", timeout=10, case=["a"])
            result, _ = compare.compile_group(
                "sdcc", [case], "size", args, work / "out"
            )
            self.assertEqual(result["a"]["status"], "ok")
            selected = (work / "out/selected.c").read_text()
            self.assertIn(function, selected)
            self.assertNotIn("unwanted", selected)
            self.assertNotIn("_unwanted", (work / "out/output.asm").read_text())

    def test_stack_patterns_report_storage_without_claiming_spills(self):
        result = compare.asm_metrics(
            "push bc\nadd sp, -8\n.block0:\nld hl, sp + 2\nld [hl], a\nldhl sp, #12\nld a, (hl)\ncall helper\nadd sp, 8\npop bc\nret\n"
        )["stack"]
        self.assertEqual(result["entry_add_sp_reservation_bytes"], 8)
        self.assertEqual(result["adjacent_stack_load_count"], 1)
        self.assertEqual(result["adjacent_stack_store_count"], 1)
        self.assertNotIn("spill_count", result)
        self.assertNotIn("peak_stack_depth", result)
        large = compare.asm_metrics(
            "add sp, -128\nadd sp, -128\nadd sp, -35\nld a, b\n"
        )["stack"]
        self.assertEqual(large["entry_add_sp_reservation_bytes"], 291)

    @unittest.skipUnless(shutil.which("sdcc"), "requires SDCC")
    def test_selected_call_keeps_and_measures_required_callee(self):
        with tempfile.TemporaryDirectory() as temp:
            work = Path(temp)
            source = work / "calls.c"
            helper = {
                "id": "helper",
                "c_function": "uint8_t helper(uint8_t a) { return a ^ 1; }",
            }
            function = "uint8_t caller(uint8_t a) { return helper(a); }"
            source.write_text(
                "#include <stdint.h>\n\n" + helper["c_function"] + "\n\n" + function
            )
            case = {
                "id": "caller",
                "kind": "call",
                "operation": "tail",
                "expected_fixture_calls": 1,
                "c_source": str(source),
                "c_function": function,
                "support_functions": [helper],
            }
            args = SimpleNamespace(sdcc="sdcc", timeout=10, case=["caller"])
            result, _ = compare.compile_group(
                "sdcc", [case], "size", args, work / "out"
            )
            self.assertEqual(result["caller"]["status"], "ok")
            self.assertIn("helper", result["caller"]["fixture_helpers"])
            self.assertGreater(
                result["caller"]["function_with_fixture_helpers_bytes"],
                result["caller"]["function_bytes"],
            )
            case["c_function"] = "uint8_t caller(uint8_t a) { return a; }"
            result, _ = compare.compile_group(
                "sdcc", [case], "size", args, work / "removed"
            )
            self.assertEqual(result["caller"]["status"], "error")
            self.assertIn(
                "expected 1 fixture calls/tail transfers, found 0",
                result["caller"]["diagnostic"],
            )


if __name__ == "__main__":
    unittest.main()
