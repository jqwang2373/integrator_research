#!/usr/bin/env python3
"""Validate the plan-only closed-loop true-dynamic local row contract."""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
MODELS = {"four_link", "slider_crank"}
PUBLIC_BASELINES = {"rA", "rp", "reps"}
STEPS = {0.1, 0.05, 0.025}
METRICS = {
    "position_error",
    "velocity_error",
    "acceleration_error",
    "observed_order",
    "runtime",
    "newton_iterations",
    "constraint_drift",
}


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


def float_set(rows: list[dict[str, str]], key: str) -> set[float]:
    return {float(row[key]) for row in rows}


def main() -> int:
    checks = Checks()
    try:
        rows = read_csv(RESULTS / "closed_loop_true_dynamic_local_row_plan.csv")
        summary = read_json(RESULTS / "closed_loop_true_dynamic_local_row_plan.json")
        report = (RESULTS / "closed_loop_true_dynamic_local_row_plan.md").read_text(encoding="utf-8")
        closure = read_json(RESULTS / "closed_loop_dynamic_order_closure_contract.json")
        feasibility = read_json(RESULTS / "closed_loop_true_dynamic_row_feasibility_audit.json")
    except Exception as exc:  # noqa: BLE001 - concise CLI failure.
        print(f"closed-loop true dynamic local row plan validation: FAIL\n- {exc}")
        return 1

    checks.check(summary.get("schema") == "closed-loop-true-dynamic-local-row-plan-v1", "schema changed")
    checks.check(summary.get("status") == "plan_only_not_run", "status changed")
    checks.check(summary.get("execution_status") == "not_run", "execution status changed")
    checks.check(summary.get("plan_only") is True, "plan-only marker changed")
    checks.check(summary.get("default_policy") == "coarse_first_no_default_1e-4", "default policy changed")
    checks.check(set(summary.get("models", [])) == MODELS, "model set changed")
    checks.check(summary.get("local_method") == "Gauss6/FullVA", "local method changed")
    checks.check(set(summary.get("public_baselines", [])) == PUBLIC_BASELINES, "public baselines changed")
    checks.check(set(float(value) for value in summary.get("step_sizes", [])) == STEPS, "step sizes changed")
    checks.check(math.isclose(float(summary.get("reference_h")), 0.0125), "reference h changed")
    checks.check(set(summary.get("metrics", [])) == METRICS, "metrics changed")
    checks.check(summary.get("row_count") == 24, "row count changed")
    checks.check(summary.get("local_target_row_count") == 6, "local target row count changed")
    checks.check(summary.get("public_comparator_row_count") == 18, "public comparator row count changed")
    checks.check(summary.get("true_dynamic_local_rows_available") == 0, "true dynamic local rows overclaimed")
    checks.check(summary.get("accepted_dynamic_order_count") == 0, "dynamic order overclaimed")
    checks.check(summary.get("strict_public_policy_1e-4_required") is False, "strict 1e-4 incorrectly required")
    checks.check(summary.get("default_1e-4_required") is False, "default 1e-4 incorrectly required")
    checks.check(summary.get("heavy_numerical_run_invoked") is False, "plan invoked numerical run")
    checks.check(summary.get("external_superiority_claim") is False, "external superiority overclaimed")
    checks.check(summary.get("new_code_required_before_execution") is True, "new code requirement lost")
    checks.check(
        summary.get("required_new_runner") == "local_closed_loop_dynamic_dae_gauss6_fullva_runner",
        "required runner changed",
    )
    checks.check(summary.get("parallelization") == "split_by_model_method_and_step", "parallelization changed")
    checks.check(
        "strict_public_policy_1e-4_without_explicit_opt_in" in summary.get("do_not_run", []),
        "do-not-run list lost strict 1e-4 guard",
    )

    source = summary.get("source_inputs", {})
    checks.check(source.get("closure_contract_schema") == closure.get("schema"), "closure source mismatch")
    checks.check(source.get("feasibility_audit_schema") == feasibility.get("schema"), "feasibility source mismatch")
    checks.check(set(source.get("missing_dynamic_order_models", [])) == MODELS, "source missing models changed")
    checks.check(
        source.get("current_local_row_kind") == "kinematic_fullva_plus_reaction_reconstruction",
        "source local row kind changed",
    )

    checks.check(len(rows) == 24, "expected 24 plan rows")
    checks.check({row.get("model") for row in rows} == MODELS, "CSV model set changed")
    checks.check(float_set(rows, "step_size") == STEPS, "CSV step sizes changed")
    checks.check({row.get("method") for row in rows} == {"Gauss6/FullVA", "rA", "rp", "reps"}, "CSV methods changed")
    checks.check(
        all(math.isclose(float(row.get("reference_h", "nan")), 0.0125) for row in rows),
        "CSV reference h changed",
    )
    for row in rows:
        row_id = row.get("row_id", "<missing>")
        checks.check(row.get("execution_status") == "not_run", f"{row_id} execution status changed")
        checks.check(row.get("plan_only") == "true", f"{row_id} lost plan-only marker")
        checks.check(row.get("default_policy") == "coarse_first_no_default_1e-4", f"{row_id} default policy changed")
        checks.check(row.get("strict_public_policy_1e-4_required") == "false", f"{row_id} strict 1e-4 changed")
        checks.check(row.get("heavy_numerical_run_invoked") == "false", f"{row_id} invoked a run")
        checks.check(row.get("accepted_dynamic_order") == "false", f"{row_id} accepted dynamic order")
        checks.check(row.get("external_superiority_claim_allowed") == "false", f"{row_id} allowed superiority claim")
        checks.check(set(row.get("metrics", "").split("|")) == METRICS, f"{row_id} metrics changed")
        if row.get("method") == "Gauss6/FullVA":
            checks.check(row.get("row_role") == "local_dynamic_target", f"{row_id} local role changed")
            checks.check(row.get("new_code_required") == "true", f"{row_id} lost new-code requirement")
            checks.check(
                row.get("required_runner") == "local_closed_loop_dynamic_dae_gauss6_fullva_runner",
                f"{row_id} local runner changed",
            )
            checks.check(
                row.get("true_dynamic_local_row_available") == "false",
                f"{row_id} true local row availability overclaimed",
            )
        else:
            checks.check(row.get("row_role") == "public_baseline_comparator", f"{row_id} public role changed")
            checks.check(row.get("new_code_required") == "false", f"{row_id} public new-code flag changed")
            checks.check(row.get("required_runner") == "ra2021_public_dynamic_runner", f"{row_id} public runner changed")

    normalized_report = " ".join(report.split())
    for token in [
        "Closed-Loop True-Dynamic Local Row Plan",
        "plan only; no numerical rows have been run",
        "h=[0.1,0.05,0.025]",
        "It is not a source-paper `1e-4` reproduction campaign",
        "No row in this plan permits an external superiority claim",
    ]:
        checks.check(token in report or token in normalized_report, f"report missing token: {token}")

    if checks.errors:
        print("closed-loop true dynamic local row plan validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("closed-loop true dynamic local row plan validation: PASS")
    print("status=plan_only_not_run")
    print("row_count=24")
    print("local_target_rows=6")
    print("public_comparator_rows=18")
    print("default_1e-4=False")
    print("heavy_numerical_run_invoked=False")
    print("accepted_dynamic_order=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
