#!/usr/bin/env python3
"""E7: solver envelope and exact stage identity on the E1 grid.

For every step of the E1 sweep (smooth chain, T = 0.5, h = 0.1/2^k, k = 0..5) the stage system is
solved with the production Newton rule (stop when the residual norm or the update norm is below
1e-11, at most 80 iterations) and the converged stage vector is examined:

* ||F_h(Z~)||: the implemented (row-scaled) residual at the accepted iterate, and its ratio to h^7,
  which is the c_eta needed for hypothesis (H3) on that step;
* the reduced collocation defects Delta_i[s_j], Delta_i[s_j'], Delta_i[theta_j], Delta_i[theta_j']
  and the components of d_j, d_j', d_j'' orthogonal to n_j (exact stage identity, Lemma 1);
* Newton iterations.

Writes results/E7_solver_envelope.csv/json.
"""

from __future__ import annotations

import importlib.util
import sys
import time

import numpy as np

from common import NUMERICS, RESULTS, smooth_params, v047, write_csv, write_json

REPO = NUMERICS.parent

IDENTITY_CHECK = REPO / "validation" / "paper_v047_cylindrical_chain" / "run_exact_stage_identity_numerical_check.py"
T_FINAL = 0.5
H_VALUES = [0.1 / 2**k for k in range(6)]
TOL = 1.0e-11
MAX_ITERS = 80


def load_identity_helpers():
    spec = importlib.util.spec_from_file_location("identity_check_helpers", IDENTITY_CHECK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def production_newton(state, h, params):
    import jax.numpy as jnp
    x = np.asarray(v047.stage_guess(state, h, params), float)
    args = v047.build_args(state, h, params)
    last = np.inf
    for it in range(1, MAX_ITERS + 1):
        res = np.asarray(v047.R_VALUE(jnp.asarray(x), *args), float)
        last = float(np.linalg.norm(res))
        if last < TOL:
            return x, args, last, it
        delta = np.linalg.solve(np.asarray(v047.R_JAC(jnp.asarray(x), *args), float), -res)
        x = x + delta
        if float(np.linalg.norm(delta)) < TOL:
            last = float(np.linalg.norm(np.asarray(v047.R_VALUE(jnp.asarray(x), *args), float)))
            return x, args, last, it
    raise RuntimeError(f"Newton failed, residual {last:.3e}")


def main() -> int:
    started = time.perf_counter()
    helpers = load_identity_helpers()
    params = smooth_params(0.5)
    normals = helpers.fixed_normals(params)
    _, A, _ = v047.qp.gauss_legendre_coefficients(v047.N_STAGES)
    A = np.asarray(A, float)
    rows = []
    for h in H_VALUES:
        import jax.numpy as jnp
        state = v047.project_endpoint_velocity(v047.initial_state(params), params)
        n_steps = int(round(T_FINAL / h))
        worst = {"residual": 0.0, "ratio_h7": 0.0, "reduced_defect": 0.0, "perp": 0.0, "factorization": 0.0}
        iters = []
        min_axis = np.inf
        for _ in range(n_steps):
            x, args, res_norm, it = production_newton(state, h, params)
            iters.append(it)
            kins, kin0 = helpers.stage_kinematics(x, state, params)
            d = helpers.collocation_defects(kins, kin0, normals, h, A)
            worst["residual"] = max(worst["residual"], res_norm)
            worst["ratio_h7"] = max(worst["ratio_h7"], res_norm / h**7)
            worst["reduced_defect"] = max(worst["reduced_defect"], d["s"], d["sdot"], d["theta"], d["thetadot"])
            worst["perp"] = max(worst["perp"], d["perp_point"], d["perp_vel"], d["perp_acc"])
            worst["factorization"] = max(worst["factorization"], d["factorization"])
            min_axis = min(min_axis, d["min_n_dot_axis"])
            state = v047.next_state_from_stages(state, h, v047.unpack_stages(jnp.asarray(x)), params, project_velocity=True)
        row = {"h": h, "steps": n_steps, "mean_newton_iterations": float(np.mean(iters)), "max_newton_iterations": int(max(iters)),
               "max_residual_norm": worst["residual"], "max_residual_over_h7": worst["ratio_h7"], "h7": h**7,
               "max_reduced_collocation_defect": worst["reduced_defect"], "max_perp_component": worst["perp"],
               "max_factorization_defect": worst["factorization"], "min_n_dot_axis": min_axis}
        rows.append(row)
        print(f"h={h:.6g}: newton {row['mean_newton_iterations']:.2f}/step, max residual {row['max_residual_norm']:.2e} "
              f"(= {row['max_residual_over_h7']:.2e} h^7), reduced defect {row['max_reduced_collocation_defect']:.1e}, perp {row['max_perp_component']:.1e}, "
              f"factorization {row['max_factorization_defect']:.1e}, min n.a {min_axis:.3f}", flush=True)
    write_csv(RESULTS / "E7_solver_envelope.csv", rows)
    write_json(RESULTS / "E7_solver_envelope.json", {"schema": "e7-solver-envelope-v1", "t_final": T_FINAL, "newton_tolerance": TOL, "max_iterations": MAX_ITERS,
                                                     "max_c_eta_needed": max(r["max_residual_over_h7"] for r in rows), "rows": rows, "runtime_sec": time.perf_counter() - started})
    print("E7 written; c_eta needed on the whole sweep:", f"{max(r['max_residual_over_h7'] for r in rows):.2e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
