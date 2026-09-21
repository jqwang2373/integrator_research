#!/usr/bin/env python3
"""Validate the D5 P_acc acceleration-map definition audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "D5_P_ACC_MAP_DEFINITION_AUDIT.json"
AUDIT_MD = PAPER / "D5_P_ACC_MAP_DEFINITION_AUDIT.md"


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
        primitive_reduction = read_json(PAPER / "D5_PRIMITIVE_BOUND_REDUCTION_AUDIT.json")
        term_budget = read_json(PAPER / "D5_TAYLOR_TERM_BUDGET_AUDIT.json")
    except Exception as exc:  # noqa: BLE001
        print(f"D5 P_acc map definition audit validation: FAIL\n- {exc}")
        return 1

    summary = audit.get("summary", {})
    source = audit.get("source_consistency", {})
    map_def = audit.get("map_definition", {})
    anti = audit.get("anti_circularity_gate", {})
    claim = audit.get("claim_boundary", {})

    checks.check(audit.get("schema") == "d5-p-acc-map-definition-audit-v1", "schema changed")
    checks.check(audit.get("status") == "p_acc_map_definition_closed_lift_open", "status changed")
    checks.check(audit.get("read_only") is True, "audit must be read-only")
    checks.check(audit.get("run_v047_invoked") is False, "run_v047 must not be invoked")
    checks.check(audit.get("submission_ready") is False, "submission readiness overclaimed")
    checks.check(audit.get("pc2_closed") is False, "PC2 unexpectedly closed")
    checks.check(audit.get("proof_gap_closed") is False, "proof gap unexpectedly closed")
    checks.check(audit.get("primitive_id") == "P_acceleration_lift", "primitive id changed")
    checks.check(audit.get("primitive_closed") is False, "P_acc unexpectedly closed")
    checks.check(audit.get("pa1_map_definition_closed") is True, "PA1 map definition not closed")
    checks.check(audit.get("acceleration_lift_rate_proved") is False, "acceleration lift rate overclaimed")
    checks.check(audit.get("term_bounds_proved") == 0, "Taylor bounds unexpectedly proved")
    checks.check(audit.get("term_rows_using_p_acc") == 36, "P_acc term-row count changed")
    checks.check(audit.get("term_rows_conditionally_mapped") == 36, "mapped acceleration row count changed")
    checks.check(audit.get("translational_acceleration_rows") == 18, "translational acceleration rows changed")
    checks.check(audit.get("angular_acceleration_rows") == 18, "angular acceleration rows changed")
    checks.check(summary.get("closed_subproof_count") == 1, "closed subproof count changed")
    checks.check(summary.get("required_subproof_count") == 4, "required subproof count changed")
    checks.check(summary.get("open_subproof_count") == 3, "open subproof count changed")
    checks.check(summary.get("term_rows_using_p_acc") == 36, "summary P_acc row count changed")
    checks.check(summary.get("term_rows_conditionally_mapped") == 36, "summary mapped row count changed")
    checks.check(summary.get("translational_acceleration_rows") == 18, "summary translational rows changed")
    checks.check(summary.get("angular_acceleration_rows") == 18, "summary angular rows changed")
    checks.check(summary.get("acceleration_lift_rate_proved") is False, "summary overclaims acceleration lift")
    checks.check(summary.get("pc2_closed") is False, "summary overclaims PC2")
    checks.check(map_def.get("map_name") == "A_h^acc", "map name changed")
    checks.check(map_def.get("acceleration_block") == ["a_i", "alpha_i"], "acceleration block changed")
    checks.check(map_def.get("row_terms") == ["T_acceleration_lift", "R_angular_acceleration_lift"], "row terms changed")
    checks.check(map_def.get("total_rows") == 36, "map total row count changed")
    checks.check(map_def.get("stage_body_pairs") == 6, "stage/body pair count changed")
    checks.check(map_def.get("codomain") == "R^36", "map codomain changed")
    checks.check(anti.get("map_definition_is_not_acceleration_lift_rate") is True, "map/rate boundary missing")
    checks.check(anti.get("velocity_collocation_rate_not_assumed") is True, "velocity collocation boundary missing")
    checks.check(anti.get("dynamic_balance_disallowed_as_acceleration_lift_proof") is True, "dynamic balance not barred")
    checks.check(anti.get("stage_residual_perturbation_lemma_disallowed_as_input") is True, "stage lemma not barred")
    checks.check(audit.get("manuscript_link", {}).get("main_tex_present") is True, "main TeX lemma link missing")
    checks.check(audit.get("manuscript_link", {}).get("flat_tex_present") is True, "flat TeX lemma link missing")
    checks.check(source.get("primitive_reduction_schema") == primitive_reduction.get("schema"), "primitive reduction schema link missing")
    checks.check(source.get("primitive_reduction_pc2_closed") is False, "primitive reduction unexpectedly closes PC2")
    checks.check(source.get("term_budget_schema") == term_budget.get("schema"), "term budget schema link missing")
    checks.check(source.get("term_budget_pc2_closed") is False, "term budget unexpectedly closes PC2")
    checks.check(source.get("term_rows") == 36, "source term row count changed")
    checks.check(source.get("translational_rows") == 18, "source translational row count changed")
    checks.check(source.get("angular_rows") == 18, "source angular row count changed")
    checks.check("P_acc primitive closure" in claim.get("forbidden_now", []), "P_acc closure not forbidden")
    checks.check("acceleration lift O(h^7) proved" in claim.get("forbidden_now", []), "acceleration lift overclaim not forbidden")

    for token in [
        "Status: **P_acc map definition closed; lift remains open**.",
        "Closed P_acc subproofs: `1/4`.",
        "Open P_acc subproofs: `3`.",
        "Acceleration-map rows: `36/36`.",
        "Translational/angular acceleration rows: `18/18`.",
        "P_acc primitive closed: `False`.",
        "Acceleration lift rate proved: `False`.",
        "Primitive/Taylor PC2 route closed: `False`.",
        "`A_h^acc(A)` binds `A=(a_i, alpha_i)`",
        "PA1 map definition is closed.",
        "PA2 velocity-collocation-to-acceleration lift proof remains open.",
        "`P_acc` remains open.",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("D5 P_acc map definition audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("D5 P_acc map definition audit validation: PASS")
    print("closed_subproofs=1/4")
    print("acceleration_map_rows=36/36")
    print("p_acc_closed=False")
    print("pc2_closed=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
