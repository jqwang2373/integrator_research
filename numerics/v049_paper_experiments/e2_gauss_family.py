#!/usr/bin/env python3
"""E2: work/precision of the Gauss family (1, 2, 3 stages: orders 2, 4, 6) with the same FullVA
stage system and endpoint reconstruction, on the smooth chain over T = 1.

The v047 implementation reads the stage count from the module constant `N_STAGES`; this script
overrides it (and `DIM`) before each family member runs.  The jitted residual/Jacobian retrace for
the new stage-vector shape.  Errors are measured against the E1 Gauss6 reference (h_ref = 0.1/256).
Writes results/E2_gauss_family.csv/json/png.
"""

from __future__ import annotations

import sys
import time

import numpy as np

import common
from common import RESULTS, compare, fit_order, integrate_trajectory, load_or_compute_reference, pairwise_orders, smooth_params, write_csv, write_json

T_FINAL = 0.5
H_REF = 0.1 / 256
STAGE_H = {1: [0.1 / 2**k for k in range(8)], 2: [0.1 / 2**k for k in range(7)], 3: [0.1 / 2**k for k in range(6)]}
ORDER = {1: 2, 2: 4, 3: 6}


set_stages = common.set_stages


def main() -> int:
    params = smooth_params(0.5)
    started = time.perf_counter()
    set_stages(3)
    ref = load_or_compute_reference("smooth_T0p5_h0p1_256", params, H_REF, T_FINAL)
    ref2 = load_or_compute_reference("smooth_T0p5_h0p1_128", params, 0.1 / 128, T_FINAL)
    floor = compare(ref2, ref)
    rows, fits = [], {}
    for stages, hs in STAGE_H.items():
        set_stages(stages)
        integrate_trajectory(params, hs[0], 2 * hs[0])  # warm-up: JIT compilation for this stage count, not timed
        errs_pos, errs_vel, used_h = [], [], []
        for h in hs:
            traj = integrate_trajectory(params, h, T_FINAL)
            row = {"stages": stages, "nominal_order": ORDER[stages], "h": h, "steps": traj.steps, "converged": traj.converged,
                   "runtime_sec": traj.runtime_sec, "total_newton_iterations": int(traj.newton_iterations.sum()) if traj.steps else 0,
                   "mean_newton_iterations": float(traj.newton_iterations.mean()) if traj.steps else float("nan"),
                   "max_position_constraint_norm": float(traj.constraint_norm.max()) if traj.steps else float("nan"),
                   "max_velocity_constraint_norm": float(traj.velocity_constraint_norm.max()) if traj.steps else float("nan")}
            if traj.converged:
                row.update(compare(traj, ref)); used_h.append(h); errs_pos.append(row["final_position"]); errs_vel.append(row["final_velocity"])
            else:
                row["failure"] = traj.failure
            rows.append(row)
            print(f"stages={stages} h={h:.6g} converged={traj.converged} pos={row.get('final_position', float('nan')):.3e} vel={row.get('final_velocity', float('nan')):.3e} {traj.runtime_sec:.1f}s")
        fits[stages] = {"position_fit": fit_order(used_h, errs_pos, floor["final_position"])[0], "velocity_fit": fit_order(used_h, errs_vel, floor["final_velocity"])[0],
                        "position_pairwise": pairwise_orders(used_h, errs_pos), "velocity_pairwise": pairwise_orders(used_h, errs_vel)}
    set_stages(3)
    write_csv(RESULTS / "E2_gauss_family.csv", rows)
    write_json(RESULTS / "E2_gauss_family.json", {"schema": "e2-gauss-family-v1", "t_final": T_FINAL, "h_ref": H_REF, "richardson_floor": floor,
                                                  "fits": fits, "rows": rows, "runtime_sec": time.perf_counter() - started})
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.8))
    for stages in STAGE_H:
        ok = [r for r in rows if r["stages"] == stages and r["converged"]]
        axes[0].loglog([r["h"] for r in ok], [r["final_position"] for r in ok], marker="o", label=f"{stages} stage(s), order {ORDER[stages]}")
        axes[1].loglog([r["runtime_sec"] for r in ok], [r["final_position"] for r in ok], marker="o", label=f"{stages} stage(s)")
        axes[2].loglog([r["total_newton_iterations"] for r in ok], [r["final_position"] for r in ok], marker="o", label=f"{stages} stage(s)")
    axes[0].set_xlabel("h"); axes[0].set_ylabel("position error at t = T"); axes[0].set_title("convergence")
    axes[1].set_xlabel("wall time [s]"); axes[1].set_title("work/precision: time")
    axes[2].set_xlabel("total Newton iterations"); axes[2].set_title("work/precision: Newton iterations")
    for ax in axes: ax.grid(True, which="both", alpha=0.3); ax.axhline(floor["final_position"], color="grey", ls=":", lw=0.8)
    axes[0].legend(fontsize=8)
    fig.suptitle("Gauss family with the FullVA stage system, smooth chain, T = 0.5")
    fig.tight_layout(); fig.savefig(RESULTS / "E2_gauss_family.png", dpi=160); plt.close(fig)
    print("E2 written; fits:", {k: (round(v["position_fit"], 2), round(v["velocity_fit"], 2)) for k, v in fits.items()})
    return 0


if __name__ == "__main__":
    sys.exit(main())
