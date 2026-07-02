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
from scipy import sparse
from scipy.sparse import linalg as spla


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RESULTS = HERE / "results"
V029_PATH = ROOT / "v029_double_revolute_pivotva_dae" / "run_v029.py"

CASES = {
    "double_revolute_smooth": 0.50,
    "double_revolute_sharp": 0.05,
}
METHODS = [
    "double_revolute_gauss4_fullva",
    "double_revolute_gauss6_pivotva",
    "double_revolute_gauss6_fullva",
]
SOLVERS = ["dense", "sparse_csr"]
H = 0.02
T_FINAL = 0.10
REF_H = 0.01
REFERENCE_METHOD = "double_revolute_gauss6_fullva"
SPARSITY_ATOL = 1.0e-12
CSV_COLUMNS = [
    "case",
    "method",
    "solver",
    "h",
    "status",
    "error_message",
    "steps",
    "orientation_error_rad",
    "omega_l2_error",
    "runtime_sec",
    "total_newton_iterations",
    "total_residual_eval_sec",
    "total_jacobian_eval_sec",
    "total_linear_solve_sec",
    "avg_linear_solve_sec",
    "avg_jacobian_density",
    "max_linear_residual_norm",
    "max_endpoint_constraint_norm",
    "max_endpoint_velocity_constraint_norm",
    "max_stage_pivot_acceleration_constraint_norm",
    "max_stage_axis_acceleration_constraint_norm",
    "max_quaternion_unit_error",
]


