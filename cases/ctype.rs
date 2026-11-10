#![no_std]
#![allow(unused_unsafe, improper_ctypes_definitions)]

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn ctype_isdigit_loop(value : u8) -> u8 {
  unsafe { (value >= b '0' && value <= b '9') as u8 }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn ctype_isdigit_library(value : u8) -> u8 {
  unsafe { value.is_ascii_digit() as u8 }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn ctype_isalpha_loop(value : u8) -> u8 {
  unsafe {
    ((value >= b 'A' && value <= b 'Z') || (value >= b 'a' && value <= b 'z'))
        as u8
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn ctype_isalpha_library(value : u8) -> u8 {
  unsafe { value.is_ascii_alphabetic() as u8 }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn ctype_isspace_loop(value : u8) -> u8 {
  unsafe { (value == b ' ' || (value >= 9 && value <= 13)) as u8 }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn ctype_isspace_library(value : u8) -> u8 {
  unsafe { (value == b ' ' || (9.. = 13).contains(&value)) as u8 }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn ctype_tolower_loop(value : u8) -> u8 {
  unsafe {
    (if value >= b 'A' &&
     value <= b 'Z' { value + (b 'a' - b 'A') } else {value}) as u8
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn ctype_tolower_library(value : u8) -> u8 {
  unsafe { value.to_ascii_lowercase() }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn ctype_toupper_loop(value : u8) -> u8 {
  unsafe {
    (if value >= b 'a' &&
     value <= b 'z' { value - (b 'a' - b 'A') } else {value}) as u8
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn ctype_toupper_library(value : u8) -> u8 {
  unsafe { value.to_ascii_uppercase() }
}
