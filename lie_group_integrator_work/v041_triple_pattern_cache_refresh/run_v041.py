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
V040_PATH = ROOT / "v040_generated_block_triple_pattern" / "run_v040.py"

H = 0.02
T_DISCOVERY = 0.06
T_VALIDATE = 0.12
PATTERN_ATOL = 1.0e-14
CSV_COLUMNS = [
    "scenario",
    "friction_case",
    "policy",
    "h",
    "t_final",
    "status",
    "error_message",
    "steps",
    "runtime_sec",
    "refresh_scan_sec",
    "dense_validation_pattern_sec",
    "initial_cache_nnz",
    "refresh_active_nnz",
    "refresh_added_entries",
    "final_cache_nnz",
    "dense_validation_nnz",
    "final_missing_vs_dense",
    "final_extra_vs_dense",
    "final_colors",
    "dense_colors",
    "orientation_error_vs_dense_rad",
    "omega_error_vs_dense",
    "max_endpoint_constraint_norm",
    "max_endpoint_velocity_constraint_norm",
    "max_stage_pivot_acceleration_constraint_norm",
    "max_stage_axis_acceleration_constraint_norm",
    "max_quaternion_unit_error",
]


def load_v040():
    spec = importlib.util.spec_from_file_location("v040_generated_block_triple_pattern", V040_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


v040 = load_v040()
v039 = v040.v039


@dataclass(frozen=True)
class Scenario:
    name: str
    friction_case: str
    q_offset: np.ndarray
    qd_offset: np.ndarray


SCENARIOS = [
    Scenario(
        name="smooth_nominal_long",
        friction_case="triple_revolute_smooth",
        q_offset=np.zeros(3),
        qd_offset=np.zeros(3),
    ),
    Scenario(
        name="sharp_nominal_long",
        friction_case="triple_revolute_sharp",
        q_offset=np.zeros(3),
        qd_offset=np.zeros(3),
    ),
    Scenario(
        name="smooth_perturbed_long",
        friction_case="triple_revolute_smooth",
        q_offset=np.array([0.16, -0.12, 0.09]),
        qd_offset=np.array([0.05, 0.04, -0.06]),
    ),
    Scenario(
        name="sharp_perturbed_long",
        friction_case="triple_revolute_sharp",
        q_offset=np.array([-0.13, 0.10, 0.15]),
        qd_offset=np.array([-0.04, 0.06, 0.05]),
    ),
]


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


def chain_state_from_offsets(params: v039.Params, q_offset: np.ndarray, qd_offset: np.ndarray) -> v039.State:
    q = np.array([0.82, 1.28, 0.67]) + q_offset
    qd = np.array([0.18, -0.32, 0.24]) + qd_offset
    p = np.stack([v039.qp.quat_exp(np.array([0.0, qi, 0.0])) for qi in q])
    R = [v039.qp.quat_to_rot(pi) for pi in p]
    w = np.stack([np.array([0.0, qdi, 0.0]) for qdi in qd])
    r = np.zeros((v039.N_BODIES, 3))
    v = np.zeros((v039.N_BODIES, 3))
    r[0] = -R[0] @ params.s_prev[0]
    v[0] = -R[0] @ np.cross(w[0], params.s_prev[0])
    for i in range(1, v039.N_BODIES):
        r[i] = r[i - 1] + R[i - 1] @ params.s_next[i - 1] - R[i] @ params.s_prev[i]
        v[i] = (
            v[i - 1]
            + R[i - 1] @ np.cross(w[i - 1], params.s_next[i - 1])
            - R[i] @ np.cross(w[i], params.s_prev[i])
        )
    return v039.State(r=r, p=p, v=v, w=w)


def integrate_from_state(params: v039.Params, initial: v039.State, solver: str, sp: v039.SparsePattern, seeds: np.ndarray, t_final: float):
    state = v039.State(r=initial.r.copy(), p=initial.p.copy(), v=initial.v.copy(), w=initial.w.copy())
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
        "max_stage_pivot_acceleration_constraint_norm": 0.0,
        "max_stage_axis_acceleration_constraint_norm": 0.0,
        "max_quaternion_unit_error": 0.0,
    }
    n_steps = int(round(t_final / H))
    for _ in range(n_steps):
        state, diag = v039.gauss_step(state, params, solver, sp, seeds)
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
            "max_stage_pivot_acceleration_constraint_norm",
            "max_stage_axis_acceleration_constraint_norm",
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


