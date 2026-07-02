#!/usr/bin/env python3
"""Run a finite Newton-tolerance regime sweep for the v047 proof contract.

The sweep compares three smooth short-trajectory stopping policies requested
by the proof review: fixed absolute tolerance, ``c h^7``, and ``c h^8``.  It
imports the accepted v047 residual functions and never invokes ``run_v047.py``.
The result is finite solver-policy diagnostic support only, not an asymptotic theorem
closure and not a closure of the optional primitive/global dynamic symbolic lane.
"""

from __future__ import annotations

import csv
import json
import math
import sys
import time
from pathlib import Path
from typing import Any, Callable

import jax.numpy as jnp
import numpy as np


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
PIPELINE = ROOT / "v047_cylindrical_chain_pipeline"
OUT_JSON = PAPER / "PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.json"
OUT_CSV = PAPER / "PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.csv"
OUT_MD = PAPER / "PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.md"

if str(PIPELINE) not in sys.path:
    sys.path.insert(0, str(PIPELINE))

import run_v047 as v047  # noqa: E402


H_VALUES = [0.04, 0.02, 0.01, 0.005]
T_FINAL = 0.08
REFERENCE_H = 0.0025
REFERENCE_TOL = 1.0e-13
MAX_NEWTON_ITERS = 100
POLICIES = [
    {
        "name": "fixed_1e-10",
        "description": "fixed absolute residual target 1e-10",
        "target_kind": "fixed",
        "constant": 1.0e-10,
        "exponent": 0,
    },
    {
        "name": "scaled_h7_c1e4",
        "description": "scaled residual target c h^7 with c=1e4",
        "target_kind": "scaled_h7",
        "constant": 1.0e4,
        "exponent": 7,
    },
    {
        "name": "scaled_h8_c1e6",
        "description": "scaled residual target c h^8 with c=1e6",
        "target_kind": "scaled_h8",
        "constant": 1.0e6,
        "exponent": 8,
    },
]


def tolerance_target(policy: dict[str, Any], h: float) -> float:
    exponent = int(policy["exponent"])
    if exponent == 0:
        return float(policy["constant"])
    return float(policy["constant"]) * math.pow(h, exponent)


def solve_step(
    state: Any,
    h: float,
    params: Any,
    eta_target: float,
    policy_name: str,
) -> tuple[Any, dict[str, Any]]:
    x = v047.stage_guess(state, h, params)
    args = v047.build_args(state, h, params)
    started_all = time.perf_counter()
    residual_norms: list[float] = []
    linear_residuals: list[float] = []
    total_residual_eval_sec = 0.0
    total_jacobian_eval_sec = 0.0
    total_linear_solve_sec = 0.0
    final_delta_norm = 0.0
    final_residual_norm = math.inf
    status = "failed"
    iterations = 0

    for iteration in range(1, MAX_NEWTON_ITERS + 1):
        x_jax = jnp.asarray(x, dtype=jnp.float64)
        started = time.perf_counter()
        res = np.asarray(v047.R_VALUE(x_jax, *args), dtype=float)
        total_residual_eval_sec += time.perf_counter() - started
        final_residual_norm = float(np.linalg.norm(res))
        residual_norms.append(final_residual_norm)
        iterations = iteration
        if final_residual_norm <= eta_target:
            status = "ok"
            break

        started = time.perf_counter()
        jac = np.asarray(v047.R_JAC(x_jax, *args), dtype=float)
        total_jacobian_eval_sec += time.perf_counter() - started
        started = time.perf_counter()
        delta = np.linalg.solve(jac, -res)
        total_linear_solve_sec += time.perf_counter() - started
        linear_residuals.append(float(np.linalg.norm(jac @ delta + res)))
        final_delta_norm = float(np.linalg.norm(delta))
        x = x + delta

    final_res = np.asarray(v047.R_VALUE(jnp.asarray(x, dtype=jnp.float64), *args), dtype=float)
    final_residual_norm = float(np.linalg.norm(final_res))
    if final_residual_norm <= eta_target:
        status = "ok"

    stages = v047.unpack_stages(x)
    next_state = v047.next_state_from_stages(state, h, stages, params, project_velocity=True)
    endpoint_con, endpoint_vel = v047.constraint_parts_np(next_state, params, h)
    stage_pos_acc, stage_rot_acc = v047.stage_acceleration_parts(state, stages, params)
    jac_final = np.asarray(v047.R_JAC(jnp.asarray(x, dtype=jnp.float64), *args), dtype=float)

    return next_state, {
        "policy": policy_name,
        "status": status,
        "newton_iterations": iterations,
        "eta_target": eta_target,
        "final_residual_norm": final_residual_norm,
        "final_residual_over_h7": final_residual_norm / math.pow(h, 7),
        "final_residual_over_h8": final_residual_norm / math.pow(h, 8),
        "max_linear_residual_norm": max(linear_residuals) if linear_residuals else 0.0,
        "final_delta_norm": final_delta_norm,
        "max_endpoint_constraint_norm": float(np.linalg.norm(endpoint_con)),
        "max_endpoint_velocity_constraint_norm": float(np.linalg.norm(endpoint_vel)),
        "max_stage_position_acceleration_constraint_norm": stage_pos_acc,
        "max_stage_orientation_acceleration_constraint_norm": stage_rot_acc,
        "final_jacobian_rank": int(np.linalg.matrix_rank(jac_final, tol=1.0e-10)),
        "final_jacobian_condition": float(np.linalg.cond(jac_final)),
        "runtime_sec": time.perf_counter() - started_all,
        "total_residual_eval_sec": total_residual_eval_sec,
        "total_jacobian_eval_sec": total_jacobian_eval_sec,
        "total_linear_solve_sec": total_linear_solve_sec,
        "residual_norm_sequence": residual_norms,
    }


