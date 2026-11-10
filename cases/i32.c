#include <stdint.h>
_Static_assert(sizeof(int32_t) * 8 == 32, "required width: i32");
_Static_assert((-1 >> 1) == -1, "arithmetic signed right shift required");

int32_t i32_add(int32_t a, int32_t b) {
  return (int32_t)((uint32_t)(uint32_t)a + (uint32_t)(uint32_t)b);
}

int32_t i32_sub(int32_t a, int32_t b) {
  return (int32_t)((uint32_t)(uint32_t)a - (uint32_t)(uint32_t)b);
}

int32_t i32_mul(int32_t a, int32_t b) {
  return (int32_t)((uint32_t)(uint32_t)a * (uint32_t)(uint32_t)b);
}

int32_t i32_div(int32_t a, int32_t b) { return a / b; }

int32_t i32_rem(int32_t a, int32_t b) { return a % b; }

int32_t i32_and(int32_t a, int32_t b) { return a & b; }

int32_t i32_or(int32_t a, int32_t b) { return a | b; }

int32_t i32_xor(int32_t a, int32_t b) { return a ^ b; }

uint8_t i32_eq(int32_t a, int32_t b) { return a == b; }

uint8_t i32_ne(int32_t a, int32_t b) { return a != b; }

uint8_t i32_lt(int32_t a, int32_t b) { return a < b; }

uint8_t i32_le(int32_t a, int32_t b) { return a <= b; }

uint8_t i32_gt(int32_t a, int32_t b) { return a > b; }

uint8_t i32_ge(int32_t a, int32_t b) { return a >= b; }

int32_t i32_min(int32_t a, int32_t b) { return a < b ? a : b; }

int32_t i32_max(int32_t a, int32_t b) { return a > b ? a : b; }

int32_t i32_not(int32_t a) { return ~a; }

int32_t i32_neg(int32_t a) { return (int32_t)(0 - (uint32_t)(uint32_t)a); }

int32_t i32_add1(int32_t a) { return (int32_t)((uint32_t)(uint32_t)a + 1); }

int32_t i32_mul3(int32_t a) { return (int32_t)((uint32_t)(uint32_t)a * 3); }

int32_t i32_mul10(int32_t a) { return (int32_t)((uint32_t)(uint32_t)a * 10); }

int32_t i32_div3(int32_t a) { return a / 3; }

int32_t i32_rem10(int32_t a) { return a % 10; }

int32_t i32_shl(int32_t a, uint8_t b) {
  return (int32_t)((uint32_t)(uint32_t)a << (b & 31));
}

int32_t i32_shl1(int32_t a) { return (int32_t)((uint32_t)(uint32_t)a << 1); }

int32_t i32_shl7(int32_t a) { return (int32_t)((uint32_t)(uint32_t)a << 7); }

int32_t i32_shr(int32_t a, uint8_t b) { return (int32_t)(a >> (b & 31)); }

int32_t i32_shr1(int32_t a) { return (int32_t)(a >> 1); }

int32_t i32_shr7(int32_t a) { return (int32_t)(a >> 7); }

int32_t i32_rol(int32_t a, uint8_t b) {
  return (int32_t)(((uint32_t)(uint32_t)a << (b & 31)) |
                   ((uint32_t)(uint32_t)a >> ((0u - (b & 31)) & 31)));
}

int32_t i32_ror(int32_t a, uint8_t b) {
  return (int32_t)(((uint32_t)(uint32_t)a >> (b & 31)) |
                   ((uint32_t)(uint32_t)a << ((0u - (b & 31)) & 31)));
}

int32_t i32_as_signed(int32_t a) { return (int32_t)a; }

uint32_t i32_as_unsigned(int32_t a) { return (uint32_t)a; }

uint16_t i32_narrow(int32_t a) { return (uint16_t)a; }

int64_t i32_widen(int32_t a) { return (int64_t)a; }
