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

uint16_t packing_load_le16(const uint8_t *src) {
  return ((uint16_t)src[0] << 0) | ((uint16_t)src[1] << 8);
}

uint8_t *packing_store_le16(uint8_t *dst, uint16_t value) {
  dst[0] = (uint8_t)(value >> 0);
  dst[1] = (uint8_t)(value >> 8);
  return dst;
}

uint16_t packing_load_be16(const uint8_t *src) {
  return ((uint16_t)src[0] << 8) | ((uint16_t)src[1] << 0);
}

uint8_t *packing_store_be16(uint8_t *dst, uint16_t value) {
  dst[0] = (uint8_t)(value >> 8);
  dst[1] = (uint8_t)(value >> 0);
  return dst;
}

uint32_t packing_load_le32(const uint8_t *src) {
  return ((uint32_t)src[0] << 0) | ((uint32_t)src[1] << 8) |
         ((uint32_t)src[2] << 16) | ((uint32_t)src[3] << 24);
}

uint8_t *packing_store_le32(uint8_t *dst, uint32_t value) {
  dst[0] = (uint8_t)(value >> 0);
  dst[1] = (uint8_t)(value >> 8);
  dst[2] = (uint8_t)(value >> 16);
  dst[3] = (uint8_t)(value >> 24);
  return dst;
}

uint32_t packing_load_be32(const uint8_t *src) {
  return ((uint32_t)src[0] << 24) | ((uint32_t)src[1] << 16) |
         ((uint32_t)src[2] << 8) | ((uint32_t)src[3] << 0);
}

uint8_t *packing_store_be32(uint8_t *dst, uint32_t value) {
  dst[0] = (uint8_t)(value >> 24);
  dst[1] = (uint8_t)(value >> 16);
  dst[2] = (uint8_t)(value >> 8);
  dst[3] = (uint8_t)(value >> 0);
  return dst;
}

uint64_t packing_load_le64(const uint8_t *src) {
  return ((uint64_t)src[0] << 0) | ((uint64_t)src[1] << 8) |
         ((uint64_t)src[2] << 16) | ((uint64_t)src[3] << 24) |
         ((uint64_t)src[4] << 32) | ((uint64_t)src[5] << 40) |
         ((uint64_t)src[6] << 48) | ((uint64_t)src[7] << 56);
}

uint8_t *packing_store_le64(uint8_t *dst, uint64_t value) {
  dst[0] = (uint8_t)(value >> 0);
  dst[1] = (uint8_t)(value >> 8);
  dst[2] = (uint8_t)(value >> 16);
  dst[3] = (uint8_t)(value >> 24);
  dst[4] = (uint8_t)(value >> 32);
  dst[5] = (uint8_t)(value >> 40);
  dst[6] = (uint8_t)(value >> 48);
  dst[7] = (uint8_t)(value >> 56);
  return dst;
}

uint64_t packing_load_be64(const uint8_t *src) {
  return ((uint64_t)src[0] << 56) | ((uint64_t)src[1] << 48) |
         ((uint64_t)src[2] << 40) | ((uint64_t)src[3] << 32) |
         ((uint64_t)src[4] << 24) | ((uint64_t)src[5] << 16) |
         ((uint64_t)src[6] << 8) | ((uint64_t)src[7] << 0);
}

uint8_t *packing_store_be64(uint8_t *dst, uint64_t value) {
  dst[0] = (uint8_t)(value >> 56);
  dst[1] = (uint8_t)(value >> 48);
  dst[2] = (uint8_t)(value >> 40);
  dst[3] = (uint8_t)(value >> 32);
  dst[4] = (uint8_t)(value >> 24);
  dst[5] = (uint8_t)(value >> 16);
  dst[6] = (uint8_t)(value >> 8);
  dst[7] = (uint8_t)(value >> 0);
  return dst;
}
