#!/usr/bin/env python3
"""Validate the TFE source-pendulum same-test work/precision artifact."""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
RAW_CSV = RESULTS / "tfe_source_pendulum_same_test_work_precision_rows.csv"
SUMMARY_CSV = RESULTS / "tfe_source_pendulum_same_test_work_precision_summary.csv"
SUMMARY_JSON = RESULTS / "tfe_source_pendulum_same_test_work_precision.json"
SUMMARY_MD = RESULTS / "tfe_source_pendulum_same_test_work_precision.md"
FIGURE = RESULTS / "tfe_source_pendulum_same_test_work_precision.png"
EXPECTED_METHODS = {
    "Newmark_beta",
    "trapezoidal",
    "TFE_m1",
    "TFE_m2",
    "TFE_m3_GL",
    "Gauss6_FullVA",
}
STEP_SIZES = {0.1, 0.05, 0.025}


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
        out = float(value)
    except (TypeError, ValueError):
        return float("nan")
    return out if math.isfinite(out) else float("nan")


def main() -> int:
    checks = Checks()
    try:
        rows = read_csv(RAW_CSV)
        summary_rows = read_csv(SUMMARY_CSV)
        summary = read_json(SUMMARY_JSON)
        report = SUMMARY_MD.read_text(encoding="utf-8")
    except Exception as exc:  # noqa: BLE001
        print(f"TFE source-pendulum same-test work/precision validation: FAIL\n- {exc}")
        return 1

    checks.check(summary.get("schema") == "tfe-source-pendulum-same-test-work-precision-v1", "schema changed")
    checks.check(
        summary.get("status") == "same_test_candidate_work_precision_available_not_source_policy",
        "status changed",
    )
    checks.check(summary.get("same_test_work_precision_available") is True, "availability marker missing")
    checks.check(summary.get("example") == "source_pendulum", "example changed")
    checks.check(summary.get("case_id") == "frictionless_pendulum_same_test_work_precision", "case changed")
    checks.check(summary.get("t_final") == 1.0, "time horizon changed")
    checks.check(summary.get("reference_method") == "rk4_reference", "reference method changed")
    checks.check(summary.get("reference_h") == 0.00025, "reference h changed")
    checks.check(set(float(item) for item in summary.get("step_sizes", [])) == STEP_SIZES, "step sizes changed")
    checks.check(set(summary.get("candidate_methods", [])) == EXPECTED_METHODS, "method set changed")
    checks.check(summary.get("method_count") == 6, "method count changed")
    checks.check(summary.get("row_count") == 18, "raw row count changed")
    checks.check(summary.get("ok_row_count") == 18, "not all raw rows ok")
    checks.check(summary.get("summary_row_count") == 6, "summary row count changed")
    checks.check(summary.get("figure_available") is True, "figure availability marker missing")
    checks.check(FIGURE.exists() and FIGURE.stat().st_size > 10_000, "figure missing or too small")
    checks.check(summary.get("source_policy_method_runner_equivalent") is False, "method equivalence overclaimed")
    checks.check(summary.get("source_policy_rows_completed") == 0, "source-policy rows overclosed")
    checks.check(summary.get("fullva_dae_source_policy_equivalent") is False, "FullVA DAE source-policy equivalence overclaimed")
    checks.check(summary.get("external_superiority_claim") is False, "external superiority overclaimed")
    checks.check(summary.get("external_superiority_claim_allowed") is False, "external superiority allowed")
    checks.check(summary.get("default_1e-4_required") is False, "default 1e-4 unexpectedly required")
    checks.check(summary.get("heavy_numerical_run_invoked") is False, "heavy run unexpectedly invoked")
    checks.check(as_float(summary.get("gauss6_velocity_pairwise_order_floor")) > 5.5, "Gauss6 velocity order floor too low")
    checks.check(as_float(summary.get("gauss6_coordinate_pairwise_order_floor")) > 5.5, "Gauss6 coordinate order floor too low")
    checks.check(as_float(summary.get("gauss6_frobenius_pairwise_order_floor")) > 5.5, "Gauss6 Frobenius order floor too low")
    checks.check(as_float(summary.get("tfe_m3_velocity_pairwise_order_floor")) > 4.5, "TFE m=3 velocity order floor too low")
    checks.check(as_float(summary.get("tfe_m3_coordinate_pairwise_order_floor")) > 4.5, "TFE m=3 coordinate order floor too low")

    checks.check(len(rows) == 18, "CSV raw row count changed")
    checks.check({row.get("source_method") for row in rows} == EXPECTED_METHODS, "CSV method set changed")
    checks.check({float(row.get("h", "nan")) for row in rows} == STEP_SIZES, "CSV h-grid changed")
    checks.check({row.get("status") for row in rows} == {"ok"}, "CSV status changed")
    checks.check({row.get("frictional") for row in rows} == {"false"}, "CSV friction policy changed")
    checks.check({row.get("source_policy_method_runner_equivalent") for row in rows} == {"false"}, "CSV method equivalence overclaimed")
    checks.check({row.get("source_policy_row_completed") for row in rows} == {"false"}, "CSV source-policy row overclosed")
    checks.check({row.get("external_superiority_claim_allowed") for row in rows} == {"false"}, "CSV external superiority allowed")
    checks.check(
        {row.get("accepted_use") for row in rows} == {"same_test_candidate_work_precision_not_source_policy"},
        "CSV accepted-use marker changed",
    )
    for source_method in EXPECTED_METHODS:
        group = [row for row in rows if row.get("source_method") == source_method]
        checks.check(len(group) == 3, f"{source_method} raw row count changed")
        checks.check(all(as_float(row.get("runtime_sec")) > 0.0 for row in group), f"{source_method} runtime missing")
        checks.check(all(as_float(row.get("max_newton_residual_norm")) < 1.0e-8 for row in group), f"{source_method} residual too large")
        checks.check(all(as_float(row.get("velocity_error_v")) > 0.0 for row in group), f"{source_method} velocity error missing")
        checks.check(all(as_float(row.get("coordinate_error_q")) > 0.0 for row in group), f"{source_method} coordinate error missing")
        checks.check(all(as_float(row.get("work_units_newton_iterations")) >= 0.0 for row in group), f"{source_method} work units missing")

    checks.check(len(summary_rows) == 6, "summary CSV row count changed")
    checks.check({row.get("source_method") for row in summary_rows} == EXPECTED_METHODS, "summary method set changed")
    for row in summary_rows:
        method = row.get("source_method")
        checks.check(row.get("ok_row_count") == "3", f"{method} summary ok count changed")
        checks.check(row.get("source_policy_row_completed") == "false", f"{method} summary overclosed source-policy row")
        checks.check(
            row.get("external_superiority_claim_allowed") == "false",
            f"{method} summary external superiority allowed",
        )
        checks.check(row.get("coordinate_error_decreased") == "true", f"{method} coordinate error not decreasing")
        checks.check(row.get("velocity_error_decreased") == "true", f"{method} velocity error not decreasing")
        checks.check(row.get("frobenius_error_decreased") == "true", f"{method} Frobenius error not decreasing")
        if method in {"Newmark_beta", "trapezoidal"}:
            checks.check(as_float(row.get("velocity_pairwise_order_floor")) > 1.75, f"{method} velocity order too low")
        if method == "TFE_m2":
            checks.check(as_float(row.get("velocity_pairwise_order_floor")) > 2.5, "TFE m=2 velocity order too low")
        if method == "TFE_m3_GL":
            checks.check(as_float(row.get("velocity_pairwise_order_floor")) > 4.5, "TFE m=3 velocity order too low")
        if method == "Gauss6_FullVA":
            checks.check(as_float(row.get("velocity_pairwise_order_floor")) > 5.5, "Gauss6 velocity order too low")

    for token in [
        "TFE Source-Pendulum Same-Test Work/Precision",
        "Rows: `18/18` ok",
        "Source-policy rows completed: `0`",
        "External superiority claim: `False`",
        "candidate-level",
        "same-test evidence only",
    ]:
        checks.check(token in report, f"report missing token: {token}")

    if checks.errors:
        print("TFE source-pendulum same-test work/precision validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("TFE source-pendulum same-test work/precision validation: PASS")
    print("rows_ok=18/18")
    print("methods=6")
    print(f"gauss6_velocity_order_floor={summary.get('gauss6_velocity_pairwise_order_floor'):.3f}")
    print(f"tfe_m3_velocity_order_floor={summary.get('tfe_m3_velocity_pairwise_order_floor'):.3f}")
    print("source_policy_rows_completed=0")
    print("external_superiority_claim=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
