#!/usr/bin/env python3
"""Numerical instantiation of the constants in Lemma p2-from-p1 and Lemma newton-envelope.

For the smooth cylindrical-chain case on the accepted horizon T = 0.08 and the reported step sizes,
every stage solve is run to a tight Newton tolerance with the accepted residual functions imported
from the v047 pipeline.  At each step n the following are formed with the implemented Jacobian
R_JAC (automatic derivative of residual_cylindrical_chain):

    J_h = D_Z F_{A,h}(Z_G)          stage Jacobian at the converged stage vector,
    J_0 = D_Z F_{A,0}(Z_*)          h -> 0 limit: Jacobian of the h = 0 stage system at its root
                                    Z_* (all stages equal to the lifted endpoint state).

Three norms are recorded for the Neumann argument ||J_h^{-1}|| <= 2 ||J_0^{-1}|| whenever
||J_0^{-1}|| ||J_h - J_0|| <= 1/2:

  * Euclidean operator norm on the implemented stage layout: M_0 = max_n ||J_0^{-1}||_2,
    C_J = max_n ||J_h - J_0||_2 / h, implied h_0 = 1 / (2 M_0 C_J).
  * Endpoint-linearized (J_0-weighted) residual norm ||F||_n := ||J_0(x_n)^{-1} F||_2, i.e. the
    length of the simplified Newton correction at the endpoint linearization, with the Euclidean
    norm on the stage space.  In this norm ||J_0^{-1}|| = 1 exactly and the perturbation is
    ||J_0^{-1}(J_h - J_0)||_2; this is the sharpest norm-based form of the Neumann argument.
  * Row/column-equilibrated Euclidean norm (rows of J_0 scaled to unit norm, then columns).

The dominant row/column block of (J_h - J_0)/h is identified on the implemented layout, and the
whole computation is repeated for a frictionless variant of the same mechanism (mu_s = mu_d =
viscous damping = 0) to attribute the size of C_J.  For Lemma newton-envelope the distances of two
predictors to Z_G are recorded: the lifted endpoint stage Z_* (O(h) by construction) and the
implemented Algorithm-1 predictor stage_guess (zero angular-velocity/acceleration guesses),
together with the contraction ratio of the first full Newton step from the implemented predictor.

The check runs 14 stage solves plus 14 h = 0 solves per variant.  It never invokes run_v047.py's
main campaign and does not use the default 1e-4 step size.  It is a finite-window diagnostic of
the lemma constants, not a proof input.
"""

from __future__ import annotations

import csv
import dataclasses
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

# implemented stage layout (see unpack_stages and residual_cylindrical_chain in run_v047.py)
COL_BLOCKS = [name for _stage in range(v047.N_STAGES)
              for name in ([nm for _body in range(v047.N_BODIES) for nm in ("u", "r", "v", "w", "a", "alpha") for _ in range(3)]
                           + ["lam"] * (v047.N_JOINTS * v047.LAMBDA_SIZE))]
ROW_BLOCKS = [name for _stage in range(v047.N_STAGES)
              for name in (["pvel"] * 6 + ["ublk"] * 6 + ["pacc"] * 6 + ["wblk"] * 6 + ["dyn"] * 12 + ["cons"] * 8)]


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


