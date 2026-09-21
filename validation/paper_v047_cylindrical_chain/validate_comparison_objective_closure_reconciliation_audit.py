#!/usr/bin/env python3
"""Validate the comparison objective closure reconciliation audit."""

from __future__ import annotations

import json
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
        audit = read_json(PAPER / "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.json")
        audit_md = read_text(PAPER / "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.md")
    except Exception as exc:  # noqa: BLE001
        print(f"comparison objective closure reconciliation audit validation: FAIL\n- {exc}")
        return 1

    checks.check(
        audit.get("schema") == "comparison-objective-closure-reconciliation-v1",
        "schema changed",
    )
    checks.check(
        audit.get("status") == "common_reference_objective_closed_source_policy_reproduction_open",
        "status changed",
    )
    checks.check(audit.get("submission_ready") is False, "audit must not mark submission ready")
    checks.check(audit.get("comparison_matrix_closed") is True, "comparison matrix should be closed")
    checks.check(audit.get("common_reference_claim_allowed") is True, "common-reference claim boundary changed")
    checks.check(
        audit.get("paper_direct_error_superiority_claim_allowed") is False,
        "paper-level direct error superiority should remain blocked",
    )
    checks.check(
        audit.get("strict_external_error_claim_allowed_rows") == 0,
        "strict external error-claim row count changed",
    )
    checks.check(audit.get("all_method_example_cells_checked") == 44, "all-example forensic coverage changed")
    checks.check(
        audit.get("source_policy_reproduction_open") is True,
        "source-policy reproduction boundary changed",
    )
    checks.check(
        audit.get("source_policy_superiority_claim_allowed") is False,
        "source-policy superiority boundary changed",
    )
    checks.check(audit.get("common_reference_cells") == 44, "common-reference cell count changed")
    checks.check(audit.get("raw_rows_recomputed") == 132, "raw recomputation row count changed")
    checks.check(audit.get("summary_mismatches") == 0, "summary mismatch count changed")
    checks.check(audit.get("required_method_labels_resolved") is True, "required method labels not resolved")
    checks.check(audit.get("source_unresolved_methods") == [], "source-unresolved methods should be empty")
    checks.check(
        audit.get("alias_resolved_methods") == ["vp2024_lie_group_ode_partitioning"],
        "VP alias resolution changed",
    )
    checks.check(
        audit.get("scope_excluded_methods") == ["tfe2026_TFE_m3_GL"],
        "scope-excluded method list changed",
    )
    checks.check(
        audit.get("direct_nonlocal_velocity_order_wins")
        == audit.get("direct_nonlocal_velocity_order_comparisons")
        == 40,
        "direct nonlocal order win count changed",
    )
    checks.check(
        audit.get("direct_nonlocal_finest_velocity_error_wins")
        == audit.get("direct_nonlocal_finest_velocity_error_comparisons")
        == 40,
        "direct nonlocal error win count changed",
    )
    checks.check(
        audit.get("original_paper_velocity_error_wins")
        == audit.get("original_paper_velocity_error_comparisons")
        == 16,
        "original-paper error win count changed",
    )
    checks.check(
        audit.get("kissel_negrut_velocity_error_wins")
        == audit.get("kissel_negrut_velocity_error_comparisons")
        == 24,
        "Kissel/Negrut error win count changed",
    )
    checks.check(audit.get("source_policy_flagged_rows") == 15, "source-policy flagged row count changed")
    checks.check(
        audit.get("source_policy_velocity_mismatch_rows") == 10,
        "source-policy velocity mismatch count changed",
    )
    checks.check(
        audit.get("b2_b4_reconciliation", {}).get("paper_submission_b2_b4_can_close_now") is False,
        "B2/B4 closure boundary changed",
    )
    for token in [
        "bounded common-reference diagnostic assembled",
        "Comparison matrix closed: `True`",
        "Common-reference claim allowed: `True`",
        "Paper direct error superiority allowed: `False`",
        "Strict external error-claim rows allowed: `0`",
        "All method/example cells checked: `44`",
        "Source-policy superiority allowed: `False`",
        "Direct nonlocal velocity-order wins: `40/40`",
        "Direct nonlocal finest-velocity-error wins: `40/40`",
        "B2/B4 can close now: `False`",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("comparison objective closure reconciliation audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("comparison objective closure reconciliation audit validation: PASS")
    print("comparison_matrix_closed=True")
    print("common_reference_claim_allowed=True")
    print("paper_direct_error_superiority_claim_allowed=False")
    print("source_policy_superiority_claim_allowed=False")
    print("direct_nonlocal_order_wins=40/40")
    print("direct_nonlocal_error_wins=40/40")
    return 0


if __name__ == "__main__":
    sys.exit(main())
