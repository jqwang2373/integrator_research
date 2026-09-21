#!/usr/bin/env python3
"""Validate the RA2021 source-policy row audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
V048_RESULTS = PAPER.parent.parent / "numerics" / "v048_cross_paper_same_test_benchmarks" / "results"


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
        audit = read_json(PAPER / "RA2021_SOURCE_POLICY_ROW_AUDIT.json")
        audit_md = read_text(PAPER / "RA2021_SOURCE_POLICY_ROW_AUDIT.md")
        source_identity = read_json(PAPER / "RA2021_SOURCE_IDENTITY_AUDIT.json")
        b2 = read_json(PAPER / "B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.json")
        external_case = read_json(PAPER / "EXTERNAL_CASE_EVIDENCE_RECONCILIATION.json")
        double_source_policy_candidate = read_json(
            V048_RESULTS / "ra2021_double_local_source_policy_candidate_summary.json"
        )
        double_low_order_diagnosis = read_json(
            PAPER / "RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.json"
        )
        closed_loop_public_work = read_json(
            V048_RESULTS / "closed_loop_true_dynamic_public_work_precision.json"
        )
    except Exception as exc:  # noqa: BLE001
        print(f"RA2021 source-policy row audit validation: FAIL\n- {exc}")
        return 1

    progress = external_case.get("source_policy_progress", {}).get("ra2021_public_baselines", {})
    rows = audit.get("rows", [])
    active_b2_rows = [
        row
        for row in b2.get("rows", [])
        if row.get("suite_id") == "ra2021_absolute_coordinate" and row.get("active_b2_requirement") is True
    ]
    criteria = audit.get("closure_criteria", {})
    decision = audit.get("decision", {})
    source_identity_block = audit.get("source_identity_audit", {})
    local_feasibility = audit.get("local_candidate_feasibility", {})
    closed_loop_same_window = audit.get("closed_loop_same_window_public_work_precision_evidence", {})
    isolated_double_candidate = audit.get("ra2021_double_local_source_policy_candidate", {})
    isolated_double_low_order = isolated_double_candidate.get("low_order_diagnosis", {})
    promotion_gap = audit.get("promotion_gap_drilldown", {})
    allowed_double_candidate_statuses = {
        "planned_isolated_source_policy_candidate",
        "reference_failed_isolated_source_policy_candidate",
        "reference_checkpointed_isolated_source_policy_candidate",
        "reference_cached_isolated_source_policy_candidate",
        "partially_executed_isolated_source_policy_candidate",
        "executed_isolated_source_policy_candidate",
    }
    expected_double_candidate_completed = double_source_policy_candidate.get("source_policy_candidate_rows_completed")

    checks.check(audit.get("schema") == "ra2021-source-policy-row-audit-v1", "schema changed")
    checks.check(
        audit.get("status") == "public_rows_complete_source_policy_rows_not_closed",
        "status changed",
    )
    checks.check(audit.get("submission_ready") is False, "audit overclaims submission readiness")
    checks.check(audit.get("suite_id") == "ra2021_absolute_coordinate", "suite id changed")
    checks.check(audit.get("source_policy_external_superiority_allowed") is False, "source-policy superiority overclaimed")
    checks.check(audit.get("external_superiority_claim_allowed") is False, "external superiority overclaimed")
    checks.check(audit.get("active_b2_flagged_rows") == len(active_b2_rows) == 0, "active B2 row count changed")
    checks.check(audit.get("audited_active_rows") == len(rows) == 0, "audited row count changed")
    checks.check(audit.get("source_policy_closed_rows") == 0, "source-policy rows unexpectedly closed")
    checks.check(audit.get("external_superiority_ready_rows") == 0, "external-superiority-ready rows unexpectedly present")
    checks.check(
        audit.get("public_order_groups_completed")
        == progress.get("order_groups_completed")
        == audit.get("public_order_groups_required")
        == progress.get("order_groups_required")
        == 12,
        "public order group count changed",
    )
    checks.check(
        audit.get("public_timing_rows_completed")
        == progress.get("timing_rows_completed")
        == audit.get("public_timing_rows_required")
        == progress.get("timing_rows_required")
        == 12,
        "public timing row count changed",
    )
    checks.check(audit.get("order_summary_rows") == 9, "order summary row count changed")
    checks.check(audit.get("order_summary_ok_rows") == 9, "order summary ok count changed")
    checks.check(audit.get("timing_rows") == 12, "timing row count changed")
    checks.check(audit.get("timing_ok_rows") == 12, "timing ok row count changed")
    checks.check(audit.get("fixed_grid_common_reference_rows") == 12, "fixed-grid RA2021 row count changed")
    checks.check(audit.get("paper_safe_common_reference_rows") == 12, "paper-safe RA2021 row count changed")
    checks.check(audit.get("source_policy_reproduction_rows") == 0, "source-policy reproduction count changed")
    checks.check(
        audit.get("per_row_source_identity_requirements_resolved") == 3,
        "per-row resolved source-identity requirement count changed",
    )
    checks.check(
        audit.get("per_row_source_policy_promotion_requirements_remaining") == 4,
        "per-row remaining promotion requirement count changed",
    )
    checks.check(
        audit.get("row_missing_evidence_shrunk_by_identity_audit") is True,
        "row missing-evidence shrink marker missing",
    )
    checks.check(audit.get("position_aligned_velocity_mismatch_rows") == 9, "RA2021 velocity mismatch count changed")
    checks.check(
        audit.get("velocity_nonmonotone_or_floor_limited_rows") == 1,
        "RA2021 nonmonotone/floor-limited count changed",
    )
    for key in [
        "public_order_groups_completed",
        "public_timing_rows_completed",
        "order_summary_rows_ok",
        "timing_rows_ok",
        "fixed_grid_common_reference_rows_present",
        "paper_safe_common_reference_rows_present",
        "source_policy_reproduction_rows_present",
        "source_output_mapping_verified",
        "source_time_grid_policy_extracted",
    ]:
        checks.check(criteria.get(key) is True, f"criterion {key} changed")
    for key in [
        "source_default_horizon_and_h_policy_reproduced",
        "flagged_velocity_mapping_or_floor_issues_resolved",
        "runtime_policy_tied_to_source_policy_order_rows",
        "rerun_or_independent_verification_artifact_present",
    ]:
        checks.check(criteria.get(key) is False, f"criterion {key} unexpectedly closed")
    checks.check(decision.get("can_close_ra2021_b2_requirement_now") is False, "RA2021 B2 requirement overclosed")
    checks.check(
        source_identity_block.get("schema")
        == source_identity.get("schema")
        == "ra2021-source-identity-audit-v1",
        "source-identity audit not carried into RA2021 source-policy audit",
    )
    checks.check(
        source_identity_block.get("output_mapping_verified_from_source") is True,
        "source output mapping not carried into RA2021 audit",
    )
    checks.check(
        source_identity_block.get("time_grid_policy_extracted_from_source") is True,
        "source time-grid policy not carried into RA2021 audit",
    )
    checks.check(
        source_identity_block.get("source_policy_reproduction_rows_closed") == 0,
        "source-identity audit overclosed rows",
    )
    checks.check(
        "verify body.r/body.dr/body.ddr" not in " ".join(decision.get("required_to_close", [])),
        "verified output mapping should not remain in required-to-close list",
    )
    checks.check(
        set(local_feasibility) == {"single_pendulum", "double_pendulum", "four_link", "slider_crank"},
        "local candidate feasibility examples changed",
    )
    checks.check(
        closed_loop_same_window.get("schema")
        == "ra2021-closed-loop-same-window-public-work-precision-evidence-v1",
        "closed-loop same-window evidence schema missing",
    )
    checks.check(
        closed_loop_same_window.get("artifact_present") is True,
        "closed-loop same-window work/precision artifact missing",
    )
    checks.check(
        closed_loop_same_window.get("artifact_status")
        == closed_loop_public_work.get("status")
        == "same_window_public_work_precision_available_reference_caveat_not_external_superiority",
        "closed-loop same-window artifact status changed",
    )
    checks.check(closed_loop_same_window.get("row_count") == closed_loop_public_work.get("row_count") == 24, "closed-loop same-window row count changed")
    checks.check(closed_loop_same_window.get("ok_row_count") == closed_loop_public_work.get("ok_row_count") == 24, "closed-loop same-window ok count changed")
    checks.check(closed_loop_same_window.get("summary_row_count") == closed_loop_public_work.get("summary_row_count") == 8, "closed-loop same-window summary count changed")
    checks.check(
        set(closed_loop_same_window.get("models", [])) == {"four_link", "slider_crank"},
        "closed-loop same-window model set changed",
    )
    checks.check(closed_loop_same_window.get("t_end") == 0.1, "closed-loop same-window T changed")
    checks.check(closed_loop_same_window.get("step_sizes") == [0.1, 0.05, 0.025], "closed-loop same-window h values changed")
    checks.check(closed_loop_same_window.get("reference_h") == 0.0125, "closed-loop same-window reference h changed")
    checks.check(closed_loop_same_window.get("public_forms") == ["rA", "rp", "reps"], "closed-loop same-window public forms changed")
    checks.check(closed_loop_same_window.get("public_work_precision_available_count") == 2, "closed-loop same-window available count changed")
    checks.check(
        set(closed_loop_same_window.get("public_work_precision_available_examples", []))
        == {"four_link", "slider_crank"},
        "closed-loop same-window available examples changed",
    )
    checks.check(closed_loop_same_window.get("public_work_precision_missing_count") == 0, "closed-loop same-window missing count changed")
    checks.check(closed_loop_same_window.get("local_true_dynamic_order_available_count") == 2, "closed-loop same-window local order count changed")
    checks.check(
        closed_loop_same_window.get("strict_common_reference_error_columns") is False,
        "closed-loop same-window overclaims strict common reference",
    )
    checks.check(
        closed_loop_same_window.get("reference_alignment_status") == "mixed_reference_family_requires_manuscript_caveat",
        "closed-loop same-window reference caveat changed",
    )
    checks.check(
        closed_loop_same_window.get("external_superiority_claim") is False,
        "closed-loop same-window overclaims external superiority",
    )
    checks.check(
        closed_loop_same_window.get("accepted_external_dynamic_order_examples") == [],
        "closed-loop same-window unexpectedly accepts external dynamic order examples",
    )
    checks.check(
        closed_loop_same_window.get("counts_as_bounded_same_window_diagnostic") is True,
        "closed-loop same-window diagnostic marker missing",
    )
    checks.check(
        closed_loop_same_window.get("counts_as_source_policy_reproduction") is False,
        "closed-loop same-window overclaims source-policy reproduction",
    )
    checks.check(
        closed_loop_same_window.get("counts_as_external_superiority_evidence") is False,
        "closed-loop same-window overclaims external superiority evidence",
    )
    checks.check(
        closed_loop_same_window.get("source_policy_rows_closed_by_this_evidence") == 0,
        "closed-loop same-window overcloses source-policy rows",
    )
    checks.check(
        closed_loop_same_window.get("b4_b7_can_close_from_this_evidence") is False,
        "closed-loop same-window overcloses B4/B7",
    )
    model_summaries = closed_loop_same_window.get("model_summaries", {})
    checks.check(set(model_summaries) == {"four_link", "slider_crank"}, "closed-loop same-window summary models changed")
    for example, min_vel_order in [("four_link", 6.0), ("slider_crank", 7.0)]:
        model_summary = model_summaries.get(example, {})
        checks.check(model_summary.get("local_summary_present") is True, f"{example} same-window local summary missing")
        checks.check(model_summary.get("public_summary_count") == 3, f"{example} same-window public summary count changed")
        checks.check(
            model_summary.get("public_methods") == ["rA-public-dynamics", "reps-public-dynamics", "rp-public-dynamics"],
            f"{example} same-window public methods changed",
        )
        checks.check(
            isinstance(model_summary.get("local_vel_observed_order"), (int, float))
            and model_summary.get("local_vel_observed_order") > min_vel_order,
            f"{example} same-window local velocity order changed",
        )
        checks.check(
            model_summary.get("external_superiority_claim_allowed") is False,
            f"{example} same-window overclaims external superiority",
        )
    checks.check(promotion_gap.get("checked") is True, "promotion gap drilldown not checked")
    checks.check(promotion_gap.get("examples_checked") == 4, "promotion gap example count changed")
    checks.check(promotion_gap.get("active_rows_checked") == 0, "promotion gap active row count changed")
    checks.check(
        promotion_gap.get("closed_loop_same_window_public_work_precision_checked") is True,
        "promotion gap did not check closed-loop same-window work/precision",
    )
    checks.check(
        set(promotion_gap.get("closed_loop_same_window_public_work_precision_available_examples", []))
        == {"four_link", "slider_crank"},
        "promotion gap same-window available examples changed",
    )
    checks.check(
        promotion_gap.get("closed_loop_same_window_public_work_precision_rows_closed") == 0,
        "promotion gap same-window overcloses rows",
    )
    checks.check(
        promotion_gap.get("closed_loop_same_window_public_work_precision_promotion_closed") is False,
        "promotion gap same-window overcloses promotion",
    )
    checks.check(promotion_gap.get("source_identity_closed") is True, "promotion gap lost source-identity closure")
    checks.check(
        promotion_gap.get("source_policy_promotion_closed") is False,
        "promotion gap unexpectedly closes source-policy promotion",
    )
    checks.check(promotion_gap.get("source_policy_rows_closed") == 0, "promotion gap source rows changed")
    checks.check(promotion_gap.get("external_superiority_ready_rows") == 0, "promotion gap claim rows changed")
    gap_summary = promotion_gap.get("row_level_gap_summary", {})
    checks.check(
        set(gap_summary) == {"single_pendulum", "double_pendulum", "four_link", "slider_crank"},
        "promotion gap summary examples changed",
    )
    per_example_gap = promotion_gap.get("per_example", {})
    checks.check(
        set(per_example_gap) == {"single_pendulum", "double_pendulum", "four_link", "slider_crank"},
        "promotion gap per-example set changed",
    )
    single = local_feasibility.get("single_pendulum", {})
    checks.check(single.get("candidate_rows_exist") is True, "single local public-h candidate rows missing")
    checks.check(single.get("public_policy_h_rows_completed") == 3, "single public h rows changed")
    checks.check(single.get("public_policy_h_rows_required") == 3, "single required public h rows changed")
    checks.check(
        single.get("promotion_status") == "not_promoted_floor_limited_public_h_tranche",
        "single promotion status changed",
    )
    checks.check(single.get("step_sizes") == [0.0001, 0.001, 0.01], "single public-policy h values changed")
    checks.check(isinstance(single.get("velocity_observed_order"), (int, float)), "single velocity order missing")
    single_gap = per_example_gap.get("single_pendulum", {})
    checks.check(single_gap.get("source_policy_step_sizes") == [0.0001, 0.001, 0.01], "single gap h values changed")
    checks.check(single_gap.get("local_candidate_step_sizes") == [0.0001, 0.001, 0.01], "single local gap h values changed")
    checks.check(single_gap.get("source_policy_reference_h") == 0.001, "single gap reference h changed")
    checks.check(single_gap.get("source_policy_contract_satisfied") is False, "single gap overclosed")
    checks.check(
        single_gap.get("promotion_status") == "not_promoted_floor_limited_public_h_tranche",
        "single gap promotion status changed",
    )
    double = local_feasibility.get("double_pendulum", {})
    checks.check(double.get("candidate_rows_exist") is True, "double local coarse candidate rows missing")
    checks.check(double.get("public_policy_h_rows_completed") == 0, "double public h rows unexpectedly closed")
    checks.check(
        double.get("promotion_status") == "not_promoted_coarse_h_and_reference_policy_mismatch",
        "double promotion status changed",
    )
    checks.check(double.get("step_sizes") == [0.025, 0.05, 0.1], "double coarse h values changed")
    checks.check(
        double.get("source_policy_step_sizes_required") == [0.01, 0.002, 0.001],
        "double source-policy h values changed",
    )
    checks.check(
        double.get("reference_h") == 0.0125 and double.get("source_policy_reference_h_required") == 0.0001,
        "double reference policy mismatch marker changed",
    )
    checks.check(
        double.get("isolated_source_policy_candidate_present") is True,
        "double isolated source-policy candidate plan missing",
    )
    checks.check(
        double.get("isolated_source_policy_candidate_status")
        == isolated_double_candidate.get("status")
        == double_source_policy_candidate.get("status"),
        "double isolated candidate status changed",
    )
    checks.check(
        double.get("isolated_source_policy_candidate_status") in allowed_double_candidate_statuses,
        "double isolated candidate status not recognized",
    )
    checks.check(
        double.get("isolated_source_policy_candidate_execution_mode")
        == isolated_double_candidate.get("execution_mode")
        == double_source_policy_candidate.get("execution_mode"),
        "double isolated candidate execution mode changed",
    )
    checks.check(
        double.get("isolated_source_policy_candidate_execution_mode") in {"plan", "plan_only", "reference", "candidate", "all"},
        "double isolated candidate execution mode not recognized",
    )
    checks.check(
        double.get("isolated_source_policy_candidate_contract_selected")
        == isolated_double_candidate.get("source_policy_contract_selected")
        == double_source_policy_candidate.get("source_policy_contract_selected")
        is True,
        "double isolated candidate source-policy contract not selected",
    )
    checks.check(
        double.get("isolated_source_policy_candidate_reference_status")
        == isolated_double_candidate.get("reference_status")
        == double_source_policy_candidate.get("reference_status"),
        "double isolated candidate reference status changed",
    )
    checks.check(
        double.get("isolated_source_policy_candidate_jax_safe_small_angle_patch_enabled")
        == isolated_double_candidate.get("jax_safe_small_angle_patch_enabled")
        == double_source_policy_candidate.get("jax_safe_small_angle_patch_enabled")
        is True,
        "double isolated candidate JAX-safe patch marker missing",
    )
    checks.check(
        double.get("isolated_source_policy_candidate_jax_safe_small_angle_patch_id")
        == isolated_double_candidate.get("jax_safe_small_angle_patch_id")
        == double_source_policy_candidate.get("jax_safe_small_angle_patch_id")
        == "isolated_v013_jax_safe_small_angle_taylor_v1",
        "double isolated candidate JAX-safe patch id changed",
    )
    checks.check(
        double.get("isolated_source_policy_candidate_reference_failure_kind")
        == isolated_double_candidate.get("reference_failure_kind")
        == double_source_policy_candidate.get("reference_failure_kind"),
        "double isolated candidate reference failure kind changed",
    )
    checks.check(
        double.get("isolated_source_policy_candidate_rows") == 3,
        "double isolated candidate row count changed",
    )
    checks.check(
        double.get("isolated_source_policy_candidate_rows_completed")
        == isolated_double_candidate.get("source_policy_candidate_rows_completed")
        == expected_double_candidate_completed,
        "double isolated candidate row-completion count stale",
    )
    checks.check(
        double.get("isolated_source_policy_candidate_low_order_diagnosis_status")
        == isolated_double_low_order.get("status")
        == double_low_order_diagnosis.get("status")
        == "diagnosis_only_low_order_floor_limited_not_promoted",
        "double isolated low-order diagnosis status changed",
    )
    checks.check(
        double.get("isolated_source_policy_candidate_low_order_fine_pair_floor_limited")
        == isolated_double_low_order.get("fine_pair_floor_limited")
        == double_low_order_diagnosis.get("diagnosis", {}).get("fine_pair_floor_limited")
        is True,
        "double isolated low-order fine-pair marker missing",
    )
    checks.check(
        double.get("isolated_source_policy_candidate_low_order_fine_pair_label")
        == isolated_double_low_order.get("fine_pair_label")
        == double_low_order_diagnosis.get("diagnosis", {}).get("fine_pair_label")
        == "0.002_to_0.001",
        "double isolated low-order fine-pair label changed",
    )
    checks.check(
        double.get("isolated_source_policy_candidate_low_order_coarse_h_constraint_threshold_satisfied")
        == isolated_double_low_order.get("coarse_h_constraint_threshold_satisfied")
        == double_low_order_diagnosis.get("diagnosis", {}).get("coarse_h_constraint_threshold_satisfied")
        is False,
        "double isolated low-order coarse-h threshold marker changed",
    )
    checks.check(
        double.get("isolated_source_policy_candidate_low_order_constraint_failure_components")
        == isolated_double_low_order.get("coarse_h_constraint_failure_components")
        == double_low_order_diagnosis.get("diagnosis", {}).get("coarse_h_constraint_failure_components")
        == ["endpoint_velocity_constraint"],
        "double isolated low-order constraint failure component changed",
    )
    checks.check(
        abs(
            float(double.get("isolated_source_policy_candidate_low_order_fine_pair_floor_margin_to_threshold"))
            - float(
                double_low_order_diagnosis.get("diagnosis", {}).get(
                    "fine_pair_floor_margin_to_threshold"
                )
            )
        )
        < 1.0e-12,
        "double isolated low-order fine-pair floor margin stale",
    )
    checks.check(
        double.get("isolated_source_policy_candidate_low_order_finest_to_reference_step_ratio")
        == isolated_double_low_order.get("finest_to_reference_step_ratio")
        == double_low_order_diagnosis.get("diagnosis", {}).get("finest_to_reference_step_ratio")
        == 10.0,
        "double isolated low-order finest/reference ratio changed",
    )
    checks.check(
        double.get("isolated_source_policy_candidate_low_order_reference_floor_sensitivity")
        == isolated_double_low_order.get("reference_floor_sensitivity")
        == double_low_order_diagnosis.get("diagnosis", {}).get("reference_floor_sensitivity")
        == "fine_pair_errors_below_floor_threshold_and_only_ten_reference_steps_per_finest_step",
        "double isolated low-order reference-floor sensitivity changed",
    )
    checks.check(
        double.get("isolated_source_policy_candidate_low_order_rows_promoted")
        == isolated_double_low_order.get("source_policy_rows_promoted_by_this_diagnosis")
        == double_low_order_diagnosis.get("promotion_decision", {}).get(
            "source_policy_rows_promoted_by_this_diagnosis"
        )
        == 0,
        "double isolated low-order diagnosis promoted rows",
    )
    checks.check(
        expected_double_candidate_completed in {0, 1, 2, 3},
        "double isolated candidate row-completion count out of range",
    )
    checks.check(
        double.get("isolated_source_policy_candidate_order_acceptance_satisfied")
        == isolated_double_candidate.get("source_policy_order_acceptance_satisfied")
        == double_source_policy_candidate.get("source_policy_order_acceptance_satisfied"),
        "double isolated candidate order-acceptance marker stale",
    )
    if expected_double_candidate_completed == 3:
        checks.check(
            double_source_policy_candidate.get("source_policy_order_acceptance_satisfied") is False,
            "completed isolated source-policy rows should remain low-order/unaccepted",
        )
        checks.check(
            isinstance(double.get("isolated_source_policy_candidate_pos_observed_order"), (int, float))
            and isinstance(double.get("isolated_source_policy_candidate_vel_observed_order"), (int, float)),
            "double isolated candidate observed orders missing",
        )
    checks.check(
        double.get("isolated_source_policy_candidate_estimated_reference_steps")
        == isolated_double_candidate.get("estimated_reference_steps")
        == double_source_policy_candidate.get("estimated_reference_steps")
        == 30000,
        "double isolated candidate reference-step estimate changed",
    )
    checks.check(
        double.get("isolated_source_policy_candidate_estimated_candidate_steps") == [300, 1500, 3000],
        "double isolated candidate step estimates changed",
    )
    checks.check(
        isolated_double_candidate.get("present") is True,
        "top-level isolated double candidate marker missing",
    )
    checks.check(
        isolated_double_candidate.get("promotion_ready") == double_source_policy_candidate.get("promotion_ready") is False,
        "isolated double candidate overclaims promotion readiness",
    )
    checks.check(
        isolated_double_low_order.get("schema")
        == double_low_order_diagnosis.get("schema")
        == "ra2021-double-source-policy-low-order-diagnosis-v1",
        "top-level isolated double low-order diagnosis schema changed",
    )
    checks.check(
        isolated_double_low_order.get("b4_b7_can_close_from_this_diagnosis")
        == double_low_order_diagnosis.get("promotion_decision", {}).get("b4_b7_can_close_from_this_diagnosis")
        is False,
        "top-level isolated double low-order diagnosis overcloses B4/B7",
    )
    checks.check(
        isolated_double_low_order.get("coarse_h_constraint_failure_components")
        == ["endpoint_velocity_constraint"],
        "top-level isolated double low-order constraint failure component missing",
    )
    checks.check(
        isolated_double_low_order.get("fine_pair_floor_margin_to_threshold") < 0.2,
        "top-level isolated double fine-pair floor margin changed",
    )
    checks.check(
        isolated_double_low_order.get("finest_to_reference_step_ratio") == 10.0,
        "top-level isolated double finest/reference ratio changed",
    )
    checks.check(
        isolated_double_candidate.get("reference_status") == double_source_policy_candidate.get("reference_status"),
        "top-level isolated double candidate reference status stale",
    )
    checks.check(
        isolated_double_candidate.get("jax_safe_small_angle_patch_enabled") is True,
        "top-level isolated double candidate patch marker missing",
    )
    double_gap = per_example_gap.get("double_pendulum", {})
    checks.check(
        double_gap.get("source_policy_step_sizes") == [0.01, 0.002, 0.001],
        "double gap source h values changed",
    )
    checks.check(
        double_gap.get("local_candidate_step_sizes") == [0.025, 0.05, 0.1],
        "double gap local h values changed",
    )
    checks.check(double_gap.get("source_policy_reference_h") == 0.0001, "double gap source reference changed")
    checks.check(double_gap.get("local_candidate_reference_h") == 0.0125, "double gap local reference changed")
    checks.check(double_gap.get("source_policy_contract_satisfied") is False, "double gap overclosed")
    checks.check(
        double_gap.get("isolated_source_policy_candidate_present") is True,
        "double gap isolated candidate marker missing",
    )
    checks.check(
        double_gap.get("isolated_source_policy_candidate_contract_selected") is True,
        "double gap source-policy contract marker missing",
    )
    checks.check(
        double_gap.get("isolated_source_policy_candidate_execution_mode") in {"plan", "plan_only", "reference", "candidate", "all"},
        "double gap execution mode changed",
    )
    checks.check(
        double_gap.get("isolated_source_policy_candidate_rows_completed") == expected_double_candidate_completed,
        "double gap candidate row-completion count stale",
    )
    for example in ["four_link", "slider_crank"]:
        item = local_feasibility.get(example, {})
        checks.check(item.get("candidate_rows_exist") is True, f"{example} true-dynamic candidate rows missing")
        checks.check(item.get("public_policy_h_rows_completed") == 6, f"{example} public h rows changed")
        checks.check(
            item.get("promotion_status")
            == "not_promoted_true_dynamic_not_source_policy_and_public_horizon_not_dynamic_order",
            f"{example} promotion status changed",
        )
        checks.check(item.get("true_dynamic_step_sizes") == [0.025, 0.05, 0.1], f"{example} true dynamic h values changed")
        checks.check(item.get("true_dynamic_t_end") == 0.1, f"{example} true dynamic T changed")
        checks.check(item.get("source_policy_t_end_required") == 3.0, f"{example} source policy T changed")
        checks.check(
            item.get("same_window_public_work_precision_available") is True,
            f"{example} same-window public work/precision marker missing",
        )
        checks.check(
            item.get("same_window_public_work_precision_status")
            == "same_window_public_work_precision_available_reference_caveat_not_external_superiority",
            f"{example} same-window public work/precision status changed",
        )
        checks.check(
            item.get("same_window_public_work_precision_reference_alignment_status")
            == "mixed_reference_family_requires_manuscript_caveat",
            f"{example} same-window reference caveat changed",
        )
        checks.check(
            item.get("same_window_public_work_precision_source_policy_rows_closed") == 0,
            f"{example} same-window overcloses source-policy rows",
        )
        checks.check(
            item.get("same_window_public_work_precision_promotion_status")
            == "diagnostic_only_mixed_reference_family_not_source_policy",
            f"{example} same-window promotion status changed",
        )
        checks.check(
            any("mixed reference families" in str(blocker) for blocker in item.get("promotion_blockers", [])),
            f"{example} same-window mixed-reference blocker missing",
        )
        item_gap = per_example_gap.get(example, {})
        checks.check(item_gap.get("source_policy_t_end") == 3.0, f"{example} gap source T changed")
        checks.check(item_gap.get("local_candidate_t_end") == 0.1, f"{example} gap local T changed")
        checks.check(
            item_gap.get("local_candidate_step_sizes") == [0.025, 0.05, 0.1],
            f"{example} gap local h values changed",
        )
        checks.check(
            item_gap.get("source_policy_contract_satisfied") is False,
            f"{example} gap overclosed",
        )
        checks.check(
            item_gap.get("same_window_public_work_precision_available") is True,
            f"{example} gap same-window marker missing",
        )
        checks.check(
            item_gap.get("same_window_public_work_precision_reference_alignment_status")
            == "mixed_reference_family_requires_manuscript_caveat",
            f"{example} gap same-window caveat changed",
        )
        checks.check(
            item_gap.get("same_window_public_work_precision_source_policy_rows_closed") == 0,
            f"{example} gap same-window overcloses rows",
        )
    for row in rows:
        checks.check(row.get("public_code_replay_present") is True, f"row {row.get('row_index')} lost public replay")
        checks.check(row.get("fixed_grid_replay_used") is True, f"row {row.get('row_index')} lost fixed-grid replay")
        checks.check(row.get("paper_safe_common_reference") is True, f"row {row.get('row_index')} not paper safe")
        checks.check(row.get("source_policy_reproduction") is False, f"row {row.get('row_index')} source-policy closed")
        checks.check(row.get("source_policy_closed") is False, f"row {row.get('row_index')} source-policy closed")
        checks.check(row.get("external_superiority_ready") is False, f"row {row.get('row_index')} claim-ready")
        checks.check("source_policy_not_closed" in row.get("issues", []), f"row {row.get('row_index')} missing issue")
        resolved = row.get("resolved_required_evidence", [])
        remaining = row.get("remaining_required_evidence", [])
        checks.check(row.get("resolved_required_evidence_count") == len(resolved) == 3, f"row {row.get('row_index')} resolved evidence count changed")
        checks.check(row.get("remaining_required_evidence_count") == len(remaining) == 4, f"row {row.get('row_index')} remaining evidence count changed")
        joined_remaining = " ".join(str(item) for item in remaining)
        checks.check("public code path" not in joined_remaining, f"row {row.get('row_index')} keeps resolved public code path evidence open")
        checks.check("body.r/body.dr/body.ddr" not in joined_remaining, f"row {row.get('row_index')} keeps resolved output mapping evidence open")
        checks.check("time-grid convention" not in joined_remaining, f"row {row.get('row_index')} keeps resolved time-grid extraction open")
        checks.check(
            any("local Gauss6 FullVA row" in str(item) for item in remaining),
            f"row {row.get('row_index')} missing local promotion evidence requirement",
        )
        checks.check(
            isinstance(row.get("local_candidate_promotion_blockers"), list)
            and len(row.get("local_candidate_promotion_blockers")) >= 2,
            f"row {row.get('row_index')} missing local candidate blockers",
        )
        checks.check(
            str(row.get("local_candidate_promotion_status", "")).startswith("not_promoted_"),
            f"row {row.get('row_index')} local candidate status changed",
        )

    execution = audit.get("execution_policy", {})
    checks.check(execution.get("default_1e_4_required") is False, "audit requires default 1e-4")
    checks.check(execution.get("heavy_numerical_run_invoked") is False, "audit invoked heavy run")
    checks.check(execution.get("run_v047_invoked") is False, "audit invoked run_v047")
    checks.check(execution.get("v048_runner_invoked") is False, "audit invoked v048 runner")

    for token in [
        "Status: **public rows complete; source-policy rows not closed**.",
        "Active B2 flagged RA2021 rows: `0`.",
        "Public order groups completed: `12/12`.",
        "Public timing rows completed: `12/12`.",
        "Fixed-grid common-reference RA2021 rows: `12/12`.",
        "Paper-safe common-reference RA2021 rows: `12/12`.",
        "Source-policy reproduction rows: `0/12`.",
        "Per-row source-identity requirements resolved: `3`.",
        "Per-row source-policy promotion requirements remaining: `4`.",
        "Row missing evidence shrunk by identity audit: `True`.",
        "Source-policy closed rows: `0`.",
        "External-superiority-ready rows: `0`.",
        "Source output mapping verified from RA2021 source: `True`.",
        "Source time-grid policy extracted from RA2021 source: `True`.",
        "Closed-loop same-window public work/precision:",
        "available `2/2`",
        "strict common-reference `False`",
        "external superiority `False`",
        "source-policy rows closed `0`",
        "Can close RA2021 B2 requirement now: `False`.",
        "## Promotion Gap Drilldown",
        "Checked examples: `4`.",
        "Checked active B2 rows: `0`.",
        "Closed-loop same-window public work/precision checked: `True`.",
        "Closed-loop same-window source-policy rows closed: `0`.",
        "Source identity closed: `True`.",
        "Source-policy promotion closed: `False`.",
        "floor-limited public-h tranche",
        "coarse h/reference-policy rows",
        "mixed-reference diagnostic, not source-policy promotion",
        "bounded same-window public work/precision available, but mixed-reference diagnostic only",
        "## Local Candidate Feasibility",
        "`not_promoted_floor_limited_public_h_tranche`",
        "`not_promoted_coarse_h_and_reference_policy_mismatch`",
        "`not_promoted_true_dynamic_not_source_policy_and_public_horizon_not_dynamic_order`",
        "plus isolated exact candidate",
        "Isolated double low-order diagnosis:",
        "fine pair floor-limited `True`",
        "coarse h constraint threshold `False`",
        "constraint failure components `['endpoint_velocity_constraint']`",
        "fine-pair floor margin `0.176`",
        "finest/reference h ratio `10.0`",
        "rows promoted `0`",
        "plus same-window public work/precision",
        "isolated exact rows",
        "Each active RA2021 row now carries the resolved source-identity evidence separately from the still-open promotion evidence.",
        "The RA2021 rows remain bounded common-reference diagnostics, not external-superiority evidence.",
        "The previous output-mapping unknown is closed as a source-identity question; source-policy promotion remains open.",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")
    candidate_md_token = (
        "Isolated double source-policy candidate plan: "
        f"`{double_source_policy_candidate.get('status')}`, "
        "contract `True`, "
        f"reference `{double_source_policy_candidate.get('reference_status')}`, "
        "JAX-safe small-angle patch `True`, "
        f"rows completed `{expected_double_candidate_completed}/3`, "
        f"order accepted `{double_source_policy_candidate.get('source_policy_order_acceptance_satisfied')}`, "
        "estimated reference steps `30000`."
    )
    checks.check(candidate_md_token in audit_md, "markdown isolated double candidate line stale")
    if expected_double_candidate_completed == 3:
        checks.check("observed order is below acceptance" in audit_md, "markdown missing low-order promotion blocker")

    if checks.errors:
        print("RA2021 source-policy row audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("RA2021 source-policy row audit validation: PASS")
    print("active_b2_flagged_rows=0")
    print("public_order_groups=12/12")
    print("public_timing_rows=12/12")
    print("source_policy_reproduction_rows=0/12")
    print("can_close_ra2021_b2_requirement_now=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
