#!/usr/bin/env python3
"""Replay-check the embedded four-link/slider-crank local closed-loop rows."""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "v048_report"
RESULTS = ROOT / "results"
SUMMARY_JSON = RESULTS / "closed_loop_local_rows_summary.json"
ROWS_CSV = RESULTS / "closed_loop_local_rows.csv"
MODELS = ("four_link", "slider_crank")
STEP_SIZES = (0.1, 0.05, 0.025)


def read_json(path: Path) -> dict:
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
        number = float(value)
    except (TypeError, ValueError):
        return float("nan")
    return number if math.isfinite(number) else float("nan")


def estimate_order(rows: list[dict[str, str]], key: str) -> float:
    pairs = sorted(
        [(as_float(row["h"]), as_float(row[key])) for row in rows],
        reverse=True,
    )
    pairs = [(h, e) for h, e in pairs if h > 0.0 and e > 0.0]
    if len(pairs) != 3:
        return float("nan")
    x = [math.log(h) for h, _ in pairs]
    y = [math.log(e) for _, e in pairs]
    x_mean = sum(x) / len(x)
    y_mean = sum(y) / len(y)
    denom = sum((item - x_mean) ** 2 for item in x)
    if denom == 0.0:
        return float("nan")
    return sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, y, strict=True)) / denom


def write_outputs(rows: list[dict[str, str]], orders: dict[str, tuple[float, float]]) -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    summary = {
        "schema": "cmame-closed-loop-local-rows-replay-v1",
        "status": "closed_loop_local_rows_replay_checked_not_self_contained_runner",
        "models": list(MODELS),
        "h_values": list(STEP_SIZES),
        "local_rows": len(rows),
        "model_orders": {
            model: {
                "position_order": orders[model][0],
                "velocity_order": orders[model][1],
            }
            for model in MODELS
        },
        "self_contained_simulation_runner": False,
        "source_policy_external_superiority_allowed": False,
        "proof_gap_closed_by_adapter": False,
        "submission_ready": False,
    }
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    fieldnames = [
        "model",
        "h",
        "pos_final_linf",
        "vel_final_linf",
        "status",
        "stage_oracle_used",
        "accepted_dynamic_order",
        "external_superiority_claim_allowed",
        "default_1e-4_required",
    ]
    with ROWS_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def main() -> int:
    summary = read_json(DATA / "closed_loop_true_dynamic_strict_common_reference.json")
    rows = read_csv(DATA / "closed_loop_true_dynamic_strict_common_reference_rows.csv")
    local_rows = [
        row
        for row in rows
        if row.get("source_suite") == "local_true_dynamic_newton"
        and row.get("method") == "Gauss6/FullVA-local-true-dynamic-newton"
    ]
    errors: list[str] = []
    if summary.get("schema") != "closed-loop-true-dynamic-strict-common-reference-v1":
        errors.append("closed-loop strict-common-reference schema changed")
    if summary.get("status") != "strict_common_reference_error_columns_available_not_external_superiority":
        errors.append("closed-loop strict-common-reference status changed")
    if summary.get("local_raw_row_count") != 6 or len(local_rows) != 6:
        errors.append("local closed-loop row count is not 6")
    if set(summary.get("strict_common_reference_available_examples", [])) != set(MODELS):
        errors.append("strict common-reference example set changed")
    if summary.get("external_superiority_claim") is not False:
        errors.append("closed-loop summary overclaims external superiority")
    if summary.get("heavy_numerical_run_invoked") is not False:
        errors.append("closed-loop summary unexpectedly marks a heavy numerical run")

    orders: dict[str, tuple[float, float]] = {}
    for model in MODELS:
        model_rows = sorted(
            [row for row in local_rows if row.get("model") == model],
            key=lambda row: as_float(row["h"]),
            reverse=True,
        )
        if [round(as_float(row["h"]), 12) for row in model_rows] != [round(h, 12) for h in STEP_SIZES]:
            errors.append(f"{model} h-grid changed")
            continue
        for row in model_rows:
            if row.get("status") != "ok":
                errors.append(f"{model} local row status changed")
            if row.get("stage_oracle_used") != "false":
                errors.append(f"{model} unexpectedly uses a stage oracle")
            if row.get("accepted_dynamic_order") != "true":
                errors.append(f"{model} local row lost accepted dynamic-order marker")
            if row.get("external_superiority_claim_allowed") != "false":
                errors.append(f"{model} overclaims external superiority")
            if row.get("default_1e-4_required") != "false":
                errors.append(f"{model} unexpectedly requires default 1e-4 policy")
        pos_order = estimate_order(model_rows, "pos_final_linf")
        vel_order = estimate_order(model_rows, "vel_final_linf")
        orders[model] = (pos_order, vel_order)
        if pos_order <= 5.0 or vel_order <= 5.0:
            errors.append(f"{model} local position/velocity order below threshold")

    if errors:
        print("cmame_closed_loop_local_rows_replay=FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    write_outputs(local_rows, orders)
    print("cmame_closed_loop_local_rows_replay=PASS")
    print("models=four_link,slider_crank")
    print("local_rows=6/6")
    print("summary_json=results/closed_loop_local_rows_summary.json")
    print("rows_csv=results/closed_loop_local_rows.csv")
    print(f"four_link_orders={orders['four_link'][0]:.6f}/{orders['four_link'][1]:.6f}")
    print(f"slider_crank_orders={orders['slider_crank'][0]:.6f}/{orders['slider_crank'][1]:.6f}")
    print("self_contained_simulation_runner=False")
    print("source_policy_external_superiority_allowed=False")
    print("proof_gap_closed_by_adapter=False")
    print("submission_ready=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
