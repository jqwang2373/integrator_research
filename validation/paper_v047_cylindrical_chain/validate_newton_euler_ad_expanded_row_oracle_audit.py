#!/usr/bin/env python3
"""Validate Newton-Euler AD-expanded row oracle coverage."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "NEWTON_EULER_AD_EXPANDED_ROW_ORACLE_AUDIT.json"
AUDIT_MD = PAPER / "NEWTON_EULER_AD_EXPANDED_ROW_ORACLE_AUDIT.md"


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


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(AUDIT_JSON)
        audit_md = read_text(AUDIT_MD)
        dynamic_oracle = read_json(PAPER / "DYNAMIC_ROW_ORACLE_GATE.json")
        target_audit = read_json(PAPER / "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.json")
        proof_contract = read_json(PAPER / "CMAME_PROOF_CONTRACT_GATE.json")
    except Exception as exc:  # noqa: BLE001
        print(f"newton_euler_ad_expanded_row_oracle_audit=FAIL\n- {exc}")
        return 1

    full_formula = dynamic_oracle.get("full_independent_formula_row_oracle", {})
    formula_ad = dynamic_oracle.get("formula_row_ad_jacobian_oracle", {})
    theorem = proof_contract.get("theorem_contract", {})
    rows = audit.get("row_ad_coverage", [])
    checks.check(audit.get("schema") == "newton-euler-ad-expanded-row-oracle-audit-v1", "schema changed")
    checks.check(
        audit.get("status") == "ad_expanded_runtime_formula_binding_complete_symbolic_oracle_open",
        "status changed",
    )
    checks.check(audit.get("submission_ready") is False, "audit overclaims submission readiness")
    checks.check(audit.get("row_family") == "newton_euler_weak_balance", "row family changed")
    checks.check(audit.get("row_count") == 36, "row count changed")
    checks.check(audit.get("translational_row_count") == 18, "translational row count changed")
    checks.check(audit.get("rotational_row_count") == 18, "rotational row count changed")
    checks.check(audit.get("formula_family_major_offset") == 72, "formula-family-major offset changed")
    checks.check(audit.get("ad_jacobian_column_count") == 132, "AD column count changed")
    checks.check(audit.get("formula_row_ad_jacobian_probe_count") == 3, "probe count changed")
    checks.check(audit.get("formula_row_ad_jacobian_probe_vectors") == formula_ad.get("probe_vectors"), "probe vector list mismatch")
    checks.check(
        audit.get("formula_row_ad_jacobian_max_mismatch")
        == theorem.get("formula_row_ad_jacobian_max_mismatch"),
        "max mismatch not sourced from proof contract",
    )
    checks.check(
        float(audit.get("formula_row_ad_jacobian_max_mismatch", 1.0)) <= 1.0e-12,
        "formula-row AD max mismatch too large",
    )
    checks.check(audit.get("full_formula_row_oracle_132_rows_checked") is True, "full formula oracle not checked")
    checks.check(
        audit.get("formula_row_ad_jacobian_oracle_132x132_checked") is True,
        "132x132 formula-row AD oracle not checked",
    )
    checks.check(audit.get("formula_row_ad_jacobian_multi_probe_checked") is True, "multi-probe AD oracle missing")
    checks.check(audit.get("runtime_ad_oracle_complete") is True, "runtime AD oracle missing")
    checks.check(audit.get("ad_expanded_row_oracle_closed") is True, "row-level AD binding not closed")
    checks.check(audit.get("ad_expanded_row_oracle_rows") == 36, "AD row coverage count changed")
    checks.check(audit.get("ad_expanded_row_oracle_columns_per_row") == 132, "AD columns per row changed")
    checks.check(audit.get("ad_expanded_symbolic_oracle_closure") is False, "audit overclaims symbolic closure")
    checks.check(
        audit.get("independent_symbolic_row_by_row_oracle_closed") is False,
        "audit overclaims independent symbolic row oracle",
    )
    checks.check(audit.get("dynamic_symbolic_oracle_complete") is False, "audit overclaims dynamic symbolic oracle")
    checks.check(
        audit.get("stage_residual_O_h7_implementation_defect_proved") is False,
        "audit overclaims O(h^7) dynamic defect",
    )
    checks.check(audit.get("proof_gap_closed") is False, "audit overclaims proof gap closure")
    checks.check(full_formula.get("row_count") == 132, "source full formula row count changed")
    checks.check(formula_ad.get("row_count") == 132 and formula_ad.get("column_count") == 132, "source AD shape changed")
    checks.check(target_audit.get("row_count") == 36, "source target audit row count changed")
    checks.check(len(rows) == 36, "row coverage list length changed")

    expected_formula_rows = list(range(72, 108))
    expected_accepted_rows: list[int] = []
    for stage in range(3):
        expected_accepted_rows.extend(range(stage * 44 + 24, stage * 44 + 36))
    checks.check(audit.get("formula_family_major_rows") == expected_formula_rows, "formula-major rows changed")
    checks.check(audit.get("accepted_residual_rows") == expected_accepted_rows, "accepted residual rows changed")

    target_by_row = {
        item.get("global_row"): item
        for item in target_audit.get("row_targets", [])
        if isinstance(item, dict)
    }
    for row in rows:
        global_row = row.get("global_row")
        target = target_by_row.get(global_row)
        checks.check(isinstance(target, dict), f"target audit missing row {global_row}")
        if isinstance(target, dict):
            checks.check(row.get("stage") == target.get("stage"), f"stage mismatch for row {global_row}")
            checks.check(row.get("body") == target.get("body"), f"body mismatch for row {global_row}")
            checks.check(row.get("component") == target.get("component"), f"component mismatch for row {global_row}")
            checks.check(row.get("local_block_row") == target.get("local_block_row"), f"local row mismatch for row {global_row}")
        checks.check(row.get("accepted_residual_row_covered") is True, f"accepted row not covered: {global_row}")
        checks.check(row.get("formula_family_major_row_covered") is True, f"formula-major row not covered: {global_row}")
        checks.check(row.get("ad_jacobian_columns_covered") == 132, f"AD columns changed for row {global_row}")
        checks.check(row.get("probe_count") == 3, f"probe count changed for row {global_row}")
        checks.check(row.get("row_ad_binding_checked") is True, f"row AD binding not checked: {global_row}")
        checks.check(
            "not a symbolic identity proof" in row.get("row_ad_binding_scope", ""),
            f"row scope boundary missing: {global_row}",
        )

    forbidden = audit.get("claim_policy", {}).get("forbidden_now", [])
    for token in [
        "independent_symbolic_row_by_row_oracle_closed",
        "ad_expanded_symbolic_oracle_closure",
        "dynamic_symbolic_oracle_complete",
        "stage_residual_O_h7_implementation_defect_proved",
        "proof_gap_closed",
        "submission_ready",
    ]:
        checks.check(token in forbidden, f"forbidden claim missing: {token}")

    for token in [
        "Newton-Euler AD-Expanded Row Oracle Audit",
        "AD-expanded runtime formula binding complete; symbolic oracle open",
        "AD-expanded row oracle closed: `True`.",
        "AD-expanded rows: `36/36`.",
        "AD columns per row: `132`.",
        "Formula-family-major offset: `72`.",
        "Formula-row AD Jacobian probes: `3`.",
        "AD-expanded symbolic oracle closure: `False`.",
        "Independent symbolic row-by-row oracle closed: `False`.",
        "Dynamic symbolic oracle complete: `False`.",
        "Stage residual O(h^7) implementation defect proved: `False`.",
        "not prove a symbolic identity",
        "validate_newton_euler_ad_expanded_row_oracle_audit.py",
    ]:
        checks.check(token in audit_md, f"audit markdown missing token: {token}")

    if checks.errors:
        print("newton_euler_ad_expanded_row_oracle_audit=FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("newton_euler_ad_expanded_row_oracle_audit=PASS")
    print("ad_expanded_rows=36")
    print("ad_columns_per_row=132")
    print("dynamic_symbolic_oracle_complete=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
