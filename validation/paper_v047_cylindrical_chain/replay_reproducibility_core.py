#!/usr/bin/env python3
"""Replay the compact CMAME reproducibility checks without running experiments."""

from __future__ import annotations

import json
import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MINIMAL = ROOT / "cmame_minimal_reproducibility_candidate"
ADAPTER = ROOT / "cmame_runner_adapter_candidate"


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def run_script(cwd: Path, script: str) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, script],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return proc.returncode, proc.stdout


def format_value(value: object) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:.3e}" if abs(value) < 1.0e-2 else f"{value:.3f}"
    return str(value)


def matrix_markdown(matrix: dict) -> str:
    rows = sorted(
        matrix.get("rows", []),
        key=lambda row: (row.get("example", ""), row.get("method", "")),
    )
    lines = [
        "# CMAME Replay Result Table",
        "",
        "Scope: human-runnable bounded common-reference replay only.",
        "This table reproduces the recorded 44-row, four-example, eleven-method result matrix from embedded artifacts.",
        "Source-policy external superiority is not allowed by this replay.",
        "",
        "| example | method | position order | velocity order | finest velocity error | claim scope | local row accepted | external source-policy closed |",
        "|---|---|---:|---:|---:|---|---:|---:|",
    ]
    for row in rows:
        local_row_accepted = (
            row.get("method") == "local_Gauss6_FullVA"
            and row.get("paper_claim_scope") == "internal_order_evidence"
        )
        lines.append(
            "| "
            f"{row.get('example')} | "
            f"{row.get('method')} | "
            f"{format_value(row.get('position_order'))} | "
            f"{format_value(row.get('velocity_order'))} | "
            f"{format_value(row.get('finest_velocity_error'))} | "
            f"{row.get('paper_claim_scope')} | "
            f"{local_row_accepted} | "
            "False |"
        )
    lines.extend(
        [
            "",
            "Boundary checks:",
            "",
            f"- row count: `{matrix.get('row_count')}`",
            f"- raw rows recomputed: `{matrix.get('raw_row_count')}`",
            f"- methods/examples: `{matrix.get('method_count')}/{len(matrix.get('examples', []))}`",
            f"- common-reference order/error wins: `{matrix.get('direct_nonlocal_velocity_order_wins')}/{matrix.get('direct_nonlocal_velocity_order_comparisons')}`, `{matrix.get('direct_nonlocal_velocity_error_wins')}/{matrix.get('direct_nonlocal_velocity_error_comparisons')}`",
            f"- source-policy external superiority allowed: `{matrix.get('source_policy_external_superiority_allowed')}`",
            f"- paper direct error superiority allowed: `{matrix.get('paper_direct_error_superiority_allowed')}`",
        ]
    )
    return "\n".join(lines) + "\n"


