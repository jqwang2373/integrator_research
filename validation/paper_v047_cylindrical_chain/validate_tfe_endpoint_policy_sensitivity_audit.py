#!/usr/bin/env python3
"""Read-only validator for the diagnostic TFE endpoint-policy sensitivity audit."""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
JSON_PATH = PAPER / "TFE_ENDPOINT_POLICY_SENSITIVITY_AUDIT.json"
MD_PATH = PAPER / "TFE_ENDPOINT_POLICY_SENSITIVITY_AUDIT.md"
CSV_PATH = PAPER / "TFE_ENDPOINT_POLICY_SENSITIVITY_AUDIT.csv"

EXPECTED_POLICIES = [
    "adjust_h_to_hit_T_exactly",
    "algorithm_literal_fixed_h_until_tn_ge_tfinal",
    "floor_horizon",
    "integer_steps_plus_final_partial_step",
]

EXPECTED_METHODS = [
    "tfe2026_Newmark_beta",
    "tfe2026_TFE_m1",
    "tfe2026_TFE_m2",
    "tfe2026_trapezoidal",
]

EXPECTED_SOURCE_METHODS = {
    "tfe2026_Newmark_beta": "Newmark_beta",
    "tfe2026_TFE_m1": "TFE_m1",
    "tfe2026_TFE_m2": "TFE_m2",
    "tfe2026_trapezoidal": "trapezoidal",
}

EXPECTED_NOMINAL_H = [0.012, 0.006, 0.003]


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def finite_or_none(value: object) -> bool:
    if value is None:
        return True
    return isinstance(value, (int, float)) and math.isfinite(float(value))


def close_list(values: list[Any], expected: list[float], tol: float = 1.0e-12) -> bool:
    if len(values) != len(expected):
        return False
    return all(abs(float(value) - target) <= tol for value, target in zip(values, expected))


