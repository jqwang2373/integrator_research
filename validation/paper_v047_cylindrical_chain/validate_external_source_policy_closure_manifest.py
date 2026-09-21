#!/usr/bin/env python3
"""Validate the external source-policy closure manifest."""

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
        manifest = read_json(PAPER / "EXTERNAL_SOURCE_POLICY_CLOSURE_MANIFEST.json")
        manifest_md = read_text(PAPER / "EXTERNAL_SOURCE_POLICY_CLOSURE_MANIFEST.md")
        acceptance = read_json(PAPER / "EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.json")
        source_policy = read_json(PAPER / "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.json")
        suite_disposition = read_json(PAPER / "EXTERNAL_SUITE_DISPOSITION_AUDIT.json")
    except Exception as exc:  # noqa: BLE001
        print(f"external source-policy closure manifest validation: FAIL\n- {exc}")
        return 1

    perf = manifest.get("performance_matrix", {})
    common = manifest.get("common_reference_boundary", {})
    suite_ids = {row.get("suite_id") for row in manifest.get("suites", [])}
    reqs = {row.get("id"): row for row in manifest.get("closure_requirements", [])}
    dispositions = {row.get("suite_id"): row for row in suite_disposition.get("suite_dispositions", [])}

    checks.check(manifest.get("schema") == "external-source-policy-closure-manifest-v1", "schema changed")
    checks.check(
        manifest.get("status") == "not_closed_source_policy_reproduction_required",
        "status changed",
    )
    checks.check(manifest.get("submission_ready") is False, "manifest must not mark submission ready")
    checks.check(
        manifest.get("examples") == ["single_pendulum", "double_pendulum", "four_link", "slider_crank"],
        "example coverage changed",
    )
    checks.check(manifest.get("same_test_campaign_status") == "not_run", "same-test campaign status changed")
    checks.check(manifest.get("source_policy_reproduction") is False, "source-policy reproduction boundary changed")
    checks.check(manifest.get("external_superiority_claim_allowed") is False, "external superiority boundary changed")
    checks.check(
        manifest.get("paper_direct_error_superiority_claim_allowed") is False,
        "paper direct-error superiority boundary changed",
    )
    checks.check(manifest.get("b2_can_close_now") is False, "B2 closure changed")
    checks.check(manifest.get("b4_can_close_now") is False, "B4 closure changed")
    checks.check(perf.get("row_count") == 48, "performance row count changed")
    checks.check(perf.get("completed_row_count") == 32, "completed performance row count changed")
    checks.check(perf.get("not_complete_row_count") == 16, "not-complete performance row count changed")
    checks.check(perf.get("partial_row_count") == 0, "partial performance row count changed")
    checks.check(perf.get("external_superiority_claim") is False, "performance matrix overclaims superiority")
    checks.check(common.get("bounded_common_reference_diagnostic_rows") == 44, "bounded diagnostic count changed")
    checks.check(common.get("strict_external_error_claim_allowed_rows") == 0, "strict external claim rows changed")
    checks.check(common.get("all_method_example_cells_checked") == 44, "forensic cell count changed")
    checks.check(
        manifest.get("source_policy_flagged_rows")
        == source_policy.get("coverage", {}).get("flagged_row_count")
        == 15,
        "source-policy flagged rows changed",
    )
    checks.check(
        manifest.get("source_policy_flagged_raw_rows")
        == source_policy.get("coverage", {}).get("flagged_raw_row_count")
        == 45,
        "source-policy flagged raw rows changed",
    )
    checks.check(
        manifest.get("source_policy_flagged_by_suite")
        == source_policy.get("coverage", {}).get("flagged_by_suite"),
        "source-policy suite counts changed",
    )
    checks.check(manifest.get("parallel_ready_shards_without_default_1e_4") == 20, "parallel shard count changed")
    checks.check(manifest.get("default_1e_4_required") is False, "default 1e-4 policy changed")
    checks.check(manifest.get("heavy_numerical_run_invoked") is False, "manifest invoked heavy run")
    checks.check(
        set(manifest.get("runnable_parallel_suites", []))
        == {"ra2021_absolute_coordinate", "hi2022_half_implicit"},
        "runnable suite set changed",
    )
    checks.check(
        set(manifest.get("not_ready_or_demote_suites", []))
        == {"tfe2026_original_pendulum", "vp2024_velocity_partitioning"},
        "not-ready suite set changed",
    )
    checks.check(
        suite_ids
        == {
            "ra2021_absolute_coordinate",
            "hi2022_half_implicit",
            "tfe2026_original_pendulum",
            "vp2024_velocity_partitioning",
        },
        "suite ids changed",
    )
    for suite_id in suite_ids:
        suite = next(row for row in manifest.get("suites", []) if row.get("suite_id") == suite_id)
        checks.check(
            suite.get("accepted_for_external_superiority") is False,
            f"{suite_id} incorrectly accepted for external superiority",
        )
        checks.check(
            suite.get("current_disposition") == dispositions.get(suite_id, {}).get("current_disposition"),
            f"{suite_id} disposition not synchronized",
        )
    checks.check(
        reqs.get("SP2", {}).get("accepted_external_dynamic_order_examples_count")
        == acceptance.get("acceptance_counts", {}).get("accepted_external_dynamic_order_examples_count")
        == 0,
        "accepted external dynamic-order count changed",
    )
    checks.check(all(row.get("satisfied") is False for row in reqs.values()), "closure requirements should remain open")
    for token in [
        "not closed - source-policy reproduction required",
        "Performance rows: `32/48` completed.",
        "Strict external error-claim rows allowed: `0`.",
        "B2/B4 can close now: `False/False`.",
        "External superiority claim allowed: `False`.",
        "Kissel--Taves--Negrut absolute-coordinate suite",
        "Fang--Kissel--Zhang--Negrut half-implicit suite",
        "Chaturvedi--Sandu--Sandu TFE pendulum",
        "Kissel--Bakke--Negrut velocity-partitioning suite",
    ]:
        checks.check(token in manifest_md, f"markdown missing token: {token}")

    if checks.errors:
        print("external source-policy closure manifest validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("external source-policy closure manifest validation: PASS")
    print("performance_rows=32/48")
    print("strict_external_error_claim_rows=0")
    print("external_superiority_claim_allowed=False")
    print("b2_b4_can_close_now=False/False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
