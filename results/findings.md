# Codegen findings

[comparison.json](comparison.json) records size and speed runs for 613 paired
probes: 388 numeric, 82 string/memory, 56 call/pressure, and 87 libc-style
pattern cases. Every case has an `analysis` with assembly evidence, observed
facts, inferred causes, and suggested areas to investigate. Sangoku compiles all
613; SDCC supplies 508 direct comparisons. The other 105 are unsupported
widths/features, including four byte-array struct-return capability probes that
crash SDCC.

In size mode, sangoku has the smaller function body in 25 cases, SDCC in 471,
and 12 tie. In speed mode those counts are 27, 469, and 12. These counts include
ABI overhead and exclude external helper bodies. String/memory and libc-style
pattern cases also measure reachable helpers: sangoku is smaller in 21 of 165
supported comparisons in both modes. All figures below use size mode.

| Case                  | Sangoku body | SDCC body | Sangoku with helpers | SDCC with helpers |
| --------------------- | -----------: | --------: | -------------------: | ----------------: |
| `strings_strlen`      |           89 |         3 |                  122 |                14 |
| `strings_strlen_loop` |           32 |        12 |                   32 |                12 |
| `strings_strcmp`      |          512 |        36 |                  593 |                81 |
| `strings_strcmp_loop` |          147 |       102 |                  147 |               102 |
| `strings_strcpy`      |          204 |         3 |                  269 |                14 |
| `strings_memmove`     |           51 |        24 |                  107 |               245 |
| `strings_memcpy4`     |           45 |         8 |                   77 |                58 |
| `strings_strchr`      |           62 |        44 |                   62 |                76 |

The helper totals come from isolated links, excluding startup, test entry, and
alignment padding. SDCC's linked totals are checked against its installed
archive members; the report includes disassembly of those linked bytes.
Sangoku's helper assembly and ROM section sizes are also included. Shared
helpers are charged once per case; an application can amortize them across
multiple calls. These are static size comparisons, with no timing claims.

`strlen` exposes substantial overhead around Rust's CStr abstraction. Its
wrapper reserves 14 stack bytes and calls a 33-byte Rust `strlen`, while SDCC
tail-jumps to an 11-byte helper. The wrapper also stores intermediate pointer
and length values that the final result does not need. Reducing those
materialized slice intermediates is a likely codegen improvement. The loop
control removes this abstraction, reducing Rust's total from 122 to 32 bytes.

The remaining `strlen_loop` gap has concrete instruction-selection evidence.
SDCC uses `add hl, bc` and `inc bc`. Sangoku recomputes the indexed address with
byte `add`/`adc`, increments the counter with explicit carry handling, emits a
self-copy, and uses absolute jumps for its block edges. This points to
register-pair arithmetic selection and branch/copy cleanup as areas to inspect.

`strcmp` changes the algorithm as well as the abstraction. The Rust library
probe scans both inputs through CStr and then compares the byte slices, while C
`strcmp` can compare during its scan. The matched-loop control reduces sangoku
from 593 to 147 bytes and SDCC uses 102 bytes. Treat the larger library-style
gap as a mixture of source algorithm and codegen costs. Likewise, Rust's
`strcpy` probe scans to determine the length before copying; C's helper copies
and tests for NUL in the same loop.

`memmove` demonstrates why wrapper size alone can reverse the result. SDCC pulls
in a 171-byte memmove member and a 50-byte memcpy member. Sangoku uses one
56-byte helper. Its wrapper costs 27 more bytes, but its isolated total saves
138 bytes. The speed-mode Rust helper is larger, and its total rises to 165
bytes versus SDCC's 245; runtime still needs measurement.

The fixed-length `memcpy4` and `memcpy16` probes both retain general copy
helpers. Sangoku reserves seven stack bytes and marshals arguments through
several stores and reloads. SDCC's wrapper loads the count, pushes it, calls,
and returns. Reducing marshaling and evaluating an inline small-copy strategy
are separate opportunities. The same comparison controls exist for fills, moves,
and memory comparisons.

