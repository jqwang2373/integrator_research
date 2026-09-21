#!/usr/bin/env python3
"""E3: observed order versus the sharpness of the Brown–McPhee friction law.

Stribeck velocities v_s in {0.5, 0.2, 0.1, 0.05, 0.02}, T = 1, six step sizes h_k = 0.1/2^k, each
against its own Gauss6 reference at h_ref = 0.1/256 (with the 0.1/128 Richardson floor).  For each
v_s the script also evaluates the small-step threshold of the uniform-inverse lemma in the
endpoint-linearized norm, h_0 = 1 / (2 max_n ||J_0^{-1}(J_h - J_0)|| / h), over the first steps of
the h = 0.01 trajectory, so that the order-recovery step size can be compared with h_0.
Writes results/E3_friction_sweep.csv/json/png.
"""

from __future__ import annotations

import sys
import time

import numpy as np

from common import (RESULTS, compare, fit_order, integrate_trajectory, load_or_compute_reference, pairwise_orders, smooth_params,
                    v047, write_csv, write_json)

T_FINAL = 0.5
STRIBECK = [0.5, 0.2, 0.1, 0.05, 0.02]
H_VALUES = [0.1 / 2**k for k in range(6)]
H_REF = 0.1 / 256
H_REF2 = 0.1 / 128
H0_PROBE_H = 0.01
H0_PROBE_STEPS = 10


def newton_root(x0, args, tol=1e-13, max_iter=60):
    import jax.numpy as jnp
    x = np.array(x0, float)
    for _ in range(max_iter):
        res = np.asarray(v047.R_VALUE(jnp.asarray(x), *args), float)
        if np.linalg.norm(res) <= tol:
            return x, True
        x = x + np.linalg.solve(np.asarray(v047.R_JAC(jnp.asarray(x), *args), float), -res)
    return x, np.linalg.norm(np.asarray(v047.R_VALUE(jnp.asarray(x), *args), float)) <= tol


def neumann_threshold(params, h: float, steps: int) -> dict:
    """h_0 = 1/(2 C_J) with C_J = max_n ||J_0^{-1}(J_h - J_0)||_2 / h along the first `steps` steps."""
    import jax.numpy as jnp
    state = v047.project_endpoint_velocity(v047.initial_state(params), params)
    worst = 0.0
    for _ in range(steps):
        args = v047.build_args(state, h, params)
        z_g, ok = newton_root(v047.stage_guess(state, h, params), args)
        args0 = v047.build_args(state, 0.0, params)
        guess = v047.stage_guess(state, 0.0, params)
        stages = v047.unpack_stages(guess)
        blocks = []
        for st in stages:
            blocks.extend([np.asarray(st["u"]).reshape(-1), np.asarray(st["r"]).reshape(-1), np.asarray(st["v"]).reshape(-1),
                           np.asarray(state.w, float).reshape(-1), np.asarray(st["a"]).reshape(-1), np.asarray(st["alpha"]).reshape(-1), np.asarray(st["lambda"]).reshape(-1)])
        z0, ok0 = newton_root(np.concatenate(blocks), args0)
        j_h = np.asarray(v047.R_JAC(jnp.asarray(z_g), *args), float); j_0 = np.asarray(v047.R_JAC(jnp.asarray(z0), *args0), float)
        rel = np.linalg.norm(np.linalg.solve(j_0, j_h - j_0), 2) / h
        worst = max(worst, rel)
        state = v047.next_state_from_stages(state, h, v047.unpack_stages(jnp.asarray(z_g)), params, project_velocity=True)
    return {"weighted_CJ": worst, "h0": 1.0 / (2.0 * worst)}


