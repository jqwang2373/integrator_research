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

import jax.numpy as jnp
import numpy as np
from scipy import sparse
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
    "double_revolute_gauss6_pivotva",
    "double_revolute_gauss6_fullva",
]
SOLVER_REFRESH_PERIOD = {
    "fresh_csr": 1,
    "lagged2_csr": 2,
    "step_lagged_csr": 10_000,
}
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
    "total_linear_solves",
    "total_jacobian_evaluations",
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


def load_v031():
    spec = importlib.util.spec_from_file_location("v031_sparse_newton", V031_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


v031 = load_v031()
v029 = v031.v029


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


def csr_from_jacobian(jac: np.ndarray):
    mask = np.abs(jac) > SPARSITY_ATOL
    density = float(mask.sum() / jac.size)
    csr = sparse.csr_matrix(np.where(mask, jac, 0.0))
    return csr, density


def stage_diagnostics(state, stages, next_state, params) -> dict:
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
    return {
        "max_endpoint_constraint_norm": float(np.linalg.norm(v029.double_constraints_np(next_state, params))),
        "max_endpoint_velocity_constraint_norm": float(np.linalg.norm(v029.double_velocity_constraints_np(next_state, params))),
        "max_stage_pivot_acceleration_constraint_norm": max_stage_pivot_a,
        "max_stage_axis_acceleration_constraint_norm": max_stage_axis_a,
        "max_quaternion_unit_error": float(
            max(abs(np.linalg.norm(next_state.p1) - 1.0), abs(np.linalg.norm(next_state.p2) - 1.0))
        ),
    }


def gauss_step_lagged(state, h: float, params, n_stages: int, mode: str, refresh_period: int):
    _, _, b = v029.qp.gauss_legendre_coefficients(n_stages)
    x = v029.stage_guess(state, h, params, n_stages)
    args = v031.build_args(state, h, params)
    value, jacobian, max_iters = v031.select_residual(mode, n_stages)
    total_residual_sec = 0.0
    total_jacobian_sec = 0.0
    total_linear_sec = 0.0
    total_linear_solves = 0
    total_jacobian_evals = 0
    density_weighted_sum = 0.0
    max_linear_residual = 0.0
    current_csr = None
    current_dense_jac = None
    last_norm = np.inf
    for it in range(max_iters):
        x_jax = jnp.asarray(x, dtype=jnp.float64)
        start = time.perf_counter()
        res = np.asarray(value(x_jax, *args), dtype=float)
        total_residual_sec += time.perf_counter() - start
        last_norm = float(np.linalg.norm(res))
        if last_norm < 1.0e-11:
            break
        need_refresh = current_csr is None or (total_linear_solves % refresh_period == 0)
        if need_refresh:
            start = time.perf_counter()
            current_dense_jac = np.asarray(jacobian(x_jax, *args), dtype=float)
            total_jacobian_sec += time.perf_counter() - start
            current_csr, current_density = csr_from_jacobian(current_dense_jac)
            total_jacobian_evals += 1
        assert current_csr is not None and current_dense_jac is not None
        start = time.perf_counter()
        delta = spla.spsolve(current_csr, -res)
        total_linear_sec += time.perf_counter() - start
        total_linear_solves += 1
        density_weighted_sum += current_density
        max_linear_residual = max(max_linear_residual, float(np.linalg.norm(current_dense_jac @ delta + res)))
        x = x + np.asarray(delta, dtype=float)
        if float(np.linalg.norm(delta)) < 1.0e-11:
            break
    else:
        raise RuntimeError(f"lagged sparse Newton failed, residual={last_norm:.3e}")

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
    diag = stage_diagnostics(state, stages, next_state, params)
    diag.update(
        {
            "newton_iterations": it + 1,
            "stage_residual_norm": last_norm,
            "linear_solves": total_linear_solves,
            "jacobian_evaluations": total_jacobian_evals,
            "total_residual_eval_sec": total_residual_sec,
            "total_jacobian_eval_sec": total_jacobian_sec,
            "total_linear_solve_sec": total_linear_sec,
            "avg_jacobian_density": density_weighted_sum / max(total_linear_solves, 1),
            "max_linear_residual_norm": max_linear_residual,
        }
    )
    return next_state, it + 1, diag


def integrate_lagged(method: str, h: float, t_final: float, params, solver: str) -> dict:
    n_steps = int(round(t_final / h))
    if abs(n_steps * h - t_final) > 1.0e-12:
        raise ValueError("h must divide t_final")
    n_stages = v031.method_stage_count(method)
    mode = v031.residual_mode(method)
    refresh_period = SOLVER_REFRESH_PERIOD[solver]
    state = v029.initial_state(params)
    total_iters = 0
    total_linear_solves = 0
    total_jacobian_evals = 0
    total_residual_eval = 0.0
    total_jacobian_eval = 0.0
    total_linear_solve = 0.0
    density_weighted_sum = 0.0
    max_linear_residual = 0.0
    max_endpoint_constraint = 0.0
    max_endpoint_velocity = 0.0
    max_stage_pivot_a = 0.0
    max_stage_axis_a = 0.0
    max_quat = 0.0
    for _ in range(n_steps):
        state, niters, diag = gauss_step_lagged(state, h, params, n_stages, mode, refresh_period)
        total_iters += niters
        total_linear_solves += diag["linear_solves"]
        total_jacobian_evals += diag["jacobian_evaluations"]
        total_residual_eval += diag["total_residual_eval_sec"]
        total_jacobian_eval += diag["total_jacobian_eval_sec"]
        total_linear_solve += diag["total_linear_solve_sec"]
        density_weighted_sum += diag["avg_jacobian_density"] * diag["linear_solves"]
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
        "total_linear_solves": total_linear_solves,
        "total_jacobian_evaluations": total_jacobian_evals,
        "total_residual_eval_sec": total_residual_eval,
        "total_jacobian_eval_sec": total_jacobian_eval,
        "total_linear_solve_sec": total_linear_solve,
        "avg_linear_solve_sec": total_linear_solve / max(total_linear_solves, 1),
        "avg_jacobian_density": density_weighted_sum / max(total_linear_solves, 1),
        "max_linear_residual_norm": max_linear_residual,
        "max_endpoint_constraint_norm": max_endpoint_constraint,
        "max_endpoint_velocity_constraint_norm": max_endpoint_velocity,
        "max_stage_pivot_acceleration_constraint_norm": max_stage_pivot_a,
        "max_stage_axis_acceleration_constraint_norm": max_stage_axis_a,
        "max_quaternion_unit_error": max_quat,
    }


