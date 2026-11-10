#include <stdint.h>
_Static_assert(sizeof(int8_t) * 8 == 8, "required width: i8");
_Static_assert((-1 >> 1) == -1, "arithmetic signed right shift required");

int8_t i8_add(int8_t a, int8_t b) {
  return (int8_t)((uint32_t)(uint8_t)a + (uint32_t)(uint8_t)b);
}

int8_t i8_sub(int8_t a, int8_t b) {
  return (int8_t)((uint32_t)(uint8_t)a - (uint32_t)(uint8_t)b);
}

int8_t i8_mul(int8_t a, int8_t b) {
  return (int8_t)((uint32_t)(uint8_t)a * (uint32_t)(uint8_t)b);
}

int8_t i8_div(int8_t a, int8_t b) { return a / b; }

int8_t i8_rem(int8_t a, int8_t b) { return a % b; }

int8_t i8_and(int8_t a, int8_t b) { return a & b; }

int8_t i8_or(int8_t a, int8_t b) { return a | b; }

int8_t i8_xor(int8_t a, int8_t b) { return a ^ b; }

uint8_t i8_eq(int8_t a, int8_t b) { return a == b; }

uint8_t i8_ne(int8_t a, int8_t b) { return a != b; }

uint8_t i8_lt(int8_t a, int8_t b) { return a < b; }

uint8_t i8_le(int8_t a, int8_t b) { return a <= b; }

uint8_t i8_gt(int8_t a, int8_t b) { return a > b; }

uint8_t i8_ge(int8_t a, int8_t b) { return a >= b; }

int8_t i8_min(int8_t a, int8_t b) { return a < b ? a : b; }

int8_t i8_max(int8_t a, int8_t b) { return a > b ? a : b; }

int8_t i8_not(int8_t a) { return ~a; }

int8_t i8_neg(int8_t a) { return (int8_t)(0 - (uint32_t)(uint8_t)a); }

int8_t i8_add1(int8_t a) { return (int8_t)((uint32_t)(uint8_t)a + 1); }

int8_t i8_mul3(int8_t a) { return (int8_t)((uint32_t)(uint8_t)a * 3); }

int8_t i8_mul10(int8_t a) { return (int8_t)((uint32_t)(uint8_t)a * 10); }

int8_t i8_div3(int8_t a) { return a / 3; }

int8_t i8_rem10(int8_t a) { return a % 10; }

int8_t i8_shl(int8_t a, uint8_t b) {
  return (int8_t)((uint32_t)(uint8_t)a << (b & 7));
}

int8_t i8_shl1(int8_t a) { return (int8_t)((uint32_t)(uint8_t)a << 1); }

int8_t i8_shl7(int8_t a) { return (int8_t)((uint32_t)(uint8_t)a << 7); }

int8_t i8_shr(int8_t a, uint8_t b) { return (int8_t)(a >> (b & 7)); }

int8_t i8_shr1(int8_t a) { return (int8_t)(a >> 1); }

int8_t i8_shr7(int8_t a) { return (int8_t)(a >> 7); }

int8_t i8_rol(int8_t a, uint8_t b) {
  return (int8_t)(((uint32_t)(uint8_t)a << (b & 7)) |
                  ((uint32_t)(uint8_t)a >> ((0u - (b & 7)) & 7)));
}

int8_t i8_ror(int8_t a, uint8_t b) {
  return (int8_t)(((uint32_t)(uint8_t)a >> (b & 7)) |
                  ((uint32_t)(uint8_t)a << ((0u - (b & 7)) & 7)));
}

int8_t i8_as_signed(int8_t a) { return (int8_t)a; }

uint8_t i8_as_unsigned(int8_t a) { return (uint8_t)a; }

int16_t i8_widen(int8_t a) { return (int16_t)a; }
