#!/usr/bin/env python3
"""Build a read-only public-code refresh for nonpublic source-policy suites.

This artifact records the 2026-06-14 refresh requested by the user: if no
usable public source-code artifact is found, use the already attempted local
self-reproduction evidence and keep the rows marked unable-to-reproduce / not
promoted.  It does not run numerical campaigns or guarded B4 commands.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.json"
OUT_MD = PAPER / "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.md"


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def main() -> None:
    tfe_recheck = read_json(PAPER / "TFE_PUBLIC_CODE_RECHECK_20260613.json")
    vp_recheck = read_json(PAPER / "VP2024_PUBLIC_CODE_RECHECK_20260613.json")
    self_attempt = read_json(PAPER / "SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json")

    tfe_rows = [
        row
        for row in self_attempt.get("rows", [])
        if isinstance(row, dict) and row.get("suite_id") == "tfe2026_original_pendulum"
    ]
    vp_rows = [
        row
        for row in self_attempt.get("rows", [])
        if isinstance(row, dict) and row.get("suite_id") == "vp2024_velocity_partitioning"
    ]

    tfe_confirmed_zero_queries = [
        {
            "interface": "web_search",
            "query": '"Higher-order integration of index-3 DAE with friction using time finite elements on Lie groups" code GitHub',
            "result": "no_entries_returned",
        },
        {
            "interface": "web_search",
            "query": '"10.1007/s11044-026-10153-w" GitHub',
            "result": "no_entries_returned",
        },
        {
            "interface": "web_search",
            "query": '"time finite elements" "Lie groups" "Brown" "McPhee" code',
            "result": "no_entries_returned",
        },
        {
            "interface": "github_repository_search_api",
            "query": "s11044-026-10153-w",
            "total_count": 0,
        },
        {
            "interface": "github_repository_search_api",
            "query": '"Higher-order integration of index-3 DAE"',
            "total_count": 0,
        },
        {
            "interface": "github_repository_search_api",
            "query": '"time finite elements" "Lie groups" pendulum',
            "total_count": 0,
        },
    ]
    tfe_rate_limited_queries = [
        {
            "interface": "github_repository_search_api",
            "query": '"Brown McPhee" "time finite element"',
            "result": "api_rate_limited_no_positive_evidence",
        }
    ]
    vp_confirmed_zero_queries = [
        {
            "interface": "web_search",
            "query": '"velocity partitioning" "Kissel" "Bakke" "Negrut" GitHub',
            "result": "no_entries_returned",
        },
        {
            "interface": "web_search",
            "query": '"DETC2023" "116950" "velocity" "partition" GitHub',
            "result": "no_entries_returned",
        },
        {
            "interface": "web_search",
            "query": 'site:github.com/uwsbel/sbel-reproducibility "DETC2023" "116950"',
            "result": "no_entries_returned",
        },
        {
            "interface": "web_search",
            "query": 'site:github.com/uwsbel/sbel-reproducibility "velocity partitioning"',
            "result": "no_entries_returned",
        },
    ]

    vp_tree_refresh = {
        "tree_api_url": vp_recheck.get("public_repository_recheck", {}).get("tree_api_url"),
        "tree_sha": "cf9884a24a22a5281bacc3d87e67ff06c0911dfc",
        "tree_truncated": False,
        "tree_total_paths": 4487,
        "keyword_regex": vp_recheck.get("public_repository_recheck", {}).get("keyword_regex"),
        "keyword_path_hit_count": 0,
        "keyword_path_hits": [],
    }

    suite_refreshes = [
        {
            "suite_id": "tfe2026_original_pendulum",
            "row_count": len(tfe_rows),
            "prior_public_code_recheck": "TFE_PUBLIC_CODE_RECHECK_20260613.json",
            "prior_recheck_status": tfe_recheck.get("status"),
            "confirmed_zero_query_count": len(tfe_confirmed_zero_queries),
            "rate_limited_query_count": len(tfe_rate_limited_queries),
            "confirmed_zero_queries": tfe_confirmed_zero_queries,
            "rate_limited_queries": tfe_rate_limited_queries,
            "public_code_available_now": False,
            "self_reproduction_attempted_rows": sum(
                1 for row in tfe_rows if row.get("self_reproduction_attempted") is True
            ),
            "unable_to_reproduce_rows": sum(1 for row in tfe_rows if row.get("unable_to_reproduce") is True),
            "source_policy_rows_closed": 0,
            "source_policy_rows_promoted": 0,
            "final_disposition": "unable_to_reproduce_not_promoted",
            "reopen_condition": "new_public_or_source_code_equivalent_tfe_implementation_artifact",
        },
        {
            "suite_id": "vp2024_velocity_partitioning",
            "row_count": len(vp_rows),
            "prior_public_code_recheck": "VP2024_PUBLIC_CODE_RECHECK_20260613.json",
            "prior_recheck_status": vp_recheck.get("status"),
            "confirmed_zero_query_count": len(vp_confirmed_zero_queries),
            "confirmed_zero_queries": vp_confirmed_zero_queries,
            "public_repository_tree_refresh": vp_tree_refresh,
            "public_code_available_now": False,
            "self_reproduction_attempted_rows": sum(
                1 for row in vp_rows if row.get("self_reproduction_attempted") is True
            ),
            "unable_to_reproduce_rows": sum(1 for row in vp_rows if row.get("unable_to_reproduce") is True),
            "source_policy_rows_closed": 0,
            "source_policy_rows_promoted": 0,
            "final_disposition": "unable_to_reproduce_not_promoted",
            "reopen_condition": "new_distinct_public_vp2024_velocity_partitioning_code_path",
        },
    ]

    output: dict[str, Any] = {
        "schema": "source-policy-public-code-refresh-20260614-v1",
        "status": "public_code_refresh_no_new_source_artifact_nonpublic_rows_remain_unable_to_reproduce",
        "date_checked": "2026-06-14",
        "read_only": True,
        "source_files": [
            "TFE_PUBLIC_CODE_RECHECK_20260613.json",
            "VP2024_PUBLIC_CODE_RECHECK_20260613.json",
            "SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json",
        ],
        "policy": {
            "public_code_absent_action": "use_self_reproduction_attempt_evidence",
            "failed_or_proxy_self_reproduction_action": "mark_unable_to_reproduce_not_promoted",
            "not_reproducible_rows_are_source_policy_closed": False,
            "not_reproducible_rows_are_external_superiority_ready": False,
            "rate_limited_query_policy": "rate_limited_queries_are_not_positive_public_code_evidence",
        },
        "suite_refreshes": suite_refreshes,
        "row_count": sum(item["row_count"] for item in suite_refreshes),
        "public_code_available_rows": 0,
        "self_reproduction_attempted_rows": sum(
            item["self_reproduction_attempted_rows"] for item in suite_refreshes
        ),
        "unable_to_reproduce_rows": sum(item["unable_to_reproduce_rows"] for item in suite_refreshes),
        "source_policy_rows_closed": 0,
        "source_policy_rows_promoted": 0,
        "external_superiority_ready_rows": 0,
        "open_execution_queue_rows": 0,
        "heavy_numerical_run_invoked": False,
        "run_v047_invoked": False,
        "v048_runner_invoked": False,
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# Source-Policy Public-Code Refresh 2026-06-14",
        "",
        f"Status: `{output['status']}`.",
        "",
        "This is a read-only refresh. It records that no new usable public source-code artifact was found for the nonpublic TFE/VP lanes, so the existing self-reproduction attempt disposition remains in force.",
        "",
        f"- Rows refreshed: `{output['row_count']}`.",
        f"- Public-code-available rows: `{output['public_code_available_rows']}`.",
        f"- Self-reproduction attempted rows: `{output['self_reproduction_attempted_rows']}`.",
        f"- Unable-to-reproduce rows: `{output['unable_to_reproduce_rows']}`.",
        f"- Source-policy rows closed/promoted: `{output['source_policy_rows_closed']}/{output['source_policy_rows_promoted']}`.",
        f"- External-superiority ready rows: `{output['external_superiority_ready_rows']}`.",
        f"- Open execution-queue rows: `{output['open_execution_queue_rows']}`.",
        f"- Heavy/run_v047/v048 invoked: `{output['heavy_numerical_run_invoked']}/{output['run_v047_invoked']}/{output['v048_runner_invoked']}`.",
        "",
        "## Suite Refreshes",
        "",
        "| suite | rows | public code now | attempted | unable | closed | promoted | disposition |",
        "|---|---:|---|---:|---:|---:|---:|---|",
    ]
    for item in suite_refreshes:
        lines.append(
            f"| `{item['suite_id']}` | `{item['row_count']}` | "
            f"`{item['public_code_available_now']}` | "
            f"`{item['self_reproduction_attempted_rows']}` | "
            f"`{item['unable_to_reproduce_rows']}` | "
            f"`{item['source_policy_rows_closed']}` | "
            f"`{item['source_policy_rows_promoted']}` | "
            f"`{item['final_disposition']}` |"
        )
    lines.extend(
        [
            "",
            "## VP Tree Refresh",
            "",
            f"- Tree SHA: `{vp_tree_refresh['tree_sha']}`.",
            f"- Tree truncated: `{vp_tree_refresh['tree_truncated']}`.",
            f"- Total paths: `{vp_tree_refresh['tree_total_paths']}`.",
            f"- Keyword path hits: `{vp_tree_refresh['keyword_path_hit_count']}`.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("source_policy_public_code_refresh_20260614=written")
    print(f"rows={output['row_count']}")
    print("public_code_available_rows=0")
    print(f"unable_to_reproduce_rows={output['unable_to_reproduce_rows']}")


if __name__ == "__main__":
    main()
