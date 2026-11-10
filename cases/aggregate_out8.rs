#![no_std]
#![allow(unused_unsafe, improper_ctypes_definitions)]
#[repr(C)]
#[derive(Clone, Copy)]
pub struct PatternBlob8 {
  pub bytes : [u8; 8],
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn fixture_blob8_out(dst : *mut PatternBlob8,
                                           src : *const PatternBlob8) {
  unsafe { core::ptr::write_unaligned(dst, core::ptr::read_unaligned(src)); }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn aggregate_out8_call(dst : *mut u8, src : *const u8)
    -> u16 {
  unsafe {
    let mut tmp = core::mem::MaybeUninit::<PatternBlob8>::uninit();
    fixture_blob8_out(tmp.as_mut_ptr(), src.cast());
    core::ptr::write_unaligned(dst.cast::<PatternBlob8>(), tmp.assume_init());
    8
  }
}
