#![no_std]

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn fixture_leaf_u32(a : u32, b : u32) -> u32{a.wrapping_add(b)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn
    fixture_six_u32(a : u32, b : u32, c : u32, d : u32, e : u32, f : u32)
        ->u32{a ^ b ^ c ^ d ^ e ^ f}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn fixture_touch_u32(p : *mut u8, a : u32)
        ->u32 {
  unsafe {
    *p ^= a as u8;
    *p.add(7) = (*p.add(7)).wrapping_add(1);
    *p.add(7) as u32
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn calls_u32_leaf(a : u32, b : u32) -> u32 {
  unsafe { a.wrapping_add(b) }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn calls_u32_tail(a : u32, b : u32) -> u32 {
  unsafe { fixture_leaf_u32(a, b) }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn calls_u32_post(a : u32, b : u32) -> u32 {
  unsafe { fixture_leaf_u32(a, b).wrapping_add(1) }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn calls_u32_chain(a : u32, b : u32, c : u32) -> u32 {
  unsafe {
    let x = fixture_leaf_u32(a, b);
    fixture_leaf_u32(x, c)
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn calls_u32_args6(a : u32, b : u32, c : u32, d : u32,
                                         e : u32, f : u32) -> u32 {
  unsafe { fixture_six_u32(a, b, c, d, e, f) }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn calls_u32_indirect(f : extern "C" fn(u32, u32)->u32,
                                            a : u32, b : u32, ) -> u32 {
  unsafe { f(a, b) }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn calls_u32_live2(p : *const u32, a : u32, b : u32)
    -> u32 {
  unsafe {
    let v0 = core::ptr::read_volatile(p.add(0));
    let v1 = core::ptr::read_volatile(p.add(1));
    let mut r = fixture_leaf_u32(a, b);
    r = (r ^ v0).wrapping_add(r >> 1);
    r = (r ^ v1).wrapping_add(r >> 1);
    r
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn calls_u32_live2_inline(p : *const u32, a : u32,
                                                b : u32) -> u32 {
  unsafe {
    let v0 = core::ptr::read_volatile(p.add(0));
    let v1 = core::ptr::read_volatile(p.add(1));
    let mut r = a.wrapping_add(b);
    r = (r ^ v0).wrapping_add(r >> 1);
    r = (r ^ v1).wrapping_add(r >> 1);
    r
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn calls_u32_live4(p : *const u32, a : u32, b : u32)
    -> u32 {
  unsafe {
    let v0 = core::ptr::read_volatile(p.add(0));
    let v1 = core::ptr::read_volatile(p.add(1));
    let v2 = core::ptr::read_volatile(p.add(2));
    let v3 = core::ptr::read_volatile(p.add(3));
    let mut r = fixture_leaf_u32(a, b);
    r = (r ^ v0).wrapping_add(r >> 1);
    r = (r ^ v1).wrapping_add(r >> 1);
    r = (r ^ v2).wrapping_add(r >> 1);
    r = (r ^ v3).wrapping_add(r >> 1);
    r
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn calls_u32_live4_inline(p : *const u32, a : u32,
                                                b : u32) -> u32 {
  unsafe {
    let v0 = core::ptr::read_volatile(p.add(0));
    let v1 = core::ptr::read_volatile(p.add(1));
    let v2 = core::ptr::read_volatile(p.add(2));
    let v3 = core::ptr::read_volatile(p.add(3));
    let mut r = a.wrapping_add(b);
    r = (r ^ v0).wrapping_add(r >> 1);
    r = (r ^ v1).wrapping_add(r >> 1);
    r = (r ^ v2).wrapping_add(r >> 1);
    r = (r ^ v3).wrapping_add(r >> 1);
    r
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn calls_u32_live8(p : *const u32, a : u32, b : u32)
    -> u32 {
  unsafe {
    let v0 = core::ptr::read_volatile(p.add(0));
    let v1 = core::ptr::read_volatile(p.add(1));
    let v2 = core::ptr::read_volatile(p.add(2));
    let v3 = core::ptr::read_volatile(p.add(3));
    let v4 = core::ptr::read_volatile(p.add(4));
    let v5 = core::ptr::read_volatile(p.add(5));
    let v6 = core::ptr::read_volatile(p.add(6));
    let v7 = core::ptr::read_volatile(p.add(7));
    let mut r = fixture_leaf_u32(a, b);
    r = (r ^ v0).wrapping_add(r >> 1);
    r = (r ^ v1).wrapping_add(r >> 1);
    r = (r ^ v2).wrapping_add(r >> 1);
    r = (r ^ v3).wrapping_add(r >> 1);
    r = (r ^ v4).wrapping_add(r >> 1);
    r = (r ^ v5).wrapping_add(r >> 1);
    r = (r ^ v6).wrapping_add(r >> 1);
    r = (r ^ v7).wrapping_add(r >> 1);
    r
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn calls_u32_live8_inline(p : *const u32, a : u32,
                                                b : u32) -> u32 {
  unsafe {
    let v0 = core::ptr::read_volatile(p.add(0));
    let v1 = core::ptr::read_volatile(p.add(1));
    let v2 = core::ptr::read_volatile(p.add(2));
    let v3 = core::ptr::read_volatile(p.add(3));
    let v4 = core::ptr::read_volatile(p.add(4));
    let v5 = core::ptr::read_volatile(p.add(5));
    let v6 = core::ptr::read_volatile(p.add(6));
    let v7 = core::ptr::read_volatile(p.add(7));
    let mut r = a.wrapping_add(b);
    r = (r ^ v0).wrapping_add(r >> 1);
    r = (r ^ v1).wrapping_add(r >> 1);
    r = (r ^ v2).wrapping_add(r >> 1);
    r = (r ^ v3).wrapping_add(r >> 1);
    r = (r ^ v4).wrapping_add(r >> 1);
    r = (r ^ v5).wrapping_add(r >> 1);
    r = (r ^ v6).wrapping_add(r >> 1);
    r = (r ^ v7).wrapping_add(r >> 1);
    r
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn calls_u32_local8(a : u32, b : u32) -> u32 {
  unsafe {
    let mut storage = core::mem::MaybeUninit::<[u8; 8]>::uninit();
    let p = storage.as_mut_ptr().cast::<u8>();
        for
          i in 0..8 { *p.add(i) = (a as u8).wrapping_add(i as u8); }
        let r = fixture_touch_u32(p, b);
        r.wrapping_add(*p as u32).wrapping_add(*p.add(7) as u32)
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn calls_u32_local32(a : u32, b : u32) -> u32 {
  unsafe {
    let mut storage = core::mem::MaybeUninit::<[u8; 32]>::uninit();
    let p = storage.as_mut_ptr().cast::<u8>();
        for
          i in 0..32 { *p.add(i) = (a as u8).wrapping_add(i as u8); }
        let r = fixture_touch_u32(p, b);
        r.wrapping_add(*p as u32).wrapping_add(*p.add(31) as u32)
  }
}
