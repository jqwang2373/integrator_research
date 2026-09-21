#!/usr/bin/env python3
"""Build the D5 conditional Taylor-bound certificate.

This certificate checks the finite implication used by
Lemma~\\ref{lem:d5-primitive-obligation-implication}: if the five open
primitive lift/bilinear obligations are assumed in addition to the closed
compact-tube constants, every recorded D5 Taylor subterm is conditionally
O(h^7).  It does not prove those primitive obligations or close the primitive/Taylor PC2 route.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
OUT_JSON = PAPER / "D5_CONDITIONAL_TAYLOR_CERTIFICATE.json"
OUT_MD = PAPER / "D5_CONDITIONAL_TAYLOR_CERTIFICATE.md"

OPEN_PRIMITIVES = {
    "P_state_lift",
    "P_acceleration_lift",
    "P_multiplier_lift",
    "P_geometry_lift",
    "P_gyroscopic_lift",
}
PROVED_PRIMITIVES = {"P_uniform_tube_constants"}
TAYLOR_TEMPLATE_LIBRARY = {
    "acceleration_lift": {
        "template_kind": "exact_linear_no_remainder",
        "term_rows": 36,
        "term_ids": ["T_acceleration_lift", "R_angular_acceleration_lift"],
        "formula": "L(Ahat)-L(A)=m_b delta a or J_b delta alpha",
        "bound": "||L(Ahat)-L(A)|| <= C_acc ||delta A|| = O(h^7) under P_acceleration_lift",
        "primitive_inputs": ["P_acceleration_lift", "P_uniform_tube_constants"],
        "uses_direct_substitution": False,
    },
    "smooth_force_torque_lift": {
        "template_kind": "first_order_taylor_integral_remainder",
        "term_rows": 72,
        "term_ids": [
            "T_external_force_lift",
            "T_friction_force_lift",
            "R_external_torque_lift",
            "R_friction_torque_lift",
        ],
        "formula": "F(zhat)-F(z)=int_0^1 DF(z+theta delta z) delta z dtheta",
        "bound": "||F(zhat)-F(z)|| <= L_F ||delta z|| = O(h^7) under P_state_lift and, where present, P_multiplier_lift",
        "primitive_inputs": [
            "P_state_lift",
            "P_multiplier_lift",
            "P_uniform_tube_constants",
        ],
        "uses_direct_substitution": False,
    },
    "multiplier_geometry_lift": {
        "template_kind": "product_taylor_mean_value",
        "term_rows": 36,
        "term_ids": ["T_multiplier_force_lift", "R_multiplier_torque_lift"],
        "formula": "A(qhat)^T lambdahat-A(q)^T lambda=A(q)^T delta lambda+(int_0^1 DA(q+theta delta q)[delta q] dtheta)^T lambdahat",
        "bound": "||delta(A^T lambda)|| <= C_A (||delta q||+||delta lambda||) = O(h^7) under P_state_lift and P_multiplier_lift",
        "primitive_inputs": [
            "P_state_lift",
            "P_multiplier_lift",
            "P_geometry_lift",
            "P_uniform_tube_constants",
        ],
        "uses_direct_substitution": False,
    },
    "gyroscopic_bilinear_lift": {
        "template_kind": "exact_bilinear_difference",
        "term_rows": 18,
        "term_ids": ["R_gyroscopic_lift"],
        "formula": "what x J what - w x J w = delta w x J what + w x J delta w",
        "bound": "||delta(omega x J omega)|| <= C_gyro ||delta omega|| = O(h^7) under P_state_lift",
        "primitive_inputs": ["P_state_lift", "P_gyroscopic_lift", "P_uniform_tube_constants"],
        "uses_direct_substitution": False,
    },
}


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        row.get("stage"),
        row.get("body"),
        row.get("global_row"),
        row.get("component"),
        row.get("balance_block"),
        row.get("term_id"),
    )


def contains_normalized(text: str, token: str) -> bool:
    return token in text or " ".join(token.split()) in " ".join(text.split())


def main() -> None:
    term_budget = read_json(PAPER / "D5_TAYLOR_TERM_BUDGET_AUDIT.json")
    primitive_reduction = read_json(PAPER / "D5_PRIMITIVE_BOUND_REDUCTION_AUDIT.json")
    p_tube = read_json(PAPER / "D5_P_TUBE_CONSTANTS_AUDIT.json")
    closure_plan = read_json(PAPER / "D5_PRIMITIVE_OBLIGATION_CLOSURE_PLAN.json")
    open_gap = read_json(PAPER / "D5_OPEN_PRIMITIVE_GAP_AUDIT.json")
    main_tex = read_text(LATEX / "main_cmame.tex")
    flat_tex = read_text(LATEX / "cmame_submission_flat" / "main_cmame_submission.tex")

    reduction_by_key = {
        key(row): row for row in primitive_reduction.get("reduction_rows", []) if isinstance(row, dict)
    }
    term_rows = [row for row in term_budget.get("term_rows", []) if isinstance(row, dict)]
    if len(reduction_by_key) != len(term_rows):
        raise ValueError("D5 reduction rows do not match Taylor term rows")

    conditional_terms: list[dict[str, Any]] = []
    primitive_usage: Counter[str] = Counter()
    reduction_group_usage: Counter[str] = Counter()
    row_terms: dict[int, list[dict[str, Any]]] = defaultdict(list)
    mismatches: list[str] = []

    for term in term_rows:
        reduction = reduction_by_key.get(key(term))
        if reduction is None:
            mismatches.append(f"missing reduction row for {key(term)}")
            continue
        if reduction.get("term_id") != term.get("term_id"):
            mismatches.append(f"term id mismatch for {key(term)}")
            continue

        obligations = list(reduction.get("primitive_obligations", []))
        open_obligations = [item for item in obligations if item in OPEN_PRIMITIVES]
        proved_obligations = [item for item in obligations if item in PROVED_PRIMITIVES]
        unknown_obligations = [
            item for item in obligations if item not in OPEN_PRIMITIVES and item not in PROVED_PRIMITIVES
        ]
        for item in obligations:
            primitive_usage[item] += 1
        reduction_group_usage[str(reduction.get("reduction_group"))] += 1

        conditional_ok = (
            not unknown_obligations
            and "P_uniform_tube_constants" in obligations
            and bool(open_obligations)
            and reduction.get("reduction_rule_recorded") is True
            and term.get("regularity_inputs_available") is True
            and term.get("row_binding_available") is True
            and term.get("required_bound") == "O(h^7)"
            and term.get("taylor_bound_proved") is False
            and reduction.get("term_bound_proved") is False
            and reduction.get("certifies_theorem_now") is False
        )
        record = {
            "stage": term.get("stage"),
            "body": term.get("body"),
            "global_row": term.get("global_row"),
            "component": term.get("component"),
            "balance_block": term.get("balance_block"),
            "term_id": term.get("term_id"),
            "reduction_group": reduction.get("reduction_group"),
            "required_bound": term.get("required_bound"),
            "primitive_obligations": obligations,
            "proved_obligations": proved_obligations,
            "open_obligations_assumed": open_obligations,
            "unknown_obligations": unknown_obligations,
            "conditional_bound_if_open_primitives_assumed": conditional_ok,
            "actual_taylor_bound_proved": False,
            "certifies_theorem_now": False,
        }
        conditional_terms.append(record)
        row_terms[int(term.get("global_row"))].append(record)

    row_certificates = []
    for global_row, terms in sorted(row_terms.items()):
        blocks = {term["balance_block"] for term in terms}
        block = next(iter(blocks)) if len(blocks) == 1 else "mixed"
        expected_terms = 4 if block == "translational_newton_balance" else 5
        row_certificates.append(
            {
                "global_row": global_row,
                "balance_block": block,
                "term_count": len(terms),
                "expected_term_count": expected_terms,
                "conditional_terms": sum(
                    1 for term in terms if term["conditional_bound_if_open_primitives_assumed"]
                ),
                "actual_terms_proved": sum(1 for term in terms if term["actual_taylor_bound_proved"]),
                "conditional_row_bound_if_open_primitives_assumed": (
                    len(terms) == expected_terms
                    and all(term["conditional_bound_if_open_primitives_assumed"] for term in terms)
                ),
                "actual_row_bound_proved": False,
            }
        )

    manuscript_tokens = [
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
    ]
    conditional_term_count = sum(
        1 for term in conditional_terms if term["conditional_bound_if_open_primitives_assumed"]
    )
    conditional_row_count = sum(
        1 for row in row_certificates if row["conditional_row_bound_if_open_primitives_assumed"]
    )
    actual_term_count = sum(1 for term in conditional_terms if term["actual_taylor_bound_proved"])
    actual_row_count = sum(1 for row in row_certificates if row["actual_row_bound_proved"])
    global_submission_boundaries = [
        "full_source_policy_package_ready",
        "theorem_level_eta_h_solver_policy_evidence",
        "closed_residual_to_error_theorem_for_mechanism_rows",
    ]

    result = {
        "schema": "d5-conditional-taylor-certificate-v1",
        "status": "conditional_taylor_certificate_recorded_primitive_taylor_pc2_open",
        "read_only": True,
        "run_v047_invoked": False,
        "submission_ready": False,
        "submission_ready_scope": (
            "d5_conditional_taylor_global_boundary_not_narrowed_claim_package_decision"
        ),
        "readiness_boundary": {
            "conditional_taylor_certificate_scope": (
                "conditional_162_subterm_implication_under_open_primitives_not_actual_taylor_bound_closure"
            ),
            "open_primitive_assumptions": sorted(OPEN_PRIMITIVES),
            "narrowed_claim_package_decision_not_made_by_this_certificate": True,
            "global_submission_boundaries_retained": global_submission_boundaries,
        },
        "pc2_closed": False,
        "pc2_closed_scope": "false only for the separate primitive/Taylor PC2 route; active direct PC2 residual-bridge slot is closed separately",
        "primitive_route_pc2_closed": False,
        "proof_gap_closed": False,
        "proof_gap_closed_scope": "false only for the separate primitive/Taylor proof gap; active direct PC2 residual-bridge proof-gap slot is closed separately",
        "primitive_route_proof_gap_closed": False,
        "stage_residual_O_h7_implementation_defect_proved": False,
        "stage_residual_O_h7_implementation_defect_proved_scope": "not proved by this separate primitive/Taylor certificate; active theorem residual input is proved by the direct 96+36 bridge",
        "primitive_route_stage_residual_O_h7_implementation_defect_proved": False,
        "conditional_certificate_only": True,
        "strict_taylor_template_library": TAYLOR_TEMPLATE_LIBRARY,
        "strict_taylor_template_status": {
            "template_count": len(TAYLOR_TEMPLATE_LIBRARY),
            "template_rows": {
                key: value["term_rows"] for key, value in TAYLOR_TEMPLATE_LIBRARY.items()
            },
            "template_rows_sum": sum(
                value["term_rows"] for value in TAYLOR_TEMPLATE_LIBRARY.values()
            ),
            "all_templates_are_taylor_or_exact_linear": True,
            "uses_direct_substitution": False,
            "uses_residual_to_error_promotion": False,
            "finite_probe_used_as_proof": False,
        },
        "summary": {
            "dynamic_rows": len(row_certificates),
            "term_rows": len(conditional_terms),
            "conditional_term_bounds_under_open_primitive_assumptions": conditional_term_count,
            "conditional_dynamic_rows_under_open_primitive_assumptions": conditional_row_count,
            "actual_taylor_bounds_proved": actual_term_count,
            "actual_dynamic_rows_proved": actual_row_count,
            "open_primitive_assumption_count": len(OPEN_PRIMITIVES),
            "proved_primitive_count": len(PROVED_PRIMITIVES),
            "primitive_obligation_usage": dict(sorted(primitive_usage.items())),
            "reduction_group_usage": dict(sorted(reduction_group_usage.items())),
            "mismatch_count": len(mismatches),
            "strict_taylor_templates_recorded": len(TAYLOR_TEMPLATE_LIBRARY),
        },
        "remaining_global_submission_boundaries": global_submission_boundaries,
        "remaining_gate_scope": {
            "actual_taylor_bounds_proved": actual_term_count,
            "open_primitive_assumption_count": len(OPEN_PRIMITIVES),
            "pc2_closed": False,
            "proof_gap_closed": False,
            "conditional_templates_not_additive_proof_evidence": True,
            "conditional_templates_not_spliced_with_direct_pc2_bridge": True,
            "narrowed_claim_package_decision_not_made_by_this_certificate": True,
            "global_submission_boundaries_retained": global_submission_boundaries,
        },
        "source_consistency": {
            "term_budget_schema": term_budget.get("schema"),
            "term_budget_terms": term_budget.get("summary", {}).get("term_rows"),
            "term_budget_certified_terms": term_budget.get("summary", {}).get(
                "certified_taylor_bound_terms"
            ),
            "term_budget_pc2_closed": term_budget.get("pc2_closed"),
            "primitive_reduction_schema": primitive_reduction.get("schema"),
            "primitive_reduction_terms": primitive_reduction.get("summary", {}).get("term_rows"),
            "primitive_reduction_rules": primitive_reduction.get("summary", {}).get(
                "term_rows_with_reduction_rule"
            ),
            "primitive_reduction_term_bounds_proved": primitive_reduction.get("summary", {}).get(
                "term_bounds_proved"
            ),
            "primitive_reduction_pc2_closed": primitive_reduction.get("pc2_closed"),
            "p_tube_schema": p_tube.get("schema"),
            "p_tube_closed": p_tube.get("primitive_closed"),
            "p_tube_pc2_closed": p_tube.get("pc2_closed"),
            "closure_plan_schema": closure_plan.get("schema"),
            "closure_plan_open_primitives": closure_plan.get("summary", {}).get(
                "open_primitive_obligations"
            ),
            "closure_plan_induced_bounds_proved": closure_plan.get("summary", {}).get(
                "induced_taylor_bounds_proved"
            ),
            "closure_plan_pc2_closed": closure_plan.get("pc2_closed"),
            "open_gap_schema": open_gap.get("schema"),
            "open_gap_open_primitives": open_gap.get("summary", {}).get("open_primitive_count"),
            "open_gap_pc2_closed": open_gap.get("pc2_closed"),
        },
        "manuscript_link": {
            "lemma_label": "lem:d5-primitive-obligation-implication",
            "main_tex_present": all(contains_normalized(main_tex, token) for token in manuscript_tokens),
            "flat_tex_present": all(contains_normalized(flat_tex, token) for token in manuscript_tokens),
            "tokens": manuscript_tokens,
        },
        "anti_overclaim": {
            "assumes_not_proves_five_open_primitives": True,
            "does_not_certify_actual_taylor_bounds": True,
            "does_not_close_pc2": True,
            "does_not_close_proof_gap": True,
            "does_not_mark_submission_ready": True,
            "finite_sum_constant_is_conditional_only": True,
            "finite_sum_not_inverse_projection_from_aggregate_residual": True,
            "conditional_templates_not_additive_proof_evidence": True,
            "conditional_templates_not_spliced_with_direct_pc2_bridge": True,
            "direct_pc2_bridge_does_not_close_primitive_route": True,
            "primitive_route_requires_five_lifts_and_redone_chain": True,
        },
        "route_separation": {
            "load_bearing_route": "direct_132_row_residual_bridge",
            "diagnostic_route": "conditional_primitive_taylor_template_library",
            "finite_sum_row_constant_recorded": True,
            "finite_sum_not_inverse_projection_from_aggregate_residual": True,
            "conditional_templates_not_additive_proof_evidence": True,
            "conditional_templates_not_spliced_with_direct_pc2_bridge": True,
            "direct_pc2_bridge_does_not_close_primitive_route": True,
            "primitive_route_must_prove_five_uniform_lift_primitives": True,
            "primitive_route_must_redo_residual_to_root_endpoint_solver_global_chain": True,
            "route_separation_scope": (
                "conditional_taylor_templates_are_schema_only_until_their_own_"
                "primitive_lifts_and_full_perturbation_chain_close"
            ),
        },
        "reference_proof_boundary": {
            "reference_role": "proof_order_discipline_only",
            "imports_reference_taylor_estimate": False,
            "imports_reference_multiplier_recursion": False,
            "imports_reference_hidden_constraint_estimate": False,
            "reference_supplies_primitive_fullva_lift_estimate": False,
            "reference_closes_primitive_taylor_ledger": False,
            "reference_supplies_pc2": False,
            "primitive_taylor_certificate_role": "fullva_specific_finite_implication_under_open_primitive_inputs",
        },
        "mismatches": mismatches,
        "row_certificates": row_certificates,
        "conditional_terms": conditional_terms,
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# D5 Conditional Taylor Certificate",
        "",
        "Status: **conditional Taylor certificate recorded; primitive-and-Taylor PC2 route remains open**.",
        "Here `submission_ready=false` is scoped to the conditional Taylor/global proof-package boundary,",
        "not to the separate narrowed-claim package decision.",
        "",
        "This read-only certificate checks the finite implication from the D5",
        "primitive obligations to the 162 Newton-Euler Taylor subterms. It is",
        "conditional on the five open lift/bilinear primitives and does not",
        "prove those primitives, certify an actual Taylor bound, or close the primitive/Taylor PC2 route.",
        "",
        "## Summary",
        "",
        f"- Dynamic rows conditionally covered: `{conditional_row_count}/{len(row_certificates)}`.",
        f"- Taylor subterms conditionally covered: `{conditional_term_count}/{len(conditional_terms)}`.",
        f"- Actual Taylor bounds proved: `{actual_term_count}/{len(conditional_terms)}`.",
        f"- Open primitive assumptions: `{len(OPEN_PRIMITIVES)}`.",
        f"- Proved primitive obligations used: `{len(PROVED_PRIMITIVES)}`.",
        f"- Primitive/Taylor PC2 route closed: `{result['pc2_closed']}`.",
        f"- Conditional templates are additive proof evidence: `{not result['anti_overclaim']['conditional_templates_not_additive_proof_evidence']}`.",
        f"- Conditional templates spliced with direct PC2 bridge: `{not result['anti_overclaim']['conditional_templates_not_spliced_with_direct_pc2_bridge']}`.",
        f"- Finite-sum row constant recorded: `{result['route_separation']['finite_sum_row_constant_recorded']}`.",
        f"- Finite-sum step is inverse projection from aggregate residual: `{not result['anti_overclaim']['finite_sum_not_inverse_projection_from_aggregate_residual']}`.",
        f"- Primitive route must prove five lift primitives and redo the perturbation chain: `{result['anti_overclaim']['primitive_route_requires_five_lifts_and_redone_chain']}`.",
        f"- Reference proof imports Taylor estimate: `{result['reference_proof_boundary']['imports_reference_taylor_estimate']}`.",
        f"- Reference proof supplies primitive FullVA lift estimate: `{result['reference_proof_boundary']['reference_supplies_primitive_fullva_lift_estimate']}`.",
        f"- Reference proof closes primitive/Taylor ledger or PC2: `{result['reference_proof_boundary']['reference_closes_primitive_taylor_ledger']}/{result['reference_proof_boundary']['reference_supplies_pc2']}`.",
        f"- Submission ready: `{result['submission_ready']}`.",
        f"- Submission-ready scope: `{result['submission_ready_scope']}`.",
        f"- Conditional Taylor certificate scope: `{result['readiness_boundary']['conditional_taylor_certificate_scope']}`.",
        f"- Remaining global submission boundaries: `{','.join(result['remaining_global_submission_boundaries'])}`.",
        "",
        "## Primitive Usage",
        "",
        "| primitive | term rows | proved now | assumed now |",
        "|---|---:|---:|---:|",
    ]
    for primitive, count in sorted(primitive_usage.items()):
        lines.append(
            f"| `{primitive}` | `{count}` | `{primitive in PROVED_PRIMITIVES}` | `{primitive in OPEN_PRIMITIVES}` |"
        )
    lines.extend(
        [
            "",
            "## Reduction Groups",
            "",
            "| group | term rows |",
            "|---|---:|",
        ]
    )
    for group, count in sorted(reduction_group_usage.items()):
        lines.append(f"| `{group}` | `{count}` |")
    lines.extend(
        [
            "",
            "## Primitive/Taylor Diagnostic Templates",
            "",
            "| group | template | bound |",
            "|---|---|---|",
        ]
    )
    for group, template in sorted(TAYLOR_TEMPLATE_LIBRARY.items()):
        lines.append(
            f"| `{group}` | `{template['template_kind']}` | `{template['bound']}` |"
        )
    lines.extend(
        [
            "",
            "## Row Coverage",
            "",
            "| row | block | terms | conditional terms | actual terms proved |",
            "|---:|---|---:|---:|---:|",
        ]
    )
    for row in row_certificates:
        lines.append(
            f"| `{row['global_row']}` | `{row['balance_block']}` | "
            f"`{row['term_count']}` | `{row['conditional_terms']}` | `{row['actual_terms_proved']}` |"
        )
    lines.extend(
        [
            "",
            "## Acceptance Boundary",
            "",
            "- This certificate proves only a finite conditional implication.",
            "- It assumes the five open primitive obligations: state and acceleration root lifts, the multiplier lift propagated from them, and the downstream geometry and gyroscopic reductions.",
            "- It does not certify any actual D5 Taylor subterm bound.",
            "- The Wieloch--Arnold constrained-BDF proof (`wieloch2021bdf`; local reference text `../../external/literature/1-s2.0-S0377042719305229-main.txt`) is invoked as proof-order discipline only; it does not import a Taylor estimate, primitive FullVA lift, multiplier recursion, hidden-constraint estimate, or PC2 input for this certificate.",
            "- The conditional templates are not additive proof evidence and cannot be spliced with the direct PC2 bridge.",
            "- A primitive-route theorem would have to prove the five open primitive obligations and redo the residual-to-root, endpoint, solver, and global-transfer chain.",
            "- It does not close the primitive-route proof gap or submission readiness; only the active direct PC2 residual-bridge proof-gap slot is closed elsewhere by the direct residual-bridge route.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("d5_conditional_taylor_certificate=written")
    print(f"conditional_terms={conditional_term_count}/{len(conditional_terms)}")
    print(f"conditional_rows={conditional_row_count}/{len(row_certificates)}")
    print(f"actual_taylor_bounds_proved={actual_term_count}")
    print("pc2_closed=False")


if __name__ == "__main__":
    main()
