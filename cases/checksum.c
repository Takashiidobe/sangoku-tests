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

uint8_t checksum_sum8(const uint8_t *src, uint16_t n) {
  uint8_t value = 0;
  for (uint16_t i = 0; i < n; ++i)
    value = (uint8_t)(value + src[i]);
  return value;
}

uint16_t checksum_sum16(const uint8_t *src, uint16_t n) {
  uint16_t value = 0;
  for (uint16_t i = 0; i < n; ++i)
    value = (uint16_t)(value + src[i]);
  return value;
}

uint16_t checksum_crc16(const uint8_t *src, uint16_t n, uint16_t value) {
  for (uint16_t i = 0; i < n; ++i) {
    value ^= (uint16_t)src[i] << 8;
    for (uint8_t j = 0; j < 8; ++j)
      value = (uint16_t)((value << 1) ^ ((value & 0x8000u) ? 0x1021u : 0));
  }
  return value;
}
