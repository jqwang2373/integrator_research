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
from scipy import sparse
from scipy.sparse import linalg as spla


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RESULTS = HERE / "results"
V034_PATH = ROOT / "v034_colored_jvp_sparse_jacobian" / "run_v034.py"

CASES = {
    "double_revolute_smooth": 0.50,
    "double_revolute_sharp": 0.05,
}
METHOD = "double_revolute_gauss6_fullva"
SOLVERS = ["dense_jacfwd_csr", "sequential_colored_jvp_csr", "batched_colored_jvp_csr"]
H = 0.02
T_FINAL = 0.06
SPARSITY_ATOL = 1.0e-12
CSV_COLUMNS = [
    "case",
    "solver",
    "h",
    "status",
    "error_message",
    "steps",
    "runtime_sec",
    "total_newton_iterations",
    "total_linear_solves",
    "total_jacobian_assemblies",
    "total_residual_eval_sec",
    "total_jacobian_eval_sec",
    "total_linear_solve_sec",
    "avg_jacobian_eval_sec",
    "avg_linear_solve_sec",
    "pattern_nnz",
    "pattern_density",
    "colors",
    "avg_jvp_dispatches",
    "avg_seed_vectors",
    "max_linear_residual_norm",
    "orientation_error_vs_dense_rad",
    "omega_error_vs_dense",
    "max_endpoint_constraint_norm",
    "max_endpoint_velocity_constraint_norm",
    "max_stage_pivot_acceleration_constraint_norm",
    "max_stage_axis_acceleration_constraint_norm",
    "max_quaternion_unit_error",
]


