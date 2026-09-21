#!/usr/bin/env python3
"""Validate the B4 source-policy row closure-readiness ledger."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
EXPECTED_SUITE_ROWS = {
    "ra2021_absolute_coordinate": 12,
    "tfe2026_original_pendulum": 16,
    "hi2022_half_implicit": 8,
    "vp2024_velocity_partitioning": 4,
}
EXPECTED_METHODS = {
    "ra2021_rA",
    "ra2021_reps",
    "ra2021_rp",
    "hi2022_rA",
    "hi2022_rA_half",
    "tfe2026_Newmark_beta",
    "tfe2026_TFE_m1",
    "tfe2026_TFE_m2",
    "tfe2026_trapezoidal",
    "vp2024_coordinate_partitioning_rA",
}
EXPECTED_EXAMPLES = {"single_pendulum", "double_pendulum", "four_link", "slider_crank"}
EXPECTED_BLOCKER_COUNTS = {
    "hi2022_ra_half_double_partial_newton_failure_not_promoted": 1,
    "hi2022_selected_coarse_trio_not_full_public_grid_not_promoted": 7,
    "distinct_public_vp2024_code_path_not_found_proxy_not_source_policy": 4,
    "paper_spec_candidate_runner_not_source_policy_equivalent": 4,
    "ra2021_closed_loop_T0p1_mixed_reference_not_source_policy": 6,
    "ra2021_double_low_order_floor_limited_constraint_not_promoted": 3,
    "ra2021_single_floor_limited_public_h_tranche_not_promoted": 3,
    "tfe_source_paper_pendulum_suite_does_not_define_this_mechanism_runner": 12,
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


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    checks = Checks()
    try:
        ledger = read_json(PAPER / "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.json")
        ledger_md = read_text(PAPER / "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.md")
        csv_rows = read_csv_rows(PAPER / "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.csv")
        matrix = read_json(PAPER / "PAPER_NUMERICAL_RESULT_MATRIX.json")
        b4 = read_json(PAPER / "B4_SOURCE_POLICY_WORK_PRECISION_EXECUTION_PLAN.json")
        disposition = read_json(PAPER / "ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.json")
        tfe_demotion_audit = read_json(PAPER / "TFE_B4_B7_SOURCE_POLICY_DEMOTION_AUDIT.json")
        post_execution = read_json(PAPER / "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.json")
    except Exception as exc:  # noqa: BLE001
        print(f"B4 source-policy row closure-readiness ledger validation: FAIL\n- {exc}")
        return 1

    rows = ledger.get("rows", [])
    suite_rows: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        if isinstance(row, dict):
            suite_rows.setdefault(str(row.get("suite_id")), []).append(row)

    nonlocal_matrix_rows = [
        row for row in matrix.get("rows", []) if isinstance(row, dict) and row.get("method") != "local_Gauss6_FullVA"
    ]
    matrix_pairs = {(row.get("method"), row.get("example")) for row in nonlocal_matrix_rows}
    ledger_pairs = {(row.get("method"), row.get("example")) for row in rows if isinstance(row, dict)}

    checks.check(ledger.get("schema") == "b4-source-policy-row-closure-readiness-ledger-v1", "schema changed")
    checks.check(
        ledger.get("status")
        == "all_40_external_rows_mapped_20_attempted_not_reproducible_0_source_policy_rows_closed",
        "status changed",
    )
    checks.check(ledger.get("read_only") is True, "ledger must be read-only")
    checks.check(ledger.get("row_count") == len(rows) == 40, "ledger row count changed")
    checks.check(ledger.get("total_rows") == 40, "ledger total_rows alias changed")
    checks.check(ledger.get("source_policy_rows_total") == 40, "ledger source_policy_rows_total alias changed")
    checks.check(len(csv_rows) == 40, "CSV row count changed")
    checks.check(
        ledger.get("expected_external_row_count")
        == disposition.get("coverage", {}).get("expected_nonlocal_cells")
        == len(nonlocal_matrix_rows)
        == 40,
        "external row coverage changed",
    )
    checks.check(ledger_pairs == matrix_pairs, "ledger method/example coverage does not match paper matrix")
    checks.check({row.get("method") for row in rows} == EXPECTED_METHODS, "method set changed")
    checks.check({row.get("example") for row in rows} == EXPECTED_EXAMPLES, "example set changed")
    checks.check(ledger.get("source_policy_rows_closed") == 0, "ledger overcloses source-policy rows")
    checks.check(ledger.get("source_policy_rows_unclosed") == 40, "ledger unclosed row count changed")
    checks.check(ledger.get("source_policy_rows_open") == 20, "ledger open execution/promotion row count changed")
    checks.check(
        ledger.get("source_policy_rows_still_requiring_execution_or_promotion") == 20,
        "still-requiring-execution row count changed",
    )
    checks.check(
        ledger.get("source_policy_rows_attempted_not_reproducible") == 20,
        "attempted-not-reproducible row count changed",
    )
    checks.check(
        ledger.get("source_policy_rows_unable_to_reproduce") == 20,
        "unable-to-reproduce row count changed",
    )
    checks.check(ledger.get("external_superiority_ready_rows") == 0, "ledger overclaims external superiority rows")
    checks.check(ledger.get("rows_with_launch_command_refs") == 20, "command-mapped row count changed")
    checks.check(ledger.get("rows_without_launch_command_refs") == 20, "non-command-mapped row count changed")
    checks.check(
        ledger.get("rows_without_launch_command_refs_attempted_not_reproducible") == 20,
        "non-command attempted-not-reproducible row count changed",
    )
    checks.check(
        ledger.get("rows_demoted_related_work_proxy_for_current_claim") == 20,
        "current-claim demotion row count changed",
    )
    checks.check(ledger.get("ra2021_explicit_1e_4_rows") == 12, "RA2021 explicit 1e-4 row count changed")
    checks.check(ledger.get("hi2022_command_mapped_rows") == 8, "HI2022 command-mapped row count changed")
    checks.check(
        ledger.get("hi2022_existing_candidate_not_promoted_rows") == 7,
        "HI2022 existing candidate row count changed",
    )
    checks.check(
        ledger.get("hi2022_partial_or_failed_not_promoted_rows") == 1,
        "HI2022 partial/failed candidate row count changed",
    )
    checks.check(
        ledger.get("ra2021_ready_command_output_rows_not_promoted") == 12
        and ledger.get("ra2021_approved_driver_output_rows_not_promoted") == 12,
        "RA2021 ready-command output row count changed",
    )
    verified_authorized = post_execution.get("verified_authorized_execution_recorded") is True
    expected_ra_output_scope = (
        "verified_authorized_driver_output_presence_not_promoted"
        if verified_authorized
        else "legacy_ready_command_output_presence_not_verified_authorized_execution"
    )
    checks.check(
        ledger.get("ra2021_output_row_scope") == expected_ra_output_scope,
        "RA2021 output row scope missing",
    )
    checks.check(
        ledger.get("ra2021_approved_driver_output_rows_not_promoted") == 12,
        "RA2021 legacy approved-driver row-count alias changed",
    )
    checks.check(
        ledger.get("post_execution_decision_counts")
        == {"attempted_not_reproducible": 20, "not_promoted": 20},
        "post-execution decision counts changed",
    )
    checks.check(
        ledger.get("primary_promotion_blocker_counts") == EXPECTED_BLOCKER_COUNTS,
        "primary promotion-blocker counts changed",
    )
    checks.check(
        post_execution.get("approved_driver_execution_recorded") is verified_authorized
        and post_execution.get("verified_authorized_execution_recorded") is verified_authorized
        and post_execution.get("existing_ready_command_artifacts_present") is True
        and post_execution.get("promotion_decision", {}).get("source_policy_rows_closed_after_driver") == 0,
        "post-execution audit no-promotion boundary changed",
    )
    checks.check(
        ledger.get("ready_suite_count")
        == b4.get("execution_lane_summary", {}).get("ready_to_launch_after_explicit_opt_in_count")
        == 2,
        "ready suite count changed",
    )
    checks.check(
        ledger.get("not_ready_suite_count") == b4.get("execution_lane_summary", {}).get("not_ready_lane_count") == 2,
        "not-ready suite count changed",
    )
    checks.check(ledger.get("b4_can_close_now") is False, "ledger overcloses B4")
    checks.check(ledger.get("b7_can_close_now") is False, "ledger overcloses B7")
    checks.check(ledger.get("heavy_numerical_run_invoked") is False, "ledger invoked heavy run")
    checks.check(ledger.get("run_v047_invoked") is False, "ledger invoked run_v047")
    checks.check(ledger.get("v048_runner_invoked") is False, "ledger invoked v048")

    summary = {item.get("suite_id"): item for item in ledger.get("suite_summary", []) if isinstance(item, dict)}
    checks.check(set(summary) == set(EXPECTED_SUITE_ROWS), "suite summary set changed")
    for suite_id, expected_count in EXPECTED_SUITE_ROWS.items():
        checks.check(len(suite_rows.get(suite_id, [])) == expected_count, f"{suite_id} row count changed")
        checks.check(
            summary.get(suite_id, {}).get("source_policy_rows_total") == expected_count,
            f"{suite_id} summary total changed",
        )
        checks.check(
            summary.get(suite_id, {}).get("source_policy_rows_closed") == 0,
            f"{suite_id} overcloses rows",
        )
        if suite_id in {"tfe2026_original_pendulum", "vp2024_velocity_partitioning"}:
            checks.check(
                summary.get(suite_id, {}).get("source_policy_rows_attempted_not_reproducible")
                == expected_count,
                f"{suite_id} attempted-not-reproducible count changed",
            )
            checks.check(
                summary.get(suite_id, {}).get("source_policy_rows_unable_to_reproduce") == expected_count,
                f"{suite_id} unable-to-reproduce count changed",
            )
            checks.check(
                summary.get(suite_id, {}).get("source_policy_rows_still_requiring_execution_or_promotion")
                == 0,
                f"{suite_id} should not remain in execution queue",
            )
        else:
            checks.check(
                summary.get(suite_id, {}).get("source_policy_rows_attempted_not_reproducible") == 0,
                f"{suite_id} unexpectedly marked attempted-not-reproducible",
            )
            checks.check(
                summary.get(suite_id, {}).get("source_policy_rows_unable_to_reproduce") == 0,
                f"{suite_id} unexpectedly marked unable-to-reproduce",
            )
            checks.check(
                summary.get(suite_id, {}).get("source_policy_rows_still_requiring_execution_or_promotion")
                == expected_count,
                f"{suite_id} still-requiring-execution count changed",
            )
        checks.check(
            summary.get(suite_id, {}).get("b4_can_close_now") is False
            and summary.get(suite_id, {}).get("b7_can_close_now") is False,
            f"{suite_id} overcloses B4/B7",
        )
    checks.check(
        summary.get("tfe2026_original_pendulum", {}).get("rows_demoted_related_work_proxy_for_current_claim")
        == tfe_demotion_audit.get("demoted_related_work_proxy_rows_for_current_claim")
        == 16,
        "TFE suite demotion row count changed",
    )
    checks.check(
        summary.get("vp2024_velocity_partitioning", {}).get("rows_demoted_related_work_proxy_for_current_claim")
        == 4,
        "VP2024 suite demotion row count changed",
    )

    checks.check(
        all(row.get("source_policy_1e_4_opt_in_required") is True for row in suite_rows["ra2021_absolute_coordinate"]),
        "RA2021 rows should require explicit 1e-4 opt-in",
    )
    checks.check(
        all(row.get("command_refs") for row in suite_rows["ra2021_absolute_coordinate"]),
        "RA2021 rows should be command-mapped",
    )
    checks.check(
        all(
            row.get("readiness_status") == "approved_driver_outputs_present_not_promoted"
            for row in suite_rows["ra2021_absolute_coordinate"]
        ),
        "RA2021 readiness status changed",
    )
    checks.check(
        all(
            "preflight_only_not_run" not in row.get("command_artifact_statuses", [])
            for row in suite_rows["ra2021_absolute_coordinate"]
        ),
        "RA2021 rows fell back to pre-execution artifact status",
    )
    checks.check(
        sum(
            1
            for row in suite_rows["ra2021_absolute_coordinate"]
            if row.get("primary_promotion_blocker") == "ra2021_single_floor_limited_public_h_tranche_not_promoted"
        )
        == 3,
        "RA2021 single blocker count changed",
    )
    checks.check(
        sum(
            1
            for row in suite_rows["ra2021_absolute_coordinate"]
            if row.get("primary_promotion_blocker")
            == "ra2021_double_low_order_floor_limited_constraint_not_promoted"
        )
        == 3,
        "RA2021 double blocker count changed",
    )
    checks.check(
        sum(
            1
            for row in suite_rows["ra2021_absolute_coordinate"]
            if row.get("primary_promotion_blocker")
            == "ra2021_closed_loop_T0p1_mixed_reference_not_source_policy"
        )
        == 6,
        "RA2021 closed-loop blocker count changed",
    )
    hi_rows = suite_rows["hi2022_half_implicit"]
    checks.check(sum(1 for row in hi_rows if row.get("command_refs")) == 8, "HI2022 command row count changed")
    checks.check(
        sum(1 for row in hi_rows if row.get("readiness_status") == "selected_candidate_executed_not_promoted") == 7,
        "HI2022 executed-candidate row count changed",
    )
    checks.check(
        sum(1 for row in hi_rows if row.get("readiness_status") == "selected_candidate_partial_or_failed_not_promoted")
        == 1,
        "HI2022 partial/failed candidate row count changed",
    )
    checks.check(
        all(
            row.get("source_policy_1e_4_opt_in_required") is False
            for row in hi_rows
        ),
        "HI2022 rows should not require default 1e-4",
    )
    checks.check(
        sum(
            1
            for row in hi_rows
            if row.get("primary_promotion_blocker")
            == "hi2022_selected_coarse_trio_not_full_public_grid_not_promoted"
        )
        == 7,
        "HI2022 coarse-trio blocker count changed",
    )
    checks.check(
        sum(
            1
            for row in hi_rows
            if row.get("primary_promotion_blocker")
            == "hi2022_ra_half_double_partial_newton_failure_not_promoted"
        )
        == 1,
        "HI2022 rA_half double failure blocker count changed",
    )
    checks.check(
        all(
            row.get("readiness_status") == "attempted_not_reproducible"
            for row in suite_rows["tfe2026_original_pendulum"]
        ),
        "TFE readiness status changed",
    )
    checks.check(
        all(
            row.get("primary_promotion_blocker")
            in {
                "paper_spec_candidate_runner_not_source_policy_equivalent",
                "tfe_source_paper_pendulum_suite_does_not_define_this_mechanism_runner",
            }
            for row in suite_rows["tfe2026_original_pendulum"]
        ),
        "TFE blocker class changed",
    )
    checks.check(
        all(row.get("current_claim_requires_source_policy_execution") is False for row in suite_rows["tfe2026_original_pendulum"]),
        "TFE current-claim execution boundary changed",
    )
    checks.check(
        all(row.get("demotion_audit") == "TFE_B4_B7_SOURCE_POLICY_DEMOTION_AUDIT.json" for row in suite_rows["tfe2026_original_pendulum"]),
        "TFE demotion audit path changed",
    )
    checks.check(
        "TFE_PUBLIC_CODE_RECHECK_20260613.json" in ledger.get("source_files", []),
        "TFE public-code recheck certificate missing from source files",
    )
    checks.check(
        "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.json" in ledger.get("source_files", []),
        "2026-06-14 public-code refresh missing from source files",
    )
    checks.check(
        all(not row.get("command_refs") for row in suite_rows["tfe2026_original_pendulum"]),
        "TFE rows should not expose launch commands",
    )
    checks.check(
        all(row.get("readiness_status") == "attempted_not_reproducible" for row in suite_rows["vp2024_velocity_partitioning"]),
        "VP2024 readiness status changed",
    )
    checks.check(
        all(
            row.get("primary_promotion_blocker")
            == "distinct_public_vp2024_code_path_not_found_proxy_not_source_policy"
            for row in suite_rows["vp2024_velocity_partitioning"]
        ),
        "VP2024 blocker class changed",
    )
    checks.check(
        all(row.get("current_claim_requires_source_policy_execution") is False for row in suite_rows["vp2024_velocity_partitioning"]),
        "VP2024 current-claim execution boundary changed",
    )
    checks.check(
        all(row.get("demotion_audit") == "VP2024_CODE_PATH_DISPOSITION_AUDIT.json" for row in suite_rows["vp2024_velocity_partitioning"]),
        "VP2024 demotion audit path changed",
    )
    checks.check(
        "VP2024_PUBLIC_CODE_RECHECK_20260613.json" in ledger.get("source_files", []),
        "VP2024 public-code recheck certificate missing from source files",
    )
    checks.check(
        "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.json" in ledger.get("source_files", []),
        "2026-06-14 public-code refresh missing from source files",
    )
    checks.check(
        all(not row.get("command_refs") for row in suite_rows["vp2024_velocity_partitioning"]),
        "VP2024 rows should not expose launch commands",
    )

    for row in rows:
        if not isinstance(row, dict):
            checks.check(False, "row is not an object")
            continue
        checks.check(row.get("source_policy_closed") is False, f"{row.get('method')} {row.get('example')} overclosed")
        checks.check(
            row.get("post_execution_decision") in {"not_promoted", "attempted_not_reproducible"},
            "row promotion decision invalid",
        )
        checks.check(row.get("primary_promotion_blocker") in EXPECTED_BLOCKER_COUNTS, "row blocker class invalid")
        checks.check(row.get("promotion_evidence_ref"), "row promotion evidence ref missing")
        if row.get("suite_id") in {"tfe2026_original_pendulum", "vp2024_velocity_partitioning"}:
            checks.check(
                row.get("current_claim_requires_source_policy_execution") is False,
                f"{row.get('method')} {row.get('example')} current-claim demotion missing",
            )
            checks.check(
                row.get("source_policy_disposition") == "attempted_not_reproducible",
                f"{row.get('method')} {row.get('example')} missing not-reproducible disposition",
            )
            checks.check(
                row.get("self_reproduction_attempted") is True,
                f"{row.get('method')} {row.get('example')} missing self-reproduction attempt",
            )
            checks.check(
                row.get("unable_to_reproduce") is True,
                f"{row.get('method')} {row.get('example')} missing unable-to-reproduce marker",
            )
            checks.check(
                row.get("final_nonpublic_code_disposition") == "unable_to_reproduce_not_promoted",
                f"{row.get('method')} {row.get('example')} final nonpublic-code disposition changed",
            )
            checks.check(
                row.get("counts_as_open_execution_queue") is False,
                f"{row.get('method')} {row.get('example')} should not remain in execution queue",
            )
        else:
            checks.check(
                row.get("current_claim_requires_source_policy_execution") is True,
                f"{row.get('method')} {row.get('example')} unexpectedly demoted",
            )
            checks.check(
                row.get("source_policy_disposition") == "promotion_open",
                f"{row.get('method')} {row.get('example')} disposition changed",
            )
            checks.check(
                row.get("unable_to_reproduce") is False,
                f"{row.get('method')} {row.get('example')} public-root row misclassified as unable-to-reproduce",
            )
            checks.check(
                row.get("counts_as_open_execution_queue") is True,
                f"{row.get('method')} {row.get('example')} should remain in execution/promotion queue",
            )
        checks.check(row.get("external_superiority_ready") is False, f"{row.get('method')} {row.get('example')} overclaims")
        checks.check(row.get("b4_can_close_from_row") is False, f"{row.get('method')} {row.get('example')} closes B4")
        checks.check(row.get("b7_can_close_from_row") is False, f"{row.get('method')} {row.get('example')} closes B7")
        checks.check(row.get("blocking_reasons"), f"{row.get('method')} {row.get('example')} has no blockers")

    for token in [
        "Status: `all_40_external_rows_mapped_20_attempted_not_reproducible_0_source_policy_rows_closed`.",
        "External rows mapped: `40/40`.",
        "Source-policy rows closed/unclosed: `0/40`.",
        "Source-policy rows still requiring execution/promotion: `20`.",
        "Source-policy rows attempted-not-reproducible: `20`.",
        "Source-policy rows unable-to-reproduce/not-promoted: `20`.",
        "Rows with launch command refs: `20`.",
        "Rows without launch command refs: `20`.",
        "Rows without launch command refs attempted-not-reproducible: `20`.",
        "Rows demoted related-work/proxy for current claim: `20`.",
        "RA2021 ready-command output rows not promoted: `12`.",
        f"RA2021 output row scope: `{expected_ra_output_scope}`.",
        "HI2022 selected-candidate executed/partial rows not promoted: `7/1`.",
        "Post-execution decision counts: `{'attempted_not_reproducible': 20, 'not_promoted': 20}`.",
        "ra2021_double_low_order_floor_limited_constraint_not_promoted",
        "hi2022_ra_half_double_partial_newton_failure_not_promoted",
        "paper_spec_candidate_runner_not_source_policy_equivalent",
        "distinct_public_vp2024_code_path_not_found_proxy_not_source_policy",
        "Ready/not-ready suites: `2/2`.",
        "B4/B7 can close now: `False/False`.",
        "Heavy/run_v047/v048 invoked: `False/False/False`.",
        "`ra2021_absolute_coordinate`",
        "`tfe2026_original_pendulum`",
        "`hi2022_half_implicit`",
        "`vp2024_velocity_partitioning`",
        "this B4 ledger tracks all 40 external method/example cells",
    ]:
        checks.check(token in ledger_md, f"markdown missing token: {token}")

    if checks.errors:
        print("B4 source-policy row closure-readiness ledger validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("B4 source-policy row closure-readiness ledger validation: PASS")
    print("external_rows=40/40")
    print("source_policy_closed=0/40")
    print("attempted_not_reproducible=20")
    print("still_requiring_execution_or_promotion=20")
    print("rows_with_launch_command_refs=20")
    print("ready_not_ready_suites=2/2")
    print("b4_can_close_now=False")
    print("b7_can_close_now=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
