#!/usr/bin/env python3
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any

from analyze import instructions
from compare import run
from cycle_cases import subcases
from cycle_runner import DEFAULT_LIBRARY, SameBoy
from generate import ROOT
from rust_z80 import NativeRustZ80
from setup_llvm_z80 import DEFAULT_BIN
from setup_rust_z80 import DEFAULT_RUSTC
from sm83 import read_ihx


INPUT = 0xC100
OUTPUT = 0xC180
DONE = 0xC1A0
C_TYPES = {"u8": "uint8_t", "u16": "uint16_t", "*const u8": "const uint8_t *"}


def signature(case):
    match = re.search(r"fn \w+\(([^)]*)\)\s*->\s*([^\{]+)", case["rust_function"])
    if match is None:
        raise ValueError("unsupported timing fixture signature")
    parameters = [
        tuple(v.strip() for v in arg.split(":", 1))
        for arg in match[1].split(",")
        if arg.strip()
    ]
    return parameters, match[2].strip()


def wrapper(case, language, include=False):
    parameters, result = signature(case)
    name = case["id"]
    if language == "rust":
        arguments = ", ".join(
            f"core::ptr::read_volatile({INPUT + 16 * i} as *const {ty})"
            for i, (_, ty) in enumerate(parameters)
        )
        declarations = (
            ""
            if include
            else f'unsafe extern "C" {{ fn {name}({", ".join(n + ": " + ty for n, ty in parameters)}) -> {result}; }}\n'
        )
        body = f"#[unsafe(no_mangle)]\npub fn gbc_main() -> u8 {{ unsafe {{ let value = {name}({arguments}); core::ptr::write_volatile({OUTPUT} as *mut {result}, value); core::ptr::write_volatile({DONE} as *mut u8, 1); }} 0 }}\n"
        if include:
            header = (
                case.get("rust_header")
                or (ROOT / case["rust_source"]).read_text().split("\n\n", 1)[0]
            )
            return header + "\n\n" + case["rust_function"] + "\n\n" + body
        return "#![no_std]\n" + declarations + body
    arguments = ", ".join(
        f"*({C_TYPES[ty]} volatile *){INPUT + 16 * i}"
        for i, (_, ty) in enumerate(parameters)
    )
    prototype = case["c_function"].split("{", 1)[0].strip() + ";\n"
    return (
        "#include <stdint.h>\n"
        + prototype
        + f"void gbc_main(void) {{ {C_TYPES[result]} value = {name}({arguments}); *({C_TYPES[result]} volatile *){OUTPUT} = value; *(uint8_t volatile *){DONE} = 1; }}\n"
    )


def elf_image(path, readobj, execute):
    data = path.read_bytes()
    obj = json.loads(
        execute([readobj, "--elf-output-style=JSON", "--sections", "--symbols", path])[
            "stdout"
        ]
    )[0]
    rom, memory = bytearray(0x8000), {}
    for entry in obj["Sections"]:
        section = entry["Section"]
        if section["Type"]["Name"] != "SHT_PROGBITS" or not any(
            f["Name"] == "SHF_ALLOC" for f in section["Flags"]["Flags"]
        ):
            continue
        address, size, offset = section["Address"], section["Size"], section["Offset"]
        content = data[offset : offset + size]
        if address + size <= len(rom):
            rom[address : address + size] = content
        elif 0xC000 <= address and address + size <= 0xE000:
            memory[address] = content
        elif size:
            raise ValueError(
                f"ELF section outside benchmark memory: {section['Name']['Name']}"
            )
    symbols = {
        s["Symbol"]["Name"]["Name"]: s["Symbol"]["Value"] for s in obj["Symbols"]
    }
    return bytes(rom), memory, symbols