def run_trajectory_with_target(
    h: float,
    t_final: float,
    target_fn: Callable[[float], float],
    policy_name: str,
) -> tuple[Any, dict[str, Any]]:
    params = v047.make_params(v047.CASES["cylindrical_smooth"])
    state = v047.project_endpoint_velocity(v047.initial_state(params), params)
    n_steps = int(round(t_final / h))
    if abs(n_steps * h - t_final) > 1.0e-14:
        raise ValueError(f"t_final={t_final} is not an integer multiple of h={h}")

    step_rows: list[dict[str, Any]] = []
    started = time.perf_counter()
    for step_index in range(n_steps):
        state, step_diag = solve_step(state, h, params, target_fn(h), policy_name)
        step_diag["step_index"] = step_index
        step_rows.append(step_diag)

    all_steps_ok = all(row["status"] == "ok" for row in step_rows)
    summary = {
        "case": "cylindrical_smooth",
        "policy": policy_name,
        "h": h,
        "t_final": t_final,
        "steps": n_steps,
        "eta_target": target_fn(h),
        "status": "ok" if all_steps_ok else "failed",
        "all_steps_ok": all_steps_ok,
        "total_newton_iterations": sum(int(row["newton_iterations"]) for row in step_rows),
        "max_step_newton_iterations": max(int(row["newton_iterations"]) for row in step_rows),
        "max_final_residual_norm": max(row["final_residual_norm"] for row in step_rows),
        "max_final_residual_over_h7": max(row["final_residual_over_h7"] for row in step_rows),
        "max_final_residual_over_h8": max(row["final_residual_over_h8"] for row in step_rows),
        "max_linear_residual_norm": max(row["max_linear_residual_norm"] for row in step_rows),
        "max_endpoint_constraint_norm": max(row["max_endpoint_constraint_norm"] for row in step_rows),
        "max_endpoint_velocity_constraint_norm": max(row["max_endpoint_velocity_constraint_norm"] for row in step_rows),
        "max_stage_position_acceleration_constraint_norm": max(
            row["max_stage_position_acceleration_constraint_norm"] for row in step_rows
        ),
        "max_stage_orientation_acceleration_constraint_norm": max(
            row["max_stage_orientation_acceleration_constraint_norm"] for row in step_rows
        ),
        "min_final_jacobian_rank": min(int(row["final_jacobian_rank"]) for row in step_rows),
        "max_final_jacobian_condition": max(row["final_jacobian_condition"] for row in step_rows),
        "runtime_sec": time.perf_counter() - started,
        "step_rows": step_rows,
    }
    return state, summary


