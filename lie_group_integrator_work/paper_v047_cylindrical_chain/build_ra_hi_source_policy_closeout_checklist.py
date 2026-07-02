#!/usr/bin/env python3
"""Build the RA/HI source-policy closeout checklist.

This is a read-only bridge between the guarded B4 execution packet and the
post-execution promotion decision. It does not run numerical experiments.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "RA_HI_SOURCE_POLICY_CLOSEOUT_CHECKLIST.json"
OUT_MD = PAPER / "RA_HI_SOURCE_POLICY_CLOSEOUT_CHECKLIST.md"


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def batch_summary(batch: dict[str, Any]) -> dict[str, Any]:
    commands = batch.get("commands", [])
    if not isinstance(commands, list):
        commands = []
    expected_outputs = [
        command.get("expected_output_after_run")
        for command in commands
        if isinstance(command, dict) and command.get("expected_output_after_run")
    ]
    expected_summaries = [
        command.get("expected_summary_after_run")
        for command in commands
        if isinstance(command, dict) and command.get("expected_summary_after_run")
    ]
    return {
        "suite_id": batch.get("suite_id"),
        "batch_id": batch.get("id"),
        "status": batch.get("status"),
        "command_count": int(batch.get("command_count") or len(commands)),
        "mapped_external_rows": int(batch.get("mapped_external_rows") or 0),
        "source_policy_1e_4_opt_in_required": bool(batch.get("source_policy_1e_4_opt_in_required")),
        "all_commands_require_allow_source_policy_1e_4": bool(
            batch.get("all_commands_require_allow_source_policy_1e_4")
        ),
        "all_commands_avoid_allow_source_policy_1e_4": bool(
            batch.get("all_commands_avoid_allow_source_policy_1e_4")
        ),
        "acceptance_contract": list(batch.get("acceptance_contract", [])),
        "command_ids": [
            command.get("id") for command in commands if isinstance(command, dict) and command.get("id")
        ],
        "expected_outputs": expected_outputs,
        "expected_summaries": expected_summaries,
    }


def row_summary(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "row_id": row.get("row_id"),
        "suite_id": row.get("suite_id"),
        "method": row.get("method"),
        "example": row.get("example"),
        "source_policy_closed": bool(row.get("source_policy_closed")),
        "external_superiority_ready": bool(row.get("external_superiority_ready")),
        "ready_to_launch_after_explicit_opt_in": bool(row.get("ready_to_launch_after_explicit_opt_in")),
        "source_policy_1e_4_opt_in_required": bool(row.get("source_policy_1e_4_opt_in_required")),
        "primary_promotion_blocker": row.get("primary_promotion_blocker"),
        "post_execution_decision": row.get("post_execution_decision"),
        "post_execution_attempt_status": row.get("post_execution_attempt_status"),
        "command_refs": list(row.get("command_refs", [])),
        "blocking_reasons": list(row.get("blocking_reasons", [])),
    }


def false_criteria(criteria: dict[str, Any]) -> list[str]:
    return [key for key, value in sorted(criteria.items()) if value is False]


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
    opt_in = read_json(PAPER / "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json")
    b4_handoff = read_json(PAPER / "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json")
    post = read_json(PAPER / "RA_HI_SOURCE_POLICY_POST_EXECUTION_ATTEMPT_CERTIFICATE.json")
    ledger = read_json(PAPER / "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.json")
    ra = read_json(PAPER / "RA2021_SOURCE_POLICY_ROW_AUDIT.json")
    hi = read_json(PAPER / "HI2022_SOURCE_POLICY_ROW_AUDIT.json")
    output_inventory = read_json(PAPER / "RA_HI_SOURCE_POLICY_OUTPUT_INVENTORY.json")

    batches = [batch_summary(batch) for batch in opt_in.get("execution_batches", [])]
    rows = [row_summary(row) for row in post.get("rows", []) if isinstance(row, dict)]
    ra_rows = [row for row in rows if row.get("suite_id") == "ra2021_absolute_coordinate"]
    hi_rows = [row for row in rows if row.get("suite_id") == "hi2022_half_implicit"]

    output: dict[str, Any] = {
        "schema": "ra-hi-source-policy-closeout-checklist-v1",
        "status": "ready_for_authorized_execution_closeout_not_executed_not_promoted",
        "read_only": True,
        "source_files": [
            "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json",
            "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json",
            "RA_HI_SOURCE_POLICY_POST_EXECUTION_ATTEMPT_CERTIFICATE.json",
            "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.json",
            "RA2021_SOURCE_POLICY_ROW_AUDIT.json",
            "HI2022_SOURCE_POLICY_ROW_AUDIT.json",
            "RA_HI_SOURCE_POLICY_OUTPUT_INVENTORY.json",
        ],
        "guarded_execution_boundary": {
            "exact_required_user_approval_statement": opt_in.get("required_user_approval_statement"),
            "explicit_user_opt_in_required_before_any_command": bool(
                opt_in.get("explicit_user_opt_in_required_before_any_command")
            ),
            "execution_invoked_by_packet": bool(opt_in.get("execution_invoked_by_packet")),
            "packet_does_not_authorize_execution": bool(opt_in.get("packet_does_not_authorize_execution")),
            "heavy_numerical_run_invoked": bool(opt_in.get("heavy_numerical_run_invoked")),
            "run_v047_invoked": bool(opt_in.get("run_v047_invoked")),
            "v048_runner_invoked": bool(opt_in.get("v048_runner_invoked")),
        },
        "ready_command_count": int(opt_in.get("ready_command_count") or 0),
        "ready_command_mapped_external_rows": int(opt_in.get("ready_command_mapped_external_rows") or 0),
        "ready_command_mapped_rows": int(opt_in.get("ready_command_mapped_external_rows") or 0),
        "source_policy_rows_total": 20,
        "source_policy_rows_completed": int(post.get("source_policy_rows_completed") or 0),
        "source_policy_rows_promoted": int(post.get("source_policy_rows_promoted") or 0),
        "external_superiority_ready_rows": int(post.get("external_superiority_ready_rows") or 0),
        "source_policy_closed": False,
        "source_policy_closed_ratio": f"{int(post.get('source_policy_rows_completed') or 0)}/20",
        "can_close_ra_hi_source_policy_rows_now": bool(
            post.get("closure_decision", {}).get("can_close_ra_hi_source_policy_rows_now")
        ),
        "can_claim_external_superiority_from_ra_hi_now": bool(
            post.get("closure_decision", {}).get("can_claim_external_superiority_from_ra_hi_now")
        ),
        "b4_can_close": False,
        "b7_can_close": False,
        "exact_approval_statement": opt_in.get("required_user_approval_statement"),
        "opt_in_required": True,
        "execution_invoked": bool(b4_handoff.get("source_policy_execution_invoked")),
        "coverage": {
            "source_policy_rows_total": 20,
            "ra2021_rows": len(ra_rows),
            "hi2022_rows": len(hi_rows),
            "ready_command_count": int(opt_in.get("ready_command_count") or 0),
            "ready_command_mapped_external_rows": int(opt_in.get("ready_command_mapped_external_rows") or 0),
            "ledger_rows_still_requiring_execution_or_promotion": int(
                ledger.get("source_policy_rows_still_requiring_execution_or_promotion") or 0
            ),
            "post_certificate_rows_still_requiring_execution_or_promotion": int(
                post.get("rows_still_requiring_execution_or_promotion") or 0
            ),
            "source_policy_rows_promoted": int(post.get("source_policy_rows_promoted") or 0),
            "source_policy_rows_completed": int(post.get("source_policy_rows_completed") or 0),
            "external_superiority_ready_rows": int(post.get("external_superiority_ready_rows") or 0),
            "output_inventory_status": output_inventory.get("status"),
            "output_inventory_command_count": output_inventory.get("coverage", {}).get("command_count"),
            "output_inventory_expected_outputs_existing": output_inventory.get("coverage", {}).get(
                "expected_output_existing_count"
            ),
            "output_inventory_expected_summaries_existing": output_inventory.get("coverage", {}).get(
                "expected_summary_existing_count"
            ),
            "output_inventory_csv_data_rows": output_inventory.get("coverage", {}).get(
                "expected_output_csv_data_rows"
            ),
            "output_inventory_source_policy_rows_closed": output_inventory.get("coverage", {}).get(
                "source_policy_rows_closed_by_inventory"
            ),
        },
        "execution_batches": batches,
        "suite_closeout": {
            "ra2021_absolute_coordinate": {
                "row_count": len(ra_rows),
                "command_count": next(
                    (batch["command_count"] for batch in batches if batch["suite_id"] == "ra2021_absolute_coordinate"),
                    0,
                ),
                "source_policy_1e_4_opt_in_required": True,
                "current_status": ra.get("status"),
                "false_closure_criteria": false_criteria(ra.get("closure_criteria", {})),
                "primary_promotion_blocker_counts": {
                    key: value
                    for key, value in post.get("primary_promotion_blocker_counts", {}).items()
                    if key.startswith("ra2021_")
                },
                "closeout_requirements": [
                    "authorized RA2021 commands must include --allow-source-policy-1e-4",
                    "local Gauss6/FullVA rows must use the RA2021 source time grid and output norm",
                    "error/order rows and runtime/Newton metrics must be bound to the same promoted rows",
                    "single, double, four-link, and slider-crank rows must be promoted or explicitly remain demoted",
                ],
            },
            "hi2022_half_implicit": {
                "row_count": len(hi_rows),
                "command_count": next(
                    (batch["command_count"] for batch in batches if batch["suite_id"] == "hi2022_half_implicit"),
                    0,
                ),
                "source_policy_1e_4_opt_in_required": False,
                "current_status": hi.get("status"),
                "false_closure_criteria": false_criteria(hi.get("closure_criteria", {})),
                "primary_promotion_blocker_counts": {
                    key: value
                    for key, value in post.get("primary_promotion_blocker_counts", {}).items()
                    if key.startswith("hi2022_")
                },
                "partial_or_failed_shards": list(
                    hi.get("t8_selected_candidate_matrix_preflight", {}).get("partial_or_failed_shards", [])
                ),
                "closeout_requirements": [
                    "full T=8 public-policy step/reference grid must be selected and documented",
                    "selected coarse-trio shards cannot be promoted as a full public grid",
                    "rA_half double-pendulum failure must be repaired or the row family must stay demoted",
                    "runtime/error/order rows must be bound before any B4/B7 work-precision closure",
                ],
            },
        },
        "rows": rows,
        "post_execution_promotion_requirements": list(opt_in.get("post_execution_promotion_requirements", [])),
        "not_promoted_disposition": {
            "can_close_ra_hi_source_policy_rows_now": bool(
                post.get("closure_decision", {}).get("can_close_ra_hi_source_policy_rows_now")
            ),
            "can_claim_external_superiority_from_ra_hi_now": bool(
                post.get("closure_decision", {}).get("can_claim_external_superiority_from_ra_hi_now")
            ),
            "source_policy_closed_rows_after_this_checklist": 0,
            "b4_can_close_from_this_checklist": False,
            "b7_can_close_from_this_checklist": False,
        },
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
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# RA/HI Source-Policy Closeout Checklist",
        "",
        f"Status: `{output['status']}`.",
        "",
        "This read-only checklist does not run guarded source-policy commands.",
        "",
        f"- Rows: RA2021 `{len(ra_rows)}`, HI2022 `{len(hi_rows)}`, total `{output['coverage']['source_policy_rows_total']}`.",
        f"- Ready commands: `{output['coverage']['ready_command_count']}` mapped to `{output['coverage']['ready_command_mapped_external_rows']}` rows.",
        f"- Output inventory: `{output['coverage']['output_inventory_status']}`; outputs/summaries/data rows `{output['coverage']['output_inventory_expected_outputs_existing']}/{output['coverage']['output_inventory_expected_summaries_existing']}/{output['coverage']['output_inventory_csv_data_rows']}`; source-policy rows closed `{output['coverage']['output_inventory_source_policy_rows_closed']}`.",
        f"- Source-policy closed/ratio: `{output['source_policy_closed']}/{output['source_policy_closed_ratio']}`.",
        f"- Promoted/completed/external-ready rows now: `{output['coverage']['source_policy_rows_promoted']}`/`{output['coverage']['source_policy_rows_completed']}`/`{output['coverage']['external_superiority_ready_rows']}`.",
        f"- Exact authorization phrase: `{output['guarded_execution_boundary']['exact_required_user_approval_statement']}`.",
        f"- Source-policy execution allowed now/invoked/exact opt-in required: `{output['source_policy_execution_allowed_now']}/{output['source_policy_execution_invoked']}/{output['exact_b4_opt_in_required_for_execution']}`.",
        f"- Safe action ids: `{output['safe_action_ids']}`; opt-in action ids: `{output['opt_in_action_ids']}`.",
        f"- Source-policy execution handoff exact approval/driver: `{output['source_policy_execution_handoff']['exact_required_user_approval_statement']}/{output['source_policy_execution_handoff']['guarded_execution_driver']}/{output['source_policy_execution_handoff']['driver_requires_exact_approval']}/{output['source_policy_execution_handoff']['driver_does_not_authorize_execution']}/{output['source_policy_execution_handoff']['opt_in_required_command_count']}/{output['source_policy_execution_handoff']['opt_in_required_mapped_external_rows']}/{output['source_policy_execution_handoff']['terminal_unable_to_reproduce_rows']}`.",
        f"- Source-policy execution handoff authorized/commands-not-run: `{output['source_policy_execution_handoff']['execution_authorized']}/{output['source_policy_execution_handoff']['commands_not_run_by_handoff']}`.",
        "",
        "| suite | rows | commands | 1e-4 opt-in | status | unresolved criteria |",
        "|---|---:|---:|---:|---|---|",
    ]
    for suite_id, suite in output["suite_closeout"].items():
        unresolved = ", ".join(suite["false_closure_criteria"]) or "none"
        lines.append(
            f"| `{suite_id}` | `{suite['row_count']}` | `{suite['command_count']}` | "
            f"`{suite['source_policy_1e_4_opt_in_required']}` | `{suite['current_status']}` | {unresolved} |"
        )
    lines.extend(
        [
            "",
            "Post-execution promotion requirements:",
        ]
    )
    for item in output["post_execution_promotion_requirements"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            f"Closeout now: rows `{output['not_promoted_disposition']['source_policy_closed_rows_after_this_checklist']}/20`, B4/B7 `{output['not_promoted_disposition']['b4_can_close_from_this_checklist']}/{output['not_promoted_disposition']['b7_can_close_from_this_checklist']}`.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("ra_hi_source_policy_closeout_checklist=written")
    print(f"rows={len(rows)}")
    print(f"ra_hi={len(ra_rows)}/{len(hi_rows)}")
    print(f"ready_commands={output['coverage']['ready_command_count']}")
    print("source_policy_closed=0/20")
    print(f"source_policy_execution_allowed_now={output['source_policy_execution_allowed_now']}")
    print(f"source_policy_execution_invoked={output['source_policy_execution_invoked']}")


if __name__ == "__main__":
    main()
