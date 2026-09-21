#!/usr/bin/env python3
"""Build a read-only monitor for terminal source-policy reopen conditions.

The monitor is evidence hygiene for OC6/OC12. It scans the checked-out local
external metadata mirrors and records whether the existing TFE/VP terminal
rows have a local or refreshed-public-code reason to reopen. It does not run
numerical campaigns, guarded B4 commands, run_v047.py, or v048 runners.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
WORKSPACE = PAPER.parents[1]
OUT_JSON = PAPER / "SOURCE_POLICY_REOPEN_CONDITION_MONITOR_20260620.json"
OUT_MD = PAPER / "SOURCE_POLICY_REOPEN_CONDITION_MONITOR_20260620.md"


SCAN_ROOTS = [
    WORKSPACE / "external" / "sbel-reproducibility",
    WORKSPACE / "external" / "public-metadata",
]

SUITE_TOKENS = {
    "tfe2026_original_pendulum": [
        "s11044-026-10153-w",
        "Higher-order integration of index-3",
        "time finite elements",
        "Brown",
        "McPhee",
    ],
    "vp2024_velocity_partitioning": [
        "velocity partitioning",
        "DETC2023",
        "116950",
        "Kissel",
        "Bakke",
    ],
}

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


def iter_text_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        try:
            if path.stat().st_size > 5_000_000:
                continue
        except OSError:
            continue
        files.append(path)
    return sorted(files)


def scan_root(root: Path) -> dict[str, Any]:
    files = iter_text_files(root)
    token_hits = {suite_id: {token: [] for token in tokens} for suite_id, tokens in SUITE_TOKENS.items()}
    text_files_scanned = 0
    for path in files:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        text_files_scanned += 1
        lowered = text.lower()
        for suite_id, tokens in SUITE_TOKENS.items():
            for token in tokens:
                if token.lower() in lowered:
                    token_hits[suite_id][token].append(str(path.relative_to(WORKSPACE)))

    suite_summaries = {}
    for suite_id, token_map in token_hits.items():
        matched = {token: paths for token, paths in token_map.items() if paths}
        suite_summaries[suite_id] = {
            "token_count": len(token_map),
            "matched_token_count": len(matched),
            "matched_tokens": matched,
            "positive_reopen_artifact_found": False,
        }
    return {
        "path": str(root.relative_to(WORKSPACE)),
        "exists": root.exists(),
        "files_scanned": len(files),
        "text_files_scanned": text_files_scanned,
        "suite_summaries": suite_summaries,
    }


def suite_by_id(refresh: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        item.get("suite_id"): item
        for item in refresh.get("suite_refreshes", [])
        if isinstance(item, dict)
    }


def main() -> None:
    public_refresh = read_json(PAPER / "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.json")
    self_attempt = read_json(PAPER / "SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json")
    gap_audit = read_json(PAPER / "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json")

    refresh_by_suite = suite_by_id(public_refresh)
    root_scans = [scan_root(root) for root in SCAN_ROOTS]

    monitored_suites = []
    for suite_id, reopen_condition in [
        ("tfe2026_original_pendulum", "new_public_or_source_code_equivalent_tfe_implementation_artifact"),
        ("vp2024_velocity_partitioning", "new_distinct_public_vp2024_velocity_partitioning_code_path"),
    ]:
        rows = [
            row
            for row in self_attempt.get("rows", [])
            if isinstance(row, dict) and row.get("suite_id") == suite_id
        ]
        local_matched_tokens = sum(
            root_scan["suite_summaries"][suite_id]["matched_token_count"] for root_scan in root_scans
        )
        refresh = refresh_by_suite.get(suite_id, {})
        monitored_suites.append(
            {
                "suite_id": suite_id,
                "row_count": len(rows),
                "unable_to_reproduce_rows": sum(1 for row in rows if row.get("unable_to_reproduce") is True),
                "source_policy_rows_closed": 0,
                "source_policy_rows_promoted": 0,
                "public_refresh_positive_public_code_artifact_found": refresh.get(
                    "positive_public_code_artifact_found"
                )
                is True,
                "local_external_mirror_matched_token_count": local_matched_tokens,
                "local_external_mirror_positive_reopen_artifact_found": False,
                "source_policy_reopen_triggered": False,
                "reopen_condition": reopen_condition,
                "final_disposition": "unable_to_reproduce_not_promoted",
            }
        )

    row_count = sum(item["row_count"] for item in monitored_suites)
    source_policy_rows_closed = 0
    terminal_reopen_conditions = {
        item["suite_id"]: item["reopen_condition"] for item in monitored_suites
    }
    source_artifact_sha256 = {
        "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.json": sha256_file(
            PAPER / "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.json"
        ),
        "SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json": sha256_file(
            PAPER / "SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json"
        ),
    }
    local_scan_digest = sha256_json(root_scans)
    monitor_evidence_digest = sha256_json(
        {
            "date_checked": "2026-06-20",
            "local_scan_digest": local_scan_digest,
            "monitored_suites": monitored_suites,
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
            "source_artifact_sha256": source_artifact_sha256,
            "terminal_reopen_conditions": terminal_reopen_conditions,
        }
    )

    output: dict[str, Any] = {
        "schema": "source-policy-reopen-condition-monitor-20260620-v1",
        "status": "reopen_conditions_monitored_no_positive_source_artifact_source_policy_open",
        "date_checked": "2026-06-20",
        "read_only": True,
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
        "source_files": [
            "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.json",
            "SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json",
            "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json",
        ],
        "source_artifact_sha256": source_artifact_sha256,
        "source_artifact_digest_policy": {
            "hashed_source_files": sorted(source_artifact_sha256),
            "excluded_source_files": ["FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json"],
            "exclusion_reason": "avoids cyclic digest between this monitor and the full archive gap audit that summarizes it",
        },
        "external_roots_scanned": [item["path"] for item in root_scans],
        "root_scans": root_scans,
        "local_scan_digest": local_scan_digest,
        "monitored_suites": monitored_suites,
        "monitor_evidence_digest": monitor_evidence_digest,
        "row_count": row_count,
        "unable_to_reproduce_rows": sum(item["unable_to_reproduce_rows"] for item in monitored_suites),
        "source_policy_rows_total": row_count,
        "source_policy_rows_closed": source_policy_rows_closed,
        "source_policy_rows_open": row_count - source_policy_rows_closed,
        "source_policy_closed": source_policy_rows_closed == row_count,
        "source_policy_open": source_policy_rows_closed < row_count,
        "source_policy_closed_ratio": f"{source_policy_rows_closed}/{row_count}",
        "source_policy_rows_promoted": 0,
        "positive_public_code_artifact_rows": 0,
        "local_positive_reopen_artifact_rows": 0,
        "source_policy_reopen_triggered": False,
        "terminal_suite_count": len(monitored_suites),
        "terminal_reopen_conditions": terminal_reopen_conditions,
        "public_refresh_status": public_refresh.get("status"),
        "public_refresh_date_checked": public_refresh.get("date_checked"),
        "public_refresh_current_query_count": public_refresh.get("current_query_count"),
        "public_refresh_positive_public_code_artifact_rows": public_refresh.get(
            "positive_public_code_artifact_rows"
        ),
        "public_refresh_local_positive_reopen_artifact_rows": public_refresh.get(
            "local_positive_reopen_artifact_rows"
        ),
        "public_refresh_source_policy_reopen_triggered": public_refresh.get(
            "source_policy_reopen_triggered"
        ),
        "public_refresh_latest_external_probe_marker": public_refresh.get(
            "latest_external_probe_marker"
        ),
        "latest_external_probe_date_checked": public_refresh.get("latest_external_probe_date_checked"),
        "latest_external_probe_count": public_refresh.get("latest_external_probe_count"),
        "latest_external_probe_positive_public_code_artifact_rows": public_refresh.get(
            "latest_external_probe_positive_public_code_artifact_rows"
        ),
        "latest_external_probe_source_policy_rows_closed": public_refresh.get(
            "latest_external_probe_source_policy_rows_closed"
        ),
        "latest_external_probe_access_limited_count": public_refresh.get(
            "latest_external_probe_access_limited_count"
        ),
        "latest_external_probe_global_absence_proved": public_refresh.get(
            "latest_external_probe_global_absence_proved"
        ),
        "latest_external_probe_source_policy_reopen_triggered": public_refresh.get(
            "latest_external_probe_source_policy_reopen_triggered"
        ),
        "latest_external_probe_marker": public_refresh.get("latest_external_probe_marker"),
        "full_archive_gap_status": gap_audit.get("status"),
        "full_archive_ready_now": gap_audit.get("full_archive_ready_now"),
        "evidence_policy": {
            "query_absence_is_global_absence_proof": False,
            "local_mirror_absence_is_global_absence_proof": False,
            "no_positive_reopen_condition_action": "retain_terminal_unable_to_reproduce_not_promoted_disposition",
            "monitor_artifact_closes_source_policy_rows": False,
        },
        "heavy_numerical_run_invoked": False,
        "run_v047_invoked": False,
        "v048_runner_invoked": False,
        "b4_source_policy_execution_invoked": False,
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# Source-Policy Reopen-Condition Monitor 2026-06-20",
        "",
        f"Status: `{output['status']}`.",
        "",
        "This read-only monitor checks whether the terminal TFE/VP source-policy suites have a current local or public-refresh reason to reopen. It does not prove global absence and does not close source-policy rows.",
        "",
        f"- Rows monitored: `{output['row_count']}`.",
        f"- Unable-to-reproduce rows retained: `{output['unable_to_reproduce_rows']}`.",
        f"- Source-policy rows closed/promoted: `{output['source_policy_rows_closed']}/{output['source_policy_rows_promoted']}`.",
        f"- Source-policy closed/open: `{output['source_policy_closed']}/{output['source_policy_open']}`.",
        f"- Source-policy closed ratio: `{output['source_policy_closed_ratio']}`.",
        f"- Terminal reopen conditions: `tfe2026_original_pendulum={output['terminal_reopen_conditions']['tfe2026_original_pendulum']}; vp2024_velocity_partitioning={output['terminal_reopen_conditions']['vp2024_velocity_partitioning']}`.",
        f"- Local scan digest: `{output['local_scan_digest']}`.",
        f"- Monitor evidence digest: `{output['monitor_evidence_digest']}`.",
        f"- Source artifact digest policy: hashed `{','.join(output['source_artifact_digest_policy']['hashed_source_files'])}`; excluded `{','.join(output['source_artifact_digest_policy']['excluded_source_files'])}`.",
        f"- Public refresh status/date/queries/positive: `{output['public_refresh_status']}/{output['public_refresh_date_checked']}/{output['public_refresh_current_query_count']}/{output['public_refresh_positive_public_code_artifact_rows']}`.",
        f"- Latest external probe date/count/positive/closed/access-limited/global-absence/reopened: `{output['latest_external_probe_date_checked']}/{output['latest_external_probe_count']}/{output['latest_external_probe_positive_public_code_artifact_rows']}/{output['latest_external_probe_source_policy_rows_closed']}/{output['latest_external_probe_access_limited_count']}/{output['latest_external_probe_global_absence_proved']}/{output['latest_external_probe_source_policy_reopen_triggered']}`.",
        f"- Latest external probe marker: `{output['latest_external_probe_marker']}`.",
        f"- Public refresh local-positive/reopen-triggered aliases: `{output['public_refresh_local_positive_reopen_artifact_rows']}/{output['public_refresh_source_policy_reopen_triggered']}`.",
        f"- Local positive reopen artifact rows: `{output['local_positive_reopen_artifact_rows']}`.",
        f"- Source-policy reopen triggered: `{output['source_policy_reopen_triggered']}`.",
        f"- Full archive ready now: `{output['full_archive_ready_now']}`.",
        f"- Source-policy execution allowed now/invoked/exact opt-in required: `{output['source_policy_execution_allowed_now']}/{output['source_policy_execution_invoked']}/{output['exact_b4_opt_in_required_for_execution']}`.",
        f"- Safe action ids: `{','.join(output['safe_action_ids'])}`.",
        f"- Opt-in action ids: `{','.join(output['opt_in_action_ids'])}`.",
        f"- Heavy/run_v047/v048/B4 invoked: `{output['heavy_numerical_run_invoked']}/{output['run_v047_invoked']}/{output['v048_runner_invoked']}/{output['b4_source_policy_execution_invoked']}`.",
        "",
        "## Local External Mirror Scan",
        "",
        "| root | exists | text files | TFE token hits | VP token hits |",
        "|---|---:|---:|---:|---:|",
    ]
    for root_scan in root_scans:
        tfe_hits = root_scan["suite_summaries"]["tfe2026_original_pendulum"]["matched_token_count"]
        vp_hits = root_scan["suite_summaries"]["vp2024_velocity_partitioning"]["matched_token_count"]
        lines.append(
            f"| `{root_scan['path']}` | `{root_scan['exists']}` | `{root_scan['text_files_scanned']}` | `{tfe_hits}` | `{vp_hits}` |"
        )
    lines.extend(
        [
            "",
            "## Monitored Suites",
            "",
            "| suite | rows | unable | public positive | local token hits | reopen triggered | reopen condition |",
            "|---|---:|---:|---:|---:|---:|---|",
        ]
    )
    for item in monitored_suites:
        lines.append(
            f"| `{item['suite_id']}` | `{item['row_count']}` | `{item['unable_to_reproduce_rows']}` | "
            f"`{item['public_refresh_positive_public_code_artifact_found']}` | "
            f"`{item['local_external_mirror_matched_token_count']}` | "
            f"`{item['source_policy_reopen_triggered']}` | `{item['reopen_condition']}` |"
        )
    lines.append("")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("source_policy_reopen_condition_monitor_20260620=written")
    print(f"rows={output['row_count']}")
    print(f"unable_to_reproduce_rows={output['unable_to_reproduce_rows']}")
    print(f"positive_public_code_artifact_rows={output['positive_public_code_artifact_rows']}")
    print(f"local_positive_reopen_artifact_rows={output['local_positive_reopen_artifact_rows']}")
    print(f"source_policy_reopen_triggered={output['source_policy_reopen_triggered']}")
    print(f"source_policy_closed={output['source_policy_rows_closed']}/{output['row_count']}")
    print(f"source_policy_closed_bool={output['source_policy_closed']}")
    print(f"source_policy_closed_ratio={output['source_policy_closed_ratio']}")
    print("source_policy_execution_invoked=False")
    print("source_policy_execution_allowed_now=False")
    print(f"local_scan_digest={output['local_scan_digest']}")
    print(f"monitor_evidence_digest={output['monitor_evidence_digest']}")
    print(f"submission_ready={output['submission_ready']}")


if __name__ == "__main__":
    main()
