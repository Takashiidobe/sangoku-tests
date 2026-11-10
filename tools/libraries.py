import hashlib
from pathlib import Path
import re
import subprocess

from sm83 import disassemble, read_ihx

ROM_AREAS = {"_CODE", "_HOME", "_INITIALIZER", "_GSINIT", "_GSFINAL", "_CONST"}


def parse_rel(text):
    areas = {
        name: int(size, 16)
        for name, size in re.findall(r"^A (\S+) size ([0-9a-fA-F]+) ", text, re.M)
    }
    definitions = set(re.findall(r"^S (\S+) Def[0-9a-fA-F]+$", text, re.M)) - {
        ".__.ABS."
    }
    references = set(re.findall(r"^S (\S+) Ref[0-9a-fA-F]+$", text, re.M))
    return {
        "code_bytes": sum(size for name, size in areas.items() if name in ROM_AREAS),
        "areas": areas,
        "definitions": sorted(definitions),
        "references": sorted(references),
    }


class SdccLibrary:
    def __init__(self, sdcc, work, archive=None):
        if archive is None:
            search = subprocess.run(
                [sdcc, "-msm83", "--print-search-dirs"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout
            paths = search.split("libdir:\n", 1)[1].split("libpath:", 1)[0].splitlines()
            archive = next(
                (
                    Path(p) / "sm83.lib"
                    for p in paths
                    if (Path(p) / "sm83.lib").is_file()
                ),
                None,
            )
        if archive is None:
            raise ValueError("SDCC sm83.lib not found")
        self.archive = Path(archive).resolve()
        self.sha256 = hashlib.sha256(self.archive.read_bytes()).hexdigest()
        self.work = work.resolve()
        self.work.mkdir(parents=True, exist_ok=True)
        listing = subprocess.run(
            ["sdar", "-t", str(self.archive)],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
        subprocess.run(
            ["sdar", "-x", str(self.archive)],
            cwd=self.work,
            check=True,
            capture_output=True,
        )
        self.modules = {}
        self.exports = {}
        for member in listing:
            path = self.work / member
            module = parse_rel(path.read_text())
            module.update(
                {
                    "member": member,
                    "object_path": str(path),
                    "object_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                }
            )
            self.modules[member] = module
            for symbol in module["definitions"]:
                self.exports.setdefault(symbol, member)

    def resolve(self, symbols):
        pending = list(symbols)
        selected = set()
        missing = set()
        while pending:
            symbol = pending.pop()
            member = self.exports.get(symbol)
            if member is None:
                missing.add(symbol)
            elif member not in selected:
                selected.add(member)
                pending.extend(self.modules[member]["references"])
        modules = [self.modules[name] for name in sorted(selected)]
        return {
            "status": "partial" if missing else "ok",
            "measurement": "installed SDCC archive object ROM areas; transitive members counted once; section alignment excluded",
            "archive": str(self.archive),
            "archive_sha256": self.sha256,
            "dependency_bytes": sum(m["code_bytes"] for m in modules),
            "modules": modules,
            "unresolved_symbols": sorted(missing),
        }


def rust_map_sections(text):
    sections = []
    region = ""
    for line in text.splitlines():
        if re.match(r"^[A-Z0-9]+ bank #", line):
            region = line.split()[0]
        match = re.search(r'SECTION:.*\(\$([0-9a-fA-F]+) bytes?\) \["([^"]+)"\]', line)
        if match and region in {"ROM0", "ROMX"}:
            sections.append({"name": match[2], "bytes": int(match[1], 16)})
    return sections


def measure_rust_link(case, mode, args, work, run):
    work.mkdir(parents=True, exist_ok=True)
    source = work / "linked_case.rs"
    source.write_text(
        case.get("rust_header", "#![no_std]\n")
        + "\n\n"
        + "\n\n".join(
            h["rust_function"]
            for h in case.get("support_functions", [])
            if "rust" in h.get("languages", ["c", "rust"])
        )
        + "\n\n"
        + case["rust_function"]
        + "\n\n"
        + case["link_entry"]
        + "\n"
    )
    result = run(
        [
            args.sangoku,
            "build",
            source,
            work / "case.gb",
            "--opt-level",
            "z" if mode == "size" else "3",
        ],
        timeout=args.timeout,
    )
    if result["returncode"] != 0:
        return {"status": "error", "diagnostic": result["stderr"]}, result
    match = re.search(r"Build artifacts: (.+)", result["stderr"])
    if not match:
        return {
            "status": "error",
            "diagnostic": "sangoku did not report the build artifacts directory",
        }, result
    artifacts = Path(match[1].strip())
    sections = rust_map_sections((artifacts / "probe.map").read_text())
    excluded = {
        "Startup",
        "Cartridge entry",
        "Unreachable trap vector",
        "__rust_gbc_main",
    }
    root_name = "__rust_" + case["id"]
    root = next((s for s in sections if s["name"] == root_name), None)
    if root is None:
        return {
            "status": "error",
            "diagnostic": "linked case section missing from map",
        }, result
    dependencies = [s for s in sections if s["name"] not in excluded | {root_name}]
    assembly = (artifacts / "probe.asm").read_text()
    repo = Path(args.sangoku).resolve().parents[2]
    for obj in artifacts.glob("*.o"):
        catalog = repo / "src/runtime"
        if catalog.is_dir():
            for file in catalog.glob("*.rs"):
                found = re.search(
                    rf'object!\(\s*"{re.escape(obj.stem)}"\s*,\s*"([^"]+)"\s*\)',
                    file.read_text(),
                )
                if found and (repo / found[1]).is_file():
                    assembly += "\n" + (repo / found[1]).read_text()
    body_index = {
        name: body
        for name, body in re.findall(
            r'^SECTION\s+"([^"]+)"[^\n]*\n(.*?)(?=^SECTION\s|\Z)', assembly, re.M | re.S
        )
    }
    for section in dependencies:
        section["assembly"] = body_index.get(section["name"])
    return {
        "status": "ok",
        "measurement": "isolated sangoku build: reachable ROM sections in probe.map; entry, cartridge header and startup excluded; section alignment excluded",
        "root_function_bytes": root["bytes"],
        "dependency_bytes": sum(s["bytes"] for s in dependencies),
        "total_bytes": root["bytes"] + sum(s["bytes"] for s in dependencies),
        "sections": dependencies,
        "map_path": str(artifacts / "probe.map"),
        "assembly_path": str(artifacts / "probe.asm"),
    }, result


def measure_sdcc_link(case, mode, args, work, library, run):
    work.mkdir(parents=True, exist_ok=True)
    source = work / "linked_case.c"
    source.write_text(
        case.get("c_header", "#include <stdint.h>\n#include <string.h>\n")
        + "\n\n"
        + "\n\n".join(
            h["c_function"]
            for h in case.get("support_functions", [])
            if "c" in h.get("languages", ["c", "rust"])
        )
        + "\n\n"
        + case["c_function"]
        + "\n"
    )
    rel = work / "case.rel"
    logs = []
    for command in [
        [
            args.sdcc,
            "-msm83",
            "--std-c11",
            "--Werror",
            "--disable-warning",
            "110",
            "--opt-code-" + mode,
            "-c",
            source,
            "-o",
            rel,
        ],
        [
            args.sdcc,
            "-msm83",
            "--no-std-crt0",
            "--code-loc",
            "0x0200",
            "--data-loc",
            "0xc000",
            rel,
            "-o",
            work / "case.ihx",
        ],
    ]:
        outcome = run(command, timeout=args.timeout)
        logs.append(outcome)
        if outcome["returncode"] != 0:
            return {**library, "status": "error", "diagnostic": outcome["stderr"]}, logs
    text = (work / "case.map").read_text()
    areas = {
        name: int(size)
        for name, size in re.findall(
            r"^(\S+)\s+[0-9a-fA-F]+\s+[0-9a-fA-F]+\s+=\s+(\d+)\. bytes", text, re.M
        )
    }
    total = sum(size for name, size in areas.items() if name in ROM_AREAS)
    object_bytes = parse_rel(rel.read_text())["code_bytes"]
    estimate = object_bytes + library["dependency_bytes"]
    from compare import measure_sdcc

    root_id = case.get("id")
    if root_id is None:
        match = re.search(r"\b([A-Za-z_]\w*)\s*\(", case["c_function"])
        if match is None:
            raise ValueError("cannot identify the linked C function")
        root_id = match[1]
    root = measure_sdcc(work / "case.asm", rel, [{"id": root_id}])[root_id][
        "function_bytes"
    ]
    if total != estimate:
        return {
            **library,
            "status": "error",
            "diagnostic": f"archive estimate {estimate} disagrees with linked ROM bytes {total}",
        }, logs
    memory = read_ihx((work / "case.ihx").read_text())
    modules = disassemble_sdcc_modules(library["modules"], text, memory)
    return {
        **library,
        "measurement": "isolated SDCC link map ROM areas; no CRT, entry harness or section alignment; verified against transitive archive member sizes",
        "total_bytes": total,
        "root_function_bytes": root,
        "dependency_bytes": total - root,
        "archive_dependency_bytes": library["dependency_bytes"],
        "map_path": str(work / "case.map"),
        "archive_estimate_verified": True,
        "modules": modules,
    }, logs


def disassemble_sdcc_modules(originals, map_text, memory):
    addresses = {
        symbol: int(address, 16)
        for address, symbol in re.findall(
            r"^\s+([0-9a-fA-F]{8})\s+(_\w+)(?:\s|$)", map_text, re.M
        )
    }
    modules = []
    for original in originals:
        module = dict(original)
        area = None
        origins = {}
        for line in Path(module["object_path"]).read_text().splitlines():
            if line.startswith("A "):
                area = line.split()[1]
            match = re.fullmatch(r"S (\S+) Def([0-9a-fA-F]+)", line)
            if match and area in ROM_AREAS and match[1] in addresses:
                origins.setdefault(area, addresses[match[1]] - int(match[2], 16))
        decoded_areas = []
        unresolved = []
        for area, size in module["areas"].items():
            if area not in ROM_AREAS or not size:
                continue
            if area not in origins:
                unresolved.append(area)
                continue
            origin = origins[area]
            data = bytes(memory[origin + offset] for offset in range(size))
            decoded = disassemble(data, origin)
            decoded_areas.append(
                {
                    "area": area,
                    "address": origin,
                    "bytes": size,
                    "assembly": "\n".join(
                        f"{item['address']:04x}: {item['bytes']:<6} {item['instruction']}"
                        for item in decoded
                    ),
                }
            )
        module["disassembly_areas"] = decoded_areas
        module["unresolved_rom_areas"] = unresolved
        module["data_only"] = module["code_bytes"] == 0
        if decoded_areas:
            module["linked_address"] = decoded_areas[0]["address"]
            module["assembly"] = "\n\n".join(
                f"{part['area']} @ ${part['address']:04x}\n{part['assembly']}"
                for part in decoded_areas
            )
            module["disassembly_note"] = (
                "linear decode of actual linked ROM-area bytes; embedded data is not distinguished; no cycle estimates"
            )
        modules.append(module)
    return modules
