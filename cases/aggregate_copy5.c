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

uint8_t *aggregate_copy5_assign(uint8_t *dst, const uint8_t *src) {
  *(PatternBlob5 *)dst = *(const PatternBlob5 *)src;
  return dst;
}
