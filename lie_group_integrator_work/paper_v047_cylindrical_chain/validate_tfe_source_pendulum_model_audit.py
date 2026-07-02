#!/usr/bin/env python3
"""Validate the TFE source-pendulum parameter-model audit."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
MODEL_PATH = ROOT / "v048_cross_paper_same_test_benchmarks" / "tfe_source_pendulum_model.py"


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(PAPER / "TFE_SOURCE_PENDULUM_MODEL_AUDIT.json")
        audit_md = read_text(PAPER / "TFE_SOURCE_PENDULUM_MODEL_AUDIT.md")
        spec = read_json(PAPER / "TFE_SOURCE_POLICY_SPEC.json")
    except Exception as exc:  # noqa: BLE001
        print(f"TFE source-pendulum model audit validation: FAIL\n- {exc}")
        return 1

    body = spec.get("source_policy", {}).get("body_parameters", {})
    friction = spec.get("source_policy", {}).get("friction_parameters", {})
    values = audit.get("parameter_values", {})
    reductions = audit.get("candidate_planar_reductions", {})
    smoke = audit.get("frictionless_smoke_trajectory", {})
    metric_smoke = audit.get("source_metric_smoke", {})
    friction_torque_smoke = audit.get("candidate_friction_torque_smoke", {})
    friction_source_anchor = audit.get("brown_mcphee_source_text_anchor", {})
    friction_formula_boundary = audit.get("brown_mcphee_formula_boundary", {})
    frictional_smoke = audit.get("frictional_candidate_smoke_trajectory", {})
    absolute_smoke = audit.get("absolute_coordinate_dae_residual_smoke", {})
    absolute_frictional_smoke = audit.get("absolute_coordinate_frictional_candidate_dae_smoke", {})
    source_output_time_smoke = audit.get("source_output_time_integration_smoke", {})
    source_reference_policy_smoke = audit.get("source_reference_solution_policy_smoke", {})
    source_reference_full_t10_probe = audit.get("source_reference_solution_policy_full_T10_probe", {})
    comparator_smoke = audit.get("source_comparator_candidate_runner_smoke", {})
    tfe_candidate_smoke = audit.get("source_tfe_candidate_runner_smoke", {})
    method_candidate_contract = audit.get("source_method_candidate_runner_contract_smoke", {})
    source_policy_method_runner_contract = audit.get(
        "source_policy_method_runner_contract",
        {},
    )
    gauss6_smoke = audit.get("gauss6_fullva_source_pendulum_candidate_smoke", {})
    gauss6_dae_candidate_contract = audit.get("gauss6_fullva_dae_candidate_contract_smoke", {})
    source_policy_gauss6_dae_runner_contract = audit.get(
        "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_contract",
        {},
    )
    same_test_work_precision = audit.get("source_pendulum_same_test_work_precision_smoke", {})
    absolute_lift_probe = audit.get("absolute_coordinate_planar_lift_trajectory_probe", {})
    bounded_dae_trajectory_runner = audit.get(
        "bounded_absolute_coordinate_dae_trajectory_runner_smoke",
        {},
    )
    monolithic_dae_candidate_runner = audit.get(
        "monolithic_absolute_coordinate_dae_candidate_runner_smoke",
        {},
    )
    source_policy_dae_runner_contract = audit.get(
        "source_policy_absolute_coordinate_dae_runner_contract",
        {},
    )
    dae_trajectory_bridge_contract = audit.get("dae_trajectory_bridge_contract_smoke", {})
    candidate_frictional_dae_trajectory_contract = audit.get(
        "candidate_frictional_dae_trajectory_contract_smoke",
        {},
    )
    appendix_b_certificate = audit.get("tfe_appendix_b_coefficient_certificate", {})
    bounded_runner_smoke = audit.get("bounded_source_policy_runner_smoke", {})
    active_b2_smoke = audit.get("active_tfe_b2_candidate_row_smoke", {})
    full_t10_coarse_probe = audit.get("active_tfe_b2_full_T10_coarse_candidate_probe", {})
    source_reference_full_t10_candidate_probe = audit.get(
        "active_tfe_b2_source_reference_full_T10_candidate_probe",
        {},
    )
    tfe_m3_full_t10_formula_probe = audit.get("tfe_m3_full_T10_coarse_formula_probe", {})
    boundary = audit.get("closure_boundary", {})
    execution = audit.get("execution_policy", {})
    preflight = audit.get("source_policy_runner_equivalence_preflight", {})

    checks.check(MODEL_PATH.exists() and MODEL_PATH.stat().st_size > 0, "model file missing")
    checks.check(audit.get("schema") == "tfe-source-pendulum-model-audit-v1", "schema changed")
    checks.check(
        audit.get("status") == "source_parameter_model_implemented_runner_policy_open",
        "status changed",
    )
    checks.check(audit.get("submission_ready") is False, "audit overclaims submission readiness")
    checks.check(audit.get("external_superiority_claim_allowed") is False, "audit overclaims external superiority")
    checks.check(audit.get("parameter_match_source_spec") is True, "parameters no longer match source spec")
    checks.check(audit.get("source_pendulum_parameter_model_implemented") is True, "parameter model not implemented")
    checks.check(audit.get("frictionless_planar_rhs_smoke_implemented") is True, "frictionless smoke missing")
    checks.check(
        audit.get("absolute_coordinate_dae_residual_smoke_implemented") is True,
        "absolute-coordinate DAE residual smoke missing",
    )
    checks.check(
        audit.get("absolute_coordinate_frictional_candidate_dae_smoke_implemented") is True,
        "absolute-coordinate frictional candidate DAE smoke missing",
    )
    checks.check(
        audit.get("source_output_time_integration_smoke_implemented") is True,
        "source-output time-integration smoke missing",
    )
    checks.check(
        audit.get("source_policy_time_integration_runner_equivalent") is False,
        "source-policy time-integration runner overclaimed",
    )
    checks.check(
        audit.get("source_reference_solution_policy_smoke_implemented") is True,
        "source reference solution policy smoke missing",
    )
    checks.check(
        audit.get("source_reference_solution_policy_smoke_full_T10") is False,
        "source reference solution policy smoke overclaims full T=10 run",
    )
    checks.check(
        audit.get("source_reference_solution_policy_full_T10_probe_implemented") is True,
        "source reference full T=10 probe missing",
    )
    checks.check(
        audit.get("source_reference_solution_policy_full_T10_probe_completed") is True,
        "source reference full T=10 probe not completed",
    )
    checks.check(
        audit.get("source_reference_solution_policy_full_T10_probe_rows_completed") == 0,
        "source reference full T=10 probe overclosed source-policy rows",
    )
    checks.check(
        audit.get("source_comparator_candidate_runners_implemented") is True,
        "source comparator candidate runners missing",
    )
    checks.check(
        audit.get("newmark_beta_candidate_runner_smoke_implemented") is True,
        "Newmark-beta candidate runner smoke missing",
    )
    checks.check(
        audit.get("trapezoidal_candidate_runner_smoke_implemented") is True,
        "trapezoidal candidate runner smoke missing",
    )
    checks.check(
        audit.get("source_policy_method_runner_equivalent") is False,
        "source-policy method runner equivalence overclaimed",
    )
    checks.check(
        audit.get("tfe_m1_m2_m3_candidate_runner_smoke_implemented") is True,
        "TFE m=1/2/3 candidate runner smoke missing",
    )
    checks.check(
        audit.get("source_method_candidate_runner_contract_implemented") is True,
        "source-method candidate runner contract missing",
    )
    checks.check(
        audit.get("source_method_candidate_runner_contract_complete") is True,
        "source-method candidate runner contract incomplete",
    )
    checks.check(
        audit.get("source_method_candidate_runner_contract_rows") == 5,
        "source-method candidate runner contract row count changed",
    )
    checks.check(
        audit.get("source_method_candidate_runner_contract_all_step_states_finite") is True,
        "source-method candidate runner contract has nonfinite states",
    )
    checks.check(
        audit.get("source_method_candidate_runner_contract_all_candidate_residuals_below_1e_8")
        is True,
        "source-method candidate runner contract residual gate failed",
    )
    checks.check(
        audit.get("source_method_candidate_runner_contract_source_policy_rows_completed") == 0,
        "source-method candidate runner contract overcloses source-policy rows",
    )
    checks.check(
        audit.get("source_method_candidate_runner_contract_method_equivalent") is False,
        "source-method candidate runner contract overclaims method equivalence",
    )
    checks.check(
        audit.get("source_method_candidate_runner_contract_dae_equivalent") is False,
        "source-method candidate runner contract overclaims DAE equivalence",
    )
    checks.check(
        audit.get("tfe_appendix_b_coefficient_certificate_checked") is True,
        "TFE Appendix-B coefficient certificate missing",
    )
    checks.check(
        audit.get("tfe_appendix_b_coefficient_certificate_row_count") == 3,
        "TFE Appendix-B coefficient certificate row count changed",
    )
    checks.check(
        float(audit.get("tfe_appendix_b_coefficient_certificate_max_abs_diff")) <= 1.0e-14,
        "TFE Appendix-B coefficient certificate mismatch too large",
    )
    checks.check(
        audit.get("tfe_m1_m2_m3_source_policy_runners_implemented") is False,
        "TFE source-policy runners unexpectedly implemented",
    )
    checks.check(
        audit.get("gauss6_fullva_source_pendulum_candidate_smoke_implemented") is True,
        "Gauss6/FullVA source-pendulum candidate smoke missing",
    )
    checks.check(
        audit.get("gauss6_fullva_absolute_coordinate_source_policy_runner_implemented") is False,
        "Gauss6/FullVA source-policy runner unexpectedly implemented",
    )
    checks.check(
        audit.get("gauss6_fullva_on_source_pendulum_implemented") is True,
        "Gauss6/FullVA legacy candidate alias changed",
    )
    checks.check(
        audit.get("gauss6_fullva_source_pendulum_candidate_rows") == 2,
        "Gauss6/FullVA source-pendulum candidate row count changed",
    )
    checks.check(
        audit.get("gauss6_fullva_source_pendulum_candidate_source_policy_rows_completed") == 0,
        "Gauss6/FullVA candidate overclosed source-policy rows",
    )
    checks.check(
        audit.get("gauss6_fullva_source_pendulum_candidate_method_equivalent") is False,
        "Gauss6/FullVA candidate overclaims source-policy method equivalence",
    )
    checks.check(
        audit.get("gauss6_fullva_dae_candidate_contract_implemented") is True,
        "Gauss6/FullVA DAE candidate contract missing",
    )
    checks.check(
        audit.get("gauss6_fullva_dae_candidate_contract_rows") == 1,
        "Gauss6/FullVA DAE candidate contract row count changed",
    )
    checks.check(
        audit.get("gauss6_fullva_dae_candidate_contract_all_step_states_finite") is True,
        "Gauss6/FullVA DAE candidate contract has nonfinite state",
    )
    checks.check(
        audit.get("gauss6_fullva_dae_candidate_contract_all_candidate_residuals_below_1e_8")
        is True,
        "Gauss6/FullVA DAE candidate contract residual gate failed",
    )
    checks.check(
        audit.get("gauss6_fullva_dae_candidate_contract_source_policy_rows_completed") == 0,
        "Gauss6/FullVA DAE candidate contract overcloses source-policy rows",
    )
    checks.check(
        audit.get("gauss6_fullva_dae_candidate_contract_method_equivalent") is False,
        "Gauss6/FullVA DAE candidate contract overclaims method equivalence",
    )
    checks.check(
        audit.get("gauss6_fullva_dae_candidate_contract_dae_equivalent") is False,
        "Gauss6/FullVA DAE candidate contract overclaims DAE equivalence",
    )
    checks.check(
        audit.get("gauss6_fullva_dae_candidate_contract_fullva_dae_equivalent") is False,
        "Gauss6/FullVA DAE candidate contract overclaims FullVA DAE equivalence",
    )
    checks.check(
        audit.get("gauss6_fullva_dae_candidate_contract_absolute_source_policy_runner_implemented")
        is False,
        "Gauss6/FullVA DAE candidate contract overclaims absolute source-policy runner",
    )
    checks.check(
        float(audit.get("gauss6_fullva_dae_candidate_contract_max_candidate_step_residual_norm"))
        < 1.0e-8,
        "Gauss6/FullVA DAE candidate contract residual too large",
    )
    checks.check(
        audit.get("source_pendulum_same_test_work_precision_implemented") is True,
        "source-pendulum same-test work/precision smoke missing",
    )
    checks.check(
        audit.get("source_pendulum_same_test_work_precision_method_count") == 6,
        "source-pendulum same-test method count changed",
    )
    checks.check(
        audit.get("source_pendulum_same_test_work_precision_method_rows") == 6,
        "source-pendulum same-test method row count changed",
    )
    checks.check(
        audit.get("source_pendulum_same_test_work_precision_metric_rows") == 18,
        "source-pendulum same-test metric row count changed",
    )
    checks.check(
        audit.get("source_pendulum_same_test_work_precision_source_policy_rows_completed") == 0,
        "source-pendulum same-test overcloses source-policy rows",
    )
    checks.check(
        audit.get("source_pendulum_same_test_work_precision_external_superiority_claim_allowed") is False,
        "source-pendulum same-test overclaims external superiority",
    )
    checks.check(
        float(audit.get("source_pendulum_same_test_work_precision_gauss6_velocity_order_floor")) > 5.5,
        "source-pendulum same-test Gauss6 velocity order floor too low",
    )
    checks.check(
        float(audit.get("source_pendulum_same_test_work_precision_tfe_m3_velocity_order_floor")) > 4.5,
        "source-pendulum same-test TFE m=3 velocity order floor too low",
    )
    checks.check(
        audit.get("absolute_coordinate_planar_lift_trajectory_probe_implemented") is True,
        "absolute-coordinate planar-lift trajectory probe missing",
    )
    checks.check(
        audit.get("absolute_coordinate_planar_lift_trajectory_probe_method_count") == 6,
        "absolute-coordinate planar-lift method count changed",
    )
    checks.check(
        audit.get("absolute_coordinate_planar_lift_trajectory_probe_rows") == 12,
        "absolute-coordinate planar-lift row count changed",
    )
    checks.check(
        audit.get("absolute_coordinate_planar_lift_trajectory_probe_metric_rows") == 36,
        "absolute-coordinate planar-lift metric row count changed",
    )
    checks.check(
        audit.get("absolute_coordinate_planar_lift_trajectory_probe_source_policy_rows_completed") == 0,
        "absolute-coordinate planar-lift overcloses source-policy rows",
    )
    checks.check(
        audit.get("absolute_coordinate_planar_lift_trajectory_probe_dae_runner_equivalent") is False,
        "absolute-coordinate planar-lift overclaims source-policy DAE equivalence",
    )
    for key in [
        "absolute_coordinate_planar_lift_trajectory_probe_max_hinge_position_constraint_norm",
        "absolute_coordinate_planar_lift_trajectory_probe_max_hinge_velocity_constraint_norm",
        "absolute_coordinate_planar_lift_trajectory_probe_max_translational_balance_residual_norm",
        "absolute_coordinate_planar_lift_trajectory_probe_max_axis_projected_rotational_residual_abs",
    ]:
        checks.check(float(audit.get(key)) < 1.0e-10, f"{key} too large")
    checks.check(
        audit.get("bounded_absolute_coordinate_dae_trajectory_runner_implemented") is True,
        "bounded absolute-coordinate DAE trajectory runner missing",
    )
    checks.check(
        audit.get("bounded_absolute_coordinate_dae_trajectory_runner_rows") == 4,
        "bounded absolute-coordinate DAE trajectory runner row count changed",
    )
    checks.check(
        audit.get("bounded_absolute_coordinate_dae_trajectory_runner_metric_rows") == 12,
        "bounded absolute-coordinate DAE trajectory runner metric row count changed",
    )
    checks.check(
        audit.get("bounded_absolute_coordinate_dae_trajectory_runner_step_residual_rows") == 56,
        "bounded absolute-coordinate DAE trajectory runner step residual count changed",
    )
    checks.check(
        audit.get("bounded_absolute_coordinate_dae_trajectory_runner_all_step_states_finite") is True,
        "bounded absolute-coordinate DAE trajectory runner has nonfinite step states",
    )
    checks.check(
        audit.get("bounded_absolute_coordinate_dae_trajectory_runner_source_policy_rows_completed") == 0,
        "bounded absolute-coordinate DAE trajectory runner overcloses source-policy rows",
    )
    checks.check(
        audit.get("bounded_absolute_coordinate_dae_trajectory_runner_dae_runner_equivalent") is False,
        "bounded absolute-coordinate DAE trajectory runner overclaims DAE equivalence",
    )
    checks.check(
        audit.get("bounded_absolute_coordinate_dae_trajectory_runner_monolithic_integrator") is False,
        "bounded absolute-coordinate DAE trajectory runner overclaims monolithic integration",
    )
    for key in [
        "bounded_absolute_coordinate_dae_trajectory_runner_max_hinge_position_constraint_norm",
        "bounded_absolute_coordinate_dae_trajectory_runner_max_hinge_velocity_constraint_norm",
        "bounded_absolute_coordinate_dae_trajectory_runner_max_translational_balance_residual_norm",
        "bounded_absolute_coordinate_dae_trajectory_runner_max_axis_projected_rotational_residual_abs",
    ]:
        checks.check(float(audit.get(key)) < 1.0e-10, f"{key} too large")
    checks.check(
        audit.get("monolithic_absolute_coordinate_dae_candidate_runner_implemented") is True,
        "monolithic absolute-coordinate DAE candidate runner missing",
    )
    checks.check(
        audit.get("monolithic_absolute_coordinate_dae_candidate_runner_rows") == 4,
        "monolithic absolute-coordinate DAE candidate runner row count changed",
    )
    checks.check(
        audit.get("monolithic_absolute_coordinate_dae_candidate_runner_metric_rows") == 12,
        "monolithic absolute-coordinate DAE candidate runner metric row count changed",
    )
    checks.check(
        audit.get("monolithic_absolute_coordinate_dae_candidate_runner_step_residual_rows") == 56,
        "monolithic absolute-coordinate DAE candidate runner step residual count changed",
    )
    checks.check(
        audit.get("monolithic_absolute_coordinate_dae_candidate_runner_all_step_states_finite")
        is True,
        "monolithic absolute-coordinate DAE candidate runner has nonfinite step states",
    )
    checks.check(
        audit.get("monolithic_absolute_coordinate_dae_candidate_runner_all_rows_finite") is True,
        "monolithic absolute-coordinate DAE candidate runner has nonfinite rows",
    )
    checks.check(
        audit.get("monolithic_absolute_coordinate_dae_candidate_runner_all_dae_residuals_below_1e_10")
        is True,
        "monolithic absolute-coordinate DAE candidate runner residual gate failed",
    )
    checks.check(
        audit.get("monolithic_absolute_coordinate_dae_candidate_runner_source_policy_rows_completed")
        == 0,
        "monolithic absolute-coordinate DAE candidate runner overcloses source-policy rows",
    )
    checks.check(
        audit.get("monolithic_absolute_coordinate_dae_candidate_runner_dae_runner_equivalent")
        is False,
        "monolithic absolute-coordinate DAE candidate runner overclaims DAE equivalence",
    )
    checks.check(
        audit.get("monolithic_absolute_coordinate_dae_candidate_runner_monolithic_integrator")
        is False,
        "monolithic absolute-coordinate DAE candidate runner overclaims source-policy monolithic integration",
    )
    for key in [
        "monolithic_absolute_coordinate_dae_candidate_runner_max_hinge_position_constraint_norm",
        "monolithic_absolute_coordinate_dae_candidate_runner_max_hinge_velocity_constraint_norm",
        "monolithic_absolute_coordinate_dae_candidate_runner_max_translational_balance_residual_norm",
        "monolithic_absolute_coordinate_dae_candidate_runner_max_axis_projected_rotational_residual_abs",
    ]:
        checks.check(float(audit.get(key)) < 1.0e-10, f"{key} too large")
    checks.check(
        audit.get("source_policy_absolute_coordinate_dae_runner_contract_present") is True,
        "source-policy absolute-coordinate DAE runner contract marker missing",
    )
    checks.check(
        audit.get("source_policy_absolute_coordinate_dae_runner_implemented") is False,
        "source-policy absolute-coordinate DAE runner overclaims implementation",
    )
    checks.check(
        audit.get("source_policy_absolute_coordinate_dae_runner_rows") == 4,
        "source-policy absolute-coordinate DAE runner contract row count changed",
    )
    checks.check(
        audit.get("source_policy_absolute_coordinate_dae_runner_metric_rows") == 12,
        "source-policy absolute-coordinate DAE runner contract metric row count changed",
    )
    checks.check(
        audit.get("source_policy_absolute_coordinate_dae_runner_step_residual_rows") == 56,
        "source-policy absolute-coordinate DAE runner contract step residual count changed",
    )
    checks.check(
        audit.get("source_policy_absolute_coordinate_dae_runner_all_step_states_finite")
        is True,
        "source-policy absolute-coordinate DAE runner contract has nonfinite step states",
    )
    checks.check(
        audit.get("source_policy_absolute_coordinate_dae_runner_all_rows_finite") is True,
        "source-policy absolute-coordinate DAE runner contract has nonfinite rows",
    )
    checks.check(
        audit.get("source_policy_absolute_coordinate_dae_runner_all_dae_residuals_below_1e_10")
        is True,
        "source-policy absolute-coordinate DAE runner contract residual gate failed",
    )
    checks.check(
        audit.get("source_policy_absolute_coordinate_dae_runner_source_policy_rows_completed")
        == 0,
        "source-policy absolute-coordinate DAE runner contract overcloses source-policy rows",
    )
    checks.check(
        audit.get("source_policy_absolute_coordinate_dae_runner_dae_runner_equivalent")
        is False,
        "source-policy absolute-coordinate DAE runner contract overclaims DAE equivalence",
    )
    checks.check(
        audit.get("source_policy_absolute_coordinate_dae_runner_monolithic_integrator")
        is False,
        "source-policy absolute-coordinate DAE runner contract overclaims monolithic integration",
    )
    checks.check(
        audit.get("source_policy_absolute_coordinate_dae_runner_candidate_api")
        == "monolithic_absolute_coordinate_dae_candidate_runner_smoke",
        "source-policy absolute-coordinate DAE runner contract candidate binding changed",
    )
    for key in [
        "source_policy_absolute_coordinate_dae_runner_max_hinge_position_constraint_norm",
        "source_policy_absolute_coordinate_dae_runner_max_hinge_velocity_constraint_norm",
        "source_policy_absolute_coordinate_dae_runner_max_translational_balance_residual_norm",
        "source_policy_absolute_coordinate_dae_runner_max_axis_projected_rotational_residual_abs",
    ]:
        checks.check(float(audit.get(key)) < 1.0e-10, f"{key} too large")
    checks.check(
        audit.get("dae_trajectory_bridge_contract_implemented") is True,
        "DAE trajectory bridge contract missing",
    )
    checks.check(
        audit.get("dae_trajectory_bridge_contract_rows") == 12,
        "DAE trajectory bridge contract row count changed",
    )
    checks.check(
        audit.get("dae_trajectory_bridge_contract_matched_rows") == 12,
        "DAE trajectory bridge contract lost row matches",
    )
    checks.check(
        audit.get("dae_trajectory_bridge_contract_source_metric_rows") == 12,
        "DAE trajectory bridge source metric row count changed",
    )
    checks.check(
        audit.get("dae_trajectory_bridge_contract_dae_metric_rows") == 12,
        "DAE trajectory bridge DAE metric row count changed",
    )
    checks.check(
        audit.get("dae_trajectory_bridge_contract_all_rows_finite") is True,
        "DAE trajectory bridge has nonfinite rows",
    )
    checks.check(
        audit.get("dae_trajectory_bridge_contract_all_dae_residuals_below_1e_10") is True,
        "DAE trajectory bridge residual gate failed",
    )
    checks.check(
        audit.get("dae_trajectory_bridge_contract_source_policy_rows_completed") == 0,
        "DAE trajectory bridge overcloses source-policy rows",
    )
    checks.check(
        audit.get("dae_trajectory_bridge_contract_dae_runner_equivalent") is False,
        "DAE trajectory bridge overclaims DAE equivalence",
    )
    checks.check(
        audit.get("dae_trajectory_bridge_contract_monolithic_integrator") is False,
        "DAE trajectory bridge overclaims monolithic integration",
    )
    for key in [
        "dae_trajectory_bridge_contract_max_candidate_step_residual_norm",
        "dae_trajectory_bridge_contract_max_hinge_position_constraint_norm",
        "dae_trajectory_bridge_contract_max_hinge_velocity_constraint_norm",
        "dae_trajectory_bridge_contract_max_translational_balance_residual_norm",
        "dae_trajectory_bridge_contract_max_axis_projected_rotational_residual_abs",
    ]:
        checks.check(float(audit.get(key)) < 1.0e-10, f"{key} too large")
    checks.check(
        audit.get("candidate_frictional_dae_trajectory_contract_implemented") is True,
        "candidate-friction DAE trajectory contract missing",
    )
    checks.check(
        audit.get("candidate_frictional_dae_trajectory_contract_rows") == 12,
        "candidate-friction DAE trajectory contract row count changed",
    )
    checks.check(
        audit.get("candidate_frictional_dae_trajectory_contract_step_residual_rows") == 56,
        "candidate-friction DAE trajectory contract step-residual row count changed",
    )
    checks.check(
        audit.get("candidate_frictional_dae_trajectory_contract_all_rows_finite") is True,
        "candidate-friction DAE trajectory contract has nonfinite rows",
    )
    checks.check(
        audit.get("candidate_frictional_dae_trajectory_contract_all_dae_residuals_below_1e_9") is True,
        "candidate-friction DAE trajectory contract residual gate failed",
    )
    checks.check(
        audit.get("candidate_frictional_dae_trajectory_contract_all_friction_power_nonpositive") is True,
        "candidate-friction DAE trajectory contract friction power sign failed",
    )
    checks.check(
        audit.get("candidate_frictional_dae_trajectory_contract_source_policy_rows_completed") == 0,
        "candidate-friction DAE trajectory contract overcloses source-policy rows",
    )
    checks.check(
        audit.get("candidate_frictional_dae_trajectory_contract_dae_runner_equivalent") is False,
        "candidate-friction DAE trajectory contract overclaims DAE equivalence",
    )
    checks.check(
        audit.get("candidate_frictional_dae_trajectory_contract_method_runner_equivalent") is False,
        "candidate-friction DAE trajectory contract overclaims method equivalence",
    )
    checks.check(
        audit.get("candidate_frictional_dae_trajectory_contract_brown_mcphee_source_code_equivalent_law") is False,
        "candidate-friction DAE trajectory contract overclaims Brown--McPhee source-code law",
    )
    checks.check(
        audit.get("candidate_frictional_dae_trajectory_contract_monolithic_integrator") is False,
        "candidate-friction DAE trajectory contract overclaims monolithic integration",
    )
    checks.check(
        float(audit.get("candidate_frictional_dae_trajectory_contract_max_candidate_step_residual_norm")) < 1.0e-9,
        "candidate-friction DAE trajectory contract step residual too large",
    )
    for key in [
        "candidate_frictional_dae_trajectory_contract_max_hinge_position_constraint_norm",
        "candidate_frictional_dae_trajectory_contract_max_hinge_velocity_constraint_norm",
        "candidate_frictional_dae_trajectory_contract_max_translational_balance_residual_norm",
        "candidate_frictional_dae_trajectory_contract_max_axis_projected_rotational_residual_abs",
    ]:
        checks.check(float(audit.get(key)) < 1.0e-9, f"{key} too large")
    checks.check(
        float(audit.get("candidate_frictional_dae_trajectory_contract_max_candidate_friction_power")) <= 1.0e-12,
        "candidate-friction DAE trajectory contract friction power should be nonpositive",
    )
    checks.check(
        float(audit.get("candidate_frictional_dae_trajectory_contract_min_candidate_friction_power")) < 0.0,
        "candidate-friction DAE trajectory contract should record dissipative friction power",
    )
    checks.check(
        audit.get("bounded_source_policy_runner_api_implemented") is True,
        "bounded source-policy runner API missing",
    )
    checks.check(
        audit.get("bounded_source_policy_runner_smoke_implemented") is True,
        "bounded source-policy runner smoke missing",
    )
    checks.check(
        audit.get("bounded_source_policy_runner_unified_dispatch") is True,
        "bounded source-policy runner lost unified dispatch",
    )
    checks.check(audit.get("bounded_source_policy_runner_method_count") == 4, "bounded runner method count changed")
    checks.check(audit.get("bounded_source_policy_runner_rows") == 4, "bounded runner row count changed")
    checks.check(
        audit.get("bounded_source_policy_runner_full_T10") is False,
        "bounded runner overclaims full T=10",
    )
    checks.check(
        audit.get("bounded_source_policy_runner_source_policy_rows_completed") == 0,
        "bounded runner overcloses source-policy rows",
    )
    checks.check(
        audit.get("bounded_source_policy_runner_method_equivalent") is False,
        "bounded runner overclaims source-policy method equivalence",
    )
    checks.check(
        audit.get("active_tfe_b2_candidate_row_smoke_implemented") is True,
        "active B2 candidate row smoke missing",
    )
    checks.check(
        audit.get("active_tfe_b2_candidate_row_smoke_full_T10") is False,
        "active B2 candidate smoke overclaims full T=10",
    )
    checks.check(
        audit.get("active_tfe_b2_source_policy_rows_completed") == 0,
        "active B2 smoke overcloses source-policy rows",
    )
    checks.check(
        audit.get("active_tfe_b2_full_T10_coarse_candidate_probe_implemented") is True,
        "active B2 full T=10 coarse probe missing",
    )
    checks.check(
        audit.get("active_tfe_b2_full_T10_coarse_candidate_probe_full_T10") is True,
        "active B2 full T=10 coarse probe did not run full horizon",
    )
    checks.check(
        audit.get("active_tfe_b2_full_T10_coarse_candidate_probe_source_policy_rows_completed") == 0,
        "active B2 full T=10 coarse probe overcloses source-policy rows",
    )
    checks.check(
        audit.get("active_tfe_b2_full_T10_coarse_candidate_probe_source_policy_reference_not_invoked") is True,
        "active B2 full T=10 coarse probe invoked source-policy reference",
    )
    checks.check(
        audit.get("active_tfe_b2_full_T10_coarse_candidate_probe_finite_rows") == 4,
        "active B2 full T=10 coarse probe finite row count changed",
    )
    checks.check(
        audit.get("active_tfe_b2_full_T10_coarse_candidate_probe_residual_ok_rows") == 4,
        "active B2 full T=10 coarse probe residual row count changed",
    )
    checks.check(
        audit.get("active_tfe_b2_source_reference_full_T10_candidate_probe_implemented") is True,
        "active B2 source-reference full T=10 candidate probe missing",
    )
    checks.check(
        audit.get("active_tfe_b2_source_reference_full_T10_candidate_probe_full_T10") is True,
        "active B2 source-reference probe did not run full horizon",
    )
    checks.check(
        audit.get(
            "active_tfe_b2_source_reference_full_T10_candidate_probe_source_policy_reference_h"
        )
        == 0.0001,
        "active B2 source-reference probe h changed",
    )
    checks.check(
        audit.get(
            "active_tfe_b2_source_reference_full_T10_candidate_probe_source_policy_reference_invoked"
        )
        is True,
        "active B2 source-reference probe did not invoke h=1e-4 reference",
    )
    checks.check(
        audit.get(
            "active_tfe_b2_source_reference_full_T10_candidate_probe_source_policy_rows_completed"
        )
        == 0,
        "active B2 source-reference probe overcloses source-policy rows",
    )
    checks.check(
        audit.get("active_tfe_b2_source_reference_full_T10_candidate_probe_finite_rows") == 4,
        "active B2 source-reference probe finite row count changed",
    )
    checks.check(
        audit.get("active_tfe_b2_source_reference_full_T10_candidate_probe_residual_ok_rows") == 4,
        "active B2 source-reference probe residual row count changed",
    )
    checks.check(
        audit.get("active_tfe_b2_source_reference_full_T10_candidate_probe_method_equivalent")
        is False,
        "active B2 source-reference probe overclaims method equivalence",
    )
    checks.check(
        audit.get("active_tfe_b2_source_reference_full_T10_candidate_probe_dae_runner_equivalent")
        is False,
        "active B2 source-reference probe overclaims DAE equivalence",
    )
    checks.check(
        audit.get("tfe_m3_full_T10_coarse_formula_probe_implemented") is True,
        "TFE m=3 full T=10 formula probe missing",
    )
    checks.check(
        audit.get("tfe_m3_full_T10_coarse_formula_probe_full_T10") is True,
        "TFE m=3 full T=10 formula probe did not run full horizon",
    )
    checks.check(
        audit.get("tfe_m3_full_T10_coarse_formula_probe_source_policy_rows_completed") == 0,
        "TFE m=3 formula probe overclosed source-policy rows",
    )
    checks.check(
        audit.get("tfe_m3_full_T10_coarse_formula_probe_source_policy_reference_not_invoked") is True,
        "TFE m=3 formula probe invoked source-policy reference",
    )
    checks.check(
        audit.get("tfe_m3_full_T10_coarse_formula_probe_finite_rows") == 1,
        "TFE m=3 formula probe finite row count changed",
    )
    checks.check(
        audit.get("tfe_m3_full_T10_coarse_formula_probe_residual_ok_rows") == 1,
        "TFE m=3 formula probe residual row count changed",
    )
    checks.check(
        audit.get("tfe_m3_full_T10_coarse_formula_probe_formal_expected_order") == 5,
        "TFE m=3 formula probe expected order changed",
    )
    checks.check(audit.get("source_policy_dae_runner_equivalent") is False, "source-policy DAE runner overclaimed")
    checks.check(audit.get("pendulum_dae_runner_implemented") is False, "DAE runner unexpectedly implemented")
    checks.check(audit.get("brown_mcphee_friction_law_implemented") is False, "friction law unexpectedly implemented")
    checks.check(
        audit.get("brown_mcphee_candidate_friction_law_encoded") is True,
        "candidate friction law not encoded",
    )
    checks.check(
        friction_source_anchor.get("source_text_found") is True,
        "Brown--McPhee source text anchor missing",
    )
    checks.check(
        friction_source_anchor.get("names_velocity_based_continuous_model") is True,
        "source text no longer anchors Brown--McPhee velocity model",
    )
    checks.check(
        friction_source_anchor.get("reports_mu_static_dynamic") is True,
        "source text no longer anchors mu_s/mu_d values",
    )
    checks.check(
        friction_source_anchor.get("reports_reference_step_1e_4") is True,
        "source text no longer anchors TFE reference h=1e-4",
    )
    checks.check(
        friction_source_anchor.get("reports_friction_step_sizes") is True,
        "source text no longer anchors friction step sizes",
    )
    checks.check(
        friction_source_anchor.get("defers_law_details_to_refs_38_39") is True,
        "source text no longer records friction-law detail delegation",
    )
    checks.check(
        audit.get("brown_mcphee_published_formula_structure_encoded") is True,
        "Brown--McPhee published-formula structure not encoded",
    )
    checks.check(
        audit.get("brown_mcphee_source_code_equivalent_law") is False,
        "Brown--McPhee source-code equivalence overclaimed",
    )
    checks.check(
        audit.get("brown_mcphee_transition_velocity_policy_resolved_from_source") is False,
        "Brown--McPhee transition velocity unexpectedly marked resolved",
    )
    checks.check(
        "tau = -R N" in friction_formula_boundary.get("encoded_candidate_formula", ""),
        "encoded Brown--McPhee candidate formula missing",
    )
    encoded_parameters = friction_formula_boundary.get("encoded_parameters", {})
    checks.check(encoded_parameters.get("mu_static") == 0.3, "encoded mu_static changed")
    checks.check(encoded_parameters.get("mu_dynamic") == 0.2, "encoded mu_dynamic changed")
    checks.check(encoded_parameters.get("hinge_pin_radius_m") == 0.5, "encoded hinge radius changed")
    checks.check(
        len(friction_formula_boundary.get("missing_for_source_policy_equivalence", [])) >= 4,
        "Brown--McPhee source-equivalence missing-work list too short",
    )
    checks.check(
        audit.get("candidate_friction_law_provenance")
        == "v022_revolute_brown_mcphee_surrogate_not_source_policy_equivalent",
        "candidate friction provenance changed",
    )
    checks.check(
        audit.get("tfe_newmark_trapezoidal_source_policy_runners_implemented") is False,
        "TFE/Newmark/trapezoidal runners unexpectedly implemented",
    )
    checks.check(audit.get("source_error_norm_and_output_policy_encoded") is True, "source output policy not encoded")
    checks.check(
        audit.get("frictional_planar_candidate_rhs_smoke_implemented") is True,
        "frictional candidate RHS smoke missing",
    )
    checks.check(audit.get("source_policy_rows_completed") == 0, "source-policy rows unexpectedly completed")
    checks.check(
        preflight.get("schema") == "tfe-source-policy-runner-equivalence-preflight-v1",
        "runner-equivalence preflight schema changed",
    )
    checks.check(
        preflight.get("status") == "preflight_ready_runner_equivalence_open",
        "runner-equivalence preflight status changed",
    )
    checks.check(preflight.get("closed_precondition_count") == 25, "runner-equivalence precondition count changed")
    checks.check(preflight.get("open_blocker_count") == 6, "runner-equivalence blocker count changed")
    checks.check(
        preflight.get("source_policy_rows_closed_by_preflight") == 0,
        "runner-equivalence preflight overclosed rows",
    )
    checks.check(
        preflight.get("source_policy_dae_runner_equivalent") is False,
        "runner-equivalence preflight overclaims DAE equivalence",
    )
    checks.check(
        preflight.get("pendulum_dae_runner_implemented") is False,
        "runner-equivalence preflight overclaims pendulum DAE runner",
    )
    checks.check(
        preflight.get("source_policy_absolute_coordinate_dae_runner_contract_present")
        is True,
        "runner-equivalence preflight lost source-policy DAE runner contract marker",
    )
    checks.check(
        preflight.get("source_policy_absolute_coordinate_dae_runner_implemented")
        is False,
        "runner-equivalence preflight overclaims source-policy DAE runner implementation",
    )
    checks.check(
        preflight.get("source_policy_method_runner_contract_present") is True,
        "runner-equivalence preflight lost source-policy method contract marker",
    )
    checks.check(
        preflight.get("source_policy_tfe_newmark_trapezoidal_method_runners_implemented")
        is False,
        "runner-equivalence preflight overclaims source-policy method runners",
    )
    checks.check(
        preflight.get(
            "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_contract_present"
        )
        is True,
        "runner-equivalence preflight lost source-policy Gauss6 DAE contract marker",
    )
    checks.check(
        preflight.get(
            "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_implemented"
        )
        is False,
        "runner-equivalence preflight overclaims source-policy Gauss6 DAE runner",
    )
    checks.check(
        preflight.get("brown_mcphee_source_code_equivalent_law") is False,
        "runner-equivalence preflight overclaims Brown--McPhee source-code law",
    )
    checks.check(
        preflight.get("tfe_newmark_trapezoidal_source_policy_runners_implemented") is False,
        "runner-equivalence preflight overclaims TFE/Newmark/trapezoidal source-policy runners",
    )
    checks.check(
        preflight.get("gauss6_fullva_source_policy_runner_implemented") is False,
        "runner-equivalence preflight overclaims Gauss6 source-policy runner",
    )
    checks.check(
        preflight.get("source_grid_policy_resolved_for_full_T10") is False,
        "runner-equivalence preflight overcloses full T=10 grid policy",
    )
    checks.check(
        preflight.get("source_grid_policy_resolved_for_exact_T_compatible_rows") is True,
        "runner-equivalence preflight lost exact-T subset grid policy",
    )
    checks.check(
        preflight.get("can_close_tfe_lane_from_preflight") is False,
        "runner-equivalence preflight overcloses TFE lane",
    )
    checks.check(
        preflight.get("b4_b7_can_close_from_preflight") is False,
        "runner-equivalence preflight overcloses B4/B7",
    )
    checks.check(preflight.get("heavy_numerical_run_invoked") is False, "runner-equivalence preflight invoked heavy run")
    checks.check(preflight.get("run_v047_invoked") is False, "runner-equivalence preflight invoked run_v047")
    checks.check(preflight.get("v048_runner_invoked") is False, "runner-equivalence preflight invoked v048 runner")
    expected_precondition_ids = {
        "source_policy_spec_extracted",
        "source_pendulum_parameter_model_implemented",
        "source_output_error_policy_encoded",
        "absolute_coordinate_dae_residual_smoke_implemented",
        "absolute_coordinate_planar_lift_trajectory_probe_implemented",
        "bounded_absolute_coordinate_dae_trajectory_runner_implemented",
        "monolithic_absolute_coordinate_dae_candidate_runner_implemented",
        "source_policy_absolute_coordinate_dae_runner_contract_present",
        "dae_trajectory_bridge_contract_implemented",
        "candidate_frictional_dae_trajectory_contract_implemented",
        "source_reference_full_T10_h1e4_probe_completed",
        "newmark_trapezoidal_candidate_runner_smoke_implemented",
        "tfe_m1_m2_m3_candidate_runner_smoke_implemented",
        "source_method_candidate_runner_contract_implemented",
        "source_policy_tfe_newmark_trapezoidal_method_runner_contract_present",
        "tfe_appendix_b_coefficient_certificate_checked",
        "bounded_source_policy_runner_api_implemented",
        "active_tfe_b2_full_T10_coarse_candidate_probe_implemented",
        "active_tfe_b2_source_reference_full_T10_candidate_probe_implemented",
        "tfe_m3_full_T10_coarse_formula_probe_implemented",
        "gauss6_source_pendulum_candidate_smoke_implemented",
        "gauss6_fullva_dae_candidate_contract_implemented",
        "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_contract_present",
        "same_test_candidate_work_precision_available",
        "exact_T_compatible_grid_subset_policy_resolved",
    }
    precondition_rows = preflight.get("closed_preconditions", [])
    checks.check(
        {item.get("id") for item in precondition_rows} == expected_precondition_ids,
        "runner-equivalence precondition ids changed",
    )
    checks.check(
        all(item.get("status") is True for item in precondition_rows),
        "runner-equivalence precondition unexpectedly open",
    )
    expected_blocker_ids = {
        "brown_mcphee_source_code_equivalent_law_open",
        "pendulum_absolute_coordinate_source_policy_dae_runner_missing",
        "tfe_newmark_trapezoidal_source_policy_method_runners_missing",
        "gauss6_fullva_absolute_coordinate_source_policy_runner_missing",
        "full_T10_source_grid_endpoint_policy_open",
        "accepted_source_policy_work_precision_rows_not_executed_or_bound",
    }
    blocker_rows = preflight.get("open_blockers", [])
    checks.check(
        {item.get("id") for item in blocker_rows} == expected_blocker_ids,
        "runner-equivalence blocker ids changed",
    )
    checks.check(
        all(item.get("status") == "open" for item in blocker_rows),
        "runner-equivalence blocker unexpectedly closed",
    )

    checks.check(values.get("mass_kg") == body.get("mass_kg") == 10.0, "mass changed")
    checks.check(values.get("length_m") == body.get("length_m") == 2.0, "length changed")
    checks.check(values.get("hinge_pin_radius_m") == body.get("hinge_pin_radius_m") == 0.5, "hinge radius changed")
    checks.check(values.get("center_of_mass_x_m") == body.get("center_of_mass_x_m") == 3.09, "cmx changed")
    checks.check(values.get("mu_static") == friction.get("mu_static") == 0.3, "mu_static changed")
    checks.check(values.get("mu_dynamic") == friction.get("mu_dynamic") == 0.2, "mu_dynamic changed")
    checks.check(values.get("gravity_axis") == spec.get("source_policy", {}).get("gravity_axis") == "-Y", "gravity axis changed")
    checks.check(values.get("inertia_kg_m2") == body.get("inertia_kg_m2"), "inertia changed")

    checks.check(set(reductions) == {"x", "y", "z"}, "candidate axis set changed")
    checks.check(reductions.get("x", {}).get("nondegenerate_frictionless_planar_candidate") is False, "x axis degeneracy changed")
    checks.check(reductions.get("y", {}).get("nondegenerate_frictionless_planar_candidate") is False, "y axis degeneracy changed")
    checks.check(reductions.get("z", {}).get("nondegenerate_frictionless_planar_candidate") is True, "z axis should be nondegenerate")
    checks.check(math.isclose(reductions.get("z", {}).get("parallel_axis_inertia_about_pin"), 95.509, rel_tol=0.0, abs_tol=1e-12), "z inertia changed")
    checks.check(math.isclose(reductions.get("z", {}).get("gravity_torque_scale"), 303.129, rel_tol=0.0, abs_tol=1e-12), "z torque scale changed")

    checks.check(smoke.get("h") == 1.0e-3, "smoke h changed")
    checks.check(smoke.get("steps") == 10, "smoke step count changed")
    checks.check(math.isfinite(float(smoke.get("theta_final"))), "theta final not finite")
    checks.check(math.isfinite(float(smoke.get("omega_final"))), "omega final not finite")
    checks.check(abs(float(smoke.get("energy_delta"))) < 1.0e-11, "frictionless smoke energy drift too large")

    checks.check(audit.get("source_output_policy", {}).get("coordinate_error_order_q"), "coordinate output policy missing")
    checks.check(audit.get("source_output_policy", {}).get("velocity_error_order_v"), "velocity output policy missing")
    checks.check(audit.get("source_output_policy", {}).get("Frobenius_error_norm_eta"), "Frobenius output policy missing")
    checks.check(audit.get("source_output_policy", {}).get("mechanical_energy_deviation"), "energy output policy missing")
    checks.check(math.isclose(float(metric_smoke.get("coordinate_error_q")), 0.1, rel_tol=0.0, abs_tol=1e-12), "metric coordinate smoke changed")
    checks.check(math.isclose(float(metric_smoke.get("velocity_error_v")), 0.2, rel_tol=0.0, abs_tol=1e-12), "metric velocity smoke changed")
    checks.check(math.isfinite(float(metric_smoke.get("frobenius_error_norm_eta"))), "metric Frobenius eta not finite")
    checks.check(math.isfinite(float(metric_smoke.get("mechanical_energy_deviation"))), "metric energy deviation not finite")

    checks.check(friction_torque_smoke.get("dissipative_sign_check") is True, "candidate friction sign check failed")
    checks.check(float(friction_torque_smoke.get("torque_at_positive_omega")) < 0.0, "positive-omega torque should oppose motion")
    checks.check(float(friction_torque_smoke.get("torque_at_negative_omega")) > 0.0, "negative-omega torque should oppose motion")
    checks.check(abs(float(friction_torque_smoke.get("torque_at_zero_omega"))) < 1.0e-14, "zero-omega torque should vanish")
    checks.check(frictional_smoke.get("h") == 1.0e-3, "frictional smoke h changed")
    checks.check(frictional_smoke.get("steps") == 10, "frictional smoke step count changed")
    checks.check(math.isfinite(float(frictional_smoke.get("theta_final"))), "frictional theta final not finite")
    checks.check(math.isfinite(float(frictional_smoke.get("omega_final"))), "frictional omega final not finite")
    checks.check(float(frictional_smoke.get("max_candidate_friction_power")) <= 1.0e-12, "candidate friction power should be nonpositive")
    checks.check(float(frictional_smoke.get("energy_delta")) < 0.0, "candidate friction smoke should dissipate energy")

    for label, row in [
        ("frictionless absolute", absolute_smoke),
        ("frictional absolute", absolute_frictional_smoke),
    ]:
        checks.check(row.get("source_policy_dae_runner_equivalent") is False, f"{label} smoke overclaims source-policy equivalence")
        checks.check(float(row.get("hinge_position_constraint_norm")) < 1.0e-13, f"{label} hinge position residual too large")
        checks.check(float(row.get("hinge_velocity_constraint_norm")) < 1.0e-13, f"{label} hinge velocity residual too large")
        checks.check(float(row.get("rotation_orthogonality_residual_norm")) < 1.0e-13, f"{label} rotation residual too large")
        checks.check(float(row.get("angular_velocity_axis_constraint_norm")) < 1.0e-13, f"{label} angular velocity axis residual too large")
        checks.check(float(row.get("translational_balance_residual_norm")) < 1.0e-12, f"{label} translational residual too large")
        checks.check(float(row.get("axis_projected_rotational_residual_abs")) < 1.0e-12, f"{label} axis rotational residual too large")
    checks.check(absolute_smoke.get("frictional") is False, "frictionless absolute smoke mislabeled")
    checks.check(absolute_frictional_smoke.get("frictional") is True, "frictional absolute smoke mislabeled")
    checks.check(
        float(absolute_frictional_smoke.get("candidate_friction_power")) < 0.0,
        "absolute frictional smoke should dissipate power",
    )

    rows = source_output_time_smoke.get("rows", [])
    checks.check(source_output_time_smoke.get("source_policy_time_integration_runner_equivalent") is False, "time smoke overclaims source-policy equivalence")
    checks.check(source_output_time_smoke.get("t_final") == 0.1, "time smoke t_final changed")
    checks.check(source_output_time_smoke.get("reference_h") == 0.00025, "time smoke reference h changed")
    checks.check(source_output_time_smoke.get("comparison_h") == [0.01, 0.005, 0.0025], "time smoke h-grid changed")
    checks.check(len(rows) == 2, "time smoke row count changed")
    checks.check(
        {row.get("case_id") for row in rows}
        == {"frictionless_pendulum_smoke", "frictional_pendulum_candidate_smoke"},
        "time smoke cases changed",
    )
    for row in rows:
        checks.check(row.get("coordinate_error_decreased") is True, f"{row.get('case_id')} coordinate error not decreasing")
        checks.check(row.get("velocity_error_decreased") is True, f"{row.get('case_id')} velocity error not decreasing")
        checks.check(row.get("frobenius_error_decreased") is True, f"{row.get('case_id')} Frobenius error not decreasing")
        checks.check(len(row.get("metrics", [])) == 3, f"{row.get('case_id')} metric row count changed")
        for key in ["coordinate_pairwise_orders", "velocity_pairwise_orders", "frobenius_pairwise_orders"]:
            orders = row.get(key, [])
            checks.check(len(orders) == 2, f"{row.get('case_id')} {key} length changed")
            for order in orders:
                checks.check(order is not None and 3.5 <= float(order) <= 4.5, f"{row.get('case_id')} {key} not RK4-like")

    reference_rows = source_reference_policy_smoke.get("rows", [])
    checks.check(
        source_reference_policy_smoke.get("source_reference_solution_policy_smoke_implemented") is True,
        "source reference policy smoke not marked implemented",
    )
    checks.check(source_reference_policy_smoke.get("source_reference_h") == 0.0001, "source reference h changed")
    checks.check(source_reference_policy_smoke.get("check_h") == 0.00005, "source reference check h changed")
    checks.check(source_reference_policy_smoke.get("t_final") == 0.01, "source reference smoke t_final changed")
    checks.check(
        source_reference_policy_smoke.get("bounded_reference_smoke_not_full_T10") is True,
        "source reference smoke lost bounded marker",
    )
    checks.check(
        source_reference_policy_smoke.get("default_1e_4_campaign_invoked") is False,
        "source reference smoke invoked default 1e-4 campaign",
    )
    checks.check(source_reference_policy_smoke.get("source_policy_rows_completed") == 0, "source reference smoke overclosed rows")
    checks.check(len(reference_rows) == 2, "source reference smoke row count changed")
    for row in reference_rows:
        checks.check(row.get("finite_source_reference_state") is True, f"{row.get('case_id')} source reference state not finite")
        checks.check(row.get("source_reference_steps") == 100, f"{row.get('case_id')} source reference step count changed")
        checks.check(row.get("check_steps") == 200, f"{row.get('case_id')} check step count changed")
        metrics = row.get("metrics_vs_check_h", {})
        checks.check(float(metrics.get("coordinate_error_q")) < 1.0e-12, f"{row.get('case_id')} reference coordinate mismatch too large")
        checks.check(float(metrics.get("velocity_error_v")) < 1.0e-12, f"{row.get('case_id')} reference velocity mismatch too large")

    checks.check(
        source_reference_full_t10_probe.get("schema") == "tfe-source-reference-full-t10-probe-v1",
        "source reference full T=10 probe schema changed",
    )
    checks.check(
        source_reference_full_t10_probe.get("status")
        == "full_T10_frictionless_source_reference_probe_not_method_reproduction",
        "source reference full T=10 probe status changed",
    )
    checks.check(
        source_reference_full_t10_probe.get("case_id") == "frictionless_pendulum_reference_full_T10_probe",
        "source reference full T=10 probe case changed",
    )
    checks.check(source_reference_full_t10_probe.get("frictional") is False, "source reference full T=10 probe friction policy changed")
    checks.check(source_reference_full_t10_probe.get("source_reference_h") == 0.0001, "source reference full T=10 h changed")
    checks.check(source_reference_full_t10_probe.get("check_h") == 0.00005, "source reference full T=10 check h changed")
    checks.check(source_reference_full_t10_probe.get("t_final") == 10.0, "source reference full T=10 horizon changed")
    checks.check(
        source_reference_full_t10_probe.get("source_reference_steps") == 100000,
        "source reference full T=10 source step count changed",
    )
    checks.check(
        source_reference_full_t10_probe.get("check_steps") == 200000,
        "source reference full T=10 check step count changed",
    )
    checks.check(
        source_reference_full_t10_probe.get("finite_source_reference_state") is True,
        "source reference full T=10 state not finite",
    )
    full_t10_metrics = source_reference_full_t10_probe.get("metrics_vs_check_h", {})
    checks.check(
        float(full_t10_metrics.get("coordinate_error_q")) < 1.0e-10,
        "source reference full T=10 coordinate mismatch too large",
    )
    checks.check(
        float(full_t10_metrics.get("velocity_error_v")) < 1.0e-10,
        "source reference full T=10 velocity mismatch too large",
    )
    checks.check(
        source_reference_full_t10_probe.get("source_reference_h_1e4_invoked") is True,
        "source reference full T=10 did not invoke h=1e-4 marker",
    )
    checks.check(
        source_reference_full_t10_probe.get("full_T10_source_reference_probe_completed") is True,
        "source reference full T=10 completion marker missing",
    )
    checks.check(
        source_reference_full_t10_probe.get("source_policy_method_runner_equivalent") is False,
        "source reference full T=10 probe overclaims method equivalence",
    )
    checks.check(
        source_reference_full_t10_probe.get("source_policy_rows_completed") == 0,
        "source reference full T=10 probe overcloses source-policy rows",
    )

    comparator_rows = comparator_smoke.get("rows", [])
    checks.check(comparator_smoke.get("source_policy_method_runner_equivalent") is False, "comparator smoke overclaims method equivalence")
    checks.check(comparator_smoke.get("tfe_m1_m2_m3_source_policy_runners_implemented") is False, "comparator smoke overclaims TFE runners")
    checks.check(comparator_smoke.get("candidate_methods") == ["Newmark_beta", "trapezoidal"], "candidate comparator methods changed")
    checks.check(comparator_smoke.get("comparison_h") == [0.02, 0.01, 0.005], "comparator h-grid changed")
    checks.check(len(comparator_rows) == 4, "comparator smoke row count changed")
    for row in comparator_rows:
        checks.check(row.get("source_policy_method_runner_equivalent") is False, f"{row.get('method')} row overclaims equivalence")
        checks.check(row.get("coordinate_error_decreased") is True, f"{row.get('method')} coordinate error not decreasing")
        checks.check(row.get("velocity_error_decreased") is True, f"{row.get('method')} velocity error not decreasing")
        checks.check(float(row.get("max_newton_residual_norm")) < 1.0e-10, f"{row.get('method')} residual too large")
        for key in ["coordinate_pairwise_orders", "velocity_pairwise_orders"]:
            orders = row.get(key, [])
            checks.check(len(orders) == 2, f"{row.get('method')} {key} length changed")
            for order in orders:
                checks.check(order is not None and 1.75 <= float(order) <= 2.25, f"{row.get('method')} {key} not second-order")

    tfe_candidate_rows = tfe_candidate_smoke.get("rows", [])
    checks.check(
        tfe_candidate_smoke.get("tfe_m1_m2_m3_candidate_runner_smoke_implemented") is True,
        "TFE candidate smoke does not mark candidate runners implemented",
    )
    checks.check(
        tfe_candidate_smoke.get("tfe_m1_m2_m3_source_policy_runners_implemented") is False,
        "TFE candidate smoke overclaims source-policy runners",
    )
    checks.check(
        tfe_candidate_smoke.get("source_policy_method_runner_equivalent") is False,
        "TFE candidate smoke overclaims method equivalence",
    )
    checks.check(
        tfe_candidate_smoke.get("candidate_methods") == ["TFE_m1", "TFE_m2", "TFE_m3_GL"],
        "TFE candidate methods changed",
    )
    checks.check(tfe_candidate_smoke.get("t_final") == 1.0, "TFE candidate t_final changed")
    checks.check(tfe_candidate_smoke.get("reference_h") == 0.00025, "TFE candidate reference h changed")
    checks.check(tfe_candidate_smoke.get("comparison_h") == [0.1, 0.05, 0.025], "TFE candidate h-grid changed")
    checks.check(len(tfe_candidate_rows) == 6, "TFE candidate smoke row count changed")
    for row in tfe_candidate_rows:
        checks.check(row.get("source_policy_method_runner_equivalent") is False, f"{row.get('method')} TFE row overclaims equivalence")
        checks.check(len(row.get("metrics", [])) == 3, f"{row.get('method')} TFE metric row count changed")
        checks.check(float(row.get("max_newton_residual_norm")) < 1.0e-8, f"{row.get('method')} TFE residual too large")
        for key in ["coordinate_pairwise_orders", "velocity_pairwise_orders"]:
            orders = row.get(key, [])
            checks.check(len(orders) == 2, f"{row.get('method')} TFE {key} length changed")
            for order in orders:
                checks.check(order is not None and math.isfinite(float(order)), f"{row.get('method')} TFE {key} not finite")
        if row.get("case_id") == "frictionless_pendulum_smoke":
            velocity_orders = [float(item) for item in row.get("velocity_pairwise_orders", [])]
            if row.get("method") == "TFE_m1":
                checks.check(min(velocity_orders) > 1.0, "frictionless TFE_m1 velocity order smoke too low")
            elif row.get("method") == "TFE_m2":
                checks.check(min(velocity_orders) > 2.5, "frictionless TFE_m2 velocity order smoke too low")
            elif row.get("method") == "TFE_m3_GL":
                checks.check(min(velocity_orders) > 4.5, "frictionless TFE_m3 velocity order smoke too low")

    method_contract_rows = method_candidate_contract.get("rows", [])
    checks.check(
        method_candidate_contract.get("schema")
        == "tfe-source-method-candidate-runner-contract-smoke-v1",
        "source-method candidate contract schema changed",
    )
    checks.check(
        method_candidate_contract.get("runner_api") == "source_method_candidate_runner_contract_smoke",
        "source-method candidate contract API changed",
    )
    checks.check(
        method_candidate_contract.get("runner_scope")
        == "candidate_method_dispatch_and_parameter_contract_not_source_policy",
        "source-method candidate contract scope changed",
    )
    checks.check(
        method_candidate_contract.get("source_method_candidate_runner_contract_implemented")
        is True,
        "source-method candidate contract implementation marker missing",
    )
    checks.check(
        method_candidate_contract.get("source_method_candidate_runner_contract_complete") is True,
        "source-method candidate contract completion marker missing",
    )
    checks.check(
        method_candidate_contract.get("method_count") == 5
        and method_candidate_contract.get("row_count") == 5
        and len(method_contract_rows) == 5,
        "source-method candidate contract row count changed",
    )
    checks.check(
        method_candidate_contract.get("all_step_states_finite") is True,
        "source-method candidate contract has nonfinite rows",
    )
    checks.check(
        method_candidate_contract.get("all_candidate_residuals_below_1e_8") is True,
        "source-method candidate contract residual flag failed",
    )
    checks.check(
        method_candidate_contract.get("source_policy_rows_completed") == 0,
        "source-method candidate contract overcloses source-policy rows",
    )
    checks.check(
        method_candidate_contract.get("source_policy_method_runner_equivalent") is False,
        "source-method candidate contract overclaims method equivalence",
    )
    checks.check(
        method_candidate_contract.get("source_policy_dae_runner_equivalent") is False,
        "source-method candidate contract overclaims DAE equivalence",
    )
    checks.check(
        method_candidate_contract.get("accepted_use")
        == "candidate_method_dispatch_contract_not_source_policy",
        "source-method candidate contract accepted-use changed",
    )
    checks.check(
        method_candidate_contract.get("appendix_b_certificate_checked") is True,
        "source-method candidate contract lost Appendix-B check",
    )
    expected_method_contract_methods = {
        "Newmark_beta",
        "trapezoidal",
        "TFE_m1",
        "TFE_m2",
        "TFE_m3_GL",
    }
    checks.check(
        {row.get("source_method") for row in method_contract_rows} == expected_method_contract_methods,
        "source-method candidate contract methods changed",
    )
    for row in method_contract_rows:
        checks.check(row.get("step_states_finite") is True, f"{row.get('source_method')} contract state not finite")
        checks.check(
            row.get("candidate_step_residual_below_1e_8") is True,
            f"{row.get('source_method')} contract residual too large",
        )
        checks.check(
            row.get("source_method_dispatch_available") is True,
            f"{row.get('source_method')} dispatch marker missing",
        )
        checks.check(
            row.get("source_policy_method_runner_equivalent") is False,
            f"{row.get('source_method')} contract overclaims method equivalence",
        )
        checks.check(
            row.get("source_policy_dae_runner_equivalent") is False,
            f"{row.get('source_method')} contract overclaims DAE equivalence",
        )
        checks.check(
            row.get("source_policy_row_completed") is False,
            f"{row.get('source_method')} contract overcloses row",
        )
        checks.check(
            row.get("accepted_use") == "candidate_method_dispatch_contract_not_source_policy",
            f"{row.get('source_method')} contract accepted-use changed",
        )

    source_policy_method_rows = source_policy_method_runner_contract.get("rows", [])
    checks.check(
        source_policy_method_runner_contract.get("schema")
        == "tfe-source-policy-method-runners-contract-v1",
        "source-policy method-runner contract schema changed",
    )
    checks.check(
        source_policy_method_runner_contract.get("runner_api")
        == "source_policy_tfe_newmark_trapezoidal_method_runners",
        "source-policy method-runner contract API changed",
    )
    checks.check(
        source_policy_method_runner_contract.get(
            "source_policy_method_runner_contract_present"
        )
        is True,
        "source-policy method-runner contract marker missing",
    )
    checks.check(
        source_policy_method_runner_contract.get(
            "source_policy_tfe_newmark_trapezoidal_method_runners_implemented"
        )
        is False,
        "source-policy method-runner contract overclaims implementation",
    )
    checks.check(
        source_policy_method_runner_contract.get("method_count") == 5
        and source_policy_method_runner_contract.get("row_count") == 5
        and len(source_policy_method_rows) == 5,
        "source-policy method-runner contract row count changed",
    )
    checks.check(
        source_policy_method_runner_contract.get("source_policy_rows_completed") == 0,
        "source-policy method-runner contract overcloses rows",
    )
    checks.check(
        source_policy_method_runner_contract.get("source_policy_method_runner_equivalent")
        is False
        and source_policy_method_runner_contract.get("source_policy_dae_runner_equivalent")
        is False,
        "source-policy method-runner contract overclaims equivalence",
    )
    checks.check(
        source_policy_method_runner_contract.get("candidate_contract_api")
        == "source_method_candidate_runner_contract_smoke",
        "source-policy method-runner contract candidate binding changed",
    )
    checks.check(
        source_policy_method_runner_contract.get("all_step_states_finite") is True
        and source_policy_method_runner_contract.get("all_candidate_residuals_below_1e_8")
        is True,
        "source-policy method-runner contract finite/residual flags changed",
    )
    checks.check(
        {row.get("source_method") for row in source_policy_method_rows}
        == expected_method_contract_methods,
        "source-policy method-runner contract methods changed",
    )
    for row in source_policy_method_rows:
        checks.check(
            row.get("source_policy_method_runner_contract_present") is True,
            f"{row.get('source_method')} source-policy method contract marker missing",
        )
        checks.check(
            row.get("source_policy_tfe_newmark_trapezoidal_method_runners_implemented")
            is False,
            f"{row.get('source_method')} source-policy method contract overclaims implementation",
        )
        checks.check(
            row.get("source_policy_method_runner_equivalent") is False
            and row.get("source_policy_dae_runner_equivalent") is False,
            f"{row.get('source_method')} source-policy method contract overclaims equivalence",
        )
        checks.check(
            row.get("source_policy_row_completed") is False,
            f"{row.get('source_method')} source-policy method contract overcloses row",
        )
        checks.check(
            row.get("accepted_use")
            == "method_runner_contract_entrypoint_only_not_source_policy",
            f"{row.get('source_method')} source-policy method contract accepted-use changed",
        )

    gauss6_rows = gauss6_smoke.get("rows", [])
    checks.check(
        gauss6_smoke.get("runner_api") == "source_gauss6_fullva_candidate_runner_smoke",
        "Gauss6 candidate runner API changed",
    )
    checks.check(
        gauss6_smoke.get("runner_scope")
        == "source_pendulum_planar_gauss6_candidate_not_fullva_dae_source_policy",
        "Gauss6 candidate runner scope changed",
    )
    checks.check(
        gauss6_smoke.get("gauss6_fullva_source_pendulum_candidate_smoke_implemented") is True,
        "Gauss6 candidate smoke does not mark implementation",
    )
    checks.check(
        gauss6_smoke.get("gauss6_fullva_absolute_coordinate_source_policy_runner_implemented") is False,
        "Gauss6 candidate smoke overclaims source-policy runner implementation",
    )
    checks.check(
        gauss6_smoke.get("gauss6_fullva_on_source_pendulum_implemented") is True,
        "Gauss6 candidate legacy alias changed",
    )
    checks.check(
        gauss6_smoke.get("fullva_dae_source_policy_equivalent") is False,
        "Gauss6 candidate overclaims FullVA DAE source-policy equivalence",
    )
    checks.check(
        gauss6_smoke.get("source_policy_method_runner_equivalent") is False,
        "Gauss6 candidate overclaims source-policy method equivalence",
    )
    checks.check(
        gauss6_smoke.get("source_policy_rows_completed") == 0,
        "Gauss6 candidate overcloses source-policy rows",
    )
    checks.check(
        gauss6_smoke.get("external_superiority_claim_allowed") is False,
        "Gauss6 candidate overclaims external superiority",
    )
    checks.check(gauss6_smoke.get("candidate_methods") == ["Gauss6_FullVA"], "Gauss6 candidate method set changed")
    checks.check(gauss6_smoke.get("t_final") == 1.0, "Gauss6 candidate t_final changed")
    checks.check(gauss6_smoke.get("reference_h") == 0.00025, "Gauss6 candidate reference h changed")
    checks.check(gauss6_smoke.get("comparison_h") == [0.1, 0.05, 0.025], "Gauss6 candidate h-grid changed")
    checks.check(gauss6_smoke.get("row_count") == 2, "Gauss6 candidate row count changed")
    checks.check(len(gauss6_rows) == 2, "Gauss6 candidate row list changed")
    for row in gauss6_rows:
        checks.check(
            row.get("accepted_use") == "gauss6_source_pendulum_candidate_not_source_policy",
            f"{row.get('case_id')} Gauss6 allowed-use changed",
        )
        checks.check(row.get("method") == "Gauss6_FullVA", f"{row.get('case_id')} Gauss6 method changed")
        checks.check(row.get("expected_order") == 6, f"{row.get('case_id')} Gauss6 expected order changed")
        checks.check(
            row.get("source_policy_method_runner_equivalent") is False,
            f"{row.get('case_id')} Gauss6 overclaims method equivalence",
        )
        checks.check(
            row.get("fullva_dae_source_policy_equivalent") is False,
            f"{row.get('case_id')} Gauss6 overclaims DAE equivalence",
        )
        checks.check(row.get("source_policy_row_completed") is False, f"{row.get('case_id')} Gauss6 overcloses row")
        checks.check(row.get("coordinate_error_decreased") is True, f"{row.get('case_id')} Gauss6 coordinate error not decreasing")
        checks.check(row.get("velocity_error_decreased") is True, f"{row.get('case_id')} Gauss6 velocity error not decreasing")
        checks.check(row.get("frobenius_error_decreased") is True, f"{row.get('case_id')} Gauss6 Frobenius error not decreasing")
        checks.check(len(row.get("metrics", [])) == 3, f"{row.get('case_id')} Gauss6 metric row count changed")
        checks.check(float(row.get("max_newton_residual_norm")) < 1.0e-8, f"{row.get('case_id')} Gauss6 residual too large")
        for metric in row.get("metrics", []):
            checks.check(math.isfinite(float(metric.get("coordinate_error_q"))), f"{row.get('case_id')} Gauss6 coordinate error not finite")
            checks.check(math.isfinite(float(metric.get("velocity_error_v"))), f"{row.get('case_id')} Gauss6 velocity error not finite")
            checks.check(math.isfinite(float(metric.get("frobenius_error_norm_eta"))), f"{row.get('case_id')} Gauss6 Frobenius error not finite")
        for key in ["coordinate_pairwise_orders", "velocity_pairwise_orders", "frobenius_pairwise_orders"]:
            orders = row.get(key, [])
            checks.check(len(orders) == 2, f"{row.get('case_id')} Gauss6 {key} length changed")
            for order in orders:
                checks.check(order is not None and math.isfinite(float(order)), f"{row.get('case_id')} Gauss6 {key} not finite")
        if row.get("case_id") == "frictionless_pendulum_smoke":
            velocity_orders = [float(item) for item in row.get("velocity_pairwise_orders", [])]
            coordinate_orders = [float(item) for item in row.get("coordinate_pairwise_orders", [])]
            checks.check(min(velocity_orders) > 5.5, "frictionless Gauss6 velocity order smoke too low")
            checks.check(min(coordinate_orders) > 5.5, "frictionless Gauss6 coordinate order smoke too low")

    gauss6_contract_rows = gauss6_dae_candidate_contract.get("rows", [])
    checks.check(
        gauss6_dae_candidate_contract.get("schema")
        == "tfe-gauss6-fullva-dae-candidate-contract-smoke-v1",
        "Gauss6 DAE candidate contract schema changed",
    )
    checks.check(
        gauss6_dae_candidate_contract.get("runner_api")
        == "source_gauss6_fullva_dae_candidate_contract_smoke",
        "Gauss6 DAE candidate contract runner API changed",
    )
    checks.check(
        gauss6_dae_candidate_contract.get("runner_scope")
        == "single_step_gauss6_candidate_lifted_to_absolute_dae_residual_not_source_policy",
        "Gauss6 DAE candidate contract scope changed",
    )
    checks.check(
        gauss6_dae_candidate_contract.get("gauss6_fullva_dae_candidate_contract_implemented")
        is True,
        "Gauss6 DAE candidate contract marker missing",
    )
    checks.check(
        gauss6_dae_candidate_contract.get("row_count") == 1
        and len(gauss6_contract_rows) == 1,
        "Gauss6 DAE candidate contract row count changed",
    )
    checks.check(
        gauss6_dae_candidate_contract.get("source_policy_rows_completed") == 0,
        "Gauss6 DAE candidate contract overcloses source-policy rows",
    )
    checks.check(
        gauss6_dae_candidate_contract.get("source_policy_method_runner_equivalent") is False
        and gauss6_dae_candidate_contract.get("source_policy_dae_runner_equivalent") is False
        and gauss6_dae_candidate_contract.get("fullva_dae_source_policy_equivalent") is False,
        "Gauss6 DAE candidate contract overclaims source-policy equivalence",
    )
    checks.check(
        gauss6_dae_candidate_contract.get("monolithic_absolute_coordinate_dae_time_integrator")
        is False,
        "Gauss6 DAE candidate contract overclaims monolithic integrator",
    )
    checks.check(
        gauss6_dae_candidate_contract.get("accepted_use")
        == "gauss6_fullva_dae_candidate_contract_not_source_policy",
        "Gauss6 DAE candidate contract accepted-use changed",
    )
    checks.check(
        gauss6_dae_candidate_contract.get("all_step_states_finite") is True
        and gauss6_dae_candidate_contract.get("all_candidate_residuals_below_1e_8") is True,
        "Gauss6 DAE candidate contract finite/residual gate changed",
    )
    checks.check(
        float(gauss6_dae_candidate_contract.get("max_candidate_step_residual_norm")) < 1.0e-8,
        "Gauss6 DAE candidate contract residual too large",
    )
    for row in gauss6_contract_rows:
        residual = row.get("absolute_coordinate_dae_residual", {})
        checks.check(
            row.get("source_method") == "Gauss6_FullVA"
            and row.get("expected_order") == 6,
            "Gauss6 DAE candidate row method/order changed",
        )
        checks.check(
            row.get("accepted_use") == "gauss6_fullva_dae_candidate_contract_not_source_policy",
            "Gauss6 DAE candidate row accepted-use changed",
        )
        checks.check(row.get("step_state_finite") is True, "Gauss6 DAE candidate row state nonfinite")
        checks.check(
            row.get("candidate_step_residual_below_1e_8") is True,
            "Gauss6 DAE candidate row residual gate failed",
        )
        checks.check(
            row.get("source_policy_method_runner_equivalent") is False
            and row.get("source_policy_dae_runner_equivalent") is False
            and row.get("fullva_dae_source_policy_equivalent") is False,
            "Gauss6 DAE candidate row overclaims equivalence",
        )
        checks.check(
            row.get("source_policy_row_completed") is False,
            "Gauss6 DAE candidate row overcloses source-policy row",
        )
        for key in [
            "hinge_position_constraint_norm",
            "hinge_velocity_constraint_norm",
            "translational_balance_residual_norm",
            "axis_projected_rotational_residual_abs",
        ]:
            checks.check(
                key in residual and math.isfinite(float(residual.get(key))),
                f"Gauss6 DAE candidate residual missing finite {key}",
            )

    source_policy_gauss6_rows = source_policy_gauss6_dae_runner_contract.get("rows", [])
    checks.check(
        source_policy_gauss6_dae_runner_contract.get("schema")
        == "tfe-source-policy-gauss6-fullva-absolute-coordinate-dae-runner-contract-v1",
        "source-policy Gauss6 DAE runner contract schema changed",
    )
    checks.check(
        source_policy_gauss6_dae_runner_contract.get("runner_api")
        == "source_policy_gauss6_fullva_absolute_coordinate_dae_runner",
        "source-policy Gauss6 DAE runner contract API changed",
    )
    checks.check(
        source_policy_gauss6_dae_runner_contract.get(
            "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_contract_present"
        )
        is True,
        "source-policy Gauss6 DAE runner contract marker missing",
    )
    checks.check(
        source_policy_gauss6_dae_runner_contract.get(
            "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_implemented"
        )
        is False,
        "source-policy Gauss6 DAE runner contract overclaims implementation",
    )
    checks.check(
        source_policy_gauss6_dae_runner_contract.get("row_count") == 1
        and len(source_policy_gauss6_rows) == 1,
        "source-policy Gauss6 DAE runner contract row count changed",
    )
    checks.check(
        source_policy_gauss6_dae_runner_contract.get("source_policy_rows_completed") == 0,
        "source-policy Gauss6 DAE runner contract overcloses rows",
    )
    checks.check(
        source_policy_gauss6_dae_runner_contract.get("source_policy_dae_runner_equivalent")
        is False
        and source_policy_gauss6_dae_runner_contract.get("fullva_dae_source_policy_equivalent")
        is False
        and source_policy_gauss6_dae_runner_contract.get(
            "monolithic_absolute_coordinate_dae_time_integrator"
        )
        is False,
        "source-policy Gauss6 DAE runner contract overclaims equivalence",
    )
    checks.check(
        source_policy_gauss6_dae_runner_contract.get("candidate_contract_api")
        == "source_gauss6_fullva_dae_candidate_contract_smoke",
        "source-policy Gauss6 DAE runner contract candidate binding changed",
    )
    checks.check(
        source_policy_gauss6_dae_runner_contract.get("all_step_states_finite") is True
        and source_policy_gauss6_dae_runner_contract.get(
            "all_candidate_residuals_below_1e_8"
        )
        is True,
        "source-policy Gauss6 DAE runner contract finite/residual flags changed",
    )
    for row in source_policy_gauss6_rows:
        checks.check(
            row.get("source_policy_gauss6_fullva_absolute_coordinate_dae_runner_contract_present")
            is True,
            "source-policy Gauss6 DAE runner row contract marker missing",
        )
        checks.check(
            row.get("source_policy_gauss6_fullva_absolute_coordinate_dae_runner_implemented")
            is False,
            "source-policy Gauss6 DAE runner row overclaims implementation",
        )
        checks.check(
            row.get("source_policy_dae_runner_equivalent") is False
            and row.get("fullva_dae_source_policy_equivalent") is False
            and row.get("monolithic_absolute_coordinate_dae_time_integrator") is False,
            "source-policy Gauss6 DAE runner row overclaims equivalence",
        )
        checks.check(
            row.get("source_policy_row_completed") is False,
            "source-policy Gauss6 DAE runner row overcloses source-policy row",
        )
        checks.check(
            row.get("accepted_use")
            == "gauss6_fullva_dae_runner_contract_entrypoint_only_not_source_policy",
            "source-policy Gauss6 DAE runner row accepted-use changed",
        )

    same_test_rows = same_test_work_precision.get("rows", [])
    checks.check(
        same_test_work_precision.get("runner_api") == "source_pendulum_same_test_work_precision_smoke",
        "same-test work/precision runner API changed",
    )
    checks.check(
        same_test_work_precision.get("runner_scope")
        == "frictionless_source_pendulum_same_grid_candidate_work_precision",
        "same-test work/precision runner scope changed",
    )
    checks.check(
        same_test_work_precision.get("same_test_work_precision_implemented") is True,
        "same-test work/precision implementation marker missing",
    )
    checks.check(same_test_work_precision.get("t_final") == 1.0, "same-test work/precision horizon changed")
    checks.check(same_test_work_precision.get("reference_h") == 0.00025, "same-test work/precision reference h changed")
    checks.check(
        same_test_work_precision.get("comparison_h") == [0.1, 0.05, 0.025],
        "same-test work/precision h-grid changed",
    )
    checks.check(
        same_test_work_precision.get("candidate_methods")
        == ["Newmark_beta", "trapezoidal", "TFE_m1", "TFE_m2", "TFE_m3_GL", "Gauss6_FullVA"],
        "same-test work/precision method list changed",
    )
    checks.check(same_test_work_precision.get("method_count") == 6, "same-test work/precision method count changed")
    checks.check(same_test_work_precision.get("row_count") == 6, "same-test work/precision row count changed")
    checks.check(
        same_test_work_precision.get("source_policy_method_runner_equivalent") is False,
        "same-test work/precision overclaims method equivalence",
    )
    checks.check(
        same_test_work_precision.get("source_policy_rows_completed") == 0,
        "same-test work/precision overcloses source-policy rows",
    )
    checks.check(
        same_test_work_precision.get("external_superiority_claim_allowed") is False,
        "same-test work/precision overclaims external superiority",
    )
    checks.check(len(same_test_rows) == 6, "same-test work/precision row list changed")
    for row in same_test_rows:
        checks.check(
            row.get("accepted_use") == "same_test_candidate_work_precision_not_source_policy",
            f"{row.get('source_method')} same-test accepted-use changed",
        )
        checks.check(row.get("frictional") is False, f"{row.get('source_method')} same-test friction policy changed")
        checks.check(
            row.get("source_policy_method_runner_equivalent") is False,
            f"{row.get('source_method')} same-test overclaims method equivalence",
        )
        checks.check(row.get("source_policy_row_completed") is False, f"{row.get('source_method')} same-test overcloses row")
        checks.check(
            row.get("external_superiority_claim_allowed") is False,
            f"{row.get('source_method')} same-test overclaims external superiority",
        )
        checks.check(row.get("coordinate_error_decreased") is True, f"{row.get('source_method')} same-test coordinate error not decreasing")
        checks.check(row.get("velocity_error_decreased") is True, f"{row.get('source_method')} same-test velocity error not decreasing")
        checks.check(row.get("frobenius_error_decreased") is True, f"{row.get('source_method')} same-test Frobenius error not decreasing")
        checks.check(len(row.get("metrics", [])) == 3, f"{row.get('source_method')} same-test metric row count changed")
        checks.check(float(row.get("max_newton_residual_norm")) < 1.0e-8, f"{row.get('source_method')} same-test residual too large")
        for metric in row.get("metrics", []):
            checks.check(math.isfinite(float(metric.get("runtime_sec"))), f"{row.get('source_method')} same-test runtime missing")
            checks.check(math.isfinite(float(metric.get("velocity_error_v"))), f"{row.get('source_method')} same-test velocity error missing")
            checks.check(math.isfinite(float(metric.get("work_units_newton_iterations"))), f"{row.get('source_method')} same-test work missing")
        velocity_orders = [float(item) for item in row.get("velocity_pairwise_orders", [])]
        if row.get("source_method") in {"Newmark_beta", "trapezoidal"}:
            checks.check(min(velocity_orders) > 1.75, f"{row.get('source_method')} same-test velocity order too low")
        if row.get("source_method") == "TFE_m2":
            checks.check(min(velocity_orders) > 2.5, "same-test TFE m=2 velocity order too low")
        if row.get("source_method") == "TFE_m3_GL":
            checks.check(min(velocity_orders) > 4.5, "same-test TFE m=3 velocity order too low")
        if row.get("source_method") == "Gauss6_FullVA":
            checks.check(min(velocity_orders) > 5.5, "same-test Gauss6 velocity order too low")

    absolute_lift_rows = absolute_lift_probe.get("rows", [])
    checks.check(
        absolute_lift_probe.get("runner_api") == "absolute_coordinate_planar_lift_trajectory_probe",
        "absolute-coordinate planar-lift API changed",
    )
    checks.check(
        absolute_lift_probe.get("runner_scope")
        == "planar_candidate_trajectory_lifted_to_absolute_coordinate_residuals_not_source_policy",
        "absolute-coordinate planar-lift scope changed",
    )
    checks.check(
        absolute_lift_probe.get("absolute_coordinate_planar_lift_trajectory_probe_implemented") is True,
        "absolute-coordinate planar-lift implementation marker missing",
    )
    checks.check(
        absolute_lift_probe.get("monolithic_absolute_coordinate_dae_time_integrator") is False,
        "absolute-coordinate planar-lift overclaims monolithic DAE integration",
    )
    checks.check(
        absolute_lift_probe.get("source_policy_dae_runner_equivalent") is False,
        "absolute-coordinate planar-lift overclaims source-policy DAE equivalence",
    )
    checks.check(
        absolute_lift_probe.get("source_policy_method_runner_equivalent") is False,
        "absolute-coordinate planar-lift overclaims source-policy method equivalence",
    )
    checks.check(
        absolute_lift_probe.get("source_policy_rows_completed") == 0,
        "absolute-coordinate planar-lift overcloses source-policy rows",
    )
    checks.check(
        absolute_lift_probe.get("external_superiority_claim_allowed") is False,
        "absolute-coordinate planar-lift overclaims external superiority",
    )
    checks.check(absolute_lift_probe.get("t_final") == 1.0, "absolute-coordinate planar-lift horizon changed")
    checks.check(
        absolute_lift_probe.get("comparison_h") == [0.1, 0.05, 0.025],
        "absolute-coordinate planar-lift h-grid changed",
    )
    checks.check(absolute_lift_probe.get("reference_h") == 0.00025, "absolute-coordinate planar-lift reference h changed")
    checks.check(absolute_lift_probe.get("case_count") == 2, "absolute-coordinate planar-lift case count changed")
    checks.check(absolute_lift_probe.get("method_count") == 6, "absolute-coordinate planar-lift method count changed")
    checks.check(absolute_lift_probe.get("row_count") == 12, "absolute-coordinate planar-lift row count changed")
    checks.check(absolute_lift_probe.get("metric_row_count") == 36, "absolute-coordinate planar-lift metric row count changed")
    for key in [
        "max_hinge_position_constraint_norm",
        "max_hinge_velocity_constraint_norm",
        "max_translational_balance_residual_norm",
        "max_axis_projected_rotational_residual_abs",
    ]:
        checks.check(float(absolute_lift_probe.get(key)) < 1.0e-10, f"absolute-coordinate planar-lift {key} too large")
    checks.check(len(absolute_lift_rows) == 12, "absolute-coordinate planar-lift row list length changed")
    expected_lift_cases = {
        "frictionless_pendulum_absolute_lift_probe",
        "frictional_pendulum_candidate_absolute_lift_probe",
    }
    expected_lift_methods = {
        "Newmark_beta",
        "trapezoidal",
        "TFE_m1",
        "TFE_m2",
        "TFE_m3_GL",
        "Gauss6_FullVA",
    }
    checks.check(
        {row.get("case_id") for row in absolute_lift_rows} == expected_lift_cases,
        "absolute-coordinate planar-lift cases changed",
    )
    checks.check(
        {row.get("source_method") for row in absolute_lift_rows} == expected_lift_methods,
        "absolute-coordinate planar-lift methods changed",
    )
    for row in absolute_lift_rows:
        checks.check(
            row.get("accepted_use") == "absolute_coordinate_planar_lift_probe_not_source_policy",
            f"{row.get('source_method')} absolute-lift accepted-use changed",
        )
        checks.check(
            row.get("source_policy_dae_runner_equivalent") is False,
            f"{row.get('source_method')} absolute-lift overclaims DAE equivalence",
        )
        checks.check(
            row.get("monolithic_absolute_coordinate_dae_time_integrator") is False,
            f"{row.get('source_method')} absolute-lift overclaims monolithic DAE integrator",
        )
        checks.check(
            row.get("source_policy_method_runner_equivalent") is False,
            f"{row.get('source_method')} absolute-lift overclaims method equivalence",
        )
        checks.check(row.get("source_policy_row_completed") is False, f"{row.get('source_method')} absolute-lift overcloses row")
        checks.check(len(row.get("metrics", [])) == 3, f"{row.get('source_method')} absolute-lift metric count changed")
        checks.check(float(row.get("max_newton_residual_norm")) < 1.0e-8, f"{row.get('source_method')} absolute-lift residual too large")
        for metric in row.get("metrics", []):
            checks.check(math.isfinite(float(metric.get("coordinate_error_q"))), f"{row.get('source_method')} absolute-lift coordinate error missing")
            checks.check(math.isfinite(float(metric.get("velocity_error_v"))), f"{row.get('source_method')} absolute-lift velocity error missing")
            checks.check(float(metric.get("hinge_position_constraint_norm")) < 1.0e-10, f"{row.get('source_method')} absolute-lift hinge position residual too large")
            checks.check(float(metric.get("hinge_velocity_constraint_norm")) < 1.0e-10, f"{row.get('source_method')} absolute-lift hinge velocity residual too large")
            checks.check(float(metric.get("translational_balance_residual_norm")) < 1.0e-10, f"{row.get('source_method')} absolute-lift translational residual too large")
            checks.check(float(metric.get("axis_projected_rotational_residual_abs")) < 1.0e-10, f"{row.get('source_method')} absolute-lift axis residual too large")
            checks.check(
                metric.get("source_policy_dae_runner_equivalent") is False,
                f"{row.get('source_method')} absolute-lift metric overclaims DAE equivalence",
            )

    bounded_dae_rows = bounded_dae_trajectory_runner.get("rows", [])
    checks.check(
        bounded_dae_trajectory_runner.get("runner_api")
        == "bounded_absolute_coordinate_dae_trajectory_runner_smoke",
        "bounded DAE trajectory runner API changed",
    )
    checks.check(
        bounded_dae_trajectory_runner.get("runner_scope")
        == "bounded_stepwise_absolute_dae_residual_runner_not_source_policy",
        "bounded DAE trajectory runner scope changed",
    )
    checks.check(
        bounded_dae_trajectory_runner.get("bounded_absolute_coordinate_dae_trajectory_runner_implemented")
        is True,
        "bounded DAE trajectory runner implementation marker missing",
    )
    checks.check(
        bounded_dae_trajectory_runner.get("monolithic_absolute_coordinate_dae_time_integrator") is False,
        "bounded DAE trajectory runner overclaims monolithic integration",
    )
    checks.check(
        bounded_dae_trajectory_runner.get("source_policy_dae_runner_equivalent") is False,
        "bounded DAE trajectory runner overclaims DAE equivalence",
    )
    checks.check(
        bounded_dae_trajectory_runner.get("source_policy_method_runner_equivalent") is False,
        "bounded DAE trajectory runner overclaims method equivalence",
    )
    checks.check(
        bounded_dae_trajectory_runner.get("source_policy_rows_completed") == 0,
        "bounded DAE trajectory runner overcloses source-policy rows",
    )
    checks.check(
        bounded_dae_trajectory_runner.get("external_superiority_claim_allowed") is False,
        "bounded DAE trajectory runner overclaims external superiority",
    )
    checks.check(bounded_dae_trajectory_runner.get("t_final") == 0.024, "bounded DAE trajectory horizon changed")
    checks.check(
        bounded_dae_trajectory_runner.get("comparison_h") == [0.012, 0.006, 0.003],
        "bounded DAE trajectory h-grid changed",
    )
    checks.check(bounded_dae_trajectory_runner.get("reference_h") == 0.0001, "bounded DAE trajectory reference h changed")
    checks.check(bounded_dae_trajectory_runner.get("method_count") == 4, "bounded DAE trajectory method count changed")
    checks.check(bounded_dae_trajectory_runner.get("row_count") == 4, "bounded DAE trajectory row count changed")
    checks.check(bounded_dae_trajectory_runner.get("metric_row_count") == 12, "bounded DAE trajectory metric row count changed")
    checks.check(
        bounded_dae_trajectory_runner.get("step_residual_row_count") == 56,
        "bounded DAE trajectory step residual row count changed",
    )
    checks.check(
        bounded_dae_trajectory_runner.get("all_step_states_finite") is True,
        "bounded DAE trajectory has nonfinite step states",
    )
    for key in [
        "max_hinge_position_constraint_norm",
        "max_hinge_velocity_constraint_norm",
        "max_translational_balance_residual_norm",
        "max_axis_projected_rotational_residual_abs",
    ]:
        checks.check(float(bounded_dae_trajectory_runner.get(key)) < 1.0e-10, f"bounded DAE trajectory {key} too large")
    checks.check(len(bounded_dae_rows) == 4, "bounded DAE trajectory row list length changed")
    expected_bounded_dae_methods = {"Newmark_beta", "TFE_m1", "TFE_m2", "trapezoidal"}
    checks.check(
        {row.get("source_method") for row in bounded_dae_rows} == expected_bounded_dae_methods,
        "bounded DAE trajectory methods changed",
    )
    for row in bounded_dae_rows:
        checks.check(
            row.get("accepted_use") == "bounded_stepwise_absolute_dae_residual_runner_not_source_policy",
            f"{row.get('source_method')} bounded DAE accepted-use changed",
        )
        checks.check(
            row.get("source_policy_dae_runner_equivalent") is False,
            f"{row.get('source_method')} bounded DAE overclaims DAE equivalence",
        )
        checks.check(
            row.get("monolithic_absolute_coordinate_dae_time_integrator") is False,
            f"{row.get('source_method')} bounded DAE overclaims monolithic integration",
        )
        checks.check(
            row.get("source_policy_method_runner_equivalent") is False,
            f"{row.get('source_method')} bounded DAE overclaims method equivalence",
        )
        checks.check(row.get("source_policy_row_completed") is False, f"{row.get('source_method')} bounded DAE overcloses row")
        checks.check(row.get("step_states_finite") is True, f"{row.get('source_method')} bounded DAE step states not finite")
        checks.check(row.get("step_residual_rows") == 14, f"{row.get('source_method')} bounded DAE step rows changed")
        checks.check(len(row.get("metrics", [])) == 3, f"{row.get('source_method')} bounded DAE metric count changed")
        for metric in row.get("metrics", []):
            checks.check(metric.get("step_states_finite") is True, f"{row.get('source_method')} bounded DAE h-row nonfinite")
            checks.check(metric.get("step_count") in {2, 4, 8}, f"{row.get('source_method')} bounded DAE step count changed")
            checks.check(math.isfinite(float(metric.get("coordinate_error_q"))), f"{row.get('source_method')} bounded DAE coordinate error missing")
            checks.check(math.isfinite(float(metric.get("velocity_error_v"))), f"{row.get('source_method')} bounded DAE velocity error missing")
            checks.check(float(metric.get("max_hinge_position_constraint_norm")) < 1.0e-10, f"{row.get('source_method')} bounded DAE hinge position too large")
            checks.check(float(metric.get("max_hinge_velocity_constraint_norm")) < 1.0e-10, f"{row.get('source_method')} bounded DAE hinge velocity too large")
            checks.check(float(metric.get("max_translational_balance_residual_norm")) < 1.0e-10, f"{row.get('source_method')} bounded DAE translational residual too large")
            checks.check(float(metric.get("max_axis_projected_rotational_residual_abs")) < 1.0e-10, f"{row.get('source_method')} bounded DAE axis residual too large")
            checks.check(
                metric.get("source_policy_dae_runner_equivalent") is False,
                f"{row.get('source_method')} bounded DAE metric overclaims DAE equivalence",
            )

    monolithic_dae_candidate_rows = monolithic_dae_candidate_runner.get("rows", [])
    checks.check(
        monolithic_dae_candidate_runner.get("runner_api")
        == "monolithic_absolute_coordinate_dae_candidate_runner_smoke",
        "monolithic DAE candidate runner API changed",
    )
    checks.check(
        monolithic_dae_candidate_runner.get("runner_scope")
        == "single_entrypoint_absolute_dae_candidate_runner_not_source_policy",
        "monolithic DAE candidate runner scope changed",
    )
    checks.check(
        monolithic_dae_candidate_runner.get(
            "monolithic_absolute_coordinate_dae_candidate_runner_implemented"
        )
        is True,
        "monolithic DAE candidate runner implementation marker missing",
    )
    checks.check(
        monolithic_dae_candidate_runner.get("monolithic_candidate_time_integration_entrypoint")
        is True,
        "monolithic DAE candidate runner entrypoint marker missing",
    )
    checks.check(
        monolithic_dae_candidate_runner.get("monolithic_absolute_coordinate_dae_time_integrator")
        is False,
        "monolithic DAE candidate runner overclaims source-policy monolithic integration",
    )
    checks.check(
        monolithic_dae_candidate_runner.get("source_policy_dae_runner_equivalent") is False,
        "monolithic DAE candidate runner overclaims DAE equivalence",
    )
    checks.check(
        monolithic_dae_candidate_runner.get("source_policy_method_runner_equivalent") is False,
        "monolithic DAE candidate runner overclaims method equivalence",
    )
    checks.check(
        monolithic_dae_candidate_runner.get("source_policy_rows_completed") == 0,
        "monolithic DAE candidate runner overcloses source-policy rows",
    )
    checks.check(
        monolithic_dae_candidate_runner.get("external_superiority_claim_allowed") is False,
        "monolithic DAE candidate runner overclaims external superiority",
    )
    checks.check(
        monolithic_dae_candidate_runner.get("accepted_use")
        == "monolithic_absolute_coordinate_candidate_runner_not_source_policy",
        "monolithic DAE candidate runner accepted-use changed",
    )
    checks.check(
        monolithic_dae_candidate_runner.get("bounded_stepwise_runner_api")
        == "bounded_absolute_coordinate_dae_trajectory_runner_smoke",
        "monolithic DAE candidate runner stopped binding to bounded DAE runner",
    )
    checks.check(
        monolithic_dae_candidate_runner.get("t_final") == 0.024,
        "monolithic DAE candidate runner horizon changed",
    )
    checks.check(
        monolithic_dae_candidate_runner.get("comparison_h") == [0.012, 0.006, 0.003],
        "monolithic DAE candidate runner h-grid changed",
    )
    checks.check(
        monolithic_dae_candidate_runner.get("reference_h") == 0.0001,
        "monolithic DAE candidate runner reference h changed",
    )
    checks.check(
        monolithic_dae_candidate_runner.get("method_count") == 4,
        "monolithic DAE candidate runner method count changed",
    )
    checks.check(
        monolithic_dae_candidate_runner.get("row_count") == 4,
        "monolithic DAE candidate runner row count changed",
    )
    checks.check(
        monolithic_dae_candidate_runner.get("metric_row_count") == 12,
        "monolithic DAE candidate runner metric row count changed",
    )
    checks.check(
        monolithic_dae_candidate_runner.get("step_residual_row_count") == 56,
        "monolithic DAE candidate runner step residual row count changed",
    )
    checks.check(
        monolithic_dae_candidate_runner.get("all_step_states_finite") is True,
        "monolithic DAE candidate runner has nonfinite step states",
    )
    checks.check(
        monolithic_dae_candidate_runner.get("all_rows_finite") is True,
        "monolithic DAE candidate runner has nonfinite rows",
    )
    checks.check(
        monolithic_dae_candidate_runner.get("all_dae_residuals_below_1e_10") is True,
        "monolithic DAE candidate runner residual gate failed",
    )
    for key in [
        "max_hinge_position_constraint_norm",
        "max_hinge_velocity_constraint_norm",
        "max_translational_balance_residual_norm",
        "max_axis_projected_rotational_residual_abs",
    ]:
        checks.check(
            float(monolithic_dae_candidate_runner.get(key)) < 1.0e-10,
            f"monolithic DAE candidate runner {key} too large",
        )
    checks.check(len(monolithic_dae_candidate_rows) == 4, "monolithic DAE candidate row list length changed")
    checks.check(
        {row.get("source_method") for row in monolithic_dae_candidate_rows}
        == expected_bounded_dae_methods,
        "monolithic DAE candidate runner methods changed",
    )
    for row in monolithic_dae_candidate_rows:
        checks.check(
            row.get("accepted_use")
            == "monolithic_absolute_coordinate_candidate_runner_not_source_policy",
            f"{row.get('source_method')} monolithic DAE candidate accepted-use changed",
        )
        checks.check(
            row.get("bounded_stepwise_runner_api")
            == "bounded_absolute_coordinate_dae_trajectory_runner_smoke",
            f"{row.get('source_method')} monolithic DAE candidate stopped binding bounded runner",
        )
        checks.check(
            row.get("monolithic_candidate_time_integration_entrypoint") is True,
            f"{row.get('source_method')} monolithic DAE candidate entrypoint marker missing",
        )
        checks.check(
            row.get("monolithic_absolute_coordinate_dae_time_integrator") is False,
            f"{row.get('source_method')} monolithic DAE candidate overclaims monolithic integration",
        )
        checks.check(
            row.get("source_policy_dae_runner_equivalent") is False,
            f"{row.get('source_method')} monolithic DAE candidate overclaims DAE equivalence",
        )
        checks.check(
            row.get("source_policy_method_runner_equivalent") is False,
            f"{row.get('source_method')} monolithic DAE candidate overclaims method equivalence",
        )
        checks.check(
            row.get("source_policy_row_completed") is False,
            f"{row.get('source_method')} monolithic DAE candidate overcloses row",
        )
        checks.check(
            row.get("step_states_finite") is True,
            f"{row.get('source_method')} monolithic DAE candidate step states not finite",
        )
        checks.check(
            row.get("all_metrics_finite") is True,
            f"{row.get('source_method')} monolithic DAE candidate metrics not finite",
        )
        checks.check(
            row.get("all_dae_residuals_below_1e_10") is True,
            f"{row.get('source_method')} monolithic DAE candidate residual flag failed",
        )
        checks.check(
            row.get("step_residual_rows") == 14,
            f"{row.get('source_method')} monolithic DAE candidate step rows changed",
        )
        checks.check(
            len(row.get("metrics", [])) == 3,
            f"{row.get('source_method')} monolithic DAE candidate metric count changed",
        )
        for metric in row.get("metrics", []):
            checks.check(
                metric.get("step_states_finite") is True,
                f"{row.get('source_method')} monolithic DAE candidate h-row nonfinite",
            )
            checks.check(
                metric.get("monolithic_candidate_time_integration_entrypoint") is True,
                f"{row.get('source_method')} monolithic DAE candidate metric entrypoint marker missing",
            )
            checks.check(
                metric.get("monolithic_absolute_coordinate_dae_time_integrator") is False,
                f"{row.get('source_method')} monolithic DAE candidate metric overclaims monolithic integration",
            )
            checks.check(
                metric.get("source_policy_row_completed") is False,
                f"{row.get('source_method')} monolithic DAE candidate metric overcloses row",
            )
            checks.check(
                metric.get("accepted_use")
                == "monolithic_absolute_coordinate_candidate_runner_not_source_policy",
                f"{row.get('source_method')} monolithic DAE candidate metric accepted-use changed",
            )
            checks.check(
                metric.get("step_count") in {2, 4, 8},
                f"{row.get('source_method')} monolithic DAE candidate step count changed",
            )
            checks.check(
                math.isfinite(float(metric.get("coordinate_error_q"))),
                f"{row.get('source_method')} monolithic DAE candidate coordinate error missing",
            )
            checks.check(
                math.isfinite(float(metric.get("velocity_error_v"))),
                f"{row.get('source_method')} monolithic DAE candidate velocity error missing",
            )
            checks.check(
                float(metric.get("max_hinge_position_constraint_norm")) < 1.0e-10,
                f"{row.get('source_method')} monolithic DAE candidate hinge position too large",
            )
            checks.check(
                float(metric.get("max_hinge_velocity_constraint_norm")) < 1.0e-10,
                f"{row.get('source_method')} monolithic DAE candidate hinge velocity too large",
            )
            checks.check(
                float(metric.get("max_translational_balance_residual_norm")) < 1.0e-10,
                f"{row.get('source_method')} monolithic DAE candidate translational residual too large",
            )
            checks.check(
                float(metric.get("max_axis_projected_rotational_residual_abs")) < 1.0e-10,
                f"{row.get('source_method')} monolithic DAE candidate axis residual too large",
            )
            checks.check(
                metric.get("source_policy_dae_runner_equivalent") is False,
                f"{row.get('source_method')} monolithic DAE candidate metric overclaims DAE equivalence",
            )

    source_policy_dae_runner_contract_rows = source_policy_dae_runner_contract.get("rows", [])
    checks.check(
        source_policy_dae_runner_contract.get("schema")
        == "tfe-source-policy-absolute-coordinate-dae-runner-contract-v1",
        "source-policy absolute-coordinate DAE runner contract schema changed",
    )
    checks.check(
        source_policy_dae_runner_contract.get("runner_api")
        == "source_policy_absolute_coordinate_dae_runner",
        "source-policy absolute-coordinate DAE runner contract API changed",
    )
    checks.check(
        source_policy_dae_runner_contract.get("runner_scope")
        == "contract_entrypoint_present_candidate_backed_not_source_policy_equivalent",
        "source-policy absolute-coordinate DAE runner contract scope changed",
    )
    checks.check(
        source_policy_dae_runner_contract.get(
            "source_policy_absolute_coordinate_dae_runner_contract_present"
        )
        is True,
        "source-policy absolute-coordinate DAE runner contract marker missing",
    )
    checks.check(
        source_policy_dae_runner_contract.get(
            "source_policy_absolute_coordinate_dae_runner_implemented"
        )
        is False,
        "source-policy absolute-coordinate DAE runner contract overclaims implementation",
    )
    checks.check(
        source_policy_dae_runner_contract.get(
            "source_policy_absolute_coordinate_dae_runner_equivalent"
        )
        is False,
        "source-policy absolute-coordinate DAE runner contract overclaims equivalence",
    )
    checks.check(
        source_policy_dae_runner_contract.get("monolithic_absolute_coordinate_dae_time_integrator")
        is False,
        "source-policy absolute-coordinate DAE runner contract overclaims monolithic integration",
    )
    checks.check(
        source_policy_dae_runner_contract.get("source_policy_dae_runner_equivalent") is False,
        "source-policy absolute-coordinate DAE runner contract overclaims DAE equivalence",
    )
    checks.check(
        source_policy_dae_runner_contract.get("source_policy_method_runner_equivalent") is False,
        "source-policy absolute-coordinate DAE runner contract overclaims method equivalence",
    )
    checks.check(
        source_policy_dae_runner_contract.get("source_policy_rows_completed") == 0,
        "source-policy absolute-coordinate DAE runner contract overcloses rows",
    )
    checks.check(
        source_policy_dae_runner_contract.get("external_superiority_claim_allowed") is False,
        "source-policy absolute-coordinate DAE runner contract overclaims external superiority",
    )
    checks.check(
        source_policy_dae_runner_contract.get("accepted_use")
        == "contract_entrypoint_only_not_source_policy_reproduction",
        "source-policy absolute-coordinate DAE runner contract accepted-use changed",
    )
    checks.check(
        source_policy_dae_runner_contract.get("candidate_runner_api")
        == "monolithic_absolute_coordinate_dae_candidate_runner_smoke",
        "source-policy absolute-coordinate DAE runner contract candidate API changed",
    )
    checks.check(
        source_policy_dae_runner_contract.get("bounded_stepwise_runner_api")
        == "bounded_absolute_coordinate_dae_trajectory_runner_smoke",
        "source-policy absolute-coordinate DAE runner contract bounded runner binding changed",
    )
    checks.check(
        source_policy_dae_runner_contract.get("t_final") == 0.024,
        "source-policy absolute-coordinate DAE runner contract horizon changed",
    )
    checks.check(
        source_policy_dae_runner_contract.get("comparison_h") == [0.012, 0.006, 0.003],
        "source-policy absolute-coordinate DAE runner contract h-grid changed",
    )
    checks.check(
        source_policy_dae_runner_contract.get("reference_h") == 0.0001,
        "source-policy absolute-coordinate DAE runner contract reference h changed",
    )
    checks.check(
        source_policy_dae_runner_contract.get("method_count") == 4,
        "source-policy absolute-coordinate DAE runner contract method count changed",
    )
    checks.check(
        source_policy_dae_runner_contract.get("row_count") == 4,
        "source-policy absolute-coordinate DAE runner contract row count changed",
    )
    checks.check(
        source_policy_dae_runner_contract.get("metric_row_count") == 12,
        "source-policy absolute-coordinate DAE runner contract metric row count changed",
    )
    checks.check(
        source_policy_dae_runner_contract.get("step_residual_row_count") == 56,
        "source-policy absolute-coordinate DAE runner contract step residual row count changed",
    )
    checks.check(
        source_policy_dae_runner_contract.get("all_step_states_finite") is True,
        "source-policy absolute-coordinate DAE runner contract has nonfinite step states",
    )
    checks.check(
        source_policy_dae_runner_contract.get("all_rows_finite") is True,
        "source-policy absolute-coordinate DAE runner contract has nonfinite rows",
    )
    checks.check(
        source_policy_dae_runner_contract.get("all_dae_residuals_below_1e_10") is True,
        "source-policy absolute-coordinate DAE runner contract residual gate failed",
    )
    for key in [
        "max_hinge_position_constraint_norm",
        "max_hinge_velocity_constraint_norm",
        "max_translational_balance_residual_norm",
        "max_axis_projected_rotational_residual_abs",
    ]:
        checks.check(
            float(source_policy_dae_runner_contract.get(key)) < 1.0e-10,
            f"source-policy absolute-coordinate DAE runner contract {key} too large",
        )
    checks.check(
        len(source_policy_dae_runner_contract_rows) == 4,
        "source-policy absolute-coordinate DAE runner contract row list length changed",
    )
    checks.check(
        {row.get("source_method") for row in source_policy_dae_runner_contract_rows}
        == expected_bounded_dae_methods,
        "source-policy absolute-coordinate DAE runner contract methods changed",
    )
    for row in source_policy_dae_runner_contract_rows:
        checks.check(
            row.get("accepted_use") == "contract_entrypoint_only_not_source_policy_reproduction",
            f"{row.get('source_method')} source-policy DAE contract accepted-use changed",
        )
        checks.check(
            row.get("source_policy_absolute_coordinate_dae_runner_contract_present") is True,
            f"{row.get('source_method')} source-policy DAE contract marker missing",
        )
        checks.check(
            row.get("source_policy_absolute_coordinate_dae_runner_implemented") is False,
            f"{row.get('source_method')} source-policy DAE contract overclaims implementation",
        )
        checks.check(
            row.get("source_policy_absolute_coordinate_dae_runner_equivalent") is False,
            f"{row.get('source_method')} source-policy DAE contract overclaims equivalence",
        )
        checks.check(
            row.get("candidate_runner_api")
            == "monolithic_absolute_coordinate_dae_candidate_runner_smoke",
            f"{row.get('source_method')} source-policy DAE contract candidate binding changed",
        )
        checks.check(
            row.get("monolithic_absolute_coordinate_dae_time_integrator") is False,
            f"{row.get('source_method')} source-policy DAE contract overclaims monolithic integration",
        )
        checks.check(
            row.get("source_policy_dae_runner_equivalent") is False,
            f"{row.get('source_method')} source-policy DAE contract overclaims DAE equivalence",
        )
        checks.check(
            row.get("source_policy_method_runner_equivalent") is False,
            f"{row.get('source_method')} source-policy DAE contract overclaims method equivalence",
        )
        checks.check(
            row.get("source_policy_row_completed") is False,
            f"{row.get('source_method')} source-policy DAE contract overcloses row",
        )
        checks.check(
            row.get("step_states_finite") is True,
            f"{row.get('source_method')} source-policy DAE contract step states not finite",
        )
        checks.check(
            row.get("all_metrics_finite") is True,
            f"{row.get('source_method')} source-policy DAE contract metrics not finite",
        )
        checks.check(
            row.get("all_dae_residuals_below_1e_10") is True,
            f"{row.get('source_method')} source-policy DAE contract residual flag failed",
        )
        checks.check(
            row.get("step_residual_rows") == 14,
            f"{row.get('source_method')} source-policy DAE contract step rows changed",
        )
        checks.check(
            len(row.get("metrics", [])) == 3,
            f"{row.get('source_method')} source-policy DAE contract metric count changed",
        )
        for metric in row.get("metrics", []):
            checks.check(
                metric.get("step_states_finite") is True,
                f"{row.get('source_method')} source-policy DAE contract h-row nonfinite",
            )
            checks.check(
                metric.get("source_policy_absolute_coordinate_dae_runner_contract_present")
                is True,
                f"{row.get('source_method')} source-policy DAE contract metric marker missing",
            )
            checks.check(
                metric.get("source_policy_absolute_coordinate_dae_runner_implemented")
                is False,
                f"{row.get('source_method')} source-policy DAE contract metric overclaims implementation",
            )
            checks.check(
                metric.get("source_policy_absolute_coordinate_dae_runner_equivalent")
                is False,
                f"{row.get('source_method')} source-policy DAE contract metric overclaims equivalence",
            )
            checks.check(
                metric.get("monolithic_absolute_coordinate_dae_time_integrator") is False,
                f"{row.get('source_method')} source-policy DAE contract metric overclaims monolithic integration",
            )
            checks.check(
                metric.get("source_policy_row_completed") is False,
                f"{row.get('source_method')} source-policy DAE contract metric overcloses row",
            )
            checks.check(
                metric.get("accepted_use")
                == "contract_entrypoint_only_not_source_policy_reproduction",
                f"{row.get('source_method')} source-policy DAE contract metric accepted-use changed",
            )
            checks.check(
                metric.get("candidate_runner_api")
                == "monolithic_absolute_coordinate_dae_candidate_runner_smoke",
                f"{row.get('source_method')} source-policy DAE contract metric candidate binding changed",
            )
            checks.check(
                metric.get("step_count") in {2, 4, 8},
                f"{row.get('source_method')} source-policy DAE contract step count changed",
            )
            checks.check(
                math.isfinite(float(metric.get("coordinate_error_q"))),
                f"{row.get('source_method')} source-policy DAE contract coordinate error missing",
            )
            checks.check(
                math.isfinite(float(metric.get("velocity_error_v"))),
                f"{row.get('source_method')} source-policy DAE contract velocity error missing",
            )
            checks.check(
                float(metric.get("max_hinge_position_constraint_norm")) < 1.0e-10,
                f"{row.get('source_method')} source-policy DAE contract hinge position too large",
            )
            checks.check(
                float(metric.get("max_hinge_velocity_constraint_norm")) < 1.0e-10,
                f"{row.get('source_method')} source-policy DAE contract hinge velocity too large",
            )
            checks.check(
                float(metric.get("max_translational_balance_residual_norm")) < 1.0e-10,
                f"{row.get('source_method')} source-policy DAE contract translational residual too large",
            )
            checks.check(
                float(metric.get("max_axis_projected_rotational_residual_abs")) < 1.0e-10,
                f"{row.get('source_method')} source-policy DAE contract axis residual too large",
            )
            checks.check(
                metric.get("source_policy_dae_runner_equivalent") is False,
                f"{row.get('source_method')} source-policy DAE contract metric overclaims DAE equivalence",
            )

    bridge_rows = dae_trajectory_bridge_contract.get("rows", [])
    checks.check(
        dae_trajectory_bridge_contract.get("schema")
        == "tfe-dae-trajectory-bridge-contract-smoke-v1",
        "DAE trajectory bridge schema changed",
    )
    checks.check(
        dae_trajectory_bridge_contract.get("runner_api") == "dae_trajectory_bridge_contract_smoke",
        "DAE trajectory bridge API changed",
    )
    checks.check(
        dae_trajectory_bridge_contract.get("runner_scope")
        == "bounded_source_metrics_bound_to_stepwise_absolute_dae_residuals_not_source_policy",
        "DAE trajectory bridge scope changed",
    )
    checks.check(
        dae_trajectory_bridge_contract.get("dae_trajectory_bridge_contract_implemented") is True,
        "DAE trajectory bridge implementation marker missing",
    )
    checks.check(
        dae_trajectory_bridge_contract.get("source_runner_api") == "bounded_source_policy_runner_smoke",
        "DAE trajectory bridge source runner changed",
    )
    checks.check(
        dae_trajectory_bridge_contract.get("dae_runner_api")
        == "bounded_absolute_coordinate_dae_trajectory_runner_smoke",
        "DAE trajectory bridge DAE runner changed",
    )
    checks.check(dae_trajectory_bridge_contract.get("t_final") == 0.024, "DAE trajectory bridge horizon changed")
    checks.check(
        dae_trajectory_bridge_contract.get("comparison_h") == [0.012, 0.006, 0.003],
        "DAE trajectory bridge h-grid changed",
    )
    checks.check(
        dae_trajectory_bridge_contract.get("reference_h") == 0.0001,
        "DAE trajectory bridge reference h changed",
    )
    checks.check(dae_trajectory_bridge_contract.get("method_count") == 4, "DAE trajectory bridge method count changed")
    checks.check(
        dae_trajectory_bridge_contract.get("source_metric_row_count") == 12,
        "DAE trajectory bridge source row count changed",
    )
    checks.check(
        dae_trajectory_bridge_contract.get("dae_metric_row_count") == 12,
        "DAE trajectory bridge DAE row count changed",
    )
    checks.check(dae_trajectory_bridge_contract.get("row_count") == 12, "DAE trajectory bridge row count changed")
    checks.check(
        dae_trajectory_bridge_contract.get("matched_contract_row_count") == 12,
        "DAE trajectory bridge matched row count changed",
    )
    checks.check(
        dae_trajectory_bridge_contract.get("all_rows_finite") is True,
        "DAE trajectory bridge has nonfinite row",
    )
    checks.check(
        dae_trajectory_bridge_contract.get("all_dae_residuals_below_1e_10") is True,
        "DAE trajectory bridge DAE residual flag failed",
    )
    checks.check(
        dae_trajectory_bridge_contract.get("monolithic_absolute_coordinate_dae_time_integrator") is False,
        "DAE trajectory bridge overclaims monolithic integration",
    )
    checks.check(
        dae_trajectory_bridge_contract.get("source_policy_dae_runner_equivalent") is False,
        "DAE trajectory bridge overclaims DAE equivalence",
    )
    checks.check(
        dae_trajectory_bridge_contract.get("source_policy_method_runner_equivalent") is False,
        "DAE trajectory bridge overclaims method equivalence",
    )
    checks.check(
        dae_trajectory_bridge_contract.get("source_policy_rows_completed") == 0,
        "DAE trajectory bridge overcloses rows",
    )
    checks.check(len(bridge_rows) == 12, "DAE trajectory bridge row list length changed")
    expected_bridge_methods = {"Newmark_beta", "TFE_m1", "TFE_m2", "trapezoidal"}
    checks.check(
        {row.get("source_method") for row in bridge_rows} == expected_bridge_methods,
        "DAE trajectory bridge methods changed",
    )
    checks.check(
        {float(row.get("h")) for row in bridge_rows} == {0.012, 0.006, 0.003},
        "DAE trajectory bridge h values changed",
    )
    for row in bridge_rows:
        checks.check(
            row.get("accepted_use") == "dae_trajectory_bridge_contract_not_source_policy",
            f"{row.get('source_method')} bridge accepted-use changed",
        )
        checks.check(row.get("source_metric_row_matched") is True, f"{row.get('source_method')} source row not matched")
        checks.check(row.get("dae_metric_row_matched") is True, f"{row.get('source_method')} DAE row not matched")
        checks.check(row.get("row_finite") is True, f"{row.get('source_method')} bridge row not finite")
        checks.check(
            row.get("dae_residual_below_1e_10") is True,
            f"{row.get('source_method')} bridge residual threshold failed",
        )
        checks.check(
            row.get("source_policy_dae_runner_equivalent") is False,
            f"{row.get('source_method')} bridge overclaims DAE equivalence",
        )
        checks.check(
            row.get("source_policy_method_runner_equivalent") is False,
            f"{row.get('source_method')} bridge overclaims method equivalence",
        )
        checks.check(row.get("source_policy_row_completed") is False, f"{row.get('source_method')} bridge overcloses row")
        checks.check(row.get("step_count") in {2, 4, 8}, f"{row.get('source_method')} bridge step count changed")
        checks.check(row.get("step_residual_rows") in {2, 4, 8}, f"{row.get('source_method')} bridge step residual count changed")
        checks.check(row.get("step_states_finite") is True, f"{row.get('source_method')} bridge step states not finite")
        for key in [
            "coordinate_error_q",
            "velocity_error_v",
            "frobenius_error_norm_eta",
            "work_units_newton_iterations",
        ]:
            checks.check(math.isfinite(float(row.get(key))), f"{row.get('source_method')} bridge {key} not finite")
        for key in [
            "max_candidate_step_residual_norm",
            "max_hinge_position_constraint_norm",
            "max_hinge_velocity_constraint_norm",
            "max_translational_balance_residual_norm",
            "max_axis_projected_rotational_residual_abs",
        ]:
            checks.check(float(row.get(key)) < 1.0e-10, f"{row.get('source_method')} bridge {key} too large")

    friction_contract_rows = candidate_frictional_dae_trajectory_contract.get("rows", [])
    checks.check(
        candidate_frictional_dae_trajectory_contract.get("schema")
        == "tfe-candidate-frictional-dae-trajectory-contract-smoke-v1",
        "candidate-friction DAE trajectory contract schema changed",
    )
    checks.check(
        candidate_frictional_dae_trajectory_contract.get("runner_api")
        == "candidate_frictional_dae_trajectory_contract_smoke",
        "candidate-friction DAE trajectory contract API changed",
    )
    checks.check(
        candidate_frictional_dae_trajectory_contract.get("runner_scope")
        == "candidate_brown_mcphee_friction_bound_to_stepwise_absolute_dae_residuals_not_source_policy",
        "candidate-friction DAE trajectory contract scope changed",
    )
    checks.check(
        candidate_frictional_dae_trajectory_contract.get(
            "candidate_frictional_dae_trajectory_contract_implemented"
        )
        is True,
        "candidate-friction DAE trajectory contract implementation marker missing",
    )
    checks.check(
        candidate_frictional_dae_trajectory_contract.get("t_final") == 0.024,
        "candidate-friction DAE trajectory contract horizon changed",
    )
    checks.check(
        candidate_frictional_dae_trajectory_contract.get("comparison_h") == [0.012, 0.006, 0.003],
        "candidate-friction DAE trajectory contract h-grid changed",
    )
    checks.check(
        candidate_frictional_dae_trajectory_contract.get("reference_h") == 0.0001,
        "candidate-friction DAE trajectory contract reference h changed",
    )
    checks.check(
        candidate_frictional_dae_trajectory_contract.get("theta0") == 0.0
        and candidate_frictional_dae_trajectory_contract.get("omega0") == 1.0
        and candidate_frictional_dae_trajectory_contract.get("frictional") is True,
        "candidate-friction DAE trajectory contract initial/friction policy changed",
    )
    checks.check(
        candidate_frictional_dae_trajectory_contract.get("method_count") == 4,
        "candidate-friction DAE trajectory contract method count changed",
    )
    checks.check(
        candidate_frictional_dae_trajectory_contract.get("row_count") == 12,
        "candidate-friction DAE trajectory contract row count changed",
    )
    checks.check(
        candidate_frictional_dae_trajectory_contract.get("step_residual_row_count") == 56,
        "candidate-friction DAE trajectory contract step-residual count changed",
    )
    checks.check(
        candidate_frictional_dae_trajectory_contract.get("all_rows_finite") is True,
        "candidate-friction DAE trajectory contract has nonfinite rows",
    )
    checks.check(
        candidate_frictional_dae_trajectory_contract.get("all_dae_residuals_below_1e_9") is True,
        "candidate-friction DAE trajectory contract residual flag failed",
    )
    checks.check(
        candidate_frictional_dae_trajectory_contract.get("all_candidate_friction_power_nonpositive") is True,
        "candidate-friction DAE trajectory contract friction power flag failed",
    )
    checks.check(
        candidate_frictional_dae_trajectory_contract.get("brown_mcphee_source_code_equivalent_law") is False,
        "candidate-friction DAE trajectory contract overclaims Brown--McPhee source law",
    )
    checks.check(
        candidate_frictional_dae_trajectory_contract.get("monolithic_absolute_coordinate_dae_time_integrator") is False,
        "candidate-friction DAE trajectory contract overclaims monolithic integration",
    )
    checks.check(
        candidate_frictional_dae_trajectory_contract.get("source_policy_dae_runner_equivalent") is False,
        "candidate-friction DAE trajectory contract overclaims DAE equivalence",
    )
    checks.check(
        candidate_frictional_dae_trajectory_contract.get("source_policy_method_runner_equivalent") is False,
        "candidate-friction DAE trajectory contract overclaims method equivalence",
    )
    checks.check(
        candidate_frictional_dae_trajectory_contract.get("source_policy_rows_completed") == 0,
        "candidate-friction DAE trajectory contract overcloses rows",
    )
    checks.check(len(friction_contract_rows) == 12, "candidate-friction DAE trajectory contract row list length changed")
    checks.check(
        {row.get("source_method") for row in friction_contract_rows} == expected_bridge_methods,
        "candidate-friction DAE trajectory contract methods changed",
    )
    checks.check(
        {float(row.get("h")) for row in friction_contract_rows} == {0.012, 0.006, 0.003},
        "candidate-friction DAE trajectory contract h values changed",
    )
    for row in friction_contract_rows:
        checks.check(
            row.get("accepted_use") == "candidate_frictional_dae_trajectory_contract_not_source_policy",
            f"{row.get('source_method')} candidate-friction accepted-use changed",
        )
        checks.check(row.get("frictional") is True, f"{row.get('source_method')} candidate-friction row not frictional")
        checks.check(row.get("row_finite") is True, f"{row.get('source_method')} candidate-friction row not finite")
        checks.check(
            row.get("dae_residual_below_1e_9") is True,
            f"{row.get('source_method')} candidate-friction residual threshold failed",
        )
        checks.check(
            row.get("candidate_friction_power_nonpositive") is True,
            f"{row.get('source_method')} candidate-friction power sign failed",
        )
        checks.check(
            row.get("brown_mcphee_source_code_equivalent_law") is False,
            f"{row.get('source_method')} candidate-friction overclaims source law",
        )
        checks.check(
            row.get("source_policy_dae_runner_equivalent") is False,
            f"{row.get('source_method')} candidate-friction overclaims DAE equivalence",
        )
        checks.check(
            row.get("source_policy_method_runner_equivalent") is False,
            f"{row.get('source_method')} candidate-friction overclaims method equivalence",
        )
        checks.check(row.get("source_policy_row_completed") is False, f"{row.get('source_method')} candidate-friction overcloses row")
        checks.check(row.get("step_count") in {2, 4, 8}, f"{row.get('source_method')} candidate-friction step count changed")
        checks.check(row.get("step_residual_rows") in {2, 4, 8}, f"{row.get('source_method')} candidate-friction step residual count changed")
        checks.check(row.get("step_states_finite") is True, f"{row.get('source_method')} candidate-friction step states not finite")
        checks.check(float(row.get("max_candidate_friction_power")) <= 1.0e-12, f"{row.get('source_method')} candidate-friction max power positive")
        checks.check(float(row.get("min_candidate_friction_power")) < 0.0, f"{row.get('source_method')} candidate-friction min power not dissipative")
        for key in [
            "coordinate_error_q",
            "velocity_error_v",
            "frobenius_error_norm_eta",
            "total_newton_iterations",
        ]:
            checks.check(math.isfinite(float(row.get(key))), f"{row.get('source_method')} candidate-friction {key} not finite")
        for key in [
            "max_candidate_step_residual_norm",
            "max_hinge_position_constraint_norm",
            "max_hinge_velocity_constraint_norm",
            "max_translational_balance_residual_norm",
            "max_axis_projected_rotational_residual_abs",
        ]:
            checks.check(float(row.get(key)) < 1.0e-9, f"{row.get('source_method')} candidate-friction {key} too large")

    checks.check(
        appendix_b_certificate.get("schema") == "tfe-appendix-b-coefficient-certificate-v1",
        "TFE Appendix-B coefficient certificate schema changed",
    )
    checks.check(
        appendix_b_certificate.get("all_appendix_b_formula_matches") is True,
        "TFE Appendix-B coefficient certificate does not match source formulas",
    )
    checks.check(
        appendix_b_certificate.get("checked_methods") == ["TFE_m1", "TFE_m2", "TFE_m3_GL"],
        "TFE Appendix-B checked method set changed",
    )
    checks.check(appendix_b_certificate.get("row_count") == 3, "TFE Appendix-B row count changed")
    checks.check(
        float(appendix_b_certificate.get("max_abs_diff")) <= 1.0e-14,
        "TFE Appendix-B max difference too large",
    )
    checks.check(
        appendix_b_certificate.get("scope")
        == "coefficient_formula_certificate_only_not_source_policy_runner_equivalence",
        "TFE Appendix-B certificate scope changed",
    )
    checks.check(
        appendix_b_certificate.get("source_policy_method_runner_equivalent") is False,
        "TFE Appendix-B certificate overclaims source-policy runner equivalence",
    )
    checks.check(
        appendix_b_certificate.get("source_policy_rows_completed") == 0,
        "TFE Appendix-B certificate overcloses source-policy rows",
    )
    appendix_rows = appendix_b_certificate.get("rows", [])
    checks.check(len(appendix_rows) == 3, "TFE Appendix-B certificate row list changed")
    for row in appendix_rows:
        checks.check(row.get("appendix_b_formula_match") is True, f"{row.get('method')} Appendix-B formula mismatch")
        checks.check(float(row.get("max_abs_diff")) <= 1.0e-14, f"{row.get('method')} Appendix-B max diff too large")
        part_diffs = row.get("part_max_abs_diff", {})
        checks.check(set(part_diffs) == {"alpha", "beta", "gamma", "nodes"}, f"{row.get('method')} part diff keys changed")
        for value in part_diffs.values():
            checks.check(float(value) <= 1.0e-14, f"{row.get('method')} part diff too large")

    bounded_rows = bounded_runner_smoke.get("rows", [])
    checks.check(
        bounded_runner_smoke.get("bounded_source_policy_runner_api_implemented") is True,
        "bounded runner smoke missing API marker",
    )
    checks.check(
        bounded_runner_smoke.get("bounded_source_policy_runner_smoke_implemented") is True,
        "bounded runner smoke missing implemented marker",
    )
    checks.check(bounded_runner_smoke.get("runner_api") == "bounded_source_policy_runner_smoke", "bounded runner API name changed")
    checks.check(bounded_runner_smoke.get("unified_method_dispatch") is True, "bounded runner dispatch marker changed")
    checks.check(bounded_runner_smoke.get("t_final") == 0.024, "bounded runner t_final changed")
    checks.check(bounded_runner_smoke.get("reference_h") == 0.0001, "bounded runner reference h changed")
    checks.check(bounded_runner_smoke.get("comparison_h") == [0.012, 0.006, 0.003], "bounded runner h-grid changed")
    checks.check(bounded_runner_smoke.get("method_count") == 4, "bounded runner method count changed")
    checks.check(bounded_runner_smoke.get("row_count") == 4, "bounded runner row count changed")
    checks.check(
        bounded_runner_smoke.get("full_T10_source_policy_reproduction") is False,
        "bounded runner overclaims full source-policy reproduction",
    )
    checks.check(
        bounded_runner_smoke.get("source_policy_method_runner_equivalent") is False,
        "bounded runner overclaims method equivalence",
    )
    checks.check(bounded_runner_smoke.get("source_policy_rows_completed") == 0, "bounded runner overcloses rows")
    checks.check(len(bounded_rows) == 4, "bounded runner row list length changed")
    for row in bounded_rows:
        checks.check(
            row.get("accepted_use") == "bounded_candidate_runner_api_only_not_source_policy",
            f"{row.get('paper_method')} bounded row allowed-use changed",
        )
        checks.check(row.get("source_policy_row_completed") is False, f"{row.get('paper_method')} bounded row overclosed")
        checks.check(row.get("source_policy_method_runner_equivalent") is False, f"{row.get('paper_method')} bounded row overclaims equivalence")
        checks.check(row.get("coordinate_error_decreased") is True, f"{row.get('paper_method')} bounded coordinate error not decreasing")
        checks.check(row.get("velocity_error_decreased") is True, f"{row.get('paper_method')} bounded velocity error not decreasing")
        checks.check(len(row.get("metrics", [])) == 3, f"{row.get('paper_method')} bounded metric row count changed")
        checks.check(float(row.get("max_newton_residual_norm")) < 1.0e-8, f"{row.get('paper_method')} bounded residual too large")

    active_rows = active_b2_smoke.get("rows", [])
    checks.check(
        active_b2_smoke.get("active_b2_candidate_row_smoke_implemented") is True,
        "active B2 smoke does not mark implementation",
    )
    checks.check(active_b2_smoke.get("t_final") == 0.024, "active B2 smoke t_final changed")
    checks.check(active_b2_smoke.get("reference_h") == 0.0001, "active B2 smoke reference h changed")
    checks.check(active_b2_smoke.get("comparison_h") == [0.012, 0.006, 0.003], "active B2 h-grid changed")
    checks.check(
        active_b2_smoke.get("full_T10_source_policy_reproduction") is False,
        "active B2 smoke overclaims full source-policy reproduction",
    )
    checks.check(
        active_b2_smoke.get("source_policy_method_runner_equivalent") is False,
        "active B2 smoke overclaims source-policy method equivalence",
    )
    checks.check(active_b2_smoke.get("source_policy_rows_completed") == 0, "active B2 smoke overcloses rows")
    checks.check(len(active_rows) == 4, "active B2 smoke row count changed")
    expected_active_methods = {
        ("tfe2026_Newmark_beta", "Newmark_beta", 2),
        ("tfe2026_TFE_m1", "TFE_m1", 1),
        ("tfe2026_TFE_m2", "TFE_m2", 3),
        ("tfe2026_trapezoidal", "trapezoidal", 2),
    }
    observed_active_methods = {
        (row.get("paper_method"), row.get("source_method"), row.get("expected_order"))
        for row in active_rows
    }
    checks.check(observed_active_methods == expected_active_methods, "active B2 method set changed")
    for row in active_rows:
        checks.check(row.get("example") == "single_pendulum", f"{row.get('paper_method')} active B2 example changed")
        checks.check(row.get("frictional") is False, f"{row.get('paper_method')} active B2 friction policy changed")
        checks.check(row.get("source_policy_method_runner_equivalent") is False, f"{row.get('paper_method')} overclaims equivalence")
        checks.check(row.get("source_policy_row_completed") is False, f"{row.get('paper_method')} overcloses row")
        checks.check(row.get("coordinate_error_decreased") is True, f"{row.get('paper_method')} coordinate error not decreasing")
        checks.check(row.get("velocity_error_decreased") is True, f"{row.get('paper_method')} velocity error not decreasing")
        checks.check(len(row.get("metrics", [])) == 3, f"{row.get('paper_method')} active metric row count changed")
        checks.check(float(row.get("max_newton_residual_norm")) < 1.0e-8, f"{row.get('paper_method')} active residual too large")
        for key in ["coordinate_pairwise_orders", "velocity_pairwise_orders", "frobenius_pairwise_orders"]:
            orders = row.get(key, [])
            checks.check(len(orders) == 2, f"{row.get('paper_method')} active {key} length changed")
            for order in orders:
                checks.check(order is not None and math.isfinite(float(order)), f"{row.get('paper_method')} active {key} not finite")

    full_t10_rows = full_t10_coarse_probe.get("rows", [])
    checks.check(
        full_t10_coarse_probe.get("runner_api") == "active_tfe_b2_full_t10_coarse_candidate_probe",
        "full T=10 coarse probe API changed",
    )
    checks.check(full_t10_coarse_probe.get("t_final") == 10.0, "full T=10 coarse probe horizon changed")
    checks.check(full_t10_coarse_probe.get("reference_h") == 0.0125, "full T=10 coarse probe reference h changed")
    checks.check(
        full_t10_coarse_probe.get("comparison_h") == [0.1, 0.05, 0.025],
        "full T=10 coarse probe h-grid changed",
    )
    checks.check(
        full_t10_coarse_probe.get("full_T10_candidate_probe_completed") is True,
        "full T=10 coarse probe not marked complete",
    )
    checks.check(
        full_t10_coarse_probe.get("full_T10_source_policy_reproduction") is False,
        "full T=10 coarse probe overclaims source-policy reproduction",
    )
    checks.check(
        full_t10_coarse_probe.get("source_policy_reference_h") == 0.0001,
        "full T=10 coarse probe source reference h changed",
    )
    checks.check(
        full_t10_coarse_probe.get("source_policy_reference_not_invoked") is True,
        "full T=10 coarse probe invoked source-policy reference",
    )
    checks.check(full_t10_coarse_probe.get("source_policy_rows_completed") == 0, "full T=10 coarse probe overclosed rows")
    checks.check(full_t10_coarse_probe.get("finite_row_count") == 4, "full T=10 coarse probe finite row count changed")
    checks.check(full_t10_coarse_probe.get("residual_ok_row_count") == 4, "full T=10 coarse probe residual row count changed")
    checks.check(len(full_t10_rows) == 4, "full T=10 coarse probe row count changed")
    for row in full_t10_rows:
        checks.check(
            row.get("accepted_use") == "full_T10_coarse_candidate_probe_not_source_policy",
            f"{row.get('paper_method')} full T=10 row allowed-use changed",
        )
        checks.check(row.get("source_policy_row_completed") is False, f"{row.get('paper_method')} full T=10 row overclosed")
        checks.check(
            row.get("source_policy_method_runner_equivalent") is False,
            f"{row.get('paper_method')} full T=10 row overclaims equivalence",
        )
        checks.check(len(row.get("metrics", [])) == 3, f"{row.get('paper_method')} full T=10 metric row count changed")
        checks.check(float(row.get("max_newton_residual_norm")) < 1.0e-8, f"{row.get('paper_method')} full T=10 residual too large")
        for metric in row.get("metrics", []):
            checks.check(math.isfinite(float(metric.get("coordinate_error_q"))), f"{row.get('paper_method')} coordinate error not finite")
            checks.check(math.isfinite(float(metric.get("velocity_error_v"))), f"{row.get('paper_method')} velocity error not finite")
        for key in ["coordinate_pairwise_orders", "velocity_pairwise_orders", "frobenius_pairwise_orders"]:
            orders = row.get(key, [])
            checks.check(len(orders) == 2, f"{row.get('paper_method')} full T=10 {key} length changed")
            for order in orders:
                checks.check(order is not None and math.isfinite(float(order)), f"{row.get('paper_method')} full T=10 {key} not finite")

    source_reference_full_t10_rows = source_reference_full_t10_candidate_probe.get("rows", [])
    checks.check(
        source_reference_full_t10_candidate_probe.get("runner_api")
        == "active_tfe_b2_source_reference_full_t10_candidate_probe",
        "source-reference full T=10 probe API changed",
    )
    checks.check(
        source_reference_full_t10_candidate_probe.get("t_final") == 10.0,
        "source-reference full T=10 probe horizon changed",
    )
    checks.check(
        source_reference_full_t10_candidate_probe.get("reference_h") == 0.0001,
        "source-reference full T=10 probe reference h changed",
    )
    checks.check(
        source_reference_full_t10_candidate_probe.get("comparison_h") == [0.1, 0.05, 0.025],
        "source-reference full T=10 probe h-grid changed",
    )
    checks.check(
        source_reference_full_t10_candidate_probe.get("source_policy_reference_invoked") is True,
        "source-reference full T=10 probe did not invoke source reference",
    )
    checks.check(
        source_reference_full_t10_candidate_probe.get("source_policy_reference_not_invoked") is False,
        "source-reference full T=10 probe reference boundary changed",
    )
    checks.check(
        source_reference_full_t10_candidate_probe.get("full_T10_source_policy_reproduction") is False,
        "source-reference full T=10 probe overclaims source-policy reproduction",
    )
    checks.check(
        source_reference_full_t10_candidate_probe.get("source_policy_rows_completed") == 0,
        "source-reference full T=10 probe overclosed rows",
    )
    checks.check(
        source_reference_full_t10_candidate_probe.get("source_policy_method_runner_equivalent") is False,
        "source-reference full T=10 probe overclaims method equivalence",
    )
    checks.check(
        source_reference_full_t10_candidate_probe.get("source_policy_dae_runner_equivalent") is False,
        "source-reference full T=10 probe overclaims DAE equivalence",
    )
    checks.check(len(source_reference_full_t10_rows) == 4, "source-reference full T=10 probe row count changed")
    for row in source_reference_full_t10_rows:
        checks.check(
            row.get("accepted_use") == "full_T10_source_reference_candidate_probe_not_source_policy",
            f"{row.get('paper_method')} source-reference full T=10 row allowed-use changed",
        )
        checks.check(row.get("source_policy_row_completed") is False, f"{row.get('paper_method')} source-reference row overclosed")
        checks.check(
            row.get("source_policy_method_runner_equivalent") is False,
            f"{row.get('paper_method')} source-reference row overclaims equivalence",
        )
        checks.check(len(row.get("metrics", [])) == 3, f"{row.get('paper_method')} source-reference metric row count changed")
        checks.check(float(row.get("max_newton_residual_norm")) < 1.0e-8, f"{row.get('paper_method')} source-reference residual too large")
        for metric in row.get("metrics", []):
            checks.check(math.isfinite(float(metric.get("coordinate_error_q"))), f"{row.get('paper_method')} source-reference coordinate error not finite")
            checks.check(math.isfinite(float(metric.get("velocity_error_v"))), f"{row.get('paper_method')} source-reference velocity error not finite")
        for key in ["coordinate_pairwise_orders", "velocity_pairwise_orders", "frobenius_pairwise_orders"]:
            orders = row.get(key, [])
            checks.check(len(orders) == 2, f"{row.get('paper_method')} source-reference {key} length changed")
            for order in orders:
                checks.check(order is not None and math.isfinite(float(order)), f"{row.get('paper_method')} source-reference {key} not finite")

    checks.check(
        tfe_m3_full_t10_formula_probe.get("runner_api") == "tfe_m3_gl_full_t10_coarse_formula_probe",
        "TFE m=3 formula probe API changed",
    )
    checks.check(tfe_m3_full_t10_formula_probe.get("t_final") == 10.0, "TFE m=3 formula probe horizon changed")
    checks.check(
        tfe_m3_full_t10_formula_probe.get("reference_h") == 0.0125,
        "TFE m=3 formula probe reference h changed",
    )
    checks.check(
        tfe_m3_full_t10_formula_probe.get("comparison_h") == [0.1, 0.05, 0.025],
        "TFE m=3 formula probe h-grid changed",
    )
    checks.check(tfe_m3_full_t10_formula_probe.get("row_count") == 1, "TFE m=3 formula probe row count changed")
    checks.check(
        tfe_m3_full_t10_formula_probe.get("full_T10_formula_probe_completed") is True,
        "TFE m=3 formula probe not marked complete",
    )
    checks.check(
        tfe_m3_full_t10_formula_probe.get("full_T10_source_policy_reproduction") is False,
        "TFE m=3 formula probe overclaims source-policy reproduction",
    )
    checks.check(
        tfe_m3_full_t10_formula_probe.get("source_policy_reference_h") == 0.0001,
        "TFE m=3 formula probe source reference h changed",
    )
    checks.check(
        tfe_m3_full_t10_formula_probe.get("source_policy_reference_not_invoked") is True,
        "TFE m=3 formula probe invoked source-policy reference",
    )
    checks.check(
        tfe_m3_full_t10_formula_probe.get("source_policy_rows_completed") == 0,
        "TFE m=3 formula probe overclosed rows",
    )
    checks.check(tfe_m3_full_t10_formula_probe.get("finite_row_count") == 1, "TFE m=3 formula probe finite rows changed")
    checks.check(
        tfe_m3_full_t10_formula_probe.get("residual_ok_row_count") == 1,
        "TFE m=3 formula probe residual rows changed",
    )
    checks.check(
        tfe_m3_full_t10_formula_probe.get("formal_expected_order") == 5,
        "TFE m=3 formula probe expected order changed",
    )
    for row in tfe_m3_full_t10_formula_probe.get("rows", []):
        checks.check(
            row.get("paper_method") == "tfe2026_TFE_m3_GL_formula_target",
            "TFE m=3 formula probe method label changed",
        )
        checks.check(row.get("expected_order") == 5, "TFE m=3 formula probe row expected order changed")
        checks.check(
            row.get("accepted_use") == "full_T10_m3_formula_probe_not_source_policy",
            "TFE m=3 formula probe allowed-use changed",
        )
        checks.check(
            row.get("source_policy_method_runner_equivalent") is False,
            "TFE m=3 formula probe overclaims method equivalence",
        )
        checks.check(row.get("source_policy_row_completed") is False, "TFE m=3 formula probe overcloses row")
        checks.check(len(row.get("metrics", [])) == 3, "TFE m=3 formula probe metric row count changed")
        checks.check(float(row.get("max_newton_residual_norm")) < 1.0e-8, "TFE m=3 formula probe residual too large")
        for metric in row.get("metrics", []):
            checks.check(math.isfinite(float(metric.get("coordinate_error_q"))), "TFE m=3 coordinate error not finite")
            checks.check(math.isfinite(float(metric.get("velocity_error_v"))), "TFE m=3 velocity error not finite")
        for key in ["coordinate_pairwise_orders", "velocity_pairwise_orders", "frobenius_pairwise_orders"]:
            orders = row.get(key, [])
            checks.check(len(orders) == 2, f"TFE m=3 formula probe {key} length changed")
            for order in orders:
                checks.check(order is not None and math.isfinite(float(order)), f"TFE m=3 formula probe {key} not finite")

    checks.check(boundary.get("can_close_source_pendulum_setup_subrequirement") is True, "setup subrequirement not closed")
    checks.check(boundary.get("can_close_tfe_b2_requirement_now") is False, "TFE B2 requirement overclosed")
    checks.check(execution.get("default_1e_4_required") is False, "default 1e-4 requirement changed")
    checks.check(execution.get("heavy_numerical_run_invoked") is False, "heavy run invoked")
    checks.check(execution.get("run_v047_invoked") is False, "run_v047 invoked")
    checks.check(execution.get("v048_campaign_invoked") is False, "v048 campaign invoked")

    for token in [
        "Status: **source parameter model implemented; runner policy open**.",
        "Parameter match with source-policy spec: `True`.",
        "Source pendulum parameter model implemented: `True`.",
        "Absolute-coordinate DAE residual smoke implemented: `True`.",
        "Absolute-coordinate frictional candidate DAE smoke implemented: `True`.",
        "Source-output time-integration smoke implemented: `True`.",
        "Source-policy time-integration runner equivalent: `False`.",
        "Source reference solution policy smoke implemented: `True`.",
        "Source reference solution policy full T=10 run: `False`.",
        "Source reference solution policy full T=10 probe implemented: `True`.",
        "Source reference solution policy full T=10 probe completed/source rows: `True/0`.",
        "Source comparator candidate runners implemented: `True`.",
        "Newmark-beta candidate runner smoke implemented: `True`.",
        "Trapezoidal candidate runner smoke implemented: `True`.",
        "Source-policy method runner equivalent: `False`.",
        "TFE m=1/2/3 candidate runner smoke implemented: `True`.",
        "Source-method candidate runner contract rows/source-policy rows/equivalent method: `5/0/False`.",
        "Source-method candidate runner contract finite/residual-below-1e-8: `True/True`.",
        "Source-policy method runner contract present/implemented: `True/False`.",
        "Source-policy method runner contract rows/source rows/equivalent method/DAE: `5/0/False/False`.",
        "TFE Appendix-B coefficient certificate checked: `True`.",
        "TFE Appendix-B coefficient certificate rows/max diff: `3/0.000e+00`.",
        "TFE m=1/2/3 source-policy runners implemented: `False`.",
        "Gauss6/FullVA source-pendulum candidate smoke implemented: `True`.",
        "Gauss6/FullVA source-pendulum candidate rows/source-policy rows: `2/0`.",
        "Gauss6/FullVA source-pendulum candidate method equivalent: `False`.",
        "Bounded source-policy runner API implemented: `True`.",
        "Bounded source-policy runner smoke implemented: `True`.",
        "Bounded source-policy runner unified dispatch: `True`.",
        "Bounded source-policy runner rows/full T=10/source-policy rows: `4/False/0`.",
        "Bounded source-policy runner method equivalent: `False`.",
        "Active TFE B2 candidate row smoke implemented: `True`.",
        "Active TFE B2 candidate row smoke full T=10: `False`.",
        "Active TFE B2 source-policy rows completed: `0`.",
        "Active TFE B2 full T=10 coarse candidate probe implemented: `True`.",
        "Active TFE B2 full T=10 coarse candidate probe full T=10/source-policy rows: `True/0`.",
        "Active TFE B2 full T=10 coarse candidate probe finite/residual-ok rows: `4/4`.",
        "Active TFE B2 full T=10 coarse candidate probe source reference invoked: `False`.",
        "TFE m=3 full T=10 coarse formula probe implemented: `True`.",
        "TFE m=3 full T=10 coarse formula probe full T=10/source-policy rows: `True/0`.",
        "TFE m=3 full T=10 coarse formula probe finite/residual-ok rows: `1/1`.",
        "TFE m=3 full T=10 coarse formula probe expected order: `5`.",
        "TFE m=3 full T=10 coarse formula probe source reference invoked: `False`.",
        "## TFE m=3 Full T=10 Coarse Formula Probe",
        "## Gauss6/FullVA Source-Pendulum Candidate Smoke",
        "Source-pendulum same-test work/precision implemented: `True`.",
        "Source-pendulum same-test work/precision methods/method rows/metric rows: `6/6/18`.",
        "Source-pendulum same-test work/precision source-policy rows/external superiority allowed: `0/False`.",
        "Absolute-coordinate planar-lift trajectory probe implemented: `True`.",
        "Absolute-coordinate planar-lift methods/rows/metric rows: `6/12/36`.",
        "Absolute-coordinate planar-lift source-policy rows/equivalent DAE runner: `0/False`.",
        "Bounded absolute-coordinate DAE trajectory runner implemented: `True`.",
        "Bounded absolute-coordinate DAE trajectory runner rows/metric rows/step residual rows: `4/12/56`.",
        "Bounded absolute-coordinate DAE trajectory runner source-policy rows/equivalent DAE/monolithic integrator: `0/False/False`.",
        "Monolithic absolute-coordinate DAE candidate runner implemented: `True`.",
        "Monolithic absolute-coordinate DAE candidate runner rows/metric rows/step residual rows: `4/12/56`.",
        "Monolithic absolute-coordinate DAE candidate runner source-policy rows/equivalent DAE/monolithic integrator: `0/False/False`.",
        "Source-policy absolute-coordinate DAE runner contract present/implemented: `True/False`.",
        "Source-policy absolute-coordinate DAE runner contract rows/metric rows/step residual rows/source rows/equivalent/monolithic: `4/12/56/0/False/False`.",
        "DAE trajectory bridge contract implemented: `True`.",
        "DAE trajectory bridge contract rows/matched/source rows: `12/12/0`.",
        "DAE trajectory bridge contract all finite/all DAE residuals below 1e-10: `True/True`.",
        "DAE trajectory bridge contract equivalent DAE/monolithic integrator: `False/False`.",
        "Candidate-friction DAE trajectory contract implemented: `True`.",
        "Candidate-friction DAE trajectory contract rows/step residual rows/source rows: `12/56/0`.",
        "Candidate-friction DAE trajectory contract finite/residual-below-1e-9/friction-power-nonpositive: `True/True/True`.",
        "Candidate-friction DAE trajectory contract equivalent DAE/method/source-law/monolithic: `False/False/False/False`.",
        "Gauss6/FullVA DAE candidate contract rows/source-policy rows/equivalent DAE/FullVA: `1/0/False/False`.",
        "Gauss6/FullVA DAE candidate contract finite/residual-below-1e-8: `True/True`.",
        "Source-policy Gauss6/FullVA absolute-coordinate DAE runner contract present/implemented: `True/False`.",
        "Source-policy Gauss6/FullVA absolute-coordinate DAE runner contract rows/source rows/equivalent DAE/FullVA/monolithic: `1/0/False/False/False`.",
        "## DAE Trajectory Bridge Contract",
        "methods/source metric rows/DAE metric rows/contract rows: `4` / `12` / `12` / `12`.",
        "matched contract rows: `12`.",
        "all rows finite: `True`.",
        "all DAE residuals below 1e-10: `True`.",
        "## Source-Pendulum Same-Test Work/Precision",
        "## Absolute-Coordinate Planar-Lift Trajectory Probe",
        "FullVA DAE source-policy equivalent: `False`.",
        "full T=10 formula probe completed: `True`.",
        "formal expected order: `5`.",
        "## Source Reference Full T=10 Probe",
        "source/check steps: `100000` / `200000`.",
        "Source-policy DAE runner equivalent: `False`.",
        "Source output/error policy encoded: `True`.",
        "## TFE Appendix-B Coefficient Certificate",
        "all formula matches: `True`.",
        "scope: `coefficient_formula_certificate_only_not_source_policy_runner_equivalence`.",
        "Brown--McPhee candidate friction law encoded: `True`.",
        "Frictional candidate RHS smoke implemented: `True`.",
        "Pendulum DAE runner implemented: `False`.",
        "Brown--McPhee friction law implemented: `False`.",
        "Source-policy rows completed: `0`.",
        "Source-policy runner-equivalence preflight: `preflight_ready_runner_equivalence_open`.",
        "Source-policy runner-equivalence preflight closed/open/source rows: `25/6/0`.",
        "## Source-Policy Runner Equivalence Preflight",
        "Closed preconditions/open blockers: `25/6`.",
        "Source-policy rows closed by preflight: `0`.",
        "Brown--McPhee source-code-equivalent law: `False`.",
        "TFE/Newmark/trapezoidal source-policy runners implemented: `False`.",
        "Gauss6/FullVA source-policy runner implemented: `False`.",
        "Full T=10 source grid policy resolved: `False`.",
        "Can close TFE lane from preflight: `False`.",
        "absolute_coordinate_planar_lift_trajectory_probe_implemented",
        "bounded_absolute_coordinate_dae_trajectory_runner_implemented",
        "source_policy_absolute_coordinate_dae_runner_contract_present",
        "source_policy_tfe_newmark_trapezoidal_method_runner_contract_present",
        "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_contract_present",
        "dae_trajectory_bridge_contract_implemented",
        "source_reference_full_T10_h1e4_probe_completed",
        "active_tfe_b2_source_reference_full_T10_candidate_probe_implemented",
        "accepted_source_policy_work_precision_rows_not_executed_or_bound",
        "Can close TFE B2 requirement now: `False`.",
        "named non-equivalent method-runner and Gauss6/FullVA DAE runner contract entrypoints",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("TFE source-pendulum model audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("TFE source-pendulum model audit validation: PASS")
    print("source_pendulum_parameter_model_implemented=True")
    print("frictionless_rhs_smoke_implemented=True")
    print("source_error_norm_and_output_policy_encoded=True")
    print("brown_mcphee_candidate_friction_law_encoded=True")
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
    print("gauss6_fullva_source_pendulum_candidate_rows=2")
    print("gauss6_fullva_source_pendulum_candidate_source_policy_rows_completed=0")
    print("source_pendulum_same_test_work_precision_implemented=True")
    print("source_pendulum_same_test_work_precision_metric_rows=18")
    print("absolute_coordinate_planar_lift_trajectory_probe_implemented=True")
    print("absolute_coordinate_planar_lift_trajectory_probe_rows=12")
    print("absolute_coordinate_planar_lift_trajectory_probe_source_policy_rows_completed=0")
    print("source_policy_absolute_coordinate_dae_runner_contract_present=True")
    print("source_policy_absolute_coordinate_dae_runner_implemented=False")
    print("dae_trajectory_bridge_contract_implemented=True")
    print("dae_trajectory_bridge_contract_rows=12")
    print("dae_trajectory_bridge_contract_source_policy_rows_completed=0")
    print("tfe_appendix_b_coefficient_certificate_checked=True")
    print("bounded_source_policy_runner_smoke_implemented=True")
    print("active_tfe_b2_candidate_row_smoke_implemented=True")
    print("active_tfe_b2_full_T10_coarse_candidate_probe_implemented=True")
    print("active_tfe_b2_source_reference_full_T10_candidate_probe_implemented=True")
    print("tfe_m3_full_T10_coarse_formula_probe_implemented=True")
    print("pendulum_dae_runner_implemented=False")
    print("source_policy_rows_completed=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
