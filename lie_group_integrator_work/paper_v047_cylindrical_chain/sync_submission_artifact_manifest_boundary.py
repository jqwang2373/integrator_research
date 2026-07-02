#!/usr/bin/env python3
"""Synchronize submission-manifest boundary aliases from authoritative audits.

This is a read-only-boundary maintenance step: it rewrites only
SUBMISSION_ARTIFACT_MANIFEST.json metadata from existing objective and
reproducibility manifests. It does not execute source-policy commands.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
SUBMISSION_MANIFEST = PAPER / "SUBMISSION_ARTIFACT_MANIFEST.json"
REPRO_MANIFEST = PAPER / "CMAME_REPRODUCIBILITY_PACKAGE_MANIFEST.json"
OBJECTIVE_AUDIT = PAPER / "OBJECTIVE_COMPLETION_AUDIT.json"

BOUNDARY_ALIAS_MAP = {
    "narrowed_archive_boundary_status": "status",
    "narrowed_archive_boundary_source_policy_closed_ratio": "source_policy_closed_ratio",
    "narrowed_archive_boundary_current_archive_usable_as_full_source_policy_runner_archive": (
        "current_archive_usable_as_full_source_policy_runner_archive"
    ),
    "narrowed_archive_boundary_source_policy_execution_allowed_now": (
        "source_policy_execution_allowed_now"
    ),
    "narrowed_archive_boundary_source_policy_execution_invoked": (
        "source_policy_execution_invoked"
    ),
    "narrowed_archive_boundary_exact_b4_opt_in_required_for_execution": (
        "exact_b4_opt_in_required_for_execution"
    ),
    "narrowed_archive_boundary_safe_action_ids": "safe_action_ids",
    "narrowed_archive_boundary_opt_in_action_ids": "opt_in_action_ids",
    "narrowed_archive_boundary_required_user_approval_statement": (
        "required_user_approval_statement"
    ),
    "narrowed_archive_boundary_guarded_execution_driver": "guarded_execution_driver",
}

BLOCKER_ALIAS_MAP = {
    "blocker_required_to_close_by_id": "blocker_required_to_close_by_id",
    "blocker_safe_next_actions_by_id": "blocker_safe_next_actions_by_id",
    "blocker_opt_in_required_actions_by_id": "blocker_opt_in_required_actions_by_id",
    "objective_blocker_required_to_close_by_id": "blocker_required_to_close_by_id",
    "objective_blocker_safe_next_actions_by_id": "blocker_safe_next_actions_by_id",
    "objective_blocker_opt_in_required_actions_by_id": "blocker_opt_in_required_actions_by_id",
}


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path.name} is not a JSON object")
    return data


def oc4_traceability_tuple(boundary: dict[str, Any]) -> str | None:
    route = (
        boundary.get("blocker_required_to_close_by_id", {})
        .get("OC4", {})
        .get("authorized_ra_hi_closeout_route", {})
    )
    if not isinstance(route, dict):
        return None
    value = route.get("expected_output_schema_command_traceability_tuple")
    return value if isinstance(value, str) else None


def main() -> None:
    manifest = read_json(SUBMISSION_MANIFEST)
    repro = read_json(REPRO_MANIFEST)
    objective = read_json(OBJECTIVE_AUDIT)

    boundary = repro.get("narrowed_archive_boundary")
    if not isinstance(boundary, dict):
        raise ValueError("CMAME_REPRODUCIBILITY_PACKAGE_MANIFEST.json lacks narrowed_archive_boundary")

    manifest["narrowed_archive_boundary"] = boundary
    for manifest_key, boundary_key in BOUNDARY_ALIAS_MAP.items():
        manifest[manifest_key] = boundary.get(boundary_key)

    for manifest_key, objective_key in BLOCKER_ALIAS_MAP.items():
        manifest[manifest_key] = objective.get(objective_key)

    manifest["submission_artifact_manifest_boundary_sync"] = {
        "schema": "submission-artifact-manifest-boundary-sync-v1",
        "authoritative_inputs": [
            "CMAME_REPRODUCIBILITY_PACKAGE_MANIFEST.json",
            "OBJECTIVE_COMPLETION_AUDIT.json",
        ],
        "synchronized_boundary": "narrowed_archive_boundary",
        "synchronized_boundary_aliases": sorted(BOUNDARY_ALIAS_MAP),
        "synchronized_blocker_aliases": sorted(BLOCKER_ALIAS_MAP),
        "narrowed_archive_boundary_matches_reproducibility_manifest": True,
        "objective_blocker_aliases_match_objective_audit": True,
        "source_policy_execution_invoked": boundary.get("source_policy_execution_invoked"),
        "oc4_expected_output_schema_command_traceability_tuple": oc4_traceability_tuple(boundary),
        "does_not_execute_source_policy_commands": True,
    }

    SUBMISSION_MANIFEST.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print("submission_artifact_manifest_boundary_sync=written")
    print(
        "narrowed_archive_boundary_matches_reproducibility_manifest="
        f"{manifest['narrowed_archive_boundary'] == boundary}"
    )
    print(
        "objective_blocker_aliases_match_objective_audit="
        f"{manifest['objective_blocker_required_to_close_by_id'] == objective.get('blocker_required_to_close_by_id')}"
    )
    print(
        "source_policy_execution_invoked="
        f"{manifest.get('narrowed_archive_boundary_source_policy_execution_invoked')}"
    )
    print(
        "oc4_expected_output_schema_command_traceability_tuple="
        f"{oc4_traceability_tuple(boundary)}"
    )


if __name__ == "__main__":
    main()
