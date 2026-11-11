import hashlib
import json
from pathlib import Path
import re
from typing import Any

from setup_llvm_z80 import DEFAULT_BIN


TARGET = "sm83-nintendo-none-elf"
LAYOUT = "e-m:o-p:16:8-i16:8-i32:8-i64:8-i128:8-f32:8-f64:8-ve-n8:16"
METHOD = "experimental fixed-width scalar Rust LLVM IR retargeting; not the Rust-Z80 frontend"


def supported(case):
    return (
        case["kind"] == "integer" and case["width"] <= 64 and case["result_width"] <= 64
    )


def retarget(text):
    text = re.sub(
        r"^target datalayout = .*$", f'target datalayout = "{LAYOUT}"', text, flags=re.M
    )
    text = re.sub(
        r"^target triple = .*$", f'target triple = "{TARGET}"', text, flags=re.M
    )
    text = re.sub(r'"(?:target-cpu|target-features|probe-stack)"="[^"]*"', "", text)
    text = re.sub(r"\b(?:zeroext|signext|uwtable|nonlazybind)\b", "", text)
    text = text.replace(" personality ptr @rust_eh_personality", "")
    return re.sub(
        r"^(attributes #\d+ = \{)",
        r'\1 "target-cpu"="sm83" "target-features"="+inline-i16-runtime" ',
        text,
        flags=re.M,
    )


def parse_symbols(text):
    return {
        match[3]: int(match[2], 16)
        for match in re.finditer(
            r"^([0-9a-fA-F]+)\s+([0-9a-fA-F]+)\s+[Tt]\s+(\w+)$", text, re.M
        )
    }


