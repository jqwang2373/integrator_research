#!/usr/bin/env python3
"""E6: behaviour over the whole regular branch, T = 0.5 at h = 0.01 (50 steps).

Two runs: the conservative variant (no friction, no external loads) for the energy drift, and the
smooth frictional chain for the constraint norms and Newton iteration counts.  Writes
results/E6_long_time.csv/json/png.
"""

from __future__ import annotations

import sys
import time

import numpy as np

from common import RESULTS, conservative_params, energy, integrate_trajectory, smooth_params, write_csv, write_json

T_FINAL = 0.5  # the regular branch of the accepted benchmark ends at t ~ 0.605
H = 0.01


def summarize(name: str, params, traj) -> tuple[dict, np.ndarray]:
    kin, pot = zip(*[energy(params, traj.r[k], traj.p[k], traj.v[k], traj.w[k]) for k in range(traj.steps + 1)])
    total = np.array(kin) + np.array(pot)
    drift = np.abs(total - total[0]) / max(abs(total[0]), 1e-300)
    row = {"case": name, "h": H, "t_final": T_FINAL, "steps": traj.steps, "converged": traj.converged, "runtime_sec": traj.runtime_sec,
           "energy_t0": float(total[0]), "max_relative_energy_drift": float(drift.max()), "final_relative_energy_drift": float(drift[-1]),
           "max_position_constraint_norm": float(traj.constraint_norm.max()), "max_velocity_constraint_norm": float(traj.velocity_constraint_norm.max()),
           "max_acc_position_constraint_norm": float(traj.acc_position_constraint_norm.max()),
           "max_acc_orientation_constraint_norm": float(traj.acc_orientation_constraint_norm.max()),
           "max_quaternion_unit_error": float(traj.quaternion_unit_error.max()),
           "mean_newton_iterations": float(traj.newton_iterations.mean()), "max_newton_iterations": int(traj.newton_iterations.max())}
    return row, drift


def main() -> int:
    started = time.perf_counter()
    runs = {"conservative": conservative_params(0.5), "smooth_friction": smooth_params(0.5)}
    rows, series = [], {}
    for name, params in runs.items():
        traj = integrate_trajectory(params, H, T_FINAL)
        if not traj.converged:
            print(f"{name}: FAILED after {traj.steps} steps: {traj.failure}")
        row, drift = summarize(name, params, traj)
        rows.append(row); series[name] = (traj, drift)
        print(f"{name}: steps={traj.steps} energy drift max={row['max_relative_energy_drift']:.3e} constraint max={row['max_position_constraint_norm']:.3e} "
              f"vel-constraint max={row['max_velocity_constraint_norm']:.3e} newton mean={row['mean_newton_iterations']:.2f} ({traj.runtime_sec:.1f}s)")
    write_csv(RESULTS / "E6_long_time.csv", rows)
    tc, dc = series["conservative"]; tf, _ = series["smooth_friction"]
    np.savez(RESULTS / "E6_series.npz", t=tc.t, drift_conservative=dc,
             constraint_conservative=tc.constraint_norm, velocity_constraint_conservative=tc.velocity_constraint_norm, newton_conservative=tc.newton_iterations,
             constraint_smooth_friction=tf.constraint_norm, velocity_constraint_smooth_friction=tf.velocity_constraint_norm, newton_smooth_friction=tf.newton_iterations)
    write_json(RESULTS / "E6_long_time.json", {"schema": "e6-long-time-v1", "h": H, "t_final": T_FINAL, "rows": rows, "runtime_sec": time.perf_counter() - started})
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.6))
    traj, drift = series["conservative"]
    axes[0].semilogy(traj.t, np.maximum(drift, 1e-17)); axes[0].set_title("relative energy drift (conservative variant)"); axes[0].set_xlabel("t")
    for name, style in (("conservative", "-"), ("smooth_friction", "--")):
        traj, _ = series[name]
        axes[1].semilogy(traj.t[1:], np.maximum(traj.constraint_norm, 1e-17), style, label=f"position level, {name}")
        axes[1].semilogy(traj.t[1:], np.maximum(traj.velocity_constraint_norm, 1e-17), style, alpha=0.6, label=f"velocity level, {name}")
    axes[1].set_title("endpoint constraint norms"); axes[1].set_xlabel("t"); axes[1].legend(fontsize=7)
    for name in ("conservative", "smooth_friction"):
        traj, _ = series[name]
        axes[2].plot(traj.t[1:], traj.newton_iterations, label=name, lw=0.8)
    axes[2].set_title("Newton iterations per step"); axes[2].set_xlabel("t"); axes[2].legend(fontsize=8)
    for ax in axes: ax.grid(True, alpha=0.3)
    fig.tight_layout(); fig.savefig(RESULTS / "E6_long_time.png", dpi=160); plt.close(fig)
    print("E6 written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
