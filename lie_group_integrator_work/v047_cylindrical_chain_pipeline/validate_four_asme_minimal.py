#!/usr/bin/env python3
"""Read-only minimal validator for the v047 four-example ASME method gate.

This script intentionally does not rerun simulations. It checks the existing
v047 result artifacts that prove the four-example method-row claim, leaving the
full historical audit suite to validate_v047_outputs.py.
"""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"

EXPECTED_MODELS = {
    "single_pendulum",
    "double_pendulum",
    "four_link",
    "slider_crank",
}
EXPECTED_GATE_STATUS = "four_asme_method_rows_accepted_projection_sharp_sparse_caveats"
EXPECTED_MAPPING_STATUS = {
    "single_pendulum": "exact_driven_absolute_fullva_residual",
    "double_pendulum": "accepted_method_side_double_revolute_fullva_reference_policy",
    "four_link": "accepted_closed_loop_kinematic_fullva_reaction_dynamics",
    "slider_crank": "accepted_closed_loop_kinematic_fullva_reaction_dynamics",
}
H_GRAPH = {0.005, 0.01, 0.02}
H_SINGLE_ABSOLUTE = {0.05, 0.1, 0.2}
H_DOUBLE_METHOD = {0.01, 0.02, 0.04}
CONSTRAINT_TOL = 1.0e-12
DYNAMICS_TOL = 1.0e-12
HIGH_ORDER_FLOOR = 5.5


class CheckSet:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_csv(name: str) -> list[dict[str, str]]:
    path = RESULTS / name
    if not path.exists():
        raise FileNotFoundError(f"missing result artifact: {path}")
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def read_summary() -> dict:
    path = RESULTS / "summary_v047.json"
    if not path.exists():
        raise FileNotFoundError(f"missing summary artifact: {path}")
    with path.open() as handle:
        return json.load(handle)


def as_float(row: dict[str, str], key: str) -> float:
    value = row.get(key, "")
    try:
        result = float(value)
    except ValueError as exc:
        raise ValueError(f"{key}={value!r} is not a float in row {row}") from exc
    if not math.isfinite(result):
        raise ValueError(f"{key}={value!r} is not finite in row {row}")
    return result


def h_values(rows: Iterable[dict[str, str]]) -> set[float]:
    return {round(as_float(row, "h"), 12) for row in rows}