def rows_for(rows: list[dict[str, Any]], *, policy: str, method: str | None = None) -> list[dict[str, Any]]:
    selected = [row for row in rows if row.get("policy") == policy]
    if method is not None:
        selected = [row for row in selected if row.get("paper_method") == method]
    return selected


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(JSON_PATH)
        markdown = MD_PATH.read_text(encoding="utf-8")
        with CSV_PATH.open(encoding="utf-8", newline="") as handle:
            csv_rows = list(csv.DictReader(handle))
    except Exception as exc:  # noqa: BLE001
        print(f"TFE endpoint-policy sensitivity audit validation: FAIL\n- {exc}")
        return 1

    summary_rows = audit.get("summary_rows", [])
    raw_rows = audit.get("raw_rows", [])
    checks.check(isinstance(summary_rows, list), "summary_rows is not a list")
    checks.check(isinstance(raw_rows, list), "raw_rows is not a list")
    summary_dicts = [row for row in summary_rows if isinstance(row, dict)]
    raw_dicts = [row for row in raw_rows if isinstance(row, dict)]

    checks.check(audit.get("schema") == "tfe-endpoint-policy-sensitivity-audit-v1", "schema changed")
    checks.check(
        audit.get("status") == "diagnostic_endpoint_policy_sensitivity_not_source_policy",
        "status must remain diagnostic, not source-policy closure",
    )
    checks.check(audit.get("read_only") is True, "audit must be read-only")
    checks.check(audit.get("submission_ready") is False, "audit must not mark submission-ready")
    checks.check(audit.get("source_policy_rows_completed") == 0, "source-policy rows unexpectedly completed")
    checks.check(
        audit.get("external_superiority_claim_allowed") is False,
        "external superiority claim unexpectedly allowed",
    )
    checks.check(audit.get("source_policy_runner_equivalent") is False, "source runner equivalence changed")
    checks.check(audit.get("case_id") == "frictionless_pendulum_active_b2_planar_candidate", "case id changed")
    checks.check(abs(float(audit.get("t_final", -1.0)) - 10.0) <= 1.0e-12, "t_final changed")
    checks.check(abs(float(audit.get("reference_h", -1.0)) - 0.0001) <= 1.0e-15, "reference_h changed")
    checks.check(close_list(list(audit.get("nominal_h", [])), EXPECTED_NOMINAL_H), "nominal h values changed")
    checks.check(audit.get("endpoint_policies") == EXPECTED_POLICIES, "endpoint policies changed")
    checks.check(audit.get("method_count") == 4, "method count changed")
    checks.check(audit.get("policy_count") == 4, "policy count changed")
    checks.check(audit.get("summary_row_count") == 16 == len(summary_dicts), "summary row count changed")
    checks.check(audit.get("raw_row_count") == 48 == len(raw_dicts), "raw row count changed")
    checks.check(len(csv_rows) == 48, "CSV raw row count changed")

    execution_policy = audit.get("execution_policy", {})
    checks.check(isinstance(execution_policy, dict), "execution_policy missing")
    if isinstance(execution_policy, dict):
        checks.check(execution_policy.get("default_1e_4_campaign_invoked") is False, "default 1e-4 campaign changed")
        checks.check(execution_policy.get("run_v047_invoked") is False, "run_v047 was unexpectedly invoked")
        checks.check(execution_policy.get("source_policy_rows_completed") == 0, "execution source rows changed")

    method_names = sorted({str(row.get("paper_method")) for row in summary_dicts})
    checks.check(method_names == sorted(EXPECTED_METHODS), "summary method set changed")
    source_methods = {
        str(row.get("paper_method")): str(row.get("source_method"))
        for row in summary_dicts
        if row.get("paper_method") in EXPECTED_METHODS
    }
    checks.check(source_methods == EXPECTED_SOURCE_METHODS, "source-method mapping changed")
    policy_names = sorted({str(row.get("policy")) for row in summary_dicts})
    checks.check(policy_names == sorted(EXPECTED_POLICIES), "summary policy set changed")

    for method in EXPECTED_METHODS:
        checks.check(len([row for row in summary_dicts if row.get("paper_method") == method]) == 4, f"{method} policy rows changed")
    for policy in EXPECTED_POLICIES:
        checks.check(len(rows_for(summary_dicts, policy=policy)) == 4, f"{policy} summary rows changed")
        checks.check(len(rows_for(raw_dicts, policy=policy)) == 12, f"{policy} raw rows changed")

    expected_algorithm_times = [10.008000000000001, 10.002, 10.002]
    expected_floor_times = [9.996, 9.996, 9.999]
    for row in rows_for(summary_dicts, policy="adjust_h_to_hit_T_exactly"):
        checks.check(close_list(list(row.get("terminal_times", [])), [10.0, 10.0, 10.0]), "adjusted policy terminal times changed")
    for row in rows_for(summary_dicts, policy="integer_steps_plus_final_partial_step"):
        checks.check(close_list(list(row.get("terminal_times", [])), [10.0, 10.0, 10.0]), "partial-step policy terminal times changed")
    for row in rows_for(summary_dicts, policy="algorithm_literal_fixed_h_until_tn_ge_tfinal"):
        checks.check(close_list(list(row.get("terminal_times", [])), expected_algorithm_times, 1.0e-12), "algorithm-literal terminal times changed")
        checks.check(abs(float(row.get("max_terminal_time_offset_abs", -1.0)) - 0.008000000000000895) <= 1.0e-12, "algorithm-literal overrun changed")
    for row in rows_for(summary_dicts, policy="floor_horizon"):
        checks.check(close_list(list(row.get("terminal_times", [])), expected_floor_times, 1.0e-12), "floor policy terminal times changed")

    for row in summary_dicts:
        checks.check(row.get("source_policy_row_completed") is False, "summary row completed a source-policy row")
        checks.check(close_list(list(row.get("nominal_h", [])), EXPECTED_NOMINAL_H), "summary nominal h values changed")
        for key in [
            "coordinate_pairwise_orders_nominal_h",
            "velocity_pairwise_orders_nominal_h",
            "coordinate_pairwise_orders_effective_h",
            "velocity_pairwise_orders_effective_h",
        ]:
            values = row.get(key)
            checks.check(isinstance(values, list) and len(values) == 2, f"{key} shape changed")
            if isinstance(values, list):
                checks.check(all(finite_or_none(value) for value in values), f"{key} has nonfinite values")
        for key in ["finest_coordinate_error", "finest_velocity_error", "max_residual_norm"]:
            value = row.get(key)
            checks.check(isinstance(value, (int, float)) and math.isfinite(float(value)) and float(value) >= 0.0, f"{key} invalid")

    for row in raw_dicts:
        for key in ["coordinate_error_q", "velocity_error_v", "frobenius_error_norm_eta", "max_residual_norm"]:
            value = row.get(key)
            checks.check(isinstance(value, (int, float)) and math.isfinite(float(value)) and float(value) >= 0.0, f"raw {key} invalid")
        checks.check(row.get("paper_method") in EXPECTED_METHODS, "raw method changed")
        checks.check(row.get("policy") in EXPECTED_POLICIES, "raw policy changed")
        checks.check(float(row.get("nominal_h", -1.0)) in EXPECTED_NOMINAL_H, "raw nominal h changed")

    sensitivity = audit.get("sensitivity_by_method", {})
    checks.check(isinstance(sensitivity, dict), "sensitivity_by_method missing")
    if isinstance(sensitivity, dict):
        checks.check(sorted(sensitivity) == sorted(EXPECTED_METHODS), "sensitivity methods changed")
        for method, row in sensitivity.items():
            checks.check(isinstance(row, dict), f"{method} sensitivity row missing")
            if isinstance(row, dict):
                checks.check(row.get("policy_count") == 4, f"{method} policy count changed")
                checks.check(finite_or_none(row.get("velocity_order_spread_across_policies")), f"{method} order spread invalid")
                checks.check(finite_or_none(row.get("finest_velocity_error_ratio_across_policies")), f"{method} error ratio invalid")

    for token in [
        "diagnostic endpoint-policy sensitivity",
        "not source-policy closure",
        "Source-policy rows completed: `0`",
        "External superiority claim allowed: `False`",
        "algorithm_literal_fixed_h_until_tn_ge_tfinal",
        "integer_steps_plus_final_partial_step",
    ]:
        checks.check(token in markdown, f"markdown missing token: {token}")

    if checks.errors:
        print("TFE endpoint-policy sensitivity audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("TFE endpoint-policy sensitivity audit validation: PASS")
    print(f"summary_rows={audit['summary_row_count']}")
    print(f"raw_rows={audit['raw_row_count']}")
    print(f"source_policy_rows_completed={audit['source_policy_rows_completed']}")
    print(f"external_superiority_claim_allowed={audit['external_superiority_claim_allowed']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
