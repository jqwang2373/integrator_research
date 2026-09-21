#!/usr/bin/env python3
"""Validate the D5 P_lambda interface audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "D5_P_LAMBDA_INTERFACE_AUDIT.json"
AUDIT_MD = PAPER / "D5_P_LAMBDA_INTERFACE_AUDIT.md"
DIRECT_MULTIPLIER_ROWS = list(range(24, 36)) + list(range(68, 80)) + list(range(112, 124))


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
        primitive_reduction = read_json(PAPER / "D5_PRIMITIVE_BOUND_REDUCTION_AUDIT.json")
        term_budget = read_json(PAPER / "D5_TAYLOR_TERM_BUDGET_AUDIT.json")
        d3_wrench = read_json(PAPER / "NEWTON_EULER_VIRTUAL_WORK_WRENCH_AUDIT.json")
    except Exception as exc:  # noqa: BLE001
        print(f"D5 P_lambda interface audit validation: FAIL\n- {exc}")
        return 1

    primitive = None
    for row in primitive_reduction.get("primitive_obligations", []):
        if isinstance(row, dict) and row.get("id") == "P_multiplier_lift":
            primitive = row
            break
    direct_rows = [
        row
        for row in term_budget.get("term_rows", [])
        if isinstance(row, dict)
        and row.get("term_id") in {"T_multiplier_force_lift", "R_multiplier_torque_lift"}
    ]

    summary = audit.get("summary", {})
    lambda_interface = audit.get("lambda_variable_interface", {})
    kkt_interface = audit.get("kkt_column_interface", {})
    term_interface = audit.get("term_interface", {})
    d3_link = audit.get("d3_consistency_link", {})
    anti = audit.get("anti_circularity_gate", {})
    source = audit.get("source_consistency", {})
    claim = audit.get("claim_boundary", {})

    checks.check(audit.get("schema") == "d5-p-lambda-interface-audit-v1", "schema changed")
    checks.check(audit.get("status") == "p_lambda_interface_closed_lift_open", "status changed")
    checks.check(audit.get("read_only") is True, "audit must be read-only")
    checks.check(audit.get("run_v047_invoked") is False, "run_v047 must not be invoked")
    checks.check(audit.get("submission_ready") is False, "submission readiness overclaimed")
    checks.check(audit.get("pc2_closed") is False, "PC2 unexpectedly closed")
    checks.check(audit.get("proof_gap_closed") is False, "proof gap unexpectedly closed")
    checks.check(audit.get("primitive_id") == "P_multiplier_lift", "primitive id changed")
    checks.check(audit.get("primitive_closed") is False, "P_lambda unexpectedly closed")
    checks.check(audit.get("pl1_interface_closed") is True, "PL1 interface not closed")
    checks.check(audit.get("multiplier_lift_rate_proved") is False, "multiplier lift rate overclaimed")
    checks.check(audit.get("uniform_inf_sup_bound_proved") is False, "uniform inf-sup overclaimed")
    checks.check(audit.get("term_bounds_proved") == 0, "Taylor bounds unexpectedly proved")
    checks.check(audit.get("term_rows_using_p_lambda") == 72, "P_lambda primitive row count changed")
    checks.check(audit.get("direct_multiplier_term_rows") == 36, "direct multiplier row count changed")
    checks.check(audit.get("direct_multiplier_global_rows") == DIRECT_MULTIPLIER_ROWS, "direct rows changed")
    checks.check(
        audit.get("direct_multiplier_term_counts")
        == {"R_multiplier_torque_lift": 18, "T_multiplier_force_lift": 18},
        "direct multiplier term counts changed",
    )

    checks.check(summary.get("closed_subproof_count_for_this_audit") == 1, "closed subproof count changed")
    checks.check(
        summary.get("p_lambda_closed_subproof_count_after_interface") == 1,
        "P_lambda aggregate closed subproof count changed",
    )
    checks.check(summary.get("required_subproof_count") == 4, "required subproof count changed")
    checks.check(summary.get("open_subproof_count_after_interface") == 3, "open subproof count changed")
    checks.check(summary.get("stage_lambda_variables") == 24, "stage lambda variable count changed")
    checks.check(summary.get("per_stage_lambda_variables") == 8, "per-stage lambda variable count changed")
    checks.check(summary.get("direct_multiplier_term_rows") == 36, "summary direct row count changed")
    checks.check(summary.get("term_rows_using_p_lambda") == 72, "summary primitive row count changed")
    checks.check(summary.get("multiplier_lift_rate_proved") is False, "summary overclaims lift rate")
    checks.check(summary.get("uniform_inf_sup_bound_proved") is False, "summary overclaims inf-sup")
    checks.check(summary.get("term_bounds_proved") == 0, "summary overclaims Taylor bounds")
    checks.check(summary.get("pc2_closed") is False, "summary overclaims PC2")

    checks.check(
        audit.get("closed_subproofs") == ["PL1_multiplier_variable_and_kkt_column_interface_exposed"],
        "closed subproof list changed",
    )
    checks.check(
        audit.get("open_subproofs")
        == [
            "PL2_uniform_multiplier_inf_sup_bound",
            "PL3_D3_wrench_consistency_used_non_circularly",
            "PL4_state_acceleration_lift_propagation_to_multiplier_rate",
        ],
        "open subproof list changed",
    )
    checks.check(lambda_interface.get("stage_count") == 3, "stage count changed")
    checks.check(lambda_interface.get("body_count") == 2, "body count changed")
    checks.check(lambda_interface.get("joint_count") == 2, "joint count changed")
    checks.check(lambda_interface.get("body_size") == 18, "body size changed")
    checks.check(lambda_interface.get("lambda_size") == 4, "lambda size changed")
    checks.check(lambda_interface.get("stage_size") == 44, "stage size changed")
    checks.check(lambda_interface.get("per_stage_lambda_dim") == 8, "per-stage lambda dim changed")
    checks.check(lambda_interface.get("total_lambda_variables") == 24, "total lambda variable count changed")
    checks.check(len(lambda_interface.get("lambda_components", [])) == 4, "lambda component list changed")

    checks.check(kkt_interface.get("column_group_name") == "lower_pair_lambda", "lambda group name changed")
    checks.check(kkt_interface.get("per_stage_column_width") == 8, "per-stage column width changed")
    checks.check(kkt_interface.get("total_column_width") == 24, "total column width changed")
    checks.check(kkt_interface.get("source_trace_complete") is True, "source trace incomplete")
    for token, present in kkt_interface.get("source_trace", {}).items():
        checks.check(present is True, f"source trace token missing: {token}")

    checks.check(term_interface.get("direct_term_ids") == ["R_multiplier_torque_lift", "T_multiplier_force_lift"], "direct term ids changed")
    checks.check(term_interface.get("direct_multiplier_rows") == DIRECT_MULTIPLIER_ROWS, "term interface rows changed")
    checks.check(all(term_interface.get("checks", {}).values()), "term interface has failed subcheck")
    checks.check(len(term_interface.get("interface_rows", [])) == 36, "interface row inventory changed")
    checks.check(len(direct_rows) == 36, "source term budget direct row count changed")
    checks.check(sorted({int(row.get("global_row")) for row in direct_rows}) == DIRECT_MULTIPLIER_ROWS, "source direct rows changed")

    checks.check(d3_link.get("schema") == "newton-euler-virtual-work-wrench-audit-v1", "D3 schema link changed")
    checks.check(
        d3_link.get("status") == "d3_row_expanded_virtual_work_identity_checked_dynamic_defect_open",
        "D3 status link changed",
    )
    checks.check(d3_link.get("checked_rows") == 36, "D3 checked rows changed")
    checks.check(d3_link.get("translational_rows") == 18, "D3 translational rows changed")
    checks.check(d3_link.get("rotational_rows") == 18, "D3 rotational rows changed")
    checks.check(d3_link.get("site_count_checked") == 9, "D3 site count changed")
    checks.check(d3_link.get("template_virtual_work_identity_proved") is True, "D3 template identity missing")
    checks.check(d3_link.get("row_expanded_virtual_work_identity_proved") is True, "D3 row identity missing")
    checks.check(d3_link.get("multiplier_wrench_consistency_closed") is True, "D3 wrench consistency missing")
    checks.check(d3_link.get("stage_residual_defect_rate_proved") is False, "D3 overclaims residual rate")
    checks.check(d3_link.get("d3_link_closed") is True, "D3 link not closed")

    checks.check(anti.get("interface_is_not_inf_sup_bound") is True, "interface/inf-sup boundary missing")
    checks.check(anti.get("interface_is_not_multiplier_lift_rate") is True, "interface/lift boundary missing")
    checks.check(anti.get("dynamic_balance_defect_rate_not_assumed") is True, "dynamic defect boundary missing")
    checks.check(anti.get("stage_residual_perturbation_lemma_disallowed_as_input") is True, "stage lemma not barred")
    checks.check(anti.get("d3_wrench_identity_not_used_as_multiplier_rate") is True, "D3/rate boundary missing")
    checks.check(anti.get("direct_multiplier_rows_are_not_taylor_bounds") is True, "direct row/Taylor-bound boundary missing")
    checks.check(audit.get("manuscript_link", {}).get("main_tex_present") is True, "main TeX lemma link missing")
    checks.check(audit.get("manuscript_link", {}).get("flat_tex_present") is True, "flat TeX lemma link missing")

    checks.check(
        source.get("primitive_reduction_schema") == primitive_reduction.get("schema"),
        "primitive reduction schema link missing",
    )
    checks.check(source.get("primitive_reduction_pc2_closed") is False, "primitive reduction closes PC2")
    checks.check(source.get("primitive_term_rows_using_p_lambda") == 72, "primitive row count link changed")
    checks.check(source.get("primitive_closed_in_reduction") is False, "primitive reduction overcloses P_lambda")
    checks.check(source.get("term_budget_schema") == term_budget.get("schema"), "term budget schema link missing")
    checks.check(source.get("term_budget_pc2_closed") is False, "term budget closes PC2")
    checks.check(source.get("direct_multiplier_term_rows") == 36, "direct term row source link changed")
    checks.check(source.get("d3_wrench_schema") == d3_wrench.get("schema"), "D3 source schema link missing")
    checks.check(source.get("d3_wrench_consistency_closed") is True, "D3 source closure missing")
    checks.check(source.get("d3_stage_residual_defect_proved") is False, "D3 source overclaims residual defect")
    checks.check(primitive is not None and primitive.get("term_rows_using_obligation") == 72, "primitive source row missing")
    checks.check(primitive is not None and primitive.get("proved") is False, "primitive source unexpectedly proved")

    for forbidden in [
        "P_lambda primitive closure",
        "multiplier lift O(h^7) proved",
        "uniform multiplier inf-sup bound proved",
        "Taylor term bounds certified from P_lambda",
        "D3 wrench consistency used as a multiplier-rate proof",
        "primitive/Taylor PC2 route closure",
    ]:
        checks.check(forbidden in claim.get("forbidden_now", []), f"forbidden claim missing: {forbidden}")

    for token in [
        "Status: **P_lambda interface closed; lift remains open**.",
        "Closed P_lambda subproofs after interface: `1/4`.",
        "Open P_lambda subproofs after interface: `3`.",
        "Stage lambda variables: `24`.",
        "Per-stage lambda variables: `8`.",
        "Direct multiplier-wrench term rows: `36`.",
        "Primitive-ledger term rows using P_lambda: `72`.",
        "P_lambda primitive closed: `False`.",
        "Multiplier lift rate proved: `False`.",
        "Uniform inf-sup bound proved: `False`.",
        "Taylor bounds proved: `0/72`.",
        "Primitive/Taylor PC2 route closed: `False`.",
        "PL1 multiplier variable and KKT-column interface is closed.",
        "PL2/PL3/PL4 are not closed by this interface audit; later audits record PL2, PL3, and conditional PL4 separately.",
        "The actual multiplier lift rate still waits on the `P_state` and `P_acc` inputs.",
        "`P_lambda` remains open.",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("D5 P_lambda interface audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("D5 P_lambda interface audit validation: PASS")
    print("closed_subproofs_after_interface=1/4")
    print("direct_multiplier_term_rows=36")
    print("term_rows_using_p_lambda=72")
    print("p_lambda_closed=False")
    print("pc2_closed=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
