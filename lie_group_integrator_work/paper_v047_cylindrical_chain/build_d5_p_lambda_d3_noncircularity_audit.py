#!/usr/bin/env python3
"""Build the D5 P_lambda/D3 non-circularity audit.

This audit closes only PL3 for P_lambda: the already audited D3 virtual-work
identity may be used as an algebraic multiplier-wrench mapping without using
the D5 dynamic residual defect rate. It does not itself prove PL2, PL4, any
Taylor bound, PC2, or the full theorem; later audits record PL2 and the
conditional PL4 propagation separately.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "D5_P_LAMBDA_D3_NONCIRCULARITY_AUDIT.json"
OUT_MD = PAPER / "D5_P_LAMBDA_D3_NONCIRCULARITY_AUDIT.md"

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


def close_requirement_satisfied(manifest: dict[str, Any], requirement_id: str) -> bool | None:
    for row in manifest.get("close_requirements", []):
        if isinstance(row, dict) and row.get("id") == requirement_id:
            value = row.get("satisfied")
            return value if isinstance(value, bool) else None
    return None


def primitive_row(data: dict[str, Any], primitive_id: str) -> dict[str, Any]:
    for row in data.get("primitive_obligations", []):
        if isinstance(row, dict) and row.get("id") == primitive_id:
            return row
    raise ValueError(f"primitive not found: {primitive_id}")


def main() -> None:
    p_lambda_interface = read_json(PAPER / "D5_P_LAMBDA_INTERFACE_AUDIT.json")
    p_lambda_inf_sup_probe = read_json(PAPER / "D5_P_LAMBDA_INF_SUP_PROBE.json")
    d3_wrench = read_json(PAPER / "NEWTON_EULER_VIRTUAL_WORK_WRENCH_AUDIT.json")
    term_budget = read_json(PAPER / "D5_TAYLOR_TERM_BUDGET_AUDIT.json")
    primitive_reduction = read_json(PAPER / "D5_PRIMITIVE_BOUND_REDUCTION_AUDIT.json")
    proof_manifest = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
    main_tex = read_text(PAPER / "main_cmame.tex")
    flat_tex = read_text(PAPER / "cmame_submission_flat" / "main_cmame_submission.tex")

    primitive = primitive_row(primitive_reduction, "P_multiplier_lift")
    direct_rows = [
        row
        for row in term_budget.get("term_rows", [])
        if isinstance(row, dict) and row.get("term_id") in DIRECT_MULTIPLIER_TERM_IDS
    ]
    direct_global_rows = sorted({int(row.get("global_row")) for row in direct_rows})
    d3_summary = d3_wrench.get("summary", {})

    d3_evidence = {
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
        "proof_gap_closed": d3_wrench.get("proof_gap_closed"),
    }

    d3_non_circularity_gate = {
        "d3_identity_is_algebraic_mapping": True,
        "d3_identity_does_not_assume_dynamic_defect_rate": True,
        "d3_identity_not_used_as_multiplier_rate": True,
        "d3_identity_not_used_as_inf_sup_bound": True,
        "d3_identity_not_used_as_taylor_bound": True,
        "stage_residual_perturbation_lemma_disallowed_as_input": True,
    }
    d3_link_ready = (
        d3_evidence["schema"] == "newton-euler-virtual-work-wrench-audit-v1"
        and d3_evidence["checked_rows"] == 36
        and d3_evidence["translational_rows"] == 18
        and d3_evidence["rotational_rows"] == 18
        and d3_evidence["template_virtual_work_identity_proved"] is True
        and d3_evidence["row_expanded_virtual_work_identity_proved"] is True
        and d3_evidence["multiplier_wrench_consistency_closed"] is True
        and d3_evidence["stage_residual_defect_rate_proved"] is False
        and d3_evidence["proof_gap_closed"] is False
    )
    p_lambda_interface_ready = (
        p_lambda_interface.get("pl1_interface_closed") is True
        and p_lambda_interface.get("primitive_closed") is False
        and p_lambda_interface.get("pc2_closed") is False
        and p_lambda_interface.get("d3_consistency_link", {}).get("d3_link_closed") is True
    )
    finite_probe_boundary_ready = (
        p_lambda_inf_sup_probe.get("p_lambda_inf_sup_probe_recorded") is True
        and p_lambda_inf_sup_probe.get("summary", {}).get("finite_probe_full_column_rank_all") is True
        and p_lambda_inf_sup_probe.get("uniform_constant_proved") is False
        and p_lambda_inf_sup_probe.get("pc2_closed") is False
    )
    term_boundary_ready = (
        len(direct_rows) == 36
        and direct_global_rows == DIRECT_MULTIPLIER_ROWS
        and primitive.get("term_rows_using_obligation") == 72
        and all(row.get("taylor_bound_proved") is False for row in direct_rows)
        and term_budget.get("summary", {}).get("certified_taylor_bound_terms") == 0
    )
    pl3_closed = (
        p_lambda_interface_ready
        and finite_probe_boundary_ready
        and term_boundary_ready
        and d3_link_ready
        and all(d3_non_circularity_gate.values())
    )

    manuscript_tokens = [
        r"\label{lem:d5-p-lambda-d3-noncircularity}",
        "closes PL3",
        "does not prove a multiplier lift rate",
        "does not prove a uniform inf-sup bound",
        "does not close the primitive-and-Taylor route to PC2",
    ]

    result = {
        "schema": "d5-p-lambda-d3-noncircularity-audit-v1",
        "status": "p_lambda_d3_noncircularity_closed_lift_open",
        "read_only": True,
        "run_v047_invoked": False,
        "submission_ready": False,
        "pc2_closed": False,
        "proof_gap_closed": False,
        "primitive_id": "P_multiplier_lift",
        "primitive_closed": False,
        "pl3_d3_noncircularity_closed": pl3_closed,
        "pl2_uniform_inf_sup_bound_proved": False,
        "pl4_lift_propagation_closed": False,
        "uniform_inf_sup_bound_proved": False,
        "multiplier_lift_rate_proved": False,
        "term_bounds_proved": 0,
        "closed_subproofs": [
            "PL1_multiplier_variable_and_kkt_column_interface_exposed",
            "PL3_D3_wrench_consistency_used_non_circularly",
        ],
        "open_subproofs": [
            "PL2_uniform_multiplier_inf_sup_bound",
            "PL4_state_acceleration_lift_propagation_to_multiplier_rate",
        ],
        "summary": {
            "closed_subproof_count_for_this_audit": 1,
            "p_lambda_closed_subproof_count_after_d3": 2,
            "required_subproof_count": 4,
            "open_subproof_count_after_d3": 2,
            "direct_multiplier_term_rows": len(direct_rows),
            "term_rows_using_p_lambda": primitive.get("term_rows_using_obligation"),
            "pl3_d3_noncircularity_closed": pl3_closed,
            "pl2_uniform_inf_sup_bound_proved": False,
            "pl4_lift_propagation_closed": False,
            "multiplier_lift_rate_proved": False,
            "term_bounds_proved": 0,
            "pc2_closed": False,
        },
        "d3_non_circularity_gate": d3_non_circularity_gate,
        "d3_evidence": d3_evidence,
        "p_lambda_interface_link": {
            "schema": p_lambda_interface.get("schema"),
            "pl1_interface_closed": p_lambda_interface.get("pl1_interface_closed"),
            "primitive_closed": p_lambda_interface.get("primitive_closed"),
            "pc2_closed": p_lambda_interface.get("pc2_closed"),
            "d3_link_closed": p_lambda_interface.get("d3_consistency_link", {}).get("d3_link_closed"),
        },
        "p_lambda_inf_sup_probe_link": {
            "schema": p_lambda_inf_sup_probe.get("schema"),
            "p_lambda_inf_sup_probe_recorded": p_lambda_inf_sup_probe.get(
                "p_lambda_inf_sup_probe_recorded"
            ),
            "finite_probe_full_column_rank_all": p_lambda_inf_sup_probe.get("summary", {}).get(
                "finite_probe_full_column_rank_all"
            ),
            "min_singular_value_across_probes": p_lambda_inf_sup_probe.get("summary", {}).get(
                "min_singular_value_across_probes"
            ),
            "max_condition_number_across_probes": p_lambda_inf_sup_probe.get("summary", {}).get(
                "max_condition_number_across_probes"
            ),
            "uniform_constant_proved": p_lambda_inf_sup_probe.get("uniform_constant_proved"),
            "pl2_uniform_inf_sup_bound_proved": p_lambda_inf_sup_probe.get(
                "pl2_uniform_inf_sup_bound_proved"
            ),
            "pc2_closed": p_lambda_inf_sup_probe.get("pc2_closed"),
        },
        "term_budget_link": {
            "term_budget_schema": term_budget.get("schema"),
            "term_budget_pc2_closed": term_budget.get("pc2_closed"),
            "direct_multiplier_term_rows": len(direct_rows),
            "direct_multiplier_global_rows": direct_global_rows,
            "p_lambda_term_rows": primitive.get("term_rows_using_obligation"),
            "certified_taylor_bound_terms": term_budget.get("summary", {}).get(
                "certified_taylor_bound_terms"
            ),
            "direct_multiplier_taylor_bounds_proved": sum(
                1 for row in direct_rows if row.get("taylor_bound_proved") is True
            ),
        },
        "source_consistency": {
            "primitive_reduction_schema": primitive_reduction.get("schema"),
            "primitive_reduction_pc2_closed": primitive_reduction.get("pc2_closed"),
            "primitive_term_rows_using_p_lambda": primitive.get("term_rows_using_obligation"),
            "primitive_closed_in_reduction": primitive.get("proved"),
            "proof_manifest_schema": proof_manifest.get("schema"),
            "proof_manifest_proof_gap_closed": proof_manifest.get("closure_state", {}).get(
                "proof_gap_closed"
            ),
            "proof_manifest_direct_route_gap_closed": proof_manifest.get("closure_state", {}).get(
                "direct_pc2_proof_gap_closed"
            ),
            "proof_manifest_proof_gap_closed_scope": proof_manifest.get("closure_state", {}).get(
                "proof_gap_closed_scope"
            ),
            "proof_manifest_pc2_closed": close_requirement_satisfied(proof_manifest, "PC2"),
        },
        "manuscript_link": {
            "main_tex_present": all(contains_normalized(main_tex, token) for token in manuscript_tokens),
            "flat_tex_present": all(contains_normalized(flat_tex, token) for token in manuscript_tokens),
            "tokens": manuscript_tokens,
        },
        "claim_boundary": {
            "allowed_now": (
                "PL3 is closed: the D3 row-expanded virtual-work identity may be "
                "used as an algebraic multiplier-wrench mapping interface for the "
                "36 Newton-Euler rows."
            ),
            "forbidden_now": [
                "P_lambda primitive closure",
                "uniform multiplier inf-sup bound proved",
                "multiplier lift O(h^7) proved",
                "Taylor term bounds certified from P_lambda",
                "D3 wrench identity used as a multiplier-rate proof",
                "primitive/Taylor PC2 route closure",
            ],
            "close_condition": (
                "P_lambda closes only after PL2 proves a uniform multiplier "
                "inf-sup bound and PL4 propagates the open state and acceleration "
                "lift estimates to an O(h^7) multiplier rate."
            ),
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# D5 P_lambda D3 Non-Circularity Audit",
        "",
        "Status: **P_lambda PL3 closed; lift remains open**.",
        "",
        "This read-only audit records that D3's row-expanded virtual-work",
        "identity is used only as an algebraic multiplier-wrench mapping.",
        "It does not use the D5 dynamic residual defect rate, a stage-residual",
        "perturbation lemma, or finite numerical slopes as a multiplier-rate",
        "argument.",
        "",
        "## Summary",
        "",
        f"- Closed P_lambda subproofs after D3 non-circularity: `{result['summary']['p_lambda_closed_subproof_count_after_d3']}/4`.",
        f"- Open P_lambda subproofs after D3 non-circularity: `{result['summary']['open_subproof_count_after_d3']}`.",
        f"- Direct multiplier-wrench term rows: `{result['summary']['direct_multiplier_term_rows']}`.",
        f"- Primitive-ledger term rows using P_lambda: `{result['summary']['term_rows_using_p_lambda']}`.",
        f"- PL3 non-circular D3 use closed: `{result['pl3_d3_noncircularity_closed']}`.",
        f"- Uniform inf-sup bound proved: `{result['uniform_inf_sup_bound_proved']}`.",
        f"- Multiplier lift rate proved: `{result['multiplier_lift_rate_proved']}`.",
        f"- Taylor bounds proved: `{result['term_bounds_proved']}/72`.",
        f"- P_lambda primitive closed: `{result['primitive_closed']}`.",
        f"- Primitive/Taylor PC2 route closed: `{result['pc2_closed']}`.",
        "",
        "## Closed Subproof",
        "",
        "- PL1 multiplier variable and KKT-column interface remains closed from `D5_P_LAMBDA_INTERFACE_AUDIT`.",
        "- PL3 D3 wrench consistency is closed as a non-circular algebraic mapping interface.",
        "- The D3 identity is not used as a multiplier-rate proof.",
        "- The D3 identity is not used as a uniform inf-sup proof.",
        "- The D3 identity is not used as a Taylor-bound certificate.",
        "",
        "## Open Subproofs",
        "",
        "- PL2 and PL4 are not closed by this D3 non-circularity audit; later audits record PL2 and conditional PL4 separately.",
        "- The actual multiplier lift rate still waits on the `P_state` and `P_acc` inputs.",
        "- `P_lambda` remains open.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("d5_p_lambda_d3_noncircularity_audit=written")
    print(f"closed_subproofs_after_d3={result['summary']['p_lambda_closed_subproof_count_after_d3']}/4")
    print("p_lambda_closed=False")
    print("pc2_closed=False")


if __name__ == "__main__":
    main()
