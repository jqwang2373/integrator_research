#!/usr/bin/env python3
"""Build a read-only inventory of RA/HI source-policy output artifacts."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
OUT_JSON = PAPER / "RA_HI_SOURCE_POLICY_OUTPUT_INVENTORY.json"
OUT_MD = PAPER / "RA_HI_SOURCE_POLICY_OUTPUT_INVENTORY.md"


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def resolve_artifact(path_text: str | None) -> Path | None:
    if not path_text:
        return None
    path = Path(path_text)
    if path.is_absolute():
        return path
    return (manuscript_path(path)).resolve()


def rel(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return path.relative_to(PAPER).as_posix()
    except ValueError:
        return path.as_posix()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def csv_snapshot(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {"path": None, "exists": False, "nonempty": False}
    exists = path.exists()
    output: dict[str, Any] = {
        "path": rel(path),
        "exists": exists,
        "nonempty": exists and path.stat().st_size > 0,
    }
    if not exists:
        return output
    output["bytes"] = path.stat().st_size
    output["sha256"] = sha256(path)
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    header = list(rows[0].keys()) if rows else []
    output["csv_data_rows"] = len(rows)
    output["csv_header"] = header
    if "status" in header:
        counts: dict[str, int] = {}
        for row in rows:
            status = row.get("status") or ""
            counts[status] = counts.get(status, 0) + 1
        output["csv_status_counts"] = counts
    if "ok" in header:
        output["csv_ok_true_rows"] = sum(1 for row in rows if str(row.get("ok")).lower() == "true")
    return output


def json_snapshot(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {"path": None, "exists": False, "nonempty": False}
    exists = path.exists()
    output: dict[str, Any] = {
        "path": rel(path),
        "exists": exists,
        "nonempty": exists and path.stat().st_size > 0,
    }
    if not exists:
        return output
    data = read_json(path)
    output["bytes"] = path.stat().st_size
    output["sha256"] = sha256(path)
    for key in [
        "status",
        "row_count",
        "ok_row_count",
        "source_policy_rows_closed_by_this_evidence",
        "promotion_ready",
        "full_public_grid_selected",
        "selected_coarse_trio",
    ]:
        if key in data:
            output[key] = data.get(key)
    return output


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
    packet = read_json(PAPER / "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json")
    b4_handoff = read_json(PAPER / "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json")
    commands: list[dict[str, Any]] = []
    for batch in packet.get("execution_batches", []):
        if not isinstance(batch, dict):
            continue
        for command in batch.get("commands", []):
            if not isinstance(command, dict):
                continue
            output_path = resolve_artifact(command.get("expected_output_after_run"))
            summary_path = resolve_artifact(command.get("expected_summary_after_run"))
            commands.append(
                {
                    "suite_id": batch.get("suite_id"),
                    "batch_id": batch.get("id"),
                    "command_id": command.get("id"),
                    "artifact_status": command.get("artifact_status"),
                    "mapped_row_count": int(command.get("mapped_row_count") or 0),
                    "expected_output": csv_snapshot(output_path),
                    "expected_summary": json_snapshot(summary_path),
                    "source_policy_1e_4_opt_in_required": bool(batch.get("source_policy_1e_4_opt_in_required")),
                }
            )

    output_entries = [item["expected_output"] for item in commands]
    summary_entries = [
        item["expected_summary"] for item in commands if item["expected_summary"].get("path") is not None
    ]
    suite_counts: dict[str, int] = {}
    for item in commands:
        suite = str(item.get("suite_id"))
        suite_counts[suite] = suite_counts.get(suite, 0) + 1
    hi_summary_ok_rows = sum(int(item.get("ok_row_count") or 0) for item in summary_entries)
    hi_summary_closed_rows = sum(
        int(item.get("source_policy_rows_closed_by_this_evidence") or 0) for item in summary_entries
    )
    summary_promotion_ready_count = sum(1 for item in summary_entries if item.get("promotion_ready") is True)
    full_public_grid_summary_count = sum(1 for item in summary_entries if item.get("full_public_grid_selected") is True)
    selected_coarse_trio_summary_count = sum(1 for item in summary_entries if item.get("selected_coarse_trio") is True)

    inventory: dict[str, Any] = {
        "schema": "ra-hi-source-policy-output-inventory-v1",
        "status": "existing_expected_outputs_present_not_promotion_evidence",
        "read_only": True,
        "source_files": [
            "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json",
            "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json",
        ],
        "guarded_execution_boundary": {
            "execution_invoked_by_packet": bool(packet.get("execution_invoked_by_packet")),
            "explicit_user_opt_in_required_before_any_command": bool(
                packet.get("explicit_user_opt_in_required_before_any_command")
            ),
            "heavy_numerical_run_invoked": bool(packet.get("heavy_numerical_run_invoked")),
            "run_v047_invoked": bool(packet.get("run_v047_invoked")),
            "v048_runner_invoked": bool(packet.get("v048_runner_invoked")),
        },
        "coverage": {
            "command_count": len(commands),
            "suite_command_counts": suite_counts,
            "mapped_external_rows": int(packet.get("ready_command_mapped_external_rows") or 0),
            "expected_output_count": len(output_entries),
            "expected_output_existing_count": sum(1 for item in output_entries if item.get("exists") is True),
            "expected_output_nonempty_count": sum(1 for item in output_entries if item.get("nonempty") is True),
            "expected_output_csv_data_rows": sum(int(item.get("csv_data_rows") or 0) for item in output_entries),
            "expected_summary_count": len(summary_entries),
            "expected_summary_existing_count": sum(1 for item in summary_entries if item.get("exists") is True),
            "expected_summary_nonempty_count": sum(1 for item in summary_entries if item.get("nonempty") is True),
            "hi2022_summary_ok_rows": hi_summary_ok_rows,
            "hi2022_summary_closed_rows": hi_summary_closed_rows,
            "summary_promotion_ready_count": summary_promotion_ready_count,
            "full_public_grid_summary_count": full_public_grid_summary_count,
            "selected_coarse_trio_summary_count": selected_coarse_trio_summary_count,
            "source_policy_rows_closed_by_inventory": 0,
            "accepted_for_promotion": False,
        },
        "commands": commands,
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
        json.dump(inventory, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# RA/HI Source-Policy Output Inventory",
        "",
        f"Status: `{inventory['status']}`.",
        "",
        "This read-only inventory hashes and counts the expected RA/HI output artifacts. It does not run guarded commands and does not promote rows.",
        "",
        f"- Commands/outputs/summaries: `{len(commands)}`/`{inventory['coverage']['expected_output_existing_count']}`/`{inventory['coverage']['expected_summary_existing_count']}`.",
        f"- CSV data rows: `{inventory['coverage']['expected_output_csv_data_rows']}`.",
        f"- HI2022 summary ok/closed rows: `{hi_summary_ok_rows}`/`{hi_summary_closed_rows}`.",
        f"- Promotion-ready/full-grid/coarse-trio summaries: `{summary_promotion_ready_count}`/`{full_public_grid_summary_count}`/`{selected_coarse_trio_summary_count}`.",
        f"- Source-policy rows closed by inventory: `{inventory['coverage']['source_policy_rows_closed_by_inventory']}`.",
        f"- Source-policy execution allowed now/invoked/exact opt-in required: `{inventory['source_policy_execution_allowed_now']}/{inventory['source_policy_execution_invoked']}/{inventory['exact_b4_opt_in_required_for_execution']}`.",
        f"- Safe action ids: `{inventory['safe_action_ids']}`; opt-in action ids: `{inventory['opt_in_action_ids']}`.",
        f"- Source-policy execution handoff exact approval/driver: `{inventory['source_policy_execution_handoff']['exact_required_user_approval_statement']}/{inventory['source_policy_execution_handoff']['guarded_execution_driver']}/{inventory['source_policy_execution_handoff']['driver_requires_exact_approval']}/{inventory['source_policy_execution_handoff']['driver_does_not_authorize_execution']}/{inventory['source_policy_execution_handoff']['opt_in_required_command_count']}/{inventory['source_policy_execution_handoff']['opt_in_required_mapped_external_rows']}/{inventory['source_policy_execution_handoff']['terminal_unable_to_reproduce_rows']}`.",
        f"- Source-policy execution handoff authorized/commands-not-run: `{inventory['source_policy_execution_handoff']['execution_authorized']}/{inventory['source_policy_execution_handoff']['commands_not_run_by_handoff']}`.",
        "",
        "| suite | command | output rows | summary status |",
        "|---|---|---:|---|",
    ]
    for item in commands:
        summary_status = item["expected_summary"].get("status") or "none"
        lines.append(
            f"| `{item['suite_id']}` | `{item['command_id']}` | "
            f"`{item['expected_output'].get('csv_data_rows', 0)}` | `{summary_status}` |"
        )
    lines.append("")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("ra_hi_source_policy_output_inventory=written")
    print(f"commands={len(commands)}")
    print(f"outputs={inventory['coverage']['expected_output_existing_count']}/{len(output_entries)}")
    print(f"summaries={inventory['coverage']['expected_summary_existing_count']}/{len(summary_entries)}")
    print(f"csv_data_rows={inventory['coverage']['expected_output_csv_data_rows']}")
    print("source_policy_closed=0")
    print(f"source_policy_execution_allowed_now={inventory['source_policy_execution_allowed_now']}")
    print(f"source_policy_execution_invoked={inventory['source_policy_execution_invoked']}")


if __name__ == "__main__":
    main()
