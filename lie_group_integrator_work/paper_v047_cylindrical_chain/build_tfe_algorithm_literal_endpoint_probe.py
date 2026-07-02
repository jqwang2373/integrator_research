#!/usr/bin/env python3
"""Build a full-horizon TFE endpoint-policy probe from Algorithm 1 literally.

The source paper's Algorithm 1 advances with fixed h while t_n < t_final.  This
probe runs that literal endpoint policy for the active original-TFE pendulum
methods.  It is a runner-policy artifact only: it does not settle the paper's
noninteger-h error sampling convention and does not close source-policy rows.
"""

from __future__ import annotations

import csv
import importlib.util
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
MODEL_PATH = ROOT / "v048_cross_paper_same_test_benchmarks" / "tfe_source_pendulum_model.py"
OUT_JSON = PAPER / "TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE.json"
OUT_MD = PAPER / "TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE.md"
OUT_CSV = PAPER / "TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE.csv"

T_FINAL = 10.0
REFERENCE_H = 1.0e-4
COMPARISON_H = (0.012, 0.006, 0.003)


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def load_model_module():
    spec = importlib.util.spec_from_file_location("tfe_source_pendulum_model", MODEL_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {MODEL_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def pairwise_orders(errors: list[float], hs: tuple[float, ...]) -> list[float | None]:
    orders: list[float | None] = []
    for prev_error, next_error, prev_h, next_h in zip(errors[:-1], errors[1:], hs[:-1], hs[1:]):
        if prev_error > 0.0 and next_error > 0.0 and prev_h > next_h:
            orders.append(float(np.log(prev_error / next_error) / np.log(prev_h / next_h)))
        else:
            orders.append(None)
    return orders


def algorithm_literal_step_count(t_final: float, h: float) -> int:
    return int(math.ceil((float(t_final) - 1.0e-14) / float(h)))


def step_once(model, method: str, theta: float, omega: float, h: float) -> tuple[float, float, int, float]:
    if method == "Newmark_beta":
        return model.newmark_beta_candidate_step(theta, omega, h, beta=0.3, gamma=0.5)
    if method == "trapezoidal":
        return model.trapezoidal_candidate_step(theta, omega, h)
    if method == "TFE_m1":
        return model.tfe_m1_candidate_step(theta, omega, h, nu=0.99)
    if method == "TFE_m2":
        return model.tfe_multinode_candidate_step(theta, omega, h, m=2, nu=0.95)
    raise ValueError(f"unsupported active TFE B2 source method: {method}")


def integrate_algorithm_literal(
    model,
    *,
    method: str,
    theta0: float,
    omega0: float,
    h: float,
    t_final: float,
) -> tuple[Any, dict[str, float]]:
    steps = algorithm_literal_step_count(t_final, h)
    theta = float(theta0)
    omega = float(omega0)
    total_newton_iterations = 0.0
    max_residual_norm = 0.0
    for _ in range(steps):
        theta, omega, iterations, residual_norm = step_once(model, method, theta, omega, h)
        total_newton_iterations += float(iterations)
        max_residual_norm = max(max_residual_norm, float(residual_norm))
    terminal_time = float(steps) * float(h)
    return (
        model.SourcePlanarState(theta=theta, omega=omega),
        {
            "steps": float(steps),
            "terminal_time": terminal_time,
            "terminal_overshoot": terminal_time - float(t_final),
            "hits_exact_T": float(abs(terminal_time - float(t_final)) <= 1.0e-12),
            "total_newton_iterations": total_newton_iterations,
            "max_residual_norm": max_residual_norm,
        },
    )


def main() -> None:
    model = load_model_module()
    grid_audit = read_json(PAPER / "TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.json")
    source_text = grid_audit.get("source_text_endpoint_convention_audit", {})
    reference, _ = model.integrate_planar_case_with_method(
        method="rk4_reference",
        theta0=0.0,
        omega0=0.0,
        h=REFERENCE_H,
        t_final=T_FINAL,
        frictional=False,
        axis="z",
    )

    method_rows: list[dict[str, Any]] = []
    csv_rows: list[dict[str, Any]] = []
    for method in model.active_tfe_b2_source_method_specs():
        coordinate_errors: list[float] = []
        velocity_errors: list[float] = []
        frobenius_errors: list[float] = []
        metrics_rows: list[dict[str, Any]] = []
        for h in COMPARISON_H:
            candidate, diagnostics = integrate_algorithm_literal(
                model,
                method=str(method["source_method"]),
                theta0=0.0,
                omega0=0.0,
                h=float(h),
                t_final=T_FINAL,
            )
            metrics = model.source_error_metrics(reference, candidate, axis="z")
            metric_row = {
                "h": float(h),
                **metrics,
                **diagnostics,
            }
            metrics_rows.append(metric_row)
            coordinate_errors.append(float(metrics["coordinate_error_q"]))
            velocity_errors.append(float(metrics["velocity_error_v"]))
            frobenius_errors.append(float(metrics["frobenius_error_norm_eta"]))
            csv_rows.append(
                {
                    "paper_method": method["paper_method"],
                    "source_method": method["source_method"],
                    "expected_order": method["expected_order"],
                    "h": float(h),
                    "steps": int(diagnostics["steps"]),
                    "terminal_time": diagnostics["terminal_time"],
                    "terminal_overshoot": diagnostics["terminal_overshoot"],
                    "coordinate_error_q": metrics["coordinate_error_q"],
                    "velocity_error_v": metrics["velocity_error_v"],
                    "frobenius_error_norm_eta": metrics["frobenius_error_norm_eta"],
                    "total_newton_iterations": diagnostics["total_newton_iterations"],
                    "max_residual_norm": diagnostics["max_residual_norm"],
                    "source_policy_row_completed": "false",
                }
            )
        method_rows.append(
            {
                "paper_method": method["paper_method"],
                "source_method": method["source_method"],
                "expected_order": method["expected_order"],
                "source_parameters": method["source_parameters"],
                "metrics": metrics_rows,
                "coordinate_pairwise_orders": pairwise_orders(coordinate_errors, COMPARISON_H),
                "velocity_pairwise_orders": pairwise_orders(velocity_errors, COMPARISON_H),
                "frobenius_pairwise_orders": pairwise_orders(frobenius_errors, COMPARISON_H),
                "finite_metrics": all(np.isfinite(value) for row in metrics_rows for value in row.values() if isinstance(value, float)),
                "max_residual_norm": max(float(row["max_residual_norm"]) for row in metrics_rows),
                "source_policy_method_runner_equivalent": False,
                "source_policy_row_completed": False,
                "accepted_use": "algorithm_literal_full_T10_endpoint_probe_not_source_policy",
            }
        )

    terminal_overrun_rows = sum(1 for row in csv_rows if float(row["terminal_overshoot"]) > 1.0e-12)
    output = {
        "schema": "tfe-algorithm-literal-endpoint-probe-v1",
        "status": "algorithm_literal_full_T10_probe_available_source_policy_open",
        "submission_ready": False,
        "external_superiority_claim_allowed": False,
        "source_policy_rows_completed": 0,
        "source_policy_method_runner_equivalent": False,
        "source_policy_exact_T_error_sampling_equivalent": False,
        "source_text_fixed_h_loop_supported": source_text.get("algorithm_literal_constant_h_until_tn_ge_tfinal") is True,
        "source_text_anchor_count": source_text.get("anchor_count"),
        "algorithm_literal_endpoint_policy": "fixed_h_until_tn_ge_tfinal",
        "t_final": T_FINAL,
        "reference_h": REFERENCE_H,
        "comparison_h": list(COMPARISON_H),
        "reference_exact_T": True,
        "reference_theta_final": reference.theta,
        "reference_omega_final": reference.omega,
        "method_count": len(method_rows),
        "metric_row_count": len(csv_rows),
        "terminal_overrun_rows": terminal_overrun_rows,
        "method_rows": method_rows,
        "csv": "TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE.csv",
        "remaining_to_close_source_policy": [
            "prove the source paper's reported error/order sampling uses the algorithm-literal terminal state or another explicit endpoint convention",
            "replace the scalar planar candidate runners with the source-equivalent absolute-coordinate DAE runners or source-code reproduction",
            "keep source_policy_rows_completed at zero until runner equivalence and sampling policy are both closed",
        ],
        "execution_policy": {
            "run_v047_invoked": False,
            "v048_campaign_invoked": False,
            "default_1e_4_required": False,
            "source_reference_h_1e4_invoked_for_scalar_reference": True,
        },
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, sort_keys=True)
        handle.write("\n")
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(csv_rows[0].keys()))
        writer.writeheader()
        writer.writerows(csv_rows)

    lines = [
        "# TFE Algorithm-Literal Endpoint Probe",
        "",
        f"Status: **{output['status']}**.",
        "",
        f"- Source text fixed-h loop supported: `{output['source_text_fixed_h_loop_supported']}`.",
        f"- Endpoint policy: `{output['algorithm_literal_endpoint_policy']}`.",
        f"- Methods / metric rows: `{output['method_count']}/{output['metric_row_count']}`.",
        f"- Terminal overrun rows: `{output['terminal_overrun_rows']}`.",
        f"- Source-policy rows completed: `{output['source_policy_rows_completed']}`.",
        f"- Source-policy method runner equivalent: `{output['source_policy_method_runner_equivalent']}`.",
        f"- Exact-T error sampling equivalent: `{output['source_policy_exact_T_error_sampling_equivalent']}`.",
        "",
        "## Method Summary",
        "",
        "| method | expected order | max residual | coordinate orders | velocity orders |",
        "|---|---:|---:|---|---|",
    ]
    for row in method_rows:
        lines.append(
            f"| `{row['paper_method']}` | `{row['expected_order']}` | `{row['max_residual_norm']:.3e}` | "
            f"`{row['coordinate_pairwise_orders']}` | `{row['velocity_pairwise_orders']}` |"
        )
    lines.extend(["", "## Remaining To Close Source Policy", ""])
    for item in output["remaining_to_close_source_policy"]:
        lines.append(f"- {item}.")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("tfe_algorithm_literal_endpoint_probe=written")
    print(f"methods={output['method_count']}")
    print(f"metric_rows={output['metric_row_count']}")
    print(f"terminal_overrun_rows={output['terminal_overrun_rows']}")
    print("source_policy_rows_completed=0")


if __name__ == "__main__":
    main()
