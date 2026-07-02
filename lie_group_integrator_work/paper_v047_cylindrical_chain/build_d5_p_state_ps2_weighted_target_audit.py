#!/usr/bin/env python3
"""Build the D5 P_state PS2 weighted inf-sup target audit.

This audit closes only the PS2 target specification: the non-dynamic map is
not a literal square inverse in all stage state and acceleration variables.
The correct PS2 target is a state-block inf-sup estimate with acceleration
treated as a parameter in the h-weighted norm. It does not prove the uniform
constant, the state lift rate, or PC2.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "D5_P_STATE_PS2_WEIGHTED_TARGET_AUDIT.json"
OUT_MD = PAPER / "D5_P_STATE_PS2_WEIGHTED_TARGET_AUDIT.md"


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
    p_state_map = read_json(PAPER / "D5_P_STATE_MAP_DEFINITION_AUDIT.json")
    p_state_anti = read_json(PAPER / "D5_P_STATE_ANTICIRCULARITY_AUDIT.json")
    p_acc_obstruction = read_json(PAPER / "D5_P_ACC_LIFT_OBSTRUCTION_AUDIT.json")
    kinematic = read_json(PAPER / "KINEMATIC_ROW_DEFECT_CERTIFICATE.json")
    proof_manifest = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
    main_tex = read_text(PAPER / "main_cmame.tex")
    flat_tex = read_text(PAPER / "cmame_submission_flat" / "main_cmame_submission.tex")

    stages = 3
    bodies = 2
    per_body_state_dim = 12  # r, eta, v, omega
    per_body_acc_dim = 6  # a, alpha
    state_dim = stages * bodies * per_body_state_dim
    acceleration_dim = stages * bodies * per_body_acc_dim
    domain_dim_with_acceleration = state_dim + acceleration_dim
    row_family_dims = {
        "translational_position_weak_defect": 18,
        "rotational_lie_position_weak_defect": 18,
        "translational_velocity_weak_defect": 18,
        "angular_velocity_weak_defect": 18,
        "lower_pair_index3_weak_constraints": 24,
    }
    row_dim = sum(row_family_dims.values())
    manuscript_tokens = [
        r"\label{lem:d5-p-state-ps2-weighted-target}",
        "weighted PS2 target",
        r"h\|\delta A\|",
        "does not close PS2",
        "does not close PS3",
    ]

    result = {
        "schema": "d5-p-state-ps2-weighted-target-audit-v1",
        "status": "p_state_ps2_weighted_infsup_target_recorded_ps2_open",
        "read_only": True,
        "run_v047_invoked": False,
        "submission_ready": False,
        "pc2_closed": False,
        "proof_gap_closed": False,
        "primitive_id": "P_state_lift",
        "plan_id": "P_state",
        "primitive_closed": False,
        "ps2_target_spec_closed": True,
        "ps2_inverse_or_infsup_closed": False,
        "ps3_state_lift_conversion_closed": False,
        "state_lift_rate_proved": False,
        "certifies_induced_taylor_bounds": False,
        "certifies_dynamic_row_defect": False,
        "dimensions": {
            "stages": stages,
            "bodies": bodies,
            "state_block_dimension": state_dim,
            "auxiliary_acceleration_dimension": acceleration_dim,
            "domain_dimension_with_acceleration": domain_dim_with_acceleration,
            "non_dynamic_row_dimension": row_dim,
            "row_deficit_vs_full_state_acceleration_domain": domain_dim_with_acceleration - row_dim,
            "row_surplus_vs_state_block": row_dim - state_dim,
            "row_family_dimensions": row_family_dims,
        },
        "weighted_infsup_target": {
            "literal_full_domain_inverse_possible": False,
            "reason_literal_inverse_not_target": (
                "The map has 96 non-dynamic residual rows but 108 state-plus-acceleration "
                "coordinates, so a square inverse in (S,A) is not the PS2 object."
            ),
            "state_block_infsup_with_acceleration_parameter": True,
            "target_estimate": "||delta S|| <= C_PS2 (||delta N_h^nd|| + h ||delta A||)",
            "weighted_domain_norm": "||delta S|| + h ||delta A||",
            "why_h_weighted": (
                "The collocation equations see acceleration through h A_G delta A; "
                "an unweighted acceleration inverse would be nonuniform as h -> 0."
            ),
            "compatible_with_p_acc_obstruction": (
                "The P_acc audit shows that velocity collocation alone naturally loses "
                "one h-power for unweighted acceleration; PS2 only needs h-weighted "
                "acceleration influence for the state estimate."
            ),
        },
        "non_circularity": {
            "uses_stage_residual_defect": False,
            "uses_d5_dynamic_residual_defect": False,
            "uses_residual_identity_as_variable_lift": False,
            "allowed_inputs": [
                "96-row non-dynamic residual certificate",
                "P_state map definition",
                "P_state PS4 anti-circularity audit",
                "compact proof-tube smoothness constants",
            ],
        },
        "summary": {
            "ps2_target_spec_closed": True,
            "ps2_inverse_or_infsup_closed": False,
            "ps3_state_lift_conversion_closed": False,
            "closed_p_state_subproofs_after_target_spec": 2,
            "state_block_dimension": state_dim,
            "auxiliary_acceleration_dimension": acceleration_dim,
            "non_dynamic_row_dimension": row_dim,
            "induced_taylor_bounds_proved": 0,
        },
        "source_consistency": {
            "p_state_map_schema": p_state_map.get("schema"),
            "p_state_map_definition_closed": p_state_map.get("ps1_map_definition_closed"),
            "p_state_map_primitive_closed": p_state_map.get("primitive_closed"),
            "p_state_anticircularity_schema": p_state_anti.get("schema"),
            "p_state_anticircularity_closed": p_state_anti.get("ps4_anticircularity_closed"),
            "p_state_anticircularity_pc2_closed": p_state_anti.get("pc2_closed"),
            "p_acc_obstruction_schema": p_acc_obstruction.get("schema"),
            "p_acc_current_unweighted_acceleration_rate": p_acc_obstruction.get(
                "current_recorded_inputs_imply_only_unweighted_acceleration_rate"
            ),
            "kinematic_certificate_schema": kinematic.get("schema"),
            "kinematic_certificate_certified_rows": kinematic.get("proof_scope", {}).get(
                "certified_row_count"
            ),
            "proof_manifest_proof_gap_closed": proof_manifest.get("closure_state", {}).get(
                "proof_gap_closed"
            ),
            "proof_manifest_direct_route_gap_closed": proof_manifest.get("closure_state", {}).get(
                "direct_pc2_proof_gap_closed"
            ),
            "proof_manifest_proof_gap_closed_scope": proof_manifest.get("closure_state", {}).get(
                "proof_gap_closed_scope"
            ),
        },
        "manuscript_link": {
            "main_tex_present": all(contains_normalized(main_tex, token) for token in manuscript_tokens),
            "flat_tex_present": all(contains_normalized(flat_tex, token) for token in manuscript_tokens),
            "tokens": manuscript_tokens,
        },
        "claim_boundary": {
            "allowed_now": "PS2 target specification is fixed as a weighted state-block inf-sup estimate.",
            "forbidden_now": [
                "PS2 inverse or inf-sup constant proved",
                "PS3 state lift O(h^7) conversion",
                "P_state primitive closure",
                "Taylor term bounds certified from P_state",
                "primitive/Taylor PC2 route closure",
                "submission-ready proof",
            ],
            "close_condition": (
                "Close PS2 only after proving a uniform lower bound for the "
                "state-block linearization in the h-weighted norm on the compact "
                "proof tube, independently of D5 dynamic residual closure."
            ),
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# D5 P_state PS2 Weighted Target Audit",
        "",
        "Status: **PS2 target specified; P_state lift remains open**.",
        "",
        "This read-only audit fixes the correct PS2 inverse/inf-sup target.",
        "The non-dynamic map is not a literal square inverse in all state and",
        "acceleration variables; the acceleration block must enter as a",
        "parameter in the `h`-weighted norm.",
        "",
        "## Summary",
        "",
        f"- PS2 target specification closed: `{result['ps2_target_spec_closed']}`.",
        f"- PS2 inverse or inf-sup closed: `{result['ps2_inverse_or_infsup_closed']}`.",
        f"- PS3 state lift conversion closed: `{result['ps3_state_lift_conversion_closed']}`.",
        f"- P_state primitive closed: `{result['primitive_closed']}`.",
        f"- State block dimension: `{state_dim}`.",
        f"- Auxiliary acceleration dimension: `{acceleration_dim}`.",
        f"- Non-dynamic row dimension: `{row_dim}`.",
        f"- Induced Taylor bounds proved: `{result['summary']['induced_taylor_bounds_proved']}/162`.",
        f"- Primitive/Taylor PC2 route closed: `{result['pc2_closed']}`.",
        "",
        "## Weighted PS2 Target",
        "",
        "`||delta S|| <= C_PS2 (||delta N_h^nd|| + h ||delta A||)`.",
        "",
        "The full `(S,A)` map has `108` coordinates and `96` residual rows,",
        "so a literal square inverse in all variables is not the PS2 target.",
        "With acceleration treated as a parameter, PS2 must prove a uniform",
        "state-block inf-sup bound on the compact proof tube.",
        "",
        "## Acceptance Boundary",
        "",
        "- The PS2 target specification is closed.",
        "- The uniform PS2 inf-sup constant remains open.",
        "- PS3 conversion to `O(h^7)` state lift rates remains open.",
        "- `P_state` remains open.",
        "- Primitive/Taylor PC2 lane remains open.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("d5_p_state_ps2_weighted_target_audit=written")
    print("ps2_target_spec_closed=True")
    print("ps2_inverse_or_infsup_closed=False")
    print("pc2_closed=False")


if __name__ == "__main__":
    main()
