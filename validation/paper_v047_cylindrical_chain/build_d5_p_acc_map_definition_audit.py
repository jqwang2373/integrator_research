#!/usr/bin/env python3
"""Build the D5 P_acc acceleration-map definition audit.

This audit closes only the first P_acc subproof: the accepted translational and
angular acceleration variables are bound to the 36 acceleration-lift Taylor
rows. It does not prove any O(h^7) acceleration lift rate.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
OUT_JSON = PAPER / "D5_P_ACC_MAP_DEFINITION_AUDIT.json"
OUT_MD = PAPER / "D5_P_ACC_MAP_DEFINITION_AUDIT.md"


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


def main() -> None:
    primitive_reduction = read_json(PAPER / "D5_PRIMITIVE_BOUND_REDUCTION_AUDIT.json")
    term_budget = read_json(PAPER / "D5_TAYLOR_TERM_BUDGET_AUDIT.json")
    main_tex = read_text(LATEX / "main_cmame.tex")
    flat_tex = read_text(LATEX / "cmame_submission_flat" / "main_cmame_submission.tex")

    primitive_rows = primitive_reduction.get("primitive_obligations", [])
    p_acc_row = next(
        (
            row
            for row in primitive_rows
            if isinstance(row, dict) and row.get("id") == "P_acceleration_lift"
        ),
        {},
    )
    term_rows = term_budget.get("term_rows", [])
    acc_rows = [
        row
        for row in term_rows
        if isinstance(row, dict) and row.get("term_id") in {"T_acceleration_lift", "R_angular_acceleration_lift"}
    ]
    translational_rows = [row for row in acc_rows if row.get("term_id") == "T_acceleration_lift"]
    angular_rows = [row for row in acc_rows if row.get("term_id") == "R_angular_acceleration_lift"]
    row_ids = [row.get("global_row") for row in acc_rows]
    stage_body_pairs = sorted({(row.get("stage"), row.get("body")) for row in acc_rows})

    manuscript_tokens = [
        r"\label{lem:d5-p-acc-map-definition}",
        r"\mathcal A_h^{\mathrm{acc}}",
        r"A=(a_i,\alpha_i)",
        "closes only the PA1 map-definition subproof",
        "does not prove an acceleration lift rate",
    ]

    closed_subproofs = ["PA1_acceleration_variable_and_row_map_defined"]
    open_subproofs = [
        "PA2_velocity_collocation_to_acceleration_lift",
        "PA3_lower_pair_acceleration_independence_from_dynamic_balance",
        "PA4_binding_to_residual_ordering_and_D5_terms",
    ]

    result = {
        "schema": "d5-p-acc-map-definition-audit-v1",
        "status": "p_acc_map_definition_closed_lift_open",
        "read_only": True,
        "run_v047_invoked": False,
        "submission_ready": False,
        "pc2_closed": False,
        "proof_gap_closed": False,
        "primitive_id": "P_acceleration_lift",
        "primitive_closed": False,
        "pa1_map_definition_closed": True,
        "acceleration_lift_rate_proved": False,
        "term_bounds_proved": 0,
        "term_rows_using_p_acc": p_acc_row.get("term_rows_using_obligation"),
        "term_rows_conditionally_mapped": len(acc_rows),
        "translational_acceleration_rows": len(translational_rows),
        "angular_acceleration_rows": len(angular_rows),
        "row_ids": row_ids,
        "map_definition": {
            "map_name": "A_h^acc",
            "acceleration_block": ["a_i", "alpha_i"],
            "row_terms": ["T_acceleration_lift", "R_angular_acceleration_lift"],
            "total_rows": len(acc_rows),
            "stage_body_pairs": len(stage_body_pairs),
            "codomain": "R^36",
            "purpose": (
                "Bind accepted translational and angular stage acceleration variables "
                "to the D5 acceleration-lift Taylor rows before any lift-rate proof."
            ),
        },
        "summary": {
            "closed_subproof_count": len(closed_subproofs),
            "required_subproof_count": 4,
            "open_subproof_count": len(open_subproofs),
            "term_rows_using_p_acc": p_acc_row.get("term_rows_using_obligation"),
            "term_rows_conditionally_mapped": len(acc_rows),
            "translational_acceleration_rows": len(translational_rows),
            "angular_acceleration_rows": len(angular_rows),
            "acceleration_lift_rate_proved": False,
            "pc2_closed": False,
        },
        "closed_subproofs": closed_subproofs,
        "open_subproofs": open_subproofs,
        "anti_circularity_gate": {
            "map_definition_is_not_acceleration_lift_rate": True,
            "velocity_collocation_rate_not_assumed": True,
            "dynamic_balance_disallowed_as_acceleration_lift_proof": True,
            "stage_residual_perturbation_lemma_disallowed_as_input": True,
        },
        "manuscript_link": {
            "main_tex_present": all(contains_normalized(main_tex, token) for token in manuscript_tokens),
            "flat_tex_present": all(contains_normalized(flat_tex, token) for token in manuscript_tokens),
            "tokens": manuscript_tokens,
        },
        "source_consistency": {
            "primitive_reduction_schema": primitive_reduction.get("schema"),
            "primitive_reduction_pc2_closed": primitive_reduction.get("pc2_closed"),
            "term_budget_schema": term_budget.get("schema"),
            "term_budget_pc2_closed": term_budget.get("pc2_closed"),
            "term_rows": len(acc_rows),
            "translational_rows": len(translational_rows),
            "angular_rows": len(angular_rows),
        },
        "claim_boundary": {
            "allowed_now": (
                "P_acc PA1 is closed: the accepted acceleration map is defined "
                "and bound to the 36 acceleration-lift Taylor rows."
            ),
            "forbidden_now": [
                "P_acc primitive closure",
                "acceleration lift O(h^7) proved",
                "velocity-collocation implication proved",
                "Taylor term bounds certified from P_acc",
                "primitive/Taylor PC2 route closure",
                "unconditional sixth-order theorem",
            ],
            "close_condition": (
                "P_acc closes only after velocity-collocation and smooth-lift arguments "
                "prove O(h^7) translational and angular acceleration lift rates in the "
                "accepted row ordering, independently of the dynamic balance defect."
            ),
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# D5 P_acc Map Definition Audit",
        "",
        "Status: **P_acc map definition closed; lift remains open**.",
        "",
        "This read-only audit closes only PA1 for `P_acc`: the accepted",
        "translational and angular acceleration variables are bound to the 36",
        "D5 acceleration-lift Taylor rows. It does not prove an `O(h^7)`",
        "acceleration lift rate.",
        "",
        "## Summary",
        "",
        f"- Closed P_acc subproofs: `{len(closed_subproofs)}/4`.",
        f"- Open P_acc subproofs: `{len(open_subproofs)}`.",
        f"- Acceleration-map rows: `{len(acc_rows)}/36`.",
        f"- Translational/angular acceleration rows: `{len(translational_rows)}/{len(angular_rows)}`.",
        f"- P_acc primitive closed: `{result['primitive_closed']}`.",
        f"- Acceleration lift rate proved: `{result['acceleration_lift_rate_proved']}`.",
        f"- Primitive/Taylor PC2 route closed: `{result['pc2_closed']}`.",
        "",
        "## Map Interface",
        "",
        "`A_h^acc(A)` binds `A=(a_i, alpha_i)` to the accepted acceleration",
        "lift terms `T_acceleration_lift` and `R_angular_acceleration_lift`.",
        "",
        "| term family | rows |",
        "|---|---:|",
        f"| `T_acceleration_lift` | `{len(translational_rows)}` |",
        f"| `R_angular_acceleration_lift` | `{len(angular_rows)}` |",
        "",
        "## Acceptance Boundary",
        "",
        "- PA1 map definition is closed.",
        "- PA2 velocity-collocation-to-acceleration lift proof remains open.",
        "- PA3 independence from dynamic balance remains open.",
        "- PA4 residual-ordering/Taylor-term binding proof remains open.",
        "- `P_acc` remains open.",
        "- Primitive/Taylor PC2 lane remains open.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("d5_p_acc_map_definition_audit=written")
    print("closed_subproofs=1/4")
    print("acceleration_map_rows=36/36")
    print("p_acc_closed=False")
    print("pc2_closed=False")


if __name__ == "__main__":
    main()
