#!/usr/bin/env python3
"""Validate the RA/HI source-policy post-execution attempt certificate."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
EXPECTED_BLOCKERS = {
    "ra2021_single_floor_limited_public_h_tranche_not_promoted": 3,
    "ra2021_double_low_order_floor_limited_constraint_not_promoted": 3,
    "ra2021_closed_loop_T0p1_mixed_reference_not_source_policy": 6,
    "hi2022_selected_coarse_trio_not_full_public_grid_not_promoted": 7,
    "hi2022_ra_half_double_partial_newton_failure_not_promoted": 1,
}
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


def main() -> int:
    checks = Checks()
    try:
        cert = read_json(PAPER / "RA_HI_SOURCE_POLICY_POST_EXECUTION_ATTEMPT_CERTIFICATE.json")
        text = (PAPER / "RA_HI_SOURCE_POLICY_POST_EXECUTION_ATTEMPT_CERTIFICATE.md").read_text(
            encoding="utf-8",
            errors="replace",
        )
        ledger = read_json(PAPER / "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.json")
        post = read_json(PAPER / "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.json")
        ra_low = read_json(PAPER / "RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.json")
        hi_fail = read_json(PAPER / "HI2022_RA_HALF_DOUBLE_SOURCE_POLICY_FAILURE_DIAGNOSIS.json")
        hi_repair = read_json(PAPER / "HI2022_RA_HALF_DOUBLE_REPAIR_ATTEMPT_CERTIFICATE.json")
    except Exception as exc:  # noqa: BLE001
        print(f"RA/HI post-execution attempt certificate validation: FAIL\n- {exc}")
        return 1

    rows = [row for row in cert.get("rows", []) if isinstance(row, dict)]
    ra_rows = [row for row in rows if row.get("suite_id") == "ra2021_absolute_coordinate"]
    hi_rows = [row for row in rows if row.get("suite_id") == "hi2022_half_implicit"]
    authorized = post.get("verified_authorized_execution_recorded") is True
    expected_scope = (
        "verified_authorized_guarded_driver_execution"
        if authorized
        else "no_verified_current_authorized_execution_record_existing_artifacts_only"
    )

    checks.check(
        cert.get("schema") == "ra-hi-source-policy-post-execution-attempt-certificate-v1",
        "schema changed",
    )
    checks.check(
        cert.get("status")
        == "post_execution_attempts_recorded_rows_not_promoted_full_source_policy_open",
        "status changed",
    )
    checks.check(cert.get("read_only") is True, "certificate must remain read-only")
    checks.check(cert.get("heavy_numerical_run_invoked") is False, "top-level certificate invoked heavy run")
    checks.check(cert.get("run_v047_invoked") is False, "top-level certificate invoked run_v047")
    checks.check(cert.get("v048_runner_invoked") is False, "top-level certificate invoked v048")
    checks.check(
        cert.get("heavy_numerical_run_invoked_by_this_builder") is False,
        "certificate invoked heavy run",
    )
    checks.check(cert.get("run_v047_invoked_by_this_builder") is False, "certificate invoked run_v047")
    checks.check(cert.get("v048_runner_invoked_by_this_builder") is False, "certificate invoked v048")
    checks.check(cert.get("source_policy_closed") is False, "top-level source-policy closure overclaimed")
    checks.check(cert.get("source_policy_closed_ratio") == "0/40", "top-level source-policy ratio changed")
    checks.check(
        cert.get("source_policy_execution_invoked") == post.get("source_policy_execution_invoked") is authorized,
        "source-policy execution alias inconsistent with post audit",
    )
    checks.check(
        cert.get("source_policy_execution_allowed_now") == post.get("source_policy_execution_allowed_now") is False,
        "source-policy execution allowed-now alias changed",
    )
    checks.check(
        cert.get("exact_b4_opt_in_required_for_execution")
        == post.get("exact_b4_opt_in_required_for_execution")
        is True,
        "exact B4 opt-in requirement changed",
    )
    checks.check(cert.get("safe_action_ids") == EXPECTED_SAFE_ACTION_IDS, "safe action ids changed")
    checks.check(cert.get("opt_in_action_ids") == EXPECTED_OPT_IN_ACTION_IDS, "opt-in action ids changed")
    checks.check(
        cert.get("required_user_approval_statement") == EXPECTED_APPROVAL,
        "exact approval statement missing or stale",
    )
    checks.check(cert.get("guarded_execution_driver") == EXPECTED_DRIVER, "guarded driver alias missing or stale")
    checks.check(
        cert.get("next_safe_action_ids") == cert.get("safe_action_ids") == EXPECTED_SAFE_ACTION_IDS,
        "next safe action ids stale",
    )
    checks.check(
        [item.get("id") for item in cert.get("next_safe_actions", [])]
        == EXPECTED_SAFE_ACTION_IDS,
        "next safe actions stale",
    )
    checks.check(cert.get("source_policy_rows_closed") == 0, "top-level source-policy rows overclosed")
    checks.check(cert.get("source_policy_rows_total") == 40, "top-level source-policy row total changed")
    checks.check(cert.get("submission_ready") is False, "top-level submission readiness overclaimed")
    checks.check(cert.get("row_count") == len(rows) == 20, "row count changed")
    checks.check(cert.get("ra2021_row_count") == len(ra_rows) == 12, "RA row count changed")
    checks.check(cert.get("hi2022_row_count") == len(hi_rows) == 8, "HI row count changed")
    checks.check(cert.get("source_policy_rows_completed") == 0, "certificate overclosed rows")
    checks.check(cert.get("source_policy_rows_promoted") == 0, "certificate promoted rows")
    checks.check(cert.get("external_superiority_ready_rows") == 0, "certificate overclaims superiority")
    checks.check(cert.get("rows_still_requiring_execution_or_promotion") == 20, "open rows changed")
    checks.check(cert.get("rows_removed_from_open_queue") == 0, "certificate removed rows from open queue")
    checks.check(
        cert.get("not_promoted_rows_remain_full_source_policy_blockers") is True,
        "not-promoted row boundary missing",
    )
    checks.check(
        cert.get("approved_driver_execution_recorded")
        == post.get("approved_driver_execution_recorded")
        is authorized,
        "approved driver execution marker inconsistent",
    )
    checks.check(
        cert.get("verified_authorized_execution_recorded")
        == post.get("verified_authorized_execution_recorded")
        is authorized,
        "verified authorized execution marker inconsistent",
    )
    checks.check(
        cert.get("existing_ready_command_artifacts_present") is True,
        "existing ready-command artifact presence missing",
    )
    checks.check(
        cert.get("execution_record_scope")
        == post.get("execution_record_scope")
        == expected_scope,
        "execution record scope changed",
    )
    checks.check(
        cert.get("post_execution_audit_status") == post.get("status"),
        "post-execution audit status not carried into certificate",
    )
    checks.check(
        cert.get("primary_promotion_blocker_counts") == EXPECTED_BLOCKERS,
        "primary promotion blocker counts changed",
    )
    checks.check(
        cert.get("post_execution_decision_counts") == {"not_promoted": 20},
        "post-execution decision counts changed",
    )

    row_status = cert.get("post_execution_row_status", {})
    checks.check(
        row_status.get("source_policy_rows_closed") == ledger.get("source_policy_rows_closed") == 0,
        "row-status closed rows changed",
    )
    checks.check(
        row_status.get("source_policy_rows_total") == ledger.get("row_count") == 40,
        "row-status total rows changed",
    )
    checks.check(
        row_status.get("source_policy_rows_open") == ledger.get("source_policy_rows_open") == 20,
        "row-status open rows changed",
    )
    checks.check(
        row_status.get("source_policy_rows_still_requiring_execution_or_promotion")
        == ledger.get("source_policy_rows_still_requiring_execution_or_promotion")
        == 20,
        "row-status still-requiring rows changed",
    )

    ra = cert.get("ra2021_evidence", {})
    checks.check(ra.get("audit_status") == "public_rows_complete_source_policy_rows_not_closed", "RA status changed")
    checks.check(
        ra.get("public_baseline_progress", {}).get("order_groups_completed") == 12
        and ra.get("public_baseline_progress", {}).get("timing_rows_completed") == 12,
        "RA public baseline progress changed",
    )
    checks.check(
        ra.get("single_public_horizon_step_trio_completed") is True,
        "RA single public trio marker missing",
    )
    checks.check(
        ra.get("closed_loop_public_step_trios_completed") is True
        and ra.get("closed_loop_rows_are_dynamic_work_precision") is False,
        "RA closed-loop residual-only boundary changed",
    )
    checks.check(
        ra.get("double_low_order_diagnosis_status") == ra_low.get("status"),
        "RA double low-order diagnosis status stale",
    )
    checks.check(
        float(ra.get("double_low_order_pos_order")) < 6.0
        and float(ra.get("double_low_order_vel_order")) < 6.0,
        "RA double low-order unexpectedly promotable",
    )
    checks.check(
        ra.get("double_low_order_fine_pair_floor_limited") is True
        and ra.get("double_low_order_constraint_threshold_satisfied") is False,
        "RA double low-order root-cause markers changed",
    )
    checks.check(ra.get("rows_promoted_by_double_diagnosis") == 0, "RA double diagnosis promoted rows")

    hi = cert.get("hi2022_evidence", {})
    checks.check(
        hi.get("audit_status") == "bounded_T0p1_rows_complete_full_T8_source_policy_rows_not_closed",
        "HI status changed",
    )
    checks.check(
        hi.get("selected_candidate_completed_shards") == 7
        and hi.get("selected_candidate_expected_shards") == 8
        and hi.get("selected_candidate_rows_ok") == 22
        and hi.get("selected_candidate_rows_total") == 24,
        "HI selected candidate counts changed",
    )
    checks.check(
        hi.get("full_public_grid_selected") is False and hi.get("full_t8_policy_completed") is False,
        "HI full-grid policy overclaimed",
    )
    checks.check(
        hi.get("ra_half_double_failure_status") == hi_fail.get("status"),
        "HI rA_half double failure status stale",
    )
    checks.check(
        hi.get("ra_half_double_rows_ok") == 1
        and hi.get("ra_half_double_rows_failed") == 2
        and hi.get("ra_half_double_newton_failure_count") == 2
        and hi.get("ra_half_double_pair_orders_available") is False,
        "HI rA_half double failure counts changed",
    )
    checks.check(hi.get("rows_promoted_by_ra_half_double_diagnosis") == 0, "HI diagnosis promoted rows")
    checks.check(
        hi.get("ra_half_double_repair_attempt_status") == hi_repair.get("status")
        == "targeted_repair_attempted_not_reproducible_not_promoted",
        "HI rA_half double repair-attempt status stale",
    )
    checks.check(
        hi.get("ra_half_double_repair_target_ok_rows") == 1
        and hi.get("ra_half_double_repair_target_failed_rows") == 2,
        "HI rA_half double repair target counts changed",
    )
    checks.check(
        hi.get("ra_half_double_repair_combined_ok_rows") == 19
        and hi.get("ra_half_double_repair_combined_row_count") == 24
        and hi.get("ra_half_double_repair_combined_complete_groups") == 4
        and hi.get("ra_half_double_repair_combined_group_count") == 8,
        "HI rA_half double repair combined counts changed",
    )
    checks.check(
        hi.get("ra_half_double_repair_source_policy_closed") is False
        and hi.get("rows_promoted_by_ra_half_double_repair_attempt") == 0,
        "HI rA_half double repair overpromoted source-policy rows",
    )

    for row in rows:
        label = row.get("row_id")
        checks.check(row.get("source_policy_closed") is False, f"{label} overclosed")
        checks.check(row.get("external_superiority_ready") is False, f"{label} overclaims superiority")
        checks.check(row.get("source_policy_disposition") == "promotion_open", f"{label} disposition changed")
        checks.check(row.get("post_execution_decision") == "not_promoted", f"{label} post decision changed")
        checks.check(row.get("primary_promotion_blocker") in EXPECTED_BLOCKERS, f"{label} unknown blocker")
        checks.check(row.get("blocking_reasons"), f"{label} missing blocking reasons")
        checks.check(row.get("command_refs"), f"{label} missing command refs")
        checks.check(row.get("command_artifact_statuses"), f"{label} missing command artifact statuses")
        checks.check(
            row.get("accepted_use") == "post_execution_source_policy_attempt_not_promoted",
            f"{label} accepted use changed",
        )

    checks.check(
        cert.get("closure_decision", {}).get("can_close_ra_hi_source_policy_rows_now") is False,
        "closure decision overclaims RA/HI rows",
    )
    checks.check(
        cert.get("closure_decision", {}).get("can_claim_external_superiority_from_ra_hi_now") is False,
        "closure decision overclaims superiority",
    )
    source_files = cert.get("source_files", [])
    checks.check(
        "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.json" in source_files
        and "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.json" in source_files
        and "RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.json" in source_files
        and "HI2022_RA_HALF_DOUBLE_SOURCE_POLICY_FAILURE_DIAGNOSIS.json" in source_files,
        "source files missing from certificate",
    )
    checks.check(
        "HI2022_RA_HALF_DOUBLE_REPAIR_ATTEMPT_CERTIFICATE.json" in source_files,
        "HI repair-attempt certificate missing from source files",
    )

    for token in [
        "Status: **post-execution attempts recorded; rows not promoted; full source-policy open**.",
        "Rows audited: `20`.",
        "RA2021/HI2022 rows: `12/8`.",
        "Source-policy rows promoted: `0`.",
        "External-superiority ready rows: `0`.",
        "Rows still requiring execution or promotion: `20`.",
        "Source-policy closed/total: `0/40`.",
        "Heavy/run_v047/v048 invoked: `False/False/False`.",
        "Submission ready: `False`.",
        f"Source-policy execution allowed now/invoked/exact opt-in required: `False/{authorized}/True`.",
        "Safe action ids: `rebuild_read_only_audit_chain,rerun_read_only_validators,keep_narrowed_archive_provenance_only,monitor_reopen_conditions`.",
        "Opt-in action ids: `authorized_b4_ra_hi_source_policy_execution`.",
        "Required approval/driver: `I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json./run_b4_source_policy_after_opt_in.sh`.",
        "`ra2021_double_low_order_floor_limited_constraint_not_promoted`",
        "`hi2022_ra_half_double_partial_newton_failure_not_promoted`",
        "RA2021 double candidate pos/vel order and promoted rows:",
        "HI2022 rA_half double ok/failed/Newton-failure/promoted rows:",
        "HI2022 rA_half double repair target ok/failed and combined ok/rows/groups:",
    ]:
        checks.check(token in text, f"markdown missing token: {token}")

    if checks.errors:
        print("RA/HI post-execution attempt certificate validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("RA/HI post-execution attempt certificate validation: PASS")
    print("rows=20")
    print("source_policy_rows_promoted=0")
    print("external_superiority_ready_rows=0")
    print("source_policy_closed=0/40")
    print(f"source_policy_execution_invoked={authorized}")
    print("source_policy_execution_allowed_now=False")
    print("run_v047_invoked=False")
    print("submission_ready=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
