import argparse
import ctypes as c
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LIBRARY = Path.home() / "SameBoy/build/lib/libsameboy.so"


class Registers(c.Structure):
    _fields_ = [(name, c.c_uint16) for name in ("af", "bc", "de", "hl", "sp", "pc")]


class SameBoy:
    def __init__(self, library=DEFAULT_LIBRARY):
        self.path = Path(library).resolve()
        self.lib = c.CDLL(str(self.path))
        signatures = {
            "GB_alloc": (c.c_void_p, []),
            "GB_init": (c.c_void_p, [c.c_void_p, c.c_int]),
            "GB_dealloc": (None, [c.c_void_p]),
            "GB_load_rom_from_buffer": (None, [c.c_void_p, c.c_void_p, c.c_size_t]),
            "GB_get_registers": (c.POINTER(Registers), [c.c_void_p]),
            "GB_get_direct_access": (
                c.c_void_p,
                [c.c_void_p, c.c_int, c.POINTER(c.c_size_t), c.POINTER(c.c_uint16)],
            ),
            "GB_read_memory": (c.c_uint8, [c.c_void_p, c.c_uint16]),
            "GB_write_memory": (None, [c.c_void_p, c.c_uint16, c.c_uint8]),
            "GB_run": (c.c_uint, [c.c_void_p]),
        }
        for name, (result, args) in signatures.items():
            function = getattr(self.lib, name)
            function.restype, function.argtypes = result, args
        self.metadata = {
            "library": str(self.path),
            "sha256": hashlib.sha256(self.path.read_bytes()).hexdigest(),
            "model": "DMG-B, normal speed, LCD and interrupts disabled",
            "unit": "T-cycles; SameBoy 8MHz ticks divided by 2",
        }

    def run(
        self,
        rom,
        entry,
        *,
        measure=None,
        registers=None,
        memory=None,
        done=None,
        output=None,
        expected=None,
        limit=1_000_000,
    ):
        if len(rom) > 0x8000:
            raise ValueError("cycle runner supports unbanked 32 KiB ROM images")
        gb = self.lib.GB_init(self.lib.GB_alloc(), 2)
        try:
            data = c.create_string_buffer(bytes(rom).ljust(0x8000, b"\0"))
            self.lib.GB_load_rom_from_buffer(gb, data, len(data) - 1)
            for region in (1, 4):
                size, bank = c.c_size_t(), c.c_uint16()
                pointer = self.lib.GB_get_direct_access(
                    gb, region, c.byref(size), c.byref(bank)
                )
                c.memset(pointer, 0, size.value)
            for address, value in [(0xFF50, 1), (0xFF40, 0), (0xFFFF, 0), (0xFF0F, 0)]:
                self.lib.GB_write_memory(gb, address, value)
            regs = self.lib.GB_get_registers(gb).contents
            for name, _ in Registers._fields_:
                setattr(regs, name, 0)
            regs.pc, regs.sp = entry, 0xDFF0
            for name, value in (registers or {}).items():
                if name not in dict(Registers._fields_) or not 0 <= value <= 0xFFFF:
                    raise ValueError(f"invalid register assignment: {name}={value}")
                setattr(regs, name, value)
            for address, values in (memory or {}).items():
                for offset, value in enumerate(values):
                    self.lib.GB_write_memory(gb, address + offset, value)
            sentinel = 0xFF80
            regs.sp -= 2
            self.lib.GB_write_memory(gb, regs.sp, sentinel & 255)
            self.lib.GB_write_memory(gb, regs.sp + 1, sentinel >> 8)
            active, returned, ticks, stop = False, False, 0, sentinel
            measure = entry if measure is None else measure
            for instructions in range(limit):
                if not active and not returned and regs.pc == measure:
                    active = True
                    stop = (
                        self.lib.GB_read_memory(gb, regs.sp)
                        | self.lib.GB_read_memory(gb, regs.sp + 1) << 8
                    )
                if active and regs.pc == stop:
                    active, returned = False, True
                if returned and (
                    done is None or self.lib.GB_read_memory(gb, done) == 1
                ):
                    actual = (
                        bytes(
                            self.lib.GB_read_memory(gb, output[0] + i)
                            for i in range(output[1])
                        )
                        if output
                        else None
                    )
                    if expected is not None and actual != expected:
                        raise ValueError(
                            f"result mismatch: expected {expected.hex()}, got {actual.hex() if actual is not None else None}"
                        )
                    if ticks % 2:
                        raise ValueError("non-integral normal-speed T-cycle count")
                    return {
                        "status": "ok",
                        "t_cycles": ticks // 2,
                        "registers": {
                            name: getattr(regs, name) for name, _ in Registers._fields_
                        },
                        "output": actual.hex() if actual is not None else None,
                        "instructions_run": instructions,
                    }
                elapsed = self.lib.GB_run(gb)
                if active:
                    ticks += elapsed
            raise ValueError(
                f"execution limit reached after {limit} instructions; pc={regs.pc:04x}"
            )
        finally:
            self.lib.GB_dealloc(gb)


def assemble(source, directory):
    text = Path(source).read_text()
    if "SECTION" not in text:
        text = 'SECTION "cycle probe", ROM0[$200]\n' + text
    asm, obj, rom, symbols = [
        directory / name for name in ("probe.asm", "probe.o", "probe.gb", "probe.sym")
    ]
    asm.write_text(text)
    for command in [
        ["rgbasm", "-o", obj, asm],
        ["rgblink", "-n", symbols, "-o", rom, obj],
    ]:
        subprocess.run(command, check=True, capture_output=True, text=True)
    names = {
        line.split()[1]: int(line.split()[0].split(":")[1], 16)
        for line in symbols.read_text().splitlines()
        if line and not line.startswith(";")
    }
    return rom.read_bytes(), names


def main():
    parser = argparse.ArgumentParser(
        description="Execute a linked RGBDS assembly snippet for explicit register inputs and count T-cycles."
    )
    parser.add_argument("assembly", type=Path)
    parser.add_argument("--entry", required=True)
    parser.add_argument("--reg", action="append", default=[], metavar="PAIR=VALUE")
    parser.add_argument("--expect", action="append", default=[], metavar="PAIR=VALUE")
    parser.add_argument("--sameboy-library", type=Path, default=DEFAULT_LIBRARY)
    parser.add_argument("--limit", type=int, default=1_000_000)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory() as temporary:
        rom, symbols = assemble(args.assembly, Path(temporary))
        if args.entry not in symbols:
            parser.error(f"entry symbol not found: {args.entry}")

        def assignments(pairs):
            return {
                name: int(value, 0) for name, value in (p.split("=", 1) for p in pairs)
            }

        result = SameBoy(args.sameboy_library).run(
            rom, symbols[args.entry], registers=assignments(args.reg), limit=args.limit
        )
        for name, value in assignments(args.expect).items():
            if result["registers"].get(name) != value:
                parser.error(
                    f"unexpected {name}: {result['registers'].get(name)}, expected {value}"
                )
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
