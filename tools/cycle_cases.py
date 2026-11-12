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
        "u8_mulhi": [(0, 255), (127, 255), (128, 128), (255, 255)],
        "i8_mulhi": [(0, 255), (128, 255), (127, 127), (129, 3)],
        "u16_mulhi": [(0, 65535), (1, 65535), (32768, 65535), (65535, 65535)],
        "i16_mulhi": [(0, 65535), (32768, 65535), (32767, 32767), (4660, 43981)],
        "i16_mulhi_u16": [(32768, 65535), (32767, 65535), (4660, 43981)],
        "u16_mul_u8": [(0, 65535), (255, 65535), (256, 3), (65535, 7)],
        "u16_mul_loop": [(0, 0), (7, 1), (7, 4), (65535, 16), (1234, 64)],
        "u16_mul3": [(0,), (7,), (65535,)],
        "u16_div": [(0, 1), (1, 1), (2, 3), (3, 3), (4, 3), (65535, 2), (65535, 255), (65535, 256), (65535, 257), (65535, 32768), (65535, 65535)],
        "u16_rem": [(0, 1), (1, 1), (2, 3), (3, 3), (4, 3), (65535, 2), (65535, 255), (65535, 256), (65535, 257), (65535, 32768), (65535, 65535)],
        "i16_div": [(0, 1), (1, 1), (65535, 1), (100, 3), (65436, 3), (100, 65533), (65436, 65533), (32768, 2), (32767, 65534), (65535, 65535)],
        "i16_rem": [(0, 1), (1, 1), (65535, 1), (100, 3), (65436, 3), (100, 65533), (65436, 65533), (32768, 2), (32767, 65534), (65535, 65535)],
        "u16_divrem_xor": [(0, 3), (65535, 1), (65535, 3), (65535, 255)],
        "u16_div1": [(0,), (1,), (65535,)],
        "u16_div2": [(0,), (1,), (65535,)],
        "u16_div256": [(0,), (255,), (256,), (65535,)],
        "u16_rem256": [(0,), (255,), (256,), (65535,)],
        "u16_div255": [(0,), (1,), (254,), (255,), (256,), (65535,)],
        "u16_rem255": [(0,), (1,), (254,), (255,), (256,), (65535,)],
        "u16_div257": [(0,), (1,), (256,), (257,), (258,), (65535,)],
        "u16_rem257": [(0,), (1,), (256,), (257,), (258,), (65535,)],
        "i16_div255": [(32768,), (65436,), (65535,), (0,), (32767,)],
        "i16_rem255": [(32768,), (65436,), (65535,), (0,), (32767,)],
        "i16_div257": [(32768,), (65436,), (65535,), (0,), (32767,)],
        "i16_rem257": [(32768,), (65436,), (65535,), (0,), (32767,)],
        "u16_div3": [(0,), (2,), (3,), (255,), (65535,)],
        "u16_rem10": [(0,), (9,), (10,), (65535,)],
    }
    if name not in examples:
        return []
    mask = (1 << case["width"]) - 1

    def signed(v):
        sign = 1 << (case["width"] - 1)
        return (v ^ sign) - sign

    def trunc_div(lhs, rhs):
        quotient = abs(lhs) // abs(rhs)
        return -quotient if (lhs < 0) != (rhs < 0) else quotient

    result = []
    for values in examples[name]:
        a, b = values[0], values[1] if len(values) == 2 else 0
        operation = case["operation"]
        expected = {
            "add": lambda: (a + b) & mask,
            "eq": lambda: int(a == b),
            "min": lambda: min(a, b),
            "mul": lambda: a * b & mask,
            "mulhi": lambda: (
                (
                    ((a ^ (1 << (case["width"] - 1))) - (1 << (case["width"] - 1)))
                    * ((b ^ (1 << (case["width"] - 1))) - (1 << (case["width"] - 1)))
                    >> case["width"]
                )
                & mask
                if case["signed"]
                else (a * b >> case["width"]) & mask
            ),
            "mulhi_u16": lambda: ((signed(a) * b) >> case["width"]) & mask,
            "mul_u8": lambda: (a & 255) * b & mask,
            "mul_loop": lambda: sum(a * i for i in range(b)) & mask,
            "mul3": lambda: a * 3 & mask,
            "div": lambda: (trunc_div(signed(a), signed(b)) if case["signed"] else a // b) & mask,
            "rem": lambda: (signed(a) - trunc_div(signed(a), signed(b)) * signed(b)) & mask if case["signed"] else a % b,
            "divrem_xor": lambda: (a // b) ^ (a % b),
            "div1": lambda: a,
            "div2": lambda: a // 2,
            "div256": lambda: a // 256,
            "rem256": lambda: a % 256,
            "div255": lambda: (trunc_div(signed(a), 255) if case["signed"] else a // 255) & mask,
            "rem255": lambda: (signed(a) - trunc_div(signed(a), 255) * 255) & mask if case["signed"] else a % 255,
            "div257": lambda: (trunc_div(signed(a), 257) if case["signed"] else a // 257) & mask,
            "rem257": lambda: (signed(a) - trunc_div(signed(a), 257) * 257) & mask if case["signed"] else a % 257,
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
