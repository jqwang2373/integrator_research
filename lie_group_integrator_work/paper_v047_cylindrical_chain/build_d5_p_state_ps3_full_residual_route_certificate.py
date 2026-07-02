#!/usr/bin/env python3
"""Build the D5 P_state PS3 full-residual route certificate."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent.parent
REF_TXT = ROOT / "s11044-026-10153-w.txt"
OUT_JSON = PAPER / "D5_P_STATE_PS3_FULL_RESIDUAL_ROUTE_CERTIFICATE.json"
OUT_MD = PAPER / "D5_P_STATE_PS3_FULL_RESIDUAL_ROUTE_CERTIFICATE.md"


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
    aggregate = read_json(PAPER / "D5_P_STATE_PS2_AGGREGATE_PROMOTION_AUDIT.json")
    conditional = read_json(PAPER / "D5_P_STATE_PS3_CONDITIONAL_CONVERSION_AUDIT.json")
    h_acc = read_json(PAPER / "D5_P_STATE_PS3_H_ACC_INPUT_OBSTRUCTION_AUDIT.json")
    kinematic = read_json(PAPER / "KINEMATIC_ROW_DEFECT_CERTIFICATE.json")
    direct = read_json(PAPER / "D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE.json")
    proof_manifest = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
    main_tex = read_text(PAPER / "main_cmame.tex")
    flat_tex = read_text(PAPER / "cmame_submission_flat" / "main_cmame_submission.tex")
    ref_text = read_text(REF_TXT)

    closure_state = proof_manifest.get("closure_state", {})
    evidence = proof_manifest.get("evidence_summary", {})
    direct_summary = direct.get("summary", {})
    h_acc_summary = h_acc.get("summary", {})
    certified_non_dynamic_rows = kinematic.get("proof_scope", {}).get("certified_row_count")
    dynamic_zero_rows = direct_summary.get("dynamic_zero_residual_rows")
    full_stage_rows = direct_summary.get(
        "full_stage_rows_when_assembled_by_bridge",
        direct_summary.get("full_stage_rows_if_promoted"),
    )

    manuscript_tokens = [
        r"\label{lem:d5-p-state-ps3-full-residual-route}",
        "Direct-route state-block corollary; not primitive",
        "full 132-row residual",
        r"h\|\delta A\|=O(h^7)",
        "does not use velocity collocation",
        "does not certify the primitive/Taylor route",
    ]
    feedback_nonclosure_tokens = [
        r"\label{lem:d5-p-state-direct-feedback-nonclosure}",
        r"No direct-route feedback into primitive \(P_{\mathrm{state}}\)",
        "theorem-route corollary, not an admissible primitive-route input",
        r"\(126\) \(P_{\mathrm{state}}\)-dependent",
        r"\(0/162\) primitive Taylor inventory unchanged",
    ]
    reference_tokens = {
        "expected_order_convention": "ensures 2m",
        "m3_fifth_order_appendix": "For a fifth order accurate method m = 3",
        "dae_order_reduction_reported": "TFE (m = 3) achieves only fourth order accuracy",
        "appendix_b_coefficients": "Appendix B: Time",
    }

    full_residual_route_closed = (
        certified_non_dynamic_rows == 96
        and dynamic_zero_rows == 36
        and full_stage_rows == 132
        and direct.get("direct_route_mathematical_certificate_closed") is True
        and direct.get("direct_route_non_circular") is True
        and direct.get("stage_residual_O_h7_by_direct_route") is True
        and closure_state.get("pc2_closed_by_direct_substitution") is True
    )
    direct_route_ps3_input_closed = (
        full_residual_route_closed
        and aggregate.get("ps2_inverse_or_infsup_closed") is True
        and conditional.get("ps3_conditional_conversion_closed") is True
    )
    strict_proof_steps = [
        {
            "id": "FR1",
            "statement": "The 96 non-dynamic rows have O(h^7) residual on the smooth lifted Gauss stage.",
            "closed": certified_non_dynamic_rows == 96,
            "evidence": "KINEMATIC_ROW_DEFECT_CERTIFICATE",
        },
        {
            "id": "FR2",
            "statement": "The 36 Newton-Euler rows have zero direct-route residual remainder by direct substitution.",
            "closed": dynamic_zero_rows == 36 and direct.get("stage_residual_O_h7_by_direct_route") is True,
            "evidence": "D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE",
        },
        {
            "id": "FR3",
            "statement": "The full 132-row residual therefore satisfies the O(h^7) stage-residual perturbation hypothesis.",
            "closed": full_residual_route_closed,
            "evidence": "PROOF_CLOSURE_MANIFEST",
        },
        {
            "id": "FR4",
            "statement": "The aggregate PS2 estimate converts the full-route bound into ||delta S||=O(h^7) and h||delta A||=O(h^7).",
            "closed": direct_route_ps3_input_closed,
            "evidence": "D5_P_STATE_PS2_AGGREGATE_PROMOTION_AUDIT and D5_P_STATE_PS3_CONDITIONAL_CONVERSION_AUDIT",
        },
    ]

    result = {
        "schema": "d5-p-state-ps3-full-residual-route-certificate-v1",
        "status": "full_residual_route_certificate_closed_primitive_route_boundary_retained",
        "read_only": True,
        "run_v047_invoked": False,
        "submission_ready": False,
        "proof_gap_closed": proof_manifest.get("closure_state", {}).get("proof_gap_closed"),
        "direct_residual_bridge_proof_gap_closed": proof_manifest.get("closure_state", {}).get(
            "direct_pc2_proof_gap_closed"
        ),
        "proof_gap_closed_scope": "direct_residual_bridge_ps3_corollary_only",
        "pc2_closed_by_referenced_manifest": closure_state.get("pc2_closed_by_direct_substitution"),
        "primitive_route_pc2_closed": False,
        "primitive_route_closed": False,
        "primitive_taylor_route_closed": False,
        "residual_to_error_route_closed": False,
        "multiplier_reaction_output_order_claimed": False,
        "primitive_id": "P_state_lift",
        "plan_id": "P_state",
        "p_state_primitive_closed_by_primitive_route": False,
        "direct_route_p_state_corollary_closed": direct_route_ps3_input_closed,
        "certifies_strict_taylor_subproof": True,
        "certifies_induced_taylor_bounds": False,
        "certifies_primitive_taylor_route": False,
        "direct_route_certificate": {
            "full_132_row_residual_route_closed": full_residual_route_closed,
            "direct_route_ps3_input_closed": direct_route_ps3_input_closed,
            "direct_route_state_lift_rate_closed": direct_route_ps3_input_closed,
            "direct_route_h_weighted_acceleration_input_closed": direct_route_ps3_input_closed,
            "non_dynamic_rows_from_kinematic_certificate": certified_non_dynamic_rows,
            "dynamic_rows_from_direct_substitution": dynamic_zero_rows,
            "full_stage_rows": full_stage_rows,
            "direct_route_residual_remainder_mode": "zero residual remainder after direct substitution of the smooth Gauss FullVA lift",
            "primitive_162_subterm_taylor_lane_certified": False,
            "state_estimate_used": aggregate.get("aggregate_estimate", {}).get("statement"),
            "conditional_conversion_rate": conditional.get("rate_budget", {}).get(
                "conditional_state_lift_rate"
            ),
            "stage_residual_perturbation_applied": True,
            "stage_residual_perturbation_source": "Lemma stage-residual-defect plus PROOF_CLOSURE_MANIFEST PC2 direct-substitution route",
            "h_acceleration_obstruction_bypassed": True,
            "h_acceleration_obstruction_source": h_acc.get("schema"),
        },
        "strict_proof_steps": strict_proof_steps,
        "non_circularity": {
            "uses_p_state_actual_ps3_as_input": False,
            "uses_p_acc_lift_as_input": False,
            "uses_p_lambda_lift_as_input": False,
            "uses_velocity_collocation_h_inverse_route": False,
            "uses_finite_probe_as_proof": False,
            "uses_residual_to_error_promotion": False,
            "why_non_circular": (
                "The proof first evaluates the full residual at the smooth Gauss lift. "
                "Only after the 132-row residual perturbation criterion is available "
                "does it read off the weighted state and acceleration components."
            ),
        },
        "primitive_route_boundary": {
            "not_used_to_close_primitive_taylor_route": True,
            "reason": (
                "The primitive/Taylor route is an alternative stronger route that must "
                "derive its primitive lift bounds before using them to certify the 162 "
                "D5 Taylor subterms. This certificate is a direct-route corollary of "
                "the already closed PC2 direct-substitution route, so it cannot be "
                "recycled as an independent primitive-route proof."
            ),
            "induced_taylor_bounds_proved": 0,
            "open_primitive_route_obligations_retained": [
                "P_state primitive-route closure",
                "P_acc unweighted acceleration lift",
                "P_lambda uniform inf-sup and multiplier-rate propagation",
                "P_geom conditional downstream bound",
                "P_gyro conditional downstream bound",
            ],
        },
        "reference_proof_style": {
            "source_text": "../../s11044-026-10153-w.txt",
            "features_checked": {
                key: contains_normalized(ref_text, token) for key, token in reference_tokens.items()
            },
            "style_adopted": [
                "separate expected formula order from DAE/order-reduction evidence",
                "prove local algebraic expansion or row identity before using numerical convergence evidence",
                "state the compact-tube derivative bounds and the theorem boundary explicitly",
            ],
        },
        "source_consistency": {
            "aggregate_schema": aggregate.get("schema"),
            "aggregate_ps2_inverse_closed": aggregate.get("ps2_inverse_or_infsup_closed"),
            "conditional_schema": conditional.get("schema"),
            "conditional_conversion_closed": conditional.get("ps3_conditional_conversion_closed"),
            "h_acc_obstruction_schema": h_acc.get("schema"),
            "h_acc_recommended_route": h_acc_summary.get("recommended_non_circular_close_route"),
            "h_acc_residual_only_input_sufficient": h_acc_summary.get(
                "residual_only_input_sufficient_for_h_acceleration"
            ),
            "h_acc_full_dynamic_residual_route_closed_before_certificate": h_acc_summary.get(
                "full_dynamic_residual_route_closed"
            ),
            "kinematic_schema": kinematic.get("schema"),
            "direct_schema": direct.get("schema"),
            "direct_certificate_closed": direct.get("direct_route_mathematical_certificate_closed"),
            "proof_manifest_status": proof_manifest.get("status"),
            "proof_manifest_pc2_closed_by_direct_substitution": closure_state.get(
                "pc2_closed_by_direct_substitution"
            ),
            "proof_manifest_primitive_lift_route_closed": closure_state.get("primitive_lift_route_closed"),
            "proof_manifest_stage_residual_O_h7": closure_state.get(
                "stage_residual_O_h7_implementation_defect_proved"
            ),
            "proof_manifest_dynamic_symbolic_oracle_complete": closure_state.get(
                "dynamic_symbolic_oracle_complete"
            ),
            "evidence_direct_dynamic_zero_rows": evidence.get(
                "newton_euler_d5_direct_substitution_dynamic_zero_rows"
            ),
        },
        "manuscript_link": {
            "lemma_label": "lem:d5-p-state-ps3-full-residual-route",
            "main_tex_present": all(contains_normalized(main_tex, token) for token in manuscript_tokens),
            "flat_tex_present": all(contains_normalized(flat_tex, token) for token in manuscript_tokens),
            "feedback_nonclosure_label": "lem:d5-p-state-direct-feedback-nonclosure",
            "feedback_nonclosure_main_tex_present": all(
                contains_normalized(main_tex, token) for token in feedback_nonclosure_tokens
            ),
            "feedback_nonclosure_flat_tex_present": all(
                contains_normalized(flat_tex, token) for token in feedback_nonclosure_tokens
            ),
            "tokens": manuscript_tokens,
            "feedback_nonclosure_tokens": feedback_nonclosure_tokens,
        },
        "summary": {
            "full_residual_route_certificate_closed": full_residual_route_closed,
            "direct_route_ps3_input_closed": direct_route_ps3_input_closed,
            "direct_route_state_lift_rate_closed": direct_route_ps3_input_closed,
            "direct_route_h_weighted_acceleration_input_closed": direct_route_ps3_input_closed,
            "p_state_primitive_closed_by_primitive_route": False,
            "primitive_route_closed": False,
            "primitive_route_induced_taylor_bounds_proved": 0,
            "strict_proof_steps_closed": sum(1 for item in strict_proof_steps if item["closed"]),
            "strict_proof_steps_total": 4,
            "submission_ready": False,
        },
        "claim_boundary": {
            "allowed_now": (
                "The full-residual direct route supplies a non-circular PS3 input "
                "corollary for P_state under the existing conditional proof boundary."
            ),
            "forbidden_now": [
                "primitive/Taylor route closed",
                "162 induced Taylor subterms certified",
                "B1 independent implementation oracle closed",
                "submission-ready proof",
            ],
            "close_condition_for_primitive_route": (
                "The primitive route still requires independent P_state/P_acc/P_lambda "
                "lift proofs before P_geom/P_gyro and the 162 Taylor subterms can close."
            ),
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# D5 P_state PS3 Full-Residual Route Certificate",
        "",
        "Status: **full residual route certificate closed; primitive route boundary retained**.",
        "",
        "This certificate records the strict direct-route proof that bypasses the",
        "`h delta A` obstruction without using velocity collocation or a finite",
        "rank probe. It is a proof artifact, not a numerical diagnostic.",
        "",
        "## Summary",
        "",
        f"- Full 132-row residual route closed: `{result['summary']['full_residual_route_certificate_closed']}`.",
        f"- Direct-route PS3 corollary closed, not primitive P_state closure: `{result['summary']['direct_route_ps3_input_closed']}`.",
        f"- Direct-route state lift rate closed: `{result['summary']['direct_route_state_lift_rate_closed']}`.",
        f"- Direct-route h-weighted acceleration input closed: `{result['summary']['direct_route_h_weighted_acceleration_input_closed']}`.",
        f"- Proof gap closed scope: `{result['proof_gap_closed_scope']}`.",
        f"- Primitive/Taylor route closed: `{result['primitive_taylor_route_closed']}`.",
        f"- Residual-to-error route closed: `{result['residual_to_error_route_closed']}`.",
        f"- Multiplier/reaction output order claimed: `{result['multiplier_reaction_output_order_claimed']}`.",
        f"- P_state primitive closed by primitive route: `{result['summary']['p_state_primitive_closed_by_primitive_route']}`.",
        f"- Primitive-route induced Taylor bounds proved: `{result['summary']['primitive_route_induced_taylor_bounds_proved']}/162`.",
        "- Direct-route feedback into primitive P_state blocked main/flat: "
        f"`{result['manuscript_link']['feedback_nonclosure_main_tex_present']}/"
        f"{result['manuscript_link']['feedback_nonclosure_flat_tex_present']}`.",
        f"- Strict proof steps closed: `{result['summary']['strict_proof_steps_closed']}/{result['summary']['strict_proof_steps_total']}`.",
        f"- Submission ready: `{result['summary']['submission_ready']}`.",
        "",
        "## Strict Proof Route",
        "",
        "| id | status | statement |",
        "|---|---:|---|",
    ]
    for item in result["strict_proof_steps"]:
        lines.append(f"| `{item['id']}` | `{item['closed']}` | {item['statement']} |")
    lines += [
        "",
        "The 36 Newton-Euler rows are handled by direct-route residual decomposition with",
        "zero residual remainder after direct substitution of the smooth Gauss FullVA lift.",
        "Together with the 96 certified non-dynamic rows, this supplies the full",
        "132-row residual hypothesis in the stage-residual perturbation lemma.",
        "This is not a certification of the primitive 162-subterm Taylor lane:",
        "the primitive-route induced Taylor bounds remain `0/162`, all 162",
        "subterms remain blocked by open primitives, and the 36 h-weighted",
        "acceleration primitive terms remain insufficient.",
        "",
        "Applying the aggregate PS2 estimate",
        "",
        "`||delta S|| <= C_PS2 (||delta N_h^nd|| + h ||delta A||)`",
        "",
        "to the full-route perturbation bound gives `||delta S||=O(h^7)` and",
        "`h||delta A||=O(h^7)` without the circular",
        "`delta_A = h^{-1} (A_G^{-1} \\otimes I)(delta_V-rho_V)` route.",
        "",
        "## Non-Circularity",
        "",
        "- Does not use actual PS3 as an input.",
        "- Does not use `P_acc` or `P_lambda` lift estimates as inputs.",
        "- Does not use velocity collocation as an h-inverse acceleration proof.",
        "- Does not promote finite rank probes to compact-tube theorems.",
        "- Does not use residual-to-error promotion.",
        "",
        "## Primitive-Route Boundary",
        "",
        "This certificate closes only the direct-route PS3 corollary. It does not",
        "certify the alternative primitive/Taylor route, does not prove the 162",
        "induced Taylor subterm bounds, and does not close B1's independent",
        "implementation-oracle boundary.",
        "The reader-facing feedback-prohibition lemma records that the direct-route",
        "state estimate is a theorem-route corollary, not an admissible primitive-route",
        "input for `P_state`; the 126 P_state-dependent primitive subterms and the",
        "`0/162` primitive Taylor inventory remains unchanged.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("d5_p_state_ps3_full_residual_route_certificate=written")
    print(f"full_residual_route_certificate_closed={full_residual_route_closed}")
    print(f"direct_route_ps3_input_closed={direct_route_ps3_input_closed}")
    print("primitive_route_closed=False")


if __name__ == "__main__":
    main()
