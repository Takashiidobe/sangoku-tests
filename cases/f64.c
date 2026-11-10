#include <stdint.h>
_Static_assert(sizeof(double) * 8 == 64, "required width: f64");

double f64_add(double a, double b) { return a + b; }

double f64_sub(double a, double b) { return a - b; }

double f64_mul(double a, double b) { return a * b; }

double f64_div(double a, double b) { return a / b; }

uint8_t f64_eq(double a, double b) { return a == b; }

uint8_t f64_ne(double a, double b) { return a != b; }

uint8_t f64_lt(double a, double b) { return a < b; }

uint8_t f64_le(double a, double b) { return a <= b; }

uint8_t f64_gt(double a, double b) { return a > b; }

uint8_t f64_ge(double a, double b) { return a >= b; }

double f64_neg(double a) { return -a; }
