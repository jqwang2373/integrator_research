#!/usr/bin/env python3
"""Validate the D5 P_state PS3 conditional-conversion audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "D5_P_STATE_PS3_CONDITIONAL_CONVERSION_AUDIT.json"
AUDIT_MD = PAPER / "D5_P_STATE_PS3_CONDITIONAL_CONVERSION_AUDIT.md"


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
        p_state_ps2 = read_json(PAPER / "D5_P_STATE_PS2_WEIGHTED_TARGET_AUDIT.json")
        p_state_ps2_aggregate = read_json(PAPER / "D5_P_STATE_PS2_AGGREGATE_PROMOTION_AUDIT.json")
        p_acc_obstruction = read_json(PAPER / "D5_P_ACC_LIFT_OBSTRUCTION_AUDIT.json")
        kinematic = read_json(PAPER / "KINEMATIC_ROW_DEFECT_CERTIFICATE.json")
    except Exception as exc:  # noqa: BLE001
        print(f"D5 P_state PS3 conditional conversion audit validation: FAIL\n- {exc}")
        return 1

    summary = audit.get("summary", {})
    rate = audit.get("rate_budget", {})
    implication = audit.get("conditional_implication", {})
    source = audit.get("source_consistency", {})

    checks.check(
        audit.get("schema") == "d5-p-state-ps3-conditional-conversion-audit-v1",
        "schema changed",
    )
    checks.check(
        audit.get("status") == "p_state_ps3_conditional_conversion_recorded_ps3_actual_open",
        "status changed",
    )
    checks.check(audit.get("read_only") is True, "audit must be read-only")
    checks.check(audit.get("run_v047_invoked") is False, "run_v047 must not be invoked")
    checks.check(audit.get("submission_ready") is False, "submission readiness overclaimed")
    checks.check(audit.get("pc2_closed") is False, "PC2 unexpectedly closed")
    checks.check(audit.get("proof_gap_closed") is False, "proof gap unexpectedly closed")
    checks.check(audit.get("primitive_id") == "P_state_lift", "primitive id changed")
    checks.check(audit.get("plan_id") == "P_state", "plan id changed")
    checks.check(audit.get("primitive_closed") is False, "P_state unexpectedly closed")
    checks.check(audit.get("ps3_conditional_conversion_closed") is True, "conditional PS3 not recorded")
    checks.check(
        audit.get("ps3_actual_state_lift_conversion_closed") is False,
        "actual PS3 unexpectedly closed",
    )
    checks.check(audit.get("ps2_uniform_infsup_required") is True, "PS2 requirement missing")
    checks.check(
        audit.get("ps2_dependency_satisfied_by_aggregate") is True,
        "aggregate PS2 dependency not recorded as satisfied",
    )
    checks.check(audit.get("ps2_inverse_or_infsup_closed") is True, "PS2 aggregate inf-sup not closed")
    checks.check(
        audit.get("actual_ps3_input_instantiation_closed") is False,
        "actual PS3 input instantiation unexpectedly closed",
    )
    checks.check(audit.get("state_lift_rate_proved") is False, "state lift unexpectedly proved")
    checks.check(audit.get("certifies_induced_taylor_bounds") is False, "Taylor bounds overclaimed")
    checks.check(audit.get("certifies_dynamic_row_defect") is False, "dynamic defect overclaimed")
    checks.check(rate.get("non_dynamic_residual_rate") == "O(h^7)", "non-dynamic rate changed")
    checks.check(rate.get("unweighted_acceleration_input_rate") == "O(h^6)", "acceleration rate changed")
    checks.check(rate.get("weighted_acceleration_input_rate") == "h * O(h^6) = O(h^7)", "weighted acceleration rate changed")
    checks.check(rate.get("conditional_state_lift_rate") == "O(h^7)", "conditional state rate changed")
    checks.check(
        rate.get("state_estimate") == "||delta S|| <= C_PS2 (||delta N_h^nd|| + h ||delta A||)",
        "state estimate changed",
    )
    checks.check(implication.get("closed_as_algebraic_implication") is True, "conditional implication not closed")
    checks.check(implication.get("conclusion_under_assumptions") == "||delta S|| = O(h^7)", "conditional conclusion changed")
    checks.check(len(implication.get("assumptions", [])) == 3, "assumption list changed")
    checks.check(
        "actual PS3 residual and acceleration inputs" in implication.get("does_not_close_because", [""])[0],
        "non-closure reason missing PS3 input instantiation",
    )
    checks.check(summary.get("ps3_conditional_conversion_closed") is True, "summary conditional PS3 missing")
    checks.check(summary.get("ps3_actual_state_lift_conversion_closed") is False, "summary actual PS3 overclosed")
    checks.check(summary.get("ps2_uniform_infsup_required") is True, "summary PS2 requirement missing")
    checks.check(
        summary.get("ps2_dependency_satisfied_by_aggregate") is True,
        "summary aggregate PS2 dependency missing",
    )
    checks.check(summary.get("ps2_inverse_or_infsup_closed") is True, "summary PS2 aggregate inf-sup not closed")
    checks.check(
        summary.get("actual_ps3_input_instantiation_closed") is False,
        "summary actual PS3 input instantiation overclosed",
    )
    checks.check(summary.get("non_dynamic_rows_certified") == 96, "summary non-dynamic rows changed")
    checks.check(summary.get("weighted_acceleration_input_rate") == "O(h^7)", "summary weighted rate changed")
    checks.check(summary.get("conditional_state_lift_rate") == "O(h^7)", "summary conditional rate changed")
    checks.check(summary.get("induced_taylor_bounds_proved") == 0, "summary Taylor bounds overclaimed")
    checks.check(source.get("p_state_ps2_schema") == "d5-p-state-ps2-weighted-target-audit-v1", "PS2 source schema missing")
    checks.check(
        source.get("p_state_ps2_target_spec_closed") is True
        and p_state_ps2.get("ps2_target_spec_closed") is True,
        "PS2 target spec not linked",
    )
    checks.check(
        source.get("p_state_ps2_infsup_closed") is False
        and p_state_ps2.get("ps2_inverse_or_infsup_closed") is False,
        "PS2 target unexpectedly linked as closed",
    )
    checks.check(source.get("p_state_ps2_pc2_closed") is False, "PS2 source unexpectedly closes PC2")
    checks.check(
        source.get("p_state_ps2_aggregate_schema") == "d5-p-state-ps2-aggregate-promotion-audit-v1",
        "aggregate PS2 source schema missing",
    )
    checks.check(
        source.get("p_state_ps2_aggregate_promotion_recorded") is True
        and p_state_ps2_aggregate.get("p_state_ps2_aggregate_promotion_recorded") is True,
        "aggregate PS2 promotion not linked",
    )
    checks.check(
        source.get("p_state_ps2_aggregate_uniform_constant_certified") is True
        and p_state_ps2_aggregate.get("certifies_uniform_ps2_constant") is True,
        "aggregate PS2 uniform constant not linked",
    )
    checks.check(
        source.get("p_state_ps2_aggregate_infsup_closed") is True
        and p_state_ps2_aggregate.get("ps2_inverse_or_infsup_closed") is True,
        "aggregate PS2 inf-sup not linked as closed",
    )
    checks.check(source.get("p_state_ps2_aggregate_pc2_closed") is False, "aggregate PS2 unexpectedly closes PC2")
    checks.check(source.get("p_acc_obstruction_schema") == "d5-p-acc-lift-obstruction-audit-v1", "P_acc obstruction source missing")
    checks.check(
        source.get("p_acc_pa2_closed") is False
        and p_acc_obstruction.get("pa2_closed") is False,
        "P_acc PA2 unexpectedly closed",
    )
    checks.check(
        source.get("p_acc_current_unweighted_acceleration_rate") == "O(h^6)"
        and p_acc_obstruction.get("current_recorded_inputs_imply_only_unweighted_acceleration_rate") == "O(h^6)",
        "P_acc acceleration rate link changed",
    )
    checks.check(source.get("p_acc_pc2_closed") is False, "P_acc source unexpectedly closes PC2")
    checks.check(source.get("kinematic_certificate_schema") == "kinematic-row-defect-certificate-v1", "kinematic source missing")
    checks.check(
        source.get("kinematic_certificate_certified_rows") == 96
        and kinematic.get("proof_scope", {}).get("certified_row_count") == 96,
        "kinematic certified row count changed",
    )
    checks.check(source.get("kinematic_certificate_excluded_dynamic_rows") == 36, "excluded dynamic row count changed")
    checks.check(audit.get("manuscript_link", {}).get("main_tex_present") is True, "main TeX PS3 lemma missing")
    checks.check(audit.get("manuscript_link", {}).get("flat_tex_present") is True, "flat TeX PS3 lemma missing")

    for token in [
        "Status: **PS3 conditional conversion recorded; actual P_state lift remains open**.",
        "PS3 conditional conversion closed: `True`.",
        "Actual PS3 state lift conversion closed: `False`.",
        "PS2 uniform inf-sup required: `True`.",
        "PS2 dependency satisfied by aggregate: `True`.",
        "PS2 inverse or inf-sup closed: `True`.",
        "Actual PS3 input instantiation closed: `False`.",
        "Non-dynamic rows certified: `96/96`.",
        "Weighted acceleration input rate: `O(h^7)`.",
        "Conditional state lift rate: `O(h^7)`.",
        "Induced Taylor bounds proved: `0/162`.",
        "Primitive/Taylor PC2 route closed: `False`.",
        "`||delta S|| <= C_PS2 (||delta N_h^nd|| + h ||delta A||)`.",
        "`||delta S||=O(h^7)`.",
        "The conditional PS3 algebraic conversion is recorded.",
        "The aggregate PS2 uniform inverse dependency is closed.",
        "The actual residual and acceleration inputs have not been instantiated in PS3.",
        "The actual PS3 state lift conversion remains open.",
        "`P_state` remains open.",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("D5 P_state PS3 conditional conversion audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("D5 P_state PS3 conditional conversion audit validation: PASS")
    print("ps3_conditional_conversion_closed=True")
    print("ps3_actual_state_lift_conversion_closed=False")
    print("pc2_closed=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
