#!/usr/bin/env python3
"""Build a read-only audit for B4 expected-output promotion blockers.

The expected-output schema audit proves that the frozen B4 command outputs are
present, parseable, and hash-matched.  This companion audit proves the separate
negative fact: those outputs are still not promotion evidence because no
authorized B4 closeout has been recorded and no source-policy row has been
promoted.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "B4_EXPECTED_OUTPUT_PROMOTION_READINESS_BLOCKER_AUDIT_20260620.json"
OUT_MD = PAPER / "B4_EXPECTED_OUTPUT_PROMOTION_READINESS_BLOCKER_AUDIT_20260620.md"
SCHEMA = "b4-expected-output-promotion-readiness-blocker-audit-20260620-v1"
STATUS = "expected_outputs_schema_ready_but_promotion_blocked"
APPROVAL = (
    "I explicitly approve running the B4 source-policy execution commands listed in "
    "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json."
)
SOURCE_FILES = [
    "B4_SOURCE_POLICY_EXPECTED_OUTPUT_SCHEMA_AUDIT_20260620.json",
    "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.json",
    "B4_EXISTING_ARTIFACT_PROMOTION_AUDIT.json",
    "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json",
    "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json",
    "RA_HI_SOURCE_POLICY_PROMOTION_BLOCKER_MATRIX.json",
    "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json",
]
SAFE_ACTIONS_WITHOUT_B4_OPT_IN = [
    {
        "id": "rebuild_read_only_audit_chain",
        "description": "Rebuild this promotion blocker audit plus downstream objective, review, and package manifests.",
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


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return sha256_text(payload)


def int0(value: Any) -> int:
    if value is None:
        return 0
    return int(value)


def count_by(values: list[Any]) -> dict[str, int]:
    return dict(sorted(Counter(str(value) for value in values).items()))


def row_key_from_matrix_row(row: dict[str, Any]) -> str:
    return f"{row.get('suite_id')}|{row.get('method')}|{row.get('example')}"


def blocker_rows_for_command(
    command: dict[str, Any],
    ra_hi_by_key: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for key in command.get("row_keys", []):
        source_row = ra_hi_by_key.get(str(key), {})
        rows.append(
            {
                "row_key": str(key),
                "matrix_row_present": bool(source_row),
                "post_execution_decision": source_row.get("post_execution_decision"),
                "post_execution_attempt_status": source_row.get("post_execution_attempt_status"),
                "primary_promotion_blocker": source_row.get("primary_promotion_blocker"),
                "all_command_outputs_present": source_row.get("all_command_outputs_present"),
                "source_policy_closed": source_row.get("source_policy_closed"),
                "source_policy_reproduction_complete": source_row.get(
                    "source_policy_reproduction_complete"
                ),
                "ready_to_launch_after_explicit_opt_in": source_row.get(
                    "ready_to_launch_after_explicit_opt_in"
                ),
                "future_promotion_requires_authorized_execution_or_new_artifact": source_row.get(
                    "future_promotion_requires_authorized_execution_or_new_artifact"
                ),
            }
        )
    return rows


def command_record(
    command: dict[str, Any],
    ra_hi_by_key: dict[str, dict[str, Any]],
    authorized_execution_recorded: bool,
) -> dict[str, Any]:
    output_schema = command.get("expected_output_schema", {})
    summary_schema = command.get("expected_summary_schema", {})
    row_blockers = blocker_rows_for_command(command, ra_hi_by_key)
    row_decisions = [row.get("post_execution_decision") for row in row_blockers]
    primary_blockers = [row.get("primary_promotion_blocker") for row in row_blockers]
    summary_closed_rows = int0(summary_schema.get("source_policy_rows_closed_by_this_evidence"))
    summary_promoted_rows = int0(summary_schema.get("source_policy_reproduction_rows_promoted"))
    summary_promotion_ready = summary_schema.get("promotion_ready") is True
    promotion_ready = (
        command.get("schema_ready") is True
        and authorized_execution_recorded
        and summary_promotion_ready
        and summary_closed_rows > 0
        and summary_promoted_rows > 0
        and all(decision != "not_promoted" for decision in row_decisions)
    )
    return {
        "id": command.get("id"),
        "suite_id": command.get("suite_id"),
        "batch_id": command.get("batch_id"),
        "artifact_status": command.get("artifact_status"),
        "schema_ready": command.get("schema_ready"),
        "schema_status": command.get("schema_status"),
        "expected_output_path": output_schema.get("path"),
        "expected_summary_path": summary_schema.get("path"),
        "csv_row_count": output_schema.get("row_count"),
        "csv_column_count": output_schema.get("column_count"),
        "csv_status_counts": output_schema.get("status_counts"),
        "summary_status": summary_schema.get("status"),
        "summary_promotion_ready": summary_promotion_ready,
        "summary_source_policy_rows_closed": summary_closed_rows,
        "summary_source_policy_rows_promoted": summary_promoted_rows,
        "mapped_row_count_declared": command.get("mapped_row_count_declared"),
        "mapped_row_count_traced": command.get("mapped_row_count_traced"),
        "mapped_row_key_count": len(command.get("row_keys", [])),
        "matched_ra_hi_matrix_rows": sum(1 for row in row_blockers if row["matrix_row_present"]),
        "matched_rows_not_promoted": sum(
            1 for row in row_blockers if row.get("post_execution_decision") == "not_promoted"
        ),
        "matched_rows_source_policy_closed": sum(
            1 for row in row_blockers if row.get("source_policy_closed") is True
        ),
        "matched_rows_reproduction_complete": sum(
            1
            for row in row_blockers
            if row.get("source_policy_reproduction_complete") is True
        ),
        "matched_rows_output_present": sum(
            1 for row in row_blockers if row.get("all_command_outputs_present") is True
        ),
        "matched_rows_future_authorization_or_new_artifact": sum(
            1
            for row in row_blockers
            if row.get("future_promotion_requires_authorized_execution_or_new_artifact")
            is True
        ),
        "primary_promotion_blocker_counts": count_by(primary_blockers),
        "promotion_ready": promotion_ready,
        "promotion_status": (
            "promotion_ready" if promotion_ready else "schema_ready_promotion_blocked"
        ),
        "blocking_flags": {
            "schema_ready_is_not_promotion_ready": command.get("schema_ready") is True
            and not promotion_ready,
            "verified_authorized_execution_recorded": authorized_execution_recorded,
            "commands_executed_by_schema_audit": command.get("commands_executed_by_audit"),
            "summary_rows_promoted": summary_promoted_rows,
            "summary_rows_closed": summary_closed_rows,
            "all_mapped_rows_promoted": all(
                decision != "not_promoted" for decision in row_decisions
            ),
        },
        "row_blockers": row_blockers,
    }


def build_payload() -> dict[str, Any]:
    schema_audit = read_json(PAPER / "B4_SOURCE_POLICY_EXPECTED_OUTPUT_SCHEMA_AUDIT_20260620.json")
    post_execution = read_json(PAPER / "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.json")
    existing_promotion = read_json(PAPER / "B4_EXISTING_ARTIFACT_PROMOTION_AUDIT.json")
    opt_in = read_json(PAPER / "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json")
    handoff = read_json(PAPER / "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json")
    ra_hi = read_json(PAPER / "RA_HI_SOURCE_POLICY_PROMOTION_BLOCKER_MATRIX.json")
    archive_gap = read_json(PAPER / "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json")

    ra_hi_rows = [row for row in ra_hi.get("rows", []) if isinstance(row, dict)]
    ra_hi_by_key = {row_key_from_matrix_row(row): row for row in ra_hi_rows}
    authorized_execution_recorded = (
        post_execution.get("verified_authorized_execution_recorded") is True
        or handoff.get("execution_authorized") is True
        or opt_in.get("execution_invoked_by_packet") is True
    )
    commands = [
        command_record(command, ra_hi_by_key, authorized_execution_recorded)
        for command in schema_audit.get("commands", [])
        if isinstance(command, dict)
    ]
    unique_mapped_rows = sorted(
        {
            row.get("row_key")
            for command in commands
            for row in command.get("row_blockers", [])
            if row.get("matrix_row_present")
        }
    )
    promotion_blocker_matrix = {
        "schema_ready_commands": schema_audit.get("schema_ready_commands"),
        "schema_ready_expected_artifacts": schema_audit.get("expected_artifact_count"),
        "schema_ready_csv_rows": schema_audit.get("total_csv_data_rows"),
        "verified_authorized_execution_recorded": authorized_execution_recorded,
        "post_execution_promoted_rows": post_execution.get(
            "post_execution_summary", {}
        ).get("source_policy_rows_promoted_after_driver"),
        "post_execution_rows_still_requiring_execution_or_promotion": post_execution.get(
            "post_execution_summary", {}
        ).get("source_policy_rows_still_requiring_execution_or_promotion"),
        "existing_artifacts_promotion_ready_without_new_execution": existing_promotion.get(
            "promotion_ready_without_new_execution_count"
        ),
        "ra_hi_rows_not_promoted": ra_hi.get("source_policy_rows_not_promoted"),
        "ra_hi_rows_with_all_command_outputs_present": ra_hi.get(
            "rows_with_all_command_outputs_present"
        ),
        "full_archive_ready_now": archive_gap.get("full_archive_ready_now"),
        "source_policy_closed_ratio": archive_gap.get("source_policy_closed_ratio"),
        "blocking_ids": ["OC4", "OC12"],
    }
    digest_inputs = {
        "commands": [
            {
                "id": command.get("id"),
                "schema_ready": command.get("schema_ready"),
                "csv_row_count": command.get("csv_row_count"),
                "summary_status": command.get("summary_status"),
                "summary_source_policy_rows_closed": command.get(
                    "summary_source_policy_rows_closed"
                ),
                "summary_source_policy_rows_promoted": command.get(
                    "summary_source_policy_rows_promoted"
                ),
                "matched_rows_not_promoted": command.get("matched_rows_not_promoted"),
                "promotion_ready": command.get("promotion_ready"),
                "promotion_status": command.get("promotion_status"),
                "primary_promotion_blocker_counts": command.get(
                    "primary_promotion_blocker_counts"
                ),
            }
            for command in commands
        ],
        "promotion_blocker_matrix": promotion_blocker_matrix,
    }
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "date_checked": "2026-06-20",
        "read_only": True,
        "execution_authorized": authorized_execution_recorded,
        "commands_executed_by_audit": False,
        "source_policy_execution_invoked": False,
        "source_policy_execution_allowed_now": False,
        "exact_b4_opt_in_required_for_execution": True,
        "safe_action_ids": SAFE_ACTION_IDS,
        "opt_in_action_ids": OPT_IN_ACTION_IDS,
        "next_safe_actions": SAFE_ACTIONS_WITHOUT_B4_OPT_IN,
        "next_safe_action_ids": SAFE_ACTION_IDS,
        "builder_invoked_heavy_numerical_run": False,
        "run_v047_invoked": False,
        "v048_runner_invoked": False,
        "required_user_approval_statement": APPROVAL,
        "guarded_execution_driver": opt_in.get("guarded_execution_driver", {}).get("path"),
        "source_policy_rows_total": schema_audit.get("source_policy_rows_total"),
        "source_policy_rows_closed": 0,
        "source_policy_rows_promoted": 0,
        "promotion_ready_rows": 0,
        "submission_ready": False,
        "b4_can_close_now": False,
        "b7_can_close_now": False,
        "schema_audit_summary": {
            "status": schema_audit.get("status"),
            "command_count": schema_audit.get("command_count"),
            "schema_ready_commands": schema_audit.get("schema_ready_commands"),
            "expected_artifact_count": schema_audit.get("expected_artifact_count"),
            "artifacts_sha256_match_freeze": schema_audit.get(
                "artifacts_sha256_match_freeze"
            ),
            "csv_parseable_artifacts": schema_audit.get("csv_parseable_artifacts"),
            "json_summary_parseable_artifacts": schema_audit.get(
                "json_summary_parseable_artifacts"
            ),
            "total_csv_data_rows": schema_audit.get("total_csv_data_rows"),
            "source_policy_rows_closed": schema_audit.get("source_policy_rows_closed"),
            "promotion_ready_rows": schema_audit.get("promotion_ready_rows"),
            "commands_executed_by_audit": schema_audit.get("commands_executed_by_audit"),
            "source_policy_execution_invoked": schema_audit.get(
                "source_policy_execution_invoked"
            ),
            "source_policy_execution_allowed_now": schema_audit.get(
                "source_policy_execution_allowed_now"
            ),
            "exact_b4_opt_in_required_for_execution": schema_audit.get(
                "exact_b4_opt_in_required_for_execution"
            ),
            "safe_action_ids": schema_audit.get("safe_action_ids"),
            "opt_in_action_ids": schema_audit.get("opt_in_action_ids"),
            "expected_output_schema_audit_sha256": schema_audit.get(
                "expected_output_schema_audit_sha256"
            ),
        },
        "post_execution_summary": {
            "status": post_execution.get("status"),
            "verified_authorized_execution_recorded": post_execution.get(
                "verified_authorized_execution_recorded"
            ),
            "approved_driver_execution_recorded": post_execution.get(
                "approved_driver_execution_recorded"
            ),
            "source_policy_rows_closed": post_execution.get("source_policy_rows_closed"),
            "source_policy_rows_open": post_execution.get("source_policy_rows_open"),
            "source_policy_rows_still_requiring_execution_or_promotion": post_execution.get(
                "source_policy_rows_still_requiring_execution_or_promotion"
            ),
            "b4_can_close_now": post_execution.get("b4_can_close_now"),
            "b7_can_close_now": post_execution.get("b7_can_close_now"),
        },
        "existing_artifact_promotion_summary": {
            "status": existing_promotion.get("status"),
            "candidate_item_count": existing_promotion.get("candidate_item_count"),
            "promotion_ready_without_new_execution_count": existing_promotion.get(
                "promotion_ready_without_new_execution_count"
            ),
            "source_policy_rows_closed_by_existing_artifacts": existing_promotion.get(
                "source_policy_rows_closed_by_existing_artifacts"
            ),
            "b4_can_close_now": existing_promotion.get("b4_can_close_now"),
            "b7_can_close_now": existing_promotion.get("b7_can_close_now"),
        },
        "ra_hi_promotion_matrix_summary": {
            "status": ra_hi.get("status"),
            "row_count": ra_hi.get("row_count"),
            "ra2021_row_count": ra_hi.get("ra2021_row_count"),
            "hi2022_row_count": ra_hi.get("hi2022_row_count"),
            "rows_with_all_command_outputs_present": ra_hi.get(
                "rows_with_all_command_outputs_present"
            ),
            "source_policy_rows_closed": ra_hi.get("source_policy_rows_closed"),
            "source_policy_rows_not_promoted": ra_hi.get("source_policy_rows_not_promoted"),
            "future_promotion_requires_authorized_execution_or_new_artifact_rows": ra_hi.get(
                "future_promotion_requires_authorized_execution_or_new_artifact_rows"
            ),
            "primary_promotion_blocker_counts": ra_hi.get(
                "primary_promotion_blocker_counts"
            ),
            "post_execution_attempt_status_counts": ra_hi.get(
                "post_execution_attempt_status_counts"
            ),
        },
        "archive_gap_summary": {
            "status": archive_gap.get("status"),
            "source_policy_closed_ratio": archive_gap.get("source_policy_closed_ratio"),
            "source_policy_execution_allowed_now": archive_gap.get(
                "source_policy_execution_allowed_now"
            ),
            "source_policy_execution_invoked": archive_gap.get("source_policy_execution_invoked"),
            "exact_b4_opt_in_required_for_execution": archive_gap.get(
                "exact_b4_opt_in_required_for_execution"
            ),
            "safe_action_ids": archive_gap.get("safe_action_ids"),
            "opt_in_action_ids": archive_gap.get("opt_in_action_ids"),
            "terminal_unable_to_reproduce_rows": archive_gap.get(
                "terminal_unable_to_reproduce_rows"
            ),
            "ra_hi_rows_requiring_authorized_closeout_or_new_artifact": archive_gap.get(
                "ra_hi_rows_requiring_authorized_closeout_or_new_artifact"
            ),
            "full_archive_ready_now": archive_gap.get("full_archive_ready_now"),
            "submission_ready": archive_gap.get("submission_ready"),
        },
        "promotion_blocker_matrix": promotion_blocker_matrix,
        "command_count": len(commands),
        "schema_ready_command_count": sum(1 for command in commands if command.get("schema_ready") is True),
        "promotion_ready_command_count": sum(1 for command in commands if command.get("promotion_ready") is True),
        "command_row_reference_total": sum(
            int(command.get("mapped_row_key_count") or 0) for command in commands
        ),
        "unique_mapped_ra_hi_row_count": len(unique_mapped_rows),
        "unique_mapped_ra_hi_rows_not_promoted": ra_hi.get("source_policy_rows_not_promoted"),
        "summary_source_policy_rows_closed_total": sum(
            int(command.get("summary_source_policy_rows_closed") or 0)
            for command in commands
        ),
        "summary_source_policy_rows_promoted_total": sum(
            int(command.get("summary_source_policy_rows_promoted") or 0)
            for command in commands
        ),
        "commands_with_schema_ready_but_promotion_blocked": sum(
            1
            for command in commands
            if command.get("schema_ready") is True
            and command.get("promotion_status") == "schema_ready_promotion_blocked"
        ),
        "unique_mapped_ra_hi_rows": unique_mapped_rows,
        "commands": commands,
        "promotion_readiness_digest": canonical_digest(digest_inputs),
        "source_files": SOURCE_FILES,
    }


def write_markdown(payload: dict[str, Any]) -> None:
    lines = [
        "# B4 Expected-Output Promotion-Readiness Blocker Audit 20260620",
        "",
        f"Status: `{payload['status']}`.",
        "",
        "This is a read-only promotion-readiness audit. It consumes existing expected-output, post-execution, and RA/HI blocker artifacts; it does not authorize or run B4 source-policy commands.",
        "",
        f"- Schema-ready commands / promotion-ready commands: `{payload['schema_ready_command_count']}/{payload['promotion_ready_command_count']}`.",
        f"- Expected artifacts / CSV rows: `{payload['schema_audit_summary']['expected_artifact_count']}/{payload['schema_audit_summary']['total_csv_data_rows']}`.",
        f"- Parseable CSV/JSON summaries: `{payload['schema_audit_summary']['csv_parseable_artifacts']}/{payload['schema_audit_summary']['json_summary_parseable_artifacts']}`.",
        f"- Command row references / unique RA/HI rows: `{payload['command_row_reference_total']}/{payload['unique_mapped_ra_hi_row_count']}`.",
        f"- Unique mapped RA/HI rows not promoted: `{payload['unique_mapped_ra_hi_rows_not_promoted']}`.",
        f"- Summary rows closed/promoted: `{payload['summary_source_policy_rows_closed_total']}/{payload['summary_source_policy_rows_promoted_total']}`.",
        f"- Commands with schema-ready outputs but blocked promotion: `{payload['commands_with_schema_ready_but_promotion_blocked']}`.",
        f"- Verified authorized execution recorded: `{payload['post_execution_summary']['verified_authorized_execution_recorded']}`.",
        f"- Source-policy rows closed/promoted/promotion-ready: `{payload['source_policy_rows_closed']}/{payload['source_policy_rows_promoted']}/{payload['promotion_ready_rows']}`.",
        f"- Source-policy execution allowed now/invoked/exact opt-in required: `{payload['source_policy_execution_allowed_now']}/{payload['source_policy_execution_invoked']}/{payload['exact_b4_opt_in_required_for_execution']}`.",
        f"- Required approval/driver: `{payload['required_user_approval_statement']}/{payload['guarded_execution_driver']}`.",
        f"- Safe action ids: `{','.join(payload['safe_action_ids'])}`.",
        f"- Opt-in action ids: `{','.join(payload['opt_in_action_ids'])}`.",
        f"- B4/B7 can close now: `{payload['b4_can_close_now']}/{payload['b7_can_close_now']}`.",
        f"- Submission ready: `{payload['submission_ready']}`.",
        "",
        "## Objective Blocker Matrix",
        "",
        "This audit records OC4 expected-output promotion readiness. It does not close the global objective blockers.",
        "",
        "- `blocker_open_by_id=OC4:True,OC6:True,OC12:True`",
        "- `blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready`",
        "- `blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False`",
        "",
        "## Promotion Blocker Matrix",
        "",
        "| check | value |",
        "|---|---:|",
    ]
    for key, value in payload["promotion_blocker_matrix"].items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(
        [
            "",
            "## Commands",
            "",
            "| command | schema | CSV rows | matched rows | blocked rows | summary closed/promoted | promotion status |",
            "|---|---|---:|---:|---:|---:|---|",
        ]
    )
    for command in payload["commands"]:
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}/{}` | `{}` |".format(
                command["id"],
                command["schema_status"],
                command["csv_row_count"],
                command["matched_ra_hi_matrix_rows"],
                command["matched_rows_not_promoted"],
                command["summary_source_policy_rows_closed"],
                command["summary_source_policy_rows_promoted"],
                command["promotion_status"],
            )
        )
    lines.extend(
        [
            "",
            "Reading rule: schema-ready expected outputs are only structure/fingerprint evidence. They remain blocked from B4/B7 promotion until authorized execution and post-execution promotion evidence close source-policy rows.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    payload = build_payload()
    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    write_markdown(payload)
    print(
        "wrote "
        f"{OUT_JSON.name} and {OUT_MD.name}: "
        f"schema_ready={payload['schema_ready_command_count']}/"
        f"{payload['command_count']} "
        f"promotion_ready={payload['promotion_ready_command_count']} "
        f"unique_rows={payload['unique_mapped_ra_hi_row_count']} "
        f"source_policy_rows_closed={payload['source_policy_rows_closed']}"
    )


if __name__ == "__main__":
    main()
