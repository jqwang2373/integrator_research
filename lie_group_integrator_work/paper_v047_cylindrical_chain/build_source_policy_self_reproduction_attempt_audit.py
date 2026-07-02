#!/usr/bin/env python3
"""Build a source-policy self-reproduction attempt audit.

When a source suite has no distinct public implementation in the local/public
evidence, this audit records the attempted local reconstruction path and gives
each affected row an explicit disposition.  Rows marked here are not promoted:
the point is to distinguish "not yet checked" from "attempted but not
reproducible from the available source material."
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json"
OUT_MD = PAPER / "SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.md"

EXAMPLES = ["single_pendulum", "double_pendulum", "four_link", "slider_crank"]
TFE_METHODS = [
    "tfe2026_Newmark_beta",
    "tfe2026_TFE_m1",
    "tfe2026_TFE_m2",
    "tfe2026_trapezoidal",
]
VP_METHOD = "vp2024_coordinate_partitioning_rA"


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def tfe_rows(
    *,
    tfe_demotion: dict[str, Any],
    tfe_gap: dict[str, Any],
    brown_mcphee: dict[str, Any],
    same_test: dict[str, Any],
    tfe_attempt_certificate: dict[str, Any],
    tfe_public_code_recheck: dict[str, Any],
) -> list[dict[str, Any]]:
    gap_blocks = tfe_gap.get("source_policy_execution_missing_contract_blocks", [])
    nonheavy_blocks = tfe_gap.get("nonheavy_missing_contract_blocks", [])
    row_ids = set(tfe_demotion.get("source_policy_row_ids", []))
    recheck_coverage = tfe_public_code_recheck.get("coverage", {})
    rows: list[dict[str, Any]] = []
    for method in TFE_METHODS:
        for example in EXAMPLES:
            row_id = f"{method}:{example}"
            source_scope_issue = example != "single_pendulum"
            if source_scope_issue:
                reason = "tfe_source_paper_pendulum_suite_does_not_define_this_mechanism_runner"
            else:
                reason = "paper_spec_candidate_runner_not_source_policy_equivalent"
            rows.append(
                {
                    "row_id": row_id,
                    "suite_id": "tfe2026_original_pendulum",
                    "method": method,
                    "example": example,
                    "row_present_in_b4_matrix": row_id in row_ids,
                    "public_code_available": False,
                    "self_reproduction_attempted": True,
                    "self_reproduction_artifacts": [
                        "TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.json",
                        "TFE_PUBLIC_CODE_RECHECK_20260613.json",
                        "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.json",
                        "TFE_SOURCE_POLICY_SPEC.json",
                        "TFE_DAE_RUNNER_CONTRACT_GAP_AUDIT.json",
                        "TFE_BROWN_MCPHEE_SOURCE_LAW_BOUNDARY_AUDIT.json",
                        "../v048_cross_paper_same_test_benchmarks/tfe_source_pendulum_model.py",
                        "../v048_cross_paper_same_test_benchmarks/results/tfe_source_pendulum_same_test_work_precision.json",
                    ],
                    "self_reproduction_attempt_certificate": "TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.json",
                    "self_reproduction_attempt_certificate_status": tfe_attempt_certificate.get("status"),
                    "self_reproduction_attempt_certificate_rows": tfe_attempt_certificate.get("row_count"),
                    "self_reproduction_attempt_certificate_closed_rows": tfe_attempt_certificate.get(
                        "source_policy_closed_rows"
                    ),
                "public_code_recheck_certificate": "TFE_PUBLIC_CODE_RECHECK_20260613.json",
                "public_code_refresh_certificate": "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.json",
                "public_code_recheck_certificate_status": tfe_public_code_recheck.get("status"),
                    "public_code_recheck_date": tfe_public_code_recheck.get("date_checked"),
                    "public_code_recheck_github_repository_search_total_count": recheck_coverage.get(
                        "github_repository_search_total_count"
                    ),
                    "public_code_recheck_github_user_search_total_count": recheck_coverage.get(
                        "github_user_search_total_count"
                    ),
                    "public_code_recheck_github_code_search_api_status": recheck_coverage.get(
                        "github_code_search_api_status"
                    ),
                    "public_code_recheck_source_policy_closed_rows": recheck_coverage.get(
                        "source_policy_rows_closed"
                    ),
                    "public_code_recheck_attempted_not_reproducible_rows": recheck_coverage.get(
                        "source_policy_rows_attempted_not_reproducible"
                    ),
                    "candidate_runner_available": bool(same_test.get("same_test_work_precision_available")),
                    "candidate_runner_source_policy_equivalent": bool(
                        same_test.get("source_policy_method_runner_equivalent")
                    ),
                    "source_policy_method_runner_equivalent": False,
                    "source_policy_dae_runner_equivalent": bool(tfe_gap.get("source_policy_dae_runner_equivalent")),
                    "brown_mcphee_source_code_equivalent_law": bool(
                        brown_mcphee.get("brown_mcphee_source_code_equivalent_law")
                    ),
                    "missing_contract_blocks": gap_blocks,
                    "nonheavy_missing_contract_blocks": nonheavy_blocks,
                    "primary_nonreproducibility_reason": reason,
                    "source_policy_disposition": "attempted_not_reproducible",
                    "unable_to_reproduce": True,
                    "final_nonpublic_code_disposition": "unable_to_reproduce_not_promoted",
                    "post_execution_decision": "attempted_not_reproducible",
                    "source_policy_closed": False,
                    "external_superiority_ready": False,
                    "counts_as_open_execution_queue": False,
                    "accepted_use": "diagnostic_candidate_or_related_work_only_not_source_policy",
                }
            )
    return rows


def vp_rows(vp: dict[str, Any], vp_recheck: dict[str, Any]) -> list[dict[str, Any]]:
    code_path = vp.get("source_code_path_disposition", {})
    coverage = vp.get("coverage", {})
    recheck_coverage = vp_recheck.get("coverage", {})
    recheck_boundary = vp_recheck.get("claim_boundary", {})
    rows: list[dict[str, Any]] = []
    for example in EXAMPLES:
        rows.append(
            {
                "row_id": f"{VP_METHOD}:{example}",
                "suite_id": "vp2024_velocity_partitioning",
                "method": VP_METHOD,
                "example": example,
                "row_present_in_b4_matrix": True,
                "public_code_available": bool(code_path.get("distinct_public_vp_code_path_found")),
                "self_reproduction_attempted": True,
                "self_reproduction_artifacts": [
                    "VP2024_CODE_PATH_DISPOSITION_AUDIT.json",
                    "VP2024_PUBLIC_CODE_RECHECK_20260613.json",
                    "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.json",
                    "../v048_cross_paper_same_test_benchmarks/results/velocity_partitioning_code_search.csv",
                    "../v048_cross_paper_same_test_benchmarks/results/vp_coordinate_partitioning_order_audit.json",
                ],
                "public_code_recheck_certificate": "VP2024_PUBLIC_CODE_RECHECK_20260613.json",
                "public_code_refresh_certificate": "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.json",
                "public_code_recheck_certificate_status": vp_recheck.get("status"),
                "public_code_recheck_date": vp_recheck.get("date_checked"),
                "public_code_recheck_tree_truncated": recheck_coverage.get("tree_truncated"),
                "public_code_recheck_tree_total_paths": recheck_coverage.get("tree_total_paths"),
                "public_code_recheck_year2024_path_count": recheck_coverage.get("year2024_path_count"),
                "public_code_recheck_keyword_path_hit_count": recheck_coverage.get("keyword_path_hit_count"),
                "public_code_recheck_source_policy_closed_rows": recheck_coverage.get("source_policy_rows_closed"),
                "public_code_recheck_attempted_not_reproducible_rows": recheck_coverage.get(
                    "source_policy_rows_attempted_not_reproducible"
                ),
                "distinct_public_vp2024_code_path_found": bool(
                    recheck_boundary.get("distinct_public_vp2024_code_path_found")
                ),
                "candidate_runner_available": bool(code_path.get("coordinate_partitioning_proxy_available")),
                "candidate_runner_source_policy_equivalent": bool(
                    code_path.get("coordinate_partitioning_proxy_is_source_policy_reproduction")
                ),
                "source_policy_method_runner_equivalent": False,
                "source_policy_dae_runner_equivalent": False,
                "primary_nonreproducibility_reason": "distinct_public_vp2024_code_path_not_found_proxy_not_source_policy",
                "public_code_search_status": vp.get("public_code_search", {}).get("public_web_search_status"),
                "local_code_search_hit_count": vp.get("local_repository_tree_scan", {}).get(
                    "local_sbel_velocity_partition_term_hit_count"
                ),
                "source_policy_code_path_unresolved_rows": coverage.get(
                    "source_policy_code_path_unresolved_rows"
                ),
                "source_policy_disposition": "attempted_not_reproducible",
                "unable_to_reproduce": True,
                "final_nonpublic_code_disposition": "unable_to_reproduce_not_promoted",
                "post_execution_decision": "attempted_not_reproducible",
                "source_policy_closed": False,
                "external_superiority_ready": False,
                "counts_as_open_execution_queue": False,
                "accepted_use": "common_reference_proxy_diagnostic_only_not_source_policy",
            }
        )
    return rows


def main() -> None:
    vp = read_json(PAPER / "VP2024_CODE_PATH_DISPOSITION_AUDIT.json")
    vp_recheck = read_json(PAPER / "VP2024_PUBLIC_CODE_RECHECK_20260613.json")
    tfe_demotion = read_json(PAPER / "TFE_B4_B7_SOURCE_POLICY_DEMOTION_AUDIT.json")
    tfe_gap = read_json(PAPER / "TFE_DAE_RUNNER_CONTRACT_GAP_AUDIT.json")
    brown_mcphee = read_json(PAPER / "TFE_BROWN_MCPHEE_SOURCE_LAW_BOUNDARY_AUDIT.json")
    tfe_attempt_certificate = read_json(
        PAPER / "TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.json"
    )
    tfe_public_code_recheck = read_json(PAPER / "TFE_PUBLIC_CODE_RECHECK_20260613.json")
    same_test = read_json(
        PAPER.parent / "v048_cross_paper_same_test_benchmarks" / "results" /
        "tfe_source_pendulum_same_test_work_precision.json"
    )

    rows = tfe_rows(
        tfe_demotion=tfe_demotion,
        tfe_gap=tfe_gap,
        brown_mcphee=brown_mcphee,
        same_test=same_test,
        tfe_attempt_certificate=tfe_attempt_certificate,
        tfe_public_code_recheck=tfe_public_code_recheck,
    ) + vp_rows(vp, vp_recheck)
    rows.sort(key=lambda row: (row["suite_id"], row["method"], EXAMPLES.index(row["example"])))

    suite_summary: list[dict[str, Any]] = []
    for suite_id in sorted({row["suite_id"] for row in rows}):
        suite_rows = [row for row in rows if row["suite_id"] == suite_id]
        suite_summary.append(
            {
                "suite_id": suite_id,
                "row_count": len(suite_rows),
                "self_reproduction_attempted_rows": sum(
                    1 for row in suite_rows if row["self_reproduction_attempted"]
                ),
                "attempted_not_reproducible_rows": sum(
                    1
                    for row in suite_rows
                    if row["source_policy_disposition"] == "attempted_not_reproducible"
                ),
                "unable_to_reproduce_rows": sum(1 for row in suite_rows if row["unable_to_reproduce"]),
                "source_policy_closed_rows": sum(1 for row in suite_rows if row["source_policy_closed"]),
                "external_superiority_ready_rows": sum(
                    1 for row in suite_rows if row["external_superiority_ready"]
                ),
                "open_execution_queue_rows": sum(
                    1 for row in suite_rows if row["counts_as_open_execution_queue"]
                ),
            }
        )

    output: dict[str, Any] = {
        "schema": "source-policy-self-reproduction-attempt-audit-v1",
        "status": "nonpublic_code_rows_attempted_not_reproducible_not_promoted",
        "read_only": True,
        "policy": {
            "public_code_absent_action": "attempt_paper_spec_self_reproduction",
            "under_specified_or_proxy_only_action": "mark_attempted_not_reproducible",
            "failed_self_reproduction_action": "mark_unable_to_reproduce_not_promoted",
            "not_reproducible_rows_are_source_policy_closed": False,
            "not_reproducible_rows_are_external_superiority_ready": False,
        },
        "source_files": [
            "VP2024_CODE_PATH_DISPOSITION_AUDIT.json",
            "VP2024_PUBLIC_CODE_RECHECK_20260613.json",
            "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.json",
            "TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.json",
            "TFE_PUBLIC_CODE_RECHECK_20260613.json",
            "TFE_B4_B7_SOURCE_POLICY_DEMOTION_AUDIT.json",
            "TFE_DAE_RUNNER_CONTRACT_GAP_AUDIT.json",
            "TFE_BROWN_MCPHEE_SOURCE_LAW_BOUNDARY_AUDIT.json",
            "../v048_cross_paper_same_test_benchmarks/results/tfe_source_pendulum_same_test_work_precision.json",
        ],
        "row_count": len(rows),
        "total_rows": len(rows),
        "suites": sorted({row["suite_id"] for row in rows}),
        "self_reproduction_attempted_rows": sum(1 for row in rows if row["self_reproduction_attempted"]),
        "attempted_not_reproducible_rows": sum(
            1 for row in rows if row["source_policy_disposition"] == "attempted_not_reproducible"
        ),
        "source_policy_rows_attempted_not_reproducible": sum(
            1 for row in rows if row["source_policy_disposition"] == "attempted_not_reproducible"
        ),
        "unable_to_reproduce_rows": sum(1 for row in rows if row["unable_to_reproduce"]),
        "source_policy_rows_unable_to_reproduce": sum(1 for row in rows if row["unable_to_reproduce"]),
        "source_policy_closed_rows": sum(1 for row in rows if row["source_policy_closed"]),
        "source_policy_rows_closed": sum(1 for row in rows if row["source_policy_closed"]),
        "external_superiority_ready_rows": sum(1 for row in rows if row["external_superiority_ready"]),
        "open_execution_queue_rows": sum(1 for row in rows if row["counts_as_open_execution_queue"]),
        "suite_summary": suite_summary,
        "rows": rows,
        "heavy_numerical_run_invoked": False,
        "run_v047_invoked": False,
        "v048_runner_invoked": False,
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# Source-Policy Self-Reproduction Attempt Audit",
        "",
        f"Status: `{output['status']}`.",
        "",
        "Rows without a usable public implementation are now explicitly attempted and dispositioned.",
        "A row marked `attempted_not_reproducible` is not promoted, not source-policy closed, and not external-superiority evidence.",
        "",
        f"- Rows audited: `{output['row_count']}`.",
        f"- Self-reproduction attempted rows: `{output['self_reproduction_attempted_rows']}`.",
        f"- Attempted-not-reproducible rows: `{output['attempted_not_reproducible_rows']}`.",
        f"- Unable-to-reproduce rows: `{output['unable_to_reproduce_rows']}`.",
        f"- Source-policy closed rows: `{output['source_policy_closed_rows']}`.",
        f"- External-superiority ready rows: `{output['external_superiority_ready_rows']}`.",
        f"- Open execution-queue rows from this audit: `{output['open_execution_queue_rows']}`.",
        f"- Heavy/run_v047/v048 invoked: `{output['heavy_numerical_run_invoked']}/{output['run_v047_invoked']}/{output['v048_runner_invoked']}`.",
        "",
        "## Suite Summary",
        "",
        "| suite | rows | attempted | not reproducible | unable to reproduce | closed | external ready | open execution |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in suite_summary:
        lines.append(
            f"| `{item['suite_id']}` | `{item['row_count']}` | "
            f"`{item['self_reproduction_attempted_rows']}` | "
            f"`{item['attempted_not_reproducible_rows']}` | "
            f"`{item['unable_to_reproduce_rows']}` | "
            f"`{item['source_policy_closed_rows']}` | "
            f"`{item['external_superiority_ready_rows']}` | "
            f"`{item['open_execution_queue_rows']}` |"
        )
    lines.extend(
        [
            "",
            "## Row Disposition",
            "",
            "| suite | method | example | disposition | primary reason |",
            "|---|---|---|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            f"| `{row['suite_id']}` | `{row['method']}` | `{row['example']}` | "
            f"`{row['source_policy_disposition']}` | "
            f"`{row['primary_nonreproducibility_reason']}` |"
        )
    lines.append("")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("source_policy_self_reproduction_attempt_audit=written")
    print(f"attempted_not_reproducible_rows={output['attempted_not_reproducible_rows']}/{output['row_count']}")
    print("source_policy_closed_rows=0")
    print("external_superiority_ready_rows=0")


if __name__ == "__main__":
    main()
