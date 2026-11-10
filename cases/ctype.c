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

uint8_t ctype_isdigit_loop(uint8_t value) {
  return (uint8_t)(value >= '0' && value <= '9');
}

uint8_t ctype_isdigit_library(uint8_t value) {
  return (uint8_t)(value < 128 && isdigit(value) != 0);
}

uint8_t ctype_isalpha_loop(uint8_t value) {
  return (uint8_t)((value >= 'A' && value <= 'Z') ||
                   (value >= 'a' && value <= 'z'));
}

uint8_t ctype_isalpha_library(uint8_t value) {
  return (uint8_t)(value < 128 && isalpha(value) != 0);
}

uint8_t ctype_isspace_loop(uint8_t value) {
  return (uint8_t)(value == ' ' || (value >= 9 && value <= 13));
}

uint8_t ctype_isspace_library(uint8_t value) {
  return (uint8_t)(value < 128 && isspace(value) != 0);
}

uint8_t ctype_tolower_loop(uint8_t value) {
  return (uint8_t)(value >= 'A' && value <= 'Z' ? value + ('a' - 'A') : value);
}

uint8_t ctype_tolower_library(uint8_t value) {
  return (uint8_t)(value < 128 ? tolower(value) : value);
}

uint8_t ctype_toupper_loop(uint8_t value) {
  return (uint8_t)(value >= 'a' && value <= 'z' ? value - ('a' - 'A') : value);
}

uint8_t ctype_toupper_library(uint8_t value) {
  return (uint8_t)(value < 128 ? toupper(value) : value);
}
