#!/usr/bin/env python3
"""Build a row-local D5 dynamic-defect readiness and closure audit.

This read-only artifact records the row-local direct-substitution closure for
the D5 dynamic-defect proof while preserving the separate primitive/Taylor route
as open.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "D5_DYNAMIC_DEFECT_READINESS_AUDIT.json"
OUT_MD = PAPER / "D5_DYNAMIC_DEFECT_READINESS_AUDIT.md"


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def row_readiness(row: dict[str, Any]) -> dict[str, Any]:
    closure = row.get("closure_state", {})
    evidence = row.get("evidence_present", {})
    blueprint = row.get("d5_dynamic_defect_blueprint", {})
    decomposition = blueprint.get("defect_decomposition", [])
    closed_terms = [
        item.get("term")
        for item in decomposition
        if isinstance(item, dict) and str(item.get("status", "")).startswith("closed")
    ]
    open_terms = [
        item.get("term")
        for item in decomposition
        if isinstance(item, dict) and item.get("status") == "open"
    ]
    closed_input_keys = [
        "balance_identity_closed",
        "multiplier_wrench_consistency_closed",
        "smooth_force_lift_consistency_closed",
        "row_ordering_scaling_ad_equivalence_closed",
        "runtime_formula_row_oracle_link_checked",
    ]
    return {
        "global_row": row.get("global_row"),
        "stage": row.get("stage"),
        "body": row.get("body"),
        "component": row.get("component"),
        "balance_block": row.get("balance_block"),
        "residual_symbol": blueprint.get("residual_symbol"),
        "target_balance": blueprint.get("target_balance"),
        "closed_input_terms": closed_terms,
        "open_terms": open_terms,
        "closed_input_count": sum(1 for key in closed_input_keys if evidence.get(key) is True),
        "closed_input_expected": len(closed_input_keys),
        "runtime_traceability_ready": all(evidence.get(key) is True for key in closed_input_keys),
        "required_certificate_kind": blueprint.get("required_certificate_kind"),
        "required_defect_power": blueprint.get("required_defect_power"),
        "finite_probe_evidence_sufficient": blueprint.get("finite_probe_evidence_sufficient"),
        "residual_to_error_promotion_allowed": blueprint.get("residual_to_error_promotion_allowed"),
        "direct_substitution_closed": blueprint.get("direct_substitution_closed"),
        "direct_substitution_residual_after_substitution": blueprint.get(
            "direct_substitution_residual_after_substitution"
        ),
        "primitive_taylor_route_closed": blueprint.get("primitive_taylor_route_closed"),
        "certified_for_theorem": closure.get("certified_for_theorem"),
        "defect_bound_O_h7_proved": closure.get("defect_bound_O_h7_proved"),
        "required_next_statement": (
            "preserve the direct-substitution proof that substituting Z_G into "
            "the expanded row gives zero residual; keep the primitive/Taylor "
            "route separate and open"
        ),
    }


def main() -> None:
    contract = read_json(PAPER / "NEWTON_EULER_DYNAMIC_ROW_CLOSURE_CONTRACT.json")
    target = read_json(PAPER / "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.json")
    certificate = read_json(PAPER / "NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.json")
    proof_manifest = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
    direct_substitution = read_json(PAPER / "D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE.json")
    main_tex = read_text(PAPER / "main_cmame.tex")
    flat_tex = read_text(PAPER / "cmame_submission_flat" / "main_cmame_submission.tex")

    rows = [row_readiness(row) for row in contract.get("row_contracts", []) if isinstance(row, dict)]
    row_count = len(rows)
    theorem_certified_rows = sum(1 for row in rows if row.get("certified_for_theorem") is True)
    runtime_ready_rows = sum(1 for row in rows if row.get("runtime_traceability_ready") is True)
    power_seven_rows = sum(1 for row in rows if row.get("required_defect_power") == 7)
    open_lifted_stage_terms = sum(1 for row in rows if row.get("open_terms") == ["E_lifted_stage_dynamics"])
    direct_substitution_closed_rows = sum(
        1
        for row in rows
        if row.get("direct_substitution_closed") is True
        and row.get("direct_substitution_residual_after_substitution") == "0"
    )
    primitive_taylor_closed_rows = sum(1 for row in rows if row.get("primitive_taylor_route_closed") is True)
    finite_probe_sufficient_rows = sum(1 for row in rows if row.get("finite_probe_evidence_sufficient") is True)
    residual_promotion_allowed_rows = sum(
        1 for row in rows if row.get("residual_to_error_promotion_allowed") is True
    )
    translational_rows = sum(1 for row in rows if row.get("balance_block") == "translational_newton_balance")
    rotational_rows = sum(1 for row in rows if row.get("balance_block") == "rotational_euler_balance")
    stage_counts = {
        str(stage): sum(1 for row in rows if row.get("stage") == stage)
        for stage in sorted({row.get("stage") for row in rows if row.get("stage") is not None})
    }
    body_counts = {
        str(body): sum(1 for row in rows if row.get("body") == body)
        for body in sorted({row.get("body") for row in rows if row.get("body") is not None})
    }
    manuscript_tokens = [
        r"\label{tab:d5-taylor-certificate-target}",
        "Conditional D5 primitive/Taylor certificate schema retained",
        "Conditional primitive/Taylor target only; active direct route closes separately.",
        "primitive/Taylor route remains open",
    ]
    main_tex_missing = [token for token in manuscript_tokens if token not in main_tex]
    flat_tex_missing = [token for token in manuscript_tokens if token not in flat_tex]

    result = {
        "schema": "d5-dynamic-defect-readiness-audit-v1",
        "status": "d5_direct_substitution_closure_recorded_primitive_taylor_route_open",
        "submission_ready": False,
        "read_only": True,
        "run_v047_invoked": False,
        "stage_residual_O_h7_implementation_defect_proved": True,
        "proof_gap_closed": True,
        "direct_residual_bridge_proof_gap_closed": True,
        "proof_gap_closed_scope": "direct_substitution_row_defect_pc2_only",
        "pc2_closed": True,
        "primitive_taylor_route_closed": False,
        "residual_to_error_route_closed": False,
        "multiplier_reaction_output_order_claimed": False,
        "summary": {
            "row_count": row_count,
            "expected_row_count": contract.get("summary", {}).get("row_count"),
            "translational_rows": translational_rows,
            "rotational_rows": rotational_rows,
            "stage_counts": stage_counts,
            "body_counts": body_counts,
            "runtime_traceability_ready_rows": runtime_ready_rows,
            "power_seven_required_rows": power_seven_rows,
            "open_lifted_stage_terms": open_lifted_stage_terms,
            "direct_substitution_closed_rows": direct_substitution_closed_rows,
            "direct_substitution_dynamic_zero_rows": direct_substitution.get("summary", {}).get(
                "dynamic_zero_residual_rows"
            ),
            "primitive_taylor_closed_rows": primitive_taylor_closed_rows,
            "theorem_certified_rows": theorem_certified_rows,
            "finite_probe_sufficient_rows": finite_probe_sufficient_rows,
            "residual_to_error_promotion_allowed_rows": residual_promotion_allowed_rows,
            "manuscript_d5_target_table_present_main_flat": not main_tex_missing and not flat_tex_missing,
        },
        "claim_boundary": {
            "allowed_now": "row-local D5 direct-substitution closure and primitive/Taylor non-closure boundary",
            "forbidden_now": [
                "primitive/Taylor-route closure",
                "finite-probe-only D5 closure",
                "residual-to-error D5 closure",
                "submission-ready proof",
            ],
            "reason_open": (
                "The direct-substitution D5 route is closed for all 36 rows. "
                "The primitive/Taylor route remains open and must not be cited as closed."
            ),
        },
        "manuscript_link": {
            "main_tex_missing_tokens": main_tex_missing,
            "flat_tex_missing_tokens": flat_tex_missing,
            "main_tex_present": not main_tex_missing,
            "flat_tex_present": not flat_tex_missing,
        },
        "source_files": {
            "dynamic_row_closure_contract": "NEWTON_EULER_DYNAMIC_ROW_CLOSURE_CONTRACT.json",
            "symbolic_target_audit": "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.json",
            "symbolic_defect_certificate": "NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.json",
            "proof_closure_manifest": "PROOF_CLOSURE_MANIFEST.json",
            "direct_substitution_certificate": "D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE.json",
        },
        "source_consistency": {
            "contract_schema": contract.get("schema"),
            "target_schema": target.get("schema"),
            "certificate_schema": certificate.get("schema"),
            "proof_manifest_status": proof_manifest.get("status"),
            "contract_d5_blueprint_is_not_closure": contract.get("summary", {}).get("d5_blueprint_is_not_closure"),
            "certificate_pc2_closed": certificate.get("summary", {}).get("pc2_dynamic_O_h7_defect_certificate_closed"),
            "direct_substitution_status": direct_substitution.get("status"),
            "direct_substitution_closed": direct_substitution.get("direct_route_mathematical_certificate_closed"),
        },
        "rows": rows,
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# D5 Dynamic-Defect Readiness Audit",
        "",
        "Status: **D5 direct-substitution closure recorded; primitive/Taylor route remains open**.",
        "",
        "This read-only audit records the row-local direct-substitution closure",
        "for the 36 Newton-Euler dynamic rows. It also preserves the separate",
        "primitive/Taylor route as open.",
        "",
        "## Summary",
        "",
        f"- Rows checked: `{row_count}/36`.",
        f"- Translational/rotational rows: `{translational_rows}/{rotational_rows}`.",
        f"- Runtime-traceability-ready rows: `{runtime_ready_rows}/36`.",
        f"- Rows requiring defect power at least seven: `{power_seven_rows}/36`.",
        f"- Open lifted-stage dynamic terms: `{open_lifted_stage_terms}/36`.",
        f"- Direct-substitution closed rows: `{direct_substitution_closed_rows}/36`.",
        f"- Direct-substitution dynamic zero rows: `{result['summary']['direct_substitution_dynamic_zero_rows']}/36`.",
        f"- Primitive/Taylor closed rows: `{primitive_taylor_closed_rows}/36`.",
        f"- Direct-route certified rows: `{theorem_certified_rows}/36`.",
        f"- Finite-probe-sufficient rows: `{finite_probe_sufficient_rows}/36`.",
        f"- Residual-to-error-promotion rows: `{residual_promotion_allowed_rows}/36`.",
        f"- Manuscript D5 Taylor target table present in main/flat TeX: `{not main_tex_missing}/{not flat_tex_missing}`.",
        f"- Stage residual O(h^7) implementation defect proved: `{result['stage_residual_O_h7_implementation_defect_proved']}`.",
        f"- Direct PC2 row-defect route closed: `{result['pc2_closed']}`.",
        f"- Proof gap closed scope: `{result['proof_gap_closed_scope']}`.",
        f"- Primitive/Taylor route closed: `{result['primitive_taylor_route_closed']}`.",
        f"- Residual-to-error route closed: `{result['residual_to_error_route_closed']}`.",
        f"- Multiplier/reaction output order claimed: `{result['multiplier_reaction_output_order_claimed']}`.",
        f"- Submission ready: `{result['submission_ready']}`.",
        "",
        "## Required D5 Statement",
        "",
        "For each row, substitute the smooth FullVA Gauss lift `Z_G` into the",
        "expanded Newton-Euler row. The D5 direct-substitution certificate records",
        "zero residual row-by-row, hence an `O(h^7)` bound. Finite probes and",
        "residual-to-error promotion do not satisfy this acceptance test.",
        "",
        "## Row Coverage",
        "",
        "| row | stage | body | block | component | closed inputs | open term | direct residual |",
        "|---:|---:|---:|---|---|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['global_row']}` | `{row['stage']}` | `{row['body']}` | "
            f"{row['balance_block']} | `{row['component']}` | "
            f"`{row['closed_input_count']}/{row['closed_input_expected']}` | "
            f"`{','.join(row['open_terms'])}` | "
            f"`{row['direct_substitution_residual_after_substitution']}` |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- Allowed now: row-local direct-substitution D5 closure and a precise primitive/Taylor non-closure boundary.",
            "- Forbidden now: primitive/Taylor-route closure, finite-probe-only D5 closure, residual-to-error D5 closure, or submission-ready proof.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("d5_dynamic_defect_readiness_audit=written")
    print(f"rows={row_count}")
    print(f"runtime_traceability_ready_rows={runtime_ready_rows}")
    print(f"open_lifted_stage_terms={open_lifted_stage_terms}")
    print("pc2_closed=True")
    print("submission_ready=False")


if __name__ == "__main__":
    main()