Numeric findings remain visible in the same report:

| Case        | Sangoku body | SDCC body | Evidence                                                                           |
| ----------- | -----------: | --------: | ---------------------------------------------------------------------------------- |
| `u8_add`    |            5 |         2 | Result moves through H and immediately back into A                                 |
| `u16_div3`  |        1,103 |         6 | Rust calls four wide-multiply helpers and two mul32 helpers; C tail-calls division |
| `i32_rem10` |        2,559 |        11 | Rust emits multiply and shift helper calls                                         |
| `u64_le`    |          436 |        45 | No external helper calls; SP references are 63 versus 3                            |
| `u64_add`   |          538 |       152 | No external helper calls; SP references are 85 versus 29                           |

Start with redundant moves, native register-pair arithmetic, and wide
comparison/add lowering. Investigate constant division's multiplication
expansion under `--opt-level z`, accounting for helper cost before choosing a
replacement. SP references include arguments and locals, so these counts do not
measure spills or peak stack usage directly.

Unsigned addition grows from 5 to 12, 133, 538, and 1,644 bytes in sangoku at 8,
16, 32, 64, and 128 bits. SDCC uses 2, 6, 58, and 152 bytes through 64 bits. The
128-bit probe emits 98 pushes, 98 pops, and 440 bytes through `db`. Inspect
carry propagation and preservation of live values. The JSON's width patterns
provide the same comparison for every operation without inventing a C baseline
for unsupported widths.

Inspect the evidence and helper implementations with:

```bash
python3 tools/report.py --kind string
python3 tools/report.py --case strings_strlen_loop
python3 tools/report.py --case strings_memmove --dependencies
python3 tools/report.py --case u16_div3
```

[semantics.json](semantics.json) records 41,118 passing host integer vectors per
language against Clang, with UBSan enabled for C.
[string-semantics.json](string-semantics.json) records 15,744 passing host
string/memory vectors against Clang and libc, including buffer contents and
relative return pointers. The 28 harness/catalog tests also validate archive
accounting, ranking reversals, and disassembler round trips through RGBDS. These
checks validate the harness and source pairing; SM83 execution and
floating-point runtime correctness remain untested.

Call fixtures in [calls.json](calls.json) isolate direct/indirect dispatch,
argument placement, local storage, and preservation pressure. The caller and its
deliberately non-inlined fixture callees have separate byte metrics. The runner
verifies that expected direct calls/tail transfers remain in the output.

| Fixture                 | Sangoku caller bytes | SDCC caller bytes | Sangoku leading SP reservation | SDCC leading SP reservation |
| ----------------------- | -------------------: | ----------------: | -----------------------------: | --------------------------: |
| `calls_u8_tail`         |                    4 |                 3 |                              0 |                           0 |
| `calls_u8_args6`        |                   33 |                27 |                              3 |                           0 |
| `calls_u8_live8`        |                  264 |               132 |                             20 |                           9 |
| `calls_u8_live8_inline` |                  275 |               122 |                             18 |                           8 |
| `calls_u8_local32`      |                  727 |                47 |                             58 |                          32 |
| `calls_u64_live8`       |                7,213 |             1,793 |                            291 |                          83 |

`calls_u8_tail` emits `call`/`ret` in sangoku and a tail `jp` in SDCC. Check
whether the caller/callee ABI permits tail-call elimination before generalizing
that optimization to stack-argument cases.

`calls_u8_live8` loads eight volatile values before the fixture call and uses
each in a dependent fold afterward. Against its inline control, sangoku's
leading reservation grows by two bytes and SDCC's by one. Sangoku's caller is
actually 11 bytes smaller than its inline control, while its caller plus callee
is six bytes smaller. Scheduling and register allocation can make a function
boundary reduce code size, so the entire 132-byte compiler gap is not evidence
of call-induced spills.

