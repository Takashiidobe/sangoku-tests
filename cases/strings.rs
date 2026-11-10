#![no_std]

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_strlen(s : *const u8) -> u16 {
  unsafe { core::ffi::CStr::from_ptr(s.cast()).to_bytes().len() as u16 }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_strlen_loop(s : *const u8) -> u16 {
  unsafe {
    let mut n = 0u16;
    while
      *s.add(n as usize) != 0 { n = n.wrapping_add(1); }
    n
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_strcmp(a : *const u8, b : *const u8) -> i8 {
  unsafe {
    let v = core::ffi::CStr::from_ptr(a.cast()).to_bytes().cmp(
        core::ffi::CStr::from_ptr(b.cast()).to_bytes());
    match v {
      core::cmp::Ordering::Less = > -1, core::cmp::Ordering::Equal = > 0,
      core::cmp::Ordering::Greater = > 1,
    }
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_strcmp_loop(a : *const u8, b : *const u8)
    -> i8 {
  unsafe {
    let mut i = 0usize;
    loop {
      let x = *a.add(i);
      let y = *b.add(i);
      if x
        != y { return (x > y) as i8 - (x < y) as i8; }
      if x
        == 0 { return 0; }
      i += 1;
    }
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_strncmp(a : *const u8, b : *const u8, n : u16)
    -> i8 {
  unsafe {
    let mut i = 0usize;
    while
      i < n as usize {
        let x = *a.add(i);
        let y = *b.add(i);
        if x
          != y { return (x > y) as i8 - (x < y) as i8; }
        if x
          == 0 { return 0; }
        i += 1;
      }
    0
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_strchr(s : *const u8, value : u8) -> u16 {
  unsafe {
    let mut i = 0u16;
    let mut found = u16::MAX;
    loop {
      let x = *s.add(i as usize);
      if x
        == value { return i; }
      if x
        == 0 { return u16::MAX; }
      i = i.wrapping_add(1);
    }
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_strrchr(s : *const u8, value : u8) -> u16 {
  unsafe {
    let mut i = 0u16;
    let mut found = u16::MAX;
    loop {
      let x = *s.add(i as usize);
      if x
        == value { found = i; }
      if x
        == 0 { return found; }
      i = i.wrapping_add(1);
    }
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_strcpy(dst : *mut u8, src : *const u8)
    -> *mut u8 {
  unsafe {
    let bytes = core::ffi::CStr::from_ptr(src.cast()).to_bytes_with_nul();
    core::ptr::copy_nonoverlapping(bytes.as_ptr(), dst, bytes.len());
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_strncpy(dst : *mut u8, src : *const u8,
                                         n : u16) -> *mut u8 {
  unsafe {
    let mut i = 0usize;
    while
      i < n as usize {
        let x = *src.add(i);
        if x
          == 0 { break; }
        *dst.add(i) = x;
        i += 1;
      }
    while
      i < n as usize {
        *dst.add(i) = 0;
        i += 1;
      }
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memcpy(dst : *mut u8, src : *const u8, n : u16)
    -> *mut u8 {
  unsafe {
    core::ptr::copy_nonoverlapping(src, dst, n as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memcpy0(dst : *mut u8, src : *const u8)
    -> *mut u8 {
  unsafe {
    core::ptr::copy_nonoverlapping(src, dst, 0 as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memcpy1(dst : *mut u8, src : *const u8)
    -> *mut u8 {
  unsafe {
    core::ptr::copy_nonoverlapping(src, dst, 1 as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memcpy2(dst : *mut u8, src : *const u8)
    -> *mut u8 {
  unsafe {
    core::ptr::copy_nonoverlapping(src, dst, 2 as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memcpy3(dst : *mut u8, src : *const u8)
    -> *mut u8 {
  unsafe {
    core::ptr::copy_nonoverlapping(src, dst, 3 as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memcpy4(dst : *mut u8, src : *const u8)
    -> *mut u8 {
  unsafe {
    core::ptr::copy_nonoverlapping(src, dst, 4 as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memcpy7(dst : *mut u8, src : *const u8)
    -> *mut u8 {
  unsafe {
    core::ptr::copy_nonoverlapping(src, dst, 7 as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memcpy8(dst : *mut u8, src : *const u8)
    -> *mut u8 {
  unsafe {
    core::ptr::copy_nonoverlapping(src, dst, 8 as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memcpy15(dst : *mut u8, src : *const u8)
    -> *mut u8 {
  unsafe {
    core::ptr::copy_nonoverlapping(src, dst, 15 as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memcpy16(dst : *mut u8, src : *const u8)
    -> *mut u8 {
  unsafe {
    core::ptr::copy_nonoverlapping(src, dst, 16 as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memcpy17(dst : *mut u8, src : *const u8)
    -> *mut u8 {
  unsafe {
    core::ptr::copy_nonoverlapping(src, dst, 17 as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memcpy31(dst : *mut u8, src : *const u8)
    -> *mut u8 {
  unsafe {
    core::ptr::copy_nonoverlapping(src, dst, 31 as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memcpy32(dst : *mut u8, src : *const u8)
    -> *mut u8 {
  unsafe {
    core::ptr::copy_nonoverlapping(src, dst, 32 as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memcpy63(dst : *mut u8, src : *const u8)
    -> *mut u8 {
  unsafe {
    core::ptr::copy_nonoverlapping(src, dst, 63 as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memcpy64(dst : *mut u8, src : *const u8)
    -> *mut u8 {
  unsafe {
    core::ptr::copy_nonoverlapping(src, dst, 64 as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memcpy127(dst : *mut u8, src : *const u8)
    -> *mut u8 {
  unsafe {
    core::ptr::copy_nonoverlapping(src, dst, 127 as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memcpy128(dst : *mut u8, src : *const u8)
    -> *mut u8 {
  unsafe {
    core::ptr::copy_nonoverlapping(src, dst, 128 as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memmove(dst : *mut u8, src : *const u8,
                                         n : u16) -> *mut u8 {
  unsafe {
    core::ptr::copy(src, dst, n as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memmove0(dst : *mut u8, src : *const u8)
    -> *mut u8 {
  unsafe {
    core::ptr::copy(src, dst, 0 as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memmove1(dst : *mut u8, src : *const u8)
    -> *mut u8 {
  unsafe {
    core::ptr::copy(src, dst, 1 as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memmove2(dst : *mut u8, src : *const u8)
    -> *mut u8 {
  unsafe {
    core::ptr::copy(src, dst, 2 as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memmove3(dst : *mut u8, src : *const u8)
    -> *mut u8 {
  unsafe {
    core::ptr::copy(src, dst, 3 as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memmove4(dst : *mut u8, src : *const u8)
    -> *mut u8 {
  unsafe {
    core::ptr::copy(src, dst, 4 as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memmove7(dst : *mut u8, src : *const u8)
    -> *mut u8 {
  unsafe {
    core::ptr::copy(src, dst, 7 as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memmove8(dst : *mut u8, src : *const u8)
    -> *mut u8 {
  unsafe {
    core::ptr::copy(src, dst, 8 as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memmove15(dst : *mut u8, src : *const u8)
    -> *mut u8 {
  unsafe {
    core::ptr::copy(src, dst, 15 as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memmove16(dst : *mut u8, src : *const u8)
    -> *mut u8 {
  unsafe {
    core::ptr::copy(src, dst, 16 as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memmove17(dst : *mut u8, src : *const u8)
    -> *mut u8 {
  unsafe {
    core::ptr::copy(src, dst, 17 as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memmove31(dst : *mut u8, src : *const u8)
    -> *mut u8 {
  unsafe {
    core::ptr::copy(src, dst, 31 as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memmove32(dst : *mut u8, src : *const u8)
    -> *mut u8 {
  unsafe {
    core::ptr::copy(src, dst, 32 as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memmove63(dst : *mut u8, src : *const u8)
    -> *mut u8 {
  unsafe {
    core::ptr::copy(src, dst, 63 as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memmove64(dst : *mut u8, src : *const u8)
    -> *mut u8 {
  unsafe {
    core::ptr::copy(src, dst, 64 as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memmove127(dst : *mut u8, src : *const u8)
    -> *mut u8 {
  unsafe {
    core::ptr::copy(src, dst, 127 as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memmove128(dst : *mut u8, src : *const u8)
    -> *mut u8 {
  unsafe {
    core::ptr::copy(src, dst, 128 as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memset(dst : *mut u8, value : u8, n : u16)
    -> *mut u8 {
  unsafe {
    core::ptr::write_bytes(dst, value, n as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memset0(dst : *mut u8, value : u8) -> *mut u8 {
  unsafe {
    core::ptr::write_bytes(dst, value, 0 as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memset1(dst : *mut u8, value : u8) -> *mut u8 {
  unsafe {
    core::ptr::write_bytes(dst, value, 1 as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memset2(dst : *mut u8, value : u8) -> *mut u8 {
  unsafe {
    core::ptr::write_bytes(dst, value, 2 as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memset3(dst : *mut u8, value : u8) -> *mut u8 {
  unsafe {
    core::ptr::write_bytes(dst, value, 3 as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memset4(dst : *mut u8, value : u8) -> *mut u8 {
  unsafe {
    core::ptr::write_bytes(dst, value, 4 as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memset7(dst : *mut u8, value : u8) -> *mut u8 {
  unsafe {
    core::ptr::write_bytes(dst, value, 7 as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memset8(dst : *mut u8, value : u8) -> *mut u8 {
  unsafe {
    core::ptr::write_bytes(dst, value, 8 as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memset15(dst : *mut u8, value : u8)
    -> *mut u8 {
  unsafe {
    core::ptr::write_bytes(dst, value, 15 as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memset16(dst : *mut u8, value : u8)
    -> *mut u8 {
  unsafe {
    core::ptr::write_bytes(dst, value, 16 as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memset17(dst : *mut u8, value : u8)
    -> *mut u8 {
  unsafe {
    core::ptr::write_bytes(dst, value, 17 as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memset31(dst : *mut u8, value : u8)
    -> *mut u8 {
  unsafe {
    core::ptr::write_bytes(dst, value, 31 as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memset32(dst : *mut u8, value : u8)
    -> *mut u8 {
  unsafe {
    core::ptr::write_bytes(dst, value, 32 as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memset63(dst : *mut u8, value : u8)
    -> *mut u8 {
  unsafe {
    core::ptr::write_bytes(dst, value, 63 as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memset64(dst : *mut u8, value : u8)
    -> *mut u8 {
  unsafe {
    core::ptr::write_bytes(dst, value, 64 as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memset127(dst : *mut u8, value : u8)
    -> *mut u8 {
  unsafe {
    core::ptr::write_bytes(dst, value, 127 as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memset128(dst : *mut u8, value : u8)
    -> *mut u8 {
  unsafe {
    core::ptr::write_bytes(dst, value, 128 as usize);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memcmp(a : *const u8, b : *const u8, n : u16)
    -> i8 {
  unsafe {
    let v = core::slice::from_raw_parts(a, n as usize)
                .cmp(core::slice::from_raw_parts(b, n as usize));
    match v {
      core::cmp::Ordering::Less = > -1, core::cmp::Ordering::Equal = > 0,
      core::cmp::Ordering::Greater = > 1,
    }
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memcmp0(a : *const u8, b : *const u8) -> i8 {
  unsafe {
    let v = core::slice::from_raw_parts(a, 0 as usize)
                .cmp(core::slice::from_raw_parts(b, 0 as usize));
    match v {
      core::cmp::Ordering::Less = > -1, core::cmp::Ordering::Equal = > 0,
      core::cmp::Ordering::Greater = > 1,
    }
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memcmp1(a : *const u8, b : *const u8) -> i8 {
  unsafe {
    let v = core::slice::from_raw_parts(a, 1 as usize)
                .cmp(core::slice::from_raw_parts(b, 1 as usize));
    match v {
      core::cmp::Ordering::Less = > -1, core::cmp::Ordering::Equal = > 0,
      core::cmp::Ordering::Greater = > 1,
    }
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memcmp2(a : *const u8, b : *const u8) -> i8 {
  unsafe {
    let v = core::slice::from_raw_parts(a, 2 as usize)
                .cmp(core::slice::from_raw_parts(b, 2 as usize));
    match v {
      core::cmp::Ordering::Less = > -1, core::cmp::Ordering::Equal = > 0,
      core::cmp::Ordering::Greater = > 1,
    }
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memcmp3(a : *const u8, b : *const u8) -> i8 {
  unsafe {
    let v = core::slice::from_raw_parts(a, 3 as usize)
                .cmp(core::slice::from_raw_parts(b, 3 as usize));
    match v {
      core::cmp::Ordering::Less = > -1, core::cmp::Ordering::Equal = > 0,
      core::cmp::Ordering::Greater = > 1,
    }
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memcmp4(a : *const u8, b : *const u8) -> i8 {
  unsafe {
    let v = core::slice::from_raw_parts(a, 4 as usize)
                .cmp(core::slice::from_raw_parts(b, 4 as usize));
    match v {
      core::cmp::Ordering::Less = > -1, core::cmp::Ordering::Equal = > 0,
      core::cmp::Ordering::Greater = > 1,
    }
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memcmp7(a : *const u8, b : *const u8) -> i8 {
  unsafe {
    let v = core::slice::from_raw_parts(a, 7 as usize)
                .cmp(core::slice::from_raw_parts(b, 7 as usize));
    match v {
      core::cmp::Ordering::Less = > -1, core::cmp::Ordering::Equal = > 0,
      core::cmp::Ordering::Greater = > 1,
    }
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memcmp8(a : *const u8, b : *const u8) -> i8 {
  unsafe {
    let v = core::slice::from_raw_parts(a, 8 as usize)
                .cmp(core::slice::from_raw_parts(b, 8 as usize));
    match v {
      core::cmp::Ordering::Less = > -1, core::cmp::Ordering::Equal = > 0,
      core::cmp::Ordering::Greater = > 1,
    }
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memcmp15(a : *const u8, b : *const u8) -> i8 {
  unsafe {
    let v = core::slice::from_raw_parts(a, 15 as usize)
                .cmp(core::slice::from_raw_parts(b, 15 as usize));
    match v {
      core::cmp::Ordering::Less = > -1, core::cmp::Ordering::Equal = > 0,
      core::cmp::Ordering::Greater = > 1,
    }
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memcmp16(a : *const u8, b : *const u8) -> i8 {
  unsafe {
    let v = core::slice::from_raw_parts(a, 16 as usize)
                .cmp(core::slice::from_raw_parts(b, 16 as usize));
    match v {
      core::cmp::Ordering::Less = > -1, core::cmp::Ordering::Equal = > 0,
      core::cmp::Ordering::Greater = > 1,
    }
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memcmp17(a : *const u8, b : *const u8) -> i8 {
  unsafe {
    let v = core::slice::from_raw_parts(a, 17 as usize)
                .cmp(core::slice::from_raw_parts(b, 17 as usize));
    match v {
      core::cmp::Ordering::Less = > -1, core::cmp::Ordering::Equal = > 0,
      core::cmp::Ordering::Greater = > 1,
    }
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memcmp31(a : *const u8, b : *const u8) -> i8 {
  unsafe {
    let v = core::slice::from_raw_parts(a, 31 as usize)
                .cmp(core::slice::from_raw_parts(b, 31 as usize));
    match v {
      core::cmp::Ordering::Less = > -1, core::cmp::Ordering::Equal = > 0,
      core::cmp::Ordering::Greater = > 1,
    }
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memcmp32(a : *const u8, b : *const u8) -> i8 {
  unsafe {
    let v = core::slice::from_raw_parts(a, 32 as usize)
                .cmp(core::slice::from_raw_parts(b, 32 as usize));
    match v {
      core::cmp::Ordering::Less = > -1, core::cmp::Ordering::Equal = > 0,
      core::cmp::Ordering::Greater = > 1,
    }
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memcmp63(a : *const u8, b : *const u8) -> i8 {
  unsafe {
    let v = core::slice::from_raw_parts(a, 63 as usize)
                .cmp(core::slice::from_raw_parts(b, 63 as usize));
    match v {
      core::cmp::Ordering::Less = > -1, core::cmp::Ordering::Equal = > 0,
      core::cmp::Ordering::Greater = > 1,
    }
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memcmp64(a : *const u8, b : *const u8) -> i8 {
  unsafe {
    let v = core::slice::from_raw_parts(a, 64 as usize)
                .cmp(core::slice::from_raw_parts(b, 64 as usize));
    match v {
      core::cmp::Ordering::Less = > -1, core::cmp::Ordering::Equal = > 0,
      core::cmp::Ordering::Greater = > 1,
    }
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memcmp127(a : *const u8, b : *const u8) -> i8 {
  unsafe {
    let v = core::slice::from_raw_parts(a, 127 as usize)
                .cmp(core::slice::from_raw_parts(b, 127 as usize));
    match v {
      core::cmp::Ordering::Less = > -1, core::cmp::Ordering::Equal = > 0,
      core::cmp::Ordering::Greater = > 1,
    }
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memcmp128(a : *const u8, b : *const u8) -> i8 {
  unsafe {
    let v = core::slice::from_raw_parts(a, 128 as usize)
                .cmp(core::slice::from_raw_parts(b, 128 as usize));
    match v {
      core::cmp::Ordering::Less = > -1, core::cmp::Ordering::Equal = > 0,
      core::cmp::Ordering::Greater = > 1,
    }
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memeq(a : *const u8, b : *const u8, n : u16)
    -> u8 {
  unsafe {
    (core::slice::from_raw_parts(a, n as usize) ==
     core::slice::from_raw_parts(b, n as usize)) as u8
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memchr(s : *const u8, value : u8, n : u16)
    -> u16 {
  unsafe {
    let mut i = 0u16;
    while
      i < n {
        if
          *s.add(i as usize) == value { return i; }
        i += 1;
      }
    u16::MAX
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memcpy_offset1(dst : *mut u8, src : *const u8,
                                                n : u16) -> *mut u8 {
  unsafe {
    core::ptr::copy_nonoverlapping(src.add(1), dst.add(1), n as usize);
    dst.add(1)
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memcpy_offset3(dst : *mut u8, src : *const u8,
                                                n : u16) -> *mut u8 {
  unsafe {
    core::ptr::copy_nonoverlapping(src.add(3), dst.add(3), n as usize);
    dst.add(3)
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn strings_memcpy_offset7(dst : *mut u8, src : *const u8,
                                                n : u16) -> *mut u8 {
  unsafe {
    core::ptr::copy_nonoverlapping(src.add(7), dst.add(7), n as usize);
    dst.add(7)
  }
}
