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
V016_PATH = ROOT / "v016_trapezoidal_baseline" / "run_v016.py"

ORDER_CASES = {
    "frictionless": {"friction_mu": 0.0, "friction_eps": 0.5, "viscous_damping": 0.0},
    "smooth_friction": {"friction_mu": 0.08, "friction_eps": 0.5, "viscous_damping": 0.04},
    "sharp_friction": {"friction_mu": 0.08, "friction_eps": 0.05, "viscous_damping": 0.04},
}
METHODS = [
    "reduced_lie_lobatto4_fd",
    "reduced_lie_lobatto6_fd",
    "quaternion_gauss_lie6_endpoint_jax",
]
HS = [0.1, 0.05, 0.025]
T_FINAL_ORDER = 1.0
T_FINAL_LONG = 20.0
H_LONG = 0.05


def load_v016_module():
    spec = importlib.util.spec_from_file_location("v016_trapezoidal", V016_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


base = load_v016_module()
qp = base.qp


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


def collocation_coefficients(nodes: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    nodes = np.asarray(nodes, dtype=float)
    n = len(nodes)
    A = np.zeros((n, n), dtype=float)
    b = np.zeros(n, dtype=float)
    for j in range(n):
        poly = np.poly1d([1.0])
        denom = 1.0
        for m in range(n):
            if m == j:
                continue
            poly *= np.poly1d([1.0, -nodes[m]])
            denom *= nodes[j] - nodes[m]
        ipoly = np.polyint(poly / denom)
        for i in range(n):
            A[i, j] = ipoly(nodes[i]) - ipoly(0.0)
        b[j] = ipoly(1.0) - ipoly(0.0)
    return A, b


def lobatto_nodes(n_stages: int) -> np.ndarray:
    if n_stages == 3:
        return np.array([0.0, 0.5, 1.0])
    if n_stages == 4:
        root5 = np.sqrt(5.0)
        return np.array([0.0, 0.5 - root5 / 10.0, 0.5 + root5 / 10.0, 1.0])
    raise ValueError(f"unsupported Lobatto stage count: {n_stages}")


def reduced_vector_field(p0: np.ndarray, y: np.ndarray, params) -> np.ndarray:
    u = y[:3]
    w = y[3:6]
    p = qp.compose_right_quat(p0, u)
    return np.concatenate((qp.right_jacobian_inverse_apply(u, w), qp.reduced_rhs_w(p, w, params)))


def stage_guess(state, h: float, nodes: np.ndarray, params) -> np.ndarray:
    blocks = []
    for c in nodes[1:]:
        guess, _ = qp.reduced_step_rkmk4(state, float(c * h), params)
        u = qp.log_so3(qp.quat_to_rot(state.p).T @ qp.quat_to_rot(guess.p))
        blocks.append(np.concatenate((u, guess.w)))
    return np.concatenate(blocks)


def unpack_unknown_stages(x: np.ndarray, n_stages: int) -> list[np.ndarray]:
    stages = [None] * n_stages
    offset = 0
    for i in range(1, n_stages):
        stages[i] = x[offset : offset + 6]
        offset += 6
    return stages


def reduced_lie_lobatto_step(
    state,
    h: float,
    params,
    n_stages: int,
    tol: float = 1.0e-11,
    max_iters: int = 14,
) -> tuple[object, int, dict]:
    nodes = lobatto_nodes(n_stages)
    A, _ = collocation_coefficients(nodes)
    y0 = np.concatenate((np.zeros(3), state.w))
    f0 = reduced_vector_field(state.p, y0, params)
    x = stage_guess(state, h, nodes, params)

    def residual(z: np.ndarray) -> np.ndarray:
        stages = unpack_unknown_stages(z, n_stages)
        y = [y0] + stages[1:]
        f = [f0] + [reduced_vector_field(state.p, y[i], params) for i in range(1, n_stages)]
        out = []
        for i in range(1, n_stages):
            coll = y0 + h * sum(A[i, j] * f[j] for j in range(n_stages))
            out.append(y[i] - coll)
        return np.concatenate(out)

    last_norm = np.inf
    for it in range(max_iters):
        res = residual(x)
        last_norm = float(np.linalg.norm(res))
        if last_norm < tol:
            break
        jac = base.finite_difference_jacobian(residual, x)
        delta = np.linalg.solve(jac, -res)
        x = x + delta
        if float(np.linalg.norm(delta)) < tol:
            break
    else:
        raise RuntimeError(f"Lie-Lobatto{2 * n_stages - 2} Newton failed, residual={last_norm:.3e}")

    stages = unpack_unknown_stages(x, n_stages)
    y_end = stages[-1]
    p_end = qp.compose_right_quat(state.p, y_end[:3])
    next_state = base.reconstruct_state(p_end, y_end[3:6], params)
    cn, cv = qp.constraint_norms(next_state, params)
    return (
        next_state,
        it + 1,
        {
            "newton_iterations": it + 1,
            "residual_norm": last_norm,
            "max_endpoint_constraint_norm": cn,
            "max_endpoint_velocity_constraint_norm": cv,
            "max_quaternion_unit_error": float(abs(np.linalg.norm(next_state.p) - 1.0)),
        },
    )


def integrate_lobatto(method: str, h: float, t_final: float, params) -> dict:
    n_stages = 3 if method == "reduced_lie_lobatto4_fd" else 4
    state = qp.initial_state(params)
    n_steps = int(round(t_final / h))
    if abs(n_steps * h - t_final) > 1.0e-12:
        raise ValueError("h must divide t_final")
    E0 = qp.energy_state(state, params)
    prev_energy = E0
    max_energy = 0.0
    max_step_energy_increase = 0.0
    max_constraint = 0.0
    max_velocity_constraint = 0.0
    max_quat_unit = abs(np.linalg.norm(state.p) - 1.0)
    total_iters = 0
    max_residual = 0.0
    for _ in range(n_steps):
        state, niters, diag = reduced_lie_lobatto_step(state, h, params, n_stages=n_stages)
        total_iters += niters
        max_residual = max(max_residual, diag["residual_norm"])
        cn, cv = qp.constraint_norms(state, params)
        energy = qp.energy_state(state, params)
        max_step_energy_increase = max(max_step_energy_increase, energy - prev_energy)
        prev_energy = energy
        max_constraint = max(max_constraint, cn)
        max_velocity_constraint = max(max_velocity_constraint, cv)
        max_energy = max(max_energy, abs(energy - E0) / max(abs(E0), 1.0e-30))
        max_quat_unit = max(max_quat_unit, float(abs(np.linalg.norm(state.p) - 1.0)))
    final_energy = qp.energy_state(state, params)
    return {
        "state": state,
        "steps": n_steps,
        "max_energy_relative_error": max_energy,
        "final_energy_change": final_energy - E0,
        "final_energy_relative_change": (final_energy - E0) / max(abs(E0), 1.0e-30),
        "max_step_energy_increase": max_step_energy_increase,
        "max_endpoint_constraint_norm": max_constraint,
        "max_endpoint_velocity_constraint_norm": max_velocity_constraint,
        "max_quaternion_unit_error": max_quat_unit,
        "total_newton_iterations": total_iters,
        "max_newton_residual_norm": max_residual,
    }


def integrate_method(method: str, h: float, t_final: float, params) -> dict:
    if method.startswith("reduced_lie_lobatto"):
        return integrate_lobatto(method, h, t_final, params)
    return qp.integrate(method, h, t_final, params)


def method_label(method: str) -> str:
    return method.replace("reduced_lie_", "").replace("_fd", "").replace("quaternion_", "").replace(
        "_endpoint_jax", ""
    )


def run_order_cases() -> tuple[list[dict], dict]:
    rows = []
    summary = {}
    for case_name, param_kwargs in ORDER_CASES.items():
        params = qp.make_params(**param_kwargs)
        base.warm_jax(params)
        ref_h = T_FINAL_ORDER / 131072.0
        ref = qp.integrate("reduced_rkmk4", ref_h, T_FINAL_ORDER, params)
        method_summary = {}
        for method in METHODS:
            orientation_errors = []
            omega_errors = []
            runs = {}
            for h in HS:
                start = time.perf_counter()
                out = integrate_method(method, h, T_FINAL_ORDER, params)
                runtime = time.perf_counter() - start
                oerr, werr = base.state_error(ref["state"], out["state"])
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
                        "runtime_sec": f"{runtime:.8e}",
                        "total_newton_iterations": out["total_newton_iterations"],
                        "max_endpoint_constraint_norm": f"{out['max_endpoint_constraint_norm']:.16e}",
                        "max_endpoint_velocity_constraint_norm": f"{out['max_endpoint_velocity_constraint_norm']:.16e}",
                        "max_quaternion_unit_error": f"{out['max_quaternion_unit_error']:.16e}",
                        "final_energy_relative_change": f"{out['final_energy_relative_change']:.16e}",
                        "max_step_energy_increase": f"{out['max_step_energy_increase']:.16e}",
                    }
                )
                runs[str(h)] = {
                    "orientation_error_rad": oerr,
                    "omega_l2_error": werr,
                    "runtime_sec": runtime,
                    "total_newton_iterations": out["total_newton_iterations"],
                    "max_endpoint_constraint_norm": out["max_endpoint_constraint_norm"],
                    "max_endpoint_velocity_constraint_norm": out["max_endpoint_velocity_constraint_norm"],
                    "max_quaternion_unit_error": out["max_quaternion_unit_error"],
                    "final_energy_relative_change": out["final_energy_relative_change"],
                    "max_step_energy_increase": out["max_step_energy_increase"],
                }
            method_summary[method] = {
                "orientation_observed_order": qp.estimate_order(HS, orientation_errors),
                "omega_observed_order": qp.estimate_order(HS, omega_errors),
                "runs": runs,
            }
        summary[case_name] = {
            "params": param_kwargs,
            "reference_method": "reduced_rkmk4",
            "reference_h": ref_h,
            "methods": method_summary,
        }
    write_csv(RESULTS / "order_lobatto.csv", rows)
    return rows, summary


