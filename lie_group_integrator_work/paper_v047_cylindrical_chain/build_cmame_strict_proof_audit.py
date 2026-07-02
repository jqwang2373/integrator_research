#!/usr/bin/env python3
"""Build a strict-proof boundary audit for the CMAME manuscript."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent.parent
REF_TXT = ROOT / "1-s2.0-S0377042719305229-main.txt"
MAIN_TEX = PAPER / "main_cmame.tex"
FLAT_TEX = PAPER / "cmame_submission_flat" / "main_cmame_submission.tex"
BLOCKER = PAPER / "CMAME_BLOCKER_CLOSURE_GATE.json"
PROOF_CONTRACT = PAPER / "CMAME_PROOF_CONTRACT_GATE.json"
PROOF_CLOSURE = PAPER / "PROOF_CLOSURE_MANIFEST.json"
PROOF_CLAIM_TRACEABILITY = PAPER / "PROOF_CLAIM_TRACEABILITY_AUDIT.json"
PROOF_STYLE = PAPER / "CMAME_PROOF_STYLE_AUDIT.json"
D5_TAYLOR = PAPER / "D5_CONDITIONAL_TAYLOR_CERTIFICATE.json"
D5_TERM_BUDGET = PAPER / "D5_TAYLOR_TERM_BUDGET_AUDIT.json"
D5_OPEN_PRIMITIVE = PAPER / "D5_OPEN_PRIMITIVE_GAP_AUDIT.json"
D5_DIRECT = PAPER / "D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE.json"
D5_P_STATE_PS3_FULL_ROUTE = PAPER / "D5_P_STATE_PS3_FULL_RESIDUAL_ROUTE_CERTIFICATE.json"
DYNAMIC_ORACLE = PAPER / "DYNAMIC_ROW_ORACLE_GATE.json"
B1_AD_EXPANDED_CLOSURE = PAPER / "B1_AD_EXPANDED_SYMBOLIC_ORACLE_CLOSURE_CERTIFICATE.json"
OUT_JSON = PAPER / "CMAME_STRICT_PROOF_AUDIT.json"
OUT_MD = PAPER / "CMAME_STRICT_PROOF_AUDIT.md"
DIRECT_ROUTE_SCOPE = "direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def contains_normalized(text: str, token: str) -> bool:
    return token in text or " ".join(token.split()) in " ".join(text.split())


def blocker_by_id(gate: dict[str, Any], blocker_id: str) -> dict[str, Any]:
    for item in gate.get("blockers", []):
        if item.get("id") == blocker_id:
            return item
    raise KeyError(blocker_id)


def feature_map(text: str, tokens: dict[str, str]) -> dict[str, bool]:
    return {key: contains_normalized(text, token) for key, token in tokens.items()}


def sidecar_proof_gap_scope_entries() -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []

    def walk(file_name: str, node: Any, path: str) -> None:
        if isinstance(node, dict):
            if "proof_manifest_proof_gap_closed" in node:
                scope = node.get("proof_manifest_proof_gap_closed_scope")
                entries.append(
                    {
                        "file": file_name,
                        "json_path": path,
                        "legacy_key": "proof_manifest_proof_gap_closed",
                        "legacy_value": node.get("proof_manifest_proof_gap_closed"),
                        "scope": scope,
                        "scope_ok": scope == DIRECT_ROUTE_SCOPE,
                        "interpretation": (
                            "legacy manifest link only: direct residual-bridge/Kantorovich "
                            "proof-gap closure; not primitive Taylor, P6, P7, source-policy, "
                            "or output-order closure"
                        ),
                    }
                )
            for key, value in node.items():
                child_path = f"{path}.{key}" if path else str(key)
                walk(file_name, value, child_path)
        elif isinstance(node, list):
            for index, value in enumerate(node):
                walk(file_name, value, f"{path}[{index}]")

    for path in sorted(PAPER.glob("D5_*.json")):
        walk(path.name, read_json(path), "$")
    return entries


def main() -> None:
    ref_text = read_text(REF_TXT)
    main_tex = read_text(MAIN_TEX)
    flat_tex = read_text(FLAT_TEX)
    blocker = read_json(BLOCKER)
    proof_contract = read_json(PROOF_CONTRACT)
    proof_closure = read_json(PROOF_CLOSURE)
    proof_claim_traceability = read_json(PROOF_CLAIM_TRACEABILITY)
    proof_style = read_json(PROOF_STYLE)
    d5_taylor = read_json(D5_TAYLOR)
    d5_term_budget = read_json(D5_TERM_BUDGET)
    d5_open_primitive = read_json(D5_OPEN_PRIMITIVE)
    d5_direct = read_json(D5_DIRECT)
    d5_p_state_ps3_full_route = read_json(D5_P_STATE_PS3_FULL_ROUTE)
    dynamic_oracle = read_json(DYNAMIC_ORACLE)
    b1_ad_expanded_closure = read_json(B1_AD_EXPANDED_CLOSURE)

    b1 = blocker_by_id(blocker, "B1")
    b3 = blocker_by_id(blocker, "B3")
    b4 = blocker_by_id(blocker, "B4")
    b6 = blocker_by_id(blocker, "B6")
    b7 = blocker_by_id(blocker, "B7")
    b3_direct_review_passed = "b3_direct_proof_review_audit_passed" in b3.get("partial_progress", [])
    theorem_contract = proof_contract.get("theorem_contract", {})
    closure_state = proof_closure.get("closure_state", {})
    direct_residual_bridge_standard = proof_closure.get(
        "direct_residual_bridge_kantorovich_submission_standard",
        proof_closure.get("strict_direct_residual_bridge_submission_standard", {}),
    )
    evidence = proof_closure.get("evidence_summary", {})
    theorem_statement_boundary = proof_closure.get("theorem_statement_boundary", {})
    manuscript_traceability = proof_closure.get("manuscript_traceability", {})
    proof_closure_anchor_map = proof_closure.get("manuscript_anchor_map", {})
    proof_claim_anchor_map = proof_claim_traceability.get("manuscript_anchor_map", {})
    proof_writing_card = proof_claim_traceability.get("proof_writing_boundary_card", {})
    proof_claim_remaining_boundary = proof_claim_traceability.get("remaining_claim_boundary", {})
    d5_summary = d5_taylor.get("summary", {})
    d5_route_separation = d5_taylor.get("route_separation", {})
    term_budget_summary = d5_term_budget.get("summary", {})
    primitive_gap_summary = d5_open_primitive.get("summary", {})
    primitive_dependency_graph = d5_open_primitive.get("primitive_dependency_graph", {})
    dynamic_boundary = dynamic_oracle.get("acceptance_boundary", {})
    formula_ad_oracle = dynamic_oracle.get("formula_row_ad_jacobian_oracle", {})
    full_formula_oracle = dynamic_oracle.get("full_independent_formula_row_oracle", {})
    sidecar_scope_entries = sidecar_proof_gap_scope_entries()
    sidecar_scope_ok_count = sum(1 for item in sidecar_scope_entries if item.get("scope_ok"))

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

    theorem_tokens = {
        "regularity_assumption": r"\label{ass:regularity}",
        "endpoint_closure_lemma": r"\label{lem:endpoint-closure}",
        "endpoint_functional_velocity_kkt": "velocity-level/KKT closure equations",
        "endpoint_not_raw_diagnostics": "not the set of every raw endpoint",
        "endpoint_raw_position_monitor_boundary": "raw position residual in that table is a separate monitor",
        "endpoint_diagnostics_do_not_discharge_p2": "do not discharge the compact-tube endpoint raw-defect/right-inverse hypothesis",
        "endpoint_diagnostic_scope_checkpoint": "Endpoint diagnostic-scope checkpoint",
        "endpoint_order_fit_not_hypothesis_source": "order-fit row in Table~\\ref{tab:endpoint-closure-scaling} is not used",
        "endpoint_fixed_compact_tube_data_before_table": "fixed uniform compact-tube data before that table is read",
        "endpoint_raw_position_slope_no_contradiction": "raw position monitor may have a different fitted slope without contradicting the lemma",
        "endpoint_small_raw_position_no_discharge": "small raw position monitor would not discharge the velocity-level/KKT defect bound",
        "endpoint_table_consistency_diagnostic_only": "consistency diagnostic for the reported closure subsystem",
        "stage_residual_perturbation_lemma": r"\label{lem:stage-residual-defect}",
        "stage_taylor_expansion": r"F_{A,h}(Z_G+\Delta;y)",
        "quadratic_remainder": r"Q_h(\Delta)",
        "newton_kantorovich_absorption": r"\mathcal T_h(\Delta)",
        "contraction_radius": r"\rho_h=2M\|R_h\|",
        "stage_error_bound": r"\le 2MC_Rh^7=C_Zh^7",
        "stage_single_instance_requirement": "Single-instance requirement",
        "stage_same_fixed_residual_map_norm": "same fixed residual map and norm",
        "ideal_lift_not_implementation_discharge": "Ideal lift is not implementation discharge",
        "ideal_lift_target_equation_identity": "target-equation identity for the smooth lift",
        "ideal_lift_code_facing_bridge": r"code-facing implemented \(O(h^7)\) bridge statement",
        "endpoint_closure_explicit_constant": r"C_E=4M_{E,\mathrm{ri}}C_{E,\mathrm{raw}}",
        "inexact_newton_lemma": r"\label{lem:inexact-newton}",
        "inexact_newton_endpoint_constant": r"C_N=2M_AM_N",
        "inexact_newton_scaled_endpoint_constant": r"C_Nc_\eta h^7",
        "p6_reported_log_nonclosure_lemma": r"\label{lem:p6-reported-log-nonclosure}",
        "p6_reported_logs_do_not_close": "Reported solver logs are not a P6 proof",
        "p6_log_not_compact_tube_envelope": "not a compact-tube solver envelope",
        "p6_log_cannot_calibrate_ceta": "It cannot calibrate",
        "p6_log_does_not_prove_branch_membership": "prove branch membership",
        "p6_log_diagnostic_grade": "diagnostic-grade solver information",
        "inexact_branch_ball_checkpoint": "Branch-ball membership checkpoint",
        "inexact_two_independent_solver_facts": "two independent solver facts",
        "inexact_iterate_certified_in_ball": r"\(B_{r_A}(Z_A)\)",
        "inexact_residual_envelope_fixed_norm": r"\eta_h^{\rm tube}",
        "inexact_residual_cannot_replace_membership": "cannot replace the first",
        "inexact_log_not_theorem_input": "not a theorem input unless",
        "inexact_same_gauss_predictor_branch": "same Gauss-predictor branch",
        "inexact_not_larger_constant_or_lower_order": "not counted as a larger local constant or as a lower-order inexact Newton step",
        "p6_conditional_instantiation_checkpoint": "P6 conditional-instantiation checkpoint",
        "p6_operational_sufficient_instantiation": "operational sufficient instantiation",
        "p6_fixed_norm_scaling_branch_rule": "proof norm, row scaling, branch rule",
        "p6_same_gauss_predictor_branch_certified": "same Gauss-predictor branch",
        "p6_proof_norm_stopping_target": "proof-norm stopping target",
        "p6_reported_grid_specialization": "reported-grid specialization",
        "p6_no_hidden_h_dependent_row_weights": "hidden \\(h\\)-dependent row weights",
        "p6_h_independent_norm_equivalence": "\\(h\\)-independent compact-tube norm equivalence",
        "p6_explicit_residual_h_factor_binding": "finite-dimensional norm-equivalence constant after the explicit residual",
        "p6_small_residual_wrong_norm_not_input": "small residual in a different norm, branch, row scaling, or terminal solve is not an input",
        "p6_sufficient_not_empirical_discharge": "sufficient instantiation rule, not a hidden empirical discharge",
        "p6_no_theorem_level_solver_evidence": "does not prove a theorem-level solver-policy theorem",
        "p6_no_residual_ratio_fitting": r"does not choose \(c_\eta\) from residual ratios",
        "p6_no_global_newton_remote_root": "does not prove global Newton convergence or remote-root exclusion",
        "p6_evidence_grade_rule": "P6 evidence-grade rule",
        "p6_only_one_theorem_grade_input": "P6 has only one theorem-grade input",
        "p6_predeclared_same_branch_residual_envelope": "predeclared same-branch residual envelope",
        "p6_diagnostic_grade_evidence_only": "diagnostic-grade evidence only",
        "p6_log_specializes_not_creates": "solver log can specialize a P6 hypothesis",
        "reported_grid_domain_qualification": "reported run may instantiate the theorem",
        "reported_grid_predeclared_dh_branch": "branch, tube, endpoint, proof-norm",
        "reported_grid_not_posthoc_filtered_logs": "post-hoc filtered solver logs",
        "proof_obligation_closure_narrative": "Residual-bridge handoff",
        "p5_direct_dynamic_row_identity": "P5 direct dynamic-row identity",
        "p1p2p3_p4binding_p6_retained_conditions": "branch-solver scale are theorem-domain hypotheses",
        "closed_scope_direct_route_only": "The theorem closure below refers only to the direct residual-bridge/Kantorovich",
        "closed_scope_retained_interfaces": "argument under the stated branch, endpoint, implementation, and solver-scale",
        "closed_scope_not_p6_p7_primitive": "it does not prove a separate theorem for fixed production tolerances",
        "p7_residual_to_error_deliberately_not_used": "P7 residual-to-error route is deliberately not used",
        "strong_but_conditional_theorem": "the theorem is strong but conditional",
        "reference_proof_method_alignment": "Reference-paper proof-method alignment",
        "reference_bdf_alignment": "Lie-group constrained-BDF convergence",
        "reference_not_tfe_comparator": "not the temporal finite-element comparator",
        "reference_disjoint_roles": "the comparator paper therefore have disjoint roles",
        "reference_ordering_template_not_literal_transfer": "as a proof-obligation ordering template, not as a literal proof transfer",
        "reference_no_fullva_residual_taylor_constant": "no FullVA residual Taylor constant",
        "reference_no_one_step_gauss_theorem": "no one-step Gauss theorem",
        "reference_reduced_gauss_order_only": "formal Gauss order is used only for the reduced smooth Gauss branch",
        "reference_fullva_next_slot_bridge": "FullVA enters the next proof slot through the fixed",
        "reference_technical_startvalue_boundary": "technical neighborhood and start-value assumptions",
        "reference_technical_assumptions_mapped_to_domain": "retained compact-tube/branch domain, endpoint and solver-scale interfaces",
        "reference_no_retroactive_diagnostic_verification": "do not verify them retroactively",
        "reference_technical_theorem_contract_boundary": "technical-neighborhood and start-value clauses",
        "reference_technical_theorem_contract_replacement": "same-reduced-initial-state clauses, all fixed before any diagnostic table is read",
        "reference_order_taylor_discipline": "Reference-order Taylor discipline",
        "reference_structural_order_no_taylor_import": "structural ordering discipline only; no Taylor estimate, primitive lift bound, or multiplier estimate is imported",
        "reference_fullmap_taylor_closed_fixed_132": "T2 full-map Taylor/Kantorovich estimate is established only for the fixed",
        "reference_diagnostics_after_theorem_boundary": "report numerical diagnostics after the theorem boundary is fixed",
        "reference_taylor_local_error": "Taylor-expansion local truncation estimate",
        "reference_lie_algebra_global_error": "global configuration error in the Lie algebra",
        "reference_bch_perturbation": "Baker--Campbell--Hausdorff perturbation estimates",
        "reference_coupled_error_recursion": "holonomic-constraint differences, a multiplier estimate, and a coupled error",
        "reference_no_bdf_import": "not by importing the",
        "reference_no_estimate_transfer_ledger": "Reference no-estimate-transfer table",
        "reference_no_estimate_transfer_caption": "No-estimate-transfer table for the Wieloch--Arnold constrained-BDF proof",
        "reference_forbidden_transfer_column": "Forbidden estimate transfer",
        "reference_replacement_column": "Replacement in this proof",
        "reference_no_bdf_premise": "No BLieDF Taylor constant, BDF \\(p=k\\) conclusion",
        "reference_no_bch_constants": "The BCH constants and global Lie-algebra recursion constants",
        "reference_no_multiplier_history_import": "The reference multiplier-history estimate and hidden-constraint estimate",
        "reference_table_not_theorem_input": "The table is not a theorem input",
        "reference_fixed_object_sequence": "fixed object, smooth-branch insertion, local defect, and local-to-global",
        "reference_proof_order_not_estimate_transfer": "proof-order transfer, not an estimate transfer",
        "reference_direct_bridge_supplies_formula_residual": "the 132-row residual bridge used here",
        "reference_no_primitive_fullva_subterm_bound_imported": "does not import the reference paper's BLieDF hidden-constraint estimates",
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
        "reference_slot_analogy_not_symmetric": "slot analogy is not symmetric",
        "reference_bdf_hidden_constraint_not_fullva_certificate": "BDF hidden-constraint estimate cannot replace the FullVA lower-pair",
        "reference_direct_bridge_not_multiplier_history_theorem": "FullVA direct residual bridge cannot be read as proving the reference",
        "method_endpoint_p2_controlled": "Controlled by P2 local right-inverse and raw-defect",
        "method_endpoint_diagnostics_separate": "KKT/projection diagnostics are recorded separately",
        "theorem_named_clauses": "For this theorem invocation the named clauses are",
        "theorem_p1_smooth_lift_clause": "P1 fixes the smooth lift and chart tube",
        "theorem_p2_endpoint_inverse_clause": "P2 fixes the compact stage inverse, endpoint raw-defect",
        "theorem_p3_implementation_clause": "P3 fixes the implementation path, row ordering, row scaling, and proof norm",
        "theorem_p4_only_96_rows": "P4 supplies only the 96 non-dynamic row-local certificate",
        "theorem_p5_only_direct_36_rows": "P5 supplies the 36 Newton--Euler rows only through the direct substitution identity",
        "theorem_p6_only_solver_envelope": "P6 supplies only the branch-selected solver residual envelope",
        "theorem_clauses_not_inferred_from_diagnostics": "None of these clauses is inferred from observed slopes",
        "theorem_input_output_reading_rule": "Theorem input-output reading rule",
        "theorem_no_backward_arrows": "No arrow in this chain is used backwards",
        "theorem_reported_run_only_specializes": "reported run may only specialize that theorem instance",
        "theorem_no_retroactive_instance_change": "cannot retroactively change the theorem branch, norm, row scaling, or residual envelope",
        "theorem_one_residual_certificate": "Only one residual-value certificate is consumed in this theorem invocation",
        "theorem_future_t3_same_tuple_replacement": "future primitive/Taylor certificate may replace the accepted direct",
        "theorem_no_append_lower_remove_promote": "cannot be appended to the direct certificate to lower constants, remove",
        "proof_gap_token_scope_checkpoint": "Direct residual-bridge scope convention",
        "proof_gap_token_direct_pc2_only": "residual-bridge/Kantorovich input",
        "proof_gap_token_not_p6_p7_primitive": "does not prove a solver-policy theorem or a P7 residual-to-error boundary, does not complete the primitive/Taylor route",
        "proof_gap_token_not_extra_assumption": "not an additional theorem assumption",
        "same_object_closure_criterion": "Same-object theorem-composition criterion",
        "same_object_branch_row_norm_endpoint_agree": "branch, row convention, norm, and endpoint map agree before the constants are chosen",
        "same_object_no_cross_branch_splicing": "cannot be spliced into a single theorem instance",
        "same_object_jointly_admissible_tuple": "jointly admissible tuple",
        "same_object_reference_c1_c4_slots": "reference-style C1--C4 slots are admissible only when their outputs live in this same theorem object",
        "same_object_c1_c3_declared_residual": "C1 local-error slot may feed the C3 perturbation slot only as the bridged residual value for the declared",
        "same_object_different_typed_object": "different typed object",
        "same_object_equivalence_transport_required": "requires an explicit equivalence or transport lemma before it can enter the theorem composition",
        "constraint_multiplier_reaction_output_fence": "Constraint-multiplier and reaction-output fence",
        "multiplier_step_not_theorem_output": "multiplier-error estimate; it is not a theorem",
        "stage_multipliers_algebraic_unknowns": "stage multipliers",
        "multipliers_enter_only_through_residual_bridge": "They enter the accepted theorem only through the \\(132\\)-row residual bridge",
        "no_multiplier_reaction_h6_estimate": "\\(h^6\\) trajectory estimate for multiplier histories",
        "separate_multiplier_reaction_theorem_required": "separate multiplier/reaction reporting theorem",
        "reaction_residuals_not_multiplier_order_claim": "not be read as a residual-to-error promotion or as a multiplier-order claim",
        "taylor_layer_separation_checkpoint": "Taylor-layer separation",
        "taylor_t1_gauss_layer": "T1 is the standard smooth Gauss collocation local-truncation layer",
        "taylor_t2_full_residual_map_layer": "T2 is the theorem-level FullVA residual-map layer",
        "taylor_t3_optional_primitive_route": "T3 is the separate primitive Newton--Euler Taylor route",
        "taylor_t1_t2_load_bearing": "Only T1 and T2 are load-bearing",
        "taylor_accounting_rule": "Taylor accounting rule",
        "taylor_fixed_before_expansion": "scheme, variables, comparison solution, and constants are fixed before",
        "taylor_constants_compact_tube_only": "all Taylor constants in the load-bearing lemmas are compact-tube constants",
        "taylor_t2_variable_delta": r"Taylor variable for T2 is \(\Delta=Z-Z_G\)",
        "taylor_zero_rows_before_full_map": "zero Newton--Euler rows enter before the full-map Taylor expansion",
        "taylor_no_t2_to_prove_primitives": "cannot use the T2 conclusion to prove those primitives",
        "taylor_same_object_transport_gate": r"\label{lem:same-object-taylor-transport-gate}",
        "taylor_same_mathematical_object": "same mathematical object used here",
        "taylor_transport_fullva_stage_variables": "accepted FullVA stage variables",
        "taylor_transport_not_t3_input": "not a T3 input, cannot certify any of the \\(162\\) primitive D5 Taylor",
        "taylor_no_reverse_inference_lemma": r"\label{lem:no-reverse-taylor-inference}",
        "taylor_no_reverse_global_estimate": "global \\(O(h^6)\\) output estimate and finite diagnostics cannot be used backward",
        "taylor_no_reverse_does_not_prove_primitives": "do not prove the five open primitive lift or bilinear estimates",
        "taylor_projection_checkpoint": "Taylor-projection checkpoint",
        "taylor_aggregate_fixed_block_norm": "aggregate estimate in the fixed block norm",
        "taylor_not_projection_certificate_162": "not a projection certificate for the 162 primitive scalar subterms",
        "taylor_primitive_projection_operator": r"\Pi_{\rm prim}",
        "taylor_projection_right_inverse_needed": "primitive projection/right-inverse",
        "taylor_independent_primitive_lift_bounds": r"independent \(O(h^7)\) bounds for all primitive lift maps",
        "taylor_no_projection_right_inverse_used": "No such primitive projection/right-inverse is used",
        "taylor_t2_closed_while_primitive_separate": "aggregate residual bridge can close the T2 residual-defect input while the primitive-route status",
        "taylor_counts_not_additive_proof_evidence": "not additive proof evidence",
        "taylor_templates_not_spliced_with_pc2": "conditional templates cannot be spliced",
        "taylor_primitive_route_must_prove_five_obligations": "primitive-route theorem would have to prove the five open primitive obligations",
        "taylor_primitive_route_must_redo_chain": "redo the residual-to-root, endpoint, solver, and global-transfer chain",
        "taylor_route_exclusivity_refinement": "Route-exclusivity refinement",
        "taylor_route_same_branch_tuple": "one same-branch proof tuple",
        "taylor_route_future_t3_own_cr": r"C_R^{\mathrm{T3}}h^7",
        "taylor_route_cannot_lower_constants": "cannot be combined with the accepted direct \\(C_Rh^7\\) term to",
        "taylor_route_cannot_remove_p6": "remove the retained P6 solver-scale condition",
        "taylor_route_cannot_promote_p7": "use P7 residual-to-error rows",
        "taylor_route_one_residual_certificate": "consumes one residual-value certificate",
        "taylor_route_never_mixes_partial": "never mixes partial certificates from the direct and primitive routes",
        "same_object_direct_substitution_calculation": "Same-object direct-substitution calculation",
        "same_object_block_residual": r"R_h=F_{A,h}(Z_G;y)",
        "same_object_dynamic_zero_block": r"F^{\rm dyn}_{A,h}(Z_G;y)=0",
        "same_object_stage_root_equation": r"\Delta=-J_h^{-1}R_h-J_h^{-1}Q_h(\Delta)",
        "same_object_endpoint_bound": r"\le M_EC_Zh^7=C_Ah^7",
        "same_object_no_imported_fitted_primitive_constants": "No constant in this calculation is imported from",
        "taylor_conditional_implication_prop": r"\label{prop:d5-primitive-taylor-conditional-implication}",
        "taylor_conditional_implication_lemma": r"\label{lem:d5-primitive-obligation-implication}",
        "taylor_conditional_implication_intro": "This separate primitive-route lemma is a conditional finite implication",
        "taylor_conditional_five_open_obligations": "Assume the five remaining primitive obligations",
        "taylor_conditional_all_d5_subterms": "every D5 Taylor subterm in the 36 Newton--Euler rows",
        "taylor_conditional_not_pc2_input": "not an accepted primitive-route closure, not a PC2 input",
        "common_admissible_window_checkpoint": "Common admissible-window checkpoint",
        "single_same_branch_admissibility_rule": "single same-branch admissibility rule",
        "common_h_star_window": r"h_\star=",
        "common_window_res_rep_disambiguated": r"h_{\rm res}",
        "common_window_reporting_symbol": r"h_{\rm rep}",
        "kantorovich_common_window_restrictions": r"2MC_Rh_0^7\le r",
        "exact_comparison_inputs_in_accepted_domain": r"y(t_n)\in\mathcal D_h",
        "exact_state_defect_domain_invocation": "be admissible as exact-state inputs for that local-defect comparison",
        "compact_tube_part_first_exit": "compact-tube part of this domain is handled by the first-exit",
        "branch_solver_parts_retained": "P6 solver-envelope membership remain retained transition hypotheses",
        "mean_value_residual": "mean-value form of the residual",
        "local_global_transfer_lemma": r"\label{lem:local-global-transfer}",
        "local_global_reduced_grid_constant": r"C_{\rm red}=C_{\rm loc}\Gamma_s(T)",
        "reference_proof_invariant_checkpoint": "Reference-style proof invariant",
        "reference_invariant_fixed_fullva": "fixed FullVA residual and branch",
        "reference_invariant_same_branch_residual": "same-branch residual defect at",
        "reference_invariant_no_bdf_import": "No BLieDF local-error constant",
        "reference_invariant_no_downstream_backfill": "not allowed to define an upstream arrow",
        "reference_recursion_analogue_checkpoint": "Reference-style recursion analogue",
        "reference_recursion_structural_not_estimate": "The analogy is structural, not an estimate transfer",
        "reference_recursion_fullva_variables_consumed": "lower-pair algebraic variables and stage multipliers have already been consumed inside the fixed",
        "reference_recursion_no_hidden_multiplier": "There is no hidden multiplier recursion",
        "reference_recursion_separate_output": "separate coupled output recursion",
        "local_global_truncated_first_exit_checkpoint": "Truncated first-exit recursion checkpoint",
        "local_global_truncated_index": r"m_\ast=\min\{N,n_\ast\}",
        "local_global_truncated_only_before_exit": "evaluated only before the hypothetical first exit",
        "local_global_no_post_exit_estimates": "does not use the local estimates after a hypothetical exit",
        "local_global_exit_contradiction": "contradicting the definition of the first exit",
        "local_global_extend_after_exit_excluded": "only after this contradiction is the estimate extended to every reported index",
        "local_global_time_augmentation_checkpoint": "Time-augmentation convention for the transfer",
        "local_global_augmented_chart": r"\widehat y=(y,\tau)",
        "local_global_tau_dot_one": r"\dot\tau=1",
        "local_global_exact_time_advance": r"\tau\mapsto\tau+h",
        "local_global_time_zero_error": "time component contributes zero grid error",
        "local_global_two_parameter_flow": r"\varphi_{t+h,t}(y)",
        "local_global_no_time_phase_mismatch": "no time-phase mismatch",
        "local_global_augmented_semigroup_identity": "autonomous augmented semigroup identity",
        "local_global_synchronized_time_slice": "Synchronized-time stability slice",
        "local_global_same_input_time_slice": "same reported input-time slice",
        "local_global_tau_n_equals_t_n": r"\tau_n=t_n",
        "local_global_exact_next_time": r"\tau_{n+1}=t_{n+1}",
        "local_global_no_time_registration_error": "does not hide a time-registration error",
        "local_global_no_different_time_phases": "never compares states with different time phases",
        "local_global_no_time_shifted_fit": "time-shifted trajectory data",
        "local_global_time_indexed_map": r"\Psi_{h,t_n}",
        "stability_map_binding_checkpoint": "Stability-map binding checkpoint",
        "stability_map_is_g6fullva": "the endpoint-closed inexact accepted map",
        "stability_same_branch_proof_norm": "same accepted compact branch and proof norm",
        "exact_stage_maps_local_defect_only": "used only to decompose the one-step local defect",
        "no_exact_stage_stability_substitution": "their stability is not substituted into the global recursion",
        "stability_constant_accepted_map": "same-branch stability scale for the accepted map",
        "single_g6fullva_recurrence": r"y_{n+1}=\Psi_h^{\mathrm{G6FVA}}(y_n)",
        "no_hidden_map_switch": "prevents a hidden map-switch",
        "qv_reporting_explicit_constant": r"C_{qv}=C_{\mathcal R}C_{\rm red}",
        "reporting_convex_chart_checkpoint": "Convex chart-neighborhood checkpoint",
        "reporting_fixed_convex_neighborhood": r"fixed convex coordinate neighborhood",
        "reporting_u_k_derivative_supremum": r"\sup_{y\in U_K}\|D\mathcal R(y)\|\le C_{\mathcal R}",
        "reporting_no_convex_k_assumption": r"does not assume that \(K\) itself is convex",
        "reporting_segments_inside_uk": "segments between them stay inside \\(U_K\\)",
        "reporting_one_euclidean_chart": "one fixed Euclidean chart",
        "reporting_no_atlas_switch": "not an atlas switch",
        "reporting_no_fitted_norm_equivalence": "not a fitted norm-equivalence constant",
        "order_accounting_checkpoint": "Order-accounting checkpoint",
        "order_accounting_local_h7_global_h6": r"local defect bounded by \(C_{\rm loc}h^7\)",
        "order_accounting_nh_inverse": r"N_h=O(h^{-1})",
        "order_accounting_sixth_order_grid_bound": "theorem refers to the same-initial-state reported-grid \\(h^6\\) bound",
        "order_accounting_observed_slopes_downstream": "7.161/7.066 are downstream consistency evidence",
        "order_accounting_not_seventh_order": "not a seventh-order theorem",
        "order_accounting_stronger_claim_requires_new_theorem": "A stronger global-order statement would require a new theorem",
        "conditional_order_theorem": r"\label{thm:g6fullva-order}",
        "discrete_gronwall_step": "discrete Gronwall argument",
        "primitive_taylor_route_retained": "retained as a separate primitive-route specification",
        "integral_remainder_primitive": "Taylor's formula with integral remainder",
        "p_state_ps3_full_residual_route": r"\label{lem:d5-p-state-ps3-full-residual-route}",
        "direct_route_state_block_corollary": "Direct-route state-block corollary; not primitive",
        "direct_route_residual_decomposition": "direct-route residual decomposition",
        "dynamic_row_component_balance_expansion": "componentwise Newton--Euler equations on the same lifted stage",
        "dynamic_row_residual_zero_substitution": r"r^{\rm tr}_{sbc}(Z_G)=0",
        "dynamic_row_virtual_work_sign_binding": "D3 fixes the signs",
        "dynamic_row_implemented_scalar_binding": "implemented unweighted scalar rows are exactly these component residuals",
        "primitive_162_subterm_boundary": "not a certification of the primitive 162-subterm Taylor route",
        "primitive_taylor_bounds_not_established": "no actual D5 primitive",
        "h_weighted_acceleration_terms_insufficient": r"36 \(h\)-weighted acceleration primitive terms",
        "proof_boundary_not_source_replacement": "not a complete source-paper temporal finite-element residual replacement",
    }
    main_features = feature_map(main_tex, theorem_tokens)
    flat_features = feature_map(flat_tex, theorem_tokens)

    strict_conditional_math_proof_present = all(
        main_features[key]
        for key in [
            "regularity_assumption",
            "endpoint_closure_lemma",
            "endpoint_functional_velocity_kkt",
            "endpoint_not_raw_diagnostics",
            "endpoint_raw_position_monitor_boundary",
            "endpoint_diagnostics_do_not_discharge_p2",
            "endpoint_diagnostic_scope_checkpoint",
            "endpoint_order_fit_not_hypothesis_source",
            "endpoint_fixed_compact_tube_data_before_table",
            "endpoint_raw_position_slope_no_contradiction",
            "endpoint_small_raw_position_no_discharge",
            "endpoint_table_consistency_diagnostic_only",
            "stage_residual_perturbation_lemma",
            "stage_taylor_expansion",
            "quadratic_remainder",
            "newton_kantorovich_absorption",
            "contraction_radius",
            "stage_error_bound",
            "stage_single_instance_requirement",
            "stage_same_fixed_residual_map_norm",
            "endpoint_closure_explicit_constant",
            "inexact_newton_lemma",
            "inexact_newton_endpoint_constant",
            "inexact_newton_scaled_endpoint_constant",
            "inexact_branch_ball_checkpoint",
            "inexact_two_independent_solver_facts",
            "inexact_iterate_certified_in_ball",
            "inexact_residual_envelope_fixed_norm",
            "inexact_residual_cannot_replace_membership",
            "inexact_log_not_theorem_input",
            "inexact_same_gauss_predictor_branch",
            "inexact_not_larger_constant_or_lower_order",
            "p6_conditional_instantiation_checkpoint",
            "p6_operational_sufficient_instantiation",
            "p6_fixed_norm_scaling_branch_rule",
            "p6_same_gauss_predictor_branch_certified",
            "p6_proof_norm_stopping_target",
            "p6_reported_grid_specialization",
            "p6_no_hidden_h_dependent_row_weights",
            "p6_h_independent_norm_equivalence",
            "p6_explicit_residual_h_factor_binding",
            "p6_small_residual_wrong_norm_not_input",
            "p6_sufficient_not_empirical_discharge",
            "p6_no_theorem_level_solver_evidence",
            "p6_no_residual_ratio_fitting",
            "p6_no_global_newton_remote_root",
            "p6_evidence_grade_rule",
            "p6_only_one_theorem_grade_input",
            "p6_predeclared_same_branch_residual_envelope",
            "p6_diagnostic_grade_evidence_only",
            "p6_log_specializes_not_creates",
            "proof_obligation_closure_narrative",
            "p5_direct_dynamic_row_identity",
            "p1p2p3_p4binding_p6_retained_conditions",
            "p7_residual_to_error_deliberately_not_used",
            "strong_but_conditional_theorem",
            "reference_proof_method_alignment",
            "reference_bdf_alignment",
            "reference_not_tfe_comparator",
            "reference_disjoint_roles",
            "reference_ordering_template_not_literal_transfer",
            "reference_no_fullva_residual_taylor_constant",
            "reference_no_one_step_gauss_theorem",
            "reference_technical_startvalue_boundary",
            "reference_technical_assumptions_mapped_to_domain",
            "reference_no_retroactive_diagnostic_verification",
            "reference_technical_theorem_contract_boundary",
            "reference_technical_theorem_contract_replacement",
            "reference_taylor_local_error",
            "reference_lie_algebra_global_error",
            "reference_bch_perturbation",
            "reference_coupled_error_recursion",
            "reference_no_bdf_import",
            "reference_no_estimate_transfer_ledger",
            "reference_no_estimate_transfer_caption",
            "reference_forbidden_transfer_column",
            "reference_replacement_column",
            "reference_no_bdf_premise",
            "reference_no_bch_constants",
            "reference_no_multiplier_history_import",
            "reference_table_not_theorem_input",
            "reference_fixed_object_sequence",
            "reference_proof_order_not_estimate_transfer",
            "reference_direct_bridge_supplies_formula_residual",
            "reference_no_primitive_fullva_subterm_bound_imported",
            "reference_fullva_translation_checkpoint",
            "reference_partial_order_obligations",
            "reference_r1_fixed_discrete_object",
            "reference_r2_smooth_branch_same_object",
            "reference_r3_fixed_object_defect_conversion",
            "reference_r4_stability_after_local_defect",
            "reference_right_hand_independent",
            "reference_does_not_repair_failed_lemma",
            "reference_dependency_graph_not_premise",
            "reference_constrained_dae_slot_checkpoint",
            "reference_two_distinct_dae_slots",
            "reference_constraint_difference_multiplier_slot",
            "reference_local_defect_slot_full_bridge",
            "reference_constrained_dae_slot_fullva",
            "reference_multipliers_stage_unknowns_not_histories",
            "reference_no_bypass_constraint_layer",
            "reference_slot_analogy_not_symmetric",
            "reference_bdf_hidden_constraint_not_fullva_certificate",
            "reference_direct_bridge_not_multiplier_history_theorem",
            "method_endpoint_p2_controlled",
            "method_endpoint_diagnostics_separate",
            "theorem_named_clauses",
            "theorem_p1_smooth_lift_clause",
            "theorem_p2_endpoint_inverse_clause",
            "theorem_p3_implementation_clause",
            "theorem_p4_only_96_rows",
            "theorem_p5_only_direct_36_rows",
            "theorem_p6_only_solver_envelope",
            "theorem_clauses_not_inferred_from_diagnostics",
            "theorem_input_output_reading_rule",
            "theorem_no_backward_arrows",
            "theorem_reported_run_only_specializes",
            "theorem_no_retroactive_instance_change",
            "theorem_one_residual_certificate",
            "theorem_future_t3_same_tuple_replacement",
            "theorem_no_append_lower_remove_promote",
            "proof_gap_token_scope_checkpoint",
            "proof_gap_token_direct_pc2_only",
            "proof_gap_token_not_p6_p7_primitive",
            "proof_gap_token_not_extra_assumption",
            "same_object_closure_criterion",
            "same_object_branch_row_norm_endpoint_agree",
            "same_object_no_cross_branch_splicing",
            "same_object_jointly_admissible_tuple",
            "constraint_multiplier_reaction_output_fence",
            "multiplier_step_not_theorem_output",
            "stage_multipliers_algebraic_unknowns",
            "multipliers_enter_only_through_residual_bridge",
            "no_multiplier_reaction_h6_estimate",
            "separate_multiplier_reaction_theorem_required",
            "reaction_residuals_not_multiplier_order_claim",
            "taylor_layer_separation_checkpoint",
            "taylor_t1_gauss_layer",
            "taylor_t2_full_residual_map_layer",
            "taylor_t3_optional_primitive_route",
            "taylor_t1_t2_load_bearing",
            "taylor_accounting_rule",
            "taylor_fixed_before_expansion",
            "taylor_constants_compact_tube_only",
            "taylor_t2_variable_delta",
            "taylor_zero_rows_before_full_map",
            "taylor_no_t2_to_prove_primitives",
            "taylor_projection_checkpoint",
            "taylor_aggregate_fixed_block_norm",
            "taylor_not_projection_certificate_162",
            "taylor_primitive_projection_operator",
            "taylor_projection_right_inverse_needed",
            "taylor_independent_primitive_lift_bounds",
            "taylor_no_projection_right_inverse_used",
            "taylor_t2_closed_while_primitive_separate",
            "taylor_counts_not_additive_proof_evidence",
            "taylor_templates_not_spliced_with_pc2",
            "taylor_primitive_route_must_prove_five_obligations",
            "taylor_primitive_route_must_redo_chain",
            "taylor_route_exclusivity_refinement",
            "taylor_route_same_branch_tuple",
            "taylor_route_future_t3_own_cr",
            "taylor_route_cannot_lower_constants",
            "taylor_route_cannot_remove_p6",
            "taylor_route_cannot_promote_p7",
            "taylor_route_one_residual_certificate",
            "taylor_route_never_mixes_partial",
            "same_object_direct_substitution_calculation",
            "same_object_block_residual",
            "same_object_dynamic_zero_block",
            "same_object_stage_root_equation",
            "same_object_endpoint_bound",
            "same_object_no_imported_fitted_primitive_constants",
            "common_admissible_window_checkpoint",
            "single_same_branch_admissibility_rule",
            "common_h_star_window",
            "common_window_res_rep_disambiguated",
            "common_window_reporting_symbol",
            "kantorovich_common_window_restrictions",
            "exact_comparison_inputs_in_accepted_domain",
            "exact_state_defect_domain_invocation",
            "compact_tube_part_first_exit",
            "branch_solver_parts_retained",
            "mean_value_residual",
            "local_global_reduced_grid_constant",
            "reference_recursion_analogue_checkpoint",
            "reference_recursion_structural_not_estimate",
            "reference_recursion_fullva_variables_consumed",
            "reference_recursion_no_hidden_multiplier",
            "reference_recursion_separate_output",
            "local_global_truncated_first_exit_checkpoint",
            "local_global_truncated_index",
            "local_global_truncated_only_before_exit",
            "local_global_no_post_exit_estimates",
            "local_global_exit_contradiction",
            "local_global_extend_after_exit_excluded",
            "local_global_time_augmentation_checkpoint",
            "local_global_augmented_chart",
            "local_global_tau_dot_one",
            "local_global_exact_time_advance",
            "local_global_time_zero_error",
            "local_global_two_parameter_flow",
            "local_global_no_time_phase_mismatch",
            "local_global_augmented_semigroup_identity",
            "local_global_synchronized_time_slice",
            "local_global_same_input_time_slice",
            "local_global_tau_n_equals_t_n",
            "local_global_exact_next_time",
            "local_global_no_time_registration_error",
            "local_global_no_different_time_phases",
            "local_global_no_time_shifted_fit",
            "local_global_time_indexed_map",
            "stability_map_binding_checkpoint",
            "stability_map_is_g6fullva",
            "stability_same_branch_proof_norm",
            "exact_stage_maps_local_defect_only",
            "no_exact_stage_stability_substitution",
            "stability_constant_accepted_map",
            "single_g6fullva_recurrence",
            "no_hidden_map_switch",
            "qv_reporting_explicit_constant",
            "reporting_convex_chart_checkpoint",
            "reporting_fixed_convex_neighborhood",
            "reporting_u_k_derivative_supremum",
            "reporting_no_convex_k_assumption",
            "reporting_segments_inside_uk",
            "reporting_one_euclidean_chart",
            "reporting_no_atlas_switch",
            "reporting_no_fitted_norm_equivalence",
            "order_accounting_checkpoint",
            "order_accounting_local_h7_global_h6",
            "order_accounting_nh_inverse",
            "order_accounting_sixth_order_grid_bound",
            "order_accounting_observed_slopes_downstream",
            "order_accounting_not_seventh_order",
            "order_accounting_stronger_claim_requires_new_theorem",
            "conditional_order_theorem",
            "discrete_gronwall_step",
            "taylor_conditional_implication_prop",
            "taylor_conditional_implication_lemma",
            "taylor_conditional_implication_intro",
            "taylor_conditional_five_open_obligations",
            "taylor_conditional_all_d5_subterms",
            "taylor_conditional_not_pc2_input",
            "dynamic_row_component_balance_expansion",
            "dynamic_row_residual_zero_substitution",
            "dynamic_row_virtual_work_sign_binding",
            "dynamic_row_implemented_scalar_binding",
        ]
    ) and all(flat_features.values())

    direct_route_strict_proof_complete = (
        b1.get("status") == "closed"
        and b3.get("status") == "closed"
        and b3_direct_review_passed
        and b1_ad_expanded_closure.get("ad_expanded_symbolic_oracle_closure") is True
        and b1_ad_expanded_closure.get("ad_expanded_symbolic_oracle_closed_cells") == 4752
        and theorem_contract.get("stage_residual_O_h7_implementation_defect_proved") is True
        and closure_state.get("stage_residual_O_h7_implementation_defect_proved") is True
        and direct_residual_bridge_standard.get("satisfied") is True
        and direct_residual_bridge_standard.get("direct_residual_bridge_kantorovich_route_closed") is True
    )

    result: dict[str, Any] = {
        "schema": "cmame-strict-proof-audit-v1",
        "status": "strict_conditional_residual_bridge_proof_audited_b3_closed_submission_not_ready",
        "read_only_audit": True,
        "submission_ready": False,
        "submission_ready_scope": "strict_proof_global_boundary_not_narrowed_claim_package_decision",
        "readiness_boundary": {
            "strict_proof_audit_scope": "B1_B3_strict_conditional_residual_bridge_proof_boundary",
            "narrowed_claim_b4_b6_b7_statuses": {
                "B4": b4.get("status"),
                "B6": b6.get("status"),
                "B7": b7.get("status"),
            },
            "global_submission_boundaries_retained": [
                "full_source_policy_package_ready",
                "theorem_level_eta_h_solver_policy_evidence",
                "closed_residual_to_error_theorem_for_mechanism_rows",
            ],
        },
        "reference_text": "../../1-s2.0-S0377042719305229-main.txt",
        "reference_style_features": reference_features,
        "reference_style_interpretation": (
            "The reference paper proves Lie-group constrained-BDF convergence by first fixing "
            "the Lie-group reconstruction, then proving Taylor local defects, moving global "
            "configuration errors into the Lie algebra, estimating exponential-composition "
            "perturbations, and closing the constrained case with multiplier and coupled-error "
            "recursions.  It informs proof organization only; it does not provide a replacement "
            "for this manuscript's direct residual-bridge/Kantorovich proof route."
        ),
        "manuscript_strict_proof_features": {
            "main": main_features,
            "flat": flat_features,
            "strict_conditional_math_proof_present": strict_conditional_math_proof_present,
        },
        "sidecar_proof_gap_scope_audit": {
            "legacy_key": "proof_manifest_proof_gap_closed",
            "legacy_key_retained_for_schema_compatibility": True,
            "expected_scope": DIRECT_ROUTE_SCOPE,
            "entry_count": len(sidecar_scope_entries),
            "direct_route_scoped_count": sidecar_scope_ok_count,
            "all_legacy_references_direct_route_scoped": (
                len(sidecar_scope_entries) > 0
                and sidecar_scope_ok_count == len(sidecar_scope_entries)
            ),
            "not_primitive_taylor_route_closure": True,
            "not_p6_solver_policy_closure": True,
            "not_p7_residual_to_error_closure": True,
            "not_source_policy_or_output_order_closure": True,
            "entries": sidecar_scope_entries,
        },
        "manuscript_theorem_traceability": {
            "proof_closure_status": proof_closure.get("status"),
            "accepted_theorem_label": theorem_statement_boundary.get("accepted_theorem_label"),
            "accepted_method_order": theorem_statement_boundary.get("accepted_method_order"),
            "accepted_local_defect_order": theorem_statement_boundary.get("accepted_local_defect_order"),
            "theorem_statement_labels_present": theorem_statement_boundary.get(
                "all_required_labels_present_main_and_flat"
            ),
            "conditional_theorem_boundary_present": theorem_statement_boundary.get(
                "conditional_theorem_boundary_present_main_and_flat"
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
            "proof_closure_proof_claim_anchor_maps_match": proof_closure_anchor_map
            == proof_claim_anchor_map,
            "reader_facing_manuscript_boundary_present": proof_writing_card.get(
                "reader_facing_manuscript_boundary_present"
            ),
            "p7_retained_nonpromotion_boundary_present": proof_writing_card.get(
                "p7_retained_nonpromotion_boundary_present"
            ),
            "b1_closure_scope_boundary_present": proof_writing_card.get(
                "b1_closure_scope_boundary_present"
            ),
            "p6_solver_scope_boundary_present": proof_writing_card.get(
                "p6_solver_scope_boundary_present"
            ),
            "p1p2_compact_tube_boundary_present": proof_claim_remaining_boundary.get(
                "p1p2_compact_tube_boundary_present"
            ),
            "p3p4_implementation_boundary_present": proof_writing_card.get(
                "p3p4_implementation_boundary_present"
            ),
            "p5_direct_route_boundary_present": proof_writing_card.get(
                "p5_direct_route_boundary_present"
            ),
            "proof_causality_ledger_present": proof_writing_card.get(
                "proof_causality_ledger_present"
            ),
            "direct_route_anticircularity_ledger_present": proof_writing_card.get(
                "direct_route_anticircularity_ledger_present"
            ),
            "p_interface_satisfaction_ledger_present": proof_writing_card.get(
                "p_interface_satisfaction_ledger_present"
            ),
            "p7_residual_to_error_ledger_present": proof_writing_card.get(
                "p7_residual_to_error_ledger_present"
            ),
            "theorem_use_rule_present": proof_writing_card.get(
                "theorem_use_rule_present"
            ),
            "quantifier_domain_ledger_present": proof_writing_card.get(
                "quantifier_domain_ledger_present"
            ),
            "local_global_transfer_ledger_present": proof_writing_card.get(
                "local_global_transfer_ledger_present"
            ),
            "objective_completion_boundary_present": proof_writing_card.get(
                "objective_completion_boundary_present"
            ),
            "constant_dependency_ledger_present": proof_writing_card.get(
                "constant_dependency_ledger_present"
            ),
            "theorem_dependency_consumption_ledger_present": proof_writing_card.get(
                "theorem_dependency_consumption_ledger_present"
            ),
            "branch_consistency_ledger_present": proof_claim_remaining_boundary.get(
                "branch_consistency_table_present"
            ),
            "implementation_route_oracle_ledger_present": (
                proof_writing_card.get("implementation_route_oracle_ledger_present")
                or proof_writing_card.get("implementation_route_oracle_table_present")
                or proof_claim_remaining_boundary.get("implementation_route_oracle_table_present")
            ),
            "nonlinear_solver_scale_ledger_present": (
                proof_writing_card.get("nonlinear_solver_scale_ledger_present")
                or proof_writing_card.get("nonlinear_solver_scale_table_present")
                or proof_claim_remaining_boundary.get("nonlinear_solver_scale_ledger_present")
                or proof_claim_remaining_boundary.get("nonlinear_solver_scale_table_present")
            ),
            "local_defect_decomposition_ledger_present": proof_writing_card.get(
                "local_defect_decomposition_ledger_present"
            ),
            "theorem_output_scope_ledger_present": proof_writing_card.get(
                "theorem_output_scope_ledger_present"
            ),
            "reporting_map_ledger_present": proof_writing_card.get(
                "reporting_map_ledger_present"
            ),
            "theorem_conclusion_scope_guard_present": proof_writing_card.get(
                "theorem_conclusion_scope_guard_present"
            ),
            "proof_strength_certificate_present": proof_writing_card.get(
                "proof_strength_certificate_present"
            ),
            "full_residual_bridge_present": proof_writing_card.get(
                "full_residual_bridge_present"
            ),
            "anchor_evidence_sources": [
                "PROOF_CLOSURE_MANIFEST.json",
                "PROOF_CLAIM_TRACEABILITY_AUDIT.json",
            ],
            "traceability_role": (
                "reader-facing theorem/proof boundary in main and flat TeX; does not close "
                "eta_h solver-policy theorem, residual-to-error theorem, or source-policy/full-TFE gates"
            ),
        },
        "two_layer_proof_boundary": {
            "b1_status": b1.get("status"),
            "b3_status": b3.get("status"),
            "b3_direct_proof_review_passed": b3_direct_review_passed,
            "b3_closed_by_direct_proof_review": b3.get("status") == "closed",
            "b1_ad_expanded_implementation_oracle_still_open": b1.get("status") == "open",
            "primitive_dynamic_symbolic_oracle_complete": theorem_contract.get(
                "dynamic_symbolic_oracle_complete"
            ),
            "b1_closed_by_ad_expanded_symbolic_certificate": (
                b1.get("status") == "closed"
                and b1_ad_expanded_closure.get("ad_expanded_symbolic_oracle_closure") is True
            ),
            "b1_ad_expanded_symbolic_certificate_schema": b1_ad_expanded_closure.get("schema"),
            "b1_ad_expanded_symbolic_certificate_status": b1_ad_expanded_closure.get("status"),
            "b1_ad_expanded_symbolic_oracle_closure": b1_ad_expanded_closure.get(
                "ad_expanded_symbolic_oracle_closure"
            ),
            "b1_ad_expanded_symbolic_oracle_closed_cells": b1_ad_expanded_closure.get(
                "ad_expanded_symbolic_oracle_closed_cells"
            ),
            "proof_contract_status": proof_contract.get("status"),
            "proof_closure_status": proof_closure.get("status"),
            "proof_style_status": proof_style.get("status"),
            "contract_stage_residual_O_h7_implementation_defect_proved": theorem_contract.get(
                "stage_residual_O_h7_implementation_defect_proved"
            ),
            "direct_route_stage_residual_O_h7": closure_state.get("stage_residual_O_h7_implementation_defect_proved"),
            "direct_route_dynamic_zero_rows": evidence.get("newton_euler_d5_direct_substitution_dynamic_zero_rows"),
            "direct_route_full_stage_rows": evidence.get("newton_euler_d5_direct_substitution_full_stage_rows"),
            "dynamic_symbolic_oracle_complete": theorem_contract.get("dynamic_symbolic_oracle_complete"),
            "runtime_formula_row_oracle_complete": full_formula_oracle.get("runtime_formula_row_oracle_complete"),
            "runtime_ad_oracle_complete": formula_ad_oracle.get("runtime_ad_oracle_complete"),
            "independent_symbolic_row_oracle_complete": dynamic_boundary.get("independent_symbolic_row_oracle_complete"),
            "dynamic_row_oracle_status": dynamic_oracle.get("status"),
            "direct_route_strict_residual_bridge_kantorovich_proof_complete": direct_route_strict_proof_complete,
            "direct_route_strict_proof_scope": "active_direct_residual_bridge_kantorovich_route_for_B1_B3",
            "symbolic_primitive_route_strict_implementation_proof_complete": False,
            "symbolic_primitive_route_scope": "conditional_schema_symbolic_primitive_route_not_active_pc2",
            "two_layer_boundary_consistent": (
                b1.get("status") == "closed"
                and b3.get("status") == "closed"
                and b3_direct_review_passed
                and b1_ad_expanded_closure.get("ad_expanded_symbolic_oracle_closure") is True
                and b1_ad_expanded_closure.get("ad_expanded_symbolic_oracle_closed_cells") == 4752
                and theorem_contract.get("stage_residual_O_h7_implementation_defect_proved") is True
                and closure_state.get("stage_residual_O_h7_implementation_defect_proved") is True
                and theorem_contract.get("dynamic_symbolic_oracle_complete") is False
                and dynamic_boundary.get("independent_symbolic_row_oracle_complete") is False
                and direct_residual_bridge_standard.get("satisfied") is True
                and direct_residual_bridge_standard.get("direct_residual_bridge_kantorovich_route_closed") is True
            ),
        },
        "primitive_taylor_route": {
            "rows": d5_summary.get("dynamic_rows"),
            "terms": d5_summary.get("term_rows"),
            "conditional_rows": d5_summary.get("conditional_dynamic_rows_under_open_primitive_assumptions"),
            "conditional_terms": d5_summary.get("conditional_term_bounds_under_open_primitive_assumptions"),
            "actual_rows_proved": d5_summary.get("actual_dynamic_rows_proved"),
            "actual_terms_proved": d5_summary.get("actual_taylor_bounds_proved"),
            "open_primitive_assumptions": d5_summary.get("open_primitive_assumption_count"),
            "proved_primitive_count": d5_summary.get("proved_primitive_count"),
            "strict_taylor_reduction_terms": term_budget_summary.get("strict_taylor_reduction_terms"),
            "anti_circular_taylor_terms": term_budget_summary.get("anti_circular_taylor_terms"),
            "terms_with_open_primitive_blockers": term_budget_summary.get(
                "terms_with_open_primitive_blockers"
            ),
            "unweighted_acceleration_blocked_terms": term_budget_summary.get(
                "unweighted_acceleration_blocked_terms"
            ),
            "h_weighted_acceleration_sufficient_terms": term_budget_summary.get(
                "h_weighted_acceleration_sufficient_terms"
            ),
            "h_weighted_acceleration_insufficient_terms": term_budget_summary.get(
                "h_weighted_acceleration_insufficient_terms"
            ),
            "primitive_blocker_usage": term_budget_summary.get("primitive_blocker_usage"),
            "taylor_template_usage": term_budget_summary.get("taylor_template_usage"),
            "dependency_graph_recorded": primitive_dependency_graph.get("graph_recorded"),
            "root_lift_primitives": primitive_dependency_graph.get("root_lift_primitives"),
            "root_dependent_primitives": primitive_dependency_graph.get(
                "root_dependent_primitives"
            ),
            "conditional_downstream_primitives": primitive_dependency_graph.get(
                "conditional_downstream_primitives"
            ),
            "dependency_edge_count": len(primitive_dependency_graph.get("dependency_edges", [])),
            "closure_sequence": primitive_dependency_graph.get("closure_sequence"),
            "minimal_next_subproofs": primitive_dependency_graph.get("minimal_next_subproofs"),
            "root_lift_term_row_total": primitive_gap_summary.get("root_lift_term_row_total"),
            "root_dependent_term_row_total": primitive_gap_summary.get(
                "root_dependent_term_row_total"
            ),
            "conditional_downstream_term_row_total": primitive_gap_summary.get(
                "conditional_downstream_term_row_total"
            ),
            "primitive_route_pc2_closed": d5_taylor.get("pc2_closed"),
            "primitive_route_proof_gap_closed": d5_taylor.get("proof_gap_closed"),
            "primitive_route_stage_residual_O_h7_implementation_defect_proved": d5_taylor.get(
                "stage_residual_O_h7_implementation_defect_proved"
            ),
            "conditional_templates_not_additive_proof_evidence": d5_route_separation.get(
                "conditional_templates_not_additive_proof_evidence"
            ),
            "conditional_templates_not_spliced_with_direct_pc2_bridge": d5_route_separation.get(
                "conditional_templates_not_spliced_with_direct_pc2_bridge"
            ),
            "direct_pc2_bridge_does_not_close_primitive_route": d5_route_separation.get(
                "direct_pc2_bridge_does_not_close_primitive_route"
            ),
            "primitive_route_must_prove_five_uniform_lift_primitives": d5_route_separation.get(
                "primitive_route_must_prove_five_uniform_lift_primitives"
            ),
            "primitive_route_must_redo_residual_to_root_endpoint_solver_global_chain": d5_route_separation.get(
                "primitive_route_must_redo_residual_to_root_endpoint_solver_global_chain"
            ),
            "route_separation_scope": d5_route_separation.get("route_separation_scope"),
            "primitive_route_status_scope": "conditional_schema_symbolic_primitive_route_not_active_direct_pc2",
            "route_role": (
                "open conditional primitive/Taylor certificate schema, not the active "
                "direct-substitution closure"
            ),
        },
        "direct_residual_bridge_kantorovich_submission_standard": {
            "manifest_status": direct_residual_bridge_standard.get("status"),
            "required_pc2_route": direct_residual_bridge_standard.get("required_pc2_route"),
            "satisfied": direct_residual_bridge_standard.get("satisfied"),
            "proof_gap_closed_under_active_direct_residual_bridge_standard": direct_residual_bridge_standard.get(
                "proof_gap_closed_under_active_direct_residual_bridge_standard"
            ),
            "not_primitive_162_term_taylor_closure": direct_residual_bridge_standard.get(
                "not_primitive_162_term_taylor_closure"
            ),
            "direct_substitution_supplies_active_pc2_residual_bridge": direct_residual_bridge_standard.get(
                "direct_substitution_supplies_active_pc2_residual_bridge"
            ),
            "current_gate_b3_status": b3.get("status"),
            "b3_should_close_under_active_direct_residual_bridge_standard": True,
            "actual_taylor_bounds_proved": direct_residual_bridge_standard.get("actual_taylor_bounds_proved"),
            "open_taylor_bound_terms": direct_residual_bridge_standard.get("open_taylor_bound_terms"),
            "terms_with_open_primitive_blockers": direct_residual_bridge_standard.get(
                "terms_with_open_primitive_blockers"
            ),
            "open_primitive_count": direct_residual_bridge_standard.get("open_primitive_count"),
            "h_weighted_acceleration_sufficient_terms": direct_residual_bridge_standard.get(
                "h_weighted_acceleration_sufficient_terms"
            ),
            "h_weighted_acceleration_insufficient_terms": direct_residual_bridge_standard.get(
                "h_weighted_acceleration_insufficient_terms"
            ),
            "minimum_required_next_route": direct_residual_bridge_standard.get("minimum_required_next_route"),
            "primitive_route_required_for_b3_closure": direct_residual_bridge_standard.get(
                "primitive_route_required_for_b3_closure"
            ),
            "direct_residual_bridge_kantorovich_route_closed": direct_residual_bridge_standard.get(
                "direct_residual_bridge_kantorovich_route_closed"
            ),
        },
        "direct_route_ps3_corollary": {
            "schema": d5_p_state_ps3_full_route.get("schema"),
            "certificate_closed": d5_p_state_ps3_full_route.get("summary", {}).get(
                "full_residual_route_certificate_closed"
            ),
            "direct_route_ps3_input_closed": d5_p_state_ps3_full_route.get("summary", {}).get(
                "direct_route_ps3_input_closed"
            ),
            "direct_route_state_lift_rate_closed": d5_p_state_ps3_full_route.get("summary", {}).get(
                "direct_route_state_lift_rate_closed"
            ),
            "direct_route_h_weighted_acceleration_input_closed": d5_p_state_ps3_full_route.get(
                "summary", {}
            ).get("direct_route_h_weighted_acceleration_input_closed"),
            "strict_proof_steps_closed": d5_p_state_ps3_full_route.get("summary", {}).get(
                "strict_proof_steps_closed"
            ),
            "strict_proof_steps_total": d5_p_state_ps3_full_route.get("summary", {}).get(
                "strict_proof_steps_total"
            ),
            "primitive_route_closed": d5_p_state_ps3_full_route.get("summary", {}).get(
                "primitive_route_closed"
            ),
            "primitive_route_induced_taylor_bounds_proved": d5_p_state_ps3_full_route.get(
                "summary", {}
            ).get("primitive_route_induced_taylor_bounds_proved"),
            "certifies_primitive_taylor_route": d5_p_state_ps3_full_route.get(
                "certifies_primitive_taylor_route"
            ),
            "uses_velocity_collocation_h_inverse_route": d5_p_state_ps3_full_route.get(
                "non_circularity", {}
            ).get("uses_velocity_collocation_h_inverse_route"),
            "uses_finite_probe_as_proof": d5_p_state_ps3_full_route.get(
                "non_circularity", {}
            ).get("uses_finite_probe_as_proof"),
            "route_role": (
                "strict direct-route PS3 corollary; not an independent primitive/Taylor "
                "route closure and not a B1 implementation-oracle closure"
            ),
        },
        "required_to_close_for_full_source_policy_package_ready": [
            "B4 source-policy publication-grade work/precision evidence if external claims are reintroduced",
            "B6 full source-policy prose/material relocation pass if full package claims are reintroduced",
            "B7 full publication-grade source-policy baseline/work-precision figure set if source-policy claims are reintroduced",
        ],
        "remaining_gate_scope": {
            "narrowed_claim_b4_b6_b7_statuses": {
                "B4": b4.get("status"),
                "B6": b6.get("status"),
                "B7": b7.get("status"),
            },
            "b4_b6_b7_closed_elsewhere_under_narrowed_claim": all(
                item.get("status") == "closed" for item in [b4, b6, b7]
            ),
            "strict_proof_audit_scope": "B1_B3_proof_boundary_only",
            "global_submission_boundaries_retained": [
                "full_source_policy_package_ready",
                "theorem_level_eta_h_solver_policy_evidence",
                "closed_residual_to_error_theorem_for_mechanism_rows",
            ],
        },
        "forbidden_claims": [
            "submission_ready_true",
            "B1_closed_without_ad_expanded_symbolic_certificate",
            "dynamic_symbolic_oracle_complete_true",
            "unconditional_implementation_proof_complete_true",
        ],
    }
    strict_standard = result["direct_residual_bridge_kantorovich_submission_standard"]
    strict_standard["active_standard_name"] = "strict_direct_residual_bridge_submission_standard"
    result["strict_direct_residual_bridge_submission_standard"] = {
        "manifest_status": strict_standard["manifest_status"],
        "required_pc2_route": strict_standard["required_pc2_route"],
        "satisfied": strict_standard["satisfied"],
        "proof_gap_closed_under_active_direct_residual_bridge_standard": strict_standard[
            "proof_gap_closed_under_active_direct_residual_bridge_standard"
        ],
        "direct_substitution_supplies_active_pc2_residual_bridge": strict_standard[
            "direct_substitution_supplies_active_pc2_residual_bridge"
        ],
        "not_primitive_162_term_taylor_closure": strict_standard[
            "not_primitive_162_term_taylor_closure"
        ],
        "direct_residual_bridge_kantorovich_route_closed": strict_standard[
            "direct_residual_bridge_kantorovich_route_closed"
        ],
        "primitive_route_required_for_b3_closure": strict_standard[
            "primitive_route_required_for_b3_closure"
        ],
        "primitive_taylor_actual_bounds_proved": strict_standard["actual_taylor_bounds_proved"],
        "primitive_taylor_open_bound_terms": strict_standard["open_taylor_bound_terms"],
        "primitive_taylor_open_primitive_count": strict_standard["open_primitive_count"],
    }

    lines = [
        "# CMAME Strict Proof Audit",
        "",
        "Status: **strict conditional residual-bridge proof audited; global proof-package submission not ready**.",
        "Here `submission_ready=false` is scoped to the strict-proof/global proof-package boundary,",
        "not to the separate narrowed-claim package decision.",
        "",
        "This read-only audit responds to the proof-standard concern by separating",
        "the direct residual-bridge/Kantorovich proof route in the manuscript from the",
        "implementation-level symbolic oracle, now closed for B1 by the AD-expanded",
        "symbolic closure certificate.",
        "",
        "## Reference Style Read",
        "",
        "- Reference text: `../../1-s2.0-S0377042719305229-main.txt`.",
        f"- BLieDF/convergence sections present: `{reference_features['bliedf_section_present']}/{reference_features['convergence_section_present']}`.",
        f"- Taylor local-error lemma and constrained local-error theorem present: `{reference_features['taylor_local_error_lemma_present']}/{reference_features['constrained_local_error_theorem_present']}`.",
        f"- Lie-algebra global-error and BCH perturbation structure present: `{reference_features['lie_algebra_global_error_present']}/{reference_features['bch_perturbation_present']}`.",
        f"- Constraint multiplier estimate and coupled recursion present: `{reference_features['constraint_multiplier_estimate_present']}/{reference_features['coupled_error_recursion_present']}`.",
        f"- BDF order boundary and appendix proof present: `{reference_features['bdf_order_boundary_present']}/{reference_features['appendix_proof_present']}`.",
        f"- Reference no-estimate-transfer table present: `{main_features['reference_no_estimate_transfer_ledger']}`.",
        f"- Reference role-separation locks present: `{main_features['reference_not_tfe_comparator']}/{main_features['reference_disjoint_roles']}/{main_features['reference_ordering_template_not_literal_transfer']}/{main_features['reference_no_fullva_residual_taylor_constant']}/{main_features['reference_no_one_step_gauss_theorem']}/{main_features['reference_diagnostics_after_theorem_boundary']}`.",
        f"- Reference technical/start-value boundary present: `{main_features['reference_technical_startvalue_boundary']}/{main_features['reference_technical_assumptions_mapped_to_domain']}/{main_features['reference_no_retroactive_diagnostic_verification']}/{main_features['reference_technical_theorem_contract_boundary']}/{main_features['reference_technical_theorem_contract_replacement']}`.",
        f"- Reference forbidden-transfer/replacement columns present: `{main_features['reference_forbidden_transfer_column']}/{main_features['reference_replacement_column']}`.",
        f"- Reference imported-estimate locks present: `{main_features['reference_no_bdf_premise']}/{main_features['reference_no_bch_constants']}/{main_features['reference_no_multiplier_history_import']}`.",
        f"- Reference proof-order transfer locks present: `{main_features['reference_proof_order_not_estimate_transfer']}/{main_features['reference_direct_bridge_supplies_formula_residual']}/{main_features['reference_no_primitive_fullva_subterm_bound_imported']}`.",
        f"- Constraint-multiplier/reaction output fence present: `{main_features['constraint_multiplier_reaction_output_fence']}/{main_features['multiplier_step_not_theorem_output']}/{main_features['stage_multipliers_algebraic_unknowns']}/{main_features['multipliers_enter_only_through_residual_bridge']}/{main_features['no_multiplier_reaction_h6_estimate']}/{main_features['separate_multiplier_reaction_theorem_required']}/{main_features['reaction_residuals_not_multiplier_order_claim']}`.",
        f"- Residual-bridge handoff present: `{main_features['proof_obligation_closure_narrative']}/{main_features['p5_direct_dynamic_row_identity']}/{main_features['p1p2p3_p4binding_p6_retained_conditions']}/{main_features['p7_residual_to_error_deliberately_not_used']}/{main_features['strong_but_conditional_theorem']}`.",
        "",
        "## Manuscript Strict-Proof Features",
        "",
        f"- Strict conditional residual-bridge proof present: `{strict_conditional_math_proof_present}`.",
        f"- Reference-to-FullVA translation map present: `{main_features['reference_fullva_translation_checkpoint']}/{main_features['reference_partial_order_obligations']}/{main_features['reference_r1_fixed_discrete_object']}/{main_features['reference_r2_smooth_branch_same_object']}/{main_features['reference_r3_fixed_object_defect_conversion']}/{main_features['reference_r4_stability_after_local_defect']}/{main_features['reference_right_hand_independent']}/{main_features['reference_does_not_repair_failed_lemma']}/{main_features['reference_dependency_graph_not_premise']}`.",
        f"- Reference constrained-DAE slot map present: `{main_features['reference_constrained_dae_slot_checkpoint']}/{main_features['reference_two_distinct_dae_slots']}/{main_features['reference_constraint_difference_multiplier_slot']}/{main_features['reference_local_defect_slot_full_bridge']}/{main_features['reference_constrained_dae_slot_fullva']}/{main_features['reference_multipliers_stage_unknowns_not_histories']}/{main_features['reference_no_bypass_constraint_layer']}/{main_features['reference_slot_analogy_not_symmetric']}/{main_features['reference_bdf_hidden_constraint_not_fullva_certificate']}/{main_features['reference_direct_bridge_not_multiplier_history_theorem']}`.",
        f"- Named theorem-domain clauses present: `{main_features['method_endpoint_p2_controlled']}/{main_features['method_endpoint_diagnostics_separate']}/{main_features['theorem_named_clauses']}/{main_features['theorem_p1_smooth_lift_clause']}/{main_features['theorem_p2_endpoint_inverse_clause']}/{main_features['theorem_p3_implementation_clause']}/{main_features['theorem_p4_only_96_rows']}/{main_features['theorem_p5_only_direct_36_rows']}/{main_features['theorem_p6_only_solver_envelope']}/{main_features['theorem_clauses_not_inferred_from_diagnostics']}`.",
        f"- Theorem input-output direction locks present: `{main_features['theorem_input_output_reading_rule']}/{main_features['theorem_no_backward_arrows']}/{main_features['theorem_reported_run_only_specializes']}/{main_features['theorem_no_retroactive_instance_change']}`.",
        f"- Theorem residual-certificate exclusivity locks present: `{main_features['theorem_one_residual_certificate']}/{main_features['theorem_future_t3_same_tuple_replacement']}/{main_features['theorem_no_append_lower_remove_promote']}`.",
        f"- Proof-gap closure scope locks present: `{main_features['proof_gap_token_scope_checkpoint']}/{main_features['proof_gap_token_direct_pc2_only']}/{main_features['proof_gap_token_not_p6_p7_primitive']}/{main_features['proof_gap_token_not_extra_assumption']}`.",
        f"- D5 sidecar proof-gap legacy keys direct-route scoped: `{sidecar_scope_ok_count}/{len(sidecar_scope_entries)}`; primitive/P6/P7/source-policy nonclosure retained: `{result['sidecar_proof_gap_scope_audit']['not_primitive_taylor_route_closure']}/{result['sidecar_proof_gap_scope_audit']['not_p6_solver_policy_closure']}/{result['sidecar_proof_gap_scope_audit']['not_p7_residual_to_error_closure']}/{result['sidecar_proof_gap_scope_audit']['not_source_policy_or_output_order_closure']}`.",
        f"- Same-object closure locks present: `{main_features['same_object_closure_criterion']}/{main_features['same_object_branch_row_norm_endpoint_agree']}/{main_features['same_object_no_cross_branch_splicing']}/{main_features['same_object_jointly_admissible_tuple']}`.",
        f"- Same-object typed-slot composition locks present: `{main_features['same_object_reference_c1_c4_slots']}/{main_features['same_object_c1_c3_declared_residual']}/{main_features['same_object_different_typed_object']}/{main_features['same_object_equivalence_transport_required']}`.",
        f"- Stage Taylor expansion token present: `{main_features['stage_taylor_expansion']}`.",
        f"- Taylor accounting rule present: `{main_features['taylor_accounting_rule']}/{main_features['taylor_fixed_before_expansion']}/{main_features['taylor_constants_compact_tube_only']}/{main_features['taylor_t2_variable_delta']}/{main_features['taylor_zero_rows_before_full_map']}/{main_features['taylor_no_t2_to_prove_primitives']}`.",
        f"- Taylor same-object/no-reverse boundary present: `{main_features['taylor_same_object_transport_gate']}/{flat_features['taylor_same_object_transport_gate']}/{main_features['taylor_same_mathematical_object']}/{main_features['taylor_transport_fullva_stage_variables']}/{main_features['taylor_transport_not_t3_input']}/{main_features['taylor_no_reverse_inference_lemma']}/{flat_features['taylor_no_reverse_inference_lemma']}/{main_features['taylor_no_reverse_global_estimate']}/{main_features['taylor_no_reverse_does_not_prove_primitives']}`.",
        f"- Taylor projection checkpoint present: `{main_features['taylor_projection_checkpoint']}/{main_features['taylor_aggregate_fixed_block_norm']}/{main_features['taylor_not_projection_certificate_162']}/{main_features['taylor_primitive_projection_operator']}/{main_features['taylor_projection_right_inverse_needed']}/{main_features['taylor_independent_primitive_lift_bounds']}/{main_features['taylor_no_projection_right_inverse_used']}/{main_features['taylor_t2_closed_while_primitive_separate']}`.",
        f"- Taylor no-splicing boundary present: `{main_features['taylor_counts_not_additive_proof_evidence']}/{main_features['taylor_templates_not_spliced_with_pc2']}/{main_features['taylor_primitive_route_must_prove_five_obligations']}/{main_features['taylor_primitive_route_must_redo_chain']}`.",
        f"- Taylor route-exclusivity refinement present: `{main_features['taylor_route_exclusivity_refinement']}/{main_features['taylor_route_same_branch_tuple']}/{main_features['taylor_route_future_t3_own_cr']}/{main_features['taylor_route_cannot_lower_constants']}/{main_features['taylor_route_cannot_remove_p6']}/{main_features['taylor_route_cannot_promote_p7']}/{main_features['taylor_route_one_residual_certificate']}/{main_features['taylor_route_never_mixes_partial']}`.",
        f"- Same-object direct-substitution calculation present: `{main_features['same_object_direct_substitution_calculation']}/{main_features['same_object_block_residual']}/{main_features['same_object_dynamic_zero_block']}/{main_features['same_object_stage_root_equation']}/{main_features['same_object_endpoint_bound']}/{main_features['same_object_no_imported_fitted_primitive_constants']}`.",
        f"- Taylor finite-implication formal statements present: `{main_features['taylor_conditional_implication_prop']}/{flat_features['taylor_conditional_implication_prop']}/{main_features['taylor_conditional_implication_lemma']}/{flat_features['taylor_conditional_implication_lemma']}/{main_features['taylor_conditional_not_pc2_input']}/{flat_features['taylor_conditional_not_pc2_input']}`.",
        f"- Endpoint diagnostic-scope checkpoint present: `{main_features['endpoint_diagnostic_scope_checkpoint']}/{main_features['endpoint_order_fit_not_hypothesis_source']}/{main_features['endpoint_fixed_compact_tube_data_before_table']}/{main_features['endpoint_raw_position_slope_no_contradiction']}/{main_features['endpoint_small_raw_position_no_discharge']}/{main_features['endpoint_table_consistency_diagnostic_only']}`.",
        f"- Quadratic remainder token present: `{main_features['quadratic_remainder']}`.",
        f"- Newton--Kantorovich absorption present: `{main_features['newton_kantorovich_absorption']}`.",
        f"- Contraction radius present: `{main_features['contraction_radius']}`.",
        f"- Quantitative stage-error bound present: `{main_features['stage_error_bound']}`.",
        f"- Stage single-instance locks present: `{main_features['stage_single_instance_requirement']}/{main_features['stage_same_fixed_residual_map_norm']}`.",
        f"- Inexact Newton mean-value proof present: `{main_features['mean_value_residual']}`.",
        f"- Inexact Newton branch-ball checkpoint present: `{main_features['inexact_branch_ball_checkpoint']}/{main_features['inexact_two_independent_solver_facts']}/{main_features['inexact_iterate_certified_in_ball']}/{main_features['inexact_residual_envelope_fixed_norm']}/{main_features['inexact_residual_cannot_replace_membership']}/{main_features['inexact_log_not_theorem_input']}/{main_features['inexact_same_gauss_predictor_branch']}/{main_features['inexact_not_larger_constant_or_lower_order']}`.",
        f"- P6 conditional-instantiation checkpoint present: `{main_features['p6_conditional_instantiation_checkpoint']}/{main_features['p6_operational_sufficient_instantiation']}/{main_features['p6_fixed_norm_scaling_branch_rule']}/{main_features['p6_same_gauss_predictor_branch_certified']}/{main_features['p6_proof_norm_stopping_target']}/{main_features['p6_reported_grid_specialization']}/{main_features['p6_sufficient_not_empirical_discharge']}/{main_features['p6_no_theorem_level_solver_evidence']}/{main_features['p6_no_residual_ratio_fitting']}/{main_features['p6_no_global_newton_remote_root']}`.",
        f"- P6 evidence-grade rule present: `{main_features['p6_evidence_grade_rule']}/{main_features['p6_only_one_theorem_grade_input']}/{main_features['p6_predeclared_same_branch_residual_envelope']}/{main_features['p6_diagnostic_grade_evidence_only']}/{main_features['p6_log_specializes_not_creates']}`.",
        f"- P6 proof-norm/no-reweighting checkpoint present: `{main_features['p6_no_hidden_h_dependent_row_weights']}/{main_features['p6_h_independent_norm_equivalence']}/{main_features['p6_explicit_residual_h_factor_binding']}/{main_features['p6_small_residual_wrong_norm_not_input']}`.",
        f"- Stability-map binding checkpoint present: `{main_features['stability_map_binding_checkpoint']}/{main_features['stability_map_is_g6fullva']}/{main_features['stability_same_branch_proof_norm']}/{main_features['exact_stage_maps_local_defect_only']}/{main_features['no_exact_stage_stability_substitution']}/{main_features['stability_constant_accepted_map']}/{main_features['single_g6fullva_recurrence']}/{main_features['no_hidden_map_switch']}`.",
        f"- Reference-style proof invariant present: `{main_features['reference_proof_invariant_checkpoint']}/{main_features['reference_invariant_fixed_fullva']}/{main_features['reference_invariant_same_branch_residual']}/{main_features['reference_invariant_no_bdf_import']}/{main_features['reference_invariant_no_downstream_backfill']}`.",
        f"- Reference-style recursion analogue present: `{main_features['reference_recursion_analogue_checkpoint']}/{main_features['reference_recursion_structural_not_estimate']}/{main_features['reference_recursion_fullva_variables_consumed']}/{main_features['reference_recursion_no_hidden_multiplier']}/{main_features['reference_recursion_separate_output']}`.",
        f"- Truncated first-exit recursion checkpoint present: `{main_features['local_global_truncated_first_exit_checkpoint']}/{main_features['local_global_truncated_index']}/{main_features['local_global_truncated_only_before_exit']}/{main_features['local_global_no_post_exit_estimates']}/{main_features['local_global_exit_contradiction']}/{main_features['local_global_extend_after_exit_excluded']}`.",
        f"- Time-augmentation local-to-global checkpoint present: `{main_features['local_global_time_augmentation_checkpoint']}/{main_features['local_global_augmented_chart']}/{main_features['local_global_tau_dot_one']}/{main_features['local_global_exact_time_advance']}/{main_features['local_global_time_zero_error']}/{main_features['local_global_two_parameter_flow']}/{main_features['local_global_no_time_phase_mismatch']}/{main_features['local_global_augmented_semigroup_identity']}`.",
        f"- Synchronized-time stability slice present: `{main_features['local_global_synchronized_time_slice']}/{main_features['local_global_same_input_time_slice']}/{main_features['local_global_tau_n_equals_t_n']}/{main_features['local_global_exact_next_time']}/{main_features['local_global_no_time_registration_error']}/{main_features['local_global_no_different_time_phases']}/{main_features['local_global_no_time_shifted_fit']}/{main_features['local_global_time_indexed_map']}`.",
        f"- Reporting-map convex chart checkpoint present: `{main_features['reporting_convex_chart_checkpoint']}/{main_features['reporting_fixed_convex_neighborhood']}/{main_features['reporting_u_k_derivative_supremum']}/{main_features['reporting_no_convex_k_assumption']}/{main_features['reporting_segments_inside_uk']}/{main_features['reporting_one_euclidean_chart']}/{main_features['reporting_no_atlas_switch']}/{main_features['reporting_no_fitted_norm_equivalence']}`.",
        f"- Order-accounting checkpoint present: `{main_features['order_accounting_checkpoint']}/{main_features['order_accounting_local_h7_global_h6']}/{main_features['order_accounting_nh_inverse']}/{main_features['order_accounting_sixth_order_grid_bound']}/{main_features['order_accounting_observed_slopes_downstream']}/{main_features['order_accounting_not_seventh_order']}/{main_features['order_accounting_stronger_claim_requires_new_theorem']}`.",
        f"- Discrete Gronwall global step present: `{main_features['discrete_gronwall_step']}`.",
        f"- Direct-route state-block corollary present: `{main_features['p_state_ps3_full_residual_route']}`.",
        f"- Direct-route residual decomposition boundary present: `{main_features['direct_route_residual_decomposition']}`.",
        f"- Primitive 162-subterm Taylor route not certified: `{main_features['primitive_162_subterm_boundary']}`.",
        f"- Primitive Taylor bounds not established on theorem route: `{main_features['primitive_taylor_bounds_not_established']}`.",
        f"- 36 h-weighted acceleration primitive terms remain insufficient: `{main_features['h_weighted_acceleration_terms_insufficient']}`.",
        "",
        "## Manuscript Theorem Traceability",
        "",
        f"- Theorem labels/boundary/mapped: `{result['manuscript_theorem_traceability']['theorem_statement_labels_present']}/{result['manuscript_theorem_traceability']['conditional_theorem_boundary_present']}/{result['manuscript_theorem_traceability']['conditional_proof_claims_mapped_to_manuscript']}`.",
        f"- Proof dependency/traceability/dynamic matrix: `{result['manuscript_theorem_traceability']['proof_dependency_graph_present']}/{result['manuscript_theorem_traceability']['proof_traceability_table_present']}/{result['manuscript_theorem_traceability']['dynamic_proof_closure_matrix_present']}`.",
        f"- Primitive-route and residual scope boundaries: `{result['manuscript_theorem_traceability']['primitive_lane_boundary_present']}/{result['manuscript_theorem_traceability']['residual_nonpromotion_present']}`.",
        f"- Eta condition/closure and fixed-tolerance proof: `{result['manuscript_theorem_traceability']['eta_h_theorem_condition_retained']}/{result['manuscript_theorem_traceability']['eta_h_solver_policy_evidence_closed']}/{result['manuscript_theorem_traceability']['fixed_tolerance_runs_are_asymptotic_proof']}`.",
        f"- Residual/source-policy-full-TFE not promoted: `{result['manuscript_theorem_traceability']['residual_to_error_not_promoted']}/{result['manuscript_theorem_traceability']['source_policy_or_full_tfe_not_promoted']}`; no-state-change `{result['manuscript_theorem_traceability']['does_not_change_proof_closure_state']}`.",
        f"- Proof-closure manuscript anchor map: `{result['manuscript_theorem_traceability']['manuscript_anchor_map_present']}`; label anchors `{result['manuscript_theorem_traceability']['manuscript_anchor_label_count']}`; theorem-interface/P7-output-boundary anchors `{result['manuscript_theorem_traceability']['theorem_assumption_anchor_count']}`; IDs `{','.join(result['manuscript_theorem_traceability']['theorem_assumption_anchor_ids'])}`; proof-claim map match `{result['manuscript_theorem_traceability']['proof_closure_proof_claim_anchor_maps_match']}`.",
        "- Reader-facing theorem-interface split: theorem interfaces `P1--P6`; P7 is an output nonclaim/residual-to-error boundary anchor, not a theorem premise.",
        f"- Reader-facing proof-claim boundary present in manuscript/PDF text: `{result['manuscript_theorem_traceability']['reader_facing_manuscript_boundary_present']}`.",
        f"- P7 output nonclaim/residual-to-error boundary present in manuscript: `{result['manuscript_theorem_traceability']['p7_retained_nonpromotion_boundary_present']}`.",
        f"- B1 closure-scope boundary present in manuscript/PDF text: `{result['manuscript_theorem_traceability']['b1_closure_scope_boundary_present']}`.",
        f"- P6 solver-scope boundary present in manuscript/PDF text: `{result['manuscript_theorem_traceability']['p6_solver_scope_boundary_present']}`.",
        f"- P1/P2 compact-tube boundary present in manuscript/PDF text: `{result['manuscript_theorem_traceability']['p1p2_compact_tube_boundary_present']}`.",
        f"- P3/P4 implementation-defect boundary present in manuscript/PDF text: `{result['manuscript_theorem_traceability']['p3p4_implementation_boundary_present']}`.",
        f"- P5 direct-route boundary present in manuscript/PDF text: `{result['manuscript_theorem_traceability']['p5_direct_route_boundary_present']}`.",
        f"- Proof-causality table present in manuscript/PDF text: `{result['manuscript_theorem_traceability']['proof_causality_ledger_present']}`.",
        f"- Direct-route anti-circularity table present in manuscript/PDF text: `{result['manuscript_theorem_traceability']['direct_route_anticircularity_ledger_present']}`.",
        f"- Theorem-interface satisfaction table present in manuscript/PDF text: `{result['manuscript_theorem_traceability']['p_interface_satisfaction_ledger_present']}`.",
        f"- Residual-to-error transfer-scope exclusion table present in manuscript/PDF text: `{result['manuscript_theorem_traceability']['p7_residual_to_error_ledger_present']}`.",
        f"- Auxiliary-evidence scope present in manuscript/PDF text: `{result['manuscript_theorem_traceability']['theorem_use_rule_present']}`.",
        f"- Quantifier/domain table present in manuscript/PDF text: `{result['manuscript_theorem_traceability']['quantifier_domain_ledger_present']}`.",
        f"- Local-to-global transfer table present in manuscript/PDF text: `{result['manuscript_theorem_traceability']['local_global_transfer_ledger_present']}`.",
        f"- Objective-completion boundary present in manuscript/PDF text: `{result['manuscript_theorem_traceability']['objective_completion_boundary_present']}`.",
        f"- Constant-dependency table present in manuscript/PDF text: `{result['manuscript_theorem_traceability']['constant_dependency_ledger_present']}`.",
        f"- Theorem dependency consumption table present in manuscript/PDF text: `{result['manuscript_theorem_traceability']['theorem_dependency_consumption_ledger_present']}`.",
        f"- Accepted-branch consistency table present in manuscript/PDF text: `{result['manuscript_theorem_traceability']['branch_consistency_ledger_present']}`.",
        f"- Implementation-route/certificate separation table present in manuscript/PDF text: `{result['manuscript_theorem_traceability']['implementation_route_oracle_ledger_present']}`.",
        f"- Nonlinear-solver scale table present in manuscript/PDF text: `{result['manuscript_theorem_traceability']['nonlinear_solver_scale_ledger_present']}`.",
        f"- Local-defect decomposition table present in manuscript/PDF text: `{result['manuscript_theorem_traceability']['local_defect_decomposition_ledger_present']}`.",
        f"- Theorem output scope table present in manuscript/PDF text: `{result['manuscript_theorem_traceability']['theorem_output_scope_ledger_present']}`.",
        f"- Reporting-map/norm-equivalence table present in manuscript/PDF text: `{result['manuscript_theorem_traceability']['reporting_map_ledger_present']}`.",
        f"- Scope-of-conclusion statement present in manuscript/PDF text: `{result['manuscript_theorem_traceability']['theorem_conclusion_scope_guard_present']}`.",
        f"- Proof-structure statement present in manuscript/PDF text: `{result['manuscript_theorem_traceability']['proof_strength_certificate_present']}`.",
        f"- Full 132-row residual-defect bridge present in manuscript/PDF text: `{result['manuscript_theorem_traceability']['full_residual_bridge_present']}`.",
        f"- Anchor evidence sources: `{','.join(result['manuscript_theorem_traceability']['anchor_evidence_sources'])}`.",
        "",
        "## Two-Layer Boundary",
        "",
        f"- B3 closed by direct proof review: `{result['two_layer_proof_boundary']['b3_closed_by_direct_proof_review']}`.",
        f"- B3 direct proof review passed: `{result['two_layer_proof_boundary']['b3_direct_proof_review_passed']}`.",
        f"- B1 AD-expanded implementation oracle still open: `{result['two_layer_proof_boundary']['b1_ad_expanded_implementation_oracle_still_open']}`.",
        f"- Primitive/global dynamic symbolic oracle complete: `{result['two_layer_proof_boundary']['primitive_dynamic_symbolic_oracle_complete']}`.",
        f"- B1 closed by AD-expanded symbolic certificate: `{result['two_layer_proof_boundary']['b1_closed_by_ad_expanded_symbolic_certificate']}`.",
        f"- B1 AD-expanded symbolic closure/cells: `{result['two_layer_proof_boundary']['b1_ad_expanded_symbolic_oracle_closure']}/{result['two_layer_proof_boundary']['b1_ad_expanded_symbolic_oracle_closed_cells']}`.",
        f"- Contract-level implementation defect proved: `{result['two_layer_proof_boundary']['contract_stage_residual_O_h7_implementation_defect_proved']}`.",
        f"- Direct-route stage residual O(h^7): `{result['two_layer_proof_boundary']['direct_route_stage_residual_O_h7']}`.",
        f"- Direct-route dynamic/full rows: `{result['two_layer_proof_boundary']['direct_route_dynamic_zero_rows']}/{result['two_layer_proof_boundary']['direct_route_full_stage_rows']}`.",
        f"- Direct residual-bridge/Kantorovich proof complete: `{result['two_layer_proof_boundary']['direct_route_strict_residual_bridge_kantorovich_proof_complete']}`.",
        f"- Symbolic/primitive implementation proof complete: `{result['two_layer_proof_boundary']['symbolic_primitive_route_strict_implementation_proof_complete']}`.",
        f"- Dynamic symbolic oracle complete: `{result['two_layer_proof_boundary']['dynamic_symbolic_oracle_complete']}`.",
        f"- Two-layer boundary consistent: `{result['two_layer_proof_boundary']['two_layer_boundary_consistent']}`.",
        "",
        "## Primitive Taylor Route",
        "",
        f"- Rows/terms: `{result['primitive_taylor_route']['rows']}/{result['primitive_taylor_route']['terms']}`.",
        f"- Conditional rows/terms: `{result['primitive_taylor_route']['conditional_rows']}/{result['primitive_taylor_route']['conditional_terms']}`.",
        f"- Actual terms proved: `{result['primitive_taylor_route']['actual_terms_proved']}`.",
        f"- Open primitive assumptions: `{result['primitive_taylor_route']['open_primitive_assumptions']}`.",
        f"- Primitive/Taylor reductions: `{result['primitive_taylor_route']['strict_taylor_reduction_terms']}/162`.",
        f"- Anti-circular Taylor terms: `{result['primitive_taylor_route']['anti_circular_taylor_terms']}/162`.",
        f"- Terms blocked by open primitives: `{result['primitive_taylor_route']['terms_with_open_primitive_blockers']}/162`.",
        f"- Unweighted acceleration blockers: `{result['primitive_taylor_route']['unweighted_acceleration_blocked_terms']}/36`.",
        f"- h-weighted acceleration sufficient terms: `{result['primitive_taylor_route']['h_weighted_acceleration_sufficient_terms']}`.",
        f"- Primitive dependency graph recorded: `{result['primitive_taylor_route']['dependency_graph_recorded']}`.",
        f"- Root lift primitives: `{result['primitive_taylor_route']['root_lift_primitives']}`.",
        f"- Root-dependent conditional primitives: `{result['primitive_taylor_route']['root_dependent_primitives']}`.",
        f"- Conditional downstream primitives: `{result['primitive_taylor_route']['conditional_downstream_primitives']}`.",
        f"- Dependency edges: `{result['primitive_taylor_route']['dependency_edge_count']}`.",
        f"- Closure sequence: `{result['primitive_taylor_route']['closure_sequence']}`.",
        f"- Root, root-dependent, and downstream term-row totals: `{result['primitive_taylor_route']['root_lift_term_row_total']}/{result['primitive_taylor_route']['root_dependent_term_row_total']}/{result['primitive_taylor_route']['conditional_downstream_term_row_total']}`.",
        f"- PC2 closed by primitive route: `{result['primitive_taylor_route']['primitive_route_pc2_closed']}`.",
        f"- Primitive-route proof gap closed: `{result['primitive_taylor_route']['primitive_route_proof_gap_closed']}`.",
        f"- Primitive-route stage residual O(h^7) proved: `{result['primitive_taylor_route']['primitive_route_stage_residual_O_h7_implementation_defect_proved']}`.",
        "- Primitive-route reading rule: `False` here means the conditional primitive/Taylor certificate schema has no current instance, not the active PC2 status; the active PC2 residual-bridge proof is reported in the direct-route block below.",
        f"- D5 route-separation locks: `{result['primitive_taylor_route']['conditional_templates_not_additive_proof_evidence']}/{result['primitive_taylor_route']['conditional_templates_not_spliced_with_direct_pc2_bridge']}/{result['primitive_taylor_route']['direct_pc2_bridge_does_not_close_primitive_route']}/{result['primitive_taylor_route']['primitive_route_must_prove_five_uniform_lift_primitives']}/{result['primitive_taylor_route']['primitive_route_must_redo_residual_to_root_endpoint_solver_global_chain']}`.",
        f"- D5 route-separation scope: `{result['primitive_taylor_route']['route_separation_scope']}`.",
        "",
        "## Direct-Route Residual-Bridge Proof Contract",
        "",
        f"- Active direct residual-bridge proof standard: `{result['strict_direct_residual_bridge_submission_standard']['required_pc2_route']}`.",
        f"- Manifest status: `{result['strict_direct_residual_bridge_submission_standard']['manifest_status']}`.",
        f"- Required PC2 route: `{result['strict_direct_residual_bridge_submission_standard']['required_pc2_route']}`.",
        f"- Direct residual-bridge proof contract satisfied: `{result['strict_direct_residual_bridge_submission_standard']['satisfied']}`.",
        f"- Direct PC2 proof gap closed under active residual-bridge contract: `{result['strict_direct_residual_bridge_submission_standard']['proof_gap_closed_under_active_direct_residual_bridge_standard']}`.",
        f"- Direct substitution supplies the active PC2 residual-bridge proof input: `{result['strict_direct_residual_bridge_submission_standard']['direct_substitution_supplies_active_pc2_residual_bridge']}`.",
        f"- Not primitive 162-term Taylor closure: `{result['strict_direct_residual_bridge_submission_standard']['not_primitive_162_term_taylor_closure']}`.",
        f"- Current B3 direct-route status: `{result['direct_residual_bridge_kantorovich_submission_standard']['current_gate_b3_status']}`.",
        f"- B3 should close under active residual-bridge standard: `{result['direct_residual_bridge_kantorovich_submission_standard']['b3_should_close_under_active_direct_residual_bridge_standard']}`.",
        f"- Primitive/Taylor actual/open terms: `{result['strict_direct_residual_bridge_submission_standard']['primitive_taylor_actual_bounds_proved']}` / `{result['strict_direct_residual_bridge_submission_standard']['primitive_taylor_open_bound_terms']}`.",
        f"- Primitive/Taylor open primitive count: `{result['strict_direct_residual_bridge_submission_standard']['primitive_taylor_open_primitive_count']}`.",
        "",
        "## Direct-Route PS3 Corollary",
        "",
        f"- Full residual route certificate closed for direct-route PS3 corollary only: `{result['direct_route_ps3_corollary']['certificate_closed']}`.",
        f"- Direct-route PS3 corollary closed, not primitive P_state closure: `{result['direct_route_ps3_corollary']['direct_route_ps3_input_closed']}`.",
        f"- Direct-route state/h-acceleration corollary rates closed, not primitive lifts: `{result['direct_route_ps3_corollary']['direct_route_state_lift_rate_closed']}/{result['direct_route_ps3_corollary']['direct_route_h_weighted_acceleration_input_closed']}`.",
        f"- Direct-route strict proof steps closed: `{result['direct_route_ps3_corollary']['strict_proof_steps_closed']}/{result['direct_route_ps3_corollary']['strict_proof_steps_total']}`.",
        f"- Primitive route closed by corollary: `{result['direct_route_ps3_corollary']['primitive_route_closed']}`.",
        f"- Primitive-route induced Taylor bounds proved by corollary: `{result['direct_route_ps3_corollary']['primitive_route_induced_taylor_bounds_proved']}/162`.",
        f"- Uses velocity-collocation h-inverse route: `{result['direct_route_ps3_corollary']['uses_velocity_collocation_h_inverse_route']}`.",
        f"- Uses finite probe as proof: `{result['direct_route_ps3_corollary']['uses_finite_probe_as_proof']}`.",
        "",
        "## Remaining Gate",
        "",
        f"- Submission-ready scope: `{result['submission_ready_scope']}`.",
        f"- Strict proof audit scope: `{result['readiness_boundary']['strict_proof_audit_scope']}`.",
        "- B1 is closed by `B1_AD_EXPANDED_SYMBOLIC_ORACLE_CLOSURE_CERTIFICATE.md`; this audit scopes only the B1/B3 proof boundary.",
        f"- Narrowed-claim B4/B6/B7 subcheck statuses are recorded elsewhere (narrowed-only; not source-policy row closure): `{result['remaining_gate_scope']['narrowed_claim_b4_b6_b7_statuses']['B4']}/{result['remaining_gate_scope']['narrowed_claim_b4_b6_b7_statuses']['B6']}/{result['remaining_gate_scope']['narrowed_claim_b4_b6_b7_statuses']['B7']}`.",
        f"- Remaining global submission boundaries: `{','.join(result['remaining_gate_scope']['global_submission_boundaries_retained'])}`.",
        "- `submission_ready=false`.",
    ]

    OUT_JSON.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("cmame_strict_proof_audit=written")
    print(f"strict_conditional_residual_bridge_proof_present={strict_conditional_math_proof_present}")
    print(f"two_layer_boundary_consistent={result['two_layer_proof_boundary']['two_layer_boundary_consistent']}")
    print("submission_ready=False")


if __name__ == "__main__":
    main()
