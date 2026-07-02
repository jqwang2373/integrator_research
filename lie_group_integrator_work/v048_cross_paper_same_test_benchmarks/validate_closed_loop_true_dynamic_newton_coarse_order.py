#!/usr/bin/env python3
"""Validate closed-loop true-dynamic Newton coarse order rows."""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
MODELS = {"four_link", "slider_crank"}
STEP_SIZES = {0.1, 0.05, 0.025}


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
        rows = read_csv(RESULTS / "closed_loop_true_dynamic_newton_coarse_order_rows.csv")
        summary = read_json(RESULTS / "closed_loop_true_dynamic_newton_coarse_order.json")
        report = (RESULTS / "closed_loop_true_dynamic_newton_coarse_order.md").read_text(encoding="utf-8")
    except Exception as exc:  # noqa: BLE001 - concise CLI failure.
        print(f"closed-loop true dynamic Newton coarse order validation: FAIL\n- {exc}")
        return 1

    checks.check(summary.get("schema") == "closed-loop-true-dynamic-newton-coarse-order-v1", "schema changed")
    checks.check(
        summary.get("status") == "coarse_true_dynamic_order_candidates_available_not_external_superiority",
        "status changed",
    )
    checks.check(summary.get("method") == "Gauss6/FullVA", "method changed")
    checks.check(set(summary.get("models", [])) == MODELS, "model set changed")
    checks.check(summary.get("row_count") == 6, "row count changed")
    checks.check(summary.get("ok_row_count") == 6, "ok count changed")
    checks.check(set(float(h) for h in summary.get("step_sizes", [])) == STEP_SIZES, "step sizes changed")
    checks.check(summary.get("t_end") == 0.1, "time window changed")
    checks.check(summary.get("stage_count_per_step") == 3, "stage count changed")
    checks.check(summary.get("stage_unknown_dim") == 72, "stage unknown dim changed")
    checks.check(summary.get("stage_residual_dim") == 72, "stage residual dim changed")
    checks.check(summary.get("stage_predictor_policy") == "start_extrapolated_no_stage_oracle", "predictor changed")
    checks.check(summary.get("stage_oracle_used") is False, "stage oracle overclaimed")
    checks.check(summary.get("simulate_runner_implemented") is True, "simulate runner not recorded")
    checks.check(summary.get("convergence_sweep_run") is True, "convergence sweep not recorded")
    checks.check(summary.get("accepted_dynamic_order_count") == 2, "dynamic order candidates not accepted")
    checks.check(summary.get("default_policy") == "coarse_first_no_default_1e-4", "default policy changed")
    checks.check(summary.get("strict_public_policy_1e-4_required") is False, "strict 1e-4 overclaimed")
    checks.check(summary.get("default_1e-4_required") is False, "default 1e-4 overclaimed")
    checks.check(summary.get("heavy_numerical_run_invoked") is False, "heavy run invoked")
    checks.check(summary.get("external_superiority_claim") is False, "external superiority overclaimed")

    model_summaries = summary.get("model_summaries", {})
    checks.check(set(model_summaries) == MODELS, "model summaries changed")
    for model in MODELS:
        item = model_summaries.get(model, {})
        checks.check(item.get("row_count") == 3, f"{model} row count changed")
        checks.check(item.get("ok_row_count") == 3, f"{model} ok row count changed")
        checks.check(item.get("accepted_dynamic_order_candidate") is True, f"{model} not accepted")
        for key in [
            "pos_observed_order",
            "orientation_observed_order",
            "vel_observed_order",
            "omega_observed_order",
            "min_primary_order",
        ]:
            value = float(item.get(key, "nan"))
            checks.check(math.isfinite(value), f"{model} {key} not finite")
            checks.check(value >= 4.5, f"{model} {key} below acceptance threshold")
        checks.check(float(item.get("acc_observed_order", "nan")) < 2.0, f"{model} acceleration diagnostic unexpectedly changed")

    checks.check(len(rows) == 6, "CSV row count changed")
    checks.check({row.get("model") for row in rows} == MODELS, "CSV model set changed")
    for model in MODELS:
        model_rows = [row for row in rows if row.get("model") == model]
        checks.check({float(row.get("h", "nan")) for row in model_rows} == STEP_SIZES, f"{model} h set changed")
    for row in rows:
        label = f"{row.get('model')} h={row.get('h')}"
        checks.check(row.get("status") == "ok", f"{label} status changed")
        checks.check(row.get("step_policy") == "non_oracle_newton_multistep_coarse_order_candidate", f"{label} policy changed")
        checks.check(row.get("stage_oracle_used") == "false", f"{label} used stage oracle")
        checks.check(row.get("stage_count_per_step") == "3", f"{label} stage count changed")
        checks.check(row.get("stage_unknown_dim") == "72", f"{label} stage unknown dim changed")
        checks.check(row.get("stage_residual_dim") == "72", f"{label} stage residual dim changed")
        checks.check(as_float(row.get("max_stage_residual_inf", "nan")) < 1.0e-8, f"{label} stage residual too large")
        checks.check(row.get("all_stages_converged") == "true", f"{label} did not converge")
        checks.check(int(row.get("total_stage_newton_iterations", "0")) > 0, f"{label} did not run Newton")
        checks.check(row.get("trajectory_stepper_executed") == "true", f"{label} did not execute trajectory stepper")
        checks.check(row.get("simulate_runner_implemented") == "true", f"{label} simulate runner flag changed")
        checks.check(row.get("accepted_dynamic_order") == "true", f"{label} dynamic order flag changed")
        checks.check(row.get("convergence_sweep_run") == "true", f"{label} convergence sweep flag changed")
        checks.check(row.get("default_policy") == "coarse_first_no_default_1e-4", f"{label} default policy changed")
        checks.check(row.get("strict_public_policy_1e-4_required") == "false", f"{label} strict 1e-4 changed")
        checks.check(row.get("default_1e-4_required") == "false", f"{label} default 1e-4 changed")
        checks.check(row.get("heavy_numerical_run_invoked") == "false", f"{label} invoked heavy run")

    for token in [
        "Closed-Loop True-Dynamic Newton Coarse Order",
        "Accepted dynamic-order candidates: `2`",
        "position, orientation, linear velocity, and",
        "angular velocity orders",
        "public-baseline work/precision comparison",
        "External superiority claim: `False`",
    ]:
        checks.check(token in report, f"report missing token: {token}")

    if checks.errors:
        print("closed-loop true dynamic Newton coarse order validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("closed-loop true dynamic Newton coarse order validation: PASS")
    print("rows_ok=6/6")
    print("accepted_dynamic_order=2")
    for model in sorted(MODELS):
        item = model_summaries[model]
        print(
            f"{model}_orders="
            f"{float(item['pos_observed_order']):.3f}/"
            f"{float(item['orientation_observed_order']):.3f}/"
            f"{float(item['vel_observed_order']):.3f}/"
            f"{float(item['omega_observed_order']):.3f}"
        )
    print("stage_oracle_used=False")
    print("convergence_sweep_run=True")
    print("default_1e-4=False")
    print("external_superiority_claim=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
