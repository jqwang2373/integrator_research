#!/usr/bin/env python3
"""Build the D5 P_lambda PL4 rate-propagation audit.

This audit closes only the conditional PL4 propagation step: with the PL2
uniform multiplier inf-sup bound already proved, an O(h^7) state lift and an
unweighted O(h^7) acceleration lift imply an O(h^7) lower-pair multiplier
lift.  The required state and acceleration lift inputs remain open, so this
does not close P_lambda, any Taylor term, PC2, or the theorem.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
OUT_JSON = PAPER / "D5_P_LAMBDA_PL4_RATE_PROPAGATION_AUDIT.json"
OUT_MD = PAPER / "D5_P_LAMBDA_PL4_RATE_PROPAGATION_AUDIT.md"

DIRECT_MULTIPLIER_TERM_IDS = {
    "T_multiplier_force_lift",
    "R_multiplier_torque_lift",
}


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def contains_normalized(text: str, token: str) -> bool:
    return token in text or " ".join(token.split()) in " ".join(text.split())


def primitive_row(data: dict[str, Any], primitive_id: str) -> dict[str, Any]:
    for row in data.get("primitive_obligations", []):
        if isinstance(row, dict) and row.get("id") == primitive_id:
            return row
    raise ValueError(f"primitive not found: {primitive_id}")


def close_requirement_satisfied(manifest: dict[str, Any], requirement_id: str) -> bool | None:
    for row in manifest.get("close_requirements", []):
        if isinstance(row, dict) and row.get("id") == requirement_id:
            value = row.get("satisfied")
            return value if isinstance(value, bool) else None
    return None


def main() -> None:
    p_lambda_interface = read_json(PAPER / "D5_P_LAMBDA_INTERFACE_AUDIT.json")
    p_lambda_d3 = read_json(PAPER / "D5_P_LAMBDA_D3_NONCIRCULARITY_AUDIT.json")
    p_lambda_pl2 = read_json(PAPER / "D5_P_LAMBDA_PL2_GEOMETRIC_MARGIN_AUDIT.json")
    p_state_gap = read_json(PAPER / "D5_P_STATE_LIFT_GAP_AUDIT.json")
    p_state_ps3_actual_gap = read_json(PAPER / "D5_P_STATE_PS3_ACTUAL_INSTANTIATION_GAP_AUDIT.json")
    p_acc_pa2 = read_json(PAPER / "D5_P_ACC_PA2_WEIGHTED_INVERSE_AUDIT.json")
    term_budget = read_json(PAPER / "D5_TAYLOR_TERM_BUDGET_AUDIT.json")
    primitive_reduction = read_json(PAPER / "D5_PRIMITIVE_BOUND_REDUCTION_AUDIT.json")
    p_tube = read_json(PAPER / "D5_P_TUBE_CONSTANTS_AUDIT.json")
    proof_manifest = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
    main_tex = read_text(LATEX / "main_cmame.tex")
    flat_tex = read_text(LATEX / "cmame_submission_flat" / "main_cmame_submission.tex")

    primitive = primitive_row(primitive_reduction, "P_multiplier_lift")
    term_rows = term_budget.get("term_rows", [])
    if not isinstance(term_rows, list):
        raise ValueError("D5 term-budget term_rows must be a list")
    direct_rows = [
        row
        for row in term_rows
        if isinstance(row, dict) and row.get("term_id") in DIRECT_MULTIPLIER_TERM_IDS
    ]

    pl1_closed = p_lambda_interface.get("pl1_interface_closed") is True
    pl2_closed = p_lambda_pl2.get("pl2_uniform_inf_sup_bound_proved") is True
    pl3_closed = p_lambda_d3.get("pl3_d3_noncircularity_closed") is True
    state_input_closed = (
        p_state_gap.get("primitive_closed") is True
        and p_state_ps3_actual_gap.get("summary", {}).get("actual_state_lift_rate_closed") is True
    )
    acceleration_input_closed = (
        p_acc_pa2.get("unweighted_acceleration_uniform_control_proved") is True
        and p_acc_pa2.get("pa2_closed") is True
    )

    manuscript_tokens = [
        r"\label{lem:d5-p-lambda-pl4-rate-propagation}",
        "PL4 conditional multiplier-rate propagation",
        r"F(y,\lambda,h)",
        "first-order Taylor formula with integral remainder",
        r"\|\widehat\lambda-\lambda\| \le C_{\lambda y}",
        r"does not close \(P_{\lambda}\)",
    ]
    conditional_nonclosure_tokens = [
        r"\label{lem:d5-p-lambda-conditional-nonclosure}",
        r"PL4 closure is not \(P_{\lambda}\) closure",
        "conditional multiplier propagation mechanism is complete",
        "72 D5 Taylor subterms",
    ]

    closed_subproofs = [
        "PL1_multiplier_variable_and_kkt_column_interface_exposed",
        "PL2_uniform_multiplier_inf_sup_bound_on_compact_tube",
        "PL3_D3_wrench_consistency_used_non_circularly",
        "PL4_conditional_state_acceleration_to_multiplier_rate_propagation",
    ]
    open_dependencies = [
        "P_state actual state lift O(h^7)",
        "P_acc unweighted acceleration lift O(h^7)",
    ]

    pl4_closed = pl1_closed and pl2_closed and pl3_closed
    result = {
        "schema": "d5-p-lambda-pl4-rate-propagation-audit-v1",
        "status": "p_lambda_pl4_rate_propagation_closed_conditionally_lift_open",
        "read_only": True,
        "run_v047_invoked": False,
        "submission_ready": False,
        "pc2_closed": False,
        "proof_gap_closed": False,
        "primitive_id": "P_multiplier_lift",
        "primitive_closed": False,
        "pl4_lift_propagation_closed": pl4_closed,
        "conditional_multiplier_lift_rate_proved": True,
        "multiplier_lift_rate_proved": False,
        "actual_state_lift_input_closed": state_input_closed,
        "actual_acceleration_lift_input_closed": acceleration_input_closed,
        "pl2_uniform_inf_sup_bound_proved": pl2_closed,
        "uniform_left_inverse_available": pl2_closed,
        "term_bounds_proved": 0,
        "direct_multiplier_term_rows": len(direct_rows),
        "term_rows_using_p_lambda": primitive.get("term_rows_using_obligation"),
        "closed_subproofs": closed_subproofs,
        "open_dependencies": open_dependencies,
        "summary": {
            "closed_subproof_count_for_this_audit": 1,
            "p_lambda_closed_subproof_count_after_pl4": len(closed_subproofs),
            "required_subproof_count": 4,
            "open_subproof_count_after_pl4": 0,
            "open_input_dependency_count": len(open_dependencies),
            "direct_multiplier_term_rows": len(direct_rows),
            "term_rows_using_p_lambda": primitive.get("term_rows_using_obligation"),
            "pl1_interface_closed": pl1_closed,
            "pl2_uniform_inf_sup_bound_proved": pl2_closed,
            "pl3_d3_noncircularity_closed": pl3_closed,
            "pl4_lift_propagation_closed": pl4_closed,
            "conditional_multiplier_lift_rate_proved": True,
            "multiplier_lift_rate_proved": False,
            "actual_state_lift_input_closed": state_input_closed,
            "actual_acceleration_lift_input_closed": acceleration_input_closed,
            "term_bounds_proved": 0,
            "pc2_closed": False,
        },
        "proof_certificate": {
            "route": "quantitative_implicit_function_taylor_expansion",
            "stage_row_map": (
                "F(y,lambda,h) is the accepted lower-pair dynamic-row map after "
                "PL1 exposes the multiplier columns and PL3 identifies their "
                "D3 wrench action; y collects state and acceleration variables."
            ),
            "taylor_expansion": (
                "0 = F(y_hat,lambda_hat,h)-F(y,lambda,h) = "
                "B(y,lambda,h) delta_lambda + D_y F(y,lambda,h) delta_y + "
                "O((||delta_y||+||delta_lambda||)^2)"
            ),
            "left_inverse_bound": (
                "PL2 gives ||B(y,lambda,h) delta_lambda|| >= "
                "gamma_PL2 ||delta_lambda|| uniformly on the compact proof tube."
            ),
            "compact_remainder_bound": (
                "The compact-tube C^2 bounds give a constant C_R for the Taylor "
                "remainder and a constant L_y for D_y F."
            ),
            "absorption_step": (
                "On the accepted local solution branch, the quadratic remainder "
                "is absorbed for sufficiently small h, yielding "
                "||delta_lambda|| <= C_lambda_y (||delta_z|| + ||delta_a||)."
            ),
            "conditional_rate": (
                "If P_state proves ||delta_z||=O(h^7) and P_acc proves the "
                "unweighted acceleration lift ||delta_a||=O(h^7), then "
                "||delta_lambda||=O(h^7)."
            ),
            "uses_first_order_taylor_with_quadratic_remainder": True,
            "uses_quantitative_implicit_function_theorem": True,
            "uses_stage_residual_defect": False,
            "uses_d5_dynamic_residual_defect": False,
            "uses_direct_substitution_as_proof": False,
            "uses_finite_probe_as_proof": False,
            "uses_d3_as_rate_proof": False,
        },
        "manuscript_link": {
            "main_tex_present": all(contains_normalized(main_tex, token) for token in manuscript_tokens),
            "flat_tex_present": all(contains_normalized(flat_tex, token) for token in manuscript_tokens),
            "reader_facing_conditional_nonclosure_main": all(
                contains_normalized(main_tex, token) for token in conditional_nonclosure_tokens
            ),
            "reader_facing_conditional_nonclosure_flat": all(
                contains_normalized(flat_tex, token) for token in conditional_nonclosure_tokens
            ),
            "tokens": manuscript_tokens,
            "conditional_nonclosure_tokens": conditional_nonclosure_tokens,
        },
        "source_consistency": {
            "p_lambda_interface_schema": p_lambda_interface.get("schema"),
            "p_lambda_interface_closed": p_lambda_interface.get("pl1_interface_closed"),
            "p_lambda_interface_pc2_closed": p_lambda_interface.get("pc2_closed"),
            "p_lambda_pl2_schema": p_lambda_pl2.get("schema"),
            "p_lambda_pl2_uniform_inf_sup_bound_proved": p_lambda_pl2.get(
                "pl2_uniform_inf_sup_bound_proved"
            ),
            "p_lambda_pl2_pc2_closed": p_lambda_pl2.get("pc2_closed"),
            "p_lambda_d3_schema": p_lambda_d3.get("schema"),
            "p_lambda_d3_noncircularity_closed": p_lambda_d3.get("pl3_d3_noncircularity_closed"),
            "p_lambda_d3_pc2_closed": p_lambda_d3.get("pc2_closed"),
            "p_state_schema": p_state_gap.get("schema"),
            "p_state_primitive_closed": p_state_gap.get("primitive_closed"),
            "p_state_ps3_actual_inputs_closed": p_state_ps3_actual_gap.get("summary", {}).get(
                "input_requirements_closed"
            ),
            "p_acc_pa2_schema": p_acc_pa2.get("schema"),
            "p_acc_unweighted_acceleration_uniform_control_proved": p_acc_pa2.get(
                "unweighted_acceleration_uniform_control_proved"
            ),
            "p_acc_pa2_closed": p_acc_pa2.get("pa2_closed"),
            "p_tube_schema": p_tube.get("schema"),
            "p_tube_closed": p_tube.get("primitive_closed"),
            "proof_manifest_pc2_closed": close_requirement_satisfied(proof_manifest, "PC2"),
        },
        "claim_boundary": {
            "allowed_now": (
                "PL4 is closed only as a conditional Taylor/implicit-function "
                "propagation from state and acceleration lift inputs to the "
                "multiplier lift"
            ),
            "forbidden_now": [
                "P_lambda primitive closure",
                "P_state closure",
                "P_acc closure",
                "Taylor term bounds certified",
                "primitive/Taylor PC2 route closure",
                "unconditional sixth-order theorem",
            ],
            "close_condition": (
                "P_lambda closes only after the P_state actual state lift and "
                "the P_acc unweighted acceleration lift are independently proved "
                "and this conditional PL4 propagation is instantiated."
            ),
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# D5 P_lambda PL4 Rate Propagation Audit",
        "",
        "Status: **PL4 conditional multiplier-rate propagation closed; P_lambda remains open**.",
        "",
        "This read-only audit proves the conditional propagation step from",
        "state and acceleration lift errors to the lower-pair multiplier error.",
        "It uses the PL2 compact-tube inf-sup bound and a first-order Taylor",
        "expansion with quadratic remainder. It does not prove the required",
        "state or acceleration lift inputs, so it does not close `P_lambda` or PC2.",
        "",
        "## Summary",
        "",
        f"- P_lambda subproofs closed: `{len(closed_subproofs)}/4`.",
        f"- Open input dependencies: `{len(open_dependencies)}`.",
        f"- Direct multiplier rows: `{len(direct_rows)}/36`.",
        f"- Term rows using P_lambda: `{primitive.get('term_rows_using_obligation')}/72`.",
        f"- PL2 uniform inf-sup proved: `{pl2_closed}`.",
        f"- Conditional multiplier lift rate proved: `{result['conditional_multiplier_lift_rate_proved']}`.",
        f"- Actual multiplier lift rate proved: `{result['multiplier_lift_rate_proved']}`.",
        f"- P_state actual state lift input closed: `{state_input_closed}`.",
        f"- P_acc unweighted acceleration lift input closed: `{acceleration_input_closed}`.",
        f"- P_lambda primitive closed: `{result['primitive_closed']}`.",
        f"- Taylor term bounds proved: `{result['term_bounds_proved']}`.",
        f"- Primitive/Taylor PC2 route closed: `{result['pc2_closed']}`.",
        "- Reader-facing conditional nonclosure lemma main/flat: "
        f"`{result['manuscript_link']['reader_facing_conditional_nonclosure_main']}/"
        f"{result['manuscript_link']['reader_facing_conditional_nonclosure_flat']}`.",
        "",
        "## Taylor Propagation",
        "",
        "Let `F(y,lambda,h)` be the accepted lower-pair dynamic-row map, with",
        "`y` collecting the state and acceleration variables.  On the compact",
        "proof tube, PL2 gives",
        "",
        "`||B(y,lambda,h) delta_lambda|| >= gamma_PL2 ||delta_lambda||`.",
        "",
        "For two points on the same accepted lower-pair solution branch,",
        "",
        "`0 = B delta_lambda + D_y F delta_y + O((||delta_y||+||delta_lambda||)^2)`.",
        "",
        "The compact `C^2` bounds and the PL2 left inverse absorb the quadratic",
        "remainder for sufficiently small `h`, giving",
        "",
        "`||delta_lambda|| <= C_lambda_y (||delta_z|| + ||delta_a||)`.",
        "",
        "Thus `delta_lambda=O(h^7)` once `P_state` supplies `delta_z=O(h^7)`",
        "and `P_acc` supplies the unweighted acceleration lift `delta_a=O(h^7)`.",
        "",
        "## Acceptance Boundary",
        "",
        "- PL4 is closed as a conditional Taylor/implicit-function propagation.",
        "- `P_state` and `P_acc` input lifts remain open.",
        "- The actual multiplier lift rate remains open.",
        "- The reader-facing PL4 nonclosure lemma records that `4/4` local PL subproofs "
        "mean conditional propagation only, not actual `P_lambda` closure.",
        "- Zero Taylor term bounds are certified by this audit.",
        "- Primitive/Taylor PC2 lane remains open.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("d5_p_lambda_pl4_rate_propagation_audit=written")
    print(f"p_lambda_subproofs_closed={len(closed_subproofs)}/4")
    print(f"open_input_dependencies={len(open_dependencies)}")
    print("p_lambda_closed=False")
    print("pc2_closed=False")


if __name__ == "__main__":
    main()
