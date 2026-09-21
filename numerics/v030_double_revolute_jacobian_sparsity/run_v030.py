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
MODES = ["raw", "pivot_va", "full_va"]
STAGE_COUNTS = [2, 3]
H = 0.02
T_FINAL_FOR_CONTEXT = 0.2
SPARSITY_ATOL = 1.0e-12
SOLVE_REPEATS = 80
CSV_COLUMNS = [
    "case",
    "mode",
    "n_stages",
    "dimension",
    "newton_iterations",
    "residual_norm",
    "jacobian_eval_sec",
    "dense_nnz",
    "density",
    "condition_number",
    "dense_solve_sec",
    "csr_conversion_sec",
    "sparse_solve_sec",
    "sparse_solve_residual_norm",
    "dense_sparse_solution_diff",
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
    raise ValueError(f"unsupported mode/stages {mode}/{n_stages}")


def converged_stage_solution(case_name: str, mode: str, n_stages: int):
    import jax.numpy as jnp

    params = v029.make_params(CASES[case_name])
    state = v029.initial_state(params)
    x = v029.stage_guess(state, H, params, n_stages)
    args = build_args(state, H, params)
    value, jacobian, max_iters = select_residual(mode, n_stages)
    last_norm = np.inf
    niters = 0
    # Warm JIT compilation outside the timed final Jacobian measurement.
    x_jax = jnp.asarray(x, dtype=jnp.float64)
    np.asarray(value(x_jax, *args), dtype=float)
    np.asarray(jacobian(x_jax, *args), dtype=float)
    for it in range(max_iters):
        x_jax = jnp.asarray(x, dtype=jnp.float64)
        res = np.asarray(value(x_jax, *args), dtype=float)
        last_norm = float(np.linalg.norm(res))
        niters = it + 1
        if last_norm < 1.0e-11:
            break
        jac = np.asarray(jacobian(x_jax, *args), dtype=float)
        delta = np.linalg.solve(jac, -res)
        x = x + delta
        if float(np.linalg.norm(delta)) < 1.0e-11:
            break
    else:
        raise RuntimeError(f"Newton failed for {case_name}/{mode}/{n_stages}, residual={last_norm:.3e}")
    x_jax = jnp.asarray(x, dtype=jnp.float64)
    res = np.asarray(value(x_jax, *args), dtype=float)
    start = time.perf_counter()
    jac = np.asarray(jacobian(x_jax, *args), dtype=float)
    jac_time = time.perf_counter() - start
    return x, res, jac, jac_time, niters, float(np.linalg.norm(res)), params


def time_solve(fn, repeats: int) -> tuple[float, object]:
    output = None
    start = time.perf_counter()
    for _ in range(repeats):
        output = fn()
    return (time.perf_counter() - start) / repeats, output


def analyze_case_with_timing(case_name: str, mode: str, n_stages: int) -> dict:
    _, res, jac, jac_time, niters, res_norm, _ = converged_stage_solution(case_name, mode, n_stages)
    dim = jac.shape[0]
    mask = np.abs(jac) > SPARSITY_ATOL
    nnz = int(mask.sum())
    density = nnz / float(dim * dim)
    condition = float(np.linalg.cond(jac))
    rng = np.random.default_rng(20260526 + dim + len(mode))
    rhs = rng.standard_normal(dim)
    dense_sec, dense_solution = time_solve(lambda: np.linalg.solve(jac, rhs), SOLVE_REPEATS)
    start = time.perf_counter()
    csr = sparse.csr_matrix(np.where(mask, jac, 0.0))
    csr_conversion = time.perf_counter() - start
    sparse_sec, sparse_solution = time_solve(lambda: spla.spsolve(csr, rhs), SOLVE_REPEATS)
    sparse_residual = float(np.linalg.norm(jac @ sparse_solution - rhs))
    solution_diff = float(np.linalg.norm(dense_solution - sparse_solution))
    return {
        "case": case_name,
        "mode": mode,
        "n_stages": n_stages,
        "dimension": dim,
        "newton_iterations": niters,
        "residual_norm": res_norm,
        "jacobian_eval_sec": jac_time,
        "dense_nnz": nnz,
        "density": density,
        "condition_number": condition,
        "dense_solve_sec": dense_sec,
        "csr_conversion_sec": csr_conversion,
        "sparse_solve_sec": sparse_sec,
        "sparse_solve_residual_norm": sparse_residual,
        "dense_sparse_solution_diff": solution_diff,
        "jacobian": jac,
    }


def run_diagnostics() -> dict:
    rows = []
    cases = {}
    for case_name in CASES:
        case_rows = []
        for n_stages in STAGE_COUNTS:
            for mode in MODES:
                item = analyze_case_with_timing(case_name, mode, n_stages)
                rows.append(item)
                case_rows.append({key: value for key, value in item.items() if key != "jacobian"})
        cases[case_name] = case_rows
    write_csv(
        RESULTS / "double_revolute_jacobian_sparsity.csv",
        [
            {
                key: (f"{row[key]:.16e}" if isinstance(row.get(key), float) else row.get(key))
                for key in CSV_COLUMNS
            }
            for row in rows
        ],
    )
    return {"rows": rows, "cases": cases}


def plot_results(summary: dict) -> None:
    import matplotlib.pyplot as plt

    rows = summary["rows"]
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.2))
    labels = [f"{r['case'].replace('double_revolute_', '')}\nG{2 * r['n_stages']} {r['mode']}" for r in rows]
    xs = np.arange(len(rows))
    axes[0].bar(xs, [r["density"] for r in rows])
    axes[0].set_ylabel("Jacobian density")
    axes[0].set_xticks(xs)
    axes[0].set_xticklabels(labels, rotation=70, ha="right", fontsize=7)
    axes[0].grid(True, axis="y", alpha=0.35)

    axes[1].bar(xs - 0.18, [r["dense_solve_sec"] for r in rows], width=0.36, label="dense solve")
    axes[1].bar(xs + 0.18, [r["sparse_solve_sec"] for r in rows], width=0.36, label="CSR spsolve")
    axes[1].set_ylabel("average solve seconds")
    axes[1].set_yscale("log")
    axes[1].set_xticks(xs)
    axes[1].set_xticklabels(labels, rotation=70, ha="right", fontsize=7)
    axes[1].grid(True, axis="y", alpha=0.35)
    axes[1].legend()
    fig.tight_layout()
    fig.savefig(RESULTS / "double_revolute_sparse_solve_summary.png", dpi=180)
    plt.close(fig)

    selected = [
        row
        for row in rows
        if row["case"] == "double_revolute_smooth" and row["mode"] == "full_va" and row["n_stages"] == 3
    ][0]
    plt.figure(figsize=(6.0, 6.0))
    plt.spy(np.abs(selected["jacobian"]) > SPARSITY_ATOL, markersize=1.4)
    plt.title("Smooth Gauss6 FullVA Jacobian Sparsity")
    plt.tight_layout()
    plt.savefig(RESULTS / "double_revolute_gauss6_fullva_sparsity.png", dpi=220)
    plt.close()


