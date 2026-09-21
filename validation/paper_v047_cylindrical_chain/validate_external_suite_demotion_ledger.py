#!/usr/bin/env python3
"""Validate the explicit external-suite demotion ledger."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
EXPECTED_EXAMPLES = ["single_pendulum", "double_pendulum", "four_link", "slider_crank"]


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
        ledger = read_json(PAPER / "EXTERNAL_SUITE_DEMOTION_LEDGER.json")
        ledger_md = read_text(PAPER / "EXTERNAL_SUITE_DEMOTION_LEDGER.md")
        vp = read_json(PAPER / "VP2024_CODE_PATH_DISPOSITION_AUDIT.json")
        source_policy = read_json(PAPER / "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.json")
    except Exception as exc:  # noqa: BLE001
        print(f"external suite demotion ledger validation: FAIL\n- {exc}")
        return 1

    demoted = ledger.get("demoted_suites", [])
    demoted_by_suite = {item.get("suite_id"): item for item in demoted if isinstance(item, dict)}
    vp_suite = demoted_by_suite.get("vp2024_velocity_partitioning", {})
    hi_suite = demoted_by_suite.get("hi2022_half_implicit", {})
    ra_suite = demoted_by_suite.get("ra2021_absolute_coordinate", {})
    tfe_suite = demoted_by_suite.get("tfe2026_original_pendulum", {})
    vp_disposition = vp.get("source_code_path_disposition", {})
    flagged_by_suite = source_policy.get("coverage", {}).get("flagged_by_suite", {})

    checks.check(ledger.get("schema") == "external-suite-demotion-ledger-v1", "schema changed")
    checks.check(
        ledger.get("status") == "all_external_suites_demoted_from_external_superiority_scope",
        "status changed",
    )
    checks.check(ledger.get("submission_ready") is False, "ledger must not mark submission ready")
    checks.check(ledger.get("external_superiority_claim_allowed") is False, "external superiority overclaimed")
    checks.check(ledger.get("demoted_suite_count") == 4, "demoted suite count changed")
    checks.check(
        ledger.get("b2_subrequirements_closed_by_demotion")
        == [
            "vp2024_code_resolution_or_demotion",
            "hi2022_public_code_same_test_rows",
            "ra2021_public_code_same_test_rows",
            "original_tfe_pendulum_error_order_work_rows",
        ],
        "B2 demotion-closed subrequirements changed",
    )
    checks.check(ledger.get("b2_required_to_close_after_demotions") == [], "post-demotion B2 required list changed")
    checks.check(ledger.get("demoted_source_policy_rows") == 16, "demoted source-policy row count changed")
    checks.check(
        ledger.get("demoted_source_policy_flagged_rows")
        == sum(flagged_by_suite.values())
        == 15,
        "demoted flagged-row count changed",
    )
    checks.check(ledger.get("vp2024_demoted_source_policy_rows") == 4, "VP demoted source-policy rows changed")
    checks.check(ledger.get("vp2024_demoted_source_policy_flagged_rows") == 3, "VP demoted flagged rows changed")
    checks.check(ledger.get("hi2022_demoted_source_policy_rows") == 3, "HI2022 demoted source-policy rows changed")
    checks.check(ledger.get("hi2022_demoted_source_policy_flagged_rows") == 3, "HI2022 demoted flagged rows changed")
    checks.check(ledger.get("ra2021_demoted_source_policy_rows") == 5, "RA2021 demoted source-policy rows changed")
    checks.check(ledger.get("ra2021_demoted_source_policy_flagged_rows") == 5, "RA2021 demoted flagged rows changed")
    checks.check(ledger.get("tfe2026_demoted_source_policy_rows") == 4, "TFE demoted source-policy rows changed")
    checks.check(ledger.get("tfe2026_demoted_source_policy_flagged_rows") == 4, "TFE demoted flagged rows changed")
    checks.check(ledger.get("active_source_policy_flagged_rows_after_demotions") == 0, "active flagged rows changed")
    checks.check(
        set(demoted_by_suite)
        == {
            "vp2024_velocity_partitioning",
            "hi2022_half_implicit",
            "ra2021_absolute_coordinate",
            "tfe2026_original_pendulum",
        },
        "demoted suite set changed",
    )
    checks.check(vp_suite.get("examples_checked") == EXPECTED_EXAMPLES, "VP2024 example coverage changed")
    checks.check(
        vp_suite.get("decision") == "attempted_not_reproducible_not_promoted_keep_proxy_diagnostic",
        "VP2024 demotion decision changed",
    )
    checks.check(vp_suite.get("source_policy_rows") == 4, "VP2024 source-policy row count changed")
    checks.check(vp_suite.get("source_policy_code_path_unresolved_rows") == 4, "VP2024 unresolved rows changed")
    checks.check(
        vp_suite.get("self_reproduction_attempted_rows") == 4
        and vp_suite.get("unable_to_reproduce_rows") == 4,
        "VP2024 attempted/unable row count changed",
    )
    checks.check(
        vp_suite.get("final_nonpublic_code_disposition") == "unable_to_reproduce_not_promoted",
        "VP2024 final nonpublic-code disposition changed",
    )
    checks.check(vp_suite.get("distinct_public_code_path_found") is False, "VP code path unexpectedly found")
    checks.check(vp_suite.get("proxy_is_source_policy_reproduction") is False, "VP proxy promoted to source policy")
    checks.check(
        vp_suite.get("claim_allowed_now") == vp_disposition.get("claim_allowed_now") == "code-path-unresolved_related_work_only",
        "VP claim boundary changed",
    )
    checks.check(vp_suite.get("accepted_for_external_superiority") is False, "VP accepted for external superiority")
    checks.check(vp_suite.get("common_reference_proxy_retained") is True, "VP common-reference proxy not retained")
    checks.check(
        hi_suite.get("decision") == "explicitly_demoted_after_incomplete_full_T8_source_policy_evidence",
        "HI2022 demotion decision changed",
    )
    checks.check(hi_suite.get("source_policy_rows") == 3, "HI2022 source-policy row count changed")
    checks.check(hi_suite.get("source_policy_flagged_rows") == 3, "HI2022 flagged row count changed")
    checks.check(hi_suite.get("bounded_T0p1_rows_ok") == 24, "HI2022 bounded ok rows changed")
    checks.check(hi_suite.get("bounded_T0p1_rows") == 24, "HI2022 bounded rows changed")
    checks.check(hi_suite.get("t8_coarse_ok_rows") == 18, "HI2022 T=8 ok rows changed")
    checks.check(hi_suite.get("t8_coarse_rows") == 24, "HI2022 T=8 rows changed")
    checks.check(hi_suite.get("t8_coarse_complete_groups") == 4, "HI2022 T=8 complete groups changed")
    checks.check(hi_suite.get("t8_coarse_group_count") == 8, "HI2022 T=8 group count changed")
    checks.check(
        hi_suite.get("t8_tolerance_repair_combined_best_complete_groups") == 4,
        "HI2022 repair complete groups changed",
    )
    checks.check(
        hi_suite.get("t8_tolerance_repair_combined_best_group_count") == 8,
        "HI2022 repair group count changed",
    )
    checks.check(hi_suite.get("source_policy_reproduction_closed") is False, "HI2022 source policy overclosed")
    checks.check(hi_suite.get("accepted_for_external_superiority") is False, "HI2022 accepted for external superiority")
    checks.check(
        hi_suite.get("claim_allowed_now") == "demoted_incomplete_full_T8_source_policy_related_work_only",
        "HI2022 claim boundary changed",
    )
    checks.check(
        ledger.get("remaining_open_suites", []) == [],
        "remaining open suite set changed",
    )
    checks.check(
        ra_suite.get("decision") == "route_b_demoted_keep_public_baseline_and_common_reference_diagnostics",
        "RA2021 demotion decision changed",
    )
    checks.check(ra_suite.get("source_policy_rows") == 5, "RA2021 source-policy row count changed")
    checks.check(ra_suite.get("source_policy_flagged_rows") == 5, "RA2021 flagged row count changed")
    checks.check(ra_suite.get("public_order_groups_completed") == 12, "RA2021 public order groups changed")
    checks.check(ra_suite.get("public_timing_rows_completed") == 12, "RA2021 public timing rows changed")
    checks.check(ra_suite.get("source_policy_reproduction_rows") == 0, "RA2021 source-policy rows overclosed")
    checks.check(ra_suite.get("external_superiority_ready_rows") == 0, "RA2021 external-superiority rows overclosed")
    checks.check(ra_suite.get("accepted_for_external_superiority") is False, "RA2021 accepted for external superiority")
    checks.check(
        ra_suite.get("claim_allowed_now") == "route_b_demoted_related_work_and_diagnostics_only",
        "RA2021 claim boundary changed",
    )
    checks.check(
        tfe_suite.get("decision") == "route_b_demoted_keep_formula_comparator_and_candidate_diagnostics",
        "TFE demotion decision changed",
    )
    checks.check(tfe_suite.get("source_policy_rows") == 4, "TFE source-policy row count changed")
    checks.check(tfe_suite.get("source_policy_flagged_rows") == 4, "TFE flagged row count changed")
    checks.check(tfe_suite.get("source_policy_rows_completed") == 0, "TFE source-policy rows overclosed")
    checks.check(tfe_suite.get("external_superiority_ready_rows") == 0, "TFE external-superiority rows overclosed")
    checks.check(tfe_suite.get("pendulum_dae_runner_implemented") is False, "TFE DAE runner unexpectedly implemented")
    checks.check(tfe_suite.get("accepted_for_external_superiority") is False, "TFE accepted for external superiority")
    checks.check(
        tfe_suite.get("claim_allowed_now") == "route_b_demoted_formal_comparator_and_diagnostics_only",
        "TFE claim boundary changed",
    )
    execution = ledger.get("execution_policy", {})
    checks.check(execution.get("default_1e_4_required") is False, "ledger requires default 1e-4")
    checks.check(execution.get("heavy_numerical_run_invoked") is False, "ledger invoked heavy run")
    checks.check(execution.get("run_v047_invoked") is False, "ledger invoked run_v047")
    checks.check(execution.get("v048_runner_invoked") is False, "ledger invoked v048 runner")
    for token in [
        "all external source-policy suites explicitly demoted from external-superiority scope",
        "B2 subrequirements closed by demotion",
        "vp2024_code_resolution_or_demotion",
        "hi2022_public_code_same_test_rows",
        "ra2021_public_code_same_test_rows",
        "original_tfe_pendulum_error_order_work_rows",
        "Demoted VP2024 source-policy rows/flagged rows: `4/3`",
        "VP2024 attempted/unable/final disposition: `4/4/unable_to_reproduce_not_promoted`",
        "attempted_not_reproducible_not_promoted_keep_proxy_diagnostic",
        "Demoted HI2022 source-policy rows/flagged rows: `3/3`",
        "Demoted RA2021 source-policy rows/flagged rows: `5/5`",
        "Demoted TFE source-policy rows/flagged rows: `4/4`",
        "Active source-policy flagged rows after demotions: `0`",
        "These demotions are claim-boundary decisions, not numerical wins.",
    ]:
        checks.check(token in ledger_md, f"markdown missing token: {token}")

    if checks.errors:
        print("external suite demotion ledger validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("external suite demotion ledger validation: PASS")
    print("demoted_suites=4")
    print("vp2024_demoted=True")
    print("hi2022_demoted=True")
    print("ra2021_demoted=True")
    print("tfe2026_demoted=True")
    print("active_source_policy_flagged_rows_after_demotions=0")
    print("default_1e-4=False")
    print("run_v047_invoked=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
