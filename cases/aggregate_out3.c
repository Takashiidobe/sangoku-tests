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
  uint8_t bytes[3];
} PatternBlob3;

NOINLINE void fixture_blob3_out(PatternBlob3 *dst, const PatternBlob3 *src) {
  *dst = *src;
}

uint16_t aggregate_out3_call(uint8_t *dst, const uint8_t *src) {
  PatternBlob3 tmp;
  fixture_blob3_out(&tmp, (const PatternBlob3 *)src);
  *(PatternBlob3 *)dst = tmp;
  return 3;
}
