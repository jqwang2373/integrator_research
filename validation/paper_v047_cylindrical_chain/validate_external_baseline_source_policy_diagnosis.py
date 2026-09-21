#!/usr/bin/env python3
"""Validate the external baseline source-policy diagnosis audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path


PAPER = Path(__file__).resolve().parent
EXPECTED_EXAMPLES = {"single_pendulum", "double_pendulum", "four_link", "slider_crank"}


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
        diagnosis = read_json(PAPER / "EXTERNAL_BASELINE_SOURCE_POLICY_DIAGNOSIS.json")
        diagnosis_md = read_text(PAPER / "EXTERNAL_BASELINE_SOURCE_POLICY_DIAGNOSIS.md")
        sanity = read_json(PAPER / "ALL_EXAMPLES_RESULT_SANITY_AUDIT.json")
        recomputation = read_json(PAPER / "COMMON_REFERENCE_ORDER_RECOMPUTATION_AUDIT.json")
    except Exception as exc:  # noqa: BLE001
        print(f"external baseline source-policy diagnosis validation: FAIL\n- {exc}")
        return 1

    coverage = diagnosis.get("coverage", {})
    context = diagnosis.get("source_policy_context", {})
    claim = diagnosis.get("claim_boundary", {})
    category_counts = coverage.get("category_counts", {})
    rows = diagnosis.get("diagnosis_rows", [])

    checks.check(diagnosis.get("schema") == "external-baseline-source-policy-diagnosis-v1", "schema changed")
    checks.check(diagnosis.get("status") == "diagnosis_only_source_policy_recheck_required", "status changed")
    checks.check(diagnosis.get("submission_ready") is False, "diagnosis must not mark submission ready")
    checks.check(diagnosis.get("source_policy_recheck_required") is True, "source-policy recheck gate missing")
    checks.check(diagnosis.get("external_superiority_allowed") is False, "external superiority boundary changed")
    checks.check(diagnosis.get("all_four_examples_covered_by_flagged_rows") is True, "flagged rows do not cover all examples")
    checks.check(coverage.get("flagged_row_count") == sanity.get("baseline_sanity", {}).get("flagged_nonlocal_count") == 15, "flagged row count changed")
    checks.check(set(coverage.get("flagged_examples", [])) == EXPECTED_EXAMPLES, "flagged example set changed")
    checks.check(len(rows) == 15, "diagnosis row count changed")
    checks.check(coverage.get("position_aligned_velocity_mismatch_count", 0) >= 8, "velocity mismatch diagnosis missing")
    checks.check("position_aligned_velocity_mismatch" in category_counts, "position/velocity mismatch category missing")
    checks.check("single_pendulum_velocity_output_policy_suspect" in category_counts, "single-pendulum source-policy category missing")
    checks.check(context.get("common_reference_arithmetic_mismatches") == recomputation.get("verification", {}).get("mismatch_count") == 0, "arithmetic mismatch context changed")
    checks.check(context.get("same_test_campaign_status") == "not_run", "same-test campaign boundary changed")
    checks.check(context.get("accepted_external_dynamic_order_examples_count") == 0, "external dynamic-order acceptance changed")
    checks.check(claim.get("diagnosis_is_not_method_correctness_judgment") is True, "method-correctness boundary missing")
    checks.check(claim.get("diagnosis_is_not_external_superiority_evidence") is True, "external-superiority boundary missing")
    checks.check(claim.get("b2_b4_status") == "not_closed", "B2/B4 status changed")
    for token in [
        "diagnosis only",
        "Flagged baseline rows diagnosed: `15`",
        "Common-reference arithmetic mismatches: `0`",
        "Same-test campaign status: `not_run`",
        "External superiority allowed: `False`",
        "B2/B4 remain open",
    ]:
        checks.check(token in diagnosis_md, f"markdown missing token: {token}")

    if checks.errors:
        print("external baseline source-policy diagnosis validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("external baseline source-policy diagnosis validation: PASS")
    print("flagged_rows=15")
    print(f"position_aligned_velocity_mismatch={coverage.get('position_aligned_velocity_mismatch_count')}")
    print("same_test_campaign_status=not_run")
    print("external_superiority_allowed=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
