#!/usr/bin/env python3
"""Run a larger-step local-vs-VP order audit to avoid floor-dominated slopes."""

from __future__ import annotations

import csv
import importlib
import json
import math
from pathlib import Path

import numpy as np

import build_closed_loop_true_dynamic_newton_coarse_order as closed_loop_local
import run_coarse_four_example_order as coarse
import run_v048 as rv


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
OUT_RAW = RESULTS / "large_step_vp_local_order_raw_rows.csv"
OUT_SUMMARY = RESULTS / "large_step_vp_local_order_summary.csv"
OUT_JSON = RESULTS / "large_step_vp_local_order_summary.json"
OUT_MD = RESULTS / "large_step_vp_local_order_summary.md"

STEP_SIZES = (0.15, 0.075, 0.0375)
REFERENCE_H = 0.01875
T_END = 0.15
EXAMPLES = ("single_pendulum", "double_pendulum", "four_link", "slider_crank")
LOCAL = "local_Gauss6_FullVA"
VP = "vp2024_coordinate_partitioning_rA"


def as_float(value: object) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return float("nan")
    return out if math.isfinite(out) else float("nan")


def fmt(value: object) -> str:
    number = as_float(value)
    return "nan" if not math.isfinite(number) else f"{number:.16e}"


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty {path.name}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def estimate_order(rows: list[dict[str, object]], key: str) -> float:
    pairs = [
        (as_float(row["h"]), as_float(row[key]))
        for row in rows
        if row.get("status") == "ok" and as_float(row["h"]) > 0.0 and as_float(row[key]) > 0.0
    ]
    pairs.sort(reverse=True)
    if len(pairs) < 2:
        return float("nan")
    slope, _ = np.polyfit(np.log([h for h, _ in pairs]), np.log([err for _, err in pairs]), 1)
    return float(slope)


def pairwise_orders(rows: list[dict[str, object]], key: str) -> list[float]:
    pairs = [
        (as_float(row["h"]), as_float(row[key]))
        for row in rows
        if row.get("status") == "ok" and as_float(row["h"]) > 0.0 and as_float(row[key]) > 0.0
    ]
    pairs.sort(reverse=True)
    out: list[float] = []
    for (h0, e0), (h1, e1) in zip(pairs, pairs[1:]):
        out.append(float(np.log(e0 / e1) / np.log(h0 / h1)))
    return out


def raw_row(
    *,
    method: str,
    example: str,
    h: object,
    status: str,
    pos_error: object = "nan",
    vel_error: object = "nan",
    acc_error: object = "nan",
    reference_h: object = REFERENCE_H,
    evidence: str,
    notes: str,
) -> dict[str, object]:
    return {
        "method": method,
        "example": example,
        "h": fmt(h),
        "t_end": fmt(T_END),
        "reference_h": fmt(reference_h),
        "status": status,
        "pos_error": fmt(pos_error),
        "vel_error": fmt(vel_error),
        "acc_error": fmt(acc_error),
        "evidence": evidence,
        "notes": notes,
    }


def run_local_single_rows() -> list[dict[str, object]]:
    config = rv.Gauss6PublicSingleConfig(
        policy="large_step_vp_order_audit_local_single",
        run_mode="large_step_vp_order_audit_local_single",
        step_sizes=STEP_SIZES,
        reference_h=REFERENCE_H,
        t_end=T_END,
        run_model=True,
    )
    rows, _summary = rv.run_gauss6_fullva_public_horizon_single_rows(config)
    return [
        raw_row(
            method=LOCAL,
            example="single_pendulum",
            h=row["h"],
            status=row["status"],
            pos_error=row["position_l2_error"],
            vel_error=row["velocity_l2_error"],
            acc_error=row["omega_l2_error"],
            evidence="run_v048.run_gauss6_fullva_public_horizon_single_rows",
            notes="larger-step local single-pendulum analytic-reference row",
        )
        for row in rows
    ]


