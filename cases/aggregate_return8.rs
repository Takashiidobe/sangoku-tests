#![no_std]
#![allow(unused_unsafe, improper_ctypes_definitions)]
#[repr(C)]
#[derive(Clone, Copy)]
pub struct PatternBlob8 {
  pub bytes : [u8; 8],
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn aggregate_return8_value(src : *const u8)
    -> PatternBlob8 {
  unsafe { core::ptr::read_unaligned(src.cast::<PatternBlob8>()) }
}
