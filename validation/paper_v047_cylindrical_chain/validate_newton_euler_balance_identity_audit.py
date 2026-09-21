#!/usr/bin/env python3
"""Validate the Newton-Euler D1/D2 balance-identity audit."""

from __future__ import annotations

import json
from pathlib import Path


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "NEWTON_EULER_BALANCE_IDENTITY_AUDIT.json"
AUDIT_MD = PAPER / "NEWTON_EULER_BALANCE_IDENTITY_AUDIT.md"


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def main() -> int:
    checks = Checks()
    audit = read_json(AUDIT_JSON)
    md = AUDIT_MD.read_text(encoding="utf-8", errors="replace")
    summary = audit.get("summary", {})
    rows = audit.get("row_audit", [])

    checks.check(audit.get("schema") == "newton-euler-balance-identity-audit-v1", "schema changed")
    checks.check(
        audit.get("status") == "d1_d2_balance_identities_closed_d5_dynamic_defect_open",
        "status changed",
    )
    checks.check(audit.get("row_family") == "newton_euler_weak_balance", "row family changed")
    checks.check(audit.get("translational_balance_identity_closed") is True, "D1 not closed")
    checks.check(audit.get("rotational_balance_identity_closed") is True, "D2 not closed")
    checks.check(audit.get("balance_identity_closed") is True, "balance identity not closed")
    checks.check(audit.get("stage_residual_O_h7_implementation_defect_proved") is False, "D5 overclaimed")
    checks.check(audit.get("proof_gap_closed") is False, "proof gap overclaimed")
    checks.check(audit.get("submission_ready") is False, "submission readiness overclaimed")
    checks.check(
        "not proved by this audit alone" in audit.get("scope_note", "")
        and "D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE" in audit.get("scope_note", "")
        and "NEWTON_EULER_DYNAMIC_ROW_CLOSURE_CONTRACT" in audit.get("scope_note", ""),
        "D1/D2 audit scope note missing current D5 authority boundary",
    )
    checks.check(
        audit.get("current_d5_direct_route_authorities")
        == [
            "D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE.json",
            "NEWTON_EULER_DYNAMIC_ROW_CLOSURE_CONTRACT.json",
        ],
        "current D5 direct-route authorities changed",
    )
    checks.check(summary.get("row_count") == 36, "row count changed")
    checks.check(summary.get("balance_identity_closed_rows") == 36, "closed row count changed")
    checks.check(summary.get("translational_row_count") == 18, "translational row count changed")
    checks.check(summary.get("rotational_row_count") == 18, "rotational row count changed")
    checks.check(
        summary.get("translational_balance_identity_closed_rows") == 18,
        "translational closed count changed",
    )
    checks.check(
        summary.get("rotational_balance_identity_closed_rows") == 18,
        "rotational closed count changed",
    )
    for key in [
        "template_algebraic_equivalence_closed_rows",
        "runtime_template_instantiation_closed_rows",
        "body_specific_wrench_expansion_closed_rows",
        "multiplier_wrench_consistency_closed_rows",
        "smooth_force_lift_consistency_closed_rows",
        "row_ordering_scaling_ad_closed_rows",
        "runtime_row_equivalence_closed_rows",
    ]:
        checks.check(summary.get(key) == 36, f"{key} changed")
    checks.check(summary.get("d5_dynamic_defect_rate_closed") is False, "D5 closure changed")
    checks.check(len(rows) == 36, "row audit count changed")
    checks.check(all(row.get("balance_identity_closed") is True for row in rows), "not all row identities closed")
    checks.check(
        {row.get("identity_id") for row in rows}
        == {"translational_balance_identity", "rotational_balance_identity"},
        "row identity ids changed",
    )
    checks.check(
        sum(row.get("identity_id") == "translational_balance_identity" for row in rows) == 18,
        "D1 row split changed",
    )
    checks.check(
        sum(row.get("identity_id") == "rotational_balance_identity" for row in rows) == 18,
        "D2 row split changed",
    )
    checks.check(
        all(row.get("template_simplified_difference") == "0" for row in rows),
        "nonzero template difference",
    )
    checks.check(
        set(audit.get("closed_obligation_ids", []))
        == {"translational_balance_identity", "rotational_balance_identity"},
        "closed obligation ids changed",
    )
    for token in [
        "Newton-Euler Balance Identity Audit",
        "d1_d2_balance_identities_closed_d5_dynamic_defect_open",
        "Translational D1 rows closed: `18/18`",
        "Rotational D2 rows closed: `18/18`",
        "D5 dynamic defect rate closed: `False`",
        "Scope note: D1/D2-only balance audit",
        "not proved by this audit alone",
        "Current theorem-level D5/direct-route status is determined by D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE",
        "This audit is not a dynamic-defect certificate",
    ]:
        checks.check(token in md, f"markdown missing token: {token}")

    if checks.errors:
        print("newton_euler_balance_identity_audit=FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1
    print("newton_euler_balance_identity_audit=PASS")
    print("translational_balance_identity_closed=True")
    print("rotational_balance_identity_closed=True")
    print("balance_identity_closed_rows=36")
    print("stage_residual_O_h7_implementation_defect_proved=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
