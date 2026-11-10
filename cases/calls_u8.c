#include <stdint.h>
#if defined(__SDCC)
#define NOINLINE
#else
#define NOINLINE __attribute__((noinline))
#endif

NOINLINE uint8_t fixture_leaf_u8(uint8_t a, uint8_t b) {
  return (uint8_t)(a + b);
}

NOINLINE uint8_t fixture_six_u8(uint8_t a, uint8_t b, uint8_t c, uint8_t d,
                                uint8_t e, uint8_t f) {
  return (uint8_t)(a ^ b ^ c ^ d ^ e ^ f);
}

NOINLINE uint8_t fixture_touch_u8(uint8_t *p, uint8_t a) {
  p[0] ^= (uint8_t)a;
  p[7] = (uint8_t)(p[7] + 1u);
  return (uint8_t)p[7];
}

uint8_t calls_u8_leaf(uint8_t a, uint8_t b) { return (uint8_t)(a + b); }

uint8_t calls_u8_tail(uint8_t a, uint8_t b) { return fixture_leaf_u8(a, b); }

uint8_t calls_u8_post(uint8_t a, uint8_t b) {
  return (uint8_t)(fixture_leaf_u8(a, b) + 1u);
}

uint8_t calls_u8_chain(uint8_t a, uint8_t b, uint8_t c) {
  uint8_t x = fixture_leaf_u8(a, b);
  return fixture_leaf_u8(x, c);
}

uint8_t calls_u8_args6(uint8_t a, uint8_t b, uint8_t c, uint8_t d, uint8_t e,
                       uint8_t f) {
  return fixture_six_u8(a, b, c, d, e, f);
}

uint8_t calls_u8_indirect(uint8_t (*f)(uint8_t, uint8_t), uint8_t a,
                          uint8_t b) {
  return f(a, b);
}

uint8_t calls_u8_live2(const volatile uint8_t *p, uint8_t a, uint8_t b) {
  uint8_t v0 = p[0];
  uint8_t v1 = p[1];
  uint8_t r = fixture_leaf_u8(a, b);
  r = (uint8_t)((r ^ v0) + (r >> 1));
  r = (uint8_t)((r ^ v1) + (r >> 1));
  return r;
}

uint8_t calls_u8_live2_inline(const volatile uint8_t *p, uint8_t a, uint8_t b) {
  uint8_t v0 = p[0];
  uint8_t v1 = p[1];
  uint8_t r = (uint8_t)(a + b);
  r = (uint8_t)((r ^ v0) + (r >> 1));
  r = (uint8_t)((r ^ v1) + (r >> 1));
  return r;
}

uint8_t calls_u8_live4(const volatile uint8_t *p, uint8_t a, uint8_t b) {
  uint8_t v0 = p[0];
  uint8_t v1 = p[1];
  uint8_t v2 = p[2];
  uint8_t v3 = p[3];
  uint8_t r = fixture_leaf_u8(a, b);
  r = (uint8_t)((r ^ v0) + (r >> 1));
  r = (uint8_t)((r ^ v1) + (r >> 1));
  r = (uint8_t)((r ^ v2) + (r >> 1));
  r = (uint8_t)((r ^ v3) + (r >> 1));
  return r;
}

uint8_t calls_u8_live4_inline(const volatile uint8_t *p, uint8_t a, uint8_t b) {
  uint8_t v0 = p[0];
  uint8_t v1 = p[1];
  uint8_t v2 = p[2];
  uint8_t v3 = p[3];
  uint8_t r = (uint8_t)(a + b);
  r = (uint8_t)((r ^ v0) + (r >> 1));
  r = (uint8_t)((r ^ v1) + (r >> 1));
  r = (uint8_t)((r ^ v2) + (r >> 1));
  r = (uint8_t)((r ^ v3) + (r >> 1));
  return r;
}

uint8_t calls_u8_live8(const volatile uint8_t *p, uint8_t a, uint8_t b) {
  uint8_t v0 = p[0];
  uint8_t v1 = p[1];
  uint8_t v2 = p[2];
  uint8_t v3 = p[3];
  uint8_t v4 = p[4];
  uint8_t v5 = p[5];
  uint8_t v6 = p[6];
  uint8_t v7 = p[7];
  uint8_t r = fixture_leaf_u8(a, b);
  r = (uint8_t)((r ^ v0) + (r >> 1));
  r = (uint8_t)((r ^ v1) + (r >> 1));
  r = (uint8_t)((r ^ v2) + (r >> 1));
  r = (uint8_t)((r ^ v3) + (r >> 1));
  r = (uint8_t)((r ^ v4) + (r >> 1));
  r = (uint8_t)((r ^ v5) + (r >> 1));
  r = (uint8_t)((r ^ v6) + (r >> 1));
  r = (uint8_t)((r ^ v7) + (r >> 1));
  return r;
}

uint8_t calls_u8_live8_inline(const volatile uint8_t *p, uint8_t a, uint8_t b) {
  uint8_t v0 = p[0];
  uint8_t v1 = p[1];
  uint8_t v2 = p[2];
  uint8_t v3 = p[3];
  uint8_t v4 = p[4];
  uint8_t v5 = p[5];
  uint8_t v6 = p[6];
  uint8_t v7 = p[7];
  uint8_t r = (uint8_t)(a + b);
  r = (uint8_t)((r ^ v0) + (r >> 1));
  r = (uint8_t)((r ^ v1) + (r >> 1));
  r = (uint8_t)((r ^ v2) + (r >> 1));
  r = (uint8_t)((r ^ v3) + (r >> 1));
  r = (uint8_t)((r ^ v4) + (r >> 1));
  r = (uint8_t)((r ^ v5) + (r >> 1));
  r = (uint8_t)((r ^ v6) + (r >> 1));
  r = (uint8_t)((r ^ v7) + (r >> 1));
  return r;
}

uint8_t calls_u8_local8(uint8_t a, uint8_t b) {
  uint8_t p[8];
  for (uint8_t i = 0; i < 8; ++i)
    p[i] = (uint8_t)(a + i);
  uint8_t r = fixture_touch_u8(p, b);
  return (uint8_t)(r + (uint8_t)p[0] + (uint8_t)p[7]);
}

uint8_t calls_u8_local32(uint8_t a, uint8_t b) {
  uint8_t p[32];
  for (uint8_t i = 0; i < 32; ++i)
    p[i] = (uint8_t)(a + i);
  uint8_t r = fixture_touch_u8(p, b);
  return (uint8_t)(r + (uint8_t)p[0] + (uint8_t)p[31]);
}
