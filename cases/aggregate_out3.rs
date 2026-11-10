#![no_std]
#![allow(unused_unsafe, improper_ctypes_definitions)]
#[repr(C)]
#[derive(Clone, Copy)]
pub struct PatternBlob3 {
  pub bytes : [u8; 3],
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn fixture_blob3_out(dst : *mut PatternBlob3,
                                           src : *const PatternBlob3) {
  unsafe { core::ptr::write_unaligned(dst, core::ptr::read_unaligned(src)); }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn aggregate_out3_call(dst : *mut u8, src : *const u8)
    -> u16 {
  unsafe {
    let mut tmp = core::mem::MaybeUninit::<PatternBlob3>::uninit();
    fixture_blob3_out(tmp.as_mut_ptr(), src.cast());
    core::ptr::write_unaligned(dst.cast::<PatternBlob3>(), tmp.assume_init());
    3
  }
}