def norm_variants(j_h: np.ndarray, j_0: np.ndarray, h: float) -> dict[str, float]:
    d = j_h - j_0
    out: dict[str, float] = {}
    out["M0"] = inv_norm(j_0)
    out["Mh"] = inv_norm(j_h)
    out["condJ0"] = out["M0"] * opnorm(j_0)
    out["delta"] = opnorm(d)
    out["CJ"] = out["delta"] / h
    out["neumann"] = out["M0"] * out["delta"]
    # endpoint-linearized (J_0-weighted) residual norm: ||J_0^{-1}|| = 1, perturbation = ||J_0^{-1} (J_h - J_0)||
    out["rel_delta"] = opnorm(np.linalg.solve(j_0, d))
    out["rel_CJ"] = out["rel_delta"] / h
    # row/column equilibration from J_0
    row = np.linalg.norm(j_0, axis=1)
    t_row = 1.0 / row
    j0r = j_0 * t_row[:, None]
    col = np.linalg.norm(j0r, axis=0)
    s_col = 1.0 / col
    j0e = j0r * s_col[None, :]
    de = (d * t_row[:, None]) * s_col[None, :]
    out["eq_M0"] = inv_norm(j0e)
    out["eq_delta"] = opnorm(de)
    out["eq_neumann"] = out["eq_M0"] * out["eq_delta"]
    out["eq_condJ0"] = out["eq_M0"] * opnorm(j0e)
    # dominant block of (J_h - J_0)/h by largest absolute entry
    rows = np.array(ROW_BLOCKS)
    cols = np.array(COL_BLOCKS)
    best = ("", "", 0.0)
    other = 0.0
    for rn in np.unique(rows):
        for cn in np.unique(cols):
            blk = np.abs(d[np.ix_(rows == rn, cols == cn)]).max() / h
            if blk > best[2]:
                if best[2] > other:
                    other = best[2]
                best = (str(rn), str(cn), float(blk))
            elif blk > other:
                other = float(blk)
    out["dominant_block"] = f"{best[0]}x{best[1]}"
    out["dominant_block_entry_ratio"] = best[2]
    out["next_block_entry_ratio"] = other
    return out


