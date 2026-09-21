#!/usr/bin/env python3
"""Build a read-only audit for the TFE pendulum DAE runner contract gap."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
MODEL_PATH = ROOT.parent / "numerics" / "v048_cross_paper_same_test_benchmarks" / "tfe_source_pendulum_model.py"
OUT_JSON = PAPER / "TFE_DAE_RUNNER_CONTRACT_GAP_AUDIT.json"
OUT_MD = PAPER / "TFE_DAE_RUNNER_CONTRACT_GAP_AUDIT.md"


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def main() -> None:
    model_audit = read_json(PAPER / "TFE_SOURCE_PENDULUM_MODEL_AUDIT.json")
    row_audit = read_json(PAPER / "TFE_SOURCE_POLICY_ROW_AUDIT.json")
    grid_audit = read_json(PAPER / "TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.json")
    brown_law = read_json(PAPER / "TFE_BROWN_MCPHEE_SOURCE_LAW_BOUNDARY_AUDIT.json")
    brown_certificate = read_json(
        PAPER / "TFE_BROWN_MCPHEE_SOURCE_CODE_EQUIVALENCE_CERTIFICATE.json"
    )
    endpoint_probe = read_json(PAPER / "TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE.json")
    endpoint_work = read_json(PAPER / "TFE_ALGORITHM_LITERAL_WORK_PRECISION_AUDIT.json")
    endpoint_boundary = read_json(PAPER / "TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.json")
    endpoint_certificate = read_json(
        PAPER / "TFE_FULL_T10_ENDPOINT_POLICY_CLOSURE_CERTIFICATE.json"
    )
    full_t10_absolute = read_json(PAPER / "TFE_FULL_T10_ABSOLUTE_DAE_LIFT_SUMMARY.json")
    spec = read_json(PAPER / "TFE_SOURCE_POLICY_SPEC.json")
    model_source = read_text(MODEL_PATH)
    source_spec_boundary = spec.get("candidate_vs_source_policy_boundary", {})

    preflight = model_audit.get("source_policy_runner_equivalence_preflight", {})
    gap_matrix = row_audit.get("source_policy_runner_equivalence_gap_matrix", {})
    bounded = model_audit.get("bounded_absolute_coordinate_dae_trajectory_runner_smoke", {})
    monolithic_candidate = model_audit.get(
        "monolithic_absolute_coordinate_dae_candidate_runner_smoke",
        {},
    )
    source_policy_dae_contract = model_audit.get(
        "source_policy_absolute_coordinate_dae_runner_contract",
        {},
    )
    method_candidate_contract = model_audit.get(
        "source_method_candidate_runner_contract_smoke",
        {},
    )
    source_policy_method_contract = model_audit.get(
        "source_policy_method_runner_contract",
        {},
    )
    lift = model_audit.get("absolute_coordinate_planar_lift_trajectory_probe", {})
    residual = model_audit.get("absolute_coordinate_dae_residual_smoke", {})
    full_reference = model_audit.get("source_reference_solution_policy_full_T10_probe", {})
    gauss6_candidate = model_audit.get("gauss6_fullva_source_pendulum_candidate_smoke", {})
    gauss6_dae_candidate_contract = model_audit.get(
        "gauss6_fullva_dae_candidate_contract_smoke",
        {},
    )
    source_policy_gauss6_dae_contract = model_audit.get(
        "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_contract",
        {},
    )

    code_text_scan = {
        "absolute_state_lift_function_present": "def absolute_state_from_planar" in model_source,
        "absolute_residual_smoke_function_present": "def absolute_coordinate_dae_residual_smoke" in model_source,
        "bounded_stepwise_dae_runner_function_present": (
            "def bounded_absolute_coordinate_dae_trajectory_runner_smoke" in model_source
        ),
        "monolithic_candidate_dae_runner_function_present": (
            "def monolithic_absolute_coordinate_dae_candidate_runner_smoke" in model_source
        ),
        "source_policy_absolute_coordinate_dae_runner_contract_symbol_present": (
            "def source_policy_absolute_coordinate_dae_runner" in model_source
        ),
        "source_method_candidate_contract_function_present": (
            "def source_method_candidate_runner_contract_smoke" in model_source
        ),
        "source_policy_method_runner_contract_symbol_present": (
            "def source_policy_tfe_newmark_trapezoidal_method_runners" in model_source
        ),
        "gauss6_fullva_dae_candidate_contract_function_present": (
            "def source_gauss6_fullva_dae_candidate_contract_smoke" in model_source
        ),
        "source_policy_gauss6_fullva_dae_runner_contract_symbol_present": (
            "def source_policy_gauss6_fullva_absolute_coordinate_dae_runner" in model_source
        ),
        "planar_step_dispatch_function_present": "def advance_planar_method_step" in model_source,
        "explicit_monolithic_source_policy_dae_solver_function_present": (
            "def monolithic_absolute_coordinate_source_policy_dae_runner" in model_source
        ),
    }

    available_blocks = {
        "source_policy_spec_extracted": spec.get("runner_gap", {}).get("source_policy_spec_extracted"),
        "source_spec_candidate_scaffold_present": source_spec_boundary.get("candidate_scaffold_present"),
        "source_spec_candidate_allowed_use": source_spec_boundary.get("candidate_scaffold_allowed_use"),
        "source_spec_boundary_source_policy_dae_runner_equivalent": source_spec_boundary.get(
            "source_policy_dae_runner_equivalent"
        ),
        "source_spec_boundary_source_policy_method_runner_equivalent": source_spec_boundary.get(
            "source_policy_method_runner_equivalent"
        ),
        "source_spec_boundary_source_policy_rows_completed": source_spec_boundary.get(
            "source_policy_rows_completed"
        ),
        "source_spec_gauss6_candidate_smoke_available": source_spec_boundary.get(
            "gauss6_fullva_candidate_smoke_available"
        ),
        "source_spec_gauss6_candidate_smoke_allowed_use": source_spec_boundary.get(
            "gauss6_fullva_candidate_smoke_allowed_use"
        ),
        "source_spec_gauss6_candidate_smoke_source_policy_rows_completed": (
            source_spec_boundary.get(
                "gauss6_fullva_candidate_smoke_source_policy_rows_completed"
            )
        ),
        "source_spec_gauss6_source_policy_dae_runner_required": source_spec_boundary.get(
            "gauss6_fullva_absolute_coordinate_source_policy_dae_runner_required"
        ),
        "source_spec_gauss6_source_policy_dae_runner_implemented": (
            source_spec_boundary.get(
                "gauss6_fullva_absolute_coordinate_source_policy_dae_runner_implemented"
            )
        ),
        "source_spec_gauss6_source_policy_dae_runner_equivalent": (
            source_spec_boundary.get(
                "gauss6_fullva_absolute_coordinate_source_policy_dae_runner_equivalent"
            )
        ),
        "source_spec_gauss6_source_policy_dae_runner_rows_completed": (
            source_spec_boundary.get(
                "gauss6_fullva_absolute_coordinate_source_policy_dae_runner_rows_completed"
            )
        ),
        "source_pendulum_parameter_model_implemented": model_audit.get(
            "source_pendulum_parameter_model_implemented"
        ),
        "absolute_coordinate_state_lift_present": code_text_scan["absolute_state_lift_function_present"],
        "absolute_coordinate_dae_residual_smoke_implemented": model_audit.get(
            "absolute_coordinate_dae_residual_smoke_implemented"
        ),
        "absolute_coordinate_residual_smoke_equivalent": residual.get("source_policy_dae_runner_equivalent"),
        "absolute_coordinate_planar_lift_probe_rows": lift.get("row_count"),
        "absolute_coordinate_planar_lift_probe_metric_rows": lift.get("metric_row_count"),
        "absolute_coordinate_planar_lift_probe_source_policy_rows_completed": lift.get(
            "source_policy_rows_completed"
        ),
        "bounded_stepwise_dae_runner_rows": bounded.get("row_count"),
        "bounded_stepwise_dae_runner_metric_rows": bounded.get("metric_row_count"),
        "bounded_stepwise_dae_runner_step_residual_rows": bounded.get("step_residual_row_count"),
        "bounded_stepwise_dae_runner_all_step_states_finite": bounded.get("all_step_states_finite"),
        "bounded_stepwise_dae_runner_source_policy_rows_completed": bounded.get(
            "source_policy_rows_completed"
        ),
        "bounded_stepwise_dae_runner_equivalent": bounded.get("source_policy_dae_runner_equivalent"),
        "bounded_stepwise_dae_runner_monolithic": bounded.get(
            "monolithic_absolute_coordinate_dae_time_integrator"
        ),
        "monolithic_candidate_dae_runner_implemented": monolithic_candidate.get(
            "monolithic_absolute_coordinate_dae_candidate_runner_implemented"
        ),
        "monolithic_candidate_dae_runner_rows": monolithic_candidate.get("row_count"),
        "monolithic_candidate_dae_runner_metric_rows": monolithic_candidate.get("metric_row_count"),
        "monolithic_candidate_dae_runner_step_residual_rows": monolithic_candidate.get(
            "step_residual_row_count"
        ),
        "monolithic_candidate_dae_runner_all_rows_finite": monolithic_candidate.get(
            "all_rows_finite"
        ),
        "monolithic_candidate_dae_runner_residuals_below_1e_10": monolithic_candidate.get(
            "all_dae_residuals_below_1e_10"
        ),
        "monolithic_candidate_dae_runner_source_policy_rows_completed": monolithic_candidate.get(
            "source_policy_rows_completed"
        ),
        "monolithic_candidate_dae_runner_equivalent": monolithic_candidate.get(
            "source_policy_dae_runner_equivalent"
        ),
        "monolithic_candidate_dae_runner_monolithic": monolithic_candidate.get(
            "monolithic_absolute_coordinate_dae_time_integrator"
        ),
        "source_policy_absolute_coordinate_dae_runner_contract_symbol_present": (
            code_text_scan[
                "source_policy_absolute_coordinate_dae_runner_contract_symbol_present"
            ]
        ),
        "source_policy_absolute_coordinate_dae_runner_contract_present": (
            source_policy_dae_contract.get(
                "source_policy_absolute_coordinate_dae_runner_contract_present"
            )
        ),
        "source_policy_absolute_coordinate_dae_runner_implemented": (
            source_policy_dae_contract.get(
                "source_policy_absolute_coordinate_dae_runner_implemented"
            )
        ),
        "source_policy_absolute_coordinate_dae_runner_rows": (
            source_policy_dae_contract.get("row_count")
        ),
        "source_policy_absolute_coordinate_dae_runner_metric_rows": (
            source_policy_dae_contract.get("metric_row_count")
        ),
        "source_policy_absolute_coordinate_dae_runner_step_residual_rows": (
            source_policy_dae_contract.get("step_residual_row_count")
        ),
        "source_policy_absolute_coordinate_dae_runner_all_rows_finite": (
            source_policy_dae_contract.get("all_rows_finite")
        ),
        "source_policy_absolute_coordinate_dae_runner_residuals_below_1e_10": (
            source_policy_dae_contract.get("all_dae_residuals_below_1e_10")
        ),
        "source_policy_absolute_coordinate_dae_runner_source_policy_rows_completed": (
            source_policy_dae_contract.get("source_policy_rows_completed")
        ),
        "source_policy_absolute_coordinate_dae_runner_equivalent": (
            source_policy_dae_contract.get("source_policy_dae_runner_equivalent")
        ),
        "source_policy_absolute_coordinate_dae_runner_monolithic": (
            source_policy_dae_contract.get(
                "monolithic_absolute_coordinate_dae_time_integrator"
            )
        ),
        "source_policy_absolute_coordinate_dae_runner_candidate_api": (
            source_policy_dae_contract.get("candidate_runner_api")
        ),
        "source_method_candidate_contract_implemented": method_candidate_contract.get(
            "source_method_candidate_runner_contract_implemented"
        ),
        "source_method_candidate_contract_rows": method_candidate_contract.get("row_count"),
        "source_method_candidate_contract_finite": method_candidate_contract.get(
            "all_step_states_finite"
        ),
        "source_method_candidate_contract_residuals_below_1e_8": method_candidate_contract.get(
            "all_candidate_residuals_below_1e_8"
        ),
        "source_method_candidate_contract_source_policy_rows_completed": method_candidate_contract.get(
            "source_policy_rows_completed"
        ),
        "source_method_candidate_contract_equivalent": method_candidate_contract.get(
            "source_policy_method_runner_equivalent"
        ),
        "source_method_candidate_contract_dae_equivalent": method_candidate_contract.get(
            "source_policy_dae_runner_equivalent"
        ),
        "source_policy_method_runner_contract_symbol_present": (
            code_text_scan["source_policy_method_runner_contract_symbol_present"]
        ),
        "source_policy_method_runner_contract_present": (
            source_policy_method_contract.get("source_policy_method_runner_contract_present")
        ),
        "source_policy_tfe_newmark_trapezoidal_method_runners_implemented": (
            source_policy_method_contract.get(
                "source_policy_tfe_newmark_trapezoidal_method_runners_implemented"
            )
        ),
        "source_policy_method_runner_contract_rows": (
            source_policy_method_contract.get("row_count")
        ),
        "source_policy_method_runner_contract_source_policy_rows_completed": (
            source_policy_method_contract.get("source_policy_rows_completed")
        ),
        "source_policy_method_runner_contract_equivalent": (
            source_policy_method_contract.get("source_policy_method_runner_equivalent")
        ),
        "source_policy_method_runner_contract_dae_equivalent": (
            source_policy_method_contract.get("source_policy_dae_runner_equivalent")
        ),
        "source_policy_method_runner_contract_finite": (
            source_policy_method_contract.get("all_step_states_finite")
        ),
        "source_policy_method_runner_contract_residuals_below_1e_8": (
            source_policy_method_contract.get("all_candidate_residuals_below_1e_8")
        ),
        "full_T10_source_reference_probe_completed": full_reference.get(
            "full_T10_source_reference_probe_completed"
        ),
        "full_T10_source_reference_probe_rows_completed": full_reference.get(
            "source_policy_rows_completed"
        ),
        "gauss6_fullva_source_pendulum_candidate_smoke_implemented": gauss6_candidate.get(
            "gauss6_fullva_source_pendulum_candidate_smoke_implemented"
        ),
        "gauss6_fullva_absolute_coordinate_source_policy_runner_implemented": gauss6_candidate.get(
            "gauss6_fullva_absolute_coordinate_source_policy_runner_implemented"
        ),
        "gauss6_fullva_candidate_source_policy_rows_completed": gauss6_candidate.get(
            "source_policy_rows_completed"
        ),
        "gauss6_fullva_dae_candidate_contract_implemented": gauss6_dae_candidate_contract.get(
            "gauss6_fullva_dae_candidate_contract_implemented"
        ),
        "gauss6_fullva_dae_candidate_contract_rows": gauss6_dae_candidate_contract.get(
            "row_count"
        ),
        "gauss6_fullva_dae_candidate_contract_finite": gauss6_dae_candidate_contract.get(
            "all_step_states_finite"
        ),
        "gauss6_fullva_dae_candidate_contract_residuals_below_1e_8": (
            gauss6_dae_candidate_contract.get("all_candidate_residuals_below_1e_8")
        ),
        "gauss6_fullva_dae_candidate_contract_source_policy_rows_completed": (
            gauss6_dae_candidate_contract.get("source_policy_rows_completed")
        ),
        "gauss6_fullva_dae_candidate_contract_equivalent": (
            gauss6_dae_candidate_contract.get("source_policy_dae_runner_equivalent")
        ),
        "gauss6_fullva_dae_candidate_contract_fullva_equivalent": (
            gauss6_dae_candidate_contract.get("fullva_dae_source_policy_equivalent")
        ),
        "source_policy_gauss6_fullva_dae_runner_contract_symbol_present": (
            code_text_scan[
                "source_policy_gauss6_fullva_dae_runner_contract_symbol_present"
            ]
        ),
        "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_contract_present": (
            source_policy_gauss6_dae_contract.get(
                "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_contract_present"
            )
        ),
        "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_implemented": (
            source_policy_gauss6_dae_contract.get(
                "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_implemented"
            )
        ),
        "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_rows": (
            source_policy_gauss6_dae_contract.get("row_count")
        ),
        "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_source_policy_rows_completed": (
            source_policy_gauss6_dae_contract.get("source_policy_rows_completed")
        ),
        "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_equivalent": (
            source_policy_gauss6_dae_contract.get("source_policy_dae_runner_equivalent")
        ),
        "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_fullva_equivalent": (
            source_policy_gauss6_dae_contract.get("fullva_dae_source_policy_equivalent")
        ),
        "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_monolithic": (
            source_policy_gauss6_dae_contract.get(
                "monolithic_absolute_coordinate_dae_time_integrator"
            )
        ),
        "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_finite": (
            source_policy_gauss6_dae_contract.get("all_step_states_finite")
        ),
        "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_residuals_below_1e_8": (
            source_policy_gauss6_dae_contract.get("all_candidate_residuals_below_1e_8")
        ),
        "full_T10_absolute_dae_lift_completed": full_t10_absolute.get(
            "full_T10_absolute_coordinate_lift_completed"
        ),
        "full_T10_absolute_dae_lift_metric_rows": full_t10_absolute.get("metric_row_count"),
        "full_T10_absolute_dae_lift_step_residual_rows": full_t10_absolute.get(
            "step_residual_row_count"
        ),
        "full_T10_absolute_dae_lift_source_reference_invoked": full_t10_absolute.get(
            "source_reference_invoked"
        ),
        "full_T10_absolute_dae_lift_source_policy_rows_completed": full_t10_absolute.get(
            "source_policy_rows_completed"
        ),
        "full_T10_absolute_dae_lift_monolithic": full_t10_absolute.get(
            "monolithic_absolute_coordinate_dae_time_integrator"
        ),
        "full_T10_absolute_dae_lift_equivalent": full_t10_absolute.get(
            "source_policy_dae_runner_equivalent"
        ),
        "preflight_closed_preconditions": preflight.get("closed_precondition_count"),
        "preflight_open_blockers": preflight.get("open_blocker_count"),
        "preflight_source_policy_rows_closed": preflight.get("source_policy_rows_closed_by_preflight"),
    }

    missing_blocks = [
        {
            "id": row.get("id"),
            "status": row.get("status"),
            "first_required_artifact": row.get("first_required_artifact"),
            "blocking_scope": row.get("blocking_scope"),
            "can_resolve_without_heavy_run": row.get("can_resolve_without_heavy_run"),
        }
        for row in gap_matrix.get("open_blockers", [])
    ]
    nonheavy_missing = [
        row["id"] for row in missing_blocks if row.get("can_resolve_without_heavy_run") is True
    ]
    source_policy_execution_missing = [
        row["id"] for row in missing_blocks if row.get("can_resolve_without_heavy_run") is False
    ]
    source_policy_execution_preflight = {
        "schema": "tfe-source-policy-execution-preflight-v1",
        "status": "terminal_no_public_code_self_reproduction_attempted_not_promoted",
        "read_only": True,
        "heavy_numerical_run_invoked": False,
        "run_v047_invoked": False,
        "v048_runner_invoked": False,
        "current_route": "no_public_code_self_reproduction_attempted_unable_to_reproduce_not_promoted",
        "nonheavy_blocks_dispositioned_by_demotion": None,
        "nonheavy_demotion_does_not_close_source_policy": True,
        "execution_block_count": len(source_policy_execution_missing),
        "execution_blocks": source_policy_execution_missing,
        "runner_contracts_required_before_execution": [
            "monolithic_absolute_coordinate_DAE_time_integrator",
            "TFE_m1_m2_m3_Newmark_beta_trapezoidal_source_policy_method_runners",
            "Gauss6_FullVA_absolute_coordinate_source_policy_DAE_runner",
            "accepted_T10_source_policy_work_precision_rows",
        ],
        "source_policy_rows_completed": 0,
        "can_promote_any_tfe_source_policy_row_now": False,
        "ready_to_execute_source_policy_now": False,
        "explicit_user_opt_in_required": False,
        "opt_in_required_for": [],
        "reopen_condition": "new_public_or_source_code_equivalent_tfe_implementation_artifact",
        "reviewer_facing_decision": "no_public_code_self_reproduction_attempted_unable_to_reproduce_not_promoted",
    }
    brown_demotion_allowed_use = brown_law.get(
        "frictional_source_policy_row_demotion_contract", {}
    ).get("candidate_evidence_allowed_use")
    brown_nonheavy_demoted = (
        brown_law.get("frictional_source_policy_rows_demoted") is True
        and brown_law.get("source_policy_rows_promoted") == 0
        and brown_demotion_allowed_use
        == "local_dissipativity_residual_sensitivity_diagnostic_only"
    )
    endpoint_demotion_contract = endpoint_boundary.get("endpoint_incompatible_demotion_contract")
    endpoint_nonheavy_demoted = (
        endpoint_boundary.get("endpoint_incompatible_rows_demoted_from_source_policy")
        == grid_audit.get("integer_step_incompatible_rows")
        == 4
        and endpoint_boundary.get("source_policy_rows_completed") == 0
        and isinstance(endpoint_demotion_contract, str)
        and "diagnostic-only" in endpoint_demotion_contract
    )
    nonheavy_dispositions = [
        {
            "id": "brown_mcphee_source_code_equivalent_law_open",
            "disposition": "demoted_not_promoted" if brown_nonheavy_demoted else "open",
            "demotion_evidence": "TFE_BROWN_MCPHEE_SOURCE_LAW_BOUNDARY_AUDIT.json",
            "source_code_equivalence_certificate": (
                "TFE_BROWN_MCPHEE_SOURCE_CODE_EQUIVALENCE_CERTIFICATE.json"
            ),
            "certificate_status": brown_certificate.get("status"),
            "certificate_available": brown_certificate.get("certificate_available"),
            "positive_source_code_equivalence_certified": brown_certificate.get(
                "positive_source_code_equivalence_certified"
            ),
            "negative_certificate_nonheavy_block_closed": brown_certificate.get(
                "nonheavy_contract_block_closed"
            ),
            "source_policy_execution_invoked": brown_certificate.get(
                "source_policy_execution_invoked"
            ),
            "can_close_now": brown_certificate.get("can_close_now"),
            "frictional_source_policy_rows_demoted": brown_law.get(
                "frictional_source_policy_rows_demoted"
            ),
            "source_policy_rows_promoted": brown_law.get("source_policy_rows_promoted"),
            "source_policy_rows_completed": brown_certificate.get(
                "source_policy_rows_completed"
            ),
            "candidate_evidence_allowed_use": brown_demotion_allowed_use,
            "demotion_reason": brown_law.get(
                "frictional_source_policy_row_demotion_contract", {}
            ).get("demotion_reason"),
            "required_to_promote": brown_law.get(
                "frictional_source_policy_row_demotion_contract", {}
            ).get("required_to_promote"),
            "still_missing_source_code_equivalent_law": (
                brown_law.get("brown_mcphee_source_code_equivalent_law") is False
            ),
            "transition_velocity_policy_resolved_from_source": brown_law.get(
                "brown_mcphee_transition_velocity_policy_resolved_from_source"
            ),
            "does_not_close_source_policy": True,
        },
        {
            "id": "full_T10_source_grid_endpoint_policy_open",
            "disposition": "demoted_not_promoted" if endpoint_nonheavy_demoted else "open",
            "demotion_evidence": "TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.json",
            "endpoint_incompatible_rows_demoted_from_source_policy": endpoint_boundary.get(
                "endpoint_incompatible_rows_demoted_from_source_policy"
            ),
            "source_policy_rows_completed": endpoint_boundary.get("source_policy_rows_completed"),
            "source_grid_policy_resolved_for_full_T10": endpoint_boundary.get(
                "source_grid_policy_resolved_for_full_T10"
            ),
            "source_policy_exact_T_error_sampling_equivalent": endpoint_boundary.get(
                "source_policy_exact_T_error_sampling_equivalent"
            ),
            "algorithm_literal_exact_T_row_count": endpoint_boundary.get(
                "algorithm_literal_exact_T_row_count"
            ),
            "algorithm_literal_overrun_row_count": endpoint_boundary.get(
                "algorithm_literal_overrun_row_count"
            ),
            "endpoint_incompatible_demotion_contract": endpoint_boundary.get(
                "endpoint_incompatible_demotion_contract"
            ),
            "endpoint_policy_closure_certificate": (
                "TFE_FULL_T10_ENDPOINT_POLICY_CLOSURE_CERTIFICATE.json"
            ),
            "certificate_status": endpoint_certificate.get("status"),
            "certificate_available": endpoint_certificate.get("certificate_available"),
            "positive_full_T10_endpoint_policy_certified": endpoint_certificate.get(
                "positive_full_T10_endpoint_policy_certified"
            ),
            "negative_certificate_nonheavy_block_closed": endpoint_certificate.get(
                "nonheavy_contract_block_closed"
            ),
            "source_policy_execution_invoked": endpoint_certificate.get(
                "source_policy_execution_invoked"
            ),
            "can_close_now": endpoint_certificate.get("can_close_now"),
            "does_not_close_source_policy": True,
        },
    ]
    nonheavy_dispositioned_by_demotion = (
        [row["id"] for row in nonheavy_dispositions] == nonheavy_missing
        and all(row["disposition"] == "demoted_not_promoted" for row in nonheavy_dispositions)
    )
    source_policy_execution_preflight[
        "nonheavy_blocks_dispositioned_by_demotion"
    ] = nonheavy_dispositioned_by_demotion
    effective_missing_contract_blocks = list(source_policy_execution_missing)
    candidate_backed_non_equivalent_runner_blocks = [
        {
            "id": "pendulum_absolute_coordinate_source_policy_dae_runner_missing",
            "contract_present": source_policy_dae_contract.get(
                "source_policy_absolute_coordinate_dae_runner_contract_present"
            ),
            "candidate_backed": source_policy_dae_contract.get("runner_api")
            == "source_policy_absolute_coordinate_dae_runner",
            "implemented": source_policy_dae_contract.get(
                "source_policy_absolute_coordinate_dae_runner_implemented"
            ),
            "source_policy_equivalent": source_policy_dae_contract.get(
                "source_policy_dae_runner_equivalent"
            ),
            "source_policy_rows_completed": source_policy_dae_contract.get(
                "source_policy_rows_completed"
            ),
            "closure_status": "open_candidate_backed_not_source_policy_equivalent",
        },
        {
            "id": "tfe_newmark_trapezoidal_source_policy_method_runners_missing",
            "contract_present": source_policy_method_contract.get(
                "source_policy_method_runner_contract_present"
            ),
            "candidate_backed": source_policy_method_contract.get("runner_api")
            == "source_policy_tfe_newmark_trapezoidal_method_runners",
            "implemented": source_policy_method_contract.get(
                "source_policy_tfe_newmark_trapezoidal_method_runners_implemented"
            ),
            "source_policy_equivalent": source_policy_method_contract.get(
                "source_policy_method_runner_equivalent"
            ),
            "source_policy_rows_completed": source_policy_method_contract.get(
                "source_policy_rows_completed"
            ),
            "closure_status": "open_candidate_backed_not_source_policy_equivalent",
        },
        {
            "id": "gauss6_fullva_absolute_coordinate_source_policy_runner_missing",
            "contract_present": source_policy_gauss6_dae_contract.get(
                "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_contract_present"
            ),
            "candidate_backed": source_policy_gauss6_dae_contract.get("runner_api")
            == "source_policy_gauss6_fullva_absolute_coordinate_dae_runner",
            "implemented": source_policy_gauss6_dae_contract.get(
                "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_implemented"
            ),
            "source_policy_equivalent": source_policy_gauss6_dae_contract.get(
                "source_policy_dae_runner_equivalent"
            ),
            "source_policy_rows_completed": source_policy_gauss6_dae_contract.get(
                "source_policy_rows_completed"
            ),
            "closure_status": "open_candidate_backed_not_source_policy_equivalent",
        },
    ]
    terminal_nonpromoted_contract_blocks = (
        list(nonheavy_missing) if nonheavy_dispositioned_by_demotion else []
    )
    contract_block_accounting = {
        "raw_open_contract_block_count": len(missing_blocks),
        "raw_open_contract_blocks": [row["id"] for row in missing_blocks],
        "terminal_nonpromoted_contract_block_count": len(terminal_nonpromoted_contract_blocks),
        "terminal_nonpromoted_contract_blocks": terminal_nonpromoted_contract_blocks,
        "effective_source_policy_execution_contract_block_count": len(
            effective_missing_contract_blocks
        ),
        "effective_source_policy_execution_contract_blocks": effective_missing_contract_blocks,
        "source_policy_rows_closed_by_accounting": 0,
        "accounting_disposition": (
            "nonheavy_terminal_demotions_recorded_source_policy_execution_blocks_remain"
        ),
    }

    output: dict[str, Any] = {
        "schema": "tfe-dae-runner-contract-gap-audit-v1",
        "status": "dae_runner_contract_gap_open_not_source_policy",
        "read_only": True,
        "heavy_numerical_run_invoked": False,
        "run_v047_invoked": False,
        "v048_runner_invoked": False,
        "submission_ready": False,
        "external_superiority_claim_allowed": False,
        "source_policy_rows_completed": 0,
        "source_policy_dae_runner_equivalent": False,
        "source_policy_method_runner_equivalent": False,
        "pendulum_dae_runner_implemented": False,
        "source_policy_absolute_coordinate_dae_runner_contract_present": (
            source_policy_dae_contract.get(
                "source_policy_absolute_coordinate_dae_runner_contract_present"
            )
        ),
        "source_policy_absolute_coordinate_dae_runner_implemented": (
            source_policy_dae_contract.get(
                "source_policy_absolute_coordinate_dae_runner_implemented"
            )
        ),
        "source_policy_method_runner_contract_present": (
            source_policy_method_contract.get("source_policy_method_runner_contract_present")
        ),
        "source_policy_tfe_newmark_trapezoidal_method_runners_implemented": (
            source_policy_method_contract.get(
                "source_policy_tfe_newmark_trapezoidal_method_runners_implemented"
            )
        ),
        "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_contract_present": (
            source_policy_gauss6_dae_contract.get(
                "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_contract_present"
            )
        ),
        "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_implemented": (
            source_policy_gauss6_dae_contract.get(
                "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_implemented"
            )
        ),
        "monolithic_absolute_coordinate_dae_time_integrator": False,
        "ready_to_execute_source_policy_now": False,
        "code_text_scan": code_text_scan,
        "available_contract_blocks": available_blocks,
        "candidate_vs_source_policy_boundary": source_spec_boundary,
        "missing_contract_blocks": missing_blocks,
        "missing_contract_block_count": len(missing_blocks),
        "nonheavy_missing_contract_blocks": nonheavy_missing,
        "nonheavy_missing_contract_block_count": len(nonheavy_missing),
        "nonheavy_missing_contract_block_dispositions": nonheavy_dispositions,
        "nonheavy_missing_contract_blocks_dispositioned_by_demotion": nonheavy_dispositioned_by_demotion,
        "nonheavy_demotion_does_not_close_source_policy": True,
        "terminal_nonpromoted_contract_blocks": terminal_nonpromoted_contract_blocks,
        "terminal_nonpromoted_contract_block_count": len(terminal_nonpromoted_contract_blocks),
        "effective_missing_contract_blocks": effective_missing_contract_blocks,
        "effective_missing_contract_block_count": len(effective_missing_contract_blocks),
        "contract_block_accounting": contract_block_accounting,
        "source_policy_execution_missing_contract_blocks": source_policy_execution_missing,
        "source_policy_execution_missing_contract_block_count": len(source_policy_execution_missing),
        "candidate_backed_non_equivalent_runner_blocks": (
            candidate_backed_non_equivalent_runner_blocks
        ),
        "candidate_backed_non_equivalent_runner_block_count": len(
            candidate_backed_non_equivalent_runner_blocks
        ),
        "candidate_backed_non_equivalent_runner_block_ids": [
            row["id"] for row in candidate_backed_non_equivalent_runner_blocks
        ],
        "source_policy_execution_missing_scope": {
            "open_blocks": source_policy_execution_missing,
            "missing_block_count": len(source_policy_execution_missing),
            "candidate_backed_non_equivalent_runner_block_count": len(
                candidate_backed_non_equivalent_runner_blocks
            ),
            "candidate_backed_non_equivalent_runner_blocks": [
                row["id"] for row in candidate_backed_non_equivalent_runner_blocks
            ],
            "requires_new_runner_contract_or_explicit_source_policy_execution": False,
            "requires_new_public_or_source_code_equivalent_artifact_to_reopen": True,
            "ready_to_execute_source_policy_now": False,
        },
        "source_policy_execution_preflight": source_policy_execution_preflight,
        "grid_policy": {
            "source_grid_policy_resolved_for_exact_T_compatible_rows": grid_audit.get(
                "source_grid_policy_resolved_for_exact_T_compatible_rows"
            ),
            "source_grid_policy_resolved_for_full_T10": grid_audit.get(
                "source_grid_policy_resolved_for_full_T10"
            ),
            "integer_step_compatible_rows": grid_audit.get("integer_step_compatible_rows"),
            "integer_step_incompatible_rows": grid_audit.get("integer_step_incompatible_rows"),
        },
        "nonheavy_blocker_evidence": {
            "brown_mcphee": {
                "audit": "TFE_BROWN_MCPHEE_SOURCE_LAW_BOUNDARY_AUDIT.json",
                "source_code_equivalence_certificate": (
                    "TFE_BROWN_MCPHEE_SOURCE_CODE_EQUIVALENCE_CERTIFICATE.json"
                ),
                "status": brown_law.get("status"),
                "certificate_status": brown_certificate.get("status"),
                "certificate_available": brown_certificate.get("certificate_available"),
                "positive_source_code_equivalence_certified": brown_certificate.get(
                    "positive_source_code_equivalence_certified"
                ),
                "negative_certificate_nonheavy_block_closed": brown_certificate.get(
                    "nonheavy_contract_block_closed"
                ),
                "source_policy_execution_invoked": brown_certificate.get(
                    "source_policy_execution_invoked"
                ),
                "can_close_now": brown_certificate.get("can_close_now"),
                "candidate_formula_encoded": brown_law.get(
                    "brown_mcphee_candidate_friction_law_encoded"
                ),
                "published_formula_structure_encoded": brown_law.get(
                    "brown_mcphee_published_formula_structure_encoded"
                ),
                "source_code_equivalent_law": brown_law.get(
                    "brown_mcphee_source_code_equivalent_law"
                ),
                "transition_velocity_policy_resolved_from_source": brown_law.get(
                    "brown_mcphee_transition_velocity_policy_resolved_from_source"
                ),
                "frictional_source_policy_rows_demoted": brown_law.get(
                    "frictional_source_policy_rows_demoted"
                ),
                "frictional_source_policy_demotion_allowed_use": brown_law.get(
                    "frictional_source_policy_row_demotion_contract", {}
                ).get("candidate_evidence_allowed_use"),
                "closure_can_close_now": brown_law.get("closure_decision", {}).get(
                    "can_close_brown_mcphee_source_code_equivalent_law_now"
                ),
                "source_policy_rows_promoted": brown_law.get("source_policy_rows_promoted"),
            },
            "endpoint_policy": {
                "grid_audit": "TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.json",
                "algorithm_literal_probe": "TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE.json",
                "algorithm_literal_work_precision": "TFE_ALGORITHM_LITERAL_WORK_PRECISION_AUDIT.json",
                "endpoint_boundary_certificate": "TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.json",
                "endpoint_policy_closure_certificate": (
                    "TFE_FULL_T10_ENDPOINT_POLICY_CLOSURE_CERTIFICATE.json"
                ),
                "certificate_status": endpoint_certificate.get("status"),
                "certificate_available": endpoint_certificate.get("certificate_available"),
                "positive_full_T10_endpoint_policy_certified": endpoint_certificate.get(
                    "positive_full_T10_endpoint_policy_certified"
                ),
                "negative_certificate_nonheavy_block_closed": endpoint_certificate.get(
                    "nonheavy_contract_block_closed"
                ),
                "source_policy_execution_invoked": endpoint_certificate.get(
                    "source_policy_execution_invoked"
                ),
                "can_close_now": endpoint_certificate.get("can_close_now"),
                "source_text_fixed_h_loop_supported": endpoint_probe.get(
                    "source_text_fixed_h_loop_supported"
                ),
                "algorithm_literal_endpoint_policy": endpoint_probe.get(
                    "algorithm_literal_endpoint_policy"
                ),
                "endpoint_probe_metric_rows": endpoint_probe.get("metric_row_count"),
                "endpoint_probe_terminal_overrun_rows": endpoint_probe.get(
                    "terminal_overrun_rows"
                ),
                "endpoint_probe_source_policy_rows_completed": endpoint_probe.get(
                    "source_policy_rows_completed"
                ),
                "work_precision_rows": endpoint_work.get("raw_row_count"),
                "work_precision_summary_rows": endpoint_work.get("summary_row_count"),
                "work_precision_figure_available": endpoint_work.get(
                    "work_precision_figure_available"
                ),
                "work_precision_b4_progress": endpoint_work.get("decision", {}).get(
                    "b4_progress"
                ),
                "work_precision_b4_closure": endpoint_work.get("decision", {}).get(
                    "b4_closure"
                ),
                "source_policy_exact_T_error_sampling_equivalent": endpoint_work.get(
                    "source_policy_exact_T_error_sampling_equivalent"
                ),
                "source_policy_method_runner_equivalent": endpoint_work.get(
                    "source_policy_method_runner_equivalent"
                ),
                "literal_overrun_bound_proved": endpoint_boundary.get("theorem", {}).get(
                    "name"
                )
                == "fixed_h_until_final_time_endpoint_bound",
                "literal_exact_T_rows": endpoint_boundary.get(
                    "algorithm_literal_exact_T_row_count"
                ),
                "literal_overrun_rows": endpoint_boundary.get(
                    "algorithm_literal_overrun_row_count"
                ),
                "boundary_source_policy_rows_completed": endpoint_boundary.get(
                    "source_policy_rows_completed"
                ),
                "boundary_full_T10_policy_resolved": endpoint_boundary.get(
                    "source_grid_policy_resolved_for_full_T10"
                ),
                "endpoint_incompatible_rows_demoted_from_source_policy": endpoint_boundary.get(
                    "endpoint_incompatible_rows_demoted_from_source_policy"
                ),
                "endpoint_incompatible_demotion_contract": endpoint_boundary.get(
                    "endpoint_incompatible_demotion_contract"
                ),
                "boundary_exact_T_error_sampling_equivalent": endpoint_boundary.get(
                    "source_policy_exact_T_error_sampling_equivalent"
                ),
            },
        },
        "closure_decision": {
            "can_close_tfe_lane_now": False,
            "can_close_b4_b7_now": False,
            "reason": (
                "Current evidence proves a parameter model, source metrics, absolute-coordinate residual "
                "smokes, and a bounded stepwise residual runner. It does not prove a monolithic "
                "absolute-coordinate source-policy DAE time integrator, source-method equivalence, "
                "full T=10 endpoint policy, or accepted work/precision row binding."
            ),
        },
        "safe_next_actions": [
            "Keep the recorded Gauss6 runner-vs-candidate split active until a source-policy DAE runner artifact appears.",
            "Keep the recorded negative Brown-McPhee source-code-equivalence certificate active and do not promote frictional rows until source code or Refs. 38-39 resolve the transition policy.",
            "Keep the endpoint-incompatible h-row demotion boundary in force until source-confirmed output sampling is available.",
            "Only after the DAE and method-runner contracts exist, run accepted TFE source-policy rows under explicit opt-in.",
        ],
        "source_files": {
            "model_audit": "TFE_SOURCE_PENDULUM_MODEL_AUDIT.json",
            "row_audit": "TFE_SOURCE_POLICY_ROW_AUDIT.json",
            "grid_audit": "TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.json",
            "brown_mcphee_source_law_boundary": "TFE_BROWN_MCPHEE_SOURCE_LAW_BOUNDARY_AUDIT.json",
            "brown_mcphee_source_code_equivalence_certificate": (
                "TFE_BROWN_MCPHEE_SOURCE_CODE_EQUIVALENCE_CERTIFICATE.json"
            ),
            "algorithm_literal_endpoint_probe": "TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE.json",
            "algorithm_literal_work_precision": "TFE_ALGORITHM_LITERAL_WORK_PRECISION_AUDIT.json",
            "endpoint_policy_boundary_certificate": "TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.json",
            "full_T10_endpoint_policy_closure_certificate": (
                "TFE_FULL_T10_ENDPOINT_POLICY_CLOSURE_CERTIFICATE.json"
            ),
            "full_T10_absolute_dae_lift_summary": "TFE_FULL_T10_ABSOLUTE_DAE_LIFT_SUMMARY.json",
            "source_spec": "TFE_SOURCE_POLICY_SPEC.json",
            "model_source": "../../numerics/v048_cross_paper_same_test_benchmarks/tfe_source_pendulum_model.py",
        },
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# TFE DAE Runner Contract Gap Audit",
        "",
        "Status: **DAE runner contract gap open; not source policy**.",
        "",
        "This audit is read-only over existing TFE artifacts and source text. It does not run a numerical campaign.",
        "",
        f"- Source-policy rows completed: `{output['source_policy_rows_completed']}`.",
        (
            "- Source spec candidate/source-policy boundary scaffold/use/DAE-equivalent/method-equivalent/rows: "
            f"`{source_spec_boundary.get('candidate_scaffold_present')}/"
            f"{source_spec_boundary.get('candidate_scaffold_allowed_use')}/"
            f"{source_spec_boundary.get('source_policy_dae_runner_equivalent')}/"
            f"{source_spec_boundary.get('source_policy_method_runner_equivalent')}/"
            f"{source_spec_boundary.get('source_policy_rows_completed')}`."
        ),
        (
            "- Source spec Gauss6 candidate/source-policy DAE split available/use/runner/source rows/equivalent: "
            f"`{available_blocks['source_spec_gauss6_candidate_smoke_available']}/"
            f"{available_blocks['source_spec_gauss6_candidate_smoke_allowed_use']}/"
            f"{available_blocks['source_spec_gauss6_source_policy_dae_runner_implemented']}/"
            f"{available_blocks['source_spec_gauss6_source_policy_dae_runner_rows_completed']}/"
            f"{available_blocks['source_spec_gauss6_source_policy_dae_runner_equivalent']}`."
        ),
        f"- Source-policy DAE runner equivalent: `{output['source_policy_dae_runner_equivalent']}`.",
        f"- Monolithic absolute-coordinate DAE time integrator: `{output['monolithic_absolute_coordinate_dae_time_integrator']}`.",
        f"- Pendulum DAE runner implemented: `{output['pendulum_dae_runner_implemented']}`.",
        (
            "- Bounded stepwise DAE runner rows/metric rows/step residual rows: "
            f"`{available_blocks['bounded_stepwise_dae_runner_rows']}/"
            f"{available_blocks['bounded_stepwise_dae_runner_metric_rows']}/"
            f"{available_blocks['bounded_stepwise_dae_runner_step_residual_rows']}`."
        ),
        (
            "- Monolithic candidate DAE runner rows/metric rows/step residual rows/source rows/equivalent/monolithic: "
            f"`{available_blocks['monolithic_candidate_dae_runner_rows']}/"
            f"{available_blocks['monolithic_candidate_dae_runner_metric_rows']}/"
            f"{available_blocks['monolithic_candidate_dae_runner_step_residual_rows']}/"
            f"{available_blocks['monolithic_candidate_dae_runner_source_policy_rows_completed']}/"
            f"{available_blocks['monolithic_candidate_dae_runner_equivalent']}/"
            f"{available_blocks['monolithic_candidate_dae_runner_monolithic']}`."
        ),
        (
            "- Source-policy absolute-coordinate DAE runner contract symbol/present/implemented: "
            f"`{available_blocks['source_policy_absolute_coordinate_dae_runner_contract_symbol_present']}/"
            f"{available_blocks['source_policy_absolute_coordinate_dae_runner_contract_present']}/"
            f"{available_blocks['source_policy_absolute_coordinate_dae_runner_implemented']}`."
        ),
        (
            "- Source-policy absolute-coordinate DAE runner contract rows/metric rows/step residual rows/source rows/equivalent/monolithic: "
            f"`{available_blocks['source_policy_absolute_coordinate_dae_runner_rows']}/"
            f"{available_blocks['source_policy_absolute_coordinate_dae_runner_metric_rows']}/"
            f"{available_blocks['source_policy_absolute_coordinate_dae_runner_step_residual_rows']}/"
            f"{available_blocks['source_policy_absolute_coordinate_dae_runner_source_policy_rows_completed']}/"
            f"{available_blocks['source_policy_absolute_coordinate_dae_runner_equivalent']}/"
            f"{available_blocks['source_policy_absolute_coordinate_dae_runner_monolithic']}`."
        ),
        (
            "- Source-method candidate contract rows/source rows/equivalent method/DAE: "
            f"`{available_blocks['source_method_candidate_contract_rows']}/"
            f"{available_blocks['source_method_candidate_contract_source_policy_rows_completed']}/"
            f"{available_blocks['source_method_candidate_contract_equivalent']}/"
            f"{available_blocks['source_method_candidate_contract_dae_equivalent']}`."
        ),
        (
            "- Source-policy method runner contract symbol/present/implemented: "
            f"`{available_blocks['source_policy_method_runner_contract_symbol_present']}/"
            f"{available_blocks['source_policy_method_runner_contract_present']}/"
            f"{available_blocks['source_policy_tfe_newmark_trapezoidal_method_runners_implemented']}`."
        ),
        (
            "- Source-policy method runner contract rows/source rows/equivalent method/DAE: "
            f"`{available_blocks['source_policy_method_runner_contract_rows']}/"
            f"{available_blocks['source_policy_method_runner_contract_source_policy_rows_completed']}/"
            f"{available_blocks['source_policy_method_runner_contract_equivalent']}/"
            f"{available_blocks['source_policy_method_runner_contract_dae_equivalent']}`."
        ),
        (
            "- Planar-lift rows/metric rows/source-policy rows: "
            f"`{available_blocks['absolute_coordinate_planar_lift_probe_rows']}/"
            f"{available_blocks['absolute_coordinate_planar_lift_probe_metric_rows']}/"
            f"{available_blocks['absolute_coordinate_planar_lift_probe_source_policy_rows_completed']}`."
        ),
        (
            "- Runner-equivalence preflight closed/open/source rows: "
            f"`{available_blocks['preflight_closed_preconditions']}/"
            f"{available_blocks['preflight_open_blockers']}/"
            f"{available_blocks['preflight_source_policy_rows_closed']}`."
        ),
        (
            "- Gauss6/FullVA candidate smoke/source-policy runner/source-policy rows: "
            f"`{available_blocks['gauss6_fullva_source_pendulum_candidate_smoke_implemented']}/"
            f"{available_blocks['gauss6_fullva_absolute_coordinate_source_policy_runner_implemented']}/"
            f"{available_blocks['gauss6_fullva_candidate_source_policy_rows_completed']}`."
        ),
        (
            "- Gauss6/FullVA DAE candidate contract rows/source rows/equivalent/FullVA-equivalent: "
            f"`{available_blocks['gauss6_fullva_dae_candidate_contract_rows']}/"
            f"{available_blocks['gauss6_fullva_dae_candidate_contract_source_policy_rows_completed']}/"
            f"{available_blocks['gauss6_fullva_dae_candidate_contract_equivalent']}/"
            f"{available_blocks['gauss6_fullva_dae_candidate_contract_fullva_equivalent']}`."
        ),
        (
            "- Source-policy Gauss6/FullVA DAE runner contract symbol/present/implemented: "
            f"`{available_blocks['source_policy_gauss6_fullva_dae_runner_contract_symbol_present']}/"
            f"{available_blocks['source_policy_gauss6_fullva_absolute_coordinate_dae_runner_contract_present']}/"
            f"{available_blocks['source_policy_gauss6_fullva_absolute_coordinate_dae_runner_implemented']}`."
        ),
        (
            "- Source-policy Gauss6/FullVA DAE runner contract rows/source rows/equivalent/FullVA-equivalent/monolithic: "
            f"`{available_blocks['source_policy_gauss6_fullva_absolute_coordinate_dae_runner_rows']}/"
            f"{available_blocks['source_policy_gauss6_fullva_absolute_coordinate_dae_runner_source_policy_rows_completed']}/"
            f"{available_blocks['source_policy_gauss6_fullva_absolute_coordinate_dae_runner_equivalent']}/"
            f"{available_blocks['source_policy_gauss6_fullva_absolute_coordinate_dae_runner_fullva_equivalent']}/"
            f"{available_blocks['source_policy_gauss6_fullva_absolute_coordinate_dae_runner_monolithic']}`."
        ),
        (
            "- Full T=10 absolute DAE-lift metric/step/source rows/monolithic/equivalent: "
            f"`{available_blocks['full_T10_absolute_dae_lift_metric_rows']}/"
            f"{available_blocks['full_T10_absolute_dae_lift_step_residual_rows']}/"
            f"{available_blocks['full_T10_absolute_dae_lift_source_policy_rows_completed']}/"
            f"{available_blocks['full_T10_absolute_dae_lift_monolithic']}/"
            f"{available_blocks['full_T10_absolute_dae_lift_equivalent']}`."
        ),
        (
            "- Full T=10 grid exact/incompatible/full-policy-resolved: "
            f"`{output['grid_policy']['integer_step_compatible_rows']}/"
            f"{output['grid_policy']['integer_step_incompatible_rows']}/"
            f"{output['grid_policy']['source_grid_policy_resolved_for_full_T10']}`."
        ),
        f"- Missing contract blocks: `{output['missing_contract_block_count']}`.",
        f"- Non-heavy missing contract blocks: `{nonheavy_missing}`.",
        f"- Non-heavy blocks dispositioned by demotion: `{nonheavy_dispositioned_by_demotion}`.",
        "- Non-heavy demotion closes source-policy rows: `False`.",
        (
            "- Contract block accounting raw/non-heavy-terminal/effective-execution/source-rows: "
            f"`{contract_block_accounting['raw_open_contract_block_count']}/"
            f"{contract_block_accounting['terminal_nonpromoted_contract_block_count']}/"
            f"{contract_block_accounting['effective_source_policy_execution_contract_block_count']}/"
            f"{contract_block_accounting['source_policy_rows_closed_by_accounting']}`."
        ),
        f"- Effective source-policy execution contract blocks: `{effective_missing_contract_blocks}`.",
        f"- Source-policy execution/integrator missing contract blocks: `{source_policy_execution_missing}`.",
        f"- Source-policy execution/integrator missing block count: `{len(source_policy_execution_missing)}`.",
        (
            "- Candidate-backed non-equivalent runner blocks/count: "
            f"`{[row['id'] for row in candidate_backed_non_equivalent_runner_blocks]}/"
            f"{len(candidate_backed_non_equivalent_runner_blocks)}`."
        ),
        f"- Ready to execute source policy now: `{output['ready_to_execute_source_policy_now']}`.",
        (
            "- Source-policy execution preflight schema/status/opt-in: "
            f"`{source_policy_execution_preflight['schema']}/"
            f"{source_policy_execution_preflight['status']}/"
            f"{source_policy_execution_preflight['explicit_user_opt_in_required']}`."
        ),
        (
            "- Source-policy execution preflight nonheavy/execution/promote/ready: "
            f"`{source_policy_execution_preflight['nonheavy_blocks_dispositioned_by_demotion']}/"
            f"{source_policy_execution_preflight['execution_block_count']}/"
            f"{source_policy_execution_preflight['can_promote_any_tfe_source_policy_row_now']}/"
            f"{source_policy_execution_preflight['ready_to_execute_source_policy_now']}`."
        ),
        (
            "- Source-policy execution preflight required runner contracts: "
            f"`{source_policy_execution_preflight['runner_contracts_required_before_execution']}`."
        ),
        "",
        "## Non-Heavy Blocker Evidence",
        "",
        (
            "- Brown--McPhee encoded/published/source-equivalent/transition-policy/close-now: "
            f"`{output['nonheavy_blocker_evidence']['brown_mcphee']['candidate_formula_encoded']}/"
            f"{output['nonheavy_blocker_evidence']['brown_mcphee']['published_formula_structure_encoded']}/"
            f"{output['nonheavy_blocker_evidence']['brown_mcphee']['source_code_equivalent_law']}/"
            f"{output['nonheavy_blocker_evidence']['brown_mcphee']['transition_velocity_policy_resolved_from_source']}/"
            f"{output['nonheavy_blocker_evidence']['brown_mcphee']['can_close_now']}`."
        ),
        (
            "- Brown--McPhee source-code equivalence certificate status/available/positive/closed-block: "
            f"`{output['nonheavy_blocker_evidence']['brown_mcphee']['certificate_status']}/"
            f"{output['nonheavy_blocker_evidence']['brown_mcphee']['certificate_available']}/"
            f"{output['nonheavy_blocker_evidence']['brown_mcphee']['positive_source_code_equivalence_certified']}/"
            f"{output['nonheavy_blocker_evidence']['brown_mcphee']['negative_certificate_nonheavy_block_closed']}`."
        ),
        (
            "- Brown--McPhee frictional source-policy demotion/allowed-use: "
            f"`{output['nonheavy_blocker_evidence']['brown_mcphee']['frictional_source_policy_rows_demoted']}/"
            f"{output['nonheavy_blocker_evidence']['brown_mcphee']['frictional_source_policy_demotion_allowed_use']}`."
        ),
        (
            "- Algorithm-literal endpoint probe metric/overrun/source rows: "
            f"`{output['nonheavy_blocker_evidence']['endpoint_policy']['endpoint_probe_metric_rows']}/"
            f"{output['nonheavy_blocker_evidence']['endpoint_policy']['endpoint_probe_terminal_overrun_rows']}/"
            f"{output['nonheavy_blocker_evidence']['endpoint_policy']['endpoint_probe_source_policy_rows_completed']}`."
        ),
        (
            "- Algorithm-literal work-precision rows/summary/figure/B4-progress/B4-closure: "
            f"`{output['nonheavy_blocker_evidence']['endpoint_policy']['work_precision_rows']}/"
            f"{output['nonheavy_blocker_evidence']['endpoint_policy']['work_precision_summary_rows']}/"
            f"{output['nonheavy_blocker_evidence']['endpoint_policy']['work_precision_figure_available']}/"
            f"{output['nonheavy_blocker_evidence']['endpoint_policy']['work_precision_b4_progress']}/"
            f"{output['nonheavy_blocker_evidence']['endpoint_policy']['work_precision_b4_closure']}`."
        ),
        (
            "- Endpoint boundary certificate proved/exact/overrun/source rows/full-policy/exact-T-equivalent: "
            f"`{output['nonheavy_blocker_evidence']['endpoint_policy']['literal_overrun_bound_proved']}/"
            f"{output['nonheavy_blocker_evidence']['endpoint_policy']['literal_exact_T_rows']}/"
            f"{output['nonheavy_blocker_evidence']['endpoint_policy']['literal_overrun_rows']}/"
            f"{output['nonheavy_blocker_evidence']['endpoint_policy']['boundary_source_policy_rows_completed']}/"
            f"{output['nonheavy_blocker_evidence']['endpoint_policy']['boundary_full_T10_policy_resolved']}/"
            f"{output['nonheavy_blocker_evidence']['endpoint_policy']['boundary_exact_T_error_sampling_equivalent']}`."
        ),
        (
            "- Full-T10 endpoint policy closure certificate status/available/positive/closed-block: "
            f"`{output['nonheavy_blocker_evidence']['endpoint_policy']['certificate_status']}/"
            f"{output['nonheavy_blocker_evidence']['endpoint_policy']['certificate_available']}/"
            f"{output['nonheavy_blocker_evidence']['endpoint_policy']['positive_full_T10_endpoint_policy_certified']}/"
            f"{output['nonheavy_blocker_evidence']['endpoint_policy']['negative_certificate_nonheavy_block_closed']}`."
        ),
        (
            "- Endpoint-incompatible rows demoted from source-policy row set: "
            f"`{output['nonheavy_blocker_evidence']['endpoint_policy']['endpoint_incompatible_rows_demoted_from_source_policy']}`."
        ),
        (
            "- Endpoint source-equivalent sampling/method-runner: "
            f"`{output['nonheavy_blocker_evidence']['endpoint_policy']['source_policy_exact_T_error_sampling_equivalent']}/"
            f"{output['nonheavy_blocker_evidence']['endpoint_policy']['source_policy_method_runner_equivalent']}`."
        ),
        "",
        "## Non-Heavy Demotion Disposition",
        "",
        (
            "- Brown--McPhee non-heavy disposition/rows-promoted/allowed-use: "
            f"`{nonheavy_dispositions[0]['disposition']}/"
            f"{nonheavy_dispositions[0]['source_policy_rows_promoted']}/"
            f"{nonheavy_dispositions[0]['candidate_evidence_allowed_use']}`."
        ),
        (
            "- Brown--McPhee demotion certificate/positive/closed-block/source rows: "
            f"`{nonheavy_dispositions[0]['certificate_status']}/"
            f"{nonheavy_dispositions[0]['positive_source_code_equivalence_certified']}/"
            f"{nonheavy_dispositions[0]['negative_certificate_nonheavy_block_closed']}/"
            f"{nonheavy_dispositions[0]['source_policy_rows_completed']}`."
        ),
        (
            "- Endpoint non-heavy disposition/rows-demoted/full-policy: "
            f"`{nonheavy_dispositions[1]['disposition']}/"
            f"{nonheavy_dispositions[1]['endpoint_incompatible_rows_demoted_from_source_policy']}/"
            f"{nonheavy_dispositions[1]['source_grid_policy_resolved_for_full_T10']}/"
            f"{nonheavy_dispositions[1]['negative_certificate_nonheavy_block_closed']}`."
        ),
        (
            "- Endpoint demotion exact/overrun rows/exact-T-equivalent/source rows: "
            f"`{nonheavy_dispositions[1]['algorithm_literal_exact_T_row_count']}/"
            f"{nonheavy_dispositions[1]['algorithm_literal_overrun_row_count']}/"
            f"{nonheavy_dispositions[1]['source_policy_exact_T_error_sampling_equivalent']}/"
            f"{nonheavy_dispositions[1]['source_policy_rows_completed']}`."
        ),
        "- These demotions remove the non-heavy rows from source-policy promotion scope but do not close the TFE runner lane.",
        "",
        "## Missing Contract Blocks",
        "",
        "| id | first required artifact | non-heavy resolvable |",
        "|---|---|---:|",
    ]
    for row in missing_blocks:
        lines.append(
            f"| `{row['id']}` | `{row['first_required_artifact']}` | "
            f"`{row['can_resolve_without_heavy_run']}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            output["closure_decision"]["reason"],
            "",
            "No TFE source-policy rows are closed by this audit.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("tfe_dae_runner_contract_gap_audit=written")
    print(f"status={output['status']}")
    print(f"missing_contract_blocks={output['missing_contract_block_count']}")
    print("source_policy_rows_completed=0")


if __name__ == "__main__":
    main()
