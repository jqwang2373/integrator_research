#!/usr/bin/env python3
"""Validate the D5 P_acc independence audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "D5_P_ACC_INDEPENDENCE_AUDIT.json"
AUDIT_MD = PAPER / "D5_P_ACC_INDEPENDENCE_AUDIT.md"
PROOF_INPUT_FAMILIES = [
    "translational_velocity_weak_defect",
    "angular_velocity_weak_defect",
    "lower_pair_index3_weak_constraints",
]
ACC_TERM_ROWS = list(range(24, 36)) + list(range(68, 80)) + list(range(112, 124))


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
        p_acc_row_binding = read_json(PAPER / "D5_P_ACC_ROW_BINDING_AUDIT.json")
        dynamic_gate = read_json(PAPER / "DYNAMIC_ROW_ORACLE_GATE.json")
        kinematic_certificate = read_json(PAPER / "KINEMATIC_ROW_DEFECT_CERTIFICATE.json")
    except Exception as exc:  # noqa: BLE001
        print(f"D5 P_acc independence audit validation: FAIL\n- {exc}")
        return 1

    summary = audit.get("summary", {})
    dynamic_boundary = audit.get("dynamic_family_boundary", {})
    dynamic_checks = dynamic_boundary.get("checks", {})
    source = audit.get("source_consistency", {})
    anti = audit.get("anti_circularity_gate", {})
    claim = audit.get("claim_boundary", {})
    input_rows = audit.get("non_dynamic_input_families", [])

    checks.check(audit.get("schema") == "d5-p-acc-independence-audit-v1", "schema changed")
    checks.check(audit.get("status") == "p_acc_independence_closed_lift_open", "status changed")
    checks.check(audit.get("read_only") is True, "audit must be read-only")
    checks.check(audit.get("run_v047_invoked") is False, "run_v047 must not be invoked")
    checks.check(audit.get("submission_ready") is False, "submission readiness overclaimed")
    checks.check(audit.get("pc2_closed") is False, "PC2 unexpectedly closed")
    checks.check(audit.get("proof_gap_closed") is False, "proof gap unexpectedly closed")
    checks.check(audit.get("primitive_id") == "P_acceleration_lift", "primitive id changed")
    checks.check(audit.get("primitive_closed") is False, "P_acc unexpectedly closed")
    checks.check(audit.get("pa3_independence_closed") is True, "PA3 independence not closed")
    checks.check(audit.get("acceleration_lift_rate_proved") is False, "acceleration lift rate overclaimed")
    checks.check(audit.get("term_bounds_proved") == 0, "Taylor bounds unexpectedly proved")
    checks.check(audit.get("term_rows_using_p_acc") == 36, "P_acc row count changed")
    checks.check(audit.get("acceleration_term_rows") == ACC_TERM_ROWS, "acceleration term rows changed")
    checks.check(summary.get("closed_subproof_count_for_this_audit") == 1, "closed subproof count changed")
    checks.check(
        summary.get("p_acc_closed_subproof_count_after_independence") == 3,
        "P_acc aggregate closed subproof count changed",
    )
    checks.check(summary.get("required_subproof_count") == 4, "required subproof count changed")
    checks.check(summary.get("open_subproof_count_after_independence") == 1, "open subproof count changed")
    checks.check(summary.get("non_dynamic_input_families_certified") == 3, "non-dynamic input closure changed")
    checks.check(summary.get("required_non_dynamic_input_families") == 3, "required input family count changed")
    checks.check(summary.get("dynamic_balance_input_families_used") == 0, "dynamic balance used as input")
    checks.check(summary.get("dynamic_balance_rows_disallowed") == 36, "dynamic balance disallowed row count changed")
    checks.check(summary.get("acceleration_lift_rate_proved") is False, "summary overclaims acceleration lift")
    checks.check(summary.get("term_bounds_proved") == 0, "summary overclaims Taylor bounds")
    checks.check(summary.get("pc2_closed") is False, "summary overclaims PC2")
    checks.check(
        audit.get("closed_subproofs")
        == [
            "PA1_acceleration_variable_and_row_map_defined",
            "PA3_lower_pair_acceleration_independence_from_dynamic_balance",
            "PA4_binding_to_residual_ordering_and_D5_terms",
        ],
        "closed subproof list changed",
    )
    checks.check(
        audit.get("open_subproofs") == ["PA2_velocity_collocation_to_acceleration_lift"],
        "open subproof list changed",
    )
    checks.check(anti.get("non_dynamic_rows_can_be_inputs_to_pa2") is True, "PA2 input boundary missing")
    checks.check(anti.get("dynamic_balance_disallowed_as_acceleration_lift_proof") is True, "dynamic balance not barred")
    checks.check(anti.get("stage_residual_perturbation_lemma_disallowed_as_input") is True, "stage lemma not barred")
    checks.check(anti.get("velocity_collocation_rate_not_assumed") is True, "velocity rate assumption boundary missing")
    checks.check(anti.get("row_independence_is_not_acceleration_lift_rate") is True, "independence/rate boundary missing")
    checks.check(anti.get("row_independence_is_not_taylor_bound") is True, "independence/Taylor-bound boundary missing")
    checks.check(audit.get("manuscript_link", {}).get("main_tex_present") is True, "main TeX lemma link missing")
    checks.check(audit.get("manuscript_link", {}).get("flat_tex_present") is True, "flat TeX lemma link missing")

    checks.check(isinstance(input_rows, list) and len(input_rows) == 3, "input family row count changed")
    checks.check([row.get("family") for row in input_rows] == PROOF_INPUT_FAMILIES, "input family order changed")
    expected_offsets = {
        "translational_velocity_weak_defect": (12, 6, 18),
        "angular_velocity_weak_defect": (18, 6, 18),
        "lower_pair_index3_weak_constraints": (36, 8, 24),
    }
    for row in input_rows:
        family = row.get("family")
        expected = expected_offsets.get(family)
        checks.check(expected is not None, f"unexpected input family {family}")
        if expected is None:
            continue
        checks.check((row.get("offset"), row.get("width"), row.get("total_rows")) == expected, f"{family} layout changed")
        checks.check(row.get("input_boundary_closed") is True, f"{family} input boundary not closed")
        checks.check(all(row.get("checks", {}).values()), f"{family} has failed subcheck")

    checks.check(dynamic_boundary.get("family") == "newton_euler_weak_balance", "dynamic family changed")
    checks.check((dynamic_boundary.get("offset"), dynamic_boundary.get("width"), dynamic_boundary.get("total_rows")) == (24, 12, 36), "dynamic layout changed")
    checks.check(dynamic_boundary.get("global_rows") == ACC_TERM_ROWS, "dynamic global rows changed")
    checks.check(dynamic_boundary.get("dynamic_balance_disallowed_as_input") is True, "dynamic disallowance not closed")
    checks.check(all(dynamic_checks.values()), "dynamic boundary has failed subcheck")

    source_trace = audit.get("source_trace", {})
    for token in [
        '("translational_velocity_weak_defect", 12, 6)',
        '("angular_velocity_weak_defect", 18, 6)',
        '("newton_euler_weak_balance", 24, 12)',
        '("lower_pair_index3_weak_constraints", 36, 8)',
        "def residual_cylindrical_chain",
        "pacc.append",
        "w_block.append",
        "dyn.extend([trans, rot])",
        "R_INDEPENDENT_STAGE_FUNCTIONAL_BLOCKS",
    ]:
        checks.check(source_trace.get(token) is True, f"source trace missing: {token}")

    checks.check(
        source.get("p_acc_map_definition_schema") == p_acc_map.get("schema")
        and source.get("p_acc_map_definition_closed") is True
        and p_acc_map.get("pa1_map_definition_closed") is True,
        "P_acc map-definition link missing",
    )
    checks.check(source.get("p_acc_map_definition_primitive_closed") is False, "P_acc map unexpectedly closes primitive")
    checks.check(source.get("p_acc_map_definition_pc2_closed") is False, "P_acc map unexpectedly closes PC2")
    checks.check(
        source.get("p_acc_row_binding_schema") == p_acc_row_binding.get("schema")
        and source.get("p_acc_row_binding_closed") is True
        and p_acc_row_binding.get("pa4_row_binding_closed") is True,
        "P_acc row-binding link missing",
    )
    checks.check(source.get("p_acc_row_binding_primitive_closed") is False, "P_acc row binding unexpectedly closes primitive")
    checks.check(source.get("p_acc_row_binding_pc2_closed") is False, "P_acc row binding unexpectedly closes PC2")
    checks.check(source.get("dynamic_gate_schema") == dynamic_gate.get("schema"), "dynamic gate schema link missing")
    checks.check(source.get("dynamic_gate_stage_residual_defect_proved") is False, "dynamic gate unexpectedly proves stage defect")
    checks.check(
        source.get("kinematic_certificate_schema") == kinematic_certificate.get("schema"),
        "kinematic certificate schema link missing",
    )
    checks.check(source.get("kinematic_certificate_row_count") == 96, "kinematic row count changed")
    checks.check(source.get("kinematic_certificate_excluded_family") == "newton_euler_weak_balance", "excluded family changed")
    checks.check(source.get("kinematic_certificate_stage_residual_defect_proved") is False, "kinematic certificate unexpectedly proves stage defect")
    checks.check("P_acc primitive closure" in claim.get("forbidden_now", []), "P_acc closure not forbidden")
    checks.check("acceleration lift O(h^7) proved" in claim.get("forbidden_now", []), "acceleration lift overclaim not forbidden")
    checks.check("velocity-collocation implication proved" in claim.get("forbidden_now", []), "velocity implication overclaim not forbidden")
    checks.check("primitive/Taylor PC2 route closure" in claim.get("forbidden_now", []), "PC2 overclaim not forbidden")

    for token in [
        "Status: **P_acc independence closed; lift remains open**.",
        "Closed P_acc subproofs after independence: `3/4`.",
        "Open P_acc subproofs after independence: `1`.",
        "Non-dynamic input families certified: `3/3`.",
        "Dynamic-balance input families used: `0`.",
        "Dynamic-balance rows disallowed as inputs: `36`.",
        "P_acc primitive closed: `False`.",
        "Acceleration lift rate proved: `False`.",
        "Taylor bounds proved: `0/36`.",
        "Primitive/Taylor PC2 route closed: `False`.",
        "PA3 lower-pair acceleration independence from dynamic balance is closed.",
        "PA2 velocity-collocation-to-acceleration lift proof remains open.",
        "`P_acc` remains open.",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("D5 P_acc independence audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("D5 P_acc independence audit validation: PASS")
    print("closed_subproofs_after_independence=3/4")
    print("non_dynamic_input_families_certified=3/3")
    print("p_acc_closed=False")
    print("pc2_closed=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
