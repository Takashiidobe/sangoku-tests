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
  uint8_t bytes[5];
} PatternBlob5;

NOINLINE void fixture_blob5_out(PatternBlob5 *dst, const PatternBlob5 *src) {
  *dst = *src;
}

uint16_t aggregate_out5_call(uint8_t *dst, const uint8_t *src) {
  PatternBlob5 tmp;
  fixture_blob5_out(&tmp, (const PatternBlob5 *)src);
  *(PatternBlob5 *)dst = tmp;
  return 5;
}
