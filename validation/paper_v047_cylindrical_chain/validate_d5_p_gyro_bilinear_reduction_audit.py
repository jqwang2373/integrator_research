#!/usr/bin/env python3
"""Validate the D5 P_gyro bilinear-reduction audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "D5_P_GYRO_BILINEAR_REDUCTION_AUDIT.json"
AUDIT_MD = PAPER / "D5_P_GYRO_BILINEAR_REDUCTION_AUDIT.md"


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


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(AUDIT_JSON)
        audit_md = AUDIT_MD.read_text(encoding="utf-8", errors="replace")
        readiness = read_json(PAPER / "D5_DYNAMIC_DEFECT_READINESS_AUDIT.json")
        p_tube = read_json(PAPER / "D5_P_TUBE_CONSTANTS_AUDIT.json")
        p_state = read_json(PAPER / "D5_P_STATE_LIFT_GAP_AUDIT.json")
        proof_manifest = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
    except Exception as exc:  # noqa: BLE001
        print(f"D5 P_gyro bilinear reduction audit validation: FAIL\n- {exc}")
        return 1

    summary = audit.get("summary", {})
    source = audit.get("source_consistency", {})
    proof = audit.get("proof_sketch", {})
    claim = audit.get("claim_boundary", {})
    conditional_rows = audit.get("conditional_gyro_row_bounds_under_p_state", {})
    rotational_rows = [
        row
        for row in readiness.get("rows", [])
        if isinstance(row, dict) and row.get("balance_block") == "rotational_euler_balance"
    ]

    checks.check(audit.get("schema") == "d5-p-gyro-bilinear-reduction-audit-v1", "schema changed")
    checks.check(
        audit.get("status") == "p_gyro_bilinear_reduction_closed_primitive_open",
        "status changed",
    )
    checks.check(audit.get("read_only") is True, "audit must be read-only")
    checks.check(audit.get("run_v047_invoked") is False, "run_v047 must not be invoked")
    checks.check(audit.get("submission_ready") is False, "submission readiness overclaimed")
    checks.check(audit.get("pc2_closed") is False, "PC2 unexpectedly closed")
    checks.check(audit.get("proof_gap_closed") is False, "proof gap unexpectedly closed")
    checks.check(audit.get("primitive_id") == "P_gyroscopic_lift", "primitive id changed")
    checks.check(audit.get("primitive_closed") is False, "P_gyro primitive unexpectedly closed")
    checks.check(audit.get("algebraic_reduction_closed") is True, "algebraic reduction not closed")
    checks.check(audit.get("term_bounds_proved") == 0, "Taylor term bounds unexpectedly proved")
    checks.check(audit.get("term_rows_conditionally_reduced") == 18, "rotational row count changed")
    checks.check(conditional_rows.get("closed") is True, "conditional gyro row corollary not closed")
    checks.check(conditional_rows.get("row_count") == 18, "conditional gyro row count changed")
    checks.check(conditional_rows.get("rows") == audit.get("rotational_row_ids"), "conditional gyro rows mismatch")
    checks.check(
        conditional_rows.get("constant") == "C_gyro = 2 M_omega J_max C_omega",
        "conditional gyro constant changed",
    )
    checks.check("P_state" in conditional_rows.get("assumption", ""), "conditional gyro P_state assumption missing")
    checks.check(conditional_rows.get("actual_taylor_bounds_proved") == 0, "conditional corollary overclaims Taylor bounds")
    checks.check(conditional_rows.get("primitive_closed") is False, "conditional corollary overclaims P_gyro")
    checks.check(conditional_rows.get("pc2_closed") is False, "conditional corollary overclaims PC2")
    checks.check(summary.get("closed_subproof_count") == 3, "closed subproof count changed")
    checks.check(summary.get("required_subproof_count") == 3, "required subproof count changed")
    checks.check(summary.get("open_dependency_count") == 1, "open dependency count changed")
    checks.check(summary.get("term_rows_conditionally_reduced") == 18, "summary row count changed")
    checks.check(
        summary.get("conditional_gyro_row_bounds_under_p_state") == 18,
        "summary conditional gyro row count changed",
    )
    checks.check(summary.get("stage_body_pairs") == 6, "stage/body pair count changed")
    checks.check(summary.get("component_rows") == 18, "component row count changed")
    checks.check(summary.get("p_tube_closed") is True and p_tube.get("primitive_closed") is True, "P_tube link missing")
    checks.check(summary.get("p_state_closed") is False and p_state.get("primitive_closed") is False, "P_state unexpectedly closed")
    checks.check(summary.get("pc2_closed") is False, "summary PC2 unexpectedly closed")
    checks.check(len(audit.get("closed_subproofs", [])) == 3, "closed subproof list changed")
    checks.check(audit.get("open_dependencies") == ["P_state angular-velocity lift O(h^7)"], "open dependency changed")
    checks.check(proof.get("map") == "G(omega)=omega x J omega", "proof map changed")
    checks.check("omega_hat-omega" in proof.get("difference_identity", ""), "difference identity missing")
    checks.check("2 M ||J||" in proof.get("compact_bound", ""), "compact bound missing")
    checks.check("P_state" in proof.get("conditional_rate", ""), "P_state conditional rate missing")
    checks.check(audit.get("manuscript_link", {}).get("main_tex_present") is True, "main TeX lemma link missing")
    checks.check(audit.get("manuscript_link", {}).get("flat_tex_present") is True, "flat TeX lemma link missing")
    checks.check(source.get("readiness_schema") == readiness.get("schema"), "readiness schema link missing")
    checks.check(
        source.get("readiness_status") == "d5_direct_substitution_closure_recorded_primitive_taylor_route_open",
        "readiness direct-route/primitive-route boundary changed",
    )
    checks.check(
        source.get("readiness_pc2_closed") is True and readiness.get("pc2_closed") is True,
        "readiness direct-substitution PC2 closure missing",
    )
    checks.check(
        source.get("readiness_direct_substitution_closed_rows") == 36,
        "readiness direct-substitution row count changed",
    )
    checks.check(
        source.get("readiness_primitive_taylor_closed_rows") == 0,
        "readiness unexpectedly closes primitive Taylor rows",
    )
    checks.check(source.get("rotational_rows") == 18 and len(rotational_rows) == 18, "rotational source rows changed")
    checks.check(source.get("p_tube_closed") is True, "P_tube source link missing")
    checks.check(source.get("p_state_closed") is False, "P_state source link changed")
    checks.check(source.get("proof_manifest_pc2_closed") is True, "proof manifest direct PC2 closure not reflected")
    checks.check("P_gyro primitive closure" in claim.get("forbidden_now", []), "P_gyro closure not forbidden")
    checks.check(
        proof_manifest.get("closure_state", {}).get("pc2_closed_by_direct_substitution") is True,
        "proof manifest direct-substitution closure missing",
    )
    checks.check(
        proof_manifest.get("closure_state", {}).get("primitive_lift_route_closed") is False,
        "proof manifest unexpectedly closes primitive lift route",
    )

    for token in [
        "Status: **P_gyro bilinear reduction closed; primitive remains open**.",
        "Closed P_gyro subproofs: `3/3`.",
        "Open dependencies: `1`.",
        "Rotational Newton-Euler rows conditionally reduced: `18/18`.",
        "P_state closed: `False`.",
        "P_gyro primitive closed: `False`.",
        "Primitive/Taylor PC2 route closed: `False`.",
        "`||G(omega_hat)-G(omega)|| <= 2 M ||J|| ||omega_hat-omega||`.",
        "`C_gyro = 2 M_omega J_max C_omega`",
        "Conditional gyro row bounds under P_state: `18/18`.",
        "Actual Taylor bounds proved by this audit remain `0`.",
        "`P_state` remains open, so `P_gyro` remains open.",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("D5 P_gyro bilinear reduction audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("D5 P_gyro bilinear reduction audit validation: PASS")
    print("closed_subproofs=3/3")
    print("rotational_rows_conditionally_reduced=18/18")
    print("p_gyro_closed=False")
    print("pc2_closed=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
