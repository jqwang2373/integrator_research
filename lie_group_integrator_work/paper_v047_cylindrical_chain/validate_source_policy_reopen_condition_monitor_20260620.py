#!/usr/bin/env python3
"""Validate the 2026-06-20 source-policy reopen-condition monitor."""

from __future__ import annotations

import hashlib
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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_json(data: Any) -> str:
    encoded = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def main() -> int:
    checks = Checks()
    try:
        monitor = read_json(PAPER / "SOURCE_POLICY_REOPEN_CONDITION_MONITOR_20260620.json")
        text = (PAPER / "SOURCE_POLICY_REOPEN_CONDITION_MONITOR_20260620.md").read_text(
            encoding="utf-8",
            errors="replace",
        )
        public_refresh = read_json(PAPER / "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.json")
        self_attempt = read_json(PAPER / "SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json")
        gap_audit = read_json(PAPER / "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json")
    except Exception as exc:  # noqa: BLE001
        print(f"source-policy reopen-condition monitor validation: FAIL\n- {exc}")
        return 1

    suites = {
        item.get("suite_id"): item
        for item in monitor.get("monitored_suites", [])
        if isinstance(item, dict)
    }
    tfe = suites.get("tfe2026_original_pendulum", {})
    vp = suites.get("vp2024_velocity_partitioning", {})
    roots = {
        item.get("path"): item
        for item in monitor.get("root_scans", [])
        if isinstance(item, dict)
    }
    expected_terminal_reopen_conditions = {
        "tfe2026_original_pendulum": "new_public_or_source_code_equivalent_tfe_implementation_artifact",
        "vp2024_velocity_partitioning": "new_distinct_public_vp2024_velocity_partitioning_code_path",
    }
    expected_source_artifact_sha256 = {
        "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.json": sha256_file(
            PAPER / "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.json"
        ),
        "SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json": sha256_file(
            PAPER / "SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json"
        ),
    }
    expected_local_scan_digest = sha256_json(monitor.get("root_scans", []))
    expected_monitor_evidence_digest = sha256_json(
        {
            "date_checked": "2026-06-20",
            "local_scan_digest": expected_local_scan_digest,
            "monitored_suites": monitor.get("monitored_suites", []),
            "public_refresh_status": public_refresh.get("status"),
            "public_refresh_current_query_count": public_refresh.get("current_query_count"),
            "public_refresh_latest_external_probe_marker": public_refresh.get(
                "latest_external_probe_marker"
            ),
            "public_refresh_source_policy_reopen_triggered": public_refresh.get(
                "source_policy_reopen_triggered"
            ),
            "public_refresh_local_positive_reopen_artifact_rows": public_refresh.get(
                "local_positive_reopen_artifact_rows"
            ),
            "source_artifact_sha256": expected_source_artifact_sha256,
            "terminal_reopen_conditions": expected_terminal_reopen_conditions,
        }
    )

    checks.check(
        monitor.get("schema") == "source-policy-reopen-condition-monitor-20260620-v1",
        "schema changed",
    )
    checks.check(
        monitor.get("status")
        == "reopen_conditions_monitored_no_positive_source_artifact_source_policy_open",
        "status changed",
    )
    checks.check(monitor.get("date_checked") == "2026-06-20", "date changed")
    checks.check(monitor.get("read_only") is True, "monitor must remain read-only")
    checks.check(monitor.get("submission_ready") is False, "monitor overclaims submission readiness")
    for source_file in [
        "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.json",
        "SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json",
        "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json",
    ]:
        checks.check(source_file in monitor.get("source_files", []), f"missing source file: {source_file}")
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
    checks.check(
        digest_policy.get("exclusion_reason")
        == "avoids cyclic digest between this monitor and the full archive gap audit that summarizes it",
        "digest exclusion reason changed",
    )

    checks.check(monitor.get("row_count") == 20, "row count changed")
    checks.check(monitor.get("unable_to_reproduce_rows") == 20, "unable rows changed")
    checks.check(monitor.get("source_policy_rows_total") == monitor.get("row_count") == 20, "source-policy total changed")
    checks.check(monitor.get("source_policy_rows_closed") == 0, "monitor overclosed source-policy rows")
    checks.check(monitor.get("source_policy_rows_open") == 20, "source-policy open rows changed")
    checks.check(monitor.get("source_policy_closed") is False, "monitor overclaimed source-policy closure")
    checks.check(monitor.get("source_policy_open") is True, "monitor lost source-policy open marker")
    checks.check(monitor.get("source_policy_closed_ratio") == "0/20", "source-policy closed ratio changed")
    checks.check(monitor.get("source_policy_rows_promoted") == 0, "monitor overpromoted source-policy rows")
    checks.check(monitor.get("positive_public_code_artifact_rows") == 0, "positive public artifacts changed")
    checks.check(monitor.get("local_positive_reopen_artifact_rows") == 0, "local positive rows changed")
    checks.check(monitor.get("source_policy_reopen_triggered") is False, "monitor unexpectedly reopened rows")
    checks.check(monitor.get("terminal_suite_count") == 2, "terminal suite count changed")
    checks.check(
        monitor.get("terminal_reopen_conditions") == expected_terminal_reopen_conditions,
        "terminal reopen conditions changed",
    )
    checks.check(
        monitor.get("terminal_reopen_conditions") == gap_audit.get("terminal_reopen_conditions"),
        "monitor terminal reopen conditions drifted from archive gap audit",
    )
    checks.check(monitor.get("public_refresh_status") == public_refresh.get("status"), "public refresh status stale")
    checks.check(monitor.get("public_refresh_date_checked") == public_refresh.get("date_checked"), "refresh date stale")
    checks.check(
        monitor.get("public_refresh_current_query_count") == public_refresh.get("current_query_count") == 11,
        "refresh query count stale",
    )
    checks.check(
        monitor.get("public_refresh_positive_public_code_artifact_rows")
        == public_refresh.get("positive_public_code_artifact_rows")
        == 0,
        "refresh positive count stale",
    )
    checks.check(
        monitor.get("public_refresh_local_positive_reopen_artifact_rows")
        == public_refresh.get("local_positive_reopen_artifact_rows")
        == 0,
        "refresh local-positive reopen alias stale",
    )
    checks.check(
        monitor.get("public_refresh_source_policy_reopen_triggered")
        == public_refresh.get("source_policy_reopen_triggered")
        is False,
        "refresh reopen-triggered alias stale",
    )
    checks.check(
        monitor.get("public_refresh_latest_external_probe_marker")
        == public_refresh.get("latest_external_probe_marker")
        == "2026-06-21/9/0/0/4/False/False",
        "refresh latest external probe marker stale",
    )
    checks.check(
        monitor.get("latest_external_probe_date_checked")
        == public_refresh.get("latest_external_probe_date_checked")
        == "2026-06-21",
        "latest external probe date stale",
    )
    checks.check(
        monitor.get("latest_external_probe_count")
        == public_refresh.get("latest_external_probe_count")
        == 9,
        "latest external probe count stale",
    )
    checks.check(
        monitor.get("latest_external_probe_positive_public_code_artifact_rows")
        == public_refresh.get("latest_external_probe_positive_public_code_artifact_rows")
        == 0,
        "latest external probe positive rows stale",
    )
    checks.check(
        monitor.get("latest_external_probe_source_policy_rows_closed")
        == public_refresh.get("latest_external_probe_source_policy_rows_closed")
        == 0,
        "latest external probe source-policy closure stale",
    )
    checks.check(
        monitor.get("latest_external_probe_access_limited_count")
        == public_refresh.get("latest_external_probe_access_limited_count")
        == 4,
        "latest external probe access-limited count stale",
    )
    checks.check(
        monitor.get("latest_external_probe_global_absence_proved")
        == public_refresh.get("latest_external_probe_global_absence_proved")
        is False,
        "latest external probe overproved global absence",
    )
    checks.check(
        monitor.get("latest_external_probe_source_policy_reopen_triggered")
        == public_refresh.get("latest_external_probe_source_policy_reopen_triggered")
        is False,
        "latest external probe unexpectedly reopened source policy",
    )
    checks.check(
        monitor.get("latest_external_probe_marker")
        == public_refresh.get("latest_external_probe_marker")
        == "2026-06-21/9/0/0/4/False/False",
        "latest external probe marker stale",
    )
    checks.check(monitor.get("full_archive_gap_status") == gap_audit.get("status"), "gap status stale")
    checks.check(monitor.get("full_archive_ready_now") == gap_audit.get("full_archive_ready_now") is False, "archive overready")

    checks.check(tfe.get("row_count") == 16, "TFE row count changed")
    checks.check(tfe.get("unable_to_reproduce_rows") == 16, "TFE unable rows changed")
    checks.check(tfe.get("source_policy_reopen_triggered") is False, "TFE unexpectedly reopened")
    checks.check(
        tfe.get("reopen_condition") == "new_public_or_source_code_equivalent_tfe_implementation_artifact",
        "TFE reopen condition changed",
    )
    checks.check(vp.get("row_count") == 4, "VP row count changed")
    checks.check(vp.get("unable_to_reproduce_rows") == 4, "VP unable rows changed")
    checks.check(vp.get("source_policy_reopen_triggered") is False, "VP unexpectedly reopened")
    checks.check(
        vp.get("reopen_condition") == "new_distinct_public_vp2024_velocity_partitioning_code_path",
        "VP reopen condition changed",
    )
    checks.check(
        {
            "tfe2026_original_pendulum": tfe.get("reopen_condition"),
            "vp2024_velocity_partitioning": vp.get("reopen_condition"),
        }
        == expected_terminal_reopen_conditions,
        "suite reopen conditions do not match top-level terminal map",
    )

    checks.check(self_attempt.get("row_count") == 20, "self-attempt row count changed")
    checks.check(self_attempt.get("unable_to_reproduce_rows") == 20, "self-attempt unable rows changed")
    checks.check(self_attempt.get("source_policy_closed_rows") == 0, "self-attempt overclosed rows")

    for root in ["external/sbel-reproducibility", "external/public-metadata"]:
        root_scan = roots.get(root, {})
        checks.check(root_scan.get("exists") is True, f"local root missing: {root}")
        checks.check(root_scan.get("text_files_scanned", 0) >= 0, f"invalid text scan count: {root}")
        tfe_summary = root_scan.get("suite_summaries", {}).get("tfe2026_original_pendulum", {})
        vp_summary = root_scan.get("suite_summaries", {}).get("vp2024_velocity_partitioning", {})
        checks.check(tfe_summary.get("positive_reopen_artifact_found") is False, f"TFE overpositive in {root}")
        checks.check(vp_summary.get("positive_reopen_artifact_found") is False, f"VP overpositive in {root}")
    checks.check(
        monitor.get("local_scan_digest") == expected_local_scan_digest,
        "local scan digest stale",
    )
    checks.check(
        monitor.get("monitor_evidence_digest") == expected_monitor_evidence_digest,
        "monitor evidence digest stale",
    )

    policy = monitor.get("evidence_policy", {})
    checks.check(policy.get("query_absence_is_global_absence_proof") is False, "query absence overclaimed")
    checks.check(policy.get("local_mirror_absence_is_global_absence_proof") is False, "local absence overclaimed")
    checks.check(
        policy.get("no_positive_reopen_condition_action")
        == "retain_terminal_unable_to_reproduce_not_promoted_disposition",
        "no-positive action changed",
    )
    checks.check(policy.get("monitor_artifact_closes_source_policy_rows") is False, "monitor overcloses rows")
    checks.check(monitor.get("heavy_numerical_run_invoked") is False, "monitor invoked heavy run")
    checks.check(monitor.get("run_v047_invoked") is False, "monitor invoked run_v047")
    checks.check(monitor.get("v048_runner_invoked") is False, "monitor invoked v048")
    checks.check(monitor.get("b4_source_policy_execution_invoked") is False, "monitor invoked B4")
    checks.check(monitor.get("source_policy_execution_invoked") is False, "monitor invoked source-policy execution")
    checks.check(monitor.get("source_policy_execution_allowed_now") is False, "monitor allowed source-policy execution")
    checks.check(
        monitor.get("exact_b4_opt_in_required_for_execution") is True,
        "monitor lost exact opt-in requirement",
    )
    checks.check(monitor.get("safe_action_ids") == EXPECTED_SAFE_ACTION_IDS, "safe action ids changed")
    checks.check(
        monitor.get("next_safe_action_ids") == EXPECTED_SAFE_ACTION_IDS,
        "next safe action ids changed",
    )
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
        "Status: `reopen_conditions_monitored_no_positive_source_artifact_source_policy_open`.",
        "Rows monitored: `20`.",
        "Unable-to-reproduce rows retained: `20`.",
        "Source-policy rows closed/promoted: `0/0`.",
        "Source-policy closed/open: `False/True`.",
        "Source-policy closed ratio: `0/20`.",
        "Terminal reopen conditions: `tfe2026_original_pendulum=new_public_or_source_code_equivalent_tfe_implementation_artifact; vp2024_velocity_partitioning=new_distinct_public_vp2024_velocity_partitioning_code_path`.",
        f"Local scan digest: `{expected_local_scan_digest}`.",
        f"Monitor evidence digest: `{expected_monitor_evidence_digest}`.",
        "Source artifact digest policy: hashed `SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.json,SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json`; excluded `FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json`.",
        "Public refresh status/date/queries/positive: `public_code_refresh_20260620_no_positive_new_source_artifact_rows_remain_unable_to_reproduce/2026-06-20/11/0`.",
        "Latest external probe date/count/positive/closed/access-limited/global-absence/reopened: `2026-06-21/9/0/0/4/False/False`.",
        "Latest external probe marker: `2026-06-21/9/0/0/4/False/False`.",
        "Public refresh local-positive/reopen-triggered aliases: `0/False`.",
        "Local positive reopen artifact rows: `0`.",
        "Source-policy reopen triggered: `False`.",
        "Full archive ready now: `False`.",
        "Source-policy execution allowed now/invoked/exact opt-in required: `False/False/True`.",
        "Safe action ids: `rebuild_read_only_audit_chain,rerun_read_only_validators,keep_narrowed_archive_provenance_only,monitor_reopen_conditions`.",
        "Opt-in action ids: `authorized_b4_ra_hi_source_policy_execution`.",
        "Heavy/run_v047/v048/B4 invoked: `False/False/False/False`.",
        "`tfe2026_original_pendulum`",
        "`vp2024_velocity_partitioning`",
        "`new_public_or_source_code_equivalent_tfe_implementation_artifact`",
        "`new_distinct_public_vp2024_velocity_partitioning_code_path`",
    ]:
        checks.check(token in text, f"markdown missing token: {token}")

    if checks.errors:
        print("source-policy reopen-condition monitor validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("source-policy reopen-condition monitor validation: PASS")
    print("rows=20")
    print("unable_to_reproduce_rows=20")
    print("positive_public_code_artifact_rows=0")
    print("local_positive_reopen_artifact_rows=0")
    print("source_policy_reopen_triggered=False")
    print("source_policy_closed=0/20")
    print("source_policy_closed_bool=False")
    print("source_policy_closed_ratio=0/20")
    print("source_policy_execution_invoked=False")
    print("source_policy_execution_allowed_now=False")
    print(f"local_scan_digest={expected_local_scan_digest}")
    print(f"monitor_evidence_digest={expected_monitor_evidence_digest}")
    print("latest_external_probe=2026-06-21/9/0/0/4/False/False")
    print("submission_ready=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
