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

uint16_t format_u32_decimal_divmod(uint8_t *dst, uint32_t value) {
  uint8_t tmp[20], i = 0;
  do {
    uint32_t q = value / 10;
    uint8_t d = (uint8_t)(value % 10);
    tmp[i++] = (uint8_t)(d < 10 ? '0' + d : 'a' + d - 10);
    value = q;
  } while (value);
  for (uint8_t j = 0; j < i; ++j)
    dst[j] = tmp[i - 1 - j];
  dst[i] = 0;
  return i;
}

uint16_t format_u32_decimal_derived(uint8_t *dst, uint32_t value) {
  uint8_t tmp[20], i = 0;
  do {
    uint32_t q = value / 10;
    uint8_t d = (uint8_t)(value - q * 10);
    tmp[i++] = (uint8_t)(d < 10 ? '0' + d : 'a' + d - 10);
    value = q;
  } while (value);
  for (uint8_t j = 0; j < i; ++j)
    dst[j] = tmp[i - 1 - j];
  dst[i] = 0;
  return i;
}

uint16_t format_u32_hex(uint8_t *dst, uint32_t value) {
  uint8_t tmp[20], i = 0;
  do {
    uint32_t q = value >> 4;
    uint8_t d = (uint8_t)(value & 15);
    tmp[i++] = (uint8_t)(d < 10 ? '0' + d : 'a' + d - 10);
    value = q;
  } while (value);
  for (uint8_t j = 0; j < i; ++j)
    dst[j] = tmp[i - 1 - j];
  dst[i] = 0;
  return i;
}

uint16_t format_u32_decimal_library(uint8_t *dst, uint32_t value) {
  return (uint16_t)sprintf((char *)dst, "%lu", (unsigned long)value);
}
