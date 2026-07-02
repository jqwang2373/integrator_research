#!/usr/bin/env python3
"""Build the D5 P_state PS2 Lie-chart binding audit.

This artifact records the compact-tube SO(3) chart norm-equivalence constants
needed by the weighted PS2 route.  It is deliberately narrower than a PS2
inverse proof: nonlinear mean-value binding and 72-to-96 row injection remain
open.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "D5_P_STATE_PS2_LIE_CHART_BINDING_AUDIT.json"
OUT_MD = PAPER / "D5_P_STATE_PS2_LIE_CHART_BINDING_AUDIT.md"


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


def right_jacobian_inverse_norm_bound(theta: float) -> float:
    """Exact SO(3) right-Jacobian inverse 2-norm bound for ||eta|| <= theta."""
    return theta / (2.0 * math.sin(0.5 * theta))


def main() -> None:
    p_tube = read_json(PAPER / "D5_P_TUBE_CONSTANTS_AUDIT.json")
    ps2_target = read_json(PAPER / "D5_P_STATE_PS2_WEIGHTED_TARGET_AUDIT.json")
    p_state_map = read_json(PAPER / "D5_P_STATE_MAP_DEFINITION_AUDIT.json")
    p_state_gap = read_json(PAPER / "D5_P_STATE_LIFT_GAP_AUDIT.json")
    main_tex = read_text(PAPER / "main_cmame.tex")
    flat_tex = read_text(PAPER / "cmame_submission_flat" / "main_cmame_submission.tex")

    chart_radius = 0.5
    jr_norm_bound = 1.0
    jr_inv_norm_bound = right_jacobian_inverse_norm_bound(chart_radius)
    equivalence_factor = max(jr_norm_bound, jr_inv_norm_bound)
    rotational_chart_rows = 18
    angular_velocity_rows = 18

    manuscript_tokens = [
        r"\label{lem:d5-p-state-ps2-lie-chart-binding}",
        "SO(3) chart binding for the weighted PS2 route",
        r"\|J_r(\eta)\|_2\le 1",
        "does not supply the nonlinear mean-value estimate",
        "does not close PS2",
    ]

    result = {
        "schema": "d5-p-state-ps2-lie-chart-binding-audit-v1",
        "status": "ps2_lie_chart_binding_recorded_full_ps2_open",
        "read_only": True,
        "run_v047_invoked": False,
        "submission_ready": False,
        "pc2_closed": False,
        "proof_gap_closed": False,
        "primitive_id": "P_state_lift",
        "plan_id": "P_state",
        "primitive_closed": False,
        "p_state_ps2_lie_chart_binding_recorded": True,
        "certifies_so3_chart_norm_equivalence": True,
        "certifies_rotational_chart_binding_constant": True,
        "certifies_full_nonlinear_mean_value_binding": False,
        "certifies_full_row_injection_scaling": False,
        "certifies_full_nonlinear_ps2": False,
        "ps2_inverse_or_infsup_closed": False,
        "certifies_induced_taylor_bounds": False,
        "certifies_dynamic_row_defect": False,
        "constants": {
            "chart_radius_rad": chart_radius,
            "right_jacobian_2_norm_bound": jr_norm_bound,
            "right_jacobian_inverse_2_norm_bound": jr_inv_norm_bound,
            "chart_equivalence_factor": equivalence_factor,
            "valid_radius_condition": "chart_radius_rad < pi",
        },
        "dimensions": {
            "stages": 3,
            "bodies": 2,
            "rotational_chart_rows": rotational_chart_rows,
            "angular_velocity_rows": angular_velocity_rows,
            "rotational_kinematic_rows": rotational_chart_rows + angular_velocity_rows,
        },
        "resolved_binding_input": (
            "pure SO(3) chart norm-equivalence constants for the rotational "
            "coordinates in the weighted PS2 route"
        ),
        "remaining_binding_gaps": [
            "prove the nonlinear compact-tube mean-value estimate for the implemented rotational row eta_i - h sum_j A_ij J_r^{-1}(eta_j) omega_j",
            "record the full-row ordering/scaling injection from the 72 kinematic rows into the 96-row non-dynamic residual norm",
        ],
        "source_consistency": {
            "p_tube_schema": p_tube.get("schema"),
            "p_tube_closed": p_tube.get("primitive_closed"),
            "p_tube_pc2_closed": p_tube.get("pc2_closed"),
            "ps2_target_schema": ps2_target.get("schema"),
            "ps2_target_spec_closed": ps2_target.get("ps2_target_spec_closed"),
            "ps2_target_infsup_closed": ps2_target.get("ps2_inverse_or_infsup_closed"),
            "p_state_map_schema": p_state_map.get("schema"),
            "p_state_map_definition_closed": p_state_map.get("ps1_map_definition_closed"),
            "p_state_gap_schema": p_state_gap.get("schema"),
            "p_state_gap_closed": p_state_gap.get("primitive_closed"),
        },
        "manuscript_link": {
            "lemma_label": "lem:d5-p-state-ps2-lie-chart-binding",
            "main_tex_present": all(contains_normalized(main_tex, token) for token in manuscript_tokens),
            "flat_tex_present": all(contains_normalized(flat_tex, token) for token in manuscript_tokens),
            "tokens": manuscript_tokens,
        },
        "claim_boundary": {
            "allowed_now": (
                "The pure SO(3) chart norm-equivalence constants needed by the "
                "weighted PS2 kinematic route are recorded on a compact chart tube."
            ),
            "forbidden_now": [
                "full nonlinear rotational row mean-value binding",
                "72-to-96 non-dynamic row injection/scaling closure",
                "full nonlinear PS2 closure",
                "PS3 state lift conversion",
                "P_state primitive closure",
                "Taylor term bounds certified from P_state",
                "primitive/Taylor PC2 route closure",
                "submission-ready proof",
            ],
            "close_condition": (
                "PS2 can only be promoted after this chart-equivalence input is "
                "combined with a nonlinear compact-tube mean-value estimate and "
                "the full 72-to-96 row injection/scaling proof."
            ),
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# D5 P_state PS2 Lie-Chart Binding Audit",
        "",
        "Status: **PS2 Lie-chart binding recorded; full PS2 remains open**.",
        "",
        "This artifact records the compact-tube SO(3) chart norm-equivalence",
        "constants used by the weighted PS2 route. It is not a nonlinear PS2",
        "inverse or inf-sup proof.",
        "",
        "## Summary",
        "",
        f"- Lie-chart binding recorded: `{result['p_state_ps2_lie_chart_binding_recorded']}`.",
        f"- SO(3) chart norm-equivalence certified: `{result['certifies_so3_chart_norm_equivalence']}`.",
        f"- Full nonlinear mean-value binding certified: `{result['certifies_full_nonlinear_mean_value_binding']}`.",
        f"- Full row injection/scaling certified: `{result['certifies_full_row_injection_scaling']}`.",
        f"- Full nonlinear PS2 certified: `{result['certifies_full_nonlinear_ps2']}`.",
        f"- Chart radius: `{chart_radius}` rad.",
        f"- Right-Jacobian 2-norm bound: `{jr_norm_bound:.12e}`.",
        f"- Right-Jacobian inverse 2-norm bound: `{jr_inv_norm_bound:.12e}`.",
        f"- Chart equivalence factor: `{equivalence_factor:.12e}`.",
        f"- Rotational kinematic rows: `{rotational_chart_rows + angular_velocity_rows}`.",
        f"- PS2 closed: `{result['ps2_inverse_or_infsup_closed']}`.",
        f"- Primitive/Taylor PC2 route closed: `{result['pc2_closed']}`.",
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
            "- Pure SO(3) chart norm-equivalence is recorded.",
            "- Nonlinear rotational-row mean-value binding remains open.",
            "- 72-to-96 residual row injection/scaling remains open.",
            "- PS2, PS3, P_state, PC2, and induced Taylor bounds remain open.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("d5_p_state_ps2_lie_chart_binding_audit=written")
    print(f"chart_equivalence_factor={equivalence_factor:.12e}")
    print("ps2_closed=False")
    print("pc2_closed=False")


if __name__ == "__main__":
    main()
