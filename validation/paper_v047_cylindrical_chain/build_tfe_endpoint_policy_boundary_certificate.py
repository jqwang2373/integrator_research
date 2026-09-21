#!/usr/bin/env python3
"""Build a strict boundary certificate for the TFE endpoint policy."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.json"
OUT_MD = PAPER / "TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.md"
OUT_CSV = PAPER / "TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.csv"


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def as_float(value: Any) -> float:
    return float(value)


def main() -> None:
    grid = read_json(PAPER / "TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.json")
    endpoint_probe = read_json(PAPER / "TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE.json")
    endpoint_work = read_json(PAPER / "TFE_ALGORITHM_LITERAL_WORK_PRECISION_AUDIT.json")
    sensitivity = read_json(PAPER / "TFE_ENDPOINT_POLICY_SENSITIVITY_AUDIT.json")

    literal_by_id = {
        row["row_id"]: row
        for row in grid.get("source_text_endpoint_convention_audit", {}).get(
            "algorithm_literal_rows", []
        )
    }
    certificate_rows: list[dict[str, Any]] = []
    for row in grid.get("rows", []):
        row_id = str(row["row_id"])
        literal = literal_by_id[row_id]
        h = as_float(row["h"])
        overshoot = as_float(literal["algorithm_literal_overshoot"])
        terminal_time = as_float(literal["algorithm_literal_terminal_time"])
        hits_exact_t = bool(literal["hits_exact_T"])
        certificate_rows.append(
            {
                "row_id": row_id,
                "case_id": row["case_id"],
                "friction_enabled": bool(row["friction_enabled"]),
                "h": h,
                "t_final": as_float(row["t_final"]),
                "exact_steps": as_float(row["exact_steps"]),
                "ceil_steps_to_reach_or_exceed_T": int(literal["steps_to_reach_or_exceed_T"]),
                "algorithm_literal_terminal_time": terminal_time,
                "algorithm_literal_overshoot": overshoot,
                "algorithm_literal_overrun_strictly_less_than_h": (
                    0.0 < overshoot < h if not hits_exact_t else overshoot == 0.0
                ),
                "hits_exact_T": hits_exact_t,
                "integer_step_compatible": bool(row["integer_step_compatible"]),
                "final_partial_step_size_for_exact_T": as_float(
                    row["final_partial_step_size_for_exact_T"]
                ),
                "final_partial_step_fraction_of_h": as_float(
                    row["final_partial_step_fraction_of_h"]
                ),
                "requires_source_error_sampling_policy": bool(
                    row["source_endpoint_policy_needed_for_exact_T"]
                ),
                "source_policy_row_completed": False,
                "source_policy_demoted_until_source_endpoint_sampling_policy": not hits_exact_t,
            }
        )

    compatible_rows = [row for row in certificate_rows if row["hits_exact_T"]]
    overrun_rows = [row for row in certificate_rows if not row["hits_exact_T"]]
    row_fieldnames = [
        "row_id",
        "case_id",
        "friction_enabled",
        "h",
        "t_final",
        "exact_steps",
        "ceil_steps_to_reach_or_exceed_T",
        "algorithm_literal_terminal_time",
        "algorithm_literal_overshoot",
        "algorithm_literal_overrun_strictly_less_than_h",
        "hits_exact_T",
        "integer_step_compatible",
        "final_partial_step_size_for_exact_T",
        "final_partial_step_fraction_of_h",
        "requires_source_error_sampling_policy",
        "source_policy_row_completed",
        "source_policy_demoted_until_source_endpoint_sampling_policy",
    ]

    result = {
        "schema": "tfe-endpoint-policy-boundary-certificate-v1",
        "status": "endpoint_policy_literal_overrun_bound_proved_source_policy_open",
        "read_only": True,
        "submission_ready": False,
        "source_policy_rows_completed": 0,
        "external_superiority_claim_allowed": False,
        "source_policy_exact_T_error_sampling_equivalent": False,
        "source_policy_method_runner_equivalent": False,
        "source_grid_policy_resolved_for_full_T10": False,
        "source_grid_policy_resolved_for_exact_T_compatible_rows": grid.get(
            "source_grid_policy_resolved_for_exact_T_compatible_rows"
        ),
        "algorithm_literal_endpoint_policy": endpoint_probe.get(
            "algorithm_literal_endpoint_policy"
        ),
        "t_final": 10.0,
        "row_count": len(certificate_rows),
        "algorithm_literal_overrun_row_count": len(overrun_rows),
        "algorithm_literal_exact_T_row_count": len(compatible_rows),
        "source_endpoint_incompatible_row_ids": [
            row["row_id"] for row in overrun_rows
        ],
        "source_endpoint_compatible_row_ids": [
            row["row_id"] for row in compatible_rows
        ],
        "source_endpoint_incompatible_row_ids_demoted_from_source_policy": [
            row["row_id"] for row in overrun_rows
        ],
        "endpoint_incompatible_rows_demoted_from_source_policy": len(overrun_rows),
        "endpoint_incompatible_demotion_contract": (
            "Algorithm-literal overrun rows are diagnostic-only and excluded from source-policy "
            "promotion unless source-confirmed endpoint/output sampling for noninteger T/h is found."
        ),
        "theorem": {
            "name": "fixed_h_until_final_time_endpoint_bound",
            "statement": (
                "For T>0 and h>0, the Algorithm-1-literal loop with fixed h "
                "and N=ceil(T/h) terminates at t_N=N h. If T/h is not an "
                "integer, then 0 < t_N - T < h; if T/h is an integer, then "
                "t_N=T."
            ),
            "assumptions": [
                "Algorithm 1 advances by the published fixed step h.",
                "The loop condition is while t_n < t_final.",
                "No source-confirmed interpolation, adjusted h, or partial final step is used for the reported error sample.",
            ],
            "proof_steps": [
                "The loop performs N=ceil(T/h) fixed-size updates before the first index with t_N >= T.",
                "By the ceiling definition, N-1 < T/h <= N.",
                "Multiplying by h gives (N-1)h < T <= Nh.",
                "Thus t_N=Nh and t_N-T is nonnegative and strictly smaller than h.",
                "The residual is zero exactly when T/h is an integer; otherwise the terminal state is an overrun state rather than an exact-T state.",
            ],
            "conclusion": (
                "Endpoint-incompatible published h rows need a source-confirmed "
                "error/output sampling policy before any exact-T source-policy "
                "row or work/precision row can be accepted; otherwise they remain "
                "explicitly demoted from the source-policy row set."
            ),
        },
        "source_text_support": {
            "source_text_available": grid.get("source_text_endpoint_convention_audit", {}).get(
                "source_text_available"
            ),
            "anchor_count": grid.get("source_text_endpoint_convention_audit", {}).get(
                "anchor_count"
            ),
            "algorithm_literal_constant_h_until_tn_ge_tfinal": grid.get(
                "source_text_endpoint_convention_audit", {}
            ).get("algorithm_literal_constant_h_until_tn_ge_tfinal"),
            "source_endpoint_convention_resolved_for_error_sampling": grid.get(
                "source_text_endpoint_convention_audit", {}
            ).get("source_endpoint_convention_resolved_for_error_sampling"),
        },
        "diagnostic_work_precision_boundary": {
            "source_probe": "TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE.json",
            "work_precision_audit": "TFE_ALGORITHM_LITERAL_WORK_PRECISION_AUDIT.json",
            "endpoint_policy_sensitivity_audit": "TFE_ENDPOINT_POLICY_SENSITIVITY_AUDIT.json",
            "endpoint_probe_metric_rows": endpoint_probe.get("metric_row_count"),
            "endpoint_probe_terminal_overrun_rows": endpoint_probe.get(
                "terminal_overrun_rows"
            ),
            "work_precision_rows": endpoint_work.get("raw_row_count"),
            "work_precision_summary_rows": endpoint_work.get("summary_row_count"),
            "work_precision_figure_available": endpoint_work.get(
                "work_precision_figure_available"
            ),
            "work_precision_b4_progress": endpoint_work.get("decision", {}).get(
                "b4_progress"
            ),
            "work_precision_b4_closure": endpoint_work.get("decision", {}).get(
                "b4_closure"
            ),
            "endpoint_sensitivity_raw_rows": sensitivity.get("raw_row_count"),
            "endpoint_sensitivity_source_policy_rows_completed": sensitivity.get(
                "source_policy_rows_completed"
            ),
        },
        "policy_disposition": [
            {
                "policy": "algorithm_literal_fixed_h_until_tn_ge_tfinal",
                "proved_grid_effect": "overrun_for_noninteger_T_over_h",
                "source_equivalent_for_exact_T_error_sampling": False,
                "source_policy_rows_completed": 0,
            },
            {
                "policy": "adjust_h_to_hit_T_exactly",
                "proved_grid_effect": "exact_T_by_changing_published_h",
                "source_equivalent_for_exact_T_error_sampling": False,
                "source_policy_rows_completed": 0,
            },
            {
                "policy": "integer_steps_plus_final_partial_step",
                "proved_grid_effect": "exact_T_by_adding_unconfirmed_partial_step",
                "source_equivalent_for_exact_T_error_sampling": False,
                "source_policy_rows_completed": 0,
            },
            {
                "policy": "interpolate_or_sample_exact_T",
                "proved_grid_effect": "requires_source_output_policy_not_present_in_text",
                "source_equivalent_for_exact_T_error_sampling": False,
                "source_policy_rows_completed": 0,
            },
        ],
        "rows": certificate_rows,
        "claim_boundary": {
            "proved": "algorithm_literal_fixed_h_endpoint_overrun_bound",
            "not_proved": [
                "source-code-equivalent endpoint/output sampling for noninteger T/h rows",
                "exact-T source-policy error sampling equivalence",
                "source-policy method-runner equivalence",
                "B4/B7 source-policy closure",
            ],
            "demoted": [
                "endpoint-incompatible noninteger T/h rows without source-confirmed endpoint/output sampling",
            ],
            "accepted_use": "endpoint_policy_boundary_proof_not_source_policy",
        },
        "source_files": {
            "grid_audit": "TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.json",
            "algorithm_literal_endpoint_probe": "TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE.json",
            "algorithm_literal_work_precision": "TFE_ALGORITHM_LITERAL_WORK_PRECISION_AUDIT.json",
            "endpoint_sensitivity": "TFE_ENDPOINT_POLICY_SENSITIVITY_AUDIT.json",
        },
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")

    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=row_fieldnames)
        writer.writeheader()
        writer.writerows(certificate_rows)

    lines = [
        "# TFE Endpoint Policy Boundary Certificate",
        "",
        f"Status: **{result['status']}**.",
        "",
        "This certificate is a read-only proof over the extracted TFE source grid and endpoint diagnostics.",
        "",
        "## Boundary",
        "",
        f"- Source-policy rows completed: `{result['source_policy_rows_completed']}`.",
        f"- Full T=10 source-grid policy resolved: `{result['source_grid_policy_resolved_for_full_T10']}`.",
        f"- Exact-T error-sampling equivalent: `{result['source_policy_exact_T_error_sampling_equivalent']}`.",
        f"- Method-runner equivalent: `{result['source_policy_method_runner_equivalent']}`.",
        f"- Algorithm-literal endpoint policy: `{result['algorithm_literal_endpoint_policy']}`.",
        f"- Exact-T / overrun source h rows: `{result['algorithm_literal_exact_T_row_count']}/{result['algorithm_literal_overrun_row_count']}`.",
        f"- Endpoint-incompatible demoted rows: `{result['endpoint_incompatible_rows_demoted_from_source_policy']}`.",
        "",
        "## Theorem",
        "",
        result["theorem"]["statement"],
        "",
        "Proof sketch:",
    ]
    for step in result["theorem"]["proof_steps"]:
        lines.append(f"- {step}")
    lines.extend(
        [
            "",
            f"Conclusion: {result['theorem']['conclusion']}",
            "",
            "## Source Text Support",
            "",
            f"- Source text available / anchors / fixed-h loop: `{result['source_text_support']['source_text_available']}/{result['source_text_support']['anchor_count']}/{result['source_text_support']['algorithm_literal_constant_h_until_tn_ge_tfinal']}`.",
            f"- Source endpoint convention resolved for error sampling: `{result['source_text_support']['source_endpoint_convention_resolved_for_error_sampling']}`.",
            f"- Demotion contract: {result['endpoint_incompatible_demotion_contract']}",
            "",
            "## Diagnostic Work Precision Boundary",
            "",
            (
                "- Endpoint probe metric/overrun rows: "
                f"`{result['diagnostic_work_precision_boundary']['endpoint_probe_metric_rows']}/"
                f"{result['diagnostic_work_precision_boundary']['endpoint_probe_terminal_overrun_rows']}`."
            ),
            (
                "- Work-precision rows/summary/figure/B4-progress/B4-closure: "
                f"`{result['diagnostic_work_precision_boundary']['work_precision_rows']}/"
                f"{result['diagnostic_work_precision_boundary']['work_precision_summary_rows']}/"
                f"{result['diagnostic_work_precision_boundary']['work_precision_figure_available']}/"
                f"{result['diagnostic_work_precision_boundary']['work_precision_b4_progress']}/"
                f"{result['diagnostic_work_precision_boundary']['work_precision_b4_closure']}`."
            ),
            "",
            "## Rows",
            "",
            "| row | h | terminal time | overshoot | hits exact T | source-policy row |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in certificate_rows:
        lines.append(
            f"| `{row['row_id']}` | `{row['h']:.12g}` | "
            f"`{row['algorithm_literal_terminal_time']:.12g}` | "
            f"`{row['algorithm_literal_overshoot']:.12g}` | "
            f"`{row['hits_exact_T']}` | `{row['source_policy_row_completed']}` |"
        )
    lines.extend(
        [
            "",
            "No source-policy rows are closed by this certificate.",
            "Endpoint-incompatible rows remain demoted from source-policy promotion until a source-confirmed endpoint/output sampling policy is available.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("tfe_endpoint_policy_boundary_certificate=written")
    print(f"rows={result['row_count']}")
    print(
        "exact_overrun_rows="
        f"{result['algorithm_literal_exact_T_row_count']}/"
        f"{result['algorithm_literal_overrun_row_count']}"
    )
    print("source_policy_rows_completed=0")


if __name__ == "__main__":
    main()
