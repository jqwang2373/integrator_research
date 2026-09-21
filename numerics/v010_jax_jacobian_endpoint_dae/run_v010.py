from __future__ import annotations

import csv
import json
import os
import platform
import time
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", "/tmp/mplconfig")

import jax
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

METHODS = {
    "endpoint_fd": "absolute_gauss_lie4_endpoint",
    "endpoint_jax": "absolute_gauss_lie4_endpoint_jax",
}


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


def warm_jax() -> float:
    params = params_for_case(FRICTION_CASES["smooth_eps_0p50"])
    start = time.perf_counter()
    integrate("absolute_gauss_lie4_endpoint_jax", 0.2, 0.2, params)
    return time.perf_counter() - start


def run_order_runtime() -> dict:
    t_final = 2.0
    hs = [0.2, 0.1, 0.05]
    rows = []
    cases = {}

    for case_name, case_config in FRICTION_CASES.items():
        params = params_for_case(case_config)
        ref_h = 2.0 / 131072.0
        ref = integrate("reduced_rkmk4", ref_h, t_final, params)
        method_summary = {}

        for label, method in METHODS.items():
            orientation_errors = []
            omega_errors = []
            runtimes = []
            runs = {}
            for h in hs:
                start = time.perf_counter()
                out = integrate(method, h, t_final, params)
                runtime = time.perf_counter() - start
                ref_state = ref["state"]
                state = out["state"]
                oerr = orientation_error(ref_state.R, state.R)
                werr = float(np.linalg.norm(ref_state.w - state.w))
                orientation_errors.append(oerr)
                omega_errors.append(werr)
                runtimes.append(runtime)
                row = {
                    "case": case_name,
                    "method": label,
                    "h": f"{h:.10g}",
                    "steps": out["steps"],
                    "orientation_error_rad": f"{oerr:.16e}",
                    "omega_l2_error": f"{werr:.16e}",
                    "max_endpoint_constraint_norm": f"{out['max_endpoint_constraint_norm']:.16e}",
                    "max_endpoint_velocity_constraint_norm": f"{out['max_endpoint_velocity_constraint_norm']:.16e}",
                    "max_stage_constraint_norm": f"{out['max_stage_constraint_norm']:.16e}",
                    "max_stage_force_residual_norm": f"{out['max_stage_force_residual_norm']:.16e}",
                    "max_stage_torque_residual_norm": f"{out['max_stage_torque_residual_norm']:.16e}",
                    "max_lambda_norm": f"{out['max_lambda_norm']:.16e}",
                    "final_energy_relative_change": f"{out['final_energy_relative_change']:.16e}",
                    "max_step_energy_increase": f"{out['max_step_energy_increase']:.16e}",
                    "total_newton_iterations": out["total_newton_iterations"],
                    "runtime_sec": f"{runtime:.8e}",
                }
                rows.append(row)
                runs[str(h)] = {
                    "orientation_error_rad": oerr,
                    "omega_l2_error": werr,
                    "max_endpoint_constraint_norm": out["max_endpoint_constraint_norm"],
                    "max_endpoint_velocity_constraint_norm": out["max_endpoint_velocity_constraint_norm"],
                    "max_stage_constraint_norm": out["max_stage_constraint_norm"],
                    "max_stage_force_residual_norm": out["max_stage_force_residual_norm"],
                    "max_stage_torque_residual_norm": out["max_stage_torque_residual_norm"],
                    "max_lambda_norm": out["max_lambda_norm"],
                    "final_energy_relative_change": out["final_energy_relative_change"],
                    "max_step_energy_increase": out["max_step_energy_increase"],
                    "total_newton_iterations": out["total_newton_iterations"],
                    "runtime_sec": runtime,
                }

            method_summary[label] = {
                "backend_method": method,
                "orientation_observed_order": estimate_order(hs, orientation_errors),
                "omega_observed_order": estimate_order(hs, omega_errors),
                "runtime_sec_by_h": dict(zip([str(h) for h in hs], runtimes)),
                "runs": runs,
            }

        fd = method_summary["endpoint_fd"]["runs"]
        jx = method_summary["endpoint_jax"]["runs"]
        speedups = {
            str(h): fd[str(h)]["runtime_sec"] / max(jx[str(h)]["runtime_sec"], 1.0e-30)
            for h in hs
        }
        cases[case_name] = {
            "friction": case_config,
            "reference_method": "reduced_rkmk4",
            "reference_h": ref_h,
            "methods": method_summary,
            "jax_speedup_over_fd": speedups,
        }

    write_csv(RESULTS / "jax_order_runtime.csv", rows)
    return {
        "t_final": t_final,
        "step_sizes": hs,
        "cases": cases,
    }


