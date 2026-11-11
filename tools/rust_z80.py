import hashlib
import json
from pathlib import Path
import re

from generate import ROOT
from llvm_z80 import LlvmZ80, TARGET, parse_symbols


METHOD = "native Rust-Z80 SM83 frontend and LLVM backend"


def source_for_cases(cases):
    header = cases[0].get("rust_header")
    if header is None:
        header = (ROOT / cases[0]["rust_source"]).read_text().split("\n\n", 1)[0]
    helpers = {
        h["id"]: h
        for c in cases
        for h in c.get("support_functions", [])
        if "rust" in h.get("languages", ["rust", "c"])
    }
    return (
        header
        + "\n\n"
        + "\n\n".join(c["rust_function"] for c in [*helpers.values(), *cases])
        + "\n"
    )


def rom_sections(objects):
    return [
        {"name": s["Name"]["Name"], "bytes": s["Size"]}
        for obj in objects
        for entry in obj["Sections"]
        for s in [entry["Section"]]
        if s["Size"]
        and s["Type"]["Name"] == "SHT_PROGBITS"
        and any(flag["Name"] == "SHF_ALLOC" for flag in s["Flags"]["Flags"])
    ]


class NativeRustZ80(LlvmZ80):
    def __init__(self, bin_directory, rustc, run, timeout=180):
        rustc = Path(rustc).resolve()
        if not rustc.is_file():
            raise ValueError(
                f"native Rust-Z80 compiler missing: {rustc}; run python3 tools/setup_rust_z80.py, pass --llvm-rustc, or select --llvm-frontend ir"
            )
        super().__init__(bin_directory, None, run, timeout, native_rustc=rustc)
        self.metadata["merge_functions"] = "disabled in fixture modules"
        targets = self.execute([*self.rustc_command, "--print", "target-list"])[
            "stdout"
        ]
        if TARGET not in targets.splitlines():
            raise ValueError(f"{rustc} does not support {TARGET}")
        self.target_lib = self.sysroot / "lib/rustlib" / TARGET / "lib"
        if not list(self.target_lib.glob("libcore-*.rlib")):
            raise ValueError(
                f"native SM83 core is missing from {self.target_lib}; rebuild with tools/setup_rust_z80.py"
            )
        if not (self.target_lib / "self-contained/libsm83_rt.a").is_file():
            raise ValueError(
                "native SM83 runtime is missing; rebuild with tools/setup_rust_z80.py"
            )
        match = re.search(r"^host: (.+)$", self.metadata["rustc"], re.M)
        if match is None:
            raise ValueError("native rustc did not report its host triple")
        host = match[1]
        host_bin = self.sysroot / "lib/rustlib" / host / "bin"
        linker = next(
            (
                p
                for p in [host_bin / "rust-lld", host_bin / "gcc-ld/ld.lld"]
                if p.is_file()
            ),
            None,
        )
        if linker is None:
            raise ValueError(
                "native Rust-Z80 needs its matching bundled LLD; rebuild with tools/setup_rust_z80.py"
            )
        self.linker_command = (
            [linker, "-flavor", "gnu"] if linker.name == "rust-lld" else [linker]
        )
        self.metadata["sha256"][str(linker)] = hashlib.sha256(
            linker.read_bytes()
        ).hexdigest()
        manifest = self.sysroot.parents[1] / "toolchain.json"
        if manifest.is_file():
            self.metadata["build"] = json.loads(manifest.read_text())

    def linked_cost(self, case, directory):
        output = directory / (case["id"] + ".elf")
        script = directory / "probe.ld"
        script.write_text(
            "SECTIONS { . = 0; .text : { *(.text*) *(.rodata*) } .data : { *(.data*) } .bss (NOLOAD) : { *(.bss*) *(COMMON) } /DISCARD/ : { *(.comment) *(.eh_frame*) } }\n"
        )
        archives = sorted(self.target_lib.glob("*.rlib"))
        if self.archive.is_file():
            archives.append(self.archive)
        try:
            self.execute(
                [
                    *self.linker_command,
                    "--gc-sections",
                    "--entry=_" + case["id"],
                    "-T",
                    script,
                    directory / "output.o",
                    "--start-group",
                    *archives,
                    "--end-group",
                    "-o",
                    output,
                ]
            )
            sections = rom_sections(
                json.loads(
                    self.execute(
                        [
                            self.bin / "llvm-readobj",
                            "--elf-output-style=JSON",
                            "--sections",
                            output,
                        ]
                    )["stdout"]
                )
            )
            return {
                "status": "ok",
                "measurement": "isolated linked reachable ELF ROM sections; no startup or entry harness; section padding included",
                "total_bytes": sum(s["bytes"] for s in sections),
                "sections": sections,
                "elf_path": str(output),
            }
        except (ValueError, OSError) as error:
            return {
                "status": "partial",
                "measurement": "isolated native ELF link failed",
                "diagnostic": str(error),
            }

    def compile_group(self, cases, mode, work):
        start = len(self.logs)

        def compile_selected(selected, directory):
            directory.mkdir(parents=True, exist_ok=True)
            source = directory / "selected.rs"
            source.write_text(source_for_cases(selected))
            self.execute(
                [
                    *self.rustc_command,
                    source,
                    "--target",
                    TARGET,
                    "--crate-type",
                    "lib",
                    "--edition",
                    "2024",
                    "--emit=asm,obj,llvm-ir",
                    "-Copt-level=" + ("z" if mode == "size" else "3"),
                    "-Cdebug-assertions=no",
                    "-Coverflow-checks=no",
                    "-Zmerge-functions=disabled",
                    "-Cllvm-args=-enable-machine-outliner=never -z80-warn-stack-align-padding=0",
                    "-o",
                    directory / "output",
                ]
            )
            sizes = parse_symbols(
                self.execute(
                    [self.bin / "llvm-nm", "--print-size", directory / "output.o"]
                )["stdout"]
            )
            assembly = (directory / "output.s").read_text()
            if "_OUTLINED_FUNCTION_" in assembly:
                raise ValueError("native machine outlining was not disabled")
            bodies = {
                m[1]: m[2]
                for m in re.finditer(
                    r"^(_\w+):[^\n]*\n(.*?)^\.Lfunc_end\d+:", assembly, re.M | re.S
                )
            }
            records = {}
            for case in selected:
                symbol = "_" + case["id"]
                if symbol not in sizes or symbol not in bodies:
                    raise ValueError(f"missing native function symbol: {symbol}")
                body = bodies[symbol]
                helper_names = {
                    h["id"]
                    for h in case.get("support_functions", [])
                    if "rust" in h.get("languages", ["rust", "c"])
                }
                helpers = {
                    n: {"function_bytes": sizes["_" + n], "assembly": bodies["_" + n]}
                    for n in sorted(helper_names)
                }
                helper_bytes = sum(h["function_bytes"] for h in helpers.values())
                library = self.linked_cost(case, directory)
                if library["status"] == "ok":
                    library["dependency_bytes"] = library["total_bytes"] - sizes[symbol]
                    library["includes_fixture_helpers"] = True
                records[case["id"]] = {
                    "status": "ok",
                    "method": METHOD,
                    "function_bytes": sizes[symbol],
                    "assembly": body,
                    "assembly_path": str(directory / "output.s"),
                    "external_transfers": [
                        {"kind": m[1], "target": m[2]}
                        for m in re.finditer(
                            r"^\s*(call|jp)\s+(?:[a-z]+,)?(_\w+)\s*$", body, re.M
                        )
                    ],
                    "library": library,
                }
                if helpers:
                    records[case["id"]].update(
                        {
                            "fixture_helpers": helpers,
                            "fixture_helper_bytes": helper_bytes,
                            "function_with_fixture_helpers_bytes": sizes[symbol]
                            + helper_bytes,
                        }
                    )
            return records

        try:
            results = compile_selected(cases, work)
        except (ValueError, OSError, KeyError) as error:
            results = {}
            for case in cases:
                try:
                    results.update(compile_selected([case], work / case["id"]))
                except (ValueError, OSError, KeyError) as isolated:
                    results[case["id"]] = {
                        "status": "error",
                        "method": METHOD,
                        "diagnostic": str(isolated),
                        "group_diagnostic": str(error),
                    }
        return results, self.logs[start:]
