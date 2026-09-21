#!/usr/bin/env python3
"""E4: convergence of Gauss6/FullVA on the four public benchmark mechanisms.

* single pendulum (kinematically driven, theta(t) = pi/2 + pi/4 cos 2t): the absolute-coordinate
  FullVA harness `run_v047.integrate_asme_single_driven_absolute_fullva`; errors are against the
  analytic state, so no reference run and no Richardson floor are needed.  Its predictor is built
  from the analytic drive, so only the position/orientation errors (Gauss-weight reconstruction,
  order six down to roundoff) are meaningful; the velocity errors sit at the roundoff level set by
  the conditioning of the driven stage Jacobian and carry no h-dependence;
* double pendulum: the v029 double-revolute FullVA harness (`integrate_v029_asme_double_trajectory`,
  method `double_revolute_gauss6_fullva`), errors on the recorded world-frame trajectories against
  the h_ref = 0.1/128 run (the 0.1/64 run gives the Richardson floor).  The v029 module is loaded
  with the AD-safe small-angle quaternion helpers of v048 (`install_v029_jax_safe_small_angle_patch`),
  without which its Newton loop returns NaN below h ~ 1e-3;
* four-link and slider-crank: the v048 public-horizon closed-loop runner
  (`run_public_closed_loop_shard.py`, Gauss6/FullVA with the public rA initial conditions), which
  writes trajectory L-infinity errors against its own Gauss6 reference at h_ref = 0.1/128; the
  h = 0.1/64 row of the same shard is used as the Richardson floor and excluded from the fit.

Horizon T = 1 for all four mechanisms.  Writes results/E4_asme.csv/json/png.
"""

from __future__ import annotations

import csv
import subprocess
import sys
import time

import numpy as np

from common import NUMERICS, RESULTS, fit_order, pairwise_orders, v047, write_csv, write_json

V048 = NUMERICS / "v048_cross_paper_same_test_benchmarks"
sys.path.insert(0, str(V048))
import run_ra2021_double_local_source_policy_candidate as cand  # noqa: E402  (AD-safe small-angle patch for v029)
PY = sys.executable
T_FINAL = 1.0
H_SINGLE = [0.1 / 2**k for k in range(6)]
H_DOUBLE = [0.1 / 2**k for k in range(6)]
H_DOUBLE_REF, H_DOUBLE_REF2 = 0.1 / 128, 0.1 / 64
ROUNDOFF_LEVEL = 1e-12  # errors below this on every step size: the mechanism is driven and reproduced at roundoff
H_CLOSED = [0.1 / 2**k for k in range(1, 6)]
H_CLOSED_FLOOR = 0.1 / 64
H_CLOSED_REF = 0.1 / 128


def run_single(h_values):
    rows = []
    for h in h_values:
        t0 = time.perf_counter(); out = v047.integrate_asme_single_driven_absolute_fullva(h, T_FINAL, False); rt = time.perf_counter() - t0
        row = {"model": "single_pendulum", "harness": "v047_asme_single_driven_absolute_fullva", "h": h, "t_final": T_FINAL, "steps": int(out["steps"]),
               "runtime_sec": rt, "total_newton_iterations": int(out["total_newton_iterations"]),
               "max_position_constraint_norm": float(out["max_endpoint_pivot_constraint_norm"]), "max_velocity_constraint_norm": float(out["max_endpoint_pivot_velocity_norm"]),
               "final_position": float(out["position_l2_error"]), "final_velocity": float(out["velocity_l2_error"]),
               "final_orientation": float(out["orientation_error_rad"]), "final_angular_velocity": float(out["omega_l2_error"]), "status": "ok"}
        rows.append(row)
        print(f"single h={h:.5g} pos={row['final_position']:.3e} ori={row['final_orientation']:.3e} vel={row['final_velocity']:.3e} ({rt:.1f}s)")
    # analytic reference: the floor is roundoff; fits use only errors above 100 x this level
    return rows, {"final_position": 1e-15, "final_velocity": 1e-15, "final_orientation": 1e-15, "final_angular_velocity": 1e-15}


