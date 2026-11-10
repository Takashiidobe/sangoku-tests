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

uint32_t parse_decimal_loop(const uint8_t *src, uint16_t *end) {
  uint16_t i = 0;
  uint32_t value = 0;
  while (src[i] == ' ' || (src[i] >= 9 && src[i] <= 13))
    ++i;
  uint8_t minus = src[i] == '-';
  if (minus || src[i] == '+')
    ++i;
  uint16_t first = i;
  while (src[i] >= '0' && src[i] <= '9') {
    value = value * 10u + (uint32_t)(src[i] - '0');
    ++i;
  }
  *end = i == first ? 0 : i;
  return minus ? (uint32_t)(0u - value) : value;
}

uint32_t parse_strtoul_decimal(const uint8_t *src, uint16_t *end) {
  char *last;
  uint32_t value = (uint32_t)strtoul((const char *)src, &last, 10);
  *end = (uint16_t)(last - (const char *)src);
  return value;
}

uint32_t parse_decimal_checked(const uint8_t *src, uint16_t *end) {
  uint16_t i = 0;
  uint32_t value = 0;
  uint8_t overflow = 0;
  while (src[i] == ' ' || (src[i] >= 9 && src[i] <= 13))
    ++i;
  uint8_t minus = src[i] == '-';
  if (minus || src[i] == '+')
    ++i;
  uint16_t first = i;
  while (src[i] >= '0' && src[i] <= '9') {
    uint32_t d = (uint32_t)(src[i] - '0');
    if (value > (UINT32_MAX - d) / 10u) {
      overflow = 1;
      value = UINT32_MAX;
    } else if (!overflow)
      value = value * 10u + d;
    ++i;
  }
  *end = (uint16_t)((i == first ? 0 : i) | (overflow ? 0x8000u : 0));
  return minus ? (uint32_t)(0u - value) : value;
}

uint32_t parse_hex_loop(const uint8_t *src, uint16_t *end) {
  uint16_t i = 0;
  uint32_t value = 0;
  if (src[0] == '0' && (src[1] == 'x' || src[1] == 'X'))
    i = 2;
  uint16_t first = i;
  for (;;) {
    uint8_t c = src[i];
    uint8_t d = c >= '0' && c <= '9'   ? c - '0'
                : c >= 'a' && c <= 'f' ? c - 'a' + 10
                : c >= 'A' && c <= 'F' ? c - 'A' + 10
                                       : 255;
    if (d == 255)
      break;
    value = (value << 4) | d;
    ++i;
  }
  *end = i == first ? 0 : i;
  return value;
}

int16_t parse_atoi(const uint8_t *src) {
  return (int16_t)atoi((const char *)src);
}