def load_v029():
    spec = importlib.util.spec_from_file_location("v029_double_revolute", V029_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


v029 = load_v029()


def json_safe(obj: object) -> object:
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {key: json_safe(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [json_safe(value) for value in obj]
    if isinstance(obj, tuple):
        return [json_safe(value) for value in obj]
    if isinstance(obj, float) and not np.isfinite(obj):
        return None
    return obj


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def base_method(method: str) -> str:
    return v029.base_method(method)


def residual_mode(method: str) -> str:
    return v029.residual_mode(method)


def method_stage_count(method: str) -> int:
    raw_method = base_method(method)
    if raw_method == "double_revolute_gauss4":
        return 2
    if raw_method == "double_revolute_gauss6":
        return 3
    raise ValueError(f"unknown method {method}")


def select_residual(mode: str, n_stages: int):
    if n_stages == 2 and mode == "raw":
        return v029.R2_RAW_VALUE, v029.R2_RAW_JAC, 42
    if n_stages == 3 and mode == "raw":
        return v029.R3_RAW_VALUE, v029.R3_RAW_JAC, 54
    if n_stages == 2 and mode == "pivot_va":
        return v029.R2_PIVOT_VALUE, v029.R2_PIVOT_JAC, 46
    if n_stages == 3 and mode == "pivot_va":
        return v029.R3_PIVOT_VALUE, v029.R3_PIVOT_JAC, 60
    if n_stages == 2 and mode == "full_va":
        return v029.R2_FULL_VALUE, v029.R2_FULL_JAC, 50
    if n_stages == 3 and mode == "full_va":
        return v029.R3_FULL_VALUE, v029.R3_FULL_JAC, 64
    raise ValueError(f"unsupported stage count/mode {n_stages}/{mode}")


def build_args(state, h: float, params):
    import jax.numpy as jnp

    state0 = (
        jnp.asarray(state.r1, dtype=jnp.float64),
        jnp.asarray(state.p1, dtype=jnp.float64),
        jnp.asarray(state.v1, dtype=jnp.float64),
        jnp.asarray(state.w1, dtype=jnp.float64),
        jnp.asarray(state.r2, dtype=jnp.float64),
        jnp.asarray(state.p2, dtype=jnp.float64),
        jnp.asarray(state.v2, dtype=jnp.float64),
        jnp.asarray(state.w2, dtype=jnp.float64),
    )
    return (
        state0,
        jnp.asarray(h, dtype=jnp.float64),
        jnp.asarray(params.mass1, dtype=jnp.float64),
        jnp.asarray(params.mass2, dtype=jnp.float64),
        jnp.asarray(params.J1, dtype=jnp.float64),
        jnp.asarray(params.J2, dtype=jnp.float64),
        jnp.asarray(params.s1_ground, dtype=jnp.float64),
        jnp.asarray(params.s1_tip, dtype=jnp.float64),
        jnp.asarray(params.s2_joint, dtype=jnp.float64),
        jnp.asarray(params.gravity, dtype=jnp.float64),
        jnp.asarray(params.hinge_axis_body, dtype=jnp.float64),
        jnp.asarray(params.mu_s, dtype=jnp.float64),
        jnp.asarray(params.mu_d, dtype=jnp.float64),
        jnp.asarray(params.stribeck_velocity, dtype=jnp.float64),
        jnp.asarray(params.viscous_damping, dtype=jnp.float64),
        jnp.asarray(params.friction_radius, dtype=jnp.float64),
        jnp.asarray(params.external_torque1_body, dtype=jnp.float64),
        jnp.asarray(params.external_torque2_body, dtype=jnp.float64),
    )


def solve_newton_linear_system(jac: np.ndarray, rhs: np.ndarray, solver: str) -> tuple[np.ndarray, float, float, float]:
    start = time.perf_counter()
    if solver == "dense":
        delta = np.linalg.solve(jac, rhs)
        density = float(np.count_nonzero(np.abs(jac) > SPARSITY_ATOL) / jac.size)
    elif solver == "sparse_csr":
        mask = np.abs(jac) > SPARSITY_ATOL
        density = float(mask.sum() / jac.size)
        csr = sparse.csr_matrix(np.where(mask, jac, 0.0))
        delta = spla.spsolve(csr, rhs)
    else:
        raise ValueError(f"unknown linear solver {solver}")
    solve_sec = time.perf_counter() - start
    linear_residual = float(np.linalg.norm(jac @ delta - rhs))
    return np.asarray(delta, dtype=float), solve_sec, density, linear_residual


def gauss_step_with_solver(state, h: float, params, n_stages: int, mode: str, solver: str):
    import jax.numpy as jnp

    _, _, b = v029.qp.gauss_legendre_coefficients(n_stages)
    x = v029.stage_guess(state, h, params, n_stages)
    args = build_args(state, h, params)
    value, jacobian, max_iters = select_residual(mode, n_stages)
    total_residual_sec = 0.0
    total_jacobian_sec = 0.0
    total_linear_sec = 0.0
    density_sum = 0.0
    linear_residual_max = 0.0
    linear_solves = 0
    last_norm = np.inf
    for it in range(max_iters):
        x_jax = jnp.asarray(x, dtype=jnp.float64)
        start = time.perf_counter()
        res = np.asarray(value(x_jax, *args), dtype=float)
        total_residual_sec += time.perf_counter() - start
        last_norm = float(np.linalg.norm(res))
        if last_norm < 1.0e-11:
            break
        start = time.perf_counter()
        jac = np.asarray(jacobian(x_jax, *args), dtype=float)
        total_jacobian_sec += time.perf_counter() - start
        delta, solve_sec, density, lin_res = solve_newton_linear_system(jac, -res, solver)
        total_linear_sec += solve_sec
        density_sum += density
        linear_residual_max = max(linear_residual_max, lin_res)
        linear_solves += 1
        x = x + delta
        if float(np.linalg.norm(delta)) < 1.0e-11:
            break
    else:
        raise RuntimeError(f"double revolute sparse Newton solve failed, residual={last_norm:.3e}")

    stages = v029.unpack_stages(x, n_stages)
    k1 = [v029.qp.right_jacobian_inverse_apply(st["u1"], st["w1"]) for st in stages]
    k2 = [v029.qp.right_jacobian_inverse_apply(st["u2"], st["w2"]) for st in stages]
    next_state = v029.State(
        r1=state.r1 + h * sum(b[j] * stages[j]["v1"] for j in range(n_stages)),
        p1=v029.qp.compose_right_quat(state.p1, h * sum(b[j] * k1[j] for j in range(n_stages))),
        v1=state.v1 + h * sum(b[j] * stages[j]["a1"] for j in range(n_stages)),
        w1=state.w1 + h * sum(b[j] * stages[j]["alpha1"] for j in range(n_stages)),
        r2=state.r2 + h * sum(b[j] * stages[j]["v2"] for j in range(n_stages)),
        p2=v029.qp.compose_right_quat(state.p2, h * sum(b[j] * k2[j] for j in range(n_stages))),
        v2=state.v2 + h * sum(b[j] * stages[j]["a2"] for j in range(n_stages)),
        w2=state.w2 + h * sum(b[j] * stages[j]["alpha2"] for j in range(n_stages)),
    )

    max_stage_constraint = 0.0
    max_stage_velocity = 0.0
    max_stage_pivot_v = 0.0
    max_stage_axis_v = 0.0
    max_stage_pivot_a = 0.0
    max_stage_axis_a = 0.0
    max_stage_acc = 0.0
    max_lambda = 0.0
    max_power = -np.inf
    for st in stages:
        p1 = v029.qp.compose_right_quat(state.p1, st["u1"])
        p2 = v029.qp.compose_right_quat(state.p2, st["u2"])
        st_state = v029.State(st["r1"], p1, st["v1"], st["w1"], st["r2"], p2, st["v2"], st["w2"])
        max_stage_constraint = max(max_stage_constraint, float(np.linalg.norm(v029.double_constraints_np(st_state, params))))
        max_stage_velocity = max(
            max_stage_velocity, float(np.linalg.norm(v029.double_velocity_constraints_np(st_state, params)))
        )
        pv, av, pa, aa = v029.constraint_parts_np(
            st["r1"],
            p1,
            st["v1"],
            st["w1"],
            st["a1"],
            st["alpha1"],
            st["r2"],
            p2,
            st["v2"],
            st["w2"],
            st["a2"],
            st["alpha2"],
            params,
        )
        max_stage_pivot_v = max(max_stage_pivot_v, pv)
        max_stage_axis_v = max(max_stage_axis_v, av)
        max_stage_pivot_a = max(max_stage_pivot_a, pa)
        max_stage_axis_a = max(max_stage_axis_a, aa)
        max_stage_acc = max(max_stage_acc, float(np.hypot(pa, aa)))
        F0 = st["lambda"][:3]
        F12 = st["lambda"][5:8]
        tau0 = v029.brown_mcphee_scalar(st["w1"][1], float(np.linalg.norm(F0)), params)
        tau12 = v029.brown_mcphee_scalar(st["w2"][1] - st["w1"][1], float(np.linalg.norm(F12)), params)
        max_power = max(max_power, float(tau0 * st["w1"][1] + tau12 * (st["w2"][1] - st["w1"][1])))
        max_lambda = max(max_lambda, float(np.linalg.norm(st["lambda"])))
    endpoint_pv, endpoint_av, _, _ = v029.constraint_parts_np(
        next_state.r1,
        next_state.p1,
        next_state.v1,
        next_state.w1,
        np.zeros(3),
        np.zeros(3),
        next_state.r2,
        next_state.p2,
        next_state.v2,
        next_state.w2,
        np.zeros(3),
        np.zeros(3),
        params,
    )
    diag = {
        "newton_iterations": it + 1,
        "stage_residual_norm": last_norm,
        "linear_solves": linear_solves,
        "total_residual_eval_sec": total_residual_sec,
        "total_jacobian_eval_sec": total_jacobian_sec,
        "total_linear_solve_sec": total_linear_sec,
        "avg_jacobian_density": density_sum / max(linear_solves, 1),
        "max_linear_residual_norm": linear_residual_max,
        "max_stage_constraint_norm": max_stage_constraint,
        "max_stage_velocity_constraint_norm": max_stage_velocity,
        "max_stage_pivot_velocity_constraint_norm": max_stage_pivot_v,
        "max_stage_axis_velocity_constraint_norm": max_stage_axis_v,
        "max_stage_pivot_acceleration_constraint_norm": max_stage_pivot_a,
        "max_stage_axis_acceleration_constraint_norm": max_stage_axis_a,
        "max_stage_acceleration_constraint_norm": max_stage_acc,
        "max_endpoint_constraint_norm": float(np.linalg.norm(v029.double_constraints_np(next_state, params))),
        "max_endpoint_velocity_constraint_norm": float(np.linalg.norm(v029.double_velocity_constraints_np(next_state, params))),
        "max_endpoint_pivot_velocity_constraint_norm": endpoint_pv,
        "max_endpoint_axis_velocity_constraint_norm": endpoint_av,
        "max_lambda_norm": max_lambda,
        "max_stage_friction_power": max_power,
        "max_quaternion_unit_error": float(
            max(abs(np.linalg.norm(next_state.p1) - 1.0), abs(np.linalg.norm(next_state.p2) - 1.0))
        ),
    }
    return next_state, it + 1, diag


def integrate_with_solver(method: str, h: float, t_final: float, params, solver: str) -> dict:
    n_steps = int(round(t_final / h))
    if abs(n_steps * h - t_final) > 1.0e-12:
        raise ValueError("h must divide t_final")
    n_stages = method_stage_count(method)
    mode = residual_mode(method)
    state = v029.initial_state(params)
    E0 = v029.energy(state, params)
    prev_energy = E0
    total_iters = 0
    total_residual_eval = 0.0
    total_jacobian_eval = 0.0
    total_linear_solve = 0.0
    total_linear_solves = 0
    density_weighted_sum = 0.0
    max_linear_residual = 0.0
    max_step_energy_increase = 0.0
    max_endpoint_constraint = 0.0
    max_endpoint_velocity = 0.0
    max_stage_pivot_a = 0.0
    max_stage_axis_a = 0.0
    max_quat = 0.0
    for _ in range(n_steps):
        state, niters, diag = gauss_step_with_solver(state, h, params, n_stages, mode, solver)
        total_iters += niters
        total_residual_eval += diag["total_residual_eval_sec"]
        total_jacobian_eval += diag["total_jacobian_eval_sec"]
        total_linear_solve += diag["total_linear_solve_sec"]
        total_linear_solves += diag["linear_solves"]
        density_weighted_sum += diag["avg_jacobian_density"] * diag["linear_solves"]
        max_linear_residual = max(max_linear_residual, diag["max_linear_residual_norm"])
        max_endpoint_constraint = max(max_endpoint_constraint, diag["max_endpoint_constraint_norm"])
        max_endpoint_velocity = max(max_endpoint_velocity, diag["max_endpoint_velocity_constraint_norm"])
        max_stage_pivot_a = max(max_stage_pivot_a, diag["max_stage_pivot_acceleration_constraint_norm"])
        max_stage_axis_a = max(max_stage_axis_a, diag["max_stage_axis_acceleration_constraint_norm"])
        max_quat = max(max_quat, diag["max_quaternion_unit_error"])
        E = v029.energy(state, params)
        max_step_energy_increase = max(max_step_energy_increase, E - prev_energy)
        prev_energy = E
    final_energy = v029.energy(state, params)
    return {
        "state": state,
        "steps": n_steps,
        "total_newton_iterations": total_iters,
        "total_residual_eval_sec": total_residual_eval,
        "total_jacobian_eval_sec": total_jacobian_eval,
        "total_linear_solve_sec": total_linear_solve,
        "avg_linear_solve_sec": total_linear_solve / max(total_linear_solves, 1),
        "avg_jacobian_density": density_weighted_sum / max(total_linear_solves, 1),
        "max_linear_residual_norm": max_linear_residual,
        "final_energy_relative_change": (final_energy - E0) / max(abs(E0), 1.0e-30),
        "max_step_energy_increase": max_step_energy_increase,
        "max_endpoint_constraint_norm": max_endpoint_constraint,
        "max_endpoint_velocity_constraint_norm": max_endpoint_velocity,
        "max_stage_pivot_acceleration_constraint_norm": max_stage_pivot_a,
        "max_stage_axis_acceleration_constraint_norm": max_stage_axis_a,
        "max_quaternion_unit_error": max_quat,
    }


def warm_jax(params) -> None:
    state = v029.initial_state(params)
    for method in METHODS:
        n_stages = method_stage_count(method)
        mode = residual_mode(method)
        gauss_step_with_solver(state, H, params, n_stages, mode, "dense")


def run_experiment() -> dict:
    rows = []
    cases = {}
    for case_name, vs in CASES.items():
        params = v029.make_params(vs)
        warm_jax(params)
        ref = integrate_with_solver(REFERENCE_METHOD, REF_H, T_FINAL, params, "sparse_csr")
        ref_state = ref["state"]
        case_runs = {}
        for method in METHODS:
            method_runs = {}
            method_states = {}
            for solver in SOLVERS:
                row = {key: "" for key in CSV_COLUMNS}
                row.update({"case": case_name, "method": method, "solver": solver, "h": f"{H:.10g}"})
                start = time.perf_counter()
                try:
                    out = integrate_with_solver(method, H, T_FINAL, params, solver)
                    runtime = time.perf_counter() - start
                    oerr, werr = v029.state_error(ref_state, out["state"])
                    item = {key: value for key, value in out.items() if key != "state"}
                    item.update(
                        {
                            "status": "ok",
                            "runtime_sec": runtime,
                            "orientation_error_rad": oerr,
                            "omega_l2_error": werr,
                        }
                    )
                    method_states[solver] = out["state"]
                    row.update(
                        {
                            "status": "ok",
                            "steps": out["steps"],
                            "orientation_error_rad": f"{oerr:.16e}",
                            "omega_l2_error": f"{werr:.16e}",
                            "runtime_sec": f"{runtime:.8e}",
                            "total_newton_iterations": out["total_newton_iterations"],
                            "total_residual_eval_sec": f"{out['total_residual_eval_sec']:.16e}",
                            "total_jacobian_eval_sec": f"{out['total_jacobian_eval_sec']:.16e}",
                            "total_linear_solve_sec": f"{out['total_linear_solve_sec']:.16e}",
                            "avg_linear_solve_sec": f"{out['avg_linear_solve_sec']:.16e}",
                            "avg_jacobian_density": f"{out['avg_jacobian_density']:.16e}",
                            "max_linear_residual_norm": f"{out['max_linear_residual_norm']:.16e}",
                            "max_endpoint_constraint_norm": f"{out['max_endpoint_constraint_norm']:.16e}",
                            "max_endpoint_velocity_constraint_norm": f"{out['max_endpoint_velocity_constraint_norm']:.16e}",
                            "max_stage_pivot_acceleration_constraint_norm": f"{out['max_stage_pivot_acceleration_constraint_norm']:.16e}",
                            "max_stage_axis_acceleration_constraint_norm": f"{out['max_stage_axis_acceleration_constraint_norm']:.16e}",
                            "max_quaternion_unit_error": f"{out['max_quaternion_unit_error']:.16e}",
                        }
                    )
                except Exception as exc:
                    runtime = time.perf_counter() - start
                    item = {"status": "failed", "error_message": str(exc), "runtime_sec": runtime}
                    row.update({"status": "failed", "error_message": str(exc), "runtime_sec": f"{runtime:.8e}"})
                rows.append(row)
                method_runs[solver] = item
            dense = method_runs.get("dense", {})
            sparse_run = method_runs.get("sparse_csr", {})
            if dense.get("status") == "ok" and sparse_run.get("status") == "ok":
                pair_oerr, pair_werr = v029.state_error(method_states["dense"], method_states["sparse_csr"])
                method_runs["dense_sparse_difference"] = {
                    "orientation_difference_rad": pair_oerr,
                    "omega_l2_difference": pair_werr,
                    "runtime_speedup_dense_over_sparse": dense["runtime_sec"] / max(sparse_run["runtime_sec"], 1.0e-30),
                    "linear_solve_speedup_dense_over_sparse": dense["total_linear_solve_sec"]
                    / max(sparse_run["total_linear_solve_sec"], 1.0e-30),
                }
            case_runs[method] = method_runs
        cases[case_name] = {
            "stribeck_velocity": vs,
            "reference_method": REFERENCE_METHOD,
            "reference_h": REF_H,
            "reference_solver": "sparse_csr",
            "reference": {key: value for key, value in ref.items() if key != "state"},
            "methods": case_runs,
        }
    write_csv(RESULTS / "double_revolute_sparse_newton_runs.csv", rows)
    return {"t_final": T_FINAL, "h": H, "cases": cases}


def plot_results(summary: dict) -> None:
    import matplotlib.pyplot as plt

    labels = []
    dense_runtime = []
    sparse_runtime = []
    dense_linear = []
    sparse_linear = []
    state_diffs = []
    for case_name, case in summary["cases"].items():
        for method in METHODS:
            runs = case["methods"][method]
            label = f"{case_name.replace('double_revolute_', '')}\n{method.replace('double_revolute_', '')}"
            labels.append(label)
            dense = runs["dense"]
            sparse_run = runs["sparse_csr"]
            dense_runtime.append(dense.get("runtime_sec", np.nan))
            sparse_runtime.append(sparse_run.get("runtime_sec", np.nan))
            dense_linear.append(dense.get("total_linear_solve_sec", np.nan))
            sparse_linear.append(sparse_run.get("total_linear_solve_sec", np.nan))
            state_diffs.append(runs.get("dense_sparse_difference", {}).get("orientation_difference_rad", np.nan))
    xs = np.arange(len(labels))

    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.2))
    axes[0].bar(xs - 0.18, dense_runtime, width=0.36, label="dense Newton")
    axes[0].bar(xs + 0.18, sparse_runtime, width=0.36, label="CSR Newton")
    axes[0].set_yscale("log")
    axes[0].set_ylabel("runtime seconds")
    axes[0].set_xticks(xs)
    axes[0].set_xticklabels(labels, rotation=70, ha="right", fontsize=7)
    axes[0].grid(True, axis="y", alpha=0.35)
    axes[0].legend()

    axes[1].bar(xs - 0.18, dense_linear, width=0.36, label="dense solve total")
    axes[1].bar(xs + 0.18, sparse_linear, width=0.36, label="CSR solve total")
    axes[1].set_yscale("log")
    axes[1].set_ylabel("linear solve seconds")
    axes[1].set_xticks(xs)
    axes[1].set_xticklabels(labels, rotation=70, ha="right", fontsize=7)
    axes[1].grid(True, axis="y", alpha=0.35)
    axes[1].legend()
    fig.tight_layout()
    fig.savefig(RESULTS / "double_revolute_sparse_newton_runtime.png", dpi=180)
    plt.close(fig)

    plt.figure(figsize=(7.5, 4.2))
    plt.bar(xs, state_diffs)
    plt.yscale("log")
    plt.ylabel("dense vs CSR final orientation difference rad")
    plt.xticks(xs, labels, rotation=70, ha="right", fontsize=7)
    plt.grid(True, axis="y", alpha=0.35)
    plt.tight_layout()
    plt.savefig(RESULTS / "double_revolute_sparse_newton_equivalence.png", dpi=180)
    plt.close()


def write_report(summary: dict) -> None:
    lines = [
        "# v031 Experiment Report",
        "",
        "Generated by `run_v031.py`.",
        "",
        "## Purpose",
        "",
        "- Convert the v030 Jacobian sparsity result into an actual Newton-loop comparison.",
        "- Reuse the v029 double-revolute quaternion DAE residual unchanged.",
        "- Compare dense `numpy.linalg.solve` against thresholded CSR `scipy.sparse.linalg.spsolve` inside every Newton iteration.",
        "- Measure end-to-end runtime, linear-solve time, constraint quality, and dense-vs-sparse trajectory agreement.",
        "",
        "## Results",
        "",
    ]
    best_runtime = None
    best_linear = None
    worst_state_diff = 0.0
    for case_name, case in summary["cases"].items():
        lines.append(f"### {case_name}")
        for method in METHODS:
            runs = case["methods"][method]
            dense = runs["dense"]
            sparse_run = runs["sparse_csr"]
            if dense.get("status") != "ok" or sparse_run.get("status") != "ok":
                lines.append(f"- `{method}`: dense status {dense.get('status')}, sparse status {sparse_run.get('status')}.")
                continue
            diff = runs["dense_sparse_difference"]
            runtime_speedup = diff["runtime_speedup_dense_over_sparse"]
            linear_speedup = diff["linear_solve_speedup_dense_over_sparse"]
            worst_state_diff = max(worst_state_diff, diff["orientation_difference_rad"])
            if best_runtime is None or runtime_speedup > best_runtime[0]:
                best_runtime = (runtime_speedup, case_name, method)
            if best_linear is None or linear_speedup > best_linear[0]:
                best_linear = (linear_speedup, case_name, method)
            lines.append(
                f"- `{method}`: runtime dense {dense['runtime_sec']:.3f}s vs CSR {sparse_run['runtime_sec']:.3f}s "
                f"(speedup {runtime_speedup:.2f}x); linear solve dense {dense['total_linear_solve_sec']:.3e}s "
                f"vs CSR {sparse_run['total_linear_solve_sec']:.3e}s (speedup {linear_speedup:.2f}x); "
                f"final orientation diff {diff['orientation_difference_rad']:.3e}; "
                f"CSR endpoint velocity {sparse_run['max_endpoint_velocity_constraint_norm']:.3e}."
            )
        lines.append("")
    if best_runtime and best_linear:
        lines.extend(
            [
                "## Interpretation",
                "",
                f"- Best end-to-end runtime speedup is {best_runtime[0]:.2f}x for `{best_runtime[1]} {best_runtime[2]}`.",
                f"- Best Newton linear-solve speedup is {best_linear[0]:.2f}x for `{best_linear[1]} {best_linear[2]}`.",
                f"- Worst dense-vs-CSR final orientation difference is {worst_state_diff:.3e} rad over the tested runs.",
                "- Sparse linear algebra now works inside the actual time integrator, not just as a post-hoc Jacobian diagnostic.",
                "- The remaining cost is still JAX dense Jacobian materialization. v031 is therefore an implementation bridge, not the final scalable solver architecture.",
                "- The next useful step is structured sparse/block Jacobian assembly or Newton-Krylov, plus a less planar/larger lower-pair benchmark.",
                "",
            ]
        )
    lines.extend(
        [
            "## Outputs",
            "",
            "- `double_revolute_sparse_newton_runs.csv`",
            "- `summary_v031.json`",
            "- `double_revolute_sparse_newton_runtime.png`",
            "- `double_revolute_sparse_newton_equivalence.png`",
            "",
        ]
    )
    (RESULTS / "v031_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    experiment = run_experiment()
    plot_results(experiment)
    summary = {
        "version": "v031_sparse_newton_double_revolute",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "scipy": __import__("scipy").__version__,
        "source_version": "v029_double_revolute_pivotva_dae",
        "diagnostic_parent": "v030_double_revolute_jacobian_sparsity",
        "model": {
            "cases": CASES,
            "methods": METHODS,
            "solvers": SOLVERS,
            "h": H,
            "t_final": T_FINAL,
            "reference_method": REFERENCE_METHOD,
            "reference_h": REF_H,
            "sparsity_atol": SPARSITY_ATOL,
        },
        "experiment": experiment,
        "runtime_sec": time.perf_counter() - started,
    }
    with (RESULTS / "summary_v031.json").open("w", encoding="utf-8") as f:
        json.dump(json_safe(summary), f, indent=2, sort_keys=True)
    write_report(experiment)


if __name__ == "__main__":
    main()
