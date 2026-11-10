#![no_std]
#![feature(core_intrinsics)]
#![allow(internal_features, improper_ctypes_definitions)]

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i32_add(a : i32, b : i32) -> i32{a.wrapping_add(b)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i32_sub(a : i32, b : i32)
    ->i32{a.wrapping_sub(b)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i32_mul(a : i32, b : i32)
    ->i32{a.wrapping_mul(b)}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn i32_div(a : i32, b : i32)
    ->i32 {
  unsafe { core::intrinsics::unchecked_div(a, b) }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn i32_rem(a : i32, b : i32) -> i32 {
  unsafe { core::intrinsics::unchecked_rem(a, b) }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i32_and(a : i32, b : i32) -> i32{a & b}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i32_or(a : i32, b : i32)
    ->i32{a | b}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i32_xor(a : i32, b : i32)
    ->i32{a ^ b}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i32_eq(a : i32, b : i32)
    ->u8{(a == b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i32_ne(a : i32, b : i32)
    ->u8{(a != b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i32_lt(a : i32, b : i32)
    ->u8{(a < b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i32_le(a : i32, b : i32)
    ->u8{(a <= b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i32_gt(a : i32, b : i32)
    ->u8{(a > b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i32_ge(a : i32, b : i32)
    ->u8{(a >= b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i32_min(a : i32, b : i32)
    ->i32 {
  if a
    < b { a }
  else {
    b
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i32_max(a : i32, b : i32) -> i32 {
  if a
    > b { a }
  else {
    b
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i32_not(a : i32) -> i32{!a}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i32_neg(a : i32)
    ->i32{a.wrapping_neg()}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i32_add1(a : i32)
    ->i32{a.wrapping_add(1)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i32_mul3(a : i32)
    ->i32{a.wrapping_mul(3)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i32_mul10(a : i32)
    ->i32{a.wrapping_mul(10)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i32_div3(a : i32)
    ->i32{a / 3}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i32_rem10(a : i32)
    ->i32{a % 10}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i32_shl(a : i32, b : u8)
    ->i32{a.wrapping_shl(b as u32)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i32_shl1(a : i32)
    ->i32{a.wrapping_shl(1)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i32_shl7(a : i32)
    ->i32{a.wrapping_shl(7)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i32_shr(a : i32, b : u8)
    ->i32{a.wrapping_shr(b as u32)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i32_shr1(a : i32)
    ->i32{a.wrapping_shr(1)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i32_shr7(a : i32)
    ->i32{a.wrapping_shr(7)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i32_rol(a : i32, b : u8)
    ->i32{a.rotate_left(b as u32)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i32_ror(a : i32, b : u8)
    ->i32{a.rotate_right(b as u32)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i32_as_signed(a : i32)
    ->i32{a as i32}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i32_as_unsigned(a : i32)
    ->u32{a as u32}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i32_narrow(a : i32)
    ->u16{a as u16}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn i32_widen(a : i32)
    ->i64 {
  a as i64
}
