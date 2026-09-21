#!/usr/bin/env python3
"""Validate the RA/HI source-policy closeout checklist."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
EXPECTED_APPROVAL = (
    "I explicitly approve running the B4 source-policy execution commands listed in "
    "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json."
)
EXPECTED_SAFE_ACTION_IDS = [
    "rebuild_read_only_audit_chain",
    "rerun_read_only_validators",
    "keep_narrowed_archive_provenance_only",
    "monitor_reopen_conditions",
]
EXPECTED_OPT_IN_ACTION_IDS = ["authorized_b4_ra_hi_source_policy_execution"]


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


def expected_handoff_summary(handoff: dict[str, Any]) -> dict[str, Any]:
    approval_boundary = handoff.get("approval_boundary", {})
    guarded_driver = approval_boundary.get("guarded_execution_driver", {})
    opt_in = handoff.get("opt_in_required_actions", {})
    row_state = handoff.get("source_policy_row_state", {})
    return {
        "status": handoff.get("status"),
        "execution_authorized": handoff.get("execution_authorized"),
        "commands_not_run_by_handoff": handoff.get("commands_not_run_by_handoff"),
        "exact_required_user_approval_statement": approval_boundary.get(
            "exact_required_user_approval_statement"
        ),
        "guarded_execution_driver": guarded_driver.get("path"),
        "driver_requires_exact_approval": guarded_driver.get(
            "requires_exact_approval_argument"
        ),
        "driver_does_not_authorize_execution": guarded_driver.get(
            "driver_does_not_authorize_execution"
        ),
        "opt_in_required_command_count": opt_in.get("command_count"),
        "opt_in_required_mapped_external_rows": opt_in.get("mapped_external_rows"),
        "terminal_unable_to_reproduce_rows": row_state.get("unable_to_reproduce"),
    }


def main() -> int:
    checks = Checks()
    try:
        checklist = read_json(PAPER / "RA_HI_SOURCE_POLICY_CLOSEOUT_CHECKLIST.json")
        checklist_md = read_text(PAPER / "RA_HI_SOURCE_POLICY_CLOSEOUT_CHECKLIST.md")
        opt_in = read_json(PAPER / "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json")
        b4_handoff = read_json(PAPER / "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json")
        post = read_json(PAPER / "RA_HI_SOURCE_POLICY_POST_EXECUTION_ATTEMPT_CERTIFICATE.json")
        ledger = read_json(PAPER / "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.json")
        output_inventory = read_json(PAPER / "RA_HI_SOURCE_POLICY_OUTPUT_INVENTORY.json")
    except Exception as exc:  # noqa: BLE001
        print(f"RA/HI source-policy closeout checklist validation: FAIL\n- {exc}")
        return 1

    boundary = checklist.get("guarded_execution_boundary", {})
    coverage = checklist.get("coverage", {})
    suite_closeout = checklist.get("suite_closeout", {})
    ra = suite_closeout.get("ra2021_absolute_coordinate", {})
    hi = suite_closeout.get("hi2022_half_implicit", {})
    rows = checklist.get("rows", [])
    disposition = checklist.get("not_promoted_disposition", {})
    batches = checklist.get("execution_batches", [])
    expected_handoff = expected_handoff_summary(b4_handoff)
    actual_handoff = checklist.get("source_policy_execution_handoff", {})

    checks.check(checklist.get("schema") == "ra-hi-source-policy-closeout-checklist-v1", "schema changed")
    checks.check(
        checklist.get("status") == "ready_for_authorized_execution_closeout_not_executed_not_promoted",
        "status changed",
    )
    checks.check(checklist.get("read_only") is True, "checklist must be read-only")
    checks.check(
        boundary.get("exact_required_user_approval_statement")
        == opt_in.get("required_user_approval_statement")
        == EXPECTED_APPROVAL,
        "exact opt-in phrase not preserved",
    )
    checks.check(boundary.get("explicit_user_opt_in_required_before_any_command") is True, "opt-in guard missing")
    checks.check(boundary.get("execution_invoked_by_packet") is False, "packet execution unexpectedly invoked")
    checks.check(boundary.get("packet_does_not_authorize_execution") is True, "packet authorization boundary changed")
    checks.check(boundary.get("heavy_numerical_run_invoked") is False, "heavy run invoked")
    checks.check(boundary.get("run_v047_invoked") is False, "run_v047 invoked")
    checks.check(boundary.get("v048_runner_invoked") is False, "v048 runner invoked by packet")
    checks.check(actual_handoff == expected_handoff, "B4 execution handoff summary not preserved")
    checks.check(
        actual_handoff.get("status") == "source_policy_execution_handoff_ready_not_authorized_not_run",
        "handoff status changed",
    )
    checks.check(actual_handoff.get("execution_authorized") is False, "handoff unexpectedly authorized")
    checks.check(actual_handoff.get("commands_not_run_by_handoff") is True, "handoff command boundary changed")
    checks.check(actual_handoff.get("guarded_execution_driver") == "run_b4_source_policy_after_opt_in.sh", "handoff driver changed")
    checks.check(actual_handoff.get("driver_requires_exact_approval") is True, "handoff driver exact-approval guard missing")
    checks.check(actual_handoff.get("driver_does_not_authorize_execution") is True, "handoff driver authorization boundary missing")
    checks.check(actual_handoff.get("opt_in_required_command_count") == 13, "handoff opt-in command count changed")
    checks.check(actual_handoff.get("opt_in_required_mapped_external_rows") == 20, "handoff mapped row count changed")
    checks.check(actual_handoff.get("terminal_unable_to_reproduce_rows") == 20, "handoff terminal unable row count changed")
    checks.check(
        checklist.get("source_policy_execution_allowed_now")
        == b4_handoff.get("source_policy_execution_allowed_now")
        is False
        and checklist.get("source_policy_execution_invoked")
        == b4_handoff.get("source_policy_execution_invoked")
        is False
        and checklist.get("exact_b4_opt_in_required_for_execution")
        == b4_handoff.get("exact_b4_opt_in_required_for_execution")
        is True
        and checklist.get("safe_action_ids")
        == b4_handoff.get("safe_action_ids")
        == EXPECTED_SAFE_ACTION_IDS
        and checklist.get("opt_in_action_ids")
        == b4_handoff.get("opt_in_action_ids")
        == EXPECTED_OPT_IN_ACTION_IDS
        and checklist.get("required_user_approval_statement") == EXPECTED_APPROVAL
        and checklist.get("guarded_execution_driver") == "run_b4_source_policy_after_opt_in.sh",
        "top-level source-policy execution aliases stale",
    )
    checks.check(checklist.get("ready_command_count") == 13, "top-level ready command alias changed")
    checks.check(
        checklist.get("ready_command_mapped_external_rows")
        == checklist.get("ready_command_mapped_rows")
        == 20,
        "top-level ready mapped row alias changed",
    )
    checks.check(
        checklist.get("source_policy_rows_total") == 20
        and checklist.get("source_policy_rows_completed") == 0
        and checklist.get("source_policy_rows_promoted") == 0
        and checklist.get("external_superiority_ready_rows") == 0
        and checklist.get("source_policy_closed") is False
        and checklist.get("source_policy_closed_ratio") == "0/20",
        "top-level source-policy row aliases stale",
    )
    checks.check(
        checklist.get("can_close_ra_hi_source_policy_rows_now") is False
        and checklist.get("can_claim_external_superiority_from_ra_hi_now") is False
        and checklist.get("b4_can_close") is False
        and checklist.get("b7_can_close") is False,
        "top-level closeout decision aliases overclaim",
    )
    checks.check(
        checklist.get("exact_approval_statement") == EXPECTED_APPROVAL
        and checklist.get("opt_in_required") is True
        and checklist.get("execution_invoked") is False,
        "top-level opt-in/execution aliases stale",
    )

    checks.check(coverage.get("source_policy_rows_total") == 20, "RA/HI row total changed")
    checks.check(coverage.get("ra2021_rows") == 12, "RA2021 row count changed")
    checks.check(coverage.get("hi2022_rows") == 8, "HI2022 row count changed")
    checks.check(coverage.get("ready_command_count") == opt_in.get("ready_command_count") == 13, "ready command count changed")
    checks.check(
        coverage.get("ready_command_mapped_external_rows")
        == opt_in.get("ready_command_mapped_external_rows")
        == 20,
        "mapped external row count changed",
    )
    checks.check(
        coverage.get("ledger_rows_still_requiring_execution_or_promotion")
        == ledger.get("source_policy_rows_still_requiring_execution_or_promotion")
        == 20,
        "ledger open row count changed",
    )
    checks.check(
        coverage.get("post_certificate_rows_still_requiring_execution_or_promotion")
        == post.get("rows_still_requiring_execution_or_promotion")
        == 20,
        "post-certificate open row count changed",
    )
    checks.check(coverage.get("source_policy_rows_promoted") == 0, "checklist overpromotes rows")
    checks.check(coverage.get("source_policy_rows_completed") == 0, "checklist overcompletes rows")
    checks.check(coverage.get("external_superiority_ready_rows") == 0, "checklist enables external superiority")
    checks.check(
        coverage.get("output_inventory_status")
        == output_inventory.get("status")
        == "existing_expected_outputs_present_not_promotion_evidence",
        "output inventory status not propagated",
    )
    checks.check(
        coverage.get("output_inventory_command_count")
        == output_inventory.get("coverage", {}).get("command_count")
        == 13,
        "output inventory command count changed",
    )
    checks.check(
        coverage.get("output_inventory_expected_outputs_existing")
        == output_inventory.get("coverage", {}).get("expected_output_existing_count")
        == 13,
        "output inventory output count changed",
    )
    checks.check(
        coverage.get("output_inventory_expected_summaries_existing")
        == output_inventory.get("coverage", {}).get("expected_summary_existing_count")
        == 8,
        "output inventory summary count changed",
    )
    checks.check(
        coverage.get("output_inventory_csv_data_rows")
        == output_inventory.get("coverage", {}).get("expected_output_csv_data_rows")
        == 54,
        "output inventory data-row count changed",
    )
    checks.check(
        coverage.get("output_inventory_source_policy_rows_closed")
        == output_inventory.get("coverage", {}).get("source_policy_rows_closed_by_inventory")
        == 0,
        "output inventory closes source-policy rows",
    )

    checks.check(len(rows) == post.get("row_count") == 20, "row inventory changed")
    checks.check(len(batches) == 2, "execution batch count changed")
    checks.check(ra.get("row_count") == 12 and ra.get("command_count") == 5, "RA2021 closeout coverage changed")
    checks.check(hi.get("row_count") == 8 and hi.get("command_count") == 8, "HI2022 closeout coverage changed")
    checks.check(ra.get("source_policy_1e_4_opt_in_required") is True, "RA2021 1e-4 opt-in boundary changed")
    checks.check(hi.get("source_policy_1e_4_opt_in_required") is False, "HI2022 1e-4 boundary changed")
    checks.check(
        "source_default_horizon_and_h_policy_reproduced" in ra.get("false_closure_criteria", []),
        "RA2021 source-policy horizon blocker missing",
    )
    checks.check(
        "runtime_policy_tied_to_source_policy_order_rows" in ra.get("false_closure_criteria", []),
        "RA2021 runtime binding blocker missing",
    )
    checks.check(
        "full_T8_public_policy_completed" in hi.get("false_closure_criteria", []),
        "HI2022 full T=8 policy blocker missing",
    )
    checks.check(
        "velocity_mapping_and_error_norm_closed" in hi.get("false_closure_criteria", []),
        "HI2022 velocity/norm blocker missing",
    )
    checks.check(
        "rA_half:double_pendulum" in hi.get("partial_or_failed_shards", []),
        "HI2022 rA_half double failure not preserved",
    )
    checks.check(
        disposition.get("can_close_ra_hi_source_policy_rows_now") is False,
        "RA/HI rows unexpectedly closable",
    )
    checks.check(
        disposition.get("can_claim_external_superiority_from_ra_hi_now") is False,
        "RA/HI external superiority unexpectedly allowed",
    )
    checks.check(disposition.get("source_policy_closed_rows_after_this_checklist") == 0, "checklist closes rows")
    checks.check(disposition.get("b4_can_close_from_this_checklist") is False, "checklist closes B4")
    checks.check(disposition.get("b7_can_close_from_this_checklist") is False, "checklist closes B7")

    for token in [
        "Status: `ready_for_authorized_execution_closeout_not_executed_not_promoted`.",
        "Rows: RA2021 `12`, HI2022 `8`, total `20`.",
        "Ready commands: `13` mapped to `20` rows.",
        "Output inventory: `existing_expected_outputs_present_not_promotion_evidence`; outputs/summaries/data rows `13/8/54`; source-policy rows closed `0`.",
        "Source-policy closed/ratio: `False/0/20`.",
        f"Exact authorization phrase: `{EXPECTED_APPROVAL}`.",
        "Source-policy execution allowed now/invoked/exact opt-in required: `False/False/True`.",
        "Safe action ids: `['rebuild_read_only_audit_chain', 'rerun_read_only_validators', 'keep_narrowed_archive_provenance_only', 'monitor_reopen_conditions']`; opt-in action ids: `['authorized_b4_ra_hi_source_policy_execution']`.",
        f"Source-policy execution handoff exact approval/driver: `{EXPECTED_APPROVAL}/run_b4_source_policy_after_opt_in.sh/True/True/13/20/20`.",
        "Source-policy execution handoff authorized/commands-not-run: `False/True`.",
        "`ra2021_absolute_coordinate`",
        "`hi2022_half_implicit`",
        "Closeout now: rows `0/20`, B4/B7 `False/False`.",
    ]:
        checks.check(token in checklist_md, f"markdown missing token: {token}")

    if checks.errors:
        print("RA/HI source-policy closeout checklist validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("RA/HI source-policy closeout checklist validation: PASS")
    print("rows=20")
    print("ra_hi=12/8")
    print("ready_commands=13")
    print("source_policy_closed=0/20")
    print(f"source_policy_execution_allowed_now={checklist.get('source_policy_execution_allowed_now')}")
    print(f"source_policy_execution_invoked={checklist.get('source_policy_execution_invoked')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
