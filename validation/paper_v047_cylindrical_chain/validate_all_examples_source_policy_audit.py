#!/usr/bin/env python3
"""Validate the all-example source-policy audit artifact."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
V048 = ROOT.parent / "numerics" / "v048_cross_paper_same_test_benchmarks"
EXAMPLES = {"single_pendulum", "double_pendulum", "four_link", "slider_crank"}


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
        audit = read_json(PAPER / "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.json")
        audit_md = read_text(PAPER / "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.md")
        diagnosis = read_json(PAPER / "EXTERNAL_BASELINE_SOURCE_POLICY_DIAGNOSIS.json")
        triage = read_json(PAPER / "SOURCE_POLICY_CLOSURE_TRIAGE.json")
        recomputation = read_json(PAPER / "COMMON_REFERENCE_ORDER_RECOMPUTATION_AUDIT.json")
        comparison = read_json(PAPER / "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.json")
        common_ref_src = read_text(V048 / "build_common_reference_error_audit.py")
        coarse_src = read_text(V048 / "run_coarse_four_example_order.py")
    except Exception as exc:  # noqa: BLE001
        print(f"all-examples source-policy audit validation: FAIL\n- {exc}")
        return 1

    coverage = audit.get("coverage", {})
    mechanics = audit.get("common_reference_mechanics", {})
    execution = audit.get("execution_policy", {})
    closure = audit.get("closure_boundary", {})
    suite_rows = audit.get("suite_policy_rows", {})
    row_audits = audit.get("row_audits", [])
    triage_crosscheck = audit.get("triage_crosscheck", {})

    checks.check(audit.get("schema") == "all-examples-source-policy-audit-v1", "schema changed")
    checks.check(
        audit.get("status") == "all_flagged_examples_checked_source_policy_reproduction_open",
        "status changed",
    )
    checks.check(audit.get("submission_ready") is False, "audit must not mark submission ready")
    checks.check(audit.get("external_superiority_claim") is False, "audit must not claim external superiority")
    checks.check(
        audit.get("source_policy_superiority_claim_allowed")
        == comparison.get("source_policy_superiority_claim_allowed")
        is False,
        "source-policy superiority boundary changed",
    )
    checks.check(audit.get("common_reference_claim_allowed") is True, "common-reference boundary changed")
    checks.check(audit.get("comparison_matrix_closed") is True, "comparison matrix closure changed")
    checks.check(execution.get("default_1e_4_required") is False, "audit incorrectly requires default 1e-4")
    checks.check(execution.get("heavy_numerical_run_invoked") is False, "audit invoked a heavy run")
    checks.check(execution.get("run_v047_invoked") is False, "audit invoked run_v047")
    checks.check(execution.get("audit_mode") == "read_only_static_and_existing_csv", "audit mode changed")

    checks.check(
        coverage.get("flagged_row_count") == diagnosis.get("coverage", {}).get("flagged_row_count") == 15,
        "flagged row count changed",
    )
    checks.check(coverage.get("flagged_raw_row_count") == 45, "flagged raw-row count changed")
    checks.check(set(coverage.get("flagged_examples", [])) == EXAMPLES, "flagged examples changed")
    checks.check(coverage.get("all_four_examples_covered") is True, "all-example coverage missing")
    checks.check(coverage.get("all_flagged_rows_have_three_step_sizes") is True, "three-step coverage missing")
    checks.check(coverage.get("flagged_by_example", {}).get("single_pendulum") == 8, "single count changed")
    checks.check(coverage.get("flagged_by_example", {}).get("double_pendulum") == 2, "double count changed")
    checks.check(coverage.get("flagged_by_example", {}).get("four_link") == 4, "four-link count changed")
    checks.check(coverage.get("flagged_by_example", {}).get("slider_crank") == 1, "slider-crank count changed")
    checks.check(coverage.get("flagged_by_suite", {}).get("ra2021_absolute_coordinate") == 5, "RA2021 count changed")
    checks.check(coverage.get("flagged_by_suite", {}).get("tfe2026_original_pendulum") == 4, "TFE count changed")
    checks.check(coverage.get("flagged_by_suite", {}).get("hi2022_half_implicit") == 3, "HI2022 count changed")
    checks.check(coverage.get("flagged_by_suite", {}).get("vp2024_velocity_partitioning") == 3, "VP2024 count changed")
    checks.check(
        coverage.get("diagnostic_category_counts", {}).get("position_aligned_velocity_mismatch") == 10,
        "position/velocity mismatch count changed",
    )

    checks.check(mechanics.get("step_sizes") == [0.1, 0.05, 0.025], "step sizes changed")
    checks.check(mechanics.get("t_end") == 0.1, "t_end changed")
    checks.check(mechanics.get("reference_h") == 0.0125, "reference_h changed")
    checks.check(
        mechanics.get("summary_order_mismatches") == recomputation.get("verification", {}).get("mismatch_count") == 0,
        "recomputed order mismatch count changed",
    )
    checks.check(mechanics.get("summary_cells_recomputed") == 44, "summary cell recomputation count changed")
    checks.check(mechanics.get("raw_ok_rows_recomputed") == 132, "raw ok row count changed")
    checks.check(mechanics.get("fixed_grid_public_replay_token_found") is True, "fixed-grid replay token missing")
    checks.check(mechanics.get("body_velocity_source_token_found") is True, "body.dr token missing")
    checks.check(mechanics.get("body_acceleration_source_token_found") is True, "body.ddr token missing")
    for token in [
        "run_public_fixed_grid_model",
        "np.linspace(0.0, params.t_end, steps + 1, endpoint=True)",
        "body.dr",
        "body.ddr",
        "linspace(0,T,int(T/h))",
    ]:
        checks.check(token in common_ref_src, f"common-reference runner missing token: {token}")
    for token in [
        "run_ra2021_rA_model_with_installed_step",
        "install_ra_newmark_family_step",
        "install_ra_tfe_m1_step",
        "install_ra_tfe_multinode_step",
        "install_ra_vp2024_coordinate_partitioning_step",
    ]:
        checks.check(token in coarse_src, f"coarse runner missing token: {token}")

    checks.check(set(suite_rows) == set(coverage.get("flagged_by_suite", {})), "suite policy keys changed")
    checks.check(suite_rows.get("ra2021_absolute_coordinate", {}).get("source_policy_closed") is False, "RA2021 incorrectly closed")
    checks.check(suite_rows.get("hi2022_half_implicit", {}).get("full_T8_public_policy_complete") is False, "HI2022 full T8 unexpectedly closed")
    checks.check(
        suite_rows.get("tfe2026_original_pendulum", {}).get("original_pendulum_source_policy_encoded") is False,
        "TFE original pendulum policy unexpectedly encoded",
    )
    checks.check(
        suite_rows.get("tfe2026_original_pendulum", {}).get("self_reproduction_disposition")
        == "attempted_not_reproducible_not_promoted",
        "TFE self-reproduction disposition not propagated",
    )
    checks.check(
        "attempted_not_reproducible_not_promoted"
        in suite_rows.get("tfe2026_original_pendulum", {}).get("closure_required", ""),
        "TFE closure-required text stale",
    )
    checks.check(
        suite_rows.get("vp2024_velocity_partitioning", {}).get("independent_velocity_partitioning_code_path_resolved") is False,
        "VP2024 source code path unexpectedly resolved",
    )
    checks.check(
        suite_rows.get("vp2024_velocity_partitioning", {}).get("self_reproduction_disposition")
        == "attempted_not_reproducible_not_promoted",
        "VP2024 self-reproduction disposition not propagated",
    )
    checks.check(
        "attempted_not_reproducible_not_promoted"
        in suite_rows.get("vp2024_velocity_partitioning", {}).get("closure_required", ""),
        "VP2024 closure-required text stale",
    )
    checks.check(len(row_audits) == 15, "row audit count changed")
    checks.check(all(row.get("source_policy_closed") is False for row in row_audits), "some source-policy rows marked closed")
    checks.check(all(row.get("all_three_step_sizes_present") is True for row in row_audits), "some rows lost three step sizes")
    checks.check(
        all(row.get("candidate_compared_on_shared_reference_norm") is True for row in row_audits),
        "some rows lost common-reference comparison marker",
    )

    checks.check(closure.get("all_source_policy_rows_closed") is False, "audit incorrectly closes all rows")
    checks.check(closure.get("b2_can_close_now") is False, "audit incorrectly closes B2")
    checks.check(closure.get("b4_can_close_now") is False, "audit incorrectly closes B4")
    checks.check(closure.get("source_policy_reproduction_open") is True, "source-policy reproduction boundary changed")
    checks.check(
        closure.get("source_policy_audit_is_not_method_correctness_judgment") is True,
        "method-correctness boundary missing",
    )
    checks.check(
        closure.get("source_policy_audit_is_not_external_superiority_evidence") is True,
        "external-superiority boundary missing",
    )
    checks.check(
        triage_crosscheck.get("triage_flagged_row_count")
        == triage.get("triage_scope", {}).get("flagged_row_count")
        == 15,
        "triage crosscheck count changed",
    )
    checks.check(triage_crosscheck.get("triage_b2_can_close_now") is False, "triage B2 crosscheck changed")
    checks.check(triage_crosscheck.get("triage_b4_can_close_now") is False, "triage B4 crosscheck changed")

    for token in [
        "ALL FLAGGED EXAMPLES CHECKED - SOURCE-POLICY REPRODUCTION OPEN",
        "Flagged rows checked: `15`",
        "Flagged raw rows checked: `45`",
        "All four examples covered: `True`",
        "All rows have `h=[0.1,0.05,0.025]`: `True`",
        "Source-policy superiority allowed: `False`",
        "B2/B4 can close now: `False/False`",
        "Heavy numerical run invoked: `False`",
        "`ra2021_absolute_coordinate`",
        "`hi2022_half_implicit`",
        "`tfe2026_original_pendulum`",
        "`vp2024_velocity_partitioning`",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("all-examples source-policy audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("all-examples source-policy audit validation: PASS")
    print("flagged_rows=15")
    print("flagged_raw_rows=45")
    print("flagged_examples=single_pendulum,double_pendulum,four_link,slider_crank")
    print("suite_counts=5/4/3/3")
    print("b2_b4_can_close_now=False/False")
    print("heavy_numerical_run_invoked=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
