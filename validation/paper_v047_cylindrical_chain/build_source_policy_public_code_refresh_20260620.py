#!/usr/bin/env python3
"""Build the 2026-06-20 read-only public-code refresh supplement.

The supplement records a current web-search pass for the TFE/VP source-policy
lanes whose reopen conditions depend on new public or source-code-equivalent
artifacts. It is evidence hygiene only: it does not run numerical campaigns,
does not invoke guarded B4 execution, and does not promote source-policy rows.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.json"
OUT_MD = PAPER / "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.md"

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


def suite_rows(self_attempt: dict[str, Any], suite_id: str) -> list[dict[str, Any]]:
    return [
        row
        for row in self_attempt.get("rows", [])
        if isinstance(row, dict) and row.get("suite_id") == suite_id
    ]


def query(interface: str, text: str) -> dict[str, str]:
    return {
        "interface": interface,
        "query": text,
        "observation": "no_positive_public_source_code_artifact_found",
    }


def external_probe(
    *,
    suite_id: str,
    interface: str,
    text: str,
    observation: str,
    parseable_result_count: int | None = None,
    access_limited: bool = False,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "suite_id": suite_id,
        "interface": interface,
        "query": text,
        "observation": observation,
        "positive_public_code_artifact_found": False,
        "source_policy_rows_closed_by_probe": 0,
        "access_limited": access_limited,
    }
    if parseable_result_count is not None:
        row["parseable_result_count"] = parseable_result_count
    return row


def latest_external_probe_rows() -> list[dict[str, Any]]:
    return [
        external_probe(
            suite_id="tfe2026_original_pendulum",
            interface="web_search",
            text='"Higher-order integration of index-3 DAE with friction using time finite elements on Lie groups" code GitHub',
            observation="available_search_interface_returned_no_result_refs",
        ),
        external_probe(
            suite_id="tfe2026_original_pendulum",
            interface="web_search",
            text='"10.1007/s11044-026-10153-w" GitHub',
            observation="available_search_interface_returned_no_result_refs",
        ),
        external_probe(
            suite_id="tfe2026_original_pendulum",
            interface="github_rest_search_api",
            text='"Higher-order integration" "index-3" "time finite elements"',
            observation="github_anonymous_api_rate_limited_no_search_result_obtained",
            access_limited=True,
        ),
        external_probe(
            suite_id="tfe2026_original_pendulum",
            interface="github_html_repository_search",
            text='"Higher-order integration" "index-3" "time finite elements"',
            observation="github_html_repository_search_parseable_zero_results",
            parseable_result_count=0,
        ),
        external_probe(
            suite_id="tfe2026_original_pendulum",
            interface="github_html_code_search",
            text='"s11044-026-10153-w"',
            observation="github_html_code_search_secondary_rate_limited_no_search_result_obtained",
            access_limited=True,
        ),
        external_probe(
            suite_id="vp2024_velocity_partitioning",
            interface="web_search",
            text='"velocity partitioning" "Kissel" "Bakke" "Negrut" GitHub',
            observation="available_search_interface_returned_no_result_refs",
        ),
        external_probe(
            suite_id="vp2024_velocity_partitioning",
            interface="web_search",
            text='"DETC2023" "116950" "velocity" "partition" GitHub',
            observation="available_search_interface_returned_no_result_refs",
        ),
        external_probe(
            suite_id="vp2024_velocity_partitioning",
            interface="github_rest_search_api",
            text='"velocity partitioning" Negrut',
            observation="github_anonymous_api_rate_limited_no_search_result_obtained",
            access_limited=True,
        ),
        external_probe(
            suite_id="vp2024_velocity_partitioning",
            interface="github_html_code_search",
            text='"velocity partitioning" Negrut',
            observation="github_html_code_search_secondary_rate_limited_no_search_result_obtained",
            access_limited=True,
        ),
    ]


def summarize_latest_external_probe(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "date_checked": "2026-06-21",
        "probe_count": len(rows),
        "positive_public_code_artifact_rows": sum(
            1 for row in rows if row.get("positive_public_code_artifact_found") is True
        ),
        "source_policy_rows_closed_by_probe": sum(
            int(row.get("source_policy_rows_closed_by_probe") or 0) for row in rows
        ),
        "access_limited_probe_count": sum(1 for row in rows if row.get("access_limited") is True),
        "parseable_zero_result_probe_count": sum(
            1 for row in rows if row.get("parseable_result_count") == 0
        ),
        "global_absence_proved": False,
        "source_policy_reopen_triggered": False,
    }


def suite_refresh(
    *,
    suite_id: str,
    rows: list[dict[str, Any]],
    prior: dict[str, Any],
    current_queries: list[dict[str, str]],
    reopen_condition: str,
) -> dict[str, Any]:
    return {
        "suite_id": suite_id,
        "row_count": len(rows),
        "prior_refresh_public_code_available": prior.get("public_code_available_now"),
        "prior_refresh_disposition": prior.get("final_disposition"),
        "current_query_count": len(current_queries),
        "current_queries": current_queries,
        "positive_public_code_artifact_found": False,
        "public_code_available_now": False,
        "self_reproduction_attempted_rows": sum(
            1 for row in rows if row.get("self_reproduction_attempted") is True
        ),
        "unable_to_reproduce_rows": sum(1 for row in rows if row.get("unable_to_reproduce") is True),
        "source_policy_rows_closed": 0,
        "source_policy_rows_promoted": 0,
        "external_superiority_ready_rows": 0,
        "final_disposition": "unable_to_reproduce_not_promoted",
        "reopen_condition": reopen_condition,
    }


def main() -> None:
    prior_refresh = read_json(PAPER / "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.json")
    self_attempt = read_json(PAPER / "SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json")

    prior_by_suite = {
        item.get("suite_id"): item
        for item in prior_refresh.get("suite_refreshes", [])
        if isinstance(item, dict)
    }
    tfe_rows = suite_rows(self_attempt, "tfe2026_original_pendulum")
    vp_rows = suite_rows(self_attempt, "vp2024_velocity_partitioning")

    tfe_queries = [
        query(
            "web_search",
            '"Higher-order integration of index-3 DAE with friction using time finite elements on Lie groups" code GitHub',
        ),
        query("web_search", '"10.1007/s11044-026-10153-w" GitHub'),
        query("web_search", '"10.1007/s11044-026-10153-w"'),
        query("web_search", '"Higher-order integration of index-3 DAE"'),
        query("web_search", '"time finite elements" "Lie groups" "Brown" "McPhee" code'),
    ]
    vp_queries = [
        query("web_search", '"velocity partitioning" "Kissel" "Bakke" "Negrut" GitHub'),
        query("web_search", '"DETC2023" "116950" "velocity" "partition" GitHub'),
        query("web_search", '"DETC2023" "116950" "velocity" "partition"'),
        query("web_search", '"sbel-reproducibility" "velocity partitioning"'),
        query("web_search", 'site:github.com/uwsbel/sbel-reproducibility "DETC2023" "116950"'),
        query("web_search", 'site:github.com/uwsbel/sbel-reproducibility "velocity partitioning"'),
    ]

    suite_refreshes = [
        suite_refresh(
            suite_id="tfe2026_original_pendulum",
            rows=tfe_rows,
            prior=prior_by_suite.get("tfe2026_original_pendulum", {}),
            current_queries=tfe_queries,
            reopen_condition="new_public_or_source_code_equivalent_tfe_implementation_artifact",
        ),
        suite_refresh(
            suite_id="vp2024_velocity_partitioning",
            rows=vp_rows,
            prior=prior_by_suite.get("vp2024_velocity_partitioning", {}),
            current_queries=vp_queries,
            reopen_condition="new_distinct_public_vp2024_velocity_partitioning_code_path",
        ),
    ]
    latest_probe_rows = latest_external_probe_rows()
    latest_probe_summary = summarize_latest_external_probe(latest_probe_rows)
    row_count = sum(item["row_count"] for item in suite_refreshes)
    current_query_count = sum(item["current_query_count"] for item in suite_refreshes)

    output: dict[str, Any] = {
        "schema": "source-policy-public-code-refresh-20260620-v1",
        "status": "public_code_refresh_20260620_no_positive_new_source_artifact_rows_remain_unable_to_reproduce",
        "date": "2026-06-20",
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
        "supplemental_to": "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.json",
        "source_files": [
            "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.json",
            "SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json",
        ],
        "evidence_policy": {
            "query_absence_is_global_absence_proof": False,
            "rate_limited_search_is_positive_artifact_evidence": False,
            "no_positive_query_result_action": "retain_prior_unable_to_reproduce_not_promoted_disposition",
            "not_reproducible_rows_are_source_policy_closed": False,
            "not_reproducible_rows_are_external_superiority_ready": False,
        },
        "suite_refreshes": suite_refreshes,
        "latest_external_probe": latest_probe_summary,
        "latest_external_probe_rows": latest_probe_rows,
        "latest_external_probe_date_checked": latest_probe_summary["date_checked"],
        "latest_external_probe_count": latest_probe_summary["probe_count"],
        "latest_external_probe_positive_public_code_artifact_rows": latest_probe_summary[
            "positive_public_code_artifact_rows"
        ],
        "latest_external_probe_source_policy_rows_closed": latest_probe_summary[
            "source_policy_rows_closed_by_probe"
        ],
        "latest_external_probe_access_limited_count": latest_probe_summary[
            "access_limited_probe_count"
        ],
        "latest_external_probe_global_absence_proved": latest_probe_summary[
            "global_absence_proved"
        ],
        "latest_external_probe_source_policy_reopen_triggered": latest_probe_summary[
            "source_policy_reopen_triggered"
        ],
        "latest_external_probe_marker": (
            f"{latest_probe_summary['date_checked']}/{latest_probe_summary['probe_count']}/"
            f"{latest_probe_summary['positive_public_code_artifact_rows']}/"
            f"{latest_probe_summary['source_policy_rows_closed_by_probe']}/"
            f"{latest_probe_summary['access_limited_probe_count']}/"
            f"{latest_probe_summary['global_absence_proved']}/"
            f"{latest_probe_summary['source_policy_reopen_triggered']}"
        ),
        "row_count": row_count,
        "rows": row_count,
        "current_query_count": current_query_count,
        "current_queries": current_query_count,
        "query_count": current_query_count,
        "positive_public_code_artifact_rows": 0,
        "local_positive_reopen_artifact_rows": 0,
        "source_policy_reopen_triggered": latest_probe_summary[
            "source_policy_reopen_triggered"
        ],
        "public_code_available_rows": 0,
        "self_reproduction_attempted_rows": sum(
            item["self_reproduction_attempted_rows"] for item in suite_refreshes
        ),
        "unable_to_reproduce_rows": sum(item["unable_to_reproduce_rows"] for item in suite_refreshes),
        "source_policy_closed": False,
        "source_policy_closed_ratio": f"0/{row_count}",
        "source_policy_closed_rows": 0,
        "source_policy_rows_closed": 0,
        "source_policy_rows_promoted": 0,
        "external_superiority_ready_rows": 0,
        "open_execution_queue_rows": 0,
        "heavy_numerical_run_invoked": False,
        "run_v047_invoked": False,
        "v048_runner_invoked": False,
        "b4_source_policy_execution_invoked": False,
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# Source-Policy Public-Code Refresh 2026-06-20",
        "",
        f"Status: `{output['status']}`.",
        "",
        "This is a read-only supplemental refresh. The current query set found no positive new public source-code artifact for the TFE/VP lanes; this is not treated as proof of global absence.",
        "",
        f"- Supplemental to: `{output['supplemental_to']}`.",
        f"- Rows refreshed: `{output['row_count']}`.",
        f"- Current queries: `{output['current_query_count']}`.",
        f"- Positive public-code artifact rows: `{output['positive_public_code_artifact_rows']}`.",
        f"- Public-code-available rows: `{output['public_code_available_rows']}`.",
        f"- Self-reproduction attempted rows: `{output['self_reproduction_attempted_rows']}`.",
        f"- Unable-to-reproduce rows: `{output['unable_to_reproduce_rows']}`.",
        f"- Source-policy closed ratio: `{output['source_policy_closed_ratio']}`.",
        f"- Source-policy rows closed/promoted: `{output['source_policy_rows_closed']}/{output['source_policy_rows_promoted']}`.",
        f"- External-superiority ready rows: `{output['external_superiority_ready_rows']}`.",
        f"- Submission ready: `{output['submission_ready']}`.",
        f"- Latest external probe date/count/positive/closed/access-limited/global-absence/reopened: `{output['latest_external_probe_date_checked']}/{output['latest_external_probe_count']}/{output['latest_external_probe_positive_public_code_artifact_rows']}/{output['latest_external_probe_source_policy_rows_closed']}/{output['latest_external_probe_access_limited_count']}/{output['latest_external_probe_global_absence_proved']}/{output['latest_external_probe_source_policy_reopen_triggered']}`.",
        f"- Latest external probe marker: `{output['latest_external_probe_marker']}`.",
        f"- Local positive reopen artifact rows / source-policy reopen triggered: `{output['local_positive_reopen_artifact_rows']}/{output['source_policy_reopen_triggered']}`.",
        f"- Source-policy execution allowed now/invoked/exact opt-in required: `{output['source_policy_execution_allowed_now']}/{output['source_policy_execution_invoked']}/{output['exact_b4_opt_in_required_for_execution']}`.",
        f"- Safe action ids: `{','.join(output['safe_action_ids'])}`.",
        f"- Opt-in action ids: `{','.join(output['opt_in_action_ids'])}`.",
        f"- Heavy/run_v047/v048/B4 invoked: `{output['heavy_numerical_run_invoked']}/{output['run_v047_invoked']}/{output['v048_runner_invoked']}/{output['b4_source_policy_execution_invoked']}`.",
        "",
        "## Suite Refreshes",
        "",
        "| suite | rows | queries | positive artifact | attempted | unable | closed | promoted | disposition |",
        "|---|---:|---:|---|---:|---:|---:|---:|---|",
    ]
    for item in suite_refreshes:
        lines.append(
            f"| `{item['suite_id']}` | `{item['row_count']}` | "
            f"`{item['current_query_count']}` | "
            f"`{item['positive_public_code_artifact_found']}` | "
            f"`{item['self_reproduction_attempted_rows']}` | "
            f"`{item['unable_to_reproduce_rows']}` | "
            f"`{item['source_policy_rows_closed']}` | "
            f"`{item['source_policy_rows_promoted']}` | "
            f"`{item['final_disposition']}` |"
        )
    lines.extend(
        [
            "",
            "## Latest External Probe",
            "",
            "The 2026-06-21 supplemental probe found no positive public/source-code-equivalent artifact. GitHub API/code search was partially rate-limited, so this remains reopen monitoring evidence rather than a proof of global absence.",
            "",
            "| suite | interface | observation | positive | access-limited |",
            "|---|---|---|---:|---:|",
        ]
    )
    for item in latest_probe_rows:
        lines.append(
            f"| `{item['suite_id']}` | `{item['interface']}` | "
            f"`{item['observation']}` | "
            f"`{item['positive_public_code_artifact_found']}` | "
            f"`{item['access_limited']}` |"
        )
    lines.extend(
        [
            "",
            "## Reopen Conditions",
            "",
            "- TFE: `new_public_or_source_code_equivalent_tfe_implementation_artifact`.",
            "- VP2024: `new_distinct_public_vp2024_velocity_partitioning_code_path`.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("source_policy_public_code_refresh_20260620=written")
    print(f"rows={output['row_count']}")
    print(f"current_queries={output['current_query_count']}")
    print("positive_public_code_artifact_rows=0")
    print(f"unable_to_reproduce_rows={output['unable_to_reproduce_rows']}")
    print(f"source_policy_closed={output['source_policy_rows_closed']}/{output['row_count']}")
    print("source_policy_execution_invoked=False")
    print("source_policy_execution_allowed_now=False")
    print(f"submission_ready={output['submission_ready']}")


if __name__ == "__main__":
    main()
