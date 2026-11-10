#include <stdint.h>
_Static_assert(sizeof(float) * 8 == 32, "required width: f32");

float f32_add(float a, float b) { return a + b; }

float f32_sub(float a, float b) { return a - b; }

float f32_mul(float a, float b) { return a * b; }

float f32_div(float a, float b) { return a / b; }

uint8_t f32_eq(float a, float b) { return a == b; }

uint8_t f32_ne(float a, float b) { return a != b; }

uint8_t f32_lt(float a, float b) { return a < b; }

uint8_t f32_le(float a, float b) { return a <= b; }

uint8_t f32_gt(float a, float b) { return a > b; }

uint8_t f32_ge(float a, float b) { return a >= b; }

float f32_neg(float a) { return -a; }
