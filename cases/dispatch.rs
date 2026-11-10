#![no_std]
#![allow(unused_unsafe, improper_ctypes_definitions)]

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn dispatch_dense(value : u8) -> u16 {
  unsafe {
    match value {
      0 = > 7, 1 = > 0, 2 = > 99, 3 = > 2, 4 = > 1, 5 = > 17, 6 = > 31, 7 = > 6,
      _ = > u16::MAX,
    }
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn dispatch_sparse(value : u8) -> u16 {
  unsafe {
    match value {
      0 = > 7, 1 = > 11, 7 = > 3, 31 = > 13, 128 = > 5, 255 = > 17, _ = > 0,
    }
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn dispatch_parser_state(src : *const u8, n : u16)
    -> u16 {
  unsafe {
    let mut acc = 0u16;
    let mut total = 0u16;
    let mut state = 0u8;
        for
          i in 0..n as usize {
            let c = *src.add(i);
            match c {
              b ':' = > state ^= 1, b ',' => {
                total = total.wrapping_add(acc);
                acc = 0;
              }
              _ => {
                if c
                  >= b '0' && c <= b '9' {
                    acc = acc.wrapping_mul(10).wrapping_add((c - b '0') as u16);
                  }
                else if c
                  != b ' ' { state = 2; }
              }
            }
          }
        total ^ acc ^ state as u16
  }
}
