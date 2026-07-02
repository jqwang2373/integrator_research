#!/usr/bin/env python3
"""Build a closed-loop dynamic error floor audit from existing v048 rows."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
MODELS = ("four_link", "slider_crank")
PUBLIC_METHOD = "rA-public-dynamics"
LOCAL_METHOD = "Gauss6/FullVA-local-closed-loop"
RATIO_THRESHOLD = 1.0e-4
RESIDUAL_THRESHOLD = 1.0e-12


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def as_float(row: dict[str, str], key: str) -> float:
    try:
        return float(row.get(key, "nan"))
    except (TypeError, ValueError):
        return float("nan")


def fmt(value: float) -> str:
    if not math.isfinite(value):
        return "nan"
    return f"{value:.16e}"


def method_row(rows: list[dict[str, str]], model: str, method: str) -> dict[str, str]:
    matches = [row for row in rows if row.get("model") == model and row.get("method") == method]
    if len(matches) != 1:
        raise ValueError(f"expected exactly one {model}/{method} work row, got {len(matches)}")
    return matches[0]


def build_audit() -> tuple[list[dict[str, str]], dict]:
    work_rows = read_csv(RESULTS / "gauss6_closed_loop_same_window_work_precision_summary.csv")
    rows: list[dict[str, str]] = []
    for model in MODELS:
        public = method_row(work_rows, model, PUBLIC_METHOD)
        local = method_row(work_rows, model, LOCAL_METHOD)

        local_pos_ratio = as_float(local, "finest_pos_error_ratio_vs_rA")
        local_vel_ratio = as_float(local, "finest_vel_error_ratio_vs_rA")
        local_acc_ratio = as_float(local, "finest_acc_error_ratio_vs_rA")
        local_residual = as_float(local, "max_dynamics_residual_norm")
        velocity_acceleration_floor_evidence = (
            math.isfinite(local_vel_ratio)
            and math.isfinite(local_acc_ratio)
            and local_vel_ratio < RATIO_THRESHOLD
            and local_acc_ratio < RATIO_THRESHOLD
            and math.isfinite(local_residual)
            and local_residual < RESIDUAL_THRESHOLD
        )
        position_floor_blocker = math.isfinite(local_pos_ratio) and local_pos_ratio > 1.0

        status = "velocity_acceleration_floor_evidence_position_reference_floor_blocks_dynamic_order"
        rows.append(
            {
                "model": model,
                "policy": "closed_loop_dynamic_error_floor_audit_no_default_1e-4",
                "default_policy": "coarse_first_no_default_1e-4",
                "t_end": local.get("t_end", public.get("t_end", "0.2")),
                "finest_h": local.get("finest_h", "nan"),
                "reference_method": local.get("reference_method", "rA-public-kinematics"),
                "reference_h": local.get("reference_h", "0.001"),
                "public_method": PUBLIC_METHOD,
                "local_method": LOCAL_METHOD,
                "status": status,
                "accepted_dynamic_order": "false",
                "external_superiority_claim_allowed": "false",
                "velocity_acceleration_floor_evidence": str(velocity_acceleration_floor_evidence),
                "position_floor_blocker": str(position_floor_blocker),
                "public_pos_order": public.get("pos_observed_order", "nan"),
                "public_vel_order": public.get("vel_observed_order", "nan"),
                "public_acc_order": public.get("acc_observed_order", "nan"),
                "local_pos_order": local.get("pos_observed_order", "nan"),
                "local_vel_order": local.get("vel_observed_order", "nan"),
                "local_acc_order": local.get("acc_observed_order", "nan"),
                "public_finest_pos_error": public.get("finest_pos_final_linf", "nan"),
                "public_finest_vel_error": public.get("finest_vel_final_linf", "nan"),
                "public_finest_acc_error": public.get("finest_acc_final_linf", "nan"),
                "local_finest_pos_error": local.get("finest_pos_final_linf", "nan"),
                "local_finest_vel_error": local.get("finest_vel_final_linf", "nan"),
                "local_finest_acc_error": local.get("finest_acc_final_linf", "nan"),
                "local_pos_error_ratio_vs_public": fmt(local_pos_ratio),
                "local_vel_error_ratio_vs_public": fmt(local_vel_ratio),
                "local_acc_error_ratio_vs_public": fmt(local_acc_ratio),
                "local_runtime_ratio_vs_public": local.get("finest_runtime_ratio_vs_rA", "nan"),
                "local_max_dynamics_residual_norm": fmt(local_residual),
                "next_gate": (
                    "add true local dynamic trajectory/order rows or a proof that the residual-floor "
                    "velocity/acceleration evidence is an admissible dynamic error bound"
                ),
                "blocker": (
                    "position error is dominated by the public kinematic reference floor, while the "
                    "local closed-loop row is still a kinematic FullVA plus reaction reconstruction row"
                ),
                "evidence_paths": (
                    "results/gauss6_closed_loop_same_window_work_precision_summary.csv;"
                    "results/gauss6_fullva_closed_loop_same_window_comparison_rows.csv"
                ),
            }
        )

    summary = {
        "schema": "closed-loop-dynamic-error-floor-audit-v1",
        "models": list(MODELS),
        "row_count": len(rows),
        "velocity_acceleration_evidence_count": sum(
            1 for row in rows if row["velocity_acceleration_floor_evidence"] == "True"
        ),
        "position_floor_blocker_count": sum(1 for row in rows if row["position_floor_blocker"] == "True"),
        "accepted_dynamic_order_count": 0,
        "external_superiority_claim": False,
        "same_test_campaign_status": "not_run",
        "default_policy": "coarse_first_no_default_1e-4",
        "selected_t_end": 0.2,
        "selected_step_sizes": [0.02, 0.01, 0.005],
        "selected_reference_h": 0.001,
        "ratio_threshold": RATIO_THRESHOLD,
        "residual_threshold": RESIDUAL_THRESHOLD,
        "interpretation": (
            "The selected-window rows show velocity and acceleration errors far below the public rA "
            "dynamics row and near-roundoff local dynamics residuals, but the position column is "
            "reference-floor dominated. This audit therefore narrows the blocker without accepting "
            "dynamic order or external superiority."
        ),
    }
    return rows, summary


def write_markdown(rows: list[dict[str, str]], summary: dict) -> None:
    lines = [
        "# Closed-Loop Dynamic Error Floor Audit",
        "",
        "Status: **floor audit only; accepted dynamic order remains zero**",
        "",
        f"- Default policy: `{summary['default_policy']}`.",
        f"- Selected window: `T={summary['selected_t_end']}`, `h=0.02|0.01|0.005`.",
        f"- Velocity/acceleration evidence rows: `{summary['velocity_acceleration_evidence_count']}/{summary['row_count']}`.",
        f"- Position-floor blocker rows: `{summary['position_floor_blocker_count']}/{summary['row_count']}`.",
        f"- Accepted dynamic order rows: `{summary['accepted_dynamic_order_count']}`.",
        f"- External superiority claim: `{summary['external_superiority_claim']}`.",
        "",
        "Reading rule: this audit does not run default `1e-4` rows and does not convert kinematic/reaction rows into accepted dynamic order evidence.",
        "",
        "| Model | Public vel order | Public acc order | Local vel ratio | Local acc ratio | Local residual | Position blocker |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            f"`{row['model']}` | "
            f"{row['public_vel_order']} | "
            f"{row['public_acc_order']} | "
            f"{row['local_vel_error_ratio_vs_public']} | "
            f"{row['local_acc_error_ratio_vs_public']} | "
            f"{row['local_max_dynamics_residual_norm']} | "
            f"{row['blocker']} |"
        )
    lines.append("")
    (RESULTS / "closed_loop_dynamic_error_floor_audit.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    rows, summary = build_audit()
    write_csv(RESULTS / "closed_loop_dynamic_error_floor_audit.csv", rows)
    with (RESULTS / "closed_loop_dynamic_error_floor_audit.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")
    write_markdown(rows, summary)
    print("closed_loop_dynamic_error_floor_audit=written")
    print(f"rows={summary['row_count']}")
    print(f"velocity_acceleration_evidence={summary['velocity_acceleration_evidence_count']}")
    print(f"position_floor_blockers={summary['position_floor_blocker_count']}")
    print(f"accepted_dynamic_order={summary['accepted_dynamic_order_count']}")
    print("external_superiority_claim=False")


if __name__ == "__main__":
    main()
