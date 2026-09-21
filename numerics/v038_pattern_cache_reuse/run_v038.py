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


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RESULTS = HERE / "results"
V037_PATH = ROOT / "v037_jvp_pruned_symbolic_pattern" / "run_v037.py"

CASES = {
    "double_revolute_smooth": 0.50,
    "double_revolute_sharp": 0.05,
}
DISCOVERY_CASE = "double_revolute_smooth"
H = 0.02
T_DISCOVERY = 0.06
T_VALIDATE = 0.12
PATTERN_ATOL = 1.0e-14
CSV_COLUMNS = [
    "case",
    "solver",
    "pattern_source",
    "h",
    "t_final",
    "status",
    "error_message",
    "steps",
    "runtime_sec",
    "pattern_build_sec",
    "validation_dense_pattern_build_sec",
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
    "cached_extra_vs_validation_dense",
    "cached_missing_vs_validation_dense",
    "orientation_error_vs_dense_rad",
    "omega_error_vs_dense",
    "max_linear_residual_norm",
    "max_endpoint_constraint_norm",
    "max_endpoint_velocity_constraint_norm",
    "max_stage_pivot_acceleration_constraint_norm",
    "max_stage_axis_acceleration_constraint_norm",
    "max_quaternion_unit_error",
]


def load_v037():
    spec = importlib.util.spec_from_file_location("v037_jvp_pruned_symbolic_pattern", V037_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


v037 = load_v037()
v036 = v037.v036
v035 = v037.v035
v034 = v037.v034
v029 = v037.v029


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


def make_sparse_pattern(mask: np.ndarray):
    return v034.make_sparse_pattern_from_mask(mask)


def pattern_relation(candidate, reference) -> dict:
    extra = np.logical_and(candidate.pattern, np.logical_not(reference.pattern))
    missing = np.logical_and(reference.pattern, np.logical_not(candidate.pattern))
    return {
        "extra_vs_reference": int(extra.sum()),
        "missing_vs_reference": int(missing.sum()),
        "candidate_nnz": candidate.nnz,
        "reference_nnz": reference.nnz,
        "candidate_colors": len(candidate.colors),
        "reference_colors": len(reference.colors),
    }


def build_dense_validation_pattern(params, t_final: float):
    state = v029.initial_state(params)
    pattern = None
    _, _, b = v029.qp.gauss_legendre_coefficients(3)
    for _ in range(int(round(t_final / H))):
        x = v029.stage_guess(state, H, params, 3)
        args = v035.v031.build_args(state, H, params)
        for _it in range(8):
            x_jax = jnp.asarray(x, dtype=jnp.float64)
            res = np.asarray(v029.R3_FULL_VALUE(x_jax, *args), dtype=float)
            jac = np.asarray(v029.R3_FULL_JAC(x_jax, *args), dtype=float)
            current = np.abs(jac) > PATTERN_ATOL
            pattern = current if pattern is None else np.logical_or(pattern, current)
            if float(np.linalg.norm(res)) < 1.0e-11:
                break
            delta = np.linalg.solve(jac, -res)
            x = x + delta
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
    assert pattern is not None
    return make_sparse_pattern(pattern)


def integrate_solver_tfinal(params, solver: str, sp, seeds: np.ndarray, t_final: float):
    n_steps = int(round(t_final / H))
    state = v029.initial_state(params)
    total_iters = 0
    total_linear_solves = 0
    total_jacobian_assemblies = 0
    total_residual_eval = 0.0
    total_jacobian_eval = 0.0
    total_linear_solve = 0.0
    max_linear_residual = 0.0
    max_endpoint_constraint = 0.0
    max_endpoint_velocity = 0.0
    max_stage_pivot_a = 0.0
    max_stage_axis_a = 0.0
    max_quat = 0.0
    for _ in range(n_steps):
        state, niters, diag = v035.gauss_step_with_jacobian_source(state, H, params, solver, sp, seeds)
        total_iters += niters
        total_linear_solves += diag["linear_solves"]
        total_jacobian_assemblies += diag["jacobian_assemblies"]
        total_residual_eval += diag["total_residual_eval_sec"]
        total_jacobian_eval += diag["total_jacobian_eval_sec"]
        total_linear_solve += diag["total_linear_solve_sec"]
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
        "max_linear_residual_norm": max_linear_residual,
        "max_endpoint_constraint_norm": max_endpoint_constraint,
        "max_endpoint_velocity_constraint_norm": max_endpoint_velocity,
        "max_stage_pivot_acceleration_constraint_norm": max_stage_pivot_a,
        "max_stage_axis_acceleration_constraint_norm": max_stage_axis_a,
        "max_quaternion_unit_error": max_quat,
    }


