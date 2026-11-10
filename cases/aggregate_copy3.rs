#![no_std]
#![allow(unused_unsafe, improper_ctypes_definitions)]
#[repr(C)]
#[derive(Clone, Copy)]
pub struct PatternBlob3 {
  pub bytes : [u8; 3],
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn aggregate_copy3_assign(dst : *mut u8, src : *const u8)
    -> *mut u8 {
  unsafe {
    let value = core::ptr::read_unaligned(src.cast::<PatternBlob3>());
    core::ptr::write_unaligned(dst.cast::<PatternBlob3>(), value);
    dst
  }
}
