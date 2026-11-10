#include <stdint.h>
_Static_assert(sizeof(int64_t) * 8 == 64, "required width: i64");
_Static_assert((-1 >> 1) == -1, "arithmetic signed right shift required");

int64_t i64_add(int64_t a, int64_t b) {
  return (int64_t)((uint64_t)(uint64_t)a + (uint64_t)(uint64_t)b);
}

int64_t i64_sub(int64_t a, int64_t b) {
  return (int64_t)((uint64_t)(uint64_t)a - (uint64_t)(uint64_t)b);
}

int64_t i64_mul(int64_t a, int64_t b) {
  return (int64_t)((uint64_t)(uint64_t)a * (uint64_t)(uint64_t)b);
}

int64_t i64_div(int64_t a, int64_t b) { return a / b; }

int64_t i64_rem(int64_t a, int64_t b) { return a % b; }

int64_t i64_and(int64_t a, int64_t b) { return a & b; }

int64_t i64_or(int64_t a, int64_t b) { return a | b; }

int64_t i64_xor(int64_t a, int64_t b) { return a ^ b; }

uint8_t i64_eq(int64_t a, int64_t b) { return a == b; }

uint8_t i64_ne(int64_t a, int64_t b) { return a != b; }

uint8_t i64_lt(int64_t a, int64_t b) { return a < b; }

uint8_t i64_le(int64_t a, int64_t b) { return a <= b; }

uint8_t i64_gt(int64_t a, int64_t b) { return a > b; }

uint8_t i64_ge(int64_t a, int64_t b) { return a >= b; }

int64_t i64_min(int64_t a, int64_t b) { return a < b ? a : b; }

int64_t i64_max(int64_t a, int64_t b) { return a > b ? a : b; }

int64_t i64_not(int64_t a) { return ~a; }

int64_t i64_neg(int64_t a) { return (int64_t)(0 - (uint64_t)(uint64_t)a); }

int64_t i64_add1(int64_t a) { return (int64_t)((uint64_t)(uint64_t)a + 1); }

int64_t i64_mul3(int64_t a) { return (int64_t)((uint64_t)(uint64_t)a * 3); }

int64_t i64_mul10(int64_t a) { return (int64_t)((uint64_t)(uint64_t)a * 10); }

int64_t i64_div3(int64_t a) { return a / 3; }

int64_t i64_rem10(int64_t a) { return a % 10; }

int64_t i64_shl(int64_t a, uint8_t b) {
  return (int64_t)((uint64_t)(uint64_t)a << (b & 63));
}

int64_t i64_shl1(int64_t a) { return (int64_t)((uint64_t)(uint64_t)a << 1); }

int64_t i64_shl7(int64_t a) { return (int64_t)((uint64_t)(uint64_t)a << 7); }

int64_t i64_shr(int64_t a, uint8_t b) { return (int64_t)(a >> (b & 63)); }

int64_t i64_shr1(int64_t a) { return (int64_t)(a >> 1); }

int64_t i64_shr7(int64_t a) { return (int64_t)(a >> 7); }

int64_t i64_rol(int64_t a, uint8_t b) {
  return (int64_t)(((uint64_t)(uint64_t)a << (b & 63)) |
                   ((uint64_t)(uint64_t)a >> ((0u - (b & 63)) & 63)));
}

int64_t i64_ror(int64_t a, uint8_t b) {
  return (int64_t)(((uint64_t)(uint64_t)a >> (b & 63)) |
                   ((uint64_t)(uint64_t)a << ((0u - (b & 63)) & 63)));
}

int64_t i64_as_signed(int64_t a) { return (int64_t)a; }

uint64_t i64_as_unsigned(int64_t a) { return (uint64_t)a; }

uint32_t i64_narrow(int64_t a) { return (uint32_t)a; }
