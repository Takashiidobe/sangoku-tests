#![no_std]
#![allow(unused_unsafe, improper_ctypes_definitions)]
struct PatternWriter {
  dst : *mut u8, len : usize,
}
impl core::fmt::Write for PatternWriter {
  fn write_str(&mut self, s : &str) -> core::fmt::Result {
    unsafe {
      core::ptr::copy_nonoverlapping(s.as_ptr(), self.dst.add(self.len),
                                     s.len());
    }
    self.len += s.len();
    Ok(())
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn format_u64_decimal_divmod(dst : *mut u8,
                                                   mut value : u64) -> u16 {
  unsafe {
    let mut storage = core::mem::MaybeUninit::<[u8; 20]>::uninit();
    let tmp = storage.as_mut_ptr().cast::<u8>();
    let mut i = 0usize;
    loop {
      let q = value / 10;
      let d = (value % 10) as u8;
      *tmp.add(i) = if d < 10 { b '0' + d }
      else {b 'a' + d - 10};
      i += 1;
      value = q;
      if value
        == 0 { break; }
    }
        for
          j in 0..i { *dst.add(j) = *tmp.add(i - 1 - j); }
        *dst.add(i) = 0;
        i as u16
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn format_u64_decimal_derived(dst : *mut u8,
                                                    mut value : u64) -> u16 {
  unsafe {
    let mut storage = core::mem::MaybeUninit::<[u8; 20]>::uninit();
    let tmp = storage.as_mut_ptr().cast::<u8>();
    let mut i = 0usize;
    loop {
      let q = value / 10;
      let d = value.wrapping_sub(q.wrapping_mul(10)) as u8;
      *tmp.add(i) = if d < 10 { b '0' + d }
      else {b 'a' + d - 10};
      i += 1;
      value = q;
      if value
        == 0 { break; }
    }
        for
          j in 0..i { *dst.add(j) = *tmp.add(i - 1 - j); }
        *dst.add(i) = 0;
        i as u16
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn format_u64_hex(dst : *mut u8, mut value : u64) -> u16 {
  unsafe {
    let mut storage = core::mem::MaybeUninit::<[u8; 20]>::uninit();
    let tmp = storage.as_mut_ptr().cast::<u8>();
    let mut i = 0usize;
    loop {
      let q = value >> 4;
      let d = (value & 15) as u8;
      *tmp.add(i) = if d < 10 { b '0' + d }
      else {b 'a' + d - 10};
      i += 1;
      value = q;
      if value
        == 0 { break; }
    }
        for
          j in 0..i { *dst.add(j) = *tmp.add(i - 1 - j); }
        *dst.add(i) = 0;
        i as u16
  }
}
