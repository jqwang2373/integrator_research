#!/usr/bin/env python3
"""E5: Gauss6/FullVA against the public absolute-coordinate codes on the benchmark mechanisms.

Part A (computed here): the double pendulum, the only benchmark mechanism whose motion is not fixed
by a drive constraint, on the public horizon T = 3.  Every error is the final-state L-infinity
difference (over bodies and components, positions and velocities) to ONE common reference: the
local Gauss6/FullVA double-revolute run at h = 1e-4 cached by v048
(`ra2021_double_local_source_policy_candidate_reference_h0p0001_T3.npz`, 30000 steps).  Rows:

* Gauss6/FullVA (v029 double-revolute harness with the AD-safe small-angle helpers, the same
  configuration that produced the reference) at h in {0.1, 0.05, 0.025, 0.0125, 0.01, 0.002, 0.001};
* the 2021 public rA / rp / reps formulations (dynamics mode, states recorded on t_i = i h);
* the 2022 public half-implicit rA and rA_half codes with the source tolerance policy.

Model-alignment check (computed here): on the short horizon T = 0.1, where the double pendulum has
not yet amplified perturbations, the 2021 rA final state is compared with a local Gauss6 run at
h = 0.1/16 for h in {0.1/16, 0.1/64}; the error must decrease with h (same model, same initial
state) rather than sit at a constant offset (different model).

Part B (assembled from the v048 result files, no reruns): the three driven mechanisms (single
pendulum, four-link, slider-crank) on the public horizon T = 3 and public step sizes
{1e-2, 1e-3, 1e-4}: Gauss6/FullVA errors (analytic for the driven single pendulum, local
reference at h = 1e-3 for the closed loops) and the public rA / rp / reps errors against their own
kinematic-mode reference, together with the recorded runtimes.

Writes results/E5_double_pendulum.csv/json/png and results/E5_driven_public_horizon.csv.
"""

from __future__ import annotations

import csv
import sys
import time

import numpy as np

from common import NUMERICS, RESULTS, pairwise_orders, v047, write_csv, write_json

V048 = NUMERICS / "v048_cross_paper_same_test_benchmarks"
sys.path.insert(0, str(V048))
import run_v048 as rv  # noqa: E402
import run_ra2021_double_local_source_policy_candidate as cand  # noqa: E402

T_END = 3.0
H_VALUES = [0.1, 0.05, 0.025, 0.0125, 0.01, 0.002, 0.001]
REFERENCE_NPZ = V048 / "results" / "ra2021_double_local_source_policy_candidate_reference_h0p0001_T3.npz"
PUBLIC_2021_FORMS = ("rA", "rp", "reps")
PUBLIC_2022_FORMS = ("rA", "rA_half")


def load_reference() -> dict:
    with np.load(REFERENCE_NPZ) as data:
        ref = {"h": float(data["h"]), "steps": int(data["steps"]), "pos": np.asarray(data["pos"], float)[:, :, -1], "vel": np.asarray(data["vel"], float)[:, :, -1],
               "runtime_sec": float(data["runtime_sec"]), "max_endpoint_constraint_norm": float(data["max_endpoint_constraint_norm"])}
    assert ref["steps"] == int(round(T_END / ref["h"]))
    return ref


def final_errors(pos_final: np.ndarray, vel_final: np.ndarray, ref: dict) -> dict[str, float]:
    return {"pos_final_linf": float(np.max(np.abs(pos_final - ref["pos"]))), "vel_final_linf": float(np.max(np.abs(vel_final - ref["vel"])))}


def run_public_fixed_grid(module_name: str, model_name: str, form: str, h: float, tol: float | None, time_flag: str, t_end: float = T_END) -> dict:
    """Replay a public example with its own setup and stepper, recording states on t_i = i h (v048 convention)."""
    import importlib
    module = importlib.import_module(module_name)
    setup = getattr(module, f"setup_{model_name}")
    args = ["--form", form, "--mode", "dynamics", "--step_size", str(h), time_flag, str(t_end), "--log", "warning", "--no-plot"]
    if tol is not None:
        args.extend(["--tol", str(tol)])
    started = time.perf_counter()
    system, params = setup(args)
    system.initialize()
    steps = int(round(params.t_end / params.h))
    if abs(steps * params.h - params.t_end) > 1e-12:
        raise ValueError(f"h={params.h} does not divide t_end={params.t_end}")
    t_grid = np.linspace(0.0, params.t_end, steps + 1, endpoint=True)
    pos = np.zeros((system.nb, 3)); vel = np.zeros((system.nb, 3)); iters = np.zeros(steps + 1)
    for i, t in enumerate(t_grid):
        system.do_step(i, t)
        iters[i] = system.k
    for j, body in enumerate(system.bodies):
        pos[j] = np.asarray(body.r, float).reshape(3); vel[j] = np.asarray(body.dr, float).reshape(3)
    return {"pos": pos, "vel": vel, "runtime_sec": time.perf_counter() - started, "avg_iterations": float(np.mean(iters)), "max_iterations": float(np.max(iters)), "steps": steps}


