#!/usr/bin/env python3
"""Numerical counterpart of the exact stage identity (Lemma exact-stage-identity).

For the smooth cylindrical-chain case and the accepted step sizes, every stage solve is run to a
tight Newton tolerance with the accepted residual functions imported from the v047 pipeline.
The converged 132-dimensional stage vector is then read in the reduced joint-coordinate chart
(sliding coordinate s_j = n_j . d_j, twist angle theta_j, and their rates), and the reduced
three-stage Gauss collocation defects

    s_j(Z_i) - s_j(x_n) - h sum_k A_ik sdot_j(Z_k),   (and the same for sdot, theta, thetadot)

are evaluated.  The lemma says these vanish exactly at any root of the implemented rows; here they
must be at roundoff.  Two auxiliary identities from the proof are checked as well: the relative
displacement/velocity/acceleration are parallel to the fixed direction n_j, and the implemented
sliding collocation row equals the reduced defect times n_j . a_j(q_i).

This script imports the residual functions and runs at most 14 Newton stage solves on the
accepted T = 0.08 horizon.  It never invokes run_v047.py's main campaign and does not use the
default 1e-4 step size.
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
OUT_JSON = PAPER / "EXACT_STAGE_IDENTITY_NUMERICAL_CHECK.json"
OUT_CSV = PAPER / "EXACT_STAGE_IDENTITY_NUMERICAL_CHECK.csv"
OUT_MD = PAPER / "EXACT_STAGE_IDENTITY_NUMERICAL_CHECK.md"

if str(PIPELINE) not in sys.path:
    sys.path.insert(0, str(PIPELINE))

import run_v047 as v047  # noqa: E402

H_VALUES = [0.04, 0.02, 0.01]
T_FINAL = 0.08
NEWTON_TOL = 1.0e-13
MAX_NEWTON_ITERS = 60
THRESHOLD = 1.0e-10


def newton_stage_solve(state: Any, h: float, params: Any) -> tuple[np.ndarray, tuple, dict[str, Any]]:
    x = v047.stage_guess(state, h, params)
    args = v047.build_args(state, h, params)
    final_residual = math.inf
    iterations = 0
    for iteration in range(1, MAX_NEWTON_ITERS + 1):
        x_jax = jnp.asarray(x, dtype=jnp.float64)
        res = np.asarray(v047.R_VALUE(x_jax, *args), dtype=float)
        final_residual = float(np.linalg.norm(res))
        iterations = iteration
        if final_residual <= NEWTON_TOL:
            break
        jac = np.asarray(v047.R_JAC(x_jax, *args), dtype=float)
        x = x + np.linalg.solve(jac, -res)
    final_residual = float(np.linalg.norm(np.asarray(v047.R_VALUE(jnp.asarray(x, dtype=jnp.float64), *args), dtype=float)))
    return x, args, {"newton_iterations": iterations, "final_residual_norm": final_residual,
                     "converged": final_residual <= NEWTON_TOL}


def stage_kinematics(x: np.ndarray, state: Any, params: Any) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Reproduce the kinematic preamble of residual_cylindrical_chain on a converged stage vector."""
    dtype = jnp.float64
    r0 = jnp.asarray(state.r, dtype=dtype)
    p0 = jnp.asarray(state.p, dtype=dtype)
    v0 = jnp.asarray(state.v, dtype=dtype)
    w0 = jnp.asarray(state.w, dtype=dtype)
    params_arrays = tuple(jnp.asarray(a, dtype=dtype) for a in (
        params.s_prev, params.s_next, params.axis_prev, params.axis_next, params.twist_prev,
        params.twist_next, params.ground_axis, params.ground_twist, params.joint_basis))
    stages = v047.unpack_stages(jnp.asarray(x, dtype=dtype))
    kins = []
    for st in stages:
        p = [v047.compose_right_quat_jax_safe(p0[i], st["u"][i]) for i in range(v047.N_BODIES)]
        R = [v047.qp.quat_to_rot_jax(p[i]) for i in range(v047.N_BODIES)]
        kins.append(v047.joint_kinematics_jax(st, R, params_arrays, dtype))
    R0 = [v047.qp.quat_to_rot_jax(p0[i]) for i in range(v047.N_BODIES)]
    state_st = {"r": r0, "v": v0, "w": w0, "a": jnp.zeros_like(v0), "alpha": jnp.zeros_like(w0)}
    kin0 = v047.joint_kinematics_jax(state_st, R0, params_arrays, dtype)
    return kins, kin0


def fixed_normals(params: Any) -> list[np.ndarray]:
    normals = []
    for j in range(v047.N_JOINTS):
        b0 = np.asarray(params.joint_basis[j, 0], dtype=float)
        b1 = np.asarray(params.joint_basis[j, 1], dtype=float)
        n = np.cross(b0, b1)
        n = n / np.linalg.norm(n)
        normals.append(n)
    return normals


