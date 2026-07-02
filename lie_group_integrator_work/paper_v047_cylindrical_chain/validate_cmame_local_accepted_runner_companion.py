#!/usr/bin/env python3
"""Validate the CMAME local accepted-row runner companion."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
COMPANION = PAPER / "cmame_local_accepted_runner_companion"
MANIFEST_JSON = PAPER / "CMAME_LOCAL_ACCEPTED_RUNNER_COMPANION_MANIFEST.json"
MANIFEST_MD = PAPER / "CMAME_LOCAL_ACCEPTED_RUNNER_COMPANION_MANIFEST.md"
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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def python_lines(path: Path) -> int:
    return len(read_text(path).splitlines()) if path.suffix == ".py" else 0


def main() -> int:
    checks = Checks()
    try:
        manifest = read_json(MANIFEST_JSON)
        package_manifest = read_json(COMPANION / "MANIFEST.json")
        manifest_md = read_text(MANIFEST_MD)
        readme = read_text(COMPANION / "README.md")
        b6 = read_json(PAPER / "B6_FOUR_EXAMPLE_LOCAL_EVIDENCE_SUMMARY.json")
        review = read_json(PAPER / "CMAME_REVIEW_AGENT_REPORT.json")
        b4_handoff = read_json(PAPER / "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json")
        minimal = read_json(PAPER / "CMAME_MINIMAL_REPRODUCIBILITY_CANDIDATE_MANIFEST.json")
        single = read_json(PAPER / "cmame_p1_single_runner_candidate/results/single_pendulum_summary.json")
        double = read_json(PAPER / "cmame_p1_double_runner_candidate/results/double_pendulum_summary.json")
        closed = read_json(PAPER / "cmame_closed_loop_local_runner_candidate/results/closed_loop_local_summary.json")
    except Exception as exc:  # noqa: BLE001
        print(f"CMAME local accepted-row runner companion validation: FAIL\n- {exc}")
        return 1

    result_checks = review.get("result_checks", {})
    checks.check(manifest == package_manifest, "top-level and package manifests differ")
    checks.check(
        manifest.get("schema") == "cmame-local-accepted-runner-companion-v1",
        "schema changed",
    )
    checks.check(
        manifest.get("status") == "local_accepted_runner_companion_ready_source_policy_package_open",
        "status changed",
    )
    checks.check(manifest.get("submission_ready") is False, "companion overclaims submission ready")
    checks.check(manifest.get("launcher_passed") is True, "launcher pass marker missing")
    checks.check(
        manifest.get("minimal_replay_boundary_preserved") == (minimal.get("read_only_replay_package") is True),
        "minimal replay boundary marker stale",
    )
    checks.check(manifest.get("copies_runner_source") is False, "companion should not copy runner source")
    checks.check(
        manifest.get("uses_existing_self_contained_runner_candidates") is True,
        "companion should reuse existing runner candidates",
    )
    checks.check(
        manifest.get("local_accepted_rows_runner_available") is True,
        "local accepted-row runner availability missing",
    )
    checks.check(
        manifest.get("full_source_policy_runner_package_ready") is False,
        "companion overclaims full source-policy package",
    )
    checks.check(
        manifest.get("source_policy_external_superiority_allowed") is False,
        "companion overclaims source-policy superiority",
    )
    b4_driver = b4_handoff.get("approval_boundary", {}).get("guarded_execution_driver", {})
    expected_handoff = {
        "status": b4_handoff.get("status"),
        "execution_authorized": b4_handoff.get("execution_authorized"),
        "commands_not_run_by_handoff": b4_handoff.get("commands_not_run_by_handoff"),
        "exact_required_user_approval_statement": b4_handoff.get("approval_boundary", {}).get(
            "exact_required_user_approval_statement"
        ),
        "guarded_execution_driver": b4_driver.get("path"),
        "driver_requires_exact_approval": b4_driver.get("requires_exact_approval_argument"),
        "driver_does_not_authorize_execution": b4_driver.get("driver_does_not_authorize_execution"),
        "opt_in_required_command_count": b4_handoff.get("opt_in_required_actions", {}).get(
            "command_count"
        ),
        "opt_in_required_mapped_external_rows": b4_handoff.get("opt_in_required_actions", {}).get(
            "mapped_external_rows"
        ),
        "terminal_unable_to_reproduce_rows": b4_handoff.get("source_policy_row_state", {}).get(
            "unable_to_reproduce"
        ),
    }
    checks.check(
        manifest.get("source_policy_execution_handoff") == expected_handoff,
        "companion source-policy handoff boundary stale",
    )
    checks.check(
        expected_handoff.get("status") == "source_policy_execution_handoff_ready_not_authorized_not_run"
        and expected_handoff.get("execution_authorized") is False
        and expected_handoff.get("commands_not_run_by_handoff") is True
        and expected_handoff.get("exact_required_user_approval_statement") == EXPECTED_APPROVAL
        and expected_handoff.get("guarded_execution_driver") == "run_b4_source_policy_after_opt_in.sh"
        and expected_handoff.get("driver_requires_exact_approval") is True
        and expected_handoff.get("driver_does_not_authorize_execution") is True
        and expected_handoff.get("opt_in_required_command_count") == 13
        and expected_handoff.get("opt_in_required_mapped_external_rows") == 20
        and expected_handoff.get("terminal_unable_to_reproduce_rows") == 20,
        "B4 handoff exact approval/driver boundary changed",
    )
    checks.check(
        manifest.get("source_policy_execution_allowed_now")
        == b4_handoff.get("source_policy_execution_allowed_now")
        is False
        and manifest.get("source_policy_execution_invoked")
        == b4_handoff.get("source_policy_execution_invoked")
        is False
        and manifest.get("exact_b4_opt_in_required_for_execution")
        == b4_handoff.get("exact_b4_opt_in_required_for_execution")
        is True
        and manifest.get("safe_action_ids")
        == b4_handoff.get("safe_action_ids")
        == EXPECTED_SAFE_ACTION_IDS
        and manifest.get("opt_in_action_ids")
        == b4_handoff.get("opt_in_action_ids")
        == EXPECTED_OPT_IN_ACTION_IDS
        and manifest.get("required_user_approval_statement") == EXPECTED_APPROVAL
        and manifest.get("guarded_execution_driver") == "run_b4_source_policy_after_opt_in.sh",
        "top-level source-policy execution aliases stale",
    )
    checks.check(
        manifest.get("source_policy_closed_rows")
        == result_checks.get("source_policy_apples_to_apples_external_rows")
        == 0,
        "source-policy closed row count changed",
    )
    checks.check(
        manifest.get("source_policy_total_rows")
        == result_checks.get("source_policy_apples_to_apples_external_total_rows")
        == 40,
        "source-policy total row count changed",
    )
    checks.check(manifest.get("local_rows") == b6.get("local_rows") == 12, "local row count changed")
    checks.check(
        set(manifest.get("self_contained_examples", []))
        == {"single_pendulum", "double_pendulum", "four_link", "slider_crank"},
        "self-contained example set changed",
    )
    checks.check(manifest.get("replay_only_examples", []) == [], "replay-only examples changed")
    checks.check(
        manifest.get("candidate_python_file_count") == 1
        and 1 <= int(manifest.get("candidate_python_line_count", 0)) <= 260,
        "companion launcher size changed",
    )
    checks.check(
        manifest.get("reviewer_facing_python_file_limit") == 12
        and manifest.get("reviewer_facing_python_line_limit") == 2000,
        "reviewer-facing limits changed",
    )

    summaries = manifest.get("runner_summaries", {})
    checks.check(summaries.get("single_pendulum_rows") == single.get("rows") == 3, "single rows stale")
    checks.check(summaries.get("double_pendulum_rows") == double.get("rows") == 3, "double rows stale")
    checks.check(summaries.get("closed_loop_rows") == closed.get("row_count") == 6, "closed-loop rows stale")
    checks.check(float(summaries.get("single_position_order", 0.0)) > 5.0, "single order too low")
    checks.check(float(summaries.get("double_position_order", 0.0)) > 5.0, "double order too low")
    checks.check(
        set(summaries.get("closed_loop_models", [])) == {"four_link", "slider_crank"},
        "closed-loop model set changed",
    )

    expected_commands = [
        "cmame_minimal_reproducibility_candidate/scripts/replay_paper_matrix.py",
        "cmame_p1_single_runner_candidate/scripts/run_single_pendulum_fullva.py",
        "cmame_p1_double_runner_candidate/scripts/run_double_pendulum_fullva.py",
        "cmame_closed_loop_local_runner_candidate/scripts/run_closed_loop_fullva_candidate.py",
    ]
    checks.check(manifest.get("runner_commands") == expected_commands, "runner command list changed")

    for item in manifest.get("files", []):
        rel = item.get("path")
        path = COMPANION / str(rel)
        checks.check(path.exists(), f"companion file missing: {rel}")
        if path.exists():
            checks.check(path.stat().st_size == item.get("bytes"), f"file size stale: {rel}")
            checks.check(sha256(path) == item.get("sha256"), f"file hash stale: {rel}")
            if path.suffix == ".py":
                checks.check(python_lines(path) == item.get("python_lines"), f"Python line count stale: {rel}")

    actual_files = {path.relative_to(COMPANION).as_posix() for path in COMPANION.rglob("*") if path.is_file()}
    expected_files = {"README.md", "MANIFEST.json", *{str(item.get("path")) for item in manifest.get("files", [])}}
    checks.check(actual_files == expected_files, f"companion file set changed: {sorted(actual_files ^ expected_files)}")

    launcher = subprocess.run(
        [sys.executable, "scripts/run_local_accepted_runner_companion.py"],
        cwd=COMPANION,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    checks.check(launcher.returncode == 0, f"launcher failed:\n{launcher.stdout}")
    for token in [
        "cmame_local_accepted_runner_companion=PASS",
        "minimal_replay_boundary=preserved",
        "self_contained_examples=single_pendulum,double_pendulum,four_link,slider_crank",
        "local_rows=12",
        "source_policy_external_rows=0/40",
        "source_policy_handoff_status=source_policy_execution_handoff_ready_not_authorized_not_run",
        "source_policy_handoff_authorized=False",
        "source_policy_handoff_driver=run_b4_source_policy_after_opt_in.sh",
        "source_policy_handoff_opt_in=13/20",
        "full_source_policy_runner_package_ready=False",
        "submission_ready=False",
    ]:
        checks.check(token in launcher.stdout, f"launcher output missing token: {token}")
        checks.check(token in readme, f"README missing token: {token}")

    for token in [
        "Status: **local_accepted_runner_companion_ready_source_policy_package_open**.",
        "Launcher passed: `True`.",
        "Minimal replay boundary preserved: `True`.",
        "Local rows: `12`.",
        "Source-policy rows closed: `0/40`.",
        "Source-policy execution allowed now/invoked/exact opt-in required: `False/False/True`.",
        "Safe action ids: `['rebuild_read_only_audit_chain', 'rerun_read_only_validators', 'keep_narrowed_archive_provenance_only', 'monitor_reopen_conditions']`; opt-in action ids: `['authorized_b4_ra_hi_source_policy_execution']`.",
        "Source-policy execution handoff exact approval/driver: `I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json./run_b4_source_policy_after_opt_in.sh/True/True/13/20`.",
        "Full source-policy runner package ready: `False`.",
        "Reading rule: this is a launcher/index for local accepted-row runner candidates, not a source-policy runner archive.",
    ]:
        checks.check(token in manifest_md, f"manifest markdown missing token: {token}")

    if checks.errors:
        print("CMAME local accepted-row runner companion validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("CMAME local accepted-row runner companion validation: PASS")
    print(f"status={manifest.get('status')}")
    print(f"local_rows={manifest.get('local_rows')}")
    print(f"candidate_python_lines={manifest.get('candidate_python_line_count')}")
    print(f"source_policy_closed={manifest.get('source_policy_closed_rows')}/{manifest.get('source_policy_total_rows')}")
    print(f"source_policy_execution_allowed_now={manifest.get('source_policy_execution_allowed_now')}")
    print(f"source_policy_execution_invoked={manifest.get('source_policy_execution_invoked')}")
    print("submission_ready=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
