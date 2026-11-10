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

uint8_t *concat_strcat_loop(uint8_t *dst, const uint8_t *src) {
  uint16_t i = 0, j = 0;
  while (dst[i])
    ++i;
  do {
    dst[i] = src[j];
    ++i;
  } while (src[j++]);
  return dst;
}

uint8_t *concat_strcat_library(uint8_t *dst, const uint8_t *src) {
  return (uint8_t *)strcat((char *)dst, (const char *)src);
}

uint8_t *concat_strncat_loop(uint8_t *dst, const uint8_t *src, uint16_t n) {
  uint16_t i = 0, j = 0;
  while (dst[i])
    ++i;
  while (j < n && src[j]) {
    dst[i++] = src[j++];
  }
  dst[i] = 0;
  return dst;
}

uint8_t *concat_strncat_library(uint8_t *dst, const uint8_t *src, uint16_t n) {
  return (uint8_t *)strncat((char *)dst, (const char *)src, n);
}

uint16_t concat_append_bounded(uint8_t *dst, const uint8_t *src,
                               uint16_t limit) {
  uint16_t i = 0, j = 0;
  while (i < limit && dst[i])
    ++i;
  if (i == limit)
    return UINT16_MAX;
  while (i + 1 < limit && src[j])
    dst[i++] = src[j++];
  dst[i] = 0;
  return i;
}
