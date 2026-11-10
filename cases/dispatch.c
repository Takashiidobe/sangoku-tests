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

uint16_t dispatch_dense(uint8_t value) {
  switch (value) {
  case 0:
    return 7;
  case 1:
    return 0;
  case 2:
    return 99;
  case 3:
    return 2;
  case 4:
    return 1;
  case 5:
    return 17;
  case 6:
    return 31;
  case 7:
    return 6;
  default:
    return 65535;
  }
}

uint16_t dispatch_sparse(uint8_t value) {
  switch (value) {
  case 0:
    return 7;
  case 1:
    return 11;
  case 7:
    return 3;
  case 31:
    return 13;
  case 128:
    return 5;
  case 255:
    return 17;
  default:
    return 0;
  }
}

uint16_t dispatch_parser_state(const uint8_t *src, uint16_t n) {
  uint16_t acc = 0, total = 0;
  uint8_t state = 0;
  for (uint16_t i = 0; i < n; ++i) {
    uint8_t c = src[i];
    switch (c) {
    case ':':
      state ^= 1;
      break;
    case ',':
      total = (uint16_t)(total + acc);
      acc = 0;
      break;
    default:
      if (c >= '0' && c <= '9')
        acc = (uint16_t)(acc * 10u + c - '0');
      else if (c != ' ')
        state = 2;
      break;
    }
  }
  return (uint16_t)(total ^ acc ^ state);
}
