#!/usr/bin/env python3
"""Validate the D5 P_lambda/D3 non-circularity audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "D5_P_LAMBDA_D3_NONCIRCULARITY_AUDIT.json"
AUDIT_MD = PAPER / "D5_P_LAMBDA_D3_NONCIRCULARITY_AUDIT.md"
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


def close_requirement_satisfied(manifest: dict[str, Any], requirement_id: str) -> bool | None:
    for row in manifest.get("close_requirements", []):
        if isinstance(row, dict) and row.get("id") == requirement_id:
            value = row.get("satisfied")
            return value if isinstance(value, bool) else None
    return None


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(AUDIT_JSON)
        audit_md = AUDIT_MD.read_text(encoding="utf-8", errors="replace")
        p_lambda_interface = read_json(PAPER / "D5_P_LAMBDA_INTERFACE_AUDIT.json")
        p_lambda_inf_sup_probe = read_json(PAPER / "D5_P_LAMBDA_INF_SUP_PROBE.json")
        d3_wrench = read_json(PAPER / "NEWTON_EULER_VIRTUAL_WORK_WRENCH_AUDIT.json")
        term_budget = read_json(PAPER / "D5_TAYLOR_TERM_BUDGET_AUDIT.json")
        primitive_reduction = read_json(PAPER / "D5_PRIMITIVE_BOUND_REDUCTION_AUDIT.json")
        proof_manifest = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
    except Exception as exc:  # noqa: BLE001
        print(f"D5 P_lambda D3 non-circularity audit validation: FAIL\n- {exc}")
        return 1

    summary = audit.get("summary", {})
    gate = audit.get("d3_non_circularity_gate", {})
    d3_evidence = audit.get("d3_evidence", {})
    interface_link = audit.get("p_lambda_interface_link", {})
    probe_link = audit.get("p_lambda_inf_sup_probe_link", {})
    term_link = audit.get("term_budget_link", {})
    source = audit.get("source_consistency", {})
    claim = audit.get("claim_boundary", {})
    d3_summary = d3_wrench.get("summary", {})

    checks.check(audit.get("schema") == "d5-p-lambda-d3-noncircularity-audit-v1", "schema changed")
    checks.check(
        audit.get("status") == "p_lambda_d3_noncircularity_closed_lift_open",
        "status changed",
    )
    checks.check(audit.get("read_only") is True, "audit must be read-only")
    checks.check(audit.get("run_v047_invoked") is False, "run_v047 must not be invoked")
    checks.check(audit.get("submission_ready") is False, "submission readiness overclaimed")
    checks.check(audit.get("pc2_closed") is False, "PC2 unexpectedly closed")
    checks.check(audit.get("proof_gap_closed") is False, "proof gap unexpectedly closed")
    checks.check(audit.get("primitive_id") == "P_multiplier_lift", "primitive id changed")
    checks.check(audit.get("primitive_closed") is False, "P_lambda unexpectedly closed")
    checks.check(audit.get("pl3_d3_noncircularity_closed") is True, "PL3 not closed")
    checks.check(audit.get("pl2_uniform_inf_sup_bound_proved") is False, "PL2 unexpectedly closed")
    checks.check(audit.get("pl4_lift_propagation_closed") is False, "PL4 unexpectedly closed")
    checks.check(audit.get("uniform_inf_sup_bound_proved") is False, "uniform inf-sup overclaimed")
    checks.check(audit.get("multiplier_lift_rate_proved") is False, "multiplier lift overclaimed")
    checks.check(audit.get("term_bounds_proved") == 0, "Taylor bounds unexpectedly proved")

    checks.check(summary.get("closed_subproof_count_for_this_audit") == 1, "audit subproof count changed")
    checks.check(
        summary.get("p_lambda_closed_subproof_count_after_d3") == 2,
        "P_lambda aggregate closed subproof count changed",
    )
    checks.check(summary.get("required_subproof_count") == 4, "required subproof count changed")
    checks.check(summary.get("open_subproof_count_after_d3") == 2, "open subproof count changed")
    checks.check(summary.get("direct_multiplier_term_rows") == 36, "direct row count changed")
    checks.check(summary.get("term_rows_using_p_lambda") == 72, "P_lambda term-row count changed")
    checks.check(summary.get("pl3_d3_noncircularity_closed") is True, "summary PL3 closure missing")
    checks.check(summary.get("pl2_uniform_inf_sup_bound_proved") is False, "summary PL2 overclaimed")
    checks.check(summary.get("pl4_lift_propagation_closed") is False, "summary PL4 overclaimed")
    checks.check(summary.get("multiplier_lift_rate_proved") is False, "summary lift overclaimed")
    checks.check(summary.get("term_bounds_proved") == 0, "summary Taylor bounds overclaimed")
    checks.check(summary.get("pc2_closed") is False, "summary PC2 overclaimed")

    checks.check(
        audit.get("closed_subproofs")
        == [
            "PL1_multiplier_variable_and_kkt_column_interface_exposed",
            "PL3_D3_wrench_consistency_used_non_circularly",
        ],
        "closed subproof list changed",
    )
    checks.check(
        audit.get("open_subproofs")
        == [
            "PL2_uniform_multiplier_inf_sup_bound",
            "PL4_state_acceleration_lift_propagation_to_multiplier_rate",
        ],
        "open subproof list changed",
    )

    for key in [
        "d3_identity_is_algebraic_mapping",
        "d3_identity_does_not_assume_dynamic_defect_rate",
        "d3_identity_not_used_as_multiplier_rate",
        "d3_identity_not_used_as_inf_sup_bound",
        "d3_identity_not_used_as_taylor_bound",
        "stage_residual_perturbation_lemma_disallowed_as_input",
    ]:
        checks.check(gate.get(key) is True, f"D3 non-circularity gate missing: {key}")

    checks.check(
        d3_evidence.get("schema") == "newton-euler-virtual-work-wrench-audit-v1",
        "D3 schema link changed",
    )
    checks.check(
        d3_evidence.get("status") == "d3_row_expanded_virtual_work_identity_checked_dynamic_defect_open",
        "D3 status link changed",
    )
    checks.check(d3_evidence.get("checked_rows") == 36, "D3 checked rows changed")
    checks.check(d3_evidence.get("translational_rows") == 18, "D3 translational rows changed")
    checks.check(d3_evidence.get("rotational_rows") == 18, "D3 rotational rows changed")
    checks.check(d3_evidence.get("site_count_checked") == 9, "D3 site count changed")
    checks.check(
        d3_evidence.get("template_virtual_work_identity_proved") is True
        and d3_summary.get("template_virtual_work_identity_proved") is True,
        "D3 template identity missing",
    )
    checks.check(
        d3_evidence.get("row_expanded_virtual_work_identity_proved") is True
        and d3_summary.get("row_expanded_virtual_work_identity_proved") is True,
        "D3 row-expanded identity missing",
    )
    checks.check(
        d3_evidence.get("multiplier_wrench_consistency_closed") is True
        and d3_summary.get("multiplier_wrench_consistency_closed") is True,
        "D3 multiplier consistency missing",
    )
    checks.check(
        d3_evidence.get("stage_residual_defect_rate_proved") is False
        and d3_wrench.get("stage_residual_O_h7_implementation_defect_proved") is False,
        "D3 residual-rate overclaimed",
    )
    checks.check(
        d3_evidence.get("proof_gap_closed") is False and d3_wrench.get("proof_gap_closed") is False,
        "D3 proof gap unexpectedly closed",
    )

    checks.check(interface_link.get("schema") == p_lambda_interface.get("schema"), "PL1 schema link missing")
    checks.check(
        interface_link.get("pl1_interface_closed") is True
        and p_lambda_interface.get("pl1_interface_closed") is True,
        "PL1 interface not closed",
    )
    checks.check(
        interface_link.get("primitive_closed") is False
        and p_lambda_interface.get("primitive_closed") is False,
        "PL1 link unexpectedly closes primitive",
    )
    checks.check(
        interface_link.get("pc2_closed") is False and p_lambda_interface.get("pc2_closed") is False,
        "PL1 link unexpectedly closes PC2",
    )
    checks.check(interface_link.get("d3_link_closed") is True, "PL1 D3 link missing")

    checks.check(probe_link.get("schema") == p_lambda_inf_sup_probe.get("schema"), "PL2 probe schema link missing")
    checks.check(
        probe_link.get("p_lambda_inf_sup_probe_recorded") is True
        and p_lambda_inf_sup_probe.get("p_lambda_inf_sup_probe_recorded") is True,
        "PL2 finite probe not recorded",
    )
    checks.check(
        probe_link.get("finite_probe_full_column_rank_all") is True
        and p_lambda_inf_sup_probe.get("summary", {}).get("finite_probe_full_column_rank_all") is True,
        "PL2 finite rank diagnostic missing",
    )
    checks.check(
        probe_link.get("uniform_constant_proved") is False
        and p_lambda_inf_sup_probe.get("uniform_constant_proved") is False,
        "finite probe unexpectedly proves uniform constant",
    )
    checks.check(
        probe_link.get("pl2_uniform_inf_sup_bound_proved") is False
        and p_lambda_inf_sup_probe.get("pl2_uniform_inf_sup_bound_proved") is False,
        "PL2 unexpectedly closed by finite probe",
    )
    checks.check(
        probe_link.get("pc2_closed") is False and p_lambda_inf_sup_probe.get("pc2_closed") is False,
        "finite probe unexpectedly closes PC2",
    )

    checks.check(term_link.get("term_budget_schema") == term_budget.get("schema"), "term-budget schema link missing")
    checks.check(term_link.get("term_budget_pc2_closed") is False, "term budget unexpectedly closes PC2")
    checks.check(term_link.get("direct_multiplier_term_rows") == 36, "direct term row count changed")
    checks.check(term_link.get("direct_multiplier_global_rows") == DIRECT_MULTIPLIER_ROWS, "direct rows changed")
    checks.check(term_link.get("p_lambda_term_rows") == 72, "P_lambda primitive row count changed")
    checks.check(term_link.get("certified_taylor_bound_terms") == 0, "term budget unexpectedly certifies terms")
    checks.check(term_link.get("direct_multiplier_taylor_bounds_proved") == 0, "direct terms unexpectedly certified")

    primitive = None
    for row in primitive_reduction.get("primitive_obligations", []):
        if isinstance(row, dict) and row.get("id") == "P_multiplier_lift":
            primitive = row
            break
    checks.check(source.get("primitive_reduction_schema") == primitive_reduction.get("schema"), "primitive reduction link missing")
    checks.check(source.get("primitive_reduction_pc2_closed") is False, "primitive reduction closes PC2")
    checks.check(source.get("primitive_term_rows_using_p_lambda") == 72, "primitive source row count changed")
    checks.check(source.get("primitive_closed_in_reduction") is False, "primitive reduction overcloses P_lambda")
    checks.check(primitive is not None and primitive.get("term_rows_using_obligation") == 72, "P_lambda primitive row missing")
    checks.check(primitive is not None and primitive.get("proved") is False, "P_lambda primitive unexpectedly proved")
    checks.check(source.get("proof_manifest_schema") == proof_manifest.get("schema"), "proof manifest link missing")
    checks.check(
        source.get("proof_manifest_proof_gap_closed")
        == proof_manifest.get("closure_state", {}).get("proof_gap_closed"),
        "proof manifest proof-gap link mismatch",
    )
    checks.check(
        source.get("proof_manifest_pc2_closed") == close_requirement_satisfied(proof_manifest, "PC2"),
        "proof manifest PC2 link mismatch",
    )
    checks.check(
        audit.get("pc2_closed") is False and audit.get("primitive_closed") is False,
        "local PL3 audit must not inherit direct-route PC2 closure",
    )

    checks.check(audit.get("manuscript_link", {}).get("main_tex_present") is True, "main TeX lemma link missing")
    checks.check(audit.get("manuscript_link", {}).get("flat_tex_present") is True, "flat TeX lemma link missing")

    for forbidden in [
        "P_lambda primitive closure",
        "uniform multiplier inf-sup bound proved",
        "multiplier lift O(h^7) proved",
        "Taylor term bounds certified from P_lambda",
        "D3 wrench identity used as a multiplier-rate proof",
        "primitive/Taylor PC2 route closure",
    ]:
        checks.check(forbidden in claim.get("forbidden_now", []), f"forbidden claim missing: {forbidden}")

    for token in [
        "Status: **P_lambda PL3 closed; lift remains open**.",
        "Closed P_lambda subproofs after D3 non-circularity: `2/4`.",
        "Open P_lambda subproofs after D3 non-circularity: `2`.",
        "Direct multiplier-wrench term rows: `36`.",
        "Primitive-ledger term rows using P_lambda: `72`.",
        "PL3 non-circular D3 use closed: `True`.",
        "Uniform inf-sup bound proved: `False`.",
        "Multiplier lift rate proved: `False`.",
        "Taylor bounds proved: `0/72`.",
        "P_lambda primitive closed: `False`.",
        "Primitive/Taylor PC2 route closed: `False`.",
        "PL3 D3 wrench consistency is closed as a non-circular algebraic mapping interface.",
        "The D3 identity is not used as a multiplier-rate proof.",
        "PL2 and PL4 are not closed by this D3 non-circularity audit; later audits record PL2 and conditional PL4 separately.",
        "The actual multiplier lift rate still waits on the `P_state` and `P_acc` inputs.",
        "`P_lambda` remains open.",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("D5 P_lambda D3 non-circularity audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("D5 P_lambda D3 non-circularity audit validation: PASS")
    print("closed_subproofs_after_d3=2/4")
    print("p_lambda_closed=False")
    print("pc2_closed=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