class CycleBench:
    def __init__(
        self,
        report,
        library=DEFAULT_LIBRARY,
        *,
        sangoku=None,
        sdcc=None,
        llvm_bin=DEFAULT_BIN,
        rustc=DEFAULT_RUSTC,
    ):
        self.report = report
        self.emulator = SameBoy(library)
        self.sangoku = Path(
            sangoku or report["tools"]["sangoku"]["command"][0]
        ).resolve()
        self.sdcc = sdcc or report["tools"]["sdcc"]["command"][0]
        version = run([self.sdcc, "--version"])
        if version["stdout"] + version["stderr"] != report["tools"]["sdcc"]["version"]:
            raise ValueError(
                "SDCC differs from the comparison; rebuild the report before timing"
            )
        if (
            hashlib.sha256(self.sangoku.read_bytes()).hexdigest()
            != report["tools"]["sangoku"]["binary_sha256"]
        ):
            raise ValueError(
                "Sangoku changed since this report; rebuild the comparison before timing"
            )
        self.native = NativeRustZ80(llvm_bin, rustc, run)
        recorded = report["tools"].get("llvm_z80", {})
        if (
            recorded.get("method") != self.native.metadata["method"]
            or recorded.get("sha256") != self.native.metadata["sha256"]
        ):
            raise ValueError(
                "native LLVM toolchain differs from the comparison; rebuild the report before timing"
            )
        self.logs = []

    def execute(self, command):
        result = run(command)
        self.logs.append(result)
        if result["returncode"] != 0:
            raise ValueError(result["stderr"] or result["stdout"])
        return result

    def build(self, case, compiler, mode, directory):
        directory.mkdir(parents=True, exist_ok=True)
        result = case[compiler]
        if result["status"] != "ok":
            raise ValueError("no successful static measurement")
        level = "z" if mode == "size" else "3"
        if compiler == "sangoku":
            source, rom = directory / "probe.rs", directory / "probe.gb"
            source.write_text(wrapper(case, "rust", include=True))
            outcome = self.execute(
                [self.sangoku, "build", source, rom, "--opt-level", level]
            )
            match = re.search(r"Build artifacts: (.+)", outcome["stderr"])
            if not match:
                raise ValueError("Sangoku did not report build artifacts")
            artifacts = Path(match[1].strip())
            symbols = {
                m[2]: int(m[1], 16)
                for m in re.finditer(
                    r"^\s*\$([0-9a-fA-F]+) = (\S+)",
                    (artifacts / "game.map").read_text(),
                    re.M,
                )
            }
            assembly = (artifacts / "probe.asm").read_text()
            body = re.search(
                r'^SECTION "__rust_'
                + re.escape(case["id"])
                + r'"[^\n]*\n(.*?)(?=^SECTION|\Z)',
                assembly,
                re.M | re.S,
            )
            if body is None or [v for _, v in instructions(body[1])] != [
                v for _, v in instructions(result["assembly"])
            ]:
                raise ValueError("Sangoku timing body differs from static comparison")
            return (
                rom.read_bytes(),
                {},
                symbols["__rust_gbc_main"],
                symbols["__rust_" + case["id"]],
            )
        static = Path(result["assembly_path"]).with_suffix(
            ".rel" if compiler == "sdcc" else ".o"
        )
        if not static.is_file():
            raise ValueError(f"static object missing: {static}; rebuild the comparison")
        if compiler == "sdcc":
            source = directory / "wrapper.c"
            source.write_text(wrapper(case, "c"))
            self.execute(
                [
                    self.sdcc,
                    "-msm83",
                    "--std-c11",
                    "--opt-code-" + mode,
                    "-c",
                    source,
                    "-o",
                    directory / "wrapper.rel",
                ]
            )
            self.execute(
                [
                    self.sdcc,
                    "-msm83",
                    "--no-std-crt0",
                    "--code-loc",
                    "0x0200",
                    "--data-loc",
                    "0xc800",
                    static,
                    directory / "wrapper.rel",
                    "-o",
                    directory / "probe.ihx",
                ]
            )
            memory = read_ihx((directory / "probe.ihx").read_text())
            rom, initial = bytearray(0x8000), {}
            for address, value in memory.items():
                if address < len(rom):
                    rom[address] = value
                elif 0xC000 <= address < 0xE000:
                    initial[address] = bytes([value])
                else:
                    raise ValueError(
                        f"SDCC linked byte outside benchmark memory: {address:04x}"
                    )
            symbols = {
                m[2]: int(m[1], 16)
                for m in re.finditer(
                    r"^\s*([0-9a-fA-F]{8})\s+(_\w+)\s",
                    (directory / "probe.map").read_text(),
                    re.M,
                )
            }
            return bytes(rom), initial, symbols["_gbc_main"], symbols["_" + case["id"]]
        source = directory / "wrapper.rs"
        source.write_text(wrapper(case, "rust"))
        self.execute(
            [
                *self.native.rustc_command,
                source,
                "--target",
                "sm83-nintendo-none-elf",
                "--crate-type",
                "lib",
                "--edition",
                "2024",
                "--emit=obj",
                "-Copt-level=" + level,
                "-Cdebug-assertions=no",
                "-Coverflow-checks=no",
                "-o",
                directory / "wrapper.o",
            ]
        )
        script = directory / "probe.ld"
        script.write_text(
            "SECTIONS { . = 0x200; .text : { *(.text*) *(.rodata*) } . = 0xc800; .data : { *(.data*) } .bss (NOLOAD) : { *(.bss*) *(COMMON) } /DISCARD/ : { *(.comment) *(.eh_frame*) } }\n"
        )
        self.execute(
            [
                *self.native.linker_command,
                "--gc-sections",
                "--entry=_gbc_main",
                "-T",
                script,
                static,
                directory / "wrapper.o",
                "--start-group",
                *sorted(self.native.target_lib.glob("*.rlib")),
                self.native.archive,
                "--end-group",
                "-o",
                directory / "probe.elf",
            ]
        )
        rom, initial, symbols = elf_image(
            directory / "probe.elf", self.native.bin / "llvm-readobj", self.execute
        )
        return rom, initial, symbols["_gbc_main"], symbols["_" + case["id"]]

    def measure(self, case, mode, directory):
        samples = subcases(case)
        results: list[dict[str, Any]] = [
            {
                "input": sample["input"],
                "args": sample["args"],
                "memory": {
                    f"{address:04x}": bytes(data).hex()
                    for address, data in sample["memory"].items()
                },
                "expected": sample["expected"],
                "compilers": {},
            }
            for sample in samples
        ]
        for compiler in ("sangoku", "sdcc", "llvm_z80"):
            try:
                image, initial, entry, target = self.build(
                    case, compiler, mode, directory / compiler
                )
                (directory / compiler / "timed.gb").write_bytes(image)
                binary_hash = hashlib.sha256(image).hexdigest()
            except (ValueError, KeyError, OSError) as error:
                for result in results:
                    result["compilers"][compiler] = {
                        "status": "error",
                        "diagnostic": str(error),
                    }
                continue
            parameters, result_type = signature(case)
            size = {"u8": 1, "u16": 2}[result_type]
            for sample, result in zip(samples, results):
                memory = {**initial, **sample["memory"]}
                for i, (value, (_, ty)) in enumerate(zip(sample["args"], parameters)):
                    memory[INPUT + 16 * i] = value.to_bytes(
                        1 if ty == "u8" else 2, "little"
                    )
                try:
                    measured = self.emulator.run(
                        image,
                        entry,
                        measure=target,
                        memory=memory,
                        done=DONE,
                        output=(OUTPUT, size),
                        expected=sample["expected"].to_bytes(size, "little"),
                    )
                    result["compilers"][compiler] = {
                        "status": "ok",
                        "t_cycles": measured["t_cycles"],
                        "output": measured["output"],
                        "rom_sha256": binary_hash,
                    }
                except ValueError as error:
                    result["compilers"][compiler] = {
                        "status": "error",
                        "diagnostic": str(error),
                        "rom_sha256": binary_hash,
                    }
        for result in results:
            candidates = {
                name: result["compilers"][name]["t_cycles"]
                for name in ("sdcc", "llvm_z80")
                if result["compilers"][name]["status"] == "ok"
            }
            result["reference"] = (
                {
                    "status": "ok",
                    "t_cycles": min(candidates.values()),
                    "compilers": [
                        name
                        for name, value in candidates.items()
                        if value == min(candidates.values())
                    ],
                }
                if candidates
                else {"status": "unavailable"}
            )
        return {
            "unit": "T-cycles",
            "scope": "function entry through return, including executed helpers; wrapper setup and result stores excluded",
            "samples": results,
        }


