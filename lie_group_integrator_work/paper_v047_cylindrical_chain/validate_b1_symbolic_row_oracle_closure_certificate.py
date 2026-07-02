#!/usr/bin/env python3
"""Validate the narrow B1 symbolic row-oracle closure certificate."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
CERT_JSON = PAPER / "B1_SYMBOLIC_ROW_ORACLE_CLOSURE_CERTIFICATE.json"
CERT_MD = PAPER / "B1_SYMBOLIC_ROW_ORACLE_CLOSURE_CERTIFICATE.md"


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
        certificate = read_json(CERT_JSON)
        certificate_md = read_text(CERT_MD)
        defect_certificate = read_json(PAPER / "NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.json")
        ad_expanded_audit = read_json(PAPER / "NEWTON_EULER_AD_EXPANDED_ROW_ORACLE_AUDIT.json")
        proof_remaining = read_json(PAPER / "PROOF_REMAINING_WORK_MANIFEST.json")
    except Exception as exc:  # noqa: BLE001
        print(f"b1 symbolic row-oracle closure certificate: FAIL\n- {exc}")
        return 1

    defect_summary = defect_certificate.get("summary", {})
    cert_defect_summary = certificate.get("defect_certificate_summary", {})
    ad_summary = certificate.get("ad_expanded_row_oracle_audit", {})
    rows = certificate.get("row_closures", [])

    checks.check(
        certificate.get("schema") == "b1-symbolic-row-oracle-closure-certificate-v1",
        "schema changed",
    )
    checks.check(
        certificate.get("status")
        == "independent_symbolic_row_oracle_closed_ad_expanded_symbolic_oracle_open",
        "status changed",
    )
    checks.check(certificate.get("submission_ready") is False, "certificate overclaims submission readiness")
    checks.check(certificate.get("accepted_method") == "Gauss6/FullVA", "accepted method changed")
    checks.check(certificate.get("row_family") == "newton_euler_weak_balance", "row family changed")
    checks.check(certificate.get("row_count") == 36, "row count changed")
    checks.check(
        certificate.get("independent_symbolic_row_by_row_oracle_for_expanded_fullva_rows_closed") is True,
        "independent symbolic row-oracle item not closed",
    )
    checks.check(
        certificate.get("independent_symbolic_row_by_row_oracle_closed_rows") == 36,
        "closed symbolic row count changed",
    )
    checks.check(certificate.get("source_template_symbolic_identity_rows") == 36, "source identity rows changed")
    checks.check(certificate.get("runtime_row_binding_checked_rows") == 36, "runtime binding rows changed")
    checks.check(
        certificate.get("ad_expanded_runtime_formula_binding_checked_rows") == 36,
        "AD-expanded runtime binding rows changed",
    )
    checks.check(certificate.get("residual_row_identity_scope_only") is True, "scope boundary missing")
    checks.check(
        certificate.get("ad_expanded_derivative_symbolic_scope_closed") is False,
        "certificate overclaims AD derivative symbolic scope",
    )
    checks.check(
        certificate.get("ad_expanded_symbolic_oracle_closure") is False,
        "certificate overclaims AD-expanded symbolic closure",
    )
    checks.check(
        certificate.get("dynamic_symbolic_oracle_complete") is False,
        "certificate overclaims dynamic symbolic oracle",
    )
    checks.check(
        certificate.get("stage_residual_O_h7_symbolic_certificate_proved") is False,
        "certificate overclaims symbolic-certificate O(h^7) proof",
    )
    checks.check(
        certificate.get("stage_residual_O_h7_implementation_defect_proved_from_this_certificate") is False,
        "certificate overclaims implementation-defect proof from this lane",
    )
    checks.check(
        certificate.get("proof_gap_closed_by_this_certificate") is False,
        "certificate overclaims proof gap closure",
    )
    checks.check(
        certificate.get("newton_euler_symbolic_defect_certificate_complete")
        == defect_certificate.get("certificate_complete")
        is False,
        "source symbolic defect certificate completion changed",
    )
    checks.check(
        certificate.get("newton_euler_symbolic_defect_certificate_certified_rows")
        == defect_summary.get("certified_row_count")
        == 0,
        "source symbolic defect certified row count changed",
    )
    checks.check(
        certificate.get("newton_euler_symbolic_defect_certificate_open_rows")
        == defect_summary.get("open_row_count")
        == 36,
        "source symbolic defect open row count changed",
    )
    checks.check(
        certificate.get("newton_euler_symbolic_defect_certificate_proof_gap_closed")
        == defect_certificate.get("proof_gap_closed")
        is False,
        "source symbolic defect proof gap changed",
    )
    checks.check(
        certificate.get("proof_remaining_work_status") == proof_remaining.get("status"),
        "proof remaining-work status not sourced",
    )
    checks.check(
        certificate.get("direct_route_O_h7_proof_recorded_elsewhere")
        == proof_remaining.get("stage_residual_O_h7_direct_route_proved")
        is True,
        "direct-route proof boundary not reflected",
    )

    for key, expected in [
        ("pc1_symbolic_row_oracle_closed", True),
        ("c1_row_expansion_closed", True),
        ("c2_runtime_equivalence_closed", True),
        ("c2_template_algebraic_equivalence_closed", True),
        ("symbolic_expanded_row_count", 36),
        ("runtime_mapped_row_count", 36),
        ("runtime_template_instantiation_checked_rows", 36),
        ("template_algebraic_equivalence_checked_rows", 36),
        ("body_specific_wrench_expansion_checked_rows", 36),
        ("virtual_work_template_identity_rows", 36),
        ("row_expanded_virtual_work_identity_rows", 36),
        ("balance_identity_closed_rows", 36),
        ("smooth_force_lift_consistency_closed", True),
        ("row_ordering_scaling_ad_equivalence_closed", True),
        ("certificate_complete", False),
        ("certified_row_count", 0),
        ("open_row_count", 36),
        ("proof_gap_closed", False),
    ]:
        checks.check(cert_defect_summary.get(key) == expected, f"defect summary changed: {key}")
        if key in defect_summary:
            checks.check(defect_summary.get(key) == expected, f"source defect summary changed: {key}")

    checks.check(
        ad_summary.get("status") == ad_expanded_audit.get("status"),
        "AD-expanded audit status not sourced",
    )
    checks.check(
        ad_summary.get("ad_expanded_row_oracle_closed")
        == ad_expanded_audit.get("ad_expanded_row_oracle_closed")
        is True,
        "AD-expanded row oracle closure changed",
    )
    checks.check(
        ad_summary.get("ad_expanded_row_oracle_rows")
        == ad_expanded_audit.get("ad_expanded_row_oracle_rows")
        == 36,
        "AD-expanded row count changed",
    )
    checks.check(
        ad_summary.get("ad_expanded_row_oracle_columns_per_row")
        == ad_expanded_audit.get("ad_expanded_row_oracle_columns_per_row")
        == 132,
        "AD-expanded column count changed",
    )
    checks.check(
        ad_summary.get("formula_row_ad_jacobian_probe_count")
        == ad_expanded_audit.get("formula_row_ad_jacobian_probe_count")
        == 3,
        "AD-expanded probe count changed",
    )
    checks.check(
        float(ad_summary.get("formula_row_ad_jacobian_max_mismatch", 1.0)) <= 1.0e-12,
        "AD-expanded mismatch too large",
    )
    checks.check(
        ad_summary.get("ad_expanded_symbolic_oracle_closure")
        == ad_expanded_audit.get("ad_expanded_symbolic_oracle_closure")
        is False,
        "AD-expanded audit overclaims symbolic closure",
    )
    checks.check(
        ad_summary.get("independent_symbolic_row_by_row_oracle_closed")
        == ad_expanded_audit.get("independent_symbolic_row_by_row_oracle_closed")
        is False,
        "AD-expanded audit boundary changed",
    )
    checks.check(
        ad_summary.get("dynamic_symbolic_oracle_complete")
        == ad_expanded_audit.get("dynamic_symbolic_oracle_complete")
        is False,
        "AD-expanded audit overclaims dynamic symbolic oracle",
    )
    checks.check(
        ad_summary.get("stage_residual_O_h7_implementation_defect_proved")
        == ad_expanded_audit.get("stage_residual_O_h7_implementation_defect_proved")
        is False,
        "AD-expanded audit overclaims O(h^7) proof",
    )

    checks.check(len(rows) == 36, "row closure list length changed")
    expected_rows: list[int] = []
    for stage in range(3):
        expected_rows.extend(range(stage * 44 + 24, stage * 44 + 36))
    checks.check([row.get("global_row") for row in rows] == expected_rows, "global row order changed")
    for row in rows:
        global_row = row.get("global_row")
        for key in [
            "symbolic_expansion_present",
            "runtime_row_mapping_present",
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
            "runtime_formula_row_oracle_link_checked",
            "row_ordering_scaling_ad_equivalence_closed",
            "ad_expanded_runtime_formula_binding_checked",
            "source_template_symbolic_identity_closed",
            "runtime_row_binding_checked",
            "symbolic_row_oracle_closed",
        ]:
            checks.check(row.get(key) is True, f"row {global_row} missing closure field {key}")
        checks.check(row.get("defect_bound_O_h7_proved") is False, f"row {global_row} overclaims O(h^7)")
        checks.check("outside this row item" in row.get("scope", ""), f"row {global_row} scope boundary missing")

    forbidden = certificate.get("claim_policy", {}).get("forbidden_now", [])
    for token in [
        "AD_expanded_symbolic_oracle_closure",
        "dynamic_symbolic_oracle_complete",
        "stage_residual_O_h7_symbolic_certificate_proved",
        "stage_residual_O_h7_implementation_defect_proved_from_this_certificate",
        "newton_euler_symbolic_defect_certificate_complete",
        "submission_ready",
    ]:
        checks.check(token in forbidden, f"forbidden claim missing: {token}")

    for token in [
        "B1 Symbolic Row-Oracle Closure Certificate",
        "independent residual-row symbolic oracle closed; AD-expanded closure recorded in companion certificate",
        "Independent symbolic row-by-row oracle closed: `True`.",
        "Closed symbolic rows: `36/36`.",
        "Source/template symbolic identity rows: `36/36`.",
        "Runtime row binding checked rows: `36/36`.",
        "AD-expanded runtime formula binding checked rows: `36/36`.",
        "AD-expanded symbolic oracle closure by this certificate: `False`.",
        "Companion AD-expanded closure certificate closes the global B1 derivative-cell item: `True`.",
        "Dynamic symbolic oracle complete: `False`.",
        "O(h^7) symbolic-certificate proof closed by this certificate: `False`.",
        "Remaining item inside this certificate only: `AD_expanded_symbolic_oracle_closure`.",
        "validate_b1_symbolic_row_oracle_closure_certificate.py",
    ]:
        checks.check(token in certificate_md, f"certificate markdown missing token: {token}")

    if checks.errors:
        print("b1_symbolic_row_oracle_closure_certificate=FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("b1_symbolic_row_oracle_closure_certificate=PASS")
    print("closed_symbolic_rows=36")
    print("remaining_b1_required_item=AD_expanded_symbolic_oracle_closure")
    return 0


if __name__ == "__main__":
    sys.exit(main())
