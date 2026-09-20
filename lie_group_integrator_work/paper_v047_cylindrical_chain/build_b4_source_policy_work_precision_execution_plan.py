#!/usr/bin/env python3
"""Build the B4 source-policy work/precision execution plan from existing artifacts."""

from __future__ import annotations

import json
import math
import csv
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
V048 = PAPER.parent / "v048_cross_paper_same_test_benchmarks"
RA2021_DOUBLE_ORDER_FORMS = ("rA", "rp", "reps")


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def pair_orders(rows: list[dict[str, str]], metric: str) -> list[float]:
    pairs = sorted(
        [(float(row["h"]), float(row[metric])) for row in rows if row.get("status") == "ok"],
        reverse=True,
    )
    orders: list[float] = []
    for (h0, e0), (h1, e1) in zip(pairs, pairs[1:]):
        orders.append(math.log(e0 / e1) / math.log(h0 / h1))
    return orders


def finite_float_values(rows: list[dict[str, str]], key: str) -> list[float]:
    values: list[float] = []
    for row in rows:
        try:
            value = float(row[key])
        except (KeyError, TypeError, ValueError):
            continue
        if math.isfinite(value):
            values.append(value)
    return values


def summarize_executed_ra2021_shard(form: str) -> dict[str, Any]:
    shard_label = (
        "../v048_cross_paper_same_test_benchmarks/results/ra2021_double_order_shards/"
        f"{form}_double_pendulum_0p0001.csv"
    )
    shard_path = manuscript_path(shard_label)
    rows = read_csv(shard_path.resolve())
    ok_rows = [row for row in rows if row.get("status") == "ok"]
    h_values = [float(row["h"]) for row in rows] if rows else []
    return {
        "path": shard_label,
        "exists": shard_path.exists() and shard_path.stat().st_size > 0,
        "form": form,
        "row_count": len(rows),
        "ok_row_count": len(ok_rows),
        "source_suite": sorted({row.get("source_suite") for row in rows if row.get("source_suite")}),
        "model": sorted({row.get("model") for row in rows if row.get("model")}),
        "mode": sorted({row.get("mode") for row in rows if row.get("mode")}),
        "h_values": h_values,
        "reference_h_values": sorted({float(row["reference_h"]) for row in rows}) if rows else [],
        "public_double_order_policy_values": sorted({row.get("public_double_order_policy") for row in rows}),
        "runtime_sec_values": [float(row["runtime_sec"]) for row in rows] if rows else [],
        "reference_runtime_sec_values": sorted({float(row["reference_runtime_sec"]) for row in rows}) if rows else [],
        "avg_iteration_values": [float(row["avg_iterations"]) for row in rows] if rows else [],
        "max_iteration_values": [float(row["max_iterations"]) for row in rows] if rows else [],
        "position_pair_orders": pair_orders(rows, "pos_final_linf") if rows else [],
        "velocity_pair_orders": pair_orders(rows, "vel_final_linf") if rows else [],
        "acceleration_pair_orders": pair_orders(rows, "acc_final_linf") if rows else [],
        "counts_as_source_policy_baseline_shard": len(ok_rows) == 3,
    }


def build_executed_ra2021_shard_evidence() -> dict[str, Any]:
    shards = [summarize_executed_ra2021_shard(form) for form in RA2021_DOUBLE_ORDER_FORMS]
    completed_shards = [
        shard
        for shard in shards
        if shard["exists"]
        and shard["ok_row_count"] == 3
        and shard["h_values"] == [0.01, 0.002, 0.001]
        and shard["reference_h_values"] == [0.0001]
        and shard["public_double_order_policy_values"] == ["True"]
    ]
    all_expected_completed = len(completed_shards) == len(RA2021_DOUBLE_ORDER_FORMS)
    source_suites = sorted({suite for shard in shards for suite in shard["source_suite"]})
    models = sorted({model for shard in shards for model in shard["model"]})
    modes = sorted({mode for shard in shards for mode in shard["mode"]})
    reference_h_values = sorted({ref_h for shard in shards for ref_h in shard["reference_h_values"]})
    return {
        "schema": "b4-ra2021-executed-source-policy-shard-evidence-v2",
        "status": (
            "all_public_baseline_source_policy_shards_completed_not_promoted"
            if all_expected_completed
            else "partial_public_baseline_source_policy_shards_not_promoted"
        ),
        "expected_forms": list(RA2021_DOUBLE_ORDER_FORMS),
        "completed_forms": [shard["form"] for shard in completed_shards],
        "expected_form_count": len(RA2021_DOUBLE_ORDER_FORMS),
        "completed_form_count": len(completed_shards),
        "exists": all(shard["exists"] for shard in shards),
        "row_count": sum(shard["row_count"] for shard in shards),
        "ok_row_count": sum(shard["ok_row_count"] for shard in shards),
        "source_suite": source_suites,
        "model": models,
        "mode": modes,
        "shared_h_values": [0.01, 0.002, 0.001] if all_expected_completed else [],
        "reference_h_values": reference_h_values,
        "shards": shards,
        "position_pair_orders_by_form": {
            shard["form"]: shard["position_pair_orders"] for shard in shards if shard["position_pair_orders"]
        },
        "velocity_pair_orders_by_form": {
            shard["form"]: shard["velocity_pair_orders"] for shard in shards if shard["velocity_pair_orders"]
        },
        "acceleration_pair_orders_by_form": {
            shard["form"]: shard["acceleration_pair_orders"] for shard in shards if shard["acceleration_pair_orders"]
        },
        "source_policy_shard_artifacts_present": len(completed_shards) > 0,
        "heavy_numerical_run_invoked": len(completed_shards) > 0,
        "builder_invoked_heavy_numerical_run": False,
        "run_v047_invoked": False,
        "counts_as_source_policy_baseline_shards": all_expected_completed,
        "baseline_source_policy_rows_completed_by_shards": sum(
            shard["ok_row_count"] for shard in completed_shards
        ),
        "counts_as_gauss6_fullva_local_source_policy_row": False,
        "counts_as_complete_work_precision_curve": False,
        "source_policy_rows_closed_by_this_evidence": 0,
        "source_policy_rows_closed_by_this_shard": 0,
        "b4_can_close_from_this_evidence": False,
        "b7_can_close_from_this_evidence": False,
        "b4_can_close_from_this_shard": False,
        "b7_can_close_from_this_shard": False,
        "promotion_gap": [
            "needs matching Gauss6/FullVA local source-policy rows",
            "needs runtime/Newton metrics tied to promoted local rows",
            "needs full RA2021 suite source-policy work/precision figure before B4/B7 closure",
        ],
    }


def summarize_gauss6_csv(path_label: str, model: str | None = None) -> dict[str, Any]:
    path = manuscript_path(path_label)
    rows = read_csv(path.resolve())
    ok_rows = [row for row in rows if row.get("status") == "ok"]
    failed_rows = [row for row in rows if str(row.get("status", "")).startswith("failed")]
    return {
        "path": path_label,
        "exists": path.exists() and path.stat().st_size > 0,
        "model": model or sorted({row.get("model") for row in rows if row.get("model")}),
        "row_count": len(rows),
        "ok_row_count": len(ok_rows),
        "failed_row_count": len(failed_rows),
        "failed_statuses": sorted({row.get("status") for row in failed_rows}),
        "method": sorted({row.get("method") for row in rows if row.get("method")}),
        "row_type": sorted({row.get("row_type") for row in rows if row.get("row_type")}),
        "h_values": [float(row["h"]) for row in rows] if rows else [],
        "reference_h_values": sorted({float(row["reference_h"]) for row in rows}) if rows else [],
        "public_policy_time_window_values": sorted({row.get("public_policy_time_window") for row in rows}),
        "public_policy_h_values": sorted({row.get("public_policy_h") for row in rows}),
        "runtime_sec_values": finite_float_values(rows, "runtime_sec"),
        "total_newton_iteration_values": finite_float_values(rows, "total_newton_iterations"),
        "max_dynamics_residual_norm_values": finite_float_values(rows, "max_dynamics_residual_norm"),
        "notes": rows[0].get("notes") if rows else "",
    }


def build_gauss6_local_source_policy_evidence() -> dict[str, Any]:
    single = summarize_gauss6_csv(
        "../v048_cross_paper_same_test_benchmarks/results/gauss6_fullva_public_horizon_single_rows.csv"
    )
    closed_loop_combined = [
        summarize_gauss6_csv(
            "../v048_cross_paper_same_test_benchmarks/results/public_closed_loop_shards/"
            f"{model}_1em02_1em03_1em04.csv",
            model,
        )
        for model in ("four_link", "slider_crank")
    ]
    closed_loop_legacy_reference_nesting = [
        summarize_gauss6_csv(
            "../v048_cross_paper_same_test_benchmarks/results/public_closed_loop_shards/"
            f"{model}_1em03_1em04.csv",
            model,
        )
        for model in ("four_link", "slider_crank")
    ]
    closed_loop_h1e4 = [
        summarize_gauss6_csv(
            "../v048_cross_paper_same_test_benchmarks/results/public_closed_loop_shards/"
            f"{model}_1em04.csv",
            model,
        )
        for model in ("four_link", "slider_crank")
    ]
    single_complete = (
        single["exists"]
        and single["row_count"] == 3
        and single["ok_row_count"] == 3
        and single["h_values"] == [0.01, 0.001, 0.0001]
        and single["reference_h_values"] == [0.001]
        and single["public_policy_time_window_values"] == ["True"]
        and single["public_policy_h_values"] == ["True"]
    )
    closed_loop_h1e4_ok_count = sum(
        1
        for shard in closed_loop_h1e4
        if shard["exists"] and shard["row_count"] == 1 and shard["ok_row_count"] == 1 and shard["h_values"] == [0.0001]
    )
    combined_ok_rows = sum(shard["ok_row_count"] for shard in closed_loop_combined)
    combined_failed_rows = sum(shard["failed_row_count"] for shard in closed_loop_combined)
    latest_public_step_trios_completed = all(
        shard["exists"]
        and shard["row_count"] == 3
        and shard["ok_row_count"] == 3
        and shard["failed_row_count"] == 0
        and shard["h_values"] == [0.01, 0.001, 0.0001]
        and shard["reference_h_values"] == [0.001]
        and shard["public_policy_time_window_values"] == ["True"]
        and shard["public_policy_h_values"] == ["True"]
        for shard in closed_loop_combined
    )
    legacy_reference_nesting_failed_rows = sum(
        shard["failed_row_count"] for shard in closed_loop_legacy_reference_nesting
    )
    return {
        "schema": "b4-gauss6-local-source-policy-evidence-v1",
        "status": (
            "partial_local_source_policy_evidence_single_complete_closed_loop_residual_only_not_promoted"
            if single_complete
            else "local_source_policy_evidence_incomplete_not_promoted"
        ),
        "single_public_horizon_step_trio_completed": single_complete,
        "single_public_horizon_rows": single,
        "closed_loop_combined_shards": closed_loop_combined,
        "closed_loop_legacy_reference_nesting_shards": closed_loop_legacy_reference_nesting,
        "closed_loop_h1e4_standalone_shards": closed_loop_h1e4,
        "closed_loop_combined_ok_rows": combined_ok_rows,
        "closed_loop_combined_failed_rows": combined_failed_rows,
        "closed_loop_legacy_reference_nesting_failed_rows": legacy_reference_nesting_failed_rows,
        "closed_loop_h1e4_standalone_ok_models": closed_loop_h1e4_ok_count,
        "closed_loop_public_step_trios_completed": latest_public_step_trios_completed,
        "closed_loop_rows_are_dynamic_work_precision": False,
        "counts_as_partial_local_source_policy_evidence": single_complete or closed_loop_h1e4_ok_count > 0,
        "counts_as_b4_accepted_source_policy_rows": False,
        "counts_as_complete_ra2021_work_precision_curve": False,
        "source_policy_rows_closed_by_this_evidence": 0,
        "b4_can_close_from_this_evidence": False,
        "b7_can_close_from_this_evidence": False,
        "promotion_gap": [
            "single-pendulum local rows need matching accepted RA2021 baseline work/error rows in the same figure policy",
            "four-link and slider-crank shards are kinematic reaction/residual rows, not dynamic order/work-superiority rows",
            "closed-loop source-policy step trios are now complete but remain residual/kinematic rows rather than dynamic work/precision rows",
            "legacy h=1e-3/1e-4 shards remain recorded as reference-nesting diagnostics, not promotion evidence",
            "all promoted work/precision curves must bind error/order and runtime/Newton metrics from the same accepted rows",
        ],
    }


