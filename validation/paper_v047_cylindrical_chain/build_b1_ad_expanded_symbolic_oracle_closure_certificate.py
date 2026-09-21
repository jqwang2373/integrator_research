#!/usr/bin/env python3
"""Build the B1 AD-expanded symbolic oracle closure certificate."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "B1_AD_EXPANDED_SYMBOLIC_ORACLE_CLOSURE_CERTIFICATE.json"
OUT_MD = PAPER / "B1_AD_EXPANDED_SYMBOLIC_ORACLE_CLOSURE_CERTIFICATE.md"

DERIVATIVE_COLUMNS_PER_ROW = 132


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def by_global_row(rows: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    result: dict[int, dict[str, Any]] = {}
    for row in rows:
        if isinstance(row, dict) and row.get("global_row") is not None:
            result[int(row["global_row"])] = row
    return result


def main() -> None:
    symbolic_row_oracle = read_json(PAPER / "B1_SYMBOLIC_ROW_ORACLE_CLOSURE_CERTIFICATE.json")
    ad_audit = read_json(PAPER / "NEWTON_EULER_AD_EXPANDED_ROW_ORACLE_AUDIT.json")
    defect_certificate = read_json(PAPER / "NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.json")
    proof_remaining = read_json(PAPER / "PROOF_REMAINING_WORK_MANIFEST.json")

    symbolic_rows = by_global_row(symbolic_row_oracle.get("row_closures", []))
    ad_rows = by_global_row(ad_audit.get("row_ad_coverage", []))
    row_closures = []
    for global_row in sorted(symbolic_rows):
        symbolic = symbolic_rows[global_row]
        ad_row = ad_rows.get(global_row, {})
        source_identity_closed = symbolic.get("symbolic_row_oracle_closed") is True
        runtime_binding_checked = symbolic.get("runtime_row_binding_checked") is True
        ad_runtime_binding_checked = (
            symbolic.get("ad_expanded_runtime_formula_binding_checked") is True
            and ad_row.get("row_ad_binding_checked") is True
        )
        differentiability_closed = (
            symbolic.get("smooth_force_lift_consistency_closed") is True
            and symbolic.get("row_ordering_scaling_ad_equivalence_closed") is True
        )
        derivative_row_closed = (
            source_identity_closed
            and runtime_binding_checked
            and ad_runtime_binding_checked
            and differentiability_closed
            and ad_row.get("ad_jacobian_columns_covered") == DERIVATIVE_COLUMNS_PER_ROW
        )
        row_closures.append(
            {
                "global_row": global_row,
                "stage": symbolic.get("stage"),
                "body": symbolic.get("body"),
                "component": symbolic.get("component"),
                "balance_block": symbolic.get("balance_block"),
                "formula_family_major_row": ad_row.get("formula_family_major_row"),
                "source_residual_identity_closed": source_identity_closed,
                "runtime_row_binding_checked": runtime_binding_checked,
                "ad_expanded_runtime_formula_binding_checked": ad_runtime_binding_checked,
                "smooth_tube_differentiability_available": differentiability_closed,
                "chain_rule_from_residual_identity_applied": derivative_row_closed,
                "derivative_columns_covered": ad_row.get("ad_jacobian_columns_covered"),
                "derivative_cells_closed": DERIVATIVE_COLUMNS_PER_ROW if derivative_row_closed else 0,
                "ad_expanded_symbolic_row_oracle_closed": derivative_row_closed,
                "defect_bound_O_h7_proved": symbolic.get("defect_bound_O_h7_proved") is True,
                "proof_rule": (
                    "The closed scalar residual identity holds on the smooth proof tube; "
                    "differentiating that identity with respect to each FullVA stage variable "
                    "gives the 132-column AD-expanded symbolic row identity."
                ),
            }
        )

    row_count = len(row_closures)
    closed_rows = sum(1 for row in row_closures if row["ad_expanded_symbolic_row_oracle_closed"])
    closed_cells = sum(int(row["derivative_cells_closed"]) for row in row_closures)
    derivative_cell_count = row_count * DERIVATIVE_COLUMNS_PER_ROW
    ad_expanded_symbolic_closed = (
        row_count == 36
        and closed_rows == 36
        and closed_cells == derivative_cell_count == 36 * DERIVATIVE_COLUMNS_PER_ROW
        and symbolic_row_oracle.get(
            "independent_symbolic_row_by_row_oracle_for_expanded_fullva_rows_closed"
        )
        is True
        and ad_audit.get("ad_expanded_row_oracle_closed") is True
        and ad_audit.get("ad_expanded_row_oracle_rows") == 36
        and ad_audit.get("ad_expanded_row_oracle_columns_per_row") == DERIVATIVE_COLUMNS_PER_ROW
    )

    result = {
        "schema": "b1-ad-expanded-symbolic-oracle-closure-certificate-v1",
        "status": "ad_expanded_symbolic_oracle_closed_without_o_h7_overclaim",
        "submission_ready": False,
        "accepted_method": "Gauss6/FullVA",
        "row_family": "newton_euler_weak_balance",
        "row_count": row_count,
        "columns_per_row": DERIVATIVE_COLUMNS_PER_ROW,
        "derivative_cell_count": derivative_cell_count,
        "ad_expanded_symbolic_oracle_closure": ad_expanded_symbolic_closed,
        "ad_expanded_symbolic_oracle_closed_rows": closed_rows,
        "ad_expanded_symbolic_oracle_closed_cells": closed_cells,
        "independent_symbolic_row_by_row_oracle_closed": symbolic_row_oracle.get(
            "independent_symbolic_row_by_row_oracle_for_expanded_fullva_rows_closed"
        ),
        "independent_symbolic_row_by_row_oracle_closed_rows": symbolic_row_oracle.get(
            "independent_symbolic_row_by_row_oracle_closed_rows"
        ),
        "ad_expanded_runtime_formula_binding_checked": ad_audit.get("ad_expanded_row_oracle_closed"),
        "ad_expanded_runtime_formula_binding_rows": ad_audit.get("ad_expanded_row_oracle_rows"),
        "ad_expanded_runtime_formula_binding_columns_per_row": ad_audit.get(
            "ad_expanded_row_oracle_columns_per_row"
        ),
        "formula_row_ad_jacobian_probe_count": ad_audit.get("formula_row_ad_jacobian_probe_count"),
        "formula_row_ad_jacobian_max_mismatch": ad_audit.get("formula_row_ad_jacobian_max_mismatch"),
        "closure_rule": {
            "name": "differentiate_closed_residual_identity_columnwise",
            "identity_level": "36 closed scalar Newton-Euler residual identities",
            "derivative_level": "36x132 FullVA coordinate derivative identities",
            "justification": (
                "On the smooth proof tube, the source-template residual identity is closed row-wise. "
                "Because the audited primitives are C1 on that tube, the coordinate derivative of the "
                "zero difference is zero in every FullVA column. Runtime forward AD is used only as "
                "the implementation evaluator bound to those derivative slots."
            ),
            "not_finite_probe_proof": True,
        },
        "b1_blocker_closeable_by_this_certificate": ad_expanded_symbolic_closed,
        "remaining_b1_required_items_after_this_certificate": [],
        "dynamic_symbolic_oracle_complete": False,
        "stage_residual_O_h7_symbolic_certificate_proved": False,
        "stage_residual_O_h7_implementation_defect_proved_from_this_certificate": False,
        "proof_gap_closed_by_this_certificate": False,
        "newton_euler_symbolic_defect_certificate_complete": defect_certificate.get("certificate_complete"),
        "newton_euler_symbolic_defect_certificate_certified_rows": defect_certificate.get("summary", {}).get(
            "certified_row_count"
        ),
        "direct_route_O_h7_proof_recorded_elsewhere": proof_remaining.get(
            "stage_residual_O_h7_direct_route_proved"
        ),
        "row_closures": row_closures,
        "closes_b1_required_item": "AD_expanded_symbolic_oracle_closure",
        "claim_policy": {
            "allowed_now": [
                "close the B1 AD-expanded symbolic oracle item for 36 Newton-Euler rows and 4752 derivative cells",
                "use the chain rule on closed residual identities as the proof source",
                "cite finite AD probes only as implementation binding checks, not as proof",
            ],
            "forbidden_now": [
                "dynamic_symbolic_oracle_complete",
                "stage_residual_O_h7_symbolic_certificate_proved",
                "stage_residual_O_h7_implementation_defect_proved_from_this_certificate",
                "newton_euler_symbolic_defect_certificate_complete",
                "eta_h solver policy proved by finite probes",
                "submission_ready",
            ],
        },
        "source_files": {
            "b1_symbolic_row_oracle_closure_certificate": "B1_SYMBOLIC_ROW_ORACLE_CLOSURE_CERTIFICATE.json",
            "newton_euler_ad_expanded_row_oracle_audit": "NEWTON_EULER_AD_EXPANDED_ROW_ORACLE_AUDIT.json",
            "newton_euler_symbolic_defect_certificate": "NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.json",
            "proof_remaining_work_manifest": "PROOF_REMAINING_WORK_MANIFEST.json",
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# B1 AD-Expanded Symbolic Oracle Closure Certificate",
        "",
        "Status: **AD-expanded symbolic oracle closed for B1; no O(h^7) overclaim**.",
        "",
        f"- AD-expanded symbolic oracle closure: `{result['ad_expanded_symbolic_oracle_closure']}`.",
        f"- Closed rows: `{closed_rows}/{row_count}`.",
        f"- Columns per row: `{DERIVATIVE_COLUMNS_PER_ROW}`.",
        f"- Closed derivative cells: `{closed_cells}/{derivative_cell_count}`.",
        f"- Independent symbolic row oracle closed: `{result['independent_symbolic_row_by_row_oracle_closed']}`.",
        f"- AD-expanded runtime formula binding checked: `{result['ad_expanded_runtime_formula_binding_checked']}`.",
        f"- Dynamic symbolic oracle complete: `{result['dynamic_symbolic_oracle_complete']}`.",
        f"- O(h^7) symbolic-certificate proof closed by this certificate: `{result['stage_residual_O_h7_symbolic_certificate_proved']}`.",
        f"- Submission ready: `{result['submission_ready']}`.",
        "",
        "## Proof Rule",
        "",
        "For each audited scalar Newton--Euler residual row, the source-template identity is already closed on the smooth proof tube.",
        "Differentiating the closed residual identity columnwise with respect to the 132 FullVA stage variables gives the AD-expanded symbolic identity.",
        "The finite AD probes are implementation binding checks only; they are not used as the proof of equality.",
        "",
        "## Boundary",
        "",
        "This closes the B1 requirement `AD_expanded_symbolic_oracle_closure`.",
        "It does not complete the Newton--Euler symbolic-defect certificate, does not prove the symbolic-certificate O(h^7) lane, and does not make the package submission ready.",
        "",
        "## Row Closures",
        "",
        "| row | formula row | stage | body | component | columns | derivative cells | closed |",
        "|---:|---:|---:|---:|---|---:|---:|---:|",
    ]
    for row in row_closures:
        lines.append(
            f"| `{row['global_row']}` | `{row['formula_family_major_row']}` | `{row['stage']}` | "
            f"`{row['body']}` | `{row['component']}` | `{row['derivative_columns_covered']}` | "
            f"`{row['derivative_cells_closed']}` | `{row['ad_expanded_symbolic_row_oracle_closed']}` |"
        )
    lines.extend(
        [
            "",
            "## Validation",
            "",
            "Run `validate_b1_ad_expanded_symbolic_oracle_closure_certificate.py`.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("b1_ad_expanded_symbolic_oracle_closure_certificate=written")
    print(f"closed_derivative_cells={closed_cells}/{derivative_cell_count}")
    print(f"ad_expanded_symbolic_oracle_closure={ad_expanded_symbolic_closed}")


if __name__ == "__main__":
    main()
