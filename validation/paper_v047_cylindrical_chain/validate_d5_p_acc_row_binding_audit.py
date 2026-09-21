#!/usr/bin/env python3
"""Validate the D5 P_acc row-binding audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "D5_P_ACC_ROW_BINDING_AUDIT.json"
AUDIT_MD = PAPER / "D5_P_ACC_ROW_BINDING_AUDIT.md"
EXPECTED_ROWS = list(range(24, 36)) + list(range(68, 80)) + list(range(112, 124))


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
        p_acc_map = read_json(PAPER / "D5_P_ACC_MAP_DEFINITION_AUDIT.json")
        term_budget = read_json(PAPER / "D5_TAYLOR_TERM_BUDGET_AUDIT.json")
        d6_audit = read_json(PAPER / "NEWTON_EULER_ROW_ORDERING_SCALING_AD_AUDIT.json")
        readiness = read_json(PAPER / "D5_DYNAMIC_DEFECT_READINESS_AUDIT.json")
    except Exception as exc:  # noqa: BLE001
        print(f"D5 P_acc row-binding audit validation: FAIL\n- {exc}")
        return 1

    summary = audit.get("summary", {})
    source = audit.get("source_consistency", {})
    anti = audit.get("anti_circularity_gate", {})
    claim = audit.get("claim_boundary", {})
    corollary = audit.get("conditional_row_level_corollary", {})
    rows = audit.get("row_checks", [])

    checks.check(audit.get("schema") == "d5-p-acc-row-binding-audit-v1", "schema changed")
    checks.check(audit.get("status") == "p_acc_row_binding_closed_lift_open", "status changed")
    checks.check(audit.get("read_only") is True, "audit must be read-only")
    checks.check(audit.get("run_v047_invoked") is False, "run_v047 must not be invoked")
    checks.check(audit.get("submission_ready") is False, "submission readiness overclaimed")
    checks.check(audit.get("pc2_closed") is False, "PC2 unexpectedly closed")
    checks.check(audit.get("proof_gap_closed") is False, "proof gap unexpectedly closed")
    checks.check(audit.get("primitive_id") == "P_acceleration_lift", "primitive id changed")
    checks.check(audit.get("primitive_closed") is False, "P_acc unexpectedly closed")
    checks.check(audit.get("pa4_row_binding_closed") is True, "PA4 row binding not closed")
    checks.check(audit.get("acceleration_lift_rate_proved") is False, "acceleration lift rate overclaimed")
    checks.check(audit.get("term_bounds_proved") == 0, "Taylor bounds unexpectedly proved")
    checks.check(audit.get("term_rows_using_p_acc") == 36, "P_acc term-row count changed")
    checks.check(audit.get("term_rows_bound_to_ordering") == 36, "bound row count changed")
    checks.check(audit.get("translational_acceleration_rows") == 18, "translational row count changed")
    checks.check(audit.get("angular_acceleration_rows") == 18, "angular row count changed")
    checks.check(audit.get("row_ids") == EXPECTED_ROWS, "row ids changed")
    checks.check(audit.get("row_ids_expected") == EXPECTED_ROWS, "expected row ids changed")
    checks.check(summary.get("closed_subproof_count_for_this_audit") == 1, "closed subproof count changed")
    checks.check(summary.get("p_acc_closed_subproof_count_after_binding") == 2, "P_acc aggregate closed subproof count changed")
    checks.check(summary.get("required_subproof_count") == 4, "required subproof count changed")
    checks.check(summary.get("open_subproof_count_after_binding") == 2, "open subproof count changed")
    checks.check(summary.get("term_rows_using_p_acc") == 36, "summary P_acc rows changed")
    checks.check(summary.get("term_rows_bound_to_ordering") == 36, "summary bound rows changed")
    checks.check(summary.get("rows_with_closed_binding") == 36, "closed binding row count changed")
    checks.check(summary.get("translational_acceleration_rows") == 18, "summary translational rows changed")
    checks.check(summary.get("angular_acceleration_rows") == 18, "summary angular rows changed")
    checks.check(summary.get("acceleration_lift_rate_proved") is False, "summary overclaims acceleration lift")
    checks.check(summary.get("term_bounds_proved") == 0, "summary overclaims Taylor bounds")
    checks.check(summary.get("pc2_closed") is False, "summary overclaims PC2")
    checks.check(audit.get("closed_subproofs") == [
        "PA1_acceleration_variable_and_row_map_defined",
        "PA4_binding_to_residual_ordering_and_D5_terms",
    ], "closed subproof list changed")
    checks.check(audit.get("open_subproofs") == [
        "PA2_velocity_collocation_to_acceleration_lift",
        "PA3_lower_pair_acceleration_independence_from_dynamic_balance",
    ], "open subproof list changed")
    checks.check(anti.get("row_binding_is_not_acceleration_lift_rate") is True, "row/rate boundary missing")
    checks.check(anti.get("row_binding_is_not_taylor_bound") is True, "row/Taylor-bound boundary missing")
    checks.check(anti.get("velocity_collocation_rate_not_assumed") is True, "velocity collocation boundary missing")
    checks.check(anti.get("dynamic_balance_disallowed_as_acceleration_lift_proof") is True, "dynamic balance not barred")
    checks.check(anti.get("stage_residual_perturbation_lemma_disallowed_as_input") is True, "stage lemma not barred")
    checks.check(audit.get("manuscript_link", {}).get("main_tex_present") is True, "main TeX lemma link missing")
    checks.check(audit.get("manuscript_link", {}).get("flat_tex_present") is True, "flat TeX lemma link missing")
    checks.check(
        r"\label{cor:d5-p-acc-row-bound-under-pacc}" in audit.get("manuscript_link", {}).get("tokens", []),
        "P_acc row-level corollary token missing",
    )
    checks.check(corollary.get("label") == "cor:d5-p-acc-row-bound-under-pacc", "P_acc corollary label missing")
    checks.check(corollary.get("main_tex_present") is True, "P_acc corollary missing in main TeX")
    checks.check(corollary.get("flat_tex_present") is True, "P_acc corollary missing in flat TeX")
    checks.check(
        corollary.get("term_rows_conditionally_bound_under_p_acc") == 36,
        "P_acc corollary row count changed",
    )
    checks.check(corollary.get("actual_taylor_bounds_proved") == 0, "P_acc corollary overclaims Taylor bounds")
    checks.check(corollary.get("primitive_closed") is False, "P_acc corollary overclaims primitive closure")
    checks.check(corollary.get("pc2_closed") is False, "P_acc corollary overclaims PC2 closure")
    checks.check(
        corollary.get("uses_weighted_pa2_diagnostic_as_proof") is False,
        "P_acc corollary must not use weighted PA2 diagnostic as proof",
    )
    checks.check(source.get("p_acc_map_definition_schema") == p_acc_map.get("schema"), "P_acc map-definition schema link missing")
    checks.check(source.get("p_acc_map_definition_closed") is True and p_acc_map.get("pa1_map_definition_closed") is True, "P_acc PA1 link missing")
    checks.check(source.get("p_acc_map_definition_primitive_closed") is False, "P_acc map unexpectedly closes primitive")
    checks.check(source.get("p_acc_map_definition_pc2_closed") is False, "P_acc map unexpectedly closes PC2")
    checks.check(source.get("term_budget_schema") == term_budget.get("schema"), "term-budget schema link missing")
    checks.check(source.get("term_budget_pc2_closed") is False, "term budget unexpectedly closes PC2")
    checks.check(source.get("d6_audit_schema") == d6_audit.get("schema"), "D6 audit schema link missing")
    checks.check(source.get("d6_row_ordering_scaling_ad_closed") is True, "D6 row binding not carried")
    checks.check(source.get("d6_stage_residual_defect_proved") is False, "D6 unexpectedly proves D5 defect")
    checks.check(source.get("readiness_schema") == readiness.get("schema"), "readiness schema link missing")
    checks.check(source.get("readiness_pc2_closed") == readiness.get("pc2_closed"), "readiness PC2 link mismatch")
    checks.check(
        source.get("readiness_direct_route_status_not_used_for_pa4") is True,
        "readiness direct-route status must not be used to close PA4",
    )
    checks.check("P_acc primitive closure" in claim.get("forbidden_now", []), "P_acc closure not forbidden")
    checks.check("acceleration lift O(h^7) proved" in claim.get("forbidden_now", []), "acceleration lift overclaim not forbidden")
    checks.check("Taylor term bounds certified from P_acc" in claim.get("forbidden_now", []), "Taylor-bound overclaim not forbidden")
    checks.check(
        "PA2 proves the translational and angular acceleration lift rates"
        in claim.get("close_condition", ""),
        "P_acc close condition must retain PA2 rate proof",
    )
    checks.check(
        "PA3 is closed separately as the non-dynamic input-independence subproof"
        in claim.get("close_condition", ""),
        "P_acc close condition must separate PA3 independence from PA2 rate proof",
    )
    checks.check(
        "PA2 and PA3 prove" not in claim.get("close_condition", ""),
        "P_acc close condition has stale PA3 rate-proof wording",
    )

    checks.check(isinstance(rows, list) and len(rows) == 36, "row checks count changed")
    for row in rows:
        if not isinstance(row, dict):
            checks.check(False, "row check is not an object")
            continue
        checks.check(row.get("row_binding_closed") is True, f"row {row.get('global_row')} binding not closed")
        checks.check(row.get("taylor_bound_proved") is False, f"row {row.get('global_row')} unexpectedly proves Taylor bound")
        checks.check(all(row.get("checks", {}).values()), f"row {row.get('global_row')} has failed subcheck")
        if row.get("term_id") == "T_acceleration_lift":
            checks.check(row.get("balance_block") == "translational_newton_balance", "translational row block mismatch")
            checks.check("translational" in row.get("runtime_source_component", ""), "translational runtime component mismatch")
        if row.get("term_id") == "R_angular_acceleration_lift":
            checks.check(row.get("balance_block") == "rotational_euler_balance", "angular row block mismatch")
            checks.check("rotational" in row.get("runtime_source_component", ""), "rotational runtime component mismatch")

    for token in [
        "Status: **P_acc row binding closed; lift remains open**.",
        "Closed P_acc subproofs after binding: `2/4`.",
        "Open P_acc subproofs after binding: `2`.",
        "Acceleration rows bound to ordering: `36/36`.",
        "Rows with closed binding: `36/36`.",
        "Translational/angular acceleration rows: `18/18`.",
        "P_acc primitive closed: `False`.",
        "Acceleration lift rate proved: `False`.",
        "Taylor bounds proved: `0/36`.",
        "Conditional row-level P_acc corollary present main/flat: `True/True`.",
        "Primitive/Taylor PC2 route closed: `False`.",
        "PA4 row-ordering/Taylor-term binding is closed.",
        "PA2 velocity-collocation-to-acceleration lift proof remains open.",
        "PA3 independence is not closed by this row-binding audit; the later independence audit closes PA3 separately.",
        "`P_acc` remains open.",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("D5 P_acc row-binding audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("D5 P_acc row-binding audit validation: PASS")
    print("closed_subproofs_after_binding=2/4")
    print("acceleration_rows_bound=36/36")
    print("p_acc_closed=False")
    print("pc2_closed=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
