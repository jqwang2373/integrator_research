#!/usr/bin/env python3
"""Validate the read-only B4 source-policy execution handoff package."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
APPROVAL = (
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


def row_key(row: dict[str, Any]) -> str:
    explicit = row.get("row_key")
    if isinstance(explicit, str) and explicit:
        return explicit
    return f"{row.get('suite_id')}|{row.get('method')}|{row.get('example')}"


def expected_command_row_traceability(
    handoff: dict[str, Any],
    provenance: dict[str, Any],
) -> dict[str, Any]:
    batches = handoff.get("ra_hi_authorized_closeout_handoff", {}).get("execution_batches", [])
    rows = [row for row in provenance.get("rows", []) if isinstance(row, dict)]
    command_records: list[dict[str, Any]] = []
    command_ids: list[str] = []
    for batch in batches:
        if not isinstance(batch, dict):
            continue
        for command in batch.get("commands", []):
            if not isinstance(command, dict):
                continue
            command_id = str(command.get("id"))
            command_ids.append(command_id)
            matched_rows = [
                row for row in rows if command_id in (row.get("command_refs") or [])
            ]
            command_records.append(
                {
                    "id": command_id,
                    "batch_id": batch.get("id"),
                    "command": command.get("command"),
                    "declared_mapped_row_count": command.get("mapped_row_count"),
                    "traced_row_count": len(matched_rows),
                    "declared_matches_traced": command.get("mapped_row_count") == len(matched_rows),
                    "row_keys": [row_key(row) for row in matched_rows],
                    "suite_ids": sorted({str(row.get("suite_id")) for row in matched_rows}),
                    "source_policy_closed_rows": sum(
                        1 for row in matched_rows if row.get("source_policy_closed") is True
                    ),
                    "promotion_ready_rows": sum(
                        1 for row in matched_rows if row.get("promotion_ready_now") is True
                    ),
                    "unable_to_reproduce_rows": sum(
                        1 for row in matched_rows if row.get("unable_to_reproduce") is True
                    ),
                    "expected_output_exists_now": command.get("expected_output_exists_now"),
                    "expected_summary_exists_now": command.get("expected_summary_exists_now"),
                    "artifact_status": command.get("artifact_status"),
                }
            )

    command_id_set = set(command_ids)
    traced_rows = [
        row
        for row in rows
        if any(ref in command_id_set for ref in (row.get("command_refs") or []))
    ]
    unique_rows = sorted({row_key(row) for row in traced_rows})
    terminal_rows_with_command_refs = [
        row
        for row in traced_rows
        if row.get("unable_to_reproduce") is True
        or row.get("suite_id") in {"tfe2026_original_pendulum", "vp2024_velocity_partitioning"}
    ]
    ra_hi_rows = [
        row
        for row in rows
        if row.get("suite_id") in {"ra2021_absolute_coordinate", "hi2022_half_implicit"}
    ]
    ra_hi_unique_rows = sorted({row_key(row) for row in ra_hi_rows})
    rows_without_command_refs = [
        row for row in rows if not (row.get("command_refs") or [])
    ]
    summary = {
        "ready_command_count": len(command_records),
        "declared_mapped_row_reference_total": sum(
            int(command.get("declared_mapped_row_count") or 0)
            for command in command_records
        ),
        "traced_command_row_reference_total": sum(
            int(command.get("traced_row_count") or 0) for command in command_records
        ),
        "declared_vs_traced_mismatch_count": sum(
            1 for command in command_records if command.get("declared_matches_traced") is not True
        ),
        "unique_mapped_row_count": len(unique_rows),
        "ra2021_unique_mapped_rows": sum(
            1 for row in traced_rows if row.get("suite_id") == "ra2021_absolute_coordinate"
        ),
        "hi2022_unique_mapped_rows": sum(
            1 for row in traced_rows if row.get("suite_id") == "hi2022_half_implicit"
        ),
        "ra_hi_unique_row_count": len(ra_hi_unique_rows),
        "ra_hi_unique_rows_all_mapped": sorted(unique_rows) == ra_hi_unique_rows,
        "terminal_rows_with_command_refs": len(terminal_rows_with_command_refs),
        "rows_without_command_refs": len(rows_without_command_refs),
        "rows_without_command_refs_attempted_not_reproducible": sum(
            1 for row in rows_without_command_refs if row.get("unable_to_reproduce") is True
        ),
        "commands_without_traced_rows": [
            command.get("id")
            for command in command_records
            if command.get("traced_row_count") == 0
        ],
        "source_policy_closed_rows": sum(
            1 for row in traced_rows if row.get("source_policy_closed") is True
        ),
        "promotion_ready_rows": sum(
            1 for row in traced_rows if row.get("promotion_ready_now") is True
        ),
        "unable_to_reproduce_rows": sum(
            1 for row in traced_rows if row.get("unable_to_reproduce") is True
        ),
        "source_policy_disposition": "command_traceability_ready_not_authorized_not_promoted",
    }
    unique_row_records = [
        {
            "row_key": row_key(row),
            "suite_id": row.get("suite_id"),
            "method": row.get("method"),
            "example": row.get("example"),
            "command_refs": row.get("command_refs") or [],
            "source_policy_disposition": row.get("source_policy_disposition"),
            "source_policy_closed": row.get("source_policy_closed"),
            "promotion_ready_now": row.get("promotion_ready_now"),
            "unable_to_reproduce": row.get("unable_to_reproduce"),
            "primary_promotion_blocker": row.get("primary_promotion_blocker"),
        }
        for row in sorted(traced_rows, key=row_key)
    ]
    return {
        "summary": summary,
        "commands": command_records,
        "unique_rows": unique_row_records,
    }


def main() -> int:
    checks = Checks()
    try:
        handoff = read_json(PAPER / "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json")
        text = (PAPER / "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.md").read_text(
            encoding="utf-8",
            errors="replace",
        )
        packet = read_json(PAPER / "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json")
        ledger = read_json(PAPER / "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.json")
        closeout = read_json(PAPER / "RA_HI_SOURCE_POLICY_CLOSEOUT_CHECKLIST.json")
        matrix = read_json(PAPER / "RA_HI_SOURCE_POLICY_PROMOTION_BLOCKER_MATRIX.json")
        public_refresh = read_json(PAPER / "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.json")
        self_attempt = read_json(PAPER / "SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json")
        provenance = read_json(PAPER / "FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.json")
        command_freeze = read_json(PAPER / "B4_SOURCE_POLICY_COMMAND_PREFLIGHT_FREEZE_20260620.json")
        expected_output_schema_audit = read_json(
            PAPER / "B4_SOURCE_POLICY_EXPECTED_OUTPUT_SCHEMA_AUDIT_20260620.json"
        )
    except Exception as exc:  # noqa: BLE001
        print(f"B4 source-policy execution handoff package validation: FAIL\n- {exc}")
        return 1

    checks.check(
        handoff.get("schema") == "b4-source-policy-execution-handoff-package-v1",
        "schema changed",
    )
    checks.check(
        handoff.get("status") == "source_policy_execution_handoff_ready_not_authorized_not_run",
        "status changed",
    )
    checks.check(handoff.get("read_only") is True, "handoff must be read-only")
    checks.check(handoff.get("handoff_does_not_authorize_execution") is True, "handoff authorizes execution")
    checks.check(handoff.get("execution_authorized") is False, "handoff unexpectedly authorized execution")
    checks.check(handoff.get("commands_not_run_by_handoff") is True, "handoff ran commands")
    checks.check(handoff.get("source_policy_execution_invoked") is False, "handoff invoked source-policy execution")
    checks.check(
        handoff.get("source_policy_execution_allowed_now") is False,
        "handoff allows source-policy execution without opt-in",
    )
    checks.check(
        handoff.get("exact_b4_opt_in_required_for_execution") is True,
        "handoff lost exact B4 opt-in requirement",
    )
    checks.check(handoff.get("safe_action_ids") == EXPECTED_SAFE_ACTION_IDS, "safe action ids changed")
    checks.check(handoff.get("opt_in_action_ids") == EXPECTED_OPT_IN_ACTION_IDS, "opt-in action ids changed")
    checks.check(
        handoff.get("next_safe_action_ids") == handoff.get("safe_action_ids") == EXPECTED_SAFE_ACTION_IDS,
        "next safe action ids stale",
    )
    checks.check(
        [item.get("id") for item in handoff.get("next_safe_actions", [])]
        == EXPECTED_SAFE_ACTION_IDS,
        "next safe actions stale",
    )
    checks.check(handoff.get("heavy_numerical_run_invoked") is False, "handoff invoked heavy run")
    checks.check(handoff.get("run_v047_invoked") is False, "handoff invoked run_v047")
    checks.check(handoff.get("v048_runner_invoked") is False, "handoff invoked v048")
    checks.check(handoff.get("source_policy_closed") is False, "top-level source-policy closure overclaimed")
    checks.check(handoff.get("source_policy_closed_ratio") == "0/40", "top-level source-policy ratio changed")
    checks.check(handoff.get("source_policy_rows_closed") == 0, "top-level source-policy rows overclosed")
    checks.check(handoff.get("source_policy_rows_total") == 40, "top-level source-policy total changed")
    checks.check(
        handoff.get("terminal_unable_to_reproduce_rows") == 20,
        "top-level terminal unable-to-reproduce rows changed",
    )
    checks.check(
        handoff.get("still_requiring_execution_or_promotion_rows") == 20,
        "top-level still-requiring rows changed",
    )
    checks.check(handoff.get("ready_command_count") == 13, "top-level ready command count changed")
    checks.check(
        handoff.get("ready_command_mapped_external_rows") == 20,
        "top-level ready mapped rows changed",
    )
    checks.check(handoff.get("opt_in_required_command_count") == 13, "top-level opt-in command count changed")
    checks.check(
        handoff.get("opt_in_required_mapped_external_rows") == 20,
        "top-level opt-in mapped rows changed",
    )
    checks.check(handoff.get("opt_in_required_phrase") == APPROVAL, "top-level opt-in phrase changed")
    checks.check(handoff.get("exact_approval_statement") == APPROVAL, "top-level exact approval changed")
    checks.check(
        handoff.get("required_user_approval_statement") == APPROVAL,
        "top-level required approval changed",
    )
    checks.check(
        handoff.get("guarded_execution_driver") == "run_b4_source_policy_after_opt_in.sh",
        "top-level guarded driver changed",
    )
    checks.check(
        handoff.get("driver_requires_exact_approval") is True,
        "top-level guarded driver exact-approval marker changed",
    )
    checks.check(
        handoff.get("driver_does_not_authorize_execution") is True,
        "top-level guarded driver authorization marker changed",
    )
    checks.check(handoff.get("execution_invoked_by_packet") is False, "top-level packet execution marker changed")
    checks.check(handoff.get("submission_ready") is False, "top-level submission readiness overclaimed")

    for source_file in [
        "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json",
        "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.json",
        "RA_HI_SOURCE_POLICY_CLOSEOUT_CHECKLIST.json",
        "RA_HI_SOURCE_POLICY_PROMOTION_BLOCKER_MATRIX.json",
        "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.json",
        "SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json",
        "FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.json",
        "B4_SOURCE_POLICY_EXPECTED_OUTPUT_SCHEMA_AUDIT_20260620.json",
    ]:
        checks.check(source_file in handoff.get("source_files", []), f"missing source file: {source_file}")

    rows = handoff.get("source_policy_row_state", {})
    checks.check(rows.get("total") == ledger.get("source_policy_rows_total") == 40, "row total changed")
    checks.check(rows.get("closed") == ledger.get("source_policy_rows_closed") == 0, "source-policy rows overclosed")
    checks.check(
        rows.get("attempted_not_reproducible")
        == ledger.get("source_policy_rows_attempted_not_reproducible")
        == 20,
        "attempted-not-reproducible rows changed",
    )
    checks.check(
        rows.get("unable_to_reproduce") == ledger.get("source_policy_rows_unable_to_reproduce") == 20,
        "unable-to-reproduce rows changed",
    )
    checks.check(
        rows.get("still_requiring_execution_or_promotion")
        == ledger.get("source_policy_rows_still_requiring_execution_or_promotion")
        == 20,
        "still-requiring-execution rows changed",
    )
    checks.check(rows.get("rows_with_launch_command_refs") == 20, "launch-command rows changed")
    checks.check(rows.get("rows_without_launch_command_refs") == 20, "no-launch-command rows changed")

    terminal = handoff.get("terminal_unable_to_reproduce", {})
    checks.check(terminal.get("status") == self_attempt.get("status"), "terminal status changed")
    checks.check(terminal.get("public_code_refresh_status") == public_refresh.get("status"), "refresh status changed")
    checks.check(terminal.get("row_count") == self_attempt.get("row_count") == 20, "terminal row count changed")
    checks.check(
        terminal.get("public_code_available_rows") == public_refresh.get("public_code_available_rows") == 0,
        "public code unexpectedly available",
    )
    checks.check(
        terminal.get("self_reproduction_attempted_rows")
        == self_attempt.get("self_reproduction_attempted_rows")
        == 20,
        "self-reproduction attempted rows changed",
    )
    checks.check(
        terminal.get("unable_to_reproduce_rows") == self_attempt.get("unable_to_reproduce_rows") == 20,
        "terminal unable rows changed",
    )
    checks.check(terminal.get("source_policy_rows_closed") == 0, "terminal suites overclosed rows")
    terminal_suites = {
        item.get("suite_id"): item
        for item in terminal.get("suites", [])
        if isinstance(item, dict)
    }
    checks.check(terminal_suites.get("tfe2026_original_pendulum", {}).get("row_count") == 16, "TFE row count changed")
    checks.check(
        terminal_suites.get("tfe2026_original_pendulum", {}).get("unable_to_reproduce_rows") == 16,
        "TFE unable rows changed",
    )
    checks.check(terminal_suites.get("vp2024_velocity_partitioning", {}).get("row_count") == 4, "VP row count changed")
    checks.check(
        terminal_suites.get("vp2024_velocity_partitioning", {}).get("unable_to_reproduce_rows") == 4,
        "VP unable rows changed",
    )

    ra_hi = handoff.get("ra_hi_authorized_closeout_handoff", {})
    checks.check(ra_hi.get("status") == closeout.get("status"), "RA/HI closeout status changed")
    checks.check(ra_hi.get("promotion_blocker_status") == matrix.get("status"), "RA/HI promotion status changed")
    checks.check(ra_hi.get("public_source_root_available_rows") == 20, "RA/HI public-root rows changed")
    checks.check(ra_hi.get("no_public_code_rows_included") == 0, "RA/HI incorrectly marked no-public-code")
    checks.check(ra_hi.get("row_count") == 20, "RA/HI row count changed")
    checks.check(ra_hi.get("ra2021_rows") == 12 and ra_hi.get("hi2022_rows") == 8, "RA/HI suite counts changed")
    checks.check(ra_hi.get("source_policy_rows_promoted") == 0, "RA/HI rows promoted unexpectedly")
    checks.check(ra_hi.get("source_policy_rows_completed") == 0, "RA/HI rows completed unexpectedly")
    checks.check(ra_hi.get("source_policy_rows_not_promoted") == 20, "RA/HI not-promoted rows changed")
    checks.check(ra_hi.get("current_evidence_terminal_not_promotable_rows") == 20, "RA/HI terminal evidence changed")
    checks.check(
        ra_hi.get("future_promotion_requires_authorized_execution_or_new_artifact_rows") == 20,
        "RA/HI future authorization/artifact rows changed",
    )
    checks.check(ra_hi.get("source_policy_reproduction_complete_rows") == 0, "RA/HI reproduction overclaimed")
    checks.check(
        ra_hi.get("ready_command_batch_count") == packet.get("ready_command_batch_count") == 2,
        "ready batch count changed",
    )
    checks.check(ra_hi.get("ready_command_count") == packet.get("ready_command_count") == 13, "ready command count changed")
    checks.check(
        ra_hi.get("ready_command_mapped_external_rows")
        == packet.get("ready_command_mapped_external_rows")
        == 20,
        "ready command mapped rows changed",
    )
    checks.check(
        ra_hi.get("unaddressed_external_rows_after_ready_commands") == 0,
        "unaddressed rows changed",
    )
    batches = {item.get("id"): item for item in ra_hi.get("execution_batches", []) if isinstance(item, dict)}
    checks.check(set(batches) == {"ra2021_ready_after_explicit_1e_4_opt_in", "hi2022_ready_no_1e_4_selected_candidate"}, "batch ids changed")
    checks.check(
        batches.get("ra2021_ready_after_explicit_1e_4_opt_in", {}).get("command_count") == 5
        and batches.get("ra2021_ready_after_explicit_1e_4_opt_in", {}).get("mapped_external_rows") == 12
        and batches.get("ra2021_ready_after_explicit_1e_4_opt_in", {}).get(
            "all_commands_require_allow_source_policy_1e_4"
        )
        is True,
        "RA batch boundary changed",
    )
    checks.check(
        batches.get("hi2022_ready_no_1e_4_selected_candidate", {}).get("command_count") == 8
        and batches.get("hi2022_ready_no_1e_4_selected_candidate", {}).get("mapped_external_rows") == 8,
        "HI batch boundary changed",
    )
    for batch in batches.values():
        checks.check(batch.get("all_commands_parse_ok") is True, f"{batch.get('id')} parse preflight failed")
        checks.check(
            batch.get("all_commands_shell_safe_single_command") is True,
            f"{batch.get('id')} shell-safe preflight failed",
        )
        checks.check(
            batch.get("all_commands_dry_run_only_in_packet") is True,
            f"{batch.get('id')} lost dry-run marker",
        )
        checks.check(
            batch.get("all_commands_marked_not_executed_by_packet") is True,
            f"{batch.get('id')} marked executed by packet",
        )

    expected_traceability = expected_command_row_traceability(handoff, provenance)
    traceability = handoff.get("command_row_traceability", {})
    trace_summary = traceability.get("summary", {})
    checks.check(
        traceability == expected_traceability,
        "command-to-row traceability stale or not copied from provenance",
    )
    checks.check(
        ra_hi.get("command_row_traceability_summary") == expected_traceability.get("summary"),
        "RA/HI command traceability summary mirror stale",
    )
    checks.check(trace_summary.get("ready_command_count") == 13, "traceability command count changed")
    checks.check(
        trace_summary.get("declared_mapped_row_reference_total") == 32,
        "traceability declared row-reference total changed",
    )
    checks.check(
        trace_summary.get("traced_command_row_reference_total") == 32,
        "traceability traced row-reference total changed",
    )
    checks.check(
        trace_summary.get("declared_vs_traced_mismatch_count") == 0,
        "traceability declared/traced mismatch introduced",
    )
    checks.check(trace_summary.get("unique_mapped_row_count") == 20, "traceability unique row count changed")
    checks.check(trace_summary.get("ra2021_unique_mapped_rows") == 12, "RA2021 traceability row count changed")
    checks.check(trace_summary.get("hi2022_unique_mapped_rows") == 8, "HI2022 traceability row count changed")
    checks.check(trace_summary.get("ra_hi_unique_row_count") == 20, "RA/HI traceability row count changed")
    checks.check(trace_summary.get("ra_hi_unique_rows_all_mapped") is True, "not all RA/HI rows mapped")
    checks.check(
        trace_summary.get("terminal_rows_with_command_refs") == 0,
        "terminal TFE/VP rows unexpectedly mapped to B4 commands",
    )
    checks.check(trace_summary.get("rows_without_command_refs") == 20, "terminal no-command row count changed")
    checks.check(
        trace_summary.get("rows_without_command_refs_attempted_not_reproducible") == 20,
        "no-command terminal row accounting changed",
    )
    checks.check(trace_summary.get("commands_without_traced_rows") == [], "a ready command has no traced rows")
    checks.check(trace_summary.get("source_policy_closed_rows") == 0, "traceability overclosed rows")
    checks.check(trace_summary.get("promotion_ready_rows") == 0, "traceability overpromoted rows")
    checks.check(trace_summary.get("unable_to_reproduce_rows") == 0, "RA/HI traced rows marked unable")
    checks.check(
        trace_summary.get("source_policy_disposition")
        == "command_traceability_ready_not_authorized_not_promoted",
        "traceability disposition changed",
    )
    trace_commands = traceability.get("commands", [])
    checks.check(len(trace_commands) == 13, "traceability command rows changed")
    checks.check(
        all(command.get("declared_matches_traced") is True for command in trace_commands),
        "some command trace counts do not match declared mapped rows",
    )
    checks.check(
        len(traceability.get("unique_rows", [])) == 20,
        "traceability unique-row table changed",
    )
    checks.check(
        command_freeze.get("status") == "command_preflight_frozen_not_authorized_not_run_not_promoted",
        "B4 command preflight freeze status changed",
    )
    checks.check(command_freeze.get("ready_command_count") == 13, "B4 command freeze command count changed")
    checks.check(
        command_freeze.get("unique_mapped_ra_hi_rows") == 20,
        "B4 command freeze mapped row count changed",
    )
    checks.check(
        command_freeze.get("declared_row_reference_total") == 32
        and command_freeze.get("traced_row_reference_total") == 32
        and command_freeze.get("declared_vs_traced_mismatch_count") == 0,
        "B4 command freeze row traceability changed",
    )
    checks.check(
        command_freeze.get("expected_artifacts_existing_now") == 21
        and command_freeze.get("expected_artifact_count") == 21,
        "B4 command freeze expected-artifact count changed",
    )
    checks.check(
        command_freeze.get("commands_executed_by_freeze") is False,
        "B4 command freeze executed commands",
    )
    checks.check(
        command_freeze.get("source_policy_rows_closed") == 0
        and command_freeze.get("source_policy_rows_total") == 40,
        "B4 command freeze overclosed source-policy rows",
    )
    schema_audit = handoff.get("expected_output_schema_audit", {})
    checks.check(
        schema_audit.get("status")
        == expected_output_schema_audit.get("status")
        == "expected_outputs_schema_ready_not_authorized_not_run_not_promoted",
        "B4 expected-output schema audit status changed",
    )
    checks.check(schema_audit.get("command_count") == 13, "schema audit command count changed")
    checks.check(
        schema_audit.get("expected_artifact_count") == 21
        and schema_audit.get("artifacts_existing_now") == 21
        and schema_audit.get("artifacts_sha256_match_freeze") == 21,
        "schema audit artifact accounting changed",
    )
    checks.check(
        schema_audit.get("csv_parseable_artifacts") == 13
        and schema_audit.get("json_summary_parseable_artifacts") == 8
        and schema_audit.get("schema_ready_commands") == 13,
        "schema audit parseability/readiness changed",
    )
    checks.check(
        schema_audit.get("source_policy_rows_closed") == 0
        and schema_audit.get("promotion_ready_rows") == 0
        and schema_audit.get("commands_executed_by_audit") is False,
        "schema audit overclosed or executed commands",
    )
    checks.check(
        schema_audit.get("expected_output_schema_audit_sha256")
        == expected_output_schema_audit.get("expected_output_schema_audit_sha256"),
        "schema audit digest not propagated",
    )
    expected_schema_traceability = {
        "commands_with_shell_command": 13,
        "commands_with_expected_output_path": 13,
        "commands_with_expected_summary_path": 8,
        "commands_without_expected_summary_path": 5,
        "commands_with_existing_expected_output": 13,
        "commands_with_existing_expected_summary": 8,
        "source_policy_execution_invoked": False,
        "commands_executed_by_audit": False,
    }
    checks.check(
        schema_audit.get("command_traceability")
        == handoff.get("expected_output_schema_command_traceability")
        == expected_output_schema_audit.get("command_traceability")
        == expected_schema_traceability,
        "schema audit command traceability not propagated",
    )

    approval = handoff.get("approval_boundary", {})
    checks.check(approval.get("exact_required_user_approval_statement") == APPROVAL, "approval statement changed")
    checks.check(approval.get("explicit_user_opt_in_required_before_any_command") is True, "opt-in boundary missing")
    checks.check(approval.get("packet_does_not_authorize_execution") is True, "packet authorizes execution")
    checks.check(approval.get("execution_invoked_by_packet") is False, "packet invoked execution")
    checks.check(
        approval.get("guarded_execution_protocol", {}).get("execute_commands_now") is False,
        "guarded protocol executes now",
    )
    checks.check(
        approval.get("guarded_execution_driver", {}).get("requires_exact_approval_argument") is True,
        "guarded driver no longer requires exact approval",
    )

    promotion = handoff.get("post_execution_promotion_boundary", {})
    checks.check(promotion.get("post_execution_promotion_required") is True, "promotion guard missing")
    checks.check(promotion.get("source_policy_rows_closed_now") == 0, "promotion overclosed rows")
    checks.check(promotion.get("b4_can_close_now") is False, "handoff overcloses B4")
    checks.check(promotion.get("b7_can_close_now") is False, "handoff overcloses B7")
    checks.check(promotion.get("b4_can_close_after_ready_commands_only") is False, "commands alone close B4")
    checks.check(promotion.get("b7_can_close_after_ready_commands_only") is False, "commands alone close B7")
    checks.check(promotion.get("existing_artifact_promotion_ready_count") == 0, "existing artifacts overpromoted")
    checks.check(
        promotion.get("promotion_contract_status") == "promotion_contract_defined_no_rows_promoted",
        "promotion contract status changed",
    )
    checks.check(promotion.get("all_required_checks_satisfied_now") is False, "promotion checklist overclosed")

    opt_in = handoff.get("opt_in_required_actions", {})
    checks.check(opt_in.get("required_user_approval_statement") == APPROVAL, "opt-in statement changed")
    checks.check(opt_in.get("driver") == "run_b4_source_policy_after_opt_in.sh", "driver path changed")
    checks.check(opt_in.get("command_count") == 13, "opt-in command count changed")
    checks.check(opt_in.get("mapped_external_rows") == 20, "opt-in mapped rows changed")
    checks.check(len(opt_in.get("commands", [])) == 13, "opt-in command list length changed")

    closure = handoff.get("closure_state", {})
    checks.check(closure.get("source_policy_rows_closed") == 0, "closure state overclosed rows")
    checks.check(closure.get("source_policy_rows_total") == 40, "closure state row total changed")
    checks.check(closure.get("full_source_policy_reproduction_ready") is False, "full source overclaimed")
    checks.check(closure.get("external_superiority_claim_allowed") is False, "external superiority overclaimed")
    checks.check(closure.get("submission_ready") is False, "submission readiness overclaimed")

    for token in [
        "Status: `source_policy_execution_handoff_ready_not_authorized_not_run`.",
        "Source-policy rows closed/total: `0/40`.",
        "Terminal unable-to-reproduce rows: `20`.",
        "RA/HI rows requiring authorized closeout or new artifact: `20`.",
        "Ready command batches/commands/mapped rows: `2/13/20`.",
        "Command traceability unique RA/HI rows: `20/20`.",
        "Command traceability references/declared references/mismatches: `32/32/0`.",
        "Command traceability terminal rows/source-policy closed rows: `0/0`.",
        "Expected output schema audit: `expected_outputs_schema_ready_not_authorized_not_run_not_promoted`; commands/artifacts/hash-match/parseable/schema-ready/closed `13/21/21/13/13/0`.",
        "Expected output schema command traceability shell/output/summary/no-summary/existing-output/existing-summary: `13/13/8/5/13/8`.",
        "Execution authorized: `False`.",
        "Commands run by this handoff: `False`.",
        "Source-policy execution allowed now/invoked/exact opt-in required: `False/False/True`.",
        "Safe action ids: `rebuild_read_only_audit_chain,rerun_read_only_validators,keep_narrowed_archive_provenance_only,monitor_reopen_conditions`.",
        "Opt-in action ids: `authorized_b4_ra_hi_source_policy_execution`.",
        "Post-execution promotion required: `True`.",
        "B4/B7 can close now: `False/False`.",
        "`tfe2026_original_pendulum`",
        "`vp2024_velocity_partitioning`",
        "`ra2021_ready_after_explicit_1e_4_opt_in`",
        "`hi2022_ready_no_1e_4_selected_candidate`",
        "`ra2021_public_timing_all_forms_models` | `12` | `12` | `0` | `0`",
        "`hi2022_selected_t8_rA_half_double_pendulum` | `1` | `1` | `0` | `0`",
        f"`{APPROVAL}`",
    ]:
        checks.check(token in text, f"markdown missing token: {token}")

    if checks.errors:
        print("B4 source-policy execution handoff package validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("B4 source-policy execution handoff package validation: PASS")
    print("source_policy_closed=0/40")
    print("terminal_unable_to_reproduce_rows=20")
    print("ready_command_count=13")
    print("opt_in_required_command_count=13")
    print("opt_in_required_mapped_external_rows=20")
    print("execution_authorized=False")
    print("source_policy_execution_invoked=False")
    print("source_policy_execution_allowed_now=False")
    print("safe_action_ids=rebuild_read_only_audit_chain,rerun_read_only_validators,keep_narrowed_archive_provenance_only,monitor_reopen_conditions")
    print("opt_in_action_ids=authorized_b4_ra_hi_source_policy_execution")
    print("exact_approval_statement=present")
    print("guarded_execution_driver=run_b4_source_policy_after_opt_in.sh")
    print("driver_requires_exact_approval=True")
    print("command_preflight_freeze=PASS")
    print("expected_output_schema_audit=PASS")
    print("submission_ready=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
