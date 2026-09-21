#!/usr/bin/env python3
"""Build a B4 source-policy post-execution/readiness audit.

The opt-in packet is intentionally a pre-execution guard. This audit is the
separate artifact-state record: it can record a verified authorized guarded
driver run only when the exact approval statement is supplied. Otherwise it
records existing output presence without treating those files as a verified
current authorized execution.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
OUT_JSON = PAPER / "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.json"
OUT_MD = PAPER / "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.md"
APPROVAL_REQUIRED = (
    "I explicitly approve running the B4 source-policy execution commands listed in "
    "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json."
)
SAFE_ACTIONS_WITHOUT_B4_OPT_IN = [
    {
        "id": "rebuild_read_only_audit_chain",
        "description": "Rebuild this post-execution audit plus downstream RA/HI, objective, review, and package manifests.",
    },
    {
        "id": "rerun_read_only_validators",
        "description": "Rerun validators that only read artifacts and do not execute B4 source-policy commands.",
    },
    {
        "id": "keep_narrowed_archive_provenance_only",
        "description": "Keep narrowed archive artifacts marked as provenance-only, not as a full source-policy runner archive.",
    },
    {
        "id": "monitor_reopen_conditions",
        "description": "Monitor for new public code, author-provided code, or source-equivalent artifacts before reopening rows.",
    },
]
SAFE_ACTION_IDS = [item["id"] for item in SAFE_ACTIONS_WITHOUT_B4_OPT_IN]
OPT_IN_ACTION_IDS = ["authorized_b4_ra_hi_source_policy_execution"]


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def resolve_artifact(path_label: str | None) -> Path | None:
    if not path_label:
        return None
    if path_label.startswith("../"):
        return (manuscript_path(path_label)).resolve()
    return manuscript_path(path_label)


def read_csv_rows(path_label: str) -> list[dict[str, str]]:
    path = resolve_artifact(path_label)
    if path is None or not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def csv_summary(path_label: str) -> dict[str, Any]:
    rows = read_csv_rows(path_label)
    status_counts = Counter(row.get("status", "") for row in rows)
    return {
        "path": path_label,
        "exists": bool(rows),
        "row_count": len(rows),
        "ok_row_count": status_counts.get("ok", 0),
        "status_counts": dict(sorted(status_counts.items())),
    }


def iter_packet_commands(packet: dict[str, Any]) -> list[dict[str, Any]]:
    commands: list[dict[str, Any]] = []
    for batch in packet.get("execution_batches", []):
        if not isinstance(batch, dict):
            continue
        for command in batch.get("commands", []):
            if isinstance(command, dict):
                commands.append(command)
    return commands


def command_presence(command: dict[str, Any]) -> dict[str, Any]:
    output_label = command.get("expected_output_after_run")
    summary_label = command.get("expected_summary_after_run")
    output_path = resolve_artifact(output_label)
    summary_path = resolve_artifact(summary_label)
    preflight = command.get("execution_preflight", {})
    return {
        "id": command.get("id"),
        "mapped_row_count": command.get("mapped_row_count"),
        "packet_artifact_status": command.get("artifact_status"),
        "parse_ok": preflight.get("parse_ok"),
        "runner_script": preflight.get("runner_script"),
        "expected_output_after_run": output_label,
        "expected_output_exists_now": (
            output_path.exists() and output_path.stat().st_size > 0 if output_path is not None else None
        ),
        "expected_summary_after_run": summary_label,
        "expected_summary_exists_now": (
            summary_path.exists() and summary_path.stat().st_size > 0 if summary_path is not None else None
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--record-approved-driver-execution",
        default="",
        help="Exact B4 approval statement used by the guarded driver.",
    )
    args = parser.parse_args()
    verified_authorized_execution_recorded = args.record_approved_driver_execution == APPROVAL_REQUIRED

    b4 = read_json(PAPER / "B4_SOURCE_POLICY_WORK_PRECISION_EXECUTION_PLAN.json")
    existing_promotion = read_json(PAPER / "B4_EXISTING_ARTIFACT_PROMOTION_AUDIT.json")
    row_ledger = read_json(PAPER / "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.json")
    packet = read_json(PAPER / "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json")
    review = read_json(PAPER / "CMAME_REVIEW_AGENT_REPORT.json")
    ra2021_double_low_order = read_json(PAPER / "RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.json")
    hi2022_ra_half_double_failure = read_json(
        PAPER / "HI2022_RA_HALF_DOUBLE_SOURCE_POLICY_FAILURE_DIAGNOSIS.json"
    )

    commands = iter_packet_commands(packet)
    command_presence_rows = [command_presence(command) for command in commands]
    expected_output_missing = [
        row["id"] for row in command_presence_rows if row.get("expected_output_exists_now") is False
    ]
    expected_summary_missing = [
        row["id"] for row in command_presence_rows if row.get("expected_summary_exists_now") is False
    ]
    optional_summary_missing = [row for row in expected_summary_missing if row is not None]

    current = b4.get("current_evidence", {})
    ra_shards = b4.get("ra2021_executed_shard_evidence", {})
    gauss6 = b4.get("gauss6_local_source_policy_evidence", {})
    double_candidate = b4.get("ra2021_double_local_source_policy_candidate_evidence", {})
    double_low_order_diagnosis = ra2021_double_low_order.get("diagnosis", {})
    double_low_order_promotion = ra2021_double_low_order.get("promotion_decision", {})
    hi_candidate = b4.get("hi2022_full_t8_source_policy_candidate_evidence", {})
    hi_failure_evidence = hi2022_ra_half_double_failure.get("execution_evidence", {})
    hi_failure_diagnosis = hi2022_ra_half_double_failure.get("diagnosis", {})
    hi_failure_promotion = hi2022_ra_half_double_failure.get("promotion_decision", {})
    hi_demotion = b4.get("hi2022_b4_b7_figure_scope_demotion_evidence", {})
    tfe = b4.get("tfe_source_policy_runner_equivalence_preflight_evidence", {})

    public_closed_loop_shards = {
        "four_link": csv_summary(
            "../../numerics/v048_cross_paper_same_test_benchmarks/results/public_closed_loop_shards/"
            "four_link_1em02_1em03_1em04.csv"
        ),
        "slider_crank": csv_summary(
            "../../numerics/v048_cross_paper_same_test_benchmarks/results/public_closed_loop_shards/"
            "slider_crank_1em02_1em03_1em04.csv"
        ),
    }
    public_closed_loop_trios_completed = all(
        item["row_count"] == 3 and item["ok_row_count"] == 3 for item in public_closed_loop_shards.values()
    )

    row_status = {
        "source_policy_rows_closed": row_ledger.get("source_policy_rows_closed"),
        "source_policy_rows_total": row_ledger.get("row_count"),
        "source_policy_rows_unclosed": row_ledger.get("source_policy_rows_unclosed"),
        "source_policy_rows_open": row_ledger.get("source_policy_rows_open"),
        "source_policy_rows_attempted_not_reproducible": row_ledger.get(
            "source_policy_rows_attempted_not_reproducible"
        ),
        "source_policy_rows_still_requiring_execution_or_promotion": row_ledger.get(
            "source_policy_rows_still_requiring_execution_or_promotion"
        ),
        "rows_with_launch_command_refs": row_ledger.get("rows_with_launch_command_refs"),
        "rows_without_launch_command_refs": row_ledger.get("rows_without_launch_command_refs"),
        "rows_without_launch_command_refs_attempted_not_reproducible": row_ledger.get(
            "rows_without_launch_command_refs_attempted_not_reproducible"
        ),
        "b4_can_close_now": row_ledger.get("b4_can_close_now"),
        "b7_can_close_now": row_ledger.get("b7_can_close_now"),
    }

    command_artifacts_present = not expected_output_missing and not optional_summary_missing
    output_status = (
        "verified_authorized_driver_execution_recorded_no_source_policy_rows_promoted"
        if verified_authorized_execution_recorded
        else "existing_outputs_present_no_verified_authorized_execution_no_source_policy_rows_promoted"
    )
    promotion_reason = (
        "The guarded driver was run with the exact approval statement and populated ready "
        "RA2021/HI2022 artifacts, but the row-closure ledger and promotion audit still "
        "record zero promotable source-policy rows. Authorized execution is therefore "
        "recorded as output-presence evidence, not row promotion."
        if verified_authorized_execution_recorded
        else (
            "The ready RA2021/HI2022 artifacts are present, but no exact approval statement "
            "was supplied to this builder. Existing artifacts are treated as artifact-presence "
            "evidence rather than a verified current authorized execution."
        )
    )

    output: dict[str, Any] = {
        "schema": "b4-source-policy-post-execution-audit-v1",
        "status": output_status,
        "read_only": True,
        "heavy_numerical_run_invoked_by_this_builder": False,
        "run_v047_invoked_by_this_builder": False,
        "v048_runner_invoked_by_this_builder": False,
        "approved_driver_execution_recorded": verified_authorized_execution_recorded,
        "verified_authorized_execution_recorded": verified_authorized_execution_recorded,
        "approval_statement_matched": verified_authorized_execution_recorded,
        "execution_authorized": verified_authorized_execution_recorded,
        "commands_executed_by_audit": False,
        "source_policy_execution_invoked": verified_authorized_execution_recorded,
        "source_policy_execution_allowed_now": False,
        "exact_b4_opt_in_required_for_execution": True,
        "safe_action_ids": SAFE_ACTION_IDS,
        "opt_in_action_ids": OPT_IN_ACTION_IDS,
        "required_user_approval_statement": packet.get("required_user_approval_statement"),
        "guarded_execution_driver": packet.get("guarded_execution_driver", {}).get("path"),
        "next_safe_actions": SAFE_ACTIONS_WITHOUT_B4_OPT_IN,
        "next_safe_action_ids": SAFE_ACTION_IDS,
        "existing_ready_command_artifacts_present": command_artifacts_present,
        "execution_record_scope": (
            "verified_authorized_guarded_driver_execution"
            if verified_authorized_execution_recorded
            else "no_verified_current_authorized_execution_record_existing_artifacts_only"
        ),
        "source_policy_rows_closed": row_status["source_policy_rows_closed"],
        "source_policy_rows_promoted": row_status["source_policy_rows_closed"],
        "source_policy_closed_ratio": (
            f"{row_status['source_policy_rows_closed']}/{row_status['source_policy_rows_total']}"
        ),
        "source_policy_total_rows": row_status["source_policy_rows_total"],
        "source_policy_rows_unclosed": row_status["source_policy_rows_unclosed"],
        "source_policy_rows_open": row_status["source_policy_rows_open"],
        "source_policy_rows_attempted_not_reproducible": row_status[
            "source_policy_rows_attempted_not_reproducible"
        ],
        "source_policy_rows_still_requiring_execution_or_promotion": row_status[
            "source_policy_rows_still_requiring_execution_or_promotion"
        ],
        "b4_can_close_now": row_status["b4_can_close_now"],
        "b7_can_close_now": row_status["b7_can_close_now"],
        "external_superiority_claim_allowed": False,
        "post_execution_summary": {
            "approved_driver_execution_recorded": verified_authorized_execution_recorded,
            "verified_authorized_execution_recorded": verified_authorized_execution_recorded,
            "existing_ready_command_artifacts_present": command_artifacts_present,
            "ready_commands_in_packet": packet.get("ready_command_count"),
            "ready_commands_verified_executed_by_this_record": (
                packet.get("ready_command_count") if verified_authorized_execution_recorded else 0
            ),
            "ready_command_mapped_external_rows": packet.get("ready_command_mapped_external_rows"),
            "unaddressed_external_rows_after_ready_commands": packet.get(
                "unaddressed_external_rows_after_ready_commands"
            ),
            "source_policy_rows_promoted_after_driver": row_status["source_policy_rows_closed"],
            "source_policy_rows_total": row_status["source_policy_rows_total"],
            "source_policy_rows_attempted_not_reproducible": row_status[
                "source_policy_rows_attempted_not_reproducible"
            ],
            "source_policy_rows_still_requiring_execution_or_promotion": row_status[
                "source_policy_rows_still_requiring_execution_or_promotion"
            ],
            "b4_can_close_now": row_status["b4_can_close_now"],
            "b7_can_close_now": row_status["b7_can_close_now"],
        },
        "guarded_driver": {
            "path": packet.get("guarded_execution_driver", {}).get("path"),
            "exists": packet.get("guarded_execution_driver", {}).get("exists"),
            "ready_command_count": packet.get("ready_command_count"),
            "ready_command_batch_count": packet.get("ready_command_batch_count"),
            "ready_command_mapped_external_rows": packet.get("ready_command_mapped_external_rows"),
            "unaddressed_external_rows_after_ready_commands": packet.get(
                "unaddressed_external_rows_after_ready_commands"
            ),
        },
        "packet_semantics": {
            "packet_status": packet.get("status"),
            "execution_invoked_by_packet": packet.get("execution_invoked_by_packet"),
            "note": (
                "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET is a pre-execution guard; "
                "this audit records artifact state and only records verified authorized "
                "execution when the exact approval statement is supplied to the builder."
            ),
        },
        "command_artifact_presence": {
            "command_count": len(command_presence_rows),
            "all_expected_outputs_exist_now": not expected_output_missing,
            "expected_output_missing_command_ids": expected_output_missing,
            "all_expected_summaries_exist_now": not optional_summary_missing,
            "expected_summary_missing_command_ids": optional_summary_missing,
            "packet_artifact_status_counts": dict(
                sorted(Counter(str(row.get("packet_artifact_status")) for row in command_presence_rows).items())
            ),
            "commands": command_presence_rows,
        },
        "post_execution_artifact_evidence": {
            "ra2021_public_baseline_progress": current.get("ra2021_public_baseline_progress"),
            "ra2021_public_baseline_shards_status": ra_shards.get("status"),
            "ra2021_public_baseline_shards_ok_rows": ra_shards.get("ok_row_count"),
            "ra2021_double_local_candidate_status": double_candidate.get("status"),
            "ra2021_double_local_candidate_rows": double_candidate.get("row_count"),
            "ra2021_double_local_candidate_order_acceptance_satisfied": double_candidate.get(
                "source_policy_order_acceptance_satisfied"
            ),
            "ra2021_double_local_candidate_pos_order": double_candidate.get("source_policy_pos_observed_order"),
            "ra2021_double_local_candidate_vel_order": double_candidate.get("source_policy_vel_observed_order"),
            "ra2021_double_low_order_diagnosis_status": ra2021_double_low_order.get("status"),
            "ra2021_double_low_order_fine_pair_floor_limited": double_low_order_diagnosis.get(
                "fine_pair_floor_limited"
            ),
            "ra2021_double_low_order_fine_pair_label": double_low_order_diagnosis.get("fine_pair_label"),
            "ra2021_double_low_order_coarse_h_constraint_threshold_satisfied": (
                double_low_order_diagnosis.get("coarse_h_constraint_threshold_satisfied")
            ),
            "ra2021_double_low_order_constraint_failure_components": double_low_order_diagnosis.get(
                "coarse_h_constraint_failure_components"
            ),
            "ra2021_double_low_order_fine_pair_floor_margin_to_threshold": double_low_order_diagnosis.get(
                "fine_pair_floor_margin_to_threshold"
            ),
            "ra2021_double_low_order_finest_to_reference_step_ratio": double_low_order_diagnosis.get(
                "finest_to_reference_step_ratio"
            ),
            "ra2021_double_low_order_accepted_binding_closed": ra2021_double_low_order.get(
                "ledger_binding_reconciliation",
                {},
            ).get("accepted_source_policy_binding_closed"),
            "ra2021_double_low_order_local_metrics_present": ra2021_double_low_order.get(
                "ledger_binding_reconciliation",
                {},
            ).get("candidate_local_error_runtime_newton_columns_present"),
            "ra2021_double_low_order_rows_promoted_by_diagnosis": double_low_order_promotion.get(
                "source_policy_rows_promoted_by_this_diagnosis"
            ),
            "ra2021_double_low_order_b4_b7_can_close": double_low_order_promotion.get(
                "b4_b7_can_close_from_this_diagnosis"
            ),
            "gauss6_local_status": gauss6.get("status"),
            "gauss6_single_public_horizon_step_trio_completed": gauss6.get(
                "single_public_horizon_step_trio_completed"
            ),
            "gauss6_closed_loop_public_step_trios_completed": gauss6.get(
                "closed_loop_public_step_trios_completed"
            ),
            "gauss6_closed_loop_rows_are_dynamic_work_precision": gauss6.get(
                "closed_loop_rows_are_dynamic_work_precision"
            ),
            "public_closed_loop_shards": public_closed_loop_shards,
            "public_closed_loop_trios_completed_by_latest_driver_outputs": public_closed_loop_trios_completed,
            "hi2022_selected_candidate_status": hi_candidate.get("status"),
            "hi2022_selected_candidate_completed_shards": hi_candidate.get("completed_shard_count"),
            "hi2022_selected_candidate_expected_shards": hi_candidate.get("expected_shard_count"),
            "hi2022_selected_candidate_partial_or_failed_shards": hi_candidate.get("partial_or_failed_shards"),
            "hi2022_selected_candidate_rows_ok": hi_candidate.get("ok_row_count"),
            "hi2022_selected_candidate_rows_total": hi_candidate.get("row_count"),
            "hi2022_full_t8_policy_completed": hi_candidate.get("full_T8_policy_completed"),
            "hi2022_full_public_grid_selected": hi_candidate.get("full_public_grid_selected"),
            "hi2022_ra_half_double_failure_diagnosis_status": hi2022_ra_half_double_failure.get("status"),
            "hi2022_ra_half_double_failure_rows_ok": hi_failure_evidence.get("ok_row_count"),
            "hi2022_ra_half_double_failure_rows_failed": hi_failure_evidence.get("failed_row_count"),
            "hi2022_ra_half_double_failure_rows_total": hi_failure_evidence.get("row_count"),
            "hi2022_ra_half_double_failure_newton_failure_count": hi_failure_diagnosis.get(
                "newton_failure_count"
            ),
            "hi2022_ra_half_double_failure_pair_orders_available": hi_failure_diagnosis.get(
                "pair_orders_available"
            ),
            "hi2022_ra_half_double_failure_rows_promoted_by_diagnosis": hi_failure_promotion.get(
                "source_policy_rows_promoted_by_this_diagnosis"
            ),
            "hi2022_ra_half_double_failure_b4_b7_can_close": hi_failure_promotion.get(
                "b4_b7_can_close_from_this_diagnosis"
            ),
            "hi2022_figure_scope_demotion_status": hi_demotion.get("status"),
            "tfe_runner_equivalence_status": tfe.get("status"),
            "tfe_runner_equivalence_open_blocker_count": tfe.get("open_blocker_count"),
        },
        "promotion_decision": {
            "source_policy_rows_closed_by_existing_artifacts": existing_promotion.get(
                "source_policy_rows_closed_by_existing_artifacts"
            ),
            "existing_artifact_promotion_ready_count": existing_promotion.get(
                "promotion_ready_without_new_execution_count"
            ),
            "source_policy_rows_closed_after_driver": row_status["source_policy_rows_closed"],
            "source_policy_rows_total": row_status["source_policy_rows_total"],
            "source_policy_rows_attempted_not_reproducible": row_status[
                "source_policy_rows_attempted_not_reproducible"
            ],
            "source_policy_rows_still_requiring_execution_or_promotion": row_status[
                "source_policy_rows_still_requiring_execution_or_promotion"
            ],
            "b4_can_close_now": row_status["b4_can_close_now"],
            "b7_can_close_now": row_status["b7_can_close_now"],
            "external_superiority_claim_allowed": False,
            "reason": promotion_reason,
        },
        "row_status_after_driver": row_status,
        "review_agent_status_after_driver": {
            "submission_standard_scope": review.get("submission_standard_scope"),
            "submission_standard_met": review.get("submission_standard_met"),
            "global_submission_standard_met": review.get("global_submission_standard_met"),
            "decision": review.get("decision"),
            "open_blockers": review.get("open_blockers"),
            "cmame_blocker_gate_open_blocker_count": review.get("cmame_blocker_gate_open_blocker_count"),
            "cmame_blocker_gate_open_blockers": review.get("cmame_blocker_gate_open_blockers"),
            "narrowed_submission_standard_met": review.get("narrowed_submission_standard_met"),
            "narrowed_claim_decision": review.get("narrowed_claim_decision"),
        },
        "next_required_actions": [
            "Do not rerun the same guarded B4 driver blindly; it now records zero promoted rows.",
            "Root-cause the RA2021 double local source-policy candidate low-order result before promotion.",
            "Keep RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.md/json as diagnostic-only evidence until a non-floor-limited verified row policy exists.",
            "Keep HI2022_RA_HALF_DOUBLE_SOURCE_POLICY_FAILURE_DIAGNOSIS.md/json as diagnostic-only evidence until a repaired complete shard or formal suite demotion exists.",
            "Keep TFE and VP rows marked attempted-not-reproducible and demoted unless new public-code or source-equivalent runner evidence is introduced.",
            "Run the B6 final prose pass only after B4/B7 wording is settled.",
        ],
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, sort_keys=True)
        handle.write("\n")

    pos_order = double_candidate.get("source_policy_pos_observed_order")
    vel_order = double_candidate.get("source_policy_vel_observed_order")
    lines = [
        "# B4 Source-Policy Post-Execution Audit",
        "",
        f"Status: `{output['status']}`.",
        "",
        "This audit is separate from `B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET`: the packet is a guard, "
        "while this file records artifact state. Without the exact approval statement, existing outputs are not treated as a verified current authorized guarded-driver run.",
        "",
        f"- Verified authorized execution recorded: `{output['verified_authorized_execution_recorded']}`.",
        f"- Existing ready-command artifacts present: `{output['existing_ready_command_artifacts_present']}`.",
        f"- Execution record scope: `{output['execution_record_scope']}`.",
        f"- Source-policy execution allowed now/invoked/exact opt-in required: `{output['source_policy_execution_allowed_now']}/{output['source_policy_execution_invoked']}/{output['exact_b4_opt_in_required_for_execution']}`.",
        f"- Safe action ids: `{','.join(output['safe_action_ids'])}`.",
        f"- Opt-in action ids: `{','.join(output['opt_in_action_ids'])}`.",
        f"- Required approval/driver: `{output['required_user_approval_statement']}/{output['guarded_execution_driver']}`.",
        f"- Guarded driver: `{output['guarded_driver']['path']}`.",
        f"- Ready commands in packet/mapped rows: `{output['guarded_driver']['ready_command_count']}` / `{output['guarded_driver']['ready_command_mapped_external_rows']}`.",
        f"- Ready commands verified executed by this record: `{output['post_execution_summary']['ready_commands_verified_executed_by_this_record']}`.",
        f"- Unaddressed rows after ready commands: `{output['guarded_driver']['unaddressed_external_rows_after_ready_commands']}`.",
        f"- Attempted-not-reproducible rows: `{row_status['source_policy_rows_attempted_not_reproducible']}`.",
        f"- Rows still requiring execution/promotion: `{row_status['source_policy_rows_still_requiring_execution_or_promotion']}`.",
        f"- Expected outputs present: `{output['command_artifact_presence']['all_expected_outputs_exist_now']}`.",
        f"- Source-policy rows closed: `{row_status['source_policy_rows_closed']}/{row_status['source_policy_rows_total']}`.",
        f"- B4/B7 can close now: `{row_status['b4_can_close_now']}/{row_status['b7_can_close_now']}`.",
        f"- Top-level post-execution summary rows/B4/B7: `{output['source_policy_rows_closed']}/{output['source_policy_total_rows']}` / `{output['b4_can_close_now']}/{output['b7_can_close_now']}`.",
        f"- Global review agent: `{review.get('decision')}` with blockers `{review.get('open_blockers')}`.",
        (
            "- Bounded narrowed subcheck disposition: "
            "`bounded_subcheck_satisfied_not_global_submit`; "
            f"deprecated compatibility decision alias `{review.get('narrowed_claim_decision')}` "
            "retained for validators only, not as a submit instruction; "
            f"bounded subcheck marker `{review.get('narrowed_submission_standard_met')}`; "
            f"CMAME blocker-gate blockers `{review.get('cmame_blocker_gate_open_blockers')}`."
        ),
        "",
        "## Objective Blocker Matrix",
        "",
        "This audit records OC4 post-execution state. It does not close the global objective blockers.",
        "",
        "- `blocker_open_by_id=OC4:True,OC6:True,OC12:True`",
        "- `blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready`",
        "- `blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False`",
        "",
        "## Post-Run Evidence",
        "",
        f"- RA2021 public baseline shards: `{ra_shards.get('status')}` with `{ra_shards.get('ok_row_count')}` rows.",
        f"- RA2021 double local candidate: `{double_candidate.get('status')}`; accepted order `{double_candidate.get('source_policy_order_acceptance_satisfied')}`; pos/vel `{pos_order:.3f}/{vel_order:.3f}`.",
        f"- RA2021 double low-order diagnosis: `{ra2021_double_low_order.get('status')}`; fine pair floor-limited `{double_low_order_diagnosis.get('fine_pair_floor_limited')}`; rows promoted `{double_low_order_promotion.get('source_policy_rows_promoted_by_this_diagnosis')}`.",
        (
            "- RA2021 double low-order binding: "
            f"constraint components `{double_low_order_diagnosis.get('coarse_h_constraint_failure_components')}`; "
            f"floor margin `{double_low_order_diagnosis.get('fine_pair_floor_margin_to_threshold'):.3f}`; "
            f"finest/reference h ratio `{double_low_order_diagnosis.get('finest_to_reference_step_ratio'):.1f}`; "
            f"accepted binding `{ra2021_double_low_order.get('ledger_binding_reconciliation', {}).get('accepted_source_policy_binding_closed')}`."
        ),
        f"- Gauss6 local evidence: `{gauss6.get('status')}`; single trio `{gauss6.get('single_public_horizon_step_trio_completed')}`; closed-loop dynamic work/precision `{gauss6.get('closed_loop_rows_are_dynamic_work_precision')}`.",
        f"- Public closed-loop latest shard trios: `{public_closed_loop_trios_completed}`.",
        f"- HI2022 selected candidate: `{hi_candidate.get('status')}`; shards `{hi_candidate.get('completed_shard_count')}/{hi_candidate.get('expected_shard_count')}`; partial `{hi_candidate.get('partial_or_failed_shards')}`.",
        f"- HI2022 rA_half double failure diagnosis: `{hi2022_ra_half_double_failure.get('status')}`; ok/failed/total `{hi_failure_evidence.get('ok_row_count')}/{hi_failure_evidence.get('failed_row_count')}/{hi_failure_evidence.get('row_count')}`; Newton failures `{hi_failure_diagnosis.get('newton_failure_count')}`; rows promoted `{hi_failure_promotion.get('source_policy_rows_promoted_by_this_diagnosis')}`.",
        f"- TFE runner-equivalence preflight: `{tfe.get('status')}`; open blockers `{tfe.get('open_blocker_count')}`.",
        f"- Nonpublic-code self-reproduction disposition: attempted-not-reproducible `{row_status['source_policy_rows_attempted_not_reproducible']}`; still requiring execution/promotion `{row_status['source_policy_rows_still_requiring_execution_or_promotion']}`.",
        "",
        "## Public Closed-Loop Shards",
        "",
        "| model | rows | ok rows | path |",
        "|---|---:|---:|---|",
    ]
    for model, item in public_closed_loop_shards.items():
        lines.append(f"| `{model}` | `{item['row_count']}` | `{item['ok_row_count']}` | `{item['path']}` |")
    lines.extend(
        [
            "",
            "## Promotion Decision",
            "",
            f"Source-policy rows promoted by current verified execution/artifact state: `{row_status['source_policy_rows_closed']}/{row_status['source_policy_rows_total']}`.",
            "B4/B7 remain open because artifact presence or authorized execution is not row promotion; rows promote only after the source-policy row audits close.",
            "",
            "## Next Required Actions",
            "",
        ]
    )
    for action in output["next_required_actions"]:
        lines.append(f"- {action}")
    lines.append("")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("b4_source_policy_post_execution_audit=written")
    print(f"verified_authorized_execution_recorded={verified_authorized_execution_recorded}")
    print(f"source_policy_execution_invoked={verified_authorized_execution_recorded}")
    print("source_policy_execution_allowed_now=False")
    print(f"existing_ready_command_artifacts_present={command_artifacts_present}")
    print(f"ready_commands={packet.get('ready_command_count')}")
    print(
        f"source_policy_rows_closed={row_status['source_policy_rows_closed']}/{row_status['source_policy_rows_total']}"
    )
    print(f"b4_can_close_now={row_status['b4_can_close_now']}")
    print(f"b7_can_close_now={row_status['b7_can_close_now']}")


if __name__ == "__main__":
    main()
