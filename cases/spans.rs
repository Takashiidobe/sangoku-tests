#![no_std]
#![allow(unused_unsafe, improper_ctypes_definitions)]

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn spans_strspn_loop(src : *const u8, set : *const u8)
    -> u16 {
  unsafe {
    let mut i = 0usize;
    while
      *src.add(i) != 0 {
        let mut j = 0usize;
        while
          *set.add(j) != 0 && *set.add(j) != *src.add(i) { j += 1; }
        let found = *set.add(j) != 0;
        if !found {
          break;
        }
        i += 1;
      }
    i as u16
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn spans_strspn_library(src : *const u8, set : *const u8)
    -> u16 {
  unsafe {
    let a = core::ffi::CStr::from_ptr(src.cast()).to_bytes();
    let b = core::ffi::CStr::from_ptr(set.cast()).to_bytes();
    a.iter().take_while(| x | b.contains(x)).count() as u16
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn spans_strcspn_loop(src : *const u8, set : *const u8)
    -> u16 {
  unsafe {
    let mut i = 0usize;
    while
      *src.add(i) != 0 {
        let mut j = 0usize;
        while
          *set.add(j) != 0 && *set.add(j) != *src.add(i) { j += 1; }
        let found = *set.add(j) != 0;
        if found {
          break;
        }
        i += 1;
      }
    i as u16
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn spans_strcspn_library(src : *const u8, set : *const u8)
    -> u16 {
  unsafe {
    let a = core::ffi::CStr::from_ptr(src.cast()).to_bytes();
    let b = core::ffi::CStr::from_ptr(set.cast()).to_bytes();
    a.iter()
        .position(| x | b.contains(x))
        .map_or(a.len() as u16, | i | i as u16)
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn spans_strpbrk_loop(src : *const u8, set : *const u8)
    -> u16 {
  unsafe {
    let mut i = 0usize;
    while
      *src.add(i) != 0 {
        let mut j = 0usize;
        while
          *set.add(j) != 0 && *set.add(j) != *src.add(i) { j += 1; }
        let found = *set.add(j) != 0;
        if found {
          break;
        }
        i += 1;
      }
    if
      *src.add(i) == 0 { u16::MAX }
    else {
      i as u16
    }
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn spans_strpbrk_library(src : *const u8, set : *const u8)
    -> u16 {
  unsafe {
    let a = core::ffi::CStr::from_ptr(src.cast()).to_bytes();
    let b = core::ffi::CStr::from_ptr(set.cast()).to_bytes();
    a.iter().position(| x | b.contains(x)).map_or(u16::MAX, | i | i as u16)
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn spans_tokenize_loop(dst : *mut u8, src : *const u8,
                                             set : *const u8) -> u16 {
  unsafe {
    let mut i = 0usize;
    let mut count = 0usize;
    while
      *src.add(i) != 0 {
        let mut j = 0usize;
        while
          *set.add(j) != 0 && *set.add(j) != *src.add(i) { j += 1; }
        if
          *set.add(j) != 0 {
            i += 1;
            continue;
          }
        let start = i;
        loop {
          i += 1;
          j = 0;
          while
            *set.add(j) != 0 && *set.add(j) != *src.add(i) { j += 1; }
          if
            *src.add(i) == 0 || *set.add(j) != 0 { break; }
        }
        *dst.add(2 * count) = start as u8;
        *dst.add(2 * count + 1) = (i - start) as u8;
        count += 1;
      }
    count as u16
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn spans_strtok_library(dst : *mut u8, src : *const u8,
                                              set : *const u8) -> u16 {
  unsafe {
    let bytes = core::ffi::CStr::from_ptr(src.cast()).to_bytes_with_nul();
    core::ptr::copy_nonoverlapping(bytes.as_ptr(), dst, bytes.len());
    let delimiters = core::ffi::CStr::from_ptr(set.cast()).to_bytes();
    let mut i = 0usize;
    let mut count = 0u16;
    loop {
      while
        *dst.add(i) != 0 && delimiters.contains(&*dst.add(i)) { i += 1; }
      if
        *dst.add(i) == 0 { break; }
      count += 1;
      while
        *dst.add(i) != 0 && !delimiters.contains(&*dst.add(i)) { i += 1; }
      if
        *dst.add(i) == 0 { break; }
      *dst.add(i) = 0;
      i += 1;
    }
    count
  }
}
