#![no_std]
#![allow(internal_features, improper_ctypes_definitions)]

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn f64_add(a : f64, b : f64) -> f64{a + b}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn f64_sub(a : f64, b : f64)
    ->f64{a - b}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn f64_mul(a : f64, b : f64)
    ->f64{a * b}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn f64_div(a : f64, b : f64)
    ->f64{a / b}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn f64_eq(a : f64, b : f64)
    ->u8{(a == b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn f64_ne(a : f64, b : f64)
    ->u8{(a != b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn f64_lt(a : f64, b : f64)
    ->u8{(a < b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn f64_le(a : f64, b : f64)
    ->u8{(a <= b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn f64_gt(a : f64, b : f64)
    ->u8{(a > b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn f64_ge(a : f64, b : f64)
    ->u8{(a >= b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn f64_neg(a : f64)
    ->f64 {
  -a
}
