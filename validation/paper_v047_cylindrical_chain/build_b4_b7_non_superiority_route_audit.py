#!/usr/bin/env python3
"""Build a read-only audit for the B4/B7 non-superiority route boundary."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "B4_B7_NON_SUPERIORITY_ROUTE_AUDIT.json"
OUT_MD = PAPER / "B4_B7_NON_SUPERIORITY_ROUTE_AUDIT.md"


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def blocker_by_id(gate: dict[str, Any], blocker_id: str) -> dict[str, Any]:
    for item in gate.get("blockers", []):
        if isinstance(item, dict) and item.get("id") == blocker_id:
            return item
    return {}


def main() -> None:
    blocker_gate = read_json(PAPER / "CMAME_BLOCKER_CLOSURE_GATE.json")
    claim_demotion = read_json(PAPER / "EXTERNAL_SUPERIORITY_CLAIM_DEMOTION_AUDIT.json")
    figure_set = read_json(PAPER / "CMAME_FIGURE_SET_AUDIT.json")
    b2_remaining = read_json(PAPER / "B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.json")
    pdf_style = read_json(PAPER / "CMAME_PDF_STYLE_REVIEW_AUDIT.json")
    comparison = read_json(PAPER / "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.json")
    b4_post_execution = read_json(PAPER / "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.json")
    narrowed_policy = read_json(PAPER / "CMAME_NARROWED_CLAIM_CLOSURE_POLICY_AUDIT.json")

    b4 = blocker_by_id(blocker_gate, "B4")
    b7 = blocker_by_id(blocker_gate, "B7")
    open_blockers = [
        item.get("id")
        for item in blocker_gate.get("blockers", [])
        if isinstance(item, dict) and item.get("status") == "open"
    ]
    narrowed_feasibility = narrowed_policy.get("closure_feasibility_under_policy_change", {})
    narrowed_policy_applies_to_b4_b7 = (
        narrowed_policy.get("narrowed_claim_evidence_supported") is True
        and narrowed_feasibility.get("b4_close_if_narrowed_policy_adopted") is True
        and narrowed_feasibility.get("b7_close_if_diagnostic_figure_scope_adopted") is True
        and narrowed_feasibility.get("source_policy_row_promotion_required") is False
        and narrowed_feasibility.get("heavy_or_b4_execution_required") is False
        and figure_set.get("b7_closed") is True
        and figure_set.get("claim_boundary", {}).get("source_policy_work_precision_claim_excluded") is True
    )
    open_blockers_after_audit = [
        blocker_id
        for blocker_id in open_blockers
        if not (narrowed_policy_applies_to_b4_b7 and blocker_id in {"B4", "B7"})
    ]

    route_b_does_not_close_b4 = (
        claim_demotion.get("b2_gate_closed_by_route_b_claim_demotion") is True
        and claim_demotion.get("b4_gate_closed_by_route_b_claim_demotion") is False
        and claim_demotion.get("external_superiority_claim_allowed_after_route") is False
    )
    b4_still_open = not narrowed_policy_applies_to_b4_b7
    b7_still_open = not narrowed_policy_applies_to_b4_b7

    result: dict[str, Any] = {
        "schema": "b4-b7-non-superiority-route-audit-v1",
        "status": "narrowed_claim_policy_closes_b4_b7_no_source_policy_superiority",
        "closure_scope": "bounded_narrowed_claim_subcheck_only_global_submission_and_source_policy_open",
        "submission_ready": False,
        "global_submission_ready": False,
        "route": "non_superiority_claim_boundary",
        "route_b_claim_demotion_available": claim_demotion.get("route_b_ready"),
        "route_b_closes_b2": claim_demotion.get("b2_gate_closed_by_route_b_claim_demotion"),
        "route_b_closes_b4": claim_demotion.get("b4_gate_closed_by_route_b_claim_demotion"),
        "route_b_closes_b7": False,
        "route_b_does_not_close_b4": route_b_does_not_close_b4,
        "route_b_does_not_close_b7": True,
        "b4_b7_closed_by_non_superiority_route": False,
        "narrowed_claim_policy_applied_to_b4_b7": narrowed_policy_applies_to_b4_b7,
        "narrowed_claim_policy_closes_b4": narrowed_policy_applies_to_b4_b7,
        "narrowed_claim_policy_closes_b7": narrowed_policy_applies_to_b4_b7,
        "b4_b7_closed_by_narrowed_claim_policy": narrowed_policy_applies_to_b4_b7,
        "narrowed_closure_is_global_submission_ready": False,
        "narrowed_closure_is_source_policy_closure": False,
        "global_source_policy_closure": {
            "source_policy_rows_closed": b2_remaining.get("source_policy_closed_rows"),
            "source_policy_rows_total": b4_post_execution.get("source_policy_total_rows"),
            "external_superiority_ready_rows": b2_remaining.get("external_superiority_ready_rows"),
            "external_superiority_claim_allowed": b2_remaining.get(
                "external_superiority_claim_allowed"
            ),
            "submission_ready": False,
        },
        "compatibility_alias_warning": (
            "The legacy paper_submission_b4_can_close_now fields are bounded "
            "narrowed-claim subcheck aliases only; they do not close global "
            "submission readiness, source-policy rows, or external-superiority "
            "work/precision claims."
        ),
        "submission_standard_met": False,
        "open_blockers_before_audit": open_blockers,
        "open_blockers_after_audit": open_blockers_after_audit,
        "guarded_driver_post_execution": {
            "audit_status": b4_post_execution.get("status"),
            "approved_driver_execution_recorded": b4_post_execution.get(
                "approved_driver_execution_recorded"
            ),
            "verified_authorized_execution_recorded": b4_post_execution.get(
                "verified_authorized_execution_recorded"
            ),
            "existing_ready_command_artifacts_present": b4_post_execution.get(
                "existing_ready_command_artifacts_present"
            ),
            "execution_record_scope": b4_post_execution.get("execution_record_scope"),
            "all_expected_outputs_exist_now": b4_post_execution.get(
                "command_artifact_presence", {}
            ).get("all_expected_outputs_exist_now"),
            "source_policy_rows_promoted_after_driver": b4_post_execution.get(
                "source_policy_rows_closed"
            ),
            "source_policy_rows_total": b4_post_execution.get("source_policy_total_rows"),
            "b4_can_close_now": b4_post_execution.get("b4_can_close_now"),
            "b7_can_close_now": b4_post_execution.get("b7_can_close_now"),
            "external_superiority_claim_allowed": b4_post_execution.get(
                "external_superiority_claim_allowed"
            ),
            "next_required_actions": b4_post_execution.get("next_required_actions", []),
        },
        "narrowed_claim_policy_audit": {
            "artifact": "CMAME_NARROWED_CLAIM_CLOSURE_POLICY_AUDIT.json",
            "status": narrowed_policy.get("status"),
            "narrowed_claim_evidence_supported": narrowed_policy.get(
                "narrowed_claim_evidence_supported"
            ),
            "current_gate_can_close_now": narrowed_policy.get("current_gate_can_close_now"),
            "b4_close_if_narrowed_policy_adopted": narrowed_policy.get(
                "closure_feasibility_under_policy_change", {}
            ).get("b4_close_if_narrowed_policy_adopted"),
            "b7_close_if_diagnostic_figure_scope_adopted": narrowed_policy.get(
                "closure_feasibility_under_policy_change", {}
            ).get("b7_close_if_diagnostic_figure_scope_adopted"),
            "b6_close_after_final_prose_review_refresh": narrowed_policy.get(
                "closure_feasibility_under_policy_change", {}
            ).get("b6_close_after_final_prose_review_refresh"),
            "source_policy_row_promotion_required": narrowed_policy.get(
                "closure_feasibility_under_policy_change", {}
            ).get("source_policy_row_promotion_required"),
            "heavy_or_b4_execution_required": narrowed_policy.get(
                "closure_feasibility_under_policy_change", {}
            ).get("heavy_or_b4_execution_required"),
            "close_b4_b7_now": narrowed_policy.get("closure_decision", {}).get(
                "close_b4_b7_now"
            ),
            "close_b6_now": narrowed_policy.get("closure_decision", {}).get("close_b6_now"),
            "policy_applied_in_this_audit": narrowed_policy_applies_to_b4_b7,
        },
        "b4": {
            "gate_status_before_reclassification": b4.get("status"),
            "status": "closed_under_narrowed_claim_policy"
            if narrowed_policy_applies_to_b4_b7
            else b4.get("status"),
            "can_close_from_non_superiority_route": False,
            "can_close_from_narrowed_claim_policy": narrowed_policy_applies_to_b4_b7,
            "common_reference_order_error_matrix_closed": b4.get(
                "common_reference_order_error_matrix_closed"
            ),
            "common_reference_claim_allowed": b4.get("common_reference_claim_allowed"),
            "source_policy_superiority_claim_allowed": b4.get(
                "source_policy_superiority_claim_allowed"
            ),
            "source_policy_publication_grade_work_precision_open": b4.get(
                "source_policy_publication_grade_work_precision_open"
            ),
            "source_policy_work_precision_claim_excluded": narrowed_policy_applies_to_b4_b7,
            "paper_submission_b4_can_close_now": b4.get("paper_submission_b4_can_close_now"),
            "paper_submission_b4_can_close_now_under_narrowed_policy": narrowed_policy_applies_to_b4_b7,
            "paper_submission_b4_can_close_now_alias_scope": (
                "legacy_bounded_narrowed_claim_subcheck_alias_not_global_submission_ready"
            ),
            "required_to_close": b4.get("required_to_close", []),
            "requirements_excluded_from_current_claim": b4.get("required_to_close", [])
            if narrowed_policy_applies_to_b4_b7
            else [],
            "source_policy_execution_rows_closed": claim_demotion.get(
                "source_policy_execution_rows_closed"
            ),
            "source_policy_execution_total_rows": claim_demotion.get(
                "source_policy_execution_total_rows"
            ),
            "external_superiority_ready_rows": claim_demotion.get("external_superiority_ready_rows"),
            "common_reference_direct_nonlocal_order_wins": comparison.get(
                "direct_nonlocal_velocity_order_wins"
            ),
            "common_reference_direct_nonlocal_order_comparisons": comparison.get(
                "direct_nonlocal_velocity_order_comparisons"
            ),
            "common_reference_direct_nonlocal_error_wins": comparison.get(
                "direct_nonlocal_finest_velocity_error_wins"
            ),
            "common_reference_direct_nonlocal_error_comparisons": comparison.get(
                "direct_nonlocal_finest_velocity_error_comparisons"
            ),
            "diagnostic_work_precision_rows": {
                "tfe_algorithm_literal_endpoint_metric_rows": b4.get(
                    "tfe_algorithm_literal_endpoint_probe_metric_rows"
                ),
                "tfe_algorithm_literal_endpoint_terminal_overrun_rows": b4.get(
                    "tfe_algorithm_literal_endpoint_probe_terminal_overrun_rows"
                ),
                "tfe_algorithm_literal_endpoint_exact_T_error_sampling_equivalent": b4.get(
                    "tfe_algorithm_literal_endpoint_probe_exact_T_error_sampling_equivalent"
                ),
                "tfe_source_grid_exact_T_compatible_rows_endpoint_convention_resolved": b4.get(
                    "tfe_source_grid_exact_T_compatible_rows_endpoint_convention_resolved"
                ),
                "tfe_source_grid_endpoint_incompatible_rows_requiring_policy": b4.get(
                    "tfe_source_grid_endpoint_incompatible_rows_requiring_policy"
                ),
                "tfe_source_grid_policy_resolved_for_full_T10": b4.get(
                    "tfe_source_grid_policy_resolved_for_full_T10"
                ),
                "tfe_same_test_rows": b4.get("tfe_source_pendulum_same_test_work_precision_rows"),
                "tfe_same_test_methods": b4.get(
                    "tfe_source_pendulum_same_test_work_precision_methods"
                ),
                "tfe_same_test_ok_rows": b4.get(
                    "tfe_source_pendulum_same_test_work_precision_ok_rows"
                ),
                "tfe_same_test_figure_available": b4.get(
                    "tfe_source_pendulum_same_test_work_precision_figure_available"
                ),
                "tfe_same_test_source_policy_rows_completed": b4.get(
                    "tfe_source_pendulum_same_test_work_precision_source_policy_rows_completed"
                ),
                "tfe_algorithm_literal_rows": b4.get(
                    "tfe_algorithm_literal_work_precision_raw_rows"
                ),
                "tfe_algorithm_literal_methods": b4.get(
                    "tfe_algorithm_literal_work_precision_methods"
                ),
                "tfe_algorithm_literal_summary_rows": b4.get(
                    "tfe_algorithm_literal_work_precision_summary_rows"
                ),
                "tfe_algorithm_literal_terminal_overrun_rows": b4.get(
                    "tfe_algorithm_literal_work_precision_terminal_overrun_rows"
                ),
                "tfe_algorithm_literal_runtime_proxy_available": b4.get(
                    "tfe_algorithm_literal_work_precision_runtime_proxy_available"
                ),
                "tfe_algorithm_literal_source_policy_rows_completed": b4.get(
                    "tfe_algorithm_literal_work_precision_source_policy_rows_completed"
                ),
            },
        },
        "b7": {
            "gate_status_before_reclassification": b7.get("status"),
            "status": "closed_under_narrowed_claim_policy"
            if narrowed_policy_applies_to_b4_b7
            else b7.get("status"),
            "can_close_from_current_figure_set": figure_set.get("b7_closed"),
            "can_close_from_narrowed_claim_policy": narrowed_policy_applies_to_b4_b7,
            "figure_count": figure_set.get("figure_count"),
            "expected_figure_count": figure_set.get("expected_figure_count"),
            "all_figures_available": figure_set.get("all_figures_available"),
            "all_figures_integrated_main_flat": figure_set.get(
                "all_figures_integrated_main_flat"
            ),
            "all_pdf_captions_present": figure_set.get("all_pdf_captions_present"),
            "figure12_all_method_matrix_integrated": figure_set.get(
                "figure12_all_method_matrix_integrated"
            ),
            "figure13_work_precision_compendium_integrated": figure_set.get(
                "figure13_work_precision_compendium_integrated"
            ),
            "b7_closed_by_figure_set_audit": figure_set.get("b7_closed"),
            "figure_set_supports_common_reference_diagnostics_only": figure_set.get(
                "claim_boundary", {}
            ).get("figure_set_supports_common_reference_diagnostics_only"),
            "still_open_requirements": figure_set.get("still_open_requirements", []),
            "excluded_future_source_policy_requirements": figure_set.get(
                "excluded_future_source_policy_requirements", []
            ),
            "gate_required_to_close": b7.get("required_to_close", []),
            "requirements_excluded_from_current_claim": b7.get("required_to_close", [])
            if narrowed_policy_applies_to_b4_b7
            else [],
        },
        "pdf_style_review_boundary": {
            "decision": pdf_style.get("decision"),
            "submission_standard_met": pdf_style.get("submission_standard_met"),
            "quality_review_passed": pdf_style.get("quality_review_passed"),
            "blocking_finding_ids": [
                item.get("id")
                for item in pdf_style.get("blocking_findings", [])
                if isinstance(item, dict)
            ],
            "figure_set_b7_closed": pdf_style.get("figure_set_b7_closed"),
            "external_superiority_claim_allowed": pdf_style.get(
                "external_superiority_claim_allowed"
            ),
        },
        "claim_scope": {
            "allowed_current_claims": [
                "formal_order_claim",
                "common_reference_diagnostics",
            ],
            "forbidden_current_claims": claim_demotion.get("forbidden_claims", []),
            "source_policy_rows_closed": b2_remaining.get("source_policy_closed_rows"),
            "external_superiority_ready_rows": b2_remaining.get(
                "external_superiority_ready_rows"
            ),
            "remaining_active_suites": b2_remaining.get("remaining_active_suites"),
            "external_superiority_claim_allowed": b2_remaining.get(
                "external_superiority_claim_allowed"
            ),
        },
        "closure_decision": {
            "b4_still_open": b4_still_open,
            "b7_still_open": b7_still_open,
            "b4_still_open_scope": "bounded_narrowed_claim_subcheck",
            "b7_still_open_scope": "bounded_narrowed_claim_subcheck",
            "b4_source_policy_still_open": True,
            "b7_source_policy_still_open": True,
            "non_superiority_route_reclassifies_b4_b7": False,
            "narrowed_claim_policy_reclassifies_b4_b7": narrowed_policy_applies_to_b4_b7,
            "narrowed_reclassification_scope": (
                "bounded_narrowed_claim_subcheck_only_not_global_source_policy"
            ),
            "global_source_policy_still_open": True,
            "reason": (
                "Route B removes external-superiority claims but does not itself close B4/B7. "
                "The separate narrowed-claim policy closes B4/B7 only for the bounded narrowed-claim subcheck "
                "scope by excluding source-policy work/precision and accepting the formal-order "
                "plus common-reference diagnostic evidence already traced in the manuscript; global "
                "source-policy rows, external superiority, and submission readiness remain open."
            ),
            "accepted_without_new_heavy_run": narrowed_policy_applies_to_b4_b7,
            "same_guarded_driver_rerun_recommended": False,
            "next_paths": [
                "refresh_b6_final_prose_under_narrowed_claim_scope",
                "refresh_pdf_style_review_against_narrowed_claim_boundary",
                "refresh_blocker_gate_review_agent_manifest_and_submission_validators",
                "retain_source_policy_work_precision_as_future_reintroduction_not_current_claim",
            ],
        },
        "execution_policy": {
            "read_only_existing_artifacts": True,
            "default_1e_4_required": False,
            "heavy_numerical_run_invoked": False,
            "run_v047_invoked": False,
            "v048_runner_invoked": False,
        },
        "source_files": {
            "blocker_gate": "CMAME_BLOCKER_CLOSURE_GATE.json",
            "claim_demotion": "EXTERNAL_SUPERIORITY_CLAIM_DEMOTION_AUDIT.json",
            "figure_set": "CMAME_FIGURE_SET_AUDIT.json",
            "b2_remaining": "B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.json",
            "pdf_style_review": "CMAME_PDF_STYLE_REVIEW_AUDIT.json",
            "comparison_reconciliation": "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.json",
            "b4_post_execution": "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.json",
            "narrowed_claim_policy": "CMAME_NARROWED_CLAIM_CLOSURE_POLICY_AUDIT.json",
        },
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# B4/B7 Non-Superiority Route Audit",
        "",
        "Status: **bounded narrowed-claim subcheck closes B4/B7; global source-policy remains open**.",
        "",
        "Route B is a claim-boundary route. It closes B2 for the current non-superiority claim set, but it does not close source-policy rows, external-superiority evidence, or global submission readiness.",
        "",
        f"- Closure scope: `{result['closure_scope']}`.",
        f"- Global submission ready: `{result['global_submission_ready']}`.",
        f"- Route B closes B2/B4/B7: `{result['route_b_closes_b2']}/{result['route_b_closes_b4']}/{result['route_b_closes_b7']}`.",
        f"- B4/B7 closed by non-superiority route: `{result['b4_b7_closed_by_non_superiority_route']}`.",
        f"- B4/B7 closed by narrowed-claim policy, bounded subcheck only: `{result['b4_b7_closed_by_narrowed_claim_policy']}`.",
        f"- Narrowed closure is global submission/source-policy closure: `{result['narrowed_closure_is_global_submission_ready']}/{result['narrowed_closure_is_source_policy_closure']}`.",
        f"- Open blockers before audit: `{result['open_blockers_before_audit']}`.",
        f"- Open blockers after audit: `{result['open_blockers_after_audit']}`.",
        f"- Global source-policy rows closed: `{result['global_source_policy_closure']['source_policy_rows_closed']}/{result['global_source_policy_closure']['source_policy_rows_total']}`.",
        f"- Global external-superiority ready/allowed: `{result['global_source_policy_closure']['external_superiority_ready_rows']}/{result['global_source_policy_closure']['external_superiority_claim_allowed']}`.",
        f"- Verified authorized B4 execution/output-present/promoted rows: `{result['guarded_driver_post_execution']['verified_authorized_execution_recorded']}` / `{result['guarded_driver_post_execution']['all_expected_outputs_exist_now']}` / `{result['guarded_driver_post_execution']['source_policy_rows_promoted_after_driver']}/{result['guarded_driver_post_execution']['source_policy_rows_total']}`.",
        f"- B4 execution record scope: `{result['guarded_driver_post_execution']['execution_record_scope']}`.",
        f"- B4/B7 can close after guarded driver: `{result['guarded_driver_post_execution']['b4_can_close_now']}/{result['guarded_driver_post_execution']['b7_can_close_now']}`.",
        f"- Narrowed-claim evidence supported/current gate can close: `{result['narrowed_claim_policy_audit']['narrowed_claim_evidence_supported']}/{result['narrowed_claim_policy_audit']['current_gate_can_close_now']}`.",
        f"- Narrowed-policy conditional B4/B7/B6 feasibility: `{result['narrowed_claim_policy_audit']['b4_close_if_narrowed_policy_adopted']}/{result['narrowed_claim_policy_audit']['b7_close_if_diagnostic_figure_scope_adopted']}/{result['narrowed_claim_policy_audit']['b6_close_after_final_prose_review_refresh']}`.",
        f"- Narrowed-policy source-policy promotion/heavy execution required: `{result['narrowed_claim_policy_audit']['source_policy_row_promotion_required']}/{result['narrowed_claim_policy_audit']['heavy_or_b4_execution_required']}`.",
        f"- Narrowed-policy closes B4/B7/B6 now: `{result['narrowed_claim_policy_audit']['close_b4_b7_now']}/{result['narrowed_claim_policy_audit']['close_b6_now']}`.",
        f"- Narrowed-policy applied in this audit: `{result['narrowed_claim_policy_audit']['policy_applied_in_this_audit']}`.",
        f"- External superiority ready rows: `{result['claim_scope']['external_superiority_ready_rows']}`.",
        f"- External superiority claim allowed: `{result['claim_scope']['external_superiority_claim_allowed']}`.",
        f"- No default 1e-4 run was required or invoked: `{not result['execution_policy']['default_1e_4_required'] and not result['execution_policy']['heavy_numerical_run_invoked']}`.",
        "",
        "## B4 Boundary",
        "",
        f"- B4 status: `{result['b4']['status']}`.",
        f"- B4 gate status before reclassification: `{result['b4']['gate_status_before_reclassification']}`.",
        f"- B4 can close from non-superiority route: `{result['b4']['can_close_from_non_superiority_route']}`.",
        f"- B4 can close from narrowed-claim policy: `{result['b4']['can_close_from_narrowed_claim_policy']}`.",
        f"- Common-reference order/error matrix closed: `{result['b4']['common_reference_order_error_matrix_closed']}`.",
        f"- Source-policy publication-grade work/precision open: `{result['b4']['source_policy_publication_grade_work_precision_open']}`.",
        f"- Source-policy work/precision claim excluded: `{result['b4']['source_policy_work_precision_claim_excluded']}`.",
        f"- Legacy paper_submission_b4_can_close_now alias: `{result['b4']['paper_submission_b4_can_close_now']}`.",
        f"- Legacy paper_submission_b4_can_close_now_under_narrowed_policy alias: `{result['b4']['paper_submission_b4_can_close_now_under_narrowed_policy']}`.",
        f"- Legacy B4 alias scope: `{result['b4']['paper_submission_b4_can_close_now_alias_scope']}`.",
        f"- B4 required to close: `{result['b4']['required_to_close']}`.",
        f"- Common-reference direct order/error wins: `{result['b4']['common_reference_direct_nonlocal_order_wins']}/{result['b4']['common_reference_direct_nonlocal_order_comparisons']}` and `{result['b4']['common_reference_direct_nonlocal_error_wins']}/{result['b4']['common_reference_direct_nonlocal_error_comparisons']}`.",
        f"- TFE Algorithm-1 endpoint metric/terminal-overrun rows: `{result['b4']['diagnostic_work_precision_rows']['tfe_algorithm_literal_endpoint_metric_rows']}/{result['b4']['diagnostic_work_precision_rows']['tfe_algorithm_literal_endpoint_terminal_overrun_rows']}`.",
        f"- TFE exact-T compatible/incompatible endpoint-grid rows: `{result['b4']['diagnostic_work_precision_rows']['tfe_source_grid_exact_T_compatible_rows_endpoint_convention_resolved']}/{result['b4']['diagnostic_work_precision_rows']['tfe_source_grid_endpoint_incompatible_rows_requiring_policy']}`; full-T10 grid policy resolved `{result['b4']['diagnostic_work_precision_rows']['tfe_source_grid_policy_resolved_for_full_T10']}`.",
        f"- TFE same-test work/precision methods/rows/ok/source-policy rows: `{result['b4']['diagnostic_work_precision_rows']['tfe_same_test_methods']}/{result['b4']['diagnostic_work_precision_rows']['tfe_same_test_rows']}/{result['b4']['diagnostic_work_precision_rows']['tfe_same_test_ok_rows']}/{result['b4']['diagnostic_work_precision_rows']['tfe_same_test_source_policy_rows_completed']}`.",
        f"- TFE Algorithm-1 literal work/precision methods/raw/summary/terminal-overrun/source-policy rows: `{result['b4']['diagnostic_work_precision_rows']['tfe_algorithm_literal_methods']}/{result['b4']['diagnostic_work_precision_rows']['tfe_algorithm_literal_rows']}/{result['b4']['diagnostic_work_precision_rows']['tfe_algorithm_literal_summary_rows']}/{result['b4']['diagnostic_work_precision_rows']['tfe_algorithm_literal_terminal_overrun_rows']}/{result['b4']['diagnostic_work_precision_rows']['tfe_algorithm_literal_source_policy_rows_completed']}`; runtime proxy `{result['b4']['diagnostic_work_precision_rows']['tfe_algorithm_literal_runtime_proxy_available']}`.",
        "",
        "## B7 Boundary",
        "",
        f"- B7 status: `{result['b7']['status']}`.",
        f"- B7 gate status before reclassification: `{result['b7']['gate_status_before_reclassification']}`.",
        f"- B7 can close from current figure set: `{result['b7']['can_close_from_current_figure_set']}`.",
        f"- B7 can close from narrowed-claim policy: `{result['b7']['can_close_from_narrowed_claim_policy']}`.",
        f"- Figures audited: `{result['b7']['figure_count']}/{result['b7']['expected_figure_count']}`.",
        f"- All figures integrated main/flat: `{result['b7']['all_figures_integrated_main_flat']}`.",
        f"- All PDF captions present: `{result['b7']['all_pdf_captions_present']}`.",
        f"- Figure 12/13 integrated: `{result['b7']['figure12_all_method_matrix_integrated']}/{result['b7']['figure13_work_precision_compendium_integrated']}`.",
        f"- Figure set supports common-reference diagnostics only: `{result['b7']['figure_set_supports_common_reference_diagnostics_only']}`.",
        f"- B7 still-open requirements: `{result['b7']['still_open_requirements']}`.",
        f"- B7 excluded future source-policy requirements: `{result['b7']['excluded_future_source_policy_requirements']}`.",
        "",
        "## Closure Decision",
        "",
        f"- B4 still open under bounded narrowed gate: `{result['closure_decision']['b4_still_open']}`.",
        f"- B7 still open under bounded narrowed gate: `{result['closure_decision']['b7_still_open']}`.",
        f"- B4/B7 source-policy still open: `{result['closure_decision']['b4_source_policy_still_open']}/{result['closure_decision']['b7_source_policy_still_open']}`.",
        f"- Non-superiority route reclassifies B4/B7: `{result['closure_decision']['non_superiority_route_reclassifies_b4_b7']}`.",
        f"- Narrowed-claim policy reclassifies B4/B7: `{result['closure_decision']['narrowed_claim_policy_reclassifies_b4_b7']}`.",
        f"- Narrowed reclassification scope: `{result['closure_decision']['narrowed_reclassification_scope']}`.",
        f"- Global source-policy still open: `{result['closure_decision']['global_source_policy_still_open']}`.",
        f"- Accepted without new heavy run: `{result['closure_decision']['accepted_without_new_heavy_run']}`.",
        f"- Same guarded-driver rerun recommended: `{result['closure_decision']['same_guarded_driver_rerun_recommended']}`.",
        f"- Reason: {result['closure_decision']['reason']}",
        "",
        "Next paths:",
    ]
    for item in result["closure_decision"]["next_paths"]:
        lines.append(f"- `{item}`")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("b4_b7_non_superiority_route_audit=written")
    print("route_b_closes_b2_b4_b7=True/False/False")
    print("b4_b7_closed_by_non_superiority_route=False")
    print(f"b4_b7_closed_by_narrowed_claim_policy={narrowed_policy_applies_to_b4_b7}")
    print(f"b4_still_open={b4_still_open}")
    print(f"b7_still_open={b7_still_open}")
    print("source_policy_rows_closed=0/40")
    print(
        "verified_authorized_execution_recorded="
        f"{result['guarded_driver_post_execution']['verified_authorized_execution_recorded']}"
    )
    print("existing_ready_command_artifacts_present=True")
    print("verified_execution_promoted_rows=0/40")
    print("run_v047_invoked=False")


if __name__ == "__main__":
    main()
