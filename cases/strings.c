#include <stdint.h>
#include <string.h>

uint16_t strings_strlen(const uint8_t *s) {
  return (uint16_t)strlen((const char *)s);
}

uint16_t strings_strlen_loop(const uint8_t *s) {
  uint16_t n = 0;
  while (s[n])
    ++n;
  return n;
}

int8_t strings_strcmp(const uint8_t *a, const uint8_t *b) {
  int v = strcmp((const char *)a, (const char *)b);
  return (int8_t)((v > 0) - (v < 0));
}

int8_t strings_strcmp_loop(const uint8_t *a, const uint8_t *b) {
  uint16_t i = 0;
  for (;;) {
    uint8_t x = a[i], y = b[i];
    if (x != y)
      return (int8_t)((x > y) - (x < y));
    if (!x)
      return 0;
    ++i;
  }
}

int8_t strings_strncmp(const uint8_t *a, const uint8_t *b, uint16_t n) {
  int v = strncmp((const char *)a, (const char *)b, n);
  return (int8_t)((v > 0) - (v < 0));
}

uint16_t strings_strchr(const uint8_t *s, uint8_t value) {
  const char *p = strchr((const char *)s, value);
  return p ? (uint16_t)((const uint8_t *)p - s) : UINT16_MAX;
}

uint16_t strings_strrchr(const uint8_t *s, uint8_t value) {
  const char *p = strrchr((const char *)s, value);
  return p ? (uint16_t)((const uint8_t *)p - s) : UINT16_MAX;
}

uint8_t *strings_strcpy(uint8_t *dst, const uint8_t *src) {
  return (uint8_t *)strcpy((char *)dst, (const char *)src);
}

uint8_t *strings_strncpy(uint8_t *dst, const uint8_t *src, uint16_t n) {
  return (uint8_t *)strncpy((char *)dst, (const char *)src, n);
}

uint8_t *strings_memcpy(uint8_t *dst, const uint8_t *src, uint16_t n) {
  return (uint8_t *)memcpy(dst, src, n);
}

uint8_t *strings_memcpy0(uint8_t *dst, const uint8_t *src) {
  return (uint8_t *)memcpy(dst, src, 0);
}

uint8_t *strings_memcpy1(uint8_t *dst, const uint8_t *src) {
  return (uint8_t *)memcpy(dst, src, 1);
}

uint8_t *strings_memcpy2(uint8_t *dst, const uint8_t *src) {
  return (uint8_t *)memcpy(dst, src, 2);
}

uint8_t *strings_memcpy3(uint8_t *dst, const uint8_t *src) {
  return (uint8_t *)memcpy(dst, src, 3);
}

uint8_t *strings_memcpy4(uint8_t *dst, const uint8_t *src) {
  return (uint8_t *)memcpy(dst, src, 4);
}

uint8_t *strings_memcpy7(uint8_t *dst, const uint8_t *src) {
  return (uint8_t *)memcpy(dst, src, 7);
}

uint8_t *strings_memcpy8(uint8_t *dst, const uint8_t *src) {
  return (uint8_t *)memcpy(dst, src, 8);
}

uint8_t *strings_memcpy15(uint8_t *dst, const uint8_t *src) {
  return (uint8_t *)memcpy(dst, src, 15);
}

uint8_t *strings_memcpy16(uint8_t *dst, const uint8_t *src) {
  return (uint8_t *)memcpy(dst, src, 16);
}

uint8_t *strings_memcpy17(uint8_t *dst, const uint8_t *src) {
  return (uint8_t *)memcpy(dst, src, 17);
}

uint8_t *strings_memcpy31(uint8_t *dst, const uint8_t *src) {
  return (uint8_t *)memcpy(dst, src, 31);
}

uint8_t *strings_memcpy32(uint8_t *dst, const uint8_t *src) {
  return (uint8_t *)memcpy(dst, src, 32);
}

uint8_t *strings_memcpy63(uint8_t *dst, const uint8_t *src) {
  return (uint8_t *)memcpy(dst, src, 63);
}

uint8_t *strings_memcpy64(uint8_t *dst, const uint8_t *src) {
  return (uint8_t *)memcpy(dst, src, 64);
}

uint8_t *strings_memcpy127(uint8_t *dst, const uint8_t *src) {
  return (uint8_t *)memcpy(dst, src, 127);
}

uint8_t *strings_memcpy128(uint8_t *dst, const uint8_t *src) {
  return (uint8_t *)memcpy(dst, src, 128);
}

