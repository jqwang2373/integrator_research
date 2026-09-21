#!/usr/bin/env python3
"""Build a narrowed-claim reproducibility package audit.

This audit consolidates the replay package and local accepted-row runners that
support the current narrowed manuscript claim. It deliberately keeps the full
source-policy runner package open.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "CMAME_NARROWED_REPRODUCIBILITY_PACKAGE_AUDIT.json"
OUT_MD = PAPER / "CMAME_NARROWED_REPRODUCIBILITY_PACKAGE_AUDIT.md"


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def main() -> None:
    review = read_json(PAPER / "CMAME_REVIEW_AGENT_REPORT.json")
    minimal = read_json(PAPER / "CMAME_MINIMAL_REPRODUCIBILITY_CANDIDATE_MANIFEST.json")
    companion = read_json(PAPER / "CMAME_LOCAL_ACCEPTED_RUNNER_COMPANION_MANIFEST.json")
    b6 = read_json(PAPER / "B6_FOUR_EXAMPLE_LOCAL_EVIDENCE_SUMMARY.json")
    p1 = read_json(PAPER / "CMAME_P1_LOCAL_RUNNER_EXTRACTION_AUDIT.json")
    closed_loop = read_json(PAPER / "CMAME_CLOSED_LOOP_LOCAL_RUNNER_CANDIDATE_MANIFEST.json")
    runner_centered = read_json(PAPER / "CMAME_RUNNER_CENTERED_REPRODUCIBILITY_AUDIT.json")
    extraction = read_json(PAPER / "CMAME_SELF_CONTAINED_RUNNER_EXTRACTION_PLAN.json")
    b4_handoff = read_json(PAPER / "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json")
    bundle_manifest = read_json(PAPER / "cmame_narrowed_repro_bundle" / "MANIFEST.json")
    bundle_summary = read_json(
        PAPER
        / "cmame_narrowed_repro_bundle"
        / "results"
        / "narrowed_repro_bundle_summary.json"
    )

    result_checks = review.get("result_checks", {})
    source_rows_closed = result_checks.get("source_policy_apples_to_apples_external_rows")
    source_rows_total = result_checks.get("source_policy_apples_to_apples_external_total_rows")
    expected_examples = ["single_pendulum", "double_pendulum", "four_link", "slider_crank"]
    self_contained_examples = list(b6.get("self_contained_examples", []))
    replay_only_examples = list(b6.get("replay_only_examples", []))
    b4_guarded_driver = b4_handoff.get("approval_boundary", {}).get(
        "guarded_execution_driver", {}
    )
    source_policy_execution_handoff = {
        "status": b4_handoff.get("status"),
        "execution_authorized": b4_handoff.get("execution_authorized"),
        "commands_not_run_by_handoff": b4_handoff.get("commands_not_run_by_handoff"),
        "exact_required_user_approval_statement": b4_handoff.get(
            "approval_boundary", {}
        ).get("exact_required_user_approval_statement"),
        "guarded_execution_driver": b4_guarded_driver.get("path"),
        "driver_requires_exact_approval": b4_guarded_driver.get(
            "requires_exact_approval_argument"
        ),
        "driver_does_not_authorize_execution": b4_guarded_driver.get(
            "driver_does_not_authorize_execution"
        ),
        "opt_in_required_command_count": b4_handoff.get("opt_in_required_actions", {}).get(
            "command_count"
        ),
        "opt_in_required_mapped_external_rows": b4_handoff.get(
            "opt_in_required_actions", {}
        ).get("mapped_external_rows"),
        "terminal_unable_to_reproduce_rows": b4_handoff.get("source_policy_row_state", {}).get(
            "unable_to_reproduce"
        ),
    }

    narrowed_ready = (
        review.get("narrowed_submission_standard_met") is True
        and review.get("narrowed_claim_decision") == "submit_under_narrowed_claim"
        and review.get("submission_standard_scope") == "global_submission_standard"
        and review.get("global_submission_standard_met") is False
        and minimal.get("read_only_replay_package") is True
        and companion.get("launcher_passed") is True
        and companion.get("local_accepted_rows_runner_available") is True
        and companion.get("local_rows") == 12
        and b6.get("b6_local_evidence_runner_passed") is True
        and b6.get("human_runnable_four_example_self_contained_simulation_ready") is True
        and self_contained_examples == expected_examples
        and replay_only_examples == []
        and p1.get("p1_single_runner_candidate_ready") is True
        and p1.get("p1_double_runner_candidate_ready") is True
        and p1.get("p1_regenerated_candidate_rows") == p1.get("p1_required_rows") == 6
        and p1.get("p1_missing_candidate_rows") == 0
        and closed_loop.get("runner_passed") is True
        and closed_loop.get("self_contained_simulation_runner") is True
        and closed_loop.get("closed_loop_local_rows") == 6
        and source_rows_closed == 0
        and source_rows_total == 40
        and companion.get("full_source_policy_runner_package_ready") is False
        and runner_centered.get("full_source_policy_runner_package_ready") is False
        and extraction.get("full_source_policy_self_contained_runner_ready") is False
        and bundle_manifest.get("status")
        == "narrowed_repro_bundle_ready_replay_plus_local_runners_source_policy_open"
        and bundle_summary.get("status") == "pass"
        and bundle_summary.get("source_policy_rows_closed") == 0
        and bundle_summary.get("source_policy_rows_total") == 40
        and bundle_summary.get("full_source_policy_runner_package_ready") is False
    )

    output: dict[str, Any] = {
        "schema": "cmame-narrowed-reproducibility-package-audit-v1",
        "status": (
            "narrowed_claim_reproducibility_package_ready_full_source_policy_open"
            if narrowed_ready
            else "narrowed_claim_reproducibility_package_open"
        ),
        "read_only": True,
        "submission_ready": False,
        "narrowed_claim_submission_standard_met": review.get("narrowed_submission_standard_met"),
        "narrowed_claim_decision": review.get("narrowed_claim_decision"),
        "submission_standard_scope": review.get("submission_standard_scope"),
        "global_submission_standard_met": review.get("global_submission_standard_met"),
        "narrowed_claim_reproducibility_package_ready": narrowed_ready,
        "full_source_policy_runner_package_ready": False,
        "source_policy_external_superiority_allowed": False,
        "source_policy_execution_handoff": source_policy_execution_handoff,
        "source_policy_execution_allowed_now": b4_handoff.get("source_policy_execution_allowed_now"),
        "source_policy_execution_invoked": b4_handoff.get("source_policy_execution_invoked"),
        "exact_b4_opt_in_required_for_execution": b4_handoff.get(
            "exact_b4_opt_in_required_for_execution"
        ),
        "safe_action_ids": b4_handoff.get("safe_action_ids"),
        "opt_in_action_ids": b4_handoff.get("opt_in_action_ids"),
        "required_user_approval_statement": (
            b4_handoff.get("required_user_approval_statement")
            or b4_handoff.get("exact_approval_statement")
            or b4_handoff.get("opt_in_required_phrase")
        ),
        "guarded_execution_driver": b4_handoff.get("guarded_execution_driver"),
        "source_policy_rows_closed": source_rows_closed,
        "source_policy_rows_total": source_rows_total,
        "minimal_replay_package": {
            "status": minimal.get("status"),
            "read_only_replay_package": minimal.get("read_only_replay_package"),
            "candidate_file_count": minimal.get("candidate_file_count"),
            "candidate_python_file_count": minimal.get("candidate_python_file_count"),
            "candidate_python_line_count": minimal.get("candidate_python_line_count"),
            "runner_centered": minimal.get("reviewer_facing_code_policy", {}).get(
                "candidate_runner_centered"
            ),
        },
        "local_accepted_runner_companion": {
            "status": companion.get("status"),
            "launcher_passed": companion.get("launcher_passed"),
            "local_rows": companion.get("local_rows"),
            "candidate_python_line_count": companion.get("candidate_python_line_count"),
            "runner_commands": companion.get("runner_commands"),
            "full_source_policy_runner_package_ready": companion.get(
                "full_source_policy_runner_package_ready"
            ),
        },
        "human_runnable_local_evidence": {
            "runner_passed": b6.get("b6_local_evidence_runner_passed"),
            "local_rows": b6.get("local_rows"),
            "self_contained_examples": self_contained_examples,
            "replay_only_examples": replay_only_examples,
            "four_example_self_contained_simulation_ready": b6.get(
                "human_runnable_four_example_self_contained_simulation_ready"
            ),
        },
        "p1_runner_candidates": {
            "single_ready": p1.get("p1_single_runner_candidate_ready"),
            "double_ready": p1.get("p1_double_runner_candidate_ready"),
            "regenerated_rows": p1.get("p1_regenerated_candidate_rows"),
            "required_rows": p1.get("p1_required_rows"),
            "missing_rows": p1.get("p1_missing_candidate_rows"),
        },
        "closed_loop_runner_candidate": {
            "status": closed_loop.get("status"),
            "runner_passed": closed_loop.get("runner_passed"),
            "self_contained_simulation_runner": closed_loop.get("self_contained_simulation_runner"),
            "closed_loop_local_rows": closed_loop.get("closed_loop_local_rows"),
            "closed_loop_models": closed_loop.get("closed_loop_models"),
            "candidate_python_line_count": closed_loop.get("candidate_python_line_count"),
        },
        "narrowed_repro_bundle": {
            "manifest_status": bundle_manifest.get("status"),
            "summary_status": bundle_summary.get("status"),
            "entrypoint": bundle_manifest.get("entrypoint"),
            "report": bundle_summary.get("report"),
            "source_policy_rows_closed": bundle_summary.get("source_policy_rows_closed"),
            "source_policy_rows_total": bundle_summary.get("source_policy_rows_total"),
            "full_source_policy_runner_package_ready": bundle_summary.get(
                "full_source_policy_runner_package_ready"
            ),
            "submission_ready": bundle_summary.get("submission_ready"),
            "run_v047_invoked": bundle_summary.get("run_v047_invoked"),
            "run_v048_invoked": bundle_summary.get("run_v048_invoked"),
        },
        "package_boundary": {
            "accepted_use": "reviewer_facing_narrowed_claim_reproducibility_package",
            "not_a_source_policy_runner_archive": True,
            "minimal_replay_boundary_preserved": minimal.get("read_only_replay_package") is True,
            "local_runners_are_existing_self_contained_candidates": True,
            "full_source_policy_deferred_until_rows_close": True,
            "source_policy_rows_required_for_full_package": 40,
            "source_policy_rows_closed_now": source_rows_closed,
        },
        "source_files": {
            "review_agent": "CMAME_REVIEW_AGENT_REPORT.json",
            "minimal_replay_manifest": "CMAME_MINIMAL_REPRODUCIBILITY_CANDIDATE_MANIFEST.json",
            "local_runner_companion": "CMAME_LOCAL_ACCEPTED_RUNNER_COMPANION_MANIFEST.json",
            "b6_local_evidence": "B6_FOUR_EXAMPLE_LOCAL_EVIDENCE_SUMMARY.json",
            "p1_local_runner_audit": "CMAME_P1_LOCAL_RUNNER_EXTRACTION_AUDIT.json",
            "closed_loop_runner_candidate": "CMAME_CLOSED_LOOP_LOCAL_RUNNER_CANDIDATE_MANIFEST.json",
            "narrowed_repro_bundle_manifest": "cmame_narrowed_repro_bundle/MANIFEST.json",
            "narrowed_repro_bundle_summary": "cmame_narrowed_repro_bundle/results/narrowed_repro_bundle_summary.json",
            "runner_centered_audit": "CMAME_RUNNER_CENTERED_REPRODUCIBILITY_AUDIT.json",
            "self_contained_extraction_plan": "CMAME_SELF_CONTAINED_RUNNER_EXTRACTION_PLAN.json",
            "b4_source_policy_execution_handoff_package": "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json",
        },
    }

    OUT_JSON.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# CMAME Narrowed Reproducibility Package Audit",
        "",
        f"Status: **{output['status']}**.",
        "",
        f"- Narrowed-claim reproducibility package ready: `{narrowed_ready}`.",
        f"- Global submission ready: `{output['submission_ready']}`.",
        f"- Submission standard scope: `{output['submission_standard_scope']}`.",
        f"- Full source-policy runner package ready: `{output['full_source_policy_runner_package_ready']}`.",
        f"- Source-policy rows closed: `{source_rows_closed}/{source_rows_total}`.",
        f"- Source-policy execution allowed now/invoked/exact opt-in required: `{output['source_policy_execution_allowed_now']}/{output['source_policy_execution_invoked']}/{output['exact_b4_opt_in_required_for_execution']}`.",
        f"- Safe action ids: `{output['safe_action_ids']}`; opt-in action ids: `{output['opt_in_action_ids']}`.",
        f"- Source-policy execution handoff exact approval/driver: `{source_policy_execution_handoff['exact_required_user_approval_statement']}/{source_policy_execution_handoff['guarded_execution_driver']}/{source_policy_execution_handoff['driver_requires_exact_approval']}/{source_policy_execution_handoff['driver_does_not_authorize_execution']}/{source_policy_execution_handoff['opt_in_required_command_count']}/{source_policy_execution_handoff['opt_in_required_mapped_external_rows']}`.",
        f"- Source-policy execution handoff authorized/commands-not-run/terminal-unable: `{source_policy_execution_handoff['execution_authorized']}/{source_policy_execution_handoff['commands_not_run_by_handoff']}/{source_policy_execution_handoff['terminal_unable_to_reproduce_rows']}`.",
        "",
        "## Included Current-Scope Evidence",
        "",
        f"- Minimal replay package/status/files/Python lines: `{minimal.get('status')}/{minimal.get('candidate_file_count')}/{minimal.get('candidate_python_line_count')}`.",
        f"- Local accepted-row companion/status/rows/Python lines: `{companion.get('status')}/{companion.get('local_rows')}/{companion.get('candidate_python_line_count')}`.",
        f"- Self-contained examples: `{self_contained_examples}`.",
        f"- Replay-only examples: `{replay_only_examples}`.",
        f"- P1 single/double runner ready: `{p1.get('p1_single_runner_candidate_ready')}/{p1.get('p1_double_runner_candidate_ready')}`.",
        f"- Closed-loop runner/models/rows: `{closed_loop.get('closed_loop_models')}/{closed_loop.get('closed_loop_local_rows')}`.",
        f"- Narrowed bundle/status/report: `{bundle_summary.get('status')}/{bundle_summary.get('report')}`.",
        "",
        "## Boundary",
        "",
        "This is a reviewer-facing package for the narrowed current claim. It is not a full source-policy runner archive, and it does not promote any source-policy rows.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("cmame_narrowed_reproducibility_package_audit=written")
    print(f"narrowed_claim_reproducibility_package_ready={narrowed_ready}")
    print(f"source_policy_rows={source_rows_closed}/{source_rows_total}")
    print(f"source_policy_execution_allowed_now={output['source_policy_execution_allowed_now']}")
    print(f"source_policy_execution_invoked={output['source_policy_execution_invoked']}")


if __name__ == "__main__":
    main()
