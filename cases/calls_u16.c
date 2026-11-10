#include <stdint.h>
#if defined(__SDCC)
#define NOINLINE
#else
#define NOINLINE __attribute__((noinline))
#endif

NOINLINE uint16_t fixture_leaf_u16(uint16_t a, uint16_t b) {
  return (uint16_t)(a + b);
}

NOINLINE uint16_t fixture_six_u16(uint16_t a, uint16_t b, uint16_t c,
                                  uint16_t d, uint16_t e, uint16_t f) {
  return (uint16_t)(a ^ b ^ c ^ d ^ e ^ f);
}

NOINLINE uint16_t fixture_touch_u16(uint8_t *p, uint16_t a) {
  p[0] ^= (uint8_t)a;
  p[7] = (uint8_t)(p[7] + 1u);
  return (uint16_t)p[7];
}

uint16_t calls_u16_leaf(uint16_t a, uint16_t b) { return (uint16_t)(a + b); }

uint16_t calls_u16_tail(uint16_t a, uint16_t b) {
  return fixture_leaf_u16(a, b);
}

uint16_t calls_u16_post(uint16_t a, uint16_t b) {
  return (uint16_t)(fixture_leaf_u16(a, b) + 1u);
}

uint16_t calls_u16_chain(uint16_t a, uint16_t b, uint16_t c) {
  uint16_t x = fixture_leaf_u16(a, b);
  return fixture_leaf_u16(x, c);
}

uint16_t calls_u16_args6(uint16_t a, uint16_t b, uint16_t c, uint16_t d,
                         uint16_t e, uint16_t f) {
  return fixture_six_u16(a, b, c, d, e, f);
}

uint16_t calls_u16_indirect(uint16_t (*f)(uint16_t, uint16_t), uint16_t a,
                            uint16_t b) {
  return f(a, b);
}

uint16_t calls_u16_live2(const volatile uint16_t *p, uint16_t a, uint16_t b) {
  uint16_t v0 = p[0];
  uint16_t v1 = p[1];
  uint16_t r = fixture_leaf_u16(a, b);
  r = (uint16_t)((r ^ v0) + (r >> 1));
  r = (uint16_t)((r ^ v1) + (r >> 1));
  return r;
}

uint16_t calls_u16_live2_inline(const volatile uint16_t *p, uint16_t a,
                                uint16_t b) {
  uint16_t v0 = p[0];
  uint16_t v1 = p[1];
  uint16_t r = (uint16_t)(a + b);
  r = (uint16_t)((r ^ v0) + (r >> 1));
  r = (uint16_t)((r ^ v1) + (r >> 1));
  return r;
}

uint16_t calls_u16_live4(const volatile uint16_t *p, uint16_t a, uint16_t b) {
  uint16_t v0 = p[0];
  uint16_t v1 = p[1];
  uint16_t v2 = p[2];
  uint16_t v3 = p[3];
  uint16_t r = fixture_leaf_u16(a, b);
  r = (uint16_t)((r ^ v0) + (r >> 1));
  r = (uint16_t)((r ^ v1) + (r >> 1));
  r = (uint16_t)((r ^ v2) + (r >> 1));
  r = (uint16_t)((r ^ v3) + (r >> 1));
  return r;
}

uint16_t calls_u16_live4_inline(const volatile uint16_t *p, uint16_t a,
                                uint16_t b) {
  uint16_t v0 = p[0];
  uint16_t v1 = p[1];
  uint16_t v2 = p[2];
  uint16_t v3 = p[3];
  uint16_t r = (uint16_t)(a + b);
  r = (uint16_t)((r ^ v0) + (r >> 1));
  r = (uint16_t)((r ^ v1) + (r >> 1));
  r = (uint16_t)((r ^ v2) + (r >> 1));
  r = (uint16_t)((r ^ v3) + (r >> 1));
  return r;
}

uint16_t calls_u16_live8(const volatile uint16_t *p, uint16_t a, uint16_t b) {
  uint16_t v0 = p[0];
  uint16_t v1 = p[1];
  uint16_t v2 = p[2];
  uint16_t v3 = p[3];
  uint16_t v4 = p[4];
  uint16_t v5 = p[5];
  uint16_t v6 = p[6];
  uint16_t v7 = p[7];
  uint16_t r = fixture_leaf_u16(a, b);
  r = (uint16_t)((r ^ v0) + (r >> 1));
  r = (uint16_t)((r ^ v1) + (r >> 1));
  r = (uint16_t)((r ^ v2) + (r >> 1));
  r = (uint16_t)((r ^ v3) + (r >> 1));
  r = (uint16_t)((r ^ v4) + (r >> 1));
  r = (uint16_t)((r ^ v5) + (r >> 1));
  r = (uint16_t)((r ^ v6) + (r >> 1));
  r = (uint16_t)((r ^ v7) + (r >> 1));
  return r;
}

uint16_t calls_u16_live8_inline(const volatile uint16_t *p, uint16_t a,
                                uint16_t b) {
  uint16_t v0 = p[0];
  uint16_t v1 = p[1];
  uint16_t v2 = p[2];
  uint16_t v3 = p[3];
  uint16_t v4 = p[4];
  uint16_t v5 = p[5];
  uint16_t v6 = p[6];
  uint16_t v7 = p[7];
  uint16_t r = (uint16_t)(a + b);
  r = (uint16_t)((r ^ v0) + (r >> 1));
  r = (uint16_t)((r ^ v1) + (r >> 1));
  r = (uint16_t)((r ^ v2) + (r >> 1));
  r = (uint16_t)((r ^ v3) + (r >> 1));
  r = (uint16_t)((r ^ v4) + (r >> 1));
  r = (uint16_t)((r ^ v5) + (r >> 1));
  r = (uint16_t)((r ^ v6) + (r >> 1));
  r = (uint16_t)((r ^ v7) + (r >> 1));
  return r;
}

uint16_t calls_u16_local8(uint16_t a, uint16_t b) {
  uint8_t p[8];
  for (uint8_t i = 0; i < 8; ++i)
    p[i] = (uint8_t)(a + i);
  uint16_t r = fixture_touch_u16(p, b);
  return (uint16_t)(r + (uint16_t)p[0] + (uint16_t)p[7]);
}

uint16_t calls_u16_local32(uint16_t a, uint16_t b) {
  uint8_t p[32];
  for (uint8_t i = 0; i < 32; ++i)
    p[i] = (uint8_t)(a + i);
  uint16_t r = fixture_touch_u16(p, b);
  return (uint16_t)(r + (uint16_t)p[0] + (uint16_t)p[31]);
}
