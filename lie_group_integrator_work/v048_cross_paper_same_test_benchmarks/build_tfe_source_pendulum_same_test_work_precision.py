#!/usr/bin/env python3
"""Build same-test work/precision rows for the TFE source pendulum scaffold."""

from __future__ import annotations

import csv
import json
import math
import os
from pathlib import Path

import numpy as np

import tfe_source_pendulum_model as model


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
os.environ.setdefault("MPLCONFIGDIR", str(Path("/tmp") / "jingquan_mplconfig"))
POLICY = "tfe_source_pendulum_same_test_candidate_work_precision"
RAW_CSV = RESULTS / "tfe_source_pendulum_same_test_work_precision_rows.csv"
SUMMARY_CSV = RESULTS / "tfe_source_pendulum_same_test_work_precision_summary.csv"
SUMMARY_JSON = RESULTS / "tfe_source_pendulum_same_test_work_precision.json"
SUMMARY_MD = RESULTS / "tfe_source_pendulum_same_test_work_precision.md"
FIGURE = RESULTS / "tfe_source_pendulum_same_test_work_precision.png"
EXPECTED_METHODS = (
    "Newmark_beta",
    "trapezoidal",
    "TFE_m1",
    "TFE_m2",
    "TFE_m3_GL",
    "Gauss6_FullVA",
)


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty {path.name}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def as_float(value: object) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return float("nan")
    return out if math.isfinite(out) else float("nan")


def fmt(value: object) -> str:
    number = as_float(value)
    return "nan" if not math.isfinite(number) else f"{number:.16e}"


def fit_order(rows: list[dict[str, object]], key: str) -> float:
    clean = sorted(
        [(as_float(row.get("h")), as_float(row.get(key))) for row in rows if row.get("status") == "ok"],
        reverse=True,
    )
    clean = [(h, e) for h, e in clean if h > 0.0 and e > 0.0 and math.isfinite(e)]
    if len(clean) < 2:
        return float("nan")
    slope, _ = np.polyfit(np.log([h for h, _ in clean]), np.log([e for _, e in clean]), 1)
    return float(slope)


def order_floor(values: object) -> float:
    if not isinstance(values, list) or not values:
        return float("nan")
    clean = [as_float(value) for value in values]
    clean = [value for value in clean if math.isfinite(value)]
    return min(clean) if clean else float("nan")