def row_from_run(
    case_name: str,
    solver: str,
    source: str,
    out: dict,
    runtime: float,
    sp,
    relation: dict,
    pattern_build_sec: float,
    validation_build_sec: float,
    oerr: float,
    werr: float,
) -> dict:
    return {
        "case": case_name,
        "solver": solver,
        "pattern_source": source,
        "h": f"{H:.10g}",
        "t_final": f"{T_VALIDATE:.10g}",
        "status": "ok",
        "error_message": "",
        "steps": out["steps"],
        "runtime_sec": f"{runtime:.8e}",
        "pattern_build_sec": f"{pattern_build_sec:.8e}",
        "validation_dense_pattern_build_sec": f"{validation_build_sec:.8e}",
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
        "cached_extra_vs_validation_dense": relation["extra_vs_reference"],
        "cached_missing_vs_validation_dense": relation["missing_vs_reference"],
        "orientation_error_vs_dense_rad": f"{oerr:.16e}",
        "omega_error_vs_dense": f"{werr:.16e}",
        "max_linear_residual_norm": f"{out['max_linear_residual_norm']:.16e}",
        "max_endpoint_constraint_norm": f"{out['max_endpoint_constraint_norm']:.16e}",
        "max_endpoint_velocity_constraint_norm": f"{out['max_endpoint_velocity_constraint_norm']:.16e}",
        "max_stage_pivot_acceleration_constraint_norm": f"{out['max_stage_pivot_acceleration_constraint_norm']:.16e}",
        "max_stage_axis_acceleration_constraint_norm": f"{out['max_stage_axis_acceleration_constraint_norm']:.16e}",
        "max_quaternion_unit_error": f"{out['max_quaternion_unit_error']:.16e}",
    }


