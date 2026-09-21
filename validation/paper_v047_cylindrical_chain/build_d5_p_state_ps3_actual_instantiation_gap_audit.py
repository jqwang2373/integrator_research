#!/usr/bin/env python3
"""Build the D5 P_state PS3 actual-instantiation gap audit."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "D5_P_STATE_PS3_ACTUAL_INSTANTIATION_GAP_AUDIT.json"
OUT_MD = PAPER / "D5_P_STATE_PS3_ACTUAL_INSTANTIATION_GAP_AUDIT.md"


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def main() -> None:
    aggregate = read_json(PAPER / "D5_P_STATE_PS2_AGGREGATE_PROMOTION_AUDIT.json")
    ps3_conditional = read_json(PAPER / "D5_P_STATE_PS3_CONDITIONAL_CONVERSION_AUDIT.json")
    kinematic = read_json(PAPER / "KINEMATIC_ROW_DEFECT_CERTIFICATE.json")
    p_acc_obstruction = read_json(PAPER / "D5_P_ACC_LIFT_OBSTRUCTION_AUDIT.json")
    p_acc_weighted = read_json(PAPER / "D5_P_ACC_PA2_WEIGHTED_INVERSE_AUDIT.json")
    h_acc_obstruction = read_json(PAPER / "D5_P_STATE_PS3_H_ACC_INPUT_OBSTRUCTION_AUDIT.json")

    result = {
        "schema": "d5-p-state-ps3-actual-instantiation-gap-audit-v1",
        "status": "ps3_actual_instantiation_gap_recorded_actual_ps3_open",
        "read_only": True,
        "run_v047_invoked": False,
        "submission_ready": False,
        "proof_gap_closed": False,
        "pc2_closed": False,
        "primitive_id": "P_state_lift",
        "primitive_closed": False,
        "ps3_actual_state_lift_conversion_closed": False,
        "actual_ps3_input_instantiation_closed": False,
        "certifies_induced_taylor_bounds": False,
        "certifies_dynamic_row_defect": False,
        "input_requirements": [
            {
                "id": "PS3-I1",
                "statement": "Aggregate weighted PS2 inverse on the compact proof tube.",
                "closed": aggregate.get("ps2_inverse_or_infsup_closed") is True,
                "evidence": "D5_P_STATE_PS2_AGGREGATE_PROMOTION_AUDIT",
            },
            {
                "id": "PS3-I2",
                "statement": "Non-dynamic residual defect source for the 96 certified rows.",
                "closed": kinematic.get("proof_scope", {}).get("certified_row_count") == 96,
                "evidence": "KINEMATIC_ROW_DEFECT_CERTIFICATE",
            },
            {
                "id": "PS3-I3",
                "statement": "Independent h-weighted acceleration input for PS3 that does not use the state-lift variable being solved for.",
                "closed": False,
                "evidence": "D5_P_STATE_PS3_H_ACC_INPUT_OBSTRUCTION_AUDIT records the residual-only and circularity obstruction",
            },
            {
                "id": "PS3-I4",
                "statement": "A single non-circular PS3 instantiation ledger combining I1-I3.",
                "closed": False,
                "evidence": "this audit records the missing ledger",
            },
        ],
        "circularity_diagnostic": {
            "velocity_collocation_formula": p_acc_obstruction.get("rate_algebra", {}).get(
                "velocity_collocation_difference"
            ),
            "acceleration_formula": p_acc_obstruction.get("rate_algebra", {}).get(
                "acceleration_difference"
            ),
            "current_unweighted_acceleration_rate": p_acc_obstruction.get(
                "current_recorded_inputs_imply_only_unweighted_acceleration_rate"
            ),
            "why_not_ps3_input": (
                "The O(h^6) acceleration rate obtained from velocity collocation uses "
                "delta_V, a component of the P_state perturbation.  Supplying it as a "
                "PS3 input would make the P_state lift proof circular."
            ),
            "finite_weighted_h_probe_recorded": p_acc_weighted.get("weighted_h_acceleration_control_recorded"),
            "finite_weighted_h_probe_uniform_ps3_input": False,
            "h_acceleration_input_obstruction_recorded": h_acc_obstruction.get(
                "summary", {}
            ).get("h_acceleration_input_obstruction_recorded"),
            "residual_only_input_sufficient_for_h_acceleration": h_acc_obstruction.get(
                "summary", {}
            ).get("residual_only_input_sufficient_for_h_acceleration"),
            "finite_probe_residual_only_nullity_range": [
                h_acc_obstruction.get("summary", {}).get("finite_probe_nullity_min"),
                h_acc_obstruction.get("summary", {}).get("finite_probe_nullity_max"),
            ],
            "finite_probe_is_proof": h_acc_obstruction.get("finite_probe_is_proof"),
        },
        "source_consistency": {
            "aggregate_schema": aggregate.get("schema"),
            "aggregate_ps2_closed": aggregate.get("ps2_inverse_or_infsup_closed"),
            "aggregate_p_state_closed": aggregate.get("primitive_closed"),
            "aggregate_pc2_closed": aggregate.get("pc2_closed"),
            "ps3_conditional_schema": ps3_conditional.get("schema"),
            "ps3_conditional_closed": ps3_conditional.get("ps3_conditional_conversion_closed"),
            "ps3_conditional_ps2_dependency_satisfied": ps3_conditional.get(
                "ps2_dependency_satisfied_by_aggregate"
            ),
            "ps3_conditional_actual_inputs_closed": ps3_conditional.get(
                "actual_ps3_input_instantiation_closed"
            ),
            "ps3_conditional_actual_ps3_closed": ps3_conditional.get(
                "ps3_actual_state_lift_conversion_closed"
            ),
            "kinematic_schema": kinematic.get("schema"),
            "kinematic_certified_rows": kinematic.get("proof_scope", {}).get("certified_row_count"),
            "kinematic_excluded_rows": kinematic.get("proof_scope", {}).get("excluded_row_count"),
            "p_acc_obstruction_schema": p_acc_obstruction.get("schema"),
            "p_acc_pa2_closed": p_acc_obstruction.get("pa2_closed"),
            "p_acc_primitive_closed": p_acc_obstruction.get("primitive_closed"),
            "p_acc_pc2_closed": p_acc_obstruction.get("pc2_closed"),
            "p_acc_weighted_schema": p_acc_weighted.get("schema"),
            "p_acc_weighted_h_control_recorded": p_acc_weighted.get(
                "weighted_h_acceleration_control_recorded"
            ),
            "p_acc_weighted_unweighted_uniform_control_proved": p_acc_weighted.get(
                "unweighted_acceleration_uniform_control_proved"
            ),
            "h_acc_obstruction_schema": h_acc_obstruction.get("schema"),
            "h_acc_obstruction_recorded": h_acc_obstruction.get("summary", {}).get(
                "h_acceleration_input_obstruction_recorded"
            ),
            "h_acc_obstruction_residual_only_input_sufficient": h_acc_obstruction.get(
                "summary", {}
            ).get("residual_only_input_sufficient_for_h_acceleration"),
            "h_acc_obstruction_independent_h_input_closed": h_acc_obstruction.get(
                "summary", {}
            ).get("independent_h_weighted_acceleration_input_closed"),
            "h_acc_obstruction_actual_ps3_closed": h_acc_obstruction.get(
                "summary", {}
            ).get("ps3_actual_state_lift_conversion_closed"),
            "h_acc_obstruction_pc2_closed": h_acc_obstruction.get("pc2_closed"),
            "h_acc_obstruction_finite_probe_is_proof": h_acc_obstruction.get(
                "finite_probe_is_proof"
            ),
        },
        "summary": {
            "input_requirements_closed": 2,
            "input_requirements_total": 4,
            "ps2_dependency_satisfied_by_aggregate": True,
            "non_dynamic_residual_certificate_available": True,
            "h_acceleration_input_obstruction_recorded": h_acc_obstruction.get(
                "summary", {}
            ).get("h_acceleration_input_obstruction_recorded"),
            "residual_only_h_acceleration_input_sufficient": h_acc_obstruction.get(
                "summary", {}
            ).get("residual_only_input_sufficient_for_h_acceleration"),
            "finite_probe_residual_only_nullity_min": h_acc_obstruction.get(
                "summary", {}
            ).get("finite_probe_nullity_min"),
            "finite_probe_residual_only_nullity_max": h_acc_obstruction.get(
                "summary", {}
            ).get("finite_probe_nullity_max"),
            "independent_h_weighted_acceleration_input_closed": False,
            "non_circular_ps3_instantiation_closed": False,
            "ps3_actual_state_lift_conversion_closed": False,
            "primitive_closed": False,
            "pc2_closed": False,
            "induced_taylor_bounds_proved": 0,
        },
        "claim_boundary": {
            "allowed_now": (
                "The actual PS3 blocker is narrowed to a non-circular h-weighted "
                "acceleration-input instantiation and combined PS3 ledger."
            ),
            "forbidden_now": [
                "actual PS3 state lift proved",
                "P_state primitive closure",
                "Taylor term bounds certified from P_state",
                "h-acceleration obstruction promoted to closure",
                "primitive/Taylor PC2 route closure",
                "submission-ready proof",
            ],
            "close_condition": (
                "Actual PS3 closes only after an independent, non-circular h-weighted "
                "acceleration input is supplied and combined with aggregate PS2 and the "
                "96-row non-dynamic residual certificate in a PS3 instantiation ledger."
            ),
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# D5 P_state PS3 Actual-Instantiation Gap Audit",
        "",
        "Status: **actual PS3 instantiation gap recorded; P_state remains open**.",
        "",
        "This read-only audit narrows the post-aggregate-PS2 gap. The aggregate",
        "weighted PS2 inverse is closed, and the 96-row non-dynamic residual",
        "certificate is available. The remaining PS3 blocker is an independent",
        "h-weighted acceleration input that does not reuse the state-lift",
        "variable being solved for.",
        "",
        "## Summary",
        "",
        f"- Input requirements closed: `{result['summary']['input_requirements_closed']}/{result['summary']['input_requirements_total']}`.",
        f"- PS2 dependency satisfied by aggregate: `{result['summary']['ps2_dependency_satisfied_by_aggregate']}`.",
        f"- Non-dynamic residual certificate available: `{result['summary']['non_dynamic_residual_certificate_available']}`.",
        f"- H-acceleration input obstruction recorded/nullity/residual-only sufficient: `{result['summary']['h_acceleration_input_obstruction_recorded']}` / `{result['summary']['finite_probe_residual_only_nullity_min']}`-`{result['summary']['finite_probe_residual_only_nullity_max']}` / `{result['summary']['residual_only_h_acceleration_input_sufficient']}`.",
        f"- Independent h-weighted acceleration input closed: `{result['summary']['independent_h_weighted_acceleration_input_closed']}`.",
        f"- Non-circular PS3 instantiation closed: `{result['summary']['non_circular_ps3_instantiation_closed']}`.",
        f"- Actual PS3 state lift conversion closed: `{result['summary']['ps3_actual_state_lift_conversion_closed']}`.",
        f"- P_state primitive closed: `{result['summary']['primitive_closed']}`.",
        f"- Induced Taylor bounds proved: `{result['summary']['induced_taylor_bounds_proved']}/162`.",
        f"- Primitive/Taylor PC2 route closed: `{result['summary']['pc2_closed']}`.",
        "",
        "## Input Requirements",
        "",
        "| id | status | statement |",
        "|---|---|---|",
    ]
    for item in result["input_requirements"]:
        lines.append(f"| `{item['id']}` | `{item['closed']}` | {item['statement']} |")
    lines += [
        "",
        "## Circularity Diagnostic",
        "",
        "The current acceleration-rate algebra is",
        "",
        "`delta_V - h (A_G \\otimes I) delta_A = rho_V`,",
        "",
        "hence",
        "",
        "`delta_A = h^{-1} (A_G^{-1} \\otimes I) (delta_V - rho_V)`.",
        "",
        "This gives an `O(h^6)` unweighted acceleration rate only after using",
        "`delta_V`, a component of the `P_state` perturbation. It is therefore",
        "not an independent PS3 input for proving `P_state` itself.",
        "",
        "The finite `h delta A` weighted probe is recorded, but it is not a",
        "uniform compact-tube, non-circular PS3 input.",
        "",
        "The h-acceleration obstruction audit records that the residual-only",
        "finite nullity is `12`-`12`; adding the `h delta A` rows is what makes",
        "the diagnostic weighted operator full column rank. This diagnostic is",
        "not a theorem-level PS3 input.",
        "",
        "## Acceptance Boundary",
        "",
        "- This audit does not close actual PS3.",
        "- `P_state` remains open.",
        "- Zero P_state-induced Taylor bounds are certified.",
        "- Primitive/Taylor PC2 lane remains open.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("d5_p_state_ps3_actual_instantiation_gap_audit=written")
    print("input_requirements_closed=2/4")
    print("ps3_actual_state_lift_conversion_closed=False")
    print("p_state_closed=False")
    print("pc2_closed=False")


if __name__ == "__main__":
    main()