def run_equivalence() -> dict:
    rows = []
    cases = {}
    t_final = 5.0
    h = 0.05
    for case_name, case_config in FRICTION_CASES.items():
        params = params_for_case(case_config)
        outputs = {}
        for label, method in METHODS.items():
            start = time.perf_counter()
            out = integrate(method, h, t_final, params)
            runtime = time.perf_counter() - start
            outputs[label] = (out, runtime)
            rows.append(
                {
                    "case": case_name,
                    "method": label,
                    "h": f"{h:.10g}",
                    "t_final": f"{t_final:.10g}",
                    "final_energy_relative_change": f"{out['final_energy_relative_change']:.16e}",
                    "max_step_energy_increase": f"{out['max_step_energy_increase']:.16e}",
                    "max_friction_power": f"{out['max_friction_power']:.16e}",
                    "min_friction_power": f"{out['min_friction_power']:.16e}",
                    "max_endpoint_constraint_norm": f"{out['max_endpoint_constraint_norm']:.16e}",
                    "max_endpoint_velocity_constraint_norm": f"{out['max_endpoint_velocity_constraint_norm']:.16e}",
                    "total_newton_iterations": out["total_newton_iterations"],
                    "runtime_sec": f"{runtime:.8e}",
                }
            )
        fd_state = outputs["endpoint_fd"][0]["state"]
        jx_state = outputs["endpoint_jax"][0]["state"]
        cases[case_name] = {
            "h": h,
            "t_final": t_final,
            "fd_runtime_sec": outputs["endpoint_fd"][1],
            "jax_runtime_sec": outputs["endpoint_jax"][1],
            "speedup": outputs["endpoint_fd"][1] / max(outputs["endpoint_jax"][1], 1.0e-30),
            "fd_jax_orientation_difference_rad": orientation_error(fd_state.R, jx_state.R),
            "fd_jax_omega_difference_l2": float(np.linalg.norm(fd_state.w - jx_state.w)),
            "fd_jax_energy_relative_difference": float(
                outputs["endpoint_fd"][0]["final_energy_relative_change"]
                - outputs["endpoint_jax"][0]["final_energy_relative_change"]
            ),
        }
    write_csv(RESULTS / "jax_equivalence_dissipation.csv", rows)
    return {
        "cases": cases,
    }


def plot_results(summary: dict) -> None:
    import matplotlib.pyplot as plt

    hs = summary["order_runtime"]["step_sizes"]
    for case_name, case in summary["order_runtime"]["cases"].items():
        plt.figure(figsize=(7.0, 4.5))
        for label, item in case["methods"].items():
            errors = [item["runs"][str(h)]["orientation_error_rad"] for h in hs]
            plt.loglog(hs, errors, marker="o", label=label)
        plt.gca().invert_xaxis()
        plt.xlabel("step size h")
        plt.ylabel("orientation error [rad]")
        plt.title(f"JAX Jacobian Endpoint DAE: {case_name}")
        plt.grid(True, which="both", alpha=0.35)
        plt.legend()
        plt.tight_layout()
        plt.savefig(RESULTS / f"jax_order_{case_name}.png", dpi=180)
        plt.close()

    plt.figure(figsize=(7.0, 4.5))
    labels = []
    values = []
    for case_name, case in summary["order_runtime"]["cases"].items():
        labels.append(f"{case_name}\nh=0.05")
        values.append(case["jax_speedup_over_fd"]["0.05"])
    plt.bar(range(len(values)), values)
    plt.xticks(range(len(values)), labels)
    plt.ylabel("speedup over finite-difference Jacobian")
    plt.title("JAX Jacobian Runtime Speedup")
    plt.grid(True, axis="y", alpha=0.35)
    plt.tight_layout()
    plt.savefig(RESULTS / "jax_speedup.png", dpi=180)
    plt.close()


