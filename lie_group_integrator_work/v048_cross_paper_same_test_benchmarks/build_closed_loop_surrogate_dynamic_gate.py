#!/usr/bin/env python3
"""Build selected-window closed-loop residual-to-error surrogate gate."""

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


def build_gate() -> tuple[list[dict[str, str]], dict]:
    work_rows = read_csv(RESULTS / "gauss6_closed_loop_same_window_work_precision_summary.csv")
    raw_rows = read_csv(RESULTS / "gauss6_fullva_closed_loop_same_window_comparison_rows.csv")

    rows: list[dict[str, str]] = []
    for model in MODELS:
        public = method_row(work_rows, model, PUBLIC_METHOD)
        local = method_row(work_rows, model, LOCAL_METHOD)
        model_raw = [row for row in raw_rows if row.get("model") == model]
        step_values = sorted({as_float(row, "h") for row in model_raw if math.isfinite(as_float(row, "h"))}, reverse=True)
        evidence_paths = (
            "results/gauss6_fullva_closed_loop_same_window_comparison_rows.csv;"
            "results/gauss6_closed_loop_same_window_work_precision_summary.csv"
        )
        rows.append(
            {
                "model": model,
                "policy": "selected_window_residual_to_error_surrogate_not_full_campaign",
                "default_policy": "coarse_first_no_default_1e-4",
                "t_end": public.get("t_end", "0.2"),
                "step_sizes": "|".join(f"{value:.6g}" for value in step_values),
                "reference_method": public.get("reference_method", "rA-public-kinematics"),
                "reference_h": public.get("reference_h", "0.001"),
                "public_method": PUBLIC_METHOD,
                "local_method": LOCAL_METHOD,
                "public_pos_order": public.get("pos_observed_order", "nan"),
                "public_vel_order": public.get("vel_observed_order", "nan"),
                "public_acc_order": public.get("acc_observed_order", "nan"),
                "local_surrogate_pos_order": local.get("pos_observed_order", "nan"),
                "local_surrogate_vel_order": local.get("vel_observed_order", "nan"),
                "local_surrogate_acc_order": local.get("acc_observed_order", "nan"),
                "public_finest_pos_error": public.get("finest_pos_final_linf", "nan"),
                "public_finest_vel_error": public.get("finest_vel_final_linf", "nan"),
                "public_finest_acc_error": public.get("finest_acc_final_linf", "nan"),
                "local_finest_pos_error": local.get("finest_pos_final_linf", "nan"),
                "local_finest_vel_error": local.get("finest_vel_final_linf", "nan"),
                "local_finest_acc_error": local.get("finest_acc_final_linf", "nan"),
                "local_pos_error_ratio_vs_public": local.get("finest_pos_error_ratio_vs_rA", "nan"),
                "local_vel_error_ratio_vs_public": local.get("finest_vel_error_ratio_vs_rA", "nan"),
                "local_acc_error_ratio_vs_public": local.get("finest_acc_error_ratio_vs_rA", "nan"),
                "local_runtime_ratio_vs_public": local.get("finest_runtime_ratio_vs_rA", "nan"),
                "local_max_dynamics_residual_norm": local.get("max_dynamics_residual_norm", "nan"),
                "surrogate_status": "available_not_dynamic_superiority",
                "dynamic_superiority_claim_allowed": "false",
                "acceptance_blocker": (
                    "local row is kinematic FullVA plus reaction reconstruction; promote only after "
                    "a true local dynamic order/work row or a reviewer-defensible residual-to-error "
                    "acceptance argument is added"
                ),
                "evidence_paths": evidence_paths,
            }
        )

    summary = {
        "schema": "closed-loop-surrogate-dynamic-gate-v1",
        "models": list(MODELS),
        "row_count": len(rows),
        "surrogate_available_count": len(rows),
        "accepted_dynamic_order_count": 0,
        "dynamic_superiority_claim": False,
        "same_test_campaign_status": "not_run",
        "default_policy": "coarse_first_no_default_1e-4",
        "selected_t_end": 0.2,
        "selected_step_sizes": [0.02, 0.01, 0.005],
        "selected_reference_h": 0.001,
        "interpretation": (
            "This gate promotes the existing selected-window closed-loop comparison into a "
            "residual-to-error surrogate artifact. It is useful for planning and manuscript "
            "tables, but it does not convert local kinematic/reaction residual rows into "
            "accepted dynamic order/work superiority."
        ),
    }
    return rows, summary


def write_markdown(rows: list[dict[str, str]], summary: dict) -> None:
    lines = [
        "# Closed-Loop Surrogate Dynamic Gate",
        "",
        "Status: **surrogate evidence only; not external superiority**",
        "",
        f"- Models: `{','.join(summary['models'])}`.",
        f"- Selected window: `T={summary['selected_t_end']}`, `h=0.02|0.01|0.005`.",
        f"- Reference: `rA-public-kinematics`, `h={summary['selected_reference_h']}`.",
        f"- Surrogate available rows: `{summary['surrogate_available_count']}`.",
        f"- Accepted dynamic order rows: `{summary['accepted_dynamic_order_count']}`.",
        f"- Default policy: `{summary['default_policy']}`.",
        "",
        "Reading rule: this is the lightweight residual-to-error bridge requested by the coarse-first policy. It does not use default `1e-4` runs and does not close the CMAME same-test superiority gate.",
        "",
        "| Model | Public vel order | Local surrogate vel order | Local vel-error ratio | Local runtime ratio | Max local dynamics residual | Blocker |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            f"`{row['model']}` | "
            f"{row['public_vel_order']} | "
            f"{row['local_surrogate_vel_order']} | "
            f"{row['local_vel_error_ratio_vs_public']} | "
            f"{row['local_runtime_ratio_vs_public']} | "
            f"{row['local_max_dynamics_residual_norm']} | "
            f"{row['acceptance_blocker']} |"
        )
    lines.append("")
    (RESULTS / "closed_loop_surrogate_dynamic_gate.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    rows, summary = build_gate()
    write_csv(RESULTS / "closed_loop_surrogate_dynamic_gate.csv", rows)
    with (RESULTS / "closed_loop_surrogate_dynamic_gate.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")
    write_markdown(rows, summary)
    print("closed_loop_surrogate_dynamic_gate=written")
    print(f"rows={summary['row_count']}")
    print(f"surrogate_available={summary['surrogate_available_count']}")
    print(f"accepted_dynamic_order={summary['accepted_dynamic_order_count']}")
    print("dynamic_superiority_claim=False")


if __name__ == "__main__":
    main()
