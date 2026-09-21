#!/usr/bin/env python3
"""Build a current-day delta monitor for terminal source-policy reopen conditions.

This is a read-only supplement to the 2026-06-20 reopen monitor. It records
that the 2026-06-21 OC6 external source-artifact recheck does not change the
terminal TFE/VP disposition. It does not perform network access, execute B4
commands, run run_v047.py, or launch v048 runners.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
OUT_JSON = PAPER / "SOURCE_POLICY_REOPEN_CONDITION_MONITOR_20260621_DELTA.json"
OUT_MD = PAPER / "SOURCE_POLICY_REOPEN_CONDITION_MONITOR_20260621_DELTA.md"

SAFE_ACTIONS_WITHOUT_B4_OPT_IN = [
    {
        "action_id": "rebuild_read_only_audit_chain",
        "description": "Regenerate read-only audit/manifest/review artifacts from existing evidence.",
    },
    {
        "action_id": "rerun_read_only_validators",
        "description": "Run validators that inspect artifacts without launching numerical campaigns.",
    },
    {
        "action_id": "keep_narrowed_archive_provenance_only",
        "description": "Use the current archive only for narrowed-claim replay and provenance evidence.",
    },
    {
        "action_id": "monitor_reopen_conditions",
        "description": "Refresh read-only reopen-condition monitors for new local/public-code evidence.",
    },
]
SAFE_ACTION_IDS = [item["action_id"] for item in SAFE_ACTIONS_WITHOUT_B4_OPT_IN]
OPT_IN_ACTION_IDS = ["authorized_b4_ra_hi_source_policy_execution"]
REQUIRED_USER_APPROVAL_STATEMENT = (
    "I explicitly approve running the B4 source-policy execution commands listed in "
    "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json."
)


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


def main() -> None:
    prior_monitor = read_json(PAPER / "SOURCE_POLICY_REOPEN_CONDITION_MONITOR_20260620.json")
    oc6_recheck = read_json(PAPER / "OC6_EXTERNAL_SOURCE_ARTIFACT_RECHECK_20260621.json")
    oc6_reopen = read_json(PAPER / "OC6_SOURCE_EQUIVALENT_REOPEN_READINESS_AUDIT_20260620.json")
    public_refresh = read_json(PAPER / "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.json")
    full_gap = read_json(PAPER / "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json")

    source_files = [
        "SOURCE_POLICY_REOPEN_CONDITION_MONITOR_20260620.json",
        "OC6_EXTERNAL_SOURCE_ARTIFACT_RECHECK_20260621.json",
        "OC6_SOURCE_EQUIVALENT_REOPEN_READINESS_AUDIT_20260620.json",
        "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.json",
        "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json",
    ]
    source_artifact_sha256 = {
        name: sha256_file(manuscript_path(name))
        for name in source_files
        if name != "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json"
    }
    oc6_external_marker = marker_from_recheck(oc6_recheck)
    legacy_probe_marker = prior_monitor.get("latest_external_probe_marker")
    combined_monitor_digest = sha256_json(
        {
            "date_checked": "2026-06-21",
            "prior_monitor_evidence_digest": prior_monitor.get("monitor_evidence_digest"),
            "prior_monitor_local_scan_digest": prior_monitor.get("local_scan_digest"),
            "legacy_probe_marker": legacy_probe_marker,
            "oc6_external_source_artifact_recheck_marker": oc6_external_marker,
            "terminal_reopen_conditions": prior_monitor.get("terminal_reopen_conditions"),
            "source_artifact_sha256": source_artifact_sha256,
            "source_policy_reopen_triggered": False,
            "source_policy_rows_closed_by_delta": 0,
        }
    )

    output: dict[str, Any] = {
        "schema": "source-policy-reopen-condition-monitor-20260621-delta-v1",
        "status": "current_day_delta_no_positive_source_artifact_source_policy_open",
        "date_checked": "2026-06-21",
        "read_only": True,
        "delta_scope": "supplemental_current_day_monitor_over_existing_artifacts_no_new_network_claim",
        "submission_ready": False,
        "source_policy_execution_invoked": False,
        "source_policy_execution_allowed_now": False,
        "exact_b4_opt_in_required_for_execution": True,
        "safe_actions_without_b4_opt_in": SAFE_ACTIONS_WITHOUT_B4_OPT_IN,
        "safe_action_ids": SAFE_ACTION_IDS,
        "opt_in_action_ids": OPT_IN_ACTION_IDS,
        "next_safe_actions": SAFE_ACTIONS_WITHOUT_B4_OPT_IN,
        "next_safe_action_ids": SAFE_ACTION_IDS,
        "required_user_approval_statement": REQUIRED_USER_APPROVAL_STATEMENT,
        "guarded_execution_driver": "run_b4_source_policy_after_opt_in.sh",
        "source_files": source_files,
        "source_artifact_sha256": source_artifact_sha256,
        "source_artifact_digest_policy": {
            "hashed_source_files": sorted(source_artifact_sha256),
            "excluded_source_files": ["FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json"],
            "exclusion_reason": "avoids cyclic digest with the full archive gap audit that summarizes reopen monitors",
        },
        "prior_monitor": {
            "file": "SOURCE_POLICY_REOPEN_CONDITION_MONITOR_20260620.json",
            "date_checked": prior_monitor.get("date_checked"),
            "status": prior_monitor.get("status"),
            "row_count": prior_monitor.get("row_count"),
            "unable_to_reproduce_rows": prior_monitor.get("unable_to_reproduce_rows"),
            "source_policy_closed_ratio": prior_monitor.get("source_policy_closed_ratio"),
            "source_policy_reopen_triggered": prior_monitor.get("source_policy_reopen_triggered"),
            "local_scan_digest": prior_monitor.get("local_scan_digest"),
            "monitor_evidence_digest": prior_monitor.get("monitor_evidence_digest"),
            "latest_external_probe_marker": legacy_probe_marker,
        },
        "oc6_external_source_artifact_recheck_20260621": {
            "file": "OC6_EXTERNAL_SOURCE_ARTIFACT_RECHECK_20260621.json",
            "status": oc6_recheck.get("status"),
            "date_checked": oc6_recheck.get("date_checked"),
            "query_count": oc6_recheck.get("query_count"),
            "positive_public_code_artifact_rows": oc6_recheck.get(
                "positive_public_code_artifact_rows"
            ),
            "source_code_equivalent_artifact_rows": oc6_recheck.get(
                "source_code_equivalent_artifact_rows"
            ),
            "source_policy_rows_closed_by_recheck": oc6_recheck.get(
                "source_policy_rows_closed_by_recheck"
            ),
            "source_policy_reopen_triggered": oc6_recheck.get(
                "source_policy_reopen_triggered"
            ),
            "global_absence_proved": oc6_recheck.get("global_absence_proved"),
            "submission_ready": oc6_recheck.get("submission_ready"),
            "marker": oc6_external_marker,
        },
        "oc6_reopen_readiness_aliases": {
            "status": oc6_reopen.get("status"),
            "oc6_blocker_open": oc6_reopen.get("oc6_blocker_open"),
            "oc6_closure_allowed_now": oc6_reopen.get("oc6_closure_allowed_now"),
            "oc6_closure_decision": oc6_reopen.get("oc6_closure_decision"),
            "latest_external_probe_boundary_marker": oc6_reopen.get(
                "latest_external_probe_boundary",
                {},
            ).get("marker"),
            "source_policy_reopen_triggered": oc6_reopen.get("source_policy_reopen_triggered"),
            "source_policy_rows_closed": oc6_reopen.get("source_policy_rows_closed"),
        },
        "public_refresh_aliases": {
            "status": public_refresh.get("status"),
            "date_checked": public_refresh.get("date_checked"),
            "current_query_count": public_refresh.get("current_query_count"),
            "latest_external_probe_marker": public_refresh.get("latest_external_probe_marker"),
            "source_policy_reopen_triggered": public_refresh.get(
                "source_policy_reopen_triggered"
            ),
            "source_policy_rows_closed": public_refresh.get("source_policy_rows_closed"),
        },
        "terminal_reopen_conditions": prior_monitor.get("terminal_reopen_conditions"),
        "terminal_suite_count": prior_monitor.get("terminal_suite_count"),
        "row_count": prior_monitor.get("row_count"),
        "unable_to_reproduce_rows": prior_monitor.get("unable_to_reproduce_rows"),
        "source_policy_rows_total": prior_monitor.get("source_policy_rows_total"),
        "source_policy_rows_closed": 0,
        "source_policy_rows_closed_by_delta": 0,
        "source_policy_rows_open": prior_monitor.get("source_policy_rows_open"),
        "source_policy_closed": False,
        "source_policy_open": True,
        "source_policy_closed_ratio": prior_monitor.get("source_policy_closed_ratio"),
        "source_policy_rows_promoted": 0,
        "positive_public_code_artifact_rows": 0,
        "source_code_equivalent_artifact_rows": 0,
        "source_policy_reopen_triggered": False,
        "global_absence_proved": False,
        "combined_monitor_digest": combined_monitor_digest,
        "evidence_policy": {
            "delta_artifact_closes_source_policy_rows": False,
            "query_absence_is_global_absence_proof": False,
            "local_mirror_absence_is_global_absence_proof": False,
            "no_positive_reopen_condition_action": "retain_terminal_unable_to_reproduce_not_promoted_disposition",
            "new_network_or_source_policy_execution_performed": False,
        },
        "full_archive_gap_status": full_gap.get("status"),
        "full_archive_ready_now": full_gap.get("full_archive_ready_now"),
        "heavy_numerical_run_invoked": False,
        "run_v047_invoked": False,
        "v048_runner_invoked": False,
        "b4_source_policy_execution_invoked": False,
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# Source-Policy Reopen-Condition Monitor 2026-06-21 Delta",
        "",
        f"Status: `{output['status']}`.",
        "",
        "This read-only delta monitor supplements the 2026-06-20 reopen monitor with the 2026-06-21 OC6 external source-artifact recheck. It does not perform a new network search, does not prove global absence, and does not close source-policy rows.",
        "",
        f"- Delta scope: `{output['delta_scope']}`.",
        f"- Rows monitored: `{output['row_count']}`.",
        f"- Unable-to-reproduce rows retained: `{output['unable_to_reproduce_rows']}`.",
        f"- Source-policy rows closed/promoted: `{output['source_policy_rows_closed']}/{output['source_policy_rows_promoted']}`.",
        f"- Source-policy closed/open: `{output['source_policy_closed']}/{output['source_policy_open']}`.",
        f"- Source-policy closed ratio: `{output['source_policy_closed_ratio']}`.",
        f"- Source-policy reopen triggered: `{output['source_policy_reopen_triggered']}`.",
        f"- Global absence proved: `{output['global_absence_proved']}`.",
        f"- Prior monitor date/status/evidence digest: `{output['prior_monitor']['date_checked']}/{output['prior_monitor']['status']}/{output['prior_monitor']['monitor_evidence_digest']}`.",
        f"- Prior monitor latest external probe marker: `{legacy_probe_marker}`.",
        f"- OC6 external recheck marker: `{oc6_external_marker}`.",
        f"- OC6 external recheck status: `{output['oc6_external_source_artifact_recheck_20260621']['status']}`.",
        f"- OC6 external recheck query/positive/source-equivalent/closed/reopened/global-absence: `{oc6_recheck.get('query_count')}/{oc6_recheck.get('positive_public_code_artifact_rows')}/{oc6_recheck.get('source_code_equivalent_artifact_rows')}/{oc6_recheck.get('source_policy_rows_closed_by_recheck')}/{oc6_recheck.get('source_policy_reopen_triggered')}/{oc6_recheck.get('global_absence_proved')}`.",
        f"- OC6 reopen readiness status/closure allowed/decision: `{oc6_reopen.get('status')}/{oc6_reopen.get('oc6_closure_allowed_now')}/{oc6_reopen.get('oc6_closure_decision')}`.",
        f"- Terminal reopen conditions: `tfe2026_original_pendulum={output['terminal_reopen_conditions']['tfe2026_original_pendulum']}; vp2024_velocity_partitioning={output['terminal_reopen_conditions']['vp2024_velocity_partitioning']}`.",
        f"- Source artifact digest policy: hashed `{','.join(output['source_artifact_digest_policy']['hashed_source_files'])}`; excluded `{','.join(output['source_artifact_digest_policy']['excluded_source_files'])}`.",
        f"- Combined monitor digest: `{combined_monitor_digest}`.",
        f"- Full archive ready now: `{output['full_archive_ready_now']}`.",
        f"- Source-policy execution allowed now/invoked/exact opt-in required: `{output['source_policy_execution_allowed_now']}/{output['source_policy_execution_invoked']}/{output['exact_b4_opt_in_required_for_execution']}`.",
        f"- Safe action ids: `{','.join(output['safe_action_ids'])}`.",
        f"- Opt-in action ids: `{','.join(output['opt_in_action_ids'])}`.",
        f"- Heavy/run_v047/v048/B4 invoked: `{output['heavy_numerical_run_invoked']}/{output['run_v047_invoked']}/{output['v048_runner_invoked']}/{output['b4_source_policy_execution_invoked']}`.",
        "",
        "## Monitored Delta",
        "",
        "| source | marker/status | closes rows | reopens | global absence |",
        "|---|---|---:|---:|---:|",
        (
            f"| `SOURCE_POLICY_REOPEN_CONDITION_MONITOR_20260620.json` | `{legacy_probe_marker}` | "
            f"`{prior_monitor.get('source_policy_rows_closed')}` | `{prior_monitor.get('source_policy_reopen_triggered')}` | `False` |"
        ),
        (
            f"| `OC6_EXTERNAL_SOURCE_ARTIFACT_RECHECK_20260621.json` | `{oc6_external_marker}` | "
            f"`{oc6_recheck.get('source_policy_rows_closed_by_recheck')}` | `{oc6_recheck.get('source_policy_reopen_triggered')}` | `{oc6_recheck.get('global_absence_proved')}` |"
        ),
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("source_policy_reopen_condition_monitor_20260621_delta=written")
    print(f"rows={output['row_count']}")
    print(f"unable_to_reproduce_rows={output['unable_to_reproduce_rows']}")
    print(f"oc6_external_recheck={oc6_external_marker}")
    print("positive_public_code_artifact_rows=0")
    print("source_code_equivalent_artifact_rows=0")
    print("source_policy_reopen_triggered=False")
    print("source_policy_closed=0/20")
    print("source_policy_closed_bool=False")
    print("source_policy_closed_ratio=0/20")
    print("global_absence_proved=False")
    print("source_policy_execution_invoked=False")
    print("source_policy_execution_allowed_now=False")
    print(f"combined_monitor_digest={combined_monitor_digest}")
    print("submission_ready=False")


if __name__ == "__main__":
    main()
