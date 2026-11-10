#![no_std]
#![allow(unused_unsafe, improper_ctypes_definitions)]

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn slices_sum_index(src : *const u8, n : u16) -> u16 {
  unsafe {
    let s = core::slice::from_raw_parts(src, n as usize);
    let mut value = 0u16;
        for
          i in 0..s.len() { value = value.wrapping_add(s[i] as u16); }
        value
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn slices_sum_iter(src : *const u8, n : u16) -> u16 {
  unsafe {
    core::slice::from_raw_parts(src, n as usize)
        .iter()
        .fold(0u16, | a, &b | a.wrapping_add(b as u16))
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn slices_sum_raw(src : *const u8, n : u16) -> u16 {
  unsafe {
    let mut value = 0u16;
        for
          i in 0..n as usize { value = value.wrapping_add(*src.add(i) as u16); }
        value
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn slices_sum_pointer(src : *const u8, n : u16) -> u16 {
  unsafe {
    let mut value = 0u16;
    let last = src.add(n as usize);
    let mut p = src;
    while
      p != last {
        value = value.wrapping_add(*p as u16);
        p = p.add(1);
      }
    value
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn slices_sum_countdown(src : *const u8, n : u16) -> u16 {
  unsafe {
    let mut value = 0u16;
    let mut p = src;
    let mut count = n;
    while
      count != 0 {
        value = value.wrapping_add(*p as u16);
        p = p.add(1);
        count -= 1;
      }
    value
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn slices_copy_from_slice(dst : *mut u8, src : *const u8,
                                                n : u16) -> *mut u8 {
  unsafe {
    let a = core::slice::from_raw_parts_mut(dst, n as usize);
    let b = core::slice::from_raw_parts(src, n as usize);
    a.copy_from_slice(b);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn slices_copy_within(dst : *mut u8, n : u16) -> *mut u8 {
  unsafe {
    let s = core::slice::from_raw_parts_mut(dst, n as usize);
    let half = s.len() / 2;
    s.copy_within(0..half, s.len() - half);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn slices_fill(dst : *mut u8, n : u16, value : u8)
    -> *mut u8 {
  unsafe {
    core::slice::from_raw_parts_mut(dst, n as usize).fill(value);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn slices_chunks_exact(src : *const u8, n : u16) -> u16 {
  unsafe {
    core::slice::from_raw_parts(src, n as usize)
        .chunks_exact(2)
        .fold(0u16, | a,
              c | {a.wrapping_add(u16::from_le_bytes([ c[0], c[1] ]))})
  }
}
