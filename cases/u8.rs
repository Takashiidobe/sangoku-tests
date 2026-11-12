#![no_std]
#![feature(core_intrinsics)]
#![allow(internal_features, improper_ctypes_definitions)]

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u8_add(a : u8, b : u8) -> u8{a.wrapping_add(b)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u8_sub(a : u8, b : u8)
    ->u8{a.wrapping_sub(b)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u8_mul(a : u8, b : u8)
    ->u8{a.wrapping_mul(b)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u8_mulhi(a: u8, b: u8) -> u8 {
  ((a as u16).wrapping_mul(b as u16) >> 8) as u8
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn u8_div(a : u8, b : u8)
    ->u8 {
  unsafe { core::intrinsics::unchecked_div(a, b) }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn u8_rem(a : u8, b : u8) -> u8 {
  unsafe { core::intrinsics::unchecked_rem(a, b) }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u8_and(a : u8, b : u8) -> u8{a & b}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u8_or(a : u8, b : u8)
    ->u8{a | b}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u8_xor(a : u8, b : u8)
    ->u8{a ^ b}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u8_eq(a : u8, b : u8)
    ->u8{(a == b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u8_ne(a : u8, b : u8)
    ->u8{(a != b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u8_lt(a : u8, b : u8)
    ->u8{(a < b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u8_le(a : u8, b : u8)
    ->u8{(a <= b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u8_gt(a : u8, b : u8)
    ->u8{(a > b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u8_ge(a : u8, b : u8)
    ->u8{(a >= b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u8_min(a : u8, b : u8)
    ->u8 {
  if a
    < b { a }
  else {
    b
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u8_max(a : u8, b : u8) -> u8 {
  if a
    > b { a }
  else {
    b
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u8_not(a : u8) -> u8{!a}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u8_neg(a : u8)
    ->u8{a.wrapping_neg()}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u8_add1(a : u8)
    ->u8{a.wrapping_add(1)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u8_mul3(a : u8)
    ->u8{a.wrapping_mul(3)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u8_mul10(a : u8)
    ->u8{a.wrapping_mul(10)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u8_div3(a : u8)
    ->u8{a / 3}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u8_rem10(a : u8)
    ->u8{a % 10}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u8_shl(a : u8, b : u8)
    ->u8{a.wrapping_shl(b as u32)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u8_shl1(a : u8)
    ->u8{a.wrapping_shl(1)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u8_shl7(a : u8)
    ->u8{a.wrapping_shl(7)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u8_shr(a : u8, b : u8)
    ->u8{a.wrapping_shr(b as u32)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u8_shr1(a : u8)
    ->u8{a.wrapping_shr(1)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u8_shr7(a : u8)
    ->u8{a.wrapping_shr(7)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u8_rol(a : u8, b : u8)
    ->u8{a.rotate_left(b as u32)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u8_ror(a : u8, b : u8)
    ->u8{a.rotate_right(b as u32)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u8_as_signed(a : u8)
    ->i8{a as i8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u8_as_unsigned(a : u8)
    ->u8{a as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u8_widen(a : u8)
    ->u16 {
  a as u16
}
