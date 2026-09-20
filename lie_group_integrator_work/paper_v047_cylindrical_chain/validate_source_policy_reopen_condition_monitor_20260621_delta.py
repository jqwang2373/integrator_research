#!/usr/bin/env python3
"""Validate the 2026-06-21 source-policy reopen-condition delta monitor."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_json(data: Any) -> str:
    encoded = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def marker_from_recheck(recheck: dict[str, Any]) -> str:
    return (
        f"{recheck.get('date_checked')}/"
        f"{recheck.get('query_count')}/"
        f"{recheck.get('positive_public_code_artifact_rows')}/"
        f"{recheck.get('source_code_equivalent_artifact_rows')}/"
        f"{recheck.get('source_policy_rows_closed_by_recheck')}/"
        f"{recheck.get('source_policy_reopen_triggered')}/"
        f"{recheck.get('global_absence_proved')}"
    )


def main() -> int:
    checks = Checks()
    try:
        monitor = read_json(PAPER / "SOURCE_POLICY_REOPEN_CONDITION_MONITOR_20260621_DELTA.json")
        text = (PAPER / "SOURCE_POLICY_REOPEN_CONDITION_MONITOR_20260621_DELTA.md").read_text(
            encoding="utf-8",
            errors="replace",
        )
        prior_monitor = read_json(PAPER / "SOURCE_POLICY_REOPEN_CONDITION_MONITOR_20260620.json")
        oc6_recheck = read_json(PAPER / "OC6_EXTERNAL_SOURCE_ARTIFACT_RECHECK_20260621.json")
        oc6_reopen = read_json(PAPER / "OC6_SOURCE_EQUIVALENT_REOPEN_READINESS_AUDIT_20260620.json")
        public_refresh = read_json(PAPER / "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.json")
        full_gap = read_json(PAPER / "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json")
    except Exception as exc:  # noqa: BLE001
        print(f"source-policy reopen-condition 20260621 delta validation: FAIL\n- {exc}")
        return 1

    expected_source_files = [
        "SOURCE_POLICY_REOPEN_CONDITION_MONITOR_20260620.json",
        "OC6_EXTERNAL_SOURCE_ARTIFACT_RECHECK_20260621.json",
        "OC6_SOURCE_EQUIVALENT_REOPEN_READINESS_AUDIT_20260620.json",
        "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.json",
        "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json",
    ]
    expected_source_artifact_sha256 = {
        name: sha256_file(manuscript_path(name))
        for name in expected_source_files
        if name != "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json"
    }
    expected_oc6_marker = marker_from_recheck(oc6_recheck)
    expected_combined_digest = sha256_json(
        {
            "date_checked": "2026-06-21",
            "prior_monitor_evidence_digest": prior_monitor.get("monitor_evidence_digest"),
            "prior_monitor_local_scan_digest": prior_monitor.get("local_scan_digest"),
            "legacy_probe_marker": prior_monitor.get("latest_external_probe_marker"),
            "oc6_external_source_artifact_recheck_marker": expected_oc6_marker,
            "terminal_reopen_conditions": prior_monitor.get("terminal_reopen_conditions"),
            "source_artifact_sha256": expected_source_artifact_sha256,
            "source_policy_reopen_triggered": False,
            "source_policy_rows_closed_by_delta": 0,
        }
    )

    checks.check(
        monitor.get("schema") == "source-policy-reopen-condition-monitor-20260621-delta-v1",
        "schema changed",
    )
    checks.check(
        monitor.get("status") == "current_day_delta_no_positive_source_artifact_source_policy_open",
        "status changed",
    )
    checks.check(monitor.get("date_checked") == "2026-06-21", "date changed")
    checks.check(monitor.get("read_only") is True, "monitor must remain read-only")
    checks.check(
        monitor.get("delta_scope")
        == "supplemental_current_day_monitor_over_existing_artifacts_no_new_network_claim",
        "delta scope changed",
    )
    checks.check(monitor.get("submission_ready") is False, "monitor overclaims submission readiness")
    checks.check(monitor.get("source_files") == expected_source_files, "source file list changed")
    checks.check(
        monitor.get("source_artifact_sha256") == expected_source_artifact_sha256,
        "source artifact sha256 map stale",
    )
    digest_policy = monitor.get("source_artifact_digest_policy", {})
    checks.check(
        digest_policy.get("hashed_source_files") == sorted(expected_source_artifact_sha256),
        "hashed source file policy changed",
    )
    checks.check(
        digest_policy.get("excluded_source_files") == ["FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json"],
        "digest exclusion list changed",
    )

    prior = monitor.get("prior_monitor", {})
    checks.check(prior.get("date_checked") == prior_monitor.get("date_checked") == "2026-06-20", "prior date stale")
    checks.check(prior.get("status") == prior_monitor.get("status"), "prior status stale")
    checks.check(prior.get("row_count") == prior_monitor.get("row_count") == 20, "prior row count stale")
    checks.check(
        prior.get("unable_to_reproduce_rows") == prior_monitor.get("unable_to_reproduce_rows") == 20,
        "prior unable rows stale",
    )
    checks.check(
        prior.get("source_policy_closed_ratio") == prior_monitor.get("source_policy_closed_ratio") == "0/20",
        "prior source-policy ratio stale",
    )
    checks.check(
        prior.get("source_policy_reopen_triggered") == prior_monitor.get("source_policy_reopen_triggered") is False,
        "prior reopen marker stale",
    )
    checks.check(
        prior.get("local_scan_digest") == prior_monitor.get("local_scan_digest"),
        "prior local scan digest stale",
    )
    checks.check(
        prior.get("monitor_evidence_digest") == prior_monitor.get("monitor_evidence_digest"),
        "prior monitor evidence digest stale",
    )
    checks.check(
        prior.get("latest_external_probe_marker")
        == prior_monitor.get("latest_external_probe_marker")
        == "2026-06-21/9/0/0/4/False/False",
        "prior latest-probe marker stale",
    )

    recheck = monitor.get("oc6_external_source_artifact_recheck_20260621", {})
    checks.check(recheck.get("marker") == expected_oc6_marker, "OC6 external marker stale")
    checks.check(expected_oc6_marker == "2026-06-21/10/0/0/0/False/False", "OC6 external marker changed")
    checks.check(recheck.get("query_count") == oc6_recheck.get("query_count") == 10, "OC6 query count stale")
    checks.check(
        recheck.get("positive_public_code_artifact_rows")
        == oc6_recheck.get("positive_public_code_artifact_rows")
        == 0,
        "OC6 positive public artifact rows stale",
    )
    checks.check(
        recheck.get("source_code_equivalent_artifact_rows")
        == oc6_recheck.get("source_code_equivalent_artifact_rows")
        == 0,
        "OC6 source-equivalent artifact rows stale",
    )
    checks.check(
        recheck.get("source_policy_rows_closed_by_recheck")
        == oc6_recheck.get("source_policy_rows_closed_by_recheck")
        == 0,
        "OC6 recheck overclosed source-policy rows",
    )
    checks.check(
        recheck.get("source_policy_reopen_triggered")
        == oc6_recheck.get("source_policy_reopen_triggered")
        is False,
        "OC6 recheck unexpectedly reopened source policy",
    )
    checks.check(
        recheck.get("global_absence_proved") == oc6_recheck.get("global_absence_proved") is False,
        "OC6 recheck overproved global absence",
    )
    checks.check(recheck.get("submission_ready") is False, "OC6 recheck overclaims submission readiness")

    oc6_alias = monitor.get("oc6_reopen_readiness_aliases", {})
    checks.check(oc6_alias.get("status") == oc6_reopen.get("status"), "OC6 reopen status stale")
    checks.check(oc6_alias.get("oc6_blocker_open") is True, "OC6 blocker unexpectedly closed")
    checks.check(oc6_alias.get("oc6_closure_allowed_now") is False, "OC6 closure unexpectedly allowed")
    checks.check(
        oc6_alias.get("oc6_closure_decision") == "remain_open_no_positive_source_equivalent_artifact",
        "OC6 closure decision changed",
    )
    checks.check(
        oc6_alias.get("latest_external_probe_boundary_marker") == "2026-06-21/9/0/0/4/False/False",
        "OC6 latest external boundary marker stale",
    )
    checks.check(oc6_alias.get("source_policy_reopen_triggered") is False, "OC6 reopen alias changed")
    checks.check(oc6_alias.get("source_policy_rows_closed") == 0, "OC6 closure alias changed")

    public_alias = monitor.get("public_refresh_aliases", {})
    checks.check(public_alias.get("status") == public_refresh.get("status"), "public refresh status stale")
    checks.check(public_alias.get("date_checked") == "2026-06-20", "public refresh date stale")
    checks.check(public_alias.get("current_query_count") == 11, "public refresh query count stale")
    checks.check(
        public_alias.get("latest_external_probe_marker") == "2026-06-21/9/0/0/4/False/False",
        "public refresh latest marker stale",
    )
    checks.check(public_alias.get("source_policy_reopen_triggered") is False, "public refresh reopened")
    checks.check(public_alias.get("source_policy_rows_closed") == 0, "public refresh overclosed rows")

    checks.check(monitor.get("row_count") == 20, "row count changed")
    checks.check(monitor.get("unable_to_reproduce_rows") == 20, "unable rows changed")
    checks.check(monitor.get("source_policy_rows_total") == 20, "source-policy total changed")
    checks.check(monitor.get("source_policy_rows_closed") == 0, "monitor overclosed source-policy rows")
    checks.check(monitor.get("source_policy_rows_closed_by_delta") == 0, "delta overclosed source-policy rows")
    checks.check(monitor.get("source_policy_rows_open") == 20, "source-policy open rows changed")
    checks.check(monitor.get("source_policy_closed") is False, "monitor overclaimed source-policy closure")
    checks.check(monitor.get("source_policy_open") is True, "monitor lost open marker")
    checks.check(monitor.get("source_policy_closed_ratio") == "0/20", "source-policy ratio changed")
    checks.check(monitor.get("source_policy_rows_promoted") == 0, "monitor overpromoted rows")
    checks.check(monitor.get("positive_public_code_artifact_rows") == 0, "monitor overclaimed public artifacts")
    checks.check(
        monitor.get("source_code_equivalent_artifact_rows") == 0,
        "monitor overclaimed source-equivalent artifacts",
    )
    checks.check(monitor.get("source_policy_reopen_triggered") is False, "monitor unexpectedly reopened")
    checks.check(monitor.get("global_absence_proved") is False, "monitor overproved global absence")
    checks.check(
        monitor.get("terminal_reopen_conditions") == prior_monitor.get("terminal_reopen_conditions"),
        "terminal reopen conditions changed",
    )
    checks.check(monitor.get("terminal_suite_count") == 2, "terminal suite count changed")
    checks.check(monitor.get("combined_monitor_digest") == expected_combined_digest, "combined digest stale")

    policy = monitor.get("evidence_policy", {})
    checks.check(policy.get("delta_artifact_closes_source_policy_rows") is False, "delta overcloses rows")
    checks.check(policy.get("query_absence_is_global_absence_proof") is False, "query absence overclaimed")
    checks.check(policy.get("local_mirror_absence_is_global_absence_proof") is False, "local absence overclaimed")
    checks.check(
        policy.get("no_positive_reopen_condition_action")
        == "retain_terminal_unable_to_reproduce_not_promoted_disposition",
        "no-positive action changed",
    )
    checks.check(policy.get("new_network_or_source_policy_execution_performed") is False, "delta performed disallowed action")

    checks.check(monitor.get("full_archive_gap_status") == full_gap.get("status"), "full gap status stale")
    checks.check(monitor.get("full_archive_ready_now") == full_gap.get("full_archive_ready_now") is False, "full archive overready")
    checks.check(monitor.get("heavy_numerical_run_invoked") is False, "monitor invoked heavy run")
    checks.check(monitor.get("run_v047_invoked") is False, "monitor invoked run_v047")
    checks.check(monitor.get("v048_runner_invoked") is False, "monitor invoked v048")
    checks.check(monitor.get("b4_source_policy_execution_invoked") is False, "monitor invoked B4")
    checks.check(monitor.get("source_policy_execution_invoked") is False, "monitor invoked source-policy execution")
    checks.check(monitor.get("source_policy_execution_allowed_now") is False, "monitor allowed execution")
    checks.check(
        monitor.get("exact_b4_opt_in_required_for_execution") is True,
        "monitor lost exact opt-in requirement",
    )
    checks.check(monitor.get("safe_action_ids") == EXPECTED_SAFE_ACTION_IDS, "safe action ids changed")
    checks.check(monitor.get("next_safe_action_ids") == EXPECTED_SAFE_ACTION_IDS, "next safe action ids changed")
    checks.check(monitor.get("opt_in_action_ids") == EXPECTED_OPT_IN_ACTION_IDS, "opt-in action ids changed")
    checks.check(
        monitor.get("required_user_approval_statement") == EXPECTED_APPROVAL_STATEMENT,
        "approval statement changed",
    )
    checks.check(
        monitor.get("guarded_execution_driver") == "run_b4_source_policy_after_opt_in.sh",
        "guarded driver changed",
    )

    for token in [
        "Status: `current_day_delta_no_positive_source_artifact_source_policy_open`.",
        "Delta scope: `supplemental_current_day_monitor_over_existing_artifacts_no_new_network_claim`.",
        "Rows monitored: `20`.",
        "Unable-to-reproduce rows retained: `20`.",
        "Source-policy rows closed/promoted: `0/0`.",
        "Source-policy closed/open: `False/True`.",
        "Source-policy closed ratio: `0/20`.",
        "Source-policy reopen triggered: `False`.",
        "Global absence proved: `False`.",
        f"Prior monitor date/status/evidence digest: `2026-06-20/{prior_monitor.get('status')}/{prior_monitor.get('monitor_evidence_digest')}`.",
        "Prior monitor latest external probe marker: `2026-06-21/9/0/0/4/False/False`.",
        "OC6 external recheck marker: `2026-06-21/10/0/0/0/False/False`.",
        "OC6 external recheck query/positive/source-equivalent/closed/reopened/global-absence: `10/0/0/0/False/False`.",
        "OC6 reopen readiness status/closure allowed/decision: `oc6_reopen_conditions_monitored_no_positive_source_equivalent_artifact/False/remain_open_no_positive_source_equivalent_artifact`.",
        "Terminal reopen conditions: `tfe2026_original_pendulum=new_public_or_source_code_equivalent_tfe_implementation_artifact; vp2024_velocity_partitioning=new_distinct_public_vp2024_velocity_partitioning_code_path`.",
        f"Combined monitor digest: `{expected_combined_digest}`.",
        "Full archive ready now: `False`.",
        "Source-policy execution allowed now/invoked/exact opt-in required: `False/False/True`.",
        "Safe action ids: `rebuild_read_only_audit_chain,rerun_read_only_validators,keep_narrowed_archive_provenance_only,monitor_reopen_conditions`.",
        "Opt-in action ids: `authorized_b4_ra_hi_source_policy_execution`.",
        "Heavy/run_v047/v048/B4 invoked: `False/False/False/False`.",
        "`SOURCE_POLICY_REOPEN_CONDITION_MONITOR_20260620.json`",
        "`OC6_EXTERNAL_SOURCE_ARTIFACT_RECHECK_20260621.json`",
    ]:
        checks.check(token in text, f"markdown missing token: {token}")

    if checks.errors:
        print("source-policy reopen-condition 20260621 delta validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("source-policy reopen-condition 20260621 delta validation: PASS")
    print("rows=20")
    print("unable_to_reproduce_rows=20")
    print("oc6_external_recheck=2026-06-21/10/0/0/0/False/False")
    print("positive_public_code_artifact_rows=0")
    print("source_code_equivalent_artifact_rows=0")
    print("source_policy_reopen_triggered=False")
    print("source_policy_closed=0/20")
    print("source_policy_closed_bool=False")
    print("source_policy_closed_ratio=0/20")
    print("global_absence_proved=False")
    print("source_policy_execution_invoked=False")
    print("source_policy_execution_allowed_now=False")
    print(f"combined_monitor_digest={expected_combined_digest}")
    print("submission_ready=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
