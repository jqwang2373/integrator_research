#!/usr/bin/env python3
"""Read-only validator for v048 cross-paper same-test benchmark harness."""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"


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


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader)


def as_float(value: object) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return float("nan")
    return out if math.isfinite(out) else float("nan")


def main() -> int:
    checks = Checks()
    try:
        summary = read_json(RESULTS / "summary_v048.json")
        plan_rows = read_csv(RESULTS / "cross_paper_run_plan.csv")
        workload_rows = read_csv(RESULTS / "same_test_workload_estimate.csv")
        order_rows = read_csv(RESULTS / "ra2021_order_rows.csv")
        order_work_summary_rows = read_csv(RESULTS / "ra2021_public_order_work_summary.csv")
        double_order_rows = read_csv(RESULTS / "ra2021_double_pendulum_order_rows.csv")
        double_coarse_rows = read_csv(RESULTS / "ra2021_double_pendulum_coarse_order_rows.csv")
        double_coarse_work_summary_rows = read_csv(
            RESULTS / "double_pendulum_coarse_same_window_work_precision_summary.csv"
        )
        single_coarse_public_rows = read_csv(RESULTS / "ra2021_single_pendulum_coarse_order_rows.csv")
        single_coarse_local_rows = read_csv(RESULTS / "gauss6_fullva_public_horizon_single_coarse_rows.csv")
        single_coarse_work_summary_rows = read_csv(
            RESULTS / "single_pendulum_coarse_same_window_work_precision_summary.csv"
        )
        single_coarse_work_summary_json = read_json(
            RESULTS / "single_pendulum_coarse_same_window_work_precision_summary.json"
        )
        single_coarse_work_summary_report = (
            RESULTS / "single_pendulum_coarse_same_window_work_precision_summary.md"
        ).read_text(encoding="utf-8")
        timing_rows = read_csv(RESULTS / "ra2021_public_timing_rows.csv")
        hi2022_workload_rows = read_csv(RESULTS / "hi2022_workload_estimate.csv")
        hi2022_rows = read_csv(RESULTS / "hi2022_halfimplicit_rows.csv")
        gauss6_rows = read_csv(RESULTS / "gauss6_fullva_external_rows.csv")
        gauss6_public_single_rows = read_csv(RESULTS / "gauss6_fullva_public_horizon_single_rows.csv")
        gauss6_public_double_coarse_rows = read_csv(
            RESULTS / "gauss6_fullva_public_horizon_double_coarse_rows.csv"
        )
        gauss6_closed_loop_rows = read_csv(RESULTS / "gauss6_fullva_closed_loop_external_rows.csv")
        gauss6_public_closed_loop_rows = read_csv(
            RESULTS / "gauss6_fullva_public_horizon_closed_loop_rows.csv"
        )
        gauss6_closed_loop_comparison_rows = read_csv(
            RESULTS / "gauss6_fullva_closed_loop_same_window_comparison_rows.csv"
        )
        same_window_work_summary_rows = read_csv(
            RESULTS / "gauss6_closed_loop_same_window_work_precision_summary.csv"
        )
        closed_loop_surrogate_rows = read_csv(RESULTS / "closed_loop_surrogate_dynamic_gate.csv")
        closed_loop_surrogate_summary = read_json(RESULTS / "closed_loop_surrogate_dynamic_gate.json")
        closed_loop_surrogate_report = (RESULTS / "closed_loop_surrogate_dynamic_gate.md").read_text(
            encoding="utf-8"
        )
        closed_loop_floor_audit_rows = read_csv(RESULTS / "closed_loop_dynamic_error_floor_audit.csv")
        closed_loop_floor_audit_summary = read_json(RESULTS / "closed_loop_dynamic_error_floor_audit.json")
        closed_loop_floor_audit_report = (RESULTS / "closed_loop_dynamic_error_floor_audit.md").read_text(
            encoding="utf-8"
        )
        closed_loop_coarse_probe_rows = read_csv(RESULTS / "closed_loop_coarse_dynamic_order_probe_rows.csv")
        closed_loop_coarse_probe_work_rows = read_csv(
            RESULTS / "closed_loop_coarse_dynamic_order_probe_work_precision_summary.csv"
        )
        closed_loop_coarse_probe_summary = read_json(RESULTS / "closed_loop_coarse_dynamic_order_probe.json")
        closed_loop_coarse_probe_report = (RESULTS / "closed_loop_coarse_dynamic_order_probe.md").read_text(
            encoding="utf-8"
        )
        coarse_first_gate_rows = read_csv(RESULTS / "coarse_first_external_readiness_gate.csv")
        coarse_first_gate_summary = read_json(RESULTS / "coarse_first_external_readiness_gate.json")
        coarse_first_gate_report = (RESULTS / "coarse_first_external_readiness_gate.md").read_text(
            encoding="utf-8"
        )
        stage_residual_audit_rows = read_csv(RESULTS / "closed_loop_true_dynamic_stage_residual_audit.csv")
        stage_residual_audit_summary = read_json(RESULTS / "closed_loop_true_dynamic_stage_residual_audit.json")
        stage_residual_audit_report = (
            RESULTS / "closed_loop_true_dynamic_stage_residual_audit.md"
        ).read_text(encoding="utf-8")
        one_step_smoke_rows = read_csv(RESULTS / "closed_loop_true_dynamic_one_step_smoke.csv")
        one_step_smoke_summary = read_json(RESULTS / "closed_loop_true_dynamic_one_step_smoke.json")
        one_step_smoke_report = (RESULTS / "closed_loop_true_dynamic_one_step_smoke.md").read_text(
            encoding="utf-8"
        )
        newton_stage_smoke_rows = read_csv(RESULTS / "closed_loop_true_dynamic_newton_stage_smoke.csv")
        newton_stage_smoke_summary = read_json(RESULTS / "closed_loop_true_dynamic_newton_stage_smoke.json")
        newton_stage_smoke_report = (RESULTS / "closed_loop_true_dynamic_newton_stage_smoke.md").read_text(
            encoding="utf-8"
        )
        newton_coarse_order_rows = read_csv(RESULTS / "closed_loop_true_dynamic_newton_coarse_order_rows.csv")
        newton_coarse_order_summary = read_json(RESULTS / "closed_loop_true_dynamic_newton_coarse_order.json")
        newton_coarse_order_report = (RESULTS / "closed_loop_true_dynamic_newton_coarse_order.md").read_text(
            encoding="utf-8"
        )
        public_work_precision_rows = read_csv(
            RESULTS / "closed_loop_true_dynamic_public_work_precision_rows.csv"
        )
        public_work_precision_summary_rows = read_csv(
            RESULTS / "closed_loop_true_dynamic_public_work_precision_summary.csv"
        )
        public_work_precision_summary = read_json(
            RESULTS / "closed_loop_true_dynamic_public_work_precision.json"
        )
        public_work_precision_report = (
            RESULTS / "closed_loop_true_dynamic_public_work_precision.md"
        ).read_text(encoding="utf-8")
        strict_common_reference_rows = read_csv(
            RESULTS / "closed_loop_true_dynamic_strict_common_reference_rows.csv"
        )
        strict_common_reference_summary_rows = read_csv(
            RESULTS / "closed_loop_true_dynamic_strict_common_reference_summary.csv"
        )
        strict_common_reference_summary = read_json(
            RESULTS / "closed_loop_true_dynamic_strict_common_reference.json"
        )
        strict_common_reference_report = (
            RESULTS / "closed_loop_true_dynamic_strict_common_reference.md"
        ).read_text(encoding="utf-8")
        strict_common_reference_figure = RESULTS / "closed_loop_true_dynamic_strict_common_reference_work_precision.png"
        coarse_velocity_order_figure = RESULTS / "coarse_velocity_order_by_example.png"
        coarse_velocity_error_figure = RESULTS / "coarse_finest_velocity_error_by_example.png"
        vp_search_rows = read_csv(RESULTS / "velocity_partitioning_code_search.csv")
        vp_identity_rows = read_csv(RESULTS / "vp_method_identity_audit.csv")
        vp_identity_summary = read_json(RESULTS / "vp_method_identity_audit.json")
        vp_identity_report = (RESULTS / "vp_method_identity_audit.md").read_text(encoding="utf-8")
        tfe_m3_scope_rows = read_csv(RESULTS / "tfe_m3_scope_exclusion_audit.csv")
        tfe_m3_scope_summary = read_json(RESULTS / "tfe_m3_scope_exclusion_audit.json")
        tfe_m3_scope_report = (RESULTS / "tfe_m3_scope_exclusion_audit.md").read_text(encoding="utf-8")
        tfe_m3_four_link_smoke_rows = read_csv(RESULTS / "tfe_m3_four_link_common_reference_smoke.csv")
        baseline_coverage_rows = read_csv(RESULTS / "baseline_coverage_matrix.csv")
        baseline_coverage_summary = read_json(RESULTS / "baseline_coverage_matrix.json")
        baseline_coverage_report = (RESULTS / "baseline_coverage_matrix.md").read_text(encoding="utf-8")
        large_step_vp_rows = read_csv(RESULTS / "large_step_vp_local_order_summary.csv")
        large_step_vp_summary = read_json(RESULTS / "large_step_vp_local_order_summary.json")
        large_step_vp_report = (RESULTS / "large_step_vp_local_order_summary.md").read_text(encoding="utf-8")
        error_reference_policy_rows = read_csv(RESULTS / "error_reference_policy_audit.csv")
        error_reference_policy_summary = read_json(RESULTS / "error_reference_policy_audit.json")
        error_reference_policy_report = (RESULTS / "error_reference_policy_audit.md").read_text(encoding="utf-8")
        common_reference_rows = read_csv(RESULTS / "common_reference_error_summary.csv")
        common_reference_raw_rows = read_csv(RESULTS / "common_reference_error_raw_rows.csv")
        common_reference_summary = read_json(RESULTS / "common_reference_error_summary.json")
        common_reference_report = (RESULTS / "common_reference_error_summary.md").read_text(encoding="utf-8")
        apples_policy_rows = read_csv(RESULTS / "apples_to_apples_policy_audit.csv")
        apples_policy_summary = read_json(RESULTS / "apples_to_apples_policy_audit.json")
        apples_policy_report = (RESULTS / "apples_to_apples_policy_audit.md").read_text(encoding="utf-8")
        global_policy_rows = read_csv(RESULTS / "global_comparison_policy_audit.csv")
        global_policy_summary = read_json(RESULTS / "global_comparison_policy_audit.json")
        global_policy_report = (RESULTS / "global_comparison_policy_audit.md").read_text(encoding="utf-8")
        objective_closure_rows = read_csv(RESULTS / "objective_closure_audit.csv")
        objective_closure_summary = read_json(RESULTS / "objective_closure_audit.json")
        objective_closure_report = (RESULTS / "objective_closure_audit.md").read_text(encoding="utf-8")
        report = (RESULTS / "v048_report.md").read_text(encoding="utf-8")
    except Exception as exc:  # noqa: BLE001 - concise CLI failure.
        print(f"v048 validation: FAIL\n- {exc}")
        return 1

    checks.check(summary.get("schema") == "v048-cross-paper-benchmark-harness-v1", "summary schema changed")
    checks.check(summary.get("same_test_campaign_status") == "not_run", "same-test campaign must not be marked complete")
    checks.check(summary.get("external_superiority_claim") is False, "external superiority claim must remain false")
    checks.check(summary.get("gauss6_fullva_external_rows_completed") is False, "Gauss6 external rows unexpectedly marked complete")
    checks.check(
        summary.get("gauss6_fullva_external", {}).get("full_external_campaign_completed") is False,
        "Gauss6 full external campaign unexpectedly marked complete",
    )
    checks.check(summary.get("gauss6_fullva_external", {}).get("row_count", 0) >= 1, "no Gauss6 selected rows recorded")
    checks.check(
        summary.get("gauss6_fullva_public_horizon_single", {}).get("row_count", 0) >= 1,
        "no Gauss6 public-horizon single-pendulum rows recorded",
    )
    checks.check(
        summary.get("gauss6_fullva_public_horizon_double_coarse", {}).get("row_count", 0) >= 3,
        "no Gauss6 public-horizon double-pendulum coarse rows recorded",
    )
    checks.check(
        summary.get("gauss6_fullva_public_horizon_single", {}).get("full_external_campaign_completed") is False,
        "Gauss6 public-horizon single-pendulum tranche unexpectedly marked full campaign complete",
    )
    checks.check(
        summary.get("gauss6_fullva_closed_loop_external", {}).get("row_count", 0) >= 1,
        "no Gauss6 closed-loop selected rows recorded",
    )
    checks.check(
        summary.get("gauss6_fullva_public_horizon_closed_loop", {}).get("row_count", 0) >= 1,
        "no Gauss6 public-horizon closed-loop rows recorded",
    )
    checks.check(
        summary.get("gauss6_fullva_closed_loop_same_window_comparison", {}).get("row_count", 0) >= 1,
        "no Gauss6 closed-loop same-window comparison rows recorded",
    )
    checks.check(
        summary.get("gauss6_closed_loop_same_window_work_precision_summary", {}).get("row_count", 0) >= 1,
        "no Gauss6 closed-loop same-window work/precision summary rows recorded",
    )
    checks.check(
        summary.get("closed_loop_dynamic_error_floor_audit", {}).get("row_count", 0) == 2,
        "summary missing closed-loop dynamic error floor audit",
    )
    coarse_probe_summary = summary.get("closed_loop_coarse_dynamic_order_probe", {})
    checks.check(
        coarse_probe_summary.get("schema") == "closed-loop-coarse-dynamic-order-probe-v1",
        "summary missing closed-loop coarse dynamic-order probe",
    )
    checks.check(coarse_probe_summary.get("row_count") == 12, "coarse probe should record twelve raw rows")
    checks.check(coarse_probe_summary.get("ok_row_count") == 11, "coarse probe should record eleven ok rows")
    checks.check(coarse_probe_summary.get("failed_row_count") == 1, "coarse probe should record one failed row")
    checks.check(
        coarse_probe_summary.get("public_failed_row_count") == 1,
        "coarse probe should record one public failed row",
    )
    checks.check(
        coarse_probe_summary.get("local_velocity_evidence_rows") == 2,
        "coarse probe should preserve two local velocity-evidence rows",
    )
    checks.check(
        coarse_probe_summary.get("local_acceleration_evidence_rows") == 2,
        "coarse probe should preserve two local acceleration-evidence rows",
    )
    checks.check(
        coarse_probe_summary.get("local_position_floor_rows") == 2,
        "coarse probe should preserve two local position-floor rows",
    )
    checks.check(
        coarse_probe_summary.get("accepted_dynamic_order_count") == 0,
        "coarse probe must not accept dynamic order rows",
    )
    checks.check(
        coarse_probe_summary.get("external_superiority_claim") is False,
        "coarse probe must not claim external superiority",
    )
    checks.check(
        coarse_probe_summary.get("default_policy") == "coarse_first_no_default_1e-4",
        "coarse probe summary default policy changed",
    )
    checks.check(
        coarse_probe_summary.get("same_test_campaign_status") == "not_run",
        "coarse probe must keep same-test campaign status not_run",
    )
    checks.check(summary.get("case_inventory_rows", 0) >= 17, "case inventory row count too small")
    checks.check(
        summary.get("velocity_partitioning_code_status") == "not_resolved_in_local_sbel_or_public_metadata_tree",
        "velocity-partitioning status changed",
    )
    checks.check(
        summary.get("velocity_partitioning_code_search", {}).get("relevant_code_path_resolved") is False,
        "velocity-partitioning code path unexpectedly resolved",
    )
    checks.check(
        summary.get("velocity_partitioning_code_search", {}).get("method_identity_resolved") is True,
        "velocity-partitioning method identity should be resolved as an alias",
    )
    checks.check(
        summary.get("velocity_partitioning_code_search", {}).get("row_count", 0) >= 11,
        "velocity-partitioning code search summary too small",
    )
    checks.check(
        summary.get("velocity_partitioning_code_search", {}).get("public_web_search_status")
        == "no_distinct_repo_found",
        "velocity-partitioning public web search status missing",
    )
    checks.check(
        set(summary.get("velocity_partitioning_code_search", {}).get("searched_refs", []))
        >= {"origin/master", "origin/user/aaron/msd"},
        "velocity-partitioning searched refs incomplete",
    )
    checks.check(
        any(row.get("evidence_type") == "pdf_reference_check" for row in vp_search_rows),
        "velocity-partitioning search missing EasyChair PDF reference check row",
    )
    checks.check(
        any(row.get("evidence_type") == "public_web_search" for row in vp_search_rows),
        "velocity-partitioning search missing public web search row",
    )
    checks.check(
        any(row.get("evidence_type") == "metadata_abstract_check" for row in vp_search_rows),
        "velocity-partitioning search missing metadata abstract public-code-claim check",
    )
    checks.check(
        any(row.get("evidence_type") == "crossref_primary_metadata_check" for row in vp_search_rows),
        "velocity-partitioning search missing Crossref/ASME method-identity check",
    )
    checks.check(
        any(row.get("evidence_type") == "pdf_full_reference_extraction" for row in vp_search_rows),
        "velocity-partitioning search missing full EasyChair PDF reference extraction row",
    )
    checks.check(
        any("origin/user/aaron/msd" in row.get("search_scope", "") for row in vp_search_rows),
        "velocity-partitioning search missing origin/user/aaron/msd tree rows",
    )
    tfe_candidate_rows = [
        row for row in tfe_m3_four_link_smoke_rows if row.get("interpretation") == "candidate row"
    ]
    tfe_order_rows = [
        row for row in tfe_m3_four_link_smoke_rows if row.get("h") == "nan"
    ]
    checks.check(
        len(tfe_m3_four_link_smoke_rows) == 4,
        "TFE(m=3) four-link common-reference smoke should have three candidates plus one order row",
    )
    checks.check(
        {row.get("h") for row in tfe_candidate_rows}
        == {"1.0000000000000001e-01", "5.0000000000000003e-02", "2.5000000000000001e-02"},
        "TFE(m=3) four-link common-reference smoke h trio changed",
    )
    checks.check(len(tfe_order_rows) == 1, "TFE(m=3) four-link smoke missing order row")
    if tfe_order_rows:
        order_row = tfe_order_rows[0]
        checks.check(
            as_float(order_row.get("pos_order")) < 0.0
            and as_float(order_row.get("vel_order")) < 0.0
            and as_float(order_row.get("acc_order")) < 0.0,
            "TFE(m=3) four-link smoke should remain rejected with negative observed orders",
        )
        checks.check(
            "not accepted" in order_row.get("interpretation", ""),
            "TFE(m=3) four-link smoke must not be presented as accepted convergence evidence",
        )
    checks.check(
        baseline_coverage_summary.get("schema") == "baseline-coverage-matrix-v1",
        "baseline coverage matrix schema missing",
    )
    checks.check(
        baseline_coverage_summary.get("row_count") == 13,
        "baseline coverage matrix should track thirteen coarse methods",
    )
    checks.check(
        baseline_coverage_summary.get("accepted_same_grid_four_example_methods") == 11,
        "baseline coverage matrix accepted-method count changed",
    )
    checks.check(
        baseline_coverage_summary.get("source_unresolved_methods") == [],
        "baseline coverage matrix should have no remaining source-unresolved methods after VP alias audit",
    )
    checks.check(
        baseline_coverage_summary.get("alias_resolved_methods") == ["vp2024_lie_group_ode_partitioning"],
        "baseline coverage matrix should mark VP Lie-group ODE as an alias-resolved method",
    )
    checks.check(
        baseline_coverage_summary.get("implemented_or_alias_resolved_methods") == 12,
        "baseline coverage matrix should count 12 accepted-or-alias-resolved methods",
    )
    checks.check(
        baseline_coverage_summary.get("required_methods_resolved") is True
        and baseline_coverage_summary.get("required_methods_resolved_count") == 13,
        "baseline coverage matrix should resolve all required method rows",
    )
    checks.check(
        baseline_coverage_summary.get("scope_excluded_methods") == ["tfe2026_TFE_m3_GL"],
        "baseline coverage matrix should mark TFE(m=3) as scope-excluded",
    )
    checks.check(
        baseline_coverage_summary.get("tfe_m3_scope_exclusion_source_backed") is True,
        "baseline coverage matrix should include source-backed TFE(m=3) exclusion",
    )
    checks.check(
        baseline_coverage_summary.get("vp_method_identity_alias_resolved") is True,
        "baseline coverage matrix should include the VP method-identity audit result",
    )
    checks.check(
        baseline_coverage_summary.get("rejected_partial_methods") == [],
        "baseline coverage matrix should have no remaining rejected partial methods after scope audit",
    )
    checks.check(
        baseline_coverage_summary.get("direct_error_vs_local_comparable_rows") == 40,
        "baseline coverage matrix should include common-reference direct-error rows",
    )
    checks.check(
        baseline_coverage_summary.get("common_reference_local_velocity_order_wins") == 40,
        "baseline coverage matrix should record common-reference local order wins",
    )
    checks.check(
        baseline_coverage_summary.get("common_reference_local_finest_velocity_error_wins") == 40,
        "baseline coverage matrix should record common-reference local finest-error wins",
    )
    baseline_by_method = {row.get("method"): row for row in baseline_coverage_rows}
    checks.check(
        baseline_by_method.get("local_Gauss6_FullVA", {}).get("implementation_status")
        == "accepted_same_grid_four_examples",
        "baseline coverage matrix should mark local method accepted on four examples",
    )
    checks.check(
        baseline_by_method.get("vp2024_coordinate_partitioning_rA", {}).get("implementation_status")
        == "accepted_same_grid_four_examples",
        "baseline coverage matrix should mark VP coordinate-partitioning wrapper accepted on four examples",
    )
    checks.check(
        baseline_by_method.get("vp2024_lie_group_ode_partitioning", {}).get("implementation_status")
        == "alias_resolved_to_vp2024_coordinate_partitioning_rA",
        "baseline coverage matrix should mark VP Lie-group ODE as an alias of the implemented wrapper",
    )
    checks.check(
        baseline_by_method.get("tfe2026_TFE_m3_GL", {}).get("implementation_status")
        == "scope_excluded_after_rejected_four_link",
        "baseline coverage matrix should mark TFE(m=3) as source-backed scope-excluded",
    )
    checks.check(
        "VP Lie-group ODE label is resolved as an alias" in baseline_coverage_report,
        "baseline coverage matrix report missing claim boundary",
    )
    checks.check(
        "TFE(m=3) four-link is a source-backed excluded stress row" in baseline_coverage_report,
        "baseline coverage matrix report missing TFE(m=3) scope boundary",
    )
    checks.check(
        len(vp_identity_rows) == 3
        and vp_identity_summary.get("schema") == "vp-method-identity-audit-v1"
        and vp_identity_summary.get("alias_resolved") is True
        and vp_identity_summary.get("distinct_unresolved_vp_method_remaining") is False,
        "VP method identity audit should resolve the duplicate VP label",
    )
    checks.check(
        "vp2024_coordinate_partitioning_rA" in vp_identity_report,
        "VP method identity report should identify the implemented wrapper",
    )
    checks.check(
        len(tfe_m3_scope_rows) == 4
        and tfe_m3_scope_summary.get("schema") == "tfe-m3-scope-exclusion-audit-v1"
        and tfe_m3_scope_summary.get("source_backed_exclusion") is True
        and tfe_m3_scope_summary.get("required_accepted_matrix_excludes_method") is True
        and tfe_m3_scope_summary.get("paper_four_link_claim_found") is False,
        "TFE(m=3) scope exclusion audit should be source-backed",
    )
    checks.check(
        "single revolute-pendulum" in tfe_m3_scope_report,
        "TFE(m=3) scope exclusion report should mention paper numerical scope",
    )
    checks.check(
        large_step_vp_summary.get("schema") == "large-step-vp-local-order-audit-v1",
        "large-step VP/local order audit schema missing",
    )
    checks.check(
        large_step_vp_summary.get("step_sizes") == [0.15, 0.075, 0.0375],
        "large-step VP/local order audit should use the larger h trio",
    )
    checks.check(
        large_step_vp_summary.get("reference_h") == 0.01875,
        "large-step VP/local order audit reference h changed",
    )
    checks.check(
        large_step_vp_summary.get("comparable_examples") == 4,
        "large-step VP/local order audit should compare all four examples",
    )
    checks.check(
        large_step_vp_summary.get("local_velocity_order_wins") == 4,
        "large-step VP/local order audit should preserve four local velocity-order wins",
    )
    checks.check(
        large_step_vp_summary.get("local_finest_velocity_error_wins") == 1,
        "large-step VP/local order audit should preserve the observed finest-error boundary",
    )
    checks.check(
        len(large_step_vp_rows) == 8,
        "large-step VP/local order audit summary should have local and VP rows for four examples",
    )
    checks.check(
        "Local finest-velocity-error wins: `1/4`" in large_step_vp_report,
        "large-step VP/local order report must state the finest-error boundary",
    )
    checks.check(
        error_reference_policy_summary.get("schema") == "error-reference-policy-audit-v1",
        "error reference-policy audit schema missing",
    )
    checks.check(
        error_reference_policy_summary.get("observed_order_comparable_rows") == 43,
        "error reference-policy audit should preserve 43 observed-order comparison rows",
    )
    checks.check(
        error_reference_policy_summary.get("mixed_policy_direct_error_vs_local_comparable_rows") == 0,
        "main mixed-reference matrix should still have zero direct-error rows",
    )
    checks.check(
        error_reference_policy_summary.get("direct_error_vs_local_comparable_rows") == 40,
        "error reference-policy audit should include common-reference direct-error rows",
    )
    checks.check(
        error_reference_policy_summary.get("common_reference_local_velocity_order_wins") == 40,
        "error reference-policy audit should record common-reference local order wins",
    )
    checks.check(
        error_reference_policy_summary.get("common_reference_local_finest_velocity_error_wins") == 40,
        "error reference-policy audit should record common-reference local finest-error wins",
    )
    checks.check(
        error_reference_policy_summary.get("large_step_local_velocity_order_wins_vs_vp") == 4,
        "error reference-policy audit should preserve large-step VP order result",
    )
    checks.check(
        error_reference_policy_summary.get("large_step_local_reported_finest_velocity_error_wins_vs_vp") == 1,
        "error reference-policy audit should preserve reported finest-error boundary",
    )
    checks.check(
        len(error_reference_policy_rows) >= 96,
        "error reference-policy audit should include main, large-step, and common-reference rows",
    )
    checks.check(
        "Common-reference local finest-velocity-error wins: `40/40`" in error_reference_policy_report,
        "error reference-policy audit report missing common-reference error wins",
    )
    checks.check(
        common_reference_summary.get("schema") == "common-reference-error-audit-v1",
        "common-reference error audit schema missing",
    )
    checks.check(
        common_reference_summary.get("step_sizes") == [0.1, 0.05, 0.025],
        "common-reference error audit should use the coarse h trio",
    )
    checks.check(
        common_reference_summary.get("reference_h") == 0.0125,
        "common-reference error audit reference h changed",
    )
    checks.check(
        common_reference_summary.get("run_method_count") == 11,
        "common-reference error audit should cover the 11 accepted runnable methods",
    )
    checks.check(
        common_reference_summary.get("raw_row_count") == 132,
        "common-reference error audit should have 132 raw rows",
    )
    checks.check(
        common_reference_summary.get("summary_row_count") == 44,
        "common-reference error audit should have 44 summary rows",
    )
    checks.check(
        len(common_reference_raw_rows) == 132 and len(common_reference_rows) == 44,
        "common-reference error audit row counts changed",
    )
    checks.check(
        common_reference_summary.get("local_velocity_order_wins") == 40
        and common_reference_summary.get("local_velocity_order_comparisons") == 40,
        "common-reference error audit should preserve 40/40 local velocity-order wins",
    )
    checks.check(
        common_reference_summary.get("local_finest_velocity_error_wins") == 40
        and common_reference_summary.get("local_finest_velocity_error_comparisons") == 40,
        "common-reference error audit should preserve 40/40 local velocity-error wins",
    )
    checks.check(
        common_reference_summary.get("original_paper_velocity_error_wins") == 16
        and common_reference_summary.get("original_paper_velocity_error_comparisons") == 16,
        "common-reference error audit should preserve 16/16 original-paper error wins",
    )
    checks.check(
        common_reference_summary.get("kissel_negrut_velocity_error_wins") == 24
        and common_reference_summary.get("kissel_negrut_velocity_error_comparisons") == 24,
        "common-reference error audit should preserve 24/24 Kissel/Negrut-family error wins",
    )
    checks.check(
        common_reference_summary.get("apples_to_apples_coarse_claim") is True,
        "common-reference error audit must explicitly be an apples-to-apples coarse claim",
    )
    checks.check(
        common_reference_summary.get("source_policy_reproduction") is False,
        "common-reference error audit must not be labeled source-policy reproduction",
    )
    checks.check(
        common_reference_summary.get("public_code_fixed_grid_replay") is True,
        "common-reference error audit must record fixed-grid replay for public-code rows",
    )
    checks.check(
        "Direct all-row error superiority claim: `True`" in common_reference_report,
        "common-reference error audit report missing direct-error claim",
    )
    checks.check(
        "Apples-to-apples coarse claim: `True`" in common_reference_report,
        "common-reference error audit report missing apples-to-apples claim boundary",
    )
    checks.check(
        "Source-policy reproduction: `False`" in common_reference_report,
        "common-reference error audit report missing source-policy boundary",
    )
    checks.check(
        "Public-code fixed-grid replay: `True`" in common_reference_report,
        "common-reference error audit report missing fixed-grid replay boundary",
    )
    checks.check(
        apples_policy_summary.get("schema") == "apples-to-apples-policy-audit-v1",
        "apples-to-apples policy audit schema missing",
    )
    checks.check(
        apples_policy_summary.get("row_count") == 44
        and apples_policy_summary.get("paper_safe_row_count") == 44,
        "apples-to-apples policy audit must pass all 44 rows",
    )
    checks.check(
        apples_policy_summary.get("nonlocal_paper_safe_comparison_count") == 40,
        "apples-to-apples policy audit must preserve 40 nonlocal comparison rows",
    )
    checks.check(
        apples_policy_summary.get("public_source_time_grid_caveat_detected") is True,
        "apples-to-apples policy audit must detect the public source time-grid caveat",
    )
    checks.check(
        apples_policy_summary.get("fixed_grid_wrapper_present") is True,
        "apples-to-apples policy audit must require the fixed-grid wrapper",
    )
    checks.check(
        apples_policy_summary.get("source_policy_reproduction") is False,
        "apples-to-apples policy audit must not claim source-policy reproduction",
    )
    checks.check(
        len(apples_policy_rows) == 44
        and {row.get("paper_safe_coarse_apples_to_apples") for row in apples_policy_rows} == {"true"},
        "apples-to-apples policy CSV must mark every row paper-safe",
    )
    checks.check(
        {row.get("source_policy_reproduction") for row in apples_policy_rows} == {"false"},
        "apples-to-apples policy CSV must keep source-policy reproduction false for every row",
    )
    checks.check(
        "Paper-safe rows: `44/44`" in apples_policy_report,
        "apples-to-apples policy report missing 44/44 row claim",
    )
    checks.check(
        "Fixed-grid wrapper present: `True`" in apples_policy_report,
        "apples-to-apples policy report missing fixed-grid wrapper evidence",
    )
    checks.check(
        global_policy_summary.get("schema") == "global-comparison-policy-audit-v1",
        "global comparison-policy audit schema missing",
    )
    checks.check(
        global_policy_summary.get("reasonable_apples_to_apples_claims") is True,
        "global comparison-policy audit must pass before v048 claims are accepted",
    )
    checks.check(
        global_policy_summary.get("passed_count") == global_policy_summary.get("row_count") == 14,
        "global comparison-policy audit should pass all fourteen requirements",
    )
    checks.check(
        len(global_policy_rows) == 14 and {row.get("status") for row in global_policy_rows} == {"pass"},
        "global comparison-policy CSV should contain fourteen passing rows",
    )
    checks.check(
        global_policy_summary.get("mixed_policy_direct_error_vs_local_comparable_rows") == 0,
        "global comparison-policy audit must block mixed-policy direct-error comparisons",
    )
    checks.check(
        global_policy_summary.get("direct_error_vs_local_comparable_rows") == 40,
        "global comparison-policy audit must preserve 40 allowed direct-error rows",
    )
    checks.check(
        global_policy_summary.get("direct_error_rows_allowed_for_paper") == 0
        and global_policy_summary.get("paper_direct_error_superiority_claim_allowed") is False,
        "global comparison-policy audit must block paper-level direct-error superiority",
    )
    checks.check(
        global_policy_summary.get("source_policy_reproduction") is False
        and global_policy_summary.get("public_code_fixed_grid_replay") is True,
        "global comparison-policy audit must record fixed-grid non-source-policy boundary",
    )
    checks.check(
        global_policy_summary.get("external_superiority_claim") is False,
        "global comparison-policy audit must not claim full external superiority",
    )
    checks.check(
        "Reasonable apples-to-apples claims: `True`" in global_policy_report,
        "global comparison-policy report missing pass statement",
    )
    checks.check(
        "Mixed-policy direct error rows allowed: `0`" in global_policy_report,
        "global comparison-policy report missing mixed-policy boundary",
    )
    checks.check(
        objective_closure_summary.get("schema") == "objective-closure-audit-v1",
        "objective closure audit schema missing",
    )
    checks.check(
        objective_closure_summary.get("objective_complete") is True,
        "objective closure audit should mark the active comparison objective complete",
    )
    checks.check(
        objective_closure_summary.get("passed_count") == objective_closure_summary.get("row_count") == 13,
        "objective closure audit should pass all thirteen requirements",
    )
    checks.check(
        len(objective_closure_rows) == 13 and {row.get("status") for row in objective_closure_rows} == {"pass"},
        "objective closure CSV should contain thirteen passing rows",
    )
    checks.check(
        objective_closure_summary.get("examples") == ["single_pendulum", "double_pendulum", "four_link", "slider_crank"],
        "objective closure audit should cover the four requested examples",
    )
    checks.check(
        objective_closure_summary.get("step_sizes") == [0.1, 0.05, 0.025],
        "objective closure audit should use the requested coarse h trio",
    )
    checks.check(
        objective_closure_summary.get("reference_h") == 0.0125,
        "objective closure audit should use reference h=0.0125",
    )
    checks.check(
        objective_closure_summary.get("required_methods_resolved") is True,
        "objective closure audit should resolve all required method labels",
    )
    checks.check(
        objective_closure_summary.get("scope_excluded_methods") == ["tfe2026_TFE_m3_GL"],
        "objective closure audit should preserve the source-backed TFE(m=3) scope exclusion",
    )
    checks.check(
        objective_closure_summary.get("alias_resolved_methods") == ["vp2024_lie_group_ode_partitioning"],
        "objective closure audit should preserve the VP alias resolution",
    )
    checks.check(
        objective_closure_summary.get("apples_to_apples_policy_safe_rows")
        == objective_closure_summary.get("apples_to_apples_policy_row_count")
        == 44,
        "objective closure audit should preserve 44/44 apples-to-apples policy rows",
    )
    checks.check(
        objective_closure_summary.get("apples_to_apples_nonlocal_comparisons") == 40,
        "objective closure audit should preserve 40 apples-to-apples nonlocal comparisons",
    )
    checks.check(
        objective_closure_summary.get("global_comparison_policy_passed") is True
        and objective_closure_summary.get("global_comparison_policy_passed_count")
        == objective_closure_summary.get("global_comparison_policy_row_count")
        == 13,
        "objective closure audit should preserve the global comparison-policy audit result",
    )
    checks.check(
        objective_closure_summary.get("mixed_policy_direct_error_vs_local_comparable_rows") == 0,
        "objective closure audit should record zero mixed-policy direct-error rows",
    )
    checks.check(
        objective_closure_summary.get("source_policy_reproduction") is False,
        "objective closure audit must record that this is not source-policy reproduction",
    )
    checks.check(
        objective_closure_summary.get("public_code_fixed_grid_replay") is True,
        "objective closure audit must record fixed-grid replay for public-code baselines",
    )
    checks.check(
        objective_closure_summary.get("local_velocity_order_wins")
        == objective_closure_summary.get("local_velocity_order_comparisons")
        == 40,
        "objective closure audit should preserve 40/40 velocity-order wins",
    )
    checks.check(
        objective_closure_summary.get("local_finest_velocity_error_wins")
        == objective_closure_summary.get("local_finest_velocity_error_comparisons")
        == 40,
        "objective closure audit should preserve 40/40 velocity-error wins",
    )
    checks.check(
        objective_closure_summary.get("original_paper_velocity_error_wins")
        == objective_closure_summary.get("original_paper_velocity_error_comparisons")
        == 16,
        "objective closure audit should preserve 16/16 original-paper error wins",
    )
    checks.check(
        objective_closure_summary.get("kissel_negrut_velocity_error_wins")
        == objective_closure_summary.get("kissel_negrut_velocity_error_comparisons")
        == 24,
        "objective closure audit should preserve 24/24 Kissel/Negrut-family error wins",
    )
    checks.check(
        set(objective_closure_summary.get("local_orders", {})) == {
            "single_pendulum",
            "double_pendulum",
            "four_link",
            "slider_crank",
        },
        "objective closure audit should include local orders for all four examples",
    )
    checks.check(
        "Objective complete: `True`" in objective_closure_report,
        "objective closure report should state objective completion",
    )
    checks.check(summary.get("ra2021_order", {}).get("row_count", 0) >= 1, "no 2021 order/smoke rows recorded")
    checks.check(
        summary.get("ra2021_public_order_work_summary", {}).get("row_count", 0) >= 1,
        "no 2021 public order/work summary rows recorded",
    )
    timing_summary = summary.get("ra2021_public_timing", {})
    double_order_summary = summary.get("ra2021_double_pendulum_order", {})
    double_coarse_summary = summary.get("ra2021_double_pendulum_coarse_order", {})
    single_coarse_public_summary = summary.get("ra2021_single_pendulum_coarse_order", {})
    single_coarse_local_summary = summary.get("gauss6_fullva_public_horizon_single_coarse", {})
    double_coarse_work_summary = summary.get(
        "double_pendulum_coarse_same_window_work_precision_summary",
        {},
    )
    single_coarse_work_summary = summary.get(
        "single_pendulum_coarse_same_window_work_precision_summary",
        {},
    )
    checks.check(
        double_order_summary.get("row_count", 0) >= 9,
        "2021 double-pendulum dynamic order rows should include all three form trios",
    )
    checks.check(
        double_order_summary.get("ok_row_count", 0) >= 9,
        "2021 double-pendulum dynamic order rows should have nine ok rows",
    )
    checks.check(
        double_order_summary.get("selected_step_trio_group_count") == 3,
        "2021 double-pendulum dynamic order should complete all three form groups",
    )
    checks.check(
        double_order_summary.get("full_ra2021_double_order_completed") is True,
        "2021 double-pendulum dynamic order should be marked complete for the selected policy",
    )
    checks.check(
        double_coarse_summary.get("row_count", 0) >= 9,
        "2021 double-pendulum coarse same-window rows should include all three form trios",
    )
    checks.check(
        double_coarse_summary.get("ok_row_count", 0) >= 6,
        "2021 double-pendulum coarse same-window rows should preserve the rA/reps ok rows",
    )
    checks.check(
        double_coarse_summary.get("selected_step_trio_group_count") == 2,
        "2021 double-pendulum coarse same-window should record two completed form groups",
    )
    checks.check(
        double_coarse_summary.get("full_external_campaign_completed") is False,
        "2021 double-pendulum coarse same-window unexpectedly marked full campaign complete",
    )
    checks.check(
        double_coarse_work_summary.get("row_count", 0) >= 3,
        "double-pendulum coarse work/precision summary should include Gauss6 plus public baselines",
    )
    checks.check(
        single_coarse_public_summary.get("row_count", 0) == 9,
        "2021 single-pendulum coarse same-window rows should include all three form trios",
    )
    checks.check(
        single_coarse_public_summary.get("ok_row_count", 0) == 9,
        "2021 single-pendulum coarse same-window rows should have nine ok rows",
    )
    checks.check(
        single_coarse_public_summary.get("selected_step_trio_group_count") == 3,
        "2021 single-pendulum coarse same-window should complete three form groups",
    )
    checks.check(
        single_coarse_public_summary.get("full_external_campaign_completed") is False,
        "2021 single-pendulum coarse same-window unexpectedly marked full campaign complete",
    )
    checks.check(
        single_coarse_local_summary.get("row_count", 0) == 3,
        "Gauss6 single-pendulum coarse rows should include three rows",
    )
    checks.check(
        single_coarse_local_summary.get("ok_row_count", 0) == 3,
        "Gauss6 single-pendulum coarse rows should have three ok rows",
    )
    checks.check(
        float(single_coarse_local_summary.get("position_observed_order", 0.0) or 0.0) > 5.0,
        "Gauss6 single-pendulum coarse position order should be above five",
    )
    checks.check(
        single_coarse_work_summary.get("row_count", 0) == 4,
        "single-pendulum coarse work/precision summary should include Gauss6 plus three public baselines",
    )
    checks.check(
        single_coarse_work_summary.get("default_policy") == "coarse_first_no_default_1e-4",
        "single-pendulum coarse summary default policy changed",
    )
    checks.check(
        single_coarse_work_summary.get("external_superiority_claim") is False,
        "single-pendulum coarse summary must not claim superiority",
    )
    checks.check(
        coarse_first_gate_summary.get("schema") == "coarse-first-external-readiness-gate-v1",
        "coarse-first readiness gate schema changed",
    )
    checks.check(
        coarse_first_gate_summary.get("default_policy") == "coarse_first_no_default_1e-4",
        "coarse-first readiness gate default policy changed",
    )
    checks.check(
        coarse_first_gate_summary.get("same_test_campaign_status") == "not_run",
        "coarse-first readiness gate must keep same-test status not_run",
    )
    checks.check(
        coarse_first_gate_summary.get("external_superiority_claim") is False,
        "coarse-first readiness gate must not claim superiority",
    )
    checks.check(
        coarse_first_gate_summary.get("coarse_same_window_ready_count") == 2,
        "coarse-first readiness gate should currently have two ready examples",
    )
    checks.check(
        coarse_first_gate_summary.get("single_coarse_same_window_available_count") == 1,
        "coarse-first readiness gate should record single coarse same-window availability",
    )
    checks.check(
        coarse_first_gate_summary.get("local_true_dynamic_order_available_count") == 2,
        "coarse-first readiness gate should record two local true-dynamic order rows",
    )
    checks.check(
        coarse_first_gate_summary.get("public_work_precision_available_count") == 2,
        "coarse-first readiness gate should record two public work/precision available rows",
    )
    checks.check(
        coarse_first_gate_summary.get("public_work_precision_missing_count") == 0,
        "coarse-first readiness gate should close public work/precision availability blockers",
    )
    checks.check(
        coarse_first_gate_summary.get("strict_common_reference_available_count") == 2,
        "coarse-first readiness gate should record two strict common-reference available rows",
    )
    checks.check(
        coarse_first_gate_summary.get("strict_common_reference_gap_count") == 0,
        "coarse-first readiness gate should close strict common-reference gaps",
    )
    checks.check(
        coarse_first_gate_summary.get("strict_common_reference_figure_available") is True,
        "coarse-first readiness gate should record strict common-reference figure availability",
    )
    checks.check(
        coarse_first_gate_summary.get("closed_loop_surrogate_available_count") == 0,
        "coarse-first readiness gate should no longer classify closed-loop rows as surrogate-only",
    )
    checks.check(
        coarse_first_gate_summary.get("closed_loop_floor_audit_available_count") == 2,
        "coarse-first readiness gate should record two closed-loop floor-audit rows",
    )
    checks.check(
        coarse_first_gate_summary.get("dynamic_order_missing_count") == 0,
        "coarse-first readiness gate should close local dynamic-order gaps",
    )
    checks.check(
        stage_residual_audit_summary.get("schema") == "closed-loop-true-dynamic-stage-residual-audit-v1",
        "stage residual audit schema changed",
    )
    checks.check(
        stage_residual_audit_summary.get("status") == "stage_residual_evaluator_verified_stepper_not_implemented",
        "stage residual audit status changed",
    )
    checks.check(stage_residual_audit_summary.get("row_count") == 6, "stage residual audit row count changed")
    checks.check(stage_residual_audit_summary.get("ok_row_count") == 6, "stage residual audit ok count changed")
    checks.check(stage_residual_audit_summary.get("max_stage_residual_inf", 1.0) < 1.0e-10, "stage residual audit residual too large")
    checks.check(
        stage_residual_audit_summary.get("stage_residual_evaluator_implemented") is True,
        "stage residual evaluator not recorded",
    )
    checks.check(
        stage_residual_audit_summary.get("trajectory_stepper_implemented") is False,
        "stage residual audit stepper overclaimed",
    )
    checks.check(
        stage_residual_audit_summary.get("accepted_dynamic_order_count") == 0,
        "stage residual audit dynamic order overclaimed",
    )
    checks.check(
        stage_residual_audit_summary.get("default_1e-4_required") is False,
        "stage residual audit default 1e-4 overclaimed",
    )
    checks.check(len(stage_residual_audit_rows) == 6, "stage residual audit CSV row count changed")
    checks.check({row.get("status") for row in stage_residual_audit_rows} == {"ok"}, "stage residual audit rows not ok")
    checks.check(
        {row.get("trajectory_stepper_executed") for row in stage_residual_audit_rows} == {"false"},
        "stage residual audit executed stepper",
    )
    checks.check(
        "must not be counted as a trajectory order row" in stage_residual_audit_report,
        "stage residual audit report lost no-order boundary",
    )
    checks.check(
        one_step_smoke_summary.get("schema") == "closed-loop-true-dynamic-one-step-smoke-v1",
        "one-step smoke schema changed",
    )
    checks.check(
        one_step_smoke_summary.get("status") == "one_step_smoke_passed_order_rows_not_run",
        "one-step smoke status changed",
    )
    checks.check(one_step_smoke_summary.get("row_count") == 2, "one-step smoke row count changed")
    checks.check(one_step_smoke_summary.get("ok_row_count") == 2, "one-step smoke ok count changed")
    checks.check(one_step_smoke_summary.get("max_stage_residual_inf", 1.0) < 1.0e-10, "one-step smoke residual too large")
    checks.check(one_step_smoke_summary.get("max_endpoint_pos_error_inf", 1.0) < 1.0e-4, "one-step smoke endpoint error too large")
    checks.check(
        one_step_smoke_summary.get("trajectory_stepper_executed") is True,
        "one-step smoke did not execute stepper",
    )
    checks.check(
        one_step_smoke_summary.get("convergence_sweep_run") is False,
        "one-step smoke ran convergence sweep",
    )
    checks.check(
        one_step_smoke_summary.get("accepted_dynamic_order_count") == 0,
        "one-step smoke dynamic order overclaimed",
    )
    checks.check(
        one_step_smoke_summary.get("default_1e-4_required") is False,
        "one-step smoke default 1e-4 overclaimed",
    )
    checks.check(len(one_step_smoke_rows) == 2, "one-step smoke CSV row count changed")
    checks.check({row.get("status") for row in one_step_smoke_rows} == {"ok"}, "one-step smoke rows not ok")
    checks.check(
        {row.get("trajectory_stepper_executed") for row in one_step_smoke_rows} == {"true"},
        "one-step smoke did not execute stepper",
    )
    checks.check(
        {row.get("accepted_dynamic_order") for row in one_step_smoke_rows} == {"false"},
        "one-step smoke accepted dynamic order",
    )
    checks.check(
        "must not be counted as order" in one_step_smoke_report,
        "one-step smoke report lost no-order boundary",
    )
    checks.check(
        newton_stage_smoke_summary.get("schema") == "closed-loop-true-dynamic-newton-stage-smoke-v1",
        "Newton stage smoke schema changed",
    )
    checks.check(
        newton_stage_smoke_summary.get("status") == "non_oracle_stage_newton_smoke_passed_order_rows_not_run",
        "Newton stage smoke status changed",
    )
    checks.check(newton_stage_smoke_summary.get("row_count") == 2, "Newton stage smoke row count changed")
    checks.check(newton_stage_smoke_summary.get("ok_row_count") == 2, "Newton stage smoke ok count changed")
    checks.check(
        newton_stage_smoke_summary.get("stage_oracle_used") is False,
        "Newton stage smoke used a stage oracle",
    )
    checks.check(
        newton_stage_smoke_summary.get("stage_predictor_policy") == "start_extrapolated_no_stage_oracle",
        "Newton stage smoke predictor policy changed",
    )
    checks.check(
        newton_stage_smoke_summary.get("max_initial_stage_residual_inf", 0.0) > 1.0e-8,
        "Newton stage smoke initial residual not diagnostic",
    )
    checks.check(
        newton_stage_smoke_summary.get("max_stage_residual_inf", 1.0) < 1.0e-8,
        "Newton stage smoke residual too large",
    )
    checks.check(
        newton_stage_smoke_summary.get("trajectory_stepper_executed") is True,
        "Newton stage smoke did not execute stepper",
    )
    checks.check(
        newton_stage_smoke_summary.get("convergence_sweep_run") is False,
        "Newton stage smoke ran convergence sweep",
    )
    checks.check(
        newton_stage_smoke_summary.get("accepted_dynamic_order_count") == 0,
        "Newton stage smoke dynamic order overclaimed",
    )
    checks.check(
        newton_stage_smoke_summary.get("default_1e-4_required") is False,
        "Newton stage smoke default 1e-4 overclaimed",
    )
    checks.check(len(newton_stage_smoke_rows) == 2, "Newton stage smoke CSV row count changed")
    checks.check({row.get("status") for row in newton_stage_smoke_rows} == {"ok"}, "Newton stage smoke rows not ok")
    checks.check(
        {row.get("stage_oracle_used") for row in newton_stage_smoke_rows} == {"false"},
        "Newton stage smoke CSV used a stage oracle",
    )
    checks.check(
        {row.get("accepted_dynamic_order") for row in newton_stage_smoke_rows} == {"false"},
        "Newton stage smoke accepted dynamic order",
    )
    checks.check(
        "No stage-time kinematic oracle is used" in newton_stage_smoke_report,
        "Newton stage smoke report lost no-stage-oracle boundary",
    )
    checks.check(
        "must not be counted as order" in newton_stage_smoke_report,
        "Newton stage smoke report lost no-order boundary",
    )
    checks.check(
        newton_coarse_order_summary.get("schema") == "closed-loop-true-dynamic-newton-coarse-order-v1",
        "Newton coarse order schema changed",
    )
    checks.check(
        newton_coarse_order_summary.get("status") == "coarse_true_dynamic_order_candidates_available_not_external_superiority",
        "Newton coarse order status changed",
    )
    checks.check(newton_coarse_order_summary.get("row_count") == 6, "Newton coarse order row count changed")
    checks.check(newton_coarse_order_summary.get("ok_row_count") == 6, "Newton coarse order ok count changed")
    checks.check(
        newton_coarse_order_summary.get("accepted_dynamic_order_count") == 2,
        "Newton coarse order should accept two local dynamic order candidates",
    )
    checks.check(
        newton_coarse_order_summary.get("stage_oracle_used") is False,
        "Newton coarse order used stage oracle",
    )
    checks.check(
        newton_coarse_order_summary.get("convergence_sweep_run") is True,
        "Newton coarse order did not record convergence sweep",
    )
    checks.check(
        newton_coarse_order_summary.get("default_1e-4_required") is False,
        "Newton coarse order default 1e-4 overclaimed",
    )
    checks.check(
        newton_coarse_order_summary.get("external_superiority_claim") is False,
        "Newton coarse order external superiority overclaimed",
    )
    for model, item in newton_coarse_order_summary.get("model_summaries", {}).items():
        checks.check(model in {"four_link", "slider_crank"}, f"unexpected Newton coarse model {model}")
        checks.check(item.get("accepted_dynamic_order_candidate") is True, f"{model} Newton coarse order not accepted")
        for key in ["pos_observed_order", "orientation_observed_order", "vel_observed_order", "omega_observed_order"]:
            checks.check(float(item.get(key, 0.0)) >= 4.5, f"{model} {key} below threshold")
    checks.check(len(newton_coarse_order_rows) == 6, "Newton coarse order CSV row count changed")
    checks.check({row.get("accepted_dynamic_order") for row in newton_coarse_order_rows} == {"true"}, "Newton coarse order CSV not accepted")
    checks.check("public-baseline work/precision comparison" in newton_coarse_order_report, "Newton coarse order report lost public-work boundary")
    checks.check("External superiority claim: `False`" in newton_coarse_order_report, "Newton coarse order report overclaimed superiority")
    checks.check(
        public_work_precision_summary.get("schema") == "closed-loop-true-dynamic-public-work-precision-v1",
        "public work/precision schema changed",
    )
    checks.check(
        public_work_precision_summary.get("status")
        == "same_window_public_work_precision_available_reference_caveat_not_external_superiority",
        "public work/precision status changed",
    )
    checks.check(
        public_work_precision_summary.get("default_policy") == "coarse_first_no_default_1e-4",
        "public work/precision default policy changed",
    )
    checks.check(public_work_precision_summary.get("row_count") == 24, "public work/precision raw row count changed")
    checks.check(public_work_precision_summary.get("ok_row_count") == 24, "public work/precision ok count changed")
    checks.check(
        public_work_precision_summary.get("public_raw_row_count") == 18,
        "public work/precision public raw row count changed",
    )
    checks.check(
        public_work_precision_summary.get("local_raw_row_count") == 6,
        "public work/precision local raw row count changed",
    )
    checks.check(
        public_work_precision_summary.get("summary_row_count") == 8,
        "public work/precision summary row count changed",
    )
    checks.check(
        public_work_precision_summary.get("public_work_precision_available_count") == 2,
        "public work/precision availability count changed",
    )
    checks.check(
        public_work_precision_summary.get("public_work_precision_missing_count") == 0,
        "public work/precision missing count should be zero",
    )
    checks.check(
        public_work_precision_summary.get("local_true_dynamic_order_available_count") == 2,
        "public work/precision local true-dynamic count changed",
    )
    checks.check(
        public_work_precision_summary.get("strict_common_reference_error_columns") is False,
        "public work/precision strict common-reference caveat changed",
    )
    checks.check(
        public_work_precision_summary.get("external_superiority_claim") is False,
        "public work/precision overclaimed external superiority",
    )
    checks.check(
        public_work_precision_summary.get("default_1e-4_required") is False,
        "public work/precision default 1e-4 overclaimed",
    )
    checks.check(len(public_work_precision_rows) == 24, "public work/precision CSV row count changed")
    checks.check(
        {row.get("model") for row in public_work_precision_rows} == {"four_link", "slider_crank"},
        "public work/precision model set changed",
    )
    checks.check(
        {float(row.get("h", "nan")) for row in public_work_precision_rows} == {0.1, 0.05, 0.025},
        "public work/precision step-size set changed",
    )
    checks.check(
        {row.get("status") for row in public_work_precision_rows} == {"ok"},
        "public work/precision CSV status changed",
    )
    checks.check(
        len(public_work_precision_summary_rows) == 8,
        "public work/precision summary CSV row count changed",
    )
    checks.check(
        "Strict common-reference error columns: `False`" in public_work_precision_report,
        "public work/precision report lost strict common-reference caveat",
    )
    checks.check(
        "External superiority claim: `False`" in public_work_precision_report,
        "public work/precision report overclaimed superiority",
    )
    checks.check(
        strict_common_reference_summary.get("schema") == "closed-loop-true-dynamic-strict-common-reference-v1",
        "strict common-reference schema changed",
    )
    checks.check(
        strict_common_reference_summary.get("status")
        == "strict_common_reference_error_columns_available_not_external_superiority",
        "strict common-reference status changed",
    )
    checks.check(
        strict_common_reference_summary.get("default_policy") == "coarse_first_no_default_1e-4",
        "strict common-reference default policy changed",
    )
    checks.check(strict_common_reference_summary.get("row_count") == 24, "strict common-reference raw row count changed")
    checks.check(strict_common_reference_summary.get("ok_row_count") == 24, "strict common-reference ok count changed")
    checks.check(
        strict_common_reference_summary.get("public_raw_row_count") == 18,
        "strict common-reference public raw row count changed",
    )
    checks.check(
        strict_common_reference_summary.get("local_raw_row_count") == 6,
        "strict common-reference local raw row count changed",
    )
    checks.check(
        strict_common_reference_summary.get("summary_row_count") == 8,
        "strict common-reference summary row count changed",
    )
    checks.check(
        strict_common_reference_summary.get("strict_common_reference_available_count") == 2,
        "strict common-reference availability count changed",
    )
    checks.check(
        strict_common_reference_summary.get("strict_common_reference_gap_count") == 0,
        "strict common-reference gap count should be zero",
    )
    checks.check(
        strict_common_reference_summary.get("strict_common_reference_error_columns") is True,
        "strict common-reference flag changed",
    )
    checks.check(
        strict_common_reference_summary.get("publication_quality_figure_available") is True,
        "strict common-reference figure availability changed",
    )
    checks.check(
        strict_common_reference_summary.get("external_superiority_claim") is False,
        "strict common-reference overclaimed external superiority",
    )
    checks.check(
        strict_common_reference_summary.get("default_1e-4_required") is False,
        "strict common-reference default 1e-4 overclaimed",
    )
    checks.check(len(strict_common_reference_rows) == 24, "strict common-reference CSV row count changed")
    checks.check(
        {row.get("model") for row in strict_common_reference_rows} == {"four_link", "slider_crank"},
        "strict common-reference model set changed",
    )
    checks.check(
        {float(row.get("h", "nan")) for row in strict_common_reference_rows} == {0.1, 0.05, 0.025},
        "strict common-reference step-size set changed",
    )
    checks.check(
        {row.get("status") for row in strict_common_reference_rows} == {"ok"},
        "strict common-reference CSV status changed",
    )
    checks.check(
        len(strict_common_reference_summary_rows) == 8,
        "strict common-reference summary CSV row count changed",
    )
    checks.check(
        strict_common_reference_figure.exists() and strict_common_reference_figure.stat().st_size > 10_000,
        "strict common-reference figure missing or too small",
    )
    checks.check(
        coarse_velocity_order_figure.exists() and coarse_velocity_order_figure.stat().st_size > 50_000,
        "coarse velocity-order figure missing or too small",
    )
    checks.check(
        coarse_velocity_error_figure.exists() and coarse_velocity_error_figure.stat().st_size > 50_000,
        "coarse velocity-error figure missing or too small",
    )
    checks.check(
        "Strict common-reference examples missing: `0`" in strict_common_reference_report,
        "strict common-reference report lost closed-gap token",
    )
    checks.check(
        "External superiority claim: `False`" in strict_common_reference_report,
        "strict common-reference report overclaimed superiority",
    )
    checks.check(len(coarse_first_gate_rows) == 4, "coarse-first readiness gate must have four example rows")
    by_gate_example = {row.get("example"): row for row in coarse_first_gate_rows}
    checks.check(
        set(by_gate_example) == {"single_pendulum", "double_pendulum", "four_link", "slider_crank"},
        "coarse-first readiness gate examples changed",
    )
    checks.check(
        by_gate_example.get("double_pendulum", {}).get("readiness_status")
        == "coarse_same_window_order_time_available",
        "double_pendulum should be the coarse same-window ready row",
    )
    checks.check(
        "7.951/7.042" in by_gate_example.get("double_pendulum", {}).get("current_order_evidence", ""),
        "coarse-first readiness gate missing double Gauss6 order",
    )
    checks.check(
        "0.703/0.754" in by_gate_example.get("double_pendulum", {}).get("current_order_evidence", ""),
        "coarse-first readiness gate missing double public order",
    )
    checks.check(
        by_gate_example.get("single_pendulum", {}).get("readiness_status")
        == "coarse_same_window_order_time_available",
        "single_pendulum should be the second coarse same-window ready row",
    )
    checks.check(
        "6.054/2.951" in by_gate_example.get("single_pendulum", {}).get("current_order_evidence", ""),
        "coarse-first readiness gate missing single Gauss6 order",
    )
    checks.check(
        "reference floor" in by_gate_example.get("single_pendulum", {}).get("current_order_evidence", ""),
        "coarse-first readiness gate missing single reference-floor caveat",
    )
    for example in ["four_link", "slider_crank"]:
        checks.check(
            by_gate_example.get(example, {}).get("readiness_status")
            == "local_true_dynamic_order_public_work_and_strict_common_reference_available",
            f"{example} should have local true-dynamic order, public work rows, and strict common-reference rows",
        )
        checks.check(
            "Local true-dynamic Newton coarse row available"
            in by_gate_example.get(example, {}).get("current_order_evidence", ""),
            f"{example} readiness gate missing true-dynamic order evidence",
        )
        checks.check(
            "strict common-reference v047 exact-endpoint error columns are available"
            in by_gate_example.get(example, {}).get("current_time_evidence", ""),
            f"{example} readiness gate missing strict common-reference evidence",
        )
        checks.check(
            "closed_loop_true_dynamic_newton_coarse_order_rows.csv"
            in by_gate_example.get(example, {}).get("evidence_paths", ""),
            f"{example} readiness gate missing true-dynamic order path in evidence text",
        )
    checks.check(
        closed_loop_surrogate_summary.get("schema") == "closed-loop-surrogate-dynamic-gate-v1",
        "closed-loop surrogate gate schema changed",
    )
    checks.check(
        set(closed_loop_surrogate_summary.get("models", [])) == {"four_link", "slider_crank"},
        "closed-loop surrogate model set changed",
    )
    checks.check(
        closed_loop_surrogate_summary.get("surrogate_available_count") == 2,
        "closed-loop surrogate availability count changed",
    )
    checks.check(
        closed_loop_surrogate_summary.get("accepted_dynamic_order_count") == 0,
        "closed-loop surrogate gate must not accept dynamic order rows",
    )
    checks.check(
        closed_loop_surrogate_summary.get("dynamic_superiority_claim") is False,
        "closed-loop surrogate gate must not claim dynamic superiority",
    )
    checks.check(
        closed_loop_surrogate_summary.get("default_policy") == "coarse_first_no_default_1e-4",
        "closed-loop surrogate default policy changed",
    )
    checks.check(
        closed_loop_surrogate_summary.get("selected_step_sizes") == [0.02, 0.01, 0.005],
        "closed-loop surrogate selected step sizes changed",
    )
    checks.check(
        len(closed_loop_surrogate_rows) == 2,
        "closed-loop surrogate gate should have one row for four_link and one for slider_crank",
    )
    by_surrogate_model = {row.get("model"): row for row in closed_loop_surrogate_rows}
    for model in ["four_link", "slider_crank"]:
        row = by_surrogate_model.get(model, {})
        checks.check(row.get("surrogate_status") == "available_not_dynamic_superiority", f"{model} surrogate status changed")
        checks.check(row.get("dynamic_superiority_claim_allowed") == "false", f"{model} surrogate claim flag changed")
        checks.check(row.get("step_sizes") == "0.02|0.01|0.005", f"{model} surrogate step sizes changed")
        checks.check(
            "kinematic FullVA plus reaction reconstruction" in row.get("acceptance_blocker", ""),
            f"{model} surrogate blocker weakened",
        )
    checks.check(
        closed_loop_floor_audit_summary.get("schema") == "closed-loop-dynamic-error-floor-audit-v1",
        "closed-loop floor audit schema changed",
    )
    checks.check(
        closed_loop_floor_audit_summary.get("velocity_acceleration_evidence_count") == 2,
        "closed-loop floor audit should record two velocity/acceleration evidence rows",
    )
    checks.check(
        closed_loop_floor_audit_summary.get("position_floor_blocker_count") == 2,
        "closed-loop floor audit should record two position-floor blockers",
    )
    checks.check(
        closed_loop_floor_audit_summary.get("accepted_dynamic_order_count") == 0,
        "closed-loop floor audit must not accept dynamic order rows",
    )
    checks.check(
        closed_loop_floor_audit_summary.get("external_superiority_claim") is False,
        "closed-loop floor audit must not claim external superiority",
    )
    checks.check(
        len(closed_loop_floor_audit_rows) == 2,
        "closed-loop floor audit should have one row for four_link and one for slider_crank",
    )
    by_floor_model = {row.get("model"): row for row in closed_loop_floor_audit_rows}
    for model in ["four_link", "slider_crank"]:
        row = by_floor_model.get(model, {})
        checks.check(row.get("accepted_dynamic_order") == "false", f"{model} floor audit accepted flag changed")
        checks.check(row.get("velocity_acceleration_floor_evidence") == "True", f"{model} floor audit evidence flag changed")
        checks.check(row.get("position_floor_blocker") == "True", f"{model} floor audit position blocker changed")
        checks.check(
            float(row.get("local_vel_error_ratio_vs_public", "nan")) < 1.0e-4,
            f"{model} floor audit velocity ratio too large",
        )
        checks.check(
            float(row.get("local_acc_error_ratio_vs_public", "nan")) < 1.0e-4,
            f"{model} floor audit acceleration ratio too large",
        )
    checks.check(
        closed_loop_coarse_probe_summary.get("schema") == "closed-loop-coarse-dynamic-order-probe-v1",
        "closed-loop coarse probe schema changed",
    )
    checks.check(
        closed_loop_coarse_probe_summary.get("default_policy") == "coarse_first_no_default_1e-4",
        "closed-loop coarse probe default policy changed",
    )
    checks.check(
        closed_loop_coarse_probe_summary.get("row_count") == 12,
        "closed-loop coarse probe should record twelve raw rows",
    )
    checks.check(
        closed_loop_coarse_probe_summary.get("ok_row_count") == 11,
        "closed-loop coarse probe should record eleven ok rows",
    )
    checks.check(
        closed_loop_coarse_probe_summary.get("failed_row_count") == 1,
        "closed-loop coarse probe should record one failed row",
    )
    checks.check(
        closed_loop_coarse_probe_summary.get("public_failed_row_count") == 1,
        "closed-loop coarse probe should record one public failure",
    )
    checks.check(
        closed_loop_coarse_probe_summary.get("local_velocity_evidence_rows") == 2,
        "closed-loop coarse probe should preserve two local velocity-evidence rows",
    )
    checks.check(
        closed_loop_coarse_probe_summary.get("local_acceleration_evidence_rows") == 2,
        "closed-loop coarse probe should preserve two local acceleration-evidence rows",
    )
    checks.check(
        closed_loop_coarse_probe_summary.get("local_position_floor_rows") == 2,
        "closed-loop coarse probe should preserve two local position-floor rows",
    )
    checks.check(
        closed_loop_coarse_probe_summary.get("accepted_dynamic_order_count") == 0,
        "closed-loop coarse probe must not accept dynamic order rows",
    )
    checks.check(
        closed_loop_coarse_probe_summary.get("external_superiority_claim") is False,
        "closed-loop coarse probe must not claim external superiority",
    )
    checks.check(
        closed_loop_coarse_probe_summary.get("same_test_campaign_status") == "not_run",
        "closed-loop coarse probe must keep same-test campaign status not_run",
    )
    checks.check(
        closed_loop_coarse_probe_summary.get("failed_rows")
        == [
            {
                "model": "slider_crank",
                "method": "rA-public-dynamics",
                "h": 0.1,
                "status": "failed:ValueError:array must not contain infs or NaNs",
            }
        ],
        "closed-loop coarse probe failed-row detail changed",
    )
    checks.check(len(closed_loop_coarse_probe_rows) == 12, "closed-loop coarse probe raw CSV should have twelve rows")
    checks.check(
        len(closed_loop_coarse_probe_work_rows) == 4,
        "closed-loop coarse probe work/precision CSV should have four rows",
    )
    checks.check(
        all(row.get("default_policy") == "coarse_first_no_default_1e-4" for row in closed_loop_coarse_probe_rows),
        "closed-loop coarse probe raw rows lost no-default-1e-4 policy",
    )
    checks.check(
        all(row.get("accepted_dynamic_order") == "false" for row in closed_loop_coarse_probe_work_rows),
        "closed-loop coarse probe work rows promoted dynamic order",
    )
    checks.check(
        "Raw rows: `11/12` ok" in closed_loop_coarse_probe_report,
        "closed-loop coarse probe report missing raw-row count",
    )
    checks.check(
        "Failed public rows: `1`" in closed_loop_coarse_probe_report,
        "closed-loop coarse probe report missing public failure count",
    )
    checks.check(
        "accepted dynamic order remains zero" in closed_loop_coarse_probe_report,
        "closed-loop coarse probe report missing accepted-order boundary",
    )
    checks.check(
        "does not run default `1e-4` rows" in closed_loop_coarse_probe_report,
        "closed-loop coarse probe report missing no-default-1e-4 boundary",
    )
    checks.check(
        "`1e-4` is not a default execution target" in coarse_first_gate_report,
        "coarse-first readiness gate report missing no-default-1e-4 policy",
    )
    checks.check(
        "not submission ready; no external superiority claim" in coarse_first_gate_report,
        "coarse-first readiness gate report missing no-superiority status",
    )
    checks.check(
        "surrogate evidence only; not external superiority" in closed_loop_surrogate_report,
        "closed-loop surrogate report missing no-superiority status",
    )
    checks.check(
        "does not use default `1e-4` runs" in closed_loop_surrogate_report,
        "closed-loop surrogate report missing no-default-1e-4 boundary",
    )
    checks.check(
        "floor audit only; accepted dynamic order remains zero" in closed_loop_floor_audit_report,
        "closed-loop floor audit report missing status boundary",
    )
    checks.check(
        "does not run default `1e-4` rows" in closed_loop_floor_audit_report,
        "closed-loop floor audit report missing no-default-1e-4 boundary",
    )
    checks.check(timing_summary.get("row_count", 0) >= 12, "2021 public timing should include all 12 form/model rows")
    checks.check(
        timing_summary.get("ok_row_count", 0) >= 12,
        "2021 public timing rows should include twelve ok form/model rows",
    )
    checks.check(
        timing_summary.get("public_timing_rows_completed") == 12,
        "2021 public timing policy should complete 12/12 rows",
    )
    checks.check(
        timing_summary.get("full_ra2021_timing_completed") is True,
        "2021 public timing rows should be marked as the full 12-row timing policy",
    )
    checks.check(summary.get("hi2022_halfimplicit", {}).get("row_count", 0) >= 1, "no 2022 half-implicit rows recorded")
    checks.check(
        summary.get("hi2022_halfimplicit", {}).get("full_hi2022_campaign_completed") is False,
        "2022 half-implicit full campaign unexpectedly marked complete",
    )
    checks.check(
        "public_step_trio_group_count" in summary.get("ra2021_order", {}),
        "summary missing public step-trio group count",
    )
    checks.check(
        summary.get("ra2021_order", {}).get("public_step_trio_required_group_count") == 9,
        "unexpected 2021 public step-trio required group count",
    )
    if summary.get("ra2021_order", {}).get("run_public_code") is False:
        checks.check(
            summary.get("ra2021_order", {}).get("planned_row_count", 0) >= 1,
            "plan-only 2021 run did not record planned rows",
        )
    else:
        checks.check(
            summary.get("ra2021_order", {}).get("ok_row_count", 0) >= 1,
            "2021 public-code smoke did not record an ok row",
        )
        checks.check(
            summary.get("ra2021_order", {}).get("row_count", 0) >= 27,
            "2021 public-code selected run should include all nine public step-size trios",
        )
        checks.check(
            summary.get("ra2021_order", {}).get("ok_row_count", 0) >= 27,
            "2021 public-code selected run should have at least 27 ok rows",
        )
        checks.check(
            summary.get("ra2021_order", {}).get("public_step_trio_group_count", 0) == 9,
            "2021 public-code selected run should complete all nine public step-size trio groups",
        )
        checks.check(
            summary.get("ra2021_order", {}).get("full_ra2021_order_completed") is True,
            "2021 full public order policy should be marked complete",
        )
        checks.check(
            summary.get("ra2021_public_order_work_summary", {}).get("row_count", 0) >= 9,
            "2021 public order/work summary should include all nine form/model groups",
        )
        checks.check(
            len(order_work_summary_rows) >= 9,
            "2021 public order/work summary CSV should include all nine form/model groups",
        )
        selected_groups = set(summary.get("ra2021_order", {}).get("selected_groups", []))
        for group in [
            "rA:single_pendulum",
            "rA:four_link",
            "rA:slider_crank",
            "rp:single_pendulum",
            "rp:four_link",
            "rp:slider_crank",
            "reps:single_pendulum",
            "reps:four_link",
            "reps:slider_crank",
        ]:
            checks.check(group in selected_groups, f"2021 selected groups missing {group}")
    timing_groups = set(timing_summary.get("selected_groups", []))
    double_order_groups = set(double_order_summary.get("selected_groups", []))
    for group in ["rA:double_pendulum", "rp:double_pendulum", "reps:double_pendulum"]:
        checks.check(group in double_order_groups, f"2021 double-pendulum dynamic order groups missing {group}")
    for form in ["rA", "rp", "reps"]:
        checks.check(
            sum(
                1
                for row in double_order_rows
                if row.get("form") == form
                and row.get("model") == "double_pendulum"
                and row.get("status") == "ok"
                and row.get("public_double_order_policy") == "True"
            )
            >= 3,
            f"2021 double-pendulum dynamic order CSV missing ok {form} trio",
        )
    double_coarse_groups = set(double_coarse_summary.get("selected_groups", []))
    for group in ["rA:double_pendulum", "rp:double_pendulum", "reps:double_pendulum"]:
        checks.check(group in double_coarse_groups, f"2021 double-pendulum coarse groups missing {group}")
    for form in ["rA", "reps"]:
        checks.check(
            sum(
                1
                for row in double_coarse_rows
                if row.get("form") == form
                and row.get("model") == "double_pendulum"
                and row.get("status") == "ok"
            )
            >= 3,
            f"2021 double-pendulum coarse same-window CSV missing ok {form} trio",
        )
    checks.check(
        any(
            row.get("form") == "rp"
            and row.get("model") == "double_pendulum"
            and row.get("status", "").startswith("failed:RuntimeError:Newton-Raphson not converging")
            for row in double_coarse_rows
        ),
        "2021 double-pendulum coarse same-window should preserve the rp nonconvergence caveat",
    )
    for method in [
        "Gauss6/FullVA-public-horizon-double-coarse",
        "rA-public-dynamics-coarse",
        "reps-public-dynamics-coarse",
    ]:
        checks.check(
            any(row.get("method") == method for row in double_coarse_work_summary_rows),
            f"double-pendulum coarse work/precision summary missing {method}",
        )
    for form in ["rA", "rp", "reps"]:
        checks.check(
            sum(
                1
                for row in single_coarse_public_rows
                if row.get("form") == form
                and row.get("model") == "single_pendulum"
                and row.get("status") == "ok"
                and row.get("coarse_same_window_policy") == "True"
                and row.get("public_policy_h") == "False"
            )
            == 3,
            f"2021 single-pendulum coarse same-window CSV missing ok {form} trio",
        )
    checks.check(
        len(single_coarse_local_rows) == 3,
        "Gauss6 single-pendulum coarse CSV should have three rows",
    )
    checks.check(
        all(
            row.get("status") == "ok"
            and row.get("coarse_same_window_policy") == "True"
            and row.get("public_policy_h") == "False"
            for row in single_coarse_local_rows
        ),
        "Gauss6 single-pendulum coarse CSV rows should be ok no-default-1e-4 rows",
    )
    for method in [
        "Gauss6/FullVA-public-horizon-single-coarse",
        "rA-public-dynamics-coarse",
        "rp-public-dynamics-coarse",
        "reps-public-dynamics-coarse",
    ]:
        checks.check(
            any(row.get("method") == method for row in single_coarse_work_summary_rows),
            f"single-pendulum coarse work/precision summary missing {method}",
        )
    gauss_single_work = next(
        (
            row
            for row in single_coarse_work_summary_rows
            if row.get("method") == "Gauss6/FullVA-public-horizon-single-coarse"
        ),
        {},
    )
    checks.check(
        float(gauss_single_work.get("pos_observed_order", "0") or 0.0) > 5.0,
        "single-pendulum coarse work summary should record Gauss6 sixth-order position convergence",
    )
    checks.check(
        single_coarse_work_summary_json.get("default_policy") == "coarse_first_no_default_1e-4",
        "single-pendulum coarse JSON should preserve no-default-1e-4 policy",
    )
    checks.check(
        "intentionally avoids default `1e-4` rows" in single_coarse_work_summary_report,
        "single-pendulum coarse markdown should preserve no-default-1e-4 policy",
    )
    for group in ["rA:double_pendulum", "rp:double_pendulum", "reps:double_pendulum"]:
        checks.check(group in timing_groups, f"2021 public timing groups missing {group}")
    for form in ["rA", "rp", "reps"]:
        checks.check(
            any(
                row.get("form") == form
                and row.get("model") == "double_pendulum"
                and row.get("status") == "ok"
                and row.get("public_timing_policy") == "True"
                for row in timing_rows
            ),
            f"2021 public timing CSV missing ok {form}:double_pendulum row",
        )
    checks.check(len(plan_rows) >= 17, "run plan missing case inventory rows")
    checks.check(len(workload_rows) >= 2, "workload estimate missing public/selected rows")
    checks.check(len(hi2022_workload_rows) >= 2, "2022 half-implicit workload estimate missing public/selected rows")
    checks.check(len(order_rows) >= 1, "2021 order rows CSV is empty")
    checks.check(len(order_work_summary_rows) >= 1, "2021 public order/work summary CSV is empty")
    checks.check(len(double_order_rows) >= 9, "2021 double-pendulum dynamic order CSV is missing rows")
    checks.check(len(double_coarse_rows) >= 9, "2021 double-pendulum coarse same-window CSV is missing rows")
    checks.check(len(single_coarse_public_rows) == 9, "2021 single-pendulum coarse same-window CSV is missing rows")
    checks.check(len(single_coarse_local_rows) == 3, "Gauss6 single-pendulum coarse CSV is missing rows")
    checks.check(
        len(double_coarse_work_summary_rows) >= 3,
        "double-pendulum coarse same-window work/precision summary CSV is missing rows",
    )
    checks.check(
        len(single_coarse_work_summary_rows) == 4,
        "single-pendulum coarse same-window work/precision summary CSV is missing rows",
    )
    checks.check(len(timing_rows) >= 3, "2021 public timing rows CSV is missing the double-pendulum rows")
    checks.check(len(hi2022_rows) >= 1, "2022 half-implicit rows CSV is empty")
    checks.check(len(gauss6_rows) >= 1, "Gauss6 external rows CSV is empty")
    checks.check(len(gauss6_public_single_rows) >= 1, "Gauss6 public-horizon single rows CSV is empty")
    checks.check(
        len(gauss6_public_double_coarse_rows) >= 3,
        "Gauss6 public-horizon double coarse rows CSV is missing rows",
    )
    checks.check(len(gauss6_closed_loop_rows) >= 1, "Gauss6 closed-loop external rows CSV is empty")
    checks.check(
        len(gauss6_public_closed_loop_rows) >= 1,
        "Gauss6 public-horizon closed-loop rows CSV is empty",
    )
    checks.check(
        len(gauss6_closed_loop_comparison_rows) >= 1,
        "Gauss6 closed-loop same-window comparison rows CSV is empty",
    )
    checks.check(
        len(same_window_work_summary_rows) >= 1,
        "Gauss6 closed-loop same-window work/precision summary CSV is empty",
    )
    checks.check(len(closed_loop_floor_audit_rows) == 2, "closed-loop dynamic error floor audit CSV is incomplete")
    checks.check(
        len(closed_loop_coarse_probe_rows) == 12,
        "closed-loop coarse dynamic-order probe raw CSV is incomplete",
    )
    checks.check(
        len(closed_loop_coarse_probe_work_rows) == 4,
        "closed-loop coarse dynamic-order probe work/precision CSV is incomplete",
    )
    checks.check(len(coarse_first_gate_rows) == 4, "coarse-first external readiness gate CSV is incomplete")
    checks.check(len(vp_search_rows) >= 5, "velocity-partitioning code search CSV is empty")
    checks.check(any(row.get("case_id") == "ra2021_single_pendulum_order" for row in plan_rows), "run plan missing 2021 single order")
    checks.check(any(row.get("case_id") == "hi2022_double_pendulum_open_loop_convergence" for row in plan_rows), "run plan missing 2022 double convergence")
    checks.check(any(row.get("case_id") == "vp2024_velocity_partitioning_code_resolution" for row in plan_rows), "run plan missing velocity-partitioning code gate")
    if summary.get("ra2021_order", {}).get("run_public_code") is False:
        checks.check(any(row.get("status") == "planned_not_run" for row in order_rows), "plan-only rows missing planned_not_run status")
    else:
        checks.check(any(row.get("status") == "ok" for row in order_rows), "2021 order/smoke rows have no ok row")
    if summary.get("gauss6_fullva_external", {}).get("run_model") is True:
        checks.check(any(row.get("status") == "ok" for row in gauss6_rows), "Gauss6 selected rows have no ok row")
    else:
        checks.check(
            any(row.get("status") == "planned_not_run" for row in gauss6_rows),
            "Gauss6 non-run rows missing planned_not_run status",
        )
    public_single_summary = summary.get("gauss6_fullva_public_horizon_single", {})
    checks.check(
        public_single_summary.get("public_step_size_required_count") == 3,
        "Gauss6 public-horizon single-pendulum required public h count changed",
    )
    if public_single_summary.get("public_single_step_trio_completed") is True:
        checks.check(
            public_single_summary.get("public_step_size_rows_completed") == 3,
            "Gauss6 public-horizon single-pendulum trio marked complete without all three public h rows",
        )
    if public_single_summary.get("run_model") is True:
        checks.check(
            any(row.get("status") == "ok" for row in gauss6_public_single_rows),
            "Gauss6 public-horizon single rows have no ok row",
        )
        checks.check(
            any(row.get("public_policy_time_window") == "True" for row in gauss6_public_single_rows),
            "Gauss6 public-horizon single rows are not on the public time window",
        )
    else:
        checks.check(
            any(row.get("status") == "planned_not_run" for row in gauss6_public_single_rows),
            "Gauss6 public-horizon single non-run rows missing planned_not_run status",
        )
    public_double_coarse_summary = summary.get("gauss6_fullva_public_horizon_double_coarse", {})
    checks.check(
        public_double_coarse_summary.get("public_policy_h_required_count") == 3,
        "Gauss6 public-horizon double coarse required public h count changed",
    )
    checks.check(
        public_double_coarse_summary.get("full_external_campaign_completed") is False,
        "Gauss6 public-horizon double coarse unexpectedly marked full campaign complete",
    )
    checks.check(
        public_double_coarse_summary.get("public_double_step_trio_completed") is False,
        "Gauss6 public-horizon double coarse must not be marked as public policy trio complete",
    )
    if public_double_coarse_summary.get("run_model") is True:
        checks.check(
            public_double_coarse_summary.get("ok_row_count", 0) >= 3,
            "Gauss6 public-horizon double coarse should have three ok rows",
        )
        checks.check(
            any(row.get("status") == "ok" for row in gauss6_public_double_coarse_rows),
            "Gauss6 public-horizon double coarse rows have no ok row",
        )
        checks.check(
            any(row.get("public_policy_time_window") == "True" for row in gauss6_public_double_coarse_rows),
            "Gauss6 public-horizon double coarse rows are not on the public time window",
        )
        checks.check(
            all(row.get("public_policy_h") == "False" for row in gauss6_public_double_coarse_rows),
            "Gauss6 public-horizon double coarse rows must remain outside the public h policy",
        )
    else:
        checks.check(
            any(row.get("status") == "planned_not_run" for row in gauss6_public_double_coarse_rows),
            "Gauss6 public-horizon double coarse non-run rows missing planned_not_run status",
        )
    if summary.get("gauss6_fullva_closed_loop_external", {}).get("run_model") is True:
        checks.check(
            summary.get("gauss6_fullva_closed_loop_external", {}).get("row_count", 0) >= 6,
            "Gauss6 closed-loop selected rows should include four_link and slider_crank three-step rows",
        )
        checks.check(
            summary.get("gauss6_fullva_closed_loop_external", {}).get("ok_row_count", 0) >= 6,
            "Gauss6 closed-loop selected rows should have at least six ok rows",
        )
        selected_models = set(summary.get("gauss6_fullva_closed_loop_external", {}).get("selected_models", []))
        for model in ["four_link", "slider_crank"]:
            checks.check(model in selected_models, f"Gauss6 closed-loop selected models missing {model}")
        checks.check(any(row.get("status") == "ok" for row in gauss6_closed_loop_rows), "Gauss6 closed-loop rows have no ok row")
    else:
        checks.check(
            any(row.get("status") == "planned_not_run" for row in gauss6_closed_loop_rows),
            "Gauss6 closed-loop non-run rows missing planned_not_run status",
        )
    public_closed_loop_summary = summary.get("gauss6_fullva_public_horizon_closed_loop", {})
    checks.check(
        public_closed_loop_summary.get("public_step_size_required_count") == 6,
        "Gauss6 public-horizon closed-loop required public h count changed",
    )
    checks.check(
        public_closed_loop_summary.get("full_external_campaign_completed") is False,
        "Gauss6 public-horizon closed-loop tranche unexpectedly marked full campaign complete",
    )
    if public_closed_loop_summary.get("public_closed_loop_step_trios_completed") is True:
        checks.check(
            public_closed_loop_summary.get("public_step_size_rows_completed") == 6,
            "Gauss6 public-horizon closed-loop trios marked complete without all six public h rows",
        )
    if public_closed_loop_summary.get("run_model") is True:
        checks.check(
            any(row.get("status") == "ok" for row in gauss6_public_closed_loop_rows),
            "Gauss6 public-horizon closed-loop rows have no ok row",
        )
        checks.check(
            any(row.get("public_policy_time_window") == "True" for row in gauss6_public_closed_loop_rows),
            "Gauss6 public-horizon closed-loop rows are not on the public time window",
        )
    else:
        checks.check(
            any(row.get("status") == "planned_not_run" for row in gauss6_public_closed_loop_rows),
            "Gauss6 public-horizon closed-loop non-run rows missing planned_not_run status",
        )
    comparison_summary = summary.get("gauss6_fullva_closed_loop_same_window_comparison", {})
    if comparison_summary.get("run_model") is True:
        checks.check(
            comparison_summary.get("row_count", 0) >= 12,
            "Gauss6 closed-loop same-window comparison should include two models, two methods, and three step sizes",
        )
        checks.check(
            comparison_summary.get("ok_row_count", 0) >= 12,
            "Gauss6 closed-loop same-window comparison should have at least twelve ok rows",
        )
        selected_models = set(comparison_summary.get("selected_models", []))
        for model in ["four_link", "slider_crank"]:
            checks.check(model in selected_models, f"same-window comparison selected models missing {model}")
        methods = {row.get("method") for row in gauss6_closed_loop_comparison_rows}
        for method in ["rA-public-dynamics", "Gauss6/FullVA-local-closed-loop"]:
            checks.check(method in methods, f"same-window comparison missing method {method}")
        work_methods = {row.get("method") for row in same_window_work_summary_rows}
        for method in ["rA-public-dynamics", "Gauss6/FullVA-local-closed-loop"]:
            checks.check(method in work_methods, f"same-window work/precision summary missing method {method}")
        checks.check(
            summary.get("gauss6_closed_loop_same_window_work_precision_summary", {}).get("row_count", 0) >= 4,
            "same-window work/precision summary should include two models and two methods",
        )
        checks.check(
            any(row.get("status") == "ok" for row in gauss6_closed_loop_comparison_rows),
            "Gauss6 closed-loop same-window comparison rows have no ok row",
        )
    else:
        checks.check(
            any(row.get("status") == "planned_not_run" for row in gauss6_closed_loop_comparison_rows),
            "Gauss6 closed-loop same-window comparison non-run rows missing planned_not_run status",
        )
    if summary.get("hi2022_halfimplicit", {}).get("run_public_code") is True:
        checks.check(
            summary.get("hi2022_halfimplicit", {}).get("row_count", 0) >= 24,
            "2022 half-implicit selected run should include four models x two forms x three-step rows",
        )
        checks.check(
            summary.get("hi2022_halfimplicit", {}).get("ok_row_count", 0) >= 24,
            "2022 half-implicit selected run should have at least 24 ok rows",
        )
        checks.check(
            summary.get("hi2022_halfimplicit", {}).get("selected_step_trio_group_count", 0) >= 8,
            "2022 half-implicit selected run should complete all four-model form trios",
        )
        selected_forms = set(summary.get("hi2022_halfimplicit", {}).get("selected_forms", []))
        for form in ["rA", "rA_half"]:
            checks.check(form in selected_forms, f"2022 half-implicit selected forms missing {form}")
        selected_models = set(summary.get("hi2022_halfimplicit", {}).get("selected_models", []))
        for model in ["single_pendulum", "double_pendulum", "four_link", "slider_crank"]:
            checks.check(model in selected_models, f"2022 half-implicit selected models missing {model}")
        group_keys = set(summary.get("hi2022_halfimplicit", {}).get("groups", {}))
        for form in ["rA", "rA_half"]:
            for model in ["single_pendulum", "double_pendulum", "four_link", "slider_crank"]:
                checks.check(f"{form}:{model}" in group_keys, f"2022 half-implicit group missing {form}:{model}")
        checks.check(any(row.get("status") == "ok" for row in hi2022_rows), "2022 half-implicit rows have no ok row")
        checks.check(
            any(row.get("execution_path") == "state_history_replay" for row in hi2022_rows),
            "2022 half-implicit closed-loop replay rows missing execution_path audit",
        )
    else:
        checks.check(
            any(row.get("status") == "planned_not_run" for row in hi2022_rows),
            "2022 half-implicit non-run rows missing planned_not_run status",
        )
    checks.check(
        any(row.get("scope") == "ra2021_full_public_order_policy" for row in workload_rows),
        "workload estimate missing full public 2021 policy row",
    )
    checks.check(
        any(row.get("scope") == "ra2021_selected_run" for row in workload_rows),
        "workload estimate missing selected run row",
    )

    for token in [
        "same-test campaign has passed",
        "external-method superiority",
        "not a new integrator version",
        "2021 `rA/rp/reps` public-code order policy is now complete",
        "complete `Gauss6/FullVA` external campaign",
        "public step-size trio groups completed",
        "2021 selected groups",
        "2021 public order/work summary rows",
        "2021 Public Order/Work Summary",
        "ra2021_public_order_work_summary.csv",
        "2021 double-pendulum dynamic order rows",
        "2021 Double-Pendulum Dynamic Self-Reference Order Rows",
        "ra2021_double_pendulum_order_rows.csv",
        "dynamic self-reference order",
        "2021 double-pendulum coarse same-window public rows",
        "2021 Double-Pendulum Coarse Same-Window Public Rows",
        "ra2021_double_pendulum_coarse_order_rows.csv",
        "Double-Pendulum Coarse Same-Window Work/Precision Summary",
        "double_pendulum_coarse_same_window_work_precision_summary.csv",
        "2021 single-pendulum coarse same-window public rows",
        "Single-Pendulum Coarse Same-Window Work/Precision Summary",
        "ra2021_single_pendulum_coarse_order_rows.csv",
        "gauss6_fullva_public_horizon_single_coarse_rows.csv",
        "single_pendulum_coarse_same_window_work_precision_summary.csv",
        "single_pendulum_coarse_same_window_work_precision_summary.json",
        "single_pendulum_coarse_same_window_work_precision_summary.md",
        "`1e-4` is not a default execution target",
        "reference `h=0.0125`",
        "2021 public timing rows",
        "2021 Public Timing/Iteration Rows",
        "ra2021_public_timing_rows.csv",
        "public dynamics default tolerance",
        "2022 half-implicit selected rows",
        "2022 Half-Implicit Group Orders",
        "hi2022_halfimplicit_rows.csv",
        "Gauss6/FullVA selected external rows",
        "Gauss6/FullVA public-horizon single rows",
        "Gauss6/FullVA Public-Horizon Single-Pendulum Tranche",
        "gauss6_fullva_public_horizon_single_rows.csv",
        "actual 2021 public time window",
        "Gauss6/FullVA public-horizon double coarse rows",
        "Gauss6/FullVA Public-Horizon Double-Pendulum Coarse Tranche",
        "gauss6_fullva_public_horizon_double_coarse_rows.csv",
        "larger step",
        "Gauss6/FullVA closed-loop external rows",
        "Gauss6/FullVA Closed-Loop External Rows",
        "gauss6_fullva_closed_loop_external_rows.csv",
        "Gauss6/FullVA public-horizon closed-loop rows",
        "Gauss6/FullVA Public-Horizon Closed-Loop Tranche",
        "gauss6_fullva_public_horizon_closed_loop_rows.csv",
        "Selected Closed-Loop Same-Window Comparison",
        "Closed-loop same-window comparison rows",
        "gauss6_fullva_closed_loop_same_window_comparison_rows.csv",
        "Selected Same-Window Work/Precision Summary",
        "gauss6_closed_loop_same_window_work_precision_summary.csv",
        "Closed-Loop Surrogate Dynamic Gate",
        "closed_loop_surrogate_dynamic_gate.csv",
        "closed_loop_surrogate_dynamic_gate.json",
        "closed_loop_surrogate_dynamic_gate.md",
        "surrogate evidence only",
        "accepted dynamic order rows",
        "Closed-Loop Dynamic Error Floor Audit",
        "closed_loop_dynamic_error_floor_audit.csv",
        "closed_loop_dynamic_error_floor_audit.json",
        "closed_loop_dynamic_error_floor_audit.md",
        "velocity/acceleration evidence",
        "position-floor blockers",
        "Closed-Loop Coarse Dynamic-Order Probe",
        "closed_loop_coarse_dynamic_order_probe_rows.csv",
        "closed_loop_coarse_dynamic_order_probe_work_precision_summary.csv",
        "closed_loop_coarse_dynamic_order_probe.json",
        "closed_loop_coarse_dynamic_order_probe.md",
        "large-step",
        "`11/12` rows",
        "one public `slider_crank`/`rA` failure",
        "zero accepted dynamic-order rows",
        "coarse_first_external_readiness_gate.csv",
        "coarse_first_external_readiness_gate.json",
        "coarse_first_external_readiness_gate.md",
        "public-kinematic-reference final-error",
        "bounded same-mechanism pilot",
        "velocity_partitioning_code_search.csv",
        "public-metadata",
    ]:
        checks.check(token in report, f"report missing token: {token}")

    forbidden = [
        "same_test_campaign_status=passed",
        "external_superiority_claim=True",
        "Gauss6/FullVA has beaten the external baselines",
    ]
    serialized = json.dumps(summary, sort_keys=True) + "\n" + report
    for token in forbidden:
        checks.check(token not in serialized, f"forbidden completed claim present: {token}")

    if checks.errors:
        print("v048 validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("v048 validation: PASS")
    print(f"run_mode={summary.get('run_mode')}")
    print("same_test_campaign_status=not_run")
    print(f"case_inventory_rows={summary.get('case_inventory_rows')}")
    print(f"ra2021_order_rows={summary.get('ra2021_order', {}).get('row_count')}")
    print(f"ra2021_ok_rows={summary.get('ra2021_order', {}).get('ok_row_count')}")
    print(f"ra2021_planned_rows={summary.get('ra2021_order', {}).get('planned_row_count')}")
    print(f"ra2021_public_step_trio_groups={summary.get('ra2021_order', {}).get('public_step_trio_group_count')}/9")
    print(f"ra2021_selected_groups={','.join(summary.get('ra2021_order', {}).get('selected_groups', []))}")
    print(f"ra2021_public_order_work_summary_rows={summary.get('ra2021_public_order_work_summary', {}).get('row_count')}")
    print(f"ra2021_double_order_rows={double_order_summary.get('ok_row_count')}/{double_order_summary.get('row_count')}")
    print(
        "ra2021_double_order_groups="
        f"{double_order_summary.get('selected_step_trio_group_count')}/{double_order_summary.get('selected_step_trio_required_group_count')}"
    )
    print(
        "ra2021_double_coarse_rows="
        f"{double_coarse_summary.get('ok_row_count')}/{double_coarse_summary.get('row_count')}"
    )
    print(
        "ra2021_double_coarse_groups="
        f"{double_coarse_summary.get('selected_step_trio_group_count')}/{double_coarse_summary.get('selected_step_trio_required_group_count')}"
    )
    print(f"double_coarse_work_precision_rows={double_coarse_work_summary.get('row_count')}")
    print(
        "ra2021_single_coarse_rows="
        f"{single_coarse_public_summary.get('ok_row_count')}/{single_coarse_public_summary.get('row_count')}"
    )
    print(
        "gauss6_single_coarse_rows="
        f"{single_coarse_local_summary.get('ok_row_count')}/{single_coarse_local_summary.get('row_count')}"
    )
    print(f"single_coarse_work_precision_rows={single_coarse_work_summary.get('row_count')}")
    print(f"closed_loop_surrogate_rows={closed_loop_surrogate_summary.get('row_count')}")
    print(
        "closed_loop_surrogate_accepted_dynamic_order="
        f"{closed_loop_surrogate_summary.get('accepted_dynamic_order_count')}"
    )
    print(f"closed_loop_floor_audit_rows={closed_loop_floor_audit_summary.get('row_count')}")
    print(
        "closed_loop_floor_audit_velocity_acceleration_evidence="
        f"{closed_loop_floor_audit_summary.get('velocity_acceleration_evidence_count')}"
    )
    print(
        "closed_loop_floor_audit_accepted_dynamic_order="
        f"{closed_loop_floor_audit_summary.get('accepted_dynamic_order_count')}"
    )
    print(
        "closed_loop_coarse_probe_rows="
        f"{closed_loop_coarse_probe_summary.get('ok_row_count')}/{closed_loop_coarse_probe_summary.get('row_count')}"
    )
    print(
        "closed_loop_coarse_probe_accepted_dynamic_order="
        f"{closed_loop_coarse_probe_summary.get('accepted_dynamic_order_count')}"
    )
    print(f"closed_loop_stage_residual_audit_rows={stage_residual_audit_summary.get('ok_row_count')}/{stage_residual_audit_summary.get('row_count')}")
    print(f"closed_loop_stage_residual_audit_max={stage_residual_audit_summary.get('max_stage_residual_inf'):.6e}")
    print("closed_loop_stage_residual_audit_accepted_dynamic_order=0")
    print(f"closed_loop_one_step_smoke_rows={one_step_smoke_summary.get('ok_row_count')}/{one_step_smoke_summary.get('row_count')}")
    print(f"closed_loop_one_step_smoke_max_endpoint_pos_error={one_step_smoke_summary.get('max_endpoint_pos_error_inf'):.6e}")
    print("closed_loop_one_step_smoke_accepted_dynamic_order=0")
    print(
        "closed_loop_newton_stage_smoke_rows="
        f"{newton_stage_smoke_summary.get('ok_row_count')}/{newton_stage_smoke_summary.get('row_count')}"
    )
    print(f"closed_loop_newton_stage_smoke_max_initial={newton_stage_smoke_summary.get('max_initial_stage_residual_inf'):.6e}")
    print(f"closed_loop_newton_stage_smoke_max_final={newton_stage_smoke_summary.get('max_stage_residual_inf'):.6e}")
    print("closed_loop_newton_stage_smoke_stage_oracle_used=False")
    print("closed_loop_newton_stage_smoke_accepted_dynamic_order=0")
    print(f"closed_loop_newton_coarse_order_rows={newton_coarse_order_summary.get('ok_row_count')}/{newton_coarse_order_summary.get('row_count')}")
    print(f"closed_loop_newton_coarse_order_accepted_dynamic_order={newton_coarse_order_summary.get('accepted_dynamic_order_count')}")
    print(
        "closed_loop_public_work_precision_rows="
        f"{public_work_precision_summary.get('ok_row_count')}/{public_work_precision_summary.get('row_count')}"
    )
    print(
        "closed_loop_public_work_precision_available="
        f"{public_work_precision_summary.get('public_work_precision_available_count')}/2"
    )
    print(
        "closed_loop_strict_common_reference_rows="
        f"{strict_common_reference_summary.get('ok_row_count')}/{strict_common_reference_summary.get('row_count')}"
    )
    print(
        "closed_loop_strict_common_reference_available="
        f"{strict_common_reference_summary.get('strict_common_reference_available_count')}/2"
    )
    print(f"closed_loop_strict_common_reference_gap={strict_common_reference_summary.get('strict_common_reference_gap_count')}")
    print(
        "coarse_first_ready_examples="
        f"{coarse_first_gate_summary.get('coarse_same_window_ready_count')}/4"
    )
    print(f"coarse_first_dynamic_order_missing={coarse_first_gate_summary.get('dynamic_order_missing_count')}")
    print(f"coarse_first_public_work_precision_available={coarse_first_gate_summary.get('public_work_precision_available_count')}")
    print(f"coarse_first_public_work_precision_missing={coarse_first_gate_summary.get('public_work_precision_missing_count')}")
    print(f"coarse_first_strict_common_reference_available={coarse_first_gate_summary.get('strict_common_reference_available_count')}")
    print(f"coarse_first_strict_common_reference_gap={coarse_first_gate_summary.get('strict_common_reference_gap_count')}")
    print(f"coarse_first_strict_common_reference_figure_available={coarse_first_gate_summary.get('strict_common_reference_figure_available')}")
    print(f"ra2021_public_timing_rows={timing_summary.get('ok_row_count')}/{timing_summary.get('row_count')}")
    print(
        "ra2021_public_timing_policy_rows="
        f"{timing_summary.get('public_timing_rows_completed')}/{timing_summary.get('public_timing_required_count')}"
    )
    print(f"gauss6_fullva_selected_rows={summary.get('gauss6_fullva_external', {}).get('ok_row_count')}/{summary.get('gauss6_fullva_external', {}).get('row_count')}")
    print(f"gauss6_fullva_selected_rows_completed={summary.get('gauss6_fullva_selected_rows_completed')}")
    print(f"gauss6_public_horizon_single_rows={public_single_summary.get('ok_row_count')}/{public_single_summary.get('row_count')}")
    print(f"gauss6_public_horizon_single_public_h_rows={public_single_summary.get('public_step_size_rows_completed')}/3")
    print(
        "gauss6_public_horizon_double_coarse_rows="
        f"{public_double_coarse_summary.get('ok_row_count')}/{public_double_coarse_summary.get('row_count')}"
    )
    print(
        "gauss6_public_horizon_closed_loop_rows="
        f"{public_closed_loop_summary.get('ok_row_count')}/{public_closed_loop_summary.get('row_count')}"
    )
    print(
        "gauss6_public_horizon_closed_loop_public_h_rows="
        f"{public_closed_loop_summary.get('public_step_size_rows_completed')}/6"
    )
    print(f"gauss6_closed_loop_same_window_rows={comparison_summary.get('ok_row_count')}/{comparison_summary.get('row_count')}")
    print(f"gauss6_same_window_work_precision_rows={summary.get('gauss6_closed_loop_same_window_work_precision_summary', {}).get('row_count')}")
    print(f"hi2022_halfimplicit_rows={summary.get('hi2022_halfimplicit', {}).get('ok_row_count')}/{summary.get('hi2022_halfimplicit', {}).get('row_count')}")
    print(f"hi2022_selected_forms={','.join(summary.get('hi2022_halfimplicit', {}).get('selected_forms', []))}")
    print(f"velocity_partitioning_code_status={summary.get('velocity_partitioning_code_status')}")
    if tfe_order_rows:
        order_row = tfe_order_rows[0]
        print(
            "tfe_m3_four_link_common_reference_orders="
            f"{order_row.get('pos_order')}/{order_row.get('vel_order')}/{order_row.get('acc_order')}"
        )
    print(
        "baseline_coverage_matrix="
        f"{baseline_coverage_summary.get('accepted_same_grid_four_example_methods')}/"
        f"{baseline_coverage_summary.get('row_count')}"
    )
    print(
        "baseline_required_methods_resolved="
        f"{baseline_coverage_summary.get('required_methods_resolved_count')}/"
        f"{baseline_coverage_summary.get('row_count')}"
    )
    print(
        "baseline_scope_excluded="
        f"{','.join(baseline_coverage_summary.get('scope_excluded_methods', []))}"
    )
    print(
        "baseline_coverage_unresolved="
        f"{','.join(baseline_coverage_summary.get('source_unresolved_methods', []))}"
    )
    print(
        "common_reference_error_wins="
        f"{common_reference_summary.get('local_finest_velocity_error_wins')}/"
        f"{common_reference_summary.get('local_finest_velocity_error_comparisons')}"
    )
    print(
        "apples_to_apples_rows="
        f"{apples_policy_summary.get('paper_safe_row_count')}/{apples_policy_summary.get('row_count')}"
    )
    print(f"apples_to_apples_nonlocal={apples_policy_summary.get('nonlocal_paper_safe_comparison_count')}")
    print(
        "global_comparison_policy="
        f"{global_policy_summary.get('passed_count')}/{global_policy_summary.get('row_count')}"
    )
    print(f"mixed_policy_direct_error_rows={global_policy_summary.get('mixed_policy_direct_error_vs_local_comparable_rows')}")
    print(f"public_code_fixed_grid_replay={common_reference_summary.get('public_code_fixed_grid_replay')}")
    print(f"source_policy_reproduction={common_reference_summary.get('source_policy_reproduction')}")
    print(f"objective_closure_complete={objective_closure_summary.get('objective_complete')}")
    print(
        "objective_closure_requirements="
        f"{objective_closure_summary.get('passed_count')}/{objective_closure_summary.get('row_count')}"
    )
    print("external_superiority_claim=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
