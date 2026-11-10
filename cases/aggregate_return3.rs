#![no_std]
#![allow(unused_unsafe, improper_ctypes_definitions)]
#[repr(C)]
#[derive(Clone, Copy)]
pub struct PatternBlob3 {
  pub bytes : [u8; 3],
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn aggregate_return3_value(src : *const u8)
    -> PatternBlob3 {
  unsafe { core::ptr::read_unaligned(src.cast::<PatternBlob3>()) }
}
