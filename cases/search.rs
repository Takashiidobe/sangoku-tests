#![no_std]
#![allow(unused_unsafe, improper_ctypes_definitions)]

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn search_binary_loop(src : *const u16, n : u16,
                                            value : u16) -> u16 {
  unsafe {
    let mut low = 0usize;
    let mut high = n as usize;
    while
      low < high {
        let mid = low + (high - low) / 2;
        let x = *src.add(mid);
        if x
          < value { low = mid + 1; }
        else if x
          > value { high = mid; }
        else {
          return mid as u16;
        }
      }
    u16::MAX
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn search_bsearch_library(src : *const u16, n : u16,
                                                value : u16) -> u16 {
  unsafe {
    core::slice::from_raw_parts(src, n as usize)
        .binary_search(&value)
        .map_or(u16::MAX, | i | i as u16)
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn search_insertion_sort(dst : *mut u16, n : u16)
    -> *mut u8 {
  unsafe {
        for
          i in 1..n as usize {
            let value = *dst.add(i);
            let mut j = i;
            while
              j != 0 && *dst.add(j - 1) > value {
                *dst.add(j) = *dst.add(j - 1);
                j -= 1;
              }
            *dst.add(j) = value;
          }
        dst.cast::<u8>()
  }
}

#[unsafe(no_mangle)]
#[inline(never)]
pub unsafe extern "C" fn search_qsort_library(dst : *mut u16, n : u16)
    -> *mut u8 {
  unsafe {
    core::slice::from_raw_parts_mut(dst, n as usize).sort_unstable();
    dst.cast::<u8>()
  }
}
