#include <stdint.h>
#if defined(__SDCC)
#define NOINLINE
#else
#define NOINLINE __attribute__((noinline))
#endif

NOINLINE uint32_t fixture_leaf_u32(uint32_t a, uint32_t b) {
  return (uint32_t)(a + b);
}

NOINLINE uint32_t fixture_six_u32(uint32_t a, uint32_t b, uint32_t c,
                                  uint32_t d, uint32_t e, uint32_t f) {
  return (uint32_t)(a ^ b ^ c ^ d ^ e ^ f);
}

NOINLINE uint32_t fixture_touch_u32(uint8_t *p, uint32_t a) {
  p[0] ^= (uint8_t)a;
  p[7] = (uint8_t)(p[7] + 1u);
  return (uint32_t)p[7];
}

uint32_t calls_u32_leaf(uint32_t a, uint32_t b) { return (uint32_t)(a + b); }

uint32_t calls_u32_tail(uint32_t a, uint32_t b) {
  return fixture_leaf_u32(a, b);
}

uint32_t calls_u32_post(uint32_t a, uint32_t b) {
  return (uint32_t)(fixture_leaf_u32(a, b) + 1u);
}

uint32_t calls_u32_chain(uint32_t a, uint32_t b, uint32_t c) {
  uint32_t x = fixture_leaf_u32(a, b);
  return fixture_leaf_u32(x, c);
}

uint32_t calls_u32_args6(uint32_t a, uint32_t b, uint32_t c, uint32_t d,
                         uint32_t e, uint32_t f) {
  return fixture_six_u32(a, b, c, d, e, f);
}

uint32_t calls_u32_indirect(uint32_t (*f)(uint32_t, uint32_t), uint32_t a,
                            uint32_t b) {
  return f(a, b);
}

uint32_t calls_u32_live2(const volatile uint32_t *p, uint32_t a, uint32_t b) {
  uint32_t v0 = p[0];
  uint32_t v1 = p[1];
  uint32_t r = fixture_leaf_u32(a, b);
  r = (uint32_t)((r ^ v0) + (r >> 1));
  r = (uint32_t)((r ^ v1) + (r >> 1));
  return r;
}

uint32_t calls_u32_live2_inline(const volatile uint32_t *p, uint32_t a,
                                uint32_t b) {
  uint32_t v0 = p[0];
  uint32_t v1 = p[1];
  uint32_t r = (uint32_t)(a + b);
  r = (uint32_t)((r ^ v0) + (r >> 1));
  r = (uint32_t)((r ^ v1) + (r >> 1));
  return r;
}

uint32_t calls_u32_live4(const volatile uint32_t *p, uint32_t a, uint32_t b) {
  uint32_t v0 = p[0];
  uint32_t v1 = p[1];
  uint32_t v2 = p[2];
  uint32_t v3 = p[3];
  uint32_t r = fixture_leaf_u32(a, b);
  r = (uint32_t)((r ^ v0) + (r >> 1));
  r = (uint32_t)((r ^ v1) + (r >> 1));
  r = (uint32_t)((r ^ v2) + (r >> 1));
  r = (uint32_t)((r ^ v3) + (r >> 1));
  return r;
}

uint32_t calls_u32_live4_inline(const volatile uint32_t *p, uint32_t a,
                                uint32_t b) {
  uint32_t v0 = p[0];
  uint32_t v1 = p[1];
  uint32_t v2 = p[2];
  uint32_t v3 = p[3];
  uint32_t r = (uint32_t)(a + b);
  r = (uint32_t)((r ^ v0) + (r >> 1));
  r = (uint32_t)((r ^ v1) + (r >> 1));
  r = (uint32_t)((r ^ v2) + (r >> 1));
  r = (uint32_t)((r ^ v3) + (r >> 1));
  return r;
}

uint32_t calls_u32_live8(const volatile uint32_t *p, uint32_t a, uint32_t b) {
  uint32_t v0 = p[0];
  uint32_t v1 = p[1];
  uint32_t v2 = p[2];
  uint32_t v3 = p[3];
  uint32_t v4 = p[4];
  uint32_t v5 = p[5];
  uint32_t v6 = p[6];
  uint32_t v7 = p[7];
  uint32_t r = fixture_leaf_u32(a, b);
  r = (uint32_t)((r ^ v0) + (r >> 1));
  r = (uint32_t)((r ^ v1) + (r >> 1));
  r = (uint32_t)((r ^ v2) + (r >> 1));
  r = (uint32_t)((r ^ v3) + (r >> 1));
  r = (uint32_t)((r ^ v4) + (r >> 1));
  r = (uint32_t)((r ^ v5) + (r >> 1));
  r = (uint32_t)((r ^ v6) + (r >> 1));
  r = (uint32_t)((r ^ v7) + (r >> 1));
  return r;
}

uint32_t calls_u32_live8_inline(const volatile uint32_t *p, uint32_t a,
                                uint32_t b) {
  uint32_t v0 = p[0];
  uint32_t v1 = p[1];
  uint32_t v2 = p[2];
  uint32_t v3 = p[3];
  uint32_t v4 = p[4];
  uint32_t v5 = p[5];
  uint32_t v6 = p[6];
  uint32_t v7 = p[7];
  uint32_t r = (uint32_t)(a + b);
  r = (uint32_t)((r ^ v0) + (r >> 1));
  r = (uint32_t)((r ^ v1) + (r >> 1));
  r = (uint32_t)((r ^ v2) + (r >> 1));
  r = (uint32_t)((r ^ v3) + (r >> 1));
  r = (uint32_t)((r ^ v4) + (r >> 1));
  r = (uint32_t)((r ^ v5) + (r >> 1));
  r = (uint32_t)((r ^ v6) + (r >> 1));
  r = (uint32_t)((r ^ v7) + (r >> 1));
  return r;
}

uint32_t calls_u32_local8(uint32_t a, uint32_t b) {
  uint8_t p[8];
  for (uint8_t i = 0; i < 8; ++i)
    p[i] = (uint8_t)(a + i);
  uint32_t r = fixture_touch_u32(p, b);
  return (uint32_t)(r + (uint32_t)p[0] + (uint32_t)p[7]);
}

uint32_t calls_u32_local32(uint32_t a, uint32_t b) {
  uint8_t p[32];
  for (uint8_t i = 0; i < 32; ++i)
    p[i] = (uint8_t)(a + i);
  uint32_t r = fixture_touch_u32(p, b);
  return (uint32_t)(r + (uint32_t)p[0] + (uint32_t)p[31]);
}
