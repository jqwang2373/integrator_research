#!/usr/bin/env python3
"""Read-only validator for the proof numerical scale audit."""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "PROOF_NUMERICAL_SCALE_AUDIT.json"
AUDIT_MD = PAPER / "PROOF_NUMERICAL_SCALE_AUDIT.md"
SOURCE_CSV = PAPER.parent / "v047_cylindrical_chain_pipeline" / "results" / "cylindrical_chain_convergence.csv"


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


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def contains_normalized(text: str, token: str) -> bool:
    return token in text or " ".join(token.split()) in " ".join(text.split())


def require_tokens(checks: Checks, text: str, tokens: list[str], label: str) -> None:
    for token in tokens:
        checks.check(contains_normalized(text, token), f"{label} missing token: {token}")


def fit_order(rows: list[dict[str, str]], key: str) -> float:
    xs = [math.log(float(row["h"])) for row in rows]
    ys = [math.log(float(row[key])) for row in rows]
    x_bar = sum(xs) / len(xs)
    y_bar = sum(ys) / len(ys)
    return sum((x - x_bar) * (y - y_bar) for x, y in zip(xs, ys)) / sum((x - x_bar) ** 2 for x in xs)


def pair_orders(rows: list[dict[str, str]], key: str) -> list[float]:
    values = [float(row[key]) for row in rows]
    return [math.log(values[i] / values[i + 1], 2.0) for i in range(len(values) - 1)]


def h_power_ratios(rows: list[dict[str, str]], key: str, power: int) -> list[float]:
    return [float(row[key]) / (float(row["h"]) ** power) for row in rows]


