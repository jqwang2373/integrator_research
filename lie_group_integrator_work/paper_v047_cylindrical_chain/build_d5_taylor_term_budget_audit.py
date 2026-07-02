#!/usr/bin/env python3
"""Build a term-level budget for the open D5 Taylor certificate."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "D5_TAYLOR_TERM_BUDGET_AUDIT.json"
OUT_MD = PAPER / "D5_TAYLOR_TERM_BUDGET_AUDIT.md"


TRANSLATIONAL_TERMS = [
    {
        "id": "T_acceleration_lift",
        "expression": "m_b (a_hat_{s,b} - a_b(t_s))",
        "required_bound": "O(h^7)",
    },
    {
        "id": "T_external_force_lift",
        "expression": "f_ext(q_hat_s,v_hat_s,t_s) - f_ext(q(t_s),v(t_s),t_s)",
        "required_bound": "O(h^7)",
    },
    {
        "id": "T_multiplier_force_lift",
        "expression": "G_hat_{s,b}^T lambda_hat_s - G_b(q(t_s))^T lambda(t_s)",
        "required_bound": "O(h^7)",
    },
    {
        "id": "T_friction_force_lift",
        "expression": "f_fric(q_hat_s,v_hat_s,lambda_hat_s) - f_fric(q(t_s),v(t_s),lambda(t_s))",
        "required_bound": "O(h^7)",
    },
]

ROTATIONAL_TERMS = [
    {
        "id": "R_angular_acceleration_lift",
        "expression": "J_b (alpha_hat_{s,b} - alpha_b(t_s))",
        "required_bound": "O(h^7)",
    },
    {
        "id": "R_gyroscopic_lift",
        "expression": "omega_hat_{s,b} x J_b omega_hat_{s,b} - omega_b(t_s) x J_b omega_b(t_s)",
        "required_bound": "O(h^7)",
    },
    {
        "id": "R_external_torque_lift",
        "expression": "tau_ext(q_hat_s,v_hat_s,t_s) - tau_ext(q(t_s),v(t_s),t_s)",
        "required_bound": "O(h^7)",
    },
    {
        "id": "R_multiplier_torque_lift",
        "expression": "H_hat_{s,b}^T lambda_hat_s - H_b(q(t_s))^T lambda(t_s)",
        "required_bound": "O(h^7)",
    },
    {
        "id": "R_friction_torque_lift",
        "expression": "tau_fric(q_hat_s,v_hat_s,lambda_hat_s) - tau_fric(q(t_s),v(t_s),lambda(t_s))",
        "required_bound": "O(h^7)",
    },
]

TERM_PROOF_TEMPLATES = {
    "T_acceleration_lift": {
        "taylor_template": "linear_unweighted_acceleration_lift",
        "conditional_inequality": "||m_b delta a|| <= m_max ||delta a||",
        "primitive_obligations": ["P_acceleration_lift", "P_uniform_tube_constants"],
        "blocking_primitive_ids": ["P_acceleration_lift"],
        "requires_unweighted_acceleration_O_h7": True,
        "h_weighted_acceleration_control_sufficient": False,
        "blocker_reason": (
            "D6 records unweighted Newton rows, so h*delta a=O(h^7) does not "
            "imply the required delta a=O(h^7) acceleration subterm bound."
        ),
    },
    "T_external_force_lift": {
        "taylor_template": "smooth_force_lipschitz_state_lift",
        "conditional_inequality": "||Delta f_ext|| <= L_f (||delta q|| + ||delta v||)",
        "primitive_obligations": ["P_state_lift", "P_uniform_tube_constants"],
        "blocking_primitive_ids": ["P_state_lift"],
        "requires_unweighted_acceleration_O_h7": False,
        "h_weighted_acceleration_control_sufficient": None,
        "blocker_reason": "The state/velocity primitive lift is still open on the primitive/Taylor route.",
    },
    "T_multiplier_force_lift": {
        "taylor_template": "product_geometry_multiplier_lift",
        "conditional_inequality": (
            "||Delta(G^T lambda)|| <= C_G ||delta lambda|| + C_lambda ||delta G|| "
            "+ C ||delta G|| ||delta lambda||"
        ),
        "primitive_obligations": [
            "P_state_lift",
            "P_multiplier_lift",
            "P_geometry_lift",
            "P_uniform_tube_constants",
        ],
        "blocking_primitive_ids": ["P_state_lift", "P_multiplier_lift", "P_geometry_lift"],
        "requires_unweighted_acceleration_O_h7": False,
        "h_weighted_acceleration_control_sufficient": None,
        "blocker_reason": "Multiplier and geometry lift primitives remain open.",
    },
    "T_friction_force_lift": {
        "taylor_template": "smooth_friction_lipschitz_state_multiplier_lift",
        "conditional_inequality": (
            "||Delta f_fric|| <= L_fric (||delta q|| + ||delta v|| + ||delta lambda||)"
        ),
        "primitive_obligations": ["P_state_lift", "P_multiplier_lift", "P_uniform_tube_constants"],
        "blocking_primitive_ids": ["P_state_lift", "P_multiplier_lift"],
        "requires_unweighted_acceleration_O_h7": False,
        "h_weighted_acceleration_control_sufficient": None,
        "blocker_reason": "State and multiplier lift primitives remain open.",
    },
    "R_angular_acceleration_lift": {
        "taylor_template": "linear_unweighted_angular_acceleration_lift",
        "conditional_inequality": "||J_b delta alpha|| <= J_max ||delta alpha||",
        "primitive_obligations": ["P_acceleration_lift", "P_uniform_tube_constants"],
        "blocking_primitive_ids": ["P_acceleration_lift"],
        "requires_unweighted_acceleration_O_h7": True,
        "h_weighted_acceleration_control_sufficient": False,
        "blocker_reason": (
            "D6 records unweighted Euler rows, so h*delta alpha=O(h^7) does not "
            "imply the required delta alpha=O(h^7) angular-acceleration subterm bound."
        ),
    },
    "R_gyroscopic_lift": {
        "taylor_template": "bilinear_gyroscopic_mean_value_lift",
        "conditional_inequality": (
            "||Delta(omega x J omega)|| <= C_gyro (||omega||+||omega_hat||) ||delta omega||"
        ),
        "primitive_obligations": ["P_state_lift", "P_gyroscopic_lift", "P_uniform_tube_constants"],
        "blocking_primitive_ids": ["P_state_lift", "P_gyroscopic_lift"],
        "requires_unweighted_acceleration_O_h7": False,
        "h_weighted_acceleration_control_sufficient": None,
        "blocker_reason": "Angular-velocity and gyroscopic bilinear lift primitives remain open.",
    },
    "R_external_torque_lift": {
        "taylor_template": "smooth_torque_lipschitz_state_lift",
        "conditional_inequality": "||Delta tau_ext|| <= L_tau (||delta q|| + ||delta v||)",
        "primitive_obligations": ["P_state_lift", "P_uniform_tube_constants"],
        "blocking_primitive_ids": ["P_state_lift"],
        "requires_unweighted_acceleration_O_h7": False,
        "h_weighted_acceleration_control_sufficient": None,
        "blocker_reason": "The pose/angular-velocity primitive lift is still open on the primitive/Taylor route.",
    },
    "R_multiplier_torque_lift": {
        "taylor_template": "product_geometry_multiplier_lift",
        "conditional_inequality": (
            "||Delta(H^T lambda)|| <= C_H ||delta lambda|| + C_lambda ||delta H|| "
            "+ C ||delta H|| ||delta lambda||"
        ),
        "primitive_obligations": [
            "P_state_lift",
            "P_multiplier_lift",
            "P_geometry_lift",
            "P_uniform_tube_constants",
        ],
        "blocking_primitive_ids": ["P_state_lift", "P_multiplier_lift", "P_geometry_lift"],
        "requires_unweighted_acceleration_O_h7": False,
        "h_weighted_acceleration_control_sufficient": None,
        "blocker_reason": "Multiplier and moment-arm geometry lift primitives remain open.",
    },
    "R_friction_torque_lift": {
        "taylor_template": "smooth_friction_torque_lipschitz_state_multiplier_lift",
        "conditional_inequality": (
            "||Delta tau_fric|| <= L_tau_fric (||delta q|| + ||delta v|| + ||delta lambda||)"
        ),
        "primitive_obligations": ["P_state_lift", "P_multiplier_lift", "P_uniform_tube_constants"],
        "blocking_primitive_ids": ["P_state_lift", "P_multiplier_lift"],
        "requires_unweighted_acceleration_O_h7": False,
        "h_weighted_acceleration_control_sufficient": None,
        "blocker_reason": "State and multiplier lift primitives remain open.",
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


def row_terms(row: dict[str, Any]) -> list[dict[str, Any]]:
    block = row.get("balance_block")
    templates = TRANSLATIONAL_TERMS if block == "translational_newton_balance" else ROTATIONAL_TERMS
    rows = []
    for term in templates:
        proof = TERM_PROOF_TEMPLATES[term["id"]]
        rows.append(
            {
            "global_row": row.get("global_row"),
            "stage": row.get("stage"),
            "body": row.get("body"),
            "component": row.get("component"),
            "balance_block": block,
            "term_id": term["id"],
            "expression": term["expression"],
            "required_bound": term["required_bound"],
            "strict_taylor_reduction_recorded": True,
            "taylor_template": proof["taylor_template"],
            "conditional_inequality": proof["conditional_inequality"],
            "primitive_obligations": proof["primitive_obligations"],
            "blocking_primitive_ids": proof["blocking_primitive_ids"],
            "blocked_by_open_primitives": bool(proof["blocking_primitive_ids"]),
            "requires_unweighted_acceleration_O_h7": proof["requires_unweighted_acceleration_O_h7"],
            "h_weighted_acceleration_control_sufficient": proof[
                "h_weighted_acceleration_control_sufficient"
            ],
            "blocker_reason": proof["blocker_reason"],
            "anti_circularity": {
                "uses_stage_residual_defect": False,
                "uses_d5_direct_substitution": False,
                "uses_finite_probe_as_proof": False,
                "uses_residual_to_error_promotion": False,
            },
            "regularity_inputs_available": True,
            "row_binding_available": row.get("runtime_traceability_ready") is True,
            "taylor_bound_proved": False,
            "certifies_theorem_now": False,
            "finite_probe_evidence_sufficient": False,
            "residual_to_error_promotion_allowed": False,
        }
        )
    return rows


def main() -> None:
    readiness = read_json(PAPER / "D5_DYNAMIC_DEFECT_READINESS_AUDIT.json")
    certificate = read_json(PAPER / "NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.json")
    proof_manifest = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
    p_acc_lift_obstruction = read_json(PAPER / "D5_P_ACC_LIFT_OBSTRUCTION_AUDIT.json")
    p_acc_weighted_inverse = read_json(PAPER / "D5_P_ACC_PA2_WEIGHTED_INVERSE_AUDIT.json")
    main_tex = read_text(PAPER / "main_cmame.tex")
    flat_tex = read_text(PAPER / "cmame_submission_flat" / "main_cmame_submission.tex")

    rows = readiness.get("rows", [])
    term_rows = [term for row in rows if isinstance(row, dict) for term in row_terms(row)]
    translational_term_rows = [
        term for term in term_rows if term.get("balance_block") == "translational_newton_balance"
    ]
    rotational_term_rows = [
        term for term in term_rows if term.get("balance_block") == "rotational_euler_balance"
    ]
    certified_terms = sum(1 for term in term_rows if term.get("taylor_bound_proved") is True)
    open_terms = sum(1 for term in term_rows if term.get("taylor_bound_proved") is False)
    regularity_ready_terms = sum(1 for term in term_rows if term.get("regularity_inputs_available") is True)
    row_binding_ready_terms = sum(1 for term in term_rows if term.get("row_binding_available") is True)
    strict_reduction_terms = sum(1 for term in term_rows if term.get("strict_taylor_reduction_recorded") is True)
    anti_circular_terms = sum(
        1
        for term in term_rows
        if term.get("anti_circularity", {}).get("uses_stage_residual_defect") is False
        and term.get("anti_circularity", {}).get("uses_d5_direct_substitution") is False
        and term.get("anti_circularity", {}).get("uses_finite_probe_as_proof") is False
        and term.get("anti_circularity", {}).get("uses_residual_to_error_promotion") is False
    )
    primitive_blocker_usage: dict[str, int] = {}
    template_usage: dict[str, int] = {}
    for term in term_rows:
        template = str(term.get("taylor_template"))
        template_usage[template] = template_usage.get(template, 0) + 1
        for primitive in term.get("blocking_primitive_ids", []):
            primitive_blocker_usage[primitive] = primitive_blocker_usage.get(primitive, 0) + 1
    unweighted_acceleration_blocked_terms = sum(
        1 for term in term_rows if term.get("requires_unweighted_acceleration_O_h7") is True
    )
    h_weighted_acceleration_sufficient_terms = sum(
        1 for term in term_rows if term.get("h_weighted_acceleration_control_sufficient") is True
    )
    h_weighted_acceleration_insufficient_terms = sum(
        1 for term in term_rows if term.get("h_weighted_acceleration_control_sufficient") is False
    )
    p_acc_terms = [
        term
        for term in term_rows
        if "P_acceleration_lift" in term.get("blocking_primitive_ids", [])
    ]
    p_acc_translational_terms = [
        term for term in p_acc_terms if term.get("term_id") == "T_acceleration_lift"
    ]
    p_acc_rotational_terms = [
        term for term in p_acc_terms if term.get("term_id") == "R_angular_acceleration_lift"
    ]
    p_acc_global_rows = sorted({int(term["global_row"]) for term in p_acc_terms})

    manuscript_tokens = [
        "D5 term-budget record",
        "162 Taylor subterms",
        "zero term-level bounds",
    ]
    global_submission_boundaries = [
        "full_source_policy_package_ready",
        "theorem_level_eta_h_solver_policy_evidence",
        "closed_residual_to_error_theorem_for_mechanism_rows",
    ]
    result = {
        "schema": "d5-taylor-term-budget-audit-v1",
        "status": "d5_taylor_subterm_budget_recorded_pc2_open",
        "read_only": True,
        "run_v047_invoked": False,
        "submission_ready": False,
        "submission_ready_scope": (
            "d5_primitive_taylor_term_budget_global_boundary_not_narrowed_claim_package_decision"
        ),
        "readiness_boundary": {
            "primitive_taylor_budget_scope": (
                "162_subterm_budget_inventory_not_actual_taylor_bound_closure"
            ),
            "required_route": "primitive_162_term_taylor_route",
            "narrowed_claim_package_decision_not_made_by_this_audit": True,
            "global_submission_boundaries_retained": global_submission_boundaries,
        },
        "pc2_closed": False,
        "pc2_closed_scope": "false only for the separate primitive/Taylor PC2 route; active direct PC2 residual-bridge slot is closed separately",
        "primitive_route_pc2_closed": False,
        "proof_gap_closed": False,
        "proof_gap_closed_scope": "false only for the separate primitive/Taylor proof gap; active direct PC2 residual-bridge proof-gap slot is closed separately",
        "primitive_route_proof_gap_closed": False,
        "stage_residual_O_h7_implementation_defect_proved": False,
        "stage_residual_O_h7_implementation_defect_proved_scope": "not proved by this separate primitive/Taylor term budget; active theorem residual input is proved by the direct 96+36 bridge",
        "primitive_route_stage_residual_O_h7_implementation_defect_proved": False,
        "summary": {
            "dynamic_rows": len(rows),
            "translational_rows": readiness.get("summary", {}).get("translational_rows"),
            "rotational_rows": readiness.get("summary", {}).get("rotational_rows"),
            "translational_subterms_per_row": len(TRANSLATIONAL_TERMS),
            "rotational_subterms_per_row": len(ROTATIONAL_TERMS),
            "term_rows": len(term_rows),
            "translational_term_rows": len(translational_term_rows),
            "rotational_term_rows": len(rotational_term_rows),
            "regularity_ready_terms": regularity_ready_terms,
            "row_binding_ready_terms": row_binding_ready_terms,
            "strict_taylor_reduction_terms": strict_reduction_terms,
            "anti_circular_taylor_terms": anti_circular_terms,
            "terms_with_open_primitive_blockers": sum(
                1 for term in term_rows if term.get("blocked_by_open_primitives") is True
            ),
            "unweighted_acceleration_blocked_terms": unweighted_acceleration_blocked_terms,
            "h_weighted_acceleration_sufficient_terms": h_weighted_acceleration_sufficient_terms,
            "h_weighted_acceleration_insufficient_terms": h_weighted_acceleration_insufficient_terms,
            "p_acc_strict_requirement_recorded": True,
            "p_acc_strict_requirement_terms": len(p_acc_terms),
            "p_acc_velocity_collocation_only_unweighted_rate": p_acc_lift_obstruction.get(
                "current_recorded_inputs_imply_only_unweighted_acceleration_rate"
            ),
            "p_acc_weighted_h_control_recorded": p_acc_weighted_inverse.get(
                "weighted_h_acceleration_control_recorded"
            ),
            "p_acc_unweighted_uniform_control_proved": p_acc_weighted_inverse.get(
                "unweighted_acceleration_uniform_control_proved"
            ),
            "primitive_blocker_usage": dict(sorted(primitive_blocker_usage.items())),
            "taylor_template_usage": dict(sorted(template_usage.items())),
            "certified_taylor_bound_terms": certified_terms,
            "open_taylor_bound_terms": open_terms,
            "finite_probe_sufficient_terms": 0,
            "residual_to_error_promotion_allowed_terms": 0,
        },
        "remaining_global_submission_boundaries": global_submission_boundaries,
        "remaining_gate_scope": {
            "open_primitive_taylor_terms": open_terms,
            "certified_taylor_bound_terms": certified_terms,
            "pc2_closed": False,
            "proof_gap_closed": False,
            "narrowed_claim_package_decision_not_made_by_this_audit": True,
            "global_submission_boundaries_retained": global_submission_boundaries,
        },
        "claim_boundary": {
            "allowed_now": "term-level D5 Taylor budget and exact remaining subterm inventory",
            "forbidden_now": [
                "primitive/Taylor PC2 route closure",
                "O(h^7) dynamic-row proof closure",
                "certified Newton-Euler theorem rows",
                "submission-ready proof",
            ],
            "close_condition": (
                "Primitive/Taylor PC2 route closes only after every listed subterm has an independent "
                "uniform O(h^7) Taylor bound on the compact smooth proof tube."
            ),
        },
        "manuscript_link": {
            "main_tex_present": all(token in main_tex for token in manuscript_tokens),
            "flat_tex_present": all(token in flat_tex for token in manuscript_tokens),
            "tokens": manuscript_tokens,
        },
        "source_consistency": {
            "readiness_schema": readiness.get("schema"),
            "readiness_pc2_closed": readiness.get("pc2_closed"),
            "certificate_complete": certificate.get("certificate_complete"),
            "certificate_pc2_closed": certificate.get("summary", {}).get("pc2_dynamic_O_h7_defect_certificate_closed"),
            "proof_manifest_proof_gap_closed": proof_manifest.get("closure_state", {}).get("proof_gap_closed"),
            "proof_manifest_direct_route_gap_closed": proof_manifest.get("closure_state", {}).get(
                "direct_pc2_proof_gap_closed"
            ),
            "proof_manifest_proof_gap_closed_scope": proof_manifest.get("closure_state", {}).get(
                "proof_gap_closed_scope"
            ),
            "p_acc_lift_obstruction_schema": p_acc_lift_obstruction.get("schema"),
            "p_acc_lift_obstruction_pa2_closed": p_acc_lift_obstruction.get("pa2_closed"),
            "p_acc_lift_obstruction_current_unweighted_rate": p_acc_lift_obstruction.get(
                "current_recorded_inputs_imply_only_unweighted_acceleration_rate"
            ),
            "p_acc_weighted_inverse_schema": p_acc_weighted_inverse.get("schema"),
            "p_acc_weighted_inverse_weighted_h_control_recorded": p_acc_weighted_inverse.get(
                "weighted_h_acceleration_control_recorded"
            ),
            "p_acc_weighted_inverse_unweighted_control_proved": p_acc_weighted_inverse.get(
                "unweighted_acceleration_uniform_control_proved"
            ),
        },
        "p_acc_strict_taylor_requirement": {
            "requirement_recorded": True,
            "term_count": len(p_acc_terms),
            "translational_term_count": len(p_acc_translational_terms),
            "rotational_term_count": len(p_acc_rotational_terms),
            "global_rows": p_acc_global_rows,
            "required_unweighted_rate": "O(h^7)",
            "blocking_primitive": "P_acceleration_lift",
            "linear_taylor_reduction": {
                "translational": "||m_b delta a|| <= m_max ||delta a||",
                "rotational": "||J_b delta alpha|| <= J_max ||delta alpha||",
                "remainder": "zero for the acceleration maps because the maps are linear in acceleration",
                "uniform_constants_source": "P_uniform_tube_constants",
            },
            "weighted_control_boundary": {
                "h_delta_A_control_recorded": p_acc_weighted_inverse.get(
                    "weighted_h_acceleration_control_recorded"
                ),
                "unweighted_acceleration_uniform_control_proved": p_acc_weighted_inverse.get(
                    "unweighted_acceleration_uniform_control_proved"
                ),
                "h_weighted_control_sufficient_for_current_d5_budget": False,
                "reason": (
                    "The implemented Newton-Euler rows contain m_b delta a and "
                    "J_b delta alpha without an extra h factor."
                ),
            },
            "velocity_collocation_boundary": {
                "velocity_collocation_alone_sufficient_for_O_h7_acceleration": p_acc_lift_obstruction.get(
                    "velocity_collocation_alone_sufficient_for_O_h7_acceleration"
                ),
                "current_recorded_inputs_imply_only_unweighted_acceleration_rate": p_acc_lift_obstruction.get(
                    "current_recorded_inputs_imply_only_unweighted_acceleration_rate"
                ),
                "rate_algebra": p_acc_lift_obstruction.get("rate_algebra"),
            },
            "strict_close_condition": (
                "Certify these 36 Taylor terms only after an unweighted "
                "||delta A||=O(h^7) acceleration lift is proved uniformly on "
                "the compact smooth proof tube, or after P_acceleration_lift "
                "is carried as an explicit theorem assumption."
            ),
            "anti_overclaim": {
                "does_not_use_d5_direct_substitution": True,
                "does_not_use_finite_probe_as_proof": True,
                "does_not_use_residual_to_error_promotion": True,
                "does_not_certify_p_acc": True,
                "does_not_certify_taylor_terms": True,
            },
        },
        "term_templates": {
            "translational": TRANSLATIONAL_TERMS,
            "rotational": ROTATIONAL_TERMS,
        },
        "term_rows": term_rows,
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# D5 Taylor Term-Budget Audit",
        "",
        "Status: **D5 Taylor subterm budget recorded; separate primitive-route certificate remains open**.",
        "Here `submission_ready=false` is scoped to the primitive Taylor/global proof-package boundary,",
        "not to the separate narrowed-claim package decision.",
        "",
        "This read-only audit decomposes the open lifted-stage Newton-Euler",
        "dynamic term into row-local Taylor subterms. It does not certify any",
        "subterm bound and does not close the separate primitive/Taylor reproof",
        "route; it is not used by the active direct-route conditional theorem proof.",
        "",
        "## Summary",
        "",
        f"- Dynamic rows: `{len(rows)}/36`.",
        f"- Translational/rotational rows: `{result['summary']['translational_rows']}/{result['summary']['rotational_rows']}`.",
        f"- Translational subterms per row: `{len(TRANSLATIONAL_TERMS)}`.",
        f"- Rotational subterms per row: `{len(ROTATIONAL_TERMS)}`.",
        f"- Total Taylor subterms: `{len(term_rows)}`.",
        f"- Regularity-ready subterms: `{regularity_ready_terms}/{len(term_rows)}`.",
        f"- Row-binding-ready subterms: `{row_binding_ready_terms}/{len(term_rows)}`.",
        f"- Primitive/Taylor reduction subterms: `{strict_reduction_terms}/{len(term_rows)}`.",
        f"- Anti-circular Taylor subterms: `{anti_circular_terms}/{len(term_rows)}`.",
        f"- Subterms blocked by open primitives: `{result['summary']['terms_with_open_primitive_blockers']}/{len(term_rows)}`.",
        f"- Unweighted acceleration-blocked subterms: `{unweighted_acceleration_blocked_terms}/36`.",
        f"- h-weighted acceleration sufficient subterms: `{h_weighted_acceleration_sufficient_terms}`.",
        f"- Certified Taylor-bound subterms: `{certified_terms}/{len(term_rows)}`.",
        f"- Open Taylor-bound subterms: `{open_terms}/{len(term_rows)}`.",
        f"- Separate primitive/Taylor PC2 route closed: `{result['pc2_closed']}`.",
        f"- Submission ready: `{result['submission_ready']}`.",
        f"- Submission-ready scope: `{result['submission_ready_scope']}`.",
        f"- Primitive Taylor budget scope: `{result['readiness_boundary']['primitive_taylor_budget_scope']}`.",
        f"- Remaining global submission boundaries: `{','.join(result['remaining_global_submission_boundaries'])}`.",
        "",
        "## Term Templates",
        "",
        "| block | term | expression | required bound | proof status |",
        "|---|---|---|---|---|",
    ]
    for term in TRANSLATIONAL_TERMS:
        proof = TERM_PROOF_TEMPLATES[term["id"]]
        lines.append(
            f"| translational | `{term['id']}` | `{term['expression']}` | `{term['required_bound']}` | conditional `{proof['taylor_template']}`; open |"
        )
    for term in ROTATIONAL_TERMS:
        proof = TERM_PROOF_TEMPLATES[term["id"]]
        lines.append(
            f"| rotational | `{term['id']}` | `{term['expression']}` | `{term['required_bound']}` | conditional `{proof['taylor_template']}`; open |"
        )
    lines.extend(
        [
            "",
            "## Primitive/Taylor Diagnostic Boundary",
            "",
            "- Every subterm has a recorded Taylor/mean-value inequality and primitive dependency list.",
            "- The primitive/Taylor reductions use compact-tube smoothness and row binding only.",
            "- They do not use Lemma `stage-residual-defect`, D5 direct substitution, finite probes, or residual-to-error promotion.",
            "- The 36 acceleration subterms remain blocked because the implemented Newton-Euler rows are unweighted.",
            "- Recorded `h delta A` control is not sufficient for the unweighted acceleration Taylor subterms.",
            "",
            "## P_acc Primitive/Taylor Requirement",
            "",
            "- Acceleration Taylor subterms: `36`.",
            "- Translational acceleration subterms: `18`.",
            "- Rotational acceleration subterms: `18`.",
            "- Required primitive input: unweighted `||delta A||=O(h^7)`.",
            "- Velocity-collocation alone currently gives only unweighted `O(h^6)`.",
            "- The recorded weighted diagnostic controls `h delta A`, not the unweighted D5 acceleration terms.",
            "",
            "The acceleration reductions are exact linear Taylor reductions:",
            "`||m_b delta a|| <= m_max ||delta a||` and",
            "`||J_b delta alpha|| <= J_max ||delta alpha||`. Since the",
            "implemented Newton-Euler rows contain these acceleration terms without",
            "an extra factor of `h`, `h delta A=O(h^7)` cannot certify the required",
            "unweighted `O(h^7)` Taylor subterm bounds.",
            "",
            "## Acceptance Boundary",
            "",
            "- Finite probes are not sufficient for any subterm.",
            "- Residual-to-error promotion is not allowed for any subterm.",
            "- Primitive/Taylor PC2 route closes only after all 162 Taylor subterms have independent uniform O(h^7) bounds.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("d5_taylor_term_budget_audit=written")
    print(f"term_rows={len(term_rows)}")
    print(f"certified_taylor_bound_terms={certified_terms}")
    print("pc2_closed=False")
    print("submission_ready=False")


if __name__ == "__main__":
    main()
