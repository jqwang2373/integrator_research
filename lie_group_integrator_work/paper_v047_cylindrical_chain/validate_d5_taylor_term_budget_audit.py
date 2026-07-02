#!/usr/bin/env python3
"""Validate the D5 Taylor term-budget audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "D5_TAYLOR_TERM_BUDGET_AUDIT.json"
AUDIT_MD = PAPER / "D5_TAYLOR_TERM_BUDGET_AUDIT.md"

EXPECTED_PRIMITIVE_BLOCKERS = {
    "P_acceleration_lift": 36,
    "P_geometry_lift": 36,
    "P_gyroscopic_lift": 18,
    "P_multiplier_lift": 72,
    "P_state_lift": 126,
}

EXPECTED_TEMPLATE_USAGE = {
    "bilinear_gyroscopic_mean_value_lift": 18,
    "linear_unweighted_acceleration_lift": 18,
    "linear_unweighted_angular_acceleration_lift": 18,
    "product_geometry_multiplier_lift": 36,
    "smooth_force_lipschitz_state_lift": 18,
    "smooth_friction_lipschitz_state_multiplier_lift": 18,
    "smooth_friction_torque_lipschitz_state_multiplier_lift": 18,
    "smooth_torque_lipschitz_state_lift": 18,
}


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


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(AUDIT_JSON)
        audit_md = AUDIT_MD.read_text(encoding="utf-8", errors="replace")
        readiness = read_json(PAPER / "D5_DYNAMIC_DEFECT_READINESS_AUDIT.json")
        proof_manifest = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
        p_acc_lift_obstruction = read_json(PAPER / "D5_P_ACC_LIFT_OBSTRUCTION_AUDIT.json")
        p_acc_weighted_inverse = read_json(PAPER / "D5_P_ACC_PA2_WEIGHTED_INVERSE_AUDIT.json")
    except Exception as exc:  # noqa: BLE001
        print(f"D5 Taylor term-budget audit validation: FAIL\n- {exc}")
        return 1

    summary = audit.get("summary", {})
    source = audit.get("source_consistency", {})
    manuscript = audit.get("manuscript_link", {})
    p_acc_requirement = audit.get("p_acc_strict_taylor_requirement", {})
    term_rows = audit.get("term_rows", [])
    readiness_boundary = audit.get("readiness_boundary", {})
    remaining_gate_scope = audit.get("remaining_gate_scope", {})
    expected_global_boundaries = [
        "full_source_policy_package_ready",
        "theorem_level_eta_h_solver_policy_evidence",
        "closed_residual_to_error_theorem_for_mechanism_rows",
    ]

    checks.check(audit.get("schema") == "d5-taylor-term-budget-audit-v1", "schema changed")
    checks.check(audit.get("status") == "d5_taylor_subterm_budget_recorded_pc2_open", "status changed")
    checks.check(audit.get("read_only") is True, "audit must be read-only")
    checks.check(audit.get("run_v047_invoked") is False, "run_v047 must not be invoked")
    checks.check(audit.get("submission_ready") is False, "submission readiness overclaimed")
    checks.check(
        audit.get("submission_ready_scope")
        == "d5_primitive_taylor_term_budget_global_boundary_not_narrowed_claim_package_decision",
        "submission-ready scope changed",
    )
    checks.check(
        readiness_boundary.get("primitive_taylor_budget_scope")
        == "162_subterm_budget_inventory_not_actual_taylor_bound_closure",
        "primitive Taylor budget scope changed",
    )
    checks.check(
        readiness_boundary.get("required_route") == "primitive_162_term_taylor_route",
        "primitive Taylor required route changed",
    )
    checks.check(
        readiness_boundary.get("narrowed_claim_package_decision_not_made_by_this_audit") is True,
        "narrowed-claim decision boundary missing",
    )
    checks.check(
        readiness_boundary.get("global_submission_boundaries_retained") == expected_global_boundaries,
        "readiness-boundary global submission boundaries changed",
    )
    checks.check(
        audit.get("remaining_global_submission_boundaries") == expected_global_boundaries,
        "remaining global submission boundaries changed",
    )
    checks.check(
        remaining_gate_scope.get("global_submission_boundaries_retained") == expected_global_boundaries,
        "remaining gate global boundaries changed",
    )
    checks.check(
        remaining_gate_scope.get("narrowed_claim_package_decision_not_made_by_this_audit") is True,
        "remaining gate narrowed-claim boundary missing",
    )
    checks.check(audit.get("pc2_closed") is False, "PC2 unexpectedly closed")
    checks.check(audit.get("proof_gap_closed") is False, "proof gap unexpectedly closed")
    checks.check(
        audit.get("stage_residual_O_h7_implementation_defect_proved") is False,
        "O(h^7) dynamic proof unexpectedly closed",
    )
    checks.check(summary.get("dynamic_rows") == 36, "dynamic row count changed")
    checks.check(summary.get("translational_rows") == 18, "translational row count changed")
    checks.check(summary.get("rotational_rows") == 18, "rotational row count changed")
    checks.check(summary.get("translational_subterms_per_row") == 4, "translational subterm count changed")
    checks.check(summary.get("rotational_subterms_per_row") == 5, "rotational subterm count changed")
    checks.check(summary.get("term_rows") == 162, "term-row count changed")
    checks.check(summary.get("translational_term_rows") == 72, "translational term-row count changed")
    checks.check(summary.get("rotational_term_rows") == 90, "rotational term-row count changed")
    checks.check(summary.get("regularity_ready_terms") == 162, "regularity-ready term count changed")
    checks.check(summary.get("row_binding_ready_terms") == 162, "row-binding-ready term count changed")
    checks.check(summary.get("strict_taylor_reduction_terms") == 162, "strict Taylor reduction count changed")
    checks.check(summary.get("anti_circular_taylor_terms") == 162, "anti-circular Taylor term count changed")
    checks.check(
        summary.get("terms_with_open_primitive_blockers") == 162,
        "open primitive blocker term count changed",
    )
    checks.check(
        summary.get("unweighted_acceleration_blocked_terms") == 36,
        "unweighted acceleration blocker count changed",
    )
    checks.check(
        summary.get("h_weighted_acceleration_sufficient_terms") == 0,
        "h-weighted acceleration was incorrectly accepted as sufficient",
    )
    checks.check(
        summary.get("h_weighted_acceleration_insufficient_terms") == 36,
        "h-weighted acceleration insufficiency count changed",
    )
    checks.check(summary.get("p_acc_strict_requirement_recorded") is True, "P_acc strict requirement missing")
    checks.check(summary.get("p_acc_strict_requirement_terms") == 36, "P_acc requirement term count changed")
    checks.check(
        summary.get("p_acc_velocity_collocation_only_unweighted_rate") == "O(h^6)",
        "P_acc velocity-collocation rate boundary changed",
    )
    checks.check(
        summary.get("p_acc_weighted_h_control_recorded") is True,
        "P_acc weighted h-control link missing",
    )
    checks.check(
        summary.get("p_acc_unweighted_uniform_control_proved") is False,
        "P_acc unweighted control unexpectedly proved",
    )
    checks.check(
        summary.get("primitive_blocker_usage") == EXPECTED_PRIMITIVE_BLOCKERS,
        "primitive blocker usage changed",
    )
    checks.check(
        summary.get("taylor_template_usage") == EXPECTED_TEMPLATE_USAGE,
        "Taylor template usage changed",
    )
    checks.check(summary.get("certified_taylor_bound_terms") == 0, "Taylor-bound terms unexpectedly certified")
    checks.check(summary.get("open_taylor_bound_terms") == 162, "open Taylor-bound term count changed")
    checks.check(
        remaining_gate_scope.get("open_primitive_taylor_terms") == summary.get("open_taylor_bound_terms") == 162,
        "remaining gate open primitive Taylor term count changed",
    )
    checks.check(
        remaining_gate_scope.get("certified_taylor_bound_terms")
        == summary.get("certified_taylor_bound_terms")
        == 0,
        "remaining gate certified Taylor term count changed",
    )
    checks.check(
        remaining_gate_scope.get("pc2_closed") is False
        and remaining_gate_scope.get("proof_gap_closed") is False,
        "remaining gate overclaims PC2 or proof-gap closure",
    )
    checks.check(summary.get("finite_probe_sufficient_terms") == 0, "finite-probe term boundary changed")
    checks.check(
        summary.get("residual_to_error_promotion_allowed_terms") == 0,
        "residual-to-error term boundary changed",
    )
    checks.check(
        readiness.get("pc2_closed") is True,
        "readiness direct-route PC2 closure missing",
    )
    checks.check(
        source.get("readiness_pc2_closed") is True,
        "source readiness direct-route PC2 marker changed",
    )
    checks.check(
        readiness.get("summary", {}).get("primitive_taylor_closed_rows") == 0,
        "readiness unexpectedly closes primitive/Taylor rows",
    )
    checks.check(source.get("certificate_complete") is False, "symbolic certificate unexpectedly complete")
    checks.check(source.get("certificate_pc2_closed") is False, "symbolic certificate unexpectedly closes PC2")
    checks.check(
        source.get("proof_manifest_proof_gap_closed") is True
        and proof_manifest.get("closure_state", {}).get("pc2_closed_by_direct_substitution") is True,
        "proof manifest direct-substitution closure not reflected",
    )
    checks.check(
        proof_manifest.get("closure_state", {}).get("primitive_lift_route_closed") is False,
        "proof manifest unexpectedly closes primitive lift route",
    )
    checks.check(
        source.get("p_acc_lift_obstruction_schema") == p_acc_lift_obstruction.get("schema"),
        "P_acc lift-obstruction schema link missing",
    )
    checks.check(
        source.get("p_acc_lift_obstruction_pa2_closed") is False
        and p_acc_lift_obstruction.get("pa2_closed") is False,
        "P_acc PA2 unexpectedly closed",
    )
    checks.check(
        source.get("p_acc_lift_obstruction_current_unweighted_rate") == "O(h^6)",
        "P_acc obstruction rate link changed",
    )
    checks.check(
        source.get("p_acc_weighted_inverse_schema") == p_acc_weighted_inverse.get("schema"),
        "P_acc weighted-inverse schema link missing",
    )
    checks.check(
        source.get("p_acc_weighted_inverse_weighted_h_control_recorded") is True
        and p_acc_weighted_inverse.get("weighted_h_acceleration_control_recorded") is True,
        "P_acc weighted h-control source link missing",
    )
    checks.check(
        source.get("p_acc_weighted_inverse_unweighted_control_proved") is False
        and p_acc_weighted_inverse.get("unweighted_acceleration_uniform_control_proved") is False,
        "P_acc unweighted control source unexpectedly proved",
    )
    checks.check(
        p_acc_requirement.get("requirement_recorded") is True,
        "P_acc strict requirement record missing",
    )
    checks.check(p_acc_requirement.get("term_count") == 36, "P_acc strict term count changed")
    checks.check(
        p_acc_requirement.get("translational_term_count") == 18,
        "P_acc translational term count changed",
    )
    checks.check(
        p_acc_requirement.get("rotational_term_count") == 18,
        "P_acc rotational term count changed",
    )
    checks.check(
        p_acc_requirement.get("global_rows")
        == [24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35,
            68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79,
            112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123],
        "P_acc global row list changed",
    )
    checks.check(p_acc_requirement.get("required_unweighted_rate") == "O(h^7)", "P_acc required rate changed")
    checks.check(
        p_acc_requirement.get("blocking_primitive") == "P_acceleration_lift",
        "P_acc blocking primitive changed",
    )
    linear = p_acc_requirement.get("linear_taylor_reduction", {})
    checks.check(
        linear.get("translational") == "||m_b delta a|| <= m_max ||delta a||",
        "P_acc translational Taylor inequality changed",
    )
    checks.check(
        linear.get("rotational") == "||J_b delta alpha|| <= J_max ||delta alpha||",
        "P_acc rotational Taylor inequality changed",
    )
    checks.check(
        linear.get("remainder") == "zero for the acceleration maps because the maps are linear in acceleration",
        "P_acc Taylor remainder boundary changed",
    )
    weighted = p_acc_requirement.get("weighted_control_boundary", {})
    checks.check(weighted.get("h_delta_A_control_recorded") is True, "P_acc h-weighted control missing")
    checks.check(
        weighted.get("unweighted_acceleration_uniform_control_proved") is False,
        "P_acc unweighted control unexpectedly proved in requirement",
    )
    checks.check(
        weighted.get("h_weighted_control_sufficient_for_current_d5_budget") is False,
        "P_acc h-weighted control incorrectly accepted",
    )
    velocity = p_acc_requirement.get("velocity_collocation_boundary", {})
    checks.check(
        velocity.get("velocity_collocation_alone_sufficient_for_O_h7_acceleration") is False,
        "velocity-collocation sufficiency overclaimed",
    )
    checks.check(
        velocity.get("current_recorded_inputs_imply_only_unweighted_acceleration_rate") == "O(h^6)",
        "velocity-collocation rate algebra changed",
    )
    checks.check(
        velocity.get("rate_algebra", {}).get("weighted_h_delta_A_O_h7_is_not_enough_for_current_D5_budget")
        is True,
        "weighted acceleration insufficiency algebra missing",
    )
    checks.check(
        "unweighted ||delta A||=O(h^7)" in p_acc_requirement.get("strict_close_condition", ""),
        "P_acc strict close condition missing unweighted rate",
    )
    anti_req = p_acc_requirement.get("anti_overclaim", {})
    for key in [
        "does_not_use_d5_direct_substitution",
        "does_not_use_finite_probe_as_proof",
        "does_not_use_residual_to_error_promotion",
        "does_not_certify_p_acc",
        "does_not_certify_taylor_terms",
    ]:
        checks.check(anti_req.get(key) is True, f"P_acc anti-overclaim marker missing: {key}")
    checks.check(manuscript.get("main_tex_present") is True, "main TeX term-budget link missing")
    checks.check(manuscript.get("flat_tex_present") is True, "flat TeX term-budget link missing")
    checks.check(isinstance(term_rows, list) and len(term_rows) == 162, "term row list length changed")
    for term in term_rows:
        if not isinstance(term, dict):
            checks.check(False, "term row is not an object")
            continue
        checks.check(term.get("required_bound") == "O(h^7)", "term required bound changed")
        checks.check(term.get("strict_taylor_reduction_recorded") is True, "term strict Taylor reduction missing")
        checks.check(isinstance(term.get("taylor_template"), str), "term Taylor template missing")
        checks.check(isinstance(term.get("conditional_inequality"), str), "term inequality missing")
        checks.check(
            isinstance(term.get("primitive_obligations"), list)
            and "P_uniform_tube_constants" in term.get("primitive_obligations", []),
            "term primitive obligations missing P_tube",
        )
        checks.check(
            isinstance(term.get("blocking_primitive_ids"), list)
            and len(term.get("blocking_primitive_ids", [])) >= 1,
            "term blocking primitive list missing",
        )
        checks.check(term.get("blocked_by_open_primitives") is True, "term open primitive blocker missing")
        anti = term.get("anti_circularity", {})
        checks.check(anti.get("uses_stage_residual_defect") is False, "term uses stage-residual shortcut")
        checks.check(anti.get("uses_d5_direct_substitution") is False, "term uses direct-substitution shortcut")
        checks.check(anti.get("uses_finite_probe_as_proof") is False, "term uses finite probe as proof")
        checks.check(
            anti.get("uses_residual_to_error_promotion") is False,
            "term uses residual-to-error promotion",
        )
        if term.get("term_id") in {"T_acceleration_lift", "R_angular_acceleration_lift"}:
            checks.check(
                term.get("requires_unweighted_acceleration_O_h7") is True,
                "acceleration term no longer requires unweighted O(h^7)",
            )
            checks.check(
                term.get("h_weighted_acceleration_control_sufficient") is False,
                "h-weighted acceleration incorrectly closes acceleration term",
            )
            checks.check(
                term.get("blocking_primitive_ids") == ["P_acceleration_lift"],
                "acceleration blocker primitive changed",
            )
        else:
            checks.check(
                term.get("requires_unweighted_acceleration_O_h7") is False,
                "non-acceleration term incorrectly marked as acceleration blocker",
            )
        checks.check(term.get("regularity_inputs_available") is True, "term regularity input missing")
        checks.check(term.get("row_binding_available") is True, "term row binding missing")
        checks.check(term.get("taylor_bound_proved") is False, "term unexpectedly proved")
        checks.check(term.get("certifies_theorem_now") is False, "term unexpectedly certifies theorem")
        checks.check(term.get("finite_probe_evidence_sufficient") is False, "finite probe term boundary changed")
        checks.check(
            term.get("residual_to_error_promotion_allowed") is False,
            "residual-to-error term boundary changed",
        )

    for token in [
        "Status: **D5 Taylor subterm budget recorded; separate primitive-route certificate remains open**.",
        "Here `submission_ready=false` is scoped to the primitive Taylor/global proof-package boundary,",
        "not to the separate narrowed-claim package decision.",
        "Total Taylor subterms: `162`.",
        "Certified Taylor-bound subterms: `0/162`.",
        "Open Taylor-bound subterms: `162/162`.",
        "Submission-ready scope: `d5_primitive_taylor_term_budget_global_boundary_not_narrowed_claim_package_decision`.",
        "Primitive Taylor budget scope: `162_subterm_budget_inventory_not_actual_taylor_bound_closure`.",
        "Remaining global submission boundaries: `full_source_policy_package_ready,theorem_level_eta_h_solver_policy_evidence,closed_residual_to_error_theorem_for_mechanism_rows`.",
        "Primitive/Taylor reduction subterms: `162/162`.",
        "Anti-circular Taylor subterms: `162/162`.",
        "Unweighted acceleration-blocked subterms: `36/36`.",
        "Recorded `h delta A` control is not sufficient",
        "P_acc Primitive/Taylor Requirement",
        "Acceleration Taylor subterms: `36`.",
        "Required primitive input: unweighted `||delta A||=O(h^7)`.",
        "Velocity-collocation alone currently gives only unweighted `O(h^6)`.",
        "`||m_b delta a|| <= m_max ||delta a||`",
        "`||J_b delta alpha|| <= J_max ||delta alpha||`",
        "Separate primitive/Taylor PC2 route closed: `False`.",
        "Primitive/Taylor PC2 route closes only after all 162 Taylor subterms",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("D5 Taylor term-budget audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("D5 Taylor term-budget audit validation: PASS")
    print("term_rows=162")
    print("certified_taylor_bound_terms=0")
    print("pc2_closed=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
