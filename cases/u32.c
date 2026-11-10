#include <stdint.h>
_Static_assert(sizeof(uint32_t) * 8 == 32, "required width: u32");

uint32_t u32_add(uint32_t a, uint32_t b) {
  return (uint32_t)((uint32_t)(uint32_t)a + (uint32_t)(uint32_t)b);
}

uint32_t u32_sub(uint32_t a, uint32_t b) {
  return (uint32_t)((uint32_t)(uint32_t)a - (uint32_t)(uint32_t)b);
}

uint32_t u32_mul(uint32_t a, uint32_t b) {
  return (uint32_t)((uint32_t)(uint32_t)a * (uint32_t)(uint32_t)b);
}

uint32_t u32_div(uint32_t a, uint32_t b) { return a / b; }

uint32_t u32_rem(uint32_t a, uint32_t b) { return a % b; }

uint32_t u32_and(uint32_t a, uint32_t b) { return a & b; }

uint32_t u32_or(uint32_t a, uint32_t b) { return a | b; }

uint32_t u32_xor(uint32_t a, uint32_t b) { return a ^ b; }

uint8_t u32_eq(uint32_t a, uint32_t b) { return a == b; }

uint8_t u32_ne(uint32_t a, uint32_t b) { return a != b; }

uint8_t u32_lt(uint32_t a, uint32_t b) { return a < b; }

uint8_t u32_le(uint32_t a, uint32_t b) { return a <= b; }

uint8_t u32_gt(uint32_t a, uint32_t b) { return a > b; }

uint8_t u32_ge(uint32_t a, uint32_t b) { return a >= b; }

uint32_t u32_min(uint32_t a, uint32_t b) { return a < b ? a : b; }

uint32_t u32_max(uint32_t a, uint32_t b) { return a > b ? a : b; }

uint32_t u32_not(uint32_t a) { return ~a; }

uint32_t u32_neg(uint32_t a) { return (uint32_t)(0 - (uint32_t)(uint32_t)a); }

uint32_t u32_add1(uint32_t a) { return (uint32_t)((uint32_t)(uint32_t)a + 1); }

uint32_t u32_mul3(uint32_t a) { return (uint32_t)((uint32_t)(uint32_t)a * 3); }

uint32_t u32_mul10(uint32_t a) {
  return (uint32_t)((uint32_t)(uint32_t)a * 10);
}

uint32_t u32_div3(uint32_t a) { return a / 3; }

uint32_t u32_rem10(uint32_t a) { return a % 10; }

uint32_t u32_shl(uint32_t a, uint8_t b) {
  return (uint32_t)((uint32_t)(uint32_t)a << (b & 31));
}

uint32_t u32_shl1(uint32_t a) { return (uint32_t)((uint32_t)(uint32_t)a << 1); }

uint32_t u32_shl7(uint32_t a) { return (uint32_t)((uint32_t)(uint32_t)a << 7); }

uint32_t u32_shr(uint32_t a, uint8_t b) { return (uint32_t)(a >> (b & 31)); }

uint32_t u32_shr1(uint32_t a) { return (uint32_t)(a >> 1); }

uint32_t u32_shr7(uint32_t a) { return (uint32_t)(a >> 7); }

uint32_t u32_rol(uint32_t a, uint8_t b) {
  return (uint32_t)(((uint32_t)(uint32_t)a << (b & 31)) |
                    ((uint32_t)(uint32_t)a >> ((0u - (b & 31)) & 31)));
}

uint32_t u32_ror(uint32_t a, uint8_t b) {
  return (uint32_t)(((uint32_t)(uint32_t)a >> (b & 31)) |
                    ((uint32_t)(uint32_t)a << ((0u - (b & 31)) & 31)));
}

int32_t u32_as_signed(uint32_t a) { return (int32_t)a; }

uint32_t u32_as_unsigned(uint32_t a) { return (uint32_t)a; }

uint16_t u32_narrow(uint32_t a) { return (uint16_t)a; }

uint64_t u32_widen(uint32_t a) { return (uint64_t)a; }
