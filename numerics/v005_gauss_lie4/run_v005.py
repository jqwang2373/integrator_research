from __future__ import annotations

import csv
import json
import os
import platform
import time
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", "/tmp/mplconfig")

import numpy as np

from so3_integrators import (
    determinant_error,
    estimate_order,
    integrate_euler_top,
    integrate_orientation,
    orientation_error,
    orthogonality_error,
)


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def plot_results(summary: dict) -> None:
    import matplotlib.pyplot as plt

    hs = summary["euler_top_order"]["step_sizes"]
    plt.figure(figsize=(7.0, 4.5))
    for method, item in summary["euler_top_order"]["methods"].items():
        errors = [item["runs"][str(h)]["orientation_error_rad"] for h in hs]
        plt.loglog(hs, errors, marker="o", label=method)
    plt.gca().invert_xaxis()
    plt.xlabel("step size h")
    plt.ylabel("orientation error [rad]")
    plt.title("Euler Top Short-Time Orientation Error")
    plt.grid(True, which="both", alpha=0.35)
    plt.legend()
    plt.tight_layout()
    plt.savefig(RESULTS / "euler_top_orientation_order.png", dpi=180)
    plt.close()

    hs_long = [0.2, 0.1, 0.05]
    plt.figure(figsize=(7.0, 4.5))
    for method, items in summary["euler_top_invariants"]["methods"].items():
        errors = [items[str(h)]["max_spatial_momentum_vector_error"] for h in hs_long]
        plt.loglog(hs_long, errors, marker="o", label=method)
    plt.gca().invert_xaxis()
    plt.xlabel("step size h")
    plt.ylabel("max spatial momentum vector drift")
    plt.title("Euler Top 100s Spatial Momentum Drift")
    plt.grid(True, which="both", alpha=0.35)
    plt.legend()
    plt.tight_layout()
    plt.savefig(RESULTS / "euler_top_spatial_momentum_drift.png", dpi=180)
    plt.close()


def run_kinematic_order() -> dict:
    t_final = 4.0
    hs = [0.25, 0.125, 0.0625, 0.03125, 0.015625]
    methods = ["lie_euler", "exp_midpoint", "cf4", "rkmk4", "matrix_rk4"]

    ref_h = 4.0 / 32768.0
    ref = integrate_orientation("rkmk4", ref_h, t_final)

    rows = []
    by_method = {}
    for method in methods:
        method_errors = []
        for h in hs:
            start = time.perf_counter()
            R = integrate_orientation(method, h, t_final)
            runtime = time.perf_counter() - start
            err = orientation_error(ref, R)
            method_errors.append(err)
            rows.append(
                {
                    "method": method,
                    "h": f"{h:.10g}",
                    "steps": int(round(t_final / h)),
                    "orientation_error_rad": f"{err:.16e}",
                    "orthogonality_fro": f"{orthogonality_error(R):.16e}",
                    "determinant_abs_error": f"{determinant_error(R):.16e}",
                    "runtime_sec": f"{runtime:.8e}",
                }
            )
        by_method[method] = {
            "observed_order": estimate_order(hs, method_errors),
            "errors": method_errors,
        }

    write_csv(RESULTS / "kinematic_order.csv", rows)
    return {
        "t_final": t_final,
        "reference_method": "rkmk4",
        "reference_h": ref_h,
        "step_sizes": hs,
        "methods": {
            name: {
                "observed_order": val["observed_order"],
                "finest_error_rad": val["errors"][-1],
                "coarsest_error_rad": val["errors"][0],
            }
            for name, val in by_method.items()
        },
    }


def run_euler_top_invariants() -> dict:
    inertia = np.diag([1.0, 2.0, 3.5])
    w0 = np.array([0.9, 0.35, 1.1])
    t_final = 100.0
    hs = [0.2, 0.1, 0.05]
    methods = ["rkmk4", "lie_midpoint", "lie_midpoint_yoshida4", "gauss_lie4"]

    rows = []
    summary = {}
    for method in methods:
        method_summary = {}
        for h in hs:
            start = time.perf_counter()
            out = integrate_euler_top(method, h, t_final, inertia, w0)
            runtime = time.perf_counter() - start
            rows.append(
                {
                    "method": method,
                    "h": f"{h:.10g}",
                    "steps": out["steps"],
                    "max_energy_relative_error": f"{out['max_energy_rel']:.16e}",
                    "max_body_momentum_norm_relative_error": f"{out['max_body_momentum_rel']:.16e}",
                    "max_spatial_momentum_vector_error": f"{out['max_spatial_momentum_abs']:.16e}",
                    "max_orthogonality_fro": f"{out['max_orthogonality_error']:.16e}",
                    "total_newton_iterations": out["total_newton_iterations"],
                    "runtime_sec": f"{runtime:.8e}",
                }
            )
            method_summary[str(h)] = {
                "max_energy_relative_error": out["max_energy_rel"],
                "max_body_momentum_norm_relative_error": out["max_body_momentum_rel"],
                "max_spatial_momentum_vector_error": out["max_spatial_momentum_abs"],
                "max_orthogonality_fro": out["max_orthogonality_error"],
                "total_newton_iterations": out["total_newton_iterations"],
                "runtime_sec": runtime,
            }
        summary[method] = method_summary

    write_csv(RESULTS / "euler_top_invariants.csv", rows)
    return {
        "t_final": t_final,
        "inertia_diag": np.diag(inertia).tolist(),
        "w0": w0.tolist(),
        "methods": summary,
    }