uint8_t *strings_memmove(uint8_t *dst, const uint8_t *src, uint16_t n) {
  return (uint8_t *)memmove(dst, src, n);
}

uint8_t *strings_memmove0(uint8_t *dst, const uint8_t *src) {
  return (uint8_t *)memmove(dst, src, 0);
}

uint8_t *strings_memmove1(uint8_t *dst, const uint8_t *src) {
  return (uint8_t *)memmove(dst, src, 1);
}

uint8_t *strings_memmove2(uint8_t *dst, const uint8_t *src) {
  return (uint8_t *)memmove(dst, src, 2);
}

uint8_t *strings_memmove3(uint8_t *dst, const uint8_t *src) {
  return (uint8_t *)memmove(dst, src, 3);
}

uint8_t *strings_memmove4(uint8_t *dst, const uint8_t *src) {
  return (uint8_t *)memmove(dst, src, 4);
}

uint8_t *strings_memmove7(uint8_t *dst, const uint8_t *src) {
  return (uint8_t *)memmove(dst, src, 7);
}

uint8_t *strings_memmove8(uint8_t *dst, const uint8_t *src) {
  return (uint8_t *)memmove(dst, src, 8);
}

uint8_t *strings_memmove15(uint8_t *dst, const uint8_t *src) {
  return (uint8_t *)memmove(dst, src, 15);
}

uint8_t *strings_memmove16(uint8_t *dst, const uint8_t *src) {
  return (uint8_t *)memmove(dst, src, 16);
}

uint8_t *strings_memmove17(uint8_t *dst, const uint8_t *src) {
  return (uint8_t *)memmove(dst, src, 17);
}

uint8_t *strings_memmove31(uint8_t *dst, const uint8_t *src) {
  return (uint8_t *)memmove(dst, src, 31);
}

uint8_t *strings_memmove32(uint8_t *dst, const uint8_t *src) {
  return (uint8_t *)memmove(dst, src, 32);
}

uint8_t *strings_memmove63(uint8_t *dst, const uint8_t *src) {
  return (uint8_t *)memmove(dst, src, 63);
}

uint8_t *strings_memmove64(uint8_t *dst, const uint8_t *src) {
  return (uint8_t *)memmove(dst, src, 64);
}

uint8_t *strings_memmove127(uint8_t *dst, const uint8_t *src) {
  return (uint8_t *)memmove(dst, src, 127);
}

uint8_t *strings_memmove128(uint8_t *dst, const uint8_t *src) {
  return (uint8_t *)memmove(dst, src, 128);
}

uint8_t *strings_memset(uint8_t *dst, uint8_t value, uint16_t n) {
  return (uint8_t *)memset(dst, value, n);
}

uint8_t *strings_memset0(uint8_t *dst, uint8_t value) {
  return (uint8_t *)memset(dst, value, 0);
}

uint8_t *strings_memset1(uint8_t *dst, uint8_t value) {
  return (uint8_t *)memset(dst, value, 1);
}

uint8_t *strings_memset2(uint8_t *dst, uint8_t value) {
  return (uint8_t *)memset(dst, value, 2);
}

uint8_t *strings_memset3(uint8_t *dst, uint8_t value) {
  return (uint8_t *)memset(dst, value, 3);
}

uint8_t *strings_memset4(uint8_t *dst, uint8_t value) {
  return (uint8_t *)memset(dst, value, 4);
}

uint8_t *strings_memset7(uint8_t *dst, uint8_t value) {
  return (uint8_t *)memset(dst, value, 7);
}

uint8_t *strings_memset8(uint8_t *dst, uint8_t value) {
  return (uint8_t *)memset(dst, value, 8);
}

uint8_t *strings_memset15(uint8_t *dst, uint8_t value) {
  return (uint8_t *)memset(dst, value, 15);
}

uint8_t *strings_memset16(uint8_t *dst, uint8_t value) {
  return (uint8_t *)memset(dst, value, 16);
}

uint8_t *strings_memset17(uint8_t *dst, uint8_t value) {
  return (uint8_t *)memset(dst, value, 17);
}

uint8_t *strings_memset31(uint8_t *dst, uint8_t value) {
  return (uint8_t *)memset(dst, value, 31);
}

uint8_t *strings_memset32(uint8_t *dst, uint8_t value) {
  return (uint8_t *)memset(dst, value, 32);
}

uint8_t *strings_memset63(uint8_t *dst, uint8_t value) {
  return (uint8_t *)memset(dst, value, 63);
}

