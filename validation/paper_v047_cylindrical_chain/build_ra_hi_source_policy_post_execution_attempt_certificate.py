#!/usr/bin/env python3
"""Build a row-level RA/HI source-policy post-execution attempt certificate.

The B4 guarded driver has produced/recorded the RA2021 and HI2022 artifacts, but
none of those rows are promotable as full source-policy evidence.  This
certificate binds each still-open RA/HI row to its post-execution evidence and
keeps the rows open until a repair, independent rerun, or formal demotion is
available.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "RA_HI_SOURCE_POLICY_POST_EXECUTION_ATTEMPT_CERTIFICATE.json"
OUT_MD = PAPER / "RA_HI_SOURCE_POLICY_POST_EXECUTION_ATTEMPT_CERTIFICATE.md"

SUITES = {"ra2021_absolute_coordinate", "hi2022_half_implicit"}
SAFE_ACTIONS_WITHOUT_B4_OPT_IN = [
    {
        "id": "rebuild_read_only_audit_chain",
        "description": "Rebuild this RA/HI certificate plus downstream objective, review, and package manifests.",
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


def row_id(row: dict[str, Any]) -> str:
    return f"{row.get('suite_id')}:{row.get('method')}:{row.get('example')}"


def main() -> None:
    ledger = read_json(PAPER / "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.json")
    post = read_json(PAPER / "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.json")
    ra_low = read_json(PAPER / "RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.json")
    hi_fail = read_json(PAPER / "HI2022_RA_HALF_DOUBLE_SOURCE_POLICY_FAILURE_DIAGNOSIS.json")
    hi_repair = read_json(PAPER / "HI2022_RA_HALF_DOUBLE_REPAIR_ATTEMPT_CERTIFICATE.json")
    ra_audit = read_json(PAPER / "RA2021_SOURCE_POLICY_ROW_AUDIT.json")
    hi_audit = read_json(PAPER / "HI2022_SOURCE_POLICY_ROW_AUDIT.json")

    source_rows = [
        row
        for row in ledger.get("rows", [])
        if isinstance(row, dict) and row.get("suite_id") in SUITES
    ]
    source_rows.sort(key=lambda row: (str(row.get("suite_id")), str(row.get("method")), str(row.get("example"))))

    cert_rows: list[dict[str, Any]] = []
    for row in source_rows:
        blocker = str(row.get("primary_promotion_blocker"))
        if row.get("suite_id") == "ra2021_absolute_coordinate":
            evidence_status = (
                "diagnosis_only_low_order_floor_limited_not_promoted"
                if blocker == "ra2021_double_low_order_floor_limited_constraint_not_promoted"
                else "approved_driver_outputs_present_not_promoted"
            )
        elif blocker == "hi2022_ra_half_double_partial_newton_failure_not_promoted":
            evidence_status = "diagnosis_only_partial_newton_failure_not_promoted"
        else:
            evidence_status = "selected_candidate_executed_not_promoted"
        cert_rows.append(
            {
                "row_id": row_id(row),
                "suite_id": row.get("suite_id"),
                "method": row.get("method"),
                "example": row.get("example"),
                "source_policy_disposition": row.get("source_policy_disposition"),
                "post_execution_decision": row.get("post_execution_decision"),
                "post_execution_attempt_status": evidence_status,
                "source_policy_closed": row.get("source_policy_closed"),
                "external_superiority_ready": row.get("external_superiority_ready"),
                "counts_as_open_execution_queue": row.get("counts_as_open_execution_queue"),
                "ready_to_launch_after_explicit_opt_in": row.get("ready_to_launch_after_explicit_opt_in"),
                "readiness_status": row.get("readiness_status"),
                "primary_promotion_blocker": blocker,
                "blocking_reasons": row.get("blocking_reasons", []),
                "promotion_evidence_ref": row.get("promotion_evidence_ref"),
                "command_refs": row.get("command_refs", []),
                "command_artifact_statuses": row.get("command_artifact_statuses", []),
                "source_policy_1e_4_opt_in_required": row.get("source_policy_1e_4_opt_in_required"),
                "accepted_use": "post_execution_source_policy_attempt_not_promoted",
            }
        )

    blocker_counts = dict(sorted(Counter(row["primary_promotion_blocker"] for row in cert_rows).items()))
    suite_counts = {
        suite_id: len([row for row in cert_rows if row["suite_id"] == suite_id])
        for suite_id in sorted(SUITES)
    }
    row_status = post.get("row_status_after_driver", {})
    post_evidence = post.get("post_execution_artifact_evidence", {})
    output: dict[str, Any] = {
        "schema": "ra-hi-source-policy-post-execution-attempt-certificate-v1",
        "status": "post_execution_attempts_recorded_rows_not_promoted_full_source_policy_open",
        "read_only": True,
        "heavy_numerical_run_invoked": False,
        "run_v047_invoked": False,
        "v048_runner_invoked": False,
        "heavy_numerical_run_invoked_by_this_builder": False,
        "run_v047_invoked_by_this_builder": False,
        "v048_runner_invoked_by_this_builder": False,
        "source_policy_closed": False,
        "source_policy_closed_ratio": f"{row_status.get('source_policy_rows_closed')}/{row_status.get('source_policy_rows_total')}",
        "source_policy_execution_invoked": post.get("source_policy_execution_invoked"),
        "source_policy_execution_allowed_now": post.get("source_policy_execution_allowed_now"),
        "exact_b4_opt_in_required_for_execution": post.get("exact_b4_opt_in_required_for_execution"),
        "safe_action_ids": post.get("safe_action_ids") or SAFE_ACTION_IDS,
        "opt_in_action_ids": post.get("opt_in_action_ids") or OPT_IN_ACTION_IDS,
        "required_user_approval_statement": post.get("required_user_approval_statement"),
        "guarded_execution_driver": post.get("guarded_execution_driver"),
        "next_safe_actions": post.get("next_safe_actions") or SAFE_ACTIONS_WITHOUT_B4_OPT_IN,
        "next_safe_action_ids": post.get("next_safe_action_ids") or SAFE_ACTION_IDS,
        "source_policy_rows_closed": row_status.get("source_policy_rows_closed"),
        "source_policy_rows_total": row_status.get("source_policy_rows_total"),
        "submission_ready": False,
        "source_policy_rows_completed": 0,
        "source_policy_rows_promoted": 0,
        "external_superiority_ready_rows": 0,
        "row_count": len(cert_rows),
        "ra2021_row_count": suite_counts.get("ra2021_absolute_coordinate", 0),
        "hi2022_row_count": suite_counts.get("hi2022_half_implicit", 0),
        "post_execution_decision_counts": dict(
            sorted(Counter(str(row["post_execution_decision"]) for row in cert_rows).items())
        ),
        "primary_promotion_blocker_counts": blocker_counts,
        "rows_still_requiring_execution_or_promotion": len(cert_rows),
        "rows_removed_from_open_queue": 0,
        "not_promoted_rows_remain_full_source_policy_blockers": True,
        "post_execution_audit_status": post.get("status"),
        "approved_driver_execution_recorded": post.get("approved_driver_execution_recorded"),
        "verified_authorized_execution_recorded": post.get("verified_authorized_execution_recorded"),
        "existing_ready_command_artifacts_present": post.get("existing_ready_command_artifacts_present"),
        "execution_record_scope": post.get("execution_record_scope"),
        "post_execution_row_status": {
            "source_policy_rows_closed": row_status.get("source_policy_rows_closed"),
            "source_policy_rows_total": row_status.get("source_policy_rows_total"),
            "source_policy_rows_open": row_status.get("source_policy_rows_open"),
            "source_policy_rows_still_requiring_execution_or_promotion": row_status.get(
                "source_policy_rows_still_requiring_execution_or_promotion"
            ),
        },
        "ra2021_evidence": {
            "audit_status": ra_audit.get("status"),
            "public_baseline_progress": post_evidence.get("ra2021_public_baseline_progress"),
            "public_baseline_shards_status": post_evidence.get("ra2021_public_baseline_shards_status"),
            "single_public_horizon_step_trio_completed": post_evidence.get(
                "gauss6_single_public_horizon_step_trio_completed"
            ),
            "closed_loop_public_step_trios_completed": post_evidence.get(
                "gauss6_closed_loop_public_step_trios_completed"
            ),
            "closed_loop_rows_are_dynamic_work_precision": post_evidence.get(
                "gauss6_closed_loop_rows_are_dynamic_work_precision"
            ),
            "double_low_order_diagnosis_status": ra_low.get("status"),
            "double_low_order_pos_order": post_evidence.get("ra2021_double_local_candidate_pos_order"),
            "double_low_order_vel_order": post_evidence.get("ra2021_double_local_candidate_vel_order"),
            "double_low_order_fine_pair_floor_limited": post_evidence.get(
                "ra2021_double_low_order_fine_pair_floor_limited"
            ),
            "double_low_order_constraint_threshold_satisfied": post_evidence.get(
                "ra2021_double_low_order_coarse_h_constraint_threshold_satisfied"
            ),
            "rows_promoted_by_double_diagnosis": ra_low.get("promotion_decision", {}).get(
                "source_policy_rows_promoted_by_this_diagnosis"
            ),
        },
        "hi2022_evidence": {
            "audit_status": hi_audit.get("status"),
            "selected_candidate_status": post_evidence.get("hi2022_selected_candidate_status"),
            "selected_candidate_completed_shards": post_evidence.get(
                "hi2022_selected_candidate_completed_shards"
            ),
            "selected_candidate_expected_shards": post_evidence.get(
                "hi2022_selected_candidate_expected_shards"
            ),
            "selected_candidate_rows_ok": post_evidence.get("hi2022_selected_candidate_rows_ok"),
            "selected_candidate_rows_total": post_evidence.get("hi2022_selected_candidate_rows_total"),
            "selected_candidate_partial_or_failed_shards": post_evidence.get(
                "hi2022_selected_candidate_partial_or_failed_shards"
            ),
            "full_public_grid_selected": post_evidence.get("hi2022_full_public_grid_selected"),
            "full_t8_policy_completed": post_evidence.get("hi2022_full_t8_policy_completed"),
            "ra_half_double_failure_status": hi_fail.get("status"),
            "ra_half_double_rows_ok": hi_fail.get("execution_evidence", {}).get("ok_row_count"),
            "ra_half_double_rows_failed": hi_fail.get("execution_evidence", {}).get("failed_row_count"),
            "ra_half_double_newton_failure_count": hi_fail.get("diagnosis", {}).get(
                "newton_failure_count"
            ),
            "ra_half_double_pair_orders_available": hi_fail.get("diagnosis", {}).get(
                "pair_orders_available"
            ),
            "rows_promoted_by_ra_half_double_diagnosis": hi_fail.get("promotion_decision", {}).get(
                "source_policy_rows_promoted_by_this_diagnosis"
            ),
            "ra_half_double_repair_attempt_status": hi_repair.get("status"),
            "ra_half_double_repair_target_ok_rows": hi_repair.get("tolerance_repair_evidence", {})
            .get("combined_target_group", {})
            .get("ok_row_count"),
            "ra_half_double_repair_target_failed_rows": hi_repair.get("tolerance_repair_evidence", {})
            .get("combined_target_group", {})
            .get("failed_row_count"),
            "ra_half_double_repair_combined_ok_rows": hi_repair.get("tolerance_repair_evidence", {}).get(
                "combined_best_ok_rows"
            ),
            "ra_half_double_repair_combined_row_count": hi_repair.get("tolerance_repair_evidence", {}).get(
                "combined_best_row_count"
            ),
            "ra_half_double_repair_combined_complete_groups": hi_repair.get(
                "tolerance_repair_evidence", {}
            ).get("combined_best_complete_groups"),
            "ra_half_double_repair_combined_group_count": hi_repair.get("tolerance_repair_evidence", {}).get(
                "combined_best_group_count"
            ),
            "ra_half_double_repair_source_policy_closed": hi_repair.get("source_policy_closed"),
            "rows_promoted_by_ra_half_double_repair_attempt": hi_repair.get("source_policy_rows_promoted"),
        },
        "closure_decision": {
            "can_close_ra_hi_source_policy_rows_now": False,
            "can_claim_external_superiority_from_ra_hi_now": False,
            "reason": (
                "The RA2021 and HI2022 rows have post-driver evidence, but each row remains blocked by "
                "low-order/floor-limited behavior, residual-only or mixed-reference coverage, incomplete "
                "public-grid execution, partial Newton failure, or missing error/runtime/Newton work binding."
            ),
        },
        "next_required_actions": [
            "Root-cause or rerun RA2021 single rows under a non-floor-limited public-h tranche.",
            "Repair or independently rerun the RA2021 double source-policy candidate with accepted order and binding.",
            "Replace RA2021 closed-loop residual-only rows with true source-policy dynamic work/precision rows or demote formally.",
            "Select and execute the full HI2022 public T=8 grid with bound work/error rows, not just the selected coarse trio.",
            "Repair HI2022 rA_half double Newton failure or formally demote that row family.",
        ],
        "rows": cert_rows,
        "source_files": [
            "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.json",
            "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.json",
            "RA2021_SOURCE_POLICY_ROW_AUDIT.json",
            "RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.json",
            "HI2022_SOURCE_POLICY_ROW_AUDIT.json",
            "HI2022_RA_HALF_DOUBLE_SOURCE_POLICY_FAILURE_DIAGNOSIS.json",
            "HI2022_RA_HALF_DOUBLE_REPAIR_ATTEMPT_CERTIFICATE.json",
        ],
    }

    OUT_JSON.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# RA/HI Source-Policy Post-Execution Attempt Certificate",
        "",
        "Status: **post-execution attempts recorded; rows not promoted; full source-policy open**.",
        "",
        f"- Rows audited: `{output['row_count']}`.",
        f"- RA2021/HI2022 rows: `{output['ra2021_row_count']}/{output['hi2022_row_count']}`.",
        f"- Source-policy rows promoted: `{output['source_policy_rows_promoted']}`.",
        f"- External-superiority ready rows: `{output['external_superiority_ready_rows']}`.",
        f"- Rows still requiring execution or promotion: `{output['rows_still_requiring_execution_or_promotion']}`.",
        f"- Source-policy closed/total: `{output['source_policy_rows_closed']}/{output['source_policy_rows_total']}`.",
        f"- Heavy/run_v047/v048 invoked: `{output['heavy_numerical_run_invoked']}/{output['run_v047_invoked']}/{output['v048_runner_invoked']}`.",
        f"- Submission ready: `{output['submission_ready']}`.",
        f"- Verified authorized B4 execution recorded: `{output['verified_authorized_execution_recorded']}`.",
        f"- Existing ready-command artifacts present: `{output['existing_ready_command_artifacts_present']}`.",
        f"- Execution record scope: `{output['execution_record_scope']}`.",
        f"- Source-policy execution allowed now/invoked/exact opt-in required: `{output['source_policy_execution_allowed_now']}/{output['source_policy_execution_invoked']}/{output['exact_b4_opt_in_required_for_execution']}`.",
        f"- Required approval/driver: `{output['required_user_approval_statement']}/{output['guarded_execution_driver']}`.",
        f"- Safe action ids: `{','.join(output['safe_action_ids'])}`.",
        f"- Opt-in action ids: `{','.join(output['opt_in_action_ids'])}`.",
        "",
        "## Promotion Blockers",
        "",
        "| blocker | rows |",
        "|---|---:|",
    ]
    for blocker, count in blocker_counts.items():
        lines.append(f"| `{blocker}` | `{count}` |")
    lines.extend(
        [
            "",
            "## Evidence Summary",
            "",
            (
                "- RA2021 public order/timing groups: "
                f"`{output['ra2021_evidence']['public_baseline_progress']['order_groups_completed']}/"
                f"{output['ra2021_evidence']['public_baseline_progress']['timing_rows_completed']}`."
            ),
            (
                "- RA2021 double candidate pos/vel order and promoted rows: "
                f"`{output['ra2021_evidence']['double_low_order_pos_order']:.3f}/"
                f"{output['ra2021_evidence']['double_low_order_vel_order']:.3f}/"
                f"{output['ra2021_evidence']['rows_promoted_by_double_diagnosis']}`."
            ),
            (
                "- HI2022 selected candidate completed/expected shards and ok/total rows: "
                f"`{output['hi2022_evidence']['selected_candidate_completed_shards']}/"
                f"{output['hi2022_evidence']['selected_candidate_expected_shards']}` and "
                f"`{output['hi2022_evidence']['selected_candidate_rows_ok']}/"
                f"{output['hi2022_evidence']['selected_candidate_rows_total']}`."
            ),
            (
                "- HI2022 rA_half double ok/failed/Newton-failure/promoted rows: "
                f"`{output['hi2022_evidence']['ra_half_double_rows_ok']}/"
                f"{output['hi2022_evidence']['ra_half_double_rows_failed']}/"
                f"{output['hi2022_evidence']['ra_half_double_newton_failure_count']}/"
                f"{output['hi2022_evidence']['rows_promoted_by_ra_half_double_diagnosis']}`."
            ),
            (
                "- HI2022 rA_half double repair target ok/failed and combined ok/rows/groups: "
                f"`{output['hi2022_evidence']['ra_half_double_repair_target_ok_rows']}/"
                f"{output['hi2022_evidence']['ra_half_double_repair_target_failed_rows']}` and "
                f"`{output['hi2022_evidence']['ra_half_double_repair_combined_ok_rows']}/"
                f"{output['hi2022_evidence']['ra_half_double_repair_combined_row_count']}/"
                f"{output['hi2022_evidence']['ra_half_double_repair_combined_complete_groups']}/"
                f"{output['hi2022_evidence']['ra_half_double_repair_combined_group_count']}`."
            ),
            "",
            "## Row Disposition",
            "",
            "| suite | method | example | status | primary blocker |",
            "|---|---|---|---|---|",
        ]
    )
    for row in cert_rows:
        lines.append(
            f"| `{row['suite_id']}` | `{row['method']}` | `{row['example']}` | "
            f"`{row['post_execution_attempt_status']}` | `{row['primary_promotion_blocker']}` |"
        )
    lines.extend(["", output["closure_decision"]["reason"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("ra_hi_source_policy_post_execution_attempt_certificate=written")
    print(f"rows={output['row_count']}")
    print("source_policy_rows_promoted=0")
    print("external_superiority_ready_rows=0")


if __name__ == "__main__":
    main()
