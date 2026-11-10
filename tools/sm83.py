REGISTERS = ["b", "c", "d", "e", "h", "l", "[hl]", "a"]
PAIRS = ["bc", "de", "hl", "sp"]
ALU = [
    "add a, {}",
    "adc a, {}",
    "sub {}",
    "sbc a, {}",
    "and {}",
    "xor {}",
    "or {}",
    "cp {}",
]
CONDITIONS = ["nz", "z", "nc", "c"]
SINGLE = {
    0x00: "nop",
    0x07: "rlca",
    0x0F: "rrca",
    0x17: "rla",
    0x1F: "rra",
    0x27: "daa",
    0x2F: "cpl",
    0x37: "scf",
    0x3F: "ccf",
    0xC9: "ret",
    0xD9: "reti",
    0xE2: "ldh [c], a",
    0xF2: "ldh a, [c]",
    0xE9: "jp hl",
    0xF3: "di",
    0xFB: "ei",
    0xF9: "ld sp, hl",
}


def decode(data, offset, address):
    op = data[offset]

    def byte():
        return data[offset + 1]

    def word():
        return data[offset + 1] | data[offset + 2] << 8

    def relative():
        return (address + 2 + (byte() if byte() < 128 else byte() - 256)) & 0xFFFF

    if op == 0xCB:
        code = byte()
        reg = REGISTERS[code & 7]
        if code < 64:
            return 2, ["rlc", "rrc", "rl", "rr", "sla", "sra", "swap", "srl"][
                code >> 3
            ] + " " + reg
        return 2, f"{['bit', 'res', 'set'][(code >> 6) - 1]} {(code >> 3) & 7}, {reg}"
    if op == 0x10:
        byte()
        return 2, "stop"
    if op == 0x08:
        return 3, f"ld [${word():04x}], sp"
    if op == 0x18:
        return 2, f"jr ${relative():04x}"
    if op in [0x20, 0x28, 0x30, 0x38]:
        return 2, f"jr {CONDITIONS[(op - 0x20) >> 3]}, ${relative():04x}"
    if op < 0x40:
        reg = REGISTERS[(op >> 3) & 7]
        pair = PAIRS[(op >> 4) & 3]
        if op & 0x0F == 1:
            return 3, f"ld {pair}, ${word():04x}"
        if op & 0x0F == 3:
            return 1, f"inc {pair}"
        if op & 0x0F == 9:
            return 1, f"add hl, {pair}"
        if op & 0x0F == 0x0B:
            return 1, f"dec {pair}"
        if op & 7 == 4:
            return 1, f"inc {reg}"
        if op & 7 == 5:
            return 1, f"dec {reg}"
        if op & 7 == 6:
            return 2, f"ld {reg}, ${byte():02x}"
        if op & 7 == 2:
            pointer = ["[bc]", "[de]", "[hli]", "[hld]"][(op >> 4) & 3]
            return 1, f"ld a, {pointer}" if op & 8 else f"ld {pointer}, a"
    if 0x40 <= op < 0x80:
        return (
            1,
            "halt"
            if op == 0x76
            else f"ld {REGISTERS[(op >> 3) & 7]}, {REGISTERS[op & 7]}",
        )
    if 0x80 <= op < 0xC0:
        return 1, ALU[(op >> 3) & 7].format(REGISTERS[op & 7])
    if op >= 0xC0:
        pair = ["bc", "de", "hl", "af"][(op >> 4) & 3]
        if op & 0x0F == 1:
            return 1, f"pop {pair}"
        if op & 0x0F == 5:
            return 1, f"push {pair}"
        if op & 7 == 6:
            return 2, ALU[(op >> 3) & 7].format(f"${byte():02x}")
        if op & 7 == 7:
            return 1, f"rst ${op & 0x38:02x}"
        if op < 0xE0:
            condition = CONDITIONS[(op >> 3) & 3]
            if op & 7 == 0:
                return 1, f"ret {condition}"
            if op & 7 == 2:
                return 3, f"jp {condition}, ${word():04x}"
            if op & 7 == 4:
                return 3, f"call {condition}, ${word():04x}"
        if op in [0xC3, 0xCD]:
            return 3, f"{'jp' if op == 0xC3 else 'call'} ${word():04x}"
        if op in [0xE0, 0xF0]:
            pointer = f"[${0xFF00 + byte():04x}]"
            return 2, f"ldh {pointer}, a" if op == 0xE0 else f"ldh a, {pointer}"
        if op in [0xEA, 0xFA]:
            pointer = f"[${word():04x}]"
            return 3, f"ld {pointer}, a" if op == 0xEA else f"ld a, {pointer}"
        if op in [0xE8, 0xF8]:
            value = byte() if byte() < 128 else byte() - 256
            return 2, f"add sp, {value}" if op == 0xE8 else f"ld hl, sp {value:+}"
    return 1, SINGLE.get(op, f"db ${op:02x}")


def disassemble(data, start):
    result = []
    offset = 0
    while offset < len(data):
        try:
            size, text = decode(data, offset, (start + offset) & 0xFFFF)
        except IndexError:
            size, text = 1, f"db ${data[offset]:02x}"
        result.append(
            {
                "address": (start + offset) & 0xFFFF,
                "bytes": data[offset : offset + size].hex(),
                "instruction": text,
            }
        )
        offset += size
    return result


def read_ihx(text):
    memory = {}
    base = 0
    for line in text.splitlines():
        if not line:
            continue
        if not line.startswith(":"):
            raise ValueError("invalid Intel HEX record")
        record = bytes.fromhex(line[1:])
        if len(record) != record[0] + 5 or sum(record) & 255:
            raise ValueError("invalid Intel HEX length or checksum")
        count, address, kind = record[0], record[1] << 8 | record[2], record[3]
        if kind == 0:
            memory.update(
                (base + address + i, value)
                for i, value in enumerate(record[4 : 4 + count])
            )
        elif kind == 1:
            break
        elif kind == 2:
            base = int.from_bytes(record[4:6], "big") << 4
        elif kind == 4:
            base = int.from_bytes(record[4:6], "big") << 16
    return memory
