#!/usr/bin/env python3
"""Build a coarse closed-loop dynamic-order probe without default 1e-4 rows."""

from __future__ import annotations

import json
import math
from pathlib import Path

import run_v048 as rv


RESULTS = Path(__file__).resolve().parent / "results"
MODELS = ("four_link", "slider_crank")
STEP_SIZES = (0.1, 0.05, 0.025)
REFERENCE_H = 0.0125
T_END = 0.2
POLICY = "ra2021_closed_loop_coarse_dynamic_order_probe_no_default_1e-4"


def finite(value: object) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def relabel_rows(rows: list[dict]) -> list[dict]:
    out: list[dict] = []
    for row in rows:
        row = dict(row)
        row["policy"] = POLICY
        row["row_type"] = "coarse_same_window_final_error_work_probe"
        row["coarse_probe_policy"] = "True"
        row["default_policy"] = "coarse_first_no_default_1e-4"
        row["accepted_dynamic_order"] = "false"
        row["external_superiority_claim_allowed"] = "false"
        row["notes"] = (
            "Coarse h=0.1|0.05|0.025 probe for four_link/slider_crank. "
            "This tests whether larger steps remove the selected-window floor issue; "
            "it is still a kinematic FullVA plus reaction reconstruction row and is "
            "not accepted dynamic order/work superiority."
        )
        out.append(row)
    return out


def relabel_work_rows(rows: list[dict]) -> list[dict]:
    out: list[dict] = []
    for row in rows:
        row = dict(row)
        row["policy"] = f"{POLICY}_work_precision_summary"
        row["case_id"] = row.get("case_id", "").replace("selected_same_window", "coarse_dynamic_order_probe")
        row["coarse_probe_policy"] = "True"
        row["default_policy"] = "coarse_first_no_default_1e-4"
        row["accepted_dynamic_order"] = "false"
        row["external_superiority_claim_allowed"] = "false"
        row["notes"] = (
            "Work/precision summary for the coarse closed-loop probe. Ratios use "
            "public rA dynamics at the same model and finest coarse h. This remains "
            "probe evidence because the local row is kinematic/reaction, not a true "
            "local dynamic trajectory row."
        )
        out.append(row)
    return out


def build_summary(rows: list[dict], work_rows: list[dict]) -> dict:
    local_rows = [row for row in work_rows if row.get("method") == "Gauss6/FullVA-local-closed-loop"]
    public_rows = [row for row in work_rows if row.get("method") == "rA-public-dynamics"]
    local_position_floor_rows = 0
    local_velocity_evidence_rows = 0
    local_acceleration_evidence_rows = 0
    for row in local_rows:
        pos_ratio = finite(row.get("finest_pos_error_ratio_vs_rA"))
        vel_ratio = finite(row.get("finest_vel_error_ratio_vs_rA"))
        acc_ratio = finite(row.get("finest_acc_error_ratio_vs_rA"))
        residual = finite(row.get("max_dynamics_residual_norm"))
        if pos_ratio is not None and pos_ratio > 1.0:
            local_position_floor_rows += 1
        if vel_ratio is not None and residual is not None and vel_ratio < 1.0e-4 and residual < 1.0e-12:
            local_velocity_evidence_rows += 1
        if acc_ratio is not None and residual is not None and acc_ratio < 1.0e-4 and residual < 1.0e-12:
            local_acceleration_evidence_rows += 1
    failed_rows = [row for row in rows if row.get("status") != "ok"]
    public_failed_rows = [row for row in failed_rows if row.get("method") == "rA-public-dynamics"]

    return {
        "schema": "closed-loop-coarse-dynamic-order-probe-v1",
        "policy": POLICY,
        "default_policy": "coarse_first_no_default_1e-4",
        "models": list(MODELS),
        "step_sizes": list(STEP_SIZES),
        "reference_h": REFERENCE_H,
        "t_end": T_END,
        "row_count": len(rows),
        "ok_row_count": sum(1 for row in rows if row.get("status") == "ok"),
        "failed_row_count": len(failed_rows),
        "public_failed_row_count": len(public_failed_rows),
        "failed_rows": [
            {
                "model": row.get("model"),
                "method": row.get("method"),
                "h": row.get("h"),
                "status": row.get("status"),
            }
            for row in failed_rows
        ],
        "work_summary_row_count": len(work_rows),
        "local_method_count": len(local_rows),
        "public_method_count": len(public_rows),
        "local_position_floor_rows": local_position_floor_rows,
        "local_velocity_evidence_rows": local_velocity_evidence_rows,
        "local_acceleration_evidence_rows": local_acceleration_evidence_rows,
        "accepted_dynamic_order_count": 0,
        "external_superiority_claim": False,
        "same_test_campaign_status": "not_run",
        "interpretation": (
            "This coarse probe uses h=0.1|0.05|0.025 to test the user's large-step "
            "diagnostic idea without running default 1e-4 rows. It is not promoted "
            "to accepted dynamic order because the local closed-loop method row is "
            "still the kinematic FullVA plus reaction reconstruction policy."
        ),
        "next_gate": (
            "Add a true local dynamic trajectory/order row for four_link and "
            "slider_crank, or prove a reviewer-defensible residual-to-error "
            "acceptance theorem for the kinematic/reaction row."
        ),
    }


