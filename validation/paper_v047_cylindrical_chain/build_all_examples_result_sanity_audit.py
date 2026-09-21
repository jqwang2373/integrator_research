#!/usr/bin/env python3
"""Build an all-example sanity audit for the paper-facing result matrix."""

from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
V048_SUMMARY = ROOT.parent / "numerics" / "v048_cross_paper_same_test_benchmarks" / "results" / "summary_v048.json"
OUT_JSON = PAPER / "ALL_EXAMPLES_RESULT_SANITY_AUDIT.json"
OUT_MD = PAPER / "ALL_EXAMPLES_RESULT_SANITY_AUDIT.md"

EXAMPLES = ("single_pendulum", "double_pendulum", "four_link", "slider_crank")
LOCAL_METHOD = "local_Gauss6_FullVA"
LOCAL_ORDER_MIN = 5.5
LOCAL_ERROR_MAX = 1.0e-8
WARNING_ERROR = 1.0e-1
VERY_LARGE_ERROR = 1.0
LOW_ORDER = 0.5
FLOOR_ORDER = 0.1


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def as_float(value: object) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return float("nan")
    return out if math.isfinite(out) else float("nan")


def fmt(value: object) -> str:
    number = as_float(value)
    if not math.isfinite(number):
        return "nan"
    if abs(number) >= 1000.0 or (0.0 < abs(number) < 1.0e-2):
        return f"{number:.3e}"
    return f"{number:.3f}"


def row_flags(method: str, order: float, error: float) -> list[str]:
    if method == LOCAL_METHOD:
        return []
    flags: list[str] = []
    if not math.isfinite(order):
        flags.append("nonfinite_observed_order")
    elif order < 0.0:
        flags.append("negative_observed_order")
    elif abs(order) < FLOOR_ORDER:
        flags.append("floor_limited_or_zero_observed_order")
    elif order < LOW_ORDER:
        flags.append("low_observed_order_lt_0p5")
    if not math.isfinite(error):
        flags.append("nonfinite_finest_velocity_error")
    elif error > VERY_LARGE_ERROR:
        flags.append("very_large_finest_velocity_error_gt_1")
    elif error > WARNING_ERROR:
        flags.append("large_finest_velocity_error_gt_0p1")
    return flags


def severity(flags: list[str]) -> str:
    critical = {
        "nonfinite_observed_order",
        "negative_observed_order",
        "floor_limited_or_zero_observed_order",
        "nonfinite_finest_velocity_error",
        "very_large_finest_velocity_error_gt_1",
    }
    if any(flag in critical for flag in flags):
        return "critical_recheck"
    if flags:
        return "warning_recheck"
    return "none"


def compact_flags(flags: list[str]) -> str:
    return ", ".join(flags) if flags else "none"


