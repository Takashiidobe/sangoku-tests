#![no_std]
#![feature(core_intrinsics)]
#![allow(internal_features, improper_ctypes_definitions)]

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i64_add(a : i64, b : i64) -> i64{a.wrapping_add(b)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i64_sub(a : i64, b : i64)
    ->i64{a.wrapping_sub(b)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i64_mul(a : i64, b : i64)
    ->i64{a.wrapping_mul(b)}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn i64_div(a : i64, b : i64)
    ->i64 {
  unsafe { core::intrinsics::unchecked_div(a, b) }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn i64_rem(a : i64, b : i64) -> i64 {
  unsafe { core::intrinsics::unchecked_rem(a, b) }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i64_and(a : i64, b : i64) -> i64{a & b}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i64_or(a : i64, b : i64)
    ->i64{a | b}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i64_xor(a : i64, b : i64)
    ->i64{a ^ b}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i64_eq(a : i64, b : i64)
    ->u8{(a == b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i64_ne(a : i64, b : i64)
    ->u8{(a != b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i64_lt(a : i64, b : i64)
    ->u8{(a < b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i64_le(a : i64, b : i64)
    ->u8{(a <= b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i64_gt(a : i64, b : i64)
    ->u8{(a > b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i64_ge(a : i64, b : i64)
    ->u8{(a >= b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i64_min(a : i64, b : i64)
    ->i64 {
  if a
    < b { a }
  else {
    b
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i64_max(a : i64, b : i64) -> i64 {
  if a
    > b { a }
  else {
    b
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i64_not(a : i64) -> i64{!a}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i64_neg(a : i64)
    ->i64{a.wrapping_neg()}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i64_add1(a : i64)
    ->i64{a.wrapping_add(1)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i64_mul3(a : i64)
    ->i64{a.wrapping_mul(3)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i64_mul10(a : i64)
    ->i64{a.wrapping_mul(10)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i64_div3(a : i64)
    ->i64{a / 3}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i64_rem10(a : i64)
    ->i64{a % 10}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i64_shl(a : i64, b : u8)
    ->i64{a.wrapping_shl(b as u32)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i64_shl1(a : i64)
    ->i64{a.wrapping_shl(1)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i64_shl7(a : i64)
    ->i64{a.wrapping_shl(7)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i64_shr(a : i64, b : u8)
    ->i64{a.wrapping_shr(b as u32)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i64_shr1(a : i64)
    ->i64{a.wrapping_shr(1)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i64_shr7(a : i64)
    ->i64{a.wrapping_shr(7)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i64_rol(a : i64, b : u8)
    ->i64{a.rotate_left(b as u32)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i64_ror(a : i64, b : u8)
    ->i64{a.rotate_right(b as u32)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i64_as_signed(a : i64)
    ->i64{a as i64}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i64_as_unsigned(a : i64)
    ->u64{a as u64}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i64_narrow(a : i64)
    ->u32 {
  a as u32
}
