#![no_std]
#![feature(core_intrinsics)]
#![allow(internal_features, improper_ctypes_definitions)]

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i16_add(a : i16, b : i16) -> i16{a.wrapping_add(b)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i16_sub(a : i16, b : i16)
    ->i16{a.wrapping_sub(b)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i16_mul(a : i16, b : i16)
    ->i16{a.wrapping_mul(b)}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn i16_div(a : i16, b : i16)
    ->i16 {
  unsafe { core::intrinsics::unchecked_div(a, b) }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn i16_rem(a : i16, b : i16) -> i16 {
  unsafe { core::intrinsics::unchecked_rem(a, b) }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i16_and(a : i16, b : i16) -> i16{a & b}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i16_or(a : i16, b : i16)
    ->i16{a | b}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i16_xor(a : i16, b : i16)
    ->i16{a ^ b}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i16_eq(a : i16, b : i16)
    ->u8{(a == b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i16_ne(a : i16, b : i16)
    ->u8{(a != b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i16_lt(a : i16, b : i16)
    ->u8{(a < b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i16_le(a : i16, b : i16)
    ->u8{(a <= b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i16_gt(a : i16, b : i16)
    ->u8{(a > b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i16_ge(a : i16, b : i16)
    ->u8{(a >= b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i16_min(a : i16, b : i16)
    ->i16 {
  if a
    < b { a }
  else {
    b
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i16_max(a : i16, b : i16) -> i16 {
  if a
    > b { a }
  else {
    b
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i16_not(a : i16) -> i16{!a}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i16_neg(a : i16)
    ->i16{a.wrapping_neg()}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i16_add1(a : i16)
    ->i16{a.wrapping_add(1)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i16_mul3(a : i16)
    ->i16{a.wrapping_mul(3)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i16_mul10(a : i16)
    ->i16{a.wrapping_mul(10)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i16_div3(a : i16)
    ->i16{a / 3}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i16_rem10(a : i16)
    ->i16{a % 10}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i16_shl(a : i16, b : u8)
    ->i16{a.wrapping_shl(b as u32)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i16_shl1(a : i16)
    ->i16{a.wrapping_shl(1)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i16_shl7(a : i16)
    ->i16{a.wrapping_shl(7)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i16_shr(a : i16, b : u8)
    ->i16{a.wrapping_shr(b as u32)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i16_shr1(a : i16)
    ->i16{a.wrapping_shr(1)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i16_shr7(a : i16)
    ->i16{a.wrapping_shr(7)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i16_rol(a : i16, b : u8)
    ->i16{a.rotate_left(b as u32)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i16_ror(a : i16, b : u8)
    ->i16{a.rotate_right(b as u32)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i16_as_signed(a : i16)
    ->i16{a as i16}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i16_as_unsigned(a : i16)
    ->u16{a as u16}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i16_narrow(a : i16)
    ->u8{a as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i16_widen(a : i16)
    ->i32 {
  a as i32
}
