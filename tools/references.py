from collections import Counter


REFERENCE_COMPILERS = ("sdcc", "llvm_z80")


def body_bytes(result):
    if result.get("status") != "ok":
        return None
    return result["function_bytes"] + result.get("outlined_helper_bytes", 0)


def dependency_bytes(result):
    if result.get("status") != "ok":
        return None
    library = result.get("library", {})
    if library.get("status") == "ok":
        return library["total_bytes"]
    return None


def choose_reference(row, metric):
    measure = body_bytes if metric == "body" else dependency_bytes
    candidates = {}
    excluded = {}
    for compiler in REFERENCE_COMPILERS:
        result = row.get(compiler, {})
        value = measure(result)
        if value is None:
            excluded[compiler] = result.get("diagnostic") or (
                result.get("status", "not run")
                if result.get("status") != "ok"
                else result.get("library", {}).get(
                    "diagnostic", "complete dependency measurement unavailable"
                )
            )
        else:
            candidates[compiler] = value
    if not candidates:
        return {"status": "unavailable", "excluded": excluded}
    best = min(candidates.values())
    current = measure(row.get("sangoku", {}))
    return {
        "status": "ok",
        "bytes": best,
        "compilers": [name for name, value in candidates.items() if value == best],
        "candidates": candidates,
        "excluded": excluded,
        "sangoku_bytes": current,
        "sangoku_delta": current - best if current is not None else None,
        "external_helpers_excluded": metric == "body",
    }


def annotate_references(rows):
    for row in rows:
        row["reference"] = {
            metric: choose_reference(row, metric)
            for metric in ("body", "with_dependencies")
        }


def reference_summary(rows):
    return {
        metric: dict(
            Counter(
                "+".join(row.get("reference", {}).get(metric, {}).get("compilers", []))
                or "unavailable"
                for row in rows
            )
        )
        for metric in ("body", "with_dependencies")
    }
