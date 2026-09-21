#!/usr/bin/env python3
"""Build a read-only audit of local candidate gaps for source-policy closure."""

from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
V048_RESULTS = PAPER.parent.parent / "numerics" / "v048_cross_paper_same_test_benchmarks" / "results"
OUT_JSON = PAPER / "SOURCE_POLICY_LOCAL_CANDIDATE_GAP_AUDIT.json"
OUT_MD = PAPER / "SOURCE_POLICY_LOCAL_CANDIDATE_GAP_AUDIT.md"


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


def bool_cell(value: object) -> bool:
    return str(value).strip().lower() == "true"


def sorted_floats(rows: list[dict[str, str]], key: str) -> list[float]:
    values = {value for row in rows if (value := as_float(row.get(key))) is not None}
    return sorted(values)


def ok_count(rows: list[dict[str, str]]) -> int:
    return sum(1 for row in rows if row.get("status") == "ok")


def group_by(rows: list[dict[str, str]], key: str) -> dict[str, list[dict[str, str]]]:
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[str(row.get(key))].append(row)
    return dict(groups)


def summarize_ra2021() -> dict[str, Any]:
    single_rows = read_csv(V048_RESULTS / "gauss6_fullva_public_horizon_single_rows.csv")
    double_rows = read_csv(V048_RESULTS / "gauss6_fullva_public_horizon_double_coarse_rows.csv")
    closed_rows = read_csv(V048_RESULTS / "gauss6_fullva_public_horizon_closed_loop_rows.csv")
    public_summary = read_csv(V048_RESULTS / "ra2021_public_order_work_summary.csv")
    public_timing = read_csv(V048_RESULTS / "ra2021_public_timing_rows.csv")
    true_dynamic = read_json(V048_RESULTS / "closed_loop_true_dynamic_newton_coarse_order.json")
    public_work = read_json(V048_RESULTS / "closed_loop_true_dynamic_public_work_precision.json")
    readiness_gate = read_json(V048_RESULTS / "coarse_first_external_readiness_gate.json")

    closed_by_model = group_by(closed_rows, "model")
    closed_model_summary = {}
    for model, rows in sorted(closed_by_model.items()):
        closed_model_summary[model] = {
            "row_count": len(rows),
            "ok_row_count": ok_count(rows),
            "h_values": sorted_floats(rows, "h"),
            "t_end_values": sorted_floats(rows, "t_end"),
            "reference_h_values": sorted_floats(rows, "reference_h"),
            "public_policy_h_rows": sum(1 for row in rows if bool_cell(row.get("public_policy_h"))),
            "dynamic_order_work_row": False,
            "kinematic_reaction_residual_row": True,
            "finest_max_dynamics_residual_norm": min(
                (value for row in rows if (value := as_float(row.get("max_dynamics_residual_norm"))) is not None),
                default=None,
            ),
        }

    single_velocity_orders = [
        value for row in single_rows if (value := as_float(row.get("velocity_observed_order"))) is not None
    ]
    single_finest_velocity_errors = [
        value for row in single_rows if (value := as_float(row.get("velocity_l2_error"))) is not None
    ]
    double_velocity_orders = [
        value for row in double_rows if (value := as_float(row.get("vel_observed_order"))) is not None
    ]
    double_finest_velocity_errors = [
        value for row in double_rows if (value := as_float(row.get("vel_final_linf"))) is not None
    ]

    return {
        "suite_id": "ra2021_absolute_coordinate",
        "status": "local_candidate_rows_present_but_not_source_policy_closed",
        "public_baseline_order_groups": f"{sum(1 for row in public_summary if row.get('ok_row_count') == row.get('row_count'))}/9",
        "public_baseline_timing_rows": f"{ok_count(public_timing)}/12",
        "single_pendulum_public_policy_candidate": {
            "row_count": len(single_rows),
            "ok_row_count": ok_count(single_rows),
            "h_values": sorted_floats(single_rows, "h"),
            "t_end_values": sorted_floats(single_rows, "t_end"),
            "reference_h_values": sorted_floats(single_rows, "reference_h"),
            "public_policy_h_rows": sum(1 for row in single_rows if bool_cell(row.get("public_policy_h"))),
            "public_policy_time_window_rows": sum(
                1 for row in single_rows if bool_cell(row.get("public_policy_time_window"))
            ),
            "velocity_order": single_velocity_orders[0] if single_velocity_orders else None,
            "finest_velocity_error": min(single_finest_velocity_errors) if single_finest_velocity_errors else None,
            "source_policy_candidate_grid_present": True,
            "accepted_source_policy_dynamic_order": False,
            "blocking_reason": "near-roundoff/floor-limited public-policy tranche; not enough to close all four RA2021 source-policy examples",
        },
        "double_pendulum_public_horizon_candidate": {
            "row_count": len(double_rows),
            "ok_row_count": ok_count(double_rows),
            "h_values": sorted_floats(double_rows, "h"),
            "t_end_values": sorted_floats(double_rows, "t_end"),
            "reference_h_values": sorted_floats(double_rows, "reference_h"),
            "public_policy_h_rows": sum(1 for row in double_rows if bool_cell(row.get("public_policy_h"))),
            "public_policy_time_window_rows": sum(
                1 for row in double_rows if bool_cell(row.get("public_policy_time_window"))
            ),
            "velocity_order": double_velocity_orders[0] if double_velocity_orders else None,
            "finest_velocity_error": min(double_finest_velocity_errors) if double_finest_velocity_errors else None,
            "source_policy_candidate_grid_present": False,
            "accepted_source_policy_dynamic_order": False,
            "blocking_reason": "public horizon is present, but h/reference policy is coarse and local-self-reference, not the public source-policy grid",
        },
        "closed_loop_public_horizon_candidates": closed_model_summary,
        "closed_loop_true_dynamic_coarse_candidates": {
            "status": true_dynamic.get("status"),
            "models": true_dynamic.get("models"),
            "row_count": true_dynamic.get("row_count"),
            "ok_row_count": true_dynamic.get("ok_row_count"),
            "accepted_dynamic_order_count": true_dynamic.get("accepted_dynamic_order_count"),
            "step_sizes": true_dynamic.get("step_sizes"),
            "t_end": true_dynamic.get("t_end"),
            "stage_oracle_used": true_dynamic.get("stage_oracle_used"),
            "default_policy": true_dynamic.get("default_policy"),
            "strict_public_policy_1e-4_required": true_dynamic.get("strict_public_policy_1e-4_required"),
            "default_1e-4_required": true_dynamic.get("default_1e-4_required"),
            "external_superiority_claim": true_dynamic.get("external_superiority_claim"),
            "model_summaries": true_dynamic.get("model_summaries"),
            "interpretation": (
                "coarse true-dynamic local order evidence for four_link and slider_crank; "
                "not a source-paper default-policy reproduction"
            ),
        },
        "closed_loop_true_dynamic_public_work_precision": {
            "status": public_work.get("status"),
            "row_count": public_work.get("row_count"),
            "ok_row_count": public_work.get("ok_row_count"),
            "public_work_precision_available_count": public_work.get(
                "public_work_precision_available_count"
            ),
            "public_work_precision_missing_count": public_work.get(
                "public_work_precision_missing_count"
            ),
            "strict_common_reference_error_columns": public_work.get(
                "strict_common_reference_error_columns"
            ),
            "reference_alignment_status": public_work.get("reference_alignment_status"),
            "default_policy": public_work.get("default_policy"),
            "strict_public_policy_1e-4_required": public_work.get(
                "strict_public_policy_1e-4_required"
            ),
            "default_1e-4_required": public_work.get("default_1e-4_required"),
            "external_superiority_claim": public_work.get("external_superiority_claim"),
            "interpretation": (
                "same-window public work/precision rows exist, but the reference-family caveat "
                "keeps this out of strict external-superiority scope"
            ),
        },
        "coarse_first_external_readiness": {
            "coarse_same_window_ready_count": readiness_gate.get(
                "coarse_same_window_ready_count"
            ),
            "local_true_dynamic_order_available_count": readiness_gate.get(
                "local_true_dynamic_order_available_count"
            ),
            "public_work_precision_available_count": readiness_gate.get(
                "public_work_precision_available_count"
            ),
            "strict_common_reference_available_count": readiness_gate.get(
                "strict_common_reference_available_count"
            ),
            "strict_common_reference_gap_count": readiness_gate.get(
                "strict_common_reference_gap_count"
            ),
            "dynamic_order_missing_count": readiness_gate.get("dynamic_order_missing_count"),
            "strict_common_reference_figure_available": readiness_gate.get(
                "strict_common_reference_figure_available"
            ),
            "same_test_campaign_status": readiness_gate.get("same_test_campaign_status"),
            "default_policy": readiness_gate.get("default_policy"),
            "submission_ready": readiness_gate.get("submission_ready"),
            "external_superiority_claim": readiness_gate.get("external_superiority_claim"),
        },
        "accepted_source_policy_dynamic_order_examples": 0,
        "source_policy_closed_rows": 0,
        "external_superiority_ready": False,
    }


