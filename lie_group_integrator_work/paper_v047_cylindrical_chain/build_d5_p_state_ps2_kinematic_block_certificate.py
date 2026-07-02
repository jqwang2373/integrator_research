#!/usr/bin/env python3
"""Build the D5 P_state PS2 kinematic-block certificate.

This artifact records an analytic, reproducible constant for the 72-row
Gauss kinematic subblock used by the weighted PS2 route.  It is a proof
increment, not a full PS2 closure: the nonlinear Lie-chart/tube binding is
still recorded as open.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "D5_P_STATE_PS2_KINEMATIC_BLOCK_CERTIFICATE.json"
OUT_MD = PAPER / "D5_P_STATE_PS2_KINEMATIC_BLOCK_CERTIFICATE.md"


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


def gauss3_matrix() -> np.ndarray:
    root15 = math.sqrt(15.0)
    return np.asarray(
        [
            [5.0 / 36.0, 2.0 / 9.0 - root15 / 15.0, 5.0 / 36.0 - root15 / 30.0],
            [5.0 / 36.0 + root15 / 24.0, 2.0 / 9.0, 5.0 / 36.0 - root15 / 24.0],
            [5.0 / 36.0 + root15 / 30.0, 2.0 / 9.0 + root15 / 15.0, 5.0 / 36.0],
        ],
        dtype=float,
    )


def inverse_template(gauss_a: np.ndarray, h: float) -> np.ndarray:
    eye = np.eye(3)
    zeros = np.zeros((3, 3))
    return np.block(
        [
            [eye, h * gauss_a, h * (gauss_a @ gauss_a)],
            [zeros, eye, gauss_a],
        ]
    )


def main() -> None:
    ps2_target = read_json(PAPER / "D5_P_STATE_PS2_WEIGHTED_TARGET_AUDIT.json")
    p_state_gap = read_json(PAPER / "D5_P_STATE_LIFT_GAP_AUDIT.json")
    p_tube = read_json(PAPER / "D5_P_TUBE_CONSTANTS_AUDIT.json")
    p_state_map = read_json(PAPER / "D5_P_STATE_MAP_DEFINITION_AUDIT.json")
    p_state_anti = read_json(PAPER / "D5_P_STATE_ANTICIRCULARITY_AUDIT.json")
    main_tex = read_text(PAPER / "main_cmame.tex")
    flat_tex = read_text(PAPER / "cmame_submission_flat" / "main_cmame_submission.tex")

    h_max = 0.04
    gauss_a = gauss3_matrix()
    a_norm = float(np.linalg.norm(gauss_a, ord=2))
    a2_norm = float(np.linalg.norm(gauss_a @ gauss_a, ord=2))
    template = inverse_template(gauss_a, h_max)
    template_norm = float(np.linalg.norm(template, ord=2))
    simple_bound = float(math.sqrt((1.0 + h_max * a_norm + h_max * a2_norm) ** 2 + (1.0 + a_norm) ** 2))
    row_dim = 72
    state_dim = 72
    acceleration_dim = 36
    lower_pair_surplus_rows = 24
    manuscript_tokens = [
        r"\label{lem:d5-p-state-ps2-kinematic-block}",
        "Kinematic-block certificate for the weighted PS2 route",
        "72 kinematic rows already provide a concrete analytic subblock",
        "24 lower-pair rows are surplus",
        "does not by itself close PS2",
    ]

    result = {
        "schema": "d5-p-state-ps2-kinematic-block-certificate-v1",
        "status": "ps2_kinematic_block_certificate_recorded_binding_gap_open",
        "read_only": True,
        "run_v047_invoked": False,
        "submission_ready": False,
        "pc2_closed": False,
        "proof_gap_closed": False,
        "primitive_id": "P_state_lift",
        "plan_id": "P_state",
        "primitive_closed": False,
        "ps2_kinematic_block_certificate_recorded": True,
        "certifies_uniform_euclidean_kinematic_subblock_bound": True,
        "certifies_full_nonlinear_ps2": False,
        "ps2_inverse_or_infsup_closed": False,
        "ps3_state_lift_conversion_closed": False,
        "certifies_induced_taylor_bounds": False,
        "certifies_dynamic_row_defect": False,
        "constants": {
            "h_max": h_max,
            "gauss_matrix_2_norm": a_norm,
            "gauss_matrix_square_2_norm": a2_norm,
            "kinematic_inverse_template_2_norm_at_h_max": template_norm,
            "simple_triangle_bound": simple_bound,
        },
        "dimensions": {
            "stages": 3,
            "bodies": 2,
            "scalar_channel_state_dim": 6,
            "scalar_channel_weighted_input_dim": 9,
            "state_block_dimension": state_dim,
            "auxiliary_acceleration_dimension": acceleration_dim,
            "kinematic_row_dimension": row_dim,
            "lower_pair_surplus_rows_not_needed_for_subblock": lower_pair_surplus_rows,
            "non_dynamic_row_dimension": row_dim + lower_pair_surplus_rows,
        },
        "analytic_template": {
            "residual_form": [
                "delta R_q = delta q - h A_G delta v",
                "delta R_v = delta v - h A_G delta a",
            ],
            "inverse_form": [
                "delta v = delta R_v + A_G (h delta a)",
                "delta q = delta R_q + h A_G delta R_v + h A_G^2 (h delta a)",
            ],
            "input_norm": "||(delta R_q, delta R_v, h delta a)||_2",
            "output_norm": "||(delta q, delta v)||_2",
            "uniform_for_h_interval": "0 < h <= 0.04",
        },
        "remaining_binding_gaps": [
            "bind the implemented rotational Lie-chart residual rows to this Euclidean triangular template through compact-tube dexp norm-equivalence constants",
            "turn the linear subblock estimate into a nonlinear compact-tube mean-value estimate for the accepted non-dynamic map",
            "record the full-row ordering/scaling injection from the 72 kinematic rows into the 96-row non-dynamic residual norm",
        ],
        "source_consistency": {
            "ps2_target_schema": ps2_target.get("schema"),
            "ps2_target_spec_closed": ps2_target.get("ps2_target_spec_closed"),
            "ps2_target_infsup_closed": ps2_target.get("ps2_inverse_or_infsup_closed"),
            "p_state_gap_schema": p_state_gap.get("schema"),
            "p_state_gap_closed": p_state_gap.get("primitive_closed"),
            "p_tube_schema": p_tube.get("schema"),
            "p_tube_closed": p_tube.get("primitive_closed"),
            "p_state_map_schema": p_state_map.get("schema"),
            "p_state_map_definition_closed": p_state_map.get("ps1_map_definition_closed"),
            "p_state_anticircularity_schema": p_state_anti.get("schema"),
            "p_state_anticircularity_closed": p_state_anti.get("ps4_anticircularity_closed"),
        },
        "manuscript_link": {
            "lemma_label": "lem:d5-p-state-ps2-kinematic-block",
            "main_tex_present": all(contains_normalized(main_tex, token) for token in manuscript_tokens),
            "flat_tex_present": all(contains_normalized(flat_tex, token) for token in manuscript_tokens),
            "tokens": manuscript_tokens,
        },
        "claim_boundary": {
            "allowed_now": "The Euclidean Gauss kinematic subblock has a reproducible h-uniform weighted state estimate for h<=0.04.",
            "forbidden_now": [
                "full nonlinear PS2 closure",
                "PS3 state lift conversion",
                "P_state primitive closure",
                "Taylor term bounds certified from P_state",
                "primitive/Taylor PC2 route closure",
                "submission-ready proof",
            ],
            "close_condition": (
                "Promote this subblock certificate to PS2 closure only after the "
                "rotational Lie-chart norm equivalence, nonlinear mean-value binding, "
                "and 72-to-96 row injection/scaling are written as uniform compact-tube estimates."
            ),
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# D5 P_state PS2 Kinematic-Block Certificate",
        "",
        "Status: **PS2 kinematic-block certificate recorded; binding gap remains open**.",
        "",
        "This artifact records an analytic bound for the 72 kinematic rows in",
        "the weighted PS2 route. It is not a full nonlinear PS2 proof.",
        "",
        "## Summary",
        "",
        f"- Kinematic subblock certificate recorded: `{result['ps2_kinematic_block_certificate_recorded']}`.",
        f"- Uniform Euclidean kinematic subblock bound certified: `{result['certifies_uniform_euclidean_kinematic_subblock_bound']}`.",
        f"- Full nonlinear PS2 certified: `{result['certifies_full_nonlinear_ps2']}`.",
        f"- Kinematic rows / lower-pair surplus rows: `{row_dim}` / `{lower_pair_surplus_rows}`.",
        f"- Step threshold: `0 < h <= {h_max}`.",
        f"- Gauss matrix 2-norm: `{a_norm:.12e}`.",
        f"- Kinematic inverse template 2-norm at h_max: `{template_norm:.12e}`.",
        f"- Simple triangle bound: `{simple_bound:.12e}`.",
        f"- PS2 closed: `{result['ps2_inverse_or_infsup_closed']}`.",
        f"- Primitive/Taylor PC2 route closed: `{result['pc2_closed']}`.",
        "",
        "## Analytic Template",
        "",
        "`delta R_q = delta q - h A_G delta v`",
        "",
        "`delta R_v = delta v - h A_G delta a`",
        "",
        "`delta v = delta R_v + A_G (h delta a)`",
        "",
        "`delta q = delta R_q + h A_G delta R_v + h A_G^2 (h delta a)`",
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
            "- The Euclidean Gauss kinematic subblock estimate is recorded.",
            "- The full nonlinear PS2 inverse or inf-sup proof remains open.",
            "- PS3, P_state, PC2, and induced Taylor bounds remain open.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("d5_p_state_ps2_kinematic_block_certificate=written")
    print(f"kinematic_inverse_template_norm={template_norm:.12e}")
    print("ps2_closed=False")
    print("pc2_closed=False")


if __name__ == "__main__":
    main()
