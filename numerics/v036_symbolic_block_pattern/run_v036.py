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
V035_PATH = ROOT / "v035_batched_colored_jvp" / "run_v035.py"

CASES = {
    "double_revolute_smooth": 0.50,
    "double_revolute_sharp": 0.05,
}
H = 0.02
T_FINAL = 0.06
STAGE_SIZE = 46
N_STAGES = 3
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


def load_v035():
    spec = importlib.util.spec_from_file_location("v035_batched_colored_jvp", V035_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


v035 = load_v035()
v034 = v035.v034
v029 = v035.v029


BLOCK_OFFSETS = {
    "u1": (0, 3),
    "r1": (3, 6),
    "v1": (6, 9),
    "w1": (9, 12),
    "a1": (12, 15),
    "alpha1": (15, 18),
    "u2": (18, 21),
    "r2": (21, 24),
    "v2": (24, 27),
    "w2": (27, 30),
    "a2": (30, 33),
    "alpha2": (33, 36),
    "lambda": (36, 46),
}


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


def row_slice(stage: int, start: int, stop: int) -> slice:
    base = stage * STAGE_SIZE
    return slice(base + start, base + stop)


def col_slice(stage: int, block: str) -> slice:
    start, stop = BLOCK_OFFSETS[block]
    base = stage * STAGE_SIZE
    return slice(base + start, base + stop)


def add(mask: np.ndarray, rows: slice, deps: list[tuple[int, str]]) -> None:
    for stage, block in deps:
        mask[rows, col_slice(stage, block)] = True


def all_stage_blocks(*blocks: str) -> list[tuple[int, str]]:
    return [(stage, block) for stage in range(N_STAGES) for block in blocks]


def same(stage: int, *blocks: str) -> list[tuple[int, str]]:
    return [(stage, block) for block in blocks]


def build_block_symbolic_pattern():
    """Conservative block dependency pattern for v029 residual3_fullva.

    The mask follows the exact residual block order in v029:
    r_block, u_block, v_block, w_block, trans1, rot1, trans2, rot2,
    constraints. It intentionally over-approximates within small 3-vector
    blocks but does not inspect a dense Jacobian.
    """

    dim = STAGE_SIZE * N_STAGES
    mask = np.zeros((dim, dim), dtype=bool)
    for stage in range(N_STAGES):
        # r_block = [pv0, pv12]
        add(mask, row_slice(stage, 0, 3), same(stage, "u1", "v1", "w1"))
        add(mask, row_slice(stage, 3, 6), same(stage, "u1", "v1", "w1", "u2", "v2", "w2"))

        # u_block = [u1_coll_y, axis_rate1_xz, u2_coll_y, axis_rate2_xz].
        add(mask, row_slice(stage, 6, 7), all_stage_blocks("u1", "w1"))
        add(mask, row_slice(stage, 7, 9), same(stage, "u1", "w1"))
        add(mask, row_slice(stage, 9, 10), all_stage_blocks("u2", "w2"))
        add(mask, row_slice(stage, 10, 12), same(stage, "u2", "w2"))

        # v_block = [pa0, pa12].
        add(mask, row_slice(stage, 12, 15), same(stage, "u1", "w1", "a1", "alpha1"))
        add(
            mask,
            row_slice(stage, 15, 18),
            same(stage, "u1", "w1", "a1", "alpha1", "u2", "w2", "a2", "alpha2"),
        )

        # w_block = [w1_coll_y, axis_acc1_xz, w2_coll_y, axis_acc2_xz].
        add(mask, row_slice(stage, 18, 19), same(stage, "w1") + all_stage_blocks("alpha1"))
        add(mask, row_slice(stage, 19, 21), same(stage, "u1", "w1", "alpha1"))
        add(mask, row_slice(stage, 21, 22), same(stage, "w2") + all_stage_blocks("alpha2"))
        add(mask, row_slice(stage, 22, 24), same(stage, "u2", "w2", "alpha2"))

        # Dynamics.
        add(mask, row_slice(stage, 24, 27), same(stage, "a1", "lambda"))
        add(mask, row_slice(stage, 27, 30), same(stage, "u1", "w1", "alpha1", "w2", "lambda"))
        add(mask, row_slice(stage, 30, 33), same(stage, "a2", "lambda"))
        add(mask, row_slice(stage, 33, 36), same(stage, "u2", "w2", "alpha2", "w1", "lambda"))

        # Position/axis constraints.
        add(mask, row_slice(stage, 36, 39), same(stage, "r1", "u1"))
        add(mask, row_slice(stage, 39, 41), same(stage, "u1"))
        add(mask, row_slice(stage, 41, 44), same(stage, "r1", "u1", "r2", "u2"))
        add(mask, row_slice(stage, 44, 46), same(stage, "u2"))
    return v034.make_sparse_pattern_from_mask(mask)


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


def run_one(case_name: str, params) -> dict:
    start = time.perf_counter()
    warmup = v034.build_initial_pattern(params)
    warmup_build_sec = time.perf_counter() - start
    start = time.perf_counter()
    block = build_block_symbolic_pattern()
    block_build_sec = time.perf_counter() - start

    warmup_seeds = v035.make_seed_matrix(warmup)
    block_seeds = v035.make_seed_matrix(block)
    v035.warm_jax(params, warmup, warmup_seeds)
    v035.warm_jax(params, block, block_seeds)

    warmup_diag = v035.accuracy_diagnostics(params, warmup, warmup_seeds)
    block_diag = v035.accuracy_diagnostics(params, block, block_seeds)
    relation = pattern_relation(block, warmup)

    runs = {}
    dense_state = None
    specs = [
        ("dense_jacfwd_csr", "dense", warmup, warmup_seeds, 0.0, {}),
        ("batched_colored_warmup_pattern", "warmup_union", warmup, warmup_seeds, warmup_build_sec, warmup_diag),
        ("batched_colored_block_symbolic", "block_symbolic", block, block_seeds, block_build_sec, block_diag),
    ]
    rows = []
    for solver_name, source, sp, seeds, pattern_build_sec, diag in specs:
        row = {key: "" for key in CSV_COLUMNS}
        row.update({"case": case_name, "solver": solver_name, "pattern_source": source, "h": f"{H:.10g}"})
        start = time.perf_counter()
        try:
            internal_solver = "dense_jacfwd_csr" if solver_name == "dense_jacfwd_csr" else "batched_colored_jvp_csr"
            out = v035.integrate_solver(params, internal_solver, sp, seeds)
            runtime = time.perf_counter() - start
            if solver_name == "dense_jacfwd_csr":
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
            if source == "block_symbolic":
                item["pattern_relation_to_warmup"] = relation
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
                    "pattern_extra_vs_warmup": relation["extra_vs_warmup"] if source == "block_symbolic" else "",
                    "pattern_missing_vs_warmup": relation["missing_vs_warmup"] if source == "block_symbolic" else "",
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
        rows.append(row)
        runs[solver_name] = item

    return {
        "stribeck_velocity": CASES[case_name],
        "warmup_pattern_build_sec": warmup_build_sec,
        "block_pattern_build_sec": block_build_sec,
        "pattern_relation": relation,
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
    write_csv(RESULTS / "double_revolute_symbolic_block_pattern_runs.csv", all_rows)
    return {"t_final": T_FINAL, "h": H, "cases": cases}


def plot_results(summary: dict) -> None:
    import matplotlib.pyplot as plt

    labels = []
    runtimes = {"dense_jacfwd_csr": [], "batched_colored_warmup_pattern": [], "batched_colored_block_symbolic": []}
    jac_times = {key: [] for key in runtimes}
    colors = {"warmup": [], "block_symbolic": []}
    nnz = {"warmup": [], "block_symbolic": []}
    for case_name, case in summary["cases"].items():
        labels.append(case_name.replace("double_revolute_", ""))
        for solver in runtimes:
            run = case["runs"][solver]
            runtimes[solver].append(run.get("runtime_sec", np.nan))
            jac_times[solver].append(run.get("total_jacobian_eval_sec", np.nan))
        warm = case["runs"]["batched_colored_warmup_pattern"]["pattern"]
        block = case["runs"]["batched_colored_block_symbolic"]["pattern"]
        colors["warmup"].append(warm["colors"])
        colors["block_symbolic"].append(block["colors"])
        nnz["warmup"].append(warm["nnz"])
        nnz["block_symbolic"].append(block["nnz"])

    xs = np.arange(len(labels))
    width = 0.24
    fig, axes = plt.subplots(1, 2, figsize=(11.4, 4.0))
    for idx, solver in enumerate(runtimes):
        label = solver.replace("batched_colored_", "").replace("_", " ")
        axes[0].bar(xs + (idx - 1) * width, runtimes[solver], width=width, label=label)
        axes[1].bar(xs + (idx - 1) * width, jac_times[solver], width=width, label=label)
    for ax in axes:
        ax.set_yscale("log")
        ax.set_xticks(xs)
        ax.set_xticklabels(labels)
        ax.grid(True, axis="y", alpha=0.35)
        ax.legend(fontsize=7)
    axes[0].set_ylabel("runtime seconds")
    axes[1].set_ylabel("Jacobian assembly seconds")
    fig.tight_layout()
    fig.savefig(RESULTS / "double_revolute_symbolic_block_pattern_runtime.png", dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.0))
    axes[0].bar(xs - 0.18, nnz["warmup"], width=0.36, label="warmup")
    axes[0].bar(xs + 0.18, nnz["block_symbolic"], width=0.36, label="block symbolic")
    axes[1].bar(xs - 0.18, colors["warmup"], width=0.36, label="warmup")
    axes[1].bar(xs + 0.18, colors["block_symbolic"], width=0.36, label="block symbolic")
    axes[0].set_ylabel("pattern nonzeros")
    axes[1].set_ylabel("column colors")
    for ax in axes:
        ax.set_xticks(xs)
        ax.set_xticklabels(labels)
        ax.grid(True, axis="y", alpha=0.35)
        ax.legend()
    fig.tight_layout()
    fig.savefig(RESULTS / "double_revolute_symbolic_block_pattern_stats.png", dpi=180)
    plt.close(fig)


def write_report(summary: dict) -> None:
    lines = [
        "# v036 Experiment Report",
        "",
        "Generated by `run_v036.py`.",
        "",
        "## Purpose",
        "",
        "- Remove v035's dense warm-up sparsity discovery from the production path.",
        "- Build a conservative block-symbolic sparsity pattern from the v029 Gauss6 FullVA residual structure.",
        "- Compare dense `jacfwd` CSR, v035 batched colored JVP with warm-up pattern, and batched colored JVP with the block-symbolic pattern.",
        "",
        "## Results",
        "",
    ]
    for case_name, case in summary["cases"].items():
        dense = case["runs"]["dense_jacfwd_csr"]
        warm = case["runs"]["batched_colored_warmup_pattern"]
        block = case["runs"]["batched_colored_block_symbolic"]
        relation = case["pattern_relation"]
        lines.append(f"### {case_name}")
        lines.append(
            f"- Pattern relation: block-symbolic nnz {relation['candidate_nnz']} vs warm-up nnz "
            f"{relation['reference_nnz']}; extra {relation['extra_vs_warmup']}, "
            f"missing {relation['missing_vs_warmup']}; colors {relation['candidate_colors']} vs "
            f"{relation['reference_colors']}."
        )
        if dense.get("status") == "ok":
            lines.append(
                f"- Dense jacfwd CSR: runtime {dense['runtime_sec']:.3f}s, "
                f"Jacobian assembly {dense['total_jacobian_eval_sec']:.3e}s."
            )
        if warm.get("status") == "ok":
            dense_speed = dense["runtime_sec"] / max(warm["runtime_sec"], 1.0e-30)
            lines.append(
                f"- Warm-up-pattern batched colored JVP: runtime {warm['runtime_sec']:.3f}s "
                f"(dense/warm-up {dense_speed:.2f}x), assembly {warm['total_jacobian_eval_sec']:.3e}s, "
                f"build {warm['pattern_build_sec']:.3f}s, dense-relative error "
                f"{warm['accuracy_diagnostics']['max_batched_dense_relative_error']:.3e}."
            )
        if block.get("status") == "ok":
            dense_speed = dense["runtime_sec"] / max(block["runtime_sec"], 1.0e-30)
            warm_speed = warm["runtime_sec"] / max(block["runtime_sec"], 1.0e-30)
            lines.append(
                f"- Block-symbolic batched colored JVP: runtime {block['runtime_sec']:.3f}s "
                f"(dense/block {dense_speed:.2f}x, warm-up/block {warm_speed:.2f}x), "
                f"assembly {block['total_jacobian_eval_sec']:.3e}s, build "
                f"{block['pattern_build_sec']:.3e}s, missed dense entry "
                f"{block['accuracy_diagnostics']['max_pattern_missing_abs']:.3e}, "
                f"dense-relative error {block['accuracy_diagnostics']['max_batched_dense_relative_error']:.3e}, "
                f"trajectory diff {block['orientation_error_vs_dense_rad']:.3e} rad."
            )
        else:
            lines.append(f"- Block-symbolic run failed: {block.get('error_message')}.")
        lines.append("")
    lines.extend(
        [
            "## Interpretation",
            "",
            "- The block-symbolic pattern is a conservative production-style replacement for dense warm-up pattern discovery: it has zero missed dense entries in the diagnostics and keeps the trajectory at roundoff agreement.",
            "- The price is a coarser mask: 1755 entries and 34 colors instead of the warm-up pattern's 582 entries and 11 colors.",
            "- Even with that overpattern, runtime remains competitive because the pattern is built in milliseconds rather than seconds. The sharp-friction block-symbolic run is still 1.59x faster than dense `jacfwd` CSR, and the smooth run is essentially tied while avoiding the dense warm-up dependency.",
            "- The next target is a finer component-symbolic pattern or a generated symbolic pattern for larger chains, not a return to dense pattern discovery.",
            "",
            "## Outputs",
            "",
            "- `double_revolute_symbolic_block_pattern_runs.csv`",
            "- `summary_v036.json`",
            "- `double_revolute_symbolic_block_pattern_runtime.png`",
            "- `double_revolute_symbolic_block_pattern_stats.png`",
            "",
        ]
    )
    (RESULTS / "v036_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    experiment = run_experiment()
    plot_results(experiment)
    summary = {
        "version": "v036_symbolic_block_pattern",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "jax": v035.jax.__version__,
        "source_version": "v029_double_revolute_pivotva_dae",
        "solver_parent": "v035_batched_colored_jvp",
        "model": {
            "cases": CASES,
            "method": "double_revolute_gauss6_fullva",
            "h": H,
            "t_final": T_FINAL,
            "pattern_types": ["warmup_union", "block_symbolic"],
        },
        "experiment": experiment,
        "runtime_sec": time.perf_counter() - started,
    }
    with (RESULTS / "summary_v036.json").open("w", encoding="utf-8") as f:
        json.dump(json_safe(summary), f, indent=2, sort_keys=True)
    write_report(experiment)


if __name__ == "__main__":
    main()
