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

uint16_t substring_strstr_loop(const uint8_t *src, const uint8_t *other) {
  if (!other[0])
    return 0;
  uint16_t i = 0;
  while (src[i]) {
    uint16_t j = 0;
    while (other[j] && src[i + j] == other[j])
      ++j;
    if (!other[j])
      return i;
    ++i;
  }
  return UINT16_MAX;
}

uint16_t substring_strstr_library(const uint8_t *src, const uint8_t *other) {
  const char *p = strstr((const char *)src, (const char *)other);
  return p ? (uint16_t)((const uint8_t *)p - src) : UINT16_MAX;
}

uint16_t substring_needle2(const uint8_t *src, const uint8_t *other,
                           uint16_t n) {
  if (n < 2)
    return UINT16_MAX;
  for (uint16_t i = 0; i <= n - 2; ++i)
    if (src[i + 0] == other[0] && src[i + 1] == other[1])
      return i;
  return UINT16_MAX;
}

uint16_t substring_needle4(const uint8_t *src, const uint8_t *other,
                           uint16_t n) {
  if (n < 4)
    return UINT16_MAX;
  for (uint16_t i = 0; i <= n - 4; ++i)
    if (src[i + 0] == other[0] && src[i + 1] == other[1] &&
        src[i + 2] == other[2] && src[i + 3] == other[3])
      return i;
  return UINT16_MAX;
}