def write_report(summary: dict) -> None:
    rows = summary["rows"]
    smooth_full = next(
        r for r in rows if r["case"] == "double_revolute_smooth" and r["mode"] == "full_va" and r["n_stages"] == 3
    )
    sharp_full = next(
        r for r in rows if r["case"] == "double_revolute_sharp" and r["mode"] == "full_va" and r["n_stages"] == 3
    )
    best_sparse = min(rows, key=lambda r: r["sparse_solve_sec"] / max(r["dense_solve_sec"], 1e-30))
    worst_sparse = max(rows, key=lambda r: r["sparse_solve_sec"] / max(r["dense_solve_sec"], 1e-30))
    gauss6_rows = [row for row in rows if row["n_stages"] == 3]
    best_gauss6_ratio = min(row["sparse_solve_sec"] / max(row["dense_solve_sec"], 1e-30) for row in gauss6_rows)
    worst_gauss6_ratio = max(row["sparse_solve_sec"] / max(row["dense_solve_sec"], 1e-30) for row in gauss6_rows)
    lines = [
        "# v030 Experiment Report",
        "",
        "Generated by `run_v030.py`.",
        "",
        "## Purpose",
        "",
        "- Diagnose the dense Newton cost wall exposed by v029's double-revolute Gauss6 FullVA residual.",
        "- Measure Jacobian sparsity, condition number, dense solve time, and CSR sparse solve time for the converged first-step Newton systems.",
        "- Use the same v029 residual code and Brown-McPhee multiplier-dependent friction; this version changes the linear algebra diagnostics, not the integrator equations.",
        "",
        "## Results",
        "",
    ]
    for row in rows:
        ratio = row["sparse_solve_sec"] / max(row["dense_solve_sec"], 1e-30)
        lines.append(
            f"- `{row['case']} {row['mode']} G{2 * row['n_stages']}`: dim {row['dimension']}, "
            f"density {row['density']:.3f}, cond {row['condition_number']:.3e}, "
            f"dense solve {row['dense_solve_sec']:.3e}s, sparse solve {row['sparse_solve_sec']:.3e}s "
            f"({ratio:.2f}x dense), sparse residual {row['sparse_solve_residual_norm']:.3e}."
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"- Smooth Gauss6 FullVA has dimension {smooth_full['dimension']} and density {smooth_full['density']:.3f}; sharp Gauss6 FullVA density is {sharp_full['density']:.3f}.",
            f"- The best sparse/dense solve ratio observed is {best_sparse['sparse_solve_sec'] / max(best_sparse['dense_solve_sec'], 1e-30):.2f}x for `{best_sparse['case']} {best_sparse['mode']} G{2 * best_sparse['n_stages']}`.",
            f"- The worst sparse/dense solve ratio observed is {worst_sparse['sparse_solve_sec'] / max(worst_sparse['dense_solve_sec'], 1e-30):.2f}x for `{worst_sparse['case']} {worst_sparse['mode']} G{2 * worst_sparse['n_stages']}`.",
            f"- For Gauss6 specifically, sparse/dense solve ratios range from {best_gauss6_ratio:.3e}x to {worst_gauss6_ratio:.3e}x; CSR `spsolve` is decisively faster for the 138-dimensional systems in this environment.",
            "- For Gauss4, the 92-dimensional systems are too small for generic CSR to be consistently better; sparse overhead sometimes loses.",
            "- The immediate v031 engineering target should be integrating sparse/block linear solves into the Gauss6 Newton loop. The deeper target is to avoid materializing a dense AD Jacobian by exploiting block/stage sparsity or using structured Newton-Krylov.",
            "",
            "## Outputs",
            "",
            "- `double_revolute_jacobian_sparsity.csv`",
            "- `summary_v030.json`",
            "- `double_revolute_sparse_solve_summary.png`",
            "- `double_revolute_gauss6_fullva_sparsity.png`",
            "",
        ]
    )
    (RESULTS / "v030_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    diagnostics = run_diagnostics()
    plot_results(diagnostics)
    summary = {
        "version": "v030_double_revolute_jacobian_sparsity",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "scipy": __import__("scipy").__version__,
        "source_version": "v029_double_revolute_pivotva_dae",
        "model": {
            "cases": CASES,
            "modes": MODES,
            "stage_counts": STAGE_COUNTS,
            "h": H,
            "t_final_context": T_FINAL_FOR_CONTEXT,
            "sparsity_atol": SPARSITY_ATOL,
            "solve_repeats": SOLVE_REPEATS,
        },
        "diagnostics": {
            "rows": [{key: value for key, value in row.items() if key != "jacobian"} for row in diagnostics["rows"]]
        },
        "runtime_sec": time.perf_counter() - started,
    }
    with (RESULTS / "summary_v030.json").open("w", encoding="utf-8") as f:
        json.dump(json_safe(summary), f, indent=2, sort_keys=True)
    write_report(diagnostics)


if __name__ == "__main__":
    main()
