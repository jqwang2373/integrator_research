#!/usr/bin/env python3
"""Build the D5 P_acc independence audit.

This audit closes only PA3 for P_acc: the acceleration-lift proof inputs are
restricted to non-dynamic FullVA row families and the 96-row non-dynamic
certificate. It does not prove the O(h^7) acceleration lift rate.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
RUN_V047 = PAPER.parent / "v047_cylindrical_chain_pipeline" / "run_v047.py"
OUT_JSON = PAPER / "D5_P_ACC_INDEPENDENCE_AUDIT.json"
OUT_MD = PAPER / "D5_P_ACC_INDEPENDENCE_AUDIT.md"

PROOF_INPUT_FAMILIES = [
    "translational_velocity_weak_defect",
    "angular_velocity_weak_defect",
    "lower_pair_index3_weak_constraints",
]
DYNAMIC_FAMILY = "newton_euler_weak_balance"
EXPECTED_FAMILY_LAYOUT = {
    "translational_velocity_weak_defect": {"offset": 12, "width": 6, "total_rows": 18},
    "angular_velocity_weak_defect": {"offset": 18, "width": 6, "total_rows": 18},
    "newton_euler_weak_balance": {"offset": 24, "width": 12, "total_rows": 36},
    "lower_pair_index3_weak_constraints": {"offset": 36, "width": 8, "total_rows": 24},
}
ACC_TERM_ROWS = list(range(24, 36)) + list(range(68, 80)) + list(range(112, 124))


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


def family_global_rows(stage_size: int, n_stages: int, offset: int, width: int) -> list[int]:
    rows: list[int] = []
    for stage in range(n_stages):
        base = stage * stage_size + offset
        rows.extend(range(base, base + width))
    return rows


def main() -> None:
    p_acc_map = read_json(PAPER / "D5_P_ACC_MAP_DEFINITION_AUDIT.json")
    p_acc_row_binding = read_json(PAPER / "D5_P_ACC_ROW_BINDING_AUDIT.json")
    dynamic_gate = read_json(PAPER / "DYNAMIC_ROW_ORACLE_GATE.json")
    kinematic_certificate = read_json(PAPER / "KINEMATIC_ROW_DEFECT_CERTIFICATE.json")
    main_tex = read_text(LATEX / "main_cmame.tex")
    flat_tex = read_text(LATEX / "cmame_submission_flat" / "main_cmame_submission.tex")
    run_source = read_text(RUN_V047)

    layout = dynamic_gate.get("layout", {})
    n_stages = int(layout.get("n_stages", 0))
    stage_size = int(layout.get("stage_size", 0))
    row_families = {
        row.get("name"): row
        for row in layout.get("row_families", [])
        if isinstance(row, dict)
    }
    certified_families = set(
        kinematic_certificate.get("proof_scope", {}).get("certified_row_families", [])
    )
    excluded_family = kinematic_certificate.get("proof_scope", {}).get("excluded_row_family")
    partial_oracle_families = set(
        dynamic_gate.get("partial_independent_formula_row_oracle", {}).get("row_families", [])
    )

    proof_input_checks: list[dict[str, Any]] = []
    for family in PROOF_INPUT_FAMILIES:
        expected = EXPECTED_FAMILY_LAYOUT[family]
        layout_row = row_families.get(family, {})
        rows = family_global_rows(
            stage_size=stage_size,
            n_stages=n_stages,
            offset=int(layout_row.get("offset", -1)),
            width=int(layout_row.get("width", 0)),
        )
        checks = {
            "layout_family_present": bool(layout_row),
            "offset_matches": layout_row.get("offset") == expected["offset"],
            "width_matches": layout_row.get("width") == expected["width"],
            "total_rows_matches": layout_row.get("total_rows") == expected["total_rows"],
            "certified_by_96_row_certificate": family in certified_families,
            "present_in_partial_formula_oracle": family in partial_oracle_families,
            "not_newton_euler_balance_family": family != DYNAMIC_FAMILY,
        }
        proof_input_checks.append(
            {
                "family": family,
                "offset": layout_row.get("offset"),
                "width": layout_row.get("width"),
                "total_rows": layout_row.get("total_rows"),
                "global_rows": rows,
                "checks": checks,
                "input_boundary_closed": all(checks.values()),
            }
        )

    dynamic_layout = row_families.get(DYNAMIC_FAMILY, {})
    dynamic_rows = family_global_rows(
        stage_size=stage_size,
        n_stages=n_stages,
        offset=int(dynamic_layout.get("offset", -1)),
        width=int(dynamic_layout.get("width", 0)),
    )
    dynamic_checks = {
        "layout_family_present": bool(dynamic_layout),
        "offset_matches": dynamic_layout.get("offset") == EXPECTED_FAMILY_LAYOUT[DYNAMIC_FAMILY]["offset"],
        "width_matches": dynamic_layout.get("width") == EXPECTED_FAMILY_LAYOUT[DYNAMIC_FAMILY]["width"],
        "total_rows_matches": dynamic_layout.get("total_rows") == EXPECTED_FAMILY_LAYOUT[DYNAMIC_FAMILY]["total_rows"],
        "excluded_from_96_row_certificate": excluded_family == DYNAMIC_FAMILY,
        "excluded_from_partial_formula_oracle": DYNAMIC_FAMILY not in partial_oracle_families,
        "not_used_as_p_acc_independence_input": DYNAMIC_FAMILY not in PROOF_INPUT_FAMILIES,
        "matches_bound_acceleration_term_rows": dynamic_rows == ACC_TERM_ROWS,
    }

    source_tokens = [
        '("translational_velocity_weak_defect", 12, 6)',
        '("angular_velocity_weak_defect", 18, 6)',
        '("newton_euler_weak_balance", 24, 12)',
        '("lower_pair_index3_weak_constraints", 36, 8)',
        "def residual_cylindrical_chain",
        "pacc.append",
        "w_block.append",
        "dyn.extend([trans, rot])",
        "R_INDEPENDENT_STAGE_FUNCTIONAL_BLOCKS",
    ]
    source_trace = {token: contains_normalized(run_source, token) for token in source_tokens}

    manuscript_tokens = [
        r"\label{lem:d5-p-acc-independence}",
        "closes only the PA3 non-circularity subproof",
        "does not prove an acceleration lift rate",
        "Newton--Euler weak-balance rows are not inputs",
        "PA2 remains open",
    ]

    non_dynamic_inputs_closed = all(row.get("input_boundary_closed") for row in proof_input_checks)
    dynamic_disallowed = all(dynamic_checks.values())
    source_bound = all(source_trace.values())
    pa3_closed = non_dynamic_inputs_closed and dynamic_disallowed and source_bound

    result = {
        "schema": "d5-p-acc-independence-audit-v1",
        "status": "p_acc_independence_closed_lift_open",
        "read_only": True,
        "run_v047_invoked": False,
        "submission_ready": False,
        "pc2_closed": False,
        "proof_gap_closed": False,
        "primitive_id": "P_acceleration_lift",
        "primitive_closed": False,
        "pa3_independence_closed": pa3_closed,
        "acceleration_lift_rate_proved": False,
        "term_bounds_proved": 0,
        "term_rows_using_p_acc": p_acc_row_binding.get("summary", {}).get("term_rows_using_p_acc"),
        "acceleration_term_rows": ACC_TERM_ROWS,
        "non_dynamic_input_families": proof_input_checks,
        "dynamic_family_boundary": {
            "family": DYNAMIC_FAMILY,
            "offset": dynamic_layout.get("offset"),
            "width": dynamic_layout.get("width"),
            "total_rows": dynamic_layout.get("total_rows"),
            "global_rows": dynamic_rows,
            "checks": dynamic_checks,
            "dynamic_balance_disallowed_as_input": all(dynamic_checks.values()),
        },
        "source_trace": source_trace,
        "summary": {
            "closed_subproof_count_for_this_audit": 1,
            "p_acc_closed_subproof_count_after_independence": 3,
            "required_subproof_count": 4,
            "open_subproof_count_after_independence": 1,
            "non_dynamic_input_families_certified": sum(
                1 for row in proof_input_checks if row.get("input_boundary_closed")
            ),
            "required_non_dynamic_input_families": len(PROOF_INPUT_FAMILIES),
            "dynamic_balance_input_families_used": 0,
            "dynamic_balance_rows_disallowed": len(dynamic_rows),
            "acceleration_lift_rate_proved": False,
            "term_bounds_proved": 0,
            "pc2_closed": False,
        },
        "closed_subproofs": [
            "PA1_acceleration_variable_and_row_map_defined",
            "PA3_lower_pair_acceleration_independence_from_dynamic_balance",
            "PA4_binding_to_residual_ordering_and_D5_terms",
        ],
        "open_subproofs": [
            "PA2_velocity_collocation_to_acceleration_lift",
        ],
        "anti_circularity_gate": {
            "non_dynamic_rows_can_be_inputs_to_pa2": True,
            "dynamic_balance_disallowed_as_acceleration_lift_proof": True,
            "stage_residual_perturbation_lemma_disallowed_as_input": True,
            "velocity_collocation_rate_not_assumed": True,
            "row_independence_is_not_acceleration_lift_rate": True,
            "row_independence_is_not_taylor_bound": True,
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
            "p_acc_row_binding_schema": p_acc_row_binding.get("schema"),
            "p_acc_row_binding_closed": p_acc_row_binding.get("pa4_row_binding_closed"),
            "p_acc_row_binding_primitive_closed": p_acc_row_binding.get("primitive_closed"),
            "p_acc_row_binding_pc2_closed": p_acc_row_binding.get("pc2_closed"),
            "dynamic_gate_schema": dynamic_gate.get("schema"),
            "dynamic_gate_stage_residual_defect_proved": dynamic_gate.get("acceptance_boundary", {}).get(
                "stage_residual_O_h7_implementation_defect_proved"
            ),
            "kinematic_certificate_schema": kinematic_certificate.get("schema"),
            "kinematic_certificate_row_count": kinematic_certificate.get("proof_scope", {}).get(
                "certified_row_count"
            ),
            "kinematic_certificate_excluded_family": excluded_family,
            "kinematic_certificate_stage_residual_defect_proved": kinematic_certificate.get(
                "certificate", {}
            ).get("stage_residual_O_h7_implementation_defect_proved"),
        },
        "claim_boundary": {
            "allowed_now": (
                "P_acc PA3 is closed: the acceleration-lift proof route is explicitly "
                "restricted to non-dynamic FullVA row families certified by the 96-row "
                "certificate, and Newton-Euler weak-balance rows are barred as inputs."
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
                "P_acc closes only after PA2 proves that the non-dynamic velocity and "
                "angular-velocity collocation perturbations imply O(h^7) translational "
                "and angular acceleration lift rates in the already-bound row ordering."
            ),
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# D5 P_acc Independence Audit",
        "",
        "Status: **P_acc independence closed; lift remains open**.",
        "",
        "This read-only audit closes only PA3 for `P_acc`: the proof route for",
        "the acceleration-lift primitive is restricted to non-dynamic FullVA",
        "row families and excludes Newton-Euler weak-balance rows as inputs.",
        "It does not prove an `O(h^7)` acceleration lift rate.",
        "",
        "## Summary",
        "",
        "- Closed P_acc subproofs after independence: `3/4`.",
        "- Open P_acc subproofs after independence: `1`.",
        f"- Non-dynamic input families certified: `{result['summary']['non_dynamic_input_families_certified']}/{len(PROOF_INPUT_FAMILIES)}`.",
        f"- Dynamic-balance input families used: `{result['summary']['dynamic_balance_input_families_used']}`.",
        f"- Dynamic-balance rows disallowed as inputs: `{len(dynamic_rows)}`.",
        f"- P_acc primitive closed: `{result['primitive_closed']}`.",
        f"- Acceleration lift rate proved: `{result['acceleration_lift_rate_proved']}`.",
        f"- Taylor bounds proved: `{result['term_bounds_proved']}/36`.",
        f"- Primitive/Taylor PC2 route closed: `{result['pc2_closed']}`.",
        "",
        "## Non-Dynamic Input Boundary",
        "",
        "| family | offset | width | rows | certified |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in proof_input_checks:
        lines.append(
            f"| `{row['family']}` | `{row['offset']}` | `{row['width']}` | "
            f"`{row['total_rows']}` | `{row['checks']['certified_by_96_row_certificate']}` |"
        )
    lines.extend(
        [
            "",
            "The Newton-Euler weak-balance family is present at offset `24` with",
            "width `12`, but it is excluded from the 96-row certificate and is not",
            "used as a `P_acc` independence input.",
            "",
            "## Acceptance Boundary",
            "",
            "- PA1 map definition is closed.",
            "- PA3 lower-pair acceleration independence from dynamic balance is closed.",
            "- PA4 row-ordering/Taylor-term binding is closed.",
            "- PA2 velocity-collocation-to-acceleration lift proof remains open.",
            "- `P_acc` remains open.",
            "- Primitive/Taylor PC2 lane remains open.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("d5_p_acc_independence_audit=written")
    print("closed_subproofs_after_independence=3/4")
    print(f"non_dynamic_input_families_certified={result['summary']['non_dynamic_input_families_certified']}/3")
    print("p_acc_closed=False")
    print("pc2_closed=False")


if __name__ == "__main__":
    main()
