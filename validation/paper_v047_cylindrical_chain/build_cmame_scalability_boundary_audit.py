#!/usr/bin/env python3
"""Build a read-only audit for the CMAME scalability/performance boundary."""

from __future__ import annotations

import csv
import json
from pathlib import Path


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
RESULTS = ROOT.parent / "numerics" / "v047_cylindrical_chain_pipeline" / "results"
OUT_JSON = PAPER / "CMAME_SCALABILITY_BOUNDARY_AUDIT.json"
OUT_MD = PAPER / "CMAME_SCALABILITY_BOUNDARY_AUDIT.md"


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def as_float(row: dict[str, str], key: str) -> float:
    return float(row[key])


def as_int(row: dict[str, str], key: str) -> int:
    return int(float(row[key]))


def figure_by_number(figure_audit: dict, number: int) -> dict:
    for row in figure_audit.get("figures", []):
        if isinstance(row, dict) and row.get("number") == number:
            return row
    return {}


def case_summary(speed_row: dict[str, str], cost_row: dict[str, str]) -> dict[str, object]:
    return {
        "case": speed_row["case"],
        "status": speed_row["status"],
        "pattern_nnz": as_int(speed_row, "pattern_nnz"),
        "dense_dimension": as_int(cost_row, "dense_dimension"),
        "column_colors": as_int(speed_row, "column_colors"),
        "row_colors": as_int(speed_row, "row_colors"),
        "row_seed_reduction_fraction": as_float(speed_row, "row_seed_reduction_fraction"),
        "median_dense_runtime_sec": as_float(speed_row, "median_dense_runtime_sec"),
        "median_column_runtime_sec": as_float(speed_row, "median_column_runtime_sec"),
        "median_row_runtime_sec": as_float(speed_row, "median_row_runtime_sec"),
        "row_runtime_over_dense": as_float(cost_row, "row_runtime_over_dense"),
        "row_runtime_over_column": as_float(cost_row, "row_runtime_over_column"),
        "row_runtime_reduction_needed_to_match_dense": as_float(
            cost_row, "row_runtime_reduction_needed_to_match_dense"
        ),
        "row_runtime_reduction_needed_for_10pct_dense_win": as_float(
            cost_row, "row_runtime_reduction_needed_for_10pct_dense_win"
        ),
        "effective_row_colors_at_dense_cost": as_float(cost_row, "effective_row_colors_at_dense_cost"),
        "target_row_colors_for_10pct_dense_win": as_float(cost_row, "target_row_colors_for_10pct_dense_win"),
        "row_beats_column": speed_row["row_beats_column"] == "True",
        "dense_beats_row": speed_row["dense_beats_row"] == "True",
        "component_block_assembly_required": cost_row["component_block_assembly_required"] == "True",
    }


