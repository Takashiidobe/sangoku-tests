#![no_std]
#![feature(f16)]
#![allow(internal_features, improper_ctypes_definitions)]

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn f16_add(a : f16, b : f16) -> f16{a + b}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn f16_sub(a : f16, b : f16)
    ->f16{a - b}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn f16_mul(a : f16, b : f16)
    ->f16{a * b}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn f16_div(a : f16, b : f16)
    ->f16{a / b}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn f16_eq(a : f16, b : f16)
    ->u8{(a == b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn f16_ne(a : f16, b : f16)
    ->u8{(a != b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn f16_lt(a : f16, b : f16)
    ->u8{(a < b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn f16_le(a : f16, b : f16)
    ->u8{(a <= b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn f16_gt(a : f16, b : f16)
    ->u8{(a > b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn f16_ge(a : f16, b : f16)
    ->u8{(a >= b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn f16_neg(a : f16)
    ->f16 {
  -a
}
