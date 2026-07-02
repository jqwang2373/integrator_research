#!/usr/bin/env python3
"""Validate the selected-window closed-loop surrogate dynamic gate."""

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
        rows = read_csv(RESULTS / "closed_loop_surrogate_dynamic_gate.csv")
        summary = read_json(RESULTS / "closed_loop_surrogate_dynamic_gate.json")
        report = (RESULTS / "closed_loop_surrogate_dynamic_gate.md").read_text(encoding="utf-8")
    except Exception as exc:  # noqa: BLE001 - concise CLI failure.
        print(f"closed-loop surrogate dynamic gate validation: FAIL\n- {exc}")
        return 1

    by_model = {row.get("model"): row for row in rows}
    checks.check(summary.get("schema") == "closed-loop-surrogate-dynamic-gate-v1", "schema changed")
    checks.check(set(summary.get("models", [])) == MODELS, "model set changed")
    checks.check(summary.get("row_count") == 2, "summary row count changed")
    checks.check(len(rows) == 2, "CSV should have one row per closed-loop model")
    checks.check(set(by_model) == MODELS, "CSV model set changed")
    checks.check(summary.get("surrogate_available_count") == 2, "surrogate availability count changed")
    checks.check(summary.get("accepted_dynamic_order_count") == 0, "accepted dynamic order count must stay zero")
    checks.check(summary.get("dynamic_superiority_claim") is False, "must not claim dynamic superiority")
    checks.check(summary.get("same_test_campaign_status") == "not_run", "same-test campaign must remain not_run")
    checks.check(summary.get("default_policy") == "coarse_first_no_default_1e-4", "default policy changed")
    checks.check(summary.get("selected_step_sizes") == [0.02, 0.01, 0.005], "selected step sizes changed")
    checks.check(summary.get("selected_reference_h") == 0.001, "selected reference h changed")

    for model in MODELS:
        row = by_model.get(model, {})
        checks.check(row.get("surrogate_status") == "available_not_dynamic_superiority", f"{model} status changed")
        checks.check(row.get("dynamic_superiority_claim_allowed") == "false", f"{model} claim flag changed")
        checks.check(row.get("public_method") == "rA-public-dynamics", f"{model} public method changed")
        checks.check(row.get("local_method") == "Gauss6/FullVA-local-closed-loop", f"{model} local method changed")
        checks.check(row.get("step_sizes") == "0.02|0.01|0.005", f"{model} step sizes changed")
        checks.check("kinematic FullVA plus reaction reconstruction" in row.get("acceptance_blocker", ""), f"{model} blocker weakened")
        checks.check("residual-to-error" in row.get("acceptance_blocker", ""), f"{model} blocker missing residual-to-error boundary")
        checks.check(
            "gauss6_fullva_closed_loop_same_window_comparison_rows.csv" in row.get("evidence_paths", ""),
            f"{model} missing raw evidence path",
        )
        checks.check(math.isfinite(as_float(row.get("public_vel_order", "nan"))), f"{model} missing public velocity order")
        checks.check(math.isfinite(as_float(row.get("local_vel_error_ratio_vs_public", "nan"))), f"{model} missing local velocity error ratio")
        checks.check(math.isfinite(as_float(row.get("local_runtime_ratio_vs_public", "nan"))), f"{model} missing runtime ratio")
        checks.check(as_float(row.get("local_max_dynamics_residual_norm", "nan")) < 1.0e-12, f"{model} residual is too large")

    checks.check("surrogate evidence only; not external superiority" in report, "report missing status boundary")
    checks.check("does not use default `1e-4` runs" in report, "report missing no-default-1e-4 boundary")
    checks.check("Accepted dynamic order rows: `0`" in report, "report must state zero accepted dynamic rows")

    if checks.errors:
        print("closed-loop surrogate dynamic gate validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("closed-loop surrogate dynamic gate validation: PASS")
    print(f"rows={summary.get('row_count')}")
    print(f"surrogate_available={summary.get('surrogate_available_count')}")
    print(f"accepted_dynamic_order={summary.get('accepted_dynamic_order_count')}")
    print("dynamic_superiority_claim=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
