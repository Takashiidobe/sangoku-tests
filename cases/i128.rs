#![no_std]
#![feature(core_intrinsics)]
#![allow(internal_features, improper_ctypes_definitions)]

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i128_add(a : i128, b : i128) -> i128{a.wrapping_add(b)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i128_sub(a : i128, b : i128)
    ->i128{a.wrapping_sub(b)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i128_mul(a : i128, b : i128)
    ->i128{a.wrapping_mul(b)}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn i128_div(a : i128, b : i128)
    ->i128 {
  unsafe { core::intrinsics::unchecked_div(a, b) }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn i128_rem(a : i128, b : i128) -> i128 {
  unsafe { core::intrinsics::unchecked_rem(a, b) }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i128_and(a : i128, b : i128) -> i128{a & b}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i128_or(a : i128, b : i128)
    ->i128{a | b}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i128_xor(a : i128, b : i128)
    ->i128{a ^ b}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i128_eq(a : i128, b : i128)
    ->u8{(a == b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i128_ne(a : i128, b : i128)
    ->u8{(a != b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i128_lt(a : i128, b : i128)
    ->u8{(a < b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i128_le(a : i128, b : i128)
    ->u8{(a <= b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i128_gt(a : i128, b : i128)
    ->u8{(a > b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i128_ge(a : i128, b : i128)
    ->u8{(a >= b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i128_min(a : i128, b : i128)
    ->i128 {
  if a
    < b { a }
  else {
    b
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i128_max(a : i128, b : i128) -> i128 {
  if a
    > b { a }
  else {
    b
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i128_not(a : i128) -> i128{!a}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i128_neg(a : i128)
    ->i128{a.wrapping_neg()}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i128_add1(a : i128)
    ->i128{a.wrapping_add(1)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i128_mul3(a : i128)
    ->i128{a.wrapping_mul(3)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i128_mul10(a : i128)
    ->i128{a.wrapping_mul(10)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i128_div3(a : i128)
    ->i128{a / 3}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i128_rem10(a : i128)
    ->i128{a % 10}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i128_shl(a : i128, b : u8)
    ->i128{a.wrapping_shl(b as u32)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i128_shl1(a : i128)
    ->i128{a.wrapping_shl(1)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i128_shl7(a : i128)
    ->i128{a.wrapping_shl(7)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i128_shr(a : i128, b : u8)
    ->i128{a.wrapping_shr(b as u32)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i128_shr1(a : i128)
    ->i128{a.wrapping_shr(1)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i128_shr7(a : i128)
    ->i128{a.wrapping_shr(7)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i128_rol(a : i128, b : u8)
    ->i128{a.rotate_left(b as u32)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i128_ror(a : i128, b : u8)
    ->i128{a.rotate_right(b as u32)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i128_as_signed(a : i128)
    ->i128{a as i128}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i128_as_unsigned(a : i128)
    ->u128{a as u128}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i128_narrow(a : i128)
    ->u64 {
  a as u64
}
