from __future__ import annotations

import csv
import importlib.util
import json
import os
import platform
import sys
import time
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", "/tmp/mplconfig")

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RESULTS = HERE / "results"
V019_PATH = ROOT / "v019_lambda_dependent_friction" / "run_v019.py"

CASES = {"lambda_smooth": 0.5, "lambda_sharp": 0.05}
TOLERANCES = [1.0e-4, 1.0e-5, 1.0e-6, 3.0e-7, 1.0e-7]
FIXED_RUNS = [
    ("gauss4_fixed_h0025", "lambda_gauss4_endpoint_jax", 0.025),
    ("gauss6_fixed_h0025", "lambda_gauss6_endpoint_jax", 0.025),
    ("gauss6_fixed_h00125", "lambda_gauss6_endpoint_jax", 0.0125),
]
T_FINAL = 1.0
REF_H = 0.00625
H_INITIAL = 0.1
H_MAX = 0.1
H_MIN = 1.0e-4
SAFETY = 0.85


def load_v019_module():
    spec = importlib.util.spec_from_file_location("v019_lambda", V019_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


v019 = load_v019_module()
qp = v019.qp


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def json_safe(obj: object) -> object:
    if isinstance(obj, dict):
        return {key: json_safe(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [json_safe(value) for value in obj]
    if isinstance(obj, tuple):
        return [json_safe(value) for value in obj]
    if isinstance(obj, float) and not np.isfinite(obj):
        return None
    return obj


def warm_jax(params) -> None:
    state = qp.initial_state(params)
    v019.endpoint_step_lambda(state, 0.025, params, n_stages=2)
    v019.endpoint_step_lambda(state, 0.025, params, n_stages=3)


def state_error(ref_state, state) -> tuple[float, float]:
    return (
        qp.orientation_error(qp.quat_to_rot(ref_state.p), qp.quat_to_rot(state.p)),
        float(np.linalg.norm(ref_state.w - state.w)),
    )


def embedded_error_norm(state4, state6, rot_tol: float, omega_tol: float) -> tuple[float, float, float]:
    rot_diff = qp.orientation_error(qp.quat_to_rot(state6.p), qp.quat_to_rot(state4.p))
    omega_diff = float(np.linalg.norm(state6.w - state4.w))
    err_norm = max(rot_diff / rot_tol, omega_diff / omega_tol)
    return err_norm, rot_diff, omega_diff


def next_step_size(h: float, err_norm: float, accepted: bool) -> float:
    if err_norm <= 1.0e-14:
        factor = 2.0
    else:
        factor = SAFETY * err_norm ** (-0.2)
    if accepted:
        factor = min(2.0, max(0.35, factor))
    else:
        factor = min(0.8, max(0.1, factor))
    return min(H_MAX, max(H_MIN, h * factor))


def adaptive_lambda_integrate(params, rot_tol: float, omega_tol: float) -> dict:
    state = qp.initial_state(params)
    h = H_INITIAL
    t = 0.0
    accepted_steps = 0
    rejected_steps = 0
    total_g4_iters = 0
    total_g6_iters = 0
    h_values = []
    err_values = []
    max_embedded_rot = 0.0
    max_embedded_omega = 0.0
    max_endpoint_constraint = 0.0
    max_endpoint_velocity_constraint = 0.0
    max_stage_constraint = 0.0
    max_stage_torque = 0.0
    max_lambda = 0.0
    max_power = -np.inf
    min_power = np.inf
    max_quat_unit = abs(np.linalg.norm(state.p) - 1.0)
    E0 = qp.energy_state(state, params)
    prev_energy = E0
    max_step_energy_increase = 0.0

    while t < T_FINAL - 1.0e-14:
        h = min(h, T_FINAL - t)
        if h < H_MIN * (1.0 - 1.0e-12):
            raise RuntimeError(f"adaptive step underflow at t={t:.16e}, h={h:.3e}")
        try:
            state6, n6, diag6 = v019.endpoint_step_lambda(state, h, params, n_stages=3)
            state4, n4, _diag4 = v019.endpoint_step_lambda(state, h, params, n_stages=2)
        except RuntimeError:
            rejected_steps += 1
            h = max(H_MIN, 0.5 * h)
            continue

        total_g6_iters += n6
        total_g4_iters += n4
        err_norm, rot_diff, omega_diff = embedded_error_norm(state4, state6, rot_tol, omega_tol)

        if err_norm <= 1.0 or h <= H_MIN * (1.0 + 1.0e-12):
            state = state6
            t += h
            accepted_steps += 1
            h_values.append(h)
            err_values.append(err_norm)
            max_embedded_rot = max(max_embedded_rot, rot_diff)
            max_embedded_omega = max(max_embedded_omega, omega_diff)
            max_stage_constraint = max(max_stage_constraint, diag6["max_stage_constraint_norm"])
            max_stage_torque = max(max_stage_torque, diag6["max_stage_torque_residual_norm"])
            max_lambda = max(max_lambda, diag6["lambda_norm_max"])
            max_power = max(max_power, diag6["max_stage_friction_power"])
            min_power = min(min_power, diag6["min_stage_friction_power"])
            max_quat_unit = max(max_quat_unit, diag6["max_quaternion_unit_error"])
            cn, cv = qp.constraint_norms(state, params)
            max_endpoint_constraint = max(max_endpoint_constraint, cn)
            max_endpoint_velocity_constraint = max(max_endpoint_velocity_constraint, cv)
            energy = qp.energy_state(state, params)
            max_step_energy_increase = max(max_step_energy_increase, energy - prev_energy)
            prev_energy = energy
            h = next_step_size(h, err_norm, accepted=True)
        else:
            rejected_steps += 1
            h = next_step_size(h, err_norm, accepted=False)

    final_energy = qp.energy_state(state, params)
    return {
        "state": state,
        "accepted_steps": accepted_steps,
        "rejected_steps": rejected_steps,
        "total_steps_attempted": accepted_steps + rejected_steps,
        "total_newton_iterations": total_g4_iters + total_g6_iters,
        "total_gauss4_newton_iterations": total_g4_iters,
        "total_gauss6_newton_iterations": total_g6_iters,
        "min_h": float(np.min(h_values)) if h_values else float("nan"),
        "max_h": float(np.max(h_values)) if h_values else float("nan"),
        "mean_h": float(np.mean(h_values)) if h_values else float("nan"),
        "median_h": float(np.median(h_values)) if h_values else float("nan"),
        "max_embedded_error_norm": float(np.max(err_values)) if err_values else float("nan"),
        "mean_embedded_error_norm": float(np.mean(err_values)) if err_values else float("nan"),
        "max_embedded_orientation_diff": max_embedded_rot,
        "max_embedded_omega_diff": max_embedded_omega,
        "max_endpoint_constraint_norm": max_endpoint_constraint,
        "max_endpoint_velocity_constraint_norm": max_endpoint_velocity_constraint,
        "max_stage_constraint_norm": max_stage_constraint,
        "max_stage_torque_residual_norm": max_stage_torque,
        "max_lambda_norm": max_lambda,
        "max_stage_friction_power": max_power,
        "min_stage_friction_power": min_power,
        "max_quaternion_unit_error": max_quat_unit,
        "final_energy_change": final_energy - E0,
        "final_energy_relative_change": (final_energy - E0) / max(abs(E0), 1.0e-30),
        "max_step_energy_increase": max_step_energy_increase,
    }


def fixed_run(label: str, method: str, h: float, params, ref_state, case_name: str) -> tuple[dict, dict]:
    start = time.perf_counter()
    out = v019.integrate_lambda(method, h, T_FINAL, params)
    runtime = time.perf_counter() - start
    rot_err, omega_err = state_error(ref_state, out["state"])
    row = {
        "case": case_name,
        "run_type": "fixed",
        "label": label,
        "method": method,
        "tolerance": "",
        "h": f"{h:.10g}",
        "accepted_steps": out["steps"],
        "rejected_steps": 0,
        "orientation_error_rad": f"{rot_err:.16e}",
        "omega_l2_error": f"{omega_err:.16e}",
        "runtime_sec": f"{runtime:.8e}",
        "total_newton_iterations": out["total_newton_iterations"],
        "min_h": f"{h:.16e}",
        "max_h": f"{h:.16e}",
        "mean_h": f"{h:.16e}",
        "max_embedded_error_norm": "",
        "max_lambda_norm": f"{out['max_lambda_norm']:.16e}",
        "max_stage_friction_power": f"{out['max_stage_friction_power']:.16e}",
        "max_endpoint_constraint_norm": f"{out['max_endpoint_constraint_norm']:.16e}",
        "max_endpoint_velocity_constraint_norm": f"{out['max_endpoint_velocity_constraint_norm']:.16e}",
        "final_energy_relative_change": f"{out['final_energy_relative_change']:.16e}",
        "max_step_energy_increase": f"{out['max_step_energy_increase']:.16e}",
    }
    summary = dict(out)
    summary.pop("state")
    summary.update(
        {
            "label": label,
            "method": method,
            "h": h,
            "orientation_error_rad": rot_err,
            "omega_l2_error": omega_err,
            "runtime_sec": runtime,
        }
    )
    return row, summary


def adaptive_run(tol: float, params, ref_state, case_name: str) -> tuple[dict, dict]:
    start = time.perf_counter()
    out = adaptive_lambda_integrate(params, rot_tol=tol, omega_tol=tol)
    runtime = time.perf_counter() - start
    rot_err, omega_err = state_error(ref_state, out["state"])
    row = {
        "case": case_name,
        "run_type": "adaptive",
        "label": f"adaptive_lambda_gauss64_tol{tol:.0e}",
        "method": "adaptive_lambda_gauss64_endpoint_jax",
        "tolerance": f"{tol:.1e}",
        "h": "",
        "accepted_steps": out["accepted_steps"],
        "rejected_steps": out["rejected_steps"],
        "orientation_error_rad": f"{rot_err:.16e}",
        "omega_l2_error": f"{omega_err:.16e}",
        "runtime_sec": f"{runtime:.8e}",
        "total_newton_iterations": out["total_newton_iterations"],
        "min_h": f"{out['min_h']:.16e}",
        "max_h": f"{out['max_h']:.16e}",
        "mean_h": f"{out['mean_h']:.16e}",
        "max_embedded_error_norm": f"{out['max_embedded_error_norm']:.16e}",
        "max_lambda_norm": f"{out['max_lambda_norm']:.16e}",
        "max_stage_friction_power": f"{out['max_stage_friction_power']:.16e}",
        "max_endpoint_constraint_norm": f"{out['max_endpoint_constraint_norm']:.16e}",
        "max_endpoint_velocity_constraint_norm": f"{out['max_endpoint_velocity_constraint_norm']:.16e}",
        "final_energy_relative_change": f"{out['final_energy_relative_change']:.16e}",
        "max_step_energy_increase": f"{out['max_step_energy_increase']:.16e}",
    }
    summary = dict(out)
    summary.pop("state")
    summary.update(
        {
            "label": row["label"],
            "method": row["method"],
            "tolerance": tol,
            "orientation_error_rad": rot_err,
            "omega_l2_error": omega_err,
            "runtime_sec": runtime,
        }
    )
    return row, summary


def run_experiment() -> dict:
    rows = []
    cases = {}
    for case_name, eps in CASES.items():
        params = v019.make_params(friction_eps=eps)
        ref = v019.integrate_lambda("lambda_gauss6_endpoint_jax", REF_H, T_FINAL, params)
        ref_state = ref["state"]
        warm_jax(params)
        fixed_summaries = []
        adaptive_summaries = []
        for label, method, h in FIXED_RUNS:
            row, summary = fixed_run(label, method, h, params, ref_state, case_name)
            rows.append(row)
            fixed_summaries.append(summary)
        for tol in TOLERANCES:
            row, summary = adaptive_run(tol, params, ref_state, case_name)
            rows.append(row)
            adaptive_summaries.append(summary)

        baseline = next(item for item in fixed_summaries if item["label"] == "gauss6_fixed_h0025")
        fine_fixed = next(item for item in fixed_summaries if item["label"] == "gauss6_fixed_h00125")
        best_adaptive = min(adaptive_summaries, key=lambda item: item["orientation_error_rad"])
        fastest_better = [
            item
            for item in adaptive_summaries
            if item["orientation_error_rad"] < baseline["orientation_error_rad"]
            and item["runtime_sec"] <= 1.25 * baseline["runtime_sec"]
        ]
        cases[case_name] = {
            "friction_eps": eps,
            "reference_method": "lambda_gauss6_endpoint_jax",
            "reference_h": REF_H,
            "fixed": fixed_summaries,
            "adaptive": adaptive_summaries,
            "gauss6_h0025_baseline": baseline,
            "gauss6_h00125_fine": fine_fixed,
            "best_adaptive": best_adaptive,
            "fastest_adaptive_better_than_gauss6_h0025": min(
                fastest_better, key=lambda item: item["runtime_sec"]
            )
            if fastest_better
            else None,
        }
    write_csv(RESULTS / "adaptive_lambda_runs.csv", rows)
    return {"t_final": T_FINAL, "cases": cases, "tolerances": TOLERANCES}


def plot_results(summary: dict) -> None:
    import matplotlib.pyplot as plt

    plt.figure(figsize=(7.8, 4.8))
    markers = {"fixed": "o", "adaptive": "s"}
    for case_name, case in summary["cases"].items():
        for group_name in ["fixed", "adaptive"]:
            group = case[group_name]
            xs = [item["runtime_sec"] for item in group]
            ys = [item["orientation_error_rad"] for item in group]
            labels = [item["label"] for item in group]
            plt.loglog(xs, ys, marker=markers[group_name], linestyle="none", label=f"{case_name} {group_name}")
            for x, y, label in zip(xs, ys, labels):
                short = label.replace("adaptive_lambda_gauss64_", "adap_").replace("gauss6_fixed_", "g6_")
                short = short.replace("gauss4_fixed_", "g4_")
                plt.annotate(short, (x, y), fontsize=7, xytext=(3, 3), textcoords="offset points")
    plt.xlabel("runtime seconds")
    plt.ylabel("orientation error rad")
    plt.title("Adaptive Lambda-Friction Gauss64 vs Fixed Steps")
    plt.grid(True, which="both", alpha=0.35)
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(RESULTS / "adaptive_lambda_error_runtime.png", dpi=180)
    plt.close()


def write_report(summary: dict) -> None:
    lines = [
        "# v020 Experiment Report",
        "",
        "Generated by `run_v020.py`.",
        "",
        "## Purpose",
        "",
        "- Combine v015's embedded adaptive Gauss64 controller with v019's multiplier-dependent Stribeck-style friction residual.",
        "- Test whether adaptive stepping improves high-accuracy lambda-dependent sharp-friction cases more efficiently than globally halving the fixed Gauss6 step.",
        "- JAX kernels are warmed before timed fixed/adaptive runs.",
        "",
        "## Results",
        "",
    ]
    for case_name, case in summary["cases"].items():
        baseline = case["gauss6_h0025_baseline"]
        fine = case["gauss6_h00125_fine"]
        best = case["best_adaptive"]
        fastest = case["fastest_adaptive_better_than_gauss6_h0025"]
        value_vs_fine = (fine["orientation_error_rad"] / best["orientation_error_rad"]) / max(
            best["runtime_sec"] / fine["runtime_sec"], 1.0e-30
        )
        error_ratio_vs_baseline = best["orientation_error_rad"] / baseline["orientation_error_rad"]
        runtime_ratio_vs_baseline = best["runtime_sec"] / baseline["runtime_sec"]
        error_ratio_vs_fine = best["orientation_error_rad"] / fine["orientation_error_rad"]
        runtime_ratio_vs_fine = best["runtime_sec"] / fine["runtime_sec"]
        lines.append(
            f"- `{case_name}` baseline Gauss6 h=0.025: error {baseline['orientation_error_rad']:.3e}, "
            f"runtime {baseline['runtime_sec']:.3f}s."
        )
        lines.append(
            f"- `{case_name}` finer fixed Gauss6 h=0.0125: error {fine['orientation_error_rad']:.3e}, "
            f"runtime {fine['runtime_sec']:.3f}s."
        )
        lines.append(
            f"- `{case_name}` best adaptive: `{best['label']}` error {best['orientation_error_rad']:.3e}, "
            f"runtime {best['runtime_sec']:.3f}s, accepted/rejected {best['accepted_steps']}/{best['rejected_steps']}, "
            f"h range [{best['min_h']:.3e}, {best['max_h']:.3e}]."
        )
        lines.append(
            f"- `{case_name}` best adaptive ratios: error/runtime vs Gauss6 h=0.025 = "
            f"{error_ratio_vs_baseline:.2e}/{runtime_ratio_vs_baseline:.2e}; "
            f"error/runtime vs Gauss6 h=0.0125 = {error_ratio_vs_fine:.2e}/{runtime_ratio_vs_fine:.2e}."
        )
        lines.append(
            f"- `{case_name}` best adaptive value ratio against fixed h=0.0125: {value_vs_fine:.2e} "
            f"(above 1 would mean lower error per extra runtime than global halving)."
        )
        if fastest is None:
            lines.append(
                f"- `{case_name}` no adaptive tolerance beat Gauss6 h=0.025 while staying within 1.25x runtime."
            )
        else:
            lines.append(
                f"- `{case_name}` fastest adaptive better than Gauss6 h=0.025 within 1.25x runtime: "
                f"`{fastest['label']}` with error {fastest['orientation_error_rad']:.3e} and runtime "
                f"{fastest['runtime_sec']:.3f}s."
            )
        if error_ratio_vs_baseline > 1.0:
            lines.append(
                f"- `{case_name}` conclusion: adaptive is not the right default here; the fixed Gauss6 "
                f"coarse step is already more accurate."
            )
        elif error_ratio_vs_fine < 1.0 and runtime_ratio_vs_fine <= 1.5:
            lines.append(
                f"- `{case_name}` conclusion: adaptive is a real win; it beats globally halving Gauss6 "
                f"by {1.0 / error_ratio_vs_fine:.1f}x in error at {runtime_ratio_vs_fine:.2f}x runtime."
            )
        else:
            lines.append(
                f"- `{case_name}` conclusion: adaptive improves the coarse fixed step, but global "
                f"halving remains the stronger high-accuracy reference."
            )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Adaptive lambda-Gauss64 tests whether the v015 near-nonsmooth strategy survives the more realistic v019 friction/multiplier coupling.",
            "- The smooth lambda-friction case is not an adaptive-step win in this benchmark: fixed Gauss6 h=0.025 is already extremely accurate and cheaper than driving an embedded controller to comparable tolerances.",
            "- The sharp lambda-friction case is the useful target: adaptive stepping can spend small steps near the high-curvature friction transition and larger steps elsewhere, so it can beat the coarse fixed Gauss6 run at similar runtime.",
            "- If the adaptive value ratio against fixed h=0.0125 stays below one, global halving is still the simpler high-accuracy choice for that case; adaptive is then a practical coarse-step improvement rather than the final accuracy-per-cost winner.",
            "- The method is still a smooth regularized-friction strategy; it is not a complementarity/contact solver.",
            "",
            "## Outputs",
            "",
            "- `adaptive_lambda_runs.csv`",
            "- `summary_v020.json`",
            "- `adaptive_lambda_error_runtime.png`",
            "",
        ]
    )
    (RESULTS / "v020_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    experiment = run_experiment()
    plot_results(experiment)
    summary = {
        "version": "v020_adaptive_lambda_friction",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "model": {
            "cases": CASES,
            "tolerances": TOLERANCES,
            "fixed_runs": FIXED_RUNS,
            "t_final": T_FINAL,
            "reference_h": REF_H,
            "h_initial": H_INITIAL,
            "h_max": H_MAX,
            "h_min": H_MIN,
        },
        "experiment": experiment,
        "runtime_sec": time.perf_counter() - started,
    }
    with (RESULTS / "summary_v020.json").open("w", encoding="utf-8") as f:
        json.dump(json_safe(summary), f, indent=2, sort_keys=True)
    write_report(experiment)


if __name__ == "__main__":
    main()
