#!/usr/bin/env python3
"""Validate submission-manifest boundary synchronization."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent

EXPECTED_OC4_TRACEABILITY_TUPLE = "13/13/8/5/13/8/False/False"


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
        raise ValueError(f"{path.name} is not a JSON object")
    return data


def oc4_traceability_tuple(payload: dict[str, Any]) -> str | None:
    route = (
        payload.get("blocker_required_to_close_by_id", {})
        .get("OC4", {})
        .get("authorized_ra_hi_closeout_route", {})
    )
    if not isinstance(route, dict):
        return None
    value = route.get("expected_output_schema_command_traceability_tuple")
    return value if isinstance(value, str) else None


def main() -> int:
    checks = Checks()
    manifest = read_json(PAPER / "SUBMISSION_ARTIFACT_MANIFEST.json")
    repro = read_json(PAPER / "CMAME_REPRODUCIBILITY_PACKAGE_MANIFEST.json")
    objective = read_json(PAPER / "OBJECTIVE_COMPLETION_AUDIT.json")

    boundary = repro.get("narrowed_archive_boundary", {})
    sync = manifest.get("submission_artifact_manifest_boundary_sync", {})
    checks.check(
        (PAPER / "sync_submission_artifact_manifest_boundary.py").exists(),
        "sync script missing",
    )
    checks.check(
        sync.get("schema") == "submission-artifact-manifest-boundary-sync-v1",
        "sync schema missing or changed",
    )
    checks.check(
        sync.get("does_not_execute_source_policy_commands") is True,
        "sync boundary overpermits source-policy execution",
    )
    checks.check(
        manifest.get("narrowed_archive_boundary") == boundary,
        "submission manifest narrowed boundary drifted from reproducibility manifest",
    )
    checks.check(
        manifest.get("narrowed_archive_boundary_status") == boundary.get("status")
        and manifest.get("narrowed_archive_boundary_source_policy_closed_ratio")
        == boundary.get("source_policy_closed_ratio")
        and manifest.get(
            "narrowed_archive_boundary_current_archive_usable_as_full_source_policy_runner_archive"
        )
        == boundary.get("current_archive_usable_as_full_source_policy_runner_archive")
        and manifest.get("narrowed_archive_boundary_source_policy_execution_allowed_now")
        == boundary.get("source_policy_execution_allowed_now")
        and manifest.get("narrowed_archive_boundary_source_policy_execution_invoked")
        == boundary.get("source_policy_execution_invoked")
        and manifest.get("narrowed_archive_boundary_exact_b4_opt_in_required_for_execution")
        == boundary.get("exact_b4_opt_in_required_for_execution")
        and manifest.get("narrowed_archive_boundary_safe_action_ids")
        == boundary.get("safe_action_ids")
        and manifest.get("narrowed_archive_boundary_opt_in_action_ids")
        == boundary.get("opt_in_action_ids"),
        "submission manifest narrowed boundary aliases drifted",
    )
    checks.check(
        manifest.get("blocker_required_to_close_by_id")
        == manifest.get("objective_blocker_required_to_close_by_id")
        == objective.get("blocker_required_to_close_by_id")
        and manifest.get("blocker_safe_next_actions_by_id")
        == manifest.get("objective_blocker_safe_next_actions_by_id")
        == objective.get("blocker_safe_next_actions_by_id")
        and manifest.get("blocker_opt_in_required_actions_by_id")
        == manifest.get("objective_blocker_opt_in_required_actions_by_id")
        == objective.get("blocker_opt_in_required_actions_by_id"),
        "submission manifest objective blocker aliases drifted",
    )
    checks.check(
        manifest.get("narrowed_archive_boundary_source_policy_execution_invoked")
        == boundary.get("source_policy_execution_invoked")
        is False,
        "source-policy execution invoked flag changed",
    )
    checks.check(
        manifest.get("narrowed_archive_boundary_exact_b4_opt_in_required_for_execution")
        is True,
        "exact B4 opt-in requirement lost",
    )
    checks.check(
        oc4_traceability_tuple(boundary)
        == oc4_traceability_tuple(manifest.get("narrowed_archive_boundary", {}))
        == oc4_traceability_tuple(objective)
        == EXPECTED_OC4_TRACEABILITY_TUPLE,
        "OC4 expected-output schema traceability tuple drifted",
    )
    checks.check(
        sync.get("oc4_expected_output_schema_command_traceability_tuple")
        == EXPECTED_OC4_TRACEABILITY_TUPLE,
        "sync summary OC4 traceability tuple missing or stale",
    )

    if checks.errors:
        print("submission artifact manifest boundary sync validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("submission artifact manifest boundary sync validation: PASS")
    print(f"source_policy_execution_invoked={manifest.get('narrowed_archive_boundary_source_policy_execution_invoked')}")
    print(f"oc4_expected_output_schema_command_traceability_tuple={EXPECTED_OC4_TRACEABILITY_TUPLE}")
    print(f"blocking_ids={','.join(objective.get('blocking_ids', []))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