`calls_u8_local32` requires a 32-byte local array whose address escapes to the
callee. Rust uses MaybeUninit, writes every byte before passing the address, and
performs no extra zero-initialization. Sangoku still reserves 58 bytes and emits
727 caller bytes, while SDCC reserves 32 and emits 47. This points to additional
local temporaries and loop/address lowering, independently of the required array
storage.

The 64-bit pressure case reserves 291 bytes in sangoku versus 83 in SDCC. Its
inline control reserves 270 versus 83. The extra 21-byte sangoku reservation is
a useful call-preservation lead; register-allocation dumps or liveness analysis
are needed to identify actual spill slots. Reservations exclude pushes, return
addresses, callees and alternate frame setup; none of these figures is peak
stack depth.

[call-semantics.json](call-semantics.json) records 7,168 passing host vectors
against Clang across all call fixtures. Coverage now includes all integer
comparison forms, rotations, signedness casts, truncation and representative
extension, plus all float comparison forms. Checked/saturating arithmetic,
bit-count intrinsics, float remainder, and float/integer casts remain outside
the current fixture set.

The new libc-style patterns are also available as
[patterns.json](patterns.json). The table below gives isolated
function-plus-helper ROM bytes in size mode:

| Pattern                      | Sangoku |  SDCC | What the control exposes                                           |
| ---------------------------- | ------: | ----: | ------------------------------------------------------------------ |
| `format_u16_decimal_divmod`  |   2,071 |   358 | Repeated quotient/remainder lowering, temporary digit buffer       |
| `format_u16_decimal_library` |  30,686 | 2,833 | Generic formatting machinery in addition to numeric conversion     |
| `parse_strtoul_decimal`      |   1,543 | 1,653 | Wrapper-only ranking reverses when the generic C parser is charged |
| `slices_sum_index`           |     444 |    68 | Indexed safe-slice metadata and potential retained checks          |
| `slices_sum_iter`            |     784 |    68 | Smaller Rust caller can still pull in more helper code             |
| `slices_sum_raw`             |     258 |    68 | Same byte-sum algorithm without safe-slice/iterator abstraction    |
| `aggregate_out3_call`        |     612 |    90 | Aggregate local, out-parameter call, then copy to output           |
| `aggregate_pair_return`      |      64 |    36 | Pointer/length result ABI and materialized aggregate               |

The parser library case has a deliberately restricted valid-input domain and
ignores errno; C's generic strtoul retains support for other bases and error
conditions. Likewise, sprintf and core::fmt retain different machinery, and
qsort versus sort_unstable use different algorithms. Use the matched loops
before treating these library-level gaps as instruction-selection failures.

Direct dereferenced struct returns (`return *p;`) of 3, 5, 8 and 12 byte arrays
trigger SDCC internal errors in capability probes. The failure also reproduces
with signed bytes, plain char, separate fields, and a single uint16_t field. A
named local copy followed by `return local;` compiles; the diagnosis is the
return-expression lowering, not byte arrays or aggregate returns in general.
This matches [SDCC issue 4250](https://sourceforge.net/p/sdcc/bugs/4250/). Their
diagnostics are preserved and no C size is invented. Assignment and
out-parameter controls compile in both languages; the pointer/length pair return
also compiles in both. This separates unsupported return lowering from ordinary
aggregate-copy overhead.

Memory probes now cover fixed lengths 0, 1, 2, 3, 4, 7, 8, 15, 16, 17, 31, 32,
63, 64, 127 and 128, plus computed pointer offsets 1, 3 and 7. Host validation
varies alignment and overlapping move direction, and compares full buffers,
including bytes outside the requested span.

[pattern-semantics.json](pattern-semantics.json) records 22,272 passing host
vectors for the 87 pattern cases. The expanded memory/string check records
15,744 vectors across 82 cases. These validate the source pairs and output
contracts; target execution and timing remain separate.
