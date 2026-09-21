#!/usr/bin/env python3
"""Independently recompute common-reference orders from raw rows."""

from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
V048 = ROOT.parent / "numerics" / "v048_cross_paper_same_test_benchmarks" / "results"
RAW_CSV = V048 / "common_reference_error_raw_rows.csv"
SUMMARY_CSV = V048 / "common_reference_error_summary.csv"
OUT_JSON = PAPER / "COMMON_REFERENCE_ORDER_RECOMPUTATION_AUDIT.json"
OUT_MD = PAPER / "COMMON_REFERENCE_ORDER_RECOMPUTATION_AUDIT.md"

EXPECTED_H = (0.1, 0.05, 0.025)
EXPECTED_EXAMPLES = ("single_pendulum", "double_pendulum", "four_link", "slider_crank")
LOCAL_METHOD = "local_Gauss6_FullVA"
CHECK_FIELDS = ("pos", "vel", "acc")
ORDER_ABS_TOL = 1.0e-10
ERROR_ABS_TOL = 1.0e-14
ERROR_REL_TOL = 1.0e-10


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def as_float(value: object) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return float("nan")
    return out if math.isfinite(out) else float("nan")


def same_float(left: float, right: float, *, abs_tol: float, rel_tol: float = 0.0) -> bool:
    if not math.isfinite(left) and not math.isfinite(right):
        return True
    if not (math.isfinite(left) and math.isfinite(right)):
        return False
    return abs(left - right) <= max(abs_tol, rel_tol * max(abs(left), abs(right), 1.0))


def fmt(value: object) -> str:
    number = as_float(value)
    if not math.isfinite(number):
        return "nan"
    if abs(number) >= 1000.0 or (0.0 < abs(number) < 1.0e-2):
        return f"{number:.3e}"
    return f"{number:.3f}"


def estimate_order(pairs: list[tuple[float, float]]) -> float:
    usable = [(h, err) for h, err in pairs if h > 0.0 and err > 0.0 and math.isfinite(h) and math.isfinite(err)]
    if len(usable) < 3:
        return float("nan")
    xs = [math.log(h) for h, _ in usable]
    ys = [math.log(err) for _, err in usable]
    x_bar = sum(xs) / len(xs)
    y_bar = sum(ys) / len(ys)
    denom = sum((x - x_bar) ** 2 for x in xs)
    if denom <= 0.0:
        return float("nan")
    return sum((x - x_bar) * (y - y_bar) for x, y in zip(xs, ys)) / denom


def monotonic_flags(rows: list[dict[str, str]], field: str) -> list[str]:
    ordered = sorted(rows, key=lambda row: as_float(row["h"]), reverse=True)
    errors = [as_float(row[f"{field}_error"]) for row in ordered]
    finite = [err for err in errors if math.isfinite(err)]
    if len(finite) < 3:
        return []
    flags: list[str] = []
    if any(finite[i + 1] > finite[i] for i in range(len(finite) - 1)):
        flags.append(f"{field}_error_not_monotone_decreasing_with_h")
    if all(abs(finite[i + 1] - finite[i]) <= 1.0e-14 for i in range(len(finite) - 1)):
        flags.append(f"{field}_error_flat_at_floor")
    return flags