def flatten_rows(smoke: dict[str, object]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for method_row in smoke["rows"]:
        method_metrics = method_row["metrics"]
        for metric in method_metrics:
            steps = as_float(metric.get("steps"))
            newton = as_float(metric.get("total_newton_iterations"))
            residual = as_float(metric.get("max_residual_norm"))
            coord_error = as_float(metric.get("coordinate_error_q"))
            vel_error = as_float(metric.get("velocity_error_v"))
            frob_error = as_float(metric.get("frobenius_error_norm_eta"))
            runtime = as_float(metric.get("runtime_sec"))
            status = "ok"
            if not all(math.isfinite(value) and value >= 0.0 for value in [coord_error, vel_error, frob_error, residual, runtime]):
                status = "nonfinite"
            row = {
                "policy": POLICY,
                "source_suite": "tfe2026_source_pendulum_candidate_scaffold",
                "case_id": method_row["case_id"],
                "example": method_row["example"],
                "method": method_row["method_label"],
                "source_method": method_row["source_method"],
                "paper_method": method_row["paper_method"],
                "expected_order": method_row["expected_order"],
                "row_type": "same_test_candidate_work_precision_raw_row",
                "frictional": str(method_row["frictional"]).lower(),
                "t_end": fmt(smoke["t_final"]),
                "reference_method": smoke["reference_method"],
                "reference_h": fmt(smoke["reference_h"]),
                "h": fmt(metric["h"]),
                "status": status,
                "steps": int(steps),
                "coordinate_error_q": fmt(coord_error),
                "velocity_error_v": fmt(vel_error),
                "frobenius_error_norm_eta": fmt(frob_error),
                "runtime_sec": fmt(runtime),
                "max_newton_residual_norm": fmt(residual),
                "avg_newton_iterations_per_step": fmt(newton / max(1.0, steps)),
                "total_newton_iterations": fmt(newton),
                "work_units_newton_iterations": fmt(metric.get("work_units_newton_iterations")),
                "source_policy_method_runner_equivalent": "false",
                "fullva_dae_source_policy_equivalent": "false",
                "source_policy_row_completed": "false",
                "external_superiority_claim_allowed": "false",
                "accepted_use": method_row["accepted_use"],
                "notes": (
                    "Shared frictionless source-pendulum grid and RK4 reference; candidate work/precision "
                    "diagnostic only, not original TFE source-policy reproduction."
                ),
            }
            rows.append(row)
    return rows


def summarize_rows(smoke: dict[str, object], rows: list[dict[str, object]]) -> tuple[list[dict[str, object]], dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault(str(row["source_method"]), []).append(row)

    source_to_nested = {str(row["source_method"]): row for row in smoke["rows"]}
    summary_rows: list[dict[str, object]] = []
    for source_method in EXPECTED_METHODS:
        group = grouped[source_method]
        nested = source_to_nested[source_method]
        ok = [row for row in group if row.get("status") == "ok"]
        sorted_ok = sorted(ok, key=lambda row: as_float(row.get("h")))
        finest = sorted_ok[0] if sorted_ok else {}
        runtime_values = [as_float(row.get("runtime_sec")) for row in ok]
        iteration_values = [as_float(row.get("total_newton_iterations")) for row in ok]
        summary_rows.append(
            {
                "policy": f"{POLICY}_summary",
                "source_suite": "tfe2026_source_pendulum_candidate_scaffold",
                "case_id": f"{source_method}_same_test_work_precision_summary",
                "example": smoke["example"],
                "method": nested["method_label"],
                "source_method": source_method,
                "paper_method": nested["paper_method"],
                "expected_order": nested["expected_order"],
                "row_count": len(group),
                "ok_row_count": len(ok),
                "t_end": fmt(smoke["t_final"]),
                "reference_method": smoke["reference_method"],
                "reference_h": fmt(smoke["reference_h"]),
                "finest_h": fmt(finest.get("h")),
                "coordinate_observed_order": fmt(fit_order(group, "coordinate_error_q")),
                "velocity_observed_order": fmt(fit_order(group, "velocity_error_v")),
                "frobenius_observed_order": fmt(fit_order(group, "frobenius_error_norm_eta")),
                "coordinate_pairwise_order_floor": fmt(order_floor(nested["coordinate_pairwise_orders"])),
                "velocity_pairwise_order_floor": fmt(order_floor(nested["velocity_pairwise_orders"])),
                "frobenius_pairwise_order_floor": fmt(order_floor(nested["frobenius_pairwise_orders"])),
                "finest_coordinate_error_q": fmt(finest.get("coordinate_error_q")),
                "finest_velocity_error_v": fmt(finest.get("velocity_error_v")),
                "finest_frobenius_error_norm_eta": fmt(finest.get("frobenius_error_norm_eta")),
                "runtime_sec_sum": fmt(sum(value for value in runtime_values if math.isfinite(value))),
                "total_newton_iterations_sum": fmt(sum(value for value in iteration_values if math.isfinite(value))),
                "max_newton_residual_norm": fmt(nested["max_newton_residual_norm"]),
                "coordinate_error_decreased": str(nested["coordinate_error_decreased"]).lower(),
                "velocity_error_decreased": str(nested["velocity_error_decreased"]).lower(),
                "frobenius_error_decreased": str(nested["frobenius_error_decreased"]).lower(),
                "source_policy_method_runner_equivalent": "false",
                "source_policy_row_completed": "false",
                "external_superiority_claim_allowed": "false",
                "accepted_use": nested["accepted_use"],
                "notes": "Same-grid candidate work/precision summary; not a source-policy row.",
            }
        )

    gauss6 = next(row for row in summary_rows if row["source_method"] == "Gauss6_FullVA")
    tfe_m3 = next(row for row in summary_rows if row["source_method"] == "TFE_m3_GL")
    summary = {
        "schema": "tfe-source-pendulum-same-test-work-precision-v1",
        "status": "same_test_candidate_work_precision_available_not_source_policy",
        "policy": POLICY,
        "case_id": smoke["case_id"],
        "example": smoke["example"],
        "t_final": smoke["t_final"],
        "reference_method": smoke["reference_method"],
        "reference_h": smoke["reference_h"],
        "step_sizes": smoke["comparison_h"],
        "candidate_methods": list(EXPECTED_METHODS),
        "method_count": len(EXPECTED_METHODS),
        "row_count": len(rows),
        "ok_row_count": sum(1 for row in rows if row.get("status") == "ok"),
        "summary_row_count": len(summary_rows),
        "same_test_work_precision_available": True,
        "work_proxy_columns": ["runtime_sec", "total_newton_iterations", "work_units_newton_iterations"],
        "figure_available": FIGURE.exists() and FIGURE.stat().st_size > 0,
        "figure": str(FIGURE.relative_to(HERE)),
        "gauss6_velocity_pairwise_order_floor": as_float(gauss6["velocity_pairwise_order_floor"]),
        "gauss6_coordinate_pairwise_order_floor": as_float(gauss6["coordinate_pairwise_order_floor"]),
        "gauss6_frobenius_pairwise_order_floor": as_float(gauss6["frobenius_pairwise_order_floor"]),
        "tfe_m3_velocity_pairwise_order_floor": as_float(tfe_m3["velocity_pairwise_order_floor"]),
        "tfe_m3_coordinate_pairwise_order_floor": as_float(tfe_m3["coordinate_pairwise_order_floor"]),
        "source_policy_method_runner_equivalent": False,
        "source_policy_rows_completed": 0,
        "fullva_dae_source_policy_equivalent": False,
        "external_superiority_claim": False,
        "external_superiority_claim_allowed": False,
        "default_1e-4_required": False,
        "heavy_numerical_run_invoked": False,
        "interpretation": (
            "This artifact puts Newmark-beta, trapezoidal, TFE m=1/2/3, and the "
            "Gauss6/FullVA planar candidate on the same frictionless source-pendulum "
            "T=1 grid. It supplies a fair candidate-level work/precision diagnostic, "
            "but it is not an original TFE source-policy reproduction and does not "
            "authorize external-superiority claims."
        ),
    }
    return summary_rows, summary


def write_markdown(summary: dict[str, object], summary_rows: list[dict[str, object]]) -> None:
    lines = [
        "# TFE Source-Pendulum Same-Test Work/Precision",
        "",
        f"Status: **{str(summary['status']).replace('_', ' ')}**.",
        "",
        f"- Rows: `{summary['ok_row_count']}/{summary['row_count']}` ok.",
        f"- Methods: `{','.join(summary['candidate_methods'])}`.",
        f"- Time/reference/grid: `T={summary['t_final']}`, `h_ref={summary['reference_h']}`, `h={summary['step_sizes']}`.",
        f"- Figure available: `{summary['figure_available']}`.",
        f"- Source-policy rows completed: `{summary['source_policy_rows_completed']}`.",
        f"- External superiority claim: `{summary['external_superiority_claim']}`.",
        "",
        "All rows share the frictionless extracted source-pendulum parameters, output",
        "policy, RK4 reference, time horizon, and step grid. Runtime and Newton",
        "iteration counts are recorded as work proxies. This is candidate-level",
        "same-test evidence only.",
        "",
        "| Method | expected | ok | coord order | vel order | Frobenius order | finest vel | Newton sum | runtime sum |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary_rows:
        lines.append(
            "| "
            f"`{row['method']}` | `{row['expected_order']}` | `{row['ok_row_count']}/{row['row_count']}` | "
            f"`{row['coordinate_observed_order']}` | `{row['velocity_observed_order']}` | "
            f"`{row['frobenius_observed_order']}` | `{row['finest_velocity_error_v']}` | "
            f"`{row['total_newton_iterations_sum']}` | `{row['runtime_sec_sum']}` |"
        )
    SUMMARY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_figure(rows: list[dict[str, object]]) -> None:
    import matplotlib.pyplot as plt

    labels = {
        "Newmark_beta": "Newmark",
        "trapezoidal": "trap.",
        "TFE_m1": "TFE m=1",
        "TFE_m2": "TFE m=2",
        "TFE_m3_GL": "TFE m=3",
        "Gauss6_FullVA": "Gauss6",
    }
    markers = {
        "Newmark_beta": "o",
        "trapezoidal": "s",
        "TFE_m1": "^",
        "TFE_m2": "D",
        "TFE_m3_GL": "P",
        "Gauss6_FullVA": "*",
    }
    colors = {
        "Newmark_beta": "#4c78a8",
        "trapezoidal": "#f58518",
        "TFE_m1": "#54a24b",
        "TFE_m2": "#b279a2",
        "TFE_m3_GL": "#e45756",
        "Gauss6_FullVA": "#111111",
    }
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
        fig, axes = plt.subplots(1, 2, figsize=(6.9, 2.85), constrained_layout=True)
        for source_method in EXPECTED_METHODS:
            group = sorted(
                [row for row in rows if row.get("source_method") == source_method and row.get("status") == "ok"],
                key=lambda row: as_float(row.get("h")),
            )
            velocity_errors = [as_float(row.get("velocity_error_v")) for row in group]
            runtimes = [as_float(row.get("runtime_sec")) for row in group]
            work_units = [as_float(row.get("work_units_newton_iterations")) for row in group]
            h_values = [as_float(row.get("h")) for row in group]
            clean_runtime = [
                (x, y)
                for x, y in zip(runtimes, velocity_errors)
                if x > 0.0 and y > 0.0 and math.isfinite(x) and math.isfinite(y)
            ]
            clean_work = [
                (max(1.0, x), y)
                for x, y in zip(work_units, velocity_errors)
                if x >= 0.0 and y > 0.0 and math.isfinite(x) and math.isfinite(y)
            ]
            if clean_runtime:
                axes[0].plot(
                    [item[0] for item in clean_runtime],
                    [item[1] for item in clean_runtime],
                    marker=markers[source_method],
                    color=colors[source_method],
                    linewidth=1.2,
                    markersize=4.4,
                    label=labels[source_method],
                )
            if clean_work:
                axes[1].plot(
                    [item[0] for item in clean_work],
                    [item[1] for item in clean_work],
                    marker=markers[source_method],
                    color=colors[source_method],
                    linewidth=1.2,
                    markersize=4.4,
                    label=labels[source_method],
                )
                for x, y, h in zip([item[0] for item in clean_work], [item[1] for item in clean_work], h_values):
                    if source_method in {"TFE_m3_GL", "Gauss6_FullVA"}:
                        axes[1].annotate(f"{h:g}", (x, y), textcoords="offset points", xytext=(3, 2), fontsize=6)
        axes[0].set_xscale("log")
        axes[0].set_yscale("log")
        axes[0].set_xlabel("runtime per row (s)")
        axes[0].set_ylabel("velocity error")
        axes[0].set_title("wall time")
        axes[1].set_xscale("log")
        axes[1].set_yscale("log")
        axes[1].set_xlabel("Newton iterations")
        axes[1].set_ylabel("velocity error")
        axes[1].set_title("iteration work proxy")
        for ax in axes:
            ax.grid(True, which="both", alpha=0.25, linewidth=0.45)
        handles, labels_out = axes[0].get_legend_handles_labels()
        fig.legend(
            handles,
            labels_out,
            loc="lower center",
            bbox_to_anchor=(0.5, -0.05),
            ncols=6,
            frameon=False,
            handlelength=1.4,
            columnspacing=0.9,
        )
        fig.savefig(FIGURE, dpi=260, bbox_inches="tight", pad_inches=0.04)
    plt.close("all")


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    smoke = model.source_pendulum_same_test_work_precision_smoke()
    rows = flatten_rows(smoke)
    write_figure(rows)
    summary_rows, summary = summarize_rows(smoke, rows)
    summary["figure_available"] = FIGURE.exists() and FIGURE.stat().st_size > 0
    write_csv(RAW_CSV, rows)
    write_csv(SUMMARY_CSV, summary_rows)
    with SUMMARY_JSON.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")
    write_markdown(summary, summary_rows)
    print("tfe_source_pendulum_same_test_work_precision=written")
    print(f"rows_ok={summary['ok_row_count']}/{summary['row_count']}")
    print(f"methods={summary['method_count']}")
    print(f"gauss6_velocity_order_floor={summary['gauss6_velocity_pairwise_order_floor']:.3f}")
    print(f"tfe_m3_velocity_order_floor={summary['tfe_m3_velocity_pairwise_order_floor']:.3f}")
    print("source_policy_rows_completed=0")
    print("external_superiority_claim=False")


if __name__ == "__main__":
    main()
