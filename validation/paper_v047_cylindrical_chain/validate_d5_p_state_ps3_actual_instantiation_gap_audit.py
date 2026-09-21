#!/usr/bin/env python3
"""Validate the D5 P_state PS3 actual-instantiation gap audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "D5_P_STATE_PS3_ACTUAL_INSTANTIATION_GAP_AUDIT.json"
AUDIT_MD = PAPER / "D5_P_STATE_PS3_ACTUAL_INSTANTIATION_GAP_AUDIT.md"


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
        aggregate = read_json(PAPER / "D5_P_STATE_PS2_AGGREGATE_PROMOTION_AUDIT.json")
        ps3_conditional = read_json(PAPER / "D5_P_STATE_PS3_CONDITIONAL_CONVERSION_AUDIT.json")
        kinematic = read_json(PAPER / "KINEMATIC_ROW_DEFECT_CERTIFICATE.json")
        p_acc_obstruction = read_json(PAPER / "D5_P_ACC_LIFT_OBSTRUCTION_AUDIT.json")
        p_acc_weighted = read_json(PAPER / "D5_P_ACC_PA2_WEIGHTED_INVERSE_AUDIT.json")
        h_acc_obstruction = read_json(PAPER / "D5_P_STATE_PS3_H_ACC_INPUT_OBSTRUCTION_AUDIT.json")
    except Exception as exc:  # noqa: BLE001
        print(f"D5 P_state PS3 actual-instantiation gap audit validation: FAIL\n- {exc}")
        return 1

    summary = audit.get("summary", {})
    source = audit.get("source_consistency", {})
    circularity = audit.get("circularity_diagnostic", {})
    requirements = audit.get("input_requirements", [])

    checks.check(
        audit.get("schema") == "d5-p-state-ps3-actual-instantiation-gap-audit-v1",
        "schema changed",
    )
    checks.check(
        audit.get("status") == "ps3_actual_instantiation_gap_recorded_actual_ps3_open",
        "status changed",
    )
    checks.check(audit.get("read_only") is True, "audit must be read-only")
    checks.check(audit.get("run_v047_invoked") is False, "run_v047 must not be invoked")
    checks.check(audit.get("submission_ready") is False, "submission readiness overclaimed")
    checks.check(audit.get("proof_gap_closed") is False, "proof gap unexpectedly closed")
    checks.check(audit.get("pc2_closed") is False, "PC2 unexpectedly closed")
    checks.check(audit.get("primitive_id") == "P_state_lift", "primitive id changed")
    checks.check(audit.get("primitive_closed") is False, "P_state unexpectedly closed")
    checks.check(
        audit.get("ps3_actual_state_lift_conversion_closed") is False,
        "actual PS3 unexpectedly closed",
    )
    checks.check(
        audit.get("actual_ps3_input_instantiation_closed") is False,
        "actual PS3 input instantiation unexpectedly closed",
    )
    checks.check(audit.get("certifies_induced_taylor_bounds") is False, "Taylor bounds overclaimed")
    checks.check(audit.get("certifies_dynamic_row_defect") is False, "dynamic defect overclaimed")
    checks.check(len(requirements) == 4, "input requirement count changed")
    checks.check(sum(1 for item in requirements if item.get("closed") is True) == 2, "closed input count changed")
    checks.check(requirements[0].get("closed") is True and requirements[0].get("id") == "PS3-I1", "PS3-I1 not closed")
    checks.check(requirements[1].get("closed") is True and requirements[1].get("id") == "PS3-I2", "PS3-I2 not closed")
    checks.check(requirements[2].get("closed") is False and requirements[2].get("id") == "PS3-I3", "PS3-I3 unexpectedly closed")
    checks.check(
        "D5_P_STATE_PS3_H_ACC_INPUT_OBSTRUCTION_AUDIT" in requirements[2].get("evidence", ""),
        "PS3-I3 obstruction evidence not linked",
    )
    checks.check(requirements[3].get("closed") is False and requirements[3].get("id") == "PS3-I4", "PS3-I4 unexpectedly closed")
    checks.check(summary.get("input_requirements_closed") == 2, "summary closed input count changed")
    checks.check(summary.get("input_requirements_total") == 4, "summary total input count changed")
    checks.check(summary.get("ps2_dependency_satisfied_by_aggregate") is True, "summary PS2 dependency missing")
    checks.check(summary.get("non_dynamic_residual_certificate_available") is True, "summary residual certificate missing")
    checks.check(summary.get("h_acceleration_input_obstruction_recorded") is True, "summary h-acc obstruction missing")
    checks.check(summary.get("residual_only_h_acceleration_input_sufficient") is False, "summary residual-only h input overclaimed")
    checks.check(summary.get("finite_probe_residual_only_nullity_min") == 12, "summary residual-only nullity min changed")
    checks.check(summary.get("finite_probe_residual_only_nullity_max") == 12, "summary residual-only nullity max changed")
    checks.check(summary.get("independent_h_weighted_acceleration_input_closed") is False, "summary h-weighted input overclosed")
    checks.check(summary.get("non_circular_ps3_instantiation_closed") is False, "summary PS3 ledger overclosed")
    checks.check(summary.get("ps3_actual_state_lift_conversion_closed") is False, "summary actual PS3 overclosed")
    checks.check(summary.get("primitive_closed") is False, "summary P_state overclosed")
    checks.check(summary.get("pc2_closed") is False, "summary PC2 overclosed")
    checks.check(summary.get("induced_taylor_bounds_proved") == 0, "summary Taylor bounds overclaimed")
    checks.check(
        source.get("aggregate_schema") == aggregate.get("schema") == "d5-p-state-ps2-aggregate-promotion-audit-v1",
        "aggregate source schema changed",
    )
    checks.check(source.get("aggregate_ps2_closed") is True and aggregate.get("ps2_inverse_or_infsup_closed") is True, "aggregate PS2 not linked closed")
    checks.check(source.get("aggregate_p_state_closed") is False and aggregate.get("primitive_closed") is False, "aggregate unexpectedly closes P_state")
    checks.check(source.get("aggregate_pc2_closed") is False and aggregate.get("pc2_closed") is False, "aggregate unexpectedly closes PC2")
    checks.check(source.get("ps3_conditional_schema") == ps3_conditional.get("schema"), "conditional source schema missing")
    checks.check(source.get("ps3_conditional_closed") is True and ps3_conditional.get("ps3_conditional_conversion_closed") is True, "conditional PS3 not linked closed")
    checks.check(source.get("ps3_conditional_ps2_dependency_satisfied") is True, "conditional PS2 dependency not linked")
    checks.check(source.get("ps3_conditional_actual_inputs_closed") is False, "conditional actual inputs overclosed")
    checks.check(source.get("ps3_conditional_actual_ps3_closed") is False, "conditional actual PS3 overclosed")
    checks.check(source.get("kinematic_schema") == kinematic.get("schema"), "kinematic source schema missing")
    checks.check(source.get("kinematic_certified_rows") == 96, "kinematic certified row count changed")
    checks.check(source.get("kinematic_excluded_rows") == 36, "kinematic excluded row count changed")
    checks.check(source.get("p_acc_obstruction_schema") == p_acc_obstruction.get("schema"), "P_acc obstruction schema missing")
    checks.check(source.get("p_acc_pa2_closed") is False and p_acc_obstruction.get("pa2_closed") is False, "PA2 unexpectedly closed")
    checks.check(source.get("p_acc_primitive_closed") is False and p_acc_obstruction.get("primitive_closed") is False, "P_acc unexpectedly closed")
    checks.check(source.get("p_acc_pc2_closed") is False and p_acc_obstruction.get("pc2_closed") is False, "P_acc unexpectedly closes PC2")
    checks.check(source.get("p_acc_weighted_schema") == p_acc_weighted.get("schema"), "P_acc weighted source schema missing")
    checks.check(source.get("p_acc_weighted_h_control_recorded") is True, "weighted h control not recorded")
    checks.check(source.get("p_acc_weighted_unweighted_uniform_control_proved") is False, "unweighted acceleration control overclaimed")
    checks.check(
        source.get("h_acc_obstruction_schema")
        == h_acc_obstruction.get("schema")
        == "d5-p-state-ps3-h-acc-input-obstruction-audit-v1",
        "h-acc obstruction source schema missing",
    )
    checks.check(source.get("h_acc_obstruction_recorded") is True, "h-acc obstruction not linked recorded")
    checks.check(
        source.get("h_acc_obstruction_residual_only_input_sufficient") is False,
        "h-acc obstruction residual-only input unexpectedly sufficient",
    )
    checks.check(
        source.get("h_acc_obstruction_independent_h_input_closed") is False,
        "h-acc obstruction input unexpectedly closed",
    )
    checks.check(
        source.get("h_acc_obstruction_actual_ps3_closed") is False,
        "h-acc obstruction actual PS3 unexpectedly closed",
    )
    checks.check(source.get("h_acc_obstruction_pc2_closed") is False, "h-acc obstruction unexpectedly closes PC2")
    checks.check(
        source.get("h_acc_obstruction_finite_probe_is_proof") is False,
        "h-acc obstruction finite probe overclaimed as proof",
    )
    checks.check("delta_V" in circularity.get("why_not_ps3_input", ""), "circularity reason missing delta_V")
    checks.check(circularity.get("finite_weighted_h_probe_recorded") is True, "finite weighted h probe not linked")
    checks.check(circularity.get("finite_weighted_h_probe_uniform_ps3_input") is False, "finite probe overclaimed as uniform PS3 input")
    checks.check(circularity.get("h_acceleration_input_obstruction_recorded") is True, "circularity h-acc obstruction missing")
    checks.check(
        circularity.get("residual_only_input_sufficient_for_h_acceleration") is False,
        "circularity residual-only h input overclaimed",
    )
    checks.check(circularity.get("finite_probe_residual_only_nullity_range") == [12, 12], "circularity nullity range changed")
    checks.check(circularity.get("finite_probe_is_proof") is False, "circularity finite probe overclaimed")

    for token in [
        "Status: **actual PS3 instantiation gap recorded; P_state remains open**.",
        "Input requirements closed: `2/4`.",
        "PS2 dependency satisfied by aggregate: `True`.",
        "Non-dynamic residual certificate available: `True`.",
        "H-acceleration input obstruction recorded/nullity/residual-only sufficient: `True` / `12`-`12` / `False`.",
        "Independent h-weighted acceleration input closed: `False`.",
        "Non-circular PS3 instantiation closed: `False`.",
        "Actual PS3 state lift conversion closed: `False`.",
        "P_state primitive closed: `False`.",
        "Induced Taylor bounds proved: `0/162`.",
        "Primitive/Taylor PC2 route closed: `False`.",
        "`delta_A = h^{-1} (A_G^{-1} \\otimes I) (delta_V - rho_V)`.",
        "not an independent PS3 input for proving `P_state` itself.",
        "The h-acceleration obstruction audit records that the residual-only",
        "not a theorem-level PS3 input.",
        "This audit does not close actual PS3.",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("D5 P_state PS3 actual-instantiation gap audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("D5 P_state PS3 actual-instantiation gap audit validation: PASS")
    print("input_requirements_closed=2/4")
    print("ps3_actual_state_lift_conversion_closed=False")
    print("p_state_closed=False")
    print("pc2_closed=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
