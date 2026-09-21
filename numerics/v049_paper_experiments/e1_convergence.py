#!/usr/bin/env python3
"""E1: convergence of Gauss6/FullVA on the smooth frictional chain over T = 1.

Step sizes h_k = 0.1 / 2^k, k = 0..5; reference h_ref = 0.1 / 256 (2560 steps) with the Richardson
difference to the h = 0.1 / 128 run reported as the resolution floor of the reference.  Writes
results/E1_convergence.csv/json and results/E1_convergence.png.
"""

from __future__ import annotations

import sys
import time

import numpy as np

from common import (RESULTS, T_REGULAR_BRANCH_END, branch_factor, compare, fit_order, integrate_trajectory, load_or_compute_reference,
                    pairwise_orders, smooth_params, write_csv, write_json)

T_FINAL = 0.5  # regular branch of the accepted benchmark ends at t ~ 0.605 (see common.T_REGULAR_BRANCH_END)
H_VALUES = [0.1 / 2**k for k in range(6)]
H_REF = 0.1 / 256
H_REF2 = 0.1 / 128
QUANTITIES = ["position", "orientation", "velocity", "angular_velocity"]


def main() -> int:
    params = smooth_params(0.5)
    started = time.perf_counter()
    ref = load_or_compute_reference("smooth_T0p5_h0p1_256", params, H_REF, T_FINAL)
    ref2 = load_or_compute_reference("smooth_T0p5_h0p1_128", params, H_REF2, T_FINAL)
    min_branch = min(branch_factor(params, ref.r[k], ref.p[k]) for k in range(ref.steps + 1))
    print(f"min n1.a1 on [0,T] = {min_branch:.4f}")
    richardson = compare(ref2, ref)
    print(f"reference ready ({time.perf_counter() - started:.1f}s); Richardson floor final position {richardson['final_position']:.3e}, velocity {richardson['final_velocity']:.3e}")
    rows = []
    trajs = {}
    for h in H_VALUES:
        traj = integrate_trajectory(params, h, T_FINAL)
        trajs[h] = traj
        row = {"h": h, "steps": traj.steps, "converged": traj.converged, "runtime_sec": traj.runtime_sec,
               "total_newton_iterations": int(traj.newton_iterations.sum()) if traj.steps else 0,
               "mean_newton_iterations": float(traj.newton_iterations.mean()) if traj.steps else float("nan"),
               "max_position_constraint_norm": float(traj.constraint_norm.max()) if traj.steps else float("nan"),
               "max_velocity_constraint_norm": float(traj.velocity_constraint_norm.max()) if traj.steps else float("nan"),
               "max_acc_position_constraint_norm": float(traj.acc_position_constraint_norm.max()) if traj.steps else float("nan"),
               "max_acc_orientation_constraint_norm": float(traj.acc_orientation_constraint_norm.max()) if traj.steps else float("nan"),
               "max_quaternion_unit_error": float(traj.quaternion_unit_error.max()) if traj.steps else float("nan")}
        if traj.converged:
            row.update(compare(traj, ref))
        else:
            row.update({f"{p}_{q}": float("nan") for p in ("final", "linf") for q in QUANTITIES})
            row["failure"] = traj.failure
        rows.append(row)
        print(f"h={h:.6g} steps={traj.steps} converged={traj.converged} pos={row.get('final_position', float('nan')):.3e} "
              f"vel={row.get('final_velocity', float('nan')):.3e} ori={row.get('final_orientation', float('nan')):.3e} newton/step={row['mean_newton_iterations']:.2f} {traj.runtime_sec:.1f}s")
    ok = [r for r in rows if r["converged"]]
    hs = [r["h"] for r in ok]
    orders = {}
    for prefix in ("final", "linf"):
        for q in QUANTITIES:
            errs = [r[f"{prefix}_{q}"] for r in ok]
            floor = richardson[f"{prefix}_{q}"]
            slope, npts = fit_order(hs, errs, floor)
            orders[f"{prefix}_{q}"] = {"pairwise": pairwise_orders(hs, errs), "fit": slope, "points_used": npts, "floor": floor}
    for r in rows:
        k = [x["h"] for x in rows].index(r["h"])
        for q in QUANTITIES:
            po = orders[f"final_{q}"]["pairwise"]
            r[f"order_final_{q}"] = po[k] if r["converged"] and k < len(po) else float("nan")
    payload = {"schema": "e1-convergence-v1", "case": "cylindrical_smooth_stribeck_0p5", "t_final": T_FINAL, "h_values": H_VALUES,
               "h_ref": H_REF, "h_ref2": H_REF2, "reference_steps": ref.steps, "reference_runtime_sec": ref.runtime_sec,
               "richardson_floor": richardson, "min_branch_factor_n1_dot_a1": min_branch, "regular_branch_end_t": T_REGULAR_BRANCH_END, "orders": orders, "rows": rows, "runtime_sec": time.perf_counter() - started,
               "error_definitions": "final_* at t=T; linf_* over all coarse output times; position/velocity/angular_velocity Frobenius over bodies; orientation max geodesic quaternion angle"}
    write_csv(RESULTS / "E1_convergence.csv", rows)
    write_json(RESULTS / "E1_convergence.json", payload)
    # figure
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.8))
    labels = {"position": "position", "orientation": "orientation", "velocity": "velocity", "angular_velocity": "angular velocity"}
    for ax, prefix, title in zip(axes, ("final", "linf"), (r"error at $t=T$", r"$L^\infty$ error over $[0,T]$")):
        for q in QUANTITIES:
            ax.loglog(hs, [r[f"{prefix}_{q}"] for r in ok], marker="o", label=labels[q])
        h_arr = np.array(hs); anchor = ok[-1][f"{prefix}_position"]
        ax.loglog(h_arr, anchor * (h_arr / hs[-1]) ** 6, "k--", lw=0.8, label=r"slope 6")
        ax.axhline(richardson[f"{prefix}_position"], color="grey", ls=":", lw=0.8, label="reference floor (position)")
        ax.set_xlabel("h"); ax.set_title(title); ax.grid(True, which="both", alpha=0.3)
    axes[0].set_ylabel("error"); axes[1].legend(fontsize=8, loc="lower right")
    fig.suptitle("Gauss6/FullVA on the smooth cylindrical chain, T = 0.5")
    fig.tight_layout(); fig.savefig(RESULTS / "E1_convergence.png", dpi=160); plt.close(fig)
    print("E1 written; fitted final orders:", {q: round(orders[f'final_{q}']['fit'], 3) for q in QUANTITIES})
    return 0


if __name__ == "__main__":
    sys.exit(main())