def by_model(rows: Iterable[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(row["model"], []).append(row)
    return grouped


def check_status_rows(checks: CheckSet, rows: Iterable[dict[str, str]], label: str) -> None:
    for row in rows:
        checks.check(row.get("status") == "ok", f"{label}: non-ok status in {row}")
        checks.check(row.get("error_message", "") == "", f"{label}: error_message is nonempty in {row}")


def validate_summary(checks: CheckSet, summary: dict) -> None:
    asme = summary.get("asme_gate", {})
    checks.check(asme.get("status") == EXPECTED_GATE_STATUS, "summary ASME gate status changed")
    models = asme.get("models", {})
    checks.check(set(models) == EXPECTED_MODELS, f"summary ASME models mismatch: {sorted(models)}")
    for model, expected in EXPECTED_MAPPING_STATUS.items():
        actual = models.get(model, {}).get("v047_mapping_status")
        checks.check(actual == expected, f"summary {model} status is {actual!r}, expected {expected!r}")


def validate_gate_csv(checks: CheckSet) -> None:
    rows = read_csv("cylindrical_chain_asme_gate.csv")
    checks.check(len(rows) == 4, "ASME gate CSV should contain exactly four model rows")
    gate_by_model = {row["model"]: row for row in rows}
    checks.check(set(gate_by_model) == EXPECTED_MODELS, f"ASME gate CSV models mismatch: {sorted(gate_by_model)}")
    for model, expected in EXPECTED_MAPPING_STATUS.items():
        row = gate_by_model.get(model, {})
        checks.check(row.get("v046_baseline_present") == "True", f"{model} missing v046 baseline marker")
        checks.check(row.get("v047_mapping_status") == expected, f"{model} gate status is not {expected}")


def validate_graph_and_rank_support(checks: CheckSet) -> None:
    graph = read_csv("cylindrical_chain_asme_lower_pair_graph_bridge.csv")
    rank = read_csv("cylindrical_chain_asme_lower_pair_rank_audit.csv")
    checks.check(len(graph) == 12, "lower-pair graph bridge should have 4 models x 3 h rows")
    checks.check(len(rank) == 12, "lower-pair rank audit should have 4 models x 3 h rows")
    check_status_rows(checks, graph, "lower-pair graph bridge")
    check_status_rows(checks, rank, "lower-pair rank audit")
    for label, rows in [("graph bridge", graph), ("rank audit", rank)]:
        grouped = by_model(rows)
        checks.check(set(grouped) == EXPECTED_MODELS, f"{label} models mismatch: {sorted(grouped)}")
        for model, model_rows in grouped.items():
            checks.check(h_values(model_rows) == H_GRAPH, f"{label} h sweep mismatch for {model}")
    for row in rank:
        checks.check(int(row["row_rank_defect"]) == 0, f"rank defect is nonzero in {row}")
        checks.check(as_float(row, "min_singular_value") > 0.0, f"rank audit singular value not positive in {row}")


def validate_single_and_double(checks: CheckSet) -> tuple[float, float]:
    single = read_csv("cylindrical_chain_asme_single_absolute_fullva_runs.csv")
    double = read_csv("cylindrical_chain_asme_double_method_runs.csv")
    checks.check(len(single) == 3, "single absolute FullVA should have three h rows")
    checks.check(len(double) == 3, "double method should have three h rows")
    check_status_rows(checks, single, "single absolute FullVA")
    check_status_rows(checks, double, "double method")
    checks.check({row["model"] for row in single} == {"single_pendulum"}, "single absolute CSV model mismatch")
    checks.check({row["model"] for row in double} == {"double_pendulum"}, "double method CSV model mismatch")
    checks.check(h_values(single) == H_SINGLE_ABSOLUTE, "single absolute FullVA h sweep changed")
    checks.check(h_values(double) == H_DOUBLE_METHOD, "double method h sweep changed")

    single_orders = [
        as_float(row, key)
        for row in single
        for key in (
            "position_observed_order",
            "velocity_observed_order",
            "orientation_observed_order",
            "omega_observed_order",
        )
    ]
    double_orders = [
        as_float(row, key)
        for row in double
        for key in ("orientation_observed_order", "omega_observed_order")
    ]
    min_single_order = min(single_orders)
    min_double_order = min(double_orders)
    checks.check(min_single_order > HIGH_ORDER_FLOOR, f"single absolute order below floor: {min_single_order:.3f}")
    checks.check(min_double_order > HIGH_ORDER_FLOOR, f"double method order below floor: {min_double_order:.3f}")
    for row in single:
        checks.check(as_float(row, "max_stage_residual_norm") < 1.0e-10, f"single stage residual too large in {row}")
        checks.check(as_float(row, "max_trans_dynamics_residual") < 1.0e-10, f"single translational residual too large in {row}")
        checks.check(as_float(row, "max_rot_dynamics_residual") < 1.0e-10, f"single rotational residual too large in {row}")
    for row in double:
        checks.check(as_float(row, "max_endpoint_constraint_norm") < 1.0e-10, f"double endpoint constraint too large in {row}")
        checks.check(as_float(row, "max_endpoint_velocity_constraint_norm") < 1.0e-10, f"double endpoint velocity too large in {row}")
        checks.check(as_float(row, "max_stage_acceleration_constraint_norm") < 1.0e-10, f"double stage acceleration constraint too large in {row}")
    return min_single_order, min_double_order


def validate_closed_loop_models(checks: CheckSet) -> tuple[float, float]:
    closed = read_csv("cylindrical_chain_asme_closed_loop_kinematic_fullva.csv")
    reaction = read_csv("cylindrical_chain_asme_closed_loop_reaction_dynamics.csv")
    expected_closed_models = {"four_link", "slider_crank"}
    checks.check(len(closed) == 6, "closed-loop kinematic FullVA should have 2 models x 3 h rows")
    checks.check(len(reaction) == 6, "closed-loop reaction dynamics should have 2 models x 3 h rows")
    check_status_rows(checks, closed, "closed-loop kinematic FullVA")
    check_status_rows(checks, reaction, "closed-loop reaction dynamics")
    for label, rows in [("closed-loop kinematic", closed), ("closed-loop reaction", reaction)]:
        grouped = by_model(rows)
        checks.check(set(grouped) == expected_closed_models, f"{label} model set changed: {sorted(grouped)}")
        for model, model_rows in grouped.items():
            checks.check(h_values(model_rows) == H_GRAPH, f"{label} h sweep mismatch for {model}")

    max_constraint = 0.0
    for row in closed:
        for key in (
            "max_position_constraint_norm",
            "max_velocity_constraint_norm",
            "max_acceleration_constraint_norm",
            "max_so3_fro",
        ):
            value = as_float(row, key)
            max_constraint = max(max_constraint, value)
            checks.check(value < CONSTRAINT_TOL, f"{row['model']} {key} exceeds tolerance: {value:.3e}")

    max_dynamics = 0.0
    for row in reaction:
        value = as_float(row, "max_dynamics_residual_norm")
        max_dynamics = max(max_dynamics, value)
        checks.check(value < DYNAMICS_TOL, f"{row['model']} dynamics residual exceeds tolerance: {value:.3e}")
    return max_constraint, max_dynamics


def main() -> int:
    checks = CheckSet()
    try:
        summary = read_summary()
        validate_summary(checks, summary)
        validate_gate_csv(checks)
        validate_graph_and_rank_support(checks)
        min_single_order, min_double_order = validate_single_and_double(checks)
        max_closed_constraint, max_reaction_residual = validate_closed_loop_models(checks)
    except Exception as exc:  # noqa: BLE001 - command-line validator reports fatal read/parse issues.
        print("v047 minimal four-ASME validation: FAIL")
        print(f"fatal={exc}")
        return 1

    if checks.errors:
        print("v047 minimal four-ASME validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    tfe = summary.get("endpoint_tfe_paper_lower_pair_velocity_compression_audit", {})
    print("v047 minimal four-ASME validation: PASS")
    print(f"asme_gate_status={summary['asme_gate']['status']}")
    print("models=double_pendulum,four_link,single_pendulum,slider_crank")
    print(f"single_absolute_min_order={min_single_order:.3f}")
    print(f"double_method_min_order={min_double_order:.3f}")
    print(f"closed_loop_max_constraint_norm={max_closed_constraint:.3e}")
    print(f"closed_loop_reaction_max_dynamics_residual={max_reaction_residual:.3e}")
    print(f"full_tfe_stage_replacement={tfe.get('full_tfe_stage_replacement', False)}")
    print("remaining_caveat=full_tfe_stage_replacement_missing_outside_four_example_gate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
