#include <stdint.h>
_Static_assert(sizeof(_Float16) * 8 == 16, "required width: f16");

_Float16 f16_add(_Float16 a, _Float16 b) { return a + b; }

_Float16 f16_sub(_Float16 a, _Float16 b) { return a - b; }

_Float16 f16_mul(_Float16 a, _Float16 b) { return a * b; }

_Float16 f16_div(_Float16 a, _Float16 b) { return a / b; }

uint8_t f16_eq(_Float16 a, _Float16 b) { return a == b; }

uint8_t f16_ne(_Float16 a, _Float16 b) { return a != b; }

uint8_t f16_lt(_Float16 a, _Float16 b) { return a < b; }

uint8_t f16_le(_Float16 a, _Float16 b) { return a <= b; }

uint8_t f16_gt(_Float16 a, _Float16 b) { return a > b; }

uint8_t f16_ge(_Float16 a, _Float16 b) { return a >= b; }

_Float16 f16_neg(_Float16 a) { return -a; }