def summarize_hi2022() -> dict[str, Any]:
    bounded_rows = read_csv(V048_RESULTS / "hi2022_halfimplicit_rows.csv")
    t8_rows: list[dict[str, str]] = []
    for path in sorted((V048_RESULTS / "hi2022_T8_coarse_model_shards").glob("hi2022_*_rows.csv")):
        t8_rows.extend(read_csv(path))
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in t8_rows:
        groups[f"{row.get('form')}:{row.get('model')}"].append(row)
    complete_groups = [
        key
        for key, rows in groups.items()
        if len(rows) == 3 and ok_count(rows) == 3
    ]
    failed_groups = [
        key
        for key, rows in groups.items()
        if ok_count(rows) != len(rows)
    ]
    return {
        "suite_id": "hi2022_half_implicit",
        "status": "bounded_and_T8_coarse_evidence_present_but_full_source_policy_open",
        "bounded_T0p1_rows": f"{ok_count(bounded_rows)}/{len(bounded_rows)}",
        "bounded_T0p1_h_values": sorted_floats(bounded_rows, "h"),
        "bounded_T0p1_reference_h_values": sorted_floats(bounded_rows, "reference_h"),
        "t8_coarse_rows": f"{ok_count(t8_rows)}/{len(t8_rows)}",
        "t8_coarse_h_values": sorted_floats(t8_rows, "h"),
        "t8_coarse_reference_h_values": sorted_floats(t8_rows, "reference_h"),
        "t8_complete_groups": sorted(complete_groups),
        "t8_failed_or_partial_groups": sorted(failed_groups),
        "t8_complete_group_count": len(complete_groups),
        "t8_group_count": len(groups),
        "full_T8_source_policy_completed": False,
        "accepted_source_policy_dynamic_order_examples": 0,
        "source_policy_closed_rows": 0,
        "external_superiority_ready": False,
        "blocking_reason": "T=8 coarse rows are useful stability/failure evidence, but only 4/8 form-model groups are complete and the source-policy h/reference contract is not met",
    }