def run_experiment() -> dict:
    rows = []
    smooth_params = v029.make_params(CASES[DISCOVERY_CASE])
    block = v036.build_block_symbolic_pattern()
    v037.warm_value_and_batched_jvp(smooth_params, block, v035.make_seed_matrix(block))
    start = time.perf_counter()
    cached = v037.build_jvp_pruned_pattern(smooth_params, block)
    cached_build_sec = time.perf_counter() - start
    cached_seeds = v035.make_seed_matrix(cached)
    v037.warm_value_and_batched_jvp(smooth_params, cached, cached_seeds)
    v034.warm_jax(smooth_params)

    cases = {}
    for case_name, vs in CASES.items():
        params = v029.make_params(vs)
        start = time.perf_counter()
        validation_pattern = build_dense_validation_pattern(params, T_VALIDATE)
        validation_build_sec = time.perf_counter() - start
        relation = pattern_relation(cached, validation_pattern)

        case_runs = {}
        dense_state = None
        for solver, source, internal_solver in [
            ("dense_jacfwd_csr", "dense", "dense_jacfwd_csr"),
            ("cached_jvp_pruned", f"cached_from_{DISCOVERY_CASE}", "batched_colored_jvp_csr"),
        ]:
            row = {key: "" for key in CSV_COLUMNS}
            row.update({"case": case_name, "solver": solver, "pattern_source": source, "h": f"{H:.10g}", "t_final": f"{T_VALIDATE:.10g}"})
            start = time.perf_counter()
            try:
                out = integrate_solver_tfinal(params, internal_solver, cached, cached_seeds, T_VALIDATE)
                runtime = time.perf_counter() - start
                if solver == "dense_jacfwd_csr":
                    dense_state = out["state"]
                    oerr, werr = 0.0, 0.0
                    pattern_build_sec = 0.0
                else:
                    assert dense_state is not None
                    oerr, werr = v029.state_error(dense_state, out["state"])
                    pattern_build_sec = cached_build_sec
                item = {key: value for key, value in out.items() if key != "state"}
                item.update(
                    {
                        "status": "ok",
                        "runtime_sec": runtime,
                        "pattern_build_sec": pattern_build_sec,
                        "orientation_error_vs_dense_rad": oerr,
                        "omega_error_vs_dense": werr,
                    }
                )
                row = row_from_run(
                    case_name,
                    solver,
                    source,
                    out,
                    runtime,
                    cached,
                    relation,
                    pattern_build_sec,
                    validation_build_sec,
                    oerr,
                    werr,
                )
            except Exception as exc:
                runtime = time.perf_counter() - start
                item = {"status": "failed", "error_message": str(exc), "runtime_sec": runtime}
                row.update({"status": "failed", "error_message": str(exc), "runtime_sec": f"{runtime:.8e}"})
            rows.append(row)
            case_runs[solver] = item
        cases[case_name] = {
            "stribeck_velocity": vs,
            "validation_t_final": T_VALIDATE,
            "validation_dense_pattern_build_sec": validation_build_sec,
            "validation_dense_pattern": {
                "nnz": validation_pattern.nnz,
                "density": validation_pattern.density,
                "colors": len(validation_pattern.colors),
            },
            "cached_relation_to_validation_dense": relation,
            "runs": case_runs,
        }
    write_csv(RESULTS / "double_revolute_cached_pattern_reuse_runs.csv", rows)
    return {
        "h": H,
        "discovery_t_final": T_DISCOVERY,
        "validation_t_final": T_VALIDATE,
        "discovery_case": DISCOVERY_CASE,
        "cached_pattern_build_sec": cached_build_sec,
        "cached_pattern": {"nnz": cached.nnz, "density": cached.density, "colors": len(cached.colors)},
        "cases": cases,
    }


