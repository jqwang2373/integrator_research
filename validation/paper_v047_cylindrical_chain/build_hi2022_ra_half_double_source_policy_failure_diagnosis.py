#!/usr/bin/env python3
"""Diagnose the failed HI2022 rA_half double-pendulum source-policy shard.

This builder is intentionally read-only over the isolated T=8 candidate rows.
It records why the shard is diagnostic-only and must not be promoted to B4/B7
source-policy closure evidence.
"""

from __future__ import annotations

import csv
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
V048_RESULTS = PAPER.parent.parent / "numerics" / "v048_cross_paper_same_test_benchmarks" / "results"
STEM = "hi2022_full_t8_source_policy_candidate_rA_half_double_pendulum"
SUMMARY = V048_RESULTS / f"{STEM}_summary.json"
ROWS = V048_RESULTS / f"{STEM}_rows.csv"
OUT_JSON = PAPER / "HI2022_RA_HALF_DOUBLE_SOURCE_POLICY_FAILURE_DIAGNOSIS.json"
OUT_MD = PAPER / "HI2022_RA_HALF_DOUBLE_SOURCE_POLICY_FAILURE_DIAGNOSIS.md"
TOLERANCE_REPAIR_AUDIT = PAPER / "HI2022_T8_TOLERANCE_REPAIR_AUDIT.json"
NEWTON_FAILURE_RE = re.compile(r"Newton-Raphson not converging at t: ([0-9.eE+-]+), k: ([0-9]+)")


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def as_float(value: object) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def as_bool(value: object) -> bool:
    return str(value).strip().lower() == "true"


def finite_float(value: object) -> float:
    number = as_float(value)
    if number is None:
        return float("nan")
    return number


def fmt(value: object, digits: int = 3) -> str:
    number = as_float(value)
    if number is None:
        return "nan"
    if abs(number) >= 1000.0 or (0.0 < abs(number) < 1.0e-2):
        return f"{number:.{digits}e}"
    return f"{number:.{digits}f}"


def parse_newton_failure(message: str) -> dict[str, Any]:
    match = NEWTON_FAILURE_RE.search(message)
    if not match:
        return {
            "newton_failure_message_parsed": False,
            "newton_failure_time": None,
            "newton_failure_iteration_k": None,
        }
    return {
        "newton_failure_message_parsed": True,
        "newton_failure_time": float(match.group(1)),
        "newton_failure_iteration_k": int(match.group(2)),
    }


def compact_row(row: dict[str, str]) -> dict[str, Any]:
    failure_message = row.get("status") if row.get("status", "").startswith("failed:") else ""
    failure_info = parse_newton_failure(failure_message)
    return {
        "h": finite_float(row.get("h")),
        "tolerance": finite_float(row.get("tolerance")),
        "reference_tolerance": finite_float(row.get("reference_tolerance")),
        "status": row.get("status"),
        "failed": row.get("status", "").startswith("failed:"),
        "failure_message": failure_message,
        **failure_info,
        "pos_final_linf": finite_float(row.get("pos_final_linf")),
        "vel_final_linf": finite_float(row.get("vel_final_linf")),
        "acc_final_linf": finite_float(row.get("acc_final_linf")),
        "avg_iterations": finite_float(row.get("avg_iterations")),
        "max_iterations": finite_float(row.get("max_iterations")),
        "runtime_sec": finite_float(row.get("runtime_sec")),
        "execution_path": row.get("execution_path"),
        "source_policy_time_window_selected": as_bool(row.get("source_policy_time_window_selected")),
        "source_policy_reference_h_selected": as_bool(row.get("source_policy_reference_h_selected")),
        "source_policy_selected_coarse_h": as_bool(row.get("source_policy_selected_coarse_h")),
        "full_public_grid_selected": as_bool(row.get("full_public_grid_selected")),
        "source_policy_row_promoted": as_bool(row.get("source_policy_row_promoted")),
        "canonical_hi2022_output_untouched": as_bool(row.get("canonical_hi2022_output_untouched")),
    }


