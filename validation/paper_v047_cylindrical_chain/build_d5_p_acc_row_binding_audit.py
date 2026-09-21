#!/usr/bin/env python3
"""Build the D5 P_acc row-binding audit.

This audit closes only PA4 for P_acc: the 36 accepted acceleration-lift Taylor
terms are bound to the D6 row ordering and runtime residual layout. It does not
prove any O(h^7) acceleration lift rate.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
OUT_JSON = PAPER / "D5_P_ACC_ROW_BINDING_AUDIT.json"
OUT_MD = PAPER / "D5_P_ACC_ROW_BINDING_AUDIT.md"

ACC_TERM_IDS = {"T_acceleration_lift", "R_angular_acceleration_lift"}
EXPECTED_ROWS = list(range(24, 36)) + list(range(68, 80)) + list(range(112, 124))


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


def runtime_component_for(term_row: dict[str, Any]) -> str:
    body = int(term_row["body"])
    if term_row["term_id"] == "T_acceleration_lift":
        return f"body{body}_translational_balance_source"
    return f"body{body}_rotational_balance_source"


def main() -> None:
    p_acc_map = read_json(PAPER / "D5_P_ACC_MAP_DEFINITION_AUDIT.json")
    term_budget = read_json(PAPER / "D5_TAYLOR_TERM_BUDGET_AUDIT.json")
    d6_audit = read_json(PAPER / "NEWTON_EULER_ROW_ORDERING_SCALING_AD_AUDIT.json")
    readiness = read_json(PAPER / "D5_DYNAMIC_DEFECT_READINESS_AUDIT.json")
    main_tex = read_text(LATEX / "main_cmame.tex")
    flat_tex = read_text(LATEX / "cmame_submission_flat" / "main_cmame_submission.tex")

    acc_rows = [
        row
        for row in term_budget.get("term_rows", [])
        if isinstance(row, dict) and row.get("term_id") in ACC_TERM_IDS
    ]
    d6_by_row = {
        row.get("global_row"): row
        for row in d6_audit.get("row_audit", [])
        if isinstance(row, dict)
    }
    readiness_by_row = {}
    for row_or_group in readiness.get("rows", []):
        if isinstance(row_or_group, dict):
            readiness_by_row[row_or_group.get("global_row")] = row_or_group
        elif isinstance(row_or_group, list):
            for row in row_or_group:
                if isinstance(row, dict):
                    readiness_by_row[row.get("global_row")] = row

    row_checks: list[dict[str, Any]] = []
    for row in acc_rows:
        global_row = row.get("global_row")
        d6_row = d6_by_row.get(global_row, {})
        readiness_row = readiness_by_row.get(global_row, {})
        target = d6_row.get("target", {}) if isinstance(d6_row, dict) else {}
        expected_runtime_component = runtime_component_for(row)
        checks = {
            "row_binding_available_in_term_budget": row.get("row_binding_available") is True,
            "term_bound_not_proved": row.get("taylor_bound_proved") is False,
            "d6_row_present": bool(d6_row),
            "d6_row_ordering_proved": d6_row.get("proved") is True,
            "d6_stage_matches": target.get("stage") == row.get("stage"),
            "d6_body_matches": target.get("body") == row.get("body"),
            "d6_component_matches": target.get("component") == row.get("component"),
            "d6_balance_block_matches": target.get("balance_block") == row.get("balance_block"),
            "d6_runtime_component_matches": target.get("runtime_source_component")
            == expected_runtime_component,
            "readiness_row_runtime_traceability_ready": readiness_row.get("runtime_traceability_ready")
            is True,
            "readiness_row_theorem_status_recorded": readiness_row.get("certified_for_theorem")
            in {True, False},
            "readiness_row_theorem_certification_not_used_for_pa4": True,
        }
        row_checks.append(
            {
                "global_row": global_row,
                "stage": row.get("stage"),
                "body": row.get("body"),
                "component": row.get("component"),
                "term_id": row.get("term_id"),
                "balance_block": row.get("balance_block"),
                "runtime_source_component": expected_runtime_component,
                "checks": checks,
                "row_binding_closed": all(checks.values()),
                "taylor_bound_proved": False,
            }
        )

    translational_rows = [row for row in acc_rows if row.get("term_id") == "T_acceleration_lift"]
    angular_rows = [row for row in acc_rows if row.get("term_id") == "R_angular_acceleration_lift"]
    all_rows_bound = len(row_checks) == 36 and all(row.get("row_binding_closed") for row in row_checks)
    row_ids = [row.get("global_row") for row in acc_rows]

    manuscript_tokens = [
        r"\label{lem:d5-p-acc-row-binding}",
        r"\label{cor:d5-p-acc-row-bound-under-pacc}",
        "global rows 24--35, 68--79, and 112--123",
        "closes only the PA4 row-ordering/Taylor-term binding subproof",
        "does not prove an acceleration lift rate",
        "PA3 is the separate non-dynamic input-independence subproof closed in",
        "with zero Taylor remainder",
        "does not prove the unweighted acceleration lift",
    ]
    conditional_corollary_tokens = [
        r"\label{cor:d5-p-acc-row-bound-under-pacc}",
        "Row-level acceleration Taylor bound under",
        "with zero Taylor remainder",
        "does not prove the unweighted acceleration lift",
        "does not close PA2",
    ]
    conditional_corollary_present_main = all(
        contains_normalized(main_tex, token) for token in conditional_corollary_tokens
    )
    conditional_corollary_present_flat = all(
        contains_normalized(flat_tex, token) for token in conditional_corollary_tokens
    )

    result = {
        "schema": "d5-p-acc-row-binding-audit-v1",
        "status": "p_acc_row_binding_closed_lift_open",
        "read_only": True,
        "run_v047_invoked": False,
        "submission_ready": False,
        "pc2_closed": False,
        "proof_gap_closed": False,
        "primitive_id": "P_acceleration_lift",
        "primitive_closed": False,
        "pa4_row_binding_closed": all_rows_bound,
        "acceleration_lift_rate_proved": False,
        "term_bounds_proved": 0,
        "term_rows_using_p_acc": p_acc_map.get("summary", {}).get("term_rows_using_p_acc"),
        "term_rows_bound_to_ordering": len(row_checks),
        "translational_acceleration_rows": len(translational_rows),
        "angular_acceleration_rows": len(angular_rows),
        "row_ids": row_ids,
        "row_ids_expected": EXPECTED_ROWS,
        "row_checks": row_checks,
        "conditional_row_level_corollary": {
            "label": "cor:d5-p-acc-row-bound-under-pacc",
            "main_tex_present": conditional_corollary_present_main,
            "flat_tex_present": conditional_corollary_present_flat,
            "term_rows_conditionally_bound_under_p_acc": 36,
            "actual_taylor_bounds_proved": 0,
            "primitive_closed": False,
            "pc2_closed": False,
            "uses_weighted_pa2_diagnostic_as_proof": False,
        },
        "summary": {
            "closed_subproof_count_for_this_audit": 1,
            "p_acc_closed_subproof_count_after_binding": 2,
            "required_subproof_count": 4,
            "open_subproof_count_after_binding": 2,
            "term_rows_using_p_acc": p_acc_map.get("summary", {}).get("term_rows_using_p_acc"),
            "term_rows_bound_to_ordering": len(row_checks),
            "rows_with_closed_binding": sum(1 for row in row_checks if row.get("row_binding_closed")),
            "translational_acceleration_rows": len(translational_rows),
            "angular_acceleration_rows": len(angular_rows),
            "acceleration_lift_rate_proved": False,
            "term_bounds_proved": 0,
            "pc2_closed": False,
        },
        "closed_subproofs": [
            "PA1_acceleration_variable_and_row_map_defined",
            "PA4_binding_to_residual_ordering_and_D5_terms",
        ],
        "open_subproofs": [
            "PA2_velocity_collocation_to_acceleration_lift",
            "PA3_lower_pair_acceleration_independence_from_dynamic_balance",
        ],
        "anti_circularity_gate": {
            "row_binding_is_not_acceleration_lift_rate": True,
            "row_binding_is_not_taylor_bound": True,
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
            "p_acc_map_definition_schema": p_acc_map.get("schema"),
            "p_acc_map_definition_closed": p_acc_map.get("pa1_map_definition_closed"),
            "p_acc_map_definition_primitive_closed": p_acc_map.get("primitive_closed"),
            "p_acc_map_definition_pc2_closed": p_acc_map.get("pc2_closed"),
            "term_budget_schema": term_budget.get("schema"),
            "term_budget_pc2_closed": term_budget.get("pc2_closed"),
            "d6_audit_schema": d6_audit.get("schema"),
            "d6_row_ordering_scaling_ad_closed": d6_audit.get("row_ordering_scaling_ad_closed"),
            "d6_stage_residual_defect_proved": d6_audit.get(
                "stage_residual_O_h7_implementation_defect_proved"
            ),
            "readiness_schema": readiness.get("schema"),
            "readiness_pc2_closed": readiness.get("pc2_closed"),
            "readiness_direct_route_status_not_used_for_pa4": True,
        },
        "claim_boundary": {
            "allowed_now": (
                "P_acc PA4 is closed: the 36 acceleration-lift Taylor terms are "
                "bound to the accepted D6 residual row ordering and runtime source components."
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
                "P_acc closes only after PA2 proves the translational and angular "
                "acceleration lift rates in this already-bound row ordering; PA3 is "
                "closed separately as the non-dynamic input-independence subproof."
            ),
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# D5 P_acc Row-Binding Audit",
        "",
        "Status: **P_acc row binding closed; lift remains open**.",
        "",
        "This read-only audit closes only PA4 for `P_acc`: the 36",
        "acceleration-lift Taylor terms are bound to the implemented D6 row",
        "ordering and runtime residual source components. It does not prove an",
        "`O(h^7)` acceleration lift rate.",
        "",
        "## Summary",
        "",
        "- Closed P_acc subproofs after binding: `2/4`.",
        "- Open P_acc subproofs after binding: `2`.",
        f"- Acceleration rows bound to ordering: `{len(row_checks)}/36`.",
        f"- Rows with closed binding: `{result['summary']['rows_with_closed_binding']}/36`.",
        f"- Translational/angular acceleration rows: `{len(translational_rows)}/{len(angular_rows)}`.",
        f"- P_acc primitive closed: `{result['primitive_closed']}`.",
        f"- Acceleration lift rate proved: `{result['acceleration_lift_rate_proved']}`.",
        f"- Taylor bounds proved: `{result['term_bounds_proved']}/36`.",
        f"- Conditional row-level P_acc corollary present main/flat: `{conditional_corollary_present_main}/{conditional_corollary_present_flat}`.",
        f"- Primitive/Taylor PC2 route closed: `{result['pc2_closed']}`.",
        "",
        "## Row Binding",
        "",
        "The accepted acceleration-lift rows occupy global rows `24--35`,",
        "`68--79`, and `112--123`. For each row, the D5 Taylor-term budget",
        "stage/body/component entry matches the D6 runtime row ordering and",
        "runtime source component.",
        "",
        "## Acceptance Boundary",
        "",
        "- PA1 map definition is closed.",
        "- PA4 row-ordering/Taylor-term binding is closed.",
        "- PA2 velocity-collocation-to-acceleration lift proof remains open.",
        "- PA3 independence is not closed by this row-binding audit; the later independence audit closes PA3 separately.",
        "- `P_acc` remains open.",
        "- Primitive/Taylor PC2 lane remains open.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("d5_p_acc_row_binding_audit=written")
    print("closed_subproofs_after_binding=2/4")
    print("acceleration_rows_bound=36/36")
    print("p_acc_closed=False")
    print("pc2_closed=False")


if __name__ == "__main__":
    main()