def run_variant(params: Any, label: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for h in H_VALUES:
        state = v047.project_endpoint_velocity(v047.initial_state(params), params)
        n_steps = int(round(T_FINAL / h))
        agg: dict[str, float] = {}
        dominant: dict[str, int] = {}
        all_conv = True
        iters = 0
        for _ in range(n_steps):
            args = v047.build_args(state, h, params)
            x_pred = v047.stage_guess(state, h, params)
            z_g, hist, conv = newton(x_pred, args)
            all_conv = all_conv and conv
            iters += len(hist) - 1
            x_star, args0, lift = lifted_endpoint_stage(state, params)
            all_conv = all_conv and bool(lift["h0_root_converged"])
            nv = norm_variants(jacobian(z_g, args), jacobian(x_star, args0), h)
            dominant[nv["dominant_block"]] = dominant.get(nv["dominant_block"], 0) + 1
            for key, val in nv.items():
                if isinstance(val, float):
                    agg[key] = max(agg.get(key, 0.0), val)
            agg["inv_ratio"] = max(agg.get("inv_ratio", 0.0), nv["Mh"] / nv["M0"])
            agg["lift_dev"] = max(agg.get("lift_dev", 0.0), lift["h0_root_endpoint_deviation"])
            d_lifted = float(np.linalg.norm(x_star - z_g))
            d_impl = float(np.linalg.norm(x_pred - z_g))
            agg["pred_lifted"] = max(agg.get("pred_lifted", 0.0), d_lifted)
            agg["pred_impl"] = max(agg.get("pred_impl", 0.0), d_impl)
            if len(hist) > 1 and d_impl > 0:
                agg["contraction_impl"] = max(agg.get("contraction_impl", 0.0), float(np.linalg.norm(hist[1] - z_g)) / d_impl)
            stages = v047.unpack_stages(jnp.asarray(z_g, dtype=jnp.float64))
            state = v047.next_state_from_stages(state, h, stages, params, project_velocity=True)
        m0, cj = agg["M0"], agg["CJ"]
        rel_cj, eq_m0, eq_delta = agg["rel_CJ"], agg["eq_M0"], agg["eq_delta"]
        row = {
            "variant": label, "h": h, "steps": n_steps, "newton_tolerance": NEWTON_TOL, "all_solves_converged": all_conv,
            "total_newton_iterations": iters,
            "max_J0_inverse_norm_M0": m0, "max_J0_condition_number": agg["condJ0"], "max_Jh_inverse_norm": agg["Mh"],
            "max_CJ_ratio": cj, "max_neumann_margin_M0_delta": agg["neumann"],
            "max_Jh_inverse_over_J0_inverse": agg["inv_ratio"],
            "implied_h0": 1.0 / (2.0 * m0 * cj),
            "weighted_norm_max_CJ_ratio": rel_cj, "weighted_norm_max_neumann_margin": agg["rel_delta"],
            "weighted_norm_implied_h0": 1.0 / (2.0 * rel_cj),
            "equilibrated_max_J0_inverse_norm": eq_m0, "equilibrated_max_J0_condition_number": agg["eq_condJ0"],
            "equilibrated_max_neumann_margin": agg["eq_neumann"],
            "equilibrated_implied_h0": h / (2.0 * agg["eq_neumann"]),
            "dominant_block_of_jacobian_difference": max(dominant.items(), key=lambda kv: kv[1])[0],
            "dominant_block_max_entry_ratio": agg["dominant_block_entry_ratio"],
            "next_block_max_entry_ratio": agg["next_block_entry_ratio"],
            "max_h0_root_endpoint_deviation": agg["lift_dev"],
            "max_lifted_predictor_distance": agg["pred_lifted"], "max_implemented_predictor_distance": agg["pred_impl"],
            "max_implemented_over_lifted_predictor_distance": agg["pred_impl"] / max(agg["pred_lifted"], 1e-300),
            "max_first_newton_contraction_from_implemented_predictor": agg.get("contraction_impl", 0.0),
        }
        row["h_le_implied_h0"] = bool(h <= row["implied_h0"])
        row["h_le_weighted_norm_implied_h0"] = bool(h <= row["weighted_norm_implied_h0"])
        row["neumann_condition_met"] = bool(agg["neumann"] <= 0.5)
        row["weighted_norm_neumann_condition_met"] = bool(agg["rel_delta"] <= 0.5)
        row["first_newton_step_contracts_from_implemented_predictor"] = bool(row["max_first_newton_contraction_from_implemented_predictor"] < 1.0)
        row["inverse_bound_observed"] = bool(all_conv and agg["inv_ratio"] <= 2.0 and agg["lift_dev"] <= LIFT_TOL)
        rows.append(row)
        print(f"[{label}] h={h:g} M0={m0:.3e} CJ={cj:.3e} h0={row['implied_h0']:.3e} | weighted CJ={rel_cj:.3e} "
              f"h0={row['weighted_norm_implied_h0']:.3e} | eq h0={row['equilibrated_implied_h0']:.3e} | inv_ratio={agg['inv_ratio']:.3f} "
              f"| dominant={row['dominant_block_of_jacobian_difference']} {agg['dominant_block_entry_ratio']:.2e} vs {agg['next_block_entry_ratio']:.2e} "
              f"| pred lifted/impl={agg['pred_lifted']:.2e}/{agg['pred_impl']:.2e} contraction={agg.get('contraction_impl', 0.0):.3f} "
              f"| inverse_bound_observed={row['inverse_bound_observed']}")
    return rows


def main() -> int:
    params = v047.make_params(v047.CASES["cylindrical_smooth"])
    params_nf = dataclasses.replace(params, mu_s=0.0, mu_d=0.0, viscous_damping=0.0)
    started = time.perf_counter()
    rows = run_variant(params, "cylindrical_smooth")
    rows_nf = run_variant(params_nf, "cylindrical_smooth_frictionless")

    all_ok = all(r["inverse_bound_observed"] for r in rows)
    neumann_all = all(r["neumann_condition_met"] for r in rows)
    weighted_all = all(r["weighted_norm_neumann_condition_met"] for r in rows)
    if all_ok and neumann_all:
        status = "inverse_bound_observed_neumann_threshold_certified"
    elif all_ok:
        status = "inverse_bound_observed_neumann_threshold_below_reported_h"
    else:
        status = "p2_constants_check_failed"
    lifted_ratios = [rows[i]["max_lifted_predictor_distance"] / rows[i + 1]["max_lifted_predictor_distance"]
                     for i in range(len(rows) - 1)]
    friction = {
        "stribeck_velocity": float(params.stribeck_velocity), "mu_s": float(params.mu_s), "mu_d": float(params.mu_d),
        "viscous_damping": float(params.viscous_damping),
        "frictionless_variant_all_solves_converged": all(r["all_solves_converged"] for r in rows_nf),
        "frictionless_variant_inverse_bound_observed": all(r["inverse_bound_observed"] for r in rows_nf),
        "CJ_overall_with_friction": max(r["max_CJ_ratio"] for r in rows),
        "CJ_overall_frictionless": max(r["max_CJ_ratio"] for r in rows_nf),
        "weighted_norm_CJ_overall_with_friction": max(r["weighted_norm_max_CJ_ratio"] for r in rows),
        "weighted_norm_CJ_overall_frictionless": max(r["weighted_norm_max_CJ_ratio"] for r in rows_nf),
        "weighted_norm_implied_h0_with_friction": min(r["weighted_norm_implied_h0"] for r in rows),
        "weighted_norm_implied_h0_frictionless": min(r["weighted_norm_implied_h0"] for r in rows_nf),
        "frictionless_all_reported_h_below_weighted_norm_h0": all(r["h_le_weighted_norm_implied_h0"] for r in rows_nf),
        "dominant_block_with_friction": [r["dominant_block_of_jacobian_difference"] for r in rows],
        "dominant_block_frictionless": [r["dominant_block_of_jacobian_difference"] for r in rows_nf],
    }
    payload = {
        "schema": "p2-constants-numerical-check-v2",
        "status": status,
        "neumann_condition_met_on_all_reported_h": neumann_all,
        "weighted_norm_neumann_condition_met_on_all_reported_h": weighted_all,
        "first_newton_step_contracts_from_implemented_predictor_on_all_h": all(
            r["first_newton_step_contracts_from_implemented_predictor"] for r in rows),
        "case": "cylindrical_smooth",
        "h_values": H_VALUES,
        "t_final": T_FINAL,
        "newton_tolerance": NEWTON_TOL,
        "norm": "euclidean_operator_norm_on_implemented_stage_layout",
        "additional_norms": ["endpoint_linearized_J0_weighted_residual_norm", "row_column_equilibrated_euclidean_norm"],
        "rows_ok": f"{sum(r['inverse_bound_observed'] for r in rows)}/{len(rows)}",
        "all_rows_ok": all_ok,
        "M0_overall": max(r["max_J0_inverse_norm_M0"] for r in rows),
        "CJ_overall": max(r["max_CJ_ratio"] for r in rows),
        "implied_h0_overall": min(r["implied_h0"] for r in rows),
        "weighted_norm_CJ_overall": max(r["weighted_norm_max_CJ_ratio"] for r in rows),
        "weighted_norm_implied_h0_overall": min(r["weighted_norm_implied_h0"] for r in rows),
        "equilibrated_implied_h0_overall": min(r["equilibrated_implied_h0"] for r in rows),
        "all_reported_h_below_implied_h0": all(r["h_le_implied_h0"] for r in rows),
        "all_reported_h_below_weighted_norm_implied_h0": all(r["h_le_weighted_norm_implied_h0"] for r in rows),
        "lifted_predictor_distance_halving_ratios": lifted_ratios,
        "friction_attribution": friction,
        "run_v047_invoked": False,
        "default_1e-4_required": False,
        "heavy_numerical_run_invoked": False,
        "runtime_sec": time.perf_counter() - started,
        "lemmas": ["lem:p2-from-p1", "lem:newton-envelope"],
        "lean_theorems": ["IntegratorOrderProof.uniform_inverse_of_perturbation",
                          "IntegratorOrderProof.simplified_newton_residual_decay"],
        "rows": rows,
        "frictionless_rows": rows_nf,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows + rows_nf)
    md = [
        "# P2 Constants Numerical Check",
        "",
        f"Status: `{payload['status']}`.",
        "",
        "Finite-window instantiation of the constants of Lemma p2-from-p1 (uniform stage inverse from the",
        "h -> 0 Jacobian, Lean `uniform_inverse_of_perturbation`) and of the predictor distances used by",
        "Lemma newton-envelope (Lean `simplified_newton_residual_decay`), computed with the implemented",
        "Jacobian `R_JAC` on the smooth cylindrical chain.  Diagnostic only; not a proof input.",
        "",
        f"- Case: `{payload['case']}`; h values: `{H_VALUES}`; t_final: `{T_FINAL}`; Newton tolerance: `{NEWTON_TOL}`.",
        f"- Rows with the lemma conclusion observed (||J_h^-1|| <= 2 ||J_0^-1||, all solves converged, h=0 root reproduces the endpoint): `{payload['rows_ok']}`.",
        f"- Euclidean norm: M0 = max ||J_0^-1|| `{payload['M0_overall']:.3e}`, C_J = max ||J_h-J_0||/h `{payload['CJ_overall']:.3e}`, implied Neumann threshold h_0 `{payload['implied_h0_overall']:.3e}`; condition met on all reported h: `{neumann_all}`.",
        f"- Endpoint-linearized norm ||J_0^-1 F||: C_J `{payload['weighted_norm_CJ_overall']:.3e}`, implied h_0 `{payload['weighted_norm_implied_h0_overall']:.3e}`; condition met on all reported h: `{weighted_all}`.",
        f"- Equilibrated norm: implied h_0 `{payload['equilibrated_implied_h0_overall']:.3e}`.",
        f"- Dominant block of (J_h-J_0)/h: `{friction['dominant_block_with_friction']}` (Newton-Euler rows vs stage velocities: the Brown-McPhee friction curvature, Stribeck velocity `{friction['stribeck_velocity']}`).",
        f"- Frictionless variant (mu_s = mu_d = viscous = 0): endpoint-linearized C_J `{friction['weighted_norm_CJ_overall_frictionless']:.3e}` vs `{friction['weighted_norm_CJ_overall_with_friction']:.3e}` with friction; implied h_0 `{friction['weighted_norm_implied_h0_frictionless']:.3e}` vs `{friction['weighted_norm_implied_h0_with_friction']:.3e}`; all reported h below the frictionless threshold: `{friction['frictionless_all_reported_h_below_weighted_norm_h0']}`; dominant block `{friction['dominant_block_frictionless']}`.",
        f"- First full-Newton step contracts from the implemented predictor on all h: `{payload['first_newton_step_contracts_from_implemented_predictor_on_all_h']}` (the implemented predictor zeroes angular velocity and acceleration guesses, so its distance to Z_G is O(1); the lifted endpoint predictor distance is O(h)).",
        "- run_v047_invoked: `False`; default_1e-4_required: `False`.",
        "",
        "| variant | h | M0 | C_J | inv ratio | h0 Euclid | C_J weighted | h0 weighted | h0 equilibrated | dominant block | lifted pred. | implemented pred. | first-step ratio | conclusion observed |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---|",
    ]
    for r in rows + rows_nf:
        md.append(
            f"| {r['variant']} | {r['h']:g} | {r['max_J0_inverse_norm_M0']:.3e} | {r['max_CJ_ratio']:.3e} | {r['max_Jh_inverse_over_J0_inverse']:.3f} | "
            f"{r['implied_h0']:.3e} | {r['weighted_norm_max_CJ_ratio']:.3e} | {r['weighted_norm_implied_h0']:.3e} | {r['equilibrated_implied_h0']:.3e} | "
            f"{r['dominant_block_of_jacobian_difference']} | {r['max_lifted_predictor_distance']:.3e} | {r['max_implemented_predictor_distance']:.3e} | "
            f"{r['max_first_newton_contraction_from_implemented_predictor']:.3e} | {r['inverse_bound_observed']} |")
    md += ["", "Validator: `validate_p2_constants_numerical_check.py`.", ""]
    OUT_MD.write_text("\n".join(md), encoding="utf-8")
    print(f"p2_constants_numerical_check={payload['status']}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
