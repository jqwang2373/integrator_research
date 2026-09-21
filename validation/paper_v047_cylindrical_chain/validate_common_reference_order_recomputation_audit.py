#!/usr/bin/env python3
"""Validate independent recomputation of common-reference orders."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path


PAPER = Path(__file__).resolve().parent


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


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(PAPER / "COMMON_REFERENCE_ORDER_RECOMPUTATION_AUDIT.json")
        audit_md = read_text(PAPER / "COMMON_REFERENCE_ORDER_RECOMPUTATION_AUDIT.md")
    except Exception as exc:  # noqa: BLE001
        print(f"common-reference order recomputation audit validation: FAIL\n- {exc}")
        return 1

    coverage = audit.get("coverage", {})
    verification = audit.get("verification", {})
    claim = audit.get("claim_boundary", {})
    anomalies = audit.get("anomalies", {})
    local_rows = [
        row
        for row in audit.get("rows", [])
        if isinstance(row, dict) and row.get("method") == "local_Gauss6_FullVA"
    ]

    checks.check(audit.get("schema") == "common-reference-order-recomputation-audit-v1", "schema changed")
    checks.check(audit.get("all_four_examples_audited") is True, "not all four examples audited")
    checks.check(audit.get("all_summary_orders_recomputed") is True, "summary orders not fully recomputed")
    checks.check(coverage.get("method_count") == 11, "method count changed")
    checks.check(coverage.get("example_count") == 4, "example count changed")
    checks.check(coverage.get("method_example_cell_count") == 44, "cell count changed")
    checks.check(coverage.get("expected_method_example_cell_count") == 44, "expected cell count changed")
    checks.check(coverage.get("expected_step_count_per_cell") == 3, "expected step count changed")
    checks.check(coverage.get("raw_ok_row_count") == 132, "raw ok row count changed")
    checks.check(coverage.get("summary_ok_row_count") == 44, "summary row count changed")
    checks.check(verification.get("mismatch_count") == 0, "summary/raw recomputation mismatch present")
    checks.check(float(verification.get("max_order_abs_diff", math.inf)) <= 1.0e-10, "order diff exceeds tolerance")
    checks.check(
        float(verification.get("max_finest_error_abs_diff", math.inf)) <= 1.0e-14,
        "finest-error diff exceeds tolerance",
    )
    checks.check(len(local_rows) == 4, "local row count changed")
    for row in local_rows:
        vel_order = float(row.get("recomputed", {}).get("vel_order", math.nan))
        checks.check(vel_order >= 5.5, f"local row order too low: {row.get('example')} {vel_order}")
        checks.check(row.get("status") == "match", f"local row recomputation mismatch: {row.get('example')}")
    checks.check(anomalies.get("anomaly_row_count", 0) >= 8, "expected anomaly interpretation rows missing")
    checks.check(claim.get("summary_arithmetic_verified") is True, "summary arithmetic boundary missing")
    checks.check(claim.get("external_superiority_allowed") is False, "external superiority boundary changed")
    checks.check(claim.get("source_policy_recheck_still_required") is True, "source-policy gate missing")
    checks.check(audit.get("submission_ready") is False, "audit must not mark submission ready")
    for token in [
        "raw-row arithmetic verified",
        "Method/example cells recomputed: `44/44`",
        "Order/finest-error mismatches against summary: `0`",
        "External superiority remains disallowed",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("common-reference order recomputation audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("common-reference order recomputation audit validation: PASS")
    print("cells=44/44")
    print("raw_rows=132")
    print("mismatches=0")
    print("external_superiority_allowed=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
