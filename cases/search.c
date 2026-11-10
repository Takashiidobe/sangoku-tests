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

NOINLINE int fixture_cmp_words(const void *a, const void *b) {
  uint16_t x = *(const uint16_t *)a, y = *(const uint16_t *)b;
  return (x > y) - (x < y);
}

uint16_t search_binary_loop(const uint16_t *src, uint16_t n, uint16_t value) {
  uint16_t low = 0, high = n;
  while (low < high) {
    uint16_t mid = low + (high - low) / 2;
    if (src[mid] < value)
      low = mid + 1;
    else if (src[mid] > value)
      high = mid;
    else
      return mid;
  }
  return UINT16_MAX;
}

uint16_t search_bsearch_library(const uint16_t *src, uint16_t n,
                                uint16_t value) {
  const uint16_t *p = (const uint16_t *)bsearch(
      &value, src, n, sizeof(uint16_t), fixture_cmp_words);
  return p ? (uint16_t)(p - src) : UINT16_MAX;
}

uint8_t *search_insertion_sort(uint16_t *dst, uint16_t n) {
  for (uint16_t i = 1; i < n; ++i) {
    uint16_t value = dst[i], j = i;
    while (j && dst[j - 1] > value) {
      dst[j] = dst[j - 1];
      --j;
    }
    dst[j] = value;
  }
  return (uint8_t *)dst;
}

uint8_t *search_qsort_library(uint16_t *dst, uint16_t n) {
  qsort(dst, n, sizeof(uint16_t), fixture_cmp_words);
  return (uint8_t *)dst;
}
