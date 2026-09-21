#!/usr/bin/env python3
"""Validate the TFE full-T10 absolute-coordinate DAE-lift summary."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path


PAPER = Path(__file__).resolve().parent
SUMMARY_JSON = PAPER / "TFE_FULL_T10_ABSOLUTE_DAE_LIFT_SUMMARY.json"
SUMMARY_MD = PAPER / "TFE_FULL_T10_ABSOLUTE_DAE_LIFT_SUMMARY.md"
SUMMARY_CSV = PAPER / "TFE_FULL_T10_ABSOLUTE_DAE_LIFT_SUMMARY.csv"


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
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def finite(value: object) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def main() -> int:
    checks = Checks()
    try:
        summary = read_json(SUMMARY_JSON)
        csv_rows = read_csv(SUMMARY_CSV)
        md = SUMMARY_MD.read_text(encoding="utf-8")
    except Exception as exc:  # noqa: BLE001
        print(f"TFE full-T10 absolute DAE-lift summary validation: FAIL\n- {exc}")
        return 1

    rows = summary.get("rows", [])
    checks.check(summary.get("schema") == "tfe-full-t10-absolute-dae-lift-summary-v1", "schema changed")
    checks.check(
        summary.get("status") == "full_T10_absolute_dae_lift_candidate_summarized_not_source_policy",
        "status changed",
    )
    checks.check(summary.get("submission_ready") is False, "summary overclaims submission readiness")
    checks.check(summary.get("external_superiority_claim_allowed") is False, "summary overclaims superiority")
    checks.check(summary.get("source_policy_rows_completed") == 0, "source-policy rows unexpectedly closed")
    checks.check(summary.get("full_T10_absolute_coordinate_lift_completed") is True, "full T10 lift missing")
    checks.check(
        summary.get("monolithic_absolute_coordinate_dae_time_integrator") is False,
        "summary overclaims monolithic DAE integration",
    )
    checks.check(
        summary.get("source_policy_dae_runner_equivalent") is False,
        "summary overclaims source-policy DAE equivalence",
    )
    checks.check(
        summary.get("source_policy_method_runner_equivalent") is False,
        "summary overclaims source-policy method equivalence",
    )
    checks.check(summary.get("default_1e_4_campaign_invoked") is False, "default 1e-4 campaign marker changed")
    checks.check(summary.get("source_reference_invoked") is True, "source-reference diagnostic not invoked")
    checks.check(summary.get("source_reference_h") == 0.0001, "source-reference h changed")
    checks.check(summary.get("t_final") == 10.0, "T=10 horizon changed")
    checks.check(summary.get("reference_h") == 0.0001, "reference h changed")
    checks.check(summary.get("comparison_h") == [0.1, 0.05, 0.025], "comparison h-grid changed")
    checks.check(summary.get("method_count") == 4, "method count changed")
    checks.check(summary.get("row_count") == len(rows) == len(csv_rows) == 4, "row count changed")
    checks.check(summary.get("metric_row_count") == 12, "metric row count changed")
    checks.check(summary.get("step_residual_row_count") == 2800, "step residual row count changed")
    checks.check(summary.get("all_step_states_finite") is True, "step-state finiteness failed")
    for key in [
        "max_candidate_step_residual_norm",
        "max_hinge_position_constraint_norm",
        "max_hinge_velocity_constraint_norm",
        "max_translational_balance_residual_norm",
        "max_axis_projected_rotational_residual_abs",
    ]:
        checks.check(finite(summary.get(key)), f"{key} is not finite")
    checks.check(summary.get("claim_boundary", {}).get("not_source_policy_reproduction") is True, "claim boundary missing")
    checks.check(
        summary.get("claim_boundary", {}).get("not_monolithic_source_policy_dae_runner") is True,
        "monolithic DAE boundary missing",
    )

    expected_methods = {
        "tfe2026_Newmark_beta": 2,
        "tfe2026_TFE_m1": 1,
        "tfe2026_TFE_m2": 3,
        "tfe2026_trapezoidal": 2,
    }
    seen = {}
    for row in rows:
        method = row.get("paper_method")
        seen[method] = row.get("expected_order")
        checks.check(row.get("expected_order") == expected_methods.get(method), f"{method} target order changed")
        checks.check(row.get("step_residual_rows") == 700, f"{method} step residual count changed")
        checks.check(row.get("step_states_finite") is True, f"{method} step states not finite")
        checks.check(len(row.get("coordinate_pairwise_orders", [])) == 2, f"{method} coordinate order pairs missing")
        checks.check(len(row.get("velocity_pairwise_orders", [])) == 2, f"{method} velocity order pairs missing")
        checks.check(row.get("finest_h") == 0.025, f"{method} finest h changed")
        for key in [
            "finest_coordinate_error",
            "finest_velocity_error",
            "finest_frobenius_error",
            "finest_hinge_position_constraint_norm",
            "finest_hinge_velocity_constraint_norm",
            "max_candidate_step_residual_norm",
            "max_hinge_position_constraint_norm",
            "max_hinge_velocity_constraint_norm",
            "max_translational_balance_residual_norm",
            "max_axis_projected_rotational_residual_abs",
        ]:
            checks.check(finite(row.get(key)), f"{method} {key} is not finite")
        checks.check(
            row.get("monolithic_absolute_coordinate_dae_time_integrator") is False,
            f"{method} overclaims monolithic DAE integration",
        )
        checks.check(row.get("source_policy_dae_runner_equivalent") is False, f"{method} overclaims DAE equivalence")
        checks.check(
            row.get("source_policy_method_runner_equivalent") is False,
            f"{method} overclaims method equivalence",
        )
        checks.check(row.get("source_policy_row_completed") is False, f"{method} overcloses source-policy row")
        checks.check(
            row.get("accepted_use") == "full_T10_absolute_dae_lift_candidate_not_source_policy",
            f"{method} accepted-use changed",
        )
    checks.check(seen == expected_methods, "method set changed")

    required_md_tokens = [
        "full T=10 absolute-coordinate DAE-lift candidate summarized",
        "Source-policy rows completed: `0`",
        "Monolithic source-policy DAE runner: `False`",
        "Methods/metric rows/step residual rows: `4/12/2800`",
        "not close original TFE source-policy reproduction",
    ]
    for token in required_md_tokens:
        checks.check(token in md, f"markdown missing token: {token}")

    if checks.errors:
        print("TFE full-T10 absolute DAE-lift summary validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("TFE full-T10 absolute DAE-lift summary validation: PASS")
    print("rows=4")
    print("metric_step_rows=12/2800")
    print("source_policy_rows_completed=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
