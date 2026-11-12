#![no_std]
#![feature(core_intrinsics)]
#![allow(internal_features, improper_ctypes_definitions)]

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u32_add(a : u32, b : u32) -> u32{a.wrapping_add(b)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u32_sub(a : u32, b : u32)
    ->u32{a.wrapping_sub(b)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u32_mul(a : u32, b : u32)
    ->u32{a.wrapping_mul(b)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u32_mulhi(a: u32, b: u32) -> u32 {
  ((a as u64).wrapping_mul(b as u64) >> 32) as u32
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn u32_div(a : u32, b : u32)
    ->u32 {
  unsafe { core::intrinsics::unchecked_div(a, b) }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn u32_rem(a : u32, b : u32) -> u32 {
  unsafe { core::intrinsics::unchecked_rem(a, b) }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u32_and(a : u32, b : u32) -> u32{a & b}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u32_or(a : u32, b : u32)
    ->u32{a | b}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u32_xor(a : u32, b : u32)
    ->u32{a ^ b}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u32_eq(a : u32, b : u32)
    ->u8{(a == b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u32_ne(a : u32, b : u32)
    ->u8{(a != b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u32_lt(a : u32, b : u32)
    ->u8{(a < b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u32_le(a : u32, b : u32)
    ->u8{(a <= b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u32_gt(a : u32, b : u32)
    ->u8{(a > b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u32_ge(a : u32, b : u32)
    ->u8{(a >= b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u32_min(a : u32, b : u32)
    ->u32 {
  if a
    < b { a }
  else {
    b
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u32_max(a : u32, b : u32) -> u32 {
  if a
    > b { a }
  else {
    b
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u32_not(a : u32) -> u32{!a}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u32_neg(a : u32)
    ->u32{a.wrapping_neg()}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u32_add1(a : u32)
    ->u32{a.wrapping_add(1)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u32_mul3(a : u32)
    ->u32{a.wrapping_mul(3)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u32_mul10(a : u32)
    ->u32{a.wrapping_mul(10)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u32_div3(a : u32)
    ->u32{a / 3}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u32_rem10(a : u32)
    ->u32{a % 10}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u32_shl(a : u32, b : u8)
    ->u32{a.wrapping_shl(b as u32)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u32_shl1(a : u32)
    ->u32{a.wrapping_shl(1)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u32_shl7(a : u32)
    ->u32{a.wrapping_shl(7)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u32_shr(a : u32, b : u8)
    ->u32{a.wrapping_shr(b as u32)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u32_shr1(a : u32)
    ->u32{a.wrapping_shr(1)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u32_shr7(a : u32)
    ->u32{a.wrapping_shr(7)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u32_rol(a : u32, b : u8)
    ->u32{a.rotate_left(b as u32)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u32_ror(a : u32, b : u8)
    ->u32{a.rotate_right(b as u32)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u32_as_signed(a : u32)
    ->i32{a as i32}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u32_as_unsigned(a : u32)
    ->u32{a as u32}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u32_narrow(a : u32)
    ->u16{a as u16}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u32_widen(a : u32)
    ->u64 {
  a as u64
}
