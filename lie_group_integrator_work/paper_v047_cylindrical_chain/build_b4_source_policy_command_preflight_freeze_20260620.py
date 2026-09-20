#!/usr/bin/env python3
"""Freeze the read-only B4 source-policy command preflight state.

The freeze records command fingerprints, row mappings, guard flags, and
expected-artifact fingerprints for the prepared B4 RA/HI commands.  It does not
execute any source-policy command.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
OUT_JSON = PAPER / "B4_SOURCE_POLICY_COMMAND_PREFLIGHT_FREEZE_20260620.json"
OUT_MD = PAPER / "B4_SOURCE_POLICY_COMMAND_PREFLIGHT_FREEZE_20260620.md"
APPROVAL = (
    "I explicitly approve running the B4 source-policy execution commands listed in "
    "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json."
)
SAFE_ACTIONS_WITHOUT_B4_OPT_IN = [
    {
        "id": "rebuild_read_only_audit_chain",
        "description": "Rebuild this command freeze plus downstream schema, promotion, objective, review, and package manifests.",
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
    return (manuscript_path(path_label)).resolve()


def row_key(row: dict[str, Any]) -> str:
    explicit = row.get("row_key")
    if isinstance(explicit, str) and explicit:
        return explicit
    return f"{row.get('suite_id')}|{row.get('method')}|{row.get('example')}"


def artifact_record(path_label: str | None) -> dict[str, Any]:
    path = package_path(path_label)
    if path is None:
        return {
            "path": None,
            "exists": None,
            "size_bytes": None,
            "sha256": None,
        }
    exists = path.exists() and path.is_file()
    return {
        "path": path_label,
        "exists": exists,
        "size_bytes": path.stat().st_size if exists else None,
        "sha256": sha256_file(path) if exists else None,
    }


def flatten_commands(packet: dict[str, Any], provenance: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [row for row in provenance.get("rows", []) if isinstance(row, dict)]
    records: list[dict[str, Any]] = []
    for batch in packet.get("execution_batches", []):
        if not isinstance(batch, dict):
            continue
        for command in batch.get("commands", []):
            if not isinstance(command, dict):
                continue
            command_id = str(command.get("id"))
            preflight = command.get("execution_preflight", {})
            if not isinstance(preflight, dict):
                preflight = {}
            matched_rows = [
                row for row in rows if command_id in (row.get("command_refs") or [])
            ]
            output_artifact = artifact_record(command.get("expected_output_after_run"))
            summary_artifact = artifact_record(command.get("expected_summary_after_run"))
            record = {
                "id": command_id,
                "batch_id": batch.get("id"),
                "suite_id": batch.get("suite_id"),
                "command": command.get("command"),
                "command_sha256": sha256_text(str(command.get("command"))),
                "argc": preflight.get("argc"),
                "argv_sha256": canonical_digest(preflight.get("argv", [])),
                "parse_ok": preflight.get("parse_ok"),
                "shell_safe_single_command": preflight.get("shell_safe_single_command"),
                "shell_control_tokens_present": preflight.get("shell_control_tokens_present"),
                "dry_run_only_in_packet": preflight.get("dry_run_only"),
                "executed_by_packet": preflight.get("executed_by_packet"),
                "execution_working_directory": preflight.get("execution_working_directory"),
                "execution_working_directory_exists": preflight.get(
                    "execution_working_directory_exists"
                ),
                "python_executable_exists": preflight.get("python_executable_exists"),
                "runner_script": preflight.get("runner_script"),
                "runner_script_exists": preflight.get("runner_script_exists"),
                "artifact_status": command.get("artifact_status"),
                "mapped_row_count_declared": command.get("mapped_row_count"),
                "mapped_row_count_traced": len(matched_rows),
                "mapped_rows_sha256": canonical_digest(
                    sorted(row_key(row) for row in matched_rows)
                ),
                "row_keys": sorted(row_key(row) for row in matched_rows),
                "source_policy_closed_rows": sum(
                    1 for row in matched_rows if row.get("source_policy_closed") is True
                ),
                "promotion_ready_rows": sum(
                    1 for row in matched_rows if row.get("promotion_ready_now") is True
                ),
                "unable_to_reproduce_rows": sum(
                    1 for row in matched_rows if row.get("unable_to_reproduce") is True
                ),
                "expected_output": output_artifact,
                "expected_summary": summary_artifact,
            }
            record["command_record_sha256"] = canonical_digest(
                {
                    key: value
                    for key, value in record.items()
                    if key != "command_record_sha256"
                }
            )
            records.append(record)
    return records


def main() -> None:
    packet = read_json(PAPER / "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json")
    handoff = read_json(PAPER / "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json")
    provenance = read_json(PAPER / "FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.json")
    records = flatten_commands(packet, provenance)
    row_keys = sorted({row for record in records for row in record["row_keys"]})
    expected_artifacts = [
        artifact
        for record in records
        for artifact in [record["expected_output"], record["expected_summary"]]
        if artifact["path"] is not None
    ]
    freeze_inputs = {
        "commands": [
            {
                "id": record["id"],
                "command_sha256": record["command_sha256"],
                "argv_sha256": record["argv_sha256"],
                "mapped_rows_sha256": record["mapped_rows_sha256"],
                "command_record_sha256": record["command_record_sha256"],
            }
            for record in records
        ],
        "expected_artifacts": [
            {
                "path": artifact["path"],
                "size_bytes": artifact["size_bytes"],
                "sha256": artifact["sha256"],
            }
            for artifact in expected_artifacts
        ],
    }
    output: dict[str, Any] = {
        "schema": "b4-source-policy-command-preflight-freeze-20260620-v1",
        "status": "command_preflight_frozen_not_authorized_not_run_not_promoted",
        "date_checked": "2026-06-20",
        "read_only": True,
        "commands_executed_by_freeze": False,
        "execution_authorized": False,
        "source_policy_execution_invoked": False,
        "source_policy_execution_allowed_now": False,
        "exact_b4_opt_in_required_for_execution": True,
        "safe_action_ids": SAFE_ACTION_IDS,
        "opt_in_action_ids": OPT_IN_ACTION_IDS,
        "next_safe_actions": SAFE_ACTIONS_WITHOUT_B4_OPT_IN,
        "next_safe_action_ids": SAFE_ACTION_IDS,
        "source_policy_rows_closed": 0,
        "source_policy_rows_total": handoff.get("source_policy_rows_total"),
        "submission_ready": False,
        "required_user_approval_statement": APPROVAL,
        "guarded_execution_driver": packet.get("guarded_execution_driver", {}).get("path"),
        "driver": packet.get("guarded_execution_driver", {}).get("path"),
        "driver_requires_exact_approval": packet.get("guarded_execution_driver", {}).get(
            "requires_exact_approval_argument"
        ),
        "driver_does_not_authorize_execution": packet.get("guarded_execution_driver", {}).get(
            "driver_does_not_authorize_execution"
        ),
        "ready_command_batch_count": packet.get("ready_command_batch_count"),
        "ready_command_count": len(records),
        "ready_command_mapped_external_rows": packet.get("ready_command_mapped_external_rows"),
        "unique_mapped_ra_hi_rows": len(row_keys),
        "declared_row_reference_total": sum(
            int(record.get("mapped_row_count_declared") or 0) for record in records
        ),
        "traced_row_reference_total": sum(
            int(record.get("mapped_row_count_traced") or 0) for record in records
        ),
        "declared_vs_traced_mismatch_count": sum(
            1
            for record in records
            if record.get("mapped_row_count_declared") != record.get("mapped_row_count_traced")
        ),
        "parse_ok_command_count": sum(1 for record in records if record.get("parse_ok") is True),
        "shell_safe_command_count": sum(
            1 for record in records if record.get("shell_safe_single_command") is True
        ),
        "dry_run_only_packet_command_count": sum(
            1 for record in records if record.get("dry_run_only_in_packet") is True
        ),
        "executed_by_packet_command_count": sum(
            1 for record in records if record.get("executed_by_packet") is True
        ),
        "expected_artifact_count": len(expected_artifacts),
        "expected_artifacts_existing_now": sum(
            1 for artifact in expected_artifacts if artifact.get("exists") is True
        ),
        "expected_artifacts_nonempty_now": sum(
            1
            for artifact in expected_artifacts
            if artifact.get("exists") is True and int(artifact.get("size_bytes") or 0) > 0
        ),
        "command_freeze_sha256": canonical_digest(freeze_inputs),
        "commands": records,
        "source_files": [
            "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json",
            "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json",
            "FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.json",
        ],
    }
    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# B4 Source-Policy Command Preflight Freeze 20260620",
        "",
        f"Status: `{output['status']}`.",
        "",
        "This is a read-only command fingerprint and artifact-state freeze. It does not authorize or run B4 source-policy commands.",
        "",
        f"- Ready command batches/commands/mapped rows: `{output['ready_command_batch_count']}/{output['ready_command_count']}/{output['ready_command_mapped_external_rows']}`.",
        f"- Unique mapped RA/HI rows: `{output['unique_mapped_ra_hi_rows']}`.",
        f"- Row references declared/traced/mismatched: `{output['declared_row_reference_total']}/{output['traced_row_reference_total']}/{output['declared_vs_traced_mismatch_count']}`.",
        f"- Preflight parse/shell-safe/dry-run-only counts: `{output['parse_ok_command_count']}/{output['shell_safe_command_count']}/{output['dry_run_only_packet_command_count']}`.",
        f"- Commands executed by packet/freezer: `{output['executed_by_packet_command_count']}/{output['commands_executed_by_freeze']}`.",
        f"- Source-policy execution allowed now/invoked/exact opt-in required: `{output['source_policy_execution_allowed_now']}/{output['source_policy_execution_invoked']}/{output['exact_b4_opt_in_required_for_execution']}`.",
        f"- Required approval/driver: `{output['required_user_approval_statement']}/{output['guarded_execution_driver']}`.",
        f"- Safe action ids: `{','.join(output['safe_action_ids'])}`.",
        f"- Opt-in action ids: `{','.join(output['opt_in_action_ids'])}`.",
        f"- Expected artifacts existing/nonempty/total: `{output['expected_artifacts_existing_now']}/{output['expected_artifacts_nonempty_now']}/{output['expected_artifact_count']}`.",
        f"- Source-policy rows closed/total: `{output['source_policy_rows_closed']}/{output['source_policy_rows_total']}`.",
        f"- Freeze digest: `{output['command_freeze_sha256']}`.",
        "",
        "## Command Fingerprints",
        "",
        "| command id | rows | command sha256 | record sha256 |",
        "|---|---:|---|---|",
    ]
    for record in records:
        lines.append(
            f"| `{record['id']}` | `{record['mapped_row_count_traced']}` | "
            f"`{record['command_sha256'][:16]}` | `{record['command_record_sha256'][:16]}` |"
        )
    lines.extend(
        [
            "",
            "## Required Opt-In Boundary",
            "",
            f"`{APPROVAL}`",
            "",
            "Rows remain unclosed until authorized execution and a post-execution promotion audit explicitly promote them.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("b4 source-policy command preflight freeze: written")
    print(f"ready_command_count={output['ready_command_count']}")
    print(f"unique_mapped_ra_hi_rows={output['unique_mapped_ra_hi_rows']}")
    print(f"expected_artifacts={output['expected_artifacts_existing_now']}/{output['expected_artifact_count']}")
    print(f"commands_executed_by_freeze={output['commands_executed_by_freeze']}")
    print("source_policy_execution_invoked=False")
    print("source_policy_execution_allowed_now=False")
    print(f"source_policy_closed={output['source_policy_rows_closed']}/{output['source_policy_rows_total']}")


if __name__ == "__main__":
    main()