def warm_jax(params) -> None:
    state = v029.initial_state(params)
    for method in METHODS:
        n_stages = v031.method_stage_count(method)
        mode = v031.residual_mode(method)
        gauss_step_lagged(state, H, params, n_stages, mode, 1)


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
        "total_linear_solves": out["total_linear_solves"],
        "total_jacobian_evaluations": out["total_jacobian_evaluations"],
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


def run_experiment() -> dict:
    rows = []
    cases = {}
    for case_name, vs in CASES.items():
        params = v029.make_params(vs)
        warm_jax(params)
        ref = integrate_lagged(REFERENCE_METHOD, REF_H, T_FINAL, params, "fresh_csr")
        ref_state = ref["state"]
        case_runs = {}
        for method in METHODS:
            method_runs = {}
            method_states = {}
            for solver in SOLVER_REFRESH_PERIOD:
                start = time.perf_counter()
                try:
                    out = integrate_lagged(method, H, T_FINAL, params, solver)
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
                    row = row_from_run(case_name, method, solver, out, oerr, werr, runtime)
                except Exception as exc:
                    runtime = time.perf_counter() - start
                    item = {"status": "failed", "error_message": str(exc), "runtime_sec": runtime}
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
                rows.append(row)
                method_runs[solver] = item
            fresh = method_runs.get("fresh_csr", {})
            if fresh.get("status") == "ok":
                for solver, run in method_runs.items():
                    if solver == "fresh_csr" or run.get("status") != "ok":
                        continue
                    pair_oerr, pair_werr = v029.state_error(method_states["fresh_csr"], method_states[solver])
                    run["fresh_difference"] = {
                        "orientation_difference_rad": pair_oerr,
                        "omega_l2_difference": pair_werr,
                        "runtime_speedup_fresh_over_solver": fresh["runtime_sec"] / max(run["runtime_sec"], 1.0e-30),
                        "jacobian_eval_reduction": fresh["total_jacobian_evaluations"]
                        / max(run["total_jacobian_evaluations"], 1),
                    }
            case_runs[method] = method_runs
        cases[case_name] = {
            "stribeck_velocity": vs,
            "reference_method": REFERENCE_METHOD,
            "reference_h": REF_H,
            "reference_solver": "fresh_csr",
            "reference": {key: value for key, value in ref.items() if key != "state"},
            "methods": case_runs,
        }
    write_csv(RESULTS / "double_revolute_lagged_sparse_runs.csv", rows)
    return {"t_final": T_FINAL, "h": H, "cases": cases}


