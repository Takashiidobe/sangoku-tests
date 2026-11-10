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

uint8_t *aggregate_copy12_assign(uint8_t *dst, const uint8_t *src) {
  *(PatternBlob12 *)dst = *(const PatternBlob12 *)src;
  return dst;
}
