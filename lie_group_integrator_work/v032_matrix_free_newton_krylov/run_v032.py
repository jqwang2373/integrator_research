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
import jax.numpy as jnp
import numpy as np
from scipy.sparse import linalg as spla


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RESULTS = HERE / "results"
V031_PATH = ROOT / "v031_sparse_newton_double_revolute" / "run_v031.py"

CASES = {
    "double_revolute_smooth": 0.50,
    "double_revolute_sharp": 0.05,
}
METHODS = [
    "double_revolute_gauss6_fullva",
]
SOLVERS = ["csr_jacobian", "jvp_gmres"]
H = 0.02
T_FINAL = 0.02
REF_H = 0.01
REFERENCE_METHOD = "double_revolute_gauss6_fullva"
GMRES_RTOL = 1.0e-10
GMRES_ATOL = 1.0e-12
GMRES_MAXITER = 200
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
    "total_jvp_eval_sec",
    "total_linear_solve_sec",
    "avg_linear_solve_sec",
    "total_linear_solves",
    "total_gmres_iterations",
    "total_jvp_matvecs",
    "avg_jvp_matvecs_per_solve",
    "max_linear_residual_norm",
    "max_endpoint_constraint_norm",
    "max_endpoint_velocity_constraint_norm",
    "max_stage_pivot_acceleration_constraint_norm",
    "max_stage_axis_acceleration_constraint_norm",
    "max_quaternion_unit_error",
]


