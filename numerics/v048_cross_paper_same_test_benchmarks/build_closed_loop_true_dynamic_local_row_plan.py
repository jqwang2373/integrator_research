#!/usr/bin/env python3
"""Build a plan-only closed-loop true-dynamic local row contract.

This script does not run any mechanism simulation. It converts the open
four_link/slider_crank dynamic-order blocker into explicit coarse-first row
contracts so later execution can be sharded without accidentally launching a
strict public-policy 1e-4 campaign.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
MODELS = ("four_link", "slider_crank")
STEPS = (0.1, 0.05, 0.025)
REFERENCE_H = 0.0125
METRICS = (
    "position_error",
    "velocity_error",
    "acceleration_error",
    "observed_order",
    "runtime",
    "newton_iterations",
    "constraint_drift",
)
METHOD_ROWS = (
    ("Gauss6/FullVA", "local_dynamic_target", "local_closed_loop_dynamic_dae_gauss6_fullva_runner", "true"),
    ("rA", "public_baseline_comparator", "ra2021_public_dynamic_runner", "false"),
    ("rp", "public_baseline_comparator", "ra2021_public_dynamic_runner", "false"),
    ("reps", "public_baseline_comparator", "ra2021_public_dynamic_runner", "false"),
)
OUT_CSV = RESULTS / "closed_loop_true_dynamic_local_row_plan.csv"
OUT_JSON = RESULTS / "closed_loop_true_dynamic_local_row_plan.json"
OUT_MD = RESULTS / "closed_loop_true_dynamic_local_row_plan.md"


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def h_token(value: float) -> str:
    return f"{value:.6g}".replace(".", "p").replace("-", "m")


def method_token(method: str) -> str:
    return method.lower().replace("/", "_").replace("-", "_")


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError("refusing to write an empty true-dynamic row plan")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def build_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for model in MODELS:
        for method, role, required_runner, new_code_required in METHOD_ROWS:
            for step in STEPS:
                rows.append(
                    {
                        "row_id": (
                            "closed_loop_true_dynamic_local_plan_"
                            f"{model}_{method_token(method)}_h{h_token(step)}"
                        ),
                        "model": model,
                        "suite": "ra2021_closed_loop_same_test",
                        "row_role": role,
                        "method": method,
                        "step_size": f"{step:.17g}",
                        "reference_h": f"{REFERENCE_H:.17g}",
                        "time_window": "coarse_first_selected_window_before_strict_public_policy",
                        "metrics": "|".join(METRICS),
                        "required_runner": required_runner,
                        "new_code_required": new_code_required,
                        "parallel_shard_key": f"{model}:{method_token(method)}:h{h_token(step)}",
                        "execution_status": "not_run",
                        "plan_only": "true",
                        "default_policy": "coarse_first_no_default_1e-4",
                        "strict_public_policy_1e-4_required": "false",
                        "heavy_numerical_run_invoked": "false",
                        "true_dynamic_local_row_available": "false" if role == "local_dynamic_target" else "not_applicable",
                        "accepted_dynamic_order": "false",
                        "external_superiority_claim_allowed": "false",
                        "blocking_reason": (
                            "local true dynamic DAE runner is not implemented"
                            if role == "local_dynamic_target"
                            else "public comparator row is planned only until local dynamic rows exist"
                        ),
                    }
                )
    return rows


def write_markdown(summary: dict, rows: list[dict[str, object]]) -> None:
    lines = [
        "# Closed-Loop True-Dynamic Local Row Plan",
        "",
        "Status: **plan only; no numerical rows have been run**",
        "",
        f"- Default policy: `{summary['default_policy']}`.",
        f"- Step sizes: `{summary['step_sizes']}` with reference `{summary['reference_h']}`.",
        f"- Plan rows: `{summary['row_count']}`.",
        f"- Local true-dynamic target rows: `{summary['local_target_row_count']}`.",
        f"- Public comparator rows: `{summary['public_comparator_row_count']}`.",
        f"- Strict public `1e-4` required: `{summary['strict_public_policy_1e-4_required']}`.",
        f"- Heavy numerical run invoked: `{summary['heavy_numerical_run_invoked']}`.",
        "",
        "This artifact is the next-row contract for the closed-loop",
        "`four_link` and `slider_crank` blocker. It deliberately uses",
        "`h=[0.1,0.05,0.025]`, `reference_h=0.0125`, and `plan_only=true`.",
        "It is not a source-paper `1e-4` reproduction campaign.",
        "",
        "| Model | Method | Role | h | Runner | New code | Execution |",
        "|---|---|---|---:|---|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            f"`{row['model']}` | `{row['method']}` | `{row['row_role']}` | "
            f"`{row['step_size']}` | `{row['required_runner']}` | "
            f"`{row['new_code_required']}` | `{row['execution_status']}` |"
        )
    lines.extend(
        [
            "",
            "## Acceptance Boundary",
            "",
            "The local `Gauss6/FullVA` rows remain unaccepted until a true",
            "closed-loop dynamic DAE runner solves the dynamic trajectory rather",
            "than replaying kinematic constraints plus reaction reconstruction.",
            "The public rows are comparator rows, not a replacement for the local",
            "dynamic-order evidence. No row in this plan permits an external",
            "superiority claim.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    closure = read_json(RESULTS / "closed_loop_dynamic_order_closure_contract.json")
    feasibility = read_json(RESULTS / "closed_loop_true_dynamic_row_feasibility_audit.json")
    rows = build_rows()
    local_rows = [row for row in rows if row["row_role"] == "local_dynamic_target"]
    public_rows = [row for row in rows if row["row_role"] == "public_baseline_comparator"]
    summary = {
        "schema": "closed-loop-true-dynamic-local-row-plan-v1",
        "status": "plan_only_not_run",
        "execution_status": "not_run",
        "plan_only": True,
        "default_policy": "coarse_first_no_default_1e-4",
        "models": list(MODELS),
        "local_method": "Gauss6/FullVA",
        "public_baselines": ["rA", "rp", "reps"],
        "step_sizes": list(STEPS),
        "reference_h": REFERENCE_H,
        "time_window": "coarse_first_selected_window_before_strict_public_policy",
        "metrics": list(METRICS),
        "row_count": len(rows),
        "local_target_row_count": len(local_rows),
        "public_comparator_row_count": len(public_rows),
        "true_dynamic_local_rows_available": 0,
        "accepted_dynamic_order_count": 0,
        "strict_public_policy_1e-4_required": False,
        "default_1e-4_required": False,
        "heavy_numerical_run_invoked": False,
        "external_superiority_claim": False,
        "new_code_required_before_execution": True,
        "required_new_runner": "local_closed_loop_dynamic_dae_gauss6_fullva_runner",
        "parallelization": "split_by_model_method_and_step",
        "source_inputs": {
            "closure_contract_schema": closure.get("schema"),
            "feasibility_audit_schema": feasibility.get("schema"),
            "missing_dynamic_order_models": closure.get("missing_dynamic_order_models"),
            "current_local_row_kind": feasibility.get("current_local_row_kind"),
        },
        "do_not_run": [
            "v047_cylindrical_chain_pipeline/run_v047.py",
            "strict_public_policy_1e-4_without_explicit_opt_in",
            "residual_only_surrogate_as_dynamic_order",
        ],
        "interpretation": (
            "This is a row contract only. It closes no dynamic-order claim; it prevents "
            "the next work item from drifting into default 1e-4 source-policy runs."
        ),
    }
    write_csv(OUT_CSV, rows)
    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")
    write_markdown(summary, rows)
    print("closed_loop_true_dynamic_local_row_plan=written")
    print("status=plan_only_not_run")
    print(f"row_count={len(rows)}")
    print(f"local_target_rows={len(local_rows)}")
    print(f"public_comparator_rows={len(public_rows)}")
    print("default_1e-4=False")
    print("heavy_numerical_run_invoked=False")
    print("accepted_dynamic_order=0")


if __name__ == "__main__":
    main()