def run_euler_top_order() -> dict:
    inertia = np.diag([1.0, 2.0, 3.5])
    w0 = np.array([0.9, 0.35, 1.1])
    t_final = 10.0
    hs = [0.4, 0.2, 0.1, 0.05]
    methods = ["rkmk4", "lie_midpoint", "lie_midpoint_yoshida4", "gauss_lie4"]

    ref_h = 10.0 / 32768.0
    ref = integrate_euler_top("rkmk4", ref_h, t_final, inertia, w0)

    rows = []
    summary = {}
    for method in methods:
        orientation_errors = []
        omega_errors = []
        method_summary = {}
        for h in hs:
            start = time.perf_counter()
            out = integrate_euler_top(method, h, t_final, inertia, w0)
            runtime = time.perf_counter() - start
            orient_err = orientation_error(ref["R"], out["R"])
            omega_err = float(np.linalg.norm(ref["w"] - out["w"]))
            orientation_errors.append(orient_err)
            omega_errors.append(omega_err)
            rows.append(
                {
                    "method": method,
                    "h": f"{h:.10g}",
                    "steps": out["steps"],
                    "orientation_error_rad": f"{orient_err:.16e}",
                    "omega_l2_error": f"{omega_err:.16e}",
                    "max_energy_relative_error": f"{out['max_energy_rel']:.16e}",
                    "max_body_momentum_norm_relative_error": f"{out['max_body_momentum_rel']:.16e}",
                    "max_spatial_momentum_vector_error": f"{out['max_spatial_momentum_abs']:.16e}",
                    "total_newton_iterations": out["total_newton_iterations"],
                    "runtime_sec": f"{runtime:.8e}",
                }
            )
            method_summary[str(h)] = {
                "orientation_error_rad": orient_err,
                "omega_l2_error": omega_err,
                "max_energy_relative_error": out["max_energy_rel"],
                "max_body_momentum_norm_relative_error": out["max_body_momentum_rel"],
                "max_spatial_momentum_vector_error": out["max_spatial_momentum_abs"],
                "total_newton_iterations": out["total_newton_iterations"],
                "runtime_sec": runtime,
            }
        summary[method] = {
            "orientation_observed_order": estimate_order(hs, orientation_errors),
            "omega_observed_order": estimate_order(hs, omega_errors),
            "runs": method_summary,
        }

    write_csv(RESULTS / "euler_top_order.csv", rows)
    return {
        "t_final": t_final,
        "reference_method": "rkmk4",
        "reference_h": ref_h,
        "inertia_diag": np.diag(inertia).tolist(),
        "w0": w0.tolist(),
        "step_sizes": hs,
        "methods": summary,
    }


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    summary = {
        "version": "v005_gauss_lie4",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "kinematic_order": run_kinematic_order(),
        "euler_top_order": run_euler_top_order(),
        "euler_top_invariants": run_euler_top_invariants(),
    }
    summary["runtime_sec"] = time.perf_counter() - started
    plot_results(summary)
    with (RESULTS / "summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True)

    h_key = "0.05"
    order_methods = summary["euler_top_order"]["methods"]
    invariant_methods = summary["euler_top_invariants"]["methods"]
    gauss_order = order_methods["gauss_lie4"]
    gauss_long = invariant_methods["gauss_lie4"][h_key]
    rkmk_long = invariant_methods["rkmk4"][h_key]
    yoshida_long = invariant_methods["lie_midpoint_yoshida4"][h_key]
    gauss_vs_rkmk_cost = gauss_long["runtime_sec"] / rkmk_long["runtime_sec"]
    gauss_vs_yoshida_cost = gauss_long["runtime_sec"] / yoshida_long["runtime_sec"]

    report = [
        "# v005 Experiment Report",
        "",
        "Generated by `run_v005.py`.",
        "",
        "Delta from v004: add `gauss_lie4`, a two-stage Gauss-Legendre body-angular-velocity solve plus right-action CF4 attitude reconstruction.",
        "",
        "## Literature Position",
        "",
        "- The 2026 Chaturvedi/Sandu/Sandu paper targets higher-order index-3 DAE integration with friction using Lie-group time finite elements.",
        "- Web searches on 2026-05-26 for the title/DOI did not expose reliable forward citations yet, so this version follows the paper's reference trail instead.",
        "- The paper's references emphasize Munthe-Kaas high-order Lie methods, Wieloch-Arnold BDF Lie-group constrained mechanics, and SBEL/Negrut rA baselines; the v005 candidate instead tests a collocation-like nonnegative-stage direction.",
        "",
        "## Current Best Candidate",
        "",
        f"- `gauss_lie4` is the best current smooth-mechanics candidate in this local study: orientation order {gauss_order['orientation_observed_order']:.3f}, omega order {gauss_order['omega_observed_order']:.3f}.",
        f"- At h={h_key} over 100s, `gauss_lie4` gives energy drift {gauss_long['max_energy_relative_error']:.3e}, body momentum-norm drift {gauss_long['max_body_momentum_norm_relative_error']:.3e}, and spatial momentum-vector drift {gauss_long['max_spatial_momentum_vector_error']:.3e}.",
        f"- Cost caveat: in the 100s h={h_key} run, `gauss_lie4` was {gauss_vs_rkmk_cost:.1f}x the runtime of explicit `rkmk4` and {gauss_vs_yoshida_cost:.1f}x the runtime of `lie_midpoint_yoshida4` in this Python prototype.",
        "",
        "## Kinematic SO(3) Order",
        "",
    ]
    for method, item in summary["kinematic_order"]["methods"].items():
        report.append(
            f"- `{method}`: observed order {item['observed_order']:.3f}, "
            f"finest error {item['finest_error_rad']:.3e} rad."
        )
    report.extend(["", "## Torque-Free Rigid Body Order", ""])
    for method, item in summary["euler_top_order"]["methods"].items():
        finest = item["runs"]["0.05"]
        report.append(
            f"- `{method}`: orientation order {item['orientation_observed_order']:.3f}, "
            f"omega order {item['omega_observed_order']:.3f}; at h=0.05 orientation error "
            f"{finest['orientation_error_rad']:.3e} rad, omega error {finest['omega_l2_error']:.3e}."
        )

    report.extend(["", "## Torque-Free Rigid Body Long-Time Invariants", ""])
    finest_h = "0.05"
    for method, items in summary["euler_top_invariants"]["methods"].items():
        item = items[finest_h]
        report.append(
            f"- `{method}` at h={finest_h}: max relative energy drift "
            f"{item['max_energy_relative_error']:.3e}, body momentum-norm drift "
            f"{item['max_body_momentum_norm_relative_error']:.3e}, spatial momentum-vector drift "
            f"{item['max_spatial_momentum_vector_error']:.3e}."
        )
    report.extend(
        [
            "",
            "## Plots",
            "",
            "- `euler_top_orientation_order.png`",
            "- `euler_top_spatial_momentum_drift.png`",
            "",
            "## Provisional Interpretation",
            "",
            "- For pure prescribed-omega kinematics, `rkmk4` and `cf4` are the relevant high-order candidates.",
            "- For smooth conservative rigid-body dynamics, `gauss_lie4` now supersedes `lie_midpoint_yoshida4` in this benchmark: better fourth-order behavior, better spatial momentum drift, and no backward composition substep.",
            "- The next serious DAE candidate should embed this style of Gauss/collocation Lie update into an index-3 constrained solve with Lagrange multipliers and friction forces.",
            "",
            "## Source Links",
            "",
            "- Chaturvedi/Sandu/Sandu 2026 Springer article: https://link.springer.com/article/10.1007/s11044-026-10153-w",
            "- SBEL/Negrut reproducibility repository: https://github.com/uwsbel/sbel-reproducibility/tree/master/2021/ASME/rA-formulation",
            "- Bogfjellmo/Marthinsen high-order symplectic partitioned Lie group methods: https://arxiv.org/abs/1303.5654",
            "- Gauss collocation invariant-preserving context: https://epubs.siam.org/doi/10.1137/110856617",
            "",
        ]
    )
    (RESULTS / "v005_report.md").write_text("\n".join(report), encoding="utf-8")


if __name__ == "__main__":
    main()
