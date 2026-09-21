#!/usr/bin/env python3
"""Build the D5 P_geom chart-reduction audit.

This audit closes only the accepted-chart Lipschitz reduction for the
lower-pair multiplier-wrench geometry terms.  It remains conditional on the
P_state pose lift and P_lambda multiplier lift, so it does not close P_geom or
PC2.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
OUT_JSON = PAPER / "D5_P_GEOM_CHART_REDUCTION_AUDIT.json"
OUT_MD = PAPER / "D5_P_GEOM_CHART_REDUCTION_AUDIT.md"


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


def close_requirement_satisfied(manifest: dict[str, Any], requirement_id: str) -> bool | None:
    for row in manifest.get("close_requirements", []):
        if isinstance(row, dict) and row.get("id") == requirement_id:
            value = row.get("satisfied")
            return value if isinstance(value, bool) else None
    return None


def main() -> None:
    term_budget = read_json(PAPER / "D5_TAYLOR_TERM_BUDGET_AUDIT.json")
    p_tube = read_json(PAPER / "D5_P_TUBE_CONSTANTS_AUDIT.json")
    p_state_gap = read_json(PAPER / "D5_P_STATE_LIFT_GAP_AUDIT.json")
    proof_manifest = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
    main_tex = read_text(LATEX / "main_cmame.tex")
    flat_tex = read_text(LATEX / "cmame_submission_flat" / "main_cmame_submission.tex")

    term_rows = term_budget.get("term_rows", [])
    if not isinstance(term_rows, list):
        raise ValueError("D5 term-budget term_rows must be a list")
    geom_rows = [
        row
        for row in term_rows
        if isinstance(row, dict) and row.get("term_id") in {"T_multiplier_force_lift", "R_multiplier_torque_lift"}
    ]
    translational_rows = [row for row in geom_rows if row.get("term_id") == "T_multiplier_force_lift"]
    rotational_rows = [row for row in geom_rows if row.get("term_id") == "R_multiplier_torque_lift"]
    row_ids = [row.get("global_row") for row in geom_rows]
    stage_body_pairs = sorted({(row.get("stage"), row.get("body")) for row in geom_rows})

    manuscript_tokens = [
        r"\label{lem:d5-geom-chart-reduction}",
        r"\label{cor:d5-geom-row-bound-under-lifts}",
        "Multiplier-geometry chart reduction",
        r"W_G(q,\lambda)=G_b(q)^T\lambda",
        r"W_H(q,\lambda)=H_b(q)^T\lambda",
        r"C_{\mathrm{geom}}=C_{W,\max}(C_q+C_\lambda)",
        "does not close \(P_{\mathrm{geom}}\)",
        "pose and multiplier lifts supplied by \(P_{\mathrm{state}}\) and \(P_{\lambda}\)",
    ]

    closed_subproofs = [
        "accepted_chart_multiplier_wrench_expansion",
        "compact_tube_lipschitz_geometry_bound",
        "binding_to_36_multiplier_geometry_rows",
    ]
    open_dependencies = [
        "P_state pose lift O(h^7)",
        "P_lambda multiplier lift O(h^7)",
    ]

    result = {
        "schema": "d5-p-geom-chart-reduction-audit-v1",
        "status": "p_geom_chart_reduction_closed_primitive_open",
        "read_only": True,
        "run_v047_invoked": False,
        "submission_ready": False,
        "pc2_closed": False,
        "proof_gap_closed": False,
        "primitive_id": "P_geometry_lift",
        "primitive_closed": False,
        "chart_reduction_closed": True,
        "term_bounds_proved": 0,
        "term_rows_conditionally_reduced": len(geom_rows),
        "translational_rows_conditionally_reduced": len(translational_rows),
        "rotational_rows_conditionally_reduced": len(rotational_rows),
        "conditional_geom_row_bounds_under_lifts": {
            "closed": True,
            "row_count": len(geom_rows),
            "rows": row_ids,
            "translational_row_count": len(translational_rows),
            "rotational_row_count": len(rotational_rows),
            "constant": "C_geom = C_max (C_q + C_lambda)",
            "assumptions": [
                "P_state pose lift ||q_hat_{s,b}-q_b(t_s)|| <= C_q h^7",
                "P_lambda multiplier lift ||lambda_hat_s-lambda(t_s)|| <= C_lambda h^7",
            ],
            "actual_taylor_bounds_proved": 0,
            "primitive_closed": False,
            "pc2_closed": False,
        },
        "row_ids": row_ids,
        "summary": {
            "closed_subproof_count": len(closed_subproofs),
            "required_subproof_count": 4,
            "open_dependency_count": len(open_dependencies),
            "term_rows_conditionally_reduced": len(geom_rows),
            "conditional_geom_row_bounds_under_lifts": len(geom_rows),
            "translational_rows_conditionally_reduced": len(translational_rows),
            "rotational_rows_conditionally_reduced": len(rotational_rows),
            "stage_body_pairs": len(stage_body_pairs),
            "p_tube_closed": p_tube.get("primitive_closed"),
            "p_state_closed": p_state_gap.get("primitive_closed"),
            "p_lambda_closed": False,
            "pc2_closed": False,
        },
        "closed_subproofs": closed_subproofs,
        "open_dependencies": open_dependencies,
        "proof_sketch": {
            "maps": [
                "W_G(q,lambda)=G_b(q)^T lambda",
                "W_H(q,lambda)=H_b(q)^T lambda",
            ],
            "difference_identity": (
                "A(q_hat)^T lambda_hat - A(q)^T lambda = "
                "(A(q_hat)-A(q))^T lambda_hat + A(q)^T (lambda_hat-lambda)"
            ),
            "compact_bound": (
                "If A is either G_b or H_b with sup_K ||A|| <= M_A, "
                "sup_K ||D A|| <= L_A, and ||lambda_hat|| is bounded on the compact tube, "
                "then ||A(q_hat)^T lambda_hat - A(q)^T lambda|| <= "
                "C_A (||q_hat-q|| + ||lambda_hat-lambda||)."
            ),
            "conditional_rate": (
                "The multiplier-geometry contribution is O(h^7) once P_state supplies "
                "the pose lift and P_lambda supplies the multiplier lift."
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
            "term_rows": len(geom_rows),
            "p_tube_schema": p_tube.get("schema"),
            "p_tube_closed": p_tube.get("primitive_closed"),
            "p_tube_pc2_closed": p_tube.get("pc2_closed"),
            "p_state_schema": p_state_gap.get("schema"),
            "p_state_closed": p_state_gap.get("primitive_closed"),
            "p_state_pc2_closed": p_state_gap.get("pc2_closed"),
            "proof_manifest_pc2_closed": close_requirement_satisfied(proof_manifest, "PC2"),
        },
        "claim_boundary": {
            "allowed_now": "P_geom accepted-chart geometry conditional reduction is recorded; the P_geom primitive remains open until the P_state and P_lambda lifts close",
            "forbidden_now": [
                "P_geom primitive closure",
                "P_state closure",
                "P_lambda closure",
                "Taylor term bounds certified",
                "primitive/Taylor PC2 route closure",
                "unconditional sixth-order theorem",
            ],
            "close_condition": (
                "P_geom closes only after P_state and P_lambda prove the O(h^7) lift "
                "rates and the conditional reduction is applied to all listed "
                "multiplier-geometry term rows."
            ),
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# D5 P_geom Chart Reduction Audit",
        "",
        "Status: **P_geom chart reduction closed; primitive remains open**.",
        "",
        "This read-only audit proves the accepted-chart Lipschitz reduction for",
        "the lower-pair multiplier-wrench geometry maps `G_b(q)^T lambda` and",
        "`H_b(q)^T lambda`. It does not prove the pose or multiplier lift rates,",
        "so it does not close `P_geom` or PC2.",
        "",
        "## Summary",
        "",
        f"- Closed P_geom subproofs: `{len(closed_subproofs)}/4`.",
        f"- Open dependencies: `{len(open_dependencies)}`.",
        f"- Multiplier-geometry rows conditionally reduced: `{len(geom_rows)}/36`.",
        f"- Translational/rotational rows: `{len(translational_rows)}/{len(rotational_rows)}`.",
        f"- P_tube closed: `{p_tube.get('primitive_closed')}`.",
        f"- P_state closed: `{p_state_gap.get('primitive_closed')}`.",
        "- P_lambda closed: `False`.",
        f"- P_geom primitive closed: `{result['primitive_closed']}`.",
        f"- Primitive/Taylor PC2 route closed: `{result['pc2_closed']}`.",
        "",
        "## Bound",
        "",
        "For `A(q)` equal to either `G_b(q)` or `H_b(q)`,",
        "",
        "`A(q_hat)^T lambda_hat - A(q)^T lambda = (A(q_hat)-A(q))^T lambda_hat + A(q)^T (lambda_hat-lambda)`.",
        "",
        "On the compact proof tube, bounded `A`, bounded `D A`, and bounded",
        "`lambda_hat` give",
        "",
        "`||A(q_hat)^T lambda_hat - A(q)^T lambda|| <= C_A (||q_hat-q|| + ||lambda_hat-lambda||)`.",
        "",
        "Thus the geometry contribution is `O(h^7)` once `P_state` supplies the",
        "pose lift and `P_lambda` supplies the multiplier lift.",
        "",
        "## Conditional Row Corollary",
        "",
        "Under the still-open `P_state` pose lift and `P_lambda` multiplier",
        "lift, the row-level corollary in the manuscript gives",
        "",
        "`C_geom = C_max (C_q + C_lambda)`",
        "",
        "and binds the estimate to rows",
        "",
        f"`{row_ids}`.",
        "",
        f"Conditional geometry row bounds under lifts: `{len(geom_rows)}/36`.",
        "Actual Taylor bounds proved by this audit remain `0`.",
        "",
        "## Acceptance Boundary",
        "",
        "- The accepted-chart geometry expansion is closed.",
        "- The compact-tube Lipschitz reduction is closed.",
        "- The estimate is bound to the 36 multiplier-geometry term rows.",
        "- `P_state` and `P_lambda` remain open, so `P_geom` remains open.",
        "- Zero Taylor term bounds are certified by this audit.",
        "- Primitive/Taylor PC2 lane remains open.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("d5_p_geom_chart_reduction_audit=written")
    print(f"closed_subproofs={len(closed_subproofs)}/4")
    print(f"multiplier_geometry_rows_conditionally_reduced={len(geom_rows)}/36")
    print("p_geom_closed=False")
    print("pc2_closed=False")


if __name__ == "__main__":
    main()
