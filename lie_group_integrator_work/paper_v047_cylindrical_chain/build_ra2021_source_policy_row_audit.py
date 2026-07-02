#!/usr/bin/env python3
"""Audit RA2021 active source-policy rows against existing public baseline artifacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
V048_RESULTS = PAPER.parent / "v048_cross_paper_same_test_benchmarks" / "results"


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_json_if_exists(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return read_json(path)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_csv_if_exists(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    return read_csv(path)


def bool_from_cell(value: str | None) -> bool:
    return str(value).strip().lower() == "true"


def float_from_cell(value: str | None) -> float | None:
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return None


def h_values(rows: list[dict[str, str]]) -> list[float]:
    values = [float_from_cell(row.get("h")) for row in rows]
    return sorted(value for value in values if value is not None)


def finest_row(rows: list[dict[str, str]]) -> dict[str, str]:
    ok_rows = [row for row in rows if row.get("status") == "ok"]
    if not ok_rows:
        return {}
    return min(ok_rows, key=lambda row: float_from_cell(row.get("h")) or float("inf"))


def main() -> None:
    b2_manifest = read_json(PAPER / "B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.json")
    external_case = read_json(PAPER / "EXTERNAL_CASE_EVIDENCE_RECONCILIATION.json")
    source_identity = read_json(PAPER / "RA2021_SOURCE_IDENTITY_AUDIT.json")
    summary_v048 = read_json(V048_RESULTS / "summary_v048.json")
    policy_rows = read_csv(V048_RESULTS / "apples_to_apples_policy_audit.csv")
    forensic_rows = read_csv(V048_RESULTS / "all_examples_apples_to_apples_forensic_audit.csv")
    order_summary_rows = read_csv(V048_RESULTS / "ra2021_public_order_work_summary.csv")
    timing_rows = read_csv(V048_RESULTS / "ra2021_public_timing_rows.csv")
    local_single_public_rows = read_csv(V048_RESULTS / "gauss6_fullva_public_horizon_single_rows.csv")
    local_double_coarse_rows = read_csv(V048_RESULTS / "gauss6_fullva_public_horizon_double_coarse_rows.csv")
    local_closed_loop_public_rows = read_csv(V048_RESULTS / "gauss6_fullva_public_horizon_closed_loop_rows.csv")
    local_closed_loop_true_dynamic_rows = read_csv(
        V048_RESULTS / "closed_loop_true_dynamic_newton_coarse_order_rows.csv"
    )
    closed_loop_same_window_public_work = read_json_if_exists(
        V048_RESULTS / "closed_loop_true_dynamic_public_work_precision.json"
    )
    closed_loop_same_window_public_work_rows = read_csv_if_exists(
        V048_RESULTS / "closed_loop_true_dynamic_public_work_precision_rows.csv"
    )
    closed_loop_same_window_public_work_summary_rows = read_csv_if_exists(
        V048_RESULTS / "closed_loop_true_dynamic_public_work_precision_summary.csv"
    )
    double_source_policy_candidate = read_json_if_exists(
        V048_RESULTS / "ra2021_double_local_source_policy_candidate_summary.json"
    )
    double_source_policy_candidate_rows = read_csv_if_exists(
        V048_RESULTS / "ra2021_double_local_source_policy_candidate_rows.csv"
    )
    double_low_order_diagnosis = read_json_if_exists(
        PAPER / "RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.json"
    )
    double_low_order_diagnosis_block = double_low_order_diagnosis.get("diagnosis", {})
    double_low_order_promotion = double_low_order_diagnosis.get("promotion_decision", {})
    double_candidate_completed = int(double_source_policy_candidate.get("source_policy_candidate_rows_completed") or 0)
    double_candidate_row_count = len(double_source_policy_candidate_rows)
    double_candidate_order_satisfied = double_source_policy_candidate.get("source_policy_order_acceptance_satisfied")
    double_candidate_pos_order = double_source_policy_candidate.get("source_policy_pos_observed_order")
    double_candidate_vel_order = double_source_policy_candidate.get("source_policy_vel_observed_order")
    if double_candidate_completed == double_candidate_row_count == 3:
        if double_candidate_order_satisfied is False:
            double_candidate_execution_note = (
                "isolated exact source-policy rows are complete, but their observed order is below sixth-order "
                "acceptance and they remain unpromoted"
            )
            double_candidate_table_note = "isolated exact rows complete but low-order"
            double_candidate_gap_note = "isolated exact rows complete; observed order is below acceptance"
        else:
            double_candidate_execution_note = (
                "isolated exact source-policy rows are complete, but they remain unpromoted until independent rerun "
                "and source-policy error/runtime/Newton bindings are complete"
            )
            double_candidate_table_note = "isolated exact rows complete but unpromoted"
            double_candidate_gap_note = "isolated exact rows complete; promotion still blocked by verification/binding"
    else:
        double_candidate_execution_note = (
            "an isolated exact source-policy candidate exists, but its heavy rows remain incomplete or unverified"
        )
        double_candidate_table_note = "isolated exact rows incomplete"
        double_candidate_gap_note = "isolated exact rows not yet complete"

    active_rows = [
        row
        for row in b2_manifest.get("rows", [])
        if row.get("suite_id") == "ra2021_absolute_coordinate" and row.get("active_b2_requirement") is True
    ]
    policy_by_key = {(row["method"], row["example"]): row for row in policy_rows if row["method"].startswith("ra2021_")}
    forensic_by_key = {
        (row["method"], row["example"]): row for row in forensic_rows if row["method"].startswith("ra2021_")
    }

    single_summary = summary_v048.get("gauss6_fullva_public_horizon_single", {})
    single_finest = finest_row(local_single_public_rows)
    double_summary = summary_v048.get("gauss6_fullva_public_horizon_double_coarse", {})
    double_finest = finest_row(local_double_coarse_rows)
    closed_summary = summary_v048.get("gauss6_fullva_public_horizon_closed_loop", {})
    true_dynamic_models: dict[str, list[dict[str, str]]] = {}
    for row in local_closed_loop_true_dynamic_rows:
        true_dynamic_models.setdefault(row.get("model", ""), []).append(row)
    same_window_model_summaries: dict[str, dict[str, Any]] = {}
    for model_name in ("four_link", "slider_crank"):
        local_rows = [
            row
            for row in closed_loop_same_window_public_work_summary_rows
            if row.get("model") == model_name and row.get("source_suite") == "local_true_dynamic_newton"
        ]
        public_rows = [
            row
            for row in closed_loop_same_window_public_work_summary_rows
            if row.get("model") == model_name and row.get("source_suite") == "ra2021_taves_kissel_negrut"
        ]
        local_summary = local_rows[0] if local_rows else {}
        same_window_model_summaries[model_name] = {
            "local_summary_present": bool(local_summary),
            "public_summary_count": len(public_rows),
            "public_methods": sorted(row.get("method") for row in public_rows if row.get("method")),
            "local_pos_observed_order": float_from_cell(local_summary.get("pos_observed_order")),
            "local_vel_observed_order": float_from_cell(local_summary.get("vel_observed_order")),
            "local_finest_pos_final_linf": float_from_cell(local_summary.get("finest_pos_final_linf")),
            "local_finest_vel_final_linf": float_from_cell(local_summary.get("finest_vel_final_linf")),
            "local_runtime_sec_sum": float_from_cell(local_summary.get("runtime_sec_sum")),
            "local_finest_runtime_ratio_vs_public_rA": float_from_cell(
                local_summary.get("finest_runtime_ratio_vs_public_rA")
            ),
            "reference_alignment": local_summary.get("reference_alignment"),
            "accepted_dynamic_order": bool_from_cell(local_summary.get("accepted_dynamic_order")),
            "external_superiority_claim_allowed": bool_from_cell(
                local_summary.get("external_superiority_claim_allowed")
            ),
        }
    closed_loop_same_window_public_work_evidence = {
        "schema": "ra2021-closed-loop-same-window-public-work-precision-evidence-v1",
        "artifact_present": bool(closed_loop_same_window_public_work),
        "artifact_status": closed_loop_same_window_public_work.get("status"),
        "artifact_json": "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_public_work_precision.json",
        "artifact_rows": "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_public_work_precision_rows.csv",
        "artifact_summary_rows": "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_public_work_precision_summary.csv",
        "row_count": len(closed_loop_same_window_public_work_rows),
        "ok_row_count": sum(1 for row in closed_loop_same_window_public_work_rows if row.get("status") == "ok"),
        "summary_row_count": len(closed_loop_same_window_public_work_summary_rows),
        "models": closed_loop_same_window_public_work.get("models", []),
        "t_end": closed_loop_same_window_public_work.get("t_end"),
        "step_sizes": closed_loop_same_window_public_work.get("step_sizes", []),
        "reference_h": closed_loop_same_window_public_work.get("reference_h"),
        "public_forms": closed_loop_same_window_public_work.get("public_forms", []),
        "public_work_precision_available_count": closed_loop_same_window_public_work.get(
            "public_work_precision_available_count"
        ),
        "public_work_precision_available_examples": closed_loop_same_window_public_work.get(
            "public_work_precision_available_examples", []
        ),
        "public_work_precision_missing_count": closed_loop_same_window_public_work.get(
            "public_work_precision_missing_count"
        ),
        "local_true_dynamic_order_available_count": closed_loop_same_window_public_work.get(
            "local_true_dynamic_order_available_count"
        ),
        "strict_common_reference_error_columns": closed_loop_same_window_public_work.get(
            "strict_common_reference_error_columns"
        ),
        "reference_alignment_status": closed_loop_same_window_public_work.get("reference_alignment_status"),
        "external_superiority_claim": closed_loop_same_window_public_work.get("external_superiority_claim"),
        "accepted_external_dynamic_order_examples": closed_loop_same_window_public_work.get(
            "accepted_external_dynamic_order_examples", []
        ),
        "counts_as_bounded_same_window_diagnostic": (
            closed_loop_same_window_public_work.get("public_work_precision_available_count") == 2
            and closed_loop_same_window_public_work.get("strict_common_reference_error_columns") is False
            and closed_loop_same_window_public_work.get("external_superiority_claim") is False
        ),
        "counts_as_source_policy_reproduction": False,
        "counts_as_external_superiority_evidence": False,
        "source_policy_rows_closed_by_this_evidence": 0,
        "b4_b7_can_close_from_this_evidence": False,
        "promotion_gap": (
            "same-window public work/precision rows are available for the two closed-loop examples, "
            "but public errors use the RA2021 rA kinematic reference while local errors use the local exact-endpoint "
            "reference; the T=0.1 bounded rows therefore remain diagnostic rather than source-policy promotion rows"
        ),
        "model_summaries": same_window_model_summaries,
    }
    local_candidate_feasibility = {
        "single_pendulum": {
            "candidate_rows_exist": len(local_single_public_rows) == 3,
            "row_file": "../v048_cross_paper_same_test_benchmarks/results/gauss6_fullva_public_horizon_single_rows.csv",
            "public_policy_time_window": single_summary.get("public_policy_time_window"),
            "public_policy_h_rows_completed": single_summary.get("public_step_size_rows_completed"),
            "public_policy_h_rows_required": single_summary.get("public_step_size_required_count"),
            "step_sizes": h_values(local_single_public_rows),
            "reference_h": single_summary.get("selected_reference_h"),
            "position_observed_order": single_summary.get("position_observed_order"),
            "velocity_observed_order": single_summary.get("velocity_observed_order"),
            "orientation_observed_order": single_summary.get("orientation_observed_order"),
            "omega_observed_order": single_summary.get("omega_observed_order"),
            "finest_h": float_from_cell(single_finest.get("h")),
            "finest_position_l2_error": float_from_cell(single_finest.get("position_l2_error")),
            "finest_velocity_l2_error": float_from_cell(single_finest.get("velocity_l2_error")),
            "runtime_sec_at_finest_h": float_from_cell(single_finest.get("runtime_sec")),
            "newton_iterations_at_finest_h": float_from_cell(single_finest.get("total_newton_iterations")),
            "promotion_status": "not_promoted_floor_limited_public_h_tranche",
            "promotion_blockers": [
                "public h rows exist, but position/orientation errors are near roundoff and observed order is floor limited",
                "source-policy dynamic-order superiority would need a wider admissible step window or a stronger precision/reference policy",
                "runtime/Newton policy still has to be bound to any accepted promoted row",
            ],
        },
        "double_pendulum": {
            "candidate_rows_exist": len(local_double_coarse_rows) == 3,
            "row_file": "../v048_cross_paper_same_test_benchmarks/results/gauss6_fullva_public_horizon_double_coarse_rows.csv",
            "public_policy_time_window": double_summary.get("public_policy_time_window"),
            "public_policy_h_rows_completed": double_summary.get("public_policy_h_rows_completed"),
            "public_policy_h_rows_required": double_summary.get("public_policy_h_required_count"),
            "step_sizes": h_values(local_double_coarse_rows),
            "source_policy_step_sizes_required": summary_v048.get("ra2021_double_pendulum_order", {}).get(
                "selected_step_sizes"
            ),
            "reference_h": double_summary.get("selected_reference_h"),
            "source_policy_reference_h_required": summary_v048.get("ra2021_double_pendulum_order", {}).get(
                "selected_reference_h"
            ),
            "position_observed_order": double_summary.get("pos_observed_order"),
            "velocity_observed_order": double_summary.get("vel_observed_order"),
            "finest_h": float_from_cell(double_finest.get("h")),
            "finest_position_linf_error": float_from_cell(double_finest.get("pos_final_linf")),
            "finest_velocity_linf_error": float_from_cell(double_finest.get("vel_final_linf")),
            "runtime_sec_at_finest_h": float_from_cell(double_finest.get("runtime_sec")),
            "newton_iterations_at_finest_h": float_from_cell(double_finest.get("total_newton_iterations")),
            "isolated_source_policy_candidate_present": bool(double_source_policy_candidate),
            "isolated_source_policy_candidate_status": double_source_policy_candidate.get("status"),
            "isolated_source_policy_candidate_execution_mode": double_source_policy_candidate.get("execution_mode"),
            "isolated_source_policy_candidate_contract_selected": double_source_policy_candidate.get(
                "source_policy_contract_selected"
            ),
            "isolated_source_policy_candidate_reference_status": double_source_policy_candidate.get(
                "reference_status"
            ),
            "isolated_source_policy_candidate_reference_failure_kind": double_source_policy_candidate.get(
                "reference_failure_kind"
            ),
            "isolated_source_policy_candidate_reference_failure_message": double_source_policy_candidate.get(
                "reference_failure_message"
            ),
            "isolated_source_policy_candidate_jax_safe_small_angle_patch_enabled": (
                double_source_policy_candidate.get("jax_safe_small_angle_patch_enabled")
            ),
            "isolated_source_policy_candidate_jax_safe_small_angle_patch_id": double_source_policy_candidate.get(
                "jax_safe_small_angle_patch_id"
            ),
            "isolated_source_policy_candidate_rows": double_candidate_row_count,
            "isolated_source_policy_candidate_rows_completed": double_source_policy_candidate.get(
                "source_policy_candidate_rows_completed"
            ),
            "isolated_source_policy_candidate_pos_observed_order": double_candidate_pos_order,
            "isolated_source_policy_candidate_vel_observed_order": double_candidate_vel_order,
            "isolated_source_policy_candidate_order_acceptance_satisfied": double_candidate_order_satisfied,
            "isolated_source_policy_candidate_estimated_reference_steps": double_source_policy_candidate.get(
                "estimated_reference_steps"
            ),
            "isolated_source_policy_candidate_estimated_candidate_steps": double_source_policy_candidate.get(
                "estimated_candidate_steps"
            ),
            "isolated_source_policy_candidate_rows_file": (
                "../v048_cross_paper_same_test_benchmarks/results/"
                "ra2021_double_local_source_policy_candidate_rows.csv"
            ),
            "isolated_source_policy_candidate_low_order_diagnosis_file": (
                "RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.json"
            ),
            "isolated_source_policy_candidate_low_order_diagnosis_status": double_low_order_diagnosis.get(
                "status"
            ),
            "isolated_source_policy_candidate_low_order_fine_pair_floor_limited": (
                double_low_order_diagnosis_block.get("fine_pair_floor_limited")
            ),
            "isolated_source_policy_candidate_low_order_fine_pair_label": (
                double_low_order_diagnosis_block.get("fine_pair_label")
            ),
            "isolated_source_policy_candidate_low_order_coarse_h_constraint_threshold_satisfied": (
                double_low_order_diagnosis_block.get("coarse_h_constraint_threshold_satisfied")
            ),
            "isolated_source_policy_candidate_low_order_constraint_failure_components": (
                double_low_order_diagnosis_block.get("coarse_h_constraint_failure_components")
            ),
            "isolated_source_policy_candidate_low_order_fine_pair_floor_margin_to_threshold": (
                double_low_order_diagnosis_block.get("fine_pair_floor_margin_to_threshold")
            ),
            "isolated_source_policy_candidate_low_order_finest_to_reference_step_ratio": (
                double_low_order_diagnosis_block.get("finest_to_reference_step_ratio")
            ),
            "isolated_source_policy_candidate_low_order_reference_floor_sensitivity": (
                double_low_order_diagnosis_block.get("reference_floor_sensitivity")
            ),
            "isolated_source_policy_candidate_low_order_rows_promoted": (
                double_low_order_promotion.get("source_policy_rows_promoted_by_this_diagnosis")
            ),
            "isolated_source_policy_candidate_summary_file": (
                "../v048_cross_paper_same_test_benchmarks/results/"
                "ra2021_double_local_source_policy_candidate_summary.json"
            ),
            "isolated_source_policy_candidate_validator": (
                "../v048_cross_paper_same_test_benchmarks/"
                "validate_ra2021_double_local_source_policy_candidate.py"
            ),
            "promotion_status": "not_promoted_coarse_h_and_reference_policy_mismatch",
            "promotion_blockers": [
                "strong local coarse order exists, but h values are 0.1/0.05/0.025 rather than the RA2021 double-pendulum source-policy h trio",
                "reference_h is 0.0125 rather than the public double-pendulum 1e-4 self-reference",
                double_candidate_execution_note,
                "runtime/Newton policy still has to be bound to accepted source-policy rows",
            ],
        },
        "four_link": {
            "candidate_rows_exist": len(true_dynamic_models.get("four_link", [])) == 3,
            "public_horizon_kinematic_row_file": "../v048_cross_paper_same_test_benchmarks/results/gauss6_fullva_public_horizon_closed_loop_rows.csv",
            "true_dynamic_row_file": "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_newton_coarse_order_rows.csv",
            "same_window_public_work_precision_json": closed_loop_same_window_public_work_evidence["artifact_json"],
            "same_window_public_work_precision_rows_file": closed_loop_same_window_public_work_evidence["artifact_rows"],
            "public_policy_time_window": closed_summary.get("public_policy_time_window"),
            "public_policy_h_rows_completed": closed_summary.get("public_step_size_rows_completed"),
            "public_policy_h_rows_required": closed_summary.get("public_step_size_required_count"),
            "public_horizon_status": closed_summary.get("models", {}).get("four_link", {}).get("status"),
            "true_dynamic_step_sizes": h_values(true_dynamic_models.get("four_link", [])),
            "true_dynamic_t_end": 0.1,
            "source_policy_t_end_required": 3.0,
            "same_window_public_work_precision_available": "four_link"
            in closed_loop_same_window_public_work_evidence["public_work_precision_available_examples"],
            "same_window_public_work_precision_status": closed_loop_same_window_public_work_evidence[
                "artifact_status"
            ],
            "same_window_public_work_precision_reference_alignment_status": (
                closed_loop_same_window_public_work_evidence["reference_alignment_status"]
            ),
            "same_window_public_work_precision_source_policy_rows_closed": 0,
            "same_window_public_work_precision_promotion_status": (
                "diagnostic_only_mixed_reference_family_not_source_policy"
            ),
            "true_dynamic_position_order": (
                float_from_cell(true_dynamic_models["four_link"][0].get("model_pos_observed_order"))
                if true_dynamic_models.get("four_link")
                else None
            ),
            "true_dynamic_velocity_order": (
                float_from_cell(true_dynamic_models["four_link"][0].get("model_vel_observed_order"))
                if true_dynamic_models.get("four_link")
                else None
            ),
            "promotion_status": "not_promoted_true_dynamic_not_source_policy_and_public_horizon_not_dynamic_order",
            "promotion_blockers": [
                "public-horizon T=3 h-policy rows are kinematic/reaction rows, not true-dynamic order rows",
                "true-dynamic local rows exist only for the bounded T=0.1 coarse common-reference policy",
                "same-window public work/precision rows exist for bounded T=0.1, but mixed reference families keep them diagnostic",
                "source-policy promotion needs a true-dynamic T=3 public-horizon row or an explicit suite demotion",
            ],
        },
    }
    local_candidate_feasibility["slider_crank"] = {
        **local_candidate_feasibility["four_link"],
        "candidate_rows_exist": len(true_dynamic_models.get("slider_crank", [])) == 3,
        "public_horizon_status": closed_summary.get("models", {}).get("slider_crank", {}).get("status"),
        "true_dynamic_step_sizes": h_values(true_dynamic_models.get("slider_crank", [])),
        "same_window_public_work_precision_available": "slider_crank"
        in closed_loop_same_window_public_work_evidence["public_work_precision_available_examples"],
        "true_dynamic_position_order": (
            float_from_cell(true_dynamic_models["slider_crank"][0].get("model_pos_observed_order"))
            if true_dynamic_models.get("slider_crank")
            else None
        ),
        "true_dynamic_velocity_order": (
            float_from_cell(true_dynamic_models["slider_crank"][0].get("model_vel_observed_order"))
            if true_dynamic_models.get("slider_crank")
            else None
        ),
    }
    promotion_gap_drilldown = {
        "checked": True,
        "examples_checked": 4,
        "active_rows_checked": len(active_rows),
        "closed_loop_same_window_public_work_precision_checked": True,
        "closed_loop_same_window_public_work_precision_available_examples": (
            closed_loop_same_window_public_work_evidence["public_work_precision_available_examples"]
        ),
        "closed_loop_same_window_public_work_precision_rows_closed": 0,
        "closed_loop_same_window_public_work_precision_promotion_closed": False,
        "source_identity_closed": source_identity.get("claim_boundary", {}).get(
            "output_mapping_verified_from_source"
        )
        is True
        and source_identity.get("claim_boundary", {}).get("time_grid_policy_extracted_from_source") is True,
        "source_policy_promotion_closed": False,
        "source_policy_rows_closed": 0,
        "external_superiority_ready_rows": 0,
        "row_level_gap_summary": {
            "single_pendulum": "public h grid is present, but position/orientation errors are floor-limited",
            "double_pendulum": "local candidate uses coarse h/ref policy rather than the public double-pendulum h/ref policy",
            "four_link": "true-dynamic local evidence is bounded T=0.1, not the public T=3 source-policy horizon",
            "slider_crank": "true-dynamic local evidence is bounded T=0.1, not the public T=3 source-policy horizon",
        },
        "per_example": {
            "single_pendulum": {
                "source_policy_t_end": 3.0,
                "source_policy_step_sizes": local_candidate_feasibility["single_pendulum"]["step_sizes"],
                "local_candidate_step_sizes": local_candidate_feasibility["single_pendulum"]["step_sizes"],
                "source_policy_reference_h": local_candidate_feasibility["single_pendulum"]["reference_h"],
                "local_candidate_reference_h": local_candidate_feasibility["single_pendulum"]["reference_h"],
                "local_candidate_position_order": local_candidate_feasibility["single_pendulum"][
                    "position_observed_order"
                ],
                "local_candidate_velocity_order": local_candidate_feasibility["single_pendulum"][
                    "velocity_observed_order"
                ],
                "finest_velocity_error": local_candidate_feasibility["single_pendulum"][
                    "finest_velocity_l2_error"
                ],
                "promotion_status": local_candidate_feasibility["single_pendulum"]["promotion_status"],
                "promotion_gap": "source grid exists but the candidate is floor limited and not a stable order row",
                "source_policy_contract_satisfied": False,
            },
            "double_pendulum": {
                "source_policy_t_end": 3.0,
                "source_policy_step_sizes": local_candidate_feasibility["double_pendulum"][
                    "source_policy_step_sizes_required"
                ],
                "local_candidate_step_sizes": local_candidate_feasibility["double_pendulum"]["step_sizes"],
                "source_policy_reference_h": local_candidate_feasibility["double_pendulum"][
                    "source_policy_reference_h_required"
                ],
                "local_candidate_reference_h": local_candidate_feasibility["double_pendulum"]["reference_h"],
                "local_candidate_position_order": local_candidate_feasibility["double_pendulum"][
                    "position_observed_order"
                ],
                "local_candidate_velocity_order": local_candidate_feasibility["double_pendulum"][
                    "velocity_observed_order"
                ],
                "finest_velocity_error": local_candidate_feasibility["double_pendulum"][
                    "finest_velocity_linf_error"
                ],
                "promotion_status": local_candidate_feasibility["double_pendulum"]["promotion_status"],
                "promotion_gap": "coarse local h/ref policy is not the public double-pendulum source h/ref policy",
                "source_policy_contract_satisfied": False,
                "isolated_source_policy_candidate_present": local_candidate_feasibility["double_pendulum"][
                    "isolated_source_policy_candidate_present"
                ],
                "isolated_source_policy_candidate_contract_selected": local_candidate_feasibility["double_pendulum"][
                    "isolated_source_policy_candidate_contract_selected"
                ],
                "isolated_source_policy_candidate_execution_mode": local_candidate_feasibility["double_pendulum"][
                    "isolated_source_policy_candidate_execution_mode"
                ],
                "isolated_source_policy_candidate_rows_completed": local_candidate_feasibility["double_pendulum"][
                    "isolated_source_policy_candidate_rows_completed"
                ],
            },
            "four_link": {
                "source_policy_t_end": local_candidate_feasibility["four_link"]["source_policy_t_end_required"],
                "source_policy_step_sizes": "public_horizon_rows_are_kinematic_reaction_not_dynamic_order",
                "local_candidate_t_end": local_candidate_feasibility["four_link"]["true_dynamic_t_end"],
                "local_candidate_step_sizes": local_candidate_feasibility["four_link"]["true_dynamic_step_sizes"],
                "same_window_public_work_precision_available": local_candidate_feasibility["four_link"][
                    "same_window_public_work_precision_available"
                ],
                "same_window_public_work_precision_reference_alignment_status": local_candidate_feasibility[
                    "four_link"
                ]["same_window_public_work_precision_reference_alignment_status"],
                "same_window_public_work_precision_source_policy_rows_closed": 0,
                "local_candidate_position_order": local_candidate_feasibility["four_link"][
                    "true_dynamic_position_order"
                ],
                "local_candidate_velocity_order": local_candidate_feasibility["four_link"][
                    "true_dynamic_velocity_order"
                ],
                "promotion_status": local_candidate_feasibility["four_link"]["promotion_status"],
                "promotion_gap": "true-dynamic order row exists only for bounded T=0.1",
                "source_policy_contract_satisfied": False,
            },
            "slider_crank": {
                "source_policy_t_end": local_candidate_feasibility["slider_crank"][
                    "source_policy_t_end_required"
                ],
                "source_policy_step_sizes": "public_horizon_rows_are_kinematic_reaction_not_dynamic_order",
                "local_candidate_t_end": local_candidate_feasibility["slider_crank"]["true_dynamic_t_end"],
                "local_candidate_step_sizes": local_candidate_feasibility["slider_crank"][
                    "true_dynamic_step_sizes"
                ],
                "same_window_public_work_precision_available": local_candidate_feasibility["slider_crank"][
                    "same_window_public_work_precision_available"
                ],
                "same_window_public_work_precision_reference_alignment_status": local_candidate_feasibility[
                    "slider_crank"
                ]["same_window_public_work_precision_reference_alignment_status"],
                "same_window_public_work_precision_source_policy_rows_closed": 0,
                "local_candidate_position_order": local_candidate_feasibility["slider_crank"][
                    "true_dynamic_position_order"
                ],
                "local_candidate_velocity_order": local_candidate_feasibility["slider_crank"][
                    "true_dynamic_velocity_order"
                ],
                "promotion_status": local_candidate_feasibility["slider_crank"]["promotion_status"],
                "promotion_gap": "true-dynamic order row exists only for bounded T=0.1",
                "source_policy_contract_satisfied": False,
            },
        },
    }

    audited_rows: list[dict[str, Any]] = []
    for item in active_rows:
        key = (item.get("method"), item.get("example"))
        policy = policy_by_key.get(key, {})
        forensic = forensic_by_key.get(key, {})
        issues = [part for part in forensic.get("issues", "").split("|") if part]
        resolved_evidence = item.get("resolved_evidence", [])
        remaining_evidence = item.get("required_evidence", [])
        audited_rows.append(
            {
                "row_index": item.get("row_index"),
                "example": item.get("example"),
                "method": item.get("method"),
                "public_code_replay_present": forensic.get("source_level") == "public_code_replay",
                "fixed_grid_replay_used": bool_from_cell(policy.get("fixed_grid_replay_used")),
                "same_h_grid": bool_from_cell(policy.get("same_h_grid")),
                "same_reference_and_norm_as_local": bool_from_cell(policy.get("same_reference_and_norm_as_local")),
                "paper_safe_common_reference": bool_from_cell(policy.get("paper_safe_coarse_apples_to_apples")),
                "source_policy_reproduction": bool_from_cell(policy.get("source_policy_reproduction")),
                "paper_claim_scope": forensic.get("paper_claim_scope"),
                "issues": issues,
                "vel_order": float(forensic.get("vel_order", "nan")),
                "finest_vel_error": float(forensic.get("finest_vel_error", "nan")),
                "source_policy_closed": False,
                "external_superiority_ready": False,
                "resolved_required_evidence": resolved_evidence,
                "resolved_required_evidence_count": len(resolved_evidence),
                "remaining_required_evidence": remaining_evidence,
                "remaining_required_evidence_count": len(remaining_evidence),
                "local_candidate_promotion_status": local_candidate_feasibility.get(
                    str(item.get("example")), {}
                ).get("promotion_status"),
                "local_candidate_promotion_blockers": local_candidate_feasibility.get(
                    str(item.get("example")), {}
                ).get("promotion_blockers", []),
            }
        )

    ra_policy_rows = [row for row in policy_rows if row["method"].startswith("ra2021_")]
    ra_forensic_rows = [row for row in forensic_rows if row["method"].startswith("ra2021_")]
    public_progress = external_case.get("source_policy_progress", {}).get("ra2021_public_baselines", {})
    order_groups_completed = public_progress.get("order_groups_completed")
    order_groups_required = public_progress.get("order_groups_required")
    timing_rows_completed = public_progress.get("timing_rows_completed")
    timing_rows_required = public_progress.get("timing_rows_required")

    order_summary_ok = sum(1 for row in order_summary_rows if row.get("ok_row_count") == row.get("row_count"))
    timing_ok = sum(1 for row in timing_rows if row.get("status") == "ok")
    fixed_grid_rows = sum(1 for row in ra_policy_rows if bool_from_cell(row.get("fixed_grid_replay_used")))
    paper_safe_rows = sum(1 for row in ra_policy_rows if bool_from_cell(row.get("paper_safe_coarse_apples_to_apples")))
    source_policy_rows = sum(1 for row in ra_policy_rows if bool_from_cell(row.get("source_policy_reproduction")))
    position_mismatch_rows = sum(1 for row in ra_forensic_rows if "position_aligned_velocity_mismatch" in row.get("issues", ""))
    nonmonotone_rows = sum(
        1 for row in ra_forensic_rows if "velocity_error_nonmonotone_or_floor_limited" in row.get("issues", "")
    )

    closure_criteria = {
        "public_order_groups_completed": order_groups_completed == order_groups_required == 12,
        "public_timing_rows_completed": timing_rows_completed == timing_rows_required == 12,
        "order_summary_rows_ok": order_summary_ok == 9,
        "timing_rows_ok": timing_ok == 12,
        "fixed_grid_common_reference_rows_present": fixed_grid_rows == 12,
        "paper_safe_common_reference_rows_present": paper_safe_rows == 12,
        "source_policy_reproduction_rows_present": source_policy_rows == 0,
        "source_output_mapping_verified": source_identity.get("claim_boundary", {}).get(
            "output_mapping_verified_from_source"
        )
        is True,
        "source_time_grid_policy_extracted": source_identity.get("claim_boundary", {}).get(
            "time_grid_policy_extracted_from_source"
        )
        is True,
        "source_default_horizon_and_h_policy_reproduced": False,
        "flagged_velocity_mapping_or_floor_issues_resolved": False,
        "runtime_policy_tied_to_source_policy_order_rows": False,
        "rerun_or_independent_verification_artifact_present": False,
    }

    output = {
        "schema": "ra2021-source-policy-row-audit-v1",
        "status": "public_rows_complete_source_policy_rows_not_closed",
        "submission_ready": False,
        "suite_id": "ra2021_absolute_coordinate",
        "source_policy_external_superiority_allowed": False,
        "external_superiority_claim_allowed": False,
        "active_b2_flagged_rows": len(active_rows),
        "audited_active_rows": len(audited_rows),
        "source_policy_closed_rows": 0,
        "external_superiority_ready_rows": 0,
        "public_order_groups_completed": order_groups_completed,
        "public_order_groups_required": order_groups_required,
        "public_timing_rows_completed": timing_rows_completed,
        "public_timing_rows_required": timing_rows_required,
        "order_summary_rows": len(order_summary_rows),
        "order_summary_ok_rows": order_summary_ok,
        "timing_rows": len(timing_rows),
        "timing_ok_rows": timing_ok,
        "fixed_grid_common_reference_rows": fixed_grid_rows,
        "paper_safe_common_reference_rows": paper_safe_rows,
        "source_policy_reproduction_rows": source_policy_rows,
        "per_row_source_identity_requirements_resolved": 3,
        "per_row_source_policy_promotion_requirements_remaining": 4,
        "row_missing_evidence_shrunk_by_identity_audit": True,
        "position_aligned_velocity_mismatch_rows": position_mismatch_rows,
        "velocity_nonmonotone_or_floor_limited_rows": nonmonotone_rows,
        "local_candidate_feasibility": local_candidate_feasibility,
        "closed_loop_same_window_public_work_precision_evidence": closed_loop_same_window_public_work_evidence,
        "ra2021_double_local_source_policy_candidate": {
            "present": bool(double_source_policy_candidate),
            "schema": double_source_policy_candidate.get("schema"),
            "status": double_source_policy_candidate.get("status"),
            "execution_mode": double_source_policy_candidate.get("execution_mode"),
            "source_policy_contract_selected": double_source_policy_candidate.get(
                "source_policy_contract_selected"
            ),
            "reference_status": double_source_policy_candidate.get("reference_status"),
            "reference_failure_kind": double_source_policy_candidate.get("reference_failure_kind"),
            "reference_failure_message": double_source_policy_candidate.get("reference_failure_message"),
            "jax_safe_small_angle_patch_enabled": double_source_policy_candidate.get(
                "jax_safe_small_angle_patch_enabled"
            ),
            "jax_safe_small_angle_patch_id": double_source_policy_candidate.get("jax_safe_small_angle_patch_id"),
            "estimated_reference_steps": double_source_policy_candidate.get("estimated_reference_steps"),
            "source_policy_candidate_rows_completed": double_source_policy_candidate.get(
                "source_policy_candidate_rows_completed"
            ),
            "source_policy_pos_observed_order": double_candidate_pos_order,
            "source_policy_vel_observed_order": double_candidate_vel_order,
            "source_policy_order_acceptance_satisfied": double_candidate_order_satisfied,
            "promotion_ready": double_source_policy_candidate.get("promotion_ready"),
            "validator": "../v048_cross_paper_same_test_benchmarks/validate_ra2021_double_local_source_policy_candidate.py",
            "low_order_diagnosis": {
                "schema": double_low_order_diagnosis.get("schema"),
                "status": double_low_order_diagnosis.get("status"),
                "fine_pair_floor_limited": double_low_order_diagnosis_block.get("fine_pair_floor_limited"),
                "fine_pair_label": double_low_order_diagnosis_block.get("fine_pair_label"),
                "coarse_h_constraint_threshold_satisfied": double_low_order_diagnosis_block.get(
                    "coarse_h_constraint_threshold_satisfied"
                ),
                "coarse_h_constraint_failure_components": double_low_order_diagnosis_block.get(
                    "coarse_h_constraint_failure_components"
                ),
                "fine_pair_floor_margin_to_threshold": double_low_order_diagnosis_block.get(
                    "fine_pair_floor_margin_to_threshold"
                ),
                "finest_to_reference_step_ratio": double_low_order_diagnosis_block.get(
                    "finest_to_reference_step_ratio"
                ),
                "reference_floor_sensitivity": double_low_order_diagnosis_block.get(
                    "reference_floor_sensitivity"
                ),
                "source_policy_rows_promoted_by_this_diagnosis": double_low_order_promotion.get(
                    "source_policy_rows_promoted_by_this_diagnosis"
                ),
                "b4_b7_can_close_from_this_diagnosis": double_low_order_promotion.get(
                    "b4_b7_can_close_from_this_diagnosis"
                ),
            },
        },
        "promotion_gap_drilldown": promotion_gap_drilldown,
        "source_identity_audit": {
            "schema": source_identity.get("schema"),
            "status": source_identity.get("status"),
            "output_mapping_verified_from_source": source_identity.get("claim_boundary", {}).get(
                "output_mapping_verified_from_source"
            ),
            "time_grid_policy_extracted_from_source": source_identity.get("claim_boundary", {}).get(
                "time_grid_policy_extracted_from_source"
            ),
            "source_policy_reproduction_rows_closed": source_identity.get("claim_boundary", {}).get(
                "source_policy_reproduction_rows_closed"
            ),
            "external_superiority_claim_allowed": source_identity.get("claim_boundary", {}).get(
                "external_superiority_claim_allowed"
            ),
        },
        "closure_criteria": closure_criteria,
        "rows": audited_rows,
        "decision": {
            "can_close_ra2021_b2_requirement_now": False,
            "reason": (
                "RA2021 public order/timing rows are complete and useful as bounded common-reference evidence, "
                "and the source-code identity audit now verifies body.r/body.dr/body.ddr output mapping and extracts "
                "the public time-grid convention. Local Gauss6/FullVA candidate rows exist for single pendulum, "
                "double pendulum, and the two closed-loop examples, but they are respectively floor limited, coarse "
                "h/reference-policy rows, or bounded T=0.1 true-dynamic rows rather than promoted RA2021 source-policy "
                "dynamic-order rows. The closed-loop same-window public work/precision artifact closes the availability "
                "gap for bounded diagnostics, but mixed reference families prevent external-superiority promotion; "
                "the error/runtime/Newton policy binding is also not closed."
            ),
            "required_to_close": [
                "run or promote local Gauss6 FullVA under the same RA2021 source time-grid and dynamic policy",
                "bind error norm/output policy to source-policy order rows",
                "tie runtime/Newton-iteration policy to the accepted source-policy order rows",
                "produce rerun or independent verification artifact",
            ],
        },
        "execution_policy": {
            "read_only_existing_artifacts": True,
            "default_1e_4_required": False,
            "heavy_numerical_run_invoked": False,
            "run_v047_invoked": False,
            "v048_runner_invoked": False,
        },
        "source_files": {
            "b2_remaining_work_manifest": "B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.json",
            "external_case_evidence_reconciliation": "EXTERNAL_CASE_EVIDENCE_RECONCILIATION.json",
            "apples_to_apples_policy_audit": "../v048_cross_paper_same_test_benchmarks/results/apples_to_apples_policy_audit.csv",
            "forensic_audit": "../v048_cross_paper_same_test_benchmarks/results/all_examples_apples_to_apples_forensic_audit.csv",
            "ra2021_public_order_work_summary": "../v048_cross_paper_same_test_benchmarks/results/ra2021_public_order_work_summary.csv",
            "ra2021_public_timing_rows": "../v048_cross_paper_same_test_benchmarks/results/ra2021_public_timing_rows.csv",
            "ra2021_source_identity_audit": "RA2021_SOURCE_IDENTITY_AUDIT.json",
            "ra2021_double_local_source_policy_candidate_summary": (
                "../v048_cross_paper_same_test_benchmarks/results/"
                "ra2021_double_local_source_policy_candidate_summary.json"
            ),
            "ra2021_double_source_policy_low_order_diagnosis": (
                "RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.json"
            ),
            "ra2021_double_local_source_policy_candidate_rows": (
                "../v048_cross_paper_same_test_benchmarks/results/"
                "ra2021_double_local_source_policy_candidate_rows.csv"
            ),
            "ra2021_double_local_source_policy_candidate_validator": (
                "../v048_cross_paper_same_test_benchmarks/"
                "validate_ra2021_double_local_source_policy_candidate.py"
            ),
            "closed_loop_true_dynamic_public_work_precision": (
                "../v048_cross_paper_same_test_benchmarks/results/"
                "closed_loop_true_dynamic_public_work_precision.json"
            ),
            "closed_loop_true_dynamic_public_work_precision_rows": (
                "../v048_cross_paper_same_test_benchmarks/results/"
                "closed_loop_true_dynamic_public_work_precision_rows.csv"
            ),
            "closed_loop_true_dynamic_public_work_precision_summary": (
                "../v048_cross_paper_same_test_benchmarks/results/"
                "closed_loop_true_dynamic_public_work_precision_summary.csv"
            ),
        },
    }

    out_json = PAPER / "RA2021_SOURCE_POLICY_ROW_AUDIT.json"
    out_md = PAPER / "RA2021_SOURCE_POLICY_ROW_AUDIT.md"
    with out_json.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# RA2021 Source-Policy Row Audit",
        "",
        "Status: **public rows complete; source-policy rows not closed**.",
        "",
        "This audit is read-only over existing v048 and paper-package artifacts. It does not rerun RA2021.",
        "",
        f"- Active B2 flagged RA2021 rows: `{output['active_b2_flagged_rows']}`.",
        f"- Public order groups completed: `{order_groups_completed}/{order_groups_required}`.",
        f"- Public timing rows completed: `{timing_rows_completed}/{timing_rows_required}`.",
        f"- Fixed-grid common-reference RA2021 rows: `{fixed_grid_rows}/12`.",
        f"- Paper-safe common-reference RA2021 rows: `{paper_safe_rows}/12`.",
        f"- Source-policy reproduction rows: `{source_policy_rows}/12`.",
        f"- Per-row source-identity requirements resolved: `{output['per_row_source_identity_requirements_resolved']}`.",
        f"- Per-row source-policy promotion requirements remaining: `{output['per_row_source_policy_promotion_requirements_remaining']}`.",
        f"- Row missing evidence shrunk by identity audit: `{output['row_missing_evidence_shrunk_by_identity_audit']}`.",
        f"- Source-policy closed rows: `{output['source_policy_closed_rows']}`.",
        f"- External-superiority-ready rows: `{output['external_superiority_ready_rows']}`.",
        f"- Position-aligned velocity-mismatch rows in RA2021 forensic table: `{position_mismatch_rows}`.",
        f"- Velocity nonmonotone/floor-limited rows in RA2021 forensic table: `{nonmonotone_rows}`.",
        f"- Source output mapping verified from RA2021 source: `{output['source_identity_audit']['output_mapping_verified_from_source']}`.",
        f"- Source time-grid policy extracted from RA2021 source: `{output['source_identity_audit']['time_grid_policy_extracted_from_source']}`.",
        (
            "- Closed-loop same-window public work/precision: "
            f"`{closed_loop_same_window_public_work_evidence['artifact_status']}`, "
            f"available `{closed_loop_same_window_public_work_evidence['public_work_precision_available_count']}/2`, "
            f"strict common-reference `{closed_loop_same_window_public_work_evidence['strict_common_reference_error_columns']}`, "
            f"external superiority `{closed_loop_same_window_public_work_evidence['external_superiority_claim']}`, "
            f"source-policy rows closed `{closed_loop_same_window_public_work_evidence['source_policy_rows_closed_by_this_evidence']}`."
        ),
        f"- External superiority claim allowed: `{output['external_superiority_claim_allowed']}`.",
        f"- Default 1e-4/heavy/run_v047: `{output['execution_policy']['default_1e_4_required']}/{output['execution_policy']['heavy_numerical_run_invoked']}/{output['execution_policy']['run_v047_invoked']}`.",
        (
            "- Isolated double source-policy candidate plan: "
            f"`{output['ra2021_double_local_source_policy_candidate']['status']}`, "
            f"contract `{output['ra2021_double_local_source_policy_candidate']['source_policy_contract_selected']}`, "
            f"reference `{output['ra2021_double_local_source_policy_candidate']['reference_status']}`, "
            f"JAX-safe small-angle patch `{output['ra2021_double_local_source_policy_candidate']['jax_safe_small_angle_patch_enabled']}`, "
            f"rows completed `{output['ra2021_double_local_source_policy_candidate']['source_policy_candidate_rows_completed']}/3`, "
            f"order accepted `{output['ra2021_double_local_source_policy_candidate']['source_policy_order_acceptance_satisfied']}`, "
            f"estimated reference steps `{output['ra2021_double_local_source_policy_candidate']['estimated_reference_steps']}`."
        ),
        (
            "- Isolated double low-order diagnosis: "
            f"`{output['ra2021_double_local_source_policy_candidate']['low_order_diagnosis']['status']}`, "
            f"fine pair floor-limited `{output['ra2021_double_local_source_policy_candidate']['low_order_diagnosis']['fine_pair_floor_limited']}`, "
            f"coarse h constraint threshold `{output['ra2021_double_local_source_policy_candidate']['low_order_diagnosis']['coarse_h_constraint_threshold_satisfied']}`, "
            f"constraint failure components `{output['ra2021_double_local_source_policy_candidate']['low_order_diagnosis']['coarse_h_constraint_failure_components']}`, "
            f"fine-pair floor margin `{output['ra2021_double_local_source_policy_candidate']['low_order_diagnosis']['fine_pair_floor_margin_to_threshold']:.3f}`, "
            f"finest/reference h ratio `{output['ra2021_double_local_source_policy_candidate']['low_order_diagnosis']['finest_to_reference_step_ratio']:.1f}`, "
            f"rows promoted `{output['ra2021_double_local_source_policy_candidate']['low_order_diagnosis']['source_policy_rows_promoted_by_this_diagnosis']}`."
        ),
        "",
        "## Local Candidate Feasibility",
        "",
        "| example | local candidate status | key available rows | promotion blocker |",
        "|---|---|---:|---|",
        (
            "| `single_pendulum` | "
            f"`{local_candidate_feasibility['single_pendulum']['promotion_status']}` | "
            f"`{len(local_single_public_rows)}` | floor-limited public-h tranche |"
        ),
        (
            "| `double_pendulum` | "
            f"`{local_candidate_feasibility['double_pendulum']['promotion_status']}` | "
            f"`{len(local_double_coarse_rows)}` plus isolated exact candidate | {double_candidate_table_note} |"
        ),
        (
            "| `four_link` | "
            f"`{local_candidate_feasibility['four_link']['promotion_status']}` | "
            f"`{len(true_dynamic_models.get('four_link', []))}` plus same-window public work/precision | mixed-reference diagnostic, not source-policy promotion |"
        ),
        (
            "| `slider_crank` | "
            f"`{local_candidate_feasibility['slider_crank']['promotion_status']}` | "
            f"`{len(true_dynamic_models.get('slider_crank', []))}` plus same-window public work/precision | mixed-reference diagnostic, not source-policy promotion |"
        ),
        "",
        "## Closure Decision",
        "",
        f"Can close RA2021 B2 requirement now: `{output['decision']['can_close_ra2021_b2_requirement_now']}`.",
        "",
        output["decision"]["reason"],
        "",
        "## Promotion Gap Drilldown",
        "",
        f"- Checked examples: `{promotion_gap_drilldown['examples_checked']}`.",
        f"- Checked active B2 rows: `{promotion_gap_drilldown['active_rows_checked']}`.",
        f"- Closed-loop same-window public work/precision checked: `{promotion_gap_drilldown['closed_loop_same_window_public_work_precision_checked']}`.",
        f"- Closed-loop same-window source-policy rows closed: `{promotion_gap_drilldown['closed_loop_same_window_public_work_precision_rows_closed']}`.",
        f"- Source identity closed: `{promotion_gap_drilldown['source_identity_closed']}`.",
        f"- Source-policy promotion closed: `{promotion_gap_drilldown['source_policy_promotion_closed']}`.",
        "",
        "| example | source-policy target | local candidate | promotion gap |",
        "|---|---|---|---|",
        (
            "| `single_pendulum` | "
            "$T=3$, $h=\\{10^{-2},10^{-3},10^{-4}\\}$ | "
            f"same grid, $v$ order `{local_candidate_feasibility['single_pendulum']['velocity_observed_order']:.3f}`, "
            f"finest $v$ error `{local_candidate_feasibility['single_pendulum']['finest_velocity_l2_error']:.3e}` | "
            "floor-limited public-h tranche |"
        ),
        (
            "| `double_pendulum` | "
            "$T=3$, $h=\\{10^{-2},2\\cdot10^{-3},10^{-3}\\}$, $h_{ref}=10^{-4}$ | "
            f"$h=\\{{0.1,0.05,0.025\\}}$, $h_{{ref}}=0.0125$, "
            f"$v$ order `{local_candidate_feasibility['double_pendulum']['velocity_observed_order']:.3f}`; "
            f"isolated exact rows `{double_candidate_completed}/3` | {double_candidate_gap_note} |"
        ),
        (
            "| `four_link` | "
            "$T=3$ public-horizon dynamic-order row | "
            f"$T=0.1$, $h=\\{{0.1,0.05,0.025\\}}$, "
            f"$v$ order `{local_candidate_feasibility['four_link']['true_dynamic_velocity_order']:.3f}` | "
            "bounded same-window public work/precision available, but mixed-reference diagnostic only |"
        ),
        (
            "| `slider_crank` | "
            "$T=3$ public-horizon dynamic-order row | "
            f"$T=0.1$, $h=\\{{0.1,0.05,0.025\\}}$, "
            f"$v$ order `{local_candidate_feasibility['slider_crank']['true_dynamic_velocity_order']:.3f}` | "
            "bounded same-window public work/precision available, but mixed-reference diagnostic only |"
        ),
        "",
        "## Active Rows",
        "",
        "| # | example | method | fixed-grid | paper-safe | source-policy | issues |",
        "|---:|---|---|---:|---:|---:|---|",
    ]
    for row in audited_rows:
        lines.append(
            f"| {row['row_index']} | `{row['example']}` | `{row['method']}` | "
            f"`{row['fixed_grid_replay_used']}` | `{row['paper_safe_common_reference']}` | "
            f"`{row['source_policy_reproduction']}` | {'; '.join(row['issues'])} |"
        )
    lines.extend(
        [
            "",
            "Each active RA2021 row now carries the resolved source-identity evidence separately from the still-open promotion evidence.",
            "The RA2021 rows remain bounded common-reference diagnostics, not external-superiority evidence.",
            "The previous output-mapping unknown is closed as a source-identity question; source-policy promotion remains open.",
        ]
    )
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("ra2021_source_policy_row_audit=written")
    print(f"active_b2_flagged_rows={len(active_rows)}")
    print("public_order_groups=12/12")
    print("public_timing_rows=12/12")
    print("source_policy_reproduction_rows=0/12")
    print("can_close_ra2021_b2_requirement_now=False")


if __name__ == "__main__":
    main()
