#!/usr/bin/env python3
"""Validate the closed-loop true-dynamic-row feasibility audit."""

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


def main() -> int:
    checks = Checks()
    try:
        rows = read_csv(RESULTS / "closed_loop_true_dynamic_row_feasibility_audit.csv")
        summary = read_json(RESULTS / "closed_loop_true_dynamic_row_feasibility_audit.json")
        report = (RESULTS / "closed_loop_true_dynamic_row_feasibility_audit.md").read_text(encoding="utf-8")
        closure = read_json(RESULTS / "closed_loop_dynamic_order_closure_contract.json")
    except Exception as exc:  # noqa: BLE001 - concise CLI failure.
        print(f"closed-loop true dynamic-row feasibility audit validation: FAIL\n- {exc}")
        return 1

    checks.check(summary.get("schema") == "closed-loop-true-dynamic-row-feasibility-audit-v1", "schema changed")
    checks.check(summary.get("default_policy") == "coarse_first_no_default_1e-4", "default policy changed")
    checks.check(set(summary.get("models", [])) == MODELS, "model set changed")
    checks.check(set(summary.get("missing_dynamic_order_models", [])) == MODELS, "missing model set changed")
    checks.check(summary.get("true_dynamic_local_rows_available") == 0, "true dynamic local rows unexpectedly available")
    checks.check(summary.get("accepted_dynamic_order_count") == 0, "accepted dynamic-order count must remain zero")
    checks.check(
        summary.get("current_local_row_kind") == "kinematic_fullva_plus_reaction_reconstruction",
        "local row kind changed",
    )
    checks.check(summary.get("current_local_setup_mode") == "kinematics", "local setup mode changed")
    checks.check(summary.get("current_public_baseline_kind") == "rA_public_dynamics", "public baseline kind changed")
    checks.check(summary.get("coarse_step_sizes") == [0.1, 0.05, 0.025], "coarse step sizes changed")
    checks.check(math.isclose(float(summary.get("reference_h")), 0.0125), "reference h changed")
    checks.check(summary.get("strict_public_policy_1e-4_required") is False, "strict 1e-4 incorrectly required")
    checks.check(summary.get("external_superiority_claim") is False, "external superiority incorrectly accepted")
    checks.check(summary.get("submission_ready") is False, "submission readiness incorrectly accepted")
    checks.check(
        summary.get("required_next_implementation")
        == "local_closed_loop_dynamic_dae_gauss6_fullva_runner_or_residual_to_error_theorem",
        "required next implementation changed",
    )
    theorem = summary.get("method_order_theorem", {})
    checks.check(theorem.get("accepted_method") == "Gauss6/FullVA", "theorem method changed")
    checks.check(theorem.get("global_order") == 6, "theorem order changed")
    checks.check("not kinematic/reaction replay" in theorem.get("applies_to", ""), "theorem boundary changed")

    source = summary.get("source_identity_checks", {})
    for key in [
        "v048_closed_loop_runner_uses_local_kinematic_fullva",
        "v047_local_runner_setup_mode_is_kinematics",
        "v047_local_runner_reconstructs_reactions_after_kinematics",
        "v048_public_baseline_uses_public_dynamics",
    ]:
        checks.check(source.get(key) is True, f"source identity check failed: {key}")
    checks.check(source.get("local_dynamic_fullva_runner_exists") is False, "local dynamic runner unexpectedly exists")
    checks.check(source.get("local_setup_system_dynamics_path_exists") is False, "local dynamics setup path unexpectedly exists")

    checks.check(len(rows) == 2, "expected one audit row per closed-loop model")
    checks.check({row.get("model") for row in rows} == MODELS, "CSV model set changed")
    for row in rows:
        model = row.get("model", "<missing>")
        checks.check(row.get("current_local_runner") == "simulate_v046_local_kinematic_fullva", f"{model} runner changed")
        checks.check(row.get("current_local_setup_mode") == "kinematics", f"{model} setup mode changed")
        checks.check(row.get("true_dynamic_local_row_available") == "false", f"{model} true dynamic row accepted")
        checks.check(row.get("accepted_dynamic_order") == "false", f"{model} dynamic order accepted")
        checks.check("Newton-Euler" in row.get("required_residual_blocks", ""), f"{model} missing dynamic residual block")
        checks.check("Lagrange multipliers" in row.get("required_unknown_blocks", ""), f"{model} missing multiplier unknown block")
        checks.check("h=[0.1,0.05,0.025]" in row.get("accepted_order_campaign", ""), f"{model} lost coarse h policy")
        checks.check(row.get("default_policy") == "coarse_first_no_default_1e-4", f"{model} default policy changed")
        checks.check(row.get("strict_public_policy_1e-4_required") == "false", f"{model} strict 1e-4 changed")
        checks.check(row.get("external_superiority_claim_allowed") == "false", f"{model} superiority boundary changed")

    checks.check(closure.get("accepted_dynamic_order_count") == 2, "closure contract lost new local order result")
    checks.check(closure.get("true_dynamic_local_rows_available") == 2, "closure contract lost true dynamic local rows")
    checks.check(closure.get("public_work_precision_available_count") == 2, "closure contract lost public work/precision availability")
    checks.check(closure.get("public_work_precision_missing_count") == 0, "closure contract lost closed public work/precision gap")
    checks.check(closure.get("strict_common_reference_available_count") == 2, "closure contract lost strict common-reference availability")
    checks.check(closure.get("strict_common_reference_gap_count") == 0, "closure contract lost strict common-reference closure")
    checks.check(closure.get("strict_common_reference_figure_available") is True, "closure contract lost strict common-reference figure")

    normalized_report = " ".join(report.split())
    for token in [
        "Closed-Loop True-Dynamic-Row Feasibility Audit",
        "true local dynamic trajectory rows are not implemented",
        "setup_system(..., \"kinematics\", ...)",
        "Required Dynamic Row",
        "No default `1e-4` run",
    ]:
        checks.check(token in report, f"report missing token: {token}")
    checks.check(
        "not a local dynamic DAE trajectory integrator" in normalized_report,
        "report missing dynamic-integrator boundary",
    )

    if checks.errors:
        print("closed-loop true dynamic-row feasibility audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("closed-loop true dynamic-row feasibility audit validation: PASS")
    print("missing_dynamic_order_models=four_link,slider_crank")
    print("true_dynamic_local_rows=0")
    print("accepted_dynamic_order=0")
    print("local_row_kind=kinematic_fullva_plus_reaction_reconstruction")
    print("required_next=local_dynamic_dae_runner_or_residual_to_error_theorem")
    print("default_1e-4=False")
    print("external_superiority_claim=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
