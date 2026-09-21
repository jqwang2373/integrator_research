#!/usr/bin/env python3
"""Validate the D6 row-ordering/scaling/AD audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "NEWTON_EULER_ROW_ORDERING_SCALING_AD_AUDIT.json"
AUDIT_MD = PAPER / "NEWTON_EULER_ROW_ORDERING_SCALING_AD_AUDIT.md"


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


def expected_global_rows() -> list[int]:
    rows: list[int] = []
    for stage in range(3):
        rows.extend(range(stage * 44 + 24, stage * 44 + 36))
    return rows


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(AUDIT_JSON)
        audit_md = AUDIT_MD.read_text(encoding="utf-8", errors="replace")
        target_audit = read_json(PAPER / "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.json")
        dynamic_oracle = read_json(PAPER / "DYNAMIC_ROW_ORACLE_GATE.json")
        proof_contract = read_json(PAPER / "CMAME_PROOF_CONTRACT_GATE.json")
        manifest = read_json(PAPER / "SUBMISSION_ARTIFACT_MANIFEST.json")
    except Exception as exc:  # noqa: BLE001
        print(f"newton_euler_row_ordering_scaling_ad_audit=FAIL\n- {exc}")
        return 1

    checks.check(
        audit.get("schema") == "newton-euler-row-ordering-scaling-ad-audit-v1",
        "schema changed",
    )
    checks.check(
        audit.get("status") == "d6_row_ordering_scaling_ad_closed_dynamic_defect_open",
        "status changed",
    )
    checks.check(audit.get("submission_ready") is False, "submission readiness overclaimed")
    checks.check(audit.get("proof_gap_closed") is False, "proof gap overclosed")
    checks.check(
        audit.get("proof_gap_closed_scope")
        == (
            "local_d6_row_ordering_scaling_ad_audit_only; this audit closes "
            "implementation layout/AD binding but not the D5 O(h^7) dynamic defect "
            "or the full direct D5/PC2 closure artifact"
        ),
        "D6 local proof-gap scope missing",
    )
    checks.check(
        "Local D6 audit proof gap closed" in audit_md
        and "Proof gap closed scope" in audit_md,
        "D6 proof-gap wording not scoped in markdown",
    )
    checks.check(
        audit.get("dynamic_symbolic_oracle_complete") is False,
        "dynamic symbolic oracle unexpectedly complete",
    )
    checks.check(
        audit.get("stage_residual_O_h7_implementation_defect_proved") is False,
        "dynamic O(h^7) defect overclaimed",
    )
    checks.check(
        audit.get("symbolic_runtime_row_equivalence_closed") is True,
        "D6 row-equivalence sub-obligation not closed",
    )
    checks.check(audit.get("row_ordering_scaling_ad_closed") is True, "D6 row ordering/scaling/AD not closed")
    checks.check(audit.get("accepted_residual") == "residual_cylindrical_chain", "accepted residual changed")

    layout = audit.get("row_layout", {})
    checks.check(layout.get("stage_size") == 44, "stage size changed")
    checks.check(layout.get("stage_count") == 3, "stage count changed")
    checks.check(layout.get("dynamic_offset") == 24, "dynamic offset changed")
    checks.check(layout.get("dynamic_width") == 12, "dynamic width changed")
    checks.check(layout.get("dynamic_rows") == 36, "dynamic row count changed")
    checks.check(
        layout.get("per_stage_order")
        == [
            "body0_translational_rows_0_2",
            "body0_rotational_rows_3_5",
            "body1_translational_rows_6_8",
            "body1_rotational_rows_9_11",
        ],
        "per-stage dynamic order changed",
    )

    for group_name in ["source_checks", "layout_checks", "ad_binding_checks"]:
        group = audit.get(group_name, {})
        checks.check(isinstance(group, dict) and group, f"{group_name} missing")
        checks.check(all(value is True for value in group.values()), f"{group_name} has a failed check")

    row_audit = audit.get("row_audit", [])
    checks.check(isinstance(row_audit, list) and len(row_audit) == 36, "row audit count changed")
    checks.check([row.get("global_row") for row in row_audit] == expected_global_rows(), "global row order changed")
    target_by_row = {
        row.get("global_row"): row
        for row in target_audit.get("row_targets", [])
        if isinstance(row, dict)
    }
    checks.check(len(target_by_row) == 36, "target audit row map incomplete")
    for row in row_audit:
        checks.check(row.get("proved") is True, f"row {row.get('global_row')} not proved")
        checks.check(all(row.get("checks", {}).values()), f"row {row.get('global_row')} check failed")
        target = target_by_row.get(row.get("global_row"), {})
        checks.check(row.get("target", {}).get("body") == target.get("body"), "target body mismatch")
        checks.check(
            row.get("target", {}).get("balance_block") == target.get("balance_block"),
            "target balance block mismatch",
        )
        local = int(row.get("local_dynamic_offset", -1))
        expected_block = (
            "translational_newton_balance"
            if local in {0, 1, 2, 6, 7, 8}
            else "rotational_euler_balance"
        )
        checks.check(row.get("expected", {}).get("balance_block") == expected_block, "expected block mismatch")

    formula_ad = dynamic_oracle.get("formula_row_ad_jacobian_oracle", {})
    theorem = proof_contract.get("theorem_contract", {})
    checks.check(formula_ad.get("checked") is True, "source formula-row AD oracle not checked")
    checks.check(formula_ad.get("probe_count") == 3, "source formula-row AD probe count changed")
    checks.check(
        formula_ad.get("relation_checked")
        == "jax.jacfwd(independent_formula_family_major_vector) equals accepted R_JAC in row-family-major order",
        "source AD relation changed",
    )
    checks.check(
        float(theorem.get("formula_row_ad_jacobian_max_mismatch", 1.0)) <= 1.0e-12,
        "source AD mismatch too large",
    )

    for token in [
        "Newton-Euler Row Ordering, Scaling, and AD Audit",
        "D6 CLOSED - row ordering, residual scaling, and AD binding are checked",
        "Symbolic runtime row-equivalence sub-obligation closed: `True`.",
        "Stage residual O(h^7) implementation defect proved: `False`.",
        "Dynamic offset/width: `24/12`.",
        "body0 translational, body0 rotational, body1 translational, body1 rotational",
        "closes only D6",
        "does not close the D1/D2 balance identities",
        "does not prove the D5 O(h^7) dynamic-row defect",
        "validate_newton_euler_row_ordering_scaling_ad_audit.py",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    checks.check(
        manifest.get("newton_euler_row_ordering_scaling_ad_audit")
        == "NEWTON_EULER_ROW_ORDERING_SCALING_AD_AUDIT.md",
        "manifest missing D6 audit MD path",
    )
    checks.check(
        manifest.get("newton_euler_row_ordering_scaling_ad_audit_json")
        == "NEWTON_EULER_ROW_ORDERING_SCALING_AD_AUDIT.json",
        "manifest missing D6 audit JSON path",
    )
    checks.check(
        "NEWTON_EULER_ROW_ORDERING_SCALING_AD_AUDIT.md" in manifest.get("evidence_anchors", []),
        "manifest missing D6 audit MD anchor",
    )
    checks.check(
        "NEWTON_EULER_ROW_ORDERING_SCALING_AD_AUDIT.json" in manifest.get("evidence_anchors", []),
        "manifest missing D6 audit JSON anchor",
    )
    checks.check(
        "validate_newton_euler_row_ordering_scaling_ad_audit.py" in manifest.get("validators", []),
        "manifest missing D6 audit validator",
    )

    if checks.errors:
        print("newton_euler_row_ordering_scaling_ad_audit=FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("newton_euler_row_ordering_scaling_ad_audit=PASS")
    print("symbolic_runtime_row_equivalence_closed=True")
    print("dynamic_rows=36")
    print("stage_residual_O_h7_implementation_defect_proved=False")
    print("local_d6_audit_proof_gap_closed=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