def gauss6_rows(ref: dict) -> list[dict]:
    v029 = cand.load_v029_for_candidate(v047, True)
    params = v047.make_asme_double_pendulum_params(v029)
    rows = []
    for h in H_VALUES:
        row = {"model": "double_pendulum", "method": "Gauss6/FullVA", "code": "local v029 double-revolute harness (AD-safe small-angle helpers)", "t_end": T_END, "h": h, "steps": int(round(T_END / h)), "status": "ok"}
        t0 = time.perf_counter()
        try:
            out = v047.integrate_v029_asme_double_trajectory(v029, "double_revolute_gauss6_fullva", h, T_END, params)
            row["runtime_sec"] = time.perf_counter() - t0
            row.update(final_errors(np.asarray(out["pos"], float)[:, :, -1], np.asarray(out["vel"], float)[:, :, -1], ref))
            row.update({"total_iterations": int(out["total_newton_iterations"]), "avg_iterations": out["total_newton_iterations"] / row["steps"],
                        "max_position_constraint_norm": float(out["max_endpoint_constraint_norm"]), "max_velocity_constraint_norm": float(out["max_endpoint_velocity_constraint_norm"])})
        except Exception as exc:  # noqa: BLE001
            row.update({"status": f"failed: {type(exc).__name__}: {str(exc)[:80]}", "runtime_sec": time.perf_counter() - t0, "pos_final_linf": float("nan"), "vel_final_linf": float("nan")})
        rows.append(row)
        print(f"Gauss6 h={h:g}: {row['status']} pos={row['pos_final_linf']:.3e} vel={row['vel_final_linf']:.3e} ({row['runtime_sec']:.1f}s)", flush=True)
    return rows


def public_2021_rows(ref: dict) -> list[dict]:
    rv.switch_simengine_root(rv.SBEL_C2)
    rv.patch_modern_numpy_scalar_assignments()
    rows = []
    for form in PUBLIC_2021_FORMS:
        for h in H_VALUES:
            row = {"model": "double_pendulum", "method": f"2021 public {form}", "code": "sbel-reproducibility 2021/ASME/rA-formulation/C2, dynamics mode", "t_end": T_END, "h": h, "steps": int(round(T_END / h)), "status": "ok"}
            try:
                out = run_public_fixed_grid("SimEngineMBD.example_models.double_pendulum", "double_pendulum", form, h, None, "--end_time")
                row.update(final_errors(out["pos"], out["vel"], ref)); row.update({k: out[k] for k in ("runtime_sec", "avg_iterations", "max_iterations")})
            except Exception as exc:  # noqa: BLE001
                row.update({"status": f"failed: {type(exc).__name__}: {str(exc)[:80]}", "pos_final_linf": float("nan"), "vel_final_linf": float("nan"), "runtime_sec": float("nan")})
            rows.append(row)
            print(f"2021 {form} h={h:g}: {row['status']} pos={row['pos_final_linf']:.3e} vel={row['vel_final_linf']:.3e} ({row['runtime_sec']:.1f}s)", flush=True)
    return rows


def public_2022_rows(ref: dict) -> list[dict]:
    rv.switch_simengine_root(rv.HI2022_ROOT)
    rv.patch_hi2022_modern_numpy_scalar_assignments()
    rows = []
    for form in PUBLIC_2022_FORMS:
        for h in H_VALUES:
            tol = rv.hi2022_tolerance(form, h, rv.HI2022_TOLERANCE_BASE)
            row = {"model": "double_pendulum", "method": f"2022 half-implicit {form}", "code": "sbel-reproducibility 2022/HalfImplicit_JCND, dynamics mode, source tolerance policy", "t_end": T_END, "h": h, "steps": int(round(T_END / h)), "status": "ok", "tolerance": tol}
            try:
                out = run_public_fixed_grid("SimEngineMBD.example_models.double_pendulum", "double_pendulum", form, h, tol, "-t")
                row.update(final_errors(out["pos"], out["vel"], ref)); row.update({k: out[k] for k in ("runtime_sec", "avg_iterations", "max_iterations")})
            except Exception as exc:  # noqa: BLE001
                row.update({"status": f"failed: {type(exc).__name__}: {str(exc)[:80]}", "pos_final_linf": float("nan"), "vel_final_linf": float("nan"), "runtime_sec": float("nan")})
            rows.append(row)
            print(f"2022 {form} h={h:g}: {row['status']} pos={row['pos_final_linf']:.3e} vel={row['vel_final_linf']:.3e} ({row['runtime_sec']:.1f}s)", flush=True)
    return rows


