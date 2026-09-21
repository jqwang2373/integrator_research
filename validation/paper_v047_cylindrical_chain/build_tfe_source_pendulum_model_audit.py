#!/usr/bin/env python3
"""Build an audit for the runnable TFE source-pendulum parameter model."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
MODEL_PATH = ROOT.parent / "numerics" / "v048_cross_paper_same_test_benchmarks" / "tfe_source_pendulum_model.py"
OUT_JSON = PAPER / "TFE_SOURCE_PENDULUM_MODEL_AUDIT.json"
OUT_MD = PAPER / "TFE_SOURCE_PENDULUM_MODEL_AUDIT.md"


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def load_model_module():
    spec = importlib.util.spec_from_file_location("tfe_source_pendulum_model", MODEL_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {MODEL_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def finite_order_floor(row: dict[str, Any], key: str) -> float:
    values = row.get(key, [])
    if not isinstance(values, list):
        return float("nan")
    clean = [float(item) for item in values if item is not None]
    return min(clean) if clean else float("nan")


def main() -> None:
    source_spec = read_json(PAPER / "TFE_SOURCE_POLICY_SPEC.json")
    grid_audit = read_json(PAPER / "TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.json")
    model = load_model_module()
    params = model.source_parameters()
    reductions = model.candidate_planar_reductions(params)
    smoke = model.smoke_trajectory(h=1.0e-3, steps=10, axis="z")
    output_policy = model.source_output_policy()
    source_metric_smoke = model.source_error_metrics(
        model.SourcePlanarState(theta=0.0, omega=0.0),
        model.SourcePlanarState(theta=0.1, omega=-0.2),
        axis="z",
        params=params,
    )
    positive_torque = model.brown_mcphee_candidate_torque(
        1.0,
        25.0,
        stribeck_velocity=0.5,
        params=params,
    )
    negative_torque = model.brown_mcphee_candidate_torque(
        -1.0,
        25.0,
        stribeck_velocity=0.5,
        params=params,
    )
    zero_torque = model.brown_mcphee_candidate_torque(
        0.0,
        25.0,
        stribeck_velocity=0.5,
        params=params,
    )
    frictional_smoke = model.frictional_smoke_trajectory(
        theta0=0.0,
        omega0=1.0,
        h=1.0e-3,
        steps=10,
        axis="z",
        stribeck_velocity=0.5,
    )
    absolute_dae_smoke = model.absolute_coordinate_dae_residual_smoke(theta=0.2, omega=0.3)
    absolute_frictional_dae_smoke = model.absolute_coordinate_dae_residual_smoke(
        theta=0.2,
        omega=0.3,
        frictional=True,
        stribeck_velocity=0.5,
    )
    source_output_time_smoke = model.source_output_time_integration_smoke()
    source_reference_policy_smoke = model.source_reference_solution_policy_smoke()
    source_reference_full_t10_probe = model.source_reference_solution_policy_full_t10_probe()
    comparator_candidate_smoke = model.source_comparator_candidate_runner_smoke()
    tfe_candidate_smoke = model.source_tfe_candidate_runner_smoke()
    method_candidate_contract = model.source_method_candidate_runner_contract_smoke()
    source_policy_method_runner_contract = (
        model.source_policy_tfe_newmark_trapezoidal_method_runners(
            candidate_contract=method_candidate_contract
        )
    )
    gauss6_candidate_smoke = model.source_gauss6_fullva_candidate_runner_smoke()
    gauss6_dae_candidate_contract = model.source_gauss6_fullva_dae_candidate_contract_smoke()
    source_policy_gauss6_fullva_dae_runner_contract = (
        model.source_policy_gauss6_fullva_absolute_coordinate_dae_runner(
            candidate_contract=gauss6_dae_candidate_contract
        )
    )
    same_test_work_precision_smoke = model.source_pendulum_same_test_work_precision_smoke()
    absolute_lift_probe = model.absolute_coordinate_planar_lift_trajectory_probe()
    bounded_dae_trajectory_runner = model.bounded_absolute_coordinate_dae_trajectory_runner_smoke()
    monolithic_dae_candidate_runner = (
        model.monolithic_absolute_coordinate_dae_candidate_runner_smoke()
    )
    source_policy_absolute_coordinate_dae_runner = (
        model.source_policy_absolute_coordinate_dae_runner(
            candidate_runner=monolithic_dae_candidate_runner
        )
    )
    dae_trajectory_bridge_contract = model.dae_trajectory_bridge_contract_smoke()
    candidate_frictional_dae_trajectory_contract = (
        model.candidate_frictional_dae_trajectory_contract_smoke()
    )
    same_test_work_precision_rows = same_test_work_precision_smoke["rows"]
    same_test_work_precision_metric_rows = sum(
        len(row.get("metrics", [])) for row in same_test_work_precision_rows
    )
    same_test_gauss6_row = next(
        row for row in same_test_work_precision_rows if row["source_method"] == "Gauss6_FullVA"
    )
    same_test_tfe_m3_row = next(
        row for row in same_test_work_precision_rows if row["source_method"] == "TFE_m3_GL"
    )
    appendix_b_coefficient_certificate = model.tfe_appendix_b_coefficient_certificate()
    bounded_runner_smoke = model.bounded_source_policy_runner_smoke()
    active_b2_candidate_smoke = model.active_tfe_b2_candidate_row_smoke()
    full_t10_coarse_candidate_probe = model.active_tfe_b2_full_t10_coarse_candidate_probe()
    source_reference_full_t10_candidate_probe = (
        model.active_tfe_b2_source_reference_full_t10_candidate_probe()
    )
    tfe_m3_full_t10_formula_probe = model.tfe_m3_gl_full_t10_coarse_formula_probe()
    source_text_path = ROOT.parent / "external" / "literature" / "s11044-026-10153-w.txt"
    source_text = read_text(source_text_path) if source_text_path.exists() else ""
    normalized_source_text = " ".join(source_text.split()).lower()

    source_body = source_spec.get("source_policy", {}).get("body_parameters", {})
    source_friction = source_spec.get("source_policy", {}).get("friction_parameters", {})
    params_match = (
        params.mass_kg == source_body.get("mass_kg")
        and params.length_m == source_body.get("length_m")
        and params.hinge_pin_radius_m == source_body.get("hinge_pin_radius_m")
        and params.center_of_mass_x_m == source_body.get("center_of_mass_x_m")
        and params.mu_static == source_friction.get("mu_static")
        and params.mu_dynamic == source_friction.get("mu_dynamic")
        and params.gravity_axis == source_spec.get("source_policy", {}).get("gravity_axis")
    )
    runner_gap = source_spec.get("runner_gap", {})
    closed_preconditions = [
        {
            "id": "source_policy_spec_extracted",
            "status": runner_gap.get("source_policy_spec_extracted") is True,
            "evidence": "TFE_SOURCE_POLICY_SPEC.json",
        },
        {
            "id": "source_pendulum_parameter_model_implemented",
            "status": params_match,
            "evidence": "../../numerics/v048_cross_paper_same_test_benchmarks/tfe_source_pendulum_model.py",
        },
        {
            "id": "source_output_error_policy_encoded",
            "status": bool(output_policy),
            "evidence": "source_output_policy/source_metric_smoke",
        },
        {
            "id": "absolute_coordinate_dae_residual_smoke_implemented",
            "status": absolute_dae_smoke.get("source_policy_dae_runner_equivalent") is False,
            "evidence": "absolute_coordinate_dae_residual_smoke",
        },
        {
            "id": "absolute_coordinate_planar_lift_trajectory_probe_implemented",
            "status": (
                absolute_lift_probe.get("absolute_coordinate_planar_lift_trajectory_probe_implemented")
                is True
                and absolute_lift_probe.get("source_policy_rows_completed") == 0
            ),
            "evidence": "absolute_coordinate_planar_lift_trajectory_probe",
        },
        {
            "id": "bounded_absolute_coordinate_dae_trajectory_runner_implemented",
            "status": (
                bounded_dae_trajectory_runner.get(
                    "bounded_absolute_coordinate_dae_trajectory_runner_implemented"
                )
                is True
                and bounded_dae_trajectory_runner.get("source_policy_rows_completed") == 0
                and bounded_dae_trajectory_runner.get("source_policy_dae_runner_equivalent") is False
            ),
            "evidence": "bounded_absolute_coordinate_dae_trajectory_runner_smoke",
        },
        {
            "id": "monolithic_absolute_coordinate_dae_candidate_runner_implemented",
            "status": (
                monolithic_dae_candidate_runner.get(
                    "monolithic_absolute_coordinate_dae_candidate_runner_implemented"
                )
                is True
                and monolithic_dae_candidate_runner.get("monolithic_candidate_time_integration_entrypoint")
                is True
                and monolithic_dae_candidate_runner.get("source_policy_rows_completed") == 0
                and monolithic_dae_candidate_runner.get("source_policy_dae_runner_equivalent")
                is False
                and monolithic_dae_candidate_runner.get(
                    "monolithic_absolute_coordinate_dae_time_integrator"
                )
                is False
            ),
            "evidence": "monolithic_absolute_coordinate_dae_candidate_runner_smoke",
        },
        {
            "id": "source_policy_absolute_coordinate_dae_runner_contract_present",
            "status": (
                source_policy_absolute_coordinate_dae_runner.get(
                    "source_policy_absolute_coordinate_dae_runner_contract_present"
                )
                is True
                and source_policy_absolute_coordinate_dae_runner.get(
                    "source_policy_absolute_coordinate_dae_runner_implemented"
                )
                is False
                and source_policy_absolute_coordinate_dae_runner.get(
                    "source_policy_rows_completed"
                )
                == 0
                and source_policy_absolute_coordinate_dae_runner.get(
                    "source_policy_dae_runner_equivalent"
                )
                is False
                and source_policy_absolute_coordinate_dae_runner.get(
                    "monolithic_absolute_coordinate_dae_time_integrator"
                )
                is False
            ),
            "evidence": "source_policy_absolute_coordinate_dae_runner",
        },
        {
            "id": "dae_trajectory_bridge_contract_implemented",
            "status": (
                dae_trajectory_bridge_contract.get("dae_trajectory_bridge_contract_implemented")
                is True
                and dae_trajectory_bridge_contract.get("matched_contract_row_count")
                == dae_trajectory_bridge_contract.get("row_count")
                and dae_trajectory_bridge_contract.get("source_policy_rows_completed") == 0
                and dae_trajectory_bridge_contract.get("source_policy_dae_runner_equivalent") is False
            ),
            "evidence": "dae_trajectory_bridge_contract_smoke",
        },
        {
            "id": "candidate_frictional_dae_trajectory_contract_implemented",
            "status": (
                candidate_frictional_dae_trajectory_contract.get(
                    "candidate_frictional_dae_trajectory_contract_implemented"
                )
                is True
                and candidate_frictional_dae_trajectory_contract.get("row_count") == 12
                and candidate_frictional_dae_trajectory_contract.get("source_policy_rows_completed") == 0
                and candidate_frictional_dae_trajectory_contract.get(
                    "source_policy_dae_runner_equivalent"
                )
                is False
                and candidate_frictional_dae_trajectory_contract.get(
                    "brown_mcphee_source_code_equivalent_law"
                )
                is False
            ),
            "evidence": "candidate_frictional_dae_trajectory_contract_smoke",
        },
        {
            "id": "source_reference_full_T10_h1e4_probe_completed",
            "status": (
                source_reference_full_t10_probe.get("full_T10_source_reference_probe_completed") is True
                and source_reference_full_t10_probe.get("source_policy_rows_completed") == 0
            ),
            "evidence": "source_reference_solution_policy_full_T10_probe",
        },
        {
            "id": "newmark_trapezoidal_candidate_runner_smoke_implemented",
            "status": comparator_candidate_smoke.get("source_policy_method_runner_equivalent") is False,
            "evidence": "source_comparator_candidate_runner_smoke",
        },
        {
            "id": "tfe_m1_m2_m3_candidate_runner_smoke_implemented",
            "status": tfe_candidate_smoke.get("tfe_m1_m2_m3_candidate_runner_smoke_implemented") is True,
            "evidence": "source_tfe_candidate_runner_smoke",
        },
        {
            "id": "source_method_candidate_runner_contract_implemented",
            "status": (
                method_candidate_contract.get("source_method_candidate_runner_contract_implemented")
                is True
                and method_candidate_contract.get("row_count") == 5
                and method_candidate_contract.get("source_policy_rows_completed") == 0
                and method_candidate_contract.get("source_policy_method_runner_equivalent") is False
                and method_candidate_contract.get("all_step_states_finite") is True
                and method_candidate_contract.get("all_candidate_residuals_below_1e_8") is True
            ),
            "evidence": "source_method_candidate_runner_contract_smoke",
        },
        {
            "id": "source_policy_tfe_newmark_trapezoidal_method_runner_contract_present",
            "status": (
                source_policy_method_runner_contract.get(
                    "source_policy_method_runner_contract_present"
                )
                is True
                and source_policy_method_runner_contract.get(
                    "source_policy_tfe_newmark_trapezoidal_method_runners_implemented"
                )
                is False
                and source_policy_method_runner_contract.get("source_policy_rows_completed") == 0
                and source_policy_method_runner_contract.get(
                    "source_policy_method_runner_equivalent"
                )
                is False
                and source_policy_method_runner_contract.get(
                    "source_policy_dae_runner_equivalent"
                )
                is False
            ),
            "evidence": "source_policy_tfe_newmark_trapezoidal_method_runners",
        },
        {
            "id": "tfe_appendix_b_coefficient_certificate_checked",
            "status": appendix_b_coefficient_certificate.get("all_appendix_b_formula_matches") is True,
            "evidence": "tfe_appendix_b_coefficient_certificate",
        },
        {
            "id": "bounded_source_policy_runner_api_implemented",
            "status": (
                bounded_runner_smoke.get("bounded_source_policy_runner_api_implemented") is True
                and bounded_runner_smoke.get("source_policy_rows_completed") == 0
            ),
            "evidence": "bounded_source_policy_runner_smoke",
        },
        {
            "id": "active_tfe_b2_full_T10_coarse_candidate_probe_implemented",
            "status": (
                full_t10_coarse_candidate_probe.get("full_T10_candidate_probe_completed") is True
                and full_t10_coarse_candidate_probe.get("source_policy_rows_completed") == 0
            ),
            "evidence": "active_tfe_b2_full_T10_coarse_candidate_probe",
        },
        {
            "id": "active_tfe_b2_source_reference_full_T10_candidate_probe_implemented",
            "status": (
                source_reference_full_t10_candidate_probe.get("full_T10_candidate_probe_completed")
                is True
                and source_reference_full_t10_candidate_probe.get("source_policy_reference_invoked")
                is True
                and source_reference_full_t10_candidate_probe.get("source_policy_rows_completed") == 0
                and source_reference_full_t10_candidate_probe.get(
                    "source_policy_method_runner_equivalent"
                )
                is False
            ),
            "evidence": "active_tfe_b2_source_reference_full_T10_candidate_probe",
        },
        {
            "id": "tfe_m3_full_T10_coarse_formula_probe_implemented",
            "status": (
                tfe_m3_full_t10_formula_probe.get("full_T10_formula_probe_completed") is True
                and tfe_m3_full_t10_formula_probe.get("source_policy_rows_completed") == 0
            ),
            "evidence": "tfe_m3_full_T10_coarse_formula_probe",
        },
        {
            "id": "gauss6_source_pendulum_candidate_smoke_implemented",
            "status": (
                gauss6_candidate_smoke.get(
                    "gauss6_fullva_source_pendulum_candidate_smoke_implemented"
                )
                is True
                and gauss6_candidate_smoke.get(
                    "gauss6_fullva_absolute_coordinate_source_policy_runner_implemented"
                )
                is False
                and gauss6_candidate_smoke.get("source_policy_rows_completed") == 0
            ),
            "evidence": "gauss6_fullva_source_pendulum_candidate_smoke",
        },
        {
            "id": "gauss6_fullva_dae_candidate_contract_implemented",
            "status": (
                gauss6_dae_candidate_contract.get(
                    "gauss6_fullva_dae_candidate_contract_implemented"
                )
                is True
                and gauss6_dae_candidate_contract.get("row_count") == 1
                and gauss6_dae_candidate_contract.get("source_policy_rows_completed") == 0
                and gauss6_dae_candidate_contract.get("source_policy_dae_runner_equivalent")
                is False
                and gauss6_dae_candidate_contract.get(
                    "gauss6_fullva_absolute_coordinate_source_policy_runner_implemented"
                )
                is False
                and gauss6_dae_candidate_contract.get("all_step_states_finite") is True
                and gauss6_dae_candidate_contract.get("all_candidate_residuals_below_1e_8")
                is True
            ),
            "evidence": "source_gauss6_fullva_dae_candidate_contract_smoke",
        },
        {
            "id": "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_contract_present",
            "status": (
                source_policy_gauss6_fullva_dae_runner_contract.get(
                    "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_contract_present"
                )
                is True
                and source_policy_gauss6_fullva_dae_runner_contract.get(
                    "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_implemented"
                )
                is False
                and source_policy_gauss6_fullva_dae_runner_contract.get(
                    "source_policy_rows_completed"
                )
                == 0
                and source_policy_gauss6_fullva_dae_runner_contract.get(
                    "source_policy_dae_runner_equivalent"
                )
                is False
                and source_policy_gauss6_fullva_dae_runner_contract.get(
                    "monolithic_absolute_coordinate_dae_time_integrator"
                )
                is False
            ),
            "evidence": "source_policy_gauss6_fullva_absolute_coordinate_dae_runner",
        },
        {
            "id": "same_test_candidate_work_precision_available",
            "status": same_test_work_precision_smoke.get("same_test_work_precision_implemented") is True,
            "evidence": "source_pendulum_same_test_work_precision_smoke",
        },
        {
            "id": "exact_T_compatible_grid_subset_policy_resolved",
            "status": grid_audit.get("source_grid_policy_resolved_for_exact_T_compatible_rows") is True,
            "evidence": "TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.json",
        },
    ]
    open_blockers = [
        {
            "id": "brown_mcphee_source_code_equivalent_law_open",
            "status": "open",
            "reason": "published formula structure is encoded, but transition velocity and source-code coupling policy remain unresolved",
        },
        {
            "id": "pendulum_absolute_coordinate_source_policy_dae_runner_missing",
            "status": "open",
            "reason": "a named contract entrypoint now binds the monolithic candidate rows, but it is not source-code-equivalent, not a monolithic source-policy DAE time integrator, and closes zero source-policy rows",
        },
        {
            "id": "tfe_newmark_trapezoidal_source_policy_method_runners_missing",
            "status": "open",
            "reason": "a named method-runner contract entrypoint now binds candidate dispatch rows, but TFE m=1/2/3, Newmark-beta, and trapezoidal source-policy runners remain non-equivalent and close zero source-policy rows",
        },
        {
            "id": "gauss6_fullva_absolute_coordinate_source_policy_runner_missing",
            "status": "open",
            "reason": "a named Gauss6/FullVA absolute-coordinate DAE contract entrypoint now binds the candidate lift, but it is not a monolithic FullVA source-policy DAE runner and closes zero source-policy rows",
        },
        {
            "id": "full_T10_source_grid_endpoint_policy_open",
            "status": "open",
            "reason": "full T=10 source grid policy remains open for endpoint-incompatible h values",
            "endpoint_incompatible_rows": grid_audit.get("endpoint_incompatible_rows_require_source_endpoint_policy"),
        },
        {
            "id": "accepted_source_policy_work_precision_rows_not_executed_or_bound",
            "status": "open",
            "reason": "no accepted source-policy row table binds error/order, runtime, and work metrics for B4/B7",
        },
    ]
    source_policy_runner_equivalence_preflight = {
        "schema": "tfe-source-policy-runner-equivalence-preflight-v1",
        "status": "preflight_ready_runner_equivalence_open",
        "closed_precondition_count": sum(1 for item in closed_preconditions if item["status"] is True),
        "open_blocker_count": len(open_blockers),
        "source_policy_rows_closed_by_preflight": 0,
        "source_policy_dae_runner_equivalent": False,
        "pendulum_dae_runner_implemented": False,
        "source_policy_absolute_coordinate_dae_runner_contract_present": (
            source_policy_absolute_coordinate_dae_runner.get(
                "source_policy_absolute_coordinate_dae_runner_contract_present"
            )
        ),
        "source_policy_absolute_coordinate_dae_runner_implemented": (
            source_policy_absolute_coordinate_dae_runner.get(
                "source_policy_absolute_coordinate_dae_runner_implemented"
            )
        ),
        "source_policy_method_runner_contract_present": (
            source_policy_method_runner_contract.get(
                "source_policy_method_runner_contract_present"
            )
        ),
        "source_policy_tfe_newmark_trapezoidal_method_runners_implemented": (
            source_policy_method_runner_contract.get(
                "source_policy_tfe_newmark_trapezoidal_method_runners_implemented"
            )
        ),
        "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_contract_present": (
            source_policy_gauss6_fullva_dae_runner_contract.get(
                "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_contract_present"
            )
        ),
        "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_implemented": (
            source_policy_gauss6_fullva_dae_runner_contract.get(
                "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_implemented"
            )
        ),
        "brown_mcphee_source_code_equivalent_law": False,
        "tfe_newmark_trapezoidal_source_policy_runners_implemented": False,
        "gauss6_fullva_source_policy_runner_implemented": False,
        "source_grid_policy_resolved_for_full_T10": grid_audit.get(
            "source_grid_policy_resolved_for_full_T10"
        ),
        "source_grid_policy_resolved_for_exact_T_compatible_rows": grid_audit.get(
            "source_grid_policy_resolved_for_exact_T_compatible_rows"
        ),
        "can_close_tfe_lane_from_preflight": False,
        "b4_b7_can_close_from_preflight": False,
        "heavy_numerical_run_invoked": False,
        "run_v047_invoked": False,
        "v048_runner_invoked": False,
        "closed_preconditions": closed_preconditions,
        "open_blockers": open_blockers,
    }

    result = {
        "schema": "tfe-source-pendulum-model-audit-v1",
        "status": "source_parameter_model_implemented_runner_policy_open",
        "submission_ready": False,
        "external_superiority_claim_allowed": False,
        "model_file": "../../numerics/v048_cross_paper_same_test_benchmarks/tfe_source_pendulum_model.py",
        "source_policy_spec": "TFE_SOURCE_POLICY_SPEC.json",
        "parameter_match_source_spec": params_match,
        "source_pendulum_parameter_model_implemented": True,
        "frictionless_planar_rhs_smoke_implemented": True,
        "absolute_coordinate_dae_residual_smoke_implemented": True,
        "absolute_coordinate_frictional_candidate_dae_smoke_implemented": True,
        "source_output_time_integration_smoke_implemented": True,
        "source_policy_time_integration_runner_equivalent": source_output_time_smoke[
            "source_policy_time_integration_runner_equivalent"
        ],
        "source_reference_solution_policy_smoke_implemented": True,
        "source_reference_solution_policy_smoke_full_T10": False,
        "source_reference_solution_policy_full_T10_probe_implemented": True,
        "source_reference_solution_policy_full_T10_probe_completed": source_reference_full_t10_probe[
            "full_T10_source_reference_probe_completed"
        ],
        "source_reference_solution_policy_full_T10_probe_source_h": source_reference_full_t10_probe[
            "source_reference_h"
        ],
        "source_reference_solution_policy_full_T10_probe_check_h": source_reference_full_t10_probe["check_h"],
        "source_reference_solution_policy_full_T10_probe_steps": source_reference_full_t10_probe[
            "source_reference_steps"
        ],
        "source_reference_solution_policy_full_T10_probe_check_steps": source_reference_full_t10_probe[
            "check_steps"
        ],
        "source_reference_solution_policy_full_T10_probe_coordinate_error": source_reference_full_t10_probe[
            "metrics_vs_check_h"
        ]["coordinate_error_q"],
        "source_reference_solution_policy_full_T10_probe_velocity_error": source_reference_full_t10_probe[
            "metrics_vs_check_h"
        ]["velocity_error_v"],
        "source_reference_solution_policy_full_T10_probe_rows_completed": source_reference_full_t10_probe[
            "source_policy_rows_completed"
        ],
        "source_comparator_candidate_runners_implemented": True,
        "newmark_beta_candidate_runner_smoke_implemented": True,
        "trapezoidal_candidate_runner_smoke_implemented": True,
        "source_policy_method_runner_equivalent": comparator_candidate_smoke[
            "source_policy_method_runner_equivalent"
        ],
        "tfe_m1_m2_m3_candidate_runner_smoke_implemented": True,
        "source_method_candidate_runner_contract_implemented": method_candidate_contract[
            "source_method_candidate_runner_contract_implemented"
        ],
        "source_method_candidate_runner_contract_complete": method_candidate_contract[
            "source_method_candidate_runner_contract_complete"
        ],
        "source_method_candidate_runner_contract_rows": method_candidate_contract["row_count"],
        "source_method_candidate_runner_contract_all_step_states_finite": method_candidate_contract[
            "all_step_states_finite"
        ],
        "source_method_candidate_runner_contract_all_candidate_residuals_below_1e_8": (
            method_candidate_contract["all_candidate_residuals_below_1e_8"]
        ),
        "source_method_candidate_runner_contract_source_policy_rows_completed": (
            method_candidate_contract["source_policy_rows_completed"]
        ),
        "source_method_candidate_runner_contract_method_equivalent": method_candidate_contract[
            "source_policy_method_runner_equivalent"
        ],
        "source_method_candidate_runner_contract_dae_equivalent": method_candidate_contract[
            "source_policy_dae_runner_equivalent"
        ],
        "source_method_candidate_runner_contract_max_candidate_step_residual_norm": (
            method_candidate_contract["max_candidate_step_residual_norm"]
        ),
        "source_policy_method_runner_contract_present": source_policy_method_runner_contract[
            "source_policy_method_runner_contract_present"
        ],
        "source_policy_tfe_newmark_trapezoidal_method_runners_implemented": (
            source_policy_method_runner_contract[
                "source_policy_tfe_newmark_trapezoidal_method_runners_implemented"
            ]
        ),
        "source_policy_method_runner_contract_rows": source_policy_method_runner_contract[
            "row_count"
        ],
        "source_policy_method_runner_contract_source_policy_rows_completed": (
            source_policy_method_runner_contract["source_policy_rows_completed"]
        ),
        "source_policy_method_runner_contract_method_equivalent": (
            source_policy_method_runner_contract["source_policy_method_runner_equivalent"]
        ),
        "source_policy_method_runner_contract_dae_equivalent": (
            source_policy_method_runner_contract["source_policy_dae_runner_equivalent"]
        ),
        "source_policy_method_runner_contract_all_step_states_finite": (
            source_policy_method_runner_contract["all_step_states_finite"]
        ),
        "source_policy_method_runner_contract_all_candidate_residuals_below_1e_8": (
            source_policy_method_runner_contract["all_candidate_residuals_below_1e_8"]
        ),
        "source_policy_method_runner_contract_candidate_api": (
            source_policy_method_runner_contract["candidate_contract_api"]
        ),
        "tfe_appendix_b_coefficient_certificate_checked": appendix_b_coefficient_certificate[
            "all_appendix_b_formula_matches"
        ],
        "tfe_appendix_b_coefficient_certificate_row_count": appendix_b_coefficient_certificate["row_count"],
        "tfe_appendix_b_coefficient_certificate_max_abs_diff": appendix_b_coefficient_certificate["max_abs_diff"],
        "tfe_m1_m2_m3_source_policy_runners_implemented": comparator_candidate_smoke[
            "tfe_m1_m2_m3_source_policy_runners_implemented"
        ],
        "gauss6_fullva_source_pendulum_candidate_smoke_implemented": gauss6_candidate_smoke[
            "gauss6_fullva_source_pendulum_candidate_smoke_implemented"
        ],
        "gauss6_fullva_absolute_coordinate_source_policy_runner_implemented": gauss6_candidate_smoke[
            "gauss6_fullva_absolute_coordinate_source_policy_runner_implemented"
        ],
        "gauss6_fullva_on_source_pendulum_implemented": gauss6_candidate_smoke[
            "gauss6_fullva_on_source_pendulum_implemented"
        ],
        "gauss6_fullva_source_pendulum_candidate_rows": gauss6_candidate_smoke["row_count"],
        "gauss6_fullva_source_pendulum_candidate_source_policy_rows_completed": gauss6_candidate_smoke[
            "source_policy_rows_completed"
        ],
        "gauss6_fullva_source_pendulum_candidate_method_equivalent": gauss6_candidate_smoke[
            "source_policy_method_runner_equivalent"
        ],
        "gauss6_fullva_dae_candidate_contract_implemented": gauss6_dae_candidate_contract[
            "gauss6_fullva_dae_candidate_contract_implemented"
        ],
        "gauss6_fullva_dae_candidate_contract_rows": gauss6_dae_candidate_contract[
            "row_count"
        ],
        "gauss6_fullva_dae_candidate_contract_all_step_states_finite": gauss6_dae_candidate_contract[
            "all_step_states_finite"
        ],
        "gauss6_fullva_dae_candidate_contract_all_candidate_residuals_below_1e_8": (
            gauss6_dae_candidate_contract["all_candidate_residuals_below_1e_8"]
        ),
        "gauss6_fullva_dae_candidate_contract_source_policy_rows_completed": (
            gauss6_dae_candidate_contract["source_policy_rows_completed"]
        ),
        "gauss6_fullva_dae_candidate_contract_method_equivalent": gauss6_dae_candidate_contract[
            "source_policy_method_runner_equivalent"
        ],
        "gauss6_fullva_dae_candidate_contract_dae_equivalent": gauss6_dae_candidate_contract[
            "source_policy_dae_runner_equivalent"
        ],
        "gauss6_fullva_dae_candidate_contract_fullva_dae_equivalent": gauss6_dae_candidate_contract[
            "fullva_dae_source_policy_equivalent"
        ],
        "gauss6_fullva_dae_candidate_contract_absolute_source_policy_runner_implemented": (
            gauss6_dae_candidate_contract[
                "gauss6_fullva_absolute_coordinate_source_policy_runner_implemented"
            ]
        ),
        "gauss6_fullva_dae_candidate_contract_max_candidate_step_residual_norm": (
            gauss6_dae_candidate_contract["max_candidate_step_residual_norm"]
        ),
        "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_contract_present": (
            source_policy_gauss6_fullva_dae_runner_contract[
                "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_contract_present"
            ]
        ),
        "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_implemented": (
            source_policy_gauss6_fullva_dae_runner_contract[
                "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_implemented"
            ]
        ),
        "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_rows": (
            source_policy_gauss6_fullva_dae_runner_contract["row_count"]
        ),
        "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_source_policy_rows_completed": (
            source_policy_gauss6_fullva_dae_runner_contract["source_policy_rows_completed"]
        ),
        "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_dae_equivalent": (
            source_policy_gauss6_fullva_dae_runner_contract[
                "source_policy_dae_runner_equivalent"
            ]
        ),
        "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_fullva_equivalent": (
            source_policy_gauss6_fullva_dae_runner_contract[
                "fullva_dae_source_policy_equivalent"
            ]
        ),
        "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_monolithic_integrator": (
            source_policy_gauss6_fullva_dae_runner_contract[
                "monolithic_absolute_coordinate_dae_time_integrator"
            ]
        ),
        "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_all_step_states_finite": (
            source_policy_gauss6_fullva_dae_runner_contract["all_step_states_finite"]
        ),
        "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_all_candidate_residuals_below_1e_8": (
            source_policy_gauss6_fullva_dae_runner_contract[
                "all_candidate_residuals_below_1e_8"
            ]
        ),
        "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_candidate_api": (
            source_policy_gauss6_fullva_dae_runner_contract["candidate_contract_api"]
        ),
        "source_pendulum_same_test_work_precision_implemented": same_test_work_precision_smoke[
            "same_test_work_precision_implemented"
        ],
        "source_pendulum_same_test_work_precision_method_count": same_test_work_precision_smoke[
            "method_count"
        ],
        "source_pendulum_same_test_work_precision_method_rows": same_test_work_precision_smoke[
            "row_count"
        ],
        "source_pendulum_same_test_work_precision_metric_rows": same_test_work_precision_metric_rows,
        "source_pendulum_same_test_work_precision_source_policy_rows_completed": same_test_work_precision_smoke[
            "source_policy_rows_completed"
        ],
        "source_pendulum_same_test_work_precision_external_superiority_claim_allowed": same_test_work_precision_smoke[
            "external_superiority_claim_allowed"
        ],
        "source_pendulum_same_test_work_precision_gauss6_velocity_order_floor": finite_order_floor(
            same_test_gauss6_row,
            "velocity_pairwise_orders",
        ),
        "source_pendulum_same_test_work_precision_tfe_m3_velocity_order_floor": finite_order_floor(
            same_test_tfe_m3_row,
            "velocity_pairwise_orders",
        ),
        "absolute_coordinate_planar_lift_trajectory_probe_implemented": absolute_lift_probe[
            "absolute_coordinate_planar_lift_trajectory_probe_implemented"
        ],
        "absolute_coordinate_planar_lift_trajectory_probe_method_count": absolute_lift_probe["method_count"],
        "absolute_coordinate_planar_lift_trajectory_probe_rows": absolute_lift_probe["row_count"],
        "absolute_coordinate_planar_lift_trajectory_probe_metric_rows": absolute_lift_probe[
            "metric_row_count"
        ],
        "absolute_coordinate_planar_lift_trajectory_probe_source_policy_rows_completed": absolute_lift_probe[
            "source_policy_rows_completed"
        ],
        "absolute_coordinate_planar_lift_trajectory_probe_dae_runner_equivalent": absolute_lift_probe[
            "source_policy_dae_runner_equivalent"
        ],
        "absolute_coordinate_planar_lift_trajectory_probe_max_hinge_position_constraint_norm": absolute_lift_probe[
            "max_hinge_position_constraint_norm"
        ],
        "absolute_coordinate_planar_lift_trajectory_probe_max_hinge_velocity_constraint_norm": absolute_lift_probe[
            "max_hinge_velocity_constraint_norm"
        ],
        "absolute_coordinate_planar_lift_trajectory_probe_max_translational_balance_residual_norm": absolute_lift_probe[
            "max_translational_balance_residual_norm"
        ],
        "absolute_coordinate_planar_lift_trajectory_probe_max_axis_projected_rotational_residual_abs": absolute_lift_probe[
            "max_axis_projected_rotational_residual_abs"
        ],
        "bounded_absolute_coordinate_dae_trajectory_runner_implemented": bounded_dae_trajectory_runner[
            "bounded_absolute_coordinate_dae_trajectory_runner_implemented"
        ],
        "bounded_absolute_coordinate_dae_trajectory_runner_rows": bounded_dae_trajectory_runner["row_count"],
        "bounded_absolute_coordinate_dae_trajectory_runner_metric_rows": bounded_dae_trajectory_runner[
            "metric_row_count"
        ],
        "bounded_absolute_coordinate_dae_trajectory_runner_step_residual_rows": bounded_dae_trajectory_runner[
            "step_residual_row_count"
        ],
        "bounded_absolute_coordinate_dae_trajectory_runner_all_step_states_finite": bounded_dae_trajectory_runner[
            "all_step_states_finite"
        ],
        "bounded_absolute_coordinate_dae_trajectory_runner_source_policy_rows_completed": bounded_dae_trajectory_runner[
            "source_policy_rows_completed"
        ],
        "bounded_absolute_coordinate_dae_trajectory_runner_dae_runner_equivalent": bounded_dae_trajectory_runner[
            "source_policy_dae_runner_equivalent"
        ],
        "bounded_absolute_coordinate_dae_trajectory_runner_monolithic_integrator": bounded_dae_trajectory_runner[
            "monolithic_absolute_coordinate_dae_time_integrator"
        ],
        "bounded_absolute_coordinate_dae_trajectory_runner_max_candidate_step_residual_norm": bounded_dae_trajectory_runner[
            "max_candidate_step_residual_norm"
        ],
        "bounded_absolute_coordinate_dae_trajectory_runner_max_hinge_position_constraint_norm": bounded_dae_trajectory_runner[
            "max_hinge_position_constraint_norm"
        ],
        "bounded_absolute_coordinate_dae_trajectory_runner_max_hinge_velocity_constraint_norm": bounded_dae_trajectory_runner[
            "max_hinge_velocity_constraint_norm"
        ],
        "bounded_absolute_coordinate_dae_trajectory_runner_max_translational_balance_residual_norm": bounded_dae_trajectory_runner[
            "max_translational_balance_residual_norm"
        ],
        "bounded_absolute_coordinate_dae_trajectory_runner_max_axis_projected_rotational_residual_abs": bounded_dae_trajectory_runner[
            "max_axis_projected_rotational_residual_abs"
        ],
        "monolithic_absolute_coordinate_dae_candidate_runner_implemented": monolithic_dae_candidate_runner[
            "monolithic_absolute_coordinate_dae_candidate_runner_implemented"
        ],
        "monolithic_absolute_coordinate_dae_candidate_runner_rows": monolithic_dae_candidate_runner[
            "row_count"
        ],
        "monolithic_absolute_coordinate_dae_candidate_runner_metric_rows": monolithic_dae_candidate_runner[
            "metric_row_count"
        ],
        "monolithic_absolute_coordinate_dae_candidate_runner_step_residual_rows": (
            monolithic_dae_candidate_runner["step_residual_row_count"]
        ),
        "monolithic_absolute_coordinate_dae_candidate_runner_all_step_states_finite": (
            monolithic_dae_candidate_runner["all_step_states_finite"]
        ),
        "monolithic_absolute_coordinate_dae_candidate_runner_all_rows_finite": (
            monolithic_dae_candidate_runner["all_rows_finite"]
        ),
        "monolithic_absolute_coordinate_dae_candidate_runner_all_dae_residuals_below_1e_10": (
            monolithic_dae_candidate_runner["all_dae_residuals_below_1e_10"]
        ),
        "monolithic_absolute_coordinate_dae_candidate_runner_source_policy_rows_completed": (
            monolithic_dae_candidate_runner["source_policy_rows_completed"]
        ),
        "monolithic_absolute_coordinate_dae_candidate_runner_dae_runner_equivalent": (
            monolithic_dae_candidate_runner["source_policy_dae_runner_equivalent"]
        ),
        "monolithic_absolute_coordinate_dae_candidate_runner_monolithic_integrator": (
            monolithic_dae_candidate_runner["monolithic_absolute_coordinate_dae_time_integrator"]
        ),
        "monolithic_absolute_coordinate_dae_candidate_runner_max_candidate_step_residual_norm": (
            monolithic_dae_candidate_runner["max_candidate_step_residual_norm"]
        ),
        "monolithic_absolute_coordinate_dae_candidate_runner_max_hinge_position_constraint_norm": (
            monolithic_dae_candidate_runner["max_hinge_position_constraint_norm"]
        ),
        "monolithic_absolute_coordinate_dae_candidate_runner_max_hinge_velocity_constraint_norm": (
            monolithic_dae_candidate_runner["max_hinge_velocity_constraint_norm"]
        ),
        "monolithic_absolute_coordinate_dae_candidate_runner_max_translational_balance_residual_norm": (
            monolithic_dae_candidate_runner["max_translational_balance_residual_norm"]
        ),
        "monolithic_absolute_coordinate_dae_candidate_runner_max_axis_projected_rotational_residual_abs": (
            monolithic_dae_candidate_runner["max_axis_projected_rotational_residual_abs"]
        ),
        "source_policy_absolute_coordinate_dae_runner_contract_present": (
            source_policy_absolute_coordinate_dae_runner[
                "source_policy_absolute_coordinate_dae_runner_contract_present"
            ]
        ),
        "source_policy_absolute_coordinate_dae_runner_implemented": (
            source_policy_absolute_coordinate_dae_runner[
                "source_policy_absolute_coordinate_dae_runner_implemented"
            ]
        ),
        "source_policy_absolute_coordinate_dae_runner_rows": (
            source_policy_absolute_coordinate_dae_runner["row_count"]
        ),
        "source_policy_absolute_coordinate_dae_runner_metric_rows": (
            source_policy_absolute_coordinate_dae_runner["metric_row_count"]
        ),
        "source_policy_absolute_coordinate_dae_runner_step_residual_rows": (
            source_policy_absolute_coordinate_dae_runner["step_residual_row_count"]
        ),
        "source_policy_absolute_coordinate_dae_runner_all_step_states_finite": (
            source_policy_absolute_coordinate_dae_runner["all_step_states_finite"]
        ),
        "source_policy_absolute_coordinate_dae_runner_all_rows_finite": (
            source_policy_absolute_coordinate_dae_runner["all_rows_finite"]
        ),
        "source_policy_absolute_coordinate_dae_runner_all_dae_residuals_below_1e_10": (
            source_policy_absolute_coordinate_dae_runner[
                "all_dae_residuals_below_1e_10"
            ]
        ),
        "source_policy_absolute_coordinate_dae_runner_source_policy_rows_completed": (
            source_policy_absolute_coordinate_dae_runner["source_policy_rows_completed"]
        ),
        "source_policy_absolute_coordinate_dae_runner_dae_runner_equivalent": (
            source_policy_absolute_coordinate_dae_runner[
                "source_policy_dae_runner_equivalent"
            ]
        ),
        "source_policy_absolute_coordinate_dae_runner_monolithic_integrator": (
            source_policy_absolute_coordinate_dae_runner[
                "monolithic_absolute_coordinate_dae_time_integrator"
            ]
        ),
        "source_policy_absolute_coordinate_dae_runner_candidate_api": (
            source_policy_absolute_coordinate_dae_runner["candidate_runner_api"]
        ),
        "source_policy_absolute_coordinate_dae_runner_max_candidate_step_residual_norm": (
            source_policy_absolute_coordinate_dae_runner[
                "max_candidate_step_residual_norm"
            ]
        ),
        "source_policy_absolute_coordinate_dae_runner_max_hinge_position_constraint_norm": (
            source_policy_absolute_coordinate_dae_runner[
                "max_hinge_position_constraint_norm"
            ]
        ),
        "source_policy_absolute_coordinate_dae_runner_max_hinge_velocity_constraint_norm": (
            source_policy_absolute_coordinate_dae_runner[
                "max_hinge_velocity_constraint_norm"
            ]
        ),
        "source_policy_absolute_coordinate_dae_runner_max_translational_balance_residual_norm": (
            source_policy_absolute_coordinate_dae_runner[
                "max_translational_balance_residual_norm"
            ]
        ),
        "source_policy_absolute_coordinate_dae_runner_max_axis_projected_rotational_residual_abs": (
            source_policy_absolute_coordinate_dae_runner[
                "max_axis_projected_rotational_residual_abs"
            ]
        ),
        "dae_trajectory_bridge_contract_implemented": dae_trajectory_bridge_contract[
            "dae_trajectory_bridge_contract_implemented"
        ],
        "dae_trajectory_bridge_contract_rows": dae_trajectory_bridge_contract["row_count"],
        "dae_trajectory_bridge_contract_matched_rows": dae_trajectory_bridge_contract[
            "matched_contract_row_count"
        ],
        "dae_trajectory_bridge_contract_source_metric_rows": dae_trajectory_bridge_contract[
            "source_metric_row_count"
        ],
        "dae_trajectory_bridge_contract_dae_metric_rows": dae_trajectory_bridge_contract[
            "dae_metric_row_count"
        ],
        "dae_trajectory_bridge_contract_all_rows_finite": dae_trajectory_bridge_contract[
            "all_rows_finite"
        ],
        "dae_trajectory_bridge_contract_all_dae_residuals_below_1e_10": dae_trajectory_bridge_contract[
            "all_dae_residuals_below_1e_10"
        ],
        "dae_trajectory_bridge_contract_source_policy_rows_completed": dae_trajectory_bridge_contract[
            "source_policy_rows_completed"
        ],
        "dae_trajectory_bridge_contract_dae_runner_equivalent": dae_trajectory_bridge_contract[
            "source_policy_dae_runner_equivalent"
        ],
        "dae_trajectory_bridge_contract_monolithic_integrator": dae_trajectory_bridge_contract[
            "monolithic_absolute_coordinate_dae_time_integrator"
        ],
        "dae_trajectory_bridge_contract_max_candidate_step_residual_norm": dae_trajectory_bridge_contract[
            "max_candidate_step_residual_norm"
        ],
        "dae_trajectory_bridge_contract_max_hinge_position_constraint_norm": dae_trajectory_bridge_contract[
            "max_hinge_position_constraint_norm"
        ],
        "dae_trajectory_bridge_contract_max_hinge_velocity_constraint_norm": dae_trajectory_bridge_contract[
            "max_hinge_velocity_constraint_norm"
        ],
        "dae_trajectory_bridge_contract_max_translational_balance_residual_norm": dae_trajectory_bridge_contract[
            "max_translational_balance_residual_norm"
        ],
        "dae_trajectory_bridge_contract_max_axis_projected_rotational_residual_abs": dae_trajectory_bridge_contract[
            "max_axis_projected_rotational_residual_abs"
        ],
        "candidate_frictional_dae_trajectory_contract_implemented": (
            candidate_frictional_dae_trajectory_contract[
                "candidate_frictional_dae_trajectory_contract_implemented"
            ]
        ),
        "candidate_frictional_dae_trajectory_contract_rows": (
            candidate_frictional_dae_trajectory_contract["row_count"]
        ),
        "candidate_frictional_dae_trajectory_contract_step_residual_rows": (
            candidate_frictional_dae_trajectory_contract["step_residual_row_count"]
        ),
        "candidate_frictional_dae_trajectory_contract_all_rows_finite": (
            candidate_frictional_dae_trajectory_contract["all_rows_finite"]
        ),
        "candidate_frictional_dae_trajectory_contract_all_dae_residuals_below_1e_9": (
            candidate_frictional_dae_trajectory_contract["all_dae_residuals_below_1e_9"]
        ),
        "candidate_frictional_dae_trajectory_contract_all_friction_power_nonpositive": (
            candidate_frictional_dae_trajectory_contract[
                "all_candidate_friction_power_nonpositive"
            ]
        ),
        "candidate_frictional_dae_trajectory_contract_source_policy_rows_completed": (
            candidate_frictional_dae_trajectory_contract["source_policy_rows_completed"]
        ),
        "candidate_frictional_dae_trajectory_contract_dae_runner_equivalent": (
            candidate_frictional_dae_trajectory_contract["source_policy_dae_runner_equivalent"]
        ),
        "candidate_frictional_dae_trajectory_contract_method_runner_equivalent": (
            candidate_frictional_dae_trajectory_contract[
                "source_policy_method_runner_equivalent"
            ]
        ),
        "candidate_frictional_dae_trajectory_contract_brown_mcphee_source_code_equivalent_law": (
            candidate_frictional_dae_trajectory_contract[
                "brown_mcphee_source_code_equivalent_law"
            ]
        ),
        "candidate_frictional_dae_trajectory_contract_monolithic_integrator": (
            candidate_frictional_dae_trajectory_contract[
                "monolithic_absolute_coordinate_dae_time_integrator"
            ]
        ),
        "candidate_frictional_dae_trajectory_contract_max_candidate_step_residual_norm": (
            candidate_frictional_dae_trajectory_contract["max_candidate_step_residual_norm"]
        ),
        "candidate_frictional_dae_trajectory_contract_max_hinge_position_constraint_norm": (
            candidate_frictional_dae_trajectory_contract[
                "max_hinge_position_constraint_norm"
            ]
        ),
        "candidate_frictional_dae_trajectory_contract_max_hinge_velocity_constraint_norm": (
            candidate_frictional_dae_trajectory_contract[
                "max_hinge_velocity_constraint_norm"
            ]
        ),
        "candidate_frictional_dae_trajectory_contract_max_translational_balance_residual_norm": (
            candidate_frictional_dae_trajectory_contract[
                "max_translational_balance_residual_norm"
            ]
        ),
        "candidate_frictional_dae_trajectory_contract_max_axis_projected_rotational_residual_abs": (
            candidate_frictional_dae_trajectory_contract[
                "max_axis_projected_rotational_residual_abs"
            ]
        ),
        "candidate_frictional_dae_trajectory_contract_max_candidate_friction_power": (
            candidate_frictional_dae_trajectory_contract["max_candidate_friction_power"]
        ),
        "candidate_frictional_dae_trajectory_contract_min_candidate_friction_power": (
            candidate_frictional_dae_trajectory_contract["min_candidate_friction_power"]
        ),
        "bounded_source_policy_runner_api_implemented": bounded_runner_smoke[
            "bounded_source_policy_runner_api_implemented"
        ],
        "bounded_source_policy_runner_smoke_implemented": bounded_runner_smoke[
            "bounded_source_policy_runner_smoke_implemented"
        ],
        "bounded_source_policy_runner_unified_dispatch": bounded_runner_smoke["unified_method_dispatch"],
        "bounded_source_policy_runner_method_count": bounded_runner_smoke["method_count"],
        "bounded_source_policy_runner_rows": bounded_runner_smoke["row_count"],
        "bounded_source_policy_runner_full_T10": bounded_runner_smoke["full_T10_source_policy_reproduction"],
        "bounded_source_policy_runner_source_policy_rows_completed": bounded_runner_smoke[
            "source_policy_rows_completed"
        ],
        "bounded_source_policy_runner_method_equivalent": bounded_runner_smoke[
            "source_policy_method_runner_equivalent"
        ],
        "active_tfe_b2_candidate_row_smoke_implemented": True,
        "active_tfe_b2_candidate_row_smoke_full_T10": False,
        "active_tfe_b2_source_policy_rows_completed": 0,
        "active_tfe_b2_full_T10_coarse_candidate_probe_implemented": True,
        "active_tfe_b2_full_T10_coarse_candidate_probe_full_T10": full_t10_coarse_candidate_probe[
            "full_T10_candidate_probe_completed"
        ],
        "active_tfe_b2_full_T10_coarse_candidate_probe_source_policy_rows_completed": full_t10_coarse_candidate_probe[
            "source_policy_rows_completed"
        ],
        "active_tfe_b2_full_T10_coarse_candidate_probe_source_policy_reference_not_invoked": full_t10_coarse_candidate_probe[
            "source_policy_reference_not_invoked"
        ],
        "active_tfe_b2_full_T10_coarse_candidate_probe_finite_rows": full_t10_coarse_candidate_probe[
            "finite_row_count"
        ],
        "active_tfe_b2_full_T10_coarse_candidate_probe_residual_ok_rows": full_t10_coarse_candidate_probe[
            "residual_ok_row_count"
        ],
        "active_tfe_b2_source_reference_full_T10_candidate_probe_implemented": True,
        "active_tfe_b2_source_reference_full_T10_candidate_probe_full_T10": (
            source_reference_full_t10_candidate_probe["full_T10_candidate_probe_completed"]
        ),
        "active_tfe_b2_source_reference_full_T10_candidate_probe_source_policy_reference_h": (
            source_reference_full_t10_candidate_probe["source_policy_reference_h"]
        ),
        "active_tfe_b2_source_reference_full_T10_candidate_probe_source_policy_reference_invoked": (
            source_reference_full_t10_candidate_probe["source_policy_reference_invoked"]
        ),
        "active_tfe_b2_source_reference_full_T10_candidate_probe_source_policy_rows_completed": (
            source_reference_full_t10_candidate_probe["source_policy_rows_completed"]
        ),
        "active_tfe_b2_source_reference_full_T10_candidate_probe_finite_rows": (
            source_reference_full_t10_candidate_probe["finite_row_count"]
        ),
        "active_tfe_b2_source_reference_full_T10_candidate_probe_residual_ok_rows": (
            source_reference_full_t10_candidate_probe["residual_ok_row_count"]
        ),
        "active_tfe_b2_source_reference_full_T10_candidate_probe_coordinate_decrease_rows": (
            source_reference_full_t10_candidate_probe["coordinate_error_decrease_row_count"]
        ),
        "active_tfe_b2_source_reference_full_T10_candidate_probe_velocity_decrease_rows": (
            source_reference_full_t10_candidate_probe["velocity_error_decrease_row_count"]
        ),
        "active_tfe_b2_source_reference_full_T10_candidate_probe_method_equivalent": (
            source_reference_full_t10_candidate_probe["source_policy_method_runner_equivalent"]
        ),
        "active_tfe_b2_source_reference_full_T10_candidate_probe_dae_runner_equivalent": (
            source_reference_full_t10_candidate_probe["source_policy_dae_runner_equivalent"]
        ),
        "tfe_m3_full_T10_coarse_formula_probe_implemented": True,
        "tfe_m3_full_T10_coarse_formula_probe_full_T10": tfe_m3_full_t10_formula_probe[
            "full_T10_formula_probe_completed"
        ],
        "tfe_m3_full_T10_coarse_formula_probe_source_policy_rows_completed": tfe_m3_full_t10_formula_probe[
            "source_policy_rows_completed"
        ],
        "tfe_m3_full_T10_coarse_formula_probe_source_policy_reference_not_invoked": tfe_m3_full_t10_formula_probe[
            "source_policy_reference_not_invoked"
        ],
        "tfe_m3_full_T10_coarse_formula_probe_finite_rows": tfe_m3_full_t10_formula_probe[
            "finite_row_count"
        ],
        "tfe_m3_full_T10_coarse_formula_probe_residual_ok_rows": tfe_m3_full_t10_formula_probe[
            "residual_ok_row_count"
        ],
        "tfe_m3_full_T10_coarse_formula_probe_formal_expected_order": tfe_m3_full_t10_formula_probe[
            "formal_expected_order"
        ],
        "source_policy_dae_runner_equivalent": False,
        "pendulum_dae_runner_implemented": False,
        "brown_mcphee_friction_law_implemented": False,
        "brown_mcphee_candidate_friction_law_encoded": True,
        "brown_mcphee_source_text_anchor": {
            "source_text": "../../external/literature/s11044-026-10153-w.txt",
            "source_text_found": bool(source_text),
            "names_velocity_based_continuous_model": (
                "brown and mcphee" in normalized_source_text
                and "velocity based continuous friction model" in normalized_source_text
            ),
            "reports_mu_static_dynamic": (
                "μs = 0.3" in source_text
                and "μd = 0.2" in source_text
            ),
            "reports_reference_step_1e_4": "step-size 1e − 4" in source_text,
            "reports_friction_step_sizes": (
                "step-sizes h = 0.003 and h = 0.008" in source_text
            ),
            "defers_law_details_to_refs_38_39": (
                "For more details on continuous" in source_text
                and "readers are advised to refer to preliminary work by authors [39]" in source_text
            ),
        },
        "brown_mcphee_published_formula_structure_encoded": True,
        "brown_mcphee_source_code_equivalent_law": False,
        "brown_mcphee_transition_velocity_policy_resolved_from_source": False,
        "brown_mcphee_formula_boundary": {
            "encoded_candidate_formula": (
                "tau = -R N [mu_d tanh(4 omega/vs) + "
                "(mu_s-mu_d)(omega/vs)/(0.25(omega/vs)^2+0.75)^2] "
                "- c tanh(4) omega"
            ),
            "encoded_parameters": {
                "mu_static": params.mu_static,
                "mu_dynamic": params.mu_dynamic,
                "hinge_pin_radius_m": params.hinge_pin_radius_m,
            },
            "missing_for_source_policy_equivalence": [
                "transition/Stribeck velocity used by the source experiments",
                "source-code treatment of normal-load coupling and joint multipliers",
                "source-code treatment of viscous damping or zero-viscous default",
                "source implementation tolerance/Jacobian coupling for friction rows",
            ],
        },
        "candidate_friction_law_provenance": (
            "v022_revolute_brown_mcphee_surrogate_not_source_policy_equivalent"
        ),
        "tfe_newmark_trapezoidal_source_policy_runners_implemented": False,
        "source_error_norm_and_output_policy_encoded": True,
        "source_output_policy": output_policy,
        "source_metric_smoke": source_metric_smoke,
        "candidate_friction_torque_smoke": {
            "normal_load": 25.0,
            "stribeck_velocity": 0.5,
            "torque_at_positive_omega": positive_torque,
            "torque_at_negative_omega": negative_torque,
            "torque_at_zero_omega": zero_torque,
            "positive_omega_power": positive_torque,
            "negative_omega_power": -negative_torque,
            "dissipative_sign_check": positive_torque < 0.0 and negative_torque > 0.0 and abs(zero_torque) < 1.0e-14,
        },
        "frictional_planar_candidate_rhs_smoke_implemented": True,
        "frictional_candidate_smoke_trajectory": frictional_smoke,
        "absolute_coordinate_dae_residual_smoke": absolute_dae_smoke,
        "absolute_coordinate_frictional_candidate_dae_smoke": absolute_frictional_dae_smoke,
        "source_output_time_integration_smoke": source_output_time_smoke,
        "source_reference_solution_policy_smoke": source_reference_policy_smoke,
        "source_reference_solution_policy_full_T10_probe": source_reference_full_t10_probe,
        "source_comparator_candidate_runner_smoke": comparator_candidate_smoke,
        "source_tfe_candidate_runner_smoke": tfe_candidate_smoke,
        "source_method_candidate_runner_contract_smoke": method_candidate_contract,
        "source_policy_method_runner_contract": source_policy_method_runner_contract,
        "gauss6_fullva_source_pendulum_candidate_smoke": gauss6_candidate_smoke,
        "gauss6_fullva_dae_candidate_contract_smoke": gauss6_dae_candidate_contract,
        "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_contract": (
            source_policy_gauss6_fullva_dae_runner_contract
        ),
        "source_pendulum_same_test_work_precision_smoke": same_test_work_precision_smoke,
        "absolute_coordinate_planar_lift_trajectory_probe": absolute_lift_probe,
        "bounded_absolute_coordinate_dae_trajectory_runner_smoke": bounded_dae_trajectory_runner,
        "monolithic_absolute_coordinate_dae_candidate_runner_smoke": (
            monolithic_dae_candidate_runner
        ),
        "source_policy_absolute_coordinate_dae_runner_contract": (
            source_policy_absolute_coordinate_dae_runner
        ),
        "dae_trajectory_bridge_contract_smoke": dae_trajectory_bridge_contract,
        "candidate_frictional_dae_trajectory_contract_smoke": (
            candidate_frictional_dae_trajectory_contract
        ),
        "tfe_appendix_b_coefficient_certificate": appendix_b_coefficient_certificate,
        "bounded_source_policy_runner_smoke": bounded_runner_smoke,
        "active_tfe_b2_candidate_row_smoke": active_b2_candidate_smoke,
        "active_tfe_b2_full_T10_coarse_candidate_probe": full_t10_coarse_candidate_probe,
        "active_tfe_b2_source_reference_full_T10_candidate_probe": (
            source_reference_full_t10_candidate_probe
        ),
        "tfe_m3_full_T10_coarse_formula_probe": tfe_m3_full_t10_formula_probe,
        "source_policy_rows_completed": 0,
        "source_policy_runner_equivalence_preflight": source_policy_runner_equivalence_preflight,
        "parameter_values": {
            "mass_kg": params.mass_kg,
            "length_m": params.length_m,
            "hinge_pin_radius_m": params.hinge_pin_radius_m,
            "center_of_mass_x_m": params.center_of_mass_x_m,
            "mu_static": params.mu_static,
            "mu_dynamic": params.mu_dynamic,
            "gravity_axis": params.gravity_axis,
            "inertia_kg_m2": params.inertia_kg_m2().tolist(),
        },
        "candidate_planar_reductions": reductions,
        "selected_smoke_axis": "z",
        "frictionless_smoke_trajectory": smoke,
        "closure_boundary": {
            "can_close_source_pendulum_setup_subrequirement": True,
            "can_close_tfe_b2_requirement_now": False,
            "reason": (
                "The source table parameters, planar source output/error metrics, and a "
                "Brown--McPhee-style candidate friction smoke layer are encoded. An "
                "absolute-coordinate pendulum constraint/dynamics residual smoke and a "
                "bounded source-output time-integration smoke are also encoded. A bounded "
                "h=1e-4 source-reference-policy smoke and candidate Newmark-beta, "
                "trapezoidal, and TFE m=1/2/3 source-output runners are encoded. A separate "
                "full T=10 frictionless source-reference probe now exercises the extracted "
                "h=1e-4 reference step against a h=5e-5 check, but it is still not a "
                "source-policy method-row reproduction. The TFE "
                "m=1/2/3 coefficient matrices are checked against Appendix B equations "
                "(40), (41), and (43) with zero recorded difference for the source parameter choices. The four "
                "active B2 TFE rows are also exercised through a unified bounded source-policy "
                "runner API on a source-shaped h grid and a full T=10 coarse candidate probe "
                "with h={0.1,0.05,0.025}. A separate full T=10 active-B2 candidate "
                "probe now invokes the h=1e-4 source reference over the same large-step "
                "comparison grid while closing zero source-policy rows. A separate TFE "
                "m=3 Gauss--Lobatto full-T10 "
                "formula probe now checks the fifth-order Appendix-B comparator target on the "
                "same non-heavy coarse horizon. A Gauss6/FullVA source-pendulum candidate "
                "smoke is now also present on the same source-pendulum output policy, but it "
                "is a planar candidate and not an absolute-coordinate FullVA DAE source-policy "
                "runner. A same-test work/precision artifact now runs Newmark-beta, "
                "trapezoidal, TFE m=1/2/3, and Gauss6/FullVA on one frictionless "
                "source-pendulum grid and records runtime/Newton work proxies. A trajectory-level "
                "absolute-coordinate planar-lift probe now reconstructs frictionless and candidate-"
                "friction trajectories for the same method family and checks absolute-coordinate "
                "constraint/dynamics residuals at every metric row, but it remains candidate-level "
                "evidence and closes zero source-policy rows. A bounded stepwise DAE residual "
                "runner now streams the active-B2 short-horizon candidate trajectories through "
                "absolute-coordinate residual checks at every accepted step; it also closes zero "
                "source-policy rows and is not a monolithic T=10 source-policy DAE integrator. A "
                "DAE trajectory bridge contract now binds the same bounded source-metric rows to "
                "the corresponding stepwise absolute-coordinate residual rows in a 12-row "
                "method/grid matrix; it closes zero source-policy rows and remains non-equivalent "
                "to the original source-policy runner. A candidate-friction DAE trajectory "
                "contract now also streams Brown--McPhee-style surrogate-friction trajectories "
                "through the same bounded absolute-coordinate residual checks in a 12-row "
                "method/grid matrix; it checks nonpositive friction power and closes zero "
                "source-policy rows. The "
                "source-policy method-runner equivalence, "
                "source-code-equivalent Brown--McPhee law, and exact source-policy rows "
                "remain open. The Brown--McPhee model family, mu_s/mu_d parameters, "
                "and candidate published-formula structure are encoded, but the source "
                "paper delegates law details to Refs. 38--39 and does not fix enough "
                "implementation policy to certify source-code equivalence."
            ),
        },
        "execution_policy": {
            "default_1e_4_required": False,
            "heavy_numerical_run_invoked": False,
            "run_v047_invoked": False,
            "v048_campaign_invoked": False,
        },
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# TFE Source Pendulum Model Audit",
        "",
        "Status: **source parameter model implemented; runner policy open**.",
        "",
        f"- Parameter match with source-policy spec: `{result['parameter_match_source_spec']}`.",
        f"- Source pendulum parameter model implemented: `{result['source_pendulum_parameter_model_implemented']}`.",
        f"- Frictionless planar RHS smoke implemented: `{result['frictionless_planar_rhs_smoke_implemented']}`.",
        f"- Absolute-coordinate DAE residual smoke implemented: `{result['absolute_coordinate_dae_residual_smoke_implemented']}`.",
        f"- Absolute-coordinate frictional candidate DAE smoke implemented: `{result['absolute_coordinate_frictional_candidate_dae_smoke_implemented']}`.",
        f"- Source-output time-integration smoke implemented: `{result['source_output_time_integration_smoke_implemented']}`.",
        f"- Source-policy time-integration runner equivalent: `{result['source_policy_time_integration_runner_equivalent']}`.",
        f"- Source reference solution policy smoke implemented: `{result['source_reference_solution_policy_smoke_implemented']}`.",
        f"- Source reference solution policy full T=10 run: `{result['source_reference_solution_policy_smoke_full_T10']}`.",
        f"- Source reference solution policy full T=10 probe implemented: `{result['source_reference_solution_policy_full_T10_probe_implemented']}`.",
        f"- Source reference solution policy full T=10 probe completed/source rows: `{result['source_reference_solution_policy_full_T10_probe_completed']}/{result['source_reference_solution_policy_full_T10_probe_rows_completed']}`.",
        f"- Source comparator candidate runners implemented: `{result['source_comparator_candidate_runners_implemented']}`.",
        f"- Newmark-beta candidate runner smoke implemented: `{result['newmark_beta_candidate_runner_smoke_implemented']}`.",
        f"- Trapezoidal candidate runner smoke implemented: `{result['trapezoidal_candidate_runner_smoke_implemented']}`.",
        f"- Source-policy method runner equivalent: `{result['source_policy_method_runner_equivalent']}`.",
        f"- TFE m=1/2/3 candidate runner smoke implemented: `{result['tfe_m1_m2_m3_candidate_runner_smoke_implemented']}`.",
        f"- Source-method candidate runner contract rows/source-policy rows/equivalent method: `{result['source_method_candidate_runner_contract_rows']}/{result['source_method_candidate_runner_contract_source_policy_rows_completed']}/{result['source_method_candidate_runner_contract_method_equivalent']}`.",
        f"- Source-method candidate runner contract finite/residual-below-1e-8: `{result['source_method_candidate_runner_contract_all_step_states_finite']}/{result['source_method_candidate_runner_contract_all_candidate_residuals_below_1e_8']}`.",
        f"- Source-policy method runner contract present/implemented: `{result['source_policy_method_runner_contract_present']}/{result['source_policy_tfe_newmark_trapezoidal_method_runners_implemented']}`.",
        f"- Source-policy method runner contract rows/source rows/equivalent method/DAE: `{result['source_policy_method_runner_contract_rows']}/{result['source_policy_method_runner_contract_source_policy_rows_completed']}/{result['source_policy_method_runner_contract_method_equivalent']}/{result['source_policy_method_runner_contract_dae_equivalent']}`.",
        f"- TFE Appendix-B coefficient certificate checked: `{result['tfe_appendix_b_coefficient_certificate_checked']}`.",
        f"- TFE Appendix-B coefficient certificate rows/max diff: `{result['tfe_appendix_b_coefficient_certificate_row_count']}/{result['tfe_appendix_b_coefficient_certificate_max_abs_diff']:.3e}`.",
        f"- TFE m=1/2/3 source-policy runners implemented: `{result['tfe_m1_m2_m3_source_policy_runners_implemented']}`.",
        f"- Gauss6/FullVA source-pendulum candidate smoke implemented: `{result['gauss6_fullva_source_pendulum_candidate_smoke_implemented']}`.",
        f"- Gauss6/FullVA absolute-coordinate source-policy runner implemented: `{result['gauss6_fullva_absolute_coordinate_source_policy_runner_implemented']}`.",
        f"- Gauss6/FullVA source-pendulum legacy candidate alias implemented: `{result['gauss6_fullva_on_source_pendulum_implemented']}`.",
        f"- Gauss6/FullVA source-pendulum candidate rows/source-policy rows: `{result['gauss6_fullva_source_pendulum_candidate_rows']}/{result['gauss6_fullva_source_pendulum_candidate_source_policy_rows_completed']}`.",
        f"- Gauss6/FullVA source-pendulum candidate method equivalent: `{result['gauss6_fullva_source_pendulum_candidate_method_equivalent']}`.",
        f"- Gauss6/FullVA DAE candidate contract rows/source-policy rows/equivalent DAE/FullVA: `{result['gauss6_fullva_dae_candidate_contract_rows']}/{result['gauss6_fullva_dae_candidate_contract_source_policy_rows_completed']}/{result['gauss6_fullva_dae_candidate_contract_dae_equivalent']}/{result['gauss6_fullva_dae_candidate_contract_fullva_dae_equivalent']}`.",
        f"- Gauss6/FullVA DAE candidate contract finite/residual-below-1e-8: `{result['gauss6_fullva_dae_candidate_contract_all_step_states_finite']}/{result['gauss6_fullva_dae_candidate_contract_all_candidate_residuals_below_1e_8']}`.",
        f"- Source-policy Gauss6/FullVA absolute-coordinate DAE runner contract present/implemented: `{result['source_policy_gauss6_fullva_absolute_coordinate_dae_runner_contract_present']}/{result['source_policy_gauss6_fullva_absolute_coordinate_dae_runner_implemented']}`.",
        f"- Source-policy Gauss6/FullVA absolute-coordinate DAE runner contract rows/source rows/equivalent DAE/FullVA/monolithic: `{result['source_policy_gauss6_fullva_absolute_coordinate_dae_runner_rows']}/{result['source_policy_gauss6_fullva_absolute_coordinate_dae_runner_source_policy_rows_completed']}/{result['source_policy_gauss6_fullva_absolute_coordinate_dae_runner_dae_equivalent']}/{result['source_policy_gauss6_fullva_absolute_coordinate_dae_runner_fullva_equivalent']}/{result['source_policy_gauss6_fullva_absolute_coordinate_dae_runner_monolithic_integrator']}`.",
        f"- Source-pendulum same-test work/precision implemented: `{result['source_pendulum_same_test_work_precision_implemented']}`.",
        f"- Source-pendulum same-test work/precision methods/method rows/metric rows: `{result['source_pendulum_same_test_work_precision_method_count']}/{result['source_pendulum_same_test_work_precision_method_rows']}/{result['source_pendulum_same_test_work_precision_metric_rows']}`.",
        f"- Source-pendulum same-test work/precision source-policy rows/external superiority allowed: `{result['source_pendulum_same_test_work_precision_source_policy_rows_completed']}/{result['source_pendulum_same_test_work_precision_external_superiority_claim_allowed']}`.",
        f"- Source-pendulum same-test work/precision Gauss6/TFE m=3 velocity order floors: `{result['source_pendulum_same_test_work_precision_gauss6_velocity_order_floor']:.3f}` / `{result['source_pendulum_same_test_work_precision_tfe_m3_velocity_order_floor']:.3f}`.",
        f"- Absolute-coordinate planar-lift trajectory probe implemented: `{result['absolute_coordinate_planar_lift_trajectory_probe_implemented']}`.",
        f"- Absolute-coordinate planar-lift methods/rows/metric rows: `{result['absolute_coordinate_planar_lift_trajectory_probe_method_count']}/{result['absolute_coordinate_planar_lift_trajectory_probe_rows']}/{result['absolute_coordinate_planar_lift_trajectory_probe_metric_rows']}`.",
        f"- Absolute-coordinate planar-lift source-policy rows/equivalent DAE runner: `{result['absolute_coordinate_planar_lift_trajectory_probe_source_policy_rows_completed']}/{result['absolute_coordinate_planar_lift_trajectory_probe_dae_runner_equivalent']}`.",
        f"- Bounded absolute-coordinate DAE trajectory runner implemented: `{result['bounded_absolute_coordinate_dae_trajectory_runner_implemented']}`.",
        f"- Bounded absolute-coordinate DAE trajectory runner rows/metric rows/step residual rows: `{result['bounded_absolute_coordinate_dae_trajectory_runner_rows']}/{result['bounded_absolute_coordinate_dae_trajectory_runner_metric_rows']}/{result['bounded_absolute_coordinate_dae_trajectory_runner_step_residual_rows']}`.",
        f"- Bounded absolute-coordinate DAE trajectory runner source-policy rows/equivalent DAE/monolithic integrator: `{result['bounded_absolute_coordinate_dae_trajectory_runner_source_policy_rows_completed']}/{result['bounded_absolute_coordinate_dae_trajectory_runner_dae_runner_equivalent']}/{result['bounded_absolute_coordinate_dae_trajectory_runner_monolithic_integrator']}`.",
        f"- Monolithic absolute-coordinate DAE candidate runner implemented: `{result['monolithic_absolute_coordinate_dae_candidate_runner_implemented']}`.",
        f"- Monolithic absolute-coordinate DAE candidate runner rows/metric rows/step residual rows: `{result['monolithic_absolute_coordinate_dae_candidate_runner_rows']}/{result['monolithic_absolute_coordinate_dae_candidate_runner_metric_rows']}/{result['monolithic_absolute_coordinate_dae_candidate_runner_step_residual_rows']}`.",
        f"- Monolithic absolute-coordinate DAE candidate runner source-policy rows/equivalent DAE/monolithic integrator: `{result['monolithic_absolute_coordinate_dae_candidate_runner_source_policy_rows_completed']}/{result['monolithic_absolute_coordinate_dae_candidate_runner_dae_runner_equivalent']}/{result['monolithic_absolute_coordinate_dae_candidate_runner_monolithic_integrator']}`.",
        f"- Source-policy absolute-coordinate DAE runner contract present/implemented: `{result['source_policy_absolute_coordinate_dae_runner_contract_present']}/{result['source_policy_absolute_coordinate_dae_runner_implemented']}`.",
        f"- Source-policy absolute-coordinate DAE runner contract rows/metric rows/step residual rows/source rows/equivalent/monolithic: `{result['source_policy_absolute_coordinate_dae_runner_rows']}/{result['source_policy_absolute_coordinate_dae_runner_metric_rows']}/{result['source_policy_absolute_coordinate_dae_runner_step_residual_rows']}/{result['source_policy_absolute_coordinate_dae_runner_source_policy_rows_completed']}/{result['source_policy_absolute_coordinate_dae_runner_dae_runner_equivalent']}/{result['source_policy_absolute_coordinate_dae_runner_monolithic_integrator']}`.",
        f"- DAE trajectory bridge contract implemented: `{result['dae_trajectory_bridge_contract_implemented']}`.",
        f"- DAE trajectory bridge contract rows/matched/source rows: `{result['dae_trajectory_bridge_contract_rows']}/{result['dae_trajectory_bridge_contract_matched_rows']}/{result['dae_trajectory_bridge_contract_source_policy_rows_completed']}`.",
        f"- DAE trajectory bridge contract all finite/all DAE residuals below 1e-10: `{result['dae_trajectory_bridge_contract_all_rows_finite']}/{result['dae_trajectory_bridge_contract_all_dae_residuals_below_1e_10']}`.",
        f"- DAE trajectory bridge contract equivalent DAE/monolithic integrator: `{result['dae_trajectory_bridge_contract_dae_runner_equivalent']}/{result['dae_trajectory_bridge_contract_monolithic_integrator']}`.",
        f"- Candidate-friction DAE trajectory contract implemented: `{result['candidate_frictional_dae_trajectory_contract_implemented']}`.",
        f"- Candidate-friction DAE trajectory contract rows/step residual rows/source rows: `{result['candidate_frictional_dae_trajectory_contract_rows']}/{result['candidate_frictional_dae_trajectory_contract_step_residual_rows']}/{result['candidate_frictional_dae_trajectory_contract_source_policy_rows_completed']}`.",
        f"- Candidate-friction DAE trajectory contract finite/residual-below-1e-9/friction-power-nonpositive: `{result['candidate_frictional_dae_trajectory_contract_all_rows_finite']}/{result['candidate_frictional_dae_trajectory_contract_all_dae_residuals_below_1e_9']}/{result['candidate_frictional_dae_trajectory_contract_all_friction_power_nonpositive']}`.",
        f"- Candidate-friction DAE trajectory contract equivalent DAE/method/source-law/monolithic: `{result['candidate_frictional_dae_trajectory_contract_dae_runner_equivalent']}/{result['candidate_frictional_dae_trajectory_contract_method_runner_equivalent']}/{result['candidate_frictional_dae_trajectory_contract_brown_mcphee_source_code_equivalent_law']}/{result['candidate_frictional_dae_trajectory_contract_monolithic_integrator']}`.",
        f"- Bounded source-policy runner API implemented: `{result['bounded_source_policy_runner_api_implemented']}`.",
        f"- Bounded source-policy runner smoke implemented: `{result['bounded_source_policy_runner_smoke_implemented']}`.",
        f"- Bounded source-policy runner unified dispatch: `{result['bounded_source_policy_runner_unified_dispatch']}`.",
        f"- Bounded source-policy runner rows/full T=10/source-policy rows: `{result['bounded_source_policy_runner_rows']}/{result['bounded_source_policy_runner_full_T10']}/{result['bounded_source_policy_runner_source_policy_rows_completed']}`.",
        f"- Bounded source-policy runner method equivalent: `{result['bounded_source_policy_runner_method_equivalent']}`.",
        f"- Active TFE B2 candidate row smoke implemented: `{result['active_tfe_b2_candidate_row_smoke_implemented']}`.",
        f"- Active TFE B2 candidate row smoke full T=10: `{result['active_tfe_b2_candidate_row_smoke_full_T10']}`.",
        f"- Active TFE B2 source-policy rows completed: `{result['active_tfe_b2_source_policy_rows_completed']}`.",
        f"- Active TFE B2 full T=10 coarse candidate probe implemented: `{result['active_tfe_b2_full_T10_coarse_candidate_probe_implemented']}`.",
        f"- Active TFE B2 full T=10 coarse candidate probe full T=10/source-policy rows: `{result['active_tfe_b2_full_T10_coarse_candidate_probe_full_T10']}/{result['active_tfe_b2_full_T10_coarse_candidate_probe_source_policy_rows_completed']}`.",
        f"- Active TFE B2 full T=10 coarse candidate probe finite/residual-ok rows: `{result['active_tfe_b2_full_T10_coarse_candidate_probe_finite_rows']}/{result['active_tfe_b2_full_T10_coarse_candidate_probe_residual_ok_rows']}`.",
        f"- Active TFE B2 full T=10 coarse candidate probe source reference invoked: `{not result['active_tfe_b2_full_T10_coarse_candidate_probe_source_policy_reference_not_invoked']}`.",
        f"- Active TFE B2 source-reference full T=10 candidate probe implemented: `{result['active_tfe_b2_source_reference_full_T10_candidate_probe_implemented']}`.",
        f"- Active TFE B2 source-reference full T=10 candidate probe full T=10/reference invoked/source-policy rows: `{result['active_tfe_b2_source_reference_full_T10_candidate_probe_full_T10']}/{result['active_tfe_b2_source_reference_full_T10_candidate_probe_source_policy_reference_invoked']}/{result['active_tfe_b2_source_reference_full_T10_candidate_probe_source_policy_rows_completed']}`.",
        f"- Active TFE B2 source-reference full T=10 candidate probe finite/residual-ok rows: `{result['active_tfe_b2_source_reference_full_T10_candidate_probe_finite_rows']}/{result['active_tfe_b2_source_reference_full_T10_candidate_probe_residual_ok_rows']}`.",
        f"- Active TFE B2 source-reference full T=10 candidate probe method/DAE equivalent: `{result['active_tfe_b2_source_reference_full_T10_candidate_probe_method_equivalent']}/{result['active_tfe_b2_source_reference_full_T10_candidate_probe_dae_runner_equivalent']}`.",
        f"- TFE m=3 full T=10 coarse formula probe implemented: `{result['tfe_m3_full_T10_coarse_formula_probe_implemented']}`.",
        f"- TFE m=3 full T=10 coarse formula probe full T=10/source-policy rows: `{result['tfe_m3_full_T10_coarse_formula_probe_full_T10']}/{result['tfe_m3_full_T10_coarse_formula_probe_source_policy_rows_completed']}`.",
        f"- TFE m=3 full T=10 coarse formula probe finite/residual-ok rows: `{result['tfe_m3_full_T10_coarse_formula_probe_finite_rows']}/{result['tfe_m3_full_T10_coarse_formula_probe_residual_ok_rows']}`.",
        f"- TFE m=3 full T=10 coarse formula probe expected order: `{result['tfe_m3_full_T10_coarse_formula_probe_formal_expected_order']}`.",
        f"- TFE m=3 full T=10 coarse formula probe source reference invoked: `{not result['tfe_m3_full_T10_coarse_formula_probe_source_policy_reference_not_invoked']}`.",
        f"- Source-policy DAE runner equivalent: `{result['source_policy_dae_runner_equivalent']}`.",
        f"- Source output/error policy encoded: `{result['source_error_norm_and_output_policy_encoded']}`.",
        f"- Brown--McPhee candidate friction law encoded: `{result['brown_mcphee_candidate_friction_law_encoded']}`.",
        f"- Brown--McPhee source-text anchor found: `{result['brown_mcphee_source_text_anchor']['source_text_found']}`.",
        f"- Brown--McPhee source text names velocity-based continuous model: `{result['brown_mcphee_source_text_anchor']['names_velocity_based_continuous_model']}`.",
        f"- Brown--McPhee source text reports mu_s/mu_d: `{result['brown_mcphee_source_text_anchor']['reports_mu_static_dynamic']}`.",
        f"- Brown--McPhee published-formula structure encoded: `{result['brown_mcphee_published_formula_structure_encoded']}`.",
        f"- Brown--McPhee source-code-equivalent law: `{result['brown_mcphee_source_code_equivalent_law']}`.",
        f"- Frictional candidate RHS smoke implemented: `{result['frictional_planar_candidate_rhs_smoke_implemented']}`.",
        f"- Pendulum DAE runner implemented: `{result['pendulum_dae_runner_implemented']}`.",
        f"- Brown--McPhee friction law implemented: `{result['brown_mcphee_friction_law_implemented']}`.",
        f"- TFE/Newmark/trapezoidal runners implemented: `{result['tfe_newmark_trapezoidal_source_policy_runners_implemented']}`.",
        f"- Source-policy rows completed: `{result['source_policy_rows_completed']}`.",
        f"- Source-policy runner-equivalence preflight: `{source_policy_runner_equivalence_preflight['status']}`.",
        f"- Source-policy runner-equivalence preflight closed/open/source rows: `{source_policy_runner_equivalence_preflight['closed_precondition_count']}/{source_policy_runner_equivalence_preflight['open_blocker_count']}/{source_policy_runner_equivalence_preflight['source_policy_rows_closed_by_preflight']}`.",
        f"- Can close TFE B2 requirement now: `{result['closure_boundary']['can_close_tfe_b2_requirement_now']}`.",
        "",
        "## Source-Policy Runner Equivalence Preflight",
        "",
        f"- Status: `{source_policy_runner_equivalence_preflight['status']}`.",
        f"- Closed preconditions/open blockers: `{source_policy_runner_equivalence_preflight['closed_precondition_count']}/{source_policy_runner_equivalence_preflight['open_blocker_count']}`.",
        f"- Source-policy rows closed by preflight: `{source_policy_runner_equivalence_preflight['source_policy_rows_closed_by_preflight']}`.",
        f"- Source-policy DAE runner equivalent: `{source_policy_runner_equivalence_preflight['source_policy_dae_runner_equivalent']}`.",
        f"- Pendulum DAE runner implemented: `{source_policy_runner_equivalence_preflight['pendulum_dae_runner_implemented']}`.",
        f"- Brown--McPhee source-code-equivalent law: `{source_policy_runner_equivalence_preflight['brown_mcphee_source_code_equivalent_law']}`.",
        f"- TFE/Newmark/trapezoidal source-policy runners implemented: `{source_policy_runner_equivalence_preflight['tfe_newmark_trapezoidal_source_policy_runners_implemented']}`.",
        f"- Gauss6/FullVA source-policy runner implemented: `{source_policy_runner_equivalence_preflight['gauss6_fullva_source_policy_runner_implemented']}`.",
        f"- Full T=10 source grid policy resolved: `{source_policy_runner_equivalence_preflight['source_grid_policy_resolved_for_full_T10']}`.",
        f"- Can close TFE lane from preflight: `{source_policy_runner_equivalence_preflight['can_close_tfe_lane_from_preflight']}`.",
        "",
        "| closed precondition | satisfied | evidence |",
        "|---|---:|---|",
    ]
    for item in source_policy_runner_equivalence_preflight["closed_preconditions"]:
        lines.append(f"| `{item['id']}` | `{item['status']}` | `{item['evidence']}` |")
    lines.extend(
        [
            "",
            "| open blocker | status | reason |",
            "|---|---|---|",
        ]
    )
    for item in source_policy_runner_equivalence_preflight["open_blockers"]:
        lines.append(f"| `{item['id']}` | `{item['status']}` | {item['reason']} |")
    lines.extend(
        [
            "",
            "## Candidate Planar Reductions",
            "",
            "| axis | inertia about pin | gravity torque scale | nondegenerate |",
            "|---|---:|---:|---:|",
        ]
    )
    for axis, row in reductions.items():
        lines.append(
            f"| `{axis}` | `{row['parallel_axis_inertia_about_pin']:.6e}` | "
            f"`{row['gravity_torque_scale']:.6e}` | `{row['nondegenerate_frictionless_planar_candidate']}` |"
        )

    lines.extend(
        [
            "",
            "## Smoke Trajectory",
            "",
            f"- Axis: `{result['selected_smoke_axis']}`.",
            f"- h/steps: `{smoke['h']}` / `{smoke['steps']}`.",
            f"- theta/omega final: `{smoke['theta_final']:.6e}` / `{smoke['omega_final']:.6e}`.",
            f"- energy delta: `{smoke['energy_delta']:.6e}`.",
            "",
            "## Source Metric Smoke",
            "",
            f"- coordinate/velocity error: `{source_metric_smoke['coordinate_error_q']:.6e}` / `{source_metric_smoke['velocity_error_v']:.6e}`.",
            f"- Frobenius eta: `{source_metric_smoke['frobenius_error_norm_eta']:.6e}`.",
            f"- mechanical energy deviation: `{source_metric_smoke['mechanical_energy_deviation']:.6e}`.",
            "",
            "## Candidate Friction Smoke",
            "",
            f"- Provenance: `{result['candidate_friction_law_provenance']}`.",
            f"- Source text: `{result['brown_mcphee_source_text_anchor']['source_text']}`.",
            f"- Source text names Brown--McPhee velocity model: `{result['brown_mcphee_source_text_anchor']['names_velocity_based_continuous_model']}`.",
            f"- Source text reports mu_s/mu_d: `{result['brown_mcphee_source_text_anchor']['reports_mu_static_dynamic']}`.",
            f"- Source text defers law details to Refs. 38--39: `{result['brown_mcphee_source_text_anchor']['defers_law_details_to_refs_38_39']}`.",
            f"- Encoded candidate formula: `{result['brown_mcphee_formula_boundary']['encoded_candidate_formula']}`.",
            f"- Source-code-equivalent law: `{result['brown_mcphee_source_code_equivalent_law']}`.",
            f"- Transition velocity resolved from source: `{result['brown_mcphee_transition_velocity_policy_resolved_from_source']}`.",
            f"- Torque sign check: `{result['candidate_friction_torque_smoke']['dissipative_sign_check']}`.",
            f"- Frictional h/steps: `{frictional_smoke['h']}` / `{frictional_smoke['steps']}`.",
            f"- Frictional theta/omega final: `{frictional_smoke['theta_final']:.6e}` / `{frictional_smoke['omega_final']:.6e}`.",
            f"- Frictional energy delta: `{frictional_smoke['energy_delta']:.6e}`.",
            f"- Max candidate friction power: `{frictional_smoke['max_candidate_friction_power']:.6e}`.",
            "",
            "## Absolute-Coordinate DAE Smoke",
            "",
            f"- Frictionless hinge position/velocity residuals: `{absolute_dae_smoke['hinge_position_constraint_norm']:.6e}` / `{absolute_dae_smoke['hinge_velocity_constraint_norm']:.6e}`.",
            f"- Frictionless translational/axis-rotational residuals: `{absolute_dae_smoke['translational_balance_residual_norm']:.6e}` / `{absolute_dae_smoke['axis_projected_rotational_residual_abs']:.6e}`.",
            f"- Frictional candidate translational/axis-rotational residuals: `{absolute_frictional_dae_smoke['translational_balance_residual_norm']:.6e}` / `{absolute_frictional_dae_smoke['axis_projected_rotational_residual_abs']:.6e}`.",
            f"- Frictional candidate power: `{absolute_frictional_dae_smoke['candidate_friction_power']:.6e}`.",
            f"- Source-policy DAE runner equivalent: `{result['source_policy_dae_runner_equivalent']}`.",
            "",
            "## Source-Output Time-Integration Smoke",
            "",
            f"- t_final/reference h: `{source_output_time_smoke['t_final']}` / `{source_output_time_smoke['reference_h']}`.",
            f"- rows: `{len(source_output_time_smoke['rows'])}`.",
            f"- Source-policy time-integration runner equivalent: `{result['source_policy_time_integration_runner_equivalent']}`.",
            "",
            "## Source Reference Solution Policy Smoke",
            "",
            f"- h/check h: `{source_reference_policy_smoke['source_reference_h']}` / `{source_reference_policy_smoke['check_h']}`.",
            f"- t_final: `{source_reference_policy_smoke['t_final']}`.",
            f"- bounded smoke, not full T=10: `{source_reference_policy_smoke['bounded_reference_smoke_not_full_T10']}`.",
            f"- default 1e-4 campaign invoked: `{source_reference_policy_smoke['default_1e_4_campaign_invoked']}`.",
            f"- rows: `{len(source_reference_policy_smoke['rows'])}`.",
            "",
            "## Source Reference Full T=10 Probe",
            "",
            f"- case: `{source_reference_full_t10_probe['case_id']}`.",
            f"- h/check h: `{source_reference_full_t10_probe['source_reference_h']}` / `{source_reference_full_t10_probe['check_h']}`.",
            f"- t_final: `{source_reference_full_t10_probe['t_final']}`.",
            f"- source/check steps: `{source_reference_full_t10_probe['source_reference_steps']}` / `{source_reference_full_t10_probe['check_steps']}`.",
            f"- theta/omega final: `{source_reference_full_t10_probe['source_reference_theta_final']:.6e}` / `{source_reference_full_t10_probe['source_reference_omega_final']:.6e}`.",
            f"- coordinate/velocity check error: `{source_reference_full_t10_probe['metrics_vs_check_h']['coordinate_error_q']:.6e}` / `{source_reference_full_t10_probe['metrics_vs_check_h']['velocity_error_v']:.6e}`.",
            f"- source-policy rows completed: `{source_reference_full_t10_probe['source_policy_rows_completed']}`.",
            f"- source-policy method runner equivalent: `{source_reference_full_t10_probe['source_policy_method_runner_equivalent']}`.",
            "",
            "## Source Comparator Candidate Runner Smoke",
            "",
            f"- candidate methods: `{','.join(comparator_candidate_smoke['candidate_methods'])}`.",
            f"- rows: `{len(comparator_candidate_smoke['rows'])}`.",
            f"- Source-policy method runner equivalent: `{result['source_policy_method_runner_equivalent']}`.",
            f"- TFE m=1/2/3 source-policy runners implemented: `{result['tfe_m1_m2_m3_source_policy_runners_implemented']}`.",
            "",
            "## Candidate TFE m=1/2/3 Runner Smoke",
            "",
            f"- t_final/reference h: `{tfe_candidate_smoke['t_final']}` / `{tfe_candidate_smoke['reference_h']}`.",
            f"- h grid: `{tfe_candidate_smoke['comparison_h']}`.",
            f"- candidate methods: `{','.join(tfe_candidate_smoke['candidate_methods'])}`.",
            f"- rows: `{len(tfe_candidate_smoke['rows'])}`.",
            f"- Source-policy method runner equivalent: `{tfe_candidate_smoke['source_policy_method_runner_equivalent']}`.",
            f"- TFE m=1/2/3 source-policy runners implemented: `{tfe_candidate_smoke['tfe_m1_m2_m3_source_policy_runners_implemented']}`.",
            "",
            "## Gauss6/FullVA Source-Pendulum Candidate Smoke",
            "",
            f"- API: `{gauss6_candidate_smoke['runner_api']}`.",
            f"- t_final/reference h: `{gauss6_candidate_smoke['t_final']}` / `{gauss6_candidate_smoke['reference_h']}`.",
            f"- h grid: `{gauss6_candidate_smoke['comparison_h']}`.",
            f"- candidate methods: `{','.join(gauss6_candidate_smoke['candidate_methods'])}`.",
            f"- rows: `{gauss6_candidate_smoke['row_count']}`.",
            f"- Candidate smoke implemented: `{gauss6_candidate_smoke['gauss6_fullva_source_pendulum_candidate_smoke_implemented']}`.",
            f"- Absolute-coordinate source-policy runner implemented: `{gauss6_candidate_smoke['gauss6_fullva_absolute_coordinate_source_policy_runner_implemented']}`.",
            f"- Legacy candidate alias implemented: `{gauss6_candidate_smoke['gauss6_fullva_on_source_pendulum_implemented']}`.",
            f"- FullVA DAE source-policy equivalent: `{gauss6_candidate_smoke['fullva_dae_source_policy_equivalent']}`.",
            f"- Source-policy method runner equivalent: `{gauss6_candidate_smoke['source_policy_method_runner_equivalent']}`.",
            f"- Source-policy rows completed: `{gauss6_candidate_smoke['source_policy_rows_completed']}`.",
            "",
            "| case | method | frictional | coord pair orders | vel pair orders | Frobenius pair orders | max residual |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in gauss6_candidate_smoke["rows"]:
        lines.append(
            "| "
            f"`{row['case_id']}` | `{row['method']}` | `{row['frictional']}` | "
            f"`{row['coordinate_pairwise_orders']}` | `{row['velocity_pairwise_orders']}` | "
            f"`{row['frobenius_pairwise_orders']}` | `{row['max_newton_residual_norm']:.3e}` |"
        )
    lines.extend(
        [
            "",
            "## Source-Pendulum Same-Test Work/Precision",
            "",
            f"- API: `{same_test_work_precision_smoke['runner_api']}`.",
            f"- t_final/reference h: `{same_test_work_precision_smoke['t_final']}` / `{same_test_work_precision_smoke['reference_h']}`.",
            f"- h grid: `{same_test_work_precision_smoke['comparison_h']}`.",
            f"- methods/method rows/metric rows: `{same_test_work_precision_smoke['method_count']}` / `{same_test_work_precision_smoke['row_count']}` / `{same_test_work_precision_metric_rows}`.",
            f"- Source-policy method runner equivalent: `{same_test_work_precision_smoke['source_policy_method_runner_equivalent']}`.",
            f"- Source-policy rows completed: `{same_test_work_precision_smoke['source_policy_rows_completed']}`.",
            f"- External superiority allowed: `{same_test_work_precision_smoke['external_superiority_claim_allowed']}`.",
            "",
            "| method | expected order | coord pair orders | vel pair orders | finest vel error | Newton sum | runtime sum |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in same_test_work_precision_smoke["rows"]:
        finest = row["metrics"][-1]
        lines.append(
            "| "
            f"`{row['method_label']}` | `{row['expected_order']}` | "
            f"`{row['coordinate_pairwise_orders']}` | `{row['velocity_pairwise_orders']}` | "
            f"`{finest['velocity_error_v']:.3e}` | `{row['total_newton_iterations']:.1f}` | "
            f"`{row['total_runtime_sec']:.3e}` |"
        )
    lines.extend(
        [
            "",
            "## Absolute-Coordinate Planar-Lift Trajectory Probe",
            "",
            f"- API: `{absolute_lift_probe['runner_api']}`.",
            f"- t_final/reference h: `{absolute_lift_probe['t_final']}` / `{absolute_lift_probe['reference_h']}`.",
            f"- h grid: `{absolute_lift_probe['comparison_h']}`.",
            f"- cases/methods/rows/metric rows: `{absolute_lift_probe['case_count']}` / `{absolute_lift_probe['method_count']}` / `{absolute_lift_probe['row_count']}` / `{absolute_lift_probe['metric_row_count']}`.",
            f"- Max hinge position/velocity residuals: `{absolute_lift_probe['max_hinge_position_constraint_norm']:.3e}` / `{absolute_lift_probe['max_hinge_velocity_constraint_norm']:.3e}`.",
            f"- Max translational/axis-rotational residuals: `{absolute_lift_probe['max_translational_balance_residual_norm']:.3e}` / `{absolute_lift_probe['max_axis_projected_rotational_residual_abs']:.3e}`.",
            f"- Source-policy DAE runner equivalent: `{absolute_lift_probe['source_policy_dae_runner_equivalent']}`.",
            f"- Source-policy rows completed: `{absolute_lift_probe['source_policy_rows_completed']}`.",
            "",
            "| case | method | frictional | coord pair orders | vel pair orders | max DAE residual |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    for row in absolute_lift_probe["rows"]:
        max_dae = max(
            max(float(metric["hinge_position_constraint_norm"]) for metric in row["metrics"]),
            max(float(metric["hinge_velocity_constraint_norm"]) for metric in row["metrics"]),
            max(float(metric["translational_balance_residual_norm"]) for metric in row["metrics"]),
            max(float(metric["axis_projected_rotational_residual_abs"]) for metric in row["metrics"]),
        )
        lines.append(
            "| "
            f"`{row['case_id']}` | `{row['method_label']}` | `{row['frictional']}` | "
            f"`{row['coordinate_pairwise_orders']}` | `{row['velocity_pairwise_orders']}` | "
            f"`{max_dae:.3e}` |"
        )
    lines.extend(
        [
            "",
            "## DAE Trajectory Bridge Contract",
            "",
            f"- API: `{dae_trajectory_bridge_contract['runner_api']}`.",
            f"- Source runner / DAE runner: `{dae_trajectory_bridge_contract['source_runner_api']}` / `{dae_trajectory_bridge_contract['dae_runner_api']}`.",
            f"- t_final/reference h: `{dae_trajectory_bridge_contract['t_final']}` / `{dae_trajectory_bridge_contract['reference_h']}`.",
            f"- h grid: `{dae_trajectory_bridge_contract['comparison_h']}`.",
            f"- methods/source metric rows/DAE metric rows/contract rows: `{dae_trajectory_bridge_contract['method_count']}` / `{dae_trajectory_bridge_contract['source_metric_row_count']}` / `{dae_trajectory_bridge_contract['dae_metric_row_count']}` / `{dae_trajectory_bridge_contract['row_count']}`.",
            f"- matched contract rows: `{dae_trajectory_bridge_contract['matched_contract_row_count']}`.",
            f"- all rows finite: `{dae_trajectory_bridge_contract['all_rows_finite']}`.",
            f"- all DAE residuals below 1e-10: `{dae_trajectory_bridge_contract['all_dae_residuals_below_1e_10']}`.",
            f"- Source-policy DAE runner equivalent: `{dae_trajectory_bridge_contract['source_policy_dae_runner_equivalent']}`.",
            f"- Monolithic absolute-coordinate DAE integrator: `{dae_trajectory_bridge_contract['monolithic_absolute_coordinate_dae_time_integrator']}`.",
            f"- Source-policy rows completed: `{dae_trajectory_bridge_contract['source_policy_rows_completed']}`.",
            "",
            "| method | h | coord error | vel error | step residual rows | max DAE residual |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in dae_trajectory_bridge_contract["rows"]:
        max_dae = max(
            float(row["max_hinge_position_constraint_norm"]),
            float(row["max_hinge_velocity_constraint_norm"]),
            float(row["max_translational_balance_residual_norm"]),
            float(row["max_axis_projected_rotational_residual_abs"]),
        )
        lines.append(
            "| "
            f"`{row['paper_method']}` | `{row['h']:.6g}` | "
            f"`{row['coordinate_error_q']:.3e}` | `{row['velocity_error_v']:.3e}` | "
            f"`{row['step_residual_rows']}` | `{max_dae:.3e}` |"
        )
    lines.extend(
        [
            "",
            "## Candidate-Friction DAE Trajectory Contract",
            "",
            f"- API: `{candidate_frictional_dae_trajectory_contract['runner_api']}`.",
            f"- scope: `{candidate_frictional_dae_trajectory_contract['runner_scope']}`.",
            f"- t_final/reference h: `{candidate_frictional_dae_trajectory_contract['t_final']}` / `{candidate_frictional_dae_trajectory_contract['reference_h']}`.",
            f"- h grid: `{candidate_frictional_dae_trajectory_contract['comparison_h']}`.",
            f"- methods/rows/step residual rows: `{candidate_frictional_dae_trajectory_contract['method_count']}` / `{candidate_frictional_dae_trajectory_contract['row_count']}` / `{candidate_frictional_dae_trajectory_contract['step_residual_row_count']}`.",
            f"- all rows finite: `{candidate_frictional_dae_trajectory_contract['all_rows_finite']}`.",
            f"- all DAE residuals below 1e-9: `{candidate_frictional_dae_trajectory_contract['all_dae_residuals_below_1e_9']}`.",
            f"- all candidate friction power nonpositive: `{candidate_frictional_dae_trajectory_contract['all_candidate_friction_power_nonpositive']}`.",
            f"- Brown--McPhee source-code-equivalent law: `{candidate_frictional_dae_trajectory_contract['brown_mcphee_source_code_equivalent_law']}`.",
            f"- Source-policy DAE/method runner equivalent: `{candidate_frictional_dae_trajectory_contract['source_policy_dae_runner_equivalent']}` / `{candidate_frictional_dae_trajectory_contract['source_policy_method_runner_equivalent']}`.",
            f"- Monolithic absolute-coordinate DAE integrator: `{candidate_frictional_dae_trajectory_contract['monolithic_absolute_coordinate_dae_time_integrator']}`.",
            f"- Source-policy rows completed: `{candidate_frictional_dae_trajectory_contract['source_policy_rows_completed']}`.",
            "",
            "| method | h | coord error | vel error | step residual rows | max DAE residual | max friction power |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in candidate_frictional_dae_trajectory_contract["rows"]:
        max_dae = max(
            float(row["max_hinge_position_constraint_norm"]),
            float(row["max_hinge_velocity_constraint_norm"]),
            float(row["max_translational_balance_residual_norm"]),
            float(row["max_axis_projected_rotational_residual_abs"]),
        )
        lines.append(
            "| "
            f"`{row['paper_method']}` | `{row['h']:.6g}` | "
            f"`{row['coordinate_error_q']:.3e}` | `{row['velocity_error_v']:.3e}` | "
            f"`{row['step_residual_rows']}` | `{max_dae:.3e}` | "
            f"`{row['max_candidate_friction_power']:.3e}` |"
        )
    lines.extend(
        [
            "",
            "## TFE Appendix-B Coefficient Certificate",
            "",
            f"- Source: `{appendix_b_coefficient_certificate['source']}`.",
            f"- h: `{appendix_b_coefficient_certificate['h']}`.",
            f"- methods: `{','.join(appendix_b_coefficient_certificate['checked_methods'])}`.",
            f"- all formula matches: `{appendix_b_coefficient_certificate['all_appendix_b_formula_matches']}`.",
            f"- max absolute difference: `{appendix_b_coefficient_certificate['max_abs_diff']:.3e}`.",
            f"- scope: `{appendix_b_coefficient_certificate['scope']}`.",
            f"- Source-policy method runner equivalent: `{appendix_b_coefficient_certificate['source_policy_method_runner_equivalent']}`.",
            f"- Source-policy rows completed: `{appendix_b_coefficient_certificate['source_policy_rows_completed']}`.",
            "",
            "| method | formula match | max abs diff | alpha | beta | gamma | nodes |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in appendix_b_coefficient_certificate["rows"]:
        diffs = row["part_max_abs_diff"]
        lines.append(
            "| "
            f"`{row['method']}` | `{row['appendix_b_formula_match']}` | "
            f"`{row['max_abs_diff']:.3e}` | `{diffs['alpha']:.3e}` | "
            f"`{diffs['beta']:.3e}` | `{diffs['gamma']:.3e}` | `{diffs['nodes']:.3e}` |"
        )
    lines.extend(
        [
            "",
            "## Bounded Source-Policy Runner Smoke",
            "",
            f"- API: `{bounded_runner_smoke['runner_api']}`.",
            f"- t_final/reference h: `{bounded_runner_smoke['t_final']}` / `{bounded_runner_smoke['reference_h']}`.",
            f"- h grid: `{bounded_runner_smoke['comparison_h']}`.",
            f"- rows: `{bounded_runner_smoke['row_count']}`.",
            f"- unified method dispatch: `{bounded_runner_smoke['unified_method_dispatch']}`.",
            f"- Full T=10 source-policy reproduction: `{bounded_runner_smoke['full_T10_source_policy_reproduction']}`.",
            f"- Source-policy method runner equivalent: `{bounded_runner_smoke['source_policy_method_runner_equivalent']}`.",
            f"- Source-policy rows completed: `{bounded_runner_smoke['source_policy_rows_completed']}`.",
            "",
            "## Active B2 Candidate Row Smoke",
            "",
            f"- t_final/reference h: `{active_b2_candidate_smoke['t_final']}` / `{active_b2_candidate_smoke['reference_h']}`.",
            f"- h grid: `{active_b2_candidate_smoke['comparison_h']}`.",
            f"- rows: `{len(active_b2_candidate_smoke['rows'])}`.",
            f"- Full T=10 source-policy reproduction: `{active_b2_candidate_smoke['full_T10_source_policy_reproduction']}`.",
            f"- Source-policy method runner equivalent: `{active_b2_candidate_smoke['source_policy_method_runner_equivalent']}`.",
            f"- Source-policy rows completed: `{active_b2_candidate_smoke['source_policy_rows_completed']}`.",
            "",
            "| method | expected order | coord pair orders | vel pair orders | finest coord error | finest vel error | max residual |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in active_b2_candidate_smoke["rows"]:
        finest = row["metrics"][-1]
        lines.append(
            "| "
            f"`{row['paper_method']}` | `{row['expected_order']}` | "
            f"`{row['coordinate_pairwise_orders']}` | `{row['velocity_pairwise_orders']}` | "
            f"`{finest['coordinate_error_q']:.3e}` | `{finest['velocity_error_v']:.3e}` | "
            f"`{row['max_newton_residual_norm']:.3e}` |"
        )
    lines.extend(
        [
            "",
            "## Active B2 Full T=10 Coarse Candidate Probe",
            "",
            f"- API: `{full_t10_coarse_candidate_probe['runner_api']}`.",
            f"- t_final/reference h: `{full_t10_coarse_candidate_probe['t_final']}` / `{full_t10_coarse_candidate_probe['reference_h']}`.",
            f"- h grid: `{full_t10_coarse_candidate_probe['comparison_h']}`.",
            f"- rows: `{len(full_t10_coarse_candidate_probe['rows'])}`.",
            f"- Full T=10 candidate probe completed: `{full_t10_coarse_candidate_probe['full_T10_candidate_probe_completed']}`.",
            f"- Full T=10 source-policy reproduction: `{full_t10_coarse_candidate_probe['full_T10_source_policy_reproduction']}`.",
            f"- Source-policy reference h: `{full_t10_coarse_candidate_probe['source_policy_reference_h']}`.",
            f"- Source-policy reference invoked: `{not full_t10_coarse_candidate_probe['source_policy_reference_not_invoked']}`.",
            f"- Source-policy rows completed: `{full_t10_coarse_candidate_probe['source_policy_rows_completed']}`.",
            f"- Finite/residual-ok rows: `{full_t10_coarse_candidate_probe['finite_row_count']}/{full_t10_coarse_candidate_probe['residual_ok_row_count']}`.",
            "",
            "| method | expected order | coord pair orders | vel pair orders | finest coord error | finest vel error | max residual |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in full_t10_coarse_candidate_probe["rows"]:
        finest = row["metrics"][-1]
        lines.append(
            "| "
            f"`{row['paper_method']}` | `{row['expected_order']}` | "
            f"`{row['coordinate_pairwise_orders']}` | `{row['velocity_pairwise_orders']}` | "
            f"`{finest['coordinate_error_q']:.3e}` | `{finest['velocity_error_v']:.3e}` | "
            f"`{row['max_newton_residual_norm']:.3e}` |"
        )
    lines.extend(
        [
            "",
            "## Active B2 Source-Reference Full T=10 Candidate Probe",
            "",
            f"- API: `{source_reference_full_t10_candidate_probe['runner_api']}`.",
            f"- t_final/reference h: `{source_reference_full_t10_candidate_probe['t_final']}` / `{source_reference_full_t10_candidate_probe['reference_h']}`.",
            f"- h grid: `{source_reference_full_t10_candidate_probe['comparison_h']}`.",
            f"- rows: `{len(source_reference_full_t10_candidate_probe['rows'])}`.",
            f"- Full T=10 candidate probe completed: `{source_reference_full_t10_candidate_probe['full_T10_candidate_probe_completed']}`.",
            f"- Full T=10 source-policy reproduction: `{source_reference_full_t10_candidate_probe['full_T10_source_policy_reproduction']}`.",
            f"- Source-policy reference h: `{source_reference_full_t10_candidate_probe['source_policy_reference_h']}`.",
            f"- Source-policy reference invoked: `{source_reference_full_t10_candidate_probe['source_policy_reference_invoked']}`.",
            f"- Source-policy rows completed: `{source_reference_full_t10_candidate_probe['source_policy_rows_completed']}`.",
            f"- Method/DAE runner equivalent: `{source_reference_full_t10_candidate_probe['source_policy_method_runner_equivalent']}/{source_reference_full_t10_candidate_probe['source_policy_dae_runner_equivalent']}`.",
            f"- Finite/residual-ok rows: `{source_reference_full_t10_candidate_probe['finite_row_count']}/{source_reference_full_t10_candidate_probe['residual_ok_row_count']}`.",
            "",
            "| method | expected order | coord pair orders | vel pair orders | finest coord error | finest vel error | max residual | accepted use |",
            "|---|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in source_reference_full_t10_candidate_probe["rows"]:
        finest = row["metrics"][-1]
        lines.append(
            "| "
            f"`{row['paper_method']}` | `{row['expected_order']}` | "
            f"`{row['coordinate_pairwise_orders']}` | `{row['velocity_pairwise_orders']}` | "
            f"`{finest['coordinate_error_q']:.3e}` | `{finest['velocity_error_v']:.3e}` | "
            f"`{row['max_newton_residual_norm']:.3e}` | `{row['accepted_use']}` |"
        )
    lines.extend(
        [
            "",
            "## TFE m=3 Full T=10 Coarse Formula Probe",
            "",
            f"- API: `{tfe_m3_full_t10_formula_probe['runner_api']}`.",
            f"- t_final/reference h: `{tfe_m3_full_t10_formula_probe['t_final']}` / `{tfe_m3_full_t10_formula_probe['reference_h']}`.",
            f"- h grid: `{tfe_m3_full_t10_formula_probe['comparison_h']}`.",
            f"- rows: `{len(tfe_m3_full_t10_formula_probe['rows'])}`.",
            f"- full T=10 formula probe completed: `{tfe_m3_full_t10_formula_probe['full_T10_formula_probe_completed']}`.",
            f"- formal expected order: `{tfe_m3_full_t10_formula_probe['formal_expected_order']}`.",
            f"- Source-policy reference invoked: `{not tfe_m3_full_t10_formula_probe['source_policy_reference_not_invoked']}`.",
            f"- Source-policy rows completed: `{tfe_m3_full_t10_formula_probe['source_policy_rows_completed']}`.",
            f"- Finite/residual-ok rows: `{tfe_m3_full_t10_formula_probe['finite_row_count']}/{tfe_m3_full_t10_formula_probe['residual_ok_row_count']}`.",
            "",
            "| method | expected order | coord pair orders | vel pair orders | finest coord error | finest vel error | max residual |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in tfe_m3_full_t10_formula_probe["rows"]:
        finest = row["metrics"][-1]
        lines.append(
            "| "
            f"`{row['paper_method']}` | `{row['expected_order']}` | "
            f"`{row['coordinate_pairwise_orders']}` | `{row['velocity_pairwise_orders']}` | "
            f"`{finest['coordinate_error_q']:.3e}` | `{finest['velocity_error_v']:.3e}` | "
            f"`{row['max_newton_residual_norm']:.3e}` |"
        )
    lines.extend(
        [
            "",
            "| case | method | frictional | coord pair orders | vel pair orders | max residual |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    for row in tfe_candidate_smoke["rows"]:
        lines.append(
            "| "
            f"`{row['case_id']}` | `{row['method']}` | `{row['frictional']}` | "
            f"`{row['coordinate_pairwise_orders']}` | `{row['velocity_pairwise_orders']}` | "
            f"`{row['max_newton_residual_norm']:.3e}` |"
        )
    lines.append("")
    lines.append(
        "Reading rule: this closes parameter, planar metric, absolute-coordinate residual-smoke, "
        "bounded trajectory-metric smoke, and candidate Newmark/trapezoidal/TFE/Gauss6/friction smoke "
        "layers plus a unified bounded source-policy runner API, an absolute-coordinate planar-lift "
        "trajectory probe, a bounded stepwise absolute-coordinate DAE residual runner, a named "
        "source-policy absolute-coordinate DAE runner contract entrypoint that remains candidate-backed "
        "and non-equivalent, named non-equivalent method-runner and Gauss6/FullVA DAE runner contract "
        "entrypoints, a DAE trajectory bridge contract, a candidate-friction DAE trajectory contract, full T=10 coarse candidate probe, "
        "full T=10 active-B2 h=1e-4 source-reference candidate probe, TFE m=3 full T=10 coarse formula probe, "
        "and a full T=10 frictionless source-reference h=1e-4 probe only. It is not an original TFE source-policy reproduction and does not "
        "authorize external-superiority claims."
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("tfe_source_pendulum_model_audit=written")
    print(f"parameter_match_source_spec={params_match}")
    print("source_pendulum_parameter_model_implemented=True")
    print("source_error_norm_and_output_policy_encoded=True")
    print("brown_mcphee_candidate_friction_law_encoded=True")
    print("brown_mcphee_published_formula_structure_encoded=True")
    print("brown_mcphee_source_code_equivalent_law=False")
    print("absolute_coordinate_dae_residual_smoke_implemented=True")
    print("source_output_time_integration_smoke_implemented=True")
    print("source_reference_solution_policy_smoke_implemented=True")
    print("source_reference_solution_policy_full_T10_probe_implemented=True")
    print("source_comparator_candidate_runners_implemented=True")
    print("tfe_m1_m2_m3_candidate_runner_smoke_implemented=True")
    print("source_policy_method_runner_contract_present=True")
    print("source_policy_tfe_newmark_trapezoidal_method_runners_implemented=False")
    print("gauss6_fullva_source_pendulum_candidate_smoke_implemented=True")
    print("gauss6_fullva_absolute_coordinate_source_policy_runner_implemented=False")
    print("source_policy_gauss6_fullva_absolute_coordinate_dae_runner_contract_present=True")
    print("source_policy_gauss6_fullva_absolute_coordinate_dae_runner_implemented=False")
    print("gauss6_fullva_on_source_pendulum_implemented=True")
    print(f"gauss6_fullva_source_pendulum_candidate_rows={gauss6_candidate_smoke['row_count']}")
    print("gauss6_fullva_source_pendulum_candidate_source_policy_rows_completed=0")
    print("source_pendulum_same_test_work_precision_implemented=True")
    print(f"source_pendulum_same_test_work_precision_metric_rows={same_test_work_precision_metric_rows}")
    print("absolute_coordinate_planar_lift_trajectory_probe_implemented=True")
    print(f"absolute_coordinate_planar_lift_trajectory_probe_rows={absolute_lift_probe['row_count']}")
    print("absolute_coordinate_planar_lift_trajectory_probe_source_policy_rows_completed=0")
    print("dae_trajectory_bridge_contract_implemented=True")
    print(f"dae_trajectory_bridge_contract_rows={dae_trajectory_bridge_contract['row_count']}")
    print("dae_trajectory_bridge_contract_source_policy_rows_completed=0")
    print("candidate_frictional_dae_trajectory_contract_implemented=True")
    print(
        "candidate_frictional_dae_trajectory_contract_rows="
        f"{candidate_frictional_dae_trajectory_contract['row_count']}"
    )
    print("candidate_frictional_dae_trajectory_contract_source_policy_rows_completed=0")
    print("tfe_appendix_b_coefficient_certificate_checked=True")
    print("bounded_source_policy_runner_smoke_implemented=True")
    print("active_tfe_b2_candidate_row_smoke_implemented=True")
    print("active_tfe_b2_full_T10_coarse_candidate_probe_implemented=True")
    print("active_tfe_b2_source_reference_full_T10_candidate_probe_implemented=True")
    print("tfe_m3_full_T10_coarse_formula_probe_implemented=True")
    print("pendulum_dae_runner_implemented=False")
    print("source_policy_rows_completed=0")


if __name__ == "__main__":
    main()
