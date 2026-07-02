#!/usr/bin/env python3
"""Build a T=10 algorithm-literal TFE work/precision audit.

This is a read-only derivative of ``TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE``.
It plots precision against Newton-iteration work for the fixed-h Algorithm 1
endpoint policy.  It does not resolve source-policy runner equivalence or the
source paper's exact-T error-sampling convention.
"""

from __future__ import annotations

import csv
import json
import math
import os
from pathlib import Path
from typing import Any

import numpy as np


PAPER = Path(__file__).resolve().parent
os.environ.setdefault("MPLCONFIGDIR", str(Path("/tmp") / "jingquan_mplconfig"))
SOURCE_JSON = PAPER / "TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE.json"
SOURCE_CSV = PAPER / "TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE.csv"
OUT_JSON = PAPER / "TFE_ALGORITHM_LITERAL_WORK_PRECISION_AUDIT.json"
OUT_MD = PAPER / "TFE_ALGORITHM_LITERAL_WORK_PRECISION_AUDIT.md"
OUT_CSV = PAPER / "TFE_ALGORITHM_LITERAL_WORK_PRECISION_AUDIT.csv"
OUT_FIG = PAPER / "figures" / "tfe_algorithm_literal_work_precision.png"


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def as_float(value: object) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return float("nan")
    return out if math.isfinite(out) else float("nan")


def fit_order(rows: list[dict[str, Any]], key: str) -> float:
    clean = sorted(
        [
            (as_float(row.get("h")), as_float(row.get(key)))
            for row in rows
            if as_float(row.get("h")) > 0.0 and as_float(row.get(key)) > 0.0
        ],
        reverse=True,
    )
    if len(clean) < 2:
        return float("nan")
    slope, _ = np.polyfit(np.log([h for h, _ in clean]), np.log([e for _, e in clean]), 1)
    return float(slope)


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty {path.name}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_figure(rows: list[dict[str, Any]]) -> None:
    import matplotlib.pyplot as plt

    OUT_FIG.parent.mkdir(parents=True, exist_ok=True)
    labels = {
        "tfe2026_Newmark_beta": "Newmark",
        "tfe2026_TFE_m1": "TFE m=1",
        "tfe2026_TFE_m2": "TFE m=2",
        "tfe2026_trapezoidal": "trap.",
    }
    markers = {
        "tfe2026_Newmark_beta": "o",
        "tfe2026_TFE_m1": "^",
        "tfe2026_TFE_m2": "D",
        "tfe2026_trapezoidal": "s",
    }
    colors = {
        "tfe2026_Newmark_beta": "#4c78a8",
        "tfe2026_TFE_m1": "#54a24b",
        "tfe2026_TFE_m2": "#b279a2",
        "tfe2026_trapezoidal": "#f58518",
    }
    methods = list(labels)
    rc = {
        "font.size": 8,
        "axes.titlesize": 9,
        "axes.labelsize": 8,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
        "legend.fontsize": 7,
        "figure.titlesize": 10,
    }
    with plt.rc_context(rc):
        fig, axes = plt.subplots(1, 2, figsize=(6.9, 2.8), constrained_layout=True)
        for method in methods:
            group = sorted(
                [row for row in rows if row["paper_method"] == method],
                key=lambda row: as_float(row["work_units_newton_iterations"]),
            )
            work = [as_float(row["work_units_newton_iterations"]) for row in group]
            velocity = [as_float(row["velocity_error_v"]) for row in group]
            coordinate = [as_float(row["coordinate_error_q"]) for row in group]
            hs = [as_float(row["h"]) for row in group]
            axes[0].plot(
                work,
                velocity,
                marker=markers[method],
                color=colors[method],
                linewidth=1.25,
                markersize=4.4,
                label=labels[method],
            )
            axes[1].plot(
                work,
                coordinate,
                marker=markers[method],
                color=colors[method],
                linewidth=1.25,
                markersize=4.4,
                label=labels[method],
            )
            for x, y, h in zip(work, velocity, hs):
                if method in {"tfe2026_TFE_m1", "tfe2026_TFE_m2"}:
                    axes[0].annotate(f"{h:g}", (x, y), textcoords="offset points", xytext=(3, 2), fontsize=6)
        axes[0].set_title("velocity precision")
        axes[1].set_title("coordinate precision")
        for ax in axes:
            ax.set_xscale("log")
            ax.set_yscale("log")
            ax.set_xlabel("Newton iterations")
            ax.grid(True, which="both", alpha=0.25, linewidth=0.45)
        axes[0].set_ylabel("error")
        axes[1].set_ylabel("error")
        handles, labels_out = axes[0].get_legend_handles_labels()
        fig.legend(handles, labels_out, loc="lower center", bbox_to_anchor=(0.5, -0.06), ncols=4, frameon=False)
        fig.savefig(OUT_FIG, dpi=260, bbox_inches="tight", pad_inches=0.04)
    plt.close("all")


