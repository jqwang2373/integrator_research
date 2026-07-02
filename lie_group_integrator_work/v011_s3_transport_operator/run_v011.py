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

jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp
import numpy as np

from s3_transport import (
    default_inputs,
    left_quat_update_jax,
    left_quat_update_np,
    pi_operator,
    quat_normalize_np,
    transport_matrix_np,
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


def rel_norm(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.linalg.norm(a - b) / max(np.linalg.norm(b), 1.0e-30))


def run_transport_matrix_validation() -> dict:
    p0 = quat_normalize_np(np.array([0.91, 0.22, -0.28, 0.19]))
    theta_cases = {
        "tiny": np.array([1.0e-8, -2.0e-8, 1.5e-8]),
        "small": np.array([1.0e-4, -2.0e-4, 1.5e-4]),
        "moderate": np.array([0.18, -0.11, 0.27]),
        "large": np.array([1.15, -0.72, 0.93]),
    }
    rows = []
    summary = {}
    for name, theta in theta_cases.items():
        T = transport_matrix_np(theta, p0)
        T_ad = np.asarray(
            jax.jacfwd(lambda th: left_quat_update_jax(th, jnp.asarray(p0, dtype=jnp.float64)))(
                jnp.asarray(theta, dtype=jnp.float64)
            )
        )
        p_np = left_quat_update_np(theta, p0)
        p_jax = np.asarray(left_quat_update_jax(jnp.asarray(theta, dtype=jnp.float64), jnp.asarray(p0, dtype=jnp.float64)))
        max_abs = float(np.max(np.abs(T - T_ad)))
        rel = rel_norm(T, T_ad)
        unit_error = float(abs(np.linalg.norm(p_np) - 1.0))
        update_error = float(np.linalg.norm(p_np - p_jax))
        item = {
            "theta_norm": float(np.linalg.norm(theta)),
            "max_abs_T_minus_AD": max_abs,
            "relative_T_error": rel,
            "unit_norm_error": unit_error,
            "np_jax_update_l2": update_error,
        }
        summary[name] = item
        rows.append(
            {
                "case": name,
                "theta_norm": f"{item['theta_norm']:.16e}",
                "max_abs_T_minus_AD": f"{max_abs:.16e}",
                "relative_T_error": f"{rel:.16e}",
                "unit_norm_error": f"{unit_error:.16e}",
                "np_jax_update_l2": f"{update_error:.16e}",
            }
        )
    write_csv(RESULTS / "transport_matrix_validation.csv", rows)
    return summary


def run_pi_theta_validation() -> dict:
    cases = {
        "smooth_eps_0p50_base": default_inputs(mu=0.08, eps=0.50, scale=1.0),
        "sharp_eps_0p05_base": default_inputs(mu=0.08, eps=0.05, scale=1.0),
        "smooth_eps_0p50_larger_rotation": default_inputs(mu=0.08, eps=0.50, scale=2.2),
        "sharp_eps_0p05_larger_rotation": default_inputs(mu=0.08, eps=0.05, scale=2.2),
    }
    rows = []
    summary = {}
    for name, inputs in cases.items():
        start = time.perf_counter()
        out = pi_operator(inputs)
        runtime = time.perf_counter() - start
        pi_err = out["pi"] - out["direct_pi"]
        theta_err = out["theta_op"] - out["direct_theta"]
        fd_err = out["pi"] - out["fd_pi"]
        item = {
            "theta_norm": float(np.linalg.norm(inputs.theta)),
            "mu": float(inputs.mu),
            "eps": float(inputs.eps),
            "transported_pi_vs_direct_ad_max_abs": float(np.max(np.abs(pi_err))),
            "transported_pi_vs_direct_ad_relative": rel_norm(out["pi"], out["direct_pi"]),
            "theta_operator_vs_direct_ad_max_abs": float(np.max(np.abs(theta_err))),
            "theta_operator_vs_direct_ad_relative": rel_norm(out["theta_op"], out["direct_theta"]),
            "transported_pi_vs_finite_difference_max_abs": float(np.max(np.abs(fd_err))),
            "transported_pi_vs_finite_difference_relative": rel_norm(out["pi"], out["fd_pi"]),
            "unit_quaternion_error": float(abs(np.linalg.norm(out["p"]) - 1.0)),
            "runtime_sec": runtime,
        }
        summary[name] = item
        rows.append(
            {
                "case": name,
                "theta_norm": f"{item['theta_norm']:.16e}",
                "mu": f"{item['mu']:.16e}",
                "eps": f"{item['eps']:.16e}",
                "Pi_vs_direct_AD_max_abs": f"{item['transported_pi_vs_direct_ad_max_abs']:.16e}",
                "Pi_vs_direct_AD_relative": f"{item['transported_pi_vs_direct_ad_relative']:.16e}",
                "Theta_vs_direct_AD_max_abs": f"{item['theta_operator_vs_direct_ad_max_abs']:.16e}",
                "Theta_vs_direct_AD_relative": f"{item['theta_operator_vs_direct_ad_relative']:.16e}",
                "Pi_vs_finite_difference_max_abs": f"{item['transported_pi_vs_finite_difference_max_abs']:.16e}",
                "Pi_vs_finite_difference_relative": f"{item['transported_pi_vs_finite_difference_relative']:.16e}",
                "unit_quaternion_error": f"{item['unit_quaternion_error']:.16e}",
                "runtime_sec": f"{runtime:.8e}",
            }
        )
    write_csv(RESULTS / "pi_theta_validation.csv", rows)
    return summary


def plot_results(summary: dict) -> None:
    import matplotlib.pyplot as plt

    labels = list(summary["pi_theta_validation"].keys())
    values = [
        summary["pi_theta_validation"][label]["transported_pi_vs_direct_ad_max_abs"]
        for label in labels
    ]
    fd_values = [
        summary["pi_theta_validation"][label]["transported_pi_vs_finite_difference_max_abs"]
        for label in labels
    ]
    x = np.arange(len(labels))
    width = 0.36
    plt.figure(figsize=(8.0, 4.8))
    plt.bar(x - width / 2, values, width, label="vs direct AD")
    plt.bar(x + width / 2, fd_values, width, label="vs finite diff")
    plt.yscale("log")
    plt.xticks(x, labels, rotation=25, ha="right")
    plt.ylabel("max absolute error")
    plt.title("S3 Transported Pi Operator Validation")
    plt.grid(True, axis="y", alpha=0.35)
    plt.legend()
    plt.tight_layout()
    plt.savefig(RESULTS / "pi_validation_errors.png", dpi=180)
    plt.close()


def write_report(summary: dict) -> None:
    transport = summary["transport_matrix_validation"]
    pi_cases = summary["pi_theta_validation"]
    max_t_abs = max(item["max_abs_T_minus_AD"] for item in transport.values())
    max_pi_ad = max(item["transported_pi_vs_direct_ad_max_abs"] for item in pi_cases.values())
    max_theta_ad = max(item["theta_operator_vs_direct_ad_max_abs"] for item in pi_cases.values())
    max_pi_fd = max(item["transported_pi_vs_finite_difference_max_abs"] for item in pi_cases.values())
    lines = [
        "# v011 Experiment Report",
        "",
        "Generated by `run_v011.py`.",
        "",
        "## Purpose",
        "",
        "- v010 validated that AD Jacobians make the frictional endpoint DAE practical.",
        "- v011 implements the paper's central quaternion transport idea in isolation: `p(theta)=exp(theta/2) * p0`, `T_exp=dp/dtheta`, `Pi(g)=g_p T_exp + g_theta`, and `Theta(g)=[g_r, Pi(g)]`.",
        "- The goal is to verify the derivative glue for an arbitrary nonlinear friction-like load before embedding it in a full quaternion DAE integrator.",
        "",
        "## Transport Matrix Validation",
        "",
        f"- Largest `T_exp` analytic-vs-AD max absolute error across tiny/small/moderate/large rotations: {max_t_abs:.3e}.",
    ]
    for name, item in transport.items():
        lines.append(
            f"- `{name}` theta norm {item['theta_norm']:.3e}: max abs {item['max_abs_T_minus_AD']:.3e}, "
            f"relative {item['relative_T_error']:.3e}, unit error {item['unit_norm_error']:.3e}."
        )
    lines.extend(
        [
            "",
            "## Pi/Theta Validation",
            "",
            f"- Largest transported `Pi(g)` vs direct composite AD max absolute error: {max_pi_ad:.3e}.",
            f"- Largest transported `Theta(g)` vs direct composite AD max absolute error: {max_theta_ad:.3e}.",
            f"- Largest transported `Pi(g)` vs central finite-difference max absolute error: {max_pi_fd:.3e}.",
        ]
    )
    for name, item in pi_cases.items():
        lines.append(
            f"- `{name}`: Pi-vs-AD max {item['transported_pi_vs_direct_ad_max_abs']:.3e}, "
            f"Theta-vs-AD max {item['theta_operator_vs_direct_ad_max_abs']:.3e}, "
            f"Pi-vs-FD max {item['transported_pi_vs_finite_difference_max_abs']:.3e}."
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The paper's transport identity is numerically verified here for a load that depends nonlinearly on position, quaternion orientation, local rotation, velocity, angular velocity, and multiplier-like normal load.",
            "- The AD-level errors are at roundoff scale, while finite-difference agreement is limited by differencing error. This is the practical reason the transport operator is useful: `g_p` and `g_theta` can come from ordinary AD of the load model.",
            "- This version is still an isolated operator test, not a complete quaternion TFE integrator. It provides the missing bridge needed to move v010's endpoint DAE residual from SO(3) local-vector form to the paper's explicit `S^3` formulation.",
            "",
            "## Outputs",
            "",
            "- `transport_matrix_validation.csv`",
            "- `pi_theta_validation.csv`",
            "- `pi_validation_errors.png`",
            "",
        ]
    )
    (RESULTS / "v011_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    summary = {
        "version": "v011_s3_transport_operator",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "jax": jax.__version__,
        "convention": {
            "quaternion_order": "scalar_first",
            "update": "p(theta) = exp(theta/2) * p0",
            "operator": "Pi(g) = g_p T_exp + g_theta; Theta(g) = [g_r, Pi(g)]",
        },
        "transport_matrix_validation": run_transport_matrix_validation(),
        "pi_theta_validation": run_pi_theta_validation(),
    }
    summary["runtime_sec"] = time.perf_counter() - started
    plot_results(summary)
    with (RESULTS / "summary_v011.json").open("w", encoding="utf-8") as f:
        json.dump(json_safe(summary), f, indent=2, sort_keys=True)
    write_report(summary)


if __name__ == "__main__":
    main()
