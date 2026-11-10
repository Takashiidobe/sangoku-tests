#include <stdint.h>
_Static_assert(sizeof(uint64_t) * 8 == 64, "required width: u64");

uint64_t u64_add(uint64_t a, uint64_t b) {
  return (uint64_t)((uint64_t)(uint64_t)a + (uint64_t)(uint64_t)b);
}

uint64_t u64_sub(uint64_t a, uint64_t b) {
  return (uint64_t)((uint64_t)(uint64_t)a - (uint64_t)(uint64_t)b);
}

uint64_t u64_mul(uint64_t a, uint64_t b) {
  return (uint64_t)((uint64_t)(uint64_t)a * (uint64_t)(uint64_t)b);
}

uint64_t u64_div(uint64_t a, uint64_t b) { return a / b; }

uint64_t u64_rem(uint64_t a, uint64_t b) { return a % b; }

uint64_t u64_and(uint64_t a, uint64_t b) { return a & b; }

uint64_t u64_or(uint64_t a, uint64_t b) { return a | b; }

uint64_t u64_xor(uint64_t a, uint64_t b) { return a ^ b; }

uint8_t u64_eq(uint64_t a, uint64_t b) { return a == b; }

uint8_t u64_ne(uint64_t a, uint64_t b) { return a != b; }

uint8_t u64_lt(uint64_t a, uint64_t b) { return a < b; }

uint8_t u64_le(uint64_t a, uint64_t b) { return a <= b; }

uint8_t u64_gt(uint64_t a, uint64_t b) { return a > b; }

uint8_t u64_ge(uint64_t a, uint64_t b) { return a >= b; }

uint64_t u64_min(uint64_t a, uint64_t b) { return a < b ? a : b; }

uint64_t u64_max(uint64_t a, uint64_t b) { return a > b ? a : b; }

uint64_t u64_not(uint64_t a) { return ~a; }

uint64_t u64_neg(uint64_t a) { return (uint64_t)(0 - (uint64_t)(uint64_t)a); }

uint64_t u64_add1(uint64_t a) { return (uint64_t)((uint64_t)(uint64_t)a + 1); }

uint64_t u64_mul3(uint64_t a) { return (uint64_t)((uint64_t)(uint64_t)a * 3); }

uint64_t u64_mul10(uint64_t a) {
  return (uint64_t)((uint64_t)(uint64_t)a * 10);
}

uint64_t u64_div3(uint64_t a) { return a / 3; }

uint64_t u64_rem10(uint64_t a) { return a % 10; }

uint64_t u64_shl(uint64_t a, uint8_t b) {
  return (uint64_t)((uint64_t)(uint64_t)a << (b & 63));
}

uint64_t u64_shl1(uint64_t a) { return (uint64_t)((uint64_t)(uint64_t)a << 1); }

uint64_t u64_shl7(uint64_t a) { return (uint64_t)((uint64_t)(uint64_t)a << 7); }

uint64_t u64_shr(uint64_t a, uint8_t b) { return (uint64_t)(a >> (b & 63)); }

uint64_t u64_shr1(uint64_t a) { return (uint64_t)(a >> 1); }

uint64_t u64_shr7(uint64_t a) { return (uint64_t)(a >> 7); }

uint64_t u64_rol(uint64_t a, uint8_t b) {
  return (uint64_t)(((uint64_t)(uint64_t)a << (b & 63)) |
                    ((uint64_t)(uint64_t)a >> ((0u - (b & 63)) & 63)));
}

uint64_t u64_ror(uint64_t a, uint8_t b) {
  return (uint64_t)(((uint64_t)(uint64_t)a >> (b & 63)) |
                    ((uint64_t)(uint64_t)a << ((0u - (b & 63)) & 63)));
}

int64_t u64_as_signed(uint64_t a) { return (int64_t)a; }

uint64_t u64_as_unsigned(uint64_t a) { return (uint64_t)a; }

uint32_t u64_narrow(uint64_t a) { return (uint32_t)a; }
