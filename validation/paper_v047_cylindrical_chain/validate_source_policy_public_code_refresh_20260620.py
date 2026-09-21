#!/usr/bin/env python3
"""Validate the 2026-06-20 source-policy public-code refresh supplement."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
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
        audit = read_json(PAPER / "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.json")
        text = (PAPER / "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.md").read_text(
            encoding="utf-8",
            errors="replace",
        )
        prior = read_json(PAPER / "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.json")
        self_attempt = read_json(PAPER / "SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json")
    except Exception as exc:  # noqa: BLE001
        print(f"Source-policy public-code refresh 20260620 validation: FAIL\n- {exc}")
        return 1

    suite_refreshes = [row for row in audit.get("suite_refreshes", []) if isinstance(row, dict)]
    by_suite = {row.get("suite_id"): row for row in suite_refreshes}
    tfe = by_suite.get("tfe2026_original_pendulum", {})
    vp = by_suite.get("vp2024_velocity_partitioning", {})

    checks.check(audit.get("schema") == "source-policy-public-code-refresh-20260620-v1", "schema changed")
    checks.check(
        audit.get("status")
        == "public_code_refresh_20260620_no_positive_new_source_artifact_rows_remain_unable_to_reproduce",
        "status changed",
    )
    checks.check(audit.get("date") == "2026-06-20", "date alias changed")
    checks.check(audit.get("date_checked") == "2026-06-20", "date changed")
    checks.check(audit.get("read_only") is True, "refresh must remain read-only")
    checks.check(audit.get("submission_ready") is False, "refresh overclaims submission readiness")
    checks.check(audit.get("supplemental_to") == "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.json", "prior pointer changed")
    checks.check(audit.get("row_count") == prior.get("row_count") == 20, "row count changed")
    checks.check(audit.get("rows") == audit.get("row_count") == 20, "rows alias changed")
    checks.check(audit.get("current_query_count") == 11, "current query count changed")
    checks.check(audit.get("current_queries") == audit.get("current_query_count") == 11, "current queries alias changed")
    checks.check(audit.get("query_count") == audit.get("current_query_count") == 11, "query count alias changed")
    checks.check(audit.get("positive_public_code_artifact_rows") == 0, "positive artifact rows changed")
    checks.check(audit.get("local_positive_reopen_artifact_rows") == 0, "local positive reopen rows changed")
    checks.check(audit.get("source_policy_reopen_triggered") is False, "refresh unexpectedly triggered reopen")
    checks.check(audit.get("public_code_available_rows") == 0, "public-code rows unexpectedly available")
    checks.check(audit.get("self_reproduction_attempted_rows") == 20, "attempted count changed")
    checks.check(audit.get("unable_to_reproduce_rows") == 20, "unable-to-reproduce count changed")
    checks.check(audit.get("source_policy_closed") is False, "refresh overcloses source policy")
    checks.check(audit.get("source_policy_closed_ratio") == "0/20", "source-policy closed ratio changed")
    checks.check(audit.get("source_policy_closed_rows") == 0, "source-policy closed row alias changed")
    checks.check(audit.get("source_policy_rows_closed") == 0, "refresh overcloses source-policy rows")
    checks.check(audit.get("source_policy_rows_promoted") == 0, "refresh overpromotes source-policy rows")
    checks.check(audit.get("external_superiority_ready_rows") == 0, "refresh overclaims external superiority")
    checks.check(audit.get("open_execution_queue_rows") == 0, "refresh should not reopen execution queue")
    checks.check(audit.get("heavy_numerical_run_invoked") is False, "refresh invoked heavy run")
    checks.check(audit.get("run_v047_invoked") is False, "refresh invoked run_v047")
    checks.check(audit.get("v048_runner_invoked") is False, "refresh invoked v048")
    checks.check(audit.get("b4_source_policy_execution_invoked") is False, "refresh invoked B4 source-policy execution")
    checks.check(audit.get("source_policy_execution_invoked") is False, "refresh invoked source-policy execution")
    checks.check(audit.get("source_policy_execution_allowed_now") is False, "refresh allowed source-policy execution")
    checks.check(
        audit.get("exact_b4_opt_in_required_for_execution") is True,
        "refresh lost exact opt-in requirement",
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

    policy = audit.get("evidence_policy", {})
    checks.check(policy.get("query_absence_is_global_absence_proof") is False, "query absence overclaimed")
    checks.check(
        policy.get("rate_limited_search_is_positive_artifact_evidence") is False,
        "rate-limited search overclaimed as positive evidence",
    )
    checks.check(
        policy.get("no_positive_query_result_action")
        == "retain_prior_unable_to_reproduce_not_promoted_disposition",
        "query result disposition changed",
    )
    checks.check(policy.get("not_reproducible_rows_are_source_policy_closed") is False, "policy overcloses")
    checks.check(
        policy.get("not_reproducible_rows_are_external_superiority_ready") is False,
        "policy overclaims external superiority",
    )

    checks.check(tfe.get("row_count") == 16, "TFE row count changed")
    checks.check(tfe.get("current_query_count") == 5, "TFE query count changed")
    checks.check(tfe.get("positive_public_code_artifact_found") is False, "TFE positive artifact overclaimed")
    checks.check(tfe.get("public_code_available_now") is False, "TFE public code unexpectedly available")
    checks.check(tfe.get("unable_to_reproduce_rows") == 16, "TFE unable rows changed")
    checks.check(tfe.get("source_policy_rows_closed") == 0, "TFE overclosed")
    checks.check(tfe.get("source_policy_rows_promoted") == 0, "TFE overpromoted")
    checks.check(tfe.get("external_superiority_ready_rows") == 0, "TFE overclaimed external superiority")
    checks.check(tfe.get("final_disposition") == "unable_to_reproduce_not_promoted", "TFE disposition changed")
    checks.check(
        tfe.get("reopen_condition") == "new_public_or_source_code_equivalent_tfe_implementation_artifact",
        "TFE reopen condition changed",
    )

    checks.check(vp.get("row_count") == 4, "VP row count changed")
    checks.check(vp.get("current_query_count") == 6, "VP query count changed")
    checks.check(vp.get("positive_public_code_artifact_found") is False, "VP positive artifact overclaimed")
    checks.check(vp.get("public_code_available_now") is False, "VP public code unexpectedly available")
    checks.check(vp.get("unable_to_reproduce_rows") == 4, "VP unable rows changed")
    checks.check(vp.get("source_policy_rows_closed") == 0, "VP overclosed")
    checks.check(vp.get("source_policy_rows_promoted") == 0, "VP overpromoted")
    checks.check(vp.get("external_superiority_ready_rows") == 0, "VP overclaimed external superiority")
    checks.check(vp.get("final_disposition") == "unable_to_reproduce_not_promoted", "VP disposition changed")
    checks.check(
        vp.get("reopen_condition") == "new_distinct_public_vp2024_velocity_partitioning_code_path",
        "VP reopen condition changed",
    )

    checks.check(self_attempt.get("row_count") == 20, "self-reproduction audit row count changed")
    checks.check(self_attempt.get("unable_to_reproduce_rows") == 20, "self-reproduction unable count changed")
    checks.check(self_attempt.get("source_policy_closed_rows") == 0, "self-reproduction overclosed rows")

    latest_probe = audit.get("latest_external_probe", {})
    latest_rows = [row for row in audit.get("latest_external_probe_rows", []) if isinstance(row, dict)]
    checks.check(latest_probe.get("date_checked") == "2026-06-21", "latest probe date changed")
    checks.check(audit.get("latest_external_probe_date_checked") == "2026-06-21", "latest probe date alias changed")
    checks.check(latest_probe.get("probe_count") == audit.get("latest_external_probe_count") == 9, "latest probe count changed")
    checks.check(len(latest_rows) == 9, "latest probe row count changed")
    checks.check(
        latest_probe.get("positive_public_code_artifact_rows")
        == audit.get("latest_external_probe_positive_public_code_artifact_rows")
        == 0,
        "latest probe overclaimed positive artifact rows",
    )
    checks.check(
        latest_probe.get("source_policy_rows_closed_by_probe")
        == audit.get("latest_external_probe_source_policy_rows_closed")
        == 0,
        "latest probe overclosed source-policy rows",
    )
    checks.check(
        latest_probe.get("access_limited_probe_count")
        == audit.get("latest_external_probe_access_limited_count")
        == 4,
        "latest probe access-limited count changed",
    )
    checks.check(
        latest_probe.get("parseable_zero_result_probe_count") == 1,
        "latest probe parseable zero-result count changed",
    )
    checks.check(
        latest_probe.get("global_absence_proved")
        == audit.get("latest_external_probe_global_absence_proved")
        is False,
        "latest probe overproved global absence",
    )
    checks.check(
        latest_probe.get("source_policy_reopen_triggered")
        == audit.get("latest_external_probe_source_policy_reopen_triggered")
        == audit.get("source_policy_reopen_triggered")
        is False,
        "latest probe unexpectedly reopened source policy",
    )
    checks.check(
        audit.get("latest_external_probe_marker")
        == "2026-06-21/9/0/0/4/False/False",
        "latest probe marker changed",
    )
    checks.check(
        sum(1 for row in latest_rows if row.get("suite_id") == "tfe2026_original_pendulum") == 5,
        "latest TFE probe row count changed",
    )
    checks.check(
        sum(1 for row in latest_rows if row.get("suite_id") == "vp2024_velocity_partitioning") == 4,
        "latest VP probe row count changed",
    )
    checks.check(
        all(row.get("positive_public_code_artifact_found") is False for row in latest_rows),
        "latest probe has unexpected positive artifact row",
    )
    checks.check(
        all(int(row.get("source_policy_rows_closed_by_probe") or 0) == 0 for row in latest_rows),
        "latest probe closed source-policy rows",
    )
    checks.check(
        any(
            row.get("interface") == "github_html_repository_search"
            and row.get("parseable_result_count") == 0
            for row in latest_rows
        ),
        "latest probe missing parseable GitHub zero-result record",
    )
    checks.check(
        any(row.get("observation") == "github_anonymous_api_rate_limited_no_search_result_obtained" for row in latest_rows),
        "latest probe missing GitHub API rate-limit record",
    )
    checks.check(
        any(
            row.get("observation") == "github_html_code_search_secondary_rate_limited_no_search_result_obtained"
            for row in latest_rows
        ),
        "latest probe missing GitHub HTML code-search rate-limit record",
    )

    for token in [
        "Status: `public_code_refresh_20260620_no_positive_new_source_artifact_rows_remain_unable_to_reproduce`.",
        "Supplemental to: `SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.json`.",
        "Rows refreshed: `20`.",
        "Current queries: `11`.",
        "Positive public-code artifact rows: `0`.",
        "Public-code-available rows: `0`.",
        "Source-policy closed ratio: `0/20`.",
        "Source-policy rows closed/promoted: `0/0`.",
        "Submission ready: `False`.",
        "Latest external probe date/count/positive/closed/access-limited/global-absence/reopened: `2026-06-21/9/0/0/4/False/False`.",
        "Latest external probe marker: `2026-06-21/9/0/0/4/False/False`.",
        "Local positive reopen artifact rows / source-policy reopen triggered: `0/False`.",
        "Source-policy execution allowed now/invoked/exact opt-in required: `False/False/True`.",
        "Safe action ids: `rebuild_read_only_audit_chain,rerun_read_only_validators,keep_narrowed_archive_provenance_only,monitor_reopen_conditions`.",
        "Opt-in action ids: `authorized_b4_ra_hi_source_policy_execution`.",
        "The 2026-06-21 supplemental probe found no positive public/source-code-equivalent artifact.",
        "`github_html_repository_search_parseable_zero_results`",
        "`github_anonymous_api_rate_limited_no_search_result_obtained`",
        "`github_html_code_search_secondary_rate_limited_no_search_result_obtained`",
        "Heavy/run_v047/v048/B4 invoked: `False/False/False/False`.",
        "`tfe2026_original_pendulum`",
        "`vp2024_velocity_partitioning`",
        "TFE: `new_public_or_source_code_equivalent_tfe_implementation_artifact`.",
        "VP2024: `new_distinct_public_vp2024_velocity_partitioning_code_path`.",
    ]:
        checks.check(token in text, f"markdown missing token: {token}")

    if checks.errors:
        print("Source-policy public-code refresh 20260620 validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("Source-policy public-code refresh 20260620 validation: PASS")
    print("rows=20")
    print("current_queries=11")
    print("positive_public_code_artifact_rows=0")
    print("latest_external_probe=2026-06-21/9/0/0/4/False/False")
    print("source_policy_closed=0")
    print("source_policy_closed_ratio=0/20")
    print("source_policy_execution_invoked=False")
    print("source_policy_execution_allowed_now=False")
    print("submission_ready=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
