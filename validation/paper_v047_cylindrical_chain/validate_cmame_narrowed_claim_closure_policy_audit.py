#!/usr/bin/env python3
"""Validate the narrowed-claim closure policy audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "CMAME_NARROWED_CLAIM_CLOSURE_POLICY_AUDIT.json"
AUDIT_MD = PAPER / "CMAME_NARROWED_CLAIM_CLOSURE_POLICY_AUDIT.md"
EXPECTED_BLOCKER_OPEN_BY_ID = {"OC4": True, "OC6": True, "OC12": True}
EXPECTED_BLOCKER_CLOSURE_DECISION_BY_ID = {
    "OC4": "remain_open_ready_for_authorized_execution_not_executed_not_promoted",
    "OC6": "remain_open_no_positive_source_equivalent_artifact",
    "OC12": "remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready",
}
EXPECTED_BLOCKER_CLOSURE_ALLOWED_BY_ID = {"OC4": False, "OC6": False, "OC12": False}
EXPECTED_BLOCKER_OPEN_TOKEN = "blocker_open_by_id=OC4:True,OC6:True,OC12:True"
EXPECTED_BLOCKER_CLOSURE_DECISION_TOKEN = (
    "blocker_closure_decision_by_id="
    "OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,"
    "OC6:remain_open_no_positive_source_equivalent_artifact,"
    "OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready"
)
EXPECTED_BLOCKER_CLOSURE_ALLOWED_TOKEN = (
    "blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False"
)


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
        md = read_text(AUDIT_MD)
        gate = read_json(PAPER / "CMAME_BLOCKER_CLOSURE_GATE.json")
        b4_post = read_json(PAPER / "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.json")
        figure = read_json(PAPER / "CMAME_FIGURE_SET_AUDIT.json")
        prose = read_json(PAPER / "CMAME_PROSE_RESIDUE_AUDIT.json")
        matrix = read_json(PAPER / "PAPER_NUMERICAL_RESULT_MATRIX.json")
        traceability = read_json(PAPER / "RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.json")
        claim_demotion = read_json(PAPER / "EXTERNAL_SUPERIORITY_CLAIM_DEMOTION_AUDIT.json")
        pdf_style = read_json(PAPER / "CMAME_PDF_STYLE_REVIEW_AUDIT.json")
        objective = read_json(PAPER / "OBJECTIVE_COMPLETION_AUDIT.json")
    except Exception as exc:  # noqa: BLE001
        print(f"CMAME narrowed-claim closure policy audit validation: FAIL\n- {exc}")
        return 1

    policy = audit.get("policy_scope", {})
    evidence = audit.get("evidence_support", {})
    current = audit.get("current_contract_state", {})
    feasibility = audit.get("closure_feasibility_under_policy_change", {})
    decision = audit.get("closure_decision", {})
    execution = audit.get("execution_policy", {})
    source_files = audit.get("source_files", {})
    authorized = b4_post.get("verified_authorized_execution_recorded") is True
    expected_b4_scope = (
        "verified_authorized_guarded_driver_execution"
        if authorized
        else "no_verified_current_authorized_execution_record_existing_artifacts_only"
    )

    checks.check(
        audit.get("schema") == "cmame-narrowed-claim-closure-policy-audit-v1",
        "schema changed",
    )
    checks.check(
        audit.get("status") == "narrowed_claim_route_applied_current_gate_reclassified",
        "status changed",
    )
    checks.check(audit.get("read_only") is True, "audit must be read-only")
    checks.check(
        audit.get("submission_ready") is False,
        "audit must keep global submission_ready false outside the narrowed claim",
    )
    checks.check(
        audit.get("legacy_submission_ready_under_narrowed_claim") is True,
        "audit did not record legacy narrowed-claim readiness",
    )
    checks.check(
        audit.get("submission_ready_under_narrowed_claim") is True,
        "narrowed submission-readiness marker missing",
    )
    alias_warning = audit.get("narrowed_claim_alias_warning", "")
    checks.check(
        "validator-only compatibility aliases" in alias_warning
        and "do not read" in alias_warning
        and "global submission readiness" in alias_warning
        and "legacy_submission_ready_under_narrowed_claim" in alias_warning
        and "submission_ready_under_narrowed_claim" in alias_warning,
        "narrowed-claim readiness alias warning missing or too weak",
    )
    checks.check(
        audit.get("full_source_policy_submission_ready") is False,
        "audit overclaims full source-policy submission readiness",
    )
    checks.check(
        audit.get("narrowed_claim_evidence_supported") is True,
        "narrowed evidence support missing",
    )
    checks.check(
        audit.get("current_gate_can_close_now") is True,
        "audit did not record current gate closure",
    )
    checks.check(
        audit.get("current_gate_open_blockers") == [],
        "current open blockers changed",
    )
    checks.check(
        audit.get("current_narrowed_gate_open_blockers") == [],
        "current narrowed-gate blockers changed",
    )
    checks.check(audit.get("global_open_blockers") == ["OC4", "OC6", "OC12"], "global blockers changed")
    checks.check(
        audit.get("objective_blocker_matrix_status") == "global_objective_blockers_remain_open",
        "objective blocker matrix status changed",
    )
    checks.check(
        audit.get("objective_blocking_ids")
        == objective.get("blocking_ids")
        == ["OC4", "OC6", "OC12"],
        "objective blocking IDs changed",
    )
    checks.check(
        audit.get("objective_source_policy_closed_ratio")
        == objective.get("source_policy_closed_ratio")
        == "0/40",
        "objective source-policy ratio changed",
    )
    checks.check(
        audit.get("blocker_open_by_id")
        == audit.get("objective_blocker_open_by_id")
        == objective.get("blocker_open_by_id")
        == EXPECTED_BLOCKER_OPEN_BY_ID,
        "objective blocker open map changed",
    )
    checks.check(
        audit.get("blocker_closure_decision_by_id")
        == audit.get("objective_blocker_closure_decision_by_id")
        == objective.get("blocker_closure_decision_by_id")
        == EXPECTED_BLOCKER_CLOSURE_DECISION_BY_ID,
        "objective blocker closure-decision map changed",
    )
    checks.check(
        audit.get("blocker_closure_allowed_by_id")
        == audit.get("objective_blocker_closure_allowed_by_id")
        == objective.get("blocker_closure_allowed_by_id")
        == EXPECTED_BLOCKER_CLOSURE_ALLOWED_BY_ID,
        "objective blocker closure-allowed map changed",
    )
    checks.check(
        current.get("blocker_gate_status")
        == gate.get("status")
        == "closed_narrowed_claim_subcheck_global_submission_open",
        "current blocker gate status changed",
    )
    checks.check(
        current.get("open_blocker_count") == gate.get("closure_rule", {}).get("open_blocker_count") == 0,
        "current open blocker count changed",
    )
    checks.check(
        current.get("narrowed_claim_open_blocker_count")
        == gate.get("narrowed_claim_open_blocker_count")
        == 0,
        "current narrowed blocker count changed",
    )
    checks.check(
        current.get("global_open_blockers") == gate.get("global_open_blockers") == ["OC4", "OC6", "OC12"],
        "current global blockers changed",
    )

    checks.check(policy.get("route_id") == "no_source_policy_work_precision_publication_claim", "policy route changed")
    checks.check(policy.get("source_policy_rows_closed_must_remain") == 0, "policy overpromotes source-policy rows")
    checks.check(policy.get("source_policy_rows_total") == 40, "policy source-policy total changed")
    checks.check(policy.get("external_superiority_claim_allowed") is False, "policy overclaims external superiority")
    checks.check(policy.get("default_1e_4_required") is False, "policy unexpectedly requires default 1e-4")
    for claim in [
        "strict_conditional_formal_order_claim",
        "common_reference_order_error_diagnostics",
        "diagnostic_work_precision_panels_not_source_policy_superiority",
    ]:
        checks.check(claim in policy.get("accepted_claims", []), f"missing accepted claim: {claim}")
    for claim in [
        "external_superiority_claim",
        "source_policy_work_precision_claim",
        "source_paper_reproduction_claim",
        "strict_external_error_superiority_claim",
        "full_tfe_replacement_claim",
        "seventh_order_theorem",
    ]:
        checks.check(claim in policy.get("excluded_claims", []), f"missing excluded claim: {claim}")

    checks.check(evidence.get("route_b_ready") is True, "Route B readiness missing")
    checks.check(
        evidence.get("claim_after_route") == "formal_order_and_common_reference_diagnostics_only",
        "claim-after-route changed",
    )
    checks.check(
        evidence.get("matrix_rows") == matrix.get("row_count") == 44,
        "matrix row count changed",
    )
    checks.check(
        evidence.get("matrix_raw_rows") == matrix.get("raw_row_count") == 132,
        "matrix raw row count changed",
    )
    checks.check(
        evidence.get("common_reference_order_wins")
        == evidence.get("common_reference_order_comparisons")
        == matrix.get("direct_nonlocal_velocity_order_wins")
        == matrix.get("direct_nonlocal_velocity_order_comparisons")
        == 40,
        "common-reference order wins changed",
    )
    checks.check(
        evidence.get("common_reference_error_wins")
        == evidence.get("common_reference_error_comparisons")
        == matrix.get("direct_nonlocal_velocity_error_wins")
        == matrix.get("direct_nonlocal_velocity_error_comparisons")
        == 40,
        "common-reference error wins changed",
    )
    checks.check(
        evidence.get("source_policy_reproduction") == matrix.get("source_policy_reproduction") is False,
        "source-policy reproduction overclaimed",
    )
    checks.check(
        evidence.get("external_superiority_claim_allowed")
        == matrix.get("external_superiority_claim_allowed")
        == claim_demotion.get("external_superiority_claim_allowed_after_route")
        is False,
        "external superiority overclaimed",
    )
    checks.check(
        evidence.get("strict_external_error_claim_allowed_rows") == 0,
        "strict external error claim rows changed",
    )
    checks.check(
        evidence.get("traceability_closed")
        == traceability.get("claim_boundary", {}).get("result_to_manuscript_traceability_closed")
        is True,
        "traceability closure changed",
    )
    checks.check(evidence.get("traceability_velocity_cells_checked") == 44, "traceability cell count changed")
    checks.check(evidence.get("traceability_source_policy_closed_nonlocal_rows") == 0, "traceability overcloses source-policy rows")

    checks.check(
        evidence.get("figure_count")
        == evidence.get("expected_figure_count")
        == figure.get("figure_count")
        == figure.get("expected_figure_count")
        == 13,
        "figure count changed",
    )
    checks.check(evidence.get("all_figures_available") is True, "figure availability changed")
    checks.check(evidence.get("all_figures_integrated_main_flat") is True, "figure integration changed")
    checks.check(evidence.get("all_pdf_captions_present") is True, "PDF captions changed")
    checks.check(evidence.get("all_legible_dimensions") is True, "figure legibility changed")
    checks.check(
        evidence.get("figure_set_supports_common_reference_diagnostics_only") is True,
        "figure diagnostic boundary missing",
    )
    checks.check(
        current.get("figure_audit_b7_closed") == figure.get("b7_closed") is True,
        "current figure audit did not close B7",
    )
    checks.check(
        current.get("figure_preflight_b7_closure_allowed_now")
        == figure.get("b7_closure_readiness_preflight", {}).get("b7_closure_allowed_now")
        is True,
        "current figure preflight did not close B7",
    )

    checks.check(evidence.get("prose_main_body_machine_token_count") == 0, "main prose token count changed")
    checks.check(evidence.get("prose_flat_main_body_machine_token_count") == 0, "flat prose token count changed")
    checks.check(evidence.get("prose_appendix_artifact_macro_count") == 0, "appendix artifact macro count changed")
    checks.check(evidence.get("prose_flat_appendix_artifact_macro_count") == 0, "flat appendix artifact macro count changed")
    checks.check(
        current.get("b6_closure_allowed_now")
        == prose.get("post_baseline_final_prose_dependency", {}).get("b6_closure_allowed_now")
        is True,
        "current B6 closure not allowed",
    )
    checks.check(
        current.get("b6_final_prose_pass_ready")
        == prose.get("post_baseline_final_prose_dependency", {}).get("final_prose_pass_ready")
        is True,
        "current B6 final prose pass not ready",
    )

    checks.check(
        evidence.get("direct_residual_bridge_submission_standard_satisfied") is True,
        "direct residual-bridge evidence missing",
    )
    checks.check(
        evidence.get("direct_residual_bridge_active_standard_name")
        == "strict_direct_residual_bridge_submission_standard",
        "direct residual-bridge field did not preserve the active direct-route standard name",
    )
    checks.check(
        evidence.get("direct_residual_bridge_submission_standard_scope")
        == "closed_by_direct_residual_bridge_kantorovich_route_primitive_taylor_conditional_schema_open",
        "direct residual-bridge field scope changed",
    )
    checks.check(evidence.get("primitive_taylor_route_closed") is False, "primitive Taylor route overclosed")
    checks.check(
        evidence.get("primitive_taylor_schema_current_instance_available") is False,
        "primitive Taylor conditional schema unexpectedly has a current instance",
    )
    checks.check(
        evidence.get("primitive_taylor_schema_blocker_summary")
        == "0/162 Taylor bounds certified; five primitive lift/bilinear antecedents remain open",
        "primitive Taylor conditional-schema blocker summary changed",
    )
    checks.check(evidence.get("actual_taylor_bounds_proved") == 0, "actual Taylor bound count changed")
    checks.check(evidence.get("open_taylor_bound_terms") == 162, "open Taylor term count changed")
    checks.check(evidence.get("proof_gap_closed") is True, "proof gap closure missing")
    checks.check(evidence.get("stage_residual_O_h7_implementation_defect_proved") is True, "stage residual proof missing")
    checks.check(
        evidence.get("b4_post_execution_status")
        == b4_post.get("status"),
        "B4 post-execution status changed",
    )
    checks.check(
        evidence.get("b4_post_execution_verified_authorized_execution_recorded")
        == b4_post.get("verified_authorized_execution_recorded")
        is authorized,
        "B4 post-execution verified authorized marker inconsistent",
    )
    checks.check(
        evidence.get("b4_post_execution_existing_ready_command_artifacts_present")
        == b4_post.get("existing_ready_command_artifacts_present")
        is True,
        "B4 post-execution existing-artifact marker changed",
    )
    checks.check(
        evidence.get("b4_post_execution_execution_record_scope")
        == b4_post.get("execution_record_scope")
        == expected_b4_scope,
        "B4 post-execution scope changed",
    )
    checks.check(
        evidence.get("b4_post_execution_source_policy_rows_closed")
        == b4_post.get("source_policy_rows_closed")
        == 0,
        "B4 post-execution source-policy rows changed",
    )
    checks.check(
        evidence.get("b4_post_execution_source_policy_rows_total")
        == b4_post.get("source_policy_total_rows")
        == 40,
        "B4 post-execution source-policy total changed",
    )
    checks.check(
        evidence.get("b4_post_execution_b4_can_close_now") == b4_post.get("b4_can_close_now") is False,
        "B4 post-execution unexpectedly closes B4",
    )
    checks.check(
        evidence.get("b4_post_execution_b7_can_close_now") == b4_post.get("b7_can_close_now") is False,
        "B4 post-execution unexpectedly closes B7",
    )

    checks.check(feasibility.get("b4_close_if_narrowed_policy_adopted") is True, "conditional B4 feasibility missing")
    checks.check(feasibility.get("b7_close_if_diagnostic_figure_scope_adopted") is True, "conditional B7 feasibility missing")
    checks.check(feasibility.get("b6_close_after_final_prose_review_refresh") is True, "conditional B6 feasibility missing")
    checks.check(feasibility.get("final_pdf_style_review_refresh_required") is False, "PDF refresh still marked required")
    checks.check(feasibility.get("blocker_gate_reclassification_required") is False, "gate reclassification still marked required")
    checks.check(feasibility.get("review_agent_refresh_required") is False, "review-agent refresh still marked required")
    checks.check(feasibility.get("reproducibility_manifest_refresh_required") is False, "manifest refresh still marked required")
    checks.check(feasibility.get("submission_bundle_refresh_required") is False, "submission-bundle refresh still marked required")
    checks.check(feasibility.get("source_policy_row_promotion_required") is False, "policy unexpectedly requires source-policy promotion")
    checks.check(feasibility.get("heavy_or_b4_execution_required") is False, "policy unexpectedly requires heavy/B4 execution")

    checks.check(decision.get("current_contract_applied") is True, "decision did not apply current narrowed contract")
    checks.check(decision.get("close_b4_b7_now") is True, "decision did not close B4/B7 under narrowed policy")
    checks.check(decision.get("close_b6_now") is True, "decision did not close B6 under narrowed policy")
    checks.check(current.get("pdf_style_decision") == pdf_style.get("decision") == "submit_under_narrowed_claim", "PDF-style decision changed")
    checks.check(current.get("pdf_style_blocking_finding_ids") == [], "PDF-style blocking IDs changed")
    checks.check(
        "Narrowed-claim readiness alias warning:" in md
        and (
            "`validator-only compatibility aliases; do not read "
            "legacy_submission_ready_under_narrowed_claim or "
            "submission_ready_under_narrowed_claim as global submission readiness`"
        )
        in md,
        "narrowed-readiness alias warning missing from markdown",
    )

    checks.check(execution.get("read_only_existing_artifacts") is True, "execution policy not read-only")
    checks.check(execution.get("default_1e_4_required") is False, "execution policy requires default 1e-4")
    checks.check(execution.get("heavy_numerical_run_invoked") is False, "execution policy invoked heavy run")
    checks.check(execution.get("run_v047_invoked") is False, "execution policy invoked run_v047")
    checks.check(execution.get("v048_runner_invoked") is False, "execution policy invoked v048 runner")

    required_sources = {
        "claim_boundary": "CLAIM_BOUNDARY.json",
        "claim_hygiene": "CMAME_CLAIM_HYGIENE_AUDIT.json",
        "claim_demotion": "EXTERNAL_SUPERIORITY_CLAIM_DEMOTION_AUDIT.json",
        "paper_numerical_matrix": "PAPER_NUMERICAL_RESULT_MATRIX.json",
        "traceability": "RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.json",
        "figure_set": "CMAME_FIGURE_SET_AUDIT.json",
        "prose_residue": "CMAME_PROSE_RESIDUE_AUDIT.json",
        "proof_closure": "PROOF_CLOSURE_MANIFEST.json",
        "b4_post_execution": "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.json",
        "pdf_style_review": "CMAME_PDF_STYLE_REVIEW_AUDIT.json",
        "blocker_gate": "CMAME_BLOCKER_CLOSURE_GATE.json",
        "non_superiority_route": "B4_B7_NON_SUPERIORITY_ROUTE_AUDIT.json",
        "objective_completion": "OBJECTIVE_COMPLETION_AUDIT.json",
    }
    checks.check(source_files == required_sources, "source file map changed")

    checks.check(audit.get("required_downstream_updates_before_closure") == [], "downstream updates still marked required")
    checks.check(audit.get("validators_that_currently_reject_direct_flip") == [], "validators still marked as rejecting direct flip")
    for item in [
        "B4 reclassified as narrowed formal-order/common-reference numerical evidence with source-policy work/precision explicitly excluded",
        "B7 reclassified as publication-grade diagnostic/common-reference figure set",
        "B6 prose residue refreshed under the narrowed B4/B7 boundary",
        "PDF-style review refreshed against the narrowed claim boundary",
        "review-agent report, blocker-closure gate, and reproducibility manifest refreshed",
    ]:
        checks.check(item in audit.get("downstream_updates_completed_for_closure", []), f"missing completed downstream update: {item}")

    for token in [
        "CMAME Narrowed-Claim Closure Policy Audit",
        "Narrowed claim evidence supported: `True`.",
        "Current gate can close now: `True`.",
        "Global submission ready: `False`.",
        "Bounded narrowed subcheck satisfied: `True`.",
        "Legacy narrowed-claim readiness marker: `True`; not a global submission readiness marker.",
        "Full source-policy submission ready: `False`.",
        "Current narrowed-gate open blockers: ``.",
        "Global open blockers: `OC4,OC6,OC12`.",
        "## Objective Blocker Matrix",
        "This audit records a bounded narrowed-claim subcheck. It does not close the global objective blockers.",
        EXPECTED_BLOCKER_OPEN_TOKEN,
        EXPECTED_BLOCKER_CLOSURE_DECISION_TOKEN,
        EXPECTED_BLOCKER_CLOSURE_ALLOWED_TOKEN,
        "Route: `no_source_policy_work_precision_publication_claim`.",
        "Source-policy rows remain: `0/40`.",
        "External superiority allowed: `False`.",
        "Common-reference diagnostic favorable order/error cells: `40/40` and `40/40`; not source-policy superiority evidence.",
        "Source-policy reproduction/external superiority: `False` / `False`.",
        "Figure set: `13/13` figures",
        "Prose main/flat machine tokens: `0/0`.",
        "Direct residual-bridge active standard/scope: `strict_direct_residual_bridge_submission_standard` / `closed_by_direct_residual_bridge_kantorovich_route_primitive_taylor_conditional_schema_open`.",
        "Primitive/Taylor conditional-schema route closed and actual/open terms: `False` / `0/162`.",
        "Primitive/Taylor schema instance available and blocker summary: `False` / `0/162 Taylor bounds certified; five primitive lift/bilinear antecedents remain open`.",
        "B4 post-execution rows and close flags: `0/40` and `False/False`.",
        "B4 close if narrowed policy adopted: `True`.",
        "B7 close if diagnostic figure scope adopted: `True`.",
        "B6 close after final prose review refresh: `True`.",
        "Source-policy row promotion required: `False`.",
        "Heavy or B4 execution required: `False`.",
        "Close B4/B7 now: `True`.",
        "Close B6 now: `True`.",
    ]:
        checks.check(token in md, f"markdown missing token: {token}")

    if checks.errors:
        print("CMAME narrowed-claim closure policy audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("CMAME narrowed-claim closure policy audit validation: PASS")
    print("narrowed_claim_evidence_supported=True")
    print("current_gate_can_close_now=True")
    print("source_policy_rows=0/40")
    print(EXPECTED_BLOCKER_OPEN_TOKEN)
    print(EXPECTED_BLOCKER_CLOSURE_DECISION_TOKEN)
    print(EXPECTED_BLOCKER_CLOSURE_ALLOWED_TOKEN)
    return 0


if __name__ == "__main__":
    sys.exit(main())
