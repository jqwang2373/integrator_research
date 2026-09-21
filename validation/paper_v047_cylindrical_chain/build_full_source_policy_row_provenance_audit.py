#!/usr/bin/env python3
"""Build a read-only row provenance audit for the full source-policy lane."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
ROOT = PAPER.parents[1]
OUT_JSON = PAPER / "FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.json"
OUT_MD = PAPER / "FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.md"
OUT_CSV = PAPER / "FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.csv"


SOURCE_ROOTS = {
    "ra2021_absolute_coordinate": ROOT / "external" / "sbel-reproducibility" / "2021" / "ASME" / "rA-formulation",
    "hi2022_half_implicit": ROOT / "external" / "sbel-reproducibility" / "2022" / "HalfImplicit_JCND",
}


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def rel(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return str(path.resolve().relative_to(PAPER))
    except ValueError:
        try:
            return str(path.resolve().relative_to(ROOT))
        except ValueError:
            return str(path)


def resolve_paper_relative(label: str | None) -> Path | None:
    if not label:
        return None
    path = Path(label)
    if path.is_absolute():
        return path
    return (manuscript_path(path)).resolve()


def file_sha256(path: Path | None) -> str | None:
    if path is None or not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_root_digest(root: Path | None) -> dict[str, Any]:
    if root is None or not root.exists():
        return {
            "exists": False,
            "path": rel(root) if root else None,
            "tracked_file_count": 0,
            "python_file_count": 0,
            "digest": None,
        }
    files = sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and ".git" not in path.parts and path.suffix.lower() in {".py", ".md", ".csv", ".sh"}
    )
    digest = hashlib.sha256()
    for path in files:
        relative = path.relative_to(root).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update((file_sha256(path) or "").encode("ascii"))
        digest.update(b"\0")
    return {
        "exists": True,
        "path": rel(root),
        "tracked_file_count": len(files),
        "python_file_count": sum(1 for path in files if path.suffix.lower() == ".py"),
        "digest": digest.hexdigest(),
    }


def command_index(packet: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for batch in packet.get("execution_batches", []):
        if not isinstance(batch, dict):
            continue
        for command in batch.get("commands", []):
            if isinstance(command, dict):
                out[str(command.get("id"))] = command
    return out


def blocker_rows(matrix: dict[str, Any]) -> dict[tuple[str, str, str], dict[str, Any]]:
    out: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in matrix.get("rows", []):
        if not isinstance(row, dict):
            continue
        key = (str(row.get("suite_id")), str(row.get("method")), str(row.get("example")))
        out[key] = row
    return out


def handoff_summary(handoff: dict[str, Any]) -> dict[str, Any]:
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


def row_key(row: dict[str, Any]) -> tuple[str, str, str]:
    return (str(row.get("suite_id")), str(row.get("method")), str(row.get("example")))


def provenance_for_row(
    row: dict[str, Any],
    commands: dict[str, dict[str, Any]],
    blocker_by_key: dict[tuple[str, str, str], dict[str, Any]],
) -> dict[str, Any]:
    suite_id, method, example = row_key(row)
    command_refs = [str(item) for item in row.get("command_refs", [])]
    root = SOURCE_ROOTS.get(suite_id)
    root_info = source_root_digest(root) if suite_id in SOURCE_ROOTS else {
        "exists": False,
        "path": None,
        "tracked_file_count": 0,
        "python_file_count": 0,
        "digest": None,
    }
    command_entries: list[dict[str, Any]] = []
    all_outputs_present = bool(command_refs)
    for command_id in command_refs:
        command = commands.get(command_id, {})
        output = resolve_paper_relative(command.get("expected_output_after_run"))
        summary = resolve_paper_relative(command.get("expected_summary_after_run"))
        output_present = bool(output and output.exists() and output.stat().st_size > 0)
        summary_present = None if not command.get("expected_summary_after_run") else bool(
            summary and summary.exists() and summary.stat().st_size > 0
        )
        all_outputs_present = all_outputs_present and output_present and (summary_present is not False)
        command_entries.append(
            {
                "command_id": command_id,
                "artifact_status": command.get("artifact_status"),
                "expected_output": command.get("expected_output_after_run"),
                "expected_output_exists": output_present,
                "expected_output_sha256": file_sha256(output),
                "expected_summary": command.get("expected_summary_after_run"),
                "expected_summary_exists": summary_present,
                "expected_summary_sha256": file_sha256(summary),
            }
        )

    blocker = blocker_by_key.get((suite_id, method, example), {})
    no_public_code_case = bool(row.get("unable_to_reproduce")) or suite_id in {
        "tfe2026_original_pendulum",
        "vp2024_velocity_partitioning",
    }
    source_root_status = (
        "public_source_root_present"
        if root_info.get("exists")
        else "no_public_or_no_source_equivalent_code_root"
    )
    disposition = str(row.get("source_policy_disposition"))
    evidence_ref = str(row.get("promotion_evidence_ref") or "")
    primary_blocker = str(row.get("primary_promotion_blocker") or "")
    provenance_preflight_complete = all(
        [
            suite_id,
            method,
            example,
            disposition,
            evidence_ref,
            primary_blocker,
            (root_info.get("exists") and bool(command_refs)) or no_public_code_case,
        ]
    )
    return {
        "row_key": f"{suite_id}|{method}|{example}",
        "suite_id": suite_id,
        "method": method,
        "example": example,
        "source_root_status": source_root_status,
        "source_root": root_info,
        "command_refs": command_refs,
        "command_outputs": command_entries,
        "all_command_outputs_present": all_outputs_present,
        "source_policy_disposition": disposition,
        "source_policy_closed": bool(row.get("source_policy_closed")),
        "source_policy_reproduction_complete": bool(row.get("source_policy_reproduction_complete")),
        "unable_to_reproduce": bool(row.get("unable_to_reproduce")),
        "no_public_code_case": no_public_code_case,
        "primary_promotion_blocker": primary_blocker,
        "promotion_evidence_ref": evidence_ref,
        "blocking_reasons": row.get("blocking_reasons", []),
        "matrix_current_evidence_terminal_not_promotable": blocker.get(
            "current_evidence_terminal_not_promotable"
        ),
        "matrix_future_promotion_requires_authorized_execution_or_new_artifact": blocker.get(
            "future_promotion_requires_authorized_execution_or_new_artifact"
        ),
        "matrix_ready_to_launch_after_explicit_opt_in": blocker.get(
            "ready_to_launch_after_explicit_opt_in"
        ),
        "provenance_preflight_complete": provenance_preflight_complete,
        "promotion_ready_now": False,
    }


def main() -> None:
    row_ledger = read_json(PAPER / "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.json")
    packet = read_json(PAPER / "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json")
    matrix = read_json(PAPER / "RA_HI_SOURCE_POLICY_PROMOTION_BLOCKER_MATRIX.json")
    public_refresh = read_json(PAPER / "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.json")
    handoff = read_json(PAPER / "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json")
    source_policy_execution_handoff = handoff_summary(handoff)
    safe_action_ids = [
        "rebuild_read_only_audit_chain",
        "rerun_read_only_validators",
        "keep_narrowed_archive_provenance_only",
        "monitor_reopen_conditions",
    ]
    safe_next_actions = [
        {
            "id": "rebuild_read_only_audit_chain",
            "allowed_without_b4_opt_in": True,
            "does_not_execute_source_policy_commands": True,
            "description": "Rebuild read-only provenance and downstream audit artifacts after metadata-only changes.",
        },
        {
            "id": "rerun_read_only_validators",
            "allowed_without_b4_opt_in": True,
            "does_not_execute_source_policy_commands": True,
            "description": "Run validators that only inspect existing artifacts and source-policy execution guards.",
        },
        {
            "id": "keep_narrowed_archive_provenance_only",
            "allowed_without_b4_opt_in": True,
            "does_not_execute_source_policy_commands": True,
            "description": "Keep the narrowed archive as provenance only; do not promote row provenance as source-policy closure.",
        },
        {
            "id": "monitor_reopen_conditions",
            "allowed_without_b4_opt_in": True,
            "does_not_execute_source_policy_commands": True,
            "description": "Monitor terminal rows for new public, author-provided, or source-equivalent implementation artifacts.",
        },
    ]
    opt_in_action_ids = ["authorized_b4_ra_hi_source_policy_execution"]
    required_approval_statement = source_policy_execution_handoff.get(
        "required_user_approval_statement"
    ) or source_policy_execution_handoff.get("exact_required_user_approval_statement")
    guarded_execution_driver = source_policy_execution_handoff.get("guarded_execution_driver")
    action_boundary = {
        "safe_without_b4_opt_in_count": len(safe_action_ids),
        "opt_in_required_action_count": len(opt_in_action_ids),
        "source_policy_execution_allowed_now": False,
        "exact_b4_opt_in_required_for_execution": True,
        "safe_action_ids": safe_action_ids,
        "opt_in_action_ids": opt_in_action_ids,
        "required_user_approval_statement": required_approval_statement,
        "guarded_execution_driver": guarded_execution_driver,
        "opt_in_required_command_count": source_policy_execution_handoff.get(
            "opt_in_required_command_count"
        ),
        "opt_in_required_mapped_external_rows": source_policy_execution_handoff.get(
            "opt_in_required_mapped_external_rows"
        ),
    }

    commands = command_index(packet)
    blockers = blocker_rows(matrix)
    rows = [
        provenance_for_row(row, commands, blockers)
        for row in row_ledger.get("rows", [])
        if isinstance(row, dict)
    ]
    suite_summary: dict[str, dict[str, Any]] = {}
    for row in rows:
        item = suite_summary.setdefault(
            row["suite_id"],
            {
                "row_count": 0,
                "provenance_preflight_complete_rows": 0,
                "source_policy_closed_rows": 0,
                "unable_to_reproduce_rows": 0,
                "public_source_root_rows": 0,
                "command_mapped_rows": 0,
                "promotion_ready_rows": 0,
            },
        )
        item["row_count"] += 1
        item["provenance_preflight_complete_rows"] += int(row["provenance_preflight_complete"])
        item["source_policy_closed_rows"] += int(row["source_policy_closed"])
        item["unable_to_reproduce_rows"] += int(row["unable_to_reproduce"])
        item["public_source_root_rows"] += int(row["source_root_status"] == "public_source_root_present")
        item["command_mapped_rows"] += int(bool(row["command_refs"]))
        item["promotion_ready_rows"] += int(row["promotion_ready_now"])

    source_policy_rows_total = int(row_ledger.get("row_count") or len(rows))
    source_policy_rows_closed = int(row_ledger.get("source_policy_rows_closed") or 0)
    source_policy_rows_promoted = sum(1 for row in rows if row["promotion_ready_now"])
    terminal_unable_to_reproduce_rows = int(
        row_ledger.get("source_policy_rows_unable_to_reproduce")
        or sum(1 for row in rows if row["unable_to_reproduce"])
    )
    attempted_not_reproducible_rows = int(
        row_ledger.get("source_policy_rows_attempted_not_reproducible")
        or sum(1 for row in rows if row["source_policy_disposition"] == "attempted_not_reproducible")
    )
    ready_command_count = int(packet.get("ready_command_count") or 0)
    mapped_external_row_count = int(packet.get("ready_command_mapped_external_rows") or 0)
    command_traceability_summary = handoff.get("command_row_traceability", {}).get(
        "summary",
        {},
    )

    result: dict[str, Any] = {
        "schema": "full-source-policy-row-provenance-audit-v1",
        "status": "row_provenance_preflight_complete_source_policy_promotion_open",
        "blocker_id": "OC4",
        "oc4_blocker_id": "OC4",
        "blocker_status": "open",
        "oc4_blocker_status": "open",
        "oc4_blocker_open": True,
        "closure_decision": "remain_open_ready_for_authorized_execution_not_executed_not_promoted",
        "oc4_closure_decision": "remain_open_ready_for_authorized_execution_not_executed_not_promoted",
        "closure_allowed_now": False,
        "oc4_closure_allowed_now": False,
        "required_evidence_to_close": [
            "authorized RA/HI source-policy closeout under the exact B4 opt-in or a new source-policy promotion artifact",
            "post-execution promotion validator records source-policy rows as closed",
            "work/precision rows bind error, order, runtime, Newton, and source-policy labels to the same promoted rows",
        ],
        "read_only": True,
        "execution_invoked": False,
        "source_policy_execution_invoked": False,
        "source_policy_execution_allowed_now": False,
        "exact_b4_opt_in_required_for_execution": True,
        "run_v047_invoked": False,
        "v048_runner_invoked": False,
        "packet_does_not_authorize_execution": True,
        "required_user_approval_statement": required_approval_statement,
        "guarded_execution_driver": guarded_execution_driver,
        "safe_without_b4_opt_in_count": len(safe_action_ids),
        "opt_in_required_action_count": len(opt_in_action_ids),
        "next_safe_actions": safe_next_actions,
        "next_safe_action_ids": safe_action_ids,
        "safe_action_ids": safe_action_ids,
        "opt_in_action_ids": opt_in_action_ids,
        "action_boundary": action_boundary,
        "row_count": len(rows),
        "rows_total": len(rows),
        "source_policy_rows_total": source_policy_rows_total,
        "source_policy_rows_closed": source_policy_rows_closed,
        "source_policy_rows_promoted": source_policy_rows_promoted,
        "source_policy_closed": False,
        "source_policy_closed_ratio": f"{source_policy_rows_closed}/{source_policy_rows_total}",
        "ready_command_count": ready_command_count,
        "mapped_external_row_count": mapped_external_row_count,
        "ready_commands_mapped_rows": f"{ready_command_count}/{mapped_external_row_count}",
        "command_traceability_summary": command_traceability_summary,
        "traceability_unique_rows": command_traceability_summary.get("unique_mapped_row_count"),
        "traceability_reference_count": command_traceability_summary.get(
            "traced_command_row_reference_total"
        ),
        "traceability_declared_reference_count": command_traceability_summary.get(
            "declared_mapped_row_reference_total"
        ),
        "traceability_mismatch_count": command_traceability_summary.get(
            "declared_vs_traced_mismatch_count"
        ),
        "traceability_unique_traced_declared_mismatch": (
            f"{command_traceability_summary.get('unique_mapped_row_count')}/"
            f"{command_traceability_summary.get('traced_command_row_reference_total')}/"
            f"{command_traceability_summary.get('declared_mapped_row_reference_total')}/"
            f"{command_traceability_summary.get('declared_vs_traced_mismatch_count')}"
        ),
        "terminal_unable_to_reproduce_rows": terminal_unable_to_reproduce_rows,
        "attempted_not_reproducible_rows": attempted_not_reproducible_rows,
        "source_policy_rows_unable_to_reproduce": terminal_unable_to_reproduce_rows,
        "source_policy_rows_still_requiring_execution_or_promotion": row_ledger.get(
            "source_policy_rows_still_requiring_execution_or_promotion"
        ),
        "provenance_preflight_complete_rows": sum(
            1 for row in rows if row["provenance_preflight_complete"]
        ),
        "provenance_preflight": f"{sum(1 for row in rows if row['provenance_preflight_complete'])}/{len(rows)}",
        "provenance_preflight_complete": all(
            row["provenance_preflight_complete"] for row in rows
        ),
        "public_source_root_rows": sum(
            1 for row in rows if row["source_root_status"] == "public_source_root_present"
        ),
        "command_mapped_rows": sum(1 for row in rows if row["command_refs"]),
        "rows_with_all_command_outputs_present": sum(
            1 for row in rows if row["command_refs"] and row["all_command_outputs_present"]
        ),
        "promotion_ready_rows": sum(1 for row in rows if row["promotion_ready_now"]),
        "source_policy_reproduction_complete_rows": sum(
            1 for row in rows if row["source_policy_reproduction_complete"]
        ),
        "public_code_refresh_status": public_refresh.get("status"),
        "handoff_execution_authorized": handoff.get("execution_authorized"),
        "handoff_commands_not_run_by_handoff": handoff.get("commands_not_run_by_handoff"),
        "source_policy_execution_handoff": source_policy_execution_handoff,
        "source_root_inventory": {
            suite_id: source_root_digest(path) for suite_id, path in SOURCE_ROOTS.items()
        },
        "suite_summary": sorted(suite_summary.values(), key=lambda item: item["row_count"], reverse=True),
        "rows": rows,
        "source_files": {
            "row_ledger": "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.json",
            "opt_in_packet": "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json",
            "promotion_blocker_matrix": "RA_HI_SOURCE_POLICY_PROMOTION_BLOCKER_MATRIX.json",
            "public_code_refresh": "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.json",
            "handoff_package": "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json",
        },
        "claim_boundary": {
            "provenance_preflight_complete_is_not_source_policy_closure": True,
            "source_policy_promotion_still_requires_authorized_closeout_or_new_artifact": True,
            "b4_can_close_now": False,
            "b7_can_close_now": False,
            "full_source_policy_submission_ready": False,
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "row_key",
                "suite_id",
                "method",
                "example",
                "source_root_status",
                "command_refs",
                "all_command_outputs_present",
                "source_policy_disposition",
                "source_policy_closed",
                "unable_to_reproduce",
                "primary_promotion_blocker",
                "promotion_evidence_ref",
                "provenance_preflight_complete",
                "promotion_ready_now",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    **{key: row.get(key) for key in writer.fieldnames if key not in {"command_refs"}},
                    "command_refs": ";".join(row.get("command_refs", [])),
                }
            )

    lines = [
        "# Full Source-Policy Row Provenance Audit",
        "",
        f"Status: `{result['status']}`.",
        "",
        "This read-only audit does not execute B4, v048, or heavy numerical commands.",
        "It records row-level provenance preflight only; provenance preflight is not source-policy promotion.",
        "",
        "## Summary",
        "",
        f"- Rows: `{result['row_count']}/{result['source_policy_rows_total']}`.",
        f"- Provenance preflight complete rows: `{result['provenance_preflight_complete_rows']}/{result['row_count']}`.",
        f"- Public-source-root rows: `{result['public_source_root_rows']}`.",
        f"- Unable-to-reproduce rows: `{result['source_policy_rows_unable_to_reproduce']}`.",
        f"- Attempted-not-reproducible/promoted rows: `{result['attempted_not_reproducible_rows']}/{result['source_policy_rows_promoted']}`.",
        f"- Command-mapped rows: `{result['command_mapped_rows']}`.",
        f"- Ready commands/mapped external rows: `{result['ready_command_count']}/{result['mapped_external_row_count']}`.",
        f"- Command traceability unique/traced/declared/mismatch rows: `{result['traceability_unique_rows']}/{result['traceability_reference_count']}/{result['traceability_declared_reference_count']}/{result['traceability_mismatch_count']}`.",
        f"- OC4 aliases blocker/status/closure/allowed-now: `{result['oc4_blocker_id']}/{result['oc4_blocker_status']}/{result['oc4_closure_decision']}/{result['oc4_closure_allowed_now']}`.",
        f"- OC4 ready-command and traceability aliases: `{result['ready_commands_mapped_rows']}/{result['traceability_unique_traced_declared_mismatch']}`.",
        f"- Rows with all command outputs present: `{result['rows_with_all_command_outputs_present']}`.",
        f"- Source-policy closed/promotion-ready rows: `{result['source_policy_rows_closed']}/{result['promotion_ready_rows']}`.",
        f"- Blocker/status/closure decision: `{result['blocker_id']}/{result['blocker_status']}/{result['closure_decision']}`.",
        f"- Closure allowed now / OC4 blocker open: `{result['closure_allowed_now']}/{result['oc4_blocker_open']}`.",
        f"- Source-policy execution invoked/allowed now: `{result['source_policy_execution_invoked']}/{result['source_policy_execution_allowed_now']}`.",
        f"- Action boundary safe/opt-in action counts: `{result['safe_without_b4_opt_in_count']}/{result['opt_in_required_action_count']}`.",
        f"- Required approval/driver: `{result['required_user_approval_statement']}/{result['guarded_execution_driver']}`.",
        f"- Top-level next safe action ids: `{','.join(result['next_safe_action_ids'])}`.",
        f"- Handoff authorized/commands-not-run: `{result['handoff_execution_authorized']}/{result['handoff_commands_not_run_by_handoff']}`.",
        f"- Handoff status/driver: `{source_policy_execution_handoff['status']}/{source_policy_execution_handoff['guarded_execution_driver']}`.",
        f"- Handoff exact approval: `{source_policy_execution_handoff['exact_required_user_approval_statement']}`.",
        f"- Handoff driver requires exact approval/does not authorize: `{source_policy_execution_handoff['driver_requires_exact_approval']}/{source_policy_execution_handoff['driver_does_not_authorize_execution']}`.",
        f"- Handoff opt-in commands/mapped rows/terminal unable rows: `{source_policy_execution_handoff['opt_in_required_command_count']}/{source_policy_execution_handoff['opt_in_required_mapped_external_rows']}/{source_policy_execution_handoff['terminal_unable_to_reproduce_rows']}`.",
        "",
        "## Source Roots",
        "",
        "| suite | exists | python files | digest |",
        "|---|---:|---:|---|",
    ]
    for suite_id, info in result["source_root_inventory"].items():
        lines.append(
            f"| `{suite_id}` | `{info['exists']}` | `{info['python_file_count']}` | `{info['digest']}` |"
        )
    lines.extend(
        [
            "",
            "## Suite Summary",
            "",
            "| rows | preflight | public-root | command-mapped | unable | closed | promotion-ready |",
            "|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for item in result["suite_summary"]:
        lines.append(
            f"| `{item['row_count']}` | `{item['provenance_preflight_complete_rows']}` | `{item['public_source_root_rows']}` | `{item['command_mapped_rows']}` | `{item['unable_to_reproduce_rows']}` | `{item['source_policy_closed_rows']}` | `{item['promotion_ready_rows']}` |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- `provenance_preflight_complete_is_not_source_policy_closure=True`.",
            "- `source_policy_promotion_still_requires_authorized_closeout_or_new_artifact=True`.",
            "- B4/B7 can close now under full source-policy: `False/False`.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("full_source_policy_row_provenance_audit=written")
    print(f"rows={result['row_count']}")
    print(f"provenance_preflight={result['provenance_preflight_complete_rows']}/{result['row_count']}")
    print(f"source_policy_closed={result['source_policy_rows_closed']}/{result['source_policy_rows_total']}")
    print(f"source_policy_rows_promoted={result['source_policy_rows_promoted']}")
    print(f"terminal_unable_to_reproduce_rows={result['terminal_unable_to_reproduce_rows']}")
    print(f"attempted_not_reproducible_rows={result['attempted_not_reproducible_rows']}")
    print(f"promotion_ready_rows={result['promotion_ready_rows']}")


if __name__ == "__main__":
    main()
