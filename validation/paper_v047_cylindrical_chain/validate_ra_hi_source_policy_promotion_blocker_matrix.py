#!/usr/bin/env python3
"""Validate the RA/HI source-policy promotion blocker matrix."""

from __future__ import annotations

import csv
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
EXPECTED_BLOCKER_COUNTS = {
    "hi2022_ra_half_double_partial_newton_failure_not_promoted": 1,
    "hi2022_selected_coarse_trio_not_full_public_grid_not_promoted": 7,
    "ra2021_closed_loop_T0p1_mixed_reference_not_source_policy": 6,
    "ra2021_double_low_order_floor_limited_constraint_not_promoted": 3,
    "ra2021_single_floor_limited_public_h_tranche_not_promoted": 3,
}
EXPECTED_ATTEMPT_STATUS_COUNTS = {
    "approved_driver_outputs_present_not_promoted": 9,
    "diagnosis_only_low_order_floor_limited_not_promoted": 3,
    "diagnosis_only_partial_newton_failure_not_promoted": 1,
    "selected_candidate_executed_not_promoted": 7,
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


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


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
        matrix = read_json(PAPER / "RA_HI_SOURCE_POLICY_PROMOTION_BLOCKER_MATRIX.json")
        matrix_md = read_text(PAPER / "RA_HI_SOURCE_POLICY_PROMOTION_BLOCKER_MATRIX.md")
        csv_rows = read_csv_rows(PAPER / "RA_HI_SOURCE_POLICY_PROMOTION_BLOCKER_MATRIX.csv")
        b4 = read_json(PAPER / "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.json")
        post_attempt = read_json(PAPER / "RA_HI_SOURCE_POLICY_POST_EXECUTION_ATTEMPT_CERTIFICATE.json")
        closeout = read_json(PAPER / "RA_HI_SOURCE_POLICY_CLOSEOUT_CHECKLIST.json")
        output_inventory = read_json(PAPER / "RA_HI_SOURCE_POLICY_OUTPUT_INVENTORY.json")
        b4_handoff = read_json(PAPER / "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json")
    except Exception as exc:  # noqa: BLE001
        print(f"RA/HI source-policy promotion blocker matrix validation: FAIL\n- {exc}")
        return 1

    rows = [row for row in matrix.get("rows", []) if isinstance(row, dict)]
    ra_rows = [row for row in rows if row.get("suite_id") == "ra2021_absolute_coordinate"]
    hi_rows = [row for row in rows if row.get("suite_id") == "hi2022_half_implicit"]
    b4_ra_hi_rows = [
        row
        for row in b4.get("rows", [])
        if isinstance(row, dict)
        and row.get("suite_id") in {"ra2021_absolute_coordinate", "hi2022_half_implicit"}
    ]
    expected_handoff = expected_handoff_summary(b4_handoff)
    actual_handoff = matrix.get("source_policy_execution_handoff", {})

    checks.check(matrix.get("schema") == "ra-hi-source-policy-promotion-blocker-matrix-v1", "schema changed")
    checks.check(
        matrix.get("status") == "ra_hi_public_root_rows_not_promoted_source_policy_open",
        "status changed",
    )
    checks.check(matrix.get("read_only") is True, "matrix must remain read-only")
    checks.check(matrix.get("row_count") == len(rows) == len(csv_rows) == 20, "row count changed")
    checks.check(len(ra_rows) == matrix.get("ra2021_row_count") == 12, "RA2021 row count changed")
    checks.check(len(hi_rows) == matrix.get("hi2022_row_count") == 8, "HI2022 row count changed")
    checks.check(
        {(row.get("suite_id"), row.get("method"), row.get("example")) for row in rows}
        == {(row.get("suite_id"), row.get("method"), row.get("example")) for row in b4_ra_hi_rows},
        "RA/HI coverage no longer matches B4 readiness ledger",
    )
    checks.check(matrix.get("public_source_root_available_rows") == 20, "public-root row count changed")
    checks.check(matrix.get("no_public_code_rows_included") == 0, "matrix must exclude no-public-code rows")
    checks.check(matrix.get("source_policy_rows_closed") == 0, "matrix overcloses source-policy rows")
    checks.check(matrix.get("source_policy_rows_promoted") == 0, "matrix overpromotes source-policy rows")
    checks.check(matrix.get("source_policy_rows_not_promoted") == 20, "not-promoted row count changed")
    checks.check(
        matrix.get("source_policy_rows_still_requiring_execution_or_promotion") == 20,
        "open RA/HI row count changed",
    )
    checks.check(matrix.get("source_policy_closed") is False, "source-policy closed alias overclaims")
    checks.check(matrix.get("source_policy_closed_ratio") == "0/20", "source-policy closed ratio alias changed")
    checks.check(
        matrix.get("source_policy_reproduction_complete") is False,
        "source-policy reproduction-complete alias overclaims",
    )
    checks.check(matrix.get("promoted") == 0, "promoted alias overclaims")
    checks.check(matrix.get("not_promoted") == 20, "not-promoted alias changed")
    checks.check(matrix.get("attempted_not_reproducible") == 0, "attempted-not-reproducible alias changed")
    checks.check(
        matrix.get("command_mapped_output_present") == "20/20",
        "command mapped/output-present alias changed",
    )
    checks.check(
        matrix.get("command_mapped_output_present_rows") == 20,
        "command mapped/output-present row alias changed",
    )
    checks.check(
        matrix.get("all_command_mapped_outputs_present") is True,
        "all command-mapped outputs-present alias changed",
    )
    checks.check(
        matrix.get("current_evidence_terminal_not_promotable_rows") == 20,
        "current-evidence terminal/not-promotable row count changed",
    )
    checks.check(
        matrix.get("future_promotion_requires_authorized_execution_or_new_artifact_rows") == 20,
        "future promotion reopen-boundary row count changed",
    )
    checks.check(
        matrix.get("source_policy_reproduction_complete_rows") == 0,
        "matrix overclaims source-policy reproduction completion",
    )
    checks.check(matrix.get("attempted_not_reproducible_rows") == 0, "RA/HI rows misclassified as no-public-code")
    checks.check(matrix.get("command_mapped_rows") == 20, "command-mapped row count changed")
    checks.check(matrix.get("rows_with_all_command_outputs_present") == 20, "output-present row count changed")
    checks.check(matrix.get("ready_to_launch_after_explicit_opt_in_rows") == 20, "launch-ready row count changed")
    checks.check(matrix.get("source_policy_1e_4_opt_in_required_rows") == 12, "RA 1e-4 row count changed")
    checks.check(matrix.get("post_execution_decision_counts") == {"not_promoted": 20}, "decision counts changed")
    checks.check(
        matrix.get("post_execution_attempt_status_counts") == EXPECTED_ATTEMPT_STATUS_COUNTS,
        "attempt-status counts changed",
    )
    checks.check(matrix.get("primary_promotion_blocker_counts") == EXPECTED_BLOCKER_COUNTS, "blocker counts changed")
    checks.check(
        matrix.get("output_inventory_status") == "existing_expected_outputs_present_not_promotion_evidence",
        "output inventory status changed",
    )
    checks.check(matrix.get("output_inventory_command_count") == 13, "output inventory command count changed")
    checks.check(matrix.get("output_inventory_outputs_existing") == 13, "output inventory output count changed")
    checks.check(matrix.get("output_inventory_closed_rows") == 0, "output inventory overclosed rows")
    checks.check(actual_handoff == expected_handoff, "B4 execution handoff summary not preserved")
    checks.check(
        closeout.get("source_policy_execution_handoff") == expected_handoff,
        "closeout handoff summary drifted from B4 handoff",
    )
    checks.check(
        output_inventory.get("source_policy_execution_handoff") == expected_handoff,
        "output inventory handoff summary drifted from B4 handoff",
    )
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
        matrix.get("source_policy_execution_allowed_now")
        == b4_handoff.get("source_policy_execution_allowed_now")
        is False
        and matrix.get("source_policy_execution_invoked")
        == b4_handoff.get("source_policy_execution_invoked")
        is False
        and matrix.get("exact_b4_opt_in_required_for_execution")
        == b4_handoff.get("exact_b4_opt_in_required_for_execution")
        is True
        and matrix.get("safe_action_ids")
        == b4_handoff.get("safe_action_ids")
        == EXPECTED_SAFE_ACTION_IDS
        and matrix.get("opt_in_action_ids")
        == b4_handoff.get("opt_in_action_ids")
        == EXPECTED_OPT_IN_ACTION_IDS
        and matrix.get("required_user_approval_statement") == EXPECTED_APPROVAL
        and matrix.get("guarded_execution_driver") == "run_b4_source_policy_after_opt_in.sh",
        "top-level source-policy execution aliases stale",
    )
    checks.check(matrix.get("closeout_execution_invoked") is False, "matrix claims closeout execution")
    checks.check(matrix.get("b4_can_close_now") is False, "matrix overcloses B4")
    checks.check(matrix.get("b7_can_close_now") is False, "matrix overcloses B7")
    checks.check(matrix.get("external_superiority_ready_rows") == 0, "matrix overclaims external superiority")
    checks.check(matrix.get("heavy_numerical_run_invoked") is False, "matrix invoked heavy run")
    checks.check(matrix.get("run_v047_invoked") is False, "matrix invoked run_v047")
    checks.check(matrix.get("v048_runner_invoked") is False, "matrix invoked v048")
    checks.check(post_attempt.get("row_count") == 20, "post-attempt source row count changed")
    checks.check(
        output_inventory.get("coverage", {}).get("source_policy_rows_closed_by_inventory") == 0,
        "inventory overclosed rows",
    )

    for row in rows:
        label = f"{row.get('suite_id')}:{row.get('method')}:{row.get('example')}"
        checks.check(row.get("public_source_root_available") is True, f"{label} lost public-root marker")
        checks.check(row.get("row_id") == label, f"{label} missing stable row id")
        checks.check(isinstance(row.get("source_lane_id"), str), f"{label} missing source lane id")
        checks.check(row.get("no_public_code_case") is False, f"{label} misclassified as no-public-code")
        checks.check(row.get("source_policy_disposition") == "promotion_open", f"{label} disposition changed")
        checks.check(row.get("post_execution_decision") == "not_promoted", f"{label} promotion decision changed")
        checks.check(row.get("source_policy_closed") is False, f"{label} overclosed")
        checks.check(row.get("source_policy_reproduction_complete") is False, f"{label} overclaims reproduction")
        checks.check(row.get("external_superiority_ready") is False, f"{label} overclaims")
        checks.check(row.get("counts_as_open_execution_queue") is True, f"{label} should remain open")
        checks.check(row.get("ready_to_launch_after_explicit_opt_in") is True, f"{label} launch boundary changed")
        checks.check(row.get("command_refs"), f"{label} missing command refs")
        checks.check(row.get("all_command_outputs_present") is True, f"{label} missing command output evidence")
        checks.check(
            row.get("current_evidence_terminal_not_promotable") is True,
            f"{label} missing terminal current-evidence marker",
        )
        checks.check(
            row.get("current_evidence_disposition") == "terminal_current_evidence_not_promotable",
            f"{label} current-evidence disposition changed",
        )
        checks.check(
            row.get("existing_attempt_output_present_not_promotion_evidence") is True,
            f"{label} missing output-present-not-promotion marker",
        )
        checks.check(
            row.get("future_promotion_requires_authorized_execution_or_new_artifact") is True,
            f"{label} missing future-promotion reopen boundary",
        )
        checks.check(
            row.get("future_promotion_reopen_condition")
            == "exact_b4_opt_in_authorized_execution_closeout_or_new_source_policy_promotion_artifact",
            f"{label} future-promotion reopen condition changed",
        )
        checks.check(row.get("blocking_reasons"), f"{label} missing blocking reasons")
        if row.get("suite_id") == "ra2021_absolute_coordinate":
            checks.check(row.get("source_policy_1e_4_opt_in_required") is True, f"{label} should require 1e-4 opt-in")
        if row.get("suite_id") == "hi2022_half_implicit":
            checks.check(row.get("source_policy_1e_4_opt_in_required") is False, f"{label} should not require 1e-4")

    summary = {item.get("suite_id"): item for item in matrix.get("suite_summary", []) if isinstance(item, dict)}
    checks.check(summary.get("ra2021_absolute_coordinate", {}).get("row_count") == 12, "RA summary row count changed")
    checks.check(summary.get("hi2022_half_implicit", {}).get("row_count") == 8, "HI summary row count changed")
    checks.check(
        summary.get("ra2021_absolute_coordinate", {}).get("source_policy_1e_4_opt_in_required_rows") == 12,
        "RA summary 1e-4 count changed",
    )
    checks.check(
        summary.get("hi2022_half_implicit", {}).get("source_policy_1e_4_opt_in_required_rows") == 0,
        "HI summary 1e-4 count changed",
    )

    for token in [
        "Status: `ra_hi_public_root_rows_not_promoted_source_policy_open`.",
        "Rows: `20`; RA/HI `12/8`.",
        "Public-source-root rows: `20`.",
        "No-public-code rows included: `0`.",
        "Direct aliases source-policy-closed/ratio/reproduction-complete: `False/0/20/False`.",
        "Direct aliases promoted/not-promoted/attempted-not-reproducible: `0/20/0`.",
        "Direct alias command-mapped/output-present: `20/20`; all present: `True`.",
        "Source-policy rows closed/promoted/not-promoted: `0/0/20`.",
        "Still requiring execution or promotion: `20`.",
        "Current-evidence terminal/not-promotable rows: `20`.",
        "Future promotion requires authorized execution or new artifact rows: `20`.",
        "Source-policy reproduction complete rows: `0`.",
        "Attempted-not-reproducible rows: `0`.",
        "Command-mapped/output-present rows: `20/20`.",
        "Rows requiring explicit `1e-4` opt-in: `12`.",
        "Source-policy execution allowed now/invoked/exact opt-in required: `False/False/True`.",
        "Safe action ids: `['rebuild_read_only_audit_chain', 'rerun_read_only_validators', 'keep_narrowed_archive_provenance_only', 'monitor_reopen_conditions']`; opt-in action ids: `['authorized_b4_ra_hi_source_policy_execution']`.",
        f"Source-policy execution handoff exact approval/driver: `{EXPECTED_APPROVAL}/run_b4_source_policy_after_opt_in.sh/True/True/13/20/20`.",
        "Source-policy execution handoff authorized/commands-not-run: `False/True`.",
        "B4/B7 can close now: `False/False`.",
        "Current evidence is terminal/not-promotable for all 20 rows, while source-policy reproduction remains incomplete.",
    ]:
        checks.check(token in matrix_md, f"markdown missing token: {token}")

    if checks.errors:
        print("RA/HI source-policy promotion blocker matrix validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("RA/HI source-policy promotion blocker matrix validation: PASS")
    print("rows=20")
    print("source_policy_closed=0/20")
    print(f"source_policy_closed_alias={matrix.get('source_policy_closed')}")
    print("not_promoted=20")
    print("attempted_not_reproducible=0")
    print(f"command_mapped_output_present={matrix.get('command_mapped_output_present')}")
    print(f"source_policy_execution_allowed_now={matrix.get('source_policy_execution_allowed_now')}")
    print(f"source_policy_execution_invoked={matrix.get('source_policy_execution_invoked')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