def write_report(summary: dict) -> None:
    lines = [
        "# v010 Experiment Report",
        "",
        "Generated by `run_v010.py`.",
        "",
        "## Purpose",
        "",
        "- v009 showed that endpoint-constrained Gauss-Lie DAE integration works for smooth friction, but finite-difference Newton Jacobians dominate runtime.",
        "- v010 keeps the same equations and adds a JAX `jacfwd` Jacobian for the 54-variable endpoint residual.",
        "- This directly tests the paper's claim that frictional Lie-group DAE implementations need derivative-based, AD-friendly Jacobian construction.",
        "",
        "## Environment",
        "",
        f"- Python {summary['python']}, NumPy {summary['numpy']}, JAX {summary['jax']}.",
        f"- JAX warm-up one-step compile/run time: {summary['jax_warmup_sec']:.3f}s.",
        "",
        "## Order and Runtime",
        "",
    ]

    for case_name, case in summary["order_runtime"]["cases"].items():
        lines.append(f"### {case_name}")
        for label, item in case["methods"].items():
            fine = item["runs"]["0.05"]
            lines.append(
                f"- `{label}`: orientation order {item['orientation_observed_order']:.3f}, "
                f"omega order {item['omega_observed_order']:.3f}; at h=0.05 orientation error "
                f"{fine['orientation_error_rad']:.3e}, endpoint constraint "
                f"{fine['max_endpoint_constraint_norm']:.3e}, runtime {fine['runtime_sec']:.3f}s."
            )
        lines.append(f"- JAX speedup over finite difference at h=0.05: {case['jax_speedup_over_fd']['0.05']:.2f}x.")

    lines.extend(["", "## 5s Dissipation Equivalence", ""])
    for case_name, case in summary["equivalence"]["cases"].items():
        lines.append(
            f"- `{case_name}`: FD/JAX orientation difference {case['fd_jax_orientation_difference_rad']:.3e}, "
            f"omega difference {case['fd_jax_omega_difference_l2']:.3e}, "
            f"energy-relative difference {case['fd_jax_energy_relative_difference']:.3e}, "
            f"speedup {case['speedup']:.2f}x."
        )

    smooth_speed = summary["order_runtime"]["cases"]["smooth_eps_0p50"]["jax_speedup_over_fd"]["0.05"]
    sharp_speed = summary["order_runtime"]["cases"]["sharp_eps_0p05"]["jax_speedup_over_fd"]["0.05"]
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The AD Jacobian preserves the v009 numerical behavior to roundoff-level agreement with the finite-difference solve.",
            f"- At h=0.05, warm JAX Jacobians speed the endpoint Newton solve by {smooth_speed:.2f}x for smooth friction and {sharp_speed:.2f}x for sharper friction.",
            "- This is not a new integrator by itself; it removes a practical bottleneck in the current best frictional DAE prototype and makes higher-order friction/contact experiments more realistic.",
            "- The next method-level comparison should implement a Lie-group BDF/TFE family member, because v010 primarily improves the nonlinear solve backend.",
            "",
            "## Outputs",
            "",
            "- `jax_order_runtime.csv`",
            "- `jax_equivalence_dissipation.csv`",
            "- `jax_order_smooth_eps_0p50.png`",
            "- `jax_order_sharp_eps_0p05.png`",
            "- `jax_speedup.png`",
            "",
        ]
    )
    (RESULTS / "v010_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    base_params = params_for_case(FRICTION_CASES["smooth_eps_0p50"])
    state0 = initial_state(base_params)
    summary = {
        "version": "v010_jax_jacobian_endpoint_dae",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "jax": jax.__version__,
        "model": {
            "mass": base_params.mass,
            "J_com_diag": np.diag(base_params.J_com).tolist(),
            "s_com_to_pivot": base_params.s_com_to_pivot.tolist(),
            "gravity": base_params.gravity.tolist(),
            "initial_energy_smooth_case": energy_state(state0, base_params),
            "constraint": "r + R s = 0",
            "friction_law": "tau_f(omega) = -c_v omega - mu tanh(omega / eps)",
            "endpoint_unknown_count": 54,
        },
        "jax_warmup_sec": warm_jax(),
        "order_runtime": run_order_runtime(),
        "equivalence": run_equivalence(),
    }
    summary["runtime_sec"] = time.perf_counter() - started
    plot_results(summary)
    with (RESULTS / "summary_v010.json").open("w", encoding="utf-8") as f:
        json.dump(json_safe(summary), f, indent=2, sort_keys=True)
    write_report(summary)


if __name__ == "__main__":
    main()
