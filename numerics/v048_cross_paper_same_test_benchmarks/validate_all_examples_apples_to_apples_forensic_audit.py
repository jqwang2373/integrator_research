#!/usr/bin/env python3
"""Validate the all-example forensic comparison audit."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
EXAMPLES = {"single_pendulum", "double_pendulum", "four_link", "slider_crank"}


class Checks:
    def __init__(self) -> None:
        self.failures: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.failures.append(message)


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    checks = Checks()
    summary = read_json(RESULTS / "all_examples_apples_to_apples_forensic_audit.json")
    rows = read_csv(RESULTS / "all_examples_apples_to_apples_forensic_audit.csv")
    report = (RESULTS / "all_examples_apples_to_apples_forensic_audit.md").read_text(encoding="utf-8")

    checks.check(
        summary.get("schema") == "all-examples-apples-to-apples-forensic-audit-v1",
        "unexpected forensic audit schema",
    )
    checks.check(summary.get("all_examples_checked") is True, "not all four examples were checked")
    checks.check(
        set(summary.get("examples", [])) == EXAMPLES,
        f"examples mismatch: {summary.get('examples')}",
    )
    checks.check(summary.get("row_count") == 44 == len(rows), "expected exactly 44 method/example rows")
    checks.check(summary.get("raw_row_count") == 132, "expected 132 raw h rows")
    checks.check(summary.get("method_count") == 11, "expected 11 common-reference methods")
    checks.check(
        summary.get("bounded_common_reference_diagnostic_rows") == 44,
        "all 44 rows should remain bounded common-reference diagnostics",
    )
    checks.check(
        summary.get("strict_external_error_claim_allowed_rows") == 0,
        "strict external error claims should remain blocked",
    )
    checks.check(
        summary.get("direct_error_superiority_claim_allowed_for_paper") is False,
        "paper-level direct error superiority must be blocked",
    )
    checks.check(
        summary.get("external_superiority_claim_allowed") is False,
        "external superiority must remain blocked",
    )
    checks.check(
        summary.get("source_policy_reproduction") is False,
        "source-policy reproduction should remain open",
    )
    checks.check(
        all(item.get("strict_external_error_claim_allowed") == "false" for item in rows),
        "a row unexpectedly allowed a strict external error claim",
    )
    checks.check(
        all(item.get("bounded_common_reference_diagnostic") == "true" for item in rows),
        "some common-reference row is no longer a bounded diagnostic",
    )
    checks.check(
        "source_policy_not_closed" in summary.get("issue_counts", {}),
        "source-policy-open issue count is missing",
    )
    checks.check(
        "Direct error superiority allowed for paper: `False`" in report,
        "markdown report missing claim-blocking line",
    )

    if checks.failures:
        print("validate_all_examples_apples_to_apples_forensic_audit=FAIL")
        for failure in checks.failures:
            print(f"- {failure}")
        return 1

    print("validate_all_examples_apples_to_apples_forensic_audit=PASS")
    print(f"rows={summary.get('row_count')}")
    print(f"examples={','.join(summary.get('examples', []))}")
    print("direct_error_superiority_claim_allowed_for_paper=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