def summarize_tfe2026() -> dict[str, Any]:
    model = read_json(PAPER / "TFE_SOURCE_PENDULUM_MODEL_AUDIT.json")
    grid = read_json(PAPER / "TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.json")
    endpoint = read_json(PAPER / "TFE_ENDPOINT_POLICY_SENSITIVITY_AUDIT.json")
    return {
        "suite_id": "tfe2026_original_pendulum",
        "status": "nonpublic_code_attempted_not_reproducible_not_promoted",
        "public_code_available": False,
        "self_reproduction_attempted": True,
        "self_reproduction_attempt_status": "attempted_not_reproducible_not_promoted",
        "self_reproduction_attempt_audit": "SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json",
        "source_parameter_model_implemented": model.get("source_pendulum_parameter_model_implemented"),
        "bounded_source_policy_runner_rows": model.get("bounded_source_policy_runner_rows"),
        "bounded_source_policy_runner_full_T10": model.get("bounded_source_policy_runner_full_T10"),
        "source_comparator_candidate_runners_implemented": model.get(
            "source_comparator_candidate_runners_implemented"
        ),
        "tfe_m1_m2_m3_candidate_runner_smoke_implemented": model.get(
            "tfe_m1_m2_m3_candidate_runner_smoke_implemented"
        ),
        "pendulum_dae_runner_implemented": model.get("pendulum_dae_runner_implemented"),
        "brown_mcphee_friction_law_implemented": model.get("brown_mcphee_friction_law_implemented"),
        "source_policy_method_runner_equivalent": model.get("source_policy_method_runner_equivalent"),
        "source_policy_rows_completed": model.get("source_policy_rows_completed"),
        "integer_step_compatible_rows": grid.get("integer_step_compatible_rows"),
        "integer_step_incompatible_rows": grid.get("integer_step_incompatible_rows"),
        "exact_T_compatible_endpoint_grid_rows_resolved": grid.get(
            "endpoint_compatible_rows_source_endpoint_convention_resolved"
        ),
        "endpoint_incompatible_rows_requiring_source_policy": grid.get(
            "endpoint_incompatible_rows_require_source_endpoint_policy"
        ),
        "source_grid_policy_resolved_for_exact_T_compatible_rows": grid.get(
            "source_grid_policy_resolved_for_exact_T_compatible_rows"
        ),
        "source_grid_policy_resolved_for_full_T10": grid.get("source_grid_policy_resolved_for_full_T10"),
        "endpoint_sensitivity_raw_rows": endpoint.get("raw_row_count"),
        "endpoint_sensitivity_source_policy_rows_completed": endpoint.get("source_policy_rows_completed"),
        "accepted_source_policy_dynamic_order_examples": 0,
        "source_policy_closed_rows": 0,
        "external_superiority_ready": False,
        "blocking_reason": "no distinct public TFE code artifact was found; paper-spec/proxy self-reproduction is not source-policy equivalent, so these rows stay attempted-not-reproducible and not promoted",
    }


