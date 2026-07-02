#!/usr/bin/env python3
"""Validate strict common-reference rows for closed-loop true-dynamic comparisons."""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
MODELS = {"four_link", "slider_crank"}
PUBLIC_METHODS = {"rA-public-dynamics", "rp-public-dynamics", "reps-public-dynamics"}
LOCAL_METHOD = "Gauss6/FullVA-local-true-dynamic-newton"
STEP_SIZES = {0.1, 0.05, 0.025}
FIGURE = RESULTS / "closed_loop_true_dynamic_strict_common_reference_work_precision.png"


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def as_float(value: object) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return float("nan")
    return number if math.isfinite(number) else float("nan")


def main() -> int:
    checks = Checks()
    try:
        rows = read_csv(RESULTS / "closed_loop_true_dynamic_strict_common_reference_rows.csv")
        summary_rows = read_csv(RESULTS / "closed_loop_true_dynamic_strict_common_reference_summary.csv")
        summary = read_json(RESULTS / "closed_loop_true_dynamic_strict_common_reference.json")
        report = (RESULTS / "closed_loop_true_dynamic_strict_common_reference.md").read_text(encoding="utf-8")
    except Exception as exc:  # noqa: BLE001 - concise CLI failure.
        print(f"closed-loop true dynamic strict common-reference validation: FAIL\n- {exc}")
        return 1

    checks.check(summary.get("schema") == "closed-loop-true-dynamic-strict-common-reference-v1", "schema changed")
    checks.check(
        summary.get("status") == "strict_common_reference_error_columns_available_not_external_superiority",
        "status changed",
    )
    checks.check(summary.get("default_policy") == "coarse_first_no_default_1e-4", "default policy changed")
    checks.check(set(summary.get("models", [])) == MODELS, "model set changed")
    checks.check(set(summary.get("public_forms", [])) == {"rA", "rp", "reps"}, "public forms changed")
    checks.check(set(float(h) for h in summary.get("step_sizes", [])) == STEP_SIZES, "step sizes changed")
    checks.check(summary.get("t_end") == 0.1, "time window changed")
    checks.check(summary.get("common_reference_method") == "v047_exact_kinematic_endpoint", "common reference changed")
    checks.check(summary.get("common_reference_h") == 0.0125, "common reference h changed")
    checks.check(summary.get("row_count") == 24, "raw row count changed")
    checks.check(summary.get("ok_row_count") == 24, "all strict common-reference rows should be ok")
    checks.check(summary.get("public_raw_row_count") == 18, "public raw row count changed")
    checks.check(summary.get("local_raw_row_count") == 6, "local raw row count changed")
    checks.check(summary.get("summary_row_count") == 8, "summary row count changed")
    checks.check(summary.get("strict_common_reference_available_count") == 2, "availability count changed")
    checks.check(set(summary.get("strict_common_reference_available_examples", [])) == MODELS, "available examples changed")
    checks.check(summary.get("strict_common_reference_gap_count") == 0, "strict common-reference gap should be closed")
    checks.check(summary.get("strict_common_reference_error_columns") is True, "strict common-reference flag changed")
    checks.check(
        set(summary.get("strict_common_reference_columns", []))
        == {"pos_final_linf", "vel_final_linf", "acc_final_linf"},
        "strict common-reference column set changed",
    )
    checks.check(summary.get("acceleration_column_diagnostic") is True, "acceleration diagnostic marker changed")
    checks.check(summary.get("publication_quality_figure_available") is True, "figure availability changed")
    checks.check(summary.get("accepted_external_dynamic_order_examples") == [], "external dynamic order overclaimed")
    checks.check(summary.get("external_superiority_claim") is False, "external superiority overclaimed")
    checks.check(summary.get("default_1e-4_required") is False, "default 1e-4 overclaimed")
    checks.check(summary.get("strict_public_policy_1e-4_required") is False, "strict public 1e-4 overclaimed")
    checks.check(summary.get("heavy_numerical_run_invoked") is False, "heavy run marker changed")

    checks.check(len(rows) == 24, "CSV raw row count changed")
    checks.check({row.get("model") for row in rows} == MODELS, "CSV model set changed")
    checks.check({float(row.get("h", "nan")) for row in rows} == STEP_SIZES, "CSV h set changed")
    checks.check({row.get("status") for row in rows} == {"ok"}, "CSV status changed")
    checks.check({row.get("common_reference_method") for row in rows} == {"v047_exact_kinematic_endpoint"}, "CSV reference changed")
    checks.check({row.get("strict_common_reference_error_columns") for row in rows} == {"true"}, "CSV strict flag changed")
    checks.check({row.get("default_1e-4_required") for row in rows} == {"false"}, "CSV default 1e-4 changed")
    checks.check({row.get("external_superiority_claim_allowed") for row in rows} == {"false"}, "CSV superiority marker changed")
    checks.check({row.get("method") for row in rows} == PUBLIC_METHODS | {LOCAL_METHOD}, "CSV method set changed")

    for model in MODELS:
        model_rows = [row for row in rows if row.get("model") == model]
        checks.check(len(model_rows) == 12, f"{model} raw row count changed")
        local = [row for row in model_rows if row.get("method") == LOCAL_METHOD]
        public = [row for row in model_rows if row.get("method") in PUBLIC_METHODS]
        checks.check(len(local) == 3, f"{model} local row count changed")
        checks.check(len(public) == 9, f"{model} public row count changed")
        checks.check({row.get("accepted_dynamic_order") for row in local} == {"true"}, f"{model} local order flag changed")
        checks.check({row.get("accepted_dynamic_order") for row in public} == {"false"}, f"{model} public order flag changed")
        checks.check(all(as_float(row.get("runtime_sec")) > 0.0 for row in model_rows), f"{model} runtime missing")
        checks.check(all(as_float(row.get("pos_final_linf")) > 0.0 for row in model_rows), f"{model} position error missing")
        checks.check(all(as_float(row.get("vel_final_linf")) > 0.0 for row in model_rows), f"{model} velocity error missing")
        checks.check(all(as_float(row.get("reference_floor_pos_linf")) < 1.0e-5 for row in model_rows), f"{model} position reference floor too high")
        checks.check(all(as_float(row.get("reference_floor_vel_linf")) < 1.0e-5 for row in model_rows), f"{model} velocity reference floor too high")

    checks.check(len(summary_rows) == 8, "summary CSV row count changed")
    for model in MODELS:
        model_summary = [row for row in summary_rows if row.get("model") == model]
        checks.check(len(model_summary) == 4, f"{model} summary row count changed")
        checks.check({row.get("method") for row in model_summary} == PUBLIC_METHODS | {LOCAL_METHOD}, f"{model} summary methods changed")
        local_summary = [row for row in model_summary if row.get("method") == LOCAL_METHOD][0]
        checks.check(local_summary.get("accepted_dynamic_order") == "true", f"{model} local summary order changed")
        checks.check(as_float(local_summary.get("pos_observed_order")) >= 4.5, f"{model} local pos order too low")
        checks.check(as_float(local_summary.get("vel_observed_order")) >= 4.5, f"{model} local vel order too low")

    checks.check(FIGURE.exists() and FIGURE.stat().st_size > 10_000, "strict common-reference figure missing or too small")
    for token in [
        "Closed-Loop True-Dynamic Strict Common Reference",
        "Strict common-reference examples available: `2`",
        "Strict common-reference examples missing: `0`",
        "Common reference: `v047_exact_kinematic_endpoint`",
        "Publication figure available: `True`",
        "External superiority claim: `False`",
    ]:
        checks.check(token in report, f"report missing token: {token}")

    if checks.errors:
        print("closed-loop true dynamic strict common-reference validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("closed-loop true dynamic strict common-reference validation: PASS")
    print("rows_ok=24/24")
    print("strict_common_reference_available=2/2")
    print("strict_common_reference_gap=0")
    print("figure=closed_loop_true_dynamic_strict_common_reference_work_precision.png")
    print("default_1e-4=False")
    print("external_superiority_claim=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