def main() -> int:
    started = time.perf_counter()
    rows, summary = [], []
    for vs in STRIBECK:
        params = smooth_params(vs)
        tag = f"stribeck_{vs:g}".replace(".", "p")
        ref = load_or_compute_reference(f"{tag}_T0p5_h0p1_256", params, H_REF, T_FINAL)
        ref2 = load_or_compute_reference(f"{tag}_T0p5_h0p1_128", params, H_REF2, T_FINAL)
        floor = compare(ref2, ref)
        hs, ep, ev = [], [], []
        for h in H_VALUES:
            traj = integrate_trajectory(params, h, T_FINAL)
            row = {"stribeck_velocity": vs, "h": h, "steps": traj.steps, "converged": traj.converged, "runtime_sec": traj.runtime_sec,
                   "mean_newton_iterations": float(traj.newton_iterations.mean()) if traj.steps else float("nan")}
            if traj.converged:
                row.update(compare(traj, ref)); hs.append(h); ep.append(row["final_position"]); ev.append(row["final_velocity"])
            else:
                row["failure"] = traj.failure
            rows.append(row)
        po, vo = pairwise_orders(hs, ep), pairwise_orders(hs, ev)
        for k, h in enumerate(hs):
            r = next(x for x in rows if x["stribeck_velocity"] == vs and x["h"] == h)
            r["order_position_pairwise"] = po[k] if k < len(po) else float("nan")
            r["order_velocity_pairwise"] = vo[k] if k < len(vo) else float("nan")
        # smallest h at which the pairwise position order to the next finer step reaches 5.5
        recovery = next((hs[k] for k in range(len(po)) if po[k] >= 5.5), float("nan"))
        thr = neumann_threshold(params, H0_PROBE_H, H0_PROBE_STEPS)
        summary.append({"stribeck_velocity": vs, "position_fit": fit_order(hs, ep, floor["final_position"])[0], "velocity_fit": fit_order(hs, ev, floor["final_velocity"])[0],
                        "position_pairwise": po, "velocity_pairwise": vo, "order_recovery_h": recovery, "richardson_floor_position": floor["final_position"],
                        "neumann_weighted_CJ": thr["weighted_CJ"], "neumann_h0": thr["h0"], "converged_steps": [h for h in hs]})
        print(f"v_s={vs:g}: fit pos/vel {summary[-1]['position_fit']:.2f}/{summary[-1]['velocity_fit']:.2f}  pairwise pos {[round(x,2) for x in po]}  recovery h={recovery}  h0={thr['h0']:.2e}")
    write_csv(RESULTS / "E3_friction_sweep.csv", rows)
    write_json(RESULTS / "E3_friction_sweep.json", {"schema": "e3-friction-sweep-v1", "t_final": T_FINAL, "h_values": H_VALUES, "h_ref": H_REF,
                                                    "summary": summary, "rows": rows, "runtime_sec": time.perf_counter() - started})
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    for vs in STRIBECK:
        ok = [r for r in rows if r["stribeck_velocity"] == vs and r["converged"]]
        axes[0].loglog([r["h"] for r in ok], [r["final_position"] for r in ok], marker="o", label=f"$v_s$ = {vs:g}")
    h_arr = np.array(H_VALUES); base = [r for r in rows if r["stribeck_velocity"] == 0.5 and r["converged"]][-1]
    axes[0].loglog(h_arr, base["final_position"] * (h_arr / base["h"]) ** 6, "k--", lw=0.8, label="slope 6")
    axes[0].set_xlabel("h"); axes[0].set_ylabel("position error at t = T"); axes[0].legend(fontsize=8); axes[0].set_title("convergence by friction sharpness")
    axes[1].semilogx([s["stribeck_velocity"] for s in summary], [s["position_fit"] for s in summary], "o-", label="fitted position order")
    axes[1].semilogx([s["stribeck_velocity"] for s in summary], [s["velocity_fit"] for s in summary], "s--", label="fitted velocity order")
    axes[1].axhline(6, color="k", lw=0.8, ls=":"); axes[1].set_xlabel("Stribeck velocity $v_s$"); axes[1].set_ylabel("observed order"); axes[1].legend(fontsize=8)
    axes[1].set_title("observed order vs friction sharpness")
    for ax in axes: ax.grid(True, which="both", alpha=0.3)
    fig.tight_layout(); fig.savefig(RESULTS / "E3_friction_sweep.png", dpi=160); plt.close(fig)
    print("E3 written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
