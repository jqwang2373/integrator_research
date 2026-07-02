#!/usr/bin/env python3
"""Build the Newton-Euler translational/rotational balance-identity audit.

This audit closes only D1 and D2 at source-identity level.  It checks that the
implemented Newton-Euler dynamic rows are the accepted linear- and
angular-momentum balance laws after row ordering, body-specific sign expansion,
multiplier-wrench consistency, smooth force lift, and AD binding have already
been audited.  It deliberately does not prove the D5 O(h^7) dynamic-row defect.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "NEWTON_EULER_BALANCE_IDENTITY_AUDIT.json"
OUT_MD = PAPER / "NEWTON_EULER_BALANCE_IDENTITY_AUDIT.md"


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def row_identity_closed(row: dict[str, Any]) -> bool:
    return all(
        row.get(key) is True
        for key in [
            "runtime_template_instantiation_checked",
            "body_specific_wrench_expansion_checked",
            "template_algebraic_equivalence_checked",
            "multiplier_wrench_consistency_closed",
            "smooth_force_lift_consistency_closed",
            "row_ordering_scaling_ad_equivalence_closed",
            "runtime_row_equivalence_proved",
        ]
    )


def audit_row(row: dict[str, Any]) -> dict[str, Any]:
    block = str(row.get("balance_block"))
    is_trans = block == "translational_newton_balance"
    body = int(row.get("body"))
    if is_trans:
        accepted_law = "m_b a_b - m_b g - f_ext,b - f_joint,b(lambda) = 0"
        identity_id = "translational_balance_identity"
        identity_label = "D1"
    else:
        accepted_law = "J_b alpha_b + omega_b x J_b omega_b - tau_ext,b - tau_joint,b(lambda) = 0"
        identity_id = "rotational_balance_identity"
        identity_label = "D2"
    return {
        "global_row": row.get("global_row"),
        "stage": row.get("stage"),
        "body": body,
        "component": row.get("component"),
        "balance_block": block,
        "identity_id": identity_id,
        "identity_label": identity_label,
        "accepted_balance_law": accepted_law,
        "runtime_source_component": row.get("runtime_source_component"),
        "local_block_row": row.get("local_block_row"),
        "runtime_template_instantiation_checked": row.get("runtime_template_instantiation_checked") is True,
        "body_specific_wrench_expansion_checked": row.get("body_specific_wrench_expansion_checked") is True,
        "template_algebraic_equivalence_checked": row.get("template_algebraic_equivalence_checked") is True,
        "template_simplified_difference": row.get("template_algebraic_equivalence", {}).get(
            "simplified_difference"
        ),
        "multiplier_wrench_consistency_closed": row.get("multiplier_wrench_consistency_closed") is True,
        "smooth_force_lift_consistency_closed": row.get("smooth_force_lift_consistency_closed") is True,
        "row_ordering_scaling_ad_equivalence_closed": row.get(
            "row_ordering_scaling_ad_equivalence_closed"
        )
        is True,
        "runtime_row_equivalence_proved": row.get("runtime_row_equivalence_proved") is True,
        "balance_identity_closed": row_identity_closed(row),
        "stage_residual_O_h7_implementation_defect_proved": False,
        "scope": (
            "source-level Newton-Euler balance identity closed for this row; "
            "the D5 lifted-stage O(h^7) dynamic-defect rate remains open"
        ),
    }


def main() -> None:
    certificate = read_json(PAPER / "NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.json")
    virtual_work = read_json(PAPER / "NEWTON_EULER_VIRTUAL_WORK_WRENCH_AUDIT.json")
    smooth_force = read_json(PAPER / "SMOOTH_FORCE_LIFT_CERTIFICATE.json")
    row_ordering = read_json(PAPER / "NEWTON_EULER_ROW_ORDERING_SCALING_AD_AUDIT.json")

    rows = [audit_row(row) for row in certificate.get("row_certificates", [])]
    translational_rows = [row for row in rows if row["identity_id"] == "translational_balance_identity"]
    rotational_rows = [row for row in rows if row["identity_id"] == "rotational_balance_identity"]
    closed_rows = [row for row in rows if row["balance_identity_closed"]]
    closed_trans = [row for row in translational_rows if row["balance_identity_closed"]]
    closed_rot = [row for row in rotational_rows if row["balance_identity_closed"]]

    translational_closed = len(translational_rows) == len(closed_trans) == 18
    rotational_closed = len(rotational_rows) == len(closed_rot) == 18
    all_closed = translational_closed and rotational_closed and len(closed_rows) == 36

    result = {
        "schema": "newton-euler-balance-identity-audit-v1",
        "status": (
            "d1_d2_balance_identities_closed_d5_dynamic_defect_open"
            if all_closed
            else "d1_d2_balance_identities_incomplete"
        ),
        "accepted_method": "Gauss6/FullVA",
        "accepted_residual": "residual_cylindrical_chain",
        "row_family": "newton_euler_weak_balance",
        "submission_ready": False,
        "proof_gap_closed": False,
        "dynamic_symbolic_oracle_complete": False,
        "stage_residual_O_h7_implementation_defect_proved": False,
        "scope_note": (
            "D1/D2-only balance audit. The false D5 and stage-residual booleans mean "
            "not proved by this audit alone. Current theorem-level D5/direct-route "
            "status is determined by D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE and "
            "NEWTON_EULER_DYNAMIC_ROW_CLOSURE_CONTRACT; the optional symbolic/primitive "
            "certificate route remains separate."
        ),
        "current_d5_direct_route_authorities": [
            "D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE.json",
            "NEWTON_EULER_DYNAMIC_ROW_CLOSURE_CONTRACT.json",
        ],
        "translational_balance_identity_closed": translational_closed,
        "rotational_balance_identity_closed": rotational_closed,
        "balance_identity_closed": all_closed,
        "closed_obligation_ids": [
            "translational_balance_identity",
            "rotational_balance_identity",
        ]
        if all_closed
        else [],
        "summary": {
            "row_count": len(rows),
            "balance_identity_closed_rows": len(closed_rows),
            "translational_row_count": len(translational_rows),
            "translational_balance_identity_closed_rows": len(closed_trans),
            "rotational_row_count": len(rotational_rows),
            "rotational_balance_identity_closed_rows": len(closed_rot),
            "template_algebraic_equivalence_closed_rows": sum(
                row["template_algebraic_equivalence_checked"] for row in rows
            ),
            "runtime_template_instantiation_closed_rows": sum(
                row["runtime_template_instantiation_checked"] for row in rows
            ),
            "body_specific_wrench_expansion_closed_rows": sum(
                row["body_specific_wrench_expansion_checked"] for row in rows
            ),
            "multiplier_wrench_consistency_closed_rows": sum(
                row["multiplier_wrench_consistency_closed"] for row in rows
            ),
            "smooth_force_lift_consistency_closed_rows": sum(
                row["smooth_force_lift_consistency_closed"] for row in rows
            ),
            "row_ordering_scaling_ad_closed_rows": sum(
                row["row_ordering_scaling_ad_equivalence_closed"] for row in rows
            ),
            "runtime_row_equivalence_closed_rows": sum(row["runtime_row_equivalence_proved"] for row in rows),
            "d5_dynamic_defect_rate_closed": False,
        },
        "required_inputs": {
            "symbolic_defect_certificate": "NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.json",
            "virtual_work_wrench_audit": "NEWTON_EULER_VIRTUAL_WORK_WRENCH_AUDIT.json",
            "smooth_force_lift_certificate": "SMOOTH_FORCE_LIFT_CERTIFICATE.json",
            "row_ordering_scaling_ad_audit": "NEWTON_EULER_ROW_ORDERING_SCALING_AD_AUDIT.json",
        },
        "input_closure_checks": {
            "d3_multiplier_wrench_consistency_closed": virtual_work.get(
                "multiplier_wrench_consistency_closed"
            )
            is True,
            "d4_smooth_force_lift_consistency_closed": smooth_force.get(
                "smooth_force_lift_consistency_closed"
            )
            is True,
            "d4_global_C7_tube_derivative_bound_proved": smooth_force.get(
                "global_C7_tube_derivative_bound_proved"
            )
            is True,
            "d6_symbolic_runtime_row_equivalence_closed": row_ordering.get(
                "symbolic_runtime_row_equivalence_closed"
            )
            is True,
        },
        "closure_boundary": {
            "closes": [
                "D1 translational balance identity",
                "D2 rotational balance identity",
            ]
            if all_closed
            else [],
            "does_not_close": [
                "D5 Gauss-stage dynamic defect rate",
                "stage_residual_O_h7_implementation_defect_proved",
                "dynamic_symbolic_oracle_complete",
                "submission_ready",
            ],
            "scope": (
                "The audit closes the source-level Newton-Euler balance identities by combining "
                "runtime-template instantiation, body-specific sign expansion, scalar symbolic "
                "template equality, D3 multiplier-wrench consistency, D4 smooth force lift, "
                "and D6 row-ordering/scaling/AD binding.  It does not substitute the lifted "
                "Gauss solution into the dynamic rows and therefore does not prove D5 by "
                "itself. The current direct D5 theorem status is supplied elsewhere by "
                "D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE and "
                "NEWTON_EULER_DYNAMIC_ROW_CLOSURE_CONTRACT."
            ),
        },
        "row_audit": rows,
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# Newton-Euler Balance Identity Audit",
        "",
        f"Status: **{result['status']}**.",
        "",
        f"Scope note: {result['scope_note']}",
        "",
        f"- Row family: `{result['row_family']}`.",
        f"- Rows checked: `{result['summary']['row_count']}`.",
        f"- Balance identity closed rows: `{result['summary']['balance_identity_closed_rows']}`.",
        f"- Translational D1 rows closed: `{result['summary']['translational_balance_identity_closed_rows']}/{result['summary']['translational_row_count']}`.",
        f"- Rotational D2 rows closed: `{result['summary']['rotational_balance_identity_closed_rows']}/{result['summary']['rotational_row_count']}`.",
        f"- Template algebraic equivalence rows: `{result['summary']['template_algebraic_equivalence_closed_rows']}`.",
        f"- Runtime-template instantiation rows: `{result['summary']['runtime_template_instantiation_closed_rows']}`.",
        f"- Body-specific wrench-expansion rows: `{result['summary']['body_specific_wrench_expansion_closed_rows']}`.",
        f"- D3 multiplier-wrench consistency rows: `{result['summary']['multiplier_wrench_consistency_closed_rows']}`.",
        f"- D4 smooth force-lift consistency rows: `{result['summary']['smooth_force_lift_consistency_closed_rows']}`.",
        f"- D6 row-ordering/scaling/AD rows: `{result['summary']['row_ordering_scaling_ad_closed_rows']}`.",
        f"- D5 dynamic defect rate closed: `{result['summary']['d5_dynamic_defect_rate_closed']}`.",
        f"- Stage residual O(h^7) implementation defect proved: `{result['stage_residual_O_h7_implementation_defect_proved']}`.",
        f"- Submission ready: `{result['submission_ready']}`.",
        "",
        "## Boundary",
        "",
        result["closure_boundary"]["scope"],
        "",
        "## Row Evidence",
        "",
        "| row | stage | body | component | identity | closed | simplified difference |",
        "|---:|---:|---:|---|---|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['global_row']} | {row['stage']} | {row['body']} | {row['component']} | "
            f"{row['identity_label']} | `{row['balance_identity_closed']}` | "
            f"`{row['template_simplified_difference']}` |"
        )
    lines.extend(
        [
            "",
            "## Non-Closure",
            "",
            "This audit is not a dynamic-defect certificate.  The D5 proof must still "
            "substitute the lifted Gauss stage into the assembled dynamic rows and prove "
            "the residual is `O(h^7)`.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("newton_euler_balance_identity_audit=written")
    print(f"translational_balance_identity_closed={translational_closed}")
    print(f"rotational_balance_identity_closed={rotational_closed}")
    print("stage_residual_O_h7_implementation_defect_proved=False")
    print("proof_gap_closed=False")


if __name__ == "__main__":
    main()
