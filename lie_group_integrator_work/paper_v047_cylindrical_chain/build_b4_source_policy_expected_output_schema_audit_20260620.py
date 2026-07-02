#!/usr/bin/env python3
"""Audit the expected B4 source-policy outputs without executing commands.

The command preflight freeze records the artifacts that would be consumed after
an authorized B4 closeout.  This audit only checks the already-existing expected
CSV and JSON output files for parseability, stable size/hash, and basic schema
shape.  It does not run B4 commands and does not promote source-policy rows.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "B4_SOURCE_POLICY_EXPECTED_OUTPUT_SCHEMA_AUDIT_20260620.json"
OUT_MD = PAPER / "B4_SOURCE_POLICY_EXPECTED_OUTPUT_SCHEMA_AUDIT_20260620.md"
FREEZE_PATH = PAPER / "B4_SOURCE_POLICY_COMMAND_PREFLIGHT_FREEZE_20260620.json"
SCHEMA = "b4-source-policy-expected-output-schema-audit-20260620-v1"
STATUS = "expected_outputs_schema_ready_not_authorized_not_run_not_promoted"
FREEZE_STATUS = "command_preflight_frozen_not_authorized_not_run_not_promoted"
APPROVAL = (
    "I explicitly approve running the B4 source-policy execution commands listed in "
    "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json."
)
SAFE_ACTIONS_WITHOUT_B4_OPT_IN = [
    {
        "id": "rebuild_read_only_audit_chain",
        "description": "Rebuild this schema audit plus downstream promotion, objective, review, and package manifests.",
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


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def canonical_digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return sha256_text(payload)


def package_path(path_label: str | None) -> Path | None:
    if not path_label:
        return None
    return (PAPER / path_label).resolve()


def artifact_state(path_label: str | None, frozen: dict[str, Any] | None) -> dict[str, Any]:
    path = package_path(path_label)
    exists = path is not None and path.exists() and path.is_file()
    size_bytes = path.stat().st_size if exists and path is not None else None
    current_sha256 = sha256_file(path) if exists and path is not None else None
    frozen = frozen or {}
    return {
        "path": path_label,
        "exists": exists,
        "size_bytes": size_bytes,
        "sha256": current_sha256,
        "frozen_size_bytes": frozen.get("size_bytes"),
        "frozen_sha256": frozen.get("sha256"),
        "size_matches_freeze": size_bytes == frozen.get("size_bytes"),
        "sha256_matches_freeze": current_sha256 == frozen.get("sha256"),
        "nonempty": bool(exists and int(size_bytes or 0) > 0),
    }


def compact_counts(values: list[Any]) -> dict[str, int]:
    return dict(sorted(Counter(str(value) for value in values).items()))


def compact_unique(rows: list[dict[str, str]], key: str) -> list[str]:
    values = sorted({row.get(key, "") for row in rows if row.get(key, "") != ""})
    return values[:20]


def inspect_csv(path_label: str | None, frozen: dict[str, Any] | None) -> dict[str, Any]:
    state = artifact_state(path_label, frozen)
    result: dict[str, Any] = {
        **state,
        "artifact_type": "csv",
        "parseable": False,
        "parse_error": None,
        "header": [],
        "column_count": 0,
        "row_count": 0,
        "status_counts": {},
        "policy_counts": {},
        "model_values": [],
        "form_values": [],
        "method_values": [],
        "h_values": [],
        "schema_signature": None,
    }
    path = package_path(path_label)
    if not state["exists"] or path is None:
        result["parse_error"] = "missing"
        return result
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            header = list(reader.fieldnames or [])
            rows = [dict(row) for row in reader]
    except Exception as exc:  # noqa: BLE001
        result["parse_error"] = f"{type(exc).__name__}:{exc}"
        return result

    result.update(
        {
            "parseable": True,
            "header": header,
            "column_count": len(header),
            "row_count": len(rows),
            "status_counts": compact_counts([row.get("status", "") for row in rows]),
            "policy_counts": compact_counts([row.get("policy", "") for row in rows]),
            "model_values": compact_unique(rows, "model"),
            "form_values": compact_unique(rows, "form"),
            "method_values": compact_unique(rows, "method"),
            "h_values": compact_unique(rows, "h"),
            "schema_signature": canonical_digest(
                {
                    "header": header,
                    "row_count": len(rows),
                    "status_counts": compact_counts([row.get("status", "") for row in rows]),
                    "policy_counts": compact_counts([row.get("policy", "") for row in rows]),
                }
            ),
        }
    )
    return result


def inspect_json_summary(path_label: str | None, frozen: dict[str, Any] | None) -> dict[str, Any]:
    state = artifact_state(path_label, frozen)
    result: dict[str, Any] = {
        **state,
        "artifact_type": "json_summary",
        "parseable": None if path_label is None else False,
        "parse_error": None,
        "keys": [],
        "schema": None,
        "status": None,
        "row_count": None,
        "ok_row_count": None,
        "source_policy_rows_closed_by_this_evidence": None,
        "source_policy_reproduction_rows_promoted": None,
        "promotion_ready": None,
        "heavy_numerical_run_invoked": None,
        "canonical_v048_main_invoked": None,
        "schema_signature": None,
    }
    if path_label is None:
        return result
    path = package_path(path_label)
    if not state["exists"] or path is None:
        result["parse_error"] = "missing"
        return result
    try:
        payload = read_json(path)
    except Exception as exc:  # noqa: BLE001
        result["parse_error"] = f"{type(exc).__name__}:{exc}"
        return result

    keys = sorted(payload.keys())
    result.update(
        {
            "parseable": True,
            "keys": keys,
            "schema": payload.get("schema"),
            "status": payload.get("status"),
            "row_count": payload.get("row_count"),
            "ok_row_count": payload.get("ok_row_count"),
            "source_policy_rows_closed_by_this_evidence": payload.get(
                "source_policy_rows_closed_by_this_evidence"
            ),
            "source_policy_reproduction_rows_promoted": payload.get(
                "source_policy_reproduction_rows_promoted"
            ),
            "promotion_ready": payload.get("promotion_ready"),
            "heavy_numerical_run_invoked": payload.get("heavy_numerical_run_invoked"),
            "canonical_v048_main_invoked": payload.get("canonical_v048_main_invoked"),
            "schema_signature": canonical_digest(
                {
                    "keys": keys,
                    "schema": payload.get("schema"),
                    "status": payload.get("status"),
                    "row_count": payload.get("row_count"),
                    "ok_row_count": payload.get("ok_row_count"),
                    "source_policy_rows_closed_by_this_evidence": payload.get(
                        "source_policy_rows_closed_by_this_evidence"
                    ),
                    "source_policy_reproduction_rows_promoted": payload.get(
                        "source_policy_reproduction_rows_promoted"
                    ),
                    "promotion_ready": payload.get("promotion_ready"),
                }
            ),
        }
    )
    return result


def command_schema_record(command: dict[str, Any]) -> dict[str, Any]:
    output_schema = inspect_csv(
        command.get("expected_output", {}).get("path"),
        command.get("expected_output"),
    )
    summary_schema = inspect_json_summary(
        command.get("expected_summary", {}).get("path"),
        command.get("expected_summary"),
    )
    summary_required = summary_schema.get("path") is not None
    summary_ready = (
        summary_schema.get("parseable") is True
        and summary_schema.get("size_matches_freeze") is True
        and summary_schema.get("sha256_matches_freeze") is True
    )
    if not summary_required:
        summary_ready = True
    schema_ready = (
        output_schema.get("parseable") is True
        and output_schema.get("row_count", 0) > 0
        and output_schema.get("column_count", 0) > 0
        and output_schema.get("size_matches_freeze") is True
        and output_schema.get("sha256_matches_freeze") is True
        and summary_ready
    )
    return {
        "id": command.get("id"),
        "batch_id": command.get("batch_id"),
        "suite_id": command.get("suite_id"),
        "command": command.get("command"),
        "artifact_status": command.get("artifact_status"),
        "mapped_row_count_declared": command.get("mapped_row_count_declared"),
        "mapped_row_count_traced": command.get("mapped_row_count_traced"),
        "row_keys": command.get("row_keys", []),
        "expected_output_after_run": command.get("expected_output", {}).get("path"),
        "expected_output_exists_now": output_schema.get("exists"),
        "expected_summary_after_run": command.get("expected_summary", {}).get("path"),
        "expected_summary_exists_now": summary_schema.get("exists"),
        "expected_output_schema": output_schema,
        "expected_summary_schema": summary_schema,
        "schema_status": "schema_ready" if schema_ready else "schema_blocked",
        "schema_ready": schema_ready,
        "source_policy_rows_closed_by_audit": 0,
        "promotion_ready_rows_by_audit": 0,
        "commands_executed_by_audit": False,
    }


def build_payload() -> dict[str, Any]:
    freeze = read_json(FREEZE_PATH)
    commands = [
        command_schema_record(command)
        for command in freeze.get("commands", [])
        if isinstance(command, dict)
    ]
    output_artifacts = [command["expected_output_schema"] for command in commands]
    summary_artifacts = [
        command["expected_summary_schema"]
        for command in commands
        if command["expected_summary_schema"].get("path") is not None
    ]
    all_artifacts = output_artifacts + summary_artifacts
    digest_inputs = [
        {
            "id": command["id"],
            "command": command.get("command"),
            "expected_output_after_run": command.get("expected_output_after_run"),
            "expected_summary_after_run": command.get("expected_summary_after_run"),
            "output": {
                "path": command["expected_output_schema"].get("path"),
                "size_bytes": command["expected_output_schema"].get("size_bytes"),
                "sha256": command["expected_output_schema"].get("sha256"),
                "schema_signature": command["expected_output_schema"].get(
                    "schema_signature"
                ),
            },
            "summary": {
                "path": command["expected_summary_schema"].get("path"),
                "size_bytes": command["expected_summary_schema"].get("size_bytes"),
                "sha256": command["expected_summary_schema"].get("sha256"),
                "schema_signature": command["expected_summary_schema"].get(
                    "schema_signature"
                ),
            },
            "schema_status": command["schema_status"],
        }
        for command in commands
    ]
    command_traceability = {
        "commands_with_shell_command": sum(1 for command in commands if command.get("command")),
        "commands_with_expected_output_path": sum(
            1 for command in commands if command.get("expected_output_after_run")
        ),
        "commands_with_expected_summary_path": sum(
            1 for command in commands if command.get("expected_summary_after_run")
        ),
        "commands_without_expected_summary_path": sum(
            1 for command in commands if not command.get("expected_summary_after_run")
        ),
        "commands_with_existing_expected_output": sum(
            1 for command in commands if command.get("expected_output_exists_now") is True
        ),
        "commands_with_existing_expected_summary": sum(
            1 for command in commands if command.get("expected_summary_exists_now") is True
        ),
        "source_policy_execution_invoked": False,
        "commands_executed_by_audit": False,
    }
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "date_checked": "2026-06-20",
        "read_only": True,
        "execution_authorized": False,
        "commands_executed_by_audit": False,
        "source_policy_execution_invoked": False,
        "source_policy_execution_allowed_now": False,
        "exact_b4_opt_in_required_for_execution": True,
        "safe_action_ids": SAFE_ACTION_IDS,
        "opt_in_action_ids": OPT_IN_ACTION_IDS,
        "next_safe_actions": SAFE_ACTIONS_WITHOUT_B4_OPT_IN,
        "next_safe_action_ids": SAFE_ACTION_IDS,
        "builder_invoked_heavy_numerical_run": False,
        "source_policy_rows_closed": 0,
        "source_policy_rows_total": freeze.get("source_policy_rows_total"),
        "promotion_ready_rows": 0,
        "submission_ready": False,
        "required_user_approval_statement": APPROVAL,
        "guarded_execution_driver": freeze.get("guarded_execution_driver", freeze.get("driver")),
        "input_freeze": {
            "path": "B4_SOURCE_POLICY_COMMAND_PREFLIGHT_FREEZE_20260620.json",
            "schema": freeze.get("schema"),
            "status": freeze.get("status"),
            "ready_command_count": freeze.get("ready_command_count"),
            "unique_mapped_ra_hi_rows": freeze.get("unique_mapped_ra_hi_rows"),
            "declared_row_reference_total": freeze.get("declared_row_reference_total"),
            "traced_row_reference_total": freeze.get("traced_row_reference_total"),
            "expected_artifact_count": freeze.get("expected_artifact_count"),
            "commands_executed_by_freeze": freeze.get("commands_executed_by_freeze"),
            "execution_authorized": freeze.get("execution_authorized"),
            "source_policy_execution_invoked": freeze.get("source_policy_execution_invoked"),
            "source_policy_execution_allowed_now": freeze.get("source_policy_execution_allowed_now"),
            "exact_b4_opt_in_required_for_execution": freeze.get(
                "exact_b4_opt_in_required_for_execution"
            ),
            "safe_action_ids": freeze.get("safe_action_ids"),
            "opt_in_action_ids": freeze.get("opt_in_action_ids"),
            "source_policy_rows_closed": freeze.get("source_policy_rows_closed"),
            "submission_ready": freeze.get("submission_ready"),
        },
        "command_count": len(commands),
        "expected_csv_artifact_count": len(output_artifacts),
        "expected_json_summary_artifact_count": len(summary_artifacts),
        "expected_artifact_count": len(all_artifacts),
        "artifacts_existing_now": sum(1 for artifact in all_artifacts if artifact.get("exists") is True),
        "artifacts_nonempty_now": sum(1 for artifact in all_artifacts if artifact.get("nonempty") is True),
        "artifacts_size_match_freeze": sum(
            1 for artifact in all_artifacts if artifact.get("size_matches_freeze") is True
        ),
        "artifacts_sha256_match_freeze": sum(
            1 for artifact in all_artifacts if artifact.get("sha256_matches_freeze") is True
        ),
        "csv_parseable_artifacts": sum(
            1 for artifact in output_artifacts if artifact.get("parseable") is True
        ),
        "json_summary_parseable_artifacts": sum(
            1 for artifact in summary_artifacts if artifact.get("parseable") is True
        ),
        "schema_ready_commands": sum(1 for command in commands if command.get("schema_ready") is True),
        "total_csv_data_rows": sum(
            int(command["expected_output_schema"].get("row_count") or 0)
            for command in commands
        ),
        "summary_status_counts": compact_counts(
            [
                command["expected_summary_schema"].get("status")
                for command in commands
                if command["expected_summary_schema"].get("status") is not None
            ]
        ),
        "csv_status_counts": compact_counts(
            [
                status
                for command in commands
                for status in command["expected_output_schema"].get("status_counts", {}).keys()
            ]
        ),
        "command_traceability": command_traceability,
        "commands": commands,
        "expected_output_schema_audit_sha256": canonical_digest(digest_inputs),
        "source_files": [
            "B4_SOURCE_POLICY_COMMAND_PREFLIGHT_FREEZE_20260620.json",
        ],
    }
    return payload


def write_markdown(payload: dict[str, Any]) -> None:
    lines = [
        "# B4 Source-Policy Expected Output Schema Audit 20260620",
        "",
        f"Status: `{payload['status']}`.",
        "",
        "This is a read-only schema audit of expected B4 output artifacts. It does not authorize or run B4 source-policy commands, and it closes zero source-policy rows.",
        "",
        f"- Commands/CSV summaries/JSON summaries/artifacts: `{payload['command_count']}/{payload['expected_csv_artifact_count']}/{payload['expected_json_summary_artifact_count']}/{payload['expected_artifact_count']}`.",
        f"- Artifacts existing/nonempty/size-match/hash-match: `{payload['artifacts_existing_now']}/{payload['artifacts_nonempty_now']}/{payload['artifacts_size_match_freeze']}/{payload['artifacts_sha256_match_freeze']}`.",
        f"- Parseable CSV/JSON summary artifacts: `{payload['csv_parseable_artifacts']}/{payload['json_summary_parseable_artifacts']}`.",
        f"- Schema-ready commands: `{payload['schema_ready_commands']}/{payload['command_count']}`.",
        f"- Command traceability shell/output/summary/no-summary/existing-output/existing-summary: `{payload['command_traceability']['commands_with_shell_command']}/{payload['command_traceability']['commands_with_expected_output_path']}/{payload['command_traceability']['commands_with_expected_summary_path']}/{payload['command_traceability']['commands_without_expected_summary_path']}/{payload['command_traceability']['commands_with_existing_expected_output']}/{payload['command_traceability']['commands_with_existing_expected_summary']}`.",
        f"- Total CSV data rows: `{payload['total_csv_data_rows']}`.",
        f"- Commands executed / source-policy rows closed / promotion-ready rows: `{payload['commands_executed_by_audit']}/{payload['source_policy_rows_closed']}/{payload['promotion_ready_rows']}`.",
        f"- Source-policy execution allowed now/invoked/exact opt-in required: `{payload['source_policy_execution_allowed_now']}/{payload['source_policy_execution_invoked']}/{payload['exact_b4_opt_in_required_for_execution']}`.",
        f"- Required approval/driver: `{payload['required_user_approval_statement']}/{payload['guarded_execution_driver']}`.",
        f"- Safe action ids: `{','.join(payload['safe_action_ids'])}`.",
        f"- Opt-in action ids: `{','.join(payload['opt_in_action_ids'])}`.",
        f"- Submission ready: `{payload['submission_ready']}`.",
        "",
        "| Command | Expected CSV | Expected summary | CSV rows | CSV columns | CSV status counts | Summary status | Schema status |",
        "| --- | --- | --- | ---: | ---: | --- | --- | --- |",
    ]
    for command in payload["commands"]:
        csv_schema = command["expected_output_schema"]
        summary_schema = command["expected_summary_schema"]
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                command["id"],
                command.get("expected_output_after_run"),
                command.get("expected_summary_after_run") or "none",
                csv_schema.get("row_count"),
                csv_schema.get("column_count"),
                json.dumps(csv_schema.get("status_counts", {}), sort_keys=True),
                summary_schema.get("status") or "none",
                command["schema_status"],
            )
        )
    lines.extend(
        [
            "",
            "The schema-ready status is a structure and fingerprint check only; post-execution promotion evidence is still required before any B4 source-policy row can close.",
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
        f"schema_ready_commands={payload['schema_ready_commands']}/"
        f"{payload['command_count']} "
        f"artifacts={payload['artifacts_existing_now']}/"
        f"{payload['expected_artifact_count']} "
        f"source_policy_rows_closed={payload['source_policy_rows_closed']}"
    )


if __name__ == "__main__":
    main()
