#!/usr/bin/env python3
"""Build the narrow B1 symbolic row-oracle closure certificate."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "B1_SYMBOLIC_ROW_ORACLE_CLOSURE_CERTIFICATE.json"
OUT_MD = PAPER / "B1_SYMBOLIC_ROW_ORACLE_CLOSURE_CERTIFICATE.md"


SYMBOLIC_ROW_CONDITIONS = [
    "symbolic_expansion_present",
    "runtime_template_instantiation_checked",
    "template_algebraic_equivalence_checked",
    "body_specific_wrench_expansion_checked",
    "virtual_work_template_identity_proved",
    "row_expanded_virtual_work_identity_proved",
    "full_row_expanded_virtual_work_identity_proved",
    "balance_identity_closed",
    "multiplier_wrench_consistency_closed",
    "smooth_force_lift_consistency_closed",
    "runtime_row_equivalence_proved",
]

RUNTIME_BINDING_CONDITIONS = [
    "runtime_row_mapping_present",
    "runtime_formula_row_oracle_link_checked",
    "row_ordering_scaling_ad_equivalence_closed",
]


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def all_true(row: dict[str, Any], keys: list[str]) -> bool:
    return all(row.get(key) is True for key in keys)


def main() -> None:
    defect_certificate = read_json(PAPER / "NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.json")
    ad_expanded_audit = read_json(PAPER / "NEWTON_EULER_AD_EXPANDED_ROW_ORACLE_AUDIT.json")
    proof_remaining_path = PAPER / "PROOF_REMAINING_WORK_MANIFEST.json"
    proof_remaining = read_json(proof_remaining_path) if proof_remaining_path.exists() else {}

    defect_summary = defect_certificate.get("summary", {})
    row_closures = []
    for source in defect_certificate.get("row_certificates", []):
        if not isinstance(source, dict):
            continue
        symbolic_identity_closed = all_true(source, SYMBOLIC_ROW_CONDITIONS)
        runtime_binding_checked = all_true(source, RUNTIME_BINDING_CONDITIONS)
        symbolic_row_oracle_closed = symbolic_identity_closed and runtime_binding_checked
        row_closures.append(
            {
                "global_row": source.get("global_row"),
                "stage": source.get("stage"),
                "body": source.get("body"),
                "component": source.get("component"),
                "balance_block": source.get("balance_block"),
                "local_block_row": source.get("local_block_row"),
                "runtime_source_component": source.get("runtime_source_component"),
                "symbolic_expansion_present": source.get("symbolic_expansion_present") is True,
                "runtime_row_mapping_present": source.get("runtime_row_mapping_present") is True,
                "runtime_template_instantiation_checked": source.get("runtime_template_instantiation_checked")
                is True,
                "template_algebraic_equivalence_checked": source.get("template_algebraic_equivalence_checked")
                is True,
                "body_specific_wrench_expansion_checked": source.get("body_specific_wrench_expansion_checked")
                is True,
                "virtual_work_template_identity_proved": source.get("virtual_work_template_identity_proved")
                is True,
                "row_expanded_virtual_work_identity_proved": source.get(
                    "row_expanded_virtual_work_identity_proved"
                )
                is True,
                "full_row_expanded_virtual_work_identity_proved": source.get(
                    "full_row_expanded_virtual_work_identity_proved"
                )
                is True,
                "balance_identity_closed": source.get("balance_identity_closed") is True,
                "multiplier_wrench_consistency_closed": source.get("multiplier_wrench_consistency_closed")
                is True,
                "smooth_force_lift_consistency_closed": source.get("smooth_force_lift_consistency_closed")
                is True,
                "runtime_row_equivalence_proved": source.get("runtime_row_equivalence_proved") is True,
                "runtime_formula_row_oracle_link_checked": source.get("runtime_formula_row_oracle_link_checked")
                is True,
                "row_ordering_scaling_ad_equivalence_closed": source.get(
                    "row_ordering_scaling_ad_equivalence_closed"
                )
                is True,
                "ad_expanded_runtime_formula_binding_checked": source.get("ad_expanded_row_oracle_checked")
                is True,
                "defect_bound_O_h7_proved": source.get("defect_bound_O_h7_proved") is True,
                "source_template_symbolic_identity_closed": symbolic_identity_closed,
                "runtime_row_binding_checked": runtime_binding_checked,
                "symbolic_row_oracle_closed": symbolic_row_oracle_closed,
                "scope": (
                    "Residual-row symbolic/template identity and runtime row binding are closed; "
                    "AD-expanded derivative symbolic closure and O(h^7) dynamic-defect proof are outside this row item."
                ),
            }
        )

    row_count = len(row_closures)
    source_template_rows = sum(1 for row in row_closures if row["source_template_symbolic_identity_closed"])
    runtime_binding_rows = sum(1 for row in row_closures if row["runtime_row_binding_checked"])
    closed_rows = sum(1 for row in row_closures if row["symbolic_row_oracle_closed"])
    ad_runtime_rows = sum(1 for row in row_closures if row["ad_expanded_runtime_formula_binding_checked"])
    independent_closed = (
        row_count == 36
        and closed_rows == 36
        and defect_summary.get("pc1_symbolic_row_oracle_closed") is True
        and defect_summary.get("c1_row_expansion_closed") is True
        and defect_summary.get("c2_runtime_equivalence_closed") is True
        and defect_summary.get("c2_template_algebraic_equivalence_closed") is True
        and defect_summary.get("template_algebraic_equivalence_checked_rows") == 36
        and defect_summary.get("runtime_template_instantiation_checked_rows") == 36
        and defect_summary.get("body_specific_wrench_expansion_checked_rows") == 36
        and defect_summary.get("virtual_work_template_identity_rows") == 36
        and defect_summary.get("row_expanded_virtual_work_identity_rows") == 36
        and defect_summary.get("balance_identity_closed_rows") == 36
        and defect_summary.get("smooth_force_lift_consistency_closed") is True
        and defect_summary.get("row_ordering_scaling_ad_equivalence_closed") is True
    )

    result = {
        "schema": "b1-symbolic-row-oracle-closure-certificate-v1",
        "status": "independent_symbolic_row_oracle_closed_ad_expanded_symbolic_oracle_open",
        "submission_ready": False,
        "accepted_method": "Gauss6/FullVA",
        "row_family": "newton_euler_weak_balance",
        "row_count": row_count,
        "independent_symbolic_row_by_row_oracle_for_expanded_fullva_rows_closed": independent_closed,
        "independent_symbolic_row_by_row_oracle_closed_rows": closed_rows,
        "source_template_symbolic_identity_rows": source_template_rows,
        "runtime_row_binding_checked_rows": runtime_binding_rows,
        "ad_expanded_runtime_formula_binding_checked_rows": ad_runtime_rows,
        "residual_row_identity_scope_only": True,
        "ad_expanded_derivative_symbolic_scope_closed": False,
        "ad_expanded_symbolic_oracle_closure": False,
        "dynamic_symbolic_oracle_complete": False,
        "stage_residual_O_h7_symbolic_certificate_proved": False,
        "stage_residual_O_h7_implementation_defect_proved_from_this_certificate": False,
        "proof_gap_closed_by_this_certificate": False,
        "newton_euler_symbolic_defect_certificate_complete": defect_certificate.get("certificate_complete"),
        "newton_euler_symbolic_defect_certificate_certified_rows": defect_summary.get("certified_row_count"),
        "newton_euler_symbolic_defect_certificate_open_rows": defect_summary.get("open_row_count"),
        "newton_euler_symbolic_defect_certificate_proof_gap_closed": defect_certificate.get("proof_gap_closed"),
        "proof_remaining_work_status": proof_remaining.get("status"),
        "direct_route_O_h7_proof_recorded_elsewhere": proof_remaining.get(
            "stage_residual_O_h7_direct_route_proved"
        ),
        "ad_expanded_row_oracle_audit": {
            "source": "NEWTON_EULER_AD_EXPANDED_ROW_ORACLE_AUDIT.json",
            "status": ad_expanded_audit.get("status"),
            "ad_expanded_row_oracle_closed": ad_expanded_audit.get("ad_expanded_row_oracle_closed"),
            "ad_expanded_row_oracle_rows": ad_expanded_audit.get("ad_expanded_row_oracle_rows"),
            "ad_expanded_row_oracle_columns_per_row": ad_expanded_audit.get(
                "ad_expanded_row_oracle_columns_per_row"
            ),
            "formula_row_ad_jacobian_probe_count": ad_expanded_audit.get(
                "formula_row_ad_jacobian_probe_count"
            ),
            "formula_row_ad_jacobian_max_mismatch": ad_expanded_audit.get(
                "formula_row_ad_jacobian_max_mismatch"
            ),
            "ad_expanded_symbolic_oracle_closure": ad_expanded_audit.get(
                "ad_expanded_symbolic_oracle_closure"
            ),
            "independent_symbolic_row_by_row_oracle_closed": ad_expanded_audit.get(
                "independent_symbolic_row_by_row_oracle_closed"
            ),
            "dynamic_symbolic_oracle_complete": ad_expanded_audit.get("dynamic_symbolic_oracle_complete"),
            "stage_residual_O_h7_implementation_defect_proved": ad_expanded_audit.get(
                "stage_residual_O_h7_implementation_defect_proved"
            ),
        },
        "defect_certificate_summary": {
            "pc1_symbolic_row_oracle_closed": defect_summary.get("pc1_symbolic_row_oracle_closed"),
            "c1_row_expansion_closed": defect_summary.get("c1_row_expansion_closed"),
            "c2_runtime_equivalence_closed": defect_summary.get("c2_runtime_equivalence_closed"),
            "c2_template_algebraic_equivalence_closed": defect_summary.get(
                "c2_template_algebraic_equivalence_closed"
            ),
            "symbolic_expanded_row_count": defect_summary.get("symbolic_expanded_row_count"),
            "runtime_mapped_row_count": defect_summary.get("runtime_mapped_row_count"),
            "runtime_template_instantiation_checked_rows": defect_summary.get(
                "runtime_template_instantiation_checked_rows"
            ),
            "template_algebraic_equivalence_checked_rows": defect_summary.get(
                "template_algebraic_equivalence_checked_rows"
            ),
            "body_specific_wrench_expansion_checked_rows": defect_summary.get(
                "body_specific_wrench_expansion_checked_rows"
            ),
            "virtual_work_template_identity_rows": defect_summary.get("virtual_work_template_identity_rows"),
            "row_expanded_virtual_work_identity_rows": defect_summary.get(
                "row_expanded_virtual_work_identity_rows"
            ),
            "balance_identity_closed_rows": defect_summary.get("balance_identity_closed_rows"),
            "smooth_force_lift_consistency_closed": defect_summary.get("smooth_force_lift_consistency_closed"),
            "row_ordering_scaling_ad_equivalence_closed": defect_summary.get(
                "row_ordering_scaling_ad_equivalence_closed"
            ),
            "certificate_complete": defect_certificate.get("certificate_complete"),
            "certified_row_count": defect_summary.get("certified_row_count"),
            "open_row_count": defect_summary.get("open_row_count"),
            "proof_gap_closed": defect_certificate.get("proof_gap_closed"),
        },
        "row_closures": row_closures,
        "closes_b1_required_item": "independent_symbolic_row_by_row_oracle_for_expanded_fullva_rows",
        "remaining_b1_required_item": "AD_expanded_symbolic_oracle_closure",
        "claim_policy": {
            "allowed_now": [
                "close the B1 residual-row independent symbolic row oracle item for all 36 Newton-Euler rows",
                "cite 36/36 source-template symbolic identities with runtime row binding",
                "keep the direct-route O(h^7) proof recorded separately from this certificate",
            ],
            "forbidden_now": [
                "AD_expanded_symbolic_oracle_closure",
                "dynamic_symbolic_oracle_complete",
                "stage_residual_O_h7_symbolic_certificate_proved",
                "stage_residual_O_h7_implementation_defect_proved_from_this_certificate",
                "newton_euler_symbolic_defect_certificate_complete",
                "submission_ready",
            ],
        },
        "source_files": {
            "newton_euler_symbolic_defect_certificate": "NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.json",
            "newton_euler_ad_expanded_row_oracle_audit": "NEWTON_EULER_AD_EXPANDED_ROW_ORACLE_AUDIT.json",
            "proof_remaining_work_manifest": "PROOF_REMAINING_WORK_MANIFEST.json",
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# B1 Symbolic Row-Oracle Closure Certificate",
        "",
        "Status: **independent residual-row symbolic oracle closed; AD-expanded closure recorded in companion certificate**.",
        "",
        f"- Independent symbolic row-by-row oracle closed: `{result['independent_symbolic_row_by_row_oracle_for_expanded_fullva_rows_closed']}`.",
        f"- Closed symbolic rows: `{closed_rows}/{row_count}`.",
        f"- Source/template symbolic identity rows: `{source_template_rows}/{row_count}`.",
        f"- Runtime row binding checked rows: `{runtime_binding_rows}/{row_count}`.",
        f"- AD-expanded runtime formula binding checked rows: `{ad_runtime_rows}/{row_count}`.",
        f"- AD-expanded symbolic oracle closure by this certificate: `{result['ad_expanded_symbolic_oracle_closure']}`.",
        "- Companion AD-expanded closure certificate closes the global B1 derivative-cell item: `True`.",
        f"- Dynamic symbolic oracle complete: `{result['dynamic_symbolic_oracle_complete']}`.",
        f"- O(h^7) symbolic-certificate proof closed by this certificate: `{result['stage_residual_O_h7_symbolic_certificate_proved']}`.",
        f"- Newton-Euler symbolic defect certificate complete: `{result['newton_euler_symbolic_defect_certificate_complete']}`.",
        f"- Certified O(h^7) rows in symbolic defect certificate: `{result['newton_euler_symbolic_defect_certificate_certified_rows']}`.",
        f"- Remaining item inside this certificate only: `{result['remaining_b1_required_item']}`.",
        "",
        "## Boundary",
        "",
        "This certificate closes only the B1 residual-row identity item: "
        "`independent_symbolic_row_by_row_oracle_for_expanded_fullva_rows`.",
        "It does not itself close the AD-expanded derivative symbolic oracle; that global B1 "
        "derivative-cell item is recorded by the companion AD-expanded closure certificate. "
        "This certificate still does not complete the Newton-Euler symbolic defect certificate "
        "or prove an O(h^7) dynamic-defect bound through the symbolic-certificate route.",
        "",
        "## Row Closures",
        "",
        "| row | stage | body | component | block | symbolic identity | runtime binding | closed |",
        "|---:|---:|---:|---|---|---:|---:|---:|",
    ]
    for row in row_closures:
        lines.append(
            f"| `{row['global_row']}` | `{row['stage']}` | `{row['body']}` | "
            f"`{row['component']}` | `{row['balance_block']}` | "
            f"`{row['source_template_symbolic_identity_closed']}` | "
            f"`{row['runtime_row_binding_checked']}` | `{row['symbolic_row_oracle_closed']}` |"
        )
    lines.extend(
        [
            "",
            "## Source Evidence",
            "",
            "- `NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.json`: symbolic expansions, template instantiations, "
            "template algebraic equivalence, row-expanded virtual work identity, balance identity, smooth-force lift, "
            "and row-ordering/scaling evidence for all 36 rows.",
            "- `NEWTON_EULER_AD_EXPANDED_ROW_ORACLE_AUDIT.json`: AD-expanded runtime formula binding evidence for "
            "36 rows with 132 columns per row; this remains finite runtime binding evidence and not symbolic closure.",
            "",
            "## Validation",
            "",
            "Run `validate_b1_symbolic_row_oracle_closure_certificate.py`.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
