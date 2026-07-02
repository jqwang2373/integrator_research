#!/usr/bin/env python3
"""Explain VP coordinate-partitioning finest-error wins versus observed order."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
SUMMARY_CSV = RESULTS / "coarse_four_example_order_summary.csv"
RAW_CSV = RESULTS / "coarse_four_example_order_raw_rows.csv"
OUT_CSV = RESULTS / "vp_coordinate_partitioning_order_audit.csv"
OUT_JSON = RESULTS / "vp_coordinate_partitioning_order_audit.json"
OUT_MD = RESULTS / "vp_coordinate_partitioning_order_audit.md"
LARGE_STEP_JSON = RESULTS / "large_step_vp_local_order_summary.json"

LOCAL = "local_Gauss6_FullVA"
VP = "vp2024_coordinate_partitioning_rA"
EXAMPLES = ("single_pendulum", "double_pendulum", "four_link", "slider_crank")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def as_float(value: str | None) -> float:
    try:
        out = float(value or "nan")
    except ValueError:
        return float("nan")
    return out if math.isfinite(out) else float("nan")


def fmt(value: float) -> str:
    if not math.isfinite(value):
        return "nan"
    return f"{value:.16e}"


def sequence(raw_rows: list[dict[str, str]], method: str, example: str, metric: str) -> list[float]:
    rows = [
        row
        for row in raw_rows
        if row.get("method") == method and row.get("example") == example and row.get("status") == "ok"
    ]
    rows.sort(key=lambda row: as_float(row.get("h")))
    # Report coarse-to-fine to match the h display 0.1 -> 0.05 -> 0.025.
    rows = list(reversed(rows))
    return [as_float(row.get(metric)) for row in rows]


def ratio_sequence(errors: list[float]) -> list[float]:
    ratios: list[float] = []
    for left, right in zip(errors, errors[1:]):
        if left > 0.0 and right > 0.0:
            ratios.append(left / right)
        else:
            ratios.append(float("nan"))
    return ratios


def pipe(values: list[float]) -> str:
    return "|".join(fmt(value) for value in values)


def interpretation(
    example: str,
    local_finest_error: float,
    vp_finest_error: float,
    local_order: float,
    vp_order: float,
) -> str:
    vp_wins_finest_error = vp_finest_error < local_finest_error
    vp_low_order = math.isfinite(vp_order) and vp_order < 1.5
    vp_near_floor = math.isfinite(vp_finest_error) and vp_finest_error < 1.0e-10
    if vp_wins_finest_error and vp_low_order and vp_near_floor:
        return (
            "VP has the smaller finest-step velocity error and a low observed order on this "
            "grid. This row is a pointwise VP error win, not evidence that VP is high order."
        )
    if vp_wins_finest_error and vp_low_order:
        return (
            "VP has the smaller finest-step velocity error, but the observed velocity order "
            "is low; this supports only a pointwise error win."
        )
    if local_order > vp_order:
        return "Local method has higher observed velocity order."
    return "No local velocity-order advantage is established by this row."


def main() -> None:
    summary_rows = read_csv(SUMMARY_CSV)
    raw_rows = read_csv(RAW_CSV)
    by_key = {(row["method"], row["example"]): row for row in summary_rows}
    large_step_summary = {}
    if LARGE_STEP_JSON.exists():
        with LARGE_STEP_JSON.open(encoding="utf-8") as handle:
            large_step_summary = json.load(handle)

    rows: list[dict[str, object]] = []
    local_order_wins = 0
    vp_finest_error_wins = 0
    vp_floor_dominated_error_wins = 0

    for example in EXAMPLES:
        local_row = by_key[(LOCAL, example)]
        vp_row = by_key[(VP, example)]
        local_order = as_float(local_row.get("vel_order"))
        vp_order = as_float(vp_row.get("vel_order"))
        local_errors = sequence(raw_rows, LOCAL, example, "vel_error")
        vp_errors = sequence(raw_rows, VP, example, "vel_error")
        local_finest = as_float(local_row.get("finest_vel_error"))
        vp_finest = as_float(vp_row.get("finest_vel_error"))
        vp_error_ratio = vp_finest / local_finest if local_finest > 0.0 else float("nan")
        local_wins_order = math.isfinite(local_order) and math.isfinite(vp_order) and local_order > vp_order
        vp_wins_error = math.isfinite(vp_finest) and math.isfinite(local_finest) and vp_finest < local_finest
        floor_dominated = vp_wins_error and vp_finest < 1.0e-10 and vp_order < 1.5

        local_order_wins += int(local_wins_order)
        vp_finest_error_wins += int(vp_wins_error)
        vp_floor_dominated_error_wins += int(floor_dominated)

        rows.append(
            {
                "example": example,
                "h_values_coarse_to_fine": "0.1|0.05|0.025",
                "local_velocity_errors": pipe(local_errors),
                "vp_velocity_errors": pipe(vp_errors),
                "local_velocity_error_ratios": pipe(ratio_sequence(local_errors)),
                "vp_velocity_error_ratios": pipe(ratio_sequence(vp_errors)),
                "local_velocity_order": fmt(local_order),
                "vp_velocity_order": fmt(vp_order),
                "local_finest_velocity_error": fmt(local_finest),
                "vp_finest_velocity_error": fmt(vp_finest),
                "vp_finest_error_ratio_vs_local": fmt(vp_error_ratio),
                "local_wins_velocity_order": local_wins_order,
                "vp_wins_finest_velocity_error": vp_wins_error,
                "vp_floor_dominated_error_win": floor_dominated,
                "interpretation": interpretation(example, local_finest, vp_finest, local_order, vp_order),
            }
        )

    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "schema": "vp-coordinate-partitioning-order-audit-v1",
        "row_count": len(rows),
        "examples": list(EXAMPLES),
        "h_values_coarse_to_fine": [0.1, 0.05, 0.025],
        "local_velocity_order_wins": local_order_wins,
        "vp_finest_velocity_error_wins": vp_finest_error_wins,
        "vp_floor_dominated_error_wins": vp_floor_dominated_error_wins,
        "large_step_comparable_examples": large_step_summary.get("comparable_examples", 0),
        "large_step_local_velocity_order_wins": large_step_summary.get("local_velocity_order_wins", 0),
        "large_step_local_finest_velocity_error_wins": large_step_summary.get(
            "local_finest_velocity_error_wins",
            0,
        ),
        "claim": (
            "Local Gauss6 FullVA has higher observed velocity order on all four VP-coordinate "
            "comparison rows. VP coordinate partitioning wins three finest-step velocity-error "
            "rows on this grid. The larger-step diagnostic keeps the same order conclusion but "
            "also keeps the boundary that local does not win every finest-step error row."
        ),
    }
    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# VP Coordinate-Partitioning Order Audit",
        "",
        "This audit separates finest-step velocity error from observed velocity order.",
        "",
        f"Local velocity-order wins: `{local_order_wins}/4`.",
        f"VP finest-step velocity-error wins: `{vp_finest_error_wins}/4`.",
        f"Larger-step local velocity-order wins: `{summary['large_step_local_velocity_order_wins']}/{summary['large_step_comparable_examples']}`.",
        f"Larger-step local finest-velocity-error wins: `{summary['large_step_local_finest_velocity_error_wins']}/{summary['large_step_comparable_examples']}`.",
        "",
        "| Example | local vel errors | VP vel errors | local order | VP order | VP finest/error local | interpretation |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            f"`{row['example']}` | `{row['local_velocity_errors']}` | `{row['vp_velocity_errors']}` | "
            f"`{row['local_velocity_order']}` | `{row['vp_velocity_order']}` | "
            f"`{row['vp_finest_error_ratio_vs_local']}` | {row['interpretation']} |"
        )
    lines.extend(["", summary["claim"]])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("vp_coordinate_partitioning_order_audit=written")
    print(f"local_velocity_order_wins={local_order_wins}/4")
    print(f"vp_finest_velocity_error_wins={vp_finest_error_wins}/4")
    print(f"vp_floor_dominated_error_wins={vp_floor_dominated_error_wins}/4")


if __name__ == "__main__":
    main()
