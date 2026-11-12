#include <stdint.h>
_Static_assert(sizeof(int16_t) * 8 == 16, "required width: i16");
_Static_assert((-1 >> 1) == -1, "arithmetic signed right shift required");

int16_t i16_add(int16_t a, int16_t b) {
  return (int16_t)((uint32_t)(uint16_t)a + (uint32_t)(uint16_t)b);
}

int16_t i16_sub(int16_t a, int16_t b) {
  return (int16_t)((uint32_t)(uint16_t)a - (uint32_t)(uint16_t)b);
}

int16_t i16_mul(int16_t a, int16_t b) {
  return (int16_t)((uint32_t)(uint16_t)a * (uint32_t)(uint16_t)b);
}

int16_t i16_mulhi(int16_t a, int16_t b) {
  return (int16_t)(((int32_t)a * (int32_t)b) >> 16);
}

uint16_t i16_mulhi_u16(int16_t a, uint16_t b) {
  return (uint16_t)(((int32_t)a * (int32_t)b) >> 16);
}

int16_t i16_div(int16_t a, int16_t b) { return a / b; }

int16_t i16_rem(int16_t a, int16_t b) { return a % b; }

int16_t i16_and(int16_t a, int16_t b) { return a & b; }

int16_t i16_or(int16_t a, int16_t b) { return a | b; }

int16_t i16_xor(int16_t a, int16_t b) { return a ^ b; }

uint8_t i16_eq(int16_t a, int16_t b) { return a == b; }

uint8_t i16_ne(int16_t a, int16_t b) { return a != b; }

uint8_t i16_lt(int16_t a, int16_t b) { return a < b; }

uint8_t i16_le(int16_t a, int16_t b) { return a <= b; }

uint8_t i16_gt(int16_t a, int16_t b) { return a > b; }

uint8_t i16_ge(int16_t a, int16_t b) { return a >= b; }

int16_t i16_min(int16_t a, int16_t b) { return a < b ? a : b; }

int16_t i16_max(int16_t a, int16_t b) { return a > b ? a : b; }

int16_t i16_not(int16_t a) { return ~a; }

int16_t i16_neg(int16_t a) { return (int16_t)(0 - (uint32_t)(uint16_t)a); }

int16_t i16_add1(int16_t a) { return (int16_t)((uint32_t)(uint16_t)a + 1); }

int16_t i16_mul3(int16_t a) { return (int16_t)((uint32_t)(uint16_t)a * 3); }

int16_t i16_mul10(int16_t a) { return (int16_t)((uint32_t)(uint16_t)a * 10); }

int16_t i16_div3(int16_t a) { return a / 3; }

int16_t i16_rem10(int16_t a) { return a % 10; }

int16_t i16_div255(int16_t a) { return a / 255; }

int16_t i16_rem255(int16_t a) { return a % 255; }

int16_t i16_div257(int16_t a) { return a / 257; }

int16_t i16_rem257(int16_t a) { return a % 257; }

int16_t i16_shl(int16_t a, uint8_t b) {
  return (int16_t)((uint32_t)(uint16_t)a << (b & 15));
}

int16_t i16_shl1(int16_t a) { return (int16_t)((uint32_t)(uint16_t)a << 1); }

int16_t i16_shl7(int16_t a) { return (int16_t)((uint32_t)(uint16_t)a << 7); }

int16_t i16_shr(int16_t a, uint8_t b) { return (int16_t)(a >> (b & 15)); }

int16_t i16_shr1(int16_t a) { return (int16_t)(a >> 1); }

int16_t i16_shr7(int16_t a) { return (int16_t)(a >> 7); }

int16_t i16_rol(int16_t a, uint8_t b) {
  return (int16_t)(((uint32_t)(uint16_t)a << (b & 15)) |
                   ((uint32_t)(uint16_t)a >> ((0u - (b & 15)) & 15)));
}

int16_t i16_ror(int16_t a, uint8_t b) {
  return (int16_t)(((uint32_t)(uint16_t)a >> (b & 15)) |
                   ((uint32_t)(uint16_t)a << ((0u - (b & 15)) & 15)));
}

int16_t i16_as_signed(int16_t a) { return (int16_t)a; }

uint16_t i16_as_unsigned(int16_t a) { return (uint16_t)a; }

uint8_t i16_narrow(int16_t a) { return (uint8_t)a; }

int32_t i16_widen(int16_t a) { return (int32_t)a; }
