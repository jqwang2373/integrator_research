from __future__ import annotations

import csv
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/mplconfig")

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "version_ledger.csv"
PLOT_PATH = ROOT / "version_progression.png"


STAGE_SCORE = {
    "baseline": 1,
    "kinematics": 2,
    "reproduction": 2,
    "mechanics": 3,
    "reduced_dae": 4,
    "absolute_dae": 5,
    "friction_dae": 6,
    "solver_backend": 6.5,
    "operator": 7,
    "quaternion_dae": 8,
    "higher_order": 9,
    "decision_boundary": 9.5,
    "adaptive": 10,
    "baseline_comparison": 10.5,
    "in_progress": 11,
    "revolute_benchmark": 11.5,
    "absolute_revolute_dae": 12,
    "lobatto_full_dae": 12.2,
    "projected_full_dae": 12.4,
    "stage_velocity_dae": 12.8,
    "stage_acceleration_dae": 13.0,
    "full_axis_dae": 13.2,
    "multi_joint_dae": 13.5,
    "solver_scaling": 13.8,
    "sparse_newton": 14.0,
    "matrix_free_krylov": 14.1,
    "lagged_sparse_newton": 14.15,
    "colored_sparse_ad": 14.25,
    "batched_colored_sparse_ad": 14.35,
    "symbolic_sparse_pattern": 14.45,
    "jvp_pruned_sparse_pattern": 14.55,
    "pattern_cache_reuse": 14.65,
    "larger_topology_scaling": 14.85,
    "generated_block_triple_pattern": 14.95,
    "cache_refresh_policy": 15.05,
    "skew_axis_lower_pair": 15.25,
    "prismatic_lower_pair": 15.35,
    "interbody_prismatic_lower_pair": 15.45,
    "row_colored_vjp_sparse_ad": 15.55,
    "four_example_validation": 15.65,
    "cylindrical_lower_pair_scaffold": 15.75,
}


def maybe_float(text: str) -> float:
    text = text.strip()
    if not text:
        return float("nan")
    try:
        return float(text)
    except ValueError:
        return float("nan")


def read_rows() -> list[dict[str, str]]:
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main() -> None:
    rows = read_rows()
    xs = np.arange(1, len(rows) + 1)
    labels = [row["version"] for row in rows]
    smooth_orders = np.array([maybe_float(row["order_smooth"]) for row in rows])
    sharp_orders = np.array([maybe_float(row["order_sharp"]) for row in rows])
    stage_scores = np.array([STAGE_SCORE.get(row["stage"], np.nan) for row in rows])

    fig, axes = plt.subplots(2, 1, figsize=(12.0, 7.5), sharex=True)

    ax = axes[0]
    ax.plot(xs, smooth_orders, marker="o", label="smooth/frictionless observed order")
    ax.plot(xs, sharp_orders, marker="s", label="sharp-friction observed order")
    ax.set_ylabel("observed order")
    ax.set_title("Lie-Group Integrator Version Progression")
    ax.grid(True, alpha=0.35)
    ax.legend()
    for x, y, label in zip(xs, smooth_orders, labels):
        if np.isfinite(y):
            ax.annotate(label, (x, y), fontsize=7, xytext=(2, 4), textcoords="offset points")

    ax = axes[1]
    ax.step(xs, stage_scores, where="mid", linewidth=2.0)
    ax.scatter(xs, stage_scores, s=28)
    ax.set_ylabel("capability score")
    ax.set_xlabel("version")
    ax.grid(True, alpha=0.35)
    ax.set_yticks(sorted(set(STAGE_SCORE.values())))
    ax.set_xticks(xs)
    ax.set_xticklabels(labels, rotation=45, ha="right")
    for x, y, row in zip(xs, stage_scores, rows):
        ax.annotate(row["stage"], (x, y), fontsize=7, xytext=(2, 4), textcoords="offset points")

    fig.tight_layout()
    fig.savefig(PLOT_PATH, dpi=180)


if __name__ == "__main__":
    main()