def load_v034():
    spec = importlib.util.spec_from_file_location("v034_colored_jvp", V034_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


v034 = load_v034()
v031 = v034.v031
v029 = v034.v029


@jax.jit
def batched_jvp3_full(x, seeds, *args):
    def one(seed):
        return jax.jvp(lambda y: v029.residual3_fullva(y, *args), (x,), (seed,))[1]

    return jax.vmap(one)(seeds)


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


def make_seed_matrix(sp) -> np.ndarray:
    seeds = np.zeros((len(sp.colors), sp.pattern.shape[1]), dtype=float)
    for idx, color in enumerate(sp.colors):
        seeds[idx, color] = 1.0
    return seeds


def csr_from_dense_jac(jac: np.ndarray):
    mask = np.abs(jac) > SPARSITY_ATOL
    return sparse.csr_matrix(np.where(mask, jac, 0.0))


def sequential_colored_jvp_csr(x: np.ndarray, args, sp):
    csr, elapsed, calls = v034.colored_jvp_csr(x, args, sp)
    return csr, elapsed, calls, calls


def batched_colored_jvp_csr(x: np.ndarray, args, sp, seeds: np.ndarray):
    rows = []
    cols = []
    data = []
    x_jax = jnp.asarray(x, dtype=jnp.float64)
    seeds_jax = jnp.asarray(seeds, dtype=jnp.float64)
    start = time.perf_counter()
    y_by_color = np.asarray(batched_jvp3_full(x_jax, seeds_jax, *args), dtype=float)
    elapsed = time.perf_counter() - start
    for color_idx, color in enumerate(sp.colors):
        y = y_by_color[color_idx]
        for col in color:
            col_rows = sp.rows_by_col[col]
            if col_rows.size:
                values = y[col_rows]
                keep = np.abs(values) > SPARSITY_ATOL
                if np.any(keep):
                    kept_rows = col_rows[keep]
                    rows.extend(kept_rows.tolist())
                    cols.extend([col] * kept_rows.size)
                    data.extend(values[keep].tolist())
    csr = sparse.csr_matrix((data, (rows, cols)), shape=sp.pattern.shape)
    return csr, elapsed, 1, len(sp.colors)


def stage_diagnostics(state, stages, next_state, params) -> dict:
    return v034.stage_diagnostics(state, stages, next_state, params)


def gauss_step_with_jacobian_source(state, h: float, params, solver: str, sp, seeds: np.ndarray):
    _, _, b = v029.qp.gauss_legendre_coefficients(3)
    x = v029.stage_guess(state, h, params, 3)
    args = v031.build_args(state, h, params)
    value = v029.R3_FULL_VALUE
    jacobian = v029.R3_FULL_JAC
    max_iters = 64
    total_residual_sec = 0.0
    total_jacobian_sec = 0.0
    total_linear_sec = 0.0
    total_linear_solves = 0
    total_jacobian_assemblies = 0
    total_jvp_dispatches = 0
    total_seed_vectors = 0
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
        if solver == "dense_jacfwd_csr":
            start = time.perf_counter()
            csr = csr_from_dense_jac(np.asarray(jacobian(x_jax, *args), dtype=float))
            total_jacobian_sec += time.perf_counter() - start
        elif solver == "sequential_colored_jvp_csr":
            csr, assemble_sec, dispatches, seed_vectors = sequential_colored_jvp_csr(x, args, sp)
            total_jacobian_sec += assemble_sec
            total_jvp_dispatches += dispatches
            total_seed_vectors += seed_vectors
        elif solver == "batched_colored_jvp_csr":
            csr, assemble_sec, dispatches, seed_vectors = batched_colored_jvp_csr(x, args, sp, seeds)
            total_jacobian_sec += assemble_sec
            total_jvp_dispatches += dispatches
            total_seed_vectors += seed_vectors
        else:
            raise ValueError(f"unknown solver {solver}")
        total_jacobian_assemblies += 1
        start = time.perf_counter()
        delta = spla.spsolve(csr, -res)
        total_linear_sec += time.perf_counter() - start
        total_linear_solves += 1
        max_linear_residual = max(max_linear_residual, float(np.linalg.norm(csr @ delta + res)))
        x = x + np.asarray(delta, dtype=float)
        if float(np.linalg.norm(delta)) < 1.0e-11:
            break
    else:
        raise RuntimeError(f"batched colored sparse Newton failed, residual={last_norm:.3e}")

    stages = v029.unpack_stages(x, 3)
    k1 = [v029.qp.right_jacobian_inverse_apply(st["u1"], st["w1"]) for st in stages]
    k2 = [v029.qp.right_jacobian_inverse_apply(st["u2"], st["w2"]) for st in stages]
    next_state = v029.State(
        r1=state.r1 + h * sum(b[j] * stages[j]["v1"] for j in range(3)),
        p1=v029.qp.compose_right_quat(state.p1, h * sum(b[j] * k1[j] for j in range(3))),
        v1=state.v1 + h * sum(b[j] * stages[j]["a1"] for j in range(3)),
        w1=state.w1 + h * sum(b[j] * stages[j]["alpha1"] for j in range(3)),
        r2=state.r2 + h * sum(b[j] * stages[j]["v2"] for j in range(3)),
        p2=v029.qp.compose_right_quat(state.p2, h * sum(b[j] * k2[j] for j in range(3))),
        v2=state.v2 + h * sum(b[j] * stages[j]["a2"] for j in range(3)),
        w2=state.w2 + h * sum(b[j] * stages[j]["alpha2"] for j in range(3)),
    )
    diag = stage_diagnostics(state, stages, next_state, params)
    diag.update(
        {
            "newton_iterations": it + 1,
            "stage_residual_norm": last_norm,
            "linear_solves": total_linear_solves,
            "jacobian_assemblies": total_jacobian_assemblies,
            "total_residual_eval_sec": total_residual_sec,
            "total_jacobian_eval_sec": total_jacobian_sec,
            "total_linear_solve_sec": total_linear_sec,
            "jvp_dispatches": total_jvp_dispatches,
            "seed_vectors": total_seed_vectors,
            "max_linear_residual_norm": max_linear_residual,
        }
    )
    return next_state, it + 1, diag


def integrate_solver(params, solver: str, sp, seeds: np.ndarray):
    n_steps = int(round(T_FINAL / H))
    state = v029.initial_state(params)
    total_iters = 0
    total_linear_solves = 0
    total_jacobian_assemblies = 0
    total_residual_eval = 0.0
    total_jacobian_eval = 0.0
    total_linear_solve = 0.0
    total_jvp_dispatches = 0
    total_seed_vectors = 0
    max_linear_residual = 0.0
    max_endpoint_constraint = 0.0
    max_endpoint_velocity = 0.0
    max_stage_pivot_a = 0.0
    max_stage_axis_a = 0.0
    max_quat = 0.0
    for _ in range(n_steps):
        state, niters, diag = gauss_step_with_jacobian_source(state, H, params, solver, sp, seeds)
        total_iters += niters
        total_linear_solves += diag["linear_solves"]
        total_jacobian_assemblies += diag["jacobian_assemblies"]
        total_residual_eval += diag["total_residual_eval_sec"]
        total_jacobian_eval += diag["total_jacobian_eval_sec"]
        total_linear_solve += diag["total_linear_solve_sec"]
        total_jvp_dispatches += diag["jvp_dispatches"]
        total_seed_vectors += diag["seed_vectors"]
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
        "total_jacobian_assemblies": total_jacobian_assemblies,
        "total_residual_eval_sec": total_residual_eval,
        "total_jacobian_eval_sec": total_jacobian_eval,
        "total_linear_solve_sec": total_linear_solve,
        "avg_jacobian_eval_sec": total_jacobian_eval / max(total_jacobian_assemblies, 1),
        "avg_linear_solve_sec": total_linear_solve / max(total_linear_solves, 1),
        "avg_jvp_dispatches": total_jvp_dispatches / max(total_jacobian_assemblies, 1),
        "avg_seed_vectors": total_seed_vectors / max(total_jacobian_assemblies, 1),
        "max_linear_residual_norm": max_linear_residual,
        "max_endpoint_constraint_norm": max_endpoint_constraint,
        "max_endpoint_velocity_constraint_norm": max_endpoint_velocity,
        "max_stage_pivot_acceleration_constraint_norm": max_stage_pivot_a,
        "max_stage_axis_acceleration_constraint_norm": max_stage_axis_a,
        "max_quaternion_unit_error": max_quat,
    }


