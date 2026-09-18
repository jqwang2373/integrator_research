#!/usr/bin/env python3
"""Numerical instantiation of the constants in Lemma p2-from-p1 and Lemma newton-envelope.

For the smooth cylindrical-chain case on the accepted horizon T = 0.08 and the reported step sizes,
every stage solve is run to a tight Newton tolerance with the accepted residual functions imported
from the v047 pipeline.  At each step n the following are formed with the implemented Jacobian
R_JAC (automatic derivative of residual_cylindrical_chain):

    J_h = D_Z F_{A,h}(Z_G)          stage Jacobian at the converged stage vector,
    J_0 = D_Z F_{A,0}(Z_*)          h -> 0 limit: Jacobian of the h = 0 stage system at its root
                                    Z_* (all stages equal to the lifted endpoint state).

The Euclidean operator norm on the implemented stage layout is used throughout.  Recorded per h:
M_0 = max_n ||J_0^{-1}||, C_J = max_n ||J_h - J_0|| / h, the Neumann margin max_n M_0 ||J_h - J_0||
(the lemma needs <= 1/2), the ratio ||J_h^{-1}|| / ||J_0^{-1}|| (the lemma gives <= 2), and the
implied threshold h_0 = 1 / (2 M_0 C_J).  For Lemma newton-envelope the distances of two predictors
to Z_G are recorded: the lifted endpoint stage Z_* (O(h) by construction) and the implemented
Algorithm-1 predictor stage_guess (zero angular velocity/acceleration guesses), together with the
contraction of the first Newton step from the implemented predictor.

The check runs at most 14 stage solves plus 14 h = 0 solves.  It never invokes run_v047.py's main
campaign and does not use the default 1e-4 step size.  It is a finite-window diagnostic of the
lemma constants, not a proof input.
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
PIPELINE = ROOT / "v047_cylindrical_chain_pipeline"
OUT_JSON = PAPER / "P2_CONSTANTS_NUMERICAL_CHECK.json"
OUT_CSV = PAPER / "P2_CONSTANTS_NUMERICAL_CHECK.csv"
OUT_MD = PAPER / "P2_CONSTANTS_NUMERICAL_CHECK.md"

if str(PIPELINE) not in sys.path:
    sys.path.insert(0, str(PIPELINE))

import run_v047 as v047  # noqa: E402

H_VALUES = [0.04, 0.02, 0.01]
T_FINAL = 0.08
NEWTON_TOL = 1.0e-13
MAX_NEWTON_ITERS = 60
LIFT_TOL = 1.0e-9  # the h = 0 root must reproduce the endpoint state (u = 0, r, v, w) to this accuracy


def residual(x: np.ndarray, args: tuple) -> np.ndarray:
    return np.asarray(v047.R_VALUE(jnp.asarray(x, dtype=jnp.float64), *args), dtype=float)


def jacobian(x: np.ndarray, args: tuple) -> np.ndarray:
    return np.asarray(v047.R_JAC(jnp.asarray(x, dtype=jnp.float64), *args), dtype=float)


def newton(x0: np.ndarray, args: tuple) -> tuple[np.ndarray, list[np.ndarray], bool]:
    """Full Newton from x0; returns the root, the iterate history, and the convergence flag."""
    x = np.array(x0, dtype=float)
    history = [x.copy()]
    converged = False
    for _ in range(MAX_NEWTON_ITERS):
        res = residual(x, args)
        if float(np.linalg.norm(res)) <= NEWTON_TOL:
            converged = True
            break
        x = x + np.linalg.solve(jacobian(x, args), -res)
        history.append(x.copy())
    if not converged:
        converged = float(np.linalg.norm(residual(x, args))) <= NEWTON_TOL
    return x, history, converged


def lifted_endpoint_stage(state: Any, params: Any) -> tuple[np.ndarray, tuple, dict[str, Any]]:
    """Root Z_* of the h = 0 stage system: every stage equals the lifted endpoint state."""
    args0 = v047.build_args(state, 0.0, params)
    guess = v047.stage_guess(state, 0.0, params)
    # start the angular-velocity guess from the endpoint value; the h = 0 rows fix it anyway
    stages = v047.unpack_stages(guess)
    blocks = []
    for st in stages:
        w = np.asarray(state.w, dtype=float)
        blocks.extend([np.asarray(st["u"]).reshape(-1), np.asarray(st["r"]).reshape(-1), np.asarray(st["v"]).reshape(-1),
                       w.reshape(-1), np.asarray(st["a"]).reshape(-1), np.asarray(st["alpha"]).reshape(-1),
                       np.asarray(st["lambda"]).reshape(-1)])
    x_star, _, conv = newton(np.concatenate(blocks), args0)
    st = v047.unpack_stages(x_star)
    dev = 0.0
    for s in st:
        dev = max(dev, float(np.max(np.abs(np.asarray(s["u"])))),
                  float(np.max(np.abs(np.asarray(s["r"]) - np.asarray(state.r)))),
                  float(np.max(np.abs(np.asarray(s["v"]) - np.asarray(state.v)))),
                  float(np.max(np.abs(np.asarray(s["w"]) - np.asarray(state.w)))))
    return x_star, args0, {"h0_root_converged": conv, "h0_root_endpoint_deviation": dev}


def opnorm(mat: np.ndarray) -> float:
    return float(np.linalg.norm(mat, 2))


def inv_norm(mat: np.ndarray) -> float:
    return float(1.0 / np.linalg.svd(mat, compute_uv=False)[-1])


def main() -> int:
    params = v047.make_params(v047.CASES["cylindrical_smooth"])
    rows: list[dict[str, Any]] = []
    started = time.perf_counter()
    for h in H_VALUES:
        state = v047.project_endpoint_velocity(v047.initial_state(params), params)
        n_steps = int(round(T_FINAL / h))
        agg = {"M0": 0.0, "condJ0": 0.0, "CJ": 0.0, "neumann": 0.0, "inv_ratio": 0.0, "Mh": 0.0,
               "lift_dev": 0.0, "pred_lifted": 0.0, "pred_impl": 0.0, "contraction_impl": 0.0,
               "pred_impl_over_lifted": 0.0}
        h0_implied = math.inf
        all_conv = True
        iters = 0
        for _ in range(n_steps):
            args = v047.build_args(state, h, params)
            x_pred = v047.stage_guess(state, h, params)
            z_g, hist, conv = newton(x_pred, args)
            all_conv = all_conv and conv
            iters += len(hist) - 1
            x_star, _args0, lift = lifted_endpoint_stage(state, params)
            all_conv = all_conv and bool(lift["h0_root_converged"])
            j_h = jacobian(z_g, args)
            j_0 = jacobian(x_star, _args0)
            m0 = inv_norm(j_0)
            mh = inv_norm(j_h)
            delta = opnorm(j_h - j_0)
            cj = delta / h
            agg["M0"] = max(agg["M0"], m0)
            agg["Mh"] = max(agg["Mh"], mh)
            agg["condJ0"] = max(agg["condJ0"], m0 * opnorm(j_0))
            agg["CJ"] = max(agg["CJ"], cj)
            agg["neumann"] = max(agg["neumann"], m0 * delta)
            agg["inv_ratio"] = max(agg["inv_ratio"], mh / m0)
            h0_implied = min(h0_implied, 1.0 / (2.0 * m0 * cj))
            agg["lift_dev"] = max(agg["lift_dev"], lift["h0_root_endpoint_deviation"])
            d_lifted = float(np.linalg.norm(x_star - z_g))
            d_impl = float(np.linalg.norm(x_pred - z_g))
            agg["pred_lifted"] = max(agg["pred_lifted"], d_lifted)
            agg["pred_impl"] = max(agg["pred_impl"], d_impl)
            agg["pred_impl_over_lifted"] = max(agg["pred_impl_over_lifted"], d_impl / max(d_lifted, 1e-300))
            if len(hist) > 1 and d_impl > 0:
                agg["contraction_impl"] = max(agg["contraction_impl"], float(np.linalg.norm(hist[1] - z_g)) / d_impl)
            stages = v047.unpack_stages(jnp.asarray(z_g, dtype=jnp.float64))
            state = v047.next_state_from_stages(state, h, stages, params, project_velocity=True)
        row = {
            "h": h, "steps": n_steps, "newton_tolerance": NEWTON_TOL, "all_solves_converged": all_conv,
            "total_newton_iterations": iters,
            "max_J0_inverse_norm_M0": agg["M0"], "max_J0_condition_number": agg["condJ0"],
            "max_Jh_inverse_norm": agg["Mh"], "max_CJ_ratio": agg["CJ"], "max_neumann_margin_M0_delta": agg["neumann"],
            "max_Jh_inverse_over_J0_inverse": agg["inv_ratio"], "implied_h0": h0_implied,
            "h_le_implied_h0": bool(h <= h0_implied),
            "max_h0_root_endpoint_deviation": agg["lift_dev"],
            "max_lifted_predictor_distance": agg["pred_lifted"], "max_implemented_predictor_distance": agg["pred_impl"],
            "max_implemented_over_lifted_predictor_distance": agg["pred_impl_over_lifted"],
            "max_first_newton_contraction_from_implemented_predictor": agg["contraction_impl"],
        }
        # The lemma's conclusion (uniform inverse within factor 2) is checked directly; the Neumann
        # sufficient condition M0*delta <= 1/2 is recorded separately because it is expected to be far
        # more restrictive than the observed behaviour in this norm.
        row["neumann_condition_met"] = bool(agg["neumann"] <= 0.5)
        row["first_newton_step_contracts_from_implemented_predictor"] = bool(agg["contraction_impl"] < 1.0)
        row["inverse_bound_observed"] = bool(all_conv and agg["inv_ratio"] <= 2.0 and agg["lift_dev"] <= LIFT_TOL)
        rows.append(row)
        print(f"h={h:g} steps={n_steps} M0={agg['M0']:.3e} CJ={agg['CJ']:.3e} M0*delta={agg['neumann']:.3e} "
              f"inv_ratio={agg['inv_ratio']:.3f} h0={h0_implied:.3e} pred_lifted={agg['pred_lifted']:.3e} "
              f"pred_impl={agg['pred_impl']:.3e} contraction={agg['contraction_impl']:.3e} "
              f"inverse_bound_observed={row['inverse_bound_observed']} neumann={row['neumann_condition_met']}")

    all_ok = all(r["inverse_bound_observed"] for r in rows)
    neumann_all = all(r["neumann_condition_met"] for r in rows)
    if all_ok and neumann_all:
        status = "inverse_bound_observed_neumann_threshold_certified"
    elif all_ok:
        status = "inverse_bound_observed_neumann_threshold_below_reported_h"
    else:
        status = "p2_constants_check_failed"
    lifted_ratios = [rows[i]["max_lifted_predictor_distance"] / rows[i + 1]["max_lifted_predictor_distance"]
                     for i in range(len(rows) - 1)]
    payload = {
        "schema": "p2-constants-numerical-check-v1",
        "status": status,
        "neumann_condition_met_on_all_reported_h": neumann_all,
        "first_newton_step_contracts_from_implemented_predictor_on_all_h": all(
            r["first_newton_step_contracts_from_implemented_predictor"] for r in rows),
        "case": "cylindrical_smooth",
        "h_values": H_VALUES,
        "t_final": T_FINAL,
        "newton_tolerance": NEWTON_TOL,
        "norm": "euclidean_operator_norm_on_implemented_stage_layout",
        "rows_ok": f"{sum(r['inverse_bound_observed'] for r in rows)}/{len(rows)}",
        "all_rows_ok": all_ok,
        "M0_overall": max(r["max_J0_inverse_norm_M0"] for r in rows),
        "CJ_overall": max(r["max_CJ_ratio"] for r in rows),
        "implied_h0_overall": min(r["implied_h0"] for r in rows),
        "all_reported_h_below_implied_h0": all(r["h_le_implied_h0"] for r in rows),
        "lifted_predictor_distance_halving_ratios": lifted_ratios,
        "run_v047_invoked": False,
        "default_1e-4_required": False,
        "heavy_numerical_run_invoked": False,
        "runtime_sec": time.perf_counter() - started,
        "lemmas": ["lem:p2-from-p1", "lem:newton-envelope"],
        "lean_theorems": ["IntegratorOrderProof.uniform_inverse_of_perturbation",
                          "IntegratorOrderProof.simplified_newton_residual_decay"],
        "rows": rows,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    md = [
        "# P2 Constants Numerical Check",
        "",
        f"Status: `{payload['status']}`.",
        "",
        "Finite-window instantiation of the constants of Lemma p2-from-p1 (uniform stage inverse from the",
        "h -> 0 Jacobian, Lean `uniform_inverse_of_perturbation`) and of the predictor distances used by",
        "Lemma newton-envelope (Lean `simplified_newton_residual_decay`), computed with the implemented",
        "Jacobian `R_JAC` on the smooth cylindrical chain.  Euclidean operator norm on the implemented",
        "stage layout.  Diagnostic only; not a proof input.",
        "",
        f"- Case: `{payload['case']}`; h values: `{H_VALUES}`; t_final: `{T_FINAL}`; Newton tolerance: `{NEWTON_TOL}`.",
        f"- Rows with the lemma conclusion observed (||J_h^-1|| <= 2 ||J_0^-1||, all solves converged, h=0 root reproduces the endpoint): `{payload['rows_ok']}`.",
        f"- M0 = max ||J_0^-1||: `{payload['M0_overall']:.3e}`; C_J = max ||J_h-J_0||/h: `{payload['CJ_overall']:.3e}`; implied Neumann threshold h_0 = 1/(2 M0 C_J): `{payload['implied_h0_overall']:.3e}`.",
        f"- Neumann sufficient condition M0*||J_h-J_0|| <= 1/2 met on all reported h: `{payload['neumann_condition_met_on_all_reported_h']}` (expected False: the sufficient condition is pessimistic in this norm; the conclusion is checked directly).",
        f"- First full-Newton step contracts from the implemented predictor on all h: `{payload['first_newton_step_contracts_from_implemented_predictor_on_all_h']}` (the implemented predictor zeroes angular velocity and acceleration guesses, so its distance to Z_G is O(1); the lifted endpoint predictor distance is O(h)).",
        "- run_v047_invoked: `False`; default_1e-4_required: `False`.",
        "",
        "| h | steps | M0 | cond J0 | C_J | M0*delta | inv ratio | implied h0 | lifted pred. dist | implemented pred. dist | first-step contraction | conclusion observed |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for r in rows:
        md.append(
            f"| {r['h']:g} | {r['steps']} | {r['max_J0_inverse_norm_M0']:.3e} | {r['max_J0_condition_number']:.3e} | "
            f"{r['max_CJ_ratio']:.3e} | {r['max_neumann_margin_M0_delta']:.3e} | {r['max_Jh_inverse_over_J0_inverse']:.3f} | "
            f"{r['implied_h0']:.3e} | {r['max_lifted_predictor_distance']:.3e} | {r['max_implemented_predictor_distance']:.3e} | "
            f"{r['max_first_newton_contraction_from_implemented_predictor']:.3e} | {r['inverse_bound_observed']} |")
    md += ["", "Validator: `validate_p2_constants_numerical_check.py`.", ""]
    OUT_MD.write_text("\n".join(md), encoding="utf-8")
    print(f"p2_constants_numerical_check={payload['status']}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