def main() -> None:
    figure_audit = read_json(PAPER / "CMAME_FIGURE_SET_AUDIT.json")
    package_manifest = read_json(PAPER / "CMAME_REPRODUCIBILITY_PACKAGE_MANIFEST.json")
    speed_rows = read_csv(RESULTS / "cylindrical_chain_sparse_speed_gap_audit.csv")
    cost_rows = read_csv(RESULTS / "cylindrical_chain_sparse_cost_model_audit.csv")
    cost_by_case = {row["case"]: row for row in cost_rows}
    cases = [case_summary(row, cost_by_case[row["case"]]) for row in speed_rows]
    fig6 = figure_by_number(figure_audit, 6)
    fig7 = figure_by_number(figure_audit, 7)
    fig9 = figure_by_number(figure_audit, 9)
    summary = package_manifest.get("summary", {})

    dense_beats_all = all(row["dense_beats_row"] for row in cases)
    component_required_all = all(row["component_block_assembly_required"] for row in cases)
    row_runtime_over_dense_values = [float(row["row_runtime_over_dense"]) for row in cases]
    reduction_needed_values = [float(row["row_runtime_reduction_needed_to_match_dense"]) for row in cases]
    reduction_10pct_values = [float(row["row_runtime_reduction_needed_for_10pct_dense_win"]) for row in cases]
    effective_row_colors = [float(row["effective_row_colors_at_dense_cost"]) for row in cases]

    result = {
        "schema": "cmame-scalability-boundary-audit-v1",
        "status": "reference_implementation_scalability_boundary_recorded_b7_open",
        "blocker": "B7",
        "read_only": True,
        "run_v047_invoked": False,
        "submission_ready": False,
        "b7_closed": False,
        "performance_superiority_claim_allowed": False,
        "production_scalability_claim_allowed": False,
        "current_reference_implementation": {
            "residual_dimension": 132,
            "pattern_nnz": sorted({row["pattern_nnz"] for row in cases}),
            "column_colors": sorted({row["column_colors"] for row in cases}),
            "row_colors": sorted({row["row_colors"] for row in cases}),
            "dense_beats_row_all_cases": dense_beats_all,
            "component_block_assembly_required_all_cases": component_required_all,
            "row_runtime_over_dense_min": min(row_runtime_over_dense_values),
            "row_runtime_over_dense_max": max(row_runtime_over_dense_values),
            "row_runtime_reduction_needed_to_match_dense_min": min(reduction_needed_values),
            "row_runtime_reduction_needed_to_match_dense_max": max(reduction_needed_values),
            "row_runtime_reduction_needed_for_10pct_dense_win_min": min(reduction_10pct_values),
            "row_runtime_reduction_needed_for_10pct_dense_win_max": max(reduction_10pct_values),
            "effective_row_colors_at_dense_cost_min": min(effective_row_colors),
            "effective_row_colors_at_dense_cost_max": max(effective_row_colors),
        },
        "work_precision_boundary": {
            "strict_common_reference_figure_present": bool(fig7.get("main_exists") and fig7.get("flat_exists")),
            "coarse_baseline_work_precision_figure_present": bool(fig9.get("main_exists") and fig9.get("flat_exists")),
            "sparse_speed_gap_figure_present": bool(fig6.get("main_exists") and fig6.get("flat_exists")),
            "common_reference_order_wins": summary.get("common_reference_order_wins"),
            "common_reference_error_wins": summary.get("common_reference_error_wins"),
            "source_policy_closed_rows": summary.get("source_policy_closed_rows"),
            "source_policy_total_rows": summary.get("source_policy_total_rows"),
            "external_source_policy_superiority_allowed": False,
        },
        "scalability_campaign_status": {
            "n_body_chain_sweep_present": False,
            "requested_body_counts": [2, 4, 8, 16, 32],
            "completed_body_counts": [],
            "wall_clock_vs_body_count_present": False,
            "newton_iterations_vs_body_count_present": False,
            "jacobian_assembly_vs_body_count_present": False,
            "linear_solve_time_vs_body_count_present": False,
            "condition_number_vs_body_count_present": False,
            "memory_scaling_vs_body_count_present": False,
        },
        "required_to_close": [
            "N-body chain benchmark for N=2,4,8,16,32",
            "dense AD versus sparse/block Jacobian timing",
            "wall-clock, Newton-iteration, Jacobian-assembly, and linear-solve breakdowns",
            "condition-number or rank diagnostics versus body count",
            "memory scaling versus body count",
            "complete source-policy work-precision curves for external suites",
        ],
        "case_rows": cases,
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# CMAME Scalability Boundary Audit",
        "",
        "Status: **reference implementation scalability boundary recorded; B7 remains open**.",
        "",
        f"- Read-only audit: `{result['read_only']}`.",
        f"- Invoked `run_v047.py`: `{result['run_v047_invoked']}`.",
        f"- B7 closed: `{result['b7_closed']}`.",
        f"- Performance superiority claim allowed: `{result['performance_superiority_claim_allowed']}`.",
        f"- Production scalability claim allowed: `{result['production_scalability_claim_allowed']}`.",
        "- Reference residual dimension: `132`.",
        "- Sparse pattern nonzeros: `2637`.",
        "- Column/row colors: `90/60`.",
        (
            "- Row runtime over dense `jacfwd`: "
            f"`{min(row_runtime_over_dense_values):.3f}` to `{max(row_runtime_over_dense_values):.3f}`."
        ),
        (
            "- Row-runtime reduction needed to match dense: "
            f"`{min(reduction_needed_values):.1%}` to `{max(reduction_needed_values):.1%}`."
        ),
        "",
        "## Sparse Timing Boundary",
        "",
        "| case | dense sec | row sec | row/dense | row colors | dense faster | block assembly needed |",
        "|---|---:|---:|---:|---:|---|---|",
    ]
    for row in cases:
        lines.append(
            "| {case} | {dense:.3e} | {row_sec:.3e} | {ratio:.3f} | {colors} | `{dense_fast}` | `{block}` |".format(
                case=row["case"],
                dense=row["median_dense_runtime_sec"],
                row_sec=row["median_row_runtime_sec"],
                ratio=row["row_runtime_over_dense"],
                colors=row["row_colors"],
                dense_fast=row["dense_beats_row"],
                block=row["component_block_assembly_required"],
            )
        )
    lines.extend(
        [
            "",
            "## Work-Precision Boundary",
            "",
            f"- Strict common-reference work/precision figure present: `{result['work_precision_boundary']['strict_common_reference_figure_present']}`.",
            f"- Coarse baseline work/precision figure present: `{result['work_precision_boundary']['coarse_baseline_work_precision_figure_present']}`.",
            f"- Common-reference order/error wins: `{summary.get('common_reference_order_wins')}/{summary.get('common_reference_error_wins')}`.",
            f"- Source-policy rows closed: `{summary.get('source_policy_closed_rows')}/{summary.get('source_policy_total_rows')}`.",
            "- External source-policy superiority remains disallowed.",
            "",
            "## Missing Scalability Campaign",
            "",
            "- N-body chain sweep present: `False`.",
            "- Requested body counts: `N=2,4,8,16,32`.",
            "- Completed body counts: `[]`.",
            "- Wall-clock, Newton-iteration, Jacobian-assembly, linear-solve, condition, and memory scaling versus body count are not yet present.",
            "",
            "## Required To Close",
            "",
        ]
    )
    for item in result["required_to_close"]:
        lines.append(f"- {item}.")
    lines.append("")

    with OUT_MD.open("w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))


if __name__ == "__main__":
    main()