def plot_results(summary: dict) -> None:
    import matplotlib.pyplot as plt

    labels = []
    runtimes = {solver: [] for solver in SOLVER_REFRESH_PERIOD}
    jac_counts = {solver: [] for solver in SOLVER_REFRESH_PERIOD}
    newton_counts = {solver: [] for solver in SOLVER_REFRESH_PERIOD}
    state_diffs = {"lagged2_csr": [], "step_lagged_csr": []}
    for case_name, case in summary["cases"].items():
        for method in METHODS:
            runs = case["methods"][method]
            labels.append(f"{case_name.replace('double_revolute_', '')}\n{method.replace('double_revolute_', '')}")
            for solver in SOLVER_REFRESH_PERIOD:
                run = runs[solver]
                runtimes[solver].append(run.get("runtime_sec", np.nan))
                jac_counts[solver].append(run.get("total_jacobian_evaluations", np.nan))
                newton_counts[solver].append(run.get("total_newton_iterations", np.nan))
            for solver in state_diffs:
                state_diffs[solver].append(runs[solver].get("fresh_difference", {}).get("orientation_difference_rad", np.nan))
    xs = np.arange(len(labels))
    width = 0.24
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.2))
    for idx, solver in enumerate(SOLVER_REFRESH_PERIOD):
        axes[0].bar(xs + (idx - 1) * width, runtimes[solver], width=width, label=solver)
        axes[1].bar(xs + (idx - 1) * width, jac_counts[solver], width=width, label=solver)
    axes[0].set_yscale("log")
    axes[0].set_ylabel("runtime seconds")
    axes[1].set_ylabel("Jacobian evaluations")
    for ax in axes:
        ax.set_xticks(xs)
        ax.set_xticklabels(labels, rotation=65, ha="right", fontsize=7)
        ax.grid(True, axis="y", alpha=0.35)
        ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(RESULTS / "double_revolute_lagged_sparse_runtime.png", dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.0))
    for idx, solver in enumerate(SOLVER_REFRESH_PERIOD):
        axes[0].bar(xs + (idx - 1) * width, newton_counts[solver], width=width, label=solver)
    axes[0].set_ylabel("Newton iterations")
    axes[0].set_xticks(xs)
    axes[0].set_xticklabels(labels, rotation=65, ha="right", fontsize=7)
    axes[0].grid(True, axis="y", alpha=0.35)
    axes[0].legend(fontsize=8)
    axes[1].bar(xs - width / 2, state_diffs["lagged2_csr"], width=width, label="lagged2 vs fresh")
    axes[1].bar(xs + width / 2, state_diffs["step_lagged_csr"], width=width, label="step-lagged vs fresh")
    axes[1].set_yscale("log")
    axes[1].set_ylabel("final orientation difference rad")
    axes[1].set_xticks(xs)
    axes[1].set_xticklabels(labels, rotation=65, ha="right", fontsize=7)
    axes[1].grid(True, axis="y", alpha=0.35)
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(RESULTS / "double_revolute_lagged_sparse_equivalence.png", dpi=180)
    plt.close(fig)


