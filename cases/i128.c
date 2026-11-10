#include <stdint.h>
_Static_assert(sizeof(__int128) * 8 == 128, "required width: i128");
_Static_assert((-1 >> 1) == -1, "arithmetic signed right shift required");

__int128 i128_add(__int128 a, __int128 b) {
  return (__int128)((unsigned __int128)(unsigned __int128)a +
                    (unsigned __int128)(unsigned __int128)b);
}

__int128 i128_sub(__int128 a, __int128 b) {
  return (__int128)((unsigned __int128)(unsigned __int128)a -
                    (unsigned __int128)(unsigned __int128)b);
}

__int128 i128_mul(__int128 a, __int128 b) {
  return (__int128)((unsigned __int128)(unsigned __int128)a *
                    (unsigned __int128)(unsigned __int128)b);
}

__int128 i128_div(__int128 a, __int128 b) { return a / b; }

__int128 i128_rem(__int128 a, __int128 b) { return a % b; }

__int128 i128_and(__int128 a, __int128 b) { return a & b; }

__int128 i128_or(__int128 a, __int128 b) { return a | b; }

__int128 i128_xor(__int128 a, __int128 b) { return a ^ b; }

uint8_t i128_eq(__int128 a, __int128 b) { return a == b; }

uint8_t i128_ne(__int128 a, __int128 b) { return a != b; }

uint8_t i128_lt(__int128 a, __int128 b) { return a < b; }

uint8_t i128_le(__int128 a, __int128 b) { return a <= b; }

uint8_t i128_gt(__int128 a, __int128 b) { return a > b; }

uint8_t i128_ge(__int128 a, __int128 b) { return a >= b; }

__int128 i128_min(__int128 a, __int128 b) { return a < b ? a : b; }

__int128 i128_max(__int128 a, __int128 b) { return a > b ? a : b; }

__int128 i128_not(__int128 a) { return ~a; }

__int128 i128_neg(__int128 a) {
  return (__int128)(0 - (unsigned __int128)(unsigned __int128)a);
}

__int128 i128_add1(__int128 a) {
  return (__int128)((unsigned __int128)(unsigned __int128)a + 1);
}

__int128 i128_mul3(__int128 a) {
  return (__int128)((unsigned __int128)(unsigned __int128)a * 3);
}

__int128 i128_mul10(__int128 a) {
  return (__int128)((unsigned __int128)(unsigned __int128)a * 10);
}

__int128 i128_div3(__int128 a) { return a / 3; }

__int128 i128_rem10(__int128 a) { return a % 10; }

__int128 i128_shl(__int128 a, uint8_t b) {
  return (__int128)((unsigned __int128)(unsigned __int128)a << (b & 127));
}

__int128 i128_shl1(__int128 a) {
  return (__int128)((unsigned __int128)(unsigned __int128)a << 1);
}

__int128 i128_shl7(__int128 a) {
  return (__int128)((unsigned __int128)(unsigned __int128)a << 7);
}

__int128 i128_shr(__int128 a, uint8_t b) { return (__int128)(a >> (b & 127)); }

__int128 i128_shr1(__int128 a) { return (__int128)(a >> 1); }

__int128 i128_shr7(__int128 a) { return (__int128)(a >> 7); }

__int128 i128_rol(__int128 a, uint8_t b) {
  return (__int128)(((unsigned __int128)(unsigned __int128)a << (b & 127)) |
                    ((unsigned __int128)(unsigned __int128)a >>
                     ((0u - (b & 127)) & 127)));
}

__int128 i128_ror(__int128 a, uint8_t b) {
  return (__int128)(((unsigned __int128)(unsigned __int128)a >> (b & 127)) |
                    ((unsigned __int128)(unsigned __int128)a
                     << ((0u - (b & 127)) & 127)));
}

__int128 i128_as_signed(__int128 a) { return (__int128)a; }

unsigned __int128 i128_as_unsigned(__int128 a) { return (unsigned __int128)a; }

uint64_t i128_narrow(__int128 a) { return (uint64_t)a; }
