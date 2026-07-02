#!/usr/bin/env python3
"""Validate the finite Newton-tolerance regime sweep."""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
SWEEP_JSON = PAPER / "PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.json"
SWEEP_CSV = PAPER / "PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.csv"
SWEEP_MD = PAPER / "PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.md"
SOLVER_AUDIT_JSON = PAPER / "PROOF_SOLVER_SCALE_AUDIT.json"
SOLVER_AUDIT_MD = PAPER / "PROOF_SOLVER_SCALE_AUDIT.md"
MANIFEST = PAPER / "SUBMISSION_ARTIFACT_MANIFEST.json"

EXPECTED_H = [0.04, 0.02, 0.01, 0.005]
EXPECTED_POLICIES = ["fixed_1e-10", "scaled_h7_c1e4", "scaled_h8_c1e6"]
EXPECTED_T_FINAL = 0.08
EXPECTED_REFERENCE_H = 0.0025
EXPECTED_REFERENCE_TOL = 1.0e-13


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8", errors="replace")


def close(left: Any, right: Any, tol: float = 1.0e-12) -> bool:
    left_f = float(left)
    right_f = float(right)
    return abs(left_f - right_f) <= tol * max(1.0, abs(left_f), abs(right_f))


def contains_normalized(text: str, token: str) -> bool:
    return token in text or " ".join(token.split()) in " ".join(text.split())