def close_list(actual: list[float], expected: Any, tol: float = 1.0e-12) -> bool:
    if not isinstance(expected, list) or len(actual) != len(expected):
        return False
    return all(abs(a - float(e)) <= tol * max(1.0, abs(a), abs(float(e))) for a, e in zip(actual, expected))


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(AUDIT_JSON)
        audit_md = read_text(AUDIT_MD)
        rows = read_csv_rows(SOURCE_CSV)
    except Exception as exc:  # noqa: BLE001 - concise CLI failure.
        print(f"proof_numerical_scale_audit=FAIL\n- {exc}")
        return 1

    projected = [
        row
        for row in rows
        if row.get("case") == "cylindrical_smooth" and row.get("endpoint_mode") == "projected_velocity"
    ]
    raw = [
        row
        for row in rows
        if row.get("case") == "cylindrical_smooth" and row.get("endpoint_mode") == "raw_endpoint"
    ]
    projected.sort(key=lambda row: float(row["h"]), reverse=True)
    raw.sort(key=lambda row: float(row["h"]), reverse=True)

    checks.check(audit.get("schema") == "proof-numerical-scale-audit-v1", "schema changed")
    checks.check(
        audit.get("status") == "finite_run_global_scale_diagnostic_not_asymptotic_solver_proof",
        "status changed",
    )
    checks.check(audit.get("submission_ready") is False, "audit incorrectly claims submission ready")
    checks.check(audit.get("accepted_method") == "Gauss6/FullVA", "accepted method changed")
    checks.check(len(projected) == 3, "projected smooth row count changed")
    checks.check(len(raw) == 3, "raw smooth row count changed")
    checks.check([float(row["h"]) for row in projected] == [0.04, 0.02, 0.01], "projected h values changed")
    checks.check([float(row["h"]) for row in raw] == [0.04, 0.02, 0.01], "raw h values changed")

    execution = audit.get("execution_policy", {})
    checks.check(execution.get("read_only_audit") is True, "audit lost read-only marker")
    checks.check(execution.get("default_step_policy") == "coarse_first_no_default_1e-4", "default policy changed")
    checks.check(execution.get("default_1e-4_required") is False, "audit incorrectly requires default 1e-4")
    checks.check(execution.get("heavy_numerical_run_invoked") is False, "audit invoked heavy numerical run")
    checks.check(execution.get("run_v047_invoked") is False, "audit invoked run_v047")

    projected_orders = audit.get("smooth_projected_velocity_global_orders", {})
    checks.check(
        abs(projected_orders.get("position_error_fit", 0.0) - fit_order(projected, "position_error")) < 1.0e-12,
        "projected position fit changed",
    )
    checks.check(
        abs(projected_orders.get("velocity_error_fit", 0.0) - fit_order(projected, "velocity_error")) < 1.0e-12,
        "projected velocity fit changed",
    )
    checks.check(
        close_list(pair_orders(projected, "position_error"), projected_orders.get("position_error_pair_orders")),
        "projected position pair orders changed",
    )
    checks.check(
        close_list(pair_orders(projected, "velocity_error"), projected_orders.get("velocity_error_pair_orders")),
        "projected velocity pair orders changed",
    )

    endpoint_orders = audit.get("endpoint_global_closure_orders", {})
    checks.check(
        abs(endpoint_orders.get("raw_endpoint_position_constraint_fit", 0.0) - fit_order(raw, "max_endpoint_constraint_norm"))
        < 1.0e-12,
        "raw endpoint position-constraint fit changed",
    )
    checks.check(
        abs(endpoint_orders.get("raw_endpoint_velocity_constraint_fit", 0.0) - fit_order(raw, "max_endpoint_velocity_constraint_norm"))
        < 1.0e-12,
        "raw endpoint velocity-constraint fit changed",
    )
    checks.check(
        abs(
            endpoint_orders.get("projected_velocity_position_constraint_fit", 0.0)
            - fit_order(projected, "max_endpoint_constraint_norm")
        )
        < 1.0e-12,
        "projected endpoint position-constraint fit changed",
    )
    checks.check(
        endpoint_orders.get("projected_velocity_constraint_interpretation")
        == "roundoff-limited after projection; do not fit as solver-tolerance proof",
        "projected velocity-constraint interpretation changed",
    )

    ratios = audit.get("global_h6_scale_ratios", {})
    checks.check(
        close_list(h_power_ratios(projected, "position_error", 6), ratios.get("projected_position_error_over_h6")),
        "projected position h6 ratios changed",
    )
    checks.check(
        close_list(h_power_ratios(projected, "velocity_error", 6), ratios.get("projected_velocity_error_over_h6")),
        "projected velocity h6 ratios changed",
    )
    checks.check(
        close_list(h_power_ratios(raw, "max_endpoint_constraint_norm", 6), ratios.get("raw_position_constraint_over_h6")),
        "raw endpoint position-constraint h6 ratios changed",
    )
    checks.check(
        close_list(h_power_ratios(raw, "max_endpoint_velocity_constraint_norm", 6), ratios.get("raw_velocity_constraint_over_h6")),
        "raw endpoint velocity-constraint h6 ratios changed",
    )

    boundary = audit.get("proof_boundary", {})
    checks.check(boundary.get("local_defect_order_required") == 7, "local defect order changed")
    checks.check(boundary.get("global_error_order_supported") == 6, "global error order changed")
    checks.check(boundary.get("finite_run_error_scale_supports_order_six") is True, "lost order-six scale marker")
    checks.check(
        boundary.get("endpoint_global_closure_scale_supports_local_h7_budget") is True,
        "lost endpoint scale marker",
    )
    checks.check(
        boundary.get("endpoint_functional_is_velocity_kkt_not_raw_position_monitor") is True,
        "lost endpoint functional versus raw monitor boundary",
    )
    checks.check(
        boundary.get("raw_position_endpoint_defect_is_diagnostic_monitor") is True,
        "lost raw endpoint position diagnostic-monitor boundary",
    )
    checks.check(
        boundary.get("finite_endpoint_diagnostics_do_not_discharge_endpoint_p2") is True,
        "lost P2 endpoint-hypothesis boundary",
    )
    checks.check(boundary.get("newton_residual_norm_recorded") is False, "audit overclaims Newton residual availability")
    checks.check(boundary.get("eta_h_O_h7_solver_policy_evidence") is False, "audit overclaims solver-policy proof")
    checks.check(boundary.get("fixed_tolerance_runs_are_asymptotic_proof") is False, "audit overclaims fixed tolerances")
    checks.check(
        boundary.get("stage_residual_O_h7_implementation_defect_proved_by_this_audit") is False,
        "audit overclaims implementation defect proof by numerical scale diagnostic",
    )
    checks.check(boundary.get("dynamic_symbolic_oracle_complete") is False, "audit overclaims symbolic oracle")
    checks.check(boundary.get("external_superiority_claim") is False, "audit overclaims external superiority")

    require_tokens(
        checks,
        audit_md,
        [
            "Proof Numerical Scale Audit",
            "finite-run scale diagnostic, not an asymptotic solver proof",
            "coarse_first_no_default_1e-4",
            "default_1e-4_required=false",
            "7.160828003417387",
            "7.066182539651858",
            "5.985100758394371",
            "6.072290794930567",
            "global sixth-order error budget",
            "local O(h^7) endpoint-closure budget",
            "velocity-level/KKT closure subsystem",
            "raw position defect is a separate diagnostic monitor",
            "do not discharge the retained P2 endpoint raw-defect/right-inverse hypothesis",
            "eta_h_O_h7_solver_policy_evidence=false",
            "stage_residual_O_h7_implementation_defect_proved_by_this_audit=false",
            "validate_proof_numerical_scale_audit.py",
        ],
        "PROOF_NUMERICAL_SCALE_AUDIT.md",
    )

    forbidden = set(audit.get("forbidden_claims", []))
    for token in [
        "proof_unconditional",
        "eta_h_O_h7_solver_policy_evidence_true",
        "fixed_tolerance_runs_are_asymptotic_proof_true",
        "stage_residual_O_h7_implementation_defect_proved_by_this_audit_true",
        "dynamic_symbolic_oracle_complete_true",
        "external_superiority_claim_true",
        "default_1e-4_required_true",
        "submission_ready_true",
    ]:
        checks.check(token in forbidden, f"forbidden claim missing: {token}")

    if checks.errors:
        print("proof_numerical_scale_audit=FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("proof_numerical_scale_audit=PASS")
    print("finite_run_error_scale_supports_order_six=True")
    print(f"projected_position_order={projected_orders.get('position_error_fit'):.6f}")
    print(f"projected_velocity_order={projected_orders.get('velocity_error_fit'):.6f}")
    print("endpoint_global_closure_scale_supports_local_h7_budget=True")
    print("endpoint_functional_is_velocity_kkt_not_raw_position_monitor=True")
    print("finite_endpoint_diagnostics_do_not_discharge_endpoint_p2=True")
    print("eta_h_O_h7_solver_policy_evidence=False")
    print("stage_residual_O_h7_implementation_defect_proved_by_this_audit=False")
    print("default_1e-4=False")
    print("run_v047_invoked=False")
    print("submission_ready=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
