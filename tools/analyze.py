from collections import Counter
import re


def instructions(assembly):
    lines = []
    for number, raw in enumerate(assembly.splitlines(), 1):
        line = raw.split(";", 1)[0].strip()
        if (
            line
            and not line.endswith(":")
            and not line.startswith(".")
            and line.split()[0].lower() not in {"export", "section", "def"}
        ):
            lines.append((number, re.sub(r"\s+", " ", line.lower())))
    return lines


def move_evidence(assembly):
    lines = instructions(assembly)
    identity = []
    reloads = []
    for index, (number, line) in enumerate(lines):
        match = re.fullmatch(r"ld ([abcdehl]),\s*([abcdehl])", line)
        if match and match[1] == match[2]:
            identity.append({"line": number, "instruction": line})
        if match and match[1] != match[2] and index + 1 < len(lines):
            after = lines[index + 1]
            if re.fullmatch(rf"ld {match[2]},\s*{match[1]}", after[1]) and not any(
                line.strip().endswith(":")
                for line in assembly.splitlines()[number : after[0] - 1]
            ):
                reloads.append({"line": number, "instructions": [line, after[1]]})
    return {"identity_moves": identity, "immediate_reloads": reloads}


def annotate(rows):
    by_id = {r["id"]: r for r in rows}
    for row in rows:
        r, c = row["sangoku"], row["sdcc"]
        notes = []
        row["comparison"].pop("with_dependencies", None)

        def note(
            category,
            observation,
            evidence=None,
            implication=None,
            confidence="observed",
        ):
            notes.append(
                {
                    "category": category,
                    "confidence": confidence,
                    "observation": observation,
                    "evidence": evidence or {},
                    **({"investigate": implication} if implication else {}),
                }
            )

        if row["comparison"]["status"] != "compared":
            status = row["comparison"]["status"]
            summary = (
                "No direct C baseline for this fixture; inspect Rust lowering and related controls."
                if status == "pattern_only"
                else "Compilation or measurement failed; no size judgment is available."
            )
            note(
                "support",
                summary,
                {compiler: row[compiler]["status"] for compiler in ["sangoku", "sdcc"]},
            )
        else:
            delta = row["comparison"]["bytes_delta"]
            summary = (
                f"Sangoku function body is {abs(delta)} bytes "
                + ("larger" if delta > 0 else "smaller")
                + " than SDCC."
                if delta
                else "The function bodies have equal assembled size."
            )
            note(
                "body_size",
                summary,
                {
                    compiler: row[compiler]["function_bytes"]
                    for compiler in ["sangoku", "sdcc"]
                },
            )
            stack_delta = r["stack_reference_count"] - c["stack_reference_count"]
            if stack_delta:
                note(
                    "stack_addressing",
                    f"Sangoku has {abs(stack_delta)} "
                    + ("more" if stack_delta > 0 else "fewer")
                    + " source instructions referencing SP.",
                    {
                        compiler: {
                            key: row[compiler][key]
                            for key in [
                                "stack_reference_count",
                                "push_count",
                                "pop_count",
                            ]
                        }
                        for compiler in ["sangoku", "sdcc"]
                    },
                    "Inspect value lifetimes, stack slot reuse and argument/result marshaling. SP references include arguments and locals, so they are not a pure spill count.",
                    "inference",
                )
            pair_ops = {
                compiler: [
                    text
                    for _, text in instructions(row[compiler]["assembly"])
                    if re.fullmatch(
                        r"(?:add hl,\s*(?:bc|de|hl|sp)|(?:inc|dec) (?:bc|de|hl|sp))",
                        text,
                    )
                ]
                for compiler in ["sangoku", "sdcc"]
            }
            if len(pair_ops["sangoku"]) != len(pair_ops["sdcc"]):
                note(
                    "pair_arithmetic",
                    "The source uses different amounts of native register-pair arithmetic.",
                    {
                        compiler: {"count": len(ops), "examples": ops[:4]}
                        for compiler, ops in pair_ops.items()
                    },
                    "Compare native 16-bit address arithmetic with split-byte add/carry sequences. Account for differing algorithms and calling conventions before attributing the size gap.",
                    "inference",
                )
            branch = {
                compiler: sum(
                    row[compiler]["mnemonics"].get(op, 0) for op in ["jp", "jr"]
                )
                for compiler in ["sangoku", "sdcc"]
            }
            if branch["sangoku"] != branch["sdcc"]:
                note(
                    "control_flow",
                    "The emitted source has different branch structure.",
                    branch,
                    "Inspect compare/boolean lowering and fallthrough layout; branch counts alone do not determine cycles.",
                    "inference",
                )
        if r["status"] == "ok":
            moves = move_evidence(r["assembly"])
            if moves["identity_moves"] or moves["immediate_reloads"]:
                note(
                    "redundant_moves",
                    "Sangoku emits register self-copies or an immediate reload of a value just copied from that register.",
                    {
                        key: {"count": len(value), "examples": value[:3]}
                        for key, value in moves.items()
                    },
                    "Add or improve post-allocation copy cleanup; verify register liveness before removing the original copy.",
                )
            if r["inline_machine_code_bytes"]:
                note(
                    "opaque_machine_code",
                    f"{r['inline_machine_code_bytes']} bytes are emitted through db. They count toward function size but are absent from source mnemonic counts.",
                    {"inline_machine_code_bytes": r["inline_machine_code_bytes"]},
                )
            if row["kind"] == "integer" and row["width"] > 16:
                small = by_id.get(
                    f"{'i' if row['signed'] else 'u'}{row['width'] // 2}_{row['operation']}"
                )
                if small and small["sangoku"]["status"] == "ok":
                    note(
                        "width_scaling",
                        "Compare this lowering with the next smaller integer width.",
                        {
                            "current_bits": row["width"],
                            "current_bytes": r["function_bytes"],
                            "smaller_case": small["id"],
                            "smaller_bytes": small["sangoku"]["function_bytes"],
                        },
                        "Inspect carry/sign propagation and live multi-byte values. The growth also includes wider arguments/results.",
                        "inference",
                    )
            base_op = {
                "div3": "div",
                "rem10": "rem",
                "mul3": "mul",
                "mul10": "mul",
                "add1": "add",
            }.get(row["operation"])
            if base_op:
                variable = by_id.get(f"{row['type']}_{base_op}")
                if variable and variable["sangoku"]["status"] == "ok":
                    targets = [t["target"] for t in r["external_transfers"]]
                    note(
                        "constant_lowering",
                        "Compare the constant operand form with its variable operand counterpart.",
                        {
                            "constant_bytes": r["function_bytes"],
                            "variable_case": variable["id"],
                            "variable_bytes": variable["sangoku"]["function_bytes"],
                            "helper_targets": dict(Counter(targets)),
                        },
                        "Review the constant-operation cost model. Multiplication helpers in constant division/remainder are consistent with reciprocal-multiply expansion; check intermediate IR before attributing the cause.",
                        "inference",
                    )
        if any(
            row[compiler].get("external_transfers") for compiler in ["sangoku", "sdcc"]
        ):
            note(
                "helper_calls",
                "Part of the implementation is outside the measured function body.",
                {
                    compiler: list(
                        dict.fromkeys(
                            t["target"]
                            for t in row[compiler].get("external_transfers", [])
                        )
                    )
                    for compiler in ["sangoku", "sdcc"]
                },
                "Compare reachable helper bodies and calling conventions before judging total code size or speed.",
            )
        if row["comparison"]["status"] == "compared":
            strategies = {}
            for compiler in ["sangoku", "sdcc"]:
                transfers = row[compiler]["external_transfers"]
                strategies[compiler] = {
                    "calls": sum(t["kind"] == "call" for t in transfers),
                    "tail_jumps": sum(t["kind"] in {"jp", "jr"} for t in transfers),
                    "targets": sorted({t["target"] for t in transfers}),
                }
            if strategies["sangoku"] != strategies["sdcc"] and any(
                v["targets"] for v in strategies.values()
            ):
                note(
                    "helper_strategy",
                    "The wrappers use different helper calls or tail transfers.",
                    strategies,
                    "A tail transfer can avoid a call/return pair and argument cleanup in the wrapper. An inline loop versus a helper trades shared code size against call overhead; measure runtime before choosing.",
                    "inference",
                )
        if row["kind"] == "integer" and row["operation"] in {"shl", "shr"}:
            note(
                "shift_count",
                "Both sources mask variable shift counts to the operand width minus one.",
                {
                    "mask": row["width"] - 1,
                    "rust_count_source_type": "u8 converted to u32",
                },
                "Inspect shift-count widening, repeated masks and helper argument setup; unsafe unchecked shifts are not being compared against wrapping shifts.",
                "inference",
            )
        libraries = {
            compiler: row[compiler].get("library", {})
            for compiler in ["sangoku", "sdcc"]
        }
        if all(
            v.get("status") == "ok" and "total_bytes" in v for v in libraries.values()
        ):
            rb, cb = [
                libraries[compiler]["total_bytes"] for compiler in ["sangoku", "sdcc"]
            ]
            delta = rb - cb
            row["comparison"]["with_dependencies"] = {
                "sangoku_bytes": rb,
                "sdcc_bytes": cb,
                "bytes_delta": delta,
                "bytes_ratio": rb / cb if cb else None,
                "smaller": "tie" if rb == cb else "sangoku" if rb < cb else "sdcc",
            }
            note(
                "dependency_size",
                "Including reachable helpers "
                + (
                    "reverses the function-body ranking."
                    if row["comparison"].get("smaller")
                    != row["comparison"]["with_dependencies"]["smaller"]
                    else "preserves the function-body ranking."
                ),
                {
                    "total_bytes": {"sangoku": rb, "sdcc": cb},
                    "dependency_bytes": {
                        compiler: libraries[compiler]["dependency_bytes"]
                        for compiler in libraries
                    },
                },
                "This is cold, isolated ROM cost. Shared helpers are charged once per case; an application can amortize them across calls. SDCC cost is at archive-member granularity.",
            )
        if row["kind"] == "call":
            note(
                "call_shape",
                row["semantic_note"],
                {
                    "expected_fixture_calls_or_tail_transfers": row[
                        "expected_fixture_calls"
                    ],
                    "live_values_across_call": row["live_values_across_call"],
                    "explicit_local_array_bytes": row["explicit_local_array_bytes"],
                },
            )
            note(
                "stack_evidence",
                "Compare explicit stack reservation and adjacent stack load/store patterns.",
                {
                    compiler: row[compiler].get("stack")
                    for compiler in ["sangoku", "sdcc"]
                },
                "These patterns include locals, stack arguments and caller/callee saves. Register-allocation dumps or liveness analysis are required to classify exact spills; this is not peak stack depth.",
                "inference",
            )
            if any(
                row[compiler].get("fixture_helpers") for compiler in ["sangoku", "sdcc"]
            ):
                note(
                    "fixture_callees",
                    "The deliberately non-inlined fixture callees are measured separately from the caller.",
                    {
                        compiler: {
                            "caller_bytes": row[compiler].get("function_bytes"),
                            "callee_bytes": row[compiler].get(
                                "fixture_helper_bytes", 0
                            ),
                            "caller_plus_callees_bytes": row[compiler].get(
                                "function_with_fixture_helpers_bytes"
                            ),
                        }
                        for compiler in ["sangoku", "sdcc"]
                    },
                    "These totals exclude further runtime helpers. Compare caller frames and callee prologues independently.",
                )
            control_id = (
                row["id"] + "_inline"
                if row["live_values_across_call"]
                else row["type"] + "_leaf"
                if row["operation"] == "tail"
                else None
            )
            control = by_id.get(control_id)
            if control and all(
                row[compiler]["status"] == control[compiler]["status"] == "ok"
                for compiler in ["sangoku", "sdcc"]
            ):
                changes = {}
                for compiler in ["sangoku", "sdcc"]:
                    measured, base = row[compiler], control[compiler]
                    changes[compiler] = {
                        "caller_bytes_delta": measured["function_bytes"]
                        - base["function_bytes"],
                        "caller_and_fixture_callees_bytes_delta": measured.get(
                            "function_with_fixture_helpers_bytes",
                            measured["function_bytes"],
                        )
                        - base["function_bytes"],
                        "entry_add_sp_reservation_delta": measured["stack"][
                            "entry_add_sp_reservation_bytes"
                        ]
                        - base["stack"]["entry_add_sp_reservation_bytes"],
                        "stack_reference_delta": measured["stack_reference_count"]
                        - base["stack_reference_count"],
                        "push_delta": measured["push_count"] - base["push_count"],
                    }
                row["comparison"]["call_control"] = {"case": control_id, **changes}
                note(
                    "call_control",
                    "Compare the same computation with an inline/no-call control.",
                    row["comparison"]["call_control"],
                    "The delta includes call marshaling, preservation and changed scheduling, not just proven spill instructions.",
                    "inference",
                )
            if row["operation"] == "indirect":
                note(
                    "indirect_call",
                    "A runtime callback forces an indirect transfer.",
                    {
                        compiler: {
                            "indirect_sites": row[compiler]
                            .get("stack", {})
                            .get("indirect_transfer_sites"),
                            "external_targets": row[compiler].get("external_transfers"),
                        }
                        for compiler in ["sangoku", "sdcc"]
                    },
                    "Inspect return-address synthesis, trampolines and argument shuffling separately from direct-call cost.",
                    "inference",
                )
        if row["kind"] == "pattern":
            note(
                "pattern_contract",
                row["semantic_note"],
                {
                    "family": row["pattern_family"],
                    "style": row["style"],
                    "domain": row["domain"],
                },
            )
            if row["style"] in {"library", "idiomatic"}:
                note(
                    "abstraction_boundary",
                    "This probe uses a library or idiomatic API on at least one side.",
                    {"description": row["description"]},
                    "Use the matching raw/loop control to separate algorithm choice, abstraction and ABI costs from instruction selection. The valid-input domain must match.",
                    "inference",
                )
            if row.get("support_functions"):
                note(
                    "pattern_callees",
                    "Fixture callbacks/out-parameter callees are included only in the language that uses them.",
                    {
                        compiler: {
                            "helpers": list(row[compiler].get("fixture_helpers", {})),
                            "bytes": row[compiler].get("fixture_helper_bytes", 0),
                        }
                        for compiler in ["sangoku", "sdcc"]
                    },
                )
        if row["kind"] == "string":
            note("source_semantics", row["semantic_note"], {"style": row["style"]})
            if row["operation"] in {"strlen", "strcmp"}:
                matched = by_id.get(row["id"] + "_loop")
                if matched and r["status"] == matched["sangoku"]["status"] == "ok":
                    note(
                        "abstraction_cost",
                        "The matched-loop probe provides a control for the Rust library abstraction.",
                        {
                            "library_case": row["id"],
                            "library_body_bytes": r["function_bytes"],
                            "loop_case": matched["id"],
                            "loop_body_bytes": matched["sangoku"]["function_bytes"],
                        },
                        "Inspect CStr and slice construction for materialized intermediates. strcmp also changes from a fused scan/compare to CStr scans followed by comparison.",
                        "inference",
                    )
            if row.get("fixed_length") is not None:
                base = "strings_" + row["base_operation"]
                variable = by_id.get(base)
                if variable:
                    note(
                        "fixed_length",
                        "The length is known at compile time.",
                        {
                            "variable_case": base,
                            "function_helpers": {
                                compiler: row[compiler].get("external_transfers")
                                for compiler in ["sangoku", "sdcc"]
                            },
                        },
                        "Check whether a small inline copy/fill/compare beats passing a constant count to a general routine; measure cycles separately.",
                        "inference",
                    )
        if not notes:
            note("scope", "No direct comparison is available.")
        row["analysis"] = {
            "summary": summary,
            "metric": "static function-body bytes; reachable dependency size reported separately when available",
            "notes": notes,
            "timing": "not measured",
        }