def main() -> int:
    checks = Checks()
    try:
        sweep = read_json(SWEEP_JSON)
        audit = read_json(SOLVER_AUDIT_JSON)
        manifest = read_json(MANIFEST)
        sweep_md = read_text(SWEEP_MD)
        audit_md = read_text(SOLVER_AUDIT_MD)
        with SWEEP_CSV.open(newline="", encoding="utf-8") as handle:
            csv_rows = list(csv.DictReader(handle))
    except Exception as exc:  # noqa: BLE001
        print(f"proof_solver_tolerance_regime_sweep=FAIL\n- {exc}")
        return 1

    policies = sweep.get("policies", [])
    policy_by_name = {policy.get("name"): policy for policy in policies}
    checks.check(sweep.get("schema") == "proof-solver-tolerance-regime-sweep-v1", "sweep schema changed")
    checks.check(
        sweep.get("status") == "finite_tolerance_regime_sweep_recorded_not_theorem_closure",
        "sweep status changed",
    )
    checks.check(sweep.get("case") == "cylindrical_smooth", "sweep case changed")
    checks.check(sweep.get("accepted_method") == "Gauss6/FullVA", "accepted method changed")
    checks.check(sweep.get("h_values") == EXPECTED_H, "h values changed")
    checks.check(close(sweep.get("t_final"), EXPECTED_T_FINAL), "t_final changed")
    checks.check(sweep.get("policy_count") == len(EXPECTED_POLICIES), "policy count changed")
    checks.check(sweep.get("total_rows_checked") == len(EXPECTED_H) * len(EXPECTED_POLICIES), "row count changed")
    checks.check(sweep.get("total_steps_checked") == 90, "step count changed")
    checks.check(sweep.get("all_rows_converged") is True, "not all rows converged")
    checks.check(sweep.get("finite_tolerance_regime_sweep_recorded") is True, "finite regime marker missing")
    checks.check(
        sweep.get("finite_h_scaled_tolerance_sweep_recorded") is True,
        "finite h-scaled regime marker missing",
    )
    checks.check(
        sweep.get("finite_h_scaled_policy_names") == ["scaled_h7_c1e4", "scaled_h8_c1e6"],
        "finite h-scaled policy names changed",
    )
    checks.check(sweep.get("finite_h_scaled_policy_rows") == 8, "finite h-scaled row count changed")
    checks.check(sweep.get("finite_h_scaled_policy_steps") == 60, "finite h-scaled step count changed")
    checks.check(
        float(sweep.get("finite_h_scaled_position_order_floor", math.nan)) > 6.0,
        "finite h-scaled position order floor too small",
    )
    checks.check(
        float(sweep.get("finite_h_scaled_velocity_order_floor", math.nan)) > 6.0,
        "finite h-scaled velocity order floor too small",
    )
    checks.check(sweep.get("scaled_h7_residual_bound_satisfied") is True, "h7 residual bound not satisfied")
    checks.check(sweep.get("scaled_h8_residual_bound_satisfied") is True, "h8 residual bound not satisfied")
    checks.check(sweep.get("scaled_tolerance_sweep_recorded") is False, "sweep overclaims theorem-level scaled sweep")
    checks.check(sweep.get("eta_h_O_h7_solver_policy_evidence") is False, "sweep overclaims eta-h proof")
    checks.check(sweep.get("fixed_tolerance_runs_are_asymptotic_proof") is False, "fixed tolerance overclaim")
    checks.check(sweep.get("theorem_level_solver_proof_closed") is False, "sweep overclaims theorem closure")
    checks.check(sweep.get("dynamic_symbolic_oracle_complete") is False, "sweep overclaims symbolic oracle")
    checks.check(
        sweep.get("stage_residual_O_h7_implementation_defect_proved") is False,
        "sweep overclaims implementation defect",
    )
    checks.check(sweep.get("submission_ready") is False, "sweep overclaims submission")
    checks.check(len(csv_rows) == len(EXPECTED_H) * len(EXPECTED_POLICIES), "CSV row count changed")

    reference = sweep.get("reference", {})
    checks.check(reference.get("policy") == "reference_fixed_1e-13", "reference policy changed")
    checks.check(close(reference.get("h"), EXPECTED_REFERENCE_H), "reference h changed")
    checks.check(close(reference.get("eta_target"), EXPECTED_REFERENCE_TOL), "reference tolerance changed")
    checks.check(reference.get("steps") == 32, "reference step count changed")
    checks.check(reference.get("status") == "ok", "reference did not converge")

    checks.check(set(policy_by_name) == set(EXPECTED_POLICIES), "policy names changed")
    for name in EXPECTED_POLICIES:
        policy = policy_by_name.get(name, {})
        checks.check(policy.get("row_count") == len(EXPECTED_H), f"{name} row count changed")
        checks.check(policy.get("ok_row_count") == len(EXPECTED_H), f"{name} ok count changed")
        checks.check(policy.get("total_steps_checked") == 30, f"{name} step count changed")
        rows = policy.get("rows", [])
        checks.check(len(rows) == len(EXPECTED_H), f"{name} rows length changed")
        for row, h in zip(rows, EXPECTED_H):
            checks.check(close(row.get("h"), h), f"{name} h changed")
            checks.check(close(row.get("t_final"), EXPECTED_T_FINAL), f"{name} t_final changed")
            checks.check(row.get("status") == "ok", f"{name} row status not ok")
            checks.check(row.get("all_steps_ok") is True, f"{name} step status not ok")
            checks.check(row.get("min_final_jacobian_rank") == 132, f"{name} rank changed")
            checks.check(float(row.get("position_error", math.inf)) > 0.0, f"{name} position error invalid")
            checks.check(float(row.get("velocity_error", math.inf)) > 0.0, f"{name} velocity error invalid")
        orders = policy.get("orders", {})
        for key in ["position_order", "velocity_order", "orientation_order", "angular_velocity_order"]:
            checks.check(math.isfinite(float(orders.get(key, math.nan))), f"{name} {key} invalid")
        checks.check(float(policy.get("max_final_residual_over_h7", math.inf)) > 0.0, f"{name} h7 ratio invalid")
        checks.check(float(policy.get("max_final_residual_over_h8", math.inf)) > 0.0, f"{name} h8 ratio invalid")

    fixed = policy_by_name.get("fixed_1e-10", {})
    scaled_h7 = policy_by_name.get("scaled_h7_c1e4", {})
    scaled_h8 = policy_by_name.get("scaled_h8_c1e6", {})
    checks.check(float(fixed.get("max_final_residual_over_h7", -1.0)) > 1.0, "fixed policy should expose residual/h7 growth")
    checks.check(float(scaled_h7.get("max_final_residual_over_h7", math.inf)) < 1.0e4, "h7 policy exceeds c")
    checks.check(float(scaled_h8.get("max_final_residual_over_h8", math.inf)) < 1.0e6, "h8 policy exceeds c")

    execution = sweep.get("execution_policy", {})
    checks.check(execution.get("imports_accepted_residual_functions") is True, "sweep no longer imports accepted residuals")
    checks.check(execution.get("heavy_numerical_run_invoked") is False, "sweep invoked heavy numerical run")
    checks.check(execution.get("default_1e-4_required") is False, "sweep requires default 1e-4")
    checks.check(execution.get("run_v047_invoked") is False, "sweep invoked run_v047")

    audit_sweep = audit.get("finite_tolerance_regime_sweep", {})
    checks.check(
        audit_sweep.get("schema") == "proof-solver-tolerance-regime-sweep-v1",
        "solver audit missing regime sweep schema",
    )
    checks.check(audit_sweep.get("source_json") == "PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.json", "audit JSON path missing")
    checks.check(audit_sweep.get("source_csv") == "PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.csv", "audit CSV path missing")
    checks.check(audit_sweep.get("policy_count") == len(EXPECTED_POLICIES), "audit policy count changed")
    checks.check(audit_sweep.get("total_rows_checked") == len(EXPECTED_H) * len(EXPECTED_POLICIES), "audit rows changed")
    checks.check(audit_sweep.get("total_steps_checked") == 90, "audit steps changed")
    checks.check(audit_sweep.get("all_rows_converged") is True, "audit all-rows marker changed")
    checks.check(
        audit_sweep.get("finite_h_scaled_tolerance_sweep_recorded") is True,
        "audit missing finite h-scaled sweep marker",
    )
    checks.check(
        audit_sweep.get("finite_h_scaled_policy_names") == ["scaled_h7_c1e4", "scaled_h8_c1e6"],
        "audit finite h-scaled policy names changed",
    )
    checks.check(audit_sweep.get("finite_h_scaled_policy_rows") == 8, "audit finite h-scaled rows changed")
    checks.check(audit_sweep.get("finite_h_scaled_policy_steps") == 60, "audit finite h-scaled steps changed")
    checks.check(
        float(audit_sweep.get("finite_h_scaled_velocity_order_floor", math.nan)) > 6.0,
        "audit finite h-scaled velocity order floor too small",
    )
    checks.check(audit_sweep.get("theorem_level_solver_proof_closed") is False, "audit sweep overclaims theorem closure")
    checks.check(audit_sweep.get("eta_h_O_h7_solver_policy_evidence") is False, "audit sweep overclaims eta-h proof")

    boundary = audit.get("proof_boundary", {})
    checks.check(
        boundary.get("finite_tolerance_regime_sweep_recorded") is True,
        "solver audit boundary missing regime sweep marker",
    )
    checks.check(
        boundary.get("finite_h_scaled_tolerance_sweep_recorded") is True,
        "solver audit boundary missing finite h-scaled sweep marker",
    )
    checks.check(boundary.get("scaled_tolerance_sweep_recorded") is False, "solver audit overclaims scaled sweep")
    checks.check(boundary.get("eta_h_O_h7_solver_policy_evidence") is False, "solver audit overclaims eta-h proof")

    for file_label in [
        "PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.md",
        "PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.json",
        "PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.csv",
    ]:
        checks.check(file_label in manifest.get("evidence_anchors", []), f"manifest missing {file_label}")
    checks.check(
        "validate_proof_solver_tolerance_regime_sweep.py" in manifest.get("validators", []),
        "manifest missing regime sweep validator",
    )

    for token in [
        "Proof Solver Tolerance-Regime Sweep",
        "fixed `1e-10`",
        "`c h^7`",
        "`c h^8`",
        "Finite tolerance regime sweep recorded: `True`",
        "Finite h-scaled tolerance sweep recorded: `True`",
        "Finite h-scaled policy names: `['scaled_h7_c1e4', 'scaled_h8_c1e6']`",
        "Theorem-level scaled tolerance sweep recorded: `False`",
        "eta_h_O_h7_solver_policy_evidence: `False`",
        "does not close P6 theorem-level solver-policy evidence",
        "The active 36-row direct D5 stage-residual certificate is closed separately",
        "validate_proof_solver_tolerance_regime_sweep.py",
    ]:
        checks.check(contains_normalized(sweep_md, token), f"sweep MD missing token: {token}")
    for token in [
        "finite tolerance-regime sweep",
        "PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.json",
        "fixed `1e-10`, `c h^7`, and `c h^8`",
        "finite_tolerance_regime_sweep_recorded=true",
        "finite_h_scaled_tolerance_sweep_recorded=true",
    ]:
        checks.check(contains_normalized(audit_md, token), f"solver audit MD missing token: {token}")

    forbidden = set(sweep.get("forbidden_claims", []))
    for claim in [
        "theorem_level_solver_proof_closed_true",
        "eta_h_O_h7_solver_policy_evidence_true",
        "fixed_tolerance_runs_are_asymptotic_proof_true",
        "scaled_tolerance_sweep_recorded_true",
        "dynamic_symbolic_oracle_complete_true",
        "stage_residual_O_h7_implementation_defect_proved_true",
        "submission_ready_true",
    ]:
        checks.check(claim in forbidden, f"forbidden claim missing: {claim}")

    if checks.errors:
        print("proof_solver_tolerance_regime_sweep=FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("proof_solver_tolerance_regime_sweep=PASS")
    print("policies=3")
    print("rows_checked=12")
    print("steps_checked=90")
    print("finite_tolerance_regime_sweep_recorded=True")
    print("finite_h_scaled_tolerance_sweep_recorded=True")
    print("scaled_tolerance_sweep_recorded=False")
    print("eta_h_O_h7_solver_policy_evidence=False")
    print("theorem_level_solver_proof_closed=False")
    print("default_1e-4=False")
    print("run_v047_invoked=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