def run_local_double_rows() -> list[dict[str, object]]:
    config = rv.Gauss6PublicDoubleCoarseConfig(
        policy="large_step_vp_order_audit_local_double",
        run_mode="large_step_vp_order_audit_local_double",
        step_sizes=STEP_SIZES,
        reference_h=REFERENCE_H,
        t_end=T_END,
        run_model=True,
    )
    rows, _summary = rv.run_gauss6_fullva_public_horizon_double_coarse_rows(config)
    return [
        raw_row(
            method=LOCAL,
            example="double_pendulum",
            h=row["h"],
            status=row["status"],
            pos_error=row["pos_final_linf"],
            vel_error=row["vel_final_linf"],
            reference_h=row["reference_h"],
            evidence="run_v048.run_gauss6_fullva_public_horizon_double_coarse_rows",
            notes="larger-step local double-pendulum self-reference row",
        )
        for row in rows
    ]


def run_local_closed_loop_rows() -> list[dict[str, object]]:
    closed_loop_local.STEP_SIZES = STEP_SIZES
    closed_loop_local.T_END = T_END
    v047_module = closed_loop_local.import_v047_module()
    v046 = v047_module.load_v046()
    v046.patch_modern_numpy_scalar_assignments()
    models = {model.name: model for model in v046.MODELS}
    rows: list[dict[str, object]] = []
    for example in ("four_link", "slider_crank"):
        model = models[example]
        reference_system = closed_loop_local.setup_exact_system(
            v047_module,
            v046,
            model,
            REFERENCE_H,
            T_END,
        )
        reference = closed_loop_local.dynres.endpoint_state_from_system(reference_system)
        for h in STEP_SIZES:
            row = closed_loop_local.simulate_model_h(v047_module, v046, model, h, reference)
            rows.append(
                raw_row(
                    method=LOCAL,
                    example=example,
                    h=row["h"],
                    status=row["status"],
                    pos_error=row["endpoint_pos_error_inf"],
                    vel_error=row["endpoint_vel_error_inf"],
                    acc_error=row["endpoint_acc_error_inf"],
                    evidence="build_closed_loop_true_dynamic_newton_coarse_order.simulate_model_h",
                    notes="larger-step local closed-loop true-dynamic Newton row",
                )
            )
    return rows


def run_vp_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for example in EXAMPLES:
        try:
            reference = coarse.run_vp2024_coordinate_partitioning_model(
                example=example,
                h=REFERENCE_H,
                t_end=T_END,
            )
            reference_status = "ok"
        except Exception as exc:  # noqa: BLE001
            reference = None
            reference_status = f"reference_failed:{type(exc).__name__}:{str(exc).replace(chr(10), ' ')}"
        for h in STEP_SIZES:
            if reference is None:
                rows.append(
                    raw_row(
                        method=VP,
                        example=example,
                        h=h,
                        status=reference_status,
                        evidence="run_coarse_four_example_order.run_vp2024_coordinate_partitioning_model",
                        notes="larger-step VP coordinate-partitioning reference failed",
                    )
                )
                continue
            try:
                candidate = coarse.run_vp2024_coordinate_partitioning_model(example=example, h=h, t_end=T_END)
                rows.append(
                    raw_row(
                        method=VP,
                        example=example,
                        h=h,
                        status="ok",
                        pos_error=rv.final_error(reference, candidate, "pos"),
                        vel_error=rv.final_error(reference, candidate, "vel"),
                        acc_error=rv.final_error(reference, candidate, "acc"),
                        evidence="run_coarse_four_example_order.run_vp2024_coordinate_partitioning_model",
                        notes="larger-step VP coordinate-partitioning self-reference row",
                    )
                )
            except Exception as exc:  # noqa: BLE001
                rows.append(
                    raw_row(
                        method=VP,
                        example=example,
                        h=h,
                        status=f"failed:{type(exc).__name__}:{str(exc).replace(chr(10), ' ')}",
                        evidence="run_coarse_four_example_order.run_vp2024_coordinate_partitioning_model",
                        notes="larger-step VP coordinate-partitioning candidate failed",
                    )
                )
    return rows


