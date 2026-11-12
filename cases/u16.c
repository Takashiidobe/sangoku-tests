#include <stdint.h>
_Static_assert(sizeof(uint16_t) * 8 == 16, "required width: u16");

uint16_t u16_add(uint16_t a, uint16_t b) {
  return (uint16_t)((uint32_t)(uint16_t)a + (uint32_t)(uint16_t)b);
}

uint16_t u16_sub(uint16_t a, uint16_t b) {
  return (uint16_t)((uint32_t)(uint16_t)a - (uint32_t)(uint16_t)b);
}

uint16_t u16_mul(uint16_t a, uint16_t b) {
  return (uint16_t)((uint32_t)(uint16_t)a * (uint32_t)(uint16_t)b);
}

uint16_t u16_mulhi(uint16_t a, uint16_t b) {
  return (uint16_t)(((uint32_t)a * (uint32_t)b) >> 16);
}

uint16_t u16_mul_u8(uint16_t a, uint16_t b) {
  return (uint16_t)((uint16_t)(uint8_t)a * b);
}

uint16_t u16_mul_loop(uint16_t a, uint8_t n) {
  uint16_t sum = 0;
  for (uint8_t i = 0; i < n; ++i) sum = (uint16_t)(sum + (uint16_t)(a * i));
  return sum;
}

uint16_t u16_div(uint16_t a, uint16_t b) { return a / b; }

uint16_t u16_rem(uint16_t a, uint16_t b) { return a % b; }

uint16_t u16_divrem_xor(uint16_t a, uint16_t b) {
  return (a / b) ^ (a % b);
}

uint16_t u16_and(uint16_t a, uint16_t b) { return a & b; }

uint16_t u16_or(uint16_t a, uint16_t b) { return a | b; }

uint16_t u16_xor(uint16_t a, uint16_t b) { return a ^ b; }

uint8_t u16_eq(uint16_t a, uint16_t b) { return a == b; }

uint8_t u16_ne(uint16_t a, uint16_t b) { return a != b; }

uint8_t u16_lt(uint16_t a, uint16_t b) { return a < b; }

uint8_t u16_le(uint16_t a, uint16_t b) { return a <= b; }

uint8_t u16_gt(uint16_t a, uint16_t b) { return a > b; }

uint8_t u16_ge(uint16_t a, uint16_t b) { return a >= b; }

uint16_t u16_min(uint16_t a, uint16_t b) { return a < b ? a : b; }

uint16_t u16_max(uint16_t a, uint16_t b) { return a > b ? a : b; }

uint16_t u16_not(uint16_t a) { return ~a; }

uint16_t u16_neg(uint16_t a) { return (uint16_t)(0 - (uint32_t)(uint16_t)a); }

uint16_t u16_add1(uint16_t a) { return (uint16_t)((uint32_t)(uint16_t)a + 1); }

uint16_t u16_mul3(uint16_t a) { return (uint16_t)((uint32_t)(uint16_t)a * 3); }

uint16_t u16_mul10(uint16_t a) {
  return (uint16_t)((uint32_t)(uint16_t)a * 10);
}

uint16_t u16_div3(uint16_t a) { return a / 3; }

uint16_t u16_rem10(uint16_t a) { return a % 10; }

uint16_t u16_div255(uint16_t a) { return a / 255; }

uint16_t u16_rem255(uint16_t a) { return a % 255; }

uint16_t u16_div257(uint16_t a) { return a / 257; }

uint16_t u16_rem257(uint16_t a) { return a % 257; }

uint16_t u16_div1(uint16_t a) { return a / 1; }

uint16_t u16_div2(uint16_t a) { return a / 2; }

uint16_t u16_div256(uint16_t a) { return a / 256; }

uint16_t u16_rem256(uint16_t a) { return a % 256; }

uint16_t u16_shl(uint16_t a, uint8_t b) {
  return (uint16_t)((uint32_t)(uint16_t)a << (b & 15));
}

uint16_t u16_shl1(uint16_t a) { return (uint16_t)((uint32_t)(uint16_t)a << 1); }

uint16_t u16_shl7(uint16_t a) { return (uint16_t)((uint32_t)(uint16_t)a << 7); }

uint16_t u16_shr(uint16_t a, uint8_t b) { return (uint16_t)(a >> (b & 15)); }

uint16_t u16_shr1(uint16_t a) { return (uint16_t)(a >> 1); }

uint16_t u16_shr7(uint16_t a) { return (uint16_t)(a >> 7); }

uint16_t u16_rol(uint16_t a, uint8_t b) {
  return (uint16_t)(((uint32_t)(uint16_t)a << (b & 15)) |
                    ((uint32_t)(uint16_t)a >> ((0u - (b & 15)) & 15)));
}

uint16_t u16_ror(uint16_t a, uint8_t b) {
  return (uint16_t)(((uint32_t)(uint16_t)a >> (b & 15)) |
                    ((uint32_t)(uint16_t)a << ((0u - (b & 15)) & 15)));
}

int16_t u16_as_signed(uint16_t a) { return (int16_t)a; }

uint16_t u16_as_unsigned(uint16_t a) { return (uint16_t)a; }

uint8_t u16_narrow(uint16_t a) { return (uint8_t)a; }

uint32_t u16_widen(uint16_t a) { return (uint32_t)a; }
