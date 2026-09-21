#!/usr/bin/env python3
"""Validate the D5 P_state non-dynamic map-definition audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "D5_P_STATE_MAP_DEFINITION_AUDIT.json"
AUDIT_MD = PAPER / "D5_P_STATE_MAP_DEFINITION_AUDIT.md"


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
        kinematic = read_json(PAPER / "KINEMATIC_ROW_DEFECT_CERTIFICATE.json")
        primitive_reduction = read_json(PAPER / "D5_PRIMITIVE_BOUND_REDUCTION_AUDIT.json")
        term_budget = read_json(PAPER / "D5_TAYLOR_TERM_BUDGET_AUDIT.json")
        p_state_anticircularity = read_json(PAPER / "D5_P_STATE_ANTICIRCULARITY_AUDIT.json")
    except Exception as exc:  # noqa: BLE001
        print(f"D5 P_state map definition audit validation: FAIL\n- {exc}")
        return 1

    summary = audit.get("summary", {})
    source = audit.get("source_consistency", {})
    map_def = audit.get("map_definition", {})
    anti = audit.get("anti_circularity_gate", {})
    claim = audit.get("claim_boundary", {})
    row_families = map_def.get("row_families", [])
    proof_scope = kinematic.get("proof_scope", {})

    checks.check(audit.get("schema") == "d5-p-state-map-definition-audit-v1", "schema changed")
    checks.check(audit.get("status") == "p_state_map_definition_closed_lift_open", "status changed")
    checks.check(audit.get("read_only") is True, "audit must be read-only")
    checks.check(audit.get("run_v047_invoked") is False, "run_v047 must not be invoked")
    checks.check(audit.get("submission_ready") is False, "submission readiness overclaimed")
    checks.check(audit.get("pc2_closed") is False, "PC2 unexpectedly closed")
    checks.check(audit.get("proof_gap_closed") is False, "proof gap unexpectedly closed")
    checks.check(audit.get("primitive_id") == "P_state_lift", "primitive id changed")
    checks.check(audit.get("primitive_closed") is False, "P_state unexpectedly closed")
    checks.check(audit.get("ps1_map_definition_closed") is True, "PS1 map definition not closed")
    checks.check(audit.get("state_lift_rate_proved") is False, "state lift rate overclaimed")
    checks.check(audit.get("local_inverse_or_inf_sup_proved") is False, "inverse/inf-sup overclaimed")
    checks.check(audit.get("term_bounds_proved") == 0, "Taylor bounds unexpectedly proved")
    checks.check(audit.get("term_rows_using_p_state") == 126, "P_state term-row count changed")
    checks.check(audit.get("p_state_term_rows_in_budget") == 126, "P_state term-budget count changed")
    checks.check(summary.get("closed_subproof_count") == 1, "closed subproof count changed")
    checks.check(summary.get("required_subproof_count") == 4, "required subproof count changed")
    checks.check(summary.get("open_subproof_count") == 2, "open subproof count changed")
    checks.check(summary.get("aggregate_p_state_subproofs_closed_after_ps4") == 2, "aggregate P_state closure count changed")
    checks.check(summary.get("ps4_anticircularity_closed_elsewhere") is True, "PS4 anti-circularity link missing")
    checks.check(summary.get("non_dynamic_map_rows") == 96, "non-dynamic map row count changed")
    checks.check(summary.get("kinematic_certificate_rows") == 96, "kinematic row count changed")
    checks.check(summary.get("state_lift_rate_proved") is False, "summary overclaims state lift")
    checks.check(summary.get("pc2_closed") is False, "summary overclaims PC2")
    checks.check(map_def.get("map_name") == "N_h^nd", "map name changed")
    checks.check(map_def.get("state_block") == ["r_i", "eta_i", "v_i", "omega_i"], "state block changed")
    checks.check(map_def.get("auxiliary_block") == ["a_i", "alpha_i"], "auxiliary block changed")
    checks.check(map_def.get("excluded_block") == ["lambda_i"], "excluded block changed")
    checks.check(map_def.get("total_rows") == 96, "map total row count changed")
    checks.check(map_def.get("codomain") == "R^96", "map codomain changed")
    checks.check(isinstance(row_families, list) and len(row_families) == 5, "row family count changed")
    checks.check(sum(int(row.get("rows", 0)) for row in row_families) == 96, "row family row sum changed")
    checks.check(
        all(row.get("included_in_kinematic_certificate") is True for row in row_families),
        "not all row families are tied to the 96-row certificate",
    )
    checks.check(anti.get("map_definition_is_not_inverse_bound") is True, "map/inverse boundary missing")
    checks.check(anti.get("map_definition_is_not_state_lift_rate") is True, "map/lift boundary missing")
    checks.check(anti.get("stage_residual_perturbation_lemma_disallowed_as_input") is True, "stage lemma not barred")
    checks.check(anti.get("dynamic_residual_defect_disallowed_as_input") is True, "dynamic residual not barred")
    checks.check(audit.get("manuscript_link", {}).get("main_tex_present") is True, "main TeX lemma link missing")
    checks.check(audit.get("manuscript_link", {}).get("flat_tex_present") is True, "flat TeX lemma link missing")
    checks.check(source.get("kinematic_certificate_schema") == kinematic.get("schema"), "kinematic schema link missing")
    checks.check(source.get("kinematic_certificate_rows") == proof_scope.get("certified_row_count") == 96, "kinematic row link changed")
    checks.check(source.get("excluded_dynamic_family") == "newton_euler_weak_balance", "dynamic exclusion changed")
    checks.check(source.get("excluded_dynamic_rows") == 36, "dynamic exclusion row count changed")
    checks.check(source.get("primitive_reduction_schema") == primitive_reduction.get("schema"), "primitive reduction schema link missing")
    checks.check(source.get("primitive_reduction_pc2_closed") is False, "primitive reduction unexpectedly closes PC2")
    checks.check(source.get("term_budget_schema") == term_budget.get("schema"), "term budget schema link missing")
    checks.check(source.get("term_budget_pc2_closed") is False, "term budget unexpectedly closes PC2")
    checks.check(
        source.get("p_state_anticircularity_schema") == "d5-p-state-anticircularity-audit-v1",
        "P_state anti-circularity schema link missing",
    )
    checks.check(
        source.get("p_state_anticircularity_closed") is True
        and p_state_anticircularity.get("ps4_anticircularity_closed") is True,
        "P_state PS4 anti-circularity not linked",
    )
    checks.check(source.get("p_state_anticircularity_pc2_closed") is False, "P_state PS4 unexpectedly closes PC2")
    checks.check("P_state primitive closure" in claim.get("forbidden_now", []), "P_state closure not forbidden")
    checks.check("local inverse or inf-sup closure" in claim.get("forbidden_now", []), "inverse closure not forbidden")

    for token in [
        "Status: **P_state map definition closed; lift remains open**.",
        "Closed P_state subproofs: `1/4`.",
        "Open P_state subproofs in this map audit: `2`.",
        "Aggregate P_state subproofs closed after PS4: `2/4`.",
        "PS4 anti-circularity closed elsewhere: `True`.",
        "Non-dynamic map rows: `96/96`.",
        "Term rows using P_state: `126/162`.",
        "P_state primitive closed: `False`.",
        "State lift rate proved: `False`.",
        "Primitive/Taylor PC2 route closed: `False`.",
        "`N_h^nd(S,A)` collects the accepted non-dynamic residual rows",
        "PS1 map definition is closed.",
        "PS2 local inverse or inf-sup proof remains open.",
        "PS4 anti-circularity is closed separately by `D5_P_STATE_ANTICIRCULARITY_AUDIT`.",
        "`P_state` remains open.",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("D5 P_state map definition audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("D5 P_state map definition audit validation: PASS")
    print("closed_subproofs=1/4")
    print("non_dynamic_map_rows=96/96")
    print("p_state_closed=False")
    print("pc2_closed=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
