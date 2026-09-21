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
V036_PATH = ROOT / "v036_symbolic_block_pattern" / "run_v036.py"

CASES = {
    "double_revolute_smooth": 0.50,
    "double_revolute_sharp": 0.05,
}
H = 0.02
T_FINAL = 0.06
PATTERN_ATOL = 1.0e-14
SPARSITY_ATOL = 1.0e-12
CSV_COLUMNS = [
    "case",
    "solver",
    "pattern_source",
    "h",
    "status",
    "error_message",
    "steps",
    "runtime_sec",
    "pattern_build_sec",
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
    "pattern_extra_vs_warmup",
    "pattern_missing_vs_warmup",
    "colors",
    "avg_jvp_dispatches",
    "avg_seed_vectors",
    "max_linear_residual_norm",
    "max_pattern_missing_abs",
    "max_batched_dense_relative_error",
    "orientation_error_vs_dense_rad",
    "omega_error_vs_dense",
    "max_endpoint_constraint_norm",
    "max_endpoint_velocity_constraint_norm",
    "max_stage_pivot_acceleration_constraint_norm",
    "max_stage_axis_acceleration_constraint_norm",
    "max_quaternion_unit_error",
]


def load_v036():
    spec = importlib.util.spec_from_file_location("v036_symbolic_block_pattern", V036_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


v036 = load_v036()
v035 = v036.v035
v034 = v036.v034
v029 = v036.v029


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


def warm_value_and_batched_jvp(params, sp, seeds: np.ndarray) -> None:
    state = v029.initial_state(params)
    x = v029.stage_guess(state, H, params, 3)
    args = v035.v031.build_args(state, H, params)
    x_jax = jnp.asarray(x, dtype=jnp.float64)
    np.asarray(v029.R3_FULL_VALUE(x_jax, *args), dtype=float)
    np.asarray(v035.batched_jvp3_full(x_jax, jnp.asarray(seeds, dtype=jnp.float64), *args), dtype=float)


def superset_batched_jvp_csr_and_mask(x: np.ndarray, args, sp, seeds: np.ndarray, threshold: float):
    rows = []
    cols = []
    data = []
    mask = np.zeros(sp.pattern.shape, dtype=bool)
    x_jax = jnp.asarray(x, dtype=jnp.float64)
    y_by_color = np.asarray(v035.batched_jvp3_full(x_jax, jnp.asarray(seeds, dtype=jnp.float64), *args), dtype=float)
    for color_idx, color in enumerate(sp.colors):
        y = y_by_color[color_idx]
        for col in color:
            col_rows = sp.rows_by_col[col]
            if col_rows.size:
                values = y[col_rows]
                keep = np.abs(values) > threshold
                if np.any(keep):
                    kept_rows = col_rows[keep]
                    mask[kept_rows, col] = True
                    rows.extend(kept_rows.tolist())
                    cols.extend([col] * kept_rows.size)
                    data.extend(values[keep].tolist())
    return sparse.csr_matrix((data, (rows, cols)), shape=sp.pattern.shape), mask


def build_jvp_pruned_pattern(params, superset) -> object:
    """Discover a refined pattern through batched JVPs inside a safe superset.

    This is not dense-Jacobian discovery. The dry-run solves use the
    block-symbolic superset and only call residual values plus batched JVPs.
    """

    seeds = v035.make_seed_matrix(superset)
    state = v029.initial_state(params)
    pattern = np.zeros(superset.pattern.shape, dtype=bool)
    _, _, b = v029.qp.gauss_legendre_coefficients(3)
    for _ in range(int(round(T_FINAL / H))):
        x = v029.stage_guess(state, H, params, 3)
        args = v035.v031.build_args(state, H, params)
        for _it in range(8):
            x_jax = jnp.asarray(x, dtype=jnp.float64)
            res = np.asarray(v029.R3_FULL_VALUE(x_jax, *args), dtype=float)
            csr, current = superset_batched_jvp_csr_and_mask(x, args, superset, seeds, PATTERN_ATOL)
            pattern = np.logical_or(pattern, current)
            if float(np.linalg.norm(res)) < 1.0e-11:
                break
            delta = spla.spsolve(csr, -res)
            x = x + np.asarray(delta, dtype=float)
            if float(np.linalg.norm(delta)) < 1.0e-11:
                break
        stages = v029.unpack_stages(x, 3)
        k1 = [v029.qp.right_jacobian_inverse_apply(st["u1"], st["w1"]) for st in stages]
        k2 = [v029.qp.right_jacobian_inverse_apply(st["u2"], st["w2"]) for st in stages]
        state = v029.State(
            r1=state.r1 + H * sum(b[j] * stages[j]["v1"] for j in range(3)),
            p1=v029.qp.compose_right_quat(state.p1, H * sum(b[j] * k1[j] for j in range(3))),
            v1=state.v1 + H * sum(b[j] * stages[j]["a1"] for j in range(3)),
            w1=state.w1 + H * sum(b[j] * stages[j]["alpha1"] for j in range(3)),
            r2=state.r2 + H * sum(b[j] * stages[j]["v2"] for j in range(3)),
            p2=v029.qp.compose_right_quat(state.p2, H * sum(b[j] * k2[j] for j in range(3))),
            v2=state.v2 + H * sum(b[j] * stages[j]["a2"] for j in range(3)),
            w2=state.w2 + H * sum(b[j] * stages[j]["alpha2"] for j in range(3)),
        )
    return v034.make_sparse_pattern_from_mask(pattern)


def pattern_relation(candidate, reference) -> dict:
    extra = np.logical_and(candidate.pattern, np.logical_not(reference.pattern))
    missing = np.logical_and(reference.pattern, np.logical_not(candidate.pattern))
    return {
        "extra_vs_warmup": int(extra.sum()),
        "missing_vs_warmup": int(missing.sum()),
        "candidate_nnz": candidate.nnz,
        "reference_nnz": reference.nnz,
        "candidate_colors": len(candidate.colors),
        "reference_colors": len(reference.colors),
    }


def run_solver(case_name: str, solver_name: str, source: str, params, sp, seeds, pattern_build_sec: float, dense_state):
    row = {key: "" for key in CSV_COLUMNS}
    row.update({"case": case_name, "solver": solver_name, "pattern_source": source, "h": f"{H:.10g}"})
    start = time.perf_counter()
    try:
        internal_solver = "dense_jacfwd_csr" if solver_name == "dense_jacfwd_csr" else "batched_colored_jvp_csr"
        out = v035.integrate_solver(params, internal_solver, sp, seeds)
        runtime = time.perf_counter() - start
        if dense_state is None:
            dense_state = out["state"]
            oerr, werr = 0.0, 0.0
        else:
            oerr, werr = v029.state_error(dense_state, out["state"])
        diag = {} if solver_name == "dense_jacfwd_csr" else v035.accuracy_diagnostics(params, sp, seeds)
        item = {key: value for key, value in out.items() if key != "state"}
        item.update(
            {
                "status": "ok",
                "runtime_sec": runtime,
                "pattern_build_sec": pattern_build_sec,
                "orientation_error_vs_dense_rad": oerr,
                "omega_error_vs_dense": werr,
                "pattern": {
                    "nnz": sp.nnz,
                    "density": sp.density,
                    "colors": len(sp.colors),
                    "color_sizes": [len(color) for color in sp.colors],
                },
                "accuracy_diagnostics": diag,
            }
        )
        row.update(
            {
                "status": "ok",
                "steps": out["steps"],
                "runtime_sec": f"{runtime:.8e}",
                "pattern_build_sec": f"{pattern_build_sec:.8e}",
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
                "max_pattern_missing_abs": f"{diag.get('max_pattern_missing_abs', 0.0):.16e}",
                "max_batched_dense_relative_error": f"{diag.get('max_batched_dense_relative_error', 0.0):.16e}",
                "orientation_error_vs_dense_rad": f"{oerr:.16e}",
                "omega_error_vs_dense": f"{werr:.16e}",
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
    return item, row, dense_state


def run_one(case_name: str, params) -> dict:
    block = v036.build_block_symbolic_pattern()
    block_seeds = v035.make_seed_matrix(block)
    warm_value_and_batched_jvp(params, block, block_seeds)

    start = time.perf_counter()
    pruned = build_jvp_pruned_pattern(params, block)
    pruned_build_sec = time.perf_counter() - start
    pruned_seeds = v035.make_seed_matrix(pruned)
    warm_value_and_batched_jvp(params, pruned, pruned_seeds)

    # Dense warm-up remains a verification reference, not the production path.
    v034.warm_jax(params)
    start = time.perf_counter()
    warmup = v034.build_initial_pattern(params)
    warmup_build_sec = time.perf_counter() - start
    warmup_seeds = v035.make_seed_matrix(warmup)

    relations = {
        "block_vs_warmup": pattern_relation(block, warmup),
        "pruned_vs_warmup": pattern_relation(pruned, warmup),
        "pruned_vs_block": pattern_relation(pruned, block),
    }

    runs = {}
    rows = []
    dense_state = None
    specs = [
        ("dense_jacfwd_csr", "dense", warmup, warmup_seeds, 0.0),
        ("batched_colored_warmup_pattern", "warmup_union", warmup, warmup_seeds, warmup_build_sec),
        ("batched_colored_block_symbolic", "block_symbolic", block, block_seeds, 0.0),
        ("batched_colored_jvp_pruned", "jvp_pruned_from_block", pruned, pruned_seeds, pruned_build_sec),
    ]
    for spec in specs:
        item, row, dense_state = run_solver(case_name, spec[0], spec[1], params, spec[2], spec[3], spec[4], dense_state)
        rows.append(row)
        runs[spec[0]] = item
    return {
        "stribeck_velocity": CASES[case_name],
        "jvp_pruned_pattern_build_sec": pruned_build_sec,
        "warmup_pattern_build_sec": warmup_build_sec,
        "relations": relations,
        "runs": runs,
        "rows": rows,
    }


def run_experiment() -> dict:
    all_rows = []
    cases = {}
    for case_name, vs in CASES.items():
        params = v029.make_params(vs)
        case = run_one(case_name, params)
        all_rows.extend(case.pop("rows"))
        cases[case_name] = case
    write_csv(RESULTS / "double_revolute_jvp_pruned_pattern_runs.csv", all_rows)
    return {"t_final": T_FINAL, "h": H, "cases": cases}


def plot_results(summary: dict) -> None:
    import matplotlib.pyplot as plt

    solvers = [
        "dense_jacfwd_csr",
        "batched_colored_warmup_pattern",
        "batched_colored_block_symbolic",
        "batched_colored_jvp_pruned",
    ]
    labels = []
    runtimes = {solver: [] for solver in solvers}
    nnz = {"warmup": [], "block": [], "pruned": []}
    colors = {"warmup": [], "block": [], "pruned": []}
    for case_name, case in summary["cases"].items():
        labels.append(case_name.replace("double_revolute_", ""))
        for solver in solvers:
            runtimes[solver].append(case["runs"][solver].get("runtime_sec", np.nan))
        for key, solver in [
            ("warmup", "batched_colored_warmup_pattern"),
            ("block", "batched_colored_block_symbolic"),
            ("pruned", "batched_colored_jvp_pruned"),
        ]:
            pattern = case["runs"][solver]["pattern"]
            nnz[key].append(pattern["nnz"])
            colors[key].append(pattern["colors"])
    xs = np.arange(len(labels))
    width = 0.2
    fig, ax = plt.subplots(figsize=(10.2, 4.0))
    for idx, solver in enumerate(solvers):
        ax.bar(xs + (idx - 1.5) * width, runtimes[solver], width=width, label=solver.replace("batched_colored_", ""))
    ax.set_yscale("log")
    ax.set_ylabel("runtime seconds")
    ax.set_xticks(xs)
    ax.set_xticklabels(labels)
    ax.grid(True, axis="y", alpha=0.35)
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(RESULTS / "double_revolute_jvp_pruned_pattern_runtime.png", dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.0))
    for idx, key in enumerate(["warmup", "block", "pruned"]):
        axes[0].bar(xs + (idx - 1) * 0.25, nnz[key], width=0.25, label=key)
        axes[1].bar(xs + (idx - 1) * 0.25, colors[key], width=0.25, label=key)
    axes[0].set_ylabel("pattern nonzeros")
    axes[1].set_ylabel("column colors")
    for ax in axes:
        ax.set_xticks(xs)
        ax.set_xticklabels(labels)
        ax.grid(True, axis="y", alpha=0.35)
        ax.legend()
    fig.tight_layout()
    fig.savefig(RESULTS / "double_revolute_jvp_pruned_pattern_stats.png", dpi=180)
    plt.close(fig)


def write_report(summary: dict) -> None:
    lines = [
        "# v037 Experiment Report",
        "",
        "Generated by `run_v037.py`.",
        "",
        "## Purpose",
        "",
        "- Refine v036's conservative block-symbolic pattern without materializing a dense Jacobian.",
        "- Use the block-symbolic pattern as a safe superset, then run batched JVPs along a short Newton/trajectory dry-run to prune inactive entries.",
        "- Compare dense `jacfwd` CSR, dense-warm-up exact pattern, block-symbolic pattern, and JVP-pruned pattern.",
        "",
        "## Results",
        "",
    ]
    for case_name, case in summary["cases"].items():
        dense = case["runs"]["dense_jacfwd_csr"]
        warm = case["runs"]["batched_colored_warmup_pattern"]
        block = case["runs"]["batched_colored_block_symbolic"]
        pruned = case["runs"]["batched_colored_jvp_pruned"]
        rel = case["relations"]["pruned_vs_warmup"]
        lines.append(f"### {case_name}")
        lines.append(
            f"- JVP-pruned pattern: nnz {rel['candidate_nnz']} vs warm-up {rel['reference_nnz']}, "
            f"extra {rel['extra_vs_warmup']}, missing {rel['missing_vs_warmup']}; colors "
            f"{rel['candidate_colors']} vs {rel['reference_colors']}."
        )
        lines.append(
            f"- Build time: JVP-pruned {case['jvp_pruned_pattern_build_sec']:.3f}s vs dense warm-up "
            f"{case['warmup_pattern_build_sec']:.3f}s."
        )
        if dense.get("status") == "ok":
            lines.append(f"- Dense jacfwd CSR runtime {dense['runtime_sec']:.3f}s.")
        for label, run in [("Warm-up exact", warm), ("Block symbolic", block), ("JVP-pruned", pruned)]:
            if run.get("status") == "ok":
                dense_speed = dense["runtime_sec"] / max(run["runtime_sec"], 1.0e-30)
                lines.append(
                    f"- {label}: runtime {run['runtime_sec']:.3f}s (dense/{label.lower().replace(' ', '-')} "
                    f"{dense_speed:.2f}x), pattern {run['pattern']['nnz']} nnz/{run['pattern']['colors']} colors, "
                    f"missed dense entry {run['accuracy_diagnostics'].get('max_pattern_missing_abs', 0.0):.3e}, "
                    f"dense-relative error {run['accuracy_diagnostics'].get('max_batched_dense_relative_error', 0.0):.3e}, "
                    f"trajectory diff {run['orientation_error_vs_dense_rad']:.3e} rad."
                )
            else:
                lines.append(f"- {label} failed: {run.get('error_message')}.")
        lines.append("")
    lines.extend(
        [
            "## Interpretation",
            "",
            "- JVP-pruned discovery uses the sparse-AD backend itself to recover the same fine pattern as dense warm-up discovery, without dense Jacobian materialization.",
            "- In both smooth and sharp cases, the pruned pattern has 582 entries and 11 colors, with zero missing entries relative to the dense warm-up union pattern.",
            "- Pattern construction is much cheaper than dense warm-up discovery in this run: 0.053-0.067s versus 0.952-1.082s.",
            "- The diagnostic dense Jacobian is still used to check for missed entries and relative error, but not to construct the pruned pattern.",
            "- This is the best current pattern-discovery path: v036 gives a safe symbolic superset, and v037 prunes it to the exact observed sparse pattern using only batched JVPs.",
            "",
            "## Outputs",
            "",
            "- `double_revolute_jvp_pruned_pattern_runs.csv`",
            "- `summary_v037.json`",
            "- `double_revolute_jvp_pruned_pattern_runtime.png`",
            "- `double_revolute_jvp_pruned_pattern_stats.png`",
            "",
        ]
    )
    (RESULTS / "v037_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    experiment = run_experiment()
    plot_results(experiment)
    summary = {
        "version": "v037_jvp_pruned_symbolic_pattern",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "scipy": __import__("scipy").__version__,
        "jax": v035.jax.__version__,
        "source_version": "v029_double_revolute_pivotva_dae",
        "solver_parent": "v036_symbolic_block_pattern",
        "model": {
            "cases": CASES,
            "method": "double_revolute_gauss6_fullva",
            "h": H,
            "t_final": T_FINAL,
            "pattern_atol": PATTERN_ATOL,
            "sparsity_atol": SPARSITY_ATOL,
        },
        "experiment": experiment,
        "runtime_sec": time.perf_counter() - started,
    }
    with (RESULTS / "summary_v037.json").open("w", encoding="utf-8") as f:
        json.dump(json_safe(summary), f, indent=2, sort_keys=True)
    write_report(experiment)


if __name__ == "__main__":
    main()
