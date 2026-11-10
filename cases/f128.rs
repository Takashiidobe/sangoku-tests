#![no_std]
#![feature(f128)]
#![allow(internal_features, improper_ctypes_definitions)]

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn f128_add(a : f128, b : f128) -> f128{a + b}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn f128_sub(a : f128, b : f128)
    ->f128{a - b}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn f128_mul(a : f128, b : f128)
    ->f128{a * b}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn f128_div(a : f128, b : f128)
    ->f128{a / b}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn f128_eq(a : f128, b : f128)
    ->u8{(a == b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn f128_ne(a : f128, b : f128)
    ->u8{(a != b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn f128_lt(a : f128, b : f128)
    ->u8{(a < b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn f128_le(a : f128, b : f128)
    ->u8{(a <= b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn f128_gt(a : f128, b : f128)
    ->u8{(a > b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn f128_ge(a : f128, b : f128)
    ->u8{(a >= b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn f128_neg(a : f128)
    ->f128 {
  -a
}
