#!/usr/bin/env python3
"""Build an audit for the HI2022 T=8 coarse tolerance-repair attempt."""

from __future__ import annotations

import csv
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
V048_RESULTS = ROOT / "v048_cross_paper_same_test_benchmarks" / "results"
ORIGINAL_DIR = V048_RESULTS / "hi2022_T8_coarse_model_shards"
REPAIR_DIR = V048_RESULTS / "hi2022_T8_tolerance_repair_shards"
REPAIR_DIR_TOL1E6 = V048_RESULTS / "hi2022_T8_tol1e6_shards"
OUT_JSON = PAPER / "HI2022_T8_TOLERANCE_REPAIR_AUDIT.json"
OUT_MD = PAPER / "HI2022_T8_TOLERANCE_REPAIR_AUDIT.md"

HI2022_PUBLIC_FORMS = ["rA", "rA_half"]
HI2022_PUBLIC_MODELS = ["single_pendulum", "double_pendulum", "four_link", "slider_crank"]
HI2022_PUBLIC_STEP_SIZES = [1e-4, 2e-4, 4e-4, 1e-3, 2e-3, 4e-3, 1e-2, 2e-2, 4e-2]
HI2022_PUBLIC_T_END = 8.0
HI2022_PUBLIC_REFERENCE_H = 1e-3
HI2022_PUBLIC_TOLERANCE_BASE = 1.0e-10
REPAIR_STEP_SIZES = [0.1, 0.05, 0.025]
REPAIR_REFERENCE_H = 0.0125


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_rows(directory: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    if not directory.exists():
        return rows
    for path in sorted(directory.glob("hi2022_*_rows.csv")):
        rows.extend(read_csv(path))
    return rows


def as_float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def failure_family(status: str) -> str:
    if status == "ok":
        return "ok"
    lowered = status.lower()
    if "newton-raphson not converging" in lowered:
        return "newton_not_converging"
    if "nan" in lowered or "singular" in lowered or "infs" in lowered:
        return "nan_or_singular_matrix"
    if status.startswith("failed:"):
        return "other_failure"
    return "non_ok"


def attach_source(rows: list[dict[str, str]], source_label: str, tolerance_base: float) -> list[dict[str, str]]:
    return [{**row, "_source_label": source_label, "_tolerance_base": f"{tolerance_base:.16e}"} for row in rows]


def group_key(row: dict[str, str]) -> tuple[str, str, float]:
    h_value = as_float(row.get("h"))
    if h_value is None:
        h_value = float("nan")
    return str(row.get("form", "")), str(row.get("model", "")), h_value


def group_name_from_key(key: tuple[str, str, float]) -> str:
    return f"{key[0]}:{key[1]}"


def compact_row(row: dict[str, str]) -> dict[str, Any]:
    return {
        "form": row.get("form"),
        "model": row.get("model"),
        "h": as_float(row.get("h")),
        "status": row.get("status"),
        "failure_family": failure_family(row.get("status", "")),
        "source_label": row.get("_source_label", "unknown"),
        "tolerance_base": as_float(row.get("_tolerance_base")),
        "tolerance": as_float(row.get("tolerance")),
        "reference_h": as_float(row.get("reference_h")),
        "t_end": as_float(row.get("t_end")),
        "max_iterations": as_float(row.get("max_iterations")),
    }


def summarize(rows: list[dict[str, str]]) -> dict[str, Any]:
    groups: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        groups.setdefault(f"{row.get('form')}:{row.get('model')}", []).append(row)

    group_summary: dict[str, dict[str, Any]] = {}
    for key, group_rows in sorted(groups.items()):
        ok_rows = [row for row in group_rows if row.get("status") == "ok"]
        group_summary[key] = {
            "row_count": len(group_rows),
            "ok_row_count": len(ok_rows),
            "failed_row_count": len(group_rows) - len(ok_rows),
            "complete_three_step_group": len(ok_rows) == 3,
            "h_values": sorted(value for row in group_rows if (value := as_float(row.get("h"))) is not None),
            "status_values": sorted({row.get("status", "") for row in group_rows}),
            "failure_families": dict(Counter(failure_family(row.get("status", "")) for row in group_rows)),
            "max_iterations": max(
                (as_float(row.get("max_iterations")) or 0.0 for row in ok_rows),
                default=0.0,
            ),
        }

    return {
        "row_count": len(rows),
        "ok_row_count": sum(1 for row in rows if row.get("status") == "ok"),
        "failed_row_count": sum(1 for row in rows if row.get("status") != "ok"),
        "group_count": len(group_summary),
        "complete_form_model_groups": sum(1 for group in group_summary.values() if group["complete_three_step_group"]),
        "groups": group_summary,
        "t_end_values": sorted(value for row in rows if (value := as_float(row.get("t_end"))) is not None),
        "h_values": sorted({value for row in rows if (value := as_float(row.get("h"))) is not None}),
        "reference_h_values": sorted(
            {value for row in rows if (value := as_float(row.get("reference_h"))) is not None}
        ),
        "tolerance_values": sorted(
            {value for row in rows if (value := as_float(row.get("tolerance"))) is not None}
        ),
        "failure_families": dict(Counter(failure_family(row.get("status", "")) for row in rows)),
    }


def combined_best(original_rows: list[dict[str, str]], repair_rows: list[dict[str, str]]) -> dict[str, Any]:
    rows_by_key: dict[tuple[str, str, float], dict[str, str]] = {}
    attempts_by_key: dict[tuple[str, str, float], list[dict[str, Any]]] = {}
    for row in original_rows:
        key = group_key(row)
        rows_by_key[key] = row
        attempts_by_key.setdefault(key, []).append(compact_row(row))
    recovered: list[dict[str, str]] = []
    for row in repair_rows:
        key = group_key(row)
        attempts_by_key.setdefault(key, []).append(compact_row(row))
        original = rows_by_key.get(key)
        if original is not None and original.get("status") != "ok" and row.get("status") == "ok":
            recovered.append(row)
            rows_by_key[key] = row
    summary = summarize(list(rows_by_key.values()))
    summary["recovered_row_count"] = len(recovered)
    summary["recovered_rows"] = [
        {
            "form": row.get("form"),
            "model": row.get("model"),
            "h": as_float(row.get("h")),
            "status": row.get("status"),
            "max_iterations": as_float(row.get("max_iterations")),
            "source_label": row.get("_source_label", "unknown"),
            "tolerance_base": as_float(row.get("_tolerance_base")),
        }
        for row in recovered
    ]
    row_details = []
    for key, row in sorted(rows_by_key.items(), key=lambda item: (item[0][0], item[0][1], item[0][2])):
        detail = compact_row(row)
        detail["attempts"] = attempts_by_key.get(key, [])
        row_details.append(detail)
    summary["row_details"] = row_details
    summary["remaining_incomplete_groups"] = build_remaining_incomplete_groups(summary["groups"], row_details)
    return summary


def build_remaining_incomplete_groups(
    groups: dict[str, dict[str, Any]], row_details: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    rows_by_group: dict[str, list[dict[str, Any]]] = {}
    for row in row_details:
        rows_by_group.setdefault(f"{row['form']}:{row['model']}", []).append(row)

    incomplete = []
    for group_name, group in sorted(groups.items()):
        if group["complete_three_step_group"]:
            continue
        failed_rows = [
            {
                "h": row["h"],
                "best_status": row["status"],
                "failure_family": row["failure_family"],
                "best_source_label": row["source_label"],
                "attempts": row["attempts"],
            }
            for row in rows_by_group.get(group_name, [])
            if row["status"] != "ok"
        ]
        incomplete.append(
            {
                "group": group_name,
                "row_count": group["row_count"],
                "ok_row_count": group["ok_row_count"],
                "failed_row_count": group["failed_row_count"],
                "failure_families": group["failure_families"],
                "failed_rows": failed_rows,
            }
        )
    return incomplete


def public_grid_contract() -> dict[str, Any]:
    return {
        "forms": HI2022_PUBLIC_FORMS,
        "models": HI2022_PUBLIC_MODELS,
        "t_end": HI2022_PUBLIC_T_END,
        "step_sizes": HI2022_PUBLIC_STEP_SIZES,
        "reference_h": HI2022_PUBLIC_REFERENCE_H,
        "tolerance_base": HI2022_PUBLIC_TOLERANCE_BASE,
        "required_form_model_groups": len(HI2022_PUBLIC_FORMS) * len(HI2022_PUBLIC_MODELS),
        "required_rows": len(HI2022_PUBLIC_FORMS) * len(HI2022_PUBLIC_MODELS) * len(HI2022_PUBLIC_STEP_SIZES),
        "promotion_requires": [
            "all public form/model/step rows complete with finite error and work metrics",
            "row audit binds reference_h, tolerance_base, output norm, runtime, and Newton diagnostics",
            "no B4/B7 external-superiority row may be promoted from coarse repair-only diagnostics",
        ],
    }


def repair_vs_public_contract() -> dict[str, Any]:
    return {
        "current_repair_step_sizes": REPAIR_STEP_SIZES,
        "current_repair_reference_h": REPAIR_REFERENCE_H,
        "current_repair_required_rows": len(HI2022_PUBLIC_FORMS) * len(HI2022_PUBLIC_MODELS) * len(REPAIR_STEP_SIZES),
        "matches_public_step_grid": False,
        "matches_public_reference_h": False,
        "diagnostic_only": True,
    }


def post_b4_decision() -> dict[str, Any]:
    return {
        "decision": "demote_from_b4_b7_source_policy_figures",
        "demote_from_b4_b7_source_policy_figures": True,
        "rows_promoted": 0,
        "targeted_repair_required_before_promotion": True,
        "do_not_rerun_guarded_driver_blindly": True,
    }


def targeted_repair_acceptance_contract() -> dict[str, Any]:
    return {
        "coarse_trio_diagnostic_repair_requires": [
            "rA_half:double_pendulum must complete h=0.1, 0.05, and 0.025 with finite metrics",
            "remaining incomplete groups must have explicit row-level success or failure records",
            "coarse-trio success remains diagnostic and is not full public-grid source-policy closure",
        ],
        "full_public_grid_promotion_requires": [
            "all 72 public-grid rows complete for both forms, all four models, and nine public step sizes",
            "T=8.0, reference_h=0.001, tolerance_base=1e-10, output norm, runtime, and Newton diagnostics are bound",
            "B4 row-closure ledger records promotion evidence for each external comparison row",
        ],
    }


def format_float_list(values: list[float]) -> str:
    return ", ".join(f"{value:g}" for value in values)


def main() -> None:
    original_rows = read_rows(ORIGINAL_DIR)
    repair_rows = read_rows(REPAIR_DIR)
    repair_rows_tol1e6 = read_rows(REPAIR_DIR_TOL1E6)
    original_rows_labeled = attach_source(original_rows, "original_t8_coarse_1e-10", 1.0e-10)
    repair_rows_labeled = attach_source(repair_rows, "repair_t8_tol_1e-7", 1.0e-7)
    repair_rows_tol1e6_labeled = attach_source(repair_rows_tol1e6, "repair_t8_tol_1e-6", 1.0e-6)
    all_repair_rows = [*repair_rows_labeled, *repair_rows_tol1e6_labeled]
    original = summarize(original_rows)
    repair = summarize(repair_rows)
    repair_tol1e6 = summarize(repair_rows_tol1e6)
    best = combined_best(original_rows_labeled, all_repair_rows)
    output = {
        "schema": "hi2022-t8-tolerance-repair-audit-v1",
        "status": "tolerance_repair_attempt_recorded_not_source_policy_closure",
        "submission_ready": False,
        "source_suite": "hi2022_fang_kissel_zhang_negrut",
        "suite_id": "hi2022_half_implicit",
        "repair_artifact_dir": "../v048_cross_paper_same_test_benchmarks/results/hi2022_T8_tolerance_repair_shards",
        "repair_artifact_dirs": [
            "../v048_cross_paper_same_test_benchmarks/results/hi2022_T8_tolerance_repair_shards",
            "../v048_cross_paper_same_test_benchmarks/results/hi2022_T8_tol1e6_shards",
        ],
        "original_artifact_dir": "../v048_cross_paper_same_test_benchmarks/results/hi2022_T8_coarse_model_shards",
        "repair_policy": {
            "t_end": 8.0,
            "step_sizes": REPAIR_STEP_SIZES,
            "reference_h": REPAIR_REFERENCE_H,
            "original_tolerance_base": 1.0e-10,
            "repair_tolerance_base": 1.0e-7,
            "additional_repair_tolerance_bases": [1.0e-6],
            "contains_source_policy_1e_4_rows": False,
            "default_1e_4_required": False,
            "run_v047_invoked": False,
            "v048_runner_invoked_for_repair": True,
        },
        "original_t8_coarse": original,
        "repair_attempt": repair,
        "repair_attempts": [
            {"tolerance_base": 1.0e-7, "artifact_dir": str(REPAIR_DIR.relative_to(PAPER.parent)), "summary": repair},
            {
                "tolerance_base": 1.0e-6,
                "artifact_dir": str(REPAIR_DIR_TOL1E6.relative_to(PAPER.parent)),
                "summary": repair_tol1e6,
            },
        ],
        "latest_repair_attempt": repair_tol1e6,
        "combined_best": best,
        "full_public_grid_contract": public_grid_contract(),
        "current_repair_vs_public_contract": repair_vs_public_contract(),
        "post_b4_decision": post_b4_decision(),
        "targeted_repair_acceptance_contract": targeted_repair_acceptance_contract(),
        "claim_boundary": {
            "source_policy_reproduction_closed": False,
            "full_T8_policy_completed": False,
            "external_superiority_claim_allowed": False,
            "accepted_source_policy_dynamic_order_examples": 0,
        },
        "interpretation": (
            "Relaxing the HI2022 T=8 coarse tolerance base from 1e-10 to 1e-7 recovers one "
            "rA_half double-pendulum row. A second non-heavy 1e-6 sweep was also run on the "
            "failed T=8 models, but the combined best evidence still completes only four of "
            "eight three-step form/model groups. The remaining failures are Newton "
            "nonconvergence and NaN/singular-matrix failures, so the repair attempts do not "
            "close HI2022 source policy."
        ),
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# HI2022 T=8 Tolerance-Repair Audit",
        "",
        "Status: **tolerance repair recorded; source-policy closure still open**.",
        "",
        f"- Original T=8 coarse rows ok: `{original['ok_row_count']}/{original['row_count']}`.",
        f"- Original complete form/model groups: `{original['complete_form_model_groups']}/{original['group_count']}`.",
        f"- Repair rows ok: `{repair['ok_row_count']}/{repair['row_count']}`.",
        f"- Repair complete form/model groups: `{repair['complete_form_model_groups']}/{repair['group_count']}`.",
        f"- Second repair rows ok: `{repair_tol1e6['ok_row_count']}/{repair_tol1e6['row_count']}`.",
        f"- Second repair complete form/model groups: `{repair_tol1e6['complete_form_model_groups']}/{repair_tol1e6['group_count']}`.",
        f"- Combined best rows ok: `{best['ok_row_count']}/{best['row_count']}`.",
        f"- Combined best complete form/model groups: `{best['complete_form_model_groups']}/{best['group_count']}`.",
        f"- Recovered rows: `{best['recovered_row_count']}`.",
        f"- Remaining incomplete groups: `{len(best['remaining_incomplete_groups'])}`.",
        "- Repair tolerance base: `1e-07`.",
        "- Additional repair tolerance base: `1e-06`.",
        "- Contains source-policy 1e-4 rows: `False`.",
        "- Source-policy reproduction closed: `False`.",
        "- Full T=8 policy completed: `False`.",
        "- External superiority claim allowed: `False`.",
        "",
        "## Recovered Rows",
        "",
        "| form | model | h | status | max iterations |",
        "|---|---|---:|---|---:|",
    ]
    for row in best["recovered_rows"]:
        lines.append(
            f"| `{row['form']}` | `{row['model']}` | `{row['h']}` | `{row['status']}` | `{row['max_iterations']}` |"
        )
    lines.extend(
        [
            "",
            "## Remaining Incomplete Groups",
            "",
            "| group | ok rows | failed rows | failure families | failed h/status |",
            "|---|---:|---:|---|---|",
        ]
    )
    for group in best["remaining_incomplete_groups"]:
        failed_statuses = "; ".join(
            f"h={row['h']}: {row['failure_family']} ({row['best_status']})" for row in group["failed_rows"]
        )
        lines.append(
            f"| `{group['group']}` | `{group['ok_row_count']}/{group['row_count']}` | "
            f"`{group['failed_row_count']}` | `{group['failure_families']}` | `{failed_statuses}` |"
        )
    lines.extend(
        [
            "",
            "## Full Public-Grid Contract",
            "",
            f"- Full public-grid required rows: `{public_grid_contract()['required_rows']}`.",
            f"- Full public-grid required form/model groups: `{public_grid_contract()['required_form_model_groups']}`.",
            f"- Public step sizes: `{format_float_list(HI2022_PUBLIC_STEP_SIZES)}`.",
            f"- Public reference h: `{HI2022_PUBLIC_REFERENCE_H:g}`.",
            f"- Public tolerance base: `{HI2022_PUBLIC_TOLERANCE_BASE:g}`.",
            f"- Current repair step sizes: `{format_float_list(REPAIR_STEP_SIZES)}`.",
            f"- Current repair reference h: `{REPAIR_REFERENCE_H:g}`.",
            "- Current repair matches public step grid: `False`.",
            "- Current repair matches public reference h: `False`.",
            "- Post-B4 decision: `demote_from_b4_b7_source_policy_figures`.",
            "- Targeted repair required before promotion: `True`.",
            "- Do not rerun guarded driver blindly: `True`.",
            "- Rows promoted: `0`.",
            "",
            "## Targeted Repair Acceptance Contract",
            "",
            "- Coarse-trio repair must first complete `rA_half:double_pendulum` at h=`0.1`, `0.05`, and `0.025` with finite error and work metrics.",
            "- Coarse-trio success remains diagnostic and is not full public-grid source-policy closure.",
            "- Full promotion requires all `72` public-grid rows with T=`8.0`, reference h=`0.001`, tolerance base=`1e-10`, output norm, runtime, and Newton diagnostics bound.",
            "",
            "## Failure Families",
            "",
            f"- Original: `{original['failure_families']}`.",
            f"- Repair: `{repair['failure_families']}`.",
            f"- Second repair: `{repair_tol1e6['failure_families']}`.",
            "",
            "Interpretation: relaxing the tolerance records a useful negative result. The first repair recovers one row, and the second non-heavy 1e-6 sweep does not increase the combined-best closure beyond 19/24 rows and 4/8 groups. The source-policy claim remains open.",
            "",
            "Validator: `validate_hi2022_t8_tolerance_repair_audit.py`.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("hi2022_t8_tolerance_repair_audit=written")
    print(f"combined_best_rows={best['ok_row_count']}/{best['row_count']}")
    print(f"combined_best_complete_groups={best['complete_form_model_groups']}/{best['group_count']}")
    print("source_policy_reproduction_closed=False")


if __name__ == "__main__":
    main()