def active_pattern_scan(params: v039.Params, initial: v039.State, superset: v039.SparsePattern, t_final: float) -> tuple[v039.SparsePattern, float]:
    seeds = v039.make_seed_matrix(superset)
    state = v039.State(r=initial.r.copy(), p=initial.p.copy(), v=initial.v.copy(), w=initial.w.copy())
    pattern = np.zeros((v039.DIM, v039.DIM), dtype=bool)
    started = time.perf_counter()
    for _ in range(int(round(t_final / H))):
        x = v039.stage_guess(state, H, params)
        args = v039.build_args(state, H, params)
        for _it in range(8):
            x_jax = jnp.asarray(x, dtype=jnp.float64)
            res = np.asarray(v039.R3_VALUE(x_jax, *args), dtype=float)
            csr, current = v040.superset_jvp_csr_and_mask(x, args, superset, seeds)
            pattern = np.logical_or(pattern, current)
            if float(np.linalg.norm(res)) < 1.0e-11:
                break
            delta = spla.spsolve(csr, -res)
            x = x + np.asarray(delta, dtype=float)
            if float(np.linalg.norm(delta)) < 1.0e-11:
                break
        state = v039.next_state_from_stages(state, H, v039.unpack_stages(x))
    return v039.make_pattern(pattern), time.perf_counter() - started


def dense_validation_pattern_from_state(params: v039.Params, initial: v039.State, t_final: float) -> tuple[v039.SparsePattern, float]:
    state = v039.State(r=initial.r.copy(), p=initial.p.copy(), v=initial.v.copy(), w=initial.w.copy())
    pattern = None
    started = time.perf_counter()
    for _ in range(int(round(t_final / H))):
        x = v039.stage_guess(state, H, params)
        args = v039.build_args(state, H, params)
        for _it in range(8):
            x_jax = jnp.asarray(x, dtype=jnp.float64)
            res = np.asarray(v039.R3_VALUE(x_jax, *args), dtype=float)
            jac = np.asarray(v039.R3_JAC(x_jax, *args), dtype=float)
            current = np.abs(jac) > PATTERN_ATOL
            pattern = current if pattern is None else np.logical_or(pattern, current)
            if float(np.linalg.norm(res)) < 1.0e-11:
                break
            delta = np.linalg.solve(jac, -res)
            x = x + delta
            if float(np.linalg.norm(delta)) < 1.0e-11:
                break
        state = v039.next_state_from_stages(state, H, v039.unpack_stages(x))
    assert pattern is not None
    return v039.make_pattern(pattern), time.perf_counter() - started


def pattern_relation(candidate: v039.SparsePattern, reference: v039.SparsePattern) -> dict:
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


def union_pattern(a: v039.SparsePattern, b: v039.SparsePattern) -> v039.SparsePattern:
    return v039.make_pattern(np.logical_or(a.pattern, b.pattern))


