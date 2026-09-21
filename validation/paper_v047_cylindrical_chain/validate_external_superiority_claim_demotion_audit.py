#!/usr/bin/env python3
"""Validate the Route-B external-superiority claim-demotion audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
EXPECTED_EXISTING_DEMOTED = [
    "hi2022_half_implicit",
    "ra2021_absolute_coordinate",
    "tfe2026_original_pendulum",
    "vp2024_velocity_partitioning",
]
EXPECTED_ADDITIONAL: list[str] = []
EXPECTED_FULL_SCOPE = [
    "hi2022_half_implicit",
    "ra2021_absolute_coordinate",
    "tfe2026_original_pendulum",
    "vp2024_velocity_partitioning",
]


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
        audit = read_json(PAPER / "EXTERNAL_SUPERIORITY_CLAIM_DEMOTION_AUDIT.json")
        audit_md = read_text(PAPER / "EXTERNAL_SUPERIORITY_CLAIM_DEMOTION_AUDIT.md")
        numerical_matrix = read_json(PAPER / "PAPER_NUMERICAL_RESULT_MATRIX.json")
        all_method = read_json(PAPER / "ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.json")
        comparison = read_json(PAPER / "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.json")
        claim_boundary = read_json(PAPER / "CLAIM_BOUNDARY.json")
        source_row_ledger = read_json(PAPER / "SOURCE_POLICY_ROW_CLOSURE_LEDGER.json")
        suite_demotion = read_json(PAPER / "EXTERNAL_SUITE_DEMOTION_LEDGER.json")
        b2_manifest = read_json(PAPER / "B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.json")
        blocker = read_json(PAPER / "CMAME_BLOCKER_CLOSURE_GATE.json")
    except Exception as exc:  # noqa: BLE001
        print(f"external superiority claim-demotion audit validation: FAIL\n- {exc}")
        return 1

    retained = audit.get("retained_claims", {})
    suite_demotions = audit.get("suite_demotions", {})
    execution = audit.get("execution_policy", {})
    promotion = audit.get("route_b_promotion_effect", {})
    application_contract = audit.get("route_b_application_contract", {})
    decisions = {
        item.get("suite_id"): item
        for item in suite_demotions.get("decisions", [])
        if isinstance(item, dict) and isinstance(item.get("suite_id"), str)
    }
    application_steps = {
        item.get("id"): item
        for item in application_contract.get("application_steps", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    source_coverage = source_row_ledger.get("coverage", {})
    order = claim_boundary.get("order_conventions", {})
    tfe_formula = order.get("local_paper_style_tfe_formula_target", {})
    b2_blocker = next((item for item in blocker.get("blockers", []) if item.get("id") == "B2"), {})
    b4_blocker = next((item for item in blocker.get("blockers", []) if item.get("id") == "B4"), {})

    checks.check(
        audit.get("schema") == "external-superiority-claim-demotion-audit-v1",
        "schema changed",
    )
    checks.check(
        audit.get("status") == "route_b_applied_to_claim_boundary_no_external_superiority",
        "status changed",
    )
    checks.check(audit.get("submission_ready") is False, "audit must not mark submission ready")
    checks.check(audit.get("route") == "claim_demotion", "route changed")
    checks.check(audit.get("route_b_ready") is True, "Route B should be ready as a claim-boundary option")
    checks.check(
        audit.get("route_b_promoted_to_blocker_gate") is True,
        "Route B should be synchronized with the blocker claim-boundary gate",
    )
    checks.check(
        audit.get("b2_b4_gate_closed_by_this_artifact") is False,
        "audit must not close B2/B4 by itself",
    )
    checks.check(
        audit.get("claim_after_route") == "formal_order_and_common_reference_diagnostics_only",
        "claim after Route B changed",
    )
    checks.check(
        audit.get("external_superiority_claim_allowed_after_route") is False,
        "external-superiority claim overclosed",
    )
    checks.check(
        audit.get("source_policy_external_superiority_allowed") is False,
        "source-policy external superiority overclaimed",
    )
    checks.check(
        audit.get("paper_direct_error_superiority_claim_allowed") is False,
        "paper direct-error superiority overclaimed",
    )
    checks.check(
        audit.get("source_policy_execution_rows_closed") == source_coverage.get("rows_source_policy_closed") == 0,
        "source-policy execution rows unexpectedly closed",
    )
    checks.check(audit.get("source_policy_execution_total_rows") == 40, "source-policy total row count changed")
    checks.check(
        audit.get("source_policy_flagged_rows") == source_coverage.get("flagged_row_count") == 15,
        "source-policy flagged-row count changed",
    )
    checks.check(audit.get("external_superiority_ready_rows") == 0, "external-superiority ready rows changed")
    checks.check(audit.get("source_policy_reproduction_closed") is False, "source-policy reproduction overclosed")
    checks.check(audit.get("current_blocker_status", {}).get("B2") == b2_blocker.get("status") == "closed", "B2 status changed")
    checks.check(
        audit.get("current_blocker_status", {}).get("B4") == b4_blocker.get("status") == "closed",
        "B4 status changed",
    )
    checks.check(audit.get("b2_gate_closed_by_route_b_claim_demotion") is True, "B2 route-B closure marker missing")
    checks.check(audit.get("b4_gate_closed_by_route_b_claim_demotion") is False, "B4 must remain open after Route B")

    checks.check(
        promotion.get("mechanism")
        == "demote_external_superiority_claim_instead_of_executing_missing_source_policy_rows",
        "Route B mechanism changed",
    )
    checks.check(promotion.get("requires_new_numerical_runs") is False, "Route B should not require new runs")
    checks.check(promotion.get("requires_default_1e_4") is False, "Route B requires default 1e-4")
    checks.check(
        promotion.get("requires_manuscript_claim_boundary_synchronization") is True,
        "Route B promotion should require manuscript synchronization",
    )
    checks.check(
        promotion.get("requires_blocker_gate_synchronization") is False,
        "Route B blocker-gate synchronization should now be complete",
    )
    checks.check(
        promotion.get("source_policy_execution_rows_closed_after_route") == 0,
        "Route B should not create source-policy rows",
    )
    checks.check(
        promotion.get("demoted_suites_after_route") == EXPECTED_FULL_SCOPE,
        "Route B full demotion scope changed",
    )
    checks.check(promotion.get("common_reference_diagnostics_retained") is True, "common-reference diagnostics lost")
    checks.check(promotion.get("formal_order_claim_retained") is True, "formal order claim lost")
    checks.check(
        application_contract.get("schema") == "route-b-application-contract-v1",
        "Route-B application contract schema changed",
    )
    checks.check(
        application_contract.get("ready_to_promote_to_blocker_gate_now") is True,
        "Route B should now be ready for blocker-gate promotion",
    )
    checks.check(
        application_contract.get("safe_to_flip_gate_flags_without_other_edits") is False,
        "Route B should not allow bare flag flips",
    )
    checks.check(application_contract.get("application_step_count") == 6, "Route-B step count changed")
    checks.check(application_contract.get("currently_satisfied_steps") == 6, "Route-B satisfied step count changed")
    checks.check(application_contract.get("unsatisfied_step_count") == 0, "Route-B unsatisfied step count changed")
    checks.check(
        application_contract.get("unsatisfied_steps") == [],
        "Route-B unsatisfied steps changed",
    )
    checks.check(
        application_contract.get("route_a_execution_contract_retained") is True,
        "Route A execution contract should be retained",
    )
    checks.check(
        application_contract.get("route_b_demotion_contract_creates_numerical_wins") is False,
        "Route B must not create numerical wins",
    )
    checks.check(
        set(application_steps)
        == {
            "RB1_manuscript_claim_boundary_synchronized",
            "RB2_no_source_policy_rows_promoted_to_wins",
            "RB3_all_external_suites_demoted_in_suite_ledger",
            "RB4_b2_remaining_manifest_has_no_active_external_rows",
            "RB5_blocker_gate_and_validators_synchronized",
            "RB6_downstream_reports_synchronized",
        },
        "Route-B application step IDs changed",
    )
    checks.check(
        application_steps.get("RB1_manuscript_claim_boundary_synchronized", {}).get("satisfied") is True,
        "Route-B manuscript claim boundary should currently be synchronized",
    )
    checks.check(
        application_steps.get("RB2_no_source_policy_rows_promoted_to_wins", {}).get("satisfied") is True,
        "Route-B no-win-promotion step should currently be satisfied",
    )
    checks.check(
        application_steps.get("RB3_all_external_suites_demoted_in_suite_ledger", {}).get("satisfied") is True,
        "Route-B suite-ledger step should be satisfied after RA2021/TFE demotion",
    )
    checks.check(
        application_steps.get("RB4_b2_remaining_manifest_has_no_active_external_rows", {}).get("satisfied") is True,
        "Route-B B2 manifest step should be satisfied after active rows move to demoted scope",
    )
    checks.check(
        application_steps.get("RB5_blocker_gate_and_validators_synchronized", {}).get("satisfied") is True,
        "Route-B blocker-gate synchronization should be satisfied",
    )
    checks.check(
        application_steps.get("RB6_downstream_reports_synchronized", {}).get("satisfied") is True,
        "Route-B downstream report synchronization should be satisfied",
    )
    required_updates = application_contract.get("required_artifact_updates_before_promotion", [])
    for token in [
        "EXTERNAL_SUITE_DEMOTION_LEDGER must keep VP2024, HI2022, RA2021, and TFE demoted if Route B is chosen",
        "B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST must report zero active external source-policy rows after demotion",
        "CMAME_BLOCKER_CLOSURE_GATE and its validator must encode Route B as the B2 closure policy, not source-policy execution",
        "The manuscript and flat submission must keep external superiority, direct error superiority, and full TFE replacement as non-claims",
    ]:
        checks.check(token in required_updates, f"Route-B required update missing: {token}")

    checks.check(retained.get("accepted_method") == order.get("accepted_method") == "Gauss6/FullVA", "accepted method changed")
    checks.check(retained.get("accepted_method_order") == order.get("accepted_method_order") == 6, "accepted order changed")
    checks.check(retained.get("formal_comparator_expected_order") == tfe_formula.get("expected_order") == 5, "TFE formula order changed")
    checks.check(retained.get("formal_comparator_role") == "comparator_not_accepted_method", "TFE comparator role changed")
    checks.check(retained.get("formal_order_claim_retained") is True, "formal-order retention missing")
    checks.check(retained.get("common_reference_claim_allowed") is True, "common-reference claim not retained")
    checks.check(retained.get("common_reference_cells") == comparison.get("common_reference_cells") == 44, "common-reference cell count changed")
    checks.check(retained.get("all_method_cells") == all_method.get("coverage", {}).get("total_cells") == 44, "all-method cell count changed")
    checks.check(retained.get("raw_rows_recomputed") == comparison.get("raw_rows_recomputed") == 132, "raw-row count changed")
    checks.check(retained.get("direct_nonlocal_order_wins") == comparison.get("direct_nonlocal_velocity_order_wins") == 40, "direct order wins changed")
    checks.check(retained.get("direct_nonlocal_order_comparisons") == 40, "direct order comparisons changed")
    checks.check(retained.get("direct_nonlocal_error_wins") == comparison.get("direct_nonlocal_finest_velocity_error_wins") == 40, "direct error wins changed")
    checks.check(retained.get("direct_nonlocal_error_comparisons") == 40, "direct error comparisons changed")
    checks.check(retained.get("paper_matrix_direct_order_wins") == numerical_matrix.get("direct_nonlocal_velocity_order_wins") == 40, "paper matrix order wins changed")
    checks.check(retained.get("paper_matrix_direct_error_wins") == numerical_matrix.get("direct_nonlocal_velocity_error_wins") == 40, "paper matrix error wins changed")

    checks.check(
        suite_demotions.get("currently_demoted_suites") == EXPECTED_EXISTING_DEMOTED,
        "currently demoted suite list changed",
    )
    checks.check(
        suite_demotions.get("additional_demotions_needed_for_route_b") == EXPECTED_ADDITIONAL,
        "additional Route-B demotions changed",
    )
    checks.check(
        suite_demotions.get("full_demotion_scope_after_route_b") == EXPECTED_FULL_SCOPE,
        "full Route-B demotion scope changed",
    )
    checks.check(
        suite_demotions.get("b2_remaining_work_active_suite_counts_before_route_b")
        == b2_manifest.get("active_suite_counts")
        == {},
        "active suite counts changed",
    )
    checks.check(
        suite_demotions.get("b2_remaining_work_demoted_suite_counts_before_route_b")
        == b2_manifest.get("demoted_suite_counts")
        == {
            "hi2022_half_implicit": 3,
            "ra2021_absolute_coordinate": 5,
            "tfe2026_original_pendulum": 4,
            "vp2024_velocity_partitioning": 3,
        },
        "demoted suite counts changed",
    )
    checks.check(
        sorted(decisions) == EXPECTED_FULL_SCOPE,
        "suite decision set changed",
    )
    checks.check(
        decisions.get("ra2021_absolute_coordinate", {}).get("route_b_decision")
        == "already_demoted_from_external_superiority_scope",
        "RA2021 Route-B decision changed",
    )
    checks.check(decisions.get("ra2021_absolute_coordinate", {}).get("active_b2_flagged_rows") in {None, 0}, "RA2021 active rows changed")
    checks.check(decisions.get("ra2021_absolute_coordinate", {}).get("public_order_groups_completed") == 12, "RA2021 public order count changed")
    checks.check(decisions.get("ra2021_absolute_coordinate", {}).get("public_timing_rows_completed") == 12, "RA2021 public timing count changed")
    checks.check(decisions.get("ra2021_absolute_coordinate", {}).get("source_output_mapping_verified") is True, "RA2021 source mapping audit lost")
    checks.check(decisions.get("ra2021_absolute_coordinate", {}).get("source_time_grid_policy_extracted") is True, "RA2021 time-grid audit lost")
    checks.check(decisions.get("ra2021_absolute_coordinate", {}).get("source_policy_execution_rows_closed") == 0, "RA2021 source rows overclosed")

    tfe = decisions.get("tfe2026_original_pendulum", {})
    checks.check(
        tfe.get("route_b_decision") == "already_demoted_from_external_superiority_scope",
        "TFE Route-B decision changed",
    )
    checks.check(tfe.get("active_b2_flagged_rows") in {None, 0}, "TFE active rows changed")
    checks.check(tfe.get("source_reference_h") == 1e-4, "TFE reference h changed")
    checks.check(tfe.get("source_policy_runner_implemented") is False, "TFE source-policy runner unexpectedly implemented")
    checks.check(tfe.get("source_policy_execution_rows_closed") == 0, "TFE source rows overclosed")
    checks.check(tfe.get("candidate_full_T10_probe_implemented") is True, "TFE full-T10 probe lost")
    checks.check(tfe.get("candidate_full_T10_probe_finite_rows") == 4, "TFE finite probe rows changed")
    checks.check(tfe.get("candidate_full_T10_probe_residual_ok_rows") == 4, "TFE residual probe rows changed")

    for suite_id in EXPECTED_EXISTING_DEMOTED:
        checks.check(
            suite_id in {
                item.get("suite_id")
                for item in suite_demotion.get("demoted_suites", [])
                if isinstance(item, dict)
            },
            f"{suite_id} missing from existing demotion ledger",
        )
        checks.check(
            decisions.get(suite_id, {}).get("route_b_decision")
            == "already_demoted_from_external_superiority_scope",
            f"{suite_id} Route-B existing-demotion decision changed",
        )

    checks.check("complete_source_paper_residual_reproduction" in audit.get("forbidden_claims", []), "forbidden source-reproduction claim missing")
    checks.check("source_policy_external_superiority" in audit.get("forbidden_claims", []), "forbidden external-superiority claim missing")
    checks.check("accepted_independent_full_tfe_stage_replacement" in audit.get("forbidden_claims", []), "forbidden full-TFE claim missing")
    checks.check(execution.get("read_only_existing_artifacts") is True, "audit should be read-only")
    checks.check(execution.get("default_1e_4_required") is False, "audit requires default 1e-4")
    checks.check(execution.get("explicit_1e_4_opt_in_required") is False, "Route B should not require explicit 1e-4")
    checks.check(execution.get("heavy_numerical_run_invoked") is False, "audit invoked heavy run")
    checks.check(execution.get("run_v047_invoked") is False, "audit invoked run_v047")
    checks.check(execution.get("v048_runner_invoked") is False, "audit invoked v048 runner")

    for token in [
        "Status: **Route B applied to the claim boundary; external superiority demoted**.",
        "This is a claim-boundary decision, not a numerical win.",
        "Claim after Route B: `formal_order_and_common_reference_diagnostics_only`.",
        "B2/B4 gate closed by this artifact: `False`.",
        "B2 closed by Route B claim demotion: `True`.",
        "B4 closed by Route B claim demotion: `False`.",
        "External superiority claim allowed after Route B: `False`.",
        "Source-policy execution rows closed: `0/40`.",
        "Additional suites to demote: `[]`.",
        "No default 1e-4 run was required or invoked: `True`.",
        "Formal order claim retained: Gauss6/FullVA order `6` versus TFE formula target `5`.",
        "Common-reference diagnostics retained: `44` cells, `40/40` direct nonlocal order wins, `40/40` direct nonlocal error wins.",
        "Route B does not create source-policy rows.",
        "## Route B Application Contract",
        "Ready to promote to blocker gate now: `True`.",
        "Safe to flip gate flags without other edits: `False`.",
        "Satisfied steps: `6/6`.",
        "Route B creates numerical wins: `False`.",
        "`RB3_all_external_suites_demoted_in_suite_ledger`",
        "`RB6_downstream_reports_synchronized`",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("external superiority claim-demotion audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("external superiority claim-demotion audit validation: PASS")
    print("route_b_ready=True")
    print("route_b_promoted_to_blocker_gate=True")
    print("b2_b4_gate_closed_by_this_artifact=False")
    print("b2_gate_closed_by_route_b_claim_demotion=True")
    print("b4_gate_closed_by_route_b_claim_demotion=False")
    print("source_policy_execution_rows_closed=0/40")
    print("external_superiority_claim_allowed_after_route=False")
    print("run_v047_invoked=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