def main() -> None:
    summary = read_json(SUMMARY)
    tolerance_repair = read_json(TOLERANCE_REPAIR_AUDIT)
    raw_rows = read_csv(ROWS)
    rows = sorted((compact_row(row) for row in raw_rows), key=lambda row: float(row["h"]), reverse=True)
    status_counts = Counter(row.get("status") for row in rows)
    failed_rows = [row for row in rows if row.get("failed") is True]
    ok_rows = [row for row in rows if row.get("status") == "ok"]
    failure_messages = [row["failure_message"] for row in failed_rows]
    newton_failure_count = sum("Newton-Raphson not converging" in message for message in failure_messages)
    failure_loci = [
        {
            "h": row["h"],
            "tolerance": row["tolerance"],
            "failure_time": row["newton_failure_time"],
            "failure_iteration_k": row["newton_failure_iteration_k"],
            "message_parsed": row["newton_failure_message_parsed"],
        }
        for row in failed_rows
    ]
    selected_tolerances = sorted(
        {
            row["tolerance"]
            for row in rows
            if isinstance(row.get("tolerance"), float) and math.isfinite(row["tolerance"])
        }
    )
    reference_tolerances = sorted(
        {
            row["reference_tolerance"]
            for row in rows
            if isinstance(row.get("reference_tolerance"), float) and math.isfinite(row["reference_tolerance"])
        }
    )
    rows_complete = len(rows) == 3 and len(ok_rows) == 3
    candidate_partial = len(rows) == 3 and len(ok_rows) == 1 and len(failed_rows) == 2
    repair_policy = tolerance_repair.get("repair_policy", {})
    repair_best = tolerance_repair.get("combined_best", {})
    repair_boundary = tolerance_repair.get("claim_boundary", {})

    output: dict[str, Any] = {
        "schema": "hi2022-ra-half-double-source-policy-failure-diagnosis-v1",
        "status": "diagnosis_only_partial_newton_failure_not_promoted",
        "read_only": True,
        "heavy_numerical_run_invoked_by_this_builder": False,
        "run_v047_invoked_by_this_builder": False,
        "v048_runner_invoked_by_this_builder": False,
        "input_artifacts": {
            "candidate_summary": "../../numerics/v048_cross_paper_same_test_benchmarks/results/"
            f"{STEM}_summary.json",
            "candidate_rows": "../../numerics/v048_cross_paper_same_test_benchmarks/results/"
            f"{STEM}_rows.csv",
            "tolerance_repair_audit": "HI2022_T8_TOLERANCE_REPAIR_AUDIT.json",
        },
        "candidate_contract": {
            "summary_status": summary.get("status"),
            "execution_phase": summary.get("execution_phase"),
            "execute_requested": summary.get("execute_requested"),
            "heavy_numerical_run_invoked_by_source_candidate": summary.get("heavy_numerical_run_invoked"),
            "form": summary.get("form"),
            "model": summary.get("model"),
            "selected_t_end": summary.get("selected_t_end"),
            "selected_reference_h": summary.get("selected_reference_h"),
            "selected_step_sizes": summary.get("selected_step_sizes"),
            "source_policy_time_window_selected": summary.get("source_policy_time_window_selected"),
            "source_policy_reference_h_selected": summary.get("source_policy_reference_h_selected"),
            "selected_coarse_trio": summary.get("selected_coarse_trio"),
            "full_public_grid_selected": summary.get("full_public_grid_selected"),
            "source_policy_1e_4_included": summary.get("source_policy_1e_4_included"),
            "reference_status": summary.get("reference_status"),
            "reference_runtime_sec": summary.get("reference_runtime_sec"),
            "estimated_reference_steps": summary.get("estimated_reference_steps"),
            "estimated_candidate_steps": summary.get("estimated_candidate_steps"),
            "canonical_hi2022_output_untouched_by_writer": summary.get(
                "canonical_hi2022_output_untouched_by_writer"
            ),
        },
        "execution_evidence": {
            "row_count": len(rows),
            "ok_row_count": len(ok_rows),
            "failed_row_count": len(failed_rows),
            "status_counts": dict(sorted(status_counts.items())),
            "rows_complete": rows_complete,
            "candidate_partial": candidate_partial,
            "selected_step_trio_completed": summary.get("selected_step_trio_completed"),
            "source_policy_candidate_rows_completed": summary.get("source_policy_candidate_rows_completed"),
            "position_pair_orders": summary.get("position_pair_orders"),
            "velocity_pair_orders": summary.get("velocity_pair_orders"),
            "acceleration_pair_orders": summary.get("acceleration_pair_orders"),
            "runtime_sec_values": summary.get("runtime_sec_values"),
            "avg_iteration_values": summary.get("avg_iteration_values"),
            "max_iteration_values": summary.get("max_iteration_values"),
            "selected_tolerance_values": selected_tolerances,
            "reference_tolerance_values": reference_tolerances,
        },
        "diagnosis": {
            "partial_or_failed_shard": True,
            "newton_failure_count": newton_failure_count,
            "failed_h_values": [row["h"] for row in failed_rows],
            "ok_h_values": [row["h"] for row in ok_rows],
            "failure_loci": failure_loci,
            "failure_messages": failure_messages,
            "pair_orders_available": bool(summary.get("position_pair_orders"))
            or bool(summary.get("velocity_pair_orders"))
            or bool(summary.get("acceleration_pair_orders")),
            "root_cause_labels": [
                "selected_step_trio_incomplete",
                "coarse_and_mid_rows_newton_failure",
                "newton_failures_at_k_100_under_rA_half_tolerance_1e_10",
                "single_ok_row_insufficient_for_order",
                "full_public_grid_not_selected",
                "tolerance_repair_attempt_recorded_but_source_policy_still_open",
                "work_precision_publication_binding_missing",
            ],
        },
        "tolerance_repair_context": {
            "audit_status": tolerance_repair.get("status"),
            "original_tolerance_base": repair_policy.get("original_tolerance_base"),
            "repair_tolerance_base": repair_policy.get("repair_tolerance_base"),
            "additional_repair_tolerance_bases": repair_policy.get("additional_repair_tolerance_bases"),
            "combined_best_rows_ok_total": [
                repair_best.get("ok_row_count"),
                repair_best.get("row_count"),
            ],
            "combined_best_complete_groups": [
                repair_best.get("complete_form_model_groups"),
                repair_best.get("group_count"),
            ],
            "recovered_row_count": repair_best.get("recovered_row_count"),
            "source_policy_reproduction_closed": repair_boundary.get("source_policy_reproduction_closed"),
            "full_T8_policy_completed": repair_boundary.get("full_T8_policy_completed"),
            "external_superiority_claim_allowed": repair_boundary.get("external_superiority_claim_allowed"),
            "interpretation": (
                "Existing tolerance-repair evidence is useful negative evidence only: it recovers one "
                "row in the broader T=8 audit but still leaves the HI2022 source-policy reproduction, "
                "full T=8 policy, and external-superiority claim open."
            ),
        },
        "promotion_decision": {
            "promotion_ready": summary.get("promotion_ready"),
            "source_policy_rows_promoted_by_this_diagnosis": 0,
            "source_policy_rows_closed_by_this_diagnosis": 0,
            "b4_b7_can_close_from_this_diagnosis": False,
            "external_superiority_claim_allowed": False,
            "reason": (
                "The isolated HI2022 rA_half double-pendulum T=8 selected-coarse-trio shard "
                "completed only the h=0.005 row; h=0.02 and h=0.01 failed with Newton-Raphson "
                "nonconvergence, leaving no pairwise order or publication work/precision curve."
            ),
            "promotion_blockers": summary.get("promotion_blockers", []),
        },
        "rows": rows,
        "safe_next_actions": [
            "Keep this shard as diagnostic evidence only.",
            "Do not promote HI2022 rA_half:double_pendulum to B4/B7 source-policy rows from a 1/3 shard.",
            "If pursuing HI2022 closure, repair the Newton convergence policy or document a formal suite demotion before rebuilding B7 figures.",
            "Bind accepted source-policy errors, runtime, and iteration counts from complete rows before any B4/B7 promotion.",
        ],
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# HI2022 rA_half Double Source-Policy Failure Diagnosis",
        "",
        "Status: **diagnosis only; partial Newton-failure shard is not promoted**.",
        "",
        "This artifact reads the completed isolated candidate rows and does not invoke any numerical runner.",
        "",
        f"- Candidate summary status: `{summary.get('status')}`.",
        f"- Form/model: `{summary.get('form')}` / `{summary.get('model')}`.",
        f"- T=8/source reference selected: `{summary.get('source_policy_time_window_selected')}` / `{summary.get('source_policy_reference_h_selected')}`.",
        f"- Selected step sizes: `{summary.get('selected_step_sizes')}`.",
        f"- Rows ok/failed/total: `{len(ok_rows)}/{len(failed_rows)}/{len(rows)}`.",
        f"- Selected step trio completed: `{summary.get('selected_step_trio_completed')}`.",
        f"- Newton failure count: `{newton_failure_count}`.",
        f"- Failed h values: `{[row['h'] for row in failed_rows]}`.",
        f"- Failure loci: `{failure_loci}`.",
        f"- Selected tolerance values: `{selected_tolerances}`.",
        (
            "- Tolerance repair combined best rows/groups: "
            f"`{repair_best.get('ok_row_count')}/{repair_best.get('row_count')}` rows, "
            f"`{repair_best.get('complete_form_model_groups')}/{repair_best.get('group_count')}` groups."
        ),
        f"- Tolerance repair source-policy closed: `{repair_boundary.get('source_policy_reproduction_closed')}`.",
        f"- Pair orders available: `{output['diagnosis']['pair_orders_available']}`.",
        f"- Promotion ready: `{summary.get('promotion_ready')}`.",
        "- Source-policy rows promoted by this diagnosis: `0`.",
        "- B4/B7 can close from this diagnosis: `False`.",
        "",
        "## Rows",
        "",
        "| h | tolerance | status | failure t | failure k | pos final linf | vel final linf | acc final linf | avg iters | max iters | runtime sec |",
        "|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| `{fmt(row['h'])}` | `{fmt(row['tolerance'])}` | `{row['status']}` | "
            f"`{fmt(row['newton_failure_time'])}` | `{row['newton_failure_iteration_k']}` | "
            f"`{fmt(row['pos_final_linf'])}` | "
            f"`{fmt(row['vel_final_linf'])}` | `{fmt(row['acc_final_linf'])}` | "
            f"`{fmt(row['avg_iterations'])}` | `{fmt(row['max_iterations'])}` | "
            f"`{fmt(row['runtime_sec'])}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            output["promotion_decision"]["reason"],
            "",
            "These rows remain a root-cause diagnostic for B4/B7, not row-closure or external-superiority evidence.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("hi2022_ra_half_double_source_policy_failure_diagnosis=written")
    print(f"rows_ok_failed_total={len(ok_rows)}/{len(failed_rows)}/{len(rows)}")
    print(f"newton_failure_count={newton_failure_count}")
    print("source_policy_rows_promoted=0")


if __name__ == "__main__":
    main()
