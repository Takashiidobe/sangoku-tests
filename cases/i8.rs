#![no_std]
#![feature(core_intrinsics)]
#![allow(internal_features, improper_ctypes_definitions)]

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i8_add(a : i8, b : i8) -> i8{a.wrapping_add(b)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i8_sub(a : i8, b : i8)
    ->i8{a.wrapping_sub(b)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i8_mul(a : i8, b : i8)
    ->i8{a.wrapping_mul(b)}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn i8_div(a : i8, b : i8)
    ->i8 {
  unsafe { core::intrinsics::unchecked_div(a, b) }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn i8_rem(a : i8, b : i8) -> i8 {
  unsafe { core::intrinsics::unchecked_rem(a, b) }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i8_and(a : i8, b : i8) -> i8{a & b}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i8_or(a : i8, b : i8)
    ->i8{a | b}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i8_xor(a : i8, b : i8)
    ->i8{a ^ b}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i8_eq(a : i8, b : i8)
    ->u8{(a == b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i8_ne(a : i8, b : i8)
    ->u8{(a != b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i8_lt(a : i8, b : i8)
    ->u8{(a < b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i8_le(a : i8, b : i8)
    ->u8{(a <= b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i8_gt(a : i8, b : i8)
    ->u8{(a > b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i8_ge(a : i8, b : i8)
    ->u8{(a >= b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i8_min(a : i8, b : i8)
    ->i8 {
  if a
    < b { a }
  else {
    b
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i8_max(a : i8, b : i8) -> i8 {
  if a
    > b { a }
  else {
    b
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i8_not(a : i8) -> i8{!a}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i8_neg(a : i8)
    ->i8{a.wrapping_neg()}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i8_add1(a : i8)
    ->i8{a.wrapping_add(1)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i8_mul3(a : i8)
    ->i8{a.wrapping_mul(3)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i8_mul10(a : i8)
    ->i8{a.wrapping_mul(10)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i8_div3(a : i8)
    ->i8{a / 3}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i8_rem10(a : i8)
    ->i8{a % 10}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i8_shl(a : i8, b : u8)
    ->i8{a.wrapping_shl(b as u32)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i8_shl1(a : i8)
    ->i8{a.wrapping_shl(1)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i8_shl7(a : i8)
    ->i8{a.wrapping_shl(7)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i8_shr(a : i8, b : u8)
    ->i8{a.wrapping_shr(b as u32)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i8_shr1(a : i8)
    ->i8{a.wrapping_shr(1)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i8_shr7(a : i8)
    ->i8{a.wrapping_shr(7)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i8_rol(a : i8, b : u8)
    ->i8{a.rotate_left(b as u32)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i8_ror(a : i8, b : u8)
    ->i8{a.rotate_right(b as u32)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i8_as_signed(a : i8)
    ->i8{a as i8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i8_as_unsigned(a : i8)
    ->u8{a as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i8_widen(a : i8)
    ->i16 {
  a as i16
}
