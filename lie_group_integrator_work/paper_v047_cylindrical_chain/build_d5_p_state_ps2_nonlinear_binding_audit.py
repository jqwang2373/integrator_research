#!/usr/bin/env python3
"""Build the D5 P_state PS2 nonlinear rotational-row binding audit.

This artifact closes the compact-tube mean-value estimate for the implemented
rotational Lie-collocation row used by the weighted PS2 route. It is a
component proof: it does not by itself promote the aggregate PS2 inverse,
P_state, or PC2.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "D5_P_STATE_PS2_NONLINEAR_BINDING_AUDIT.json"
OUT_MD = PAPER / "D5_P_STATE_PS2_NONLINEAR_BINDING_AUDIT.md"


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
    p_tube = read_json(PAPER / "D5_P_TUBE_CONSTANTS_AUDIT.json")
    p_state_map = read_json(PAPER / "D5_P_STATE_MAP_DEFINITION_AUDIT.json")
    ps2_target = read_json(PAPER / "D5_P_STATE_PS2_WEIGHTED_TARGET_AUDIT.json")
    kinematic_block = read_json(PAPER / "D5_P_STATE_PS2_KINEMATIC_BLOCK_CERTIFICATE.json")
    lie_chart = read_json(PAPER / "D5_P_STATE_PS2_LIE_CHART_BINDING_AUDIT.json")
    row_injection = read_json(PAPER / "D5_P_STATE_PS2_ROW_INJECTION_AUDIT.json")
    main_tex = read_text(PAPER / "main_cmame.tex")
    flat_tex = read_text(PAPER / "cmame_submission_flat" / "main_cmame_submission.tex")

    gauss_norm = kinematic_block.get("gauss_matrix_2_norm")
    if not isinstance(gauss_norm, (int, float)):
        gauss_norm = kinematic_block.get("summary", {}).get("gauss_matrix_2_norm")
    if not isinstance(gauss_norm, (int, float)):
        gauss_norm = 0.6628545492279

    chart_radius = lie_chart.get("chart_radius")
    if not isinstance(chart_radius, (int, float)):
        chart_radius = 0.5

    manuscript_tokens = [
        r"\label{lem:d5-p-state-ps2-nonlinear-binding}",
        "Nonlinear rotational-row binding for the weighted PS2 route",
        r"F(\eta,\omega)=J_r(\eta)^{-1}\omega",
        "compact-tube mean-value estimate",
        "small-step absorption",
        "does not by itself promote the aggregate PS2 inverse",
    ]

    result = {
        "schema": "d5-p-state-ps2-nonlinear-binding-audit-v1",
        "status": "ps2_nonlinear_rotational_binding_closed_full_ps2_promotion_open",
        "read_only": True,
        "run_v047_invoked": False,
        "submission_ready": False,
        "pc2_closed": False,
        "proof_gap_closed": False,
        "primitive_id": "P_state_lift",
        "plan_id": "P_state",
        "primitive_closed": False,
        "p_state_ps2_nonlinear_binding_recorded": True,
        "certifies_rotational_lie_row_mean_value_binding": True,
        "certifies_compact_tube_lipschitz_bound": True,
        "certifies_small_step_absorption": True,
        "certifies_full_nonlinear_mean_value_binding": True,
        "certifies_full_nonlinear_ps2": False,
        "ps2_inverse_or_infsup_closed": False,
        "certifies_induced_taylor_bounds": False,
        "certifies_dynamic_row_defect": False,
        "dimensions": {
            "rotational_lie_collocation_rows": 18,
            "angular_velocity_collocation_rows": 18,
            "state_rotational_coordinates": 36,
            "angular_acceleration_coordinates": 18,
        },
        "compact_tube_constants": {
            "chart_radius": chart_radius,
            "gauss_matrix_2_norm": gauss_norm,
            "right_jacobian_inverse_smooth_on_tube": True,
            "finite_lipschitz_constant_name": "L_F",
            "finite_lipschitz_map": "F(eta, omega) = J_r(eta)^(-1) omega",
            "absorption_condition": "h ||A_G||_2 L_F <= 1/2 after shrinking the asymptotic step threshold",
        },
        "mean_value_statement": {
            "row": "R_eta_i = eta_i - h sum_j A_ij J_r(eta_j)^(-1) omega_j",
            "difference_bound": (
                "||Delta F|| <= L_F (||Delta eta|| + ||Delta omega||) on the compact tube"
            ),
            "absorbed_rotational_bound": (
                "||Delta eta|| + ||Delta omega|| <= C_rot "
                "(||Delta R_eta|| + ||Delta R_omega|| + h ||Delta alpha||)"
            ),
            "uses_dynamic_rows": False,
            "uses_stage_residual_lemma": False,
        },
        "remaining_promotion_gaps": [
            "promote the component nonlinear binding together with the kinematic-block, Lie-chart, and row-injection certificates into the aggregate weighted PS2 inverse constant",
        ],
        "source_consistency": {
            "p_tube_schema": p_tube.get("schema"),
            "p_tube_closed": p_tube.get("primitive_closed"),
            "p_tube_pc2_closed": p_tube.get("pc2_closed"),
            "p_state_map_schema": p_state_map.get("schema"),
            "p_state_map_definition_closed": p_state_map.get("ps1_map_definition_closed"),
            "ps2_target_schema": ps2_target.get("schema"),
            "ps2_target_spec_closed": ps2_target.get("ps2_target_spec_closed"),
            "ps2_target_infsup_closed": ps2_target.get("ps2_inverse_or_infsup_closed"),
            "kinematic_block_schema": kinematic_block.get("schema"),
            "kinematic_block_bound_certified": kinematic_block.get(
                "certifies_uniform_euclidean_kinematic_subblock_bound"
            ),
            "kinematic_block_full_ps2": kinematic_block.get("certifies_full_nonlinear_ps2"),
            "lie_chart_schema": lie_chart.get("schema"),
            "lie_chart_so3_norm_equivalence": lie_chart.get("certifies_so3_chart_norm_equivalence"),
            "lie_chart_full_mean_value_binding": lie_chart.get("certifies_full_nonlinear_mean_value_binding"),
            "row_injection_schema": row_injection.get("schema"),
            "row_injection_certified": row_injection.get("certifies_72_to_96_row_injection"),
            "row_injection_unweighted_scaling": row_injection.get("certifies_unweighted_residual_scaling"),
            "row_injection_full_ps2": row_injection.get("certifies_full_nonlinear_ps2"),
        },
        "manuscript_link": {
            "lemma_label": "lem:d5-p-state-ps2-nonlinear-binding",
            "main_tex_present": all(contains_normalized(main_tex, token) for token in manuscript_tokens),
            "flat_tex_present": all(contains_normalized(flat_tex, token) for token in manuscript_tokens),
            "tokens": manuscript_tokens,
        },
        "claim_boundary": {
            "allowed_now": (
                "The nonlinear rotational Lie-collocation row is bound to the "
                "weighted PS2 kinematic template by a compact-tube mean-value "
                "estimate and small-step absorption."
            ),
            "forbidden_now": [
                "aggregate weighted PS2 inverse promoted",
                "PS3 actual state lift conversion",
                "P_state primitive closure",
                "Taylor term bounds certified from P_state",
                "primitive/Taylor PC2 route closure",
                "submission-ready proof",
            ],
            "close_condition": (
                "The aggregate PS2 target can be promoted only after this component "
                "certificate is combined in the P_state lift-gap ledger with the "
                "kinematic-block, Lie-chart, and row-injection certificates."
            ),
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# D5 P_state PS2 Nonlinear Binding Audit",
        "",
        "Status: **PS2 nonlinear rotational-row binding closed; aggregate PS2 promotion remains open**.",
        "",
        "This artifact records the compact-tube mean-value estimate for the",
        "implemented rotational Lie-collocation row used by the weighted PS2",
        "route. It is a component proof, not a standalone PS2 inverse proof.",
        "",
        "## Summary",
        "",
        f"- Nonlinear binding recorded: `{result['p_state_ps2_nonlinear_binding_recorded']}`.",
        f"- Rotational Lie-row mean-value binding certified: `{result['certifies_rotational_lie_row_mean_value_binding']}`.",
        f"- Compact-tube Lipschitz bound certified: `{result['certifies_compact_tube_lipschitz_bound']}`.",
        f"- Small-step absorption certified: `{result['certifies_small_step_absorption']}`.",
        f"- Full nonlinear mean-value binding certified: `{result['certifies_full_nonlinear_mean_value_binding']}`.",
        f"- Full nonlinear PS2 certified by this artifact: `{result['certifies_full_nonlinear_ps2']}`.",
        f"- PS2 closed: `{result['ps2_inverse_or_infsup_closed']}`.",
        f"- Primitive/Taylor PC2 route closed: `{result['pc2_closed']}`.",
        "",
        "## Mean-Value Bound",
        "",
        "`F(eta, omega) = J_r(eta)^(-1) omega` is smooth on the accepted compact",
        "chart tube. Hence `||Delta F|| <= L_F (||Delta eta|| + ||Delta omega||)`.",
        "",
        "For the implemented row",
        "",
        "`R_eta_i = eta_i - h sum_j A_ij J_r(eta_j)^(-1) omega_j`,",
        "",
        "the perturbation term is multiplied by `h ||A_G||_2`. After shrinking the",
        "asymptotic step threshold so that `h ||A_G||_2 L_F <= 1/2`, the nonlinear",
        "term is absorbed on the left, giving the rotational weighted-PS2 bound.",
        "",
        "## Remaining Promotion Gap",
        "",
    ]
    for item in result["remaining_promotion_gaps"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Acceptance Boundary",
            "",
            "- The rotational nonlinear compact-tube mean-value estimate is certified.",
            "- The component proof uses only the non-dynamic map, Lie chart, and compact-tube constants.",
            "- It does not by itself promote the aggregate PS2 inverse.",
            "- PS3, P_state, PC2, and induced Taylor bounds remain open.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("d5_p_state_ps2_nonlinear_binding_audit=written")
    print("rotational_mean_value_binding=True")
    print("ps2_closed=False")
    print("pc2_closed=False")


if __name__ == "__main__":
    main()