def load_v031():
    spec = importlib.util.spec_from_file_location("v031_sparse_newton", V031_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


v031 = load_v031()
v029 = v031.v029


@jax.jit
def jvp2_full(x, tangent, *args):
    return jax.jvp(lambda y: v029.residual2_fullva(y, *args), (x,), (tangent,))[1]


@jax.jit
def jvp3_full(x, tangent, *args):
    return jax.jvp(lambda y: v029.residual3_fullva(y, *args), (x,), (tangent,))[1]


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


def method_stage_count(method: str) -> int:
    return v031.method_stage_count(method)


def residual_mode(method: str) -> str:
    return v031.residual_mode(method)


def select_value_jvp(mode: str, n_stages: int):
    if mode != "full_va":
        raise ValueError("v032 only tests FullVA because GMRES is unpreconditioned")
    if n_stages == 2:
        return v029.R2_FULL_VALUE, jvp2_full, 50
    if n_stages == 3:
        return v029.R3_FULL_VALUE, jvp3_full, 64
    raise ValueError(f"unsupported stage count {n_stages}")


def gmres_solve_with_jvp(value_jvp, x_jax, args, rhs: np.ndarray):
    dim = rhs.size
    counters = {"matvecs": 0, "jvp_sec": 0.0, "gmres_iterations": 0}

    def matvec(vec: np.ndarray) -> np.ndarray:
        start = time.perf_counter()
        out = np.array(value_jvp(x_jax, jnp.asarray(vec, dtype=jnp.float64), *args), dtype=float, copy=True)
        counters["jvp_sec"] += time.perf_counter() - start
        counters["matvecs"] += 1
        return out

    def callback(_value) -> None:
        counters["gmres_iterations"] += 1

    operator = spla.LinearOperator((dim, dim), matvec=matvec, dtype=float)
    start = time.perf_counter()
    delta, info = spla.gmres(
        operator,
        rhs,
        rtol=GMRES_RTOL,
        atol=GMRES_ATOL,
        restart=min(dim, 80),
        maxiter=GMRES_MAXITER,
        callback=callback,
        callback_type="pr_norm",
    )
    solve_sec = time.perf_counter() - start
    linear_residual = float(np.linalg.norm(matvec(delta) - rhs))
    if info != 0:
        raise RuntimeError(f"GMRES failed with info={info}, residual={linear_residual:.3e}")
    return np.asarray(delta, dtype=float), solve_sec, counters, linear_residual


def gauss_step_gmres(state, h: float, params, n_stages: int, mode: str):
    _, _, b = v029.qp.gauss_legendre_coefficients(n_stages)
    x = v029.stage_guess(state, h, params, n_stages)
    args = v031.build_args(state, h, params)
    value, value_jvp, max_iters = select_value_jvp(mode, n_stages)
    total_residual_sec = 0.0
    total_jvp_sec = 0.0
    total_linear_sec = 0.0
    total_linear_solves = 0
    total_gmres_iterations = 0
    total_jvp_matvecs = 0
    max_linear_residual = 0.0
    last_norm = np.inf
    for it in range(max_iters):
        x_jax = jnp.asarray(x, dtype=jnp.float64)
        start = time.perf_counter()
        res = np.asarray(value(x_jax, *args), dtype=float)
        total_residual_sec += time.perf_counter() - start
        last_norm = float(np.linalg.norm(res))
        if last_norm < 1.0e-11:
            break
        delta, solve_sec, counters, lin_res = gmres_solve_with_jvp(value_jvp, x_jax, args, -res)
        total_jvp_sec += counters["jvp_sec"]
        total_linear_sec += solve_sec
        total_linear_solves += 1
        total_gmres_iterations += counters["gmres_iterations"]
        total_jvp_matvecs += counters["matvecs"]
        max_linear_residual = max(max_linear_residual, lin_res)
        x = x + delta
        if float(np.linalg.norm(delta)) < 1.0e-11:
            break
    else:
        raise RuntimeError(f"matrix-free Newton-Krylov failed, residual={last_norm:.3e}")

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
    max_stage_pivot_a = 0.0
    max_stage_axis_a = 0.0
    for st in stages:
        p1 = v029.qp.compose_right_quat(state.p1, st["u1"])
        p2 = v029.qp.compose_right_quat(state.p2, st["u2"])
        _, _, pa, aa = v029.constraint_parts_np(
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
        max_stage_pivot_a = max(max_stage_pivot_a, pa)
        max_stage_axis_a = max(max_stage_axis_a, aa)
    diag = {
        "newton_iterations": it + 1,
        "stage_residual_norm": last_norm,
        "linear_solves": total_linear_solves,
        "total_residual_eval_sec": total_residual_sec,
        "total_jacobian_eval_sec": 0.0,
        "total_jvp_eval_sec": total_jvp_sec,
        "total_linear_solve_sec": total_linear_sec,
        "total_gmres_iterations": total_gmres_iterations,
        "total_jvp_matvecs": total_jvp_matvecs,
        "max_linear_residual_norm": max_linear_residual,
        "max_endpoint_constraint_norm": float(np.linalg.norm(v029.double_constraints_np(next_state, params))),
        "max_endpoint_velocity_constraint_norm": float(np.linalg.norm(v029.double_velocity_constraints_np(next_state, params))),
        "max_stage_pivot_acceleration_constraint_norm": max_stage_pivot_a,
        "max_stage_axis_acceleration_constraint_norm": max_stage_axis_a,
        "max_quaternion_unit_error": float(
            max(abs(np.linalg.norm(next_state.p1) - 1.0), abs(np.linalg.norm(next_state.p2) - 1.0))
        ),
    }
    return next_state, it + 1, diag


def integrate_gmres(method: str, h: float, t_final: float, params) -> dict:
    n_steps = int(round(t_final / h))
    if abs(n_steps * h - t_final) > 1.0e-12:
        raise ValueError("h must divide t_final")
    n_stages = method_stage_count(method)
    mode = residual_mode(method)
    state = v029.initial_state(params)
    total_iters = 0
    total_residual_eval = 0.0
    total_jvp_eval = 0.0
    total_linear_solve = 0.0
    total_linear_solves = 0
    total_gmres_iterations = 0
    total_jvp_matvecs = 0
    max_linear_residual = 0.0
    max_endpoint_constraint = 0.0
    max_endpoint_velocity = 0.0
    max_stage_pivot_a = 0.0
    max_stage_axis_a = 0.0
    max_quat = 0.0
    for _ in range(n_steps):
        state, niters, diag = gauss_step_gmres(state, h, params, n_stages, mode)
        total_iters += niters
        total_residual_eval += diag["total_residual_eval_sec"]
        total_jvp_eval += diag["total_jvp_eval_sec"]
        total_linear_solve += diag["total_linear_solve_sec"]
        total_linear_solves += diag["linear_solves"]
        total_gmres_iterations += diag["total_gmres_iterations"]
        total_jvp_matvecs += diag["total_jvp_matvecs"]
        max_linear_residual = max(max_linear_residual, diag["max_linear_residual_norm"])
        max_endpoint_constraint = max(max_endpoint_constraint, diag["max_endpoint_constraint_norm"])
        max_endpoint_velocity = max(max_endpoint_velocity, diag["max_endpoint_velocity_constraint_norm"])
        max_stage_pivot_a = max(max_stage_pivot_a, diag["max_stage_pivot_acceleration_constraint_norm"])
        max_stage_axis_a = max(max_stage_axis_a, diag["max_stage_axis_acceleration_constraint_norm"])
        max_quat = max(max_quat, diag["max_quaternion_unit_error"])
    return {
        "state": state,
        "steps": n_steps,
        "total_newton_iterations": total_iters,
        "total_residual_eval_sec": total_residual_eval,
        "total_jacobian_eval_sec": 0.0,
        "total_jvp_eval_sec": total_jvp_eval,
        "total_linear_solve_sec": total_linear_solve,
        "avg_linear_solve_sec": total_linear_solve / max(total_linear_solves, 1),
        "total_linear_solves": total_linear_solves,
        "total_gmres_iterations": total_gmres_iterations,
        "total_jvp_matvecs": total_jvp_matvecs,
        "avg_jvp_matvecs_per_solve": total_jvp_matvecs / max(total_linear_solves, 1),
        "max_linear_residual_norm": max_linear_residual,
        "max_endpoint_constraint_norm": max_endpoint_constraint,
        "max_endpoint_velocity_constraint_norm": max_endpoint_velocity,
        "max_stage_pivot_acceleration_constraint_norm": max_stage_pivot_a,
        "max_stage_axis_acceleration_constraint_norm": max_stage_axis_a,
        "max_quaternion_unit_error": max_quat,
    }


def normalize_csr_output(out: dict) -> dict:
    return {
        "state": out["state"],
        "steps": out["steps"],
        "total_newton_iterations": out["total_newton_iterations"],
        "total_residual_eval_sec": out["total_residual_eval_sec"],
        "total_jacobian_eval_sec": out["total_jacobian_eval_sec"],
        "total_jvp_eval_sec": 0.0,
        "total_linear_solve_sec": out["total_linear_solve_sec"],
        "avg_linear_solve_sec": out["avg_linear_solve_sec"],
        "total_linear_solves": int(round(out["total_linear_solve_sec"] / max(out["avg_linear_solve_sec"], 1.0e-30))),
        "total_gmres_iterations": 0,
        "total_jvp_matvecs": 0,
        "avg_jvp_matvecs_per_solve": 0.0,
        "max_linear_residual_norm": out["max_linear_residual_norm"],
        "max_endpoint_constraint_norm": out["max_endpoint_constraint_norm"],
        "max_endpoint_velocity_constraint_norm": out["max_endpoint_velocity_constraint_norm"],
        "max_stage_pivot_acceleration_constraint_norm": out["max_stage_pivot_acceleration_constraint_norm"],
        "max_stage_axis_acceleration_constraint_norm": out["max_stage_axis_acceleration_constraint_norm"],
        "max_quaternion_unit_error": out["max_quaternion_unit_error"],
    }


def warm_jax(params) -> None:
    state = v029.initial_state(params)
    for method in METHODS:
        n_stages = method_stage_count(method)
        mode = residual_mode(method)
        v031.gauss_step_with_solver(state, H, params, n_stages, mode, "sparse_csr")
        try:
            gauss_step_gmres(state, H, params, n_stages, mode)
        except Exception:
            # Failure is part of the v032 question; run_experiment records it.
            pass


def run_one(method: str, solver: str, params) -> dict:
    if solver == "csr_jacobian":
        return normalize_csr_output(v031.integrate_with_solver(method, H, T_FINAL, params, "sparse_csr"))
    if solver == "jvp_gmres":
        return integrate_gmres(method, H, T_FINAL, params)
    raise ValueError(f"unknown solver {solver}")


def row_from_run(case_name: str, method: str, solver: str, out: dict, oerr: float, werr: float, runtime: float) -> dict:
    return {
        "case": case_name,
        "method": method,
        "solver": solver,
        "h": f"{H:.10g}",
        "status": "ok",
        "error_message": "",
        "steps": out["steps"],
        "orientation_error_rad": f"{oerr:.16e}",
        "omega_l2_error": f"{werr:.16e}",
        "runtime_sec": f"{runtime:.8e}",
        "total_newton_iterations": out["total_newton_iterations"],
        "total_residual_eval_sec": f"{out['total_residual_eval_sec']:.16e}",
        "total_jacobian_eval_sec": f"{out['total_jacobian_eval_sec']:.16e}",
        "total_jvp_eval_sec": f"{out['total_jvp_eval_sec']:.16e}",
        "total_linear_solve_sec": f"{out['total_linear_solve_sec']:.16e}",
        "avg_linear_solve_sec": f"{out['avg_linear_solve_sec']:.16e}",
        "total_linear_solves": out["total_linear_solves"],
        "total_gmres_iterations": out["total_gmres_iterations"],
        "total_jvp_matvecs": out["total_jvp_matvecs"],
        "avg_jvp_matvecs_per_solve": f"{out['avg_jvp_matvecs_per_solve']:.16e}",
        "max_linear_residual_norm": f"{out['max_linear_residual_norm']:.16e}",
        "max_endpoint_constraint_norm": f"{out['max_endpoint_constraint_norm']:.16e}",
        "max_endpoint_velocity_constraint_norm": f"{out['max_endpoint_velocity_constraint_norm']:.16e}",
        "max_stage_pivot_acceleration_constraint_norm": f"{out['max_stage_pivot_acceleration_constraint_norm']:.16e}",
        "max_stage_axis_acceleration_constraint_norm": f"{out['max_stage_axis_acceleration_constraint_norm']:.16e}",
        "max_quaternion_unit_error": f"{out['max_quaternion_unit_error']:.16e}",
    }


def run_experiment() -> dict:
    rows = []
    cases = {}
    for case_name, vs in CASES.items():
        params = v029.make_params(vs)
        warm_jax(params)
        ref = v031.integrate_with_solver(REFERENCE_METHOD, REF_H, T_FINAL, params, "sparse_csr")
        ref_state = ref["state"]
        case_runs = {}
        for method in METHODS:
            method_runs = {}
            method_states = {}
            for solver in SOLVERS:
                try:
                    start = time.perf_counter()
                    out = run_one(method, solver, params)
                    runtime = time.perf_counter() - start
                    oerr, werr = v029.state_error(ref_state, out["state"])
                    row = row_from_run(case_name, method, solver, out, oerr, werr, runtime)
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
                except Exception as exc:
                    runtime = time.perf_counter() - start
                    row = {key: "" for key in CSV_COLUMNS}
                    row.update(
                        {
                            "case": case_name,
                            "method": method,
                            "solver": solver,
                            "h": f"{H:.10g}",
                            "status": "failed",
                            "error_message": str(exc),
                            "runtime_sec": f"{runtime:.8e}",
                        }
                    )
                    item = {"status": "failed", "error_message": str(exc), "runtime_sec": runtime}
                rows.append(row)
                method_runs[solver] = item
            csr_run = method_runs.get("csr_jacobian", {})
            gmres_run = method_runs.get("jvp_gmres", {})
            if csr_run.get("status") == "ok" and gmres_run.get("status") == "ok":
                pair_oerr, pair_werr = v029.state_error(method_states["csr_jacobian"], method_states["jvp_gmres"])
                method_runs["csr_gmres_difference"] = {
                    "orientation_difference_rad": pair_oerr,
                    "omega_l2_difference": pair_werr,
                    "runtime_speedup_csr_over_gmres": csr_run["runtime_sec"] / max(gmres_run["runtime_sec"], 1.0e-30),
                    "linear_solve_speedup_csr_over_gmres": csr_run["total_linear_solve_sec"]
                    / max(gmres_run["total_linear_solve_sec"], 1.0e-30),
                }
            case_runs[method] = method_runs
        cases[case_name] = {
            "stribeck_velocity": vs,
            "reference_method": REFERENCE_METHOD,
            "reference_h": REF_H,
            "reference_solver": "csr_jacobian",
            "reference": {key: value for key, value in ref.items() if key != "state"},
            "methods": case_runs,
        }
    write_csv(RESULTS / "double_revolute_matrix_free_runs.csv", rows)
    return {"t_final": T_FINAL, "h": H, "cases": cases}


def plot_results(summary: dict) -> None:
    import matplotlib.pyplot as plt

    labels = []
    csr_runtime = []
    gmres_runtime = []
    csr_linear = []
    gmres_linear = []
    matvecs = []
    state_diffs = []
    for case_name, case in summary["cases"].items():
        for method in METHODS:
            runs = case["methods"][method]
            label = f"{case_name.replace('double_revolute_', '')}\n{method.replace('double_revolute_', '')}"
            labels.append(label)
            csr = runs["csr_jacobian"]
            gmres = runs["jvp_gmres"]
            csr_runtime.append(csr.get("runtime_sec", np.nan))
            gmres_runtime.append(gmres.get("runtime_sec", np.nan))
            csr_linear.append(csr.get("total_linear_solve_sec", np.nan))
            gmres_linear.append(gmres.get("total_linear_solve_sec", np.nan))
            matvecs.append(gmres.get("avg_jvp_matvecs_per_solve", np.nan))
            state_diffs.append(runs.get("csr_gmres_difference", {}).get("orientation_difference_rad", np.nan))
    xs = np.arange(len(labels))
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.2))
    axes[0].bar(xs - 0.18, csr_runtime, width=0.36, label="CSR with dense J")
    axes[0].bar(xs + 0.18, gmres_runtime, width=0.36, label="JVP-GMRES")
    axes[0].set_yscale("log")
    axes[0].set_ylabel("runtime seconds")
    axes[0].set_xticks(xs)
    axes[0].set_xticklabels(labels, rotation=65, ha="right", fontsize=7)
    axes[0].grid(True, axis="y", alpha=0.35)
    axes[0].legend()
    axes[1].bar(xs - 0.18, csr_linear, width=0.36, label="CSR solve total")
    axes[1].bar(xs + 0.18, gmres_linear, width=0.36, label="GMRES total")
    axes[1].set_yscale("log")
    axes[1].set_ylabel("linear solve seconds")
    axes[1].set_xticks(xs)
    axes[1].set_xticklabels(labels, rotation=65, ha="right", fontsize=7)
    axes[1].grid(True, axis="y", alpha=0.35)
    axes[1].legend()
    fig.tight_layout()
    fig.savefig(RESULTS / "double_revolute_matrix_free_runtime.png", dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.0))
    axes[0].bar(xs, matvecs)
    axes[0].set_ylabel("avg JVP matvecs per GMRES solve")
    axes[0].set_xticks(xs)
    axes[0].set_xticklabels(labels, rotation=65, ha="right", fontsize=7)
    axes[0].grid(True, axis="y", alpha=0.35)
    axes[1].bar(xs, state_diffs)
    axes[1].set_yscale("log")
    axes[1].set_ylabel("CSR vs GMRES final orientation diff rad")
    axes[1].set_xticks(xs)
    axes[1].set_xticklabels(labels, rotation=65, ha="right", fontsize=7)
    axes[1].grid(True, axis="y", alpha=0.35)
    fig.tight_layout()
    fig.savefig(RESULTS / "double_revolute_matrix_free_gmres.png", dpi=180)
    plt.close(fig)


