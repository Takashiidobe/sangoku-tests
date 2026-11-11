import importlib
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
native = importlib.import_module("rust_z80")


class NativeRustZ80Tests(unittest.TestCase):
    def test_sources_preserve_target_features_aggregate_layout_and_rust_helpers(self):
        helper = {"id": "leaf", "rust_function": "fn leaf() {}", "languages": ["rust"]}
        c_only = {"id": "c_only", "languages": ["c"]}
        cases = [
            {
                "rust_header": "#![no_std]\n#![feature(f16)]\n#[repr(C)] struct Pair { a: u16, b: u16 }",
                "rust_function": "fn first() {}",
                "support_functions": [helper, c_only],
            },
            {"rust_function": "fn second() {}", "support_functions": [helper]},
        ]
        text = native.source_for_cases(cases)
        self.assertIn("#![feature(f16)]", text)
        self.assertIn("#[repr(C)] struct Pair", text)
        self.assertEqual(text.count("fn leaf()"), 1)
        self.assertIn("fn second()", text)

    def test_rom_cost_includes_tables_and_initializers_but_not_bss_or_debug(self):
        sections = []
        for name, size, kind, flags in [
            (".text", 7, "SHT_PROGBITS", ["SHF_ALLOC", "SHF_EXECINSTR"]),
            (".rodata", 16, "SHT_PROGBITS", ["SHF_ALLOC"]),
            (".data", 2, "SHT_PROGBITS", ["SHF_ALLOC", "SHF_WRITE"]),
            (".bss", 30, "SHT_NOBITS", ["SHF_ALLOC", "SHF_WRITE"]),
            (".debug_info", 100, "SHT_PROGBITS", []),
        ]:
            sections.append(
                {
                    "Section": {
                        "Name": {"Name": name},
                        "Size": size,
                        "Type": {"Name": kind},
                        "Flags": {"Flags": [{"Name": f} for f in flags]},
                    }
                }
            )
        measured = native.rom_sections([{"Sections": sections}])
        self.assertEqual(sum(s["bytes"] for s in measured), 25)

    def test_native_attempts_patterns_and_isolates_failures_without_losing_bodies(self):
        compiler = object.__new__(native.NativeRustZ80)
        compiler.logs = []
        compiler.rustc_command = ["native-rustc"]
        compiler.bin = Path("llvm-bin")
        cases = [
            {
                "id": name,
                "kind": "pattern",
                "rust_header": "#![no_std]",
                "rust_function": f'pub extern "C" fn {name}() {{}}',
            }
            for name in ["good", "bad"]
        ]

        def execute(command):
            if "--emit=asm,obj,llvm-ir" in command:
                source = Path(command[1]).read_text()
                if "fn bad" in source:
                    raise ValueError("backend cannot lower this operation")
                names = re.findall(r"fn (\w+)\(", source)
                output = Path(command[-1])
                output.with_suffix(".s").write_text(
                    "\n".join(
                        f"_{name}:\n ret\n.Lfunc_end{i}:"
                        for i, name in enumerate(names)
                    )
                )
            elif "--print-size" in command:
                return {"stdout": "00000000 00000001 T _good\n"}
            return {"stdout": ""}

        with tempfile.TemporaryDirectory() as temporary:
            with (
                patch.object(compiler, "execute", side_effect=execute),
                patch.object(
                    compiler,
                    "linked_cost",
                    return_value={
                        "status": "partial",
                        "diagnostic": "unresolved core helper",
                    },
                ),
            ):
                records, _ = compiler.compile_group(cases, "size", Path(temporary))
        self.assertEqual(records["good"]["status"], "ok")
        self.assertEqual(records["good"]["function_bytes"], 1)
        self.assertEqual(records["good"]["library"]["status"], "partial")
        self.assertEqual(records["bad"]["status"], "error")
        self.assertIn("backend cannot lower", records["bad"]["diagnostic"])


if __name__ == "__main__":
    unittest.main()
