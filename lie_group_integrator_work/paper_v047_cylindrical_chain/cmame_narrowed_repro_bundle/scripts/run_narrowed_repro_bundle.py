#!/usr/bin/env python3
"""Run the narrowed CMAME reproducibility bundle.

This launcher intentionally reuses the paper-level human replay entrypoint.
It runs the replay table and local accepted-row runner candidates, then writes
a compact bundle summary. It does not run source-policy campaigns.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


PAPER = Path(__file__).resolve().parents[2]
BUNDLE = Path(__file__).resolve().parents[1]
RESULTS = BUNDLE / "results"
REPORT = RESULTS / "narrowed_repro_bundle_report.md"
SUMMARY_JSON = RESULTS / "narrowed_repro_bundle_summary.json"
SUMMARY_MD = RESULTS / "narrowed_repro_bundle_summary.md"


EXPECTED_TOKENS = [
    "human_reproducibility_runner=PASS",
    "local_runners_invoked=True",
    "closed_loop_local_replay_invoked=True",
    "closed_loop_local_runner_candidate_invoked=True",
    "local_accepted_runner_companion_invoked=True",
    "local_accepted_runner_companion_rows=12/12",
    "run_v047_invoked=False",
    "run_v048_invoked=False",
    "source_policy_external_rows=0/40",
    "direct_pc2_proof_gap_closed=True",
    "stage_residual_O_h7_direct_proof=True",
    "submission_ready=False",
]


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def main() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        [
            sys.executable,
            "run_human_reproducibility.py",
            "--include-local-runners",
            "--report",
            str(REPORT),
        ],
        cwd=PAPER,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    output = proc.stdout

    errors: list[str] = []
    if proc.returncode != 0:
        errors.append(f"human reproducibility runner failed with code {proc.returncode}")
    for token in EXPECTED_TOKENS:
        if token not in output:
            errors.append(f"missing output token: {token}")
    if not REPORT.exists() or REPORT.stat().st_size == 0:
        errors.append("bundle markdown report was not written")

    manifest = read_json(BUNDLE / "MANIFEST.json")
    narrowed = read_json(PAPER / "CMAME_NARROWED_REPRODUCIBILITY_PACKAGE_AUDIT.json")
    handoff = narrowed.get("source_policy_execution_handoff", {})
    manifest_handoff = manifest.get("source_policy_execution_handoff", {})
    if manifest_handoff != handoff:
        errors.append("bundle manifest source-policy handoff boundary is stale")
    action_boundary_aliases = {
        "source_policy_execution_allowed_now": narrowed.get(
            "source_policy_execution_allowed_now"
        ),
        "source_policy_execution_invoked": narrowed.get("source_policy_execution_invoked"),
        "exact_b4_opt_in_required_for_execution": narrowed.get(
            "exact_b4_opt_in_required_for_execution"
        ),
        "safe_action_ids": narrowed.get("safe_action_ids"),
        "opt_in_action_ids": narrowed.get("opt_in_action_ids"),
        "required_user_approval_statement": narrowed.get("required_user_approval_statement"),
        "guarded_execution_driver": narrowed.get("guarded_execution_driver"),
    }
    manifest_action_boundary_aliases = {
        key: manifest.get(key) for key in action_boundary_aliases
    }
    if manifest_action_boundary_aliases != action_boundary_aliases:
        errors.append("bundle manifest top-level source-policy action boundary is stale")

    handoff_lines = [
        "",
        "## Bundle Source-Policy Handoff Boundary",
        "",
        f"- Handoff status: `{handoff.get('status')}`.",
        f"- Execution authorized: `{handoff.get('execution_authorized')}`.",
        f"- Commands run by handoff: `{not handoff.get('commands_not_run_by_handoff')}`.",
        f"- Exact B4 approval: `{handoff.get('exact_required_user_approval_statement')}`.",
        f"- Guarded B4 driver: `{handoff.get('guarded_execution_driver')}`.",
        f"- Driver requires exact approval / does not authorize execution: `{handoff.get('driver_requires_exact_approval')}/{handoff.get('driver_does_not_authorize_execution')}`.",
        f"- Opt-in commands / mapped rows: `{handoff.get('opt_in_required_command_count')}/{handoff.get('opt_in_required_mapped_external_rows')}`.",
        f"- Terminal unable-to-reproduce rows: `{handoff.get('terminal_unable_to_reproduce_rows')}`.",
    ]
    if REPORT.exists() and REPORT.stat().st_size > 0:
        report_text = REPORT.read_text(encoding="utf-8", errors="replace")
        if "## Bundle Source-Policy Handoff Boundary" not in report_text:
            REPORT.write_text(
                report_text.rstrip() + "\n" + "\n".join(handoff_lines) + "\n",
                encoding="utf-8",
            )

    summary = {
        "schema": "cmame-narrowed-repro-bundle-summary-v1",
        "status": "pass" if not errors else "fail",
        "bundle_status": manifest.get("status"),
        "narrowed_claim_reproducibility_package_ready": narrowed.get(
            "narrowed_claim_reproducibility_package_ready"
        ),
        "source_policy_rows_closed": narrowed.get("source_policy_rows_closed"),
        "source_policy_rows_total": narrowed.get("source_policy_rows_total"),
        "source_policy_execution_handoff": handoff,
        **action_boundary_aliases,
        "full_source_policy_runner_package_ready": narrowed.get(
            "full_source_policy_runner_package_ready"
        ),
        "submission_ready": narrowed.get("submission_ready"),
        "report": str(REPORT.relative_to(BUNDLE)),
        "run_v047_invoked": False,
        "run_v048_invoked": False,
        "errors": errors,
    }
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Narrowed Reproducibility Bundle Summary",
        "",
        f"Status: **{summary['status']}**.",
        "",
        f"- Bundle status: `{summary['bundle_status']}`.",
        f"- Narrowed package ready: `{summary['narrowed_claim_reproducibility_package_ready']}`.",
        f"- Source-policy rows closed: `{summary['source_policy_rows_closed']}/{summary['source_policy_rows_total']}`.",
        f"- Source-policy execution allowed now/invoked/exact opt-in required: `{summary['source_policy_execution_allowed_now']}/{summary['source_policy_execution_invoked']}/{summary['exact_b4_opt_in_required_for_execution']}`.",
        f"- Source-policy safe/opt-in action ids: `{summary['safe_action_ids']}/{summary['opt_in_action_ids']}`.",
        f"- Source-policy required approval/driver: `{summary['required_user_approval_statement']}/{summary['guarded_execution_driver']}`.",
        f"- Source-policy execution handoff exact approval/driver: `{handoff.get('exact_required_user_approval_statement')}/{handoff.get('guarded_execution_driver')}/{handoff.get('driver_requires_exact_approval')}/{handoff.get('driver_does_not_authorize_execution')}/{handoff.get('opt_in_required_command_count')}/{handoff.get('opt_in_required_mapped_external_rows')}`.",
        f"- Source-policy execution handoff authorized/commands-not-run/terminal-unable: `{handoff.get('execution_authorized')}/{handoff.get('commands_not_run_by_handoff')}/{handoff.get('terminal_unable_to_reproduce_rows')}`.",
        f"- Full source-policy runner package ready: `{summary['full_source_policy_runner_package_ready']}`.",
        f"- Submission ready: `{summary['submission_ready']}`.",
        f"- Report: `{summary['report']}`.",
    ]
    if errors:
        lines.extend(["", "## Errors", ""])
        lines.extend(f"- {error}" for error in errors)
    SUMMARY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(output.strip())
    if errors:
        print("cmame_narrowed_repro_bundle=FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("cmame_narrowed_repro_bundle=PASS")
    print("narrowed_claim_reproducibility_package_ready=True")
    print("source_policy_external_rows=0/40")
    print(f"source_policy_execution_allowed_now={summary['source_policy_execution_allowed_now']}")
    print(f"source_policy_execution_invoked={summary['source_policy_execution_invoked']}")
    print(
        "exact_b4_opt_in_required_for_execution="
        f"{summary['exact_b4_opt_in_required_for_execution']}"
    )
    print(f"source_policy_handoff_status={handoff.get('status')}")
    print(f"source_policy_handoff_authorized={handoff.get('execution_authorized')}")
    print(f"source_policy_handoff_driver={handoff.get('guarded_execution_driver')}")
    print(
        "source_policy_handoff_opt_in="
        f"{handoff.get('opt_in_required_command_count')}/"
        f"{handoff.get('opt_in_required_mapped_external_rows')}"
    )
    print("full_source_policy_runner_package_ready=False")
    print("submission_ready=False")
    print(f"summary_json={SUMMARY_JSON.relative_to(PAPER)}")
    print(f"summary_md={SUMMARY_MD.relative_to(PAPER)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
