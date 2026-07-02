#!/usr/bin/env python3
"""Validate the closed-loop true-dynamic residual scaffold contract."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
MODELS = {"four_link", "slider_crank"}
REQUIRED_SYMBOLS = {
    "pack_closed_loop_fullva_stage_vector",
    "unpack_closed_loop_fullva_stage_vector",
    "closed_loop_fullva_stage_residual",
    "gauss6_closed_loop_fullva_dynamic_step",
    "simulate_v046_local_dynamic_fullva",
}
RESIDUAL_FAMILIES = {
    "position_constraints_phi",
    "velocity_constraints_phiq_v_minus_nu",
    "acceleration_constraints_phiq_a_minus_gamma",
    "newton_euler_balance",
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


def main() -> int:
    checks = Checks()
    try:
        rows = read_csv(RESULTS / "closed_loop_true_dynamic_residual_scaffold.csv")
        summary = read_json(RESULTS / "closed_loop_true_dynamic_residual_scaffold.json")
        report = (RESULTS / "closed_loop_true_dynamic_residual_scaffold.md").read_text(encoding="utf-8")
        interface = read_json(RESULTS / "closed_loop_true_dynamic_interface_audit.json")
        plan = read_json(RESULTS / "closed_loop_true_dynamic_local_row_plan.json")
    except Exception as exc:  # noqa: BLE001 - concise CLI failure.
        print(f"closed-loop true dynamic residual scaffold validation: FAIL\n- {exc}")
        return 1

    checks.check(summary.get("schema") == "closed-loop-true-dynamic-residual-scaffold-v1", "schema changed")
    checks.check(
        summary.get("status") == "residual_layout_specified_runner_not_implemented",
        "status changed",
    )
    checks.check(summary.get("method") == "Gauss6/FullVA", "method changed")
    checks.check(set(summary.get("models", [])) == MODELS, "model set changed")
    checks.check(summary.get("n_stages") == 3, "Gauss6 stage count changed")
    checks.check(summary.get("row_count") == 2, "row count changed")
    checks.check(summary.get("stage_unknown_dim") == 72, "stage unknown dimension changed")
    checks.check(summary.get("total_unknown_dim") == 216, "total unknown dimension changed")
    checks.check(set(summary.get("residual_families", [])) == RESIDUAL_FAMILIES, "residual families changed")
    checks.check(summary.get("square_total_system") is True, "system no longer square")
    checks.check(summary.get("local_runner_implemented") is False, "runner implementation overclaimed")
    checks.check(summary.get("required_runner") == "local_closed_loop_dynamic_dae_gauss6_fullva_runner", "runner name changed")
    checks.check(set(summary.get("required_code_symbols", [])) == REQUIRED_SYMBOLS, "required symbols changed")
    checks.check(summary.get("accepted_dynamic_order_count") == 0, "dynamic order overclaimed")
    checks.check(summary.get("default_policy") == "coarse_first_no_default_1e-4", "default policy changed")
    checks.check(summary.get("strict_public_policy_1e-4_required") is False, "strict 1e-4 incorrectly required")
    checks.check(summary.get("default_1e-4_required") is False, "default 1e-4 incorrectly required")
    checks.check(summary.get("heavy_numerical_run_invoked") is False, "scaffold invoked heavy run")
    checks.check(summary.get("external_superiority_claim") is False, "external superiority overclaimed")
    source = summary.get("source_inputs", {})
    checks.check(source.get("interface_audit_schema") == interface.get("schema"), "interface source mismatch")
    checks.check(source.get("interface_dynamic_setup_ok_count") == interface.get("dynamic_setup_ok_count") == 2, "interface setup count mismatch")
    checks.check(source.get("row_plan_schema") == plan.get("schema"), "row plan source mismatch")
    checks.check(source.get("row_plan_count") == plan.get("row_count") == 24, "row plan count mismatch")

    checks.check(len(rows) == 2, "expected one scaffold row per closed-loop model")
    checks.check({row.get("model") for row in rows} == MODELS, "CSV model set changed")
    for row in rows:
        model = row.get("model", "<missing>")
        checks.check(row.get("n_stages") == "3", f"{model} stage count changed")
        checks.check(row.get("body_count") == "3", f"{model} body count changed")
        checks.check(row.get("constraint_count") == "18", f"{model} constraint count changed")
        checks.check(row.get("generalized_dim") == "18", f"{model} generalized dim changed")
        checks.check(row.get("stage_q_dim") == "18", f"{model} q dim changed")
        checks.check(row.get("stage_v_dim") == "18", f"{model} v dim changed")
        checks.check(row.get("stage_a_dim") == "18", f"{model} a dim changed")
        checks.check(row.get("stage_lambda_dim") == "18", f"{model} lambda dim changed")
        checks.check(row.get("stage_unknown_dim") == "72", f"{model} stage unknown dim changed")
        checks.check(row.get("total_unknown_dim") == "216", f"{model} total unknown dim changed")
        checks.check(row.get("stage_residual_dim") == "72", f"{model} stage residual dim changed")
        checks.check(row.get("total_residual_dim") == "216", f"{model} total residual dim changed")
        checks.check(row.get("square_stage_system") == "true", f"{model} stage system not square")
        checks.check(row.get("square_total_system") == "true", f"{model} total system not square")
        checks.check(row.get("position_constraint_rows") == "18", f"{model} Phi row count changed")
        checks.check(row.get("velocity_constraint_rows") == "18", f"{model} velocity row count changed")
        checks.check(row.get("acceleration_constraint_rows") == "18", f"{model} acceleration row count changed")
        checks.check(row.get("newton_euler_rows") == "18", f"{model} Newton-Euler row count changed")
        checks.check(row.get("accepted_dynamic_order") == "false", f"{model} dynamic order accepted")
        checks.check(row.get("default_policy") == "coarse_first_no_default_1e-4", f"{model} default policy changed")
        checks.check(row.get("strict_public_policy_1e-4_required") == "false", f"{model} strict 1e-4 changed")
        checks.check("Phi_q a-gamma" in row.get("fullva_replacement_policy", ""), f"{model} FullVA policy changed")
        checks.check("Gauss6 quadrature" in row.get("endpoint_update_policy", ""), f"{model} endpoint policy changed")

    normalized_report = " ".join(report.split())
    for token in [
        "Closed-Loop True-Dynamic Residual Scaffold",
        "residual layout specified; runner not implemented",
        "Stage unknown dimension: `72`",
        "Total Newton dimension: `216`",
        "position/acceleration consistency rows",
        "simulate_v046_local_dynamic_fullva",
    ]:
        checks.check(token in report or token in normalized_report, f"report missing token: {token}")

    if checks.errors:
        print("closed-loop true dynamic residual scaffold validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("closed-loop true dynamic residual scaffold validation: PASS")
    print("stage_unknown_dim=72")
    print("total_unknown_dim=216")
    print("square_total_system=True")
    print("local_runner_implemented=False")
    print("default_1e-4=False")
    print("accepted_dynamic_order=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