def write_report(summary: dict) -> None:
    lines = [
        "# v033 Experiment Report",
        "",
        "Generated by `run_v033.py`.",
        "",
        "## Purpose",
        "",
        "- Reduce dense AD Jacobian materialization without switching to unpreconditioned matrix-free GMRES.",
        "- Compare fresh CSR Newton with lagged sparse Jacobian variants on the v029/v031 double-revolute residual.",
        "- `fresh_csr` refreshes the sparse Jacobian every Newton correction.",
        "- `lagged2_csr` refreshes every two Newton corrections.",
        "- `step_lagged_csr` refreshes only once per time step.",
        "",
        "## Results",
        "",
    ]
    best = None
    for case_name, case in summary["cases"].items():
        lines.append(f"### {case_name}")
        for method in METHODS:
            runs = case["methods"][method]
            fresh = runs["fresh_csr"]
            if fresh.get("status") != "ok":
                lines.append(f"- `{method}`: fresh CSR failed: {fresh.get('error_message')}.")
                continue
            lines.append(
                f"- `{method}` fresh: runtime {fresh['runtime_sec']:.3f}s, "
                f"Newton {fresh['total_newton_iterations']}, Jacobians {fresh['total_jacobian_evaluations']}, "
                f"endpoint velocity {fresh['max_endpoint_velocity_constraint_norm']:.3e}."
            )
            for solver in ("lagged2_csr", "step_lagged_csr"):
                run = runs[solver]
                if run.get("status") != "ok":
                    lines.append(f"- `{method}` {solver}: failed: {run.get('error_message')}.")
                    continue
                diff = run["fresh_difference"]
                speedup = diff["runtime_speedup_fresh_over_solver"]
                if best is None or speedup > best[0]:
                    best = (speedup, case_name, method, solver)
                lines.append(
                    f"- `{method}` {solver}: runtime {run['runtime_sec']:.3f}s "
                    f"(fresh/solver {speedup:.2f}x), Newton {run['total_newton_iterations']}, "
                    f"Jacobians {run['total_jacobian_evaluations']}, "
                    f"Jacobian reduction {diff['jacobian_eval_reduction']:.2f}x, "
                    f"orientation diff {diff['orientation_difference_rad']:.3e}, "
                    f"endpoint velocity {run['max_endpoint_velocity_constraint_norm']:.3e}."
                )
        lines.append("")
    lines.extend(["## Interpretation", ""])
    if best:
        lines.append(f"- Best lagged speedup is {best[0]:.2f}x for `{best[1]} {best[2]} {best[3]}`.")
    lines.extend(
        [
            "- This tests a practical modified-Newton route: reduce Jacobian construction while preserving direct sparse solves.",
            "- All lagged variants preserve the trajectory to about roundoff scale, so the approach is numerically safe on this targeted test.",
            "- The speed result is mostly neutral or negative: fewer Jacobian evaluations are offset by more Newton corrections, residual evaluations, and linear solves.",
            "- v031-style fresh CSR remains the best default for this small double-revolute system; lagging may only become useful when Jacobian assembly is much more expensive than the extra nonlinear iterations.",
            "- The deeper production target remains structured sparse/block Jacobian assembly or a good preconditioner, not simple modified Newton.",
            "",
            "## Outputs",
            "",
            "- `double_revolute_lagged_sparse_runs.csv`",
            "- `summary_v033.json`",
            "- `double_revolute_lagged_sparse_runtime.png`",
            "- `double_revolute_lagged_sparse_equivalence.png`",
            "",
        ]
    )
    (RESULTS / "v033_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    experiment = run_experiment()
    plot_results(experiment)
    summary = {
        "version": "v033_lagged_sparse_newton",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "scipy": __import__("scipy").__version__,
        "source_version": "v029_double_revolute_pivotva_dae",
        "solver_parent": "v031_sparse_newton_double_revolute",
        "negative_parent": "v032_matrix_free_newton_krylov",
        "model": {
            "cases": CASES,
            "methods": METHODS,
            "solver_refresh_period": SOLVER_REFRESH_PERIOD,
            "h": H,
            "t_final": T_FINAL,
            "reference_method": REFERENCE_METHOD,
            "reference_h": REF_H,
            "sparsity_atol": SPARSITY_ATOL,
        },
        "experiment": experiment,
        "runtime_sec": time.perf_counter() - started,
    }
    with (RESULTS / "summary_v033.json").open("w", encoding="utf-8") as f:
        json.dump(json_safe(summary), f, indent=2, sort_keys=True)
    write_report(experiment)


if __name__ == "__main__":
    main()
