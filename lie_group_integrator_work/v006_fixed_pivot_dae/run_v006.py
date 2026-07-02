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

from rigid_pendulum import (
    default_params,
    energy,
    estimate_order,
    integrate,
    initial_state,
    orientation_error,
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


def run_order() -> dict:
    params = default_params()
    t_final = 5.0
    hs = [0.2, 0.1, 0.05, 0.025]
    methods = ["lie_euler", "rkmk4", "gauss_lie4"]
    ref_h = 5.0 / 131072.0
    ref = integrate("rkmk4", ref_h, t_final, params)

    rows = []
    summary = {}
    for method in methods:
        orientation_errors = []
        omega_errors = []
        energy_errors = []
        runs = {}
        for h in hs:
            start = time.perf_counter()
            out = integrate(method, h, t_final, params)
            runtime = time.perf_counter() - start
            oerr = orientation_error(ref["R"], out["R"])
            werr = float(np.linalg.norm(ref["w"] - out["w"]))
            orientation_errors.append(oerr)
            omega_errors.append(werr)
            energy_errors.append(out["max_energy_relative_error"])
            row = {
                "method": method,
                "h": f"{h:.10g}",
                "steps": out["steps"],
                "orientation_error_rad": f"{oerr:.16e}",
                "omega_l2_error": f"{werr:.16e}",
                "max_energy_relative_error": f"{out['max_energy_relative_error']:.16e}",
                "max_constraint_norm": f"{out['max_constraint_norm']:.16e}",
                "max_velocity_constraint_norm": f"{out['max_velocity_constraint_norm']:.16e}",
                "max_dae_force_residual_norm": f"{out['max_dae_force_residual_norm']:.16e}",
                "max_dae_torque_residual_norm": f"{out['max_dae_torque_residual_norm']:.16e}",
                "max_orthogonality_fro": f"{out['max_orthogonality_fro']:.16e}",
                "total_newton_iterations": out["total_newton_iterations"],
                "runtime_sec": f"{runtime:.8e}",
            }
            rows.append(row)
            runs[str(h)] = {
                "orientation_error_rad": oerr,
                "omega_l2_error": werr,
                "max_energy_relative_error": out["max_energy_relative_error"],
                "max_constraint_norm": out["max_constraint_norm"],
                "max_velocity_constraint_norm": out["max_velocity_constraint_norm"],
                "max_dae_force_residual_norm": out["max_dae_force_residual_norm"],
                "max_dae_torque_residual_norm": out["max_dae_torque_residual_norm"],
                "max_orthogonality_fro": out["max_orthogonality_fro"],
                "total_newton_iterations": out["total_newton_iterations"],
                "runtime_sec": runtime,
            }
        summary[method] = {
            "orientation_observed_order": estimate_order(hs, orientation_errors),
            "omega_observed_order": estimate_order(hs, omega_errors),
            "energy_observed_order": estimate_order(hs, energy_errors),
            "runs": runs,
        }
    write_csv(RESULTS / "fixed_pivot_order.csv", rows)
    return {
        "t_final": t_final,
        "reference_method": "rkmk4",
        "reference_h": ref_h,
        "step_sizes": hs,
        "methods": summary,
    }


def run_long_time() -> dict:
    params = default_params()
    t_final = 100.0
    hs = [0.1, 0.05]
    methods = ["rkmk4", "gauss_lie4"]
    rows = []
    summary = {}
    for method in methods:
        runs = {}
        for h in hs:
            start = time.perf_counter()
            out = integrate(method, h, t_final, params)
            runtime = time.perf_counter() - start
            rows.append(
                {
                    "method": method,
                    "h": f"{h:.10g}",
                    "steps": out["steps"],
                    "max_energy_relative_error": f"{out['max_energy_relative_error']:.16e}",
                    "max_constraint_norm": f"{out['max_constraint_norm']:.16e}",
                    "max_velocity_constraint_norm": f"{out['max_velocity_constraint_norm']:.16e}",
                    "max_dae_force_residual_norm": f"{out['max_dae_force_residual_norm']:.16e}",
                    "max_dae_torque_residual_norm": f"{out['max_dae_torque_residual_norm']:.16e}",
                    "max_orthogonality_fro": f"{out['max_orthogonality_fro']:.16e}",
                    "total_newton_iterations": out["total_newton_iterations"],
                    "runtime_sec": f"{runtime:.8e}",
                }
            )
            runs[str(h)] = {
                "max_energy_relative_error": out["max_energy_relative_error"],
                "max_constraint_norm": out["max_constraint_norm"],
                "max_velocity_constraint_norm": out["max_velocity_constraint_norm"],
                "max_dae_force_residual_norm": out["max_dae_force_residual_norm"],
                "max_dae_torque_residual_norm": out["max_dae_torque_residual_norm"],
                "max_orthogonality_fro": out["max_orthogonality_fro"],
                "total_newton_iterations": out["total_newton_iterations"],
                "runtime_sec": runtime,
            }
        summary[method] = runs
    write_csv(RESULTS / "fixed_pivot_long_time.csv", rows)
    return {
        "t_final": t_final,
        "step_sizes": hs,
        "methods": summary,
    }


def plot_results(summary: dict) -> None:
    import matplotlib.pyplot as plt

    hs = summary["order"]["step_sizes"]
    plt.figure(figsize=(7.0, 4.5))
    for method, item in summary["order"]["methods"].items():
        errors = [item["runs"][str(h)]["orientation_error_rad"] for h in hs]
        plt.loglog(hs, errors, marker="o", label=method)
    plt.gca().invert_xaxis()
    plt.xlabel("step size h")
    plt.ylabel("orientation error [rad]")
    plt.title("Fixed-Pivot Rigid Body: Orientation Error")
    plt.grid(True, which="both", alpha=0.35)
    plt.legend()
    plt.tight_layout()
    plt.savefig(RESULTS / "fixed_pivot_orientation_order.png", dpi=180)
    plt.close()

    hs_long = summary["long_time"]["step_sizes"]
    plt.figure(figsize=(7.0, 4.5))
    for method, item in summary["long_time"]["methods"].items():
        errors = [item[str(h)]["max_energy_relative_error"] for h in hs_long]
        plt.loglog(hs_long, errors, marker="o", label=method)
    plt.gca().invert_xaxis()
    plt.xlabel("step size h")
    plt.ylabel("max relative energy drift")
    plt.title("Fixed-Pivot Rigid Body: 100s Energy Drift")
    plt.grid(True, which="both", alpha=0.35)
    plt.legend()
    plt.tight_layout()
    plt.savefig(RESULTS / "fixed_pivot_energy_drift.png", dpi=180)
    plt.close()


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    params = default_params()
    R0, w0 = initial_state()
    started = time.perf_counter()
    summary = {
        "version": "v006_fixed_pivot_dae",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "model": {
            "mass": params.mass,
            "J_com_diag": np.diag(params.J_com).tolist(),
            "J_pivot": params.J_pivot.tolist(),
            "s_com_to_pivot": params.s_com_to_pivot.tolist(),
            "gravity": params.gravity.tolist(),
            "initial_energy": energy(R0, w0, params),
            "constraint": "r + R s = 0",
        },
        "order": run_order(),
        "long_time": run_long_time(),
    }
    summary["runtime_sec"] = time.perf_counter() - started
    plot_results(summary)
    with (RESULTS / "summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True)

    g = summary["order"]["methods"]["gauss_lie4"]
    r = summary["order"]["methods"]["rkmk4"]
    g_long = summary["long_time"]["methods"]["gauss_lie4"]["0.05"]
    r_long = summary["long_time"]["methods"]["rkmk4"]["0.05"]
    report = [
        "# v006 Experiment Report",
        "",
        "Generated by `run_v006.py`.",
        "",
        "## Model",
        "",
        "- Single rigid body with fixed pivot constraint `r + R s = 0`.",
        "- The reduced SO(3) dynamics are equivalent to the constrained DAE; the script reconstructs the center-of-mass coordinates, pivot reaction/Lagrange multiplier, and DAE residuals.",
        "- This is still frictionless, but it is a real constrained rigid-body step beyond v005's unconstrained Euler top.",
        "",
        "## Order Results",
        "",
    ]
    for method, item in summary["order"]["methods"].items():
        finest = item["runs"]["0.025"]
        report.append(
            f"- `{method}`: orientation order {item['orientation_observed_order']:.3f}, "
            f"omega order {item['omega_observed_order']:.3f}; at h=0.025 orientation error "
            f"{finest['orientation_error_rad']:.3e}, omega error {finest['omega_l2_error']:.3e}."
        )
    report.extend(
        [
            "",
            "## Long-Time Constraint/DAE Checks",
            "",
            f"- `gauss_lie4` at h=0.05 over 100s: energy drift {g_long['max_energy_relative_error']:.3e}, max position constraint {g_long['max_constraint_norm']:.3e}, max velocity constraint {g_long['max_velocity_constraint_norm']:.3e}, max DAE force residual {g_long['max_dae_force_residual_norm']:.3e}, max DAE torque residual {g_long['max_dae_torque_residual_norm']:.3e}.",
            f"- `rkmk4` at h=0.05 over 100s: energy drift {r_long['max_energy_relative_error']:.3e}, max position constraint {r_long['max_constraint_norm']:.3e}, max velocity constraint {r_long['max_velocity_constraint_norm']:.3e}.",
            "",
            "## Interpretation",
            "",
            f"- `gauss_lie4` remains fourth order on this constrained rigid-body pendulum: orientation order {g['orientation_observed_order']:.3f}, omega order {g['omega_observed_order']:.3f}.",
            f"- It improves the long-time energy drift over explicit `rkmk4` in this prototype by a factor of {r_long['max_energy_relative_error'] / g_long['max_energy_relative_error']:.1f} at h=0.05.",
            "- Because the reduced formulation enforces `r + R s = 0` by construction, this version verifies the candidate under exact constraints but does not yet implement the full augmented collocation Newton system used by general multibody DAEs.",
            "- v007 should move from reduced fixed-pivot coordinates to an absolute-coordinate stage solve with explicit multipliers, using this model as the regression target before adding friction.",
            "",
            "## Plots",
            "",
            "- `fixed_pivot_orientation_order.png`",
            "- `fixed_pivot_energy_drift.png`",
            "",
        ]
    )
    (RESULTS / "v006_report.md").write_text("\n".join(report), encoding="utf-8")


if __name__ == "__main__":
    main()
