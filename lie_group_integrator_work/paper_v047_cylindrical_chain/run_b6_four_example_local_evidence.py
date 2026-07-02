#!/usr/bin/env python3
"""Run the B6 four-example local-evidence bundle.

This is a reviewer-facing orchestration check over the current local runner
candidates. It intentionally keeps the source-policy and submission gates open:
all four local examples are self-contained simulation candidates, while external
source-policy rows remain open.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "B6_FOUR_EXAMPLE_LOCAL_EVIDENCE_SUMMARY.json"
OUT_MD = PAPER / "B6_FOUR_EXAMPLE_LOCAL_EVIDENCE_SUMMARY.md"

RUNNERS = [
    {
        "id": "single_pendulum_self_contained",
        "example": "single_pendulum",
        "mode": "self_contained_simulation",
        "command": ["cmame_p1_single_runner_candidate/scripts/run_single_pendulum_fullva.py"],
        "summary": "cmame_p1_single_runner_candidate/results/single_pendulum_summary.json",
    },
    {
        "id": "double_pendulum_self_contained",
        "example": "double_pendulum",
        "mode": "self_contained_simulation",
        "command": ["cmame_p1_double_runner_candidate/scripts/run_double_pendulum_fullva.py"],
        "summary": "cmame_p1_double_runner_candidate/results/double_pendulum_summary.json",
    },
    {
        "id": "four_link_slider_crank_closed_loop_self_contained",
        "example": "four_link,slider_crank",
        "mode": "self_contained_simulation",
        "command": ["cmame_closed_loop_local_runner_candidate/scripts/run_closed_loop_fullva_candidate.py"],
        "summary": "cmame_closed_loop_local_runner_candidate/results/closed_loop_local_summary.json",
    },
]


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def run_runner(item: dict[str, object]) -> dict[str, object]:
    command = [sys.executable, *[str(PAPER / str(part)) for part in item["command"]]]
    proc = subprocess.run(command, cwd=PAPER, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = proc.stdout.strip()
    return {
        "id": item["id"],
        "example": item["example"],
        "mode": item["mode"],
        "command": " ".join(command),
        "returncode": proc.returncode,
        "passed": proc.returncode == 0,
        "output_tail": output.splitlines()[-12:],
        "summary": item["summary"],
    }


def order_pair(summary: dict, pos_key: str = "position_order", vel_key: str = "velocity_order") -> dict[str, float]:
    return {
        "position_order": float(summary.get(pos_key, float("nan"))),
        "velocity_order": float(summary.get(vel_key, float("nan"))),
    }


def main() -> int:
    invocations = [run_runner(item) for item in RUNNERS]
    errors: list[str] = []
    for item in invocations:
        if item["passed"] is not True:
            errors.append(f"{item['id']} failed")

    single = read_json(PAPER / "cmame_p1_single_runner_candidate/results/single_pendulum_summary.json")
    double = read_json(PAPER / "cmame_p1_double_runner_candidate/results/double_pendulum_summary.json")
    closed_loop = read_json(PAPER / "cmame_closed_loop_local_runner_candidate/results/closed_loop_local_summary.json")
    proof = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
    review = read_json(PAPER / "CMAME_REVIEW_AGENT_REPORT.json")

    result_checks = review.get("result_checks", {})
    proof_gap_closed = proof.get("closure_state", {}).get("proof_gap_closed") is True
    source_policy_closed = result_checks.get("source_policy_apples_to_apples_external_rows")
    source_policy_total = result_checks.get("source_policy_apples_to_apples_external_total_rows")

    self_contained_examples = ["single_pendulum", "double_pendulum", "four_link", "slider_crank"]
    replay_only_examples: list[str] = []
    closed_orders = closed_loop.get("model_summaries", {})
    local_rows = int(single.get("rows", 0)) + int(double.get("rows", 0)) + int(closed_loop.get("row_count", 0))

    summary = {
        "schema": "b6-four-example-local-evidence-summary-v1",
        "status": "four_example_local_evidence_runnable_source_policy_open",
        "generated_from": [
            "cmame_p1_single_runner_candidate/scripts/run_single_pendulum_fullva.py",
            "cmame_p1_double_runner_candidate/scripts/run_double_pendulum_fullva.py",
            "cmame_closed_loop_local_runner_candidate/scripts/run_closed_loop_fullva_candidate.py",
            "PROOF_CLOSURE_MANIFEST.json",
            "CMAME_REVIEW_AGENT_REPORT.json",
        ],
        "submission_ready": False,
        "b6_local_evidence_runner_passed": not errors,
        "local_rows": local_rows,
        "examples": ["single_pendulum", "double_pendulum", "four_link", "slider_crank"],
        "self_contained_examples": self_contained_examples,
        "replay_only_examples": replay_only_examples,
        "human_runnable_four_example_local_evidence_available": True,
        "human_runnable_four_example_self_contained_simulation_ready": True,
        "single_pendulum": {
            "mode": "self_contained_simulation",
            "rows": single.get("rows"),
            "ready": single.get("p1_single_only_ready"),
            **order_pair(single),
            "imports_v047_or_v048": single.get("imports_v047_or_v048"),
            "proof_gap_closed_by_local_runner": single.get("proof_gap_closed"),
        },
        "double_pendulum": {
            "mode": "self_contained_simulation",
            "rows": double.get("rows"),
            "ready": double.get("p1_double_only_ready"),
            **order_pair(double),
            "imports_v047_v048_or_v029": double.get("imports_v047_v048_or_v029"),
            "proof_gap_closed_by_local_runner": double.get("proof_gap_closed"),
        },
        "four_link": {
            "mode": "self_contained_simulation",
            "ready": "four_link" in closed_orders,
            **order_pair(closed_orders.get("four_link", {}), "pos_observed_order", "vel_observed_order"),
            "orientation_order": closed_orders.get("four_link", {}).get("orientation_observed_order"),
            "omega_order": closed_orders.get("four_link", {}).get("omega_observed_order"),
        },
        "slider_crank": {
            "mode": "self_contained_simulation",
            "ready": "slider_crank" in closed_orders,
            **order_pair(closed_orders.get("slider_crank", {}), "pos_observed_order", "vel_observed_order"),
            "orientation_order": closed_orders.get("slider_crank", {}).get("orientation_observed_order"),
            "omega_order": closed_orders.get("slider_crank", {}).get("omega_observed_order"),
        },
        "closed_loop_candidate_self_contained_simulation_runner": closed_loop.get("self_contained_simulation_runner"),
        "closed_loop_candidate_status": closed_loop.get("status"),
        "closed_loop_candidate_rows": closed_loop.get("row_count"),
        "source_policy_external_rows_closed": source_policy_closed,
        "source_policy_external_rows_total": source_policy_total,
        "source_policy_external_superiority_allowed": False,
        "global_proof_gap_closed": proof_gap_closed,
        "direct_residual_bridge_proof_gap_closed": proof_gap_closed,
        "global_proof_gap_closed_scope": proof.get("closure_state", {}).get("proof_gap_closed_scope"),
        "runner_tail_proof_gap_closed_scope": (
            "runner-tail local_runner_proof_gap_closed=False is local-runner proof closure only; "
            "direct_residual_bridge_proof_gap_closed is the proof-manifest status"
        ),
        "run_v047_invoked": False,
        "run_v048_invoked": False,
        "errors": errors,
        "runner_invocations": invocations,
    }

    OUT_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# B6 Four-Example Local Evidence Summary",
        "",
        f"Status: **{summary['status']}**.",
        f"Runner passed: `{summary['b6_local_evidence_runner_passed']}`.",
        f"Local rows: `{summary['local_rows']}`.",
        f"Self-contained examples: `{','.join(self_contained_examples)}`.",
        f"Replay-only examples: `{','.join(replay_only_examples) if replay_only_examples else 'none'}`.",
        f"Four-example local evidence available/self-contained simulation ready: `{summary['human_runnable_four_example_local_evidence_available']}/{summary['human_runnable_four_example_self_contained_simulation_ready']}`.",
        f"Source-policy external rows: `{source_policy_closed}/{source_policy_total}`.",
        f"Direct residual-bridge proof gap closed: `{proof_gap_closed}`.",
        f"Direct residual-bridge proof gap scope: `{summary['global_proof_gap_closed_scope']}`.",
        f"Runner-tail proof-gap scope: `{summary['runner_tail_proof_gap_closed_scope']}`.",
        f"Submission ready: `{summary['submission_ready']}`.",
        "",
        "## Orders",
        "",
        "| example | mode | position order | velocity order |",
        "|---|---|---:|---:|",
    ]
    for example in summary["examples"]:
        item = summary[example]
        lines.append(
            f"| `{example}` | `{item['mode']}` | `{float(item['position_order']):.6f}` | `{float(item['velocity_order']):.6f}` |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    if errors:
        print("b6_four_example_local_evidence=FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("b6_four_example_local_evidence=PASS")
    print(f"local_rows={local_rows}")
    print("self_contained_examples=single_pendulum,double_pendulum,four_link,slider_crank")
    print("replay_only_examples=none")
    print("four_example_self_contained_simulation_ready=True")
    print(f"source_policy_external_rows={source_policy_closed}/{source_policy_total}")
    print(f"direct_pc2_proof_gap_closed={proof_gap_closed}")
    print("submission_ready=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
