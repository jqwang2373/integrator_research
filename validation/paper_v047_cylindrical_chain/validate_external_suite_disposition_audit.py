#!/usr/bin/env python3
"""Validate the external suite disposition audit."""

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
        audit = read_json(PAPER / "EXTERNAL_SUITE_DISPOSITION_AUDIT.json")
        audit_md = read_text(PAPER / "EXTERNAL_SUITE_DISPOSITION_AUDIT.md")
        acceptance = read_json(PAPER / "EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.json")
        queue = read_json(PAPER / "EXTERNAL_SAME_TEST_RUN_QUEUE.json")
    except Exception as exc:  # noqa: BLE001
        print(f"external suite disposition audit validation: FAIL\n- {exc}")
        return 1

    closure = audit.get("closure_counts", {})
    boundary = audit.get("b2_b4_closure", {})
    claim = audit.get("claim_boundary", {})
    markers = audit.get("manuscript_disposition_markers", {})
    dispositions = audit.get("suite_dispositions", [])
    disposition_ids = {row.get("suite_id"): row.get("current_disposition") for row in dispositions}

    checks.check(audit.get("schema") == "external-suite-disposition-audit-v1", "schema changed")
    checks.check(audit.get("status") == "suite_dispositions_defined_not_closed", "status changed")
    checks.check(audit.get("submission_ready") is False, "audit must not mark submission ready")
    checks.check(audit.get("suite_count") == 4, "suite count changed")
    checks.check(audit.get("accepted_external_superiority_suite_count") == 0, "external superiority suite count changed")
    checks.check(audit.get("same_test_campaign_status") == "not_run", "same-test campaign status changed")
    checks.check(audit.get("external_superiority_claim") is False, "external superiority claim changed")
    checks.check(
        closure.get("parallel_ready_shards_without_default_1e_4")
        == queue.get("coverage_counts", {}).get("parallel_shard_count_without_default_1e-4")
        == 20,
        "parallel shard count changed",
    )
    checks.check(
        closure.get("accepted_external_dynamic_order_examples_count")
        == acceptance.get("acceptance_counts", {}).get("accepted_external_dynamic_order_examples_count")
        == 0,
        "accepted external dynamic-order example count changed",
    )
    checks.check(closure.get("flagged_source_policy_rows") == 15, "flagged source-policy count changed")
    checks.check(closure.get("position_aligned_velocity_mismatch_rows") == 10, "velocity mismatch count changed")
    checks.check(boundary.get("b2_can_close_now") is False, "B2 closure boundary changed")
    checks.check(boundary.get("b4_can_close_now") is False, "B4 closure boundary changed")
    checks.check(claim.get("external_superiority_allowed") is False, "external superiority boundary changed")
    checks.check(claim.get("default_1e_4_required") is False, "default 1e-4 policy changed")
    checks.check(disposition_ids.get("tfe2026_original_pendulum") == "encode_then_run_or_demote", "TFE disposition changed")
    checks.check(disposition_ids.get("ra2021_absolute_coordinate") == "run_remaining_same_test_or_bound_claim", "RA disposition changed")
    checks.check(disposition_ids.get("hi2022_half_implicit") == "choose_full_T8_run_or_demote", "HI disposition changed")
    checks.check(disposition_ids.get("vp2024_velocity_partitioning") == "demote_until_code_path_resolved", "VP disposition changed")
    for key in [
        "main_cross_paper_gate_table",
        "flat_cross_paper_gate_table",
        "main_source_policy_diagnosis_table",
        "flat_source_policy_diagnosis_table",
        "main_no_external_superiority",
        "flat_no_external_superiority",
    ]:
        checks.check(markers.get(key) is True, f"manuscript marker missing: {key}")
    for token in [
        "suite dispositions defined",
        "Suites classified: `4`",
        "Accepted external-superiority suites: `0`",
        "B2 can close now: `False`",
        "B4 can close now: `False`",
        "demote_until_code_path_resolved",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("external suite disposition audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("external suite disposition audit validation: PASS")
    print("suites=4")
    print("accepted_external_superiority_suite_count=0")
    print("parallel_ready_shards_without_default_1e_4=20")
    print("b2_can_close_now=False")
    print("b4_can_close_now=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
