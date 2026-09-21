#!/usr/bin/env python3
"""Build the B4 source-policy row closure-readiness ledger.

This read-only ledger maps every external method/example cell in the paper's
44-cell matrix to the B4 source-policy work/precision closure state. It does
not execute numerical runners.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.json"
OUT_MD = PAPER / "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.md"
OUT_CSV = PAPER / "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.csv"

EXAMPLES = ["single_pendulum", "double_pendulum", "four_link", "slider_crank"]

METHOD_TO_SUITE = {
    "ra2021_rA": ("ra2021_absolute_coordinate", "ra2021_source_policy_work_precision"),
    "ra2021_reps": ("ra2021_absolute_coordinate", "ra2021_source_policy_work_precision"),
    "ra2021_rp": ("ra2021_absolute_coordinate", "ra2021_source_policy_work_precision"),
    "hi2022_rA": ("hi2022_half_implicit", "hi2022_full_T8_work_precision"),
    "hi2022_rA_half": ("hi2022_half_implicit", "hi2022_full_T8_work_precision"),
    "tfe2026_Newmark_beta": ("tfe2026_original_pendulum", "tfe_source_policy_work_precision"),
    "tfe2026_TFE_m1": ("tfe2026_original_pendulum", "tfe_source_policy_work_precision"),
    "tfe2026_TFE_m2": ("tfe2026_original_pendulum", "tfe_source_policy_work_precision"),
    "tfe2026_trapezoidal": ("tfe2026_original_pendulum", "tfe_source_policy_work_precision"),
    "vp2024_coordinate_partitioning_rA": (
        "vp2024_velocity_partitioning",
        "vp2024_source_code_path_work_precision",
    ),
}


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def command_map(preflight: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(item.get("id")): item
        for item in preflight.get("launch_commands", [])
        if isinstance(item, dict) and item.get("id")
    }


def post_command_map(post_execution: dict[str, Any]) -> dict[str, dict[str, Any]]:
    presence = post_execution.get("command_artifact_presence", {})
    return {
        str(item.get("id")): item
        for item in presence.get("commands", [])
        if isinstance(item, dict) and item.get("id")
    }


def self_attempt_map(audit: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(item.get("row_id")): item
        for item in audit.get("rows", [])
        if isinstance(item, dict) and item.get("row_id")
    }


def ra2021_post_statuses(command_refs: list[str], post_execution: dict[str, Any]) -> list[str]:
    evidence = post_execution.get("post_execution_artifact_evidence", {})
    command_presence = post_command_map(post_execution)
    statuses: list[str] = []
    for command_id in command_refs:
        command = command_presence.get(command_id, {})
        output_present = command.get("expected_output_exists_now") is True
        if command_id == "ra2021_public_timing_all_forms_models":
            statuses.append(
                evidence.get("ra2021_public_baseline_shards_status")
                if output_present
                else "approved_driver_output_missing"
            )
        elif command_id == "gauss6_public_single_source_policy_trio":
            statuses.append(
                "gauss6_single_public_horizon_step_trio_completed_not_promoted"
                if output_present and evidence.get("gauss6_single_public_horizon_step_trio_completed") is True
                else "approved_driver_output_missing"
            )
        elif command_id == "ra2021_double_order_all_forms":
            statuses.append(
                evidence.get("ra2021_double_local_candidate_status")
                if output_present
                else "approved_driver_output_missing"
            )
        elif command_id in {
            "gauss6_public_four_link_source_policy_trio",
            "gauss6_public_slider_crank_source_policy_trio",
        }:
            statuses.append(
                "public_closed_loop_step_trio_completed_residual_only_not_promoted"
                if output_present
                and evidence.get("public_closed_loop_trios_completed_by_latest_driver_outputs") is True
                else "approved_driver_output_missing"
            )
        else:
            statuses.append(str(command.get("packet_artifact_status", "unknown_command_status")))
    return [str(status) for status in statuses]


def hi2022_command_id(method: str, example: str) -> str | None:
    form = "rA_half" if method == "hi2022_rA_half" else "rA"
    return f"hi2022_selected_t8_{form}_{example}"


def ra2021_command_refs(example: str) -> list[str]:
    refs = ["ra2021_public_timing_all_forms_models"]
    if example == "single_pendulum":
        refs.append("gauss6_public_single_source_policy_trio")
    elif example == "double_pendulum":
        refs.append("ra2021_double_order_all_forms")
    elif example == "four_link":
        refs.append("gauss6_public_four_link_source_policy_trio")
    elif example == "slider_crank":
        refs.append("gauss6_public_slider_crank_source_policy_trio")
    return refs


def promotion_blocker_class(*, suite_id: str, method: str, example: str) -> tuple[str, str]:
    if suite_id == "ra2021_absolute_coordinate":
        if example == "single_pendulum":
            return (
                "ra2021_single_floor_limited_public_h_tranche_not_promoted",
                "RA2021_SOURCE_POLICY_ROW_AUDIT.json",
            )
        if example == "double_pendulum":
            return (
                "ra2021_double_low_order_floor_limited_constraint_not_promoted",
                "RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.json",
            )
        return (
            "ra2021_closed_loop_T0p1_mixed_reference_not_source_policy",
            "RA2021_SOURCE_POLICY_ROW_AUDIT.json",
        )
    if suite_id == "hi2022_half_implicit":
        if method == "hi2022_rA_half" and example == "double_pendulum":
            return (
                "hi2022_ra_half_double_partial_newton_failure_not_promoted",
                "HI2022_RA_HALF_DOUBLE_SOURCE_POLICY_FAILURE_DIAGNOSIS.json",
            )
        return (
            "hi2022_selected_coarse_trio_not_full_public_grid_not_promoted",
            "HI2022_SOURCE_POLICY_ROW_AUDIT.json",
        )
    if suite_id == "tfe2026_original_pendulum":
        return (
            "tfe_runner_equivalence_open_no_launch_command",
            "TFE_B4_B7_SOURCE_POLICY_DEMOTION_AUDIT.json",
        )
    if suite_id == "vp2024_velocity_partitioning":
        return (
            "vp2024_distinct_public_code_path_unresolved",
            "VP2024_CODE_PATH_DISPOSITION_AUDIT.json",
        )
    return ("unclassified_source_policy_blocker", "")


def build_row(
    *,
    matrix_row: dict[str, Any],
    b4_lanes: dict[str, dict[str, Any]],
    ra_commands: dict[str, dict[str, Any]],
    hi_commands: dict[str, dict[str, Any]],
    tfe_demotion_audit: dict[str, Any],
    post_execution: dict[str, Any],
    self_attempts: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    method = str(matrix_row["method"])
    example = str(matrix_row["example"])
    suite_id, lane_id = METHOD_TO_SUITE[method]
    lane = b4_lanes[lane_id]
    command_refs: list[str] = []
    command_artifact_statuses: list[str] = []
    readiness = ""
    explicit_1e4_required: bool | None = None
    current_claim_requires_source_policy_execution = True
    demotion_audit: str | None = None
    blocks = list(matrix_row.get("issues", []))
    blocks.append(str(matrix_row.get("required_action")))
    primary_blocker, promotion_evidence_ref = promotion_blocker_class(
        suite_id=suite_id, method=method, example=example
    )
    post_execution_decision = "not_promoted"
    source_policy_disposition = "promotion_open"
    self_attempt = self_attempts.get(f"{method}:{example}")
    self_reproduction_attempted = False
    self_reproduction_outcome = "not_attempted"
    self_reproduction_evidence_ref = ""
    unable_to_reproduce = False
    final_nonpublic_code_disposition = "not_applicable_public_root_or_not_attempted"
    counts_as_open_execution_queue = True

    if suite_id == "ra2021_absolute_coordinate":
        command_refs = ra2021_command_refs(example)
        command_artifact_statuses = ra2021_post_statuses(command_refs, post_execution)
        readiness = "approved_driver_outputs_present_not_promoted"
        explicit_1e4_required = True
        blocks.extend(lane.get("required_before_publication_figure", []))
    elif suite_id == "hi2022_half_implicit":
        command_id = hi2022_command_id(method, example)
        command_refs = [command_id]
        status = str(hi_commands[command_id].get("artifact_status"))
        command_artifact_statuses = [status]
        readiness = (
            "selected_candidate_executed_not_promoted"
            if status == "executed_full_T8_selected_coarse_trio_not_promoted"
            else "selected_candidate_partial_or_failed_not_promoted"
            if status == "partial_or_failed_full_T8_source_policy_candidate_not_promoted"
            else "selected_candidate_launch_ready_not_closed"
        )
        explicit_1e4_required = False
        blocks.extend(lane.get("required_before_publication_figure", []))
    elif suite_id == "tfe2026_original_pendulum":
        readiness = "not_ready_runner_equivalence_open"
        explicit_1e4_required = None
        current_claim_requires_source_policy_execution = bool(
            tfe_demotion_audit.get("current_claim_requires_tfe_source_policy_execution")
        )
        demotion_audit = "TFE_B4_B7_SOURCE_POLICY_DEMOTION_AUDIT.json"
        blocks.extend(lane.get("required_before_publication_figure", []))
    elif suite_id == "vp2024_velocity_partitioning":
        readiness = "not_ready_code_path_unresolved"
        explicit_1e4_required = False
        current_claim_requires_source_policy_execution = False
        demotion_audit = "VP2024_CODE_PATH_DISPOSITION_AUDIT.json"
        blocks.extend(lane.get("required_before_publication_figure", []))
    else:
        raise ValueError(f"unmapped suite {suite_id}")

    if self_attempt is not None:
        readiness = str(self_attempt.get("source_policy_disposition", "attempted_not_reproducible"))
        post_execution_decision = str(self_attempt.get("post_execution_decision", "attempted_not_reproducible"))
        source_policy_disposition = str(
            self_attempt.get("source_policy_disposition", "attempted_not_reproducible")
        )
        self_reproduction_attempted = bool(self_attempt.get("self_reproduction_attempted"))
        self_reproduction_outcome = source_policy_disposition
        self_reproduction_evidence_ref = "SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json"
        unable_to_reproduce = bool(self_attempt.get("unable_to_reproduce"))
        final_nonpublic_code_disposition = str(
            self_attempt.get("final_nonpublic_code_disposition", "unable_to_reproduce_not_promoted")
        )
        counts_as_open_execution_queue = bool(self_attempt.get("counts_as_open_execution_queue"))
        primary_blocker = str(
            self_attempt.get(
                "primary_nonreproducibility_reason",
                "source_policy_self_reproduction_attempt_not_reproducible",
            )
        )
        promotion_evidence_ref = self_reproduction_evidence_ref
        blocks.append(primary_blocker)

    return {
        "method": method,
        "example": example,
        "suite_id": suite_id,
        "lane_id": lane_id,
        "source_level": matrix_row.get("source_level"),
        "matrix_status": matrix_row.get("status"),
        "source_policy_closed": bool(matrix_row.get("source_policy_closed")),
        "current_claim_requires_source_policy_execution": current_claim_requires_source_policy_execution,
        "demotion_audit": demotion_audit,
        "external_superiority_ready": False,
        "b4_can_close_from_row": False,
        "b7_can_close_from_row": False,
        "readiness_status": readiness,
        "post_execution_decision": post_execution_decision,
        "source_policy_disposition": source_policy_disposition,
        "self_reproduction_attempted": self_reproduction_attempted,
        "self_reproduction_outcome": self_reproduction_outcome,
        "self_reproduction_evidence_ref": self_reproduction_evidence_ref,
        "unable_to_reproduce": unable_to_reproduce,
        "final_nonpublic_code_disposition": final_nonpublic_code_disposition,
        "counts_as_open_execution_queue": counts_as_open_execution_queue,
        "primary_promotion_blocker": primary_blocker,
        "promotion_evidence_ref": promotion_evidence_ref,
        "ready_to_launch_after_explicit_opt_in": bool(lane.get("ready_to_launch_after_explicit_opt_in"))
        and bool(command_refs),
        "source_policy_1e_4_opt_in_required": explicit_1e4_required,
        "command_refs": command_refs,
        "command_artifact_statuses": command_artifact_statuses,
        "blocking_reasons": sorted(set(item for item in blocks if item)),
    }


def suite_summary(rows: list[dict[str, Any]], lanes: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for suite_id in sorted({row["suite_id"] for row in rows}):
        suite_rows = [row for row in rows if row["suite_id"] == suite_id]
        lane_id = str(suite_rows[0]["lane_id"])
        lane = lanes[lane_id]
        out.append(
            {
                "suite_id": suite_id,
                "lane_id": lane_id,
                "status": lane.get("status"),
                "source_policy_rows_total": len(suite_rows),
                "source_policy_rows_closed": sum(1 for row in suite_rows if row["source_policy_closed"]),
                "source_policy_rows_attempted_not_reproducible": sum(
                    1
                    for row in suite_rows
                    if row.get("source_policy_disposition") == "attempted_not_reproducible"
                ),
                "source_policy_rows_unable_to_reproduce": sum(
                    1 for row in suite_rows if row.get("unable_to_reproduce")
                ),
                "source_policy_rows_still_requiring_execution_or_promotion": sum(
                    1 for row in suite_rows if row.get("counts_as_open_execution_queue")
                ),
                "rows_with_launch_command_refs": sum(1 for row in suite_rows if row["command_refs"]),
                "rows_demoted_related_work_proxy_for_current_claim": sum(
                    1 for row in suite_rows if row.get("current_claim_requires_source_policy_execution") is False
                ),
                "ready_to_launch_after_explicit_opt_in": lane.get("ready_to_launch_after_explicit_opt_in"),
                "b4_can_close_now": False,
                "b7_can_close_now": False,
            }
        )
    return out


def main() -> None:
    matrix = read_json(PAPER / "PAPER_NUMERICAL_RESULT_MATRIX.json")
    b4 = read_json(PAPER / "B4_SOURCE_POLICY_WORK_PRECISION_EXECUTION_PLAN.json")
    disposition = read_json(PAPER / "ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.json")
    row_ledger = read_json(PAPER / "SOURCE_POLICY_ROW_CLOSURE_LEDGER.json")
    tfe_demotion_audit = read_json(PAPER / "TFE_B4_B7_SOURCE_POLICY_DEMOTION_AUDIT.json")
    post_execution = read_json(PAPER / "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.json")
    verified_authorized = post_execution.get("verified_authorized_execution_recorded") is True
    self_attempt_audit = read_json(PAPER / "SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json")
    self_attempts = self_attempt_map(self_attempt_audit)

    lanes = {
        str(item.get("lane_id")): item
        for item in b4.get("execution_lanes", [])
        if isinstance(item, dict) and item.get("lane_id")
    }
    ra_commands = command_map(b4.get("ra2021_launch_preflight", {}))
    hi_commands = command_map(b4.get("hi2022_launch_preflight", {}))
    rows = [
        build_row(
            matrix_row=item,
            b4_lanes=lanes,
            ra_commands=ra_commands,
            hi_commands=hi_commands,
            tfe_demotion_audit=tfe_demotion_audit,
            post_execution=post_execution,
            self_attempts=self_attempts,
        )
        for item in matrix.get("rows", [])
        if isinstance(item, dict) and item.get("method") != "local_Gauss6_FullVA"
    ]
    rows.sort(key=lambda row: (row["suite_id"], row["method"], EXAMPLES.index(row["example"])))

    command_mapped_rows = sum(1 for row in rows if row["command_refs"])
    source_closed = sum(1 for row in rows if row["source_policy_closed"])
    attempted_not_reproducible = sum(
        1 for row in rows if row.get("source_policy_disposition") == "attempted_not_reproducible"
    )
    unable_to_reproduce = sum(1 for row in rows if row.get("unable_to_reproduce"))
    still_requiring_execution_or_promotion = sum(1 for row in rows if row.get("counts_as_open_execution_queue"))
    summary = suite_summary(rows, lanes)
    output: dict[str, Any] = {
        "schema": "b4-source-policy-row-closure-readiness-ledger-v1",
        "status": "all_40_external_rows_mapped_20_attempted_not_reproducible_0_source_policy_rows_closed",
        "read_only": True,
        "source_files": [
            "PAPER_NUMERICAL_RESULT_MATRIX.json",
            "B4_SOURCE_POLICY_WORK_PRECISION_EXECUTION_PLAN.json",
            "ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.json",
            "SOURCE_POLICY_ROW_CLOSURE_LEDGER.json",
            "TFE_B4_B7_SOURCE_POLICY_DEMOTION_AUDIT.json",
            "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.json",
            "SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json",
            "TFE_PUBLIC_CODE_RECHECK_20260613.json",
            "VP2024_PUBLIC_CODE_RECHECK_20260613.json",
            "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.json",
        ],
        "row_count": len(rows),
        "total_rows": len(rows),
        "source_policy_rows_total": len(rows),
        "expected_external_row_count": disposition.get("coverage", {}).get("expected_nonlocal_cells"),
        "source_policy_rows_closed": source_closed,
        "source_policy_rows_unclosed": len(rows) - source_closed,
        "source_policy_rows_open": still_requiring_execution_or_promotion,
        "source_policy_rows_attempted_not_reproducible": attempted_not_reproducible,
        "source_policy_rows_unable_to_reproduce": unable_to_reproduce,
        "source_policy_rows_still_requiring_execution_or_promotion": still_requiring_execution_or_promotion,
        "external_superiority_ready_rows": 0,
        "rows_with_launch_command_refs": command_mapped_rows,
        "rows_without_launch_command_refs": len(rows) - command_mapped_rows,
        "rows_without_launch_command_refs_attempted_not_reproducible": sum(
            1 for row in rows if not row["command_refs"] and row.get("source_policy_disposition") == "attempted_not_reproducible"
        ),
        "rows_demoted_related_work_proxy_for_current_claim": sum(
            1 for row in rows if row.get("current_claim_requires_source_policy_execution") is False
        ),
        "ra2021_explicit_1e_4_rows": sum(
            1 for row in rows if row["suite_id"] == "ra2021_absolute_coordinate"
        ),
        "hi2022_command_mapped_rows": sum(
            1 for row in rows if row["suite_id"] == "hi2022_half_implicit" and row["command_refs"]
        ),
        "hi2022_existing_candidate_not_promoted_rows": sum(
            1 for row in rows if row["readiness_status"] == "selected_candidate_executed_not_promoted"
        ),
        "hi2022_partial_or_failed_not_promoted_rows": sum(
            1 for row in rows if row["readiness_status"] == "selected_candidate_partial_or_failed_not_promoted"
        ),
        "ra2021_ready_command_output_rows_not_promoted": sum(
            1 for row in rows if row["readiness_status"] == "approved_driver_outputs_present_not_promoted"
        ),
        "ra2021_approved_driver_output_rows_not_promoted": sum(
            1 for row in rows if row["readiness_status"] == "approved_driver_outputs_present_not_promoted"
        ),
        "ra2021_output_row_scope": (
            "verified_authorized_driver_output_presence_not_promoted"
            if verified_authorized
            else "legacy_ready_command_output_presence_not_verified_authorized_execution"
        ),
        "post_execution_decision_counts": {
            decision: sum(1 for row in rows if row["post_execution_decision"] == decision)
            for decision in sorted({row["post_execution_decision"] for row in rows})
        },
        "primary_promotion_blocker_counts": {
            blocker: sum(1 for row in rows if row["primary_promotion_blocker"] == blocker)
            for blocker in sorted({row["primary_promotion_blocker"] for row in rows})
        },
        "ready_suite_count": b4.get("execution_lane_summary", {}).get(
            "ready_to_launch_after_explicit_opt_in_count"
        ),
        "not_ready_suite_count": b4.get("execution_lane_summary", {}).get("not_ready_lane_count"),
        "b4_can_close_now": False,
        "b7_can_close_now": False,
        "heavy_numerical_run_invoked": False,
        "run_v047_invoked": False,
        "v048_runner_invoked": False,
        "suite_summary": summary,
        "rows": rows,
        "claim_boundary": {
            "common_reference_claim_allowed": disposition.get("claim_boundary", {}).get(
                "common_reference_claim_allowed"
            ),
            "source_policy_superiority_claim_allowed": False,
            "source_policy_closed_rows_from_flagged_row_ledger": row_ledger.get("coverage", {}).get(
                "rows_source_policy_closed"
            ),
            "flagged_rows_from_flagged_row_ledger": row_ledger.get("coverage", {}).get("flagged_row_count"),
            "interpretation": (
                "The flagged-row ledger tracks the 15 anomaly rows; this B4 ledger tracks all 40 "
                "external method/example cells required before source-policy work/precision figures can close."
            ),
        },
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, sort_keys=True)
        handle.write("\n")

    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "suite_id",
                "lane_id",
                "method",
                "example",
                "readiness_status",
                "source_policy_closed",
                "ready_to_launch_after_explicit_opt_in",
                "source_policy_1e_4_opt_in_required",
                "current_claim_requires_source_policy_execution",
                "demotion_audit",
                "post_execution_decision",
                "primary_promotion_blocker",
                "promotion_evidence_ref",
                "command_refs",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "suite_id": row["suite_id"],
                    "lane_id": row["lane_id"],
                    "method": row["method"],
                    "example": row["example"],
                    "readiness_status": row["readiness_status"],
                    "source_policy_closed": row["source_policy_closed"],
                    "ready_to_launch_after_explicit_opt_in": row[
                        "ready_to_launch_after_explicit_opt_in"
                    ],
                    "source_policy_1e_4_opt_in_required": row["source_policy_1e_4_opt_in_required"],
                    "current_claim_requires_source_policy_execution": row[
                        "current_claim_requires_source_policy_execution"
                    ],
                    "demotion_audit": row["demotion_audit"] or "",
                    "post_execution_decision": row["post_execution_decision"],
                    "primary_promotion_blocker": row["primary_promotion_blocker"],
                    "promotion_evidence_ref": row["promotion_evidence_ref"],
                    "command_refs": "|".join(row["command_refs"]),
                }
            )

    lines = [
        "# B4 Source-Policy Row Closure Readiness Ledger",
        "",
        f"Status: `{output['status']}`.",
        "",
        "This is a read-only ledger over the 40 external method/example cells. It does not run numerical experiments.",
        "",
        f"- External rows mapped: `{output['row_count']}/{output['expected_external_row_count']}`.",
        f"- Source-policy rows closed/unclosed: `{output['source_policy_rows_closed']}/{output['source_policy_rows_unclosed']}`.",
        f"- Source-policy rows still requiring execution/promotion: `{output['source_policy_rows_still_requiring_execution_or_promotion']}`.",
        f"- Source-policy rows attempted-not-reproducible: `{output['source_policy_rows_attempted_not_reproducible']}`.",
        f"- Source-policy rows unable-to-reproduce/not-promoted: `{output['source_policy_rows_unable_to_reproduce']}`.",
        f"- Rows with launch command refs: `{output['rows_with_launch_command_refs']}`.",
        f"- Rows without launch command refs: `{output['rows_without_launch_command_refs']}`.",
        f"- Rows without launch command refs attempted-not-reproducible: `{output['rows_without_launch_command_refs_attempted_not_reproducible']}`.",
        f"- Rows demoted related-work/proxy for current claim: `{output['rows_demoted_related_work_proxy_for_current_claim']}`.",
        f"- RA2021 ready-command output rows not promoted: `{output['ra2021_ready_command_output_rows_not_promoted']}`.",
        f"- RA2021 output row scope: `{output['ra2021_output_row_scope']}`.",
        f"- HI2022 selected-candidate executed/partial rows not promoted: `{output['hi2022_existing_candidate_not_promoted_rows']}/{output['hi2022_partial_or_failed_not_promoted_rows']}`.",
        f"- Post-execution decision counts: `{output['post_execution_decision_counts']}`.",
        f"- Primary promotion-blocker counts: `{output['primary_promotion_blocker_counts']}`.",
        f"- Ready/not-ready suites: `{output['ready_suite_count']}/{output['not_ready_suite_count']}`.",
        f"- B4/B7 can close now: `{output['b4_can_close_now']}/{output['b7_can_close_now']}`.",
        f"- Heavy/run_v047/v048 invoked: `{output['heavy_numerical_run_invoked']}/{output['run_v047_invoked']}/{output['v048_runner_invoked']}`.",
        "",
        "## Suite Summary",
        "",
        "| suite | rows | closed | attempted not reproducible | unable to reproduce | still requiring execution | command-mapped | launch-ready | B4/B7 close |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in summary:
        lines.append(
            f"| `{item['suite_id']}` | `{item['source_policy_rows_total']}` | "
            f"`{item['source_policy_rows_closed']}` | "
            f"`{item['source_policy_rows_attempted_not_reproducible']}` | "
            f"`{item['source_policy_rows_unable_to_reproduce']}` | "
            f"`{item['source_policy_rows_still_requiring_execution_or_promotion']}` | "
            f"`{item['rows_with_launch_command_refs']}` | "
            f"`{item['ready_to_launch_after_explicit_opt_in']}` | "
            f"`{item['b4_can_close_now']}/{item['b7_can_close_now']}` |"
        )
    lines.extend(
        [
            "",
            "## Row Readiness",
            "",
            "| suite | method | example | status | disposition | decision | primary blocker | evidence | commands |",
            "|---|---|---|---|---|---|---|---|---:|",
        ]
    )
    for row in rows:
        lines.append(
            f"| `{row['suite_id']}` | `{row['method']}` | `{row['example']}` | "
            f"`{row['readiness_status']}` | `{row['source_policy_disposition']}` | "
            f"`{row['post_execution_decision']}` | "
            f"`{row['primary_promotion_blocker']}` | `{row['promotion_evidence_ref']}` | "
            f"`{len(row['command_refs'])}` |"
        )
    lines.extend(["", output["claim_boundary"]["interpretation"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("b4_source_policy_row_closure_readiness_ledger=written")
    print(f"external_rows={output['row_count']}/{output['expected_external_row_count']}")
    print(f"source_policy_closed={output['source_policy_rows_closed']}/{output['row_count']}")
    print(f"attempted_not_reproducible={output['source_policy_rows_attempted_not_reproducible']}")
    print(f"still_requiring_execution_or_promotion={output['source_policy_rows_still_requiring_execution_or_promotion']}")
    print(f"rows_with_launch_command_refs={output['rows_with_launch_command_refs']}")
    print("b4_can_close_now=False")
    print("b7_can_close_now=False")


if __name__ == "__main__":
    main()
