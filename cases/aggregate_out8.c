#include <ctype.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#if defined(__SDCC)
#define NOINLINE
#else
#define NOINLINE __attribute__((noinline))
#endif
typedef struct {
  uint8_t bytes[8];
} PatternBlob8;

NOINLINE void fixture_blob8_out(PatternBlob8 *dst, const PatternBlob8 *src) {
  *dst = *src;
}

uint16_t aggregate_out8_call(uint8_t *dst, const uint8_t *src) {
  PatternBlob8 tmp;
  fixture_blob8_out(&tmp, (const PatternBlob8 *)src);
  *(PatternBlob8 *)dst = tmp;
  return 8;
}
