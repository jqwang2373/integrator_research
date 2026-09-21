#!/usr/bin/env python3
"""Build a RA/HI-only source-policy promotion blocker matrix.

This artifact is deliberately narrower than the all-suite B4 ledger: it only
covers the 20 RA2021/HI2022 rows that have public source roots and existing
candidate outputs, but are still not promotable as source-policy evidence.
It does not run any guarded source-policy command.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "RA_HI_SOURCE_POLICY_PROMOTION_BLOCKER_MATRIX.json"
OUT_MD = PAPER / "RA_HI_SOURCE_POLICY_PROMOTION_BLOCKER_MATRIX.md"
OUT_CSV = PAPER / "RA_HI_SOURCE_POLICY_PROMOTION_BLOCKER_MATRIX.csv"
RA_HI_SUITES = {"ra2021_absolute_coordinate", "hi2022_half_implicit"}


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def count_by(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        value = str(row.get(key))
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def command_inventory_map(inventory: dict[str, Any]) -> dict[str, dict[str, Any]]:
    commands = inventory.get("commands", [])
    result: dict[str, dict[str, Any]] = {}
    if not isinstance(commands, list):
        return result
    for command in commands:
        if isinstance(command, dict) and isinstance(command.get("command_id"), str):
            result[command["command_id"]] = command
    return result


def post_attempt_map(post_attempt: dict[str, Any]) -> dict[tuple[str, str, str], dict[str, Any]]:
    rows = post_attempt.get("rows", [])
    result: dict[tuple[str, str, str], dict[str, Any]] = {}
    if not isinstance(rows, list):
        return result
    for row in rows:
        if not isinstance(row, dict):
            continue
        key = (str(row.get("suite_id")), str(row.get("method")), str(row.get("example")))
        result[key] = row
    return result


def command_statuses(command_refs: list[str], commands: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    statuses: list[dict[str, Any]] = []
    for ref in command_refs:
        command = commands.get(ref, {})
        expected_output = command.get("expected_output", {}) if isinstance(command.get("expected_output"), dict) else {}
        expected_summary = (
            command.get("expected_summary", {}) if isinstance(command.get("expected_summary"), dict) else {}
        )
        statuses.append(
            {
                "command_id": ref,
                "inventory_status": command.get("artifact_status", "missing_from_inventory"),
                "output_exists": bool(expected_output.get("exists")),
                "output_nonempty": bool(expected_output.get("nonempty")),
                "summary_exists": bool(expected_summary.get("exists")),
                "summary_nonempty": bool(expected_summary.get("nonempty")),
            }
        )
    return statuses


def suite_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for suite_id in sorted(RA_HI_SUITES):
        suite_rows = [row for row in rows if row["suite_id"] == suite_id]
        result.append(
            {
                "suite_id": suite_id,
                "row_count": len(suite_rows),
                "source_policy_closed_rows": sum(1 for row in suite_rows if row["source_policy_closed"]),
                "promoted_rows": sum(1 for row in suite_rows if row["post_execution_decision"] != "not_promoted"),
                "not_promoted_rows": sum(1 for row in suite_rows if row["post_execution_decision"] == "not_promoted"),
                "source_policy_1e_4_opt_in_required_rows": sum(
                    1 for row in suite_rows if row["source_policy_1e_4_opt_in_required"]
                ),
                "current_evidence_terminal_not_promotable_rows": sum(
                    1 for row in suite_rows if row["current_evidence_terminal_not_promotable"]
                ),
                "future_promotion_requires_authorized_execution_or_new_artifact_rows": sum(
                    1
                    for row in suite_rows
                    if row["future_promotion_requires_authorized_execution_or_new_artifact"]
                ),
                "source_policy_reproduction_complete_rows": sum(
                    1 for row in suite_rows if row["source_policy_reproduction_complete"]
                ),
                "command_mapped_rows": sum(1 for row in suite_rows if row["command_refs"]),
                "command_output_present_rows": sum(1 for row in suite_rows if row["all_command_outputs_present"]),
                "blocker_counts": count_by(suite_rows, "primary_promotion_blocker"),
                "attempt_status_counts": count_by(suite_rows, "post_execution_attempt_status"),
            }
        )
    return result


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


def main() -> None:
    b4 = read_json(PAPER / "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.json")
    post_attempt = read_json(PAPER / "RA_HI_SOURCE_POLICY_POST_EXECUTION_ATTEMPT_CERTIFICATE.json")
    closeout = read_json(PAPER / "RA_HI_SOURCE_POLICY_CLOSEOUT_CHECKLIST.json")
    output_inventory = read_json(PAPER / "RA_HI_SOURCE_POLICY_OUTPUT_INVENTORY.json")
    opt_in = read_json(PAPER / "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json")
    b4_handoff = read_json(PAPER / "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json")

    post_rows = post_attempt_map(post_attempt)
    command_map = command_inventory_map(output_inventory)
    rows: list[dict[str, Any]] = []
    for source_row in b4.get("rows", []):
        if not isinstance(source_row, dict) or source_row.get("suite_id") not in RA_HI_SUITES:
            continue
        key = (
            str(source_row.get("suite_id")),
            str(source_row.get("method")),
            str(source_row.get("example")),
        )
        row_id = source_row.get("row_id") or ":".join(key)
        post_row = post_rows.get(key, {})
        refs = [str(item) for item in source_row.get("command_refs", [])]
        inventory_statuses = command_statuses(refs, command_map)
        all_outputs_present = bool(refs) and all(
            item["output_exists"] and item["output_nonempty"] for item in inventory_statuses
        )
        rows.append(
            {
                "row_id": row_id,
                "source_lane_id": source_row.get("lane_id"),
                "suite_id": source_row.get("suite_id"),
                "method": source_row.get("method"),
                "example": source_row.get("example"),
                "public_source_root_available": True,
                "no_public_code_case": False,
                "source_policy_disposition": source_row.get("source_policy_disposition"),
                "readiness_status": source_row.get("readiness_status"),
                "post_execution_attempt_status": post_row.get(
                    "post_execution_attempt_status", source_row.get("readiness_status")
                ),
                "post_execution_decision": source_row.get("post_execution_decision"),
                "source_policy_closed": bool(source_row.get("source_policy_closed")),
                "source_policy_reproduction_complete": False,
                "external_superiority_ready": bool(source_row.get("external_superiority_ready")),
                "counts_as_open_execution_queue": bool(source_row.get("counts_as_open_execution_queue")),
                "ready_to_launch_after_explicit_opt_in": bool(
                    source_row.get("ready_to_launch_after_explicit_opt_in")
                ),
                "source_policy_1e_4_opt_in_required": bool(source_row.get("source_policy_1e_4_opt_in_required")),
                "command_refs": refs,
                "command_inventory_statuses": inventory_statuses,
                "all_command_outputs_present": all_outputs_present,
                "current_evidence_terminal_not_promotable": True,
                "current_evidence_disposition": "terminal_current_evidence_not_promotable",
                "existing_attempt_output_present_not_promotion_evidence": all_outputs_present,
                "future_promotion_requires_authorized_execution_or_new_artifact": True,
                "future_promotion_reopen_condition": (
                    "exact_b4_opt_in_authorized_execution_closeout_or_new_source_policy_promotion_artifact"
                ),
                "command_artifact_statuses": source_row.get("command_artifact_statuses", []),
                "primary_promotion_blocker": source_row.get("primary_promotion_blocker"),
                "promotion_evidence_ref": source_row.get("promotion_evidence_ref"),
                "blocking_reasons": source_row.get("blocking_reasons", []),
                "safe_current_action": "keep_not_promoted_until_source_policy_promotion_or_authorized_execution_closeout",
            }
        )

    rows.sort(key=lambda row: (row["suite_id"], row["method"], row["example"]))
    summary = suite_summary(rows)
    source_policy_rows_closed = sum(1 for row in rows if row["source_policy_closed"])
    source_policy_rows_promoted = sum(1 for row in rows if row["post_execution_decision"] != "not_promoted")
    source_policy_rows_not_promoted = sum(
        1 for row in rows if row["post_execution_decision"] == "not_promoted"
    )
    source_policy_reproduction_complete_rows = sum(
        1 for row in rows if row["source_policy_reproduction_complete"]
    )
    attempted_not_reproducible_rows = sum(
        1 for row in rows if row["source_policy_disposition"] == "attempted_not_reproducible"
    )
    command_mapped_rows = sum(1 for row in rows if row["command_refs"])
    rows_with_all_command_outputs_present = sum(1 for row in rows if row["all_command_outputs_present"])
    output: dict[str, Any] = {
        "schema": "ra-hi-source-policy-promotion-blocker-matrix-v1",
        "status": "ra_hi_public_root_rows_not_promoted_source_policy_open",
        "read_only": True,
        "source_files": [
            "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.json",
            "RA_HI_SOURCE_POLICY_POST_EXECUTION_ATTEMPT_CERTIFICATE.json",
            "RA_HI_SOURCE_POLICY_CLOSEOUT_CHECKLIST.json",
            "RA_HI_SOURCE_POLICY_OUTPUT_INVENTORY.json",
            "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json",
            "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json",
        ],
        "row_count": len(rows),
        "source_policy_closed": source_policy_rows_closed == len(rows) and bool(rows),
        "source_policy_closed_ratio": f"{source_policy_rows_closed}/{len(rows)}",
        "source_policy_reproduction_complete": source_policy_reproduction_complete_rows == len(rows) and bool(rows),
        "promoted": source_policy_rows_promoted,
        "not_promoted": source_policy_rows_not_promoted,
        "attempted_not_reproducible": attempted_not_reproducible_rows,
        "command_mapped_output_present": (
            f"{command_mapped_rows}/{rows_with_all_command_outputs_present}"
        ),
        "command_mapped_output_present_rows": rows_with_all_command_outputs_present,
        "all_command_mapped_outputs_present": (
            command_mapped_rows == rows_with_all_command_outputs_present == len(rows) and bool(rows)
        ),
        "ra2021_row_count": sum(1 for row in rows if row["suite_id"] == "ra2021_absolute_coordinate"),
        "hi2022_row_count": sum(1 for row in rows if row["suite_id"] == "hi2022_half_implicit"),
        "public_source_root_available_rows": sum(1 for row in rows if row["public_source_root_available"]),
        "no_public_code_rows_included": sum(1 for row in rows if row["no_public_code_case"]),
        "source_policy_rows_closed": source_policy_rows_closed,
        "source_policy_rows_promoted": source_policy_rows_promoted,
        "source_policy_rows_not_promoted": source_policy_rows_not_promoted,
        "source_policy_rows_still_requiring_execution_or_promotion": sum(
            1 for row in rows if row["counts_as_open_execution_queue"]
        ),
        "current_evidence_terminal_not_promotable_rows": sum(
            1 for row in rows if row["current_evidence_terminal_not_promotable"]
        ),
        "future_promotion_requires_authorized_execution_or_new_artifact_rows": sum(
            1 for row in rows if row["future_promotion_requires_authorized_execution_or_new_artifact"]
        ),
        "source_policy_reproduction_complete_rows": source_policy_reproduction_complete_rows,
        "attempted_not_reproducible_rows": attempted_not_reproducible_rows,
        "command_mapped_rows": command_mapped_rows,
        "rows_with_all_command_outputs_present": rows_with_all_command_outputs_present,
        "ready_to_launch_after_explicit_opt_in_rows": sum(
            1 for row in rows if row["ready_to_launch_after_explicit_opt_in"]
        ),
        "source_policy_1e_4_opt_in_required_rows": sum(
            1 for row in rows if row["source_policy_1e_4_opt_in_required"]
        ),
        "post_execution_decision_counts": count_by(rows, "post_execution_decision"),
        "post_execution_attempt_status_counts": count_by(rows, "post_execution_attempt_status"),
        "primary_promotion_blocker_counts": count_by(rows, "primary_promotion_blocker"),
        "output_inventory_status": output_inventory.get("status"),
        "output_inventory_command_count": output_inventory.get("coverage", {}).get("command_count"),
        "output_inventory_outputs_existing": output_inventory.get("coverage", {}).get("expected_output_existing_count"),
        "output_inventory_closed_rows": output_inventory.get("coverage", {}).get("source_policy_rows_closed_by_inventory"),
        "closeout_status": closeout.get("status"),
        "closeout_exact_opt_in_required": closeout.get("guarded_execution_boundary", {}).get(
            "required_user_approval_statement",
            opt_in.get("required_user_approval_statement"),
        ),
        "closeout_execution_invoked": bool(closeout.get("guarded_execution_boundary", {}).get("execution_invoked")),
        "b4_can_close_now": False,
        "b7_can_close_now": False,
        "external_superiority_ready_rows": 0,
        "heavy_numerical_run_invoked": False,
        "run_v047_invoked": False,
        "v048_runner_invoked": False,
        "source_policy_execution_handoff": handoff_summary(b4_handoff),
        "source_policy_execution_allowed_now": b4_handoff.get("source_policy_execution_allowed_now"),
        "source_policy_execution_invoked": b4_handoff.get("source_policy_execution_invoked"),
        "exact_b4_opt_in_required_for_execution": b4_handoff.get(
            "exact_b4_opt_in_required_for_execution"
        ),
        "safe_action_ids": b4_handoff.get("safe_action_ids"),
        "opt_in_action_ids": b4_handoff.get("opt_in_action_ids"),
        "required_user_approval_statement": (
            b4_handoff.get("required_user_approval_statement")
            or b4_handoff.get("exact_approval_statement")
            or b4_handoff.get("opt_in_required_phrase")
        ),
        "guarded_execution_driver": b4_handoff.get("guarded_execution_driver"),
        "suite_summary": summary,
        "rows": rows,
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, sort_keys=True)
        handle.write("\n")

    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "suite_id",
                "method",
                "example",
                "readiness_status",
                "post_execution_attempt_status",
                "post_execution_decision",
                "primary_promotion_blocker",
                "promotion_evidence_ref",
                "source_policy_1e_4_opt_in_required",
                "current_evidence_terminal_not_promotable",
                "future_promotion_requires_authorized_execution_or_new_artifact",
                "command_ref_count",
                "all_command_outputs_present",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "suite_id": row["suite_id"],
                    "method": row["method"],
                    "example": row["example"],
                    "readiness_status": row["readiness_status"],
                    "post_execution_attempt_status": row["post_execution_attempt_status"],
                    "post_execution_decision": row["post_execution_decision"],
                    "primary_promotion_blocker": row["primary_promotion_blocker"],
                    "promotion_evidence_ref": row["promotion_evidence_ref"],
                    "source_policy_1e_4_opt_in_required": row["source_policy_1e_4_opt_in_required"],
                    "current_evidence_terminal_not_promotable": row[
                        "current_evidence_terminal_not_promotable"
                    ],
                    "future_promotion_requires_authorized_execution_or_new_artifact": row[
                        "future_promotion_requires_authorized_execution_or_new_artifact"
                    ],
                    "command_ref_count": len(row["command_refs"]),
                    "all_command_outputs_present": row["all_command_outputs_present"],
                }
            )

    lines = [
        "# RA/HI Source-Policy Promotion Blocker Matrix",
        "",
        f"Status: `{output['status']}`.",
        "",
        "This is a read-only RA2021/HI2022 matrix. It excludes TFE/VP no-public-code rows and does not run guarded source-policy commands.",
        "",
        f"- Rows: `{output['row_count']}`; RA/HI `{output['ra2021_row_count']}/{output['hi2022_row_count']}`.",
        f"- Public-source-root rows: `{output['public_source_root_available_rows']}`.",
        f"- No-public-code rows included: `{output['no_public_code_rows_included']}`.",
        f"- Direct aliases source-policy-closed/ratio/reproduction-complete: `{output['source_policy_closed']}/{output['source_policy_closed_ratio']}/{output['source_policy_reproduction_complete']}`.",
        f"- Direct aliases promoted/not-promoted/attempted-not-reproducible: `{output['promoted']}/{output['not_promoted']}/{output['attempted_not_reproducible']}`.",
        f"- Direct alias command-mapped/output-present: `{output['command_mapped_output_present']}`; all present: `{output['all_command_mapped_outputs_present']}`.",
        f"- Source-policy rows closed/promoted/not-promoted: `{output['source_policy_rows_closed']}/{output['source_policy_rows_promoted']}/{output['source_policy_rows_not_promoted']}`.",
        f"- Still requiring execution or promotion: `{output['source_policy_rows_still_requiring_execution_or_promotion']}`.",
        f"- Current-evidence terminal/not-promotable rows: `{output['current_evidence_terminal_not_promotable_rows']}`.",
        f"- Future promotion requires authorized execution or new artifact rows: `{output['future_promotion_requires_authorized_execution_or_new_artifact_rows']}`.",
        f"- Source-policy reproduction complete rows: `{output['source_policy_reproduction_complete_rows']}`.",
        f"- Attempted-not-reproducible rows: `{output['attempted_not_reproducible_rows']}`.",
        f"- Command-mapped/output-present rows: `{output['command_mapped_rows']}/{output['rows_with_all_command_outputs_present']}`.",
        f"- Ready after exact opt-in rows: `{output['ready_to_launch_after_explicit_opt_in_rows']}`.",
        f"- Rows requiring explicit `1e-4` opt-in: `{output['source_policy_1e_4_opt_in_required_rows']}`.",
        f"- Source-policy execution allowed now/invoked/exact opt-in required: `{output['source_policy_execution_allowed_now']}/{output['source_policy_execution_invoked']}/{output['exact_b4_opt_in_required_for_execution']}`.",
        f"- Safe action ids: `{output['safe_action_ids']}`; opt-in action ids: `{output['opt_in_action_ids']}`.",
        f"- Post-execution decision counts: `{output['post_execution_decision_counts']}`.",
        f"- Attempt status counts: `{output['post_execution_attempt_status_counts']}`.",
        f"- Primary blocker counts: `{output['primary_promotion_blocker_counts']}`.",
        f"- Output inventory status/commands/outputs/closed: `{output['output_inventory_status']}` / `{output['output_inventory_command_count']}` / `{output['output_inventory_outputs_existing']}` / `{output['output_inventory_closed_rows']}`.",
        f"- Closeout status: `{output['closeout_status']}`.",
        f"- Source-policy execution handoff exact approval/driver: `{output['source_policy_execution_handoff']['exact_required_user_approval_statement']}/{output['source_policy_execution_handoff']['guarded_execution_driver']}/{output['source_policy_execution_handoff']['driver_requires_exact_approval']}/{output['source_policy_execution_handoff']['driver_does_not_authorize_execution']}/{output['source_policy_execution_handoff']['opt_in_required_command_count']}/{output['source_policy_execution_handoff']['opt_in_required_mapped_external_rows']}/{output['source_policy_execution_handoff']['terminal_unable_to_reproduce_rows']}`.",
        f"- Source-policy execution handoff authorized/commands-not-run: `{output['source_policy_execution_handoff']['execution_authorized']}/{output['source_policy_execution_handoff']['commands_not_run_by_handoff']}`.",
        f"- B4/B7 can close now: `{output['b4_can_close_now']}/{output['b7_can_close_now']}`.",
        f"- Heavy/run_v047/v048 invoked: `{output['heavy_numerical_run_invoked']}/{output['run_v047_invoked']}/{output['v048_runner_invoked']}`.",
        "",
        "## Suite Summary",
        "",
        "| suite | rows | closed | not promoted | terminal current evidence | future authorization/new artifact | command mapped | output present | 1e-4 opt-in rows |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in summary:
        lines.append(
            f"| `{item['suite_id']}` | `{item['row_count']}` | `{item['source_policy_closed_rows']}` | "
            f"`{item['not_promoted_rows']}` | `{item['current_evidence_terminal_not_promotable_rows']}` | "
            f"`{item['future_promotion_requires_authorized_execution_or_new_artifact_rows']}` | "
            f"`{item['command_mapped_rows']}` | "
            f"`{item['command_output_present_rows']}` | `{item['source_policy_1e_4_opt_in_required_rows']}` |"
        )
    lines.extend(
        [
            "",
            "## Rows",
            "",
            "| suite | method | example | attempt status | blocker | evidence | commands |",
            "|---|---|---|---|---|---|---:|",
        ]
    )
    for row in rows:
        lines.append(
            f"| `{row['suite_id']}` | `{row['method']}` | `{row['example']}` | "
            f"`{row['post_execution_attempt_status']}` | `{row['primary_promotion_blocker']}` | "
            f"`{row['promotion_evidence_ref']}` | `{len(row['command_refs'])}` |"
        )
    lines.extend(
        [
            "",
            "Reading rule: these rows are public-root rows with existing diagnostic or candidate outputs, not no-public-code rows. Current evidence is terminal/not-promotable for all 20 rows, while source-policy reproduction remains incomplete. Future promotion requires either the exact B4 opt-in authorized execution closeout or a new source-policy promotion artifact.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("ra_hi_source_policy_promotion_blocker_matrix=written")
    print(f"rows={output['row_count']}")
    print(f"source_policy_closed={output['source_policy_rows_closed']}/{output['row_count']}")
    print(f"source_policy_closed_alias={output['source_policy_closed']}")
    print(f"not_promoted={output['source_policy_rows_not_promoted']}")
    print(f"attempted_not_reproducible={output['attempted_not_reproducible_rows']}")
    print(f"command_mapped_output_present={output['command_mapped_output_present']}")
    print(f"source_policy_execution_allowed_now={output['source_policy_execution_allowed_now']}")
    print(f"source_policy_execution_invoked={output['source_policy_execution_invoked']}")


if __name__ == "__main__":
    main()