def build_ra2021_closed_loop_same_window_public_work_precision_evidence() -> dict[str, Any]:
    summary_label = (
        "../v048_cross_paper_same_test_benchmarks/results/"
        "closed_loop_true_dynamic_public_work_precision.json"
    )
    rows_label = (
        "../v048_cross_paper_same_test_benchmarks/results/"
        "closed_loop_true_dynamic_public_work_precision_rows.csv"
    )
    summary_rows_label = (
        "../v048_cross_paper_same_test_benchmarks/results/"
        "closed_loop_true_dynamic_public_work_precision_summary.csv"
    )
    summary_path = manuscript_path(summary_label)
    rows_path = manuscript_path(rows_label)
    summary_rows_path = manuscript_path(summary_rows_label)
    summary = read_json(summary_path.resolve()) if summary_path.exists() else {}
    rows = read_csv(rows_path.resolve())
    summary_rows = read_csv(summary_rows_path.resolve())
    ok_rows = [row for row in rows if row.get("status") == "ok"]
    model_summaries: dict[str, dict[str, Any]] = {}
    for model in ("four_link", "slider_crank"):
        local_rows = [
            row
            for row in summary_rows
            if row.get("model") == model and row.get("source_suite") == "local_true_dynamic_newton"
        ]
        public_rows = [
            row
            for row in summary_rows
            if row.get("model") == model and row.get("source_suite") == "ra2021_taves_kissel_negrut"
        ]
        local = local_rows[0] if local_rows else {}
        model_summaries[model] = {
            "local_summary_present": bool(local),
            "public_summary_count": len(public_rows),
            "public_methods": sorted(row.get("method") for row in public_rows if row.get("method")),
            "local_pos_observed_order": float(local["pos_observed_order"]) if local else None,
            "local_vel_observed_order": float(local["vel_observed_order"]) if local else None,
            "local_finest_pos_final_linf": float(local["finest_pos_final_linf"]) if local else None,
            "local_finest_vel_final_linf": float(local["finest_vel_final_linf"]) if local else None,
            "local_runtime_sec_sum": float(local["runtime_sec_sum"]) if local else None,
            "local_finest_runtime_ratio_vs_public_rA": (
                float(local["finest_runtime_ratio_vs_public_rA"]) if local else None
            ),
            "accepted_dynamic_order": local.get("accepted_dynamic_order") == "true" if local else False,
            "external_superiority_claim_allowed": (
                local.get("external_superiority_claim_allowed") == "true" if local else False
            ),
            "reference_alignment": local.get("reference_alignment"),
        }
    return {
        "schema": "b4-ra2021-closed-loop-same-window-public-work-precision-evidence-v1",
        "status": summary.get("status"),
        "summary_path": summary_label,
        "rows_path": rows_label,
        "summary_rows_path": summary_rows_label,
        "summary_exists": summary_path.exists() and summary_path.stat().st_size > 0,
        "rows_exists": rows_path.exists() and rows_path.stat().st_size > 0,
        "summary_rows_exists": summary_rows_path.exists() and summary_rows_path.stat().st_size > 0,
        "row_count": len(rows),
        "ok_row_count": len(ok_rows),
        "summary_row_count": len(summary_rows),
        "models": summary.get("models", []),
        "public_forms": summary.get("public_forms", []),
        "t_end": summary.get("t_end"),
        "step_sizes": summary.get("step_sizes", []),
        "reference_h": summary.get("reference_h"),
        "public_work_precision_available_count": summary.get("public_work_precision_available_count"),
        "public_work_precision_available_examples": summary.get("public_work_precision_available_examples", []),
        "public_work_precision_missing_count": summary.get("public_work_precision_missing_count"),
        "local_true_dynamic_order_available_count": summary.get("local_true_dynamic_order_available_count"),
        "strict_common_reference_error_columns": summary.get("strict_common_reference_error_columns"),
        "reference_alignment_status": summary.get("reference_alignment_status"),
        "external_superiority_claim": summary.get("external_superiority_claim"),
        "accepted_external_dynamic_order_examples": summary.get("accepted_external_dynamic_order_examples", []),
        "counts_as_bounded_same_window_diagnostic": (
            summary.get("public_work_precision_available_count") == 2
            and summary.get("strict_common_reference_error_columns") is False
            and summary.get("external_superiority_claim") is False
        ),
        "counts_as_source_policy_reproduction": False,
        "counts_as_b4_accepted_source_policy_rows": False,
        "counts_as_complete_ra2021_work_precision_curve": False,
        "source_policy_rows_closed_by_this_evidence": 0,
        "b4_can_close_from_this_evidence": False,
        "b7_can_close_from_this_evidence": False,
        "promotion_gap": [
            "same-window public work/precision rows are available for four-link and slider-crank",
            "local and public error columns use different reference families",
            "bounded T=0.1 diagnostic rows are not the RA2021 T=3 source-policy dynamic-order rows",
            "source-policy figures still need promoted rows with one reference/output/runtime policy",
        ],
        "model_summaries": model_summaries,
    }


def build_ra2021_double_local_source_policy_candidate_evidence() -> dict[str, Any]:
    summary_label = (
        "../v048_cross_paper_same_test_benchmarks/results/"
        "ra2021_double_local_source_policy_candidate_summary.json"
    )
    rows_label = (
        "../v048_cross_paper_same_test_benchmarks/results/"
        "ra2021_double_local_source_policy_candidate_rows.csv"
    )
    validator_label = "../v048_cross_paper_same_test_benchmarks/validate_ra2021_double_local_source_policy_candidate.py"
    summary_path = manuscript_path(summary_label)
    rows_path = manuscript_path(rows_label)
    validator_path = manuscript_path(validator_label)
    summary = read_json(summary_path.resolve()) if summary_path.exists() else {}
    rows = read_csv(rows_path.resolve())
    ok_rows = [row for row in rows if row.get("status") == "ok"]
    position_pair_orders = pair_orders(rows, "pos_traj_linf") if rows else []
    velocity_pair_orders = pair_orders(rows, "vel_traj_linf") if rows else []
    constraint_threshold_failed_h_values = [
        float(row["h"])
        for row in rows
        if row.get("constraint_threshold_satisfied") == "False"
    ]
    low_order_failure_modes: list[str] = []
    if summary.get("source_policy_order_acceptance_satisfied") is False:
        low_order_failure_modes.append("aggregate_observed_order_below_5p5_threshold")
    if position_pair_orders and min(position_pair_orders) < 5.5:
        low_order_failure_modes.append("position_pair_order_below_5p5_threshold")
    if velocity_pair_orders and min(velocity_pair_orders) < 5.5:
        low_order_failure_modes.append("velocity_pair_order_below_5p5_threshold")
    if constraint_threshold_failed_h_values:
        low_order_failure_modes.append("at_least_one_candidate_row_fails_endpoint_constraint_threshold")
    return {
        "schema": "b4-ra2021-double-local-source-policy-candidate-evidence-v1",
        "status": "executed_order_below_acceptance_not_promoted"
        if summary.get("status") == "executed_isolated_source_policy_candidate"
        else "candidate_missing_or_not_executed",
        "summary_path": summary_label,
        "rows_path": rows_label,
        "validator_path": validator_label,
        "summary_exists": summary_path.exists() and summary_path.stat().st_size > 0,
        "rows_exists": rows_path.exists() and rows_path.stat().st_size > 0,
        "validator_exists": validator_path.exists() and validator_path.stat().st_size > 0,
        "runner_schema": summary.get("schema"),
        "runner_status": summary.get("status"),
        "execution_mode": summary.get("execution_mode"),
        "heavy_numerical_run_invoked": summary.get("heavy_numerical_run_invoked"),
        "builder_invoked_heavy_numerical_run": False,
        "reference_status": summary.get("reference_status"),
        "reference_cache_exists": summary.get("reference_cache_exists"),
        "reference_runtime_sec": summary.get("reference_runtime_sec"),
        "estimated_reference_steps": summary.get("estimated_reference_steps"),
        "source_policy_contract_selected": summary.get("source_policy_contract_selected"),
        "source_policy_time_window_selected": summary.get("source_policy_time_window_selected"),
        "source_policy_step_trio_selected": summary.get("source_policy_step_trio_selected"),
        "source_policy_reference_h_selected": summary.get("source_policy_reference_h_selected"),
        "selected_step_sizes": summary.get("selected_step_sizes"),
        "selected_reference_h": summary.get("selected_reference_h"),
        "selected_t_end": summary.get("selected_t_end"),
        "row_count": len(rows),
        "ok_row_count": len(ok_rows),
        "source_policy_candidate_rows_completed": summary.get("source_policy_candidate_rows_completed"),
        "h_values": [float(row["h"]) for row in rows] if rows else [],
        "runtime_sec_values": finite_float_values(rows, "runtime_sec"),
        "total_newton_iteration_values": finite_float_values(rows, "total_newton_iterations"),
        "max_endpoint_constraint_norm_values": finite_float_values(rows, "max_endpoint_constraint_norm"),
        "max_endpoint_velocity_constraint_norm_values": finite_float_values(
            rows, "max_endpoint_velocity_constraint_norm"
        ),
        "constraint_threshold_satisfied_values": sorted(
            {row.get("constraint_threshold_satisfied") for row in rows if row.get("constraint_threshold_satisfied")}
        ),
        "constraint_threshold_failed_h_values": constraint_threshold_failed_h_values,
        "position_pair_orders": position_pair_orders,
        "velocity_pair_orders": velocity_pair_orders,
        "minimum_position_pair_order": min(position_pair_orders) if position_pair_orders else None,
        "minimum_velocity_pair_order": min(velocity_pair_orders) if velocity_pair_orders else None,
        "finest_pair_position_order": position_pair_orders[-1] if position_pair_orders else None,
        "finest_pair_velocity_order": velocity_pair_orders[-1] if velocity_pair_orders else None,
        "source_policy_order_acceptance_threshold": summary.get("source_policy_order_acceptance_threshold"),
        "source_policy_pos_observed_order": summary.get("source_policy_pos_observed_order"),
        "source_policy_vel_observed_order": summary.get("source_policy_vel_observed_order"),
        "source_policy_order_acceptance_satisfied": summary.get("source_policy_order_acceptance_satisfied"),
        "low_order_failure_modes": low_order_failure_modes,
        "promotion_ready": summary.get("promotion_ready"),
        "promotion_blockers": summary.get("promotion_blockers", []),
        "source_policy_reproduction_rows_promoted": summary.get("source_policy_reproduction_rows_promoted"),
        "counts_as_executed_local_candidate": len(ok_rows) == 3,
        "counts_as_b4_accepted_source_policy_rows": False,
        "counts_as_complete_work_precision_curve": False,
        "source_policy_rows_closed_by_this_evidence": 0,
        "b4_can_close_from_this_evidence": False,
        "b7_can_close_from_this_evidence": False,
    }


