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

uint8_t *aggregate_copy8_assign(uint8_t *dst, const uint8_t *src) {
  *(PatternBlob8 *)dst = *(const PatternBlob8 *)src;
  return dst;
}
