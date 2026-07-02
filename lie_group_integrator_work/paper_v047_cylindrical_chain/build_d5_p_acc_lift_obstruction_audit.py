#!/usr/bin/env python3
"""Build the D5 P_acc PA2 lift-obstruction audit.

This audit records a narrow anti-overclaim result: the accepted velocity
collocation rows alone do not turn an O(h^7) stage-velocity lift into an
O(h^7) stage-acceleration lift.  The Gauss matrix is invertible, but the
inverse relation contains a factor 1/h.  Therefore PA2 needs either a stronger
velocity-stage estimate, an additional non-dynamic inverse estimate, or an
explicit acceleration-lift assumption.  This is not a closure certificate.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent.parent
REF_TXT = ROOT / "s11044-026-10153-w.txt"
RUN_V047 = PAPER.parent / "v047_cylindrical_chain_pipeline" / "run_v047.py"
OUT_JSON = PAPER / "D5_P_ACC_LIFT_OBSTRUCTION_AUDIT.json"
OUT_MD = PAPER / "D5_P_ACC_LIFT_OBSTRUCTION_AUDIT.md"


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
    return np.array(
        [
            [5.0 / 36.0, 2.0 / 9.0 - root15 / 15.0, 5.0 / 36.0 - root15 / 30.0],
            [5.0 / 36.0 + root15 / 24.0, 2.0 / 9.0, 5.0 / 36.0 - root15 / 24.0],
            [5.0 / 36.0 + root15 / 30.0, 2.0 / 9.0 + root15 / 15.0, 5.0 / 36.0],
        ],
        dtype=float,
    )


def main() -> None:
    p_acc_independence = read_json(PAPER / "D5_P_ACC_INDEPENDENCE_AUDIT.json")
    p_acc_row_binding = read_json(PAPER / "D5_P_ACC_ROW_BINDING_AUDIT.json")
    p_state_gap = read_json(PAPER / "D5_P_STATE_LIFT_GAP_AUDIT.json")
    kinematic_certificate = read_json(PAPER / "KINEMATIC_ROW_DEFECT_CERTIFICATE.json")
    reference_text = read_text(REF_TXT)
    run_v047_text = read_text(RUN_V047)
    main_tex = read_text(PAPER / "main_cmame.tex")
    flat_tex = read_text(PAPER / "cmame_submission_flat" / "main_cmame_submission.tex")

    matrix = gauss3_matrix()
    inverse = np.linalg.inv(matrix)
    det = float(np.linalg.det(matrix))
    norm_inf = float(np.linalg.norm(inverse, ord=np.inf))
    norm_2 = float(np.linalg.norm(inverse, ord=2))
    cond_2 = float(np.linalg.cond(matrix, p=2))

    manuscript_tokens = [
        r"\label{lem:d5-p-acc-pa2-obstruction}",
        "velocity-collocation rows alone are insufficient",
        r"\delta A=h^{-1}(A_G^{-1}\otimes I)",
        "PA2 therefore remains open",
    ]
    reference_tokens = {
        "tfe_section_present": "3 Higher order time integration in absolute coordinates using TFE",
        "first_order_derivative_scaling_present": "δv = h1 δu and δ v̇ = h12 δu",
        "differential_residuals_present": "res1 (t) = ẋ(t) − y(t),       res2 (t) = ẏ(t) − z(t)",
        "velocity_from_position_relation_present": "ȳ = x̄˙ = 𝜶¯ x̄",
        "acceleration_from_velocity_relation_present": "z̄ = x̄¨ = 𝜶¯ ȳ",
        "newton_correction_derivative_relation_present": "δ x̄˙ = 𝜶¯ δ x̄,   δ x̄¨ = 𝜶¯ δ x̄˙",
    }
    reference_features = {
        key: contains_normalized(reference_text, token)
        for key, token in reference_tokens.items()
    }
    implementation_tokens = {
        "runtime_newton_euler_row_layout_present": '("newton_euler_weak_balance", 24, 12)',
        "runtime_lower_pair_acceleration_constraint_layout_present": (
            '("lower_pair_index3_weak_constraints", 36, 8)'
        ),
        "runtime_velocity_row_layout_present": '("translational_velocity_weak_defect", 12, 6)',
        "runtime_angular_velocity_row_layout_present": '("angular_velocity_weak_defect", 18, 6)',
        "translational_velocity_collocation_uses_h_times_acceleration": (
            'v_coll_axis = (kin["rel_vel"][joint] - initial_rel_vel[joint] - h * sum('
        ),
        "translational_velocity_collocation_uses_relative_acceleration": (
            'stage_kin[sj]["rel_acc"][joint]'
        ),
        "angular_velocity_collocation_uses_h_times_acceleration": (
            'spin_acc_coll_axis = kin["rel_spin_vel"][joint] - initial_rel_spin_vel[joint] - h * sum('
        ),
        "angular_velocity_collocation_uses_relative_spin_acceleration": (
            'stage_kin[sj]["rel_spin_acc"][joint]'
        ),
        "dynamic_translational_rows_use_unweighted_acceleration": (
            'trans = masses[body] * st["a"][body]'
        ),
        "dynamic_rotational_rows_use_unweighted_angular_acceleration": (
            'Js[body] @ st["alpha"][body]'
        ),
        "runtime_stage_row_assembly_order_present": (
            "out.extend([jnp.concatenate(pvel), jnp.concatenate(u_block), "
            "jnp.concatenate(pacc), jnp.concatenate(w_block), "
            "jnp.concatenate(dyn), jnp.concatenate(constraints)])"
        ),
    }
    implementation_features = {
        key: contains_normalized(run_v047_text, token)
        for key, token in implementation_tokens.items()
    }

    result = {
        "schema": "d5-p-acc-lift-obstruction-audit-v1",
        "status": "p_acc_pa2_obstruction_recorded_lift_open",
        "read_only": True,
        "run_v047_invoked": False,
        "submission_ready": False,
        "pc2_closed": False,
        "proof_gap_closed": False,
        "primitive_id": "P_acceleration_lift",
        "primitive_closed": False,
        "pa2_closed": False,
        "pa2_obstruction_recorded": True,
        "velocity_collocation_alone_sufficient_for_O_h7_acceleration": False,
        "current_recorded_inputs_imply_only_unweighted_acceleration_rate": "O(h^6)",
        "acceleration_lift_rate_proved": False,
        "term_bounds_proved": 0,
        "gauss_matrix": {
            "stage_count": 3,
            "determinant": det,
            "inverse_inf_norm": norm_inf,
            "inverse_2_norm": norm_2,
            "condition_2": cond_2,
            "invertible": abs(det) > 1.0e-14,
        },
        "rate_algebra": {
            "velocity_collocation_difference": "delta_V - h (A_G \\otimes I) delta_A = rho_V",
            "acceleration_difference": "delta_A = h^{-1} (A_G^{-1} \\otimes I) (delta_V - rho_V)",
            "if_delta_v_and_rho_v_are_O_h7": "delta_A is bounded only as O(h^6)",
            "needed_for_unweighted_delta_A_O_h7": [
                "delta_V=O(h^8) and rho_V=O(h^8) in the unweighted stage norm",
                "or an independent non-dynamic stage-map inverse that controls acceleration directly",
                "or an explicit theorem assumption P_acceleration_lift=O(h^7)",
            ],
            "weighted_h_delta_A_O_h7_is_not_enough_for_current_D5_budget": True,
        },
        "reference_paper_scaling_context": {
            "reference_text": "../../s11044-026-10153-w.txt",
            "section": "source paper Section 3, higher-order time integration in absolute coordinates using TFE",
            "features": reference_features,
            "tokens": reference_tokens,
            "interpretation": (
                "The source-paper TFE construction expresses derivative variables through "
                "position/velocity variables and step-size-dependent derivative operators. "
                "Its own first-order example records velocity and acceleration corrections "
                "with inverse powers of h. Therefore the source paper does not supply the "
                "missing unweighted O(h^7) acceleration-lift estimate for the accepted "
                "Gauss/FullVA residual."
            ),
            "supports_obstruction_not_closure": True,
            "usable_as_p_acc_proof": False,
            "why_not": (
                "Derivative reconstruction or weighted residual formulas can control a "
                "scaled derivative variable, but the D5 acceleration Taylor rows contain "
                "m_b delta a and J_b delta alpha without an extra h factor."
            ),
            "strict_consequence": (
                "A submission-standard Taylor proof must still prove unweighted "
                "delta A=O(h^7), prove O(h^8) velocity-stage and velocity-row errors "
                "before the 1/h inversion, provide a direct non-dynamic acceleration "
                "inverse, or carry P_acceleration_lift=O(h^7) as an explicit theorem "
                "assumption."
            ),
        },
        "implementation_row_scaling_evidence": {
            "run_v047_path": "../v047_cylindrical_chain_pipeline/run_v047.py",
            "features": implementation_features,
            "tokens": implementation_tokens,
            "row_layout_conclusion": (
                "The accepted runtime residual has 36 Newton-Euler rows per three-stage "
                "step, with each stage placing those rows at offsets 24:36. The stage "
                "velocity-collocation families contain acceleration only through h*A_G, "
                "while the Newton-Euler dynamic rows contain masses[body]*a and "
                "J_b*alpha without an extra h factor."
            ),
            "lower_pair_boundary": (
                "The lower-pair acceleration constraints are non-dynamic and unweighted, "
                "but they constrain only the lower-pair constraint directions; they do "
                "not provide a full unweighted inverse for all translational and angular "
                "body accelerations required by the 36 Newton-Euler Taylor terms."
            ),
            "supports_obstruction_not_closure": True,
            "usable_as_unweighted_acceleration_lift_proof": False,
            "strict_consequence": (
                "The implementation binding preserves the PA2 close condition: a strict "
                "Taylor proof still needs a uniform unweighted delta A=O(h^7) estimate, "
                "an O(h^8) pre-inversion velocity-collocation estimate, a genuine full "
                "non-dynamic acceleration inverse, or an explicit P_acceleration_lift "
                "theorem assumption."
            ),
        },
        "source_consistency": {
            "p_acc_independence_schema": p_acc_independence.get("schema"),
            "p_acc_independence_closed": p_acc_independence.get("pa3_independence_closed"),
            "p_acc_independence_pa2_open": "PA2_velocity_collocation_to_acceleration_lift"
            in p_acc_independence.get("open_subproofs", []),
            "p_acc_row_binding_schema": p_acc_row_binding.get("schema"),
            "p_acc_row_binding_closed": p_acc_row_binding.get("pa4_row_binding_closed"),
            "p_state_gap_schema": p_state_gap.get("schema"),
            "p_state_closed": p_state_gap.get("primitive_closed"),
            "p_state_future_subproofs_closed": p_state_gap.get("summary", {}).get(
                "required_future_subproofs_closed"
            ),
            "kinematic_certificate_schema": kinematic_certificate.get("schema"),
            "certified_non_dynamic_rows": kinematic_certificate.get("proof_scope", {}).get(
                "certified_row_count"
            ),
            "dynamic_family_excluded": kinematic_certificate.get("proof_scope", {}).get(
                "excluded_row_family"
            ),
        },
        "manuscript_link": {
            "main_tex_present": all(contains_normalized(main_tex, token) for token in manuscript_tokens),
            "flat_tex_present": all(contains_normalized(flat_tex, token) for token in manuscript_tokens),
            "tokens": manuscript_tokens,
        },
        "claim_boundary": {
            "allowed_now": (
                "PA2 has a recorded obstruction: the velocity-collocation equations alone "
                "lose one power of h when solved for acceleration differences."
            ),
            "forbidden_now": [
                "P_acc primitive closure",
                "PA2 closure",
                "acceleration lift O(h^7) proved",
                "Taylor term bounds certified from P_acc",
                "primitive/Taylor PC2 route closure",
                "unconditional sixth-order theorem",
            ],
            "close_condition": (
                "Close PA2 by proving an unweighted O(h^7) acceleration lift from a "
                "non-dynamic inverse estimate, by proving O(h^8) velocity-stage and "
                "velocity-row perturbations before applying A_G^{-1}/h, or by carrying "
                "P_acc as an explicit regularity assumption in the theorem."
            ),
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# D5 P_acc PA2 Lift-Obstruction Audit",
        "",
        "Status: **PA2 obstruction recorded; P_acc lift remains open**.",
        "",
        "This read-only audit records a narrow anti-overclaim result. The",
        "velocity-collocation rows alone are insufficient to prove the",
        "unweighted `O(h^7)` acceleration lift required by the current D5",
        "Taylor budget.",
        "",
        "## Summary",
        "",
        f"- PA2 closed: `{result['pa2_closed']}`.",
        f"- P_acc primitive closed: `{result['primitive_closed']}`.",
        f"- Velocity-collocation alone sufficient for O(h^7) acceleration: `{result['velocity_collocation_alone_sufficient_for_O_h7_acceleration']}`.",
        f"- Current recorded inputs imply only: `{result['current_recorded_inputs_imply_only_unweighted_acceleration_rate']}`.",
        f"- Acceleration lift rate proved: `{result['acceleration_lift_rate_proved']}`.",
        f"- Taylor bounds proved: `{result['term_bounds_proved']}/36`.",
        f"- Primitive/Taylor PC2 route closed: `{result['pc2_closed']}`.",
        "",
        "## Rate Algebra",
        "",
        "For the translational and angular velocity-collocation rows, subtracting",
        "the lifted Gauss equation from the accepted stage equation gives",
        "",
        "`delta_V - h (A_G \\otimes I) delta_A = rho_V`.",
        "",
        "Since the three-stage Gauss matrix is invertible,",
        "",
        "`delta_A = h^{-1} (A_G^{-1} \\otimes I) (delta_V - rho_V)`.",
        "",
        f"The audited Gauss matrix has determinant `{det:.6e}` and",
        f"`||A_G^-1||_inf={norm_inf:.6e}`, so the inverse is uniformly bounded",
        "but the factor `1/h` is unavoidable. Thus `delta_V=O(h^7)` and",
        "`rho_V=O(h^7)` imply only `delta_A=O(h^6)` in the unweighted norm.",
        "",
        "## Correct PA2 Close Conditions",
        "",
        "- prove `delta_V=O(h^8)` and `rho_V=O(h^8)` before applying `A_G^{-1}/h`;",
        "- or prove an independent non-dynamic stage-map inverse that controls acceleration directly;",
        "- or keep `P_acceleration_lift=O(h^7)` as an explicit theorem assumption.",
        "",
        "## External TFE Scaling Context (Diagnostic Only)",
        "",
        "The source-paper TFE formulas provide diagnostic scaling context for",
        "derivative reconstruction through step-size-dependent operators.",
        "Its first-order example records inverse-step derivative scaling for",
        "`delta v` and `delta vdot`, and its higher-order relations reconstruct",
        "`y` and `z` through derivative coefficient matrices. This supports the",
        "PA2 obstruction rather than closing it: those formulas do not prove the",
        "unweighted `delta A=O(h^7)` estimate required by the separate",
        "primitive/Taylor acceleration-lift rows.",
        "",
        "## Runtime Row-Scaling Evidence",
        "",
        "The accepted `run_v047.py` residual has the same scaling obstruction.",
        "The velocity-collocation rows contain acceleration through `h A_G`,",
        "while the Newton-Euler rows use `m_b a` and `J_b alpha` without an",
        "extra factor of `h`. The lower-pair acceleration constraints are",
        "non-dynamic and unweighted, but they only constrain lower-pair",
        "constraint directions and do not form a full unweighted inverse for",
        "all body acceleration components required by the 36 Newton-Euler",
        "Taylor terms.",
        "",
        "## Acceptance Boundary",
        "",
        "- This audit sharpens PA2; it does not close PA2.",
        "- `P_acc` remains open.",
        "- Zero P_acc-induced Taylor bounds are certified.",
        "- Primitive/Taylor PC2 lane remains open.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("d5_p_acc_lift_obstruction_audit=written")
    print("pa2_closed=False")
    print("velocity_collocation_alone_sufficient=False")
    print("current_unweighted_acceleration_rate=O(h^6)")
    print("pc2_closed=False")


if __name__ == "__main__":
    main()
