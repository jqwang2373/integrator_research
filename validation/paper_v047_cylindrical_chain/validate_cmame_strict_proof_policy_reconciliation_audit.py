#!/usr/bin/env python3
"""Validate the strict-proof policy reconciliation audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
ROOT = PAPER.parent.parent
AUDIT_JSON = PAPER / "CMAME_STRICT_PROOF_POLICY_RECONCILIATION_AUDIT.json"
AUDIT_MD = PAPER / "CMAME_STRICT_PROOF_POLICY_RECONCILIATION_AUDIT.md"
REF_TXT = ROOT / "external" / "literature" / "1-s2.0-S0377042719305229-main.txt"
BLOCKER = PAPER / "CMAME_BLOCKER_CLOSURE_GATE.json"
PROOF_CLOSURE = PAPER / "PROOF_CLOSURE_MANIFEST.json"
PROOF_CLAIM_TRACEABILITY = PAPER / "PROOF_CLAIM_TRACEABILITY_AUDIT.json"
STRICT_AUDIT = PAPER / "CMAME_STRICT_PROOF_AUDIT.json"
PROOF_CONTRACT = PAPER / "CMAME_PROOF_CONTRACT_GATE.json"
PROOF_STYLE = PAPER / "CMAME_PROOF_STYLE_AUDIT.json"
B3_REVIEW = PAPER / "B3_DIRECT_PROOF_REVIEW_AUDIT.json"
D5_TAYLOR = PAPER / "D5_CONDITIONAL_TAYLOR_CERTIFICATE.json"
D5_BUDGET = PAPER / "D5_TAYLOR_TERM_BUDGET_AUDIT.json"
D5_PLAN = PAPER / "D5_PRIMITIVE_OBLIGATION_CLOSURE_PLAN.json"
MAIN_TEX = LATEX / "main_cmame.tex"
FLAT_TEX = LATEX / "cmame_submission_flat" / "main_cmame_submission.tex"


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8", errors="replace")


def contains_normalized(text: str, token: str) -> bool:
    return token in text or " ".join(token.split()) in " ".join(text.split())


def blocker_by_id(gate: dict[str, Any], blocker_id: str) -> dict[str, Any]:
    for item in gate.get("blockers", []):
        if isinstance(item, dict) and item.get("id") == blocker_id:
            return item
    return {}


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(AUDIT_JSON)
        audit_md = read_text(AUDIT_MD)
        ref_text = read_text(REF_TXT)
        blocker = read_json(BLOCKER)
        proof_closure = read_json(PROOF_CLOSURE)
        proof_claim_traceability = read_json(PROOF_CLAIM_TRACEABILITY)
        strict_audit = read_json(STRICT_AUDIT)
        proof_contract = read_json(PROOF_CONTRACT)
        proof_style = read_json(PROOF_STYLE)
        b3_review = read_json(B3_REVIEW)
        d5_taylor = read_json(D5_TAYLOR)
        d5_budget = read_json(D5_BUDGET)
        d5_plan = read_json(D5_PLAN)
        main_tex = read_text(MAIN_TEX)
        flat_tex = read_text(FLAT_TEX)
    except Exception as exc:  # noqa: BLE001
        print(f"cmame_strict_proof_policy_reconciliation_audit=FAIL\n- {exc}")
        return 1

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
    direct_corollary = strict_audit.get("direct_route_ps3_corollary", {})
    d5_summary = d5_taylor.get("summary", {})
    budget_summary = d5_budget.get("summary", {})
    plan_summary = d5_plan.get("summary", {})
    b4 = blocker_by_id(blocker, "B4")
    b6 = blocker_by_id(blocker, "B6")
    b7 = blocker_by_id(blocker, "B7")
    expected_global_boundaries = [
        "full_source_policy_package_ready",
        "theorem_level_eta_h_solver_policy_evidence",
        "closed_residual_to_error_theorem_for_mechanism_rows",
    ]
    expected_anchor_evidence_sources = [
        "PROOF_CLOSURE_MANIFEST.json",
        "PROOF_CLAIM_TRACEABILITY_AUDIT.json",
    ]
    expected_narrowed_statuses = {"B4": b4.get("status"), "B6": b6.get("status"), "B7": b7.get("status")}

    checks.check(
        audit.get("schema") == "cmame-strict-proof-policy-reconciliation-audit-v1",
        "schema changed",
    )
    checks.check(
        audit.get("status")
        == "strict_proof_policy_reconciled_b3_direct_route_closed_primitive_taylor_open",
        "status changed",
    )
    checks.check(audit.get("read_only_audit") is True, "audit must be read-only")
    checks.check(audit.get("submission_ready") is False, "audit must not claim submission ready")
    readiness_boundary = audit.get("readiness_boundary", {})
    remaining_gate_scope = audit.get("remaining_gate_scope", {})
    checks.check(
        audit.get("submission_ready_scope")
        == "strict_proof_policy_global_boundary_not_narrowed_claim_package_decision",
        "submission-ready scope changed",
    )
    checks.check(
        readiness_boundary.get("strict_proof_policy_reconciliation_scope")
        == "direct_residual_bridge_kantorovich_route_vs_primitive_162_term_route",
        "strict proof policy reconciliation scope changed",
    )
    checks.check(
        readiness_boundary.get("narrowed_claim_b4_b6_b7_statuses")
        == expected_narrowed_statuses
        == {"B4": "closed", "B6": "closed", "B7": "closed"},
        "narrowed-claim B4/B6/B7 statuses changed",
    )
    checks.check(
        readiness_boundary.get("global_submission_boundaries_retained") == expected_global_boundaries,
        "readiness-boundary global submission boundaries changed",
    )
    checks.check(
        remaining_gate_scope.get("narrowed_claim_b4_b6_b7_statuses") == expected_narrowed_statuses,
        "remaining gate narrowed-claim statuses changed",
    )
    checks.check(
        remaining_gate_scope.get("b4_b6_b7_closed_elsewhere_under_narrowed_claim") is True,
        "remaining gate lost narrowed-claim B4/B6/B7 closure marker",
    )
    checks.check(
        remaining_gate_scope.get("global_submission_boundaries_retained") == expected_global_boundaries,
        "remaining gate global boundaries changed",
    )
    checks.check(
        audit.get("interpretation")
        == "strict_direct_residual_bridge_kantorovich_not_primitive_162_term_closure",
        "interpretation changed",
    )
    checks.check(audit.get("terminology_reconciled") is True, "terminology not reconciled")
    traceability_policy = audit.get("proof_theorem_traceability_policy", {})
    checks.check(
        traceability_policy.get("proof_closure_status") == proof_closure.get("status"),
        "policy theorem traceability proof-closure status mismatch",
    )
    checks.check(
        traceability_policy.get("strict_audit_traceability_present") is True
        and traceability_policy.get("strict_audit_traceability_source_status")
        == strict_traceability.get("proof_closure_status")
        == proof_closure.get("status"),
        "policy theorem traceability not linked to strict proof audit",
    )
    checks.check(
        traceability_policy.get("theorem_statement_labels_present")
        == strict_traceability.get("theorem_statement_labels_present")
        == theorem_statement_boundary.get("all_required_labels_present_main_and_flat")
        is True,
        "theorem labels not carried into proof policy reconciliation",
    )
    checks.check(
        traceability_policy.get("conditional_theorem_boundary_present")
        == strict_traceability.get("conditional_theorem_boundary_present")
        == theorem_statement_boundary.get("conditional_theorem_boundary_present_main_and_flat")
        is True,
        "conditional theorem boundary not carried into proof policy reconciliation",
    )
    checks.check(
        traceability_policy.get("conditional_proof_claims_mapped_to_manuscript")
        == strict_traceability.get("conditional_proof_claims_mapped_to_manuscript")
        == manuscript_traceability.get("conditional_proof_claims_mapped_to_manuscript")
        is True,
        "proof-claim mapping not carried into proof policy reconciliation",
    )
    checks.check(
        traceability_policy.get("proof_dependency_graph_present")
        == strict_traceability.get("proof_dependency_graph_present")
        == manuscript_traceability.get("proof_dependency_graph_present_main_and_flat")
        is True,
        "proof dependencies not carried into proof policy reconciliation",
    )
    checks.check(
        traceability_policy.get("proof_traceability_table_present")
        == strict_traceability.get("proof_traceability_table_present")
        == manuscript_traceability.get("proof_traceability_table_present_main_and_flat")
        is True,
        "proof traceability table not carried into proof policy reconciliation",
    )
    checks.check(
        traceability_policy.get("dynamic_proof_closure_matrix_present")
        == strict_traceability.get("dynamic_proof_closure_matrix_present")
        == manuscript_traceability.get("dynamic_proof_closure_matrix_present_main_and_flat")
        is True,
        "dynamic proof matrix not carried into proof policy reconciliation",
    )
    checks.check(
        traceability_policy.get("primitive_lane_boundary_present")
        == strict_traceability.get("primitive_lane_boundary_present")
        == manuscript_traceability.get("primitive_lane_boundary_present_main_and_flat")
        is True,
        "primitive-route boundary not carried into proof policy reconciliation",
    )
    checks.check(
        traceability_policy.get("residual_nonpromotion_present")
        == strict_traceability.get("residual_nonpromotion_present")
        == manuscript_traceability.get("residual_to_error_nonpromotion_present_main_and_flat")
        is True,
        "residual nonpromotion traceability not carried into proof policy reconciliation",
    )
    checks.check(
        traceability_policy.get("eta_h_theorem_condition_retained")
        == strict_traceability.get("eta_h_theorem_condition_retained")
        == theorem_statement_boundary.get("eta_h_theorem_condition_retained")
        is True,
        "eta_h theorem condition not retained in proof policy reconciliation",
    )
    checks.check(
        traceability_policy.get("eta_h_solver_policy_evidence_closed")
        == strict_traceability.get("eta_h_solver_policy_evidence_closed")
        == theorem_statement_boundary.get("eta_h_solver_policy_evidence_closed")
        is False,
        "proof policy reconciliation overclaims eta_h solver-policy theorem",
    )
    checks.check(
        traceability_policy.get("fixed_tolerance_runs_are_asymptotic_proof")
        == strict_traceability.get("fixed_tolerance_runs_are_asymptotic_proof")
        == theorem_statement_boundary.get("fixed_tolerance_runs_are_asymptotic_proof")
        is False,
        "proof policy reconciliation promotes fixed-tolerance runs",
    )
    checks.check(
        traceability_policy.get("residual_to_error_not_promoted")
        == strict_traceability.get("residual_to_error_not_promoted")
        == theorem_statement_boundary.get("does_not_promote_residual_to_error")
        is True,
        "proof policy reconciliation lost residual-to-error boundary",
    )
    checks.check(
        traceability_policy.get("source_policy_or_full_tfe_not_promoted")
        == strict_traceability.get("source_policy_or_full_tfe_not_promoted")
        == theorem_statement_boundary.get("does_not_promote_source_policy_or_full_tfe")
        is True,
        "proof policy reconciliation lost source-policy/full-TFE nonpromotion",
    )
    checks.check(
        traceability_policy.get("does_not_change_proof_closure_state")
        == strict_traceability.get("does_not_change_proof_closure_state")
        == manuscript_traceability.get("does_not_change_proof_closure_state")
        is True,
        "proof policy reconciliation changed proof closure state through traceability",
    )
    checks.check(
        traceability_policy.get("manuscript_anchor_map_present")
        == strict_traceability.get("manuscript_anchor_map_present")
        == proof_closure_anchor_map.get("all_label_anchors_present")
        is True,
        "proof policy reconciliation lost proof-closure manuscript anchor map",
    )
    checks.check(
        traceability_policy.get("manuscript_anchor_label_count")
        == strict_traceability.get("manuscript_anchor_label_count")
        == proof_closure_anchor_map.get("label_anchor_count")
        == 24,
        "proof policy reconciliation manuscript anchor label count changed",
    )
    checks.check(
        traceability_policy.get("theorem_assumption_anchor_map_present")
        == strict_traceability.get("theorem_assumption_anchor_map_present")
        == proof_closure_anchor_map.get("all_theorem_assumption_anchors_present")
        is True,
        "proof policy reconciliation lost theorem-assumption anchor map",
    )
    checks.check(
        traceability_policy.get("theorem_assumption_anchor_count")
        == strict_traceability.get("theorem_assumption_anchor_count")
        == proof_closure_anchor_map.get("theorem_assumption_anchor_count")
        == 7,
        "proof policy reconciliation theorem-assumption anchor count changed",
    )
    checks.check(
        traceability_policy.get("theorem_assumption_anchor_ids")
        == strict_traceability.get("theorem_assumption_anchor_ids")
        == proof_closure_anchor_map.get("theorem_assumption_anchor_ids")
        == ["P1", "P2", "P3", "P4", "P5", "P6", "P7"],
        "proof policy reconciliation theorem-assumption anchor IDs changed",
    )
    checks.check(
        traceability_policy.get("strict_audit_manuscript_anchor_map_present") is True
        and traceability_policy.get("proof_closure_strict_audit_anchor_fields_match") is True,
        "proof policy reconciliation not linked to strict-audit manuscript anchors",
    )
    checks.check(
        traceability_policy.get("proof_closure_proof_claim_anchor_maps_match") is True
        and proof_closure_anchor_map == proof_claim_anchor_map,
        "proof policy reconciliation proof-closure/proof-claim anchor maps diverged",
    )
    checks.check(
        traceability_policy.get("anchor_evidence_sources") == expected_anchor_evidence_sources,
        "proof policy reconciliation manuscript anchor evidence sources changed",
    )
    checks.check(
        traceability_policy.get("proof_contract_anchor_evidence_sources")
        == contract_traceability.get("anchor_evidence_sources")
        == expected_anchor_evidence_sources,
        "proof policy reconciliation lost proof-contract anchor evidence sources",
    )
    checks.check(
        traceability_policy.get("proof_style_anchor_evidence_sources")
        == style_traceability.get("anchor_evidence_sources")
        == expected_anchor_evidence_sources,
        "proof policy reconciliation lost proof-style anchor evidence sources",
    )
    checks.check(
        traceability_policy.get("strict_audit_anchor_evidence_sources")
        == strict_traceability.get("anchor_evidence_sources")
        == expected_anchor_evidence_sources,
        "proof policy reconciliation lost strict-audit anchor evidence sources",
    )
    checks.check(
        traceability_policy.get("all_anchor_evidence_sources_match") is True,
        "proof policy reconciliation does not enforce proof-contract/style/strict anchor-source agreement",
    )

    for token in [
        "3. BLieDF",
        "6. Convergence analysis",
        "Proof. Taylor expansion for Eq. (12)",
        "global error in the configuration variables",
        "Baker",
        "The local truncation errors of the k-step BLieDF method",
        "An error estimate for",
        "a coupled error recursion is obtained",
        "has the order of convergence p = k",
        "Appendix. Proof of Theorem 4",
    ]:
        checks.check(contains_normalized(ref_text, token), f"reference text missing token: {token}")

    source = audit.get("source_paper_style_read", {})
    source_features = source.get("features", {})
    for key in [
        "bliedf_section_present",
        "convergence_section_present",
        "taylor_local_error_lemma_present",
        "lie_algebra_global_error_present",
        "bch_perturbation_present",
        "constrained_local_error_theorem_present",
        "constraint_multiplier_estimate_present",
        "coupled_error_recursion_present",
        "bdf_order_boundary_present",
        "appendix_proof_present",
    ]:
        checks.check(source_features.get(key) is True, f"proof-method reference feature not true: {key}")
    checks.check(
        "does not supply the primitive 162-subterm Taylor bounds" in source.get("interpretation", ""),
        "proof-method reference role boundary missing",
    )
    checks.check(source.get("reference_paper_not_tfe_paper") is True, "reference/TFE distinction missing")
    checks.check(source.get("used_as_estimate_source") is False, "reference must not be an estimate source")
    checks.check(
        source.get("active_taylor_object")
        == "full_scaled_132_row_residual_map_F_A_h_not_primitive_162_subterms",
        "active Taylor object boundary changed",
    )

    for tex, label in [(main_tex, "main"), (flat_tex, "flat")]:
        for token in [
            "Reference proof usage",
            "Wieloch--Arnold BLieDF proof is invoked as a proof-order template, not as an estimate source",
            "the active Taylor object is the full scaled residual map",
            "not the \\tfe{} comparison paper",
            "Taylor's formula with integral remainder",
            r"\mathcal T_h(\Delta)",
            "primitive/Taylor route is non-active in the theorem",
            "not a complete source-paper temporal finite-element residual replacement",
            "structural and stepwise, not an estimate transfer",
            "branch-stability interfaces; the Newton--Euler row identities are separate FullVA residual-bridge inputs",
            "not imported constraint/multiplier estimates",
            "formal Gauss order is used only for the reduced smooth Gauss branch",
            "Reference-order Taylor discipline",
            "structural ordering discipline only; no Taylor estimate, primitive lift bound, or multiplier estimate is imported",
            "T2 full-map Taylor/Kantorovich estimate is established only for the fixed",
            "the Newton--Euler row identities enter separately as FullVA-specific residual-bridge inputs",
            r"\label{lem:reporting-map-norm-consequence}",
            r"\sup_{y\in U_K}\|D\mathcal R(y)\|\le C_{\mathcal R}",
            "Convex chart-neighborhood checkpoint",
            r"does not assume that \(K\) itself is convex",
            r"segments between them stay inside \(U_K\)",
            r"same reported output indices \(0\le n\le N_h\)",
            r"C_{qv}=C_{\mathcal R}C_{\rm red}",
            "local chart-to-output norm consequence",
            "integral mean-value formula",
            "does not use residual/reaction tables, source-policy rows, fitted constants, output interpolation, or a chart switch",
            r"Lemma~\ref{lem:reporting-map-norm-consequence}",
            "Primitive-route one-way implication discipline",
            "one-way logical form",
            "162 D5 primitive Taylor subterms are",
            "No converse implication is used or available",
            "That output cannot be reinserted as a proof of the primitive inputs",
            r"weighted estimate \(h\|\delta A\|=O(h^7)\) does not imply the unweighted",
            r"direct-route state-block corollary, not a primitive \(P_{\mathrm{state}}\) closure",
            "do not turn the already proved direct residual bridge into a primitive 162-subterm proof",
            "Actual primitive-route Taylor subterm bounds are not established",
        ]:
            checks.check(contains_normalized(tex, token), f"{label} TeX missing proof token: {token}")
    manuscript = audit.get("manuscript_strict_proof_features", {})
    for key, value in manuscript.items():
        checks.check(value is True, f"manuscript feature not true: {key}")
    correspondence = audit.get("reference_correspondence_discipline", {})
    checks.check(correspondence.get("closed") is True, "reference correspondence discipline not closed")
    for label in ["main_features", "flat_features"]:
        feature_group = correspondence.get(label, {})
        for key in [
            "formal_table_reference",
            "formal_table_caption",
            "caption_nonimport_boundary",
            "not_estimate_transfer",
            "constraint_multiplier_interface_split",
            "not_imported_constraint_multiplier_estimates",
            "table_constraint_multiplier_interface_split",
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
            "reference_constrained_slot_contract",
            "reference_slot_contract_four_slots",
            "reference_c1_local_error_slot",
            "reference_c2_constrained_algebraic_slot",
            "reference_c3_one_step_perturbation_slot",
            "reference_c4_global_recursion_slot",
            "reference_slot_no_imports",
            "reference_slot_not_estimate_transfer",
        ]:
            checks.check(
                feature_group.get(key) is True,
                f"{label} missing reference-correspondence feature: {key}",
            )
    checks.check(
        "Reference correspondence is enforced as a captioned manuscript table" in audit_md,
        "markdown report missing captioned-table reference-correspondence boundary",
    )
    checks.check(
        "Reference-to-FullVA translation map binds the reference proof order to present FullVA lemmas without importing estimates."
        in audit_md,
        "markdown report missing Reference-to-FullVA translation map boundary",
    )
    checks.check(
        "Reference constrained-DAE slot map present: `True/True/True/True/True/True/True`."
        in audit_md,
        "markdown report missing Reference constrained-DAE slot map boundary",
    )
    checks.check(
        "Reference-style constrained-slot contract present: `True/True/True/True/True/True/True`."
        in audit_md,
        "markdown report missing Reference-style constrained-slot contract boundary",
    )
    checkpoint = audit.get("proof_order_checkpoint_contract", {})
    checks.check(checkpoint.get("closed") is True, "proof-order instantiation contract not closed")
    for label in ["main_features", "flat_features"]:
        feature_group = checkpoint.get(label, {})
        for key in [
            "checkpoint_title",
            "fixed_discrete_object",
            "reference_table_binding",
            "local_defect_direct_bridge",
            "primitive_162_not_used",
            "p6_retained_condition",
            "fixed_tolerance_logs_do_not_discharge_p6",
            "local_global_reporting_only_after_local_defect",
            "p7_nonpromoted",
        ]:
            checks.check(
                feature_group.get(key) is True,
                f"{label} missing proof-order instantiation feature: {key}",
            )
    checks.check(
        checkpoint.get("sequence")
        == [
            "fixed_discrete_object",
            "local_defect_direct_bridge_without_primitive_162_promotion",
            "endpoint_and_retained_p6_solver_interface",
            "local_global_reporting_with_p7_nonpromotion",
        ],
        "proof-order instantiation sequence changed",
    )
    checks.check(
        checkpoint.get("adds_theorem_claim") is False
        and checkpoint.get("closes_p6") is False
        and checkpoint.get("closes_p7") is False
        and checkpoint.get("uses_primitive_162_term_route") is False,
        "proof-order instantiation overclaims closure or primitive route use",
    )
    checks.check(
        "Proof-order instantiation closed: `True`." in audit_md
        and "Proof-order instantiation fixes the discrete object, then local defect, retained P6, and P7 output boundary"
        in audit_md,
        "markdown report missing proof-order instantiation boundary",
    )
    assumption_non_circularity = audit.get("assumption_non_circularity_contract", {})
    checks.check(
        assumption_non_circularity.get("closed") is True,
        "assumption non-circularity contract not closed",
    )
    for label in ["main_features", "flat_features"]:
        feature_group = assumption_non_circularity.get(label, {})
        for key in [
            "assumption_admissibility_note",
            "does_not_assume_theorem_conclusion",
            "p2_prior_to_gronwall",
            "not_assumed_local_defect",
            "not_inferred_from_observed_slopes",
            "non_vacuity_admissibility_note",
            "does_not_assume_h7_local_defect",
            "does_not_assume_h6_grid_estimate",
            "finite_rows_not_admissibility_claim",
        ]:
            checks.check(
                feature_group.get(key) is True,
                f"{label} missing assumption non-circularity feature: {key}",
            )
    checks.check(
        assumption_non_circularity.get("assumes_theorem_conclusion") is False
        and assumption_non_circularity.get("assumes_local_defect") is False
        and assumption_non_circularity.get("assumes_grid_estimate") is False
        and assumption_non_circularity.get("inferred_from_observed_slopes_or_logs") is False
        and assumption_non_circularity.get("closes_p6") is False
        and assumption_non_circularity.get("closes_p7") is False,
        "assumption non-circularity contract overclaims assumption/proof closure",
    )
    checks.check(
        "Assumption non-circularity closed: `True`." in audit_md
        and "Retained admissibility interfaces do not assume the local defect, grid estimate, observed slopes, P6 proof, or P7 boundary"
        in audit_md,
        "markdown report missing assumption non-circularity boundary",
    )

    reporting_map = audit.get("reporting_map_norm_consequence_contract", {})
    checks.check(
        reporting_map.get("closed") is True,
        "reporting-map norm consequence contract not closed",
    )
    checks.check(
        reporting_map.get("constant_formula") == "C_qv = C_{\\mathcal R} C_red",
        "reporting-map constant formula changed",
    )
    checks.check(
        reporting_map.get("uses_residual_to_error_transfer") is False
        and reporting_map.get("uses_global_atlas_equivalence") is False
        and reporting_map.get("uses_output_interpolation") is False,
        "reporting-map contract overclaims transfer/global/output scope",
    )
    for label in ["main_features", "flat_features"]:
        feature_group = reporting_map.get(label, {})
        for key in [
            "lemma_label",
            "compact_derivative_supremum",
            "convex_chart_checkpoint",
            "no_convex_k_assumption",
            "segments_inside_uk",
            "same_reported_indices",
            "qv_constant_formula",
            "local_chart_to_output_boundary",
            "mean_value_formula",
            "no_diagnostic_inputs",
            "theorem_invocation",
        ]:
            checks.check(
                feature_group.get(key) is True,
                f"{label} missing reporting-map feature: {key}",
            )

    primitive_one_way = audit.get("primitive_route_one_way_certificate_contract", {})
    checks.check(
        primitive_one_way.get("closed") is True,
        "primitive-route one-way certificate contract not closed",
    )
    checks.check(
        primitive_one_way.get("logical_form")
        == "open primitives plus P_tube imply the 162 Taylor subterms, which imply the dynamic residual bound",
        "primitive one-way logical form changed",
    )
    checks.check(
        primitive_one_way.get("converse_available") is False
        and primitive_one_way.get("direct_route_output_reinserted_as_primitive_input") is False
        and primitive_one_way.get("weighted_acceleration_promotes_to_unweighted_pacc") is False
        and primitive_one_way.get("pstate_direct_corollary_promotes_to_pstate_closure") is False,
        "primitive one-way contract overclaims a converse or primitive promotion",
    )
    checks.check(
        primitive_one_way.get("aggregate_residual_projects_to_primitive_subterms") is False
        and primitive_one_way.get("requires_hidden_primitive_projection") is False,
        "primitive one-way contract overclaims aggregate-residual projection to primitive subterms",
    )
    checks.check(
        primitive_one_way.get("actual_primitive_taylor_bounds_proved") == 0,
        "primitive one-way contract overclaims actual Taylor bounds",
    )
    for label in ["main_features", "flat_features"]:
        feature_group = primitive_one_way.get(label, {})
        for key in [
            "paragraph_title",
            "one_way_logical_form",
            "primitive_to_162_to_residual",
            "no_converse",
            "direct_route_not_primitive_input",
            "weighted_acceleration_not_unweighted",
            "pstate_corollary_not_closure",
            "does_not_turn_direct_bridge_into_primitive_certificate",
            "primitive_bounds_not_established",
            "taylor_projection_checkpoint",
            "aggregate_fixed_block_norm",
            "not_projection_certificate_162",
            "primitive_projection_operator",
            "projection_right_inverse_needed",
            "independent_primitive_lift_bounds",
            "no_projection_right_inverse_used",
            "t2_closed_while_primitive_separate",
            "non_substitution_contract",
            "replacement_scope_one_input",
            "not_replace_t2_kantorovich",
            "not_replace_endpoint_p6_p7",
            "alternative_certificate_one_input",
            "not_complete_order_theorem",
        ]:
            checks.check(
                feature_group.get(key) is True,
                f"{label} missing primitive one-way feature: {key}",
            )

    kantorovich = audit.get("strict_kantorovich_radius_contract", {})
    checks.check(kantorovich.get("closed") is True, "strict Kantorovich radius contract not closed")
    for tex, label in [(main_tex, "main"), (flat_tex, "flat")]:
        for token in [
            "same accepted stage-coordinate vector before",
            r"\|F_{A,h}(Z_G;y)\| \le C_R h^7",
            r"Assume also, uniformly for \(y\in K\) and",
            r"\rho_h=2M\|R_h\|",
            r"\rho_h\le r",
            r"ML\rho_h\le 1/2",
            r"\sup_{0<h\le h_0}\sup_{y\in K}",
            r"\|\mathcal T_h(\Delta)\|",
            r"\|\mathcal T_h(\Delta_1)-\mathcal T_h(\Delta_2)\|",
            r"B_{\rho_h}(0)",
            r"\le 2MC_Rh^7=C_Zh^7",
            r"\mathcal E_h(Z_A)-\mathcal E_h(Z_G)",
            r"with \(C_R\) independent of \(y\in K\)",
        ]:
            checks.check(contains_normalized(tex, token), f"{label} TeX missing Kantorovich token: {token}")
    for label in ["main_features", "flat_features"]:
        feature_group = kantorovich.get(label, {})
        for key in [
            "gauss_lift_same_stage_coordinate",
            "residual_hypothesis",
            "residual_uniform_yK_hbar",
            "radius_definition",
            "radius_contained_in_tube",
            "absorption_condition",
            "endpoint_derivative_supremum",
            "self_map_bound",
            "contraction_bound",
            "fixed_point_ball",
            "stage_error_bound",
            "endpoint_transfer",
            "bridge_constant_uniform_yK",
        ]:
            checks.check(feature_group.get(key) is True, f"{label} missing Kantorovich feature: {key}")
    checks.check(
        kantorovich.get("residual_hypothesis") == "||F_A,h(Z_G;y)|| <= C_R h^7",
        "Kantorovich residual hypothesis changed",
    )
    checks.check(
        kantorovich.get("radius_definition") == "rho_h = 2 M ||R_h||",
        "Kantorovich radius definition changed",
    )
    checks.check(
        kantorovich.get("small_h_conditions") == ["rho_h <= r", "M L rho_h <= 1/2"],
        "Kantorovich small-h conditions changed",
    )
    checks.check(
        kantorovich.get("self_map_claim") == "T_h maps B_{rho_h}(0) into itself",
        "Kantorovich self-map claim changed",
    )
    checks.check(
        kantorovich.get("contraction_claim") == "Lip(T_h on B_{rho_h}(0)) <= 1/2",
        "Kantorovich contraction claim changed",
    )
    checks.check(
        kantorovich.get("stage_error_bound") == "||Z_A-Z_G|| <= C_Z h^7",
        "Kantorovich stage error bound changed",
    )
    checks.check(
        kantorovich.get("stage_error_constant") == "C_Z = 2 M C_R",
        "Kantorovich stage error constant changed",
    )
    checks.check(
        kantorovich.get("endpoint_perturbation_bound") == "||E_h(Z_A)-E_h(Z_G)|| <= C_A h^7",
        "Kantorovich endpoint perturbation bound changed",
    )
    checks.check(
        kantorovich.get("endpoint_perturbation_constant") == "C_A = M_E C_Z",
        "Kantorovich endpoint perturbation constant changed",
    )
    uniform = kantorovich.get("uniform_constant_discipline", {})
    checks.check(uniform.get("closed") is True, "Kantorovich uniform constant discipline not closed")
    checks.check(
        uniform.get("residual_uniform_scope") == "uniform for y in K and 0 < h <= hbar",
        "Kantorovich residual uniform scope changed",
    )
    checks.check(
        uniform.get("endpoint_derivative_bound")
        == "sup_{0<h<=h0} sup_{y in K} sup_{Z in B_r(Z_G(y,h))} ||D_Z E_h(Z)|| <= M_E",
        "Kantorovich endpoint derivative bound changed",
    )
    checks.check(
        uniform.get("bridge_constant_scope")
        == "C_R independent of y in K, h, reported grid length, backend, and finite diagnostic tolerances",
        "Kantorovich bridge constant scope changed",
    )
    checks.check(
        kantorovich.get("uses_finite_probe_as_proof") is False
        and kantorovich.get("uses_primitive_162_route_as_input") is False
        and kantorovich.get("closes_primitive_162_route") is False,
        "Kantorovich contract overclaims proof inputs or primitive-route closure",
    )

    direct = audit.get("direct_residual_bridge_kantorovich_route", {})
    checks.check(direct.get("closed") is True, "direct residual-bridge/Kantorovich route should be closed")
    checks.check(direct.get("b3_review_passed") is b3_review.get("b3_direct_proof_review_passed") is True, "B3 review marker changed")
    checks.check(direct.get("b3_can_close") is b3_review.get("b3_can_close_from_proof_review") is True, "B3 closure marker changed")
    checks.check(
        direct.get("direct_pc2_proof_gap_closed")
        is closure.get("direct_pc2_proof_gap_closed", closure.get("proof_gap_closed"))
        is True,
        "direct PC2 proof gap closure missing",
    )
    checks.check(direct.get("proof_gap_closed") is closure.get("proof_gap_closed") is True, "legacy proof gap direct route not closed")
    checks.check(
        direct.get("proof_gap_closed_scope")
        == "direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open",
        "direct proof gap scope changed",
    )
    checks.check(
        "schema-compatible shorthand for direct_pc2_proof_gap_closed"
        in direct.get("proof_gap_closed_reading_rule", ""),
        "direct proof gap reading rule missing",
    )
    direct_schema = direct.get("schema_compatibility", {})
    checks.check(
        direct_schema.get("legacy_key") == "proof_gap_closed"
        and direct_schema.get("legacy_key_retained_for_schema_compatibility") is True
        and direct_schema.get("preferred_key") == "direct_pc2_proof_gap_closed",
        "direct proof gap schema compatibility missing",
    )
    checks.check(
        direct.get("pc2_closed_by_direct_substitution")
        is closure.get("pc2_closed_by_direct_substitution")
        is True,
        "PC2 residual-value bridge marker changed",
    )
    checks.check(
        direct.get("stage_residual_O_h7_implementation_defect_proved")
        is closure.get("stage_residual_O_h7_implementation_defect_proved")
        is True,
        "stage-residual O(h^7) direct marker changed",
    )
    checks.check(direct.get("dynamic_zero_rows") == 36, "dynamic zero row count changed")
    checks.check(direct.get("full_stage_rows") == 132, "full-stage row count changed")
    checks.check(
        direct.get("direct_substitution_supplies_active_pc2_residual_bridge")
        is strict_manifest.get("direct_substitution_supplies_active_pc2_residual_bridge")
        is True,
        "same-branch dynamic zero-block role changed",
    )
    checks.check(direct.get("required_pc2_route") == "direct_residual_bridge_kantorovich_route", "required PC2 route changed")
    checks.check(direct.get("direct_route_ps3_certificate_closed") is True, "direct PS3 route not closed")
    checks.check(
        direct.get("uses_finite_probe_as_proof") is direct_corollary.get("uses_finite_probe_as_proof") is False,
        "finite probe must not be used as proof",
    )

    primitive_route = audit.get("primitive_162_term_taylor_route", {})
    checks.check(primitive_route.get("closed") is False, "primitive Taylor route must remain open")
    checks.check(
        strict_manifest.get("primitive_taylor_route_closed") is False,
        "manifest unexpectedly closes primitive Taylor route",
    )
    checks.check(primitive_route.get("actual_taylor_bounds_proved") == 0, "primitive actual Taylor bounds overclaimed")
    checks.check(primitive_route.get("open_taylor_bound_terms") == 162, "open Taylor term count changed")
    checks.check(primitive_route.get("terms_with_open_primitive_blockers") == 162, "primitive blocker term count changed")
    checks.check(primitive_route.get("open_primitive_count") == 5, "open primitive count changed")
    checks.check(
        primitive_route.get("current_instance_available") is False,
        "primitive Taylor conditional schema unexpectedly has a current instance",
    )
    checks.check(
        primitive_route.get("blocker_summary")
        == "0/162 Taylor bounds certified; five primitive lift/bilinear antecedents remain open",
        "primitive Taylor conditional-schema blocker summary changed",
    )
    checks.check(
        primitive_route.get("role")
        == (
            "separate stricter conditional primitive Taylor certificate schema; "
            "no current instance is claimed as closed"
        ),
        "primitive Taylor conditional-schema role changed",
    )
    checks.check(primitive_route.get("conditional_terms") == d5_summary.get("conditional_term_bounds_under_open_primitive_assumptions") == 162, "conditional term count changed")
    checks.check(primitive_route.get("certified_taylor_bound_terms") == budget_summary.get("certified_taylor_bound_terms") == 0, "certified Taylor terms overclaimed")
    checks.check(primitive_route.get("induced_taylor_bounds_proved") == plan_summary.get("induced_taylor_bounds_proved") == 0, "induced Taylor bounds overclaimed")
    checks.check(primitive_route.get("unweighted_acceleration_blocked_terms") == 36, "unweighted acceleration blocker count changed")
    checks.check(primitive_route.get("h_weighted_acceleration_sufficient_terms") == 0, "h-weighted acceleration incorrectly sufficient")
    checks.check(primitive_route.get("h_weighted_acceleration_insufficient_terms") == 36, "h-weighted acceleration insufficiency changed")
    checks.check(
        primitive_route.get("primitive_route_pc2_closed")
        is primitive.get("primitive_route_pc2_closed")
        is False,
        "primitive PC2 unexpectedly closed",
    )
    checks.check(
        primitive_route.get("primitive_route_proof_gap_closed")
        is primitive.get("primitive_route_proof_gap_closed")
        is False,
        "primitive proof gap unexpectedly closed",
    )
    checks.check(
        strict_policy.get("primitive_route_required_for_b3_closure") is False,
        "primitive route unexpectedly required for B3 closure",
    )
    checks.check(strict_policy.get("direct_residual_bridge_kantorovich_route_closed") is True, "direct strict route not closed")

    forbidden = audit.get("forbidden_interpretations", {})
    for key in [
        "primitive_route_closed",
        "actual_162_taylor_bounds_proved",
        "finite_probe_used_as_proof",
        "residual_to_error_promotion_used",
        "submission_ready",
    ]:
        checks.check(forbidden.get(key) is False, f"forbidden interpretation not false: {key}")
    checks.check(
        audit.get("remaining_narrowed_claim_submission_blockers") == [],
        "narrowed-claim blocker list changed",
    )
    checks.check(
        audit.get("remaining_global_submission_boundaries")
        == [
            "full_source_policy_package_ready",
            "theorem_level_eta_h_solver_policy_evidence",
            "closed_residual_to_error_theorem_for_mechanism_rows",
        ],
        "remaining global submission boundaries changed",
    )

    for token in [
        "Interpretation: `strict_direct_residual_bridge_kantorovich_not_primitive_162_term_closure`.",
        "Terminology reconciled: `True`.",
        "Here `submission_ready=false` is scoped to proof-policy/global proof-package readiness,",
        "not to the separate narrowed-claim package decision.",
        "Submission-ready scope: `strict_proof_policy_global_boundary_not_narrowed_claim_package_decision`.",
        "Policy reconciliation scope: `direct_residual_bridge_kantorovich_route_vs_primitive_162_term_route`.",
        "B4/B6/B7 narrowed-claim statuses (narrowed-only; not source-policy row closure): `closed/closed/closed`.",
        "Reference correspondence discipline closed: `True`.",
        "Constraint/multiplier correspondence is restricted to compact-chart, right-inverse, endpoint, and branch-stability interfaces.",
        "Newton--Euler row identities are recorded as separate FullVA residual-bridge inputs, not imported reference multiplier estimates.",
        "Reporting-map norm consequence closed: `True`.",
        "Reporting map uses the compact derivative supremum on `U_K` and the same reported output indices.",
        "Reporting map does not use residual-to-error transfer, global atlas equivalence, output interpolation, or a chart switch.",
        "Primitive-route one-way implication discipline closed: `True`.",
        "Primitive route records only primitives-to-162-terms-to-residual implication; no converse is available.",
        "Direct route output is not reinserted as a primitive input; weighted acceleration does not close unweighted P_acc.",
        "Taylor projection checkpoint keeps the aggregate 132-row residual estimate from being read as a 162-subterm primitive certificate.",
        "Direct route closed: `True`.",
        "B3 review passed/can close: `True/True`.",
        "PC2 residual-value bridge satisfied by 96-row non-dynamic certificate plus same-branch 36-row base-point zero dynamic block: `True`.",
        "Dynamic/full rows: `36/132`.",
        "Uses finite probe as proof: `False`.",
        "## Strict Kantorovich Radius Contract",
        "Contract closed in main/flat TeX: `True`.",
        "Residual hypothesis: `||F_A,h(Z_G;y)|| <= C_R h^7`.",
        "Radius definition: `rho_h = 2 M ||R_h||`.",
        "Small-h conditions: `rho_h <= r; M L rho_h <= 1/2`.",
        "Self-map claim: `T_h maps B_{rho_h}(0) into itself`.",
        "Contraction claim: `Lip(T_h on B_{rho_h}(0)) <= 1/2`.",
        "Stage error bound: `||Z_A-Z_G|| <= C_Z h^7`.",
        "Stage error constant: `C_Z = 2 M C_R`.",
        "Endpoint perturbation bound: `||E_h(Z_A)-E_h(Z_G)|| <= C_A h^7`.",
        "Endpoint perturbation constant: `C_A = M_E C_Z`.",
        "Closes primitive 162-term route: `False`.",
        "Theorem labels/boundary/mapped: `True/True/True`.",
        "Proof dependency/traceability/dynamic matrix: `True/True/True`.",
        "Primitive-route and residual scope boundaries: `True/True`.",
        "Eta condition/closure and fixed-tolerance proof: `True/False/False`.",
        "Residual/source-policy-full-TFE not promoted: `True/True`; no-state-change `True`.",
        "Manuscript anchor policy: closure anchors `True`; strict-audit anchors `True`; label anchors `24`; theorem-interface/P7-output-boundary anchors `7`; IDs `P1,P2,P3,P4,P5,P6,P7`; strict map fields match `True`; proof-claim map match `True`.",
        "Reader-facing theorem-interface split: theorem interfaces `P1--P6`; P7 is an output nonclaim/residual-to-error boundary anchor, not a theorem premise.",
        "Anchor evidence sources: `PROOF_CLOSURE_MANIFEST.json,PROOF_CLAIM_TRACEABILITY_AUDIT.json`; contract/style/strict source match `True`.",
        "Primitive route closed: `False`.",
        "Primitive route current instance available: `False`.",
        "Primitive route blocker summary: `0/162 Taylor bounds certified; five primitive lift/bilinear antecedents remain open`.",
        "Primitive actual/open Taylor terms: `0/162`.",
        "Terms blocked by open primitives: `162`.",
        "Open primitive count: `5`.",
        "Certified/induced Taylor bounds: `0/0`.",
        "h-weighted acceleration sufficient/insufficient terms: `0/36`.",
        "PC2 closed by primitive route: `False`.",
        "Proof gap closed by primitive route: `False`.",
        "Remaining narrowed-claim submission blockers: `none`.",
        "Remaining global submission boundaries: `full_source_policy_package_ready,theorem_level_eta_h_solver_policy_evidence,closed_residual_to_error_theorem_for_mechanism_rows`.",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("cmame_strict_proof_policy_reconciliation_audit=FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("cmame_strict_proof_policy_reconciliation_audit=PASS")
    print("terminology_reconciled=True")
    print("direct_route_closed=True")
    print("primitive_route_closed=False")
    print("primitive_actual_open_taylor_terms=0/162")
    print("submission_ready=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
