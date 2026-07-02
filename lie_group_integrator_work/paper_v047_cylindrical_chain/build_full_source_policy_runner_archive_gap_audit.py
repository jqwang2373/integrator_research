#!/usr/bin/env python3
"""Build the full source-policy runner archive gap audit.

This read-only audit separates the current runnable narrowed/replay package
from the still-missing full source-policy runner archive.  It is a packaging
gate, not a numerical execution gate: it records which source-policy rows are
terminal unable-to-reproduce/not-promoted and which rows still need authorized
RA/HI closeout or a new promotion artifact.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json"
OUT_MD = PAPER / "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.md"
BLOCKER_IDS = ["OC4", "OC6", "OC12"]
BLOCKER_OPEN_BY_ID = {"OC4": True, "OC6": True, "OC12": True}
BLOCKER_CLOSURE_DECISION_BY_ID = {
    "OC4": "remain_open_ready_for_authorized_execution_not_executed_not_promoted",
    "OC6": "remain_open_no_positive_source_equivalent_artifact",
    "OC12": "remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready",
}
BLOCKER_CLOSURE_ALLOWED_BY_ID = {"OC4": False, "OC6": False, "OC12": False}


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def blocker_token(values: dict[str, Any]) -> str:
    return ",".join(f"{blocker_id}:{values[blocker_id]}" for blocker_id in BLOCKER_IDS)


def handoff_boundary(provenance: dict[str, Any]) -> dict[str, Any]:
    handoff = provenance.get("source_policy_execution_handoff", {})
    return {
        "status": handoff.get("status"),
        "execution_authorized": handoff.get("execution_authorized"),
        "commands_not_run_by_handoff": handoff.get("commands_not_run_by_handoff"),
        "exact_required_user_approval_statement": handoff.get(
            "exact_required_user_approval_statement"
        ),
        "guarded_execution_driver": handoff.get("guarded_execution_driver"),
        "driver_requires_exact_approval": handoff.get("driver_requires_exact_approval"),
        "driver_does_not_authorize_execution": handoff.get(
            "driver_does_not_authorize_execution"
        ),
        "opt_in_required_command_count": handoff.get("opt_in_required_command_count"),
        "opt_in_required_mapped_external_rows": handoff.get(
            "opt_in_required_mapped_external_rows"
        ),
        "terminal_unable_to_reproduce_rows": handoff.get("terminal_unable_to_reproduce_rows"),
    }


def tfe_execution_preflight_boundary(tfe_gap: dict[str, Any]) -> dict[str, Any]:
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


def tfe_runner_contract_preflight_boundary(certificate: dict[str, Any]) -> dict[str, Any]:
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


def main() -> None:
    manifest = read_json(PAPER / "CMAME_REPRODUCIBILITY_PACKAGE_MANIFEST.json")
    runner_centered = read_json(PAPER / "CMAME_RUNNER_CENTERED_REPRODUCIBILITY_AUDIT.json")
    narrowed = read_json(PAPER / "CMAME_NARROWED_REPRODUCIBILITY_PACKAGE_AUDIT.json")
    narrowed_archive = read_json(PAPER / "CMAME_NARROWED_REPRO_CODE_ARCHIVE_MANIFEST.json")
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
    ra_hi = read_json(PAPER / "RA_HI_SOURCE_POLICY_PROMOTION_BLOCKER_MATRIX.json")
    tfe_gap = read_json(PAPER / "TFE_DAE_RUNNER_CONTRACT_GAP_AUDIT.json")
    tfe_runner_contract_preflight = read_json(PAPER / "TFE_RUNNER_CONTRACT_PREFLIGHT_CERTIFICATE.json")
    public_refresh = read_json(PAPER / "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.json")
    public_refresh_latest = read_json(PAPER / "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.json")
    reopen_monitor = read_json(PAPER / "SOURCE_POLICY_REOPEN_CONDITION_MONITOR_20260620.json")
    self_attempt = read_json(PAPER / "SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json")

    manifest_summary = manifest.get("summary", {})
    source_rows_total = int(b4_ledger.get("source_policy_rows_total") or 0)
    source_rows_closed = int(b4_ledger.get("source_policy_rows_closed") or 0)
    terminal_unable_rows = int(b4_ledger.get("source_policy_rows_unable_to_reproduce") or 0)
    ra_hi_open_rows = int(ra_hi.get("future_promotion_requires_authorized_execution_or_new_artifact_rows") or 0)
    ready_commands = int(b4_packet.get("ready_command_count") or 0)
    ready_command_rows = int(b4_packet.get("ready_command_mapped_external_rows") or 0)
    row_provenance_handoff = handoff_boundary(provenance)
    b4_command_traceability_summary = b4_handoff.get("command_row_traceability", {}).get(
        "summary",
        {},
    )
    tfe_preflight = tfe_execution_preflight_boundary(tfe_gap)
    tfe_runner_preflight = tfe_runner_contract_preflight_boundary(tfe_runner_contract_preflight)

    terminal_suites = []
    for suite_id in ["tfe2026_original_pendulum", "vp2024_velocity_partitioning"]:
        suite_rows = [
            row
            for row in self_attempt.get("rows", [])
            if isinstance(row, dict) and row.get("suite_id") == suite_id
        ]
        terminal_suites.append(
            {
                "suite_id": suite_id,
                "row_count": len(suite_rows),
                "unable_to_reproduce_rows": sum(1 for row in suite_rows if row.get("unable_to_reproduce") is True),
                "source_policy_rows_closed": sum(1 for row in suite_rows if row.get("source_policy_closed") is True),
                "reopen_condition": (
                    "new_public_or_source_code_equivalent_tfe_implementation_artifact"
                    if suite_id == "tfe2026_original_pendulum"
                    else "new_distinct_public_vp2024_velocity_partitioning_code_path"
                ),
            }
        )

    full_archive_ready_now = (
        source_rows_total == 40
        and source_rows_closed == 40
        and runner_centered.get("full_source_policy_runner_package_ready") is True
        and manifest.get("submission_ready") is True
    )
    archive_closure_matrix = [
        {
            "id": "OC4_source_policy_reproduction_rows",
            "objective_blocker": "OC4",
            "requirement": "Close apples-to-apples external source-policy reproduction rows before any full source-policy runner archive claim.",
            "current_status": "open",
            "source_policy_rows_closed": source_rows_closed,
            "source_policy_rows_total": source_rows_total,
            "terminal_unable_to_reproduce_rows": terminal_unable_rows,
            "rows_requiring_authorized_closeout_or_new_artifact": ra_hi_open_rows,
            "ready_command_count": ready_commands,
            "ready_command_mapped_external_rows": ready_command_rows,
            "command_traceability_summary": b4_command_traceability_summary,
            "execution_authorized": b4_packet.get("execution_invoked_by_packet") is True,
            "exact_approval_required": b4_packet.get("required_user_approval_statement"),
            "closure_allowed_now": False,
            "required_evidence_to_close": [
                "authorized RA/HI source-policy closeout under the exact B4 opt-in or a new source-policy promotion artifact",
                "post-execution promotion validator records source-policy rows as closed",
                "work/precision rows bind error, order, runtime, Newton, and source-policy labels to the same promoted rows",
            ],
            "archive_effect": "blocks_full_archive_primary_use",
        },
        {
            "id": "OC6_tfe_source_policy_runner",
            "objective_blocker": "OC6",
            "requirement": "Keep original TFE pendulum source-policy rows terminal/unpromoted unless a public or source-code-equivalent runner artifact appears.",
            "current_status": "partial_terminal_not_promoted",
            "source_policy_rows_completed": tfe_preflight.get("source_policy_rows_completed"),
            "terminal_nonpromoted_contract_block_count": tfe_preflight.get(
                "terminal_nonpromoted_contract_block_count"
            ),
            "effective_execution_contract_block_count": tfe_preflight.get(
                "effective_missing_contract_block_count"
            ),
            "ready_to_execute_source_policy_now": tfe_preflight.get(
                "ready_to_execute_source_policy_now"
            ),
            "can_promote_any_tfe_source_policy_row_now": tfe_preflight.get(
                "can_promote_any_tfe_source_policy_row_now"
            ),
            "runner_contract_preflight_status": tfe_runner_preflight.get("status"),
            "runner_contract_preflight_entrypoints": (
                f"{tfe_runner_preflight.get('callable_contract_count')}/"
                f"{tfe_runner_preflight.get('entrypoint_count')}"
            ),
            "runner_contract_preflight_candidate_backed": (
                f"{tfe_runner_preflight.get('candidate_backed_contract_count')}/"
                f"{tfe_runner_preflight.get('entrypoint_count')}"
            ),
            "runner_contract_preflight_source_policy_rows_completed": tfe_runner_preflight.get(
                "source_policy_rows_completed"
            ),
            "runner_contract_preflight_execution_blocks": tfe_runner_preflight.get(
                "source_policy_execution_block_count"
            ),
            "runner_contract_preflight_execution_block_matrix_summary": (
                tfe_runner_preflight.get("source_policy_execution_block_matrix_summary")
            ),
            "runner_contract_preflight_safe_use": tfe_runner_preflight.get("safe_current_use"),
            "runner_contract_preflight_all_non_equivalent": tfe_runner_preflight.get(
                "all_non_equivalent"
            ),
            "source_equivalent_request_packet_status": oc6_source_equivalent_request_packet.get(
                "status"
            ),
            "source_equivalent_request_ready": oc6_source_equivalent_request_packet.get(
                "request_ready"
            ),
            "source_equivalent_request_sent": oc6_source_equivalent_request_packet.get(
                "request_sent"
            ),
            "source_equivalent_requested_artifact_count": oc6_source_equivalent_request_packet.get(
                "requested_artifact_count"
            ),
            "reopen_condition": tfe_preflight.get("reopen_condition"),
            "closure_allowed_now": False,
            "required_evidence_to_close": [
                "new public or source-code-equivalent TFE implementation artifact",
                "monolithic absolute-coordinate source-policy DAE runner contract",
                "TFE m=1/m=2/m=3, Newmark-beta, and trapezoidal source-policy method-runner contracts",
                "Gauss6/FullVA absolute-coordinate source-pendulum DAE runner contract",
            ],
            "archive_effect": "blocks_tfe_rows_from_full_archive_promotion",
        },
        {
            "id": "OC12_full_source_policy_runner_archive",
            "objective_blocker": "OC12",
            "requirement": "Promote the narrowed/replay package into a full source-policy runner archive only after OC4 and OC6 are closed.",
            "current_status": "partial_narrowed_replay_ready_full_archive_open",
            "narrowed_reproducibility_package_ready": narrowed.get(
                "narrowed_claim_reproducibility_package_ready"
            ),
            "local_runner_centered_candidate_ready": runner_centered.get(
                "local_runner_centered_candidate_ready"
            ),
            "full_source_policy_runner_package_ready": runner_centered.get(
                "full_source_policy_runner_package_ready"
            ),
            "current_archive_usable_as_full_source_policy_runner_archive": False,
            "primary_submission_package_allowed": manifest_summary.get(
                "minimal_submission_code_dependency_primary_allowed"
            ),
            "upstream_blockers": ["OC4", "OC6"],
            "safe_current_package_use": manifest_summary.get(
                "minimal_submission_code_dependency_safe_use"
            ),
            "closure_allowed_now": False,
            "required_evidence_to_close": [
                "OC4 source-policy rows closed",
                "OC6 TFE source-policy runner boundary closed or remains terminal with an accepted target-scope change",
                "full source-policy runner archive manifest marked ready",
                "primary submission package allowed by reproducibility manifest",
            ],
            "archive_effect": "current_archive_is_narrowed_claim_provenance_only",
        },
    ]
    safe_next_actions_without_b4_opt_in = [
        {
            "id": "rebuild_read_only_audit_chain",
            "allowed_without_b4_opt_in": True,
            "does_not_execute_source_policy_commands": True,
            "description": (
                "Rebuild the read-only provenance, archive-gap, objective, review, "
                "runner-centered, manifest, and submission-manifest boundary audits "
                "after metadata-only changes."
            ),
            "representative_scripts": [
                "build_full_source_policy_row_provenance_audit.py",
                "build_full_source_policy_runner_archive_gap_audit.py",
                "build_objective_completion_audit.py",
                "cmame_submission_review_agent.py",
                "build_cmame_reproducibility_package_manifest.py",
                "sync_submission_artifact_manifest_boundary.py",
            ],
        },
        {
            "id": "rerun_read_only_validators",
            "allowed_without_b4_opt_in": True,
            "does_not_execute_source_policy_commands": True,
            "description": (
                "Run validators that check existing artifacts and execution boundaries, "
                "including the package and top-level pipeline validators."
            ),
            "representative_scripts": [
                "validate_full_source_policy_runner_archive_gap_audit.py",
                "validate_objective_completion_audit.py",
                "validate_submission_artifact_manifest_boundary_sync.py",
                "validate_paper_package.py",
                "../validate_pipeline_outputs.py",
            ],
        },
        {
            "id": "keep_narrowed_archive_provenance_only",
            "allowed_without_b4_opt_in": True,
            "does_not_execute_source_policy_commands": True,
            "description": (
                "Use the narrowed/replay archive only as provenance for the narrowed claim; "
                "do not present it as the full source-policy runner archive."
            ),
            "current_archive_use": "narrowed_claim_replay_and_audit_provenance_only",
        },
        {
            "id": "monitor_reopen_conditions",
            "allowed_without_b4_opt_in": True,
            "does_not_execute_source_policy_commands": True,
            "description": (
                "Keep the TFE and VP terminal rows open until new public code, author-provided "
                "code, or a source-equivalent implementation artifact appears."
            ),
            "reopen_conditions": {
                item["suite_id"]: item["reopen_condition"] for item in terminal_suites
            },
        },
    ]
    opt_in_required_actions = [
        {
            "id": "authorized_b4_ra_hi_source_policy_execution",
            "allowed_without_b4_opt_in": False,
            "requires_exact_user_approval_statement": True,
            "exact_required_user_approval_statement": b4_packet.get(
                "required_user_approval_statement"
            ),
            "guarded_execution_driver": row_provenance_handoff.get("guarded_execution_driver"),
            "driver_requires_exact_approval": row_provenance_handoff.get(
                "driver_requires_exact_approval"
            ),
            "driver_does_not_authorize_execution": row_provenance_handoff.get(
                "driver_does_not_authorize_execution"
            ),
            "command_count": ready_commands,
            "mapped_external_rows": ready_command_rows,
            "post_execution_promotion_required": True,
            "description": (
                "Run the prepared RA/HI source-policy commands only after the exact B4 "
                "approval phrase is supplied, then validate any post-execution promotion "
                "before closing source-policy rows."
            ),
        },
    ]
    terminal_reopen_conditions = {
        item["suite_id"]: item["reopen_condition"] for item in terminal_suites
    }
    safe_action_ids = [
        item["id"] for item in safe_next_actions_without_b4_opt_in if isinstance(item, dict)
    ]
    opt_in_action_ids = [
        item["id"] for item in opt_in_required_actions if isinstance(item, dict)
    ]
    archive_action_boundary = {
        "safe_without_b4_opt_in_count": len(safe_next_actions_without_b4_opt_in),
        "opt_in_required_action_count": len(opt_in_required_actions),
        "source_policy_execution_allowed_now": False,
        "exact_b4_opt_in_required_for_execution": True,
        "safe_action_ids": safe_action_ids,
        "opt_in_action_ids": opt_in_action_ids,
        "required_user_approval_statement": b4_packet.get(
            "required_user_approval_statement"
        ),
        "guarded_execution_driver": row_provenance_handoff.get("guarded_execution_driver"),
        "opt_in_required_command_count": ready_commands,
        "opt_in_required_mapped_external_rows": ready_command_rows,
    }
    source_policy_execution_invoked = any(
        [
            b4_packet.get("execution_invoked_by_packet") is True,
            b4_handoff.get("commands_not_run_by_handoff") is False,
            row_provenance_handoff.get("commands_not_run_by_handoff") is False,
            b4_command_freeze.get("commands_executed_by_freeze") is True,
            b4_expected_output_schema_audit.get("commands_executed_by_audit") is True,
            b4_guarded_refusal.get("source_policy_execution_invoked") is True,
        ]
    )
    guarded_refusal_boundary_tuple = (
        f"{b4_guarded_refusal.get('no_opt_in_refusal_proved_static')}/"
        f"{b4_guarded_refusal.get('wrong_approval_refusal_proved_static')}/"
        f"{b4_guarded_refusal.get('refusal_exit_code')}/"
        f"{b4_guarded_refusal.get('pre_guard_command_count')}/"
        f"{b4_guarded_refusal.get('post_guard_source_policy_command_count')}/"
        f"{b4_guarded_refusal.get('source_policy_execution_invoked')}/"
        f"{b4_guarded_refusal.get('submission_ready')}"
    )
    objective_blocking_ids = ["OC4", "OC6", "OC12"]
    archive_closure_by_objective_id = {
        item["objective_blocker"]: item
        for item in archive_closure_matrix
        if isinstance(item, dict)
    }
    objective_blocker_status_by_id = {
        "OC4": "open",
        "OC6": "partial",
        "OC12": "partial",
    }
    objective_blocker_next_actions_by_id = {
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
    expected_output_schema_command_traceability = (
        b4_expected_output_schema_audit.get("command_traceability") or {}
    )
    expected_output_schema_command_traceability_tuple = (
        f"{expected_output_schema_command_traceability.get('commands_with_shell_command')}/"
        f"{expected_output_schema_command_traceability.get('commands_with_expected_output_path')}/"
        f"{expected_output_schema_command_traceability.get('commands_with_expected_summary_path')}/"
        f"{expected_output_schema_command_traceability.get('commands_without_expected_summary_path')}/"
        f"{expected_output_schema_command_traceability.get('commands_with_existing_expected_output')}/"
        f"{expected_output_schema_command_traceability.get('commands_with_existing_expected_summary')}/"
        f"{expected_output_schema_command_traceability.get('commands_executed_by_audit')}/"
        f"{expected_output_schema_command_traceability.get('source_policy_execution_invoked')}"
    )
    archive_blocker_required_to_close_by_id = {
        "OC4": {
            "closure_condition": "close all 40 source-policy rows or introduce a new promotion artifact accepted by the source-policy ledger",
            "current_source_policy_closed_ratio": f"{source_rows_closed}/{source_rows_total}",
            "source_policy_rows_closed": source_rows_closed,
            "source_policy_rows_total": source_rows_total,
            "authorized_ra_hi_closeout_route": {
                "requires_exact_b4_opt_in": True,
                "execution_allowed_now": False,
                "execution_invoked": source_policy_execution_invoked,
                "guarded_execution_driver": row_provenance_handoff.get(
                    "guarded_execution_driver"
                ),
                "required_user_approval_statement": b4_packet.get(
                    "required_user_approval_statement"
                ),
                "opt_in_required_command_count": row_provenance_handoff.get(
                    "opt_in_required_command_count"
                ),
                "opt_in_required_mapped_external_rows": row_provenance_handoff.get(
                    "opt_in_required_mapped_external_rows"
                ),
                "ready_command_count": ready_commands,
                "ready_command_mapped_rows": ready_command_rows,
                "expected_output_schema_command_traceability": (
                    expected_output_schema_command_traceability
                ),
                "expected_output_schema_command_traceability_tuple": (
                    expected_output_schema_command_traceability_tuple
                ),
                "guarded_driver_refusal_boundary_20260621": {
                    "status": b4_guarded_refusal.get("status"),
                    "no_opt_in_refusal_proved_static": b4_guarded_refusal.get(
                        "no_opt_in_refusal_proved_static"
                    ),
                    "wrong_approval_refusal_proved_static": b4_guarded_refusal.get(
                        "wrong_approval_refusal_proved_static"
                    ),
                    "refusal_exit_code": b4_guarded_refusal.get("refusal_exit_code"),
                    "pre_guard_command_count": b4_guarded_refusal.get(
                        "pre_guard_command_count"
                    ),
                    "refusal_branch_source_policy_command_count": b4_guarded_refusal.get(
                        "refusal_branch_source_policy_command_count"
                    ),
                    "post_guard_source_policy_command_count": b4_guarded_refusal.get(
                        "post_guard_source_policy_command_count"
                    ),
                    "driver_invoked_by_audit": b4_guarded_refusal.get(
                        "driver_invoked_by_audit"
                    ),
                    "source_policy_execution_invoked": b4_guarded_refusal.get(
                        "source_policy_execution_invoked"
                    ),
                    "submission_ready": b4_guarded_refusal.get("submission_ready"),
                    "marker": b4_guarded_refusal.get("marker"),
                },
            },
            "current_handoff_status": b4_handoff.get("status"),
            "promotion_ready_rows": b4_command_traceability_summary.get(
                "promotion_ready_rows"
            ),
            "safe_current_disposition": (
                "keep source-policy rows unpromoted until authorized execution "
                "or a new source-policy promotion artifact exists"
            ),
        },
        "OC6": {
            "closure_condition": (
                "provide a source-equivalent TFE/pendulum DAE runner certificate "
                "or reopen only on a new public/source-code-equivalent TFE artifact"
            ),
            "tfe_runner_closed": tfe_runner_preflight.get("source_policy_closed"),
            "source_policy_rows_completed": tfe_runner_preflight.get(
                "source_policy_rows_completed"
            ),
            "contract_preflight_status": tfe_runner_preflight.get("status"),
            "candidate_backed_contract_count": tfe_runner_preflight.get(
                "candidate_backed_contract_count"
            ),
            "entrypoint_count": tfe_runner_preflight.get("entrypoint_count"),
            "callable_contract_count": tfe_runner_preflight.get("callable_contract_count"),
            "effective_execution_block_count": (
                tfe_gap.get("source_policy_execution_missing_contract_block_count")
                or tfe_preflight.get("effective_missing_contract_block_count")
            ),
            "effective_execution_blocks": (
                tfe_gap.get("source_policy_execution_missing_contract_blocks")
                or tfe_preflight.get("effective_missing_contract_blocks")
            ),
            "candidate_backed_non_equivalent_runner_blocks": tfe_gap.get(
                "candidate_backed_non_equivalent_runner_block_ids"
            ),
            "nonheavy_terminal_blocks": tfe_gap.get(
                "terminal_nonpromoted_contract_blocks"
            ),
            "reopen_condition": tfe_preflight.get("reopen_condition"),
            "latest_external_probe": {
                "date": public_refresh_latest.get("latest_external_probe_date_checked"),
                "probe_count": public_refresh_latest.get("latest_external_probe_count"),
                "positive_public_code_artifact_rows": public_refresh_latest.get(
                    "latest_external_probe_positive_public_code_artifact_rows"
                ),
                "source_policy_rows_closed": public_refresh_latest.get(
                    "latest_external_probe_source_policy_rows_closed"
                ),
                "access_limited_count": public_refresh_latest.get(
                    "latest_external_probe_access_limited_count"
                ),
                "global_absence_proved": public_refresh_latest.get(
                    "latest_external_probe_global_absence_proved"
                ),
                "reopen_triggered": public_refresh_latest.get(
                    "latest_external_probe_source_policy_reopen_triggered"
                ),
            },
            "external_source_artifact_recheck_20260621": {
                "date": oc6_external_recheck.get("date_checked"),
                "query_count": oc6_external_recheck.get("query_count"),
                "positive_public_code_artifact_rows": oc6_external_recheck.get(
                    "positive_public_code_artifact_rows"
                ),
                "source_code_equivalent_artifact_rows": oc6_external_recheck.get(
                    "source_code_equivalent_artifact_rows"
                ),
                "source_policy_rows_closed_by_recheck": oc6_external_recheck.get(
                    "source_policy_rows_closed_by_recheck"
                ),
                "source_policy_reopen_triggered": oc6_external_recheck.get(
                    "source_policy_reopen_triggered"
                ),
                "global_absence_proved": oc6_external_recheck.get("global_absence_proved"),
                "submission_ready": oc6_external_recheck.get("submission_ready"),
            },
            "publisher_artifact_availability_20260621": {
                "date": oc6_publisher_availability.get("date_checked"),
                "official_article_checked": oc6_publisher_availability.get(
                    "official_article_checked"
                ),
                "source_artifact_signal_count": oc6_publisher_availability.get(
                    "source_article", {}
                ).get("source_artifact_signal_count"),
                "positive_public_code_artifact_rows": oc6_publisher_availability.get(
                    "positive_public_code_artifact_rows"
                ),
                "source_code_equivalent_artifact_rows": oc6_publisher_availability.get(
                    "source_code_equivalent_artifact_rows"
                ),
                "source_policy_rows_closed_by_publisher_audit": oc6_publisher_availability.get(
                    "source_policy_rows_closed_by_publisher_audit"
                ),
                "source_policy_reopen_triggered": oc6_publisher_availability.get(
                    "source_policy_reopen_triggered"
                ),
                "global_absence_proved": oc6_publisher_availability.get(
                    "global_absence_proved"
                ),
                "submission_ready": oc6_publisher_availability.get("submission_ready"),
            },
            "source_equivalent_artifact_request_packet_20260621": {
                "status": oc6_source_equivalent_request_packet.get("status"),
                "date_prepared": oc6_source_equivalent_request_packet.get(
                    "date_prepared"
                ),
                "request_ready": oc6_source_equivalent_request_packet.get(
                    "request_ready"
                ),
                "request_sent": oc6_source_equivalent_request_packet.get("request_sent"),
                "requested_artifact_count": oc6_source_equivalent_request_packet.get(
                    "requested_artifact_count"
                ),
                "corresponding_author_email": oc6_source_equivalent_request_packet.get(
                    "source_article", {}
                ).get("corresponding_author_email"),
                "source_policy_rows_closed_by_packet": oc6_source_equivalent_request_packet.get(
                    "not_closing", {}
                ).get("source_policy_rows_closed_by_packet"),
                "source_policy_reopen_triggered": oc6_source_equivalent_request_packet.get(
                    "not_closing", {}
                ).get("source_policy_reopen_triggered"),
                "global_absence_proved": oc6_source_equivalent_request_packet.get(
                    "not_closing", {}
                ).get("global_absence_proved"),
                "submission_ready": oc6_source_equivalent_request_packet.get(
                    "not_closing", {}
                ).get("submission_ready"),
            },
            "safe_current_disposition": (
                "retain terminal unable-to-reproduce disposition; do not promote "
                "candidate runners as source-policy equivalent"
            ),
        },
        "OC12": {
            "closure_condition": (
                "promote the narrowed replay package to a full source-policy runner "
                "archive only after OC4 source-policy rows and OC6 TFE runner "
                "boundary are closed"
            ),
            "upstream_blockers": ["OC4", "OC6"],
            "current_archive_usable_as_full_source_policy_runner_archive": False,
            "full_source_policy_runner_package_ready": runner_centered.get(
                "full_source_policy_runner_package_ready"
            ),
            "narrowed_repro_code_archive_ready": (
                narrowed_archive.get("status")
                == "narrowed_repro_code_archive_ready_source_policy_open"
            ),
            "narrowed_repro_code_archive_submission_ready": narrowed_archive.get(
                "submission_ready"
            ),
            "source_policy_closed_ratio": f"{source_rows_closed}/{source_rows_total}",
            "remaining_source_policy_rows_to_close": source_rows_total - source_rows_closed,
            "safe_current_archive_use": "narrowed_claim_replay_and_audit_provenance_only",
            "action_boundary": archive_action_boundary,
        },
    }
    archive_blocker_safe_next_actions_by_id = {
        blocker_id: safe_next_actions_without_b4_opt_in
        for blocker_id in objective_blocking_ids
    }
    archive_blocker_opt_in_required_actions_by_id = {
        "OC4": opt_in_required_actions,
        "OC6": [],
        "OC12": opt_in_required_actions,
    }
    objective_archive_blocker_boundary = {
        "schema": "objective-archive-blocker-boundary-v1",
        "status": "full_archive_blocked_by_objective_blockers",
        "blocking_ids": objective_blocking_ids,
        "blocker_status_by_id": objective_blocker_status_by_id,
        "blocker_next_actions_by_id": objective_blocker_next_actions_by_id,
        "blocker_required_to_close_by_id": archive_blocker_required_to_close_by_id,
        "blocker_safe_next_actions_by_id": archive_blocker_safe_next_actions_by_id,
        "blocker_opt_in_required_actions_by_id": archive_blocker_opt_in_required_actions_by_id,
        "archive_closure_status_by_id": {
            blocker_id: archive_closure_by_objective_id.get(blocker_id, {}).get(
                "current_status"
            )
            for blocker_id in objective_blocking_ids
        },
        "archive_effect_by_id": {
            blocker_id: archive_closure_by_objective_id.get(blocker_id, {}).get(
                "archive_effect"
            )
            for blocker_id in objective_blocking_ids
        },
        "closure_allowed_by_id": {
            blocker_id: archive_closure_by_objective_id.get(blocker_id, {}).get(
                "closure_allowed_now"
            )
            for blocker_id in objective_blocking_ids
        },
        "source_policy_closed_ratio": f"{source_rows_closed}/{source_rows_total}",
        "full_archive_ready_now": full_archive_ready_now,
        "current_archive_usable_as_full_source_policy_runner_archive": False,
        "source_policy_execution_allowed_now": False,
        "exact_b4_opt_in_required_for_execution": True,
        "safe_action_ids": safe_action_ids,
        "opt_in_action_ids": opt_in_action_ids,
    }
    source_policy_rows_promoted = int(b4_ledger.get("source_policy_rows_promoted") or 0)
    attempted_not_reproducible_rows = int(
        b4_ledger.get("source_policy_rows_attempted_not_reproducible") or 0
    )
    tfe_source_policy_execution_preflight_tuple = (
        f"{tfe_preflight.get('status')}/"
        f"{tfe_preflight.get('ready_to_execute_source_policy_now')}/"
        f"{tfe_preflight.get('can_promote_any_tfe_source_policy_row_now')}/"
        f"{tfe_preflight.get('execution_block_count')}/"
        f"{tfe_preflight.get('explicit_user_opt_in_required')}"
    )
    tfe_runner_contract_preflight_tuple = (
        f"{tfe_runner_preflight.get('status')}/"
        f"{tfe_runner_preflight.get('callable_contract_count')}/"
        f"{tfe_runner_preflight.get('entrypoint_count')}/"
        f"{tfe_runner_preflight.get('candidate_backed_contract_count')}/"
        f"{tfe_runner_preflight.get('source_policy_rows_completed')}/"
        f"{tfe_runner_preflight.get('source_policy_execution_block_count')}"
    )
    expected_output_schema_audit_passed = (
        b4_expected_output_schema_audit.get("status")
        == "expected_outputs_schema_ready_not_authorized_not_run_not_promoted"
        and b4_expected_output_schema_audit.get("schema_ready_commands")
        == b4_expected_output_schema_audit.get("command_count")
        == ready_commands
        and b4_expected_output_schema_audit.get("artifacts_existing_now")
        == b4_expected_output_schema_audit.get("expected_artifact_count")
        and b4_expected_output_schema_audit.get("artifacts_sha256_match_freeze")
        == b4_expected_output_schema_audit.get("expected_artifact_count")
        and b4_expected_output_schema_audit.get("commands_executed_by_audit") is False
        and b4_expected_output_schema_audit.get("source_policy_rows_closed") == 0
        and b4_expected_output_schema_audit.get("promotion_ready_rows") == 0
    )
    expected_output_schema_audit_tuple = (
        f"{b4_expected_output_schema_audit.get('status')}/"
        f"{b4_expected_output_schema_audit.get('command_count')}/"
        f"{b4_expected_output_schema_audit.get('expected_artifact_count')}/"
        f"{b4_expected_output_schema_audit.get('artifacts_sha256_match_freeze')}/"
        f"{b4_expected_output_schema_audit.get('schema_ready_commands')}/"
        f"{b4_expected_output_schema_audit.get('commands_executed_by_audit')}/"
        f"{b4_expected_output_schema_audit.get('source_policy_rows_closed')}/"
        f"{b4_expected_output_schema_audit.get('promotion_ready_rows')}"
    )
    oc12_closure_row = next(
        row
        for row in archive_closure_matrix
        if row.get("id") == "OC12_full_source_policy_runner_archive"
    )
    oc12_required_to_close = archive_blocker_required_to_close_by_id["OC12"]
    oc12_closure_decision = (
        "remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready"
    )

    output: dict[str, Any] = {
        "schema": "full-source-policy-runner-archive-gap-audit-v1",
        "status": "full_source_policy_runner_archive_not_ready_source_policy_open",
        "oc12_blocker_id": "OC12",
        "oc12_blocker_status": "partial",
        "oc12_blocker_open": True,
        "closure_decision": oc12_closure_decision,
        "oc12_closure_decision": oc12_closure_decision,
        "oc12_closure_allowed_now": False,
        "objective_blocker_matrix_status": "global_objective_blockers_remain_open",
        "blocker_open_by_id": BLOCKER_OPEN_BY_ID,
        "blocker_closure_decision_by_id": BLOCKER_CLOSURE_DECISION_BY_ID,
        "blocker_closure_allowed_by_id": BLOCKER_CLOSURE_ALLOWED_BY_ID,
        "dependency_blockers": oc12_required_to_close.get("upstream_blockers"),
        "current_archive_usable_as_full_source_policy_runner_archive": False,
        "safe_current_use": oc12_required_to_close.get("safe_current_archive_use"),
        "safe_current_package_use": oc12_closure_row.get("safe_current_package_use"),
        "primary_submission_package_allowed": oc12_closure_row.get(
            "primary_submission_package_allowed"
        ),
        "narrowed_reproducibility_package_ready": oc12_closure_row.get(
            "narrowed_reproducibility_package_ready"
        ),
        "local_runner_centered_candidate_ready": oc12_closure_row.get(
            "local_runner_centered_candidate_ready"
        ),
        "oc12_required_evidence_to_close": oc12_closure_row.get("required_evidence_to_close"),
        "read_only": True,
        "full_archive_ready_now": full_archive_ready_now,
        "full_source_policy_runner_package_ready": full_archive_ready_now,
        "can_use_current_archive_as_full_source_policy_runner_archive": False,
        "source_policy_closed": source_rows_total == 40 and source_rows_closed == source_rows_total,
        "source_policy_closed_ratio": f"{source_rows_closed}/{source_rows_total}",
        "source_policy_rows_closed": source_rows_closed,
        "source_policy_rows_promoted": source_policy_rows_promoted,
        "source_policy_rows_total": source_rows_total,
        "remaining_source_policy_rows_to_close": source_rows_total - source_rows_closed,
        "terminal_unable_to_reproduce_rows": terminal_unable_rows,
        "attempted_not_reproducible_rows": attempted_not_reproducible_rows,
        "tfe_source_policy_execution_preflight": tfe_source_policy_execution_preflight_tuple,
        "tfe_source_policy_execution_preflight_status": tfe_preflight.get("status"),
        "tfe_runner_contract_preflight": tfe_runner_contract_preflight_tuple,
        "tfe_runner_contract_preflight_status": tfe_runner_preflight.get("status"),
        "oc12_archive_tfe_preflight": tfe_runner_contract_preflight_tuple,
        "expected_output_schema_audit": (
            "PASS" if expected_output_schema_audit_passed else "FAIL"
        ),
        "expected_output_schema_audit_status": b4_expected_output_schema_audit.get("status"),
        "expected_output_schema_audit_tuple": expected_output_schema_audit_tuple,
        "b4_guarded_driver_refusal_boundary_audit_20260621": guarded_refusal_boundary_tuple,
        "b4_expected_output_schema_command_traceability": b4_expected_output_schema_audit.get(
            "command_traceability"
        ),
        "oc6_reopen_latest_external_probe": (
            f"{oc6_reopen_readiness.get('latest_external_probe_date_checked')}/"
            f"{oc6_reopen_readiness.get('latest_external_probe_count')}/"
            f"{oc6_reopen_readiness.get('latest_external_probe_positive_public_code_artifact_rows')}/"
            f"{oc6_reopen_readiness.get('latest_external_probe_source_policy_rows_closed')}/"
            f"{oc6_reopen_readiness.get('latest_external_probe_access_limited_count')}/"
            f"{oc6_reopen_readiness.get('latest_external_probe_global_absence_proved')}/"
            f"{oc6_reopen_readiness.get('latest_external_probe_source_policy_reopen_triggered')}"
        ),
        "oc6_external_source_artifact_recheck_20260621": (
            f"{oc6_external_recheck.get('date_checked')}/"
            f"{oc6_external_recheck.get('query_count')}/"
            f"{oc6_external_recheck.get('positive_public_code_artifact_rows')}/"
            f"{oc6_external_recheck.get('source_code_equivalent_artifact_rows')}/"
            f"{oc6_external_recheck.get('source_policy_rows_closed_by_recheck')}/"
            f"{oc6_external_recheck.get('source_policy_reopen_triggered')}/"
            f"{oc6_external_recheck.get('global_absence_proved')}"
        ),
        "oc6_source_equivalent_reopen_readiness_latest_external_probe_date": oc6_reopen_readiness.get(
            "latest_external_probe_date_checked"
        ),
        "oc6_source_equivalent_reopen_readiness_latest_external_probe_count": oc6_reopen_readiness.get(
            "latest_external_probe_count"
        ),
        "oc6_source_equivalent_reopen_readiness_latest_external_probe_positive_artifact_rows": oc6_reopen_readiness.get(
            "latest_external_probe_positive_public_code_artifact_rows"
        ),
        "oc6_source_equivalent_reopen_readiness_latest_external_probe_source_policy_rows_closed": oc6_reopen_readiness.get(
            "latest_external_probe_source_policy_rows_closed"
        ),
        "oc6_source_equivalent_reopen_readiness_latest_external_probe_access_limited_count": oc6_reopen_readiness.get(
            "latest_external_probe_access_limited_count"
        ),
        "oc6_source_equivalent_reopen_readiness_latest_external_probe_global_absence_proved": oc6_reopen_readiness.get(
            "latest_external_probe_global_absence_proved"
        ),
        "oc6_source_equivalent_reopen_readiness_latest_external_probe_reopen_triggered": oc6_reopen_readiness.get(
            "latest_external_probe_source_policy_reopen_triggered"
        ),
        "ra_hi_rows_requiring_authorized_closeout_or_new_artifact": ra_hi_open_rows,
        "ready_command_count": ready_commands,
        "ready_command_mapped_external_rows": ready_command_rows,
        "opt_in_required_command_count": row_provenance_handoff.get("opt_in_required_command_count"),
        "opt_in_required_mapped_external_rows": row_provenance_handoff.get(
            "opt_in_required_mapped_external_rows"
        ),
        "execution_authorized": b4_handoff.get("execution_authorized"),
        "required_user_approval_statement": b4_packet.get("required_user_approval_statement"),
        "guarded_execution_driver": row_provenance_handoff.get("guarded_execution_driver"),
        "driver_requires_exact_approval": row_provenance_handoff.get("driver_requires_exact_approval"),
        "driver_does_not_authorize_execution": row_provenance_handoff.get(
            "driver_does_not_authorize_execution"
        ),
        "submission_ready": False,
        "safe_without_b4_opt_in_count": len(safe_next_actions_without_b4_opt_in),
        "opt_in_required_action_count": len(opt_in_required_actions),
        "source_policy_execution_allowed_now": False,
        "exact_b4_opt_in_required_for_execution": True,
        "terminal_reopen_conditions": terminal_reopen_conditions,
        "safe_next_actions_without_b4_opt_in": safe_next_actions_without_b4_opt_in,
        "next_safe_actions": safe_next_actions_without_b4_opt_in,
        "next_safe_action_ids": safe_action_ids,
        "safe_action_ids": safe_action_ids,
        "opt_in_required_actions": opt_in_required_actions,
        "opt_in_action_ids": opt_in_action_ids,
        "source_policy_execution_invoked": source_policy_execution_invoked,
        "objective_archive_blocker_boundary": objective_archive_blocker_boundary,
        "archive_blocker_required_to_close_by_id": archive_blocker_required_to_close_by_id,
        "archive_blocker_safe_next_actions_by_id": archive_blocker_safe_next_actions_by_id,
        "archive_blocker_opt_in_required_actions_by_id": archive_blocker_opt_in_required_actions_by_id,
        "blocker_required_to_close_by_id": archive_blocker_required_to_close_by_id,
        "blocker_safe_next_actions_by_id": archive_blocker_safe_next_actions_by_id,
        "blocker_opt_in_required_actions_by_id": archive_blocker_opt_in_required_actions_by_id,
        "action_boundary": archive_action_boundary,
        "source_files": [
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
        ],
        "package_boundary": {
            "narrowed_reproducibility_package_ready": narrowed.get(
                "narrowed_claim_reproducibility_package_ready"
            ),
            "narrowed_repro_code_archive_ready": (
                narrowed_archive.get("status") == "narrowed_repro_code_archive_ready_source_policy_open"
            ),
            "narrowed_repro_code_archive_submission_ready": narrowed_archive.get("submission_ready"),
            "local_runner_centered_candidate_ready": runner_centered.get(
                "local_runner_centered_candidate_ready"
            ),
            "runner_centered_package_ready": runner_centered.get("runner_centered_package_ready"),
            "full_source_policy_runner_package_ready": runner_centered.get(
                "full_source_policy_runner_package_ready"
            ),
            "minimal_reproducible_submission_code_ready": manifest_summary.get(
                "minimal_reproducible_submission_code_ready"
            ),
            "manifest_submission_ready": manifest.get("submission_ready"),
            "safe_current_package_use": manifest_summary.get("minimal_submission_code_dependency_safe_use"),
            "primary_submission_package_allowed": manifest_summary.get(
                "minimal_submission_code_dependency_primary_allowed"
            ),
        },
        "source_policy_rows": {
            "total": source_rows_total,
            "closed": source_rows_closed,
            "promoted": source_policy_rows_promoted,
            "provenance_preflight_complete": provenance.get("provenance_preflight_complete_rows"),
            "provenance_preflight_total": provenance.get("row_count"),
            "provenance_preflight_is_not_promotion": provenance.get("claim_boundary", {}).get(
                "provenance_preflight_complete_is_not_source_policy_closure"
            ),
            "attempted_not_reproducible": attempted_not_reproducible_rows,
            "unable_to_reproduce": terminal_unable_rows,
            "still_requiring_execution_or_promotion": b4_ledger.get(
                "source_policy_rows_still_requiring_execution_or_promotion"
            ),
            "rows_with_launch_command_refs": b4_ledger.get("rows_with_launch_command_refs"),
            "rows_without_launch_command_refs": b4_ledger.get("rows_without_launch_command_refs"),
        },
        "row_provenance_handoff_boundary": row_provenance_handoff,
        "row_provenance_action_boundary": provenance.get("action_boundary"),
        "row_provenance_source_policy_execution_invoked": provenance.get(
            "source_policy_execution_invoked"
        ),
        "tfe_source_policy_execution_preflight_boundary": tfe_preflight,
        "tfe_runner_contract_preflight_boundary": tfe_runner_preflight,
        "terminal_unable_to_reproduce_suites": terminal_suites,
        "archive_closure_matrix": archive_closure_matrix,
        "ra_hi_closeout_boundary": {
            "status": ra_hi.get("status"),
            "execution_handoff_status": b4_handoff.get("status"),
            "execution_handoff_authorized": b4_handoff.get("execution_authorized"),
            "execution_handoff_commands_not_run": b4_handoff.get("commands_not_run_by_handoff"),
            "public_source_root_available_rows": ra_hi.get("public_source_root_available_rows"),
            "no_public_code_rows_included": ra_hi.get("no_public_code_rows_included"),
            "source_policy_rows_closed": ra_hi.get("source_policy_rows_closed"),
            "source_policy_rows_not_promoted": ra_hi.get("source_policy_rows_not_promoted"),
            "current_evidence_terminal_not_promotable_rows": ra_hi.get(
                "current_evidence_terminal_not_promotable_rows"
            ),
            "future_promotion_requires_authorized_execution_or_new_artifact_rows": ra_hi_open_rows,
            "source_policy_reproduction_complete_rows": ra_hi.get(
                "source_policy_reproduction_complete_rows"
            ),
            "ready_command_count": ready_commands,
            "ready_command_mapped_external_rows": ready_command_rows,
            "command_traceability_summary": b4_command_traceability_summary,
            "handoff_ready_command_batch_count": b4_handoff.get(
                "ra_hi_authorized_closeout_handoff", {}
            ).get("ready_command_batch_count"),
            "handoff_ready_command_count": b4_handoff.get(
                "ra_hi_authorized_closeout_handoff", {}
            ).get("ready_command_count"),
            "handoff_ready_command_mapped_external_rows": b4_handoff.get(
                "ra_hi_authorized_closeout_handoff", {}
            ).get("ready_command_mapped_external_rows"),
            "execution_invoked_by_packet": b4_packet.get("execution_invoked_by_packet"),
            "explicit_user_opt_in_required_before_any_command": b4_packet.get(
                "explicit_user_opt_in_required_before_any_command"
            ),
            "required_user_approval_statement": b4_packet.get("required_user_approval_statement"),
        },
        "public_code_refresh": {
            "status": public_refresh.get("status"),
            "row_count": public_refresh.get("row_count"),
            "public_code_available_rows": public_refresh.get("public_code_available_rows"),
            "self_reproduction_attempted_rows": public_refresh.get("self_reproduction_attempted_rows"),
            "unable_to_reproduce_rows": public_refresh.get("unable_to_reproduce_rows"),
            "source_policy_rows_closed": public_refresh.get("source_policy_rows_closed"),
        },
        "public_code_refresh_latest_supplement": {
            "status": public_refresh_latest.get("status"),
            "date_checked": public_refresh_latest.get("date_checked"),
            "row_count": public_refresh_latest.get("row_count"),
            "current_query_count": public_refresh_latest.get("current_query_count"),
            "positive_public_code_artifact_rows": public_refresh_latest.get(
                "positive_public_code_artifact_rows"
            ),
            "source_policy_rows_closed": public_refresh_latest.get("source_policy_rows_closed"),
            "source_policy_rows_promoted": public_refresh_latest.get("source_policy_rows_promoted"),
            "latest_external_probe_date_checked": public_refresh_latest.get(
                "latest_external_probe_date_checked"
            ),
            "latest_external_probe_count": public_refresh_latest.get(
                "latest_external_probe_count"
            ),
            "latest_external_probe_positive_public_code_artifact_rows": (
                public_refresh_latest.get(
                    "latest_external_probe_positive_public_code_artifact_rows"
                )
            ),
            "latest_external_probe_source_policy_rows_closed": public_refresh_latest.get(
                "latest_external_probe_source_policy_rows_closed"
            ),
            "latest_external_probe_access_limited_count": public_refresh_latest.get(
                "latest_external_probe_access_limited_count"
            ),
            "latest_external_probe_global_absence_proved": public_refresh_latest.get(
                "latest_external_probe_global_absence_proved"
            ),
            "latest_external_probe_source_policy_reopen_triggered": public_refresh_latest.get(
                "latest_external_probe_source_policy_reopen_triggered"
            ),
        },
        "reopen_condition_monitor": {
            "status": reopen_monitor.get("status"),
            "date_checked": reopen_monitor.get("date_checked"),
            "row_count": reopen_monitor.get("row_count"),
            "unable_to_reproduce_rows": reopen_monitor.get("unable_to_reproduce_rows"),
            "source_policy_rows_total": reopen_monitor.get("source_policy_rows_total"),
            "positive_public_code_artifact_rows": reopen_monitor.get("positive_public_code_artifact_rows"),
            "local_positive_reopen_artifact_rows": reopen_monitor.get("local_positive_reopen_artifact_rows"),
            "source_policy_reopen_triggered": reopen_monitor.get("source_policy_reopen_triggered"),
            "source_policy_rows_closed": reopen_monitor.get("source_policy_rows_closed"),
            "source_policy_closed": reopen_monitor.get("source_policy_closed"),
            "source_policy_open": reopen_monitor.get("source_policy_open"),
            "source_policy_closed_ratio": reopen_monitor.get("source_policy_closed_ratio"),
            "terminal_suite_count": reopen_monitor.get("terminal_suite_count"),
            "terminal_reopen_conditions": reopen_monitor.get("terminal_reopen_conditions"),
            "source_artifact_sha256": reopen_monitor.get("source_artifact_sha256"),
            "source_artifact_digest_policy": reopen_monitor.get("source_artifact_digest_policy"),
            "local_scan_digest": reopen_monitor.get("local_scan_digest"),
            "monitor_evidence_digest": reopen_monitor.get("monitor_evidence_digest"),
        },
        "oc6_source_equivalent_reopen_readiness_audit": {
            "status": oc6_reopen_readiness.get("status"),
            "date_checked": oc6_reopen_readiness.get("date_checked"),
            "row_count": oc6_reopen_readiness.get("row_count"),
            "tfe_rows": oc6_reopen_readiness.get("tfe_rows"),
            "vp_rows": oc6_reopen_readiness.get("vp_rows"),
            "unable_to_reproduce_rows": oc6_reopen_readiness.get(
                "unable_to_reproduce_rows"
            ),
            "public_code_available_rows": oc6_reopen_readiness.get(
                "public_code_available_rows"
            ),
            "candidate_runner_available_rows": oc6_reopen_readiness.get(
                "candidate_runner_available_rows"
            ),
            "candidate_runner_source_policy_equivalent_rows": oc6_reopen_readiness.get(
                "candidate_runner_source_policy_equivalent_rows"
            ),
            "positive_public_code_artifact_rows": oc6_reopen_readiness.get(
                "positive_public_code_artifact_rows"
            ),
            "local_positive_reopen_artifact_rows": oc6_reopen_readiness.get(
                "local_positive_reopen_artifact_rows"
            ),
            "source_policy_reopen_triggered": oc6_reopen_readiness.get(
                "source_policy_reopen_triggered"
            ),
            "source_policy_rows_closed": oc6_reopen_readiness.get(
                "source_policy_rows_closed"
            ),
            "source_policy_rows_promoted": oc6_reopen_readiness.get(
                "source_policy_rows_promoted"
            ),
            "oc6_can_close_now": oc6_reopen_readiness.get("oc6_can_close_now"),
            "performs_new_public_code_search": oc6_reopen_readiness.get(
                "performs_new_public_code_search"
            ),
            "latest_external_probe_date_checked": oc6_reopen_readiness.get(
                "latest_external_probe_date_checked"
            ),
            "latest_external_probe_count": oc6_reopen_readiness.get(
                "latest_external_probe_count"
            ),
            "latest_external_probe_positive_public_code_artifact_rows": oc6_reopen_readiness.get(
                "latest_external_probe_positive_public_code_artifact_rows"
            ),
            "latest_external_probe_source_policy_rows_closed": oc6_reopen_readiness.get(
                "latest_external_probe_source_policy_rows_closed"
            ),
            "latest_external_probe_access_limited_count": oc6_reopen_readiness.get(
                "latest_external_probe_access_limited_count"
            ),
            "latest_external_probe_global_absence_proved": oc6_reopen_readiness.get(
                "latest_external_probe_global_absence_proved"
            ),
            "latest_external_probe_source_policy_reopen_triggered": oc6_reopen_readiness.get(
                "latest_external_probe_source_policy_reopen_triggered"
            ),
            "latest_external_probe_rows_by_suite": oc6_reopen_readiness.get(
                "latest_external_probe_rows_by_suite"
            ),
            "reopen_readiness_digest": oc6_reopen_readiness.get(
                "reopen_readiness_digest"
            ),
        },
        "oc6_external_source_artifact_recheck_20260621_summary": {
            "status": oc6_external_recheck.get("status"),
            "date_checked": oc6_external_recheck.get("date_checked"),
            "query_count": oc6_external_recheck.get("query_count"),
            "positive_public_code_artifact_rows": oc6_external_recheck.get(
                "positive_public_code_artifact_rows"
            ),
            "source_code_equivalent_artifact_rows": oc6_external_recheck.get(
                "source_code_equivalent_artifact_rows"
            ),
            "source_policy_rows_closed_by_recheck": oc6_external_recheck.get(
                "source_policy_rows_closed_by_recheck"
            ),
            "source_policy_reopen_triggered": oc6_external_recheck.get(
                "source_policy_reopen_triggered"
            ),
            "global_absence_proved": oc6_external_recheck.get("global_absence_proved"),
            "submission_ready": oc6_external_recheck.get("submission_ready"),
        },
        "oc6_tfe_publisher_artifact_availability_20260621": (
            f"{oc6_publisher_availability.get('date_checked')}/"
            f"{oc6_publisher_availability.get('official_article_checked')}/"
            f"{oc6_publisher_availability.get('source_article', {}).get('source_artifact_signal_count')}/"
            f"{oc6_publisher_availability.get('positive_public_code_artifact_rows')}/"
            f"{oc6_publisher_availability.get('source_code_equivalent_artifact_rows')}/"
            f"{oc6_publisher_availability.get('source_policy_rows_closed_by_publisher_audit')}/"
            f"{oc6_publisher_availability.get('source_policy_reopen_triggered')}/"
            f"{oc6_publisher_availability.get('global_absence_proved')}"
        ),
        "oc6_tfe_publisher_artifact_availability_20260621_summary": {
            "status": oc6_publisher_availability.get("status"),
            "date_checked": oc6_publisher_availability.get("date_checked"),
            "official_article_checked": oc6_publisher_availability.get(
                "official_article_checked"
            ),
            "source_artifact_signal_count": oc6_publisher_availability.get(
                "source_article", {}
            ).get("source_artifact_signal_count"),
            "positive_public_code_artifact_rows": oc6_publisher_availability.get(
                "positive_public_code_artifact_rows"
            ),
            "source_code_equivalent_artifact_rows": oc6_publisher_availability.get(
                "source_code_equivalent_artifact_rows"
            ),
            "source_policy_rows_closed_by_publisher_audit": oc6_publisher_availability.get(
                "source_policy_rows_closed_by_publisher_audit"
            ),
            "source_policy_reopen_triggered": oc6_publisher_availability.get(
                "source_policy_reopen_triggered"
            ),
            "global_absence_proved": oc6_publisher_availability.get("global_absence_proved"),
            "submission_ready": oc6_publisher_availability.get("submission_ready"),
        },
        "oc6_tfe_source_equivalent_artifact_request_packet_20260621": (
            f"{oc6_source_equivalent_request_packet.get('request_ready')}/"
            f"{oc6_source_equivalent_request_packet.get('request_sent')}/"
            f"{oc6_source_equivalent_request_packet.get('requested_artifact_count')}/"
            f"{oc6_source_equivalent_request_packet.get('not_closing', {}).get('source_policy_rows_closed_by_packet')}/"
            f"{oc6_source_equivalent_request_packet.get('not_closing', {}).get('source_policy_reopen_triggered')}/"
            f"{oc6_source_equivalent_request_packet.get('not_closing', {}).get('submission_ready')}"
        ),
        "oc6_tfe_source_equivalent_artifact_request_packet_20260621_summary": {
            "status": oc6_source_equivalent_request_packet.get("status"),
            "date_prepared": oc6_source_equivalent_request_packet.get("date_prepared"),
            "request_ready": oc6_source_equivalent_request_packet.get("request_ready"),
            "request_sent": oc6_source_equivalent_request_packet.get("request_sent"),
            "requested_artifact_count": oc6_source_equivalent_request_packet.get(
                "requested_artifact_count"
            ),
            "corresponding_author_email": oc6_source_equivalent_request_packet.get(
                "source_article", {}
            ).get("corresponding_author_email"),
            "source_policy_rows_closed_by_packet": oc6_source_equivalent_request_packet.get(
                "not_closing", {}
            ).get("source_policy_rows_closed_by_packet"),
            "source_policy_reopen_triggered": oc6_source_equivalent_request_packet.get(
                "not_closing", {}
            ).get("source_policy_reopen_triggered"),
            "global_absence_proved": oc6_source_equivalent_request_packet.get(
                "not_closing", {}
            ).get("global_absence_proved"),
            "submission_ready": oc6_source_equivalent_request_packet.get(
                "not_closing", {}
            ).get("submission_ready"),
        },
        "b4_command_preflight_freeze": {
            "status": b4_command_freeze.get("status"),
            "date_checked": b4_command_freeze.get("date_checked"),
            "ready_command_count": b4_command_freeze.get("ready_command_count"),
            "unique_mapped_ra_hi_rows": b4_command_freeze.get("unique_mapped_ra_hi_rows"),
            "declared_row_reference_total": b4_command_freeze.get("declared_row_reference_total"),
            "traced_row_reference_total": b4_command_freeze.get("traced_row_reference_total"),
            "declared_vs_traced_mismatch_count": b4_command_freeze.get(
                "declared_vs_traced_mismatch_count"
            ),
            "expected_artifacts_existing_now": b4_command_freeze.get(
                "expected_artifacts_existing_now"
            ),
            "expected_artifact_count": b4_command_freeze.get("expected_artifact_count"),
            "commands_executed_by_freeze": b4_command_freeze.get("commands_executed_by_freeze"),
            "source_policy_rows_closed": b4_command_freeze.get("source_policy_rows_closed"),
            "source_policy_rows_total": b4_command_freeze.get("source_policy_rows_total"),
            "command_freeze_sha256": b4_command_freeze.get("command_freeze_sha256"),
        },
        "b4_expected_output_schema_audit": {
            "status": b4_expected_output_schema_audit.get("status"),
            "date_checked": b4_expected_output_schema_audit.get("date_checked"),
            "command_count": b4_expected_output_schema_audit.get("command_count"),
            "expected_artifact_count": b4_expected_output_schema_audit.get(
                "expected_artifact_count"
            ),
            "artifacts_existing_now": b4_expected_output_schema_audit.get(
                "artifacts_existing_now"
            ),
            "artifacts_sha256_match_freeze": b4_expected_output_schema_audit.get(
                "artifacts_sha256_match_freeze"
            ),
            "csv_parseable_artifacts": b4_expected_output_schema_audit.get(
                "csv_parseable_artifacts"
            ),
            "json_summary_parseable_artifacts": b4_expected_output_schema_audit.get(
                "json_summary_parseable_artifacts"
            ),
            "schema_ready_commands": b4_expected_output_schema_audit.get(
                "schema_ready_commands"
            ),
            "source_policy_rows_closed": b4_expected_output_schema_audit.get(
                "source_policy_rows_closed"
            ),
            "promotion_ready_rows": b4_expected_output_schema_audit.get(
                "promotion_ready_rows"
            ),
            "commands_executed_by_audit": b4_expected_output_schema_audit.get(
                "commands_executed_by_audit"
            ),
            "command_traceability": b4_expected_output_schema_audit.get(
                "command_traceability"
            ),
            "expected_output_schema_audit_sha256": b4_expected_output_schema_audit.get(
                "expected_output_schema_audit_sha256"
            ),
        },
        "b4_expected_output_promotion_readiness_blocker_audit": {
            "status": b4_expected_output_promotion_readiness_blocker_audit.get("status"),
            "date_checked": b4_expected_output_promotion_readiness_blocker_audit.get(
                "date_checked"
            ),
            "command_count": b4_expected_output_promotion_readiness_blocker_audit.get(
                "command_count"
            ),
            "schema_ready_command_count": b4_expected_output_promotion_readiness_blocker_audit.get(
                "schema_ready_command_count"
            ),
            "promotion_ready_command_count": b4_expected_output_promotion_readiness_blocker_audit.get(
                "promotion_ready_command_count"
            ),
            "command_row_reference_total": b4_expected_output_promotion_readiness_blocker_audit.get(
                "command_row_reference_total"
            ),
            "unique_mapped_ra_hi_row_count": b4_expected_output_promotion_readiness_blocker_audit.get(
                "unique_mapped_ra_hi_row_count"
            ),
            "unique_mapped_ra_hi_rows_not_promoted": b4_expected_output_promotion_readiness_blocker_audit.get(
                "unique_mapped_ra_hi_rows_not_promoted"
            ),
            "summary_source_policy_rows_closed_total": b4_expected_output_promotion_readiness_blocker_audit.get(
                "summary_source_policy_rows_closed_total"
            ),
            "summary_source_policy_rows_promoted_total": b4_expected_output_promotion_readiness_blocker_audit.get(
                "summary_source_policy_rows_promoted_total"
            ),
            "commands_with_schema_ready_but_promotion_blocked": b4_expected_output_promotion_readiness_blocker_audit.get(
                "commands_with_schema_ready_but_promotion_blocked"
            ),
            "source_policy_rows_closed": b4_expected_output_promotion_readiness_blocker_audit.get(
                "source_policy_rows_closed"
            ),
            "promotion_ready_rows": b4_expected_output_promotion_readiness_blocker_audit.get(
                "promotion_ready_rows"
            ),
            "b4_can_close_now": b4_expected_output_promotion_readiness_blocker_audit.get(
                "b4_can_close_now"
            ),
            "b7_can_close_now": b4_expected_output_promotion_readiness_blocker_audit.get(
                "b7_can_close_now"
            ),
            "promotion_readiness_digest": b4_expected_output_promotion_readiness_blocker_audit.get(
                "promotion_readiness_digest"
            ),
        },
        "b4_guarded_driver_refusal_boundary_audit_20260621_summary": {
            "status": b4_guarded_refusal.get("status"),
            "date_checked": b4_guarded_refusal.get("date_checked"),
            "no_opt_in_refusal_proved_static": b4_guarded_refusal.get(
                "no_opt_in_refusal_proved_static"
            ),
            "wrong_approval_refusal_proved_static": b4_guarded_refusal.get(
                "wrong_approval_refusal_proved_static"
            ),
            "refusal_exit_code": b4_guarded_refusal.get("refusal_exit_code"),
            "pre_guard_command_count": b4_guarded_refusal.get("pre_guard_command_count"),
            "refusal_branch_source_policy_command_count": b4_guarded_refusal.get(
                "refusal_branch_source_policy_command_count"
            ),
            "post_guard_source_policy_command_count": b4_guarded_refusal.get(
                "post_guard_source_policy_command_count"
            ),
            "ra_allow_source_policy_1e_4_command_count": b4_guarded_refusal.get(
                "ra_allow_source_policy_1e_4_command_count"
            ),
            "hi_execute_command_count": b4_guarded_refusal.get("hi_execute_command_count"),
            "driver_commands_match_packet": b4_guarded_refusal.get(
                "driver_commands_match_packet"
            ),
            "driver_invoked_by_audit": b4_guarded_refusal.get("driver_invoked_by_audit"),
            "source_policy_execution_invoked": b4_guarded_refusal.get(
                "source_policy_execution_invoked"
            ),
            "source_policy_rows_closed_by_audit": b4_guarded_refusal.get(
                "source_policy_rows_closed_by_audit"
            ),
            "submission_ready": b4_guarded_refusal.get("submission_ready"),
            "marker": b4_guarded_refusal.get("marker"),
        },
        "closure_conditions": {
            "full_archive_ready_now": full_archive_ready_now,
            "full_row_provenance_preflight_ready": provenance.get("provenance_preflight_complete_rows")
            == provenance.get("row_count")
            == 40,
            "full_row_provenance_promotion_ready": provenance.get("promotion_ready_rows") == 40,
            "expected_outputs_schema_ready_but_promotion_blocked": (
                b4_expected_output_promotion_readiness_blocker_audit.get(
                    "schema_ready_command_count"
                )
                == b4_expected_output_promotion_readiness_blocker_audit.get("command_count")
                and b4_expected_output_promotion_readiness_blocker_audit.get(
                    "promotion_ready_command_count"
                )
                == 0
            ),
            "expected_output_promotion_ready_command_count": (
                b4_expected_output_promotion_readiness_blocker_audit.get(
                    "promotion_ready_command_count"
                )
            ),
            "expected_output_promotion_blocked_command_count": (
                b4_expected_output_promotion_readiness_blocker_audit.get(
                    "commands_with_schema_ready_but_promotion_blocked"
                )
            ),
            "row_provenance_handoff_authorized": row_provenance_handoff.get(
                "execution_authorized"
            ),
            "row_provenance_handoff_commands_not_run": row_provenance_handoff.get(
                "commands_not_run_by_handoff"
            ),
            "row_provenance_handoff_driver_requires_exact_approval": row_provenance_handoff.get(
                "driver_requires_exact_approval"
            ),
            "row_provenance_handoff_driver_does_not_authorize_execution": row_provenance_handoff.get(
                "driver_does_not_authorize_execution"
            ),
            "can_claim_full_source_policy_reproduction_now": False,
            "can_use_current_archive_as_full_source_policy_runner_archive": False,
            "can_submit_current_runner_package_as_primary_source_package": False,
            "remaining_source_policy_rows_to_close": source_rows_total - source_rows_closed,
            "ra_hi_rows_requiring_authorized_closeout_or_new_artifact": ra_hi_open_rows,
            "terminal_unable_to_reproduce_rows": terminal_unable_rows,
            "tfe_source_policy_preflight_ready_now": tfe_preflight.get(
                "ready_to_execute_source_policy_now"
            ),
            "tfe_source_policy_preflight_can_promote_now": tfe_preflight.get(
                "can_promote_any_tfe_source_policy_row_now"
            ),
            "tfe_source_policy_preflight_execution_block_count": tfe_preflight.get(
                "execution_block_count"
            ),
            "tfe_source_policy_preflight_effective_execution_block_count": tfe_preflight.get(
                "effective_missing_contract_block_count"
            ),
            "tfe_source_policy_preflight_terminal_nonpromoted_block_count": tfe_preflight.get(
                "terminal_nonpromoted_contract_block_count"
            ),
            "tfe_source_policy_preflight_requires_opt_in": tfe_preflight.get(
                "explicit_user_opt_in_required"
            ),
            "tfe_source_policy_preflight_reopen_condition": tfe_preflight.get(
                "reopen_condition"
            ),
            "oc6_source_equivalent_reopen_ready_now": oc6_reopen_readiness.get(
                "oc6_can_close_now"
            ),
            "oc6_positive_public_code_artifact_rows": oc6_reopen_readiness.get(
                "positive_public_code_artifact_rows"
            ),
            "oc6_local_positive_reopen_artifact_rows": oc6_reopen_readiness.get(
                "local_positive_reopen_artifact_rows"
            ),
            "oc6_source_equivalent_candidate_rows": oc6_reopen_readiness.get(
                "candidate_runner_source_policy_equivalent_rows"
            ),
            "oc6_source_policy_rows_closed": oc6_reopen_readiness.get(
                "source_policy_rows_closed"
            ),
            "tfe_runner_contract_preflight_status": tfe_runner_preflight.get("status"),
            "tfe_runner_contract_preflight_entrypoints": (
                f"{tfe_runner_preflight.get('callable_contract_count')}/"
                f"{tfe_runner_preflight.get('entrypoint_count')}"
            ),
            "tfe_runner_contract_preflight_candidate_backed": (
                f"{tfe_runner_preflight.get('candidate_backed_contract_count')}/"
                f"{tfe_runner_preflight.get('entrypoint_count')}"
            ),
            "tfe_runner_contract_preflight_source_policy_rows_completed": tfe_runner_preflight.get(
                "source_policy_rows_completed"
            ),
            "tfe_runner_contract_preflight_execution_blocks": tfe_runner_preflight.get(
                "source_policy_execution_block_count"
            ),
            "tfe_runner_contract_preflight_safe_use": tfe_runner_preflight.get(
                "safe_current_use"
            ),
            "tfe_runner_contract_preflight_all_non_equivalent": tfe_runner_preflight.get(
                "all_non_equivalent"
            ),
            "source_policy_handoff_ready_now": b4_handoff.get("status")
            == "source_policy_execution_handoff_ready_not_authorized_not_run",
            "source_policy_handoff_authorized_now": b4_handoff.get("execution_authorized"),
            "next_required_action": (
                "Keep the narrowed/replay package as provenance only. A full source-policy runner archive "
                "requires OC4 RA/HI closeout through the exact B4 opt-in or a new source-policy promotion "
                "artifact, plus OC6 staying terminal/nonpromoted unless new TFE/VP public or source-equivalent "
                "code appears."
            ),
        },
        "heavy_numerical_run_invoked": False,
        "run_v047_invoked": False,
        "v048_runner_invoked": False,
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# Full Source-Policy Runner Archive Gap Audit",
        "",
        f"Status: `{output['status']}`.",
        "",
        "This audit does not run numerical source-policy commands. It records why the current runnable package remains narrowed/replay provenance rather than a full source-policy runner archive.",
        "",
        f"- Full archive ready now: `{full_archive_ready_now}`.",
        f"- Full source-policy runner package ready: `{output['full_source_policy_runner_package_ready']}`.",
        f"- Source-policy rows closed/promoted/attempted-not-reproducible/total: `{source_rows_closed}/{source_policy_rows_promoted}/{attempted_not_reproducible_rows}/{source_rows_total}`.",
        f"- Row provenance preflight complete: `{output['source_policy_rows']['provenance_preflight_complete']}/{output['source_policy_rows']['provenance_preflight_total']}`.",
        f"- Row provenance is promotion: `{not output['source_policy_rows']['provenance_preflight_is_not_promotion']}`.",
        f"- Terminal unable-to-reproduce rows: `{terminal_unable_rows}`.",
        f"- Top-level TFE source-policy execution preflight alias: `{output['tfe_source_policy_execution_preflight']}`.",
        f"- TFE source-policy preflight status/ready/promote/blocks/opt-in: `{tfe_preflight['status']}/{tfe_preflight['ready_to_execute_source_policy_now']}/{tfe_preflight['can_promote_any_tfe_source_policy_row_now']}/{tfe_preflight['execution_block_count']}/{tfe_preflight['explicit_user_opt_in_required']}`.",
        f"- TFE source-policy contract accounting raw/non-heavy-terminal/effective-execution/source-rows: `{tfe_preflight['contract_block_accounting']['raw_open_contract_block_count']}/{tfe_preflight['terminal_nonpromoted_contract_block_count']}/{tfe_preflight['effective_missing_contract_block_count']}/{tfe_preflight['contract_block_accounting']['source_policy_rows_closed_by_accounting']}`.",
        f"- TFE source-policy preflight reopen condition: `{tfe_preflight['reopen_condition']}`.",
        f"- Top-level TFE runner contract preflight alias: `{output['tfe_runner_contract_preflight']}`.",
        f"- Top-level OC12 archive TFE preflight alias: `{output['oc12_archive_tfe_preflight']}`.",
        f"- TFE runner contract preflight status/entrypoints/candidate-backed/source-rows/execution-blocks: `{tfe_runner_preflight['status']}/{tfe_runner_preflight['callable_contract_count']}/{tfe_runner_preflight['entrypoint_count']}/{tfe_runner_preflight['candidate_backed_contract_count']}/{tfe_runner_preflight['source_policy_rows_completed']}/{tfe_runner_preflight['source_policy_execution_block_count']}`.",
        f"- TFE runner contract preflight safe-use/non-equivalent/submission-ready: `{tfe_runner_preflight['safe_current_use']}/{tfe_runner_preflight['all_non_equivalent']}/{tfe_runner_preflight['submission_ready']}`.",
        f"- Latest public-code refresh supplement: `{public_refresh_latest.get('status')}` on `{public_refresh_latest.get('date_checked')}`; rows/queries/positive/closed/promoted `{public_refresh_latest.get('row_count')}/{public_refresh_latest.get('current_query_count')}/{public_refresh_latest.get('positive_public_code_artifact_rows')}/{public_refresh_latest.get('source_policy_rows_closed')}/{public_refresh_latest.get('source_policy_rows_promoted')}`.",
        f"- Latest external public-code probe: `{public_refresh_latest.get('latest_external_probe_date_checked')}/{public_refresh_latest.get('latest_external_probe_count')}/{public_refresh_latest.get('latest_external_probe_positive_public_code_artifact_rows')}/{public_refresh_latest.get('latest_external_probe_source_policy_rows_closed')}/{public_refresh_latest.get('latest_external_probe_access_limited_count')}/{public_refresh_latest.get('latest_external_probe_global_absence_proved')}/{public_refresh_latest.get('latest_external_probe_source_policy_reopen_triggered')}`.",
        f"- Reopen-condition monitor: `{reopen_monitor.get('status')}` on `{reopen_monitor.get('date_checked')}`; rows/unable/public-positive/local-positive/reopened/closed/closed-bool/open-bool/ratio `{reopen_monitor.get('row_count')}/{reopen_monitor.get('unable_to_reproduce_rows')}/{reopen_monitor.get('positive_public_code_artifact_rows')}/{reopen_monitor.get('local_positive_reopen_artifact_rows')}/{reopen_monitor.get('source_policy_reopen_triggered')}/{reopen_monitor.get('source_policy_rows_closed')}/{reopen_monitor.get('source_policy_closed')}/{reopen_monitor.get('source_policy_open')}/{reopen_monitor.get('source_policy_closed_ratio')}`.",
        f"- Reopen-condition monitor terminal conditions: `tfe2026_original_pendulum={reopen_monitor.get('terminal_reopen_conditions', {}).get('tfe2026_original_pendulum')}; vp2024_velocity_partitioning={reopen_monitor.get('terminal_reopen_conditions', {}).get('vp2024_velocity_partitioning')}`.",
        f"- Reopen-condition monitor digests: local-scan `{reopen_monitor.get('local_scan_digest')}`; evidence `{reopen_monitor.get('monitor_evidence_digest')}`.",
        f"- OC6 source-equivalent reopen-readiness audit: `{oc6_reopen_readiness.get('status')}` on `{oc6_reopen_readiness.get('date_checked')}`; rows TFE/VP/total/unable/public-code/candidate/source-equivalent/positive/local-positive/reopened/closed `{oc6_reopen_readiness.get('tfe_rows')}/{oc6_reopen_readiness.get('vp_rows')}/{oc6_reopen_readiness.get('row_count')}/{oc6_reopen_readiness.get('unable_to_reproduce_rows')}/{oc6_reopen_readiness.get('public_code_available_rows')}/{oc6_reopen_readiness.get('candidate_runner_available_rows')}/{oc6_reopen_readiness.get('candidate_runner_source_policy_equivalent_rows')}/{oc6_reopen_readiness.get('positive_public_code_artifact_rows')}/{oc6_reopen_readiness.get('local_positive_reopen_artifact_rows')}/{oc6_reopen_readiness.get('source_policy_reopen_triggered')}/{oc6_reopen_readiness.get('source_policy_rows_closed')}`.",
        f"- OC6 source-equivalent reopen-readiness latest external probe: `{oc6_reopen_readiness.get('latest_external_probe_date_checked')}/{oc6_reopen_readiness.get('latest_external_probe_count')}/{oc6_reopen_readiness.get('latest_external_probe_positive_public_code_artifact_rows')}/{oc6_reopen_readiness.get('latest_external_probe_source_policy_rows_closed')}/{oc6_reopen_readiness.get('latest_external_probe_access_limited_count')}/{oc6_reopen_readiness.get('latest_external_probe_global_absence_proved')}/{oc6_reopen_readiness.get('latest_external_probe_source_policy_reopen_triggered')}`.",
        f"- OC6 external source-artifact recheck 20260621: `{oc6_external_recheck.get('status')}`; date/query/positive/source-equivalent/closed/reopened/global-absence `{oc6_external_recheck.get('date_checked')}/{oc6_external_recheck.get('query_count')}/{oc6_external_recheck.get('positive_public_code_artifact_rows')}/{oc6_external_recheck.get('source_code_equivalent_artifact_rows')}/{oc6_external_recheck.get('source_policy_rows_closed_by_recheck')}/{oc6_external_recheck.get('source_policy_reopen_triggered')}/{oc6_external_recheck.get('global_absence_proved')}`.",
        f"- OC6 TFE publisher artifact availability 20260621: `{oc6_publisher_availability.get('status')}`; date/official/signal/positive/source-equivalent/closed/reopened/global-absence `{oc6_publisher_availability.get('date_checked')}/{oc6_publisher_availability.get('official_article_checked')}/{oc6_publisher_availability.get('source_article', {}).get('source_artifact_signal_count')}/{oc6_publisher_availability.get('positive_public_code_artifact_rows')}/{oc6_publisher_availability.get('source_code_equivalent_artifact_rows')}/{oc6_publisher_availability.get('source_policy_rows_closed_by_publisher_audit')}/{oc6_publisher_availability.get('source_policy_reopen_triggered')}/{oc6_publisher_availability.get('global_absence_proved')}`.",
        f"- OC6 TFE source-equivalent artifact request packet 20260621: `{oc6_source_equivalent_request_packet.get('status')}`; ready/sent/requested/closed/reopened/submission-ready `{oc6_source_equivalent_request_packet.get('request_ready')}/{oc6_source_equivalent_request_packet.get('request_sent')}/{oc6_source_equivalent_request_packet.get('requested_artifact_count')}/{oc6_source_equivalent_request_packet.get('not_closing', {}).get('source_policy_rows_closed_by_packet')}/{oc6_source_equivalent_request_packet.get('not_closing', {}).get('source_policy_reopen_triggered')}/{oc6_source_equivalent_request_packet.get('not_closing', {}).get('submission_ready')}`.",
        f"- B4 command preflight freeze: `{b4_command_freeze.get('status')}` on `{b4_command_freeze.get('date_checked')}`; commands/unique-rows/row-refs/mismatches/artifacts/executed/closed `{b4_command_freeze.get('ready_command_count')}/{b4_command_freeze.get('unique_mapped_ra_hi_rows')}/{b4_command_freeze.get('traced_row_reference_total')}/{b4_command_freeze.get('declared_vs_traced_mismatch_count')}/{b4_command_freeze.get('expected_artifacts_existing_now')}/{b4_command_freeze.get('commands_executed_by_freeze')}/{b4_command_freeze.get('source_policy_rows_closed')}`.",
        f"- Top-level expected-output schema audit alias: `{output['expected_output_schema_audit']}` / `{output['expected_output_schema_audit_tuple']}`.",
        f"- B4 expected-output schema audit: `{b4_expected_output_schema_audit.get('status')}` on `{b4_expected_output_schema_audit.get('date_checked')}`; commands/artifacts/hash-match/csv/json/schema-ready/executed/closed `{b4_expected_output_schema_audit.get('command_count')}/{b4_expected_output_schema_audit.get('expected_artifact_count')}/{b4_expected_output_schema_audit.get('artifacts_sha256_match_freeze')}/{b4_expected_output_schema_audit.get('csv_parseable_artifacts')}/{b4_expected_output_schema_audit.get('json_summary_parseable_artifacts')}/{b4_expected_output_schema_audit.get('schema_ready_commands')}/{b4_expected_output_schema_audit.get('commands_executed_by_audit')}/{b4_expected_output_schema_audit.get('source_policy_rows_closed')}`.",
        f"- B4 expected-output schema command traceability shell/output/summary/no-summary/existing-output/existing-summary: `{b4_expected_output_schema_audit.get('command_traceability', {}).get('commands_with_shell_command')}/{b4_expected_output_schema_audit.get('command_traceability', {}).get('commands_with_expected_output_path')}/{b4_expected_output_schema_audit.get('command_traceability', {}).get('commands_with_expected_summary_path')}/{b4_expected_output_schema_audit.get('command_traceability', {}).get('commands_without_expected_summary_path')}/{b4_expected_output_schema_audit.get('command_traceability', {}).get('commands_with_existing_expected_output')}/{b4_expected_output_schema_audit.get('command_traceability', {}).get('commands_with_existing_expected_summary')}`.",
        f"- B4 expected-output promotion-readiness blocker audit: `{b4_expected_output_promotion_readiness_blocker_audit.get('status')}` on `{b4_expected_output_promotion_readiness_blocker_audit.get('date_checked')}`; commands/schema-ready/promotion-ready/row-refs/unique-rows/not-promoted/summary-closed/promoted/blocked `{b4_expected_output_promotion_readiness_blocker_audit.get('command_count')}/{b4_expected_output_promotion_readiness_blocker_audit.get('schema_ready_command_count')}/{b4_expected_output_promotion_readiness_blocker_audit.get('promotion_ready_command_count')}/{b4_expected_output_promotion_readiness_blocker_audit.get('command_row_reference_total')}/{b4_expected_output_promotion_readiness_blocker_audit.get('unique_mapped_ra_hi_row_count')}/{b4_expected_output_promotion_readiness_blocker_audit.get('unique_mapped_ra_hi_rows_not_promoted')}/{b4_expected_output_promotion_readiness_blocker_audit.get('summary_source_policy_rows_closed_total')}/{b4_expected_output_promotion_readiness_blocker_audit.get('summary_source_policy_rows_promoted_total')}/{b4_expected_output_promotion_readiness_blocker_audit.get('commands_with_schema_ready_but_promotion_blocked')}`.",
        f"- B4 guarded driver refusal boundary audit 20260621: `{guarded_refusal_boundary_tuple}`.",
        f"- RA/HI rows requiring authorized closeout or new artifact: `{ra_hi_open_rows}`.",
        f"- B4 ready commands/mapped rows: `{ready_commands}/{ready_command_rows}`.",
        f"- Source-policy execution handoff traceability: unique RA/HI rows `{b4_command_traceability_summary.get('unique_mapped_row_count')}/{b4_command_traceability_summary.get('ra_hi_unique_row_count')}`; row refs `{b4_command_traceability_summary.get('traced_command_row_reference_total')}/{b4_command_traceability_summary.get('declared_mapped_row_reference_total')}`; mismatches/terminal/closed/promotion-ready `{b4_command_traceability_summary.get('declared_vs_traced_mismatch_count')}/{b4_command_traceability_summary.get('terminal_rows_with_command_refs')}/{b4_command_traceability_summary.get('source_policy_closed_rows')}/{b4_command_traceability_summary.get('promotion_ready_rows')}`.",
        f"- B4 handoff status/authorized: `{b4_handoff.get('status')}/{b4_handoff.get('execution_authorized')}`.",
        f"- Row provenance handoff exact approval/driver: `{row_provenance_handoff['exact_required_user_approval_statement']}/{row_provenance_handoff['guarded_execution_driver']}/{row_provenance_handoff['driver_requires_exact_approval']}/{row_provenance_handoff['driver_does_not_authorize_execution']}/{row_provenance_handoff['opt_in_required_command_count']}/{row_provenance_handoff['opt_in_required_mapped_external_rows']}/{row_provenance_handoff['terminal_unable_to_reproduce_rows']}`.",
        f"- Safe next actions without B4 opt-in: `{len(safe_next_actions_without_b4_opt_in)}`.",
        f"- Top-level next safe action ids: `{','.join(output['next_safe_action_ids'])}`.",
        f"- Opt-in required actions: `{len(opt_in_required_actions)}`.",
        f"- Source-policy execution allowed now: `{output['action_boundary']['source_policy_execution_allowed_now']}`.",
        f"- Exact B4 opt-in required for execution: `{output['action_boundary']['exact_b4_opt_in_required_for_execution']}`.",
        f"- Source-policy execution invoked: `{output['source_policy_execution_invoked']}`.",
        f"- B4 execution invoked: `{b4_packet.get('execution_invoked_by_packet')}`.",
        f"- Exact B4 approval statement: `{output['ra_hi_closeout_boundary']['required_user_approval_statement']}`.",
        f"- Current archive usable as full source-policy runner archive: `{output['can_use_current_archive_as_full_source_policy_runner_archive']}`.",
        f"- OC12 blocker/status/closure decision: `{output['oc12_blocker_id']}/{output['oc12_blocker_status']}/{output['oc12_closure_decision']}`.",
        f"- OC12 current archive use/full-archive-usable/primary-allowed: `{output['safe_current_use']}/{output['current_archive_usable_as_full_source_policy_runner_archive']}/{output['primary_submission_package_allowed']}`.",
        f"- OC12 dependency blockers/closure allowed now: `{output['dependency_blockers']}/{output['oc12_closure_allowed_now']}`.",
        f"- OC12 narrowed/local runner/full package ready: `{output['narrowed_reproducibility_package_ready']}/{output['local_runner_centered_candidate_ready']}/{output['full_source_policy_runner_package_ready']}`.",
        f"- Archive closure matrix rows/blockers: `{len(archive_closure_matrix)}/OC4,OC6,OC12`.",
        f"- Objective archive blocker status by id: `{objective_blocker_status_by_id}`.",
        f"- Objective archive blocker next actions by id: `{objective_blocker_next_actions_by_id}`.",
        f"- Objective archive blocker effects by id: `{objective_archive_blocker_boundary['archive_effect_by_id']}`.",
        f"- Archive blocker required-to-close by id: `{archive_blocker_required_to_close_by_id}`.",
        f"- Archive blocker safe next actions by id: `{archive_blocker_safe_next_actions_by_id}`.",
        f"- Archive blocker opt-in required actions by id: `{archive_blocker_opt_in_required_actions_by_id}`.",
        f"- Heavy/run_v047/v048 invoked: `{output['heavy_numerical_run_invoked']}/{output['run_v047_invoked']}/{output['v048_runner_invoked']}`.",
        "",
        "## Objective Blocker Matrix",
        "",
        "This audit records OC12 full source-policy archive status. It does not close the global objective blockers.",
        "",
        f"- `blocker_open_by_id={blocker_token(output['blocker_open_by_id'])}`",
        f"- `blocker_closure_decision_by_id={blocker_token(output['blocker_closure_decision_by_id'])}`",
        f"- `blocker_closure_allowed_by_id={blocker_token(output['blocker_closure_allowed_by_id'])}`",
        "",
        "## Archive Closure Matrix",
        "",
        "| id | blocker | status | closure allowed now | archive effect |",
        "|---|---|---|---:|---|",
    ]
    for item in archive_closure_matrix:
        lines.append(
            f"| `{item['id']}` | `{item['objective_blocker']}` | "
            f"`{item['current_status']}` | `{item['closure_allowed_now']}` | "
            f"`{item['archive_effect']}` |"
        )
    lines.extend(
        [
            "",
        "## Terminal Suites",
        "",
        "| suite | rows | unable | closed | reopen condition |",
        "|---|---:|---:|---:|---|",
        ]
    )
    for item in terminal_suites:
        lines.append(
            f"| `{item['suite_id']}` | `{item['row_count']}` | "
            f"`{item['unable_to_reproduce_rows']}` | "
            f"`{item['source_policy_rows_closed']}` | "
            f"`{item['reopen_condition']}` |"
        )
    lines.extend(
        [
            "",
            "## Action Boundary",
            "",
            "| id | allowed without B4 opt-in | source-policy commands executed |",
            "|---|---:|---:|",
        ]
    )
    for item in safe_next_actions_without_b4_opt_in:
        lines.append(
            f"| `{item['id']}` | `{item['allowed_without_b4_opt_in']}` | "
            f"`{not item['does_not_execute_source_policy_commands']}` |"
        )
    for item in opt_in_required_actions:
        lines.append(
            f"| `{item['id']}` | `{item['allowed_without_b4_opt_in']}` | "
            "`requires exact B4 opt-in` |"
        )
    lines.extend(
        [
            "",
            "## Next Required Action",
            "",
            output["closure_conditions"]["next_required_action"],
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("full_source_policy_runner_archive_gap_audit=written")
    print(f"source_policy_closed={source_rows_closed}/{source_rows_total}")
    print(f"source_policy_rows_promoted={source_policy_rows_promoted}")
    print(f"attempted_not_reproducible_rows={attempted_not_reproducible_rows}")
    print(f"terminal_unable_to_reproduce_rows={terminal_unable_rows}")
    print(
        "oc6_reopen_latest_external_probe="
        f"{oc6_reopen_readiness.get('latest_external_probe_date_checked')}/"
        f"{oc6_reopen_readiness.get('latest_external_probe_count')}/"
        f"{oc6_reopen_readiness.get('latest_external_probe_positive_public_code_artifact_rows')}/"
        f"{oc6_reopen_readiness.get('latest_external_probe_source_policy_rows_closed')}/"
        f"{oc6_reopen_readiness.get('latest_external_probe_access_limited_count')}/"
        f"{oc6_reopen_readiness.get('latest_external_probe_global_absence_proved')}/"
        f"{oc6_reopen_readiness.get('latest_external_probe_source_policy_reopen_triggered')}"
    )
    print(
        "oc6_external_source_artifact_recheck_20260621="
        f"{oc6_external_recheck.get('date_checked')}/"
        f"{oc6_external_recheck.get('query_count')}/"
        f"{oc6_external_recheck.get('positive_public_code_artifact_rows')}/"
        f"{oc6_external_recheck.get('source_code_equivalent_artifact_rows')}/"
        f"{oc6_external_recheck.get('source_policy_rows_closed_by_recheck')}/"
        f"{oc6_external_recheck.get('source_policy_reopen_triggered')}/"
        f"{oc6_external_recheck.get('global_absence_proved')}"
    )
    print(
        "oc6_tfe_publisher_artifact_availability_20260621="
        f"{oc6_publisher_availability.get('date_checked')}/"
        f"{oc6_publisher_availability.get('official_article_checked')}/"
        f"{oc6_publisher_availability.get('source_article', {}).get('source_artifact_signal_count')}/"
        f"{oc6_publisher_availability.get('positive_public_code_artifact_rows')}/"
        f"{oc6_publisher_availability.get('source_code_equivalent_artifact_rows')}/"
        f"{oc6_publisher_availability.get('source_policy_rows_closed_by_publisher_audit')}/"
        f"{oc6_publisher_availability.get('source_policy_reopen_triggered')}/"
        f"{oc6_publisher_availability.get('global_absence_proved')}"
    )
    print(
        "oc6_tfe_source_equivalent_artifact_request_packet_20260621="
        f"{oc6_source_equivalent_request_packet.get('request_ready')}/"
        f"{oc6_source_equivalent_request_packet.get('request_sent')}/"
        f"{oc6_source_equivalent_request_packet.get('requested_artifact_count')}/"
        f"{oc6_source_equivalent_request_packet.get('not_closing', {}).get('source_policy_rows_closed_by_packet')}/"
        f"{oc6_source_equivalent_request_packet.get('not_closing', {}).get('source_policy_reopen_triggered')}/"
        f"{oc6_source_equivalent_request_packet.get('not_closing', {}).get('submission_ready')}"
    )
    print(f"ra_hi_rows_requiring_authorized_closeout_or_new_artifact={ra_hi_open_rows}")
    print(
        "b4_guarded_driver_refusal_boundary_audit_20260621="
        f"{guarded_refusal_boundary_tuple}"
    )
    print("full_archive_ready_now=False")
    print("full_source_policy_runner_package_ready=False")


if __name__ == "__main__":
    main()