def summarize(raw_rows: list[dict[str, object]]) -> tuple[list[dict[str, object]], dict[str, object]]:
    summary_rows: list[dict[str, object]] = []
    local_order_wins = 0
    local_finest_error_wins = 0
    comparable_examples = 0
    for method in (LOCAL, VP):
        for example in EXAMPLES:
            rows = [row for row in raw_rows if row["method"] == method and row["example"] == example]
            ok_rows = [row for row in rows if row["status"] == "ok"]
            finest = sorted(ok_rows, key=lambda row: as_float(row["h"]))[0] if ok_rows else {}
            summary_rows.append(
                {
                    "method": method,
                    "example": example,
                    "ok_count": len(ok_rows),
                    "row_count": len(rows),
                    "h_values": "|".join(fmt(row["h"]) for row in rows),
                    "reference_h": fmt(REFERENCE_H),
                    "t_end": fmt(T_END),
                    "status": "ok" if len(ok_rows) == len(STEP_SIZES) else "incomplete",
                    "pos_order": fmt(estimate_order(rows, "pos_error")),
                    "vel_order": fmt(estimate_order(rows, "vel_error")),
                    "acc_order": fmt(estimate_order(rows, "acc_error")),
                    "vel_pairwise_orders": "|".join(fmt(value) for value in pairwise_orders(rows, "vel_error")),
                    "finest_vel_error": fmt(finest.get("vel_error")),
                    "finest_pos_error": fmt(finest.get("pos_error")),
                    "notes": "larger-step audit to move VP rows away from floor-dominated 0.1/0.05/0.025 slopes",
                }
            )

    by_key = {(row["method"], row["example"]): row for row in summary_rows}
    for example in EXAMPLES:
        local = by_key[(LOCAL, example)]
        vp = by_key[(VP, example)]
        if local["status"] != "ok" or vp["status"] != "ok":
            continue
        comparable_examples += 1
        local_vel_order = as_float(local["vel_order"])
        vp_vel_order = as_float(vp["vel_order"])
        local_vel_err = as_float(local["finest_vel_error"])
        vp_vel_err = as_float(vp["finest_vel_error"])
        local_order_wins += int(local_vel_order > vp_vel_order)
        local_finest_error_wins += int(local_vel_err < vp_vel_err)

    audit_summary = {
        "schema": "large-step-vp-local-order-audit-v1",
        "step_sizes": list(STEP_SIZES),
        "reference_h": REFERENCE_H,
        "t_end": T_END,
        "raw_row_count": len(raw_rows),
        "summary_row_count": len(summary_rows),
        "comparable_examples": comparable_examples,
        "local_velocity_order_wins": local_order_wins,
        "local_finest_velocity_error_wins": local_finest_error_wins,
        "claim": (
            "This larger-step audit is diagnostic evidence for the VP coordinate-partitioning comparison. "
            "It is not a replacement for the full 13-method coarse matrix."
        ),
    }
    return summary_rows, audit_summary


def write_markdown(summary_rows: list[dict[str, object]], summary: dict[str, object]) -> None:
    lines = [
        "# Larger-Step VP/Local Order Audit",
        "",
        f"Step sizes: `{summary['step_sizes']}`; reference h: `{summary['reference_h']}`; t_end: `{summary['t_end']}`.",
        "",
        f"Comparable examples: `{summary['comparable_examples']}/4`.",
        f"Local velocity-order wins: `{summary['local_velocity_order_wins']}/{summary['comparable_examples']}`.",
        f"Local finest-velocity-error wins: `{summary['local_finest_velocity_error_wins']}/{summary['comparable_examples']}`.",
        "",
        "| Method | Example | status | vel order | pairwise vel orders | finest vel error |",
        "|---|---|---|---:|---:|---:|",
    ]
    for row in summary_rows:
        lines.append(
            "| "
            f"`{row['method']}` | `{row['example']}` | `{row['status']}` | "
            f"`{row['vel_order']}` | `{row['vel_pairwise_orders']}` | `{row['finest_vel_error']}` |"
        )
    lines.extend(["", str(summary["claim"])])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    importlib.invalidate_caches()
    raw_rows = []
    raw_rows.extend(run_local_single_rows())
    raw_rows.extend(run_local_double_rows())
    raw_rows.extend(run_local_closed_loop_rows())
    raw_rows.extend(run_vp_rows())
    summary_rows, summary = summarize(raw_rows)
    write_csv(OUT_RAW, raw_rows)
    write_csv(OUT_SUMMARY, summary_rows)
    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")
    write_markdown(summary_rows, summary)
    print("large_step_vp_local_order_audit=written")
    print(f"comparable_examples={summary['comparable_examples']}/4")
    print(f"local_velocity_order_wins={summary['local_velocity_order_wins']}/{summary['comparable_examples']}")
    print(f"local_finest_velocity_error_wins={summary['local_finest_velocity_error_wins']}/{summary['comparable_examples']}")


if __name__ == "__main__":
    main()
