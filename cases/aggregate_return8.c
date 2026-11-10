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

PatternBlob8 aggregate_return8_value(const uint8_t *src) {
  return *(const PatternBlob8 *)src;
}
