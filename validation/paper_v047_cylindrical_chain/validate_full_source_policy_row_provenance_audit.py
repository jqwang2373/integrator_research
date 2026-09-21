#!/usr/bin/env python3
"""Validate the full source-policy row provenance audit."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.json"
AUDIT_MD = PAPER / "FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.md"
AUDIT_CSV = PAPER / "FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.csv"


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
        audit = read_json(AUDIT_JSON)
        md = read_text(AUDIT_MD)
        row_ledger = read_json(PAPER / "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.json")
        packet = read_json(PAPER / "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json")
        matrix = read_json(PAPER / "RA_HI_SOURCE_POLICY_PROMOTION_BLOCKER_MATRIX.json")
        handoff = read_json(PAPER / "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json")
        with AUDIT_CSV.open(encoding="utf-8", newline="") as handle:
            csv_rows = list(csv.DictReader(handle))
    except Exception as exc:  # noqa: BLE001
        print(f"full source-policy row provenance audit validation: FAIL\n- {exc}")
        return 1

    rows = audit.get("rows", [])
    roots = audit.get("source_root_inventory", {})
    claim = audit.get("claim_boundary", {})
    expected_handoff = expected_handoff_summary(handoff)
    actual_handoff = audit.get("source_policy_execution_handoff", {})
    expected_safe_action_ids = [
        "rebuild_read_only_audit_chain",
        "rerun_read_only_validators",
        "keep_narrowed_archive_provenance_only",
        "monitor_reopen_conditions",
    ]
    expected_opt_in_action_ids = ["authorized_b4_ra_hi_source_policy_execution"]
    expected_required_approval_statement = handoff.get(
        "required_user_approval_statement"
    ) or expected_handoff.get("exact_required_user_approval_statement")
    expected_guarded_execution_driver = expected_handoff.get("guarded_execution_driver")
    expected_action_boundary = {
        "safe_without_b4_opt_in_count": 4,
        "opt_in_required_action_count": 1,
        "source_policy_execution_allowed_now": False,
        "exact_b4_opt_in_required_for_execution": True,
        "safe_action_ids": expected_safe_action_ids,
        "opt_in_action_ids": expected_opt_in_action_ids,
        "required_user_approval_statement": expected_required_approval_statement,
        "guarded_execution_driver": expected_guarded_execution_driver,
        "opt_in_required_command_count": expected_handoff.get(
            "opt_in_required_command_count"
        ),
        "opt_in_required_mapped_external_rows": expected_handoff.get(
            "opt_in_required_mapped_external_rows"
        ),
    }

    checks.check(audit.get("schema") == "full-source-policy-row-provenance-audit-v1", "schema changed")
    checks.check(
        audit.get("status") == "row_provenance_preflight_complete_source_policy_promotion_open",
        "status changed",
    )
    checks.check(audit.get("blocker_id") == "OC4", "blocker id changed")
    checks.check(audit.get("oc4_blocker_id") == "OC4", "OC4 blocker id alias changed")
    checks.check(audit.get("blocker_status") == "open", "OC4 blocker status changed")
    checks.check(audit.get("oc4_blocker_status") == "open", "OC4 blocker status alias changed")
    checks.check(audit.get("oc4_blocker_open") is True, "OC4 blocker was overclosed")
    checks.check(
        audit.get("closure_decision")
        == "remain_open_ready_for_authorized_execution_not_executed_not_promoted",
        "OC4 closure decision changed",
    )
    checks.check(
        audit.get("oc4_closure_decision")
        == audit.get("closure_decision")
        == "remain_open_ready_for_authorized_execution_not_executed_not_promoted",
        "OC4 closure decision alias changed",
    )
    checks.check(audit.get("closure_allowed_now") is False, "OC4 closure unexpectedly allowed now")
    checks.check(audit.get("oc4_closure_allowed_now") is False, "OC4 closure allowed alias changed")
    checks.check(
        audit.get("required_evidence_to_close")
        == [
            "authorized RA/HI source-policy closeout under the exact B4 opt-in or a new source-policy promotion artifact",
            "post-execution promotion validator records source-policy rows as closed",
            "work/precision rows bind error, order, runtime, Newton, and source-policy labels to the same promoted rows",
        ],
        "OC4 required evidence changed",
    )
    checks.check(audit.get("read_only") is True, "audit must be read-only")
    checks.check(audit.get("execution_invoked") is False, "audit unexpectedly invoked execution")
    checks.check(
        audit.get("source_policy_execution_invoked") is False,
        "audit unexpectedly records source-policy execution",
    )
    checks.check(
        audit.get("source_policy_execution_allowed_now") is False,
        "audit unexpectedly allows source-policy execution now",
    )
    checks.check(
        audit.get("exact_b4_opt_in_required_for_execution") is True,
        "audit lost exact B4 opt-in requirement",
    )
    checks.check(
        audit.get("required_user_approval_statement") == expected_required_approval_statement,
        "top-level approval statement missing or stale",
    )
    checks.check(
        audit.get("guarded_execution_driver") == expected_guarded_execution_driver,
        "top-level guarded driver missing or stale",
    )
    checks.check(audit.get("run_v047_invoked") is False, "audit unexpectedly invoked run_v047")
    checks.check(audit.get("v048_runner_invoked") is False, "audit unexpectedly invoked v048")
    checks.check(audit.get("packet_does_not_authorize_execution") is True, "audit authorizes execution")
    checks.check(
        audit.get("safe_without_b4_opt_in_count") == 4
        and audit.get("opt_in_required_action_count") == 1,
        "action boundary counts changed",
    )
    checks.check(
        audit.get("safe_action_ids") == expected_safe_action_ids
        and audit.get("opt_in_action_ids") == expected_opt_in_action_ids,
        "action boundary action IDs changed",
    )
    checks.check(
        audit.get("next_safe_action_ids") == audit.get("safe_action_ids") == expected_safe_action_ids
        and [item.get("id") for item in audit.get("next_safe_actions", [])]
        == expected_safe_action_ids
        and all(
            item.get("allowed_without_b4_opt_in") is True
            and item.get("does_not_execute_source_policy_commands") is True
            for item in audit.get("next_safe_actions", [])
        ),
        "top-level next-safe-action aliases changed",
    )
    checks.check(
        audit.get("action_boundary") == expected_action_boundary,
        "top-level action boundary stale or inconsistent with B4 handoff",
    )
    checks.check(audit.get("row_count") == row_ledger.get("row_count") == 40, "row count changed")
    checks.check(audit.get("rows_total") == 40, "top-level row alias changed")
    checks.check(len(rows) == len(csv_rows) == 40, "row table length changed")
    checks.check(
        audit.get("source_policy_rows_closed") == row_ledger.get("source_policy_rows_closed") == 0,
        "audit overcloses source-policy rows",
    )
    checks.check(audit.get("source_policy_rows_promoted") == 0, "audit overpromotes source-policy rows")
    checks.check(audit.get("source_policy_closed") is False, "top-level source-policy closure overclaimed")
    checks.check(audit.get("source_policy_closed_ratio") == "0/40", "top-level source-policy ratio changed")
    checks.check(
        audit.get("ready_command_count") == packet.get("ready_command_count") == 13,
        "ready command count changed",
    )
    checks.check(
        audit.get("mapped_external_row_count") == packet.get("ready_command_mapped_external_rows") == 20,
        "mapped external row count changed",
    )
    checks.check(audit.get("ready_commands_mapped_rows") == "13/20", "ready-command alias changed")
    traceability = handoff.get("command_row_traceability", {}).get("summary", {})
    checks.check(
        audit.get("command_traceability_summary") == traceability,
        "command traceability summary stale",
    )
    checks.check(audit.get("traceability_unique_rows") == 20, "traceability unique rows changed")
    checks.check(audit.get("traceability_reference_count") == 32, "traceability reference count changed")
    checks.check(
        audit.get("traceability_declared_reference_count") == 32,
        "traceability declared reference count changed",
    )
    checks.check(audit.get("traceability_mismatch_count") == 0, "traceability mismatch count changed")
    checks.check(
        audit.get("traceability_unique_traced_declared_mismatch") == "20/32/32/0",
        "traceability tuple alias changed",
    )
    checks.check(
        audit.get("terminal_unable_to_reproduce_rows")
        == row_ledger.get("source_policy_rows_unable_to_reproduce")
        == 20,
        "terminal unable-to-reproduce row count changed",
    )
    checks.check(
        audit.get("attempted_not_reproducible_rows")
        == row_ledger.get("source_policy_rows_attempted_not_reproducible")
        == 20,
        "attempted-not-reproducible row count changed",
    )
    checks.check(
        audit.get("source_policy_rows_unable_to_reproduce")
        == row_ledger.get("source_policy_rows_unable_to_reproduce")
        == 20,
        "unable-to-reproduce row count changed",
    )
    checks.check(
        audit.get("source_policy_rows_still_requiring_execution_or_promotion")
        == row_ledger.get("source_policy_rows_still_requiring_execution_or_promotion")
        == 20,
        "still-requiring row count changed",
    )
    checks.check(audit.get("provenance_preflight_complete_rows") == 40, "provenance preflight incomplete")
    checks.check(audit.get("provenance_preflight") == "40/40", "top-level provenance preflight ratio changed")
    checks.check(audit.get("provenance_preflight_complete") is True, "top-level provenance preflight flag changed")
    checks.check(audit.get("public_source_root_rows") == matrix.get("public_source_root_available_rows") == 20, "public-root row count changed")
    checks.check(audit.get("command_mapped_rows") == packet.get("ready_command_mapped_external_rows") == 20, "command-mapped row count changed")
    checks.check(audit.get("rows_with_all_command_outputs_present") == matrix.get("rows_with_all_command_outputs_present") == 20, "output-present row count changed")
    checks.check(audit.get("promotion_ready_rows") == 0, "audit marks rows promotion-ready")
    checks.check(audit.get("source_policy_reproduction_complete_rows") == 0, "audit marks source-policy reproduction complete")
    checks.check(audit.get("handoff_execution_authorized") is False, "handoff authorization changed")
    checks.check(audit.get("handoff_commands_not_run_by_handoff") is True, "handoff execution marker changed")
    checks.check(actual_handoff == expected_handoff, "source-policy handoff summary stale")
    checks.check(
        actual_handoff.get("status") == "source_policy_execution_handoff_ready_not_authorized_not_run",
        "handoff status changed",
    )
    checks.check(actual_handoff.get("execution_authorized") is False, "handoff unexpectedly authorized")
    checks.check(actual_handoff.get("commands_not_run_by_handoff") is True, "handoff commands-not-run changed")
    checks.check(
        actual_handoff.get("exact_required_user_approval_statement")
        == "I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json.",
        "handoff exact approval statement changed",
    )
    checks.check(
        actual_handoff.get("guarded_execution_driver") == "run_b4_source_policy_after_opt_in.sh",
        "handoff driver changed",
    )
    checks.check(actual_handoff.get("driver_requires_exact_approval") is True, "handoff driver exact-approval guard missing")
    checks.check(actual_handoff.get("driver_does_not_authorize_execution") is True, "handoff driver authorization boundary missing")
    checks.check(actual_handoff.get("opt_in_required_command_count") == 13, "handoff opt-in command count changed")
    checks.check(actual_handoff.get("opt_in_required_mapped_external_rows") == 20, "handoff mapped row count changed")
    checks.check(actual_handoff.get("terminal_unable_to_reproduce_rows") == 20, "handoff terminal unable row count changed")

    checks.check(roots.get("ra2021_absolute_coordinate", {}).get("exists") is True, "RA2021 source root missing")
    checks.check(roots.get("hi2022_half_implicit", {}).get("exists") is True, "HI2022 source root missing")
    checks.check(roots.get("ra2021_absolute_coordinate", {}).get("python_file_count", 0) > 0, "RA2021 Python inventory empty")
    checks.check(roots.get("hi2022_half_implicit", {}).get("python_file_count", 0) > 0, "HI2022 Python inventory empty")
    checks.check(roots.get("ra2021_absolute_coordinate", {}).get("digest"), "RA2021 digest missing")
    checks.check(roots.get("hi2022_half_implicit", {}).get("digest"), "HI2022 digest missing")

    source_root_status_counts: dict[str, int] = {}
    for row in rows:
        source_root_status_counts[row.get("source_root_status", "")] = (
            source_root_status_counts.get(row.get("source_root_status", ""), 0) + 1
        )
        checks.check(row.get("provenance_preflight_complete") is True, f"row preflight incomplete: {row.get('row_key')}")
        checks.check(row.get("promotion_ready_now") is False, f"row unexpectedly promotion-ready: {row.get('row_key')}")
    checks.check(source_root_status_counts.get("public_source_root_present") == 20, "public source-root status count changed")
    checks.check(source_root_status_counts.get("no_public_or_no_source_equivalent_code_root") == 20, "no-code/source-equivalent status count changed")

    checks.check(claim.get("provenance_preflight_complete_is_not_source_policy_closure") is True, "claim boundary missing provenance-not-closure")
    checks.check(claim.get("source_policy_promotion_still_requires_authorized_closeout_or_new_artifact") is True, "claim boundary missing promotion requirement")
    checks.check(claim.get("b4_can_close_now") is False and claim.get("b7_can_close_now") is False, "claim boundary overcloses B4/B7")

    for token in [
        "provenance preflight is not source-policy promotion",
        "Provenance preflight complete rows: `40/40`",
        "Attempted-not-reproducible/promoted rows: `20/0`.",
        "Ready commands/mapped external rows: `13/20`.",
        "Command traceability unique/traced/declared/mismatch rows: `20/32/32/0`.",
        "OC4 aliases blocker/status/closure/allowed-now: `OC4/open/remain_open_ready_for_authorized_execution_not_executed_not_promoted/False`.",
        "OC4 ready-command and traceability aliases: `13/20/20/32/32/0`.",
        "Source-policy closed/promotion-ready rows: `0/0`",
        "Blocker/status/closure decision: `OC4/open/remain_open_ready_for_authorized_execution_not_executed_not_promoted`.",
        "Closure allowed now / OC4 blocker open: `False/True`.",
        "Source-policy execution invoked/allowed now: `False/False`",
        "Action boundary safe/opt-in action counts: `4/1`",
        "Required approval/driver: `I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json./run_b4_source_policy_after_opt_in.sh`.",
        "Top-level next safe action ids: `rebuild_read_only_audit_chain,rerun_read_only_validators,keep_narrowed_archive_provenance_only,monitor_reopen_conditions`.",
        "Handoff status/driver: `source_policy_execution_handoff_ready_not_authorized_not_run/run_b4_source_policy_after_opt_in.sh`",
        "Handoff exact approval: `I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json.`",
        "Handoff driver requires exact approval/does not authorize: `True/True`",
        "Handoff opt-in commands/mapped rows/terminal unable rows: `13/20/20`",
        "B4/B7 can close now under full source-policy: `False/False`",
    ]:
        checks.check(token in md, f"markdown missing token: {token}")

    if checks.errors:
        print("full source-policy row provenance audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1
    print("full source-policy row provenance audit validation: PASS")
    print(f"rows={audit.get('row_count')}")
    print(f"provenance_preflight={audit.get('provenance_preflight_complete_rows')}/{audit.get('row_count')}")
    print(f"source_policy_closed={audit.get('source_policy_rows_closed')}/{audit.get('source_policy_rows_total')}")
    print(f"source_policy_rows_promoted={audit.get('source_policy_rows_promoted')}")
    print(f"terminal_unable_to_reproduce_rows={audit.get('terminal_unable_to_reproduce_rows')}")
    print(f"attempted_not_reproducible_rows={audit.get('attempted_not_reproducible_rows')}")
    print(f"promotion_ready_rows={audit.get('promotion_ready_rows')}")
    print(f"closure_decision={audit.get('closure_decision')}")
    print(f"oc4_blocker_id={audit.get('oc4_blocker_id')}")
    print(f"oc4_blocker_status={audit.get('oc4_blocker_status')}")
    print(f"oc4_closure_decision={audit.get('oc4_closure_decision')}")
    print(f"oc4_closure_allowed_now={audit.get('oc4_closure_allowed_now')}")
    print(f"oc4_blocker_open={audit.get('oc4_blocker_open')}")
    print(f"ready_commands_mapped_rows={audit.get('ready_commands_mapped_rows')}")
    print(
        "traceability_unique_traced_declared_mismatch="
        f"{audit.get('traceability_unique_traced_declared_mismatch')}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
