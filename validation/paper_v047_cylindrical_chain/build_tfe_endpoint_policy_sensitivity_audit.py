#!/usr/bin/env python3
"""Build a diagnostic TFE endpoint-policy sensitivity audit.

This is a bounded numerical diagnostic over the current planar candidate TFE
runner. It quantifies how much the unresolved T=10 endpoint convention can move
observed order/error for the active original-TFE B2 rows. It is not a
source-policy reproduction and must not close any external-superiority row.
"""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np


PAPER = Path(__file__).resolve().parent
V048 = PAPER.parent.parent / "numerics" / "v048_cross_paper_same_test_benchmarks"
sys.path.insert(0, str(V048))

from tfe_source_pendulum_model import (  # noqa: E402
    active_tfe_b2_source_method_specs,
    brown_mcphee_candidate_torque,
    frictional_planar_rhs,
    newmark_beta_candidate_step,
    planar_pivot_reaction_norm,
    rk4_step,
    rk4_step_frictional,
    source_error_metrics,
    tfe_m1_candidate_step,
    tfe_multinode_candidate_step,
    trapezoidal_candidate_step,
)


OUT_JSON = PAPER / "TFE_ENDPOINT_POLICY_SENSITIVITY_AUDIT.json"
OUT_MD = PAPER / "TFE_ENDPOINT_POLICY_SENSITIVITY_AUDIT.md"
OUT_CSV = PAPER / "TFE_ENDPOINT_POLICY_SENSITIVITY_AUDIT.csv"


def pairwise_orders(errors: list[float], hs: list[float]) -> list[float | None]:
    orders: list[float | None] = []
    for prev_error, next_error, prev_h, next_h in zip(errors[:-1], errors[1:], hs[:-1], hs[1:]):
        if prev_error > 0.0 and next_error > 0.0 and prev_h > next_h:
            orders.append(float(np.log(prev_error / next_error) / np.log(prev_h / next_h)))
        else:
            orders.append(None)
    return orders


def advance_one(
    method: str,
    theta: float,
    omega: float,
    h: float,
    *,
    frictional: bool,
    axis: str,
) -> tuple[float, float, int, float]:
    if method == "rk4_reference":
        if frictional:
            theta, omega = rk4_step_frictional(theta, omega, h, axis=axis)
        else:
            theta, omega = rk4_step(theta, omega, h, axis=axis)
        return theta, omega, 0, 0.0
    if method == "trapezoidal":
        return trapezoidal_candidate_step(theta, omega, h, frictional=frictional, axis=axis)
    if method == "Newmark_beta":
        return newmark_beta_candidate_step(theta, omega, h, beta=0.3, gamma=0.5, frictional=frictional, axis=axis)
    if method == "TFE_m1":
        return tfe_m1_candidate_step(theta, omega, h, nu=0.99, frictional=frictional, axis=axis)
    if method == "TFE_m2":
        return tfe_multinode_candidate_step(theta, omega, h, m=2, nu=0.95, frictional=frictional, axis=axis)
    raise ValueError(f"unsupported method: {method}")


def integrate_steps(
    *,
    method: str,
    theta0: float,
    omega0: float,
    h: float,
    steps: int,
    final_h: float,
    frictional: bool,
    axis: str,
) -> tuple[Any, dict[str, float]]:
    theta = float(theta0)
    omega = float(omega0)
    total_iterations = 0
    max_residual = 0.0
    for _ in range(int(steps)):
        theta, omega, iterations, residual = advance_one(method, theta, omega, h, frictional=frictional, axis=axis)
        total_iterations += int(iterations)
        max_residual = max(max_residual, float(residual))
    if final_h > 1.0e-14:
        theta, omega, iterations, residual = advance_one(
            method, theta, omega, final_h, frictional=frictional, axis=axis
        )
        total_iterations += int(iterations)
        max_residual = max(max_residual, float(residual))

    class State:
        def __init__(self, theta: float, omega: float) -> None:
            self.theta = theta
            self.omega = omega

    return State(theta, omega), {
        "steps": float(steps),
        "final_partial_h": float(final_h),
        "total_newton_iterations": float(total_iterations),
        "max_residual_norm": float(max_residual),
    }


def endpoint_policy_steps(policy: str, *, t_final: float, nominal_h: float) -> dict[str, float | int | bool]:
    exact_steps = t_final / nominal_h
    if policy == "adjust_h_to_hit_T_exactly":
        steps = int(round(exact_steps))
        h_effective = t_final / steps
        return {
            "steps": steps,
            "h_effective": h_effective,
            "final_partial_h": 0.0,
            "terminal_time": t_final,
            "keeps_exact_T": True,
            "keeps_published_h": False,
        }
    if policy == "algorithm_literal_fixed_h_until_tn_ge_tfinal":
        steps = int(math.ceil(exact_steps - 1.0e-14))
        return {
            "steps": steps,
            "h_effective": nominal_h,
            "final_partial_h": 0.0,
            "terminal_time": steps * nominal_h,
            "keeps_exact_T": abs(steps * nominal_h - t_final) <= 1.0e-12,
            "keeps_published_h": True,
        }
    if policy == "floor_horizon":
        steps = int(math.floor(exact_steps + 1.0e-14))
        return {
            "steps": steps,
            "h_effective": nominal_h,
            "final_partial_h": 0.0,
            "terminal_time": steps * nominal_h,
            "keeps_exact_T": abs(steps * nominal_h - t_final) <= 1.0e-12,
            "keeps_published_h": True,
        }
    if policy == "integer_steps_plus_final_partial_step":
        steps = int(math.floor(exact_steps + 1.0e-14))
        elapsed = steps * nominal_h
        final_h = max(0.0, t_final - elapsed)
        return {
            "steps": steps,
            "h_effective": nominal_h,
            "final_partial_h": final_h,
            "terminal_time": t_final,
            "keeps_exact_T": True,
            "keeps_published_h": True,
        }
    raise ValueError(f"unsupported endpoint policy: {policy}")


