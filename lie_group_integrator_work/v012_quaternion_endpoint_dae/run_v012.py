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

import jax

jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp
import numpy as np

from quaternion_pendulum import (
    compose_right_quat_jax,
    energy_state,
    estimate_order,
    initial_state,
    integrate,
    make_params,
    orientation_error,
    quat_to_rot,
    right_transport_matrix,
)


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
V010_PATH = HERE.parent / "v010_jax_jacobian_endpoint_dae" / "friction_pendulum.py"

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


def load_v010_module():
    spec = importlib.util.spec_from_file_location("v010_friction_pendulum", V010_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


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


def run_transport_validation() -> dict:
    state0 = initial_state(make_params())
    theta_cases = {
        "tiny": np.array([1.0e-8, -2.0e-8, 1.5e-8]),
        "small": np.array([1.0e-4, -2.0e-4, 1.5e-4]),
        "moderate": np.array([0.18, -0.11, 0.27]),
        "large": np.array([1.15, -0.72, 0.93]),
    }
    rows = []
    summary = {}
    q0 = state0.p
    for name, theta in theta_cases.items():
        T = right_transport_matrix(theta, q0)
        T_ad = np.asarray(
            jax.jacfwd(lambda th: compose_right_quat_jax(jnp.asarray(q0, dtype=jnp.float64), th))(
                jnp.asarray(theta, dtype=jnp.float64)
            )
        )
        max_abs = float(np.max(np.abs(T - T_ad)))
        rel = float(np.linalg.norm(T - T_ad) / max(np.linalg.norm(T_ad), 1.0e-30))
        item = {
            "theta_norm": float(np.linalg.norm(theta)),
            "max_abs_T_minus_AD": max_abs,
            "relative_T_error": rel,
        }
        summary[name] = item
        rows.append(
            {
                "case": name,
                "theta_norm": f"{item['theta_norm']:.16e}",
                "max_abs_T_minus_AD": f"{max_abs:.16e}",
                "relative_T_error": f"{rel:.16e}",
            }
        )
    write_csv(RESULTS / "right_transport_validation.csv", rows)
    return summary


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
        for method in ["reduced_rkmk4", "quaternion_gauss_lie4_endpoint_jax"]:
            orientation_errors = []
            omega_errors = []
            runs = {}
            for h in hs:
                start = time.perf_counter()
                out = integrate(method, h, t_final, params)
                runtime = time.perf_counter() - start
                state = out["state"]
                ref_state = ref["state"]
                oerr = orientation_error(quat_to_rot(ref_state.p), quat_to_rot(state.p))
                werr = float(np.linalg.norm(ref_state.w - state.w))
                orientation_errors.append(oerr)
                omega_errors.append(werr)
                rows.append(
                    {
                        "case": case_name,
                        "method": method,
                        "h": f"{h:.10g}",
                        "steps": out["steps"],
                        "orientation_error_rad": f"{oerr:.16e}",
                        "omega_l2_error": f"{werr:.16e}",
                        "max_endpoint_constraint_norm": f"{out['max_endpoint_constraint_norm']:.16e}",
                        "max_endpoint_velocity_constraint_norm": f"{out['max_endpoint_velocity_constraint_norm']:.16e}",
                        "max_stage_constraint_norm": f"{out['max_stage_constraint_norm']:.16e}",
                        "max_stage_force_residual_norm": f"{out['max_stage_force_residual_norm']:.16e}",
                        "max_stage_torque_residual_norm": f"{out['max_stage_torque_residual_norm']:.16e}",
                        "max_quaternion_unit_error": f"{out['max_quaternion_unit_error']:.16e}",
                        "final_energy_relative_change": f"{out['final_energy_relative_change']:.16e}",
                        "max_step_energy_increase": f"{out['max_step_energy_increase']:.16e}",
                        "total_newton_iterations": out["total_newton_iterations"],
                        "runtime_sec": f"{runtime:.8e}",
                    }
                )
                runs[str(h)] = {
                    "orientation_error_rad": oerr,
                    "omega_l2_error": werr,
                    "max_endpoint_constraint_norm": out["max_endpoint_constraint_norm"],
                    "max_endpoint_velocity_constraint_norm": out["max_endpoint_velocity_constraint_norm"],
                    "max_stage_constraint_norm": out["max_stage_constraint_norm"],
                    "max_stage_force_residual_norm": out["max_stage_force_residual_norm"],
                    "max_stage_torque_residual_norm": out["max_stage_torque_residual_norm"],
                    "max_quaternion_unit_error": out["max_quaternion_unit_error"],
                    "final_energy_relative_change": out["final_energy_relative_change"],
                    "max_step_energy_increase": out["max_step_energy_increase"],
                    "total_newton_iterations": out["total_newton_iterations"],
                    "runtime_sec": runtime,
                }
            method_summary[method] = {
                "orientation_observed_order": estimate_order(hs, orientation_errors),
                "omega_observed_order": estimate_order(hs, omega_errors),
                "runs": runs,
            }
        cases[case_name] = {
            "friction": case_config,
            "reference_method": "reduced_rkmk4",
            "reference_h": ref_h,
            "methods": method_summary,
        }
    write_csv(RESULTS / "quaternion_order.csv", rows)
    return {"t_final": t_final, "step_sizes": hs, "cases": cases}


def run_so3_equivalence() -> dict:
    v010 = load_v010_module()
    rows = []
    cases = {}
    for case_name, case_config in FRICTION_CASES.items():
        q_params = params_for_case(case_config)
        so3_params = v010.make_params(**case_config)
        case_runs = {}
        for t_final in [2.0, 5.0]:
            h = 0.05
            start = time.perf_counter()
            q_out = integrate("quaternion_gauss_lie4_endpoint_jax", h, t_final, q_params)
            q_runtime = time.perf_counter() - start
            start = time.perf_counter()
            so3_out = v010.integrate("absolute_gauss_lie4_endpoint_jax", h, t_final, so3_params)
            so3_runtime = time.perf_counter() - start
            q_state = q_out["state"]
            so3_state = so3_out["state"]
            o_diff = orientation_error(so3_state.R, quat_to_rot(q_state.p))
            w_diff = float(np.linalg.norm(so3_state.w - q_state.w))
            energy_diff = float(so3_out["final_energy_relative_change"] - q_out["final_energy_relative_change"])
            key = f"{t_final:g}"
            case_runs[key] = {
                "h": h,
                "orientation_difference_rad": o_diff,
                "omega_difference_l2": w_diff,
                "final_energy_relative_difference": energy_diff,
                "quaternion_runtime_sec": q_runtime,
                "so3_runtime_sec": so3_runtime,
                "runtime_ratio_quaternion_over_so3": q_runtime / max(so3_runtime, 1.0e-30),
                "quaternion_max_constraint": q_out["max_endpoint_constraint_norm"],
                "so3_max_constraint": so3_out["max_endpoint_constraint_norm"],
            }
            rows.append(
                {
                    "case": case_name,
                    "t_final": f"{t_final:.10g}",
                    "h": f"{h:.10g}",
                    "orientation_difference_rad": f"{o_diff:.16e}",
                    "omega_difference_l2": f"{w_diff:.16e}",
                    "final_energy_relative_difference": f"{energy_diff:.16e}",
                    "quaternion_runtime_sec": f"{q_runtime:.8e}",
                    "so3_runtime_sec": f"{so3_runtime:.8e}",
                    "runtime_ratio_quaternion_over_so3": f"{q_runtime / max(so3_runtime, 1.0e-30):.8e}",
                    "quaternion_max_constraint": f"{q_out['max_endpoint_constraint_norm']:.16e}",
                    "so3_max_constraint": f"{so3_out['max_endpoint_constraint_norm']:.16e}",
                }
            )
        cases[case_name] = case_runs
    write_csv(RESULTS / "so3_quaternion_equivalence.csv", rows)
    return {"cases": cases}


def run_dissipation() -> dict:
    t_final = 5.0
    h = 0.05
    rows = []
    cases = {}
    for case_name, case_config in FRICTION_CASES.items():
        params = params_for_case(case_config)
        out = integrate("quaternion_gauss_lie4_endpoint_jax", h, t_final, params)
        cases[case_name] = {
            "h": h,
            "t_final": t_final,
            "final_energy_relative_change": out["final_energy_relative_change"],
            "max_step_energy_increase": out["max_step_energy_increase"],
            "max_friction_power": out["max_friction_power"],
            "min_friction_power": out["min_friction_power"],
            "max_endpoint_constraint_norm": out["max_endpoint_constraint_norm"],
            "max_endpoint_velocity_constraint_norm": out["max_endpoint_velocity_constraint_norm"],
            "max_quaternion_unit_error": out["max_quaternion_unit_error"],
            "total_newton_iterations": out["total_newton_iterations"],
        }
        rows.append(
            {
                "case": case_name,
                "h": f"{h:.10g}",
                "t_final": f"{t_final:.10g}",
                "final_energy_relative_change": f"{out['final_energy_relative_change']:.16e}",
                "max_step_energy_increase": f"{out['max_step_energy_increase']:.16e}",
                "max_friction_power": f"{out['max_friction_power']:.16e}",
                "min_friction_power": f"{out['min_friction_power']:.16e}",
                "max_endpoint_constraint_norm": f"{out['max_endpoint_constraint_norm']:.16e}",
                "max_endpoint_velocity_constraint_norm": f"{out['max_endpoint_velocity_constraint_norm']:.16e}",
                "max_quaternion_unit_error": f"{out['max_quaternion_unit_error']:.16e}",
                "total_newton_iterations": out["total_newton_iterations"],
            }
        )
    write_csv(RESULTS / "quaternion_dissipation.csv", rows)
    return {"cases": cases}


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
        plt.title(f"Quaternion Endpoint DAE: {case_name}")
        plt.grid(True, which="both", alpha=0.35)
        plt.legend()
        plt.tight_layout()
        plt.savefig(RESULTS / f"quaternion_order_{case_name}.png", dpi=180)
        plt.close()


def write_report(summary: dict) -> None:
    transport_max = max(item["max_abs_T_minus_AD"] for item in summary["right_transport_validation"].values())
    lines = [
        "# v012 Experiment Report",
        "",
        "Generated by `run_v012.py`.",
        "",
        "## Purpose",
        "",
        "- Embed the verified `S^3` transport idea into the endpoint-constrained frictional DAE prototype.",
        "- Use scalar-first Hamilton quaternions with the right-action update `p(theta)=p0 * exp(theta/2)` to match v010's `R exp(theta)` convention.",
        "- Keep the same 54-variable endpoint residual and JAX Newton Jacobian, but compute all stage/end attitudes through unit quaternions.",
        "",
        "## Right-Action Transport Check",
        "",
        f"- Largest right-action `T_exp` analytic-vs-AD max absolute error: {transport_max:.3e}.",
        "",
        "## Short-Time Order",
        "",
    ]
    for case_name, case in summary["order"]["cases"].items():
        endpoint = case["methods"]["quaternion_gauss_lie4_endpoint_jax"]
        fine = endpoint["runs"]["0.05"]
        lines.append(
            f"- `{case_name}` endpoint: orientation order {endpoint['orientation_observed_order']:.3f}, "
            f"omega order {endpoint['omega_observed_order']:.3f}; h=0.05 orientation error "
            f"{fine['orientation_error_rad']:.3e}, endpoint constraint {fine['max_endpoint_constraint_norm']:.3e}, "
            f"quaternion unit error {fine['max_quaternion_unit_error']:.3e}."
        )
    lines.extend(["", "## SO3 Equivalence", ""])
    for case_name, case in summary["so3_equivalence"]["cases"].items():
        fine = case["5"]
        lines.append(
            f"- `{case_name}`, 5s h=0.05: quaternion/SO3 orientation difference "
            f"{fine['orientation_difference_rad']:.3e}, omega difference {fine['omega_difference_l2']:.3e}, "
            f"energy-relative difference {fine['final_energy_relative_difference']:.3e}, "
            f"runtime ratio q/SO3 {fine['runtime_ratio_quaternion_over_so3']:.2f}."
        )
    lines.extend(["", "## Dissipation", ""])
    for case_name, item in summary["dissipation"]["cases"].items():
        lines.append(
            f"- `{case_name}`, 5s h=0.05: final relative energy change "
            f"{item['final_energy_relative_change']:.3e}, max step energy increase "
            f"{item['max_step_energy_increase']:.3e}, max friction power {item['max_friction_power']:.3e}, "
            f"constraint {item['max_endpoint_constraint_norm']:.3e}."
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- v012 is the first local prototype whose endpoint DAE residual carries attitude as a unit quaternion instead of a rotation matrix.",
            "- The method preserves v010's numerical behavior while removing explicit orthogonality concerns; unit norm is maintained by exponential updates plus normalization at roundoff scale.",
            "- This is still a Gauss-Lie endpoint collocation prototype, not the paper's full TFE family. The next method-level step is a TFE/BDF comparison using the same quaternion residual and AD backend.",
            "",
            "## Outputs",
            "",
            "- `right_transport_validation.csv`",
            "- `quaternion_order.csv`",
            "- `so3_quaternion_equivalence.csv`",
            "- `quaternion_dissipation.csv`",
            "",
        ]
    )
    (RESULTS / "v012_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    base_params = params_for_case(FRICTION_CASES["smooth_eps_0p50"])
    state0 = initial_state(base_params)
    summary = {
        "version": "v012_quaternion_endpoint_dae",
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
            "quaternion_order": "scalar_first",
            "attitude_update": "p_next = p * exp(theta/2)",
            "endpoint_unknown_count": 54,
        },
        "right_transport_validation": run_transport_validation(),
        "order": run_order(),
        "so3_equivalence": run_so3_equivalence(),
        "dissipation": run_dissipation(),
    }
    summary["runtime_sec"] = time.perf_counter() - started
    plot_results(summary)
    with (RESULTS / "summary_v012.json").open("w", encoding="utf-8") as f:
        json.dump(json_safe(summary), f, indent=2, sort_keys=True)
    write_report(summary)


if __name__ == "__main__":
    main()
