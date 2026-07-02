#!/usr/bin/env python3
"""Validate the narrowed-claim reproducibility package audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
JSON_PATH = PAPER / "CMAME_NARROWED_REPRODUCIBILITY_PACKAGE_AUDIT.json"
MD_PATH = PAPER / "CMAME_NARROWED_REPRODUCIBILITY_PACKAGE_AUDIT.md"
EXPECTED_APPROVAL = (
    "I explicitly approve running the B4 source-policy execution commands listed in "
    "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json."
)
EXPECTED_SAFE_ACTION_IDS = [
    "rebuild_read_only_audit_chain",
    "rerun_read_only_validators",
    "keep_narrowed_archive_provenance_only",
    "monitor_reopen_conditions",
]
EXPECTED_OPT_IN_ACTION_IDS = ["authorized_b4_ra_hi_source_policy_execution"]


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
        audit = read_json(JSON_PATH)
        md = read_text(MD_PATH)
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
    except Exception as exc:  # noqa: BLE001
        print(f"CMAME narrowed reproducibility package audit validation: FAIL\n- {exc}")
        return 1

    result_checks = review.get("result_checks", {})
    checks.check(
        audit.get("schema") == "cmame-narrowed-reproducibility-package-audit-v1",
        "schema changed",
    )
    checks.check(
        audit.get("status")
        == "narrowed_claim_reproducibility_package_ready_full_source_policy_open",
        "status changed",
    )
    checks.check(audit.get("read_only") is True, "audit must be read-only")
    checks.check(audit.get("submission_ready") is False, "audit overclaims global submission readiness")
    checks.check(audit.get("narrowed_claim_submission_standard_met") is True, "narrowed standard missing")
    checks.check(
        audit.get("narrowed_claim_decision") == "submit_under_narrowed_claim",
        "narrowed decision changed",
    )
    checks.check(audit.get("submission_standard_scope") == "global_submission_standard", "scope changed")
    checks.check(audit.get("global_submission_standard_met") is False, "global standard overclaimed")
    checks.check(
        audit.get("narrowed_claim_reproducibility_package_ready") is True,
        "narrowed package readiness missing",
    )
    checks.check(
        audit.get("full_source_policy_runner_package_ready") is False,
        "full source-policy package overclaimed",
    )
    checks.check(audit.get("source_policy_external_superiority_allowed") is False, "superiority overclaimed")
    handoff = audit.get("source_policy_execution_handoff", {})
    checks.check(
        handoff.get("status")
        == b4_handoff.get("status")
        == "source_policy_execution_handoff_ready_not_authorized_not_run",
        "B4 handoff status not carried into narrowed package audit",
    )
    checks.check(
        handoff.get("execution_authorized") == b4_handoff.get("execution_authorized") is False
        and handoff.get("commands_not_run_by_handoff")
        == b4_handoff.get("commands_not_run_by_handoff")
        is True,
        "B4 handoff authorization boundary changed in narrowed package audit",
    )
    checks.check(
        handoff.get("exact_required_user_approval_statement")
        == b4_handoff.get("approval_boundary", {}).get("exact_required_user_approval_statement")
        == "I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json.",
        "B4 exact approval not carried into narrowed package audit",
    )
    checks.check(
        handoff.get("guarded_execution_driver")
        == b4_handoff.get("approval_boundary", {})
        .get("guarded_execution_driver", {})
        .get("path")
        == "run_b4_source_policy_after_opt_in.sh"
        and handoff.get("driver_requires_exact_approval")
        == b4_handoff.get("approval_boundary", {})
        .get("guarded_execution_driver", {})
        .get("requires_exact_approval_argument")
        is True
        and handoff.get("driver_does_not_authorize_execution")
        == b4_handoff.get("approval_boundary", {})
        .get("guarded_execution_driver", {})
        .get("driver_does_not_authorize_execution")
        is True,
        "B4 guarded driver boundary not carried into narrowed package audit",
    )
    checks.check(
        handoff.get("opt_in_required_command_count")
        == b4_handoff.get("opt_in_required_actions", {}).get("command_count")
        == 13
        and handoff.get("opt_in_required_mapped_external_rows")
        == b4_handoff.get("opt_in_required_actions", {}).get("mapped_external_rows")
        == 20
        and handoff.get("terminal_unable_to_reproduce_rows")
        == b4_handoff.get("source_policy_row_state", {}).get("unable_to_reproduce")
        == 20,
        "B4 handoff opt-in/terminal counts changed in narrowed package audit",
    )
    checks.check(
        audit.get("source_policy_execution_allowed_now")
        == b4_handoff.get("source_policy_execution_allowed_now")
        is False
        and audit.get("source_policy_execution_invoked")
        == b4_handoff.get("source_policy_execution_invoked")
        is False
        and audit.get("exact_b4_opt_in_required_for_execution")
        == b4_handoff.get("exact_b4_opt_in_required_for_execution")
        is True
        and audit.get("safe_action_ids")
        == b4_handoff.get("safe_action_ids")
        == EXPECTED_SAFE_ACTION_IDS
        and audit.get("opt_in_action_ids")
        == b4_handoff.get("opt_in_action_ids")
        == EXPECTED_OPT_IN_ACTION_IDS
        and audit.get("required_user_approval_statement") == EXPECTED_APPROVAL
        and audit.get("guarded_execution_driver") == "run_b4_source_policy_after_opt_in.sh",
        "top-level source-policy execution aliases stale",
    )
    checks.check(
        audit.get("source_policy_rows_closed")
        == result_checks.get("source_policy_apples_to_apples_external_rows")
        == 0,
        "source-policy closed rows changed",
    )
    checks.check(
        audit.get("source_policy_rows_total")
        == result_checks.get("source_policy_apples_to_apples_external_total_rows")
        == 40,
        "source-policy total rows changed",
    )

    minimal_block = audit.get("minimal_replay_package", {})
    checks.check(minimal_block.get("read_only_replay_package") is True, "minimal replay boundary lost")
    checks.check(
        minimal_block.get("status") == minimal.get("status") == "candidate_replay_package_built_not_submission_ready",
        "minimal replay status stale",
    )
    checks.check(minimal_block.get("candidate_file_count") == minimal.get("candidate_file_count") == 10, "minimal file count stale")
    checks.check(
        minimal_block.get("candidate_python_line_count")
        == minimal.get("candidate_python_line_count")
        == 180,
        "minimal replay Python line count stale",
    )
    checks.check(minimal_block.get("runner_centered") is False, "minimal replay package should not be runner-centered")

    companion_block = audit.get("local_accepted_runner_companion", {})
    checks.check(companion_block.get("launcher_passed") == companion.get("launcher_passed") is True, "companion launcher not passed")
    checks.check(companion_block.get("local_rows") == companion.get("local_rows") == 12, "companion local rows stale")
    checks.check(
        companion_block.get("full_source_policy_runner_package_ready")
        == companion.get("full_source_policy_runner_package_ready")
        is False,
        "companion overclaims full source-policy package",
    )

    local = audit.get("human_runnable_local_evidence", {})
    expected_examples = ["single_pendulum", "double_pendulum", "four_link", "slider_crank"]
    checks.check(local.get("runner_passed") == b6.get("b6_local_evidence_runner_passed") is True, "B6 runner pass stale")
    checks.check(local.get("local_rows") == b6.get("local_rows") == 12, "B6 local rows stale")
    checks.check(local.get("self_contained_examples") == expected_examples, "self-contained examples changed")
    checks.check(local.get("replay_only_examples") == [], "replay-only examples changed")
    checks.check(local.get("four_example_self_contained_simulation_ready") is True, "four-example local simulation not ready")

    p1_block = audit.get("p1_runner_candidates", {})
    checks.check(p1_block.get("single_ready") == p1.get("p1_single_runner_candidate_ready") is True, "single P1 readiness stale")
    checks.check(p1_block.get("double_ready") == p1.get("p1_double_runner_candidate_ready") is True, "double P1 readiness stale")
    checks.check(p1_block.get("regenerated_rows") == p1_block.get("required_rows") == 6, "P1 row count stale")
    checks.check(p1_block.get("missing_rows") == 0, "P1 missing rows changed")

    closed_block = audit.get("closed_loop_runner_candidate", {})
    checks.check(closed_block.get("runner_passed") == closed_loop.get("runner_passed") is True, "closed-loop runner pass stale")
    checks.check(closed_block.get("self_contained_simulation_runner") is True, "closed-loop self-contained marker stale")
    checks.check(closed_block.get("closed_loop_local_rows") == 6, "closed-loop row count stale")
    checks.check(set(closed_block.get("closed_loop_models", [])) == {"four_link", "slider_crank"}, "closed-loop models changed")

    bundle_block = audit.get("narrowed_repro_bundle", {})
    checks.check(
        bundle_block.get("manifest_status") == bundle_manifest.get("status"),
        "bundle manifest status stale",
    )
    checks.check(bundle_block.get("summary_status") == bundle_summary.get("status") == "pass", "bundle summary status stale")
    checks.check(bundle_block.get("source_policy_rows_closed") == 0, "bundle source-policy rows overclosed")
    checks.check(bundle_block.get("source_policy_rows_total") == 40, "bundle source-policy total changed")
    checks.check(
        bundle_block.get("full_source_policy_runner_package_ready") is False,
        "bundle overclaims full source-policy package",
    )
    checks.check(bundle_block.get("submission_ready") is False, "bundle overclaims submission readiness")
    checks.check(bundle_block.get("run_v047_invoked") is False, "bundle overclaims run_v047 invocation")
    checks.check(bundle_block.get("run_v048_invoked") is False, "bundle overclaims run_v048 invocation")

    boundary = audit.get("package_boundary", {})
    checks.check(boundary.get("not_a_source_policy_runner_archive") is True, "source-policy boundary missing")
    checks.check(boundary.get("full_source_policy_deferred_until_rows_close") is True, "full-source deferral missing")
    checks.check(boundary.get("source_policy_rows_closed_now") == 0, "source-policy rows overclosed")
    checks.check(runner_centered.get("full_source_policy_runner_package_ready") is False, "runner-centered source-policy ready changed")
    checks.check(extraction.get("full_source_policy_self_contained_runner_ready") is False, "extraction plan overclaims source-policy runner")

    for token in [
        "Status: **narrowed_claim_reproducibility_package_ready_full_source_policy_open**.",
        "Narrowed-claim reproducibility package ready: `True`.",
        "Global submission ready: `False`.",
        "Submission standard scope: `global_submission_standard`.",
        "Full source-policy runner package ready: `False`.",
        "Source-policy rows closed: `0/40`.",
        "Source-policy execution allowed now/invoked/exact opt-in required: `False/False/True`.",
        "Safe action ids: `['rebuild_read_only_audit_chain', 'rerun_read_only_validators', 'keep_narrowed_archive_provenance_only', 'monitor_reopen_conditions']`; opt-in action ids: `['authorized_b4_ra_hi_source_policy_execution']`.",
        "Source-policy execution handoff exact approval/driver: `I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json./run_b4_source_policy_after_opt_in.sh/True/True/13/20`.",
        "Source-policy execution handoff authorized/commands-not-run/terminal-unable: `False/True/20`.",
        f"Minimal replay package/status/files/Python lines: `{minimal.get('status')}/{minimal.get('candidate_file_count')}/{minimal.get('candidate_python_line_count')}`.",
        "P1 single/double runner ready: `True/True`.",
        "Narrowed bundle/status/report: `pass/results/narrowed_repro_bundle_report.md`.",
        "This is a reviewer-facing package for the narrowed current claim.",
    ]:
        checks.check(token in md, f"markdown missing token: {token}")
    stale_minimal_line_count_token = (
        "Minimal replay package/status/files/Python lines: "
        "`candidate_replay_package_built_not_submission_ready/10/" + "158`."
    )
    checks.check(
        stale_minimal_line_count_token not in md,
        "markdown retained stale minimal replay Python line count",
    )

    if checks.errors:
        print("CMAME narrowed reproducibility package audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("CMAME narrowed reproducibility package audit validation: PASS")
    print("narrowed_claim_reproducibility_package_ready=True")
    print("full_source_policy_runner_package_ready=False")
    print("source_policy_rows=0/40")
    print(f"source_policy_execution_allowed_now={audit.get('source_policy_execution_allowed_now')}")
    print(f"source_policy_execution_invoked={audit.get('source_policy_execution_invoked')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
