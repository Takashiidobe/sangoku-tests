#![no_std]

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn fixture_leaf_u16(a : u16, b : u16) -> u16{a.wrapping_add(b)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn
    fixture_six_u16(a : u16, b : u16, c : u16, d : u16, e : u16, f : u16)
        ->u16{a ^ b ^ c ^ d ^ e ^ f}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn fixture_touch_u16(p : *mut u8, a : u16)
        ->u16 {
  unsafe {
    *p ^= a as u8;
    *p.add(7) = (*p.add(7)).wrapping_add(1);
    *p.add(7) as u16
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn calls_u16_leaf(a : u16, b : u16) -> u16 {
  unsafe { a.wrapping_add(b) }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn calls_u16_tail(a : u16, b : u16) -> u16 {
  unsafe { fixture_leaf_u16(a, b) }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn calls_u16_post(a : u16, b : u16) -> u16 {
  unsafe { fixture_leaf_u16(a, b).wrapping_add(1) }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn calls_u16_chain(a : u16, b : u16, c : u16) -> u16 {
  unsafe {
    let x = fixture_leaf_u16(a, b);
    fixture_leaf_u16(x, c)
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn calls_u16_args6(a : u16, b : u16, c : u16, d : u16,
                                         e : u16, f : u16) -> u16 {
  unsafe { fixture_six_u16(a, b, c, d, e, f) }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn calls_u16_indirect(f : extern "C" fn(u16, u16)->u16,
                                            a : u16, b : u16, ) -> u16 {
  unsafe { f(a, b) }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn calls_u16_live2(p : *const u16, a : u16, b : u16)
    -> u16 {
  unsafe {
    let v0 = core::ptr::read_volatile(p.add(0));
    let v1 = core::ptr::read_volatile(p.add(1));
    let mut r = fixture_leaf_u16(a, b);
    r = (r ^ v0).wrapping_add(r >> 1);
    r = (r ^ v1).wrapping_add(r >> 1);
    r
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn calls_u16_live2_inline(p : *const u16, a : u16,
                                                b : u16) -> u16 {
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
pub unsafe extern "C" fn calls_u16_live4(p : *const u16, a : u16, b : u16)
    -> u16 {
  unsafe {
    let v0 = core::ptr::read_volatile(p.add(0));
    let v1 = core::ptr::read_volatile(p.add(1));
    let v2 = core::ptr::read_volatile(p.add(2));
    let v3 = core::ptr::read_volatile(p.add(3));
    let mut r = fixture_leaf_u16(a, b);
    r = (r ^ v0).wrapping_add(r >> 1);
    r = (r ^ v1).wrapping_add(r >> 1);
    r = (r ^ v2).wrapping_add(r >> 1);
    r = (r ^ v3).wrapping_add(r >> 1);
    r
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn calls_u16_live4_inline(p : *const u16, a : u16,
                                                b : u16) -> u16 {
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
pub unsafe extern "C" fn calls_u16_live8(p : *const u16, a : u16, b : u16)
    -> u16 {
  unsafe {
    let v0 = core::ptr::read_volatile(p.add(0));
    let v1 = core::ptr::read_volatile(p.add(1));
    let v2 = core::ptr::read_volatile(p.add(2));
    let v3 = core::ptr::read_volatile(p.add(3));
    let v4 = core::ptr::read_volatile(p.add(4));
    let v5 = core::ptr::read_volatile(p.add(5));
    let v6 = core::ptr::read_volatile(p.add(6));
    let v7 = core::ptr::read_volatile(p.add(7));
    let mut r = fixture_leaf_u16(a, b);
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
pub unsafe extern "C" fn calls_u16_live8_inline(p : *const u16, a : u16,
                                                b : u16) -> u16 {
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
pub unsafe extern "C" fn calls_u16_local8(a : u16, b : u16) -> u16 {
  unsafe {
    let mut storage = core::mem::MaybeUninit::<[u8; 8]>::uninit();
    let p = storage.as_mut_ptr().cast::<u8>();
        for
          i in 0..8 { *p.add(i) = (a as u8).wrapping_add(i as u8); }
        let r = fixture_touch_u16(p, b);
        r.wrapping_add(*p as u16).wrapping_add(*p.add(7) as u16)
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn calls_u16_local32(a : u16, b : u16) -> u16 {
  unsafe {
    let mut storage = core::mem::MaybeUninit::<[u8; 32]>::uninit();
    let p = storage.as_mut_ptr().cast::<u8>();
        for
          i in 0..32 { *p.add(i) = (a as u8).wrapping_add(i as u8); }
        let r = fixture_touch_u16(p, b);
        r.wrapping_add(*p as u16).wrapping_add(*p.add(31) as u16)
  }
}