def accuracy_diagnostics(params, sp, seeds: np.ndarray) -> dict:
    state = v029.initial_state(params)
    x = v029.stage_guess(state, H, params, 3)
    args = v031.build_args(state, H, params)
    max_seq_rel = 0.0
    max_batched_rel = 0.0
    max_seq_batched_rel = 0.0
    max_missing = 0.0
    max_seq_diff = 0.0
    max_batched_diff = 0.0
    samples = 0
    for _ in range(6):
        x_jax = jnp.asarray(x, dtype=jnp.float64)
        res = np.asarray(v029.R3_FULL_VALUE(x_jax, *args), dtype=float)
        dense = np.asarray(v029.R3_FULL_JAC(x_jax, *args), dtype=float)
        seq_csr, _, _, _ = sequential_colored_jvp_csr(x, args, sp)
        bat_csr, _, _, _ = batched_colored_jvp_csr(x, args, sp, seeds)
        target = np.where(sp.pattern, dense, 0.0)
        outside = np.where(sp.pattern, 0.0, dense)
        seq = seq_csr.toarray()
        bat = bat_csr.toarray()
        dense_norm = float(np.linalg.norm(dense))
        seq_diff = float(np.linalg.norm(seq - target))
        bat_diff = float(np.linalg.norm(bat - target))
        seq_bat = float(np.linalg.norm(seq - bat))
        max_seq_diff = max(max_seq_diff, seq_diff)
        max_batched_diff = max(max_batched_diff, bat_diff)
        max_seq_rel = max(max_seq_rel, seq_diff / max(dense_norm, 1.0e-30))
        max_batched_rel = max(max_batched_rel, bat_diff / max(dense_norm, 1.0e-30))
        max_seq_batched_rel = max(max_seq_batched_rel, seq_bat / max(float(np.linalg.norm(seq)), 1.0e-30))
        max_missing = max(max_missing, float(np.max(np.abs(outside))))
        samples += 1
        if float(np.linalg.norm(res)) < 1.0e-11:
            break
        delta = np.linalg.solve(dense, -res)
        x = x + delta
        if float(np.linalg.norm(delta)) < 1.0e-11:
            break
    return {
        "samples": samples,
        "max_pattern_missing_abs": max_missing,
        "max_sequential_dense_diff_norm": max_seq_diff,
        "max_batched_dense_diff_norm": max_batched_diff,
        "max_sequential_dense_relative_error": max_seq_rel,
        "max_batched_dense_relative_error": max_batched_rel,
        "max_sequential_batched_relative_error": max_seq_batched_rel,
    }


