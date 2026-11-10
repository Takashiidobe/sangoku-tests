#![no_std]
#![allow(unused_unsafe, improper_ctypes_definitions)]
#[repr(C)]
#[derive(Clone, Copy)]
pub struct PatternBlob12 {
  pub bytes : [u8; 12],
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn aggregate_return12_value(src : *const u8)
    -> PatternBlob12 {
  unsafe { core::ptr::read_unaligned(src.cast::<PatternBlob12>()) }
}
