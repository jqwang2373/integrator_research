from __future__ import annotations

import csv
import importlib.util
import json
import os
import platform
import sys
import time
from dataclasses import dataclass
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
V044_PATH = ROOT / "v044_double_prismatic_chain" / "run_v044.py"


def load_v044():
    spec = importlib.util.spec_from_file_location("v044_double_prismatic_chain", V044_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


v044 = load_v044()
jax = v044.jax

H = v044.H
T_FINAL = v044.T_FINAL
DIM = v044.DIM
CASES = v044.CASES
SPARSITY_ATOL = v044.SPARSITY_ATOL

CSV_COLUMNS = [
    "case",
    "solver",
    "h",
    "status",
    "error_message",
    "steps",
    "runtime_sec",
    "pattern_build_sec",
    "dense_validation_pattern_sec",
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
    "column_colors",
    "row_colors",
    "pattern_missing_vs_dense",
    "pattern_extra_vs_dense",
    "position_error_vs_dense",
    "velocity_error_vs_dense",
    "max_linear_residual_norm",
    "max_endpoint_constraint_norm",
    "max_endpoint_velocity_constraint_norm",
    "max_stage_position_acceleration_constraint_norm",
    "max_stage_orientation_acceleration_constraint_norm",
    "max_quaternion_unit_error",
]


@dataclass(frozen=True)
class RowSparsePattern:
    pattern: np.ndarray
    row_colors: list[list[int]]
    cols_by_row: list[np.ndarray]
    nnz: int
    density: float


def greedy_row_coloring(mask: np.ndarray) -> list[list[int]]:
    cols_by_row = [set(np.nonzero(mask[row])[0].tolist()) for row in range(mask.shape[0])]
    order = sorted(range(mask.shape[0]), key=lambda row: len(cols_by_row[row]), reverse=True)
    colors: list[list[int]] = []
    for row in order:
        support = cols_by_row[row]
        for idx, color in enumerate(colors):
            if all(support.isdisjoint(cols_by_row[other]) for other in color):
                colors[idx].append(row)
                break
        else:
            colors.append([row])
    return colors


def make_row_pattern(mask: np.ndarray) -> RowSparsePattern:
    row_colors = greedy_row_coloring(mask)
    cols_by_row = [np.nonzero(mask[row])[0] for row in range(mask.shape[0])]
    nnz = int(mask.sum())
    return RowSparsePattern(mask, row_colors, cols_by_row, nnz, nnz / mask.size)


def make_row_seed_matrix(rp: RowSparsePattern) -> np.ndarray:
    seeds = np.zeros((len(rp.row_colors), rp.pattern.shape[0]))
    for idx, color in enumerate(rp.row_colors):
        seeds[idx, color] = 1.0
    return seeds


@jax.jit
def batched_vjp(x, seeds, *args):
    _, pullback = jax.vjp(lambda y: v044.residual_double_prismatic(y, *args), x)

    def one(seed):
        return pullback(seed)[0]

    return jax.vmap(one)(seeds)


def row_colored_vjp_csr(x: np.ndarray, args, rp: RowSparsePattern, seeds: np.ndarray):
    started = time.perf_counter()
    grads_by_color = np.asarray(batched_vjp(jnp.asarray(x, dtype=jnp.float64), jnp.asarray(seeds, dtype=jnp.float64), *args), dtype=float)
    rows = []
    cols = []
    data = []
    for color_idx, rows_in_color in enumerate(rp.row_colors):
        grad = grads_by_color[color_idx]
        for row in rows_in_color:
            row_cols = rp.cols_by_row[row]
            if row_cols.size:
                values = grad[row_cols]
                keep = np.abs(values) > SPARSITY_ATOL
                if np.any(keep):
                    kept_cols = row_cols[keep]
                    rows.extend([row] * kept_cols.size)
                    cols.extend(kept_cols.tolist())
                    data.extend(values[keep].tolist())
    return sparse.csr_matrix((data, (rows, cols)), shape=rp.pattern.shape), time.perf_counter() - started


def gauss_step_row_vjp(state, params, rp: RowSparsePattern, row_seeds: np.ndarray):
    x = v044.stage_guess(state, H, params)
    args = v044.build_args(state, H, params)
    total_residual = 0.0
    total_jac = 0.0
    total_linear = 0.0
    linear_solves = 0
    max_linear_residual = 0.0
    last_norm = np.inf
    for it in range(80):
        x_jax = jnp.asarray(x, dtype=jnp.float64)
        started = time.perf_counter()
        res = np.asarray(v044.R_VALUE(x_jax, *args), dtype=float)
        total_residual += time.perf_counter() - started
        last_norm = float(np.linalg.norm(res))
        if last_norm < 1.0e-11:
            break
        csr, jac_sec = row_colored_vjp_csr(x, args, rp, row_seeds)
        total_jac += jac_sec
        started = time.perf_counter()
        delta = spla.spsolve(csr, -res)
        total_linear += time.perf_counter() - started
        linear_solves += 1
        max_linear_residual = max(max_linear_residual, float(np.linalg.norm(csr @ delta + res)))
        x = x + np.asarray(delta, dtype=float)
        if float(np.linalg.norm(delta)) < 1.0e-11:
            break
    else:
        raise RuntimeError(f"row-VJP Newton failed residual={last_norm:.3e}")
    stages = v044.unpack_stages(x)
    next_state = v044.next_state_from_stages(state, H, stages)
    con, vel = v044.constraint_parts_np(next_state, params)
    pa, oa = v044.stage_acceleration_parts(state, stages, params)
    diag = {
        "newton_iterations": it + 1,
        "linear_solves": linear_solves,
        "jacobian_assemblies": linear_solves,
        "total_residual_eval_sec": total_residual,
        "total_jacobian_eval_sec": total_jac,
        "total_linear_solve_sec": total_linear,
        "max_linear_residual_norm": max_linear_residual,
        "max_endpoint_constraint_norm": float(np.linalg.norm(con)),
        "max_endpoint_velocity_constraint_norm": float(np.linalg.norm(vel)),
        "max_stage_position_acceleration_constraint_norm": pa,
        "max_stage_orientation_acceleration_constraint_norm": oa,
        "max_quaternion_unit_error": float(np.max(np.abs(np.linalg.norm(next_state.p, axis=1) - 1.0))),
    }
    return next_state, diag


def integrate_row_vjp(params, rp: RowSparsePattern, row_seeds: np.ndarray):
    state = v044.initial_state(params)
    totals = {
        "total_newton_iterations": 0,
        "total_linear_solves": 0,
        "total_jacobian_assemblies": 0,
        "total_residual_eval_sec": 0.0,
        "total_jacobian_eval_sec": 0.0,
        "total_linear_solve_sec": 0.0,
        "max_linear_residual_norm": 0.0,
        "max_endpoint_constraint_norm": 0.0,
        "max_endpoint_velocity_constraint_norm": 0.0,
        "max_stage_position_acceleration_constraint_norm": 0.0,
        "max_stage_orientation_acceleration_constraint_norm": 0.0,
        "max_quaternion_unit_error": 0.0,
    }
    n_steps = int(round(T_FINAL / H))
    for _ in range(n_steps):
        state, diag = gauss_step_row_vjp(state, params, rp, row_seeds)
        totals["total_newton_iterations"] += diag["newton_iterations"]
        totals["total_linear_solves"] += diag["linear_solves"]
        totals["total_jacobian_assemblies"] += diag["jacobian_assemblies"]
        for key in [
            "total_residual_eval_sec",
            "total_jacobian_eval_sec",
            "total_linear_solve_sec",
            "max_linear_residual_norm",
            "max_endpoint_constraint_norm",
            "max_endpoint_velocity_constraint_norm",
            "max_stage_position_acceleration_constraint_norm",
            "max_stage_orientation_acceleration_constraint_norm",
            "max_quaternion_unit_error",
        ]:
            if key.startswith("total"):
                totals[key] += diag[key]
            else:
                totals[key] = max(totals[key], diag[key])
    totals["state"] = state
    totals["steps"] = n_steps
    totals["avg_jacobian_eval_sec"] = totals["total_jacobian_eval_sec"] / max(totals["total_jacobian_assemblies"], 1)
    totals["avg_linear_solve_sec"] = totals["total_linear_solve_sec"] / max(totals["total_linear_solves"], 1)
    return totals


def warm_vjp(params, rp: RowSparsePattern, row_seeds: np.ndarray) -> None:
    state = v044.initial_state(params)
    x = v044.stage_guess(state, H, params)
    args = v044.build_args(state, H, params)
    np.asarray(batched_vjp(jnp.asarray(x, dtype=jnp.float64), jnp.asarray(row_seeds, dtype=jnp.float64), *args), dtype=float)


def pattern_relation(candidate, reference) -> dict:
    extra = np.logical_and(candidate.pattern, np.logical_not(reference.pattern))
    missing = np.logical_and(reference.pattern, np.logical_not(candidate.pattern))
    return {
        "extra_vs_reference": int(extra.sum()),
        "missing_vs_reference": int(missing.sum()),
        "candidate_nnz": candidate.nnz,
        "reference_nnz": reference.nnz,
        "candidate_column_colors": len(candidate.colors),
        "reference_column_colors": len(reference.colors),
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def json_safe(obj: object) -> object:
    return v044.json_safe(obj)


def state_error(ref, state) -> tuple[float, float]:
    return v044.state_error(ref, state)


def row_from_run(case_name: str, solver: str, out: dict, runtime: float, column_pattern, row_pattern: RowSparsePattern, relation: dict, pattern_build: float, dense_pattern_sec: float, perr: float, verr: float):
    return {
        "case": case_name,
        "solver": solver,
        "h": f"{H:.10g}",
        "status": "ok",
        "error_message": "",
        "steps": out["steps"],
        "runtime_sec": f"{runtime:.8e}",
        "pattern_build_sec": f"{pattern_build:.8e}",
        "dense_validation_pattern_sec": f"{dense_pattern_sec:.8e}",
        "total_newton_iterations": out["total_newton_iterations"],
        "total_linear_solves": out["total_linear_solves"],
        "total_jacobian_assemblies": out["total_jacobian_assemblies"],
        "total_residual_eval_sec": f"{out['total_residual_eval_sec']:.16e}",
        "total_jacobian_eval_sec": f"{out['total_jacobian_eval_sec']:.16e}",
        "total_linear_solve_sec": f"{out['total_linear_solve_sec']:.16e}",
        "avg_jacobian_eval_sec": f"{out['avg_jacobian_eval_sec']:.16e}",
        "avg_linear_solve_sec": f"{out['avg_linear_solve_sec']:.16e}",
        "pattern_nnz": column_pattern.nnz,
        "pattern_density": f"{column_pattern.density:.16e}",
        "column_colors": len(column_pattern.colors),
        "row_colors": len(row_pattern.row_colors),
        "pattern_missing_vs_dense": relation["missing_vs_reference"],
        "pattern_extra_vs_dense": relation["extra_vs_reference"],
        "position_error_vs_dense": f"{perr:.16e}",
        "velocity_error_vs_dense": f"{verr:.16e}",
        "max_linear_residual_norm": f"{out['max_linear_residual_norm']:.16e}",
        "max_endpoint_constraint_norm": f"{out['max_endpoint_constraint_norm']:.16e}",
        "max_endpoint_velocity_constraint_norm": f"{out['max_endpoint_velocity_constraint_norm']:.16e}",
        "max_stage_position_acceleration_constraint_norm": f"{out['max_stage_position_acceleration_constraint_norm']:.16e}",
        "max_stage_orientation_acceleration_constraint_norm": f"{out['max_stage_orientation_acceleration_constraint_norm']:.16e}",
        "max_quaternion_unit_error": f"{out['max_quaternion_unit_error']:.16e}",
    }


def run_case(case_name: str, params) -> dict:
    block = v044.generated_block_superset_pattern()
    pruned, pruned_build_sec = v044.build_pruned_pattern(params, block)
    row_pattern = make_row_pattern(pruned.pattern)
    column_seeds = v044.make_seed_matrix(pruned)
    row_seeds = make_row_seed_matrix(row_pattern)
    v044.warm_jax(params, pruned, column_seeds)
    warm_vjp(params, row_pattern, row_seeds)
    dense_pattern, dense_pattern_sec = v044.dense_validation_pattern(params)
    relation = pattern_relation(pruned, dense_pattern)
    block_relation = v044.pattern_relation(block, dense_pattern)

    # Warm all timed integration paths once after compilation.
    v044.integrate(params, "dense_jacfwd_csr", pruned, column_seeds)
    v044.integrate(params, "generated_block_jvp_pruned", pruned, column_seeds)
    integrate_row_vjp(params, row_pattern, row_seeds)

    rows = []
    runs = {}
    dense_state = None
    timed = [
        ("dense_jacfwd_csr", "dense_jacfwd_csr", 0.0),
        ("column_jvp_pruned", "generated_block_jvp_pruned", pruned_build_sec),
        ("row_vjp_pruned", "row_vjp_pruned", pruned_build_sec),
    ]
    for public_name, solver, build_sec in timed:
        started = time.perf_counter()
        if solver == "row_vjp_pruned":
            out = integrate_row_vjp(params, row_pattern, row_seeds)
        else:
            out = v044.integrate(params, solver, pruned, column_seeds)
        runtime = time.perf_counter() - started
        if public_name == "dense_jacfwd_csr":
            dense_state = out["state"]
            perr, verr = 0.0, 0.0
        else:
            assert dense_state is not None
            perr, verr = state_error(dense_state, out["state"])
        runs[public_name] = {key: value for key, value in out.items() if key != "state"} | {"status": "ok", "runtime_sec": runtime, "position_error_vs_dense": perr, "velocity_error_vs_dense": verr}
        rows.append(row_from_run(case_name, public_name, out, runtime, pruned, row_pattern, relation, build_sec, dense_pattern_sec, perr, verr))

    return {
        "stribeck_velocity": CASES[case_name],
        "jvp_pruned_pattern_build_sec": pruned_build_sec,
        "dense_validation_pattern_build_sec": dense_pattern_sec,
        "patterns": {
            "generated_block_superset": {"nnz": block.nnz, "density": block.density, "column_colors": len(block.colors)},
            "generated_block_jvp_pruned": {"nnz": pruned.nnz, "density": pruned.density, "column_colors": len(pruned.colors), "row_colors": len(row_pattern.row_colors)},
            "dense_validation": {"nnz": dense_pattern.nnz, "density": dense_pattern.density, "column_colors": len(dense_pattern.colors)},
        },
        "relations": {"block_vs_dense": block_relation, "pruned_vs_dense": relation},
        "runs": runs,
        "rows": rows,
    }


def run_experiment() -> dict:
    rows = []
    cases = {}
    for case_name, vs in CASES.items():
        params = v044.make_params(vs)
        case = run_case(case_name, params)
        rows.extend(case.pop("rows"))
        cases[case_name] = case
    write_csv(RESULTS / "row_vjp_prismatic_runs.csv", rows)
    return {"h": H, "t_final": T_FINAL, "dimension": DIM, "stage_size": v044.STAGE_SIZE, "cases": cases}


def plot_results(summary: dict) -> None:
    import matplotlib.pyplot as plt

    labels = []
    dense_runtime = []
    column_runtime = []
    row_runtime = []
    column_colors = []
    row_colors = []
    for case_name, case in summary["cases"].items():
        labels.append(case_name.replace("double_prismatic_", ""))
        dense_runtime.append(case["runs"]["dense_jacfwd_csr"]["runtime_sec"])
        column_runtime.append(case["runs"]["column_jvp_pruned"]["runtime_sec"])
        row_runtime.append(case["runs"]["row_vjp_pruned"]["runtime_sec"])
        column_colors.append(case["patterns"]["generated_block_jvp_pruned"]["column_colors"])
        row_colors.append(case["patterns"]["generated_block_jvp_pruned"]["row_colors"])

    xs = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(8.8, 4.0))
    ax.bar(xs - 0.25, dense_runtime, width=0.25, label="dense jacfwd CSR")
    ax.bar(xs, column_runtime, width=0.25, label="column JVP")
    ax.bar(xs + 0.25, row_runtime, width=0.25, label="row VJP")
    ax.set_yscale("log")
    ax.set_ylabel("runtime seconds")
    ax.set_xticks(xs)
    ax.set_xticklabels(labels)
    ax.grid(True, axis="y", alpha=0.35)
    ax.legend()
    fig.tight_layout()
    fig.savefig(RESULTS / "row_vjp_runtime.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.4, 4.0))
    ax.bar(xs - 0.18, column_colors, width=0.36, label="column colors")
    ax.bar(xs + 0.18, row_colors, width=0.36, label="row colors")
    ax.set_ylabel("colors")
    ax.set_xticks(xs)
    ax.set_xticklabels(labels)
    ax.grid(True, axis="y", alpha=0.35)
    ax.legend()
    fig.tight_layout()
    fig.savefig(RESULTS / "row_vjp_colors.png", dpi=180)
    plt.close(fig)


def write_report(summary: dict) -> None:
    lines = [
        "# v045 Experiment Report",
        "",
        "Generated by `run_v045.py`.",
        "",
        "## Purpose",
        "",
        "- Address v044's 90-color column-JVP bottleneck on the double-prismatic interbody benchmark.",
        "- Keep the same 138D Gauss6 FullVA residual and exact JVP-pruned sparse pattern.",
        "- Assemble the same sparse Jacobian with row-colored batched VJP, where row coloring needs fewer seeds than column coloring.",
        "",
        "## Results",
        "",
    ]
    for case_name, case in summary["cases"].items():
        dense = case["runs"]["dense_jacfwd_csr"]
        col = case["runs"]["column_jvp_pruned"]
        row = case["runs"]["row_vjp_pruned"]
        rel = case["relations"]["pruned_vs_dense"]
        pat = case["patterns"]["generated_block_jvp_pruned"]
        lines.append(f"### {case_name}")
        lines.append(
            f"- Pattern: {pat['nnz']} entries; column colors {pat['column_colors']}, row colors {pat['row_colors']}; "
            f"dense-validation missing {rel['missing_vs_reference']}, extra {rel['extra_vs_reference']}."
        )
        lines.append(
            f"- Runtime: dense {dense['runtime_sec']:.3f}s, column-JVP {col['runtime_sec']:.3f}s, row-VJP {row['runtime_sec']:.3f}s. "
            f"Row-VJP speed vs column-JVP {col['runtime_sec'] / max(row['runtime_sec'], 1e-30):.2f}x; vs dense {dense['runtime_sec'] / max(row['runtime_sec'], 1e-30):.2f}x."
        )
        lines.append(
            f"- Trajectory diff vs dense: position {row['position_error_vs_dense']:.3e}, velocity {row['velocity_error_vs_dense']:.3e}; "
            f"endpoint velocity constraint {row['max_endpoint_velocity_constraint_norm']:.3e}; orientation acceleration "
            f"{row['max_stage_orientation_acceleration_constraint_norm']:.3e}."
        )
        lines.append("")
    lines.extend(
        [
            "## Interpretation",
            "",
            "- Row coloring lowers the seed count for this square residual because output rows have sparser overlap than input columns.",
            "- The row-VJP path keeps the same pruned sparse pattern and therefore the same Newton map when validation misses are zero.",
            "- If row-VJP is still slower than dense `jacfwd`, the remaining issue is reverse-mode overhead rather than the color count alone.",
            "",
            "## Outputs",
            "",
            "- `row_vjp_prismatic_runs.csv`",
            "- `summary_v045.json`",
            "- `row_vjp_runtime.png`",
            "- `row_vjp_colors.png`",
            "",
        ]
    )
    (RESULTS / "v045_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    experiment = run_experiment()
    plot_results(experiment)
    summary = {
        "version": "v045_row_colored_vjp_prismatic",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "scipy": __import__("scipy").__version__,
        "jax": jax.__version__,
        "source_versions": ["v044_double_prismatic_chain"],
        "model": {
            "cases": CASES,
            "method": "row_colored_vjp_double_prismatic_gauss6_fullva",
            "h": H,
            "t_final": T_FINAL,
            "dimension": DIM,
            "stage_size": v044.STAGE_SIZE,
        },
        "experiment": experiment,
        "runtime_sec": time.perf_counter() - started,
    }
    with (RESULTS / "summary_v045.json").open("w", encoding="utf-8") as f:
        json.dump(json_safe(summary), f, indent=2, sort_keys=True)
    write_report(experiment)


if __name__ == "__main__":
    main()
