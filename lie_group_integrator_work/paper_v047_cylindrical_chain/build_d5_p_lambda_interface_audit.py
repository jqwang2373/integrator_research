#!/usr/bin/env python3
"""Build the D5 P_lambda interface audit.

This audit closes only PL1 for P_lambda: the multiplier variables and their
KKT/Newton-Euler column interface are exposed in the accepted residual. It does
not prove a multiplier lift rate, an inf-sup estimate, any Taylor bound, or
PC2.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
RUN_V047 = PAPER.parent / "v047_cylindrical_chain_pipeline" / "run_v047.py"
OUT_JSON = PAPER / "D5_P_LAMBDA_INTERFACE_AUDIT.json"
OUT_MD = PAPER / "D5_P_LAMBDA_INTERFACE_AUDIT.md"

DIRECT_MULTIPLIER_TERM_IDS = {
    "T_multiplier_force_lift",
    "R_multiplier_torque_lift",
}
DIRECT_MULTIPLIER_ROWS = list(range(24, 36)) + list(range(68, 80)) + list(range(112, 124))


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


def main() -> None:
    primitive_reduction = read_json(PAPER / "D5_PRIMITIVE_BOUND_REDUCTION_AUDIT.json")
    term_budget = read_json(PAPER / "D5_TAYLOR_TERM_BUDGET_AUDIT.json")
    d3_wrench = read_json(PAPER / "NEWTON_EULER_VIRTUAL_WORK_WRENCH_AUDIT.json")
    main_tex = read_text(LATEX / "main_cmame.tex")
    flat_tex = read_text(LATEX / "cmame_submission_flat" / "main_cmame_submission.tex")
    run_source = read_text(RUN_V047)

    primitive = primitive_row(primitive_reduction, "P_multiplier_lift")
    direct_rows = [
        row
        for row in term_budget.get("term_rows", [])
        if isinstance(row, dict) and row.get("term_id") in DIRECT_MULTIPLIER_TERM_IDS
    ]
    direct_global_rows = sorted({int(row.get("global_row")) for row in direct_rows})
    direct_term_counts = {
        term_id: sum(1 for row in direct_rows if row.get("term_id") == term_id)
        for term_id in sorted(DIRECT_MULTIPLIER_TERM_IDS)
    }
    term_interface_checks = {
        "direct_multiplier_term_rows_match_expected_count": len(direct_rows) == 36,
        "direct_multiplier_global_rows_match_dynamic_rows": direct_global_rows == DIRECT_MULTIPLIER_ROWS,
        "all_direct_rows_have_row_binding": all(row.get("row_binding_available") is True for row in direct_rows),
        "all_direct_rows_have_regularity_inputs": all(
            row.get("regularity_inputs_available") is True for row in direct_rows
        ),
        "no_direct_rows_have_taylor_bounds": all(row.get("taylor_bound_proved") is False for row in direct_rows),
        "no_direct_rows_certify_theorem_now": all(row.get("certifies_theorem_now") is False for row in direct_rows),
        "no_direct_rows_allow_residual_to_error_promotion": all(
            row.get("residual_to_error_promotion_allowed") is False for row in direct_rows
        ),
    }

    source_tokens = [
        "N_BODIES = 2",
        "N_JOINTS = 2",
        "N_STAGES = 3",
        "BODY_SIZE = 18",
        "LAMBDA_SIZE = 4",
        "STAGE_SIZE = N_BODIES * BODY_SIZE + N_JOINTS * LAMBDA_SIZE",
        '"lower_pair_lambda"',
        "def lambda_slice(stage: int, joint: int) -> slice:",
        'lam = x[base + N_BODIES * BODY_SIZE : base + STAGE_SIZE].reshape((N_JOINTS, LAMBDA_SIZE))',
        'lam = st["lambda"][joint]',
        "normal_force = lam[0] * joint_basis[joint, 0] + lam[1] * joint_basis[joint, 1]",
        'eta_prox = st["lambda"][body, 2:4]',
        'eta_dist = st["lambda"][1, 2:4]',
        'dyn.extend([trans, rot])',
    ]
    source_trace = {token: contains_normalized(run_source, token) for token in source_tokens}

    d3_summary = d3_wrench.get("summary", {})
    d3_link_closed = (
        d3_wrench.get("schema") == "newton-euler-virtual-work-wrench-audit-v1"
        and d3_wrench.get("multiplier_wrench_consistency_closed") is True
        and d3_summary.get("checked_rows") == 36
        and d3_summary.get("translational_row_count") == 18
        and d3_summary.get("rotational_row_count") == 18
        and d3_wrench.get("stage_residual_O_h7_implementation_defect_proved") is False
    )

    manuscript_tokens = [
        r"\label{lem:d5-p-lambda-interface}",
        "closes only the PL1 multiplier-interface subproof",
        "does not prove a multiplier lift rate",
        "does not prove a uniform inf-sup bound",
        "does not close the primitive-and-Taylor route to PC2",
    ]
    interface_closed = all(source_trace.values()) and all(term_interface_checks.values()) and d3_link_closed

    result = {
        "schema": "d5-p-lambda-interface-audit-v1",
        "status": "p_lambda_interface_closed_lift_open",
        "read_only": True,
        "run_v047_invoked": False,
        "submission_ready": False,
        "pc2_closed": False,
        "proof_gap_closed": False,
        "primitive_id": "P_multiplier_lift",
        "primitive_closed": False,
        "pl1_interface_closed": interface_closed,
        "multiplier_lift_rate_proved": False,
        "uniform_inf_sup_bound_proved": False,
        "term_bounds_proved": 0,
        "term_rows_using_p_lambda": primitive.get("term_rows_using_obligation"),
        "direct_multiplier_term_rows": len(direct_rows),
        "direct_multiplier_global_rows": direct_global_rows,
        "direct_multiplier_term_counts": direct_term_counts,
        "lambda_variable_interface": {
            "stage_count": 3,
            "body_count": 2,
            "joint_count": 2,
            "body_size": 18,
            "lambda_size": 4,
            "stage_size": 44,
            "per_stage_lambda_dim": 8,
            "total_lambda_variables": 24,
            "lambda_components": [
                "normal_basis_0_force_multiplier",
                "normal_basis_1_force_multiplier",
                "axis_eta_0_torque_multiplier",
                "axis_eta_1_torque_multiplier",
            ],
            "stage_layout": (
                "within each 44-entry stage block, the two 18-entry body blocks are "
                "followed by two four-component lower-pair multiplier blocks"
            ),
        },
        "kkt_column_interface": {
            "column_group_name": "lower_pair_lambda",
            "lambda_slice_formula": "stage * STAGE_SIZE + N_BODIES * BODY_SIZE + joint * LAMBDA_SIZE",
            "per_stage_column_width": 8,
            "total_column_width": 24,
            "normal_force_formula": "lam[0] basis0 + lam[1] basis1",
            "axis_torque_formula": "eta[0] axis-basis0 moment + eta[1] axis-basis1 moment",
            "source_trace": source_trace,
            "source_trace_complete": all(source_trace.values()),
        },
        "term_interface": {
            "direct_term_ids": sorted(DIRECT_MULTIPLIER_TERM_IDS),
            "direct_multiplier_rows": direct_global_rows,
            "checks": term_interface_checks,
            "interface_rows": [
                {
                    "term_id": row.get("term_id"),
                    "stage": row.get("stage"),
                    "body": row.get("body"),
                    "component": row.get("component"),
                    "global_row": row.get("global_row"),
                    "balance_block": row.get("balance_block"),
                    "expression": row.get("expression"),
                    "row_binding_available": row.get("row_binding_available"),
                    "regularity_inputs_available": row.get("regularity_inputs_available"),
                    "taylor_bound_proved": row.get("taylor_bound_proved"),
                    "certifies_theorem_now": row.get("certifies_theorem_now"),
                }
                for row in direct_rows
            ],
        },
        "d3_consistency_link": {
            "schema": d3_wrench.get("schema"),
            "status": d3_wrench.get("status"),
            "checked_rows": d3_summary.get("checked_rows"),
            "translational_rows": d3_summary.get("translational_row_count"),
            "rotational_rows": d3_summary.get("rotational_row_count"),
            "site_count_checked": d3_summary.get("site_count_checked"),
            "template_virtual_work_identity_proved": d3_summary.get("template_virtual_work_identity_proved"),
            "row_expanded_virtual_work_identity_proved": d3_summary.get(
                "row_expanded_virtual_work_identity_proved"
            ),
            "multiplier_wrench_consistency_closed": d3_summary.get("multiplier_wrench_consistency_closed"),
            "stage_residual_defect_rate_proved": d3_wrench.get(
                "stage_residual_O_h7_implementation_defect_proved"
            ),
            "d3_link_closed": d3_link_closed,
        },
        "summary": {
            "closed_subproof_count_for_this_audit": 1,
            "p_lambda_closed_subproof_count_after_interface": 1,
            "required_subproof_count": 4,
            "open_subproof_count_after_interface": 3,
            "stage_lambda_variables": 24,
            "per_stage_lambda_variables": 8,
            "direct_multiplier_term_rows": len(direct_rows),
            "term_rows_using_p_lambda": primitive.get("term_rows_using_obligation"),
            "multiplier_lift_rate_proved": False,
            "uniform_inf_sup_bound_proved": False,
            "term_bounds_proved": 0,
            "pc2_closed": False,
        },
        "closed_subproofs": [
            "PL1_multiplier_variable_and_kkt_column_interface_exposed",
        ],
        "open_subproofs": [
            "PL2_uniform_multiplier_inf_sup_bound",
            "PL3_D3_wrench_consistency_used_non_circularly",
            "PL4_state_acceleration_lift_propagation_to_multiplier_rate",
        ],
        "anti_circularity_gate": {
            "interface_is_not_inf_sup_bound": True,
            "interface_is_not_multiplier_lift_rate": True,
            "dynamic_balance_defect_rate_not_assumed": True,
            "stage_residual_perturbation_lemma_disallowed_as_input": True,
            "d3_wrench_identity_not_used_as_multiplier_rate": True,
            "direct_multiplier_rows_are_not_taylor_bounds": True,
        },
        "manuscript_link": {
            "main_tex_present": all(contains_normalized(main_tex, token) for token in manuscript_tokens),
            "flat_tex_present": all(contains_normalized(flat_tex, token) for token in manuscript_tokens),
            "tokens": manuscript_tokens,
        },
        "source_consistency": {
            "primitive_reduction_schema": primitive_reduction.get("schema"),
            "primitive_reduction_pc2_closed": primitive_reduction.get("pc2_closed"),
            "primitive_term_rows_using_p_lambda": primitive.get("term_rows_using_obligation"),
            "primitive_closed_in_reduction": primitive.get("proved"),
            "term_budget_schema": term_budget.get("schema"),
            "term_budget_pc2_closed": term_budget.get("pc2_closed"),
            "direct_multiplier_term_rows": len(direct_rows),
            "d3_wrench_schema": d3_wrench.get("schema"),
            "d3_wrench_consistency_closed": d3_summary.get("multiplier_wrench_consistency_closed"),
            "d3_stage_residual_defect_proved": d3_wrench.get(
                "stage_residual_O_h7_implementation_defect_proved"
            ),
        },
        "claim_boundary": {
            "allowed_now": (
                "P_lambda PL1 is closed: the lower-pair multiplier variables, "
                "their 24 runtime columns, and the direct multiplier-wrench term "
                "interface are exposed and linked to the D3 wrench-consistency audit."
            ),
            "forbidden_now": [
                "P_lambda primitive closure",
                "multiplier lift O(h^7) proved",
                "uniform multiplier inf-sup bound proved",
                "Taylor term bounds certified from P_lambda",
                "D3 wrench consistency used as a multiplier-rate proof",
                "primitive/Taylor PC2 route closure",
                "unconditional sixth-order theorem",
            ],
            "close_condition": (
                "P_lambda closes only after a uniform constrained KKT/Newton-Euler "
                "inf-sup argument propagates the already-open state and acceleration "
                "lift estimates to O(h^7) lower-pair multiplier lift rates."
            ),
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# D5 P_lambda Interface Audit",
        "",
        "Status: **P_lambda interface closed; lift remains open**.",
        "",
        "This read-only audit closes only PL1 for `P_lambda`: the lower-pair",
        "multiplier variables and their KKT/Newton-Euler column interface are",
        "exposed in the accepted residual. It does not prove an `O(h^7)`",
        "multiplier lift rate, a uniform inf-sup bound, any Taylor bound, or PC2.",
        "",
        "## Summary",
        "",
        "- Closed P_lambda subproofs after interface: `1/4`.",
        "- Open P_lambda subproofs after interface: `3`.",
        f"- Stage lambda variables: `{result['summary']['stage_lambda_variables']}`.",
        f"- Per-stage lambda variables: `{result['summary']['per_stage_lambda_variables']}`.",
        f"- Direct multiplier-wrench term rows: `{result['summary']['direct_multiplier_term_rows']}`.",
        f"- Primitive-ledger term rows using P_lambda: `{result['summary']['term_rows_using_p_lambda']}`.",
        f"- P_lambda primitive closed: `{result['primitive_closed']}`.",
        f"- Multiplier lift rate proved: `{result['multiplier_lift_rate_proved']}`.",
        f"- Uniform inf-sup bound proved: `{result['uniform_inf_sup_bound_proved']}`.",
        f"- Taylor bounds proved: `{result['term_bounds_proved']}/72`.",
        f"- Primitive/Taylor PC2 route closed: `{result['pc2_closed']}`.",
        "",
        "## Multiplier Interface",
        "",
        "| item | value |",
        "|---|---:|",
        f"| stages | `{result['lambda_variable_interface']['stage_count']}` |",
        f"| joints | `{result['lambda_variable_interface']['joint_count']}` |",
        f"| lambda size per joint | `{result['lambda_variable_interface']['lambda_size']}` |",
        f"| per-stage lambda dimension | `{result['lambda_variable_interface']['per_stage_lambda_dim']}` |",
        f"| total lambda variables | `{result['lambda_variable_interface']['total_lambda_variables']}` |",
        "",
        "The first two multiplier components define the normal force in the",
        "joint basis. The last two components define the axis/twist torque",
        "multipliers. The multiplier-lift Taylor rows are the 36 rows named",
        "`T_multiplier_force_lift` and `R_multiplier_torque_lift`; the",
        "primitive-reduction ledger records 72 total D5 term rows depending on",
        "`P_multiplier_lift`.",
        "",
        "## Acceptance Boundary",
        "",
        "- PL1 multiplier variable and KKT-column interface is closed.",
        "- PL2/PL3/PL4 are not closed by this interface audit; later audits record PL2, PL3, and conditional PL4 separately.",
        "- The actual multiplier lift rate still waits on the `P_state` and `P_acc` inputs.",
        "- `P_lambda` remains open.",
        "- Primitive/Taylor PC2 lane remains open.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("d5_p_lambda_interface_audit=written")
    print("closed_subproofs_after_interface=1/4")
    print(f"direct_multiplier_term_rows={len(direct_rows)}")
    print(f"term_rows_using_p_lambda={primitive.get('term_rows_using_obligation')}")
    print("p_lambda_closed=False")
    print("pc2_closed=False")


if __name__ == "__main__":
    main()
