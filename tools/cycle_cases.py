def subcases(case):
    name = case["id"]
    if name == "strings_strlen_loop":
        return [
            {
                "input": f"s={text!r}",
                "args": [0xC300],
                "memory": {0xC300: text.encode() + b"\0"},
                "expected": len(text),
            }
            for text in ("", "a", "Game Boy", "x" * 32)
        ]
    examples = {
        "u8_add": [(0, 0), (1, 2), (255, 1)],
        "u8_eq": [(0, 0), (1, 2), (255, 255)],
        "u8_min": [(0, 255), (255, 0), (7, 7)],
        "u8_mul3": [(0,), (7,), (255,)],
        "u8_shl": [(1, 0), (1, 1), (1, 7), (255, 7)],
        "u8_shl7": [(0,), (1,), (255,)],
        "u16_add": [(0, 0), (255, 1), (65535, 1)],
        "u16_mul": [(0, 0), (1, 65535), (7, 3), (65535, 65535)],
        "u16_mul3": [(0,), (7,), (65535,)],
        "u16_div": [(0, 3), (65535, 1), (65535, 3), (65535, 65535)],
        "u16_div3": [(0,), (2,), (3,), (255,), (65535,)],
        "u16_rem10": [(0,), (9,), (10,), (65535,)],
    }
    if name not in examples:
        return []
    mask = (1 << case["width"]) - 1
    result = []
    for values in examples[name]:
        a, b = values[0], values[1] if len(values) == 2 else 0
        operation = case["operation"]
        expected = {
            "add": lambda: (a + b) & mask,
            "eq": lambda: int(a == b),
            "min": lambda: min(a, b),
            "mul": lambda: a * b & mask,
            "mul3": lambda: a * 3 & mask,
            "div": lambda: a // b,
            "div3": lambda: a // 3,
            "rem10": lambda: a % 10,
            "shl": lambda: a << (b & (case["width"] - 1)) & mask,
            "shl7": lambda: a << 7 & mask,
        }[operation]()
        result.append(
            {
                "input": ", ".join(f"{n}={v}" for n, v in zip(("a", "b"), values)),
                "args": list(values),
                "memory": {},
                "expected": expected,
            }
        )
    return result
