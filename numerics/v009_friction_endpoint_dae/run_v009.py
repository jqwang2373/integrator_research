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

from friction_pendulum import (
    energy_state,
    estimate_order,
    initial_state,
    integrate,
    make_params,
    orientation_error,
)


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"

FRICTION_CASES = {
    "smooth_eps_0p50": {
        "friction_mu": 0.08,
        "friction_eps": 0.50,
        "viscous_damping": 0.04,
    },
    "sharp_eps_0p05": {
        "friction_mu": 0.08,
        "friction_eps": 0.05,
        "viscous_damping": 0.04,
    },
}

METHODS = ["reduced_rkmk4", "absolute_gauss_lie4_endpoint"]


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


def params_for_case(case_config: dict) -> object:
    return make_params(
        friction_mu=case_config["friction_mu"],
        friction_eps=case_config["friction_eps"],
        viscous_damping=case_config["viscous_damping"],
    )


def run_order() -> dict:
    t_final = 2.0
    hs = [0.2, 0.1, 0.05]
    rows = []
    cases = {}

    for case_name, case_config in FRICTION_CASES.items():
        params = params_for_case(case_config)
        ref_h = 2.0 / 131072.0
        ref = integrate("reduced_rkmk4", ref_h, t_final, params)
        method_summary = {}

        for method in METHODS:
            orientation_errors = []
            omega_errors = []
            endpoint_constraints = []
            energy_increases = []
            runs = {}

            for h in hs:
                start = time.perf_counter()
                out = integrate(method, h, t_final, params)
                runtime = time.perf_counter() - start
                state = out["state"]
                ref_state = ref["state"]
                oerr = orientation_error(ref_state.R, state.R)
                werr = float(np.linalg.norm(ref_state.w - state.w))

                orientation_errors.append(oerr)
                omega_errors.append(werr)
                endpoint_constraints.append(out["max_endpoint_constraint_norm"])
                energy_increases.append(max(out["max_step_energy_increase"], 1.0e-18))

                row = {
                    "case": case_name,
                    "method": method,
                    "h": f"{h:.10g}",
                    "steps": out["steps"],
                    "orientation_error_rad": f"{oerr:.16e}",
                    "omega_l2_error": f"{werr:.16e}",
                    "max_energy_relative_change_from_initial": f"{out['max_energy_relative_error']:.16e}",
                    "final_energy_change": f"{out['final_energy_change']:.16e}",
                    "final_energy_relative_change": f"{out['final_energy_relative_change']:.16e}",
                    "max_step_energy_increase": f"{out['max_step_energy_increase']:.16e}",
                    "max_friction_power": f"{out['max_friction_power']:.16e}",
                    "min_friction_power": f"{out['min_friction_power']:.16e}",
                    "max_endpoint_constraint_norm": f"{out['max_endpoint_constraint_norm']:.16e}",
                    "max_endpoint_velocity_constraint_norm": f"{out['max_endpoint_velocity_constraint_norm']:.16e}",
                    "max_stage_constraint_norm": f"{out['max_stage_constraint_norm']:.16e}",
                    "max_stage_force_residual_norm": f"{out['max_stage_force_residual_norm']:.16e}",
                    "max_stage_torque_residual_norm": f"{out['max_stage_torque_residual_norm']:.16e}",
                    "max_lambda_norm": f"{out['max_lambda_norm']:.16e}",
                    "total_newton_iterations": out["total_newton_iterations"],
                    "runtime_sec": f"{runtime:.8e}",
                }
                rows.append(row)
                runs[str(h)] = {
                    "orientation_error_rad": oerr,
                    "omega_l2_error": werr,
                    "max_energy_relative_change_from_initial": out["max_energy_relative_error"],
                    "final_energy_change": out["final_energy_change"],
                    "final_energy_relative_change": out["final_energy_relative_change"],
                    "max_step_energy_increase": out["max_step_energy_increase"],
                    "max_friction_power": out["max_friction_power"],
                    "min_friction_power": out["min_friction_power"],
                    "max_endpoint_constraint_norm": out["max_endpoint_constraint_norm"],
                    "max_endpoint_velocity_constraint_norm": out["max_endpoint_velocity_constraint_norm"],
                    "max_stage_constraint_norm": out["max_stage_constraint_norm"],
                    "max_stage_force_residual_norm": out["max_stage_force_residual_norm"],
                    "max_stage_torque_residual_norm": out["max_stage_torque_residual_norm"],
                    "max_lambda_norm": out["max_lambda_norm"],
                    "total_newton_iterations": out["total_newton_iterations"],
                    "runtime_sec": runtime,
                }

            method_summary[method] = {
                "orientation_observed_order": estimate_order(hs, orientation_errors),
                "omega_observed_order": estimate_order(hs, omega_errors),
                "endpoint_constraint_observed_order": estimate_order(hs, endpoint_constraints),
                "max_step_energy_increase_order": estimate_order(hs, energy_increases),
                "runs": runs,
            }

        cases[case_name] = {
            "friction": case_config,
            "reference_method": "reduced_rkmk4",
            "reference_h": ref_h,
            "methods": method_summary,
        }

    write_csv(RESULTS / "friction_order.csv", rows)
    return {
        "t_final": t_final,
        "step_sizes": hs,
        "cases": cases,
    }


