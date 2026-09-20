#!/usr/bin/env python3
"""Validate the read-only B4 source-policy command preflight freeze."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
APPROVAL = (
    "I explicitly approve running the B4 source-policy execution commands listed in "
    "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json."
)
EXPECTED_DRIVER = "run_b4_source_policy_after_opt_in.sh"
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


def expected_records(packet: dict[str, Any], provenance: dict[str, Any]) -> list[dict[str, Any]]:
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
                "expected_output": artifact_record(command.get("expected_output_after_run")),
                "expected_summary": artifact_record(command.get("expected_summary_after_run")),
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


def freeze_digest(records: list[dict[str, Any]]) -> str:
    expected_artifacts = [
        artifact
        for record in records
        for artifact in [record["expected_output"], record["expected_summary"]]
        if artifact["path"] is not None
    ]
    return canonical_digest(
        {
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
    )


def main() -> int:
    checks = Checks()
    try:
        freeze = read_json(PAPER / "B4_SOURCE_POLICY_COMMAND_PREFLIGHT_FREEZE_20260620.json")
        text = (PAPER / "B4_SOURCE_POLICY_COMMAND_PREFLIGHT_FREEZE_20260620.md").read_text(
            encoding="utf-8",
            errors="replace",
        )
        packet = read_json(PAPER / "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json")
        handoff = read_json(PAPER / "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json")
        provenance = read_json(PAPER / "FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.json")
    except Exception as exc:  # noqa: BLE001
        print(f"b4 source-policy command preflight freeze validation: FAIL\n- {exc}")
        return 1

    records = expected_records(packet, provenance)
    record_by_id = {record["id"]: record for record in records}
    frozen_by_id = {
        record.get("id"): record
        for record in freeze.get("commands", [])
        if isinstance(record, dict)
    }
    expected_artifact_count = sum(
        1
        for record in records
        for artifact in [record["expected_output"], record["expected_summary"]]
        if artifact["path"] is not None
    )

    checks.check(
        freeze.get("schema") == "b4-source-policy-command-preflight-freeze-20260620-v1",
        "schema changed",
    )
    checks.check(
        freeze.get("status") == "command_preflight_frozen_not_authorized_not_run_not_promoted",
        "status changed",
    )
    checks.check(freeze.get("date_checked") == "2026-06-20", "date changed")
    checks.check(freeze.get("read_only") is True, "freeze must be read-only")
    checks.check(freeze.get("commands_executed_by_freeze") is False, "freeze executed commands")
    checks.check(freeze.get("execution_authorized") is False, "freeze authorized execution")
    checks.check(freeze.get("source_policy_execution_invoked") is False, "freeze invoked source-policy execution")
    checks.check(
        freeze.get("source_policy_execution_allowed_now") is False,
        "freeze allows source-policy execution without opt-in",
    )
    checks.check(
        freeze.get("exact_b4_opt_in_required_for_execution") is True,
        "freeze lost exact B4 opt-in requirement",
    )
    checks.check(freeze.get("safe_action_ids") == EXPECTED_SAFE_ACTION_IDS, "safe action ids changed")
    checks.check(freeze.get("opt_in_action_ids") == EXPECTED_OPT_IN_ACTION_IDS, "opt-in action ids changed")
    checks.check(
        freeze.get("next_safe_action_ids") == freeze.get("safe_action_ids") == EXPECTED_SAFE_ACTION_IDS,
        "next safe action ids stale",
    )
    checks.check(
        [item.get("id") for item in freeze.get("next_safe_actions", [])]
        == EXPECTED_SAFE_ACTION_IDS,
        "next safe actions stale",
    )
    checks.check(freeze.get("source_policy_rows_closed") == 0, "source-policy rows overclosed")
    checks.check(
        freeze.get("source_policy_rows_total") == handoff.get("source_policy_rows_total") == 40,
        "source-policy total changed",
    )
    checks.check(freeze.get("submission_ready") is False, "submission unexpectedly ready")
    checks.check(
        freeze.get("required_user_approval_statement") == APPROVAL,
        "approval statement changed",
    )
    checks.check(freeze.get("guarded_execution_driver") == EXPECTED_DRIVER, "guarded driver alias missing or stale")
    checks.check(freeze.get("driver") == EXPECTED_DRIVER, "driver changed")
    checks.check(freeze.get("driver_requires_exact_approval") is True, "driver lost exact guard")
    checks.check(
        freeze.get("driver_does_not_authorize_execution") is True,
        "driver unexpectedly authorizes execution",
    )
    checks.check(freeze.get("ready_command_batch_count") == 2, "batch count changed")
    checks.check(freeze.get("ready_command_count") == 13, "command count changed")
    checks.check(freeze.get("ready_command_mapped_external_rows") == 20, "mapped row count changed")
    checks.check(freeze.get("unique_mapped_ra_hi_rows") == 20, "unique row count changed")
    checks.check(freeze.get("declared_row_reference_total") == 32, "declared row refs changed")
    checks.check(freeze.get("traced_row_reference_total") == 32, "traced row refs changed")
    checks.check(
        freeze.get("declared_vs_traced_mismatch_count") == 0,
        "declared/traced row mismatches present",
    )
    checks.check(freeze.get("parse_ok_command_count") == 13, "not all commands parse")
    checks.check(freeze.get("shell_safe_command_count") == 13, "not all commands are shell-safe")
    checks.check(
        freeze.get("dry_run_only_packet_command_count") == 13,
        "packet did not keep all commands dry-run-only",
    )
    checks.check(
        freeze.get("executed_by_packet_command_count") == 0,
        "packet executed commands",
    )
    checks.check(
        freeze.get("expected_artifact_count") == expected_artifact_count == 21,
        "expected artifact count changed",
    )
    checks.check(
        freeze.get("expected_artifacts_existing_now") == 21,
        "not all expected artifacts exist",
    )
    checks.check(
        freeze.get("expected_artifacts_nonempty_now") == 21,
        "not all expected artifacts are nonempty",
    )
    checks.check(
        freeze.get("command_freeze_sha256") == freeze_digest(records),
        "global freeze digest is stale",
    )
    checks.check(set(record_by_id) == set(frozen_by_id), "frozen command IDs changed")
    for command_id, expected in record_by_id.items():
        frozen = frozen_by_id.get(command_id, {})
        for key in [
            "command_sha256",
            "argv_sha256",
            "mapped_rows_sha256",
            "command_record_sha256",
        ]:
            checks.check(
                frozen.get(key) == expected.get(key),
                f"{command_id} {key} is stale",
            )
        checks.check(
            frozen.get("mapped_row_count_declared") == frozen.get("mapped_row_count_traced"),
            f"{command_id} row traceability mismatch",
        )
        checks.check(
            frozen.get("source_policy_closed_rows") == 0,
            f"{command_id} overclosed source-policy rows",
        )
        checks.check(
            frozen.get("promotion_ready_rows") == 0,
            f"{command_id} unexpectedly promotion-ready",
        )
        checks.check(
            frozen.get("executed_by_packet") is False,
            f"{command_id} packet execution flag changed",
        )

    for token in [
        "command_preflight_frozen_not_authorized_not_run_not_promoted",
        "Ready command batches/commands/mapped rows: `2/13/20`",
        "Unique mapped RA/HI rows: `20`",
        "Row references declared/traced/mismatched: `32/32/0`",
        "Preflight parse/shell-safe/dry-run-only counts: `13/13/13`",
        "Commands executed by packet/freezer: `0/False`",
        "Source-policy execution allowed now/invoked/exact opt-in required: `False/False/True`",
        "Safe action ids: `rebuild_read_only_audit_chain,rerun_read_only_validators,keep_narrowed_archive_provenance_only,monitor_reopen_conditions`",
        "Opt-in action ids: `authorized_b4_ra_hi_source_policy_execution`",
        f"Required approval/driver: `{APPROVAL}/{EXPECTED_DRIVER}`.",
        "Expected artifacts existing/nonempty/total: `21/21/21`",
        "Source-policy rows closed/total: `0/40`",
        APPROVAL,
    ]:
        checks.check(token in text, f"markdown missing token: {token}")

    if checks.errors:
        print("b4 source-policy command preflight freeze validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("b4 source-policy command preflight freeze validation: PASS")
    print(f"ready_command_count={freeze.get('ready_command_count')}")
    print(f"unique_mapped_ra_hi_rows={freeze.get('unique_mapped_ra_hi_rows')}")
    print(
        f"expected_artifacts={freeze.get('expected_artifacts_existing_now')}/"
        f"{freeze.get('expected_artifact_count')}"
    )
    print(f"commands_executed_by_freeze={freeze.get('commands_executed_by_freeze')}")
    print("source_policy_execution_invoked=False")
    print("source_policy_execution_allowed_now=False")
    print("safe_action_ids=rebuild_read_only_audit_chain,rerun_read_only_validators,keep_narrowed_archive_provenance_only,monitor_reopen_conditions")
    print("opt_in_action_ids=authorized_b4_ra_hi_source_policy_execution")
    print(
        f"source_policy_closed={freeze.get('source_policy_rows_closed')}/"
        f"{freeze.get('source_policy_rows_total')}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