def main() -> None:
    result_pack = read_json(PAPER / "PAPER_RESULT_PACK.json")
    v048_summary = read_json(V048_SUMMARY) if V048_SUMMARY.exists() else {}
    matrix = result_pack.get("common_reference", {}).get("all_method_matrix", [])
    if not isinstance(matrix, list):
        raise ValueError("PAPER_RESULT_PACK common_reference.all_method_matrix is not a list")

    rows: list[dict[str, object]] = []
    local_rows: list[dict[str, object]] = []
    flagged_nonlocal_rows: list[dict[str, object]] = []
    examples_seen: set[str] = set()
    methods_seen: set[str] = set()

    for method_entry in matrix:
        if not isinstance(method_entry, dict):
            continue
        method = str(method_entry.get("method", ""))
        examples = method_entry.get("examples", {})
        if not isinstance(examples, dict):
            continue
        methods_seen.add(method)
        for example in EXAMPLES:
            cell = examples.get(example)
            if not isinstance(cell, dict):
                continue
            examples_seen.add(example)
            order = as_float(cell.get("velocity_order"))
            error = as_float(cell.get("finest_velocity_error"))
            flags = row_flags(method, order, error)
            role = "local_method" if method == LOCAL_METHOD else "external_or_prior_method"
            disposition = "accepted_local_empirical_order_row"
            if method != LOCAL_METHOD:
                disposition = (
                    "needs_source_policy_recheck_before_external_claim"
                    if flags
                    else "fixed_grid_diagnostic_only"
                )
            row = {
                "method": method,
                "example": example,
                "role": role,
                "velocity_order": order,
                "finest_velocity_error": error,
                "flags": flags,
                "severity": severity(flags),
                "disposition": disposition,
            }
            rows.append(row)
            if method == LOCAL_METHOD:
                local_rows.append(row)
            elif flags:
                flagged_nonlocal_rows.append(row)

    local_passed_rows = [
        row
        for row in local_rows
        if as_float(row.get("velocity_order")) >= LOCAL_ORDER_MIN
        and as_float(row.get("finest_velocity_error")) <= LOCAL_ERROR_MAX
    ]
    local_orders = [as_float(row.get("velocity_order")) for row in local_rows]
    local_errors = [as_float(row.get("finest_velocity_error")) for row in local_rows]
    flagged_by_example = Counter(str(row["example"]) for row in flagged_nonlocal_rows)
    flagged_by_method = Counter(str(row["method"]) for row in flagged_nonlocal_rows)
    flagged_row_keys = sorted(f"{row['method']}/{row['example']}" for row in flagged_nonlocal_rows)
    severity_counts = Counter(str(row["severity"]) for row in flagged_nonlocal_rows)
    all_flagged_rows_quarantined = all(
        row["disposition"] == "needs_source_policy_recheck_before_external_claim"
        for row in flagged_nonlocal_rows
    )

    result = {
        "schema": "all-examples-result-sanity-audit-v1",
        "source": "PAPER_RESULT_PACK.common_reference.all_method_matrix",
        "all_four_examples_audited": set(examples_seen) == set(EXAMPLES),
        "submission_ready": False,
        "coverage": {
            "examples": list(EXAMPLES),
            "example_count": len(examples_seen),
            "method_count": len(methods_seen),
            "cell_count": len(rows),
            "expected_cell_count": len(EXAMPLES) * len(methods_seen),
            "nonlocal_cell_count": len([row for row in rows if row["method"] != LOCAL_METHOD]),
        },
        "local_method_gate": {
            "method": LOCAL_METHOD,
            "order_min_threshold": LOCAL_ORDER_MIN,
            "finest_velocity_error_max_threshold": LOCAL_ERROR_MAX,
            "passed": len(local_passed_rows) == len(EXAMPLES),
            "passed_rows": len(local_passed_rows),
            "expected_rows": len(EXAMPLES),
            "min_velocity_order": min(local_orders) if local_orders else float("nan"),
            "max_finest_velocity_error": max(local_errors) if local_errors else float("nan"),
            "rows": local_rows,
        },
        "baseline_sanity": {
            "flagged_nonlocal_count": len(flagged_nonlocal_rows),
            "flagged_examples": sorted(flagged_by_example),
            "flagged_by_example": dict(sorted(flagged_by_example.items())),
            "flagged_by_method": dict(sorted(flagged_by_method.items())),
            "flagged_row_keys": flagged_row_keys,
            "severity_counts": dict(sorted(severity_counts.items())),
            "all_flagged_rows_quarantined": all_flagged_rows_quarantined,
            "source_policy_recheck_required": bool(flagged_nonlocal_rows),
            "flagged_rows": flagged_nonlocal_rows,
        },
        "source_policy_boundary": {
            "source_policy_reproduction": result_pack.get("common_reference", {}).get("source_policy_reproduction"),
            "public_code_fixed_grid_replay": result_pack.get("common_reference", {}).get("public_code_fixed_grid_replay"),
            "same_test_campaign_status": v048_summary.get("same_test_campaign_status"),
            "external_superiority_claim": result_pack.get("performance_matrix", {}).get("external_superiority_claim"),
        },
        "paper_claim_boundary": {
            "external_superiority_allowed": False,
            "baseline_rows_usable_for_external_superiority": False,
            "exact_flagged_set_required": True,
            "flagged_rows_enter_paper_claims": False,
            "allowed_claim": (
                "All four examples are audited on the fixed-grid common-reference matrix. "
                "The local Gauss6/FullVA row has strong empirical order/error evidence. "
                "Flagged nonlocal rows require source-policy recheck before any external-superiority claim."
            ),
        },
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# All Examples Result Sanity Audit",
        "",
        "Status: **all four examples audited; not submission-ready external superiority evidence**.",
        "",
        f"- Coverage: `{len(rows)}/{len(EXAMPLES) * len(methods_seen)}` method-example cells.",
        f"- Examples audited: `{', '.join(EXAMPLES)}`.",
        f"- Local empirical gate: `{len(local_passed_rows)}/{len(EXAMPLES)}` rows pass "
        f"`order >= {LOCAL_ORDER_MIN}` and `finest velocity error <= {LOCAL_ERROR_MAX:.1e}`.",
        f"- Flagged nonlocal rows needing source-policy recheck: `{len(flagged_nonlocal_rows)}`.",
        f"- Flagged examples: `{', '.join(sorted(flagged_by_example))}`.",
        f"- All flagged rows quarantined from external-superiority claims: `{all_flagged_rows_quarantined}`.",
        f"- External superiority allowed from this audit: `{result['paper_claim_boundary']['external_superiority_allowed']}`.",
        "",
        "## Local Method Rows",
        "",
        "| example | observed velocity order | finest velocity error | disposition |",
        "|---|---:|---:|---|",
    ]
    for row in local_rows:
        lines.append(
            "| "
            f"`{row['example']}` | `{fmt(row['velocity_order'])}` | "
            f"`{fmt(row['finest_velocity_error'])}` | `{row['disposition']}` |"
        )

    lines.extend(
        [
            "",
            "## Flagged Nonlocal Rows",
            "",
            "These rows are checked across all examples. A flag is not automatically a method failure; it means the row cannot support a source-policy external-superiority claim until the corresponding source runner, coordinates, output norm, and reference policy are rechecked.",
            "",
            "| method | example | observed velocity order | finest velocity error | severity | flags |",
            "|---|---|---:|---:|---|---|",
        ]
    )
    for row in flagged_nonlocal_rows:
        lines.append(
            "| "
            f"`{row['method']}` | `{row['example']}` | `{fmt(row['velocity_order'])}` | "
            f"`{fmt(row['finest_velocity_error'])}` | `{row['severity']}` | "
            f"`{compact_flags(row['flags'])}` |"
        )

    lines.extend(
        [
            "",
            "## Per-Example Flag Counts",
            "",
            "| example | flagged nonlocal rows |",
            "|---|---:|",
        ]
    )
    for example in EXAMPLES:
        lines.append(f"| `{example}` | `{flagged_by_example.get(example, 0)}` |")

    lines.extend(
        [
            "",
            "## Exact Recheck Set",
            "",
            "The validator locks this exact method/example set so a repaired single-pendulum row cannot mask unresolved rows in the other examples.",
            "",
            "| method/example row |",
            "|---|",
        ]
    )
    for row_key in flagged_row_keys:
        lines.append(f"| `{row_key}` |")

    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This audit checks every example, not only `single_pendulum`.",
            "- Every flagged row is quarantined from external-superiority claims until source-policy reproduction is closed.",
            "- It supports the local fixed-grid common-reference order/error statement.",
            "- It does not close B4 or any source-policy execution rows; B2 closure, if used, must come from Route B claim demotion.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("all_examples_result_sanity_audit=written")
    print(f"cells={len(rows)}/{len(EXAMPLES) * len(methods_seen)}")
    print(f"local_rows_passed={len(local_passed_rows)}/{len(EXAMPLES)}")
    print(f"flagged_nonlocal_rows={len(flagged_nonlocal_rows)}")


if __name__ == "__main__":
    main()
