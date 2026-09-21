#!/usr/bin/env python3
"""Validate the full source-policy runner archive gap audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
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


def expected_tfe_execution_preflight_boundary(tfe_gap: dict[str, Any]) -> dict[str, Any]:
    preflight = tfe_gap.get("source_policy_execution_preflight", {})
    missing_scope = tfe_gap.get("source_policy_execution_missing_scope", {})
    return {
        "schema": preflight.get("schema"),
        "status": preflight.get("status"),
        "read_only": preflight.get("read_only"),
        "current_route": preflight.get("current_route"),
        "reviewer_facing_decision": preflight.get("reviewer_facing_decision"),
        "explicit_user_opt_in_required": preflight.get("explicit_user_opt_in_required"),
        "opt_in_required_for": preflight.get("opt_in_required_for"),
        "ready_to_execute_source_policy_now": preflight.get("ready_to_execute_source_policy_now"),
        "can_promote_any_tfe_source_policy_row_now": preflight.get(
            "can_promote_any_tfe_source_policy_row_now"
        ),
        "source_policy_rows_completed": preflight.get("source_policy_rows_completed"),
        "execution_block_count": preflight.get("execution_block_count"),
        "execution_blocks": preflight.get("execution_blocks"),
        "terminal_nonpromoted_contract_block_count": tfe_gap.get(
            "terminal_nonpromoted_contract_block_count"
        ),
        "terminal_nonpromoted_contract_blocks": tfe_gap.get(
            "terminal_nonpromoted_contract_blocks"
        ),
        "effective_missing_contract_block_count": tfe_gap.get(
            "effective_missing_contract_block_count"
        ),
        "effective_missing_contract_blocks": tfe_gap.get("effective_missing_contract_blocks"),
        "contract_block_accounting": tfe_gap.get("contract_block_accounting"),
        "runner_contracts_required_before_execution": preflight.get(
            "runner_contracts_required_before_execution"
        ),
        "nonheavy_blocks_dispositioned_by_demotion": preflight.get(
            "nonheavy_blocks_dispositioned_by_demotion"
        ),
        "nonheavy_demotion_does_not_close_source_policy": preflight.get(
            "nonheavy_demotion_does_not_close_source_policy"
        ),
        "reopen_condition": preflight.get("reopen_condition"),
        "missing_scope_requires_new_public_or_source_code_equivalent_artifact_to_reopen": missing_scope.get(
            "requires_new_public_or_source_code_equivalent_artifact_to_reopen"
        ),
        "missing_scope_requires_new_runner_contract_or_explicit_source_policy_execution": missing_scope.get(
            "requires_new_runner_contract_or_explicit_source_policy_execution"
        ),
        "heavy_numerical_run_invoked": preflight.get("heavy_numerical_run_invoked"),
        "run_v047_invoked": preflight.get("run_v047_invoked"),
        "v048_runner_invoked": preflight.get("v048_runner_invoked"),
    }


def expected_tfe_runner_contract_preflight_boundary(certificate: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": certificate.get("schema"),
        "status": certificate.get("status"),
        "read_only": certificate.get("read_only"),
        "entrypoint_count": certificate.get("entrypoint_count"),
        "callable_contract_count": certificate.get("callable_contract_count"),
        "candidate_backed_contract_count": certificate.get("candidate_backed_contract_count"),
        "source_policy_rows_completed": certificate.get("source_policy_rows_completed"),
        "source_policy_closed": certificate.get("source_policy_closed"),
        "source_policy_execution_block_count": certificate.get(
            "source_policy_execution_block_count"
        ),
        "source_policy_execution_blocks": certificate.get("source_policy_execution_blocks"),
        "source_policy_execution_block_matrix": certificate.get(
            "source_policy_execution_block_matrix"
        ),
        "source_policy_execution_block_matrix_summary": certificate.get(
            "source_policy_execution_block_matrix_summary"
        ),
        "source_policy_execution_preflight_status": certificate.get(
            "source_policy_execution_preflight_status"
        ),
        "source_policy_dae_runner_equivalent": certificate.get(
            "source_policy_dae_runner_equivalent"
        ),
        "source_policy_method_runner_equivalent": certificate.get(
            "source_policy_method_runner_equivalent"
        ),
        "monolithic_absolute_coordinate_dae_time_integrator": certificate.get(
            "monolithic_absolute_coordinate_dae_time_integrator"
        ),
        "all_candidate_rows_finite": certificate.get("all_candidate_rows_finite"),
        "all_residual_gates_passed": certificate.get("all_residual_gates_passed"),
        "all_non_equivalent": certificate.get("all_non_equivalent"),
        "safe_current_use": certificate.get("safe_current_use"),
        "next_to_close": certificate.get("next_to_close"),
        "tfe_self_reproduction_status": certificate.get("tfe_self_reproduction_status"),
        "tfe_self_reproduction_reopen_condition": certificate.get(
            "tfe_self_reproduction_reopen_condition"
        ),
        "external_superiority_claim_allowed": certificate.get(
            "external_superiority_claim_allowed"
        ),
        "submission_ready": certificate.get("submission_ready"),
        "heavy_numerical_run_invoked": certificate.get("heavy_numerical_run_invoked"),
        "run_v047_invoked": certificate.get("run_v047_invoked"),
        "v048_runner_invoked": certificate.get("v048_runner_invoked"),
    }


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(PAPER / "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json")
        text = (PAPER / "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.md").read_text(
            encoding="utf-8",
            errors="replace",
        )
        b4_ledger = read_json(PAPER / "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.json")
        b4_packet = read_json(PAPER / "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json")
        b4_handoff = read_json(PAPER / "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json")
        b4_command_freeze = read_json(PAPER / "B4_SOURCE_POLICY_COMMAND_PREFLIGHT_FREEZE_20260620.json")
        b4_expected_output_schema_audit = read_json(
            PAPER / "B4_SOURCE_POLICY_EXPECTED_OUTPUT_SCHEMA_AUDIT_20260620.json"
        )
        b4_expected_output_promotion_readiness_blocker_audit = read_json(
            PAPER / "B4_EXPECTED_OUTPUT_PROMOTION_READINESS_BLOCKER_AUDIT_20260620.json"
        )
        b4_guarded_refusal = read_json(
            PAPER / "B4_GUARDED_DRIVER_REFUSAL_BOUNDARY_AUDIT_20260621.json"
        )
        oc6_reopen_readiness = read_json(
            PAPER / "OC6_SOURCE_EQUIVALENT_REOPEN_READINESS_AUDIT_20260620.json"
        )
        oc6_external_recheck = read_json(
            PAPER / "OC6_EXTERNAL_SOURCE_ARTIFACT_RECHECK_20260621.json"
        )
        oc6_publisher_availability = read_json(
            PAPER / "OC6_TFE_PUBLISHER_ARTIFACT_AVAILABILITY_AUDIT_20260621.json"
        )
        oc6_source_equivalent_request_packet = read_json(
            PAPER / "OC6_TFE_SOURCE_EQUIVALENT_ARTIFACT_REQUEST_PACKET_20260621.json"
        )
        provenance = read_json(PAPER / "FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.json")
        tfe_gap = read_json(PAPER / "TFE_DAE_RUNNER_CONTRACT_GAP_AUDIT.json")
        tfe_runner_contract_preflight = read_json(
            PAPER / "TFE_RUNNER_CONTRACT_PREFLIGHT_CERTIFICATE.json"
        )
        public_refresh = read_json(PAPER / "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.json")
        public_refresh_latest = read_json(PAPER / "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.json")
        reopen_monitor = read_json(PAPER / "SOURCE_POLICY_REOPEN_CONDITION_MONITOR_20260620.json")
        runner_centered = read_json(PAPER / "CMAME_RUNNER_CENTERED_REPRODUCIBILITY_AUDIT.json")
        objective_completion = read_json(PAPER / "OBJECTIVE_COMPLETION_AUDIT.json")
    except Exception as exc:  # noqa: BLE001
        print(f"full source-policy runner archive gap audit validation: FAIL\n- {exc}")
        return 1

    checks.check(audit.get("schema") == "full-source-policy-runner-archive-gap-audit-v1", "schema changed")
    checks.check(
        audit.get("status") == "full_source_policy_runner_archive_not_ready_source_policy_open",
        "status changed",
    )
    checks.check(audit.get("read_only") is True, "audit must remain read-only")
    for source_file in [
        "CMAME_REPRODUCIBILITY_PACKAGE_MANIFEST.json",
        "CMAME_RUNNER_CENTERED_REPRODUCIBILITY_AUDIT.json",
        "CMAME_NARROWED_REPRODUCIBILITY_PACKAGE_AUDIT.json",
        "CMAME_NARROWED_REPRO_CODE_ARCHIVE_MANIFEST.json",
        "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.json",
        "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json",
        "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json",
        "B4_SOURCE_POLICY_COMMAND_PREFLIGHT_FREEZE_20260620.json",
        "B4_SOURCE_POLICY_EXPECTED_OUTPUT_SCHEMA_AUDIT_20260620.json",
        "B4_EXPECTED_OUTPUT_PROMOTION_READINESS_BLOCKER_AUDIT_20260620.json",
        "B4_GUARDED_DRIVER_REFUSAL_BOUNDARY_AUDIT_20260621.json",
        "OC6_SOURCE_EQUIVALENT_REOPEN_READINESS_AUDIT_20260620.json",
        "OC6_EXTERNAL_SOURCE_ARTIFACT_RECHECK_20260621.json",
        "OC6_TFE_PUBLISHER_ARTIFACT_AVAILABILITY_AUDIT_20260621.json",
        "OC6_TFE_SOURCE_EQUIVALENT_ARTIFACT_REQUEST_PACKET_20260621.json",
        "FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.json",
        "RA_HI_SOURCE_POLICY_PROMOTION_BLOCKER_MATRIX.json",
        "TFE_DAE_RUNNER_CONTRACT_GAP_AUDIT.json",
        "TFE_RUNNER_CONTRACT_PREFLIGHT_CERTIFICATE.json",
        "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.json",
        "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.json",
        "SOURCE_POLICY_REOPEN_CONDITION_MONITOR_20260620.json",
        "SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json",
    ]:
        checks.check(source_file in audit.get("source_files", []), f"missing source file: {source_file}")

    package = audit.get("package_boundary", {})
    checks.check(package.get("narrowed_reproducibility_package_ready") is True, "narrowed package not ready")
    checks.check(package.get("narrowed_repro_code_archive_ready") is True, "narrowed archive not ready")
    checks.check(package.get("narrowed_repro_code_archive_submission_ready") is False, "narrowed archive overpromoted")
    checks.check(package.get("local_runner_centered_candidate_ready") is True, "local runner candidate lost")
    checks.check(package.get("runner_centered_package_ready") is False, "runner-centered package overpromoted")
    checks.check(
        package.get("full_source_policy_runner_package_ready")
        == runner_centered.get("full_source_policy_runner_package_ready")
        is False,
        "full source-policy runner package overpromoted",
    )
    checks.check(package.get("manifest_submission_ready") is False, "manifest overpromoted submission readiness")
    checks.check(package.get("primary_submission_package_allowed") is False, "primary package unexpectedly allowed")

    rows = audit.get("source_policy_rows", {})
    checks.check(rows.get("total") == b4_ledger.get("source_policy_rows_total") == 40, "row total changed")
    checks.check(rows.get("closed") == b4_ledger.get("source_policy_rows_closed") == 0, "source-policy rows overclosed")
    checks.check(
        rows.get("provenance_preflight_complete")
        == provenance.get("provenance_preflight_complete_rows")
        == 40,
        "provenance preflight count changed",
    )
    checks.check(
        rows.get("provenance_preflight_total") == provenance.get("row_count") == 40,
        "provenance preflight total changed",
    )
    checks.check(
        rows.get("provenance_preflight_is_not_promotion") is True,
        "provenance preflight overclaimed promotion",
    )
    checks.check(
        rows.get("attempted_not_reproducible")
        == b4_ledger.get("source_policy_rows_attempted_not_reproducible")
        == 20,
        "attempted-not-reproducible rows changed",
    )
    checks.check(
        rows.get("unable_to_reproduce") == b4_ledger.get("source_policy_rows_unable_to_reproduce") == 20,
        "unable-to-reproduce rows changed",
    )
    checks.check(
        rows.get("still_requiring_execution_or_promotion")
        == b4_ledger.get("source_policy_rows_still_requiring_execution_or_promotion")
        == 20,
        "still-open source-policy rows changed",
    )
    checks.check(rows.get("rows_with_launch_command_refs") == 20, "launch-command row count changed")
    checks.check(rows.get("rows_without_launch_command_refs") == 20, "no-launch-command row count changed")
    checks.check(
        audit.get("oc6_source_equivalent_reopen_readiness_latest_external_probe_date")
        == oc6_reopen_readiness.get("latest_external_probe_date_checked")
        == "2026-06-21"
        and audit.get("oc6_source_equivalent_reopen_readiness_latest_external_probe_count")
        == oc6_reopen_readiness.get("latest_external_probe_count")
        == 9
        and audit.get(
            "oc6_source_equivalent_reopen_readiness_latest_external_probe_positive_artifact_rows"
        )
        == oc6_reopen_readiness.get(
            "latest_external_probe_positive_public_code_artifact_rows"
        )
        == 0,
        "OC6 reopen latest external probe counts not propagated to archive gap audit",
    )
    checks.check(
        audit.get(
            "oc6_source_equivalent_reopen_readiness_latest_external_probe_source_policy_rows_closed"
        )
        == oc6_reopen_readiness.get("latest_external_probe_source_policy_rows_closed")
        == 0
        and audit.get(
            "oc6_source_equivalent_reopen_readiness_latest_external_probe_access_limited_count"
        )
        == oc6_reopen_readiness.get("latest_external_probe_access_limited_count")
        == 4
        and audit.get(
            "oc6_source_equivalent_reopen_readiness_latest_external_probe_global_absence_proved"
        )
        == oc6_reopen_readiness.get("latest_external_probe_global_absence_proved")
        is False
        and audit.get(
            "oc6_source_equivalent_reopen_readiness_latest_external_probe_reopen_triggered"
        )
        == oc6_reopen_readiness.get("latest_external_probe_source_policy_reopen_triggered")
        is False,
        "OC6 reopen latest external probe closure boundary not propagated to archive gap audit",
    )

    provenance_handoff = provenance.get("source_policy_execution_handoff", {})
    row_provenance_handoff = audit.get("row_provenance_handoff_boundary", {})
    checks.check(
        row_provenance_handoff == provenance_handoff,
        "row provenance handoff boundary stale or not copied from provenance audit",
    )
    checks.check(
        row_provenance_handoff.get("status")
        == "source_policy_execution_handoff_ready_not_authorized_not_run",
        "row provenance handoff status changed",
    )
    checks.check(
        row_provenance_handoff.get("execution_authorized") is False,
        "row provenance handoff unexpectedly authorized",
    )
    checks.check(
        row_provenance_handoff.get("commands_not_run_by_handoff") is True,
        "row provenance handoff commands unexpectedly run",
    )
    checks.check(
        row_provenance_handoff.get("exact_required_user_approval_statement")
        == "I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json.",
        "row provenance exact approval statement changed",
    )
    checks.check(
        row_provenance_handoff.get("guarded_execution_driver")
        == "run_b4_source_policy_after_opt_in.sh",
        "row provenance guarded driver changed",
    )
    checks.check(
        row_provenance_handoff.get("driver_requires_exact_approval") is True
        and row_provenance_handoff.get("driver_does_not_authorize_execution") is True,
        "row provenance guarded driver boundary changed",
    )
    checks.check(
        row_provenance_handoff.get("opt_in_required_command_count") == 13
        and row_provenance_handoff.get("opt_in_required_mapped_external_rows") == 20
        and row_provenance_handoff.get("terminal_unable_to_reproduce_rows") == 20,
        "row provenance handoff counts changed",
    )
    row_provenance_action_boundary = audit.get("row_provenance_action_boundary", {})
    checks.check(
        row_provenance_action_boundary
        == provenance.get("action_boundary")
        == audit.get("action_boundary"),
        "row provenance action boundary stale or not copied into archive gap audit",
    )
    checks.check(
        audit.get("row_provenance_source_policy_execution_invoked")
        == provenance.get("source_policy_execution_invoked")
        is False,
        "row provenance source-policy execution invocation boundary changed",
    )
    checks.check(
        row_provenance_action_boundary.get("source_policy_execution_allowed_now") is False
        and row_provenance_action_boundary.get("exact_b4_opt_in_required_for_execution") is True
        and row_provenance_action_boundary.get("safe_without_b4_opt_in_count") == 4
        and row_provenance_action_boundary.get("opt_in_required_action_count") == 1
        and row_provenance_action_boundary.get("opt_in_required_command_count") == 13
        and row_provenance_action_boundary.get("opt_in_required_mapped_external_rows") == 20,
        "row provenance action boundary counts changed",
    )

    expected_tfe_preflight = expected_tfe_execution_preflight_boundary(tfe_gap)
    tfe_preflight = audit.get("tfe_source_policy_execution_preflight_boundary", {})
    checks.check(
        tfe_preflight == expected_tfe_preflight,
        "TFE source-policy execution preflight boundary stale or not copied from gap audit",
    )
    checks.check(
        tfe_preflight.get("schema") == "tfe-source-policy-execution-preflight-v1",
        "TFE preflight schema changed",
    )
    checks.check(
        tfe_preflight.get("status") == "terminal_no_public_code_self_reproduction_attempted_not_promoted",
        "TFE preflight status changed",
    )
    checks.check(tfe_preflight.get("read_only") is True, "TFE preflight must remain read-only")
    checks.check(
        tfe_preflight.get("explicit_user_opt_in_required") is False,
        "TFE preflight unexpectedly requires opt-in",
    )
    checks.check(
        tfe_preflight.get("opt_in_required_for") == [],
        "TFE preflight opt-in list changed",
    )
    checks.check(
        tfe_preflight.get("ready_to_execute_source_policy_now") is False,
        "TFE preflight unexpectedly ready to execute",
    )
    checks.check(
        tfe_preflight.get("can_promote_any_tfe_source_policy_row_now") is False,
        "TFE preflight unexpectedly promotable",
    )
    checks.check(
        tfe_preflight.get("source_policy_rows_completed") == 0,
        "TFE preflight overcloses rows",
    )
    checks.check(
        tfe_preflight.get("execution_block_count") == 4
        and len(tfe_preflight.get("execution_blocks", [])) == 4,
        "TFE execution block count changed",
    )
    checks.check(
        tfe_preflight.get("terminal_nonpromoted_contract_block_count") == 2
        and tfe_preflight.get("effective_missing_contract_block_count") == 4
        and tfe_preflight.get("contract_block_accounting", {}).get(
            "source_policy_rows_closed_by_accounting"
        )
        == 0,
        "TFE contract block accounting changed",
    )
    checks.check(
        tfe_preflight.get("nonheavy_blocks_dispositioned_by_demotion") is True
        and tfe_preflight.get("nonheavy_demotion_does_not_close_source_policy") is True,
        "TFE non-heavy demotion boundary changed",
    )
    checks.check(
        tfe_preflight.get("reopen_condition")
        == "new_public_or_source_code_equivalent_tfe_implementation_artifact",
        "TFE preflight reopen condition changed",
    )
    checks.check(
        tfe_preflight.get("missing_scope_requires_new_public_or_source_code_equivalent_artifact_to_reopen")
        is True
        and tfe_preflight.get("missing_scope_requires_new_runner_contract_or_explicit_source_policy_execution")
        is False,
        "TFE missing-scope reopen boundary changed",
    )
    checks.check(
        tfe_preflight.get("heavy_numerical_run_invoked") is False
        and tfe_preflight.get("run_v047_invoked") is False
        and tfe_preflight.get("v048_runner_invoked") is False,
        "TFE preflight invoked a forbidden run",
    )

    expected_runner_preflight = expected_tfe_runner_contract_preflight_boundary(
        tfe_runner_contract_preflight
    )
    runner_preflight = audit.get("tfe_runner_contract_preflight_boundary", {})
    checks.check(
        runner_preflight == expected_runner_preflight,
        "TFE runner contract preflight boundary stale or not copied from certificate",
    )
    checks.check(
        runner_preflight.get("schema") == "tfe-runner-contract-preflight-certificate-v1",
        "TFE runner contract preflight schema changed",
    )
    checks.check(
        runner_preflight.get("status")
        == "contract_entrypoints_callable_candidate_backed_source_policy_open",
        "TFE runner contract preflight status changed",
    )
    checks.check(runner_preflight.get("read_only") is True, "TFE runner preflight must remain read-only")
    checks.check(
        runner_preflight.get("callable_contract_count") == 3
        and runner_preflight.get("entrypoint_count") == 3
        and runner_preflight.get("candidate_backed_contract_count") == 3,
        "TFE runner contract callable/candidate counts changed",
    )
    checks.check(
        runner_preflight.get("source_policy_rows_completed") == 0
        and runner_preflight.get("source_policy_closed") is False,
        "TFE runner contract preflight overclosed source-policy rows",
    )
    checks.check(
        runner_preflight.get("source_policy_execution_block_count") == 4
        and len(runner_preflight.get("source_policy_execution_blocks", [])) == 4,
        "TFE runner contract preflight execution block count changed",
    )
    checks.check(
        runner_preflight.get("source_policy_execution_block_matrix_summary")
        == {
            "execution_block_count": 4,
            "candidate_backed_entrypoint_blocks": 3,
            "blocks_without_candidate_entrypoint": 1,
            "source_policy_equivalent_blocks": 0,
            "source_policy_rows_completed": 0,
            "can_resolve_without_heavy_run_blocks": 0,
            "requires_new_artifact_or_execution_blocks": 4,
            "closure_status": "all_source_policy_execution_blocks_open",
        },
        "TFE runner contract execution block summary changed",
    )
    checks.check(
        len(runner_preflight.get("source_policy_execution_block_matrix", [])) == 4,
        "TFE runner contract execution block matrix row count changed",
    )
    checks.check(
        runner_preflight.get("source_policy_dae_runner_equivalent") is False
        and runner_preflight.get("source_policy_method_runner_equivalent") is False
        and runner_preflight.get("monolithic_absolute_coordinate_dae_time_integrator") is False
        and runner_preflight.get("all_non_equivalent") is True,
        "TFE runner contract preflight equivalence boundary changed",
    )
    checks.check(
        runner_preflight.get("safe_current_use")
        == "runner_contract_preflight_only_not_source_policy_reproduction",
        "TFE runner contract preflight safe-use boundary changed",
    )
    checks.check(
        runner_preflight.get("tfe_self_reproduction_reopen_condition")
        == "new_public_or_source_code_equivalent_tfe_implementation_artifact",
        "TFE runner contract preflight reopen condition changed",
    )
    checks.check(
        runner_preflight.get("external_superiority_claim_allowed") is False
        and runner_preflight.get("submission_ready") is False,
        "TFE runner contract preflight overpromoted external/submission readiness",
    )
    checks.check(
        runner_preflight.get("heavy_numerical_run_invoked") is False
        and runner_preflight.get("run_v047_invoked") is False
        and runner_preflight.get("v048_runner_invoked") is False,
        "TFE runner contract preflight invoked a forbidden run",
    )

    terminal_suites = {
        item.get("suite_id"): item
        for item in audit.get("terminal_unable_to_reproduce_suites", [])
        if isinstance(item, dict)
    }
    expected_terminal_reopen_conditions = {
        "tfe2026_original_pendulum": "new_public_or_source_code_equivalent_tfe_implementation_artifact",
        "vp2024_velocity_partitioning": "new_distinct_public_vp2024_velocity_partitioning_code_path",
    }
    checks.check(terminal_suites.get("tfe2026_original_pendulum", {}).get("row_count") == 16, "TFE row count changed")
    checks.check(
        terminal_suites.get("tfe2026_original_pendulum", {}).get("unable_to_reproduce_rows") == 16,
        "TFE unable rows changed",
    )
    checks.check(terminal_suites.get("vp2024_velocity_partitioning", {}).get("row_count") == 4, "VP row count changed")
    checks.check(
        terminal_suites.get("vp2024_velocity_partitioning", {}).get("unable_to_reproduce_rows") == 4,
        "VP unable rows changed",
    )
    checks.check(
        sum(item.get("source_policy_rows_closed", 0) for item in terminal_suites.values()) == 0,
        "terminal suites overclosed rows",
    )
    checks.check(
        {
            suite_id: terminal_suites.get(suite_id, {}).get("reopen_condition")
            for suite_id in expected_terminal_reopen_conditions
        }
        == expected_terminal_reopen_conditions,
        "terminal suite reopen conditions changed",
    )
    closure_matrix = {
        item.get("id"): item
        for item in audit.get("archive_closure_matrix", [])
        if isinstance(item, dict)
    }
    checks.check(
        set(closure_matrix)
        == {
            "OC4_source_policy_reproduction_rows",
            "OC6_tfe_source_policy_runner",
            "OC12_full_source_policy_runner_archive",
        },
        "archive closure matrix ids changed",
    )
    oc4 = closure_matrix.get("OC4_source_policy_reproduction_rows", {})
    expected_b4_traceability = b4_handoff.get("command_row_traceability", {}).get("summary", {})
    checks.check(
        oc4.get("objective_blocker") == "OC4"
        and oc4.get("current_status") == "open"
        and oc4.get("source_policy_rows_closed") == 0
        and oc4.get("source_policy_rows_total") == 40
        and oc4.get("terminal_unable_to_reproduce_rows") == 20
        and oc4.get("rows_requiring_authorized_closeout_or_new_artifact") == 20
        and oc4.get("ready_command_count") == 13
        and oc4.get("ready_command_mapped_external_rows") == 20
        and oc4.get("execution_authorized") is False
        and oc4.get("closure_allowed_now") is False
        and oc4.get("archive_effect") == "blocks_full_archive_primary_use",
        "OC4 archive closure matrix row changed",
    )
    checks.check(
        oc4.get("command_traceability_summary") == expected_b4_traceability,
        "OC4 command traceability summary stale",
    )
    checks.check(
        oc4.get("command_traceability_summary", {}).get("unique_mapped_row_count") == 20
        and oc4.get("command_traceability_summary", {}).get("ra_hi_unique_row_count") == 20
        and oc4.get("command_traceability_summary", {}).get("ra_hi_unique_rows_all_mapped") is True
        and oc4.get("command_traceability_summary", {}).get("terminal_rows_with_command_refs") == 0
        and oc4.get("command_traceability_summary", {}).get("declared_vs_traced_mismatch_count") == 0
        and oc4.get("command_traceability_summary", {}).get("source_policy_closed_rows") == 0
        and oc4.get("command_traceability_summary", {}).get("promotion_ready_rows") == 0,
        "OC4 command traceability invariants changed",
    )
    checks.check(
        oc4.get("exact_approval_required")
        == "I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json."
        and len(oc4.get("required_evidence_to_close", [])) == 3,
        "OC4 archive closure evidence contract changed",
    )
    oc6 = closure_matrix.get("OC6_tfe_source_policy_runner", {})
    checks.check(
        oc6.get("objective_blocker") == "OC6"
        and oc6.get("current_status") == "partial_terminal_not_promoted"
        and oc6.get("source_policy_rows_completed") == 0
        and oc6.get("terminal_nonpromoted_contract_block_count") == 2
        and oc6.get("effective_execution_contract_block_count") == 4
        and oc6.get("ready_to_execute_source_policy_now") is False
        and oc6.get("can_promote_any_tfe_source_policy_row_now") is False
        and oc6.get("runner_contract_preflight_status")
        == "contract_entrypoints_callable_candidate_backed_source_policy_open"
        and oc6.get("runner_contract_preflight_entrypoints") == "3/3"
        and oc6.get("runner_contract_preflight_candidate_backed") == "3/3"
        and oc6.get("runner_contract_preflight_source_policy_rows_completed") == 0
        and oc6.get("runner_contract_preflight_execution_blocks") == 4
        and oc6.get("runner_contract_preflight_execution_block_matrix_summary")
        == {
            "execution_block_count": 4,
            "candidate_backed_entrypoint_blocks": 3,
            "blocks_without_candidate_entrypoint": 1,
            "source_policy_equivalent_blocks": 0,
            "source_policy_rows_completed": 0,
            "can_resolve_without_heavy_run_blocks": 0,
            "requires_new_artifact_or_execution_blocks": 4,
            "closure_status": "all_source_policy_execution_blocks_open",
        }
        and oc6.get("runner_contract_preflight_safe_use")
        == "runner_contract_preflight_only_not_source_policy_reproduction"
        and oc6.get("runner_contract_preflight_all_non_equivalent") is True
        and oc6.get("source_equivalent_request_packet_status")
        == "request_packet_ready_not_sent_no_source_policy_closure"
        and oc6.get("source_equivalent_request_ready") is True
        and oc6.get("source_equivalent_request_sent") is False
        and oc6.get("source_equivalent_requested_artifact_count") == 7
        and oc6.get("reopen_condition")
        == "new_public_or_source_code_equivalent_tfe_implementation_artifact"
        and oc6.get("closure_allowed_now") is False
        and oc6.get("archive_effect") == "blocks_tfe_rows_from_full_archive_promotion"
        and len(oc6.get("required_evidence_to_close", [])) == 4,
        "OC6 archive closure matrix row changed",
    )
    oc12 = closure_matrix.get("OC12_full_source_policy_runner_archive", {})
    checks.check(
        oc12.get("objective_blocker") == "OC12"
        and oc12.get("current_status") == "partial_narrowed_replay_ready_full_archive_open"
        and oc12.get("narrowed_reproducibility_package_ready") is True
        and oc12.get("local_runner_centered_candidate_ready") is True
        and oc12.get("full_source_policy_runner_package_ready") is False
        and oc12.get("current_archive_usable_as_full_source_policy_runner_archive") is False
        and oc12.get("primary_submission_package_allowed") is False
        and oc12.get("upstream_blockers") == ["OC4", "OC6"]
        and oc12.get("safe_current_package_use") == "narrowed_claim_replay_and_audit_provenance_only"
        and oc12.get("closure_allowed_now") is False
        and oc12.get("archive_effect") == "current_archive_is_narrowed_claim_provenance_only"
        and len(oc12.get("required_evidence_to_close", [])) == 4,
        "OC12 archive closure matrix row changed",
    )
    checks.check(audit.get("oc12_blocker_id") == "OC12", "OC12 blocker id alias changed")
    checks.check(audit.get("oc12_blocker_status") == "partial", "OC12 blocker status alias changed")
    checks.check(audit.get("oc12_blocker_open") is True, "OC12 blocker was overclosed")
    checks.check(
        audit.get("closure_decision")
        == audit.get("oc12_closure_decision")
        == "remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready",
        "OC12 closure decision alias changed",
    )
    checks.check(audit.get("oc12_closure_allowed_now") is False, "OC12 closure unexpectedly allowed now")
    checks.check(
        audit.get("objective_blocker_matrix_status") == "global_objective_blockers_remain_open",
        "objective blocker matrix status changed",
    )
    checks.check(
        audit.get("blocker_open_by_id") == EXPECTED_BLOCKER_OPEN_BY_ID,
        "objective blocker open map changed",
    )
    checks.check(
        audit.get("blocker_closure_decision_by_id") == EXPECTED_BLOCKER_CLOSURE_DECISION_BY_ID,
        "objective blocker closure-decision map changed",
    )
    checks.check(
        audit.get("blocker_closure_allowed_by_id") == EXPECTED_BLOCKER_CLOSURE_ALLOWED_BY_ID,
        "objective blocker closure-allowed map changed",
    )
    checks.check(audit.get("dependency_blockers") == ["OC4", "OC6"], "OC12 dependency blockers changed")
    checks.check(
        audit.get("current_archive_usable_as_full_source_policy_runner_archive") is False,
        "OC12 current archive usability overclaimed",
    )
    checks.check(
        audit.get("safe_current_use") == "narrowed_claim_replay_and_audit_provenance_only",
        "OC12 safe-current-use alias changed",
    )
    checks.check(
        audit.get("safe_current_package_use") == "narrowed_claim_replay_and_audit_provenance_only",
        "OC12 safe-current-package-use alias changed",
    )
    checks.check(audit.get("primary_submission_package_allowed") is False, "OC12 primary package unexpectedly allowed")
    checks.check(audit.get("narrowed_reproducibility_package_ready") is True, "OC12 narrowed package ready alias changed")
    checks.check(audit.get("local_runner_centered_candidate_ready") is True, "OC12 local runner alias changed")
    checks.check(
        audit.get("oc12_required_evidence_to_close") == oc12.get("required_evidence_to_close"),
        "OC12 required-evidence alias changed",
    )

    ra_hi = audit.get("ra_hi_closeout_boundary", {})
    checks.check(ra_hi.get("execution_handoff_status") == b4_handoff.get("status"), "handoff status missing")
    checks.check(ra_hi.get("execution_handoff_authorized") is False, "handoff unexpectedly authorized")
    checks.check(ra_hi.get("execution_handoff_commands_not_run") is True, "handoff commands unexpectedly run")
    checks.check(ra_hi.get("public_source_root_available_rows") == 20, "RA/HI public-root rows changed")
    checks.check(ra_hi.get("no_public_code_rows_included") == 0, "RA/HI misclassified as no-public-code")
    checks.check(ra_hi.get("source_policy_rows_closed") == 0, "RA/HI rows overclosed")
    checks.check(ra_hi.get("source_policy_rows_not_promoted") == 20, "RA/HI not-promoted rows changed")
    checks.check(ra_hi.get("current_evidence_terminal_not_promotable_rows") == 20, "RA/HI terminal evidence count changed")
    checks.check(
        ra_hi.get("future_promotion_requires_authorized_execution_or_new_artifact_rows") == 20,
        "RA/HI future-promotion boundary changed",
    )
    checks.check(ra_hi.get("source_policy_reproduction_complete_rows") == 0, "RA/HI overclaims reproduction")
    checks.check(ra_hi.get("ready_command_count") == b4_packet.get("ready_command_count") == 13, "ready command count changed")
    checks.check(
        ra_hi.get("ready_command_mapped_external_rows")
        == b4_packet.get("ready_command_mapped_external_rows")
        == 20,
        "ready command mapped rows changed",
    )
    checks.check(
        ra_hi.get("command_traceability_summary") == expected_b4_traceability,
        "RA/HI command traceability summary stale",
    )
    checks.check(
        ra_hi.get("command_traceability_summary", {}).get("traced_command_row_reference_total") == 32
        and ra_hi.get("command_traceability_summary", {}).get("declared_mapped_row_reference_total") == 32
        and ra_hi.get("command_traceability_summary", {}).get("commands_without_traced_rows") == [],
        "RA/HI command traceability row-reference accounting changed",
    )
    checks.check(
        ra_hi.get("handoff_ready_command_batch_count") == b4_handoff.get(
            "ra_hi_authorized_closeout_handoff", {}
        ).get("ready_command_batch_count") == 2,
        "handoff batch count changed",
    )
    checks.check(
        ra_hi.get("handoff_ready_command_count") == b4_handoff.get(
            "ra_hi_authorized_closeout_handoff", {}
        ).get("ready_command_count") == 13,
        "handoff command count changed",
    )
    checks.check(
        ra_hi.get("handoff_ready_command_mapped_external_rows") == b4_handoff.get(
            "ra_hi_authorized_closeout_handoff", {}
        ).get("ready_command_mapped_external_rows") == 20,
        "handoff mapped-row count changed",
    )
    checks.check(ra_hi.get("execution_invoked_by_packet") is False, "B4 execution unexpectedly invoked")
    checks.check(ra_hi.get("explicit_user_opt_in_required_before_any_command") is True, "B4 opt-in boundary changed")
    expected_source_policy_execution_invoked = any(
        [
            b4_packet.get("execution_invoked_by_packet") is True,
            b4_handoff.get("commands_not_run_by_handoff") is False,
            provenance_handoff.get("commands_not_run_by_handoff") is False,
            b4_command_freeze.get("commands_executed_by_freeze") is True,
            b4_expected_output_schema_audit.get("commands_executed_by_audit") is True,
            b4_guarded_refusal.get("source_policy_execution_invoked") is True,
        ]
    )
    checks.check(
        audit.get("source_policy_execution_invoked")
        == expected_source_policy_execution_invoked
        is False,
        "source-policy execution invocation boundary changed",
    )
    checks.check(
        ra_hi.get("required_user_approval_statement")
        == b4_packet.get("required_user_approval_statement")
        == "I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json.",
        "B4 exact approval statement changed",
    )

    refresh = audit.get("public_code_refresh", {})
    checks.check(refresh.get("status") == public_refresh.get("status"), "refresh status changed")
    checks.check(refresh.get("row_count") == 20, "refresh row count changed")
    checks.check(refresh.get("public_code_available_rows") == 0, "refresh unexpectedly found public code")
    checks.check(refresh.get("self_reproduction_attempted_rows") == 20, "refresh attempted rows changed")
    checks.check(refresh.get("unable_to_reproduce_rows") == 20, "refresh unable rows changed")
    checks.check(refresh.get("source_policy_rows_closed") == 0, "refresh overclosed rows")
    latest_refresh = audit.get("public_code_refresh_latest_supplement", {})
    checks.check(
        latest_refresh.get("status")
        == public_refresh_latest.get("status")
        == "public_code_refresh_20260620_no_positive_new_source_artifact_rows_remain_unable_to_reproduce",
        "latest refresh supplement status changed",
    )
    checks.check(latest_refresh.get("date_checked") == "2026-06-20", "latest refresh supplement date changed")
    checks.check(latest_refresh.get("row_count") == 20, "latest refresh supplement row count changed")
    checks.check(latest_refresh.get("current_query_count") == 11, "latest refresh supplement query count changed")
    checks.check(
        latest_refresh.get("positive_public_code_artifact_rows") == 0,
        "latest refresh supplement found positive artifacts unexpectedly",
    )
    checks.check(latest_refresh.get("source_policy_rows_closed") == 0, "latest refresh supplement overclosed rows")
    checks.check(
        latest_refresh.get("latest_external_probe_date_checked")
        == public_refresh_latest.get("latest_external_probe_date_checked")
        == "2026-06-21",
        "latest external probe date changed",
    )
    checks.check(
        latest_refresh.get("latest_external_probe_count")
        == public_refresh_latest.get("latest_external_probe_count")
        == 9,
        "latest external probe count changed",
    )
    checks.check(
        latest_refresh.get("latest_external_probe_positive_public_code_artifact_rows")
        == public_refresh_latest.get("latest_external_probe_positive_public_code_artifact_rows")
        == 0,
        "latest external probe found positive artifacts unexpectedly",
    )
    checks.check(
        latest_refresh.get("latest_external_probe_source_policy_rows_closed")
        == public_refresh_latest.get("latest_external_probe_source_policy_rows_closed")
        == 0,
        "latest external probe overclosed source-policy rows",
    )
    checks.check(
        latest_refresh.get("latest_external_probe_access_limited_count")
        == public_refresh_latest.get("latest_external_probe_access_limited_count")
        == 4,
        "latest external probe access-limit count changed",
    )
    checks.check(
        latest_refresh.get("latest_external_probe_global_absence_proved")
        == public_refresh_latest.get("latest_external_probe_global_absence_proved")
        is False,
        "latest external probe overproved global absence",
    )
    checks.check(
        latest_refresh.get("latest_external_probe_source_policy_reopen_triggered")
        == public_refresh_latest.get("latest_external_probe_source_policy_reopen_triggered")
        is False,
        "latest external probe unexpectedly reopened source policy",
    )
    monitor = audit.get("reopen_condition_monitor", {})
    checks.check(
        monitor.get("status")
        == reopen_monitor.get("status")
        == "reopen_conditions_monitored_no_positive_source_artifact_source_policy_open",
        "reopen monitor status changed",
    )
    checks.check(monitor.get("date_checked") == "2026-06-20", "reopen monitor date changed")
    checks.check(monitor.get("row_count") == 20, "reopen monitor row count changed")
    checks.check(monitor.get("unable_to_reproduce_rows") == 20, "reopen monitor unable rows changed")
    checks.check(
        monitor.get("source_policy_rows_total") == reopen_monitor.get("source_policy_rows_total") == 20,
        "reopen monitor source-policy total changed",
    )
    checks.check(monitor.get("positive_public_code_artifact_rows") == 0, "reopen monitor public positive rows changed")
    checks.check(monitor.get("local_positive_reopen_artifact_rows") == 0, "reopen monitor local positive rows changed")
    checks.check(monitor.get("source_policy_reopen_triggered") is False, "reopen monitor reopened rows")
    checks.check(monitor.get("source_policy_rows_closed") == 0, "reopen monitor overclosed rows")
    checks.check(
        monitor.get("source_policy_closed") is False
        and reopen_monitor.get("source_policy_closed") is False,
        "reopen monitor overclaimed source-policy closure",
    )
    checks.check(
        monitor.get("source_policy_open") is True
        and reopen_monitor.get("source_policy_open") is True,
        "reopen monitor lost source-policy open marker",
    )
    checks.check(
        monitor.get("source_policy_closed_ratio") == reopen_monitor.get("source_policy_closed_ratio") == "0/20",
        "reopen monitor source-policy closed ratio changed",
    )
    checks.check(monitor.get("terminal_suite_count") == reopen_monitor.get("terminal_suite_count") == 2, "reopen monitor terminal suite count changed")
    checks.check(
        monitor.get("terminal_reopen_conditions")
        == reopen_monitor.get("terminal_reopen_conditions")
        == expected_terminal_reopen_conditions,
        "reopen monitor terminal conditions changed",
    )
    checks.check(
        monitor.get("source_artifact_sha256") == reopen_monitor.get("source_artifact_sha256"),
        "reopen monitor source artifact digest map not propagated",
    )
    checks.check(
        monitor.get("source_artifact_digest_policy")
        == reopen_monitor.get("source_artifact_digest_policy"),
        "reopen monitor source artifact digest policy not propagated",
    )
    checks.check(
        monitor.get("local_scan_digest") == reopen_monitor.get("local_scan_digest"),
        "reopen monitor local scan digest not propagated",
    )
    checks.check(
        monitor.get("monitor_evidence_digest") == reopen_monitor.get("monitor_evidence_digest"),
        "reopen monitor evidence digest not propagated",
    )
    checks.check(latest_refresh.get("source_policy_rows_promoted") == 0, "latest refresh supplement overpromoted rows")
    command_freeze = audit.get("b4_command_preflight_freeze", {})
    oc6_reopen = audit.get("oc6_source_equivalent_reopen_readiness_audit", {})
    checks.check(
        oc6_reopen.get("status")
        == oc6_reopen_readiness.get("status")
        == "oc6_reopen_conditions_monitored_no_positive_source_equivalent_artifact",
        "OC6 reopen readiness status changed",
    )
    checks.check(oc6_reopen.get("date_checked") == "2026-06-20", "OC6 reopen readiness date changed")
    checks.check(
        oc6_reopen.get("row_count") == 20
        and oc6_reopen.get("tfe_rows") == 16
        and oc6_reopen.get("vp_rows") == 4
        and oc6_reopen.get("unable_to_reproduce_rows") == 20,
        "OC6 reopen readiness row accounting changed",
    )
    checks.check(
        oc6_reopen.get("public_code_available_rows") == 0
        and oc6_reopen.get("candidate_runner_available_rows") == 20
        and oc6_reopen.get("candidate_runner_source_policy_equivalent_rows") == 0,
        "OC6 reopen source-equivalence accounting changed",
    )
    checks.check(
        oc6_reopen.get("positive_public_code_artifact_rows") == 0
        and oc6_reopen.get("local_positive_reopen_artifact_rows") == 0
        and oc6_reopen.get("source_policy_reopen_triggered") is False,
        "OC6 reopen positive-artifact accounting changed",
    )
    checks.check(
        oc6_reopen.get("source_policy_rows_closed") == 0
        and oc6_reopen.get("source_policy_rows_promoted") == 0
        and oc6_reopen.get("oc6_can_close_now") is False
        and oc6_reopen.get("performs_new_public_code_search") is False,
        "OC6 reopen readiness overclosed rows or performed a new search",
    )
    checks.check(
        oc6_reopen.get("latest_external_probe_date_checked")
        == oc6_reopen_readiness.get("latest_external_probe_date_checked")
        == "2026-06-21"
        and oc6_reopen.get("latest_external_probe_count")
        == oc6_reopen_readiness.get("latest_external_probe_count")
        == 9
        and oc6_reopen.get("latest_external_probe_positive_public_code_artifact_rows")
        == oc6_reopen_readiness.get(
            "latest_external_probe_positive_public_code_artifact_rows"
        )
        == 0,
        "OC6 reopen readiness latest-probe counts not propagated",
    )
    checks.check(
        oc6_reopen.get("latest_external_probe_source_policy_rows_closed")
        == oc6_reopen_readiness.get("latest_external_probe_source_policy_rows_closed")
        == 0
        and oc6_reopen.get("latest_external_probe_access_limited_count")
        == oc6_reopen_readiness.get("latest_external_probe_access_limited_count")
        == 4
        and oc6_reopen.get("latest_external_probe_global_absence_proved")
        == oc6_reopen_readiness.get("latest_external_probe_global_absence_proved")
        is False
        and oc6_reopen.get("latest_external_probe_source_policy_reopen_triggered")
        == oc6_reopen_readiness.get("latest_external_probe_source_policy_reopen_triggered")
        is False
        and oc6_reopen.get("latest_external_probe_rows_by_suite")
        == oc6_reopen_readiness.get("latest_external_probe_rows_by_suite")
        == {"tfe2026_original_pendulum": 5, "vp2024_velocity_partitioning": 4},
        "OC6 reopen readiness latest-probe closure boundary not propagated",
    )
    checks.check(
        oc6_reopen.get("reopen_readiness_digest")
        == oc6_reopen_readiness.get("reopen_readiness_digest"),
        "OC6 reopen readiness digest not propagated",
    )
    command_freeze = audit.get("b4_command_preflight_freeze", {})
    checks.check(
        command_freeze.get("status")
        == b4_command_freeze.get("status")
        == "command_preflight_frozen_not_authorized_not_run_not_promoted",
        "B4 command preflight freeze status changed",
    )
    checks.check(command_freeze.get("date_checked") == "2026-06-20", "B4 command freeze date changed")
    checks.check(command_freeze.get("ready_command_count") == 13, "B4 command freeze command count changed")
    checks.check(
        command_freeze.get("unique_mapped_ra_hi_rows") == 20,
        "B4 command freeze mapped row count changed",
    )
    checks.check(
        command_freeze.get("declared_row_reference_total") == 32
        and command_freeze.get("traced_row_reference_total") == 32
        and command_freeze.get("declared_vs_traced_mismatch_count") == 0,
        "B4 command freeze row-reference traceability changed",
    )
    checks.check(
        command_freeze.get("expected_artifacts_existing_now") == 21
        and command_freeze.get("expected_artifact_count") == 21,
        "B4 command freeze expected-artifact count changed",
    )
    checks.check(
        command_freeze.get("commands_executed_by_freeze") is False,
        "B4 command freeze executed commands",
    )
    checks.check(
        command_freeze.get("source_policy_rows_closed") == 0
        and command_freeze.get("source_policy_rows_total") == 40,
        "B4 command freeze overclosed source-policy rows",
    )
    checks.check(
        command_freeze.get("command_freeze_sha256")
        == b4_command_freeze.get("command_freeze_sha256"),
        "B4 command freeze digest not propagated",
    )
    schema_audit = audit.get("b4_expected_output_schema_audit", {})
    checks.check(
        schema_audit.get("status")
        == b4_expected_output_schema_audit.get("status")
        == "expected_outputs_schema_ready_not_authorized_not_run_not_promoted",
        "B4 expected-output schema audit status changed",
    )
    checks.check(schema_audit.get("date_checked") == "2026-06-20", "schema audit date changed")
    checks.check(schema_audit.get("command_count") == 13, "schema audit command count changed")
    checks.check(
        schema_audit.get("expected_artifact_count") == 21
        and schema_audit.get("artifacts_existing_now") == 21
        and schema_audit.get("artifacts_sha256_match_freeze") == 21,
        "schema audit artifact/hash accounting changed",
    )
    checks.check(
        schema_audit.get("csv_parseable_artifacts") == 13
        and schema_audit.get("json_summary_parseable_artifacts") == 8
        and schema_audit.get("schema_ready_commands") == 13,
        "schema audit parseability/readiness changed",
    )
    checks.check(
        schema_audit.get("commands_executed_by_audit") is False
        and schema_audit.get("source_policy_rows_closed") == 0
        and schema_audit.get("promotion_ready_rows") == 0,
        "schema audit overexecuted or overpromoted rows",
    )
    checks.check(
        schema_audit.get("expected_output_schema_audit_sha256")
        == b4_expected_output_schema_audit.get("expected_output_schema_audit_sha256"),
        "schema audit digest not propagated",
    )
    expected_schema_traceability = {
        "commands_with_shell_command": 13,
        "commands_with_expected_output_path": 13,
        "commands_with_expected_summary_path": 8,
        "commands_without_expected_summary_path": 5,
        "commands_with_existing_expected_output": 13,
        "commands_with_existing_expected_summary": 8,
        "source_policy_execution_invoked": False,
        "commands_executed_by_audit": False,
    }
    checks.check(
        schema_audit.get("command_traceability")
        == audit.get("b4_expected_output_schema_command_traceability")
        == b4_expected_output_schema_audit.get("command_traceability")
        == expected_schema_traceability,
        "schema audit command traceability not propagated to archive gap audit",
    )
    promotion_blocker_audit = audit.get(
        "b4_expected_output_promotion_readiness_blocker_audit", {}
    )
    checks.check(
        promotion_blocker_audit.get("status")
        == b4_expected_output_promotion_readiness_blocker_audit.get("status")
        == "expected_outputs_schema_ready_but_promotion_blocked",
        "B4 expected-output promotion blocker audit status changed",
    )
    checks.check(
        promotion_blocker_audit.get("date_checked") == "2026-06-20",
        "promotion blocker audit date changed",
    )
    checks.check(
        promotion_blocker_audit.get("command_count") == 13
        and promotion_blocker_audit.get("schema_ready_command_count") == 13
        and promotion_blocker_audit.get("promotion_ready_command_count") == 0,
        "promotion blocker command readiness accounting changed",
    )
    checks.check(
        promotion_blocker_audit.get("command_row_reference_total") == 32
        and promotion_blocker_audit.get("unique_mapped_ra_hi_row_count") == 20
        and promotion_blocker_audit.get("unique_mapped_ra_hi_rows_not_promoted") == 20,
        "promotion blocker mapped-row accounting changed",
    )
    checks.check(
        promotion_blocker_audit.get("summary_source_policy_rows_closed_total") == 0
        and promotion_blocker_audit.get("summary_source_policy_rows_promoted_total") == 0
        and promotion_blocker_audit.get("commands_with_schema_ready_but_promotion_blocked")
        == 13,
        "promotion blocker closure/promoted accounting changed",
    )
    checks.check(
        promotion_blocker_audit.get("source_policy_rows_closed") == 0
        and promotion_blocker_audit.get("promotion_ready_rows") == 0
        and promotion_blocker_audit.get("b4_can_close_now") is False
        and promotion_blocker_audit.get("b7_can_close_now") is False,
        "promotion blocker overclosed rows or B4/B7",
    )
    checks.check(
        promotion_blocker_audit.get("promotion_readiness_digest")
        == b4_expected_output_promotion_readiness_blocker_audit.get(
            "promotion_readiness_digest"
        ),
        "promotion blocker digest not propagated",
    )
    guarded_refusal = audit.get(
        "b4_guarded_driver_refusal_boundary_audit_20260621_summary", {}
    )
    checks.check(
        guarded_refusal.get("status")
        == b4_guarded_refusal.get("status")
        == "guarded_driver_refusal_boundary_static_proved_not_executed",
        "guarded driver refusal boundary status changed",
    )
    checks.check(
        guarded_refusal.get("no_opt_in_refusal_proved_static") is True
        and guarded_refusal.get("wrong_approval_refusal_proved_static") is True
        and guarded_refusal.get("refusal_exit_code") == 2,
        "guarded driver refusal proof changed",
    )
    checks.check(
        guarded_refusal.get("pre_guard_command_count") == 0
        and guarded_refusal.get("refusal_branch_source_policy_command_count") == 0
        and guarded_refusal.get("post_guard_source_policy_command_count") == 13,
        "guarded driver refusal command boundary changed",
    )
    checks.check(
        guarded_refusal.get("ra_allow_source_policy_1e_4_command_count") == 5
        and guarded_refusal.get("hi_execute_command_count") == 8
        and guarded_refusal.get("driver_commands_match_packet") is True,
        "guarded driver refusal command mix changed",
    )
    checks.check(
        guarded_refusal.get("driver_invoked_by_audit") is False
        and guarded_refusal.get("source_policy_execution_invoked") is False
        and guarded_refusal.get("source_policy_rows_closed_by_audit") == 0
        and guarded_refusal.get("submission_ready") is False,
        "guarded driver refusal audit overexecuted or overpromoted",
    )
    checks.check(
        guarded_refusal.get("marker")
        == b4_guarded_refusal.get("marker")
        == "b4_guarded_driver_refusal_boundary_audit_20260621=True/True/2/0/13/False/False",
        "guarded driver refusal marker changed",
    )

    source_rows = audit.get("source_policy_rows", {})
    closure = audit.get("closure_conditions", {})
    expected_tfe_source_policy_execution_preflight_tuple = (
        f"{tfe_preflight.get('status')}/"
        f"{tfe_preflight.get('ready_to_execute_source_policy_now')}/"
        f"{tfe_preflight.get('can_promote_any_tfe_source_policy_row_now')}/"
        f"{tfe_preflight.get('execution_block_count')}/"
        f"{tfe_preflight.get('explicit_user_opt_in_required')}"
    )
    expected_tfe_runner_contract_preflight_tuple = (
        f"{runner_preflight.get('status')}/"
        f"{runner_preflight.get('callable_contract_count')}/"
        f"{runner_preflight.get('entrypoint_count')}/"
        f"{runner_preflight.get('candidate_backed_contract_count')}/"
        f"{runner_preflight.get('source_policy_rows_completed')}/"
        f"{runner_preflight.get('source_policy_execution_block_count')}"
    )
    expected_output_schema_audit_tuple = (
        f"{schema_audit.get('status')}/"
        f"{schema_audit.get('command_count')}/"
        f"{schema_audit.get('expected_artifact_count')}/"
        f"{schema_audit.get('artifacts_sha256_match_freeze')}/"
        f"{schema_audit.get('schema_ready_commands')}/"
        f"{schema_audit.get('commands_executed_by_audit')}/"
        f"{schema_audit.get('source_policy_rows_closed')}/"
        f"{schema_audit.get('promotion_ready_rows')}"
    )
    checks.check(audit.get("full_archive_ready_now") is False, "top-level archive readiness overpromoted")
    checks.check(
        audit.get("full_source_policy_runner_package_ready") is False,
        "top-level full source-policy runner package readiness overpromoted",
    )
    checks.check(
        audit.get("can_use_current_archive_as_full_source_policy_runner_archive") is False
        and audit.get("can_use_current_archive_as_full_source_policy_runner_archive")
        == closure.get("can_use_current_archive_as_full_source_policy_runner_archive"),
        "top-level current-archive usability alias missing or stale",
    )
    checks.check(
        audit.get("current_archive_usable_as_full_source_policy_runner_archive")
        == audit.get("can_use_current_archive_as_full_source_policy_runner_archive")
        is False,
        "top-level current-archive usability aliases disagree",
    )
    checks.check(audit.get("source_policy_closed") is False, "top-level source policy overclosed")
    checks.check(audit.get("source_policy_closed_ratio") == "0/40", "top-level source-policy ratio changed")
    checks.check(
        audit.get("source_policy_rows_closed") == source_rows.get("closed") == 0,
        "top-level source-policy closed rows changed",
    )
    checks.check(
        audit.get("source_policy_rows_promoted") == source_rows.get("promoted") == 0,
        "top-level source-policy promoted rows changed",
    )
    checks.check(
        audit.get("source_policy_rows_total") == source_rows.get("total") == 40,
        "top-level source-policy total rows changed",
    )
    checks.check(
        audit.get("remaining_source_policy_rows_to_close")
        == closure.get("remaining_source_policy_rows_to_close")
        == 40,
        "top-level remaining source-policy rows changed",
    )
    checks.check(
        audit.get("terminal_unable_to_reproduce_rows")
        == closure.get("terminal_unable_to_reproduce_rows")
        == 20,
        "top-level terminal-unable rows changed",
    )
    checks.check(
        audit.get("attempted_not_reproducible_rows")
        == source_rows.get("attempted_not_reproducible")
        == 20,
        "top-level attempted-not-reproducible rows changed",
    )
    checks.check(
        audit.get("tfe_source_policy_execution_preflight")
        == expected_tfe_source_policy_execution_preflight_tuple
        == "terminal_no_public_code_self_reproduction_attempted_not_promoted/False/False/4/False",
        "top-level TFE source-policy execution preflight alias missing or stale",
    )
    checks.check(
        audit.get("tfe_source_policy_execution_preflight_status")
        == tfe_preflight.get("status")
        == "terminal_no_public_code_self_reproduction_attempted_not_promoted",
        "top-level TFE source-policy execution preflight status alias missing or stale",
    )
    checks.check(
        audit.get("tfe_runner_contract_preflight")
        == audit.get("oc12_archive_tfe_preflight")
        == expected_tfe_runner_contract_preflight_tuple
        == "contract_entrypoints_callable_candidate_backed_source_policy_open/3/3/3/0/4",
        "top-level TFE runner contract preflight alias missing or stale",
    )
    checks.check(
        audit.get("tfe_runner_contract_preflight_status")
        == runner_preflight.get("status")
        == "contract_entrypoints_callable_candidate_backed_source_policy_open",
        "top-level TFE runner contract preflight status alias missing or stale",
    )
    checks.check(
        audit.get("expected_output_schema_audit") == "PASS",
        "top-level expected-output schema audit alias missing or stale",
    )
    checks.check(
        audit.get("expected_output_schema_audit_status")
        == schema_audit.get("status")
        == "expected_outputs_schema_ready_not_authorized_not_run_not_promoted",
        "top-level expected-output schema audit status alias missing or stale",
    )
    checks.check(
        audit.get("expected_output_schema_audit_tuple")
        == expected_output_schema_audit_tuple
        == "expected_outputs_schema_ready_not_authorized_not_run_not_promoted/13/21/21/13/False/0/0",
        "top-level expected-output schema audit tuple alias missing or stale",
    )
    checks.check(
        audit.get("b4_guarded_driver_refusal_boundary_audit_20260621")
        == "True/True/2/0/13/False/False",
        "top-level B4 guarded driver refusal boundary alias missing or stale",
    )
    checks.check(
        audit.get("oc6_reopen_latest_external_probe")
        == "2026-06-21/9/0/0/4/False/False",
        "top-level OC6 reopen latest external probe alias missing or stale",
    )
    checks.check(
        audit.get("ra_hi_rows_requiring_authorized_closeout_or_new_artifact")
        == closure.get("ra_hi_rows_requiring_authorized_closeout_or_new_artifact")
        == 20,
        "top-level RA/HI authorized-closeout row count changed",
    )
    checks.check(audit.get("ready_command_count") == 13, "top-level ready command count changed")
    checks.check(audit.get("ready_command_mapped_external_rows") == 20, "top-level mapped row count changed")
    checks.check(audit.get("opt_in_required_command_count") == 13, "top-level opt-in command count changed")
    checks.check(
        audit.get("opt_in_required_mapped_external_rows") == 20,
        "top-level opt-in mapped row count changed",
    )
    checks.check(audit.get("execution_authorized") is False, "top-level execution authorization changed")
    checks.check(
        audit.get("required_user_approval_statement")
        == "I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json.",
        "top-level exact approval statement changed",
    )
    checks.check(
        audit.get("guarded_execution_driver") == "run_b4_source_policy_after_opt_in.sh"
        and audit.get("driver_requires_exact_approval") is True
        and audit.get("driver_does_not_authorize_execution") is True,
        "top-level guarded driver boundary changed",
    )
    checks.check(audit.get("submission_ready") is False, "top-level submission readiness overclaimed")
    checks.check(
        audit.get("safe_without_b4_opt_in_count") == 4
        and audit.get("opt_in_required_action_count") == 1,
        "top-level action counts changed",
    )
    checks.check(
        audit.get("source_policy_execution_allowed_now") is False
        and audit.get("exact_b4_opt_in_required_for_execution") is True,
        "top-level execution permission boundary changed",
    )
    checks.check(
        audit.get("terminal_reopen_conditions") == expected_terminal_reopen_conditions,
        "top-level terminal reopen conditions changed",
    )
    checks.check(
        audit.get("terminal_reopen_conditions")
        == audit.get("reopen_condition_monitor", {}).get("terminal_reopen_conditions"),
        "top-level terminal reopen conditions drifted from monitor summary",
    )
    safe_actions = {
        item.get("id"): item
        for item in audit.get("safe_next_actions_without_b4_opt_in", [])
        if isinstance(item, dict)
    }
    opt_in_actions = {
        item.get("id"): item
        for item in audit.get("opt_in_required_actions", [])
        if isinstance(item, dict)
    }
    checks.check(
        set(safe_actions)
        == {
            "rebuild_read_only_audit_chain",
            "rerun_read_only_validators",
            "keep_narrowed_archive_provenance_only",
            "monitor_reopen_conditions",
        },
        "safe next-action ids changed",
    )
    checks.check(
        all(item.get("allowed_without_b4_opt_in") is True for item in safe_actions.values())
        and all(item.get("does_not_execute_source_policy_commands") is True for item in safe_actions.values()),
        "safe next-action boundary overpermits execution",
    )
    checks.check(
        safe_actions.get("rebuild_read_only_audit_chain", {}).get("representative_scripts")
        == [
            "build_full_source_policy_row_provenance_audit.py",
            "build_full_source_policy_runner_archive_gap_audit.py",
            "build_objective_completion_audit.py",
            "cmame_submission_review_agent.py",
            "build_cmame_reproducibility_package_manifest.py",
            "sync_submission_artifact_manifest_boundary.py",
        ],
        "read-only rebuild representative scripts changed",
    )
    checks.check(
        safe_actions.get("rerun_read_only_validators", {}).get("representative_scripts")
        == [
            "validate_full_source_policy_runner_archive_gap_audit.py",
            "validate_objective_completion_audit.py",
            "validate_submission_artifact_manifest_boundary_sync.py",
            "validate_paper_package.py",
            "../validate_pipeline_outputs.py",
        ],
        "read-only validator representative scripts changed",
    )
    checks.check(
        safe_actions.get("keep_narrowed_archive_provenance_only", {}).get("current_archive_use")
        == "narrowed_claim_replay_and_audit_provenance_only",
        "narrowed archive safe-use action changed",
    )
    checks.check(
        safe_actions.get("monitor_reopen_conditions", {}).get("reopen_conditions")
        == expected_terminal_reopen_conditions,
        "monitor reopen-condition action changed",
    )
    checks.check(
        set(opt_in_actions) == {"authorized_b4_ra_hi_source_policy_execution"},
        "opt-in required action ids changed",
    )
    expected_safe_action_ids = [
        "rebuild_read_only_audit_chain",
        "rerun_read_only_validators",
        "keep_narrowed_archive_provenance_only",
        "monitor_reopen_conditions",
    ]
    expected_opt_in_action_ids = ["authorized_b4_ra_hi_source_policy_execution"]
    checks.check(
        audit.get("safe_action_ids") == expected_safe_action_ids
        and audit.get("opt_in_action_ids") == expected_opt_in_action_ids,
        "top-level action-id aliases changed",
    )
    checks.check(
        audit.get("next_safe_actions") == audit.get("safe_next_actions_without_b4_opt_in")
        and audit.get("next_safe_action_ids") == audit.get("safe_action_ids") == expected_safe_action_ids,
        "top-level next-safe-action aliases changed",
    )
    opt_in_action = opt_in_actions.get("authorized_b4_ra_hi_source_policy_execution", {})
    checks.check(opt_in_action.get("allowed_without_b4_opt_in") is False, "B4 execution action overpermitted")
    checks.check(
        opt_in_action.get("requires_exact_user_approval_statement") is True
        and opt_in_action.get("exact_required_user_approval_statement")
        == "I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json.",
        "B4 opt-in action exact-approval boundary changed",
    )
    checks.check(
        opt_in_action.get("guarded_execution_driver") == "run_b4_source_policy_after_opt_in.sh"
        and opt_in_action.get("driver_requires_exact_approval") is True
        and opt_in_action.get("driver_does_not_authorize_execution") is True,
        "B4 opt-in action guarded-driver boundary changed",
    )
    checks.check(
        opt_in_action.get("command_count") == 13
        and opt_in_action.get("mapped_external_rows") == 20
        and opt_in_action.get("post_execution_promotion_required") is True,
        "B4 opt-in action command/promotion counts changed",
    )
    action_boundary = audit.get("action_boundary", {})
    checks.check(
        action_boundary.get("safe_without_b4_opt_in_count") == 4
        and action_boundary.get("opt_in_required_action_count") == 1
        and action_boundary.get("source_policy_execution_allowed_now") is False
        and action_boundary.get("exact_b4_opt_in_required_for_execution") is True,
        "top-level action boundary counts or execution permission changed",
    )
    checks.check(
        action_boundary.get("safe_without_b4_opt_in_count")
        == audit.get("safe_without_b4_opt_in_count")
        and action_boundary.get("opt_in_required_action_count")
        == audit.get("opt_in_required_action_count")
        and action_boundary.get("source_policy_execution_allowed_now")
        == audit.get("source_policy_execution_allowed_now")
        and action_boundary.get("exact_b4_opt_in_required_for_execution")
        == audit.get("exact_b4_opt_in_required_for_execution"),
        "top-level action boundary aliases are stale",
    )
    checks.check(
        action_boundary.get("safe_action_ids") == audit.get("safe_action_ids")
        and action_boundary.get("opt_in_action_ids") == audit.get("opt_in_action_ids"),
        "top-level action boundary action-id aliases are stale",
    )
    checks.check(
        action_boundary.get("required_user_approval_statement")
        == "I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json."
        and action_boundary.get("guarded_execution_driver") == "run_b4_source_policy_after_opt_in.sh"
        and action_boundary.get("opt_in_required_command_count") == 13
        and action_boundary.get("opt_in_required_mapped_external_rows") == 20,
        "top-level action boundary B4 command metadata changed",
    )
    objective_boundary = audit.get("objective_archive_blocker_boundary", {})
    expected_objective_blocking_ids = ["OC4", "OC6", "OC12"]
    expected_objective_status_by_id = {
        "OC4": "open",
        "OC6": "partial",
        "OC12": "partial",
    }
    expected_objective_next_actions_by_id = {
        "OC4": (
            "RA/HI can only close through exact B4 opt-in authorized closeout or a new "
            "source-policy promotion artifact; TFE/VP remain unable-to-reproduce/not-promoted"
        ),
        "OC6": (
            "keep TFE source-policy terminal/unable-to-reproduce unless a new public or "
            "source-code-equivalent TFE implementation artifact appears"
        ),
        "OC12": (
            "promote the partial local runner package to a full source-policy runner "
            "archive after OC4/OC6 close"
        ),
    }
    expected_archive_closure_status_by_id = {
        blocker_id: closure_matrix.get(matrix_id, {}).get("current_status")
        for blocker_id, matrix_id in {
            "OC4": "OC4_source_policy_reproduction_rows",
            "OC6": "OC6_tfe_source_policy_runner",
            "OC12": "OC12_full_source_policy_runner_archive",
        }.items()
    }
    expected_archive_effect_by_id = {
        blocker_id: closure_matrix.get(matrix_id, {}).get("archive_effect")
        for blocker_id, matrix_id in {
            "OC4": "OC4_source_policy_reproduction_rows",
            "OC6": "OC6_tfe_source_policy_runner",
            "OC12": "OC12_full_source_policy_runner_archive",
        }.items()
    }
    expected_closure_allowed_by_id = {blocker_id: False for blocker_id in expected_objective_blocking_ids}
    checks.check(
        objective_boundary.get("schema") == "objective-archive-blocker-boundary-v1"
        and objective_boundary.get("status") == "full_archive_blocked_by_objective_blockers",
        "objective archive blocker boundary schema/status changed",
    )
    checks.check(
        objective_boundary.get("blocking_ids")
        == objective_completion.get("blocking_ids")
        == expected_objective_blocking_ids,
        "objective archive blocker ids drifted from objective completion audit",
    )
    checks.check(
        objective_boundary.get("blocker_status_by_id")
        == objective_completion.get("blocker_status_by_id")
        == expected_objective_status_by_id,
        "objective archive blocker status map drifted from objective completion audit",
    )
    checks.check(
        objective_boundary.get("blocker_next_actions_by_id")
        == objective_completion.get("blocker_next_actions_by_id")
        == expected_objective_next_actions_by_id,
        "objective archive blocker next-action map drifted from objective completion audit",
    )
    checks.check(
        objective_boundary.get("archive_closure_status_by_id")
        == expected_archive_closure_status_by_id
        == {
            "OC4": "open",
            "OC6": "partial_terminal_not_promoted",
            "OC12": "partial_narrowed_replay_ready_full_archive_open",
        },
        "objective archive closure-status map drifted from closure matrix",
    )
    checks.check(
        objective_boundary.get("archive_effect_by_id")
        == expected_archive_effect_by_id
        == {
            "OC4": "blocks_full_archive_primary_use",
            "OC6": "blocks_tfe_rows_from_full_archive_promotion",
            "OC12": "current_archive_is_narrowed_claim_provenance_only",
        },
        "objective archive effect map drifted from closure matrix",
    )
    checks.check(
        objective_boundary.get("closure_allowed_by_id") == expected_closure_allowed_by_id,
        "objective archive closure-allowed map overpermits closure",
    )
    checks.check(
        objective_boundary.get("source_policy_closed_ratio")
        == objective_completion.get("source_policy_closed_ratio")
        == audit.get("source_policy_closed_ratio")
        == "0/40",
        "objective archive source-policy closed ratio drifted",
    )
    checks.check(
        objective_boundary.get("full_archive_ready_now") is False
        and objective_boundary.get("current_archive_usable_as_full_source_policy_runner_archive") is False
        and objective_boundary.get("source_policy_execution_allowed_now") is False
        and objective_boundary.get("exact_b4_opt_in_required_for_execution") is True,
        "objective archive readiness/execution permission boundary changed",
    )
    checks.check(
        objective_boundary.get("safe_action_ids") == expected_safe_action_ids
        and objective_boundary.get("opt_in_action_ids") == expected_opt_in_action_ids,
        "objective archive action ids drifted",
    )
    archive_required_to_close = audit.get("archive_blocker_required_to_close_by_id", {})
    archive_safe_next_actions = audit.get("archive_blocker_safe_next_actions_by_id", {})
    archive_opt_in_actions = audit.get("archive_blocker_opt_in_required_actions_by_id", {})
    checks.check(
        audit.get("blocker_required_to_close_by_id") == archive_required_to_close
        and audit.get("blocker_safe_next_actions_by_id") == archive_safe_next_actions
        and audit.get("blocker_opt_in_required_actions_by_id") == archive_opt_in_actions,
        "archive blocker closure/action aliases are stale",
    )
    checks.check(
        set(archive_required_to_close)
        == set(archive_safe_next_actions)
        == set(archive_opt_in_actions)
        == set(expected_objective_blocking_ids),
        "archive blocker closure/action map keys changed",
    )
    checks.check(
        objective_boundary.get("blocker_required_to_close_by_id")
        == archive_required_to_close
        == objective_completion.get("blocker_required_to_close_by_id"),
        "archive required-to-close map drifted from objective completion audit",
    )
    checks.check(
        objective_boundary.get("blocker_safe_next_actions_by_id")
        == archive_safe_next_actions
        == objective_completion.get("blocker_safe_next_actions_by_id"),
        "archive safe-next-action map drifted from objective completion audit",
    )
    checks.check(
        objective_boundary.get("blocker_opt_in_required_actions_by_id")
        == archive_opt_in_actions
        == objective_completion.get("blocker_opt_in_required_actions_by_id"),
        "archive opt-in action map drifted from objective completion audit",
    )
    expected_oc4_schema_traceability = {
        "commands_with_shell_command": 13,
        "commands_with_expected_output_path": 13,
        "commands_with_expected_summary_path": 8,
        "commands_without_expected_summary_path": 5,
        "commands_with_existing_expected_output": 13,
        "commands_with_existing_expected_summary": 8,
        "source_policy_execution_invoked": False,
        "commands_executed_by_audit": False,
    }
    checks.check(
        archive_required_to_close.get("OC4", {}).get("current_source_policy_closed_ratio")
        == audit.get("source_policy_closed_ratio")
        == "0/40"
        and archive_required_to_close.get("OC4", {}).get(
            "authorized_ra_hi_closeout_route", {}
        ).get("requires_exact_b4_opt_in")
        is True
        and archive_required_to_close.get("OC4", {}).get(
            "authorized_ra_hi_closeout_route", {}
        ).get("opt_in_required_command_count")
        == 13
        and archive_required_to_close.get("OC4", {}).get(
            "authorized_ra_hi_closeout_route", {}
        ).get("opt_in_required_mapped_external_rows")
        == 20
        and archive_required_to_close.get("OC4", {}).get(
            "authorized_ra_hi_closeout_route", {}
        ).get("expected_output_schema_command_traceability")
        == expected_oc4_schema_traceability
        and archive_required_to_close.get("OC4", {}).get(
            "authorized_ra_hi_closeout_route", {}
        ).get("expected_output_schema_command_traceability_tuple")
        == "13/13/8/5/13/8/False/False",
        "OC4 archive required-to-close route changed",
    )
    oc4_guarded_refusal = archive_required_to_close.get("OC4", {}).get(
        "authorized_ra_hi_closeout_route", {}
    ).get("guarded_driver_refusal_boundary_20260621", {})
    checks.check(
        oc4_guarded_refusal.get("status")
        == b4_guarded_refusal.get("status")
        == "guarded_driver_refusal_boundary_static_proved_not_executed"
        and oc4_guarded_refusal.get("no_opt_in_refusal_proved_static") is True
        and oc4_guarded_refusal.get("wrong_approval_refusal_proved_static") is True
        and oc4_guarded_refusal.get("refusal_exit_code") == 2
        and oc4_guarded_refusal.get("pre_guard_command_count") == 0
        and oc4_guarded_refusal.get("refusal_branch_source_policy_command_count") == 0
        and oc4_guarded_refusal.get("post_guard_source_policy_command_count") == 13
        and oc4_guarded_refusal.get("driver_invoked_by_audit") is False
        and oc4_guarded_refusal.get("source_policy_execution_invoked") is False
        and oc4_guarded_refusal.get("submission_ready") is False
        and oc4_guarded_refusal.get("marker")
        == "b4_guarded_driver_refusal_boundary_audit_20260621=True/True/2/0/13/False/False",
        "OC4 guarded driver refusal boundary changed",
    )
    checks.check(
        archive_required_to_close.get("OC6", {}).get("contract_preflight_status")
        == "contract_entrypoints_callable_candidate_backed_source_policy_open"
        and archive_required_to_close.get("OC6", {}).get("effective_execution_block_count")
        == 4
        and archive_required_to_close.get("OC6", {}).get("latest_external_probe", {}).get(
            "date"
        )
        == "2026-06-21"
        and archive_required_to_close.get("OC6", {}).get("latest_external_probe", {}).get(
            "positive_public_code_artifact_rows"
        )
        == 0,
        "OC6 archive required-to-close route changed",
    )
    oc6_external_required = archive_required_to_close.get("OC6", {}).get(
        "external_source_artifact_recheck_20260621", {}
    )
    checks.check(
        oc6_external_required.get("date") == oc6_external_recheck.get("date_checked") == "2026-06-21"
        and oc6_external_required.get("query_count") == oc6_external_recheck.get("query_count") == 10
        and oc6_external_required.get("positive_public_code_artifact_rows") == 0
        and oc6_external_required.get("source_code_equivalent_artifact_rows") == 0
        and oc6_external_required.get("source_policy_rows_closed_by_recheck") == 0
        and oc6_external_required.get("source_policy_reopen_triggered") is False
        and oc6_external_required.get("global_absence_proved") is False
        and oc6_external_required.get("submission_ready") is False,
        "OC6 external source-artifact recheck not propagated to required-to-close route",
    )
    checks.check(
        audit.get("oc6_external_source_artifact_recheck_20260621")
        == "2026-06-21/10/0/0/0/False/False",
        "top-level OC6 external source-artifact recheck alias missing or stale",
    )
    oc6_publisher_required = archive_required_to_close.get("OC6", {}).get(
        "publisher_artifact_availability_20260621", {}
    )
    checks.check(
        oc6_publisher_required.get("date") == oc6_publisher_availability.get("date_checked") == "2026-06-21"
        and oc6_publisher_required.get("official_article_checked") is True
        and oc6_publisher_required.get("source_artifact_signal_count") == 0
        and oc6_publisher_required.get("positive_public_code_artifact_rows") == 0
        and oc6_publisher_required.get("source_code_equivalent_artifact_rows") == 0
        and oc6_publisher_required.get("source_policy_rows_closed_by_publisher_audit") == 0
        and oc6_publisher_required.get("source_policy_reopen_triggered") is False
        and oc6_publisher_required.get("global_absence_proved") is False
        and oc6_publisher_required.get("submission_ready") is False,
        "OC6 publisher artifact availability not propagated to required-to-close route",
    )
    checks.check(
        audit.get("oc6_tfe_publisher_artifact_availability_20260621")
        == "2026-06-21/True/0/0/0/0/False/False",
        "top-level OC6 publisher artifact availability alias missing or stale",
    )
    publisher_summary = audit.get("oc6_tfe_publisher_artifact_availability_20260621_summary", {})
    checks.check(
        publisher_summary.get("status") == oc6_publisher_availability.get("status")
        and publisher_summary.get("date_checked") == oc6_publisher_availability.get("date_checked")
        and publisher_summary.get("official_article_checked") is True
        and publisher_summary.get("source_artifact_signal_count") == 0
        and publisher_summary.get("positive_public_code_artifact_rows") == 0
        and publisher_summary.get("source_code_equivalent_artifact_rows") == 0
        and publisher_summary.get("source_policy_rows_closed_by_publisher_audit") == 0
        and publisher_summary.get("source_policy_reopen_triggered") is False
        and publisher_summary.get("global_absence_proved") is False
        and publisher_summary.get("submission_ready") is False,
        "OC6 publisher artifact availability summary changed",
    )
    oc6_request_required = archive_required_to_close.get("OC6", {}).get(
        "source_equivalent_artifact_request_packet_20260621", {}
    )
    checks.check(
        oc6_request_required.get("status")
        == oc6_source_equivalent_request_packet.get("status")
        == "request_packet_ready_not_sent_no_source_policy_closure"
        and oc6_request_required.get("date_prepared")
        == oc6_source_equivalent_request_packet.get("date_prepared")
        == "2026-06-21"
        and oc6_request_required.get("request_ready") is True
        and oc6_request_required.get("request_sent") is False
        and oc6_request_required.get("requested_artifact_count") == 7
        and oc6_request_required.get("corresponding_author_email") == "ekanshchat96@vt.edu"
        and oc6_request_required.get("source_policy_rows_closed_by_packet") == 0
        and oc6_request_required.get("source_policy_reopen_triggered") is False
        and oc6_request_required.get("global_absence_proved") is False
        and oc6_request_required.get("submission_ready") is False,
        "OC6 source-equivalent artifact request packet not propagated to required-to-close route",
    )
    checks.check(
        audit.get("oc6_tfe_source_equivalent_artifact_request_packet_20260621")
        == "True/False/7/0/False/False",
        "top-level OC6 source-equivalent artifact request packet alias missing or stale",
    )
    request_summary = audit.get(
        "oc6_tfe_source_equivalent_artifact_request_packet_20260621_summary",
        {},
    )
    checks.check(
        request_summary.get("status")
        == "request_packet_ready_not_sent_no_source_policy_closure"
        and request_summary.get("date_prepared") == "2026-06-21"
        and request_summary.get("request_ready") is True
        and request_summary.get("request_sent") is False
        and request_summary.get("requested_artifact_count") == 7
        and request_summary.get("corresponding_author_email") == "ekanshchat96@vt.edu"
        and request_summary.get("source_policy_rows_closed_by_packet") == 0
        and request_summary.get("source_policy_reopen_triggered") is False
        and request_summary.get("global_absence_proved") is False
        and request_summary.get("submission_ready") is False,
        "OC6 source-equivalent artifact request packet summary changed",
    )
    checks.check(
        archive_required_to_close.get("OC12", {}).get(
            "current_archive_usable_as_full_source_policy_runner_archive"
        )
        is False
        and archive_required_to_close.get("OC12", {}).get(
            "full_source_policy_runner_package_ready"
        )
        is False
        and archive_required_to_close.get("OC12", {}).get("upstream_blockers")
        == ["OC4", "OC6"]
        and archive_required_to_close.get("OC12", {}).get("action_boundary")
        == audit.get("action_boundary"),
        "OC12 archive required-to-close route changed",
    )
    checks.check(
        all(archive_safe_next_actions.get(req_id) == audit.get("safe_next_actions_without_b4_opt_in")
            for req_id in expected_objective_blocking_ids)
        and archive_opt_in_actions.get("OC4") == audit.get("opt_in_required_actions")
        and archive_opt_in_actions.get("OC6") == []
        and archive_opt_in_actions.get("OC12") == audit.get("opt_in_required_actions"),
        "archive blocker action maps changed",
    )
    checks.check(
        objective_completion.get("objective_complete") is False
        and objective_completion.get("submission_ready") is False
        and objective_completion.get("status") == "not_complete_submission_standard_open",
        "objective completion audit unexpectedly overclosed",
    )
    checks.check(closure.get("full_archive_ready_now") is False, "archive overpromoted")
    checks.check(closure.get("full_row_provenance_preflight_ready") is True, "provenance preflight not carried")
    checks.check(closure.get("full_row_provenance_promotion_ready") is False, "provenance promotion overclaimed")
    checks.check(
        closure.get("expected_outputs_schema_ready_but_promotion_blocked") is True
        and closure.get("expected_output_promotion_ready_command_count") == 0
        and closure.get("expected_output_promotion_blocked_command_count") == 13,
        "closure expected-output promotion blocker summary changed",
    )
    checks.check(
        closure.get("row_provenance_handoff_authorized") is False
        and closure.get("row_provenance_handoff_commands_not_run") is True,
        "closure row-provenance handoff authorization boundary changed",
    )
    checks.check(
        closure.get("row_provenance_handoff_driver_requires_exact_approval") is True
        and closure.get("row_provenance_handoff_driver_does_not_authorize_execution") is True,
        "closure row-provenance handoff driver guard changed",
    )
    checks.check(closure.get("can_claim_full_source_policy_reproduction_now") is False, "overclaims full source")
    checks.check(closure.get("can_use_current_archive_as_full_source_policy_runner_archive") is False, "overuses current archive")
    checks.check(closure.get("can_submit_current_runner_package_as_primary_source_package") is False, "overpromotes primary package")
    checks.check(closure.get("remaining_source_policy_rows_to_close") == 40, "remaining row count changed")
    checks.check(closure.get("ra_hi_rows_requiring_authorized_closeout_or_new_artifact") == 20, "RA/HI remaining rows changed")
    checks.check(closure.get("terminal_unable_to_reproduce_rows") == 20, "terminal unable rows changed")
    checks.check(closure.get("tfe_source_policy_preflight_ready_now") is False, "closure overclaims TFE preflight ready")
    checks.check(
        closure.get("tfe_source_policy_preflight_can_promote_now") is False,
        "closure overclaims TFE preflight promotion",
    )
    checks.check(
        closure.get("tfe_source_policy_preflight_execution_block_count") == 4,
        "closure TFE execution block count changed",
    )
    checks.check(
        closure.get("tfe_source_policy_preflight_effective_execution_block_count") == 4
        and closure.get("tfe_source_policy_preflight_terminal_nonpromoted_block_count") == 2,
        "closure TFE effective/terminal block counts changed",
    )
    checks.check(
        closure.get("tfe_source_policy_preflight_requires_opt_in") is False,
        "closure TFE opt-in marker changed",
    )
    checks.check(
        closure.get("tfe_source_policy_preflight_reopen_condition")
        == "new_public_or_source_code_equivalent_tfe_implementation_artifact",
        "closure TFE reopen condition changed",
    )
    checks.check(
        closure.get("oc6_source_equivalent_reopen_ready_now") is False
        and closure.get("oc6_positive_public_code_artifact_rows") == 0
        and closure.get("oc6_local_positive_reopen_artifact_rows") == 0
        and closure.get("oc6_source_equivalent_candidate_rows") == 0
        and closure.get("oc6_source_policy_rows_closed") == 0,
        "closure OC6 reopen readiness summary changed",
    )
    checks.check(
        closure.get("tfe_runner_contract_preflight_status")
        == "contract_entrypoints_callable_candidate_backed_source_policy_open",
        "closure TFE runner contract preflight status changed",
    )
    checks.check(
        closure.get("tfe_runner_contract_preflight_entrypoints") == "3/3"
        and closure.get("tfe_runner_contract_preflight_candidate_backed") == "3/3",
        "closure TFE runner contract preflight callable/candidate counts changed",
    )
    checks.check(
        closure.get("tfe_runner_contract_preflight_source_policy_rows_completed") == 0
        and closure.get("tfe_runner_contract_preflight_execution_blocks") == 4,
        "closure TFE runner contract preflight row/block counts changed",
    )
    checks.check(
        closure.get("tfe_runner_contract_preflight_safe_use")
        == "runner_contract_preflight_only_not_source_policy_reproduction"
        and closure.get("tfe_runner_contract_preflight_all_non_equivalent") is True,
        "closure TFE runner contract preflight boundary changed",
    )
    checks.check(closure.get("source_policy_handoff_ready_now") is True, "handoff ready marker changed")
    checks.check(closure.get("source_policy_handoff_authorized_now") is False, "handoff authorization marker changed")
    checks.check(audit.get("source_policy_execution_invoked") is False, "audit invoked source-policy execution")
    checks.check(audit.get("heavy_numerical_run_invoked") is False, "audit invoked heavy run")
    checks.check(audit.get("run_v047_invoked") is False, "audit invoked run_v047")
    checks.check(audit.get("v048_runner_invoked") is False, "audit invoked v048")

    for token in [
        "Status: `full_source_policy_runner_archive_not_ready_source_policy_open`.",
        "Full archive ready now: `False`.",
        "Full source-policy runner package ready: `False`.",
        "Source-policy rows closed/promoted/attempted-not-reproducible/total: `0/0/20/40`.",
        "Row provenance preflight complete: `40/40`.",
        "Row provenance is promotion: `False`.",
        "Terminal unable-to-reproduce rows: `20`.",
        "Top-level TFE source-policy execution preflight alias: `terminal_no_public_code_self_reproduction_attempted_not_promoted/False/False/4/False`.",
        "TFE source-policy preflight status/ready/promote/blocks/opt-in: `terminal_no_public_code_self_reproduction_attempted_not_promoted/False/False/4/False`.",
        "TFE source-policy contract accounting raw/non-heavy-terminal/effective-execution/source-rows: `6/2/4/0`.",
        "TFE source-policy preflight reopen condition: `new_public_or_source_code_equivalent_tfe_implementation_artifact`.",
        "Top-level TFE runner contract preflight alias: `contract_entrypoints_callable_candidate_backed_source_policy_open/3/3/3/0/4`.",
        "Top-level OC12 archive TFE preflight alias: `contract_entrypoints_callable_candidate_backed_source_policy_open/3/3/3/0/4`.",
        "TFE runner contract preflight status/entrypoints/candidate-backed/source-rows/execution-blocks: `contract_entrypoints_callable_candidate_backed_source_policy_open/3/3/3/0/4`.",
        "TFE runner contract preflight safe-use/non-equivalent/submission-ready: `runner_contract_preflight_only_not_source_policy_reproduction/True/False`.",
        "Latest public-code refresh supplement: `public_code_refresh_20260620_no_positive_new_source_artifact_rows_remain_unable_to_reproduce` on `2026-06-20`; rows/queries/positive/closed/promoted `20/11/0/0/0`.",
        "Latest external public-code probe: `2026-06-21/9/0/0/4/False/False`.",
        "Reopen-condition monitor: `reopen_conditions_monitored_no_positive_source_artifact_source_policy_open` on `2026-06-20`; rows/unable/public-positive/local-positive/reopened/closed/closed-bool/open-bool/ratio `20/20/0/0/False/0/False/True/0/20`.",
        "Reopen-condition monitor terminal conditions: `tfe2026_original_pendulum=new_public_or_source_code_equivalent_tfe_implementation_artifact; vp2024_velocity_partitioning=new_distinct_public_vp2024_velocity_partitioning_code_path`.",
        f"Reopen-condition monitor digests: local-scan `{reopen_monitor.get('local_scan_digest')}`; evidence `{reopen_monitor.get('monitor_evidence_digest')}`.",
        "OC6 source-equivalent reopen-readiness audit: `oc6_reopen_conditions_monitored_no_positive_source_equivalent_artifact` on `2026-06-20`; rows TFE/VP/total/unable/public-code/candidate/source-equivalent/positive/local-positive/reopened/closed `16/4/20/20/0/20/0/0/0/False/0`.",
        "OC6 source-equivalent reopen-readiness latest external probe: `2026-06-21/9/0/0/4/False/False`.",
        "OC6 external source-artifact recheck 20260621: `no_positive_external_source_artifact_found_reopen_conditions_remain_open`; date/query/positive/source-equivalent/closed/reopened/global-absence `2026-06-21/10/0/0/0/False/False`.",
        "OC6 TFE publisher artifact availability 20260621: `publisher_article_checked_no_code_or_supplement_source_artifact_found`; date/official/signal/positive/source-equivalent/closed/reopened/global-absence `2026-06-21/True/0/0/0/0/False/False`.",
        "OC6 TFE source-equivalent artifact request packet 20260621: `request_packet_ready_not_sent_no_source_policy_closure`; ready/sent/requested/closed/reopened/submission-ready `True/False/7/0/False/False`.",
        "B4 command preflight freeze: `command_preflight_frozen_not_authorized_not_run_not_promoted` on `2026-06-20`; commands/unique-rows/row-refs/mismatches/artifacts/executed/closed `13/20/32/0/21/False/0`.",
        "Top-level expected-output schema audit alias: `PASS` / `expected_outputs_schema_ready_not_authorized_not_run_not_promoted/13/21/21/13/False/0/0`.",
        "B4 expected-output schema audit: `expected_outputs_schema_ready_not_authorized_not_run_not_promoted` on `2026-06-20`; commands/artifacts/hash-match/csv/json/schema-ready/executed/closed `13/21/21/13/8/13/False/0`.",
        "B4 expected-output schema command traceability shell/output/summary/no-summary/existing-output/existing-summary: `13/13/8/5/13/8`.",
        "B4 expected-output promotion-readiness blocker audit: `expected_outputs_schema_ready_but_promotion_blocked` on `2026-06-20`; commands/schema-ready/promotion-ready/row-refs/unique-rows/not-promoted/summary-closed/promoted/blocked `13/13/0/32/20/20/0/0/13`.",
        "B4 guarded driver refusal boundary audit 20260621: `True/True/2/0/13/False/False`.",
        "RA/HI rows requiring authorized closeout or new artifact: `20`.",
        "B4 ready commands/mapped rows: `13/20`.",
        "Source-policy execution handoff traceability: unique RA/HI rows `20/20`; row refs `32/32`; mismatches/terminal/closed/promotion-ready `0/0/0/0`.",
        "B4 handoff status/authorized: `source_policy_execution_handoff_ready_not_authorized_not_run/False`.",
        "Row provenance handoff exact approval/driver: `I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json./run_b4_source_policy_after_opt_in.sh/True/True/13/20/20`.",
        "Safe next actions without B4 opt-in: `4`.",
        "Opt-in required actions: `1`.",
        "Source-policy execution allowed now: `False`.",
        "Exact B4 opt-in required for execution: `True`.",
        "Source-policy execution invoked: `False`.",
        "B4 execution invoked: `False`.",
        "Exact B4 approval statement: `I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json.`.",
        "Current archive usable as full source-policy runner archive: `False`.",
        "OC12 blocker/status/closure decision: `OC12/partial/remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready`.",
        "OC12 current archive use/full-archive-usable/primary-allowed: `narrowed_claim_replay_and_audit_provenance_only/False/False`.",
        "OC12 dependency blockers/closure allowed now: `['OC4', 'OC6']/False`.",
        "OC12 narrowed/local runner/full package ready: `True/True/False`.",
        "Archive closure matrix rows/blockers: `3/OC4,OC6,OC12`.",
        "Objective archive blocker status by id: `{'OC4': 'open', 'OC6': 'partial', 'OC12': 'partial'}`.",
        "Objective archive blocker next actions by id: `{'OC4': 'RA/HI can only close through exact B4 opt-in authorized closeout or a new source-policy promotion artifact; TFE/VP remain unable-to-reproduce/not-promoted'",
        "Objective archive blocker effects by id: `{'OC4': 'blocks_full_archive_primary_use', 'OC6': 'blocks_tfe_rows_from_full_archive_promotion', 'OC12': 'current_archive_is_narrowed_claim_provenance_only'}`.",
        "Archive blocker required-to-close by id: `{'OC4':",
        "Archive blocker safe next actions by id: `{'OC4':",
        "Archive blocker opt-in required actions by id: `{'OC4':",
        "## Objective Blocker Matrix",
        "This audit records OC12 full source-policy archive status. It does not close the global objective blockers.",
        f"`{EXPECTED_BLOCKER_OPEN_TOKEN}`",
        f"`{EXPECTED_BLOCKER_CLOSURE_DECISION_TOKEN}`",
        f"`{EXPECTED_BLOCKER_CLOSURE_ALLOWED_TOKEN}`",
        "`OC4_source_policy_reproduction_rows`",
        "`OC6_tfe_source_policy_runner`",
        "`OC12_full_source_policy_runner_archive`",
        "`blocks_full_archive_primary_use`",
        "`blocks_tfe_rows_from_full_archive_promotion`",
        "`current_archive_is_narrowed_claim_provenance_only`",
        "`tfe2026_original_pendulum`",
        "`vp2024_velocity_partitioning`",
        "`new_public_or_source_code_equivalent_tfe_implementation_artifact`",
        "`new_distinct_public_vp2024_velocity_partitioning_code_path`",
        "`rebuild_read_only_audit_chain`",
        "`rerun_read_only_validators`",
        "`keep_narrowed_archive_provenance_only`",
        "`monitor_reopen_conditions`",
        "`authorized_b4_ra_hi_source_policy_execution`",
        "Top-level next safe action ids: `rebuild_read_only_audit_chain,rerun_read_only_validators,keep_narrowed_archive_provenance_only,monitor_reopen_conditions`.",
    ]:
        checks.check(token in text, f"markdown missing token: {token}")

    if checks.errors:
        print("full source-policy runner archive gap audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("full source-policy runner archive gap audit validation: PASS")
    print("source_policy_closed=0/40")
    print("source_policy_rows_promoted=0")
    print("attempted_not_reproducible_rows=20")
    print("terminal_unable_to_reproduce_rows=20")
    print("oc6_reopen_latest_external_probe=2026-06-21/9/0/0/4/False/False")
    print("oc6_external_source_artifact_recheck_20260621=2026-06-21/10/0/0/0/False/False")
    print("oc6_tfe_publisher_artifact_availability_20260621=2026-06-21/True/0/0/0/0/False/False")
    print("oc6_tfe_source_equivalent_artifact_request_packet_20260621=True/False/7/0/False/False")
    print("ra_hi_rows_requiring_authorized_closeout_or_new_artifact=20")
    print("opt_in_required_command_count=13")
    print("opt_in_required_mapped_external_rows=20")
    print("safe_next_actions_without_b4_opt_in=4")
    print("opt_in_required_actions=1")
    print("safe_action_ids=rebuild_read_only_audit_chain,rerun_read_only_validators,keep_narrowed_archive_provenance_only,monitor_reopen_conditions")
    print("opt_in_action_ids=authorized_b4_ra_hi_source_policy_execution")
    print("source_policy_execution_allowed_now=False")
    print("exact_b4_opt_in_required_for_execution=True")
    print("source_policy_execution_invoked=False")
    print("driver_does_not_authorize_execution=True")
    print("expected_output_schema_audit=PASS")
    print("b4_guarded_driver_refusal_boundary_audit_20260621=True/True/2/0/13/False/False")
    print("tfe_runner_contract_preflight=contract_entrypoints_callable_candidate_backed_source_policy_open/3/3/3/0/4")
    print("full_archive_ready_now=False")
    print("full_source_policy_runner_package_ready=False")
    print(f"oc12_closure_decision={audit.get('oc12_closure_decision')}")
    print(f"oc12_blocker_open={audit.get('oc12_blocker_open')}")
    print(
        "current_archive_usable_as_full_source_policy_runner_archive="
        f"{audit.get('current_archive_usable_as_full_source_policy_runner_archive')}"
    )
    print(f"safe_current_use={audit.get('safe_current_use')}")
    print(
        "primary_submission_package_allowed="
        f"{audit.get('primary_submission_package_allowed')}"
    )
    print(
        "oc12_archive_use_full_usable_primary_allowed="
        f"{audit.get('safe_current_use')}/"
        f"{audit.get('current_archive_usable_as_full_source_policy_runner_archive')}/"
        f"{audit.get('primary_submission_package_allowed')}"
    )
    print(
        "oc12_dependency_blockers_closure_allowed="
        f"{','.join(audit.get('dependency_blockers', []))}/"
        f"{audit.get('oc12_closure_allowed_now')}"
    )
    print(EXPECTED_BLOCKER_OPEN_TOKEN)
    print(EXPECTED_BLOCKER_CLOSURE_DECISION_TOKEN)
    print(EXPECTED_BLOCKER_CLOSURE_ALLOWED_TOKEN)
    print("submission_ready=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
