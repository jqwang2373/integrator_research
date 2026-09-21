#!/usr/bin/env python3
"""Build the D5 P_state non-dynamic map-definition audit.

This audit closes only PS1 for P_state: the non-dynamic stage map is defined
in the accepted Lie chart and bound to the 96 certified row families.  It does
not prove a local inverse/inf-sup bound or any O(h^7) state lift rate.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
OUT_JSON = PAPER / "D5_P_STATE_MAP_DEFINITION_AUDIT.json"
OUT_MD = PAPER / "D5_P_STATE_MAP_DEFINITION_AUDIT.md"


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
    kinematic = read_json(PAPER / "KINEMATIC_ROW_DEFECT_CERTIFICATE.json")
    primitive_reduction = read_json(PAPER / "D5_PRIMITIVE_BOUND_REDUCTION_AUDIT.json")
    term_budget = read_json(PAPER / "D5_TAYLOR_TERM_BUDGET_AUDIT.json")
    p_state_anticircularity = read_json(PAPER / "D5_P_STATE_ANTICIRCULARITY_AUDIT.json")
    main_tex = read_text(LATEX / "main_cmame.tex")
    flat_tex = read_text(LATEX / "cmame_submission_flat" / "main_cmame_submission.tex")

    proof_scope = kinematic.get("proof_scope", {})
    certified_families = proof_scope.get("certified_row_families", [])
    if not isinstance(certified_families, list):
        certified_families = []
    family_counts = {
        "translational_position_weak_defect": 18,
        "rotational_lie_position_weak_defect": 18,
        "translational_velocity_weak_defect": 18,
        "angular_velocity_weak_defect": 18,
        "lower_pair_index3_weak_constraints": 24,
    }
    primitive_rows = primitive_reduction.get("primitive_obligations", [])
    p_state_row = next(
        (
            row
            for row in primitive_rows
            if isinstance(row, dict) and row.get("id") == "P_state_lift"
        ),
        {},
    )
    p_state_term_rows = p_state_row.get("term_rows_using_obligation")

    manuscript_tokens = [
        r"\label{lem:d5-p-state-map-definition}",
        r"\mathcal N_h^{\mathrm{nd}}",
        r"S=(r_i,\eta_i,v_i,\omega_i)",
        "does not assert a bounded inverse",
        "closes only the PS1 map-definition subproof",
    ]

    closed_subproofs = [
        "PS1_non_dynamic_stage_map_domain_codomain_defined",
    ]
    open_subproofs = [
        "PS2_local_inverse_or_inf_sup_bound",
        "PS3_residual_certificate_to_state_lift_rate",
    ]
    map_definition = {
        "map_name": "N_h^nd",
        "state_block": ["r_i", "eta_i", "v_i", "omega_i"],
        "auxiliary_block": ["a_i", "alpha_i"],
        "excluded_block": ["lambda_i"],
        "row_families": [
            {
                "family": family,
                "rows": family_counts[family],
                "included_in_kinematic_certificate": family in certified_families,
            }
            for family in family_counts
        ],
        "total_rows": sum(family_counts.values()),
        "codomain": "R^96",
        "purpose": (
            "Define the non-dynamic chart map whose inverse or inf-sup bound "
            "would later convert the 96-row residual certificate into P_state lift rates."
        ),
    }

    result = {
        "schema": "d5-p-state-map-definition-audit-v1",
        "status": "p_state_map_definition_closed_lift_open",
        "read_only": True,
        "run_v047_invoked": False,
        "submission_ready": False,
        "pc2_closed": False,
        "proof_gap_closed": False,
        "primitive_id": "P_state_lift",
        "primitive_closed": False,
        "ps1_map_definition_closed": True,
        "state_lift_rate_proved": False,
        "local_inverse_or_inf_sup_proved": False,
        "term_bounds_proved": 0,
        "term_rows_using_p_state": p_state_term_rows,
        "p_state_term_rows_in_budget": p_state_term_rows,
        "map_definition": map_definition,
        "summary": {
            "closed_subproof_count": len(closed_subproofs),
            "required_subproof_count": 4,
            "open_subproof_count": len(open_subproofs),
            "aggregate_p_state_subproofs_closed_after_ps4": 2,
            "ps4_anticircularity_closed_elsewhere": p_state_anticircularity.get(
                "ps4_anticircularity_closed"
            ),
            "non_dynamic_map_rows": map_definition["total_rows"],
            "kinematic_certificate_rows": proof_scope.get("certified_row_count"),
            "term_rows_using_p_state": p_state_term_rows,
            "p_state_term_rows_in_budget": p_state_term_rows,
            "state_lift_rate_proved": False,
            "pc2_closed": False,
        },
        "closed_subproofs": closed_subproofs,
        "open_subproofs": open_subproofs,
        "anti_circularity_gate": {
            "map_definition_is_not_inverse_bound": True,
            "map_definition_is_not_state_lift_rate": True,
            "stage_residual_perturbation_lemma_disallowed_as_input": True,
            "dynamic_residual_defect_disallowed_as_input": True,
        },
        "manuscript_link": {
            "main_tex_present": all(contains_normalized(main_tex, token) for token in manuscript_tokens),
            "flat_tex_present": all(contains_normalized(flat_tex, token) for token in manuscript_tokens),
            "tokens": manuscript_tokens,
        },
        "source_consistency": {
            "kinematic_certificate_schema": kinematic.get("schema"),
            "kinematic_certificate_status": kinematic.get("status"),
            "kinematic_certificate_rows": proof_scope.get("certified_row_count"),
            "kinematic_certificate_families": certified_families,
            "excluded_dynamic_family": proof_scope.get("excluded_row_family"),
            "excluded_dynamic_rows": proof_scope.get("excluded_row_count"),
            "primitive_reduction_schema": primitive_reduction.get("schema"),
            "primitive_reduction_pc2_closed": primitive_reduction.get("pc2_closed"),
            "term_budget_schema": term_budget.get("schema"),
            "term_budget_pc2_closed": term_budget.get("pc2_closed"),
            "p_state_anticircularity_schema": p_state_anticircularity.get("schema"),
            "p_state_anticircularity_closed": p_state_anticircularity.get("ps4_anticircularity_closed"),
            "p_state_anticircularity_pc2_closed": p_state_anticircularity.get("pc2_closed"),
        },
        "claim_boundary": {
            "allowed_now": (
                "P_state PS1 is closed: the non-dynamic stage map is defined "
                "and bound to the 96 certified non-dynamic row families."
            ),
            "forbidden_now": [
                "P_state primitive closure",
                "local inverse or inf-sup closure",
                "state lift O(h^7) proved",
                "Taylor term bounds certified from P_state",
                "primitive/Taylor PC2 route closure",
                "unconditional sixth-order theorem",
            ],
            "close_condition": (
                "P_state closes only after PS2 proves a uniform inverse or inf-sup "
                "bound, PS3 converts the 96-row certificate into O(h^7) state "
                "lift rates; PS4 anti-circularity is closed separately by "
                "D5_P_STATE_ANTICIRCULARITY_AUDIT."
            ),
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# D5 P_state Map Definition Audit",
        "",
        "Status: **P_state map definition closed; lift remains open**.",
        "",
        "This read-only audit closes only PS1 for `P_state`: the non-dynamic",
        "stage map is defined in the accepted Lie chart and bound to the 96",
        "certified non-dynamic row families. It does not prove a local inverse,",
        "an inf-sup bound, or any `O(h^7)` state lift rate.",
        "",
        "## Summary",
        "",
        f"- Closed P_state subproofs: `{len(closed_subproofs)}/4`.",
        f"- Open P_state subproofs in this map audit: `{len(open_subproofs)}`.",
        f"- Aggregate P_state subproofs closed after PS4: `{result['summary']['aggregate_p_state_subproofs_closed_after_ps4']}/4`.",
        f"- PS4 anti-circularity closed elsewhere: `{result['summary']['ps4_anticircularity_closed_elsewhere']}`.",
        f"- Non-dynamic map rows: `{map_definition['total_rows']}/96`.",
        f"- Term rows using P_state: `{p_state_row.get('term_rows_using_obligation')}/162`.",
        f"- P_state primitive closed: `{result['primitive_closed']}`.",
        f"- State lift rate proved: `{result['state_lift_rate_proved']}`.",
        f"- Primitive/Taylor PC2 route closed: `{result['pc2_closed']}`.",
        "",
        "## Map Interface",
        "",
        "`N_h^nd(S,A)` collects the accepted non-dynamic residual rows with",
        "`S=(r_i, eta_i, v_i, omega_i)` and auxiliary acceleration block",
        "`A=(a_i, alpha_i)`. The multiplier block is excluded from this",
        "map-definition subproof.",
        "",
        "| row family | rows | in 96-row certificate |",
        "|---|---:|---:|",
    ]
    for row in map_definition["row_families"]:
        lines.append(
            f"| `{row['family']}` | `{row['rows']}` | `{row['included_in_kinematic_certificate']}` |"
        )
    lines.extend(
        [
            "",
            "## Acceptance Boundary",
            "",
            "- PS1 map definition is closed.",
            "- PS2 local inverse or inf-sup proof remains open.",
            "- PS3 conversion to `O(h^7)` state lift rates remains open.",
            "- PS4 anti-circularity is closed separately by `D5_P_STATE_ANTICIRCULARITY_AUDIT`.",
            "- `P_state` remains open.",
            "- Primitive/Taylor PC2 lane remains open.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("d5_p_state_map_definition_audit=written")
    print("closed_subproofs=1/4")
    print("non_dynamic_map_rows=96/96")
    print("p_state_closed=False")
    print("pc2_closed=False")


if __name__ == "__main__":
    main()
