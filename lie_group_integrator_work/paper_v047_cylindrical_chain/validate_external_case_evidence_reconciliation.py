#!/usr/bin/env python3
"""Validate the external case evidence reconciliation artifact."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
EXPECTED_EXAMPLES = {"single_pendulum", "double_pendulum", "four_link", "slider_crank"}
EXPECTED_CASE_STATUS_COUNTS = {"code_path_unresolved": 1, "not_run": 16}
EXPECTED_FLAGGED_BY_EXAMPLE = {
    "single_pendulum": 8,
    "double_pendulum": 2,
    "four_link": 4,
    "slider_crank": 1,
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
        audit = read_json(PAPER / "EXTERNAL_CASE_EVIDENCE_RECONCILIATION.json")
        audit_md = read_text(PAPER / "EXTERNAL_CASE_EVIDENCE_RECONCILIATION.md")
        closure = read_json(PAPER / "EXTERNAL_SOURCE_POLICY_CLOSURE_MANIFEST.json")
        row_ledger = read_json(PAPER / "SOURCE_POLICY_ROW_CLOSURE_LEDGER.json")
        manifest = read_json(PAPER / "SUBMISSION_ARTIFACT_MANIFEST.json")
    except Exception as exc:  # noqa: BLE001
        print(f"external case evidence reconciliation validation: FAIL\n- {exc}")
        return 1

    suites = {row.get("suite_id"): row for row in audit.get("suites", []) if isinstance(row, dict)}
    source_policy = audit.get("source_policy_row_ledger", {})
    progress = audit.get("source_policy_progress", {})
    ra_progress = progress.get("ra2021_public_baselines", {})
    gauss_progress = progress.get("ra2021_local_gauss6_rows", {})
    hi_progress = progress.get("hi2022_public_baselines", {})
    acceptance = audit.get("acceptance_boundary", {})
    execution = audit.get("execution_policy", {})

    checks.check(audit.get("schema") == "external-case-evidence-reconciliation-v1", "schema changed")
    checks.check(
        audit.get("status") == "bounded_evidence_present_full_source_policy_campaign_open",
        "status changed",
    )
    checks.check(audit.get("submission_ready") is False, "audit must not mark submission ready")
    checks.check(set(audit.get("examples", [])) == EXPECTED_EXAMPLES, "example set changed")
    checks.check(audit.get("same_test_campaign_status") == "not_run", "same-test campaign status changed")
    checks.check(audit.get("case_inventory_case_count") == 17, "case inventory count changed")
    checks.check(audit.get("case_inventory_status_counts") == EXPECTED_CASE_STATUS_COUNTS, "case status counts changed")
    checks.check(
        set(audit.get("bounded_or_public_evidence_suites", []))
        == {"ra2021_absolute_coordinate", "hi2022_half_implicit"},
        "bounded evidence suite set changed",
    )
    checks.check(
        set(audit.get("not_ready_or_demote_suites", []))
        == {"tfe2026_original_pendulum", "vp2024_velocity_partitioning"},
        "not-ready/demote suite set changed",
    )
    checks.check(source_policy.get("flagged_rows") == row_ledger.get("coverage", {}).get("flagged_row_count") == 15, "flagged row count changed")
    checks.check(
        source_policy.get("flagged_by_example") == EXPECTED_FLAGGED_BY_EXAMPLE,
        "flagged by-example count changed",
    )
    checks.check(source_policy.get("rows_source_policy_closed") == 0, "source-policy rows unexpectedly closed")
    checks.check(source_policy.get("rows_external_superiority_ready") == 0, "claim-ready rows unexpectedly changed")
    checks.check(acceptance.get("accepted_external_dynamic_order_examples_count") == 0, "accepted external dynamic examples changed")
    checks.check(acceptance.get("external_superiority_claim") is False, "external superiority claim changed")
    checks.check(acceptance.get("b2_can_close_now") is False, "B2 closure changed")
    checks.check(acceptance.get("b4_can_close_now") is False, "B4 closure changed")
    checks.check(execution.get("read_only_existing_artifacts") is True, "audit is not read-only")
    checks.check(execution.get("default_1e_4_required") is False, "audit requires default 1e-4")
    checks.check(execution.get("heavy_numerical_run_invoked") is False, "audit invoked heavy run")
    checks.check(execution.get("run_v047_invoked") is False, "audit invoked run_v047")
    checks.check(execution.get("v048_runner_invoked") is False, "audit invoked v048 runner")
    checks.check(audit.get("interpretation", {}).get("case_inventory_not_run_is_not_zero_evidence") is True, "case inventory interpretation missing")
    checks.check(
        "local Gauss6/FullVA rows are not yet complete source-policy dynamic"
        in audit.get("interpretation", {}).get("current_source_policy_reading", ""),
        "source-policy current reading missing",
    )
    checks.check(ra_progress.get("order_groups_completed") == 12, "RA2021 public baseline group count changed")
    checks.check(ra_progress.get("order_groups_required") == 12, "RA2021 public baseline required count changed")
    checks.check(ra_progress.get("order_rows_ok") == 36, "RA2021 public baseline ok row count changed")
    checks.check(ra_progress.get("order_rows_total") == 36, "RA2021 public baseline total row count changed")
    checks.check(ra_progress.get("timing_rows_completed") == 12, "RA2021 timing row count changed")
    checks.check(ra_progress.get("timing_rows_required") == 12, "RA2021 timing required row count changed")
    checks.check(
        gauss_progress.get("single_public_policy_rows_completed") is True,
        "Gauss6 single public-policy marker changed",
    )
    checks.check(
        gauss_progress.get("double_public_policy_rows_completed") is False,
        "Gauss6 double public-policy marker changed",
    )
    checks.check(
        gauss_progress.get("closed_loop_public_horizon_rows_completed") is True,
        "Gauss6 closed-loop public-horizon marker changed",
    )
    checks.check(
        gauss_progress.get("closed_loop_row_kind") == "kinematic_reaction_residual_not_true_dynamic_order",
        "Gauss6 closed-loop row-kind boundary changed",
    )
    checks.check(
        gauss_progress.get("accepted_external_dynamic_order_count") == 0,
        "accepted external dynamic order count changed",
    )
    checks.check(
        hi_progress.get("bounded_pilot_groups_completed") == 8
        and hi_progress.get("bounded_pilot_groups_required") == 8,
        "HI2022 bounded pilot group count changed",
    )
    checks.check(hi_progress.get("full_T8_policy_completed") is False, "HI2022 full T8 boundary changed")

    checks.check(set(suites) == {
        "ra2021_absolute_coordinate",
        "hi2022_half_implicit",
        "tfe2026_original_pendulum",
        "vp2024_velocity_partitioning",
    }, "suite set changed")
    checks.check(suites["ra2021_absolute_coordinate"].get("bounded_evidence_present") is True, "RA bounded evidence missing")
    checks.check(suites["hi2022_half_implicit"].get("bounded_evidence_present") is True, "HI bounded evidence missing")
    checks.check(suites["tfe2026_original_pendulum"].get("bounded_evidence_present") is False, "TFE evidence unexpectedly present")
    checks.check(suites["vp2024_velocity_partitioning"].get("bounded_evidence_present") is False, "VP evidence unexpectedly present")
    checks.check(
        suites["ra2021_absolute_coordinate"].get("performance_rows", {}).get("all_four_examples_present") is True,
        "RA performance rows lost all-four-example marker",
    )
    checks.check(
        suites["hi2022_half_implicit"].get("performance_rows", {}).get("all_four_examples_present") is True,
        "HI performance rows lost all-four-example marker",
    )
    checks.check(
        suites["ra2021_absolute_coordinate"].get("order_group_status", {}).get(
            "double_pendulum_public_dynamic_self_reference",
            {},
        ).get("failed_or_partial_groups")
        == ["rp:double_pendulum"],
        "RA double-pendulum rp failure marker changed",
    )
    checks.check(
        suites["hi2022_half_implicit"].get("order_group_status", {}).get("bounded_T0p1_groups", {}).get(
            "completed_group_count"
        )
        == 8,
        "HI bounded group count changed",
    )
    for suite in suites.values():
        checks.check(suite.get("source_policy_closed") is False, f"{suite.get('suite_id')} unexpectedly closed")
        checks.check(suite.get("external_superiority_ready") is False, f"{suite.get('suite_id')} unexpectedly claim-ready")
        checks.check(suite.get("full_source_policy_campaign_completed") is False, f"{suite.get('suite_id')} unexpectedly full-campaign complete")

    checks.check(
        manifest.get("external_case_evidence_reconciliation") == "EXTERNAL_CASE_EVIDENCE_RECONCILIATION.md",
        "manifest reconciliation path missing",
    )
    checks.check(
        manifest.get("external_case_evidence_reconciliation_json") == "EXTERNAL_CASE_EVIDENCE_RECONCILIATION.json",
        "manifest reconciliation JSON path missing",
    )
    checks.check(
        "EXTERNAL_CASE_EVIDENCE_RECONCILIATION.md" in manifest.get("evidence_anchors", []),
        "manifest reconciliation anchor missing",
    )
    checks.check(
        "EXTERNAL_CASE_EVIDENCE_RECONCILIATION.json" in manifest.get("evidence_anchors", []),
        "manifest reconciliation JSON anchor missing",
    )
    checks.check(
        "validate_external_case_evidence_reconciliation.py" in manifest.get("validators", []),
        "manifest reconciliation validator missing",
    )
    checks.check(
        closure.get("performance_matrix", {}).get("completed_row_count") == 32,
        "source-policy manifest performance count changed",
    )

    for token in [
        "BOUNDED EVIDENCE PRESENT; FULL SOURCE-POLICY CAMPAIGN OPEN",
        "Case inventory status counts: `{'code_path_unresolved': 1, 'not_run': 16}`",
        "Bounded/public evidence suites: `ra2021_absolute_coordinate, hi2022_half_implicit`",
        "Not-ready or demote suites: `tfe2026_original_pendulum, vp2024_velocity_partitioning`",
        "2021 public baseline order groups: `12/12`",
        "2021 public timing rows: `12/12`",
        "Local Gauss6/FullVA source-policy dynamic-order examples accepted: `0/4`",
        "Source-policy rows closed: `0/15`",
        "External-superiority-ready rows: `0/15`",
        "Default `1e-4` required: `False`",
        "The case inventory's `not_run` markers refer to the full source-policy",
        "the local",
        "Gauss6/FullVA rows are not yet complete source-policy dynamic",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("external case evidence reconciliation validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("external case evidence reconciliation validation: PASS")
    print("bounded_evidence_suites=ra2021_absolute_coordinate,hi2022_half_implicit")
    print("not_ready_or_demote_suites=tfe2026_original_pendulum,vp2024_velocity_partitioning")
    print("case_inventory_status_counts=not_run:16,code_path_unresolved:1")
    print("ra2021_public_baseline_groups=12/12")
    print("local_source_policy_dynamic_order_examples=0/4")
    print("source_policy_rows_closed=0/15")
    print("external_superiority_ready_rows=0/15")
    return 0


if __name__ == "__main__":
    sys.exit(main())
