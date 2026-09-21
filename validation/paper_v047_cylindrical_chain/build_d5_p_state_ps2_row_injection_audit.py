#!/usr/bin/env python3
"""Build the D5 P_state PS2 row-injection audit.

This artifact records the 72-to-96 residual row injection used by the weighted
PS2 route.  It proves only the row-selection/scaling constant for the accepted
non-dynamic residual ordering; the nonlinear compact-tube mean-value estimate
remains open.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
OUT_JSON = PAPER / "D5_P_STATE_PS2_ROW_INJECTION_AUDIT.json"
OUT_MD = PAPER / "D5_P_STATE_PS2_ROW_INJECTION_AUDIT.md"


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
    ps2_target = read_json(PAPER / "D5_P_STATE_PS2_WEIGHTED_TARGET_AUDIT.json")
    kinematic_block = read_json(PAPER / "D5_P_STATE_PS2_KINEMATIC_BLOCK_CERTIFICATE.json")
    lie_chart = read_json(PAPER / "D5_P_STATE_PS2_LIE_CHART_BINDING_AUDIT.json")
    p_state_gap = read_json(PAPER / "D5_P_STATE_LIFT_GAP_AUDIT.json")
    main_tex = read_text(LATEX / "main_cmame.tex")
    flat_tex = read_text(LATEX / "cmame_submission_flat" / "main_cmame_submission.tex")

    kinematic_rows = 72
    lower_pair_rows = 24
    non_dynamic_rows = 96
    selector_norm = 1.0

    manuscript_tokens = [
        r"\label{lem:d5-p-state-ps2-row-injection}",
        "72-to-96 row injection for the weighted PS2 route",
        r"\|\Pi_{\mathrm{kin}}\|_2=1",
        "unweighted non-dynamic residual norm dominates the kinematic residual norm",
        "does not supply the nonlinear mean-value estimate",
    ]

    result = {
        "schema": "d5-p-state-ps2-row-injection-audit-v1",
        "status": "ps2_row_injection_recorded_full_ps2_open",
        "read_only": True,
        "run_v047_invoked": False,
        "submission_ready": False,
        "pc2_closed": False,
        "proof_gap_closed": False,
        "primitive_id": "P_state_lift",
        "plan_id": "P_state",
        "primitive_closed": False,
        "p_state_ps2_row_injection_recorded": True,
        "certifies_72_to_96_row_injection": True,
        "certifies_unweighted_residual_scaling": True,
        "row_selection_operator_2_norm": selector_norm,
        "certifies_full_nonlinear_mean_value_binding": False,
        "certifies_full_nonlinear_ps2": False,
        "ps2_inverse_or_infsup_closed": False,
        "certifies_induced_taylor_bounds": False,
        "certifies_dynamic_row_defect": False,
        "dimensions": {
            "kinematic_row_dimension": kinematic_rows,
            "lower_pair_surplus_rows": lower_pair_rows,
            "non_dynamic_row_dimension": non_dynamic_rows,
            "row_order": [
                "translational_position_collocation_18",
                "rotational_lie_collocation_18",
                "translational_velocity_collocation_18",
                "angular_velocity_collocation_18",
                "lower_pair_fullva_24",
            ],
        },
        "operator_statement": {
            "selector": "Pi_kin selects the first four 18-row kinematic families from N_h^nd",
            "norm_bound": "||Pi_kin delta N_h^nd||_2 <= ||delta N_h^nd||_2",
            "operator_norm": selector_norm,
            "weighted_ps2_use": "replace the kinematic residual norm by the full non-dynamic residual norm",
        },
        "remaining_binding_gaps": [
            "prove the nonlinear compact-tube mean-value estimate for the implemented rotational row eta_i - h sum_j A_ij J_r^{-1}(eta_j) omega_j",
        ],
        "source_consistency": {
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
            "p_state_gap_schema": p_state_gap.get("schema"),
            "p_state_gap_closed": p_state_gap.get("primitive_closed"),
        },
        "manuscript_link": {
            "lemma_label": "lem:d5-p-state-ps2-row-injection",
            "main_tex_present": all(contains_normalized(main_tex, token) for token in manuscript_tokens),
            "flat_tex_present": all(contains_normalized(flat_tex, token) for token in manuscript_tokens),
            "tokens": manuscript_tokens,
        },
        "claim_boundary": {
            "allowed_now": (
                "The accepted 96-row non-dynamic residual norm dominates the 72-row "
                "kinematic residual norm with selection constant one."
            ),
            "forbidden_now": [
                "full nonlinear rotational row mean-value binding",
                "full nonlinear PS2 closure",
                "PS3 state lift conversion",
                "P_state primitive closure",
                "Taylor term bounds certified from P_state",
                "primitive/Taylor PC2 route closure",
                "submission-ready proof",
            ],
            "close_condition": (
                "PS2 can only be promoted after the row-injection certificate, "
                "the kinematic subblock certificate, and the Lie-chart binding are "
                "combined with a nonlinear compact-tube mean-value estimate."
            ),
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# D5 P_state PS2 Row-Injection Audit",
        "",
        "Status: **PS2 row injection recorded; full PS2 remains open**.",
        "",
        "This artifact records the 72-to-96 residual row injection used by the",
        "weighted PS2 route. It is not a nonlinear PS2 inverse or inf-sup proof.",
        "",
        "## Summary",
        "",
        f"- Row injection recorded: `{result['p_state_ps2_row_injection_recorded']}`.",
        f"- 72-to-96 row injection certified: `{result['certifies_72_to_96_row_injection']}`.",
        f"- Unweighted residual scaling certified: `{result['certifies_unweighted_residual_scaling']}`.",
        f"- Row-selection operator 2-norm: `{selector_norm:.12e}`.",
        f"- Kinematic/lower-pair/non-dynamic rows: `{kinematic_rows}` / `{lower_pair_rows}` / `{non_dynamic_rows}`.",
        f"- Full nonlinear mean-value binding certified: `{result['certifies_full_nonlinear_mean_value_binding']}`.",
        f"- Full nonlinear PS2 certified: `{result['certifies_full_nonlinear_ps2']}`.",
        f"- PS2 closed: `{result['ps2_inverse_or_infsup_closed']}`.",
        f"- Primitive/Taylor PC2 route closed: `{result['pc2_closed']}`.",
        "",
        "## Operator Statement",
        "",
        "`||Pi_kin delta N_h^nd||_2 <= ||delta N_h^nd||_2`",
        "",
        "## Remaining Binding Gaps",
        "",
    ]
    for item in result["remaining_binding_gaps"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Acceptance Boundary",
            "",
            "- The 72-to-96 unweighted row injection is recorded.",
            "- Nonlinear rotational-row mean-value binding remains open.",
            "- PS2, PS3, P_state, PC2, and induced Taylor bounds remain open.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("d5_p_state_ps2_row_injection_audit=written")
    print("row_selection_operator_2_norm=1.000000000000e+00")
    print("ps2_closed=False")
    print("pc2_closed=False")


if __name__ == "__main__":
    main()
