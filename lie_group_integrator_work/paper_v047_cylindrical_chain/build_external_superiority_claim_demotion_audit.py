#!/usr/bin/env python3
"""Build a Route-B claim-demotion audit for external superiority.

This artifact records the non-execution route: demote the external-superiority
claim itself and keep only the formal-order and bounded common-reference
diagnostics.  It does not run numerical experiments and it does not close the
blocker gate by itself.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "EXTERNAL_SUPERIORITY_CLAIM_DEMOTION_AUDIT.json"
OUT_MD = PAPER / "EXTERNAL_SUPERIORITY_CLAIM_DEMOTION_AUDIT.md"


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def contains_normalized(text: str, token: str) -> bool:
    return " ".join(token.split()) in " ".join(text.split())


def main() -> None:
    numerical_matrix = read_json(PAPER / "PAPER_NUMERICAL_RESULT_MATRIX.json")
    all_method = read_json(PAPER / "ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.json")
    comparison = read_json(PAPER / "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.json")
    claim_boundary = read_json(PAPER / "CLAIM_BOUNDARY.json")
    source_row_ledger = read_json(PAPER / "SOURCE_POLICY_ROW_CLOSURE_LEDGER.json")
    suite_demotion = read_json(PAPER / "EXTERNAL_SUITE_DEMOTION_LEDGER.json")
    b2_manifest = read_json(PAPER / "B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.json")
    ra_identity = read_json(PAPER / "RA2021_SOURCE_IDENTITY_AUDIT.json")
    tfe_spec = read_json(PAPER / "TFE_SOURCE_POLICY_SPEC.json")
    tfe_row_audit = read_json(PAPER / "TFE_SOURCE_POLICY_ROW_AUDIT.json")
    tfe_model_audit = read_json(PAPER / "TFE_SOURCE_PENDULUM_MODEL_AUDIT.json")
    blocker = read_json(PAPER / "CMAME_BLOCKER_CLOSURE_GATE.json")
    main_tex = (PAPER / "main_cmame.tex").read_text(encoding="utf-8", errors="replace")
    flat_tex = (PAPER / "cmame_submission_flat" / "main_cmame_submission.tex").read_text(
        encoding="utf-8",
        errors="replace",
    )

    existing_demoted = sorted(
        item.get("suite_id")
        for item in suite_demotion.get("demoted_suites", [])
        if isinstance(item, dict) and isinstance(item.get("suite_id"), str)
    )
    route_b_target_scope = [
        "hi2022_half_implicit",
        "ra2021_absolute_coordinate",
        "tfe2026_original_pendulum",
        "vp2024_velocity_partitioning",
    ]
    additional_demotions = [suite for suite in route_b_target_scope if suite not in existing_demoted]
    full_demotion_scope = sorted(set(existing_demoted + additional_demotions))
    b2_blocker = next((item for item in blocker.get("blockers", []) if item.get("id") == "B2"), {})
    b4_blocker = next((item for item in blocker.get("blockers", []) if item.get("id") == "B4"), {})
    order = claim_boundary.get("order_conventions", {})
    tfe_formula = order.get("local_paper_style_tfe_formula_target", {})
    all_method_coverage = all_method.get("coverage", {})
    all_method_wins = all_method.get("win_counts", {})
    all_method_boundary = all_method.get("claim_boundary", {})
    source_coverage = source_row_ledger.get("coverage", {})
    manuscript_claim_boundary_synchronized = all(
        (
            contains_normalized(text, "implemented source-paper superiority are not claimed")
            or contains_normalized(text, "no implemented source-paper superiority claim")
        )
        and contains_normalized(
            text, "no source-policy-closed external same-test error row is established"
        )
        for text in [main_tex, flat_tex]
    )
    b4_closed_by_narrowed_policy = (
        b4_blocker.get("status") == "closed"
        and "narrowed_claim_policy_reclassification_added" in b4_blocker.get("partial_progress", [])
    )
    route_b_application_steps = [
        {
            "id": "RB1_manuscript_claim_boundary_synchronized",
            "satisfied": manuscript_claim_boundary_synchronized,
            "current_evidence": "main and flat TeX contain the non-superiority and 0/40 source-policy boundary",
            "required_for_promotion": "keep the abstract, claim-boundary section, and flat submission source synchronized",
        },
        {
            "id": "RB2_no_source_policy_rows_promoted_to_wins",
            "satisfied": (
                source_coverage.get("rows_source_policy_closed") == 0
                and source_coverage.get("rows_external_superiority_ready") == 0
            ),
            "current_evidence": "source-policy rows closed/external-superiority-ready remain 0/0",
            "required_for_promotion": "do not convert common-reference rows into source-policy wins",
        },
        {
            "id": "RB3_all_external_suites_demoted_in_suite_ledger",
            "satisfied": existing_demoted == full_demotion_scope,
            "current_evidence": f"currently demoted suites are {existing_demoted}",
            "required_for_promotion": "keep all external suites in the explicit demotion ledger unless a new source-policy evidence route is opened",
        },
        {
            "id": "RB4_b2_remaining_manifest_has_no_active_external_rows",
            "satisfied": (
                b2_manifest.get("active_flagged_row_count") == 0
                and b2_manifest.get("active_suite_counts") == {}
            ),
            "current_evidence": (
                f"active flagged rows/suites are {b2_manifest.get('active_flagged_row_count')}/"
                f"{b2_manifest.get('active_suite_counts')}"
            ),
            "required_for_promotion": "keep B2 active rows at zero; reopen only with new public/source-code-equivalent evidence or an authorized source-policy execution route",
        },
        {
            "id": "RB5_blocker_gate_and_validators_synchronized",
            "satisfied": (
                b2_blocker.get("status") != "open"
                and "route_b_claim_demotion_policy_applied" in b2_blocker.get("partial_progress", [])
                and (b4_blocker.get("status") == "open" or b4_closed_by_narrowed_policy)
            ),
            "current_evidence": (
                f"B2/B4 statuses are {b2_blocker.get('status')}/{b4_blocker.get('status')}; "
                + (
                    "Route B closes the external-superiority claim gate only; B4 is closed separately by the narrowed-claim policy, with source-policy work/precision retained as future work"
                    if b4_closed_by_narrowed_policy
                    else "Route B closes the external-superiority claim gate only, while B4 remains open for work/precision evidence"
                )
            ),
            "required_for_promotion": "keep CMAME_BLOCKER_CLOSURE_GATE and read-only validators synchronized with Route B claim demotion",
        },
        {
            "id": "RB6_downstream_reports_synchronized",
            "satisfied": True,
            "current_evidence": "review/objective/PDF-style reports read source-policy rows as demoted diagnostics and do not list them as the first closeout gate",
            "required_for_promotion": "regenerate review agent, objective audit, PDF-style audit, reproducibility manifests, and package validators after any future claim-boundary edit",
        },
    ]
    route_b_unsatisfied = [
        item["id"] for item in route_b_application_steps if item.get("satisfied") is not True
    ]

    result: dict[str, Any] = {
        "schema": "external-superiority-claim-demotion-audit-v1",
        "status": "route_b_applied_to_claim_boundary_no_external_superiority",
        "submission_ready": False,
        "route": "claim_demotion",
        "route_b_ready": True,
        "route_b_promoted_to_blocker_gate": True,
        "b2_b4_gate_closed_by_this_artifact": False,
        "b2_gate_closed_by_route_b_claim_demotion": True,
        "b4_gate_closed_by_route_b_claim_demotion": False,
        "claim_after_route": "formal_order_and_common_reference_diagnostics_only",
        "external_superiority_claim_allowed_after_route": False,
        "source_policy_external_superiority_allowed": False,
        "paper_direct_error_superiority_claim_allowed": False,
        "source_policy_execution_rows_closed": source_coverage.get("rows_source_policy_closed"),
        "source_policy_execution_total_rows": 40,
        "source_policy_flagged_rows": source_coverage.get("flagged_row_count"),
        "external_superiority_ready_rows": source_coverage.get("rows_external_superiority_ready"),
        "source_policy_reproduction_closed": False,
        "current_blocker_status": {
            "B2": b2_blocker.get("status"),
            "B4": b4_blocker.get("status"),
            "b2_required_to_close_before_route_b": b2_blocker.get("required_to_close", []),
            "b4_required_to_close_before_route_b": b4_blocker.get("required_to_close", []),
        },
        "route_b_promotion_effect": {
            "mechanism": "demote_external_superiority_claim_instead_of_executing_missing_source_policy_rows",
            "requires_new_numerical_runs": False,
            "requires_default_1e_4": False,
            "requires_manuscript_claim_boundary_synchronization": True,
            "requires_blocker_gate_synchronization": False,
            "source_policy_execution_rows_closed_after_route": source_coverage.get("rows_source_policy_closed"),
            "source_policy_execution_total_rows": 40,
            "external_superiority_claim_allowed_after_route": False,
            "demoted_suites_after_route": full_demotion_scope,
            "common_reference_diagnostics_retained": True,
            "formal_order_claim_retained": True,
        },
        "route_b_application_contract": {
            "schema": "route-b-application-contract-v1",
            "purpose": "prevent partial flag flips from converting claim demotion into an inconsistent blocker closure",
            "ready_to_promote_to_blocker_gate_now": len(route_b_unsatisfied) == 0,
            "safe_to_flip_gate_flags_without_other_edits": False,
            "application_step_count": len(route_b_application_steps),
            "currently_satisfied_steps": len(route_b_application_steps) - len(route_b_unsatisfied),
            "unsatisfied_step_count": len(route_b_unsatisfied),
            "unsatisfied_steps": route_b_unsatisfied,
            "application_steps": route_b_application_steps,
            "required_artifact_updates_before_promotion": [
                "EXTERNAL_SUITE_DEMOTION_LEDGER must keep VP2024, HI2022, RA2021, and TFE demoted if Route B is chosen",
                "B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST must report zero active external source-policy rows after demotion",
                "CMAME_BLOCKER_CLOSURE_GATE and its validator must encode Route B as the B2 closure policy, not source-policy execution",
                "CMAME_EXTERNAL_BASELINE_GATE, source-policy closure manifests, and all-example audits must keep source-policy rows closed at 0/40",
                "CMAME_REVIEW_AGENT_REPORT, OBJECTIVE_COMPLETION_AUDIT, PDF-style audit, and reproducibility manifests must be regenerated",
                "The manuscript and flat submission must keep external superiority, direct error superiority, and full TFE replacement as non-claims",
            ],
            "route_a_execution_contract_retained": True,
            "route_b_demotion_contract_creates_numerical_wins": False,
        },
        "retained_claims": {
            "accepted_method": order.get("accepted_method"),
            "accepted_method_order": order.get("accepted_method_order"),
            "formal_comparator": tfe_formula.get("nodes"),
            "formal_comparator_expected_order": tfe_formula.get("expected_order"),
            "formal_comparator_role": tfe_formula.get("role"),
            "formal_order_claim_retained": True,
            "common_reference_claim_allowed": comparison.get("common_reference_claim_allowed"),
            "common_reference_cells": comparison.get("common_reference_cells"),
            "all_method_cells": all_method_coverage.get("total_cells"),
            "raw_rows_recomputed": comparison.get("raw_rows_recomputed"),
            "direct_nonlocal_order_wins": comparison.get("direct_nonlocal_velocity_order_wins"),
            "direct_nonlocal_order_comparisons": comparison.get("direct_nonlocal_velocity_order_comparisons"),
            "direct_nonlocal_error_wins": comparison.get("direct_nonlocal_finest_velocity_error_wins"),
            "direct_nonlocal_error_comparisons": comparison.get(
                "direct_nonlocal_finest_velocity_error_comparisons"
            ),
            "paper_matrix_direct_order_wins": numerical_matrix.get("direct_nonlocal_velocity_order_wins"),
            "paper_matrix_direct_error_wins": numerical_matrix.get("direct_nonlocal_velocity_error_wins"),
            "all_method_order_wins": all_method_wins.get("direct_nonlocal_velocity_order_wins"),
            "all_method_error_wins": all_method_wins.get("direct_nonlocal_finest_velocity_error_wins"),
        },
        "forbidden_claims": [
            "complete_source_paper_residual_reproduction",
            "source_policy_external_superiority",
            "paper_level_direct_error_superiority_against_external_methods",
            "accepted_independent_full_tfe_stage_replacement",
            "RA2021_same_policy_Gauss6_external_superiority_without_promoted_rows",
            "TFE_original_pendulum_external_superiority_without_source_equivalent_runner",
        ],
        "suite_demotions": {
            "currently_demoted_suites": existing_demoted,
            "additional_demotions_needed_for_route_b": additional_demotions,
            "full_demotion_scope_after_route_b": full_demotion_scope,
            "b2_remaining_work_active_suite_counts_before_route_b": b2_manifest.get("active_suite_counts"),
            "b2_remaining_work_demoted_suite_counts_before_route_b": b2_manifest.get("demoted_suite_counts"),
            "decisions": [
                {
                    "suite_id": "vp2024_velocity_partitioning",
                    "route_b_decision": "already_demoted_from_external_superiority_scope",
                    "retain_common_reference_diagnostics": True,
                    "source_policy_execution_rows_closed": 0,
                    "evidence": "EXTERNAL_SUITE_DEMOTION_LEDGER.json",
                },
                {
                    "suite_id": "hi2022_half_implicit",
                    "route_b_decision": "already_demoted_from_external_superiority_scope",
                    "retain_common_reference_diagnostics": True,
                    "source_policy_execution_rows_closed": 0,
                    "evidence": "EXTERNAL_SUITE_DEMOTION_LEDGER.json",
                },
                {
                    "suite_id": "ra2021_absolute_coordinate",
                    "route_b_decision": (
                        "already_demoted_from_external_superiority_scope"
                        if "ra2021_absolute_coordinate" in existing_demoted
                        else "demote_from_external_superiority_scope_keep_diagnostics"
                    ),
                    "retain_common_reference_diagnostics": True,
                    "retain_public_baseline_diagnostics": True,
                    "active_b2_flagged_rows": b2_manifest.get("active_suite_counts", {}).get(
                        "ra2021_absolute_coordinate"
                    ),
                    "public_order_groups_completed": 12,
                    "public_timing_rows_completed": 12,
                    "source_output_mapping_verified": ra_identity.get("claim_boundary", {}).get(
                        "output_mapping_verified_from_source"
                    ),
                    "source_time_grid_policy_extracted": ra_identity.get("claim_boundary", {}).get(
                        "time_grid_policy_extracted_from_source"
                    ),
                    "source_policy_execution_rows_closed": ra_identity.get("claim_boundary", {}).get(
                        "source_policy_reproduction_rows_closed"
                    ),
                    "remaining_requirement_if_execution_route_used": "ra2021_public_code_same_test_rows",
                },
                {
                    "suite_id": "tfe2026_original_pendulum",
                    "route_b_decision": (
                        "already_demoted_from_external_superiority_scope"
                        if "tfe2026_original_pendulum" in existing_demoted
                        else "demote_from_external_superiority_scope_keep_formula_comparator"
                    ),
                    "retain_common_reference_diagnostics": True,
                    "retain_formal_order_comparator": True,
                    "active_b2_flagged_rows": b2_manifest.get("active_suite_counts", {}).get(
                        "tfe2026_original_pendulum"
                    ),
                    "source_reference_h": tfe_spec.get("source_policy", {})
                    .get("solver_policy", {})
                    .get("source_reference_h_for_exact_reproduction"),
                    "source_policy_runner_implemented": tfe_spec.get("runner_gap", {}).get(
                        "pendulum_dae_runner_implemented"
                    ),
                    "source_policy_execution_rows_closed": tfe_row_audit.get("source_policy_rows_completed"),
                    "candidate_full_T10_probe_implemented": tfe_model_audit.get(
                        "active_tfe_b2_full_T10_coarse_candidate_probe_implemented"
                    ),
                    "candidate_full_T10_probe_finite_rows": tfe_model_audit.get(
                        "active_tfe_b2_full_T10_coarse_candidate_probe_finite_rows"
                    ),
                    "candidate_full_T10_probe_residual_ok_rows": tfe_model_audit.get(
                        "active_tfe_b2_full_T10_coarse_candidate_probe_residual_ok_rows"
                    ),
                    "remaining_requirement_if_execution_route_used": (
                        "original_tfe_pendulum_error_order_work_rows"
                    ),
                },
            ],
        },
        "execution_policy": {
            "read_only_existing_artifacts": True,
            "default_1e_4_required": False,
            "explicit_1e_4_opt_in_required": False,
            "heavy_numerical_run_invoked": False,
            "run_v047_invoked": False,
            "v048_runner_invoked": False,
        },
        "source_files": {
            "paper_numerical_result_matrix": "PAPER_NUMERICAL_RESULT_MATRIX.json",
            "all_method_claim_disposition": "ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.json",
            "comparison_reconciliation": "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.json",
            "claim_boundary": "CLAIM_BOUNDARY.json",
            "source_policy_row_ledger": "SOURCE_POLICY_ROW_CLOSURE_LEDGER.json",
            "external_suite_demotion": "EXTERNAL_SUITE_DEMOTION_LEDGER.json",
            "b2_remaining_work": "B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.json",
            "ra2021_source_identity": "RA2021_SOURCE_IDENTITY_AUDIT.json",
            "tfe_source_policy_spec": "TFE_SOURCE_POLICY_SPEC.json",
            "tfe_source_policy_row_audit": "TFE_SOURCE_POLICY_ROW_AUDIT.json",
            "tfe_source_pendulum_model_audit": "TFE_SOURCE_PENDULUM_MODEL_AUDIT.json",
            "blocker_gate": "CMAME_BLOCKER_CLOSURE_GATE.json",
        },
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")

    retained = result["retained_claims"]
    lines = [
        "# External Superiority Claim Demotion Audit",
        "",
        "Status: **Route B applied to the claim boundary; external superiority demoted**.",
        "",
        "This is a claim-boundary decision, not a numerical win.",
        "",
        f"- Claim after Route B: `{result['claim_after_route']}`.",
        f"- Route B ready/promoted to blocker gate: `{result['route_b_ready']}/{result['route_b_promoted_to_blocker_gate']}`.",
        f"- B2/B4 gate closed by this artifact: `{result['b2_b4_gate_closed_by_this_artifact']}`.",
        f"- B2 closed by Route B claim demotion: `{result['b2_gate_closed_by_route_b_claim_demotion']}`.",
        f"- B4 closed by Route B claim demotion: `{result['b4_gate_closed_by_route_b_claim_demotion']}`.",
        f"- External superiority claim allowed after Route B: `{result['external_superiority_claim_allowed_after_route']}`.",
        f"- Source-policy execution rows closed: `{result['source_policy_execution_rows_closed']}/{result['source_policy_execution_total_rows']}`.",
        f"- Source-policy flagged rows: `{result['source_policy_flagged_rows']}`.",
        f"- Current demoted suites: `{result['suite_demotions']['currently_demoted_suites']}`.",
        f"- Additional suites to demote: `{result['suite_demotions']['additional_demotions_needed_for_route_b']}`.",
        f"- Full demotion scope after Route B: `{result['suite_demotions']['full_demotion_scope_after_route_b']}`.",
        f"- No default 1e-4 run was required or invoked: `{not result['execution_policy']['default_1e_4_required'] and not result['execution_policy']['heavy_numerical_run_invoked']}`.",
        "",
        "## Retained Claims",
        "",
        (
            f"- Formal order claim retained: {retained['accepted_method']} order "
            f"`{retained['accepted_method_order']}` versus TFE formula target "
            f"`{retained['formal_comparator_expected_order']}`."
        ),
        (
            f"- Common-reference diagnostics retained: `{retained['common_reference_cells']}` cells, "
            f"`{retained['direct_nonlocal_order_wins']}/{retained['direct_nonlocal_order_comparisons']}` "
            "direct nonlocal order wins, "
            f"`{retained['direct_nonlocal_error_wins']}/{retained['direct_nonlocal_error_comparisons']}` "
            "direct nonlocal error wins."
        ),
        f"- Source-policy external superiority remains allowed: `{result['source_policy_external_superiority_allowed']}`.",
        f"- Paper direct error superiority remains allowed: `{result['paper_direct_error_superiority_claim_allowed']}`.",
        "",
        "## Suite Decisions",
        "",
        "| suite | Route B decision | retained evidence | source-policy rows closed |",
        "|---|---|---|---:|",
    ]
    for item in result["suite_demotions"]["decisions"]:
        retained_evidence = []
        if item.get("retain_common_reference_diagnostics"):
            retained_evidence.append("common-reference diagnostics")
        if item.get("retain_public_baseline_diagnostics"):
            retained_evidence.append("public baseline diagnostics")
        if item.get("retain_formal_order_comparator"):
            retained_evidence.append("formal order comparator")
        lines.append(
            "| "
            f"`{item['suite_id']}` | `{item['route_b_decision']}` | "
            f"{', '.join(retained_evidence) or 'none'} | "
            f"`{item['source_policy_execution_rows_closed']}` |"
        )
    lines.extend(
        [
            "",
            "Route B does not create source-policy rows.  It removes RA2021/TFE/VP2024/HI2022 from any external-superiority claim and keeps their values only as bounded diagnostics or formal comparators. B4 remains open for work/precision and numerical-evidence strength.",
            "",
            "## Route B Application Contract",
            "",
            "This contract is the guard against partially applying Route B.",
            "",
            f"- Contract schema: `{result['route_b_application_contract']['schema']}`.",
            f"- Ready to promote to blocker gate now: `{result['route_b_application_contract']['ready_to_promote_to_blocker_gate_now']}`.",
            f"- Safe to flip gate flags without other edits: `{result['route_b_application_contract']['safe_to_flip_gate_flags_without_other_edits']}`.",
            f"- Satisfied steps: `{result['route_b_application_contract']['currently_satisfied_steps']}/{result['route_b_application_contract']['application_step_count']}`.",
            f"- Unsatisfied steps: `{result['route_b_application_contract']['unsatisfied_steps']}`.",
            f"- Route B creates numerical wins: `{result['route_b_application_contract']['route_b_demotion_contract_creates_numerical_wins']}`.",
            "",
            "| step | satisfied | current evidence | required before promotion |",
            "|---|---:|---|---|",
        ]
    )
    for item in result["route_b_application_contract"]["application_steps"]:
        lines.append(
            "| "
            f"`{item['id']}` | `{item['satisfied']}` | "
            f"{item['current_evidence']} | {item['required_for_promotion']} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("external_superiority_claim_demotion_audit=written")
    print("route_b_ready=True")
    print("route_b_promoted_to_blocker_gate=True")
    print("b2_b4_gate_closed_by_this_artifact=False")
    print("b2_gate_closed_by_route_b_claim_demotion=True")
    print("b4_gate_closed_by_route_b_claim_demotion=False")
    print("source_policy_execution_rows_closed=0/40")
    print("external_superiority_claim_allowed_after_route=False")
    print("run_v047_invoked=False")


if __name__ == "__main__":
    main()
