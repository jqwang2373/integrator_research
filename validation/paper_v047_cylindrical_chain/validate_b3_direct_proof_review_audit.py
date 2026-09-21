#!/usr/bin/env python3
"""Validate the B3 direct-proof review audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "B3_DIRECT_PROOF_REVIEW_AUDIT.json"
AUDIT_MD = PAPER / "B3_DIRECT_PROOF_REVIEW_AUDIT.md"
PROOF_CLOSURE = PAPER / "PROOF_CLOSURE_MANIFEST.json"
D5_DIRECT = PAPER / "D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE.json"
TRACEABILITY = PAPER / "PROOF_CLAIM_TRACEABILITY_AUDIT.json"
STRICT_PROOF_AUDIT = PAPER / "CMAME_STRICT_PROOF_AUDIT.json"


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(AUDIT_JSON)
        audit_md = read_text(AUDIT_MD)
        proof_closure = read_json(PROOF_CLOSURE)
        d5_direct = read_json(D5_DIRECT)
        traceability = read_json(TRACEABILITY)
        strict_proof_audit = read_json(STRICT_PROOF_AUDIT)
    except Exception as exc:  # noqa: BLE001
        print(f"b3_direct_proof_review_audit=FAIL\n- {exc}")
        return 1

    closure = proof_closure.get("closure_state", {})
    direct_summary = d5_direct.get("summary", {})
    proof = audit.get("proof_closure", {})
    direct = audit.get("direct_certificate", {})
    close_requirements = audit.get("close_requirements", {})
    manuscript = audit.get("manuscript_review", {})
    strict_conditional = audit.get("strict_conditional_taylor_proof", {})
    proof_strength_guards = audit.get("proof_strength_guards", {})
    proof_strength_groups = proof_strength_guards.get("groups", {})
    retained = audit.get("retained_theorem_boundaries", {})
    strict_features = strict_proof_audit.get("manuscript_strict_proof_features", {})
    strict_main = strict_features.get("main", {})
    strict_flat = strict_features.get("flat", {})
    strict_boundary = strict_proof_audit.get("two_layer_proof_boundary", {})

    checks.check(audit.get("schema") == "b3-direct-proof-review-audit-v1", "schema changed")
    checks.check(
        audit.get("status") == "b3_direct_proof_review_passed_residual_bridge_closure_closed",
        "status changed",
    )
    checks.check(audit.get("read_only_audit") is True, "audit should be read-only")
    checks.check(audit.get("submission_ready") is False, "audit must not claim submission ready")
    checks.check(
        audit.get("b3_review_requirement") == "direct_residual_bridge_kantorovich_route_closure",
        "B3 review requirement changed",
    )
    checks.check(audit.get("b3_direct_proof_review_passed") is True, "B3 proof review did not pass")
    checks.check(
        audit.get("b3_can_close_from_proof_review") is True,
        "direct proof review should close B3 under direct residual-bridge/Kantorovich standard",
    )
    checks.check(audit.get("b3_previous_status") == "closed", "B3 gate status changed unexpectedly")
    checks.check(
        audit.get("direct_substitution_supplies_active_pc2_residual_bridge") is True,
        "same-branch dynamic zero-block evidence not accepted as active residual-bridge proof input",
    )
    checks.check(
        audit.get("active_pc2_standard_name") == "strict_direct_residual_bridge_submission_standard"
        and "legacy_pc2_standard_alias" not in audit,
        "active PC2 proof-standard field missing or stale alias still present",
    )
    checks.check(
        audit.get("direct_residual_bridge_submission_standard_satisfied") is True
        and audit.get("direct_residual_bridge_required_pc2_route")
        == "direct_residual_bridge_kantorovich_route",
        "direct residual-bridge proof-standard field changed",
    )
    checks.check("primitive_taylor_required_pc2_route" not in audit, "stale primitive/Taylor required-route alias present")
    checks.check(
        audit.get("active_pc2_required_route") == "direct_residual_bridge_kantorovich_route",
        "active PC2 route changed",
    )
    checks.check(
        audit.get("primitive_taylor_required_for_active_pc2") is False,
        "primitive/Taylor route must remain non-required for active PC2",
    )
    checks.check(
        audit.get("primitive_taylor_route_status") == "conditional_schema_open_not_required_for_b3_closure",
        "primitive/Taylor route status changed",
    )
    checks.check(audit.get("primitive_taylor_actual_bounds_proved") == 0, "primitive/Taylor actual bounds changed")
    checks.check(audit.get("primitive_taylor_open_bound_terms") == 162, "primitive/Taylor open term count changed")
    checks.check(audit.get("primitive_taylor_open_primitive_count") == 5, "primitive/Taylor open primitive count changed")

    checks.check(
        proof.get("direct_pc2_proof_gap_closed")
        == closure.get("direct_pc2_proof_gap_closed", closure.get("proof_gap_closed"))
        is True,
        "direct PC2 proof gap not closed",
    )
    checks.check(
        proof.get("proof_gap_closed") == closure.get("proof_gap_closed") is True,
        "legacy proof gap not closed",
    )
    checks.check(
        proof.get("proof_gap_closed_scope")
        == closure.get("proof_gap_closed_scope")
        == "direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open",
        "proof gap scope changed",
    )
    checks.check(
        "schema-compatible shorthand for direct_pc2_proof_gap_closed"
        in proof.get("proof_gap_closed_reading_rule", ""),
        "proof gap reading rule missing direct-PC2 scope",
    )
    schema = proof.get("schema_compatibility", {})
    checks.check(
        schema.get("legacy_key") == "proof_gap_closed"
        and schema.get("legacy_key_retained_for_schema_compatibility") is True
        and schema.get("preferred_key") == "direct_pc2_proof_gap_closed",
        "proof gap schema-compatibility boundary missing",
    )
    checks.check(
        proof.get("pc2_closed_by_direct_substitution")
        == closure.get("pc2_closed_by_direct_substitution")
        is True,
        "PC2 direct closure not recorded",
    )
    checks.check(
        proof.get("stage_residual_O_h7_implementation_defect_proved")
        == closure.get("stage_residual_O_h7_implementation_defect_proved")
        is True,
        "stage residual proof not recorded",
    )
    checks.check(proof.get("primitive_lift_route_closed") is False, "primitive route should remain open")
    checks.check(proof.get("eta_h_O_h7_solver_policy_evidence") is False, "eta_h solver-policy theorem overclaimed")
    checks.check(proof.get("accepted_residual_to_error_theorem") is False, "residual-to-error theorem overclaimed")

    checks.check(
        direct.get("dynamic_zero_residual_rows")
        == direct_summary.get("dynamic_zero_residual_rows")
        == 36,
        "dynamic zero residual row count changed",
    )
    checks.check(
        direct.get("full_stage_rows_if_promoted")
        == direct_summary.get("full_stage_rows_if_promoted")
        == 132,
        "full stage row count changed",
    )
    checks.check(direct.get("direct_route_certificate_closed") is True, "direct certificate not closed")
    checks.check(direct.get("direct_route_non_circular") is True, "direct route non-circular marker missing")
    checks.check(direct.get("forbidden_shortcuts_used") == 0, "forbidden shortcuts were used")
    checks.check(direct.get("forbidden_shortcuts_clean") is True, "forbidden shortcut booleans not clean")

    checks.check(close_requirements.get("satisfied") == 4, "satisfied close requirement count changed")
    checks.check(close_requirements.get("unsatisfied") == 0, "unsatisfied close requirements remain")
    checks.check(
        "same-branch residual-value certificate" in close_requirements.get("pc2_satisfaction_mode", ""),
        "PC2 satisfaction mode is not the same-branch residual-value bridge",
    )

    checks.check(manuscript.get("main_tex_direct_tokens") is True, "main TeX direct proof tokens missing")
    checks.check(manuscript.get("flat_tex_direct_tokens") is True, "flat TeX direct proof tokens missing")
    checks.check(manuscript.get("main_pdf_full_stage_token") is True, "main PDF full-stage token missing")
    checks.check(manuscript.get("flat_pdf_full_stage_token") is True, "flat PDF full-stage token missing")
    checks.check(
        manuscript.get("traceability_main_boundary_tokens")
        == traceability.get("main_source", {}).get("all_boundary_tokens_present")
        is True,
        "main traceability boundary tokens missing",
    )
    checks.check(
        manuscript.get("traceability_flat_boundary_tokens")
        == traceability.get("flat_source", {}).get("all_boundary_tokens_present")
        is True,
        "flat traceability boundary tokens missing",
    )
    checks.check(
        manuscript.get("dynamic_matrix_status") == "present_direct_substitution_closure_inputs",
        "dynamic matrix status changed",
    )

    checks.check(
        strict_conditional.get("strict_conditional_math_proof_present")
        == strict_features.get("strict_conditional_math_proof_present")
        is True,
        "strict conditional math proof marker missing",
    )
    for key in [
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
    ]:
        checks.check(
            strict_conditional.get(f"main_{key}") == strict_main.get(key) is True,
            f"main direct residual-bridge proof feature missing: {key}",
        )
        checks.check(
            strict_conditional.get(f"flat_{key}") == strict_flat.get(key) is True,
            f"flat direct residual-bridge proof feature missing: {key}",
        )
    checks.check(
        strict_conditional.get("b1_status") == strict_boundary.get("b1_status") == "closed",
        "B1 strict boundary status changed",
    )
    checks.check(
        strict_conditional.get("b3_status") == strict_boundary.get("b3_status") == "closed",
        "B3 strict boundary status changed",
    )
    checks.check(
        strict_conditional.get("direct_route_stage_residual_O_h7")
        == strict_boundary.get("direct_route_stage_residual_O_h7")
        is True,
        "direct-route O(h^7) stage residual marker missing",
    )
    checks.check(
        strict_conditional.get("two_layer_boundary_consistent")
        == strict_boundary.get("two_layer_boundary_consistent")
        is True,
        "two-layer proof boundary consistency marker missing",
    )
    expected_guard_groups = {
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
    checks.check(
        proof_strength_guards.get("all_present_main_and_flat") is True,
        "B3 proof-strength guards are not all present",
    )
    interpretation = proof_strength_guards.get("interpretation", "")
    for token in [
        "reference no-estimate-transfer rule",
        "theorem-level Taylor-route separation",
        "no-backward-arrow direction rule",
        "same-object composition criterion",
        "P6 theorem-grade/diagnostic-grade evidence split",
        "do not prove P6, P7, or the primitive/Taylor route",
    ]:
        checks.check(token in interpretation, f"proof-strength guard interpretation missing: {token}")
    for group_name, keys in expected_guard_groups.items():
        group = proof_strength_groups.get(group_name, {})
        checks.check(group.get("keys") == keys, f"proof-strength guard keys changed for {group_name}")
        checks.check(group.get("main") is True, f"main proof-strength guard missing: {group_name}")
        checks.check(group.get("flat") is True, f"flat proof-strength guard missing: {group_name}")
        for key in keys:
            checks.check(strict_main.get(key) is True, f"strict main feature missing for B3 guard: {key}")
            checks.check(strict_flat.get(key) is True, f"strict flat feature missing for B3 guard: {key}")

    checks.check(
        retained.get("eta_h_condition_retained") == "eta_h^tube <= c_eta h^7 for asymptotic proof",
        "eta_h theorem condition changed",
    )
    checks.check(
        retained.get("fixed_tolerance_runs_are_asymptotic_proof") is False,
        "fixed tolerance overclaimed",
    )
    checks.check(retained.get("eta_h_O_h7_solver_policy_evidence") is False, "eta_h solver-policy theorem overclaimed")
    checks.check(retained.get("accepted_residual_to_error_theorem") is False, "residual-to-error overclaimed")
    checks.check(
        audit.get("remaining_narrowed_claim_submission_blockers_not_resolved_by_this_audit") == [],
        "narrowed-claim blocker list changed",
    )
    checks.check(
        audit.get("remaining_global_submission_boundaries_not_resolved_by_this_audit")
        == [
            "full_source_policy_package_ready",
            "theorem_level_eta_h_solver_policy_evidence",
            "closed_residual_to_error_theorem_for_mechanism_rows",
        ],
        "remaining global submission boundaries changed",
    )

    for token in [
        "B3 direct proof review passed: `True`.",
        "B3 can close from proof review: `True`.",
        "Same-branch dynamic zero-block supplies active PC2 residual-bridge proof input: `True`.",
        "Active PC2 residual-bridge proof standard satisfied: `True`.",
        "Primitive/Taylor actual/open terms: `0` / `162`.",
        "Primitive/Taylor open primitives: `5`.",
        "Direct PC2 proof gap closed: `True`.",
        "PC2 residual-value bridge satisfied by 96-row non-dynamic certificate plus same-branch 36-row base-point zero dynamic block: `True`.",
        "Stage residual O(h^7) implementation defect proved: `True`.",
        "Dynamic zero residual rows: `36`.",
        "Full stage rows covered when assembled by the full-residual bridge: `132`.",
        "Forbidden shortcuts used: `0`.",
        "Close requirements satisfied/unsatisfied: `4/0`.",
        "Strict conditional math proof present: `True`.",
        "Stage Taylor expansion main/flat: `True/True`.",
        "Quadratic remainder main/flat: `True/True`.",
        "Newton-Kantorovich absorption main/flat: `True/True`.",
        "Contraction radius main/flat: `True/True`.",
        "Stage error bound main/flat: `True/True`.",
        "Endpoint-closure explicit constant main/flat: `True/True`.",
        "Inexact-Newton endpoint constant main/flat: `True/True`.",
        "Inexact-Newton scaled endpoint constant main/flat: `True/True`.",
        "Local-to-global reduced grid constant main/flat: `True/True`.",
        "Q/V reporting explicit constant main/flat: `True/True`.",
        "Primitive Taylor route retained main/flat: `True/True`.",
        "B1/B3 boundary status: `closed/closed`.",
        "Direct-route stage residual O(h^7): `True`.",
        "Two-layer boundary consistent: `True`.",
        "Reference no-estimate-transfer guards main/flat: `True/True`.",
        "Taylor-route separation guards main/flat: `True/True`.",
        "Theorem direction locks main/flat: `True/True`.",
        "Same-object composition locks main/flat: `True/True`.",
        "P6 evidence-grade locks main/flat: `True/True`.",
        "All B3 proof-strength guards present: `True`.",
        "Guard interpretation: reference style is no-estimate-transfer only; Taylor T1/T2 are load-bearing, T3 is optional; theorem arrows are not used backwards; all lemmas compose only on the same branch, row convention, norm, and endpoint map; P6 theorem-grade input is separated from diagnostic-grade solver information.",
        "Remaining narrowed proof blocker-gate items not resolved by this B3 audit: `none`.",
        "Remaining global submission boundaries not resolved by this audit: `full_source_policy_package_ready,theorem_level_eta_h_solver_policy_evidence,closed_residual_to_error_theorem_for_mechanism_rows`.",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("b3_direct_proof_review_audit=FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("b3_direct_proof_review_audit=PASS")
    print("b3_direct_proof_review_passed=True")
    print("b3_can_close_from_proof_review=True")
    print("submission_ready=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
