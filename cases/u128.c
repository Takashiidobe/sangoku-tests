#include <stdint.h>
_Static_assert(sizeof(unsigned __int128) * 8 == 128, "required width: u128");

unsigned __int128 u128_add(unsigned __int128 a, unsigned __int128 b) {
  return (unsigned __int128)((unsigned __int128)(unsigned __int128)a +
                             (unsigned __int128)(unsigned __int128)b);
}

unsigned __int128 u128_sub(unsigned __int128 a, unsigned __int128 b) {
  return (unsigned __int128)((unsigned __int128)(unsigned __int128)a -
                             (unsigned __int128)(unsigned __int128)b);
}

unsigned __int128 u128_mul(unsigned __int128 a, unsigned __int128 b) {
  return (unsigned __int128)((unsigned __int128)(unsigned __int128)a *
                             (unsigned __int128)(unsigned __int128)b);
}

unsigned __int128 u128_div(unsigned __int128 a, unsigned __int128 b) {
  return a / b;
}

unsigned __int128 u128_rem(unsigned __int128 a, unsigned __int128 b) {
  return a % b;
}

unsigned __int128 u128_and(unsigned __int128 a, unsigned __int128 b) {
  return a & b;
}

unsigned __int128 u128_or(unsigned __int128 a, unsigned __int128 b) {
  return a | b;
}

unsigned __int128 u128_xor(unsigned __int128 a, unsigned __int128 b) {
  return a ^ b;
}

uint8_t u128_eq(unsigned __int128 a, unsigned __int128 b) { return a == b; }

uint8_t u128_ne(unsigned __int128 a, unsigned __int128 b) { return a != b; }

uint8_t u128_lt(unsigned __int128 a, unsigned __int128 b) { return a < b; }

uint8_t u128_le(unsigned __int128 a, unsigned __int128 b) { return a <= b; }

uint8_t u128_gt(unsigned __int128 a, unsigned __int128 b) { return a > b; }

uint8_t u128_ge(unsigned __int128 a, unsigned __int128 b) { return a >= b; }

unsigned __int128 u128_min(unsigned __int128 a, unsigned __int128 b) {
  return a < b ? a : b;
}

unsigned __int128 u128_max(unsigned __int128 a, unsigned __int128 b) {
  return a > b ? a : b;
}

unsigned __int128 u128_not(unsigned __int128 a) { return ~a; }

unsigned __int128 u128_neg(unsigned __int128 a) {
  return (unsigned __int128)(0 - (unsigned __int128)(unsigned __int128)a);
}

unsigned __int128 u128_add1(unsigned __int128 a) {
  return (unsigned __int128)((unsigned __int128)(unsigned __int128)a + 1);
}

unsigned __int128 u128_mul3(unsigned __int128 a) {
  return (unsigned __int128)((unsigned __int128)(unsigned __int128)a * 3);
}

unsigned __int128 u128_mul10(unsigned __int128 a) {
  return (unsigned __int128)((unsigned __int128)(unsigned __int128)a * 10);
}

unsigned __int128 u128_div3(unsigned __int128 a) { return a / 3; }

unsigned __int128 u128_rem10(unsigned __int128 a) { return a % 10; }

unsigned __int128 u128_shl(unsigned __int128 a, uint8_t b) {
  return (unsigned __int128)((unsigned __int128)(unsigned __int128)a
                             << (b & 127));
}

unsigned __int128 u128_shl1(unsigned __int128 a) {
  return (unsigned __int128)((unsigned __int128)(unsigned __int128)a << 1);
}

unsigned __int128 u128_shl7(unsigned __int128 a) {
  return (unsigned __int128)((unsigned __int128)(unsigned __int128)a << 7);
}

unsigned __int128 u128_shr(unsigned __int128 a, uint8_t b) {
  return (unsigned __int128)(a >> (b & 127));
}

unsigned __int128 u128_shr1(unsigned __int128 a) {
  return (unsigned __int128)(a >> 1);
}

unsigned __int128 u128_shr7(unsigned __int128 a) {
  return (unsigned __int128)(a >> 7);
}

unsigned __int128 u128_rol(unsigned __int128 a, uint8_t b) {
  return (unsigned __int128)(((unsigned __int128)(unsigned __int128)a
                              << (b & 127)) |
                             ((unsigned __int128)(unsigned __int128)a >>
                              ((0u - (b & 127)) & 127)));
}

unsigned __int128 u128_ror(unsigned __int128 a, uint8_t b) {
  return (unsigned __int128)(((unsigned __int128)(unsigned __int128)a >>
                              (b & 127)) |
                             ((unsigned __int128)(unsigned __int128)a
                              << ((0u - (b & 127)) & 127)));
}

__int128 u128_as_signed(unsigned __int128 a) { return (__int128)a; }

unsigned __int128 u128_as_unsigned(unsigned __int128 a) {
  return (unsigned __int128)a;
}

uint64_t u128_narrow(unsigned __int128 a) { return (uint64_t)a; }
