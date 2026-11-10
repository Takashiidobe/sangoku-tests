#![no_std]
#![allow(unused_unsafe, improper_ctypes_definitions)]

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn checksum_sum8(src : *const u8, n : u16) -> u8 {
  unsafe {
    let mut value = 0u8;
        for
          i in 0..n as usize { value = value.wrapping_add(*src.add(i)); }
        value
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn checksum_sum16(src : *const u8, n : u16) -> u16 {
  unsafe {
    let mut value = 0u16;
        for
          i in 0..n as usize { value = value.wrapping_add(*src.add(i) as u16); }
        value
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn checksum_crc16(src : *const u8, n : u16, value : u16)
    -> u16 {
  unsafe {
    let mut crc = value;
        for
          i in 0..n as usize {
            crc ^= (*src.add(i) as u16) << 8;
            for
              _ in 0..8 {
                crc = (crc << 1) ^ if crc & 0x8000 != 0 {0x1021} else {0};
              }
          }
        crc
  }
}
