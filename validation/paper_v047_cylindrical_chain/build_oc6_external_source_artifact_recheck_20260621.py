#!/usr/bin/env python3
"""Build a read-only OC6 external source-artifact recheck.

This supplement records the 2026-06-21 browser-search recheck for OC6 reopen
conditions. It is deliberately conservative: no positive source-code-equivalent
artifact was found, search absence is not treated as a global absence proof,
and no source-policy row is closed or promoted.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "OC6_EXTERNAL_SOURCE_ARTIFACT_RECHECK_20260621.json"
OUT_MD = PAPER / "OC6_EXTERNAL_SOURCE_ARTIFACT_RECHECK_20260621.md"

SCHEMA = "oc6-external-source-artifact-recheck-20260621-v1"
STATUS = "no_positive_external_source_artifact_found_reopen_conditions_remain_open"


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def search_row(
    *,
    suite_id: str,
    query: str,
    observation: str,
    non_source_result_example: str | None = None,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "suite_id": suite_id,
        "interface": "browser_web_search",
        "query": query,
        "observation": observation,
        "positive_public_code_artifact_found": False,
        "source_code_equivalent_artifact_found": False,
        "source_policy_rows_closed_by_recheck": 0,
        "source_policy_reopen_triggered": False,
        "access_limited": False,
        "accepted_use": "reopen_monitoring_only_not_source_policy_evidence",
    }
    if non_source_result_example is not None:
        row["non_source_result_example"] = non_source_result_example
    return row


def rows() -> list[dict[str, Any]]:
    return [
        search_row(
            suite_id="tfe2026_original_pendulum",
            query='"Higher-order integration of index-3 DAE with friction using time finite elements on Lie groups"',
            observation="available_search_interface_returned_no_positive_source_code_refs",
        ),
        search_row(
            suite_id="tfe2026_original_pendulum",
            query='"Higher-order integration of index-3 DAE with friction using time finite elements on Lie groups" GitHub',
            observation="available_search_interface_returned_no_positive_source_code_refs",
        ),
        search_row(
            suite_id="tfe2026_original_pendulum",
            query='"10.1007/s11044-026-10153-w" GitHub',
            observation="available_search_interface_returned_no_positive_source_code_refs",
        ),
        search_row(
            suite_id="tfe2026_original_pendulum",
            query="time finite element Lie groups index-3 DAE friction Chaturvedi Sandu Sandu",
            observation="available_search_interface_returned_only_unrelated_publication_refs",
            non_source_result_example="https://arxiv.org/abs/1112.6037",
        ),
        search_row(
            suite_id="tfe2026_original_pendulum",
            query='site:github.com "time finite element" "Lie groups"',
            observation="available_search_interface_returned_no_positive_source_code_refs",
        ),
        search_row(
            suite_id="vp2024_velocity_partitioning",
            query='"Solving a system of ordinary differential equations via velocity partitioning and Lie group"',
            observation="available_search_interface_returned_no_positive_source_code_refs",
        ),
        search_row(
            suite_id="vp2024_velocity_partitioning",
            query='"A. Kissel" "L. Bakke" "D. Negrut" velocity partitioning',
            observation="available_search_interface_returned_no_positive_source_code_refs",
        ),
        search_row(
            suite_id="vp2024_velocity_partitioning",
            query='"DETC2023-116950" "velocity partitioning"',
            observation="available_search_interface_returned_no_positive_source_code_refs",
        ),
        search_row(
            suite_id="vp2024_velocity_partitioning",
            query='"velocity partitioning" Negrut',
            observation="available_search_interface_returned_only_unrelated_publication_refs",
            non_source_result_example="https://arxiv.org/abs/1205.6697",
        ),
        search_row(
            suite_id="vp2024_velocity_partitioning",
            query='site:github.com "velocity partitioning" "Negrut"',
            observation="available_search_interface_returned_no_positive_source_code_refs",
        ),
    ]


def main() -> None:
    public_refresh = read_json(PAPER / "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.json")
    oc6_readiness = read_json(PAPER / "OC6_SOURCE_EQUIVALENT_REOPEN_READINESS_AUDIT_20260620.json")
    probe_rows = rows()
    suite_ids = sorted({row["suite_id"] for row in probe_rows})
    suite_summaries = []
    for suite_id in suite_ids:
        suite_rows = [row for row in probe_rows if row["suite_id"] == suite_id]
        suite_summaries.append(
            {
                "suite_id": suite_id,
                "query_count": len(suite_rows),
                "positive_public_code_artifact_rows": 0,
                "source_code_equivalent_artifact_rows": 0,
                "source_policy_rows_closed_by_recheck": 0,
                "source_policy_reopen_triggered": False,
            }
        )

    output: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "date_checked": "2026-06-21",
        "read_only": True,
        "supplemental_to": [
            "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.json",
            "OC6_SOURCE_EQUIVALENT_REOPEN_READINESS_AUDIT_20260620.json",
        ],
        "prior_latest_external_probe_marker": public_refresh.get("latest_external_probe_marker"),
        "prior_oc6_readiness_status": oc6_readiness.get("status"),
        "query_count": len(probe_rows),
        "suite_count": len(suite_ids),
        "suite_summaries": suite_summaries,
        "rows": probe_rows,
        "positive_public_code_artifact_rows": 0,
        "source_code_equivalent_artifact_rows": 0,
        "source_policy_rows_closed_by_recheck": 0,
        "source_policy_reopen_triggered": False,
        "source_policy_closed": False,
        "submission_ready": False,
        "global_absence_proved": False,
        "evidence_policy": {
            "browser_search_absence_is_global_absence_proof": False,
            "unrelated_publication_refs_are_source_code_artifacts": False,
            "no_positive_query_result_action": "retain_oc6_open_no_positive_source_equivalent_artifact",
            "not_reproducible_rows_are_source_policy_closed": False,
        },
        "reopen_conditions": {
            "tfe2026_original_pendulum": "new_public_or_source_code_equivalent_tfe_implementation_artifact",
            "vp2024_velocity_partitioning": "new_distinct_public_vp2024_velocity_partitioning_code_path",
        },
        "forbidden_execution_flags": {
            "source_policy_execution_invoked": False,
            "heavy_numerical_run_invoked": False,
            "run_v047_invoked": False,
            "v048_runner_invoked": False,
        },
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# OC6 External Source-Artifact Recheck 2026-06-21",
        "",
        f"Status: `{STATUS}`.",
        "",
        "This read-only supplement records the current browser-search recheck for OC6 reopen conditions. It found no positive public/source-code-equivalent artifact and closes zero source-policy rows.",
        "",
        f"- Supplemental to: `{', '.join(output['supplemental_to'])}`.",
        f"- Prior latest external probe marker: `{output['prior_latest_external_probe_marker']}`.",
        f"- Query count: `{output['query_count']}`.",
        f"- Positive public-code artifact rows: `{output['positive_public_code_artifact_rows']}`.",
        f"- Source-code-equivalent artifact rows: `{output['source_code_equivalent_artifact_rows']}`.",
        f"- Source-policy rows closed by recheck: `{output['source_policy_rows_closed_by_recheck']}`.",
        f"- Source-policy reopen triggered: `{output['source_policy_reopen_triggered']}`.",
        f"- Global absence proved: `{output['global_absence_proved']}`.",
        f"- Submission ready: `{output['submission_ready']}`.",
        "",
        "## Query Rows",
        "",
        "| suite | query | observation | positive | closed |",
        "|---|---|---|---:|---:|",
    ]
    for row in probe_rows:
        lines.append(
            f"| `{row['suite_id']}` | `{row['query']}` | `{row['observation']}` | "
            f"`{row['positive_public_code_artifact_found']}` | "
            f"`{row['source_policy_rows_closed_by_recheck']}` |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- Browser-search absence is not a proof of global absence.",
            "- Unrelated publication hits are not source-code artifacts.",
            "- OC6 remains open until a public/source-code-equivalent TFE artifact or distinct VP2024 code path appears.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("oc6_external_source_artifact_recheck_20260621=written")
    print(f"queries={output['query_count']}")
    print("positive_public_code_artifact_rows=0")
    print("source_code_equivalent_artifact_rows=0")
    print("source_policy_rows_closed_by_recheck=0")
    print("source_policy_reopen_triggered=False")
    print("global_absence_proved=False")
    print("submission_ready=False")


if __name__ == "__main__":
    main()
