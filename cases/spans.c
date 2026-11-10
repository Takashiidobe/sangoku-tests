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

uint16_t spans_strspn_loop(const uint8_t *src, const uint8_t *set) {
  uint16_t i = 0;
  while (src[i]) {
    uint16_t j = 0;
    while (set[j] && set[j] != src[i])
      ++j;
    uint8_t found = set[j] != 0;
    if (!found)
      break;
    ++i;
  }
  return i;
}

uint16_t spans_strspn_library(const uint8_t *src, const uint8_t *set) {
  return (uint16_t)strspn((const char *)src, (const char *)set);
}

uint16_t spans_strcspn_loop(const uint8_t *src, const uint8_t *set) {
  uint16_t i = 0;
  while (src[i]) {
    uint16_t j = 0;
    while (set[j] && set[j] != src[i])
      ++j;
    uint8_t found = set[j] != 0;
    if (found)
      break;
    ++i;
  }
  return i;
}

uint16_t spans_strcspn_library(const uint8_t *src, const uint8_t *set) {
  return (uint16_t)strcspn((const char *)src, (const char *)set);
}

uint16_t spans_strpbrk_loop(const uint8_t *src, const uint8_t *set) {
  uint16_t i = 0;
  while (src[i]) {
    uint16_t j = 0;
    while (set[j] && set[j] != src[i])
      ++j;
    uint8_t found = set[j] != 0;
    if (found)
      break;
    ++i;
  }
  return src[i] ? i : UINT16_MAX;
}

uint16_t spans_strpbrk_library(const uint8_t *src, const uint8_t *set) {
  const char *p = strpbrk((const char *)src, (const char *)set);
  return p ? (uint16_t)((const uint8_t *)p - src) : UINT16_MAX;
}

uint16_t spans_tokenize_loop(uint8_t *dst, const uint8_t *src,
                             const uint8_t *set) {
  uint16_t i = 0, count = 0;
  while (src[i]) {
    uint16_t j = 0;
    while (set[j] && set[j] != src[i])
      ++j;
    if (set[j]) {
      ++i;
      continue;
    }
    uint16_t start = i;
    do {
      ++i;
      j = 0;
      while (set[j] && set[j] != src[i])
        ++j;
    } while (src[i] && !set[j]);
    dst[2 * count] = (uint8_t)start;
    dst[2 * count + 1] = (uint8_t)(i - start);
    ++count;
  }
  return count;
}

uint16_t spans_strtok_library(uint8_t *dst, const uint8_t *src,
                              const uint8_t *set) {
  strcpy((char *)dst, (const char *)src);
  uint16_t count = 0;
  char *token = strtok((char *)dst, (const char *)set);
  while (token) {
    ++count;
    token = strtok(NULL, (const char *)set);
  }
  return count;
}
