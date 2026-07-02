#!/usr/bin/env python3
"""Validate the B4 expected-output promotion-readiness blocker audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import build_b4_expected_output_promotion_readiness_blocker_audit_20260620 as builder


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "B4_EXPECTED_OUTPUT_PROMOTION_READINESS_BLOCKER_AUDIT_20260620.json"
AUDIT_MD = PAPER / "B4_EXPECTED_OUTPUT_PROMOTION_READINESS_BLOCKER_AUDIT_20260620.md"
EXPECTED_SAFE_ACTION_IDS = [
    "rebuild_read_only_audit_chain",
    "rerun_read_only_validators",
    "keep_narrowed_archive_provenance_only",
    "monitor_reopen_conditions",
]
EXPECTED_OPT_IN_ACTION_IDS = ["authorized_b4_ra_hi_source_policy_execution"]
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
        audit = read_json(AUDIT_JSON)
        text = AUDIT_MD.read_text(encoding="utf-8", errors="replace")
        expected = builder.build_payload()
    except Exception as exc:  # noqa: BLE001
        print(f"b4 expected-output promotion-readiness blocker audit validation: FAIL\n- {exc}")
        return 1

    checks.check(audit == expected, "audit JSON is stale relative to source artifacts")
    checks.check(audit.get("schema") == builder.SCHEMA, "schema changed")
    checks.check(audit.get("status") == builder.STATUS, "status changed")
    checks.check(audit.get("date_checked") == "2026-06-20", "date changed")
    checks.check(audit.get("read_only") is True, "audit must remain read-only")
    checks.check(audit.get("execution_authorized") is False, "audit authorized execution")
    checks.check(audit.get("commands_executed_by_audit") is False, "audit executed commands")
    checks.check(audit.get("source_policy_execution_invoked") is False, "audit invoked source-policy execution")
    checks.check(
        audit.get("source_policy_execution_allowed_now") is False,
        "audit allows source-policy execution without opt-in",
    )
    checks.check(
        audit.get("exact_b4_opt_in_required_for_execution") is True,
        "audit lost exact B4 opt-in requirement",
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
        audit.get("builder_invoked_heavy_numerical_run") is False,
        "builder invoked heavy numerical run",
    )
    checks.check(audit.get("run_v047_invoked") is False, "audit invoked run_v047")
    checks.check(audit.get("v048_runner_invoked") is False, "audit invoked v048")
    checks.check(
        audit.get("required_user_approval_statement") == builder.APPROVAL,
        "approval statement changed",
    )
    checks.check(
        audit.get("guarded_execution_driver") == EXPECTED_DRIVER,
        "guarded driver alias missing or stale",
    )
    checks.check(
        audit.get("source_policy_rows_total") == 40,
        "source-policy total changed",
    )
    checks.check(audit.get("source_policy_rows_closed") == 0, "source-policy rows overclosed")
    checks.check(audit.get("source_policy_rows_promoted") == 0, "source-policy rows overpromoted")
    checks.check(audit.get("promotion_ready_rows") == 0, "promotion-ready rows overclaimed")
    checks.check(audit.get("submission_ready") is False, "submission unexpectedly ready")
    checks.check(audit.get("b4_can_close_now") is False, "B4 overclosed")
    checks.check(audit.get("b7_can_close_now") is False, "B7 overclosed")
    checks.check(set(audit.get("source_files", [])) == set(builder.SOURCE_FILES), "source files changed")

    schema_summary = audit.get("schema_audit_summary", {})
    checks.check(schema_summary.get("status") == "expected_outputs_schema_ready_not_authorized_not_run_not_promoted", "schema audit status changed")
    checks.check(schema_summary.get("command_count") == 13, "schema audit command count changed")
    checks.check(schema_summary.get("schema_ready_commands") == 13, "schema-ready command count changed")
    checks.check(schema_summary.get("expected_artifact_count") == 21, "expected artifact count changed")
    checks.check(schema_summary.get("artifacts_sha256_match_freeze") == 21, "artifact hash count changed")
    checks.check(schema_summary.get("csv_parseable_artifacts") == 13, "CSV parseable count changed")
    checks.check(schema_summary.get("json_summary_parseable_artifacts") == 8, "JSON parseable count changed")
    checks.check(schema_summary.get("total_csv_data_rows") == 54, "CSV data row count changed")
    checks.check(schema_summary.get("source_policy_rows_closed") == 0, "schema audit overclosed rows")
    checks.check(schema_summary.get("promotion_ready_rows") == 0, "schema audit overpromoted rows")
    checks.check(schema_summary.get("commands_executed_by_audit") is False, "schema audit executed commands")
    checks.check(
        schema_summary.get("source_policy_execution_invoked") is False
        and schema_summary.get("source_policy_execution_allowed_now") is False
        and schema_summary.get("exact_b4_opt_in_required_for_execution") is True,
        "schema audit execution boundary changed",
    )
    checks.check(
        schema_summary.get("safe_action_ids") == EXPECTED_SAFE_ACTION_IDS
        and schema_summary.get("opt_in_action_ids") == EXPECTED_OPT_IN_ACTION_IDS,
        "schema audit action ids changed",
    )

    checks.check(audit.get("command_count") == 13, "command count changed")
    checks.check(audit.get("schema_ready_command_count") == 13, "schema-ready command count changed")
    checks.check(audit.get("promotion_ready_command_count") == 0, "promotion-ready command count changed")
    checks.check(audit.get("command_row_reference_total") == 32, "command row-reference count changed")
    checks.check(audit.get("unique_mapped_ra_hi_row_count") == 20, "unique RA/HI row count changed")
    checks.check(audit.get("unique_mapped_ra_hi_rows_not_promoted") == 20, "not-promoted row count changed")
    checks.check(audit.get("summary_source_policy_rows_closed_total") == 0, "summary overclosed rows")
    checks.check(audit.get("summary_source_policy_rows_promoted_total") == 0, "summary overpromoted rows")
    checks.check(
        audit.get("commands_with_schema_ready_but_promotion_blocked") == 13,
        "schema-ready blocked command count changed",
    )
    checks.check(len(audit.get("unique_mapped_ra_hi_rows", [])) == 20, "unique mapped row list changed")

    post = audit.get("post_execution_summary", {})
    checks.check(post.get("verified_authorized_execution_recorded") is False, "post execution unexpectedly authorized")
    checks.check(post.get("approved_driver_execution_recorded") is False, "approved driver unexpectedly recorded")
    checks.check(post.get("source_policy_rows_closed") == 0, "post execution overclosed rows")
    checks.check(post.get("source_policy_rows_open") == 20, "post execution open rows changed")
    checks.check(post.get("source_policy_rows_still_requiring_execution_or_promotion") == 20, "post execution required rows changed")
    checks.check(post.get("b4_can_close_now") is False and post.get("b7_can_close_now") is False, "post execution overclosed B4/B7")

    existing = audit.get("existing_artifact_promotion_summary", {})
    checks.check(existing.get("candidate_item_count") == 8, "existing artifact candidate count changed")
    checks.check(existing.get("promotion_ready_without_new_execution_count") == 0, "existing artifacts overpromoted")
    checks.check(existing.get("source_policy_rows_closed_by_existing_artifacts") == 0, "existing artifacts overclosed rows")

    ra_hi = audit.get("ra_hi_promotion_matrix_summary", {})
    checks.check(ra_hi.get("row_count") == 20, "RA/HI row count changed")
    checks.check(ra_hi.get("ra2021_row_count") == 12, "RA row count changed")
    checks.check(ra_hi.get("hi2022_row_count") == 8, "HI row count changed")
    checks.check(ra_hi.get("rows_with_all_command_outputs_present") == 20, "RA/HI output-present rows changed")
    checks.check(ra_hi.get("source_policy_rows_closed") == 0, "RA/HI overclosed rows")
    checks.check(ra_hi.get("source_policy_rows_not_promoted") == 20, "RA/HI not-promoted rows changed")
    checks.check(
        ra_hi.get("future_promotion_requires_authorized_execution_or_new_artifact_rows") == 20,
        "RA/HI future-promotion boundary changed",
    )

    matrix = audit.get("promotion_blocker_matrix", {})
    checks.check(matrix.get("schema_ready_commands") == 13, "matrix schema-ready commands changed")
    checks.check(matrix.get("schema_ready_expected_artifacts") == 21, "matrix expected artifacts changed")
    checks.check(matrix.get("schema_ready_csv_rows") == 54, "matrix CSV row count changed")
    checks.check(matrix.get("verified_authorized_execution_recorded") is False, "matrix unexpectedly authorized")
    checks.check(matrix.get("post_execution_promoted_rows") == 0, "matrix promoted rows changed")
    checks.check(matrix.get("post_execution_rows_still_requiring_execution_or_promotion") == 20, "matrix open rows changed")
    checks.check(matrix.get("existing_artifacts_promotion_ready_without_new_execution") == 0, "matrix existing artifacts overpromoted")
    checks.check(matrix.get("ra_hi_rows_not_promoted") == 20, "matrix RA/HI not-promoted rows changed")
    checks.check(matrix.get("ra_hi_rows_with_all_command_outputs_present") == 20, "matrix output-present rows changed")
    checks.check(matrix.get("full_archive_ready_now") is False, "matrix archive readiness overclaimed")
    checks.check(matrix.get("source_policy_closed_ratio") == "0/40", "matrix source-policy ratio changed")
    checks.check(matrix.get("blocking_ids") == ["OC4", "OC12"], "matrix blocker ids changed")

    for command in audit.get("commands", []):
        label = str(command.get("id"))
        checks.check(command.get("schema_ready") is True, f"{label} lost schema-ready marker")
        checks.check(command.get("promotion_ready") is False, f"{label} unexpectedly promotion-ready")
        checks.check(
            command.get("promotion_status") == "schema_ready_promotion_blocked",
            f"{label} promotion status changed",
        )
        checks.check(command.get("matched_ra_hi_matrix_rows") == command.get("mapped_row_key_count"), f"{label} row mapping mismatch")
        checks.check(command.get("matched_rows_not_promoted") == command.get("mapped_row_key_count"), f"{label} mapped rows not all blocked")
        checks.check(command.get("matched_rows_source_policy_closed") == 0, f"{label} overclosed mapped rows")
        checks.check(command.get("matched_rows_reproduction_complete") == 0, f"{label} overclaims reproduction")
        checks.check(command.get("summary_source_policy_rows_closed") == 0, f"{label} summary overclosed rows")
        checks.check(command.get("summary_source_policy_rows_promoted") == 0, f"{label} summary overpromoted rows")
        flags = command.get("blocking_flags", {})
        checks.check(flags.get("schema_ready_is_not_promotion_ready") is True, f"{label} missing schema-ready-not-promotion flag")
        checks.check(flags.get("verified_authorized_execution_recorded") is False, f"{label} unexpectedly authorized")
        checks.check(flags.get("summary_rows_promoted") == 0, f"{label} summary row promotion flag changed")
        checks.check(flags.get("summary_rows_closed") == 0, f"{label} summary row closure flag changed")
        checks.check(flags.get("all_mapped_rows_promoted") is False, f"{label} overclaims mapped-row promotion")

    for token in [
        "Status: `expected_outputs_schema_ready_but_promotion_blocked`.",
        "Schema-ready commands / promotion-ready commands: `13/0`.",
        "Expected artifacts / CSV rows: `21/54`.",
        "Parseable CSV/JSON summaries: `13/8`.",
        "Command row references / unique RA/HI rows: `32/20`.",
        "Unique mapped RA/HI rows not promoted: `20`.",
        "Summary rows closed/promoted: `0/0`.",
        "Commands with schema-ready outputs but blocked promotion: `13`.",
        "Verified authorized execution recorded: `False`.",
        "Source-policy rows closed/promoted/promotion-ready: `0/0/0`.",
        "Source-policy execution allowed now/invoked/exact opt-in required: `False/False/True`.",
        "Safe action ids: `rebuild_read_only_audit_chain,rerun_read_only_validators,keep_narrowed_archive_provenance_only,monitor_reopen_conditions`.",
        "Opt-in action ids: `authorized_b4_ra_hi_source_policy_execution`.",
        f"Required approval/driver: `{builder.APPROVAL}/{EXPECTED_DRIVER}`.",
        "B4/B7 can close now: `False/False`.",
        "This audit records OC4 expected-output promotion readiness. It does not close the global objective blockers.",
        "blocker_open_by_id=OC4:True,OC6:True,OC12:True",
        "blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready",
        "blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False",
        "schema-ready expected outputs are only structure/fingerprint evidence",
    ]:
        checks.check(token in text, f"markdown missing token: {token}")

    if checks.errors:
        print("b4 expected-output promotion-readiness blocker audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print(
        "b4 expected-output promotion-readiness blocker audit validation: PASS "
        f"schema_ready={audit.get('schema_ready_command_count')}/{audit.get('command_count')} "
        f"promotion_ready={audit.get('promotion_ready_command_count')} "
        f"unique_rows={audit.get('unique_mapped_ra_hi_row_count')} "
        f"source_policy_rows_closed={audit.get('source_policy_rows_closed')}"
    )
    print("blocker_open_by_id=OC4:True,OC6:True,OC12:True")
    print("blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