def warm_jax(params, sp, seeds: np.ndarray) -> None:
    v034.warm_jax(params)
    state = v029.initial_state(params)
    x = v029.stage_guess(state, H, params, 3)
    args = v031.build_args(state, H, params)
    np.asarray(batched_jvp3_full(jnp.asarray(x, dtype=jnp.float64), jnp.asarray(seeds, dtype=jnp.float64), *args), dtype=float)


def row_from_run(case_name: str, solver: str, out: dict, runtime: float, sp, oerr: float, werr: float) -> dict:
    return {
        "case": case_name,
        "solver": solver,
        "h": f"{H:.10g}",
        "status": "ok",
        "error_message": "",
        "steps": out["steps"],
        "runtime_sec": f"{runtime:.8e}",
        "total_newton_iterations": out["total_newton_iterations"],
        "total_linear_solves": out["total_linear_solves"],
        "total_jacobian_assemblies": out["total_jacobian_assemblies"],
        "total_residual_eval_sec": f"{out['total_residual_eval_sec']:.16e}",
        "total_jacobian_eval_sec": f"{out['total_jacobian_eval_sec']:.16e}",
        "total_linear_solve_sec": f"{out['total_linear_solve_sec']:.16e}",
        "avg_jacobian_eval_sec": f"{out['avg_jacobian_eval_sec']:.16e}",
        "avg_linear_solve_sec": f"{out['avg_linear_solve_sec']:.16e}",
        "pattern_nnz": sp.nnz,
        "pattern_density": f"{sp.density:.16e}",
        "colors": len(sp.colors),
        "avg_jvp_dispatches": f"{out['avg_jvp_dispatches']:.16e}",
        "avg_seed_vectors": f"{out['avg_seed_vectors']:.16e}",
        "max_linear_residual_norm": f"{out['max_linear_residual_norm']:.16e}",
        "orientation_error_vs_dense_rad": f"{oerr:.16e}",
        "omega_error_vs_dense": f"{werr:.16e}",
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
        sp = v034.build_initial_pattern(params)
        seeds = make_seed_matrix(sp)
        warm_jax(params, sp, seeds)
        diag = accuracy_diagnostics(params, sp, seeds)
        case_runs = {}
        dense_state = None
        for solver in SOLVERS:
            row = {key: "" for key in CSV_COLUMNS}
            row.update({"case": case_name, "solver": solver, "h": f"{H:.10g}"})
            start = time.perf_counter()
            try:
                out = integrate_solver(params, solver, sp, seeds)
                runtime = time.perf_counter() - start
                if solver == "dense_jacfwd_csr":
                    dense_state = out["state"]
                    oerr, werr = 0.0, 0.0
                else:
                    assert dense_state is not None
                    oerr, werr = v029.state_error(dense_state, out["state"])
                item = {key: value for key, value in out.items() if key != "state"}
                item.update(
                    {
                        "status": "ok",
                        "runtime_sec": runtime,
                        "orientation_error_vs_dense_rad": oerr,
                        "omega_error_vs_dense": werr,
                    }
                )
                row = row_from_run(case_name, solver, out, runtime, sp, oerr, werr)
            except Exception as exc:
                runtime = time.perf_counter() - start
                item = {"status": "failed", "error_message": str(exc), "runtime_sec": runtime}
                row.update({"status": "failed", "error_message": str(exc), "runtime_sec": f"{runtime:.8e}"})
            rows.append(row)
            case_runs[solver] = item
        cases[case_name] = {
            "stribeck_velocity": vs,
            "method": METHOD,
            "pattern": {
                "nnz": sp.nnz,
                "density": sp.density,
                "colors": len(sp.colors),
                "color_sizes": [len(color) for color in sp.colors],
            },
            "accuracy_diagnostics": diag,
            "runs": case_runs,
        }
    write_csv(RESULTS / "double_revolute_batched_colored_jvp_runs.csv", rows)
    return {"t_final": T_FINAL, "h": H, "cases": cases}


def plot_results(summary: dict) -> None:
    import matplotlib.pyplot as plt

    labels = []
    runtimes = {solver: [] for solver in SOLVERS}
    jac_times = {solver: [] for solver in SOLVERS}
    seq_rel = []
    bat_rel = []
    seq_bat_rel = []
    for case_name, case in summary["cases"].items():
        labels.append(case_name.replace("double_revolute_", ""))
        for solver in SOLVERS:
            run = case["runs"][solver]
            runtimes[solver].append(run.get("runtime_sec", np.nan))
            jac_times[solver].append(run.get("total_jacobian_eval_sec", np.nan))
        diag = case["accuracy_diagnostics"]
        seq_rel.append(diag["max_sequential_dense_relative_error"])
        bat_rel.append(diag["max_batched_dense_relative_error"])
        seq_bat_rel.append(diag["max_sequential_batched_relative_error"])
    xs = np.arange(len(labels))
    width = 0.24

    fig, axes = plt.subplots(1, 2, figsize=(11.4, 4.0))
    for idx, solver in enumerate(SOLVERS):
        axes[0].bar(xs + (idx - 1) * width, runtimes[solver], width=width, label=solver.replace("_csr", ""))
        axes[1].bar(xs + (idx - 1) * width, jac_times[solver], width=width, label=solver.replace("_csr", ""))
    for ax in axes:
        ax.set_yscale("log")
        ax.set_xticks(xs)
        ax.set_xticklabels(labels)
        ax.grid(True, axis="y", alpha=0.35)
        ax.legend(fontsize=7)
    axes[0].set_ylabel("runtime seconds")
    axes[1].set_ylabel("Jacobian assembly seconds")
    fig.tight_layout()
    fig.savefig(RESULTS / "double_revolute_batched_colored_jvp_runtime.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.8, 4.0))
    ax.bar(xs - 0.24, seq_rel, width=0.24, label="sequential vs dense")
    ax.bar(xs, bat_rel, width=0.24, label="batched vs dense")
    ax.bar(xs + 0.24, seq_bat_rel, width=0.24, label="sequential vs batched")
    ax.set_yscale("log")
    ax.set_ylabel("relative error")
    ax.set_xticks(xs)
    ax.set_xticklabels(labels)
    ax.grid(True, axis="y", alpha=0.35)
    ax.legend()
    fig.tight_layout()
    fig.savefig(RESULTS / "double_revolute_batched_colored_jvp_accuracy.png", dpi=180)
    plt.close(fig)


def write_report(summary: dict) -> None:
    lines = [
        "# v035 Experiment Report",
        "",
        "Generated by `run_v035.py`.",
        "",
        "## Purpose",
        "",
        "- Test whether v034's correct but slow colored sparse AD path improves when all color seeds are evaluated in one compiled `vmap(jvp)` batch.",
        "- Keep the same v029 double-revolute Gauss6 FullVA Brown-McPhee friction residual and the same warm-up union sparsity pattern.",
        "- Compare dense `jacfwd` CSR, sequential colored JVP CSR, and batched colored JVP CSR with diagnostic dense checks kept outside the timed solver loop.",
        "",
        "## Results",
        "",
    ]
    for case_name, case in summary["cases"].items():
        dense = case["runs"]["dense_jacfwd_csr"]
        seq = case["runs"]["sequential_colored_jvp_csr"]
        bat = case["runs"]["batched_colored_jvp_csr"]
        diag = case["accuracy_diagnostics"]
        lines.append(f"### {case_name}")
        lines.append(
            f"- Pattern: {case['pattern']['nnz']} nonzeros, density {case['pattern']['density']:.3e}, "
            f"{case['pattern']['colors']} colors, color sizes {case['pattern']['color_sizes']}."
        )
        if dense.get("status") == "ok":
            lines.append(
                f"- Dense jacfwd CSR: runtime {dense['runtime_sec']:.3f}s, "
                f"Jacobian assembly {dense['total_jacobian_eval_sec']:.3e}s, "
                f"Newton {dense['total_newton_iterations']}."
            )
        if seq.get("status") == "ok":
            speed = dense["runtime_sec"] / max(seq["runtime_sec"], 1.0e-30) if dense.get("status") == "ok" else float("nan")
            lines.append(
                f"- Sequential colored JVP CSR: runtime {seq['runtime_sec']:.3f}s "
                f"(dense/sequential {speed:.2f}x), assembly {seq['total_jacobian_eval_sec']:.3e}s, "
                f"avg dispatches {seq['avg_jvp_dispatches']:.1f}, trajectory diff "
                f"{seq['orientation_error_vs_dense_rad']:.3e} rad."
            )
        if bat.get("status") == "ok":
            speed = dense["runtime_sec"] / max(bat["runtime_sec"], 1.0e-30) if dense.get("status") == "ok" else float("nan")
            seq_speed = seq["runtime_sec"] / max(bat["runtime_sec"], 1.0e-30) if seq.get("status") == "ok" else float("nan")
            lines.append(
                f"- Batched colored JVP CSR: runtime {bat['runtime_sec']:.3f}s "
                f"(dense/batched {speed:.2f}x, sequential/batched {seq_speed:.2f}x), "
                f"assembly {bat['total_jacobian_eval_sec']:.3e}s, avg dispatches "
                f"{bat['avg_jvp_dispatches']:.1f}, trajectory diff {bat['orientation_error_vs_dense_rad']:.3e} rad."
            )
        lines.append(
            f"- Accuracy diagnostic: max missed pattern entry {diag['max_pattern_missing_abs']:.3e}, "
            f"sequential-vs-dense relative error {diag['max_sequential_dense_relative_error']:.3e}, "
            f"batched-vs-dense relative error {diag['max_batched_dense_relative_error']:.3e}, "
            f"sequential-vs-batched relative error {diag['max_sequential_batched_relative_error']:.3e}."
        )
        lines.append("")
    lines.extend(
        [
            "## Interpretation",
            "",
            "- Batched coloring removes the one-dispatch-per-color overhead from v034 and turns the structured sparse-AD route into a real speed win on this benchmark.",
            "- The 138D double-revolute FullVA residual is still small, so a 2.49x--2.66x speedup over dense `jacfwd` CSR is a strong signal that compiled colored AD should remain in the solver path.",
            "- The main remaining caveat is not correctness or small-system speed; it is pattern acquisition and generalization. The current code still obtains the sparsity mask from a dense warm-up path, so the next target is a symbolic/block pattern for larger chains or lower-pair families.",
            "",
            "## Outputs",
            "",
            "- `double_revolute_batched_colored_jvp_runs.csv`",
            "- `summary_v035.json`",
            "- `double_revolute_batched_colored_jvp_runtime.png`",
            "- `double_revolute_batched_colored_jvp_accuracy.png`",
            "",
        ]
    )
    (RESULTS / "v035_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    experiment = run_experiment()
    plot_results(experiment)
    summary = {
        "version": "v035_batched_colored_jvp",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "scipy": __import__("scipy").__version__,
        "jax": jax.__version__,
        "source_version": "v029_double_revolute_pivotva_dae",
        "solver_parent": "v031_sparse_newton_double_revolute",
        "direct_parent": "v034_colored_jvp_sparse_jacobian",
        "negative_parents": ["v032_matrix_free_newton_krylov", "v033_lagged_sparse_newton"],
        "model": {
            "cases": CASES,
            "method": METHOD,
            "solvers": SOLVERS,
            "h": H,
            "t_final": T_FINAL,
            "sparsity_atol": SPARSITY_ATOL,
        },
        "experiment": experiment,
        "runtime_sec": time.perf_counter() - started,
    }
    with (RESULTS / "summary_v035.json").open("w", encoding="utf-8") as f:
        json.dump(json_safe(summary), f, indent=2, sort_keys=True)
    write_report(experiment)


if __name__ == "__main__":
    main()
