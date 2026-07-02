#!/usr/bin/env python3
"""Run the local accepted-row companion checks for the CMAME package."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT.parent

RUNS = [
    {
        "id": "minimal_replay_boundary",
        "example": "paper_matrix",
        "cwd": "cmame_minimal_reproducibility_candidate",
        "script": "cmame_minimal_reproducibility_candidate/scripts/replay_paper_matrix.py",
        "pass_token": "cmame_minimal_candidate_replay=PASS",
    },
    {
        "id": "single_pendulum_self_contained",
        "example": "single_pendulum",
        "cwd": "cmame_p1_single_runner_candidate",
        "script": "cmame_p1_single_runner_candidate/scripts/run_single_pendulum_fullva.py",
        "pass_token": "p1_single_runner_candidate=PASS",
    },
    {
        "id": "double_pendulum_self_contained",
        "example": "double_pendulum",
        "cwd": "cmame_p1_double_runner_candidate",
        "script": "cmame_p1_double_runner_candidate/scripts/run_double_pendulum_fullva.py",
        "pass_token": "p1_double_runner_candidate=PASS",
    },
    {
        "id": "four_link_slider_crank_self_contained",
        "example": "four_link,slider_crank",
        "cwd": "cmame_closed_loop_local_runner_candidate",
        "script": "cmame_closed_loop_local_runner_candidate/scripts/run_closed_loop_fullva_candidate.py",
        "pass_token": "cmame_closed_loop_local_runner_candidate=PASS",
    },
]


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def run_item(item: dict[str, str]) -> dict[str, object]:
    script = PAPER / item["script"]
    cwd = PAPER / item["cwd"]
    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    output = proc.stdout.strip()
    passed = proc.returncode == 0 and item["pass_token"] in output
    return {
        "id": item["id"],
        "example": item["example"],
        "script": item["script"],
        "returncode": proc.returncode,
        "passed": passed,
        "output_tail": output.splitlines()[-10:],
    }


def main() -> int:
    runs = [run_item(item) for item in RUNS]
    errors = [f"{item['id']} failed" for item in runs if item["passed"] is not True]

    minimal = read_json(PAPER / "CMAME_MINIMAL_REPRODUCIBILITY_CANDIDATE_MANIFEST.json")
    single = read_json(PAPER / "cmame_p1_single_runner_candidate/results/single_pendulum_summary.json")
    double = read_json(PAPER / "cmame_p1_double_runner_candidate/results/double_pendulum_summary.json")
    closed = read_json(PAPER / "cmame_closed_loop_local_runner_candidate/results/closed_loop_local_summary.json")
    b6 = read_json(PAPER / "B6_FOUR_EXAMPLE_LOCAL_EVIDENCE_SUMMARY.json")
    review = read_json(PAPER / "CMAME_REVIEW_AGENT_REPORT.json")
    b4_handoff = read_json(PAPER / "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json")

    result_checks = review.get("result_checks", {})
    b4_driver = b4_handoff.get("approval_boundary", {}).get("guarded_execution_driver", {})
    handoff = {
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
    source_closed = result_checks.get("source_policy_apples_to_apples_external_rows")
    source_total = result_checks.get("source_policy_apples_to_apples_external_total_rows")
    examples = ["single_pendulum", "double_pendulum", "four_link", "slider_crank"]
    local_rows = int(single.get("rows", 0)) + int(double.get("rows", 0)) + int(closed.get("row_count", 0))

    if minimal.get("read_only_replay_package") is not True:
        errors.append("minimal replay-only boundary changed")
    if local_rows != 12:
        errors.append(f"local row count changed: {local_rows}")
    if b6.get("human_runnable_four_example_self_contained_simulation_ready") is not True:
        errors.append("B6 four-example self-contained marker missing")
    if source_closed != 0 or source_total != 40:
        errors.append(f"source-policy row boundary changed: {source_closed}/{source_total}")

    if errors:
        print("cmame_local_accepted_runner_companion=FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("cmame_local_accepted_runner_companion=PASS")
    print("minimal_replay_boundary=preserved")
    print("self_contained_examples=single_pendulum,double_pendulum,four_link,slider_crank")
    print(f"local_rows={local_rows}")
    print(f"source_policy_external_rows={source_closed}/{source_total}")
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