class LlvmZ80:
    def __init__(self, bin_directory, toolchain, run, timeout=180, native_rustc=None):
        self.bin = Path(bin_directory or DEFAULT_BIN).resolve()
        self.toolchain = toolchain
        self.run = run
        self.timeout = timeout
        self.logs = []
        for name in ("clang", "llvm-nm", "llvm-readobj"):
            if not (self.bin / name).is_file():
                raise ValueError(
                    f"LLVM-Z80 {name} missing in {self.bin}; run python3 tools/setup_llvm_z80.py or pass --without-llvm-z80"
                )
        self.archive = self.bin.parent / "lib/sm83/sm83_rt.a"
        self.rustc_command = (
            [str(native_rustc)] if native_rustc else ["rustc", "+" + toolchain]
        )
        self.metadata: dict[str, Any] = {
            "method": "native Rust-Z80 SM83 frontend and LLVM backend"
            if native_rustc
            else METHOD,
            "rust_toolchain": toolchain,
            "machine_outliner": "disabled for stable per-case measurements",
        }
        for name, command in {
            "clang": [self.bin / "clang", "--version"],
            "rustc": [*self.rustc_command, "-Vv"],
        }.items():
            self.metadata[name] = self.execute(command)["stdout"]
        sysroot = Path(
            self.execute([*self.rustc_command, "--print", "sysroot"])["stdout"].strip()
        )
        self.sysroot = sysroot
        native_archive = (
            sysroot / "lib/rustlib" / TARGET / "lib/self-contained/libsm83_rt.a"
        )
        if native_rustc and native_archive.is_file():
            self.archive = native_archive
        inputs = [
            self.bin / "clang",
            self.bin / "llvm-nm",
            self.bin / "llvm-readobj",
            sysroot / "bin/rustc",
        ]
        inputs.extend(sorted((sysroot / "lib").glob("*rustc_driver*")))
        inputs.extend(sorted((sysroot / "lib").glob("*LLVM*")))
        inputs.extend(sorted(sysroot.glob("lib/rustlib/*/codegen-backends/*")))
        if native_rustc:
            inputs.extend(
                sorted((sysroot / "lib/rustlib" / TARGET / "lib").glob("*.rlib"))
            )
        inputs.extend(
            sorted(
                (sysroot / "lib/rustlib/x86_64-unknown-linux-gnu/lib").glob(
                    "libcore-*.rlib"
                )
            )
        )
        if self.archive.is_file():
            inputs.append(self.archive)
        self.metadata["sha256"] = {
            str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs
        }
        self.modules, self.exports = {}, {}
        if self.archive.is_file():
            objects = json.loads(
                self.execute(
                    [
                        self.bin / "llvm-readobj",
                        "--elf-output-style=JSON",
                        "--sections",
                        "--symbols",
                        self.archive,
                    ]
                )["stdout"]
            )
            for obj in objects:
                name = obj["FileSummary"]["File"].rsplit("(", 1)[1].removesuffix(")")
                size = 0
                for entry in obj["Sections"]:
                    section = entry["Section"]
                    flags = {f["Name"] for f in section["Flags"]["Flags"]}
                    if (
                        "SHF_ALLOC" in flags
                        and "SHF_WRITE" not in flags
                        and section["Type"]["Name"] != "SHT_NOBITS"
                    ):
                        size += section["Size"]
                definitions, references = [], []
                for entry in obj["Symbols"]:
                    symbol = entry["Symbol"]
                    if symbol["Binding"]["Name"] != "Global":
                        continue
                    target = symbol["Name"]["Name"]
                    if symbol["Section"]["Name"] == "Undefined":
                        references.append(target)
                    else:
                        definitions.append(target)
                        self.exports[target] = name
                self.modules[name] = {
                    "member": name,
                    "code_bytes": size,
                    "definitions": definitions,
                    "references": references,
                }

    def execute(self, command):
        result = self.run(command, timeout=self.timeout)
        self.logs.append(result)
        if result["returncode"] != 0:
            raise ValueError(result["stderr"] or result["stdout"])
        return result

    def dependencies(self, symbols, body_bytes):
        pending, selected, missing = list(symbols), set(), set()
        while pending:
            symbol = pending.pop()
            member = self.exports.get(symbol)
            if member is None:
                missing.add(symbol)
            elif member not in selected:
                selected.add(member)
                pending.extend(self.modules[member]["references"])
        modules = [self.modules[n] for n in sorted(selected)]
        size = sum(m["code_bytes"] for m in modules)
        result = {
            "status": "partial" if missing else "ok",
            "measurement": "transitive LLVM runtime archive member ROM sections; alignment excluded",
            "archive": str(self.archive),
            "dependency_bytes": size,
            "modules": modules,
            "unresolved_symbols": sorted(missing),
        }
        if not missing:
            result["total_bytes"] = body_bytes + size
        return result

    def compile_group(self, cases, mode, work):
        work.mkdir(parents=True, exist_ok=True)
        start = len(self.logs)
        results = {
            c["id"]: {
                "status": "unsupported",
                "diagnostic": "IR retargeting covers only scalar integer fixtures with input/result widths <= 64; requires native Rust-Z80 for other cases",
            }
            for c in cases
            if not supported(c)
        }
        group = [c for c in cases if supported(c)]
        if not group:
            return results, []

        def compile_selected(selected, directory):
            directory.mkdir(parents=True, exist_ok=True)
            source = directory / "selected.rs"
            source.write_text(
                "#![no_std]\n#![feature(core_intrinsics)]\n#![allow(internal_features)]\n\n"
                + "\n\n".join(c["rust_function"] for c in selected)
                + "\n"
            )
            level = "z" if mode == "size" else "3"
            raw, ir = directory / "raw.ll", directory / "sm83.ll"
            self.execute(
                [
                    "rustc",
                    "+" + self.toolchain,
                    source,
                    "--crate-type",
                    "lib",
                    "--edition",
                    "2024",
                    "--emit=llvm-ir",
                    "-Copt-level=" + level,
                    "-Cpanic=abort",
                    "-Cdebug-assertions=no",
                    "-Coverflow-checks=no",
                    "-Cno-prepopulate-passes",
                    "-o",
                    raw,
                ]
            )
            ir.write_text(retarget(raw.read_text()))
            command = [
                self.bin / "clang",
                "-target",
                TARGET,
                "-O" + level,
                "-mllvm",
                "-two-entry-phi-node-folding-threshold=0",
                "-mllvm",
                "-enable-load-in-loop-pre=false",
                "-mllvm",
                "-enable-machine-outliner=never",
                "-x",
                "ir",
                ir,
            ]
            self.execute(
                command + ["-S", "-emit-llvm", "-o", directory / "optimized.ll"]
            )
            self.execute(command + ["-S", "-o", directory / "output.s"])
            self.execute(command + ["-c", "-o", directory / "output.o"])
            sizes = parse_symbols(
                self.execute(
                    [self.bin / "llvm-nm", "--print-size", directory / "output.o"]
                )["stdout"]
            )
            assembly = (directory / "output.s").read_text()
            bodies = {
                m[1]: m[2]
                for m in re.finditer(
                    r"^(_\w+):[^\n]*\n(.*?)^\.Lfunc_end\d+:", assembly, re.M | re.S
                )
            }
            if "_OUTLINED_FUNCTION_" in assembly:
                raise ValueError("LLVM machine outlining was not disabled")
            records = {}
            for case in selected:
                symbol = "_" + case["id"]
                if symbol not in sizes or symbol not in bodies:
                    raise ValueError(f"missing LLVM function symbol: {symbol}")
                body = bodies[symbol]
                transfers = [
                    {"kind": m[1], "target": m[2]}
                    for m in re.finditer(
                        r"^\s*(call|jp)\s+(?:[a-z]+,)?(_\w+)\s*$", body, re.M
                    )
                ]
                records[case["id"]] = {
                    "status": "ok",
                    "method": METHOD,
                    "function_bytes": sizes[symbol],
                    "assembly": body,
                    "assembly_path": str(directory / "output.s"),
                    "external_transfers": transfers,
                    "library": self.dependencies(
                        (t["target"] for t in transfers), sizes[symbol]
                    ),
                }
            return records

        try:
            results.update(compile_selected(group, work))
        except (ValueError, OSError, KeyError) as error:
            for case in group:
                try:
                    results.update(compile_selected([case], work / case["id"]))
                except (ValueError, OSError, KeyError) as isolated:
                    results[case["id"]] = {
                        "status": "error",
                        "diagnostic": str(isolated),
                        "group_diagnostic": str(error),
                    }
        return results, self.logs[start:]
