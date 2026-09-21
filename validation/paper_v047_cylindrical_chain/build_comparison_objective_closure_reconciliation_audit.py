#!/usr/bin/env python3
"""Reconcile the closed common-reference comparison with source-policy caveats."""

from __future__ import annotations

import json
from pathlib import Path


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
V048 = ROOT.parent / "numerics" / "v048_cross_paper_same_test_benchmarks" / "results"
OUT_JSON = PAPER / "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.json"
OUT_MD = PAPER / "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.md"


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def main() -> None:
    objective = read_json(V048 / "objective_closure_audit.json")
    coverage = read_json(V048 / "baseline_coverage_matrix.json")
    recomputation = read_json(PAPER / "COMMON_REFERENCE_ORDER_RECOMPUTATION_AUDIT.json")
    diagnosis = read_json(PAPER / "EXTERNAL_BASELINE_SOURCE_POLICY_DIAGNOSIS.json")
    result_pack = read_json(PAPER / "PAPER_RESULT_PACK.json")
    forensic = read_json(V048 / "all_examples_apples_to_apples_forensic_audit.json")

    common = result_pack.get("common_reference", {})
    comparison_matrix_closed = (
        objective.get("objective_complete") is True
        and objective.get("passed_count") == objective.get("row_count") == 13
        and objective.get("required_methods_resolved") is True
        and coverage.get("source_unresolved_methods") == []
        and coverage.get("required_methods_resolved") is True
        and recomputation.get("all_summary_orders_recomputed") is True
        and recomputation.get("verification", {}).get("mismatch_count") == 0
        and common.get("apples_to_apples_rows") == common.get("apples_to_apples_total_rows") == 44
        and objective.get("local_velocity_order_wins") == objective.get("local_velocity_order_comparisons") == 40
        and objective.get("local_finest_velocity_error_wins")
        == objective.get("local_finest_velocity_error_comparisons")
        == 40
    )
    source_policy_open = (
        objective.get("source_policy_reproduction") is False
        and diagnosis.get("source_policy_recheck_required") is True
        and diagnosis.get("external_superiority_allowed") is False
    )
    claim_allowed = comparison_matrix_closed and source_policy_open

    result = {
        "schema": "comparison-objective-closure-reconciliation-v1",
        "status": "common_reference_objective_closed_source_policy_reproduction_open",
        "submission_ready": False,
        "comparison_matrix_closed": comparison_matrix_closed,
        "common_reference_claim_allowed": claim_allowed,
        "source_policy_reproduction_open": source_policy_open,
        "source_policy_superiority_claim_allowed": False,
        "paper_direct_error_superiority_claim_allowed": forensic.get(
            "direct_error_superiority_claim_allowed_for_paper",
            False,
        ),
        "strict_external_error_claim_allowed_rows": forensic.get(
            "strict_external_error_claim_allowed_rows",
            0,
        ),
        "all_method_example_cells_checked": forensic.get("row_count"),
        "examples": objective.get("examples"),
        "common_reference_cells": common.get("summary_rows"),
        "raw_rows_recomputed": recomputation.get("coverage", {}).get("raw_ok_row_count"),
        "summary_mismatches": recomputation.get("verification", {}).get("mismatch_count"),
        "required_method_labels_resolved": coverage.get("required_methods_resolved"),
        "source_unresolved_methods": coverage.get("source_unresolved_methods"),
        "alias_resolved_methods": coverage.get("alias_resolved_methods"),
        "scope_excluded_methods": coverage.get("scope_excluded_methods"),
        "direct_nonlocal_velocity_order_wins": objective.get("local_velocity_order_wins"),
        "direct_nonlocal_velocity_order_comparisons": objective.get("local_velocity_order_comparisons"),
        "direct_nonlocal_finest_velocity_error_wins": objective.get("local_finest_velocity_error_wins"),
        "direct_nonlocal_finest_velocity_error_comparisons": objective.get(
            "local_finest_velocity_error_comparisons"
        ),
        "original_paper_velocity_error_wins": objective.get("original_paper_velocity_error_wins"),
        "original_paper_velocity_error_comparisons": objective.get("original_paper_velocity_error_comparisons"),
        "kissel_negrut_velocity_error_wins": objective.get("kissel_negrut_velocity_error_wins"),
        "kissel_negrut_velocity_error_comparisons": objective.get(
            "kissel_negrut_velocity_error_comparisons"
        ),
        "source_policy_flagged_rows": diagnosis.get("coverage", {}).get("flagged_row_count"),
        "source_policy_velocity_mismatch_rows": diagnosis.get("coverage", {}).get(
            "position_aligned_velocity_mismatch_count"
        ),
        "b2_b4_reconciliation": {
            "comparison_matrix_component_closed": comparison_matrix_closed,
            "source_suite_policy_component_open": source_policy_open,
            "paper_submission_b2_b4_can_close_now": False,
            "reason": (
                "finite-grid common-reference order/error diagnostics are assembled, but source-paper "
                "default-policy reproduction and paper-level direct error superiority remain non-claims "
                "under the current CMAME blocker contract"
            ),
        },
        "paper_wording_contract": {
            "allowed": (
                "finite-grid common-reference order/error diagnostic against accepted runnable rows"
            ),
            "forbidden": (
                "paper-level direct error superiority, source-paper default-policy superiority, or complete source-policy reproduction"
            ),
        },
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# Comparison Objective Closure Reconciliation Audit",
        "",
        "Status: **bounded common-reference diagnostic assembled; source-policy reproduction open**.",
        "",
        f"- Comparison matrix closed: `{result['comparison_matrix_closed']}`.",
        f"- Common-reference claim allowed: `{result['common_reference_claim_allowed']}`.",
        f"- Paper direct error superiority allowed: `{result['paper_direct_error_superiority_claim_allowed']}`.",
        f"- Strict external error-claim rows allowed: `{result['strict_external_error_claim_allowed_rows']}`.",
        f"- All method/example cells checked: `{result['all_method_example_cells_checked']}`.",
        f"- Source-policy superiority allowed: `{result['source_policy_superiority_claim_allowed']}`.",
        f"- Common-reference cells: `{result['common_reference_cells']}`.",
        f"- Raw rows recomputed: `{result['raw_rows_recomputed']}`.",
        f"- Summary mismatches: `{result['summary_mismatches']}`.",
        f"- Required method labels resolved: `{result['required_method_labels_resolved']}`.",
        f"- Source-unresolved methods: `{result['source_unresolved_methods']}`.",
        f"- Alias-resolved methods: `{', '.join(result['alias_resolved_methods'])}`.",
        f"- Scope-excluded methods: `{', '.join(result['scope_excluded_methods'])}`.",
        f"- Direct nonlocal velocity-order wins: `{result['direct_nonlocal_velocity_order_wins']}/{result['direct_nonlocal_velocity_order_comparisons']}`.",
        f"- Direct nonlocal finest-velocity-error wins: `{result['direct_nonlocal_finest_velocity_error_wins']}/{result['direct_nonlocal_finest_velocity_error_comparisons']}`.",
        f"- Original-paper velocity-error wins: `{result['original_paper_velocity_error_wins']}/{result['original_paper_velocity_error_comparisons']}`.",
        f"- Kissel/Negrut-family velocity-error wins: `{result['kissel_negrut_velocity_error_wins']}/{result['kissel_negrut_velocity_error_comparisons']}`.",
        f"- Source-policy flagged rows: `{result['source_policy_flagged_rows']}`.",
        f"- Source-policy velocity-mismatch rows: `{result['source_policy_velocity_mismatch_rows']}`.",
        f"- B2/B4 can close now: `{result['b2_b4_reconciliation']['paper_submission_b2_b4_can_close_now']}`.",
        "",
        "## Claim Boundary",
        "",
        "- Allowed: bounded finite-grid common-reference order/error diagnostic against accepted runnable rows.",
        "- Forbidden: paper-level direct error superiority, source-paper default-policy superiority, or complete source-policy reproduction.",
        "- The VP Lie-group ODE label is treated as the alias-resolved coordinate-partitioning wrapper, not a separate unresolved row.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("comparison_objective_closure_reconciliation_audit=written")
    print(f"comparison_matrix_closed={comparison_matrix_closed}")
    print(f"common_reference_claim_allowed={claim_allowed}")
    print("source_policy_superiority_claim_allowed=False")


if __name__ == "__main__":
    main()
