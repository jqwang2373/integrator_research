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

from absolute_pendulum import (
    default_params,
    energy_state,
    estimate_order,
    initial_state,
    integrate,
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
    t_final = 2.0
    hs = [0.2, 0.1, 0.05]
    methods = [
        "reduced_rkmk4",
        "absolute_gauss_lie4",
        "absolute_gauss_lie4_projected",
        "absolute_gauss_lie4_vc_projected",
        "absolute_gauss_lie4_acc_projected",
    ]
    ref = integrate("reduced_rkmk4", 2.0 / 131072.0, t_final, params)
    rows = []
    summary = {}
    for method in methods:
        orientation_errors = []
        omega_errors = []
        energy_errors = []
        endpoint_constraints = []
        runs = {}
        for h in hs:
            start = time.perf_counter()
            out = integrate(
                "absolute_gauss_lie4_acc"
                if method.startswith("absolute_gauss_lie4_acc")
                else "absolute_gauss_lie4_vc"
                if method.startswith("absolute_gauss_lie4_vc")
                else ("absolute_gauss_lie4" if method.startswith("absolute") else method),
                h,
                t_final,
                params,
                project_endpoint=method.endswith("projected"),
            )
            runtime = time.perf_counter() - start
            state = out["state"]
            ref_state = ref["state"]
            oerr = orientation_error(ref_state.R, state.R)
            werr = float(np.linalg.norm(ref_state.w - state.w))
            orientation_errors.append(oerr)
            omega_errors.append(werr)
            energy_errors.append(out["max_energy_relative_error"])
            endpoint_constraints.append(out["max_endpoint_constraint_norm"])
            rows.append(
                {
                    "method": method,
                    "h": f"{h:.10g}",
                    "steps": out["steps"],
                    "orientation_error_rad": f"{oerr:.16e}",
                    "omega_l2_error": f"{werr:.16e}",
                    "max_energy_relative_error": f"{out['max_energy_relative_error']:.16e}",
                    "max_endpoint_constraint_norm": f"{out['max_endpoint_constraint_norm']:.16e}",
                    "max_endpoint_velocity_constraint_norm": f"{out['max_endpoint_velocity_constraint_norm']:.16e}",
                    "max_stage_constraint_norm": f"{out['max_stage_constraint_norm']:.16e}",
                    "max_stage_force_residual_norm": f"{out['max_stage_force_residual_norm']:.16e}",
                    "max_stage_torque_residual_norm": f"{out['max_stage_torque_residual_norm']:.16e}",
                    "max_lambda_norm": f"{out['max_lambda_norm']:.16e}",
                    "total_newton_iterations": out["total_newton_iterations"],
                    "runtime_sec": f"{runtime:.8e}",
                }
            )
            runs[str(h)] = {
                "orientation_error_rad": oerr,
                "omega_l2_error": werr,
                "max_energy_relative_error": out["max_energy_relative_error"],
                "max_endpoint_constraint_norm": out["max_endpoint_constraint_norm"],
                "max_endpoint_velocity_constraint_norm": out["max_endpoint_velocity_constraint_norm"],
                "max_stage_constraint_norm": out["max_stage_constraint_norm"],
                "max_stage_force_residual_norm": out["max_stage_force_residual_norm"],
                "max_stage_torque_residual_norm": out["max_stage_torque_residual_norm"],
                "max_lambda_norm": out["max_lambda_norm"],
                "total_newton_iterations": out["total_newton_iterations"],
                "runtime_sec": runtime,
            }
        summary[method] = {
            "orientation_observed_order": estimate_order(hs, orientation_errors),
            "omega_observed_order": estimate_order(hs, omega_errors),
            "energy_observed_order": estimate_order(hs, energy_errors),
            "endpoint_constraint_observed_order": estimate_order(hs, endpoint_constraints),
            "runs": runs,
        }
    write_csv(RESULTS / "absolute_dae_order.csv", rows)
    return {
        "t_final": t_final,
        "reference_method": "reduced_rkmk4",
        "reference_h": 2.0 / 131072.0,
        "step_sizes": hs,
        "methods": summary,
    }


def run_medium_time() -> dict:
    params = default_params()
    t_final = 20.0
    hs = [0.1, 0.05]
    methods = [
        "reduced_rkmk4",
        "absolute_gauss_lie4_projected",
        "absolute_gauss_lie4_vc_projected",
        "absolute_gauss_lie4_acc_projected",
    ]
    rows = []
    summary = {}
    for method in methods:
        runs = {}
        for h in hs:
            start = time.perf_counter()
            out = integrate(
                "absolute_gauss_lie4_acc"
                if method.startswith("absolute_gauss_lie4_acc")
                else "absolute_gauss_lie4_vc"
                if method.startswith("absolute_gauss_lie4_vc")
                else ("absolute_gauss_lie4" if method.startswith("absolute") else method),
                h,
                t_final,
                params,
                project_endpoint=method.endswith("projected"),
            )
            runtime = time.perf_counter() - start
            rows.append(
                {
                    "method": method,
                    "h": f"{h:.10g}",
                    "steps": out["steps"],
                    "max_energy_relative_error": f"{out['max_energy_relative_error']:.16e}",
                    "max_endpoint_constraint_norm": f"{out['max_endpoint_constraint_norm']:.16e}",
                    "max_endpoint_velocity_constraint_norm": f"{out['max_endpoint_velocity_constraint_norm']:.16e}",
                    "max_stage_constraint_norm": f"{out['max_stage_constraint_norm']:.16e}",
                    "max_stage_force_residual_norm": f"{out['max_stage_force_residual_norm']:.16e}",
                    "max_stage_torque_residual_norm": f"{out['max_stage_torque_residual_norm']:.16e}",
                    "max_lambda_norm": f"{out['max_lambda_norm']:.16e}",
                    "total_newton_iterations": out["total_newton_iterations"],
                    "runtime_sec": f"{runtime:.8e}",
                }
            )
            runs[str(h)] = {
                "max_energy_relative_error": out["max_energy_relative_error"],
                "max_endpoint_constraint_norm": out["max_endpoint_constraint_norm"],
                "max_endpoint_velocity_constraint_norm": out["max_endpoint_velocity_constraint_norm"],
                "max_stage_constraint_norm": out["max_stage_constraint_norm"],
                "max_stage_force_residual_norm": out["max_stage_force_residual_norm"],
                "max_stage_torque_residual_norm": out["max_stage_torque_residual_norm"],
                "max_lambda_norm": out["max_lambda_norm"],
                "total_newton_iterations": out["total_newton_iterations"],
                "runtime_sec": runtime,
            }
        summary[method] = runs
    write_csv(RESULTS / "absolute_dae_medium_time.csv", rows)
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
    plt.title("Absolute DAE Stage Solve: Orientation Error")
    plt.grid(True, which="both", alpha=0.35)
    plt.legend()
    plt.tight_layout()
    plt.savefig(RESULTS / "absolute_dae_orientation_order.png", dpi=180)
    plt.close()

    plt.figure(figsize=(7.0, 4.5))
    for method in [
        "absolute_gauss_lie4",
        "absolute_gauss_lie4_projected",
        "absolute_gauss_lie4_vc_projected",
        "absolute_gauss_lie4_acc_projected",
    ]:
        item = summary["order"]["methods"][method]
        errors = [item["runs"][str(h)]["max_endpoint_constraint_norm"] for h in hs]
        plt.loglog(hs, errors, marker="o", label=method)
    plt.gca().invert_xaxis()
    plt.xlabel("step size h")
    plt.ylabel("max endpoint constraint norm")
    plt.title("Endpoint Constraint Drift")
    plt.grid(True, which="both", alpha=0.35)
    plt.legend()
    plt.tight_layout()
    plt.savefig(RESULTS / "absolute_dae_constraint_drift.png", dpi=180)
    plt.close()


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    params = default_params()
    state0 = initial_state(params)
    started = time.perf_counter()
    summary = {
        "version": "v007_absolute_gauss_dae",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "model": {
            "mass": params.mass,
            "J_com_diag": np.diag(params.J_com).tolist(),
            "s_com_to_pivot": params.s_com_to_pivot.tolist(),
            "gravity": params.gravity.tolist(),
            "initial_energy": energy_state(state0, params),
            "constraint": "r + R s = 0",
            "stage_unknowns": "u_i, r_i, v_i, omega_i, a_i, alpha_i, lambda_i for i=1,2",
        },
        "order": run_order(),
        "medium_time": run_medium_time(),
    }
    summary["runtime_sec"] = time.perf_counter() - started
    plot_results(summary)
    with (RESULTS / "summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True)

    raw = summary["order"]["methods"]["absolute_gauss_lie4"]
    proj = summary["order"]["methods"]["absolute_gauss_lie4_projected"]
    vc = summary["order"]["methods"]["absolute_gauss_lie4_vc_projected"]
    acc = summary["order"]["methods"]["absolute_gauss_lie4_acc_projected"]
    raw_fine = raw["runs"]["0.05"]
    proj_fine = proj["runs"]["0.05"]
    vc_fine = vc["runs"]["0.05"]
    acc_fine = acc["runs"]["0.05"]
    medium = summary["medium_time"]["methods"]["absolute_gauss_lie4_acc_projected"]["0.05"]
    report = [
        "# v007 Experiment Report",
        "",
        "Generated by `run_v007.py`.",
        "",
        "## Model and Solver",
        "",
        "- Fixed-pivot rigid body in absolute coordinates with constraint `r + R s = 0`.",
        "- Each two-stage Gauss step solves a 42-variable nonlinear system containing stage pose increments, positions, velocities, accelerations, angular accelerations, and Lagrange multipliers.",
        "- Stage equations enforce Lie kinematics, translational dynamics, rotational dynamics, and stage position constraints.",
        "- Four variants are reported: raw position-stage constraints, projected position-stage constraints, projected position+velocity-stage constraints (`vc`), and projected position+velocity+acceleration-stage constraints (`acc`).",
        "",
        "## Short-Time Order",
        "",
    ]
    for method, item in summary["order"]["methods"].items():
        finest = item["runs"]["0.05"]
        report.append(
            f"- `{method}`: orientation order {item['orientation_observed_order']:.3f}, "
            f"omega order {item['omega_observed_order']:.3f}; at h=0.05 orientation error "
            f"{finest['orientation_error_rad']:.3e}, endpoint constraint {finest['max_endpoint_constraint_norm']:.3e}."
        )
    report.extend(
        [
            "",
            "## Constraint and Multiplier Findings",
            "",
            f"- Raw `absolute_gauss_lie4` at h=0.05: stage constraint {raw_fine['max_stage_constraint_norm']:.3e}, endpoint constraint {raw_fine['max_endpoint_constraint_norm']:.3e}, max stage force residual {raw_fine['max_stage_force_residual_norm']:.3e}, max stage torque residual {raw_fine['max_stage_torque_residual_norm']:.3e}.",
            f"- Projected `absolute_gauss_lie4` at h=0.05: endpoint constraint {proj_fine['max_endpoint_constraint_norm']:.3e}, endpoint velocity constraint {proj_fine['max_endpoint_velocity_constraint_norm']:.3e}, max lambda norm {proj_fine['max_lambda_norm']:.3e}.",
            f"- Projected `absolute_gauss_lie4_vc` at h=0.05: orientation error {vc_fine['orientation_error_rad']:.3e}, endpoint constraint {vc_fine['max_endpoint_constraint_norm']:.3e}, endpoint velocity constraint {vc_fine['max_endpoint_velocity_constraint_norm']:.3e}, max lambda norm {vc_fine['max_lambda_norm']:.3e}.",
            f"- Projected `absolute_gauss_lie4_acc` at h=0.05: orientation error {acc_fine['orientation_error_rad']:.3e}, endpoint constraint {acc_fine['max_endpoint_constraint_norm']:.3e}, endpoint velocity constraint {acc_fine['max_endpoint_velocity_constraint_norm']:.3e}, max lambda norm {acc_fine['max_lambda_norm']:.3e}.",
            f"- Medium-time acceleration-constrained projected run, 20s h=0.05: energy drift {medium['max_energy_relative_error']:.3e}, endpoint constraint {medium['max_endpoint_constraint_norm']:.3e}, stage constraint {medium['max_stage_constraint_norm']:.3e}, total Newton iterations {medium['total_newton_iterations']}.",
            "",
            "## Interpretation",
            "",
            "- v007 is the first local prototype with explicit multipliers in the nonlinear Lie-group stage solve.",
            "- Position-only stage constraints are not enough for this index-3 DAE: stage velocity consistency is required to avoid multiplier blow-up and low-order projected behavior.",
            "- Stage velocity constraints help, but the high-order behavior only returns when acceleration-level consistency is also enforced.",
            "- Endpoint projection is still used here; a production TFE method should include endpoint algebraic conditions directly instead of post-projecting.",
            "- v008 should add endpoint constraint equations directly to the nonlinear solve, likely by moving from pure two-point Gauss collocation to a TFE/Lobatto-style element with endpoint algebraic nodes, then add friction loads.",
            "",
            "## Plots",
            "",
            "- `absolute_dae_orientation_order.png`",
            "- `absolute_dae_constraint_drift.png`",
            "",
        ]
    )
    (RESULTS / "v007_report.md").write_text("\n".join(report), encoding="utf-8")


if __name__ == "__main__":
    main()