def build_hi2022_full_t8_source_policy_candidate_evidence(
    hi2022_source_row_audit: dict[str, Any],
) -> dict[str, Any]:
    validator_label = "../v048_cross_paper_same_test_benchmarks/validate_hi2022_full_t8_source_policy_candidate.py"
    validator_path = manuscript_path(validator_label)
    matrix = hi2022_source_row_audit.get("t8_selected_candidate_matrix_preflight", {})
    matrix_shards = [item for item in matrix.get("shards", []) if isinstance(item, dict)]
    summaries: list[dict[str, Any]] = []
    rows_by_shard: dict[str, list[dict[str, str]]] = {}
    shard_summaries: list[dict[str, Any]] = []
    for shard in matrix_shards:
        shard_id = str(shard.get("shard_id"))
        summary_label = str(shard.get("summary_path") or "")
        rows_label = str(shard.get("rows_path") or "")
        summary_path = manuscript_path(summary_label)
        rows_path = manuscript_path(rows_label)
        summary = read_json(summary_path.resolve()) if summary_path.exists() else {}
        rows = read_csv(rows_path.resolve()) if rows_path.exists() else []
        ok_rows = [row for row in rows if row.get("status") == "ok"]
        summaries.append(summary)
        rows_by_shard[shard_id] = rows
        shard_summaries.append(
            {
                "shard_id": shard_id,
                "form": shard.get("form"),
                "model": shard.get("model"),
                "status": summary.get("status", shard.get("artifact_status", "missing")),
                "summary_exists": summary_path.exists() and summary_path.stat().st_size > 0,
                "rows_exists": rows_path.exists() and rows_path.stat().st_size > 0,
                "row_count": len(rows),
                "ok_row_count": len(ok_rows),
                "full_public_grid_selected": summary.get("full_public_grid_selected", False),
                "selected_step_trio_completed": summary.get("selected_step_trio_completed", False),
                "source_policy_rows_closed_by_this_evidence": summary.get(
                    "source_policy_rows_closed_by_this_evidence",
                    0,
                ),
            }
        )
    all_rows = [row for rows in rows_by_shard.values() for row in rows]
    ok_rows = [row for row in all_rows if row.get("status") == "ok"]
    nonempty_summaries = [summary for summary in summaries if summary]
    completed_shards = [
        item["shard_id"]
        for item in shard_summaries
        if item["status"] == "executed_full_T8_selected_coarse_trio_not_promoted"
        and item["ok_row_count"] == 3
    ]
    partial_or_failed_shards = [
        item["shard_id"]
        for item in shard_summaries
        if item["summary_exists"] and item["rows_exists"] and item["shard_id"] not in completed_shards
    ]
    missing_artifact_shards = [
        item["shard_id"]
        for item in shard_summaries
        if not item["summary_exists"] or not item["rows_exists"]
    ]
    selected_step_sizes = sorted(
        {
            float(value)
            for summary in nonempty_summaries
            for value in (summary.get("selected_step_sizes") or [])
        },
        reverse=True,
    )
    selected_reference_h_values = sorted(
        {
            float(value)
            for summary in nonempty_summaries
            if (value := summary.get("selected_reference_h")) is not None
        }
    )
    reference_runtime_values = [
        float(value)
        for summary in nonempty_summaries
        if (value := summary.get("reference_runtime_sec")) is not None
    ]
    promotion_blockers = sorted(
        {
            blocker
            for summary in nonempty_summaries
            for blocker in summary.get("promotion_blockers", [])
        }
    )
    return {
        "schema": "b4-hi2022-full-t8-source-policy-candidate-evidence-v2",
        "status": "selected_candidate_matrix_partially_executed_not_promoted",
        "summary_artifact_count": len(nonempty_summaries),
        "rows_artifact_count": sum(1 for rows in rows_by_shard.values() if rows),
        "expected_shard_count": matrix.get("expected_shard_count", len(matrix_shards)),
        "completed_shard_count": len(completed_shards),
        "partial_or_failed_shards": partial_or_failed_shards,
        "missing_artifact_shards": missing_artifact_shards,
        "completed_shards": completed_shards,
        "shards": shard_summaries,
        "validator_path": validator_label,
        "validator_exists": validator_path.exists() and validator_path.stat().st_size > 0,
        "runner_schema": sorted({summary.get("schema") for summary in nonempty_summaries}),
        "runner_statuses": sorted({summary.get("status") for summary in nonempty_summaries}),
        "execution_phase": sorted({summary.get("execution_phase") for summary in nonempty_summaries}),
        "heavy_numerical_run_invoked": any(bool(summary.get("heavy_numerical_run_invoked")) for summary in nonempty_summaries),
        "builder_invoked_heavy_numerical_run": False,
        "canonical_v048_main_invoked": any(bool(summary.get("canonical_v048_main_invoked")) for summary in nonempty_summaries),
        "canonical_hi2022_output_untouched_by_writer": all(
            bool(summary.get("canonical_hi2022_output_untouched_by_writer")) for summary in nonempty_summaries
        ) if nonempty_summaries else False,
        "forms": sorted({summary.get("form") for summary in nonempty_summaries}),
        "models": sorted({summary.get("model") for summary in nonempty_summaries}),
        "source_policy_time_window_selected": all(
            bool(summary.get("source_policy_time_window_selected")) for summary in nonempty_summaries
        ) if nonempty_summaries else False,
        "source_policy_reference_h_selected": all(
            bool(summary.get("source_policy_reference_h_selected")) for summary in nonempty_summaries
        ) if nonempty_summaries else False,
        "selected_coarse_trio": all(bool(summary.get("selected_coarse_trio")) for summary in nonempty_summaries)
        if nonempty_summaries
        else False,
        "full_public_grid_selected": any(bool(summary.get("full_public_grid_selected")) for summary in nonempty_summaries),
        "full_T8_policy_completed": all(bool(summary.get("full_T8_policy_completed")) for summary in nonempty_summaries)
        if nonempty_summaries
        else False,
        "source_policy_1e_4_included": any(bool(summary.get("source_policy_1e_4_included")) for summary in nonempty_summaries),
        "selected_step_sizes": selected_step_sizes,
        "selected_reference_h_values": selected_reference_h_values,
        "selected_t_end_values": sorted(
            {
                float(value)
                for summary in nonempty_summaries
                if (value := summary.get("selected_t_end")) is not None
            }
        ),
        "estimated_reference_steps_values": sorted(
            {
                int(value)
                for summary in nonempty_summaries
                if (value := summary.get("estimated_reference_steps")) is not None
            }
        ),
        "estimated_candidate_steps_values": sorted(
            {
                int(value)
                for summary in nonempty_summaries
                for value in (summary.get("estimated_candidate_steps") or [])
            }
        ),
        "reference_statuses": sorted({summary.get("reference_status") for summary in nonempty_summaries}),
        "reference_runtime_sec_values": reference_runtime_values,
        "row_count": len(all_rows),
        "ok_row_count": len(ok_rows),
        "source_policy_candidate_rows_completed": len(ok_rows),
        "selected_step_trio_completed_count": len(completed_shards),
        "h_values": selected_step_sizes,
        "runtime_sec_values": finite_float_values(all_rows, "runtime_sec"),
        "avg_iteration_values": finite_float_values(all_rows, "avg_iterations"),
        "max_iteration_values": finite_float_values(all_rows, "max_iterations"),
        "position_pair_orders_by_shard": {
            shard_id: pair_orders(rows, "pos_final_linf") for shard_id, rows in rows_by_shard.items() if rows
        },
        "velocity_pair_orders_by_shard": {
            shard_id: pair_orders(rows, "vel_final_linf") for shard_id, rows in rows_by_shard.items() if rows
        },
        "acceleration_pair_orders_by_shard": {
            shard_id: pair_orders(rows, "acc_final_linf") for shard_id, rows in rows_by_shard.items() if rows
        },
        "source_policy_reproduction_rows_promoted": sum(
            int(summary.get("source_policy_reproduction_rows_promoted") or 0) for summary in nonempty_summaries
        ),
        "counts_as_executed_full_T8_candidate": len(completed_shards) == int(matrix.get("expected_shard_count", 0) or 0),
        "counts_as_full_public_grid_source_policy": False,
        "counts_as_b4_accepted_source_policy_rows": False,
        "counts_as_complete_work_precision_curve": False,
        "source_policy_rows_closed_by_this_evidence": 0,
        "promotion_ready": False,
        "promotion_blockers": promotion_blockers,
        "b4_can_close_from_this_evidence": False,
        "b7_can_close_from_this_evidence": False,
    }


def build_hi2022_b4_b7_figure_scope_demotion_evidence(
    hi2022_source_row_audit: dict[str, Any],
) -> dict[str, Any]:
    figure_scope = hi2022_source_row_audit.get("b4_b7_figure_scope_decision", {})
    t8_coarse = hi2022_source_row_audit.get("t8_coarse_horizon_evidence", {})
    t8_selected = hi2022_source_row_audit.get("t8_selected_candidate_evidence", {})
    t8_matrix = hi2022_source_row_audit.get("t8_selected_candidate_matrix_preflight", {})
    return {
        "schema": "b4-hi2022-b4-b7-figure-scope-demotion-evidence-v1",
        "status": figure_scope.get("status"),
        "source_audit": "HI2022_SOURCE_POLICY_ROW_AUDIT.json",
        "source_audit_status": hi2022_source_row_audit.get("status"),
        "bounded_rows_ok": hi2022_source_row_audit.get("bounded_ok_row_count"),
        "bounded_rows_total": hi2022_source_row_audit.get("bounded_row_count"),
        "t8_coarse_rows_ok": t8_coarse.get("ok_row_count"),
        "t8_coarse_rows_total": t8_coarse.get("row_count"),
        "t8_coarse_complete_form_model_groups": t8_coarse.get("complete_form_model_groups"),
        "t8_coarse_group_count": t8_coarse.get("group_count"),
        "t8_selected_candidate_status": t8_selected.get("artifact_status"),
        "t8_selected_candidate_rows_ok": t8_selected.get("ok_row_count"),
        "t8_selected_candidate_rows_total": t8_selected.get("row_count"),
        "t8_selected_candidate_full_public_grid_selected": t8_selected.get("full_public_grid_selected"),
        "t8_selected_candidate_source_policy_rows_closed": t8_selected.get(
            "source_policy_rows_closed_by_this_evidence"
        ),
        "t8_selected_candidate_matrix_status": t8_matrix.get("status"),
        "t8_selected_candidate_matrix_expected_shards": t8_matrix.get("expected_shard_count"),
        "t8_selected_candidate_matrix_completed_shards": t8_matrix.get("completed_shard_count"),
        "t8_selected_candidate_matrix_command_count": t8_matrix.get("command_count"),
        "t8_selected_candidate_matrix_commands_avoid_1e_4": t8_matrix.get("all_commands_avoid_1e_4"),
        "t8_selected_candidate_matrix_heavy_run_invoked": t8_matrix.get("heavy_numerical_run_invoked"),
        "t8_selected_candidate_matrix_rows_closed": t8_matrix.get("source_policy_rows_closed_by_preflight"),
        "t8_selected_candidate_matrix_rows_ok": sum(
            int(shard.get("ok_row_count") or 0)
            for shard in t8_matrix.get("shards", [])
            if isinstance(shard, dict)
        ),
        "t8_selected_candidate_matrix_rows_total": sum(
            int(shard.get("row_count") or 0)
            for shard in t8_matrix.get("shards", [])
            if isinstance(shard, dict)
        ),
        "t8_selected_candidate_matrix_b4_b7_can_close": t8_matrix.get("b4_b7_can_close_from_preflight"),
        "t8_selected_candidate_matrix_missing_or_unexecuted_shards": t8_matrix.get(
            "missing_or_unexecuted_shards",
            [],
        ),
        "t8_selected_candidate_matrix_partial_or_failed_shards": t8_matrix.get(
            "partial_or_failed_shards",
            [],
        ),
        "t8_selected_candidate_matrix_missing_artifact_shards": t8_matrix.get(
            "missing_artifact_shards",
            [],
        ),
        "full_T8_policy_completed": hi2022_source_row_audit.get("full_T8_policy_completed"),
        "source_policy_reproduction_closed": hi2022_source_row_audit.get("source_policy_reproduction_closed"),
        "source_policy_rows_closed_by_hi2022": figure_scope.get("source_policy_rows_closed_by_hi2022"),
        "counts_as_clean_work_precision_figure": figure_scope.get("counts_as_clean_work_precision_figure"),
        "allowed_figure_use": figure_scope.get("allowed_figure_use", []),
        "forbidden_figure_use": figure_scope.get("forbidden_figure_use", []),
        "b4_b7_can_close_from_hi2022": figure_scope.get("b4_b7_can_close_from_hi2022"),
        "source_policy_rows_closed_by_this_evidence": 0,
        "b4_can_close_from_this_evidence": False,
        "b7_can_close_from_this_evidence": False,
        "promotion_gap": [
            "HI2022 full T=8 public grid remains incomplete",
            (
                "HI2022 selected-candidate matrix has "
                f"{t8_matrix.get('completed_shard_count')}/{t8_matrix.get('expected_shard_count')} "
                "completed coarse-trio shards; remaining partial/missing shards are "
                f"{t8_matrix.get('missing_or_unexecuted_shards', [])}"
            ),
            "current HI2022 T=8 evidence is demoted from B4/B7 source-policy figures",
            "HI2022 contributes zero accepted source-policy work/precision rows",
        ],
    }


def blocker_by_id(blocker_gate: dict[str, Any], blocker_id: str) -> dict[str, Any]:
    for item in blocker_gate.get("blockers", []):
        if isinstance(item, dict) and item.get("id") == blocker_id:
            return item
    raise ValueError(f"blocker {blocker_id} not found")


def script_item(path_label: str) -> dict[str, Any]:
    path = V048 / path_label
    return {
        "path": f"../v048_cross_paper_same_test_benchmarks/{path_label}",
        "exists": path.exists() and path.stat().st_size > 0,
        "python_lines": len(path.read_text(encoding="utf-8").splitlines()) if path.exists() else None,
    }


def source_token_contract(path_label: str, required_tokens: list[str]) -> dict[str, Any]:
    path = V048 / path_label
    text = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
    missing = [token for token in required_tokens if token not in text]
    return {
        "path": f"../v048_cross_paper_same_test_benchmarks/{path_label}",
        "exists": path.exists() and path.stat().st_size > 0,
        "required_tokens": required_tokens,
        "missing_tokens": missing,
        "contract_satisfied": path.exists() and not missing,
    }


def command_token_contract(
    *,
    command_id: str,
    command: str,
    required_tokens: list[str],
    forbidden_tokens: list[str] | None = None,
) -> dict[str, Any]:
    forbidden = forbidden_tokens or []
    missing = [token for token in required_tokens if token not in command]
    present_forbidden = [token for token in forbidden if token in command]
    return {
        "id": command_id,
        "command": command,
        "required_tokens": required_tokens,
        "missing_tokens": missing,
        "forbidden_tokens": forbidden,
        "present_forbidden_tokens": present_forbidden,
        "contract_satisfied": not missing and not present_forbidden,
    }