def run_long_cases() -> tuple[list[dict], dict]:
    rows = []
    summary = {}
    cases = {
        "frictionless_long": qp.make_params(friction_mu=0.0, friction_eps=0.5, viscous_damping=0.0),
        "sharp_friction_long": qp.make_params(friction_mu=0.08, friction_eps=0.05, viscous_damping=0.04),
    }
    for case_name, params in cases.items():
        base.warm_jax(params)
        case_summary = {}
        for method in METHODS:
            start = time.perf_counter()
            out = integrate_method(method, H_LONG, T_FINAL_LONG, params)
            runtime = time.perf_counter() - start
            rows.append(
                {
                    "case": case_name,
                    "method": method,
                    "h": f"{H_LONG:.10g}",
                    "t_final": f"{T_FINAL_LONG:.10g}",
                    "runtime_sec": f"{runtime:.8e}",
                    "steps": out["steps"],
                    "total_newton_iterations": out["total_newton_iterations"],
                    "max_energy_relative_error": f"{out['max_energy_relative_error']:.16e}",
                    "final_energy_relative_change": f"{out['final_energy_relative_change']:.16e}",
                    "max_step_energy_increase": f"{out['max_step_energy_increase']:.16e}",
                    "max_endpoint_constraint_norm": f"{out['max_endpoint_constraint_norm']:.16e}",
                    "max_endpoint_velocity_constraint_norm": f"{out['max_endpoint_velocity_constraint_norm']:.16e}",
                    "max_quaternion_unit_error": f"{out['max_quaternion_unit_error']:.16e}",
                }
            )
            item = dict(out)
            item.pop("state")
            item["runtime_sec"] = runtime
            case_summary[method] = item
        summary[case_name] = case_summary
    write_csv(RESULTS / "longrun_lobatto.csv", rows)
    return rows, summary


