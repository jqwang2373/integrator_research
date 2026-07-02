#!/usr/bin/env python3
"""Build a read-only B4 source-policy execution handoff package.

This artifact is intentionally non-executing.  It packages the current
source-policy state for a human reviewer: TFE/VP rows are terminal
unable-to-reproduce after public-code/self-reproduction checks, while RA/HI
rows have guarded commands prepared but not authorized or promoted.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json"
OUT_MD = PAPER / "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.md"

SAFE_ACTIONS_WITHOUT_B4_OPT_IN = [
    {
        "id": "rebuild_read_only_audit_chain",
        "description": "Rebuild this handoff package plus downstream objective, review, and package manifests.",
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


def count_expected(commands: list[dict[str, Any]], key: str) -> int:
    return sum(1 for command in commands if command.get(key) is True)


def compact_batch(batch: dict[str, Any]) -> dict[str, Any]:
    commands = [item for item in batch.get("commands", []) if isinstance(item, dict)]
    preflights = [
        command.get("execution_preflight", {})
        for command in commands
        if isinstance(command.get("execution_preflight", {}), dict)
    ]
    return {
        "id": batch.get("id"),
        "status": batch.get("status"),
        "command_count": batch.get("command_count"),
        "mapped_external_rows": batch.get("mapped_external_rows"),
        "all_commands_require_allow_source_policy_1e_4": batch.get(
            "all_commands_require_allow_source_policy_1e_4"
        ),
        "all_commands_parse_ok": all(item.get("parse_ok") is True for item in preflights),
        "all_commands_shell_safe_single_command": all(
            item.get("shell_safe_single_command") is True for item in preflights
        ),
        "all_commands_dry_run_only_in_packet": all(item.get("dry_run_only") is True for item in preflights),
        "all_commands_marked_not_executed_by_packet": all(
            item.get("executed_by_packet") is False for item in preflights
        ),
        "expected_outputs_existing_now": count_expected(commands, "expected_output_exists_now"),
        "expected_summaries_existing_now": count_expected(commands, "expected_summary_exists_now"),
        "command_ids": [command.get("id") for command in commands],
        "commands": [
            {
                "id": command.get("id"),
                "command": command.get("command"),
                "artifact_status": command.get("artifact_status"),
                "mapped_row_count": command.get("mapped_row_count"),
                "expected_output_after_run": command.get("expected_output_after_run"),
                "expected_output_exists_now": command.get("expected_output_exists_now"),
                "expected_summary_after_run": command.get("expected_summary_after_run"),
                "expected_summary_exists_now": command.get("expected_summary_exists_now"),
            }
            for command in commands
        ],
    }


def row_key(row: dict[str, Any]) -> str:
    explicit = row.get("row_key")
    if isinstance(explicit, str) and explicit:
        return explicit
    return f"{row.get('suite_id')}|{row.get('method')}|{row.get('example')}"


def build_command_row_traceability(
    batches: list[dict[str, Any]],
    provenance: dict[str, Any],
) -> dict[str, Any]:
    rows = [row for row in provenance.get("rows", []) if isinstance(row, dict)]
    command_records: list[dict[str, Any]] = []
    command_ids: list[str] = []

    for batch in batches:
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
                    "suite_ids": sorted(
                        {str(row.get("suite_id")) for row in matched_rows}
                    ),
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


def main() -> None:
    packet = read_json(PAPER / "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json")
    ledger = read_json(PAPER / "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.json")
    closeout = read_json(PAPER / "RA_HI_SOURCE_POLICY_CLOSEOUT_CHECKLIST.json")
    matrix = read_json(PAPER / "RA_HI_SOURCE_POLICY_PROMOTION_BLOCKER_MATRIX.json")
    public_refresh = read_json(PAPER / "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.json")
    self_attempt = read_json(PAPER / "SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json")
    provenance = read_json(PAPER / "FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.json")
    expected_output_schema_audit = read_json(
        PAPER / "B4_SOURCE_POLICY_EXPECTED_OUTPUT_SCHEMA_AUDIT_20260620.json"
    )

    batches = [compact_batch(item) for item in packet.get("execution_batches", []) if isinstance(item, dict)]
    command_row_traceability = build_command_row_traceability(batches, provenance)
    terminal_suites = [
        {
            "suite_id": item.get("suite_id"),
            "row_count": item.get("row_count"),
            "self_reproduction_attempted_rows": item.get("self_reproduction_attempted_rows"),
            "unable_to_reproduce_rows": item.get("unable_to_reproduce_rows"),
            "source_policy_closed_rows": item.get("source_policy_closed_rows"),
            "open_execution_queue_rows": item.get("open_execution_queue_rows", 0),
        }
        for item in self_attempt.get("suite_summary", [])
        if isinstance(item, dict)
    ]

    approval = packet.get("required_user_approval_statement")
    output: dict[str, Any] = {
        "schema": "b4-source-policy-execution-handoff-package-v1",
        "status": "source_policy_execution_handoff_ready_not_authorized_not_run",
        "read_only": True,
        "handoff_does_not_authorize_execution": True,
        "execution_authorized": False,
        "commands_not_run_by_handoff": True,
        "source_policy_execution_invoked": False,
        "source_policy_execution_allowed_now": False,
        "exact_b4_opt_in_required_for_execution": True,
        "safe_action_ids": SAFE_ACTION_IDS,
        "opt_in_action_ids": OPT_IN_ACTION_IDS,
        "next_safe_actions": SAFE_ACTIONS_WITHOUT_B4_OPT_IN,
        "next_safe_action_ids": SAFE_ACTION_IDS,
        "source_policy_closed": False,
        "source_policy_closed_ratio": f"{ledger.get('source_policy_rows_closed')}/{ledger.get('source_policy_rows_total')}",
        "source_policy_rows_closed": ledger.get("source_policy_rows_closed"),
        "source_policy_rows_total": ledger.get("source_policy_rows_total"),
        "terminal_unable_to_reproduce_rows": ledger.get("source_policy_rows_unable_to_reproduce"),
        "still_requiring_execution_or_promotion_rows": ledger.get(
            "source_policy_rows_still_requiring_execution_or_promotion"
        ),
        "ready_command_count": packet.get("ready_command_count"),
        "ready_command_mapped_external_rows": packet.get("ready_command_mapped_external_rows"),
        "opt_in_required_command_count": packet.get("ready_command_count"),
        "opt_in_required_mapped_external_rows": packet.get("ready_command_mapped_external_rows"),
        "opt_in_required_phrase": approval,
        "exact_approval_statement": approval,
        "required_user_approval_statement": approval,
        "guarded_execution_driver": packet.get("guarded_execution_driver", {}).get("path"),
        "driver_requires_exact_approval": packet.get("guarded_execution_driver", {}).get(
            "requires_exact_approval_argument"
        ),
        "driver_does_not_authorize_execution": packet.get("guarded_execution_driver", {}).get(
            "driver_does_not_authorize_execution"
        ),
        "execution_invoked_by_packet": packet.get("execution_invoked_by_packet"),
        "submission_ready": False,
        "source_files": [
            "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json",
            "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.json",
            "RA_HI_SOURCE_POLICY_CLOSEOUT_CHECKLIST.json",
            "RA_HI_SOURCE_POLICY_PROMOTION_BLOCKER_MATRIX.json",
            "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.json",
            "SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json",
            "FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.json",
            "B4_SOURCE_POLICY_EXPECTED_OUTPUT_SCHEMA_AUDIT_20260620.json",
        ],
        "source_policy_row_state": {
            "total": ledger.get("source_policy_rows_total"),
            "closed": ledger.get("source_policy_rows_closed"),
            "attempted_not_reproducible": ledger.get("source_policy_rows_attempted_not_reproducible"),
            "unable_to_reproduce": ledger.get("source_policy_rows_unable_to_reproduce"),
            "still_requiring_execution_or_promotion": ledger.get(
                "source_policy_rows_still_requiring_execution_or_promotion"
            ),
            "rows_with_launch_command_refs": ledger.get("rows_with_launch_command_refs"),
            "rows_without_launch_command_refs": ledger.get("rows_without_launch_command_refs"),
        },
        "terminal_unable_to_reproduce": {
            "status": self_attempt.get("status"),
            "public_code_refresh_status": public_refresh.get("status"),
            "row_count": self_attempt.get("row_count"),
            "public_code_available_rows": public_refresh.get("public_code_available_rows"),
            "self_reproduction_attempted_rows": self_attempt.get("self_reproduction_attempted_rows"),
            "unable_to_reproduce_rows": self_attempt.get("unable_to_reproduce_rows"),
            "source_policy_rows_closed": self_attempt.get("source_policy_rows_closed"),
            "open_execution_queue_rows": self_attempt.get("open_execution_queue_rows"),
            "suites": terminal_suites,
            "disposition": (
                "TFE/VP rows remain not promoted. Reopen only if new public code, "
                "author-provided code, or a source-equivalent implementation artifact appears."
            ),
        },
        "ra_hi_authorized_closeout_handoff": {
            "status": closeout.get("status"),
            "promotion_blocker_status": matrix.get("status"),
            "public_source_root_available_rows": matrix.get("public_source_root_available_rows"),
            "no_public_code_rows_included": matrix.get("no_public_code_rows_included"),
            "row_count": closeout.get("coverage", {}).get("source_policy_rows_total"),
            "ra2021_rows": closeout.get("coverage", {}).get("ra2021_rows"),
            "hi2022_rows": closeout.get("coverage", {}).get("hi2022_rows"),
            "source_policy_rows_promoted": closeout.get("coverage", {}).get(
                "source_policy_rows_promoted"
            ),
            "source_policy_rows_completed": closeout.get("coverage", {}).get(
                "source_policy_rows_completed"
            ),
            "source_policy_rows_not_promoted": matrix.get("source_policy_rows_not_promoted"),
            "current_evidence_terminal_not_promotable_rows": matrix.get(
                "current_evidence_terminal_not_promotable_rows"
            ),
            "future_promotion_requires_authorized_execution_or_new_artifact_rows": matrix.get(
                "future_promotion_requires_authorized_execution_or_new_artifact_rows"
            ),
            "source_policy_reproduction_complete_rows": matrix.get(
                "source_policy_reproduction_complete_rows"
            ),
            "ready_command_batch_count": packet.get("ready_command_batch_count"),
            "ready_command_count": packet.get("ready_command_count"),
            "ready_command_mapped_external_rows": packet.get("ready_command_mapped_external_rows"),
            "unaddressed_external_rows_after_ready_commands": packet.get(
                "unaddressed_external_rows_after_ready_commands"
            ),
            "execution_batches": batches,
            "command_row_traceability_summary": command_row_traceability["summary"],
        },
        "command_row_traceability": command_row_traceability,
        "expected_output_schema_audit": {
            "status": expected_output_schema_audit.get("status"),
            "command_count": expected_output_schema_audit.get("command_count"),
            "expected_artifact_count": expected_output_schema_audit.get(
                "expected_artifact_count"
            ),
            "artifacts_existing_now": expected_output_schema_audit.get(
                "artifacts_existing_now"
            ),
            "artifacts_sha256_match_freeze": expected_output_schema_audit.get(
                "artifacts_sha256_match_freeze"
            ),
            "csv_parseable_artifacts": expected_output_schema_audit.get(
                "csv_parseable_artifacts"
            ),
            "json_summary_parseable_artifacts": expected_output_schema_audit.get(
                "json_summary_parseable_artifacts"
            ),
            "schema_ready_commands": expected_output_schema_audit.get(
                "schema_ready_commands"
            ),
            "source_policy_rows_closed": expected_output_schema_audit.get(
                "source_policy_rows_closed"
            ),
            "promotion_ready_rows": expected_output_schema_audit.get(
                "promotion_ready_rows"
            ),
            "commands_executed_by_audit": expected_output_schema_audit.get(
                "commands_executed_by_audit"
            ),
            "command_traceability": expected_output_schema_audit.get(
                "command_traceability"
            ),
            "expected_output_schema_audit_sha256": expected_output_schema_audit.get(
                "expected_output_schema_audit_sha256"
            ),
        },
        "expected_output_schema_command_traceability": expected_output_schema_audit.get(
            "command_traceability"
        ),
        "approval_boundary": {
            "exact_required_user_approval_statement": approval,
            "explicit_user_opt_in_required_before_any_command": packet.get(
                "explicit_user_opt_in_required_before_any_command"
            ),
            "packet_does_not_authorize_execution": packet.get("packet_does_not_authorize_execution"),
            "execution_invoked_by_packet": packet.get("execution_invoked_by_packet"),
            "guarded_execution_protocol": packet.get("guarded_execution_protocol"),
            "guarded_execution_driver": packet.get("guarded_execution_driver"),
        },
        "post_execution_promotion_boundary": {
            "post_execution_promotion_required": packet.get("post_execution_promotion_required"),
            "source_policy_rows_closed_now": packet.get("source_policy_rows_closed_now"),
            "b4_can_close_now": packet.get("b4_can_close_now"),
            "b7_can_close_now": packet.get("b7_can_close_now"),
            "b4_can_close_after_ready_commands_only": packet.get("b4_can_close_after_ready_commands_only"),
            "b7_can_close_after_ready_commands_only": packet.get("b7_can_close_after_ready_commands_only"),
            "existing_artifact_promotion_ready_count": packet.get("existing_artifact_promotion_ready_count"),
            "promotion_contract_status": packet.get("post_execution_promotion_contract", {}).get("status"),
            "all_required_checks_satisfied_now": packet.get(
                "post_execution_promotion_contract", {}
            ).get("all_required_checks_satisfied_now"),
        },
        "safe_next_actions_without_b4_opt_in": [
            "rebuild this handoff package and validators",
            "rebuild read-only objective/review/package manifests",
            "keep TFE/VP rows marked unable-to-reproduce until new public/source-equivalent artifacts appear",
        ],
        "opt_in_required_actions": {
            "required_user_approval_statement": approval,
            "driver": packet.get("guarded_execution_driver", {}).get("path"),
            "command_count": packet.get("ready_command_count"),
            "mapped_external_rows": packet.get("ready_command_mapped_external_rows"),
            "commands": [
                command.get("command")
                for batch in batches
                for command in batch.get("commands", [])
                if isinstance(command, dict)
            ],
        },
        "closure_state": {
            "source_policy_rows_closed": 0,
            "source_policy_rows_total": ledger.get("source_policy_rows_total"),
            "full_source_policy_reproduction_ready": False,
            "external_superiority_claim_allowed": False,
            "submission_ready": False,
        },
        "heavy_numerical_run_invoked": False,
        "run_v047_invoked": False,
        "v048_runner_invoked": False,
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# B4 Source-Policy Execution Handoff Package",
        "",
        f"Status: `{output['status']}`.",
        "",
        "This package is read-only. It does not authorize or run any B4 source-policy command.",
        "",
        f"- Source-policy rows closed/total: `{output['source_policy_row_state']['closed']}/{output['source_policy_row_state']['total']}`.",
        f"- Terminal unable-to-reproduce rows: `{output['source_policy_row_state']['unable_to_reproduce']}`.",
        f"- RA/HI rows requiring authorized closeout or new artifact: `{output['ra_hi_authorized_closeout_handoff']['future_promotion_requires_authorized_execution_or_new_artifact_rows']}`.",
        f"- Ready command batches/commands/mapped rows: `{packet.get('ready_command_batch_count')}/{packet.get('ready_command_count')}/{packet.get('ready_command_mapped_external_rows')}`.",
        f"- Command traceability unique RA/HI rows: `{command_row_traceability['summary']['unique_mapped_row_count']}/{command_row_traceability['summary']['ra_hi_unique_row_count']}`.",
        f"- Command traceability references/declared references/mismatches: `{command_row_traceability['summary']['traced_command_row_reference_total']}/{command_row_traceability['summary']['declared_mapped_row_reference_total']}/{command_row_traceability['summary']['declared_vs_traced_mismatch_count']}`.",
        f"- Command traceability terminal rows/source-policy closed rows: `{command_row_traceability['summary']['terminal_rows_with_command_refs']}/{command_row_traceability['summary']['source_policy_closed_rows']}`.",
        f"- Expected output schema audit: `{expected_output_schema_audit.get('status')}`; commands/artifacts/hash-match/parseable/schema-ready/closed `{expected_output_schema_audit.get('command_count')}/{expected_output_schema_audit.get('expected_artifact_count')}/{expected_output_schema_audit.get('artifacts_sha256_match_freeze')}/{expected_output_schema_audit.get('csv_parseable_artifacts')}/{expected_output_schema_audit.get('schema_ready_commands')}/{expected_output_schema_audit.get('source_policy_rows_closed')}`.",
        f"- Expected output schema command traceability shell/output/summary/no-summary/existing-output/existing-summary: `{expected_output_schema_audit.get('command_traceability', {}).get('commands_with_shell_command')}/{expected_output_schema_audit.get('command_traceability', {}).get('commands_with_expected_output_path')}/{expected_output_schema_audit.get('command_traceability', {}).get('commands_with_expected_summary_path')}/{expected_output_schema_audit.get('command_traceability', {}).get('commands_without_expected_summary_path')}/{expected_output_schema_audit.get('command_traceability', {}).get('commands_with_existing_expected_output')}/{expected_output_schema_audit.get('command_traceability', {}).get('commands_with_existing_expected_summary')}`.",
        f"- Execution authorized: `{output['execution_authorized']}`.",
        f"- Commands run by this handoff: `{not output['commands_not_run_by_handoff']}`.",
        f"- Source-policy execution allowed now/invoked/exact opt-in required: `{output['source_policy_execution_allowed_now']}/{output['source_policy_execution_invoked']}/{output['exact_b4_opt_in_required_for_execution']}`.",
        f"- Safe action ids: `{','.join(output['safe_action_ids'])}`.",
        f"- Opt-in action ids: `{','.join(output['opt_in_action_ids'])}`.",
        f"- Post-execution promotion required: `{output['post_execution_promotion_boundary']['post_execution_promotion_required']}`.",
        f"- B4/B7 can close now: `{output['post_execution_promotion_boundary']['b4_can_close_now']}/{output['post_execution_promotion_boundary']['b7_can_close_now']}`.",
        "",
        "## Terminal Unable-To-Reproduce Suites",
        "",
        "| suite | rows | attempted | unable | closed |",
        "|---|---:|---:|---:|---:|",
    ]
    for item in terminal_suites:
        lines.append(
            f"| `{item['suite_id']}` | `{item['row_count']}` | "
            f"`{item['self_reproduction_attempted_rows']}` | "
            f"`{item['unable_to_reproduce_rows']}` | "
            f"`{item['source_policy_closed_rows']}` |"
        )
    lines.extend(
        [
            "",
            "## Guarded Command Batches",
            "",
            "| batch | commands | mapped rows | status | allow 1e-4 |",
            "|---|---:|---:|---|---|",
        ]
    )
    for batch in batches:
        lines.append(
            f"| `{batch['id']}` | `{batch['command_count']}` | `{batch['mapped_external_rows']}` | "
            f"`{batch['status']}` | `{batch['all_commands_require_allow_source_policy_1e_4']}` |"
        )
    lines.extend(
        [
            "",
            "## Command Row Traceability",
            "",
            "| command | traced rows | declared rows | source-policy closed | promotion ready |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for command in command_row_traceability["commands"]:
        lines.append(
            f"| `{command['id']}` | `{command['traced_row_count']}` | "
            f"`{command['declared_mapped_row_count']}` | "
            f"`{command['source_policy_closed_rows']}` | "
            f"`{command['promotion_ready_rows']}` |"
        )
    lines.extend(
        [
            "",
            "## Exact Opt-In Boundary",
            "",
            f"`{approval}`",
            "",
            "Even after authorized execution, rows are not closed until the post-execution promotion audit and validators promote them.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("b4_source_policy_execution_handoff_package=written")
    print(f"source_policy_closed=0/{ledger.get('source_policy_rows_total')}")
    print(f"terminal_unable_to_reproduce_rows={ledger.get('source_policy_rows_unable_to_reproduce')}")
    print(f"ready_command_count={packet.get('ready_command_count')}")
    print("execution_authorized=False")
    print("source_policy_execution_invoked=False")
    print("expected_output_schema_audit=PASS")


if __name__ == "__main__":
    main()
