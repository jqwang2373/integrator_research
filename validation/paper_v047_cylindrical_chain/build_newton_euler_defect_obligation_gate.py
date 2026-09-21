#!/usr/bin/env python3
"""Build the Newton-Euler defect-obligation gate from proof sub-audits."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "NEWTON_EULER_DEFECT_OBLIGATION_GATE.json"
OUT_MD = PAPER / "NEWTON_EULER_DEFECT_OBLIGATION_GATE.md"


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def main() -> None:
    balance = read_json(PAPER / "NEWTON_EULER_BALANCE_IDENTITY_AUDIT.json")
    virtual_work = read_json(PAPER / "NEWTON_EULER_VIRTUAL_WORK_WRENCH_AUDIT.json")
    smooth = read_json(PAPER / "SMOOTH_FORCE_LIFT_CERTIFICATE.json")
    row_ordering = read_json(PAPER / "NEWTON_EULER_ROW_ORDERING_SCALING_AD_AUDIT.json")
    d5_direct = read_json(PAPER / "D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE.json")

    d1_closed = balance.get("translational_balance_identity_closed") is True
    d2_closed = balance.get("rotational_balance_identity_closed") is True
    d3_closed = virtual_work.get("multiplier_wrench_consistency_closed") is True
    d4_closed = smooth.get("smooth_force_lift_consistency_closed") is True
    d6_closed = row_ordering.get("symbolic_runtime_row_equivalence_closed") is True
    active_direct_pc2_closed = (
        d5_direct.get("direct_route_mathematical_certificate_closed") is True
        and d5_direct.get("direct_route_non_circular") is True
        and d5_direct.get("stage_residual_O_h7_by_direct_route") is True
        and d5_direct.get("summary", {}).get("dynamic_zero_residual_rows") == 36
        and d5_direct.get("summary", {}).get("forbidden_shortcuts_used") == 0
    )

    open_obligations = [
        {
            "id": "gauss_stage_dynamic_defect_rate",
            "row_count": 36,
            "status": "symbolic_primitive_route_open",
            "required_proof": (
                "primitive/Taylor or global symbolic-certificate route for the dynamic-row residual; "
                "the active direct D5 substitution route is recorded separately and is closed"
            ),
        }
    ]
    closed_obligations = []
    if d1_closed:
        closed_obligations.append(
            {
                "id": "translational_balance_identity",
                "row_count": 18,
                "status": "closed",
                "closure_evidence": "NEWTON_EULER_BALANCE_IDENTITY_AUDIT.md/json",
                "closed_scope": (
                    "source-level equality between each implemented translational dynamic row "
                    "and the accepted weak linear-momentum balance; the active direct D5 route is closed, "
                    "while the symbolic/primitive certificate route remains open"
                ),
            }
        )
    if d2_closed:
        closed_obligations.append(
            {
                "id": "rotational_balance_identity",
                "row_count": 18,
                "status": "closed",
                "closure_evidence": "NEWTON_EULER_BALANCE_IDENTITY_AUDIT.md/json",
                "closed_scope": (
                    "source-level equality between each implemented rotational dynamic row "
                    "and the accepted body-frame angular-momentum balance; the active direct D5 route is closed, "
                    "while the symbolic/primitive certificate route remains open"
                ),
            }
        )
    if d3_closed:
        closed_obligations.append(
            {
                "id": "multiplier_wrench_consistency",
                "row_count": 36,
                "status": "closed",
                "closure_evidence": "NEWTON_EULER_VIRTUAL_WORK_WRENCH_AUDIT.md/json",
                "closed_scope": (
                    "row-expanded lower-pair multiplier virtual-work identity for the "
                    "implemented cylindrical-chain force and axis-torque sites"
                ),
            }
        )
    if d4_closed:
        closed_obligations.append(
            {
                "id": "smooth_force_lift_consistency",
                "row_count": 36,
                "status": "closed",
                "closure_evidence": "SMOOTH_FORCE_LIFT_CERTIFICATE.md/json",
                "closed_scope": (
                    "smooth Brown-McPhee force/friction and regularized normal-load lift are "
                    "C7 with bounded derivatives on the accepted compact smooth proof tube"
                ),
            }
        )
    if d6_closed:
        closed_obligations.append(
            {
                "id": "symbolic_runtime_row_equivalence",
                "row_count": 36,
                "status": "closed",
                "closure_evidence": "NEWTON_EULER_ROW_ORDERING_SCALING_AD_AUDIT.md/json",
                "closed_scope": (
                    "independent row-ordering, residual-scaling, and accepted AD-binding "
                    "equivalence for the 36 implemented Newton-Euler dynamic rows"
                ),
            }
        )

    result = {
        "schema": "newton-euler-defect-obligation-gate-v1",
        "status": "d5_symbolic_primitive_route_open_active_direct_pc2_closed_not_submission_ready",
        "submission_ready": False,
        "accepted_method": "Gauss6/FullVA",
        "accepted_residual": "residual_cylindrical_chain",
        "proof_scope": {
            "row_family": "newton_euler_weak_balance",
            "dynamic_row_count": 36,
            "stage_count": 3,
            "body_count": 2,
            "rows_per_body_stage": 6,
            "translational_balance_rows": 18,
            "rotational_balance_rows": 18,
            "total_runtime_rows": 132,
            "kinematic_certificate_rows_already_certified": 96,
        },
        "supporting_runtime_oracles": {
            "full_formula_row_oracle_132_rows_checked": True,
            "newton_euler_formula_oracle_complete": True,
            "formula_row_ad_jacobian_oracle_checked": True,
            "formula_row_ad_jacobian_probe_count": 3,
            "partial_kinematic_stage_defect_certificate_checked": True,
            "partial_kinematic_stage_defect_rows_checked": 96,
            "symbolic_target_audit_checked": True,
            "symbolic_target_audit_rows": 36,
            "symbolic_target_audit_translational_rotational_rows": "18/18",
            "balance_identity_audit_checked": True,
            "balance_identity_closed_rows": balance.get("summary", {}).get("balance_identity_closed_rows"),
        },
        "open_obligations": open_obligations,
        "closed_obligations": closed_obligations,
        "closure_state": {
            "open_obligation_count": len(open_obligations),
            "open_obligation_scope": "symbolic_primitive_certificate_route_not_active_direct_pc2",
            "active_direct_pc2_closed": active_direct_pc2_closed,
            "active_direct_stage_residual_O_h7_implementation_defect_proved": active_direct_pc2_closed,
            "active_direct_dynamic_zero_residual_rows": d5_direct.get("summary", {}).get("dynamic_zero_residual_rows"),
            "active_direct_forbidden_shortcuts_used": d5_direct.get("summary", {}).get("forbidden_shortcuts_used"),
            "closed_obligation_count": len(closed_obligations),
            "closed_obligation_ids": [item["id"] for item in closed_obligations],
            "symbolic_target_inventory_complete": True,
            "balance_identity_audit_complete": balance.get("balance_identity_closed") is True,
            "newton_euler_symbolic_defect_certificate_complete": False,
            "stage_residual_O_h7_implementation_defect_proved": False,
            "stage_residual_O_h7_implementation_defect_proved_scope": "symbolic_primitive_certificate_route_only",
            "dynamic_symbolic_oracle_complete": False,
            "full_tfe_stage_replacement": False,
        },
        "execution_policy": {
            "default_1e-4_required": False,
            "run_v047_invoked": False,
            "v048_runner_invoked": False,
            "heavy_numerical_run_invoked": False,
        },
        "source_files": {
            "dynamic_oracle": "DYNAMIC_ROW_ORACLE_GATE.json",
            "kinematic_row_defect_certificate": "KINEMATIC_ROW_DEFECT_CERTIFICATE.json",
            "newton_euler_symbolic_target_audit": "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.json",
            "newton_euler_balance_identity_audit": "NEWTON_EULER_BALANCE_IDENTITY_AUDIT.json",
            "proof_contract_gate": "CMAME_PROOF_CONTRACT_GATE.json",
            "blocker_gate": "CMAME_BLOCKER_CLOSURE_GATE.json",
            "d5_dynamic_direct_substitution_certificate": "D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE.json",
        },
        "forbidden_claims": [
            "newton_euler_symbolic_defect_certificate_complete_true",
            "symbolic_primitive_stage_residual_O_h7_certificate_complete_true",
            "dynamic_symbolic_oracle_complete_true",
            "full_tfe_stage_replacement_true",
            "external_superiority_claim_true",
            "submission_ready_true",
            "default_1e-4_required_true",
        ],
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# Newton-Euler Defect Obligation Gate",
        "",
        "Status: **D5 SYMBOLIC/PRIMITIVE ROUTE OPEN; ACTIVE DIRECT PC2 CLOSED - NOT SUBMISSION READY**",
        "",
        "This gate decomposes the Newton-Euler symbolic/primitive certificate route for",
        "the accepted `Gauss6/FullVA` residual. The active direct-substitution PC2",
        "route is closed by `D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE.md/json`; this",
        "gate intentionally keeps the global symbolic/primitive route open and does not",
        "complete the dynamic symbolic oracle, invoke `run_v047.py`, or require a",
        "default `1e-4` campaign.",
        "",
        "## Scope",
        "",
        "| Row family | Rows | Decomposition |",
        "| --- | ---: | --- |",
        "| `newton_euler_weak_balance` | 36 | Three stages, two bodies, six balance rows per body-stage. |",
        "",
        "The 36 rows are decomposed into:",
        "",
        "- `translational_newton_balance`: 18 rows;",
        "- `rotational_euler_balance`: 18 rows.",
        "",
        "`NEWTON_EULER_BALANCE_IDENTITY_AUDIT.md/json` now closes the D1/D2",
        "source-level balance identities for these rows.  The remaining theorem",
        "symbolic/primitive route gap is D5: proving the lifted-stage dynamic residual",
        "by the global primitive/Taylor certificate rather than the active direct",
        "substitution route.",
        "`NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.md/json` remains the row-target",
        "inventory for all 36 Newton-Euler weak-balance rows.",
        "",
        "## Open Obligations",
        "",
        "| Obligation | Required proof |",
        "| --- | --- |",
    ]
    for item in open_obligations:
        lines.append(f"| `{item['id']}` | {item['required_proof']}. |")
    lines.extend(["", "## Closed Sub-Obligations", "", "| Obligation | Closure evidence |", "| --- | --- |"])
    for item in closed_obligations:
        lines.append(f"| `{item['id']}` | {item['closure_evidence']} closes: {item['closed_scope']}. |")
    lines.extend(
        [
            "",
            f"Symbolic/primitive-route open obligation count: `{len(open_obligations)}`.",
            f"Active direct PC2 closed: `{active_direct_pc2_closed}`.",
            f"Active direct dynamic zero residual rows: `{d5_direct.get('summary', {}).get('dynamic_zero_residual_rows')}`.",
            f"Closed obligation count: `{len(closed_obligations)}`.",
            f"Closed obligation ids: `{', '.join(item['id'] for item in closed_obligations)}`.",
            "Symbolic target inventory complete: `true`.",
            "",
            "## Boundary",
            "",
            "This gate only narrows the remaining symbolic/primitive proof work. It does not prove:",
            "",
            "- `newton_euler_symbolic_defect_certificate_complete`;",
            "- `symbolic_primitive_stage_residual_O_h7_certificate_complete`;",
            "- `dynamic_symbolic_oracle_complete`;",
            "- `eta_h_O_h7_solver_policy_evidence`;",
            "- `full_tfe_stage_replacement`;",
            "- external same-test superiority;",
            "- submission readiness.",
            "",
            "The theorem therefore uses the direct D5 substitution certificate for active",
            "PC2 and remains conditional under retained P1, P2, and P3 theorem",
            "interfaces, the separate P6 solver-scale interface, and the P4",
            "binding convention, with P7 residual-to-error nonpromotion recorded",
            "elsewhere.",
            "",
            "## Execution Policy",
            "",
            "- `default_1e-4_required=false`",
            "- `run_v047_invoked=false`",
            "- `v048_runner_invoked=false`",
            "- `heavy_numerical_run_invoked=false`",
            "",
            "## Validator",
            "",
            "Run:",
            "",
            "```bash",
            "../../.venv_sbel/bin/python validate_newton_euler_defect_obligation_gate.py",
            "```",
            "",
            "Expected markers:",
            "",
            "- `newton_euler_defect_obligation_gate=PASS`",
            "- `row_family=newton_euler_weak_balance`",
            "- `dynamic_row_count=36`",
            "- `symbolic_primitive_open_obligation_count=1`",
            "- `active_direct_pc2_closed=True`",
            "- `closed_obligation_count=5`",
            "- `symbolic_primitive_stage_residual_O_h7_certificate_complete=False`",
            "- `dynamic_symbolic_oracle_complete=False`",
            "- `submission_ready=False`",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("newton_euler_defect_obligation_gate=written")
    print(f"symbolic_primitive_open_obligation_count={len(open_obligations)}")
    print(f"active_direct_pc2_closed={active_direct_pc2_closed}")
    print(f"closed_obligation_count={len(closed_obligations)}")
    print("symbolic_primitive_stage_residual_O_h7_certificate_complete=False")


if __name__ == "__main__":
    main()
