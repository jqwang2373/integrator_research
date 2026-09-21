#!/usr/bin/env python3
"""Build the HI2022 rA_half double-pendulum repair-attempt certificate.

This certificate records the targeted self-reproduction/repair attempts already
present in the HI2022 T=8 artifacts.  It does not run the numerical runner and
does not promote the row: the repair remains incomplete and does not match the
full public-grid source-policy contract.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "HI2022_RA_HALF_DOUBLE_REPAIR_ATTEMPT_CERTIFICATE.json"
OUT_MD = PAPER / "HI2022_RA_HALF_DOUBLE_REPAIR_ATTEMPT_CERTIFICATE.md"
TARGET_GROUP = "rA_half:double_pendulum"


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def target_group(summary: dict[str, Any]) -> dict[str, Any]:
    groups = summary.get("groups", {})
    group = groups.get(TARGET_GROUP, {})
    if not isinstance(group, dict):
        return {}
    return group


def failed_rows_for_target(combined: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in combined.get("remaining_incomplete_groups", []):
        if isinstance(item, dict) and item.get("group") == TARGET_GROUP:
            for failed in item.get("failed_rows", []):
                if isinstance(failed, dict):
                    out.append(failed)
    return out


def repair_attempt_summaries(repair: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for attempt in repair.get("repair_attempts", []):
        if not isinstance(attempt, dict):
            continue
        summary = attempt.get("summary", {})
        if not isinstance(summary, dict):
            continue
        group = target_group(summary)
        out.append(
            {
                "artifact_dir": attempt.get("artifact_dir"),
                "tolerance_base": attempt.get("tolerance_base"),
                "target_group_complete": group.get("complete_three_step_group"),
                "target_group_ok_rows": group.get("ok_row_count"),
                "target_group_failed_rows": group.get("failed_row_count"),
                "target_group_status_values": group.get("status_values", []),
                "target_group_max_iterations": group.get("max_iterations"),
                "summary_row_count": summary.get("row_count"),
                "summary_ok_rows": summary.get("ok_row_count"),
                "summary_complete_groups": summary.get("complete_form_model_groups"),
                "summary_group_count": summary.get("group_count"),
            }
        )
    return out


def main() -> None:
    diagnosis = read_json(PAPER / "HI2022_RA_HALF_DOUBLE_SOURCE_POLICY_FAILURE_DIAGNOSIS.json")
    repair = read_json(PAPER / "HI2022_T8_TOLERANCE_REPAIR_AUDIT.json")
    ledger = read_json(PAPER / "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.json")
    post = read_json(PAPER / "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.json")

    row = next(
        (
            item
            for item in ledger.get("rows", [])
            if isinstance(item, dict)
            and item.get("suite_id") == "hi2022_half_implicit"
            and item.get("method") == "hi2022_rA_half"
            and item.get("example") == "double_pendulum"
        ),
        {},
    )
    combined = repair.get("combined_best", {})
    original_group = target_group(repair.get("original_t8_coarse", {}))
    combined_group = target_group(combined)
    repair_attempts = repair_attempt_summaries(repair)
    failed_rows = failed_rows_for_target(combined)
    full_contract = repair.get("full_public_grid_contract", {})
    repair_policy = repair.get("repair_policy", {})

    output: dict[str, Any] = {
        "schema": "hi2022-ra-half-double-repair-attempt-certificate-v1",
        "status": "targeted_repair_attempted_not_reproducible_not_promoted",
        "read_only": True,
        "heavy_numerical_run_invoked_by_this_builder": False,
        "run_v047_invoked_by_this_builder": False,
        "v048_runner_invoked_by_this_builder": False,
        "suite_id": "hi2022_half_implicit",
        "method": "hi2022_rA_half",
        "example": "double_pendulum",
        "target_group": TARGET_GROUP,
        "source_policy_closed": False,
        "source_policy_rows_promoted": 0,
        "external_superiority_ready": False,
        "b4_can_close_from_certificate": False,
        "b7_can_close_from_certificate": False,
        "row_ledger_status": {
            "readiness_status": row.get("readiness_status"),
            "post_execution_decision": row.get("post_execution_decision"),
            "source_policy_disposition": row.get("source_policy_disposition"),
            "counts_as_open_execution_queue": row.get("counts_as_open_execution_queue"),
            "primary_promotion_blocker": row.get("primary_promotion_blocker"),
            "promotion_evidence_ref": row.get("promotion_evidence_ref"),
            "command_refs": row.get("command_refs", []),
            "command_artifact_statuses": row.get("command_artifact_statuses", []),
        },
        "initial_selected_trio_diagnosis": {
            "status": diagnosis.get("status"),
            "row_count": diagnosis.get("execution_evidence", {}).get("row_count"),
            "ok_row_count": diagnosis.get("execution_evidence", {}).get("ok_row_count"),
            "failed_row_count": diagnosis.get("execution_evidence", {}).get("failed_row_count"),
            "ok_h_values": diagnosis.get("diagnosis", {}).get("ok_h_values", []),
            "failed_h_values": diagnosis.get("diagnosis", {}).get("failed_h_values", []),
            "failure_loci": diagnosis.get("diagnosis", {}).get("failure_loci", []),
            "pair_orders_available": diagnosis.get("diagnosis", {}).get("pair_orders_available"),
            "source_policy_rows_promoted": diagnosis.get("promotion_decision", {}).get(
                "source_policy_rows_promoted_by_this_diagnosis"
            ),
        },
        "tolerance_repair_evidence": {
            "repair_audit_status": repair.get("status"),
            "original_tolerance_base": repair_policy.get("original_tolerance_base"),
            "repair_tolerance_base": repair_policy.get("repair_tolerance_base"),
            "additional_repair_tolerance_bases": repair_policy.get("additional_repair_tolerance_bases", []),
            "repair_step_sizes": repair_policy.get("step_sizes", []),
            "repair_reference_h": repair_policy.get("reference_h"),
            "repair_t_end": repair_policy.get("t_end"),
            "contains_source_policy_1e_4_rows": repair_policy.get("contains_source_policy_1e_4_rows"),
            "repair_v048_runner_invoked_in_original_artifact": repair_policy.get(
                "v048_runner_invoked_for_repair"
            ),
            "builder_v048_runner_invoked": False,
            "original_target_group": original_group,
            "repair_attempts": repair_attempts,
            "combined_target_group": combined_group,
            "combined_failed_target_rows": failed_rows,
            "combined_best_ok_rows": combined.get("ok_row_count"),
            "combined_best_row_count": combined.get("row_count"),
            "combined_best_complete_groups": combined.get("complete_form_model_groups"),
            "combined_best_group_count": combined.get("group_count"),
            "recovered_rows": combined.get("recovered_rows", []),
            "remaining_incomplete_group_count": len(combined.get("remaining_incomplete_groups", [])),
        },
        "full_public_grid_contract": full_contract,
        "claim_boundary": {
            "targeted_repair_completed": combined_group.get("complete_three_step_group") is True,
            "coarse_trio_diagnostic_repair_completed": False,
            "full_public_grid_matches_repair_policy": False,
            "full_T8_policy_completed": repair.get("claim_boundary", {}).get("full_T8_policy_completed"),
            "source_policy_reproduction_closed": repair.get("claim_boundary", {}).get(
                "source_policy_reproduction_closed"
            ),
            "external_superiority_claim_allowed": repair.get("claim_boundary", {}).get(
                "external_superiority_claim_allowed"
            ),
            "accepted_source_policy_dynamic_order_examples": repair.get("claim_boundary", {}).get(
                "accepted_source_policy_dynamic_order_examples"
            ),
        },
        "closure_decision": {
            "can_close_hi2022_ra_half_double_now": False,
            "can_promote_to_b4_b7_source_policy_figure": False,
            "reason": (
                "The targeted repair recovers only the h=0.025 row for rA_half:double_pendulum. "
                "The h=0.05 and h=0.1 rows remain Newton failures after tolerance repair, and the "
                "repair grid/reference do not match the full HI2022 public-grid contract."
            ),
        },
        "next_required_actions": [
            "Keep this row out of B4/B7 source-policy work-precision figures.",
            "Do not claim external superiority from this target group.",
            "Either repair all rA_half:double_pendulum T=8 rows under the documented policy or demote the family.",
            "Full promotion still requires all 72 public-grid rows with T=8, reference_h=0.001, tolerance_base=1e-10, output norm, runtime, and Newton diagnostics bound.",
        ],
        "source_files": [
            "HI2022_RA_HALF_DOUBLE_SOURCE_POLICY_FAILURE_DIAGNOSIS.json",
            "HI2022_T8_TOLERANCE_REPAIR_AUDIT.json",
            "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.json",
            "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.json",
        ],
    }

    OUT_JSON.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# HI2022 rA_half Double Repair-Attempt Certificate",
        "",
        "Status: **targeted repair attempted; not reproducible; not promoted**.",
        "",
        f"- Target: `{output['target_group']}`.",
        f"- Source-policy rows promoted: `{output['source_policy_rows_promoted']}`.",
        f"- External-superiority ready: `{output['external_superiority_ready']}`.",
        f"- B4/B7 can close from certificate: `{output['b4_can_close_from_certificate']}/{output['b7_can_close_from_certificate']}`.",
        f"- Initial selected-trio ok/failed rows: `{output['initial_selected_trio_diagnosis']['ok_row_count']}/{output['initial_selected_trio_diagnosis']['failed_row_count']}`.",
        f"- Combined repair target ok/failed rows: `{combined_group.get('ok_row_count')}/{combined_group.get('failed_row_count')}`.",
        f"- Combined best matrix ok rows/groups: `{combined.get('ok_row_count')}/{combined.get('row_count')}` rows, `{combined.get('complete_form_model_groups')}/{combined.get('group_count')}` groups.",
        f"- Full public-grid rows required: `{full_contract.get('required_rows')}`.",
        f"- Repair/public reference h: `{repair_policy.get('reference_h')}/{full_contract.get('reference_h')}`.",
        f"- Repair/public tolerance base: `{repair_policy.get('repair_tolerance_base')}/{full_contract.get('tolerance_base')}`.",
        f"- Full T=8 policy completed: `{output['claim_boundary']['full_T8_policy_completed']}`.",
        f"- Source-policy reproduction closed: `{output['claim_boundary']['source_policy_reproduction_closed']}`.",
        "",
        "## Failed Target Rows",
        "",
        "| h | best status | failure family | attempts |",
        "|---:|---|---|---:|",
    ]
    for failed in failed_rows:
        lines.append(
            f"| `{failed.get('h')}` | `{failed.get('best_status')}` | "
            f"`{failed.get('failure_family')}` | `{len(failed.get('attempts', []))}` |"
        )
    lines.extend(
        [
            "",
            "## Repair Attempts",
            "",
            "| tolerance base | target ok/failed | target complete | summary ok/rows | summary groups |",
            "|---:|---:|---:|---:|---:|",
        ]
    )
    for attempt in repair_attempts:
        lines.append(
            f"| `{attempt.get('tolerance_base')}` | "
            f"`{attempt.get('target_group_ok_rows')}/{attempt.get('target_group_failed_rows')}` | "
            f"`{attempt.get('target_group_complete')}` | "
            f"`{attempt.get('summary_ok_rows')}/{attempt.get('summary_row_count')}` | "
            f"`{attempt.get('summary_complete_groups')}/{attempt.get('summary_group_count')}` |"
        )
    lines.extend(["", output["closure_decision"]["reason"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("hi2022_ra_half_double_repair_attempt_certificate=written")
    print("source_policy_rows_promoted=0")
    print("external_superiority_ready=False")
    print("b4_can_close=False")
    print("b7_can_close=False")


if __name__ == "__main__":
    main()
