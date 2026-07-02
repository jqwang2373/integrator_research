#!/usr/bin/env python3
"""Validate the closed-loop true-dynamic stage residual audit."""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
MODELS = {"four_link", "slider_crank"}


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def as_float(value: str) -> float:
    return float(value)


def main() -> int:
    checks = Checks()
    try:
        rows = read_csv(RESULTS / "closed_loop_true_dynamic_stage_residual_audit.csv")
        summary = read_json(RESULTS / "closed_loop_true_dynamic_stage_residual_audit.json")
        report = (RESULTS / "closed_loop_true_dynamic_stage_residual_audit.md").read_text(encoding="utf-8")
    except Exception as exc:  # noqa: BLE001 - concise CLI failure.
        print(f"closed-loop true dynamic stage residual audit validation: FAIL\n- {exc}")
        return 1

    checks.check(summary.get("schema") == "closed-loop-true-dynamic-stage-residual-audit-v1", "schema changed")
    checks.check(
        summary.get("status") == "stage_residual_evaluator_verified_stepper_not_implemented",
        "status changed",
    )
    checks.check(summary.get("method") == "Gauss6/FullVA", "method changed")
    checks.check(set(summary.get("models", [])) == MODELS, "model set changed")
    checks.check(summary.get("row_count") == 6, "row count changed")
    checks.check(summary.get("ok_row_count") == 6, "ok row count changed")
    checks.check(summary.get("stage_count_per_model") == 3, "stage count changed")
    checks.check(summary.get("stage_unknown_dim") == 72, "stage unknown dim changed")
    checks.check(summary.get("stage_residual_dim") == 72, "stage residual dim changed")
    checks.check(summary.get("stage_residual_evaluator_implemented") is True, "stage evaluator not implemented")
    checks.check(summary.get("trajectory_stepper_implemented") is False, "trajectory stepper overclaimed")
    checks.check(summary.get("simulate_runner_implemented") is False, "simulate runner overclaimed")
    checks.check(summary.get("accepted_dynamic_order_count") == 0, "dynamic order overclaimed")
    checks.check(summary.get("trajectory_stepper_executed") is False, "trajectory stepper executed")
    checks.check(summary.get("default_policy") == "coarse_first_no_default_1e-4", "default policy changed")
    checks.check(summary.get("strict_public_policy_1e-4_required") is False, "strict 1e-4 overclaimed")
    checks.check(summary.get("default_1e-4_required") is False, "default 1e-4 overclaimed")
    checks.check(summary.get("heavy_numerical_run_invoked") is False, "heavy run invoked")
    checks.check(summary.get("external_superiority_claim") is False, "external superiority overclaimed")
    checks.check(set(summary.get("required_symbols_implemented", [])) == {
        "pack_closed_loop_fullva_stage_vector",
        "unpack_closed_loop_fullva_stage_vector",
        "closed_loop_fullva_stage_residual",
    }, "implemented symbol list changed")
    max_residual = float(summary.get("max_stage_residual_inf", "nan"))
    checks.check(math.isfinite(max_residual) and max_residual < 1.0e-10, "stage residual too large")

    checks.check(len(rows) == 6, "expected three stages for each closed-loop model")
    checks.check({row.get("model") for row in rows} == MODELS, "CSV model set changed")
    for model in MODELS:
        model_rows = [row for row in rows if row.get("model") == model]
        checks.check({row.get("stage_index") for row in model_rows} == {"1", "2", "3"}, f"{model} stage set changed")
    for row in rows:
        label = f"{row.get('model')} stage {row.get('stage_index')}"
        checks.check(row.get("status") == "ok", f"{label} not ok")
        checks.check(row.get("source_state_policy") == "kinematic_oracle_state_for_residual_evaluator_audit", f"{label} source policy changed")
        checks.check(row.get("stage_unknown_dim") == "72", f"{label} unknown dim changed")
        checks.check(row.get("stage_residual_dim") == "72", f"{label} residual dim changed")
        checks.check(as_float(row.get("position_residual_inf", "nan")) < 1.0e-10, f"{label} position residual too large")
        checks.check(as_float(row.get("velocity_residual_inf", "nan")) < 1.0e-10, f"{label} velocity residual too large")
        checks.check(as_float(row.get("acceleration_residual_inf", "nan")) < 1.0e-10, f"{label} acceleration residual too large")
        checks.check(as_float(row.get("newton_euler_residual_inf", "nan")) < 1.0e-10, f"{label} dynamics residual too large")
        checks.check(as_float(row.get("stage_residual_inf", "nan")) < 1.0e-10, f"{label} stage residual too large")
        checks.check(as_float(row.get("pack_unpack_roundtrip_inf", "nan")) < 1.0e-14, f"{label} pack/unpack changed")
        checks.check(row.get("trajectory_stepper_executed") == "false", f"{label} executed stepper")
        checks.check(row.get("stepper_implemented") == "false", f"{label} overclaimed stepper")
        checks.check(row.get("accepted_dynamic_order") == "false", f"{label} accepted dynamic order")
        checks.check(row.get("default_policy") == "coarse_first_no_default_1e-4", f"{label} default policy changed")
        checks.check(row.get("strict_public_policy_1e-4_required") == "false", f"{label} strict 1e-4 changed")
        checks.check(row.get("heavy_numerical_run_invoked") == "false", f"{label} invoked heavy run")

    normalized_report = " ".join(report.split())
    for token in [
        "Closed-Loop True-Dynamic Stage Residual Audit",
        "stage residual evaluator verified; stepper not implemented",
        "stage system on the public/v046 dynamic interface",
        "must not be counted as a trajectory order row",
    ]:
        checks.check(token in report or token in normalized_report, f"report missing token: {token}")

    if checks.errors:
        print("closed-loop true dynamic stage residual audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("closed-loop true dynamic stage residual audit validation: PASS")
    print("rows_ok=6/6")
    print(f"max_stage_residual_inf={max_residual:.6e}")
    print("stage_residual_evaluator_implemented=True")
    print("trajectory_stepper_implemented=False")
    print("default_1e-4=False")
    print("accepted_dynamic_order=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
