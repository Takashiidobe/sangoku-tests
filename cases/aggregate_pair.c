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
  const uint8_t *ptr;
  uint16_t len;
} PatternPair;

PatternPair aggregate_pair_return(const uint8_t *src, uint16_t n) {
  PatternPair result = {src, n};
  return result;
}
