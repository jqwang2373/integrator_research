#!/usr/bin/env python3
"""Audit original-TFE active source-policy rows against extracted source spec."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent

TFE_RESOLVED_SOURCE_POLICY_EVIDENCE = [
    "source pendulum body/setup parameters encoded",
    "source coordinate/velocity output and error norm policy encoded",
    "full T=10 h_ref=1e-4 source-reference feasibility probe completed without row promotion",
]

TFE_OPEN_SOURCE_POLICY_RISKS = [
    "source_policy_DAE_runner_equivalence_open",
    "brown_mcphee_source_code_equivalent_law_open",
    "full_T10_endpoint_policy_open",
    "accepted_source_policy_work_rows_not_bound",
]


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def method_to_spec_method(method: str | None) -> str:
    mapping = {
        "tfe2026_Newmark_beta": "Newmark_beta",
        "tfe2026_TFE_m1": "TFE_m1",
        "tfe2026_TFE_m2": "TFE_m2",
        "tfe2026_trapezoidal": "trapezoidal",
    }
    if method not in mapping:
        raise ValueError(f"unexpected TFE method label: {method!r}")
    return mapping[method]


def runner_equivalence_gap_matrix(
    preflight: dict[str, Any],
    grid_audit: dict[str, Any],
) -> dict[str, Any]:
    """Turn the TFE runner-equivalence preflight into a row-level gap matrix."""

    open_detail = {
        "brown_mcphee_source_code_equivalent_law_open": {
            "first_required_artifact": "Brown--McPhee source-code-equivalent friction-law certificate",
            "blocking_scope": "frictional original-TFE source-policy rows and any source-code-equivalent frictional comparison",
            "blocking_source_fields": [
                "brown_mcphee_published_formula_structure_encoded=True",
                "brown_mcphee_source_code_equivalent_law=False",
                "brown_mcphee_transition_velocity_policy_resolved_from_source=False",
            ],
            "can_resolve_without_heavy_run": True,
        },
        "pendulum_absolute_coordinate_source_policy_dae_runner_missing": {
            "first_required_artifact": "absolute-coordinate T=10 source-policy DAE runner equivalence certificate",
            "blocking_scope": "all original-TFE source-policy rows because candidate smokes are not full DAE source-policy executions",
            "blocking_source_fields": [
                "absolute_coordinate_dae_residual_smoke_implemented=True",
                "absolute_coordinate_planar_lift_trajectory_probe_implemented=True",
                "bounded_absolute_coordinate_dae_trajectory_runner_implemented=True",
                "pendulum_dae_runner_implemented=False",
                "source_policy_dae_runner_equivalent=False",
            ],
            "can_resolve_without_heavy_run": False,
        },
        "tfe_newmark_trapezoidal_source_policy_method_runners_missing": {
            "first_required_artifact": "TFE m=1/m=2/m=3, Newmark-beta, and trapezoidal source-policy method-runner certificate",
            "blocking_scope": "method-side source-policy reproduction rows for the original TFE pendulum suite",
            "blocking_source_fields": [
                "newmark_beta_candidate_runner_smoke_implemented=True",
                "trapezoidal_candidate_runner_smoke_implemented=True",
                "tfe_m1_m2_m3_candidate_runner_smoke_implemented=True",
                "tfe_m1_m2_m3_source_policy_runners_implemented=False",
            ],
            "can_resolve_without_heavy_run": False,
        },
        "gauss6_fullva_absolute_coordinate_source_policy_runner_missing": {
            "first_required_artifact": "Gauss6/FullVA absolute-coordinate source-pendulum DAE runner certificate",
            "blocking_scope": "local method source-policy comparator rows under the original TFE pendulum policy",
            "blocking_source_fields": [
                "gauss6_fullva_source_pendulum_candidate_smoke_implemented=True",
                "gauss6_fullva_source_pendulum_candidate_method_equivalent=False",
                "gauss6_fullva_absolute_coordinate_source_policy_runner_implemented=False",
            ],
            "can_resolve_without_heavy_run": False,
        },
        "full_T10_source_grid_endpoint_policy_open": {
            "first_required_artifact": "full T=10 endpoint/output sampling policy for endpoint-incompatible h rows",
            "blocking_scope": "four non-exact-T h rows that cannot be promoted to source-policy work/precision evidence",
            "blocking_source_fields": [
                "source_grid_policy_resolved_for_exact_T_compatible_rows=True",
                "source_grid_policy_resolved_for_full_T10=False",
                f"endpoint_incompatible_rows={grid_audit.get('integer_step_incompatible_rows')}",
            ],
            "endpoint_incompatible_rows": grid_audit.get("integer_step_incompatible_rows"),
            "can_resolve_without_heavy_run": True,
        },
        "accepted_source_policy_work_precision_rows_not_executed_or_bound": {
            "first_required_artifact": "accepted source-policy work/precision row table binding error, order, runtime, and work metrics",
            "blocking_scope": "B4/B7 clean source-policy work/precision figures and external-superiority readiness",
            "blocking_source_fields": [
                "source_policy_rows_closed_by_preflight=0",
                "candidate_work_precision_rows=18",
                "b4_b7_can_close_from_preflight=False",
            ],
            "can_resolve_without_heavy_run": False,
        },
    }
    open_rows = []
    for item in preflight.get("open_blockers", []):
        detail = open_detail.get(item.get("id"), {})
        open_rows.append(
            {
                "id": item.get("id"),
                "status": item.get("status"),
                "reason": item.get("reason"),
                **detail,
            }
        )
    return {
        "schema": "tfe-source-policy-runner-equivalence-gap-matrix-v1",
        "status": preflight.get("status"),
        "closed_precondition_count": preflight.get("closed_precondition_count"),
        "open_blocker_count": preflight.get("open_blocker_count"),
        "source_policy_rows_closed_by_preflight": preflight.get("source_policy_rows_closed_by_preflight"),
        "can_close_tfe_lane_from_preflight": preflight.get("can_close_tfe_lane_from_preflight"),
        "b4_b7_can_close_from_preflight": preflight.get("b4_b7_can_close_from_preflight"),
        "heavy_numerical_run_invoked": preflight.get("heavy_numerical_run_invoked"),
        "run_v047_invoked": preflight.get("run_v047_invoked"),
        "v048_runner_invoked": preflight.get("v048_runner_invoked"),
        "ready_to_execute_source_policy_now": False,
        "first_required_artifact": "source-equivalent DAE runner certificate for the original TFE pendulum policy",
        "post_artifact_requirement": "run TFE m=1/m=2/Newmark/trapezoidal rows and local Gauss6 rows under one T=10 source reference policy",
        "closed_preconditions": preflight.get("closed_preconditions", []),
        "open_blockers": open_rows,
    }


def main() -> None:
    b2_manifest = read_json(PAPER / "B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.json")
    tfe_spec = read_json(PAPER / "TFE_SOURCE_POLICY_SPEC.json")
    model_audit = read_json(PAPER / "TFE_SOURCE_PENDULUM_MODEL_AUDIT.json")
    row_ledger = read_json(PAPER / "SOURCE_POLICY_ROW_CLOSURE_LEDGER.json")
    all_examples = read_json(PAPER / "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.json")
    closure_manifest = read_json(PAPER / "EXTERNAL_SOURCE_POLICY_CLOSURE_MANIFEST.json")
    external_case = read_json(PAPER / "EXTERNAL_CASE_EVIDENCE_RECONCILIATION.json")
    grid_audit = read_json(PAPER / "TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.json")
    algorithm_literal_endpoint_probe = read_json(PAPER / "TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE.json")

    active_rows = [
        row
        for row in b2_manifest.get("rows", [])
        if row.get("suite_id") == "tfe2026_original_pendulum" and row.get("active_b2_requirement") is True
    ]
    tfe_demoted = "original_tfe_pendulum_error_order_work_rows" in b2_manifest.get(
        "b2_closed_by_demotion", []
    )
    ledger_rows = [
        row
        for row in row_ledger.get("rows", [])
        if row.get("suite") == "tfe2026_original_pendulum"
    ]
    ledger_by_method = {row.get("method"): row for row in ledger_rows}
    policy = tfe_spec.get("source_policy", {})
    runner_gap = tfe_spec.get("runner_gap", {})
    source_spec_boundary = tfe_spec.get("candidate_vs_source_policy_boundary", {})
    execution = tfe_spec.get("execution_policy", {})
    methods = {row.get("method"): row for row in policy.get("methods", [])}
    cases = {row.get("case_id"): row for row in policy.get("cases", [])}
    active_b2_candidate_smoke = model_audit.get("active_tfe_b2_candidate_row_smoke", {})
    bounded_runner_smoke = model_audit.get("bounded_source_policy_runner_smoke", {})
    full_t10_coarse_probe = model_audit.get("active_tfe_b2_full_T10_coarse_candidate_probe", {})
    source_reference_full_t10_candidate_probe = model_audit.get(
        "active_tfe_b2_source_reference_full_T10_candidate_probe",
        {},
    )
    tfe_m3_full_t10_formula_probe = model_audit.get("tfe_m3_full_T10_coarse_formula_probe", {})
    gauss6_candidate_smoke = model_audit.get("gauss6_fullva_source_pendulum_candidate_smoke", {})
    gauss6_dae_candidate_contract = model_audit.get(
        "gauss6_fullva_dae_candidate_contract_smoke",
        {},
    )
    runner_equivalence_preflight = model_audit.get("source_policy_runner_equivalence_preflight", {})
    runner_gap_matrix = runner_equivalence_gap_matrix(runner_equivalence_preflight, grid_audit)
    active_b2_candidate_by_method = {
        row.get("paper_method"): row for row in active_b2_candidate_smoke.get("rows", [])
    }
    bounded_runner_by_method = {
        row.get("paper_method"): row for row in bounded_runner_smoke.get("rows", [])
    }
    full_t10_coarse_by_method = {
        row.get("paper_method"): row for row in full_t10_coarse_probe.get("rows", [])
    }

    audited_rows: list[dict[str, Any]] = []
    for item in active_rows:
        method = item.get("method")
        spec_method = method_to_spec_method(method)
        ledger = ledger_by_method.get(method, {})
        current = ledger.get("current_evidence", {})
        active_candidate = active_b2_candidate_by_method.get(method, {})
        bounded_candidate = bounded_runner_by_method.get(method, {})
        full_t10_candidate = full_t10_coarse_by_method.get(method, {})
        active_metrics = active_candidate.get("metrics", [])
        active_finest = active_metrics[-1] if active_metrics else {}
        full_t10_metrics = full_t10_candidate.get("metrics", [])
        full_t10_finest = full_t10_metrics[-1] if full_t10_metrics else {}
        audited_rows.append(
            {
                "row_index": item.get("row_index"),
                "example": item.get("example"),
                "method": method,
                "source_method": spec_method,
                "expected_order": methods.get(spec_method, {}).get("expected_order"),
                "diagnostic_current_allowed_use": ledger.get("current_allowed_use"),
                "diagnostic_velocity_order": current.get("velocity_order"),
                "diagnostic_finest_position_error": current.get("finest_position_error"),
                "diagnostic_finest_velocity_error": current.get("finest_velocity_error"),
                "diagnostic_categories": current.get("diagnostic_categories", []),
                "source_policy_resolved_evidence": TFE_RESOLVED_SOURCE_POLICY_EVIDENCE,
                "source_policy_risks": TFE_OPEN_SOURCE_POLICY_RISKS,
                "active_b2_candidate_smoke_present": bool(active_candidate),
                "active_b2_candidate_allowed_use": "bounded_candidate_smoke_only_not_source_policy",
                "active_b2_candidate_velocity_orders": active_candidate.get("velocity_pairwise_orders"),
                "active_b2_candidate_coordinate_orders": active_candidate.get("coordinate_pairwise_orders"),
                "active_b2_candidate_finest_velocity_error": active_finest.get("velocity_error_v"),
                "active_b2_candidate_finest_coordinate_error": active_finest.get("coordinate_error_q"),
                "active_b2_candidate_max_residual_norm": active_candidate.get("max_newton_residual_norm"),
                "bounded_runner_candidate_present": bool(bounded_candidate),
                "bounded_runner_allowed_use": "bounded_candidate_runner_api_only_not_source_policy",
                "bounded_runner_velocity_orders": bounded_candidate.get("velocity_pairwise_orders"),
                "bounded_runner_coordinate_orders": bounded_candidate.get("coordinate_pairwise_orders"),
                "full_t10_coarse_candidate_present": bool(full_t10_candidate),
                "full_t10_coarse_allowed_use": "full_T10_coarse_candidate_probe_not_source_policy",
                "full_t10_coarse_velocity_orders": full_t10_candidate.get("velocity_pairwise_orders"),
                "full_t10_coarse_coordinate_orders": full_t10_candidate.get("coordinate_pairwise_orders"),
                "full_t10_coarse_finest_velocity_error": full_t10_finest.get("velocity_error_v"),
                "full_t10_coarse_finest_coordinate_error": full_t10_finest.get("coordinate_error_q"),
                "full_t10_coarse_max_residual_norm": full_t10_candidate.get("max_newton_residual_norm"),
                "source_policy_reproduction": False,
                "source_policy_closed": False,
                "external_superiority_ready": False,
                "remaining_required_evidence": item.get("required_evidence", []),
            }
        )

    source_policy_risk_counts = {
        risk: len(ledger_rows)
        for risk in TFE_OPEN_SOURCE_POLICY_RISKS
    }
    closure_criteria = {
        "source_pendulum_body_setup_extracted": runner_gap.get("source_policy_spec_extracted") is True,
        "source_pendulum_parameter_model_implemented": model_audit.get(
            "source_pendulum_parameter_model_implemented"
        )
        is True,
        "frictionless_planar_rhs_smoke_implemented": model_audit.get("frictionless_planar_rhs_smoke_implemented")
        is True,
        "absolute_coordinate_dae_residual_smoke_implemented": model_audit.get(
            "absolute_coordinate_dae_residual_smoke_implemented"
        )
        is True,
        "absolute_coordinate_planar_lift_trajectory_probe_implemented": (
            model_audit.get("absolute_coordinate_planar_lift_trajectory_probe_implemented") is True
            and model_audit.get("absolute_coordinate_planar_lift_trajectory_probe_source_policy_rows_completed")
            == 0
        ),
        "bounded_absolute_coordinate_dae_trajectory_runner_implemented": (
            model_audit.get("bounded_absolute_coordinate_dae_trajectory_runner_implemented") is True
            and model_audit.get("bounded_absolute_coordinate_dae_trajectory_runner_source_policy_rows_completed")
            == 0
            and model_audit.get("bounded_absolute_coordinate_dae_trajectory_runner_dae_runner_equivalent")
            is False
        ),
        "monolithic_absolute_coordinate_dae_candidate_runner_implemented": (
            model_audit.get("monolithic_absolute_coordinate_dae_candidate_runner_implemented") is True
            and model_audit.get(
                "monolithic_absolute_coordinate_dae_candidate_runner_source_policy_rows_completed"
            )
            == 0
            and model_audit.get("monolithic_absolute_coordinate_dae_candidate_runner_dae_runner_equivalent")
            is False
            and model_audit.get("monolithic_absolute_coordinate_dae_candidate_runner_monolithic_integrator")
            is False
        ),
        "source_method_candidate_runner_contract_implemented": (
            model_audit.get("source_method_candidate_runner_contract_implemented") is True
            and model_audit.get("source_method_candidate_runner_contract_rows") == 5
            and model_audit.get("source_method_candidate_runner_contract_source_policy_rows_completed")
            == 0
            and model_audit.get("source_method_candidate_runner_contract_method_equivalent") is False
            and model_audit.get("source_method_candidate_runner_contract_all_step_states_finite") is True
            and model_audit.get(
                "source_method_candidate_runner_contract_all_candidate_residuals_below_1e_8"
            )
            is True
        ),
        "source_output_time_integration_smoke_implemented": model_audit.get(
            "source_output_time_integration_smoke_implemented"
        )
        is True,
        "source_reference_solution_policy_smoke_implemented": model_audit.get(
            "source_reference_solution_policy_smoke_implemented"
        )
        is True,
        "source_reference_solution_policy_full_T10_probe_completed": model_audit.get(
            "source_reference_solution_policy_full_T10_probe_completed"
        )
        is True,
        "newmark_trapezoidal_candidate_runner_smoke_implemented": (
            model_audit.get("newmark_beta_candidate_runner_smoke_implemented") is True
            and model_audit.get("trapezoidal_candidate_runner_smoke_implemented") is True
        ),
        "tfe_m1_m2_m3_candidate_runner_smoke_implemented": model_audit.get(
            "tfe_m1_m2_m3_candidate_runner_smoke_implemented"
        )
        is True,
        "gauss6_fullva_source_pendulum_candidate_smoke_implemented": (
            model_audit.get("gauss6_fullva_source_pendulum_candidate_smoke_implemented") is True
            and gauss6_candidate_smoke.get("source_policy_rows_completed") == 0
        ),
        "gauss6_fullva_dae_candidate_contract_implemented": (
            model_audit.get("gauss6_fullva_dae_candidate_contract_implemented") is True
            and model_audit.get("gauss6_fullva_dae_candidate_contract_rows") == 1
            and model_audit.get("gauss6_fullva_dae_candidate_contract_source_policy_rows_completed")
            == 0
            and model_audit.get("gauss6_fullva_dae_candidate_contract_dae_equivalent") is False
            and model_audit.get("gauss6_fullva_dae_candidate_contract_fullva_dae_equivalent")
            is False
            and model_audit.get("gauss6_fullva_dae_candidate_contract_all_step_states_finite")
            is True
            and model_audit.get(
                "gauss6_fullva_dae_candidate_contract_all_candidate_residuals_below_1e_8"
            )
            is True
        ),
        "active_tfe_b2_candidate_row_smoke_implemented": model_audit.get(
            "active_tfe_b2_candidate_row_smoke_implemented"
        )
        is True,
        "active_tfe_b2_source_reference_full_T10_candidate_probe_implemented": (
            model_audit.get(
                "active_tfe_b2_source_reference_full_T10_candidate_probe_implemented"
            )
            is True
            and model_audit.get(
                "active_tfe_b2_source_reference_full_T10_candidate_probe_source_policy_rows_completed"
            )
            == 0
        ),
        "bounded_source_policy_runner_api_implemented": model_audit.get(
            "bounded_source_policy_runner_api_implemented"
        )
        is True,
        "bounded_source_policy_runner_smoke_implemented": model_audit.get(
            "bounded_source_policy_runner_smoke_implemented"
        )
        is True,
        "algorithm_literal_endpoint_probe_available": algorithm_literal_endpoint_probe.get("status")
        == "algorithm_literal_full_T10_probe_available_source_policy_open",
        "source_reference_h_extracted": policy.get("solver_policy", {}).get("source_reference_h_for_exact_reproduction")
        == 1.0e-4,
        "source_horizon_step_grid_policy_resolved": grid_audit.get(
            "source_grid_policy_resolved_for_full_T10"
        )
        is True,
        "source_horizon_step_grid_policy_resolved_for_exact_T_compatible_rows": grid_audit.get(
            "source_grid_policy_resolved_for_exact_T_compatible_rows"
        )
        is True,
        "source_error_norm_and_output_policy_encoded": model_audit.get(
            "source_error_norm_and_output_policy_encoded"
        )
        is True,
        "brown_mcphee_friction_law_or_source_code_equivalent_implemented": runner_gap.get(
            "brown_mcphee_friction_law_implemented"
        )
        is True,
        "pendulum_dae_runner_implemented": runner_gap.get("pendulum_dae_runner_implemented") is True,
        "tfe_newmark_trapezoidal_runners_implemented": (
            runner_gap.get("tfe_m1_m2_m3_runner_implemented") is True
            and runner_gap.get("newmark_trapezoidal_runner_implemented") is True
        ),
        "gauss6_fullva_on_source_pendulum_implemented": runner_gap.get(
            "gauss6_fullva_on_source_pendulum_implemented"
        )
        is True,
        "gauss6_fullva_absolute_coordinate_source_policy_runner_implemented": runner_gap.get(
            "gauss6_fullva_absolute_coordinate_source_policy_dae_runner_implemented"
        )
        is True,
        "source_policy_rows_completed": runner_gap.get("source_policy_rows_completed") == len(ledger_rows),
        "explicit_demotion_recorded_for_tfe": tfe_demoted,
        "rerun_or_independent_verification_artifact_present": False,
    }

    output = {
        "schema": "tfe-source-policy-row-audit-v1",
        "status": "source_policy_spec_extracted_runner_rows_not_closed",
        "submission_ready": False,
        "suite_id": "tfe2026_original_pendulum",
        "source_suite": "chaturvedi_sandu_sandu_tfe_pendulum",
        "evidence_class": "source_spec_extracted_candidate_scaffold_present_source_policy_rows_open",
        "source_policy_external_superiority_allowed": False,
        "external_superiority_claim_allowed": False,
        "active_b2_flagged_rows": len(active_rows),
        "audited_active_rows": len(audited_rows),
        "source_policy_closed_rows": 0,
        "external_superiority_ready_rows": 0,
        "source_policy_rows_completed": runner_gap.get("source_policy_rows_completed"),
        "source_policy_runner_equivalence_preflight_status": runner_equivalence_preflight.get("status"),
        "source_policy_runner_equivalence_preflight_closed_preconditions": runner_equivalence_preflight.get(
            "closed_precondition_count"
        ),
        "source_policy_runner_equivalence_preflight_open_blockers": runner_equivalence_preflight.get(
            "open_blocker_count"
        ),
        "source_policy_runner_equivalence_preflight_rows_closed": runner_equivalence_preflight.get(
            "source_policy_rows_closed_by_preflight"
        ),
        "source_policy_runner_equivalence_preflight_can_close_lane": runner_equivalence_preflight.get(
            "can_close_tfe_lane_from_preflight"
        ),
        "source_policy_runner_equivalence_preflight": runner_equivalence_preflight,
        "source_policy_runner_equivalence_gap_matrix": runner_gap_matrix,
        "candidate_vs_source_policy_boundary": source_spec_boundary,
        "source_policy_spec_extracted": runner_gap.get("source_policy_spec_extracted"),
        "source_pendulum_parameter_model_implemented": model_audit.get(
            "source_pendulum_parameter_model_implemented"
        ),
        "frictionless_planar_rhs_smoke_implemented": model_audit.get("frictionless_planar_rhs_smoke_implemented"),
        "absolute_coordinate_dae_residual_smoke_implemented": model_audit.get(
            "absolute_coordinate_dae_residual_smoke_implemented"
        ),
        "absolute_coordinate_frictional_candidate_dae_smoke_implemented": model_audit.get(
            "absolute_coordinate_frictional_candidate_dae_smoke_implemented"
        ),
        "absolute_coordinate_planar_lift_trajectory_probe_implemented": model_audit.get(
            "absolute_coordinate_planar_lift_trajectory_probe_implemented"
        ),
        "absolute_coordinate_planar_lift_trajectory_probe_rows": model_audit.get(
            "absolute_coordinate_planar_lift_trajectory_probe_rows"
        ),
        "absolute_coordinate_planar_lift_trajectory_probe_metric_rows": model_audit.get(
            "absolute_coordinate_planar_lift_trajectory_probe_metric_rows"
        ),
        "absolute_coordinate_planar_lift_trajectory_probe_source_policy_rows_completed": model_audit.get(
            "absolute_coordinate_planar_lift_trajectory_probe_source_policy_rows_completed"
        ),
        "absolute_coordinate_planar_lift_trajectory_probe_dae_runner_equivalent": model_audit.get(
            "absolute_coordinate_planar_lift_trajectory_probe_dae_runner_equivalent"
        ),
        "bounded_absolute_coordinate_dae_trajectory_runner_implemented": model_audit.get(
            "bounded_absolute_coordinate_dae_trajectory_runner_implemented"
        ),
        "bounded_absolute_coordinate_dae_trajectory_runner_rows": model_audit.get(
            "bounded_absolute_coordinate_dae_trajectory_runner_rows"
        ),
        "bounded_absolute_coordinate_dae_trajectory_runner_metric_rows": model_audit.get(
            "bounded_absolute_coordinate_dae_trajectory_runner_metric_rows"
        ),
        "bounded_absolute_coordinate_dae_trajectory_runner_step_residual_rows": model_audit.get(
            "bounded_absolute_coordinate_dae_trajectory_runner_step_residual_rows"
        ),
        "bounded_absolute_coordinate_dae_trajectory_runner_source_policy_rows_completed": model_audit.get(
            "bounded_absolute_coordinate_dae_trajectory_runner_source_policy_rows_completed"
        ),
        "bounded_absolute_coordinate_dae_trajectory_runner_dae_runner_equivalent": model_audit.get(
            "bounded_absolute_coordinate_dae_trajectory_runner_dae_runner_equivalent"
        ),
        "bounded_absolute_coordinate_dae_trajectory_runner_monolithic_integrator": model_audit.get(
            "bounded_absolute_coordinate_dae_trajectory_runner_monolithic_integrator"
        ),
        "monolithic_absolute_coordinate_dae_candidate_runner_implemented": model_audit.get(
            "monolithic_absolute_coordinate_dae_candidate_runner_implemented"
        ),
        "monolithic_absolute_coordinate_dae_candidate_runner_rows": model_audit.get(
            "monolithic_absolute_coordinate_dae_candidate_runner_rows"
        ),
        "monolithic_absolute_coordinate_dae_candidate_runner_metric_rows": model_audit.get(
            "monolithic_absolute_coordinate_dae_candidate_runner_metric_rows"
        ),
        "monolithic_absolute_coordinate_dae_candidate_runner_step_residual_rows": model_audit.get(
            "monolithic_absolute_coordinate_dae_candidate_runner_step_residual_rows"
        ),
        "monolithic_absolute_coordinate_dae_candidate_runner_source_policy_rows_completed": model_audit.get(
            "monolithic_absolute_coordinate_dae_candidate_runner_source_policy_rows_completed"
        ),
        "monolithic_absolute_coordinate_dae_candidate_runner_dae_runner_equivalent": model_audit.get(
            "monolithic_absolute_coordinate_dae_candidate_runner_dae_runner_equivalent"
        ),
        "monolithic_absolute_coordinate_dae_candidate_runner_monolithic_integrator": model_audit.get(
            "monolithic_absolute_coordinate_dae_candidate_runner_monolithic_integrator"
        ),
        "source_method_candidate_runner_contract_implemented": model_audit.get(
            "source_method_candidate_runner_contract_implemented"
        ),
        "source_method_candidate_runner_contract_rows": model_audit.get(
            "source_method_candidate_runner_contract_rows"
        ),
        "source_method_candidate_runner_contract_all_step_states_finite": model_audit.get(
            "source_method_candidate_runner_contract_all_step_states_finite"
        ),
        "source_method_candidate_runner_contract_all_candidate_residuals_below_1e_8": model_audit.get(
            "source_method_candidate_runner_contract_all_candidate_residuals_below_1e_8"
        ),
        "source_method_candidate_runner_contract_source_policy_rows_completed": model_audit.get(
            "source_method_candidate_runner_contract_source_policy_rows_completed"
        ),
        "source_method_candidate_runner_contract_method_equivalent": model_audit.get(
            "source_method_candidate_runner_contract_method_equivalent"
        ),
        "source_method_candidate_runner_contract_dae_equivalent": model_audit.get(
            "source_method_candidate_runner_contract_dae_equivalent"
        ),
        "source_policy_dae_runner_equivalent": model_audit.get("source_policy_dae_runner_equivalent"),
        "source_output_time_integration_smoke_implemented": model_audit.get(
            "source_output_time_integration_smoke_implemented"
        ),
        "source_policy_time_integration_runner_equivalent": model_audit.get(
            "source_policy_time_integration_runner_equivalent"
        ),
        "source_reference_solution_policy_smoke_implemented": model_audit.get(
            "source_reference_solution_policy_smoke_implemented"
        ),
        "source_reference_solution_policy_smoke_full_T10": model_audit.get(
            "source_reference_solution_policy_smoke_full_T10"
        ),
        "source_reference_solution_policy_full_T10_probe_implemented": model_audit.get(
            "source_reference_solution_policy_full_T10_probe_implemented"
        ),
        "source_reference_solution_policy_full_T10_probe_completed": model_audit.get(
            "source_reference_solution_policy_full_T10_probe_completed"
        ),
        "source_reference_solution_policy_full_T10_probe_source_h": model_audit.get(
            "source_reference_solution_policy_full_T10_probe_source_h"
        ),
        "source_reference_solution_policy_full_T10_probe_check_h": model_audit.get(
            "source_reference_solution_policy_full_T10_probe_check_h"
        ),
        "source_reference_solution_policy_full_T10_probe_steps": model_audit.get(
            "source_reference_solution_policy_full_T10_probe_steps"
        ),
        "source_reference_solution_policy_full_T10_probe_check_steps": model_audit.get(
            "source_reference_solution_policy_full_T10_probe_check_steps"
        ),
        "source_reference_solution_policy_full_T10_probe_coordinate_error": model_audit.get(
            "source_reference_solution_policy_full_T10_probe_coordinate_error"
        ),
        "source_reference_solution_policy_full_T10_probe_velocity_error": model_audit.get(
            "source_reference_solution_policy_full_T10_probe_velocity_error"
        ),
        "source_reference_solution_policy_full_T10_probe_rows_completed": model_audit.get(
            "source_reference_solution_policy_full_T10_probe_rows_completed"
        ),
        "source_comparator_candidate_runners_implemented": model_audit.get(
            "source_comparator_candidate_runners_implemented"
        ),
        "newmark_beta_candidate_runner_smoke_implemented": model_audit.get(
            "newmark_beta_candidate_runner_smoke_implemented"
        ),
        "trapezoidal_candidate_runner_smoke_implemented": model_audit.get(
            "trapezoidal_candidate_runner_smoke_implemented"
        ),
        "source_policy_method_runner_equivalent": model_audit.get("source_policy_method_runner_equivalent"),
        "tfe_m1_m2_m3_candidate_runner_smoke_implemented": model_audit.get(
            "tfe_m1_m2_m3_candidate_runner_smoke_implemented"
        ),
        "tfe_appendix_b_coefficient_certificate_checked": model_audit.get(
            "tfe_appendix_b_coefficient_certificate_checked"
        ),
        "tfe_appendix_b_coefficient_certificate_row_count": model_audit.get(
            "tfe_appendix_b_coefficient_certificate_row_count"
        ),
        "tfe_appendix_b_coefficient_certificate_max_abs_diff": model_audit.get(
            "tfe_appendix_b_coefficient_certificate_max_abs_diff"
        ),
        "tfe_m1_m2_m3_source_policy_runners_implemented": model_audit.get(
            "tfe_m1_m2_m3_source_policy_runners_implemented"
        ),
        "bounded_source_policy_runner_api_implemented": model_audit.get(
            "bounded_source_policy_runner_api_implemented"
        ),
        "bounded_source_policy_runner_smoke_implemented": model_audit.get(
            "bounded_source_policy_runner_smoke_implemented"
        ),
        "bounded_source_policy_runner_unified_dispatch": model_audit.get(
            "bounded_source_policy_runner_unified_dispatch"
        ),
        "bounded_source_policy_runner_method_count": model_audit.get(
            "bounded_source_policy_runner_method_count"
        ),
        "bounded_source_policy_runner_rows": model_audit.get("bounded_source_policy_runner_rows"),
        "bounded_source_policy_runner_full_T10": model_audit.get("bounded_source_policy_runner_full_T10"),
        "bounded_source_policy_runner_source_policy_rows_completed": model_audit.get(
            "bounded_source_policy_runner_source_policy_rows_completed"
        ),
        "bounded_source_policy_runner_method_equivalent": model_audit.get(
            "bounded_source_policy_runner_method_equivalent"
        ),
        "bounded_source_policy_runner_accepted_use": "bounded_candidate_runner_api_only_not_source_policy",
        "bounded_source_policy_runner_dae_runner_equivalent": False,
        "bounded_source_policy_runner_monolithic_integrator": False,
        "active_tfe_b2_candidate_row_smoke_implemented": model_audit.get(
            "active_tfe_b2_candidate_row_smoke_implemented"
        ),
        "active_tfe_b2_candidate_row_smoke_full_T10": model_audit.get(
            "active_tfe_b2_candidate_row_smoke_full_T10"
        ),
        "active_tfe_b2_source_policy_rows_completed": model_audit.get(
            "active_tfe_b2_source_policy_rows_completed"
        ),
        "active_tfe_b2_full_T10_coarse_candidate_probe_implemented": model_audit.get(
            "active_tfe_b2_full_T10_coarse_candidate_probe_implemented"
        ),
        "active_tfe_b2_full_T10_coarse_candidate_probe_full_T10": model_audit.get(
            "active_tfe_b2_full_T10_coarse_candidate_probe_full_T10"
        ),
        "active_tfe_b2_full_T10_coarse_candidate_probe_source_policy_rows_completed": model_audit.get(
            "active_tfe_b2_full_T10_coarse_candidate_probe_source_policy_rows_completed"
        ),
        "active_tfe_b2_full_T10_coarse_candidate_probe_source_policy_reference_not_invoked": model_audit.get(
            "active_tfe_b2_full_T10_coarse_candidate_probe_source_policy_reference_not_invoked"
        ),
        "active_tfe_b2_full_T10_coarse_candidate_probe_finite_rows": model_audit.get(
            "active_tfe_b2_full_T10_coarse_candidate_probe_finite_rows"
        ),
        "active_tfe_b2_full_T10_coarse_candidate_probe_residual_ok_rows": model_audit.get(
            "active_tfe_b2_full_T10_coarse_candidate_probe_residual_ok_rows"
        ),
        "active_tfe_b2_source_reference_full_T10_candidate_probe_implemented": model_audit.get(
            "active_tfe_b2_source_reference_full_T10_candidate_probe_implemented"
        ),
        "active_tfe_b2_source_reference_full_T10_candidate_probe_full_T10": model_audit.get(
            "active_tfe_b2_source_reference_full_T10_candidate_probe_full_T10"
        ),
        "active_tfe_b2_source_reference_full_T10_candidate_probe_source_policy_reference_invoked": model_audit.get(
            "active_tfe_b2_source_reference_full_T10_candidate_probe_source_policy_reference_invoked"
        ),
        "active_tfe_b2_source_reference_full_T10_candidate_probe_source_policy_rows_completed": model_audit.get(
            "active_tfe_b2_source_reference_full_T10_candidate_probe_source_policy_rows_completed"
        ),
        "active_tfe_b2_source_reference_full_T10_candidate_probe_finite_rows": model_audit.get(
            "active_tfe_b2_source_reference_full_T10_candidate_probe_finite_rows"
        ),
        "active_tfe_b2_source_reference_full_T10_candidate_probe_residual_ok_rows": model_audit.get(
            "active_tfe_b2_source_reference_full_T10_candidate_probe_residual_ok_rows"
        ),
        "active_tfe_b2_source_reference_full_T10_candidate_probe_method_equivalent": model_audit.get(
            "active_tfe_b2_source_reference_full_T10_candidate_probe_method_equivalent"
        ),
        "tfe_m3_full_T10_coarse_formula_probe_implemented": model_audit.get(
            "tfe_m3_full_T10_coarse_formula_probe_implemented"
        ),
        "tfe_m3_full_T10_coarse_formula_probe_full_T10": model_audit.get(
            "tfe_m3_full_T10_coarse_formula_probe_full_T10"
        ),
        "tfe_m3_full_T10_coarse_formula_probe_source_policy_rows_completed": model_audit.get(
            "tfe_m3_full_T10_coarse_formula_probe_source_policy_rows_completed"
        ),
        "tfe_m3_full_T10_coarse_formula_probe_source_policy_reference_not_invoked": model_audit.get(
            "tfe_m3_full_T10_coarse_formula_probe_source_policy_reference_not_invoked"
        ),
        "tfe_m3_full_T10_coarse_formula_probe_finite_rows": model_audit.get(
            "tfe_m3_full_T10_coarse_formula_probe_finite_rows"
        ),
        "tfe_m3_full_T10_coarse_formula_probe_residual_ok_rows": model_audit.get(
            "tfe_m3_full_T10_coarse_formula_probe_residual_ok_rows"
        ),
        "tfe_m3_full_T10_coarse_formula_probe_formal_expected_order": model_audit.get(
            "tfe_m3_full_T10_coarse_formula_probe_formal_expected_order"
        ),
        "tfe_m3_full_T10_coarse_formula_probe": {
            "runner_api": tfe_m3_full_t10_formula_probe.get("runner_api"),
            "t_final": tfe_m3_full_t10_formula_probe.get("t_final"),
            "reference_h": tfe_m3_full_t10_formula_probe.get("reference_h"),
            "comparison_h": tfe_m3_full_t10_formula_probe.get("comparison_h"),
            "row_count": len(tfe_m3_full_t10_formula_probe.get("rows", [])),
            "full_T10_formula_probe_completed": tfe_m3_full_t10_formula_probe.get(
                "full_T10_formula_probe_completed"
            ),
            "full_T10_source_policy_reproduction": tfe_m3_full_t10_formula_probe.get(
                "full_T10_source_policy_reproduction"
            ),
            "source_policy_reference_h": tfe_m3_full_t10_formula_probe.get("source_policy_reference_h"),
            "source_policy_reference_not_invoked": tfe_m3_full_t10_formula_probe.get(
                "source_policy_reference_not_invoked"
            ),
            "source_policy_rows_completed": tfe_m3_full_t10_formula_probe.get("source_policy_rows_completed"),
            "finite_row_count": tfe_m3_full_t10_formula_probe.get("finite_row_count"),
            "residual_ok_row_count": tfe_m3_full_t10_formula_probe.get("residual_ok_row_count"),
            "formal_expected_order": tfe_m3_full_t10_formula_probe.get("formal_expected_order"),
        },
        "active_tfe_b2_full_T10_coarse_candidate_probe": {
            "runner_api": full_t10_coarse_probe.get("runner_api"),
            "t_final": full_t10_coarse_probe.get("t_final"),
            "reference_h": full_t10_coarse_probe.get("reference_h"),
            "comparison_h": full_t10_coarse_probe.get("comparison_h"),
            "row_count": len(full_t10_coarse_probe.get("rows", [])),
            "full_T10_candidate_probe_completed": full_t10_coarse_probe.get(
                "full_T10_candidate_probe_completed"
            ),
            "full_T10_source_policy_reproduction": full_t10_coarse_probe.get(
                "full_T10_source_policy_reproduction"
            ),
            "source_policy_reference_h": full_t10_coarse_probe.get("source_policy_reference_h"),
            "source_policy_reference_not_invoked": full_t10_coarse_probe.get(
                "source_policy_reference_not_invoked"
            ),
            "source_policy_rows_completed": full_t10_coarse_probe.get("source_policy_rows_completed"),
            "finite_row_count": full_t10_coarse_probe.get("finite_row_count"),
            "residual_ok_row_count": full_t10_coarse_probe.get("residual_ok_row_count"),
        },
        "active_tfe_b2_source_reference_full_T10_candidate_probe": {
            "runner_api": source_reference_full_t10_candidate_probe.get("runner_api"),
            "t_final": source_reference_full_t10_candidate_probe.get("t_final"),
            "reference_h": source_reference_full_t10_candidate_probe.get("reference_h"),
            "comparison_h": source_reference_full_t10_candidate_probe.get("comparison_h"),
            "row_count": len(source_reference_full_t10_candidate_probe.get("rows", [])),
            "full_T10_candidate_probe_completed": source_reference_full_t10_candidate_probe.get(
                "full_T10_candidate_probe_completed"
            ),
            "full_T10_source_policy_reproduction": source_reference_full_t10_candidate_probe.get(
                "full_T10_source_policy_reproduction"
            ),
            "source_policy_reference_h": source_reference_full_t10_candidate_probe.get(
                "source_policy_reference_h"
            ),
            "source_policy_reference_invoked": source_reference_full_t10_candidate_probe.get(
                "source_policy_reference_invoked"
            ),
            "source_policy_rows_completed": source_reference_full_t10_candidate_probe.get(
                "source_policy_rows_completed"
            ),
            "finite_row_count": source_reference_full_t10_candidate_probe.get("finite_row_count"),
            "residual_ok_row_count": source_reference_full_t10_candidate_probe.get(
                "residual_ok_row_count"
            ),
            "source_policy_method_runner_equivalent": source_reference_full_t10_candidate_probe.get(
                "source_policy_method_runner_equivalent"
            ),
            "source_policy_dae_runner_equivalent": source_reference_full_t10_candidate_probe.get(
                "source_policy_dae_runner_equivalent"
            ),
        },
        "active_tfe_b2_candidate_row_smoke": {
            "t_final": active_b2_candidate_smoke.get("t_final"),
            "reference_h": active_b2_candidate_smoke.get("reference_h"),
            "comparison_h": active_b2_candidate_smoke.get("comparison_h"),
            "row_count": len(active_b2_candidate_smoke.get("rows", [])),
            "full_T10_source_policy_reproduction": active_b2_candidate_smoke.get(
                "full_T10_source_policy_reproduction"
            ),
            "source_policy_rows_completed": active_b2_candidate_smoke.get("source_policy_rows_completed"),
            "source_policy_method_runner_equivalent": active_b2_candidate_smoke.get(
                "source_policy_method_runner_equivalent"
            ),
        },
        "bounded_source_policy_runner_smoke": {
            "runner_api": bounded_runner_smoke.get("runner_api"),
            "t_final": bounded_runner_smoke.get("t_final"),
            "reference_h": bounded_runner_smoke.get("reference_h"),
            "comparison_h": bounded_runner_smoke.get("comparison_h"),
            "row_count": bounded_runner_smoke.get("row_count"),
            "method_count": bounded_runner_smoke.get("method_count"),
            "unified_method_dispatch": bounded_runner_smoke.get("unified_method_dispatch"),
            "full_T10_source_policy_reproduction": bounded_runner_smoke.get(
                "full_T10_source_policy_reproduction"
            ),
            "source_policy_rows_completed": bounded_runner_smoke.get("source_policy_rows_completed"),
            "source_policy_method_runner_equivalent": bounded_runner_smoke.get(
                "source_policy_method_runner_equivalent"
            ),
            "accepted_use": "bounded_candidate_runner_api_only_not_source_policy",
            "source_policy_dae_runner_equivalent": False,
            "monolithic_absolute_coordinate_dae_time_integrator": False,
        },
        "source_error_norm_and_output_policy_encoded": model_audit.get(
            "source_error_norm_and_output_policy_encoded"
        ),
        "brown_mcphee_candidate_friction_law_encoded": model_audit.get(
            "brown_mcphee_candidate_friction_law_encoded"
        ),
        "brown_mcphee_source_text_anchor_found": model_audit.get(
            "brown_mcphee_source_text_anchor", {}
        ).get("source_text_found"),
        "brown_mcphee_source_text_names_velocity_model": model_audit.get(
            "brown_mcphee_source_text_anchor", {}
        ).get("names_velocity_based_continuous_model"),
        "brown_mcphee_source_text_reports_mu_values": model_audit.get(
            "brown_mcphee_source_text_anchor", {}
        ).get("reports_mu_static_dynamic"),
        "brown_mcphee_published_formula_structure_encoded": model_audit.get(
            "brown_mcphee_published_formula_structure_encoded"
        ),
        "brown_mcphee_source_code_equivalent_law": model_audit.get(
            "brown_mcphee_source_code_equivalent_law"
        ),
        "brown_mcphee_transition_velocity_policy_resolved_from_source": model_audit.get(
            "brown_mcphee_transition_velocity_policy_resolved_from_source"
        ),
        "frictional_planar_candidate_rhs_smoke_implemented": model_audit.get(
            "frictional_planar_candidate_rhs_smoke_implemented"
        ),
        "candidate_friction_law_provenance": model_audit.get("candidate_friction_law_provenance"),
        "pendulum_dae_runner_implemented": runner_gap.get("pendulum_dae_runner_implemented"),
        "brown_mcphee_friction_law_implemented": runner_gap.get("brown_mcphee_friction_law_implemented"),
        "tfe_m1_m2_m3_runner_implemented": runner_gap.get("tfe_m1_m2_m3_runner_implemented"),
        "newmark_trapezoidal_runner_implemented": runner_gap.get("newmark_trapezoidal_runner_implemented"),
        "gauss6_fullva_on_source_pendulum_implemented": runner_gap.get(
            "gauss6_fullva_on_source_pendulum_implemented"
        ),
        "gauss6_fullva_absolute_coordinate_source_policy_runner_implemented": runner_gap.get(
            "gauss6_fullva_absolute_coordinate_source_policy_dae_runner_implemented"
        ),
        "gauss6_fullva_source_pendulum_candidate_smoke_implemented": (
            model_audit.get("gauss6_fullva_source_pendulum_candidate_smoke_implemented") is True
        ),
        "gauss6_fullva_source_pendulum_candidate_rows": model_audit.get(
            "gauss6_fullva_source_pendulum_candidate_rows"
        ),
        "gauss6_fullva_source_pendulum_candidate_source_policy_rows_completed": model_audit.get(
            "gauss6_fullva_source_pendulum_candidate_source_policy_rows_completed"
        ),
        "gauss6_fullva_source_pendulum_candidate_method_equivalent": model_audit.get(
            "gauss6_fullva_source_pendulum_candidate_method_equivalent"
        ),
        "gauss6_fullva_dae_candidate_contract_implemented": model_audit.get(
            "gauss6_fullva_dae_candidate_contract_implemented"
        ),
        "gauss6_fullva_dae_candidate_contract_rows": model_audit.get(
            "gauss6_fullva_dae_candidate_contract_rows"
        ),
        "gauss6_fullva_dae_candidate_contract_all_step_states_finite": model_audit.get(
            "gauss6_fullva_dae_candidate_contract_all_step_states_finite"
        ),
        "gauss6_fullva_dae_candidate_contract_all_candidate_residuals_below_1e_8": (
            model_audit.get("gauss6_fullva_dae_candidate_contract_all_candidate_residuals_below_1e_8")
        ),
        "gauss6_fullva_dae_candidate_contract_source_policy_rows_completed": model_audit.get(
            "gauss6_fullva_dae_candidate_contract_source_policy_rows_completed"
        ),
        "gauss6_fullva_dae_candidate_contract_method_equivalent": model_audit.get(
            "gauss6_fullva_dae_candidate_contract_method_equivalent"
        ),
        "gauss6_fullva_dae_candidate_contract_dae_equivalent": model_audit.get(
            "gauss6_fullva_dae_candidate_contract_dae_equivalent"
        ),
        "gauss6_fullva_dae_candidate_contract_fullva_dae_equivalent": model_audit.get(
            "gauss6_fullva_dae_candidate_contract_fullva_dae_equivalent"
        ),
        "gauss6_fullva_dae_candidate_contract_absolute_source_policy_runner_implemented": (
            model_audit.get(
                "gauss6_fullva_dae_candidate_contract_absolute_source_policy_runner_implemented"
            )
        ),
        "gauss6_fullva_source_pendulum_candidate_smoke": {
            "runner_api": gauss6_candidate_smoke.get("runner_api"),
            "t_final": gauss6_candidate_smoke.get("t_final"),
            "reference_h": gauss6_candidate_smoke.get("reference_h"),
            "comparison_h": gauss6_candidate_smoke.get("comparison_h"),
            "row_count": gauss6_candidate_smoke.get("row_count"),
            "fullva_dae_source_policy_equivalent": gauss6_candidate_smoke.get(
                "fullva_dae_source_policy_equivalent"
            ),
            "source_policy_method_runner_equivalent": gauss6_candidate_smoke.get(
                "source_policy_method_runner_equivalent"
            ),
            "source_policy_rows_completed": gauss6_candidate_smoke.get("source_policy_rows_completed"),
        },
        "gauss6_fullva_dae_candidate_contract_smoke": {
            "runner_api": gauss6_dae_candidate_contract.get("runner_api"),
            "row_count": gauss6_dae_candidate_contract.get("row_count"),
            "source_policy_rows_completed": gauss6_dae_candidate_contract.get(
                "source_policy_rows_completed"
            ),
            "source_policy_dae_runner_equivalent": gauss6_dae_candidate_contract.get(
                "source_policy_dae_runner_equivalent"
            ),
            "fullva_dae_source_policy_equivalent": gauss6_dae_candidate_contract.get(
                "fullva_dae_source_policy_equivalent"
            ),
            "accepted_use": gauss6_dae_candidate_contract.get("accepted_use"),
        },
        "source_reference_h": policy.get("solver_policy", {}).get("source_reference_h_for_exact_reproduction"),
        "source_grid_compatibility_status": grid_audit.get("status"),
        "source_grid_integer_step_compatible_rows": grid_audit.get("integer_step_compatible_rows"),
        "source_grid_integer_step_incompatible_rows": grid_audit.get("integer_step_incompatible_rows"),
        "source_grid_exact_T_compatible_rows_endpoint_convention_resolved": grid_audit.get(
            "endpoint_compatible_rows_source_endpoint_convention_resolved"
        ),
        "source_grid_endpoint_incompatible_rows_requiring_policy": grid_audit.get(
            "endpoint_incompatible_rows_require_source_endpoint_policy"
        ),
        "source_grid_policy_resolved_for_exact_T_compatible_rows": grid_audit.get(
            "source_grid_policy_resolved_for_exact_T_compatible_rows"
        ),
        "source_grid_endpoint_compatible_row_ids": grid_audit.get("source_endpoint_compatible_row_ids"),
        "source_grid_endpoint_incompatible_row_ids": grid_audit.get("source_endpoint_incompatible_row_ids"),
        "source_grid_policy_resolved_for_full_T10": grid_audit.get(
            "source_grid_policy_resolved_for_full_T10"
        ),
        "algorithm_literal_endpoint_probe": "TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE.md",
        "algorithm_literal_endpoint_probe_json": "TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE.json",
        "algorithm_literal_endpoint_probe_status": algorithm_literal_endpoint_probe.get("status"),
        "algorithm_literal_endpoint_probe_method_count": algorithm_literal_endpoint_probe.get("method_count"),
        "algorithm_literal_endpoint_probe_metric_row_count": algorithm_literal_endpoint_probe.get("metric_row_count"),
        "algorithm_literal_endpoint_probe_terminal_overrun_rows": algorithm_literal_endpoint_probe.get(
            "terminal_overrun_rows"
        ),
        "algorithm_literal_endpoint_probe_source_policy_rows_completed": algorithm_literal_endpoint_probe.get(
            "source_policy_rows_completed"
        ),
        "algorithm_literal_endpoint_probe_exact_T_error_sampling_equivalent": algorithm_literal_endpoint_probe.get(
            "source_policy_exact_T_error_sampling_equivalent"
        ),
        "source_newton_tolerance": policy.get("solver_policy", {}).get("newton_tolerance"),
        "source_model": policy.get("model"),
        "source_cases": list(cases),
        "source_methods_available": list(methods),
        "source_policy_resolved_evidence": TFE_RESOLVED_SOURCE_POLICY_EVIDENCE,
        "source_policy_risk_counts": source_policy_risk_counts,
        "closure_criteria": closure_criteria,
        "rows": audited_rows,
        "decision": {
            "can_close_tfe_b2_requirement_now": False,
            "reason": (
                "The original TFE pendulum source parameters and reference policy are extracted, "
                "and the source pendulum parameter model now has runnable frictionless, planar metric, "
                "absolute-coordinate residual, bounded source-output trajectory, bounded h=1e-4 "
                "reference-policy, full T=10 frictionless h=1e-4 source-reference probe, candidate Newmark/trapezoidal, candidate TFE m=1/2/3, "
                "Appendix-B coefficient certificate, unified bounded source-policy runner, active-B2 bounded candidate-row, "
                "full T=10 coarse candidate probe, TFE m=3 full-T10 formula-probe, and Gauss6/FullVA "
                "source-pendulum candidate-smoke layers. The Brown--McPhee source-text anchors "
                "and candidate published-formula structure are now recorded, but source-policy method-runner "
                "equivalence, Brown--McPhee friction/source-code equivalence, the four non-exact-T "
                "step-grid endpoint convention rows, absolute-coordinate FullVA DAE source-policy execution, "
                "and exact TFE source-policy rows are not implemented. "
                "The four active TFE rows remain diagnostic common-reference rows, not source-policy reproduction."
            ),
            "required_to_close": [
                "promote source pendulum parameter model, planar metrics, residual smoke, bounded source-output trajectory smoke, and comparator/TFE candidate runners to a source-output absolute-coordinate DAE source-policy runner",
                "implement Brown--McPhee friction law or verify a source-code equivalent",
                "implement TFE m=1/m=2/m=3, Newmark-beta, and trapezoidal source-policy runners",
                "resolve the T=10 endpoint convention for source h values that do not divide the horizon",
                "promote the Gauss6/FullVA source-pendulum candidate smoke to an absolute-coordinate FullVA DAE source-policy row or explicitly demote the suite",
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
            "tfe_source_policy_spec": "TFE_SOURCE_POLICY_SPEC.json",
            "tfe_source_pendulum_model_audit": "TFE_SOURCE_PENDULUM_MODEL_AUDIT.json",
            "source_policy_runner_equivalence_preflight": "TFE_SOURCE_PENDULUM_MODEL_AUDIT.json#source_policy_runner_equivalence_preflight",
            "tfe_source_grid_compatibility_audit": "TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.json",
            "source_policy_row_closure_ledger": "SOURCE_POLICY_ROW_CLOSURE_LEDGER.json",
            "all_examples_source_policy_audit": "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.json",
            "external_source_policy_closure_manifest": "EXTERNAL_SOURCE_POLICY_CLOSURE_MANIFEST.json",
            "external_case_evidence_reconciliation": "EXTERNAL_CASE_EVIDENCE_RECONCILIATION.json",
            "tfe_algorithm_literal_endpoint_probe": "TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE.json",
        },
        "cross_artifact_boundary": {
            "closure_manifest_not_ready_or_demote_suites": closure_manifest.get("not_ready_or_demote_suites", []),
            "external_case_not_ready_or_demote_suites": external_case.get("not_ready_or_demote_suites", []),
        },
    }

    out_json = PAPER / "TFE_SOURCE_POLICY_ROW_AUDIT.json"
    out_md = PAPER / "TFE_SOURCE_POLICY_ROW_AUDIT.md"
    with out_json.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# TFE Source-Policy Row Audit",
        "",
        "Status: **source policy spec extracted; runner rows not closed**.",
        "",
        "This audit is read-only over existing paper-package artifacts. It does not implement or run the TFE pendulum.",
        "",
        f"- Active B2 flagged TFE rows: `{output['active_b2_flagged_rows']}`.",
        f"- Source-policy spec extracted: `{output['source_policy_spec_extracted']}`.",
        f"- Source pendulum parameter model implemented: `{output['source_pendulum_parameter_model_implemented']}`.",
        f"- Frictionless planar RHS smoke implemented: `{output['frictionless_planar_rhs_smoke_implemented']}`.",
        f"- Absolute-coordinate DAE residual smoke implemented: `{output['absolute_coordinate_dae_residual_smoke_implemented']}`.",
        f"- Absolute-coordinate frictional candidate DAE smoke implemented: `{output['absolute_coordinate_frictional_candidate_dae_smoke_implemented']}`.",
        f"- Absolute-coordinate planar-lift trajectory probe implemented: `{output['absolute_coordinate_planar_lift_trajectory_probe_implemented']}`.",
        f"- Absolute-coordinate planar-lift rows/metric rows/source-policy rows: `{output['absolute_coordinate_planar_lift_trajectory_probe_rows']}/{output['absolute_coordinate_planar_lift_trajectory_probe_metric_rows']}/{output['absolute_coordinate_planar_lift_trajectory_probe_source_policy_rows_completed']}`.",
        f"- Absolute-coordinate planar-lift equivalent DAE runner: `{output['absolute_coordinate_planar_lift_trajectory_probe_dae_runner_equivalent']}`.",
        f"- Bounded absolute-coordinate DAE trajectory runner implemented: `{output['bounded_absolute_coordinate_dae_trajectory_runner_implemented']}`.",
        f"- Bounded absolute-coordinate DAE trajectory runner rows/metric rows/step residual rows: `{output['bounded_absolute_coordinate_dae_trajectory_runner_rows']}/{output['bounded_absolute_coordinate_dae_trajectory_runner_metric_rows']}/{output['bounded_absolute_coordinate_dae_trajectory_runner_step_residual_rows']}`.",
        f"- Bounded absolute-coordinate DAE trajectory runner source-policy rows/equivalent DAE/monolithic integrator: `{output['bounded_absolute_coordinate_dae_trajectory_runner_source_policy_rows_completed']}/{output['bounded_absolute_coordinate_dae_trajectory_runner_dae_runner_equivalent']}/{output['bounded_absolute_coordinate_dae_trajectory_runner_monolithic_integrator']}`.",
        f"- Monolithic absolute-coordinate DAE candidate runner implemented: `{output['monolithic_absolute_coordinate_dae_candidate_runner_implemented']}`.",
        f"- Monolithic absolute-coordinate DAE candidate runner rows/metric rows/step residual rows: `{output['monolithic_absolute_coordinate_dae_candidate_runner_rows']}/{output['monolithic_absolute_coordinate_dae_candidate_runner_metric_rows']}/{output['monolithic_absolute_coordinate_dae_candidate_runner_step_residual_rows']}`.",
        f"- Monolithic absolute-coordinate DAE candidate runner source-policy rows/equivalent DAE/monolithic integrator: `{output['monolithic_absolute_coordinate_dae_candidate_runner_source_policy_rows_completed']}/{output['monolithic_absolute_coordinate_dae_candidate_runner_dae_runner_equivalent']}/{output['monolithic_absolute_coordinate_dae_candidate_runner_monolithic_integrator']}`.",
        f"- Source-output time-integration smoke implemented: `{output['source_output_time_integration_smoke_implemented']}`.",
        f"- Source-policy time-integration runner equivalent: `{output['source_policy_time_integration_runner_equivalent']}`.",
        f"- Source reference solution policy smoke implemented: `{output['source_reference_solution_policy_smoke_implemented']}`.",
        f"- Source reference solution policy full T=10 run: `{output['source_reference_solution_policy_smoke_full_T10']}`.",
        f"- Source reference solution policy full T=10 probe completed/source rows: `{output['source_reference_solution_policy_full_T10_probe_completed']}/{output['source_reference_solution_policy_full_T10_probe_rows_completed']}`.",
        f"- Source reference solution policy full T=10 probe steps/check error: `{output['source_reference_solution_policy_full_T10_probe_steps']}/{output['source_reference_solution_policy_full_T10_probe_check_steps']}` / `{output['source_reference_solution_policy_full_T10_probe_coordinate_error']:.3e}/{output['source_reference_solution_policy_full_T10_probe_velocity_error']:.3e}`.",
        f"- T=10 source grid policy resolved/compatible/incompatible rows: `{output['source_grid_policy_resolved_for_full_T10']}/{output['source_grid_integer_step_compatible_rows']}/{output['source_grid_integer_step_incompatible_rows']}`.",
        f"- Exact-T compatible endpoint-grid rows resolved/requiring policy: `{output['source_grid_exact_T_compatible_rows_endpoint_convention_resolved']}/{output['source_grid_endpoint_incompatible_rows_requiring_policy']}`.",
        f"- Exact-T compatible subset grid policy resolved: `{output['source_grid_policy_resolved_for_exact_T_compatible_rows']}`.",
        f"- Source comparator candidate runners implemented: `{output['source_comparator_candidate_runners_implemented']}`.",
        f"- Newmark-beta candidate runner smoke implemented: `{output['newmark_beta_candidate_runner_smoke_implemented']}`.",
        f"- Trapezoidal candidate runner smoke implemented: `{output['trapezoidal_candidate_runner_smoke_implemented']}`.",
        f"- Source-policy method runner equivalent: `{output['source_policy_method_runner_equivalent']}`.",
        f"- TFE m=1/2/3 candidate runner smoke implemented: `{output['tfe_m1_m2_m3_candidate_runner_smoke_implemented']}`.",
        f"- Source-method candidate runner contract rows/source-policy rows/equivalent method: `{output['source_method_candidate_runner_contract_rows']}/{output['source_method_candidate_runner_contract_source_policy_rows_completed']}/{output['source_method_candidate_runner_contract_method_equivalent']}`.",
        f"- Source-method candidate runner contract finite/residual-below-1e-8: `{output['source_method_candidate_runner_contract_all_step_states_finite']}/{output['source_method_candidate_runner_contract_all_candidate_residuals_below_1e_8']}`.",
        f"- TFE Appendix-B coefficient certificate checked: `{output['tfe_appendix_b_coefficient_certificate_checked']}`.",
        f"- TFE Appendix-B coefficient certificate rows/max diff: `{output['tfe_appendix_b_coefficient_certificate_row_count']}/{output['tfe_appendix_b_coefficient_certificate_max_abs_diff']:.3e}`.",
        f"- TFE m=1/2/3 source-policy runners implemented: `{output['tfe_m1_m2_m3_source_policy_runners_implemented']}`.",
        f"- Bounded source-policy runner API implemented: `{output['bounded_source_policy_runner_api_implemented']}`.",
        f"- Bounded source-policy runner smoke implemented: `{output['bounded_source_policy_runner_smoke_implemented']}`.",
        f"- Bounded source-policy runner unified dispatch: `{output['bounded_source_policy_runner_unified_dispatch']}`.",
        f"- Bounded source-policy runner rows/full T=10/source-policy rows: `{output['bounded_source_policy_runner_rows']}/{output['bounded_source_policy_runner_full_T10']}/{output['bounded_source_policy_runner_source_policy_rows_completed']}`.",
        f"- Bounded source-policy runner method equivalent: `{output['bounded_source_policy_runner_method_equivalent']}`.",
        f"- Bounded source-policy runner accepted use: `{output['bounded_source_policy_runner_accepted_use']}`.",
        f"- Bounded source-policy runner DAE-equivalent/monolithic: `{output['bounded_source_policy_runner_dae_runner_equivalent']}/{output['bounded_source_policy_runner_monolithic_integrator']}`.",
        f"- Active TFE B2 candidate row smoke implemented: `{output['active_tfe_b2_candidate_row_smoke_implemented']}`.",
        f"- Active TFE B2 candidate row smoke full T=10: `{output['active_tfe_b2_candidate_row_smoke_full_T10']}`.",
        f"- Active TFE B2 source-policy rows completed: `{output['active_tfe_b2_source_policy_rows_completed']}`.",
        f"- Active TFE B2 full T=10 coarse candidate probe implemented: `{output['active_tfe_b2_full_T10_coarse_candidate_probe_implemented']}`.",
        f"- Active TFE B2 full T=10 coarse candidate probe full T=10/source-policy rows: `{output['active_tfe_b2_full_T10_coarse_candidate_probe_full_T10']}/{output['active_tfe_b2_full_T10_coarse_candidate_probe_source_policy_rows_completed']}`.",
        f"- Active TFE B2 full T=10 coarse candidate probe finite/residual-ok rows: `{output['active_tfe_b2_full_T10_coarse_candidate_probe_finite_rows']}/{output['active_tfe_b2_full_T10_coarse_candidate_probe_residual_ok_rows']}`.",
        f"- Active TFE B2 full T=10 coarse candidate probe source reference invoked: `{not output['active_tfe_b2_full_T10_coarse_candidate_probe_source_policy_reference_not_invoked']}`.",
        f"- Active TFE B2 source-reference full T=10 candidate probe implemented: `{output['active_tfe_b2_source_reference_full_T10_candidate_probe_implemented']}`.",
        f"- Active TFE B2 source-reference full T=10 candidate probe full T=10/reference invoked/source-policy rows: `{output['active_tfe_b2_source_reference_full_T10_candidate_probe_full_T10']}/{output['active_tfe_b2_source_reference_full_T10_candidate_probe_source_policy_reference_invoked']}/{output['active_tfe_b2_source_reference_full_T10_candidate_probe_source_policy_rows_completed']}`.",
        f"- Active TFE B2 source-reference full T=10 candidate probe finite/residual-ok rows: `{output['active_tfe_b2_source_reference_full_T10_candidate_probe_finite_rows']}/{output['active_tfe_b2_source_reference_full_T10_candidate_probe_residual_ok_rows']}`.",
        f"- TFE m=3 full T=10 coarse formula probe implemented: `{output['tfe_m3_full_T10_coarse_formula_probe_implemented']}`.",
        f"- TFE m=3 full T=10 coarse formula probe full T=10/source-policy rows: `{output['tfe_m3_full_T10_coarse_formula_probe_full_T10']}/{output['tfe_m3_full_T10_coarse_formula_probe_source_policy_rows_completed']}`.",
        f"- TFE m=3 full T=10 coarse formula probe finite/residual-ok rows: `{output['tfe_m3_full_T10_coarse_formula_probe_finite_rows']}/{output['tfe_m3_full_T10_coarse_formula_probe_residual_ok_rows']}`.",
        f"- TFE m=3 full T=10 coarse formula probe expected order: `{output['tfe_m3_full_T10_coarse_formula_probe_formal_expected_order']}`.",
        f"- TFE m=3 full T=10 coarse formula probe source reference invoked: `{not output['tfe_m3_full_T10_coarse_formula_probe_source_policy_reference_not_invoked']}`.",
        f"- Algorithm-literal endpoint probe status: `{output['algorithm_literal_endpoint_probe_status']}`.",
        f"- Algorithm-literal endpoint probe methods/metric rows/terminal overruns: `{output['algorithm_literal_endpoint_probe_method_count']}/{output['algorithm_literal_endpoint_probe_metric_row_count']}/{output['algorithm_literal_endpoint_probe_terminal_overrun_rows']}`.",
        f"- Algorithm-literal endpoint probe source-policy rows/exact-T sampling equivalent: `{output['algorithm_literal_endpoint_probe_source_policy_rows_completed']}/{output['algorithm_literal_endpoint_probe_exact_T_error_sampling_equivalent']}`.",
        f"- Source-policy DAE runner equivalent: `{output['source_policy_dae_runner_equivalent']}`.",
        f"- Source output/error policy encoded: `{output['source_error_norm_and_output_policy_encoded']}`.",
        f"- Brown--McPhee candidate friction law encoded: `{output['brown_mcphee_candidate_friction_law_encoded']}`.",
        f"- Brown--McPhee source text anchors found/model/mu: `{output['brown_mcphee_source_text_anchor_found']}/{output['brown_mcphee_source_text_names_velocity_model']}/{output['brown_mcphee_source_text_reports_mu_values']}`.",
        f"- Brown--McPhee published formula structure encoded: `{output['brown_mcphee_published_formula_structure_encoded']}`.",
        f"- Brown--McPhee source-code-equivalent law: `{output['brown_mcphee_source_code_equivalent_law']}`.",
        f"- Brown--McPhee transition velocity resolved from source: `{output['brown_mcphee_transition_velocity_policy_resolved_from_source']}`.",
        f"- Frictional candidate RHS smoke implemented: `{output['frictional_planar_candidate_rhs_smoke_implemented']}`.",
        f"- Pendulum DAE runner implemented: `{output['pendulum_dae_runner_implemented']}`.",
        f"- Brown--McPhee friction/source-code equivalent implemented: `{output['brown_mcphee_friction_law_implemented']}`.",
        f"- TFE m=1/m=2/m=3 runner implemented: `{output['tfe_m1_m2_m3_runner_implemented']}`.",
        f"- Newmark/trapezoidal runner implemented: `{output['newmark_trapezoidal_runner_implemented']}`.",
        f"- Gauss6/FullVA absolute-coordinate source-policy runner implemented: `{output['gauss6_fullva_absolute_coordinate_source_policy_runner_implemented']}`.",
        f"- Gauss6/FullVA legacy source-policy runner field: `{output['gauss6_fullva_on_source_pendulum_implemented']}`.",
        f"- Gauss6/FullVA source pendulum candidate smoke implemented: `{output['gauss6_fullva_source_pendulum_candidate_smoke_implemented']}`.",
        f"- Gauss6/FullVA source pendulum candidate rows/source-policy rows: `{output['gauss6_fullva_source_pendulum_candidate_rows']}/{output['gauss6_fullva_source_pendulum_candidate_source_policy_rows_completed']}`.",
        f"- Gauss6/FullVA source pendulum candidate method equivalent: `{output['gauss6_fullva_source_pendulum_candidate_method_equivalent']}`.",
        f"- Gauss6/FullVA DAE candidate contract rows/source-policy rows/equivalent DAE/FullVA: `{output['gauss6_fullva_dae_candidate_contract_rows']}/{output['gauss6_fullva_dae_candidate_contract_source_policy_rows_completed']}/{output['gauss6_fullva_dae_candidate_contract_dae_equivalent']}/{output['gauss6_fullva_dae_candidate_contract_fullva_dae_equivalent']}`.",
        f"- Gauss6/FullVA DAE candidate contract finite/residual-below-1e-8: `{output['gauss6_fullva_dae_candidate_contract_all_step_states_finite']}/{output['gauss6_fullva_dae_candidate_contract_all_candidate_residuals_below_1e_8']}`.",
        f"- Source-policy rows completed: `{output['source_policy_rows_completed']}`.",
        f"- Source-policy runner-equivalence preflight: `{output['source_policy_runner_equivalence_preflight_status']}`.",
        f"- Source-policy runner-equivalence preflight closed/open/source rows: `{output['source_policy_runner_equivalence_preflight_closed_preconditions']}/{output['source_policy_runner_equivalence_preflight_open_blockers']}/{output['source_policy_runner_equivalence_preflight_rows_closed']}`.",
        f"- Source-policy runner-equivalence preflight can close lane: `{output['source_policy_runner_equivalence_preflight_can_close_lane']}`.",
        f"- Runner-equivalence gap matrix open blockers: `{output['source_policy_runner_equivalence_gap_matrix']['open_blocker_count']}`.",
        f"- Runner-equivalence first required artifact: `{output['source_policy_runner_equivalence_gap_matrix']['first_required_artifact']}`.",
        (
            "- Candidate/source-policy boundary scaffold/use/DAE-equivalent/method-equivalent/rows: "
            f"`{source_spec_boundary.get('candidate_scaffold_present')}/"
            f"{source_spec_boundary.get('candidate_scaffold_allowed_use')}/"
            f"{source_spec_boundary.get('source_policy_dae_runner_equivalent')}/"
            f"{source_spec_boundary.get('source_policy_method_runner_equivalent')}/"
            f"{source_spec_boundary.get('source_policy_rows_completed')}`."
        ),
        f"- Source-policy reproduction rows: `{output['source_policy_closed_rows']}/4`.",
        f"- External-superiority-ready rows: `{output['external_superiority_ready_rows']}`.",
        f"- External superiority claim allowed: `{output['external_superiority_claim_allowed']}`.",
        f"- Default 1e-4/heavy/run_v047: `{output['execution_policy']['default_1e_4_required']}/{output['execution_policy']['heavy_numerical_run_invoked']}/{output['execution_policy']['run_v047_invoked']}`.",
        "",
        "## Closure Decision",
        "",
        f"Can close TFE B2 requirement now: `{output['decision']['can_close_tfe_b2_requirement_now']}`.",
        "",
        output["decision"]["reason"],
        "",
        "## Source-Policy Runner Equivalence Preflight",
        "",
        f"- Status: `{output['source_policy_runner_equivalence_preflight_status']}`.",
        f"- Closed preconditions/open blockers: `{output['source_policy_runner_equivalence_preflight_closed_preconditions']}/{output['source_policy_runner_equivalence_preflight_open_blockers']}`.",
        f"- Source-policy rows closed by preflight: `{output['source_policy_runner_equivalence_preflight_rows_closed']}`.",
        f"- Can close TFE lane from preflight: `{output['source_policy_runner_equivalence_preflight_can_close_lane']}`.",
        "",
        "| closed precondition | satisfied | evidence |",
        "|---|---:|---|",
    ]
    for item in runner_equivalence_preflight.get("closed_preconditions", []):
        lines.append(
            f"| `{item.get('id')}` | `{item.get('status')}` | `{item.get('evidence')}` |"
        )
    lines.extend(
        [
            "",
            "| open blocker | status | reason |",
            "|---|---|---|",
        ]
    )
    for item in runner_equivalence_preflight.get("open_blockers", []):
        lines.append(f"| `{item.get('id')}` | `{item.get('status')}` | {item.get('reason')} |")
    lines.extend(
        [
            "",
            "## Runner-Equivalence Gap Matrix",
            "",
            f"First required artifact: `{runner_gap_matrix['first_required_artifact']}`.",
            f"Ready to execute source-policy rows now: `{runner_gap_matrix['ready_to_execute_source_policy_now']}`.",
            "",
            "| open blocker | first required artifact | blocking scope | source fields |",
            "|---|---|---|---|",
        ]
    )
    for item in runner_gap_matrix["open_blockers"]:
        fields = "; ".join(item.get("blocking_source_fields", []))
        lines.append(
            f"| `{item['id']}` | {item.get('first_required_artifact')} | "
            f"{item.get('blocking_scope')} | `{fields}` |"
        )
    lines.extend(
        [
            "",
            "## Active Rows",
            "",
            "| # | example | method | source method | expected order | bounded runner vel orders | full T10 coarse vel orders | active finest vel error | source-policy |",
            "|---:|---|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in audited_rows:
        lines.append(
            f"| {row['row_index']} | `{row['example']}` | `{row['method']}` | `{row['source_method']}` | "
            f"`{row['expected_order']}` | `{row['bounded_runner_velocity_orders']}` | "
            f"`{row['full_t10_coarse_velocity_orders']}` | "
            f"`{row['active_b2_candidate_finest_velocity_error']:.3e}` | "
            f"`{row['source_policy_reproduction']}` |"
        )
    lines.extend(
        [
            "",
            "The TFE rows remain diagnostic common-reference rows, not source-policy external-superiority evidence.",
        ]
    )
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("tfe_source_policy_row_audit=written")
    print(f"active_b2_flagged_rows={len(active_rows)}")
    print("source_policy_spec_extracted=True")
    print("source_error_norm_and_output_policy_encoded=True")
    print("brown_mcphee_candidate_friction_law_encoded=True")
    print("absolute_coordinate_dae_residual_smoke_implemented=True")
    print("absolute_coordinate_planar_lift_trajectory_probe_implemented=True")
    print("absolute_coordinate_planar_lift_trajectory_probe_rows=12")
    print("source_output_time_integration_smoke_implemented=True")
    print("source_reference_solution_policy_smoke_implemented=True")
    print("source_reference_solution_policy_full_T10_probe_completed=True")
    print("source_comparator_candidate_runners_implemented=True")
    print("tfe_m1_m2_m3_candidate_runner_smoke_implemented=True")
    print("gauss6_fullva_source_pendulum_candidate_smoke_implemented=True")
    print("gauss6_fullva_absolute_coordinate_source_policy_runner_implemented=False")
    print("active_tfe_b2_candidate_row_smoke_implemented=True")
    print("active_tfe_b2_source_reference_full_T10_candidate_probe_implemented=True")
    print("pendulum_dae_runner_implemented=False")
    print("source_policy_reproduction_rows=0/4")
    print("can_close_tfe_b2_requirement_now=False")


if __name__ == "__main__":
    main()
