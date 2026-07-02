#!/usr/bin/env python3
"""Validate the closed-loop true-dynamic non-oracle Newton stage smoke artifact."""

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
        rows = read_csv(RESULTS / "closed_loop_true_dynamic_newton_stage_smoke.csv")
        summary = read_json(RESULTS / "closed_loop_true_dynamic_newton_stage_smoke.json")
        report = (RESULTS / "closed_loop_true_dynamic_newton_stage_smoke.md").read_text(encoding="utf-8")
    except Exception as exc:  # noqa: BLE001 - concise CLI failure.
        print(f"closed-loop true dynamic Newton stage smoke validation: FAIL\n- {exc}")
        return 1

    checks.check(summary.get("schema") == "closed-loop-true-dynamic-newton-stage-smoke-v1", "schema changed")
    checks.check(
        summary.get("status") == "non_oracle_stage_newton_smoke_passed_order_rows_not_run",
        "status changed",
    )
    checks.check(summary.get("method") == "Gauss6/FullVA", "method changed")
    checks.check(set(summary.get("models", [])) == MODELS, "model set changed")
    checks.check(summary.get("row_count") == 2, "row count changed")
    checks.check(summary.get("ok_row_count") == 2, "ok count changed")
    checks.check(summary.get("stage_count") == 3, "stage count changed")
    checks.check(summary.get("stage_unknown_dim") == 72, "stage unknown dim changed")
    checks.check(summary.get("stage_residual_dim") == 72, "stage residual dim changed")
    checks.check(summary.get("step_policy") == "non_oracle_newton_one_step_smoke_not_order", "step policy changed")
    checks.check(
        summary.get("stage_predictor_policy") == "start_extrapolated_no_stage_oracle",
        "stage predictor policy changed",
    )
    checks.check(summary.get("stage_oracle_used") is False, "stage oracle overclaimed")
    checks.check(summary.get("trajectory_stepper_implemented") is True, "stepper not recorded")
    checks.check(summary.get("trajectory_stepper_executed") is True, "stepper did not execute")
    checks.check(summary.get("simulate_runner_implemented") is False, "simulate runner overclaimed")
    checks.check(summary.get("accepted_dynamic_order_count") == 0, "dynamic order overclaimed")
    checks.check(summary.get("convergence_sweep_run") is False, "convergence sweep unexpectedly run")
    checks.check(summary.get("default_policy") == "coarse_first_no_default_1e-4", "default policy changed")
    checks.check(summary.get("strict_public_policy_1e-4_required") is False, "strict 1e-4 overclaimed")
    checks.check(summary.get("default_1e-4_required") is False, "default 1e-4 overclaimed")
    checks.check(summary.get("heavy_numerical_run_invoked") is False, "heavy run invoked")
    checks.check(summary.get("external_superiority_claim") is False, "external superiority overclaimed")
    checks.check(math.isfinite(float(summary.get("max_initial_stage_residual_inf", "nan"))), "initial residual not finite")
    checks.check(math.isfinite(float(summary.get("max_stage_residual_inf", "nan"))), "stage residual not finite")
    checks.check(float(summary.get("max_stage_residual_inf", "nan")) < 1.0e-8, "stage residual too large")
    checks.check(math.isfinite(float(summary.get("max_endpoint_pos_error_inf", "nan"))), "endpoint position error not finite")
    checks.check(math.isfinite(float(summary.get("max_endpoint_vel_error_inf", "nan"))), "endpoint velocity error not finite")

    checks.check(len(rows) == 2, "expected one Newton smoke row per missing closed-loop model")
    checks.check({row.get("model") for row in rows} == MODELS, "CSV model set changed")
    for row in rows:
        model = row.get("model", "<missing>")
        checks.check(row.get("status") == "ok", f"{model} row not ok")
        checks.check(row.get("step_policy") == "non_oracle_newton_one_step_smoke_not_order", f"{model} step policy changed")
        checks.check(
            row.get("stage_predictor_policy") == "start_extrapolated_no_stage_oracle",
            f"{model} predictor changed",
        )
        checks.check(row.get("stage_oracle_used") == "false", f"{model} used stage oracle")
        checks.check(row.get("stage_count") == "3", f"{model} stage count changed")
        checks.check(row.get("stage_unknown_dim") == "72", f"{model} stage unknown dim changed")
        checks.check(row.get("stage_residual_dim") == "72", f"{model} stage residual dim changed")
        checks.check(as_float(row.get("max_initial_stage_residual_inf", "nan")) > 1.0e-8, f"{model} initial residual not diagnostic")
        checks.check(as_float(row.get("max_stage_residual_inf", "nan")) < 1.0e-8, f"{model} stage residual too large")
        checks.check(int(row.get("total_stage_newton_iterations", "0")) > 0, f"{model} did not run Newton")
        checks.check(row.get("all_stages_converged") == "true", f"{model} did not converge")
        checks.check(math.isfinite(as_float(row.get("endpoint_pos_error_inf", "nan"))), f"{model} endpoint position error not finite")
        checks.check(math.isfinite(as_float(row.get("endpoint_vel_error_inf", "nan"))), f"{model} endpoint velocity error not finite")
        checks.check(row.get("trajectory_stepper_executed") == "true", f"{model} did not execute stepper")
        checks.check(row.get("simulate_runner_implemented") == "false", f"{model} simulate runner overclaimed")
        checks.check(row.get("accepted_dynamic_order") == "false", f"{model} dynamic order accepted")
        checks.check(row.get("convergence_sweep_run") == "false", f"{model} convergence sweep overclaimed")
        checks.check(row.get("default_policy") == "coarse_first_no_default_1e-4", f"{model} default policy changed")
        checks.check(row.get("strict_public_policy_1e-4_required") == "false", f"{model} strict 1e-4 changed")
        checks.check(row.get("default_1e-4_required") == "false", f"{model} default 1e-4 changed")
        checks.check(row.get("heavy_numerical_run_invoked") == "false", f"{model} invoked heavy run")

    normalized_report = " ".join(report.split())
    for token in [
        "Closed-Loop True-Dynamic Newton Stage Smoke",
        "non-oracle stage Newton smoke passed; order rows not run",
        "No stage-time kinematic oracle",
        "not a convergence sweep",
        "must not be counted as order",
    ]:
        checks.check(token in report or token in normalized_report, f"report missing token: {token}")

    if checks.errors:
        print("closed-loop true dynamic Newton stage smoke validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("closed-loop true dynamic Newton stage smoke validation: PASS")
    print("rows_ok=2/2")
    print(f"max_initial_stage_residual_inf={float(summary['max_initial_stage_residual_inf']):.6e}")
    print(f"max_stage_residual_inf={float(summary['max_stage_residual_inf']):.6e}")
    print("stage_oracle_used=False")
    print("trajectory_stepper_executed=True")
    print("convergence_sweep_run=False")
    print("default_1e-4=False")
    print("accepted_dynamic_order=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
