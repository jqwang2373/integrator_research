#!/usr/bin/env python3
"""Build a primitive-bound reduction audit for the open D5 Taylor terms."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "D5_PRIMITIVE_BOUND_REDUCTION_AUDIT.json"
OUT_MD = PAPER / "D5_PRIMITIVE_BOUND_REDUCTION_AUDIT.md"


PRIMITIVE_OBLIGATIONS = {
    "P_state_lift": {
        "statement": "stage pose, translational velocity, and angular velocity lift errors are O(h^7)",
        "proved": False,
    },
    "P_acceleration_lift": {
        "statement": "stage translational and angular acceleration lift errors are O(h^7)",
        "proved": False,
    },
    "P_multiplier_lift": {
        "statement": "stage lower-pair multiplier lift errors are O(h^7)",
        "proved": False,
    },
    "P_geometry_lift": {
        "statement": "dynamic-row force and torque Jacobian lift errors are O(h^7)",
        "proved": False,
    },
    "P_gyroscopic_lift": {
        "statement": "body-frame gyroscopic bilinear lift errors are O(h^7)",
        "proved": False,
    },
    "P_uniform_tube_constants": {
        "statement": "all reduction constants are uniform on the compact smooth proof tube",
        "proved": True,
        "proof_source": "Lemma~\\ref{lem:d5-compact-tube-constants}",
    },
}


TERM_TO_PRIMITIVES = {
    "T_acceleration_lift": ["P_acceleration_lift", "P_uniform_tube_constants"],
    "T_external_force_lift": ["P_state_lift", "P_uniform_tube_constants"],
    "T_multiplier_force_lift": [
        "P_state_lift",
        "P_multiplier_lift",
        "P_geometry_lift",
        "P_uniform_tube_constants",
    ],
    "T_friction_force_lift": ["P_state_lift", "P_multiplier_lift", "P_uniform_tube_constants"],
    "R_angular_acceleration_lift": ["P_acceleration_lift", "P_uniform_tube_constants"],
    "R_gyroscopic_lift": ["P_state_lift", "P_gyroscopic_lift", "P_uniform_tube_constants"],
    "R_external_torque_lift": ["P_state_lift", "P_uniform_tube_constants"],
    "R_multiplier_torque_lift": [
        "P_state_lift",
        "P_multiplier_lift",
        "P_geometry_lift",
        "P_uniform_tube_constants",
    ],
    "R_friction_torque_lift": ["P_state_lift", "P_multiplier_lift", "P_uniform_tube_constants"],
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


def reduction_group(term_id: str) -> str:
    if term_id in {"T_acceleration_lift", "R_angular_acceleration_lift"}:
        return "acceleration_lift"
    if term_id in {
        "T_external_force_lift",
        "T_friction_force_lift",
        "R_external_torque_lift",
        "R_friction_torque_lift",
    }:
        return "smooth_force_torque_lift"
    if term_id in {"T_multiplier_force_lift", "R_multiplier_torque_lift"}:
        return "multiplier_geometry_lift"
    if term_id == "R_gyroscopic_lift":
        return "gyroscopic_bilinear_lift"
    raise ValueError(f"unknown D5 term id: {term_id}")


def build_reduction_rows(term_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in term_rows:
        term_id = row.get("term_id")
        if not isinstance(term_id, str):
            raise ValueError("term row missing term_id")
        primitives = TERM_TO_PRIMITIVES[term_id]
        rows.append(
            {
                "global_row": row.get("global_row"),
                "stage": row.get("stage"),
                "body": row.get("body"),
                "component": row.get("component"),
                "term_id": term_id,
                "balance_block": row.get("balance_block"),
                "reduction_group": reduction_group(term_id),
                "primitive_obligations": primitives,
                "reduction_rule_recorded": True,
                "primitive_bounds_proved": all(
                    PRIMITIVE_OBLIGATIONS[primitive]["proved"] is True for primitive in primitives
                ),
                "term_bound_proved": False,
                "certifies_theorem_now": False,
            }
        )
    return rows


def main() -> None:
    term_budget = read_json(PAPER / "D5_TAYLOR_TERM_BUDGET_AUDIT.json")
    readiness = read_json(PAPER / "D5_DYNAMIC_DEFECT_READINESS_AUDIT.json")
    proof_manifest = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
    main_tex = read_text(PAPER / "main_cmame.tex")
    flat_tex = read_text(PAPER / "cmame_submission_flat" / "main_cmame_submission.tex")

    term_rows = term_budget.get("term_rows", [])
    if not isinstance(term_rows, list):
        raise ValueError("D5 term-budget term_rows must be a list")
    reduction_rows = build_reduction_rows(term_rows)
    group_counts: dict[str, int] = {}
    primitive_counts = {key: 0 for key in PRIMITIVE_OBLIGATIONS}
    for row in reduction_rows:
        group = row["reduction_group"]
        group_counts[group] = group_counts.get(group, 0) + 1
        for primitive in row["primitive_obligations"]:
            primitive_counts[primitive] += 1

    primitive_proved = sum(1 for row in PRIMITIVE_OBLIGATIONS.values() if row["proved"] is True)
    manuscript_tokens = [
        r"\label{cor:d5-smooth-force-row-bound-under-lifts}",
        "primitive-bound reduction",
        "six primitive obligations",
        "compact-tube constants primitive is discharged below",
        "Row-level smooth force/torque/friction Taylor bound under",
        r"Thus the \(72\) smooth force, torque, and regularized-friction Taylor",
        "does not turn the D4 direct-route smoothness certificate into a primitive-rate proof",
        "no induced Taylor bounds are certified on the primitive/Taylor route",
    ]
    smooth_force_corollary_tokens = [
        r"\label{cor:d5-smooth-force-row-bound-under-lifts}",
        "Row-level smooth force/torque/friction Taylor bound under",
        r"Thus the \(72\) smooth force, torque, and regularized-friction Taylor",
        "does not prove either lift",
        "does not turn the D4 direct-route smoothness certificate into a primitive-rate proof",
        "does not use Lemma~\\ref{lem:stage-residual-defect}, direct substitution, or",
    ]
    smooth_force_corollary_present_main = all(
        contains_normalized(main_tex, token) for token in smooth_force_corollary_tokens
    )
    smooth_force_corollary_present_flat = all(
        contains_normalized(flat_tex, token) for token in smooth_force_corollary_tokens
    )

    result = {
        "schema": "d5-primitive-bound-reduction-audit-v1",
        "status": "primitive_reduction_recorded_pc2_open",
        "read_only": True,
        "run_v047_invoked": False,
        "submission_ready": False,
        "pc2_closed": False,
        "pc2_closed_scope": "false only for the separate primitive/Taylor PC2 route; active direct PC2 residual-bridge slot is closed separately",
        "primitive_route_pc2_closed": False,
        "proof_gap_closed": False,
        "proof_gap_closed_scope": "false only for the separate primitive/Taylor proof gap; active direct PC2 residual-bridge proof-gap slot is closed separately",
        "primitive_route_proof_gap_closed": False,
        "term_bound_closure_claimed": False,
        "summary": {
            "term_rows": len(reduction_rows),
            "term_rows_with_reduction_rule": sum(
                1 for row in reduction_rows if row.get("reduction_rule_recorded") is True
            ),
            "primitive_obligation_count": len(PRIMITIVE_OBLIGATIONS),
            "primitive_obligations_proved": primitive_proved,
            "term_bounds_proved": sum(1 for row in reduction_rows if row.get("term_bound_proved") is True),
            "open_primitive_obligations": len(PRIMITIVE_OBLIGATIONS) - primitive_proved,
            "p_tube_closed": PRIMITIVE_OBLIGATIONS["P_uniform_tube_constants"]["proved"],
            "acceleration_lift_terms": group_counts.get("acceleration_lift", 0),
            "smooth_force_torque_lift_terms": group_counts.get("smooth_force_torque_lift", 0),
            "multiplier_geometry_lift_terms": group_counts.get("multiplier_geometry_lift", 0),
            "gyroscopic_bilinear_lift_terms": group_counts.get("gyroscopic_bilinear_lift", 0),
        },
        "primitive_obligations": [
            {"id": key, **value, "term_rows_using_obligation": primitive_counts[key]}
            for key, value in PRIMITIVE_OBLIGATIONS.items()
        ],
        "conditional_row_level_corollaries": {
            "smooth_force_torque_lift": {
                "label": "cor:d5-smooth-force-row-bound-under-lifts",
                "main_tex_present": smooth_force_corollary_present_main,
                "flat_tex_present": smooth_force_corollary_present_flat,
                "term_rows_conditionally_bound_under_lifts": group_counts.get(
                    "smooth_force_torque_lift", 0
                ),
                "primitive_inputs_assumed": ["P_state_lift", "P_multiplier_lift"],
                "actual_taylor_bounds_proved": 0,
                "primitive_closed": False,
                "pc2_closed": False,
                "uses_d4_direct_route_smoothness_as_rate_proof": False,
            }
        },
        "claim_boundary": {
            "allowed_now": "D5 Taylor terms are reduced to primitive stage-bound obligations; P_tube compact constants are closed",
            "forbidden_now": [
                "primitive/Taylor PC2 route closure",
                "all primitive bounds proved",
                "Taylor term bounds certified",
                "O(h^7) dynamic-row proof closure",
                "submission-ready proof",
            ],
            "close_condition": (
                "Primitive/Taylor PC2 route closes only after every primitive obligation has a uniform O(h^7) proof "
                "and the implication is applied to every listed Taylor subterm."
            ),
        },
        "manuscript_link": {
            "main_tex_present": all(contains_normalized(main_tex, token) for token in manuscript_tokens),
            "flat_tex_present": all(contains_normalized(flat_tex, token) for token in manuscript_tokens),
            "tokens": manuscript_tokens,
        },
        "source_consistency": {
            "term_budget_schema": term_budget.get("schema"),
            "term_budget_pc2_closed": term_budget.get("pc2_closed"),
            "readiness_direct_route_pc2_closed": readiness.get("pc2_closed"),
            "readiness_primitive_taylor_closed_rows": readiness.get("summary", {}).get(
                "primitive_taylor_closed_rows"
            ),
            "readiness_primitive_route_closed": all(
                isinstance(row, dict) and row.get("primitive_taylor_route_closed") is True
                for row in readiness.get("rows", [])
            ),
            "proof_manifest_proof_gap_closed": proof_manifest.get("closure_state", {}).get("proof_gap_closed"),
            "proof_manifest_direct_route_gap_closed": proof_manifest.get("closure_state", {}).get(
                "direct_pc2_proof_gap_closed"
            ),
            "proof_manifest_proof_gap_closed_scope": proof_manifest.get("closure_state", {}).get(
                "proof_gap_closed_scope"
            ),
        },
        "reduction_rows": reduction_rows,
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# D5 Primitive-Bound Reduction Audit",
        "",
        "Status: **primitive reduction recorded; primitive/Taylor PC2 route remains open**.",
        "",
        "This read-only audit groups the 162 D5 Taylor subterms by the primitive",
        "stage-bound obligations that would imply their O(h^7) bounds. It does",
        "close only the compact-tube primitive; it does not prove the five",
        "lift and bilinear primitives and does not close the optional",
        "primitive/Taylor PC2 route; the active direct-route theorem bridge is",
        "closed elsewhere.",
        "",
        "## Summary",
        "",
        f"- Taylor subterms with reduction rules: `{result['summary']['term_rows_with_reduction_rule']}/162`.",
        f"- Primitive obligations: `{result['summary']['primitive_obligation_count']}`.",
        f"- Primitive obligations proved: `{result['summary']['primitive_obligations_proved']}/6`.",
        f"- P_tube compact constants closed: `{result['summary']['p_tube_closed']}`.",
        f"- Taylor term bounds proved: `{result['summary']['term_bounds_proved']}/162`.",
        f"- Separate primitive/Taylor PC2 route closed: `{result['pc2_closed']}`.",
        "",
        "## Reduction Groups",
        "",
        "| group | term rows | role |",
        "|---|---:|---|",
        f"| `acceleration_lift` | `{result['summary']['acceleration_lift_terms']}` | translational and angular acceleration lift errors |",
        f"| `smooth_force_torque_lift` | `{result['summary']['smooth_force_torque_lift_terms']}` | smooth force, torque, and friction maps on the proof tube |",
        f"| `multiplier_geometry_lift` | `{result['summary']['multiplier_geometry_lift_terms']}` | multiplier and dynamic-row geometry/Jacobian lifts |",
        f"| `gyroscopic_bilinear_lift` | `{result['summary']['gyroscopic_bilinear_lift_terms']}` | body-frame angular-velocity bilinear term |",
        "",
        "## Conditional Row-Level Corollaries",
        "",
        f"- Smooth force/torque/friction corollary present main/flat: `{smooth_force_corollary_present_main}/{smooth_force_corollary_present_flat}`.",
        f"- Smooth force/torque/friction rows conditionally bounded: `{group_counts.get('smooth_force_torque_lift', 0)}/72`.",
        "- Smooth force/torque/friction actual Taylor bounds proved: `0/72`.",
        "- D4 direct-route smoothness used as primitive-rate proof: `False`.",
        "",
        "## Primitive Obligations",
        "",
        "| id | term rows | proved | statement |",
        "|---|---:|---:|---|",
    ]
    for row in result["primitive_obligations"]:
        lines.append(
            f"| `{row['id']}` | `{row['term_rows_using_obligation']}` | `{row['proved']}` | {row['statement']} |"
        )
    lines.extend(
        [
            "",
            "## Acceptance Boundary",
            "",
            "- All 162 Taylor subterms have a recorded reduction rule.",
            "- The compact-tube primitive obligation is proved.",
            "- Five lift and bilinear primitive obligations remain open.",
            "- Zero Taylor term bounds are certified.",
            "- The primitive/Taylor PC2 route remains open until the primitive bounds and every induced term bound are proved uniformly.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("d5_primitive_bound_reduction_audit=written")
    print(f"term_rows_with_reduction_rule={result['summary']['term_rows_with_reduction_rule']}")
    print(f"primitive_obligations_proved={primitive_proved}")
    print("pc2_closed=False")


if __name__ == "__main__":
    main()