def run_double(h_values):
    v029 = cand.load_v029_for_candidate(v047, True)
    params = v047.make_asme_double_pendulum_params(v029)
    method = "double_revolute_gauss6_fullva"
    run = lambda h: v047.integrate_v029_asme_double_trajectory(v029, method, h, T_FINAL, params)
    ref, ref2 = run(H_DOUBLE_REF), run(H_DOUBLE_REF2)
    def err(out, base):
        c = v047.compare_nested_trajectory(base, out)
        return {"final_position": c["pos_final_l2"], "final_velocity": c["vel_final_l2"], "linf_position": c["pos_traj_linf"], "linf_velocity": c["vel_traj_linf"]}
    floor = err(ref2, ref)
    rows = []
    for h in h_values:
        t0 = time.perf_counter(); out = run(h); rt = time.perf_counter() - t0
        row = {"model": "double_pendulum", "harness": "v029_double_revolute_gauss6_fullva", "h": h, "t_final": T_FINAL, "steps": out["steps"], "runtime_sec": rt, "status": "ok",
               "total_newton_iterations": int(out.get("total_newton_iterations", 0)),
               "max_position_constraint_norm": float(out.get("max_endpoint_constraint_norm", float("nan"))),
               "max_velocity_constraint_norm": float(out.get("max_endpoint_velocity_constraint_norm", float("nan")))}
        row.update(err(out, ref)); rows.append(row)
        print(f"double h={h:.5g} pos={row['final_position']:.3e} vel={row['final_velocity']:.3e} ({rt:.1f}s)")
    return rows, floor


