#include <stdint.h>
_Static_assert(sizeof(uint8_t) * 8 == 8, "required width: u8");

uint8_t u8_add(uint8_t a, uint8_t b) {
  return (uint8_t)((uint32_t)(uint8_t)a + (uint32_t)(uint8_t)b);
}

uint8_t u8_sub(uint8_t a, uint8_t b) {
  return (uint8_t)((uint32_t)(uint8_t)a - (uint32_t)(uint8_t)b);
}

uint8_t u8_mul(uint8_t a, uint8_t b) {
  return (uint8_t)((uint32_t)(uint8_t)a * (uint32_t)(uint8_t)b);
}

uint8_t u8_mulhi(uint8_t a, uint8_t b) {
  return (uint8_t)(((uint16_t)a * (uint16_t)b) >> 8);
}

uint8_t u8_div(uint8_t a, uint8_t b) { return a / b; }

uint8_t u8_rem(uint8_t a, uint8_t b) { return a % b; }

uint8_t u8_and(uint8_t a, uint8_t b) { return a & b; }

uint8_t u8_or(uint8_t a, uint8_t b) { return a | b; }

uint8_t u8_xor(uint8_t a, uint8_t b) { return a ^ b; }

uint8_t u8_eq(uint8_t a, uint8_t b) { return a == b; }

uint8_t u8_ne(uint8_t a, uint8_t b) { return a != b; }

uint8_t u8_lt(uint8_t a, uint8_t b) { return a < b; }

uint8_t u8_le(uint8_t a, uint8_t b) { return a <= b; }

uint8_t u8_gt(uint8_t a, uint8_t b) { return a > b; }

uint8_t u8_ge(uint8_t a, uint8_t b) { return a >= b; }

uint8_t u8_min(uint8_t a, uint8_t b) { return a < b ? a : b; }

uint8_t u8_max(uint8_t a, uint8_t b) { return a > b ? a : b; }

uint8_t u8_not(uint8_t a) { return ~a; }

uint8_t u8_neg(uint8_t a) { return (uint8_t)(0 - (uint32_t)(uint8_t)a); }

uint8_t u8_add1(uint8_t a) { return (uint8_t)((uint32_t)(uint8_t)a + 1); }

uint8_t u8_mul3(uint8_t a) { return (uint8_t)((uint32_t)(uint8_t)a * 3); }

uint8_t u8_mul10(uint8_t a) { return (uint8_t)((uint32_t)(uint8_t)a * 10); }

uint8_t u8_div3(uint8_t a) { return a / 3; }

uint8_t u8_rem10(uint8_t a) { return a % 10; }

uint8_t u8_shl(uint8_t a, uint8_t b) {
  return (uint8_t)((uint32_t)(uint8_t)a << (b & 7));
}

uint8_t u8_shl1(uint8_t a) { return (uint8_t)((uint32_t)(uint8_t)a << 1); }

uint8_t u8_shl7(uint8_t a) { return (uint8_t)((uint32_t)(uint8_t)a << 7); }

uint8_t u8_shr(uint8_t a, uint8_t b) { return (uint8_t)(a >> (b & 7)); }

uint8_t u8_shr1(uint8_t a) { return (uint8_t)(a >> 1); }

uint8_t u8_shr7(uint8_t a) { return (uint8_t)(a >> 7); }

uint8_t u8_rol(uint8_t a, uint8_t b) {
  return (uint8_t)(((uint32_t)(uint8_t)a << (b & 7)) |
                   ((uint32_t)(uint8_t)a >> ((0u - (b & 7)) & 7)));
}

uint8_t u8_ror(uint8_t a, uint8_t b) {
  return (uint8_t)(((uint32_t)(uint8_t)a >> (b & 7)) |
                   ((uint32_t)(uint8_t)a << ((0u - (b & 7)) & 7)));
}

int8_t u8_as_signed(uint8_t a) { return (int8_t)a; }

uint8_t u8_as_unsigned(uint8_t a) { return (uint8_t)a; }

uint16_t u8_widen(uint8_t a) { return (uint16_t)a; }