def reference_at_time(
    *,
    theta0: float,
    omega0: float,
    t_eval: float,
    reference_h: float,
    frictional: bool,
    axis: str,
) -> Any:
    steps = int(math.floor(t_eval / reference_h + 1.0e-14))
    final_h = max(0.0, t_eval - steps * reference_h)
    state, _ = integrate_steps(
        method="rk4_reference",
        theta0=theta0,
        omega0=omega0,
        h=reference_h,
        steps=steps,
        final_h=final_h,
        frictional=frictional,
        axis=axis,
    )
    return state


def finite_spread(values: list[float | None]) -> float | None:
    finite = [float(value) for value in values if value is not None and math.isfinite(float(value))]
    if not finite:
        return None
    return max(finite) - min(finite)


def main() -> None:
    t_final = 10.0
    nominal_h_values = [0.012, 0.006, 0.003]
    reference_h = 0.0001
    axis = "z"
    theta0 = 0.0
    omega0 = 0.0
    frictional = False
    policies = [
        "adjust_h_to_hit_T_exactly",
        "algorithm_literal_fixed_h_until_tn_ge_tfinal",
        "floor_horizon",
        "integer_steps_plus_final_partial_step",
    ]
    method_specs = active_tfe_b2_source_method_specs()

    raw_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []
    references: dict[float, Any] = {}

    for policy in policies:
        for method in method_specs:
            coord_errors: list[float] = []
            vel_errors: list[float] = []
            frob_errors: list[float] = []
            effective_hs: list[float] = []
            terminal_times: list[float] = []
            residuals: list[float] = []
            iterations = 0.0
            for nominal_h in nominal_h_values:
                step_policy = endpoint_policy_steps(policy, t_final=t_final, nominal_h=nominal_h)
                terminal_time = float(step_policy["terminal_time"])
                if terminal_time not in references:
                    references[terminal_time] = reference_at_time(
                        theta0=theta0,
                        omega0=omega0,
                        t_eval=terminal_time,
                        reference_h=reference_h,
                        frictional=frictional,
                        axis=axis,
                    )
                candidate, diagnostics = integrate_steps(
                    method=str(method["source_method"]),
                    theta0=theta0,
                    omega0=omega0,
                    h=float(step_policy["h_effective"]),
                    steps=int(step_policy["steps"]),
                    final_h=float(step_policy["final_partial_h"]),
                    frictional=frictional,
                    axis=axis,
                )
                metrics = source_error_metrics(references[terminal_time], candidate, axis=axis)
                coord_errors.append(float(metrics["coordinate_error_q"]))
                vel_errors.append(float(metrics["velocity_error_v"]))
                frob_errors.append(float(metrics["frobenius_error_norm_eta"]))
                effective_hs.append(float(step_policy["h_effective"]))
                terminal_times.append(terminal_time)
                residuals.append(float(diagnostics["max_residual_norm"]))
                iterations += float(diagnostics["total_newton_iterations"])
                raw_rows.append(
                    {
                        "policy": policy,
                        "paper_method": method["paper_method"],
                        "source_method": method["source_method"],
                        "expected_order": method["expected_order"],
                        "nominal_h": nominal_h,
                        "effective_h": float(step_policy["h_effective"]),
                        "steps": int(step_policy["steps"]),
                        "final_partial_h": float(step_policy["final_partial_h"]),
                        "terminal_time": terminal_time,
                        "terminal_time_offset_from_T": terminal_time - t_final,
                        "coordinate_error_q": float(metrics["coordinate_error_q"]),
                        "velocity_error_v": float(metrics["velocity_error_v"]),
                        "frobenius_error_norm_eta": float(metrics["frobenius_error_norm_eta"]),
                        "max_residual_norm": float(diagnostics["max_residual_norm"]),
                        "total_newton_iterations": float(diagnostics["total_newton_iterations"]),
                    }
                )
            nominal_orders_q = pairwise_orders(coord_errors, nominal_h_values)
            nominal_orders_v = pairwise_orders(vel_errors, nominal_h_values)
            effective_orders_q = pairwise_orders(coord_errors, effective_hs)
            effective_orders_v = pairwise_orders(vel_errors, effective_hs)
            summary_rows.append(
                {
                    "policy": policy,
                    "paper_method": method["paper_method"],
                    "source_method": method["source_method"],
                    "expected_order": method["expected_order"],
                    "nominal_h": nominal_h_values,
                    "effective_h": effective_hs,
                    "terminal_times": terminal_times,
                    "coordinate_pairwise_orders_nominal_h": nominal_orders_q,
                    "velocity_pairwise_orders_nominal_h": nominal_orders_v,
                    "coordinate_pairwise_orders_effective_h": effective_orders_q,
                    "velocity_pairwise_orders_effective_h": effective_orders_v,
                    "finest_coordinate_error": coord_errors[-1],
                    "finest_velocity_error": vel_errors[-1],
                    "max_terminal_time_offset_abs": max(abs(item - t_final) for item in terminal_times),
                    "max_residual_norm": max(residuals),
                    "total_newton_iterations": iterations,
                    "source_policy_row_completed": False,
                }
            )

    by_method: dict[str, dict[str, Any]] = {}
    for method in method_specs:
        method_name = str(method["paper_method"])
        rows = [row for row in summary_rows if row["paper_method"] == method_name]
        velocity_orders = [
            order for row in rows for order in row["velocity_pairwise_orders_nominal_h"] if order is not None
        ]
        finest_errors = [float(row["finest_velocity_error"]) for row in rows if row["finest_velocity_error"] > 0.0]
        by_method[method_name] = {
            "velocity_order_spread_across_policies": finite_spread(velocity_orders),
            "finest_velocity_error_ratio_across_policies": (
                max(finest_errors) / min(finest_errors) if finest_errors else None
            ),
            "policy_count": len(rows),
        }

    result = {
        "schema": "tfe-endpoint-policy-sensitivity-audit-v1",
        "status": "diagnostic_endpoint_policy_sensitivity_not_source_policy",
        "read_only": True,
        "submission_ready": False,
        "source_policy_rows_completed": 0,
        "external_superiority_claim_allowed": False,
        "source_policy_runner_equivalent": False,
        "case_id": "frictionless_pendulum_active_b2_planar_candidate",
        "t_final": t_final,
        "reference_h": reference_h,
        "nominal_h": nominal_h_values,
        "endpoint_policies": policies,
        "method_count": len(method_specs),
        "policy_count": len(policies),
        "summary_row_count": len(summary_rows),
        "raw_row_count": len(raw_rows),
        "summary_rows": summary_rows,
        "raw_rows": raw_rows,
        "sensitivity_by_method": by_method,
        "interpretation": (
            "Endpoint-policy choices can be measured with the current planar candidate runner, but this "
            "does not resolve the source paper's error-sampling convention or prove source-policy equivalence."
        ),
        "execution_policy": {
            "default_1e_4_campaign_invoked": False,
            "run_v047_invoked": False,
            "source_policy_rows_completed": 0,
        },
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")

    fieldnames = [
        "policy",
        "paper_method",
        "source_method",
        "expected_order",
        "nominal_h",
        "effective_h",
        "steps",
        "final_partial_h",
        "terminal_time",
        "terminal_time_offset_from_T",
        "coordinate_error_q",
        "velocity_error_v",
        "frobenius_error_norm_eta",
        "max_residual_norm",
        "total_newton_iterations",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(raw_rows)

    lines = [
        "# TFE Endpoint-Policy Sensitivity Audit",
        "",
        "Status: **diagnostic endpoint-policy sensitivity; not source-policy closure**.",
        "",
        f"- Source-policy rows completed: `{result['source_policy_rows_completed']}`.",
        f"- Methods/policies/raw rows: `{result['method_count']}/{result['policy_count']}/{result['raw_row_count']}`.",
        f"- Nominal h values: `{result['nominal_h']}`.",
        f"- External superiority claim allowed: `{result['external_superiority_claim_allowed']}`.",
        "",
        "## Method Sensitivity Summary",
        "",
        "| method | velocity-order spread | finest velocity-error ratio |",
        "|---|---:|---:|",
    ]
    for method_name, sensitivity in by_method.items():
        lines.append(
            f"| `{method_name}` | `{sensitivity['velocity_order_spread_across_policies']:.6g}` | "
            f"`{sensitivity['finest_velocity_error_ratio_across_policies']:.6g}` |"
        )
    lines.extend(
        [
            "",
            "## Policy Rows",
            "",
            "| policy | method | terminal times | velocity orders | finest velocity error |",
            "|---|---|---|---|---:|",
        ]
    )
    for row in summary_rows:
        lines.append(
            f"| `{row['policy']}` | `{row['paper_method']}` | `{[round(item, 12) for item in row['terminal_times']]}` | "
            f"`{row['velocity_pairwise_orders_nominal_h']}` | `{row['finest_velocity_error']:.6e}` |"
        )
    lines.extend(["", result["interpretation"]])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("tfe_endpoint_policy_sensitivity_audit=written")
    print(f"summary_rows={result['summary_row_count']}")
    print(f"raw_rows={result['raw_row_count']}")
    print("source_policy_rows_completed=0")
    print("external_superiority_claim_allowed=False")


if __name__ == "__main__":
    main()