def run_closed(model: str, h_values):
    steps_token = ",".join(f"{h:.10g}" for h in list(h_values) + [H_CLOSED_FLOOR])
    cmd = [PY, "run_public_closed_loop_shard.py", "--model", model, "--step-sizes", steps_token, "--t-end", f"{T_FINAL:.10g}", "--reference-h", f"{H_CLOSED_REF:.10g}"]
    proc = subprocess.run(cmd, cwd=V048, text=True, capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(f"closed-loop shard failed for {model}:\n{proc.stdout[-2000:]}\n{proc.stderr[-2000:]}")
    shard_dir = V048 / "results" / "public_closed_loop_shards"
    latest = max(shard_dir.glob(f"{model}_*.csv"), key=lambda p: p.stat().st_mtime)
    rows = []
    for r in csv.DictReader(latest.open()):
        if r.get("row_type") not in ("", None) and "reference" in str(r.get("row_type")):
            continue
        rows.append({"model": model, "harness": "v048_gauss6_fullva_closed_loop", "h": float(r["h"]), "t_final": float(r["t_end"]), "steps": int(float(r["steps"])) if r.get("steps") else int(round(T_FINAL / float(r["h"]))),
                     "runtime_sec": float(r["runtime_sec"]) if r.get("runtime_sec") else float("nan"), "total_newton_iterations": int(float(r["total_newton_iterations"])) if r.get("total_newton_iterations") else 0,
                     "max_position_constraint_norm": float(r["max_position_constraint_norm"]), "max_velocity_constraint_norm": float(r["max_velocity_constraint_norm"]),
                     "linf_position": float(r["pos_traj_linf"]), "linf_velocity": float(r["vel_traj_linf"]), "linf_acceleration": float(r["acc_traj_linf"]) if r.get("acc_traj_linf") else float("nan"),
                     "linf_multiplier": float(r["lambda_traj_linf"]) if r.get("lambda_traj_linf") else float("nan"), "status": r.get("status", ""), "shard_csv": latest.name})
    rows.sort(key=lambda x: -x["h"])
    for r in rows:
        r["is_floor_row"] = abs(r["h"] - H_CLOSED_FLOOR) < 1e-12
        print(f"{model} h={r['h']:.5g} pos={r['linf_position']:.3e} vel={r['linf_velocity']:.3e} status={r['status']}{'  (floor row)' if r['is_floor_row'] else ''}")
    floor_row = next((r for r in rows if r["is_floor_row"]), None)
    floor = {"linf_position": floor_row["linf_position"], "linf_velocity": floor_row["linf_velocity"]} if floor_row else {}
    return rows, floor


def main() -> int:
    started = time.perf_counter()
    all_rows, floors, orders = [], {}, {}
    single, floors["single_pendulum"] = run_single(H_SINGLE); all_rows += single
    double, floors["double_pendulum"] = run_double(H_DOUBLE); all_rows += double
    for model in ("four_link", "slider_crank"):
        closed, floors[model] = run_closed(model, H_CLOSED); all_rows += closed
    for model in ("single_pendulum", "double_pendulum", "four_link", "slider_crank"):
        rows = [r for r in all_rows if r["model"] == model and r.get("status", "ok") in ("ok", "") and not r.get("is_floor_row")]
        hs = [r["h"] for r in rows]
        keys = ["final_position", "final_velocity"] if model.endswith("pendulum") else ["linf_position", "linf_velocity"]
        orders[model] = {}
        for k in keys:
            errs = [r[k] for r in rows]
            floor = floors.get(model, {}).get(k, 0.0)
            roundoff = max(errs) < ROUNDOFF_LEVEL
            orders[model][k] = {"pairwise": pairwise_orders(hs, errs), "fit": float("nan") if roundoff else fit_order(hs, errs, floor)[0], "floor": floor,
                                "at_roundoff_for_all_h": roundoff, "max_error": max(errs)}
            po = orders[model][k]["pairwise"]
            for i, r in enumerate(rows):
                r[f"order_{k}"] = po[i] if i < len(po) else float("nan")
        print(model, {k: ("roundoff" if v["at_roundoff_for_all_h"] else round(v["fit"], 2)) for k, v in orders[model].items()})
    write_csv(RESULTS / "E4_asme.csv", all_rows)
    write_json(RESULTS / "E4_asme.json", {"schema": "e4-asme-v3", "roundoff_level": ROUNDOFF_LEVEL, "t_final": T_FINAL, "single_reference": "analytic", "double_h_ref": H_DOUBLE_REF, "double_h_ref2": H_DOUBLE_REF2,
                                          "closed_h_ref": H_CLOSED_REF, "closed_floor_h": H_CLOSED_FLOOR,
                                          "richardson_floor": floors, "orders": orders, "rows": all_rows, "runtime_sec": time.perf_counter() - started})
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 4, figsize=(15, 3.6))
    titles = {"single_pendulum": "driven single pendulum", "double_pendulum": "double pendulum", "four_link": "four-link", "slider_crank": "slider-crank"}
    for ax, model in zip(axes, titles):
        rows = [r for r in all_rows if r["model"] == model and r.get("status", "ok") in ("ok", "") and not r.get("is_floor_row")]
        hs = np.array([r["h"] for r in rows])
        keys = ["final_position", "final_velocity"] if model.endswith("pendulum") else ["linf_position", "linf_velocity"]
        for k, lab in zip(keys, ("position", "velocity")):
            ax.loglog(hs, [r[k] for r in rows], marker="o", label=lab)
        base = rows[-1][keys[0]]; ax.loglog(hs, base * (hs / hs[-1]) ** 6, "k--", lw=0.8, label="slope 6")
        ax.set_title(titles[model]); ax.set_xlabel("h"); ax.grid(True, which="both", alpha=0.3)
    axes[0].set_ylabel("error"); axes[-1].legend(fontsize=8)
    fig.suptitle("Gauss6/FullVA on the four benchmark mechanisms, T = 1")
    fig.tight_layout(); fig.savefig(RESULTS / "E4_asme.png", dpi=160); plt.close(fig)
    print("E4 written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