def main() -> None:
    source = read_json(SOURCE_JSON)
    source_rows = read_csv(SOURCE_CSV)
    if source.get("status") != "algorithm_literal_full_T10_probe_available_source_policy_open":
        raise ValueError("endpoint probe status is not the expected open source-policy state")

    raw_rows: list[dict[str, Any]] = []
    for row in source_rows:
        raw_rows.append(
            {
                "policy": "algorithm_literal_T10_newton_work_precision_not_source_policy",
                "paper_method": row["paper_method"],
                "source_method": row["source_method"],
                "expected_order": int(row["expected_order"]),
                "h": as_float(row["h"]),
                "steps": int(float(row["steps"])),
                "terminal_time": as_float(row["terminal_time"]),
                "terminal_overshoot": as_float(row["terminal_overshoot"]),
                "coordinate_error_q": as_float(row["coordinate_error_q"]),
                "velocity_error_v": as_float(row["velocity_error_v"]),
                "frobenius_error_norm_eta": as_float(row["frobenius_error_norm_eta"]),
                "work_units_newton_iterations": as_float(row["total_newton_iterations"]),
                "max_residual_norm": as_float(row["max_residual_norm"]),
                "source_policy_row_completed": "false",
                "source_policy_method_runner_equivalent": "false",
                "source_policy_exact_T_error_sampling_equivalent": "false",
                "external_superiority_claim_allowed": "false",
                "accepted_use": "algorithm_literal_T10_newton_work_precision_not_source_policy",
            }
        )

    write_figure(raw_rows)
    write_csv(OUT_CSV, raw_rows)

    summary_rows: list[dict[str, Any]] = []
    for method_row in source.get("method_rows", []):
        paper_method = str(method_row["paper_method"])
        group = [row for row in raw_rows if row["paper_method"] == paper_method]
        finite = [
            value
            for row in group
            for value in [
                as_float(row["coordinate_error_q"]),
                as_float(row["velocity_error_v"]),
                as_float(row["work_units_newton_iterations"]),
                as_float(row["max_residual_norm"]),
            ]
        ]
        finest = min(group, key=lambda row: as_float(row["h"]))
        summary_rows.append(
            {
                "paper_method": paper_method,
                "source_method": method_row["source_method"],
                "expected_order": method_row["expected_order"],
                "row_count": len(group),
                "finite_row_count": sum(1 for value in finite if math.isfinite(value)),
                "terminal_overrun_rows": sum(1 for row in group if as_float(row["terminal_overshoot"]) > 1.0e-12),
                "velocity_observed_order": fit_order(group, "velocity_error_v"),
                "coordinate_observed_order": fit_order(group, "coordinate_error_q"),
                "finest_h": as_float(finest["h"]),
                "finest_velocity_error_v": as_float(finest["velocity_error_v"]),
                "finest_coordinate_error_q": as_float(finest["coordinate_error_q"]),
                "work_units_newton_iterations_sum": sum(as_float(row["work_units_newton_iterations"]) for row in group),
                "max_residual_norm": max(as_float(row["max_residual_norm"]) for row in group),
                "source_policy_row_completed": False,
                "source_policy_method_runner_equivalent": False,
            }
        )

    output = {
        "schema": "tfe-algorithm-literal-work-precision-audit-v1",
        "status": "algorithm_literal_T10_newton_work_precision_available_source_policy_open",
        "source_probe": "TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE.json",
        "source_probe_csv": "TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE.csv",
        "t_final": source.get("t_final"),
        "reference_h": source.get("reference_h"),
        "comparison_h": source.get("comparison_h"),
        "algorithm_literal_endpoint_policy": source.get("algorithm_literal_endpoint_policy"),
        "work_proxy": "total_newton_iterations",
        "runtime_proxy_available": False,
        "method_count": source.get("method_count"),
        "raw_row_count": len(raw_rows),
        "summary_row_count": len(summary_rows),
        "terminal_overrun_rows": sum(1 for row in raw_rows if as_float(row["terminal_overshoot"]) > 1.0e-12),
        "source_policy_rows_completed": 0,
        "source_policy_method_runner_equivalent": False,
        "source_policy_exact_T_error_sampling_equivalent": False,
        "external_superiority_claim_allowed": False,
        "work_precision_figure_available": OUT_FIG.exists() and OUT_FIG.stat().st_size > 0,
        "figure": "figures/tfe_algorithm_literal_work_precision.png",
        "csv": "TFE_ALGORITHM_LITERAL_WORK_PRECISION_AUDIT.csv",
        "summary_rows": summary_rows,
        "decision": {
            "b4_progress": True,
            "b4_closure": False,
            "reason": (
                "The T=10 Algorithm-1-literal endpoint runner now has Newton-iteration work/precision "
                "curves, but exact-T sampling and source-equivalent method/DAE runners remain open."
            ),
        },
    }
    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# TFE Algorithm-Literal Work/Precision Audit",
        "",
        f"Status: **{output['status']}**.",
        "",
        f"- Work proxy: `{output['work_proxy']}`.",
        f"- Runtime proxy available: `{output['runtime_proxy_available']}`.",
        f"- Methods/raw rows/summary rows: `{output['method_count']}/{output['raw_row_count']}/{output['summary_row_count']}`.",
        f"- Terminal-overrun rows: `{output['terminal_overrun_rows']}`.",
        f"- Figure available: `{output['work_precision_figure_available']}`.",
        f"- Source-policy rows completed: `{output['source_policy_rows_completed']}`.",
        f"- Source-policy method runner equivalent: `{output['source_policy_method_runner_equivalent']}`.",
        f"- Exact-T error sampling equivalent: `{output['source_policy_exact_T_error_sampling_equivalent']}`.",
        f"- External superiority claim allowed: `{output['external_superiority_claim_allowed']}`.",
        "",
        "## Method Summary",
        "",
        "| method | expected | rows | terminal overruns | velocity order | finest velocity error | Newton iterations | max residual |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary_rows:
        lines.append(
            f"| `{row['paper_method']}` | `{row['expected_order']}` | `{row['row_count']}` | "
            f"`{row['terminal_overrun_rows']}` | `{row['velocity_observed_order']:.6g}` | "
            f"`{row['finest_velocity_error_v']:.6e}` | `{row['work_units_newton_iterations_sum']:.0f}` | "
            f"`{row['max_residual_norm']:.3e}` |"
        )
    lines.extend(
        [
            "",
            "This is a Newton-iteration work/precision diagnostic for the source-text-supported",
            "fixed-h Algorithm 1 endpoint policy. It is not a source-policy reproduction and",
            "does not close B4 because exact-T error sampling and source-equivalent DAE/method",
            "runner policy remain open.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("tfe_algorithm_literal_work_precision_audit=written")
    print(f"methods={output['method_count']}")
    print(f"raw_rows={output['raw_row_count']}")
    print(f"summary_rows={output['summary_row_count']}")
    print(f"terminal_overrun_rows={output['terminal_overrun_rows']}")
    print("source_policy_rows_completed=0")


if __name__ == "__main__":
    main()
