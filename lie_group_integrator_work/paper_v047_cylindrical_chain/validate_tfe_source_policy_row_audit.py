#!/usr/bin/env python3
"""Validate the original-TFE source-policy row audit."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_json(path: Path) -> dict[str, Any]:
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
        audit = read_json(PAPER / "TFE_SOURCE_POLICY_ROW_AUDIT.json")
        audit_md = read_text(PAPER / "TFE_SOURCE_POLICY_ROW_AUDIT.md")
        b2 = read_json(PAPER / "B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.json")
        spec = read_json(PAPER / "TFE_SOURCE_POLICY_SPEC.json")
        model_audit = read_json(PAPER / "TFE_SOURCE_PENDULUM_MODEL_AUDIT.json")
        row_ledger = read_json(PAPER / "SOURCE_POLICY_ROW_CLOSURE_LEDGER.json")
        closure_manifest = read_json(PAPER / "EXTERNAL_SOURCE_POLICY_CLOSURE_MANIFEST.json")
        external_case = read_json(PAPER / "EXTERNAL_CASE_EVIDENCE_RECONCILIATION.json")
        grid_audit = read_json(PAPER / "TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.json")
        algorithm_literal_endpoint_probe = read_json(PAPER / "TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE.json")
    except Exception as exc:  # noqa: BLE001
        print(f"TFE source-policy row audit validation: FAIL\n- {exc}")
        return 1

    active_b2_rows = [
        row
        for row in b2.get("rows", [])
        if row.get("suite_id") == "tfe2026_original_pendulum" and row.get("active_b2_requirement") is True
    ]
    spec_gap = spec.get("runner_gap", {})
    criteria = audit.get("closure_criteria", {})
    decision = audit.get("decision", {})
    execution = audit.get("execution_policy", {})
    rows = audit.get("rows", [])
    active_b2_smoke = audit.get("active_tfe_b2_candidate_row_smoke", {})
    bounded_runner_smoke = audit.get("bounded_source_policy_runner_smoke", {})
    full_t10_coarse_probe = audit.get("active_tfe_b2_full_T10_coarse_candidate_probe", {})
    source_reference_full_t10_candidate_probe = audit.get(
        "active_tfe_b2_source_reference_full_T10_candidate_probe",
        {},
    )
    tfe_m3_full_t10_formula_probe = audit.get("tfe_m3_full_T10_coarse_formula_probe", {})
    gauss6_candidate_smoke = audit.get("gauss6_fullva_source_pendulum_candidate_smoke", {})
    gauss6_dae_candidate_contract = audit.get("gauss6_fullva_dae_candidate_contract_smoke", {})
    source_files = audit.get("source_files", {})
    runner_equivalence_preflight = audit.get("source_policy_runner_equivalence_preflight", {})
    runner_equivalence_gap_matrix = audit.get("source_policy_runner_equivalence_gap_matrix", {})
    model_runner_equivalence_preflight = model_audit.get("source_policy_runner_equivalence_preflight", {})
    source_spec_boundary = spec.get("candidate_vs_source_policy_boundary", {})
    audit_boundary = audit.get("candidate_vs_source_policy_boundary", {})

    checks.check(audit.get("schema") == "tfe-source-policy-row-audit-v1", "schema changed")
    checks.check(
        audit.get("status") == "source_policy_spec_extracted_runner_rows_not_closed",
        "status changed",
    )
    checks.check(audit.get("submission_ready") is False, "audit overclaims submission readiness")
    checks.check(audit.get("suite_id") == "tfe2026_original_pendulum", "suite id changed")
    checks.check(audit.get("source_suite") == "chaturvedi_sandu_sandu_tfe_pendulum", "source suite changed")
    checks.check(
        audit.get("evidence_class") == "source_spec_extracted_candidate_scaffold_present_source_policy_rows_open",
        "evidence class changed",
    )
    checks.check(audit.get("source_policy_external_superiority_allowed") is False, "source-policy superiority overclaimed")
    checks.check(audit.get("external_superiority_claim_allowed") is False, "external superiority overclaimed")
    checks.check(audit.get("active_b2_flagged_rows") == len(active_b2_rows) == 0, "active B2 row count changed")
    checks.check(audit.get("audited_active_rows") == len(rows) == 0, "audited row count changed")
    checks.check(audit.get("source_policy_closed_rows") == 0, "source-policy rows unexpectedly closed")
    checks.check(audit.get("external_superiority_ready_rows") == 0, "external-superiority-ready rows unexpectedly present")
    checks.check(audit.get("source_policy_rows_completed") == spec_gap.get("source_policy_rows_completed") == 0, "completed rows changed")
    checks.check(
        audit.get("source_policy_runner_equivalence_preflight_status")
        == model_runner_equivalence_preflight.get("status")
        == "preflight_ready_runner_equivalence_open",
        "runner-equivalence preflight status not carried into row audit",
    )
    checks.check(
        audit.get("source_policy_runner_equivalence_preflight_closed_preconditions")
        == model_runner_equivalence_preflight.get("closed_precondition_count")
        == 25,
        "runner-equivalence precondition count not carried into row audit",
    )
    checks.check(
        audit.get("source_policy_runner_equivalence_preflight_open_blockers")
        == model_runner_equivalence_preflight.get("open_blocker_count")
        == 6,
        "runner-equivalence blocker count not carried into row audit",
    )
    checks.check(
        audit.get("source_policy_runner_equivalence_preflight_rows_closed")
        == model_runner_equivalence_preflight.get("source_policy_rows_closed_by_preflight")
        == 0,
        "runner-equivalence preflight overclosed rows in row audit",
    )
    checks.check(
        audit.get("source_policy_runner_equivalence_preflight_can_close_lane")
        == model_runner_equivalence_preflight.get("can_close_tfe_lane_from_preflight")
        is False,
        "runner-equivalence preflight overcloses TFE lane in row audit",
    )
    checks.check(
        runner_equivalence_preflight == model_runner_equivalence_preflight,
        "runner-equivalence preflight payload drifted from model audit",
    )
    checks.check(
        runner_equivalence_preflight.get("source_policy_dae_runner_equivalent") is False,
        "runner-equivalence preflight overclaims DAE equivalence",
    )
    checks.check(
        runner_equivalence_preflight.get("pendulum_dae_runner_implemented") is False,
        "runner-equivalence preflight overclaims pendulum DAE runner",
    )
    checks.check(
        runner_equivalence_preflight.get("heavy_numerical_run_invoked") is False,
        "runner-equivalence preflight invoked heavy run",
    )
    checks.check(
        runner_equivalence_gap_matrix.get("schema")
        == "tfe-source-policy-runner-equivalence-gap-matrix-v1",
        "runner-equivalence gap matrix schema changed",
    )
    checks.check(
        runner_equivalence_gap_matrix.get("status") == runner_equivalence_preflight.get("status"),
        "runner-equivalence gap matrix status drifted from preflight",
    )
    checks.check(
        runner_equivalence_gap_matrix.get("closed_precondition_count") == 25
        and len(runner_equivalence_gap_matrix.get("closed_preconditions", [])) == 25,
        "runner-equivalence gap matrix closed precondition count changed",
    )
    checks.check(
        runner_equivalence_gap_matrix.get("open_blocker_count") == 6
        and len(runner_equivalence_gap_matrix.get("open_blockers", [])) == 6,
        "runner-equivalence gap matrix open blocker count changed",
    )
    checks.check(
        runner_equivalence_gap_matrix.get("source_policy_rows_closed_by_preflight") == 0,
        "runner-equivalence gap matrix overclosed source-policy rows",
    )
    checks.check(
        runner_equivalence_gap_matrix.get("can_close_tfe_lane_from_preflight") is False
        and runner_equivalence_gap_matrix.get("b4_b7_can_close_from_preflight") is False,
        "runner-equivalence gap matrix overcloses TFE/B4/B7",
    )
    checks.check(
        runner_equivalence_gap_matrix.get("heavy_numerical_run_invoked") is False
        and runner_equivalence_gap_matrix.get("run_v047_invoked") is False
        and runner_equivalence_gap_matrix.get("v048_runner_invoked") is False,
        "runner-equivalence gap matrix records an invoked run",
    )
    checks.check(
        runner_equivalence_gap_matrix.get("ready_to_execute_source_policy_now") is False,
        "runner-equivalence gap matrix marks source-policy rows executable too early",
    )
    checks.check(
        runner_equivalence_gap_matrix.get("first_required_artifact")
        == "source-equivalent DAE runner certificate for the original TFE pendulum policy",
        "runner-equivalence first artifact changed",
    )
    checks.check(
        audit_boundary == source_spec_boundary,
        "candidate/source-policy boundary drifted from TFE source-policy spec",
    )
    checks.check(
        audit_boundary.get("candidate_scaffold_present") is True
        and audit_boundary.get("candidate_scaffold_allowed_use")
        == "diagnostic_scaffold_only_not_source_policy_reproduction"
        and audit_boundary.get("source_policy_runner_required_for_promotion") is True,
        "candidate/source-policy boundary missing or weakened in row audit",
    )
    checks.check(
        audit_boundary.get("source_policy_dae_runner_equivalent") is False
        and audit_boundary.get("source_policy_method_runner_equivalent") is False
        and audit_boundary.get("source_policy_rows_completed") == 0
        and audit_boundary.get("external_superiority_allowed") is False,
        "candidate/source-policy boundary overclaims row-audit readiness",
    )
    expected_gap_artifacts = {
        "brown_mcphee_source_code_equivalent_law_open": "Brown--McPhee source-code-equivalent friction-law certificate",
        "pendulum_absolute_coordinate_source_policy_dae_runner_missing": "absolute-coordinate T=10 source-policy DAE runner equivalence certificate",
        "tfe_newmark_trapezoidal_source_policy_method_runners_missing": "TFE m=1/m=2/m=3, Newmark-beta, and trapezoidal source-policy method-runner certificate",
        "gauss6_fullva_absolute_coordinate_source_policy_runner_missing": "Gauss6/FullVA absolute-coordinate source-pendulum DAE runner certificate",
        "full_T10_source_grid_endpoint_policy_open": "full T=10 endpoint/output sampling policy for endpoint-incompatible h rows",
        "accepted_source_policy_work_precision_rows_not_executed_or_bound": "accepted source-policy work/precision row table binding error, order, runtime, and work metrics",
    }
    observed_gap_artifacts = {
        row.get("id"): row.get("first_required_artifact")
        for row in runner_equivalence_gap_matrix.get("open_blockers", [])
    }
    checks.check(observed_gap_artifacts == expected_gap_artifacts, "runner-equivalence open blocker artifact map changed")
    grid_gap = next(
        (
            row
            for row in runner_equivalence_gap_matrix.get("open_blockers", [])
            if row.get("id") == "full_T10_source_grid_endpoint_policy_open"
        ),
        {},
    )
    checks.check(grid_gap.get("endpoint_incompatible_rows") == 4, "runner-equivalence grid gap row count changed")
    checks.check(audit.get("source_policy_spec_extracted") is True, "source spec extraction marker changed")
    checks.check(audit.get("source_pendulum_parameter_model_implemented") is True, "source parameter model missing")
    checks.check(audit.get("frictionless_planar_rhs_smoke_implemented") is True, "frictionless RHS smoke missing")
    checks.check(
        audit.get("absolute_coordinate_dae_residual_smoke_implemented") is True,
        "absolute-coordinate DAE residual smoke not carried into row audit",
    )
    checks.check(
        audit.get("absolute_coordinate_frictional_candidate_dae_smoke_implemented") is True,
        "absolute-coordinate frictional candidate DAE smoke not carried into row audit",
    )
    checks.check(
        audit.get("source_output_time_integration_smoke_implemented") is True,
        "source-output time-integration smoke not carried into row audit",
    )
    checks.check(
        audit.get("source_policy_time_integration_runner_equivalent") is False,
        "source-policy time-integration equivalence overclaimed",
    )
    checks.check(
        audit.get("source_reference_solution_policy_smoke_implemented") is True,
        "source reference solution policy smoke not carried into row audit",
    )
    checks.check(
        audit.get("source_reference_solution_policy_smoke_full_T10") is False,
        "source reference solution policy smoke overclaims full T=10 run",
    )
    checks.check(
        audit.get("source_reference_solution_policy_full_T10_probe_completed") is True,
        "source reference full T=10 probe not carried into row audit",
    )
    checks.check(
        audit.get("source_reference_solution_policy_full_T10_probe_steps") == 100000,
        "source reference full T=10 source step count changed",
    )
    checks.check(
        audit.get("source_reference_solution_policy_full_T10_probe_check_steps") == 200000,
        "source reference full T=10 check step count changed",
    )
    checks.check(
        audit.get("source_reference_solution_policy_full_T10_probe_rows_completed") == 0,
        "source reference full T=10 probe overclosed rows",
    )
    checks.check(
        float(audit.get("source_reference_solution_policy_full_T10_probe_coordinate_error", 1.0)) < 1.0e-10,
        "source reference full T=10 coordinate error too large",
    )
    checks.check(
        float(audit.get("source_reference_solution_policy_full_T10_probe_velocity_error", 1.0)) < 1.0e-10,
        "source reference full T=10 velocity error too large",
    )
    checks.check(
        audit.get("source_comparator_candidate_runners_implemented") is True,
        "source comparator candidate runners not carried into row audit",
    )
    checks.check(
        audit.get("newmark_beta_candidate_runner_smoke_implemented") is True,
        "Newmark-beta candidate runner not carried into row audit",
    )
    checks.check(
        audit.get("trapezoidal_candidate_runner_smoke_implemented") is True,
        "trapezoidal candidate runner not carried into row audit",
    )
    checks.check(
        audit.get("source_policy_method_runner_equivalent") is False,
        "source-policy method runner equivalence overclaimed",
    )
    checks.check(
        audit.get("tfe_m1_m2_m3_candidate_runner_smoke_implemented") is True,
        "TFE m=1/2/3 candidate runner smoke not carried into row audit",
    )
    checks.check(
        audit.get("source_method_candidate_runner_contract_implemented")
        == model_audit.get("source_method_candidate_runner_contract_implemented")
        is True,
        "source-method candidate runner contract not carried into row audit",
    )
    checks.check(
        audit.get("source_method_candidate_runner_contract_rows")
        == model_audit.get("source_method_candidate_runner_contract_rows")
        == 5,
        "source-method candidate runner contract row count changed in row audit",
    )
    checks.check(
        audit.get("source_method_candidate_runner_contract_all_step_states_finite")
        == model_audit.get("source_method_candidate_runner_contract_all_step_states_finite")
        is True,
        "source-method candidate runner contract finite marker changed in row audit",
    )
    checks.check(
        audit.get("source_method_candidate_runner_contract_all_candidate_residuals_below_1e_8")
        == model_audit.get("source_method_candidate_runner_contract_all_candidate_residuals_below_1e_8")
        is True,
        "source-method candidate runner contract residual marker changed in row audit",
    )
    checks.check(
        audit.get("source_method_candidate_runner_contract_source_policy_rows_completed")
        == model_audit.get("source_method_candidate_runner_contract_source_policy_rows_completed")
        == 0,
        "source-method candidate runner contract overcloses source-policy rows in row audit",
    )
    checks.check(
        audit.get("source_method_candidate_runner_contract_method_equivalent")
        == model_audit.get("source_method_candidate_runner_contract_method_equivalent")
        is False,
        "source-method candidate runner contract overclaims method equivalence in row audit",
    )
    checks.check(
        audit.get("source_method_candidate_runner_contract_dae_equivalent")
        == model_audit.get("source_method_candidate_runner_contract_dae_equivalent")
        is False,
        "source-method candidate runner contract overclaims DAE equivalence in row audit",
    )
    checks.check(
        audit.get("tfe_appendix_b_coefficient_certificate_checked") is True,
        "TFE Appendix-B coefficient certificate not carried into row audit",
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
        "TFE source-policy runners unexpectedly carried as implemented",
    )
    checks.check(
        audit.get("bounded_source_policy_runner_api_implemented") is True,
        "bounded source-policy runner API not carried into row audit",
    )
    checks.check(
        audit.get("bounded_source_policy_runner_smoke_implemented") is True,
        "bounded source-policy runner smoke not carried into row audit",
    )
    checks.check(
        audit.get("bounded_source_policy_runner_unified_dispatch") is True,
        "bounded source-policy runner lost unified dispatch marker",
    )
    checks.check(audit.get("bounded_source_policy_runner_method_count") == 4, "bounded runner method count changed")
    checks.check(audit.get("bounded_source_policy_runner_rows") == 4, "bounded runner row count changed")
    checks.check(audit.get("bounded_source_policy_runner_full_T10") is False, "bounded runner overclaims full T=10")
    checks.check(
        audit.get("bounded_source_policy_runner_source_policy_rows_completed") == 0,
        "bounded runner overcloses source-policy rows",
    )
    checks.check(
        audit.get("bounded_source_policy_runner_method_equivalent") is False,
        "bounded runner overclaims method equivalence",
    )
    checks.check(
        audit.get("bounded_source_policy_runner_accepted_use")
        == "bounded_candidate_runner_api_only_not_source_policy",
        "bounded runner accepted-use boundary missing",
    )
    checks.check(
        audit.get("bounded_source_policy_runner_dae_runner_equivalent") is False,
        "bounded runner overclaims DAE equivalence",
    )
    checks.check(
        audit.get("bounded_source_policy_runner_monolithic_integrator") is False,
        "bounded runner overclaims monolithic integration",
    )
    checks.check(
        audit.get("active_tfe_b2_candidate_row_smoke_implemented") is True,
        "active B2 candidate smoke not carried into row audit",
    )
    checks.check(
        audit.get("active_tfe_b2_candidate_row_smoke_full_T10") is False,
        "active B2 smoke overclaims full T=10",
    )
    checks.check(
        audit.get("active_tfe_b2_source_policy_rows_completed") == 0,
        "active B2 smoke overcloses source-policy rows",
    )
    checks.check(
        audit.get("active_tfe_b2_full_T10_coarse_candidate_probe_implemented") is True,
        "active B2 full T=10 coarse probe not carried into row audit",
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
        "active B2 full T=10 coarse probe finite rows changed",
    )
    checks.check(
        audit.get("active_tfe_b2_full_T10_coarse_candidate_probe_residual_ok_rows") == 4,
        "active B2 full T=10 coarse probe residual rows changed",
    )
    checks.check(
        audit.get("active_tfe_b2_source_reference_full_T10_candidate_probe_implemented") is True,
        "active B2 source-reference full T=10 probe not carried into row audit",
    )
    checks.check(
        audit.get("active_tfe_b2_source_reference_full_T10_candidate_probe_full_T10") is True,
        "active B2 source-reference full T=10 probe did not run full horizon",
    )
    checks.check(
        audit.get(
            "active_tfe_b2_source_reference_full_T10_candidate_probe_source_policy_reference_invoked"
        )
        is True,
        "active B2 source-reference full T=10 probe did not invoke reference",
    )
    checks.check(
        audit.get(
            "active_tfe_b2_source_reference_full_T10_candidate_probe_source_policy_rows_completed"
        )
        == 0,
        "active B2 source-reference full T=10 probe overcloses rows",
    )
    checks.check(
        audit.get("active_tfe_b2_source_reference_full_T10_candidate_probe_finite_rows") == 4,
        "active B2 source-reference full T=10 probe finite rows changed",
    )
    checks.check(
        audit.get("active_tfe_b2_source_reference_full_T10_candidate_probe_residual_ok_rows") == 4,
        "active B2 source-reference full T=10 probe residual rows changed",
    )
    checks.check(
        audit.get("active_tfe_b2_source_reference_full_T10_candidate_probe_method_equivalent")
        is False,
        "active B2 source-reference full T=10 probe overclaims method equivalence",
    )
    checks.check(
        audit.get("tfe_m3_full_T10_coarse_formula_probe_implemented") is True,
        "TFE m=3 full T=10 formula probe not carried into row audit",
    )
    checks.check(
        audit.get("tfe_m3_full_T10_coarse_formula_probe_full_T10") is True,
        "TFE m=3 full T=10 formula probe did not run full horizon",
    )
    checks.check(
        audit.get("tfe_m3_full_T10_coarse_formula_probe_source_policy_rows_completed") == 0,
        "TFE m=3 formula probe overcloses source-policy rows",
    )
    checks.check(
        audit.get("tfe_m3_full_T10_coarse_formula_probe_source_policy_reference_not_invoked") is True,
        "TFE m=3 formula probe invoked source-policy reference",
    )
    checks.check(
        audit.get("tfe_m3_full_T10_coarse_formula_probe_finite_rows") == 1,
        "TFE m=3 formula probe finite rows changed",
    )
    checks.check(
        audit.get("tfe_m3_full_T10_coarse_formula_probe_residual_ok_rows") == 1,
        "TFE m=3 formula probe residual rows changed",
    )
    checks.check(
        audit.get("tfe_m3_full_T10_coarse_formula_probe_formal_expected_order") == 5,
        "TFE m=3 formula probe expected order changed",
    )
    checks.check(active_b2_smoke.get("t_final") == 0.024, "active B2 smoke t_final changed")
    checks.check(active_b2_smoke.get("reference_h") == 1.0e-4, "active B2 smoke reference h changed")
    checks.check(active_b2_smoke.get("comparison_h") == [0.012, 0.006, 0.003], "active B2 h-grid changed")
    checks.check(active_b2_smoke.get("row_count") == 4, "active B2 smoke row count changed")
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
    checks.check(full_t10_coarse_probe.get("row_count") == 4, "full T=10 coarse probe row count changed")
    checks.check(
        full_t10_coarse_probe.get("full_T10_candidate_probe_completed") is True,
        "full T=10 coarse probe not marked complete",
    )
    checks.check(
        full_t10_coarse_probe.get("full_T10_source_policy_reproduction") is False,
        "full T=10 coarse probe overclaims source-policy reproduction",
    )
    checks.check(
        full_t10_coarse_probe.get("source_policy_reference_h") == 1.0e-4,
        "full T=10 coarse probe source reference h changed",
    )
    checks.check(
        full_t10_coarse_probe.get("source_policy_reference_not_invoked") is True,
        "full T=10 coarse probe invoked source-policy reference",
    )
    checks.check(full_t10_coarse_probe.get("source_policy_rows_completed") == 0, "full T=10 coarse probe overclosed rows")
    checks.check(full_t10_coarse_probe.get("finite_row_count") == 4, "full T=10 coarse probe finite rows changed")
    checks.check(full_t10_coarse_probe.get("residual_ok_row_count") == 4, "full T=10 coarse probe residual rows changed")
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
        source_reference_full_t10_candidate_probe.get("reference_h") == 1.0e-4,
        "source-reference full T=10 probe reference h changed",
    )
    checks.check(
        source_reference_full_t10_candidate_probe.get("comparison_h") == [0.1, 0.05, 0.025],
        "source-reference full T=10 probe h-grid changed",
    )
    checks.check(
        source_reference_full_t10_candidate_probe.get("row_count") == 4,
        "source-reference full T=10 probe row count changed",
    )
    checks.check(
        source_reference_full_t10_candidate_probe.get("source_policy_reference_invoked") is True,
        "source-reference full T=10 probe reference invocation changed",
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
        tfe_m3_full_t10_formula_probe.get("source_policy_reference_h") == 1.0e-4,
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
    checks.check(
        active_b2_smoke.get("full_T10_source_policy_reproduction") is False,
        "active B2 smoke overclaims source-policy reproduction",
    )
    checks.check(
        active_b2_smoke.get("source_policy_method_runner_equivalent") is False,
        "active B2 smoke overclaims method equivalence",
    )
    checks.check(active_b2_smoke.get("source_policy_rows_completed") == 0, "active B2 smoke overcloses rows")
    checks.check(bounded_runner_smoke.get("runner_api") == "bounded_source_policy_runner_smoke", "bounded runner API changed")
    checks.check(bounded_runner_smoke.get("t_final") == 0.024, "bounded runner t_final changed")
    checks.check(bounded_runner_smoke.get("reference_h") == 1.0e-4, "bounded runner reference h changed")
    checks.check(bounded_runner_smoke.get("comparison_h") == [0.012, 0.006, 0.003], "bounded runner h-grid changed")
    checks.check(bounded_runner_smoke.get("row_count") == 4, "bounded runner row count changed")
    checks.check(bounded_runner_smoke.get("method_count") == 4, "bounded runner method count changed")
    checks.check(bounded_runner_smoke.get("unified_method_dispatch") is True, "bounded runner dispatch marker changed")
    checks.check(
        bounded_runner_smoke.get("full_T10_source_policy_reproduction") is False,
        "bounded runner overclaims source-policy reproduction",
    )
    checks.check(
        bounded_runner_smoke.get("source_policy_method_runner_equivalent") is False,
        "bounded runner overclaims method equivalence",
    )
    checks.check(bounded_runner_smoke.get("source_policy_rows_completed") == 0, "bounded runner overcloses rows")
    checks.check(
        bounded_runner_smoke.get("accepted_use")
        == "bounded_candidate_runner_api_only_not_source_policy",
        "bounded runner smoke accepted-use boundary missing",
    )
    checks.check(
        bounded_runner_smoke.get("source_policy_dae_runner_equivalent") is False,
        "bounded runner smoke overclaims DAE equivalence",
    )
    checks.check(
        bounded_runner_smoke.get("monolithic_absolute_coordinate_dae_time_integrator") is False,
        "bounded runner smoke overclaims monolithic integration",
    )
    checks.check(audit.get("source_policy_dae_runner_equivalent") is False, "source-policy DAE runner overclaimed")
    checks.check(audit.get("source_error_norm_and_output_policy_encoded") is True, "source output policy not encoded")
    checks.check(
        audit.get("brown_mcphee_candidate_friction_law_encoded") is True,
        "candidate friction law not carried into row audit",
    )
    checks.check(
        audit.get("brown_mcphee_source_text_anchor_found") is True,
        "Brown--McPhee source-text anchor not carried into row audit",
    )
    checks.check(
        audit.get("brown_mcphee_source_text_names_velocity_model") is True,
        "Brown--McPhee source velocity-model anchor missing from row audit",
    )
    checks.check(
        audit.get("brown_mcphee_source_text_reports_mu_values") is True,
        "Brown--McPhee mu anchor missing from row audit",
    )
    checks.check(
        audit.get("brown_mcphee_published_formula_structure_encoded") is True,
        "Brown--McPhee formula structure not carried into row audit",
    )
    checks.check(
        audit.get("brown_mcphee_source_code_equivalent_law") is False,
        "Brown--McPhee source-code equivalence overclaimed in row audit",
    )
    checks.check(
        audit.get("brown_mcphee_transition_velocity_policy_resolved_from_source") is False,
        "Brown--McPhee transition velocity unexpectedly resolved in row audit",
    )
    checks.check(
        audit.get("frictional_planar_candidate_rhs_smoke_implemented") is True,
        "frictional candidate smoke not carried into row audit",
    )
    checks.check(
        audit.get("candidate_friction_law_provenance")
        == "v022_revolute_brown_mcphee_surrogate_not_source_policy_equivalent",
        "candidate friction provenance changed",
    )
    checks.check(audit.get("pendulum_dae_runner_implemented") is False, "pendulum runner unexpectedly implemented")
    checks.check(audit.get("brown_mcphee_friction_law_implemented") is False, "friction law unexpectedly implemented")
    checks.check(audit.get("tfe_m1_m2_m3_runner_implemented") is False, "TFE runner unexpectedly implemented")
    checks.check(audit.get("newmark_trapezoidal_runner_implemented") is False, "Newmark/trapezoidal runner unexpectedly implemented")
    checks.check(
        audit.get("gauss6_fullva_absolute_coordinate_source_policy_runner_implemented") is False,
        "Gauss6 absolute-coordinate source-policy runner unexpectedly implemented",
    )
    checks.check(
        audit.get("gauss6_fullva_on_source_pendulum_implemented") is False,
        "Gauss6 legacy source-policy runner unexpectedly implemented",
    )
    checks.check(
        audit.get("gauss6_fullva_source_pendulum_candidate_smoke_implemented") is True,
        "Gauss6 source-pendulum candidate smoke not carried into row audit",
    )
    checks.check(
        audit.get("gauss6_fullva_source_pendulum_candidate_rows") == 2,
        "Gauss6 source-pendulum candidate row count changed",
    )
    checks.check(
        audit.get("gauss6_fullva_source_pendulum_candidate_source_policy_rows_completed") == 0,
        "Gauss6 source-pendulum candidate overclosed source-policy rows",
    )
    checks.check(
        audit.get("gauss6_fullva_source_pendulum_candidate_method_equivalent") is False,
        "Gauss6 source-pendulum candidate overclaims method equivalence",
    )
    checks.check(
        audit.get("gauss6_fullva_dae_candidate_contract_implemented") is True,
        "Gauss6 DAE candidate contract not carried into row audit",
    )
    checks.check(
        audit.get("gauss6_fullva_dae_candidate_contract_rows") == 1,
        "Gauss6 DAE candidate contract row count changed",
    )
    checks.check(
        audit.get("gauss6_fullva_dae_candidate_contract_source_policy_rows_completed") == 0,
        "Gauss6 DAE candidate contract overclosed source-policy rows",
    )
    checks.check(
        audit.get("gauss6_fullva_dae_candidate_contract_method_equivalent") is False,
        "Gauss6 DAE candidate contract overclaims method equivalence",
    )
    checks.check(
        audit.get("gauss6_fullva_dae_candidate_contract_dae_equivalent") is False,
        "Gauss6 DAE candidate contract overclaims DAE equivalence",
    )
    checks.check(
        audit.get("gauss6_fullva_dae_candidate_contract_fullva_dae_equivalent") is False,
        "Gauss6 DAE candidate contract overclaims FullVA DAE equivalence",
    )
    checks.check(
        audit.get("gauss6_fullva_dae_candidate_contract_absolute_source_policy_runner_implemented") is False,
        "Gauss6 DAE candidate contract overclaims absolute source-policy runner implementation",
    )
    checks.check(
        audit.get("gauss6_fullva_dae_candidate_contract_all_step_states_finite") is True,
        "Gauss6 DAE candidate contract finite marker changed",
    )
    checks.check(
        audit.get("gauss6_fullva_dae_candidate_contract_all_candidate_residuals_below_1e_8") is True,
        "Gauss6 DAE candidate contract residual marker changed",
    )
    checks.check(
        gauss6_candidate_smoke.get("runner_api") == "source_gauss6_fullva_candidate_runner_smoke",
        "Gauss6 candidate smoke API changed",
    )
    checks.check(gauss6_candidate_smoke.get("t_final") == 1.0, "Gauss6 candidate smoke t_final changed")
    checks.check(gauss6_candidate_smoke.get("reference_h") == 0.00025, "Gauss6 candidate smoke reference h changed")
    checks.check(
        gauss6_candidate_smoke.get("comparison_h") == [0.1, 0.05, 0.025],
        "Gauss6 candidate smoke h-grid changed",
    )
    checks.check(gauss6_candidate_smoke.get("row_count") == 2, "Gauss6 candidate smoke row count changed")
    checks.check(
        gauss6_candidate_smoke.get("fullva_dae_source_policy_equivalent") is False,
        "Gauss6 candidate smoke overclaims FullVA DAE equivalence",
    )
    checks.check(
        gauss6_candidate_smoke.get("source_policy_method_runner_equivalent") is False,
        "Gauss6 candidate smoke overclaims method equivalence",
    )
    checks.check(
        gauss6_candidate_smoke.get("source_policy_rows_completed") == 0,
        "Gauss6 candidate smoke overclosed source-policy rows",
    )
    checks.check(
        gauss6_dae_candidate_contract.get("runner_api")
        == "source_gauss6_fullva_dae_candidate_contract_smoke",
        "Gauss6 DAE candidate contract API changed",
    )
    checks.check(
        gauss6_dae_candidate_contract.get("row_count") == 1,
        "Gauss6 DAE candidate contract nested row count changed",
    )
    checks.check(
        gauss6_dae_candidate_contract.get("source_policy_rows_completed") == 0,
        "Gauss6 DAE candidate contract nested overclosed source-policy rows",
    )
    checks.check(
        gauss6_dae_candidate_contract.get("source_policy_dae_runner_equivalent") is False,
        "Gauss6 DAE candidate contract nested overclaims DAE equivalence",
    )
    checks.check(
        gauss6_dae_candidate_contract.get("fullva_dae_source_policy_equivalent") is False,
        "Gauss6 DAE candidate contract nested overclaims FullVA DAE equivalence",
    )
    checks.check(
        gauss6_dae_candidate_contract.get("accepted_use")
        == "gauss6_fullva_dae_candidate_contract_not_source_policy",
        "Gauss6 DAE candidate contract accepted-use boundary missing",
    )
    checks.check(audit.get("source_reference_h") == 1.0e-4, "source reference h changed")
    checks.check(
        audit.get("source_grid_compatibility_status")
        == grid_audit.get("status")
        == "source_horizon_step_grid_policy_open",
        "source grid compatibility status changed",
    )
    checks.check(
        audit.get("source_grid_integer_step_compatible_rows")
        == grid_audit.get("integer_step_compatible_rows")
        == 2,
        "source grid compatible count changed",
    )
    checks.check(
        audit.get("source_grid_integer_step_incompatible_rows")
        == grid_audit.get("integer_step_incompatible_rows")
        == 4,
        "source grid incompatible count changed",
    )
    checks.check(
        audit.get("source_grid_exact_T_compatible_rows_endpoint_convention_resolved")
        == grid_audit.get("endpoint_compatible_rows_source_endpoint_convention_resolved")
        == 2,
        "source grid exact-T endpoint-resolved count changed",
    )
    checks.check(
        audit.get("source_grid_endpoint_incompatible_rows_requiring_policy")
        == grid_audit.get("endpoint_incompatible_rows_require_source_endpoint_policy")
        == 4,
        "source grid endpoint-policy-required count changed",
    )
    checks.check(
        audit.get("source_grid_policy_resolved_for_exact_T_compatible_rows")
        == grid_audit.get("source_grid_policy_resolved_for_exact_T_compatible_rows")
        is True,
        "source grid exact-T compatible subset was not carried as resolved",
    )
    checks.check(
        audit.get("source_grid_endpoint_compatible_row_ids")
        == grid_audit.get("source_endpoint_compatible_row_ids")
        == ["frictional_pendulum:h=0.008", "frictional_pendulum:h=0.2"],
        "source grid endpoint-compatible row IDs changed",
    )
    checks.check(
        audit.get("source_grid_endpoint_incompatible_row_ids")
        == grid_audit.get("source_endpoint_incompatible_row_ids")
        == [
            "frictionless_pendulum:h=0.003",
            "frictionless_pendulum:h=0.006",
            "frictionless_pendulum:h=0.012",
            "frictional_pendulum:h=0.003",
        ],
        "source grid endpoint-incompatible row IDs changed",
    )
    checks.check(
        audit.get("source_grid_policy_resolved_for_full_T10")
        == grid_audit.get("source_grid_policy_resolved_for_full_T10")
        is False,
        "source grid policy overclosed",
    )
    checks.check(
        algorithm_literal_endpoint_probe.get("schema") == "tfe-algorithm-literal-endpoint-probe-v1",
        "algorithm-literal endpoint probe schema changed",
    )
    checks.check(
        algorithm_literal_endpoint_probe.get("status")
        == "algorithm_literal_full_T10_probe_available_source_policy_open",
        "algorithm-literal endpoint probe status changed",
    )
    checks.check(
        algorithm_literal_endpoint_probe.get("method_count") == 4,
        "algorithm-literal endpoint probe method count changed",
    )
    checks.check(
        algorithm_literal_endpoint_probe.get("metric_row_count") == 12,
        "algorithm-literal endpoint probe metric row count changed",
    )
    checks.check(
        algorithm_literal_endpoint_probe.get("terminal_overrun_rows") == 12,
        "algorithm-literal endpoint probe terminal overrun count changed",
    )
    checks.check(
        algorithm_literal_endpoint_probe.get("source_policy_rows_completed") == 0,
        "algorithm-literal endpoint probe overclosed source-policy rows",
    )
    checks.check(
        algorithm_literal_endpoint_probe.get("source_policy_exact_T_error_sampling_equivalent") is False,
        "algorithm-literal endpoint probe overclaims exact-T error sampling equivalence",
    )
    checks.check(
        audit.get("algorithm_literal_endpoint_probe") == "TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE.md",
        "algorithm-literal endpoint probe markdown pointer changed",
    )
    checks.check(
        audit.get("algorithm_literal_endpoint_probe_json") == "TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE.json",
        "algorithm-literal endpoint probe JSON pointer changed",
    )
    checks.check(
        audit.get("algorithm_literal_endpoint_probe_status")
        == algorithm_literal_endpoint_probe.get("status"),
        "algorithm-literal endpoint probe status not carried into row audit",
    )
    checks.check(
        audit.get("algorithm_literal_endpoint_probe_method_count")
        == algorithm_literal_endpoint_probe.get("method_count")
        == 4,
        "algorithm-literal endpoint probe method count not carried into row audit",
    )
    checks.check(
        audit.get("algorithm_literal_endpoint_probe_metric_row_count")
        == algorithm_literal_endpoint_probe.get("metric_row_count")
        == 12,
        "algorithm-literal endpoint probe metric row count not carried into row audit",
    )
    checks.check(
        audit.get("algorithm_literal_endpoint_probe_terminal_overrun_rows")
        == algorithm_literal_endpoint_probe.get("terminal_overrun_rows")
        == 12,
        "algorithm-literal endpoint probe terminal overrun count not carried into row audit",
    )
    checks.check(
        audit.get("algorithm_literal_endpoint_probe_source_policy_rows_completed")
        == algorithm_literal_endpoint_probe.get("source_policy_rows_completed")
        == 0,
        "algorithm-literal endpoint probe source-policy row boundary not carried into row audit",
    )
    checks.check(
        audit.get("algorithm_literal_endpoint_probe_exact_T_error_sampling_equivalent")
        == algorithm_literal_endpoint_probe.get("source_policy_exact_T_error_sampling_equivalent")
        is False,
        "algorithm-literal endpoint probe exact-T boundary not carried into row audit",
    )
    checks.check(
        source_files.get("tfe_algorithm_literal_endpoint_probe")
        == "TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE.json",
        "algorithm-literal endpoint probe source file not recorded",
    )
    checks.check(
        source_files.get("source_policy_runner_equivalence_preflight")
        == "TFE_SOURCE_PENDULUM_MODEL_AUDIT.json#source_policy_runner_equivalence_preflight",
        "runner-equivalence preflight source pointer missing",
    )
    checks.check(audit.get("source_newton_tolerance") == 1.0e-7, "source Newton tolerance changed")
    checks.check(audit.get("source_model") == "rigid_pendulum_revolute_pair", "source model changed")
    checks.check(set(audit.get("source_cases", [])) == {"frictionless_pendulum", "frictional_pendulum"}, "source case set changed")
    checks.check(
        set(audit.get("source_methods_available", []))
        == {"TFE_m1", "TFE_m2", "TFE_m3", "trapezoidal", "Newmark_beta"},
        "source method set changed",
    )
    risk_counts = audit.get("source_policy_risk_counts", {})
    for stale_risk in [
        "source_pendulum_setup_not_encoded",
        "source_error_norm_and_output_policy_not_encoded",
        "friction_law_policy_open_for_source_reproduction",
    ]:
        checks.check(stale_risk not in risk_counts, f"stale top-level TFE risk kept: {stale_risk}")
    for risk in [
        "source_policy_DAE_runner_equivalence_open",
        "brown_mcphee_source_code_equivalent_law_open",
        "full_T10_endpoint_policy_open",
        "accepted_source_policy_work_rows_not_bound",
    ]:
        checks.check(risk_counts.get(risk) == 4, f"TFE open risk count changed: {risk}")
    checks.check(
        audit.get("source_pendulum_parameter_model_implemented")
        == model_audit.get("source_pendulum_parameter_model_implemented")
        is True,
        "source parameter model audit not carried into row audit",
    )
    checks.check(
        audit.get("frictionless_planar_rhs_smoke_implemented")
        == model_audit.get("frictionless_planar_rhs_smoke_implemented")
        is True,
        "frictionless smoke audit not carried into row audit",
    )
    checks.check(
        audit.get("absolute_coordinate_dae_residual_smoke_implemented")
        == model_audit.get("absolute_coordinate_dae_residual_smoke_implemented")
        is True,
        "absolute-coordinate DAE residual smoke audit not carried into row audit",
    )
    checks.check(
        audit.get("absolute_coordinate_frictional_candidate_dae_smoke_implemented")
        == model_audit.get("absolute_coordinate_frictional_candidate_dae_smoke_implemented")
        is True,
        "absolute-coordinate frictional DAE smoke audit not carried into row audit",
    )
    checks.check(
        audit.get("absolute_coordinate_planar_lift_trajectory_probe_implemented")
        == model_audit.get("absolute_coordinate_planar_lift_trajectory_probe_implemented")
        is True,
        "absolute-coordinate planar-lift probe not carried into row audit",
    )
    checks.check(
        audit.get("absolute_coordinate_planar_lift_trajectory_probe_rows")
        == model_audit.get("absolute_coordinate_planar_lift_trajectory_probe_rows")
        == 12,
        "absolute-coordinate planar-lift row count not carried into row audit",
    )
    checks.check(
        audit.get("absolute_coordinate_planar_lift_trajectory_probe_metric_rows")
        == model_audit.get("absolute_coordinate_planar_lift_trajectory_probe_metric_rows")
        == 36,
        "absolute-coordinate planar-lift metric row count not carried into row audit",
    )
    checks.check(
        audit.get("absolute_coordinate_planar_lift_trajectory_probe_source_policy_rows_completed")
        == model_audit.get("absolute_coordinate_planar_lift_trajectory_probe_source_policy_rows_completed")
        == 0,
        "absolute-coordinate planar-lift overcloses source-policy rows in row audit",
    )
    checks.check(
        audit.get("absolute_coordinate_planar_lift_trajectory_probe_dae_runner_equivalent")
        == model_audit.get("absolute_coordinate_planar_lift_trajectory_probe_dae_runner_equivalent")
        is False,
        "absolute-coordinate planar-lift overclaims DAE equivalence in row audit",
    )
    checks.check(
        audit.get("bounded_absolute_coordinate_dae_trajectory_runner_implemented")
        == model_audit.get("bounded_absolute_coordinate_dae_trajectory_runner_implemented")
        is True,
        "bounded DAE trajectory runner not carried into row audit",
    )
    checks.check(
        audit.get("bounded_absolute_coordinate_dae_trajectory_runner_rows")
        == model_audit.get("bounded_absolute_coordinate_dae_trajectory_runner_rows")
        == 4,
        "bounded DAE trajectory runner row count not carried into row audit",
    )
    checks.check(
        audit.get("bounded_absolute_coordinate_dae_trajectory_runner_metric_rows")
        == model_audit.get("bounded_absolute_coordinate_dae_trajectory_runner_metric_rows")
        == 12,
        "bounded DAE trajectory runner metric row count not carried into row audit",
    )
    checks.check(
        audit.get("bounded_absolute_coordinate_dae_trajectory_runner_step_residual_rows")
        == model_audit.get("bounded_absolute_coordinate_dae_trajectory_runner_step_residual_rows")
        == 56,
        "bounded DAE trajectory runner step row count not carried into row audit",
    )
    checks.check(
        audit.get("bounded_absolute_coordinate_dae_trajectory_runner_source_policy_rows_completed")
        == model_audit.get("bounded_absolute_coordinate_dae_trajectory_runner_source_policy_rows_completed")
        == 0,
        "bounded DAE trajectory runner overcloses source-policy rows in row audit",
    )
    checks.check(
        audit.get("bounded_absolute_coordinate_dae_trajectory_runner_dae_runner_equivalent")
        == model_audit.get("bounded_absolute_coordinate_dae_trajectory_runner_dae_runner_equivalent")
        is False,
        "bounded DAE trajectory runner overclaims DAE equivalence in row audit",
    )
    checks.check(
        audit.get("bounded_absolute_coordinate_dae_trajectory_runner_monolithic_integrator")
        == model_audit.get("bounded_absolute_coordinate_dae_trajectory_runner_monolithic_integrator")
        is False,
        "bounded DAE trajectory runner overclaims monolithic integration in row audit",
    )
    checks.check(
        audit.get("monolithic_absolute_coordinate_dae_candidate_runner_implemented")
        == model_audit.get("monolithic_absolute_coordinate_dae_candidate_runner_implemented")
        is True,
        "monolithic DAE candidate runner not carried into row audit",
    )
    checks.check(
        audit.get("monolithic_absolute_coordinate_dae_candidate_runner_rows")
        == model_audit.get("monolithic_absolute_coordinate_dae_candidate_runner_rows")
        == 4,
        "monolithic DAE candidate runner row count not carried into row audit",
    )
    checks.check(
        audit.get("monolithic_absolute_coordinate_dae_candidate_runner_metric_rows")
        == model_audit.get("monolithic_absolute_coordinate_dae_candidate_runner_metric_rows")
        == 12,
        "monolithic DAE candidate runner metric row count not carried into row audit",
    )
    checks.check(
        audit.get("monolithic_absolute_coordinate_dae_candidate_runner_step_residual_rows")
        == model_audit.get("monolithic_absolute_coordinate_dae_candidate_runner_step_residual_rows")
        == 56,
        "monolithic DAE candidate runner step row count not carried into row audit",
    )
    checks.check(
        audit.get("monolithic_absolute_coordinate_dae_candidate_runner_source_policy_rows_completed")
        == model_audit.get(
            "monolithic_absolute_coordinate_dae_candidate_runner_source_policy_rows_completed"
        )
        == 0,
        "monolithic DAE candidate runner overcloses source-policy rows in row audit",
    )
    checks.check(
        audit.get("monolithic_absolute_coordinate_dae_candidate_runner_dae_runner_equivalent")
        == model_audit.get("monolithic_absolute_coordinate_dae_candidate_runner_dae_runner_equivalent")
        is False,
        "monolithic DAE candidate runner overclaims DAE equivalence in row audit",
    )
    checks.check(
        audit.get("monolithic_absolute_coordinate_dae_candidate_runner_monolithic_integrator")
        == model_audit.get("monolithic_absolute_coordinate_dae_candidate_runner_monolithic_integrator")
        is False,
        "monolithic DAE candidate runner overclaims monolithic integration in row audit",
    )
    checks.check(
        audit.get("source_policy_dae_runner_equivalent")
        == model_audit.get("source_policy_dae_runner_equivalent")
        is False,
        "source-policy DAE runner equivalence boundary changed",
    )
    checks.check(
        audit.get("source_output_time_integration_smoke_implemented")
        == model_audit.get("source_output_time_integration_smoke_implemented")
        is True,
        "source-output time-integration smoke audit not carried into row audit",
    )
    checks.check(
        audit.get("source_policy_time_integration_runner_equivalent")
        == model_audit.get("source_policy_time_integration_runner_equivalent")
        is False,
        "source-policy time-integration boundary changed",
    )
    checks.check(
        audit.get("source_reference_solution_policy_smoke_implemented")
        == model_audit.get("source_reference_solution_policy_smoke_implemented")
        is True,
        "source reference policy smoke not carried into row audit",
    )
    checks.check(
        audit.get("source_reference_solution_policy_smoke_full_T10")
        == model_audit.get("source_reference_solution_policy_smoke_full_T10")
        is False,
        "source reference policy smoke full-run boundary changed",
    )
    checks.check(
        audit.get("source_reference_solution_policy_full_T10_probe_completed")
        == model_audit.get("source_reference_solution_policy_full_T10_probe_completed")
        is True,
        "source reference full T=10 probe not carried into row audit",
    )
    checks.check(
        audit.get("source_reference_solution_policy_full_T10_probe_rows_completed")
        == model_audit.get("source_reference_solution_policy_full_T10_probe_rows_completed")
        == 0,
        "source reference full T=10 probe overclosed rows in row audit",
    )
    checks.check(
        audit.get("source_comparator_candidate_runners_implemented")
        == model_audit.get("source_comparator_candidate_runners_implemented")
        is True,
        "source comparator runner smoke not carried into row audit",
    )
    checks.check(
        audit.get("source_policy_method_runner_equivalent")
        == model_audit.get("source_policy_method_runner_equivalent")
        is False,
        "source-policy method runner boundary changed",
    )
    checks.check(
        audit.get("tfe_m1_m2_m3_candidate_runner_smoke_implemented")
        == model_audit.get("tfe_m1_m2_m3_candidate_runner_smoke_implemented")
        is True,
        "TFE m candidate runner smoke not carried into row audit",
    )
    checks.check(
        audit.get("tfe_appendix_b_coefficient_certificate_checked")
        == model_audit.get("tfe_appendix_b_coefficient_certificate_checked")
        is True,
        "TFE Appendix-B coefficient certificate not carried into row audit",
    )
    checks.check(
        audit.get("tfe_m1_m2_m3_source_policy_runners_implemented")
        == model_audit.get("tfe_m1_m2_m3_source_policy_runners_implemented")
        is False,
        "TFE m source-policy runner boundary changed",
    )
    checks.check(
        audit.get("gauss6_fullva_source_pendulum_candidate_smoke_implemented")
        == (model_audit.get("gauss6_fullva_source_pendulum_candidate_smoke_implemented") is True),
        "Gauss6 candidate smoke implementation marker not carried into row audit",
    )
    checks.check(
        audit.get("gauss6_fullva_absolute_coordinate_source_policy_runner_implemented")
        == model_audit.get("gauss6_fullva_absolute_coordinate_source_policy_runner_implemented")
        is False,
        "Gauss6 source-policy runner split field not carried into row audit",
    )
    checks.check(
        audit.get("gauss6_fullva_source_pendulum_candidate_source_policy_rows_completed")
        == model_audit.get("gauss6_fullva_source_pendulum_candidate_source_policy_rows_completed")
        == 0,
        "Gauss6 candidate smoke completed rows boundary changed",
    )
    checks.check(
        audit.get("gauss6_fullva_source_pendulum_candidate_method_equivalent")
        == model_audit.get("gauss6_fullva_source_pendulum_candidate_method_equivalent")
        is False,
        "Gauss6 candidate smoke method-equivalence boundary changed",
    )
    checks.check(
        audit.get("gauss6_fullva_dae_candidate_contract_implemented")
        == model_audit.get("gauss6_fullva_dae_candidate_contract_implemented")
        is True,
        "Gauss6 DAE candidate contract implementation marker not carried into row audit",
    )
    checks.check(
        audit.get("gauss6_fullva_dae_candidate_contract_rows")
        == model_audit.get("gauss6_fullva_dae_candidate_contract_rows")
        == 1,
        "Gauss6 DAE candidate contract rows not carried into row audit",
    )
    checks.check(
        audit.get("gauss6_fullva_dae_candidate_contract_source_policy_rows_completed")
        == model_audit.get("gauss6_fullva_dae_candidate_contract_source_policy_rows_completed")
        == 0,
        "Gauss6 DAE candidate contract completed rows boundary changed",
    )
    checks.check(
        audit.get("gauss6_fullva_dae_candidate_contract_dae_equivalent")
        == model_audit.get("gauss6_fullva_dae_candidate_contract_dae_equivalent")
        is False,
        "Gauss6 DAE candidate contract DAE-equivalence boundary changed",
    )
    checks.check(
        audit.get("gauss6_fullva_dae_candidate_contract_fullva_dae_equivalent")
        == model_audit.get("gauss6_fullva_dae_candidate_contract_fullva_dae_equivalent")
        is False,
        "Gauss6 DAE candidate contract FullVA-equivalence boundary changed",
    )
    checks.check(
        audit.get("gauss6_fullva_dae_candidate_contract_all_step_states_finite")
        == model_audit.get("gauss6_fullva_dae_candidate_contract_all_step_states_finite")
        is True,
        "Gauss6 DAE candidate contract finite marker not carried into row audit",
    )
    checks.check(
        audit.get("gauss6_fullva_dae_candidate_contract_all_candidate_residuals_below_1e_8")
        == model_audit.get("gauss6_fullva_dae_candidate_contract_all_candidate_residuals_below_1e_8")
        is True,
        "Gauss6 DAE candidate contract residual marker not carried into row audit",
    )
    checks.check(
        audit.get("bounded_source_policy_runner_api_implemented")
        == model_audit.get("bounded_source_policy_runner_api_implemented")
        is True,
        "bounded source-policy runner API not carried into row audit",
    )
    checks.check(
        audit.get("bounded_source_policy_runner_smoke_implemented")
        == model_audit.get("bounded_source_policy_runner_smoke_implemented")
        is True,
        "bounded source-policy runner smoke not carried into row audit",
    )
    checks.check(
        audit.get("bounded_source_policy_runner_source_policy_rows_completed")
        == model_audit.get("bounded_source_policy_runner_source_policy_rows_completed")
        == 0,
        "bounded source-policy runner completed rows boundary changed",
    )
    checks.check(
        audit.get("active_tfe_b2_candidate_row_smoke_implemented")
        == model_audit.get("active_tfe_b2_candidate_row_smoke_implemented")
        is True,
        "active B2 smoke audit not carried into row audit",
    )
    checks.check(
        audit.get("active_tfe_b2_candidate_row_smoke_full_T10")
        == model_audit.get("active_tfe_b2_candidate_row_smoke_full_T10")
        is False,
        "active B2 full-run boundary changed",
    )
    checks.check(
        audit.get("active_tfe_b2_source_policy_rows_completed")
        == model_audit.get("active_tfe_b2_source_policy_rows_completed")
        == 0,
        "active B2 completed rows boundary changed",
    )
    checks.check(
        audit.get("active_tfe_b2_full_T10_coarse_candidate_probe_implemented")
        == model_audit.get("active_tfe_b2_full_T10_coarse_candidate_probe_implemented")
        is True,
        "active B2 full T=10 coarse probe not carried into row audit",
    )
    checks.check(
        audit.get("active_tfe_b2_full_T10_coarse_candidate_probe_source_policy_rows_completed")
        == model_audit.get("active_tfe_b2_full_T10_coarse_candidate_probe_source_policy_rows_completed")
        == 0,
        "active B2 full T=10 coarse probe completed rows boundary changed",
    )
    checks.check(
        audit.get("active_tfe_b2_source_reference_full_T10_candidate_probe_implemented")
        == model_audit.get("active_tfe_b2_source_reference_full_T10_candidate_probe_implemented")
        is True,
        "active B2 source-reference full T=10 probe not carried into row audit",
    )
    checks.check(
        audit.get(
            "active_tfe_b2_source_reference_full_T10_candidate_probe_source_policy_rows_completed"
        )
        == model_audit.get(
            "active_tfe_b2_source_reference_full_T10_candidate_probe_source_policy_rows_completed"
        )
        == 0,
        "active B2 source-reference full T=10 probe completed rows boundary changed",
    )
    checks.check(
        audit.get("source_error_norm_and_output_policy_encoded")
        == model_audit.get("source_error_norm_and_output_policy_encoded")
        is True,
        "source output policy audit not carried into row audit",
    )
    checks.check(
        audit.get("brown_mcphee_candidate_friction_law_encoded")
        == model_audit.get("brown_mcphee_candidate_friction_law_encoded")
        is True,
        "candidate friction audit not carried into row audit",
    )
    checks.check(
        audit.get("brown_mcphee_published_formula_structure_encoded")
        == model_audit.get("brown_mcphee_published_formula_structure_encoded")
        is True,
        "candidate friction formula structure not carried into row audit",
    )
    checks.check(
        audit.get("brown_mcphee_source_code_equivalent_law")
        == model_audit.get("brown_mcphee_source_code_equivalent_law")
        is False,
        "source-equivalent friction boundary not carried into row audit",
    )
    checks.check(
        audit.get("frictional_planar_candidate_rhs_smoke_implemented")
        == model_audit.get("frictional_planar_candidate_rhs_smoke_implemented")
        is True,
        "frictional smoke audit not carried into row audit",
    )
    for key in [
        "source_pendulum_body_setup_extracted",
        "source_pendulum_parameter_model_implemented",
        "frictionless_planar_rhs_smoke_implemented",
        "absolute_coordinate_dae_residual_smoke_implemented",
        "absolute_coordinate_planar_lift_trajectory_probe_implemented",
        "bounded_absolute_coordinate_dae_trajectory_runner_implemented",
        "monolithic_absolute_coordinate_dae_candidate_runner_implemented",
        "source_output_time_integration_smoke_implemented",
        "source_reference_solution_policy_smoke_implemented",
        "source_reference_solution_policy_full_T10_probe_completed",
        "newmark_trapezoidal_candidate_runner_smoke_implemented",
        "tfe_m1_m2_m3_candidate_runner_smoke_implemented",
        "source_method_candidate_runner_contract_implemented",
        "gauss6_fullva_source_pendulum_candidate_smoke_implemented",
        "gauss6_fullva_dae_candidate_contract_implemented",
        "bounded_source_policy_runner_api_implemented",
        "bounded_source_policy_runner_smoke_implemented",
        "algorithm_literal_endpoint_probe_available",
        "active_tfe_b2_candidate_row_smoke_implemented",
        "active_tfe_b2_source_reference_full_T10_candidate_probe_implemented",
        "source_error_norm_and_output_policy_encoded",
        "source_reference_h_extracted",
        "source_horizon_step_grid_policy_resolved_for_exact_T_compatible_rows",
    ]:
        checks.check(criteria.get(key) is True, f"criterion {key} changed")
    checks.check(
        criteria.get("source_horizon_step_grid_policy_resolved") is False,
        "criterion source_horizon_step_grid_policy_resolved unexpectedly closed",
    )
    for key in [
        "brown_mcphee_friction_law_or_source_code_equivalent_implemented",
        "pendulum_dae_runner_implemented",
        "tfe_newmark_trapezoidal_runners_implemented",
        "gauss6_fullva_on_source_pendulum_implemented",
        "rerun_or_independent_verification_artifact_present",
    ]:
        checks.check(criteria.get(key) is False, f"criterion {key} unexpectedly closed")
    checks.check(criteria.get("source_policy_rows_completed") is False, "criterion source_policy_rows_completed unexpectedly closed")
    checks.check(criteria.get("explicit_demotion_recorded_for_tfe") is True, "criterion explicit_demotion_recorded_for_tfe missing")
    checks.check(decision.get("can_close_tfe_b2_requirement_now") is False, "TFE B2 requirement overclosed")

    expected_rows = {
        (9, "single_pendulum", "tfe2026_Newmark_beta", "Newmark_beta", 2),
        (10, "single_pendulum", "tfe2026_TFE_m1", "TFE_m1", 1),
        (11, "single_pendulum", "tfe2026_TFE_m2", "TFE_m2", 3),
        (12, "single_pendulum", "tfe2026_trapezoidal", "trapezoidal", 2),
    }
    observed_rows = {
        (
            row.get("row_index"),
            row.get("example"),
            row.get("method"),
            row.get("source_method"),
            row.get("expected_order"),
        )
        for row in rows
    }
    checks.check(observed_rows == set(), "audited TFE rows changed")
    ledger_methods = {
        row.get("method")
        for row in row_ledger.get("rows", [])
        if row.get("suite") == "tfe2026_original_pendulum"
    }
    checks.check(
        {row.get("method") for row in rows}.issubset(ledger_methods),
        "row audit no longer matches row ledger methods",
    )
    for row in rows:
        checks.check(row.get("diagnostic_current_allowed_use") == "diagnostic_common_reference_only", f"row {row.get('row_index')} allowed use changed")
        checks.check(row.get("source_policy_reproduction") is False, f"row {row.get('row_index')} source-policy closed")
        checks.check(row.get("source_policy_closed") is False, f"row {row.get('row_index')} source-policy closed")
        checks.check(row.get("external_superiority_ready") is False, f"row {row.get('row_index')} claim-ready")
        checks.check(row.get("active_b2_candidate_smoke_present") is True, f"row {row.get('row_index')} missing active smoke")
        checks.check(row.get("bounded_runner_candidate_present") is True, f"row {row.get('row_index')} missing bounded runner smoke")
        checks.check(
            row.get("active_b2_candidate_allowed_use") == "bounded_candidate_smoke_only_not_source_policy",
            f"row {row.get('row_index')} active smoke allowed-use changed",
        )
        checks.check(
            row.get("bounded_runner_allowed_use") == "bounded_candidate_runner_api_only_not_source_policy",
            f"row {row.get('row_index')} bounded runner allowed-use changed",
        )
        checks.check(
            isinstance(row.get("active_b2_candidate_velocity_orders"), list)
            and len(row.get("active_b2_candidate_velocity_orders")) == 2,
            f"row {row.get('row_index')} active velocity orders missing",
        )
        checks.check(
            isinstance(row.get("bounded_runner_velocity_orders"), list)
            and len(row.get("bounded_runner_velocity_orders")) == 2,
            f"row {row.get('row_index')} bounded runner velocity orders missing",
        )
        checks.check(
            isinstance(row.get("active_b2_candidate_coordinate_orders"), list)
            and len(row.get("active_b2_candidate_coordinate_orders")) == 2,
            f"row {row.get('row_index')} active coordinate orders missing",
        )
        checks.check(
            isinstance(row.get("bounded_runner_coordinate_orders"), list)
            and len(row.get("bounded_runner_coordinate_orders")) == 2,
            f"row {row.get('row_index')} bounded runner coordinate orders missing",
        )
        for key in [
            "active_b2_candidate_finest_velocity_error",
            "active_b2_candidate_finest_coordinate_error",
            "active_b2_candidate_max_residual_norm",
        ]:
            checks.check(
                row.get(key) is not None and math.isfinite(float(row.get(key))),
                f"row {row.get('row_index')} {key} missing or nonfinite",
            )
        checks.check(
            float(row.get("active_b2_candidate_max_residual_norm")) < 1.0e-8,
            f"row {row.get('row_index')} active residual too large",
        )
        row_risks = row.get("source_policy_risks", [])
        for stale_risk in [
            "source_pendulum_setup_not_encoded",
            "source_error_norm_and_output_policy_not_encoded",
            "friction_law_policy_open_for_source_reproduction",
        ]:
            checks.check(stale_risk not in row_risks, f"row {row.get('row_index')} keeps stale risk: {stale_risk}")
        for risk in [
            "source_policy_DAE_runner_equivalence_open",
            "brown_mcphee_source_code_equivalent_law_open",
            "full_T10_endpoint_policy_open",
            "accepted_source_policy_work_rows_not_bound",
        ]:
            checks.check(risk in row_risks, f"row {row.get('row_index')} missing open risk: {risk}")

    boundary = audit.get("cross_artifact_boundary", {})
    checks.check(
        set(boundary.get("closure_manifest_not_ready_or_demote_suites", []))
        == set(closure_manifest.get("not_ready_or_demote_suites", []))
        == {"tfe2026_original_pendulum", "vp2024_velocity_partitioning"},
        "closure manifest not-ready suites changed",
    )
    checks.check(
        set(boundary.get("external_case_not_ready_or_demote_suites", []))
        == set(external_case.get("not_ready_or_demote_suites", []))
        == {"tfe2026_original_pendulum", "vp2024_velocity_partitioning"},
        "external case not-ready suites changed",
    )
    checks.check(execution.get("read_only_existing_artifacts") is True, "audit lost read-only marker")
    checks.check(execution.get("default_1e_4_required") is False, "audit requires default 1e-4")
    checks.check(execution.get("heavy_numerical_run_invoked") is False, "audit invoked heavy run")
    checks.check(execution.get("run_v047_invoked") is False, "audit invoked run_v047")
    checks.check(execution.get("v048_runner_invoked") is False, "audit invoked v048 runner")

    for token in [
        "Status: **source policy spec extracted; runner rows not closed**.",
        "Active B2 flagged TFE rows: `0`.",
        "Source-policy spec extracted: `True`.",
        "Source pendulum parameter model implemented: `True`.",
        "Frictionless planar RHS smoke implemented: `True`.",
        "Absolute-coordinate DAE residual smoke implemented: `True`.",
        "Absolute-coordinate frictional candidate DAE smoke implemented: `True`.",
        "Source-output time-integration smoke implemented: `True`.",
        "Source-policy time-integration runner equivalent: `False`.",
        "Source reference solution policy smoke implemented: `True`.",
        "Source reference solution policy full T=10 run: `False`.",
        "T=10 source grid policy resolved/compatible/incompatible rows: `False/2/4`.",
        "Exact-T compatible endpoint-grid rows resolved/requiring policy: `2/4`.",
        "Exact-T compatible subset grid policy resolved: `True`.",
        "Source comparator candidate runners implemented: `True`.",
        "Newmark-beta candidate runner smoke implemented: `True`.",
        "Trapezoidal candidate runner smoke implemented: `True`.",
        "Source-policy method runner equivalent: `False`.",
        "TFE m=1/2/3 candidate runner smoke implemented: `True`.",
        "Source-method candidate runner contract rows/source-policy rows/equivalent method: `5/0/False`.",
        "Source-method candidate runner contract finite/residual-below-1e-8: `True/True`.",
        "TFE Appendix-B coefficient certificate checked: `True`.",
        "TFE Appendix-B coefficient certificate rows/max diff: `3/0.000e+00`.",
        "TFE m=1/2/3 source-policy runners implemented: `False`.",
        "Bounded source-policy runner API implemented: `True`.",
        "Bounded source-policy runner smoke implemented: `True`.",
        "Bounded source-policy runner unified dispatch: `True`.",
        "Bounded source-policy runner rows/full T=10/source-policy rows: `4/False/0`.",
        "Bounded source-policy runner method equivalent: `False`.",
        "Bounded source-policy runner accepted use: `bounded_candidate_runner_api_only_not_source_policy`.",
        "Bounded source-policy runner DAE-equivalent/monolithic: `False/False`.",
        "Active TFE B2 candidate row smoke implemented: `True`.",
        "Active TFE B2 candidate row smoke full T=10: `False`.",
        "Active TFE B2 source-policy rows completed: `0`.",
        "Active TFE B2 full T=10 coarse candidate probe implemented: `True`.",
        "Active TFE B2 full T=10 coarse candidate probe full T=10/source-policy rows: `True/0`.",
        "Active TFE B2 full T=10 coarse candidate probe finite/residual-ok rows: `4/4`.",
        "Active TFE B2 full T=10 coarse candidate probe source reference invoked: `False`.",
        "Active TFE B2 source-reference full T=10 candidate probe implemented: `True`.",
        "Active TFE B2 source-reference full T=10 candidate probe full T=10/reference invoked/source-policy rows: `True/True/0`.",
        "Active TFE B2 source-reference full T=10 candidate probe finite/residual-ok rows: `4/4`.",
        "TFE m=3 full T=10 coarse formula probe implemented: `True`.",
        "TFE m=3 full T=10 coarse formula probe full T=10/source-policy rows: `True/0`.",
        "TFE m=3 full T=10 coarse formula probe finite/residual-ok rows: `1/1`.",
        "TFE m=3 full T=10 coarse formula probe expected order: `5`.",
        "TFE m=3 full T=10 coarse formula probe source reference invoked: `False`.",
        "Algorithm-literal endpoint probe status: `algorithm_literal_full_T10_probe_available_source_policy_open`.",
        "Algorithm-literal endpoint probe methods/metric rows/terminal overruns: `4/12/12`.",
        "Algorithm-literal endpoint probe source-policy rows/exact-T sampling equivalent: `0/False`.",
        "Source reference solution policy full T=10 probe completed/source rows: `True/0`.",
        "Source reference solution policy full T=10 probe steps/check error: `100000/200000`",
        "Source-policy DAE runner equivalent: `False`.",
        "Absolute-coordinate planar-lift trajectory probe implemented: `True`.",
        "Absolute-coordinate planar-lift rows/metric rows/source-policy rows: `12/36/0`.",
        "Absolute-coordinate planar-lift equivalent DAE runner: `False`.",
        "Bounded absolute-coordinate DAE trajectory runner implemented: `True`.",
        "Bounded absolute-coordinate DAE trajectory runner rows/metric rows/step residual rows: `4/12/56`.",
        "Bounded absolute-coordinate DAE trajectory runner source-policy rows/equivalent DAE/monolithic integrator: `0/False/False`.",
        "Source output/error policy encoded: `True`.",
        "Brown--McPhee candidate friction law encoded: `True`.",
        "Brown--McPhee source text anchors found/model/mu: `True/True/True`.",
        "Brown--McPhee published formula structure encoded: `True`.",
        "Brown--McPhee source-code-equivalent law: `False`.",
        "Brown--McPhee transition velocity resolved from source: `False`.",
        "Frictional candidate RHS smoke implemented: `True`.",
        "Pendulum DAE runner implemented: `False`.",
        "Brown--McPhee friction/source-code equivalent implemented: `False`.",
        "Gauss6/FullVA absolute-coordinate source-policy runner implemented: `False`.",
        "Gauss6/FullVA source pendulum candidate smoke implemented: `True`.",
        "Gauss6/FullVA source pendulum candidate rows/source-policy rows: `2/0`.",
        "Gauss6/FullVA source pendulum candidate method equivalent: `False`.",
        "Gauss6/FullVA DAE candidate contract rows/source-policy rows/equivalent DAE/FullVA: `1/0/False/False`.",
        "Gauss6/FullVA DAE candidate contract finite/residual-below-1e-8: `True/True`.",
        "Source-policy rows completed: `0`.",
        "Source-policy runner-equivalence preflight: `preflight_ready_runner_equivalence_open`.",
        "Source-policy runner-equivalence preflight closed/open/source rows: `25/6/0`.",
        "Source-policy runner-equivalence preflight can close lane: `False`.",
        "Runner-equivalence gap matrix open blockers: `6`.",
        "Runner-equivalence first required artifact: `source-equivalent DAE runner certificate for the original TFE pendulum policy`.",
        "Candidate/source-policy boundary scaffold/use/DAE-equivalent/method-equivalent/rows: `True/diagnostic_scaffold_only_not_source_policy_reproduction/False/False/0`.",
        "## Source-Policy Runner Equivalence Preflight",
        "Gauss6/FullVA absolute-coordinate source-policy runner implemented: `False`.",
        "Closed preconditions/open blockers: `25/6`.",
        "source_policy_absolute_coordinate_dae_runner_contract_present",
        "source_policy_tfe_newmark_trapezoidal_method_runner_contract_present",
        "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_contract_present",
        "Source-policy rows closed by preflight: `0`.",
        "Can close TFE lane from preflight: `False`.",
        "brown_mcphee_source_code_equivalent_law_open",
        "accepted_source_policy_work_precision_rows_not_executed_or_bound",
        "## Runner-Equivalence Gap Matrix",
        "Ready to execute source-policy rows now: `False`.",
        "Source-policy reproduction rows: `0/4`.",
        "Can close TFE B2 requirement now: `False`.",
        "The TFE rows remain diagnostic common-reference rows, not source-policy external-superiority evidence.",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("TFE source-policy row audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("TFE source-policy row audit validation: PASS")
    print("active_b2_flagged_rows=0")
    print("source_policy_spec_extracted=True")
    print("source_error_norm_and_output_policy_encoded=True")
    print("brown_mcphee_candidate_friction_law_encoded=True")
    print("brown_mcphee_published_formula_structure_encoded=True")
    print("brown_mcphee_source_code_equivalent_law=False")
    print("absolute_coordinate_dae_residual_smoke_implemented=True")
    print("absolute_coordinate_planar_lift_trajectory_probe_implemented=True")
    print("absolute_coordinate_planar_lift_trajectory_probe_rows=12")
    print("source_output_time_integration_smoke_implemented=True")
    print("source_reference_solution_policy_smoke_implemented=True")
    print("source_reference_solution_policy_full_T10_probe_completed=True")
    print("source_comparator_candidate_runners_implemented=True")
    print("tfe_m1_m2_m3_candidate_runner_smoke_implemented=True")
    print("gauss6_fullva_source_pendulum_candidate_smoke_implemented=True")
    print("gauss6_fullva_dae_candidate_contract_implemented=True")
    print("gauss6_fullva_absolute_coordinate_source_policy_runner_implemented=False")
    print("tfe_appendix_b_coefficient_certificate_checked=True")
    print("bounded_source_policy_runner_smoke_implemented=True")
    print("active_tfe_b2_candidate_row_smoke_implemented=True")
    print("active_tfe_b2_full_T10_coarse_candidate_probe_implemented=True")
    print("active_tfe_b2_source_reference_full_T10_candidate_probe_implemented=True")
    print("tfe_m3_full_T10_coarse_formula_probe_implemented=True")
    print("pendulum_dae_runner_implemented=False")
    print("source_policy_reproduction_rows=0/4")
    print("can_close_tfe_b2_requirement_now=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
