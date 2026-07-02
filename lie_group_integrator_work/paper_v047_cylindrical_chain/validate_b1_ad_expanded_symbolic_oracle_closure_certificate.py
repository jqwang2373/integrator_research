#!/usr/bin/env python3
"""Validate the B1 AD-expanded symbolic oracle closure certificate."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
CERT_JSON = PAPER / "B1_AD_EXPANDED_SYMBOLIC_ORACLE_CLOSURE_CERTIFICATE.json"
CERT_MD = PAPER / "B1_AD_EXPANDED_SYMBOLIC_ORACLE_CLOSURE_CERTIFICATE.md"
DERIVATIVE_COLUMNS_PER_ROW = 132


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
        cert = read_json(CERT_JSON)
        cert_md = read_text(CERT_MD)
        symbolic_row_oracle = read_json(PAPER / "B1_SYMBOLIC_ROW_ORACLE_CLOSURE_CERTIFICATE.json")
        ad_audit = read_json(PAPER / "NEWTON_EULER_AD_EXPANDED_ROW_ORACLE_AUDIT.json")
        defect_certificate = read_json(PAPER / "NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.json")
        proof_remaining = read_json(PAPER / "PROOF_REMAINING_WORK_MANIFEST.json")
    except Exception as exc:  # noqa: BLE001
        print(f"b1 AD-expanded symbolic oracle closure certificate: FAIL\n- {exc}")
        return 1

    rows = cert.get("row_closures", [])
    derivative_cell_count = 36 * DERIVATIVE_COLUMNS_PER_ROW

    checks.check(
        cert.get("schema") == "b1-ad-expanded-symbolic-oracle-closure-certificate-v1",
        "schema changed",
    )
    checks.check(
        cert.get("status") == "ad_expanded_symbolic_oracle_closed_without_o_h7_overclaim",
        "status changed",
    )
    checks.check(cert.get("submission_ready") is False, "certificate overclaims submission readiness")
    checks.check(cert.get("accepted_method") == "Gauss6/FullVA", "accepted method changed")
    checks.check(cert.get("row_family") == "newton_euler_weak_balance", "row family changed")
    checks.check(cert.get("row_count") == 36, "row count changed")
    checks.check(cert.get("columns_per_row") == DERIVATIVE_COLUMNS_PER_ROW, "column count changed")
    checks.check(cert.get("derivative_cell_count") == derivative_cell_count, "derivative cell count changed")
    checks.check(cert.get("ad_expanded_symbolic_oracle_closure") is True, "AD-expanded symbolic oracle not closed")
    checks.check(cert.get("ad_expanded_symbolic_oracle_closed_rows") == 36, "closed row count changed")
    checks.check(
        cert.get("ad_expanded_symbolic_oracle_closed_cells") == derivative_cell_count,
        "closed derivative cell count changed",
    )
    checks.check(
        cert.get("independent_symbolic_row_by_row_oracle_closed")
        == symbolic_row_oracle.get(
            "independent_symbolic_row_by_row_oracle_for_expanded_fullva_rows_closed"
        )
        is True,
        "independent symbolic row oracle source is not closed",
    )
    checks.check(
        cert.get("independent_symbolic_row_by_row_oracle_closed_rows")
        == symbolic_row_oracle.get("independent_symbolic_row_by_row_oracle_closed_rows")
        == 36,
        "independent symbolic row count changed",
    )
    checks.check(
        cert.get("ad_expanded_runtime_formula_binding_checked")
        == ad_audit.get("ad_expanded_row_oracle_closed")
        is True,
        "AD-expanded runtime binding source not closed",
    )
    checks.check(
        cert.get("ad_expanded_runtime_formula_binding_rows")
        == ad_audit.get("ad_expanded_row_oracle_rows")
        == 36,
        "AD-expanded runtime binding row count changed",
    )
    checks.check(
        cert.get("ad_expanded_runtime_formula_binding_columns_per_row")
        == ad_audit.get("ad_expanded_row_oracle_columns_per_row")
        == DERIVATIVE_COLUMNS_PER_ROW,
        "AD-expanded runtime binding column count changed",
    )
    checks.check(cert.get("formula_row_ad_jacobian_probe_count") == 3, "AD probe count changed")
    checks.check(
        float(cert.get("formula_row_ad_jacobian_max_mismatch", 1.0)) <= 1.0e-12,
        "AD runtime binding mismatch too large",
    )
    rule = cert.get("closure_rule", {})
    checks.check(rule.get("name") == "differentiate_closed_residual_identity_columnwise", "closure rule changed")
    checks.check(rule.get("not_finite_probe_proof") is True, "finite-probe boundary missing")
    checks.check(
        "coordinate derivative of the zero difference is zero" in rule.get("justification", ""),
        "chain-rule justification missing",
    )
    checks.check(cert.get("b1_blocker_closeable_by_this_certificate") is True, "B1 closeability marker missing")
    checks.check(cert.get("remaining_b1_required_items_after_this_certificate") == [], "B1 remaining items changed")
    checks.check(cert.get("dynamic_symbolic_oracle_complete") is False, "certificate overclaims global dynamic oracle")
    checks.check(
        cert.get("stage_residual_O_h7_symbolic_certificate_proved") is False,
        "certificate overclaims symbolic-certificate O(h^7) proof",
    )
    checks.check(
        cert.get("stage_residual_O_h7_implementation_defect_proved_from_this_certificate") is False,
        "certificate overclaims implementation-defect proof from this lane",
    )
    checks.check(cert.get("proof_gap_closed_by_this_certificate") is False, "certificate overclaims proof-gap closure")
    checks.check(
        cert.get("newton_euler_symbolic_defect_certificate_complete")
        == defect_certificate.get("certificate_complete")
        is False,
        "source symbolic defect certificate unexpectedly complete",
    )
    checks.check(
        cert.get("newton_euler_symbolic_defect_certificate_certified_rows")
        == defect_certificate.get("summary", {}).get("certified_row_count")
        == 0,
        "symbolic defect certified rows changed",
    )
    checks.check(
        cert.get("direct_route_O_h7_proof_recorded_elsewhere")
        == proof_remaining.get("stage_residual_O_h7_direct_route_proved")
        is True,
        "direct-route proof boundary not reflected",
    )

    expected_rows: list[int] = []
    for stage in range(3):
        expected_rows.extend(range(stage * 44 + 24, stage * 44 + 36))
    checks.check([row.get("global_row") for row in rows] == expected_rows, "global row order changed")
    checks.check(len(rows) == 36, "row closure list length changed")
    for row in rows:
        global_row = row.get("global_row")
        for key in [
            "source_residual_identity_closed",
            "runtime_row_binding_checked",
            "ad_expanded_runtime_formula_binding_checked",
            "smooth_tube_differentiability_available",
            "chain_rule_from_residual_identity_applied",
            "ad_expanded_symbolic_row_oracle_closed",
        ]:
            checks.check(row.get(key) is True, f"row {global_row} missing closure field {key}")
        checks.check(
            row.get("derivative_columns_covered") == DERIVATIVE_COLUMNS_PER_ROW,
            f"row {global_row} column count changed",
        )
        checks.check(
            row.get("derivative_cells_closed") == DERIVATIVE_COLUMNS_PER_ROW,
            f"row {global_row} derivative cells changed",
        )
        checks.check(row.get("defect_bound_O_h7_proved") is False, f"row {global_row} overclaims O(h^7)")
        checks.check(
            "differentiating that identity" in row.get("proof_rule", ""),
            f"row {global_row} proof rule missing",
        )

    forbidden = cert.get("claim_policy", {}).get("forbidden_now", [])
    for token in [
        "dynamic_symbolic_oracle_complete",
        "stage_residual_O_h7_symbolic_certificate_proved",
        "stage_residual_O_h7_implementation_defect_proved_from_this_certificate",
        "newton_euler_symbolic_defect_certificate_complete",
        "eta_h solver policy proved by finite probes",
        "submission_ready",
    ]:
        checks.check(token in forbidden, f"forbidden claim missing: {token}")

    for token in [
        "B1 AD-Expanded Symbolic Oracle Closure Certificate",
        "AD-expanded symbolic oracle closed for B1; no O(h^7) overclaim",
        "AD-expanded symbolic oracle closure: `True`.",
        "Closed rows: `36/36`.",
        "Columns per row: `132`.",
        "Closed derivative cells: `4752/4752`.",
        "Independent symbolic row oracle closed: `True`.",
        "AD-expanded runtime formula binding checked: `True`.",
        "Dynamic symbolic oracle complete: `False`.",
        "O(h^7) symbolic-certificate proof closed by this certificate: `False`.",
        "Differentiating the closed residual identity columnwise",
        "finite AD probes are implementation binding checks only",
        "validate_b1_ad_expanded_symbolic_oracle_closure_certificate.py",
    ]:
        checks.check(token in cert_md, f"certificate markdown missing token: {token}")

    if checks.errors:
        print("b1_ad_expanded_symbolic_oracle_closure_certificate=FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("b1_ad_expanded_symbolic_oracle_closure_certificate=PASS")
    print("closed_derivative_cells=4752/4752")
    print("ad_expanded_symbolic_oracle_closure=True")
    print("submission_ready=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
