#![no_std]
#![allow(unused_unsafe, improper_ctypes_definitions)]

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn parse_decimal_loop(src : *const u8, end : *mut u16)
    -> u32 {
  unsafe {
    let mut i = 0usize;
    let mut value = 0u32;
    while
      *src.add(i) == b ' ' || (9.. = 13).contains(&*src.add(i)) { i += 1; }
    let minus = *src.add(i) == b '-';
    if minus
      || *src.add(i) == b '+' { i += 1; }
    let first = i;
    while
      *src.add(i) >= b '0' && *src.add(i) <= b '9' {
        value =
            value.wrapping_mul(10).wrapping_add((*src.add(i) - b '0') as u32);
        i += 1;
      }
    *end = if i == first{0} else {i as u16};
    if minus {
      value.wrapping_neg()
    } else {
      value
    }
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn parse_strtoul_decimal(src : *const u8, end : *mut u16)
    -> u32 {
  unsafe {
    let mut i = 0usize;
    let mut value = 0u32;
    while
      *src.add(i) == b ' ' || (9.. = 13).contains(&*src.add(i)) { i += 1; }
    let minus = *src.add(i) == b '-';
    if minus
      || *src.add(i) == b '+' { i += 1; }
    let first = i;
    while
      *src.add(i) >= b '0' && *src.add(i) <= b '9' {
        value =
            value.wrapping_mul(10).wrapping_add((*src.add(i) - b '0') as u32);
        i += 1;
      }
    *end = if i == first{0} else {i as u16};
    if minus {
      value.wrapping_neg()
    } else {
      value
    }
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn parse_decimal_checked(src : *const u8, end : *mut u16)
    -> u32 {
  unsafe {
    let mut i = 0usize;
    let mut value = 0u32;
    let mut overflow = false;
    while
      *src.add(i) == b ' ' || (9.. = 13).contains(&*src.add(i)) { i += 1; }
    let minus = *src.add(i) == b '-';
    if minus
      || *src.add(i) == b '+' { i += 1; }
    let first = i;
    while
      *src.add(i) >= b '0' && *src.add(i) <= b '9' {
        let d = (*src.add(i) - b '0') as u32;
        if value
          > (u32::MAX - d) / 10 {
            overflow = true;
            value = u32::MAX;
          }
        else if !overflow {
          value = value * 10 + d;
        }
        i += 1;
      }
    *end = (if i == first{0} else {i as u16}) | if overflow{0x8000} else {0};
    if minus {
      value.wrapping_neg()
    } else {
      value
    }
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn parse_hex_loop(src : *const u8, end : *mut u16)
    -> u32 {
  unsafe {
    let mut i = 0usize;
    let mut value = 0u32;
    if
      *src == b '0' && (*src.add(1) == b 'x' || *src.add(1) == b 'X') { i = 2; }
    let first = i;
    loop {
      let c = *src.add(i);
      let d = if c >= b '0' && c <= b '9' {c - b '0'} else if c >= b 'a' &&
              c <= b 'f' {c - b 'a' + 10} else if c >= b 'A' &&
              c <= b 'F' {c - b 'A' + 10} else {255};
      if d
        == 255 { break; }
      value = (value << 4) | d as u32;
      i += 1;
    }
    *end = if i == first{0} else {i as u16};
    value
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn parse_atoi(src : *const u8) -> i16 {
  unsafe {
    let mut i = 0usize;
    let mut value = 0u32;
    while
      *src.add(i) == b ' ' || (9.. = 13).contains(&*src.add(i)) { i += 1; }
    let minus = *src.add(i) == b '-';
    if minus
      || *src.add(i) == b '+' { i += 1; }
    let first = i;
    while
      *src.add(i) >= b '0' && *src.add(i) <= b '9' {
        value =
            value.wrapping_mul(10).wrapping_add((*src.add(i) - b '0') as u32);
        i += 1;
      }
    let _ = first;
    (if minus { value.wrapping_neg() } else {value}) as i16
  }
}
