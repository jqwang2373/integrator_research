#!/usr/bin/env python3
"""Validate the B4/B7 non-superiority route audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "B4_B7_NON_SUPERIORITY_ROUTE_AUDIT.json"
AUDIT_MD = PAPER / "B4_B7_NON_SUPERIORITY_ROUTE_AUDIT.md"


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def blocker_by_id(gate: dict[str, Any], blocker_id: str) -> dict[str, Any]:
    for item in gate.get("blockers", []):
        if isinstance(item, dict) and item.get("id") == blocker_id:
            return item
    return {}


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(AUDIT_JSON)
        audit_md = read_text(AUDIT_MD)
        blocker_gate = read_json(PAPER / "CMAME_BLOCKER_CLOSURE_GATE.json")
        claim_demotion = read_json(PAPER / "EXTERNAL_SUPERIORITY_CLAIM_DEMOTION_AUDIT.json")
        figure_set = read_json(PAPER / "CMAME_FIGURE_SET_AUDIT.json")
        b2_remaining = read_json(PAPER / "B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.json")
        pdf_style = read_json(PAPER / "CMAME_PDF_STYLE_REVIEW_AUDIT.json")
        comparison = read_json(PAPER / "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.json")
        b4_post_execution = read_json(PAPER / "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.json")
        narrowed_policy = read_json(PAPER / "CMAME_NARROWED_CLAIM_CLOSURE_POLICY_AUDIT.json")
    except Exception as exc:  # noqa: BLE001
        print(f"B4/B7 non-superiority route audit validation: FAIL\n- {exc}")
        return 1

    b4 = blocker_by_id(blocker_gate, "B4")
    b7 = blocker_by_id(blocker_gate, "B7")
    b4_audit = audit.get("b4", {})
    b7_audit = audit.get("b7", {})
    claim_scope = audit.get("claim_scope", {})
    closure = audit.get("closure_decision", {})
    execution = audit.get("execution_policy", {})
    pdf_boundary = audit.get("pdf_style_review_boundary", {})
    guarded_post = audit.get("guarded_driver_post_execution", {})
    narrowed = audit.get("narrowed_claim_policy_audit", {})
    authorized = b4_post_execution.get("verified_authorized_execution_recorded") is True
    expected_scope = (
        "verified_authorized_guarded_driver_execution"
        if authorized
        else "no_verified_current_authorized_execution_record_existing_artifacts_only"
    )

    checks.check(audit.get("schema") == "b4-b7-non-superiority-route-audit-v1", "schema changed")
    checks.check(
        audit.get("status") == "narrowed_claim_policy_closes_b4_b7_no_source_policy_superiority",
        "status changed",
    )
    checks.check(
        audit.get("closure_scope")
        == "bounded_narrowed_claim_subcheck_only_global_submission_and_source_policy_open",
        "closure scope changed",
    )
    checks.check(audit.get("submission_ready") is False, "audit must not mark submission ready")
    checks.check(audit.get("global_submission_ready") is False, "audit must keep global submission open")
    checks.check(audit.get("submission_standard_met") is False, "submission standard overclosed")
    checks.check(audit.get("route") == "non_superiority_claim_boundary", "route changed")
    checks.check(audit.get("route_b_claim_demotion_available") is True, "Route B should be available")
    checks.check(audit.get("route_b_closes_b2") is True, "Route B B2 marker changed")
    checks.check(audit.get("route_b_closes_b4") is False, "Route B must not close B4")
    checks.check(audit.get("route_b_closes_b7") is False, "Route B must not close B7")
    checks.check(audit.get("route_b_does_not_close_b4") is True, "Route B/B4 boundary missing")
    checks.check(audit.get("route_b_does_not_close_b7") is True, "Route B/B7 boundary missing")
    checks.check(
        audit.get("b4_b7_closed_by_non_superiority_route") is False,
        "B4/B7 incorrectly closed by non-superiority route",
    )
    checks.check(
        audit.get("narrowed_claim_policy_applied_to_b4_b7") is True,
        "narrowed policy was not applied to B4/B7",
    )
    checks.check(audit.get("narrowed_claim_policy_closes_b4") is True, "narrowed policy did not close B4")
    checks.check(audit.get("narrowed_claim_policy_closes_b7") is True, "narrowed policy did not close B7")
    checks.check(
        audit.get("b4_b7_closed_by_narrowed_claim_policy") is True,
        "B4/B7 not closed by narrowed claim policy",
    )
    checks.check(
        audit.get("narrowed_closure_is_global_submission_ready") is False
        and audit.get("narrowed_closure_is_source_policy_closure") is False,
        "narrowed closure overclaims global/source-policy closure",
    )
    global_source = audit.get("global_source_policy_closure", {})
    checks.check(
        global_source.get("source_policy_rows_closed") == 0
        and global_source.get("source_policy_rows_total") == 40
        and global_source.get("external_superiority_ready_rows") == 0
        and global_source.get("external_superiority_claim_allowed") is False
        and global_source.get("submission_ready") is False,
        "global source-policy closure boundary changed",
    )
    checks.check(
        "bounded narrowed-claim subcheck aliases only" in audit.get("compatibility_alias_warning", "")
        and "do not close global submission readiness" in audit.get("compatibility_alias_warning", ""),
        "compatibility alias warning missing or too weak",
    )
    checks.check(audit.get("open_blockers_before_audit", []) == [], "open blockers before audit changed")
    checks.check(audit.get("open_blockers_after_audit", []) == [], "open blockers after audit changed")
    checks.check(
        guarded_post.get("audit_status")
        == b4_post_execution.get("status"),
        "B4 post-execution audit status not carried into B4/B7 route audit",
    )
    checks.check(
        guarded_post.get("approved_driver_execution_recorded")
        == b4_post_execution.get("approved_driver_execution_recorded")
        is authorized,
        "B4 route audit approved driver execution marker inconsistent",
    )
    checks.check(
        guarded_post.get("verified_authorized_execution_recorded")
        == b4_post_execution.get("verified_authorized_execution_recorded")
        is authorized,
        "B4 route audit verified authorized execution marker inconsistent",
    )
    checks.check(
        guarded_post.get("existing_ready_command_artifacts_present")
        == b4_post_execution.get("existing_ready_command_artifacts_present")
        is True,
        "B4 route audit lost existing artifact presence",
    )
    checks.check(
        guarded_post.get("execution_record_scope")
        == b4_post_execution.get("execution_record_scope")
        == expected_scope,
        "B4 route audit execution-record scope changed",
    )
    checks.check(
        guarded_post.get("all_expected_outputs_exist_now")
        == b4_post_execution.get("command_artifact_presence", {}).get("all_expected_outputs_exist_now")
        is True,
        "B4 guarded-driver outputs not present in B4/B7 route audit",
    )
    checks.check(
        guarded_post.get("source_policy_rows_promoted_after_driver")
        == b4_post_execution.get("source_policy_rows_closed")
        == 0,
        "B4 guarded driver promoted rows unexpectedly",
    )
    checks.check(
        guarded_post.get("source_policy_rows_total")
        == b4_post_execution.get("source_policy_total_rows")
        == 40,
        "B4 guarded-driver total rows changed",
    )
    checks.check(
        guarded_post.get("b4_can_close_now")
        == b4_post_execution.get("b4_can_close_now")
        is False,
        "B4 route audit overcloses B4 after guarded driver",
    )
    checks.check(
        guarded_post.get("b7_can_close_now")
        == b4_post_execution.get("b7_can_close_now")
        is False,
        "B4 route audit overcloses B7 after guarded driver",
    )
    checks.check(
        guarded_post.get("external_superiority_claim_allowed") is False,
        "B4 route audit overclaims external superiority after guarded driver",
    )
    checks.check(
        guarded_post.get("next_required_actions") == b4_post_execution.get("next_required_actions"),
        "B4 post-execution next actions drifted in B4/B7 route audit",
    )
    checks.check(
        narrowed.get("artifact") == "CMAME_NARROWED_CLAIM_CLOSURE_POLICY_AUDIT.json",
        "narrowed-claim policy audit artifact path missing",
    )
    checks.check(
        narrowed.get("status")
        == narrowed_policy.get("status")
        == "narrowed_claim_route_applied_current_gate_reclassified",
        "narrowed-claim policy audit status changed",
    )
    checks.check(
        narrowed.get("narrowed_claim_evidence_supported")
        == narrowed_policy.get("narrowed_claim_evidence_supported")
        is True,
        "narrowed-claim evidence support missing",
    )
    checks.check(
        narrowed.get("current_gate_can_close_now")
        == narrowed_policy.get("current_gate_can_close_now")
        is True,
        "narrowed policy did not close current gate",
    )
    narrowed_feasibility = narrowed_policy.get("closure_feasibility_under_policy_change", {})
    checks.check(
        narrowed.get("b4_close_if_narrowed_policy_adopted")
        == narrowed_feasibility.get("b4_close_if_narrowed_policy_adopted")
        is True,
        "narrowed policy B4 conditional feasibility missing",
    )
    checks.check(
        narrowed.get("b7_close_if_diagnostic_figure_scope_adopted")
        == narrowed_feasibility.get("b7_close_if_diagnostic_figure_scope_adopted")
        is True,
        "narrowed policy B7 conditional feasibility missing",
    )
    checks.check(
        narrowed.get("b6_close_after_final_prose_review_refresh")
        == narrowed_feasibility.get("b6_close_after_final_prose_review_refresh")
        is True,
        "narrowed policy B6 conditional feasibility missing",
    )
    checks.check(
        narrowed.get("source_policy_row_promotion_required")
        == narrowed_feasibility.get("source_policy_row_promotion_required")
        is False,
        "narrowed policy unexpectedly requires source-policy promotion",
    )
    checks.check(
        narrowed.get("heavy_or_b4_execution_required")
        == narrowed_feasibility.get("heavy_or_b4_execution_required")
        is False,
        "narrowed policy unexpectedly requires heavy/B4 execution",
    )
    checks.check(
        narrowed.get("close_b4_b7_now")
        == narrowed_policy.get("closure_decision", {}).get("close_b4_b7_now")
        is True,
        "narrowed policy did not close B4/B7",
    )
    checks.check(
        narrowed.get("close_b6_now")
        == narrowed_policy.get("closure_decision", {}).get("close_b6_now")
        is True,
        "narrowed policy did not close B6",
    )
    checks.check(narrowed.get("policy_applied_in_this_audit") is True, "narrowed policy was not applied in this route audit")

    checks.check(b4_audit.get("gate_status_before_reclassification") == b4.get("status") == "closed", "B4 gate status changed")
    checks.check(b4_audit.get("status") == "closed_under_narrowed_claim_policy", "B4 narrowed-policy status changed")
    checks.check(b4_audit.get("can_close_from_non_superiority_route") is False, "B4 non-superiority closure changed")
    checks.check(b4_audit.get("can_close_from_narrowed_claim_policy") is True, "B4 narrowed-policy closure missing")
    checks.check(
        b4_audit.get("common_reference_order_error_matrix_closed")
        == b4.get("common_reference_order_error_matrix_closed")
        is True,
        "B4 common-reference closure marker changed",
    )
    checks.check(
        b4_audit.get("source_policy_publication_grade_work_precision_open")
        == b4.get("source_policy_publication_grade_work_precision_open")
        is True,
        "B4 source-policy work/precision boundary changed",
    )
    checks.check(
        b4_audit.get("source_policy_work_precision_claim_excluded") is True,
        "B4 source-policy work/precision claim was not excluded",
    )
    checks.check(
        b4_audit.get("paper_submission_b4_can_close_now")
        == b4.get("paper_submission_b4_can_close_now")
        is True,
        "B4 submission closure marker changed",
    )
    checks.check(
        b4_audit.get("paper_submission_b4_can_close_now_under_narrowed_policy") is True,
        "B4 narrowed-policy submission closure marker missing",
    )
    checks.check(
        b4_audit.get("paper_submission_b4_can_close_now_alias_scope")
        == "legacy_bounded_narrowed_claim_subcheck_alias_not_global_submission_ready",
        "B4 legacy alias scope missing",
    )
    checks.check(
        b4_audit.get("required_to_close", []) == [],
        "B4 requirements changed",
    )
    checks.check(
        b4_audit.get("requirements_excluded_from_current_claim", []) == [],
        "B4 excluded current-claim requirements changed",
    )
    checks.check(
        b4_audit.get("source_policy_execution_rows_closed")
        == claim_demotion.get("source_policy_execution_rows_closed")
        == 0,
        "B4 source-policy rows overclosed",
    )
    checks.check(
        b4_audit.get("source_policy_execution_total_rows")
        == claim_demotion.get("source_policy_execution_total_rows")
        == 40,
        "B4 source-policy total rows changed",
    )
    checks.check(b4_audit.get("external_superiority_ready_rows") == 0, "B4 external-superiority rows changed")
    checks.check(
        b4_audit.get("common_reference_direct_nonlocal_order_wins")
        == comparison.get("direct_nonlocal_velocity_order_wins")
        == 40,
        "B4 common-reference order wins changed",
    )
    checks.check(
        b4_audit.get("common_reference_direct_nonlocal_error_wins")
        == comparison.get("direct_nonlocal_finest_velocity_error_wins")
        == 40,
        "B4 common-reference error wins changed",
    )
    diagnostic = b4_audit.get("diagnostic_work_precision_rows", {})
    checks.check(
        diagnostic.get("tfe_algorithm_literal_endpoint_metric_rows") == 12,
        "TFE Algorithm-1 endpoint metric row count changed",
    )
    checks.check(
        diagnostic.get("tfe_algorithm_literal_endpoint_terminal_overrun_rows") == 12,
        "TFE Algorithm-1 endpoint terminal-overrun row count changed",
    )
    checks.check(
        diagnostic.get("tfe_algorithm_literal_endpoint_exact_T_error_sampling_equivalent") is False,
        "TFE Algorithm-1 endpoint exact-T equivalence overclaimed",
    )
    checks.check(
        diagnostic.get("tfe_source_grid_exact_T_compatible_rows_endpoint_convention_resolved") == 2,
        "TFE source-grid exact-T compatible row count changed",
    )
    checks.check(
        diagnostic.get("tfe_source_grid_endpoint_incompatible_rows_requiring_policy") == 4,
        "TFE source-grid incompatible row count changed",
    )
    checks.check(
        diagnostic.get("tfe_source_grid_policy_resolved_for_full_T10") is False,
        "TFE full-T10 grid policy overclosed",
    )
    checks.check(diagnostic.get("tfe_same_test_methods") == 6, "TFE same-test method count changed")
    checks.check(diagnostic.get("tfe_same_test_rows") == 18, "TFE same-test diagnostic row count changed")
    checks.check(diagnostic.get("tfe_same_test_ok_rows") == 18, "TFE same-test ok row count changed")
    checks.check(diagnostic.get("tfe_same_test_figure_available") is True, "TFE same-test figure missing")
    checks.check(diagnostic.get("tfe_same_test_source_policy_rows_completed") == 0, "TFE same-test diagnostic overclosed")
    checks.check(diagnostic.get("tfe_algorithm_literal_methods") == 4, "TFE algorithm-literal method count changed")
    checks.check(diagnostic.get("tfe_algorithm_literal_rows") == 12, "TFE algorithm-literal row count changed")
    checks.check(diagnostic.get("tfe_algorithm_literal_summary_rows") == 4, "TFE algorithm-literal summary count changed")
    checks.check(
        diagnostic.get("tfe_algorithm_literal_terminal_overrun_rows") == 12,
        "TFE algorithm-literal terminal-overrun row count changed",
    )
    checks.check(
        diagnostic.get("tfe_algorithm_literal_runtime_proxy_available") is False,
        "TFE algorithm-literal diagnostic overclaims runtime proxy",
    )
    checks.check(
        diagnostic.get("tfe_algorithm_literal_source_policy_rows_completed") == 0,
        "TFE algorithm-literal diagnostic overclosed",
    )

    checks.check(b7_audit.get("gate_status_before_reclassification") == b7.get("status") == "closed", "B7 gate status changed")
    checks.check(b7_audit.get("status") == "closed_under_narrowed_claim_policy", "B7 narrowed-policy status changed")
    checks.check(b7_audit.get("can_close_from_current_figure_set") is True, "B7 current figure set did not close")
    checks.check(b7_audit.get("can_close_from_narrowed_claim_policy") is True, "B7 narrowed-policy closure missing")
    checks.check(b7_audit.get("figure_count") == b7_audit.get("expected_figure_count") == 13, "B7 figure count changed")
    checks.check(b7_audit.get("all_figures_available") is True, "B7 figure availability changed")
    checks.check(b7_audit.get("all_figures_integrated_main_flat") is True, "B7 integration changed")
    checks.check(b7_audit.get("all_pdf_captions_present") is True, "B7 caption coverage changed")
    checks.check(b7_audit.get("figure12_all_method_matrix_integrated") is True, "B7 Figure 12 changed")
    checks.check(b7_audit.get("figure13_work_precision_compendium_integrated") is True, "B7 Figure 13 changed")
    checks.check(
        b7_audit.get("b7_closed_by_figure_set_audit") == figure_set.get("b7_closed") is True,
        "B7 figure-set audit did not close",
    )
    checks.check(
        b7_audit.get("figure_set_supports_common_reference_diagnostics_only") is True,
        "B7 diagnostic-only boundary missing",
    )
    checks.check(
        b7_audit.get("still_open_requirements", []) == [],
        "B7 still-open requirements should be empty under narrowed scope",
    )
    checks.check(
        set(b7_audit.get("excluded_future_source_policy_requirements", []))
        == {
            "full_source_policy_baseline_comparison_figures",
            "complete_work_precision_curves_for_external_source_suites",
        },
        "B7 excluded future source-policy requirements changed",
    )

    checks.check(pdf_boundary.get("decision") == pdf_style.get("decision") == "submit_under_narrowed_claim", "PDF decision changed")
    checks.check(pdf_boundary.get("submission_standard_met") is True, "PDF standard did not close")
    checks.check(pdf_boundary.get("quality_review_passed") is True, "PDF quality review did not close")
    checks.check(pdf_boundary.get("figure_set_b7_closed") is True, "PDF B7 boundary did not close")
    checks.check(pdf_boundary.get("external_superiority_claim_allowed") is False, "PDF external superiority overclaimed")
    checks.check(pdf_boundary.get("blocking_finding_ids", []) == [], "PDF blocking findings changed")

    checks.check(claim_scope.get("source_policy_rows_closed") == b2_remaining.get("source_policy_closed_rows") == 0, "claim scope rows changed")
    checks.check(claim_scope.get("external_superiority_ready_rows") == 0, "claim scope external rows changed")
    checks.check(claim_scope.get("remaining_active_suites") == [], "claim scope active suites changed")
    checks.check(claim_scope.get("external_superiority_claim_allowed") is False, "claim scope superiority overclaimed")
    checks.check("formal_order_claim" in claim_scope.get("allowed_current_claims", []), "formal-order claim missing")
    checks.check("common_reference_diagnostics" in claim_scope.get("allowed_current_claims", []), "common-reference claim missing")
    checks.check("source_policy_external_superiority" in claim_scope.get("forbidden_current_claims", []), "forbidden superiority claim missing")

    checks.check(closure.get("b4_still_open") is False, "closure decision changed for B4")
    checks.check(closure.get("b7_still_open") is False, "closure decision changed for B7")
    checks.check(
        closure.get("b4_still_open_scope") == "bounded_narrowed_claim_subcheck"
        and closure.get("b7_still_open_scope") == "bounded_narrowed_claim_subcheck",
        "B4/B7 narrowed-gate scope changed",
    )
    checks.check(
        closure.get("b4_source_policy_still_open") is True
        and closure.get("b7_source_policy_still_open") is True,
        "B4/B7 source-policy boundary overclosed",
    )
    checks.check(
        closure.get("non_superiority_route_reclassifies_b4_b7") is False,
        "closure decision incorrectly reclassifies B4/B7",
    )
    checks.check(
        closure.get("narrowed_claim_policy_reclassifies_b4_b7") is True,
        "closure decision did not record narrowed reclassification",
    )
    checks.check(
        closure.get("narrowed_reclassification_scope")
        == "bounded_narrowed_claim_subcheck_only_not_global_source_policy",
        "narrowed reclassification scope changed",
    )
    checks.check(closure.get("global_source_policy_still_open") is True, "global source-policy boundary changed")
    checks.check(closure.get("accepted_without_new_heavy_run") is True, "closure should not require new heavy run")
    checks.check(
        "excluding source-policy work/precision" in closure.get("reason", ""),
        "closure reason missing narrowed work/precision exclusion",
    )
    checks.check(
        "formal-order plus common-reference diagnostic evidence" in closure.get("reason", ""),
        "closure reason missing narrowed evidence basis",
    )
    checks.check(
        closure.get("same_guarded_driver_rerun_recommended") is False,
        "route audit should not recommend rerunning the same guarded driver",
    )
    checks.check(
        "refresh_b6_final_prose_under_narrowed_claim_scope"
        in closure.get("next_paths", []),
        "B6 refresh path missing",
    )
    checks.check(
        "refresh_pdf_style_review_against_narrowed_claim_boundary"
        in closure.get("next_paths", []),
        "PDF refresh path missing",
    )
    checks.check(
        "retain_source_policy_work_precision_as_future_reintroduction_not_current_claim"
        in closure.get("next_paths", []),
        "future source-policy retention path missing",
    )
    checks.check(execution.get("read_only_existing_artifacts") is True, "audit should be read-only")
    checks.check(execution.get("default_1e_4_required") is False, "audit should not require default 1e-4")
    checks.check(execution.get("heavy_numerical_run_invoked") is False, "audit should not invoke heavy run")
    checks.check(execution.get("run_v047_invoked") is False, "audit should not invoke run_v047")

    for token in [
        "bounded narrowed-claim subcheck closes B4/B7; global source-policy remains open",
        "Closure scope: `bounded_narrowed_claim_subcheck_only_global_submission_and_source_policy_open`.",
        "Global submission ready: `False`.",
        "Route B closes B2/B4/B7: `True/False/False`.",
        "B4/B7 closed by non-superiority route: `False`.",
        "B4/B7 closed by narrowed-claim policy, bounded subcheck only: `True`.",
        "Narrowed closure is global submission/source-policy closure: `False/False`.",
        "Open blockers before audit: `[]`.",
        "Open blockers after audit: `[]`.",
        "Global source-policy rows closed: `0/40`.",
        "Global external-superiority ready/allowed: `0/False`.",
        f"Verified authorized B4 execution/output-present/promoted rows: `{authorized}` / `True` / `0/40`.",
        f"B4 execution record scope: `{expected_scope}`.",
        "B4/B7 can close after guarded driver: `False/False`.",
        "Narrowed-claim evidence supported/current gate can close: `True/True`.",
        "Narrowed-policy conditional B4/B7/B6 feasibility: `True/True/True`.",
        "Narrowed-policy source-policy promotion/heavy execution required: `False/False`.",
        "Narrowed-policy closes B4/B7/B6 now: `True/True`.",
        "Narrowed-policy applied in this audit: `True`.",
        "B4 can close from non-superiority route: `False`.",
        "B4 can close from narrowed-claim policy: `True`.",
        "Source-policy publication-grade work/precision open: `True`.",
        "Source-policy work/precision claim excluded: `True`.",
        "Legacy paper_submission_b4_can_close_now alias: `True`.",
        "Legacy paper_submission_b4_can_close_now_under_narrowed_policy alias: `True`.",
        "Legacy B4 alias scope: `legacy_bounded_narrowed_claim_subcheck_alias_not_global_submission_ready`.",
        "TFE Algorithm-1 endpoint metric/terminal-overrun rows: `12/12`.",
        "TFE exact-T compatible/incompatible endpoint-grid rows: `2/4`; full-T10 grid policy resolved `False`.",
        "TFE same-test work/precision methods/rows/ok/source-policy rows: `6/18/18/0`.",
        "TFE Algorithm-1 literal work/precision methods/raw/summary/terminal-overrun/source-policy rows: `4/12/4/12/0`; runtime proxy `False`.",
        "B7 can close from current figure set: `True`.",
        "B7 can close from narrowed-claim policy: `True`.",
        "Figures audited: `13/13`.",
        "Figure set supports common-reference diagnostics only: `True`.",
        "B7 still-open requirements: `[]`.",
        "B4 still open under bounded narrowed gate: `False`.",
        "B7 still open under bounded narrowed gate: `False`.",
        "B4/B7 source-policy still open: `True/True`.",
        "Non-superiority route reclassifies B4/B7: `False`.",
        "Narrowed-claim policy reclassifies B4/B7: `True`.",
        "Narrowed reclassification scope: `bounded_narrowed_claim_subcheck_only_not_global_source_policy`.",
        "Global source-policy still open: `True`.",
        "Accepted without new heavy run: `True`.",
        "Same guarded-driver rerun recommended: `False`.",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("B4/B7 non-superiority route audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("B4/B7 non-superiority route audit validation: PASS")
    print("route_b_closes_b2_b4_b7=True/False/False")
    print("b4_b7_closed_by_non_superiority_route=False")
    print("b4_b7_closed_by_narrowed_claim_policy=True")
    print("b4_still_open=False")
    print("b7_still_open=False")
    print("source_policy_rows_closed=0/40")
    print(f"verified_authorized_execution_recorded={authorized}")
    print("existing_ready_command_artifacts_present=True")
    print("verified_execution_promoted_rows=0/40")
    print("run_v047_invoked=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
