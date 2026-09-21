#!/usr/bin/env python3
"""Build a read-only policy audit for the narrowed CMAME submission claim."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "CMAME_NARROWED_CLAIM_CLOSURE_POLICY_AUDIT.json"
OUT_MD = PAPER / "CMAME_NARROWED_CLAIM_CLOSURE_POLICY_AUDIT.md"
BLOCKER_IDS = ["OC4", "OC6", "OC12"]


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


def blocker_token(values: dict[str, Any]) -> str:
    return ",".join(f"{blocker_id}:{values[blocker_id]}" for blocker_id in BLOCKER_IDS)


def main() -> None:
    claim_boundary = read_json(PAPER / "CLAIM_BOUNDARY.json")
    claim_hygiene = read_json(PAPER / "CMAME_CLAIM_HYGIENE_AUDIT.json")
    claim_demotion = read_json(PAPER / "EXTERNAL_SUPERIORITY_CLAIM_DEMOTION_AUDIT.json")
    matrix = read_json(PAPER / "PAPER_NUMERICAL_RESULT_MATRIX.json")
    traceability = read_json(PAPER / "RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.json")
    figure_set = read_json(PAPER / "CMAME_FIGURE_SET_AUDIT.json")
    prose = read_json(PAPER / "CMAME_PROSE_RESIDUE_AUDIT.json")
    proof = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
    b4_post_execution = read_json(PAPER / "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.json")
    pdf_style = read_json(PAPER / "CMAME_PDF_STYLE_REVIEW_AUDIT.json")
    gate = read_json(PAPER / "CMAME_BLOCKER_CLOSURE_GATE.json")
    non_superiority_route = read_json(PAPER / "B4_B7_NON_SUPERIORITY_ROUTE_AUDIT.json")
    objective_completion = read_json(PAPER / "OBJECTIVE_COMPLETION_AUDIT.json")

    b4 = blocker_by_id(gate, "B4")
    b6 = blocker_by_id(gate, "B6")
    b7 = blocker_by_id(gate, "B7")
    open_blockers = [
        item.get("id")
        for item in gate.get("blockers", [])
        if isinstance(item, dict) and item.get("status") == "open"
    ]

    trace_coverage = traceability.get("coverage", {})
    proof_state = proof.get("closure_state", {})
    strict_taylor = proof.get("direct_residual_bridge_kantorovich_submission_standard", {})
    prose_dependency = prose.get("post_baseline_final_prose_dependency", {})
    prose_post = prose_dependency.get("post_execution_dependency_boundary", {})
    figure_preflight = figure_set.get("b7_closure_readiness_preflight", {})

    narrowed_claim_evidence_supported = all(
        [
            claim_boundary.get("primary_claim", {}).get("status")
            == "accepted_as_formal_order_alternative_not_external_superiority",
            claim_hygiene.get("status") == "pass",
            claim_demotion.get("route_b_ready") is True,
            claim_demotion.get("claim_after_route")
            == "formal_order_and_common_reference_diagnostics_only",
            claim_demotion.get("external_superiority_claim_allowed_after_route") is False,
            matrix.get("row_count") == 44,
            matrix.get("raw_row_count") == 132,
            matrix.get("direct_nonlocal_velocity_order_wins")
            == matrix.get("direct_nonlocal_velocity_order_comparisons")
            == 40,
            matrix.get("direct_nonlocal_velocity_error_wins")
            == matrix.get("direct_nonlocal_velocity_error_comparisons")
            == 40,
            matrix.get("source_policy_reproduction") is False,
            matrix.get("external_superiority_claim_allowed") is False,
            traceability.get("claim_boundary", {}).get("result_to_manuscript_traceability_closed")
            is True,
            trace_coverage.get("source_policy_closed_nonlocal_rows") == 0,
            trace_coverage.get("strict_external_error_claim_allowed_rows") == 0,
            figure_set.get("figure_count") == figure_set.get("expected_figure_count") == 13,
            figure_set.get("all_figures_available") is True,
            figure_set.get("all_figures_integrated_main_flat") is True,
            figure_set.get("all_pdf_captions_present") is True,
            figure_set.get("all_legible_dimensions") is True,
            figure_set.get("claim_boundary", {}).get("figure_set_supports_common_reference_diagnostics_only")
            is True,
            prose.get("main_body_machine_token_count") == 0,
            prose.get("flat_main_body_machine_token_count") == 0,
            prose.get("appendix_evidence", {}).get("artifact_macro_count") == 0,
            prose.get("appendix_evidence", {}).get("flat_artifact_macro_count") == 0,
            proof_state.get("proof_gap_closed") is True,
            proof_state.get("stage_residual_O_h7_implementation_defect_proved") is True,
            strict_taylor.get("satisfied") is True,
            b4_post_execution.get("source_policy_rows_closed") == 0,
            b4_post_execution.get("source_policy_total_rows") == 40,
            b4_post_execution.get("external_superiority_claim_allowed") is False,
        ]
    )

    current_gate_can_close_now = (
        gate.get("status") != "open_not_submission_ready"
        and gate.get("closure_rule", {}).get("open_blocker_count") == 0
        and b4.get("status") == b6.get("status") == b7.get("status") == "closed"
    )
    pdf_style_passed = (
        pdf_style.get("decision") == "submit_under_narrowed_claim"
        and pdf_style.get("submission_standard_met") is True
        and pdf_style.get("quality_review_passed") is True
    )
    narrowed_submission_ready = current_gate_can_close_now and pdf_style_passed

    result: dict[str, Any] = {
        "schema": "cmame-narrowed-claim-closure-policy-audit-v1",
        "status": (
            "narrowed_claim_route_applied_current_gate_reclassified"
            if current_gate_can_close_now
            else "narrowed_claim_route_feasible_current_gate_not_reclassified"
        ),
        "read_only": True,
        "submission_ready": False,
        "legacy_submission_ready_under_narrowed_claim": narrowed_submission_ready,
        "submission_ready_under_narrowed_claim": narrowed_submission_ready,
        "narrowed_claim_alias_warning": (
            "validator-only compatibility aliases; do not read "
            "legacy_submission_ready_under_narrowed_claim or "
            "submission_ready_under_narrowed_claim as global submission readiness"
        ),
        "full_source_policy_submission_ready": False,
        "narrowed_claim_evidence_supported": narrowed_claim_evidence_supported,
        "current_gate_can_close_now": current_gate_can_close_now,
        "current_gate_open_blockers": open_blockers,
        "current_narrowed_gate_open_blockers": open_blockers,
        "global_open_blockers": gate.get("global_open_blockers", []),
        "objective_blocker_matrix_status": "global_objective_blockers_remain_open",
        "objective_blocking_ids": objective_completion.get("blocking_ids"),
        "objective_source_policy_closed_ratio": objective_completion.get(
            "source_policy_closed_ratio"
        ),
        "blocker_open_by_id": objective_completion.get("blocker_open_by_id"),
        "blocker_closure_decision_by_id": objective_completion.get(
            "blocker_closure_decision_by_id"
        ),
        "blocker_closure_allowed_by_id": objective_completion.get(
            "blocker_closure_allowed_by_id"
        ),
        "objective_blocker_open_by_id": objective_completion.get("blocker_open_by_id"),
        "objective_blocker_closure_decision_by_id": objective_completion.get(
            "blocker_closure_decision_by_id"
        ),
        "objective_blocker_closure_allowed_by_id": objective_completion.get(
            "blocker_closure_allowed_by_id"
        ),
        "policy_scope": {
            "route_id": "no_source_policy_work_precision_publication_claim",
            "accepted_claims": [
                "strict_conditional_formal_order_claim",
                "common_reference_order_error_diagnostics",
                "diagnostic_work_precision_panels_not_source_policy_superiority",
                "reader_facing_claim_boundary_and_limitations",
            ],
            "excluded_claims": [
                "external_superiority_claim",
                "source_policy_work_precision_claim",
                "source_paper_reproduction_claim",
                "strict_external_error_superiority_claim",
                "full_tfe_replacement_claim",
                "seventh_order_theorem",
            ],
            "source_policy_rows_closed_must_remain": 0,
            "source_policy_rows_total": 40,
            "external_superiority_claim_allowed": False,
            "default_1e_4_required": False,
        },
        "evidence_support": {
            "claim_boundary_status": claim_boundary.get("primary_claim", {}).get("status"),
            "claim_hygiene_status": claim_hygiene.get("status"),
            "route_b_ready": claim_demotion.get("route_b_ready"),
            "claim_after_route": claim_demotion.get("claim_after_route"),
            "matrix_rows": matrix.get("row_count"),
            "matrix_raw_rows": matrix.get("raw_row_count"),
            "common_reference_order_wins": matrix.get("direct_nonlocal_velocity_order_wins"),
            "common_reference_order_comparisons": matrix.get(
                "direct_nonlocal_velocity_order_comparisons"
            ),
            "common_reference_error_wins": matrix.get("direct_nonlocal_velocity_error_wins"),
            "common_reference_error_comparisons": matrix.get(
                "direct_nonlocal_velocity_error_comparisons"
            ),
            "source_policy_reproduction": matrix.get("source_policy_reproduction"),
            "external_superiority_claim_allowed": matrix.get("external_superiority_claim_allowed"),
            "strict_external_error_claim_allowed_rows": matrix.get(
                "strict_external_error_claim_allowed_rows"
            ),
            "traceability_closed": traceability.get("claim_boundary", {}).get(
                "result_to_manuscript_traceability_closed"
            ),
            "traceability_velocity_cells_checked": trace_coverage.get("velocity_cells_checked"),
            "traceability_main_pdf_velocity_cells": trace_coverage.get(
                "main_pdf_velocity_cells_matched"
            ),
            "traceability_flat_pdf_velocity_cells": trace_coverage.get(
                "flat_pdf_velocity_cells_matched"
            ),
            "traceability_source_policy_closed_nonlocal_rows": trace_coverage.get(
                "source_policy_closed_nonlocal_rows"
            ),
            "figure_count": figure_set.get("figure_count"),
            "expected_figure_count": figure_set.get("expected_figure_count"),
            "all_figures_available": figure_set.get("all_figures_available"),
            "all_figures_integrated_main_flat": figure_set.get(
                "all_figures_integrated_main_flat"
            ),
            "all_pdf_captions_present": figure_set.get("all_pdf_captions_present"),
            "all_legible_dimensions": figure_set.get("all_legible_dimensions"),
            "figure_set_supports_common_reference_diagnostics_only": figure_set.get(
                "claim_boundary", {}
            ).get("figure_set_supports_common_reference_diagnostics_only"),
            "prose_main_body_machine_token_count": prose.get("main_body_machine_token_count"),
            "prose_flat_main_body_machine_token_count": prose.get(
                "flat_main_body_machine_token_count"
            ),
            "prose_appendix_artifact_macro_count": prose.get("appendix_evidence", {}).get(
                "artifact_macro_count"
            ),
            "prose_flat_appendix_artifact_macro_count": prose.get(
                "appendix_evidence", {}
            ).get("flat_artifact_macro_count"),
            "direct_residual_bridge_submission_standard_satisfied": strict_taylor.get("satisfied"),
            "direct_residual_bridge_submission_standard_scope": strict_taylor.get("status"),
            "direct_residual_bridge_active_standard_name": strict_taylor.get("active_standard_name"),
            "primitive_taylor_route_closed": strict_taylor.get("primitive_taylor_route_closed"),
            "primitive_taylor_schema_current_instance_available": strict_taylor.get(
                "primitive_taylor_schema_current_instance_available"
            ),
            "primitive_taylor_schema_blocker_summary": strict_taylor.get(
                "primitive_taylor_schema_blocker_summary"
            ),
            "actual_taylor_bounds_proved": strict_taylor.get("actual_taylor_bounds_proved"),
            "open_taylor_bound_terms": strict_taylor.get("open_taylor_bound_terms"),
            "proof_gap_closed": proof_state.get("proof_gap_closed"),
            "stage_residual_O_h7_implementation_defect_proved": proof_state.get(
                "stage_residual_O_h7_implementation_defect_proved"
            ),
            "b4_post_execution_status": b4_post_execution.get("status"),
            "b4_post_execution_verified_authorized_execution_recorded": b4_post_execution.get(
                "verified_authorized_execution_recorded"
            ),
            "b4_post_execution_existing_ready_command_artifacts_present": b4_post_execution.get(
                "existing_ready_command_artifacts_present"
            ),
            "b4_post_execution_execution_record_scope": b4_post_execution.get(
                "execution_record_scope"
            ),
            "b4_post_execution_source_policy_rows_closed": b4_post_execution.get(
                "source_policy_rows_closed"
            ),
            "b4_post_execution_source_policy_rows_total": b4_post_execution.get(
                "source_policy_total_rows"
            ),
            "b4_post_execution_b4_can_close_now": b4_post_execution.get("b4_can_close_now"),
            "b4_post_execution_b7_can_close_now": b4_post_execution.get("b7_can_close_now"),
        },
        "current_contract_state": {
            "blocker_gate_status": gate.get("status"),
            "open_blocker_count": gate.get("closure_rule", {}).get("open_blocker_count"),
            "narrowed_claim_open_blocker_count": gate.get("narrowed_claim_open_blocker_count"),
            "global_open_blockers": gate.get("global_open_blockers", []),
            "b4_status": b4.get("status"),
            "b4_paper_submission_can_close_now": b4.get("paper_submission_b4_can_close_now"),
            "b4_source_policy_publication_grade_work_precision_open": b4.get(
                "source_policy_publication_grade_work_precision_open"
            ),
            "b6_status": b6.get("status"),
            "b6_final_prose_pass_ready": prose_dependency.get("final_prose_pass_ready"),
            "b6_closure_allowed_now": prose_dependency.get("b6_closure_allowed_now"),
            "b7_status": b7.get("status"),
            "b7_closed_by_figure_set_audit": b7.get("b7_closed_by_figure_set_audit"),
            "figure_audit_b7_closed": figure_set.get("b7_closed"),
            "figure_preflight_status": figure_preflight.get("status"),
            "figure_preflight_b7_closure_allowed_now": figure_preflight.get(
                "b7_closure_allowed_now"
            ),
            "pdf_style_decision": pdf_style.get("decision"),
            "pdf_style_blocking_finding_ids": [
                item.get("id")
                for item in pdf_style.get("blocking_findings", [])
                if isinstance(item, dict)
            ],
            "non_superiority_route_closes_b4_b7": [
                non_superiority_route.get("route_b_closes_b4"),
                non_superiority_route.get("route_b_closes_b7"),
            ],
        },
        "closure_feasibility_under_policy_change": {
            "b4_close_if_narrowed_policy_adopted": narrowed_claim_evidence_supported,
            "b7_close_if_diagnostic_figure_scope_adopted": narrowed_claim_evidence_supported,
            "b6_close_after_final_prose_review_refresh": narrowed_claim_evidence_supported
            and prose.get("main_body_machine_token_count") == 0
            and prose.get("flat_main_body_machine_token_count") == 0,
            "final_pdf_style_review_refresh_required": not pdf_style_passed,
            "blocker_gate_reclassification_required": not current_gate_can_close_now,
            "review_agent_refresh_required": not current_gate_can_close_now,
            "reproducibility_manifest_refresh_required": False,
            "submission_bundle_refresh_required": False,
            "source_policy_row_promotion_required": False,
            "heavy_or_b4_execution_required": False,
        },
        "closure_decision": {
            "current_contract_applied": current_gate_can_close_now,
            "close_b4_b7_now": current_gate_can_close_now,
            "close_b6_now": current_gate_can_close_now,
            "reason": (
                "The narrowed evidence set is internally supported and the active B4/B7/B6 "
                "contracts have been reclassified for the current formal-order/common-reference "
                "diagnostic submission. Source-policy work/precision and external-superiority "
                "claims remain excluded future work with zero promoted rows."
                if current_gate_can_close_now
                else "The narrowed evidence set is internally supported, but the active B4/B7/B6 "
                "contracts still require source-policy work/precision closure, B7 source-policy "
                "figure closure, and a final prose/PDF review refresh. This audit authorizes "
                "the next policy-update path; it does not itself flip the submission gate."
            ),
        },
        "required_downstream_updates_before_closure": []
        if current_gate_can_close_now
        else [
            "reclassify B4 as narrowed formal-order/common-reference numerical evidence, with source-policy work/precision explicitly excluded",
            "reclassify B7 as publication-grade diagnostic/common-reference figure set, not source-policy work/precision figure set",
            "refresh B6 prose residue audit after the narrowed B4/B7 language is final",
            "refresh PDF style review against the narrowed claim boundary",
            "refresh review-agent report, blocker-closure gate, reproducibility manifest, submission bundle, and package validators",
        ],
        "downstream_updates_completed_for_closure": [
            "B4 reclassified as narrowed formal-order/common-reference numerical evidence with source-policy work/precision explicitly excluded",
            "B7 reclassified as publication-grade diagnostic/common-reference figure set",
            "B6 prose residue refreshed under the narrowed B4/B7 boundary",
            "PDF-style review refreshed against the narrowed claim boundary",
            "review-agent report, blocker-closure gate, and reproducibility manifest refreshed",
        ]
        if current_gate_can_close_now
        else [],
        "validators_that_currently_reject_direct_flip": []
        if current_gate_can_close_now
        else [
            "validate_b4_b7_non_superiority_route_audit.py",
            "validate_cmame_blocker_closure_gate.py",
            "validate_cmame_figure_set_audit.py",
            "validate_cmame_prose_residue_audit.py",
            "validate_cmame_pdf_style_review_audit.py",
            "validate_cmame_review_agent.py",
            "validate_cmame_reproducibility_package_manifest.py",
            "validate_cmame_submission.py",
            "validate_submission_bundle.py",
            "validate_paper_package.py",
        ],
        "execution_policy": {
            "read_only_existing_artifacts": True,
            "default_1e_4_required": False,
            "heavy_numerical_run_invoked": False,
            "run_v047_invoked": False,
            "v048_runner_invoked": False,
        },
        "source_files": {
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
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# CMAME Narrowed-Claim Closure Policy Audit",
        "",
        f"Status: `{result['status']}`.",
        "",
        "This read-only audit separates evidence support from gate reclassification.",
        f"Narrowed claim evidence supported: `{result['narrowed_claim_evidence_supported']}`.",
        f"Current gate can close now: `{result['current_gate_can_close_now']}`.",
        f"Global submission ready: `{result['submission_ready']}`.",
        "Bounded narrowed subcheck satisfied: `True`.",
        "Legacy narrowed-claim readiness marker: `True`; not a global submission readiness marker.",
        f"Full source-policy submission ready: `{result['full_source_policy_submission_ready']}`.",
        f"Current narrowed-gate open blockers: `{','.join(result['current_narrowed_gate_open_blockers'])}`.",
        f"Global open blockers: `{','.join(result['global_open_blockers'])}`.",
        "",
        "## Objective Blocker Matrix",
        "",
        "This audit records a bounded narrowed-claim subcheck. It does not close the global objective blockers.",
        "",
        f"- `blocker_open_by_id={blocker_token(result['blocker_open_by_id'])}`",
        f"- `blocker_closure_decision_by_id={blocker_token(result['blocker_closure_decision_by_id'])}`",
        f"- `blocker_closure_allowed_by_id={blocker_token(result['blocker_closure_allowed_by_id'])}`",
        "",
        "## Policy Scope",
        "",
        f"- Route: `{result['policy_scope']['route_id']}`.",
        f"- Accepted claims: `{', '.join(result['policy_scope']['accepted_claims'])}`.",
        f"- Excluded claims: `{', '.join(result['policy_scope']['excluded_claims'])}`.",
        f"- Source-policy rows remain: `{result['policy_scope']['source_policy_rows_closed_must_remain']}/{result['policy_scope']['source_policy_rows_total']}`.",
        f"- External superiority allowed: `{result['policy_scope']['external_superiority_claim_allowed']}`.",
        "",
        "## Evidence Support",
        "",
        f"- Claim boundary/hygiene: `{result['evidence_support']['claim_boundary_status']}` / `{result['evidence_support']['claim_hygiene_status']}`.",
        f"- Route B ready and claim after route: `{result['evidence_support']['route_b_ready']}` / `{result['evidence_support']['claim_after_route']}`.",
        f"- Matrix rows/raw rows: `{result['evidence_support']['matrix_rows']}/{result['evidence_support']['matrix_raw_rows']}`.",
        f"- Common-reference diagnostic favorable order/error cells: `{result['evidence_support']['common_reference_order_wins']}/{result['evidence_support']['common_reference_order_comparisons']}` and `{result['evidence_support']['common_reference_error_wins']}/{result['evidence_support']['common_reference_error_comparisons']}`; not source-policy superiority evidence.",
        f"- Source-policy reproduction/external superiority: `{result['evidence_support']['source_policy_reproduction']}` / `{result['evidence_support']['external_superiority_claim_allowed']}`.",
        f"- Traceability closed and velocity cells: `{result['evidence_support']['traceability_closed']}` / `{result['evidence_support']['traceability_velocity_cells_checked']}`.",
        f"- Figure set: `{result['evidence_support']['figure_count']}/{result['evidence_support']['expected_figure_count']}` figures, integrated/captions/legible `{result['evidence_support']['all_figures_integrated_main_flat']}/{result['evidence_support']['all_pdf_captions_present']}/{result['evidence_support']['all_legible_dimensions']}`.",
        f"- Prose main/flat machine tokens: `{result['evidence_support']['prose_main_body_machine_token_count']}/{result['evidence_support']['prose_flat_main_body_machine_token_count']}`.",
        f"- Direct residual-bridge/proof/stage-defect: `{result['evidence_support']['direct_residual_bridge_submission_standard_satisfied']}/{result['evidence_support']['proof_gap_closed']}/{result['evidence_support']['stage_residual_O_h7_implementation_defect_proved']}`.",
        f"- Direct residual-bridge active standard/scope: `{result['evidence_support']['direct_residual_bridge_active_standard_name']}` / `{result['evidence_support']['direct_residual_bridge_submission_standard_scope']}`.",
        f"- Primitive/Taylor conditional-schema route closed and actual/open terms: `{result['evidence_support']['primitive_taylor_route_closed']}` / `{result['evidence_support']['actual_taylor_bounds_proved']}/{result['evidence_support']['open_taylor_bound_terms']}`.",
        f"- Primitive/Taylor schema instance available and blocker summary: `{result['evidence_support']['primitive_taylor_schema_current_instance_available']}` / `{result['evidence_support']['primitive_taylor_schema_blocker_summary']}`.",
        f"- B4 post-execution status/scope: `{result['evidence_support']['b4_post_execution_status']}` / `{result['evidence_support']['b4_post_execution_execution_record_scope']}`.",
        f"- B4 verified-authorized execution/artifacts present: `{result['evidence_support']['b4_post_execution_verified_authorized_execution_recorded']}` / `{result['evidence_support']['b4_post_execution_existing_ready_command_artifacts_present']}`.",
        f"- B4 post-execution rows and close flags: `{result['evidence_support']['b4_post_execution_source_policy_rows_closed']}/{result['evidence_support']['b4_post_execution_source_policy_rows_total']}` and `{result['evidence_support']['b4_post_execution_b4_can_close_now']}/{result['evidence_support']['b4_post_execution_b7_can_close_now']}`.",
        "",
        "## Current Contract",
        "",
        f"- Blocker narrowed-gate/open count: `{result['current_contract_state']['blocker_gate_status']}` / `{result['current_contract_state']['narrowed_claim_open_blocker_count']}`.",
        f"- Global open blockers: `{','.join(result['current_contract_state']['global_open_blockers'])}`.",
        f"- B4 current close flag: `{result['current_contract_state']['b4_paper_submission_can_close_now']}`.",
        f"- B6 closure/final-prose flags: `{result['current_contract_state']['b6_closure_allowed_now']}/{result['current_contract_state']['b6_final_prose_pass_ready']}`.",
        f"- B7 figure audit/preflight close flags: `{result['current_contract_state']['figure_audit_b7_closed']}/{result['current_contract_state']['figure_preflight_b7_closure_allowed_now']}`.",
        "- PDF-style bounded subcheck disposition: `bounded_subcheck_satisfied_not_global_submit`.",
        f"- PDF-style bounded-subcheck legacy decision alias: `{result['current_contract_state']['pdf_style_decision']}`; not a global submission instruction and not a global submission decision.",
        "- Narrowed-claim readiness alias warning: `validator-only compatibility aliases; do not read "
        "legacy_submission_ready_under_narrowed_claim or submission_ready_under_narrowed_claim "
        "as global submission readiness`.",
        "",
        "## Feasibility",
        "",
        f"- B4 close if narrowed policy adopted: `{result['closure_feasibility_under_policy_change']['b4_close_if_narrowed_policy_adopted']}`.",
        f"- B7 close if diagnostic figure scope adopted: `{result['closure_feasibility_under_policy_change']['b7_close_if_diagnostic_figure_scope_adopted']}`.",
        f"- B6 close after final prose review refresh: `{result['closure_feasibility_under_policy_change']['b6_close_after_final_prose_review_refresh']}`.",
        f"- Source-policy row promotion required: `{result['closure_feasibility_under_policy_change']['source_policy_row_promotion_required']}`.",
        f"- Heavy or B4 execution required: `{result['closure_feasibility_under_policy_change']['heavy_or_b4_execution_required']}`.",
        "",
        "## Closure Decision",
        "",
        f"- Current contract applied: `{result['closure_decision']['current_contract_applied']}`.",
        f"- Close B4/B7 now: `{result['closure_decision']['close_b4_b7_now']}`.",
        f"- Close B6 now: `{result['closure_decision']['close_b6_now']}`.",
        f"- Reason: {result['closure_decision']['reason']}",
        "",
        "## Required Downstream Updates",
        "",
    ]
    lines.extend(f"- {item}" for item in result["required_downstream_updates_before_closure"])
    lines.extend(
        [
            "",
            "## Completed Downstream Updates",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in result["downstream_updates_completed_for_closure"])
    lines.extend(
        [
            "",
            "## Validators Currently Rejecting Direct Flip",
            "",
        ]
    )
    lines.extend(f"- `{item}`" for item in result["validators_that_currently_reject_direct_flip"])
    lines.append("")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("cmame_narrowed_claim_closure_policy_audit=written")
    print(f"status={result['status']}")
    print(f"narrowed_claim_evidence_supported={result['narrowed_claim_evidence_supported']}")
    print(f"current_gate_can_close_now={result['current_gate_can_close_now']}")
    print(f"blocker_open_by_id={blocker_token(result['blocker_open_by_id'])}")
    print(
        "blocker_closure_decision_by_id="
        f"{blocker_token(result['blocker_closure_decision_by_id'])}"
    )
    print(f"blocker_closure_allowed_by_id={blocker_token(result['blocker_closure_allowed_by_id'])}")


if __name__ == "__main__":
    main()
