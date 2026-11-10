#include <stdint.h>
#if defined(__SDCC)
#define NOINLINE
#else
#define NOINLINE __attribute__((noinline))
#endif

NOINLINE uint64_t fixture_leaf_u64(uint64_t a, uint64_t b) {
  return (uint64_t)(a + b);
}

NOINLINE uint64_t fixture_six_u64(uint64_t a, uint64_t b, uint64_t c,
                                  uint64_t d, uint64_t e, uint64_t f) {
  return (uint64_t)(a ^ b ^ c ^ d ^ e ^ f);
}

NOINLINE uint64_t fixture_touch_u64(uint8_t *p, uint64_t a) {
  p[0] ^= (uint8_t)a;
  p[7] = (uint8_t)(p[7] + 1u);
  return (uint64_t)p[7];
}

uint64_t calls_u64_leaf(uint64_t a, uint64_t b) { return (uint64_t)(a + b); }

uint64_t calls_u64_tail(uint64_t a, uint64_t b) {
  return fixture_leaf_u64(a, b);
}

uint64_t calls_u64_post(uint64_t a, uint64_t b) {
  return (uint64_t)(fixture_leaf_u64(a, b) + 1u);
}

uint64_t calls_u64_chain(uint64_t a, uint64_t b, uint64_t c) {
  uint64_t x = fixture_leaf_u64(a, b);
  return fixture_leaf_u64(x, c);
}

uint64_t calls_u64_args6(uint64_t a, uint64_t b, uint64_t c, uint64_t d,
                         uint64_t e, uint64_t f) {
  return fixture_six_u64(a, b, c, d, e, f);
}

uint64_t calls_u64_indirect(uint64_t (*f)(uint64_t, uint64_t), uint64_t a,
                            uint64_t b) {
  return f(a, b);
}

uint64_t calls_u64_live2(const volatile uint64_t *p, uint64_t a, uint64_t b) {
  uint64_t v0 = p[0];
  uint64_t v1 = p[1];
  uint64_t r = fixture_leaf_u64(a, b);
  r = (uint64_t)((r ^ v0) + (r >> 1));
  r = (uint64_t)((r ^ v1) + (r >> 1));
  return r;
}

uint64_t calls_u64_live2_inline(const volatile uint64_t *p, uint64_t a,
                                uint64_t b) {
  uint64_t v0 = p[0];
  uint64_t v1 = p[1];
  uint64_t r = (uint64_t)(a + b);
  r = (uint64_t)((r ^ v0) + (r >> 1));
  r = (uint64_t)((r ^ v1) + (r >> 1));
  return r;
}

uint64_t calls_u64_live4(const volatile uint64_t *p, uint64_t a, uint64_t b) {
  uint64_t v0 = p[0];
  uint64_t v1 = p[1];
  uint64_t v2 = p[2];
  uint64_t v3 = p[3];
  uint64_t r = fixture_leaf_u64(a, b);
  r = (uint64_t)((r ^ v0) + (r >> 1));
  r = (uint64_t)((r ^ v1) + (r >> 1));
  r = (uint64_t)((r ^ v2) + (r >> 1));
  r = (uint64_t)((r ^ v3) + (r >> 1));
  return r;
}

uint64_t calls_u64_live4_inline(const volatile uint64_t *p, uint64_t a,
                                uint64_t b) {
  uint64_t v0 = p[0];
  uint64_t v1 = p[1];
  uint64_t v2 = p[2];
  uint64_t v3 = p[3];
  uint64_t r = (uint64_t)(a + b);
  r = (uint64_t)((r ^ v0) + (r >> 1));
  r = (uint64_t)((r ^ v1) + (r >> 1));
  r = (uint64_t)((r ^ v2) + (r >> 1));
  r = (uint64_t)((r ^ v3) + (r >> 1));
  return r;
}

uint64_t calls_u64_live8(const volatile uint64_t *p, uint64_t a, uint64_t b) {
  uint64_t v0 = p[0];
  uint64_t v1 = p[1];
  uint64_t v2 = p[2];
  uint64_t v3 = p[3];
  uint64_t v4 = p[4];
  uint64_t v5 = p[5];
  uint64_t v6 = p[6];
  uint64_t v7 = p[7];
  uint64_t r = fixture_leaf_u64(a, b);
  r = (uint64_t)((r ^ v0) + (r >> 1));
  r = (uint64_t)((r ^ v1) + (r >> 1));
  r = (uint64_t)((r ^ v2) + (r >> 1));
  r = (uint64_t)((r ^ v3) + (r >> 1));
  r = (uint64_t)((r ^ v4) + (r >> 1));
  r = (uint64_t)((r ^ v5) + (r >> 1));
  r = (uint64_t)((r ^ v6) + (r >> 1));
  r = (uint64_t)((r ^ v7) + (r >> 1));
  return r;
}

uint64_t calls_u64_live8_inline(const volatile uint64_t *p, uint64_t a,
                                uint64_t b) {
  uint64_t v0 = p[0];
  uint64_t v1 = p[1];
  uint64_t v2 = p[2];
  uint64_t v3 = p[3];
  uint64_t v4 = p[4];
  uint64_t v5 = p[5];
  uint64_t v6 = p[6];
  uint64_t v7 = p[7];
  uint64_t r = (uint64_t)(a + b);
  r = (uint64_t)((r ^ v0) + (r >> 1));
  r = (uint64_t)((r ^ v1) + (r >> 1));
  r = (uint64_t)((r ^ v2) + (r >> 1));
  r = (uint64_t)((r ^ v3) + (r >> 1));
  r = (uint64_t)((r ^ v4) + (r >> 1));
  r = (uint64_t)((r ^ v5) + (r >> 1));
  r = (uint64_t)((r ^ v6) + (r >> 1));
  r = (uint64_t)((r ^ v7) + (r >> 1));
  return r;
}

uint64_t calls_u64_local8(uint64_t a, uint64_t b) {
  uint8_t p[8];
  for (uint8_t i = 0; i < 8; ++i)
    p[i] = (uint8_t)(a + i);
  uint64_t r = fixture_touch_u64(p, b);
  return (uint64_t)(r + (uint64_t)p[0] + (uint64_t)p[7]);
}

uint64_t calls_u64_local32(uint64_t a, uint64_t b) {
  uint8_t p[32];
  for (uint8_t i = 0; i < 32; ++i)
    p[i] = (uint8_t)(a + i);
  uint64_t r = fixture_touch_u64(p, b);
  return (uint64_t)(r + (uint64_t)p[0] + (uint64_t)p[31]);
}
