#!/usr/bin/env python3
"""Validate the D5 P_state PS3 full-residual route certificate."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "D5_P_STATE_PS3_FULL_RESIDUAL_ROUTE_CERTIFICATE.json"
AUDIT_MD = PAPER / "D5_P_STATE_PS3_FULL_RESIDUAL_ROUTE_CERTIFICATE.md"


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
        aggregate = read_json(PAPER / "D5_P_STATE_PS2_AGGREGATE_PROMOTION_AUDIT.json")
        conditional = read_json(PAPER / "D5_P_STATE_PS3_CONDITIONAL_CONVERSION_AUDIT.json")
        h_acc = read_json(PAPER / "D5_P_STATE_PS3_H_ACC_INPUT_OBSTRUCTION_AUDIT.json")
        kinematic = read_json(PAPER / "KINEMATIC_ROW_DEFECT_CERTIFICATE.json")
        direct = read_json(PAPER / "D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE.json")
        proof_manifest = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
    except Exception as exc:  # noqa: BLE001
        print(f"D5 P_state PS3 full-residual route certificate validation: FAIL\n- {exc}")
        return 1

    summary = audit.get("summary", {})
    route = audit.get("direct_route_certificate", {})
    noncirc = audit.get("non_circularity", {})
    primitive = audit.get("primitive_route_boundary", {})
    source = audit.get("source_consistency", {})
    manuscript = audit.get("manuscript_link", {})
    reference = audit.get("reference_proof_style", {})
    steps = audit.get("strict_proof_steps", [])
    closure_state = proof_manifest.get("closure_state", {})

    checks.check(
        audit.get("schema") == "d5-p-state-ps3-full-residual-route-certificate-v1",
        "schema changed",
    )
    checks.check(
        audit.get("status") == "full_residual_route_certificate_closed_primitive_route_boundary_retained",
        "status changed",
    )
    checks.check(audit.get("read_only") is True, "certificate must be read-only")
    checks.check(audit.get("run_v047_invoked") is False, "run_v047 must not be invoked")
    checks.check(audit.get("submission_ready") is False, "submission readiness overclaimed")
    checks.check(audit.get("proof_gap_closed") is True, "referenced proof gap closure missing")
    checks.check(
        audit.get("direct_residual_bridge_proof_gap_closed") is True,
        "scoped direct residual-bridge closure missing",
    )
    checks.check(
        audit.get("proof_gap_closed_scope") == "direct_residual_bridge_ps3_corollary_only",
        "proof-gap closure scope missing or changed",
    )
    checks.check(audit.get("primitive_id") == "P_state_lift", "primitive id changed")
    checks.check(audit.get("plan_id") == "P_state", "plan id changed")
    checks.check(audit.get("pc2_closed_by_referenced_manifest") is True, "referenced PC2 closure not linked")
    checks.check(audit.get("primitive_route_pc2_closed") is False, "primitive route PC2 unexpectedly closed")
    checks.check(audit.get("primitive_route_closed") is False, "primitive route unexpectedly closed")
    checks.check(audit.get("primitive_taylor_route_closed") is False, "primitive Taylor route unexpectedly closed")
    checks.check(audit.get("residual_to_error_route_closed") is False, "residual-to-error route unexpectedly closed")
    checks.check(
        audit.get("multiplier_reaction_output_order_claimed") is False,
        "multiplier/reaction output order overclaimed",
    )
    checks.check(
        audit.get("p_state_primitive_closed_by_primitive_route") is False,
        "P_state primitive route unexpectedly closed",
    )
    checks.check(audit.get("direct_route_p_state_corollary_closed") is True, "direct-route corollary not closed")
    checks.check(audit.get("certifies_strict_taylor_subproof") is True, "strict Taylor subproof not certified")
    checks.check(audit.get("certifies_induced_taylor_bounds") is False, "induced Taylor bounds overclaimed")
    checks.check(audit.get("certifies_primitive_taylor_route") is False, "primitive Taylor route overclaimed")

    checks.check(route.get("full_132_row_residual_route_closed") is True, "full residual route not closed")
    checks.check(route.get("direct_route_ps3_input_closed") is True, "direct-route PS3 input not closed")
    checks.check(route.get("direct_route_state_lift_rate_closed") is True, "direct-route state lift not closed")
    checks.check(
        route.get("direct_route_h_weighted_acceleration_input_closed") is True,
        "direct-route h-acceleration input not closed",
    )
    checks.check(route.get("non_dynamic_rows_from_kinematic_certificate") == 96, "non-dynamic row count changed")
    checks.check(route.get("dynamic_rows_from_direct_substitution") == 36, "dynamic row count changed")
    checks.check(route.get("full_stage_rows") == 132, "full stage row count changed")
    checks.check("row_local_taylor_remainder_mode" not in route, "stale Taylor-remainder route field returned")
    checks.check(
        "zero residual remainder" in route.get("direct_route_residual_remainder_mode", ""),
        "zero direct-route residual-remainder mode missing",
    )
    checks.check(
        route.get("primitive_162_subterm_taylor_lane_certified") is False,
        "primitive 162-subterm Taylor lane unexpectedly certified",
    )
    checks.check("stage-residual-defect" in route.get("stage_residual_perturbation_source", ""), "stage lemma missing")
    checks.check(route.get("h_acceleration_obstruction_bypassed") is True, "h-acc obstruction not bypassed")

    checks.check(len(steps) == 4, "strict proof step count changed")
    checks.check([item.get("id") for item in steps] == ["FR1", "FR2", "FR3", "FR4"], "strict proof step order changed")
    checks.check(all(item.get("closed") is True for item in steps), "not all strict proof steps are closed")
    checks.check(summary.get("strict_proof_steps_closed") == 4, "summary closed proof steps changed")
    checks.check(summary.get("strict_proof_steps_total") == 4, "summary proof step total changed")
    checks.check(summary.get("full_residual_route_certificate_closed") is True, "summary route not closed")
    checks.check(summary.get("direct_route_ps3_input_closed") is True, "summary PS3 input not closed")
    checks.check(summary.get("direct_route_state_lift_rate_closed") is True, "summary state lift not closed")
    checks.check(
        summary.get("direct_route_h_weighted_acceleration_input_closed") is True,
        "summary h-input not closed",
    )
    checks.check(summary.get("p_state_primitive_closed_by_primitive_route") is False, "summary overcloses P_state")
    checks.check(summary.get("primitive_route_closed") is False, "summary overcloses primitive route")
    checks.check(summary.get("primitive_route_induced_taylor_bounds_proved") == 0, "summary overclaims Taylor bounds")
    checks.check(summary.get("submission_ready") is False, "summary overclaims submission readiness")

    for key in [
        "uses_p_state_actual_ps3_as_input",
        "uses_p_acc_lift_as_input",
        "uses_p_lambda_lift_as_input",
        "uses_velocity_collocation_h_inverse_route",
        "uses_finite_probe_as_proof",
        "uses_residual_to_error_promotion",
    ]:
        checks.check(noncirc.get(key) is False, f"non-circularity shortcut used: {key}")
    checks.check("full residual" in noncirc.get("why_non_circular", ""), "non-circular reason missing full residual")

    checks.check(primitive.get("not_used_to_close_primitive_taylor_route") is True, "primitive boundary missing")
    checks.check(primitive.get("induced_taylor_bounds_proved") == 0, "primitive boundary overclaims Taylor bounds")
    checks.check(
        "P_state primitive-route closure" in primitive.get("open_primitive_route_obligations_retained", []),
        "P_state primitive obligation not retained",
    )
    checks.check(
        "P_acc unweighted acceleration lift" in primitive.get("open_primitive_route_obligations_retained", []),
        "P_acc primitive obligation not retained",
    )
    checks.check(
        "P_lambda uniform inf-sup and multiplier-rate propagation"
        in primitive.get("open_primitive_route_obligations_retained", []),
        "P_lambda primitive obligation not retained",
    )

    checks.check(source.get("aggregate_schema") == aggregate.get("schema"), "aggregate schema not linked")
    checks.check(
        source.get("aggregate_ps2_inverse_closed") is True
        and aggregate.get("ps2_inverse_or_infsup_closed") is True,
        "aggregate PS2 inverse not linked closed",
    )
    checks.check(source.get("conditional_schema") == conditional.get("schema"), "conditional schema not linked")
    checks.check(
        source.get("conditional_conversion_closed") is True
        and conditional.get("ps3_conditional_conversion_closed") is True,
        "conditional conversion not linked closed",
    )
    checks.check(source.get("h_acc_obstruction_schema") == h_acc.get("schema"), "h-acc obstruction schema not linked")
    checks.check(
        source.get("h_acc_recommended_route") == "full_132_row_dynamic_residual_route",
        "h-acc recommended route changed",
    )
    checks.check(source.get("h_acc_residual_only_input_sufficient") is False, "residual-only h input overclaimed")
    checks.check(
        source.get("h_acc_full_dynamic_residual_route_closed_before_certificate") is False,
        "source h-acc audit should remain an obstruction artifact",
    )
    checks.check(source.get("kinematic_schema") == kinematic.get("schema"), "kinematic schema not linked")
    checks.check(source.get("direct_schema") == direct.get("schema"), "direct schema not linked")
    checks.check(
        source.get("direct_certificate_closed") is True
        and direct.get("direct_route_mathematical_certificate_closed") is True,
        "direct certificate not linked closed",
    )
    checks.check(
        source.get("proof_manifest_pc2_closed_by_direct_substitution") is True
        and closure_state.get("pc2_closed_by_direct_substitution") is True,
        "proof manifest PC2 direct route not linked",
    )
    checks.check(
        source.get("proof_manifest_primitive_lift_route_closed") is False
        and closure_state.get("primitive_lift_route_closed") is False,
        "proof manifest unexpectedly closes primitive route",
    )
    checks.check(source.get("proof_manifest_stage_residual_O_h7") is True, "stage residual O(h^7) not linked")
    checks.check(
        source.get("proof_manifest_dynamic_symbolic_oracle_complete") is False,
        "dynamic symbolic oracle unexpectedly closed",
    )
    checks.check(source.get("evidence_direct_dynamic_zero_rows") == 36, "direct dynamic zero evidence changed")

    ref_features = reference.get("features_checked", {})
    checks.check(ref_features.get("expected_order_convention") is True, "reference expected-order feature missing")
    checks.check(ref_features.get("m3_fifth_order_appendix") is True, "reference m=3 appendix feature missing")
    checks.check(ref_features.get("dae_order_reduction_reported") is True, "reference DAE order-reduction feature missing")
    checks.check(ref_features.get("appendix_b_coefficients") is True, "reference appendix feature missing")
    checks.check(manuscript.get("main_tex_present") is True, "main TeX lemma missing")
    checks.check(manuscript.get("flat_tex_present") is True, "flat TeX lemma missing")
    checks.check(
        manuscript.get("feedback_nonclosure_main_tex_present") is True,
        "main TeX direct-route feedback nonclosure lemma missing",
    )
    checks.check(
        manuscript.get("feedback_nonclosure_flat_tex_present") is True,
        "flat TeX direct-route feedback nonclosure lemma missing",
    )

    for token in [
        "Status: **full residual route certificate closed; primitive route boundary retained**.",
        "Full 132-row residual route closed: `True`.",
        "Direct-route PS3 corollary closed, not primitive P_state closure: `True`.",
        "Direct-route state lift rate closed: `True`.",
        "Direct-route h-weighted acceleration input closed: `True`.",
        "Proof gap closed scope: `direct_residual_bridge_ps3_corollary_only`.",
        "Primitive/Taylor route closed: `False`.",
        "Residual-to-error route closed: `False`.",
        "Multiplier/reaction output order claimed: `False`.",
        "P_state primitive closed by primitive route: `False`.",
        "Primitive-route induced Taylor bounds proved: `0/162`.",
        "Direct-route feedback into primitive P_state blocked main/flat: `True/True`.",
        "Strict proof steps closed: `4/4`.",
        "The 36 Newton-Euler rows are handled by direct-route residual decomposition",
        "zero residual remainder after direct substitution",
        "not a certification of the primitive 162-subterm Taylor lane",
        "Primitive-route induced Taylor bounds proved: `0/162`.",
        "36 h-weighted",
        "`||delta S|| <= C_PS2 (||delta N_h^nd|| + h ||delta A||)`",
        "`h||delta A||=O(h^7)`",
        "without the circular",
        "Does not use velocity collocation as an h-inverse acceleration proof.",
        "certify the alternative primitive/Taylor route",
        "The reader-facing feedback-prohibition lemma records that the direct-route",
        "not an admissible primitive-route",
        "126 P_state-dependent primitive subterms",
        "`0/162` primitive Taylor inventory remains unchanged.",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")
    checks.check(
        "row-local Taylor remainder" not in audit_md
        and "row-local Taylor expansion" not in audit_md,
        "stale row-local Taylor wording returned in PS3 full-residual route report",
    )

    if checks.errors:
        print("D5 P_state PS3 full-residual route certificate validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("D5 P_state PS3 full-residual route certificate validation: PASS")
    print("full_residual_route_certificate_closed=True")
    print("direct_route_ps3_input_closed=True")
    print("primitive_route_closed=False")
    print("strict_proof_steps=4/4")
    return 0


if __name__ == "__main__":
    sys.exit(main())