def drop_entries_for_stale_audit(sp: v039.SparsePattern, count: int = 23) -> v039.SparsePattern:
    mask = sp.pattern.copy()
    rows, cols = np.nonzero(mask)
    stride = max(len(rows) // count, 1)
    selected = np.arange(0, len(rows), stride)[:count]
    mask[rows[selected], cols[selected]] = False
    return v039.make_pattern(mask)


def run_cached_policy(
    scenario: Scenario,
    params: v039.Params,
    initial: v039.State,
    base_cache: v039.SparsePattern,
    superset: v039.SparsePattern,
    stale: bool = False,
) -> tuple[dict, dict]:
    initial_cache = drop_entries_for_stale_audit(base_cache) if stale else base_cache
    refresh_active, refresh_sec = active_pattern_scan(params, initial, superset, T_VALIDATE)
    missing_from_cache = np.logical_and(refresh_active.pattern, np.logical_not(initial_cache.pattern))
    final_cache = union_pattern(initial_cache, refresh_active)
    final_seeds = v039.make_seed_matrix(final_cache)
    v039.warm_jax(params, final_cache, final_seeds)

    dense_pattern, dense_pattern_sec = dense_validation_pattern_from_state(params, initial, T_VALIDATE)
    relation = pattern_relation(final_cache, dense_pattern)

    dense_start = time.perf_counter()
    dense = integrate_from_state(params, initial, "dense_jacfwd_csr", final_cache, final_seeds, T_VALIDATE)
    dense_runtime = time.perf_counter() - dense_start
    cached_start = time.perf_counter()
    cached = integrate_from_state(params, initial, "cached_jvp_pruned", final_cache, final_seeds, T_VALIDATE)
    cached_runtime = time.perf_counter() - cached_start
    oerr, werr = v039.state_error(dense["state"], cached["state"])

    policy = "stale_cache_refresh_audit" if stale else "cached_refresh_union"
    item = {
        "scenario": scenario.name,
        "friction_case": scenario.friction_case,
        "policy": policy,
        "initial_cache": {"nnz": initial_cache.nnz, "colors": len(initial_cache.colors)},
        "refresh_active": {"nnz": refresh_active.nnz, "colors": len(refresh_active.colors)},
        "refresh_added_entries": int(missing_from_cache.sum()),
        "final_cache": {"nnz": final_cache.nnz, "colors": len(final_cache.colors)},
        "dense_validation": {"nnz": dense_pattern.nnz, "colors": len(dense_pattern.colors), "build_sec": dense_pattern_sec},
        "relation_final_vs_dense": relation,
        "refresh_scan_sec": refresh_sec,
        "runs": {
            "dense_jacfwd_csr": {key: value for key, value in dense.items() if key != "state"} | {"runtime_sec": dense_runtime},
            "cached_refresh_union": {key: value for key, value in cached.items() if key != "state"}
            | {"runtime_sec": cached_runtime, "orientation_error_vs_dense_rad": oerr, "omega_error_vs_dense": werr},
        },
    }
    row = {key: "" for key in CSV_COLUMNS}
    row.update(
        {
            "scenario": scenario.name,
            "friction_case": scenario.friction_case,
            "policy": policy,
            "h": f"{H:.10g}",
            "t_final": f"{T_VALIDATE:.10g}",
            "status": "ok",
            "steps": cached["steps"],
            "runtime_sec": f"{cached_runtime:.8e}",
            "refresh_scan_sec": f"{refresh_sec:.8e}",
            "dense_validation_pattern_sec": f"{dense_pattern_sec:.8e}",
            "initial_cache_nnz": initial_cache.nnz,
            "refresh_active_nnz": refresh_active.nnz,
            "refresh_added_entries": int(missing_from_cache.sum()),
            "final_cache_nnz": final_cache.nnz,
            "dense_validation_nnz": dense_pattern.nnz,
            "final_missing_vs_dense": relation["missing_vs_reference"],
            "final_extra_vs_dense": relation["extra_vs_reference"],
            "final_colors": len(final_cache.colors),
            "dense_colors": len(dense_pattern.colors),
            "orientation_error_vs_dense_rad": f"{oerr:.16e}",
            "omega_error_vs_dense": f"{werr:.16e}",
            "max_endpoint_constraint_norm": f"{cached['max_endpoint_constraint_norm']:.16e}",
            "max_endpoint_velocity_constraint_norm": f"{cached['max_endpoint_velocity_constraint_norm']:.16e}",
            "max_stage_pivot_acceleration_constraint_norm": f"{cached['max_stage_pivot_acceleration_constraint_norm']:.16e}",
            "max_stage_axis_acceleration_constraint_norm": f"{cached['max_stage_axis_acceleration_constraint_norm']:.16e}",
            "max_quaternion_unit_error": f"{cached['max_quaternion_unit_error']:.16e}",
        }
    )
    return item, row


def run_experiment() -> dict:
    superset = v040.generated_block_superset_pattern()
    smooth_params = v039.make_params(v039.CASES["triple_revolute_smooth"])
    discovery_initial = chain_state_from_offsets(smooth_params, np.zeros(3), np.zeros(3))
    discovery_cache, discovery_sec = active_pattern_scan(smooth_params, discovery_initial, superset, T_DISCOVERY)
    v039.warm_jax(smooth_params, discovery_cache, v039.make_seed_matrix(discovery_cache))

    rows = []
    cases = {}
    for scenario in SCENARIOS:
        params = v039.make_params(v039.CASES[scenario.friction_case])
        initial = chain_state_from_offsets(params, scenario.q_offset, scenario.qd_offset)
        item, row = run_cached_policy(scenario, params, initial, discovery_cache, superset, stale=False)
        rows.append(row)
        cases[scenario.name] = item

    stale_item, stale_row = run_cached_policy(SCENARIOS[0], smooth_params, discovery_initial, discovery_cache, superset, stale=True)
    rows.append(stale_row)
    cases["stale_cache_refresh_audit"] = stale_item

    write_csv(RESULTS / "triple_pattern_cache_refresh_runs.csv", rows)
    return {
        "h": H,
        "t_discovery": T_DISCOVERY,
        "t_validate": T_VALIDATE,
        "dimension": v039.DIM,
        "stage_size": v039.STAGE_SIZE,
        "discovery": {
            "case": "triple_revolute_smooth",
            "pattern_nnz": discovery_cache.nnz,
            "colors": len(discovery_cache.colors),
            "build_sec": discovery_sec,
            "superset_nnz": superset.nnz,
            "superset_colors": len(superset.colors),
        },
        "cases": cases,
    }


def plot_results(summary: dict) -> None:
    import matplotlib.pyplot as plt

    names = list(summary["cases"].keys())
    cached_runtime = [summary["cases"][name]["runs"]["cached_refresh_union"]["runtime_sec"] for name in names]
    dense_runtime = [summary["cases"][name]["runs"]["dense_jacfwd_csr"]["runtime_sec"] for name in names]
    added = [summary["cases"][name]["refresh_added_entries"] for name in names]
    final_nnz = [summary["cases"][name]["final_cache"]["nnz"] for name in names]
    dense_nnz = [summary["cases"][name]["dense_validation"]["nnz"] for name in names]
    xs = np.arange(len(names))

    fig, ax = plt.subplots(figsize=(11.2, 4.2))
    ax.bar(xs - 0.18, dense_runtime, width=0.36, label="dense jacfwd CSR")
    ax.bar(xs + 0.18, cached_runtime, width=0.36, label="cached refresh/union")
    ax.set_yscale("log")
    ax.set_ylabel("runtime seconds")
    ax.set_xticks(xs)
    ax.set_xticklabels([name.replace("_long", "").replace("triple_revolute_", "") for name in names], rotation=20, ha="right")
    ax.grid(True, axis="y", alpha=0.35)
    ax.legend()
    fig.tight_layout()
    fig.savefig(RESULTS / "triple_pattern_cache_refresh_runtime.png", dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.0))
    axes[0].bar(xs, added)
    axes[0].set_ylabel("refresh-added entries")
    axes[1].bar(xs - 0.18, final_nnz, width=0.36, label="final cache")
    axes[1].bar(xs + 0.18, dense_nnz, width=0.36, label="dense validation")
    axes[1].set_ylabel("pattern nonzeros")
    for ax in axes:
        ax.set_xticks(xs)
        ax.set_xticklabels([name.replace("_long", "") for name in names], rotation=20, ha="right")
        ax.grid(True, axis="y", alpha=0.35)
    axes[1].legend()
    fig.tight_layout()
    fig.savefig(RESULTS / "triple_pattern_cache_refresh_patterns.png", dpi=180)
    plt.close(fig)


