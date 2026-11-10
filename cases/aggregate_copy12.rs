#![no_std]
#![allow(unused_unsafe, improper_ctypes_definitions)]
#[repr(C)]
#[derive(Clone, Copy)]
pub struct PatternBlob12 {
  pub bytes : [u8; 12],
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn aggregate_copy12_assign(dst : *mut u8, src : *const u8)
    -> *mut u8 {
  unsafe {
    let value = core::ptr::read_unaligned(src.cast::<PatternBlob12>());
    core::ptr::write_unaligned(dst.cast::<PatternBlob12>(), value);
    dst
  }
}
