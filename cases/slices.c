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

uint16_t slices_sum_index(const uint8_t *src, uint16_t n) {
  uint16_t value = 0;
  for (uint16_t i = 0; i < n; ++i)
    value = (uint16_t)(value + src[i]);
  return value;
}

uint16_t slices_sum_iter(const uint8_t *src, uint16_t n) {
  uint16_t value = 0;
  for (uint16_t i = 0; i < n; ++i)
    value = (uint16_t)(value + src[i]);
  return value;
}

uint16_t slices_sum_raw(const uint8_t *src, uint16_t n) {
  uint16_t value = 0;
  for (uint16_t i = 0; i < n; ++i)
    value = (uint16_t)(value + src[i]);
  return value;
}

uint16_t slices_sum_pointer(const uint8_t *src, uint16_t n) {
  uint16_t value = 0;
  const uint8_t *last = src + n;
  while (src != last)
    value = (uint16_t)(value + *src++);
  return value;
}

uint16_t slices_sum_countdown(const uint8_t *src, uint16_t n) {
  uint16_t value = 0;
  while (n) {
    value = (uint16_t)(value + *src++);
    --n;
  }
  return value;
}

uint8_t *slices_copy_from_slice(uint8_t *dst, const uint8_t *src, uint16_t n) {
  memcpy(dst, src, n);
  return dst;
}

uint8_t *slices_copy_within(uint8_t *dst, uint16_t n) {
  uint16_t half = n / 2;
  memmove(dst + n - half, dst, half);
  return dst;
}

uint8_t *slices_fill(uint8_t *dst, uint16_t n, uint8_t value) {
  memset(dst, value, n);
  return dst;
}

uint16_t slices_chunks_exact(const uint8_t *src, uint16_t n) {
  uint16_t value = 0;
  for (uint16_t i = 0; i + 1 < n; i += 2)
    value = (uint16_t)(value + src[i] + ((uint16_t)src[i + 1] << 8));
  return value;
}
