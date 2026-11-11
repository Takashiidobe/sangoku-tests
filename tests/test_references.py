import importlib
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
references = importlib.import_module("references")
llvm_z80 = importlib.import_module("llvm_z80")


def result(body, total=None):
    data = {"status": "ok", "function_bytes": body}
    if total is not None:
        data["library"] = {"status": "ok", "total_bytes": total}
    return data


class ReferenceTests(unittest.TestCase):
    def test_body_and_complete_cost_can_choose_different_compilers(self):
        row = {
            "sangoku": result(1103),
            "sdcc": result(6, 237),
            "llvm_z80": result(53, 53),
        }
        references.annotate_references([row])
        self.assertEqual(row["reference"]["body"]["compilers"], ["sdcc"])
        complete = row["reference"]["with_dependencies"]
        self.assertEqual(complete["compilers"], ["llvm_z80"])
        self.assertEqual(complete["bytes"], 53)
        self.assertIsNone(complete["sangoku_delta"])

    def test_incomplete_helpers_never_beat_a_complete_reference(self):
        row = {"sdcc": result(6, 237), "llvm_z80": result(4)}
        row["llvm_z80"]["library"] = {"status": "partial", "total_bytes": 4}
        ref = references.choose_reference(row, "with_dependencies")
        self.assertEqual(ref["compilers"], ["sdcc"])
        self.assertIn("llvm_z80", ref["excluded"])

    def test_ties_outlined_code_and_unavailable_results(self):
        row = {"sangoku": result(12), "sdcc": result(9), "llvm_z80": result(7)}
        row["llvm_z80"]["outlined_helper_bytes"] = 2
        ref = references.choose_reference(row, "body")
        self.assertEqual(ref["compilers"], ["sdcc", "llvm_z80"])
        self.assertEqual(ref["sangoku_delta"], 3)
        self.assertEqual(
            references.choose_reference({}, "body")["status"], "unavailable"
        )
        row["llvm_z80"] = {"status": "unsupported", "diagnostic": "width"}
        self.assertEqual(
            references.choose_reference(row, "body")["candidates"], {"sdcc": 9}
        )


class LlvmTests(unittest.TestCase):
    def test_retarget_removes_host_abi_and_machine_attributes(self):
        text = """target triple = "x86_64-unknown-linux-gnu"
target datalayout = "host-layout"
define i8 @probe(i8 zeroext %a) #0 { ret i8 %a }
attributes #0 = { uwtable nonlazybind "target-cpu"="x86-64" "probe-stack"="inline-asm" }
"""
        ir = llvm_z80.retarget(text)
        self.assertIn('target triple = "sm83-nintendo-none-elf"', ir)
        for host in ["x86-64", "host-layout", "zeroext", "uwtable", "probe-stack"]:
            self.assertNotIn(host, ir)
        self.assertIn('"target-features"="+inline-i16-runtime"', ir)

    def test_runtime_archive_dependencies_are_transitive_and_counted_once(self):
        compiler = object.__new__(llvm_z80.LlvmZ80)
        compiler.archive = Path("runtime.a")
        compiler.exports = {"div": "div.o", "common": "common.o"}
        compiler.modules = {
            "div.o": {"code_bytes": 20, "references": ["common"]},
            "common.o": {"code_bytes": 5, "references": []},
        }
        resolved = compiler.dependencies(["div", "common", "div"], 6)
        self.assertEqual(resolved["total_bytes"], 31)
        partial = compiler.dependencies(["missing"], 6)
        self.assertEqual(partial["status"], "partial")
        self.assertNotIn("total_bytes", partial)

    def test_unsupported_cases_do_not_invoke_the_frontend(self):
        compiler = object.__new__(llvm_z80.LlvmZ80)
        compiler.logs = []
        cases = [
            {"id": "pointer", "kind": "pattern", "width": 16, "result_width": 16},
            {"id": "wide", "kind": "integer", "width": 128, "result_width": 128},
        ]
        with tempfile.TemporaryDirectory() as temporary:
            with patch.object(
                compiler, "execute", side_effect=AssertionError("compiled")
            ):
                records, logs = compiler.compile_group(cases, "size", Path(temporary))
        self.assertEqual({r["status"] for r in records.values()}, {"unsupported"})
        self.assertEqual(logs, [])


if __name__ == "__main__":
    unittest.main()
