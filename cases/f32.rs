#![no_std]
#![allow(internal_features, improper_ctypes_definitions)]

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn f32_add(a : f32, b : f32) -> f32{a + b}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn f32_sub(a : f32, b : f32)
    ->f32{a - b}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn f32_mul(a : f32, b : f32)
    ->f32{a * b}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn f32_div(a : f32, b : f32)
    ->f32{a / b}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn f32_eq(a : f32, b : f32)
    ->u8{(a == b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn f32_ne(a : f32, b : f32)
    ->u8{(a != b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn f32_lt(a : f32, b : f32)
    ->u8{(a < b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn f32_le(a : f32, b : f32)
    ->u8{(a <= b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn f32_gt(a : f32, b : f32)
    ->u8{(a > b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn f32_ge(a : f32, b : f32)
    ->u8{(a >= b) as u8}

#[unsafe(no_mangle)]
#[inline(never)]
pub extern "C" fn f32_neg(a : f32)
    ->f32 {
  -a
}
