#!/usr/bin/env python3
"""Summarize a full-T10 absolute-coordinate DAE-lift TFE diagnostic.

This artifact takes the existing active-B2 planar candidate runners over the
source paper's T=10 horizon and streams every accepted candidate step through
the absolute-coordinate pendulum residual smoke. It is a stronger full-horizon
diagnostic than the bounded short runner, but it is still not a source-policy
DAE runner or source-code-equivalent method reproduction.
"""

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
MODEL_PATH = ROOT / "v048_cross_paper_same_test_benchmarks" / "tfe_source_pendulum_model.py"
OUT_JSON = PAPER / "TFE_FULL_T10_ABSOLUTE_DAE_LIFT_SUMMARY.json"
OUT_MD = PAPER / "TFE_FULL_T10_ABSOLUTE_DAE_LIFT_SUMMARY.md"
OUT_CSV = PAPER / "TFE_FULL_T10_ABSOLUTE_DAE_LIFT_SUMMARY.csv"

T_FINAL = 10.0
COMPARISON_H = (0.1, 0.05, 0.025)
SOURCE_REFERENCE_H = 1.0e-4


def load_model_module():
    spec = importlib.util.spec_from_file_location("tfe_source_pendulum_model", MODEL_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {MODEL_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def pair_text(values: list[float]) -> str:
    return ", ".join(f"{float(value):.3f}" for value in values)


def main() -> None:
    model = load_model_module()
    config = model.BoundedSourcePolicyRunnerConfig(
        theta0=0.0,
        omega0=0.0,
        t_final=T_FINAL,
        comparison_h=COMPARISON_H,
        reference_h=SOURCE_REFERENCE_H,
        axis="z",
        frictional=False,
    )
    probe = model.bounded_absolute_coordinate_dae_trajectory_runner_smoke(config)

    rows: list[dict[str, Any]] = []
    csv_rows: list[dict[str, Any]] = []
    for row in probe.get("rows", []):
        metrics = row.get("metrics", [])
        if len(metrics) != len(COMPARISON_H):
            raise ValueError(f"expected {len(COMPARISON_H)} h rows for {row.get('paper_method')}")
        finest = metrics[-1]
        row_summary = {
            "paper_method": row.get("paper_method"),
            "source_method": row.get("source_method"),
            "expected_order": row.get("expected_order"),
            "t_final": T_FINAL,
            "comparison_h": list(COMPARISON_H),
            "reference_h": SOURCE_REFERENCE_H,
            "coordinate_pairwise_orders": row.get("coordinate_pairwise_orders"),
            "velocity_pairwise_orders": row.get("velocity_pairwise_orders"),
            "coordinate_order_text": pair_text(row.get("coordinate_pairwise_orders", [])),
            "velocity_order_text": pair_text(row.get("velocity_pairwise_orders", [])),
            "step_residual_rows": row.get("step_residual_rows"),
            "step_states_finite": row.get("step_states_finite"),
            "total_newton_iterations": row.get("total_newton_iterations"),
            "max_candidate_step_residual_norm": row.get("max_candidate_step_residual_norm"),
            "max_hinge_position_constraint_norm": row.get("max_hinge_position_constraint_norm"),
            "max_hinge_velocity_constraint_norm": row.get("max_hinge_velocity_constraint_norm"),
            "max_translational_balance_residual_norm": row.get("max_translational_balance_residual_norm"),
            "max_axis_projected_rotational_residual_abs": row.get("max_axis_projected_rotational_residual_abs"),
            "finest_h": finest.get("h"),
            "finest_coordinate_error": finest.get("coordinate_error_q"),
            "finest_velocity_error": finest.get("velocity_error_v"),
            "finest_frobenius_error": finest.get("frobenius_error_norm_eta"),
            "finest_hinge_position_constraint_norm": finest.get("final_hinge_position_constraint_norm"),
            "finest_hinge_velocity_constraint_norm": finest.get("final_hinge_velocity_constraint_norm"),
            "monolithic_absolute_coordinate_dae_time_integrator": row.get(
                "monolithic_absolute_coordinate_dae_time_integrator"
            ),
            "source_policy_dae_runner_equivalent": row.get("source_policy_dae_runner_equivalent"),
            "source_policy_method_runner_equivalent": row.get("source_policy_method_runner_equivalent"),
            "source_policy_row_completed": row.get("source_policy_row_completed"),
            "accepted_use": "full_T10_absolute_dae_lift_candidate_not_source_policy",
        }
        rows.append(row_summary)
        csv_rows.append(
            {
                "paper_method": row_summary["paper_method"],
                "source_method": row_summary["source_method"],
                "expected_order": row_summary["expected_order"],
                "t_final": row_summary["t_final"],
                "reference_h": row_summary["reference_h"],
                "comparison_h": row_summary["comparison_h"],
                "velocity_order_text": row_summary["velocity_order_text"],
                "coordinate_order_text": row_summary["coordinate_order_text"],
                "step_residual_rows": row_summary["step_residual_rows"],
                "finest_h": row_summary["finest_h"],
                "finest_velocity_error": row_summary["finest_velocity_error"],
                "finest_coordinate_error": row_summary["finest_coordinate_error"],
                "max_candidate_step_residual_norm": row_summary["max_candidate_step_residual_norm"],
                "max_hinge_position_constraint_norm": row_summary["max_hinge_position_constraint_norm"],
                "max_hinge_velocity_constraint_norm": row_summary["max_hinge_velocity_constraint_norm"],
                "max_translational_balance_residual_norm": row_summary[
                    "max_translational_balance_residual_norm"
                ],
                "max_axis_projected_rotational_residual_abs": row_summary[
                    "max_axis_projected_rotational_residual_abs"
                ],
                "source_policy_row_completed": row_summary["source_policy_row_completed"],
                "accepted_use": row_summary["accepted_use"],
            }
        )

    result = {
        "schema": "tfe-full-t10-absolute-dae-lift-summary-v1",
        "status": "full_T10_absolute_dae_lift_candidate_summarized_not_source_policy",
        "submission_ready": False,
        "external_superiority_claim_allowed": False,
        "source_policy_rows_completed": 0,
        "full_T10_absolute_coordinate_lift_completed": True,
        "monolithic_absolute_coordinate_dae_time_integrator": False,
        "source_policy_dae_runner_equivalent": False,
        "source_policy_method_runner_equivalent": False,
        "default_1e_4_campaign_invoked": False,
        "source_reference_h": SOURCE_REFERENCE_H,
        "source_reference_invoked": True,
        "t_final": T_FINAL,
        "comparison_h": list(COMPARISON_H),
        "reference_h": SOURCE_REFERENCE_H,
        "method_count": probe.get("method_count"),
        "row_count": len(rows),
        "metric_row_count": probe.get("metric_row_count"),
        "step_residual_row_count": probe.get("step_residual_row_count"),
        "all_step_states_finite": probe.get("all_step_states_finite"),
        "max_candidate_step_residual_norm": probe.get("max_candidate_step_residual_norm"),
        "max_hinge_position_constraint_norm": probe.get("max_hinge_position_constraint_norm"),
        "max_hinge_velocity_constraint_norm": probe.get("max_hinge_velocity_constraint_norm"),
        "max_translational_balance_residual_norm": probe.get("max_translational_balance_residual_norm"),
        "max_axis_projected_rotational_residual_abs": probe.get("max_axis_projected_rotational_residual_abs"),
        "claim_boundary": {
            "accepted_use": "full_T10_absolute_coordinate_residual_diagnostic",
            "not_source_policy_reproduction": True,
            "not_monolithic_source_policy_dae_runner": True,
            "not_external_superiority_evidence": True,
            "reason": (
                "The diagnostic invokes the extracted h=1e-4 source-reference scale and checks absolute-coordinate "
                "residuals over the full T=10 horizon, but the stepper remains a planar candidate dispatch and does "
                "not resolve original source-code method equivalence, endpoint sampling policy, or Brown-McPhee "
                "source-code-equivalent friction."
            ),
        },
        "rows": rows,
        "source_files": {
            "source_model": "../v048_cross_paper_same_test_benchmarks/tfe_source_pendulum_model.py",
            "source_policy_spec": "TFE_SOURCE_POLICY_SPEC.json",
            "dae_gap_audit": "TFE_DAE_RUNNER_CONTRACT_GAP_AUDIT.json",
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(csv_rows[0]))
        writer.writeheader()
        writer.writerows(csv_rows)

    lines = [
        "# TFE Full-T10 Absolute DAE-Lift Summary",
        "",
        "Status: **full T=10 absolute-coordinate DAE-lift candidate summarized; source-policy not closed**.",
        "",
        f"- Full T=10 absolute-coordinate lift completed: `{result['full_T10_absolute_coordinate_lift_completed']}`.",
        f"- T/reference h/comparison h: `{result['t_final']}` / `{result['reference_h']}` / `{result['comparison_h']}`.",
        f"- Source reference invoked: `{result['source_reference_invoked']}`.",
        f"- Source-policy rows completed: `{result['source_policy_rows_completed']}`.",
        f"- Monolithic source-policy DAE runner: `{result['monolithic_absolute_coordinate_dae_time_integrator']}`.",
        f"- Source-policy DAE/method equivalence: `{result['source_policy_dae_runner_equivalent']}/{result['source_policy_method_runner_equivalent']}`.",
        f"- Methods/metric rows/step residual rows: `{result['method_count']}/{result['metric_row_count']}/{result['step_residual_row_count']}`.",
        f"- All step states finite: `{result['all_step_states_finite']}`.",
        f"- Max hinge position/velocity residuals: `{result['max_hinge_position_constraint_norm']:.3e}/{result['max_hinge_velocity_constraint_norm']:.3e}`.",
        f"- Max translational/axis rotational residuals: `{result['max_translational_balance_residual_norm']:.3e}/{result['max_axis_projected_rotational_residual_abs']:.3e}`.",
        "",
        "## Rows",
        "",
        "| method | target | velocity pair orders | coordinate pair orders | step residual rows | finest velocity error | max DAE residual |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| "
            f"`{row['paper_method']}` | `{row['expected_order']}` | "
            f"`{row['velocity_order_text']}` | `{row['coordinate_order_text']}` | "
            f"`{row['step_residual_rows']}` | `{row['finest_velocity_error']:.3e}` | "
            f"`{row['max_axis_projected_rotational_residual_abs']:.3e}` |"
        )
    lines.extend(
        [
            "",
            "This artifact is claim-bounded. It strengthens full-horizon absolute-coordinate residual diagnostics, but it does not close original TFE source-policy reproduction.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("tfe_full_t10_absolute_dae_lift_summary=written")
    print(f"rows={result['row_count']}")
    print(f"metric_step_rows={result['metric_row_count']}/{result['step_residual_row_count']}")
    print("source_policy_rows_completed=0")


if __name__ == "__main__":
    main()
