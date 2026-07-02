#!/usr/bin/env python3
"""Build compact coarse-grid error/order figures for the four-example comparison."""

from __future__ import annotations

import csv
import math
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-codex")

import matplotlib.pyplot as plt
import numpy as np


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
SUMMARY_CSV = RESULTS / "coarse_four_example_order_summary.csv"
ORDER_FIGURE = RESULTS / "coarse_velocity_order_by_example.png"
ERROR_FIGURE = RESULTS / "coarse_finest_velocity_error_by_example.png"
EXAMPLES = ("single_pendulum", "double_pendulum", "four_link", "slider_crank")
METHOD_ORDER = (
    "local_Gauss6_FullVA",
    "tfe2026_Newmark_beta",
    "tfe2026_trapezoidal",
    "tfe2026_TFE_m1",
    "tfe2026_TFE_m2",
    "tfe2026_TFE_m3_GL",
    "ra2021_rA",
    "ra2021_rp",
    "ra2021_reps",
    "hi2022_rA",
    "hi2022_rA_half",
    "vp2024_coordinate_partitioning_rA",
)
METHOD_LABEL = {
    "local_Gauss6_FullVA": "Local",
    "tfe2026_Newmark_beta": "Newmark",
    "tfe2026_trapezoidal": "Trap",
    "tfe2026_TFE_m1": "TFE1",
    "tfe2026_TFE_m2": "TFE2",
    "tfe2026_TFE_m3_GL": "TFE3",
    "ra2021_rA": "rA",
    "ra2021_rp": "rp",
    "ra2021_reps": "reps",
    "hi2022_rA": "HI-rA",
    "hi2022_rA_half": "HI-half",
    "vp2024_coordinate_partitioning_rA": "VP-rA",
}


def as_float(value: object) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return float("nan")
    return out if math.isfinite(out) else float("nan")


def read_rows() -> list[dict[str, str]]:
    with SUMMARY_CSV.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def row_lookup(rows: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, str]]:
    return {(row["example"], row["method"]): row for row in rows}


def finite_values(lookup: dict[tuple[str, str], dict[str, str]], example: str, key: str) -> list[float]:
    values: list[float] = []
    for method in METHOD_ORDER:
        row = lookup.get((example, method))
        if row is None or row.get("status") != "ok":
            values.append(float("nan"))
        else:
            values.append(as_float(row.get(key)))
    return values


def bar_colors() -> list[str]:
    return ["#1f2937" if method == "local_Gauss6_FullVA" else "#9ca3af" for method in METHOD_ORDER]


def configure_axis(ax, title: str) -> None:
    ax.set_title(title, fontsize=10)
    ax.grid(axis="y", color="#e5e7eb", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(axis="x", labelrotation=65, labelsize=7)
    ax.tick_params(axis="y", labelsize=8)


def save_velocity_order_figure(lookup: dict[tuple[str, str], dict[str, str]]) -> None:
    labels = [METHOD_LABEL[method] for method in METHOD_ORDER]
    x = np.arange(len(METHOD_ORDER))
    fig, axes = plt.subplots(2, 2, figsize=(12, 7), constrained_layout=True)
    for ax, example in zip(axes.ravel(), EXAMPLES):
        values = finite_values(lookup, example, "vel_order")
        ax.bar(x, values, color=bar_colors(), width=0.72)
        ax.axhline(6.0, color="#2563eb", linewidth=1.0, linestyle="--", label="order 6")
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.set_ylabel("observed velocity order", fontsize=8)
        configure_axis(ax, example)
    fig.suptitle("Coarse-grid observed velocity order, h = 0.1, 0.05, 0.025", fontsize=12)
    fig.savefig(ORDER_FIGURE, dpi=240)
    plt.close(fig)


def save_velocity_error_figure(lookup: dict[tuple[str, str], dict[str, str]]) -> None:
    labels = [METHOD_LABEL[method] for method in METHOD_ORDER]
    x = np.arange(len(METHOD_ORDER))
    fig, axes = plt.subplots(2, 2, figsize=(12, 7), constrained_layout=True)
    for ax, example in zip(axes.ravel(), EXAMPLES):
        values = finite_values(lookup, example, "finest_vel_error")
        values = [math.log10(value) if math.isfinite(value) and value > 0.0 else float("nan") for value in values]
        ax.bar(x, values, color=bar_colors(), width=0.72)
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.set_ylabel("log10 finest velocity error", fontsize=8)
        configure_axis(ax, example)
    fig.suptitle("Finest-step velocity error against each method reference, h = 0.025", fontsize=12)
    fig.savefig(ERROR_FIGURE, dpi=240)
    plt.close(fig)


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    rows = read_rows()
    lookup = row_lookup(rows)
    save_velocity_order_figure(lookup)
    save_velocity_error_figure(lookup)
    print("coarse_order_figures=written")
    print(f"order_figure={ORDER_FIGURE}")
    print(f"error_figure={ERROR_FIGURE}")


if __name__ == "__main__":
    main()
