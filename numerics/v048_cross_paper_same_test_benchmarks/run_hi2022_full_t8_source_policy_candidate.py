#!/usr/bin/env python3
"""Run one isolated HI2022 full-T=8 source-policy candidate shard.

This script intentionally writes separate candidate artifacts instead of
overwriting the canonical ``hi2022_halfimplicit_rows.csv`` bounded-pilot table.
The default shard is the rA double-pendulum T=8 coarse trio against the in-suite
rA h=1e-3 reference.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Any

import run_v048 as rv


STEM = "hi2022_full_t8_source_policy_candidate"
DEFAULT_STEP_SIZES = (0.02, 0.01, 0.005)


def close(a: float, b: float) -> bool:
    return abs(float(a) - float(b)) <= 1.0e-15


def tag_float(value: float) -> str:
    return f"{float(value):g}".replace(".", "p").replace("-", "m")


def output_stem(form: str, model: str) -> str:
    return f"{STEM}_{form}_{model}"


def contains_1e4(values: tuple[float, ...]) -> bool:
    return any(abs(float(value) - 1.0e-4) <= 1.0e-15 for value in values)


def pair_orders(rows: list[dict[str, Any]], metric: str) -> list[float]:
    pairs = sorted(
        [
            (float(row["h"]), float(row[metric]))
            for row in rows
            if row.get("status") == "ok" and math.isfinite(float(row.get(metric, "nan")))
        ],
        reverse=True,
    )
    return [
        math.log(e0 / e1) / math.log(h0 / h1)
        for (h0, e0), (h1, e1) in zip(pairs, pairs[1:])
        if e0 > 0.0 and e1 > 0.0
    ]


def finite_float_values(rows: list[dict[str, Any]], key: str) -> list[float]:
    values: list[float] = []
    for row in rows:
        try:
            value = float(row[key])
        except (KeyError, TypeError, ValueError):
            continue
        if math.isfinite(value):
            values.append(value)
    return values


def source_policy_time_window_selected(t_end: float) -> bool:
    return close(t_end, rv.HI2022_PUBLIC_T_END)


def source_policy_reference_selected(reference_h: float) -> bool:
    return close(reference_h, rv.HI2022_REFERENCE_H)


def selected_coarse_trio(step_sizes: tuple[float, ...]) -> bool:
    return list(step_sizes) == list(DEFAULT_STEP_SIZES)


def full_public_grid_selected(step_sizes: tuple[float, ...]) -> bool:
    return list(step_sizes) == list(rv.HI2022_PUBLIC_STEP_SIZES)


def write_markdown(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# HI2022 Full T=8 Source-Policy Candidate",
        "",
        f"Status: **{summary['status']}**.",
        "",
        f"- Execution phase: `{summary['execution_phase']}`.",
        f"- Form/model: `{summary['form']}` / `{summary['model']}`.",
        f"- T=8 time window selected: `{summary['source_policy_time_window_selected']}`.",
        f"- Reference h selected: `{summary['source_policy_reference_h_selected']}`.",
        f"- Selected step sizes: `{summary['selected_step_sizes']}`.",
        f"- Full public grid selected: `{summary['full_public_grid_selected']}`.",
        f"- Source-policy 1e-4 included: `{summary['source_policy_1e_4_included']}`.",
        f"- Rows ok/total: `{summary['ok_row_count']}/{summary['row_count']}`.",
        f"- Selected step trio completed: `{summary['selected_step_trio_completed']}`.",
        f"- Position pair orders: `{summary['position_pair_orders']}`.",
        f"- Velocity pair orders: `{summary['velocity_pair_orders']}`.",
        f"- Acceleration pair orders: `{summary['acceleration_pair_orders']}`.",
        f"- Runtime values: `{summary['runtime_sec_values']}`.",
        f"- Reference runtime: `{summary['reference_runtime_sec']}`.",
        f"- Full T=8 policy completed: `{summary['full_T8_policy_completed']}`.",
        f"- Source-policy rows promoted: `{summary['source_policy_reproduction_rows_promoted']}`.",
        f"- Source-policy rows closed by this evidence: `{summary['source_policy_rows_closed_by_this_evidence']}`.",
        f"- Promotion ready: `{summary['promotion_ready']}`.",
        f"- B4/B7 can close from this candidate: `{summary['b4_can_close_from_this_evidence']}/{summary['b7_can_close_from_this_evidence']}`.",
        f"- Canonical HI2022 output untouched by this writer: `{summary['canonical_hi2022_output_untouched_by_writer']}`.",
        "",
        "Promotion blockers:",
    ]
    for blocker in summary["promotion_blockers"]:
        lines.append(f"- {blocker}")
    lines.extend(
        [
            "",
            "This candidate can document T=8 executability for one shard, but it is not a full HI2022 source-policy work/precision curve.",
            "It closes zero B4/B7 source-policy rows unless the full policy grid, tied work metrics, and figure-scope decision are promoted by a separate audited step.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def build_summary(
    *,
    form: str,
    model: str,
    step_sizes: tuple[float, ...],
    reference_h: float,
    t_end: float,
    execute: bool,
    rows: list[dict[str, Any]],
    raw_summary: dict[str, Any],
    rows_name: str,
) -> dict[str, Any]:
    ok_rows = [row for row in rows if row.get("status") == "ok"]
    group = raw_summary.get("groups", {}).get(f"{form}:{model}", {})
    ref_runtimes = finite_float_values(rows, "reference_runtime_sec")
    time_window = source_policy_time_window_selected(t_end)
    reference_selected = source_policy_reference_selected(reference_h)
    coarse_trio = selected_coarse_trio(step_sizes)
    full_grid = full_public_grid_selected(step_sizes)
    executed_complete = execute and len(ok_rows) == len(rows) and len(rows) == len(step_sizes)
    status = (
        "executed_full_T8_selected_coarse_trio_not_promoted"
        if executed_complete and time_window and reference_selected and coarse_trio
        else "planned_full_T8_source_policy_candidate"
        if not execute
        else "partial_or_failed_full_T8_source_policy_candidate_not_promoted"
    )
    promotion_blockers = [
        "full HI2022 public step grid is not selected or not completed",
        "work/precision figure rows are not promoted from this isolated shard",
        "runtime and error/order rows are not yet bound into a publication-grade full-policy figure",
    ]
    if not full_grid:
        promotion_blockers.append("selected coarse trio is not the full encoded HI2022 public step family")
    return {
        "schema": "hi2022-full-t8-source-policy-candidate-v1",
        "status": status,
        "execution_phase": "candidate" if execute else "plan_only",
        "execute_requested": execute,
        "heavy_numerical_run_invoked": execute,
        "builder_invoked_heavy_numerical_run": False,
        "canonical_v048_main_invoked": False,
        "form": form,
        "model": model,
        "selected_step_sizes": list(step_sizes),
        "selected_reference_h": reference_h,
        "selected_t_end": t_end,
        "estimated_reference_steps": int(round(t_end / reference_h)),
        "estimated_candidate_steps": [int(round(t_end / h)) for h in step_sizes],
        "source_policy_time_window_selected": time_window,
        "source_policy_reference_h_selected": reference_selected,
        "selected_coarse_trio": coarse_trio,
        "full_public_grid_selected": full_grid,
        "full_T8_policy_completed": False,
        "source_policy_1e_4_included": contains_1e4(step_sizes + (reference_h,)),
        "row_count": len(rows),
        "ok_row_count": len(ok_rows),
        "planned_row_count": sum(1 for row in rows if row.get("status") == "planned_not_run"),
        "source_policy_candidate_rows_completed": len(ok_rows),
        "selected_step_trio_completed": group.get("selected_step_trio_completed", False),
        "reference_status": group.get("reference_status"),
        "reference_execution_path": group.get("reference_execution_path"),
        "reference_runtime_sec": ref_runtimes[0] if ref_runtimes else None,
        "h_values": [float(row["h"]) for row in rows] if rows else [],
        "runtime_sec_values": finite_float_values(rows, "runtime_sec"),
        "avg_iteration_values": finite_float_values(rows, "avg_iterations"),
        "max_iteration_values": finite_float_values(rows, "max_iterations"),
        "position_pair_orders": pair_orders(rows, "pos_final_linf"),
        "velocity_pair_orders": pair_orders(rows, "vel_final_linf"),
        "acceleration_pair_orders": pair_orders(rows, "acc_final_linf"),
        "raw_group_summary": group,
        "isolated_rows_output": rows_name,
        "canonical_hi2022_output_untouched_by_writer": True,
        "source_policy_reproduction_rows_promoted": 0,
        "source_policy_rows_closed_by_this_evidence": 0,
        "counts_as_executed_full_T8_candidate": executed_complete,
        "counts_as_full_public_grid_source_policy": False,
        "counts_as_b4_accepted_source_policy_rows": False,
        "counts_as_complete_work_precision_curve": False,
        "promotion_ready": False,
        "promotion_blockers": promotion_blockers,
        "b4_can_close_from_this_evidence": False,
        "b7_can_close_from_this_evidence": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--form", default="rA", choices=rv.HI2022_FORMS)
    parser.add_argument("--model", default="double_pendulum", choices=rv.HI2022_MODELS)
    parser.add_argument("--step-sizes", default=",".join(str(h) for h in DEFAULT_STEP_SIZES))
    parser.add_argument("--reference-h", type=float, default=rv.HI2022_REFERENCE_H)
    parser.add_argument("--t-end", type=float, default=rv.HI2022_PUBLIC_T_END)
    parser.add_argument("--execute", action="store_true", help="run the public-code candidate shard")
    parser.add_argument(
        "--allow-source-policy-1e-4",
        action="store_true",
        help="permit an explicit h=1e-4 value if the selected grid contains it",
    )
    args = parser.parse_args()

    step_sizes = tuple(rv.parse_float_csv(args.step_sizes))
    rv.require_source_policy_1e4_allow(
        parser,
        args.allow_source_policy_1e_4,
        "HI2022 full-T8 source-policy candidate",
        step_sizes + (float(args.reference_h),),
    )

    config = rv.HI2022Config(
        policy="hi2022_full_T8_selected_coarse_trio_candidate_not_full_campaign",
        run_mode="hi2022_full_T8_selected_source_policy_candidate_shard",
        forms=(args.form,),
        models=(args.model,),
        step_sizes=step_sizes,
        reference_h=float(args.reference_h),
        t_end=float(args.t_end),
        tolerance_base=rv.HI2022_TOLERANCE_BASE,
        run_public_code=bool(args.execute),
        full_hi2022_campaign_completed=False,
    )
    rows, raw_summary = rv.run_hi2022_halfimplicit_rows(config)
    phase = "candidate" if args.execute else "plan_only"
    for row in rows:
        h = float(row["h"])
        row.update(
            {
                "policy": config.policy,
                "case_id": f"hi2022_{args.model}_full_T8_selected_coarse_trio",
                "reference_policy": "full_T8_in_suite_rA_reference_h1e-3",
                "row_type": "full_T8_selected_source_policy_candidate",
                "execution_phase": phase,
                "source_policy_time_window_selected": source_policy_time_window_selected(config.t_end),
                "source_policy_reference_h_selected": source_policy_reference_selected(config.reference_h),
                "source_policy_selected_coarse_h": any(close(h, value) for value in DEFAULT_STEP_SIZES),
                "full_public_grid_selected": full_public_grid_selected(step_sizes),
                "source_policy_row_promoted": False,
                "accepted_use": "full_T8_selected_coarse_trio_candidate_not_source_policy_work_precision",
                "canonical_hi2022_output_untouched": True,
            }
        )

    stem = output_stem(args.form, args.model)
    rows_name = f"{stem}_rows.csv"
    summary_name = f"{stem}_summary.json"
    md_name = f"{stem}.md"
    rv.RESULTS.mkdir(parents=True, exist_ok=True)
    rv.write_csv(rv.RESULTS / rows_name, rows)
    summary = build_summary(
        form=args.form,
        model=args.model,
        step_sizes=step_sizes,
        reference_h=float(args.reference_h),
        t_end=float(args.t_end),
        execute=bool(args.execute),
        rows=rows,
        raw_summary=raw_summary,
        rows_name=rows_name,
    )
    rv.write_json_atomic(rv.RESULTS / summary_name, summary)
    write_markdown(rv.RESULTS / md_name, summary)
    print(
        "hi2022_full_t8_source_policy_candidate=ok "
        f"status={summary['status']} group={args.form}:{args.model} "
        f"rows={summary['ok_row_count']}/{summary['row_count']}"
    )


if __name__ == "__main__":
    main()