def plot_order(summary: dict) -> None:
    import matplotlib.pyplot as plt

    cases = list(summary.keys())
    x = np.arange(len(cases))
    width = 0.25
    plt.figure(figsize=(8.0, 4.8))
    for idx, method in enumerate(METHODS):
        orders = [summary[case]["methods"][method]["orientation_observed_order"] for case in cases]
        plt.bar(x + (idx - 1) * width, orders, width, label=method_label(method))
    plt.xticks(x, cases, rotation=15, ha="right")
    plt.ylabel("orientation observed order")
    plt.title("Observed Order: Reduced Lie-Lobatto vs Gauss6")
    plt.grid(True, axis="y", alpha=0.35)
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(RESULTS / "order_lobatto_comparison.png", dpi=180)
    plt.close()


def write_report(order_summary: dict, long_summary: dict) -> None:
    lines = [
        "# v018 Experiment Report",
        "",
        "Generated by `run_v018.py`.",
        "",
        "## Purpose",
        "",
        "- Test a TFE/Gauss-Lobatto-style endpoint-node collocation direction on the reduced fixed-pivot quaternion benchmark.",
        "- Compare reduced Lobatto order-4 and order-6 targets against the current Gauss6 endpoint candidate.",
        "- This is not the paper's full absolute-coordinate TFE formulation, but it isolates the node-family question before moving more code into the larger DAE residual.",
        "",
        "## Order Results",
        "",
    ]
    for case_name, case in order_summary.items():
        lines.append(f"### {case_name}")
        for method in METHODS:
            item = case["methods"][method]
            fine = item["runs"]["0.025"]
            lines.append(
                f"- `{method}`: orientation order {item['orientation_observed_order']:.3f}, "
                f"omega order {item['omega_observed_order']:.3f}, h=0.025 orientation error "
                f"{fine['orientation_error_rad']:.3e}, runtime {fine['runtime_sec']:.3f}s."
            )
        lob6 = case["methods"]["reduced_lie_lobatto6_fd"]["runs"]["0.025"]
        g6 = case["methods"]["quaternion_gauss_lie6_endpoint_jax"]["runs"]["0.025"]
        lines.append(
            f"- Gauss6 vs reduced Lobatto6 at h=0.025: "
            f"{lob6['orientation_error_rad'] / max(g6['orientation_error_rad'], 1e-30):.2e}x lower "
            f"orientation error for Gauss6 at {g6['runtime_sec'] / max(lob6['runtime_sec'], 1e-30):.2f}x runtime."
        )
        lines.append("")
    lines.extend(["## Long Runs", ""])
    for case_name, methods in long_summary.items():
        lines.append(f"### {case_name}")
        for method in METHODS:
            item = methods[method]
            lines.append(
                f"- `{method}`: 20s h=0.05 max energy relative error {item['max_energy_relative_error']:.3e}, "
                f"final energy relative change {item['final_energy_relative_change']:.3e}, "
                f"max step energy increase {item['max_step_energy_increase']:.3e}, runtime {item['runtime_sec']:.3f}s."
            )
        lines.append("")
    lines.extend(
        [
            "## Interpretation",
            "",
            "- Reduced Lie-Lobatto confirms that endpoint-node collocation can reach the expected fourth- and sixth-order behavior when the friction regularization is smooth.",
            "- Lobatto6 is accuracy-competitive with Gauss6 in smooth cases, sometimes giving a slightly smaller fine-step orientation error, but it is much slower in this finite-difference reduced prototype.",
            "- In the sharp-friction case, both Lobatto6 and Gauss6 are order-limited; Gauss6 is slightly more accurate and much faster at h=0.025.",
            "- In long frictionless runs, Lobatto6 preserves energy well but still trails Gauss6 on max energy error and runtime.",
            "- The result does not justify replacing Gauss6 with Lobatto6 as the current best integrator. It does justify keeping Gauss-Lobatto nodes as a candidate for a full TFE-style residual if endpoint conditioning, not raw accuracy, becomes the bottleneck.",
            "",
            "## Outputs",
            "",
            "- `order_lobatto.csv`",
            "- `longrun_lobatto.csv`",
            "- `summary_v018.json`",
            "- `order_lobatto_comparison.png`",
            "",
        ]
    )
    (RESULTS / "v018_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    _, order_summary = run_order_cases()
    _, long_summary = run_long_cases()
    plot_order(order_summary)
    summary = {
        "version": "v018_lobatto_endpoint_baseline",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "model": {
            "order_cases": ORDER_CASES,
            "methods": METHODS,
            "step_sizes": HS,
            "t_final_order": T_FINAL_ORDER,
            "t_final_long": T_FINAL_LONG,
            "h_long": H_LONG,
        },
        "order": order_summary,
        "long_run": long_summary,
        "runtime_sec": time.perf_counter() - started,
    }
    with (RESULTS / "summary_v018.json").open("w", encoding="utf-8") as f:
        json.dump(json_safe(summary), f, indent=2, sort_keys=True)
    write_report(order_summary, long_summary)


if __name__ == "__main__":
    main()
