#!/usr/bin/env python3
"""Validate the TFE DAE runner contract gap audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
MODEL_PATH = ROOT / "v048_cross_paper_same_test_benchmarks" / "tfe_source_pendulum_model.py"


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
        audit = read_json(PAPER / "TFE_DAE_RUNNER_CONTRACT_GAP_AUDIT.json")
        audit_md = read_text(PAPER / "TFE_DAE_RUNNER_CONTRACT_GAP_AUDIT.md")
        model_source = read_text(MODEL_PATH)
        model = read_json(PAPER / "TFE_SOURCE_PENDULUM_MODEL_AUDIT.json")
        row_audit = read_json(PAPER / "TFE_SOURCE_POLICY_ROW_AUDIT.json")
        grid = read_json(PAPER / "TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.json")
        brown_law = read_json(PAPER / "TFE_BROWN_MCPHEE_SOURCE_LAW_BOUNDARY_AUDIT.json")
        brown_certificate = read_json(PAPER / "TFE_BROWN_MCPHEE_SOURCE_CODE_EQUIVALENCE_CERTIFICATE.json")
        endpoint_certificate = read_json(PAPER / "TFE_FULL_T10_ENDPOINT_POLICY_CLOSURE_CERTIFICATE.json")
        endpoint_probe = read_json(PAPER / "TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE.json")
        endpoint_work = read_json(PAPER / "TFE_ALGORITHM_LITERAL_WORK_PRECISION_AUDIT.json")
        endpoint_boundary = read_json(PAPER / "TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.json")
        full_t10_absolute = read_json(PAPER / "TFE_FULL_T10_ABSOLUTE_DAE_LIFT_SUMMARY.json")
        spec = read_json(PAPER / "TFE_SOURCE_POLICY_SPEC.json")
    except Exception as exc:  # noqa: BLE001
        print(f"TFE DAE runner contract gap audit validation: FAIL\n- {exc}")
        return 1

    available = audit.get("available_contract_blocks", {})
    source_spec_boundary = spec.get("candidate_vs_source_policy_boundary", {})
    audit_boundary = audit.get("candidate_vs_source_policy_boundary", {})
    missing = audit.get("missing_contract_blocks", [])
    scan = audit.get("code_text_scan", {})
    gap_matrix = row_audit.get("source_policy_runner_equivalence_gap_matrix", {})
    nonheavy = audit.get("nonheavy_blocker_evidence", {})
    brown_evidence = nonheavy.get("brown_mcphee", {})
    endpoint_evidence = nonheavy.get("endpoint_policy", {})
    dispositions = audit.get("nonheavy_missing_contract_block_dispositions", [])
    disposition_by_id = {item.get("id"): item for item in dispositions}
    execution_preflight = audit.get("source_policy_execution_preflight", {})
    safe_next_actions = audit.get("safe_next_actions", [])

    checks.check(audit.get("schema") == "tfe-dae-runner-contract-gap-audit-v1", "schema changed")
    checks.check(
        audit.get("status") == "dae_runner_contract_gap_open_not_source_policy",
        "status changed",
    )
    checks.check(audit.get("read_only") is True, "audit should be read-only")
    checks.check(audit.get("heavy_numerical_run_invoked") is False, "audit invoked heavy run")
    checks.check(audit.get("run_v047_invoked") is False, "audit invoked run_v047")
    checks.check(audit.get("v048_runner_invoked") is False, "audit invoked v048 runner")
    checks.check(audit.get("submission_ready") is False, "audit overclaims submission readiness")
    checks.check(audit.get("external_superiority_claim_allowed") is False, "audit overclaims external superiority")
    checks.check(audit.get("source_policy_rows_completed") == 0, "audit overclosed source-policy rows")
    checks.check(audit.get("source_policy_dae_runner_equivalent") is False, "audit overclaims DAE equivalence")
    checks.check(audit.get("source_policy_method_runner_equivalent") is False, "audit overclaims method equivalence")
    checks.check(audit.get("pendulum_dae_runner_implemented") is False, "audit overclaims pendulum DAE runner")
    checks.check(
        audit.get("monolithic_absolute_coordinate_dae_time_integrator") is False,
        "audit overclaims monolithic DAE integrator",
    )
    checks.check(audit.get("ready_to_execute_source_policy_now") is False, "audit marks source-policy ready too early")
    checks.check(
        "Keep the recorded negative Brown-McPhee source-code-equivalence certificate active and do not promote frictional rows until source code or Refs. 38-39 resolve the transition policy."
        in safe_next_actions,
        "Brown-McPhee safe action no longer reflects the recorded negative certificate",
    )
    checks.check(
        "Resolve the Brown-McPhee source-code-equivalent friction-law certificate without promoting rows."
        not in safe_next_actions,
        "stale Brown-McPhee safe action still treats the negative certificate as unresolved",
    )

    checks.check(scan.get("absolute_state_lift_function_present") is True, "absolute state lift scan missing")
    checks.check(scan.get("absolute_residual_smoke_function_present") is True, "absolute residual scan missing")
    checks.check(scan.get("bounded_stepwise_dae_runner_function_present") is True, "bounded runner scan missing")
    checks.check(
        scan.get("monolithic_candidate_dae_runner_function_present") is True,
        "monolithic candidate runner scan missing",
    )
    checks.check(
        scan.get("source_policy_absolute_coordinate_dae_runner_contract_symbol_present")
        is True,
        "source-policy absolute-coordinate DAE runner contract symbol scan missing",
    )
    checks.check(
        scan.get("source_method_candidate_contract_function_present") is True,
        "source-method candidate contract scan missing",
    )
    checks.check(
        scan.get("source_policy_method_runner_contract_symbol_present") is True,
        "source-policy method-runner contract symbol scan missing",
    )
    checks.check(
        scan.get("gauss6_fullva_dae_candidate_contract_function_present") is True,
        "Gauss6 DAE candidate contract scan missing",
    )
    checks.check(
        scan.get("source_policy_gauss6_fullva_dae_runner_contract_symbol_present") is True,
        "source-policy Gauss6 DAE runner contract symbol scan missing",
    )
    checks.check(scan.get("planar_step_dispatch_function_present") is True, "planar dispatch scan missing")
    checks.check(
        scan.get("explicit_monolithic_source_policy_dae_solver_function_present") is False,
        "monolithic source-policy DAE solver unexpectedly present",
    )
    checks.check(
        "def source_policy_absolute_coordinate_dae_runner" in model_source
        and "def source_policy_tfe_newmark_trapezoidal_method_runners" in model_source
        and "def source_policy_gauss6_fullva_absolute_coordinate_dae_runner" in model_source
        and "def monolithic_absolute_coordinate_source_policy_dae_runner" not in model_source,
        "model source lost a contract symbol or gained a monolithic source-policy DAE solver",
    )

    checks.check(available.get("source_policy_spec_extracted") is True, "source policy spec not extracted")
    checks.check(
        audit_boundary == source_spec_boundary,
        "candidate/source-policy boundary drifted from TFE source-policy spec",
    )
    checks.check(
        available.get("source_spec_candidate_scaffold_present")
        == source_spec_boundary.get("candidate_scaffold_present")
        is True,
        "source spec candidate scaffold boundary missing from DAE gap audit",
    )
    checks.check(
        available.get("source_spec_candidate_allowed_use")
        == source_spec_boundary.get("candidate_scaffold_allowed_use")
        == "diagnostic_scaffold_only_not_source_policy_reproduction",
        "source spec candidate allowed-use boundary changed",
    )
    checks.check(
        available.get("source_spec_boundary_source_policy_dae_runner_equivalent") is False
        and available.get("source_spec_boundary_source_policy_method_runner_equivalent") is False
        and available.get("source_spec_boundary_source_policy_rows_completed") == 0,
        "source spec boundary overclaims DAE/method equivalence in gap audit",
    )
    checks.check(
        available.get("source_spec_gauss6_candidate_smoke_available") is True
        and available.get("source_spec_gauss6_candidate_smoke_allowed_use")
        == "candidate_smoke_only_not_source_policy_dae_runner"
        and available.get("source_spec_gauss6_candidate_smoke_source_policy_rows_completed")
        == 0,
        "source spec Gauss6 candidate smoke boundary missing in gap audit",
    )
    checks.check(
        available.get("source_spec_gauss6_source_policy_dae_runner_required") is True
        and available.get("source_spec_gauss6_source_policy_dae_runner_implemented") is False
        and available.get("source_spec_gauss6_source_policy_dae_runner_equivalent") is False
        and available.get("source_spec_gauss6_source_policy_dae_runner_rows_completed") == 0,
        "source spec Gauss6 source-policy DAE runner boundary overclaims readiness",
    )
    checks.check(
        available.get("source_pendulum_parameter_model_implemented")
        == model.get("source_pendulum_parameter_model_implemented")
        is True,
        "source pendulum parameter model marker changed",
    )
    checks.check(available.get("absolute_coordinate_state_lift_present") is True, "state lift marker missing")
    checks.check(
        available.get("absolute_coordinate_dae_residual_smoke_implemented")
        == model.get("absolute_coordinate_dae_residual_smoke_implemented")
        is True,
        "absolute residual smoke marker changed",
    )
    checks.check(
        available.get("absolute_coordinate_residual_smoke_equivalent") is False,
        "absolute residual smoke overclaims equivalence",
    )
    checks.check(available.get("absolute_coordinate_planar_lift_probe_rows") == 12, "planar-lift row count changed")
    checks.check(
        available.get("absolute_coordinate_planar_lift_probe_metric_rows") == 36,
        "planar-lift metric row count changed",
    )
    checks.check(
        available.get("absolute_coordinate_planar_lift_probe_source_policy_rows_completed") == 0,
        "planar-lift overclosed source-policy rows",
    )
    checks.check(available.get("bounded_stepwise_dae_runner_rows") == 4, "bounded runner row count changed")
    checks.check(available.get("bounded_stepwise_dae_runner_metric_rows") == 12, "bounded runner metric count changed")
    checks.check(
        available.get("bounded_stepwise_dae_runner_step_residual_rows") == 56,
        "bounded runner step residual count changed",
    )
    checks.check(available.get("bounded_stepwise_dae_runner_all_step_states_finite") is True, "bounded states not finite")
    checks.check(
        available.get("bounded_stepwise_dae_runner_source_policy_rows_completed") == 0,
        "bounded runner overclosed source-policy rows",
    )
    checks.check(available.get("bounded_stepwise_dae_runner_equivalent") is False, "bounded runner overclaims equivalence")
    checks.check(available.get("bounded_stepwise_dae_runner_monolithic") is False, "bounded runner overclaims monolithic")
    checks.check(
        available.get("monolithic_candidate_dae_runner_implemented") is True,
        "monolithic candidate DAE runner not carried into contract audit",
    )
    checks.check(
        available.get("monolithic_candidate_dae_runner_rows") == 4,
        "monolithic candidate DAE runner row count changed",
    )
    checks.check(
        available.get("monolithic_candidate_dae_runner_metric_rows") == 12,
        "monolithic candidate DAE runner metric count changed",
    )
    checks.check(
        available.get("monolithic_candidate_dae_runner_step_residual_rows") == 56,
        "monolithic candidate DAE runner step residual count changed",
    )
    checks.check(
        available.get("monolithic_candidate_dae_runner_all_rows_finite") is True,
        "monolithic candidate DAE runner rows not finite",
    )
    checks.check(
        available.get("monolithic_candidate_dae_runner_residuals_below_1e_10") is True,
        "monolithic candidate DAE runner residual gate failed",
    )
    checks.check(
        available.get("monolithic_candidate_dae_runner_source_policy_rows_completed") == 0,
        "monolithic candidate DAE runner overclosed source-policy rows",
    )
    checks.check(
        available.get("monolithic_candidate_dae_runner_equivalent") is False,
        "monolithic candidate DAE runner overclaims equivalence",
    )
    checks.check(
        available.get("monolithic_candidate_dae_runner_monolithic") is False,
        "monolithic candidate DAE runner overclaims source-policy monolithic integration",
    )
    checks.check(
        available.get("source_policy_absolute_coordinate_dae_runner_contract_symbol_present")
        is True,
        "source-policy absolute-coordinate DAE runner contract symbol not carried into gap audit",
    )
    checks.check(
        audit.get("source_policy_absolute_coordinate_dae_runner_contract_present")
        == available.get("source_policy_absolute_coordinate_dae_runner_contract_present")
        is True,
        "source-policy absolute-coordinate DAE runner contract marker missing from gap audit",
    )
    checks.check(
        audit.get("source_policy_absolute_coordinate_dae_runner_implemented")
        == available.get("source_policy_absolute_coordinate_dae_runner_implemented")
        is False,
        "source-policy absolute-coordinate DAE runner contract overclaims implementation",
    )
    checks.check(
        available.get("source_policy_absolute_coordinate_dae_runner_rows") == 4,
        "source-policy absolute-coordinate DAE runner contract row count changed",
    )
    checks.check(
        available.get("source_policy_absolute_coordinate_dae_runner_metric_rows") == 12,
        "source-policy absolute-coordinate DAE runner contract metric count changed",
    )
    checks.check(
        available.get("source_policy_absolute_coordinate_dae_runner_step_residual_rows")
        == 56,
        "source-policy absolute-coordinate DAE runner contract step residual count changed",
    )
    checks.check(
        available.get("source_policy_absolute_coordinate_dae_runner_all_rows_finite")
        is True,
        "source-policy absolute-coordinate DAE runner contract rows not finite",
    )
    checks.check(
        available.get("source_policy_absolute_coordinate_dae_runner_residuals_below_1e_10")
        is True,
        "source-policy absolute-coordinate DAE runner contract residual gate failed",
    )
    checks.check(
        available.get("source_policy_absolute_coordinate_dae_runner_source_policy_rows_completed")
        == 0,
        "source-policy absolute-coordinate DAE runner contract overclosed rows",
    )
    checks.check(
        available.get("source_policy_absolute_coordinate_dae_runner_equivalent") is False,
        "source-policy absolute-coordinate DAE runner contract overclaims DAE equivalence",
    )
    checks.check(
        available.get("source_policy_absolute_coordinate_dae_runner_monolithic") is False,
        "source-policy absolute-coordinate DAE runner contract overclaims monolithic integration",
    )
    checks.check(
        available.get("source_policy_absolute_coordinate_dae_runner_candidate_api")
        == "monolithic_absolute_coordinate_dae_candidate_runner_smoke",
        "source-policy absolute-coordinate DAE runner contract candidate binding changed",
    )
    checks.check(
        available.get("source_method_candidate_contract_implemented") is True,
        "source-method candidate contract not carried into contract audit",
    )
    checks.check(
        available.get("source_method_candidate_contract_rows") == 5,
        "source-method candidate contract row count changed",
    )
    checks.check(
        available.get("source_method_candidate_contract_finite") is True,
        "source-method candidate contract has nonfinite rows",
    )
    checks.check(
        available.get("source_method_candidate_contract_residuals_below_1e_8") is True,
        "source-method candidate contract residual gate failed",
    )
    checks.check(
        available.get("source_method_candidate_contract_source_policy_rows_completed") == 0,
        "source-method candidate contract overclosed source-policy rows",
    )
    checks.check(
        available.get("source_method_candidate_contract_equivalent") is False,
        "source-method candidate contract overclaims method equivalence",
    )
    checks.check(
        available.get("source_method_candidate_contract_dae_equivalent") is False,
        "source-method candidate contract overclaims DAE equivalence",
    )
    checks.check(
        available.get("source_policy_method_runner_contract_symbol_present") is True,
        "source-policy method-runner contract symbol not carried into gap audit",
    )
    checks.check(
        audit.get("source_policy_method_runner_contract_present")
        == available.get("source_policy_method_runner_contract_present")
        is True,
        "source-policy method-runner contract marker missing from gap audit",
    )
    checks.check(
        audit.get("source_policy_tfe_newmark_trapezoidal_method_runners_implemented")
        == available.get("source_policy_tfe_newmark_trapezoidal_method_runners_implemented")
        is False,
        "source-policy method-runner contract overclaims implementation",
    )
    checks.check(
        available.get("source_policy_method_runner_contract_rows") == 5,
        "source-policy method-runner contract row count changed",
    )
    checks.check(
        available.get("source_policy_method_runner_contract_source_policy_rows_completed")
        == 0,
        "source-policy method-runner contract overclosed source-policy rows",
    )
    checks.check(
        available.get("source_policy_method_runner_contract_equivalent") is False
        and available.get("source_policy_method_runner_contract_dae_equivalent") is False,
        "source-policy method-runner contract overclaims equivalence",
    )
    checks.check(
        available.get("source_policy_method_runner_contract_finite") is True
        and available.get("source_policy_method_runner_contract_residuals_below_1e_8")
        is True,
        "source-policy method-runner contract finite/residual flags changed",
    )
    checks.check(
        available.get("full_T10_source_reference_probe_completed") is True,
        "full T10 reference probe marker changed",
    )
    checks.check(
        available.get("full_T10_source_reference_probe_rows_completed") == 0,
        "full T10 reference probe overclosed rows",
    )
    checks.check(
        available.get("gauss6_fullva_source_pendulum_candidate_smoke_implemented") is True,
        "Gauss6 candidate smoke not carried into DAE contract audit",
    )
    checks.check(
        available.get("gauss6_fullva_absolute_coordinate_source_policy_runner_implemented") is False,
        "Gauss6 source-policy runner unexpectedly implemented",
    )
    checks.check(
        available.get("gauss6_fullva_candidate_source_policy_rows_completed") == 0,
        "Gauss6 candidate overclosed source-policy rows",
    )
    checks.check(
        available.get("gauss6_fullva_dae_candidate_contract_implemented") is True,
        "Gauss6 DAE candidate contract not carried into contract audit",
    )
    checks.check(
        available.get("gauss6_fullva_dae_candidate_contract_rows") == 1,
        "Gauss6 DAE candidate contract row count changed",
    )
    checks.check(
        available.get("gauss6_fullva_dae_candidate_contract_finite") is True,
        "Gauss6 DAE candidate contract finite marker changed",
    )
    checks.check(
        available.get("gauss6_fullva_dae_candidate_contract_residuals_below_1e_8") is True,
        "Gauss6 DAE candidate contract residual gate failed",
    )
    checks.check(
        available.get("gauss6_fullva_dae_candidate_contract_source_policy_rows_completed") == 0,
        "Gauss6 DAE candidate contract overclosed source-policy rows",
    )
    checks.check(
        available.get("gauss6_fullva_dae_candidate_contract_equivalent") is False,
        "Gauss6 DAE candidate contract overclaims DAE equivalence",
    )
    checks.check(
        available.get("gauss6_fullva_dae_candidate_contract_fullva_equivalent") is False,
        "Gauss6 DAE candidate contract overclaims FullVA equivalence",
    )
    checks.check(
        available.get("source_policy_gauss6_fullva_dae_runner_contract_symbol_present")
        is True,
        "source-policy Gauss6 DAE runner contract symbol not carried into gap audit",
    )
    checks.check(
        audit.get("source_policy_gauss6_fullva_absolute_coordinate_dae_runner_contract_present")
        == available.get(
            "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_contract_present"
        )
        is True,
        "source-policy Gauss6 DAE runner contract marker missing from gap audit",
    )
    checks.check(
        audit.get("source_policy_gauss6_fullva_absolute_coordinate_dae_runner_implemented")
        == available.get(
            "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_implemented"
        )
        is False,
        "source-policy Gauss6 DAE runner contract overclaims implementation",
    )
    checks.check(
        available.get("source_policy_gauss6_fullva_absolute_coordinate_dae_runner_rows")
        == 1,
        "source-policy Gauss6 DAE runner contract row count changed",
    )
    checks.check(
        available.get(
            "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_source_policy_rows_completed"
        )
        == 0,
        "source-policy Gauss6 DAE runner contract overclosed rows",
    )
    checks.check(
        available.get("source_policy_gauss6_fullva_absolute_coordinate_dae_runner_equivalent")
        is False
        and available.get(
            "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_fullva_equivalent"
        )
        is False
        and available.get(
            "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_monolithic"
        )
        is False,
        "source-policy Gauss6 DAE runner contract overclaims equivalence",
    )
    checks.check(
        available.get("source_policy_gauss6_fullva_absolute_coordinate_dae_runner_finite")
        is True
        and available.get(
            "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_residuals_below_1e_8"
        )
        is True,
        "source-policy Gauss6 DAE runner contract finite/residual flags changed",
    )
    checks.check(
        available.get("full_T10_absolute_dae_lift_completed")
        == full_t10_absolute.get("full_T10_absolute_coordinate_lift_completed")
        is True,
        "full T10 absolute DAE-lift completion not carried into contract audit",
    )
    checks.check(
        available.get("full_T10_absolute_dae_lift_metric_rows")
        == full_t10_absolute.get("metric_row_count")
        == 12,
        "full T10 absolute DAE-lift metric row count stale",
    )
    checks.check(
        available.get("full_T10_absolute_dae_lift_step_residual_rows")
        == full_t10_absolute.get("step_residual_row_count")
        == 2800,
        "full T10 absolute DAE-lift step residual count stale",
    )
    checks.check(
        available.get("full_T10_absolute_dae_lift_source_reference_invoked")
        == full_t10_absolute.get("source_reference_invoked")
        is True,
        "full T10 absolute DAE-lift source-reference marker stale",
    )
    checks.check(
        available.get("full_T10_absolute_dae_lift_source_policy_rows_completed")
        == full_t10_absolute.get("source_policy_rows_completed")
        == 0,
        "full T10 absolute DAE-lift overclosed source-policy rows",
    )
    checks.check(
        available.get("full_T10_absolute_dae_lift_monolithic")
        == full_t10_absolute.get("monolithic_absolute_coordinate_dae_time_integrator")
        is False,
        "full T10 absolute DAE-lift overclaims monolithic integration",
    )
    checks.check(
        available.get("full_T10_absolute_dae_lift_equivalent")
        == full_t10_absolute.get("source_policy_dae_runner_equivalent")
        is False,
        "full T10 absolute DAE-lift overclaims DAE equivalence",
    )
    checks.check(available.get("preflight_closed_preconditions") == 25, "preflight closed count changed")
    checks.check(available.get("preflight_open_blockers") == 6, "preflight blocker count changed")
    checks.check(available.get("preflight_source_policy_rows_closed") == 0, "preflight overclosed rows")

    expected_missing_ids = {
        "brown_mcphee_source_code_equivalent_law_open",
        "pendulum_absolute_coordinate_source_policy_dae_runner_missing",
        "tfe_newmark_trapezoidal_source_policy_method_runners_missing",
        "gauss6_fullva_absolute_coordinate_source_policy_runner_missing",
        "full_T10_source_grid_endpoint_policy_open",
        "accepted_source_policy_work_precision_rows_not_executed_or_bound",
    }
    expected_nonheavy_gap_ids = [
        "brown_mcphee_source_code_equivalent_law_open",
        "full_T10_source_grid_endpoint_policy_open",
    ]
    expected_execution_gap_ids = sorted(
        expected_missing_ids - set(expected_nonheavy_gap_ids)
    )
    observed_missing_ids = {row.get("id") for row in missing}
    checks.check(audit.get("missing_contract_block_count") == 6, "missing block count changed")
    checks.check(len(missing) == 6, "missing block payload count changed")
    checks.check(observed_missing_ids == expected_missing_ids, "missing block ids changed")
    checks.check(
        audit.get("nonheavy_missing_contract_blocks") == expected_nonheavy_gap_ids
        and audit.get("nonheavy_missing_contract_block_count") == 2,
        "non-heavy missing block list changed",
    )
    checks.check(
        set(audit.get("source_policy_execution_missing_contract_blocks", []))
        == set(expected_execution_gap_ids),
        "source-policy execution missing block list changed",
    )
    checks.check(
        audit.get("terminal_nonpromoted_contract_blocks") == expected_nonheavy_gap_ids
        and audit.get("terminal_nonpromoted_contract_block_count") == 2
        and sorted(audit.get("effective_missing_contract_blocks", []))
        == expected_execution_gap_ids
        and audit.get("effective_missing_contract_block_count") == 4,
        "effective contract-block accounting changed",
    )
    accounting = audit.get("contract_block_accounting", {})
    checks.check(
        accounting.get("raw_open_contract_block_count") == 6
        and set(accounting.get("raw_open_contract_blocks", [])) == expected_missing_ids
        and accounting.get("terminal_nonpromoted_contract_block_count") == 2
        and accounting.get("terminal_nonpromoted_contract_blocks") == expected_nonheavy_gap_ids
        and accounting.get("effective_source_policy_execution_contract_block_count") == 4
        and sorted(accounting.get("effective_source_policy_execution_contract_blocks", []))
        == expected_execution_gap_ids
        and accounting.get("source_policy_rows_closed_by_accounting") == 0
        and accounting.get("accounting_disposition")
        == "nonheavy_terminal_demotions_recorded_source_policy_execution_blocks_remain",
        "contract block accounting summary changed",
    )
    checks.check(
        audit.get("nonheavy_missing_contract_blocks_dispositioned_by_demotion") is True,
        "non-heavy demotion disposition no longer closes the non-heavy boundary",
    )
    checks.check(
        audit.get("nonheavy_demotion_does_not_close_source_policy") is True,
        "non-heavy demotion should not close source-policy rows",
    )
    checks.check(
        audit.get("source_policy_execution_missing_contract_block_count") == 4,
        "source-policy execution missing block count changed",
    )
    checks.check(
        audit.get("source_policy_execution_missing_scope", {}).get("open_blocks")
        == audit.get("source_policy_execution_missing_contract_blocks")
        and audit.get("source_policy_execution_missing_scope", {}).get("missing_block_count") == 4
        and audit.get("source_policy_execution_missing_scope", {}).get(
            "requires_new_runner_contract_or_explicit_source_policy_execution"
        )
        is False
        and audit.get("source_policy_execution_missing_scope", {}).get(
            "requires_new_public_or_source_code_equivalent_artifact_to_reopen"
        )
        is True
        and audit.get("source_policy_execution_missing_scope", {}).get("ready_to_execute_source_policy_now")
        is False,
        "source-policy execution missing scope changed",
    )
    checks.check(
        execution_preflight.get("schema") == "tfe-source-policy-execution-preflight-v1",
        "source-policy execution preflight schema changed",
    )
    checks.check(
        execution_preflight.get("status")
        == "terminal_no_public_code_self_reproduction_attempted_not_promoted",
        "source-policy execution preflight status changed",
    )
    checks.check(
        execution_preflight.get("current_route")
        == "no_public_code_self_reproduction_attempted_unable_to_reproduce_not_promoted",
        "source-policy execution preflight route changed",
    )
    checks.check(execution_preflight.get("read_only") is True, "execution preflight should be read-only")
    checks.check(
        execution_preflight.get("heavy_numerical_run_invoked") is False
        and execution_preflight.get("run_v047_invoked") is False
        and execution_preflight.get("v048_runner_invoked") is False,
        "execution preflight invoked a forbidden runner",
    )
    checks.check(
        execution_preflight.get("nonheavy_blocks_dispositioned_by_demotion") is True
        and execution_preflight.get("nonheavy_demotion_does_not_close_source_policy") is True,
        "execution preflight non-heavy demotion boundary changed",
    )
    checks.check(
        execution_preflight.get("execution_blocks") == audit.get("source_policy_execution_missing_contract_blocks")
        and execution_preflight.get("execution_block_count") == 4
        and execution_preflight.get("opt_in_required_for") == [],
        "execution preflight block list changed",
    )
    checks.check(
        execution_preflight.get("runner_contracts_required_before_execution")
        == [
            "monolithic_absolute_coordinate_DAE_time_integrator",
            "TFE_m1_m2_m3_Newmark_beta_trapezoidal_source_policy_method_runners",
            "Gauss6_FullVA_absolute_coordinate_source_policy_DAE_runner",
            "accepted_T10_source_policy_work_precision_rows",
        ],
        "execution preflight required runner contracts changed",
    )
    checks.check(
        execution_preflight.get("source_policy_rows_completed") == 0
        and execution_preflight.get("can_promote_any_tfe_source_policy_row_now") is False
        and execution_preflight.get("ready_to_execute_source_policy_now") is False
        and execution_preflight.get("explicit_user_opt_in_required") is False,
        "execution preflight overclaims promotion or readiness",
    )
    checks.check(
        execution_preflight.get("reopen_condition")
        == "new_public_or_source_code_equivalent_tfe_implementation_artifact",
        "execution preflight reopen condition changed",
    )
    checks.check(
        execution_preflight.get("reviewer_facing_decision")
        == "no_public_code_self_reproduction_attempted_unable_to_reproduce_not_promoted",
        "execution preflight reviewer-facing decision changed",
    )
    checks.check(
        [item.get("id") for item in dispositions] == audit.get("nonheavy_missing_contract_blocks"),
        "non-heavy disposition ids no longer match non-heavy missing blocks",
    )
    checks.check(
        disposition_by_id.get("brown_mcphee_source_code_equivalent_law_open", {}).get("disposition")
        == "demoted_not_promoted"
        and disposition_by_id.get("brown_mcphee_source_code_equivalent_law_open", {}).get(
            "source_policy_rows_promoted"
        )
        == 0
        and disposition_by_id.get("brown_mcphee_source_code_equivalent_law_open", {}).get(
            "source_policy_rows_completed"
        )
        == 0
        and disposition_by_id.get("brown_mcphee_source_code_equivalent_law_open", {}).get(
            "frictional_source_policy_rows_demoted"
        )
        is True
        and disposition_by_id.get("brown_mcphee_source_code_equivalent_law_open", {}).get(
            "candidate_evidence_allowed_use"
        )
        == "local_dissipativity_residual_sensitivity_diagnostic_only"
        and disposition_by_id.get("brown_mcphee_source_code_equivalent_law_open", {}).get(
            "source_code_equivalence_certificate"
        )
        == "TFE_BROWN_MCPHEE_SOURCE_CODE_EQUIVALENCE_CERTIFICATE.json"
        and disposition_by_id.get("brown_mcphee_source_code_equivalent_law_open", {}).get(
            "certificate_status"
        )
        == brown_certificate.get("status")
        == "negative_source_code_equivalence_certificate_not_source_policy"
        and disposition_by_id.get("brown_mcphee_source_code_equivalent_law_open", {}).get(
            "certificate_available"
        )
        is True
        and disposition_by_id.get("brown_mcphee_source_code_equivalent_law_open", {}).get(
            "positive_source_code_equivalence_certified"
        )
        is False
        and disposition_by_id.get("brown_mcphee_source_code_equivalent_law_open", {}).get(
            "negative_certificate_nonheavy_block_closed"
        )
        is False
        and disposition_by_id.get("brown_mcphee_source_code_equivalent_law_open", {}).get(
            "source_policy_execution_invoked"
        )
        is False
        and disposition_by_id.get("brown_mcphee_source_code_equivalent_law_open", {}).get(
            "can_close_now"
        )
        is False
        and isinstance(
            disposition_by_id.get("brown_mcphee_source_code_equivalent_law_open", {}).get(
                "demotion_reason"
            ),
            str,
        )
        and len(
            disposition_by_id.get("brown_mcphee_source_code_equivalent_law_open", {}).get(
                "required_to_promote", []
            )
        )
        >= 5
        and disposition_by_id.get("brown_mcphee_source_code_equivalent_law_open", {}).get(
            "still_missing_source_code_equivalent_law"
        )
        is True
        and disposition_by_id.get("brown_mcphee_source_code_equivalent_law_open", {}).get(
            "transition_velocity_policy_resolved_from_source"
        )
        is False
        and disposition_by_id.get("brown_mcphee_source_code_equivalent_law_open", {}).get(
            "does_not_close_source_policy"
        )
        is True,
        "Brown-McPhee non-heavy demotion disposition changed",
    )
    checks.check(
        disposition_by_id.get("full_T10_source_grid_endpoint_policy_open", {}).get("disposition")
        == "demoted_not_promoted"
        and disposition_by_id.get("full_T10_source_grid_endpoint_policy_open", {}).get(
            "endpoint_incompatible_rows_demoted_from_source_policy"
        )
        == 4
        and disposition_by_id.get("full_T10_source_grid_endpoint_policy_open", {}).get(
            "source_policy_rows_completed"
        )
        == 0
        and disposition_by_id.get("full_T10_source_grid_endpoint_policy_open", {}).get(
            "source_grid_policy_resolved_for_full_T10"
        )
        is False
        and disposition_by_id.get("full_T10_source_grid_endpoint_policy_open", {}).get(
            "source_policy_exact_T_error_sampling_equivalent"
        )
        is False
        and disposition_by_id.get("full_T10_source_grid_endpoint_policy_open", {}).get(
            "algorithm_literal_exact_T_row_count"
        )
        == 2
        and disposition_by_id.get("full_T10_source_grid_endpoint_policy_open", {}).get(
            "algorithm_literal_overrun_row_count"
        )
        == 4
        and "diagnostic-only"
        in disposition_by_id.get("full_T10_source_grid_endpoint_policy_open", {}).get(
            "endpoint_incompatible_demotion_contract", ""
        )
        and disposition_by_id.get("full_T10_source_grid_endpoint_policy_open", {}).get(
            "endpoint_policy_closure_certificate"
        )
        == "TFE_FULL_T10_ENDPOINT_POLICY_CLOSURE_CERTIFICATE.json"
        and disposition_by_id.get("full_T10_source_grid_endpoint_policy_open", {}).get(
            "certificate_status"
        )
        == endpoint_certificate.get("status")
        == "negative_full_T10_endpoint_policy_certificate_not_source_policy"
        and disposition_by_id.get("full_T10_source_grid_endpoint_policy_open", {}).get(
            "certificate_available"
        )
        is True
        and disposition_by_id.get("full_T10_source_grid_endpoint_policy_open", {}).get(
            "positive_full_T10_endpoint_policy_certified"
        )
        is False
        and disposition_by_id.get("full_T10_source_grid_endpoint_policy_open", {}).get(
            "negative_certificate_nonheavy_block_closed"
        )
        is False
        and disposition_by_id.get("full_T10_source_grid_endpoint_policy_open", {}).get(
            "source_policy_execution_invoked"
        )
        is False
        and disposition_by_id.get("full_T10_source_grid_endpoint_policy_open", {}).get(
            "can_close_now"
        )
        is False
        and disposition_by_id.get("full_T10_source_grid_endpoint_policy_open", {}).get(
            "does_not_close_source_policy"
        )
        is True,
        "endpoint non-heavy demotion disposition changed",
    )
    checks.check(
        audit.get("grid_policy", {}).get("source_grid_policy_resolved_for_exact_T_compatible_rows")
        == grid.get("source_grid_policy_resolved_for_exact_T_compatible_rows")
        is True,
        "exact-T grid policy changed",
    )
    checks.check(
        audit.get("grid_policy", {}).get("source_grid_policy_resolved_for_full_T10")
        == grid.get("source_grid_policy_resolved_for_full_T10")
        is False,
        "full T10 grid policy overclaimed",
    )
    checks.check(audit.get("grid_policy", {}).get("integer_step_compatible_rows") == 2, "compatible grid rows changed")
    checks.check(audit.get("grid_policy", {}).get("integer_step_incompatible_rows") == 4, "incompatible grid rows changed")
    checks.check(
        audit.get("closure_decision", {}).get("can_close_tfe_lane_now") is False
        and audit.get("closure_decision", {}).get("can_close_b4_b7_now") is False,
        "closure decision overclaims lane/B4/B7 closure",
    )
    checks.check(
        gap_matrix.get("source_policy_rows_closed_by_preflight") == 0,
        "source-policy row audit gap matrix overclosed rows",
    )
    checks.check(
        brown_evidence.get("audit") == "TFE_BROWN_MCPHEE_SOURCE_LAW_BOUNDARY_AUDIT.json",
        "Brown-McPhee evidence audit path missing",
    )
    checks.check(
        brown_evidence.get("status") == brown_law.get("status"),
        "Brown-McPhee evidence status stale",
    )
    checks.check(
        brown_evidence.get("candidate_formula_encoded")
        == brown_law.get("brown_mcphee_candidate_friction_law_encoded")
        is True,
        "Brown-McPhee candidate formula evidence missing",
    )
    checks.check(
        brown_evidence.get("published_formula_structure_encoded")
        == brown_law.get("brown_mcphee_published_formula_structure_encoded")
        is True,
        "Brown-McPhee published formula evidence missing",
    )
    checks.check(
        brown_evidence.get("source_code_equivalent_law")
        == brown_law.get("brown_mcphee_source_code_equivalent_law")
        is False,
        "Brown-McPhee source-code equivalence overclaimed",
    )
    checks.check(
        brown_evidence.get("source_code_equivalence_certificate")
        == "TFE_BROWN_MCPHEE_SOURCE_CODE_EQUIVALENCE_CERTIFICATE.json",
        "Brown-McPhee source-code-equivalence certificate pointer missing",
    )
    checks.check(
        brown_evidence.get("certificate_status")
        == brown_certificate.get("status")
        == "negative_source_code_equivalence_certificate_not_source_policy",
        "Brown-McPhee source-code-equivalence certificate status changed",
    )
    checks.check(
        brown_evidence.get("certificate_available")
        == brown_certificate.get("certificate_available")
        is True,
        "Brown-McPhee source-code-equivalence certificate availability missing",
    )
    checks.check(
        brown_evidence.get("positive_source_code_equivalence_certified")
        == brown_certificate.get("positive_source_code_equivalence_certified")
        is False,
        "Brown-McPhee certificate overclaims positive source-code equivalence",
    )
    checks.check(
        brown_evidence.get("negative_certificate_nonheavy_block_closed")
        == brown_certificate.get("nonheavy_contract_block_closed")
        is False,
        "Brown-McPhee negative certificate unexpectedly closes the non-heavy block",
    )
    checks.check(
        brown_evidence.get("source_policy_execution_invoked")
        == brown_certificate.get("source_policy_execution_invoked")
        is False
        and brown_evidence.get("can_close_now")
        == brown_certificate.get("can_close_now")
        is False,
        "Brown-McPhee certificate execution/closure boundary changed",
    )
    checks.check(
        brown_evidence.get("transition_velocity_policy_resolved_from_source")
        == brown_law.get("brown_mcphee_transition_velocity_policy_resolved_from_source")
        is False,
        "Brown-McPhee transition-velocity policy overclaimed",
    )
    checks.check(
        brown_evidence.get("frictional_source_policy_rows_demoted")
        == brown_law.get("frictional_source_policy_rows_demoted")
        is True,
        "Brown-McPhee frictional demotion evidence missing",
    )
    checks.check(
        brown_evidence.get("frictional_source_policy_demotion_allowed_use")
        == brown_law.get("frictional_source_policy_row_demotion_contract", {}).get(
            "candidate_evidence_allowed_use"
        )
        == "local_dissipativity_residual_sensitivity_diagnostic_only",
        "Brown-McPhee frictional demotion allowed-use boundary changed",
    )
    checks.check(
        brown_evidence.get("closure_can_close_now")
        == brown_law.get("closure_decision", {}).get(
            "can_close_brown_mcphee_source_code_equivalent_law_now"
        )
        is False,
        "Brown-McPhee non-heavy blocker unexpectedly closed",
    )
    checks.check(
        brown_evidence.get("source_policy_rows_promoted") == brown_law.get("source_policy_rows_promoted") == 0,
        "Brown-McPhee evidence overpromotes source-policy rows",
    )
    checks.check(
        endpoint_evidence.get("grid_audit") == "TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.json",
        "endpoint evidence grid audit path missing",
    )
    checks.check(
        endpoint_evidence.get("algorithm_literal_probe") == "TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE.json",
        "endpoint probe path missing",
    )
    checks.check(
        endpoint_evidence.get("algorithm_literal_work_precision")
        == "TFE_ALGORITHM_LITERAL_WORK_PRECISION_AUDIT.json",
        "endpoint work-precision path missing",
    )
    checks.check(
        endpoint_evidence.get("endpoint_boundary_certificate")
        == "TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.json",
        "endpoint boundary certificate path missing",
    )
    checks.check(
        endpoint_evidence.get("endpoint_policy_closure_certificate")
        == "TFE_FULL_T10_ENDPOINT_POLICY_CLOSURE_CERTIFICATE.json",
        "endpoint policy closure certificate path missing",
    )
    checks.check(
        endpoint_evidence.get("certificate_status")
        == endpoint_certificate.get("status")
        == "negative_full_T10_endpoint_policy_certificate_not_source_policy",
        "endpoint policy closure certificate status stale",
    )
    checks.check(
        endpoint_evidence.get("certificate_available") is True,
        "endpoint policy closure certificate availability marker missing",
    )
    checks.check(
        endpoint_evidence.get("positive_full_T10_endpoint_policy_certified")
        == endpoint_certificate.get("positive_full_T10_endpoint_policy_certified")
        is False,
        "endpoint policy closure certificate overclaims positive closure",
    )
    checks.check(
        endpoint_evidence.get("negative_certificate_nonheavy_block_closed")
        == endpoint_certificate.get("nonheavy_contract_block_closed")
        is False,
        "endpoint policy closure certificate unexpectedly closes non-heavy block",
    )
    checks.check(
        endpoint_evidence.get("source_policy_execution_invoked")
        == endpoint_certificate.get("source_policy_execution_invoked")
        is False
        and endpoint_evidence.get("can_close_now")
        == endpoint_certificate.get("can_close_now")
        is False,
        "endpoint policy closure certificate execution/closure boundary changed",
    )
    checks.check(
        endpoint_evidence.get("source_text_fixed_h_loop_supported")
        == endpoint_probe.get("source_text_fixed_h_loop_supported")
        is True,
        "algorithm-literal fixed-h source-text support not carried into gap audit",
    )
    checks.check(
        endpoint_evidence.get("algorithm_literal_endpoint_policy")
        == endpoint_probe.get("algorithm_literal_endpoint_policy")
        == "fixed_h_until_tn_ge_tfinal",
        "algorithm-literal endpoint policy stale",
    )
    checks.check(
        endpoint_evidence.get("endpoint_probe_metric_rows")
        == endpoint_probe.get("metric_row_count")
        == 12,
        "endpoint probe metric row count stale",
    )
    checks.check(
        endpoint_evidence.get("endpoint_probe_terminal_overrun_rows")
        == endpoint_probe.get("terminal_overrun_rows")
        == 12,
        "endpoint probe terminal-overrun row count stale",
    )
    checks.check(
        endpoint_evidence.get("endpoint_probe_source_policy_rows_completed")
        == endpoint_probe.get("source_policy_rows_completed")
        == 0,
        "endpoint probe overclosed source-policy rows",
    )
    checks.check(
        endpoint_evidence.get("work_precision_rows") == endpoint_work.get("raw_row_count") == 12,
        "endpoint work-precision raw row count stale",
    )
    checks.check(
        endpoint_evidence.get("work_precision_summary_rows")
        == endpoint_work.get("summary_row_count")
        == 4,
        "endpoint work-precision summary row count stale",
    )
    checks.check(
        endpoint_evidence.get("work_precision_figure_available")
        == endpoint_work.get("work_precision_figure_available")
        is True,
        "endpoint work-precision figure evidence missing",
    )
    checks.check(
        endpoint_evidence.get("work_precision_b4_progress")
        == endpoint_work.get("decision", {}).get("b4_progress")
        is True,
        "endpoint work-precision B4 progress evidence missing",
    )
    checks.check(
        endpoint_evidence.get("work_precision_b4_closure")
        == endpoint_work.get("decision", {}).get("b4_closure")
        is False,
        "endpoint work-precision overclaims B4 closure",
    )
    checks.check(
        endpoint_evidence.get("source_policy_exact_T_error_sampling_equivalent")
        == endpoint_work.get("source_policy_exact_T_error_sampling_equivalent")
        is False,
        "endpoint source-policy exact-T sampling overclaimed",
    )
    checks.check(
        endpoint_evidence.get("source_policy_method_runner_equivalent")
        == endpoint_work.get("source_policy_method_runner_equivalent")
        is False,
        "endpoint source-policy method-runner equivalence overclaimed",
    )
    checks.check(
        endpoint_evidence.get("literal_overrun_bound_proved") is True
        and endpoint_boundary.get("theorem", {}).get("name")
        == "fixed_h_until_final_time_endpoint_bound",
        "endpoint overrun theorem was not carried into gap audit",
    )
    checks.check(
        endpoint_evidence.get("literal_exact_T_rows")
        == endpoint_boundary.get("algorithm_literal_exact_T_row_count")
        == 2,
        "endpoint boundary exact-T row count changed",
    )
    checks.check(
        endpoint_evidence.get("literal_overrun_rows")
        == endpoint_boundary.get("algorithm_literal_overrun_row_count")
        == 4,
        "endpoint boundary overrun row count changed",
    )
    checks.check(
        endpoint_evidence.get("boundary_source_policy_rows_completed")
        == endpoint_boundary.get("source_policy_rows_completed")
        == 0,
        "endpoint boundary overclosed source-policy rows",
    )
    checks.check(
        endpoint_evidence.get("boundary_full_T10_policy_resolved")
        == endpoint_boundary.get("source_grid_policy_resolved_for_full_T10")
        is False,
        "endpoint boundary overclosed full T10 policy",
    )
    checks.check(
        endpoint_evidence.get("boundary_exact_T_error_sampling_equivalent")
        == endpoint_boundary.get("source_policy_exact_T_error_sampling_equivalent")
        is False,
        "endpoint boundary overclaims exact-T sampling equivalence",
    )
    checks.check(
        endpoint_evidence.get("endpoint_incompatible_rows_demoted_from_source_policy")
        == endpoint_boundary.get("endpoint_incompatible_rows_demoted_from_source_policy")
        == 4,
        "endpoint demotion evidence changed",
    )
    checks.check(
        "diagnostic-only" in endpoint_evidence.get("endpoint_incompatible_demotion_contract", ""),
        "endpoint demotion contract missing from gap audit",
    )

    source_files = audit.get("source_files", {})
    checks.check(
        source_files.get("brown_mcphee_source_law_boundary")
        == "TFE_BROWN_MCPHEE_SOURCE_LAW_BOUNDARY_AUDIT.json",
        "Brown-McPhee source file missing from gap audit",
    )
    checks.check(
        source_files.get("brown_mcphee_source_code_equivalence_certificate")
        == "TFE_BROWN_MCPHEE_SOURCE_CODE_EQUIVALENCE_CERTIFICATE.json",
        "Brown-McPhee certificate source file missing from gap audit",
    )
    checks.check(
        source_files.get("algorithm_literal_endpoint_probe")
        == "TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE.json",
        "algorithm-literal endpoint source file missing from gap audit",
    )
    checks.check(
        source_files.get("algorithm_literal_work_precision")
        == "TFE_ALGORITHM_LITERAL_WORK_PRECISION_AUDIT.json",
        "algorithm-literal work-precision source file missing from gap audit",
    )
    checks.check(
        source_files.get("endpoint_policy_boundary_certificate")
        == "TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.json",
        "endpoint policy boundary certificate source file missing from gap audit",
    )
    checks.check(
        source_files.get("full_T10_endpoint_policy_closure_certificate")
        == "TFE_FULL_T10_ENDPOINT_POLICY_CLOSURE_CERTIFICATE.json",
        "full-T10 endpoint policy closure certificate source file missing from gap audit",
    )
    checks.check(
        source_files.get("full_T10_absolute_dae_lift_summary")
        == "TFE_FULL_T10_ABSOLUTE_DAE_LIFT_SUMMARY.json",
        "full T10 absolute DAE-lift source file missing from gap audit",
    )
    expected_candidate_backed_non_equivalent_ids = [
        "pendulum_absolute_coordinate_source_policy_dae_runner_missing",
        "tfe_newmark_trapezoidal_source_policy_method_runners_missing",
        "gauss6_fullva_absolute_coordinate_source_policy_runner_missing",
    ]
    candidate_backed_blocks = audit.get("candidate_backed_non_equivalent_runner_blocks", [])
    checks.check(
        audit.get("candidate_backed_non_equivalent_runner_block_count") == 3,
        "candidate-backed non-equivalent runner block count changed",
    )
    checks.check(
        audit.get("candidate_backed_non_equivalent_runner_block_ids")
        == expected_candidate_backed_non_equivalent_ids,
        "candidate-backed non-equivalent runner block ids changed",
    )
    checks.check(
        audit.get("source_policy_execution_missing_scope", {}).get(
            "candidate_backed_non_equivalent_runner_block_count"
        )
        == 3,
        "source-policy execution scope lost candidate-backed runner count",
    )
    checks.check(
        audit.get("source_policy_execution_missing_scope", {}).get(
            "candidate_backed_non_equivalent_runner_blocks"
        )
        == expected_candidate_backed_non_equivalent_ids,
        "source-policy execution scope lost candidate-backed runner ids",
    )
    by_candidate_block = {
        item.get("id"): item for item in candidate_backed_blocks if isinstance(item, dict)
    }
    checks.check(
        list(by_candidate_block) == expected_candidate_backed_non_equivalent_ids,
        "candidate-backed non-equivalent runner rows changed",
    )
    for block_id in expected_candidate_backed_non_equivalent_ids:
        row = by_candidate_block.get(block_id, {})
        checks.check(row.get("contract_present") is True, f"{block_id} contract marker missing")
        checks.check(row.get("candidate_backed") is True, f"{block_id} candidate-backed marker missing")
        checks.check(row.get("implemented") is False, f"{block_id} overclaims implementation")
        checks.check(row.get("source_policy_equivalent") is False, f"{block_id} overclaims source-policy equivalence")
        checks.check(row.get("source_policy_rows_completed") == 0, f"{block_id} overclosed source-policy rows")
        checks.check(
            row.get("closure_status") == "open_candidate_backed_not_source_policy_equivalent",
            f"{block_id} closure status changed",
        )

    for token in [
        "Status: **DAE runner contract gap open; not source policy**.",
        "Source-policy rows completed: `0`.",
        "Source spec candidate/source-policy boundary scaffold/use/DAE-equivalent/method-equivalent/rows: `True/diagnostic_scaffold_only_not_source_policy_reproduction/False/False/0`.",
        "Source spec Gauss6 candidate/source-policy DAE split available/use/runner/source rows/equivalent: `True/candidate_smoke_only_not_source_policy_dae_runner/False/0/False`.",
        "Source-policy DAE runner equivalent: `False`.",
        "Monolithic absolute-coordinate DAE time integrator: `False`.",
        "Pendulum DAE runner implemented: `False`.",
        "Bounded stepwise DAE runner rows/metric rows/step residual rows: `4/12/56`.",
        "Planar-lift rows/metric rows/source-policy rows: `12/36/0`.",
        "Runner-equivalence preflight closed/open/source rows: `25/6/0`.",
        "Source-policy absolute-coordinate DAE runner contract symbol/present/implemented: `True/True/False`.",
        "Source-policy absolute-coordinate DAE runner contract rows/metric rows/step residual rows/source rows/equivalent/monolithic: `4/12/56/0/False/False`.",
        "Source-method candidate contract rows/source rows/equivalent method/DAE: `5/0/False/False`.",
        "Source-policy method runner contract symbol/present/implemented: `True/True/False`.",
        "Source-policy method runner contract rows/source rows/equivalent method/DAE: `5/0/False/False`.",
        "Gauss6/FullVA candidate smoke/source-policy runner/source-policy rows: `True/False/0`.",
        "Gauss6/FullVA DAE candidate contract rows/source rows/equivalent/FullVA-equivalent: `1/0/False/False`.",
        "Source-policy Gauss6/FullVA DAE runner contract symbol/present/implemented: `True/True/False`.",
        "Source-policy Gauss6/FullVA DAE runner contract rows/source rows/equivalent/FullVA-equivalent/monolithic: `1/0/False/False/False`.",
        "Full T=10 absolute DAE-lift metric/step/source rows/monolithic/equivalent: `12/2800/0/False/False`.",
        "Full T=10 grid exact/incompatible/full-policy-resolved: `2/4/False`.",
        "Missing contract blocks: `6`.",
        "Non-heavy blocks dispositioned by demotion: `True`.",
        "Non-heavy demotion closes source-policy rows: `False`.",
        "Contract block accounting raw/non-heavy-terminal/effective-execution/source-rows: `6/2/4/0`.",
        "Effective source-policy execution contract blocks: `['pendulum_absolute_coordinate_source_policy_dae_runner_missing', 'tfe_newmark_trapezoidal_source_policy_method_runners_missing', 'gauss6_fullva_absolute_coordinate_source_policy_runner_missing', 'accepted_source_policy_work_precision_rows_not_executed_or_bound']`.",
        "Source-policy execution/integrator missing block count: `4`.",
        "Candidate-backed non-equivalent runner blocks/count: `['pendulum_absolute_coordinate_source_policy_dae_runner_missing', 'tfe_newmark_trapezoidal_source_policy_method_runners_missing', 'gauss6_fullva_absolute_coordinate_source_policy_runner_missing']/3`.",
        "Ready to execute source policy now: `False`.",
        "Source-policy execution preflight schema/status/opt-in: `tfe-source-policy-execution-preflight-v1/terminal_no_public_code_self_reproduction_attempted_not_promoted/False`.",
        "Source-policy execution preflight nonheavy/execution/promote/ready: `True/4/False/False`.",
        "Source-policy execution preflight required runner contracts: `['monolithic_absolute_coordinate_DAE_time_integrator', 'TFE_m1_m2_m3_Newmark_beta_trapezoidal_source_policy_method_runners', 'Gauss6_FullVA_absolute_coordinate_source_policy_DAE_runner', 'accepted_T10_source_policy_work_precision_rows']`.",
        "Brown--McPhee encoded/published/source-equivalent/transition-policy/close-now: `True/True/False/False/False`.",
        "Brown--McPhee source-code equivalence certificate status/available/positive/closed-block: `negative_source_code_equivalence_certificate_not_source_policy/True/False/False`.",
        "Brown--McPhee frictional source-policy demotion/allowed-use: `True/local_dissipativity_residual_sensitivity_diagnostic_only`.",
        "Algorithm-literal endpoint probe metric/overrun/source rows: `12/12/0`.",
        "Algorithm-literal work-precision rows/summary/figure/B4-progress/B4-closure: `12/4/True/True/False`.",
        "Endpoint boundary certificate proved/exact/overrun/source rows/full-policy/exact-T-equivalent: `True/2/4/0/False/False`.",
        "Full-T10 endpoint policy closure certificate status/available/positive/closed-block: `negative_full_T10_endpoint_policy_certificate_not_source_policy/True/False/False`.",
        "Endpoint-incompatible rows demoted from source-policy row set: `4`.",
        "Endpoint source-equivalent sampling/method-runner: `False/False`.",
        "Brown--McPhee non-heavy disposition/rows-promoted/allowed-use: `demoted_not_promoted/0/local_dissipativity_residual_sensitivity_diagnostic_only`.",
        "Endpoint non-heavy disposition/rows-demoted/full-policy: `demoted_not_promoted/4/False/False`.",
        "These demotions remove the non-heavy rows from source-policy promotion scope but do not close the TFE runner lane.",
        "No TFE source-policy rows are closed by this audit.",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("TFE DAE runner contract gap audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("TFE DAE runner contract gap audit validation: PASS")
    print(f"status={audit.get('status')}")
    print("missing_contract_blocks=6")
    print("candidate_backed_non_equivalent_runner_blocks=3")
    print("source_policy_rows_completed=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
