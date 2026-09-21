#!/usr/bin/env python3
"""Run a short scaled-tolerance trajectory probe for the proof contract.

This script imports the accepted v047 residual functions and advances a short
smooth trajectory with the nonlinear residual stopping target
eta_h = c_eta h^7 at every step. It is solver-policy diagnostic support only: it does not
invoke run_v047.py and it does not close the optional primitive/global dynamic
symbolic lane.
"""

from __future__ import annotations

import csv
import json
import math
import sys
import time
from pathlib import Path
from typing import Any

import jax.numpy as jnp
import numpy as np


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
PIPELINE = ROOT.parent / "numerics" / "v047_cylindrical_chain_pipeline"
OUT_JSON = PAPER / "PROOF_SOLVER_SCALED_TOLERANCE_TRAJECTORY_PROBE.json"
OUT_CSV = PAPER / "PROOF_SOLVER_SCALED_TOLERANCE_TRAJECTORY_PROBE.csv"
OUT_MD = PAPER / "PROOF_SOLVER_SCALED_TOLERANCE_TRAJECTORY_PROBE.md"

if str(PIPELINE) not in sys.path:
    sys.path.insert(0, str(PIPELINE))

import run_v047 as v047  # noqa: E402


H_VALUES = [0.04, 0.02, 0.01, 0.005]
T_FINAL = 0.08
C_ETA = 1.0e4
MAX_NEWTON_ITERS = 80


def solve_scaled_step(state: Any, h: float, c_eta: float, params: Any) -> tuple[Any, dict[str, Any]]:
    x = v047.stage_guess(state, h, params)
    args = v047.build_args(state, h, params)
    eta_target = c_eta * math.pow(h, 7)
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
        "status": status,
        "newton_iterations": iterations,
        "eta_target": eta_target,
        "final_residual_norm": final_residual_norm,
        "final_residual_over_h7": final_residual_norm / math.pow(h, 7),
        "target_over_h7": c_eta,
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


def run_trajectory(h: float, c_eta: float, t_final: float) -> dict[str, Any]:
    params = v047.make_params(v047.CASES["cylindrical_smooth"])
    state = v047.project_endpoint_velocity(v047.initial_state(params), params)
    n_steps = int(round(t_final / h))
    if abs(n_steps * h - t_final) > 1.0e-14:
        raise ValueError(f"t_final={t_final} is not an integer multiple of h={h}")

    step_rows: list[dict[str, Any]] = []
    started = time.perf_counter()
    for step_index in range(n_steps):
        state, step_diag = solve_scaled_step(state, h, c_eta, params)
        step_diag["step_index"] = step_index
        step_rows.append(step_diag)

    max_residual_over_h7 = max(row["final_residual_over_h7"] for row in step_rows)
    max_endpoint_constraint = max(row["max_endpoint_constraint_norm"] for row in step_rows)
    max_endpoint_velocity = max(row["max_endpoint_velocity_constraint_norm"] for row in step_rows)
    total_newton_iterations = sum(int(row["newton_iterations"]) for row in step_rows)
    all_steps_ok = all(
        row["status"] == "ok" and row["final_residual_over_h7"] <= c_eta for row in step_rows
    )
    return {
        "case": "cylindrical_smooth",
        "h": h,
        "t_final": t_final,
        "steps": n_steps,
        "c_eta": c_eta,
        "eta_target": c_eta * math.pow(h, 7),
        "status": "ok" if all_steps_ok else "failed",
        "all_steps_ok": all_steps_ok,
        "total_newton_iterations": total_newton_iterations,
        "max_step_newton_iterations": max(int(row["newton_iterations"]) for row in step_rows),
        "max_final_residual_norm": max(row["final_residual_norm"] for row in step_rows),
        "max_final_residual_over_h7": max_residual_over_h7,
        "target_over_h7": c_eta,
        "max_linear_residual_norm": max(row["max_linear_residual_norm"] for row in step_rows),
        "max_endpoint_constraint_norm": max_endpoint_constraint,
        "max_endpoint_velocity_constraint_norm": max_endpoint_velocity,
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


def write_csv(rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "case",
        "h",
        "t_final",
        "steps",
        "c_eta",
        "eta_target",
        "status",
        "all_steps_ok",
        "total_newton_iterations",
        "max_step_newton_iterations",
        "max_final_residual_norm",
        "max_final_residual_over_h7",
        "target_over_h7",
        "max_linear_residual_norm",
        "max_endpoint_constraint_norm",
        "max_endpoint_velocity_constraint_norm",
        "max_stage_position_acceleration_constraint_norm",
        "max_stage_orientation_acceleration_constraint_norm",
        "min_final_jacobian_rank",
        "max_final_jacobian_condition",
        "runtime_sec",
    ]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key) for key in fieldnames})