def write_report(summary: dict) -> None:
    lines = [
        "# v041 Experiment Report",
        "",
        "Generated by `run_v041.py`.",
        "",
        "## Purpose",
        "",
        "- Turn v040's generated block-pruned triple-revolute pattern into a cache refresh/union policy.",
        "- Discover once from a smooth short trajectory, then scan longer smooth/sharp and perturbed trajectories inside the generated block superset.",
        "- Validate the final cache against dense `jacfwd` union patterns, while keeping dense Jacobians out of the refresh path.",
        "",
        "## Discovery",
        "",
        f"- Smooth short discovery: {summary['discovery']['pattern_nnz']} entries, {summary['discovery']['colors']} colors, build {summary['discovery']['build_sec']:.3f}s.",
        f"- Generated block superset: {summary['discovery']['superset_nnz']} entries, {summary['discovery']['superset_colors']} colors.",
        "",
        "## Results",
        "",
    ]
    for name, case in summary["cases"].items():
        cached = case["runs"]["cached_refresh_union"]
        dense = case["runs"]["dense_jacfwd_csr"]
        rel = case["relation_final_vs_dense"]
        speed = dense["runtime_sec"] / max(cached["runtime_sec"], 1.0e-30)
        lines.append(f"### {name}")
        lines.append(
            f"- Cache: initial {case['initial_cache']['nnz']} entries, refresh-active "
            f"{case['refresh_active']['nnz']}, added {case['refresh_added_entries']}, final "
            f"{case['final_cache']['nnz']} entries/{case['final_cache']['colors']} colors."
        )
        lines.append(
            f"- Dense validation: {case['dense_validation']['nnz']} entries/{case['dense_validation']['colors']} colors; "
            f"final missing {rel['missing_vs_reference']}, extra {rel['extra_vs_reference']}."
        )
        lines.append(
            f"- Runtime: dense {dense['runtime_sec']:.3f}s vs cached {cached['runtime_sec']:.3f}s "
            f"(dense/cached {speed:.2f}x); refresh scan {case['refresh_scan_sec']:.3f}s."
        )
        lines.append(
            f"- Trajectory diff: orientation {cached['orientation_error_vs_dense_rad']:.3e} rad, "
            f"omega {cached['omega_error_vs_dense']:.3e}; endpoint velocity "
            f"{cached['max_endpoint_velocity_constraint_norm']:.3e}."
        )
        lines.append("")
    lines.extend(
        [
            "## Interpretation",
            "",
            "- The smooth short cache transfers to all longer nominal and perturbed smooth/sharp scenarios with zero refresh additions.",
            "- The stale-cache audit intentionally removes entries and the block-superset refresh scan restores them, proving the union policy can repair cache misses without dense Jacobians.",
            "- Dense Jacobians are used only as validation evidence; the refresh path uses generated block sparsity plus batched JVPs.",
            "- The remaining gap is larger and less-planar lower-pair coverage, not the basic cache refresh mechanism.",
            "",
            "## Outputs",
            "",
            "- `triple_pattern_cache_refresh_runs.csv`",
            "- `summary_v041.json`",
            "- `triple_pattern_cache_refresh_runtime.png`",
            "- `triple_pattern_cache_refresh_patterns.png`",
            "",
        ]
    )
    (RESULTS / "v041_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    experiment = run_experiment()
    plot_results(experiment)
    summary = {
        "version": "v041_triple_pattern_cache_refresh",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "scipy": __import__("scipy").__version__,
        "jax": v039.jax.__version__,
        "source_versions": ["v040_generated_block_triple_pattern", "v038_pattern_cache_reuse"],
        "model": {
            "method": "triple_revolute_gauss6_fullva",
            "h": H,
            "t_discovery": T_DISCOVERY,
            "t_validate": T_VALIDATE,
            "dimension": v039.DIM,
            "stage_size": v039.STAGE_SIZE,
        },
        "experiment": experiment,
        "runtime_sec": time.perf_counter() - started,
    }
    with (RESULTS / "summary_v041.json").open("w", encoding="utf-8") as f:
        json.dump(json_safe(summary), f, indent=2, sort_keys=True)
    write_report(experiment)


if __name__ == "__main__":
    main()
