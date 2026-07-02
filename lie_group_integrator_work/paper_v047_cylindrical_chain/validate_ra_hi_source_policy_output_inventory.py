#!/usr/bin/env python3
"""Validate the RA/HI source-policy output inventory."""

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
        inventory = read_json(PAPER / "RA_HI_SOURCE_POLICY_OUTPUT_INVENTORY.json")
        inventory_md = read_text(PAPER / "RA_HI_SOURCE_POLICY_OUTPUT_INVENTORY.md")
        packet = read_json(PAPER / "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json")
        b4_handoff = read_json(PAPER / "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json")
    except Exception as exc:  # noqa: BLE001
        print(f"RA/HI source-policy output inventory validation: FAIL\n- {exc}")
        return 1

    coverage = inventory.get("coverage", {})
    boundary = inventory.get("guarded_execution_boundary", {})
    commands = inventory.get("commands", [])
    expected_handoff = expected_handoff_summary(b4_handoff)
    actual_handoff = inventory.get("source_policy_execution_handoff", {})
    command_ids = {item.get("command_id") for item in commands if isinstance(item, dict)}
    expected_hi_commands = {
        "hi2022_selected_t8_rA_half_single_pendulum",
        "hi2022_selected_t8_rA_half_double_pendulum",
        "hi2022_selected_t8_rA_half_four_link",
        "hi2022_selected_t8_rA_half_slider_crank",
        "hi2022_selected_t8_rA_single_pendulum",
        "hi2022_selected_t8_rA_double_pendulum",
        "hi2022_selected_t8_rA_four_link",
        "hi2022_selected_t8_rA_slider_crank",
    }
    expected_ra_commands = {
        "ra2021_public_timing_all_forms_models",
        "gauss6_public_single_source_policy_trio",
        "ra2021_double_order_all_forms",
        "gauss6_public_four_link_source_policy_trio",
        "gauss6_public_slider_crank_source_policy_trio",
    }

    checks.check(inventory.get("schema") == "ra-hi-source-policy-output-inventory-v1", "schema changed")
    checks.check(
        inventory.get("status") == "existing_expected_outputs_present_not_promotion_evidence",
        "status changed",
    )
    checks.check(inventory.get("read_only") is True, "inventory must be read-only")
    checks.check(boundary.get("execution_invoked_by_packet") is False, "packet execution unexpectedly invoked")
    checks.check(boundary.get("explicit_user_opt_in_required_before_any_command") is True, "opt-in boundary missing")
    checks.check(boundary.get("heavy_numerical_run_invoked") is False, "heavy run invoked")
    checks.check(boundary.get("run_v047_invoked") is False, "run_v047 invoked")
    checks.check(boundary.get("v048_runner_invoked") is False, "v048 runner invoked by inventory")
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
        inventory.get("source_policy_execution_allowed_now")
        == b4_handoff.get("source_policy_execution_allowed_now")
        is False
        and inventory.get("source_policy_execution_invoked")
        == b4_handoff.get("source_policy_execution_invoked")
        is False
        and inventory.get("exact_b4_opt_in_required_for_execution")
        == b4_handoff.get("exact_b4_opt_in_required_for_execution")
        is True
        and inventory.get("safe_action_ids")
        == b4_handoff.get("safe_action_ids")
        == EXPECTED_SAFE_ACTION_IDS
        and inventory.get("opt_in_action_ids")
        == b4_handoff.get("opt_in_action_ids")
        == EXPECTED_OPT_IN_ACTION_IDS
        and inventory.get("required_user_approval_statement") == EXPECTED_APPROVAL
        and inventory.get("guarded_execution_driver") == "run_b4_source_policy_after_opt_in.sh",
        "top-level source-policy execution aliases stale",
    )
    checks.check(len(commands) == coverage.get("command_count") == packet.get("ready_command_count") == 13, "command count changed")
    checks.check(expected_ra_commands.issubset(command_ids), "RA command set incomplete")
    checks.check(expected_hi_commands.issubset(command_ids), "HI command set incomplete")
    checks.check(coverage.get("suite_command_counts", {}).get("ra2021_absolute_coordinate") == 5, "RA command count changed")
    checks.check(coverage.get("suite_command_counts", {}).get("hi2022_half_implicit") == 8, "HI command count changed")
    checks.check(coverage.get("mapped_external_rows") == packet.get("ready_command_mapped_external_rows") == 20, "mapped rows changed")
    checks.check(coverage.get("expected_output_count") == 13, "expected output count changed")
    checks.check(coverage.get("expected_output_existing_count") == 13, "expected outputs missing")
    checks.check(coverage.get("expected_output_nonempty_count") == 13, "expected outputs empty")
    checks.check(coverage.get("expected_output_csv_data_rows") == 54, "CSV data-row count changed")
    checks.check(coverage.get("expected_summary_count") == 8, "expected summary count changed")
    checks.check(coverage.get("expected_summary_existing_count") == 8, "expected summaries missing")
    checks.check(coverage.get("expected_summary_nonempty_count") == 8, "expected summaries empty")
    checks.check(coverage.get("hi2022_summary_ok_rows") == 22, "HI2022 ok-row summary changed")
    checks.check(coverage.get("hi2022_summary_closed_rows") == 0, "HI2022 summary overcloses rows")
    checks.check(coverage.get("summary_promotion_ready_count") == 0, "summary unexpectedly promotion-ready")
    checks.check(coverage.get("full_public_grid_summary_count") == 0, "full public grid unexpectedly selected")
    checks.check(coverage.get("selected_coarse_trio_summary_count") == 8, "selected coarse-trio count changed")
    checks.check(coverage.get("source_policy_rows_closed_by_inventory") == 0, "inventory closes source-policy rows")
    checks.check(coverage.get("accepted_for_promotion") is False, "inventory accepted for promotion")

    partial = [
        item
        for item in commands
        if isinstance(item, dict)
        and item.get("expected_summary", {}).get("status")
        == "partial_or_failed_full_T8_source_policy_candidate_not_promoted"
    ]
    checks.check(len(partial) == 1, "HI2022 partial/failure summary count changed")
    if partial:
        checks.check(
            partial[0].get("command_id") == "hi2022_selected_t8_rA_half_double_pendulum",
            "HI2022 partial/failure shard changed",
        )
        checks.check(partial[0].get("expected_summary", {}).get("ok_row_count") == 1, "partial shard ok rows changed")

    for token in [
        "Status: `existing_expected_outputs_present_not_promotion_evidence`.",
        "Commands/outputs/summaries: `13`/`13`/`8`.",
        "CSV data rows: `54`.",
        "HI2022 summary ok/closed rows: `22`/`0`.",
        "Promotion-ready/full-grid/coarse-trio summaries: `0`/`0`/`8`.",
        "Source-policy rows closed by inventory: `0`.",
        "Source-policy execution allowed now/invoked/exact opt-in required: `False/False/True`.",
        "Safe action ids: `['rebuild_read_only_audit_chain', 'rerun_read_only_validators', 'keep_narrowed_archive_provenance_only', 'monitor_reopen_conditions']`; opt-in action ids: `['authorized_b4_ra_hi_source_policy_execution']`.",
        f"Source-policy execution handoff exact approval/driver: `{EXPECTED_APPROVAL}/run_b4_source_policy_after_opt_in.sh/True/True/13/20/20`.",
        "Source-policy execution handoff authorized/commands-not-run: `False/True`.",
    ]:
        checks.check(token in inventory_md, f"markdown missing token: {token}")

    if checks.errors:
        print("RA/HI source-policy output inventory validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("RA/HI source-policy output inventory validation: PASS")
    print("commands=13")
    print("outputs=13/13")
    print("summaries=8/8")
    print("csv_data_rows=54")
    print("source_policy_closed=0")
    print(f"source_policy_execution_allowed_now={inventory.get('source_policy_execution_allowed_now')}")
    print(f"source_policy_execution_invoked={inventory.get('source_policy_execution_invoked')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
