#!/usr/bin/env python3
"""Validate the TFE source-policy self-reproduction attempt certificate."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
EXPECTED_EXAMPLES = {"single_pendulum", "double_pendulum", "four_link", "slider_crank"}
EXPECTED_METHODS = {
    "tfe2026_Newmark_beta",
    "tfe2026_TFE_m1",
    "tfe2026_TFE_m2",
    "tfe2026_trapezoidal",
}
EXPECTED_EXECUTION_BLOCKS = [
    "pendulum_absolute_coordinate_source_policy_dae_runner_missing",
    "tfe_newmark_trapezoidal_source_policy_method_runners_missing",
    "gauss6_fullva_absolute_coordinate_source_policy_runner_missing",
    "accepted_source_policy_work_precision_rows_not_executed_or_bound",
]
EXPECTED_NONHEAVY_BLOCKS = [
    "brown_mcphee_source_code_equivalent_law_open",
    "full_T10_source_grid_endpoint_policy_open",
]


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


def main() -> int:
    checks = Checks()
    try:
        cert = read_json(PAPER / "TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.json")
        text = (PAPER / "TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.md").read_text(
            encoding="utf-8",
            errors="replace",
        )
        spec = read_json(PAPER / "TFE_SOURCE_POLICY_SPEC.json")
        public_code_recheck = read_json(PAPER / "TFE_PUBLIC_CODE_RECHECK_20260613.json")
        public_code_refresh_latest = read_json(PAPER / "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.json")
        model = read_json(PAPER / "TFE_SOURCE_PENDULUM_MODEL_AUDIT.json")
        gap = read_json(PAPER / "TFE_DAE_RUNNER_CONTRACT_GAP_AUDIT.json")
        brown_certificate = read_json(PAPER / "TFE_BROWN_MCPHEE_SOURCE_CODE_EQUIVALENCE_CERTIFICATE.json")
        endpoint_certificate = read_json(PAPER / "TFE_FULL_T10_ENDPOINT_POLICY_CLOSURE_CERTIFICATE.json")
        full_t10 = read_json(PAPER / "TFE_FULL_T10_ABSOLUTE_DAE_LIFT_SUMMARY.json")
        same_test = read_json(
            PAPER.parent.parent / "numerics" / "v048_cross_paper_same_test_benchmarks" / "results" /
            "tfe_source_pendulum_same_test_work_precision.json"
        )
    except Exception as exc:  # noqa: BLE001
        print(f"TFE self-reproduction attempt certificate validation: FAIL\n- {exc}")
        return 1

    rows = [row for row in cert.get("row_dispositions", []) if isinstance(row, dict)]
    single_rows = [row for row in rows if row.get("example") == "single_pendulum"]
    unsupported_rows = [row for row in rows if row.get("example") != "single_pendulum"]
    reconstructed = cert.get("reconstructed_layers", {})
    unresolved = cert.get("unresolved_obligations", {})
    execution_preflight = cert.get("source_policy_execution_preflight", {})
    gap_execution_preflight = gap.get("source_policy_execution_preflight", {})
    nonheavy_negative_certificates = cert.get("nonheavy_negative_certificates", {})
    brown_negative_certificate = nonheavy_negative_certificates.get("brown_mcphee", {})
    endpoint_negative_certificate = nonheavy_negative_certificates.get("full_T10_endpoint_policy", {})
    public_code = cert.get("public_code_status", {})
    method_contract = cert.get("source_method_candidate_runner_contract", {})
    gauss6_dae_candidate_contract = cert.get("gauss6_fullva_dae_candidate_contract", {})
    model_method_contract = model.get("source_method_candidate_runner_contract_smoke", {})
    model_gauss6_dae_candidate_contract = model.get(
        "gauss6_fullva_dae_candidate_contract_smoke",
        {},
    )

    checks.check(
        cert.get("schema") == "tfe-source-policy-self-reproduction-attempt-certificate-v1",
        "schema changed",
    )
    checks.check(cert.get("status") == "attempted_not_reproducible_not_promoted", "status changed")
    checks.check(cert.get("read_only") is True, "certificate must remain read-only")
    checks.check(cert.get("heavy_numerical_run_invoked") is False, "certificate invoked heavy run")
    checks.check(cert.get("run_v047_invoked") is False, "certificate invoked run_v047")
    checks.check(cert.get("v048_runner_invoked") is False, "certificate invoked v048 runner")
    checks.check(cert.get("row_count") == len(rows) == 16, "row count changed")
    checks.check(cert.get("source_policy_closed") is False, "certificate overclosed source policy")
    checks.check(cert.get("source_policy_closed_ratio") == "0/16", "source-policy closed ratio changed")
    checks.check(cert.get("source_policy_rows_total") == 16, "source-policy total row count changed")
    checks.check(cert.get("self_reproduction_attempted_rows") == 16, "attempted count changed")
    checks.check(cert.get("attempted_not_reproducible_rows") == 16, "not-reproducible count changed")
    checks.check(cert.get("unable_to_reproduce_rows") == 16, "unable-to-reproduce count changed")
    checks.check(
        cert.get("source_policy_rows_unable_to_reproduce") == 16,
        "source-policy unable-to-reproduce count changed",
    )
    checks.check(
        cert.get("final_nonpublic_code_disposition") == "unable_to_reproduce_not_promoted",
        "final nonpublic-code disposition changed",
    )
    checks.check(cert.get("single_pendulum_attempted_rows") == len(single_rows) == 4, "single rows changed")
    checks.check(
        cert.get("source_scope_unsupported_mechanism_rows") == len(unsupported_rows) == 12,
        "source-scope unsupported row count changed",
    )
    checks.check(cert.get("source_policy_rows_completed") == 0, "certificate overclosed source-policy rows")
    checks.check(cert.get("source_policy_rows_closed") == 0, "certificate overclosed source-policy row alias")
    checks.check(cert.get("source_policy_closed_rows") == 0, "certificate overclosed row dispositions")
    checks.check(cert.get("submission_ready") is False, "certificate overclaims submission readiness")
    checks.check(
        cert.get("external_superiority_claim_allowed") is False
        and cert.get("external_superiority_ready_rows") == 0,
        "certificate overclaims external superiority",
    )
    checks.check(
        cert.get("public_code_recheck_status")
        == public_code_recheck.get("status")
        == "public_code_rechecked_no_distinct_tfe_code_artifact_attempted_not_reproducible",
        "top-level public-code recheck status changed",
    )
    checks.check(
        cert.get("public_code_recheck_date") == public_code_recheck.get("date_checked") == "2026-06-13",
        "top-level public-code recheck date changed",
    )
    checks.check(
        cert.get("public_code_recheck_source_policy_rows_closed")
        == public_code_recheck.get("coverage", {}).get("source_policy_rows_closed")
        == 0,
        "top-level public-code recheck overclosed rows",
    )
    checks.check(
        cert.get("public_code_recheck_attempted_not_reproducible_rows")
        == public_code_recheck.get("coverage", {}).get("source_policy_rows_attempted_not_reproducible")
        == 16,
        "top-level public-code recheck attempted rows changed",
    )
    checks.check(
        cert.get("public_code_refresh_latest_status")
        == public_code_refresh_latest.get("status")
        == "public_code_refresh_20260620_no_positive_new_source_artifact_rows_remain_unable_to_reproduce",
        "latest public-code refresh status changed",
    )
    checks.check(
        cert.get("public_code_refresh_latest_date")
        == public_code_refresh_latest.get("date_checked")
        == "2026-06-20",
        "latest public-code refresh date changed",
    )
    checks.check(
        cert.get("public_code_refresh_latest_rows")
        == public_code_refresh_latest.get("row_count")
        == 20,
        "latest public-code refresh row count changed",
    )
    checks.check(
        cert.get("public_code_refresh_latest_current_queries")
        == public_code_refresh_latest.get("current_query_count")
        == 11,
        "latest public-code refresh query count changed",
    )
    checks.check(
        cert.get("public_code_refresh_latest_positive_artifact_rows")
        == public_code_refresh_latest.get("positive_public_code_artifact_rows")
        == 0,
        "latest public-code refresh positive artifact rows changed",
    )
    checks.check(
        cert.get("public_code_refresh_latest_source_policy_closed")
        == public_code_refresh_latest.get("source_policy_closed")
        is False,
        "latest public-code refresh overcloses source policy",
    )
    checks.check(
        cert.get("public_code_refresh_latest_source_policy_closed_ratio")
        == public_code_refresh_latest.get("source_policy_closed_ratio")
        == "0/20",
        "latest public-code refresh closed ratio changed",
    )
    checks.check(
        cert.get("public_code_refresh_latest_source_policy_rows_closed")
        == public_code_refresh_latest.get("source_policy_rows_closed")
        == 0,
        "latest public-code refresh overcloses rows",
    )

    checks.check(
        public_code.get("distinct_public_tfe_code_artifact_registered") is False,
        "public TFE code artifact unexpectedly registered",
    )
    checks.check(
        public_code.get("paper_spec_self_reproduction_attempted") is True,
        "paper-spec self reproduction attempt missing",
    )
    checks.check(
        public_code.get("available_basis") == "source_paper_text_plus_local_candidate_reconstruction",
        "available basis changed",
    )
    checks.check(
        public_code.get("public_code_recheck_certificate") == "TFE_PUBLIC_CODE_RECHECK_20260613.json",
        "public-code recheck certificate pointer missing",
    )
    checks.check(
        public_code.get("public_code_recheck_certificate_status")
        == public_code_recheck.get("status")
        == "public_code_rechecked_no_distinct_tfe_code_artifact_attempted_not_reproducible",
        "public-code recheck status changed",
    )
    checks.check(
        public_code.get("public_code_recheck_date") == public_code_recheck.get("date_checked") == "2026-06-13",
        "public-code recheck date changed",
    )
    checks.check(
        public_code.get("public_code_recheck_github_repository_search_total_count")
        == public_code_recheck.get("coverage", {}).get("github_repository_search_total_count")
        == 0,
        "public-code recheck repository count changed",
    )
    checks.check(
        public_code.get("public_code_recheck_github_user_search_total_count")
        == public_code_recheck.get("coverage", {}).get("github_user_search_total_count")
        == 0,
        "public-code recheck user count changed",
    )
    checks.check(
        public_code.get("public_code_recheck_github_code_search_api_status")
        == public_code_recheck.get("coverage", {}).get("github_code_search_api_status")
        == "requires_authentication",
        "public-code recheck code-search status changed",
    )
    checks.check(
        public_code.get("public_code_recheck_source_policy_rows_closed")
        == public_code_recheck.get("coverage", {}).get("source_policy_rows_closed")
        == 0,
        "public-code recheck overclosed rows",
    )
    checks.check(
        public_code.get("public_code_recheck_attempted_not_reproducible_rows")
        == public_code_recheck.get("coverage", {}).get("source_policy_rows_attempted_not_reproducible")
        == 16,
        "public-code recheck attempted rows changed",
    )
    checks.check(
        cert.get("candidate_vs_source_policy_boundary")
        == spec.get("candidate_vs_source_policy_boundary", {}),
        "candidate/source-policy boundary diverged from TFE source spec",
    )

    checks.check(
        cert.get("candidate_same_test_work_precision_rows") == same_test.get("row_count") == 18,
        "same-test raw row count changed",
    )
    checks.check(
        cert.get("candidate_same_test_summary_rows") == same_test.get("summary_row_count") == 6,
        "same-test summary row count changed",
    )
    checks.check(
        cert.get("candidate_same_test_ok_rows") == same_test.get("ok_row_count") == 18,
        "same-test ok row count changed",
    )
    checks.check(
        reconstructed.get("source_policy_spec_extracted") is True,
        "source-policy spec extraction marker missing",
    )
    checks.check(
        reconstructed.get("source_pendulum_parameter_model_implemented") is True,
        "source-pendulum parameter marker missing",
    )
    checks.check(
        reconstructed.get("same_test_candidate_work_precision_available") is True,
        "same-test candidate work/precision not available",
    )
    checks.check(reconstructed.get("same_test_candidate_raw_rows") == 18, "raw CSV row count changed")
    checks.check(reconstructed.get("same_test_candidate_summary_rows") == 6, "summary CSV row count changed")
    checks.check(
        reconstructed.get("absolute_coordinate_planar_lift_probe_rows") == 12,
        "absolute-coordinate planar-lift row count changed",
    )
    checks.check(
        reconstructed.get("bounded_absolute_coordinate_dae_runner_rows") == 4,
        "bounded DAE runner row count changed",
    )
    checks.check(
        reconstructed.get("dae_trajectory_bridge_contract_rows") == 12,
        "DAE bridge contract row count changed",
    )
    checks.check(
        reconstructed.get("full_T10_absolute_dae_lift_completed")
        == full_t10.get("full_T10_absolute_coordinate_lift_completed")
        is True,
        "full-T10 DAE-lift completion changed",
    )
    checks.check(
        reconstructed.get("full_T10_absolute_dae_lift_step_residual_rows")
        == full_t10.get("step_residual_row_count")
        == 2800,
        "full-T10 DAE-lift step row count changed",
    )
    checks.check(
        reconstructed.get("source_method_candidate_runner_contract_implemented")
        == model.get("source_method_candidate_runner_contract_implemented")
        is True,
        "source-method candidate contract marker missing",
    )
    checks.check(
        reconstructed.get("source_method_candidate_runner_contract_rows")
        == model.get("source_method_candidate_runner_contract_rows")
        == 5,
        "source-method candidate contract row count changed",
    )
    checks.check(
        reconstructed.get("source_method_candidate_runner_contract_source_policy_rows_completed")
        == model.get("source_method_candidate_runner_contract_source_policy_rows_completed")
        == 0,
        "source-method candidate contract overclosed source-policy rows",
    )
    checks.check(
        reconstructed.get("source_method_candidate_runner_contract_method_equivalent")
        == model.get("source_method_candidate_runner_contract_method_equivalent")
        is False,
        "source-method candidate contract overclaims method equivalence",
    )
    checks.check(
        reconstructed.get("source_method_candidate_runner_contract_dae_equivalent")
        == model.get("source_method_candidate_runner_contract_dae_equivalent")
        is False,
        "source-method candidate contract overclaims DAE equivalence",
    )
    checks.check(
        reconstructed.get("gauss6_fullva_dae_candidate_contract_implemented")
        == model.get("gauss6_fullva_dae_candidate_contract_implemented")
        is True,
        "Gauss6 DAE candidate contract marker missing",
    )
    checks.check(
        reconstructed.get("gauss6_fullva_dae_candidate_contract_rows")
        == model.get("gauss6_fullva_dae_candidate_contract_rows")
        == 1,
        "Gauss6 DAE candidate contract row count changed",
    )
    checks.check(
        reconstructed.get("gauss6_fullva_dae_candidate_contract_source_policy_rows_completed")
        == model.get("gauss6_fullva_dae_candidate_contract_source_policy_rows_completed")
        == 0,
        "Gauss6 DAE candidate contract overclosed source-policy rows",
    )
    checks.check(
        reconstructed.get("gauss6_fullva_dae_candidate_contract_dae_equivalent")
        == model.get("gauss6_fullva_dae_candidate_contract_dae_equivalent")
        is False,
        "Gauss6 DAE candidate contract overclaims DAE equivalence",
    )
    checks.check(
        reconstructed.get("gauss6_fullva_dae_candidate_contract_fullva_dae_equivalent")
        == model.get("gauss6_fullva_dae_candidate_contract_fullva_dae_equivalent")
        is False,
        "Gauss6 DAE candidate contract overclaims FullVA DAE equivalence",
    )
    checks.check(
        method_contract.get("schema")
        == model_method_contract.get("schema")
        == "tfe-source-method-candidate-runner-contract-smoke-v1",
        "source-method candidate contract schema missing",
    )
    checks.check(
        method_contract.get("runner_api")
        == model_method_contract.get("runner_api")
        == "source_method_candidate_runner_contract_smoke",
        "source-method candidate contract runner API missing",
    )
    checks.check(
        method_contract.get("accepted_use")
        == model_method_contract.get("accepted_use")
        == "candidate_method_dispatch_contract_not_source_policy",
        "source-method candidate contract boundary changed",
    )
    checks.check(
        method_contract.get("row_count") == model_method_contract.get("row_count") == 5,
        "source-method candidate contract row count stale",
    )
    checks.check(
        method_contract.get("method_count") == model_method_contract.get("method_count") == 5,
        "source-method candidate contract method count stale",
    )
    checks.check(
        method_contract.get("paper_methods")
        == sorted(
            {
                str(row.get("paper_method"))
                for row in model_method_contract.get("rows", [])
                if isinstance(row, dict) and row.get("paper_method")
            }
        ),
        "source-method candidate contract method list stale",
    )
    checks.check(
        method_contract.get("b4_method_coverage_count") == 4
        and method_contract.get("b4_method_coverage_complete") is True,
        "source-method candidate contract does not cover the four B4 TFE methods",
    )
    checks.check(
        method_contract.get("all_step_states_finite")
        == model_method_contract.get("all_step_states_finite")
        is True,
        "source-method candidate contract finite-state marker missing",
    )
    checks.check(
        method_contract.get("all_candidate_residuals_below_1e_8")
        == model_method_contract.get("all_candidate_residuals_below_1e_8")
        is True,
        "source-method candidate contract residual marker missing",
    )
    checks.check(
        float(method_contract.get("max_candidate_step_residual_norm"))
        == float(model_method_contract.get("max_candidate_step_residual_norm")),
        "source-method candidate contract residual norm stale",
    )
    checks.check(
        method_contract.get("source_policy_rows_completed")
        == model_method_contract.get("source_policy_rows_completed")
        == 0,
        "source-method candidate contract overclosed source-policy rows",
    )
    checks.check(
        method_contract.get("source_policy_method_runner_equivalent")
        == model_method_contract.get("source_policy_method_runner_equivalent")
        is False,
        "source-method candidate contract overclaims method equivalence",
    )
    checks.check(
        method_contract.get("source_policy_dae_runner_equivalent")
        == model_method_contract.get("source_policy_dae_runner_equivalent")
        is False,
        "source-method candidate contract overclaims DAE equivalence",
    )
    checks.check(
        gauss6_dae_candidate_contract.get("schema")
        == model_gauss6_dae_candidate_contract.get("schema")
        == "tfe-gauss6-fullva-dae-candidate-contract-smoke-v1",
        "Gauss6 DAE candidate contract schema missing",
    )
    checks.check(
        gauss6_dae_candidate_contract.get("runner_api")
        == model_gauss6_dae_candidate_contract.get("runner_api")
        == "source_gauss6_fullva_dae_candidate_contract_smoke",
        "Gauss6 DAE candidate contract runner API missing",
    )
    checks.check(
        gauss6_dae_candidate_contract.get("accepted_use")
        == model_gauss6_dae_candidate_contract.get("accepted_use")
        == "gauss6_fullva_dae_candidate_contract_not_source_policy",
        "Gauss6 DAE candidate contract boundary changed",
    )
    checks.check(
        gauss6_dae_candidate_contract.get("row_count")
        == model_gauss6_dae_candidate_contract.get("row_count")
        == 1,
        "Gauss6 DAE candidate contract row count stale",
    )
    checks.check(
        gauss6_dae_candidate_contract.get("all_step_states_finite")
        == model_gauss6_dae_candidate_contract.get("all_step_states_finite")
        is True,
        "Gauss6 DAE candidate contract finite-state marker missing",
    )
    checks.check(
        gauss6_dae_candidate_contract.get("all_candidate_residuals_below_1e_8")
        == model_gauss6_dae_candidate_contract.get("all_candidate_residuals_below_1e_8")
        is True,
        "Gauss6 DAE candidate contract residual marker missing",
    )
    checks.check(
        gauss6_dae_candidate_contract.get("source_policy_rows_completed")
        == model_gauss6_dae_candidate_contract.get("source_policy_rows_completed")
        == 0,
        "Gauss6 DAE candidate contract overclosed source-policy rows",
    )
    checks.check(
        gauss6_dae_candidate_contract.get("source_policy_dae_runner_equivalent")
        == model_gauss6_dae_candidate_contract.get("source_policy_dae_runner_equivalent")
        is False,
        "Gauss6 DAE candidate contract overclaims DAE equivalence",
    )
    checks.check(
        gauss6_dae_candidate_contract.get("fullva_dae_source_policy_equivalent")
        == model_gauss6_dae_candidate_contract.get("fullva_dae_source_policy_equivalent")
        is False,
        "Gauss6 DAE candidate contract overclaims FullVA DAE equivalence",
    )

    checks.check(
        unresolved.get("nonheavy_missing_contract_blocks") == EXPECTED_NONHEAVY_BLOCKS,
        "non-heavy missing blocks changed",
    )
    checks.check(
        unresolved.get("source_policy_execution_missing_contract_blocks") == EXPECTED_EXECUTION_BLOCKS,
        "execution missing blocks changed",
    )
    checks.check(
        unresolved.get("source_policy_dae_runner_equivalent")
        == gap.get("source_policy_dae_runner_equivalent")
        is False,
        "DAE equivalence overclaimed",
    )
    checks.check(
        unresolved.get("source_policy_method_runner_equivalent")
        == gap.get("source_policy_method_runner_equivalent")
        is False,
        "method equivalence overclaimed",
    )
    checks.check(
        unresolved.get("monolithic_absolute_coordinate_dae_time_integrator")
        == gap.get("monolithic_absolute_coordinate_dae_time_integrator")
        is False,
        "monolithic DAE integrator overclaimed",
    )
    checks.check(
        unresolved.get("brown_mcphee_source_code_equivalent_law") is False,
        "Brown-McPhee source-law equivalence overclaimed",
    )
    checks.check(
        unresolved.get("brown_mcphee_transition_velocity_policy_resolved_from_source") is False,
        "Brown-McPhee transition policy overclaimed",
    )
    checks.check(
        unresolved.get("source_grid_policy_resolved_for_full_T10") is False,
        "full-T10 grid policy overclaimed",
    )
    checks.check(
        execution_preflight == gap_execution_preflight,
        "source-policy execution preflight drifted from DAE gap audit",
    )
    checks.check(
        execution_preflight.get("schema") == "tfe-source-policy-execution-preflight-v1"
        and execution_preflight.get("status")
        == "terminal_no_public_code_self_reproduction_attempted_not_promoted",
        "execution preflight schema/status changed",
    )
    checks.check(
        execution_preflight.get("current_route")
        == "no_public_code_self_reproduction_attempted_unable_to_reproduce_not_promoted",
        "execution preflight current route changed",
    )
    checks.check(
        cert.get("source_policy_execution_preflight_status")
        == execution_preflight.get("status")
        == "terminal_no_public_code_self_reproduction_attempted_not_promoted",
        "top-level execution preflight status changed",
    )
    checks.check(
        cert.get("source_policy_execution_preflight_current_route")
        == execution_preflight.get("current_route")
        == "no_public_code_self_reproduction_attempted_unable_to_reproduce_not_promoted",
        "top-level execution preflight route changed",
    )
    checks.check(
        execution_preflight.get("execution_blocks") == EXPECTED_EXECUTION_BLOCKS
        and execution_preflight.get("execution_block_count") == 4,
        "execution preflight blocks changed",
    )
    checks.check(
        execution_preflight.get("source_policy_rows_completed") == 0
        and execution_preflight.get("ready_to_execute_source_policy_now") is False
        and execution_preflight.get("can_promote_any_tfe_source_policy_row_now") is False,
        "execution preflight overclaims readiness or source-policy rows",
    )
    checks.check(
        cert.get("source_policy_execution_preflight_source_policy_rows_completed")
        == execution_preflight.get("source_policy_rows_completed")
        == 0,
        "top-level execution preflight overclosed source-policy rows",
    )
    checks.check(
        cert.get("source_policy_execution_preflight_ready_now")
        == execution_preflight.get("ready_to_execute_source_policy_now")
        is False,
        "top-level execution preflight overclaims ready-now",
    )
    checks.check(
        cert.get("source_policy_execution_preflight_can_promote_rows_now")
        == execution_preflight.get("can_promote_any_tfe_source_policy_row_now")
        is False,
        "top-level execution preflight overclaims promotion readiness",
    )
    checks.check(
        execution_preflight.get("run_v047_invoked") is False
        and execution_preflight.get("v048_runner_invoked") is False
        and execution_preflight.get("heavy_numerical_run_invoked") is False,
        "execution preflight unexpectedly invoked a runner",
    )
    checks.check(
        execution_preflight.get("reopen_condition")
        == "new_public_or_source_code_equivalent_tfe_implementation_artifact",
        "execution preflight reopen condition changed",
    )
    checks.check(
        cert.get("reopen_condition")
        == execution_preflight.get("reopen_condition")
        == "new_public_or_source_code_equivalent_tfe_implementation_artifact",
        "top-level reopen condition changed",
    )
    required_next_actions = cert.get("required_next_actions", [])
    checks.check(
        isinstance(required_next_actions, list) and len(required_next_actions) == 3,
        "required next actions missing",
    )
    checks.check(
        any("attempted-not-reproducible/not-promoted" in str(item) for item in required_next_actions)
        and any("source-code-equivalent TFE implementation artifact" in str(item) for item in required_next_actions)
        and any("runner contracts" in str(item) for item in required_next_actions),
        "required next actions do not carry execution preflight boundary",
    )
    checks.check(
        brown_negative_certificate.get("certificate")
        == "TFE_BROWN_MCPHEE_SOURCE_CODE_EQUIVALENCE_CERTIFICATE.json",
        "Brown-McPhee negative certificate pointer missing",
    )
    checks.check(
        brown_negative_certificate.get("status")
        == brown_certificate.get("status")
        == "negative_source_code_equivalence_certificate_not_source_policy",
        "Brown-McPhee negative certificate status changed",
    )
    checks.check(
        brown_negative_certificate.get("certificate_available")
        == brown_certificate.get("certificate_available")
        is True,
        "Brown-McPhee negative certificate availability missing",
    )
    checks.check(
        brown_negative_certificate.get("positive_source_code_equivalence_certified")
        == brown_certificate.get("positive_source_code_equivalence_certified")
        is False,
        "Brown-McPhee negative certificate overclaims source-code equivalence",
    )
    checks.check(
        brown_negative_certificate.get("nonheavy_contract_block_closed")
        == brown_certificate.get("nonheavy_contract_block_closed")
        is False,
        "Brown-McPhee negative certificate unexpectedly closes non-heavy block",
    )
    checks.check(
        brown_negative_certificate.get("source_policy_rows_completed")
        == brown_certificate.get("source_policy_rows_completed")
        == 0,
        "Brown-McPhee negative certificate overclosed source-policy rows",
    )
    checks.check(
        endpoint_negative_certificate.get("certificate")
        == "TFE_FULL_T10_ENDPOINT_POLICY_CLOSURE_CERTIFICATE.json",
        "full-T10 endpoint negative certificate pointer missing",
    )
    checks.check(
        endpoint_negative_certificate.get("status")
        == endpoint_certificate.get("status")
        == "negative_full_T10_endpoint_policy_certificate_not_source_policy",
        "full-T10 endpoint negative certificate status changed",
    )
    checks.check(
        endpoint_negative_certificate.get("certificate_available")
        == endpoint_certificate.get("certificate_available")
        is True,
        "full-T10 endpoint negative certificate availability missing",
    )
    checks.check(
        endpoint_negative_certificate.get("positive_full_T10_endpoint_policy_certified")
        == endpoint_certificate.get("positive_full_T10_endpoint_policy_certified")
        is False,
        "full-T10 endpoint negative certificate overclaims positive endpoint policy",
    )
    checks.check(
        endpoint_negative_certificate.get("nonheavy_contract_block_closed")
        == endpoint_certificate.get("nonheavy_contract_block_closed")
        is False,
        "full-T10 endpoint negative certificate unexpectedly closes non-heavy block",
    )
    checks.check(
        endpoint_negative_certificate.get("source_policy_rows_completed")
        == endpoint_certificate.get("source_policy_rows_completed")
        == 0,
        "full-T10 endpoint negative certificate overclosed source-policy rows",
    )
    checks.check(
        endpoint_negative_certificate.get("source_grid_policy_resolved_for_full_T10")
        == endpoint_certificate.get("source_grid_policy_resolved_for_full_T10")
        is False,
        "full-T10 endpoint negative certificate overclaims grid policy resolution",
    )
    checks.check(
        nonheavy_negative_certificates.get("source_policy_rows_completed_by_negative_certificates") == 0,
        "negative certificates overclosed source-policy rows",
    )
    checks.check(
        nonheavy_negative_certificates.get("nonheavy_blocks_closed_by_negative_certificates") is False,
        "negative certificates unexpectedly close non-heavy blocks",
    )

    checks.check({row.get("method") for row in rows} == EXPECTED_METHODS, "method set changed")
    checks.check({row.get("example") for row in rows} == EXPECTED_EXAMPLES, "example set changed")
    for row in rows:
        label = f"{row.get('method')}:{row.get('example')}"
        checks.check(row.get("self_reproduction_attempted") is True, f"{label} not attempted")
        checks.check(row.get("candidate_method_summary_available") is True, f"{label} missing candidate summary")
        checks.check(
            row.get("method_covered_by_source_method_candidate_contract") is True,
            f"{label} missing method-contract coverage marker",
        )
        checks.check(
            row.get("source_method_candidate_contract_source_policy_rows_completed") == 0,
            f"{label} method contract overclosed source-policy rows",
        )
        checks.check(
            row.get("source_method_candidate_contract_method_equivalent") is False,
            f"{label} method contract overclaims method equivalence",
        )
        checks.check(
            row.get("source_method_candidate_contract_dae_equivalent") is False,
            f"{label} method contract overclaims DAE equivalence",
        )
        checks.check(row.get("full_T10_absolute_dae_lift_available") is True, f"{label} missing full-T10 lift")
        checks.check(row.get("source_policy_method_runner_equivalent") is False, f"{label} overclaims method")
        checks.check(row.get("source_policy_dae_runner_equivalent") is False, f"{label} overclaims DAE")
        checks.check(row.get("source_policy_closed") is False, f"{label} overclosed")
        checks.check(row.get("external_superiority_ready") is False, f"{label} overclaims external ready")
        checks.check(row.get("unable_to_reproduce") is True, f"{label} missing unable-to-reproduce marker")
        checks.check(
            row.get("source_policy_disposition") == "attempted_not_reproducible",
            f"{label} disposition changed",
        )
        checks.check(
            row.get("final_nonpublic_code_disposition") == "unable_to_reproduce_not_promoted",
            f"{label} final nonpublic-code disposition changed",
        )
        checks.check(row.get("blocking_contract_blocks"), f"{label} missing blockers")
        if row.get("example") == "single_pendulum":
            checks.check(row.get("source_suite_scope_supported") is True, f"{label} should be in source scope")
            checks.check(
                row.get("source_method_candidate_contract_available_for_row") is True,
                f"{label} should bind the source-method candidate contract",
            )
            checks.check(
                row.get("source_method_candidate_contract_accepted_use")
                == "candidate_method_dispatch_contract_not_source_policy",
                f"{label} method-contract accepted-use boundary changed",
            )
            checks.check(
                row.get("primary_nonreproducibility_reason")
                == "paper_spec_candidate_runner_not_source_policy_equivalent",
                f"{label} reason changed",
            )
        else:
            checks.check(row.get("source_suite_scope_supported") is False, f"{label} should be out of source scope")
            checks.check(
                row.get("source_method_candidate_contract_available_for_row") is False,
                f"{label} should not use source-pendulum method contract as mechanism support",
            )
            checks.check(
                row.get("source_method_candidate_contract_accepted_use") is None,
                f"{label} should not carry source-pendulum method-contract accepted-use",
            )
            checks.check(
                row.get("primary_nonreproducibility_reason")
                == "tfe_source_paper_pendulum_suite_does_not_define_this_mechanism_runner",
                f"{label} reason changed",
            )

    checks.check(
        cert.get("closure_decision", {}).get("can_close_tfe_source_policy_rows_now") is False,
        "closure decision overclaims source-policy rows",
    )
    checks.check(
        cert.get("closure_decision", {}).get("can_claim_external_superiority_from_tfe_now") is False,
        "closure decision overclaims external superiority",
    )
    closure_reason = cert.get("closure_decision", {}).get("reason", "")
    checks.check("negative Brown--McPhee" in closure_reason, "closure reason missing Brown negative certificate")
    checks.check("full-T10 endpoint-policy" in closure_reason, "closure reason missing endpoint negative certificate")
    checks.check("close zero source-policy rows" in closure_reason, "closure reason missing zero-row boundary")
    source_files = cert.get("source_files", [])
    checks.check(
        "TFE_PUBLIC_CODE_RECHECK_20260613.json" in source_files
        and "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.json" in source_files
        and
        "TFE_SOURCE_POLICY_SPEC.json" in source_files
        and "TFE_DAE_RUNNER_CONTRACT_GAP_AUDIT.json" in source_files
        and "TFE_BROWN_MCPHEE_SOURCE_CODE_EQUIVALENCE_CERTIFICATE.json" in source_files
        and "TFE_FULL_T10_ENDPOINT_POLICY_CLOSURE_CERTIFICATE.json" in source_files
        and "TFE_FULL_T10_ABSOLUTE_DAE_LIFT_SUMMARY.json" in source_files,
        "source files missing from certificate",
    )

    for token in [
        "Status: **attempted not reproducible; not promoted**.",
        "Rows audited: `16`.",
        "Attempted-not-reproducible rows: `16`.",
        "Unable-to-reproduce rows: `16`.",
        "Final nonpublic-code disposition: `unable_to_reproduce_not_promoted`.",
        "Source-policy closed rows: `0`.",
        "External-superiority ready rows: `0`.",
        "Public-code recheck status/repo hits/user hits/code-search/attempted/closed: `public_code_rechecked_no_distinct_tfe_code_artifact_attempted_not_reproducible/0/0/requires_authentication/16/0`.",
        "Latest public-code refresh status/date/rows/queries/positive/closed: `public_code_refresh_20260620_no_positive_new_source_artifact_rows_remain_unable_to_reproduce/2026-06-20/20/11/0/0/20`.",
        "`4/12`",
        "`18/6/18`",
        "`5/4/0/False/False`",
        "`True/True/3.204e-11`",
        "`1/0/False/False`",
        "`True/2800`",
        "`False/False/False`",
        "Non-heavy negative certificates Brown/endpoint status: `negative_source_code_equivalence_certificate_not_source_policy/negative_full_T10_endpoint_policy_certificate_not_source_policy`.",
        "Non-heavy certificates closed source-policy rows/blocks: `0/False`.",
        "Source-policy execution preflight status/blocks/ready/promote: `terminal_no_public_code_self_reproduction_attempted_not_promoted/4/False/False`.",
        "Source-policy execution preflight route/reopen/source rows: `no_public_code_self_reproduction_attempted_unable_to_reproduce_not_promoted/new_public_or_source_code_equivalent_tfe_implementation_artifact/0`.",
        "## Required Next Actions",
        "`attempted_not_reproducible`",
    ]:
        checks.check(token in text, f"markdown missing token: {token}")

    if checks.errors:
        print("TFE self-reproduction attempt certificate validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("TFE self-reproduction attempt certificate validation: PASS")
    print("attempted_not_reproducible_rows=16/16")
    print("unable_to_reproduce_rows=16/16")
    print("public_code_recheck_status=public_code_rechecked_no_distinct_tfe_code_artifact_attempted_not_reproducible")
    print("reopen_condition=new_public_or_source_code_equivalent_tfe_implementation_artifact")
    print("source_policy_execution_preflight_status=terminal_no_public_code_self_reproduction_attempted_not_promoted")
    print("public_code_refresh_latest_positive_artifact_rows=0")
    print("source_policy_closed=0/16")
    print("source_policy_closed_rows=0")
    print("external_superiority_ready_rows=0")
    print("submission_ready=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
