#!/usr/bin/env python3
"""Validate the B2 source-policy remaining-work manifest."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent

EXPECTED_REMAINING: list[str] = []
EXPECTED_CLOSED_BY_DEMOTION = [
    "vp2024_code_resolution_or_demotion",
    "hi2022_public_code_same_test_rows",
    "ra2021_public_code_same_test_rows",
    "original_tfe_pendulum_error_order_work_rows",
]
EXPECTED_ACTIVE_COUNTS: dict[str, int] = {}
EXPECTED_DEMOTED_COUNTS = {
    "ra2021_absolute_coordinate": 5,
    "hi2022_half_implicit": 3,
    "tfe2026_original_pendulum": 4,
    "vp2024_velocity_partitioning": 3,
}
EXPECTED_ALL_COUNTS = {
    "ra2021_absolute_coordinate": 5,
    "hi2022_half_implicit": 3,
    "tfe2026_original_pendulum": 4,
    "vp2024_velocity_partitioning": 3,
}


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
        manifest = read_json(PAPER / "B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.json")
        manifest_md = read_text(PAPER / "B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.md")
        row_ledger = read_json(PAPER / "SOURCE_POLICY_ROW_CLOSURE_LEDGER.json")
        demotion = read_json(PAPER / "EXTERNAL_SUITE_DEMOTION_LEDGER.json")
        blocker = read_json(PAPER / "CMAME_BLOCKER_CLOSURE_GATE.json")
    except Exception as exc:  # noqa: BLE001
        print(f"b2 source-policy remaining-work manifest validation: FAIL\n- {exc}")
        return 1

    rows = manifest.get("rows", [])
    suite_summaries = manifest.get("suite_summaries", [])
    b2 = next((item for item in blocker.get("blockers", []) if item.get("id") == "B2"), {})

    checks.check(
        manifest.get("schema") == "b2-source-policy-remaining-work-manifest-v1",
        "schema changed",
    )
    checks.check(
        manifest.get("status") == "route_b_all_external_suites_demoted_no_active_external_superiority_rows",
        "status changed",
    )
    checks.check(manifest.get("submission_ready") is False, "manifest overclaims submission readiness")
    checks.check(
        manifest.get("external_superiority_claim_allowed") is False,
        "manifest overclaims external superiority",
    )
    checks.check(manifest.get("row_count") == len(rows) == 15, "row count changed")
    checks.check(
        manifest.get("row_count") == row_ledger.get("coverage", {}).get("flagged_row_count"),
        "row count no longer matches row ledger",
    )
    checks.check(manifest.get("active_flagged_row_count") == 0, "active flagged-row count changed")
    checks.check(manifest.get("demoted_flagged_row_count") == 15, "demoted flagged-row count changed")
    checks.check(manifest.get("source_policy_closed_rows") == 0, "source-policy rows unexpectedly closed")
    checks.check(
        manifest.get("external_superiority_ready_rows") == 0,
        "external-superiority-ready rows unexpectedly present",
    )
    checks.check(manifest.get("suite_counts") == EXPECTED_ALL_COUNTS, "suite counts changed")
    checks.check(manifest.get("active_suite_counts") == EXPECTED_ACTIVE_COUNTS, "active suite counts changed")
    checks.check(manifest.get("demoted_suite_counts") == EXPECTED_DEMOTED_COUNTS, "demoted suite counts changed")
    checks.check(
        manifest.get("b2_closed_by_demotion")
        == demotion.get("b2_subrequirements_closed_by_demotion")
        == EXPECTED_CLOSED_BY_DEMOTION,
        "B2 demotion-closed requirements changed",
    )
    checks.check(
        manifest.get("b2_remaining_requirements") == EXPECTED_REMAINING,
        "B2 remaining requirements changed",
    )
    checks.check(manifest.get("b2_can_close_now") is True, "manifest should close B2 by Route B claim demotion")
    checks.check(manifest.get("b4_can_close_now") is False, "manifest incorrectly closes B4")
    checks.check(
        manifest.get("route_b_b2_claim_boundary_synchronized") is True,
        "Route B B2 claim-boundary synchronized marker missing",
    )
    checks.check(
        manifest.get("route_b_b4_claim_boundary_synchronized") is True,
        "Route B B4 claim-boundary synchronized marker missing",
    )
    checks.check(
        manifest.get("route_b_b2_closure_ready_pending_gate_sync") is False,
        "Route B B2 pending-gate-sync marker should be false",
    )
    checks.check(
        manifest.get("route_b_b4_closure_ready_pending_gate_sync") is False,
        "Route B B4 pending-gate-sync marker should be false",
    )
    checks.check(
        manifest.get("remaining_active_suites", []) == [],
        "active suite set changed",
    )
    checks.check(
        manifest.get("demoted_suites")
        == [
            "hi2022_half_implicit",
            "ra2021_absolute_coordinate",
            "tfe2026_original_pendulum",
            "vp2024_velocity_partitioning",
        ],
        "demoted suite set changed",
    )

    for row in rows:
        label = f"row {row.get('row_index')}"
        checks.check(isinstance(row.get("suite_id"), str) and row.get("suite_id"), f"{label} suite id missing")
        checks.check(isinstance(row.get("status"), str) and row.get("status"), f"{label} status missing")
        checks.check(isinstance(row.get("action"), str) and row.get("action"), f"{label} action missing")
        checks.check(row.get("source_policy_closed") is False, f"{label} unexpectedly source-policy closed")
        checks.check(row.get("external_superiority_ready") is False, f"{label} unexpectedly claim-ready")
        checks.check(row.get("demoted_from_external_superiority_scope") is True, f"{label} row not demoted")
        checks.check(row.get("active_b2_requirement") is False, f"{label} row still active")

    summary_by_suite = {item.get("suite_id"): item for item in suite_summaries}
    checks.check(
        summary_by_suite.get("ra2021_absolute_coordinate", {}).get("public_baseline_order_groups_completed") == 12,
        "RA2021 public baseline group count changed",
    )
    checks.check(
        summary_by_suite.get("ra2021_absolute_coordinate", {}).get("public_timing_rows_completed") == 12,
        "RA2021 timing row count changed",
    )
    checks.check(
        summary_by_suite.get("ra2021_absolute_coordinate", {}).get("source_identity_audit")
        == "RA2021_SOURCE_IDENTITY_AUDIT.json",
        "RA2021 source-identity audit pointer missing",
    )
    checks.check(
        summary_by_suite.get("ra2021_absolute_coordinate", {}).get("source_output_mapping_verified") is True,
        "RA2021 output mapping should be source-verified",
    )
    checks.check(
        summary_by_suite.get("ra2021_absolute_coordinate", {}).get("source_time_grid_policy_extracted") is True,
        "RA2021 time-grid policy should be extracted",
    )
    checks.check(
        summary_by_suite.get("ra2021_absolute_coordinate", {}).get("active_flagged_rows") == 0,
        "RA2021 active row count should be zero after Route B demotion",
    )
    checks.check(
        summary_by_suite.get("ra2021_absolute_coordinate", {}).get("demoted_flagged_rows") == 5,
        "RA2021 demoted row count changed",
    )
    checks.check(
        summary_by_suite.get("ra2021_absolute_coordinate", {}).get("demoted_by")
        == "EXTERNAL_SUITE_DEMOTION_LEDGER.json",
        "RA2021 demotion pointer missing",
    )
    checks.check(
        summary_by_suite.get("hi2022_half_implicit", {}).get("bounded_T0p1_rows") == 24,
        "HI2022 bounded row count changed",
    )
    checks.check(
        summary_by_suite.get("hi2022_half_implicit", {}).get("active_flagged_rows") == 0,
        "HI2022 active row count should be zero after demotion",
    )
    checks.check(
        summary_by_suite.get("hi2022_half_implicit", {}).get("demoted_flagged_rows") == 3,
        "HI2022 demoted row count changed",
    )
    checks.check(
        summary_by_suite.get("hi2022_half_implicit", {}).get("full_T8_policy_completed") is False,
        "HI2022 full T=8 policy unexpectedly closed",
    )
    checks.check(
        summary_by_suite.get("tfe2026_original_pendulum", {}).get("source_policy_rows_completed") == 0,
        "TFE source-policy row count changed",
    )
    checks.check(
        summary_by_suite.get("tfe2026_original_pendulum", {}).get("runner_implemented") is False,
        "TFE runner unexpectedly implemented",
    )
    checks.check(
        summary_by_suite.get("tfe2026_original_pendulum", {}).get("candidate_full_T10_probe_implemented") is True,
        "TFE full T=10 candidate probe not carried into B2 manifest",
    )
    checks.check(
        summary_by_suite.get("tfe2026_original_pendulum", {}).get("candidate_full_T10_probe_finite_rows") == 4,
        "TFE full T=10 candidate probe finite row count changed",
    )
    checks.check(
        summary_by_suite.get("tfe2026_original_pendulum", {}).get("candidate_full_T10_probe_residual_ok_rows") == 4,
        "TFE full T=10 candidate probe residual row count changed",
    )
    checks.check(
        summary_by_suite.get("tfe2026_original_pendulum", {}).get("candidate_full_T10_probe_source_policy_rows") == 0,
        "TFE full T=10 candidate probe overcloses source-policy rows",
    )
    checks.check(
        summary_by_suite.get("tfe2026_original_pendulum", {}).get("active_flagged_rows") == 0,
        "TFE active row count should be zero after Route B demotion",
    )
    checks.check(
        summary_by_suite.get("tfe2026_original_pendulum", {}).get("demoted_flagged_rows") == 4,
        "TFE demoted row count changed",
    )
    checks.check(
        summary_by_suite.get("tfe2026_original_pendulum", {}).get("demoted_by")
        == "EXTERNAL_SUITE_DEMOTION_LEDGER.json",
        "TFE demotion pointer missing",
    )
    checks.check(
        summary_by_suite.get("vp2024_velocity_partitioning", {}).get("demoted_source_policy_rows") == 4,
        "VP2024 demoted source-policy row count changed",
    )
    checks.check(
        summary_by_suite.get("vp2024_velocity_partitioning", {}).get("full_source_policy_rows") == 4,
        "VP2024 full source-policy row count changed",
    )
    checks.check(
        summary_by_suite.get("vp2024_velocity_partitioning", {}).get("self_reproduction_attempted_rows") == 4
        and summary_by_suite.get("vp2024_velocity_partitioning", {}).get("unable_to_reproduce_rows") == 4,
        "VP2024 attempted/unable source-policy row count changed",
    )
    checks.check(
        summary_by_suite.get("vp2024_velocity_partitioning", {}).get("final_nonpublic_code_disposition")
        == "unable_to_reproduce_not_promoted",
        "VP2024 final nonpublic-code disposition changed",
    )
    execution = manifest.get("execution_policy", {})
    checks.check(execution.get("default_1e_4_required") is False, "manifest requires default 1e-4")
    checks.check(execution.get("heavy_numerical_run_invoked") is False, "manifest invoked heavy run")
    checks.check(execution.get("run_v047_invoked") is False, "manifest invoked run_v047")
    checks.check(execution.get("v048_runner_invoked") is False, "manifest invoked v048 runner")
    checks.check(
        execution.get("parallel_ready_shards_without_default_1e_4") == 20,
        "parallel-ready shard count changed",
    )

    closure_plan = manifest.get("closure_execution_plan", {})
    lanes = {item.get("suite_id"): item for item in closure_plan.get("suite_lanes", [])}
    checks.check(
        closure_plan.get("schema") == "b2-source-policy-closure-execution-plan-v1",
        "closure execution plan schema missing",
    )
    checks.check(closure_plan.get("read_only_plan") is True, "closure plan must be read-only")
    checks.check(closure_plan.get("default_1e_4_required") is False, "closure plan requires default 1e-4")
    checks.check(
        closure_plan.get("source_policy_1e_4_requires_explicit_flag") is True,
        "closure plan lost explicit 1e-4 opt-in guard",
    )
    checks.check(closure_plan.get("heavy_numerical_run_invoked") is False, "closure plan invoked heavy run")
    checks.check(closure_plan.get("run_v047_invoked") is False, "closure plan invoked run_v047")
    checks.check(closure_plan.get("v048_runner_invoked") is False, "closure plan invoked v048 runner")
    checks.check(
        closure_plan.get("all_active_suites_ready_to_launch") is True,
        "closure plan should have no active launch blockers after Route B demotion",
    )
    checks.check(
        closure_plan.get("external_superiority_claim_allowed_after_plan_only") is False,
        "closure plan overclaims external superiority",
    )
    checks.check(
        closure_plan.get("same_test_acceptance_contract_version")
        == "same-test-source-policy-contract-v1",
        "closure plan same-test contract version changed",
    )
    checks.check(
        closure_plan.get("same_test_contract_closes_rows") is False,
        "same-test contract incorrectly closes source-policy rows",
    )
    checks.check(
        closure_plan.get("parallel_ready_shards_without_default_1e_4") == 20,
        "closure plan parallel shard count changed",
    )
    checks.check(closure_plan.get("active_suite_lane_count") == 0, "closure plan lane count changed")
    checks.check(lanes == {}, "closure plan active lanes changed")

    inactive_lanes = {item.get("suite_id"): item for item in closure_plan.get("route_a_inactive_reference_lanes", [])}
    checks.check(
        set(inactive_lanes) == {"ra2021_absolute_coordinate", "tfe2026_original_pendulum"},
        "Route A inactive reference lanes changed",
    )
    ra_lane = inactive_lanes.get("ra2021_absolute_coordinate", {})
    checks.check(ra_lane.get("ready_to_launch") is True, "RA2021 lane should remain launch-ready")
    checks.check(
        ra_lane.get("source_policy_1e_4_opt_in_required") is True,
        "RA2021 lane lost explicit 1e-4 guard",
    )
    checks.check(ra_lane.get("completed_public_order_groups") == 12, "RA2021 completed order groups changed")
    checks.check(ra_lane.get("completed_public_timing_rows") == 12, "RA2021 completed timing rows changed")
    checks.check(ra_lane.get("source_output_mapping_verified") is True, "RA2021 lane lost output mapping audit")
    checks.check(
        ra_lane.get("source_time_grid_policy_extracted") is True,
        "RA2021 lane lost time-grid source audit",
    )
    checks.check(
        "resolve_position_aligned_velocity_output_mapping" not in ra_lane.get("remaining_blockers", []),
        "RA2021 lane still treats output mapping as unresolved",
    )
    checks.check(ra_lane.get("plan_only_closes_b2") is False, "RA2021 plan-only cannot close B2")
    checks.check(
        any("--full-ra2021-order --allow-source-policy-1e-4" in command for command in ra_lane.get("representative_commands", [])),
        "RA2021 source-policy rerun command missing",
    )
    ra_contract = ra_lane.get("same_test_acceptance_contract", {})
    checks.check(
        ra_contract.get("contract_id") == "ra2021-source-policy-dynamic-order-work-contract",
        "RA2021 same-test contract id changed",
    )
    checks.check(
        set(ra_contract.get("cases", []))
        == {"single_pendulum", "double_pendulum", "four_link", "slider_crank"},
        "RA2021 same-test case set changed",
    )
    checks.check(
        ra_contract.get("required_step_policy", {}).get("single_pendulum")
        == [1.0e-2, 1.0e-3, 1.0e-4],
        "RA2021 single-pendulum h contract changed",
    )
    checks.check(
        ra_contract.get("required_step_policy", {}).get("double_pendulum")
        == [1.0e-2, 2.0e-3, 1.0e-3],
        "RA2021 double-pendulum h contract changed",
    )
    checks.check(
        "wall_time_sec" in ra_contract.get("required_work_metrics", [])
        and "total_newton_iterations" in ra_contract.get("required_work_metrics", []),
        "RA2021 same-test work metrics missing",
    )
    checks.check(
        ra_contract.get("accepted_rows_closed_now") == 0,
        "RA2021 same-test contract overcloses rows",
    )
    checks.check(ra_contract.get("plan_only_closes_b2") is False, "RA2021 same-test plan-only cannot close B2")

    demoted_lanes = {item.get("suite_id"): item for item in closure_plan.get("demoted_suite_lanes", [])}
    ra_demoted_lane = demoted_lanes.get("ra2021_absolute_coordinate", {})
    checks.check(
        ra_demoted_lane.get("status") == "route_b_demoted_keep_public_baseline_and_common_reference_diagnostics",
        "RA2021 demoted lane status changed",
    )
    checks.check(
        ra_demoted_lane.get("plan_only_closes_b2_subrequirement") is True,
        "RA2021 demotion should close its B2 subrequirement",
    )
    hi_lane = demoted_lanes.get("hi2022_half_implicit", {})
    checks.check(
        hi_lane.get("status") == "demoted_after_incomplete_full_T8_source_policy_evidence",
        "HI2022 demoted lane status changed",
    )
    checks.check(hi_lane.get("source_policy_t_end") == 8.0, "HI2022 source-policy horizon changed")
    checks.check(
        hi_lane.get("plan_only_closes_b2_subrequirement") is True,
        "HI2022 demotion should close its B2 subrequirement",
    )

    tfe_lane = inactive_lanes.get("tfe2026_original_pendulum", {})
    checks.check(tfe_lane.get("ready_to_launch") is False, "TFE lane should not be launch-ready")
    checks.check(
        tfe_lane.get("status") == "nonpublic_code_attempted_not_reproducible_not_launch_ready",
        "TFE lane status changed",
    )
    checks.check(tfe_lane.get("public_code_available") is False, "TFE public-code boundary changed")
    checks.check(tfe_lane.get("self_reproduction_attempted") is True, "TFE self-reproduction marker missing")
    checks.check(
        tfe_lane.get("self_reproduction_attempt_status") == "attempted_not_reproducible_not_promoted",
        "TFE self-reproduction status changed",
    )
    checks.check(tfe_lane.get("source_reference_h") == 1e-4, "TFE source reference h changed")
    checks.check(tfe_lane.get("candidate_full_T10_probe_implemented") is True, "TFE lane lost full T=10 probe marker")
    checks.check(tfe_lane.get("candidate_full_T10_probe_finite_rows") == 4, "TFE lane finite probe rows changed")
    checks.check(tfe_lane.get("candidate_full_T10_probe_residual_ok_rows") == 4, "TFE lane residual probe rows changed")
    checks.check(tfe_lane.get("candidate_source_policy_rows_closed") == 0, "TFE lane overclosed source-policy rows")
    checks.check(tfe_lane.get("representative_commands") == [], "TFE lane should not expose runnable commands yet")
    checks.check(tfe_lane.get("plan_only_closes_b2") is False, "TFE plan-only cannot close B2")
    tfe_contract = tfe_lane.get("same_test_acceptance_contract", {})
    checks.check(
        tfe_contract.get("contract_id") == "tfe-source-pendulum-order-work-contract",
        "TFE same-test contract id changed",
    )
    checks.check(
        set(tfe_contract.get("cases", [])) == {"frictionless_pendulum", "frictional_revolute_joint_pendulum"},
        "TFE same-test cases changed",
    )
    checks.check(
        tfe_contract.get("required_reference_policy")
        == "h_ref=1e-4 full-horizon source reference, not the current h_ref=0.0125 coarse candidate probe",
        "TFE reference-policy contract changed",
    )
    checks.check(
        "TFE_m3" in tfe_contract.get("baseline_methods", [])
        and "Newmark_beta" in tfe_contract.get("baseline_methods", [])
        and "trapezoidal" in tfe_contract.get("baseline_methods", []),
        "TFE same-test method contract missing comparators",
    )
    checks.check(
        "source_reference_time_sec" in tfe_contract.get("required_work_metrics", []),
        "TFE source-reference work metric missing",
    )
    acceptance_tests = tfe_contract.get("acceptance_tests", [])
    checks.check(
        "no source-policy row is promoted from the paper-spec/proxy reconstruction"
        in acceptance_tests,
        "TFE no-promotion acceptance rule missing",
    )
    checks.check(
        "a future promotion would require a new source-code-equivalent public or author artifact"
        in acceptance_tests,
        "TFE future-artifact acceptance rule missing",
    )
    checks.check(
        tfe_contract.get("accepted_rows_closed_now") == 0,
        "TFE same-test contract overcloses rows",
    )
    checks.check(tfe_contract.get("plan_only_closes_b2") is False, "TFE same-test plan-only cannot close B2")
    tfe_demoted_lane = demoted_lanes.get("tfe2026_original_pendulum", {})
    checks.check(
        tfe_demoted_lane.get("status") == "attempted_not_reproducible_not_promoted_keep_formula_comparator_and_candidate_diagnostics",
        "TFE demoted lane status changed",
    )
    checks.check(tfe_demoted_lane.get("source_reference_h") == 1e-4, "TFE demoted lane source h changed")
    checks.check(
        tfe_demoted_lane.get("plan_only_closes_b2_subrequirement") is True,
        "TFE demotion should close its B2 subrequirement",
    )
    vp_demoted_lane = demoted_lanes.get("vp2024_velocity_partitioning", {})
    checks.check(
        vp_demoted_lane.get("status") == "attempted_not_reproducible_not_promoted_keep_proxy_diagnostic",
        "VP2024 demoted lane status changed",
    )
    checks.check(
        vp_demoted_lane.get("self_reproduction_attempted") is True
        and vp_demoted_lane.get("self_reproduction_attempt_status") == "unable_to_reproduce_not_promoted",
        "VP2024 demoted lane missing unable-to-reproduce status",
    )

    for token in [
        "Total flagged source-policy rows: `15`.",
        "Active flagged rows after Route B demotion: `0`.",
        "Demoted flagged rows after Route B demotion: `15`.",
        "Source-policy closed rows: `0`.",
        "External-superiority-ready rows: `0`.",
        "B2 closed by demotion: `['vp2024_code_resolution_or_demotion', 'hi2022_public_code_same_test_rows', 'ra2021_public_code_same_test_rows', 'original_tfe_pendulum_error_order_work_rows']`.",
        "B2 remaining requirements: `[]`.",
        "Route B B2/B4 claim-boundary synchronized: `True/True`.",
        "Route B B2/B4 closure ready pending gate sync: `False/False`.",
        "External superiority claim allowed: `False`.",
        "Default 1e-4/heavy/run_v047: `False/False/False`.",
        "Closure execution plan: `b2-source-policy-closure-execution-plan-v1`.",
        "Closure plan all active suites ready: `True`.",
        "Closure plan explicit 1e-4 opt-in required: `True`.",
        "Same-test acceptance contract: `same-test-source-policy-contract-v1`.",
        "Same-test contract closes rows now: `False`.",
        "TFE candidate full T=10 probe finite/residual/source-policy rows: `4/4/0`.",
        "TFE current disposition: `attempted_not_reproducible_not_promoted`; no public source-code-equivalent artifact was found.",
        "VP full source-policy rows unresolved/attempted/unable/closed: `4/4/4/0`; final disposition `unable_to_reproduce_not_promoted`.",
        "no source-policy row is promoted from the paper-spec/proxy reconstruction",
        "a future promotion would require a new source-code-equivalent public or author artifact",
        "## Closure Execution Plan",
        "## Same-Test Acceptance Contract",
        "T=3 source-policy target; public output variables and source-bound norm/reference policy",
        "historical T=10 source pendulum contract retained only as a future condition if a source-code-equivalent artifact appears",
        "Representative opt-in commands are stored in `B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.json`.",
        "The Route B demotions are claim-boundary decisions, not numerical wins.",
        "TFE/VP rows with no usable public source-code-equivalent artifact are attempted-not-reproducible and not promoted.",
        "RA2021 and HI2022 public-root diagnostics remain not-promoted until a source-policy promotion/execution closeout succeeds.",
    ]:
        checks.check(token in manifest_md, f"markdown missing token: {token}")
    for stale in [
        "prove_or_replace_candidate_planar_runner_with_source_policy_DAE_equivalence",
        "source-equivalent pendulum DAE runner is implemented for frictionless and frictional cases before any row promotion",
        "Brown-McPhee friction uses a source-code-equivalent law rather than the local v022 surrogate",
    ]:
        checks.check(stale not in manifest_md, f"markdown retained stale TFE route-A token: {stale}")

    if checks.errors:
        print("b2 source-policy remaining-work manifest validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("b2 source-policy remaining-work manifest validation: PASS")
    print("active_flagged_rows=0")
    print("demoted_flagged_rows=15")
    print("source_policy_closed_rows=0")
    print("b2_remaining_requirements=0")
    print("closure_execution_plan=b2-source-policy-closure-execution-plan-v1")
    print("all_active_suites_ready_to_launch=True")
    print("external_superiority_claim_allowed=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