def summarize_active_row_requirements(ledger: dict[str, Any], active_suites: list[str]) -> dict[str, Any]:
    active_suite_set = set(active_suites)
    rows = []
    by_suite: dict[str, int] = defaultdict(int)
    for row in ledger.get("rows", []):
        if not isinstance(row, dict) or row.get("suite") not in active_suite_set:
            continue
        by_suite[str(row.get("suite"))] += 1
        queue = row.get("queue", {}) if isinstance(row.get("queue"), dict) else {}
        rows.append(
            {
                "suite": row.get("suite"),
                "example": row.get("example"),
                "method": row.get("method"),
                "action_class": row.get("action_class"),
                "priority": row.get("priority"),
                "resolved_evidence_count": row.get("resolved_evidence_count"),
                "missing_evidence_count": row.get("missing_evidence_count"),
                "source_policy_closed": row.get("source_policy_closed"),
                "can_support_external_superiority": row.get("can_support_external_superiority"),
                "required_closure_action": row.get("required_closure_action"),
                "queue_status": queue.get("queue_status"),
                "can_parallelize": queue.get("can_parallelize"),
                "parallel_shard_count": queue.get("parallel_shard_count"),
                "source_policy_1e_4_required": queue.get("source_policy_1e_4_required"),
                "missing_evidence": row.get("missing_evidence", []),
                "resolved_evidence": row.get("resolved_evidence", []),
            }
        )
    return {
        "row_count": len(rows),
        "by_suite_counts": dict(sorted(by_suite.items())),
        "rows": rows,
        "all_rows_source_policy_closed": all(bool(row.get("source_policy_closed")) for row in rows),
        "external_superiority_ready_rows": sum(1 for row in rows if row.get("can_support_external_superiority")),
        "source_policy_1e_4_required_values": sorted(
            {str(row.get("source_policy_1e_4_required")) for row in rows}
        ),
    }


