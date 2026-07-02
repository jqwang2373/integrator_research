#!/usr/bin/env python3
"""Validate the D5 P_lambda PL4 rate-propagation audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "D5_P_LAMBDA_PL4_RATE_PROPAGATION_AUDIT.json"
AUDIT_MD = PAPER / "D5_P_LAMBDA_PL4_RATE_PROPAGATION_AUDIT.md"


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
        p_lambda_interface = read_json(PAPER / "D5_P_LAMBDA_INTERFACE_AUDIT.json")
        p_lambda_pl2 = read_json(PAPER / "D5_P_LAMBDA_PL2_GEOMETRIC_MARGIN_AUDIT.json")
        p_lambda_d3 = read_json(PAPER / "D5_P_LAMBDA_D3_NONCIRCULARITY_AUDIT.json")
        p_state_gap = read_json(PAPER / "D5_P_STATE_LIFT_GAP_AUDIT.json")
        p_acc_pa2 = read_json(PAPER / "D5_P_ACC_PA2_WEIGHTED_INVERSE_AUDIT.json")
        proof_manifest = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
    except Exception as exc:  # noqa: BLE001
        print(f"D5 P_lambda PL4 rate-propagation audit validation: FAIL\n- {exc}")
        return 1

    summary = audit.get("summary", {})
    proof = audit.get("proof_certificate", {})
    source = audit.get("source_consistency", {})
    claim = audit.get("claim_boundary", {})

    checks.check(audit.get("schema") == "d5-p-lambda-pl4-rate-propagation-audit-v1", "schema changed")
    checks.check(
        audit.get("status") == "p_lambda_pl4_rate_propagation_closed_conditionally_lift_open",
        "status changed",
    )
    checks.check(audit.get("read_only") is True, "audit must be read-only")
    checks.check(audit.get("run_v047_invoked") is False, "run_v047 must not be invoked")
    checks.check(audit.get("submission_ready") is False, "submission readiness overclaimed")
    checks.check(audit.get("pc2_closed") is False, "PC2 unexpectedly closed")
    checks.check(audit.get("proof_gap_closed") is False, "proof gap unexpectedly closed")
    checks.check(audit.get("primitive_id") == "P_multiplier_lift", "primitive id changed")
    checks.check(audit.get("primitive_closed") is False, "P_lambda unexpectedly closed")
    checks.check(audit.get("pl4_lift_propagation_closed") is True, "PL4 propagation not closed")
    checks.check(audit.get("conditional_multiplier_lift_rate_proved") is True, "conditional rate missing")
    checks.check(audit.get("multiplier_lift_rate_proved") is False, "actual multiplier lift overclaimed")
    checks.check(audit.get("actual_state_lift_input_closed") is False, "state input unexpectedly closed")
    checks.check(
        audit.get("actual_acceleration_lift_input_closed") is False,
        "acceleration input unexpectedly closed",
    )
    checks.check(audit.get("pl2_uniform_inf_sup_bound_proved") is True, "PL2 inf-sup link missing")
    checks.check(audit.get("uniform_left_inverse_available") is True, "PL2 left inverse link missing")
    checks.check(audit.get("term_bounds_proved") == 0, "Taylor bounds unexpectedly proved")
    checks.check(audit.get("direct_multiplier_term_rows") == 36, "direct multiplier row count changed")
    checks.check(audit.get("term_rows_using_p_lambda") == 72, "P_lambda term-row count changed")
    checks.check(len(audit.get("closed_subproofs", [])) == 4, "closed subproof list changed")
    checks.check(
        audit.get("open_dependencies")
        == ["P_state actual state lift O(h^7)", "P_acc unweighted acceleration lift O(h^7)"],
        "open dependencies changed",
    )

    checks.check(summary.get("closed_subproof_count_for_this_audit") == 1, "PL4 subproof count changed")
    checks.check(summary.get("p_lambda_closed_subproof_count_after_pl4") == 4, "P_lambda subproof count changed")
    checks.check(summary.get("required_subproof_count") == 4, "required subproof count changed")
    checks.check(summary.get("open_subproof_count_after_pl4") == 0, "open subproof count changed")
    checks.check(summary.get("open_input_dependency_count") == 2, "open input dependency count changed")
    checks.check(summary.get("pl1_interface_closed") is True, "PL1 link missing")
    checks.check(summary.get("pl2_uniform_inf_sup_bound_proved") is True, "PL2 summary link missing")
    checks.check(summary.get("pl3_d3_noncircularity_closed") is True, "PL3 summary link missing")
    checks.check(summary.get("pl4_lift_propagation_closed") is True, "PL4 summary link missing")
    checks.check(summary.get("conditional_multiplier_lift_rate_proved") is True, "conditional summary missing")
    checks.check(summary.get("multiplier_lift_rate_proved") is False, "actual rate overclaimed in summary")
    checks.check(summary.get("actual_state_lift_input_closed") is False, "state input overclaimed in summary")
    checks.check(
        summary.get("actual_acceleration_lift_input_closed") is False,
        "acceleration input overclaimed in summary",
    )
    checks.check(summary.get("term_bounds_proved") == 0, "summary Taylor bounds unexpectedly proved")
    checks.check(summary.get("pc2_closed") is False, "summary PC2 unexpectedly closed")

    checks.check(
        proof.get("route") == "quantitative_implicit_function_taylor_expansion",
        "proof route changed",
    )
    checks.check("F(y,lambda,h)" in proof.get("stage_row_map", ""), "stage row map missing")
    checks.check("B(y,lambda,h) delta_lambda" in proof.get("taylor_expansion", ""), "Taylor expansion missing")
    checks.check("gamma_PL2" in proof.get("left_inverse_bound", ""), "PL2 lower bound missing")
    checks.check("C_R" in proof.get("compact_remainder_bound", ""), "compact remainder bound missing")
    checks.check("absorbed" in proof.get("absorption_step", ""), "absorption step missing")
    checks.check("O(h^7)" in proof.get("conditional_rate", ""), "conditional O(h^7) rate missing")
    checks.check(
        proof.get("uses_first_order_taylor_with_quadratic_remainder") is True,
        "Taylor proof marker missing",
    )
    checks.check(
        proof.get("uses_quantitative_implicit_function_theorem") is True,
        "implicit-function proof marker missing",
    )
    checks.check(proof.get("uses_stage_residual_defect") is False, "stage residual used")
    checks.check(proof.get("uses_d5_dynamic_residual_defect") is False, "D5 dynamic defect used")
    checks.check(proof.get("uses_direct_substitution_as_proof") is False, "direct substitution used")
    checks.check(proof.get("uses_finite_probe_as_proof") is False, "finite probe used")
    checks.check(proof.get("uses_d3_as_rate_proof") is False, "D3 used as rate proof")

    checks.check(audit.get("manuscript_link", {}).get("main_tex_present") is True, "main TeX lemma link missing")
    checks.check(audit.get("manuscript_link", {}).get("flat_tex_present") is True, "flat TeX lemma link missing")
    checks.check(
        audit.get("manuscript_link", {}).get("reader_facing_conditional_nonclosure_main") is True,
        "main TeX conditional nonclosure lemma missing",
    )
    checks.check(
        audit.get("manuscript_link", {}).get("reader_facing_conditional_nonclosure_flat") is True,
        "flat TeX conditional nonclosure lemma missing",
    )
    checks.check(
        source.get("p_lambda_interface_closed") is True
        and p_lambda_interface.get("pl1_interface_closed") is True,
        "PL1 source link missing",
    )
    checks.check(
        source.get("p_lambda_pl2_uniform_inf_sup_bound_proved") is True
        and p_lambda_pl2.get("pl2_uniform_inf_sup_bound_proved") is True,
        "PL2 source link missing",
    )
    checks.check(
        source.get("p_lambda_d3_noncircularity_closed") is True
        and p_lambda_d3.get("pl3_d3_noncircularity_closed") is True,
        "PL3 source link missing",
    )
    checks.check(
        source.get("p_state_primitive_closed") is False and p_state_gap.get("primitive_closed") is False,
        "P_state source unexpectedly closed",
    )
    checks.check(
        source.get("p_acc_unweighted_acceleration_uniform_control_proved") is False
        and p_acc_pa2.get("unweighted_acceleration_uniform_control_proved") is False,
        "P_acc source unexpectedly proves unweighted acceleration",
    )
    checks.check(source.get("p_tube_closed") is True, "P_tube source link missing")
    checks.check(source.get("proof_manifest_pc2_closed") is True, "direct PC2 source link missing")
    checks.check(
        proof_manifest.get("closure_state", {}).get("primitive_lift_route_closed") is False,
        "proof manifest unexpectedly closes primitive route",
    )
    checks.check("P_lambda primitive closure" in claim.get("forbidden_now", []), "P_lambda closure not forbidden")
    checks.check("P_acc closure" in claim.get("forbidden_now", []), "P_acc closure not forbidden")

    for token in [
        "Status: **PL4 conditional multiplier-rate propagation closed; P_lambda remains open**.",
        "P_lambda subproofs closed: `4/4`.",
        "Open input dependencies: `2`.",
        "Direct multiplier rows: `36/36`.",
        "Term rows using P_lambda: `72/72`.",
        "PL2 uniform inf-sup proved: `True`.",
        "Conditional multiplier lift rate proved: `True`.",
        "Actual multiplier lift rate proved: `False`.",
        "P_state actual state lift input closed: `False`.",
        "P_acc unweighted acceleration lift input closed: `False`.",
        "P_lambda primitive closed: `False`.",
        "Taylor term bounds proved: `0`.",
        "Primitive/Taylor PC2 route closed: `False`.",
        "Reader-facing conditional nonclosure lemma main/flat: `True/True`.",
        "`0 = B delta_lambda + D_y F delta_y + O((||delta_y||+||delta_lambda||)^2)`.",
        "`||delta_lambda|| <= C_lambda_y (||delta_z|| + ||delta_a||)`.",
        "The actual multiplier lift rate remains open.",
        "The reader-facing PL4 nonclosure lemma records that `4/4` local PL subproofs mean conditional propagation only, not actual `P_lambda` closure.",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("D5 P_lambda PL4 rate-propagation audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("D5 P_lambda PL4 rate-propagation audit validation: PASS")
    print("p_lambda_subproofs_closed=4/4")
    print("open_input_dependencies=2")
    print("p_lambda_closed=False")
    print("pc2_closed=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
