#!/usr/bin/env python3
"""Validate the D5 conditional Taylor-bound certificate."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
CERT_JSON = PAPER / "D5_CONDITIONAL_TAYLOR_CERTIFICATE.json"
CERT_MD = PAPER / "D5_CONDITIONAL_TAYLOR_CERTIFICATE.md"
OPEN_PRIMITIVES = {
    "P_state_lift",
    "P_acceleration_lift",
    "P_multiplier_lift",
    "P_geometry_lift",
    "P_gyroscopic_lift",
}
PROVED_PRIMITIVES = {"P_uniform_tube_constants"}


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


def key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        row.get("stage"),
        row.get("body"),
        row.get("global_row"),
        row.get("component"),
        row.get("balance_block"),
        row.get("term_id"),
    )


def main() -> int:
    checks = Checks()
    try:
        cert = read_json(CERT_JSON)
        cert_md = CERT_MD.read_text(encoding="utf-8", errors="replace")
        term_budget = read_json(PAPER / "D5_TAYLOR_TERM_BUDGET_AUDIT.json")
        primitive_reduction = read_json(PAPER / "D5_PRIMITIVE_BOUND_REDUCTION_AUDIT.json")
        p_tube = read_json(PAPER / "D5_P_TUBE_CONSTANTS_AUDIT.json")
        closure_plan = read_json(PAPER / "D5_PRIMITIVE_OBLIGATION_CLOSURE_PLAN.json")
        open_gap = read_json(PAPER / "D5_OPEN_PRIMITIVE_GAP_AUDIT.json")
    except Exception as exc:  # noqa: BLE001
        print(f"D5 conditional Taylor certificate validation: FAIL\n- {exc}")
        return 1

    summary = cert.get("summary", {})
    source = cert.get("source_consistency", {})
    manuscript = cert.get("manuscript_link", {})
    anti = cert.get("anti_overclaim", {})
    route_separation = cert.get("route_separation", {})
    reference_boundary = cert.get("reference_proof_boundary", {})
    terms = cert.get("conditional_terms", [])
    rows = cert.get("row_certificates", [])
    template_library = cert.get("strict_taylor_template_library", {})
    template_status = cert.get("strict_taylor_template_status", {})
    readiness_boundary = cert.get("readiness_boundary", {})
    remaining_gate_scope = cert.get("remaining_gate_scope", {})
    expected_global_boundaries = [
        "full_source_policy_package_ready",
        "theorem_level_eta_h_solver_policy_evidence",
        "closed_residual_to_error_theorem_for_mechanism_rows",
    ]

    checks.check(cert.get("schema") == "d5-conditional-taylor-certificate-v1", "schema changed")
    checks.check(
        cert.get("status") == "conditional_taylor_certificate_recorded_primitive_taylor_pc2_open",
        "status changed",
    )
    checks.check(cert.get("read_only") is True, "certificate must be read-only")
    checks.check(cert.get("run_v047_invoked") is False, "run_v047 must not be invoked")
    checks.check(cert.get("submission_ready") is False, "submission readiness overclaimed")
    checks.check(
        cert.get("submission_ready_scope")
        == "d5_conditional_taylor_global_boundary_not_narrowed_claim_package_decision",
        "submission-ready scope changed",
    )
    checks.check(
        readiness_boundary.get("conditional_taylor_certificate_scope")
        == "conditional_162_subterm_implication_under_open_primitives_not_actual_taylor_bound_closure",
        "conditional Taylor certificate scope changed",
    )
    checks.check(
        readiness_boundary.get("open_primitive_assumptions") == sorted(OPEN_PRIMITIVES),
        "readiness-boundary open primitive assumptions changed",
    )
    checks.check(
        readiness_boundary.get("narrowed_claim_package_decision_not_made_by_this_certificate") is True,
        "narrowed-claim decision boundary missing",
    )
    checks.check(
        readiness_boundary.get("global_submission_boundaries_retained") == expected_global_boundaries,
        "readiness-boundary global submission boundaries changed",
    )
    checks.check(
        cert.get("remaining_global_submission_boundaries") == expected_global_boundaries,
        "remaining global submission boundaries changed",
    )
    checks.check(
        remaining_gate_scope.get("global_submission_boundaries_retained") == expected_global_boundaries,
        "remaining gate global boundaries changed",
    )
    checks.check(
        remaining_gate_scope.get("narrowed_claim_package_decision_not_made_by_this_certificate") is True,
        "remaining gate narrowed-claim boundary missing",
    )
    checks.check(cert.get("pc2_closed") is False, "PC2 unexpectedly closed")
    checks.check(cert.get("proof_gap_closed") is False, "proof gap unexpectedly closed")
    checks.check(
        cert.get("stage_residual_O_h7_implementation_defect_proved") is False,
        "O(h^7) implementation defect unexpectedly proved",
    )
    checks.check(cert.get("conditional_certificate_only") is True, "conditional-only marker missing")
    checks.check(summary.get("dynamic_rows") == 36, "dynamic row count changed")
    checks.check(summary.get("term_rows") == 162, "Taylor term count changed")
    checks.check(
        summary.get("conditional_term_bounds_under_open_primitive_assumptions") == 162,
        "conditional term coverage changed",
    )
    checks.check(
        summary.get("conditional_dynamic_rows_under_open_primitive_assumptions") == 36,
        "conditional row coverage changed",
    )
    checks.check(summary.get("actual_taylor_bounds_proved") == 0, "actual Taylor bounds overclaimed")
    checks.check(summary.get("actual_dynamic_rows_proved") == 0, "actual dynamic rows overclaimed")
    checks.check(summary.get("open_primitive_assumption_count") == 5, "open primitive count changed")
    checks.check(summary.get("proved_primitive_count") == 1, "proved primitive count changed")
    checks.check(summary.get("mismatch_count") == 0, "term/reduction mismatches present")
    checks.check(summary.get("strict_taylor_templates_recorded") == 4, "strict Taylor template count changed")
    checks.check(
        remaining_gate_scope.get("actual_taylor_bounds_proved")
        == summary.get("actual_taylor_bounds_proved")
        == 0,
        "remaining gate overclaims actual Taylor bounds",
    )
    checks.check(
        remaining_gate_scope.get("open_primitive_assumption_count")
        == summary.get("open_primitive_assumption_count")
        == 5,
        "remaining gate open primitive count changed",
    )
    checks.check(
        remaining_gate_scope.get("pc2_closed") is False
        and remaining_gate_scope.get("proof_gap_closed") is False,
        "remaining gate overclaims PC2 or proof-gap closure",
    )
    checks.check(
        remaining_gate_scope.get("conditional_templates_not_additive_proof_evidence") is True,
        "remaining gate lost non-additive Taylor boundary",
    )
    checks.check(
        remaining_gate_scope.get("conditional_templates_not_spliced_with_direct_pc2_bridge") is True,
        "remaining gate lost Taylor/direct-PC2 no-splicing boundary",
    )
    checks.check(cert.get("mismatches") == [], "mismatch list is nonempty")
    expected_usage = {
        "P_acceleration_lift": 36,
        "P_geometry_lift": 36,
        "P_gyroscopic_lift": 18,
        "P_multiplier_lift": 72,
        "P_state_lift": 126,
        "P_uniform_tube_constants": 162,
    }
    checks.check(
        summary.get("primitive_obligation_usage") == expected_usage,
        "primitive obligation usage changed",
    )
    checks.check(
        summary.get("reduction_group_usage")
        == {
            "acceleration_lift": 36,
            "gyroscopic_bilinear_lift": 18,
            "multiplier_geometry_lift": 36,
            "smooth_force_torque_lift": 72,
        },
        "reduction-group usage changed",
    )
    expected_templates = {
        "acceleration_lift": {
            "template_kind": "exact_linear_no_remainder",
            "term_rows": 36,
            "must_contain": ["m_b delta a", "J_b delta alpha", "P_acceleration_lift"],
        },
        "smooth_force_torque_lift": {
            "template_kind": "first_order_taylor_integral_remainder",
            "term_rows": 72,
            "must_contain": ["int_0^1 DF", "P_state_lift"],
        },
        "multiplier_geometry_lift": {
            "template_kind": "product_taylor_mean_value",
            "term_rows": 36,
            "must_contain": ["int_0^1 DA", "P_multiplier_lift"],
        },
        "gyroscopic_bilinear_lift": {
            "template_kind": "exact_bilinear_difference",
            "term_rows": 18,
            "must_contain": ["delta w x J", "P_gyroscopic_lift"],
        },
    }
    checks.check(set(template_library) == set(expected_templates), "strict Taylor template keys changed")
    checks.check(template_status.get("template_count") == 4, "template status count changed")
    checks.check(template_status.get("template_rows_sum") == 162, "template row sum changed")
    checks.check(
        template_status.get("all_templates_are_taylor_or_exact_linear") is True,
        "Taylor/exact-linear marker missing",
    )
    checks.check(template_status.get("uses_direct_substitution") is False, "template uses direct substitution")
    checks.check(
        template_status.get("uses_residual_to_error_promotion") is False,
        "template uses residual-to-error promotion",
    )
    checks.check(template_status.get("finite_probe_used_as_proof") is False, "finite probe used as proof")
    for name, expected in expected_templates.items():
        template = template_library.get(name, {})
        checks.check(
            template.get("template_kind") == expected["template_kind"],
            f"template kind changed: {name}",
        )
        checks.check(template.get("term_rows") == expected["term_rows"], f"template rows changed: {name}")
        checks.check(template.get("uses_direct_substitution") is False, f"template overclaims direct route: {name}")
        text = " ".join(
            str(template.get(field, ""))
            for field in ["formula", "bound", "primitive_inputs"]
        )
        for token in expected["must_contain"]:
            checks.check(token in text, f"template {name} missing token: {token}")
    checks.check(source.get("term_budget_terms") == 162, "term budget source count changed")
    checks.check(source.get("term_budget_certified_terms") == 0, "term budget overclaims certified terms")
    checks.check(source.get("term_budget_pc2_closed") is False, "term budget unexpectedly closes PC2")
    checks.check(source.get("primitive_reduction_terms") == 162, "primitive reduction term count changed")
    checks.check(source.get("primitive_reduction_rules") == 162, "primitive reduction rule count changed")
    checks.check(
        source.get("primitive_reduction_term_bounds_proved") == 0,
        "primitive reduction overclaims term bounds",
    )
    checks.check(
        source.get("primitive_reduction_pc2_closed") is False,
        "primitive reduction unexpectedly closes PC2",
    )
    checks.check(
        source.get("p_tube_closed") is True and p_tube.get("primitive_closed") is True,
        "P_tube closure not linked",
    )
    checks.check(source.get("p_tube_pc2_closed") is False, "P_tube unexpectedly closes PC2")
    checks.check(
        source.get("closure_plan_open_primitives") == 5
        and closure_plan.get("summary", {}).get("open_primitive_obligations") == 5,
        "closure-plan open primitive count changed",
    )
    checks.check(
        source.get("closure_plan_induced_bounds_proved") == 0,
        "closure plan unexpectedly proves induced bounds",
    )
    checks.check(source.get("closure_plan_pc2_closed") is False, "closure plan unexpectedly closes PC2")
    checks.check(
        source.get("open_gap_open_primitives") == 5
        and open_gap.get("summary", {}).get("open_primitive_count") == 5,
        "open primitive gap count changed",
    )
    checks.check(source.get("open_gap_pc2_closed") is False, "open gap unexpectedly closes PC2")
    checks.check(manuscript.get("main_tex_present") is True, "main TeX lemma link missing")
    checks.check(manuscript.get("flat_tex_present") is True, "flat TeX lemma link missing")
    checks.check(
        manuscript.get("tokens")
        == [
            r"\label{lem:d5-primitive-obligation-implication}",
            r"\label{cor:d5-p-acc-row-bound-under-pacc}",
            r"\label{cor:d5-smooth-force-row-bound-under-lifts}",
            "Assume the five remaining primitive obligations",
            "every D5 Taylor subterm",
            "The four Taylor templates are",
            "The conditional row-level acceleration version is",
            "row-level smooth force/torque/friction corollary then bounds the 72 smooth-map",
            "The conditional row-level smooth-map version is",
            "covers exactly the 72 external-force, friction-force, external-torque, and friction-torque",
            "does not turn the D4 direct-route smoothness certificate into a primitive-rate proof",
            "does not use the D4 direct-route smoothness certificate as a",
            "with zero Taylor remainder",
            "does not prove PA2 or the unweighted acceleration",
            "finite dependency certificate, not a generic smoothness assertion",
            "36\\ \\text{acceleration lift}",
            "72\\ \\text{smooth force/torque/friction lift}",
            "dependency graph is acyclic in the separate route",
            "every primitive subterm has an assigned template and primitive-input set",
            "not a projection of the accepted \\(132\\)-row direct residual estimate",
            "Taylor's formula with integral remainder",
            r"\int_0^1 DF",
            r"\int_0^1 DA",
            r"\widehat\omega\times J\widehat\omega-\omega\times J\omega",
            r"C_{\mathrm{D5},r}h^7",
            "finite primitive-row summation is the only aggregation step",
            "not an inverse projection from the aggregate 132-row residual estimate",
            "does not close the primitive-and-Taylor route to PC2",
            "not additive proof evidence",
            "conditional templates cannot be spliced",
            "Reference-proof boundary for the primitive Taylor route",
            "but it supplies no primitive FullVA lift estimate",
            "not a borrowed Taylor local-error theorem",
            "FullVA-specific finite implication",
            "the reference paper cannot close the primitive/Taylor status map or supply PC2",
            "primitive-route theorem would have to prove the five open primitive obligations",
            "redo the residual-to-root, endpoint, solver, and global-transfer chain",
        ],
        "manuscript Taylor template token set changed",
    )
    checks.check(
        reference_boundary.get("reference_role") == "proof_order_discipline_only",
        "reference proof role changed",
    )
    for key_name in [
        "imports_reference_taylor_estimate",
        "imports_reference_multiplier_recursion",
        "imports_reference_hidden_constraint_estimate",
        "reference_supplies_primitive_fullva_lift_estimate",
        "reference_closes_primitive_taylor_ledger",
        "reference_supplies_pc2",
    ]:
        checks.check(reference_boundary.get(key_name) is False, f"reference boundary overclaims: {key_name}")
    checks.check(
        reference_boundary.get("primitive_taylor_certificate_role")
        == "fullva_specific_finite_implication_under_open_primitive_inputs",
        "primitive Taylor certificate reference-boundary role changed",
    )
    for key_name in [
        "assumes_not_proves_five_open_primitives",
        "does_not_certify_actual_taylor_bounds",
        "does_not_close_pc2",
        "does_not_close_proof_gap",
        "does_not_mark_submission_ready",
        "finite_sum_constant_is_conditional_only",
        "finite_sum_not_inverse_projection_from_aggregate_residual",
        "conditional_templates_not_additive_proof_evidence",
        "conditional_templates_not_spliced_with_direct_pc2_bridge",
        "direct_pc2_bridge_does_not_close_primitive_route",
        "primitive_route_requires_five_lifts_and_redone_chain",
    ]:
        checks.check(anti.get(key_name) is True, f"anti-overclaim marker missing: {key_name}")
    checks.check(
        route_separation.get("load_bearing_route") == "direct_132_row_residual_bridge",
        "route separation load-bearing route changed",
    )
    checks.check(
        route_separation.get("diagnostic_route") == "conditional_primitive_taylor_template_library",
        "route separation diagnostic route changed",
    )
    for key_name in [
        "conditional_templates_not_additive_proof_evidence",
        "conditional_templates_not_spliced_with_direct_pc2_bridge",
        "finite_sum_row_constant_recorded",
        "finite_sum_not_inverse_projection_from_aggregate_residual",
        "direct_pc2_bridge_does_not_close_primitive_route",
        "primitive_route_must_prove_five_uniform_lift_primitives",
        "primitive_route_must_redo_residual_to_root_endpoint_solver_global_chain",
    ]:
        checks.check(
            route_separation.get(key_name) is True,
            f"route separation marker missing: {key_name}",
        )
    checks.check(
        route_separation.get("route_separation_scope")
        == (
            "conditional_taylor_templates_are_schema_only_until_their_own_"
            "primitive_lifts_and_full_perturbation_chain_close"
        ),
        "route separation scope changed",
    )

    budget_terms = {
        key(row): row for row in term_budget.get("term_rows", []) if isinstance(row, dict)
    }
    reduction_terms = {
        key(row): row for row in primitive_reduction.get("reduction_rows", []) if isinstance(row, dict)
    }
    checks.check(len(budget_terms) == 162, "budget term key count changed")
    checks.check(len(reduction_terms) == 162, "reduction term key count changed")
    checks.check(isinstance(terms, list) and len(terms) == 162, "conditional term list count changed")
    checks.check(isinstance(rows, list) and len(rows) == 36, "row certificate count changed")
    primitive_counter: Counter[str] = Counter()
    for term in terms:
        if not isinstance(term, dict):
            checks.check(False, "conditional term is not an object")
            continue
        term_key = key(term)
        checks.check(term_key in budget_terms, f"conditional term missing from budget: {term_key}")
        checks.check(term_key in reduction_terms, f"conditional term missing from reduction: {term_key}")
        obligations = term.get("primitive_obligations", [])
        checks.check("P_uniform_tube_constants" in obligations, "term missing P_tube")
        checks.check(
            set(term.get("proved_obligations", [])) == PROVED_PRIMITIVES,
            "proved obligation set changed",
        )
        checks.check(
            set(term.get("open_obligations_assumed", [])).issubset(OPEN_PRIMITIVES)
            and len(term.get("open_obligations_assumed", [])) >= 1,
            "open obligations are invalid or missing",
        )
        checks.check(term.get("unknown_obligations") == [], "unknown primitive obligation present")
        checks.check(
            term.get("conditional_bound_if_open_primitives_assumed") is True,
            "conditional bound marker missing",
        )
        checks.check(term.get("actual_taylor_bound_proved") is False, "actual Taylor bound overclaimed")
        checks.check(term.get("certifies_theorem_now") is False, "term theorem certification overclaimed")
        checks.check(term.get("required_bound") == "O(h^7)", "required bound changed")
        for item in obligations:
            primitive_counter[item] += 1
    checks.check(dict(sorted(primitive_counter.items())) == expected_usage, "term primitive counter changed")
    for row in rows:
        if not isinstance(row, dict):
            checks.check(False, "row certificate is not an object")
            continue
        block = row.get("balance_block")
        expected_terms = 4 if block == "translational_newton_balance" else 5
        checks.check(row.get("term_count") == expected_terms, "row term count changed")
        checks.check(row.get("expected_term_count") == expected_terms, "row expected term count changed")
        checks.check(row.get("conditional_terms") == expected_terms, "row conditional term count changed")
        checks.check(row.get("actual_terms_proved") == 0, "row actual term proof overclaimed")
        checks.check(
            row.get("conditional_row_bound_if_open_primitives_assumed") is True,
            "row conditional certificate missing",
        )
        checks.check(row.get("actual_row_bound_proved") is False, "row actual proof overclaimed")
    for token in [
        "conditional Taylor certificate recorded; primitive-and-Taylor PC2 route remains open",
        "Here `submission_ready=false` is scoped to the conditional Taylor/global proof-package boundary,",
        "not to the separate narrowed-claim package decision.",
        "Dynamic rows conditionally covered: `36/36`.",
        "Taylor subterms conditionally covered: `162/162`.",
        "Actual Taylor bounds proved: `0/162`.",
        "Conditional templates are additive proof evidence: `False`.",
        "Conditional templates spliced with direct PC2 bridge: `False`.",
        "Finite-sum row constant recorded: `True`.",
        "Finite-sum step is inverse projection from aggregate residual: `False`.",
        "Primitive route must prove five lift primitives and redo the perturbation chain: `True`.",
        "Reference proof imports Taylor estimate: `False`.",
        "Reference proof supplies primitive FullVA lift estimate: `False`.",
        "Reference proof closes primitive/Taylor ledger or PC2: `False/False`.",
        "Submission-ready scope: `d5_conditional_taylor_global_boundary_not_narrowed_claim_package_decision`.",
        "Conditional Taylor certificate scope: `conditional_162_subterm_implication_under_open_primitives_not_actual_taylor_bound_closure`.",
        "Remaining global submission boundaries: `full_source_policy_package_ready,theorem_level_eta_h_solver_policy_evidence,closed_residual_to_error_theorem_for_mechanism_rows`.",
        "`P_uniform_tube_constants` | `162` | `True` | `False`",
        "Primitive/Taylor Diagnostic Templates",
        "`smooth_force_torque_lift` | `first_order_taylor_integral_remainder`",
        "`multiplier_geometry_lift` | `product_taylor_mean_value`",
        "`gyroscopic_bilinear_lift` | `exact_bilinear_difference`",
        "The conditional templates are not additive proof evidence and cannot be spliced with the direct PC2 bridge.",
        "The Wieloch--Arnold constrained-BDF proof (`wieloch2021bdf`; local reference text `../../external/literature/1-s2.0-S0377042719305229-main.txt`) is invoked as proof-order discipline only; it does not import a Taylor estimate, primitive FullVA lift, multiplier recursion, hidden-constraint estimate, or PC2 input for this certificate.",
        "A primitive-route theorem would have to prove the five open primitive obligations and redo the residual-to-root, endpoint, solver, and global-transfer chain.",
        "It does not close the primitive-route proof gap or submission readiness; only the active direct PC2 residual-bridge proof-gap slot is closed elsewhere by the direct residual-bridge route.",
    ]:
        checks.check(token in cert_md, f"markdown token missing: {token}")

    if checks.errors:
        print("D5 conditional Taylor certificate validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("D5 conditional Taylor certificate validation: PASS")
    print("conditional_terms=162/162")
    print("conditional_rows=36/36")
    print("actual_taylor_bounds_proved=0")
    print("pc2_closed=False")
    print("submission_ready=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
