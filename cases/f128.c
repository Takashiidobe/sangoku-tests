#include <stdint.h>
_Static_assert(sizeof(long double) * 8 == 128, "required width: f128");

long double f128_add(long double a, long double b) { return a + b; }

long double f128_sub(long double a, long double b) { return a - b; }

long double f128_mul(long double a, long double b) { return a * b; }

long double f128_div(long double a, long double b) { return a / b; }

uint8_t f128_eq(long double a, long double b) { return a == b; }

uint8_t f128_ne(long double a, long double b) { return a != b; }

uint8_t f128_lt(long double a, long double b) { return a < b; }

uint8_t f128_le(long double a, long double b) { return a <= b; }

uint8_t f128_gt(long double a, long double b) { return a > b; }

uint8_t f128_ge(long double a, long double b) { return a >= b; }

long double f128_neg(long double a) { return -a; }