def alignment_rows() -> list[dict]:
    t_short = 0.1
    v029 = cand.load_v029_for_candidate(v047, True)
    params = v047.make_asme_double_pendulum_params(v029)
    loc = v047.integrate_v029_asme_double_trajectory(v029, "double_revolute_gauss6_fullva", t_short / 16, t_short, params)
    ref = {"pos": np.asarray(loc["pos"], float)[:, :, -1], "vel": np.asarray(loc["vel"], float)[:, :, -1]}
    rv.switch_simengine_root(rv.SBEL_C2); rv.patch_modern_numpy_scalar_assignments()
    rows = []
    for h in (t_short / 16, t_short / 64):
        out = run_public_fixed_grid("SimEngineMBD.example_models.double_pendulum", "double_pendulum", "rA", h, None, "--end_time", t_end=t_short)
        row = {"check": "model_alignment_T0p1", "method": "2021 public rA", "t_end": t_short, "h": h, "local_reference": f"Gauss6/FullVA h={t_short/16:g}"}
        row.update(final_errors(out["pos"], out["vel"], ref)); rows.append(row)
        print(f"alignment T=0.1 rA h={h:g}: pos={row['pos_final_linf']:.3e} vel={row['vel_final_linf']:.3e}", flush=True)
    return rows


def read_rows(name: str) -> list[dict]:
    with (V048 / "results" / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def driven_rows() -> list[dict]:
    """Assemble the public-horizon rows for the three driven mechanisms from the v048 result files."""
    out = []
    fl = lambda s: float(s) if s not in ("", None, "nan") else float("nan")
    for r in read_rows("gauss6_fullva_public_horizon_single_rows.csv"):
        out.append({"model": "single_pendulum", "method": "Gauss6/FullVA", "t_end": fl(r["t_end"]), "h": fl(r["h"]), "status": r["status"], "error_reference": "analytic driven solution",
                    "pos_final_error": fl(r["position_l2_error"]), "vel_final_error": fl(r["velocity_l2_error"]), "runtime_sec": fl(r["runtime_sec"]), "avg_iterations": fl(r["total_newton_iterations"]) / fl(r["steps"]), "source_csv": "gauss6_fullva_public_horizon_single_rows.csv"})
    for r in read_rows("gauss6_fullva_public_horizon_closed_loop_rows.csv"):
        degenerate = abs(fl(r["h"]) - fl(r["reference_h"])) < 1e-15
        out.append({"model": r["model"], "method": "Gauss6/FullVA", "t_end": fl(r["t_end"]), "h": fl(r["h"]), "status": "reference row (h = h_ref)" if degenerate else r["status"], "error_reference": f"local Gauss6/FullVA h = {fl(r['reference_h']):g}",
                    "pos_final_error": float("nan") if degenerate else fl(r["pos_traj_linf"]), "vel_final_error": float("nan") if degenerate else fl(r["vel_traj_linf"]), "runtime_sec": fl(r["runtime_sec"]),
                    "avg_iterations": fl(r["total_newton_iterations"]) / fl(r["steps"]) if r.get("steps") not in ("", "nan") else float("nan"), "source_csv": "gauss6_fullva_public_horizon_closed_loop_rows.csv"})
    for r in read_rows("ra2021_order_rows.csv"):
        out.append({"model": r["model"], "method": f"2021 public {r['form']}", "t_end": fl(r["t_end"]), "h": fl(r["h"]), "status": r["status"], "error_reference": f"public {r['reference_mode']} mode, h = {fl(r['reference_h']):g}",
                    "pos_final_error": fl(r["pos_final_linf"]), "vel_final_error": fl(r["vel_final_linf"]), "runtime_sec": fl(r["runtime_sec"]), "avg_iterations": fl(r["avg_iterations"]), "source_csv": "ra2021_order_rows.csv"})
    for r in read_rows("ra2021_public_timing_rows.csv"):
        out.append({"model": r["model"], "method": f"2021 public {r['form']} (timing run)", "t_end": fl(r["t_end"]), "h": fl(r["h"]), "status": r["status"], "error_reference": "none (timing row)",
                    "pos_final_error": float("nan"), "vel_final_error": float("nan"), "runtime_sec": fl(r["runtime_sec"]), "avg_iterations": fl(r["avg_iterations"]), "source_csv": "ra2021_public_timing_rows.csv"})
    order = {"single_pendulum": 0, "double_pendulum": 1, "four_link": 2, "slider_crank": 3}
    out.sort(key=lambda x: (order[x["model"]], x["method"], -x["h"]))
    return out


def main() -> int:
    started = time.perf_counter()
    ref = load_reference()
    print(f"reference: h={ref['h']:g}, {ref['steps']} steps, runtime {ref['runtime_sec']:.0f}s, constraint {ref['max_endpoint_constraint_norm']:.1e}", flush=True)
    alignment = alignment_rows()
    rows = []
    rows += public_2021_rows(ref)
    rows += public_2022_rows(ref)
    rows += gauss6_rows(ref)
    orders = {}
    for method in sorted({r["method"] for r in rows}):
        ok = [r for r in rows if r["method"] == method and r["status"] == "ok" and np.isfinite(r["pos_final_linf"])]
        hs = [r["h"] for r in ok]
        orders[method] = {"h": hs, "pos_pairwise": pairwise_orders(hs, [r["pos_final_linf"] for r in ok]), "vel_pairwise": pairwise_orders(hs, [r["vel_final_linf"] for r in ok])}
        if len(ok) >= 2:
            slope_p = np.polyfit(np.log(hs), np.log([r["pos_final_linf"] for r in ok]), 1)[0]; slope_v = np.polyfit(np.log(hs), np.log([r["vel_final_linf"] for r in ok]), 1)[0]
            orders[method].update({"pos_fit": float(slope_p), "vel_fit": float(slope_v)})
        print(method, {k: (round(v, 2) if isinstance(v, float) else v) for k, v in orders[method].items() if k.endswith("fit")})
    write_csv(RESULTS / "E5_double_pendulum.csv", rows)
    driven = driven_rows()
    write_csv(RESULTS / "E5_driven_public_horizon.csv", driven)
    write_json(RESULTS / "E5_public_baselines.json", {"schema": "e5-public-baselines-v1", "t_end": T_END, "h_values": H_VALUES,
                                                       "reference": {k: v for k, v in ref.items() if k not in ("pos", "vel")}, "reference_file": REFERENCE_NPZ.name,
                                                       "orders": orders, "model_alignment_check": alignment, "double_pendulum_rows": rows, "driven_rows": driven, "runtime_sec": time.perf_counter() - started})
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 3, figsize=(14, 3.9))
    styles = {"Gauss6/FullVA": dict(marker="o", color="C3", lw=1.8), "2021 public rA": dict(marker="s", color="C0"), "2021 public rp": dict(marker="^", color="C1"), "2021 public reps": dict(marker="v", color="C2"),
              "2022 half-implicit rA": dict(marker="D", color="C4"), "2022 half-implicit rA_half": dict(marker="P", color="C5")}
    for method, st in styles.items():
        ok = [r for r in rows if r["method"] == method and r["status"] == "ok" and np.isfinite(r["pos_final_linf"]) and r["pos_final_linf"] > 0]
        if not ok:
            continue
        hs = [r["h"] for r in ok]
        axes[0].loglog(hs, [r["pos_final_linf"] for r in ok], label=method, **st)
        axes[1].loglog(hs, [r["vel_final_linf"] for r in ok], label=method, **st)
        axes[2].loglog([r["runtime_sec"] for r in ok], [r["pos_final_linf"] for r in ok], label=method, **st)
    axes[0].set_xlabel("h"); axes[0].set_ylabel("final position error (L$^\\infty$)"); axes[0].set_title("double pendulum, T = 3: position")
    axes[1].set_xlabel("h"); axes[1].set_ylabel("final velocity error (L$^\\infty$)"); axes[1].set_title("velocity")
    axes[2].set_xlabel("wall time [s] (different implementations)"); axes[2].set_ylabel("final position error"); axes[2].set_title("work/precision (indicative)")
    for ax in axes: ax.grid(True, which="both", alpha=0.3)
    axes[0].legend(fontsize=7)
    fig.tight_layout(); fig.savefig(RESULTS / "E5_double_pendulum.png", dpi=160); plt.close(fig)
    print("E5 written", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