def add_cycles(report, args):
    bench = CycleBench(
        report, args.sameboy_library, llvm_bin=args.llvm_z80, rustc=args.llvm_rustc
    )
    work = (
        ROOT
        / "build"
        / ("cycles-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f"))
    )
    failed = False
    for mode, run_data in report["runs"].items():
        for case in run_data["cases"]:
            if subcases(case) and (
                not args.cycle_case or case["id"] in args.cycle_case
            ):
                print(f"cycles {mode}: {case['id']}", flush=True)
                case["cycles"] = bench.measure(case, mode, work / mode / case["id"])
                failed |= any(
                    v["status"] != "ok"
                    for s in case["cycles"]["samples"]
                    for v in s["compilers"].values()
                )
    report["cycle_methodology"] = {
        **bench.emulator.metadata,
        "measured_at": datetime.now(timezone.utc).isoformat(),
        "subcases_sha256": hashlib.sha256(
            (ROOT / "tools/cycle_cases.py").read_bytes()
        ).hexdigest(),
        "scope": "entry through return including helpers; caller setup excluded; each result checked against declared expected output; cycles best selected independently of size best",
    }
    report["methodology"]["scope"] = (
        "static codegen comparison plus verified emulator timing for declared input subcases; untimed fixtures and other inputs are not target-validated"
    )
    report["commands"] += [{"phase": "cycles", **log} for log in bench.logs]
    return failed


def main():
    parser = argparse.ArgumentParser(
        description="Measure explicit input subcases in SameBoy and attach verified cycle results to an existing comparison."
    )
    parser.add_argument(
        "report", nargs="?", type=Path, default=ROOT / "results/comparison.json"
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--case", dest="cycle_case", nargs="+")
    parser.add_argument("--sameboy-library", type=Path, default=DEFAULT_LIBRARY)
    parser.add_argument("--llvm-z80", type=Path, default=DEFAULT_BIN)
    parser.add_argument("--llvm-rustc", type=Path, default=DEFAULT_RUSTC)
    args = parser.parse_args()
    report = json.loads(args.report.read_text())
    available = {
        case["id"]
        for data in report["runs"].values()
        for case in data["cases"]
        if subcases(case)
    }
    if args.cycle_case and set(args.cycle_case) - available:
        parser.error(
            "no declared subcases in this report for: "
            + ", ".join(sorted(set(args.cycle_case) - available))
        )
    failed = add_cycles(report, args)
    output = args.output or args.report
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Saved explicit input timings in {output}")
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
