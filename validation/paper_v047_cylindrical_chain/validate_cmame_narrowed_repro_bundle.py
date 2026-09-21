#!/usr/bin/env python3
"""Validate the narrowed CMAME reproducibility bundle."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


PAPER = Path(__file__).resolve().parent
BUNDLE = PAPER / "cmame_narrowed_repro_bundle"
MANIFEST = BUNDLE / "MANIFEST.json"
SCRIPT = BUNDLE / "scripts" / "run_narrowed_repro_bundle.py"
SUMMARY_JSON = BUNDLE / "results" / "narrowed_repro_bundle_summary.json"
SUMMARY_MD = BUNDLE / "results" / "narrowed_repro_bundle_summary.md"
REPORT = BUNDLE / "results" / "narrowed_repro_bundle_report.md"
EXPECTED_SAFE_ACTION_IDS = [
    "rebuild_read_only_audit_chain",
    "rerun_read_only_validators",
    "keep_narrowed_archive_provenance_only",
    "monitor_reopen_conditions",
]
EXPECTED_OPT_IN_ACTION_IDS = ["authorized_b4_ra_hi_source_policy_execution"]
EXPECTED_APPROVAL_STATEMENT = (
    "I explicitly approve running the B4 source-policy execution commands listed in "
    "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json."
)
EXPECTED_GUARDED_DRIVER = "run_b4_source_policy_after_opt_in.sh"
EXPECTED_ACTION_BOUNDARY_ALIASES = {
    "source_policy_execution_allowed_now": False,
    "source_policy_execution_invoked": False,
    "exact_b4_opt_in_required_for_execution": True,
    "safe_action_ids": EXPECTED_SAFE_ACTION_IDS,
    "opt_in_action_ids": EXPECTED_OPT_IN_ACTION_IDS,
    "required_user_approval_statement": EXPECTED_APPROVAL_STATEMENT,
    "guarded_execution_driver": EXPECTED_GUARDED_DRIVER,
}


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


def main() -> int:
    checks = Checks()
    for path in [MANIFEST, SCRIPT, BUNDLE / "README.md"]:
        checks.check(path.exists() and path.stat().st_size > 0, f"missing bundle file: {path}")

    if not checks.errors:
        proc = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=PAPER,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if proc.returncode != 0:
            checks.errors.append(f"bundle launcher failed with code {proc.returncode}")
            checks.errors.append(proc.stdout)
        for token in [
            "cmame_narrowed_repro_bundle=PASS",
            "narrowed_claim_reproducibility_package_ready=True",
            "source_policy_external_rows=0/40",
            "source_policy_handoff_status=source_policy_execution_handoff_ready_not_authorized_not_run",
            "source_policy_handoff_authorized=False",
            "source_policy_handoff_driver=run_b4_source_policy_after_opt_in.sh",
            "source_policy_handoff_opt_in=13/20",
            "source_policy_execution_allowed_now=False",
            "source_policy_execution_invoked=False",
            "exact_b4_opt_in_required_for_execution=True",
            "direct_pc2_proof_gap_closed=True",
            "local_runner_proof_gap_closed=False",
            "full_source_policy_runner_package_ready=False",
            "submission_ready=False",
        ]:
            checks.check(token in proc.stdout, f"bundle launcher missing token: {token}")
        checks.check(
            "\nproof_gap_closed=True\n" not in f"\n{proc.stdout}\n",
            "bundle launcher reintroduced naked global proof_gap_closed marker",
        )
        checks.check(
            "\nproof_gap_closed=False\n" not in f"\n{proc.stdout}\n",
            "bundle launcher reintroduced naked local proof_gap_closed marker",
        )

    if not checks.errors:
        manifest = read_json(MANIFEST)
        summary = read_json(SUMMARY_JSON)
        narrowed = read_json(PAPER / "CMAME_NARROWED_REPRODUCIBILITY_PACKAGE_AUDIT.json")
        expected_handoff = narrowed.get("source_policy_execution_handoff", {})
        checks.check(
            manifest.get("schema") == "cmame-narrowed-repro-bundle-manifest-v1",
            "manifest schema changed",
        )
        checks.check(
            manifest.get("status")
            == "narrowed_repro_bundle_ready_replay_plus_local_runners_source_policy_open",
            "manifest status changed",
        )
        boundary = manifest.get("source_policy_boundary", {})
        checks.check(boundary.get("source_policy_rows_closed") == 0, "source-policy rows overclosed")
        checks.check(boundary.get("source_policy_rows_total") == 40, "source-policy total changed")
        checks.check(boundary.get("full_source_policy_runner_package_ready") is False, "full source-policy package overclaimed")
        checks.check(
            manifest.get("source_policy_execution_handoff") == expected_handoff,
            "manifest source-policy handoff boundary stale",
        )
        manifest_action_boundary_aliases = {
            key: manifest.get(key) for key in EXPECTED_ACTION_BOUNDARY_ALIASES
        }
        narrowed_action_boundary_aliases = {
            key: narrowed.get(key) for key in EXPECTED_ACTION_BOUNDARY_ALIASES
        }
        checks.check(
            manifest_action_boundary_aliases
            == narrowed_action_boundary_aliases
            == EXPECTED_ACTION_BOUNDARY_ALIASES,
            "manifest top-level source-policy action boundary stale",
        )
        handoff = summary.get("source_policy_execution_handoff", {})
        checks.check(handoff == expected_handoff, "summary source-policy handoff boundary stale")
        summary_action_boundary_aliases = {
            key: summary.get(key) for key in EXPECTED_ACTION_BOUNDARY_ALIASES
        }
        checks.check(
            summary_action_boundary_aliases == EXPECTED_ACTION_BOUNDARY_ALIASES,
            "summary top-level source-policy action boundary stale",
        )
        checks.check(
            handoff.get("status") == "source_policy_execution_handoff_ready_not_authorized_not_run"
            and handoff.get("execution_authorized") is False
            and handoff.get("commands_not_run_by_handoff") is True
            and handoff.get("exact_required_user_approval_statement")
            == EXPECTED_APPROVAL_STATEMENT
            and handoff.get("guarded_execution_driver") == EXPECTED_GUARDED_DRIVER
            and handoff.get("driver_requires_exact_approval") is True
            and handoff.get("driver_does_not_authorize_execution") is True
            and handoff.get("opt_in_required_command_count") == 13
            and handoff.get("opt_in_required_mapped_external_rows") == 20
            and handoff.get("terminal_unable_to_reproduce_rows") == 20,
            "source-policy handoff exact approval/driver boundary changed",
        )
        checks.check(summary.get("status") == "pass", "summary status not pass")
        checks.check(summary.get("source_policy_rows_closed") == 0, "summary source-policy rows overclosed")
        checks.check(summary.get("source_policy_rows_total") == 40, "summary source-policy total changed")
        checks.check(summary.get("submission_ready") is False, "summary overclaims submission ready")
        checks.check(summary.get("run_v047_invoked") is False, "summary overclaims run_v047 invocation")
        checks.check(summary.get("run_v048_invoked") is False, "summary overclaims run_v048 invocation")
        for path in [SUMMARY_MD, REPORT]:
            checks.check(path.exists() and path.stat().st_size > 0, f"missing output: {path}")
        if SUMMARY_MD.exists():
            summary_md = SUMMARY_MD.read_text(encoding="utf-8", errors="replace")
            for token in [
                "Source-policy execution allowed now/invoked/exact opt-in required: `False/False/True`.",
                "Source-policy safe/opt-in action ids: `['rebuild_read_only_audit_chain', 'rerun_read_only_validators', 'keep_narrowed_archive_provenance_only', 'monitor_reopen_conditions']/['authorized_b4_ra_hi_source_policy_execution']`.",
                "Source-policy required approval/driver: `I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json./run_b4_source_policy_after_opt_in.sh`.",
                "Source-policy execution handoff exact approval/driver: `I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json./run_b4_source_policy_after_opt_in.sh/True/True/13/20`.",
                "Source-policy execution handoff authorized/commands-not-run/terminal-unable: `False/True/20`.",
            ]:
                checks.check(token in summary_md, f"summary markdown missing token: {token}")
        if REPORT.exists():
            report = REPORT.read_text(encoding="utf-8", errors="replace")
            checks.check(
                "local_runner_proof_gap_closed=False" in report,
                "bundle report missing scoped local-runner proof boundary",
            )
            checks.check(
                "direct_pc2_proof_gap_closed=True" in report,
                "bundle report missing scoped direct-PC2 proof boundary",
            )
            for token in [
                "## Bundle Source-Policy Handoff Boundary",
                "Exact B4 approval: `I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json.`.",
                "Guarded B4 driver: `run_b4_source_policy_after_opt_in.sh`.",
                "Driver requires exact approval / does not authorize execution: `True/True`.",
                "Opt-in commands / mapped rows: `13/20`.",
            ]:
                checks.check(token in report, f"bundle report missing handoff token: {token}")
            checks.check(
                "\nproof_gap_closed=True\n" not in f"\n{report}\n",
                "bundle report reintroduced naked global proof_gap_closed marker",
            )
            checks.check(
                "\nproof_gap_closed=False\n" not in f"\n{report}\n",
                "bundle report reintroduced naked local proof_gap_closed marker",
            )

    if checks.errors:
        print("cmame narrowed repro bundle validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("cmame narrowed repro bundle validation: PASS")
    print("source_policy_external_rows=0/40")
    print("full_source_policy_runner_package_ready=False")
    print("submission_ready=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
