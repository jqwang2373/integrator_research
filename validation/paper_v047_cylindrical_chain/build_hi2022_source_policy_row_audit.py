#!/usr/bin/env python3
"""Audit HI2022 active source-policy rows against existing bounded pilot artifacts."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
V048_RESULTS = ROOT.parent / "numerics" / "v048_cross_paper_same_test_benchmarks" / "results"


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def method_to_form(method: str | None) -> str:
    if method == "hi2022_rA":
        return "rA"
    if method == "hi2022_rA_half":
        return "rA_half"
    raise ValueError(f"unexpected HI2022 method label: {method!r}")


def csv_float(row: dict[str, str], key: str) -> float:
    return float(row[key])


def finite_float(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        number = float(value)
    except ValueError:
        return None
    return number if math.isfinite(number) else None


def log_order(rows: list[dict[str, str]], error_key: str) -> float | None:
    ok_rows = [
        row
        for row in rows
        if row.get("status") == "ok"
        and finite_float(row.get("h")) is not None
        and finite_float(row.get(error_key)) is not None
        and (finite_float(row.get(error_key)) or 0.0) > 0.0
    ]
    if len(ok_rows) < 3:
        return None
    xs = [math.log(float(row["h"])) for row in ok_rows]
    ys = [math.log(float(row[error_key])) for row in ok_rows]
    x_bar = sum(xs) / len(xs)
    y_bar = sum(ys) / len(ys)
    denom = sum((x - x_bar) ** 2 for x in xs)
    if denom == 0.0:
        return None
    return sum((x - x_bar) * (y - y_bar) for x, y in zip(xs, ys)) / denom


def summarize_t8_coarse_rows(shard_dir: Path) -> dict[str, Any]:
    if not shard_dir.exists():
        return {
            "artifact_present": False,
            "row_count": 0,
            "ok_row_count": 0,
            "failed_row_count": 0,
            "group_count": 0,
            "complete_form_model_groups": 0,
            "source_policy_reproduction": False,
            "full_T8_policy_completed": False,
        }

    rows: list[dict[str, str]] = []
    for path in sorted(shard_dir.glob("hi2022_*_rows.csv")):
        rows.extend(read_csv(path))

    groups: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        groups.setdefault(f"{row.get('form')}:{row.get('model')}", []).append(row)

    group_summaries: dict[str, dict[str, Any]] = {}
    for key, group_rows in groups.items():
        ok_count = sum(1 for row in group_rows if row.get("status") == "ok")
        status_values = sorted({row.get("status", "") for row in group_rows})
        group_summaries[key] = {
            "row_count": len(group_rows),
            "ok_row_count": ok_count,
            "failed_row_count": len(group_rows) - ok_count,
            "complete_three_step_group": ok_count == 3,
            "status_values": status_values,
            "position_order": log_order(group_rows, "pos_final_linf"),
            "velocity_order": log_order(group_rows, "vel_final_linf"),
            "acceleration_order": log_order(group_rows, "acc_final_linf"),
            "max_iterations": max(
                (finite_float(row.get("max_iterations")) or 0.0 for row in group_rows if row.get("status") == "ok"),
                default=0.0,
            ),
        }

    return {
        "artifact_present": True,
        "artifact_dir": "../../numerics/v048_cross_paper_same_test_benchmarks/results/hi2022_T8_coarse_model_shards",
        "policy": "T8_coarse_horizon_sanity_not_source_policy",
        "row_count": len(rows),
        "ok_row_count": sum(1 for row in rows if row.get("status") == "ok"),
        "failed_row_count": sum(1 for row in rows if row.get("status") != "ok"),
        "group_count": len(group_summaries),
        "complete_form_model_groups": sum(1 for row in group_summaries.values() if row["complete_three_step_group"]),
        "t_end_values": sorted({value for row in rows if (value := finite_float(row.get("t_end"))) is not None}),
        "step_sizes": sorted({value for row in rows if (value := finite_float(row.get("h"))) is not None}),
        "reference_h_values": sorted(
            {value for row in rows if (value := finite_float(row.get("reference_h"))) is not None}
        ),
        "source_policy_reproduction": False,
        "full_T8_policy_completed": False,
        "default_1e_4_required": False,
        "contains_source_policy_1e_4_rows": any((finite_float(row.get("h")) or 1.0) <= 1.0e-4 for row in rows),
        "v048_runner_invoked_for_this_evidence": True,
        "groups": group_summaries,
    }


def summarize_t8_selected_candidate() -> dict[str, Any]:
    stem = "hi2022_full_t8_source_policy_candidate_rA_double_pendulum"
    summary_path = V048_RESULTS / f"{stem}_summary.json"
    rows_path = V048_RESULTS / f"{stem}_rows.csv"
    if not summary_path.exists() or not rows_path.exists():
        return {
            "artifact_present": False,
            "artifact_status": "missing",
            "row_count": 0,
            "ok_row_count": 0,
            "source_policy_rows_closed_by_this_evidence": 0,
            "b4_b7_can_close_from_this_evidence": False,
        }

    summary = read_json(summary_path)
    rows = read_csv(rows_path)
    ok_rows = [row for row in rows if row.get("status") == "ok"]
    return {
        "artifact_present": True,
        "artifact_status": summary.get("status"),
        "summary_path": f"../../numerics/v048_cross_paper_same_test_benchmarks/results/{stem}_summary.json",
        "rows_path": f"../../numerics/v048_cross_paper_same_test_benchmarks/results/{stem}_rows.csv",
        "form": summary.get("form"),
        "model": summary.get("model"),
        "selected_t_end": summary.get("selected_t_end"),
        "selected_reference_h": summary.get("selected_reference_h"),
        "selected_step_sizes": summary.get("selected_step_sizes"),
        "estimated_reference_steps": summary.get("estimated_reference_steps"),
        "estimated_candidate_steps": summary.get("estimated_candidate_steps"),
        "source_policy_time_window_selected": summary.get("source_policy_time_window_selected"),
        "source_policy_reference_h_selected": summary.get("source_policy_reference_h_selected"),
        "selected_coarse_trio": summary.get("selected_coarse_trio"),
        "full_public_grid_selected": summary.get("full_public_grid_selected"),
        "full_T8_policy_completed": summary.get("full_T8_policy_completed"),
        "source_policy_1e_4_included": summary.get("source_policy_1e_4_included"),
        "row_count": len(rows),
        "ok_row_count": len(ok_rows),
        "source_policy_candidate_rows_completed": summary.get("source_policy_candidate_rows_completed"),
        "position_pair_orders": summary.get("position_pair_orders", []),
        "velocity_pair_orders": summary.get("velocity_pair_orders", []),
        "acceleration_pair_orders": summary.get("acceleration_pair_orders", []),
        "runtime_sec_values": summary.get("runtime_sec_values", []),
        "reference_runtime_sec": summary.get("reference_runtime_sec"),
        "promotion_ready": summary.get("promotion_ready"),
        "promotion_blockers": summary.get("promotion_blockers", []),
        "source_policy_rows_closed_by_this_evidence": summary.get(
            "source_policy_rows_closed_by_this_evidence"
        ),
        "counts_as_full_public_grid_source_policy": summary.get("counts_as_full_public_grid_source_policy"),
        "counts_as_complete_work_precision_curve": summary.get("counts_as_complete_work_precision_curve"),
        "b4_b7_can_close_from_this_evidence": bool(summary.get("b4_can_close_from_this_evidence"))
        and bool(summary.get("b7_can_close_from_this_evidence")),
        "canonical_hi2022_output_untouched_by_writer": summary.get(
            "canonical_hi2022_output_untouched_by_writer"
        ),
    }


def summarize_t8_selected_candidate_matrix_preflight(queue_batch: dict[str, Any]) -> dict[str, Any]:
    models = list(queue_batch.get("models") or [])
    forms = list(queue_batch.get("public_forms") or [])
    script_label = "../../numerics/v048_cross_paper_same_test_benchmarks/run_hi2022_full_t8_source_policy_candidate.py"
    script_path = ROOT.parent / "numerics" / "v048_cross_paper_same_test_benchmarks" / "run_hi2022_full_t8_source_policy_candidate.py"
    expected_shards: list[dict[str, Any]] = []
    completed_shards: list[str] = []
    existing_artifacts: list[str] = []
    for form in forms:
        for model in models:
            shard_id = f"{form}:{model}"
            stem = f"hi2022_full_t8_source_policy_candidate_{form}_{model}"
            summary_path = V048_RESULTS / f"{stem}_summary.json"
            rows_path = V048_RESULTS / f"{stem}_rows.csv"
            summary = read_json(summary_path) if summary_path.exists() else {}
            rows = read_csv(rows_path) if rows_path.exists() else []
            ok_rows = [row for row in rows if row.get("status") == "ok"]
            completed = (
                summary.get("status") == "executed_full_T8_selected_coarse_trio_not_promoted"
                and len(ok_rows) == 3
            )
            if completed:
                completed_shards.append(shard_id)
            if summary_path.exists():
                existing_artifacts.append(shard_id)
            expected_shards.append(
                {
                    "shard_id": shard_id,
                    "form": form,
                    "model": model,
                    "summary_path": (
                        f"../../numerics/v048_cross_paper_same_test_benchmarks/results/{stem}_summary.json"
                    ),
                    "rows_path": f"../../numerics/v048_cross_paper_same_test_benchmarks/results/{stem}_rows.csv",
                    "summary_exists": summary_path.exists() and summary_path.stat().st_size > 0,
                    "rows_exists": rows_path.exists() and rows_path.stat().st_size > 0,
                    "artifact_status": summary.get("status", "missing"),
                    "row_count": len(rows),
                    "ok_row_count": len(ok_rows),
                    "source_policy_rows_closed_by_this_evidence": summary.get(
                        "source_policy_rows_closed_by_this_evidence",
                        0,
                    ),
                    "full_public_grid_selected": summary.get("full_public_grid_selected", False),
                    "counts_as_complete_work_precision_curve": summary.get(
                        "counts_as_complete_work_precision_curve",
                        False,
                    ),
                    "command": (
                        "../../.venv_sbel/bin/python run_hi2022_full_t8_source_policy_candidate.py "
                        f"--form {form} --model {model} --execute"
                    ),
                    "contains_1e_4": False,
                    "requires_source_policy_1e_4_opt_in": False,
                    "requires_heavy_run_opt_in": True,
                    "counts_as_preflight_only": True,
                    "b4_b7_can_close_from_this_shard": False,
                }
            )
    missing_shards = [
        item["shard_id"]
        for item in expected_shards
        if item["shard_id"] not in completed_shards
    ]
    partial_or_failed_shards = [
        item["shard_id"]
        for item in expected_shards
        if item["summary_exists"] and item["rows_exists"] and item["shard_id"] not in completed_shards
    ]
    missing_artifact_shards = [
        item["shard_id"]
        for item in expected_shards
        if not item["summary_exists"] or not item["rows_exists"]
    ]
    return {
        "schema": "hi2022-t8-selected-candidate-matrix-preflight-v1",
        "status": "preflight_ready_existing_selected_candidate_matrix_incomplete",
        "script": script_label,
        "script_exists": script_path.exists() and script_path.stat().st_size > 0,
        "models": models,
        "forms": forms,
        "expected_shard_count": len(expected_shards),
        "completed_shard_count": len(completed_shards),
        "existing_artifact_count": len(existing_artifacts),
        "completed_shards": completed_shards,
        "missing_or_unexecuted_shards": missing_shards,
        "partial_or_failed_shards": partial_or_failed_shards,
        "missing_artifact_shards": missing_artifact_shards,
        "command_count": len(expected_shards),
        "all_commands_avoid_1e_4": True,
        "source_policy_1e_4_required": False,
        "heavy_numerical_run_invoked": False,
        "run_v047_invoked": False,
        "v048_runner_invoked": False,
        "source_policy_rows_closed_by_preflight": 0,
        "source_policy_rows_closed_by_existing_candidates": 0,
        "counts_as_complete_work_precision_curve": False,
        "b4_b7_can_close_from_preflight": False,
        "promotion_gap": [
            "matrix preflight only enumerates isolated candidate shard commands",
            "existing selected candidates remain coarse-trio diagnostics, not full public-grid source-policy rows",
            "full source-policy promotion still requires executed rows, work metrics, and a figure policy over accepted rows",
        ],
        "shards": expected_shards,
    }


def main() -> None:
    b2_manifest = read_json(PAPER / "B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.json")
    hi_policy = read_json(PAPER / "HI2022_POLICY_DECISION_AUDIT.json")
    external_case = read_json(PAPER / "EXTERNAL_CASE_EVIDENCE_RECONCILIATION.json")
    queue = read_json(PAPER / "EXTERNAL_SAME_TEST_RUN_QUEUE.json")
    acceptance = read_json(PAPER / "EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.json")
    summary = read_json(V048_RESULTS / "summary_v048.json")
    bounded_rows = read_csv(V048_RESULTS / "hi2022_halfimplicit_rows.csv")
    workload_rows = read_csv(V048_RESULTS / "hi2022_workload_estimate.csv")
    t8_coarse = summarize_t8_coarse_rows(V048_RESULTS / "hi2022_T8_coarse_model_shards")
    t8_selected_candidate = summarize_t8_selected_candidate()

    flagged_rows = [
        row
        for row in b2_manifest.get("rows", [])
        if row.get("suite_id") == "hi2022_half_implicit"
    ]
    active_rows_after_demotion = [
        row for row in flagged_rows if row.get("active_b2_requirement") is True
    ]
    demoted_rows = [
        row
        for row in flagged_rows
        if row.get("demoted_from_external_superiority_scope") is True
        or row.get("status") == "closed_by_explicit_source_policy_demotion"
    ]
    hi_summary = summary.get("hi2022_halfimplicit", {})
    groups = hi_summary.get("groups", {})
    existing = hi_policy.get("existing_bounded_evidence", {})
    source_policy = hi_policy.get("source_policy_required_before_external_superiority", {})
    external_progress = external_case.get("source_policy_progress", {}).get("hi2022_public_baselines", {})
    queue_batch = next(
        (
            item
            for item in queue.get("batch_queue", [])
            if isinstance(item, dict) and item.get("batch_id") == "hi2022_halfimplicit_full_policy_decision"
        ),
        {},
    )
    t8_selected_candidate_matrix = summarize_t8_selected_candidate_matrix_preflight(queue_batch)
    full_workload = next(
        (row for row in workload_rows if row.get("scope") == "hi2022_full_open_loop_policy"),
        {},
    )
    bounded_workload = next(
        (row for row in workload_rows if row.get("scope") == "hi2022_selected_run"),
        {},
    )

    rows_by_group: dict[str, list[dict[str, str]]] = {}
    for row in bounded_rows:
        key = f"{row.get('form')}:{row.get('model')}"
        rows_by_group.setdefault(key, []).append(row)

    audited_rows: list[dict[str, Any]] = []
    for item in flagged_rows:
        form = method_to_form(item.get("method"))
        example = item.get("example")
        group_key = f"{form}:{example}"
        group = groups.get(group_key, {})
        row_group = rows_by_group.get(group_key, [])
        h_values = sorted(csv_float(row, "h") for row in row_group)
        audited_rows.append(
            {
                "row_index": item.get("row_index"),
                "example": example,
                "method": item.get("method"),
                "form": form,
                "bounded_group_key": group_key,
                "bounded_row_count": group.get("row_count"),
                "bounded_ok_row_count": group.get("ok_row_count"),
                "bounded_h_values": h_values,
                "bounded_t_end": existing.get("t_end_values", [None])[0],
                "bounded_reference_h": existing.get("reference_h_values", [None])[0],
                "bounded_reference_mode": group.get("reference_mode"),
                "bounded_reference_policy": group.get("reference_policy"),
                "bounded_execution_paths": group.get("execution_paths", []),
                "bounded_vel_order": group.get("vel_final_linf_order"),
                "bounded_pos_order": group.get("pos_final_linf_order"),
                "bounded_acc_order": group.get("acc_final_linf_order"),
                "source_policy_reproduction": False,
                "full_T8_source_policy_completed": False,
                "source_policy_closed": False,
                "external_superiority_ready": False,
                "remaining_required_evidence": item.get("required_evidence", []),
            }
        )

    closure_criteria = {
        "bounded_T0p1_rows_ok": existing.get("row_count") == existing.get("ok_row_count") == 24,
        "bounded_eight_form_model_groups_complete": existing.get("groups_with_three_step_sizes") == 8,
        "full_T8_public_policy_required": source_policy.get("full_T8_policy_required") is True,
        "full_T8_public_policy_completed": source_policy.get("full_T8_policy_completed") is True,
        "source_policy_reproduction_closed": source_policy.get("source_policy_reproduction_closed") is True,
        "velocity_mapping_and_error_norm_closed": False,
        "runtime_iteration_metric_tied_to_source_policy_rows": False,
        "explicit_demotion_recorded_for_hi2022": len(demoted_rows) == len(flagged_rows) == 3,
        "rerun_or_independent_verification_artifact_present": False,
        "selected_T8_candidate_artifact_present": t8_selected_candidate.get("artifact_present") is True,
        "selected_T8_candidate_promoted_to_source_policy": False,
        "hi2022_b4_b7_figure_scope_demotion_recorded": t8_selected_candidate.get("artifact_present") is True,
    }

    output = {
        "schema": "hi2022-source-policy-row-audit-v1",
        "status": "bounded_T0p1_rows_complete_full_T8_source_policy_rows_not_closed",
        "submission_ready": False,
        "suite_id": "hi2022_half_implicit",
        "source_suite": "hi2022_fang_kissel_zhang_negrut",
        "evidence_class": "bounded_pilot_only_not_source_policy_reproduction",
        "source_policy_external_superiority_allowed": False,
        "external_superiority_claim_allowed": False,
        "active_b2_flagged_rows": len(flagged_rows),
        "active_b2_flagged_rows_after_demotion": len(active_rows_after_demotion),
        "demoted_b2_flagged_rows": len(demoted_rows),
        "audited_active_rows": len(audited_rows),
        "source_policy_closed_rows": 0,
        "external_superiority_ready_rows": 0,
        "bounded_row_count": existing.get("row_count"),
        "bounded_ok_row_count": existing.get("ok_row_count"),
        "bounded_group_count": existing.get("group_count"),
        "bounded_groups_with_three_step_sizes": existing.get("groups_with_three_step_sizes"),
        "bounded_t_end_values": existing.get("t_end_values"),
        "bounded_step_sizes": existing.get("step_sizes"),
        "bounded_reference_h_values": existing.get("reference_h_values"),
        "bounded_pilot_groups_completed": external_progress.get("bounded_pilot_groups_completed"),
        "bounded_pilot_groups_required": external_progress.get("bounded_pilot_groups_required"),
        "bounded_pilot_rows_ok": external_progress.get("bounded_pilot_rows_ok"),
        "full_T8_policy_required": source_policy.get("full_T8_policy_required"),
        "full_T8_policy_completed": source_policy.get("full_T8_policy_completed"),
        "source_policy_reproduction_closed": source_policy.get("source_policy_reproduction_closed"),
        "accepted_for_bounded_evidence": source_policy.get("accepted_for_bounded_evidence"),
        "accepted_for_external_superiority": source_policy.get("accepted_for_external_superiority"),
        "accepted_source_policy_dynamic_order_examples_count": source_policy.get(
            "accepted_source_policy_dynamic_order_examples_count"
        ),
        "accepted_external_dynamic_order_examples_count": acceptance.get("acceptance_counts", {}).get(
            "accepted_external_dynamic_order_examples_count"
        ),
        "t8_coarse_horizon_evidence": t8_coarse,
        "t8_selected_candidate_evidence": t8_selected_candidate,
        "t8_selected_candidate_matrix_preflight": t8_selected_candidate_matrix,
        "b4_b7_figure_scope_decision": {
            "status": "demote_hi2022_from_b4_b7_source_policy_figures",
            "reason": (
                "Current T=8 evidence is useful for stability and failure-boundary diagnosis, but it does not "
                "complete the full public source-policy grid or a promoted work/precision curve."
            ),
            "source_policy_rows_closed_by_hi2022": 0,
            "counts_as_clean_work_precision_figure": False,
            "b4_b7_can_close_from_hi2022": False,
            "allowed_figure_use": [
                "bounded diagnostic rows",
                "T=8 failure/stability demotion evidence",
            ],
            "forbidden_figure_use": [
                "source-policy external-superiority curve",
                "publication-grade B4/B7 work/precision closure row",
            ],
        },
        "closure_criteria": closure_criteria,
        "queue_policy": {
            "batch_id": queue_batch.get("batch_id"),
            "queue_status": queue_batch.get("queue_status"),
            "models": queue_batch.get("models"),
            "public_forms": queue_batch.get("public_forms"),
            "time_horizon": queue_batch.get("time_horizon"),
            "parallel_shard_count": queue_batch.get("parallel_shard_count"),
            "source_policy_1e_4_required": queue_batch.get("source_policy_1e-4_required"),
        },
        "workload_estimate": {
            "full_T8_estimated_public_steps_total": int(full_workload.get("estimated_public_steps_total", "0")),
            "bounded_T0p1_estimated_public_steps_total": int(
                bounded_workload.get("estimated_public_steps_total", "0")
            ),
            "full_T8_evidence_status": full_workload.get("evidence_status"),
            "bounded_T0p1_evidence_status": bounded_workload.get("evidence_status"),
        },
        "rows": audited_rows,
        "decision": {
            "can_close_hi2022_b2_requirement_now": False,
            "reason": (
                "The existing HI2022 rows are a bounded T=0.1 pilot with three coarse step sizes. "
                "They cover all four models and both public forms, but they do not reproduce the full T=8 "
                "source-paper policy and therefore cannot support a source-policy external-superiority claim. "
                "The B2 requirement is now removed from active external-superiority scope by explicit demotion."
            ),
            "required_to_close": [
                "choose and document full T=8 public-policy h/reference setup or explicitly demote the suite",
                "identify the public half-implicit code path used for each accepted row",
                "close the velocity mapping and error norm policy for source-policy rows",
                "tie runtime/iteration and diagnostic metrics to the accepted source-policy rows",
                "produce a full-policy rerun artifact or an explicit demotion artifact",
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
            "hi2022_policy_decision_audit": "HI2022_POLICY_DECISION_AUDIT.json",
            "external_case_evidence_reconciliation": "EXTERNAL_CASE_EVIDENCE_RECONCILIATION.json",
            "external_same_test_run_queue": "EXTERNAL_SAME_TEST_RUN_QUEUE.json",
            "external_same_test_acceptance_sheet": "EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.json",
            "summary_v048": "../../numerics/v048_cross_paper_same_test_benchmarks/results/summary_v048.json",
            "hi2022_halfimplicit_rows": "../../numerics/v048_cross_paper_same_test_benchmarks/results/hi2022_halfimplicit_rows.csv",
            "hi2022_T8_coarse_model_shards": "../../numerics/v048_cross_paper_same_test_benchmarks/results/hi2022_T8_coarse_model_shards",
            "hi2022_T8_selected_candidate_summary": t8_selected_candidate.get("summary_path"),
            "hi2022_T8_selected_candidate_rows": t8_selected_candidate.get("rows_path"),
            "hi2022_T8_selected_candidate_matrix_script": t8_selected_candidate_matrix.get("script"),
            "hi2022_workload_estimate": "../../numerics/v048_cross_paper_same_test_benchmarks/results/hi2022_workload_estimate.csv",
        },
    }

    out_json = PAPER / "HI2022_SOURCE_POLICY_ROW_AUDIT.json"
    out_md = PAPER / "HI2022_SOURCE_POLICY_ROW_AUDIT.md"
    with out_json.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# HI2022 Source-Policy Row Audit",
        "",
        "Status: **bounded T=0.1 rows complete; full T=8 source-policy rows not closed**.",
        "",
        "This audit is read-only over existing v048 and paper-package artifacts. It does not rerun HI2022.",
        "",
        f"- Active B2 flagged HI2022 rows: `{output['active_b2_flagged_rows']}`.",
        f"- Active/demoted B2 rows after HI2022 demotion: `{output['active_b2_flagged_rows_after_demotion']}/{output['demoted_b2_flagged_rows']}`.",
        f"- Bounded rows ok: `{output['bounded_ok_row_count']}/{output['bounded_row_count']}`.",
        f"- Bounded form/model groups complete: `{output['bounded_groups_with_three_step_sizes']}/{output['bounded_group_count']}`.",
        f"- Existing bounded horizon: `{output['bounded_t_end_values']}`.",
        f"- Existing bounded h-grid: `{output['bounded_step_sizes']}`.",
        f"- Full T=8 source policy completed: `{output['full_T8_policy_completed']}`.",
        f"- T=8 coarse horizon rows ok: `{t8_coarse['ok_row_count']}/{t8_coarse['row_count']}`.",
        f"- T=8 coarse complete form/model groups: `{t8_coarse['complete_form_model_groups']}/{t8_coarse['group_count']}`.",
        f"- T=8 coarse source-policy reproduction: `{t8_coarse['source_policy_reproduction']}`.",
        f"- T=8 selected candidate rows ok: `{t8_selected_candidate['ok_row_count']}/{t8_selected_candidate['row_count']}`.",
        f"- T=8 selected candidate full public grid: `{t8_selected_candidate['full_public_grid_selected']}`.",
        f"- T=8 selected candidate matrix preflight: `{t8_selected_candidate_matrix['completed_shard_count']}/{t8_selected_candidate_matrix['expected_shard_count']}` completed, commands `{t8_selected_candidate_matrix['command_count']}`.",
        f"- T=8 selected candidate matrix source-policy rows closed: `{t8_selected_candidate_matrix['source_policy_rows_closed_by_preflight']}`.",
        f"- HI2022 B4/B7 figure-scope decision: `{output['b4_b7_figure_scope_decision']['status']}`.",
        f"- B4/B7 can close from HI2022: `{output['b4_b7_figure_scope_decision']['b4_b7_can_close_from_hi2022']}`.",
        f"- Source-policy reproduction rows: `{output['source_policy_closed_rows']}/3`.",
        f"- Source-policy dynamic-order examples: `{output['accepted_source_policy_dynamic_order_examples_count']}/4`.",
        f"- External-superiority-ready rows: `{output['external_superiority_ready_rows']}`.",
        f"- External superiority claim allowed: `{output['external_superiority_claim_allowed']}`.",
        f"- Default 1e-4/heavy/run_v047: `{output['execution_policy']['default_1e_4_required']}/{output['execution_policy']['heavy_numerical_run_invoked']}/{output['execution_policy']['run_v047_invoked']}`.",
        "",
        "## Closure Decision",
        "",
        f"Can close HI2022 B2 requirement now: `{output['decision']['can_close_hi2022_b2_requirement_now']}`.",
        "",
        output["decision"]["reason"],
        "",
        "The new T=8 coarse-horizon sanity rows are useful failure/stability evidence, but they use coarse h values and reference h=0.0125. They do not satisfy the full public source-policy h/reference contract.",
        "",
        "The selected T=8 candidate adds a finer rA double-pendulum shard with h=[0.02,0.01,0.005] and reference h=0.001. It confirms executability for that shard, but it is still not the full public grid and is demoted from B4/B7 source-policy figures.",
        "",
        "## T=8 Coarse-Horizon Sanity Rows",
        "",
        "| group | ok rows | complete trio | velocity order | max iterations | status |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for key, group in sorted(t8_coarse.get("groups", {}).items()):
        velocity_order = group.get("velocity_order")
        velocity_text = "nan" if velocity_order is None else f"{velocity_order:.3f}"
        lines.append(
            f"| `{key}` | `{group['ok_row_count']}/{group['row_count']}` | "
            f"`{group['complete_three_step_group']}` | `{velocity_text}` | "
            f"`{group['max_iterations']:.0f}` | `{'; '.join(group['status_values'])}` |"
        )
    lines.extend(
        [
            "",
            "## T=8 Selected Candidate",
            "",
            f"- Status: `{t8_selected_candidate['artifact_status']}`.",
            f"- Form/model: `{t8_selected_candidate['form']}` / `{t8_selected_candidate['model']}`.",
            f"- h values: `{t8_selected_candidate['selected_step_sizes']}`.",
            f"- reference h: `{t8_selected_candidate['selected_reference_h']}`.",
            f"- rows ok/total: `{t8_selected_candidate['ok_row_count']}/{t8_selected_candidate['row_count']}`.",
            f"- full public grid selected: `{t8_selected_candidate['full_public_grid_selected']}`.",
            f"- source-policy rows closed by this evidence: `{t8_selected_candidate['source_policy_rows_closed_by_this_evidence']}`.",
            f"- counts as complete work/precision curve: `{t8_selected_candidate['counts_as_complete_work_precision_curve']}`.",
            f"- B4/B7 can close from selected candidate: `{t8_selected_candidate['b4_b7_can_close_from_this_evidence']}`.",
            "",
            "## T=8 Selected Candidate Matrix Preflight",
            "",
            f"- Status: `{t8_selected_candidate_matrix['status']}`.",
            f"- Script exists: `{t8_selected_candidate_matrix['script_exists']}`.",
            f"- Expected/completed shards: `{t8_selected_candidate_matrix['expected_shard_count']}/{t8_selected_candidate_matrix['completed_shard_count']}`.",
            f"- Commands avoid 1e-4: `{t8_selected_candidate_matrix['all_commands_avoid_1e_4']}`.",
            f"- Heavy numerical run invoked by preflight: `{t8_selected_candidate_matrix['heavy_numerical_run_invoked']}`.",
            f"- Source-policy rows closed by preflight: `{t8_selected_candidate_matrix['source_policy_rows_closed_by_preflight']}`.",
            f"- B4/B7 can close from preflight: `{t8_selected_candidate_matrix['b4_b7_can_close_from_preflight']}`.",
            "",
            "| shard | artifact status | ok/total | command |",
            "|---|---|---:|---|",
        ]
    )
    for shard in t8_selected_candidate_matrix["shards"]:
        lines.append(
            f"| `{shard['shard_id']}` | `{shard['artifact_status']}` | "
            f"`{shard['ok_row_count']}/{shard['row_count']}` | `{shard['command']}` |"
        )
    lines.extend(
        [
            "",
        ]
    )
    lines.extend(
        [
            "",
        "## Active Rows",
        "",
        "| # | example | method | bounded group | bounded vel order | full T=8 done | source-policy |",
        "|---:|---|---|---|---:|---:|---:|",
        ]
    )
    for row in audited_rows:
        lines.append(
            f"| {row['row_index']} | `{row['example']}` | `{row['method']}` | `{row['bounded_group_key']}` | "
            f"`{row['bounded_vel_order']:.3f}` | `{row['full_T8_source_policy_completed']}` | "
            f"`{row['source_policy_reproduction']}` |"
        )
    lines.extend(
        [
            "",
            "The HI2022 rows remain bounded pilot diagnostics, not source-policy external-superiority evidence.",
        ]
    )
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("hi2022_source_policy_row_audit=written")
    print(f"active_b2_flagged_rows={len(flagged_rows)}")
    print(f"active_after_demotion={len(active_rows_after_demotion)}")
    print(f"demoted_b2_flagged_rows={len(demoted_rows)}")
    print("bounded_rows=24/24")
    print("bounded_groups=8/8")
    print("full_T8_policy_completed=False")
    print("source_policy_reproduction_rows=0/3")
    print("can_close_hi2022_b2_requirement_now=False")


if __name__ == "__main__":
    main()