def collocation_defects(kins: list[dict[str, Any]], kin0: dict[str, Any], normals: list[np.ndarray],
                        h: float, A: np.ndarray) -> dict[str, float]:
    f = lambda a: np.asarray(a, dtype=float)  # noqa: E731
    out = {"s": 0.0, "sdot": 0.0, "theta": 0.0, "thetadot": 0.0, "perp_point": 0.0, "perp_vel": 0.0,
           "perp_acc": 0.0, "factorization": 0.0, "min_n_dot_axis": math.inf}
    for j in range(v047.N_JOINTS):
        n = normals[j]
        s = [float(f(k["rel_point"][j]) @ n) for k in kins]
        sd = [float(f(k["rel_vel"][j]) @ n) for k in kins]
        sdd = [float(f(k["rel_acc"][j]) @ n) for k in kins]
        th = [float(f(k["twist_angle"][j])) for k in kins]
        thd = [float(f(k["rel_spin_vel"][j])) for k in kins]
        thdd = [float(f(k["rel_spin_acc"][j])) for k in kins]
        s0 = float(f(kin0["rel_point"][j]) @ n)
        sd0 = float(f(kin0["rel_vel"][j]) @ n)
        th0 = float(f(kin0["twist_angle"][j]))
        thd0 = float(f(kin0["rel_spin_vel"][j]))
        for i in range(v047.N_STAGES):
            r_s = s[i] - s0 - h * sum(A[i, k] * sd[k] for k in range(v047.N_STAGES))
            r_sd = sd[i] - sd0 - h * sum(A[i, k] * sdd[k] for k in range(v047.N_STAGES))
            r_th = th[i] - th0 - h * sum(A[i, k] * thd[k] for k in range(v047.N_STAGES))
            r_thd = thd[i] - thd0 - h * sum(A[i, k] * thdd[k] for k in range(v047.N_STAGES))
            out["s"] = max(out["s"], abs(r_s))
            out["sdot"] = max(out["sdot"], abs(r_sd))
            out["theta"] = max(out["theta"], abs(r_th))
            out["thetadot"] = max(out["thetadot"], abs(r_thd))
            # parallelism to n
            for key, name in (("rel_point", "perp_point"), ("rel_vel", "perp_vel"), ("rel_acc", "perp_acc")):
                vec = f(kins[i][key][j])
                perp = vec - (vec @ n) * n
                out[name] = max(out[name], float(np.linalg.norm(perp)))
            # implemented sliding row equals reduced defect times n . axis_i
            axis = f(kins[i]["parent_axis"][j])
            impl_row = float((f(kins[i]["rel_point"][j]) - f(kin0["rel_point"][j])
                              - h * sum(A[i, k] * f(kins[k]["rel_vel"][j]) for k in range(v047.N_STAGES))) @ axis)
            out["factorization"] = max(out["factorization"], abs(impl_row - r_s * float(n @ axis)))
            out["min_n_dot_axis"] = min(out["min_n_dot_axis"], abs(float(n @ axis)))
    return out


