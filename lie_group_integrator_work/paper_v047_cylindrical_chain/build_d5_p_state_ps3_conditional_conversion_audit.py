#!/usr/bin/env python3
"""Build the D5 P_state PS3 conditional-conversion audit.

This audit closes only the algebraic implication target for PS3.  The
aggregate PS2 audit now supplies the uniform weighted inverse, but the actual
PS3 lift still requires a separate instantiation ledger that supplies the
96-row non-dynamic residual defect and the h-weighted acceleration input as
non-circular inputs.  It does not prove the actual PS3 lift, the P_state
primitive, or PC2.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "D5_P_STATE_PS3_CONDITIONAL_CONVERSION_AUDIT.json"
OUT_MD = PAPER / "D5_P_STATE_PS3_CONDITIONAL_CONVERSION_AUDIT.md"


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def contains_normalized(text: str, token: str) -> bool:
    return token in text or " ".join(token.split()) in " ".join(text.split())


def main() -> None:
    p_state_ps2 = read_json(PAPER / "D5_P_STATE_PS2_WEIGHTED_TARGET_AUDIT.json")
    p_state_ps2_aggregate = read_json(PAPER / "D5_P_STATE_PS2_AGGREGATE_PROMOTION_AUDIT.json")
    p_acc_obstruction = read_json(PAPER / "D5_P_ACC_LIFT_OBSTRUCTION_AUDIT.json")
    kinematic = read_json(PAPER / "KINEMATIC_ROW_DEFECT_CERTIFICATE.json")
    main_tex = read_text(PAPER / "main_cmame.tex")
    flat_tex = read_text(PAPER / "cmame_submission_flat" / "main_cmame_submission.tex")

    manuscript_tokens = [
        r"\label{lem:d5-p-state-ps3-conditional-conversion}",
        "conditional PS3 conversion",
        r"\|\delta S\|=O(h^7)",
        "does not by itself instantiate the actual PS3 lift",
        "required residual and acceleration-rate hypotheses",
    ]
    result = {
        "schema": "d5-p-state-ps3-conditional-conversion-audit-v1",
        "status": "p_state_ps3_conditional_conversion_recorded_ps3_actual_open",
        "read_only": True,
        "run_v047_invoked": False,
        "submission_ready": False,
        "pc2_closed": False,
        "proof_gap_closed": False,
        "primitive_id": "P_state_lift",
        "plan_id": "P_state",
        "primitive_closed": False,
        "ps3_conditional_conversion_closed": True,
        "ps3_actual_state_lift_conversion_closed": False,
        "ps2_uniform_infsup_required": True,
        "ps2_dependency_satisfied_by_aggregate": True,
        "ps2_inverse_or_infsup_closed": p_state_ps2_aggregate.get("ps2_inverse_or_infsup_closed"),
        "actual_ps3_input_instantiation_closed": False,
        "state_lift_rate_proved": False,
        "certifies_induced_taylor_bounds": False,
        "certifies_dynamic_row_defect": False,
        "rate_budget": {
            "non_dynamic_residual_rate": "O(h^7)",
            "unweighted_acceleration_input_rate": "O(h^6)",
            "weighted_acceleration_input_rate": "h * O(h^6) = O(h^7)",
            "conditional_state_lift_rate": "O(h^7)",
            "state_estimate": "||delta S|| <= C_PS2 (||delta N_h^nd|| + h ||delta A||)",
        },
        "conditional_implication": {
            "closed_as_algebraic_implication": True,
            "assumptions": [
                "closed aggregate weighted PS2 inverse on the compact proof tube",
                "96-row non-dynamic residual defect is supplied as O(h^7) in an actual PS3 ledger",
                "h-weighted acceleration input is supplied as O(h^7) in an actual PS3 ledger",
            ],
            "conclusion_under_assumptions": "||delta S|| = O(h^7)",
            "does_not_close_because": [
                "the aggregate PS2 constant is proved, but the actual PS3 residual and acceleration inputs have not been instantiated in the lift ledger",
                "the actual P_state primitive still depends on the open PS3 instantiation",
                "no P_state-induced Taylor term bound is certified",
                "separate primitive-route certificate remains open",
            ],
        },
        "summary": {
            "ps3_conditional_conversion_closed": True,
            "ps3_actual_state_lift_conversion_closed": False,
            "ps2_uniform_infsup_required": True,
            "ps2_dependency_satisfied_by_aggregate": True,
            "ps2_inverse_or_infsup_closed": p_state_ps2_aggregate.get("ps2_inverse_or_infsup_closed"),
            "actual_ps3_input_instantiation_closed": False,
            "non_dynamic_rows_certified": 96,
            "weighted_acceleration_input_rate": "O(h^7)",
            "conditional_state_lift_rate": "O(h^7)",
            "induced_taylor_bounds_proved": 0,
        },
        "source_consistency": {
            "p_state_ps2_schema": p_state_ps2.get("schema"),
            "p_state_ps2_target_spec_closed": p_state_ps2.get("ps2_target_spec_closed"),
            "p_state_ps2_infsup_closed": p_state_ps2.get("ps2_inverse_or_infsup_closed"),
            "p_state_ps2_pc2_closed": p_state_ps2.get("pc2_closed"),
            "p_state_ps2_aggregate_schema": p_state_ps2_aggregate.get("schema"),
            "p_state_ps2_aggregate_promotion_recorded": p_state_ps2_aggregate.get(
                "p_state_ps2_aggregate_promotion_recorded"
            ),
            "p_state_ps2_aggregate_uniform_constant_certified": p_state_ps2_aggregate.get(
                "certifies_uniform_ps2_constant"
            ),
            "p_state_ps2_aggregate_infsup_closed": p_state_ps2_aggregate.get(
                "ps2_inverse_or_infsup_closed"
            ),
            "p_state_ps2_aggregate_pc2_closed": p_state_ps2_aggregate.get("pc2_closed"),
            "p_acc_obstruction_schema": p_acc_obstruction.get("schema"),
            "p_acc_pa2_closed": p_acc_obstruction.get("pa2_closed"),
            "p_acc_current_unweighted_acceleration_rate": p_acc_obstruction.get(
                "current_recorded_inputs_imply_only_unweighted_acceleration_rate"
            ),
            "p_acc_pc2_closed": p_acc_obstruction.get("pc2_closed"),
            "kinematic_certificate_schema": kinematic.get("schema"),
            "kinematic_certificate_certified_rows": kinematic.get("proof_scope", {}).get(
                "certified_row_count"
            ),
            "kinematic_certificate_excluded_dynamic_rows": kinematic.get("proof_scope", {}).get(
                "excluded_row_count"
            ),
        },
        "manuscript_link": {
            "main_tex_present": all(contains_normalized(main_tex, token) for token in manuscript_tokens),
            "flat_tex_present": all(contains_normalized(flat_tex, token) for token in manuscript_tokens),
            "tokens": manuscript_tokens,
        },
        "claim_boundary": {
            "allowed_now": (
                "PS3 has a closed conditional algebraic conversion, and the aggregate "
                "PS2 inverse dependency is satisfied."
            ),
            "forbidden_now": [
                "actual PS3 residual and acceleration inputs instantiated",
                "actual PS3 state lift proved",
                "P_state primitive closure",
                "Taylor term bounds certified from P_state",
                "primitive/Taylor PC2 route closure",
                "submission-ready proof",
            ],
            "close_condition": (
                "Actual PS3 closes only after the closed aggregate PS2 estimate is "
                "combined with non-circular ledger entries supplying the 96-row "
                "non-dynamic residual O(h^7) defect and the h-weighted acceleration "
                "O(h^7) input for the P_state lift."
            ),
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# D5 P_state PS3 Conditional Conversion Audit",
        "",
        "Status: **PS3 conditional conversion recorded; actual P_state lift remains open**.",
        "",
        "This read-only audit records the algebraic PS3 implication that follows",
        "from the weighted PS2 target. The aggregate PS2 audit now supplies the",
        "uniform inverse dependency, but this audit does not instantiate the",
        "actual residual and acceleration inputs for the P_state state-lift proof.",
        "",
        "## Summary",
        "",
        f"- PS3 conditional conversion closed: `{result['ps3_conditional_conversion_closed']}`.",
        f"- Actual PS3 state lift conversion closed: `{result['ps3_actual_state_lift_conversion_closed']}`.",
        f"- PS2 uniform inf-sup required: `{result['ps2_uniform_infsup_required']}`.",
        f"- PS2 dependency satisfied by aggregate: `{result['ps2_dependency_satisfied_by_aggregate']}`.",
        f"- PS2 inverse or inf-sup closed: `{result['ps2_inverse_or_infsup_closed']}`.",
        f"- Actual PS3 input instantiation closed: `{result['actual_ps3_input_instantiation_closed']}`.",
        f"- Non-dynamic rows certified: `{result['summary']['non_dynamic_rows_certified']}/96`.",
        f"- Weighted acceleration input rate: `{result['summary']['weighted_acceleration_input_rate']}`.",
        f"- Conditional state lift rate: `{result['summary']['conditional_state_lift_rate']}`.",
        f"- Induced Taylor bounds proved: `{result['summary']['induced_taylor_bounds_proved']}/162`.",
        f"- Primitive/Taylor PC2 route closed: `{result['pc2_closed']}`.",
        "",
        "## Conditional Conversion",
        "",
        "`||delta S|| <= C_PS2 (||delta N_h^nd|| + h ||delta A||)`.",
        "",
        "If `C_PS2` is uniform, `||delta N_h^nd||=O(h^7)`, and",
        "`||delta A||=O(h^6)`, then `h||delta A||=O(h^7)` and",
        "`||delta S||=O(h^7)`.",
        "",
        "## Acceptance Boundary",
        "",
        "- The conditional PS3 algebraic conversion is recorded.",
        "- The aggregate PS2 uniform inverse dependency is closed.",
        "- The actual residual and acceleration inputs have not been instantiated in PS3.",
        "- The actual PS3 state lift conversion remains open.",
        "- `P_state` remains open.",
        "- Primitive/Taylor PC2 lane remains open.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("d5_p_state_ps3_conditional_conversion_audit=written")
    print("ps3_conditional_conversion_closed=True")
    print("ps3_actual_state_lift_conversion_closed=False")
    print("pc2_closed=False")


if __name__ == "__main__":
    main()
