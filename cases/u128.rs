#![no_std]
#![feature(core_intrinsics)]
#![allow(internal_features, improper_ctypes_definitions)]

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u128_add(a : u128, b : u128) -> u128{a.wrapping_add(b)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u128_sub(a : u128, b : u128)
    ->u128{a.wrapping_sub(b)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u128_mul(a : u128, b : u128)
    ->u128{a.wrapping_mul(b)}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn u128_div(a : u128, b : u128)
    ->u128 {
  unsafe { core::intrinsics::unchecked_div(a, b) }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn u128_rem(a : u128, b : u128) -> u128 {
  unsafe { core::intrinsics::unchecked_rem(a, b) }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u128_and(a : u128, b : u128) -> u128{a & b}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u128_or(a : u128, b : u128)
    ->u128{a | b}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u128_xor(a : u128, b : u128)
    ->u128{a ^ b}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u128_eq(a : u128, b : u128)
    ->u8{(a == b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u128_ne(a : u128, b : u128)
    ->u8{(a != b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u128_lt(a : u128, b : u128)
    ->u8{(a < b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u128_le(a : u128, b : u128)
    ->u8{(a <= b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u128_gt(a : u128, b : u128)
    ->u8{(a > b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u128_ge(a : u128, b : u128)
    ->u8{(a >= b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u128_min(a : u128, b : u128)
    ->u128 {
  if a
    < b { a }
  else {
    b
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u128_max(a : u128, b : u128) -> u128 {
  if a
    > b { a }
  else {
    b
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u128_not(a : u128) -> u128{!a}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u128_neg(a : u128)
    ->u128{a.wrapping_neg()}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u128_add1(a : u128)
    ->u128{a.wrapping_add(1)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u128_mul3(a : u128)
    ->u128{a.wrapping_mul(3)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u128_mul10(a : u128)
    ->u128{a.wrapping_mul(10)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u128_div3(a : u128)
    ->u128{a / 3}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u128_rem10(a : u128)
    ->u128{a % 10}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u128_shl(a : u128, b : u8)
    ->u128{a.wrapping_shl(b as u32)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u128_shl1(a : u128)
    ->u128{a.wrapping_shl(1)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u128_shl7(a : u128)
    ->u128{a.wrapping_shl(7)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u128_shr(a : u128, b : u8)
    ->u128{a.wrapping_shr(b as u32)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u128_shr1(a : u128)
    ->u128{a.wrapping_shr(1)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u128_shr7(a : u128)
    ->u128{a.wrapping_shr(7)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u128_rol(a : u128, b : u8)
    ->u128{a.rotate_left(b as u32)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u128_ror(a : u128, b : u8)
    ->u128{a.rotate_right(b as u32)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u128_as_signed(a : u128)
    ->i128{a as i128}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u128_as_unsigned(a : u128)
    ->u128{a as u128}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u128_narrow(a : u128)
    ->u64 {
  a as u64
}
