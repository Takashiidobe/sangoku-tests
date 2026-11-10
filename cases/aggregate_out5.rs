#![no_std]
#![allow(unused_unsafe, improper_ctypes_definitions)]
#[repr(C)]
#[derive(Clone, Copy)]
pub struct PatternBlob5 {
  pub bytes : [u8; 5],
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn fixture_blob5_out(dst : *mut PatternBlob5,
                                           src : *const PatternBlob5) {
  unsafe { core::ptr::write_unaligned(dst, core::ptr::read_unaligned(src)); }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn aggregate_out5_call(dst : *mut u8, src : *const u8)
    -> u16 {
  unsafe {
    let mut tmp = core::mem::MaybeUninit::<PatternBlob5>::uninit();
    fixture_blob5_out(tmp.as_mut_ptr(), src.cast());
    core::ptr::write_unaligned(dst.cast::<PatternBlob5>(), tmp.assume_init());
    5
  }
}
