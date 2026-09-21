#!/usr/bin/env python3
"""Validate the source-policy closure triage artifact."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent


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
        triage = read_json(PAPER / "SOURCE_POLICY_CLOSURE_TRIAGE.json")
        triage_md = read_text(PAPER / "SOURCE_POLICY_CLOSURE_TRIAGE.md")
        diagnosis = read_json(PAPER / "EXTERNAL_BASELINE_SOURCE_POLICY_DIAGNOSIS.json")
        comparison = read_json(PAPER / "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.json")
    except Exception as exc:  # noqa: BLE001
        print(f"source-policy closure triage validation: FAIL\n- {exc}")
        return 1

    scope = triage.get("triage_scope", {})
    closure = triage.get("closure_boundary", {})
    action_counts = scope.get("action_counts", {})

    checks.check(triage.get("schema") == "source-policy-closure-triage-v1", "schema changed")
    checks.check(
        triage.get("status") == "triage_only_source_policy_closure_not_run",
        "status changed",
    )
    checks.check(triage.get("submission_ready") is False, "triage must not mark submission ready")
    checks.check(triage.get("external_superiority_claim") is False, "triage must not claim external superiority")
    checks.check(
        triage.get("comparison_matrix_closed") == comparison.get("comparison_matrix_closed") is True,
        "comparison matrix closure mismatch",
    )
    checks.check(
        triage.get("common_reference_claim_allowed") == comparison.get("common_reference_claim_allowed") is True,
        "common-reference claim boundary mismatch",
    )
    checks.check(
        triage.get("source_policy_superiority_claim_allowed")
        == comparison.get("source_policy_superiority_claim_allowed")
        is False,
        "source-policy superiority boundary mismatch",
    )
    checks.check(scope.get("flagged_row_count") == len(diagnosis.get("diagnosis_rows", [])) == 15, "flagged row count changed")
    checks.check(
        set(scope.get("flagged_examples", []))
        == {"single_pendulum", "double_pendulum", "four_link", "slider_crank"},
        "flagged examples changed",
    )
    checks.check(scope.get("all_four_examples_covered_by_flagged_rows") is True, "all-example flagged coverage changed")
    checks.check(scope.get("flagged_by_suite", {}).get("ra2021_absolute_coordinate") == 5, "RA2021 flagged count changed")
    checks.check(scope.get("flagged_by_suite", {}).get("tfe2026_original_pendulum") == 4, "TFE flagged count changed")
    checks.check(scope.get("flagged_by_suite", {}).get("hi2022_half_implicit") == 3, "HI2022 flagged count changed")
    checks.check(scope.get("flagged_by_suite", {}).get("vp2024_velocity_partitioning") == 3, "VP2024 flagged count changed")
    checks.check(
        action_counts.get("fix_or_rerun_public_velocity_mapping_time_grid_norm_runtime") == 5,
        "RA2021 action count changed",
    )
    checks.check(
        action_counts.get("resolve_tfe_runner_friction_endpoint_then_rerun_or_demote") == 4,
        "TFE action count changed",
    )
    checks.check(
        action_counts.get("choose_full_T8_public_policy_or_demote") == 3,
        "HI2022 action count changed",
    )
    checks.check(
        action_counts.get("demote_until_velocity_partitioning_code_path_resolved") == 3,
        "VP action count changed",
    )
    checks.check(closure.get("b2_can_close_now") is False, "triage incorrectly closes B2")
    checks.check(closure.get("b4_can_close_now") is False, "triage incorrectly closes B4")
    checks.check(closure.get("default_1e_4_required") is False, "triage incorrectly requires default 1e-4")
    checks.check(closure.get("heavy_numerical_run_invoked") is False, "triage invoked heavy numerical run")
    checks.check(len(triage.get("triage_rows", [])) == 15, "triage row count changed")
    checks.check(len(triage.get("action_plan", [])) == 4, "action plan count changed")
    display_counts: dict[str, int] = {}
    for row in triage.get("triage_rows", []):
        if isinstance(row, dict):
            display = str(row.get("display_action"))
            display_counts[display] = display_counts.get(display, 0) + 1
            if row.get("suite") in {"tfe2026_original_pendulum", "vp2024_velocity_partitioning"}:
                checks.check(
                    row.get("display_action") == "attempted_not_reproducible_not_promoted",
                    f"nonpublic-code row display action stale: {row}",
                )
                checks.check(
                    row.get("post_public_code_disposition") == "attempted_not_reproducible_not_promoted",
                    f"nonpublic-code row disposition missing: {row}",
                )
    checks.check(
        display_counts.get("attempted_not_reproducible_not_promoted") == 7,
        "attempted-not-reproducible display count changed",
    )

    for token in [
        "TRIAGE ONLY - SOURCE-POLICY CLOSURE NOT RUN",
        "Flagged source-policy rows: `15`",
        "All four examples covered by flagged rows: `True`",
        "B2/B4 can close now: `False/False`",
        "`fix_or_rerun_public_velocity_mapping_time_grid_norm_runtime`",
        "`attempted_not_reproducible_not_promoted`",
        "`choose_full_T8_public_policy_or_demote`",
    ]:
        checks.check(token in triage_md, f"triage markdown missing token: {token}")

    if checks.errors:
        print("source-policy closure triage validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("source-policy closure triage validation: PASS")
    print("flagged_rows=15")
    print("flagged_examples=single_pendulum,double_pendulum,four_link,slider_crank")
    print("action_counts=5/4/3/3")
    print("b2_b4_can_close_now=False/False")
    print("heavy_numerical_run_invoked=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
