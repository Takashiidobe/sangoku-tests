import re


def code_lines(assembly):
    result = []
    for number, raw in enumerate(assembly.splitlines(), 1):
        line = re.sub(r"\s+", " ", raw.split(";", 1)[0].strip().lower())
        if (
            line
            and not line.endswith(":")
            and not line.startswith((".", "export ", "section ", "def "))
        ):
            result.append((number, line))
    return result


def stack_metrics(assembly):
    lines = code_lines(assembly)
    reservations = []
    loads = []
    stores = []
    indirect = []
    for index, (number, line) in enumerate(lines):
        reserve = re.fullmatch(r"add sp,\s*#?(-(?:0x[0-9a-f]+|\d+))", line)
        if reserve:
            reservations.append({"line": number, "bytes": -int(reserve[1], 0)})
        if re.fullmatch(r"(?:call|jp|jr) (?:\(?hl\)?|\(?bc\)?|\(?de\)?)", line):
            indirect.append({"line": number, "instruction": line})
        if index + 1 < len(lines) and re.fullmatch(
            r"(?:ld hl, sp\s*\+\s*#?\S+|ldhl sp,\s*#?\S+)", line
        ):
            following = lines[index + 1]
            if any(
                v.strip().endswith(":")
                for v in assembly.splitlines()[number : following[0] - 1]
            ):
                continue
            normalized = following[1].replace("(", "[").replace(")", "]")
            if re.fullmatch(r"ld [abcdehl],\s*\[hl\+?\]", normalized):
                loads.append({"line": following[0], "instruction": following[1]})
            elif re.fullmatch(r"ld \[hl\+?\],\s*\S+", normalized):
                stores.append({"line": following[0], "instruction": following[1]})
    entry_reservation = 0
    for _, line in lines:
        if line.startswith("push "):
            continue
        match = re.fullmatch(r"add sp,\s*#?(-(?:0x[0-9a-f]+|\d+))", line)
        if match:
            entry_reservation -= int(match[1], 0)
        else:
            break
    return {
        "entry_add_sp_reservation_bytes": entry_reservation,
        "explicit_stack_reservations": reservations,
        "adjacent_stack_load_count": len(loads),
        "adjacent_stack_store_count": len(stores),
        "adjacent_stack_load_examples": loads[:4],
        "adjacent_stack_store_examples": stores[:4],
        "indirect_transfer_sites": indirect,
        "measurement_note": "source patterns only; leading add-sp reservation excludes pushes, return addresses and alternate frame setup; adjacent stack accesses are lower bounds, not proven spill counts or peak depth",
    }
