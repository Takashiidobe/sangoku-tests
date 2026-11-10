#![no_std]
#![allow(unused_unsafe, improper_ctypes_definitions)]
#[repr(C)]
#[derive(Clone, Copy)]
pub struct PatternBlob5 {
  pub bytes : [u8; 5],
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn aggregate_return5_value(src : *const u8)
    -> PatternBlob5 {
  unsafe { core::ptr::read_unaligned(src.cast::<PatternBlob5>()) }
}
