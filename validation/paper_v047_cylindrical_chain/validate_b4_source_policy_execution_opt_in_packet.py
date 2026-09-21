#!/usr/bin/env python3
"""Validate the B4 source-policy execution opt-in packet."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent


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
        packet = read_json(PAPER / "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json")
        packet_md = read_text(PAPER / "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.md")
        b4 = read_json(PAPER / "B4_SOURCE_POLICY_WORK_PRECISION_EXECUTION_PLAN.json")
        row_ledger = read_json(PAPER / "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.json")
        vp_audit = read_json(PAPER / "VP2024_CODE_PATH_DISPOSITION_AUDIT.json")
        tfe_demotion_audit = read_json(PAPER / "TFE_B4_B7_SOURCE_POLICY_DEMOTION_AUDIT.json")
    except Exception as exc:  # noqa: BLE001
        print(f"B4 source-policy execution opt-in packet validation: FAIL\n- {exc}")
        return 1

    batches = {item.get("id"): item for item in packet.get("execution_batches", []) if isinstance(item, dict)}
    ra_batch = batches.get("ra2021_ready_after_explicit_1e_4_opt_in", {})
    hi_batch = batches.get("hi2022_ready_no_1e_4_selected_candidate", {})
    ra_commands = ra_batch.get("commands", [])
    hi_commands = hi_batch.get("commands", [])
    all_commands = ra_commands + hi_commands
    unaddressed = packet.get("unaddressed_row_summary", {})
    terminal_attempted = packet.get("terminal_attempted_not_reproducible_row_summary", {})
    guarded = packet.get("guarded_execution_protocol", {})
    gap_program = packet.get("remaining_gap_program", {})
    promotion_contract = packet.get("post_execution_promotion_contract", {})
    vp_disposition = vp_audit.get("source_code_path_disposition", {})
    vp_source_rows = vp_audit.get("source_policy_rows", {})
    vp_coverage = vp_audit.get("coverage", {})

    checks.check(packet.get("schema") == "b4-source-policy-execution-opt-in-packet-v1", "schema changed")
    checks.check(
        packet.get("status") == "ready_for_user_opt_in_packet_not_authorized_not_run",
        "status changed",
    )
    checks.check(packet.get("read_only") is True, "packet must be read-only")
    checks.check(packet.get("packet_does_not_authorize_execution") is True, "packet authorizes execution")
    checks.check(
        packet.get("explicit_user_opt_in_required_before_any_command") is True,
        "explicit opt-in guard missing",
    )
    checks.check(packet.get("source_policy_execution_allowed_now") is False, "packet allows execution now")
    checks.check(packet.get("source_policy_execution_invoked") is False, "packet overclaims source-policy execution")
    checks.check(
        packet.get("exact_b4_opt_in_required_for_execution") is True,
        "packet lost exact B4 opt-in execution boundary",
    )
    checks.check(
        packet.get("safe_action_ids")
        == [
            "rebuild_read_only_audit_chain",
            "rerun_read_only_validators",
            "keep_narrowed_archive_provenance_only",
            "monitor_reopen_conditions",
        ],
        "packet safe action ids changed",
    )
    checks.check(
        packet.get("opt_in_action_ids") == ["authorized_b4_ra_hi_source_policy_execution"],
        "packet opt-in action ids changed",
    )
    checks.check("B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json" in packet.get("required_user_approval_statement", ""), "approval statement missing packet name")
    checks.check(
        packet.get("opt_in_required_phrase") == packet.get("required_user_approval_statement"),
        "top-level opt-in phrase alias missing or stale",
    )
    checks.check(
        packet.get("exact_approval_statement") == packet.get("required_user_approval_statement"),
        "top-level exact approval statement alias missing or stale",
    )
    checks.check(
        packet.get("exact_required_user_approval_statement") == packet.get("required_user_approval_statement"),
        "top-level exact required approval statement alias missing or stale",
    )
    checks.check(packet.get("commands_not_run_by_packet") is True, "packet command-run boundary missing")
    checks.check(
        packet.get("guarded_execution_driver_path") == "run_b4_source_policy_after_opt_in.sh",
        "top-level guarded driver path alias missing or stale",
    )
    checks.check(packet.get("driver_requires_exact_approval") is True, "top-level driver approval guard missing")
    checks.check(
        packet.get("driver_does_not_authorize_execution") is True,
        "top-level driver authorization boundary missing",
    )
    checks.check(packet.get("execution_invoked_by_packet") is False, "packet invoked execution")
    checks.check(packet.get("heavy_numerical_run_invoked") is False, "packet invoked heavy run")
    checks.check(packet.get("run_v047_invoked") is False, "packet invoked run_v047")
    checks.check(packet.get("v048_runner_invoked") is False, "packet invoked v048")
    checks.check(packet.get("source_policy_closed") is False, "top-level source-policy closure overclaimed")
    checks.check(packet.get("source_policy_closed_ratio") == "0/40", "top-level source-policy ratio changed")
    checks.check(
        packet.get("source_policy_rows_closed_now") == row_ledger.get("source_policy_rows_closed") == 0,
        "packet overcloses source-policy rows",
    )
    checks.check(packet.get("source_policy_rows_total") == row_ledger.get("row_count") == 40, "row total changed")
    checks.check(packet.get("ready_command_batch_count") == 2, "ready command batch count changed")
    checks.check(packet.get("ready_command_count") == 13, "ready command count changed")
    checks.check(packet.get("ready_command_mapped_external_rows") == 20, "mapped external row count changed")
    checks.check(packet.get("unaddressed_external_rows_after_ready_commands") == 0, "unaddressed row count changed")
    checks.check(
        packet.get("source_policy_rows_attempted_not_reproducible")
        == row_ledger.get("source_policy_rows_attempted_not_reproducible")
        == 20,
        "attempted-not-reproducible row count changed",
    )
    checks.check(
        packet.get("attempted_not_reproducible_rows")
        == packet.get("source_policy_rows_attempted_not_reproducible")
        == 20,
        "attempted-not-reproducible top-level alias changed",
    )
    checks.check(
        packet.get("source_policy_rows_still_requiring_execution_or_promotion")
        == row_ledger.get("source_policy_rows_still_requiring_execution_or_promotion")
        == 20,
        "still-requiring-execution row count changed",
    )
    checks.check(packet.get("b4_can_close_now") is False, "packet overcloses B4")
    checks.check(packet.get("b7_can_close_now") is False, "packet overcloses B7")
    checks.check(packet.get("b4_can_close_after_ready_commands_only") is False, "packet overclaims B4 after commands")
    checks.check(packet.get("b7_can_close_after_ready_commands_only") is False, "packet overclaims B7 after commands")
    checks.check(packet.get("existing_artifact_promotion_ready_count") == 0, "existing artifacts became promotable")
    checks.check(packet.get("post_execution_promotion_required") is True, "promotion guard missing")
    checks.check(
        promotion_contract.get("schema") == "b4-source-policy-post-execution-promotion-contract-v1",
        "post-execution promotion contract schema missing",
    )
    checks.check(
        promotion_contract.get("status") == "promotion_contract_defined_no_rows_promoted",
        "post-execution promotion contract status changed",
    )
    checks.check(
        promotion_contract.get("source_publication_contract_id")
        == b4.get("publication_grade_acceptance_contract", {}).get("contract_id")
        == "b4-source-policy-work-precision-publication-contract-v1",
        "promotion contract no longer points to B4 publication contract",
    )
    checks.check(promotion_contract.get("read_only") is True, "promotion contract should be read-only")
    checks.check(
        promotion_contract.get("post_execution_promotion_required") is True,
        "promotion contract lost required marker",
    )
    checks.check(
        promotion_contract.get("source_policy_rows_closed_now")
        == packet.get("source_policy_rows_closed_now")
        == 0,
        "promotion contract overcloses source-policy rows",
    )
    checks.check(
        promotion_contract.get("source_policy_rows_total")
        == packet.get("source_policy_rows_total")
        == 40,
        "promotion contract source-policy row total changed",
    )
    checks.check(
        promotion_contract.get("ready_command_mapped_external_rows")
        == packet.get("ready_command_mapped_external_rows")
        == 20,
        "promotion contract ready-mapped row count changed",
    )
    checks.check(
        promotion_contract.get("unaddressed_external_rows_after_ready_commands")
        == packet.get("unaddressed_external_rows_after_ready_commands")
        == 0,
        "promotion contract unaddressed row count changed",
    )
    checks.check(
        promotion_contract.get("source_policy_rows_attempted_not_reproducible")
        == packet.get("source_policy_rows_attempted_not_reproducible")
        == 20,
        "promotion contract attempted-not-reproducible row count changed",
    )
    checks.check(
        promotion_contract.get("source_policy_rows_still_requiring_execution_or_promotion")
        == packet.get("source_policy_rows_still_requiring_execution_or_promotion")
        == 20,
        "promotion contract still-requiring-execution row count changed",
    )
    checks.check(
        promotion_contract.get("existing_artifact_promotion_ready_count") == 0,
        "promotion contract unexpectedly marks existing artifacts promotable",
    )
    checks.check(
        promotion_contract.get("ready_lanes_after_explicit_opt_in")
        == ["ra2021_source_policy_work_precision", "hi2022_full_T8_work_precision"],
        "promotion contract ready lane set changed",
    )
    checks.check(
        promotion_contract.get("not_ready_lanes")
        == ["tfe_source_policy_work_precision", "vp2024_source_code_path_work_precision"],
        "promotion contract not-ready lane set changed",
    )
    checks.check(
        promotion_contract.get("lane_summary", {}).get("ready_to_launch_after_explicit_opt_in_count") == 2
        and promotion_contract.get("lane_summary", {}).get("not_ready_lane_count") == 2
        and promotion_contract.get("lane_summary", {}).get("source_policy_rows_closed_after_plan") == 0
        and promotion_contract.get("lane_summary", {}).get("source_policy_rows_total") == 40,
        "promotion contract lane summary changed",
    )
    checks.check(
        promotion_contract.get("remaining_gap_program_status") == gap_program.get("status"),
        "promotion contract gap-program status diverged",
    )
    checks.check(
        promotion_contract.get("remaining_gap_rows_requiring_new_runner_or_code_path") == 0,
        "promotion contract runner/code-path gap count changed",
    )
    checks.check(
        promotion_contract.get("remaining_gap_rows_demoted_related_work_proxy_for_current_claim") == 0,
        "promotion contract demotion count changed",
    )
    after_ready = promotion_contract.get("after_ready_commands_only", {})
    checks.check(
        after_ready.get("mapped_external_rows") == 20
        and after_ready.get("unaddressed_external_rows") == 0
        and after_ready.get("b4_can_close") is False
        and after_ready.get("b7_can_close") is False,
        "promotion contract overclaims ready-command closure",
    )
    checklist = promotion_contract.get("promotion_checklist", [])
    checklist_by_id = {item.get("id"): item for item in checklist if isinstance(item, dict)}
    checks.check(len(checklist) == 8, "promotion checklist length changed")
    checks.check(
        set(checklist_by_id)
        == {
            "source_policy_row_provenance",
            "same_run_error_and_work_metrics",
            "diagnostic_rows_not_promoted",
            "ready_command_rows_are_insufficient_by_themselves",
            "remaining_gap_rows_stay_open_or_demoted",
            "nonpublic_code_self_reproduction_disposition_recorded",
            "publication_figures_rebuilt_from_promoted_rows",
            "closure_validators_rerun_after_promotion",
        },
        "promotion checklist IDs changed",
    )
    checks.check(
        checklist_by_id.get("diagnostic_rows_not_promoted", {}).get("currently_satisfied") is True
        and checklist_by_id.get("ready_command_rows_are_insufficient_by_themselves", {}).get(
            "currently_satisfied"
        )
        is True,
        "promotion checklist lost current non-promotion safeguards",
    )
    for item_id in [
        "source_policy_row_provenance",
        "same_run_error_and_work_metrics",
        "publication_figures_rebuilt_from_promoted_rows",
        "closure_validators_rerun_after_promotion",
    ]:
        checks.check(
            checklist_by_id.get(item_id, {}).get("currently_satisfied") is False,
            f"promotion checklist overcloses {item_id}",
        )
    checks.check(
        checklist_by_id.get("remaining_gap_rows_stay_open_or_demoted", {}).get("currently_satisfied") is True,
        "promotion checklist should record current demotion boundary for remaining rows",
    )
    checks.check(
        checklist_by_id.get("nonpublic_code_self_reproduction_disposition_recorded", {}).get("currently_satisfied")
        is True,
        "promotion checklist should record nonpublic-code self reproduction disposition",
    )
    checks.check(
        promotion_contract.get("all_required_checks_satisfied_now") is False,
        "promotion contract overclaims current checklist satisfaction",
    )
    checks.check(
        promotion_contract.get("b4_can_close_after_promotion_contract_now") is False
        and promotion_contract.get("b7_can_close_after_promotion_contract_now") is False,
        "promotion contract overcloses B4/B7",
    )
    checks.check(
        promotion_contract.get("closure_validator_sequence", [])[-1] == "validate_paper_package.py",
        "promotion contract closure validator sequence should end with full paper package validation",
    )
    checks.check(
        "validate_ra2021_double_source_policy_low_order_diagnosis.py"
        in promotion_contract.get("closure_validator_sequence", []),
        "RA2021 double low-order diagnosis validator missing from closure sequence",
    )
    checks.check(
        "validate_hi2022_ra_half_double_source_policy_failure_diagnosis.py"
        in promotion_contract.get("closure_validator_sequence", []),
        "HI2022 rA_half double failure diagnosis validator missing from closure sequence",
    )
    checks.check(
        "RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.json" in packet.get("source_files", []),
        "RA2021 double low-order diagnosis not listed as source file",
    )
    checks.check(
        "HI2022_RA_HALF_DOUBLE_SOURCE_POLICY_FAILURE_DIAGNOSIS.json" in packet.get("source_files", []),
        "HI2022 rA_half double failure diagnosis not listed as source file",
    )
    checks.check(
        "VP2024_CODE_PATH_DISPOSITION_AUDIT.json" in packet.get("source_files", []),
        "VP2024 disposition audit not listed as source file",
    )
    checks.check(
        "VP2024_PUBLIC_CODE_RECHECK_20260613.json" in packet.get("source_files", []),
        "VP2024 public-code recheck certificate not listed as source file",
    )
    checks.check(
        "TFE_B4_B7_SOURCE_POLICY_DEMOTION_AUDIT.json" in packet.get("source_files", []),
        "TFE demotion audit not listed as source file",
    )
    checks.check(
        "TFE_PUBLIC_CODE_RECHECK_20260613.json" in packet.get("source_files", []),
        "TFE public-code recheck certificate not listed as source file",
    )
    checks.check(
        "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.json" in packet.get("source_files", []),
        "2026-06-14 public-code refresh not listed as source file",
    )

    checks.check(
        guarded.get("schema") == "b4-source-policy-guarded-execution-protocol-v1",
        "guarded execution protocol schema changed",
    )
    checks.check(
        guarded.get("status") == "dry_run_preflight_complete_execution_requires_exact_user_approval",
        "guarded execution protocol status changed",
    )
    checks.check(
        guarded.get("execution_working_directory") == "../../numerics/v048_cross_paper_same_test_benchmarks",
        "guarded execution working directory changed",
    )
    checks.check(guarded.get("execution_working_directory_exists") is True, "guarded execution cwd missing")
    checks.check(
        guarded.get("explicit_user_opt_in_required_before_any_command") is True,
        "guarded protocol lost explicit opt-in",
    )
    checks.check(
        guarded.get("exact_approval_statement_required") == packet.get("required_user_approval_statement"),
        "guarded protocol approval statement diverged",
    )
    checks.check(guarded.get("packet_does_not_authorize_execution") is True, "guarded protocol authorizes execution")
    checks.check(guarded.get("dry_run_only_until_approved") is True, "guarded protocol is not dry-run guarded")
    checks.check(guarded.get("execute_commands_now") is False, "guarded protocol executes commands")
    checks.check(guarded.get("command_preflight_count") == 13, "guarded preflight count changed")
    checks.check(guarded.get("all_commands_parse_ok") is True, "guarded protocol command parsing failed")
    checks.check(guarded.get("all_runner_scripts_exist") is True, "guarded protocol runner script missing")
    checks.check(guarded.get("all_python_executables_exist") is True, "guarded protocol Python executable missing")
    checks.check(
        guarded.get("all_commands_shell_safe_single_command") is True,
        "guarded protocol found shell-unsafe command",
    )
    checks.check(guarded.get("heavy_numerical_run_invoked") is False, "guarded protocol invoked heavy run")
    checks.check(guarded.get("run_v047_invoked") is False, "guarded protocol invoked run_v047")
    checks.check(guarded.get("v048_runner_invoked") is False, "guarded protocol invoked v048")

    checks.check(
        gap_program.get("schema") == "b4-source-policy-remaining-gap-program-v1",
        "remaining gap program schema changed",
    )
    checks.check(
        gap_program.get("status") == "remaining_0_rows_programmed_no_execution_invoked",
        "remaining gap program status changed",
    )
    checks.check(gap_program.get("row_count") == 0, "remaining gap row count changed")
    checks.check(gap_program.get("program_entry_count") == 0, "remaining gap entry count changed")
    checks.check(
        gap_program.get("all_entries_not_ready_to_execute_now") is True,
        "remaining gap program overclaims launch readiness",
    )
    checks.check(
        gap_program.get("rows_requiring_new_runner_or_code_path") == 0,
        "remaining gap runner/code-path row count changed",
    )
    checks.check(
        gap_program.get("rows_requiring_policy_definition") == 0,
        "remaining gap policy-definition row count changed",
    )
    checks.check(
        gap_program.get("rows_demoted_related_work_proxy_for_current_claim") == 0,
        "related-work/proxy demotion row count changed",
    )
    checks.check(gap_program.get("heavy_numerical_run_invoked") is False, "gap program invoked heavy run")
    checks.check(gap_program.get("run_v047_invoked") is False, "gap program invoked run_v047")
    checks.check(gap_program.get("v048_runner_invoked") is False, "gap program invoked v048")
    entries = {item.get("id"): item for item in gap_program.get("entries", []) if isinstance(item, dict)}
    checks.check(entries == {}, "remaining gap entries should be empty after terminal self-reproduction disposition")
    checks.check(
        terminal_attempted.get("tfe2026_original_pendulum")
        == tfe_demotion_audit.get("demoted_related_work_proxy_rows_for_current_claim")
        == 16,
        "TFE terminal attempted row count changed",
    )
    checks.check(
        terminal_attempted.get("vp2024_velocity_partitioning")
        == vp_coverage.get("source_policy_code_path_unresolved_rows")
        == 4,
        "VP2024 terminal attempted row count changed",
    )
    checks.check(terminal_attempted.get("total") == 20, "terminal attempted total changed")
    terminal_rows = packet.get("terminal_attempted_not_reproducible_rows", [])
    checks.check(len(terminal_rows) == 20, "terminal attempted row list count changed")
    checks.check(
        all(row.get("evidence") == "SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json" for row in terminal_rows),
        "terminal attempted rows missing self-reproduction evidence",
    )
    checks.check(vp_disposition.get("coordinate_partitioning_proxy_is_source_policy_reproduction") is False, "VP proxy promoted")
    checks.check(vp_source_rows.get("source_policy_rows_closed") == 0, "VP source-policy rows unexpectedly closed")

    checks.check(len(all_commands) == 13, "total command count changed")
    for item in all_commands:
        preflight = item.get("execution_preflight", {})
        checks.check(
            preflight.get("schema") == "b4-source-policy-command-preflight-v1",
            f"{item.get('id')} command preflight schema changed",
        )
        checks.check(
            preflight.get("execution_working_directory") == "../../numerics/v048_cross_paper_same_test_benchmarks",
            f"{item.get('id')} command cwd changed",
        )
        checks.check(preflight.get("execution_working_directory_exists") is True, f"{item.get('id')} cwd missing")
        checks.check(preflight.get("parse_ok") is True, f"{item.get('id')} command does not parse")
        checks.check(preflight.get("parse_error") is None, f"{item.get('id')} parse error recorded")
        checks.check(preflight.get("python_executable") == "../../.venv_sbel/bin/python", f"{item.get('id')} Python executable changed")
        checks.check(preflight.get("python_executable_exists") is True, f"{item.get('id')} Python executable missing")
        checks.check(str(preflight.get("runner_script", "")).endswith(".py"), f"{item.get('id')} runner script missing")
        checks.check(preflight.get("runner_script_exists") is True, f"{item.get('id')} runner script file missing")
        checks.check(preflight.get("shell_control_tokens_present") == [], f"{item.get('id')} shell control tokens present")
        checks.check(preflight.get("shell_safe_single_command") is True, f"{item.get('id')} shell safety failed")
        checks.check(preflight.get("dry_run_only") is True, f"{item.get('id')} preflight is not dry-run")
        checks.check(preflight.get("executed_by_packet") is False, f"{item.get('id')} executed by packet")

    checks.check(set(batches) == {"ra2021_ready_after_explicit_1e_4_opt_in", "hi2022_ready_no_1e_4_selected_candidate"}, "batch set changed")
    checks.check(ra_batch.get("command_count") == len(ra_commands) == 5, "RA2021 command count changed")
    checks.check(ra_batch.get("mapped_external_rows") == 12, "RA2021 mapped row count changed")
    checks.check(ra_batch.get("source_policy_1e_4_opt_in_required") is True, "RA2021 1e-4 opt-in guard missing")
    checks.check(
        ra_batch.get("all_commands_require_allow_source_policy_1e_4") is True,
        "RA2021 commands lost --allow-source-policy-1e-4",
    )
    checks.check(
        all("--allow-source-policy-1e-4" in str(item.get("command")) for item in ra_commands),
        "RA2021 command missing --allow-source-policy-1e-4",
    )
    checks.check(
        {item.get("id") for item in ra_commands}
        == {item.get("id") for item in b4.get("ra2021_launch_preflight", {}).get("launch_commands", [])},
        "RA2021 command IDs diverged from B4 preflight",
    )
    checks.check(
        sum(int(item.get("mapped_row_count", 0)) for item in ra_commands) == 24,
        "RA2021 command-to-row references changed",
    )

    checks.check(hi_batch.get("command_count") == len(hi_commands) == 8, "HI2022 command count changed")
    checks.check(hi_batch.get("mapped_external_rows") == 8, "HI2022 mapped row count changed")
    checks.check(hi_batch.get("source_policy_1e_4_opt_in_required") is False, "HI2022 should not require 1e-4")
    checks.check(
        hi_batch.get("all_commands_avoid_allow_source_policy_1e_4") is True,
        "HI2022 command has forbidden 1e-4 flag",
    )
    checks.check(
        all("--allow-source-policy-1e-4" not in str(item.get("command")) for item in hi_commands),
        "HI2022 command includes forbidden 1e-4 flag",
    )
    checks.check(
        {item.get("id") for item in hi_commands}
        == {item.get("id") for item in b4.get("hi2022_launch_preflight", {}).get("launch_commands", [])},
        "HI2022 command IDs diverged from B4 preflight",
    )
    checks.check(
        sum(int(item.get("mapped_row_count", 0)) for item in hi_commands) == 8,
        "HI2022 command-to-row references changed",
    )
    checks.check(
        sum(1 for item in hi_commands if item.get("artifact_status") == "executed_full_T8_selected_coarse_trio_not_promoted") == 7,
        "HI2022 existing executed candidate count changed",
    )

    checks.check(unaddressed.get("tfe2026_original_pendulum") == 0, "TFE unaddressed count changed")
    checks.check(unaddressed.get("vp2024_velocity_partitioning") == 0, "VP2024 unaddressed count changed")
    checks.check(
        unaddressed.get("hi2022_half_implicit_single_pendulum") == 0,
        "HI2022 single-pendulum unaddressed count changed",
    )
    checks.check(len(packet.get("unaddressed_rows", [])) == 0, "unaddressed row list count changed")
    driver = packet.get("guarded_execution_driver", {})
    checks.check(
        packet.get("guarded_execution_driver_path") == driver.get("path"),
        "top-level guarded driver path diverged from driver object",
    )
    checks.check(
        packet.get("driver_requires_exact_approval") == driver.get("requires_exact_approval_argument"),
        "top-level driver exact-approval alias diverged from driver object",
    )
    checks.check(
        packet.get("driver_does_not_authorize_execution") == driver.get("driver_does_not_authorize_execution"),
        "top-level driver authorization alias diverged from driver object",
    )
    checks.check(driver.get("path") == "run_b4_source_policy_after_opt_in.sh", "guarded driver path changed")
    checks.check(driver.get("exists") is True, "guarded driver missing")
    checks.check(driver.get("requires_exact_approval_argument") is True, "guarded driver lost approval argument guard")
    checks.check(
        driver.get("approval_argument") == guarded.get("exact_approval_statement_required"),
        "guarded driver approval argument not synchronized with protocol",
    )
    checks.check(driver.get("executes_packet_command_count") == 13, "guarded driver command count changed")
    checks.check(
        driver.get("post_execution_validator_sequence_included") is True,
        "guarded driver lost post-execution validator sequence marker",
    )
    checks.check(
        driver.get("driver_does_not_authorize_execution") is True,
        "guarded driver incorrectly authorizes execution",
    )

    for token in [
        "Status: `ready_for_user_opt_in_packet_not_authorized_not_run`.",
        "Explicit user opt-in required: `True`.",
        "Ready command batches/count: `2/13`.",
        "Ready command mapped external rows: `20/40`.",
        "Unaddressed external rows after ready commands: `0`.",
        "Attempted-not-reproducible external rows: `20`.",
        "External rows still requiring execution/promotion: `20`.",
        "Source-policy rows closed now: `0/40`.",
        "Source-policy execution allowed now/invoked/exact opt-in required: `False/False/True`.",
        "Safe action ids: `rebuild_read_only_audit_chain,rerun_read_only_validators,keep_narrowed_archive_provenance_only,monitor_reopen_conditions`.",
        "Opt-in action ids: `authorized_b4_ra_hi_source_policy_execution`.",
        "B4/B7 can close now: `False/False`.",
        "B4/B7 can close after ready commands only: `False/False`.",
        "Heavy/run_v047/v048 invoked: `False/False/False`.",
        "Command preflight parse/runner/python/shell-safe: `True/True/True/True`.",
        "Remaining gap program rows/entries: `0/0`.",
        "TFE rows attempted-not-reproducible: `16`.",
        "VP2024 rows attempted-not-reproducible: `4`.",
        "Rows demoted related-work/proxy for current claim: `0`.",
        "Post-execution promotion contract: `b4-source-policy-post-execution-promotion-contract-v1` / `promotion_contract_defined_no_rows_promoted`.",
        "Promotion checklist satisfied now: `False`.",
        "This packet is an OC4 execution handoff artifact. It does not close the global objective blockers.",
        "blocker_open_by_id=OC4:True,OC6:True,OC12:True",
        "blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready",
        "blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False",
        "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json",
        "Guarded execution driver:",
        "`run_b4_source_policy_after_opt_in.sh`",
        "It refuses to execute unless the exact approval statement above is passed as its first argument.",
        "`ra2021_ready_after_explicit_1e_4_opt_in`",
        "`hi2022_ready_no_1e_4_selected_candidate`",
        "## Guarded Execution Protocol",
        "Status: `dry_run_preflight_complete_execution_requires_exact_user_approval`.",
        "Execution working directory: `../../numerics/v048_cross_paper_same_test_benchmarks`.",
        "Command preflights: `13`.",
        "All commands parse: `True`.",
        "All runner scripts exist: `True`.",
        "All Python executables exist: `True`.",
        "All commands shell-safe single command: `True`.",
        "Execute commands now: `False`.",
        "Dry-run only until approved: `True`.",
        "TFE rows without launch commands: `0`.",
        "VP2024 rows without launch commands: `0`.",
        "TFE current-claim disposition: `attempted_not_reproducible; related-work/formal-order comparator only; source-policy rows remain 0/16`.",
        "VP2024 current-claim disposition: `attempted_not_reproducible; related-work/proxy only; source-policy rows remain 0/4`.",
        "Terminal attempted-not-reproducible rows: `20`.",
        "Terminal attempted-not-reproducible evidence: `SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json`.",
        "HI2022 single-pendulum rows outside selected-candidate preflight: `0`.",
        "## Remaining Gap Program",
        "Status: `remaining_0_rows_programmed_no_execution_invoked`.",
        "Post-execution promotion is still required",
        "## Post-Execution Promotion Contract",
        "Contract: `b4-source-policy-post-execution-promotion-contract-v1`.",
        "Source publication contract: `b4-source-policy-work-precision-publication-contract-v1`.",
        "Rows closed now: `0/40`.",
        "Ready mapped/unaddressed rows: `20/0`.",
        "Attempted-not-reproducible rows: `20`.",
        "Rows still requiring execution/promotion: `20`.",
        "Ready/not-ready lanes: `2/2`.",
        "Remaining gap rows requiring runner/code path: `0`.",
        "Remaining gap rows demoted related-work/proxy for current claim: `0`.",
        "After ready commands only can close B4/B7: `False/False`.",
        "`source_policy_row_provenance`",
        "`same_run_error_and_work_metrics`",
        "`nonpublic_code_self_reproduction_disposition_recorded`",
        "`publication_figures_rebuilt_from_promoted_rows`",
    ]:
        checks.check(token in packet_md, f"markdown missing token: {token}")

    if checks.errors:
        print("B4 source-policy execution opt-in packet validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("B4 source-policy execution opt-in packet validation: PASS")
    print("ready_command_count=13")
    print("ready_command_mapped_external_rows=20/40")
    print("unaddressed_external_rows=0")
    print("attempted_not_reproducible_rows=20")
    print("source_policy_closed_now=0/40")
    print("commands_not_run_by_packet=True")
    print("exact_approval_statement=present")
    print("guarded_execution_driver_path=run_b4_source_policy_after_opt_in.sh")
    print("driver_requires_exact_approval=True")
    print("driver_does_not_authorize_execution=True")
    print("execution_invoked_by_packet=False")
    print("blocker_open_by_id=OC4:True,OC6:True,OC12:True")
    print("blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