def state_errors(reference: Any, state: Any) -> dict[str, float]:
    position_error, velocity_error = v047.state_error(reference, state)
    return {
        "position_error": float(position_error),
        "velocity_error": float(velocity_error),
        "orientation_error": float(v047.orientation_delta_norm(reference, state)),
        "angular_velocity_error": float(np.linalg.norm(reference.w - state.w)),
    }


def observed_order(h_values: list[float], errors: list[float]) -> float:
    usable = [(h, e) for h, e in zip(h_values, errors) if e > 0.0 and np.isfinite(e)]
    if len(usable) < 2:
        return float("nan")
    hs = np.asarray([item[0] for item in usable], dtype=float)
    es = np.asarray([item[1] for item in usable], dtype=float)
    return float(np.polyfit(np.log(hs), np.log(es), 1)[0])


def run_reference() -> tuple[Any, dict[str, Any]]:
    return run_trajectory_with_target(
        REFERENCE_H,
        T_FINAL,
        lambda _h: REFERENCE_TOL,
        "reference_fixed_1e-13",
    )


def run_policy(policy: dict[str, Any], reference: Any) -> dict[str, Any]:
    h_rows: list[dict[str, Any]] = []
    h_values = [float(item) for item in H_VALUES]
    for h in h_values:
        state, row = run_trajectory_with_target(
            h,
            T_FINAL,
            lambda h_value, item=policy: tolerance_target(item, h_value),
            str(policy["name"]),
        )
        row.update(state_errors(reference, state))
        h_rows.append(row)

    orders = {
        "position_order": observed_order(h_values, [row["position_error"] for row in h_rows]),
        "velocity_order": observed_order(h_values, [row["velocity_error"] for row in h_rows]),
        "orientation_order": observed_order(h_values, [row["orientation_error"] for row in h_rows]),
        "angular_velocity_order": observed_order(h_values, [row["angular_velocity_error"] for row in h_rows]),
    }
    return {
        "name": policy["name"],
        "description": policy["description"],
        "target_kind": policy["target_kind"],
        "constant": policy["constant"],
        "exponent": policy["exponent"],
        "row_count": len(h_rows),
        "ok_row_count": sum(1 for row in h_rows if row["status"] == "ok"),
        "total_steps_checked": sum(int(row["steps"]) for row in h_rows),
        "total_newton_iterations": sum(int(row["total_newton_iterations"]) for row in h_rows),
        "orders": orders,
        "max_final_residual_over_h7": max(row["max_final_residual_over_h7"] for row in h_rows),
        "max_final_residual_over_h8": max(row["max_final_residual_over_h8"] for row in h_rows),
        "finest_position_error": h_rows[-1]["position_error"],
        "finest_velocity_error": h_rows[-1]["velocity_error"],
        "finest_orientation_error": h_rows[-1]["orientation_error"],
        "finest_angular_velocity_error": h_rows[-1]["angular_velocity_error"],
        "rows": h_rows,
    }


def write_csv(policy_results: list[dict[str, Any]]) -> None:
    fieldnames = [
        "policy",
        "target_kind",
        "h",
        "t_final",
        "steps",
        "eta_target",
        "status",
        "total_newton_iterations",
        "max_step_newton_iterations",
        "max_final_residual_norm",
        "max_final_residual_over_h7",
        "max_final_residual_over_h8",
        "position_error",
        "velocity_error",
        "orientation_error",
        "angular_velocity_error",
        "max_endpoint_constraint_norm",
        "max_endpoint_velocity_constraint_norm",
        "min_final_jacobian_rank",
        "max_final_jacobian_condition",
        "runtime_sec",
    ]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for policy in policy_results:
            for row in policy["rows"]:
                flat = {key: row.get(key) for key in fieldnames}
                flat["target_kind"] = policy["target_kind"]
                writer.writerow(flat)


