#![no_std]
#![allow(unused_unsafe, improper_ctypes_definitions)]

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn concat_strcat_loop(dst : *mut u8, src : *const u8)
    -> *mut u8 {
  unsafe {
    let mut i = 0usize;
    let mut j = 0usize;
    while
      *dst.add(i) != 0 { i += 1; }
    loop {
      let x = *src.add(j);
      *dst.add(i) = x;
      i += 1;
      j += 1;
      if x
        == 0 { break; }
    }
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn concat_strcat_library(dst : *mut u8, src : *const u8)
    -> *mut u8 {
  unsafe {
    let i = core::ffi::CStr::from_ptr(dst.cast()).to_bytes().len();
    let s = core::ffi::CStr::from_ptr(src.cast()).to_bytes_with_nul();
    core::ptr::copy_nonoverlapping(s.as_ptr(), dst.add(i), s.len());
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn concat_strncat_loop(dst : *mut u8, src : *const u8,
                                             n : u16) -> *mut u8 {
  unsafe {
    let mut i = 0usize;
    let mut j = 0usize;
    while
      *dst.add(i) != 0 { i += 1; }
    while
      j < n as usize && *src.add(j) != 0 {
        *dst.add(i) = *src.add(j);
        i += 1;
        j += 1;
      }
    *dst.add(i) = 0;
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn concat_strncat_library(dst : *mut u8, src : *const u8,
                                                n : u16) -> *mut u8 {
  unsafe {
    let mut i = 0usize;
    let mut j = 0usize;
    while
      *dst.add(i) != 0 { i += 1; }
    while
      j < n as usize && *src.add(j) != 0 {
        *dst.add(i) = *src.add(j);
        i += 1;
        j += 1;
      }
    *dst.add(i) = 0;
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn concat_append_bounded(dst : *mut u8, src : *const u8,
                                               limit : u16) -> u16 {
  unsafe {
    let mut i = 0usize;
    let mut j = 0usize;
    while
      i < limit as usize && *dst.add(i) != 0 { i += 1; }
    if i
      == limit as usize { return u16::MAX; }
    while
      i + 1 < limit as usize && *src.add(j) != 0 {
        *dst.add(i) = *src.add(j);
        i += 1;
        j += 1;
      }
    *dst.add(i) = 0;
    i as u16
  }
}
