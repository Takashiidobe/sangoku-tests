#![no_std]
#![feature(core_intrinsics)]
#![allow(internal_features, improper_ctypes_definitions)]

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u64_add(a : u64, b : u64) -> u64{a.wrapping_add(b)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u64_sub(a : u64, b : u64)
    ->u64{a.wrapping_sub(b)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u64_mul(a : u64, b : u64)
    ->u64{a.wrapping_mul(b)}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn u64_div(a : u64, b : u64)
    ->u64 {
  unsafe { core::intrinsics::unchecked_div(a, b) }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn u64_rem(a : u64, b : u64) -> u64 {
  unsafe { core::intrinsics::unchecked_rem(a, b) }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u64_and(a : u64, b : u64) -> u64{a & b}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u64_or(a : u64, b : u64)
    ->u64{a | b}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u64_xor(a : u64, b : u64)
    ->u64{a ^ b}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u64_eq(a : u64, b : u64)
    ->u8{(a == b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u64_ne(a : u64, b : u64)
    ->u8{(a != b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u64_lt(a : u64, b : u64)
    ->u8{(a < b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u64_le(a : u64, b : u64)
    ->u8{(a <= b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u64_gt(a : u64, b : u64)
    ->u8{(a > b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u64_ge(a : u64, b : u64)
    ->u8{(a >= b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u64_min(a : u64, b : u64)
    ->u64 {
  if a
    < b { a }
  else {
    b
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u64_max(a : u64, b : u64) -> u64 {
  if a
    > b { a }
  else {
    b
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u64_not(a : u64) -> u64{!a}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u64_neg(a : u64)
    ->u64{a.wrapping_neg()}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u64_add1(a : u64)
    ->u64{a.wrapping_add(1)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u64_mul3(a : u64)
    ->u64{a.wrapping_mul(3)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u64_mul10(a : u64)
    ->u64{a.wrapping_mul(10)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u64_div3(a : u64)
    ->u64{a / 3}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u64_rem10(a : u64)
    ->u64{a % 10}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u64_shl(a : u64, b : u8)
    ->u64{a.wrapping_shl(b as u32)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u64_shl1(a : u64)
    ->u64{a.wrapping_shl(1)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u64_shl7(a : u64)
    ->u64{a.wrapping_shl(7)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u64_shr(a : u64, b : u8)
    ->u64{a.wrapping_shr(b as u32)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u64_shr1(a : u64)
    ->u64{a.wrapping_shr(1)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u64_shr7(a : u64)
    ->u64{a.wrapping_shr(7)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u64_rol(a : u64, b : u8)
    ->u64{a.rotate_left(b as u32)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u64_ror(a : u64, b : u8)
    ->u64{a.rotate_right(b as u32)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u64_as_signed(a : u64)
    ->i64{a as i64}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u64_as_unsigned(a : u64)
    ->u64{a as u64}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u64_narrow(a : u64)
    ->u32 {
  a as u32
}