def write_md(payload: dict[str, Any]) -> None:
    lines = [
        "# Proof Solver Tolerance-Regime Sweep",
        "",
        f"Status: `{payload['status']}`.",
        "",
        "This finite smooth short-trajectory sweep compares three Newton",
        "stopping policies: fixed `1e-10`, `c h^7`, and `c h^8`. It imports the",
        "accepted v047 residual functions directly, does not invoke",
        "`run_v047.py`, and does not close the optional primitive/global dynamic",
        "symbolic lane; active direct PC2 remains closed by the separate",
        "D5 direct-substitution route.",
        "",
        f"- Schema: `{payload['schema']}`.",
        f"- Case: `{payload['case']}`.",
        f"- h values: `{payload['h_values']}`.",
        f"- t_final: `{payload['t_final']}`.",
        f"- Reference h/tolerance: `{payload['reference']['h']}` / `{payload['reference']['eta_target']}`.",
        f"- Policy count: `{payload['policy_count']}`.",
        f"- Total rows/steps checked: `{payload['total_rows_checked']}` / `{payload['total_steps_checked']}`.",
        f"- All rows converged: `{payload['all_rows_converged']}`.",
        f"- Finite tolerance regime sweep recorded: `{payload['finite_tolerance_regime_sweep_recorded']}`.",
        f"- Finite h-scaled tolerance sweep recorded: `{payload['finite_h_scaled_tolerance_sweep_recorded']}`.",
        f"- Finite h-scaled policy names: `{payload['finite_h_scaled_policy_names']}`.",
        f"- Finite h-scaled policy rows/steps: `{payload['finite_h_scaled_policy_rows']}` / `{payload['finite_h_scaled_policy_steps']}`.",
        f"- Finite h-scaled position/velocity order floor: `{payload['finite_h_scaled_position_order_floor']:.3f}` / `{payload['finite_h_scaled_velocity_order_floor']:.3f}`.",
        f"- Scaled residual bounds satisfied: `h7={payload['scaled_h7_residual_bound_satisfied']}`, `h8={payload['scaled_h8_residual_bound_satisfied']}`.",
        f"- Theorem-level scaled tolerance sweep recorded: `{payload['scaled_tolerance_sweep_recorded']}`.",
        f"- eta_h_O_h7_solver_policy_evidence: `{payload['eta_h_O_h7_solver_policy_evidence']}`.",
        f"- Theorem-level solver proof closed: `{payload['theorem_level_solver_proof_closed']}`.",
        f"- default_1e-4_required: `{payload['execution_policy']['default_1e-4_required']}`.",
        f"- run_v047_invoked: `{payload['execution_policy']['run_v047_invoked']}`.",
        "",
        "## Policy Summary",
        "",
        "| policy | target | rows | steps | pos order | vel order | orient order | omega order | max res/h^7 | max res/h^8 |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for policy in payload["policies"]:
        orders = policy["orders"]
        target = "1e-10" if policy["exponent"] == 0 else f"{policy['constant']:.1e} h^{policy['exponent']}"
        lines.append(
            "| "
            f"{policy['name']} | "
            f"{target} | "
            f"{policy['ok_row_count']}/{policy['row_count']} | "
            f"{policy['total_steps_checked']} | "
            f"{orders['position_order']:.3f} | "
            f"{orders['velocity_order']:.3f} | "
            f"{orders['orientation_order']:.3f} | "
            f"{orders['angular_velocity_order']:.3f} | "
            f"{policy['max_final_residual_over_h7']:.3e} | "
            f"{policy['max_final_residual_over_h8']:.3e} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The fixed policy is sufficient only for this finite short smooth",
            "diagnostic window, while its residual divided by `h^7` grows on",
            "refinement. The `h^7` and `h^8` policies exercise residual targets",
            "that shrink with `h`; they therefore better match the inexact-Newton",
            "theorem condition as finite diagnostics, not as theorem evidence.",
            "This finite h-scaled comparison is explicitly recorded separately",
            "from the theorem-level scaled-tolerance gate. It is still not a",
            "global solver proof over every reported trajectory, does not close",
            "P6 theorem-level solver-policy evidence, and does not close the",
            "optional primitive/global dynamic symbolic lane. The active 36-row",
            "direct D5 stage-residual certificate is closed separately.",
            "",
            "Validator: `validate_proof_solver_tolerance_regime_sweep.py`.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    reference_state, reference_summary = run_reference()
    policy_results = [run_policy(policy, reference_state) for policy in POLICIES]
    total_rows = sum(policy["row_count"] for policy in policy_results)
    total_steps = sum(policy["total_steps_checked"] for policy in policy_results)
    all_rows_converged = all(policy["ok_row_count"] == policy["row_count"] for policy in policy_results)
    scaled_policy_results = [
        policy for policy in policy_results if policy["target_kind"] in {"scaled_h7", "scaled_h8"}
    ]
    scaled_h7 = next(policy for policy in policy_results if policy["target_kind"] == "scaled_h7")
    scaled_h8 = next(policy for policy in policy_results if policy["target_kind"] == "scaled_h8")
    finite_h_scaled_position_order_floor = min(
        float(policy["orders"]["position_order"]) for policy in scaled_policy_results
    )
    finite_h_scaled_velocity_order_floor = min(
        float(policy["orders"]["velocity_order"]) for policy in scaled_policy_results
    )
    payload = {
        "schema": "proof-solver-tolerance-regime-sweep-v1",
        "status": "finite_tolerance_regime_sweep_recorded_not_theorem_closure",
        "case": "cylindrical_smooth",
        "accepted_method": "Gauss6/FullVA",
        "h_values": H_VALUES,
        "t_final": T_FINAL,
        "reference": {
            "policy": "reference_fixed_1e-13",
            "h": REFERENCE_H,
            "eta_target": REFERENCE_TOL,
            "steps": reference_summary["steps"],
            "status": reference_summary["status"],
            "max_final_residual_norm": reference_summary["max_final_residual_norm"],
            "max_final_residual_over_h7": reference_summary["max_final_residual_over_h7"],
        },
        "policy_count": len(policy_results),
        "total_rows_checked": total_rows,
        "total_steps_checked": total_steps,
        "all_rows_converged": all_rows_converged,
        "finite_tolerance_regime_sweep_recorded": True,
        "finite_h_scaled_tolerance_sweep_recorded": True,
        "finite_h_scaled_policy_names": [policy["name"] for policy in scaled_policy_results],
        "finite_h_scaled_policy_rows": sum(policy["row_count"] for policy in scaled_policy_results),
        "finite_h_scaled_policy_steps": sum(policy["total_steps_checked"] for policy in scaled_policy_results),
        "finite_h_scaled_position_order_floor": finite_h_scaled_position_order_floor,
        "finite_h_scaled_velocity_order_floor": finite_h_scaled_velocity_order_floor,
        "scaled_h7_residual_bound_satisfied": scaled_h7["max_final_residual_over_h7"] <= float(scaled_h7["constant"]),
        "scaled_h8_residual_bound_satisfied": scaled_h8["max_final_residual_over_h8"] <= float(scaled_h8["constant"]),
        "scaled_tolerance_sweep_recorded": False,
        "eta_h_O_h7_solver_policy_evidence": False,
        "fixed_tolerance_runs_are_asymptotic_proof": False,
        "theorem_level_solver_proof_closed": False,
        "dynamic_symbolic_oracle_complete": False,
        "stage_residual_O_h7_implementation_defect_proved": False,
        "submission_ready": False,
        "execution_policy": {
            "imports_accepted_residual_functions": True,
            "heavy_numerical_run_invoked": False,
            "default_1e-4_required": False,
            "run_v047_invoked": False,
        },
        "policies": policy_results,
        "forbidden_claims": [
            "theorem_level_solver_proof_closed_true",
            "eta_h_O_h7_solver_policy_evidence_true",
            "fixed_tolerance_runs_are_asymptotic_proof_true",
            "scaled_tolerance_sweep_recorded_true",
            "dynamic_symbolic_oracle_complete_true",
            "stage_residual_O_h7_implementation_defect_proved_true",
            "submission_ready_true",
            "external_superiority_claim_true",
        ],
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(policy_results)
    write_md(payload)
    print("proof_solver_tolerance_regime_sweep=PASS" if all_rows_converged else "proof_solver_tolerance_regime_sweep=FAIL")
    print(f"policies={len(policy_results)}")
    print(f"rows_checked={total_rows}")
    print(f"steps_checked={total_steps}")
    print(f"finite_tolerance_regime_sweep_recorded=True")
    print("finite_h_scaled_tolerance_sweep_recorded=True")
    print("scaled_tolerance_sweep_recorded=False")
    print("eta_h_O_h7_solver_policy_evidence=False")
    print("theorem_level_solver_proof_closed=False")
    print("default_1e-4=False")
    print("run_v047_invoked=False")
    return 0 if all_rows_converged else 1


if __name__ == "__main__":
    raise SystemExit(main())
