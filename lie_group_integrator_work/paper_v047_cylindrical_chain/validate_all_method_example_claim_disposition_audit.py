#!/usr/bin/env python3
"""Validate the all-method/all-example claim-disposition audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
EXPECTED_EXAMPLES = ["single_pendulum", "double_pendulum", "four_link", "slider_crank"]
EXPECTED_SUITES = {
    "hi2022_half_implicit": 8,
    "ra2021_absolute_coordinate": 12,
    "tfe2026_original_pendulum": 16,
    "vp2024_velocity_partitioning": 4,
}


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
        audit = read_json(PAPER / "ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.json")
        audit_md = read_text(PAPER / "ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.md")
        matrix = read_json(PAPER / "PAPER_NUMERICAL_RESULT_MATRIX.json")
        sanity = read_json(PAPER / "ALL_EXAMPLES_RESULT_SANITY_AUDIT.json")
        recompute = read_json(PAPER / "COMMON_REFERENCE_ORDER_RECOMPUTATION_AUDIT.json")
        comparison = read_json(PAPER / "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.json")
        source_ledger = read_json(PAPER / "SOURCE_POLICY_ROW_CLOSURE_LEDGER.json")
    except Exception as exc:  # noqa: BLE001
        print(f"all-method claim-disposition audit validation: FAIL\n- {exc}")
        return 1

    coverage = audit.get("coverage", {})
    wins = audit.get("win_counts", {})
    boundary = audit.get("claim_boundary", {})
    rows = audit.get("rows", [])
    execution = audit.get("execution_policy", {})

    checks.check(
        audit.get("schema") == "all-method-example-claim-disposition-audit-v1",
        "schema changed",
    )
    checks.check(
        audit.get("status")
        == "all_nonlocal_method_example_rows_checked_common_reference_closed_source_policy_open",
        "status changed",
    )
    checks.check(audit.get("submission_ready") is False, "audit must not mark submission ready")
    checks.check(coverage.get("examples") == EXPECTED_EXAMPLES, "example list/order changed")
    checks.check(coverage.get("all_four_examples_checked") is True, "all-four-example marker missing")
    checks.check(coverage.get("method_count") == matrix.get("method_count") == 11, "method count changed")
    checks.check(coverage.get("nonlocal_method_count") == 10, "nonlocal method count changed")
    checks.check(coverage.get("total_cells") == matrix.get("row_count") == 44, "total cell count changed")
    checks.check(coverage.get("local_cells") == 4, "local cell count changed")
    checks.check(coverage.get("nonlocal_cells") == 40, "nonlocal cell count changed")
    checks.check(coverage.get("expected_nonlocal_cells") == 40, "expected nonlocal cell count changed")
    checks.check(
        coverage.get("raw_rows_recomputed")
        == recompute.get("coverage", {}).get("raw_ok_row_count")
        == 132,
        "raw recomputation count changed",
    )
    checks.check(
        coverage.get("summary_mismatches")
        == recompute.get("verification", {}).get("mismatch_count")
        == 0,
        "summary mismatch count changed",
    )

    checks.check(
        wins.get("local_velocity_order_wins")
        == wins.get("local_velocity_order_comparisons")
        == matrix.get("direct_nonlocal_velocity_order_wins")
        == comparison.get("direct_nonlocal_velocity_order_wins")
        == 40,
        "velocity-order win count changed",
    )
    checks.check(
        wins.get("local_finest_velocity_error_wins")
        == wins.get("local_finest_velocity_error_comparisons")
        == matrix.get("direct_nonlocal_velocity_error_wins")
        == comparison.get("direct_nonlocal_finest_velocity_error_wins")
        == 40,
        "finest-velocity-error win count changed",
    )
    checks.check(
        wins.get("comparison_audit_direct_order_comparisons") == 40,
        "comparison audit order comparison count changed",
    )
    checks.check(
        wins.get("comparison_audit_direct_error_comparisons") == 40,
        "comparison audit error comparison count changed",
    )

    checks.check(boundary.get("common_reference_claim_allowed") is True, "common-reference claim boundary changed")
    checks.check(
        boundary.get("source_policy_superiority_claim_allowed") is False,
        "source-policy superiority boundary changed",
    )
    checks.check(
        boundary.get("paper_direct_error_superiority_claim_allowed") is False,
        "paper direct-error superiority boundary changed",
    )
    checks.check(boundary.get("strict_external_error_claim_allowed_rows") == 0, "strict external row count changed")
    checks.check(boundary.get("nonlocal_source_policy_closed_rows") == 0, "nonlocal source-policy rows closed unexpectedly")
    checks.check(boundary.get("nonlocal_source_policy_open_rows") == 40, "nonlocal source-policy open count changed")
    checks.check(
        boundary.get("flagged_nonlocal_rows")
        == boundary.get("flagged_nonlocal_rows_from_sanity_audit")
        == sanity.get("baseline_sanity", {}).get("flagged_nonlocal_count")
        == 15,
        "flagged nonlocal row count changed",
    )
    checks.check(
        boundary.get("source_policy_closed_rows_from_ledger")
        == source_ledger.get("coverage", {}).get("rows_source_policy_closed")
        == 0,
        "source-policy ledger closed rows changed",
    )
    checks.check(
        boundary.get("external_superiority_ready_rows_from_ledger")
        == source_ledger.get("coverage", {}).get("rows_external_superiority_ready")
        == 0,
        "external-superiority-ready rows changed",
    )

    checks.check(len(rows) == 40, "row count changed")
    checks.check(all(row.get("source_policy_closed") is False for row in rows), "some nonlocal row was source-policy closed")
    checks.check(
        all(row.get("strict_external_error_claim_allowed") is False for row in rows),
        "some strict external error row was allowed",
    )
    checks.check(all(row.get("local_velocity_order_win") is True for row in rows), "some velocity-order win is missing")
    checks.check(
        all(row.get("local_finest_velocity_error_win") is True for row in rows),
        "some finest-velocity-error win is missing",
    )
    checks.check(
        set(row.get("example") for row in rows) == set(EXPECTED_EXAMPLES),
        "row examples do not cover all four examples",
    )
    checks.check(
        sum(row.get("flagged_by_sanity_audit") is True for row in rows) == 15,
        "row-level sanity-flagged count changed",
    )
    for row in rows:
        issues = row.get("issues", [])
        if row.get("suite") == "tfe2026_original_pendulum":
            checks.check(
                "original_tfe_setup_not_encoded" not in issues,
                f"TFE row keeps stale setup issue: {row}",
            )
            checks.check(
                "original_tfe_runner_and_friction_source_policy_open" in issues,
                f"TFE row missing updated runner/friction issue: {row}",
            )

    per_suite = {item["suite"]: item for item in audit.get("per_suite", [])}
    checks.check(set(per_suite) == set(EXPECTED_SUITES), "suite set changed")
    for suite, expected_rows in EXPECTED_SUITES.items():
        item = per_suite.get(suite, {})
        checks.check(item.get("row_count") == expected_rows, f"{suite} row count changed")
        checks.check(item.get("local_velocity_order_wins") == expected_rows, f"{suite} order win count changed")
        checks.check(item.get("local_finest_velocity_error_wins") == expected_rows, f"{suite} error win count changed")
        checks.check(item.get("source_policy_closed_rows") == 0, f"{suite} source-policy closure changed")
        checks.check(item.get("strict_external_error_claim_allowed_rows") == 0, f"{suite} strict claim count changed")

    per_example = {item["example"]: item for item in audit.get("per_example", [])}
    checks.check(set(per_example) == set(EXPECTED_EXAMPLES), "per-example set changed")
    for example in EXPECTED_EXAMPLES:
        item = per_example.get(example, {})
        checks.check(item.get("row_count") == 10, f"{example} row count changed")
        checks.check(item.get("local_velocity_order_wins") == 10, f"{example} order win count changed")
        checks.check(item.get("local_finest_velocity_error_wins") == 10, f"{example} error win count changed")
        checks.check(item.get("source_policy_closed_rows") == 0, f"{example} source-policy closure changed")

    checks.check(execution.get("read_only_existing_artifacts") is True, "audit is not read-only")
    checks.check(execution.get("default_1e_4_required") is False, "audit requires default 1e-4")
    checks.check(execution.get("heavy_numerical_run_invoked") is False, "audit invoked heavy run")
    checks.check(execution.get("run_v047_invoked") is False, "audit invoked run_v047")
    checks.check(execution.get("v048_runner_invoked") is False, "audit invoked v048 runner")

    for token in [
        "ALL 40 NONLOCAL METHOD/EXAMPLE ROWS CHECKED",
        "Nonlocal comparison cells: `40/40`",
        "Local velocity-order wins: `40/40`",
        "Local finest-velocity-error wins: `40/40`",
        "Nonlocal source-policy closed rows: `0/40`",
        "Nonlocal source-policy open rows: `40/40`",
        "Flagged nonlocal rows: `15/40`",
        "Strict external error-claim rows: `0`",
        "Source-policy superiority claim allowed: `False`",
        "The `15` flagged rows are anomaly or source-policy recheck rows",
        "all 40 nonlocal rows remain source-policy open",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("all-method claim-disposition audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("all-method claim-disposition audit validation: PASS")
    print("nonlocal_cells=40/40")
    print("local_velocity_order_wins=40/40")
    print("local_finest_velocity_error_wins=40/40")
    print("nonlocal_source_policy_closed_rows=0/40")
    print("nonlocal_source_policy_open_rows=40/40")
    print("flagged_nonlocal_rows=15/40")
    print("source_policy_superiority_claim_allowed=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
