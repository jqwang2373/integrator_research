#!/usr/bin/env python3
"""Validate the CMAME figure-set audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "CMAME_FIGURE_SET_AUDIT.json"
AUDIT_MD = PAPER / "CMAME_FIGURE_SET_AUDIT.md"
B4_PLAN = PAPER / "B4_SOURCE_POLICY_WORK_PRECISION_EXECUTION_PLAN.json"
OPT_IN_PACKET = PAPER / "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json"
NARROWED_POLICY = PAPER / "CMAME_NARROWED_CLAIM_CLOSURE_POLICY_AUDIT.json"


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


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(AUDIT_JSON)
        audit_md = read_text(AUDIT_MD)
        b4_plan = read_json(B4_PLAN)
        opt_in_packet = read_json(OPT_IN_PACKET)
        narrowed_policy = read_json(NARROWED_POLICY)
    except Exception as exc:  # noqa: BLE001
        print(f"cmame figure-set audit validation: FAIL\n- {exc}")
        return 1

    figures = audit.get("figures", [])
    b4_summary = b4_plan.get("execution_lane_summary", {})
    preflight = audit.get("b7_closure_readiness_preflight", {})
    post_b4_plan = audit.get("post_b4_figure_scope_plan", {})
    ready_boundary = post_b4_plan.get("ready_command_coverage_boundary", {})
    checks.check(audit.get("schema") == "cmame-figure-set-audit-v1", "audit schema changed")
    checks.check(
        audit.get("status") == "b7_figure_set_closed_narrowed_common_reference_diagnostic_scope",
        "audit status changed",
    )
    checks.check(audit.get("blocker") == "B7", "audit blocker changed")
    checks.check(audit.get("submission_ready") is False, "figure audit must not claim submission ready")
    checks.check(audit.get("b7_closed") is True, "B7 must close under narrowed diagnostic figure scope")
    checks.check(
        audit.get("source_policy_rows_closed")
        == b4_summary.get("source_policy_rows_closed_after_plan")
        == 0,
        "figure audit source-policy row closure changed",
    )
    checks.check(
        audit.get("source_policy_rows_total")
        == b4_summary.get("source_policy_rows_total")
        == 40,
        "figure audit source-policy total changed",
    )
    checks.check(audit.get("figure_count") == audit.get("expected_figure_count") == 13, "figure count changed")
    checks.check(audit.get("all_figures_available") is True, "not all figures are available")
    checks.check(audit.get("all_figures_integrated_main_flat") is True, "not all figures are integrated in TeX")
    checks.check(audit.get("all_pdf_captions_present") is True, "not all figure captions are present in PDF text")
    checks.check(audit.get("all_legible_dimensions") is True, "figure dimensions below minimum")
    checks.check(audit.get("figure12_all_method_matrix_integrated") is True, "Figure 12 all-method matrix not integrated")
    checks.check(audit.get("figure13_work_precision_compendium_integrated") is True, "Figure 13 work/precision compendium not integrated")
    checks.check(len(figures) == 13, "figure row count changed")
    numbers = {row.get("number") for row in figures if isinstance(row, dict)}
    checks.check(numbers == set(range(1, 14)), "figure numbers changed")
    figure12 = next((row for row in figures if isinstance(row, dict) and row.get("number") == 12), {})
    checks.check(figure12.get("role") == "all-method all-example result matrix", "Figure 12 role changed")
    checks.check(figure12.get("main_tex_includes") is True, "Figure 12 main TeX include missing")
    checks.check(figure12.get("flat_tex_includes") is True, "Figure 12 flat TeX include missing")
    checks.check(figure12.get("main_pdf_caption_present") is True, "Figure 12 main PDF caption missing")
    checks.check(figure12.get("flat_pdf_caption_present") is True, "Figure 12 flat PDF caption missing")
    figure13 = next((row for row in figures if isinstance(row, dict) and row.get("number") == 13), {})
    checks.check(figure13.get("role") == "work/precision compendium", "Figure 13 role changed")
    checks.check(figure13.get("main_tex_includes") is True, "Figure 13 main TeX include missing")
    checks.check(figure13.get("flat_tex_includes") is True, "Figure 13 flat TeX include missing")
    checks.check(figure13.get("main_pdf_caption_present") is True, "Figure 13 main PDF caption missing")
    checks.check(figure13.get("flat_pdf_caption_present") is True, "Figure 13 flat PDF caption missing")
    claim_boundary = audit.get("claim_boundary", {})
    checks.check(claim_boundary.get("external_superiority_claim_allowed") is False, "figure audit overclaims external superiority")
    checks.check(claim_boundary.get("figure_set_supports_common_reference_diagnostics_only") is True, "diagnostic boundary missing")
    checks.check(
        claim_boundary.get("source_policy_work_precision_claim_excluded") is True,
        "figure audit did not exclude source-policy work/precision claims",
    )
    checks.check(claim_boundary.get("source_policy_rows_promoted") == 0, "figure audit overpromoted source-policy rows")
    checks.check(claim_boundary.get("source_policy_rows_total") == 40, "figure audit source-policy total changed")
    checks.check(
        claim_boundary.get("current_figure_scope") == "narrowed_common_reference_diagnostic_publication_scope",
        "figure audit current scope changed",
    )
    checks.check(claim_boundary.get("default_1e-4_required") is False, "figure audit incorrectly requires default 1e-4")
    checks.check(claim_boundary.get("heavy_numerical_run_invoked") is False, "figure audit invoked heavy numerical run")
    checks.check(claim_boundary.get("run_v047_invoked") is False, "figure audit invoked run_v047")
    checks.check(
        preflight.get("schema") == "cmame-b7-closure-readiness-preflight-v1",
        "B7 closure-readiness preflight schema changed",
    )
    checks.check(
        preflight.get("status") == "b7_narrowed_diagnostic_common_reference_figure_scope_closed",
        "B7 closure-readiness preflight status changed",
    )
    checks.check(preflight.get("closed_precondition_count") == 13, "B7 closed precondition count changed")
    checks.check(preflight.get("open_dependency_count") == 0, "B7 open dependency count changed")
    checks.check(preflight.get("source_policy_rows_closed") == 0, "B7 preflight overclosed source-policy rows")
    checks.check(preflight.get("source_policy_rows_total") == 40, "B7 preflight source-policy total changed")
    checks.check(preflight.get("source_policy_rows_ready_for_b7") is False, "B7 preflight overclaims source-policy readiness")
    checks.check(
        preflight.get("source_policy_rows_required_for_current_b7") is False,
        "B7 preflight requires source-policy rows for current scope",
    )
    checks.check(
        preflight.get("narrowed_claim_policy_evidence_supported")
        == narrowed_policy.get("narrowed_claim_evidence_supported")
        is True,
        "B7 preflight lost narrowed-policy evidence support",
    )
    checks.check(preflight.get("b7_closure_allowed_now") is True, "B7 preflight must allow closure")
    checks.check(preflight.get("heavy_numerical_run_invoked") is False, "B7 preflight invoked heavy run")
    checks.check(preflight.get("run_v047_invoked") is False, "B7 preflight invoked run_v047")
    checks.check(preflight.get("default_1e-4_required") is False, "B7 preflight requires default 1e-4")
    expected_preconditions = {
        "figure_inventory_complete",
        "main_flat_figure_files_available",
        "main_flat_tex_integration_present",
        "main_flat_pdf_captions_present",
        "legible_figure_dimensions_present",
        "limitation_explanation_figure_integrated",
        "coarse_baseline_work_precision_figure_integrated",
        "all_method_result_matrix_integrated",
        "work_precision_compendium_integrated",
        "read_only_no_heavy_no_default_1e4_policy_recorded",
        "narrowed_claim_policy_evidence_supported",
        "source_policy_work_precision_claim_excluded_from_current_b7_scope",
        "external_superiority_claim_forbidden_in_current_figure_scope",
    }
    precondition_rows = preflight.get("closed_preconditions", [])
    checks.check(
        {item.get("id") for item in precondition_rows} == expected_preconditions,
        "B7 closure-readiness precondition ids changed",
    )
    checks.check(
        all(item.get("status") is True for item in precondition_rows),
        "B7 closure-readiness precondition unexpectedly open",
    )
    dependency_rows = preflight.get("open_dependencies", [])
    checks.check(dependency_rows == [], "B7 closure-readiness should have no current-scope open dependencies")
    future_dependencies = preflight.get("future_source_policy_reintroduction_dependencies", [])
    checks.check(
        {item.get("id") for item in future_dependencies}
        == {
            "b4_source_policy_work_precision_rows_closed",
            "full_source_policy_baseline_comparison_figures",
            "clean_source_policy_work_precision_figures",
        },
        "B7 future source-policy dependency ids changed",
    )
    checks.check(
        all(item.get("status") == "excluded_from_current_scope" for item in future_dependencies),
        "B7 future source-policy dependency status changed",
    )
    for action in [
        "keep source-policy work/precision rows excluded from the current publication claim",
        "recheck figure captions against the narrowed accepted claim boundary",
        "refresh PDF-style review, blocker gate, review agent, and submission bundle after any figure-scope edit",
    ]:
        checks.check(action in preflight.get("post_close_actions", []), f"B7 preflight missing action: {action}")
    checks.check(
        audit.get("still_open_requirements", []) == [],
        "B7 open requirements changed",
    )
    checks.check(
        set(audit.get("excluded_future_source_policy_requirements", []))
        == {
            "full_source_policy_baseline_comparison_figures",
            "complete_work_precision_curves_for_external_source_suites",
        },
        "B7 excluded future source-policy requirements changed",
    )
    checks.check(
        post_b4_plan.get("schema") == "cmame-b7-post-b4-figure-scope-plan-v1",
        "post-B4 figure scope plan schema changed",
    )
    checks.check(
        post_b4_plan.get("status") == "post_b4_source_policy_reintroduction_plan_ready_current_b7_closed",
        "post-B4 figure scope plan status changed",
    )
    checks.check(
        post_b4_plan.get("source_policy_rows_closed_now") == audit.get("source_policy_rows_closed") == 0,
        "post-B4 figure plan source-policy closed rows changed",
    )
    checks.check(
        post_b4_plan.get("source_policy_rows_required_before_rebuild")
        == audit.get("source_policy_rows_total")
        == 40,
        "post-B4 figure plan source-policy total rows changed",
    )
    checks.check(
        post_b4_plan.get("b7_closure_allowed_by_this_plan_now") is False,
        "post-B4 figure plan incorrectly closes B7",
    )
    checks.check(
        post_b4_plan.get("current_b7_scope_closed_without_source_policy_rebuild") is True,
        "post-B4 figure plan lost current-scope closure marker",
    )
    checks.check(
        post_b4_plan.get("no_new_figure_count_required_now") is True,
        "post-B4 figure plan unexpectedly requires a new figure count now",
    )
    checks.check(
        post_b4_plan.get("action_counts")
        == {
            "rebuild_from_promoted_source_policy_rows": 2,
            "refresh_claim_boundary_overlay_or_caption": 2,
            "retain_after_caption_recheck": 9,
        },
        "post-B4 figure plan action counts changed",
    )
    checks.check(
        post_b4_plan.get("retain_after_caption_recheck_figures") == [1, 2, 3, 4, 5, 6, 7, 10, 11],
        "post-B4 retained figure list changed",
    )
    checks.check(
        post_b4_plan.get("claim_boundary_refresh_figures_after_b4") == [8, 12],
        "post-B4 claim-refresh figure list changed",
    )
    checks.check(
        post_b4_plan.get("blocking_source_policy_rebuild_figures") == [9, 13],
        "post-B4 blocking rebuild figure list changed",
    )
    checks.check(
        post_b4_plan.get("source_policy_dependent_figure_count") == 4,
        "post-B4 source-policy dependent figure count changed",
    )
    checks.check(
        ready_boundary.get("schema") == "cmame-b7-ready-command-coverage-boundary-v1",
        "post-B4 ready-command boundary schema changed",
    )
    checks.check(
        ready_boundary.get("status") == "ready_commands_cover_half_source_policy_rows_future_source_policy_reintroduction_only",
        "post-B4 ready-command boundary status changed",
    )
    checks.check(
        ready_boundary.get("ready_command_count") == opt_in_packet.get("ready_command_count") == 13,
        "post-B4 ready-command count changed",
    )
    checks.check(
        ready_boundary.get("ready_command_mapped_external_rows")
        == opt_in_packet.get("ready_command_mapped_external_rows")
        == 20,
        "post-B4 ready-command mapped row count changed",
    )
    checks.check(
        ready_boundary.get("unaddressed_external_rows_after_ready_commands")
        == opt_in_packet.get("unaddressed_external_rows_after_ready_commands")
        == 0,
        "post-B4 unaddressed row count changed",
    )
    checks.check(
        ready_boundary.get("source_policy_rows_total") == opt_in_packet.get("source_policy_rows_total") == 40,
        "post-B4 ready-command source-policy total changed",
    )
    checks.check(
        ready_boundary.get("ready_lanes_after_explicit_opt_in")
        == ["ra2021_source_policy_work_precision", "hi2022_full_T8_work_precision"],
        "post-B4 ready lane list changed",
    )
    checks.check(
        ready_boundary.get("not_ready_lanes_after_ready_commands")
        == ["tfe_source_policy_work_precision", "vp2024_source_code_path_work_precision"],
        "post-B4 not-ready lane list changed",
    )
    checks.check(
        ready_boundary.get("not_ready_suites_after_ready_commands") == [],
        "post-B4 not-ready suite list changed",
    )
    checks.check(
        ready_boundary.get("remaining_gap_program_status")
        == opt_in_packet.get("remaining_gap_program", {}).get("status")
        == "remaining_0_rows_programmed_no_execution_invoked",
        "post-B4 remaining-gap program status changed",
    )
    checks.check(
        ready_boundary.get("remaining_gap_rows_requiring_new_runner_or_code_path") == 0,
        "post-B4 new-runner/code-path row count changed",
    )
    checks.check(
        ready_boundary.get("remaining_gap_rows_demoted_related_work_proxy_for_current_claim") == 0,
        "post-B4 demoted proxy row count changed",
    )
    checks.check(
        ready_boundary.get("ready_commands_alone_can_close_b4")
        == opt_in_packet.get("b4_can_close_after_ready_commands_only")
        is False,
        "post-B4 ready commands overclose B4",
    )
    checks.check(
        ready_boundary.get("ready_commands_alone_can_close_b7")
        == opt_in_packet.get("b7_can_close_after_ready_commands_only")
        is False,
        "post-B4 ready commands overclose B7",
    )
    checks.check(
        ready_boundary.get("execution_invoked_by_packet")
        == opt_in_packet.get("execution_invoked_by_packet")
        is False,
        "post-B4 ready-command boundary invoked execution",
    )
    post_b4_rows = post_b4_plan.get("rows", [])
    checks.check(len(post_b4_rows) == 13, "post-B4 figure-scope row count changed")
    checks.check(
        [row.get("number") for row in post_b4_rows] == list(range(1, 14)),
        "post-B4 figure-scope row order changed",
    )
    checks.check(
        {row.get("number") for row in post_b4_rows if row.get("post_b4_action") == "rebuild_from_promoted_source_policy_rows"}
        == {9, 13},
        "post-B4 rebuild figures changed",
    )
    for required in [
        "promoted source-policy row table with accepted provenance for work/precision rows",
        "same-run error/order and work metrics for every promoted source-policy figure row",
        "ready-command coverage is not enough: 20/40 rows remain without executable source-policy commands",
        "demotion labels for TFE and VP2024 rows that remain without runner/code-path closure",
        "caption/claim-boundary refresh after B4 promotion validators pass",
    ]:
        checks.check(
            required in post_b4_plan.get("required_b4_evidence_before_closure", []),
            f"post-B4 figure plan missing required evidence: {required}",
        )
    for row in figures:
        if not isinstance(row, dict):
            checks.check(False, "figure row is not an object")
            continue
        checks.check(row.get("main_exists") is True, f"main figure missing: {row.get('number')}")
        checks.check(row.get("flat_exists") is True, f"flat figure missing: {row.get('number')}")
        checks.check(row.get("main_tex_includes") is True, f"main TeX include missing: {row.get('number')}")
        checks.check(row.get("flat_tex_includes") is True, f"flat TeX include missing: {row.get('number')}")
        checks.check(row.get("main_pdf_caption_present") is True, f"main PDF caption missing: {row.get('number')}")
        checks.check(row.get("flat_pdf_caption_present") is True, f"flat PDF caption missing: {row.get('number')}")
        checks.check(row.get("meets_minimum_pixel_area") is True, f"figure too small: {row.get('number')}")

    for token in [
        "B7 CLOSED - NARROWED COMMON-REFERENCE DIAGNOSTIC FIGURE SCOPE",
        "Figures audited: `13/13`",
        "Figure 12 all-method matrix integrated: `True`",
        "Figure 13 work/precision compendium integrated: `True`",
        "Source-policy rows closed/total: `0/40`",
        "B7 closed: `True`",
        "Source-policy work/precision claim excluded: `True`.",
        "source-policy baseline comparison figures and complete external-suite work/precision curves are excluded",
        "did not invoke `run_v047.py`",
        "## B7 Closure-Readiness Preflight",
        "Status: `b7_narrowed_diagnostic_common_reference_figure_scope_closed`.",
        "Closed preconditions/open dependencies: `13/0`.",
        "Source-policy rows ready for B7: `False`.",
        "Source-policy rows required for current B7: `False`.",
        "Narrowed-claim policy evidence supported: `True`.",
        "B7 closure allowed now: `True`.",
        "## Post-B4 Figure Scope Plan",
        "Status: `post_b4_source_policy_reintroduction_plan_ready_current_b7_closed`.",
        "Retain after caption recheck: `9` figures.",
        "Claim-boundary refresh after B4: `[8, 12]`.",
        "Blocking source-policy rebuild figures: `[9, 13]`.",
        "Source-policy dependent figure count: `4`.",
        "B7 closure allowed by this plan now: `False`.",
        "Current B7 scope closed without source-policy rebuild: `True`.",
        "Ready-command mapped/unaddressed rows: `20/0`.",
        "Ready commands alone close B4/B7: `False/False`.",
        "rebuild_from_promoted_source_policy_rows",
        "refresh_claim_boundary_overlay_or_caption",
        "retain_after_caption_recheck",
        "b4_source_policy_work_precision_rows_closed",
        "clean_source_policy_work_precision_figures",
    ]:
        checks.check(token in audit_md, f"audit markdown missing token: {token}")

    if checks.errors:
        print("cmame figure-set audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("cmame figure-set audit validation: PASS")
    print("figures=13/13")
    print("figure12_all_method_matrix_integrated=True")
    print("figure13_work_precision_compendium_integrated=True")
    print("b7_closed=True")
    return 0


if __name__ == "__main__":
    sys.exit(main())
