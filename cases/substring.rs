#![no_std]
#![allow(unused_unsafe, improper_ctypes_definitions)]

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn substring_strstr_loop(src : *const u8,
                                               other : *const u8) -> u16 {
  unsafe {
    if
      *other == 0 { return 0; }
    let mut i = 0usize;
    while
      *src.add(i) != 0 {
        let mut j = 0usize;
        while
          *other.add(j) != 0 && *src.add(i + j) == *other.add(j) { j += 1; }
        if
          *other.add(j) == 0 { return i as u16; }
        i += 1;
      }
    u16::MAX
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn substring_strstr_library(src : *const u8,
                                                  other : *const u8) -> u16 {
  unsafe {
    let a = core::ffi::CStr::from_ptr(src.cast()).to_bytes();
    let b = core::ffi::CStr::from_ptr(other.cast()).to_bytes();
    if b
      .is_empty(){0} else {
        a.windows(b.len())
            .position(| w | w == b)
            .map_or(u16::MAX, | i | i as u16)
      }
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn substring_needle2(src : *const u8, other : *const u8,
                                           n : u16) -> u16 {
  unsafe {
    let a = core::slice::from_raw_parts(src, n as usize);
    let b = core::slice::from_raw_parts(other, 2);
    a.windows(2).position(| w | w == b).map_or(u16::MAX, | i | i as u16)
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn substring_needle4(src : *const u8, other : *const u8,
                                           n : u16) -> u16 {
  unsafe {
    let a = core::slice::from_raw_parts(src, n as usize);
    let b = core::slice::from_raw_parts(other, 4);
    a.windows(4).position(| w | w == b).map_or(u16::MAX, | i | i as u16)
  }
}
