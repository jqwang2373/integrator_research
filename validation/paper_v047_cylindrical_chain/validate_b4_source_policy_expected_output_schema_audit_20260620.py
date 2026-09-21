#!/usr/bin/env python3
"""Validate the read-only B4 expected-output schema audit."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
AUDIT_JSON = PAPER / "B4_SOURCE_POLICY_EXPECTED_OUTPUT_SCHEMA_AUDIT_20260620.json"
AUDIT_MD = PAPER / "B4_SOURCE_POLICY_EXPECTED_OUTPUT_SCHEMA_AUDIT_20260620.md"
FREEZE_PATH = PAPER / "B4_SOURCE_POLICY_COMMAND_PREFLIGHT_FREEZE_20260620.json"
SCHEMA = "b4-source-policy-expected-output-schema-audit-20260620-v1"
STATUS = "expected_outputs_schema_ready_not_authorized_not_run_not_promoted"
FREEZE_STATUS = "command_preflight_frozen_not_authorized_not_run_not_promoted"
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

    status_counts = compact_counts([row.get("status", "") for row in rows])
    policy_counts = compact_counts([row.get("policy", "") for row in rows])
    result.update(
        {
            "parseable": True,
            "header": header,
            "column_count": len(header),
            "row_count": len(rows),
            "status_counts": status_counts,
            "policy_counts": policy_counts,
            "model_values": compact_unique(rows, "model"),
            "form_values": compact_unique(rows, "form"),
            "method_values": compact_unique(rows, "method"),
            "h_values": compact_unique(rows, "h"),
            "schema_signature": canonical_digest(
                {
                    "header": header,
                    "row_count": len(rows),
                    "status_counts": status_counts,
                    "policy_counts": policy_counts,
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


def expected_payload(freeze: dict[str, Any]) -> dict[str, Any]:
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
    return {
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
    }


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(AUDIT_JSON)
        text = AUDIT_MD.read_text(encoding="utf-8", errors="replace")
        freeze = read_json(FREEZE_PATH)
    except Exception as exc:  # noqa: BLE001
        print(f"b4 expected-output schema audit validation: FAIL\n- {exc}")
        return 1

    expected = expected_payload(freeze)
    checks.check(audit.get("schema") == SCHEMA, "schema changed")
    checks.check(audit.get("status") == STATUS, "status changed")
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
    checks.check(audit.get("source_policy_rows_closed") == 0, "source-policy rows overclosed")
    checks.check(audit.get("source_policy_rows_total") == 40, "source-policy total changed")
    checks.check(audit.get("promotion_ready_rows") == 0, "promotion rows overclaimed")
    checks.check(audit.get("submission_ready") is False, "submission unexpectedly ready")
    checks.check(
        audit.get("required_user_approval_statement") == APPROVAL,
        "approval statement changed",
    )
    checks.check(
        audit.get("guarded_execution_driver") == EXPECTED_DRIVER,
        "guarded driver alias missing or stale",
    )
    checks.check(
        "B4_SOURCE_POLICY_COMMAND_PREFLIGHT_FREEZE_20260620.json"
        in audit.get("source_files", []),
        "freeze source file missing",
    )

    freeze_input = audit.get("input_freeze", {})
    checks.check(freeze_input.get("schema") == freeze.get("schema"), "input freeze schema stale")
    checks.check(freeze_input.get("status") == FREEZE_STATUS, "input freeze status changed")
    checks.check(freeze.get("status") == FREEZE_STATUS, "freeze status changed")
    checks.check(freeze_input.get("ready_command_count") == 13, "freeze command count changed")
    checks.check(freeze_input.get("unique_mapped_ra_hi_rows") == 20, "freeze mapped rows changed")
    checks.check(freeze_input.get("declared_row_reference_total") == 32, "declared row refs changed")
    checks.check(freeze_input.get("traced_row_reference_total") == 32, "traced row refs changed")
    checks.check(freeze_input.get("expected_artifact_count") == 21, "freeze artifact count changed")
    checks.check(freeze_input.get("commands_executed_by_freeze") is False, "freeze executed commands")
    checks.check(freeze_input.get("execution_authorized") is False, "freeze authorized execution")
    checks.check(
        freeze_input.get("source_policy_execution_invoked") is False,
        "freeze input invoked source-policy execution",
    )
    checks.check(
        freeze_input.get("source_policy_execution_allowed_now") is False,
        "freeze input allows source-policy execution without opt-in",
    )
    checks.check(
        freeze_input.get("exact_b4_opt_in_required_for_execution") is True,
        "freeze input lost exact B4 opt-in requirement",
    )
    checks.check(
        freeze_input.get("safe_action_ids") == EXPECTED_SAFE_ACTION_IDS
        and freeze_input.get("opt_in_action_ids") == EXPECTED_OPT_IN_ACTION_IDS,
        "freeze input action ids changed",
    )
    checks.check(freeze_input.get("source_policy_rows_closed") == 0, "freeze overclosed rows")
    checks.check(freeze_input.get("submission_ready") is False, "freeze overclaimed submission readiness")

    for key, expected_value in expected.items():
        checks.check(audit.get(key) == expected_value, f"audit key stale: {key}")

    checks.check(audit.get("command_count") == 13, "expected 13 commands")
    checks.check(audit.get("expected_csv_artifact_count") == 13, "expected 13 CSV artifacts")
    checks.check(audit.get("expected_json_summary_artifact_count") == 8, "expected 8 JSON summaries")
    checks.check(audit.get("expected_artifact_count") == 21, "expected 21 artifacts")
    checks.check(audit.get("artifacts_existing_now") == 21, "not all expected artifacts exist")
    checks.check(audit.get("artifacts_nonempty_now") == 21, "not all expected artifacts are nonempty")
    checks.check(audit.get("artifacts_size_match_freeze") == 21, "artifact sizes no longer match freeze")
    checks.check(audit.get("artifacts_sha256_match_freeze") == 21, "artifact hashes no longer match freeze")
    checks.check(audit.get("csv_parseable_artifacts") == 13, "not all CSV artifacts parse")
    checks.check(audit.get("json_summary_parseable_artifacts") == 8, "not all JSON summaries parse")
    checks.check(audit.get("schema_ready_commands") == 13, "not all command outputs are schema-ready")
    command_traceability = audit.get("command_traceability", {})
    checks.check(
        command_traceability
        == {
            "commands_with_shell_command": 13,
            "commands_with_expected_output_path": 13,
            "commands_with_expected_summary_path": 8,
            "commands_without_expected_summary_path": 5,
            "commands_with_existing_expected_output": 13,
            "commands_with_existing_expected_summary": 8,
            "source_policy_execution_invoked": False,
            "commands_executed_by_audit": False,
        },
        "command traceability summary changed",
    )
    freeze_commands = {
        command.get("id"): command
        for command in freeze.get("commands", [])
        if isinstance(command, dict)
    }
    for command in audit.get("commands", []):
        if not isinstance(command, dict):
            checks.check(False, "command record is not an object")
            continue
        freeze_command = freeze_commands.get(command.get("id"), {})
        checks.check(command.get("command") == freeze_command.get("command"), f"command text stale: {command.get('id')}")
        checks.check(
            command.get("expected_output_after_run")
            == freeze_command.get("expected_output", {}).get("path")
            == command.get("expected_output_schema", {}).get("path"),
            f"expected output path stale: {command.get('id')}",
        )
        checks.check(
            command.get("expected_summary_after_run")
            == freeze_command.get("expected_summary", {}).get("path")
            == command.get("expected_summary_schema", {}).get("path"),
            f"expected summary path stale: {command.get('id')}",
        )
        checks.check(
            command.get("expected_output_exists_now")
            == command.get("expected_output_schema", {}).get("exists"),
            f"expected output existence alias stale: {command.get('id')}",
        )
        checks.check(
            command.get("expected_summary_exists_now")
            == command.get("expected_summary_schema", {}).get("exists"),
            f"expected summary existence alias stale: {command.get('id')}",
        )

    for token in [
        "expected_outputs_schema_ready_not_authorized_not_run_not_promoted",
        "Commands/CSV summaries/JSON summaries/artifacts: `13/13/8/21`",
        "Artifacts existing/nonempty/size-match/hash-match: `21/21/21/21`",
        "Parseable CSV/JSON summary artifacts: `13/8`",
        "Schema-ready commands: `13/13`",
        "Command traceability shell/output/summary/no-summary/existing-output/existing-summary: `13/13/8/5/13/8`.",
        "Commands executed / source-policy rows closed / promotion-ready rows: `False/0/0`",
        "Source-policy execution allowed now/invoked/exact opt-in required: `False/False/True`",
        "Safe action ids: `rebuild_read_only_audit_chain,rerun_read_only_validators,keep_narrowed_archive_provenance_only,monitor_reopen_conditions`",
        "Opt-in action ids: `authorized_b4_ra_hi_source_policy_execution`",
        f"Required approval/driver: `{APPROVAL}/{EXPECTED_DRIVER}`.",
        "Submission ready: `False`",
        "post-execution promotion evidence is still required",
    ]:
        checks.check(token in text, f"markdown token missing: {token}")

    if checks.errors:
        print("b4 expected-output schema audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print(
        "b4 expected-output schema audit validation: PASS "
        f"commands={audit.get('schema_ready_commands')}/{audit.get('command_count')} "
        f"artifacts={audit.get('artifacts_existing_now')}/{audit.get('expected_artifact_count')} "
        f"csv_json_parseable={audit.get('csv_parseable_artifacts')}/"
        f"{audit.get('json_summary_parseable_artifacts')} "
        f"source_policy_rows_closed={audit.get('source_policy_rows_closed')}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
