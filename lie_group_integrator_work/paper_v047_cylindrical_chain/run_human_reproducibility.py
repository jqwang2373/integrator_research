#!/usr/bin/env python3
"""Human-facing replay entrypoint for the CMAME paper evidence.

By default this script is intentionally a replay driver, not a numerical
campaign. It checks the embedded four-example result matrix and writes a
readable markdown table that a reviewer can inspect without navigating the
full audit tree. The optional ``--include-local-runners`` flag also runs the
self-contained single- and double-pendulum local Gauss6/FullVA candidates and
both the replay and compact self-contained candidate for the
four-link/slider-crank closed-loop local rows, then checks the local
accepted-row runner companion.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DEFAULT_REPORT = ROOT / "human_reproducibility_result_table.md"
LOCAL_RUNNERS = [
    (
        "single_pendulum",
        ROOT / "cmame_p1_single_runner_candidate",
        "scripts/run_single_pendulum_fullva.py",
        [
            "p1_single_runner_candidate=PASS",
            "rows=3",
            "p1_single_only_ready=True",
            "p1_complete=False",
            "source_policy_external_superiority_allowed=False",
            "local_runner_proof_gap_closed=False",
        ],
    ),
    (
        "double_pendulum",
        ROOT / "cmame_p1_double_runner_candidate",
        "scripts/run_double_pendulum_fullva.py",
        [
            "p1_double_runner_candidate=PASS",
            "rows=3",
            "p1_double_only_ready=True",
            "p1_complete=False",
            "source_policy_external_superiority_allowed=False",
            "local_runner_proof_gap_closed=False",
        ],
    ),
    (
        "four_link_slider_crank_closed_loop_replay",
        ROOT / "cmame_runner_adapter_candidate",
        "scripts/replay_closed_loop_local_rows.py",
        [
            "cmame_closed_loop_local_rows_replay=PASS",
            "models=four_link,slider_crank",
            "local_rows=6/6",
            "summary_json=results/closed_loop_local_rows_summary.json",
            "rows_csv=results/closed_loop_local_rows.csv",
            "self_contained_simulation_runner=False",
            "source_policy_external_superiority_allowed=False",
            "proof_gap_closed_by_adapter=False",
        ],
    ),
    (
        "four_link_slider_crank_closed_loop_self_contained_candidate",
        ROOT / "cmame_closed_loop_local_runner_candidate",
        "scripts/run_closed_loop_fullva_candidate.py",
        [
            "cmame_closed_loop_local_runner_candidate=PASS",
            "rows_ok=6/6",
            "self_contained_simulation_runner=True",
            "source_policy_external_superiority_allowed=False",
        ],
    ),
    (
        "local_accepted_runner_companion",
        ROOT / "cmame_local_accepted_runner_companion",
        "scripts/run_local_accepted_runner_companion.py",
        [
            "cmame_local_accepted_runner_companion=PASS",
            "minimal_replay_boundary=preserved",
            "self_contained_examples=single_pendulum,double_pendulum,four_link,slider_crank",
            "local_rows=12",
            "source_policy_external_rows=0/40",
            "full_source_policy_runner_package_ready=False",
            "submission_ready=False",
        ],
    ),
]


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def run_core(report: Path) -> str:
    proc = subprocess.run(
        [
            sys.executable,
            "replay_reproducibility_core.py",
            "--table",
            "--markdown-report",
            str(report),
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stdout)
    return proc.stdout


def run_local_runners() -> tuple[list[tuple[str, str]], list[str]]:
    outputs: list[tuple[str, str]] = []
    errors: list[str] = []
    for name, cwd, script, expected_tokens in LOCAL_RUNNERS:
        proc = subprocess.run(
            [sys.executable, script],
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        outputs.append((name, proc.stdout))
        if proc.returncode != 0:
            errors.append(f"{name} local runner failed with code {proc.returncode}")
        for token in expected_tokens:
            if token not in proc.stdout:
                errors.append(f"{name} local runner missing token: {token}")
    return outputs, errors


def append_local_runner_report(report: Path, outputs: list[tuple[str, str]]) -> None:
    lines = [
        "",
        "## Local Runner Checks",
        "",
            "These opt-in checks regenerate the self-contained local Gauss6/FullVA",
            "single- and double-pendulum rows, replay-check the embedded",
            "closed-loop local four-link/slider-crank rows, and run the compact",
            "self-contained closed-loop local candidate. The companion launcher",
            "then checks the existing local accepted-row packages as one group.",
            "They do not run source-paper same-policy benchmarks and do not close",
            "source-policy or symbolic-certificate gaps.",
            "The global proof boundary is carried separately by the direct residual-bridge",
            "manifest: `direct_pc2_proof_gap_closed=True` and",
            "`proof_gap_scope=direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open`.",
        "",
    ]
    for name, output in outputs:
        lines.extend(
            [
                f"### {name}",
                "",
                "```text",
                output.strip(),
                "```",
                "",
            ]
        )
    with report.open("a", encoding="utf-8") as handle:
        handle.write("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--report",
        type=Path,
        default=DEFAULT_REPORT,
        help="Markdown table to write. Defaults to human_reproducibility_result_table.md.",
    )
    parser.add_argument(
        "--include-local-runners",
        action="store_true",
        help=(
            "Also run the self-contained single/double-pendulum local "
            "Gauss6/FullVA runner candidates plus the four-link/slider-crank "
            "closed-loop local row replay, compact self-contained candidate, "
            "and local accepted-row runner companion, then append their outputs "
            "to the report."
        ),
    )
    args = parser.parse_args()

    report = args.report
    if not report.is_absolute():
        report = ROOT / report

    matrix = read_json(ROOT / "PAPER_NUMERICAL_RESULT_MATRIX.json")
    proof = read_json(ROOT / "PROOF_CLOSURE_MANIFEST.json")
    review = read_json(ROOT / "CMAME_REVIEW_AGENT_REPORT.json")

    errors: list[str] = []
    output = run_core(report)
    if "reproducibility_core=PASS" not in output:
        errors.append("core replay PASS marker missing")
    if not report.exists() or report.stat().st_size == 0:
        errors.append("markdown result table was not written")
    if matrix.get("row_count") != 44 or matrix.get("method_count") != 11:
        errors.append("matrix row or method count changed")
    if len(matrix.get("examples", [])) != 4:
        errors.append("matrix example count changed")
    if matrix.get("direct_nonlocal_velocity_order_wins") != 40:
        errors.append("common-reference order win count changed")
    if matrix.get("direct_nonlocal_velocity_error_wins") != 40:
        errors.append("common-reference error win count changed")
    if matrix.get("source_policy_external_superiority_allowed") is not False:
        errors.append("source-policy external superiority was overclaimed")
    if proof.get("closure_state", {}).get("proof_gap_closed") is not True:
        errors.append("proof gap direct closure missing")
    if proof.get("closure_state", {}).get("stage_residual_O_h7_implementation_defect_proved") is not True:
        errors.append("stage-residual direct proof missing")
    if review.get("result_checks", {}).get("source_policy_apples_to_apples_external_rows") != 0:
        errors.append("source-policy rows unexpectedly closed")
    if review.get("result_checks", {}).get("source_policy_apples_to_apples_external_total_rows") != 40:
        errors.append("source-policy row total changed")
    if (
        review.get("narrowed_submission_standard_met") is not True
        or review.get("narrowed_claim_decision") != "submit_under_narrowed_claim"
    ):
        errors.append("review agent narrowed-claim decision changed")
    if review.get("code_hygiene_checks", {}).get("minimal_reproducible_submission_code_ready") is not False:
        errors.append("minimal reproducible submission code was overclaimed")
    local_outputs: list[tuple[str, str]] = []
    if args.include_local_runners:
        local_outputs, local_errors = run_local_runners()
        errors.extend(local_errors)
        if report.exists():
            append_local_runner_report(report, local_outputs)

    print(output.strip())
    for name, runner_output in local_outputs:
        print(f"[local-runner:{name}]")
        print(runner_output.strip())
    if errors:
        print("human_reproducibility_runner=FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("human_reproducibility_runner=PASS")
    print(f"markdown_report={report}")
    print("examples=4")
    print("methods=11")
    print("matrix_rows=44")
    print("common_reference_order_error_wins=40/40,40/40")
    if args.include_local_runners:
        print("local_runners_invoked=True")
        print("closed_loop_local_replay_invoked=True")
        print("closed_loop_local_runner_candidate_invoked=True")
        print("local_accepted_runner_companion_invoked=True")
        print("local_accepted_runner_companion_rows=12/12")
        print("experiments_launched=local_p1_single_double_plus_closed_loop_replay_and_companion")
    else:
        print("local_runners_invoked=False")
        print("closed_loop_local_replay_invoked=False")
        print("experiments_launched=False")
    print("run_v047_invoked=False")
    print("run_v048_invoked=False")
    print("source_policy_external_rows=0/40")
    print("direct_pc2_proof_gap_closed=True")
    print("proof_gap_scope=direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open")
    print("stage_residual_O_h7_direct_proof=True")
    print("submission_ready=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
