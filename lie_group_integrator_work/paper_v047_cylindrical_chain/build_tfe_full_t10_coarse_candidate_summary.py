#!/usr/bin/env python3
"""Summarize the non-heavy full-T10 coarse TFE candidate probe."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "TFE_SOURCE_PENDULUM_MODEL_AUDIT.json"
OUT_JSON = PAPER / "TFE_FULL_T10_COARSE_CANDIDATE_SUMMARY.json"
OUT_MD = PAPER / "TFE_FULL_T10_COARSE_CANDIDATE_SUMMARY.md"
OUT_CSV = PAPER / "TFE_FULL_T10_COARSE_CANDIDATE_SUMMARY.csv"


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def pair_text(values: list[float]) -> str:
    return ", ".join(f"{value:.3f}" for value in values)


def main() -> None:
    audit = read_json(AUDIT_JSON)
    probe = audit.get("active_tfe_b2_full_T10_coarse_candidate_probe", {})
    rows: list[dict[str, Any]] = []
    for row in probe.get("rows", []):
        metrics = row.get("metrics", [])
        if len(metrics) != 3:
            raise ValueError(f"expected three h rows for {row.get('paper_method')}")
        finest = metrics[-1]
        rows.append(
            {
                "paper_method": row.get("paper_method"),
                "source_method": row.get("source_method"),
                "expected_order": row.get("expected_order"),
                "comparison_h": probe.get("comparison_h"),
                "reference_h": probe.get("reference_h"),
                "t_final": probe.get("t_final"),
                "coordinate_pairwise_orders": row.get("coordinate_pairwise_orders"),
                "velocity_pairwise_orders": row.get("velocity_pairwise_orders"),
                "coordinate_order_text": pair_text(row.get("coordinate_pairwise_orders", [])),
                "velocity_order_text": pair_text(row.get("velocity_pairwise_orders", [])),
                "finest_h": finest.get("h"),
                "finest_coordinate_error": finest.get("coordinate_error_q"),
                "finest_velocity_error": finest.get("velocity_error_v"),
                "finest_frobenius_error": finest.get("frobenius_error_norm_eta"),
                "max_newton_residual_norm": row.get("max_newton_residual_norm"),
                "total_newton_iterations": row.get("total_newton_iterations"),
                "coordinate_error_decreased": row.get("coordinate_error_decreased"),
                "velocity_error_decreased": row.get("velocity_error_decreased"),
                "source_policy_method_runner_equivalent": row.get("source_policy_method_runner_equivalent"),
                "source_policy_row_completed": row.get("source_policy_row_completed"),
                "accepted_use": row.get("accepted_use"),
            }
        )

    result = {
        "schema": "tfe-full-t10-coarse-candidate-summary-v1",
        "status": "full_T10_coarse_candidate_probe_summarized_not_source_policy",
        "submission_ready": False,
        "external_superiority_claim_allowed": False,
        "source_policy_rows_completed": probe.get("source_policy_rows_completed"),
        "source_policy_reference_h": probe.get("source_policy_reference_h"),
        "source_policy_reference_invoked": not bool(probe.get("source_policy_reference_not_invoked")),
        "default_1e_4_campaign_invoked": probe.get("default_1e_4_campaign_invoked"),
        "full_T10_candidate_probe_completed": probe.get("full_T10_candidate_probe_completed"),
        "full_T10_source_policy_reproduction": probe.get("full_T10_source_policy_reproduction"),
        "t_final": probe.get("t_final"),
        "comparison_h": probe.get("comparison_h"),
        "reference_h": probe.get("reference_h"),
        "row_count": len(rows),
        "finite_row_count": probe.get("finite_row_count"),
        "residual_ok_row_count": probe.get("residual_ok_row_count"),
        "coordinate_error_decrease_row_count": probe.get("coordinate_error_decrease_row_count"),
        "velocity_error_decrease_row_count": probe.get("velocity_error_decrease_row_count"),
        "claim_boundary": {
            "accepted_use": "non_heavy_full_T10_large_step_candidate_diagnostic",
            "not_source_policy_reproduction": True,
            "not_external_superiority_evidence": True,
            "reason": (
                "The run uses the original T=10 horizon, but uses h_ref=0.0125 "
                "instead of the extracted source-policy reference h=1e-4 and does "
                "not certify source-code-equivalent TFE/Newmark/trapezoidal runners."
            ),
        },
        "rows": rows,
        "source_files": {
            "tfe_source_pendulum_model_audit": "TFE_SOURCE_PENDULUM_MODEL_AUDIT.json",
            "source_model": "../v048_cross_paper_same_test_benchmarks/tfe_source_pendulum_model.py",
        },
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")

    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = [
            "paper_method",
            "source_method",
            "expected_order",
            "t_final",
            "reference_h",
            "comparison_h",
            "velocity_order_text",
            "coordinate_order_text",
            "finest_h",
            "finest_velocity_error",
            "finest_coordinate_error",
            "max_newton_residual_norm",
            "source_policy_row_completed",
            "accepted_use",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key) for key in fieldnames})

    lines = [
        "# TFE Full-T10 Coarse Candidate Summary",
        "",
        "Status: **full T=10 coarse candidate probe summarized; source-policy not closed**.",
        "",
        f"- Full T=10 candidate probe completed: `{result['full_T10_candidate_probe_completed']}`.",
        f"- T/reference h/comparison h: `{result['t_final']}` / `{result['reference_h']}` / `{result['comparison_h']}`.",
        f"- Source-policy reference h/invoked: `{result['source_policy_reference_h']}` / `{result['source_policy_reference_invoked']}`.",
        f"- Source-policy rows completed: `{result['source_policy_rows_completed']}`.",
        f"- Finite/residual-ok rows: `{result['finite_row_count']}/{result['residual_ok_row_count']}`.",
        f"- Coordinate/velocity error-decrease rows: `{result['coordinate_error_decrease_row_count']}/{result['velocity_error_decrease_row_count']}`.",
        f"- External superiority claim allowed: `{result['external_superiority_claim_allowed']}`.",
        f"- Default 1e-4 campaign invoked: `{result['default_1e_4_campaign_invoked']}`.",
        "",
        "## Rows",
        "",
        "| method | target | velocity pair orders | coordinate pair orders | finest velocity error | finest coordinate error | max residual |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| "
            f"`{row['paper_method']}` | `{row['expected_order']}` | "
            f"`{row['velocity_order_text']}` | `{row['coordinate_order_text']}` | "
            f"`{row['finest_velocity_error']:.3e}` | `{row['finest_coordinate_error']:.3e}` | "
            f"`{row['max_newton_residual_norm']:.3e}` |"
        )
    lines.extend(
        [
            "",
            "This artifact is intentionally claim-bounded: it confirms non-heavy full-horizon candidate behavior, but does not close original TFE source-policy reproduction.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("tfe_full_t10_coarse_candidate_summary=written")
    print(f"rows={result['row_count']}")
    print(f"finite_residual_ok={result['finite_row_count']}/{result['residual_ok_row_count']}")
    print("source_policy_rows_completed=0")


if __name__ == "__main__":
    main()
