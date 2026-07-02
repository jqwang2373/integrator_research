#!/usr/bin/env python3
"""Validate the B6 four-example local-evidence summary."""

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
        summary = read_json(PAPER / "B6_FOUR_EXAMPLE_LOCAL_EVIDENCE_SUMMARY.json")
        summary_md = read_text(PAPER / "B6_FOUR_EXAMPLE_LOCAL_EVIDENCE_SUMMARY.md")
        single = read_json(PAPER / "cmame_p1_single_runner_candidate/results/single_pendulum_summary.json")
        double = read_json(PAPER / "cmame_p1_double_runner_candidate/results/double_pendulum_summary.json")
        closed_loop = read_json(PAPER / "cmame_closed_loop_local_runner_candidate/results/closed_loop_local_summary.json")
        proof = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
        review = read_json(PAPER / "CMAME_REVIEW_AGENT_REPORT.json")
    except Exception as exc:  # noqa: BLE001
        print(f"B6 four-example local evidence validation: FAIL\n- {exc}")
        return 1

    result_checks = review.get("result_checks", {})
    checks.check(summary.get("schema") == "b6-four-example-local-evidence-summary-v1", "schema changed")
    checks.check(
        summary.get("status") == "four_example_local_evidence_runnable_source_policy_open",
        "status changed",
    )
    checks.check(summary.get("submission_ready") is False, "summary overclaims submission ready")
    checks.check(summary.get("b6_local_evidence_runner_passed") is True, "runner did not pass")
    checks.check(summary.get("local_rows") == 12, "local row count changed")
    checks.check(
        summary.get("examples") == ["single_pendulum", "double_pendulum", "four_link", "slider_crank"],
        "example list changed",
    )
    checks.check(
        set(summary.get("self_contained_examples", []))
        == {"single_pendulum", "double_pendulum", "four_link", "slider_crank"},
        "self-contained example set changed",
    )
    checks.check(
        summary.get("replay_only_examples", []) == [],
        "replay-only example set changed",
    )
    checks.check(
        summary.get("human_runnable_four_example_local_evidence_available") is True,
        "four-example local evidence should be available",
    )
    checks.check(
        summary.get("human_runnable_four_example_self_contained_simulation_ready") is True,
        "four-example self-contained simulation not ready",
    )

    single_summary = summary.get("single_pendulum", {})
    checks.check(single_summary.get("mode") == "self_contained_simulation", "single mode changed")
    checks.check(single_summary.get("rows") == single.get("rows") == 3, "single rows changed")
    checks.check(single_summary.get("ready") == single.get("p1_single_only_ready") is True, "single readiness changed")
    checks.check(float(single_summary.get("position_order", 0.0)) > 5.0, "single position order too low")
    checks.check(float(single_summary.get("velocity_order", 0.0)) > 5.0, "single velocity order too low")
    checks.check(single_summary.get("imports_v047_or_v048") is False, "single imports v047/v048")
    checks.check(single_summary.get("proof_gap_closed_by_local_runner") is False, "single overclaims proof closure")

    double_summary = summary.get("double_pendulum", {})
    checks.check(double_summary.get("mode") == "self_contained_simulation", "double mode changed")
    checks.check(double_summary.get("rows") == double.get("rows") == 3, "double rows changed")
    checks.check(double_summary.get("ready") == double.get("p1_double_only_ready") is True, "double readiness changed")
    checks.check(float(double_summary.get("position_order", 0.0)) > 5.0, "double position order too low")
    checks.check(float(double_summary.get("velocity_order", 0.0)) > 5.0, "double velocity order too low")
    checks.check(double_summary.get("imports_v047_v048_or_v029") is False, "double imports v047/v048/v029")
    checks.check(double_summary.get("proof_gap_closed_by_local_runner") is False, "double overclaims proof closure")

    closed_orders = closed_loop.get("model_summaries", {})
    for example in ["four_link", "slider_crank"]:
        item = summary.get(example, {})
        source = closed_orders.get(example, {})
        checks.check(item.get("mode") == "self_contained_simulation", f"{example} mode changed")
        checks.check(item.get("ready") is True, f"{example} readiness changed")
        checks.check(
            item.get("position_order") == source.get("pos_observed_order"),
            f"{example} position order not synchronized",
        )
        checks.check(
            item.get("velocity_order") == source.get("vel_observed_order"),
            f"{example} velocity order not synchronized",
        )
        checks.check(float(item.get("position_order", 0.0)) > 5.0, f"{example} position order too low")
        checks.check(float(item.get("velocity_order", 0.0)) > 5.0, f"{example} velocity order too low")

    checks.check(
        summary.get("closed_loop_candidate_self_contained_simulation_runner")
        == closed_loop.get("self_contained_simulation_runner")
        is True,
        "closed-loop candidate self-contained simulation marker missing",
    )
    checks.check(
        summary.get("closed_loop_candidate_status") == closed_loop.get("status"),
        "closed-loop candidate status not synchronized",
    )
    checks.check(
        summary.get("closed_loop_candidate_rows") == closed_loop.get("row_count") == 6,
        "closed-loop candidate row count not synchronized",
    )
    checks.check(
        summary.get("source_policy_external_rows_closed")
        == result_checks.get("source_policy_apples_to_apples_external_rows")
        == 0,
        "source-policy closed row count changed",
    )
    checks.check(
        summary.get("source_policy_external_rows_total")
        == result_checks.get("source_policy_apples_to_apples_external_total_rows")
        == 40,
        "source-policy total row count changed",
    )
    checks.check(summary.get("source_policy_external_superiority_allowed") is False, "external superiority overclaimed")
    checks.check(
        summary.get("global_proof_gap_closed") == proof.get("closure_state", {}).get("proof_gap_closed") is True,
        "global proof boundary changed",
    )
    checks.check(
        summary.get("direct_residual_bridge_proof_gap_closed") is True,
        "direct residual-bridge proof gap scope marker missing",
    )
    checks.check(
        summary.get("global_proof_gap_closed_scope")
        == proof.get("closure_state", {}).get("proof_gap_closed_scope")
        == "direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open",
        "global proof-gap scope missing or changed",
    )
    checks.check(
        "local-runner proof closure only" in summary.get("runner_tail_proof_gap_closed_scope", ""),
        "runner-tail proof-gap scope missing",
    )
    checks.check(summary.get("run_v047_invoked") is False, "run_v047 must not be invoked")
    checks.check(summary.get("run_v048_invoked") is False, "run_v048 must not be invoked")
    checks.check(summary.get("errors") == [], "summary contains runner errors")
    checks.check(len(summary.get("runner_invocations", [])) == 3, "runner invocation count changed")

    for token in [
        "Status: **four_example_local_evidence_runnable_source_policy_open**.",
        "Runner passed: `True`.",
        "Local rows: `12`.",
        "Self-contained examples: `single_pendulum,double_pendulum,four_link,slider_crank`.",
        "Replay-only examples: `none`.",
        "Four-example local evidence available/self-contained simulation ready: `True/True`.",
        "Source-policy external rows: `0/40`.",
        "Direct residual-bridge proof gap closed: `True`.",
        "Direct residual-bridge proof gap scope: `direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open`.",
        "Submission ready: `False`.",
    ]:
        checks.check(token in summary_md, f"markdown token missing: {token}")
    checks.check(
        "Global proof gap closed:" not in summary_md,
        "stale broad global proof-gap label remains in B6 summary",
    )

    if checks.errors:
        print("B6 four-example local evidence validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("B6 four-example local evidence validation: PASS")
    print(f"local_rows={summary.get('local_rows')}")
    print("self_contained_examples=single_pendulum,double_pendulum,four_link,slider_crank")
    print("replay_only_examples=none")
    print(f"source_policy_external_rows={summary.get('source_policy_external_rows_closed')}/{summary.get('source_policy_external_rows_total')}")
    print(f"direct_pc2_proof_gap_closed={summary.get('direct_residual_bridge_proof_gap_closed')}")
    print(f"schema_compat_global_proof_key_retained={summary.get('global_proof_gap_closed')}")
    print(f"submission_ready={summary.get('submission_ready')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