def batch_by_id(run_queue: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for item in run_queue.get("batch_queue", []):
        if isinstance(item, dict) and isinstance(item.get("batch_id"), str):
            result[item["batch_id"]] = item
    return result


def build_ra2021_launch_preflight(lanes: list[dict[str, Any]]) -> dict[str, Any]:
    ra_lane = next(item for item in lanes if item["lane_id"] == "ra2021_source_policy_work_precision")
    runner_files = [
        script_item("run_v048.py"),
        script_item("run_ra2021_double_order_shard.py"),
        script_item("run_ra2021_timing_shard.py"),
        script_item("run_public_closed_loop_shard.py"),
    ]
    runner_files_available = all(item["exists"] for item in runner_files)
    launch_commands = [
        {
            "id": "ra2021_public_timing_all_forms_models",
            "command": "../.venv_sbel/bin/python run_v048.py --reuse-existing-results --ra2021-public-timing --ra2021-timing-forms rA,rp,reps --ra2021-timing-models single_pendulum,double_pendulum,four_link,slider_crank --allow-source-policy-1e-4",
            "expected_output_after_run": "../v048_cross_paper_same_test_benchmarks/results/ra2021_public_timing_rows.csv",
            "purpose": "bind runtime and Newton-iteration metrics to source-policy/public-code timing rows",
        },
        {
            "id": "gauss6_public_single_source_policy_trio",
            "command": "../.venv_sbel/bin/python run_v048.py --reuse-existing-results --gauss6-public-single --gauss6-public-step-sizes 1e-2,1e-3,1e-4 --allow-source-policy-1e-4",
            "expected_output_after_run": "../v048_cross_paper_same_test_benchmarks/results/gauss6_fullva_public_horizon_single_rows.csv",
            "purpose": "produce Gauss6/FullVA source-policy single-pendulum rows over the source h trio",
        },
        {
            "id": "ra2021_double_order_all_forms",
            "command": "../.venv_sbel/bin/python run_v048.py --reuse-existing-results --ra2021-double-order --allow-source-policy-1e-4",
            "expected_output_after_run": "../v048_cross_paper_same_test_benchmarks/results/ra2021_double_pendulum_order_rows.csv",
            "purpose": "produce RA2021 double-pendulum public dynamic self-reference order rows",
        },
        {
            "id": "gauss6_public_four_link_source_policy_trio",
            "command": "../.venv_sbel/bin/python run_public_closed_loop_shard.py --model four_link --step-sizes 1e-2,1e-3,1e-4 --allow-source-policy-1e-4",
            "expected_output_after_run": "../v048_cross_paper_same_test_benchmarks/results/public_closed_loop_shards/four_link_1em02_1em03_1em04.csv",
            "purpose": "produce public-horizon Gauss6/FullVA four-link source-policy rows",
        },
        {
            "id": "gauss6_public_slider_crank_source_policy_trio",
            "command": "../.venv_sbel/bin/python run_public_closed_loop_shard.py --model slider_crank --step-sizes 1e-2,1e-3,1e-4 --allow-source-policy-1e-4",
            "expected_output_after_run": "../v048_cross_paper_same_test_benchmarks/results/public_closed_loop_shards/slider_crank_1em02_1em03_1em04.csv",
            "purpose": "produce public-horizon Gauss6/FullVA slider-crank source-policy rows",
        },
    ]
    runner_cli_contracts = [
        source_token_contract(
            "run_v048.py",
            [
                "--reuse-existing-results",
                "--ra2021-public-timing",
                "--ra2021-timing-forms",
                "--ra2021-timing-models",
                "--ra2021-double-order",
                "--gauss6-public-single",
                "--gauss6-public-step-sizes",
                "--allow-source-policy-1e-4",
            ],
        ),
        source_token_contract(
            "run_ra2021_double_order_shard.py",
            ["--form", "--step-sizes", "--reference-h", "--allow-source-policy-1e-4"],
        ),
        source_token_contract(
            "run_ra2021_timing_shard.py",
            ["--form", "--model", "--h", "--allow-source-policy-1e-4"],
        ),
        source_token_contract(
            "run_public_closed_loop_shard.py",
            ["--model", "--step-sizes", "--allow-source-policy-1e-4"],
        ),
    ]
    ra_required_by_command = {
        "ra2021_public_timing_all_forms_models": [
            "run_v048.py",
            "--reuse-existing-results",
            "--ra2021-public-timing",
            "--ra2021-timing-forms",
            "--ra2021-timing-models",
            "--allow-source-policy-1e-4",
        ],
        "gauss6_public_single_source_policy_trio": [
            "run_v048.py",
            "--reuse-existing-results",
            "--gauss6-public-single",
            "--gauss6-public-step-sizes",
            "1e-2,1e-3,1e-4",
            "--allow-source-policy-1e-4",
        ],
        "ra2021_double_order_all_forms": [
            "run_v048.py",
            "--reuse-existing-results",
            "--ra2021-double-order",
            "--allow-source-policy-1e-4",
        ],
        "gauss6_public_four_link_source_policy_trio": [
            "run_public_closed_loop_shard.py",
            "--model four_link",
            "--step-sizes 1e-2,1e-3,1e-4",
            "--allow-source-policy-1e-4",
        ],
        "gauss6_public_slider_crank_source_policy_trio": [
            "run_public_closed_loop_shard.py",
            "--model slider_crank",
            "--step-sizes 1e-2,1e-3,1e-4",
            "--allow-source-policy-1e-4",
        ],
    }
    command_cli_contracts = [
        command_token_contract(
            command_id=command["id"],
            command=command["command"],
            required_tokens=ra_required_by_command[command["id"]],
        )
        for command in launch_commands
    ]
    cli_contract_satisfied = all(item["contract_satisfied"] for item in runner_cli_contracts + command_cli_contracts)
    return {
        "schema": "b4-ra2021-source-policy-launch-preflight-v1",
        "status": "ready_not_run_requires_user_opt_in",
        "read_only_preflight": True,
        "ready_to_execute_without_code_changes": runner_files_available,
        "runner_files_available": runner_files_available,
        "runner_files": runner_files,
        "launch_command_count": len(launch_commands),
        "launch_commands": launch_commands,
        "all_launch_commands_require_explicit_1e_4_opt_in": True,
        "heavy_numerical_run_invoked": False,
        "run_v047_invoked": False,
        "v048_runner_invoked": False,
        "source_policy_rows_closed_by_preflight": 0,
        "b4_can_close_after_preflight_only": False,
        "b7_can_close_after_preflight_only": False,
        "promotion_requirements_after_launch": ra_lane["required_before_publication_figure"],
        "runner_cli_contract": {
            "schema": "b4-ra2021-runner-cli-contract-v1",
            "status": "runner_cli_contract_satisfied" if cli_contract_satisfied else "runner_cli_contract_open",
            "runner_contract_count": len(runner_cli_contracts),
            "command_contract_count": len(command_cli_contracts),
            "all_contracts_satisfied": cli_contract_satisfied,
            "runner_option_contracts": runner_cli_contracts,
            "launch_command_contracts": command_cli_contracts,
            "heavy_numerical_run_invoked": False,
            "source_policy_rows_closed_by_preflight": 0,
        },
    }


def build_hi2022_launch_preflight(
    lanes: list[dict[str, Any]],
    hi2022_source_row_audit: dict[str, Any],
) -> dict[str, Any]:
    hi_lane = next(item for item in lanes if item["lane_id"] == "hi2022_full_T8_work_precision")
    matrix = hi2022_source_row_audit.get("t8_selected_candidate_matrix_preflight", {})
    runner_files = [script_item("run_hi2022_full_t8_source_policy_candidate.py")]
    runner_files_available = all(item["exists"] for item in runner_files)
    launch_commands = [
        {
            "id": f"hi2022_selected_t8_{shard.get('form')}_{shard.get('model')}",
            "shard_id": shard.get("shard_id"),
            "command": shard.get("command"),
            "expected_output_after_run": shard.get("rows_path"),
            "expected_summary_after_run": shard.get("summary_path"),
            "artifact_status": shard.get("artifact_status"),
            "purpose": "execute one isolated HI2022 T=8 selected-coarse-trio candidate shard",
        }
        for shard in matrix.get("shards", [])
        if isinstance(shard, dict)
    ]
    runner_cli_contracts = [
        source_token_contract(
            "run_hi2022_full_t8_source_policy_candidate.py",
            ["--form", "--model", "--step-sizes", "--reference-h", "--t-end", "--execute", "--allow-source-policy-1e-4"],
        )
    ]
    command_cli_contracts = [
        command_token_contract(
            command_id=command["id"],
            command=command["command"] or "",
            required_tokens=[
                "run_hi2022_full_t8_source_policy_candidate.py",
                "--form",
                "--model",
                "--execute",
            ],
            forbidden_tokens=["--allow-source-policy-1e-4"],
        )
        for command in launch_commands
    ]
    cli_contract_satisfied = all(item["contract_satisfied"] for item in runner_cli_contracts + command_cli_contracts)
    return {
        "schema": "b4-hi2022-source-policy-launch-preflight-v1",
        "status": matrix.get("status"),
        "read_only_preflight": True,
        "ready_to_execute_without_code_changes": runner_files_available and matrix.get("script_exists") is True,
        "runner_files_available": runner_files_available,
        "runner_files": runner_files,
        "launch_command_count": len(launch_commands),
        "launch_commands": launch_commands,
        "expected_shard_count": matrix.get("expected_shard_count"),
        "completed_shard_count": matrix.get("completed_shard_count"),
        "completed_shards": matrix.get("completed_shards", []),
        "missing_or_unexecuted_shards": matrix.get("missing_or_unexecuted_shards", []),
        "all_launch_commands_avoid_1e_4": matrix.get("all_commands_avoid_1e_4"),
        "source_policy_1e_4_required": matrix.get("source_policy_1e_4_required"),
        "all_launch_commands_require_heavy_run_opt_in": all(
            bool(shard.get("requires_heavy_run_opt_in"))
            for shard in matrix.get("shards", [])
            if isinstance(shard, dict)
        ),
        "heavy_numerical_run_invoked": False,
        "run_v047_invoked": False,
        "v048_runner_invoked": False,
        "source_policy_rows_closed_by_preflight": matrix.get("source_policy_rows_closed_by_preflight"),
        "source_policy_rows_closed_by_existing_candidates": matrix.get(
            "source_policy_rows_closed_by_existing_candidates"
        ),
        "counts_as_complete_work_precision_curve": matrix.get("counts_as_complete_work_precision_curve"),
        "b4_can_close_after_preflight_only": False,
        "b7_can_close_after_preflight_only": False,
        "promotion_requirements_after_launch": hi_lane["required_before_publication_figure"],
        "promotion_gap": matrix.get("promotion_gap", []),
        "runner_cli_contract": {
            "schema": "b4-hi2022-runner-cli-contract-v1",
            "status": "runner_cli_contract_satisfied" if cli_contract_satisfied else "runner_cli_contract_open",
            "runner_contract_count": len(runner_cli_contracts),
            "command_contract_count": len(command_cli_contracts),
            "all_contracts_satisfied": cli_contract_satisfied,
            "runner_option_contracts": runner_cli_contracts,
            "launch_command_contracts": command_cli_contracts,
            "heavy_numerical_run_invoked": False,
            "source_policy_rows_closed_by_preflight": 0,
        },
    }


def build_tfe_b4_b7_figure_scope_demotion_evidence(
    tfe_demotion_audit: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema": "b4-tfe-figure-scope-demotion-evidence-v1",
        "status": tfe_demotion_audit.get("status"),
        "source_audit": "TFE_B4_B7_SOURCE_POLICY_DEMOTION_AUDIT.json",
        "source_policy_rows_total": tfe_demotion_audit.get("source_policy_rows_total"),
        "source_policy_rows_closed": tfe_demotion_audit.get("source_policy_rows_closed"),
        "source_policy_rows_closed_by_demotion": tfe_demotion_audit.get(
            "source_policy_rows_closed_by_demotion"
        ),
        "demoted_related_work_proxy_rows_for_current_claim": tfe_demotion_audit.get(
            "demoted_related_work_proxy_rows_for_current_claim"
        ),
        "future_reintroduction_requires_runner_or_code_path_rows": tfe_demotion_audit.get(
            "future_reintroduction_requires_runner_or_code_path_rows"
        ),
        "current_claim_requires_tfe_source_policy_execution": tfe_demotion_audit.get(
            "current_claim_requires_tfe_source_policy_execution"
        ),
        "brown_mcphee_source_code_equivalent_law": tfe_demotion_audit.get(
            "brown_mcphee_source_code_equivalent_law"
        ),
        "source_grid_policy_resolved_for_full_T10": tfe_demotion_audit.get(
            "source_grid_policy_resolved_for_full_T10"
        ),
        "pendulum_dae_runner_implemented": tfe_demotion_audit.get("pendulum_dae_runner_implemented"),
        "runner_equivalence_open_blocker_count": tfe_demotion_audit.get(
            "runner_equivalence_open_blocker_count"
        ),
        "demotion_reasons": tfe_demotion_audit.get("demotion_reasons", []),
        "counts_as_clean_work_precision_figure": False,
        "b4_b7_can_close_from_tfe": False,
        "allowed_figure_use": "related-work/formal-order context and explicitly labeled diagnostics only",
        "forbidden_figure_use": "current B4/B7 source-policy work/precision figures or external-superiority claim",
    }


def build_execution_lanes(
    run_queue: dict[str, Any],
    b2_manifest: dict[str, Any],
    row_ledger: dict[str, Any],
    ra2021_source_identity: dict[str, Any],
    hi2022_policy: dict[str, Any],
    hi2022_source_row_audit: dict[str, Any],
    tfe_spec: dict[str, Any],
    tfe_model_audit: dict[str, Any],
    tfe_demotion_audit: dict[str, Any],
) -> list[dict[str, Any]]:
    batches = batch_by_id(run_queue)
    suite_closure = row_ledger.get("suite_closure_status", {})
    b2_lanes = {
        item.get("suite_id"): item
        for item in b2_manifest.get("closure_execution_plan", {}).get("route_a_inactive_reference_lanes", [])
        if isinstance(item, dict)
    }
    ra_lane = b2_lanes.get("ra2021_absolute_coordinate", {})
    tfe_lane = b2_lanes.get("tfe2026_original_pendulum", {})
    tfe_runner_preflight = tfe_model_audit.get("source_policy_runner_equivalence_preflight", {})
    hi2022_matrix = hi2022_source_row_audit.get("t8_selected_candidate_matrix_preflight", {})
    hi2022_commands = [
        shard.get("command")
        for shard in hi2022_matrix.get("shards", [])
        if isinstance(shard, dict) and shard.get("command")
    ]
    return [
        {
            "lane_id": "ra2021_source_policy_work_precision",
            "suite_id": "ra2021_absolute_coordinate",
            "priority": 1,
            "status": "public_baseline_rows_complete_source_policy_work_precision_promotion_open",
            "ready_to_launch_after_explicit_opt_in": True,
            "plan_only_closes_b4": False,
            "plan_only_closes_b7": False,
            "source_policy_1e_4_opt_in_required": True,
            "source_policy_rows_completed": 0,
            "flagged_rows": suite_closure.get("ra2021_absolute_coordinate", {}).get("flagged_rows"),
            "public_order_groups_completed": 12,
            "public_timing_rows_completed": 12,
            "source_output_mapping_verified": ra2021_source_identity.get("claim_boundary", {}).get(
                "output_mapping_verified_from_source"
            ),
            "source_time_grid_policy_extracted": ra2021_source_identity.get("claim_boundary", {}).get(
                "time_grid_policy_extracted_from_source"
            ),
            "parallel_shard_count": batches.get("ra2021_coarse_same_window_order_time", {}).get(
                "parallel_shard_count"
            ),
            "representative_commands": ra_lane.get("representative_commands", []),
            "required_before_publication_figure": [
                "promote or rerun local Gauss6/FullVA rows under the RA2021 source time grid and output norm",
                "bind runtime and Newton-iteration metrics to the same promoted rows",
                "produce source-policy work/precision curves and a figure caption that states the source policy",
                "keep common-reference diagnostics separate from publication-grade source-policy rows",
            ],
            "acceptance_artifacts": [
                "source-policy row table with h grid, reference policy, errors, observed order, runtime, and Newton metrics",
                "work/precision figure over the promoted rows",
                "independent verification or rerun provenance for the promoted rows",
            ],
        },
        {
            "lane_id": "tfe_source_policy_work_precision",
            "suite_id": "tfe2026_original_pendulum",
            "priority": 2,
            "status": "diagnostic_same_test_work_precision_available_source_policy_runner_equivalence_open",
            "ready_to_launch_after_explicit_opt_in": False,
            "plan_only_closes_b4": False,
            "plan_only_closes_b7": False,
            "source_policy_1e_4_opt_in_required": None,
            "source_policy_rows_completed": tfe_spec.get("runner_gap", {}).get("source_policy_rows_completed"),
            "flagged_rows": suite_closure.get("tfe2026_original_pendulum", {}).get("flagged_rows"),
            "source_reference_h": tfe_spec.get("source_policy", {})
            .get("solver_policy", {})
            .get("source_reference_h_for_exact_reproduction"),
            "same_test_candidate_work_precision_methods": tfe_model_audit.get(
                "source_pendulum_same_test_work_precision_method_count"
            ),
            "same_test_candidate_work_precision_rows": tfe_model_audit.get(
                "source_pendulum_same_test_work_precision_metric_rows"
            ),
            "same_test_candidate_source_policy_rows_completed": tfe_model_audit.get(
                "source_pendulum_same_test_work_precision_source_policy_rows_completed"
            ),
            "candidate_full_T10_probe_implemented": tfe_model_audit.get(
                "active_tfe_b2_full_T10_coarse_candidate_probe_implemented"
            ),
            "candidate_full_T10_probe_finite_rows": tfe_model_audit.get(
                "active_tfe_b2_full_T10_coarse_candidate_probe_finite_rows"
            ),
            "candidate_full_T10_probe_residual_ok_rows": tfe_model_audit.get(
                "active_tfe_b2_full_T10_coarse_candidate_probe_residual_ok_rows"
            ),
            "pendulum_dae_runner_implemented": tfe_spec.get("runner_gap", {}).get("pendulum_dae_runner_implemented"),
            "source_policy_dae_runner_equivalent": tfe_model_audit.get("source_policy_dae_runner_equivalent"),
            "source_policy_method_runner_equivalent": tfe_model_audit.get("source_policy_method_runner_equivalent"),
            "runner_equivalence_preflight_status": tfe_runner_preflight.get("status"),
            "runner_equivalence_preflight_closed_preconditions": tfe_runner_preflight.get(
                "closed_precondition_count"
            ),
            "runner_equivalence_preflight_open_blockers": tfe_runner_preflight.get("open_blocker_count"),
            "runner_equivalence_preflight_rows_closed": tfe_runner_preflight.get(
                "source_policy_rows_closed_by_preflight"
            ),
            "runner_equivalence_preflight_can_close_lane": tfe_runner_preflight.get(
                "can_close_tfe_lane_from_preflight"
            ),
            "demotion_audit_consumed": True,
            "demotion_audit": "TFE_B4_B7_SOURCE_POLICY_DEMOTION_AUDIT.json",
            "current_claim_requires_tfe_source_policy_execution": tfe_demotion_audit.get(
                "current_claim_requires_tfe_source_policy_execution"
            ),
            "current_claim_requires_source_policy_execution": tfe_demotion_audit.get(
                "current_claim_requires_tfe_source_policy_execution"
            ),
            "demoted_related_work_proxy_rows_for_current_claim": tfe_demotion_audit.get(
                "demoted_related_work_proxy_rows_for_current_claim"
            ),
            "future_reintroduction_requires_runner_or_code_path_rows": tfe_demotion_audit.get(
                "future_reintroduction_requires_runner_or_code_path_rows"
            ),
            "claim_allowed_now": "related-work/formal-order context and explicitly labeled diagnostics only",
            "representative_commands": tfe_lane.get("representative_commands", []),
            "required_before_publication_figure": [
                "prove or replace the candidate planar runner with a source-policy equivalent DAE runner",
                "resolve Brown-McPhee friction and endpoint/output policy for the full T=10 source problem",
                "run TFE m=1/2/3, Newmark, trapezoidal, and Gauss6/FullVA rows under one source reference policy",
                "produce work/precision curves from source-policy rows, not from the current diagnostic candidate rows",
            ],
            "acceptance_artifacts": [
                "source-equivalence runner certificate",
                "full T=10 source-policy row table with h_ref=1e-4 opt-in provenance",
                "source-policy work/precision figure over accepted TFE comparator rows",
            ],
        },
        {
            "lane_id": "hi2022_full_T8_work_precision",
            "suite_id": "hi2022_half_implicit",
            "priority": 3,
            "status": "bounded_T0p1_rows_complete_full_T8_source_policy_work_precision_open",
            "ready_to_launch_after_explicit_opt_in": True,
            "plan_only_closes_b4": False,
            "plan_only_closes_b7": False,
            "source_policy_1e_4_opt_in_required": False,
            "source_policy_rows_completed": 0,
            "flagged_rows": suite_closure.get("hi2022_half_implicit", {}).get("flagged_rows"),
            "bounded_T0p1_rows": hi2022_policy.get("existing_bounded_evidence", {}).get("row_count"),
            "bounded_T0p1_ok_rows": hi2022_policy.get("existing_bounded_evidence", {}).get("ok_row_count"),
            "full_T8_policy_completed": hi2022_policy.get(
                "source_policy_required_before_external_superiority", {}
            ).get("full_T8_policy_completed"),
            "parallel_shard_count": batches.get("hi2022_halfimplicit_full_policy_decision", {}).get(
                "parallel_shard_count"
            ),
            "representative_commands": hi2022_commands,
            "required_before_publication_figure": [
                "select and document the full T=8 public-policy step/reference grid",
                "rerun or independently verify order and runtime rows under that policy",
                "bind work metrics to the same rows used in the error/order table",
                "produce source-policy work/precision curves or keep HI2022 demoted from B4 figures",
            ],
            "acceptance_artifacts": [
                "full T=8 source-policy row table",
                "runtime/Newton metric table tied to the full-policy rows",
                "work/precision figure or explicit figure-scope demotion",
            ],
        },
        {
            "lane_id": "vp2024_source_code_path_work_precision",
            "suite_id": "vp2024_velocity_partitioning",
            "priority": 4,
            "status": "not_ready_distinct_public_velocity_partitioning_code_path_unresolved",
            "ready_to_launch_after_explicit_opt_in": False,
            "plan_only_closes_b4": False,
            "plan_only_closes_b7": False,
            "source_policy_1e_4_opt_in_required": False,
            "source_policy_rows_completed": 0,
            "flagged_rows": suite_closure.get("vp2024_velocity_partitioning", {}).get("flagged_rows"),
            "code_path_resolved": suite_closure.get("vp2024_velocity_partitioning", {}).get("code_path_resolved"),
            "parallel_shard_count": 0,
            "representative_commands": [],
            "required_before_publication_figure": [
                "resolve a distinct public velocity-partitioning code path",
                "extract source step-size/reference/output policy",
                "run accepted order and work rows or keep VP as related-work-only",
                "exclude coordinate-partitioning proxy rows from source-policy work/precision figures",
            ],
            "acceptance_artifacts": [
                "code-path resolution audit",
                "source-policy row table for the resolved method",
                "work/precision figure or explicit figure-scope demotion",
            ],
        },
    ]


def main() -> None:
    blocker_gate = read_json(PAPER / "CMAME_BLOCKER_CLOSURE_GATE.json")
    b4_b7 = read_json(PAPER / "B4_B7_NON_SUPERIORITY_ROUTE_AUDIT.json")
    b2_manifest = read_json(PAPER / "B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.json")
    row_ledger = read_json(PAPER / "SOURCE_POLICY_ROW_CLOSURE_LEDGER.json")
    run_queue = read_json(PAPER / "EXTERNAL_SAME_TEST_RUN_QUEUE.json")
    external_case = read_json(PAPER / "EXTERNAL_CASE_EVIDENCE_RECONCILIATION.json")
    ra2021_source_identity = read_json(PAPER / "RA2021_SOURCE_IDENTITY_AUDIT.json")
    hi2022_policy = read_json(PAPER / "HI2022_POLICY_DECISION_AUDIT.json")
    hi2022_source_row_audit = read_json(PAPER / "HI2022_SOURCE_POLICY_ROW_AUDIT.json")
    tfe_spec = read_json(PAPER / "TFE_SOURCE_POLICY_SPEC.json")
    tfe_model_audit = read_json(PAPER / "TFE_SOURCE_PENDULUM_MODEL_AUDIT.json")
    tfe_demotion_audit = read_json(PAPER / "TFE_B4_B7_SOURCE_POLICY_DEMOTION_AUDIT.json")
    tfe_literal_work = read_json(PAPER / "TFE_ALGORITHM_LITERAL_WORK_PRECISION_AUDIT.json")
    figure_set = read_json(PAPER / "CMAME_FIGURE_SET_AUDIT.json")

    b4 = blocker_by_id(blocker_gate, "B4")
    b6 = blocker_by_id(blocker_gate, "B6")
    b7 = blocker_by_id(blocker_gate, "B7")
    b4_audit = b4_b7.get("b4", {})
    b7_audit = b4_b7.get("b7", {})
    claim_scope = b4_b7.get("claim_scope", {})
    lanes = build_execution_lanes(
        run_queue,
        b2_manifest,
        row_ledger,
        ra2021_source_identity,
        hi2022_policy,
        hi2022_source_row_audit,
        tfe_spec,
        tfe_model_audit,
        tfe_demotion_audit,
    )
    executable_lane_count = sum(1 for lane in lanes if lane["ready_to_launch_after_explicit_opt_in"])
    not_ready_lane_count = len(lanes) - executable_lane_count
    source_policy_rows_closed = b4_audit.get("source_policy_execution_rows_closed")
    source_policy_rows_total = b4_audit.get("source_policy_execution_total_rows")
    ra2021_launch_preflight = build_ra2021_launch_preflight(lanes)
    hi2022_launch_preflight = build_hi2022_launch_preflight(lanes, hi2022_source_row_audit)
    ra2021_executed_shard_evidence = build_executed_ra2021_shard_evidence()
    gauss6_local_source_policy_evidence = build_gauss6_local_source_policy_evidence()
    ra2021_closed_loop_same_window_evidence = (
        build_ra2021_closed_loop_same_window_public_work_precision_evidence()
    )
    ra2021_double_local_candidate = build_ra2021_double_local_source_policy_candidate_evidence()
    hi2022_full_t8_candidate = build_hi2022_full_t8_source_policy_candidate_evidence(
        hi2022_source_row_audit
    )
    hi2022_figure_scope_demotion = build_hi2022_b4_b7_figure_scope_demotion_evidence(
        hi2022_source_row_audit
    )
    tfe_figure_scope_demotion = build_tfe_b4_b7_figure_scope_demotion_evidence(
        tfe_demotion_audit
    )
    tfe_runner_preflight = tfe_model_audit.get("source_policy_runner_equivalence_preflight", {})
    tfe_runner_preflight_summary = {
        "schema": tfe_runner_preflight.get("schema"),
        "status": tfe_runner_preflight.get("status"),
        "closed_precondition_count": tfe_runner_preflight.get("closed_precondition_count"),
        "open_blocker_count": tfe_runner_preflight.get("open_blocker_count"),
        "source_policy_rows_closed_by_preflight": tfe_runner_preflight.get(
            "source_policy_rows_closed_by_preflight"
        ),
        "can_close_tfe_lane_from_preflight": tfe_runner_preflight.get("can_close_tfe_lane_from_preflight"),
        "b4_b7_can_close_from_preflight": tfe_runner_preflight.get("b4_b7_can_close_from_preflight"),
        "heavy_numerical_run_invoked": tfe_runner_preflight.get("heavy_numerical_run_invoked"),
        "open_blocker_ids": [
            item.get("id") for item in tfe_runner_preflight.get("open_blockers", [])
        ],
    }

    output: dict[str, Any] = {
        "schema": "b4-source-policy-work-precision-execution-plan-v1",
        "status": "execution_plan_ready_b4_b7_remain_open",
        "submission_ready": False,
        "submission_standard_met": False,
        "b4_can_close_now": False,
        "b7_can_close_now": False,
        "b6_can_close_now": False,
        "route_b_closes_b2": b4_b7.get("route_b_closes_b2"),
        "route_b_closes_b4": b4_b7.get("route_b_closes_b4"),
        "route_b_closes_b7": b4_b7.get("route_b_closes_b7"),
        "open_blockers_after_plan": b4_b7.get("open_blockers_after_audit"),
        "claim_scope": {
            "allowed_current_claims": claim_scope.get("allowed_current_claims"),
            "forbidden_current_claims": claim_scope.get("forbidden_current_claims"),
            "external_superiority_claim_allowed": claim_scope.get("external_superiority_claim_allowed"),
            "source_policy_rows_closed": claim_scope.get("source_policy_rows_closed"),
            "common_reference_claim_allowed": b4_audit.get("common_reference_claim_allowed"),
        },
        "current_evidence": {
            "common_reference_order_error_matrix_closed": b4_audit.get(
                "common_reference_order_error_matrix_closed"
            ),
            "direct_nonlocal_velocity_order_wins": b4_audit.get("common_reference_direct_nonlocal_order_wins"),
            "direct_nonlocal_velocity_order_comparisons": b4_audit.get(
                "common_reference_direct_nonlocal_order_comparisons"
            ),
            "direct_nonlocal_finest_velocity_error_wins": b4_audit.get(
                "common_reference_direct_nonlocal_error_wins"
            ),
            "direct_nonlocal_finest_velocity_error_comparisons": b4_audit.get(
                "common_reference_direct_nonlocal_error_comparisons"
            ),
            "source_policy_rows_closed": source_policy_rows_closed,
            "source_policy_rows_total": source_policy_rows_total,
            "source_policy_flagged_rows": row_ledger.get("coverage", {}).get("flagged_row_count"),
            "external_superiority_ready_rows": b4_audit.get("external_superiority_ready_rows"),
            "source_policy_publication_grade_work_precision_open": b4_audit.get(
                "source_policy_publication_grade_work_precision_open"
            ),
            "diagnostic_work_precision_rows": b4_audit.get("diagnostic_work_precision_rows"),
            "tfe_algorithm_literal_work_precision_source_policy_rows_completed": tfe_literal_work.get(
                "source_policy_rows_completed"
            ),
            "tfe_algorithm_literal_runtime_proxy_available": tfe_literal_work.get("runtime_proxy_available"),
            "tfe_algorithm_literal_terminal_overrun_rows": tfe_literal_work.get("terminal_overrun_rows"),
            "tfe_runner_equivalence_preflight_status": tfe_runner_preflight_summary["status"],
            "tfe_runner_equivalence_preflight_rows_closed": tfe_runner_preflight_summary[
                "source_policy_rows_closed_by_preflight"
            ],
            "tfe_runner_equivalence_preflight_can_close_lane": tfe_runner_preflight_summary[
                "can_close_tfe_lane_from_preflight"
            ],
            "tfe_b4_b7_rows_demoted_related_work_proxy_for_current_claim": tfe_figure_scope_demotion[
                "demoted_related_work_proxy_rows_for_current_claim"
            ],
            "tfe_current_claim_requires_source_policy_execution": tfe_figure_scope_demotion[
                "current_claim_requires_tfe_source_policy_execution"
            ],
            "ra2021_public_baseline_progress": external_case.get("source_policy_progress", {}).get(
                "ra2021_public_baselines"
            ),
        },
        "publication_grade_acceptance_contract": {
            "contract_id": "b4-source-policy-work-precision-publication-contract-v1",
            "plan_only_closes_rows": False,
            "required_to_close_b4": b4.get("required_to_close"),
            "required_to_close_b7": b7.get("required_to_close"),
            "required_to_close_b6": b6.get("required_to_close"),
            "required_row_properties": [
                "source-policy time horizon, step grid, reference, output variables, and norm are declared",
                "local Gauss6/FullVA and baseline rows use the same accepted policy for each comparison",
                "error/order rows and work metrics come from the same accepted run records",
                "runtime, Newton iterations, derivative/Jacobian cost, and failure policy are reported",
                "diagnostic common-reference rows are not promoted into source-policy figures",
            ],
            "required_figures": [
                "baseline comparison figure over source-policy accepted rows",
                "clean work/precision figure with source-policy rows and work metrics",
                "limitation figure or caption that states excluded/demoted suites",
            ],
            "figure_set_current_status": figure_set.get("status"),
            "current_figure_set_b7_closed": figure_set.get("b7_closed"),
            "current_figure_set_supports_common_reference_diagnostics_only": b7_audit.get(
                "figure_set_supports_common_reference_diagnostics_only"
            ),
        },
        "execution_policy": {
            "read_only_existing_artifacts": True,
            "default_1e_4_required": False,
            "source_policy_1e_4_requires_explicit_flag": True,
            "heavy_numerical_run_invoked": False,
            "run_v047_invoked": False,
            "v048_runner_invoked": False,
            "next_heavy_source_policy_execution_requires_user_opt_in": True,
            "parallel_ready_shards_without_default_1e_4": run_queue.get("coverage_counts", {}).get(
                "parallel_shard_count_without_default_1e-4"
            ),
        },
        "execution_lanes": lanes,
        "ra2021_launch_preflight": ra2021_launch_preflight,
        "hi2022_launch_preflight": hi2022_launch_preflight,
        "ra2021_executed_shard_evidence": ra2021_executed_shard_evidence,
        "gauss6_local_source_policy_evidence": gauss6_local_source_policy_evidence,
        "ra2021_closed_loop_same_window_public_work_precision_evidence": (
            ra2021_closed_loop_same_window_evidence
        ),
        "ra2021_double_local_source_policy_candidate_evidence": ra2021_double_local_candidate,
        "hi2022_full_t8_source_policy_candidate_evidence": hi2022_full_t8_candidate,
        "hi2022_b4_b7_figure_scope_demotion_evidence": hi2022_figure_scope_demotion,
        "tfe_b4_b7_figure_scope_demotion_evidence": tfe_figure_scope_demotion,
        "tfe_source_policy_runner_equivalence_preflight_evidence": tfe_runner_preflight_summary,
        "execution_lane_summary": {
            "lane_count": len(lanes),
            "ready_to_launch_after_explicit_opt_in_count": executable_lane_count,
            "not_ready_lane_count": not_ready_lane_count,
            "plan_only_closed_rows": 0,
            "source_policy_rows_closed_after_plan": source_policy_rows_closed,
            "source_policy_rows_total": source_policy_rows_total,
        },
        "next_decision": {
            "recommended_first_lane": "ra2021_source_policy_work_precision",
            "reason": "RA2021 has public baseline order and timing evidence plus source-output mapping extraction, but the promoted source-policy Gauss6/FullVA work/precision rows are still missing.",
            "do_not_run_by_default": True,
            "requires_explicit_1e_4_opt_in": True,
            "alternative_if_no_heavy_runs": "keep Route B claim demotion and do a final prose/figure review for a narrower no-external-superiority paper; this still does not close B4/B7 under the current gate.",
        },
        "source_files": {
            "blocker_gate": "CMAME_BLOCKER_CLOSURE_GATE.json",
            "b4_b7_non_superiority_route_audit": "B4_B7_NON_SUPERIORITY_ROUTE_AUDIT.json",
            "b2_remaining_work_manifest": "B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.json",
            "source_policy_row_ledger": "SOURCE_POLICY_ROW_CLOSURE_LEDGER.json",
            "external_same_test_run_queue": "EXTERNAL_SAME_TEST_RUN_QUEUE.json",
            "external_case_evidence_reconciliation": "EXTERNAL_CASE_EVIDENCE_RECONCILIATION.json",
            "ra2021_source_identity_audit": "RA2021_SOURCE_IDENTITY_AUDIT.json",
            "ra2021_closed_loop_same_window_public_work_precision": (
                "../v048_cross_paper_same_test_benchmarks/results/"
                "closed_loop_true_dynamic_public_work_precision.json"
            ),
            "hi2022_policy_decision_audit": "HI2022_POLICY_DECISION_AUDIT.json",
            "hi2022_source_policy_row_audit": "HI2022_SOURCE_POLICY_ROW_AUDIT.json",
            "tfe_source_policy_spec": "TFE_SOURCE_POLICY_SPEC.json",
            "tfe_source_pendulum_model_audit": "TFE_SOURCE_PENDULUM_MODEL_AUDIT.json",
            "tfe_b4_b7_source_policy_demotion_audit": "TFE_B4_B7_SOURCE_POLICY_DEMOTION_AUDIT.json",
            "tfe_algorithm_literal_work_precision_audit": "TFE_ALGORITHM_LITERAL_WORK_PRECISION_AUDIT.json",
            "figure_set_audit": "CMAME_FIGURE_SET_AUDIT.json",
        },
    }

    out_json = PAPER / "B4_SOURCE_POLICY_WORK_PRECISION_EXECUTION_PLAN.json"
    out_md = PAPER / "B4_SOURCE_POLICY_WORK_PRECISION_EXECUTION_PLAN.md"
    with out_json.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# B4 Source-Policy Work/Precision Execution Plan",
        "",
        "Status: `execution_plan_ready_b4_b7_remain_open`.",
        "",
        "This is a read-only execution plan. It records the next source-policy work/precision lanes but does not run new numerical experiments.",
        "",
        f"- Open blockers after plan: `{output['open_blockers_after_plan']}`.",
        f"- B4/B7 can close now: `{output['b4_can_close_now']}/{output['b7_can_close_now']}`.",
        f"- Route B closes B2/B4/B7: `{output['route_b_closes_b2']}/{output['route_b_closes_b4']}/{output['route_b_closes_b7']}`.",
        f"- Source-policy work/precision rows closed/total: `{source_policy_rows_closed}/{source_policy_rows_total}`.",
        f"- Source-policy flagged rows: `{output['current_evidence']['source_policy_flagged_rows']}`.",
        f"- External-superiority-ready rows: `{output['current_evidence']['external_superiority_ready_rows']}`.",
        f"- Common-reference order/error matrix closed: `{output['current_evidence']['common_reference_order_error_matrix_closed']}`.",
        f"- Common-reference velocity order wins: `{output['current_evidence']['direct_nonlocal_velocity_order_wins']}/{output['current_evidence']['direct_nonlocal_velocity_order_comparisons']}`.",
        f"- Common-reference finest velocity error wins: `{output['current_evidence']['direct_nonlocal_finest_velocity_error_wins']}/{output['current_evidence']['direct_nonlocal_finest_velocity_error_comparisons']}`.",
        f"- TFE same-test diagnostic rows/source-policy rows: `{output['current_evidence']['diagnostic_work_precision_rows']['tfe_same_test_rows']}/{output['current_evidence']['diagnostic_work_precision_rows']['tfe_same_test_source_policy_rows_completed']}`.",
        f"- TFE algorithm-literal work proxy/runtime proxy/source-policy rows: `{tfe_literal_work.get('work_proxy')}` / `{tfe_literal_work.get('runtime_proxy_available')}` / `{tfe_literal_work.get('source_policy_rows_completed')}`.",
        f"- TFE runner-equivalence preflight: `{tfe_runner_preflight_summary['status']}`.",
        f"- TFE runner-equivalence preflight closed/open/source rows: `{tfe_runner_preflight_summary['closed_precondition_count']}/{tfe_runner_preflight_summary['open_blocker_count']}/{tfe_runner_preflight_summary['source_policy_rows_closed_by_preflight']}`.",
        f"- TFE runner-equivalence preflight can close lane: `{tfe_runner_preflight_summary['can_close_tfe_lane_from_preflight']}`.",
        f"- TFE B4/B7 figure-scope demotion: `{tfe_figure_scope_demotion['status']}`.",
        f"- TFE demoted/source-policy rows closed: `{tfe_figure_scope_demotion['demoted_related_work_proxy_rows_for_current_claim']}/{tfe_figure_scope_demotion['source_policy_rows_closed_by_demotion']}`.",
        f"- TFE current claim requires source-policy execution: `{tfe_figure_scope_demotion['current_claim_requires_tfe_source_policy_execution']}`.",
        f"- Default 1e-4/heavy/run_v047/v048: `{output['execution_policy']['default_1e_4_required']}/{output['execution_policy']['heavy_numerical_run_invoked']}/{output['execution_policy']['run_v047_invoked']}/{output['execution_policy']['v048_runner_invoked']}`.",
        f"- Next heavy source-policy execution requires user opt-in: `{output['execution_policy']['next_heavy_source_policy_execution_requires_user_opt_in']}`.",
        f"- Execution lane ready/not-ready count: `{executable_lane_count}/{not_ready_lane_count}`.",
        f"- RA2021 launch preflight: `{ra2021_launch_preflight['schema']}` / `{ra2021_launch_preflight['status']}`.",
        f"- RA2021 runner files ready: `{ra2021_launch_preflight['runner_files_available']}`.",
        f"- RA2021 launch commands: `{ra2021_launch_preflight['launch_command_count']}`.",
        f"- RA2021 runner CLI contract: `{ra2021_launch_preflight['runner_cli_contract']['status']}`.",
        f"- RA2021 preflight closes B4/B7: `{ra2021_launch_preflight['b4_can_close_after_preflight_only']}/{ra2021_launch_preflight['b7_can_close_after_preflight_only']}`.",
        f"- HI2022 launch preflight: `{hi2022_launch_preflight['schema']}` / `{hi2022_launch_preflight['status']}`.",
        f"- HI2022 runner files ready: `{hi2022_launch_preflight['runner_files_available']}`.",
        f"- HI2022 launch commands/completed/missing: `{hi2022_launch_preflight['launch_command_count']}/{hi2022_launch_preflight['completed_shard_count']}/{len(hi2022_launch_preflight['missing_or_unexecuted_shards'])}`.",
        f"- HI2022 runner CLI contract: `{hi2022_launch_preflight['runner_cli_contract']['status']}`.",
        f"- HI2022 commands avoid 1e-4/source rows closed: `{hi2022_launch_preflight['all_launch_commands_avoid_1e_4']}/{hi2022_launch_preflight['source_policy_rows_closed_by_preflight']}`.",
        f"- HI2022 preflight closes B4/B7: `{hi2022_launch_preflight['b4_can_close_after_preflight_only']}/{hi2022_launch_preflight['b7_can_close_after_preflight_only']}`.",
        f"- RA2021 executed shard evidence: `{ra2021_executed_shard_evidence['status']}`.",
        f"- RA2021 executed shard forms completed: `{ra2021_executed_shard_evidence['completed_forms']}`.",
        f"- RA2021 executed shard rows/source-policy rows closed: `{ra2021_executed_shard_evidence['ok_row_count']}/{ra2021_executed_shard_evidence['source_policy_rows_closed_by_this_shard']}`.",
        f"- Gauss6 local source-policy evidence: `{gauss6_local_source_policy_evidence['status']}`.",
        f"- Gauss6 single public-horizon rows/source-policy rows closed: `{gauss6_local_source_policy_evidence['single_public_horizon_rows']['ok_row_count']}/{gauss6_local_source_policy_evidence['source_policy_rows_closed_by_this_evidence']}`.",
        f"- Gauss6 closed-loop combined ok/failed rows: `{gauss6_local_source_policy_evidence['closed_loop_combined_ok_rows']}/{gauss6_local_source_policy_evidence['closed_loop_combined_failed_rows']}`.",
        f"- RA2021 closed-loop same-window public work/precision: `{ra2021_closed_loop_same_window_evidence['status']}`.",
        f"- RA2021 closed-loop same-window rows/available/source-policy rows closed: `{ra2021_closed_loop_same_window_evidence['ok_row_count']}/{ra2021_closed_loop_same_window_evidence['public_work_precision_available_count']}/{ra2021_closed_loop_same_window_evidence['source_policy_rows_closed_by_this_evidence']}`.",
        f"- RA2021 closed-loop strict common-reference/external superiority: `{ra2021_closed_loop_same_window_evidence['strict_common_reference_error_columns']}` / `{ra2021_closed_loop_same_window_evidence['external_superiority_claim']}`.",
        f"- RA2021 double local source-policy candidate: `{ra2021_double_local_candidate['status']}`.",
        f"- RA2021 double local candidate rows/order accepted/source-policy rows closed: `{ra2021_double_local_candidate['ok_row_count']}/{ra2021_double_local_candidate['source_policy_order_acceptance_satisfied']}/{ra2021_double_local_candidate['source_policy_rows_closed_by_this_evidence']}`.",
        f"- HI2022 full T=8 source-policy candidate: `{hi2022_full_t8_candidate['status']}`.",
        f"- HI2022 full T=8 candidate rows/full grid/source-policy rows closed: `{hi2022_full_t8_candidate['ok_row_count']}/{hi2022_full_t8_candidate['full_public_grid_selected']}/{hi2022_full_t8_candidate['source_policy_rows_closed_by_this_evidence']}`.",
        f"- HI2022 B4/B7 figure-scope demotion: `{hi2022_figure_scope_demotion['status']}`.",
        f"- HI2022 B4/B7 demotion rows/clean figure/can close: `{hi2022_figure_scope_demotion['source_policy_rows_closed_by_hi2022']}/{hi2022_figure_scope_demotion['counts_as_clean_work_precision_figure']}/{hi2022_figure_scope_demotion['b4_b7_can_close_from_hi2022']}`.",
        f"- HI2022 selected-candidate matrix completed/expected/rows closed: `{hi2022_figure_scope_demotion['t8_selected_candidate_matrix_completed_shards']}/{hi2022_figure_scope_demotion['t8_selected_candidate_matrix_expected_shards']}/{hi2022_figure_scope_demotion['t8_selected_candidate_matrix_rows_closed']}`.",
        "",
        "## Publication Contract",
        "",
        f"- Contract: `{output['publication_grade_acceptance_contract']['contract_id']}`.",
        f"- Plan-only closes rows: `{output['publication_grade_acceptance_contract']['plan_only_closes_rows']}`.",
        f"- B4 required items: `{output['publication_grade_acceptance_contract']['required_to_close_b4']}`.",
        f"- B7 required items: `{output['publication_grade_acceptance_contract']['required_to_close_b7']}`.",
        f"- Current figure set closes B7: `{output['publication_grade_acceptance_contract']['current_figure_set_b7_closed']}`.",
        f"- Current figure set supports common-reference diagnostics only: `{output['publication_grade_acceptance_contract']['current_figure_set_supports_common_reference_diagnostics_only']}`.",
        "",
        "## Execution Lanes",
        "",
        "| lane | ready after opt-in | source rows | status | first missing item |",
        "|---|---:|---:|---|---|",
    ]
    for lane in lanes:
        first_missing = lane["required_before_publication_figure"][0]
        lines.append(
            f"| `{lane['lane_id']}` | `{lane['ready_to_launch_after_explicit_opt_in']}` | "
            f"`{lane['source_policy_rows_completed']}` | `{lane['status']}` | {first_missing} |"
        )
    lines.extend(
        [
            "",
        "## Next Decision",
            "",
            f"- Recommended first lane: `{output['next_decision']['recommended_first_lane']}`.",
            f"- Requires explicit 1e-4 opt-in: `{output['next_decision']['requires_explicit_1e_4_opt_in']}`.",
            f"- Do not run by default: `{output['next_decision']['do_not_run_by_default']}`.",
            f"- Alternative without heavy runs: {output['next_decision']['alternative_if_no_heavy_runs']}",
            "",
            "The current TFE work/precision rows are diagnostic same-test or algorithm-literal rows.",
            "They are useful for scope and figure development, but they do not close B4 or B7 because they do not establish a source-policy-closed external same-test row.",
            "",
            "## TFE Runner-Equivalence Preflight",
            "",
            f"- Status: `{tfe_runner_preflight_summary['status']}`.",
            f"- Closed preconditions/open blockers: `{tfe_runner_preflight_summary['closed_precondition_count']}/{tfe_runner_preflight_summary['open_blocker_count']}`.",
            f"- Source-policy rows closed by preflight: `{tfe_runner_preflight_summary['source_policy_rows_closed_by_preflight']}`.",
            f"- Can close TFE lane from preflight: `{tfe_runner_preflight_summary['can_close_tfe_lane_from_preflight']}`.",
            f"- Heavy numerical run invoked: `{tfe_runner_preflight_summary['heavy_numerical_run_invoked']}`.",
            f"- Open blocker ids: `{tfe_runner_preflight_summary['open_blocker_ids']}`.",
            "",
            "## TFE B4/B7 Figure-Scope Demotion",
            "",
            f"- Status: `{tfe_figure_scope_demotion['status']}`.",
            f"- Source audit: `{tfe_figure_scope_demotion['source_audit']}`.",
            f"- TFE rows demoted for current claim/source-policy rows closed: `{tfe_figure_scope_demotion['demoted_related_work_proxy_rows_for_current_claim']}/{tfe_figure_scope_demotion['source_policy_rows_closed']}`.",
            f"- Source-policy rows closed by demotion: `{tfe_figure_scope_demotion['source_policy_rows_closed_by_demotion']}`.",
            f"- Future reintroduction runner/code-path rows: `{tfe_figure_scope_demotion['future_reintroduction_requires_runner_or_code_path_rows']}`.",
            f"- Current claim requires TFE source-policy execution: `{tfe_figure_scope_demotion['current_claim_requires_tfe_source_policy_execution']}`.",
            f"- Brown--McPhee source-code-equivalent law: `{tfe_figure_scope_demotion['brown_mcphee_source_code_equivalent_law']}`.",
            f"- Full T=10 source grid policy resolved: `{tfe_figure_scope_demotion['source_grid_policy_resolved_for_full_T10']}`.",
            f"- pendulum DAE runner implemented: `{tfe_figure_scope_demotion['pendulum_dae_runner_implemented']}`.",
            f"- Counts as clean work/precision figure: `{tfe_figure_scope_demotion['counts_as_clean_work_precision_figure']}`.",
            f"- B4/B7 can close from TFE demotion: `{tfe_figure_scope_demotion['b4_b7_can_close_from_tfe']}`.",
            f"- Allowed figure use: `{tfe_figure_scope_demotion['allowed_figure_use']}`.",
            f"- Forbidden figure use: `{tfe_figure_scope_demotion['forbidden_figure_use']}`.",
            "",
            "## RA2021 Launch Preflight",
            "",
            "| command id | output after run | purpose |",
            "|---|---|---|",
        ]
    )
    for command in ra2021_launch_preflight["launch_commands"]:
        lines.append(
            f"| `{command['id']}` | `{command['expected_output_after_run']}` | {command['purpose']} |"
        )
    lines.extend(
        [
            "",
            "Every RA2021 launch command requires `--allow-source-policy-1e-4` and remains unexecuted by this plan.",
            "The preflight only proves that the runner interfaces and outputs are specified; it closes zero source-policy rows.",
            f"RA2021 runner CLI contract: `{ra2021_launch_preflight['runner_cli_contract']['status']}` with `{ra2021_launch_preflight['runner_cli_contract']['runner_contract_count']}` runner checks and `{ra2021_launch_preflight['runner_cli_contract']['command_contract_count']}` command checks.",
            "",
            "## HI2022 Launch Preflight",
            "",
            f"- Status: `{hi2022_launch_preflight['status']}`.",
            f"- Runner files ready: `{hi2022_launch_preflight['runner_files_available']}`.",
            f"- Expected/completed/missing shards: `{hi2022_launch_preflight['expected_shard_count']}/{hi2022_launch_preflight['completed_shard_count']}/{len(hi2022_launch_preflight['missing_or_unexecuted_shards'])}`.",
            f"- Commands avoid 1e-4: `{hi2022_launch_preflight['all_launch_commands_avoid_1e_4']}`.",
            f"- Source-policy 1e-4 required: `{hi2022_launch_preflight['source_policy_1e_4_required']}`.",
            f"- Heavy numerical run invoked by preflight: `{hi2022_launch_preflight['heavy_numerical_run_invoked']}`.",
            f"- Source-policy rows closed by preflight: `{hi2022_launch_preflight['source_policy_rows_closed_by_preflight']}`.",
            f"- B4/B7 can close from HI2022 preflight: `{hi2022_launch_preflight['b4_can_close_after_preflight_only']}/{hi2022_launch_preflight['b7_can_close_after_preflight_only']}`.",
            f"- Runner CLI contract: `{hi2022_launch_preflight['runner_cli_contract']['status']}` with `{hi2022_launch_preflight['runner_cli_contract']['runner_contract_count']}` runner checks and `{hi2022_launch_preflight['runner_cli_contract']['command_contract_count']}` command checks.",
            "",
            "| command id | shard | output after run | current artifact status |",
            "|---|---|---|---|",
        ]
    )
    for command in hi2022_launch_preflight["launch_commands"]:
        lines.append(
            f"| `{command['id']}` | `{command['shard_id']}` | "
            f"`{command['expected_output_after_run']}` | `{command['artifact_status']}` |"
        )
    lines.extend(
        [
            "",
            "This read-only plan does not execute HI2022 commands. Existing selected-candidate artifacts are summarized separately; reruns still require explicit heavy-run opt-in.",
            "The preflight only enumerates isolated candidate shard commands; it closes zero source-policy rows.",
            "",
            "## Executed RA2021 Shards",
            "",
            f"- Forms completed: `{ra2021_executed_shard_evidence['completed_forms']}`.",
            f"- Rows ok/total: `{ra2021_executed_shard_evidence['ok_row_count']}/{ra2021_executed_shard_evidence['row_count']}`.",
            f"- Shared h values: `{ra2021_executed_shard_evidence['shared_h_values']}`.",
            f"- reference h values: `{ra2021_executed_shard_evidence['reference_h_values']}`.",
            f"- Velocity pair orders by form: `{ra2021_executed_shard_evidence['velocity_pair_orders_by_form']}`.",
            f"- Public-baseline shard rows executed: `{ra2021_executed_shard_evidence['baseline_source_policy_rows_completed_by_shards']}`.",
            f"- Counts as complete work/precision curve: `{ra2021_executed_shard_evidence['counts_as_complete_work_precision_curve']}`.",
            f"- B4/B7 can close from this evidence: `{ra2021_executed_shard_evidence['b4_can_close_from_this_evidence']}/{ra2021_executed_shard_evidence['b7_can_close_from_this_evidence']}`.",
            "",
            "| form | path | ok/total | velocity pair orders |",
            "|---|---|---:|---|",
        ]
    )
    for shard in ra2021_executed_shard_evidence["shards"]:
        lines.append(
            f"| `{shard['form']}` | `{shard['path']}` | "
            f"`{shard['ok_row_count']}/{shard['row_count']}` | `{shard['velocity_pair_orders']}` |"
        )
    lines.extend(
        [
            "",
            "## Gauss6 Local Source-Policy Evidence",
            "",
            f"- Status: `{gauss6_local_source_policy_evidence['status']}`.",
            f"- Single public-horizon step trio completed: `{gauss6_local_source_policy_evidence['single_public_horizon_step_trio_completed']}`.",
            f"- Single h values: `{gauss6_local_source_policy_evidence['single_public_horizon_rows']['h_values']}`.",
            f"- Closed-loop h=1e-4 standalone ok models: `{gauss6_local_source_policy_evidence['closed_loop_h1e4_standalone_ok_models']}`.",
            f"- Closed-loop public step trios completed: `{gauss6_local_source_policy_evidence['closed_loop_public_step_trios_completed']}`.",
            f"- Closed-loop rows are dynamic work/precision: `{gauss6_local_source_policy_evidence['closed_loop_rows_are_dynamic_work_precision']}`.",
            f"- Counts as B4 accepted source-policy rows: `{gauss6_local_source_policy_evidence['counts_as_b4_accepted_source_policy_rows']}`.",
            f"- B4/B7 can close from Gauss6 evidence: `{gauss6_local_source_policy_evidence['b4_can_close_from_this_evidence']}/{gauss6_local_source_policy_evidence['b7_can_close_from_this_evidence']}`.",
            "",
            "| shard | ok/total | failed | h values | status notes |",
            "|---|---:|---:|---|---|",
        ]
    )
    single = gauss6_local_source_policy_evidence["single_public_horizon_rows"]
    lines.append(
        f"| `single_public_horizon` | `{single['ok_row_count']}/{single['row_count']}` | "
        f"`{single['failed_row_count']}` | `{single['h_values']}` | public-horizon local trio |"
    )
    for shard in gauss6_local_source_policy_evidence["closed_loop_combined_shards"]:
        lines.append(
            f"| `{shard['model']}_combined` | `{shard['ok_row_count']}/{shard['row_count']}` | "
            f"`{shard['failed_row_count']}` | `{shard['h_values']}` | residual/kinematic, not dynamic work/precision |"
        )
    for shard in gauss6_local_source_policy_evidence["closed_loop_h1e4_standalone_shards"]:
        lines.append(
            f"| `{shard['model']}_h1e4_standalone` | `{shard['ok_row_count']}/{shard['row_count']}` | "
            f"`{shard['failed_row_count']}` | `{shard['h_values']}` | residual/kinematic standalone h=1e-4 |"
        )
    lines.extend(
        [
            "",
            "## RA2021 Closed-Loop Same-Window Work/Precision",
            "",
            f"- Status: `{ra2021_closed_loop_same_window_evidence['status']}`.",
            f"- Rows ok/total: `{ra2021_closed_loop_same_window_evidence['ok_row_count']}/{ra2021_closed_loop_same_window_evidence['row_count']}`.",
            f"- Public work/precision available examples: `{ra2021_closed_loop_same_window_evidence['public_work_precision_available_examples']}`.",
            f"- Public work/precision missing count: `{ra2021_closed_loop_same_window_evidence['public_work_precision_missing_count']}`.",
            f"- T/h/reference h: `{ra2021_closed_loop_same_window_evidence['t_end']}` / `{ra2021_closed_loop_same_window_evidence['step_sizes']}` / `{ra2021_closed_loop_same_window_evidence['reference_h']}`.",
            f"- Strict common-reference error columns: `{ra2021_closed_loop_same_window_evidence['strict_common_reference_error_columns']}`.",
            f"- Reference alignment status: `{ra2021_closed_loop_same_window_evidence['reference_alignment_status']}`.",
            f"- External superiority claim: `{ra2021_closed_loop_same_window_evidence['external_superiority_claim']}`.",
            f"- Counts as bounded same-window diagnostic: `{ra2021_closed_loop_same_window_evidence['counts_as_bounded_same_window_diagnostic']}`.",
            f"- Counts as complete RA2021 work/precision curve: `{ra2021_closed_loop_same_window_evidence['counts_as_complete_ra2021_work_precision_curve']}`.",
            f"- Source-policy rows closed by same-window evidence: `{ra2021_closed_loop_same_window_evidence['source_policy_rows_closed_by_this_evidence']}`.",
            f"- B4/B7 can close from same-window evidence: `{ra2021_closed_loop_same_window_evidence['b4_can_close_from_this_evidence']}/{ra2021_closed_loop_same_window_evidence['b7_can_close_from_this_evidence']}`.",
            "",
            "| model | local velocity order | public methods | runtime ratio vs rA |",
            "|---|---:|---|---:|",
        ]
    )
    for model, summary in ra2021_closed_loop_same_window_evidence["model_summaries"].items():
        lines.append(
            f"| `{model}` | `{summary['local_vel_observed_order']}` | "
            f"`{summary['public_methods']}` | `{summary['local_finest_runtime_ratio_vs_public_rA']}` |"
        )
    lines.extend(
        [
            "",
            "## RA2021 Double Local Source-Policy Candidate",
            "",
            f"- Status: `{ra2021_double_local_candidate['status']}`.",
            f"- Runner status: `{ra2021_double_local_candidate['runner_status']}`.",
            f"- Rows ok/total: `{ra2021_double_local_candidate['ok_row_count']}/{ra2021_double_local_candidate['row_count']}`.",
            f"- h values: `{ra2021_double_local_candidate['h_values']}`.",
            f"- reference h: `{ra2021_double_local_candidate['selected_reference_h']}`.",
            f"- Reference status/cache/runtime: `{ra2021_double_local_candidate['reference_status']}` / `{ra2021_double_local_candidate['reference_cache_exists']}` / `{ra2021_double_local_candidate['reference_runtime_sec']}`.",
            f"- Candidate position/velocity order: `{ra2021_double_local_candidate['source_policy_pos_observed_order']}` / `{ra2021_double_local_candidate['source_policy_vel_observed_order']}`.",
            f"- Position pair orders: `{ra2021_double_local_candidate['position_pair_orders']}`.",
            f"- Velocity pair orders: `{ra2021_double_local_candidate['velocity_pair_orders']}`.",
            f"- Finest pair position/velocity order: `{ra2021_double_local_candidate['finest_pair_position_order']}` / `{ra2021_double_local_candidate['finest_pair_velocity_order']}`.",
            f"- Constraint-threshold failed h values: `{ra2021_double_local_candidate['constraint_threshold_failed_h_values']}`.",
            f"- Low-order failure modes: `{ra2021_double_local_candidate['low_order_failure_modes']}`.",
            f"- Order acceptance threshold/satisfied: `{ra2021_double_local_candidate['source_policy_order_acceptance_threshold']}` / `{ra2021_double_local_candidate['source_policy_order_acceptance_satisfied']}`.",
            f"- Promotion ready: `{ra2021_double_local_candidate['promotion_ready']}`.",
            f"- Counts as B4 accepted source-policy rows: `{ra2021_double_local_candidate['counts_as_b4_accepted_source_policy_rows']}`.",
            f"- B4/B7 can close from double candidate: `{ra2021_double_local_candidate['b4_can_close_from_this_evidence']}/{ra2021_double_local_candidate['b7_can_close_from_this_evidence']}`.",
            "",
            "Promotion blockers:",
            "",
        ]
    )
    for blocker in ra2021_double_local_candidate["promotion_blockers"]:
        lines.append(f"- {blocker}")
    lines.extend(
        [
            "",
            "## HI2022 Full T=8 Source-Policy Candidate",
            "",
            f"- Status: `{hi2022_full_t8_candidate['status']}`.",
            f"- Runner statuses: `{hi2022_full_t8_candidate['runner_statuses']}`.",
            f"- Forms/models: `{hi2022_full_t8_candidate['forms']}` / `{hi2022_full_t8_candidate['models']}`.",
            f"- Summary/rows artifacts: `{hi2022_full_t8_candidate['summary_artifact_count']}/{hi2022_full_t8_candidate['rows_artifact_count']}`.",
            f"- Completed/expected shards: `{hi2022_full_t8_candidate['completed_shard_count']}/{hi2022_full_t8_candidate['expected_shard_count']}`.",
            f"- Partial-or-failed shards: `{hi2022_full_t8_candidate['partial_or_failed_shards']}`.",
            f"- Missing artifact shards: `{hi2022_full_t8_candidate['missing_artifact_shards']}`.",
            f"- Rows ok/total: `{hi2022_full_t8_candidate['ok_row_count']}/{hi2022_full_t8_candidate['row_count']}`.",
            f"- T=8/reference h selected: `{hi2022_full_t8_candidate['source_policy_time_window_selected']}` / `{hi2022_full_t8_candidate['source_policy_reference_h_selected']}`.",
            f"- h values: `{hi2022_full_t8_candidate['h_values']}`.",
            f"- reference h values: `{hi2022_full_t8_candidate['selected_reference_h_values']}`.",
            f"- Full public grid selected/completed: `{hi2022_full_t8_candidate['full_public_grid_selected']}` / `{hi2022_full_t8_candidate['full_T8_policy_completed']}`.",
            f"- Source-policy 1e-4 included: `{hi2022_full_t8_candidate['source_policy_1e_4_included']}`.",
            f"- Reference statuses/runtime values: `{hi2022_full_t8_candidate['reference_statuses']}` / `{hi2022_full_t8_candidate['reference_runtime_sec_values']}`.",
            f"- Position pair orders by shard: `{hi2022_full_t8_candidate['position_pair_orders_by_shard']}`.",
            f"- Velocity pair orders by shard: `{hi2022_full_t8_candidate['velocity_pair_orders_by_shard']}`.",
            f"- Acceleration pair orders by shard: `{hi2022_full_t8_candidate['acceleration_pair_orders_by_shard']}`.",
            f"- Runtime values: `{hi2022_full_t8_candidate['runtime_sec_values']}`.",
            f"- Counts as full public-grid source-policy: `{hi2022_full_t8_candidate['counts_as_full_public_grid_source_policy']}`.",
            f"- Counts as B4 accepted source-policy rows: `{hi2022_full_t8_candidate['counts_as_b4_accepted_source_policy_rows']}`.",
            f"- Counts as complete work/precision curve: `{hi2022_full_t8_candidate['counts_as_complete_work_precision_curve']}`.",
            f"- Source-policy rows closed by HI2022 candidate: `{hi2022_full_t8_candidate['source_policy_rows_closed_by_this_evidence']}`.",
            f"- Promotion ready: `{hi2022_full_t8_candidate['promotion_ready']}`.",
            f"- B4/B7 can close from HI2022 candidate: `{hi2022_full_t8_candidate['b4_can_close_from_this_evidence']}/{hi2022_full_t8_candidate['b7_can_close_from_this_evidence']}`.",
            "",
            "HI2022 promotion blockers:",
            "",
        ]
    )
    for blocker in hi2022_full_t8_candidate["promotion_blockers"]:
        lines.append(f"- {blocker}")
    lines.extend(
        [
            "",
            "## HI2022 B4/B7 Figure-Scope Demotion",
            "",
            f"- Status: `{hi2022_figure_scope_demotion['status']}`.",
            f"- Source audit: `{hi2022_figure_scope_demotion['source_audit']}`.",
            f"- Bounded rows ok/total: `{hi2022_figure_scope_demotion['bounded_rows_ok']}/{hi2022_figure_scope_demotion['bounded_rows_total']}`.",
            f"- T=8 coarse rows ok/total: `{hi2022_figure_scope_demotion['t8_coarse_rows_ok']}/{hi2022_figure_scope_demotion['t8_coarse_rows_total']}`.",
            f"- T=8 coarse complete groups: `{hi2022_figure_scope_demotion['t8_coarse_complete_form_model_groups']}/{hi2022_figure_scope_demotion['t8_coarse_group_count']}`.",
            f"- T=8 selected candidate rows ok/total: `{hi2022_figure_scope_demotion['t8_selected_candidate_rows_ok']}/{hi2022_figure_scope_demotion['t8_selected_candidate_rows_total']}`.",
            f"- T=8 selected candidate full public grid: `{hi2022_figure_scope_demotion['t8_selected_candidate_full_public_grid_selected']}`.",
            f"- T=8 selected candidate matrix status: `{hi2022_figure_scope_demotion['t8_selected_candidate_matrix_status']}`.",
            f"- T=8 selected candidate matrix completed/expected: `{hi2022_figure_scope_demotion['t8_selected_candidate_matrix_completed_shards']}/{hi2022_figure_scope_demotion['t8_selected_candidate_matrix_expected_shards']}`.",
            f"- T=8 selected candidate matrix rows ok/total: `{hi2022_figure_scope_demotion['t8_selected_candidate_matrix_rows_ok']}/{hi2022_figure_scope_demotion['t8_selected_candidate_matrix_rows_total']}`.",
            f"- T=8 selected candidate matrix commands/count avoid 1e-4: `{hi2022_figure_scope_demotion['t8_selected_candidate_matrix_command_count']}` / `{hi2022_figure_scope_demotion['t8_selected_candidate_matrix_commands_avoid_1e_4']}`.",
            f"- T=8 selected candidate matrix heavy run invoked: `{hi2022_figure_scope_demotion['t8_selected_candidate_matrix_heavy_run_invoked']}`.",
            f"- T=8 selected candidate matrix rows closed/can close: `{hi2022_figure_scope_demotion['t8_selected_candidate_matrix_rows_closed']}` / `{hi2022_figure_scope_demotion['t8_selected_candidate_matrix_b4_b7_can_close']}`.",
            f"- T=8 selected candidate matrix partial-or-failed shards: `{hi2022_figure_scope_demotion['t8_selected_candidate_matrix_partial_or_failed_shards']}`.",
            f"- T=8 selected candidate matrix missing artifact shards: `{hi2022_figure_scope_demotion['t8_selected_candidate_matrix_missing_artifact_shards']}`.",
            f"- Source-policy rows closed by HI2022: `{hi2022_figure_scope_demotion['source_policy_rows_closed_by_hi2022']}`.",
            f"- Counts as clean work/precision figure: `{hi2022_figure_scope_demotion['counts_as_clean_work_precision_figure']}`.",
            f"- B4/B7 can close from HI2022: `{hi2022_figure_scope_demotion['b4_b7_can_close_from_hi2022']}`.",
            f"- Allowed figure use: `{hi2022_figure_scope_demotion['allowed_figure_use']}`.",
            f"- Forbidden figure use: `{hi2022_figure_scope_demotion['forbidden_figure_use']}`.",
            "",
            "HI2022 demotion gaps:",
            "",
        ]
    )
    for gap in hi2022_figure_scope_demotion["promotion_gap"]:
        lines.append(f"- {gap}")
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("b4_source_policy_work_precision_execution_plan=written")
    print(f"source_policy_rows_closed={source_policy_rows_closed}")
    print(f"source_policy_rows_total={source_policy_rows_total}")
    print(f"ready_to_launch_after_explicit_opt_in_count={executable_lane_count}")
    print(f"not_ready_lane_count={not_ready_lane_count}")
    print("b4_can_close_now=False")
    print("b7_can_close_now=False")


if __name__ == "__main__":
    main()