def main() -> int:
    params = v047.make_params(v047.CASES["cylindrical_smooth"])
    normals = fixed_normals(params)
    _, A, _ = v047.qp.gauss_legendre_coefficients(v047.N_STAGES)
    A = np.asarray(A, dtype=float)
    rows: list[dict[str, Any]] = []
    started = time.perf_counter()
    for h in H_VALUES:
        state = v047.project_endpoint_velocity(v047.initial_state(params), params)
        n_steps = int(round(T_FINAL / h))
        agg = {"s": 0.0, "sdot": 0.0, "theta": 0.0, "thetadot": 0.0, "perp_point": 0.0, "perp_vel": 0.0,
               "perp_acc": 0.0, "factorization": 0.0, "min_n_dot_axis": math.inf}
        max_res = 0.0
        iters = 0
        all_conv = True
        for _ in range(n_steps):
            x, _args, diag = newton_stage_solve(state, h, params)
            all_conv = all_conv and bool(diag["converged"])
            max_res = max(max_res, diag["final_residual_norm"])
            iters += int(diag["newton_iterations"])
            kins, kin0 = stage_kinematics(x, state, params)
            d = collocation_defects(kins, kin0, normals, h, A)
            for key in agg:
                agg[key] = min(agg[key], d[key]) if key == "min_n_dot_axis" else max(agg[key], d[key])
            stages = v047.unpack_stages(jnp.asarray(x, dtype=jnp.float64))
            state = v047.next_state_from_stages(state, h, stages, params, project_velocity=True)
        row = {"h": h, "steps": n_steps, "newton_tolerance": NEWTON_TOL, "all_steps_converged": all_conv,
               "total_newton_iterations": iters, "max_final_residual_norm": max_res,
               "max_reduced_collocation_defect_s": agg["s"], "max_reduced_collocation_defect_sdot": agg["sdot"],
               "max_reduced_collocation_defect_theta": agg["theta"],
               "max_reduced_collocation_defect_thetadot": agg["thetadot"],
               "max_reduced_collocation_defect": max(agg["s"], agg["sdot"], agg["theta"], agg["thetadot"]),
               "max_perpendicular_rel_point": agg["perp_point"], "max_perpendicular_rel_vel": agg["perp_vel"],
               "max_perpendicular_rel_acc": agg["perp_acc"], "max_factorization_mismatch": agg["factorization"],
               "min_abs_n_dot_axis": agg["min_n_dot_axis"]}
        row["identity_within_threshold"] = bool(
            all_conv and row["max_reduced_collocation_defect"] <= THRESHOLD
            and max(agg["perp_point"], agg["perp_vel"], agg["perp_acc"], agg["factorization"]) <= THRESHOLD
            and agg["min_n_dot_axis"] > 0.1)
        rows.append(row)
        print(f"h={h:g} steps={n_steps} iters={iters} max_res={max_res:.3e} "
              f"max_reduced_defect={row['max_reduced_collocation_defect']:.3e} "
              f"perp={max(agg['perp_point'], agg['perp_vel'], agg['perp_acc']):.3e} "
              f"factorization={agg['factorization']:.3e} ok={row['identity_within_threshold']}")

    all_ok = all(r["identity_within_threshold"] for r in rows)
    payload = {
        "schema": "exact-stage-identity-numerical-check-v1",
        "status": "reduced_collocation_recovered_at_roundoff" if all_ok else "identity_check_failed",
        "case": "cylindrical_smooth",
        "h_values": H_VALUES,
        "t_final": T_FINAL,
        "newton_tolerance": NEWTON_TOL,
        "threshold": THRESHOLD,
        "rows_ok": f"{sum(r['identity_within_threshold'] for r in rows)}/{len(rows)}",
        "all_rows_ok": all_ok,
        "max_reduced_collocation_defect_overall": max(r["max_reduced_collocation_defect"] for r in rows),
        "run_v047_invoked": False,
        "default_1e-4_required": False,
        "heavy_numerical_run_invoked": False,
        "runtime_sec": time.perf_counter() - started,
        "lemma": "lem:exact-stage-identity",
        "lean_theorem": "IntegratorOrderProof.FullVA.Transition.nondynamic_rows_iff",
        "rows": rows,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    md = [
        "# Exact Stage Identity Numerical Check",
        "",
        f"Status: `{payload['status']}`.",
        "",
        "Converged FullVA stage vectors of the smooth cylindrical chain are read in the reduced",
        "joint-coordinate chart; the reduced three-stage Gauss collocation defects must be at roundoff",
        "(Lemma exact-stage-identity, Lean `FullVA.Transition.nondynamic_rows_iff`).",
        "",
        f"- Case: `{payload['case']}`; h values: `{H_VALUES}`; t_final: `{T_FINAL}`; Newton tolerance: `{NEWTON_TOL}`.",
        f"- Rows ok: `{payload['rows_ok']}`; threshold: `{THRESHOLD}`.",
        f"- Max reduced collocation defect overall: `{payload['max_reduced_collocation_defect_overall']:.3e}`.",
        "- run_v047_invoked: `False`; default_1e-4_required: `False`.",
        "",
        "| h | steps | Newton iters | max residual | max reduced defect (s, ṡ, θ, θ̇) | max ⊥ component | factorization mismatch | ok |",
        "|---:|---:|---:|---:|---|---:|---:|---|",
    ]
    for r in rows:
        md.append(
            f"| {r['h']:g} | {r['steps']} | {r['total_newton_iterations']} | {r['max_final_residual_norm']:.3e} | "
            f"{r['max_reduced_collocation_defect_s']:.2e}, {r['max_reduced_collocation_defect_sdot']:.2e}, "
            f"{r['max_reduced_collocation_defect_theta']:.2e}, {r['max_reduced_collocation_defect_thetadot']:.2e} | "
            f"{max(r['max_perpendicular_rel_point'], r['max_perpendicular_rel_vel'], r['max_perpendicular_rel_acc']):.2e} | "
            f"{r['max_factorization_mismatch']:.2e} | {r['identity_within_threshold']} |")
    md += ["", "Validator: `validate_exact_stage_identity_numerical_check.py`.", ""]
    OUT_MD.write_text("\n".join(md), encoding="utf-8")
    print(f"exact_stage_identity_numerical_check={payload['status']}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