def plot_results(summary: dict) -> None:
    import matplotlib.pyplot as plt

    labels = []
    dense_runtime = []
    cached_runtime = []
    dense_pattern_build = []
    cached_missing = []
    for case_name, case in summary["cases"].items():
        labels.append(case_name.replace("double_revolute_", ""))
        dense_runtime.append(case["runs"]["dense_jacfwd_csr"].get("runtime_sec", np.nan))
        cached_runtime.append(case["runs"]["cached_jvp_pruned"].get("runtime_sec", np.nan))
        dense_pattern_build.append(case["validation_dense_pattern_build_sec"])
        cached_missing.append(case["cached_relation_to_validation_dense"]["missing_vs_reference"])
    xs = np.arange(len(labels))
    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.0))
    axes[0].bar(xs - 0.18, dense_runtime, width=0.36, label="dense jacfwd CSR")
    axes[0].bar(xs + 0.18, cached_runtime, width=0.36, label="cached JVP-pruned")
    axes[0].set_yscale("log")
    axes[0].set_ylabel("runtime seconds")
    axes[1].bar(xs - 0.18, dense_pattern_build, width=0.36, label="dense validation pattern")
    axes[1].bar(xs + 0.18, [summary["cached_pattern_build_sec"]] * len(labels), width=0.36, label="cached pattern build once")
    axes[1].set_yscale("log")
    axes[1].set_ylabel("pattern build seconds")
    for ax in axes:
        ax.set_xticks(xs)
        ax.set_xticklabels(labels)
        ax.grid(True, axis="y", alpha=0.35)
        ax.legend()
    fig.tight_layout()
    fig.savefig(RESULTS / "double_revolute_cached_pattern_reuse_runtime.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    ax.bar(xs, cached_missing)
    ax.set_ylabel("cached pattern missing entries vs dense validation")
    ax.set_xticks(xs)
    ax.set_xticklabels(labels)
    ax.grid(True, axis="y", alpha=0.35)
    fig.tight_layout()
    fig.savefig(RESULTS / "double_revolute_cached_pattern_reuse_missing.png", dpi=180)
    plt.close(fig)


def write_report(summary: dict) -> None:
    lines = [
        "# v038 Experiment Report",
        "",
        "Generated by `run_v038.py`.",
        "",
        "## Purpose",
        "",
        "- Test whether a JVP-pruned sparse pattern can be cached and reused beyond the short discovery dry-run.",
        f"- Discover one cached pattern from `{DISCOVERY_CASE}` over T={T_DISCOVERY}, then reuse it for all cases over T={T_VALIDATE}.",
        "- Use dense Jacobian patterns only as longer-horizon validation, not as the cached-pattern construction method.",
        "",
        "## Results",
        "",
        f"- Cached pattern: {summary['cached_pattern']['nnz']} entries, {summary['cached_pattern']['colors']} colors, build {summary['cached_pattern_build_sec']:.3f}s.",
        "",
    ]
    for case_name, case in summary["cases"].items():
        dense = case["runs"]["dense_jacfwd_csr"]
        cached = case["runs"]["cached_jvp_pruned"]
        rel = case["cached_relation_to_validation_dense"]
        lines.append(f"### {case_name}")
        lines.append(
            f"- Longer-horizon dense validation pattern: {case['validation_dense_pattern']['nnz']} entries, "
            f"{case['validation_dense_pattern']['colors']} colors, build "
            f"{case['validation_dense_pattern_build_sec']:.3f}s."
        )
        lines.append(
            f"- Cached-vs-validation relation: extra {rel['extra_vs_reference']}, missing {rel['missing_vs_reference']}."
        )
        if dense.get("status") == "ok" and cached.get("status") == "ok":
            speed = dense["runtime_sec"] / max(cached["runtime_sec"], 1.0e-30)
            lines.append(
                f"- Runtime: dense {dense['runtime_sec']:.3f}s vs cached JVP-pruned "
                f"{cached['runtime_sec']:.3f}s (dense/cached {speed:.2f}x)."
            )
            lines.append(
                f"- Trajectory diff vs dense: orientation {cached['orientation_error_vs_dense_rad']:.3e} rad, "
                f"omega {cached['omega_error_vs_dense']:.3e}; endpoint velocity "
                f"{cached['max_endpoint_velocity_constraint_norm']:.3e}."
            )
        else:
            lines.append(f"- Status: dense {dense.get('status')}, cached {cached.get('status')}.")
        lines.append("")
    lines.extend(
        [
            "## Interpretation",
            "",
            "- The cached pattern built from the smooth short dry-run is valid for both smooth and sharp longer-horizon validation in this benchmark if missing entries remain zero.",
            "- This tests the production policy that a sparse pattern can be discovered once with JVP pruning and then reused for subsequent solves without dense Jacobian discovery.",
            "- If future larger systems show nonzero missing entries, the cache policy should union patterns from multiple dry-runs or refresh through the block-symbolic superset.",
            "",
            "## Outputs",
            "",
            "- `double_revolute_cached_pattern_reuse_runs.csv`",
            "- `summary_v038.json`",
            "- `double_revolute_cached_pattern_reuse_runtime.png`",
            "- `double_revolute_cached_pattern_reuse_missing.png`",
            "",
        ]
    )
    (RESULTS / "v038_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    experiment = run_experiment()
    plot_results(experiment)
    summary = {
        "version": "v038_pattern_cache_reuse",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "jax": v035.jax.__version__,
        "source_version": "v029_double_revolute_pivotva_dae",
        "solver_parent": "v037_jvp_pruned_symbolic_pattern",
        "model": {
            "cases": CASES,
            "discovery_case": DISCOVERY_CASE,
            "method": "double_revolute_gauss6_fullva",
            "h": H,
            "t_discovery": T_DISCOVERY,
            "t_validate": T_VALIDATE,
            "pattern_atol": PATTERN_ATOL,
        },
        "experiment": experiment,
        "runtime_sec": time.perf_counter() - started,
    }
    with (RESULTS / "summary_v038.json").open("w", encoding="utf-8") as f:
        json.dump(json_safe(summary), f, indent=2, sort_keys=True)
    write_report(experiment)


if __name__ == "__main__":
    main()
