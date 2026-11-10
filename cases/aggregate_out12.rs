#![no_std]
#![allow(unused_unsafe, improper_ctypes_definitions)]
#[repr(C)]
#[derive(Clone, Copy)]
pub struct PatternBlob12 {
  pub bytes : [u8; 12],
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn fixture_blob12_out(dst : *mut PatternBlob12,
                                            src : *const PatternBlob12) {
  unsafe { core::ptr::write_unaligned(dst, core::ptr::read_unaligned(src)); }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn aggregate_out12_call(dst : *mut u8, src : *const u8)
    -> u16 {
  unsafe {
    let mut tmp = core::mem::MaybeUninit::<PatternBlob12>::uninit();
    fixture_blob12_out(tmp.as_mut_ptr(), src.cast());
    core::ptr::write_unaligned(dst.cast::<PatternBlob12>(), tmp.assume_init());
    12
  }
}
