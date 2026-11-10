#![no_std]
#![allow(unused_unsafe, improper_ctypes_definitions)]
#[repr(C)]
pub struct PatternPair {
  pub ptr : *const u8, pub len : u16,
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn aggregate_pair_return(src : *const u8, n : u16)
    -> PatternPair {
  unsafe {
    PatternPair {
    ptr:
      src, len : n
    }
  }
}