uint8_t *strings_memset64(uint8_t *dst, uint8_t value) {
  return (uint8_t *)memset(dst, value, 64);
}

uint8_t *strings_memset127(uint8_t *dst, uint8_t value) {
  return (uint8_t *)memset(dst, value, 127);
}

uint8_t *strings_memset128(uint8_t *dst, uint8_t value) {
  return (uint8_t *)memset(dst, value, 128);
}

int8_t strings_memcmp(const uint8_t *a, const uint8_t *b, uint16_t n) {
  int v = memcmp(a, b, n);
  return (int8_t)((v > 0) - (v < 0));
}

int8_t strings_memcmp0(const uint8_t *a, const uint8_t *b) {
  int v = memcmp(a, b, 0);
  return (int8_t)((v > 0) - (v < 0));
}

int8_t strings_memcmp1(const uint8_t *a, const uint8_t *b) {
  int v = memcmp(a, b, 1);
  return (int8_t)((v > 0) - (v < 0));
}

int8_t strings_memcmp2(const uint8_t *a, const uint8_t *b) {
  int v = memcmp(a, b, 2);
  return (int8_t)((v > 0) - (v < 0));
}

int8_t strings_memcmp3(const uint8_t *a, const uint8_t *b) {
  int v = memcmp(a, b, 3);
  return (int8_t)((v > 0) - (v < 0));
}

int8_t strings_memcmp4(const uint8_t *a, const uint8_t *b) {
  int v = memcmp(a, b, 4);
  return (int8_t)((v > 0) - (v < 0));
}

int8_t strings_memcmp7(const uint8_t *a, const uint8_t *b) {
  int v = memcmp(a, b, 7);
  return (int8_t)((v > 0) - (v < 0));
}

int8_t strings_memcmp8(const uint8_t *a, const uint8_t *b) {
  int v = memcmp(a, b, 8);
  return (int8_t)((v > 0) - (v < 0));
}

int8_t strings_memcmp15(const uint8_t *a, const uint8_t *b) {
  int v = memcmp(a, b, 15);
  return (int8_t)((v > 0) - (v < 0));
}

int8_t strings_memcmp16(const uint8_t *a, const uint8_t *b) {
  int v = memcmp(a, b, 16);
  return (int8_t)((v > 0) - (v < 0));
}

int8_t strings_memcmp17(const uint8_t *a, const uint8_t *b) {
  int v = memcmp(a, b, 17);
  return (int8_t)((v > 0) - (v < 0));
}

int8_t strings_memcmp31(const uint8_t *a, const uint8_t *b) {
  int v = memcmp(a, b, 31);
  return (int8_t)((v > 0) - (v < 0));
}

int8_t strings_memcmp32(const uint8_t *a, const uint8_t *b) {
  int v = memcmp(a, b, 32);
  return (int8_t)((v > 0) - (v < 0));
}

int8_t strings_memcmp63(const uint8_t *a, const uint8_t *b) {
  int v = memcmp(a, b, 63);
  return (int8_t)((v > 0) - (v < 0));
}

int8_t strings_memcmp64(const uint8_t *a, const uint8_t *b) {
  int v = memcmp(a, b, 64);
  return (int8_t)((v > 0) - (v < 0));
}

int8_t strings_memcmp127(const uint8_t *a, const uint8_t *b) {
  int v = memcmp(a, b, 127);
  return (int8_t)((v > 0) - (v < 0));
}

int8_t strings_memcmp128(const uint8_t *a, const uint8_t *b) {
  int v = memcmp(a, b, 128);
  return (int8_t)((v > 0) - (v < 0));
}

uint8_t strings_memeq(const uint8_t *a, const uint8_t *b, uint16_t n) {
  return memcmp(a, b, n) == 0;
}

uint16_t strings_memchr(const uint8_t *s, uint8_t value, uint16_t n) {
  const uint8_t *p = (const uint8_t *)memchr(s, value, n);
  return p ? (uint16_t)(p - s) : UINT16_MAX;
}

uint8_t *strings_memcpy_offset1(uint8_t *dst, const uint8_t *src, uint16_t n) {
  return (uint8_t *)memcpy(dst + 1, src + 1, n);
}

uint8_t *strings_memcpy_offset3(uint8_t *dst, const uint8_t *src, uint16_t n) {
  return (uint8_t *)memcpy(dst + 3, src + 3, n);
}

uint8_t *strings_memcpy_offset7(uint8_t *dst, const uint8_t *src, uint16_t n) {
  return (uint8_t *)memcpy(dst + 7, src + 7, n);
}
