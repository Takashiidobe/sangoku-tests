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
  uint8_t bytes[12];
} PatternBlob12;

NOINLINE void fixture_blob12_out(PatternBlob12 *dst, const PatternBlob12 *src) {
  *dst = *src;
}

uint16_t aggregate_out12_call(uint8_t *dst, const uint8_t *src) {
  PatternBlob12 tmp;
  fixture_blob12_out(&tmp, (const PatternBlob12 *)src);
  *(PatternBlob12 *)dst = tmp;
  return 12;
}
