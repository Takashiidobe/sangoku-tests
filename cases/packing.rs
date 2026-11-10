#![no_std]
#![allow(unused_unsafe, improper_ctypes_definitions)]

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn packing_load_le16(src : *const u8) -> u16 {
  unsafe {
    u16::from_le_bytes(core::ptr::read_unaligned(src.cast::<[u8; 2]>()))
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn packing_store_le16(dst : *mut u8, value : u16)
    -> *mut u8 {
  unsafe {
    let b = value.to_le_bytes();
    core::ptr::copy_nonoverlapping(b.as_ptr(), dst, 2);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn packing_load_be16(src : *const u8) -> u16 {
  unsafe {
    u16::from_be_bytes(core::ptr::read_unaligned(src.cast::<[u8; 2]>()))
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn packing_store_be16(dst : *mut u8, value : u16)
    -> *mut u8 {
  unsafe {
    let b = value.to_be_bytes();
    core::ptr::copy_nonoverlapping(b.as_ptr(), dst, 2);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn packing_load_le32(src : *const u8) -> u32 {
  unsafe {
    u32::from_le_bytes(core::ptr::read_unaligned(src.cast::<[u8; 4]>()))
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn packing_store_le32(dst : *mut u8, value : u32)
    -> *mut u8 {
  unsafe {
    let b = value.to_le_bytes();
    core::ptr::copy_nonoverlapping(b.as_ptr(), dst, 4);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn packing_load_be32(src : *const u8) -> u32 {
  unsafe {
    u32::from_be_bytes(core::ptr::read_unaligned(src.cast::<[u8; 4]>()))
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn packing_store_be32(dst : *mut u8, value : u32)
    -> *mut u8 {
  unsafe {
    let b = value.to_be_bytes();
    core::ptr::copy_nonoverlapping(b.as_ptr(), dst, 4);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn packing_load_le64(src : *const u8) -> u64 {
  unsafe {
    u64::from_le_bytes(core::ptr::read_unaligned(src.cast::<[u8; 8]>()))
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn packing_store_le64(dst : *mut u8, value : u64)
    -> *mut u8 {
  unsafe {
    let b = value.to_le_bytes();
    core::ptr::copy_nonoverlapping(b.as_ptr(), dst, 8);
    dst
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn packing_load_be64(src : *const u8) -> u64 {
  unsafe {
    u64::from_be_bytes(core::ptr::read_unaligned(src.cast::<[u8; 8]>()))
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn packing_store_be64(dst : *mut u8, value : u64)
    -> *mut u8 {
  unsafe {
    let b = value.to_be_bytes();
    core::ptr::copy_nonoverlapping(b.as_ptr(), dst, 8);
    dst
  }
}