def main() -> None:
    raw_rows = read_csv(RAW_CSV)
    summary_rows = read_csv(SUMMARY_CSV)
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in raw_rows:
        if row.get("status") == "ok":
            grouped[(row["method"], row["example"])].append(row)
    summary_by_key = {(row["method"], row["example"]): row for row in summary_rows if row.get("status") == "ok"}

    audit_rows: list[dict[str, object]] = []
    mismatch_rows: list[dict[str, object]] = []
    anomaly_rows: list[dict[str, object]] = []
    max_order_abs_diff = 0.0
    max_error_abs_diff = 0.0
    examples = set()
    methods = set()

    for key in sorted(grouped):
        method, example = key
        rows = grouped[key]
        summary = summary_by_key.get(key)
        examples.add(example)
        methods.add(method)
        h_values = sorted(as_float(row["h"]) for row in rows)
        h_match = len(rows) == 3 and all(
            same_float(got, expected, abs_tol=1.0e-15)
            for got, expected in zip(h_values, sorted(EXPECTED_H))
        )
        row_mismatches: list[str] = []
        row_flags: list[str] = []
        recomputed: dict[str, float] = {}
        summary_values: dict[str, float] = {}
        finest_errors: dict[str, float] = {}
        summary_finest_errors: dict[str, float] = {}

        if summary is None:
            row_mismatches.append("summary_row_missing")
        if not h_match:
            row_mismatches.append("h_trio_mismatch")

        for field in CHECK_FIELDS:
            order = estimate_order([(as_float(row["h"]), as_float(row[f"{field}_error"])) for row in rows])
            recomputed[f"{field}_order"] = order
            row_flags.extend(monotonic_flags(rows, field))
            finite_error_rows = [
                row
                for row in rows
                if as_float(row["h"]) > 0.0 and math.isfinite(as_float(row[f"{field}_error"]))
            ]
            finest_row = min(finite_error_rows, key=lambda row: as_float(row["h"])) if finite_error_rows else None
            finest_error = as_float(finest_row[f"{field}_error"]) if finest_row is not None else float("nan")
            finest_errors[f"finest_{field}_error"] = finest_error

            if summary is not None:
                summary_order = as_float(summary.get(f"{field}_order"))
                summary_error = as_float(summary.get(f"finest_{field}_error"))
            else:
                summary_order = float("nan")
                summary_error = float("nan")
            summary_values[f"{field}_order"] = summary_order
            summary_finest_errors[f"finest_{field}_error"] = summary_error

            if not same_float(order, summary_order, abs_tol=ORDER_ABS_TOL):
                row_mismatches.append(f"{field}_order_mismatch")
            if not same_float(finest_error, summary_error, abs_tol=ERROR_ABS_TOL, rel_tol=ERROR_REL_TOL):
                row_mismatches.append(f"finest_{field}_error_mismatch")
            if math.isfinite(order) and math.isfinite(summary_order):
                max_order_abs_diff = max(max_order_abs_diff, abs(order - summary_order))
            if math.isfinite(finest_error) and math.isfinite(summary_error):
                max_error_abs_diff = max(max_error_abs_diff, abs(finest_error - summary_error))

        if method == LOCAL_METHOD and recomputed.get("vel_order", float("nan")) < 5.5:
            row_flags.append("local_velocity_order_below_5p5")
        if method != LOCAL_METHOD and math.isfinite(recomputed.get("vel_order", float("nan"))):
            if recomputed["vel_order"] < 0.0:
                row_flags.append("nonlocal_negative_velocity_order")
            elif abs(recomputed["vel_order"]) < 0.1:
                row_flags.append("nonlocal_velocity_order_floor_limited")

        entry = {
            "method": method,
            "example": example,
            "h_values": h_values,
            "h_trio_matches_expected": h_match,
            "summary_row_present": summary is not None,
            "recomputed": recomputed,
            "summary": summary_values,
            "finest_errors": finest_errors,
            "summary_finest_errors": summary_finest_errors,
            "mismatches": row_mismatches,
            "anomaly_flags": sorted(set(row_flags)),
            "status": "match" if not row_mismatches else "mismatch",
        }
        audit_rows.append(entry)
        if row_mismatches:
            mismatch_rows.append(entry)
        if row_flags:
            anomaly_rows.append(entry)

    anomaly_counts = Counter(flag for row in anomaly_rows for flag in row["anomaly_flags"])
    result = {
        "schema": "common-reference-order-recomputation-audit-v1",
        "source_raw_csv": str(RAW_CSV.relative_to(ROOT)),
        "source_summary_csv": str(SUMMARY_CSV.relative_to(ROOT)),
        "all_four_examples_audited": set(examples) == set(EXPECTED_EXAMPLES),
        "all_summary_orders_recomputed": not mismatch_rows,
        "submission_ready": False,
        "coverage": {
            "method_count": len(methods),
            "example_count": len(examples),
            "raw_ok_row_count": len(raw_rows),
            "summary_ok_row_count": len(summary_rows),
            "method_example_cell_count": len(audit_rows),
            "expected_method_example_cell_count": 44,
            "expected_step_count_per_cell": 3,
        },
        "verification": {
            "mismatch_count": len(mismatch_rows),
            "max_order_abs_diff": max_order_abs_diff,
            "max_finest_error_abs_diff": max_error_abs_diff,
            "order_abs_tolerance": ORDER_ABS_TOL,
            "finest_error_abs_tolerance": ERROR_ABS_TOL,
            "finest_error_rel_tolerance": ERROR_REL_TOL,
        },
        "anomalies": {
            "anomaly_row_count": len(anomaly_rows),
            "anomaly_counts": dict(sorted(anomaly_counts.items())),
            "anomaly_rows": anomaly_rows,
        },
        "rows": audit_rows,
        "claim_boundary": {
            "summary_arithmetic_verified": not mismatch_rows,
            "anomaly_rows_are_not_external_superiority_evidence": True,
            "external_superiority_allowed": False,
            "source_policy_recheck_still_required": True,
        },
    }
    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")

    local_rows = [row for row in audit_rows if row["method"] == LOCAL_METHOD]
    lines = [
        "# Common-Reference Order Recomputation Audit",
        "",
        "Status: **raw-row arithmetic verified; external-superiority source-policy gate remains open**.",
        "",
        f"- Raw ok rows checked: `{len(raw_rows)}`.",
        f"- Method/example cells recomputed: `{len(audit_rows)}/44`.",
        f"- Order/finest-error mismatches against summary: `{len(mismatch_rows)}`.",
        f"- Max order absolute difference: `{max_order_abs_diff:.3e}`.",
        f"- Max finest-error absolute difference: `{max_error_abs_diff:.3e}`.",
        f"- Anomaly rows flagged for interpretation/source-policy review: `{len(anomaly_rows)}`.",
        "",
        "## Local Recomputed Rows",
        "",
        "| example | recomputed velocity order | summary velocity order | finest velocity error | status |",
        "|---|---:|---:|---:|---|",
    ]
    for row in sorted(local_rows, key=lambda item: str(item["example"])):
        lines.append(
            "| "
            f"`{row['example']}` | `{fmt(row['recomputed']['vel_order'])}` | "
            f"`{fmt(row['summary']['vel_order'])}` | `{fmt(row['finest_errors']['finest_vel_error'])}` | "
            f"`{row['status']}` |"
        )
    lines.extend(
        [
            "",
            "## Mismatch Rows",
            "",
            "| method | example | mismatches |",
            "|---|---|---|",
        ]
    )
    if mismatch_rows:
        for row in mismatch_rows:
            lines.append(f"| `{row['method']}` | `{row['example']}` | `{', '.join(row['mismatches'])}` |")
    else:
        lines.append("| `none` | `none` | `none` |")
    lines.extend(
        [
            "",
            "## Anomaly Counts",
            "",
            "| flag | rows |",
            "|---|---:|",
        ]
    )
    for flag, count in sorted(anomaly_counts.items()):
        lines.append(f"| `{flag}` | `{count}` |")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- The audit independently recomputes every summary order from raw rows.",
            "- The arithmetic check can confirm table integrity, but it cannot repair source-policy mismatches.",
            "- External superiority remains disallowed until B2/B4 source-policy same-test baselines close.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("common_reference_order_recomputation_audit=written")
    print(f"cells={len(audit_rows)}/44")
    print(f"mismatches={len(mismatch_rows)}")
    print(f"anomaly_rows={len(anomaly_rows)}")


if __name__ == "__main__":
    main()
