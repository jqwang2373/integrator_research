#!/usr/bin/env python3
"""Validate the D5 P_geom chart-reduction audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "D5_P_GEOM_CHART_REDUCTION_AUDIT.json"
AUDIT_MD = PAPER / "D5_P_GEOM_CHART_REDUCTION_AUDIT.md"


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
        term_budget = read_json(PAPER / "D5_TAYLOR_TERM_BUDGET_AUDIT.json")
        p_tube = read_json(PAPER / "D5_P_TUBE_CONSTANTS_AUDIT.json")
        p_state = read_json(PAPER / "D5_P_STATE_LIFT_GAP_AUDIT.json")
        proof_manifest = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
    except Exception as exc:  # noqa: BLE001
        print(f"D5 P_geom chart reduction audit validation: FAIL\n- {exc}")
        return 1

    summary = audit.get("summary", {})
    source = audit.get("source_consistency", {})
    proof = audit.get("proof_sketch", {})
    claim = audit.get("claim_boundary", {})
    conditional_rows = audit.get("conditional_geom_row_bounds_under_lifts", {})
    geom_rows = [
        row
        for row in term_budget.get("term_rows", [])
        if isinstance(row, dict) and row.get("term_id") in {"T_multiplier_force_lift", "R_multiplier_torque_lift"}
    ]

    checks.check(audit.get("schema") == "d5-p-geom-chart-reduction-audit-v1", "schema changed")
    checks.check(audit.get("status") == "p_geom_chart_reduction_closed_primitive_open", "status changed")
    checks.check(audit.get("read_only") is True, "audit must be read-only")
    checks.check(audit.get("run_v047_invoked") is False, "run_v047 must not be invoked")
    checks.check(audit.get("submission_ready") is False, "submission readiness overclaimed")
    checks.check(audit.get("pc2_closed") is False, "PC2 unexpectedly closed")
    checks.check(audit.get("proof_gap_closed") is False, "proof gap unexpectedly closed")
    checks.check(audit.get("primitive_id") == "P_geometry_lift", "primitive id changed")
    checks.check(audit.get("primitive_closed") is False, "P_geom primitive unexpectedly closed")
    checks.check(audit.get("chart_reduction_closed") is True, "chart reduction not closed")
    checks.check(audit.get("term_bounds_proved") == 0, "Taylor term bounds unexpectedly proved")
    checks.check(audit.get("term_rows_conditionally_reduced") == 36, "geometry term row count changed")
    checks.check(audit.get("translational_rows_conditionally_reduced") == 18, "translational geometry rows changed")
    checks.check(audit.get("rotational_rows_conditionally_reduced") == 18, "rotational geometry rows changed")
    checks.check(conditional_rows.get("closed") is True, "conditional geometry row corollary not closed")
    checks.check(conditional_rows.get("row_count") == 36, "conditional geometry row count changed")
    checks.check(conditional_rows.get("rows") == audit.get("row_ids"), "conditional geometry rows mismatch")
    checks.check(conditional_rows.get("translational_row_count") == 18, "conditional translational row count changed")
    checks.check(conditional_rows.get("rotational_row_count") == 18, "conditional rotational row count changed")
    checks.check(
        conditional_rows.get("constant") == "C_geom = C_max (C_q + C_lambda)",
        "conditional geometry constant changed",
    )
    checks.check(
        conditional_rows.get("assumptions")
        == [
            "P_state pose lift ||q_hat_{s,b}-q_b(t_s)|| <= C_q h^7",
            "P_lambda multiplier lift ||lambda_hat_s-lambda(t_s)|| <= C_lambda h^7",
        ],
        "conditional geometry assumptions changed",
    )
    checks.check(conditional_rows.get("actual_taylor_bounds_proved") == 0, "conditional corollary overclaims Taylor bounds")
    checks.check(conditional_rows.get("primitive_closed") is False, "conditional corollary overclaims P_geom")
    checks.check(conditional_rows.get("pc2_closed") is False, "conditional corollary overclaims PC2")
    checks.check(summary.get("closed_subproof_count") == 3, "closed subproof count changed")
    checks.check(summary.get("required_subproof_count") == 4, "required subproof count changed")
    checks.check(summary.get("open_dependency_count") == 2, "open dependency count changed")
    checks.check(summary.get("term_rows_conditionally_reduced") == 36, "summary row count changed")
    checks.check(
        summary.get("conditional_geom_row_bounds_under_lifts") == 36,
        "summary conditional geometry row count changed",
    )
    checks.check(summary.get("translational_rows_conditionally_reduced") == 18, "summary translational rows changed")
    checks.check(summary.get("rotational_rows_conditionally_reduced") == 18, "summary rotational rows changed")
    checks.check(summary.get("stage_body_pairs") == 6, "stage/body pair count changed")
    checks.check(summary.get("p_tube_closed") is True and p_tube.get("primitive_closed") is True, "P_tube link missing")
    checks.check(summary.get("p_state_closed") is False and p_state.get("primitive_closed") is False, "P_state unexpectedly closed")
    checks.check(summary.get("p_lambda_closed") is False, "P_lambda unexpectedly closed")
    checks.check(summary.get("pc2_closed") is False, "summary PC2 unexpectedly closed")
    checks.check(len(audit.get("closed_subproofs", [])) == 3, "closed subproof list changed")
    checks.check(
        audit.get("open_dependencies") == ["P_state pose lift O(h^7)", "P_lambda multiplier lift O(h^7)"],
        "open dependencies changed",
    )
    checks.check("W_G" in ",".join(proof.get("maps", [])) and "W_H" in ",".join(proof.get("maps", [])), "proof maps missing")
    checks.check("lambda_hat-lambda" in proof.get("difference_identity", ""), "difference identity missing")
    checks.check("C_A" in proof.get("compact_bound", ""), "compact bound missing")
    checks.check("P_state" in proof.get("conditional_rate", ""), "P_state conditional rate missing")
    checks.check("P_lambda" in proof.get("conditional_rate", ""), "P_lambda conditional rate missing")
    checks.check(audit.get("manuscript_link", {}).get("main_tex_present") is True, "main TeX lemma link missing")
    checks.check(audit.get("manuscript_link", {}).get("flat_tex_present") is True, "flat TeX lemma link missing")
    checks.check(source.get("term_budget_schema") == term_budget.get("schema"), "term budget schema link missing")
    checks.check(source.get("term_budget_pc2_closed") is False, "term budget unexpectedly closes PC2")
    checks.check(source.get("term_rows") == 36 and len(geom_rows) == 36, "geometry source rows changed")
    checks.check(source.get("p_tube_closed") is True, "P_tube source link missing")
    checks.check(source.get("p_state_closed") is False, "P_state source link changed")
    checks.check(source.get("proof_manifest_pc2_closed") is True, "proof manifest direct PC2 closure not reflected")
    checks.check("P_geom primitive closure" in claim.get("forbidden_now", []), "P_geom closure not forbidden")
    checks.check(
        proof_manifest.get("closure_state", {}).get("pc2_closed_by_direct_substitution") is True,
        "proof manifest direct-substitution closure missing",
    )
    checks.check(
        proof_manifest.get("closure_state", {}).get("primitive_lift_route_closed") is False,
        "proof manifest unexpectedly closes primitive lift route",
    )

    for token in [
        "Status: **P_geom chart reduction closed; primitive remains open**.",
        "Closed P_geom subproofs: `3/4`.",
        "Open dependencies: `2`.",
        "Multiplier-geometry rows conditionally reduced: `36/36`.",
        "Translational/rotational rows: `18/18`.",
        "P_state closed: `False`.",
        "P_lambda closed: `False`.",
        "P_geom primitive closed: `False`.",
        "Primitive/Taylor PC2 route closed: `False`.",
        "`||A(q_hat)^T lambda_hat - A(q)^T lambda|| <= C_A (||q_hat-q|| + ||lambda_hat-lambda||)`.",
        "`C_geom = C_max (C_q + C_lambda)`",
        "Conditional geometry row bounds under lifts: `36/36`.",
        "Actual Taylor bounds proved by this audit remain `0`.",
        "`P_state` and `P_lambda` remain open, so `P_geom` remains open.",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("D5 P_geom chart reduction audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("D5 P_geom chart reduction audit validation: PASS")
    print("closed_subproofs=3/4")
    print("multiplier_geometry_rows_conditionally_reduced=36/36")
    print("p_geom_closed=False")
    print("pc2_closed=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
