#!/usr/bin/env python3
"""Diagnose the low-order RA2021 double-pendulum source-policy candidate.

This builder is intentionally read-only over the completed isolated candidate
rows. It records why the rows are diagnostic-only and must not be promoted to
B4/B7 source-policy closure evidence.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
V048_RESULTS = PAPER.parent.parent / "numerics" / "v048_cross_paper_same_test_benchmarks" / "results"
SUMMARY = V048_RESULTS / "ra2021_double_local_source_policy_candidate_summary.json"
ROWS = V048_RESULTS / "ra2021_double_local_source_policy_candidate_rows.csv"
LEDGER = PAPER / "SOURCE_POLICY_ROW_CLOSURE_LEDGER.json"
OUT_JSON = PAPER / "RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.json"
OUT_MD = PAPER / "RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.md"

ORDER_ACCEPTANCE_THRESHOLD = 5.5
FLOOR_PAIR_ORDER_THRESHOLD = 0.5
FLOOR_ERROR_SCALE_THRESHOLD = 1.0e-11
CONSTRAINT_THRESHOLD = 1.0e-10
GENERIC_RA2021_PUBLIC_ORDER_STEP_SIZES = [0.01, 0.001, 0.0001]


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


def pair_order(coarse: dict[str, Any], fine: dict[str, Any], key: str) -> float | None:
    h_coarse = as_float(coarse.get("h"))
    h_fine = as_float(fine.get("h"))
    err_coarse = as_float(coarse.get(key))
    err_fine = as_float(fine.get(key))
    if (
        h_coarse is None
        or h_fine is None
        or err_coarse is None
        or err_fine is None
        or h_coarse <= h_fine
        or err_coarse <= 0.0
        or err_fine <= 0.0
    ):
        return None
    return math.log(err_coarse / err_fine) / math.log(h_coarse / h_fine)


def pair_order_row(coarse: dict[str, Any], fine: dict[str, Any], key: str) -> dict[str, Any]:
    h_coarse = finite_float(coarse.get("h"))
    h_fine = finite_float(fine.get("h"))
    err_coarse = finite_float(coarse.get(key))
    err_fine = finite_float(fine.get(key))
    return {
        "metric": key,
        "label": f"{h_coarse:g}_to_{h_fine:g}",
        "h_coarse": h_coarse,
        "h_fine": h_fine,
        "error_coarse": err_coarse,
        "error_fine": err_fine,
        "error_ratio": err_coarse / err_fine if err_fine > 0.0 else float("nan"),
        "pair_order": pair_order(coarse, fine, key),
    }


def fmt(value: object, digits: int = 3) -> str:
    number = as_float(value)
    if number is None:
        return "nan"
    if abs(number) >= 1000.0 or (0.0 < abs(number) < 1.0e-2):
        return f"{number:.{digits}e}"
    return f"{number:.{digits}f}"


def compact_row(row: dict[str, str]) -> dict[str, Any]:
    return {
        "h": finite_float(row.get("h")),
        "status": row.get("status"),
        "steps": int(finite_float(row.get("steps"))),
        "pos_traj_linf": finite_float(row.get("pos_traj_linf")),
        "vel_traj_linf": finite_float(row.get("vel_traj_linf")),
        "pos_final_linf": finite_float(row.get("pos_final_linf")),
        "vel_final_linf": finite_float(row.get("vel_final_linf")),
        "max_endpoint_constraint_norm": finite_float(row.get("max_endpoint_constraint_norm")),
        "max_endpoint_velocity_constraint_norm": finite_float(
            row.get("max_endpoint_velocity_constraint_norm")
        ),
        "constraint_threshold_satisfied": as_bool(row.get("constraint_threshold_satisfied")),
        "total_newton_iterations": int(finite_float(row.get("total_newton_iterations"))),
        "runtime_sec": finite_float(row.get("runtime_sec")),
        "public_policy_time_window": as_bool(row.get("public_policy_time_window")),
        "public_policy_h": as_bool(row.get("public_policy_h")),
        "source_policy_time_window": as_bool(row.get("source_policy_time_window")),
        "source_policy_h": as_bool(row.get("source_policy_h")),
        "source_policy_reference_h": as_bool(row.get("source_policy_reference_h")),
        "source_policy_contract_selected": as_bool(row.get("source_policy_contract_selected")),
    }


def main() -> None:
    summary = read_json(SUMMARY)
    ledger = read_json(LEDGER)
    raw_rows = read_csv(ROWS)
    rows = sorted((compact_row(row) for row in raw_rows), key=lambda row: float(row["h"]), reverse=True)

    pairwise: list[dict[str, Any]] = []
    for coarse, fine in zip(rows, rows[1:]):
        pos_pair_order = pair_order(coarse, fine, "pos_traj_linf")
        vel_pair_order = pair_order(coarse, fine, "vel_traj_linf")
        h_coarse = finite_float(coarse.get("h"))
        h_fine = finite_float(fine.get("h"))
        max_error_scale = max(
            finite_float(coarse.get("pos_traj_linf")),
            finite_float(fine.get("pos_traj_linf")),
            finite_float(coarse.get("vel_traj_linf")),
            finite_float(fine.get("vel_traj_linf")),
        )
        floor_limited = (
            h_coarse <= 0.002
            and h_fine <= 0.001
            and pos_pair_order is not None
            and vel_pair_order is not None
            and pos_pair_order < FLOOR_PAIR_ORDER_THRESHOLD
            and vel_pair_order < FLOOR_PAIR_ORDER_THRESHOLD
            and max_error_scale < FLOOR_ERROR_SCALE_THRESHOLD
        )
        pairwise.append(
            {
                "label": f"{h_coarse:g}_to_{h_fine:g}",
                "h_coarse": h_coarse,
                "h_fine": h_fine,
                "h_ratio": h_coarse / h_fine if h_fine > 0.0 else float("nan"),
                "pos_error_ratio": finite_float(coarse.get("pos_traj_linf"))
                / finite_float(fine.get("pos_traj_linf")),
                "vel_error_ratio": finite_float(coarse.get("vel_traj_linf"))
                / finite_float(fine.get("vel_traj_linf")),
                "pos_pair_order": pos_pair_order,
                "vel_pair_order": vel_pair_order,
                "max_pair_error_scale": max_error_scale,
                "fine_pair_floor_limited": floor_limited,
            }
        )

    h_values = sorted(finite_float(row.get("h")) for row in rows)
    reference_h_values = sorted({finite_float(row.get("reference_h", summary.get("selected_reference_h"))) for row in raw_rows})
    coarse_row = next((row for row in rows if abs(finite_float(row.get("h")) - 0.01) < 1.0e-15), {})
    coarse_pair = next((item for item in pairwise if item["label"] == "0.01_to_0.002"), {})
    fine_pair = next((item for item in pairwise if item["fine_pair_floor_limited"] is True), {})
    pairwise_error_family = [
        pair_order_row(coarse, fine, key)
        for coarse, fine in zip(rows, rows[1:])
        for key in ("pos_traj_linf", "vel_traj_linf", "pos_final_linf", "vel_final_linf")
    ]
    rows_complete = len(rows) == 3 and all(row.get("status") == "ok" for row in rows)
    aggregate_pos_order = summary.get("source_policy_pos_observed_order")
    aggregate_vel_order = summary.get("source_policy_vel_observed_order")
    aggregate_order_acceptance_satisfied = summary.get("source_policy_order_acceptance_satisfied")
    public_policy_candidate_h_values = sorted(
        finite_float(row.get("h")) for row in rows if row.get("public_policy_h") is True
    )
    public_policy_missing_candidate_h_values = [
        h for h in GENERIC_RA2021_PUBLIC_ORDER_STEP_SIZES if h not in public_policy_candidate_h_values
    ]
    non_public_selected_candidate_h_values = sorted(
        finite_float(row.get("h")) for row in rows if row.get("public_policy_h") is False
    )
    coarse_position_constraint = finite_float(coarse_row.get("max_endpoint_constraint_norm"))
    coarse_velocity_constraint = finite_float(coarse_row.get("max_endpoint_velocity_constraint_norm"))
    coarse_constraint_failure_components = []
    if coarse_position_constraint >= CONSTRAINT_THRESHOLD:
        coarse_constraint_failure_components.append("endpoint_position_constraint")
    if coarse_velocity_constraint >= CONSTRAINT_THRESHOLD:
        coarse_constraint_failure_components.append("endpoint_velocity_constraint")
    fine_pair_max_error_scale = finite_float(fine_pair.get("max_pair_error_scale"))
    floor_margin_to_threshold = (
        fine_pair_max_error_scale / FLOOR_ERROR_SCALE_THRESHOLD
        if fine_pair_max_error_scale > 0.0
        else float("nan")
    )
    finest_h = min(h_values) if h_values else float("nan")
    reference_h = finite_float(summary.get("selected_reference_h"))
    finest_to_reference_step_ratio = finest_h / reference_h if reference_h > 0.0 else float("nan")
    candidate_metric_columns = [
        "pos_traj_linf",
        "vel_traj_linf",
        "pos_final_linf",
        "vel_final_linf",
        "runtime_sec",
        "total_newton_iterations",
    ]
    candidate_local_metrics_present = all(
        all(as_float(row.get(key)) is not None for key in candidate_metric_columns)
        for row in rows
    )
    ledger_rows = [
        row
        for row in ledger.get("rows", [])
        if row.get("suite") == "ra2021_absolute_coordinate"
        and row.get("example") == "double_pendulum"
    ]
    ledger_missing_counts = [
        int(row.get("missing_evidence_count", -1))
        for row in ledger_rows
        if row.get("missing_evidence_count") is not None
    ]
    ledger_ra2021_status = ledger.get("suite_closure_status", {}).get("ra2021_absolute_coordinate", {})
    ledger_binding_reconciliation = {
        "source": "SOURCE_POLICY_ROW_CLOSURE_LEDGER.json",
        "candidate_local_error_runtime_newton_columns_present": candidate_local_metrics_present,
        "candidate_metric_columns_checked": candidate_metric_columns,
        "accepted_source_policy_binding_closed": False,
        "candidate_local_metrics_are_promotable_binding": False,
        "ledger_status": ledger.get("status"),
        "ledger_rows_source_policy_closed": ledger.get("coverage", {}).get("rows_source_policy_closed"),
        "ledger_rows_external_superiority_ready": ledger.get("coverage", {}).get(
            "rows_external_superiority_ready"
        ),
        "ledger_ra2021_status": ledger_ra2021_status.get("status"),
        "ledger_ra2021_source_identity_resolved_evidence_per_row": ledger_ra2021_status.get(
            "source_identity_resolved_evidence_per_row"
        ),
        "ledger_ra2021_source_policy_promotion_evidence_remaining_per_row": ledger_ra2021_status.get(
            "source_policy_promotion_evidence_remaining_per_row"
        ),
        "ledger_double_row_count": len(ledger_rows),
        "ledger_double_missing_evidence_counts": ledger_missing_counts,
        "ledger_double_required_actions": [
            row.get("required_closure_action") for row in ledger_rows
        ],
        "ledger_double_action_classes": sorted({row.get("action_class") for row in ledger_rows}),
        "ledger_double_allowed_uses": sorted({row.get("current_allowed_use") for row in ledger_rows}),
        "row_status_can_shrink_from_this_read_only_diagnosis": False,
        "reason": (
            "The candidate rows contain local error, runtime, and Newton fields, but the row ledger "
            "still requires accepted source-policy binding plus independent verification before any "
            "RA2021 double row can close."
        ),
    }

    output: dict[str, Any] = {
        "schema": "ra2021-double-source-policy-low-order-diagnosis-v1",
        "status": "diagnosis_only_low_order_floor_limited_not_promoted",
        "read_only": True,
        "heavy_numerical_run_invoked_by_this_builder": False,
        "run_v047_invoked_by_this_builder": False,
        "v048_runner_invoked_by_this_builder": False,
        "input_artifacts": {
            "candidate_summary": "../../numerics/v048_cross_paper_same_test_benchmarks/results/"
            "ra2021_double_local_source_policy_candidate_summary.json",
            "candidate_rows": "../../numerics/v048_cross_paper_same_test_benchmarks/results/"
            "ra2021_double_local_source_policy_candidate_rows.csv",
        },
        "candidate_contract": {
            "summary_status": summary.get("status"),
            "execution_mode": summary.get("execution_mode"),
            "rows_complete": rows_complete,
            "row_count": len(rows),
            "ok_row_count": sum(1 for row in rows if row.get("status") == "ok"),
            "source_policy_time_window_selected": summary.get("source_policy_time_window_selected"),
            "source_policy_step_trio_selected": summary.get("source_policy_step_trio_selected"),
            "source_policy_reference_h_selected": summary.get("source_policy_reference_h_selected"),
            "source_policy_contract_selected": summary.get("source_policy_contract_selected"),
            "selected_t_end": summary.get("selected_t_end"),
            "selected_step_sizes": summary.get("selected_step_sizes"),
            "observed_h_values": h_values,
            "selected_reference_h": summary.get("selected_reference_h"),
            "observed_reference_h_values": reference_h_values,
            "reference_status": summary.get("reference_status"),
            "reference_runtime_sec": summary.get("reference_runtime_sec"),
            "estimated_reference_steps": summary.get("estimated_reference_steps"),
            "estimated_candidate_steps": summary.get("estimated_candidate_steps"),
            "jax_safe_small_angle_patch_enabled": summary.get("jax_safe_small_angle_patch_enabled"),
            "jax_safe_small_angle_patch_id": summary.get("jax_safe_small_angle_patch_id"),
        },
        "public_step_family_audit": {
            "generic_ra2021_public_order_step_sizes": GENERIC_RA2021_PUBLIC_ORDER_STEP_SIZES,
            "candidate_public_policy_h_values": public_policy_candidate_h_values,
            "candidate_public_policy_h_count": len(public_policy_candidate_h_values),
            "generic_public_policy_h_required_count": len(GENERIC_RA2021_PUBLIC_ORDER_STEP_SIZES),
            "generic_public_policy_h_missing_as_candidate_values": public_policy_missing_candidate_h_values,
            "non_public_selected_candidate_h_values": non_public_selected_candidate_h_values,
            "selected_source_policy_h_values": h_values,
            "source_policy_h_marker_count": sum(1 for row in rows if row.get("source_policy_h") is True),
            "scope_note": (
                "The isolated double-pendulum candidate uses the encoded double-local source-policy "
                "trio [0.01, 0.002, 0.001] with h_ref=0.0001. In the generic RA2021 public order "
                "step family [0.01, 0.001, 0.0001], h=0.002 is not a public-policy candidate h and "
                "h=0.0001 appears only as the reference for this local candidate."
            ),
        },
        "order_evidence": {
            "source_policy_order_acceptance_threshold": summary.get(
                "source_policy_order_acceptance_threshold", ORDER_ACCEPTANCE_THRESHOLD
            ),
            "aggregate_pos_observed_order": aggregate_pos_order,
            "aggregate_vel_observed_order": aggregate_vel_order,
            "aggregate_order_acceptance_satisfied": aggregate_order_acceptance_satisfied,
            "aggregate_order_below_acceptance": aggregate_order_acceptance_satisfied is False,
            "pairwise_orders": pairwise,
            "pairwise_error_family": pairwise_error_family,
            "final_error_pairwise_orders": [
                item for item in pairwise_error_family if item["metric"] in {"pos_final_linf", "vel_final_linf"}
            ],
            "trajectory_error_pairwise_orders": [
                item for item in pairwise_error_family if item["metric"] in {"pos_traj_linf", "vel_traj_linf"}
            ],
        },
        "diagnosis": {
            "fine_pair_floor_limited": bool(fine_pair),
            "coarse_to_mid_pair_label": coarse_pair.get("label"),
            "coarse_to_mid_pos_pair_order": coarse_pair.get("pos_pair_order"),
            "coarse_to_mid_vel_pair_order": coarse_pair.get("vel_pair_order"),
            "coarse_to_mid_pair_below_acceptance": bool(
                coarse_pair
                and as_float(coarse_pair.get("pos_pair_order")) is not None
                and as_float(coarse_pair.get("vel_pair_order")) is not None
                and float(coarse_pair["pos_pair_order"]) < ORDER_ACCEPTANCE_THRESHOLD
                and float(coarse_pair["vel_pair_order"]) < ORDER_ACCEPTANCE_THRESHOLD
            ),
            "fine_pair_label": fine_pair.get("label"),
            "fine_pair_pos_pair_order": fine_pair.get("pos_pair_order"),
            "fine_pair_vel_pair_order": fine_pair.get("vel_pair_order"),
            "fine_pair_max_error_scale": fine_pair.get("max_pair_error_scale"),
            "fine_pair_floor_error_scale_threshold": FLOOR_ERROR_SCALE_THRESHOLD,
            "fine_pair_floor_margin_to_threshold": floor_margin_to_threshold,
            "finest_to_reference_step_ratio": finest_to_reference_step_ratio,
            "finest_h": finest_h,
            "reference_h": reference_h,
            "reference_floor_sensitivity": (
                "fine_pair_errors_below_floor_threshold_and_only_ten_reference_steps_per_finest_step"
            ),
            "coarse_h_constraint_threshold_satisfied": coarse_row.get("constraint_threshold_satisfied"),
            "constraint_threshold": CONSTRAINT_THRESHOLD,
            "coarse_h_constraint_failure_components": coarse_constraint_failure_components,
            "coarse_h_max_endpoint_constraint_norm": coarse_row.get("max_endpoint_constraint_norm"),
            "coarse_h_max_endpoint_velocity_constraint_norm": coarse_row.get(
                "max_endpoint_velocity_constraint_norm"
            ),
            "coarse_h_endpoint_velocity_over_threshold_factor": (
                coarse_velocity_constraint / CONSTRAINT_THRESHOLD
                if coarse_velocity_constraint > 0.0
                else float("nan")
            ),
            "root_cause_labels": [
                "fine_pair_near_reference_or_roundoff_floor",
                "coarse_to_mid_pair_below_sixth_order_acceptance",
                "coarse_h_constraint_threshold_not_satisfied",
                "aggregate_order_below_sixth_order_acceptance",
                "local_double_source_policy_not_generic_public_order_step_family",
                "no_single_implementation_defect_proven_from_existing_read_only_evidence",
                "independent_rerun_missing",
                "error_runtime_newton_policy_binding_missing",
                "coarse_h_endpoint_velocity_constraint_exceeds_threshold",
                "final_error_orders_do_not_rescue_trajectory_order_acceptance",
            ],
            "proof_boundary": (
                "The existing read-only rows prove non-promotion conditions but do not identify a "
                "single implementation defect. The low aggregate order is consistent with both a "
                "non-asymptotic coarse-to-mid pair and a near-floor fine pair."
            ),
        },
        "promotion_decision": {
            "promotion_ready": summary.get("promotion_ready"),
            "source_policy_rows_promoted_by_this_diagnosis": 0,
            "source_policy_rows_closed_by_this_diagnosis": 0,
            "b4_b7_can_close_from_this_diagnosis": False,
            "external_superiority_claim_allowed": False,
            "reason": (
                "The exact h/ref source-policy candidate rows are complete, but the aggregate order is below "
                "acceptance, the 0.01->0.002 pair is itself below sixth-order acceptance, the "
                "0.002->0.001 pair is near the numerical floor, the h=0.01 row misses the "
                "constraint threshold, the scope remains an isolated local double source-policy candidate rather "
                "than the generic RA2021 public order step family, and independent rerun plus "
                "error/runtime/Newton bindings remain absent."
            ),
            "promotion_blockers": summary.get("promotion_blockers", []),
        },
        "ledger_binding_reconciliation": ledger_binding_reconciliation,
        "rows": rows,
        "safe_next_actions": [
            "Keep the three rows as diagnostic evidence only.",
            "Do not rerun the same B4 guarded driver solely to promote these rows.",
            "If pursuing RA2021 double closure, produce a separately labeled non-floor-limited diagnostic policy or a stronger precision/reference policy plus independent verification.",
            "Bind accepted source-policy errors, runtime, and Newton iteration counts before any B4/B7 promotion.",
        ],
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, sort_keys=True)
        handle.write("\n")

    threshold = output["order_evidence"]["source_policy_order_acceptance_threshold"]
    lines = [
        "# RA2021 Double Source-Policy Low-Order Diagnosis",
        "",
        "Status: **diagnosis only; low-order rows are not promoted**.",
        "",
        "This artifact reads the completed isolated candidate rows and does not invoke any numerical runner.",
        "",
        f"- Candidate summary status: `{summary.get('status')}`.",
        f"- Rows complete: `{rows_complete}` with `{len(rows)}` rows.",
        f"- Source-policy h/ref contract selected: `{summary.get('source_policy_contract_selected')}`.",
        (
            "- Generic RA2021 public h represented as candidate rows: "
            f"`{len(public_policy_candidate_h_values)}/{len(GENERIC_RA2021_PUBLIC_ORDER_STEP_SIZES)}`."
        ),
        f"- Non-public selected candidate h values: `{non_public_selected_candidate_h_values}`.",
        f"- Aggregate pos/vel order: `{fmt(aggregate_pos_order)}/{fmt(aggregate_vel_order)}` below threshold `{fmt(threshold)}`.",
        (
            "- Coarse-to-mid 0.01 -> 0.002 pos/vel order: "
            f"`{fmt(output['diagnosis']['coarse_to_mid_pos_pair_order'])}/"
            f"{fmt(output['diagnosis']['coarse_to_mid_vel_pair_order'])}`."
        ),
        f"- Fine pair floor-limited: `{output['diagnosis']['fine_pair_floor_limited']}`.",
        (
            "- Fine pair 0.002 -> 0.001 pos/vel order: "
            f"`{fmt(output['diagnosis']['fine_pair_pos_pair_order'])}/"
            f"{fmt(output['diagnosis']['fine_pair_vel_pair_order'])}`."
        ),
        f"- h=0.01 constraint threshold satisfied: `{output['diagnosis']['coarse_h_constraint_threshold_satisfied']}`.",
        "- Single implementation defect proven by this diagnosis: `False`.",
        (
            "- Coarse h constraint failure components: "
            f"`{output['diagnosis']['coarse_h_constraint_failure_components']}`."
        ),
        (
            "- Fine-pair floor margin to threshold: "
            f"`{fmt(output['diagnosis']['fine_pair_floor_margin_to_threshold'])}` with "
            f"finest/reference h ratio `{fmt(output['diagnosis']['finest_to_reference_step_ratio'])}`."
        ),
        (
            "- Ledger binding reconciliation: local metrics present "
            f"`{ledger_binding_reconciliation['candidate_local_error_runtime_newton_columns_present']}`, "
            f"accepted binding `{ledger_binding_reconciliation['accepted_source_policy_binding_closed']}`, "
            f"ledger RA2021 remaining evidence per row "
            f"`{ledger_binding_reconciliation['ledger_ra2021_source_policy_promotion_evidence_remaining_per_row']}`, "
            f"row status shrink `{ledger_binding_reconciliation['row_status_can_shrink_from_this_read_only_diagnosis']}`."
        ),
        f"- Promotion ready: `{summary.get('promotion_ready')}`.",
        "- Source-policy rows promoted by this diagnosis: `0`.",
        "- B4/B7 can close from this diagnosis: `False`.",
        "",
        "## Pairwise Orders",
        "",
        "| pair | h ratio | pos ratio | vel ratio | pos order | vel order | floor-limited |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for item in pairwise:
        lines.append(
            f"| `{item['label']}` | `{fmt(item['h_ratio'])}` | `{fmt(item['pos_error_ratio'])}` | "
            f"`{fmt(item['vel_error_ratio'])}` | `{fmt(item['pos_pair_order'])}` | "
            f"`{fmt(item['vel_pair_order'])}` | `{item['fine_pair_floor_limited']}` |"
        )
    lines.extend(
        [
            "",
            "## Final-vs-Trajectory Order Sensitivity",
            "",
            "| metric | pair | error ratio | pair order |",
            "|---|---|---:|---:|",
        ]
    )
    for item in pairwise_error_family:
        lines.append(
            f"| `{item['metric']}` | `{item['label']}` | `{fmt(item['error_ratio'])}` | "
            f"`{fmt(item['pair_order'])}` |"
        )
    lines.extend(
        [
            "",
            "## Rows",
            "",
            "| h | status | source h | public h | pos traj linf | vel traj linf | constraint threshold | Newton iterations | runtime sec |",
            "|---:|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in rows:
        lines.append(
            f"| `{fmt(row['h'])}` | `{row['status']}` | `{row['source_policy_h']}` | "
            f"`{row['public_policy_h']}` | `{fmt(row['pos_traj_linf'])}` | "
            f"`{fmt(row['vel_traj_linf'])}` | `{row['constraint_threshold_satisfied']}` | "
            f"`{row['total_newton_iterations']}` | `{fmt(row['runtime_sec'])}` |"
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

    print("ra2021_double_source_policy_low_order_diagnosis=written")
    print(f"rows_complete={rows_complete}")
    print(f"aggregate_pos_order={fmt(aggregate_pos_order)}")
    print(f"aggregate_vel_order={fmt(aggregate_vel_order)}")
    print(f"fine_pair_floor_limited={output['diagnosis']['fine_pair_floor_limited']}")
    print("source_policy_rows_promoted=0")


if __name__ == "__main__":
    main()
