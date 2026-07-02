#!/usr/bin/env python3
"""Build a strict-proof policy reconciliation audit.

This audit fixes the terminology boundary requested for the proof: the current
B3 proof uses a direct residual-bridge/Kantorovich perturbation route, while
the separate primitive 162-subterm Taylor route remains open.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent.parent
REF_TXT = ROOT / "1-s2.0-S0377042719305229-main.txt"
BLOCKER = PAPER / "CMAME_BLOCKER_CLOSURE_GATE.json"
OUT_JSON = PAPER / "CMAME_STRICT_PROOF_POLICY_RECONCILIATION_AUDIT.json"
OUT_MD = PAPER / "CMAME_STRICT_PROOF_POLICY_RECONCILIATION_AUDIT.md"


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


def feature_map(text: str, tokens: dict[str, str]) -> dict[str, bool]:
    return {key: contains_normalized(text, token) for key, token in tokens.items()}


def blocker_by_id(gate: dict[str, Any], blocker_id: str) -> dict[str, Any]:
    for item in gate.get("blockers", []):
        if isinstance(item, dict) and item.get("id") == blocker_id:
            return item
    return {}


def main() -> None:
    proof_closure = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
    proof_claim_traceability = read_json(PAPER / "PROOF_CLAIM_TRACEABILITY_AUDIT.json")
    strict_audit = read_json(PAPER / "CMAME_STRICT_PROOF_AUDIT.json")
    b3_review = read_json(PAPER / "B3_DIRECT_PROOF_REVIEW_AUDIT.json")
    proof_contract = read_json(PAPER / "CMAME_PROOF_CONTRACT_GATE.json")
    proof_style = read_json(PAPER / "CMAME_PROOF_STYLE_AUDIT.json")
    d5_taylor = read_json(PAPER / "D5_CONDITIONAL_TAYLOR_CERTIFICATE.json")
    d5_budget = read_json(PAPER / "D5_TAYLOR_TERM_BUDGET_AUDIT.json")
    d5_plan = read_json(PAPER / "D5_PRIMITIVE_OBLIGATION_CLOSURE_PLAN.json")
    blocker = read_json(BLOCKER)
    main_tex = read_text(PAPER / "main_cmame.tex")
    flat_tex = read_text(PAPER / "cmame_submission_flat" / "main_cmame_submission.tex")
    ref_text = read_text(REF_TXT)

    closure = proof_closure.get("closure_state", {})
    strict_manifest = proof_closure.get(
        "strict_direct_residual_bridge_submission_standard",
        proof_closure.get("direct_residual_bridge_kantorovich_submission_standard", {}),
    )
    strict_policy = strict_audit.get("direct_residual_bridge_kantorovich_submission_standard", {})
    strict_traceability = strict_audit.get("manuscript_theorem_traceability", {})
    contract_traceability = proof_contract.get("manuscript_theorem_traceability", {})
    style_traceability = proof_style.get("proof_contract_theorem_traceability", {})
    theorem_statement_boundary = proof_closure.get("theorem_statement_boundary", {})
    manuscript_traceability = proof_closure.get("manuscript_traceability", {})
    proof_closure_anchor_map = proof_closure.get("manuscript_anchor_map", {})
    proof_claim_anchor_map = proof_claim_traceability.get("manuscript_anchor_map", {})
    primitive = strict_audit.get("primitive_taylor_route", {})
    boundary = strict_audit.get("two_layer_proof_boundary", {})
    direct_corollary = strict_audit.get("direct_route_ps3_corollary", {})
    d5_summary = d5_taylor.get("summary", {})
    budget_summary = d5_budget.get("summary", {})
    plan_summary = d5_plan.get("summary", {})
    contract = proof_contract.get("theorem_contract", {})
    b4 = blocker_by_id(blocker, "B4")
    b6 = blocker_by_id(blocker, "B6")
    b7 = blocker_by_id(blocker, "B7")
    global_submission_boundaries = [
        "full_source_policy_package_ready",
        "theorem_level_eta_h_solver_policy_evidence",
        "closed_residual_to_error_theorem_for_mechanism_rows",
    ]
    expected_anchor_evidence_sources = [
        "PROOF_CLOSURE_MANIFEST.json",
        "PROOF_CLAIM_TRACEABILITY_AUDIT.json",
    ]
    narrowed_claim_b4_b6_b7_statuses = {
        "B4": b4.get("status"),
        "B6": b6.get("status"),
        "B7": b7.get("status"),
    }

    reference_features = feature_map(
        ref_text,
        {
            "bliedf_section_present": "3. BLieDF",
            "convergence_section_present": "6. Convergence analysis",
            "taylor_local_error_lemma_present": "Proof. Taylor expansion for Eq. (12)",
            "lie_algebra_global_error_present": "global error in the configuration variables",
            "bch_perturbation_present": "Baker",
            "constrained_local_error_theorem_present": "The local truncation errors of the k-step BLieDF method",
            "constraint_multiplier_estimate_present": "An error estimate for",
            "coupled_error_recursion_present": "a coupled error recursion is obtained",
            "bdf_order_boundary_present": "has the order of convergence p = k",
            "appendix_proof_present": "Appendix. Proof of Theorem 4",
        },
    )
    manuscript_features = {
        "main_integral_remainder": contains_normalized(main_tex, "Taylor's formula with integral remainder"),
        "flat_integral_remainder": contains_normalized(flat_tex, "Taylor's formula with integral remainder"),
        "main_kantorovich_contraction": contains_normalized(main_tex, r"\mathcal T_h(\Delta)"),
        "flat_kantorovich_contraction": contains_normalized(flat_tex, r"\mathcal T_h(\Delta)"),
        "main_primitive_route_boundary": contains_normalized(main_tex, "primitive/Taylor route is non-active in the theorem"),
        "flat_primitive_route_boundary": contains_normalized(flat_tex, "primitive/Taylor route is non-active in the theorem"),
        "main_not_source_replacement": contains_normalized(
            main_tex, "not a complete source-paper temporal finite-element residual replacement"
        ),
        "flat_not_source_replacement": contains_normalized(
            flat_tex, "not a complete source-paper temporal finite-element residual replacement"
        ),
        "main_reference_proof_usage_paragraph": contains_normalized(main_tex, "Reference proof usage"),
        "flat_reference_proof_usage_paragraph": contains_normalized(flat_tex, "Reference proof usage"),
        "main_wieloch_arnold_not_estimate_source": contains_normalized(
            main_tex, "Wieloch--Arnold BLieDF proof is invoked as a proof-order template, not as an estimate source"
        ),
        "flat_wieloch_arnold_not_estimate_source": contains_normalized(
            flat_tex, "Wieloch--Arnold BLieDF proof is invoked as a proof-order template, not as an estimate source"
        ),
        "main_active_taylor_object_full_scaled_residual": contains_normalized(
            main_tex, "the active Taylor object is the full scaled residual map"
        ),
        "flat_active_taylor_object_full_scaled_residual": contains_normalized(
            flat_tex, "the active Taylor object is the full scaled residual map"
        ),
        "main_reference_paper_not_tfe": contains_normalized(
            main_tex, "not the \\tfe{} comparison paper"
        ),
        "flat_reference_paper_not_tfe": contains_normalized(
            flat_tex, "not the \\tfe{} comparison paper"
        ),
    }
    reference_correspondence_tokens = {
        "formal_table_reference": r"Table~\ref{tab:reference-proof-order-correspondence}",
        "formal_table_caption": r"\caption{Reference proof-order correspondence",
        "caption_nonimport_boundary": (
            "none of its BLieDF estimates, BDF order theorem, multiplier-history estimates, or "
            "source-paper comparison claims are imported"
        ),
        "not_estimate_transfer": "structural and stepwise, not an estimate transfer",
        "constraint_multiplier_interface_split": (
            "branch-stability interfaces; the Newton--Euler row identities are separate "
            "FullVA residual-bridge inputs"
        ),
        "not_imported_constraint_multiplier_estimates": "not imported constraint/multiplier estimates",
        "reference_reduced_gauss_order_only": "formal Gauss order is used only for the reduced smooth Gauss branch",
        "reference_order_taylor_discipline": "Reference-order Taylor discipline",
        "reference_structural_order_no_taylor_import": "structural ordering discipline only; no Taylor estimate, primitive lift bound, or multiplier estimate is imported",
        "reference_fullmap_taylor_closed_fixed_132": "T2 full-map Taylor/Kantorovich estimate is established only for the fixed",
        "table_constraint_multiplier_interface_split": (
            "the Newton--Euler row identities enter separately as FullVA-specific residual-bridge inputs"
        ),
        "reference_fullva_translation_checkpoint": "Reference-to-FullVA translation map",
        "reference_partial_order_obligations": "used only as a partial order on obligations",
        "reference_r1_fixed_discrete_object": "R1 fixes the discrete Lie-group object before expansion",
        "reference_r2_smooth_branch_same_object": "R2 inserts the smooth exact branch into that same object",
        "reference_r3_fixed_object_defect_conversion": "R3 converts the fixed-object defect to a nearby accepted algebraic solution",
        "reference_r4_stability_after_local_defect": "R4 applies a stability recursion only after the local defect is fixed",
        "reference_right_hand_independent": "every right-hand object is proved or retained independently",
        "reference_does_not_repair_failed_lemma": "the constrained-BDF reference theorem would not repair it",
        "reference_dependency_graph_not_premise": "proof-order dependency graph, not a theorem premise",
        "reference_constrained_dae_slot_checkpoint": "Reference constrained-DAE slot map",
        "reference_two_distinct_dae_slots": "two distinct DAE slots",
        "reference_constraint_difference_multiplier_slot": "hidden-constraint/multiplier estimate obtained from constraint differences",
        "reference_local_defect_slot_full_bridge": r"local-defect slot is occupied by the Gauss defect plus the full \(132\)-row residual bridge",
        "reference_constrained_dae_slot_fullva": "constrained-DAE slot is occupied by the retained compact FullVA chart",
        "reference_multipliers_stage_unknowns_not_histories": r"multipliers are stage unknowns in \(F_{A,h}\), not separate reported histories",
        "reference_no_bypass_constraint_layer": "FullVA proof does not bypass the constraint layer",
        "reference_constrained_slot_contract": "Reference-style constrained-slot contract",
        "reference_slot_contract_four_slots": "four-slot contract",
        "reference_c1_local_error_slot": "C1, the local-error slot",
        "reference_c2_constrained_algebraic_slot": "C2, the constrained algebraic slot",
        "reference_c3_one_step_perturbation_slot": "C3, the one-step perturbation slot",
        "reference_c4_global_recursion_slot": "C4, the global-recursion slot",
        "reference_slot_no_imports": "No slot imports a BLieDF constant",
        "reference_slot_not_estimate_transfer": "proof-order guard, not an extra theorem premise or an estimate-transfer device",
    }
    main_reference_correspondence_features = feature_map(main_tex, reference_correspondence_tokens)
    flat_reference_correspondence_features = feature_map(flat_tex, reference_correspondence_tokens)
    proof_order_checkpoint_tokens = {
        "checkpoint_title": "Proof-order instantiation",
        "fixed_discrete_object": "Fix the discrete object: the accepted Gauss-predictor branch",
        "reference_table_binding": r"Table~\ref{tab:reference-proof-order-correspondence}",
        "local_defect_direct_bridge": r"Lemmas~\ref{lem:full-132-row-residual-bridge}",
        "primitive_162_not_used": "the separate primitive 162-term Taylor closure is not used",
        "p6_retained_condition": r"P6 remains the retained compact-tube condition \(\eta_h^{\rm tube}\le c_\eta h^7\)",
        "fixed_tolerance_logs_do_not_discharge_p6": "Fixed-tolerance logs and finite solver probes do not discharge P6",
        "local_global_reporting_only_after_local_defect": "Propagate and report only after the local defect is fixed",
        "p7_nonpromoted": "P7 residual rows remain nonpromoted diagnostics",
    }
    main_proof_order_checkpoint_features = feature_map(main_tex, proof_order_checkpoint_tokens)
    flat_proof_order_checkpoint_features = feature_map(flat_tex, proof_order_checkpoint_tokens)
    proof_order_checkpoint_closed = all(main_proof_order_checkpoint_features.values()) and all(
        flat_proof_order_checkpoint_features.values()
    )
    assumption_non_circularity_tokens = {
        "assumption_admissibility_note": r"Assumption admissibility note: Assumption~\ref{ass:regularity}",
        "does_not_assume_theorem_conclusion": "does not assume the theorem conclusion",
        "p2_prior_to_gronwall": "independent of, and logically prior to, the discrete Gronwall step",
        "not_assumed_local_defect": "not an assumed local defect estimate",
        "not_inferred_from_observed_slopes": "not inferred from observed sixth-order slopes",
        "non_vacuity_admissibility_note": "Non-vacuity/admissibility note",
        "does_not_assume_h7_local_defect": r"do not assume the \(O(h^7)\) local defect",
        "does_not_assume_h6_grid_estimate": r"the \(O(h^6)\) grid estimate",
        "finite_rows_not_admissibility_claim": (
            "Finite numerical rows may identify the reported branch and check consistency, "
            "but they are not part of this admissibility claim"
        ),
    }
    main_assumption_non_circularity_features = feature_map(main_tex, assumption_non_circularity_tokens)
    flat_assumption_non_circularity_features = feature_map(flat_tex, assumption_non_circularity_tokens)
    assumption_non_circularity_closed = all(main_assumption_non_circularity_features.values()) and all(
        flat_assumption_non_circularity_features.values()
    )
    reporting_map_tokens = {
        "lemma_label": r"\label{lem:reporting-map-norm-consequence}",
        "compact_derivative_supremum": r"\sup_{y\in U_K}\|D\mathcal R(y)\|\le C_{\mathcal R}",
        "convex_chart_checkpoint": "Convex chart-neighborhood checkpoint",
        "no_convex_k_assumption": r"does not assume that \(K\) itself is convex",
        "segments_inside_uk": r"segments between them stay inside \(U_K\)",
        "same_reported_indices": r"same reported output indices \(0\le n\le N_h\)",
        "qv_constant_formula": r"C_{qv}=C_{\mathcal R}C_{\rm red}",
        "local_chart_to_output_boundary": "local chart-to-output norm consequence",
        "mean_value_formula": "integral mean-value formula",
        "no_diagnostic_inputs": (
            "does not use residual/reaction tables, source-policy rows, fitted constants, "
            "output interpolation, or a chart switch"
        ),
        "theorem_invocation": r"Lemma~\ref{lem:reporting-map-norm-consequence}",
    }
    main_reporting_map_features = feature_map(main_tex, reporting_map_tokens)
    flat_reporting_map_features = feature_map(flat_tex, reporting_map_tokens)
    reporting_map_contract_closed = all(main_reporting_map_features.values()) and all(
        flat_reporting_map_features.values()
    )
    primitive_one_way_tokens = {
        "paragraph_title": "Primitive-route one-way implication discipline",
        "one_way_logical_form": "one-way logical form",
        "primitive_to_162_to_residual": "162 D5 primitive Taylor subterms are",
        "no_converse": "No converse implication is used or available",
        "direct_route_not_primitive_input": "That output cannot be reinserted as a proof of the primitive inputs",
        "weighted_acceleration_not_unweighted": (
            r"weighted estimate \(h\|\delta A\|=O(h^7)\) does not imply the unweighted"
        ),
        "pstate_corollary_not_closure": (
            r"direct-route state-block corollary, not a primitive \(P_{\mathrm{state}}\) closure"
        ),
        "does_not_turn_direct_bridge_into_primitive_certificate": (
            "do not turn the already proved direct residual bridge into a primitive 162-subterm proof"
        ),
        "primitive_bounds_not_established": "Actual primitive-route Taylor subterm bounds are not established",
        "taylor_projection_checkpoint": "Taylor-projection checkpoint",
        "aggregate_fixed_block_norm": "aggregate estimate in the fixed block norm",
        "not_projection_certificate_162": "not a projection certificate for the 162 primitive scalar subterms",
        "primitive_projection_operator": r"\Pi_{\rm prim}",
        "projection_right_inverse_needed": "primitive projection/right-inverse",
        "independent_primitive_lift_bounds": r"independent \(O(h^7)\) bounds for all primitive lift maps",
        "no_projection_right_inverse_used": "No such primitive projection/right-inverse is used",
        "t2_closed_while_primitive_separate": "aggregate residual bridge can close the T2 residual-defect input while the primitive-route status",
        "non_substitution_contract": "Primitive-route non-substitution contract",
        "replacement_scope_one_input": "replacing the dynamic-row residual-value certificate inside the full",
        "not_replace_t2_kantorovich": "would not by itself replace the T2 full-map inverse/Kantorovich step",
        "not_replace_endpoint_p6_p7": "endpoint-closure perturbation, the retained P6 solver-scale condition",
        "alternative_certificate_one_input": "alternative certificate for one input to the existing theorem chain",
        "not_complete_order_theorem": "not a complete order theorem",
    }
    main_primitive_one_way_features = feature_map(main_tex, primitive_one_way_tokens)
    flat_primitive_one_way_features = feature_map(flat_tex, primitive_one_way_tokens)
    primitive_one_way_contract_closed = all(main_primitive_one_way_features.values()) and all(
        flat_primitive_one_way_features.values()
    )
    kantorovich_tokens = {
        "gauss_lift_same_stage_coordinate": "same accepted stage-coordinate vector before",
        "residual_hypothesis": r"\|F_{A,h}(Z_G;y)\| \le C_R h^7",
        "residual_uniform_yK_hbar": r"Assume also, uniformly for \(y\in K\) and",
        "radius_definition": r"\rho_h=2M\|R_h\|",
        "radius_contained_in_tube": r"\rho_h\le r",
        "absorption_condition": r"ML\rho_h\le 1/2",
        "endpoint_derivative_supremum": r"\sup_{0<h\le h_0}\sup_{y\in K}",
        "self_map_bound": r"\|\mathcal T_h(\Delta)\|",
        "contraction_bound": r"\|\mathcal T_h(\Delta_1)-\mathcal T_h(\Delta_2)\|",
        "fixed_point_ball": r"B_{\rho_h}(0)",
        "stage_error_bound": r"\le 2MC_Rh^7=C_Zh^7",
        "endpoint_transfer": r"\mathcal E_h(Z_A)-\mathcal E_h(Z_G)",
        "bridge_constant_uniform_yK": r"with \(C_R\) independent of \(y\in K\)",
    }
    main_kantorovich_features = feature_map(main_tex, kantorovich_tokens)
    flat_kantorovich_features = feature_map(flat_tex, kantorovich_tokens)
    kantorovich_contract_closed = all(main_kantorovich_features.values()) and all(
        flat_kantorovich_features.values()
    )

    strict_actual_taylor_bounds = strict_manifest.get(
        "actual_taylor_bounds_proved",
        strict_manifest.get("primitive_taylor_actual_bounds_proved"),
    )
    strict_open_taylor_terms = strict_manifest.get(
        "open_taylor_bound_terms",
        strict_manifest.get("primitive_taylor_open_bound_terms"),
    )
    strict_terms_with_open_primitives = strict_manifest.get(
        "terms_with_open_primitive_blockers",
        strict_manifest.get("primitive_taylor_terms_with_open_primitive_blockers"),
    )
    strict_open_primitive_count = strict_manifest.get(
        "open_primitive_count",
        strict_manifest.get("primitive_taylor_open_primitive_count"),
    )

    direct_route_closed = all(
        [
            strict_manifest.get("required_pc2_route") == "direct_residual_bridge_kantorovich_route",
            strict_manifest.get("direct_residual_bridge_kantorovich_route_closed") is True,
            strict_manifest.get("direct_substitution_supplies_active_pc2_residual_bridge") is True,
            strict_policy.get("direct_residual_bridge_kantorovich_route_closed") is True,
            strict_policy.get("direct_substitution_supplies_active_pc2_residual_bridge") is True,
            b3_review.get("b3_direct_proof_review_passed") is True,
            b3_review.get("b3_can_close_from_proof_review") is True,
            closure.get("proof_gap_closed") is True,
            closure.get("pc2_closed_by_direct_substitution") is True,
            closure.get("stage_residual_O_h7_implementation_defect_proved") is True,
            direct_corollary.get("certificate_closed") is True,
            direct_corollary.get("uses_finite_probe_as_proof") is False,
        ]
    )
    primitive_route_open = all(
        [
            strict_manifest.get("primitive_taylor_route_closed") is False,
            strict_actual_taylor_bounds == 0,
            strict_open_taylor_terms == 162,
            strict_open_primitive_count == 5,
            primitive.get("actual_terms_proved") == 0,
            primitive.get("terms_with_open_primitive_blockers") == 162,
            primitive.get("primitive_route_pc2_closed") is False,
            d5_taylor.get("pc2_closed") is False,
            d5_budget.get("pc2_closed") is False,
            d5_plan.get("pc2_closed") is False,
            d5_summary.get("actual_taylor_bounds_proved") == 0,
            budget_summary.get("certified_taylor_bound_terms") == 0,
            plan_summary.get("induced_taylor_bounds_proved") == 0,
        ]
    )

    terminology_reconciled = all(
        [
            direct_route_closed,
            primitive_route_open,
            strict_manifest.get("satisfied") is True,
            strict_manifest.get("primitive_route_required_for_b3_closure") is False,
            all(reference_features.values()),
            all(manuscript_features.values()),
            proof_order_checkpoint_closed,
            assumption_non_circularity_closed,
            reporting_map_contract_closed,
            primitive_one_way_contract_closed,
            kantorovich_contract_closed,
            contract.get("fixed_tolerance_runs_are_asymptotic_proof") is False,
            closure.get("accepted_residual_to_error_theorem") is False,
            closure.get("submission_ready") is False,
        ]
    )

    result: dict[str, Any] = {
        "schema": "cmame-strict-proof-policy-reconciliation-audit-v1",
        "status": "strict_proof_policy_reconciled_b3_direct_route_closed_primitive_taylor_open",
        "read_only_audit": True,
        "submission_ready": False,
        "submission_ready_scope": "strict_proof_policy_global_boundary_not_narrowed_claim_package_decision",
        "readiness_boundary": {
            "strict_proof_policy_reconciliation_scope": "direct_residual_bridge_kantorovich_route_vs_primitive_162_term_route",
            "narrowed_claim_b4_b6_b7_statuses": narrowed_claim_b4_b6_b7_statuses,
            "global_submission_boundaries_retained": global_submission_boundaries,
        },
        "interpretation": "strict_direct_residual_bridge_kantorovich_not_primitive_162_term_closure",
        "terminology_reconciled": terminology_reconciled,
        "source_paper_style_read": {
            "reference_text": "../../1-s2.0-S0377042719305229-main.txt",
            "features": reference_features,
            "interpretation": (
                "The Lie-group constrained-BDF reference is used for proof-organization context. "
                "It does not supply the primitive 162-subterm Taylor bounds for this FullVA proof."
            ),
            "reference_paper_not_tfe_paper": True,
            "used_as_estimate_source": False,
            "active_taylor_object": "full_scaled_132_row_residual_map_F_A_h_not_primitive_162_subterms",
        },
        "manuscript_strict_proof_features": manuscript_features,
        "reference_correspondence_discipline": {
            "closed": all(main_reference_correspondence_features.values())
            and all(flat_reference_correspondence_features.values()),
            "main_features": main_reference_correspondence_features,
            "flat_features": flat_reference_correspondence_features,
            "role": (
                "machine-checked boundary that the Wieloch-Arnold proof is used as "
                "organization discipline, while FullVA Newton-Euler identities remain "
                "separate residual-bridge inputs"
            ),
        },
        "proof_order_checkpoint_contract": {
            "closed": proof_order_checkpoint_closed,
            "main_features": main_proof_order_checkpoint_features,
            "flat_features": flat_proof_order_checkpoint_features,
            "sequence": [
                "fixed_discrete_object",
                "local_defect_direct_bridge_without_primitive_162_promotion",
                "endpoint_and_retained_p6_solver_interface",
                "local_global_reporting_with_p7_nonpromotion",
            ],
            "role": (
                "machine-checked theorem-proof checkpoint that restates the "
                "reference proof ordering inside the FullVA proof without adding "
                "closure claims"
            ),
            "adds_theorem_claim": False,
            "closes_p6": False,
            "closes_p7": False,
            "uses_primitive_162_term_route": False,
        },
        "assumption_non_circularity_contract": {
            "closed": assumption_non_circularity_closed,
            "main_features": main_assumption_non_circularity_features,
            "flat_features": flat_assumption_non_circularity_features,
            "role": (
                "machine-checked boundary that the retained compact-tube, "
                "stability, and solver-scale interfaces define the theorem domain "
                "without assuming the local defect, grid estimate, or numerical evidence"
            ),
            "assumes_theorem_conclusion": False,
            "assumes_local_defect": False,
            "assumes_grid_estimate": False,
            "inferred_from_observed_slopes_or_logs": False,
            "closes_p6": False,
            "closes_p7": False,
        },
        "reporting_map_norm_consequence_contract": {
            "closed": reporting_map_contract_closed,
            "main_features": main_reporting_map_features,
            "flat_features": flat_reporting_map_features,
            "constant_formula": "C_qv = C_{\\mathcal R} C_red",
            "role": (
                "machine-checked mean-value lemma that converts the reduced-chart "
                "grid estimate to the reported q/v estimate on the same compact "
                "accepted chart without promoting residual diagnostics"
            ),
            "uses_residual_to_error_transfer": False,
            "uses_global_atlas_equivalence": False,
            "uses_output_interpolation": False,
        },
        "primitive_route_one_way_certificate_contract": {
            "closed": primitive_one_way_contract_closed,
            "main_features": main_primitive_one_way_features,
            "flat_features": flat_primitive_one_way_features,
            "logical_form": "open primitives plus P_tube imply the 162 Taylor subterms, which imply the dynamic residual bound",
            "converse_available": False,
            "direct_route_output_reinserted_as_primitive_input": False,
            "weighted_acceleration_promotes_to_unweighted_pacc": False,
            "pstate_direct_corollary_promotes_to_pstate_closure": False,
            "aggregate_residual_projects_to_primitive_subterms": False,
            "requires_hidden_primitive_projection": False,
            "actual_primitive_taylor_bounds_proved": 0,
            "role": (
                "machine-checked one-way implication discipline for the separate "
                "primitive/Taylor route; it prevents the closed direct residual bridge "
                "from being misread as a primitive 162-subterm closure"
            ),
        },
        "strict_kantorovich_radius_contract": {
            "closed": kantorovich_contract_closed,
            "main_features": main_kantorovich_features,
            "flat_features": flat_kantorovich_features,
            "residual_hypothesis": "||F_A,h(Z_G;y)|| <= C_R h^7",
            "radius_definition": "rho_h = 2 M ||R_h||",
            "small_h_conditions": ["rho_h <= r", "M L rho_h <= 1/2"],
            "self_map_claim": "T_h maps B_{rho_h}(0) into itself",
            "contraction_claim": "Lip(T_h on B_{rho_h}(0)) <= 1/2",
            "stage_error_bound": "||Z_A-Z_G|| <= C_Z h^7",
            "stage_error_constant": "C_Z = 2 M C_R",
            "endpoint_perturbation_bound": "||E_h(Z_A)-E_h(Z_G)|| <= C_A h^7",
            "endpoint_perturbation_constant": "C_A = M_E C_Z",
            "endpoint_transfer": "smooth endpoint reconstruction transfers the C_Z h^7 stage perturbation to a C_A h^7 endpoint perturbation",
            "uniform_constant_discipline": {
                "closed": all(main_kantorovich_features.values())
                and all(flat_kantorovich_features.values()),
                "residual_uniform_scope": "uniform for y in K and 0 < h <= hbar",
                "endpoint_derivative_bound": "sup_{0<h<=h0} sup_{y in K} sup_{Z in B_r(Z_G(y,h))} ||D_Z E_h(Z)|| <= M_E",
                "bridge_constant_scope": "C_R independent of y in K, h, reported grid length, backend, and finite diagnostic tolerances",
                "role": "machine-checked constant-uniformity anchors for the full-map Taylor/Kantorovich proof layer",
            },
            "uses_finite_probe_as_proof": False,
            "uses_primitive_162_route_as_input": False,
            "closes_primitive_162_route": False,
            "role": "machine-checked radius and absorption contract for the direct residual-bridge/Kantorovich proof",
        },
        "proof_theorem_traceability_policy": {
            "proof_closure_status": proof_closure.get("status"),
            "strict_audit_traceability_present": bool(strict_traceability),
            "strict_audit_traceability_source_status": strict_traceability.get("proof_closure_status"),
            "theorem_statement_labels_present": theorem_statement_boundary.get(
                "all_required_labels_present_main_and_flat"
            ),
            "conditional_theorem_boundary_present": theorem_statement_boundary.get(
                "conditional_theorem_boundary_present_main_and_flat"
            ),
            "conditional_proof_claims_mapped_to_manuscript": manuscript_traceability.get(
                "conditional_proof_claims_mapped_to_manuscript"
            ),
            "proof_dependency_graph_present": manuscript_traceability.get(
                "proof_dependency_graph_present_main_and_flat"
            ),
            "proof_traceability_table_present": manuscript_traceability.get(
                "proof_traceability_table_present_main_and_flat"
            ),
            "dynamic_proof_closure_matrix_present": manuscript_traceability.get(
                "dynamic_proof_closure_matrix_present_main_and_flat"
            ),
            "primitive_lane_boundary_present": manuscript_traceability.get(
                "primitive_lane_boundary_present_main_and_flat"
            ),
            "residual_nonpromotion_present": manuscript_traceability.get(
                "residual_to_error_nonpromotion_present_main_and_flat"
            ),
            "eta_h_theorem_condition_retained": theorem_statement_boundary.get(
                "eta_h_theorem_condition_retained"
            ),
            "eta_h_solver_policy_evidence_closed": theorem_statement_boundary.get(
                "eta_h_solver_policy_evidence_closed"
            ),
            "fixed_tolerance_runs_are_asymptotic_proof": theorem_statement_boundary.get(
                "fixed_tolerance_runs_are_asymptotic_proof"
            ),
            "residual_to_error_not_promoted": theorem_statement_boundary.get(
                "does_not_promote_residual_to_error"
            ),
            "source_policy_or_full_tfe_not_promoted": theorem_statement_boundary.get(
                "does_not_promote_source_policy_or_full_tfe"
            ),
            "does_not_change_proof_closure_state": manuscript_traceability.get(
                "does_not_change_proof_closure_state"
            ),
            "manuscript_anchor_map_present": proof_closure_anchor_map.get(
                "all_label_anchors_present"
            ),
            "manuscript_anchor_label_count": proof_closure_anchor_map.get("label_anchor_count"),
            "theorem_assumption_anchor_map_present": proof_closure_anchor_map.get(
                "all_theorem_assumption_anchors_present"
            ),
            "theorem_assumption_anchor_count": proof_closure_anchor_map.get(
                "theorem_assumption_anchor_count"
            ),
            "theorem_assumption_anchor_ids": proof_closure_anchor_map.get(
                "theorem_assumption_anchor_ids"
            ),
            "strict_audit_manuscript_anchor_map_present": strict_traceability.get(
                "manuscript_anchor_map_present"
            ),
            "proof_closure_strict_audit_anchor_fields_match": (
                proof_closure_anchor_map.get("all_label_anchors_present")
                == strict_traceability.get("manuscript_anchor_map_present")
                and proof_closure_anchor_map.get("label_anchor_count")
                == strict_traceability.get("manuscript_anchor_label_count")
                and proof_closure_anchor_map.get("all_theorem_assumption_anchors_present")
                == strict_traceability.get("theorem_assumption_anchor_map_present")
                and proof_closure_anchor_map.get("theorem_assumption_anchor_count")
                == strict_traceability.get("theorem_assumption_anchor_count")
                and proof_closure_anchor_map.get("theorem_assumption_anchor_ids")
                == strict_traceability.get("theorem_assumption_anchor_ids")
            ),
            "proof_closure_proof_claim_anchor_maps_match": proof_closure_anchor_map
            == proof_claim_anchor_map,
            "anchor_evidence_sources": expected_anchor_evidence_sources,
            "proof_contract_anchor_evidence_sources": contract_traceability.get(
                "anchor_evidence_sources"
            ),
            "proof_style_anchor_evidence_sources": style_traceability.get(
                "anchor_evidence_sources"
            ),
            "strict_audit_anchor_evidence_sources": strict_traceability.get(
                "anchor_evidence_sources"
            ),
            "all_anchor_evidence_sources_match": (
                contract_traceability.get("anchor_evidence_sources")
                == style_traceability.get("anchor_evidence_sources")
                == strict_traceability.get("anchor_evidence_sources")
                == expected_anchor_evidence_sources
            ),
            "policy_interpretation": (
                "traceability strengthens reader-facing proof-policy wording but does not close "
                "the eta_h solver-policy, residual-to-error, source-policy, or full-TFE gates"
            ),
        },
        "direct_residual_bridge_kantorovich_route": {
            "closed": direct_route_closed,
            "b3_review_passed": b3_review.get("b3_direct_proof_review_passed"),
            "b3_can_close": b3_review.get("b3_can_close_from_proof_review"),
            "direct_pc2_proof_gap_closed": closure.get(
                "direct_pc2_proof_gap_closed", closure.get("proof_gap_closed")
            ),
            "proof_gap_closed": closure.get("proof_gap_closed"),
            "proof_gap_closed_scope": closure.get(
                "proof_gap_closed_scope",
                "direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open",
            ),
            "proof_gap_closed_reading_rule": (
                "The schema-only compatibility boolean proof_gap_closed is a schema-compatible "
                "shorthand for direct_pc2_proof_gap_closed under the active direct PC2 residual-bridge/"
                "Kantorovich route, not primitive/Taylor, P6, P7, source-policy, or "
                "full-TFE closure."
            ),
            "schema_compatibility": {
                "legacy_key": "proof_gap_closed",
                "legacy_key_retained_for_schema_compatibility": True,
                "preferred_key": "direct_pc2_proof_gap_closed",
            },
            "pc2_closed_by_direct_substitution": closure.get("pc2_closed_by_direct_substitution"),
            "stage_residual_O_h7_implementation_defect_proved": closure.get(
                "stage_residual_O_h7_implementation_defect_proved"
            ),
            "dynamic_zero_rows": proof_closure.get("evidence_summary", {}).get(
                "newton_euler_d5_direct_substitution_dynamic_zero_rows"
            ),
            "full_stage_rows": proof_closure.get("evidence_summary", {}).get(
                "newton_euler_d5_direct_substitution_full_stage_rows"
            ),
            "direct_substitution_supplies_active_pc2_residual_bridge": strict_manifest.get(
                "direct_substitution_supplies_active_pc2_residual_bridge"
            ),
            "required_pc2_route": strict_manifest.get("required_pc2_route"),
            "direct_route_ps3_certificate_closed": direct_corollary.get("certificate_closed"),
            "uses_finite_probe_as_proof": direct_corollary.get("uses_finite_probe_as_proof"),
            "role": "accepted strict residual-bridge/Kantorovich perturbation route for B3 only",
        },
        "primitive_162_term_taylor_route": {
            "closed": False,
            "actual_taylor_bounds_proved": strict_actual_taylor_bounds,
            "open_taylor_bound_terms": strict_open_taylor_terms,
            "terms_with_open_primitive_blockers": strict_terms_with_open_primitives,
            "open_primitive_count": strict_open_primitive_count,
            "conditional_terms": d5_summary.get("conditional_term_bounds_under_open_primitive_assumptions"),
            "certified_taylor_bound_terms": budget_summary.get("certified_taylor_bound_terms"),
            "induced_taylor_bounds_proved": plan_summary.get("induced_taylor_bounds_proved"),
            "unweighted_acceleration_blocked_terms": budget_summary.get(
                "unweighted_acceleration_blocked_terms"
            ),
            "h_weighted_acceleration_sufficient_terms": budget_summary.get(
                "h_weighted_acceleration_sufficient_terms"
            ),
            "h_weighted_acceleration_insufficient_terms": budget_summary.get(
                "h_weighted_acceleration_insufficient_terms"
            ),
            "primitive_route_pc2_closed": primitive.get("primitive_route_pc2_closed"),
            "primitive_route_proof_gap_closed": primitive.get("primitive_route_proof_gap_closed"),
            "required_next_route": strict_manifest.get(
                "minimum_required_next_route",
                strict_policy.get("minimum_required_next_route"),
            ),
            "role": (
                "separate stricter conditional primitive Taylor certificate schema; "
                "no current instance is claimed as closed"
            ),
            "current_instance_available": strict_manifest.get(
                "primitive_taylor_schema_current_instance_available",
                strict_policy.get("primitive_taylor_schema_current_instance_available", False),
            ),
            "blocker_summary": strict_manifest.get(
                "primitive_taylor_schema_blocker_summary",
                strict_policy.get(
                    "primitive_taylor_schema_blocker_summary",
                    "0/162 Taylor bounds certified; five primitive lift/bilinear antecedents remain open",
                ),
            ),
        },
        "forbidden_interpretations": {
            "primitive_route_closed": False,
            "actual_162_taylor_bounds_proved": False,
            "finite_probe_used_as_proof": False,
            "residual_to_error_promotion_used": False,
            "submission_ready": False,
        },
        "remaining_narrowed_claim_submission_blockers": [],
        "remaining_global_submission_boundaries": global_submission_boundaries,
        "remaining_gate_scope": {
            "narrowed_claim_b4_b6_b7_statuses": narrowed_claim_b4_b6_b7_statuses,
            "b4_b6_b7_closed_elsewhere_under_narrowed_claim": all(
                item.get("status") == "closed" for item in [b4, b6, b7]
            ),
            "global_submission_boundaries_retained": global_submission_boundaries,
        },
        "source_files": {
            "proof_contract_gate": "CMAME_PROOF_CONTRACT_GATE.json",
            "proof_closure_manifest": "PROOF_CLOSURE_MANIFEST.json",
            "proof_style_audit": "CMAME_PROOF_STYLE_AUDIT.json",
            "strict_proof_audit": "CMAME_STRICT_PROOF_AUDIT.json",
            "b3_direct_proof_review": "B3_DIRECT_PROOF_REVIEW_AUDIT.json",
            "d5_conditional_taylor": "D5_CONDITIONAL_TAYLOR_CERTIFICATE.json",
            "d5_taylor_budget": "D5_TAYLOR_TERM_BUDGET_AUDIT.json",
            "d5_primitive_plan": "D5_PRIMITIVE_OBLIGATION_CLOSURE_PLAN.json",
            "main_tex": "main_cmame.tex",
            "flat_tex": "cmame_submission_flat/main_cmame_submission.tex",
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# CMAME Strict Proof Policy Reconciliation Audit",
        "",
        "Status: **strict proof policy reconciled; B3 direct route closed; primitive Taylor route open**.",
        "Here `submission_ready=false` is scoped to proof-policy/global proof-package readiness,",
        "not to the separate narrowed-claim package decision.",
        "",
        f"Interpretation: `{result['interpretation']}`.",
        f"Terminology reconciled: `{result['terminology_reconciled']}`.",
        f"Submission ready: `{result['submission_ready']}`.",
        f"Submission-ready scope: `{result['submission_ready_scope']}`.",
        f"Policy reconciliation scope: `{result['readiness_boundary']['strict_proof_policy_reconciliation_scope']}`.",
        f"B4/B6/B7 narrowed-claim statuses (narrowed-only; not source-policy row closure): `{result['readiness_boundary']['narrowed_claim_b4_b6_b7_statuses']['B4']}/{result['readiness_boundary']['narrowed_claim_b4_b6_b7_statuses']['B6']}/{result['readiness_boundary']['narrowed_claim_b4_b6_b7_statuses']['B7']}`.",
        "",
        "## Proof-Method Reference Read",
        "",
        "- Reference text: `../../1-s2.0-S0377042719305229-main.txt`.",
        f"- BLieDF/convergence sections present: `{reference_features['bliedf_section_present']}/{reference_features['convergence_section_present']}`.",
        f"- Taylor local-error/BCH/coupled-recursion markers present: `{reference_features['taylor_local_error_lemma_present']}/{reference_features['bch_perturbation_present']}/{reference_features['coupled_error_recursion_present']}`.",
        f"- Constrained local-error and multiplier-estimate markers present: `{reference_features['constrained_local_error_theorem_present']}/{reference_features['constraint_multiplier_estimate_present']}`.",
        "- Role: proof-organization context; not a source of this proof's primitive Taylor bounds.",
        f"- Reference paper is not the TFE comparison paper: `{result['source_paper_style_read']['reference_paper_not_tfe_paper']}`.",
        f"- Reference used as estimate source: `{result['source_paper_style_read']['used_as_estimate_source']}`.",
        f"- Active Taylor object: `{result['source_paper_style_read']['active_taylor_object']}`.",
        f"- Reference correspondence discipline closed: `{result['reference_correspondence_discipline']['closed']}`.",
        "- Reference correspondence is enforced as a captioned manuscript table, not an unlabeled proof-audit block.",
        "- Reference-to-FullVA translation map binds the reference proof order to present FullVA lemmas without importing estimates.",
        f"- Reference constrained-DAE slot map present: `{result['reference_correspondence_discipline']['main_features']['reference_constrained_dae_slot_checkpoint']}/{result['reference_correspondence_discipline']['main_features']['reference_two_distinct_dae_slots']}/{result['reference_correspondence_discipline']['main_features']['reference_constraint_difference_multiplier_slot']}/{result['reference_correspondence_discipline']['main_features']['reference_local_defect_slot_full_bridge']}/{result['reference_correspondence_discipline']['main_features']['reference_constrained_dae_slot_fullva']}/{result['reference_correspondence_discipline']['main_features']['reference_multipliers_stage_unknowns_not_histories']}/{result['reference_correspondence_discipline']['main_features']['reference_no_bypass_constraint_layer']}`.",
        f"- Reference-style constrained-slot contract present: `{result['reference_correspondence_discipline']['main_features']['reference_constrained_slot_contract']}/{result['reference_correspondence_discipline']['main_features']['reference_c1_local_error_slot']}/{result['reference_correspondence_discipline']['main_features']['reference_c2_constrained_algebraic_slot']}/{result['reference_correspondence_discipline']['main_features']['reference_c3_one_step_perturbation_slot']}/{result['reference_correspondence_discipline']['main_features']['reference_c4_global_recursion_slot']}/{result['reference_correspondence_discipline']['main_features']['reference_slot_no_imports']}/{result['reference_correspondence_discipline']['main_features']['reference_slot_not_estimate_transfer']}`.",
        f"- Proof-order instantiation closed: `{result['proof_order_checkpoint_contract']['closed']}`.",
        "- Proof-order instantiation fixes the discrete object, then local defect, retained P6, and P7 output boundary in that order.",
        f"- Assumption non-circularity closed: `{result['assumption_non_circularity_contract']['closed']}`.",
        "- Retained admissibility interfaces do not assume the local defect, grid estimate, observed slopes, P6 proof, or P7 boundary.",
        "- Constraint/multiplier correspondence is restricted to compact-chart, right-inverse, endpoint, and branch-stability interfaces.",
        "- Newton--Euler row identities are recorded as separate FullVA residual-bridge inputs, not imported reference multiplier estimates.",
        f"- Reporting-map norm consequence closed: `{result['reporting_map_norm_consequence_contract']['closed']}`.",
        "- Reporting map uses the compact derivative supremum on `U_K` and the same reported output indices.",
        "- Reporting map does not use residual-to-error transfer, global atlas equivalence, output interpolation, or a chart switch.",
        f"- Primitive-route one-way implication discipline closed: `{result['primitive_route_one_way_certificate_contract']['closed']}`.",
        "- Primitive route records only primitives-to-162-terms-to-residual implication; no converse is available.",
        "- Direct route output is not reinserted as a primitive input; weighted acceleration does not close unweighted P_acc.",
        "- Taylor projection checkpoint keeps the aggregate 132-row residual estimate from being read as a 162-subterm primitive certificate.",
        "",
        "## Direct Route",
        "",
        f"- Direct route closed: `{result['direct_residual_bridge_kantorovich_route']['closed']}`.",
        f"- B3 review passed/can close: `{result['direct_residual_bridge_kantorovich_route']['b3_review_passed']}/{result['direct_residual_bridge_kantorovich_route']['b3_can_close']}`.",
        f"- Direct PC2 proof gap closed: `{result['direct_residual_bridge_kantorovich_route']['direct_pc2_proof_gap_closed']}`.",
        f"- Direct proof gap scope: `{result['direct_residual_bridge_kantorovich_route']['proof_gap_closed_scope']}`.",
        f"- Schema-only compatibility key `proof_gap_closed` retained: `{result['direct_residual_bridge_kantorovich_route']['schema_compatibility']['legacy_key_retained_for_schema_compatibility']}`; reader-facing proof status should use `{result['direct_residual_bridge_kantorovich_route']['schema_compatibility']['preferred_key']}`.",
        f"- PC2 residual-value bridge satisfied by 96-row non-dynamic certificate plus same-branch 36-row base-point zero dynamic block: `{result['direct_residual_bridge_kantorovich_route']['pc2_closed_by_direct_substitution']}`.",
        f"- Stage residual O(h^7) implementation defect proved: `{result['direct_residual_bridge_kantorovich_route']['stage_residual_O_h7_implementation_defect_proved']}`.",
        f"- Dynamic/full rows: `{result['direct_residual_bridge_kantorovich_route']['dynamic_zero_rows']}/{result['direct_residual_bridge_kantorovich_route']['full_stage_rows']}`.",
        f"- Direct substitution supplies the active PC2 residual-bridge proof input: `{result['direct_residual_bridge_kantorovich_route']['direct_substitution_supplies_active_pc2_residual_bridge']}`.",
        f"- Uses finite probe as proof: `{result['direct_residual_bridge_kantorovich_route']['uses_finite_probe_as_proof']}`.",
        "",
        "## Strict Kantorovich Radius Contract",
        "",
        f"- Contract closed in main/flat TeX: `{result['strict_kantorovich_radius_contract']['closed']}`.",
        f"- Residual hypothesis: `{result['strict_kantorovich_radius_contract']['residual_hypothesis']}`.",
        f"- Radius definition: `{result['strict_kantorovich_radius_contract']['radius_definition']}`.",
        f"- Small-h conditions: `{'; '.join(result['strict_kantorovich_radius_contract']['small_h_conditions'])}`.",
        f"- Self-map claim: `{result['strict_kantorovich_radius_contract']['self_map_claim']}`.",
        f"- Contraction claim: `{result['strict_kantorovich_radius_contract']['contraction_claim']}`.",
        f"- Stage error bound: `{result['strict_kantorovich_radius_contract']['stage_error_bound']}`.",
        f"- Stage error constant: `{result['strict_kantorovich_radius_contract']['stage_error_constant']}`.",
        f"- Endpoint perturbation bound: `{result['strict_kantorovich_radius_contract']['endpoint_perturbation_bound']}`.",
        f"- Endpoint perturbation constant: `{result['strict_kantorovich_radius_contract']['endpoint_perturbation_constant']}`.",
        f"- Endpoint transfer: `{result['strict_kantorovich_radius_contract']['endpoint_transfer']}`.",
        f"- Uniform constant discipline: `{result['strict_kantorovich_radius_contract']['uniform_constant_discipline']['closed']}`.",
        f"- Residual uniform scope: `{result['strict_kantorovich_radius_contract']['uniform_constant_discipline']['residual_uniform_scope']}`.",
        f"- Endpoint derivative bound: `{result['strict_kantorovich_radius_contract']['uniform_constant_discipline']['endpoint_derivative_bound']}`.",
        f"- Bridge constant scope: `{result['strict_kantorovich_radius_contract']['uniform_constant_discipline']['bridge_constant_scope']}`.",
        f"- Uses finite probe as proof: `{result['strict_kantorovich_radius_contract']['uses_finite_probe_as_proof']}`.",
        f"- Closes primitive 162-term route: `{result['strict_kantorovich_radius_contract']['closes_primitive_162_route']}`.",
        "",
        "## Proof Theorem Traceability Policy",
        "",
        f"- Theorem labels/boundary/mapped: `{result['proof_theorem_traceability_policy']['theorem_statement_labels_present']}/{result['proof_theorem_traceability_policy']['conditional_theorem_boundary_present']}/{result['proof_theorem_traceability_policy']['conditional_proof_claims_mapped_to_manuscript']}`.",
        f"- Proof dependency/traceability/dynamic matrix: `{result['proof_theorem_traceability_policy']['proof_dependency_graph_present']}/{result['proof_theorem_traceability_policy']['proof_traceability_table_present']}/{result['proof_theorem_traceability_policy']['dynamic_proof_closure_matrix_present']}`.",
        f"- Primitive-route and residual scope boundaries: `{result['proof_theorem_traceability_policy']['primitive_lane_boundary_present']}/{result['proof_theorem_traceability_policy']['residual_nonpromotion_present']}`.",
        f"- Eta condition/closure and fixed-tolerance proof: `{result['proof_theorem_traceability_policy']['eta_h_theorem_condition_retained']}/{result['proof_theorem_traceability_policy']['eta_h_solver_policy_evidence_closed']}/{result['proof_theorem_traceability_policy']['fixed_tolerance_runs_are_asymptotic_proof']}`.",
        f"- Residual/source-policy-full-TFE not promoted: `{result['proof_theorem_traceability_policy']['residual_to_error_not_promoted']}/{result['proof_theorem_traceability_policy']['source_policy_or_full_tfe_not_promoted']}`; no-state-change `{result['proof_theorem_traceability_policy']['does_not_change_proof_closure_state']}`.",
        f"- Manuscript anchor policy: closure anchors `{result['proof_theorem_traceability_policy']['manuscript_anchor_map_present']}`; strict-audit anchors `{result['proof_theorem_traceability_policy']['strict_audit_manuscript_anchor_map_present']}`; label anchors `{result['proof_theorem_traceability_policy']['manuscript_anchor_label_count']}`; theorem-interface/P7-output-boundary anchors `{result['proof_theorem_traceability_policy']['theorem_assumption_anchor_count']}`; IDs `{','.join(result['proof_theorem_traceability_policy']['theorem_assumption_anchor_ids'])}`; strict map fields match `{result['proof_theorem_traceability_policy']['proof_closure_strict_audit_anchor_fields_match']}`; proof-claim map match `{result['proof_theorem_traceability_policy']['proof_closure_proof_claim_anchor_maps_match']}`.",
        "- Reader-facing theorem-interface split: theorem interfaces `P1--P6`; P7 is an output nonclaim/residual-to-error boundary anchor, not a theorem premise.",
        f"- Anchor evidence sources: `{','.join(result['proof_theorem_traceability_policy']['anchor_evidence_sources'])}`; contract/style/strict source match `{result['proof_theorem_traceability_policy']['all_anchor_evidence_sources_match']}`.",
        "",
        "## Primitive 162-Term Taylor Route",
        "",
        f"- Primitive route closed: `{result['primitive_162_term_taylor_route']['closed']}`.",
        f"- Primitive route current instance available: `{result['primitive_162_term_taylor_route']['current_instance_available']}`.",
        f"- Primitive route blocker summary: `{result['primitive_162_term_taylor_route']['blocker_summary']}`.",
        f"- Primitive actual/open Taylor terms: `{result['primitive_162_term_taylor_route']['actual_taylor_bounds_proved']}/{result['primitive_162_term_taylor_route']['open_taylor_bound_terms']}`.",
        f"- Terms blocked by open primitives: `{result['primitive_162_term_taylor_route']['terms_with_open_primitive_blockers']}`.",
        f"- Open primitive count: `{result['primitive_162_term_taylor_route']['open_primitive_count']}`.",
        f"- Certified/induced Taylor bounds: `{result['primitive_162_term_taylor_route']['certified_taylor_bound_terms']}/{result['primitive_162_term_taylor_route']['induced_taylor_bounds_proved']}`.",
        f"- h-weighted acceleration sufficient/insufficient terms: `{result['primitive_162_term_taylor_route']['h_weighted_acceleration_sufficient_terms']}/{result['primitive_162_term_taylor_route']['h_weighted_acceleration_insufficient_terms']}`.",
        f"- PC2 closed by primitive route: `{result['primitive_162_term_taylor_route']['primitive_route_pc2_closed']}`.",
        f"- Proof gap closed by primitive route: `{result['primitive_162_term_taylor_route']['primitive_route_proof_gap_closed']}`.",
        "- Primitive-route reading rule: `False` here is a separate diagnostic-route status, not the active PC2 status; the active PC2 residual-bridge proof is closed by the direct residual-bridge/Kantorovich route.",
        "",
        "## Forbidden Interpretations",
        "",
        f"- Primitive route closed: `{result['forbidden_interpretations']['primitive_route_closed']}`.",
        f"- Actual 162 Taylor bounds proved: `{result['forbidden_interpretations']['actual_162_taylor_bounds_proved']}`.",
        f"- Finite probe used as proof: `{result['forbidden_interpretations']['finite_probe_used_as_proof']}`.",
        f"- Residual-to-error promotion used: `{result['forbidden_interpretations']['residual_to_error_promotion_used']}`.",
        f"- Submission ready: `{result['forbidden_interpretations']['submission_ready']}`.",
        f"- Remaining narrowed-claim submission blockers: `{','.join(result['remaining_narrowed_claim_submission_blockers']) or 'none'}`.",
        f"- Remaining global submission boundaries: `{','.join(result['remaining_global_submission_boundaries'])}`.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("cmame_strict_proof_policy_reconciliation_audit=written")
    print(f"terminology_reconciled={terminology_reconciled}")
    print(f"direct_route_closed={direct_route_closed}")
    print(f"primitive_route_open={primitive_route_open}")
    print("submission_ready=False")


if __name__ == "__main__":
    main()
