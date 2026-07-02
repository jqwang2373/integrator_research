#!/usr/bin/env python3
"""Validate the setup-level true-dynamic interface audit."""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
MODELS = {"four_link", "slider_crank"}
MODES = {"kinematics", "dynamics"}


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
        rows = read_csv(RESULTS / "closed_loop_true_dynamic_interface_audit.csv")
        summary = read_json(RESULTS / "closed_loop_true_dynamic_interface_audit.json")
        report = (RESULTS / "closed_loop_true_dynamic_interface_audit.md").read_text(encoding="utf-8")
        plan = read_json(RESULTS / "closed_loop_true_dynamic_local_row_plan.json")
    except Exception as exc:  # noqa: BLE001 - concise CLI failure.
        print(f"closed-loop true dynamic interface audit validation: FAIL\n- {exc}")
        return 1

    checks.check(summary.get("schema") == "closed-loop-true-dynamic-interface-audit-v1", "schema changed")
    checks.check(
        summary.get("status") == "setup_level_interface_verified_no_trajectory_run",
        "status changed",
    )
    checks.check(set(summary.get("models", [])) == MODELS, "model set changed")
    checks.check(set(summary.get("modes", [])) == MODES, "mode set changed")
    checks.check(summary.get("row_count") == 4, "row count changed")
    checks.check(summary.get("dynamic_setup_ok_count") == 2, "dynamic setup count changed")
    checks.check(summary.get("dynamic_setup_required_count") == 2, "dynamic setup required count changed")
    checks.check(summary.get("kinematic_setup_ok_count") == 2, "kinematic setup count changed")
    checks.check(summary.get("local_gauss6_dynamic_runner_exists") is False, "local runner unexpectedly exists")
    checks.check(summary.get("public_dynamic_setup_available") is True, "public dynamic setup unavailable")
    checks.check(summary.get("public_do_dynamics_step_available") is True, "public dynamic stepper unavailable")
    checks.check(summary.get("do_step_called") is False, "audit must not call do_step")
    checks.check(summary.get("heavy_numerical_run_invoked") is False, "audit must not invoke heavy run")
    checks.check(summary.get("default_policy") == "coarse_first_no_default_1e-4", "default policy changed")
    checks.check(summary.get("strict_public_policy_1e-4_required") is False, "strict 1e-4 incorrectly required")
    checks.check(summary.get("default_1e-4_required") is False, "default 1e-4 incorrectly required")
    checks.check(summary.get("accepted_dynamic_order_count") == 0, "dynamic order overclaimed")
    checks.check(summary.get("external_superiority_claim") is False, "external superiority overclaimed")
    checks.check(summary.get("required_next_runner") == plan.get("required_new_runner"), "row plan runner mismatch")
    checks.check(summary.get("row_plan_schema") == plan.get("schema"), "row plan schema mismatch")
    checks.check(summary.get("row_plan_count") == plan.get("row_count") == 24, "row plan count mismatch")

    checks.check(len(rows) == 4, "expected four setup audit rows")
    checks.check({row.get("model") for row in rows} == MODELS, "CSV model set changed")
    checks.check({row.get("setup_mode") for row in rows} == MODES, "CSV mode set changed")
    for row in rows:
        label = f"{row.get('model')}:{row.get('setup_mode')}"
        checks.check(row.get("setup_status") == "ok", f"{label} setup failed")
        checks.check(row.get("do_step_called") == "false", f"{label} called do_step")
        checks.check(row.get("heavy_numerical_run_invoked") == "false", f"{label} invoked heavy run")
        checks.check(row.get("default_policy") == "coarse_first_no_default_1e-4", f"{label} default policy changed")
        checks.check(row.get("strict_public_policy_1e-4_required") == "false", f"{label} strict 1e-4 changed")
        checks.check(row.get("accepted_dynamic_order") == "false", f"{label} dynamic order accepted")
        checks.check(row.get("body_count") == "3", f"{label} body count changed")
        checks.check(row.get("constraint_count") == "18", f"{label} constraint count changed")
        checks.check(row.get("generalized_dim") == "18", f"{label} generalized dim changed")
        checks.check(row.get("constraint_count_equals_generalized_dim") == "true", f"{label} constraint closure changed")
        checks.check(row.get("lambda_dim") == "18", f"{label} lambda dim changed")
        checks.check(row.get("mass_matrix_shape") == "9x9", f"{label} mass matrix shape changed")
        checks.check(row.get("inertia_matrix_shape") == "9x9", f"{label} inertia matrix shape changed")
        checks.check(row.get("force_vector_shape") == "9x1", f"{label} force vector shape changed")
        checks.check(row.get("lambda_vector_shape") == "18x1", f"{label} lambda vector shape changed")
        for key in [
            "api_get_phi",
            "api_get_phi_q",
            "api_get_phi_r",
            "api_get_pi",
            "api_get_nu",
            "api_get_gamma",
            "api_maybe_swap_gcons",
            "public_do_dynamics_step_available",
        ]:
            checks.check(row.get(key) == "true", f"{label} missing {key}")
        checks.check(row.get("local_gauss6_dynamic_runner_exists") == "false", f"{label} local runner overclaimed")
        checks.check(math.isfinite(float(row.get("runtime_sec", "nan"))), f"{label} runtime missing")
        if row.get("setup_mode") == "dynamics":
            checks.check(row.get("solver_type_after_initialize") == "DYNAMICS", f"{label} solver mode changed")
            checks.check(row.get("public_newton_unknown_dim") == "36", f"{label} public Newton dim changed")
            checks.check(
                row.get("fullva_true_dynamic_min_unknown_blocks") == "q|orientation|v|omega|a|alpha|lambda",
                f"{label} FullVA block contract changed",
            )
        else:
            checks.check(row.get("solver_type_after_initialize") == "KINEMATICS", f"{label} solver mode changed")
            checks.check(row.get("public_newton_unknown_dim") == "not_applicable", f"{label} kinematic Newton dim changed")

    normalized_report = " ".join(report.split())
    for token in [
        "Closed-Loop True-Dynamic Interface Audit",
        "setup-level interface verified; no trajectory rows run",
        "public/v046 `rA` system can be constructed in `dynamics` mode",
        "missing piece is the local `Gauss6/FullVA` dynamic trajectory stepper",
        "must not call the public `do_step` as the local method",
    ]:
        checks.check(token in report or token in normalized_report, f"report missing token: {token}")

    if checks.errors:
        print("closed-loop true dynamic interface audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("closed-loop true dynamic interface audit validation: PASS")
    print("dynamic_setup_ok=2/2")
    print("local_gauss6_dynamic_runner_exists=False")
    print("do_step_called=False")
    print("default_1e-4=False")
    print("accepted_dynamic_order=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
