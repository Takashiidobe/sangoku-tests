#![no_std]
#![feature(core_intrinsics)]
#![allow(internal_features, improper_ctypes_definitions)]

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u16_add(a : u16, b : u16) -> u16{a.wrapping_add(b)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u16_sub(a : u16, b : u16)
    ->u16{a.wrapping_sub(b)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u16_mul(a : u16, b : u16)
    ->u16{a.wrapping_mul(b)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u16_mulhi(a: u16, b: u16) -> u16 {
  ((a as u32).wrapping_mul(b as u32) >> 16) as u16
}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u16_mul_u8(a: u16, b: u16) -> u16 {
  (a as u8 as u16).wrapping_mul(b)
}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u16_mul_loop(a: u16, n: u8) -> u16 {
  let mut sum = 0u16;
  for i in 0..n {
    sum = sum.wrapping_add(a.wrapping_mul(i as u16));
  }
  sum
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn u16_div(a : u16, b : u16)
    ->u16 {
  unsafe { core::intrinsics::unchecked_div(a, b) }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn u16_rem(a : u16, b : u16) -> u16 {
  unsafe { core::intrinsics::unchecked_rem(a, b) }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u16_divrem_xor(a: u16, b: u16) -> u16 {
  unsafe { core::intrinsics::unchecked_div(a, b) ^ core::intrinsics::unchecked_rem(a, b) }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u16_and(a : u16, b : u16) -> u16{a & b}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u16_or(a : u16, b : u16)
    ->u16{a | b}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u16_xor(a : u16, b : u16)
    ->u16{a ^ b}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u16_eq(a : u16, b : u16)
    ->u8{(a == b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u16_ne(a : u16, b : u16)
    ->u8{(a != b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u16_lt(a : u16, b : u16)
    ->u8{(a < b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u16_le(a : u16, b : u16)
    ->u8{(a <= b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u16_gt(a : u16, b : u16)
    ->u8{(a > b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u16_ge(a : u16, b : u16)
    ->u8{(a >= b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u16_min(a : u16, b : u16)
    ->u16 {
  if a
    < b { a }
  else {
    b
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u16_max(a : u16, b : u16) -> u16 {
  if a
    > b { a }
  else {
    b
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u16_not(a : u16) -> u16{!a}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u16_neg(a : u16)
    ->u16{a.wrapping_neg()}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u16_add1(a : u16)
    ->u16{a.wrapping_add(1)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u16_mul3(a : u16)
    ->u16{a.wrapping_mul(3)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u16_mul10(a : u16)
    ->u16{a.wrapping_mul(10)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u16_div3(a : u16)
    ->u16{a / 3}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u16_rem10(a : u16)
    ->u16{a % 10}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u16_div255(a: u16) -> u16 { a / 255 }

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u16_rem255(a: u16) -> u16 { a % 255 }

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u16_div257(a: u16) -> u16 { a / 257 }

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u16_rem257(a: u16) -> u16 { a % 257 }

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u16_div1(a: u16) -> u16 { a / 1 }

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u16_div2(a: u16) -> u16 { a / 2 }

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u16_div256(a: u16) -> u16 { a / 256 }

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u16_rem256(a: u16) -> u16 { a % 256 }

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u16_shl(a : u16, b : u8)
    ->u16{a.wrapping_shl(b as u32)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u16_shl1(a : u16)
    ->u16{a.wrapping_shl(1)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u16_shl7(a : u16)
    ->u16{a.wrapping_shl(7)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u16_shr(a : u16, b : u8)
    ->u16{a.wrapping_shr(b as u32)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u16_shr1(a : u16)
    ->u16{a.wrapping_shr(1)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u16_shr7(a : u16)
    ->u16{a.wrapping_shr(7)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u16_rol(a : u16, b : u8)
    ->u16{a.rotate_left(b as u32)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u16_ror(a : u16, b : u8)
    ->u16{a.rotate_right(b as u32)}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u16_as_signed(a : u16)
    ->i16{a as i16}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u16_as_unsigned(a : u16)
    ->u16{a as u16}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u16_narrow(a : u16)
    ->u8{a as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn u16_widen(a : u16)
    ->u32 {
  a as u32
}