def main() -> None:
    dashboard = read_json(PAPER / "FOUR_EXAMPLE_SOURCE_POLICY_DASHBOARD.json")
    comparison = read_json(PAPER / "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.json")
    b2 = read_json(PAPER / "B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.json")
    ledger = read_json(PAPER / "SOURCE_POLICY_ROW_CLOSURE_LEDGER.json")

    ra = summarize_ra2021()
    hi = summarize_hi2022()
    tfe = summarize_tfe2026()
    suites = [ra, hi, tfe]
    active_row_requirements = summarize_active_row_requirements(
        ledger,
        list(b2.get("remaining_active_suites", [])),
    )

    result = {
        "schema": "source-policy-local-candidate-gap-audit-v1",
        "status": "local_candidate_gap_open_source_policy_not_closed",
        "submission_ready": False,
        "source_policy_superiority_claim_allowed": False,
        "external_superiority_claim_allowed": False,
        "common_reference_claim_allowed": comparison.get("common_reference_claim_allowed"),
        "source_policy_dynamic_order_examples": dashboard.get(
            "accepted_source_policy_dynamic_order_examples"
        ),
        "local_dynamic_order_examples": dashboard.get("local_dynamic_order_closed_examples"),
        "local_dynamic_order_example_names": dashboard.get(
            "local_dynamic_order_closed_example_names", []
        ),
        "active_source_policy_suites": len(b2.get("remaining_active_suites", [])),
        "active_b2_flagged_rows": b2.get("active_flagged_row_count"),
        "demoted_flagged_rows": b2.get("demoted_flagged_row_count"),
        "row_ledger_flagged_rows": ledger.get("coverage", {}).get("flagged_row_count"),
        "row_ledger_source_policy_closed_rows": ledger.get("coverage", {}).get("rows_source_policy_closed"),
        "accepted_source_policy_dynamic_order_examples": 0,
        "source_policy_closed_rows": 0,
        "source_policy_total_rows": 40,
        "execution_policy": {
            "read_only_existing_artifacts": True,
            "heavy_numerical_run_invoked": False,
            "default_1e_4_required": False,
            "run_v047_invoked": False,
            "v048_runner_invoked": False,
        },
        "active_row_requirements": active_row_requirements,
        "suite_summaries": suites,
        "closure_gaps": [
            {
                "suite_id": "ra2021_absolute_coordinate",
                "gap": "single pendulum has source-grid candidate rows, but double-pendulum and closed-loop examples are not accepted source-policy dynamic-order/work rows",
                "next_action": "run or demote the remaining RA2021 local same-policy dynamic rows after resolving velocity/output mapping and floor policy",
            },
            {
                "suite_id": "hi2022_half_implicit",
                "gap": "demoted after bounded T=0.1 evidence plus incomplete T=8 coarse/tolerance-repair source-policy evidence",
                "next_action": "keep HI2022 in bounded diagnostic/related-work scope only unless a new source-policy campaign is explicitly requested",
            },
            {
                "suite_id": "tfe2026_original_pendulum",
                "gap": "public TFE source code is absent and the available paper-spec/proxy reconstruction is not source-policy equivalent",
                "next_action": "keep TFE rows attempted-not-reproducible/not-promoted unless a new source-code-equivalent public or author artifact appears",
            },
        ],
        "source_files": {
            "gauss6_public_single": "../../numerics/v048_cross_paper_same_test_benchmarks/results/gauss6_fullva_public_horizon_single_rows.csv",
            "gauss6_public_double_coarse": "../../numerics/v048_cross_paper_same_test_benchmarks/results/gauss6_fullva_public_horizon_double_coarse_rows.csv",
            "gauss6_public_closed_loop": "../../numerics/v048_cross_paper_same_test_benchmarks/results/gauss6_fullva_public_horizon_closed_loop_rows.csv",
            "hi2022_bounded": "../../numerics/v048_cross_paper_same_test_benchmarks/results/hi2022_halfimplicit_rows.csv",
            "hi2022_t8_coarse": "../../numerics/v048_cross_paper_same_test_benchmarks/results/hi2022_T8_coarse_model_shards",
            "tfe_model_audit": "TFE_SOURCE_PENDULUM_MODEL_AUDIT.json",
            "tfe_grid_audit": "TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.json",
            "tfe_endpoint_sensitivity": "TFE_ENDPOINT_POLICY_SENSITIVITY_AUDIT.json",
            "tfe_self_reproduction_attempt": "SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json",
            "comparison_reconciliation": "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.json",
        },
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# Source-Policy Local Candidate Gap Audit",
        "",
        "Status: **local candidate gap open; source-policy not closed**.",
        "",
        f"- Active source-policy suites: `{result['active_source_policy_suites']}`.",
        f"- Active B2 flagged rows: `{result['active_b2_flagged_rows']}`.",
        f"- Demoted flagged rows: `{result['demoted_flagged_rows']}`.",
        f"- Source-policy closed rows: `{result['source_policy_closed_rows']}/{result['source_policy_total_rows']}`.",
        f"- Common-reference claim allowed: `{result['common_reference_claim_allowed']}`.",
        f"- Local dynamic-order examples: `{result['local_dynamic_order_examples']}/4`.",
        f"- Accepted source-policy dynamic-order examples: `{result['accepted_source_policy_dynamic_order_examples']}`.",
        f"- Source-policy dynamic-order examples: `{result['source_policy_dynamic_order_examples']}/4`.",
        f"- Active row requirements: `{active_row_requirements['row_count']}` rows; external-superiority-ready `{active_row_requirements['external_superiority_ready_rows']}`.",
        f"- External superiority claim allowed: `{result['external_superiority_claim_allowed']}`.",
        f"- Heavy/default `1e-4`/run_v047 invoked: `{result['execution_policy']['heavy_numerical_run_invoked']}/{result['execution_policy']['default_1e_4_required']}/{result['execution_policy']['run_v047_invoked']}`.",
        "",
        "## Local Candidate And Demotion Evidence",
        "",
        "| suite | current local evidence | accepted source-policy rows | blocking gap |",
        "|---|---|---:|---|",
        (
            f"| `ra2021_absolute_coordinate` | single public-grid `{ra['single_pendulum_public_policy_candidate']['ok_row_count']}/"
            f"{ra['single_pendulum_public_policy_candidate']['row_count']}`, double coarse `{ra['double_pendulum_public_horizon_candidate']['ok_row_count']}/"
            f"{ra['double_pendulum_public_horizon_candidate']['row_count']}`, closed-loop public-grid rows present; "
            f"closed-loop true-dynamic coarse candidates `{ra['closed_loop_true_dynamic_coarse_candidates']['accepted_dynamic_order_count']}/"
            f"{len(ra['closed_loop_true_dynamic_coarse_candidates']['models'])}` | 0 | "
            f"{ra['single_pendulum_public_policy_candidate']['blocking_reason']} |"
        ),
        (
            f"| `hi2022_half_implicit` | demoted; bounded T=0.1 `{hi['bounded_T0p1_rows']}`, T=8 coarse `{hi['t8_coarse_rows']}`, complete T=8 groups `{hi['t8_complete_group_count']}/{hi['t8_group_count']}` | 0 | "
            f"{hi['blocking_reason']} |"
        ),
        (
            f"| `tfe2026_original_pendulum` | bounded runner rows `{tfe['bounded_source_policy_runner_rows']}`, endpoint sensitivity rows `{tfe['endpoint_sensitivity_raw_rows']}` | 0 | "
            f"{tfe['blocking_reason']} |"
        ),
        "",
        "## Active Row Requirements",
        "",
        "| suite | example | method | action | resolved/missing | queue | 1e-4 policy |",
        "|---|---|---|---|---:|---|---|",
    ]
    for row in active_row_requirements["rows"]:
        lines.append(
            f"| `{row['suite']}` | `{row['example']}` | `{row['method']}` | `{row['action_class']}` | "
            f"{row['resolved_evidence_count']}/{row['missing_evidence_count']} | `{row['queue_status']}` | `{row['source_policy_1e_4_required']}` |"
        )
    lines.extend(
        [
            "",
            "## RA2021 Coarse True-Dynamic Evidence",
            "",
            (
                f"- Closed-loop true-dynamic coarse candidates: "
                f"`{ra['closed_loop_true_dynamic_coarse_candidates']['accepted_dynamic_order_count']}/"
                f"{len(ra['closed_loop_true_dynamic_coarse_candidates']['models'])}` "
                f"models, rows `{ra['closed_loop_true_dynamic_coarse_candidates']['ok_row_count']}/"
                f"{ra['closed_loop_true_dynamic_coarse_candidates']['row_count']}`."
            ),
            (
                f"- Step sizes/time window: "
                f"`{'|'.join(str(value) for value in ra['closed_loop_true_dynamic_coarse_candidates']['step_sizes'])}`/"
                f"`{ra['closed_loop_true_dynamic_coarse_candidates']['t_end']}`."
            ),
            (
                f"- Public work/precision rows: "
                f"`{ra['closed_loop_true_dynamic_public_work_precision']['ok_row_count']}/"
                f"{ra['closed_loop_true_dynamic_public_work_precision']['row_count']}`; "
                f"available examples `{ra['closed_loop_true_dynamic_public_work_precision']['public_work_precision_available_count']}`."
            ),
            (
                f"- Coarse-first gate: ready examples "
                f"`{ra['coarse_first_external_readiness']['coarse_same_window_ready_count']}/4`, "
                f"strict common-reference gap "
                f"`{ra['coarse_first_external_readiness']['strict_common_reference_gap_count']}`, "
                f"same-test campaign `{ra['coarse_first_external_readiness']['same_test_campaign_status']}`."
            ),
            "",
            "| model | pos order | orient order | vel order | omega order | accepted coarse candidate |",
            "|---|---:|---:|---:|---:|---|",
        ]
    )
    for model, model_summary in sorted(
        ra["closed_loop_true_dynamic_coarse_candidates"]["model_summaries"].items()
    ):
        lines.append(
            f"| `{model}` | `{model_summary['pos_observed_order']:.3f}` | "
            f"`{model_summary['orientation_observed_order']:.3f}` | "
            f"`{model_summary['vel_observed_order']:.3f}` | "
            f"`{model_summary['omega_observed_order']:.3f}` | "
            f"`{model_summary['accepted_dynamic_order_candidate']}` |"
        )
    lines.extend(
        [
        "",
        "## Closure Gaps",
        "",
        "| suite | gap | next action |",
        "|---|---|---|",
        ]
    )
    for gap in result["closure_gaps"]:
        lines.append(f"| `{gap['suite_id']}` | {gap['gap']} | {gap['next_action']} |")
    lines.extend(
        [
            "",
            "Reading rule: this artifact explains why existing local candidate rows do not yet close source-policy external superiority. It is not a new numerical campaign and does not promote any row to a source-policy claim.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("source_policy_local_candidate_gap_audit=written")
    print("source_policy_closed=0/40")
    print("accepted_source_policy_dynamic_order_examples=0")
    print("external_superiority_claim_allowed=False")


if __name__ == "__main__":
    main()
