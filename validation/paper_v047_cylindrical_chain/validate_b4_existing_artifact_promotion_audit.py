#!/usr/bin/env python3
"""Validate the B4 existing-artifact promotion audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
EXPECTED_ITEMS = {
    "ra2021_public_baseline_shards",
    "gauss6_public_horizon_local_rows",
    "ra2021_closed_loop_same_window_work_precision",
    "ra2021_double_local_source_policy_candidate",
    "hi2022_full_t8_selected_candidate",
    "hi2022_b4_b7_figure_scope_demotion",
    "tfe_same_test_and_runner_preflight",
    "vp2024_common_reference_proxy_and_public_recheck",
}


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


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def expected_tfe_execution_preflight_boundary(tfe_gap: dict[str, Any]) -> dict[str, Any]:
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


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(PAPER / "B4_EXISTING_ARTIFACT_PROMOTION_AUDIT.json")
        audit_md = read_text(PAPER / "B4_EXISTING_ARTIFACT_PROMOTION_AUDIT.md")
        b4 = read_json(PAPER / "B4_SOURCE_POLICY_WORK_PRECISION_EXECUTION_PLAN.json")
        tfe_gap = read_json(PAPER / "TFE_DAE_RUNNER_CONTRACT_GAP_AUDIT.json")
        public_refresh = read_json(PAPER / "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.json")
    except Exception as exc:  # noqa: BLE001
        print(f"b4 existing-artifact promotion audit validation: FAIL\n- {exc}")
        return 1

    items = {item.get("id"): item for item in audit.get("promotion_items", []) if isinstance(item, dict)}
    checks.check(audit.get("schema") == "b4-existing-artifact-promotion-audit-v1", "schema changed")
    checks.check(
        audit.get("status") == "no_existing_artifact_promotable_without_new_source_policy_execution",
        "status changed",
    )
    checks.check(audit.get("read_only") is True, "audit must be read-only")
    checks.check(audit.get("source_plan") == "B4_SOURCE_POLICY_WORK_PRECISION_EXECUTION_PLAN.json", "source plan changed")
    checks.check(audit.get("candidate_item_count") == 8, "candidate item count changed")
    checks.check(set(items) == EXPECTED_ITEMS, "promotion item set changed")
    source_files = set(audit.get("source_files", []))
    checks.check(
        "TFE_DAE_RUNNER_CONTRACT_GAP_AUDIT.json" in source_files,
        "missing TFE DAE runner contract gap source file",
    )
    checks.check("VP2024_CODE_PATH_DISPOSITION_AUDIT.json" in source_files, "missing VP2024 disposition source file")
    checks.check("VP2024_PUBLIC_CODE_RECHECK_20260613.json" in source_files, "missing VP2024 public recheck source file")
    checks.check(
        "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.json" in source_files,
        "missing 2026-06-14 public-code refresh source file",
    )
    checks.check(
        audit.get("public_code_refresh_status") == public_refresh.get("status"),
        "public-code refresh status not carried into existing-artifact audit",
    )
    checks.check(audit.get("public_code_refresh_unable_to_reproduce_rows") == 20, "refresh unable rows changed")
    checks.check(audit.get("public_code_refresh_source_policy_rows_closed") == 0, "refresh overclosed rows")
    checks.check(audit.get("promotion_ready_without_new_execution_count") == 0, "existing artifact unexpectedly promotable")
    checks.check(audit.get("b4_closing_item_count") == 0, "existing artifact unexpectedly closes B4")
    checks.check(audit.get("b7_closing_item_count") == 0, "existing artifact unexpectedly closes B7")
    checks.check(audit.get("source_policy_rows_closed_by_existing_artifacts") == 0, "existing artifacts overclose rows")
    checks.check(
        audit.get("source_policy_rows_total") == b4.get("current_evidence", {}).get("source_policy_rows_total") == 40,
        "source-policy total changed",
    )
    checks.check(audit.get("b4_can_close_now") is False, "audit overcloses B4")
    checks.check(audit.get("b7_can_close_now") is False, "audit overcloses B7")
    checks.check(audit.get("heavy_numerical_run_invoked") is False, "audit invoked heavy run")
    checks.check(audit.get("run_v047_invoked") is False, "audit invoked run_v047")
    checks.check(audit.get("v048_runner_invoked") is False, "audit invoked v048 runner")

    checks.check(items.get("ra2021_public_baseline_shards", {}).get("existing_rows") == 9, "RA2021 shard row count changed")
    checks.check(
        "needs matching Gauss6/FullVA local source-policy rows"
        in items.get("ra2021_public_baseline_shards", {}).get("blocking_reasons", []),
        "RA2021 shard blocker changed",
    )
    checks.check(items.get("gauss6_public_horizon_local_rows", {}).get("existing_rows") == 9, "Gauss6 local row count changed")
    checks.check(
        "closed-loop source-policy step trios are now complete but remain residual/kinematic rows rather than dynamic work/precision rows"
        in items.get("gauss6_public_horizon_local_rows", {}).get("blocking_reasons", []),
        "Gauss6 local blocker changed",
    )
    checks.check(
        items.get("ra2021_closed_loop_same_window_work_precision", {}).get("existing_rows") == 24,
        "same-window work/precision row count changed",
    )
    checks.check(
        "bounded T=0.1 diagnostic rows are not the RA2021 T=3 source-policy dynamic-order rows"
        in items.get("ra2021_closed_loop_same_window_work_precision", {}).get("blocking_reasons", []),
        "same-window blocker changed",
    )
    checks.check(
        "local and public error columns use different reference families"
        in items.get("ra2021_closed_loop_same_window_work_precision", {}).get("blocking_reasons", []),
        "same-window reference-family blocker changed",
    )
    checks.check(
        items.get("ra2021_double_local_source_policy_candidate", {}).get("existing_rows") == 3,
        "RA2021 double local candidate row count changed",
    )
    checks.check(
        "observed source-policy order is below sixth-order acceptance (pos=2.148, vel=2.463)"
        in items.get("ra2021_double_local_source_policy_candidate", {}).get("blocking_reasons", []),
        "RA2021 double local candidate blocker changed",
    )
    checks.check(
        items.get("hi2022_full_t8_selected_candidate", {}).get("existing_rows") == 24,
        "HI2022 selected candidate row count changed",
    )
    checks.check(
        "selected coarse trio is not the full encoded HI2022 public step family"
        in items.get("hi2022_full_t8_selected_candidate", {}).get("blocking_reasons", []),
        "HI2022 selected candidate blocker changed",
    )
    checks.check(
        items.get("hi2022_b4_b7_figure_scope_demotion", {}).get("existing_rows") == 24,
        "HI2022 demotion evidence row count changed",
    )
    checks.check(
        "HI2022 selected-candidate matrix has 7/8 completed coarse-trio shards; remaining partial/missing shards are ['rA_half:double_pendulum']"
        in items.get("hi2022_b4_b7_figure_scope_demotion", {}).get("blocking_reasons", []),
        "HI2022 demotion blocker changed",
    )
    checks.check(
        items.get("tfe_same_test_and_runner_preflight", {}).get("existing_rows") == 18,
        "TFE same-test row count changed",
    )
    tfe_item = items.get("tfe_same_test_and_runner_preflight", {})
    tfe_boundary = tfe_item.get("source_policy_execution_preflight_boundary", {})
    expected_tfe_boundary = expected_tfe_execution_preflight_boundary(tfe_gap)
    checks.check(tfe_boundary == expected_tfe_boundary, "TFE execution preflight boundary not mirrored")
    checks.check(
        audit.get("tfe_execution_preflight_status") == expected_tfe_boundary.get("status"),
        "top-level TFE preflight status not mirrored",
    )
    checks.check(
        audit.get("tfe_execution_preflight_ready_now")
        == expected_tfe_boundary.get("ready_to_execute_source_policy_now"),
        "top-level TFE preflight ready flag not mirrored",
    )
    checks.check(
        audit.get("tfe_execution_preflight_can_promote_now")
        == expected_tfe_boundary.get("can_promote_any_tfe_source_policy_row_now"),
        "top-level TFE preflight promotion flag not mirrored",
    )
    checks.check(
        audit.get("tfe_execution_preflight_execution_block_count")
        == expected_tfe_boundary.get("execution_block_count"),
        "top-level TFE preflight execution block count not mirrored",
    )
    checks.check(
        audit.get("tfe_execution_preflight_reopen_condition") == expected_tfe_boundary.get("reopen_condition"),
        "top-level TFE preflight reopen condition not mirrored",
    )
    checks.check(
        tfe_boundary.get("status") == "terminal_no_public_code_self_reproduction_attempted_not_promoted",
        "TFE preflight status changed",
    )
    checks.check(tfe_boundary.get("ready_to_execute_source_policy_now") is False, "TFE preflight became executable")
    checks.check(
        tfe_boundary.get("can_promote_any_tfe_source_policy_row_now") is False,
        "TFE preflight became promotable",
    )
    checks.check(tfe_boundary.get("source_policy_rows_completed") == 0, "TFE preflight closed rows")
    checks.check(tfe_boundary.get("execution_block_count") == 4, "TFE preflight execution block count changed")
    checks.check(
        "accepted_source_policy_work_precision_rows_not_executed_or_bound"
        in tfe_boundary.get("execution_blocks", []),
        "TFE preflight lost accepted-row execution block",
    )
    checks.check(
        tfe_boundary.get("nonheavy_blocks_dispositioned_by_demotion") is True,
        "TFE preflight lost nonheavy demotion disposition",
    )
    checks.check(
        tfe_boundary.get("nonheavy_demotion_does_not_close_source_policy") is True,
        "TFE preflight overclosed source-policy by demotion",
    )
    checks.check(tfe_boundary.get("explicit_user_opt_in_required") is False, "TFE preflight opt-in flag changed")
    checks.check(tfe_boundary.get("opt_in_required_for") == [], "TFE preflight opt-in list changed")
    checks.check(
        tfe_boundary.get("reopen_condition") == "new_public_or_source_code_equivalent_tfe_implementation_artifact",
        "TFE preflight reopen condition changed",
    )
    checks.check(tfe_boundary.get("heavy_numerical_run_invoked") is False, "TFE preflight invoked heavy run")
    checks.check(tfe_boundary.get("run_v047_invoked") is False, "TFE preflight invoked run_v047")
    checks.check(tfe_boundary.get("v048_runner_invoked") is False, "TFE preflight invoked v048 runner")
    checks.check(
        tfe_item.get("terminal_reopen_condition")
        == "new_public_or_source_code_equivalent_tfe_implementation_artifact",
        "TFE item terminal reopen condition changed",
    )
    checks.check(tfe_item.get("execution_block_count") == 4, "TFE item execution block count changed")
    checks.check(tfe_item.get("ready_to_execute_source_policy_now") is False, "TFE item became executable")
    checks.check(
        tfe_item.get("can_promote_any_tfe_source_policy_row_now") is False,
        "TFE item became promotable",
    )
    checks.check(
        "accepted_source_policy_work_precision_rows_not_executed_or_bound"
        in items.get("tfe_same_test_and_runner_preflight", {}).get("blocking_reasons", []),
        "TFE promotion blocker changed",
    )
    checks.check(
        items.get("vp2024_common_reference_proxy_and_public_recheck", {}).get("existing_rows") == 4,
        "VP2024 proxy row count changed",
    )
    checks.check(
        items.get("vp2024_common_reference_proxy_and_public_recheck", {}).get("artifact_status")
        == "public_code_rechecked_no_distinct_vp2024_path_attempted_not_reproducible",
        "VP2024 public recheck status changed",
    )
    checks.check(
        "distinct_public_vp2024_code_path_not_found"
        in items.get("vp2024_common_reference_proxy_and_public_recheck", {}).get("blocking_reasons", []),
        "VP2024 public-code blocker changed",
    )
    checks.check(
        "coordinate_partitioning_proxy_is_not_source_policy_reproduction"
        in items.get("vp2024_common_reference_proxy_and_public_recheck", {}).get("blocking_reasons", []),
        "VP2024 proxy blocker changed",
    )
    for item in items.values():
        checks.check(item.get("source_policy_rows_closed_by_this_artifact") == 0, f"{item.get('id')} overclosed rows")
        checks.check(item.get("promotion_ready_without_new_execution") is False, f"{item.get('id')} unexpectedly promotable")
        checks.check(item.get("b4_can_close_from_this_artifact") is False, f"{item.get('id')} overcloses B4")
        checks.check(item.get("b7_can_close_from_this_artifact") is False, f"{item.get('id')} overcloses B7")
        checks.check(item.get("blocking_reasons"), f"{item.get('id')} has no blocking reasons")

    for token in [
        "Status: `no_existing_artifact_promotable_without_new_source_policy_execution`.",
        "Candidate items: `8`.",
        "Promotion-ready without new execution: `0`.",
        "B4/B7 closing items: `0/0`.",
        "Source-policy rows closed by existing artifacts: `0/40`.",
        "Heavy/run_v047/v048 invoked: `False/False/False`.",
        "TFE execution preflight status/ready/promote/blocks: `terminal_no_public_code_self_reproduction_attempted_not_promoted/False/False/4`.",
        "TFE execution preflight reopen condition: `new_public_or_source_code_equivalent_tfe_implementation_artifact`.",
        "`ra2021_public_baseline_shards`",
        "`gauss6_public_horizon_local_rows`",
        "`ra2021_closed_loop_same_window_work_precision`",
        "`ra2021_double_local_source_policy_candidate`",
        "`hi2022_full_t8_selected_candidate`",
        "`hi2022_b4_b7_figure_scope_demotion`",
        "`tfe_same_test_and_runner_preflight`",
        "`vp2024_common_reference_proxy_and_public_recheck`",
        "Next required action: run or explicitly demote source-policy work/precision lanes",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("b4 existing-artifact promotion audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("b4 existing-artifact promotion audit validation: PASS")
    print("candidate_items=8")
    print("promotion_ready_without_new_execution=0")
    print("source_policy_rows_closed_by_existing_artifacts=0/40")
    print("b4_can_close_now=False")
    print("b7_can_close_now=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