def write_md(payload: dict[str, Any]) -> None:
    lines = [
        "# Proof Solver Scaled-Tolerance Trajectory Probe",
        "",
        f"Status: `{payload['status']}`.",
        "",
        "This finite short-trajectory probe imports the accepted v047 residual",
        "functions and applies `eta_h = c_eta h^7` at every smooth trajectory",
        "step. It does not invoke `run_v047.py`, does not run a default `1e-4`",
        "campaign, and does not close the optional primitive/global dynamic",
        "symbolic lane; active direct PC2 remains closed by the separate",
        "D5 direct-substitution route.",
        "",
        f"- Probe schema: `{payload['schema']}`.",
        f"- Case: `{payload['case']}`.",
        f"- h values: `{payload['h_values']}`.",
        f"- t_final: `{payload['t_final']}`.",
        f"- c_eta: `{payload['c_eta']}`.",
        f"- Rows ok: `{payload['ok_row_count']}/{payload['row_count']}`.",
        f"- Total trajectory steps checked: `{payload['total_steps_checked']}`.",
        f"- Max final residual / h^7: `{payload['max_final_residual_over_h7']:.16e}`.",
        f"- Scaled trajectory policy exercised: `{payload['scaled_trajectory_policy_exercised']}`.",
        f"- Theorem-level solver proof closed: `{payload['theorem_level_solver_proof_closed']}`.",
        f"- eta_h_O_h7_solver_policy_evidence: `{payload['eta_h_O_h7_solver_policy_evidence']}`.",
        f"- default_1e-4_required: `{payload['execution_policy']['default_1e-4_required']}`.",
        f"- run_v047_invoked: `{payload['execution_policy']['run_v047_invoked']}`.",
        "",
        "| h | steps | eta target | max residual | max residual / h^7 | Newton iters | status |",
        "|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in payload["rows"]:
        lines.append(
            "| "
            f"{row['h']:.6g} | "
            f"{row['steps']} | "
            f"{row['eta_target']:.6e} | "
            f"{row['max_final_residual_norm']:.6e} | "
            f"{row['max_final_residual_over_h7']:.6e} | "
            f"{row['total_newton_iterations']} | "
            f"{row['status']} |"
        )
    lines.extend(
        [
            "",
            "Interpretation: this is stronger than the one-step finite probe because",
            "the scaled stopping rule is exercised over a short trajectory. It is",
            "still finite solver-policy diagnostic support, not a theorem-level scaled",
            "tolerance sweep over every reported trajectory and not a substitute",
            "for the optional primitive/global dynamic symbolic lane.",
            "",
            "Validator: `validate_proof_solver_scaled_tolerance_trajectory_probe.py`.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    rows = [run_trajectory(h, C_ETA, T_FINAL) for h in H_VALUES]
    ok_rows = [row for row in rows if row["status"] == "ok" and row["max_final_residual_over_h7"] <= C_ETA]
    payload = {
        "schema": "proof-solver-scaled-tolerance-trajectory-probe-v1",
        "status": "finite_scaled_tolerance_trajectory_probe_recorded_not_theorem_closure",
        "case": "cylindrical_smooth",
        "accepted_method": "Gauss6/FullVA",
        "row_count": len(rows),
        "ok_row_count": len(ok_rows),
        "total_steps_checked": sum(row["steps"] for row in rows),
        "h_values": H_VALUES,
        "t_final": T_FINAL,
        "c_eta": C_ETA,
        "max_final_residual_over_h7": max(row["max_final_residual_over_h7"] for row in rows),
        "scaled_trajectory_policy_exercised": len(ok_rows) == len(rows),
        "theorem_level_solver_proof_closed": False,
        "eta_h_O_h7_solver_policy_evidence": False,
        "dynamic_symbolic_oracle_complete": False,
        "stage_residual_O_h7_implementation_defect_proved": False,
        "submission_ready": False,
        "execution_policy": {
            "read_only_probe": False,
            "imports_accepted_residual_functions": True,
            "heavy_numerical_run_invoked": False,
            "default_1e-4_required": False,
            "run_v047_invoked": False,
        },
        "rows": rows,
        "forbidden_claims": [
            "theorem_level_solver_proof_closed_true",
            "eta_h_O_h7_solver_policy_evidence_true",
            "dynamic_symbolic_oracle_complete_true",
            "stage_residual_O_h7_implementation_defect_proved_true",
            "submission_ready_true",
            "external_superiority_claim_true",
        ],
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(rows)
    write_md(payload)
    print("proof_solver_scaled_tolerance_trajectory_probe=PASS")
    print(f"rows_ok={len(ok_rows)}/{len(rows)}")
    print(f"total_steps_checked={payload['total_steps_checked']}")
    print(f"max_final_residual_over_h7={payload['max_final_residual_over_h7']:.6e}")
    print("theorem_level_solver_proof_closed=False")
    print("eta_h_O_h7_solver_policy_evidence=False")
    print("default_1e-4=False")
    print("run_v047_invoked=False")
    return 0 if len(ok_rows) == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
