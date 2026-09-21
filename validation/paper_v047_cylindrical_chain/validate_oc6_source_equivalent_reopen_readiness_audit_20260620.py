#!/usr/bin/env python3
"""Validate the OC6 source-equivalent reopen-readiness audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import build_oc6_source_equivalent_reopen_readiness_audit_20260620 as builder


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "OC6_SOURCE_EQUIVALENT_REOPEN_READINESS_AUDIT_20260620.json"
AUDIT_MD = PAPER / "OC6_SOURCE_EQUIVALENT_REOPEN_READINESS_AUDIT_20260620.md"
EXPECTED_SAFE_ACTION_IDS = [
    "rebuild_read_only_audit_chain",
    "rerun_read_only_validators",
    "keep_narrowed_archive_provenance_only",
    "monitor_reopen_conditions",
]
EXPECTED_OPT_IN_ACTION_IDS = ["authorized_b4_ra_hi_source_policy_execution"]
EXPECTED_APPROVAL_STATEMENT = (
    "I explicitly approve running the B4 source-policy execution commands listed in "
    "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json."
)
EXPECTED_BLOCKER_OPEN_BY_ID = {"OC4": True, "OC6": True, "OC12": True}
EXPECTED_BLOCKER_CLOSURE_DECISION_BY_ID = {
    "OC4": "remain_open_ready_for_authorized_execution_not_executed_not_promoted",
    "OC6": "remain_open_no_positive_source_equivalent_artifact",
    "OC12": "remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready",
}
EXPECTED_BLOCKER_CLOSURE_ALLOWED_BY_ID = {"OC4": False, "OC6": False, "OC12": False}
EXPECTED_BLOCKER_OPEN_TOKEN = "blocker_open_by_id=OC4:True,OC6:True,OC12:True"
EXPECTED_BLOCKER_CLOSURE_DECISION_TOKEN = (
    "blocker_closure_decision_by_id="
    "OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,"
    "OC6:remain_open_no_positive_source_equivalent_artifact,"
    "OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready"
)
EXPECTED_BLOCKER_CLOSURE_ALLOWED_TOKEN = (
    "blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False"
)


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


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(AUDIT_JSON)
        text = AUDIT_MD.read_text(encoding="utf-8", errors="replace")
        expected = builder.build_payload()
    except Exception as exc:  # noqa: BLE001
        print(f"OC6 source-equivalent reopen-readiness audit validation: FAIL\n- {exc}")
        return 1

    checks.check(audit == expected, "audit JSON is stale relative to source artifacts")
    checks.check(audit.get("schema") == builder.SCHEMA, "schema changed")
    checks.check(audit.get("status") == builder.STATUS, "status changed")
    checks.check(audit.get("blocker_id") == "OC6", "blocker id changed")
    checks.check(audit.get("oc6_blocker_id") == "OC6", "OC6 blocker id alias changed")
    checks.check(audit.get("blocker_status") == "partial", "OC6 blocker status changed")
    checks.check(audit.get("oc6_blocker_status") == "partial", "OC6 blocker status alias changed")
    checks.check(audit.get("oc6_blocker_open") is True, "OC6 blocker was overclosed")
    checks.check(
        audit.get("closure_decision") == "remain_open_no_positive_source_equivalent_artifact",
        "OC6 closure decision changed",
    )
    checks.check(
        audit.get("oc6_closure_decision")
        == audit.get("closure_decision")
        == "remain_open_no_positive_source_equivalent_artifact",
        "OC6 closure decision alias changed",
    )
    checks.check(audit.get("oc6_closure_allowed_now") is False, "OC6 closure unexpectedly allowed")
    checks.check(
        audit.get("objective_blocker_matrix_status") == "global_objective_blockers_remain_open",
        "objective blocker matrix status changed",
    )
    checks.check(
        audit.get("blocker_open_by_id") == EXPECTED_BLOCKER_OPEN_BY_ID,
        "objective blocker open map changed",
    )
    checks.check(
        audit.get("blocker_closure_decision_by_id") == EXPECTED_BLOCKER_CLOSURE_DECISION_BY_ID,
        "objective blocker closure-decision map changed",
    )
    checks.check(
        audit.get("blocker_closure_allowed_by_id") == EXPECTED_BLOCKER_CLOSURE_ALLOWED_BY_ID,
        "objective blocker closure-allowed map changed",
    )
    checks.check(
        audit.get("source_equivalent_artifact_found") is False,
        "OC6 source-equivalent artifact unexpectedly found",
    )
    checks.check(
        audit.get("source_equivalent_artifact_rows") == 0,
        "OC6 source-equivalent artifact rows changed",
    )
    checks.check(
        audit.get("source_equivalent_artifact_required_to_close") is True,
        "OC6 lost source-equivalent-artifact closure requirement",
    )
    checks.check(
        audit.get("reopen_condition") == "suite_specific_source_equivalent_reopen_conditions",
        "OC6 reopen-condition alias changed",
    )
    checks.check(audit.get("reopen_condition_count") == 2, "OC6 reopen-condition count changed")
    checks.check(
        audit.get("reopen_condition_by_suite") == builder.SUITE_REOPEN_CONDITIONS,
        "OC6 reopen-condition-by-suite alias changed",
    )
    checks.check(
        audit.get("tfe_reopen_condition")
        == "new_public_or_source_code_equivalent_tfe_implementation_artifact",
        "TFE reopen condition alias changed",
    )
    checks.check(
        audit.get("tfe_source_equivalent_reopen_condition")
        == audit.get("tfe_reopen_condition"),
        "TFE source-equivalent reopen condition alias changed",
    )
    checks.check(
        audit.get("vp_reopen_condition")
        == "new_distinct_public_vp2024_velocity_partitioning_code_path",
        "VP reopen condition alias changed",
    )
    checks.check(
        audit.get("vp_source_equivalent_reopen_condition")
        == audit.get("vp_reopen_condition"),
        "VP source-equivalent reopen condition alias changed",
    )
    checks.check(
        audit.get("source_equivalent_reopen_conditions") == builder.SUITE_REOPEN_CONDITIONS,
        "source-equivalent reopen condition map changed",
    )
    checks.check(audit.get("date_checked") == "2026-06-20", "date changed")
    checks.check(audit.get("read_only") is True, "audit must remain read-only")
    checks.check(audit.get("performs_new_public_code_search") is False, "audit performed a new public-code search")
    checks.check(audit.get("commands_executed_by_audit") is False, "audit executed commands")
    checks.check(audit.get("source_policy_execution_invoked") is False, "audit invoked source-policy execution")
    checks.check(audit.get("source_policy_execution_allowed_now") is False, "audit allowed source-policy execution")
    checks.check(
        audit.get("exact_b4_opt_in_required_for_execution") is True,
        "audit lost exact opt-in requirement",
    )
    checks.check(audit.get("safe_action_ids") == EXPECTED_SAFE_ACTION_IDS, "safe action ids changed")
    checks.check(audit.get("next_safe_action_ids") == EXPECTED_SAFE_ACTION_IDS, "next safe action ids changed")
    checks.check(audit.get("opt_in_action_ids") == EXPECTED_OPT_IN_ACTION_IDS, "opt-in action ids changed")
    checks.check(
        audit.get("required_user_approval_statement") == EXPECTED_APPROVAL_STATEMENT,
        "approval statement changed",
    )
    checks.check(
        audit.get("guarded_execution_driver") == "run_b4_source_policy_after_opt_in.sh",
        "guarded driver changed",
    )
    checks.check(audit.get("heavy_numerical_run_invoked") is False, "audit invoked heavy numerical run")
    checks.check(audit.get("run_v047_invoked") is False, "audit invoked run_v047")
    checks.check(audit.get("v048_runner_invoked") is False, "audit invoked v048")
    checks.check(audit.get("submission_ready") is False, "audit overclaimed submission readiness")
    checks.check(audit.get("oc6_can_close_now") is False, "audit overclosed OC6")
    checks.check(audit.get("external_superiority_claim_allowed") is False, "audit overclaimed external superiority")
    checks.check(set(audit.get("source_files", [])) == set(builder.SOURCE_FILES), "source files changed")

    checks.check(audit.get("rows_total") == audit.get("row_count") == 20, "row total alias changed")
    checks.check(audit.get("row_count") == 20, "row count changed")
    checks.check(audit.get("tfe_rows") == 16, "TFE row count changed")
    checks.check(audit.get("vp_rows") == 4, "VP row count changed")
    checks.check(audit.get("unable_to_reproduce_rows") == 20, "unable row count changed")
    checks.check(audit.get("public_code_available_rows") == 0, "public-code available rows changed")
    checks.check(audit.get("candidate_runner_available_rows") == 20, "candidate runner available row count changed")
    checks.check(audit.get("candidate_runner_source_policy_equivalent_rows") == 0, "source-equivalent candidate row count changed")
    checks.check(audit.get("source_policy_rows_closed") == 0, "source-policy rows overclosed")
    checks.check(audit.get("source_policy_closed_ratio") == "0/20", "source-policy closed ratio changed")
    checks.check(audit.get("source_policy_rows_promoted") == 0, "source-policy rows overpromoted")
    checks.check(audit.get("external_superiority_ready_rows") == 0, "external superiority rows overclaimed")
    checks.check(audit.get("positive_public_code_artifact_rows") == 0, "positive public-code rows changed")
    checks.check(audit.get("local_positive_reopen_artifact_rows") == 0, "local positive reopen rows changed")
    checks.check(audit.get("source_policy_reopen_triggered") is False, "reopen unexpectedly triggered")
    checks.check(
        audit.get("latest_external_probe_date_checked") == "2026-06-21",
        "latest external probe date changed",
    )
    checks.check(audit.get("latest_external_probe_count") == 9, "latest external probe count changed")
    checks.check(
        audit.get("latest_external_probe_positive_public_code_artifact_rows") == 0,
        "latest external probe positive rows changed",
    )
    checks.check(
        audit.get("latest_external_probe_source_policy_rows_closed") == 0,
        "latest external probe overclosed source-policy rows",
    )
    checks.check(
        audit.get("latest_external_probe_access_limited_count") == 4,
        "latest external probe access-limited count changed",
    )
    checks.check(
        audit.get("latest_external_probe_global_absence_proved") is False,
        "latest external probe overproved global absence",
    )
    checks.check(
        audit.get("latest_external_probe_source_policy_reopen_triggered") is False,
        "latest external probe unexpectedly triggered reopen",
    )
    checks.check(
        audit.get("latest_external_probe_marker") == "2026-06-21/9/0/0/4/False/False",
        "latest external probe marker changed",
    )
    latest_boundary = audit.get("latest_external_probe_boundary", {})
    checks.check(
        latest_boundary
        == {
            "marker": "2026-06-21/9/0/0/4/False/False",
            "access_limited_count": 4,
            "global_absence_proved": False,
            "positive_public_code_artifact_rows": 0,
            "source_policy_rows_closed": 0,
            "source_policy_reopen_triggered": False,
            "access_limited_rows_are_not_positive_evidence": True,
            "access_limited_rows_do_not_prove_global_absence": True,
        },
        "latest external probe boundary changed",
    )
    latest_rows = audit.get("latest_external_probe_rows", [])
    if not isinstance(latest_rows, list):
        latest_rows = []
        checks.check(False, "latest external probe rows must be a list")
    checks.check(len(latest_rows) == 9, "latest external probe row count changed")
    checks.check(
        audit.get("latest_external_probe_rows_by_suite")
        == {"tfe2026_original_pendulum": 5, "vp2024_velocity_partitioning": 4},
        "latest external probe suite counts changed",
    )
    checks.check(
        sum(1 for row in latest_rows if row.get("suite_id") == "tfe2026_original_pendulum") == 5,
        "latest external TFE probe count changed",
    )
    checks.check(
        sum(1 for row in latest_rows if row.get("suite_id") == "vp2024_velocity_partitioning") == 4,
        "latest external VP probe count changed",
    )
    checks.check(
        not any(row.get("positive_public_code_artifact_found") is True for row in latest_rows),
        "latest external probe found unexpected positive artifact",
    )
    checks.check(
        sum(int(row.get("source_policy_rows_closed_by_probe") or 0) for row in latest_rows) == 0,
        "latest external probe closed source-policy rows",
    )
    checks.check(
        sum(1 for row in latest_rows if row.get("access_limited") is True) == 4,
        "latest external access-limited row count changed",
    )
    checks.check(
        any(
            row.get("interface") == "github_rest_search_api"
            and row.get("access_limited") is True
            for row in latest_rows
        ),
        "latest external probe missing GitHub REST rate-limit row",
    )
    checks.check(
        any(
            row.get("interface") == "github_html_code_search"
            and row.get("access_limited") is True
            for row in latest_rows
        ),
        "latest external probe missing GitHub HTML code-search rate-limit row",
    )
    checks.check(
        any(
            row.get("interface") == "github_html_repository_search"
            and row.get("observation") == "github_html_repository_search_parseable_zero_results"
            and row.get("parseable_result_count") == 0
            for row in latest_rows
        ),
        "latest external probe missing parseable GitHub repository zero-result row",
    )

    reopen = audit.get("reopen_summary", {})
    checks.check(
        reopen.get("public_refresh_status")
        == "public_code_refresh_20260620_no_positive_new_source_artifact_rows_remain_unable_to_reproduce",
        "public refresh status changed",
    )
    checks.check(reopen.get("public_refresh_date_checked") == "2026-06-20", "public refresh date changed")
    checks.check(reopen.get("public_refresh_rows") == 20, "public refresh row count changed")
    checks.check(reopen.get("public_refresh_current_queries") == 11, "public refresh query count changed")
    checks.check(reopen.get("public_refresh_positive_public_code_artifact_rows") == 0, "public refresh positive rows changed")
    checks.check(
        reopen.get("public_refresh_local_positive_reopen_artifact_rows") == 0,
        "public refresh local-positive rows changed",
    )
    checks.check(
        reopen.get("public_refresh_source_policy_reopen_triggered") is False,
        "public refresh reopen-triggered alias changed",
    )
    checks.check(reopen.get("public_refresh_source_policy_rows_closed") == 0, "public refresh overclosed rows")
    checks.check(
        reopen.get("public_refresh_latest_external_probe_marker")
        == audit.get("latest_external_probe_marker")
        == "2026-06-21/9/0/0/4/False/False",
        "public refresh latest external probe marker changed",
    )
    for key in [
        "latest_external_probe_date_checked",
        "latest_external_probe_count",
        "latest_external_probe_positive_public_code_artifact_rows",
        "latest_external_probe_source_policy_rows_closed",
        "latest_external_probe_access_limited_count",
        "latest_external_probe_global_absence_proved",
        "latest_external_probe_source_policy_reopen_triggered",
    ]:
        checks.check(reopen.get(key) == audit.get(key), f"reopen summary missing {key}")
    checks.check(
        reopen.get("reopen_monitor_status")
        == "reopen_conditions_monitored_no_positive_source_artifact_source_policy_open",
        "reopen monitor status changed",
    )
    checks.check(reopen.get("reopen_monitor_unable_to_reproduce_rows") == 20, "reopen monitor unable rows changed")
    checks.check(reopen.get("reopen_monitor_source_policy_reopen_triggered") is False, "reopen monitor triggered")

    tfe = audit.get("tfe_reopen_summary", {})
    checks.check(tfe.get("self_reproduction_status") == "attempted_not_reproducible_not_promoted", "TFE self-reproduction status changed")
    checks.check(tfe.get("self_reproduction_source_policy_closed_ratio") == "0/16", "TFE source-policy ratio changed")
    checks.check(tfe.get("self_reproduction_unable_to_reproduce_rows") == 16, "TFE unable rows changed")
    checks.check(tfe.get("public_code_recheck_repository_hits") == 0, "TFE repository hits changed")
    checks.check(tfe.get("public_code_recheck_user_hits") == 0, "TFE user hits changed")
    checks.check(tfe.get("public_code_recheck_direct_code_hits") == 0, "TFE direct code hits changed")
    checks.check(tfe.get("brown_mcphee_source_code_equivalent_law") is False, "Brown-McPhee source equivalence changed")
    checks.check(tfe.get("full_T10_endpoint_policy_resolved") is False, "TFE full-T10 endpoint policy unexpectedly resolved")
    checks.check(tfe.get("source_policy_execution_preflight_status") == "terminal_no_public_code_self_reproduction_attempted_not_promoted", "TFE execution preflight status changed")
    checks.check(tfe.get("ready_to_execute_source_policy_now") is False, "TFE unexpectedly ready to execute")
    checks.check(tfe.get("can_promote_any_tfe_source_policy_row_now") is False, "TFE unexpectedly promotable")
    checks.check(tfe.get("execution_block_count") == 4, "TFE execution block count changed")
    checks.check(tfe.get("effective_missing_contract_block_count") == 4, "TFE effective missing block count changed")
    checks.check(tfe.get("terminal_nonpromoted_contract_block_count") == 2, "TFE terminal block count changed")
    checks.check(tfe.get("requires_new_public_or_source_code_equivalent_artifact_to_reopen") is True, "TFE reopen requirement changed")
    checks.check(tfe.get("source_policy_rows_completed") == 0, "TFE overclosed source-policy rows")
    checks.check(tfe.get("runner_contract_entrypoints") == 3, "TFE runner entrypoint count changed")
    checks.check(tfe.get("runner_contract_callable") == 3, "TFE runner callable count changed")
    checks.check(tfe.get("runner_contract_candidate_backed") == 3, "TFE runner candidate-backed count changed")
    checks.check(tfe.get("runner_contract_source_policy_equivalent_blocks") == 0, "TFE source-equivalent block count changed")
    checks.check(tfe.get("runner_contract_requires_new_artifact_or_execution_blocks") == 4, "TFE required block count changed")
    runner_contract = audit.get("runner_contract_summary", {})
    checks.check(
        runner_contract.get("status") == "contract_entrypoints_callable_candidate_backed_source_policy_open",
        "runner contract summary status changed",
    )
    checks.check(runner_contract.get("entrypoint_count") == 3, "runner contract summary entrypoint count changed")
    checks.check(
        runner_contract.get("callable_contract_count") == 3,
        "runner contract summary callable count changed",
    )
    checks.check(
        runner_contract.get("candidate_backed_contract_count") == 3,
        "runner contract summary candidate-backed count changed",
    )
    checks.check(
        runner_contract.get("source_policy_equivalent_blocks") == 0,
        "runner contract summary source-equivalent blocks changed",
    )
    checks.check(
        runner_contract.get("requires_new_artifact_or_execution_blocks") == 4,
        "runner contract summary requires-new blocks changed",
    )
    checks.check(
        runner_contract.get("safe_current_use")
        == "runner_contract_preflight_only_not_source_policy_reproduction",
        "runner contract summary safe-current-use changed",
    )

    vp = audit.get("vp_reopen_summary", {})
    checks.check(vp.get("public_code_recheck_status") == "public_code_rechecked_no_distinct_vp2024_path_attempted_not_reproducible", "VP public recheck status changed")
    checks.check(vp.get("source_policy_rows_attempted_not_reproducible") == 4, "VP attempted rows changed")
    checks.check(vp.get("source_policy_rows_closed") == 0, "VP overclosed rows")
    checks.check(vp.get("tree_total_paths") == 4487, "VP tree path count changed")
    checks.check(vp.get("year2024_path_count") == 1540, "VP 2024 path count changed")
    checks.check(vp.get("keyword_path_hit_count") == 0, "VP keyword hit count changed")
    checks.check(vp.get("can_close_vp2024_source_policy_rows_now") is False, "VP unexpectedly closable")
    checks.check(vp.get("row_disposition") == "attempted_not_reproducible_not_promoted", "VP row disposition changed")

    suites = {item.get("suite_id"): item for item in audit.get("suite_summary", [])}
    checks.check(suites.get("tfe2026_original_pendulum", {}).get("row_count") == 16, "TFE suite count changed")
    checks.check(suites.get("vp2024_velocity_partitioning", {}).get("row_count") == 4, "VP suite count changed")
    for suite_id, condition in builder.SUITE_REOPEN_CONDITIONS.items():
        suite = suites.get(suite_id, {})
        checks.check(suite.get("unable_to_reproduce_rows") == suite.get("row_count"), f"{suite_id} unable count changed")
        checks.check(suite.get("public_code_available_rows") == 0, f"{suite_id} public-code rows changed")
        checks.check(suite.get("candidate_runner_source_policy_equivalent_rows") == 0, f"{suite_id} source-equivalent rows changed")
        checks.check(suite.get("source_policy_closed_rows") == 0, f"{suite_id} overclosed rows")
        checks.check(suite.get("reopen_condition") == condition, f"{suite_id} reopen condition changed")

    for token in [
        "Status: `oc6_reopen_conditions_monitored_no_positive_source_equivalent_artifact`.",
        "Rows TFE/VP/total: `16/4/20`.",
        "Unable-to-reproduce rows: `20`.",
        "Public-code available rows: `0`.",
        "Candidate runner available/source-policy-equivalent rows: `20/0`.",
        "Positive public/local reopen artifact rows: `0/0`.",
        "Source-policy rows closed/promoted: `0/0`.",
        "Source-policy closed ratio: `0/20`.",
        "Blocker/status/closure decision: `OC6/partial/remain_open_no_positive_source_equivalent_artifact`.",
        "OC6 aliases blocker/status/closure/allowed-now: `OC6/partial/remain_open_no_positive_source_equivalent_artifact/False`.",
        "Source-equivalent artifact found/rows/required-to-close: `False/0/True`.",
        "Reopen condition alias/count: `suite_specific_source_equivalent_reopen_conditions/2`.",
        "TFE/VP reopen conditions: `new_public_or_source_code_equivalent_tfe_implementation_artifact` / `new_distinct_public_vp2024_velocity_partitioning_code_path`.",
        "OC6 can close now / external-superiority allowed / submission ready: `False/False/False`.",
        "New public-code search performed: `False`.",
        "Source-policy execution allowed now/invoked/exact opt-in required: `False/False/True`.",
        "Safe action ids: `rebuild_read_only_audit_chain,rerun_read_only_validators,keep_narrowed_archive_provenance_only,monitor_reopen_conditions`.",
        "Opt-in action ids: `authorized_b4_ra_hi_source_policy_execution`.",
        "## Objective Blocker Matrix",
        "This audit records OC6 source-equivalent reopen readiness. It does not close the global objective blockers.",
        f"`{EXPECTED_BLOCKER_OPEN_TOKEN}`",
        f"`{EXPECTED_BLOCKER_CLOSURE_DECISION_TOKEN}`",
        f"`{EXPECTED_BLOCKER_CLOSURE_ALLOWED_TOKEN}`",
        "Public refresh: `public_code_refresh_20260620_no_positive_new_source_artifact_rows_remain_unable_to_reproduce` on `2026-06-20`; rows/queries/positive/closed `20/11/0/0`.",
        "Latest external probe: `2026-06-21/9/0/0/4/False/False`.",
        "Latest external probe marker: `2026-06-21/9/0/0/4/False/False`.",
        "Latest external probe boundary positive/closed/access-limited/global-absence/reopen: `0/0/4/False/False`.",
        "Public refresh local-positive/reopen-triggered aliases: `0/False`.",
        "Latest probe reading rule: access-limited searches are not positive artifact evidence and do not prove global absence.",
        "TFE runner contract entrypoints/callable/candidate-backed/source-equivalent-blocks/requires-new: `3/3/3/0/4`.",
        "VP public recheck: `public_code_rechecked_no_distinct_vp2024_path_attempted_not_reproducible`; attempted/closed/tree/year2024/keyword-hits `4/0/4487/1540/0`.",
        "OC6 remains open.",
    ]:
        checks.check(token in text, f"markdown missing token: {token}")

    if checks.errors:
        print("OC6 source-equivalent reopen-readiness audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print(
        "OC6 source-equivalent reopen-readiness audit validation: PASS "
        f"rows={audit.get('row_count')} "
        f"unable={audit.get('unable_to_reproduce_rows')} "
        f"source_equivalent={audit.get('candidate_runner_source_policy_equivalent_rows')} "
        f"source_policy_closed={audit.get('source_policy_rows_closed')} "
        f"closure_decision={audit.get('closure_decision')} "
        f"oc6_blocker_id={audit.get('oc6_blocker_id')} "
        f"oc6_blocker_status={audit.get('oc6_blocker_status')} "
        f"oc6_closure_decision={audit.get('oc6_closure_decision')} "
        f"oc6_closure_allowed_now={audit.get('oc6_closure_allowed_now')} "
        f"reopen_condition={audit.get('reopen_condition')} "
        f"artifact_found={audit.get('source_equivalent_artifact_found')} "
        f"latest_external_probe={audit.get('latest_external_probe_date_checked')}/"
        f"{audit.get('latest_external_probe_count')}/"
        f"{audit.get('latest_external_probe_positive_public_code_artifact_rows')}/"
        f"{audit.get('latest_external_probe_source_policy_rows_closed')}/"
        f"{audit.get('latest_external_probe_access_limited_count')}/"
        f"{audit.get('latest_external_probe_global_absence_proved')}/"
        f"{audit.get('latest_external_probe_source_policy_reopen_triggered')} "
        "latest_external_probe_boundary="
        f"{audit.get('latest_external_probe_boundary', {}).get('positive_public_code_artifact_rows')}/"
        f"{audit.get('latest_external_probe_boundary', {}).get('source_policy_rows_closed')}/"
        f"{audit.get('latest_external_probe_boundary', {}).get('access_limited_count')}/"
        f"{audit.get('latest_external_probe_boundary', {}).get('global_absence_proved')}/"
        f"{audit.get('latest_external_probe_boundary', {}).get('source_policy_reopen_triggered')}"
    )
    print(EXPECTED_BLOCKER_OPEN_TOKEN)
    print(EXPECTED_BLOCKER_CLOSURE_DECISION_TOKEN)
    print(EXPECTED_BLOCKER_CLOSURE_ALLOWED_TOKEN)
    return 0


if __name__ == "__main__":
    sys.exit(main())