def print_table_preview(matrix: dict) -> None:
    by_example: dict[str, list[dict]] = {}
    for row in matrix.get("rows", []):
        by_example.setdefault(str(row.get("example")), []).append(row)
    print("replay_result_table=bounded_common_reference")
    for example in matrix.get("examples", []):
        rows = sorted(by_example.get(example, []), key=lambda row: str(row.get("method")))
        print(f"[{example}] rows={len(rows)}")
        for row in rows:
            print(
                "  "
                f"{row.get('method')}: "
                f"p={format_value(row.get('position_order'))}, "
                f"v={format_value(row.get('velocity_order'))}, "
                f"e_v={format_value(row.get('finest_velocity_error'))}, "
                f"scope={row.get('paper_claim_scope')}, "
                f"local_row_accepted={row.get('method') == 'local_Gauss6_FullVA'}, "
                "external_source_policy_closed=False"
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--table",
        action="store_true",
        help="Print the four-example/method order-error table after replay checks.",
    )
    parser.add_argument(
        "--markdown-report",
        type=Path,
        default=None,
        help="Write a markdown replay table to the given path.",
    )
    args = parser.parse_args()

    errors: list[str] = []

    minimal_manifest = read_json(MINIMAL / "MANIFEST.json")
    adapter_manifest = read_json(ADAPTER / "MANIFEST.json")
    matrix = read_json(MINIMAL / "data" / "PAPER_NUMERICAL_RESULT_MATRIX.json")
    proof = read_json(MINIMAL / "data" / "PROOF_CLOSURE_MANIFEST.json")
    review = read_json(MINIMAL / "data" / "CMAME_REVIEW_AGENT_REPORT.json")

    minimal_code, minimal_out = run_script(MINIMAL, "scripts/replay_paper_matrix.py")
    adapter_code, adapter_out = run_script(ADAPTER, "scripts/run_four_example_matrix_adapter.py")

    if minimal_code != 0:
        errors.append("minimal replay failed")
    if adapter_code != 0:
        errors.append("runner adapter embedded replay failed")
    if "cmame_minimal_candidate_replay=PASS" not in minimal_out:
        errors.append("minimal replay PASS marker missing")
    if "cmame_runner_adapter_candidate=PASS" not in adapter_out:
        errors.append("adapter replay PASS marker missing")

    if minimal_manifest.get("read_only_replay_package") is not True:
        errors.append("minimal package is not marked read-only replay")
    if minimal_manifest.get("submission_ready") is not False:
        errors.append("minimal package overclaims submission readiness")
    if adapter_manifest.get("self_contained_simulation_runner") is not False:
        errors.append("adapter overclaims self-contained simulation runner")
    if adapter_manifest.get("submission_ready") is not False:
        errors.append("adapter overclaims submission readiness")

    if matrix.get("row_count") != 44 or matrix.get("method_count") != 11:
        errors.append("paper matrix row/method count changed")
    if set(matrix.get("examples", [])) != {
        "single_pendulum",
        "double_pendulum",
        "four_link",
        "slider_crank",
    }:
        errors.append("paper matrix example set changed")
    if matrix.get("direct_nonlocal_velocity_order_wins") != 40:
        errors.append("common-reference order wins changed")
    if matrix.get("direct_nonlocal_velocity_error_wins") != 40:
        errors.append("common-reference error wins changed")
    if matrix.get("source_policy_external_superiority_allowed") is not False:
        errors.append("source-policy superiority was overclaimed")

    if proof.get("closure_state", {}).get("proof_gap_closed") is not True:
        errors.append("proof gap direct closure missing")
    if proof.get("closure_state", {}).get("stage_residual_O_h7_implementation_defect_proved") is not True:
        errors.append("stage-residual direct proof missing")
    if (
        review.get("narrowed_submission_standard_met") is not True
        or review.get("narrowed_claim_decision") != "submit_under_narrowed_claim"
    ):
        errors.append("review agent narrowed-claim decision changed")
    if review.get("code_hygiene_checks", {}).get("minimal_reproducible_submission_code_ready") is not False:
        errors.append("minimal reproducible submission code was overclaimed")

    if args.table:
        print_table_preview(matrix)
    if args.markdown_report is not None:
        args.markdown_report.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_report.write_text(matrix_markdown(matrix), encoding="utf-8")
        print(f"markdown_report={args.markdown_report}")

    print(minimal_out.strip())
    print(adapter_out.strip())

    if errors:
        print("reproducibility_core=FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("reproducibility_core=PASS")
    print("experiments_launched=False")
    print("run_v047_invoked=False")
    print("run_v048_invoked=False")
    print("embedded_matrix_rows=44")
    print("methods_examples=11/4")
    print("common_reference_order_error_wins=40/40,40/40")
    print("source_policy_external_rows_closed=0/40")
    print("direct_pc2_proof_gap_closed=True")
    print("proof_gap_scope=direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open")
    print("stage_residual_O_h7_direct_proof=True")
    print("submission_ready=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