def run_dissipation() -> dict:
    t_final = 5.0
    hs = [0.1, 0.05]
    rows = []
    cases = {}

    for case_name, case_config in FRICTION_CASES.items():
        params = params_for_case(case_config)
        method_summary = {}
        for method in METHODS:
            runs = {}
            for h in hs:
                start = time.perf_counter()
                out = integrate(method, h, t_final, params)
                runtime = time.perf_counter() - start
                rows.append(
                    {
                        "case": case_name,
                        "method": method,
                        "h": f"{h:.10g}",
                        "steps": out["steps"],
                        "max_energy_relative_change_from_initial": f"{out['max_energy_relative_error']:.16e}",
                        "final_energy_change": f"{out['final_energy_change']:.16e}",
                        "final_energy_relative_change": f"{out['final_energy_relative_change']:.16e}",
                        "max_step_energy_increase": f"{out['max_step_energy_increase']:.16e}",
                        "max_friction_power": f"{out['max_friction_power']:.16e}",
                        "min_friction_power": f"{out['min_friction_power']:.16e}",
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
                    "max_energy_relative_change_from_initial": out["max_energy_relative_error"],
                    "final_energy_change": out["final_energy_change"],
                    "final_energy_relative_change": out["final_energy_relative_change"],
                    "max_step_energy_increase": out["max_step_energy_increase"],
                    "max_friction_power": out["max_friction_power"],
                    "min_friction_power": out["min_friction_power"],
                    "max_endpoint_constraint_norm": out["max_endpoint_constraint_norm"],
                    "max_endpoint_velocity_constraint_norm": out["max_endpoint_velocity_constraint_norm"],
                    "max_stage_constraint_norm": out["max_stage_constraint_norm"],
                    "max_stage_force_residual_norm": out["max_stage_force_residual_norm"],
                    "max_stage_torque_residual_norm": out["max_stage_torque_residual_norm"],
                    "max_lambda_norm": out["max_lambda_norm"],
                    "total_newton_iterations": out["total_newton_iterations"],
                    "runtime_sec": runtime,
                }
            method_summary[method] = runs
        cases[case_name] = method_summary

    write_csv(RESULTS / "friction_dissipation.csv", rows)
    return {
        "t_final": t_final,
        "step_sizes": hs,
        "cases": cases,
    }


def plot_results(summary: dict) -> None:
    import matplotlib.pyplot as plt

    hs = summary["order"]["step_sizes"]
    for case_name, case in summary["order"]["cases"].items():
        plt.figure(figsize=(7.0, 4.5))
        for method, item in case["methods"].items():
            errors = [item["runs"][str(h)]["orientation_error_rad"] for h in hs]
            plt.loglog(hs, errors, marker="o", label=method)
        plt.gca().invert_xaxis()
        plt.xlabel("step size h")
        plt.ylabel("orientation error [rad]")
        plt.title(f"Frictional Endpoint DAE: {case_name}")
        plt.grid(True, which="both", alpha=0.35)
        plt.legend()
        plt.tight_layout()
        plt.savefig(RESULTS / f"friction_order_{case_name}.png", dpi=180)
        plt.close()

    plt.figure(figsize=(7.2, 4.6))
    h = 0.05
    labels = []
    values = []
    for case_name, case in summary["dissipation"]["cases"].items():
        for method in METHODS:
            labels.append(f"{case_name}\n{method}")
            values.append(case[method][str(h)]["final_energy_relative_change"])
    plt.bar(range(len(values)), values)
    plt.xticks(range(len(values)), labels, rotation=25, ha="right")
    plt.ylabel("final relative energy change")
    plt.title("Frictional Energy Decay at h=0.05")
    plt.grid(True, axis="y", alpha=0.35)
    plt.tight_layout()
    plt.savefig(RESULTS / "friction_energy_decay.png", dpi=180)
    plt.close()


def write_report(summary: dict) -> None:
    lines = [
        "# v009 Experiment Report",
        "",
        "Generated by `run_v009.py`.",
        "",
        "## Model and Solver",
        "",
        "- Fixed-pivot rigid body in absolute coordinates with constraint `r + R s = 0`.",
        "- The endpoint-constrained method uses the v008 54-variable two-stage Gauss-Lie nonlinear solve.",
        "- Friction is a body-frame pivot torque `tau_f(omega) = -c_v omega - mu tanh(omega / eps)`.",
        "- The rotational DAE residual and reduced reference ODE both include the same friction torque.",
        "",
        "## Friction Cases",
        "",
    ]
    for case_name, case_config in FRICTION_CASES.items():
        lines.append(
            f"- `{case_name}`: mu={case_config['friction_mu']}, "
            f"eps={case_config['friction_eps']}, c_v={case_config['viscous_damping']}."
        )

    lines.extend(["", "## Short-Time Order", ""])
    for case_name, case in summary["order"]["cases"].items():
        lines.append(f"### {case_name}")
        for method, item in case["methods"].items():
            fine = item["runs"]["0.05"]
            lines.append(
                f"- `{method}`: orientation order {item['orientation_observed_order']:.3f}, "
                f"omega order {item['omega_observed_order']:.3f}; at h=0.05 orientation error "
                f"{fine['orientation_error_rad']:.3e}, omega error {fine['omega_l2_error']:.3e}, "
                f"endpoint constraint {fine['max_endpoint_constraint_norm']:.3e}, "
                f"max step energy increase {fine['max_step_energy_increase']:.3e}."
            )

    lines.extend(["", "## Dissipation Check", ""])
    for case_name, case in summary["dissipation"]["cases"].items():
        lines.append(f"### {case_name}")
        for method in METHODS:
            fine = case[method]["0.05"]
            lines.append(
                f"- `{method}`, 5s h=0.05: final relative energy change "
                f"{fine['final_energy_relative_change']:.3e}, max step energy increase "
                f"{fine['max_step_energy_increase']:.3e}, max friction power "
                f"{fine['max_friction_power']:.3e}, min friction power {fine['min_friction_power']:.3e}, "
                f"endpoint constraint {fine['max_endpoint_constraint_norm']:.3e}, Newton iterations "
                f"{fine['total_newton_iterations']}."
            )

    smooth = summary["order"]["cases"]["smooth_eps_0p50"]["methods"]["absolute_gauss_lie4_endpoint"]
    sharp = summary["order"]["cases"]["sharp_eps_0p05"]["methods"]["absolute_gauss_lie4_endpoint"]
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"- Smooth regularized friction keeps the endpoint DAE near fourth order: orientation order {smooth['orientation_observed_order']:.3f}.",
            f"- Sharper Coulomb-like regularization is more order-stressful; the measured endpoint orientation order is {sharp['orientation_observed_order']:.3f}.",
            "- Endpoint position/velocity constraints remain at nonlinear-solve tolerance because they are solved inside Newton, not repaired afterward.",
            "- The current prototype uses finite-difference Jacobians. Analytic or AD Jacobians are the next practical step before larger friction/contact examples.",
            "",
            "## Plots",
            "",
            "- `friction_order_smooth_eps_0p50.png`",
            "- `friction_order_sharp_eps_0p05.png`",
            "- `friction_energy_decay.png`",
            "",
        ]
    )
    (RESULTS / "v009_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    base_params = make_params(**FRICTION_CASES["smooth_eps_0p50"])
    state0 = initial_state(base_params)
    summary = {
        "version": "v009_friction_endpoint_dae",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "model": {
            "mass": base_params.mass,
            "J_com_diag": np.diag(base_params.J_com).tolist(),
            "s_com_to_pivot": base_params.s_com_to_pivot.tolist(),
            "gravity": base_params.gravity.tolist(),
            "initial_energy_smooth_case": energy_state(state0, base_params),
            "constraint": "r + R s = 0",
            "friction_law": "tau_f(omega) = -c_v omega - mu tanh(omega / eps)",
            "stage_unknowns": "u_i, r_i, v_i, omega_i, a_i, alpha_i, lambda_i for i=1,2",
            "endpoint_unknowns": "u_end, r_end, v_end, omega_end",
        },
        "order": run_order(),
        "dissipation": run_dissipation(),
    }
    summary["runtime_sec"] = time.perf_counter() - started
    plot_results(summary)
    with (RESULTS / "summary.json").open("w", encoding="utf-8") as f:
        json.dump(json_safe(summary), f, indent=2, sort_keys=True)
    write_report(summary)


if __name__ == "__main__":
    main()
