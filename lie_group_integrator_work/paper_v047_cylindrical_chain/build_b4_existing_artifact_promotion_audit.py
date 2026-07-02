#!/usr/bin/env python3
"""Build the B4 existing-artifact promotion audit.

This read-only audit answers one narrow question: whether any currently
available source-policy-adjacent artifact can be promoted into B4/B7
publication-grade work/precision rows without new numerical execution.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "B4_EXISTING_ARTIFACT_PROMOTION_AUDIT.json"
OUT_MD = PAPER / "B4_EXISTING_ARTIFACT_PROMOTION_AUDIT.md"


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def promotion_item(
    *,
    item_id: str,
    source: str,
    artifact_status: Any,
    existing_rows: int,
    source_policy_rows_closed: int,
    promotion_ready: bool,
    b4_can_close: bool,
    b7_can_close: bool,
    blocking_reasons: list[str],
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    item = {
        "id": item_id,
        "source": source,
        "artifact_status": artifact_status,
        "existing_rows": existing_rows,
        "source_policy_rows_closed_by_this_artifact": source_policy_rows_closed,
        "promotion_ready_without_new_execution": promotion_ready,
        "b4_can_close_from_this_artifact": b4_can_close,
        "b7_can_close_from_this_artifact": b7_can_close,
        "blocking_reasons": blocking_reasons,
    }
    if extra:
        item.update(extra)
    return item


def tfe_execution_preflight_boundary(tfe_gap: dict[str, Any]) -> dict[str, Any]:
    preflight = tfe_gap.get("source_policy_execution_preflight", {})
    return {
        "source": "TFE_DAE_RUNNER_CONTRACT_GAP_AUDIT.json::source_policy_execution_preflight",
        "schema": preflight.get("schema"),
        "status": preflight.get("status"),
        "current_route": preflight.get("current_route"),
        "reviewer_facing_decision": preflight.get("reviewer_facing_decision"),
        "ready_to_execute_source_policy_now": preflight.get("ready_to_execute_source_policy_now"),
        "can_promote_any_tfe_source_policy_row_now": preflight.get(
            "can_promote_any_tfe_source_policy_row_now"
        ),
        "source_policy_rows_completed": preflight.get("source_policy_rows_completed"),
        "execution_block_count": preflight.get("execution_block_count"),
        "execution_blocks": list(preflight.get("execution_blocks", [])),
        "runner_contracts_required_before_execution": list(
            preflight.get("runner_contracts_required_before_execution", [])
        ),
        "nonheavy_blocks_dispositioned_by_demotion": preflight.get(
            "nonheavy_blocks_dispositioned_by_demotion"
        ),
        "nonheavy_demotion_does_not_close_source_policy": preflight.get(
            "nonheavy_demotion_does_not_close_source_policy"
        ),
        "explicit_user_opt_in_required": preflight.get("explicit_user_opt_in_required"),
        "opt_in_required_for": list(preflight.get("opt_in_required_for", [])),
        "reopen_condition": preflight.get("reopen_condition"),
        "heavy_numerical_run_invoked": preflight.get("heavy_numerical_run_invoked"),
        "run_v047_invoked": preflight.get("run_v047_invoked"),
        "v048_runner_invoked": preflight.get("v048_runner_invoked"),
    }


def main() -> None:
    b4 = read_json(PAPER / "B4_SOURCE_POLICY_WORK_PRECISION_EXECUTION_PLAN.json")
    current = b4.get("current_evidence", {})
    diagnostic = current.get("diagnostic_work_precision_rows", {})
    ra_shards = b4.get("ra2021_executed_shard_evidence", {})
    gauss6 = b4.get("gauss6_local_source_policy_evidence", {})
    same_window = b4.get("ra2021_closed_loop_same_window_public_work_precision_evidence", {})
    double_candidate = b4.get("ra2021_double_local_source_policy_candidate_evidence", {})
    hi2022_candidate = b4.get("hi2022_full_t8_source_policy_candidate_evidence", {})
    hi2022_demotion = b4.get("hi2022_b4_b7_figure_scope_demotion_evidence", {})
    tfe = b4.get("tfe_source_policy_runner_equivalence_preflight_evidence", {})
    tfe_gap = read_json(PAPER / "TFE_DAE_RUNNER_CONTRACT_GAP_AUDIT.json")
    tfe_preflight_boundary = tfe_execution_preflight_boundary(tfe_gap)
    vp_disposition = read_json(PAPER / "VP2024_CODE_PATH_DISPOSITION_AUDIT.json")
    vp_recheck = read_json(PAPER / "VP2024_PUBLIC_CODE_RECHECK_20260613.json")
    public_refresh = read_json(PAPER / "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.json")
    vp_coverage = vp_disposition.get("coverage", {})
    vp_claim_boundary = vp_recheck.get("claim_boundary", {})

    items = [
        promotion_item(
            item_id="ra2021_public_baseline_shards",
            source="ra2021_executed_shard_evidence",
            artifact_status=ra_shards.get("status"),
            existing_rows=int(ra_shards.get("ok_row_count") or 0),
            source_policy_rows_closed=int(ra_shards.get("source_policy_rows_closed_by_this_evidence") or 0),
            promotion_ready=False,
            b4_can_close=bool(ra_shards.get("b4_can_close_from_this_evidence")),
            b7_can_close=bool(ra_shards.get("b7_can_close_from_this_evidence")),
            blocking_reasons=list(ra_shards.get("promotion_gap", [])),
        ),
        promotion_item(
            item_id="gauss6_public_horizon_local_rows",
            source="gauss6_local_source_policy_evidence",
            artifact_status=gauss6.get("status"),
            existing_rows=int(gauss6.get("single_public_horizon_rows", {}).get("ok_row_count") or 0)
            + int(gauss6.get("closed_loop_combined_ok_rows") or 0),
            source_policy_rows_closed=int(gauss6.get("source_policy_rows_closed_by_this_evidence") or 0),
            promotion_ready=False,
            b4_can_close=bool(gauss6.get("b4_can_close_from_this_evidence")),
            b7_can_close=bool(gauss6.get("b7_can_close_from_this_evidence")),
            blocking_reasons=list(gauss6.get("promotion_gap", [])),
        ),
        promotion_item(
            item_id="ra2021_closed_loop_same_window_work_precision",
            source="ra2021_closed_loop_same_window_public_work_precision_evidence",
            artifact_status=same_window.get("status"),
            existing_rows=int(same_window.get("ok_row_count") or 0),
            source_policy_rows_closed=int(same_window.get("source_policy_rows_closed_by_this_evidence") or 0),
            promotion_ready=False,
            b4_can_close=bool(same_window.get("b4_can_close_from_this_evidence")),
            b7_can_close=bool(same_window.get("b7_can_close_from_this_evidence")),
            blocking_reasons=list(same_window.get("promotion_gap", [])),
        ),
        promotion_item(
            item_id="ra2021_double_local_source_policy_candidate",
            source="ra2021_double_local_source_policy_candidate_evidence",
            artifact_status=double_candidate.get("status"),
            existing_rows=int(double_candidate.get("ok_row_count") or 0),
            source_policy_rows_closed=int(double_candidate.get("source_policy_rows_closed_by_this_evidence") or 0),
            promotion_ready=bool(double_candidate.get("promotion_ready")),
            b4_can_close=bool(double_candidate.get("b4_can_close_from_this_evidence")),
            b7_can_close=bool(double_candidate.get("b7_can_close_from_this_evidence")),
            blocking_reasons=list(double_candidate.get("promotion_blockers", [])),
        ),
        promotion_item(
            item_id="hi2022_full_t8_selected_candidate",
            source="hi2022_full_t8_source_policy_candidate_evidence",
            artifact_status=hi2022_candidate.get("status"),
            existing_rows=int(hi2022_candidate.get("row_count") or 0),
            source_policy_rows_closed=int(hi2022_candidate.get("source_policy_rows_closed_by_this_evidence") or 0),
            promotion_ready=bool(hi2022_candidate.get("promotion_ready")),
            b4_can_close=bool(hi2022_candidate.get("b4_can_close_from_this_evidence")),
            b7_can_close=bool(hi2022_candidate.get("b7_can_close_from_this_evidence")),
            blocking_reasons=list(hi2022_candidate.get("promotion_blockers", [])),
        ),
        promotion_item(
            item_id="hi2022_b4_b7_figure_scope_demotion",
            source="hi2022_b4_b7_figure_scope_demotion_evidence",
            artifact_status=hi2022_demotion.get("status"),
            existing_rows=int(hi2022_demotion.get("t8_selected_candidate_matrix_rows_total") or 0),
            source_policy_rows_closed=int(hi2022_demotion.get("source_policy_rows_closed_by_hi2022") or 0),
            promotion_ready=False,
            b4_can_close=bool(hi2022_demotion.get("b4_can_close_from_this_evidence")),
            b7_can_close=bool(hi2022_demotion.get("b7_can_close_from_this_evidence")),
            blocking_reasons=list(hi2022_demotion.get("promotion_gap", [])),
        ),
        promotion_item(
            item_id="tfe_same_test_and_runner_preflight",
            source="tfe_source_policy_runner_equivalence_preflight_evidence",
            artifact_status=tfe.get("status"),
            existing_rows=int(diagnostic.get("tfe_same_test_ok_rows") or 0),
            source_policy_rows_closed=int(tfe.get("source_policy_rows_closed_by_preflight") or 0),
            promotion_ready=bool(tfe.get("can_close_tfe_lane_from_preflight")),
            b4_can_close=bool(tfe.get("b4_b7_can_close_from_preflight")),
            b7_can_close=bool(tfe.get("b4_b7_can_close_from_preflight")),
            blocking_reasons=list(tfe.get("open_blocker_ids", [])),
            extra={
                "source_policy_execution_preflight_boundary": tfe_preflight_boundary,
                "terminal_reopen_condition": tfe_preflight_boundary.get("reopen_condition"),
                "execution_block_count": tfe_preflight_boundary.get("execution_block_count"),
                "ready_to_execute_source_policy_now": tfe_preflight_boundary.get(
                    "ready_to_execute_source_policy_now"
                ),
                "can_promote_any_tfe_source_policy_row_now": tfe_preflight_boundary.get(
                    "can_promote_any_tfe_source_policy_row_now"
                ),
            },
        ),
        promotion_item(
            item_id="vp2024_common_reference_proxy_and_public_recheck",
            source="vp2024_code_path_disposition_and_public_recheck",
            artifact_status=vp_recheck.get("status"),
            existing_rows=int(vp_coverage.get("common_reference_proxy_rows") or 0),
            source_policy_rows_closed=int(vp_claim_boundary.get("source_policy_rows_closed") or 0),
            promotion_ready=False,
            b4_can_close=False,
            b7_can_close=False,
            blocking_reasons=[
                "distinct_public_vp2024_code_path_not_found",
                "coordinate_partitioning_proxy_is_not_source_policy_reproduction",
                "external_superiority_claim_not_allowed_for_vp2024_proxy",
            ],
        ),
    ]

    promotion_ready_items = [item for item in items if item["promotion_ready_without_new_execution"]]
    b4_closing_items = [item for item in items if item["b4_can_close_from_this_artifact"]]
    b7_closing_items = [item for item in items if item["b7_can_close_from_this_artifact"]]
    source_rows_closed = sum(int(item["source_policy_rows_closed_by_this_artifact"]) for item in items)

    output: dict[str, Any] = {
        "schema": "b4-existing-artifact-promotion-audit-v1",
        "status": "no_existing_artifact_promotable_without_new_source_policy_execution",
        "read_only": True,
        "source_plan": "B4_SOURCE_POLICY_WORK_PRECISION_EXECUTION_PLAN.json",
        "source_files": [
            "B4_SOURCE_POLICY_WORK_PRECISION_EXECUTION_PLAN.json",
            "TFE_DAE_RUNNER_CONTRACT_GAP_AUDIT.json",
            "VP2024_CODE_PATH_DISPOSITION_AUDIT.json",
            "VP2024_PUBLIC_CODE_RECHECK_20260613.json",
            "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.json",
        ],
        "tfe_execution_preflight_status": tfe_preflight_boundary.get("status"),
        "tfe_execution_preflight_ready_now": tfe_preflight_boundary.get(
            "ready_to_execute_source_policy_now"
        ),
        "tfe_execution_preflight_can_promote_now": tfe_preflight_boundary.get(
            "can_promote_any_tfe_source_policy_row_now"
        ),
        "tfe_execution_preflight_execution_block_count": tfe_preflight_boundary.get(
            "execution_block_count"
        ),
        "tfe_execution_preflight_reopen_condition": tfe_preflight_boundary.get("reopen_condition"),
        "public_code_refresh_status": public_refresh.get("status"),
        "public_code_refresh_unable_to_reproduce_rows": public_refresh.get("unable_to_reproduce_rows"),
        "public_code_refresh_source_policy_rows_closed": public_refresh.get("source_policy_rows_closed"),
        "candidate_item_count": len(items),
        "promotion_ready_without_new_execution_count": len(promotion_ready_items),
        "b4_closing_item_count": len(b4_closing_items),
        "b7_closing_item_count": len(b7_closing_items),
        "source_policy_rows_closed_by_existing_artifacts": source_rows_closed,
        "source_policy_rows_total": current.get("source_policy_rows_total"),
        "b4_can_close_now": False,
        "b7_can_close_now": False,
        "heavy_numerical_run_invoked": False,
        "run_v047_invoked": False,
        "v048_runner_invoked": False,
        "promotion_items": items,
        "next_required_action": (
            "run or explicitly demote source-policy work/precision lanes; current artifacts remain "
            "diagnostic, incomplete, mixed-policy, or below acceptance"
        ),
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# B4 Existing-Artifact Promotion Audit",
        "",
        f"Status: `{output['status']}`.",
        "",
        "This is a read-only audit over existing artifacts. It does not run source-policy numerical experiments.",
        "",
        f"- Candidate items: `{output['candidate_item_count']}`.",
        f"- Promotion-ready without new execution: `{output['promotion_ready_without_new_execution_count']}`.",
        f"- B4/B7 closing items: `{output['b4_closing_item_count']}/{output['b7_closing_item_count']}`.",
        f"- Source-policy rows closed by existing artifacts: `{output['source_policy_rows_closed_by_existing_artifacts']}/{output['source_policy_rows_total']}`.",
        f"- Heavy/run_v047/v048 invoked: `{output['heavy_numerical_run_invoked']}/{output['run_v047_invoked']}/{output['v048_runner_invoked']}`.",
        f"- TFE execution preflight status/ready/promote/blocks: `{output['tfe_execution_preflight_status']}/{output['tfe_execution_preflight_ready_now']}/{output['tfe_execution_preflight_can_promote_now']}/{output['tfe_execution_preflight_execution_block_count']}`.",
        f"- TFE execution preflight reopen condition: `{output['tfe_execution_preflight_reopen_condition']}`.",
        "",
        "| item | existing rows | source rows closed | promotion-ready | B4/B7 close | first blocker |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for item in items:
        first_blocker = item["blocking_reasons"][0] if item["blocking_reasons"] else "none"
        lines.append(
            f"| `{item['id']}` | `{item['existing_rows']}` | "
            f"`{item['source_policy_rows_closed_by_this_artifact']}` | "
            f"`{item['promotion_ready_without_new_execution']}` | "
            f"`{item['b4_can_close_from_this_artifact']}/{item['b7_can_close_from_this_artifact']}` | "
            f"{first_blocker} |"
        )
    lines.extend(["", f"Next required action: {output['next_required_action']}.", ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("b4_existing_artifact_promotion_audit=written")
    print(f"candidate_items={output['candidate_item_count']}")
    print(f"promotion_ready_without_new_execution={output['promotion_ready_without_new_execution_count']}")
    print(f"source_policy_rows_closed_by_existing_artifacts={source_rows_closed}")
    print("b4_can_close_now=False")
    print("b7_can_close_now=False")


if __name__ == "__main__":
    main()