def write_markdown(summary: dict, work_rows: list[dict]) -> None:
    lines = [
        "# Closed-Loop Coarse Dynamic-Order Probe",
        "",
        "Status: **coarse probe only; accepted dynamic order remains zero**",
        "",
        f"- Default policy: `{summary['default_policy']}`.",
        f"- Step sizes: `0.1|0.05|0.025`; reference h: `{summary['reference_h']}`.",
        f"- Raw rows: `{summary['ok_row_count']}/{summary['row_count']}` ok.",
        f"- Failed public rows: `{summary['public_failed_row_count']}`.",
        f"- Work-summary rows: `{summary['work_summary_row_count']}`.",
        f"- Local velocity evidence rows: `{summary['local_velocity_evidence_rows']}/{summary['local_method_count']}`.",
        f"- Local acceleration evidence rows: `{summary['local_acceleration_evidence_rows']}/{summary['local_method_count']}`.",
        f"- Local position-floor rows: `{summary['local_position_floor_rows']}/{summary['local_method_count']}`.",
        f"- Accepted dynamic order rows: `{summary['accepted_dynamic_order_count']}`.",
        f"- External superiority claim: `{summary['external_superiority_claim']}`.",
        "",
        "Reading rule: this artifact checks whether larger steps remove the closed-loop floor issue. It does not run default `1e-4` rows and does not turn kinematic/reaction rows into accepted dynamic trajectory rows.",
        "",
    ]
    if summary["failed_rows"]:
        lines.append("Failed-row detail:")
        lines.append("")
        for row in summary["failed_rows"]:
            lines.append(f"- `{row['model']}` / `{row['method']}` at `h={row['h']}`: `{row['status']}`.")
        lines.append("")
    lines.extend(
        [
            "| Model | Method | pos order | vel order | acc order | finest pos ratio | finest vel ratio | finest acc ratio | runtime ratio |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in work_rows:
        lines.append(
            "| "
            f"`{row.get('model')}` | `{row.get('method')}` | "
            f"{row.get('pos_observed_order')} | {row.get('vel_observed_order')} | "
            f"{row.get('acc_observed_order')} | {row.get('finest_pos_error_ratio_vs_rA')} | "
            f"{row.get('finest_vel_error_ratio_vs_rA')} | {row.get('finest_acc_error_ratio_vs_rA')} | "
            f"{row.get('finest_runtime_ratio_vs_rA')} |"
        )
    lines.append("")
    (RESULTS / "closed_loop_coarse_dynamic_order_probe.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    config = rv.Gauss6ClosedLoopConfig(
        policy=POLICY,
        run_mode="closed_loop_coarse_dynamic_order_probe",
        models=MODELS,
        step_sizes=STEP_SIZES,
        reference_h=REFERENCE_H,
        t_end=T_END,
        run_model=True,
    )
    rows, _ = rv.run_gauss6_fullva_closed_loop_same_window_comparison_rows(config)
    rows = relabel_rows(rows)
    work_rows, _ = rv.summarize_closed_loop_same_window_work_precision_rows(rows)
    work_rows = relabel_work_rows(work_rows)
    summary = build_summary(rows, work_rows)

    rv.write_csv(RESULTS / "closed_loop_coarse_dynamic_order_probe_rows.csv", rows)
    rv.write_csv(RESULTS / "closed_loop_coarse_dynamic_order_probe_work_precision_summary.csv", work_rows)
    with (RESULTS / "closed_loop_coarse_dynamic_order_probe.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")
    write_markdown(summary, work_rows)
    print("closed_loop_coarse_dynamic_order_probe=written")
    print(f"rows={summary['ok_row_count']}/{summary['row_count']}")
    print(f"failed_public_rows={summary['public_failed_row_count']}")
    print(f"local_velocity_evidence={summary['local_velocity_evidence_rows']}/{summary['local_method_count']}")
    print(f"local_acceleration_evidence={summary['local_acceleration_evidence_rows']}/{summary['local_method_count']}")
    print(f"local_position_floor_rows={summary['local_position_floor_rows']}/{summary['local_method_count']}")
    print(f"accepted_dynamic_order={summary['accepted_dynamic_order_count']}")
    print("external_superiority_claim=False")


if __name__ == "__main__":
    main()
