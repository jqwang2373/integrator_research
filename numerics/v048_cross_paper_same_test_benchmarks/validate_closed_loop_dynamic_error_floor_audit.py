#!/usr/bin/env python3
"""Validate the closed-loop dynamic error floor audit."""

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


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def as_float(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float("nan")


def main() -> int:
    checks = Checks()
    try:
        rows = read_csv(RESULTS / "closed_loop_dynamic_error_floor_audit.csv")
        summary = read_json(RESULTS / "closed_loop_dynamic_error_floor_audit.json")
        report = (RESULTS / "closed_loop_dynamic_error_floor_audit.md").read_text(encoding="utf-8")
    except Exception as exc:  # noqa: BLE001 - concise CLI failure.
        print(f"closed-loop dynamic error floor audit validation: FAIL\n- {exc}")
        return 1

    by_model = {row.get("model"): row for row in rows}
    checks.check(summary.get("schema") == "closed-loop-dynamic-error-floor-audit-v1", "schema changed")
    checks.check(set(summary.get("models", [])) == MODELS, "model set changed")
    checks.check(summary.get("row_count") == 2, "summary row count changed")
    checks.check(len(rows) == 2, "CSV should have two audit rows")
    checks.check(set(by_model) == MODELS, "CSV model set changed")
    checks.check(summary.get("velocity_acceleration_evidence_count") == 2, "velocity/acceleration evidence count changed")
    checks.check(summary.get("position_floor_blocker_count") == 2, "position-floor blocker count changed")
    checks.check(summary.get("accepted_dynamic_order_count") == 0, "accepted dynamic order must stay zero")
    checks.check(summary.get("external_superiority_claim") is False, "must not claim external superiority")
    checks.check(summary.get("same_test_campaign_status") == "not_run", "same-test campaign must remain not_run")
    checks.check(summary.get("default_policy") == "coarse_first_no_default_1e-4", "default policy changed")
    checks.check(summary.get("selected_step_sizes") == [0.02, 0.01, 0.005], "selected step sizes changed")
    checks.check(summary.get("ratio_threshold") == 1.0e-4, "ratio threshold changed")
    checks.check(summary.get("residual_threshold") == 1.0e-12, "residual threshold changed")

    for model in MODELS:
        row = by_model.get(model, {})
        checks.check(
            row.get("status") == "velocity_acceleration_floor_evidence_position_reference_floor_blocks_dynamic_order",
            f"{model} status changed",
        )
        checks.check(row.get("accepted_dynamic_order") == "false", f"{model} accepted flag changed")
        checks.check(row.get("external_superiority_claim_allowed") == "false", f"{model} claim flag changed")
        checks.check(row.get("velocity_acceleration_floor_evidence") == "True", f"{model} should keep velocity/acceleration evidence")
        checks.check(row.get("position_floor_blocker") == "True", f"{model} should keep position-floor blocker")
        checks.check(row.get("public_method") == "rA-public-dynamics", f"{model} public method changed")
        checks.check(row.get("local_method") == "Gauss6/FullVA-local-closed-loop", f"{model} local method changed")
        checks.check(as_float(row.get("local_vel_error_ratio_vs_public", "nan")) < 1.0e-4, f"{model} velocity ratio too large")
        checks.check(as_float(row.get("local_acc_error_ratio_vs_public", "nan")) < 1.0e-4, f"{model} acceleration ratio too large")
        checks.check(as_float(row.get("local_pos_error_ratio_vs_public", "nan")) > 1.0, f"{model} position-floor blocker missing")
        checks.check(as_float(row.get("local_max_dynamics_residual_norm", "nan")) < 1.0e-12, f"{model} residual too large")
        checks.check(math.isfinite(as_float(row.get("public_vel_order", "nan"))), f"{model} public velocity order missing")
        checks.check(math.isfinite(as_float(row.get("public_acc_order", "nan"))), f"{model} public acceleration order missing")
        checks.check("true local dynamic trajectory/order rows" in row.get("next_gate", ""), f"{model} next gate weakened")
        checks.check("kinematic FullVA plus reaction reconstruction" in row.get("blocker", ""), f"{model} blocker weakened")

    checks.check("floor audit only; accepted dynamic order remains zero" in report, "report missing audit boundary")
    checks.check("does not run default `1e-4` rows" in report, "report missing no-default-1e-4 boundary")
    checks.check("does not convert kinematic/reaction rows" in report, "report missing no-acceptance boundary")

    if checks.errors:
        print("closed-loop dynamic error floor audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("closed-loop dynamic error floor audit validation: PASS")
    print(f"rows={summary.get('row_count')}")
    print(f"velocity_acceleration_evidence={summary.get('velocity_acceleration_evidence_count')}")
    print(f"position_floor_blockers={summary.get('position_floor_blocker_count')}")
    print(f"accepted_dynamic_order={summary.get('accepted_dynamic_order_count')}")
    print("external_superiority_claim=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
