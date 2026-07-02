#!/usr/bin/env python3
"""Validate the B4 source-policy post-execution audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
EXPECTED_SAFE_ACTION_IDS = [
    "rebuild_read_only_audit_chain",
    "rerun_read_only_validators",
    "keep_narrowed_archive_provenance_only",
    "monitor_reopen_conditions",
]
EXPECTED_OPT_IN_ACTION_IDS = ["authorized_b4_ra_hi_source_policy_execution"]
EXPECTED_APPROVAL = (
    "I explicitly approve running the B4 source-policy execution commands listed in "
    "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json."
)
EXPECTED_DRIVER = "run_b4_source_policy_after_opt_in.sh"


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
        audit = read_json(PAPER / "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.json")
        audit_md = read_text(PAPER / "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.md")
        b4 = read_json(PAPER / "B4_SOURCE_POLICY_WORK_PRECISION_EXECUTION_PLAN.json")
        existing_promotion = read_json(PAPER / "B4_EXISTING_ARTIFACT_PROMOTION_AUDIT.json")
        row_ledger = read_json(PAPER / "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.json")
        packet = read_json(PAPER / "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json")
        review = read_json(PAPER / "CMAME_REVIEW_AGENT_REPORT.json")
        ra2021_double_low_order = read_json(PAPER / "RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.json")
        hi2022_ra_half_double_failure = read_json(
            PAPER / "HI2022_RA_HALF_DOUBLE_SOURCE_POLICY_FAILURE_DIAGNOSIS.json"
        )
    except Exception as exc:  # noqa: BLE001
        print(f"b4 source-policy post-execution audit validation: FAIL\n- {exc}")
        return 1

    current = b4.get("current_evidence", {})
    evidence = audit.get("post_execution_artifact_evidence", {})
    row_status = audit.get("row_status_after_driver", {})
    command_presence = audit.get("command_artifact_presence", {})
    promotion = audit.get("promotion_decision", {})
    post_summary = audit.get("post_execution_summary", {})
    packet_semantics = audit.get("packet_semantics", {})
    guarded_driver = audit.get("guarded_driver", {})
    review_status = audit.get("review_agent_status_after_driver", {})
    shards = evidence.get("public_closed_loop_shards", {})
    low_order_diagnosis = ra2021_double_low_order.get("diagnosis", {})
    low_order_promotion = ra2021_double_low_order.get("promotion_decision", {})
    hi_failure_evidence = hi2022_ra_half_double_failure.get("execution_evidence", {})
    hi_failure_diagnosis = hi2022_ra_half_double_failure.get("diagnosis", {})
    hi_failure_promotion = hi2022_ra_half_double_failure.get("promotion_decision", {})
    authorized = audit.get("verified_authorized_execution_recorded") is True
    expected_status = (
        "verified_authorized_driver_execution_recorded_no_source_policy_rows_promoted"
        if authorized
        else "existing_outputs_present_no_verified_authorized_execution_no_source_policy_rows_promoted"
    )
    expected_scope = (
        "verified_authorized_guarded_driver_execution"
        if authorized
        else "no_verified_current_authorized_execution_record_existing_artifacts_only"
    )
    expected_verified_commands = 13 if authorized else 0

    checks.check(audit.get("schema") == "b4-source-policy-post-execution-audit-v1", "schema changed")
    checks.check(audit.get("status") == expected_status, "status changed")
    checks.check(audit.get("read_only") is True, "audit should be read-only")
    checks.check(
        audit.get("approved_driver_execution_recorded") is authorized,
        "approved driver execution marker inconsistent",
    )
    checks.check(
        audit.get("verified_authorized_execution_recorded") is authorized,
        "verified authorized execution marker inconsistent",
    )
    checks.check(
        audit.get("approval_statement_matched") is authorized,
        "approval statement match marker inconsistent",
    )
    checks.check(
        audit.get("execution_authorized") is authorized,
        "execution_authorized alias inconsistent",
    )
    checks.check(audit.get("commands_executed_by_audit") is False, "audit executed commands")
    checks.check(
        audit.get("source_policy_execution_invoked") is authorized,
        "source-policy execution alias inconsistent",
    )
    checks.check(
        audit.get("source_policy_execution_allowed_now") is False,
        "audit allows source-policy execution without opt-in",
    )
    checks.check(
        audit.get("exact_b4_opt_in_required_for_execution") is True,
        "audit lost exact B4 opt-in requirement",
    )
    checks.check(
        audit.get("required_user_approval_statement") == EXPECTED_APPROVAL,
        "audit exact approval statement missing or stale",
    )
    checks.check(
        audit.get("guarded_execution_driver") == EXPECTED_DRIVER,
        "audit guarded driver alias missing or stale",
    )
    checks.check(audit.get("safe_action_ids") == EXPECTED_SAFE_ACTION_IDS, "safe action ids changed")
    checks.check(audit.get("opt_in_action_ids") == EXPECTED_OPT_IN_ACTION_IDS, "opt-in action ids changed")
    checks.check(
        audit.get("next_safe_action_ids") == audit.get("safe_action_ids") == EXPECTED_SAFE_ACTION_IDS,
        "next safe action ids stale",
    )
    checks.check(
        [item.get("id") for item in audit.get("next_safe_actions", [])]
        == EXPECTED_SAFE_ACTION_IDS,
        "next safe actions stale",
    )
    checks.check(
        audit.get("existing_ready_command_artifacts_present") is True,
        "existing ready-command artifacts should be present",
    )
    checks.check(audit.get("execution_record_scope") == expected_scope, "execution record scope changed")
    checks.check(audit.get("heavy_numerical_run_invoked_by_this_builder") is False, "builder invoked heavy run")
    checks.check(audit.get("run_v047_invoked_by_this_builder") is False, "builder invoked run_v047")
    checks.check(audit.get("v048_runner_invoked_by_this_builder") is False, "builder invoked v048 runner")
    checks.check(audit.get("source_policy_rows_closed") == 0, "top-level source-policy rows overclosed")
    checks.check(audit.get("source_policy_rows_promoted") == 0, "top-level source-policy rows overpromoted")
    checks.check(audit.get("source_policy_closed_ratio") == "0/40", "top-level source-policy ratio changed")
    checks.check(audit.get("source_policy_total_rows") == 40, "top-level source-policy total changed")
    checks.check(audit.get("source_policy_rows_unclosed") == 40, "top-level unclosed source-policy rows changed")
    checks.check(audit.get("source_policy_rows_open") == 20, "top-level open source-policy rows changed")
    checks.check(
        audit.get("source_policy_rows_attempted_not_reproducible") == 20,
        "top-level attempted-not-reproducible rows changed",
    )
    checks.check(
        audit.get("source_policy_rows_still_requiring_execution_or_promotion") == 20,
        "top-level still-requiring-execution rows changed",
    )
    checks.check(audit.get("b4_can_close_now") is False, "top-level B4 closure overclaimed")
    checks.check(audit.get("b7_can_close_now") is False, "top-level B7 closure overclaimed")
    checks.check(audit.get("external_superiority_claim_allowed") is False, "top-level superiority overclaimed")
    checks.check(
        post_summary.get("approved_driver_execution_recorded") is authorized
        and post_summary.get("verified_authorized_execution_recorded") is authorized,
        "post-execution summary authorization markers inconsistent",
    )
    checks.check(
        post_summary.get("existing_ready_command_artifacts_present") is True,
        "post-execution summary lost artifact presence",
    )
    checks.check(
        post_summary.get("ready_commands_in_packet") == 13
        and post_summary.get("ready_commands_verified_executed_by_this_record") == expected_verified_commands
        and post_summary.get("ready_command_mapped_external_rows") == 20
        and post_summary.get("unaddressed_external_rows_after_ready_commands") == 0
        and post_summary.get("source_policy_rows_attempted_not_reproducible") == 20
        and post_summary.get("source_policy_rows_still_requiring_execution_or_promotion") == 20,
        "post-execution summary command/row counts changed",
    )
    checks.check(
        post_summary.get("source_policy_rows_promoted_after_driver") == 0
        and post_summary.get("source_policy_rows_total") == 40,
        "post-execution summary promotion rows changed",
    )
    checks.check(
        post_summary.get("b4_can_close_now") is False and post_summary.get("b7_can_close_now") is False,
        "post-execution summary overcloses B4/B7",
    )

    checks.check(guarded_driver.get("path") == "run_b4_source_policy_after_opt_in.sh", "guarded driver path changed")
    checks.check(guarded_driver.get("exists") is True, "guarded driver missing")
    checks.check(
        guarded_driver.get("ready_command_count") == packet.get("ready_command_count") == 13,
        "ready command count changed",
    )
    checks.check(
        guarded_driver.get("ready_command_batch_count") == packet.get("ready_command_batch_count") == 2,
        "ready batch count changed",
    )
    checks.check(
        guarded_driver.get("ready_command_mapped_external_rows")
        == packet.get("ready_command_mapped_external_rows")
        == 20,
        "ready mapped row count changed",
    )
    checks.check(
        guarded_driver.get("unaddressed_external_rows_after_ready_commands")
        == packet.get("unaddressed_external_rows_after_ready_commands")
        == 0,
        "unaddressed row count changed",
    )
    checks.check(
        packet_semantics.get("packet_status")
        == packet.get("status")
        == "ready_for_user_opt_in_packet_not_authorized_not_run",
        "packet status changed",
    )
    checks.check(packet_semantics.get("execution_invoked_by_packet") is False, "packet semantics overclaim execution")
    checks.check(
        "pre-execution guard" in packet_semantics.get("note", "")
        and "exact approval statement" in packet_semantics.get("note", ""),
        "packet semantics note missing",
    )

    checks.check(command_presence.get("command_count") == 13, "command presence count changed")
    checks.check(command_presence.get("all_expected_outputs_exist_now") is True, "expected command output missing")
    checks.check(command_presence.get("expected_output_missing_command_ids") == [], "expected output missing list nonempty")
    checks.check(command_presence.get("all_expected_summaries_exist_now") is True, "expected command summary missing")
    checks.check(command_presence.get("expected_summary_missing_command_ids") == [], "expected summary missing list nonempty")

    checks.check(
        evidence.get("ra2021_public_baseline_progress", {}).get("order_groups_completed") == 12,
        "RA2021 public order groups changed",
    )
    checks.check(
        evidence.get("ra2021_public_baseline_progress", {}).get("timing_rows_completed") == 12,
        "RA2021 public timing rows changed",
    )
    checks.check(
        evidence.get("ra2021_public_baseline_shards_status")
        == "all_public_baseline_source_policy_shards_completed_not_promoted",
        "RA2021 public shard status changed",
    )
    checks.check(evidence.get("ra2021_public_baseline_shards_ok_rows") == 9, "RA2021 public shard row count changed")
    checks.check(
        evidence.get("ra2021_double_local_candidate_status") == "executed_order_below_acceptance_not_promoted",
        "RA2021 double candidate status changed",
    )
    checks.check(evidence.get("ra2021_double_local_candidate_rows") == 3, "RA2021 double candidate rows changed")
    checks.check(
        evidence.get("ra2021_double_local_candidate_order_acceptance_satisfied") is False,
        "RA2021 double candidate acceptance overclaimed",
    )
    checks.check(
        evidence.get("ra2021_double_low_order_diagnosis_status")
        == ra2021_double_low_order.get("status")
        == "diagnosis_only_low_order_floor_limited_not_promoted",
        "RA2021 double low-order diagnosis status changed",
    )
    checks.check(
        evidence.get("ra2021_double_low_order_fine_pair_floor_limited")
        == low_order_diagnosis.get("fine_pair_floor_limited")
        is True,
        "RA2021 double fine-pair floor marker missing",
    )
    checks.check(
        evidence.get("ra2021_double_low_order_fine_pair_label")
        == low_order_diagnosis.get("fine_pair_label")
        == "0.002_to_0.001",
        "RA2021 double fine-pair label changed",
    )
    checks.check(
        evidence.get("ra2021_double_low_order_coarse_h_constraint_threshold_satisfied")
        == low_order_diagnosis.get("coarse_h_constraint_threshold_satisfied")
        is False,
        "RA2021 double coarse-h constraint marker changed",
    )
    checks.check(
        evidence.get("ra2021_double_low_order_constraint_failure_components")
        == low_order_diagnosis.get("coarse_h_constraint_failure_components")
        == ["endpoint_velocity_constraint"],
        "RA2021 double constraint failure component changed",
    )
    checks.check(
        abs(
            float(evidence.get("ra2021_double_low_order_fine_pair_floor_margin_to_threshold"))
            - float(low_order_diagnosis.get("fine_pair_floor_margin_to_threshold"))
        )
        < 1.0e-12,
        "RA2021 double fine-pair floor margin changed",
    )
    checks.check(
        evidence.get("ra2021_double_low_order_finest_to_reference_step_ratio")
        == low_order_diagnosis.get("finest_to_reference_step_ratio")
        == 10.0,
        "RA2021 double finest/reference ratio changed",
    )
    checks.check(
        evidence.get("ra2021_double_low_order_accepted_binding_closed")
        == ra2021_double_low_order.get("ledger_binding_reconciliation", {}).get(
            "accepted_source_policy_binding_closed"
        )
        is False,
        "RA2021 double accepted binding overclaimed",
    )
    checks.check(
        evidence.get("ra2021_double_low_order_local_metrics_present")
        == ra2021_double_low_order.get("ledger_binding_reconciliation", {}).get(
            "candidate_local_error_runtime_newton_columns_present"
        )
        is True,
        "RA2021 double local metric presence marker missing",
    )
    checks.check(
        evidence.get("ra2021_double_low_order_rows_promoted_by_diagnosis")
        == low_order_promotion.get("source_policy_rows_promoted_by_this_diagnosis")
        == 0,
        "RA2021 double low-order diagnosis promoted rows",
    )
    checks.check(
        evidence.get("ra2021_double_low_order_b4_b7_can_close")
        == low_order_promotion.get("b4_b7_can_close_from_this_diagnosis")
        is False,
        "RA2021 double low-order diagnosis overcloses B4/B7",
    )
    checks.check(
        evidence.get("gauss6_local_status")
        == "partial_local_source_policy_evidence_single_complete_closed_loop_residual_only_not_promoted",
        "Gauss6 local status changed",
    )
    checks.check(evidence.get("gauss6_single_public_horizon_step_trio_completed") is True, "Gauss6 single trio changed")
    checks.check(
        evidence.get("gauss6_closed_loop_public_step_trios_completed") is True,
        "Gauss6 closed-loop latest public trios should be complete",
    )
    checks.check(
        evidence.get("gauss6_closed_loop_rows_are_dynamic_work_precision") is False,
        "Gauss6 closed-loop rows overclaimed as dynamic work/precision",
    )
    checks.check(
        evidence.get("public_closed_loop_trios_completed_by_latest_driver_outputs") is True,
        "latest public closed-loop trios missing",
    )
    for model in ["four_link", "slider_crank"]:
        checks.check(shards.get(model, {}).get("row_count") == 3, f"{model} public closed-loop row count changed")
        checks.check(shards.get(model, {}).get("ok_row_count") == 3, f"{model} public closed-loop ok count changed")
    checks.check(
        evidence.get("hi2022_selected_candidate_status") == "selected_candidate_matrix_partially_executed_not_promoted",
        "HI2022 selected candidate status changed",
    )
    checks.check(evidence.get("hi2022_selected_candidate_completed_shards") == 7, "HI2022 completed shard count changed")
    checks.check(evidence.get("hi2022_selected_candidate_expected_shards") == 8, "HI2022 expected shard count changed")
    checks.check(
        evidence.get("hi2022_selected_candidate_partial_or_failed_shards") == ["rA_half:double_pendulum"],
        "HI2022 partial shard list changed",
    )
    checks.check(evidence.get("hi2022_selected_candidate_rows_ok") == 22, "HI2022 ok rows changed")
    checks.check(evidence.get("hi2022_selected_candidate_rows_total") == 24, "HI2022 total rows changed")
    checks.check(evidence.get("hi2022_full_t8_policy_completed") is False, "HI2022 full T8 policy overclaimed")
    checks.check(evidence.get("hi2022_full_public_grid_selected") is False, "HI2022 full public grid overclaimed")
    checks.check(
        evidence.get("hi2022_ra_half_double_failure_diagnosis_status")
        == hi2022_ra_half_double_failure.get("status")
        == "diagnosis_only_partial_newton_failure_not_promoted",
        "HI2022 rA_half double failure diagnosis status changed",
    )
    checks.check(
        evidence.get("hi2022_ra_half_double_failure_rows_ok") == hi_failure_evidence.get("ok_row_count") == 1,
        "HI2022 rA_half double ok-row count changed",
    )
    checks.check(
        evidence.get("hi2022_ra_half_double_failure_rows_failed")
        == hi_failure_evidence.get("failed_row_count")
        == 2,
        "HI2022 rA_half double failed-row count changed",
    )
    checks.check(
        evidence.get("hi2022_ra_half_double_failure_rows_total") == hi_failure_evidence.get("row_count") == 3,
        "HI2022 rA_half double row count changed",
    )
    checks.check(
        evidence.get("hi2022_ra_half_double_failure_newton_failure_count")
        == hi_failure_diagnosis.get("newton_failure_count")
        == 2,
        "HI2022 rA_half double Newton failure count changed",
    )
    checks.check(
        evidence.get("hi2022_ra_half_double_failure_pair_orders_available")
        == hi_failure_diagnosis.get("pair_orders_available")
        is False,
        "HI2022 rA_half double pair-order marker overclaimed",
    )
    checks.check(
        evidence.get("hi2022_ra_half_double_failure_rows_promoted_by_diagnosis")
        == hi_failure_promotion.get("source_policy_rows_promoted_by_this_diagnosis")
        == 0,
        "HI2022 rA_half double failure diagnosis promoted rows",
    )
    checks.check(
        evidence.get("hi2022_ra_half_double_failure_b4_b7_can_close")
        == hi_failure_promotion.get("b4_b7_can_close_from_this_diagnosis")
        is False,
        "HI2022 rA_half double failure diagnosis overcloses B4/B7",
    )
    checks.check(
        evidence.get("hi2022_figure_scope_demotion_status") == "demote_hi2022_from_b4_b7_source_policy_figures",
        "HI2022 demotion status changed",
    )
    checks.check(
        evidence.get("tfe_runner_equivalence_status") == "preflight_ready_runner_equivalence_open",
        "TFE runner-equivalence status changed",
    )
    checks.check(evidence.get("tfe_runner_equivalence_open_blocker_count") == 6, "TFE open blocker count changed")

    checks.check(
        row_status.get("source_policy_rows_closed")
        == row_ledger.get("source_policy_rows_closed")
        == current.get("source_policy_rows_closed")
        == 0,
        "source-policy rows overclosed",
    )
    checks.check(row_status.get("source_policy_rows_total") == row_ledger.get("row_count") == 40, "source-policy total changed")
    checks.check(
        row_status.get("source_policy_rows_unclosed") == row_ledger.get("source_policy_rows_unclosed") == 40,
        "unclosed rows changed",
    )
    checks.check(
        row_status.get("source_policy_rows_open") == row_ledger.get("source_policy_rows_open") == 20,
        "open rows changed",
    )
    checks.check(
        row_status.get("source_policy_rows_attempted_not_reproducible")
        == row_ledger.get("source_policy_rows_attempted_not_reproducible")
        == 20,
        "attempted-not-reproducible rows changed",
    )
    checks.check(
        row_status.get("source_policy_rows_still_requiring_execution_or_promotion")
        == row_ledger.get("source_policy_rows_still_requiring_execution_or_promotion")
        == 20,
        "still-requiring-execution rows changed",
    )
    checks.check(row_status.get("rows_with_launch_command_refs") == 20, "launch-command mapped rows changed")
    checks.check(row_status.get("rows_without_launch_command_refs") == 20, "rows without commands changed")
    checks.check(
        row_status.get("rows_without_launch_command_refs_attempted_not_reproducible") == 20,
        "attempted no-command rows changed",
    )
    checks.check(row_status.get("b4_can_close_now") is False, "audit overcloses B4")
    checks.check(row_status.get("b7_can_close_now") is False, "audit overcloses B7")

    checks.check(
        promotion.get("source_policy_rows_closed_by_existing_artifacts")
        == existing_promotion.get("source_policy_rows_closed_by_existing_artifacts")
        == 0,
        "existing promotion rows changed",
    )
    checks.check(promotion.get("existing_artifact_promotion_ready_count") == 0, "existing promotion ready count changed")
    checks.check(promotion.get("source_policy_rows_closed_after_driver") == 0, "driver promoted rows unexpectedly")
    checks.check(promotion.get("source_policy_rows_total") == 40, "promotion total changed")
    checks.check(promotion.get("b4_can_close_now") is False, "promotion overcloses B4")
    checks.check(promotion.get("b7_can_close_now") is False, "promotion overcloses B7")
    checks.check(promotion.get("external_superiority_claim_allowed") is False, "external superiority overclaimed")
    promotion_reason = str(promotion.get("reason", ""))
    stale_unapproved_reason = "When no exact approval statement is supplied"
    if authorized:
        checks.check(
            stale_unapproved_reason not in promotion_reason
            and stale_unapproved_reason not in json.dumps(audit, sort_keys=True),
            "authorized B4 audit has stale unapproved-execution promotion reason",
        )
        checks.check(
            "guarded driver was run with the exact approval statement" in promotion_reason
            and "not row promotion" in promotion_reason,
            "authorized B4 audit missing verified-execution/nonpromotion reason",
        )
    checks.check(
        review_status.get("submission_standard_scope")
        == review.get("submission_standard_scope")
        == "global_submission_standard",
        "review scope changed",
    )
    checks.check(
        review_status.get("submission_standard_met") is review.get("submission_standard_met") is False,
        "global review submission standard changed",
    )
    checks.check(
        review_status.get("global_submission_standard_met")
        is review.get("global_submission_standard_met")
        is False,
        "global review standard changed",
    )
    checks.check(
        review_status.get("decision") == review.get("decision") == "do_not_submit_global",
        "global review decision changed",
    )
    checks.check(
        review_status.get("open_blockers") == review.get("open_blockers") == ["OC4", "OC6", "OC12"],
        "global review blockers changed",
    )
    checks.check(
        review_status.get("cmame_blocker_gate_open_blocker_count")
        == review.get("cmame_blocker_gate_open_blocker_count")
        == 0,
        "narrowed CMAME blocker-gate count changed",
    )
    checks.check(
        review_status.get("cmame_blocker_gate_open_blockers")
        == review.get("cmame_blocker_gate_open_blockers")
        == [],
        "narrowed CMAME blocker-gate blockers changed",
    )
    checks.check(
        review_status.get("narrowed_submission_standard_met")
        is review.get("narrowed_submission_standard_met")
        is True,
        "narrowed review submission standard changed",
    )
    checks.check(
        review_status.get("narrowed_claim_decision")
        == review.get("narrowed_claim_decision")
        == "submit_under_narrowed_claim",
        "narrowed review decision changed",
    )

    for token in [
        f"Status: `{expected_status}`.",
        f"Verified authorized execution recorded: `{authorized}`.",
        "Existing ready-command artifacts present: `True`.",
        f"Execution record scope: `{expected_scope}`.",
        f"Source-policy execution allowed now/invoked/exact opt-in required: `False/{authorized}/True`.",
        "Safe action ids: `rebuild_read_only_audit_chain,rerun_read_only_validators,keep_narrowed_archive_provenance_only,monitor_reopen_conditions`.",
        "Opt-in action ids: `authorized_b4_ra_hi_source_policy_execution`.",
        "Required approval/driver: `I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json./run_b4_source_policy_after_opt_in.sh`.",
        "Ready commands in packet/mapped rows: `13` / `20`.",
        f"Ready commands verified executed by this record: `{expected_verified_commands}`.",
        "Unaddressed rows after ready commands: `0`.",
        "Attempted-not-reproducible rows: `20`.",
        "Rows still requiring execution/promotion: `20`.",
        "Expected outputs present: `True`.",
        "Source-policy rows closed: `0/40`.",
        "B4/B7 can close now: `False/False`.",
        "Top-level post-execution summary rows/B4/B7: `0/40` / `False/False`.",
        "Global review agent: `do_not_submit_global` with blockers `['OC4', 'OC6', 'OC12']`.",
        "Bounded narrowed subcheck disposition: `bounded_subcheck_satisfied_not_global_submit`; deprecated compatibility decision alias `submit_under_narrowed_claim` retained for validators only, not as a submit instruction; bounded subcheck marker `True`; CMAME blocker-gate blockers `[]`.",
        "This audit records OC4 post-execution state. It does not close the global objective blockers.",
        "blocker_open_by_id=OC4:True,OC6:True,OC12:True",
        "blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready",
        "blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False",
        "RA2021 double local candidate: `executed_order_below_acceptance_not_promoted`",
        "RA2021 double low-order diagnosis: `diagnosis_only_low_order_floor_limited_not_promoted`; fine pair floor-limited `True`; rows promoted `0`.",
        "RA2021 double low-order binding: constraint components `['endpoint_velocity_constraint']`; floor margin `0.176`; finest/reference h ratio `10.0`; accepted binding `False`.",
        "HI2022 selected candidate: `selected_candidate_matrix_partially_executed_not_promoted`; shards `7/8`; partial `['rA_half:double_pendulum']`.",
        "HI2022 rA_half double failure diagnosis: `diagnosis_only_partial_newton_failure_not_promoted`; ok/failed/total `1/2/3`; Newton failures `2`; rows promoted `0`.",
        "Nonpublic-code self-reproduction disposition: attempted-not-reproducible `20`; still requiring execution/promotion `20`.",
        "Source-policy rows promoted by current verified execution/artifact state: `0/40`.",
        "B4/B7 remain open because artifact presence or authorized execution is not row promotion; rows promote only after the source-policy row audits close.",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("b4 source-policy post-execution audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("b4 source-policy post-execution audit validation: PASS")
    print(f"verified_authorized_execution_recorded={authorized}")
    print(f"source_policy_execution_invoked={authorized}")
    print("source_policy_execution_allowed_now=False")
    print("existing_ready_command_artifacts_present=True")
    print("source_policy_rows_closed=0/40")
    print("b4_can_close_now=False")
    print("b7_can_close_now=False")
    print("blocker_open_by_id=OC4:True,OC6:True,OC12:True")
    print("blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
