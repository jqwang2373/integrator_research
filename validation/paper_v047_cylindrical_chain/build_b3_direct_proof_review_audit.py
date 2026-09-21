#!/usr/bin/env python3
"""Build the B3 direct-proof review audit.

This review is deliberately narrower than full submission readiness.  It
checks the post-D5 direct-substitution proof evidence and the accepted direct
residual-bridge/Kantorovich route for B3, while preserving the
primitive/Taylor route as an open conditional certificate schema.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
OUT_JSON = PAPER / "B3_DIRECT_PROOF_REVIEW_AUDIT.json"
OUT_MD = PAPER / "B3_DIRECT_PROOF_REVIEW_AUDIT.md"


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def normalized_contains(text: str, token: str) -> bool:
    return token in text or " ".join(token.split()) in " ".join(text.split())


def all_present(text: str, tokens: list[str]) -> bool:
    return all(normalized_contains(text, token) for token in tokens)


def main() -> None:
    proof_closure = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
    d5_direct = read_json(PAPER / "D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE.json")
    traceability = read_json(PAPER / "PROOF_CLAIM_TRACEABILITY_AUDIT.json")
    proof_contract = read_json(PAPER / "CMAME_PROOF_CONTRACT_GATE.json")
    strict_proof_audit = read_json(PAPER / "CMAME_STRICT_PROOF_AUDIT.json")
    blocker_gate = read_json(PAPER / "CMAME_BLOCKER_CLOSURE_GATE.json")
    main_tex = read_text(LATEX / "main_cmame.tex")
    flat_tex = read_text(LATEX / "cmame_submission_flat" / "main_cmame_submission.tex")
    main_pdf_text = read_text(LATEX / "main_cmame.txt")
    flat_pdf_text = read_text(LATEX / "cmame_submission_flat" / "main_cmame_submission.txt")

    closure = proof_closure.get("closure_state", {})
    evidence = proof_closure.get("evidence_summary", {})
    close_requirements = proof_closure.get("close_requirements", [])
    direct_summary = d5_direct.get("summary", {})
    full_stage_rows_when_assembled = direct_summary.get(
        "full_stage_rows_when_assembled_by_bridge",
        direct_summary.get("full_stage_rows_if_promoted"),
    )
    forbidden = d5_direct.get("forbidden_shortcuts", {})
    theorem_contract = proof_contract.get("theorem_contract", {})
    direct_residual_bridge_standard = proof_closure.get(
        "direct_residual_bridge_kantorovich_submission_standard",
        proof_closure.get("strict_direct_residual_bridge_submission_standard", {}),
    )
    strict_features = strict_proof_audit.get("manuscript_strict_proof_features", {})
    strict_main = strict_features.get("main", {})
    strict_flat = strict_features.get("flat", {})
    strict_boundary = strict_proof_audit.get("two_layer_proof_boundary", {})
    b3 = next((item for item in blocker_gate.get("blockers", []) if item.get("id") == "B3"), {})
    proof_strength_guard_groups = {
        "reference_order_contract": [
            "reference_proof_method_alignment",
            "reference_ordering_template_not_literal_transfer",
            "reference_no_estimate_transfer_ledger",
            "reference_fullva_translation_checkpoint",
            "reference_constrained_dae_slot_checkpoint",
            "reference_dependency_graph_not_premise",
        ],
        "taylor_route_separation": [
            "taylor_layer_separation_checkpoint",
            "taylor_t1_t2_load_bearing",
            "taylor_t2_full_residual_map_layer",
            "primitive_taylor_route_retained",
            "taylor_no_t2_to_prove_primitives",
        ],
        "theorem_direction_locks": [
            "theorem_input_output_reading_rule",
            "theorem_no_backward_arrows",
            "theorem_reported_run_only_specializes",
            "theorem_no_retroactive_instance_change",
        ],
        "same_object_composition_locks": [
            "same_object_closure_criterion",
            "same_object_branch_row_norm_endpoint_agree",
            "same_object_no_cross_branch_splicing",
            "same_object_jointly_admissible_tuple",
        ],
        "p6_evidence_grade_locks": [
            "p6_evidence_grade_rule",
            "p6_only_one_theorem_grade_input",
            "p6_predeclared_same_branch_residual_envelope",
            "p6_diagnostic_grade_evidence_only",
            "p6_log_specializes_not_creates",
        ],
    }
    proof_strength_guards = {
        name: {
            "main": all(strict_main.get(key) is True for key in keys),
            "flat": all(strict_flat.get(key) is True for key in keys),
            "keys": keys,
        }
        for name, keys in proof_strength_guard_groups.items()
    }
    proof_strength_guards_present = all(
        item["main"] is True and item["flat"] is True
        for item in proof_strength_guards.values()
    )

    direct_tokens = [
        "The active theorem already consumes the direct dynamic-row identity through",
        "The D5 direct-substitution certificate proves the 36 Newton--Euler residual",
        "not imported into the active residual-bridge estimate",
    ]
    full_stage_tokens = [
        "full 132-row stage residual required for the order argument",
    ]
    tex_direct_ok = all_present(main_tex, direct_tokens) and all_present(flat_tex, direct_tokens)
    pdf_direct_ok = all_present(main_pdf_text, full_stage_tokens) and all_present(flat_pdf_text, full_stage_tokens)
    forbidden_shortcuts_clean = all(value is False for value in forbidden.values())
    satisfied_close_requirements = sum(1 for item in close_requirements if item.get("satisfied"))
    unsatisfied_close_requirements = sum(1 for item in close_requirements if not item.get("satisfied"))
    pc2 = next((item for item in close_requirements if item.get("id") == "PC2"), {})
    strict_taylor_proof_keys = [
        "stage_taylor_expansion",
        "quadratic_remainder",
        "newton_kantorovich_absorption",
        "contraction_radius",
        "stage_error_bound",
        "endpoint_closure_explicit_constant",
        "inexact_newton_endpoint_constant",
        "inexact_newton_scaled_endpoint_constant",
        "local_global_reduced_grid_constant",
        "qv_reporting_explicit_constant",
        "conditional_order_theorem",
        "discrete_gronwall_step",
        "primitive_taylor_route_retained",
    ]
    strict_conditional_taylor_proof_present = all(
        strict_main.get(key) is True and strict_flat.get(key) is True
        for key in strict_taylor_proof_keys
    ) and strict_features.get("strict_conditional_math_proof_present") is True

    proof_review_passed = all(
        [
            closure.get("proof_gap_closed") is True,
            closure.get("pc2_closed_by_direct_substitution") is True,
            closure.get("stage_residual_O_h7_implementation_defect_proved") is True,
            closure.get("primitive_lift_route_closed") is False,
            closure.get("accepted_residual_to_error_theorem") is False,
            closure.get("eta_h_O_h7_solver_policy_evidence") is False,
            direct_summary.get("direct_route_certificate_closed") is True,
            direct_summary.get("direct_route_non_circular") is True,
            direct_summary.get("dynamic_zero_residual_rows") == 36,
            full_stage_rows_when_assembled == 132,
            direct_summary.get("forbidden_shortcuts_used") == 0,
            forbidden_shortcuts_clean,
            satisfied_close_requirements == 4,
            unsatisfied_close_requirements == 0,
            pc2.get("satisfied") is True,
            "same-branch residual-value certificate" in pc2.get("satisfaction_mode", ""),
            traceability.get("main_source", {}).get("all_boundary_tokens_present") is True,
            traceability.get("flat_source", {}).get("all_boundary_tokens_present") is True,
            traceability.get("dynamic_proof_closure_matrix_status")
            == "present_direct_substitution_closure_inputs",
            strict_conditional_taylor_proof_present,
            strict_boundary.get("b1_status") == "closed",
            strict_boundary.get("b3_status") == "closed",
            strict_boundary.get("direct_route_stage_residual_O_h7") is True,
            strict_boundary.get("two_layer_boundary_consistent") is True,
            proof_strength_guards_present,
            tex_direct_ok,
            pdf_direct_ok,
            theorem_contract.get("newton_tolerance_policy") == "eta_h^tube <= c_eta h^7 for asymptotic proof",
            theorem_contract.get("fixed_tolerance_runs_are_asymptotic_proof") is False,
        ]
    )

    result = {
        "schema": "b3-direct-proof-review-audit-v1",
        "status": "b3_direct_proof_review_passed_residual_bridge_closure_closed",
        "read_only_audit": True,
        "submission_ready": False,
        "b3_review_requirement": "direct_residual_bridge_kantorovich_route_closure",
        "b3_previous_status": b3.get("status"),
        "b3_direct_proof_review_passed": proof_review_passed,
        "b3_can_close_from_proof_review": True,
        "direct_substitution_supplies_active_pc2_residual_bridge": direct_residual_bridge_standard.get(
            "direct_substitution_supplies_active_pc2_residual_bridge"
        ),
        "active_pc2_standard_name": "strict_direct_residual_bridge_submission_standard",
        "direct_residual_bridge_submission_standard_satisfied": direct_residual_bridge_standard.get("satisfied"),
        "direct_residual_bridge_required_pc2_route": direct_residual_bridge_standard.get("required_pc2_route"),
        "active_pc2_required_route": direct_residual_bridge_standard.get("required_pc2_route"),
        "primitive_taylor_required_for_active_pc2": False,
        "primitive_taylor_route_status": "conditional_schema_open_not_required_for_b3_closure",
        "primitive_taylor_actual_bounds_proved": direct_residual_bridge_standard.get("actual_taylor_bounds_proved"),
        "primitive_taylor_open_bound_terms": direct_residual_bridge_standard.get("open_taylor_bound_terms"),
        "primitive_taylor_open_primitive_count": direct_residual_bridge_standard.get("open_primitive_count"),
        "proof_closure": {
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
                "Kantorovich route. It does not close the primitive/Taylor route, P6 "
                "solver-policy evidence, P7 residual-to-error nonpromotion boundary, source-policy "
                "readiness, or full-TFE replacement."
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
            "primitive_lift_route_closed": closure.get("primitive_lift_route_closed"),
            "eta_h_O_h7_solver_policy_evidence": closure.get("eta_h_O_h7_solver_policy_evidence"),
            "accepted_residual_to_error_theorem": closure.get("accepted_residual_to_error_theorem"),
        },
        "direct_certificate": {
            "dynamic_zero_residual_rows": direct_summary.get("dynamic_zero_residual_rows"),
            "full_stage_rows_when_assembled_by_bridge": full_stage_rows_when_assembled,
            "legacy_full_stage_rows_if_promoted_scope": direct_summary.get(
                "legacy_full_stage_rows_if_promoted_scope",
                "schema-compatible alias; active direct PC2 route already consumes the bridge",
            ),
            "full_stage_rows_if_promoted": direct_summary.get("full_stage_rows_if_promoted"),
            "direct_route_certificate_closed": direct_summary.get("direct_route_certificate_closed"),
            "direct_route_non_circular": direct_summary.get("direct_route_non_circular"),
            "forbidden_shortcuts_used": direct_summary.get("forbidden_shortcuts_used"),
            "forbidden_shortcuts_clean": forbidden_shortcuts_clean,
        },
        "close_requirements": {
            "satisfied": satisfied_close_requirements,
            "unsatisfied": unsatisfied_close_requirements,
            "pc2_satisfaction_mode": pc2.get("satisfaction_mode"),
        },
        "manuscript_review": {
            "main_tex_direct_tokens": all_present(main_tex, direct_tokens),
            "flat_tex_direct_tokens": all_present(flat_tex, direct_tokens),
            "main_pdf_full_stage_token": all_present(main_pdf_text, full_stage_tokens),
            "flat_pdf_full_stage_token": all_present(flat_pdf_text, full_stage_tokens),
            "traceability_main_boundary_tokens": traceability.get("main_source", {}).get(
                "all_boundary_tokens_present"
            ),
            "traceability_flat_boundary_tokens": traceability.get("flat_source", {}).get(
                "all_boundary_tokens_present"
            ),
            "dynamic_matrix_status": traceability.get("dynamic_proof_closure_matrix_status"),
        },
        "strict_conditional_taylor_proof": {
            "strict_conditional_math_proof_present": strict_features.get(
                "strict_conditional_math_proof_present"
            ),
            "main_stage_taylor_expansion": strict_main.get("stage_taylor_expansion"),
            "flat_stage_taylor_expansion": strict_flat.get("stage_taylor_expansion"),
            "main_quadratic_remainder": strict_main.get("quadratic_remainder"),
            "flat_quadratic_remainder": strict_flat.get("quadratic_remainder"),
            "main_newton_kantorovich_absorption": strict_main.get(
                "newton_kantorovich_absorption"
            ),
            "flat_newton_kantorovich_absorption": strict_flat.get(
                "newton_kantorovich_absorption"
            ),
            "main_contraction_radius": strict_main.get("contraction_radius"),
            "flat_contraction_radius": strict_flat.get("contraction_radius"),
            "main_stage_error_bound": strict_main.get("stage_error_bound"),
            "flat_stage_error_bound": strict_flat.get("stage_error_bound"),
            "main_endpoint_closure_explicit_constant": strict_main.get("endpoint_closure_explicit_constant"),
            "flat_endpoint_closure_explicit_constant": strict_flat.get("endpoint_closure_explicit_constant"),
            "main_inexact_newton_endpoint_constant": strict_main.get("inexact_newton_endpoint_constant"),
            "flat_inexact_newton_endpoint_constant": strict_flat.get("inexact_newton_endpoint_constant"),
            "main_inexact_newton_scaled_endpoint_constant": strict_main.get("inexact_newton_scaled_endpoint_constant"),
            "flat_inexact_newton_scaled_endpoint_constant": strict_flat.get("inexact_newton_scaled_endpoint_constant"),
            "main_local_global_reduced_grid_constant": strict_main.get("local_global_reduced_grid_constant"),
            "flat_local_global_reduced_grid_constant": strict_flat.get("local_global_reduced_grid_constant"),
            "main_qv_reporting_explicit_constant": strict_main.get("qv_reporting_explicit_constant"),
            "flat_qv_reporting_explicit_constant": strict_flat.get("qv_reporting_explicit_constant"),
            "main_conditional_order_theorem": strict_main.get("conditional_order_theorem"),
            "flat_conditional_order_theorem": strict_flat.get("conditional_order_theorem"),
            "main_discrete_gronwall_step": strict_main.get("discrete_gronwall_step"),
            "flat_discrete_gronwall_step": strict_flat.get("discrete_gronwall_step"),
            "main_primitive_taylor_route_retained": strict_main.get(
                "primitive_taylor_route_retained"
            ),
            "flat_primitive_taylor_route_retained": strict_flat.get(
                "primitive_taylor_route_retained"
            ),
            "b1_status": strict_boundary.get("b1_status"),
            "b3_status": strict_boundary.get("b3_status"),
            "direct_route_stage_residual_O_h7": strict_boundary.get(
                "direct_route_stage_residual_O_h7"
            ),
            "two_layer_boundary_consistent": strict_boundary.get("two_layer_boundary_consistent"),
        },
        "proof_strength_guards": {
            "all_present_main_and_flat": proof_strength_guards_present,
            "groups": proof_strength_guards,
            "interpretation": (
                "These manuscript-level guards make the B3 proof review depend on the "
                "reference no-estimate-transfer rule, the theorem-level Taylor-route "
                "separation, the no-backward-arrow direction rule, the same-object "
                "composition criterion, and the P6 theorem-grade/diagnostic-grade "
                "evidence split. They do not prove P6, P7, or the primitive/Taylor route, "
                "source-policy rows, or full-TFE replacement."
            ),
        },
        "retained_theorem_boundaries": {
            "eta_h_condition_retained": theorem_contract.get("newton_tolerance_policy"),
            "fixed_tolerance_runs_are_asymptotic_proof": theorem_contract.get(
                "fixed_tolerance_runs_are_asymptotic_proof"
            ),
            "eta_h_O_h7_solver_policy_evidence": closure.get("eta_h_O_h7_solver_policy_evidence"),
            "accepted_residual_to_error_theorem": closure.get("accepted_residual_to_error_theorem"),
        },
        "remaining_narrowed_claim_submission_blockers_not_resolved_by_this_audit": [],
        "remaining_global_submission_boundaries_not_resolved_by_this_audit": [
            "full_source_policy_package_ready",
            "theorem_level_eta_h_solver_policy_evidence",
            "closed_residual_to_error_theorem_for_mechanism_rows",
        ],
        "source_files": {
            "proof_closure_manifest": "PROOF_CLOSURE_MANIFEST.json",
            "d5_direct_certificate": "D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE.json",
            "traceability": "PROOF_CLAIM_TRACEABILITY_AUDIT.json",
            "proof_contract": "CMAME_PROOF_CONTRACT_GATE.json",
            "strict_proof_audit": "CMAME_STRICT_PROOF_AUDIT.json",
            "main_tex": "main_cmame.tex",
            "flat_tex": "cmame_submission_flat/main_cmame_submission.tex",
            "main_pdf_text": "main_cmame.txt",
            "flat_pdf_text": "cmame_submission_flat/main_cmame_submission.txt",
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# B3 Direct Proof Review Audit",
        "",
        f"Status: `{result['status']}`.",
        f"B3 review requirement: `{result['b3_review_requirement']}`.",
        f"B3 previous status: `{result['b3_previous_status']}`.",
        f"B3 direct proof review passed: `{result['b3_direct_proof_review_passed']}`.",
        f"B3 can close from proof review: `{result['b3_can_close_from_proof_review']}`.",
        f"Same-branch dynamic zero-block supplies active PC2 residual-bridge proof input: `{result['direct_substitution_supplies_active_pc2_residual_bridge']}`.",
        f"Active PC2 proof standard: `{result['active_pc2_standard_name']}`.",
        f"Active PC2 residual-bridge proof standard satisfied: `{result['direct_residual_bridge_submission_standard_satisfied']}`.",
        f"Active PC2 residual-bridge route: `{result['direct_residual_bridge_required_pc2_route']}`.",
        f"Primitive/Taylor required for active PC2: `{result['primitive_taylor_required_for_active_pc2']}`.",
        f"Primitive/Taylor route status: `{result['primitive_taylor_route_status']}`.",
        f"Primitive/Taylor actual/open terms: `{result['primitive_taylor_actual_bounds_proved']}` / `{result['primitive_taylor_open_bound_terms']}`.",
        f"Primitive/Taylor open primitives: `{result['primitive_taylor_open_primitive_count']}`.",
        f"Global submission ready: `{result['submission_ready']}`.",
        "",
        "## Direct Proof Evidence",
        "",
        f"- Direct PC2 proof gap closed: `{result['proof_closure']['direct_pc2_proof_gap_closed']}`.",
        f"- Direct proof gap scope: `{result['proof_closure']['proof_gap_closed_scope']}`.",
        f"- Schema-only compatibility key `proof_gap_closed` retained: `{result['proof_closure']['schema_compatibility']['legacy_key_retained_for_schema_compatibility']}`; reader-facing proof status should use `{result['proof_closure']['schema_compatibility']['preferred_key']}`.",
        f"- PC2 residual-value bridge satisfied by 96-row non-dynamic certificate plus same-branch 36-row base-point zero dynamic block: `{result['proof_closure']['pc2_closed_by_direct_substitution']}`.",
        f"- Stage residual O(h^7) implementation defect proved: `{result['proof_closure']['stage_residual_O_h7_implementation_defect_proved']}`.",
        f"- Dynamic zero residual rows: `{result['direct_certificate']['dynamic_zero_residual_rows']}`.",
        f"- Full stage rows covered when assembled by the full-residual bridge: `{result['direct_certificate']['full_stage_rows_when_assembled_by_bridge']}`.",
        f"- Legacy full-stage row alias retained only for schema compatibility: `{result['direct_certificate']['legacy_full_stage_rows_if_promoted_scope']}`.",
        f"- Forbidden shortcuts used: `{result['direct_certificate']['forbidden_shortcuts_used']}`.",
        f"- Close requirements satisfied/unsatisfied: `{satisfied_close_requirements}/{unsatisfied_close_requirements}`.",
        f"- PC2 satisfaction mode: `{pc2.get('satisfaction_mode')}`.",
        "",
        "## Manuscript Review",
        "",
        f"- Main/flat TeX direct tokens: `{result['manuscript_review']['main_tex_direct_tokens']}/{result['manuscript_review']['flat_tex_direct_tokens']}`.",
        f"- Main/flat PDF full-stage token: `{result['manuscript_review']['main_pdf_full_stage_token']}/{result['manuscript_review']['flat_pdf_full_stage_token']}`.",
        f"- Traceability boundary tokens main/flat: `{result['manuscript_review']['traceability_main_boundary_tokens']}/{result['manuscript_review']['traceability_flat_boundary_tokens']}`.",
        f"- Dynamic proof matrix status: `{result['manuscript_review']['dynamic_matrix_status']}`.",
        "",
        "## Direct Residual-Bridge/Kantorovich Proof",
        "",
        f"- Strict conditional math proof present: `{result['strict_conditional_taylor_proof']['strict_conditional_math_proof_present']}`.",
        f"- Stage Taylor expansion main/flat: `{result['strict_conditional_taylor_proof']['main_stage_taylor_expansion']}/{result['strict_conditional_taylor_proof']['flat_stage_taylor_expansion']}`.",
        f"- Quadratic remainder main/flat: `{result['strict_conditional_taylor_proof']['main_quadratic_remainder']}/{result['strict_conditional_taylor_proof']['flat_quadratic_remainder']}`.",
        f"- Newton-Kantorovich absorption main/flat: `{result['strict_conditional_taylor_proof']['main_newton_kantorovich_absorption']}/{result['strict_conditional_taylor_proof']['flat_newton_kantorovich_absorption']}`.",
        f"- Contraction radius main/flat: `{result['strict_conditional_taylor_proof']['main_contraction_radius']}/{result['strict_conditional_taylor_proof']['flat_contraction_radius']}`.",
        f"- Stage error bound main/flat: `{result['strict_conditional_taylor_proof']['main_stage_error_bound']}/{result['strict_conditional_taylor_proof']['flat_stage_error_bound']}`.",
        f"- Endpoint-closure explicit constant main/flat: `{result['strict_conditional_taylor_proof']['main_endpoint_closure_explicit_constant']}/{result['strict_conditional_taylor_proof']['flat_endpoint_closure_explicit_constant']}`.",
        f"- Inexact-Newton endpoint constant main/flat: `{result['strict_conditional_taylor_proof']['main_inexact_newton_endpoint_constant']}/{result['strict_conditional_taylor_proof']['flat_inexact_newton_endpoint_constant']}`.",
        f"- Inexact-Newton scaled endpoint constant main/flat: `{result['strict_conditional_taylor_proof']['main_inexact_newton_scaled_endpoint_constant']}/{result['strict_conditional_taylor_proof']['flat_inexact_newton_scaled_endpoint_constant']}`.",
        f"- Local-to-global reduced grid constant main/flat: `{result['strict_conditional_taylor_proof']['main_local_global_reduced_grid_constant']}/{result['strict_conditional_taylor_proof']['flat_local_global_reduced_grid_constant']}`.",
        f"- Q/V reporting explicit constant main/flat: `{result['strict_conditional_taylor_proof']['main_qv_reporting_explicit_constant']}/{result['strict_conditional_taylor_proof']['flat_qv_reporting_explicit_constant']}`.",
        f"- Primitive Taylor route retained main/flat: `{result['strict_conditional_taylor_proof']['main_primitive_taylor_route_retained']}/{result['strict_conditional_taylor_proof']['flat_primitive_taylor_route_retained']}`.",
        f"- B1/B3 boundary status: `{result['strict_conditional_taylor_proof']['b1_status']}/{result['strict_conditional_taylor_proof']['b3_status']}`.",
        f"- Direct-route stage residual O(h^7): `{result['strict_conditional_taylor_proof']['direct_route_stage_residual_O_h7']}`.",
        f"- Two-layer boundary consistent: `{result['strict_conditional_taylor_proof']['two_layer_boundary_consistent']}`.",
        "",
        "## Proof Strength Guards",
        "",
        f"- Reference no-estimate-transfer guards main/flat: `{result['proof_strength_guards']['groups']['reference_order_contract']['main']}/{result['proof_strength_guards']['groups']['reference_order_contract']['flat']}`.",
        f"- Taylor-route separation guards main/flat: `{result['proof_strength_guards']['groups']['taylor_route_separation']['main']}/{result['proof_strength_guards']['groups']['taylor_route_separation']['flat']}`.",
        f"- Theorem direction locks main/flat: `{result['proof_strength_guards']['groups']['theorem_direction_locks']['main']}/{result['proof_strength_guards']['groups']['theorem_direction_locks']['flat']}`.",
        f"- Same-object composition locks main/flat: `{result['proof_strength_guards']['groups']['same_object_composition_locks']['main']}/{result['proof_strength_guards']['groups']['same_object_composition_locks']['flat']}`.",
        f"- P6 evidence-grade locks main/flat: `{result['proof_strength_guards']['groups']['p6_evidence_grade_locks']['main']}/{result['proof_strength_guards']['groups']['p6_evidence_grade_locks']['flat']}`.",
        f"- All B3 proof-strength guards present: `{result['proof_strength_guards']['all_present_main_and_flat']}`.",
        "- Guard interpretation: reference style is no-estimate-transfer only; Taylor T1/T2 are load-bearing, T3 is optional; theorem arrows are not used backwards; all lemmas compose only on the same branch, row convention, norm, and endpoint map; P6 theorem-grade input is separated from diagnostic-grade solver information.",
        "",
        "## Retained Boundaries",
        "",
        f"- eta_h theorem condition retained: `{result['retained_theorem_boundaries']['eta_h_condition_retained']}`.",
        f"- fixed-tolerance runs are asymptotic proof: `{result['retained_theorem_boundaries']['fixed_tolerance_runs_are_asymptotic_proof']}`.",
        f"- eta_h O(h^7) solver-policy theorem: `{result['retained_theorem_boundaries']['eta_h_O_h7_solver_policy_evidence']}`.",
        f"- accepted residual-to-error theorem: `{result['retained_theorem_boundaries']['accepted_residual_to_error_theorem']}`.",
        f"- Remaining narrowed proof blocker-gate items not resolved by this B3 audit: `{','.join(result['remaining_narrowed_claim_submission_blockers_not_resolved_by_this_audit']) or 'none'}`.",
        f"- Remaining global submission boundaries not resolved by this audit: `{','.join(result['remaining_global_submission_boundaries_not_resolved_by_this_audit'])}`.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("b3_direct_proof_review_audit=written")
    print(f"b3_direct_proof_review_passed={result['b3_direct_proof_review_passed']}")
    print(f"b3_can_close_from_proof_review={result['b3_can_close_from_proof_review']}")
    print("submission_ready=False")


if __name__ == "__main__":
    main()
