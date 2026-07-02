#!/usr/bin/env python3
"""Build an objective-level closure audit for the active comparison goal."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
OUT_CSV = RESULTS / "objective_closure_audit.csv"
OUT_JSON = RESULTS / "objective_closure_audit.json"
OUT_MD = RESULTS / "objective_closure_audit.md"

EXAMPLES = ["single_pendulum", "double_pendulum", "four_link", "slider_crank"]
STEP_SIZES = [0.1, 0.05, 0.025]
REFERENCE_H = 0.0125
LOCAL = "local_Gauss6_FullVA"


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty {path.name}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def row(requirement: str, status: bool, evidence: str, interpretation: str) -> dict[str, object]:
    return {
        "requirement": requirement,
        "status": "pass" if status else "fail",
        "evidence": evidence,
        "interpretation": interpretation,
    }


def main() -> None:
    baseline = read_json(RESULTS / "baseline_coverage_matrix.json")
    coarse = read_json(RESULTS / "coarse_four_example_order_summary.json")
    coarse_rows = read_csv(RESULTS / "coarse_four_example_order_summary.csv")
    common = read_json(RESULTS / "common_reference_error_summary.json")
    apples = read_json(RESULTS / "apples_to_apples_policy_audit.json")
    global_policy = read_json(RESULTS / "global_comparison_policy_audit.json")
    vp_identity = read_json(RESULTS / "vp_method_identity_audit.json")
    tfe_scope = read_json(RESULTS / "tfe_m3_scope_exclusion_audit.json")

    local_rows = {
        row["example"]: row
        for row in coarse_rows
        if row.get("method") == LOCAL and row.get("status") == "ok"
    }
    local_orders = {
        example: {
            "pos_order": local_rows[example]["pos_order"],
            "vel_order": local_rows[example]["vel_order"],
            "acc_order": local_rows[example]["acc_order"],
            "finest_vel_error": local_rows[example]["finest_vel_error"],
        }
        for example in EXAMPLES
    }

    rows = [
        row(
            "four_named_examples_present",
            sorted(common.get("examples", [])) == sorted(EXAMPLES)
            and sorted(coarse.get("examples", [])) == sorted(EXAMPLES)
            and sorted(local_rows) == sorted(EXAMPLES),
            "coarse_four_example_order_summary.json; common_reference_error_summary.json",
            "single, double, four-link, and slider-crank examples are all present for the local method and common-reference audit",
        ),
        row(
            "shared_coarse_step_sizes",
            common.get("step_sizes") == STEP_SIZES and coarse.get("step_sizes") == STEP_SIZES,
            "coarse_four_example_order_summary.json; common_reference_error_summary.json",
            "all accepted comparison rows use h = 0.1, 0.05, 0.025",
        ),
        row(
            "coarse_reference_policy",
            common.get("reference_h") == REFERENCE_H and coarse.get("reference_h") == REFERENCE_H,
            "coarse_four_example_order_summary.json; common_reference_error_summary.json",
            "the comparison uses reference h = 0.0125 rather than default 1e-4",
        ),
        row(
            "apples_to_apples_policy_audit",
            apples.get("schema") == "apples-to-apples-policy-audit-v1"
            and apples.get("row_count") == apples.get("paper_safe_row_count") == 44
            and apples.get("nonlocal_paper_safe_comparison_count") == 40
            and apples.get("public_source_time_grid_caveat_detected") is True
            and apples.get("fixed_grid_wrapper_present") is True
            and apples.get("source_policy_reproduction") is False,
            "apples_to_apples_policy_audit.json",
            "all four examples and all accepted methods pass the shared h-grid/reference/norm audit; public-code rows use fixed-grid replay",
        ),
        row(
            "global_comparison_policy_audit",
            global_policy.get("schema") == "global-comparison-policy-audit-v1"
            and global_policy.get("reasonable_apples_to_apples_claims") is True
            and global_policy.get("passed_count") == global_policy.get("row_count") == 13
            and global_policy.get("mixed_policy_direct_error_vs_local_comparable_rows") == 0
            and global_policy.get("direct_error_vs_local_comparable_rows") == 40
            and global_policy.get("external_superiority_claim") is False
            and global_policy.get("source_policy_reproduction") is False
            and global_policy.get("public_code_fixed_grid_replay") is True,
            "global_comparison_policy_audit.json",
            "all claim-bearing comparison artifacts pass the global apples-to-apples/claim-boundary audit",
        ),
        row(
            "required_methods_resolved",
            baseline.get("required_methods_resolved") is True
            and baseline.get("required_methods_resolved_count") == baseline.get("row_count")
            and not baseline.get("source_unresolved_methods")
            and not baseline.get("rejected_partial_methods"),
            "baseline_coverage_matrix.json",
            "all required method labels are accepted, alias-resolved, or source-backed scope-excluded",
        ),
        row(
            "vp_alias_resolved",
            vp_identity.get("alias_resolved") is True
            and vp_identity.get("implemented_method") == "vp2024_coordinate_partitioning_rA",
            "vp_method_identity_audit.json",
            "VP Lie-group ODE partitioning is treated as the implemented coordinate-partitioning wrapper",
        ),
        row(
            "tfe_m3_scope_excluded",
            tfe_scope.get("source_backed_exclusion") is True
            and tfe_scope.get("required_accepted_matrix_excludes_method") is True,
            "tfe_m3_scope_exclusion_audit.json",
            "TFE(m=3) four-link is a source-backed excluded stress row, not a required accepted baseline",
        ),
        row(
            "direct_common_reference_error_wins",
            common.get("direct_error_superiority_claim") is True
            and common.get("local_finest_velocity_error_wins") == common.get("local_finest_velocity_error_comparisons") == 40,
            "common_reference_error_summary.json",
            "local method has lower finest-step velocity error on all 40 direct common-reference nonlocal comparisons",
        ),
        row(
            "direct_common_reference_order_wins",
            common.get("local_velocity_order_wins") == common.get("local_velocity_order_comparisons") == 40,
            "common_reference_error_summary.json",
            "local method has higher velocity order on all 40 direct common-reference nonlocal comparisons",
        ),
        row(
            "original_paper_error_wins",
            common.get("original_paper_velocity_error_wins") == common.get("original_paper_velocity_error_comparisons") == 16,
            "common_reference_error_summary.json",
            "local method has lower finest-step velocity error than accepted original-paper baseline rows",
        ),
        row(
            "kissel_negrut_error_wins",
            common.get("kissel_negrut_velocity_error_wins") == common.get("kissel_negrut_velocity_error_comparisons") == 24,
            "common_reference_error_summary.json",
            "local method has lower finest-step velocity error than accepted Kissel/Negrut-family baseline rows",
        ),
        row(
            "order_and_error_tables_written",
            (RESULTS / "coarse_four_example_order_summary.csv").exists()
            and (RESULTS / "coarse_four_example_order_raw_rows.csv").exists()
            and (RESULTS / "common_reference_error_summary.csv").exists()
            and (RESULTS / "common_reference_error_raw_rows.csv").exists()
            and (RESULTS / "coarse_velocity_order_by_example.png").exists()
            and (RESULTS / "coarse_finest_velocity_error_by_example.png").exists(),
            "results directory",
            "raw/summary CSVs and order/error figures are present",
        ),
    ]

    objective_complete = all(item["status"] == "pass" for item in rows)
    summary = {
        "schema": "objective-closure-audit-v1",
        "objective_complete": objective_complete,
        "row_count": len(rows),
        "passed_count": sum(1 for item in rows if item["status"] == "pass"),
        "failed_requirements": [item["requirement"] for item in rows if item["status"] != "pass"],
        "examples": EXAMPLES,
        "step_sizes": STEP_SIZES,
        "reference_h": REFERENCE_H,
        "local_method": LOCAL,
        "local_orders": local_orders,
        "accepted_runnable_methods": baseline.get("accepted_same_grid_four_example_methods"),
        "required_methods_resolved": baseline.get("required_methods_resolved"),
        "direct_error_comparable_rows": common.get("direct_error_comparable_rows"),
        "apples_to_apples_policy_row_count": apples.get("row_count"),
        "apples_to_apples_policy_safe_rows": apples.get("paper_safe_row_count"),
        "apples_to_apples_nonlocal_comparisons": apples.get("nonlocal_paper_safe_comparison_count"),
        "global_comparison_policy_passed": global_policy.get("reasonable_apples_to_apples_claims"),
        "global_comparison_policy_passed_count": global_policy.get("passed_count"),
        "global_comparison_policy_row_count": global_policy.get("row_count"),
        "mixed_policy_direct_error_vs_local_comparable_rows": global_policy.get(
            "mixed_policy_direct_error_vs_local_comparable_rows"
        ),
        "public_code_fixed_grid_replay": common.get("public_code_fixed_grid_replay"),
        "source_policy_reproduction": common.get("source_policy_reproduction"),
        "local_velocity_order_wins": common.get("local_velocity_order_wins"),
        "local_velocity_order_comparisons": common.get("local_velocity_order_comparisons"),
        "local_finest_velocity_error_wins": common.get("local_finest_velocity_error_wins"),
        "local_finest_velocity_error_comparisons": common.get("local_finest_velocity_error_comparisons"),
        "original_paper_velocity_error_wins": common.get("original_paper_velocity_error_wins"),
        "original_paper_velocity_error_comparisons": common.get("original_paper_velocity_error_comparisons"),
        "kissel_negrut_velocity_error_wins": common.get("kissel_negrut_velocity_error_wins"),
        "kissel_negrut_velocity_error_comparisons": common.get("kissel_negrut_velocity_error_comparisons"),
        "scope_excluded_methods": baseline.get("scope_excluded_methods", []),
        "alias_resolved_methods": baseline.get("alias_resolved_methods", []),
        "claim": (
            "The active comparison objective is complete for the required method matrix: all required "
            "labels are accepted/alias-resolved/source-backed excluded; all four examples use the "
            "coarse h trio under explicit row-level and global apples-to-apples policy audits; "
            "public-code baselines are fixed-grid replayed rather than source-policy reproduced; "
            "mixed-policy direct error claims are blocked; and the local method wins all direct "
            "common-reference velocity-error and velocity-order comparisons against accepted "
            "original-paper and Kissel/Negrut-family rows."
        ),
    }

    write_csv(OUT_CSV, rows)
    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# Objective Closure Audit",
        "",
        f"Objective complete: `{summary['objective_complete']}`.",
        f"Passed requirements: `{summary['passed_count']}/{summary['row_count']}`.",
        f"Step sizes: `{summary['step_sizes']}`; reference h: `{summary['reference_h']}`.",
        "",
        "## Local Orders",
        "",
        "| Example | pos order | vel order | acc order | finest vel error |",
        "|---|---:|---:|---:|---:|",
    ]
    for example in EXAMPLES:
        item = local_orders[example]
        lines.append(
            "| "
            f"`{example}` | `{item['pos_order']}` | `{item['vel_order']}` | "
            f"`{item['acc_order']}` | `{item['finest_vel_error']}` |"
        )
    lines.extend(
        [
            "",
            "## Direct Wins",
            "",
            f"- Apples-to-apples policy rows: `{summary['apples_to_apples_policy_safe_rows']}/{summary['apples_to_apples_policy_row_count']}`.",
            f"- Global comparison-policy audit: `{summary['global_comparison_policy_passed_count']}/{summary['global_comparison_policy_row_count']}`.",
            f"- Mixed-policy direct error rows allowed: `{summary['mixed_policy_direct_error_vs_local_comparable_rows']}`.",
            f"- Source-policy reproduction: `{summary['source_policy_reproduction']}`.",
            f"- Public-code fixed-grid replay: `{summary['public_code_fixed_grid_replay']}`.",
            f"- Local velocity-order wins: `{summary['local_velocity_order_wins']}/{summary['local_velocity_order_comparisons']}`.",
            f"- Local finest-velocity-error wins: `{summary['local_finest_velocity_error_wins']}/{summary['local_finest_velocity_error_comparisons']}`.",
            f"- Original-paper velocity-error wins: `{summary['original_paper_velocity_error_wins']}/{summary['original_paper_velocity_error_comparisons']}`.",
            f"- Kissel/Negrut-family velocity-error wins: `{summary['kissel_negrut_velocity_error_wins']}/{summary['kissel_negrut_velocity_error_comparisons']}`.",
            "",
            "## Requirement Audit",
            "",
            "| Requirement | status | evidence | interpretation |",
            "|---|---:|---|---|",
        ]
    )
    for item in rows:
        lines.append(
            "| "
            f"`{item['requirement']}` | `{item['status']}` | `{item['evidence']}` | "
            f"{item['interpretation']} |"
        )
    lines.extend(["", summary["claim"]])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("objective_closure_audit=written")
    print(f"objective_complete={summary['objective_complete']}")
    print(f"passed={summary['passed_count']}/{summary['row_count']}")


if __name__ == "__main__":
    main()