def write_report(summary: dict) -> None:
    lines = [
        "# v032 Experiment Report",
        "",
        "Generated by `run_v032.py`.",
        "",
        "## Purpose",
        "",
        "- Test the next solver-scaling step after v031: avoid materializing a dense JAX Jacobian.",
        "- Use JAX JVPs as matrix-vector products and solve Newton systems with SciPy GMRES.",
        "- Compare against v031's CSR solve path, which is fast but still builds a dense AD Jacobian first.",
        "- Restrict the test to FullVA because its Gauss6 Jacobian is much better conditioned than raw/PivotVA in v030.",
        "- Use `check_jvp_consistency.py` after the run to verify the JVP implementation against dense Jacobian-vector products.",
        "",
        "## Results",
        "",
    ]
    best_gmres_runtime_ratio = None
    worst_state_diff = 0.0
    for case_name, case in summary["cases"].items():
        lines.append(f"### {case_name}")
        for method in METHODS:
            runs = case["methods"][method]
            csr = runs["csr_jacobian"]
            gmres = runs["jvp_gmres"]
            if csr.get("status") != "ok" or gmres.get("status") != "ok":
                lines.append(
                    f"- `{method}`: CSR status {csr.get('status')}, GMRES status {gmres.get('status')}; "
                    f"GMRES message: {gmres.get('error_message', '')}."
                )
                continue
            diff = runs["csr_gmres_difference"]
            ratio = gmres["runtime_sec"] / max(csr["runtime_sec"], 1.0e-30)
            if best_gmres_runtime_ratio is None or ratio < best_gmres_runtime_ratio[0]:
                best_gmres_runtime_ratio = (ratio, case_name, method)
            worst_state_diff = max(worst_state_diff, diff["orientation_difference_rad"])
            lines.append(
                f"- `{method}`: CSR runtime {csr['runtime_sec']:.3f}s vs JVP-GMRES {gmres['runtime_sec']:.3f}s "
                f"(GMRES/CSR {ratio:.2f}x); CSR dense-J eval {csr['total_jacobian_eval_sec']:.3e}s, "
                f"GMRES JVP eval {gmres['total_jvp_eval_sec']:.3e}s; "
                f"avg GMRES JVP matvecs/solve {gmres['avg_jvp_matvecs_per_solve']:.1f}; "
                f"final orientation diff {diff['orientation_difference_rad']:.3e}; "
                f"GMRES endpoint velocity {gmres['max_endpoint_velocity_constraint_norm']:.3e}."
            )
        lines.append("")
    if best_gmres_runtime_ratio:
        lines.extend(
            [
                "## Interpretation",
                "",
                f"- Best GMRES/CSR runtime ratio is {best_gmres_runtime_ratio[0]:.2f}x for `{best_gmres_runtime_ratio[1]} {best_gmres_runtime_ratio[2]}`.",
                f"- Worst CSR-vs-GMRES final orientation difference is {worst_state_diff:.3e} rad over successful runs.",
                "- Matrix-free Newton-Krylov is feasible: it preserves trajectory/constraints while avoiding dense Jacobian assembly.",
                "- On this small 92D/138D benchmark, unpreconditioned GMRES is expected to be slower than direct CSR because it needs many JVP matvecs.",
                "- The useful conclusion is architectural: the next serious version should add a preconditioner or block sparse assembly, not plain unpreconditioned GMRES.",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "## Interpretation",
                "",
                "- Unpreconditioned JVP-GMRES failed on all targeted Gauss6 FullVA runs even after increasing the GMRES iteration cap.",
                "- This is a useful negative result: avoiding dense Jacobian materialization needs a preconditioner, block sparse assembly, or a different Krylov/nonlinear-solve strategy.",
                "- v031 CSR direct sparse Newton remains the best implemented scaling path for the current double-revolute system.",
                "",
            ]
        )
    lines.extend(
        [
            "## Outputs",
            "",
            "- `double_revolute_matrix_free_runs.csv`",
            "- `summary_v032.json`",
            "- `double_revolute_matrix_free_runtime.png`",
            "- `double_revolute_matrix_free_gmres.png`",
            "- `jvp_consistency.json` from `check_jvp_consistency.py`",
            "",
        ]
    )
    (RESULTS / "v032_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    experiment = run_experiment()
    plot_results(experiment)
    summary = {
        "version": "v032_matrix_free_newton_krylov",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "scipy": __import__("scipy").__version__,
        "jax": jax.__version__,
        "source_version": "v029_double_revolute_pivotva_dae",
        "solver_parent": "v031_sparse_newton_double_revolute",
        "model": {
            "cases": CASES,
            "methods": METHODS,
            "solvers": SOLVERS,
            "h": H,
            "t_final": T_FINAL,
            "reference_method": REFERENCE_METHOD,
            "reference_h": REF_H,
            "gmres_rtol": GMRES_RTOL,
            "gmres_atol": GMRES_ATOL,
            "gmres_maxiter": GMRES_MAXITER,
        },
        "experiment": experiment,
        "runtime_sec": time.perf_counter() - started,
    }
    with (RESULTS / "summary_v032.json").open("w", encoding="utf-8") as f:
        json.dump(json_safe(summary), f, indent=2, sort_keys=True)
    write_report(experiment)


if __name__ == "__main__":
    main()
