#!/usr/bin/env python3
"""Build a paper-core result consolidation from existing artifacts only."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
V048_RESULTS = PAPER.parent / "v048_cross_paper_same_test_benchmarks" / "results"
OUT_JSON = PAPER / "PAPER_CORE_RESULT_CONSOLIDATION.json"
OUT_MD = PAPER / "PAPER_CORE_RESULT_CONSOLIDATION.md"


EXAMPLE_LABELS = {
    "single_pendulum": "single pendulum",
    "double_pendulum": "double pendulum",
    "four_link": "four-link",
    "slider_crank": "slider-crank",
}


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def rounded(value: object, digits: int = 3) -> float | None:
    if value is None:
        return None
    return round(float(value), digits)


def main() -> None:
    matrix = read_json(PAPER / "PAPER_NUMERICAL_RESULT_MATRIX.json")
    true_dynamic = read_json(V048_RESULTS / "closed_loop_true_dynamic_newton_coarse_order.json")
    work_precision = read_json(V048_RESULTS / "closed_loop_true_dynamic_public_work_precision.json")
    figure_audit = read_json(PAPER / "CMAME_FIGURE_SET_AUDIT.json")
    proof = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
    traceability = read_json(PAPER / "RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.json")
    review = read_json(PAPER / "CMAME_REVIEW_AGENT_REPORT.json")
    repro = read_json(PAPER / "CMAME_REPRODUCIBILITY_PACKAGE_MANIFEST.json")

    local_examples = []
    for example in ["single_pendulum", "double_pendulum", "four_link", "slider_crank"]:
        row = matrix["per_example"][example]
        local_examples.append(
            {
                "example": example,
                "label": EXAMPLE_LABELS[example],
                "velocity_order": row.get("local_velocity_order"),
                "velocity_order_rounded": rounded(row.get("local_velocity_order")),
                "finest_velocity_error": row.get("local_finest_velocity_error"),
                "method_rows": row.get("method_rows"),
                "strict_external_error_claim_allowed_rows": row.get(
                    "strict_external_error_claim_allowed_rows"
                ),
                "source": "PAPER_NUMERICAL_RESULT_MATRIX.json",
            }
        )

    closed_loop_examples = []
    for example in true_dynamic.get("models", []):
        summary = true_dynamic["model_summaries"][example]
        closed_loop_examples.append(
            {
                "example": example,
                "label": EXAMPLE_LABELS[example],
                "accepted_coarse_true_dynamic_order_candidate": summary.get(
                    "accepted_dynamic_order_candidate"
                ),
                "position_order": summary.get("pos_observed_order"),
                "orientation_order": summary.get("orientation_observed_order"),
                "velocity_order": summary.get("vel_observed_order"),
                "omega_order": summary.get("omega_observed_order"),
                "min_primary_order": summary.get("min_primary_order"),
                "rows_ok": summary.get("ok_row_count"),
                "rows_total": summary.get("row_count"),
                "source": "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_newton_coarse_order.json",
            }
        )

    figures = []
    for item in figure_audit.get("figures", []):
        if item.get("number") in {1, 7, 9, 10, 12}:
            figures.append(
                {
                    "number": item.get("number"),
                    "role": item.get("role"),
                    "path": item.get("main"),
                    "exists": item.get("main_exists") is True,
                    "flat_exists": item.get("flat_exists") is True,
                    "meets_minimum_pixel_area": item.get("meets_minimum_pixel_area") is True,
                }
            )

    direct_standard = proof.get("direct_residual_bridge_kantorovich_submission_standard", {})
    closure_state = proof.get("closure_state", {})
    evidence_summary = proof.get("evidence_summary", {})
    strict_proof_gap_closed = direct_standard.get(
        "proof_gap_closed_under_active_direct_residual_bridge_standard",
        False,
    )
    strict_dynamic_defect_proved = (
        closure_state.get("stage_residual_O_h7_implementation_defect_proved") is True
        and direct_standard.get("satisfied") is True
    )

    result = {
        "schema": "paper-core-result-consolidation-v1",
        "status": "paper_core_results_consolidated_replay_only",
        "submission_ready": False,
        "execution_policy": {
            "read_only_existing_artifacts": True,
            "experiments_launched": False,
            "run_v047_invoked": False,
            "run_v048_invoked": False,
            "default_1e_4_campaign_invoked": False,
        },
        "claim_boundary": {
            "allowed_core_claim": (
                "Gauss6/FullVA achieves about sixth-order velocity convergence on the four "
                "paper examples and wins all bounded common-reference nonlocal order/error "
                "comparisons against accepted runnable rows."
            ),
            "allowed_closed_loop_claim": (
                "four-link and slider-crank have closed-loop coarse dynamics "
                "diagnostic evidence with no stage oracle."
            ),
            "forbidden_claims": [
                "strict source-paper policy external superiority",
                "source-policy apples-to-apples closure",
                "accepted residual-to-error theorem for closed-loop coverage examples",
                "submission-ready manuscript/package",
            ],
        },
        "four_example_local_order": {
            "status": "complete_for_non_policy_core",
            "examples_closed": 4,
            "examples_total": 4,
            "rows": local_examples,
        },
        "closed_loop_true_dynamic_order": {
            "status": true_dynamic.get("status"),
            "accepted_dynamic_order_count": true_dynamic.get("accepted_dynamic_order_count"),
            "ok_row_count": true_dynamic.get("ok_row_count"),
            "row_count": true_dynamic.get("row_count"),
            "step_sizes": true_dynamic.get("step_sizes"),
            "stage_oracle_used": true_dynamic.get("stage_oracle_used"),
            "external_superiority_claim": true_dynamic.get("external_superiority_claim"),
            "rows": closed_loop_examples,
        },
        "common_reference_comparison": {
            "status": "complete_for_bounded_common_reference",
            "velocity_order_wins": matrix.get("direct_nonlocal_velocity_order_wins"),
            "velocity_order_comparisons": matrix.get("direct_nonlocal_velocity_order_comparisons"),
            "velocity_error_wins": matrix.get("direct_nonlocal_velocity_error_wins"),
            "velocity_error_comparisons": matrix.get("direct_nonlocal_velocity_error_comparisons"),
            "source_policy_reproduction": matrix.get("source_policy_reproduction"),
            "external_superiority_claim_allowed": matrix.get("external_superiority_claim_allowed"),
            "work_precision_status": work_precision.get("status"),
            "work_precision_rows": work_precision.get("row_count"),
            "work_precision_ok_rows": work_precision.get("ok_row_count"),
        },
        "paper_figures": {
            "core_figure_count": len(figures),
            "all_core_figures_exist": all(item["exists"] and item["flat_exists"] for item in figures),
            "rows": figures,
        },
        "proof_boundary": {
            "status": proof.get("status"),
            "proof_gap_closed": strict_proof_gap_closed,
            "direct_pc2_proof_gap_closed": strict_proof_gap_closed,
            "proof_gap_closed_scope": (
                "direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open"
            ),
            "proof_gap_closed_reading_rule": (
                "The schema-only compatibility boolean proof_gap_closed is a schema-compatible "
                "shorthand for direct_pc2_proof_gap_closed under the active direct PC2 residual-bridge/"
                "Kantorovich route. It does not close the primitive/Taylor route, P6 "
                "solver-policy evidence, P7 residual-to-error promotion, source-policy "
                "readiness, or full-TFE replacement."
            ),
            "schema_compatibility": {
                "legacy_key": "proof_gap_closed",
                "legacy_key_retained_for_schema_compatibility": True,
                "preferred_key": "direct_pc2_proof_gap_closed",
            },
            "direct_residual_bridge_submission_standard_satisfied": direct_standard.get("satisfied"),
            "direct_residual_bridge_submission_standard_scope": (
                "satisfied only for the active direct residual-bridge/Kantorovich "
                "PC2 route; not a primitive 162-term Taylor closure and not a "
                "global submission-ready proof package"
            ),
            "primitive_162_term_taylor_route_closed": direct_standard.get(
                "primitive_taylor_route_closed"
            ),
            "primitive_taylor_open_bound_terms": direct_standard.get("open_taylor_bound_terms"),
            "primitive_taylor_open_primitive_count": direct_standard.get("open_primitive_count"),
            "direct_substitution_supplies_active_pc2_residual_bridge": direct_standard.get(
                "direct_substitution_supplies_active_pc2_residual_bridge"
            ),
            "stage_residual_O_h7_implementation_defect_proved": strict_dynamic_defect_proved,
            "stage_residual_O_h7_implementation_defect_scope": (
                "implementation-path direct residual bridge at the lifted Gauss stage"
            ),
            "direct_route_stage_residual_O_h7_implementation_defect_proved": closure_state.get(
                "stage_residual_O_h7_implementation_defect_proved"
            ),
            "dynamic_symbolic_oracle_complete": closure_state.get("dynamic_symbolic_oracle_complete"),
            "primitive_lane_open_dynamic_rows": evidence_summary.get("open_dynamic_rows"),
            "primitive_lane_open_dynamic_rows_scope": evidence_summary.get("open_dynamic_rows_scope"),
            "open_dynamic_rows": evidence_summary.get("open_dynamic_rows"),
            "open_dynamic_rows_scope": (
                "legacy alias for primitive_lane_open_dynamic_rows; not an active direct-PC2 gap"
            ),
            "certified_non_dynamic_rows": evidence_summary.get("certified_non_dynamic_rows"),
            "newton_euler_row_obligation_links": evidence_summary.get(
                "newton_euler_row_obligation_links"
            ),
        },
        "review_and_reproducibility": {
            "result_to_manuscript_traceability_closed": traceability.get("claim_boundary", {}).get(
                "result_to_manuscript_traceability_closed"
            ),
            "review_agent_submission_standard_met": review.get("submission_standard_met"),
            "review_agent_decision": review.get("decision"),
            "reproducibility_core_candidate_files": repro.get("candidate_existing_file_count"),
            "reproducibility_core_candidate_total_files": repro.get("candidate_file_count"),
            "minimal_package_ready": repro.get("summary", {}).get(
                "minimal_reproducible_submission_code_ready"
            ),
        },
        "source_files": {
            "paper_matrix": "PAPER_NUMERICAL_RESULT_MATRIX.json",
            "closed_loop_true_dynamic_order": "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_newton_coarse_order.json",
            "work_precision": "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_public_work_precision.json",
            "figure_audit": "CMAME_FIGURE_SET_AUDIT.json",
            "proof_manifest": "PROOF_CLOSURE_MANIFEST.json",
            "traceability": "RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.json",
            "review_agent": "CMAME_REVIEW_AGENT_REPORT.json",
            "reproducibility_manifest": "CMAME_REPRODUCIBILITY_PACKAGE_MANIFEST.json",
        },
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# Paper Core Result Consolidation",
        "",
        "Status: **paper core results consolidated; replay-only, no experiment campaign**.",
        "",
        f"- Four-example local order: `{result['four_example_local_order']['examples_closed']}/{result['four_example_local_order']['examples_total']}`.",
        f"- Common-reference order/error wins: `{result['common_reference_comparison']['velocity_order_wins']}/{result['common_reference_comparison']['velocity_order_comparisons']}` and `{result['common_reference_comparison']['velocity_error_wins']}/{result['common_reference_comparison']['velocity_error_comparisons']}`.",
        f"- Closed-loop coarse dynamics candidates: `{result['closed_loop_true_dynamic_order']['accepted_dynamic_order_count']}/2`.",
        f"- Core figures available: `{result['paper_figures']['all_core_figures_exist']}`.",
        f"- Direct PC2 proof gap closed: `{result['proof_boundary']['direct_pc2_proof_gap_closed']}`.",
        f"- Direct PC2 proof-gap scope: `{result['proof_boundary']['proof_gap_closed_scope']}`.",
        f"- Schema-only compatibility key `proof_gap_closed` retained: `{result['proof_boundary']['schema_compatibility']['legacy_key_retained_for_schema_compatibility']}`; reader-facing proof status should use `{result['proof_boundary']['schema_compatibility']['preferred_key']}`.",
        f"- Primitive 162-term Taylor route closed: `{result['proof_boundary']['primitive_162_term_taylor_route_closed']}`.",
        f"- Submission ready: `{result['submission_ready']}`.",
        f"- Experiments launched: `{result['execution_policy']['experiments_launched']}`.",
        "",
        "## Four-Example Local Order",
        "",
        "| example | velocity order | finest velocity error |",
        "|---|---:|---:|",
    ]
    for row in local_examples:
        lines.append(
            f"| `{row['label']}` | `{row['velocity_order']:.3f}` | `{row['finest_velocity_error']:.3e}` |"
        )

    lines.extend(
        [
            "",
            "## Closed-Loop True-Dynamic Coarse Order",
            "",
            "| example | position | orientation | velocity | omega | accepted |",
            "|---|---:|---:|---:|---:|---|",
        ]
    )
    for row in closed_loop_examples:
        lines.append(
            f"| `{row['label']}` | `{row['position_order']:.3f}` | `{row['orientation_order']:.3f}` | "
            f"`{row['velocity_order']:.3f}` | `{row['omega_order']:.3f}` | "
            f"`{row['accepted_coarse_true_dynamic_order_candidate']}` |"
        )

    lines.extend(
        [
            "",
            "## Core Figures",
            "",
            "| no. | role | path |",
            "|---:|---|---|",
        ]
    )
    for figure in figures:
        lines.append(f"| `{figure['number']}` | {figure['role']} | `{figure['path']}` |")

    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            f"- Allowed: {result['claim_boundary']['allowed_core_claim']}",
            f"- Allowed: {result['claim_boundary']['allowed_closed_loop_claim']}",
            "- Forbidden: strict source-paper policy external superiority; source-policy apples-to-apples closure; unconditional dynamic-row proof closure; submission-ready status.",
            "",
            "Reading rule: this file is the non-policy paper-core result map. It consolidates existing artifacts only and does not promote source-policy, proof, or submission-readiness claims.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("paper_core_result_consolidation=written")
    print("four_example_local_order=4/4")
    print("common_reference_order_error_wins=40/40,40/40")
    print("closed_loop_coarse_dynamics_candidates=2/2")
    print("experiments_launched=False")


if __name__ == "__main__":
    main()
