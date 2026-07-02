#!/usr/bin/env python3
"""Build the CMAME reproducibility-package boundary manifest.

This is a read-only packaging audit over existing artifacts. It does not copy
files or run numerical experiments; it records which current files can support a
small submission supplement and which components are still missing.
"""

from __future__ import annotations

import json
from pathlib import Path


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
V048 = ROOT / "v048_cross_paper_same_test_benchmarks"
OUT_JSON = PAPER / "CMAME_REPRODUCIBILITY_PACKAGE_MANIFEST.json"
OUT_MD = PAPER / "CMAME_REPRODUCIBILITY_PACKAGE_MANIFEST.md"
DIRECT_PC2_SCOPE = "direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open"
DIRECT_PC2_READING_RULE = (
    "The schema-only compatibility boolean proof_gap_closed is a schema-compatible "
    "shorthand for direct_pc2_proof_gap_closed under the active direct PC2 residual-bridge/"
    "Kantorovich route. It does not close the primitive/Taylor route, P6 "
    "solver-policy evidence, P7 residual-to-error promotion, source-policy "
    "readiness, or full-TFE replacement."
)


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def resolve_package_path(path_label: str) -> Path:
    if path_label.startswith("../"):
        return (PAPER / path_label).resolve()
    return PAPER / path_label


def line_count(path: Path) -> int | None:
    if not path.exists() or not path.is_file() or path.suffix != ".py":
        return None
    return len(read_text(path).splitlines())


def file_item(path_label: str, role: str, layer: str, status: str, include_in_minimal: bool) -> dict[str, object]:
    path = resolve_package_path(path_label)
    item: dict[str, object] = {
        "path": path_label,
        "role": role,
        "layer": layer,
        "status": status,
        "exists": path.exists() and path.stat().st_size > 0,
        "include_in_minimal_submission_package": include_in_minimal,
    }
    count = line_count(path)
    if count is not None:
        item["python_lines"] = count
    return item


def main() -> None:
    review = read_json(PAPER / "CMAME_REVIEW_AGENT_REPORT.json")
    numerical = read_json(PAPER / "PAPER_NUMERICAL_RESULT_MATRIX.json")
    traceability = read_json(PAPER / "RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.json")
    b2 = read_json(PAPER / "B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.json")
    b4_plan = read_json(PAPER / "B4_SOURCE_POLICY_WORK_PRECISION_EXECUTION_PLAN.json")
    b4_existing_promotion_audit = read_json(PAPER / "B4_EXISTING_ARTIFACT_PROMOTION_AUDIT.json")
    b4_post_execution_audit = read_json(PAPER / "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.json")
    full_source_policy_row_provenance_audit = read_json(PAPER / "FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.json")
    ra_hi_post_execution_attempt_certificate = read_json(
        PAPER / "RA_HI_SOURCE_POLICY_POST_EXECUTION_ATTEMPT_CERTIFICATE.json"
    )
    ra_hi_source_policy_output_inventory = read_json(PAPER / "RA_HI_SOURCE_POLICY_OUTPUT_INVENTORY.json")
    ra_hi_source_policy_closeout_checklist = read_json(PAPER / "RA_HI_SOURCE_POLICY_CLOSEOUT_CHECKLIST.json")
    ra_hi_source_policy_promotion_blocker_matrix = read_json(
        PAPER / "RA_HI_SOURCE_POLICY_PROMOTION_BLOCKER_MATRIX.json"
    )
    ra2021_double_low_order = read_json(PAPER / "RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.json")
    hi2022_ra_half_double_failure = read_json(
        PAPER / "HI2022_RA_HALF_DOUBLE_SOURCE_POLICY_FAILURE_DIAGNOSIS.json"
    )
    hi2022_ra_half_double_repair = read_json(
        PAPER / "HI2022_RA_HALF_DOUBLE_REPAIR_ATTEMPT_CERTIFICATE.json"
    )
    b4_row_readiness_ledger = read_json(PAPER / "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.json")
    b4_execution_opt_in_packet = read_json(PAPER / "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json")
    b4_execution_handoff = read_json(PAPER / "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json")
    b4_command_freeze = read_json(PAPER / "B4_SOURCE_POLICY_COMMAND_PREFLIGHT_FREEZE_20260620.json")
    b4_expected_output_schema_audit = read_json(
        PAPER / "B4_SOURCE_POLICY_EXPECTED_OUTPUT_SCHEMA_AUDIT_20260620.json"
    )
    b4_expected_output_promotion_readiness_blocker_audit = read_json(
        PAPER / "B4_EXPECTED_OUTPUT_PROMOTION_READINESS_BLOCKER_AUDIT_20260620.json"
    )
    oc6_source_equivalent_reopen_readiness_audit = read_json(
        PAPER / "OC6_SOURCE_EQUIVALENT_REOPEN_READINESS_AUDIT_20260620.json"
    )
    b4_command_traceability_summary = b4_execution_handoff.get(
        "command_row_traceability", {}
    ).get("summary", {})
    b4_promotion_contract = b4_execution_opt_in_packet.get("post_execution_promotion_contract", {})
    tfe = read_json(PAPER / "TFE_SOURCE_POLICY_ROW_AUDIT.json")
    tfe_model = read_json(PAPER / "TFE_SOURCE_PENDULUM_MODEL_AUDIT.json")
    tfe_dae_gap = read_json(PAPER / "TFE_DAE_RUNNER_CONTRACT_GAP_AUDIT.json")
    tfe_runner_contract_preflight = read_json(PAPER / "TFE_RUNNER_CONTRACT_PREFLIGHT_CERTIFICATE.json")
    tfe_self_reproduction_attempt_certificate = read_json(
        PAPER / "TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.json"
    )
    tfe_public_code_recheck = read_json(PAPER / "TFE_PUBLIC_CODE_RECHECK_20260613.json")
    vp2024_public_code_recheck = read_json(PAPER / "VP2024_PUBLIC_CODE_RECHECK_20260613.json")
    source_policy_public_code_refresh = read_json(PAPER / "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.json")
    source_policy_public_code_refresh_latest = read_json(PAPER / "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.json")
    tfe_source_policy_execution_preflight = tfe_dae_gap.get("source_policy_execution_preflight", {})
    tfe_self_reproduction_execution_preflight = (
        tfe_self_reproduction_attempt_certificate.get("source_policy_execution_preflight", {})
    )
    tfe_self_reproduction_required_next_actions = (
        tfe_self_reproduction_attempt_certificate.get("required_next_actions", [])
    )
    tfe_brown_mcphee_boundary = read_json(PAPER / "TFE_BROWN_MCPHEE_SOURCE_LAW_BOUNDARY_AUDIT.json")
    tfe_brown_mcphee_contract = tfe_brown_mcphee_boundary.get(
        "candidate_frictional_dae_trajectory_contract", {}
    )
    tfe_brown_mcphee_velocity_sensitivity = tfe_brown_mcphee_boundary.get(
        "brown_mcphee_transition_velocity_sensitivity", {}
    )
    tfe_brown_mcphee_certificate = read_json(
        PAPER / "TFE_BROWN_MCPHEE_SOURCE_CODE_EQUIVALENCE_CERTIFICATE.json"
    )
    tfe_dae_gap_missing_ids = [
        item.get("id") for item in tfe_dae_gap.get("missing_contract_blocks", [])
    ]
    tfe_full_t10_absolute = read_json(PAPER / "TFE_FULL_T10_ABSOLUTE_DAE_LIFT_SUMMARY.json")
    tfe_endpoint_boundary = read_json(PAPER / "TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.json")
    tfe_endpoint_certificate = read_json(PAPER / "TFE_FULL_T10_ENDPOINT_POLICY_CLOSURE_CERTIFICATE.json")
    objective_completion = read_json(PAPER / "OBJECTIVE_COMPLETION_AUDIT.json")
    objective_summary = objective_completion.get("summary", {})
    objective_blocking_ids = list(objective_completion.get("blocking_ids", []))
    objective_blockers_by_id = {
        req_id: objective_completion.get("blockers_by_id", {}).get(req_id)
        for req_id in objective_blocking_ids
    }
    objective_blocker_status_by_id = {
        req_id: objective_completion.get("blocker_status_by_id", {}).get(req_id)
        for req_id in objective_blocking_ids
    }
    objective_blocker_next_actions_by_id = {
        req_id: objective_completion.get("blocker_next_actions_by_id", {}).get(req_id)
        for req_id in objective_blocking_ids
    }
    objective_blocker_required_to_close_by_id = {
        req_id: objective_completion.get("blocker_required_to_close_by_id", {}).get(req_id)
        for req_id in objective_blocking_ids
    }
    objective_blocker_safe_next_actions_by_id = {
        req_id: objective_completion.get("blocker_safe_next_actions_by_id", {}).get(req_id)
        for req_id in objective_blocking_ids
    }
    objective_blocker_opt_in_required_actions_by_id = {
        req_id: objective_completion.get("blocker_opt_in_required_actions_by_id", {}).get(req_id)
        for req_id in objective_blocking_ids
    }
    proof = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
    proof_claim_traceability = read_json(PAPER / "PROOF_CLAIM_TRACEABILITY_AUDIT.json")
    b4_post_execution_file_status = (
        b4_post_execution_audit.get("status")
        or "b4_post_execution_audit_status_missing_no_rows_promoted"
    )
    minimal_candidate = read_json(PAPER / "CMAME_MINIMAL_REPRODUCIBILITY_CANDIDATE_MANIFEST.json")
    runner_adapter = read_json(PAPER / "CMAME_RUNNER_ADAPTER_CANDIDATE_MANIFEST.json")
    runner_centered_audit = read_json(PAPER / "CMAME_RUNNER_CENTERED_REPRODUCIBILITY_AUDIT.json")
    p1_local_runner_audit = read_json(PAPER / "CMAME_P1_LOCAL_RUNNER_EXTRACTION_AUDIT.json")
    extraction_plan = read_json(PAPER / "CMAME_SELF_CONTAINED_RUNNER_EXTRACTION_PLAN.json")
    b6_local_evidence = read_json(PAPER / "B6_FOUR_EXAMPLE_LOCAL_EVIDENCE_SUMMARY.json")
    closed_loop_audit = read_json(PAPER / "B6_CLOSED_LOOP_SELF_CONTAINED_EXTRACTION_AUDIT.json")
    closed_loop_candidate = read_json(PAPER / "CMAME_CLOSED_LOOP_LOCAL_RUNNER_CANDIDATE_MANIFEST.json")
    local_runner_companion = read_json(PAPER / "CMAME_LOCAL_ACCEPTED_RUNNER_COMPANION_MANIFEST.json")
    narrowed_repro_audit = read_json(PAPER / "CMAME_NARROWED_REPRODUCIBILITY_PACKAGE_AUDIT.json")
    narrowed_repro_code_archive = read_json(PAPER / "CMAME_NARROWED_REPRO_CODE_ARCHIVE_MANIFEST.json")
    full_source_runner_gap = read_json(PAPER / "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json")
    source_policy_reopen_monitor = read_json(
        PAPER / "SOURCE_POLICY_REOPEN_CONDITION_MONITOR_20260620.json"
    )
    full_source_terminal_reopen_conditions = {
        item.get("suite_id"): item.get("reopen_condition")
        for item in full_source_runner_gap.get("terminal_unable_to_reproduce_suites", [])
        if isinstance(item, dict)
    }
    full_source_ra_hi_approval_statement = full_source_runner_gap.get(
        "ra_hi_closeout_boundary", {}
    ).get("required_user_approval_statement")
    oc6_latest_external_probe = (
        f"{oc6_source_equivalent_reopen_readiness_audit.get('latest_external_probe_date_checked')}/"
        f"{oc6_source_equivalent_reopen_readiness_audit.get('latest_external_probe_count')}/"
        f"{oc6_source_equivalent_reopen_readiness_audit.get('latest_external_probe_positive_public_code_artifact_rows')}/"
        f"{oc6_source_equivalent_reopen_readiness_audit.get('latest_external_probe_source_policy_rows_closed')}/"
        f"{oc6_source_equivalent_reopen_readiness_audit.get('latest_external_probe_access_limited_count')}/"
        f"{oc6_source_equivalent_reopen_readiness_audit.get('latest_external_probe_global_absence_proved')}/"
        f"{oc6_source_equivalent_reopen_readiness_audit.get('latest_external_probe_source_policy_reopen_triggered')}"
    )
    p1_single_candidate = p1_local_runner_audit.get("p1_single_runner_candidate", {})
    p1_double_candidate = p1_local_runner_audit.get("p1_double_runner_candidate", {})
    closed_loop_local_models = list(runner_adapter.get("closed_loop_local_models", []))
    closed_loop_candidate_ready = (
        closed_loop_candidate.get("runner_passed") is True
        and closed_loop_candidate.get("self_contained_simulation_runner") is True
        and closed_loop_candidate.get("candidate_python_line_limit_ok") is True
        and closed_loop_candidate.get("imports_v046_v047_v048_or_v029") is False
        and closed_loop_candidate.get("closed_loop_local_rows") == 6
        and closed_loop_candidate.get("source_policy_external_superiority_allowed") is False
    )
    closed_loop_audit_package_status = (
        "closed_loop_self_contained_runner_candidate_ready_source_policy_open"
        if closed_loop_candidate_ready
        else "closed_loop_self_contained_target_mapped_runner_open"
    )
    closed_loop_candidate_package_status = (
        "closed_loop_candidate_passed_compact_source_policy_open"
        if closed_loop_candidate_ready
        else "closed_loop_candidate_passed_not_compact_source_policy_open"
    )
    human_runnable_self_contained_examples = []
    if p1_local_runner_audit.get("p1_single_runner_candidate_ready") is True:
        human_runnable_self_contained_examples.append("single_pendulum")
    if p1_local_runner_audit.get("p1_double_runner_candidate_ready") is True:
        human_runnable_self_contained_examples.append("double_pendulum")
    if closed_loop_candidate_ready:
        human_runnable_self_contained_examples.extend(closed_loop_candidate.get("closed_loop_models", []))
    human_runnable_replay_only_examples = (
        []
        if closed_loop_candidate_ready
        else closed_loop_local_models
        if runner_adapter.get("closed_loop_local_rows_replay_present") is True
        else []
    )
    expected_human_runnable_examples = ["single_pendulum", "double_pendulum", "four_link", "slider_crank"]
    human_runnable_local_evidence_examples = [
        example
        for example in expected_human_runnable_examples
        if example in set(human_runnable_self_contained_examples + human_runnable_replay_only_examples)
    ]
    human_runnable_four_example_local_evidence_available = (
        human_runnable_local_evidence_examples == expected_human_runnable_examples
    )
    human_runnable_four_example_self_contained_simulation_ready = (
        human_runnable_self_contained_examples == expected_human_runnable_examples
    )

    result_checks = review.get("result_checks", {})
    code_checks = review.get("code_hygiene_checks", {})
    external_checks = review.get("external_checks", {})
    tfe_candidate_source_policy_boundary = external_checks.get("tfe_candidate_source_policy_boundary", {})
    proof_checks = review.get("proof_checks", {})
    proof_theorem_boundary = proof.get("theorem_statement_boundary", {})
    proof_manuscript_traceability = proof.get("manuscript_traceability", {})
    proof_claim_theorem_traceability = proof_claim_traceability.get("manuscript_theorem_traceability", {})
    proof_claim_remaining_boundary = proof_claim_traceability.get("remaining_claim_boundary", {})
    proof_writing_card = proof_claim_traceability.get("proof_writing_boundary_card", {})

    files = [
        file_item("main_cmame.tex", "manuscript_source", "paper_bundle", "ready", True),
        file_item("main_cmame.pdf", "recommended_pdf", "paper_bundle", "ready", True),
        file_item("highlights_cmame.txt", "journal_sidecar", "paper_bundle", "ready", True),
        file_item("declarations_cmame.md", "journal_sidecar", "paper_bundle", "ready", True),
        file_item("PAPER_NUMERICAL_RESULT_MATRIX.csv", "44_cell_order_error_table", "result_bundle", "ready", True),
        file_item("PAPER_NUMERICAL_RESULT_MATRIX.json", "44_cell_order_error_table_metadata", "result_bundle", "ready", True),
        file_item("PAPER_NUMERICAL_RESULT_MATRIX.md", "human_readable_result_table", "result_bundle", "ready", True),
        file_item(
            "PAPER_CORE_RESULT_CONSOLIDATION.json",
            "paper_core_result_consolidation",
            "result_bundle",
            "ready",
            True,
        ),
        file_item(
            "PAPER_CORE_RESULT_CONSOLIDATION.md",
            "human_readable_paper_core_result_consolidation",
            "result_bundle",
            "ready",
            True,
        ),
        file_item(
            "FOUR_EXAMPLE_SOURCE_POLICY_DASHBOARD.json",
            "four_example_claim_boundary",
            "result_bundle",
            "ready",
            True,
        ),
        file_item(
            "RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.json",
            "result_to_pdf_traceability",
            "result_bundle",
            "ready",
            True,
        ),
        file_item("CMAME_REVIEW_AGENT_REPORT.json", "submission_review_gate", "review_bundle", "ready", True),
        file_item(
            "REPRODUCIBILITY_GUIDE.md",
            "reviewer_facing_reproducibility_guide",
            "replay_package",
            "ready",
            True,
        ),
        file_item(
            "replay_reproducibility_core.py",
            "single_command_replay_entrypoint",
            "replay_package",
            "ready",
            True,
        ),
        file_item(
            "run_human_reproducibility.py",
            "human_facing_replay_entrypoint",
            "replay_package",
            "ready",
            True,
        ),
        file_item(
            "human_reproducibility_result_table.md",
            "human_readable_replay_result_table",
            "replay_package",
            "ready",
            True,
        ),
        file_item(
            "run_b6_four_example_local_evidence.py",
            "one_command_b6_four_example_local_evidence_runner",
            "replay_package",
            "ready_source_policy_open",
            True,
        ),
        file_item(
            "B6_FOUR_EXAMPLE_LOCAL_EVIDENCE_SUMMARY.json",
            "b6_four_example_local_evidence_metadata",
            "replay_package",
            "ready_source_policy_open",
            True,
        ),
        file_item(
            "B6_FOUR_EXAMPLE_LOCAL_EVIDENCE_SUMMARY.md",
            "human_readable_b6_four_example_local_evidence",
            "replay_package",
            "ready_source_policy_open",
            True,
        ),
        file_item(
            "validate_b6_four_example_local_evidence.py",
            "b6_four_example_local_evidence_validator",
            "replay_package",
            "ready_source_policy_open",
            True,
        ),
        file_item(
            "B6_CLOSED_LOOP_SELF_CONTAINED_EXTRACTION_AUDIT.json",
            "b6_closed_loop_self_contained_extraction_metadata",
            "candidate_runner_validation",
            closed_loop_audit_package_status,
            True,
        ),
        file_item(
            "B6_CLOSED_LOOP_SELF_CONTAINED_EXTRACTION_AUDIT.md",
            "human_readable_b6_closed_loop_self_contained_extraction_audit",
            "candidate_runner_validation",
            closed_loop_audit_package_status,
            True,
        ),
        file_item(
            "build_b6_closed_loop_self_contained_extraction_audit.py",
            "b6_closed_loop_self_contained_extraction_audit_builder",
            "candidate_runner_validation",
            closed_loop_audit_package_status,
            True,
        ),
        file_item(
            "validate_b6_closed_loop_self_contained_extraction_audit.py",
            "b6_closed_loop_self_contained_extraction_audit_validator",
            "candidate_runner_validation",
            closed_loop_audit_package_status,
            True,
        ),
        file_item(
            "CMAME_CLOSED_LOOP_LOCAL_RUNNER_CANDIDATE_MANIFEST.json",
            "b6_closed_loop_local_runner_candidate_metadata",
            "candidate_runner_validation",
            closed_loop_candidate_package_status,
            True,
        ),
        file_item(
            "CMAME_CLOSED_LOOP_LOCAL_RUNNER_CANDIDATE_MANIFEST.md",
            "human_readable_b6_closed_loop_local_runner_candidate",
            "candidate_runner_validation",
            closed_loop_candidate_package_status,
            True,
        ),
        file_item(
            "build_cmame_closed_loop_local_runner_candidate.py",
            "b6_closed_loop_local_runner_candidate_builder",
            "candidate_runner_validation",
            closed_loop_candidate_package_status,
            True,
        ),
        file_item(
            "validate_cmame_closed_loop_local_runner_candidate.py",
            "b6_closed_loop_local_runner_candidate_validator",
            "candidate_runner_validation",
            closed_loop_candidate_package_status,
            True,
        ),
        file_item(
            "cmame_closed_loop_local_runner_candidate/MANIFEST.json",
            "b6_closed_loop_local_runner_candidate_package_manifest",
            "candidate_runner_result",
            closed_loop_candidate_package_status,
            True,
        ),
        file_item(
            "cmame_closed_loop_local_runner_candidate/scripts/run_closed_loop_fullva_candidate.py",
            "b6_closed_loop_local_runner_candidate_entrypoint",
            "candidate_runner_result",
            closed_loop_candidate_package_status,
            True,
        ),
        file_item(
            "cmame_closed_loop_local_runner_candidate/results/closed_loop_local_summary.json",
            "b6_closed_loop_local_runner_candidate_result_summary",
            "candidate_runner_result",
            closed_loop_candidate_package_status,
            True,
        ),
        file_item(
            "cmame_closed_loop_local_runner_candidate/results/closed_loop_local_rows.csv",
            "b6_closed_loop_local_runner_candidate_rows",
            "candidate_runner_result",
            closed_loop_candidate_package_status,
            True,
        ),
        file_item(
            "../v047_cylindrical_chain_pipeline/run_v047.py",
            "current_full_research_generator",
            "current_source",
            "research_generator_not_minimal_api",
            False,
        ),
        file_item(
            "../v048_cross_paper_same_test_benchmarks/run_coarse_four_example_order.py",
            "coarse_four_example_order_runner",
            "candidate_runner_source",
            "needs_extraction",
            False,
        ),
        file_item(
            "../v048_cross_paper_same_test_benchmarks/closed_loop_fullva_dynamic_residual.py",
            "closed_loop_dynamic_residual_core",
            "candidate_runner_source",
            "needs_extraction",
            False,
        ),
        file_item(
            "../v048_cross_paper_same_test_benchmarks/run_ra2021_timing_shard.py",
            "ra2021_public_timing_runner",
            "external_source_policy_candidate",
            "needs_extraction",
            False,
        ),
        file_item(
            "../v048_cross_paper_same_test_benchmarks/run_ra2021_double_order_shard.py",
            "ra2021_double_order_runner",
            "external_source_policy_candidate",
            "needs_extraction",
            False,
        ),
        file_item(
            "../v048_cross_paper_same_test_benchmarks/run_hi2022_model_shard.py",
            "hi2022_model_shard_runner",
            "external_source_policy_candidate",
            "needs_extraction",
            False,
        ),
        file_item(
            "../v048_cross_paper_same_test_benchmarks/run_public_closed_loop_shard.py",
            "public_closed_loop_residual_runner",
            "external_source_policy_candidate",
            "needs_extraction",
            False,
        ),
        file_item(
            "../v048_cross_paper_same_test_benchmarks/tfe_source_pendulum_model.py",
            "tfe_source_pendulum_candidate_model_and_comparator_smoke",
            "external_source_policy_candidate",
            "needs_source_policy_promotion",
            False,
        ),
        file_item(
            "TFE_FULL_T10_ABSOLUTE_DAE_LIFT_SUMMARY.json",
            "tfe_full_t10_absolute_dae_lift_summary",
            "external_source_policy_candidate",
            "full_t10_absolute_dae_lift_candidate_not_source_policy",
            False,
        ),
        file_item(
            "TFE_FULL_T10_ABSOLUTE_DAE_LIFT_SUMMARY.md",
            "human_readable_tfe_full_t10_absolute_dae_lift_summary",
            "external_source_policy_candidate",
            "full_t10_absolute_dae_lift_candidate_not_source_policy",
            False,
        ),
        file_item(
            "TFE_FULL_T10_ABSOLUTE_DAE_LIFT_SUMMARY.csv",
            "tabular_tfe_full_t10_absolute_dae_lift_summary",
            "external_source_policy_candidate",
            "full_t10_absolute_dae_lift_candidate_not_source_policy",
            False,
        ),
        file_item(
            "TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.json",
            "tfe_source_policy_self_reproduction_attempt_certificate",
            "external_source_policy_candidate",
            "attempted_not_reproducible_not_promoted",
            False,
        ),
        file_item(
            "TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.md",
            "human_readable_tfe_source_policy_self_reproduction_attempt_certificate",
            "external_source_policy_candidate",
            "attempted_not_reproducible_not_promoted",
            False,
        ),
        file_item(
            "TFE_PUBLIC_CODE_RECHECK_20260613.json",
            "tfe_public_code_recheck_certificate",
            "external_source_policy_candidate",
            "public_code_rechecked_attempted_not_reproducible_not_promoted",
            False,
        ),
        file_item(
            "TFE_PUBLIC_CODE_RECHECK_20260613.md",
            "human_readable_tfe_public_code_recheck_certificate",
            "external_source_policy_candidate",
            "public_code_rechecked_attempted_not_reproducible_not_promoted",
            False,
        ),
        file_item(
            "VP2024_PUBLIC_CODE_RECHECK_20260613.json",
            "vp2024_public_code_recheck_certificate",
            "external_source_policy_candidate",
            "public_code_rechecked_attempted_not_reproducible_not_promoted",
            False,
        ),
        file_item(
            "VP2024_PUBLIC_CODE_RECHECK_20260613.md",
            "human_readable_vp2024_public_code_recheck_certificate",
            "external_source_policy_candidate",
            "public_code_rechecked_attempted_not_reproducible_not_promoted",
            False,
        ),
        file_item(
            "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.json",
            "source_policy_public_code_refresh",
            "external_source_policy_candidate",
            "public_code_refresh_no_new_source_artifact_unable_to_reproduce_not_promoted",
            False,
        ),
        file_item(
            "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.md",
            "human_readable_source_policy_public_code_refresh",
            "external_source_policy_candidate",
            "public_code_refresh_no_new_source_artifact_unable_to_reproduce_not_promoted",
            False,
        ),
        file_item(
            "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.json",
            "source_policy_public_code_refresh_latest_supplement",
            "external_source_policy_candidate",
            "public_code_refresh_20260620_no_positive_new_source_artifact_not_promoted",
            False,
        ),
        file_item(
            "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.md",
            "human_readable_source_policy_public_code_refresh_latest_supplement",
            "external_source_policy_candidate",
            "public_code_refresh_20260620_no_positive_new_source_artifact_not_promoted",
            False,
        ),
        file_item(
            "RA_HI_SOURCE_POLICY_POST_EXECUTION_ATTEMPT_CERTIFICATE.json",
            "ra_hi_source_policy_post_execution_attempt_certificate",
            "external_source_policy_candidate",
            "post_execution_attempts_recorded_rows_not_promoted_full_source_policy_open",
            False,
        ),
        file_item(
            "RA_HI_SOURCE_POLICY_POST_EXECUTION_ATTEMPT_CERTIFICATE.md",
            "human_readable_ra_hi_source_policy_post_execution_attempt_certificate",
            "external_source_policy_candidate",
            "post_execution_attempts_recorded_rows_not_promoted_full_source_policy_open",
            False,
        ),
        file_item(
            "RA_HI_SOURCE_POLICY_CLOSEOUT_CHECKLIST.json",
            "ra_hi_source_policy_closeout_checklist",
            "external_source_policy_candidate",
            "ready_for_authorized_execution_closeout_not_executed_not_promoted",
            False,
        ),
        file_item(
            "RA_HI_SOURCE_POLICY_CLOSEOUT_CHECKLIST.md",
            "human_readable_ra_hi_source_policy_closeout_checklist",
            "external_source_policy_candidate",
            "ready_for_authorized_execution_closeout_not_executed_not_promoted",
            False,
        ),
        file_item(
            "RA_HI_SOURCE_POLICY_OUTPUT_INVENTORY.json",
            "ra_hi_source_policy_output_inventory",
            "external_source_policy_candidate",
            "existing_expected_outputs_present_not_promotion_evidence",
            False,
        ),
        file_item(
            "RA_HI_SOURCE_POLICY_OUTPUT_INVENTORY.md",
            "human_readable_ra_hi_source_policy_output_inventory",
            "external_source_policy_candidate",
            "existing_expected_outputs_present_not_promotion_evidence",
            False,
        ),
        file_item(
            "RA_HI_SOURCE_POLICY_PROMOTION_BLOCKER_MATRIX.json",
            "ra_hi_source_policy_promotion_blocker_matrix",
            "external_source_policy_candidate",
            "ra_hi_public_root_rows_not_promoted_source_policy_open",
            False,
        ),
        file_item(
            "RA_HI_SOURCE_POLICY_PROMOTION_BLOCKER_MATRIX.md",
            "human_readable_ra_hi_source_policy_promotion_blocker_matrix",
            "external_source_policy_candidate",
            "ra_hi_public_root_rows_not_promoted_source_policy_open",
            False,
        ),
        file_item(
            "build_tfe_full_t10_absolute_dae_lift_summary.py",
            "tfe_full_t10_absolute_dae_lift_summary_builder",
            "external_source_policy_candidate",
            "full_t10_absolute_dae_lift_candidate_not_source_policy",
            False,
        ),
        file_item(
            "validate_tfe_full_t10_absolute_dae_lift_summary.py",
            "tfe_full_t10_absolute_dae_lift_summary_validator",
            "external_source_policy_candidate",
            "full_t10_absolute_dae_lift_candidate_not_source_policy",
            False,
        ),
        file_item(
            "TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.json",
            "tfe_endpoint_policy_boundary_certificate",
            "external_source_policy_candidate",
            "endpoint_policy_boundary_certificate_not_source_policy",
            False,
        ),
        file_item(
            "TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.md",
            "human_readable_tfe_endpoint_policy_boundary_certificate",
            "external_source_policy_candidate",
            "endpoint_policy_boundary_certificate_not_source_policy",
            False,
        ),
        file_item(
            "TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.csv",
            "tabular_tfe_endpoint_policy_boundary_certificate",
            "external_source_policy_candidate",
            "endpoint_policy_boundary_certificate_not_source_policy",
            False,
        ),
        file_item(
            "build_tfe_endpoint_policy_boundary_certificate.py",
            "tfe_endpoint_policy_boundary_certificate_builder",
            "external_source_policy_candidate",
            "endpoint_policy_boundary_certificate_not_source_policy",
            False,
        ),
        file_item(
            "validate_tfe_endpoint_policy_boundary_certificate.py",
            "tfe_endpoint_policy_boundary_certificate_validator",
            "external_source_policy_candidate",
            "endpoint_policy_boundary_certificate_not_source_policy",
            False,
        ),
        file_item(
            "B4_SOURCE_POLICY_WORK_PRECISION_EXECUTION_PLAN.json",
            "b4_source_policy_work_precision_execution_plan",
            "external_source_policy_candidate",
            "b4_b7_open_plan_ready",
            False,
        ),
        file_item(
            "B4_SOURCE_POLICY_WORK_PRECISION_EXECUTION_PLAN.md",
            "human_readable_b4_source_policy_work_precision_execution_plan",
            "external_source_policy_candidate",
            "b4_b7_open_plan_ready",
            False,
        ),
        file_item(
            "B4_EXISTING_ARTIFACT_PROMOTION_AUDIT.json",
            "b4_existing_artifact_promotion_audit",
            "external_source_policy_candidate",
            "no_existing_artifact_promotable",
            True,
        ),
        file_item(
            "B4_EXISTING_ARTIFACT_PROMOTION_AUDIT.md",
            "human_readable_b4_existing_artifact_promotion_audit",
            "external_source_policy_candidate",
            "no_existing_artifact_promotable",
            True,
        ),
        file_item(
            "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.json",
            "b4_source_policy_post_execution_audit",
            "external_source_policy_candidate",
            b4_post_execution_file_status,
            True,
        ),
        file_item(
            "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.md",
            "human_readable_b4_source_policy_post_execution_audit",
            "external_source_policy_candidate",
            b4_post_execution_file_status,
            True,
        ),
        file_item(
            "FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.json",
            "full_source_policy_row_provenance_audit",
            "external_source_policy_candidate",
            "row_provenance_preflight_complete_not_promotion",
            False,
        ),
        file_item(
            "FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.md",
            "human_readable_full_source_policy_row_provenance_audit",
            "external_source_policy_candidate",
            "row_provenance_preflight_complete_not_promotion",
            False,
        ),
        file_item(
            "FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.csv",
            "tabular_full_source_policy_row_provenance_audit",
            "external_source_policy_candidate",
            "row_provenance_preflight_complete_not_promotion",
            False,
        ),
        file_item(
            "build_full_source_policy_row_provenance_audit.py",
            "full_source_policy_row_provenance_audit_builder",
            "external_source_policy_candidate",
            "row_provenance_preflight_complete_not_promotion",
            False,
        ),
        file_item(
            "validate_full_source_policy_row_provenance_audit.py",
            "full_source_policy_row_provenance_audit_validator",
            "external_source_policy_candidate",
            "row_provenance_preflight_complete_not_promotion",
            False,
        ),
        file_item(
            "RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.json",
            "ra2021_double_source_policy_low_order_diagnosis",
            "external_source_policy_candidate",
            "diagnosis_only_low_order_floor_limited_not_promoted",
            True,
        ),
        file_item(
            "RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.md",
            "human_readable_ra2021_double_source_policy_low_order_diagnosis",
            "external_source_policy_candidate",
            "diagnosis_only_low_order_floor_limited_not_promoted",
            True,
        ),
        file_item(
            "HI2022_RA_HALF_DOUBLE_SOURCE_POLICY_FAILURE_DIAGNOSIS.json",
            "hi2022_ra_half_double_source_policy_failure_diagnosis",
            "external_source_policy_candidate",
            "diagnosis_only_partial_newton_failure_not_promoted",
            True,
        ),
        file_item(
            "HI2022_RA_HALF_DOUBLE_SOURCE_POLICY_FAILURE_DIAGNOSIS.md",
            "human_readable_hi2022_ra_half_double_source_policy_failure_diagnosis",
            "external_source_policy_candidate",
            "diagnosis_only_partial_newton_failure_not_promoted",
            True,
        ),
        file_item(
            "HI2022_RA_HALF_DOUBLE_REPAIR_ATTEMPT_CERTIFICATE.json",
            "hi2022_ra_half_double_repair_attempt_certificate",
            "external_source_policy_candidate",
            "targeted_repair_attempted_not_reproducible_not_promoted",
            False,
        ),
        file_item(
            "HI2022_RA_HALF_DOUBLE_REPAIR_ATTEMPT_CERTIFICATE.md",
            "human_readable_hi2022_ra_half_double_repair_attempt_certificate",
            "external_source_policy_candidate",
            "targeted_repair_attempted_not_reproducible_not_promoted",
            False,
        ),
        file_item(
            "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.json",
            "b4_source_policy_row_closure_readiness_ledger",
            "external_source_policy_candidate",
            "all_40_external_rows_mapped_b4_open",
            True,
        ),
        file_item(
            "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.md",
            "human_readable_b4_source_policy_row_closure_readiness_ledger",
            "external_source_policy_candidate",
            "all_40_external_rows_mapped_b4_open",
            True,
        ),
        file_item(
            "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.csv",
            "tabular_b4_source_policy_row_closure_readiness_ledger",
            "external_source_policy_candidate",
            "all_40_external_rows_mapped_b4_open",
            True,
        ),
        file_item(
            "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json",
            "b4_source_policy_execution_opt_in_packet",
            "external_source_policy_candidate",
            "ready_for_user_opt_in_not_run",
            False,
        ),
        file_item(
            "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.md",
            "human_readable_b4_source_policy_execution_opt_in_packet",
            "external_source_policy_candidate",
            "ready_for_user_opt_in_not_run",
            False,
        ),
        file_item(
            "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json",
            "b4_source_policy_execution_handoff_package",
            "external_source_policy_candidate",
            "handoff_ready_not_authorized_not_run",
            False,
        ),
        file_item(
            "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.md",
            "human_readable_b4_source_policy_execution_handoff_package",
            "external_source_policy_candidate",
            "handoff_ready_not_authorized_not_run",
            False,
        ),
        file_item(
            "B4_SOURCE_POLICY_COMMAND_PREFLIGHT_FREEZE_20260620.json",
            "b4_source_policy_command_preflight_freeze",
            "external_source_policy_candidate",
            "command_preflight_frozen_not_authorized_not_run_not_promoted",
            False,
        ),
        file_item(
            "B4_SOURCE_POLICY_COMMAND_PREFLIGHT_FREEZE_20260620.md",
            "human_readable_b4_source_policy_command_preflight_freeze",
            "external_source_policy_candidate",
            "command_preflight_frozen_not_authorized_not_run_not_promoted",
            False,
        ),
        file_item(
            "build_b4_source_policy_command_preflight_freeze_20260620.py",
            "builder_b4_source_policy_command_preflight_freeze",
            "external_source_policy_candidate",
            "read_only_freeze_builder",
            False,
        ),
        file_item(
            "validate_b4_source_policy_command_preflight_freeze_20260620.py",
            "validator_b4_source_policy_command_preflight_freeze",
            "external_source_policy_candidate",
            "read_only_freeze_validator",
            False,
        ),
        file_item(
            "B4_SOURCE_POLICY_EXPECTED_OUTPUT_SCHEMA_AUDIT_20260620.json",
            "b4_source_policy_expected_output_schema_audit",
            "external_source_policy_candidate",
            "expected_outputs_schema_ready_not_authorized_not_run_not_promoted",
            False,
        ),
        file_item(
            "B4_SOURCE_POLICY_EXPECTED_OUTPUT_SCHEMA_AUDIT_20260620.md",
            "human_readable_b4_source_policy_expected_output_schema_audit",
            "external_source_policy_candidate",
            "expected_outputs_schema_ready_not_authorized_not_run_not_promoted",
            False,
        ),
        file_item(
            "build_b4_source_policy_expected_output_schema_audit_20260620.py",
            "builder_b4_source_policy_expected_output_schema_audit",
            "external_source_policy_candidate",
            "read_only_schema_audit_builder",
            False,
        ),
        file_item(
            "validate_b4_source_policy_expected_output_schema_audit_20260620.py",
            "validator_b4_source_policy_expected_output_schema_audit",
            "external_source_policy_candidate",
            "read_only_schema_audit_validator",
            False,
        ),
        file_item(
            "B4_EXPECTED_OUTPUT_PROMOTION_READINESS_BLOCKER_AUDIT_20260620.json",
            "b4_expected_output_promotion_readiness_blocker_audit",
            "external_source_policy_candidate",
            "expected_outputs_schema_ready_but_promotion_blocked",
            False,
        ),
        file_item(
            "B4_EXPECTED_OUTPUT_PROMOTION_READINESS_BLOCKER_AUDIT_20260620.md",
            "human_readable_b4_expected_output_promotion_readiness_blocker_audit",
            "external_source_policy_candidate",
            "expected_outputs_schema_ready_but_promotion_blocked",
            False,
        ),
        file_item(
            "build_b4_expected_output_promotion_readiness_blocker_audit_20260620.py",
            "builder_b4_expected_output_promotion_readiness_blocker_audit",
            "external_source_policy_candidate",
            "read_only_promotion_readiness_blocker_builder",
            False,
        ),
        file_item(
            "validate_b4_expected_output_promotion_readiness_blocker_audit_20260620.py",
            "validator_b4_expected_output_promotion_readiness_blocker_audit",
            "external_source_policy_candidate",
            "read_only_promotion_readiness_blocker_validator",
            False,
        ),
        file_item(
            "OC6_SOURCE_EQUIVALENT_REOPEN_READINESS_AUDIT_20260620.json",
            "oc6_source_equivalent_reopen_readiness_audit",
            "external_source_policy_candidate",
            "oc6_reopen_conditions_monitored_no_positive_source_equivalent_artifact",
            False,
        ),
        file_item(
            "OC6_SOURCE_EQUIVALENT_REOPEN_READINESS_AUDIT_20260620.md",
            "human_readable_oc6_source_equivalent_reopen_readiness_audit",
            "external_source_policy_candidate",
            "oc6_reopen_conditions_monitored_no_positive_source_equivalent_artifact",
            False,
        ),
        file_item(
            "build_oc6_source_equivalent_reopen_readiness_audit_20260620.py",
            "builder_oc6_source_equivalent_reopen_readiness_audit",
            "external_source_policy_candidate",
            "read_only_oc6_reopen_readiness_builder",
            False,
        ),
        file_item(
            "validate_oc6_source_equivalent_reopen_readiness_audit_20260620.py",
            "validator_oc6_source_equivalent_reopen_readiness_audit",
            "external_source_policy_candidate",
            "read_only_oc6_reopen_readiness_validator",
            False,
        ),
        file_item(
            "cmame_p1_single_runner_candidate/README.md",
            "p1_single_runner_candidate_readme",
            "candidate_runner_source",
            "single_runner_candidate_not_p1_complete",
            True,
        ),
        file_item(
            "cmame_p1_single_runner_candidate/scripts/run_single_pendulum_fullva.py",
            "p1_single_runner_candidate_entrypoint",
            "candidate_runner_source",
            "single_runner_candidate_not_p1_complete",
            True,
        ),
        file_item(
            "cmame_p1_single_runner_candidate/results/single_pendulum_summary.json",
            "p1_single_runner_candidate_summary",
            "candidate_runner_result",
            "single_runner_candidate_not_p1_complete",
            True,
        ),
        file_item(
            "cmame_p1_single_runner_candidate/results/single_pendulum_rows.csv",
            "p1_single_runner_candidate_rows",
            "candidate_runner_result",
            "single_runner_candidate_not_p1_complete",
            True,
        ),
        file_item(
            "validate_cmame_p1_single_runner_candidate.py",
            "p1_single_runner_candidate_validator",
            "candidate_runner_validation",
            "single_runner_candidate_not_p1_complete",
            True,
        ),
        file_item(
            "cmame_p1_double_runner_candidate/README.md",
            "p1_double_runner_candidate_readme",
            "candidate_runner_source",
            "double_runner_candidate_not_source_policy_or_proof_complete",
            True,
        ),
        file_item(
            "cmame_p1_double_runner_candidate/scripts/run_double_pendulum_fullva.py",
            "p1_double_runner_candidate_entrypoint",
            "candidate_runner_source",
            "double_runner_candidate_not_source_policy_or_proof_complete",
            True,
        ),
        file_item(
            "cmame_p1_double_runner_candidate/results/double_pendulum_summary.json",
            "p1_double_runner_candidate_summary",
            "candidate_runner_result",
            "double_runner_candidate_not_source_policy_or_proof_complete",
            True,
        ),
        file_item(
            "cmame_p1_double_runner_candidate/results/double_pendulum_rows.csv",
            "p1_double_runner_candidate_rows",
            "candidate_runner_result",
            "double_runner_candidate_not_source_policy_or_proof_complete",
            True,
        ),
        file_item(
            "validate_cmame_p1_double_runner_candidate.py",
            "p1_double_runner_candidate_validator",
            "candidate_runner_validation",
            "double_runner_candidate_not_source_policy_or_proof_complete",
            True,
        ),
        file_item(
            "CMAME_LOCAL_ACCEPTED_RUNNER_COMPANION_MANIFEST.json",
            "local_accepted_runner_companion_metadata",
            "candidate_runner_validation",
            "local_accepted_runner_companion_ready_source_policy_package_open",
            True,
        ),
        file_item(
            "CMAME_LOCAL_ACCEPTED_RUNNER_COMPANION_MANIFEST.md",
            "human_readable_local_accepted_runner_companion",
            "candidate_runner_validation",
            "local_accepted_runner_companion_ready_source_policy_package_open",
            True,
        ),
        file_item(
            "build_cmame_local_accepted_runner_companion.py",
            "local_accepted_runner_companion_builder",
            "candidate_runner_validation",
            "local_accepted_runner_companion_ready_source_policy_package_open",
            True,
        ),
        file_item(
            "validate_cmame_local_accepted_runner_companion.py",
            "local_accepted_runner_companion_validator",
            "candidate_runner_validation",
            "local_accepted_runner_companion_ready_source_policy_package_open",
            True,
        ),
        file_item(
            "cmame_local_accepted_runner_companion/README.md",
            "local_accepted_runner_companion_readme",
            "candidate_runner_result",
            "local_accepted_runner_companion_ready_source_policy_package_open",
            True,
        ),
        file_item(
            "cmame_local_accepted_runner_companion/MANIFEST.json",
            "local_accepted_runner_companion_package_manifest",
            "candidate_runner_result",
            "local_accepted_runner_companion_ready_source_policy_package_open",
            True,
        ),
        file_item(
            "cmame_local_accepted_runner_companion/scripts/run_local_accepted_runner_companion.py",
            "local_accepted_runner_companion_launcher",
            "candidate_runner_result",
            "local_accepted_runner_companion_ready_source_policy_package_open",
            True,
        ),
        file_item(
            "cmame_narrowed_repro_bundle/README.md",
            "narrowed_repro_bundle_readme",
            "candidate_runner_result",
            "narrowed_repro_bundle_ready_replay_plus_local_runners_source_policy_open",
            True,
        ),
        file_item(
            "cmame_narrowed_repro_bundle/MANIFEST.json",
            "narrowed_repro_bundle_manifest",
            "candidate_runner_result",
            "narrowed_repro_bundle_ready_replay_plus_local_runners_source_policy_open",
            True,
        ),
        file_item(
            "cmame_narrowed_repro_bundle/scripts/run_narrowed_repro_bundle.py",
            "narrowed_repro_bundle_launcher",
            "candidate_runner_result",
            "narrowed_repro_bundle_ready_replay_plus_local_runners_source_policy_open",
            True,
        ),
        file_item(
            "cmame_narrowed_repro_bundle/results/narrowed_repro_bundle_report.md",
            "narrowed_repro_bundle_report",
            "candidate_runner_result",
            "narrowed_repro_bundle_ready_replay_plus_local_runners_source_policy_open",
            True,
        ),
        file_item(
            "cmame_narrowed_repro_bundle/results/narrowed_repro_bundle_summary.json",
            "narrowed_repro_bundle_summary_json",
            "candidate_runner_result",
            "narrowed_repro_bundle_ready_replay_plus_local_runners_source_policy_open",
            True,
        ),
        file_item(
            "cmame_narrowed_repro_bundle/results/narrowed_repro_bundle_summary.md",
            "narrowed_repro_bundle_summary_md",
            "candidate_runner_result",
            "narrowed_repro_bundle_ready_replay_plus_local_runners_source_policy_open",
            True,
        ),
        file_item(
            "validate_cmame_narrowed_repro_bundle.py",
            "narrowed_repro_bundle_validator",
            "candidate_runner_validation",
            "narrowed_repro_bundle_ready_replay_plus_local_runners_source_policy_open",
            True,
        ),
        file_item(
            "cmame_narrowed_repro_code_archive.zip",
            "narrowed_repro_code_archive",
            "candidate_runner_result",
            "narrowed_repro_code_archive_ready_source_policy_open",
            True,
        ),
        file_item(
            "CMAME_NARROWED_REPRO_CODE_ARCHIVE_MANIFEST.json",
            "narrowed_repro_code_archive_metadata",
            "candidate_runner_validation",
            "narrowed_repro_code_archive_ready_source_policy_open",
            True,
        ),
        file_item(
            "CMAME_NARROWED_REPRO_CODE_ARCHIVE_MANIFEST.md",
            "human_readable_narrowed_repro_code_archive_manifest",
            "candidate_runner_validation",
            "narrowed_repro_code_archive_ready_source_policy_open",
            True,
        ),
        file_item(
            "build_cmame_narrowed_repro_code_archive.py",
            "narrowed_repro_code_archive_builder",
            "candidate_runner_validation",
            "narrowed_repro_code_archive_ready_source_policy_open",
            True,
        ),
        file_item(
            "validate_cmame_narrowed_repro_code_archive.py",
            "narrowed_repro_code_archive_validator",
            "candidate_runner_validation",
            "narrowed_repro_code_archive_ready_source_policy_open",
            True,
        ),
        file_item(
            "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json",
            "full_source_policy_runner_archive_gap_audit",
            "candidate_runner_validation",
            "full_source_policy_runner_archive_not_ready_source_policy_open",
            False,
        ),
        file_item(
            "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.md",
            "human_readable_full_source_policy_runner_archive_gap_audit",
            "candidate_runner_validation",
            "full_source_policy_runner_archive_not_ready_source_policy_open",
            False,
        ),
        file_item(
            "build_full_source_policy_runner_archive_gap_audit.py",
            "full_source_policy_runner_archive_gap_audit_builder",
            "candidate_runner_validation",
            "full_source_policy_runner_archive_not_ready_source_policy_open",
            False,
        ),
        file_item(
            "validate_full_source_policy_runner_archive_gap_audit.py",
            "full_source_policy_runner_archive_gap_audit_validator",
            "candidate_runner_validation",
            "full_source_policy_runner_archive_not_ready_source_policy_open",
            False,
        ),
    ]

    package_layers = [
        {
            "id": "L0",
            "name": "manuscript and journal sidecars",
            "status": "artifact_present_not_global_submission_ready",
            "evidence": ["main_cmame.pdf", "main_cmame.tex", "highlights_cmame.txt", "declarations_cmame.md"],
        },
        {
            "id": "L1",
            "name": "paper order/error result table",
            "status": "common_reference_artifact_present_source_policy_open",
            "evidence": [
                "PAPER_NUMERICAL_RESULT_MATRIX.csv",
                "PAPER_NUMERICAL_RESULT_MATRIX.json",
                "RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.json",
            ],
        },
        {
            "id": "L2",
            "name": "narrowed reproducibility bundle for paper evidence",
            "status": "narrowed_repro_bundle_ready_replay_plus_local_runners_source_policy_open",
            "evidence": [
                "CMAME_NARROWED_REPRODUCIBILITY_PACKAGE_AUDIT.json",
                "cmame_narrowed_repro_code_archive.zip",
                "CMAME_NARROWED_REPRO_CODE_ARCHIVE_MANIFEST.json",
                "cmame_narrowed_repro_bundle/MANIFEST.json",
                "cmame_narrowed_repro_bundle/scripts/run_narrowed_repro_bundle.py",
                "cmame_narrowed_repro_bundle/results/narrowed_repro_bundle_summary.json",
                "CMAME_MINIMAL_REPRODUCIBILITY_CANDIDATE_MANIFEST.json",
                "cmame_minimal_reproducibility_candidate/scripts/replay_paper_matrix.py",
                "REPRODUCIBILITY_GUIDE.md",
                "replay_reproducibility_core.py",
                "run_human_reproducibility.py",
                "human_reproducibility_result_table.md",
                "run_b6_four_example_local_evidence.py",
                "B6_FOUR_EXAMPLE_LOCAL_EVIDENCE_SUMMARY.json",
                "validate_b6_four_example_local_evidence.py",
                "B6_CLOSED_LOOP_SELF_CONTAINED_EXTRACTION_AUDIT.json",
                "validate_b6_closed_loop_self_contained_extraction_audit.py",
                "CMAME_CLOSED_LOOP_LOCAL_RUNNER_CANDIDATE_MANIFEST.json",
                "validate_cmame_closed_loop_local_runner_candidate.py",
                "cmame_closed_loop_local_runner_candidate/scripts/run_closed_loop_fullva_candidate.py",
                "cmame_closed_loop_local_runner_candidate/results/closed_loop_local_summary.json",
                "cmame_p1_single_runner_candidate/scripts/run_single_pendulum_fullva.py",
                "cmame_p1_single_runner_candidate/results/single_pendulum_summary.json",
                "cmame_p1_double_runner_candidate/scripts/run_double_pendulum_fullva.py",
                "cmame_p1_double_runner_candidate/results/double_pendulum_summary.json",
                "CMAME_LOCAL_ACCEPTED_RUNNER_COMPANION_MANIFEST.json",
                "cmame_local_accepted_runner_companion/scripts/run_local_accepted_runner_companion.py",
            ],
        },
        {
            "id": "L3",
            "name": "external source-policy same-test runners",
            "status": "open",
            "evidence": [
                "RA2021_SOURCE_POLICY_ROW_AUDIT.json",
                "HI2022_SOURCE_POLICY_ROW_AUDIT.json",
                "TFE_SOURCE_POLICY_ROW_AUDIT.json",
                "TFE_SOURCE_PENDULUM_MODEL_AUDIT.json",
                "TFE_BROWN_MCPHEE_SOURCE_LAW_BOUNDARY_AUDIT.json",
                "TFE_BROWN_MCPHEE_SOURCE_CODE_EQUIVALENCE_CERTIFICATE.json",
                "TFE_FULL_T10_ABSOLUTE_DAE_LIFT_SUMMARY.json",
                "TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.json",
                "TFE_PUBLIC_CODE_RECHECK_20260613.json",
                "VP2024_PUBLIC_CODE_RECHECK_20260613.json",
                "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.json",
                "TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.json",
                "TFE_FULL_T10_ENDPOINT_POLICY_CLOSURE_CERTIFICATE.json",
                "B4_SOURCE_POLICY_WORK_PRECISION_EXECUTION_PLAN.json",
                "B4_EXISTING_ARTIFACT_PROMOTION_AUDIT.json",
                "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.json",
                "FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.json",
                "RA_HI_SOURCE_POLICY_POST_EXECUTION_ATTEMPT_CERTIFICATE.json",
                "RA_HI_SOURCE_POLICY_CLOSEOUT_CHECKLIST.json",
                "RA_HI_SOURCE_POLICY_OUTPUT_INVENTORY.json",
                "RA_HI_SOURCE_POLICY_PROMOTION_BLOCKER_MATRIX.json",
                "RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.json",
                "HI2022_RA_HALF_DOUBLE_SOURCE_POLICY_FAILURE_DIAGNOSIS.json",
                "HI2022_RA_HALF_DOUBLE_REPAIR_ATTEMPT_CERTIFICATE.json",
                "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.json",
                "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json",
            ],
        },
        {
            "id": "L4",
            "name": "symbolic proof certificate supplement",
            "status": "open",
            "evidence": ["PROOF_CLOSURE_MANIFEST.json", "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.json"],
        },
    ]

    missing_components = [
        {
            "id": "tfe_original_pendulum_source_policy_runner",
            "status": "missing",
            "required_to_close": "implement original TFE pendulum DAE runner, error norm, friction law, and output policy",
        },
        {
            "id": "ra2021_same_policy_local_dynamic_rows",
            "status": "open",
            "required_to_close": "promote or rerun local Gauss6/FullVA rows under the 2021 public source policy",
        },
        {
            "id": "hi2022_full_T8_policy_rows",
            "status": "open",
            "required_to_close": "run full T=8 source-policy rows or explicitly demote the suite",
        },
        {
            "id": "source_policy_work_precision_execution_plan",
            "status": "b4_b7_open_plan_ready",
            "required_to_close": "execute or explicitly demote source-policy work/precision lanes before B4/B7 publication figures can close",
        },
        {
            "id": "newton_euler_symbolic_defect_certificate",
            "status": "open",
            "required_to_close": "close the symbolic/primitive Newton-Euler certificate route; the direct D5/PC2 stage-residual route is tracked separately",
        },
        {
            "id": "full_source_policy_runner_archive",
            "status": "partial_local_runner_package_ready_source_policy_open",
            "required_to_close": "promote the current local self-contained runner evidence into a full source-policy runner archive after source-policy and TFE runner gates close",
        },
    ]

    summary = {
        "paper_artifact_bundle_ready": True,
        "paper_core_result_table_ready": code_checks.get("paper_core_result_table_ready"),
        "paper_numerical_matrix_rows": numerical.get("row_count"),
        "paper_numerical_matrix_raw_rows": numerical.get("raw_row_count"),
        "result_to_manuscript_traceability_closed": traceability.get("claim_boundary", {}).get(
            "result_to_manuscript_traceability_closed"
        ),
        "common_reference_order_wins": result_checks.get("comparison_reconciliation_direct_order_wins"),
        "common_reference_order_comparisons": result_checks.get("comparison_reconciliation_direct_order_comparisons"),
        "common_reference_error_wins": result_checks.get("comparison_reconciliation_direct_error_wins"),
        "common_reference_error_comparisons": result_checks.get("comparison_reconciliation_direct_error_comparisons"),
        "source_policy_closed_rows": code_checks.get("source_policy_closed_rows"),
        "source_policy_total_rows": code_checks.get("source_policy_total_rows"),
        "source_policy_external_superiority_allowed": result_checks.get("source_policy_superiority_claim_allowed"),
        "source_policy_public_code_refresh_status": source_policy_public_code_refresh.get("status"),
        "source_policy_public_code_refresh_date": source_policy_public_code_refresh.get("date_checked"),
        "source_policy_public_code_refresh_rows": source_policy_public_code_refresh.get("row_count"),
        "source_policy_public_code_refresh_public_code_available_rows": source_policy_public_code_refresh.get(
            "public_code_available_rows"
        ),
        "source_policy_public_code_refresh_self_reproduction_attempted_rows": source_policy_public_code_refresh.get(
            "self_reproduction_attempted_rows"
        ),
        "source_policy_public_code_refresh_unable_to_reproduce_rows": source_policy_public_code_refresh.get(
            "unable_to_reproduce_rows"
        ),
        "source_policy_public_code_refresh_source_policy_rows_closed": source_policy_public_code_refresh.get(
            "source_policy_rows_closed"
        ),
        "source_policy_public_code_refresh_latest_status": source_policy_public_code_refresh_latest.get("status"),
        "source_policy_public_code_refresh_latest_date": source_policy_public_code_refresh_latest.get("date_checked"),
        "source_policy_public_code_refresh_latest_rows": source_policy_public_code_refresh_latest.get("row_count"),
        "source_policy_public_code_refresh_latest_current_queries": source_policy_public_code_refresh_latest.get(
            "current_query_count"
        ),
        "source_policy_public_code_refresh_latest_positive_artifact_rows": (
            source_policy_public_code_refresh_latest.get("positive_public_code_artifact_rows")
        ),
        "source_policy_public_code_refresh_latest_source_policy_rows_closed": (
            source_policy_public_code_refresh_latest.get("source_policy_rows_closed")
        ),
        "source_policy_public_code_refresh_latest_source_policy_rows_promoted": (
            source_policy_public_code_refresh_latest.get("source_policy_rows_promoted")
        ),
        "source_policy_public_code_refresh_latest_external_probe_date": (
            source_policy_public_code_refresh_latest.get("latest_external_probe_date_checked")
        ),
        "source_policy_public_code_refresh_latest_external_probe_count": (
            source_policy_public_code_refresh_latest.get("latest_external_probe_count")
        ),
        "source_policy_public_code_refresh_latest_external_probe_positive_artifact_rows": (
            source_policy_public_code_refresh_latest.get(
                "latest_external_probe_positive_public_code_artifact_rows"
            )
        ),
        "source_policy_public_code_refresh_latest_external_probe_source_policy_rows_closed": (
            source_policy_public_code_refresh_latest.get(
                "latest_external_probe_source_policy_rows_closed"
            )
        ),
        "source_policy_public_code_refresh_latest_external_probe_access_limited_count": (
            source_policy_public_code_refresh_latest.get(
                "latest_external_probe_access_limited_count"
            )
        ),
        "source_policy_public_code_refresh_latest_external_probe_global_absence_proved": (
            source_policy_public_code_refresh_latest.get(
                "latest_external_probe_global_absence_proved"
            )
        ),
        "source_policy_public_code_refresh_latest_external_probe_reopen_triggered": (
            source_policy_public_code_refresh_latest.get(
                "latest_external_probe_source_policy_reopen_triggered"
            )
        ),
        "vp2024_public_code_recheck_status": vp2024_public_code_recheck.get("status"),
        "vp2024_public_code_recheck_date": vp2024_public_code_recheck.get("date_checked"),
        "vp2024_public_code_recheck_tree_truncated": vp2024_public_code_recheck.get("coverage", {}).get(
            "tree_truncated"
        ),
        "vp2024_public_code_recheck_tree_total_paths": vp2024_public_code_recheck.get("coverage", {}).get(
            "tree_total_paths"
        ),
        "vp2024_public_code_recheck_year2024_paths": vp2024_public_code_recheck.get("coverage", {}).get(
            "year2024_path_count"
        ),
        "vp2024_public_code_recheck_keyword_hits": vp2024_public_code_recheck.get("coverage", {}).get(
            "keyword_path_hit_count"
        ),
        "vp2024_public_code_recheck_rows_attempted_not_reproducible": vp2024_public_code_recheck.get(
            "coverage", {}
        ).get("source_policy_rows_attempted_not_reproducible"),
        "vp2024_public_code_recheck_source_policy_rows_closed": vp2024_public_code_recheck.get(
            "coverage", {}
        ).get("source_policy_rows_closed"),
        "vp2024_public_code_recheck_external_superiority_allowed": vp2024_public_code_recheck.get(
            "claim_boundary", {}
        ).get("external_superiority_claim_allowed"),
        "b4_work_precision_plan_status": b4_plan.get("status"),
        "b4_work_precision_plan_b4_can_close_now": b4_plan.get("b4_can_close_now"),
        "b4_work_precision_plan_b7_can_close_now": b4_plan.get("b7_can_close_now"),
        "b4_work_precision_plan_ready_lane_count": b4_plan.get("execution_lane_summary", {}).get(
            "ready_to_launch_after_explicit_opt_in_count"
        ),
        "b4_work_precision_plan_not_ready_lane_count": b4_plan.get("execution_lane_summary", {}).get(
            "not_ready_lane_count"
        ),
        "b4_work_precision_plan_source_policy_rows_closed": b4_plan.get("execution_lane_summary", {}).get(
            "source_policy_rows_closed_after_plan"
        ),
        "b4_work_precision_plan_source_policy_rows_total": b4_plan.get("execution_lane_summary", {}).get(
            "source_policy_rows_total"
        ),
        "b4_existing_promotion_audit_status": b4_existing_promotion_audit.get("status"),
        "b4_existing_promotion_candidate_items": b4_existing_promotion_audit.get("candidate_item_count"),
        "b4_existing_promotion_ready_without_new_execution": b4_existing_promotion_audit.get(
            "promotion_ready_without_new_execution_count"
        ),
        "b4_existing_promotion_source_policy_rows_closed": b4_existing_promotion_audit.get(
            "source_policy_rows_closed_by_existing_artifacts"
        ),
        "b4_existing_promotion_source_policy_rows_total": b4_existing_promotion_audit.get(
            "source_policy_rows_total"
        ),
        "b4_existing_promotion_b4_closing_items": b4_existing_promotion_audit.get("b4_closing_item_count"),
        "b4_existing_promotion_b7_closing_items": b4_existing_promotion_audit.get("b7_closing_item_count"),
        "b4_post_execution_audit_status": b4_post_execution_audit.get("status"),
        "b4_post_execution_audit_approved_driver_execution_recorded": b4_post_execution_audit.get(
            "approved_driver_execution_recorded"
        ),
        "b4_post_execution_audit_verified_authorized_execution_recorded": b4_post_execution_audit.get(
            "verified_authorized_execution_recorded"
        ),
        "b4_post_execution_audit_existing_ready_command_artifacts_present": b4_post_execution_audit.get(
            "existing_ready_command_artifacts_present"
        ),
        "b4_post_execution_audit_execution_record_scope": b4_post_execution_audit.get(
            "execution_record_scope"
        ),
        "b4_post_execution_audit_ready_command_count": b4_post_execution_audit.get("guarded_driver", {}).get(
            "ready_command_count"
        ),
        "b4_post_execution_audit_mapped_external_rows": b4_post_execution_audit.get("guarded_driver", {}).get(
            "ready_command_mapped_external_rows"
        ),
        "b4_post_execution_audit_unaddressed_external_rows": b4_post_execution_audit.get(
            "guarded_driver", {}
        ).get("unaddressed_external_rows_after_ready_commands"),
        "b4_post_execution_audit_expected_outputs_present": b4_post_execution_audit.get(
            "command_artifact_presence", {}
        ).get("all_expected_outputs_exist_now"),
        "b4_post_execution_audit_source_policy_rows_closed": b4_post_execution_audit.get(
            "row_status_after_driver", {}
        ).get("source_policy_rows_closed"),
        "b4_post_execution_audit_source_policy_rows_total": b4_post_execution_audit.get(
            "row_status_after_driver", {}
        ).get("source_policy_rows_total"),
        "b4_post_execution_audit_b4_can_close_now": b4_post_execution_audit.get(
            "row_status_after_driver", {}
        ).get("b4_can_close_now"),
        "b4_post_execution_audit_b7_can_close_now": b4_post_execution_audit.get(
            "row_status_after_driver", {}
        ).get("b7_can_close_now"),
        "full_source_policy_row_provenance_status": full_source_policy_row_provenance_audit.get("status"),
        "full_source_policy_row_provenance_action_boundary": full_source_policy_row_provenance_audit.get(
            "action_boundary"
        ),
        "full_source_policy_row_provenance_source_policy_execution_invoked": (
            full_source_policy_row_provenance_audit.get("source_policy_execution_invoked")
        ),
        "full_source_policy_row_provenance_rows": full_source_policy_row_provenance_audit.get("row_count"),
        "full_source_policy_row_provenance_preflight_complete_rows": full_source_policy_row_provenance_audit.get(
            "provenance_preflight_complete_rows"
        ),
        "full_source_policy_row_provenance_public_source_root_rows": full_source_policy_row_provenance_audit.get(
            "public_source_root_rows"
        ),
        "full_source_policy_row_provenance_unable_to_reproduce_rows": full_source_policy_row_provenance_audit.get(
            "source_policy_rows_unable_to_reproduce"
        ),
        "full_source_policy_row_provenance_promotion_ready_rows": full_source_policy_row_provenance_audit.get(
            "promotion_ready_rows"
        ),
        "full_source_policy_row_provenance_source_policy_closed_rows": full_source_policy_row_provenance_audit.get(
            "source_policy_rows_closed"
        ),
        "full_source_policy_row_provenance_handoff_status": full_source_policy_row_provenance_audit.get(
            "source_policy_execution_handoff", {}
        ).get("status"),
        "full_source_policy_row_provenance_handoff_authorized": full_source_policy_row_provenance_audit.get(
            "source_policy_execution_handoff", {}
        ).get("execution_authorized"),
        "full_source_policy_row_provenance_handoff_commands_not_run": full_source_policy_row_provenance_audit.get(
            "source_policy_execution_handoff", {}
        ).get("commands_not_run_by_handoff"),
        "full_source_policy_row_provenance_handoff_driver": full_source_policy_row_provenance_audit.get(
            "source_policy_execution_handoff", {}
        ).get("guarded_execution_driver"),
        "full_source_policy_row_provenance_handoff_driver_requires_exact": full_source_policy_row_provenance_audit.get(
            "source_policy_execution_handoff", {}
        ).get("driver_requires_exact_approval"),
        "full_source_policy_row_provenance_handoff_driver_does_not_authorize": full_source_policy_row_provenance_audit.get(
            "source_policy_execution_handoff", {}
        ).get("driver_does_not_authorize_execution"),
        "full_source_policy_row_provenance_handoff_exact_approval": full_source_policy_row_provenance_audit.get(
            "source_policy_execution_handoff", {}
        ).get("exact_required_user_approval_statement"),
        "full_source_policy_row_provenance_handoff_opt_in_commands": full_source_policy_row_provenance_audit.get(
            "source_policy_execution_handoff", {}
        ).get("opt_in_required_command_count"),
        "full_source_policy_row_provenance_handoff_mapped_rows": full_source_policy_row_provenance_audit.get(
            "source_policy_execution_handoff", {}
        ).get("opt_in_required_mapped_external_rows"),
        "full_source_policy_row_provenance_handoff_terminal_unable_rows": full_source_policy_row_provenance_audit.get(
            "source_policy_execution_handoff", {}
        ).get("terminal_unable_to_reproduce_rows"),
        "ra_hi_source_policy_closeout_checklist_status": ra_hi_source_policy_closeout_checklist.get("status"),
        "ra_hi_source_policy_closeout_total_rows": ra_hi_source_policy_closeout_checklist.get("coverage", {}).get(
            "source_policy_rows_total"
        ),
        "ra_hi_source_policy_closeout_ra_rows": ra_hi_source_policy_closeout_checklist.get("coverage", {}).get(
            "ra2021_rows"
        ),
        "ra_hi_source_policy_closeout_hi_rows": ra_hi_source_policy_closeout_checklist.get("coverage", {}).get(
            "hi2022_rows"
        ),
        "ra_hi_source_policy_closeout_ready_commands": ra_hi_source_policy_closeout_checklist.get(
            "coverage", {}
        ).get("ready_command_count"),
        "ra_hi_source_policy_closeout_mapped_rows": ra_hi_source_policy_closeout_checklist.get(
            "coverage", {}
        ).get("ready_command_mapped_external_rows"),
        "ra_hi_source_policy_closeout_promoted_rows": ra_hi_source_policy_closeout_checklist.get(
            "coverage", {}
        ).get("source_policy_rows_promoted"),
        "ra_hi_source_policy_closeout_completed_rows": ra_hi_source_policy_closeout_checklist.get(
            "coverage", {}
        ).get("source_policy_rows_completed"),
        "ra_hi_source_policy_closeout_external_ready_rows": ra_hi_source_policy_closeout_checklist.get(
            "coverage", {}
        ).get("external_superiority_ready_rows"),
        "ra_hi_source_policy_closeout_opt_in_required": ra_hi_source_policy_closeout_checklist.get(
            "guarded_execution_boundary", {}
        ).get("explicit_user_opt_in_required_before_any_command"),
        "ra_hi_source_policy_closeout_execution_invoked": ra_hi_source_policy_closeout_checklist.get(
            "guarded_execution_boundary", {}
        ).get("execution_invoked_by_packet"),
        "ra_hi_source_policy_closeout_b4_can_close": ra_hi_source_policy_closeout_checklist.get(
            "not_promoted_disposition", {}
        ).get("b4_can_close_from_this_checklist"),
        "ra_hi_source_policy_closeout_b7_can_close": ra_hi_source_policy_closeout_checklist.get(
            "not_promoted_disposition", {}
        ).get("b7_can_close_from_this_checklist"),
        "ra_hi_source_policy_output_inventory_status": ra_hi_source_policy_output_inventory.get("status"),
        "ra_hi_source_policy_output_inventory_command_count": ra_hi_source_policy_output_inventory.get(
            "coverage", {}
        ).get("command_count"),
        "ra_hi_source_policy_output_inventory_outputs_existing": ra_hi_source_policy_output_inventory.get(
            "coverage", {}
        ).get("expected_output_existing_count"),
        "ra_hi_source_policy_output_inventory_summaries_existing": ra_hi_source_policy_output_inventory.get(
            "coverage", {}
        ).get("expected_summary_existing_count"),
        "ra_hi_source_policy_output_inventory_csv_data_rows": ra_hi_source_policy_output_inventory.get(
            "coverage", {}
        ).get("expected_output_csv_data_rows"),
        "ra_hi_source_policy_output_inventory_hi_ok_rows": ra_hi_source_policy_output_inventory.get(
            "coverage", {}
        ).get("hi2022_summary_ok_rows"),
        "ra_hi_source_policy_output_inventory_closed_rows": ra_hi_source_policy_output_inventory.get(
            "coverage", {}
        ).get("source_policy_rows_closed_by_inventory"),
        "ra_hi_source_policy_promotion_blocker_matrix_status": ra_hi_source_policy_promotion_blocker_matrix.get(
            "status"
        ),
        "ra_hi_source_policy_promotion_blocker_matrix_rows": ra_hi_source_policy_promotion_blocker_matrix.get(
            "row_count"
        ),
        "ra_hi_source_policy_promotion_blocker_matrix_ra_rows": ra_hi_source_policy_promotion_blocker_matrix.get(
            "ra2021_row_count"
        ),
        "ra_hi_source_policy_promotion_blocker_matrix_hi_rows": ra_hi_source_policy_promotion_blocker_matrix.get(
            "hi2022_row_count"
        ),
        "ra_hi_source_policy_promotion_blocker_matrix_public_root_rows": ra_hi_source_policy_promotion_blocker_matrix.get(
            "public_source_root_available_rows"
        ),
        "ra_hi_source_policy_promotion_blocker_matrix_no_public_code_rows": ra_hi_source_policy_promotion_blocker_matrix.get(
            "no_public_code_rows_included"
        ),
        "ra_hi_source_policy_promotion_blocker_matrix_closed_rows": ra_hi_source_policy_promotion_blocker_matrix.get(
            "source_policy_rows_closed"
        ),
        "ra_hi_source_policy_promotion_blocker_matrix_not_promoted_rows": ra_hi_source_policy_promotion_blocker_matrix.get(
            "source_policy_rows_not_promoted"
        ),
        "ra_hi_source_policy_promotion_blocker_matrix_attempted_not_reproducible_rows": ra_hi_source_policy_promotion_blocker_matrix.get(
            "attempted_not_reproducible_rows"
        ),
        "ra_hi_source_policy_promotion_blocker_matrix_current_evidence_terminal_rows": ra_hi_source_policy_promotion_blocker_matrix.get(
            "current_evidence_terminal_not_promotable_rows"
        ),
        "ra_hi_source_policy_promotion_blocker_matrix_future_authorization_or_artifact_rows": ra_hi_source_policy_promotion_blocker_matrix.get(
            "future_promotion_requires_authorized_execution_or_new_artifact_rows"
        ),
        "ra_hi_source_policy_promotion_blocker_matrix_reproduction_complete_rows": ra_hi_source_policy_promotion_blocker_matrix.get(
            "source_policy_reproduction_complete_rows"
        ),
        "ra_hi_source_policy_promotion_blocker_matrix_command_mapped_rows": ra_hi_source_policy_promotion_blocker_matrix.get(
            "command_mapped_rows"
        ),
        "ra_hi_source_policy_promotion_blocker_matrix_output_present_rows": ra_hi_source_policy_promotion_blocker_matrix.get(
            "rows_with_all_command_outputs_present"
        ),
        "ra2021_double_low_order_diagnosis_status": ra2021_double_low_order.get("status"),
        "ra2021_double_low_order_fine_pair_floor_limited": ra2021_double_low_order.get(
            "diagnosis", {}
        ).get("fine_pair_floor_limited"),
        "ra2021_double_low_order_rows_promoted": ra2021_double_low_order.get(
            "promotion_decision", {}
        ).get("source_policy_rows_promoted_by_this_diagnosis"),
        "hi2022_ra_half_double_failure_diagnosis_status": hi2022_ra_half_double_failure.get("status"),
        "hi2022_ra_half_double_failure_rows_ok": hi2022_ra_half_double_failure.get(
            "execution_evidence", {}
        ).get("ok_row_count"),
        "hi2022_ra_half_double_failure_rows_failed": hi2022_ra_half_double_failure.get(
            "execution_evidence", {}
        ).get("failed_row_count"),
        "hi2022_ra_half_double_failure_rows_total": hi2022_ra_half_double_failure.get(
            "execution_evidence", {}
        ).get("row_count"),
        "hi2022_ra_half_double_failure_newton_failure_count": hi2022_ra_half_double_failure.get(
            "diagnosis", {}
        ).get("newton_failure_count"),
        "hi2022_ra_half_double_failure_pair_orders_available": hi2022_ra_half_double_failure.get(
            "diagnosis", {}
        ).get("pair_orders_available"),
        "hi2022_ra_half_double_failure_rows_promoted": hi2022_ra_half_double_failure.get(
            "promotion_decision", {}
        ).get("source_policy_rows_promoted_by_this_diagnosis"),
        "hi2022_ra_half_double_repair_attempt_status": hi2022_ra_half_double_repair.get("status"),
        "hi2022_ra_half_double_repair_target_ok_rows": hi2022_ra_half_double_repair.get(
            "tolerance_repair_evidence", {}
        ).get("combined_target_group", {}).get("ok_row_count"),
        "hi2022_ra_half_double_repair_target_failed_rows": hi2022_ra_half_double_repair.get(
            "tolerance_repair_evidence", {}
        ).get("combined_target_group", {}).get("failed_row_count"),
        "hi2022_ra_half_double_repair_combined_ok_rows": hi2022_ra_half_double_repair.get(
            "tolerance_repair_evidence", {}
        ).get("combined_best_ok_rows"),
        "hi2022_ra_half_double_repair_combined_row_count": hi2022_ra_half_double_repair.get(
            "tolerance_repair_evidence", {}
        ).get("combined_best_row_count"),
        "hi2022_ra_half_double_repair_combined_complete_groups": hi2022_ra_half_double_repair.get(
            "tolerance_repair_evidence", {}
        ).get("combined_best_complete_groups"),
        "hi2022_ra_half_double_repair_combined_group_count": hi2022_ra_half_double_repair.get(
            "tolerance_repair_evidence", {}
        ).get("combined_best_group_count"),
        "hi2022_ra_half_double_repair_rows_promoted": hi2022_ra_half_double_repair.get(
            "source_policy_rows_promoted"
        ),
        "b4_row_readiness_ledger_status": b4_row_readiness_ledger.get("status"),
        "b4_row_readiness_external_rows": b4_row_readiness_ledger.get("row_count"),
        "b4_row_readiness_expected_external_rows": b4_row_readiness_ledger.get("expected_external_row_count"),
        "b4_row_readiness_source_policy_rows_closed": b4_row_readiness_ledger.get("source_policy_rows_closed"),
        "b4_row_readiness_source_policy_rows_open": b4_row_readiness_ledger.get("source_policy_rows_open"),
        "b4_row_readiness_rows_with_launch_command_refs": b4_row_readiness_ledger.get(
            "rows_with_launch_command_refs"
        ),
        "b4_row_readiness_rows_without_launch_command_refs": b4_row_readiness_ledger.get(
            "rows_without_launch_command_refs"
        ),
        "b4_row_readiness_ready_suites": b4_row_readiness_ledger.get("ready_suite_count"),
        "b4_row_readiness_not_ready_suites": b4_row_readiness_ledger.get("not_ready_suite_count"),
        "b4_execution_opt_in_packet_status": b4_execution_opt_in_packet.get("status"),
        "b4_execution_opt_in_ready_command_count": b4_execution_opt_in_packet.get("ready_command_count"),
        "b4_execution_opt_in_mapped_external_rows": b4_execution_opt_in_packet.get(
            "ready_command_mapped_external_rows"
        ),
        "b4_execution_opt_in_unaddressed_external_rows": b4_execution_opt_in_packet.get(
            "unaddressed_external_rows_after_ready_commands"
        ),
        "b4_execution_opt_in_source_policy_rows_closed_now": b4_execution_opt_in_packet.get(
            "source_policy_rows_closed_now"
        ),
        "b4_execution_opt_in_source_policy_rows_total": b4_execution_opt_in_packet.get(
            "source_policy_rows_total"
        ),
        "b4_execution_opt_in_explicit_user_opt_in_required": b4_execution_opt_in_packet.get(
            "explicit_user_opt_in_required_before_any_command"
        ),
        "b4_post_execution_promotion_contract_schema": b4_promotion_contract.get("schema"),
        "b4_post_execution_promotion_contract_status": b4_promotion_contract.get("status"),
        "b4_post_execution_promotion_contract_rows_closed": b4_promotion_contract.get(
            "source_policy_rows_closed_now"
        ),
        "b4_post_execution_promotion_contract_rows_total": b4_promotion_contract.get(
            "source_policy_rows_total"
        ),
        "b4_post_execution_promotion_contract_ready_mapped_rows": b4_promotion_contract.get(
            "ready_command_mapped_external_rows"
        ),
        "b4_post_execution_promotion_contract_unaddressed_rows": b4_promotion_contract.get(
            "unaddressed_external_rows_after_ready_commands"
        ),
        "b4_post_execution_promotion_contract_checks_satisfied_now": b4_promotion_contract.get(
            "all_required_checks_satisfied_now"
        ),
        "b4_post_execution_promotion_contract_b4_can_close_now": b4_promotion_contract.get(
            "b4_can_close_after_promotion_contract_now"
        ),
        "b4_post_execution_promotion_contract_b7_can_close_now": b4_promotion_contract.get(
            "b7_can_close_after_promotion_contract_now"
        ),
        "tfe_source_policy_runner_implemented": code_checks.get("tfe_source_policy_runner_implemented"),
        "tfe_public_code_recheck_status": tfe_public_code_recheck.get("status"),
        "tfe_public_code_recheck_date": tfe_public_code_recheck.get("date_checked"),
        "tfe_public_code_recheck_github_repository_search_total_count": tfe_public_code_recheck.get(
            "coverage", {}
        ).get("github_repository_search_total_count"),
        "tfe_public_code_recheck_github_user_search_total_count": tfe_public_code_recheck.get(
            "coverage", {}
        ).get("github_user_search_total_count"),
        "tfe_public_code_recheck_github_code_search_api_status": tfe_public_code_recheck.get(
            "coverage", {}
        ).get("github_code_search_api_status"),
        "tfe_public_code_recheck_rows_attempted_not_reproducible": tfe_public_code_recheck.get(
            "coverage", {}
        ).get("source_policy_rows_attempted_not_reproducible"),
        "tfe_public_code_recheck_source_policy_rows_closed": tfe_public_code_recheck.get(
            "coverage", {}
        ).get("source_policy_rows_closed"),
        "tfe_public_code_recheck_external_superiority_allowed": tfe_public_code_recheck.get(
            "claim_boundary", {}
        ).get("external_superiority_claim_allowed"),
        "tfe_candidate_source_policy_boundary": tfe_candidate_source_policy_boundary,
        "tfe_candidate_source_policy_boundary_sources": external_checks.get(
            "tfe_candidate_source_policy_boundary_sources"
        ),
        "tfe_candidate_source_policy_boundary_sources_match": external_checks.get(
            "tfe_candidate_source_policy_boundary_sources_match"
        ),
        "tfe_candidate_source_policy_allowed_use": external_checks.get(
            "tfe_candidate_source_policy_allowed_use"
        ),
        "tfe_candidate_source_policy_dae_runner_equivalent": external_checks.get(
            "tfe_candidate_source_policy_dae_runner_equivalent"
        ),
        "tfe_candidate_source_policy_method_runner_equivalent": external_checks.get(
            "tfe_candidate_source_policy_method_runner_equivalent"
        ),
        "tfe_candidate_source_policy_rows_completed": external_checks.get(
            "tfe_candidate_source_policy_rows_completed"
        ),
        "tfe_candidate_source_policy_external_superiority_allowed": external_checks.get(
            "tfe_candidate_source_policy_external_superiority_allowed"
        ),
        "tfe_dae_runner_contract_gap_status": tfe_dae_gap.get("status"),
        "tfe_dae_runner_contract_gap_missing_block_count": tfe_dae_gap.get(
            "missing_contract_block_count"
        ),
        "tfe_dae_runner_contract_gap_missing_block_ids": tfe_dae_gap_missing_ids,
        "tfe_dae_runner_contract_gap_nonheavy_blocks": tfe_dae_gap.get(
            "nonheavy_missing_contract_blocks"
        ),
        "tfe_dae_runner_contract_gap_terminal_nonpromoted_blocks": tfe_dae_gap.get(
            "terminal_nonpromoted_contract_blocks"
        ),
        "tfe_dae_runner_contract_gap_terminal_nonpromoted_block_count": tfe_dae_gap.get(
            "terminal_nonpromoted_contract_block_count"
        ),
        "tfe_dae_runner_contract_gap_effective_missing_blocks": tfe_dae_gap.get(
            "effective_missing_contract_blocks"
        ),
        "tfe_dae_runner_contract_gap_effective_missing_block_count": tfe_dae_gap.get(
            "effective_missing_contract_block_count"
        ),
        "tfe_dae_runner_contract_gap_block_accounting": tfe_dae_gap.get(
            "contract_block_accounting"
        ),
        "tfe_dae_runner_contract_gap_execution_blocks": tfe_dae_gap.get(
            "source_policy_execution_missing_contract_blocks"
        ),
        "tfe_dae_runner_contract_gap_ready_to_execute_source_policy_now": tfe_dae_gap.get(
            "ready_to_execute_source_policy_now"
        ),
        "tfe_dae_runner_contract_gap_heavy_run_invoked": tfe_dae_gap.get(
            "heavy_numerical_run_invoked"
        ),
        "tfe_source_policy_execution_preflight": tfe_source_policy_execution_preflight,
        "tfe_source_policy_execution_preflight_status": tfe_source_policy_execution_preflight.get(
            "status"
        ),
        "tfe_source_policy_execution_preflight_opt_in_required": (
            tfe_source_policy_execution_preflight.get("explicit_user_opt_in_required")
        ),
        "tfe_source_policy_execution_preflight_nonheavy_dispositioned": (
            tfe_source_policy_execution_preflight.get("nonheavy_blocks_dispositioned_by_demotion")
        ),
        "tfe_source_policy_execution_preflight_execution_block_count": (
            tfe_source_policy_execution_preflight.get("execution_block_count")
        ),
        "tfe_source_policy_execution_preflight_can_promote_rows_now": (
            tfe_source_policy_execution_preflight.get("can_promote_any_tfe_source_policy_row_now")
        ),
        "tfe_source_policy_execution_preflight_ready_now": (
            tfe_source_policy_execution_preflight.get("ready_to_execute_source_policy_now")
        ),
        "tfe_runner_contract_preflight_status": tfe_runner_contract_preflight.get("status"),
        "tfe_runner_contract_preflight_entrypoints": (
            f"{tfe_runner_contract_preflight.get('callable_contract_count')}/"
            f"{tfe_runner_contract_preflight.get('entrypoint_count')}"
        ),
        "tfe_runner_contract_preflight_candidate_backed": (
            f"{tfe_runner_contract_preflight.get('candidate_backed_contract_count')}/"
            f"{tfe_runner_contract_preflight.get('entrypoint_count')}"
        ),
        "tfe_runner_contract_preflight_source_policy_rows_completed": (
            tfe_runner_contract_preflight.get("source_policy_rows_completed")
        ),
        "tfe_runner_contract_preflight_execution_blocks": (
            tfe_runner_contract_preflight.get("source_policy_execution_block_count")
        ),
        "tfe_runner_contract_preflight_safe_use": tfe_runner_contract_preflight.get(
            "safe_current_use"
        ),
        "oc12_archive_tfe_runner_contract_preflight_status": objective_summary.get(
            "full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_status"
        ),
        "oc12_archive_tfe_runner_contract_preflight_entrypoints": objective_summary.get(
            "full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_entrypoints"
        ),
        "oc12_archive_tfe_runner_contract_preflight_candidate_backed": objective_summary.get(
            "full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_candidate_backed"
        ),
        "oc12_archive_tfe_runner_contract_preflight_source_policy_rows_completed": (
            objective_summary.get(
                "full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_source_policy_rows_completed"
            )
        ),
        "oc12_archive_tfe_runner_contract_preflight_execution_blocks": objective_summary.get(
            "full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_execution_blocks"
        ),
        "oc12_archive_tfe_runner_contract_preflight_safe_use": objective_summary.get(
            "full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_safe_use"
        ),
        "oc12_archive_action_boundary": objective_summary.get(
            "full_source_policy_runner_archive_gap_action_boundary"
        ),
        "oc12_archive_safe_without_b4_opt_in_count": objective_summary.get(
            "full_source_policy_runner_archive_gap_safe_without_b4_opt_in_count"
        ),
        "oc12_archive_opt_in_required_action_count": objective_summary.get(
            "full_source_policy_runner_archive_gap_opt_in_required_action_count"
        ),
        "oc12_archive_source_policy_execution_allowed_now": objective_summary.get(
            "full_source_policy_runner_archive_gap_source_policy_execution_allowed_now"
        ),
        "oc12_archive_source_policy_execution_invoked": objective_summary.get(
            "full_source_policy_runner_archive_gap_source_policy_execution_invoked"
        ),
        "oc12_archive_exact_b4_opt_in_required_for_execution": objective_summary.get(
            "full_source_policy_runner_archive_gap_exact_b4_opt_in_required_for_execution"
        ),
        "oc12_archive_opt_in_required_command_count": objective_summary.get(
            "full_source_policy_runner_archive_gap_opt_in_required_command_count"
        ),
        "oc12_archive_opt_in_required_mapped_external_rows": objective_summary.get(
            "full_source_policy_runner_archive_gap_opt_in_required_mapped_external_rows"
        ),
        "oc12_archive_safe_action_ids": objective_summary.get(
            "full_source_policy_runner_archive_gap_safe_action_ids"
        ),
        "oc12_archive_opt_in_action_ids": objective_summary.get(
            "full_source_policy_runner_archive_gap_opt_in_action_ids"
        ),
        "tfe_source_policy_self_reproduction_preflight": tfe_self_reproduction_execution_preflight,
        "tfe_source_policy_self_reproduction_preflight_status": (
            tfe_self_reproduction_execution_preflight.get("status")
        ),
        "tfe_source_policy_self_reproduction_preflight_current_route": (
            tfe_self_reproduction_execution_preflight.get("current_route")
        ),
        "tfe_source_policy_self_reproduction_preflight_reopen_condition": (
            tfe_self_reproduction_execution_preflight.get("reopen_condition")
        ),
        "tfe_source_policy_self_reproduction_preflight_execution_block_count": (
            tfe_self_reproduction_execution_preflight.get("execution_block_count")
        ),
        "tfe_source_policy_self_reproduction_preflight_can_promote_rows_now": (
            tfe_self_reproduction_execution_preflight.get("can_promote_any_tfe_source_policy_row_now")
        ),
        "tfe_source_policy_self_reproduction_preflight_ready_now": (
            tfe_self_reproduction_execution_preflight.get("ready_to_execute_source_policy_now")
        ),
        "tfe_source_policy_self_reproduction_preflight_source_policy_rows_completed": (
            tfe_self_reproduction_execution_preflight.get("source_policy_rows_completed")
        ),
        "tfe_source_policy_self_reproduction_preflight_runner_contracts_required": (
            tfe_self_reproduction_execution_preflight.get("runner_contracts_required_before_execution", [])
        ),
        "tfe_source_policy_self_reproduction_required_next_action_count": len(
            tfe_self_reproduction_required_next_actions
        ),
        "tfe_source_pendulum_parameter_model_implemented": code_checks.get(
            "tfe_source_pendulum_parameter_model_implemented"
        ),
        "tfe_source_pendulum_frictionless_smoke_implemented": code_checks.get(
            "tfe_source_pendulum_frictionless_smoke_implemented"
        ),
        "tfe_source_pendulum_absolute_coordinate_dae_residual_smoke_implemented": code_checks.get(
            "tfe_source_pendulum_absolute_coordinate_dae_residual_smoke_implemented"
        ),
        "tfe_source_pendulum_source_policy_dae_runner_equivalent": code_checks.get(
            "tfe_source_pendulum_source_policy_dae_runner_equivalent"
        ),
        "tfe_source_pendulum_source_output_time_integration_smoke_implemented": code_checks.get(
            "tfe_source_pendulum_source_output_time_integration_smoke_implemented"
        ),
        "tfe_source_pendulum_source_policy_time_integration_runner_equivalent": code_checks.get(
            "tfe_source_pendulum_source_policy_time_integration_runner_equivalent"
        ),
        "tfe_source_pendulum_source_reference_solution_policy_smoke_implemented": code_checks.get(
            "tfe_source_pendulum_source_reference_solution_policy_smoke_implemented"
        ),
        "tfe_source_pendulum_source_reference_solution_policy_smoke_full_T10": code_checks.get(
            "tfe_source_pendulum_source_reference_solution_policy_smoke_full_T10"
        ),
        "tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_implemented": code_checks.get(
            "tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_implemented"
        ),
        "tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_completed": code_checks.get(
            "tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_completed"
        ),
        "tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_rows_completed": code_checks.get(
            "tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_rows_completed"
        ),
        "tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_steps": code_checks.get(
            "tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_steps"
        ),
        "tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_check_steps": code_checks.get(
            "tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_check_steps"
        ),
        "tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_coordinate_error": code_checks.get(
            "tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_coordinate_error"
        ),
        "tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_velocity_error": code_checks.get(
            "tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_velocity_error"
        ),
        "tfe_source_pendulum_source_comparator_candidate_runners_implemented": code_checks.get(
            "tfe_source_pendulum_source_comparator_candidate_runners_implemented"
        ),
        "tfe_source_pendulum_newmark_beta_candidate_runner_smoke_implemented": code_checks.get(
            "tfe_source_pendulum_newmark_beta_candidate_runner_smoke_implemented"
        ),
        "tfe_source_pendulum_trapezoidal_candidate_runner_smoke_implemented": code_checks.get(
            "tfe_source_pendulum_trapezoidal_candidate_runner_smoke_implemented"
        ),
        "tfe_source_pendulum_source_policy_method_runner_equivalent": code_checks.get(
            "tfe_source_pendulum_source_policy_method_runner_equivalent"
        ),
        "tfe_source_pendulum_tfe_m1_m2_m3_candidate_runner_smoke_implemented": code_checks.get(
            "tfe_source_pendulum_tfe_m1_m2_m3_candidate_runner_smoke_implemented"
        ),
        "tfe_source_pendulum_tfe_m1_m2_m3_source_policy_runners_implemented": code_checks.get(
            "tfe_source_pendulum_tfe_m1_m2_m3_source_policy_runners_implemented"
        ),
        "tfe_source_pendulum_gauss6_candidate_smoke_implemented": code_checks.get(
            "tfe_source_pendulum_gauss6_candidate_smoke_implemented"
        ),
        "tfe_source_pendulum_gauss6_absolute_coordinate_source_policy_runner_implemented": code_checks.get(
            "tfe_source_pendulum_gauss6_absolute_coordinate_source_policy_runner_implemented"
        ),
        "tfe_source_pendulum_gauss6_candidate_rows": code_checks.get(
            "tfe_source_pendulum_gauss6_candidate_rows"
        ),
        "tfe_source_pendulum_gauss6_candidate_source_policy_rows_completed": code_checks.get(
            "tfe_source_pendulum_gauss6_candidate_source_policy_rows_completed"
        ),
        "tfe_source_pendulum_gauss6_candidate_method_equivalent": code_checks.get(
            "tfe_source_pendulum_gauss6_candidate_method_equivalent"
        ),
        "tfe_source_pendulum_bounded_source_policy_runner_smoke_implemented": code_checks.get(
            "tfe_source_pendulum_bounded_source_policy_runner_smoke_implemented"
        ),
        "tfe_source_pendulum_bounded_source_policy_runner_rows": code_checks.get(
            "tfe_source_pendulum_bounded_source_policy_runner_rows"
        ),
        "tfe_source_pendulum_bounded_source_policy_runner_full_T10": code_checks.get(
            "tfe_source_pendulum_bounded_source_policy_runner_full_T10"
        ),
        "tfe_source_pendulum_bounded_source_policy_runner_source_policy_rows_completed": code_checks.get(
            "tfe_source_pendulum_bounded_source_policy_runner_source_policy_rows_completed"
        ),
        "tfe_source_pendulum_active_b2_candidate_row_smoke_implemented": code_checks.get(
            "tfe_source_pendulum_active_b2_candidate_row_smoke_implemented"
        ),
        "tfe_source_pendulum_active_b2_candidate_row_smoke_full_T10": code_checks.get(
            "tfe_source_pendulum_active_b2_candidate_row_smoke_full_T10"
        ),
        "tfe_source_pendulum_active_b2_source_policy_rows_completed": code_checks.get(
            "tfe_source_pendulum_active_b2_source_policy_rows_completed"
        ),
        "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_implemented": code_checks.get(
            "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_implemented"
        ),
        "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_full_T10": code_checks.get(
            "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_full_T10"
        ),
        "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_reference_invoked": code_checks.get(
            "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_reference_invoked"
        ),
        "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_source_policy_rows": code_checks.get(
            "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_source_policy_rows"
        ),
        "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_finite_rows": code_checks.get(
            "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_finite_rows"
        ),
        "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_residual_ok_rows": code_checks.get(
            "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_residual_ok_rows"
        ),
        "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_method_equivalent": code_checks.get(
            "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_method_equivalent"
        ),
        "tfe_full_t10_absolute_dae_lift_status": tfe_full_t10_absolute.get("status"),
        "tfe_full_t10_absolute_dae_lift_completed": tfe_full_t10_absolute.get(
            "full_T10_absolute_coordinate_lift_completed"
        ),
        "tfe_full_t10_absolute_dae_lift_method_count": tfe_full_t10_absolute.get("method_count"),
        "tfe_full_t10_absolute_dae_lift_metric_rows": tfe_full_t10_absolute.get("metric_row_count"),
        "tfe_full_t10_absolute_dae_lift_step_residual_rows": tfe_full_t10_absolute.get(
            "step_residual_row_count"
        ),
        "tfe_full_t10_absolute_dae_lift_source_reference_invoked": tfe_full_t10_absolute.get(
            "source_reference_invoked"
        ),
        "tfe_full_t10_absolute_dae_lift_source_policy_rows_completed": tfe_full_t10_absolute.get(
            "source_policy_rows_completed"
        ),
        "tfe_full_t10_absolute_dae_lift_monolithic": tfe_full_t10_absolute.get(
            "monolithic_absolute_coordinate_dae_time_integrator"
        ),
        "tfe_full_t10_absolute_dae_lift_equivalent": tfe_full_t10_absolute.get(
            "source_policy_dae_runner_equivalent"
        ),
        "tfe_endpoint_boundary_certificate_status": tfe_endpoint_boundary.get("status"),
        "tfe_endpoint_boundary_literal_overrun_bound_proved": tfe_endpoint_boundary.get(
            "theorem", {}
        ).get("name")
        == "fixed_h_until_final_time_endpoint_bound",
        "tfe_endpoint_boundary_literal_exact_T_rows": tfe_endpoint_boundary.get(
            "algorithm_literal_exact_T_row_count"
        ),
        "tfe_endpoint_boundary_literal_overrun_rows": tfe_endpoint_boundary.get(
            "algorithm_literal_overrun_row_count"
        ),
        "tfe_endpoint_boundary_source_policy_rows_completed": tfe_endpoint_boundary.get(
            "source_policy_rows_completed"
        ),
        "tfe_endpoint_boundary_full_T10_policy_resolved": tfe_endpoint_boundary.get(
            "source_grid_policy_resolved_for_full_T10"
        ),
        "tfe_endpoint_boundary_exact_T_error_sampling_equivalent": tfe_endpoint_boundary.get(
            "source_policy_exact_T_error_sampling_equivalent"
        ),
        "tfe_full_T10_endpoint_policy_closure_certificate_status": tfe_endpoint_certificate.get(
            "status"
        ),
        "tfe_full_T10_endpoint_policy_closure_certificate_available": tfe_endpoint_certificate.get(
            "certificate_available"
        ),
        "tfe_full_T10_endpoint_policy_closure_certificate_positive": tfe_endpoint_certificate.get(
            "positive_full_T10_endpoint_policy_certified"
        ),
        "tfe_full_T10_endpoint_policy_closure_certificate_nonheavy_block_closed": tfe_endpoint_certificate.get(
            "nonheavy_contract_block_closed"
        ),
        "tfe_full_T10_endpoint_policy_closure_certificate_source_policy_execution_invoked": tfe_endpoint_certificate.get(
            "source_policy_execution_invoked"
        ),
        "tfe_full_T10_endpoint_policy_closure_certificate_can_close_now": tfe_endpoint_certificate.get(
            "can_close_now"
        ),
        "tfe_source_pendulum_active_b2_candidate_row_count": code_checks.get(
            "tfe_source_pendulum_active_b2_candidate_row_count"
        ),
        "tfe_source_grid_policy_resolved_for_full_T10": external_checks.get(
            "tfe_source_grid_policy_resolved_for_full_T10"
        ),
        "tfe_source_grid_integer_step_incompatible_rows": external_checks.get(
            "tfe_source_grid_integer_step_incompatible_rows"
        ),
        "tfe_source_grid_exact_T_compatible_rows_endpoint_convention_resolved": external_checks.get(
            "tfe_source_grid_exact_T_compatible_rows_endpoint_convention_resolved"
        ),
        "tfe_source_grid_endpoint_incompatible_rows_requiring_policy": external_checks.get(
            "tfe_source_grid_endpoint_incompatible_rows_requiring_policy"
        ),
        "tfe_source_grid_policy_resolved_for_exact_T_compatible_rows": external_checks.get(
            "tfe_source_grid_policy_resolved_for_exact_T_compatible_rows"
        ),
        "tfe_source_grid_source_text_available": external_checks.get("tfe_source_grid_source_text_available"),
        "tfe_source_grid_source_text_anchor_count": external_checks.get(
            "tfe_source_grid_source_text_anchor_count"
        ),
        "tfe_source_grid_algorithm_literal_fixed_h": external_checks.get("tfe_source_grid_algorithm_literal_fixed_h"),
        "tfe_source_grid_endpoint_convention_resolved_for_error_sampling": external_checks.get(
            "tfe_source_grid_endpoint_convention_resolved_for_error_sampling"
        ),
        "tfe_endpoint_sensitivity_status": external_checks.get("tfe_endpoint_sensitivity_status"),
        "tfe_endpoint_sensitivity_method_count": external_checks.get("tfe_endpoint_sensitivity_method_count"),
        "tfe_endpoint_sensitivity_policy_count": external_checks.get("tfe_endpoint_sensitivity_policy_count"),
        "tfe_endpoint_sensitivity_summary_row_count": external_checks.get(
            "tfe_endpoint_sensitivity_summary_row_count"
        ),
        "tfe_endpoint_sensitivity_raw_row_count": external_checks.get("tfe_endpoint_sensitivity_raw_row_count"),
        "tfe_endpoint_sensitivity_source_policy_rows_completed": external_checks.get(
            "tfe_endpoint_sensitivity_source_policy_rows_completed"
        ),
        "tfe_endpoint_sensitivity_external_superiority_claim_allowed": external_checks.get(
            "tfe_endpoint_sensitivity_external_superiority_claim_allowed"
        ),
        "tfe_endpoint_sensitivity_source_policy_runner_equivalent": external_checks.get(
            "tfe_endpoint_sensitivity_source_policy_runner_equivalent"
        ),
        "tfe_endpoint_sensitivity_default_1e_4_campaign_invoked": external_checks.get(
            "tfe_endpoint_sensitivity_default_1e_4_campaign_invoked"
        ),
        "tfe_endpoint_sensitivity_run_v047_invoked": external_checks.get(
            "tfe_endpoint_sensitivity_run_v047_invoked"
        ),
        "tfe_source_pendulum_error_output_policy_encoded": code_checks.get(
            "tfe_source_pendulum_error_output_policy_encoded"
        ),
        "tfe_source_pendulum_brown_mcphee_candidate_friction_law_encoded": code_checks.get(
            "tfe_source_pendulum_brown_mcphee_candidate_friction_law_encoded"
        ),
        "tfe_source_pendulum_frictional_candidate_smoke_implemented": code_checks.get(
            "tfe_source_pendulum_frictional_candidate_smoke_implemented"
        ),
        "tfe_brown_mcphee_boundary_status": tfe_brown_mcphee_boundary.get("status"),
        "tfe_brown_mcphee_boundary_source_code_equivalent_law": tfe_brown_mcphee_boundary.get(
            "brown_mcphee_source_code_equivalent_law"
        ),
        "tfe_brown_mcphee_boundary_transition_velocity_resolved": tfe_brown_mcphee_boundary.get(
            "brown_mcphee_transition_velocity_policy_resolved_from_source"
        ),
        "tfe_brown_mcphee_boundary_rows_promoted": tfe_brown_mcphee_boundary.get(
            "source_policy_rows_promoted"
        ),
        "tfe_brown_mcphee_boundary_nonheavy_contract_block_closed": tfe_brown_mcphee_boundary.get(
            "nonheavy_contract_block_closed"
        ),
        "tfe_brown_mcphee_candidate_dae_contract_rows": tfe_brown_mcphee_contract.get(
            "row_count"
        ),
        "tfe_brown_mcphee_candidate_dae_contract_step_rows": tfe_brown_mcphee_contract.get(
            "step_residual_row_count"
        ),
        "tfe_brown_mcphee_candidate_dae_contract_source_policy_rows": tfe_brown_mcphee_contract.get(
            "source_policy_rows_completed"
        ),
        "tfe_brown_mcphee_candidate_dae_contract_all_finite": tfe_brown_mcphee_contract.get(
            "all_rows_finite"
        ),
        "tfe_brown_mcphee_candidate_dae_contract_residual_ok": tfe_brown_mcphee_contract.get(
            "all_dae_residuals_below_1e_9"
        ),
        "tfe_brown_mcphee_candidate_dae_contract_power_nonpositive": tfe_brown_mcphee_contract.get(
            "all_candidate_friction_power_nonpositive"
        ),
        "tfe_brown_mcphee_candidate_dae_contract_equivalent_dae": tfe_brown_mcphee_contract.get(
            "source_policy_dae_runner_equivalent"
        ),
        "tfe_brown_mcphee_candidate_dae_contract_equivalent_method": tfe_brown_mcphee_contract.get(
            "source_policy_method_runner_equivalent"
        ),
        "tfe_brown_mcphee_candidate_dae_contract_source_law": tfe_brown_mcphee_contract.get(
            "brown_mcphee_source_code_equivalent_law"
        ),
        "tfe_brown_mcphee_candidate_dae_contract_monolithic": tfe_brown_mcphee_contract.get(
            "monolithic_absolute_coordinate_dae_time_integrator"
        ),
        "tfe_brown_mcphee_transition_velocity_sensitivity_rows": tfe_brown_mcphee_velocity_sensitivity.get(
            "endpoint_delta_row_count"
        ),
        "tfe_brown_mcphee_transition_velocity_sensitivity_contract_rows": tfe_brown_mcphee_velocity_sensitivity.get(
            "contract_row_count"
        ),
        "tfe_brown_mcphee_transition_velocity_sensitivity_source_policy_rows": tfe_brown_mcphee_velocity_sensitivity.get(
            "source_policy_rows_completed"
        ),
        "tfe_brown_mcphee_transition_velocity_sensitivity_material": tfe_brown_mcphee_velocity_sensitivity.get(
            "missing_transition_velocity_is_numerically_material"
        ),
        "tfe_brown_mcphee_transition_velocity_sensitivity_max_coordinate_delta": tfe_brown_mcphee_velocity_sensitivity.get(
            "max_endpoint_coordinate_delta_vs_baseline"
        ),
        "tfe_brown_mcphee_transition_velocity_sensitivity_max_velocity_delta": tfe_brown_mcphee_velocity_sensitivity.get(
            "max_endpoint_velocity_delta_vs_baseline"
        ),
        "tfe_brown_mcphee_transition_velocity_sensitivity_equivalence_flags_false": tfe_brown_mcphee_velocity_sensitivity.get(
            "all_contract_equivalence_flags_false"
        ),
        "tfe_brown_mcphee_source_code_equivalence_certificate_status": tfe_brown_mcphee_certificate.get(
            "status"
        ),
        "tfe_brown_mcphee_source_code_equivalence_certificate_available": tfe_brown_mcphee_certificate.get(
            "certificate_available"
        ),
        "tfe_brown_mcphee_source_code_equivalence_certificate_positive": tfe_brown_mcphee_certificate.get(
            "positive_source_code_equivalence_certified"
        ),
        "tfe_brown_mcphee_source_code_equivalence_certificate_nonheavy_block_closed": tfe_brown_mcphee_certificate.get(
            "nonheavy_contract_block_closed"
        ),
        "tfe_brown_mcphee_source_code_equivalence_certificate_source_policy_execution_invoked": tfe_brown_mcphee_certificate.get(
            "source_policy_execution_invoked"
        ),
        "tfe_brown_mcphee_source_code_equivalence_certificate_can_close_now": tfe_brown_mcphee_certificate.get(
            "can_close_now"
        ),
        "tfe_source_pendulum_setup_subrequirement_closed": tfe_model.get("closure_boundary", {}).get(
            "can_close_source_pendulum_setup_subrequirement"
        ),
        "direct_pc2_proof_gap_closed": proof_checks.get(
            "direct_pc2_proof_gap_closed", proof_checks.get("proof_gap_closed")
        ),
        "proof_gap_closed": proof_checks.get("proof_gap_closed"),
        "proof_gap_closed_scope": proof_checks.get("proof_gap_closed_scope", DIRECT_PC2_SCOPE),
        "proof_gap_closed_reading_rule": DIRECT_PC2_READING_RULE,
        "proof_theorem_statement_labels_present": proof_theorem_boundary.get(
            "all_required_labels_present_main_and_flat"
        ),
        "proof_theorem_statement_boundary_present": proof_theorem_boundary.get(
            "conditional_theorem_boundary_present_main_and_flat"
        ),
        "proof_theorem_statement_eta_condition_retained": proof_theorem_boundary.get(
            "eta_h_theorem_condition_retained"
        ),
        "proof_theorem_statement_eta_evidence_closed": proof_theorem_boundary.get(
            "eta_h_solver_policy_evidence_closed"
        ),
        "proof_theorem_statement_fixed_tolerance_asymptotic_proof": proof_theorem_boundary.get(
            "fixed_tolerance_runs_are_asymptotic_proof"
        ),
        "proof_theorem_statement_residual_to_error_not_promoted": proof_theorem_boundary.get(
            "does_not_promote_residual_to_error"
        ),
        "proof_theorem_statement_source_policy_or_full_tfe_not_promoted": proof_theorem_boundary.get(
            "does_not_promote_source_policy_or_full_tfe"
        ),
        "proof_claim_traceability_theorem_label": proof_claim_theorem_traceability.get("accepted_theorem_label"),
        "proof_claim_traceability_theorem_labels_present": proof_claim_theorem_traceability.get(
            "theorem_statement_labels_present"
        ),
        "proof_claim_traceability_theorem_boundary_present": proof_claim_theorem_traceability.get(
            "conditional_theorem_boundary_present"
        ),
        "proof_claim_traceability_theorem_claims_mapped": proof_claim_theorem_traceability.get(
            "conditional_proof_claims_mapped_to_manuscript"
        ),
        "proof_claim_traceability_dependency_graph_present": proof_claim_theorem_traceability.get(
            "proof_dependency_graph_present"
        ),
        "proof_claim_traceability_table_present": proof_claim_theorem_traceability.get(
            "proof_traceability_table_present"
        ),
        "proof_claim_traceability_dynamic_theorem_matrix_present": proof_claim_theorem_traceability.get(
            "dynamic_proof_closure_matrix_present"
        ),
        "proof_claim_traceability_primitive_lane_boundary_present": proof_claim_theorem_traceability.get(
            "primitive_lane_boundary_present"
        ),
        "proof_claim_traceability_residual_nonpromotion_present": proof_claim_theorem_traceability.get(
            "residual_nonpromotion_present"
        ),
        "proof_claim_traceability_eta_condition_retained": proof_claim_theorem_traceability.get(
            "eta_h_theorem_condition_retained"
        ),
        "proof_claim_traceability_eta_evidence_closed": proof_claim_theorem_traceability.get(
            "eta_h_solver_policy_evidence_closed"
        ),
        "proof_claim_traceability_fixed_tolerance_asymptotic_proof": proof_claim_theorem_traceability.get(
            "fixed_tolerance_runs_are_asymptotic_proof"
        ),
        "proof_claim_traceability_residual_to_error_not_promoted": proof_claim_theorem_traceability.get(
            "residual_to_error_not_promoted"
        ),
        "proof_claim_traceability_p7_retained_nonpromotion_boundary_present": (
            proof_claim_theorem_traceability.get("p7_retained_nonpromotion_boundary_present")
        ),
        "proof_claim_traceability_b1_closure_scope_boundary_present": (
            proof_claim_theorem_traceability.get("b1_closure_scope_boundary_present")
        ),
        "proof_claim_traceability_p6_solver_scope_boundary_present": (
            proof_claim_theorem_traceability.get("p6_solver_scope_boundary_present")
        ),
        "proof_claim_traceability_p1p2_compact_tube_boundary_present": (
            proof_claim_theorem_traceability.get("p1p2_compact_tube_boundary_present")
        ),
        "proof_claim_traceability_p3p4_implementation_boundary_present": (
            proof_claim_theorem_traceability.get("p3p4_implementation_boundary_present")
        ),
        "proof_claim_traceability_p5_direct_route_boundary_present": (
            proof_claim_theorem_traceability.get("p5_direct_route_boundary_present")
        ),
        "proof_claim_traceability_proof_causality_ledger_present": (
            proof_claim_theorem_traceability.get("proof_causality_ledger_present")
        ),
        "proof_claim_traceability_direct_route_anticircularity_ledger_present": (
            proof_claim_theorem_traceability.get(
                "direct_route_anticircularity_ledger_present"
            )
        ),
        "proof_claim_traceability_p_interface_satisfaction_ledger_present": (
            proof_claim_theorem_traceability.get("p_interface_satisfaction_ledger_present")
        ),
        "proof_claim_traceability_p7_residual_to_error_ledger_present": (
            proof_claim_theorem_traceability.get("p7_residual_to_error_ledger_present")
        ),
        "proof_claim_traceability_theorem_use_rule_present": (
            proof_claim_theorem_traceability.get("theorem_use_rule_present")
        ),
        "proof_claim_traceability_quantifier_domain_ledger_present": (
            proof_claim_theorem_traceability.get("quantifier_domain_ledger_present")
        ),
        "proof_claim_traceability_local_global_transfer_ledger_present": (
            proof_claim_theorem_traceability.get("local_global_transfer_ledger_present")
        ),
        "proof_claim_traceability_objective_completion_boundary_present": (
            proof_claim_theorem_traceability.get(
                "objective_completion_boundary_present"
            )
        ),
        "proof_claim_traceability_constant_dependency_ledger_present": (
            proof_claim_theorem_traceability.get("constant_dependency_ledger_present")
        ),
        "proof_claim_traceability_theorem_dependency_consumption_ledger_present": (
            proof_claim_theorem_traceability.get(
                "theorem_dependency_consumption_ledger_present"
            )
        ),
        "proof_claim_traceability_branch_consistency_ledger_present": (
            proof_claim_theorem_traceability.get("branch_consistency_ledger_present")
        ),
        "proof_claim_traceability_implementation_route_oracle_ledger_present": (
            proof_claim_theorem_traceability.get(
                "implementation_route_oracle_ledger_present"
            )
        ),
        "proof_claim_traceability_nonlinear_solver_scale_ledger_present": (
            proof_claim_theorem_traceability.get(
                "nonlinear_solver_scale_ledger_present"
            )
        ),
        "proof_claim_traceability_local_defect_decomposition_ledger_present": (
            proof_claim_theorem_traceability.get(
                "local_defect_decomposition_ledger_present"
            )
        ),
        "proof_claim_traceability_theorem_output_scope_ledger_present": (
            proof_claim_theorem_traceability.get("theorem_output_scope_ledger_present")
        ),
        "proof_claim_traceability_reporting_map_ledger_present": (
            proof_claim_theorem_traceability.get("reporting_map_ledger_present")
        ),
        "proof_claim_traceability_source_policy_or_full_tfe_not_promoted": proof_claim_theorem_traceability.get(
            "source_policy_or_full_tfe_not_promoted"
        ),
        "proof_claim_traceability_no_state_change": proof_claim_theorem_traceability.get(
            "does_not_change_proof_closure_state"
        ),
        "proof_claim_traceability_remaining_boundary_status": proof_claim_remaining_boundary.get("status"),
        "proof_claim_traceability_submission_satisfied_assumption_ids": proof_claim_remaining_boundary.get(
            "submission_satisfied_ids"
        ),
        "proof_claim_traceability_retained_or_open_assumption_ids": proof_claim_remaining_boundary.get(
            "retained_or_open_ids"
        ),
        "proof_claim_traceability_retained_theorem_interface_ids": proof_claim_remaining_boundary.get(
            "retained_theorem_interface_ids"
        ),
        "proof_claim_traceability_open_nonpromotion_boundary_ids": proof_claim_remaining_boundary.get(
            "open_nonpromotion_boundary_ids"
        ),
        "proof_claim_traceability_retained_theorem_interface_count": proof_claim_remaining_boundary.get(
            "retained_theorem_interface_count"
        ),
        "proof_claim_traceability_open_nonpromotion_boundary_count": proof_claim_remaining_boundary.get(
            "open_nonpromotion_boundary_count"
        ),
        "proof_claim_traceability_remaining_global_boundaries": proof_claim_remaining_boundary.get(
            "global_submission_boundaries_retained"
        ),
        "proof_claim_traceability_reader_facing_manuscript_boundary_present": proof_writing_card.get(
            "reader_facing_manuscript_boundary_present"
        ),
        "proof_claim_traceability_manuscript_anchor_map_present": proof_claim_traceability.get(
            "manuscript_anchor_map", {}
        ).get("all_label_anchors_present"),
        "proof_claim_traceability_manuscript_anchor_label_count": proof_claim_traceability.get(
            "manuscript_anchor_map", {}
        ).get("label_anchor_count"),
        "proof_claim_traceability_theorem_assumption_anchor_map_present": proof_claim_traceability.get(
            "manuscript_anchor_map", {}
        ).get("all_theorem_assumption_anchors_present"),
        "proof_claim_traceability_theorem_assumption_anchor_count": proof_claim_traceability.get(
            "manuscript_anchor_map", {}
        ).get("theorem_assumption_anchor_count"),
        "proof_claim_traceability_theorem_assumption_anchor_ids": proof_claim_traceability.get(
            "manuscript_anchor_map", {}
        ).get("theorem_assumption_anchor_ids"),
        "proof_closure_manuscript_anchor_map_present": proof.get("manuscript_anchor_map", {}).get(
            "all_label_anchors_present"
        ),
        "proof_closure_manuscript_anchor_label_count": proof.get("manuscript_anchor_map", {}).get(
            "label_anchor_count"
        ),
        "proof_closure_theorem_assumption_anchor_map_present": proof.get("manuscript_anchor_map", {}).get(
            "all_theorem_assumption_anchors_present"
        ),
        "proof_closure_theorem_assumption_anchor_count": proof.get("manuscript_anchor_map", {}).get(
            "theorem_assumption_anchor_count"
        ),
        "proof_closure_theorem_assumption_anchor_ids": proof.get("manuscript_anchor_map", {}).get(
            "theorem_assumption_anchor_ids"
        ),
        "proof_closure_proof_claim_anchor_maps_match": proof.get("manuscript_anchor_map", {})
        == proof_claim_traceability.get("manuscript_anchor_map", {}),
        "proof_contract_anchor_evidence_sources": proof_checks.get(
            "proof_contract_anchor_evidence_sources"
        ),
        "proof_style_anchor_evidence_sources": proof_checks.get("proof_style_anchor_evidence_sources"),
        "strict_proof_anchor_evidence_sources": proof_checks.get(
            "strict_proof_anchor_evidence_sources"
        ),
        "proof_anchor_evidence_sources_match": proof_checks.get("proof_anchor_evidence_sources_match"),
        "proof_manuscript_traceability_mapped": proof_manuscript_traceability.get(
            "conditional_proof_claims_mapped_to_manuscript"
        ),
        "proof_manuscript_traceability_no_state_change": proof_manuscript_traceability.get(
            "does_not_change_proof_closure_state"
        ),
        "proof_manuscript_traceability_dependency_graph_present": proof_manuscript_traceability.get(
            "proof_dependency_graph_present_main_and_flat"
        ),
        "proof_manuscript_traceability_dynamic_matrix_present": proof_manuscript_traceability.get(
            "dynamic_proof_closure_matrix_present_main_and_flat"
        ),
        "proof_manuscript_traceability_primitive_lane_boundary_present": proof_manuscript_traceability.get(
            "primitive_lane_boundary_present_main_and_flat"
        ),
        "proof_manuscript_traceability_residual_nonpromotion_present": proof_manuscript_traceability.get(
            "residual_to_error_nonpromotion_present_main_and_flat"
        ),
        "stage_residual_O_h7_implementation_defect_proved": proof_checks.get(
            "stage_residual_O_h7_implementation_defect_proved"
        ),
        "newton_euler_obligation_coverage_matrix_complete": proof_checks.get(
            "newton_euler_obligation_coverage_matrix_complete"
        ),
        "newton_euler_row_obligation_links": proof_checks.get("newton_euler_row_obligation_links"),
        "newton_euler_rows_with_complete_obligation_sets": proof_checks.get(
            "newton_euler_rows_with_complete_obligation_sets"
        ),
        "newton_euler_obligation_coverage_proof_closure_advanced": proof_checks.get(
            "newton_euler_obligation_coverage_proof_closure_advanced"
        ),
        "minimal_reproducibility_candidate_present": code_checks.get("minimal_reproducibility_candidate_present"),
        "minimal_reproducibility_candidate_status": code_checks.get("minimal_reproducibility_candidate_status"),
        "minimal_reproducibility_candidate_file_count": code_checks.get(
            "minimal_reproducibility_candidate_file_count"
        ),
        "minimal_reproducibility_candidate_python_file_count": code_checks.get(
            "minimal_reproducibility_candidate_python_file_count"
        ),
        "minimal_reproducibility_candidate_python_lines": code_checks.get(
            "minimal_reproducibility_candidate_python_lines"
        ),
        "minimal_reproducibility_candidate_code_size_ok": code_checks.get(
            "minimal_reproducibility_candidate_code_size_ok"
        ),
        "minimal_reproducibility_candidate_replay_only": code_checks.get(
            "minimal_reproducibility_candidate_replay_only"
        ),
        "minimal_reproducibility_candidate_runner_centered": code_checks.get(
            "minimal_reproducibility_candidate_runner_centered"
        ),
        "minimal_reproducibility_candidate_source_policy_ready": code_checks.get(
            "minimal_reproducibility_candidate_source_policy_ready"
        ),
        "minimal_reproducibility_candidate_proof_ready": code_checks.get(
            "minimal_reproducibility_candidate_proof_ready"
        ),
        "minimal_reproducible_submission_code_ready": code_checks.get("minimal_reproducible_submission_code_ready"),
        "runner_centered_audit_status": runner_centered_audit.get("status"),
        "runner_centered_package_ready": runner_centered_audit.get("runner_centered_package_ready"),
        "local_runner_centered_candidate_ready": runner_centered_audit.get(
            "local_runner_centered_candidate_ready"
        ),
        "full_source_policy_runner_package_ready": runner_centered_audit.get(
            "full_source_policy_runner_package_ready"
        ),
        "runner_centered_existing_source_lines": runner_centered_audit.get(
            "existing_runner_source_total_python_lines"
        ),
        "runner_adapter_candidate_status": runner_adapter.get("status"),
        "runner_adapter_present": runner_adapter.get("runner_adapter_present"),
        "runner_adapter_self_contained_simulation_runner": runner_adapter.get("self_contained_simulation_runner"),
        "runner_adapter_python_file_count": runner_adapter.get("candidate_python_file_count"),
        "runner_adapter_python_lines": runner_adapter.get("candidate_python_line_count"),
        "runner_adapter_closed_loop_local_rows_replay_present": runner_adapter.get(
            "closed_loop_local_rows_replay_present"
        ),
        "runner_adapter_closed_loop_local_rows_summary_present": runner_adapter.get(
            "closed_loop_local_rows_summary_present"
        ),
        "runner_adapter_closed_loop_local_rows": runner_adapter.get("closed_loop_local_rows"),
        "runner_adapter_closed_loop_local_models": closed_loop_local_models,
        "self_contained_runner_extraction_plan_status": extraction_plan.get("status"),
        "self_contained_runner_ready": extraction_plan.get("self_contained_runner_ready"),
        "local_accepted_rows_self_contained_runner_ready": extraction_plan.get(
            "local_accepted_rows_self_contained_runner_ready"
        ),
        "full_source_policy_self_contained_runner_ready": extraction_plan.get(
            "full_source_policy_self_contained_runner_ready"
        ),
        "b6_final_prose_pass_ready": extraction_plan.get("b6_final_prose_pass_ready"),
        "b6_final_prose_pass_scope": extraction_plan.get("b6_final_prose_pass_scope"),
        "full_source_policy_b6_prose_ready": extraction_plan.get("full_source_policy_b6_prose_ready"),
        "b6_closure_preflight_status": extraction_plan.get("b6_closure_preflight_status"),
        "b6_closure_allowed_now": extraction_plan.get("b6_closure_allowed_now"),
        "self_contained_runner_package_boundary": extraction_plan.get("runner_package_boundary"),
        "self_contained_runner_target_symbol_count": extraction_plan.get("target_symbol_count"),
        "self_contained_runner_target_symbol_lines": extraction_plan.get("target_symbol_lines"),
        "b6_closed_loop_extraction_audit_status": closed_loop_audit.get("status"),
        "b6_closed_loop_extraction_ready": closed_loop_audit.get("self_contained_runner_ready"),
        "b6_closed_loop_extraction_target_source_files": closed_loop_audit.get("target_source_file_count"),
        "b6_closed_loop_extraction_target_source_lines": closed_loop_audit.get("target_source_file_lines"),
        "b6_closed_loop_extraction_target_symbols": closed_loop_audit.get("target_symbol_count"),
        "b6_closed_loop_extraction_target_symbol_lines": closed_loop_audit.get("target_symbol_lines"),
        "b6_closed_loop_extraction_replay_only_examples": closed_loop_audit.get("replay_only_closed_loop_examples"),
        "b6_closed_loop_extraction_run_v047_invoked": closed_loop_audit.get("run_v047_invoked"),
        "b6_closed_loop_extraction_run_v048_invoked": closed_loop_audit.get("run_v048_invoked"),
        "b6_closed_loop_extraction_b4_opt_in_required": closed_loop_audit.get(
            "b4_opt_in_required_for_this_audit"
        ),
        "compact_closed_loop_candidate_status": closed_loop_candidate.get("status"),
        "compact_closed_loop_candidate_runner_passed": closed_loop_candidate.get("runner_passed"),
        "compact_closed_loop_candidate_self_contained_simulation_runner": closed_loop_candidate.get(
            "self_contained_simulation_runner"
        ),
        "compact_closed_loop_candidate_python_files": closed_loop_candidate.get("candidate_python_file_count"),
        "compact_closed_loop_candidate_python_lines": closed_loop_candidate.get("candidate_python_line_count"),
        "compact_closed_loop_candidate_line_limit_ok": closed_loop_candidate.get(
            "candidate_python_line_limit_ok"
        ),
        "compact_closed_loop_candidate_rows": closed_loop_candidate.get("closed_loop_local_rows"),
        "compact_closed_loop_candidate_models": closed_loop_candidate.get("closed_loop_models"),
        "compact_closed_loop_candidate_imports_v046_v047_v048_or_v029": closed_loop_candidate.get(
            "imports_v046_v047_v048_or_v029"
        ),
        "p1_single_runner_candidate_ready": p1_local_runner_audit.get("p1_single_runner_candidate_ready"),
        "p1_double_runner_candidate_ready": p1_local_runner_audit.get("p1_double_runner_candidate_ready"),
        "p1_regenerated_candidate_rows": p1_local_runner_audit.get("p1_regenerated_candidate_rows"),
        "p1_required_rows": p1_local_runner_audit.get("p1_required_rows"),
        "p1_missing_candidate_rows": p1_local_runner_audit.get("p1_missing_candidate_rows"),
        "p1_single_runner_candidate_rows": p1_single_candidate.get("rows"),
        "p1_single_runner_candidate_status": p1_single_candidate.get("status"),
        "p1_single_runner_candidate_position_order": p1_single_candidate.get("position_order"),
        "p1_single_runner_candidate_velocity_order": p1_single_candidate.get("velocity_order"),
        "p1_single_runner_candidate_imports_v047_or_v048": p1_single_candidate.get("imports_v047_or_v048"),
        "p1_single_runner_candidate_p1_complete": p1_single_candidate.get("p1_complete"),
        "p1_double_runner_candidate_rows": p1_double_candidate.get("rows"),
        "p1_double_runner_candidate_status": p1_double_candidate.get("status"),
        "p1_double_runner_candidate_position_order": p1_double_candidate.get("position_order"),
        "p1_double_runner_candidate_velocity_order": p1_double_candidate.get("velocity_order"),
        "p1_double_runner_candidate_imports_v047_v048_or_v029": p1_double_candidate.get(
            "imports_v047_v048_or_v029"
        ),
        "p1_double_runner_candidate_p1_complete": p1_double_candidate.get("p1_complete"),
        "human_runnable_local_evidence_example_count": len(human_runnable_local_evidence_examples),
        "human_runnable_local_evidence_examples": human_runnable_local_evidence_examples,
        "human_runnable_self_contained_local_examples": human_runnable_self_contained_examples,
        "human_runnable_replay_only_local_examples": human_runnable_replay_only_examples,
        "human_runnable_four_example_local_evidence_available": human_runnable_four_example_local_evidence_available,
        "human_runnable_four_example_self_contained_simulation_ready": (
            human_runnable_four_example_self_contained_simulation_ready
        ),
        "b6_four_example_local_evidence_runner_passed": b6_local_evidence.get("b6_local_evidence_runner_passed"),
        "b6_four_example_local_rows": b6_local_evidence.get("local_rows"),
        "b6_four_example_self_contained_examples": b6_local_evidence.get("self_contained_examples"),
        "b6_four_example_replay_only_examples": b6_local_evidence.get("replay_only_examples"),
        "b6_four_example_self_contained_simulation_ready": b6_local_evidence.get(
            "human_runnable_four_example_self_contained_simulation_ready"
        ),
        "b6_four_example_source_policy_rows_closed": b6_local_evidence.get("source_policy_external_rows_closed"),
        "b6_four_example_source_policy_rows_total": b6_local_evidence.get("source_policy_external_rows_total"),
        "b6_four_example_proof_gap_closed": b6_local_evidence.get("global_proof_gap_closed"),
        "b6_four_example_direct_pc2_proof_gap_closed": b6_local_evidence.get(
            "direct_residual_bridge_proof_gap_closed", b6_local_evidence.get("global_proof_gap_closed")
        ),
        "b6_four_example_proof_gap_scope": (
            "legacy global_proof_gap_closed key means direct residual-bridge/PC2 closure only; "
            "primitive/Taylor, solver-policy, residual-to-error, and source-policy boundaries remain separate"
        ),
        "local_accepted_runner_companion_status": local_runner_companion.get("status"),
        "local_accepted_runner_companion_launcher_passed": local_runner_companion.get("launcher_passed"),
        "local_accepted_runner_companion_local_rows": local_runner_companion.get("local_rows"),
        "local_accepted_runner_companion_python_lines": local_runner_companion.get("candidate_python_line_count"),
        "local_accepted_runner_companion_source_policy_rows_closed": local_runner_companion.get(
            "source_policy_closed_rows"
        ),
        "local_accepted_runner_companion_source_policy_rows_total": local_runner_companion.get(
            "source_policy_total_rows"
        ),
        "local_accepted_runner_companion_full_source_policy_ready": local_runner_companion.get(
            "full_source_policy_runner_package_ready"
        ),
        "narrowed_reproducibility_package_audit_status": narrowed_repro_audit.get("status"),
        "narrowed_claim_reproducibility_package_ready": narrowed_repro_audit.get(
            "narrowed_claim_reproducibility_package_ready"
        ),
        "narrowed_reproducibility_package_source_policy_rows_closed": narrowed_repro_audit.get(
            "source_policy_rows_closed"
        ),
        "narrowed_reproducibility_package_source_policy_rows_total": narrowed_repro_audit.get(
            "source_policy_rows_total"
        ),
        "narrowed_reproducibility_package_full_source_policy_runner_ready": narrowed_repro_audit.get(
            "full_source_policy_runner_package_ready"
        ),
        "narrowed_repro_code_archive_status": narrowed_repro_code_archive.get("status"),
        "narrowed_repro_code_archive_entry_count": narrowed_repro_code_archive.get("entry_count"),
        "narrowed_repro_code_archive_python_files": narrowed_repro_code_archive.get("python_file_count"),
        "narrowed_repro_code_archive_python_lines": narrowed_repro_code_archive.get("python_line_count"),
        "narrowed_repro_code_archive_source_policy_rows_closed": narrowed_repro_code_archive.get(
            "source_policy_rows_closed"
        ),
        "narrowed_repro_code_archive_source_policy_rows_total": narrowed_repro_code_archive.get(
            "source_policy_rows_total"
        ),
        "narrowed_repro_code_archive_full_source_policy_runner_ready": narrowed_repro_code_archive.get(
            "full_source_policy_runner_package_ready"
        ),
        "narrowed_repro_code_archive_submission_ready": narrowed_repro_code_archive.get("submission_ready"),
        "narrowed_archive_boundary_status": narrowed_repro_code_archive.get(
            "narrowed_archive_boundary", {}
        ).get("status"),
        "narrowed_archive_boundary_scope": narrowed_repro_code_archive.get(
            "narrowed_archive_boundary", {}
        ).get("scope"),
        "narrowed_archive_boundary_blocking_ids": narrowed_repro_code_archive.get(
            "narrowed_archive_boundary", {}
        ).get("blocking_ids"),
        "narrowed_archive_boundary_blocker_status_by_id": narrowed_repro_code_archive.get(
            "narrowed_archive_boundary", {}
        ).get("blocker_status_by_id"),
        "narrowed_archive_boundary_blocker_next_actions_by_id": narrowed_repro_code_archive.get(
            "narrowed_archive_boundary", {}
        ).get("blocker_next_actions_by_id"),
        "narrowed_archive_boundary_blocker_required_to_close_by_id": narrowed_repro_code_archive.get(
            "narrowed_archive_boundary", {}
        ).get("blocker_required_to_close_by_id"),
        "narrowed_archive_boundary_blocker_safe_next_actions_by_id": narrowed_repro_code_archive.get(
            "narrowed_archive_boundary", {}
        ).get("blocker_safe_next_actions_by_id"),
        "narrowed_archive_boundary_blocker_opt_in_required_actions_by_id": narrowed_repro_code_archive.get(
            "narrowed_archive_boundary", {}
        ).get("blocker_opt_in_required_actions_by_id"),
        "narrowed_archive_boundary_closure_allowed_by_id": narrowed_repro_code_archive.get(
            "narrowed_archive_boundary", {}
        ).get("closure_allowed_by_id"),
        "narrowed_archive_boundary_archive_effect_by_id": narrowed_repro_code_archive.get(
            "narrowed_archive_boundary", {}
        ).get("archive_effect_by_id"),
        "narrowed_archive_boundary_source_policy_closed_ratio": narrowed_repro_code_archive.get(
            "narrowed_archive_boundary", {}
        ).get("source_policy_closed_ratio"),
        "narrowed_archive_boundary_current_archive_usable_as_full_source_policy_runner_archive": (
            narrowed_repro_code_archive.get("narrowed_archive_boundary", {}).get(
                "current_archive_usable_as_full_source_policy_runner_archive"
            )
        ),
        "narrowed_archive_boundary_source_policy_execution_allowed_now": narrowed_repro_code_archive.get(
            "narrowed_archive_boundary", {}
        ).get("source_policy_execution_allowed_now"),
        "narrowed_archive_boundary_exact_b4_opt_in_required_for_execution": narrowed_repro_code_archive.get(
            "narrowed_archive_boundary", {}
        ).get("exact_b4_opt_in_required_for_execution"),
        "narrowed_archive_boundary_safe_action_ids": narrowed_repro_code_archive.get(
            "narrowed_archive_boundary", {}
        ).get("safe_action_ids"),
        "narrowed_archive_boundary_opt_in_action_ids": narrowed_repro_code_archive.get(
            "narrowed_archive_boundary", {}
        ).get("opt_in_action_ids"),
        "narrowed_archive_boundary_source_artifacts": narrowed_repro_code_archive.get(
            "narrowed_archive_boundary", {}
        ).get("source_artifacts"),
        "narrowed_repro_code_archive_handoff_exact_approval": narrowed_repro_code_archive.get(
            "source_policy_execution_handoff", {}
        ).get("exact_required_user_approval_statement"),
        "narrowed_repro_code_archive_handoff_driver": narrowed_repro_code_archive.get(
            "source_policy_execution_handoff", {}
        ).get("guarded_execution_driver"),
        "narrowed_repro_code_archive_handoff_driver_requires_exact": narrowed_repro_code_archive.get(
            "source_policy_execution_handoff", {}
        ).get("driver_requires_exact_approval"),
        "narrowed_repro_code_archive_handoff_driver_does_not_authorize": narrowed_repro_code_archive.get(
            "source_policy_execution_handoff", {}
        ).get("driver_does_not_authorize_execution"),
        "narrowed_repro_code_archive_handoff_opt_in_commands": narrowed_repro_code_archive.get(
            "source_policy_execution_handoff", {}
        ).get("opt_in_required_command_count"),
        "narrowed_repro_code_archive_handoff_mapped_rows": narrowed_repro_code_archive.get(
            "source_policy_execution_handoff", {}
        ).get("opt_in_required_mapped_external_rows"),
        "full_source_policy_runner_archive_gap_status": full_source_runner_gap.get("status"),
        "full_source_policy_runner_archive_gap_ready_now": full_source_runner_gap.get(
            "closure_conditions", {}
        ).get("full_archive_ready_now"),
        "full_source_policy_runner_archive_gap_current_archive_use": full_source_runner_gap.get(
            "closure_conditions", {}
        ).get("can_use_current_archive_as_full_source_policy_runner_archive"),
        "full_source_policy_runner_archive_gap_source_policy_rows_closed": full_source_runner_gap.get(
            "source_policy_rows", {}
        ).get("closed"),
        "full_source_policy_runner_archive_gap_source_policy_rows_total": full_source_runner_gap.get(
            "source_policy_rows", {}
        ).get("total"),
        "full_source_policy_runner_archive_gap_terminal_unable_rows": full_source_runner_gap.get(
            "closure_conditions", {}
        ).get("terminal_unable_to_reproduce_rows"),
        "full_source_policy_runner_archive_gap_ra_hi_open_rows": full_source_runner_gap.get(
            "closure_conditions", {}
        ).get("ra_hi_rows_requiring_authorized_closeout_or_new_artifact"),
        "full_source_policy_runner_archive_gap_terminal_reopen_conditions": (
            full_source_terminal_reopen_conditions
        ),
        "source_policy_reopen_condition_monitor_status": source_policy_reopen_monitor.get(
            "status"
        ),
        "source_policy_reopen_condition_monitor_source_policy_closed": (
            source_policy_reopen_monitor.get("source_policy_closed")
        ),
        "source_policy_reopen_condition_monitor_source_policy_closed_ratio": (
            source_policy_reopen_monitor.get("source_policy_closed_ratio")
        ),
        "source_policy_reopen_condition_monitor_local_scan_digest": (
            source_policy_reopen_monitor.get("local_scan_digest")
        ),
        "source_policy_reopen_condition_monitor_evidence_digest": (
            source_policy_reopen_monitor.get("monitor_evidence_digest")
        ),
        "full_source_policy_runner_archive_gap_reopen_monitor_status": (
            full_source_runner_gap.get("reopen_condition_monitor", {}).get("status")
        ),
        "full_source_policy_runner_archive_gap_reopen_monitor_source_policy_closed": (
            full_source_runner_gap.get("reopen_condition_monitor", {}).get(
                "source_policy_closed"
            )
        ),
        "full_source_policy_runner_archive_gap_reopen_monitor_source_policy_closed_ratio": (
            full_source_runner_gap.get("reopen_condition_monitor", {}).get(
                "source_policy_closed_ratio"
            )
        ),
        "full_source_policy_runner_archive_gap_reopen_monitor_local_scan_digest": (
            full_source_runner_gap.get("reopen_condition_monitor", {}).get(
                "local_scan_digest"
            )
        ),
        "full_source_policy_runner_archive_gap_reopen_monitor_evidence_digest": (
            full_source_runner_gap.get("reopen_condition_monitor", {}).get(
                "monitor_evidence_digest"
            )
        ),
        "full_source_policy_runner_archive_gap_tfe_reopen_condition": (
            full_source_terminal_reopen_conditions.get("tfe2026_original_pendulum")
        ),
        "full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_status": (
            objective_summary.get(
                "full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_status"
            )
        ),
        "full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_entrypoints": (
            objective_summary.get(
                "full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_entrypoints"
            )
        ),
        "full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_candidate_backed": (
            objective_summary.get(
                "full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_candidate_backed"
            )
        ),
        "full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_source_policy_rows_completed": (
            objective_summary.get(
                "full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_source_policy_rows_completed"
            )
        ),
        "full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_execution_blocks": (
            objective_summary.get(
                "full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_execution_blocks"
            )
        ),
        "full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_safe_use": (
            objective_summary.get(
                "full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_safe_use"
            )
        ),
        "full_source_policy_runner_archive_gap_action_boundary": objective_summary.get(
            "full_source_policy_runner_archive_gap_action_boundary"
        ),
        "full_source_policy_runner_archive_gap_safe_without_b4_opt_in_count": objective_summary.get(
            "full_source_policy_runner_archive_gap_safe_without_b4_opt_in_count"
        ),
        "full_source_policy_runner_archive_gap_opt_in_required_action_count": objective_summary.get(
            "full_source_policy_runner_archive_gap_opt_in_required_action_count"
        ),
        "full_source_policy_runner_archive_gap_source_policy_execution_allowed_now": objective_summary.get(
            "full_source_policy_runner_archive_gap_source_policy_execution_allowed_now"
        ),
        "full_source_policy_runner_archive_gap_source_policy_execution_invoked": objective_summary.get(
            "full_source_policy_runner_archive_gap_source_policy_execution_invoked"
        ),
        "full_source_policy_runner_archive_gap_exact_b4_opt_in_required_for_execution": (
            objective_summary.get(
                "full_source_policy_runner_archive_gap_exact_b4_opt_in_required_for_execution"
            )
        ),
        "full_source_policy_runner_archive_gap_opt_in_required_command_count": objective_summary.get(
            "full_source_policy_runner_archive_gap_opt_in_required_command_count"
        ),
        "full_source_policy_runner_archive_gap_opt_in_required_mapped_external_rows": (
            objective_summary.get(
                "full_source_policy_runner_archive_gap_opt_in_required_mapped_external_rows"
            )
        ),
        "full_source_policy_runner_archive_gap_safe_action_ids": objective_summary.get(
            "full_source_policy_runner_archive_gap_safe_action_ids"
        ),
        "full_source_policy_runner_archive_gap_opt_in_action_ids": objective_summary.get(
            "full_source_policy_runner_archive_gap_opt_in_action_ids"
        ),
        "full_source_policy_runner_archive_gap_vp2024_reopen_condition": (
            full_source_terminal_reopen_conditions.get("vp2024_velocity_partitioning")
        ),
        "full_source_policy_runner_archive_gap_required_approval_statement": (
            full_source_ra_hi_approval_statement
        ),
        "source_policy_execution_handoff_status": b4_execution_handoff.get("status"),
        "source_policy_execution_handoff_authorized": b4_execution_handoff.get(
            "execution_authorized"
        ),
        "source_policy_execution_handoff_commands_not_run": b4_execution_handoff.get(
            "commands_not_run_by_handoff"
        ),
        "source_policy_execution_handoff_ready_command_count": b4_execution_handoff.get(
            "ready_command_count"
        ),
        "source_policy_execution_handoff_ready_command_mapped_rows": b4_execution_handoff.get(
            "ready_command_mapped_external_rows"
        ),
        "source_policy_execution_handoff_terminal_unable_rows": b4_execution_handoff.get(
            "terminal_unable_to_reproduce_rows"
        ),
        "source_policy_execution_handoff_command_traceability_summary": (
            b4_command_traceability_summary
        ),
        "source_policy_execution_handoff_unique_mapped_row_count": (
            b4_command_traceability_summary.get("unique_mapped_row_count")
        ),
        "source_policy_execution_handoff_ra_hi_unique_row_count": (
            b4_command_traceability_summary.get("ra_hi_unique_row_count")
        ),
        "source_policy_execution_handoff_ra_hi_unique_rows_all_mapped": (
            b4_command_traceability_summary.get("ra_hi_unique_rows_all_mapped")
        ),
        "source_policy_execution_handoff_declared_mapped_row_reference_total": (
            b4_command_traceability_summary.get("declared_mapped_row_reference_total")
        ),
        "source_policy_execution_handoff_traced_command_row_reference_total": (
            b4_command_traceability_summary.get("traced_command_row_reference_total")
        ),
        "source_policy_execution_handoff_declared_vs_traced_mismatch_count": (
            b4_command_traceability_summary.get("declared_vs_traced_mismatch_count")
        ),
        "source_policy_execution_handoff_terminal_rows_with_command_refs": (
            b4_command_traceability_summary.get("terminal_rows_with_command_refs")
        ),
        "source_policy_execution_handoff_traceability_closed_rows": (
            b4_command_traceability_summary.get("source_policy_closed_rows")
        ),
        "source_policy_execution_handoff_traceability_promotion_ready_rows": (
            b4_command_traceability_summary.get("promotion_ready_rows")
        ),
        "source_policy_execution_handoff_exact_approval_statement": b4_execution_handoff.get(
            "exact_approval_statement"
        ),
        "source_policy_execution_handoff_driver": b4_execution_handoff.get(
            "guarded_execution_driver"
        ),
        "source_policy_execution_handoff_driver_requires_exact_approval": b4_execution_handoff.get(
            "driver_requires_exact_approval"
        ),
        "source_policy_execution_handoff_driver_does_not_authorize_execution": b4_execution_handoff.get(
            "driver_does_not_authorize_execution"
        ),
        "source_policy_execution_handoff_opt_in_required_command_count": b4_execution_handoff.get(
            "opt_in_required_command_count"
        ),
        "source_policy_execution_handoff_opt_in_required_mapped_rows": b4_execution_handoff.get(
            "opt_in_required_mapped_external_rows"
        ),
        "source_policy_command_preflight_freeze_status": b4_command_freeze.get("status"),
        "source_policy_command_preflight_freeze_ready_commands": b4_command_freeze.get(
            "ready_command_count"
        ),
        "source_policy_command_preflight_freeze_unique_rows": b4_command_freeze.get(
            "unique_mapped_ra_hi_rows"
        ),
        "source_policy_command_preflight_freeze_row_refs": b4_command_freeze.get(
            "traced_row_reference_total"
        ),
        "source_policy_command_preflight_freeze_mismatches": b4_command_freeze.get(
            "declared_vs_traced_mismatch_count"
        ),
        "source_policy_command_preflight_freeze_expected_artifacts": b4_command_freeze.get(
            "expected_artifacts_existing_now"
        ),
        "source_policy_command_preflight_freeze_expected_artifact_total": b4_command_freeze.get(
            "expected_artifact_count"
        ),
        "source_policy_command_preflight_freeze_commands_executed": b4_command_freeze.get(
            "commands_executed_by_freeze"
        ),
        "source_policy_command_preflight_freeze_source_policy_closed": b4_command_freeze.get(
            "source_policy_rows_closed"
        ),
        "source_policy_expected_output_schema_audit_status": b4_expected_output_schema_audit.get(
            "status"
        ),
        "source_policy_expected_output_schema_audit_commands": b4_expected_output_schema_audit.get(
            "command_count"
        ),
        "source_policy_expected_output_schema_audit_artifacts": b4_expected_output_schema_audit.get(
            "expected_artifact_count"
        ),
        "source_policy_expected_output_schema_audit_hash_match": b4_expected_output_schema_audit.get(
            "artifacts_sha256_match_freeze"
        ),
        "source_policy_expected_output_schema_audit_csv_parseable": b4_expected_output_schema_audit.get(
            "csv_parseable_artifacts"
        ),
        "source_policy_expected_output_schema_audit_json_parseable": b4_expected_output_schema_audit.get(
            "json_summary_parseable_artifacts"
        ),
        "source_policy_expected_output_schema_audit_schema_ready": b4_expected_output_schema_audit.get(
            "schema_ready_commands"
        ),
        "source_policy_expected_output_schema_audit_commands_executed": b4_expected_output_schema_audit.get(
            "commands_executed_by_audit"
        ),
        "source_policy_expected_output_schema_audit_source_policy_closed": b4_expected_output_schema_audit.get(
            "source_policy_rows_closed"
        ),
        "source_policy_expected_output_promotion_readiness_blocker_status": b4_expected_output_promotion_readiness_blocker_audit.get(
            "status"
        ),
        "source_policy_expected_output_promotion_readiness_blocker_commands": b4_expected_output_promotion_readiness_blocker_audit.get(
            "command_count"
        ),
        "source_policy_expected_output_promotion_readiness_blocker_schema_ready": b4_expected_output_promotion_readiness_blocker_audit.get(
            "schema_ready_command_count"
        ),
        "source_policy_expected_output_promotion_readiness_blocker_promotion_ready": b4_expected_output_promotion_readiness_blocker_audit.get(
            "promotion_ready_command_count"
        ),
        "source_policy_expected_output_promotion_readiness_blocker_row_refs": b4_expected_output_promotion_readiness_blocker_audit.get(
            "command_row_reference_total"
        ),
        "source_policy_expected_output_promotion_readiness_blocker_unique_rows": b4_expected_output_promotion_readiness_blocker_audit.get(
            "unique_mapped_ra_hi_row_count"
        ),
        "source_policy_expected_output_promotion_readiness_blocker_not_promoted": b4_expected_output_promotion_readiness_blocker_audit.get(
            "unique_mapped_ra_hi_rows_not_promoted"
        ),
        "source_policy_expected_output_promotion_readiness_blocker_summary_closed": b4_expected_output_promotion_readiness_blocker_audit.get(
            "summary_source_policy_rows_closed_total"
        ),
        "source_policy_expected_output_promotion_readiness_blocker_summary_promoted": b4_expected_output_promotion_readiness_blocker_audit.get(
            "summary_source_policy_rows_promoted_total"
        ),
        "source_policy_expected_output_promotion_readiness_blocker_blocked_commands": b4_expected_output_promotion_readiness_blocker_audit.get(
            "commands_with_schema_ready_but_promotion_blocked"
        ),
        "oc6_source_equivalent_reopen_readiness_status": oc6_source_equivalent_reopen_readiness_audit.get(
            "status"
        ),
        "oc6_source_equivalent_reopen_readiness_rows": oc6_source_equivalent_reopen_readiness_audit.get(
            "row_count"
        ),
        "oc6_source_equivalent_reopen_readiness_tfe_rows": oc6_source_equivalent_reopen_readiness_audit.get(
            "tfe_rows"
        ),
        "oc6_source_equivalent_reopen_readiness_vp_rows": oc6_source_equivalent_reopen_readiness_audit.get(
            "vp_rows"
        ),
        "oc6_source_equivalent_reopen_readiness_unable_rows": oc6_source_equivalent_reopen_readiness_audit.get(
            "unable_to_reproduce_rows"
        ),
        "oc6_source_equivalent_reopen_readiness_public_code_rows": oc6_source_equivalent_reopen_readiness_audit.get(
            "public_code_available_rows"
        ),
        "oc6_source_equivalent_reopen_readiness_candidate_rows": oc6_source_equivalent_reopen_readiness_audit.get(
            "candidate_runner_available_rows"
        ),
        "oc6_source_equivalent_reopen_readiness_source_equivalent_rows": oc6_source_equivalent_reopen_readiness_audit.get(
            "candidate_runner_source_policy_equivalent_rows"
        ),
        "oc6_source_equivalent_reopen_readiness_positive_public_rows": oc6_source_equivalent_reopen_readiness_audit.get(
            "positive_public_code_artifact_rows"
        ),
        "oc6_source_equivalent_reopen_readiness_local_positive_rows": oc6_source_equivalent_reopen_readiness_audit.get(
            "local_positive_reopen_artifact_rows"
        ),
        "oc6_source_equivalent_reopen_readiness_closed_rows": oc6_source_equivalent_reopen_readiness_audit.get(
            "source_policy_rows_closed"
        ),
        "oc6_source_equivalent_reopen_readiness_performs_new_public_code_search": oc6_source_equivalent_reopen_readiness_audit.get(
            "performs_new_public_code_search"
        ),
        "oc6_source_equivalent_reopen_readiness_oc6_can_close_now": oc6_source_equivalent_reopen_readiness_audit.get(
            "oc6_can_close_now"
        ),
        "oc6_source_equivalent_reopen_readiness_latest_external_probe_date": oc6_source_equivalent_reopen_readiness_audit.get(
            "latest_external_probe_date_checked"
        ),
        "oc6_source_equivalent_reopen_readiness_latest_external_probe_count": oc6_source_equivalent_reopen_readiness_audit.get(
            "latest_external_probe_count"
        ),
        "oc6_source_equivalent_reopen_readiness_latest_external_probe_positive_artifact_rows": oc6_source_equivalent_reopen_readiness_audit.get(
            "latest_external_probe_positive_public_code_artifact_rows"
        ),
        "oc6_source_equivalent_reopen_readiness_latest_external_probe_source_policy_rows_closed": oc6_source_equivalent_reopen_readiness_audit.get(
            "latest_external_probe_source_policy_rows_closed"
        ),
        "oc6_source_equivalent_reopen_readiness_latest_external_probe_access_limited_count": oc6_source_equivalent_reopen_readiness_audit.get(
            "latest_external_probe_access_limited_count"
        ),
        "oc6_source_equivalent_reopen_readiness_latest_external_probe_global_absence_proved": oc6_source_equivalent_reopen_readiness_audit.get(
            "latest_external_probe_global_absence_proved"
        ),
        "oc6_source_equivalent_reopen_readiness_latest_external_probe_reopen_triggered": oc6_source_equivalent_reopen_readiness_audit.get(
            "latest_external_probe_source_policy_reopen_triggered"
        ),
        "oc6_reopen_latest_external_probe": oc6_latest_external_probe,
        "research_audit_primary_submission_line_limit": code_checks.get(
            "research_audit_primary_submission_line_limit"
        ),
        "research_audit_repo_too_large_for_primary_submission": code_checks.get(
            "research_audit_repo_too_large_for_primary_submission"
        ),
        "research_audit_repo_primary_submission_allowed": code_checks.get(
            "research_audit_repo_primary_submission_allowed"
        ),
        "research_audit_repo_provenance_only": code_checks.get("research_audit_repo_provenance_only"),
        "reviewer_facing_python_line_limit": code_checks.get("reviewer_facing_python_line_limit"),
        "reviewer_facing_python_file_limit": code_checks.get("reviewer_facing_python_file_limit"),
        "code_bloat_risk_for_submission": code_checks.get("code_bloat_risk_for_submission"),
        "combined_python_line_count": code_checks.get("combined_python_line_count"),
        "objective_complete": objective_completion.get("objective_complete"),
        "objective_blocking_open_count": objective_completion.get("summary", {}).get("blocking_open_count"),
        "objective_blocking_ids": objective_blocking_ids,
        "objective_blockers_by_id": objective_blockers_by_id,
        "objective_blocker_status_by_id": objective_blocker_status_by_id,
        "objective_blocker_next_actions_by_id": objective_blocker_next_actions_by_id,
        "blocker_required_to_close_by_id": objective_blocker_required_to_close_by_id,
        "blocker_safe_next_actions_by_id": objective_blocker_safe_next_actions_by_id,
        "blocker_opt_in_required_actions_by_id": objective_blocker_opt_in_required_actions_by_id,
        "objective_blocker_required_to_close_by_id": objective_blocker_required_to_close_by_id,
        "objective_blocker_safe_next_actions_by_id": objective_blocker_safe_next_actions_by_id,
        "objective_blocker_opt_in_required_actions_by_id": objective_blocker_opt_in_required_actions_by_id,
    }
    minimal_submission_code_dependency_boundary = {
        "schema": "minimal-submission-code-dependency-boundary-v1",
        "status": "narrowed_repro_ready_full_source_policy_package_blocked",
        "minimal_reproducible_submission_code_ready": summary.get(
            "minimal_reproducible_submission_code_ready"
        ),
        "narrowed_claim_reproducibility_package_ready": summary.get(
            "narrowed_claim_reproducibility_package_ready"
        ),
        "narrowed_repro_code_archive_ready": (
            summary.get("narrowed_repro_code_archive_status")
            == "narrowed_repro_code_archive_ready_source_policy_open"
        ),
        "narrowed_repro_code_archive_submission_ready": summary.get(
            "narrowed_repro_code_archive_submission_ready"
        ),
        "local_runner_centered_candidate_ready": summary.get("local_runner_centered_candidate_ready"),
        "runner_centered_package_ready": summary.get("runner_centered_package_ready"),
        "full_source_policy_runner_package_ready": summary.get(
            "full_source_policy_runner_package_ready"
        ),
        "candidate_code_size_ok": summary.get("minimal_reproducibility_candidate_code_size_ok"),
        "candidate_replay_only": summary.get("minimal_reproducibility_candidate_replay_only"),
        "candidate_runner_centered": summary.get("minimal_reproducibility_candidate_runner_centered"),
        "candidate_source_policy_ready": summary.get(
            "minimal_reproducibility_candidate_source_policy_ready"
        ),
        "candidate_proof_ready": summary.get("minimal_reproducibility_candidate_proof_ready"),
        "source_policy_rows_closed": summary.get("source_policy_closed_rows"),
        "source_policy_rows_total": summary.get("source_policy_total_rows"),
        "narrowed_archive_source_policy_rows_closed": summary.get(
            "narrowed_repro_code_archive_source_policy_rows_closed"
        ),
        "narrowed_archive_source_policy_rows_total": summary.get(
            "narrowed_repro_code_archive_source_policy_rows_total"
        ),
        "blocking_objective_requirements": [
            item
            for item in objective_completion.get("blocking_requirement_ids", [])
            if item in {"OC4", "OC6", "OC12"}
        ],
        "blocking_upstream_gates": [
            "OC4_source_policy_reproduction_rows",
            "OC6_TFE_source_policy_runner",
            "OC12_full_source_policy_runner_archive",
        ],
        "safe_current_package_use": "narrowed_claim_replay_and_audit_provenance_only",
        "primary_submission_package_allowed": False,
        "audit_tree_provenance_only": summary.get("research_audit_repo_provenance_only"),
        "audit_tree_too_large_for_primary_submission": summary.get(
            "research_audit_repo_too_large_for_primary_submission"
        ),
        "reviewer_facing_size_limits": {
            "python_files": summary.get("reviewer_facing_python_file_limit"),
            "python_lines": summary.get("reviewer_facing_python_line_limit"),
        },
    }
    summary["minimal_submission_code_dependency_boundary_status"] = (
        minimal_submission_code_dependency_boundary["status"]
    )
    summary["minimal_submission_code_dependency_blockers"] = (
        minimal_submission_code_dependency_boundary["blocking_objective_requirements"]
    )
    summary["minimal_submission_code_dependency_safe_use"] = (
        minimal_submission_code_dependency_boundary["safe_current_package_use"]
    )
    summary["minimal_submission_code_dependency_primary_allowed"] = (
        minimal_submission_code_dependency_boundary["primary_submission_package_allowed"]
    )
    strict_proof_writing_submission_boundary = dict(
        objective_completion.get("strict_proof_writing_submission_boundary", {})
    )
    summary["strict_proof_writing_submission_boundary_status"] = (
        strict_proof_writing_submission_boundary.get("status")
    )
    summary["strict_proof_writing_card_status"] = (
        strict_proof_writing_submission_boundary.get("proof_writing_card_status")
    )
    summary["strict_proof_writing_reader_facing_manuscript_boundary_present"] = (
        strict_proof_writing_submission_boundary.get("reader_facing_manuscript_boundary_present")
    )
    summary["strict_proof_writing_p7_retained_nonpromotion_boundary_present"] = (
        strict_proof_writing_submission_boundary.get("p7_retained_nonpromotion_boundary_present")
    )
    summary["strict_proof_writing_b1_closure_scope_boundary_present"] = (
        strict_proof_writing_submission_boundary.get("b1_closure_scope_boundary_present")
    )
    summary["strict_proof_writing_b1_ad_expanded_closure_ledger_present"] = (
        strict_proof_writing_submission_boundary.get(
            "b1_ad_expanded_closure_ledger_present"
        )
    )
    summary["strict_proof_writing_b1_ad_expanded_symbolic_oracle_closed_cells"] = (
        strict_proof_writing_submission_boundary.get(
            "b1_ad_expanded_symbolic_oracle_closed_cells"
        )
    )
    summary["strict_proof_writing_p6_solver_scope_boundary_present"] = (
        strict_proof_writing_submission_boundary.get("p6_solver_scope_boundary_present")
    )
    summary["strict_proof_writing_p1p2_compact_tube_boundary_present"] = (
        strict_proof_writing_submission_boundary.get("p1p2_compact_tube_boundary_present")
    )
    summary["strict_proof_writing_p3p4_implementation_boundary_present"] = (
        strict_proof_writing_submission_boundary.get("p3p4_implementation_boundary_present")
    )
    summary["strict_proof_writing_p5_direct_route_boundary_present"] = (
        strict_proof_writing_submission_boundary.get("p5_direct_route_boundary_present")
    )
    summary["strict_proof_writing_p_interface_satisfaction_ledger_present"] = (
        strict_proof_writing_submission_boundary.get("p_interface_satisfaction_ledger_present")
    )
    summary["strict_proof_writing_p7_residual_to_error_ledger_present"] = (
        strict_proof_writing_submission_boundary.get(
            "p7_residual_to_error_ledger_present"
        )
    )
    summary["strict_proof_writing_proof_causality_ledger_present"] = (
        strict_proof_writing_submission_boundary.get("proof_causality_ledger_present")
    )
    summary["strict_proof_writing_direct_route_anticircularity_ledger_present"] = (
        strict_proof_writing_submission_boundary.get(
            "direct_route_anticircularity_ledger_present"
        )
    )
    summary["strict_proof_writing_theorem_use_rule_present"] = (
        strict_proof_writing_submission_boundary.get("theorem_use_rule_present")
    )
    summary["strict_proof_writing_quantifier_domain_ledger_present"] = (
        strict_proof_writing_submission_boundary.get("quantifier_domain_ledger_present")
    )
    summary["strict_proof_writing_local_global_transfer_ledger_present"] = (
        strict_proof_writing_submission_boundary.get(
            "local_global_transfer_ledger_present"
        )
    )
    summary["strict_proof_writing_objective_completion_boundary_present"] = (
        strict_proof_writing_submission_boundary.get(
            "objective_completion_boundary_present"
        )
    )
    summary["strict_proof_writing_constant_dependency_ledger_present"] = (
        strict_proof_writing_submission_boundary.get("constant_dependency_ledger_present")
    )
    summary["strict_proof_writing_theorem_dependency_consumption_ledger_present"] = (
        strict_proof_writing_submission_boundary.get(
            "theorem_dependency_consumption_ledger_present"
        )
    )
    summary["strict_proof_writing_branch_consistency_ledger_present"] = (
        strict_proof_writing_submission_boundary.get("branch_consistency_ledger_present")
    )
    summary["strict_proof_writing_implementation_route_oracle_ledger_present"] = (
        strict_proof_writing_submission_boundary.get(
            "implementation_route_oracle_ledger_present"
        )
    )
    summary["strict_proof_writing_nonlinear_solver_scale_ledger_present"] = (
        strict_proof_writing_submission_boundary.get(
            "nonlinear_solver_scale_ledger_present"
        )
    )
    summary["strict_proof_writing_local_defect_decomposition_ledger_present"] = (
        strict_proof_writing_submission_boundary.get(
            "local_defect_decomposition_ledger_present"
        )
    )
    summary["strict_proof_writing_theorem_output_scope_ledger_present"] = (
        strict_proof_writing_submission_boundary.get("theorem_output_scope_ledger_present")
    )
    summary["strict_proof_writing_reporting_map_ledger_present"] = (
        strict_proof_writing_submission_boundary.get("reporting_map_ledger_present")
    )
    summary["strict_proof_writing_direct_pc2_proof_gap_closed"] = (
        strict_proof_writing_submission_boundary.get("direct_pc2_proof_gap_closed")
    )
    summary["strict_proof_writing_stage_residual_O_h7_implementation_defect_proved"] = (
        strict_proof_writing_submission_boundary.get(
            "stage_residual_O_h7_implementation_defect_proved"
        )
    )
    summary["strict_proof_writing_dynamic_symbolic_oracle_complete"] = (
        strict_proof_writing_submission_boundary.get("dynamic_symbolic_oracle_complete")
    )
    summary["strict_proof_writing_eta_h_solver_policy_evidence_closed"] = (
        strict_proof_writing_submission_boundary.get(
            "eta_h_solver_policy_evidence_closed"
        )
    )
    summary["strict_proof_writing_fixed_tolerance_asymptotic_proof"] = (
        strict_proof_writing_submission_boundary.get(
            "fixed_tolerance_runs_are_asymptotic_proof"
        )
    )
    summary["strict_proof_writing_residual_to_error_route_promoted"] = (
        strict_proof_writing_submission_boundary.get("residual_to_error_route_promoted")
    )
    summary["strict_proof_writing_residual_to_error_not_promoted"] = (
        strict_proof_writing_submission_boundary.get("residual_to_error_not_promoted")
    )
    summary["strict_proof_writing_source_policy_or_full_tfe_not_promoted"] = (
        strict_proof_writing_submission_boundary.get(
            "source_policy_or_full_tfe_not_promoted"
        )
    )
    summary["strict_proof_writing_source_policy_full_tfe_not_promoted"] = (
        strict_proof_writing_submission_boundary.get(
            "source_policy_full_tfe_not_promoted"
        )
    )
    summary["strict_proof_writing_satisfied_close_requirement_ids"] = (
        strict_proof_writing_submission_boundary.get("satisfied_close_requirement_ids")
    )
    summary["strict_proof_writing_unsatisfied_close_requirement_ids"] = (
        strict_proof_writing_submission_boundary.get("unsatisfied_close_requirement_ids")
    )
    summary["strict_proof_writing_safe_reader_claim"] = (
        strict_proof_writing_submission_boundary.get("safe_reader_claim")
    )
    summary["strict_proof_writing_safe_reader_claim_boundary_present"] = (
        strict_proof_writing_submission_boundary.get(
            "safe_reader_claim_boundary_present"
        )
    )
    summary["strict_proof_writing_reading_rule_boundary_present"] = (
        strict_proof_writing_submission_boundary.get("reading_rule_boundary_present")
    )
    summary["strict_proof_writing_theorem_assumption_partition_boundary_present"] = (
        strict_proof_writing_submission_boundary.get(
            "theorem_assumption_partition_boundary_present"
        )
    )
    summary["strict_proof_writing_theorem_assumption_anchor_ids"] = (
        strict_proof_writing_submission_boundary.get("theorem_assumption_anchor_ids")
    )
    summary["strict_proof_writing_theorem_assumption_anchor_count"] = (
        strict_proof_writing_submission_boundary.get("theorem_assumption_anchor_count")
    )
    summary["strict_proof_writing_theorem_assumption_submission_satisfied_ids"] = (
        strict_proof_writing_submission_boundary.get(
            "theorem_assumption_submission_satisfied_ids"
        )
    )
    summary["strict_proof_writing_theorem_assumption_submission_satisfied_count"] = (
        strict_proof_writing_submission_boundary.get(
            "theorem_assumption_submission_satisfied_count"
        )
    )
    summary["strict_proof_writing_theorem_assumption_retained_or_open_ids"] = (
        strict_proof_writing_submission_boundary.get(
            "theorem_assumption_retained_or_open_ids"
        )
    )
    summary["strict_proof_writing_theorem_assumption_retained_or_open_count"] = (
        strict_proof_writing_submission_boundary.get(
            "theorem_assumption_retained_or_open_count"
        )
    )
    summary["strict_proof_writing_theorem_assumption_retained_theorem_interface_ids"] = (
        strict_proof_writing_submission_boundary.get(
            "theorem_assumption_retained_theorem_interface_ids"
        )
    )
    summary["strict_proof_writing_theorem_assumption_retained_theorem_interface_count"] = (
        strict_proof_writing_submission_boundary.get(
            "theorem_assumption_retained_theorem_interface_count"
        )
    )
    summary["strict_proof_writing_theorem_assumption_open_nonpromotion_boundary_ids"] = (
        strict_proof_writing_submission_boundary.get(
            "theorem_assumption_open_nonpromotion_boundary_ids"
        )
    )
    summary["strict_proof_writing_theorem_assumption_open_nonpromotion_boundary_count"] = (
        strict_proof_writing_submission_boundary.get(
            "theorem_assumption_open_nonpromotion_boundary_count"
        )
    )
    summary["strict_proof_writing_forbidden_reader_claims"] = (
        strict_proof_writing_submission_boundary.get("forbidden_reader_claims", [])
    )
    summary["strict_proof_writing_forbidden_reader_claims_boundary_present"] = (
        strict_proof_writing_submission_boundary.get(
            "forbidden_reader_claims_boundary_present"
        )
    )
    summary["strict_proof_writing_forbidden_unconditional_theorem_boundary_present"] = (
        strict_proof_writing_submission_boundary.get(
            "forbidden_unconditional_theorem_boundary_present"
        )
    )
    summary["strict_proof_writing_forbidden_eta_h_solver_policy_claim_boundary_present"] = (
        strict_proof_writing_submission_boundary.get(
            "forbidden_eta_h_solver_policy_claim_boundary_present"
        )
    )
    summary["strict_proof_writing_forbidden_fixed_tolerance_asymptotic_claim_boundary_present"] = (
        strict_proof_writing_submission_boundary.get(
            "forbidden_fixed_tolerance_asymptotic_claim_boundary_present"
        )
    )
    summary["strict_proof_writing_forbidden_residual_to_error_theorem_claim_boundary_present"] = (
        strict_proof_writing_submission_boundary.get(
            "forbidden_residual_to_error_theorem_claim_boundary_present"
        )
    )
    summary["strict_proof_writing_forbidden_source_policy_full_tfe_package_claim_boundary_present"] = (
        strict_proof_writing_submission_boundary.get(
            "forbidden_source_policy_full_tfe_package_claim_boundary_present"
        )
    )
    summary["strict_proof_writing_objective_blockers_retained"] = (
        strict_proof_writing_submission_boundary.get("objective_blockers_retained")
    )
    summary["strict_proof_writing_global_boundaries_retained"] = (
        strict_proof_writing_submission_boundary.get("proof_global_boundaries_retained", [])
    )
    summary["strict_proof_writing_submission_ready"] = (
        strict_proof_writing_submission_boundary.get("submission_ready")
    )
    summary["strict_proof_writing_package_boundary_status"] = (
        strict_proof_writing_submission_boundary.get("package_boundary_status")
    )

    manifest = {
        "schema": "cmame-reproducibility-package-manifest-v1",
        "status": "not_ready_self_contained_runner_centered_package_missing_source_policy",
        "read_only": True,
        "submission_ready": False,
        "generated_from": [
            "CMAME_REVIEW_AGENT_REPORT.json",
            "PAPER_NUMERICAL_RESULT_MATRIX.json",
            "RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.json",
            "B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.json",
                "B4_SOURCE_POLICY_WORK_PRECISION_EXECUTION_PLAN.json",
                "B4_EXISTING_ARTIFACT_PROMOTION_AUDIT.json",
                "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.json",
                "FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.json",
                "RA_HI_SOURCE_POLICY_POST_EXECUTION_ATTEMPT_CERTIFICATE.json",
                "RA_HI_SOURCE_POLICY_CLOSEOUT_CHECKLIST.json",
                "RA_HI_SOURCE_POLICY_OUTPUT_INVENTORY.json",
                "RA_HI_SOURCE_POLICY_PROMOTION_BLOCKER_MATRIX.json",
                "RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.json",
                "HI2022_RA_HALF_DOUBLE_SOURCE_POLICY_FAILURE_DIAGNOSIS.json",
            "HI2022_RA_HALF_DOUBLE_REPAIR_ATTEMPT_CERTIFICATE.json",
                "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.json",
            "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json",
            "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json",
            "B4_SOURCE_POLICY_COMMAND_PREFLIGHT_FREEZE_20260620.json",
            "B4_SOURCE_POLICY_EXPECTED_OUTPUT_SCHEMA_AUDIT_20260620.json",
            "B4_EXPECTED_OUTPUT_PROMOTION_READINESS_BLOCKER_AUDIT_20260620.json",
            "OC6_SOURCE_EQUIVALENT_REOPEN_READINESS_AUDIT_20260620.json",
            "VP2024_PUBLIC_CODE_RECHECK_20260613.json",
            "TFE_PUBLIC_CODE_RECHECK_20260613.json",
            "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.json",
            "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.json",
            "SOURCE_POLICY_REOPEN_CONDITION_MONITOR_20260620.json",
            "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json",
            "TFE_SOURCE_PENDULUM_MODEL_AUDIT.json",
            "TFE_DAE_RUNNER_CONTRACT_GAP_AUDIT.json",
            "TFE_RUNNER_CONTRACT_PREFLIGHT_CERTIFICATE.json",
            "TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.json",
            "TFE_BROWN_MCPHEE_SOURCE_LAW_BOUNDARY_AUDIT.json",
            "TFE_BROWN_MCPHEE_SOURCE_CODE_EQUIVALENCE_CERTIFICATE.json",
            "TFE_FULL_T10_ABSOLUTE_DAE_LIFT_SUMMARY.json",
            "TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.json",
            "TFE_FULL_T10_ENDPOINT_POLICY_CLOSURE_CERTIFICATE.json",
            "TFE_ENDPOINT_POLICY_SENSITIVITY_AUDIT.json",
            "OBJECTIVE_COMPLETION_AUDIT.json",
            "PROOF_CLOSURE_MANIFEST.json",
            "CMAME_MINIMAL_REPRODUCIBILITY_CANDIDATE_MANIFEST.json",
            "CMAME_RUNNER_ADAPTER_CANDIDATE_MANIFEST.json",
            "CMAME_RUNNER_CENTERED_REPRODUCIBILITY_AUDIT.json",
            "CMAME_P1_LOCAL_RUNNER_EXTRACTION_AUDIT.json",
            "B6_FOUR_EXAMPLE_LOCAL_EVIDENCE_SUMMARY.json",
            "B6_CLOSED_LOOP_SELF_CONTAINED_EXTRACTION_AUDIT.json",
            "CMAME_CLOSED_LOOP_LOCAL_RUNNER_CANDIDATE_MANIFEST.json",
            "CMAME_LOCAL_ACCEPTED_RUNNER_COMPANION_MANIFEST.json",
            "CMAME_NARROWED_REPRODUCIBILITY_PACKAGE_AUDIT.json",
            "CMAME_NARROWED_REPRO_CODE_ARCHIVE_MANIFEST.json",
            "CMAME_SELF_CONTAINED_RUNNER_EXTRACTION_PLAN.json",
            "cmame_p1_single_runner_candidate/results/single_pendulum_summary.json",
            "cmame_p1_double_runner_candidate/results/double_pendulum_summary.json",
            "cmame_closed_loop_local_runner_candidate/results/closed_loop_local_summary.json",
        ],
        "summary": summary,
        "blocker_required_to_close_by_id": objective_blocker_required_to_close_by_id,
        "blocker_safe_next_actions_by_id": objective_blocker_safe_next_actions_by_id,
        "blocker_opt_in_required_actions_by_id": objective_blocker_opt_in_required_actions_by_id,
        "objective_blocker_required_to_close_by_id": objective_blocker_required_to_close_by_id,
        "objective_blocker_safe_next_actions_by_id": objective_blocker_safe_next_actions_by_id,
        "objective_blocker_opt_in_required_actions_by_id": objective_blocker_opt_in_required_actions_by_id,
        "current_code_inventory": {
            "paper_python_file_count": code_checks.get("paper_python_file_count"),
            "paper_python_line_count": code_checks.get("paper_python_line_count"),
            "v048_python_file_count": code_checks.get("v048_python_file_count"),
            "v048_python_line_count": code_checks.get("v048_python_line_count"),
            "combined_python_line_count": code_checks.get("combined_python_line_count"),
            "paper_python_prefix_counts": code_checks.get("paper_python_prefix_counts"),
            "v048_python_prefix_counts": code_checks.get("v048_python_prefix_counts"),
        },
        "package_layers": package_layers,
        "candidate_minimal_file_set": files,
        "minimal_reproducibility_candidate": {
            "schema": minimal_candidate.get("schema"),
            "status": minimal_candidate.get("status"),
            "submission_ready": minimal_candidate.get("submission_ready"),
            "candidate_file_count": minimal_candidate.get("candidate_file_count"),
            "candidate_python_file_count": minimal_candidate.get("candidate_python_file_count"),
            "candidate_python_line_count": minimal_candidate.get("candidate_python_line_count"),
            "source_policy_closed_rows": minimal_candidate.get("source_policy_closed_rows"),
            "source_policy_total_rows": minimal_candidate.get("source_policy_total_rows"),
            "direct_pc2_proof_gap_closed": minimal_candidate.get(
                "direct_pc2_proof_gap_closed", minimal_candidate.get("proof_gap_closed")
            ),
            "proof_gap_closed": minimal_candidate.get("proof_gap_closed"),
            "proof_gap_closed_scope": minimal_candidate.get("proof_gap_closed_scope", DIRECT_PC2_SCOPE),
            "proof_gap_closed_reading_rule": minimal_candidate.get(
                "proof_gap_closed_reading_rule", DIRECT_PC2_READING_RULE
            ),
            "read_only_replay_package": minimal_candidate.get("read_only_replay_package"),
        },
        "local_accepted_runner_companion": {
            "schema": local_runner_companion.get("schema"),
            "status": local_runner_companion.get("status"),
            "submission_ready": local_runner_companion.get("submission_ready"),
            "launcher_passed": local_runner_companion.get("launcher_passed"),
            "minimal_replay_boundary_preserved": local_runner_companion.get("minimal_replay_boundary_preserved"),
            "copies_runner_source": local_runner_companion.get("copies_runner_source"),
            "uses_existing_self_contained_runner_candidates": local_runner_companion.get(
                "uses_existing_self_contained_runner_candidates"
            ),
            "local_accepted_rows_runner_available": local_runner_companion.get(
                "local_accepted_rows_runner_available"
            ),
            "full_source_policy_runner_package_ready": local_runner_companion.get(
                "full_source_policy_runner_package_ready"
            ),
            "source_policy_closed_rows": local_runner_companion.get("source_policy_closed_rows"),
            "source_policy_total_rows": local_runner_companion.get("source_policy_total_rows"),
            "local_rows": local_runner_companion.get("local_rows"),
            "self_contained_examples": local_runner_companion.get("self_contained_examples"),
            "replay_only_examples": local_runner_companion.get("replay_only_examples"),
            "candidate_python_file_count": local_runner_companion.get("candidate_python_file_count"),
            "candidate_python_line_count": local_runner_companion.get("candidate_python_line_count"),
            "runner_commands": local_runner_companion.get("runner_commands"),
        },
        "narrowed_reproducibility_package_audit": {
            "schema": narrowed_repro_audit.get("schema"),
            "status": narrowed_repro_audit.get("status"),
            "submission_ready": narrowed_repro_audit.get("submission_ready"),
            "submission_standard_scope": narrowed_repro_audit.get("submission_standard_scope"),
            "global_submission_standard_met": narrowed_repro_audit.get("global_submission_standard_met"),
            "narrowed_claim_submission_standard_met": narrowed_repro_audit.get(
                "narrowed_claim_submission_standard_met"
            ),
            "narrowed_claim_decision": narrowed_repro_audit.get("narrowed_claim_decision"),
            "narrowed_claim_reproducibility_package_ready": narrowed_repro_audit.get(
                "narrowed_claim_reproducibility_package_ready"
            ),
            "full_source_policy_runner_package_ready": narrowed_repro_audit.get(
                "full_source_policy_runner_package_ready"
            ),
            "source_policy_rows_closed": narrowed_repro_audit.get("source_policy_rows_closed"),
            "source_policy_rows_total": narrowed_repro_audit.get("source_policy_rows_total"),
            "package_boundary": narrowed_repro_audit.get("package_boundary"),
            "human_runnable_local_evidence": narrowed_repro_audit.get("human_runnable_local_evidence"),
            "p1_runner_candidates": narrowed_repro_audit.get("p1_runner_candidates"),
            "closed_loop_runner_candidate": narrowed_repro_audit.get("closed_loop_runner_candidate"),
        },
        "narrowed_repro_code_archive": {
            "schema": narrowed_repro_code_archive.get("schema"),
            "status": narrowed_repro_code_archive.get("status"),
            "archive": narrowed_repro_code_archive.get("archive"),
            "archive_bytes": narrowed_repro_code_archive.get("archive_bytes"),
            "archive_sha256": narrowed_repro_code_archive.get("archive_sha256"),
            "entrypoint": narrowed_repro_code_archive.get("entrypoint"),
            "scope": narrowed_repro_code_archive.get("scope"),
            "entry_count": narrowed_repro_code_archive.get("entry_count"),
            "python_file_count": narrowed_repro_code_archive.get("python_file_count"),
            "python_line_count": narrowed_repro_code_archive.get("python_line_count"),
            "narrowed_claim_reproducibility_package_ready": narrowed_repro_code_archive.get(
                "narrowed_claim_reproducibility_package_ready"
            ),
            "source_policy_rows_closed": narrowed_repro_code_archive.get("source_policy_rows_closed"),
            "source_policy_rows_total": narrowed_repro_code_archive.get("source_policy_rows_total"),
            "source_policy_execution_handoff": narrowed_repro_code_archive.get(
                "source_policy_execution_handoff"
            ),
            "full_source_policy_runner_package_ready": narrowed_repro_code_archive.get(
                "full_source_policy_runner_package_ready"
            ),
            "submission_ready": narrowed_repro_code_archive.get("submission_ready"),
            "narrowed_archive_boundary": narrowed_repro_code_archive.get(
                "narrowed_archive_boundary"
            ),
        },
        "reviewer_facing_code_policy": {
            "primary_submission_package_required": True,
            "research_audit_tree_primary_submission_allowed": code_checks.get(
                "research_audit_repo_primary_submission_allowed"
            ),
            "research_audit_tree_provenance_only": code_checks.get("research_audit_repo_provenance_only"),
            "research_audit_tree_too_large_for_primary_submission": code_checks.get(
                "research_audit_repo_too_large_for_primary_submission"
            ),
            "research_audit_tree_line_limit": code_checks.get("research_audit_primary_submission_line_limit"),
            "reviewer_facing_python_file_limit": code_checks.get("reviewer_facing_python_file_limit"),
            "reviewer_facing_python_line_limit": code_checks.get("reviewer_facing_python_line_limit"),
            "candidate_code_size_ok": code_checks.get("minimal_reproducibility_candidate_code_size_ok"),
            "candidate_runner_centered": code_checks.get("minimal_reproducibility_candidate_runner_centered"),
            "candidate_replay_only": code_checks.get("minimal_reproducibility_candidate_replay_only"),
            "candidate_source_policy_ready": code_checks.get("minimal_reproducibility_candidate_source_policy_ready"),
            "candidate_proof_ready": code_checks.get("minimal_reproducibility_candidate_proof_ready"),
            "minimal_reproducible_submission_code_ready": code_checks.get(
                "minimal_reproducible_submission_code_ready"
            ),
            "code_bloat_risk_for_submission": code_checks.get("code_bloat_risk_for_submission"),
            "minimal_submission_code_dependency_boundary": minimal_submission_code_dependency_boundary,
        },
        "minimal_submission_code_dependency_boundary": minimal_submission_code_dependency_boundary,
        "strict_proof_writing_submission_boundary": strict_proof_writing_submission_boundary,
        "runner_adapter_candidate": {
            "schema": runner_adapter.get("schema"),
            "status": runner_adapter.get("status"),
            "submission_ready": runner_adapter.get("submission_ready"),
            "runner_adapter_present": runner_adapter.get("runner_adapter_present"),
            "self_contained_simulation_runner": runner_adapter.get("self_contained_simulation_runner"),
            "external_v048_required_for_report_generation": runner_adapter.get(
                "external_v048_required_for_report_generation"
            ),
            "candidate_python_file_count": runner_adapter.get("candidate_python_file_count"),
            "candidate_python_line_count": runner_adapter.get("candidate_python_line_count"),
            "closed_loop_local_rows_replay_present": runner_adapter.get("closed_loop_local_rows_replay_present"),
            "closed_loop_local_rows_summary_present": runner_adapter.get("closed_loop_local_rows_summary_present"),
            "closed_loop_local_rows": runner_adapter.get("closed_loop_local_rows"),
            "closed_loop_local_models": closed_loop_local_models,
            "source_policy_closed_rows": runner_adapter.get("source_policy_closed_rows"),
            "source_policy_total_rows": runner_adapter.get("source_policy_total_rows"),
        },
        "runner_centered_reproducibility_audit": {
            "schema": runner_centered_audit.get("schema"),
            "status": runner_centered_audit.get("status"),
            "runner_centered_package_ready": runner_centered_audit.get("runner_centered_package_ready"),
            "local_runner_centered_candidate_ready": runner_centered_audit.get(
                "local_runner_centered_candidate_ready"
            ),
            "full_source_policy_runner_package_ready": runner_centered_audit.get(
                "full_source_policy_runner_package_ready"
            ),
            "runner_package_boundary": runner_centered_audit.get("runner_package_boundary"),
            "candidate": runner_centered_audit.get("current_candidate"),
            "source_policy_scope": runner_centered_audit.get("source_policy_scope"),
            "existing_runner_source_total_python_lines": runner_centered_audit.get(
                "existing_runner_source_total_python_lines"
            ),
            "existing_runner_boundary": runner_centered_audit.get("existing_runner_boundary"),
            "requirements": runner_centered_audit.get("requirements"),
            "b6_four_example_local_evidence": runner_centered_audit.get("b6_four_example_local_evidence"),
            "b6_closed_loop_self_contained_extraction_audit": runner_centered_audit.get(
                "b6_closed_loop_self_contained_extraction_audit"
            ),
        },
        "self_contained_runner_extraction_plan": {
            "schema": extraction_plan.get("schema"),
            "status": extraction_plan.get("status"),
            "self_contained_runner_ready": extraction_plan.get("self_contained_runner_ready"),
            "local_accepted_rows_self_contained_runner_ready": extraction_plan.get(
                "local_accepted_rows_self_contained_runner_ready"
            ),
            "full_source_policy_self_contained_runner_ready": extraction_plan.get(
                "full_source_policy_self_contained_runner_ready"
            ),
            "b6_final_prose_pass_ready": extraction_plan.get("b6_final_prose_pass_ready"),
            "b6_final_prose_pass_scope": extraction_plan.get("b6_final_prose_pass_scope"),
            "full_source_policy_b6_prose_ready": extraction_plan.get("full_source_policy_b6_prose_ready"),
            "b6_closure_preflight_status": extraction_plan.get("b6_closure_preflight_status"),
            "b6_closure_allowed_now": extraction_plan.get("b6_closure_allowed_now"),
            "runner_package_boundary": extraction_plan.get("runner_package_boundary"),
            "target_symbol_count": extraction_plan.get("target_symbol_count"),
            "target_symbol_lines": extraction_plan.get("target_symbol_lines"),
            "phases": extraction_plan.get("phases"),
            "p1_single_runner_candidate_ready": extraction_plan.get("p1_local_runner_extraction_audit", {}).get(
                "p1_single_runner_candidate_ready"
            ),
            "p1_double_runner_candidate_ready": extraction_plan.get("p1_local_runner_extraction_audit", {}).get(
                "p1_double_runner_candidate_ready"
            ),
            "p1_regenerated_candidate_rows": extraction_plan.get("p1_local_runner_extraction_audit", {}).get(
                "p1_regenerated_candidate_rows"
            ),
            "p1_required_rows": extraction_plan.get("p1_local_runner_extraction_audit", {}).get("p1_required_rows"),
            "acceptance_criteria": extraction_plan.get("acceptance_criteria"),
            "next_concrete_step": extraction_plan.get("next_concrete_step"),
            "b6_four_example_local_evidence": extraction_plan.get("b6_four_example_local_evidence"),
            "b6_closed_loop_self_contained_extraction_audit": extraction_plan.get(
                "b6_closed_loop_self_contained_extraction_audit"
            ),
        },
        "b6_closed_loop_self_contained_extraction_audit": {
            "schema": closed_loop_audit.get("schema"),
            "status": closed_loop_audit.get("status"),
            "self_contained_runner_ready": closed_loop_audit.get("self_contained_runner_ready"),
            "target_source_file_count": closed_loop_audit.get("target_source_file_count"),
            "target_source_file_lines": closed_loop_audit.get("target_source_file_lines"),
            "target_symbol_count": closed_loop_audit.get("target_symbol_count"),
            "target_symbol_lines": closed_loop_audit.get("target_symbol_lines"),
            "replay_only_closed_loop_examples": closed_loop_audit.get("replay_only_closed_loop_examples"),
            "closed_loop_local_replay_rows": closed_loop_audit.get("closed_loop_local_replay_rows"),
            "run_v047_invoked": closed_loop_audit.get("run_v047_invoked"),
            "run_v048_invoked": closed_loop_audit.get("run_v048_invoked"),
            "b4_opt_in_required_for_this_audit": closed_loop_audit.get("b4_opt_in_required_for_this_audit"),
            "next_concrete_step": closed_loop_audit.get("next_concrete_step"),
        },
        "closed_loop_local_runner_candidate": {
            "schema": closed_loop_candidate.get("schema"),
            "status": closed_loop_candidate.get("status"),
            "runner_passed": closed_loop_candidate.get("runner_passed"),
            "self_contained_simulation_runner": closed_loop_candidate.get("self_contained_simulation_runner"),
            "candidate_python_file_count": closed_loop_candidate.get("candidate_python_file_count"),
            "candidate_python_line_count": closed_loop_candidate.get("candidate_python_line_count"),
            "candidate_python_line_limit_ok": closed_loop_candidate.get("candidate_python_line_limit_ok"),
            "imports_v046_v047_v048_or_v029": closed_loop_candidate.get("imports_v046_v047_v048_or_v029"),
            "closed_loop_local_rows": closed_loop_candidate.get("closed_loop_local_rows"),
            "closed_loop_models": closed_loop_candidate.get("closed_loop_models"),
            "source_policy_external_rows_closed": closed_loop_candidate.get("source_policy_external_rows_closed"),
            "source_policy_external_rows_total": closed_loop_candidate.get("source_policy_external_rows_total"),
            "source_policy_external_superiority_allowed": closed_loop_candidate.get(
                "source_policy_external_superiority_allowed"
            ),
            "submission_ready": closed_loop_candidate.get("submission_ready"),
            "next_concrete_step": closed_loop_candidate.get("next_concrete_step"),
        },
        "b6_four_example_local_evidence": {
            "schema": b6_local_evidence.get("schema"),
            "status": b6_local_evidence.get("status"),
            "runner_passed": b6_local_evidence.get("b6_local_evidence_runner_passed"),
            "local_rows": b6_local_evidence.get("local_rows"),
            "self_contained_examples": b6_local_evidence.get("self_contained_examples"),
            "replay_only_examples": b6_local_evidence.get("replay_only_examples"),
            "four_example_local_evidence_available": b6_local_evidence.get(
                "human_runnable_four_example_local_evidence_available"
            ),
            "four_example_self_contained_simulation_ready": b6_local_evidence.get(
                "human_runnable_four_example_self_contained_simulation_ready"
            ),
            "source_policy_external_rows_closed": b6_local_evidence.get("source_policy_external_rows_closed"),
            "source_policy_external_rows_total": b6_local_evidence.get("source_policy_external_rows_total"),
            "global_proof_gap_closed": b6_local_evidence.get("global_proof_gap_closed"),
            "direct_pc2_proof_gap_closed": b6_local_evidence.get(
                "direct_residual_bridge_proof_gap_closed", b6_local_evidence.get("global_proof_gap_closed")
            ),
            "legacy_global_proof_gap_closed_key_scope": (
                "direct_residual_bridge_pc2_closure_only_not_global_submission_readiness"
            ),
            "submission_ready": b6_local_evidence.get("submission_ready"),
        },
        "p1_local_runner_extraction_audit": {
            "schema": p1_local_runner_audit.get("schema"),
            "status": p1_local_runner_audit.get("status"),
            "p1_local_single_double_ready": p1_local_runner_audit.get("p1_local_single_double_ready"),
            "self_contained_runner_ready": p1_local_runner_audit.get("self_contained_runner_ready"),
            "p1_single_runner_candidate_ready": p1_local_runner_audit.get("p1_single_runner_candidate_ready"),
            "p1_double_runner_candidate_ready": p1_local_runner_audit.get("p1_double_runner_candidate_ready"),
            "p1_regenerated_candidate_rows": p1_local_runner_audit.get("p1_regenerated_candidate_rows"),
            "p1_required_rows": p1_local_runner_audit.get("p1_required_rows"),
            "p1_missing_candidate_rows": p1_local_runner_audit.get("p1_missing_candidate_rows"),
            "p1_single_runner_candidate": p1_local_runner_audit.get("p1_single_runner_candidate"),
            "p1_double_runner_candidate": p1_local_runner_audit.get("p1_double_runner_candidate"),
            "v047_source_python_lines": p1_local_runner_audit.get("v047_source_python_lines"),
            "v047_primary_recursive_internal_dependency_count": p1_local_runner_audit.get(
                "v047_primary_recursive_internal_dependency_count"
            ),
            "v047_primary_recursive_internal_dependency_lines": p1_local_runner_audit.get(
                "v047_primary_recursive_internal_dependency_lines"
            ),
            "open_blockers": p1_local_runner_audit.get("open_blockers"),
            "acceptance_criteria": p1_local_runner_audit.get("acceptance_criteria"),
            "next_extraction_actions": p1_local_runner_audit.get("next_extraction_actions"),
        },
        "missing_components": missing_components,
        "external_runner_status": {
            "b2_status": b2.get("status"),
            "active_flagged_rows": b2.get("active_flagged_row_count"),
            "demoted_flagged_rows": b2.get("demoted_flagged_row_count"),
            "source_policy_closed_rows": b2.get("source_policy_closed_rows"),
            "b4_work_precision_plan_status": b4_plan.get("status"),
            "b4_work_precision_plan_b4_can_close_now": b4_plan.get("b4_can_close_now"),
            "b4_work_precision_plan_b7_can_close_now": b4_plan.get("b7_can_close_now"),
            "b4_work_precision_plan_ready_lane_count": b4_plan.get("execution_lane_summary", {}).get(
                "ready_to_launch_after_explicit_opt_in_count"
            ),
            "b4_work_precision_plan_not_ready_lane_count": b4_plan.get("execution_lane_summary", {}).get(
                "not_ready_lane_count"
            ),
            "b4_work_precision_plan_source_policy_rows_closed": b4_plan.get("execution_lane_summary", {}).get(
                "source_policy_rows_closed_after_plan"
            ),
            "b4_work_precision_plan_source_policy_rows_total": b4_plan.get("execution_lane_summary", {}).get(
                "source_policy_rows_total"
            ),
            "b4_existing_promotion_audit_status": b4_existing_promotion_audit.get("status"),
            "b4_existing_promotion_candidate_items": b4_existing_promotion_audit.get("candidate_item_count"),
            "b4_existing_promotion_ready_without_new_execution": b4_existing_promotion_audit.get(
                "promotion_ready_without_new_execution_count"
            ),
            "b4_existing_promotion_source_policy_rows_closed": b4_existing_promotion_audit.get(
                "source_policy_rows_closed_by_existing_artifacts"
            ),
            "b4_existing_promotion_source_policy_rows_total": b4_existing_promotion_audit.get(
                "source_policy_rows_total"
            ),
            "b4_existing_promotion_b4_closing_items": b4_existing_promotion_audit.get("b4_closing_item_count"),
            "b4_existing_promotion_b7_closing_items": b4_existing_promotion_audit.get("b7_closing_item_count"),
            "b4_post_execution_audit_status": b4_post_execution_audit.get("status"),
            "b4_post_execution_audit_approved_driver_execution_recorded": b4_post_execution_audit.get(
                "approved_driver_execution_recorded"
            ),
            "b4_post_execution_audit_verified_authorized_execution_recorded": b4_post_execution_audit.get(
                "verified_authorized_execution_recorded"
            ),
            "b4_post_execution_audit_existing_ready_command_artifacts_present": b4_post_execution_audit.get(
                "existing_ready_command_artifacts_present"
            ),
            "b4_post_execution_audit_execution_record_scope": b4_post_execution_audit.get(
                "execution_record_scope"
            ),
            "b4_post_execution_audit_ready_command_count": b4_post_execution_audit.get(
                "guarded_driver", {}
            ).get("ready_command_count"),
            "b4_post_execution_audit_mapped_external_rows": b4_post_execution_audit.get(
                "guarded_driver", {}
            ).get("ready_command_mapped_external_rows"),
            "b4_post_execution_audit_unaddressed_external_rows": b4_post_execution_audit.get(
                "guarded_driver", {}
            ).get("unaddressed_external_rows_after_ready_commands"),
            "b4_post_execution_audit_expected_outputs_present": b4_post_execution_audit.get(
                "command_artifact_presence", {}
            ).get("all_expected_outputs_exist_now"),
            "b4_post_execution_audit_source_policy_rows_closed": b4_post_execution_audit.get(
                "row_status_after_driver", {}
            ).get("source_policy_rows_closed"),
            "b4_post_execution_audit_source_policy_rows_total": b4_post_execution_audit.get(
                "row_status_after_driver", {}
            ).get("source_policy_rows_total"),
            "b4_post_execution_audit_b4_can_close_now": b4_post_execution_audit.get(
                "row_status_after_driver", {}
            ).get("b4_can_close_now"),
            "b4_post_execution_audit_b7_can_close_now": b4_post_execution_audit.get(
                "row_status_after_driver", {}
            ).get("b7_can_close_now"),
            "full_source_policy_row_provenance_status": full_source_policy_row_provenance_audit.get("status"),
            "full_source_policy_row_provenance_action_boundary": full_source_policy_row_provenance_audit.get(
                "action_boundary"
            ),
            "full_source_policy_row_provenance_source_policy_execution_invoked": (
                full_source_policy_row_provenance_audit.get("source_policy_execution_invoked")
            ),
            "full_source_policy_row_provenance_rows": full_source_policy_row_provenance_audit.get("row_count"),
            "full_source_policy_row_provenance_preflight_complete_rows": full_source_policy_row_provenance_audit.get(
                "provenance_preflight_complete_rows"
            ),
            "full_source_policy_row_provenance_public_source_root_rows": full_source_policy_row_provenance_audit.get(
                "public_source_root_rows"
            ),
            "full_source_policy_row_provenance_unable_to_reproduce_rows": full_source_policy_row_provenance_audit.get(
                "source_policy_rows_unable_to_reproduce"
            ),
            "full_source_policy_row_provenance_promotion_ready_rows": full_source_policy_row_provenance_audit.get(
                "promotion_ready_rows"
            ),
            "full_source_policy_row_provenance_source_policy_closed_rows": full_source_policy_row_provenance_audit.get(
                "source_policy_rows_closed"
            ),
            "full_source_policy_row_provenance_handoff_status": full_source_policy_row_provenance_audit.get(
                "source_policy_execution_handoff", {}
            ).get("status"),
            "full_source_policy_row_provenance_handoff_authorized": full_source_policy_row_provenance_audit.get(
                "source_policy_execution_handoff", {}
            ).get("execution_authorized"),
            "full_source_policy_row_provenance_handoff_commands_not_run": full_source_policy_row_provenance_audit.get(
                "source_policy_execution_handoff", {}
            ).get("commands_not_run_by_handoff"),
            "full_source_policy_row_provenance_handoff_driver": full_source_policy_row_provenance_audit.get(
                "source_policy_execution_handoff", {}
            ).get("guarded_execution_driver"),
            "full_source_policy_row_provenance_handoff_driver_requires_exact": full_source_policy_row_provenance_audit.get(
                "source_policy_execution_handoff", {}
            ).get("driver_requires_exact_approval"),
            "full_source_policy_row_provenance_handoff_driver_does_not_authorize": full_source_policy_row_provenance_audit.get(
                "source_policy_execution_handoff", {}
            ).get("driver_does_not_authorize_execution"),
            "full_source_policy_row_provenance_handoff_exact_approval": full_source_policy_row_provenance_audit.get(
                "source_policy_execution_handoff", {}
            ).get("exact_required_user_approval_statement"),
            "full_source_policy_row_provenance_handoff_opt_in_commands": full_source_policy_row_provenance_audit.get(
                "source_policy_execution_handoff", {}
            ).get("opt_in_required_command_count"),
            "full_source_policy_row_provenance_handoff_mapped_rows": full_source_policy_row_provenance_audit.get(
                "source_policy_execution_handoff", {}
            ).get("opt_in_required_mapped_external_rows"),
            "full_source_policy_row_provenance_handoff_terminal_unable_rows": full_source_policy_row_provenance_audit.get(
                "source_policy_execution_handoff", {}
            ).get("terminal_unable_to_reproduce_rows"),
            "ra_hi_source_policy_closeout_checklist_status": ra_hi_source_policy_closeout_checklist.get("status"),
            "ra_hi_source_policy_closeout_total_rows": ra_hi_source_policy_closeout_checklist.get("coverage", {}).get(
                "source_policy_rows_total"
            ),
            "ra_hi_source_policy_closeout_ra_rows": ra_hi_source_policy_closeout_checklist.get("coverage", {}).get(
                "ra2021_rows"
            ),
            "ra_hi_source_policy_closeout_hi_rows": ra_hi_source_policy_closeout_checklist.get("coverage", {}).get(
                "hi2022_rows"
            ),
            "ra_hi_source_policy_closeout_ready_commands": ra_hi_source_policy_closeout_checklist.get(
                "coverage", {}
            ).get("ready_command_count"),
            "ra_hi_source_policy_closeout_mapped_rows": ra_hi_source_policy_closeout_checklist.get(
                "coverage", {}
            ).get("ready_command_mapped_external_rows"),
            "ra_hi_source_policy_closeout_promoted_rows": ra_hi_source_policy_closeout_checklist.get(
                "coverage", {}
            ).get("source_policy_rows_promoted"),
            "ra_hi_source_policy_closeout_completed_rows": ra_hi_source_policy_closeout_checklist.get(
                "coverage", {}
            ).get("source_policy_rows_completed"),
            "ra_hi_source_policy_closeout_external_ready_rows": ra_hi_source_policy_closeout_checklist.get(
                "coverage", {}
            ).get("external_superiority_ready_rows"),
            "ra_hi_source_policy_closeout_opt_in_required": ra_hi_source_policy_closeout_checklist.get(
                "guarded_execution_boundary", {}
            ).get("explicit_user_opt_in_required_before_any_command"),
            "ra_hi_source_policy_closeout_execution_invoked": ra_hi_source_policy_closeout_checklist.get(
                "guarded_execution_boundary", {}
            ).get("execution_invoked_by_packet"),
            "ra_hi_source_policy_closeout_b4_can_close": ra_hi_source_policy_closeout_checklist.get(
                "not_promoted_disposition", {}
            ).get("b4_can_close_from_this_checklist"),
            "ra_hi_source_policy_closeout_b7_can_close": ra_hi_source_policy_closeout_checklist.get(
                "not_promoted_disposition", {}
            ).get("b7_can_close_from_this_checklist"),
            "ra_hi_source_policy_output_inventory_status": ra_hi_source_policy_output_inventory.get("status"),
            "ra_hi_source_policy_output_inventory_command_count": ra_hi_source_policy_output_inventory.get(
                "coverage", {}
            ).get("command_count"),
            "ra_hi_source_policy_output_inventory_outputs_existing": ra_hi_source_policy_output_inventory.get(
                "coverage", {}
            ).get("expected_output_existing_count"),
            "ra_hi_source_policy_output_inventory_summaries_existing": ra_hi_source_policy_output_inventory.get(
                "coverage", {}
            ).get("expected_summary_existing_count"),
            "ra_hi_source_policy_output_inventory_csv_data_rows": ra_hi_source_policy_output_inventory.get(
                "coverage", {}
            ).get("expected_output_csv_data_rows"),
            "ra_hi_source_policy_output_inventory_hi_ok_rows": ra_hi_source_policy_output_inventory.get(
                "coverage", {}
            ).get("hi2022_summary_ok_rows"),
            "ra_hi_source_policy_output_inventory_closed_rows": ra_hi_source_policy_output_inventory.get(
                "coverage", {}
            ).get("source_policy_rows_closed_by_inventory"),
            "ra_hi_source_policy_promotion_blocker_matrix_status": ra_hi_source_policy_promotion_blocker_matrix.get(
                "status"
            ),
            "ra_hi_source_policy_promotion_blocker_matrix_rows": ra_hi_source_policy_promotion_blocker_matrix.get(
                "row_count"
            ),
            "ra_hi_source_policy_promotion_blocker_matrix_ra_rows": ra_hi_source_policy_promotion_blocker_matrix.get(
                "ra2021_row_count"
            ),
            "ra_hi_source_policy_promotion_blocker_matrix_hi_rows": ra_hi_source_policy_promotion_blocker_matrix.get(
                "hi2022_row_count"
            ),
            "ra_hi_source_policy_promotion_blocker_matrix_public_root_rows": ra_hi_source_policy_promotion_blocker_matrix.get(
                "public_source_root_available_rows"
            ),
            "ra_hi_source_policy_promotion_blocker_matrix_no_public_code_rows": ra_hi_source_policy_promotion_blocker_matrix.get(
                "no_public_code_rows_included"
            ),
            "ra_hi_source_policy_promotion_blocker_matrix_closed_rows": ra_hi_source_policy_promotion_blocker_matrix.get(
                "source_policy_rows_closed"
            ),
            "ra_hi_source_policy_promotion_blocker_matrix_not_promoted_rows": ra_hi_source_policy_promotion_blocker_matrix.get(
                "source_policy_rows_not_promoted"
            ),
            "ra_hi_source_policy_promotion_blocker_matrix_attempted_not_reproducible_rows": ra_hi_source_policy_promotion_blocker_matrix.get(
                "attempted_not_reproducible_rows"
            ),
            "ra_hi_source_policy_promotion_blocker_matrix_command_mapped_rows": ra_hi_source_policy_promotion_blocker_matrix.get(
                "command_mapped_rows"
            ),
            "ra_hi_source_policy_promotion_blocker_matrix_output_present_rows": ra_hi_source_policy_promotion_blocker_matrix.get(
                "rows_with_all_command_outputs_present"
            ),
            "ra2021_double_low_order_diagnosis_status": ra2021_double_low_order.get("status"),
            "ra2021_double_low_order_fine_pair_floor_limited": ra2021_double_low_order.get(
                "diagnosis", {}
            ).get("fine_pair_floor_limited"),
            "ra2021_double_low_order_rows_promoted": ra2021_double_low_order.get(
                "promotion_decision", {}
            ).get("source_policy_rows_promoted_by_this_diagnosis"),
            "hi2022_ra_half_double_failure_diagnosis_status": hi2022_ra_half_double_failure.get("status"),
            "hi2022_ra_half_double_failure_rows_ok": hi2022_ra_half_double_failure.get(
                "execution_evidence", {}
            ).get("ok_row_count"),
            "hi2022_ra_half_double_failure_rows_failed": hi2022_ra_half_double_failure.get(
                "execution_evidence", {}
            ).get("failed_row_count"),
            "hi2022_ra_half_double_failure_rows_total": hi2022_ra_half_double_failure.get(
                "execution_evidence", {}
            ).get("row_count"),
            "hi2022_ra_half_double_failure_newton_failure_count": hi2022_ra_half_double_failure.get(
                "diagnosis", {}
            ).get("newton_failure_count"),
            "hi2022_ra_half_double_failure_pair_orders_available": hi2022_ra_half_double_failure.get(
                "diagnosis", {}
            ).get("pair_orders_available"),
            "hi2022_ra_half_double_failure_rows_promoted": hi2022_ra_half_double_failure.get(
                "promotion_decision", {}
            ).get("source_policy_rows_promoted_by_this_diagnosis"),
            "hi2022_ra_half_double_repair_attempt_status": hi2022_ra_half_double_repair.get("status"),
            "hi2022_ra_half_double_repair_target_ok_rows": hi2022_ra_half_double_repair.get(
                "tolerance_repair_evidence", {}
            ).get("combined_target_group", {}).get("ok_row_count"),
            "hi2022_ra_half_double_repair_target_failed_rows": hi2022_ra_half_double_repair.get(
                "tolerance_repair_evidence", {}
            ).get("combined_target_group", {}).get("failed_row_count"),
            "hi2022_ra_half_double_repair_combined_ok_rows": hi2022_ra_half_double_repair.get(
                "tolerance_repair_evidence", {}
            ).get("combined_best_ok_rows"),
            "hi2022_ra_half_double_repair_combined_row_count": hi2022_ra_half_double_repair.get(
                "tolerance_repair_evidence", {}
            ).get("combined_best_row_count"),
            "hi2022_ra_half_double_repair_combined_complete_groups": hi2022_ra_half_double_repair.get(
                "tolerance_repair_evidence", {}
            ).get("combined_best_complete_groups"),
            "hi2022_ra_half_double_repair_combined_group_count": hi2022_ra_half_double_repair.get(
                "tolerance_repair_evidence", {}
            ).get("combined_best_group_count"),
            "hi2022_ra_half_double_repair_rows_promoted": hi2022_ra_half_double_repair.get(
                "source_policy_rows_promoted"
            ),
            "b4_row_readiness_ledger_status": b4_row_readiness_ledger.get("status"),
            "b4_row_readiness_external_rows": b4_row_readiness_ledger.get("row_count"),
            "b4_row_readiness_expected_external_rows": b4_row_readiness_ledger.get("expected_external_row_count"),
            "b4_row_readiness_source_policy_rows_closed": b4_row_readiness_ledger.get(
                "source_policy_rows_closed"
            ),
            "b4_row_readiness_source_policy_rows_open": b4_row_readiness_ledger.get("source_policy_rows_open"),
            "b4_row_readiness_rows_with_launch_command_refs": b4_row_readiness_ledger.get(
                "rows_with_launch_command_refs"
            ),
            "b4_row_readiness_rows_without_launch_command_refs": b4_row_readiness_ledger.get(
                "rows_without_launch_command_refs"
            ),
            "b4_row_readiness_ready_suites": b4_row_readiness_ledger.get("ready_suite_count"),
            "b4_row_readiness_not_ready_suites": b4_row_readiness_ledger.get("not_ready_suite_count"),
            "b4_execution_opt_in_packet_status": b4_execution_opt_in_packet.get("status"),
            "b4_execution_opt_in_ready_command_count": b4_execution_opt_in_packet.get("ready_command_count"),
            "b4_execution_opt_in_mapped_external_rows": b4_execution_opt_in_packet.get(
                "ready_command_mapped_external_rows"
            ),
            "b4_execution_opt_in_unaddressed_external_rows": b4_execution_opt_in_packet.get(
                "unaddressed_external_rows_after_ready_commands"
            ),
            "b4_execution_opt_in_source_policy_rows_closed_now": b4_execution_opt_in_packet.get(
                "source_policy_rows_closed_now"
            ),
            "b4_execution_opt_in_source_policy_rows_total": b4_execution_opt_in_packet.get(
                "source_policy_rows_total"
            ),
            "b4_execution_opt_in_explicit_user_opt_in_required": b4_execution_opt_in_packet.get(
                "explicit_user_opt_in_required_before_any_command"
            ),
            "b4_post_execution_promotion_contract_schema": b4_promotion_contract.get("schema"),
            "b4_post_execution_promotion_contract_status": b4_promotion_contract.get("status"),
            "b4_post_execution_promotion_contract_rows_closed": b4_promotion_contract.get(
                "source_policy_rows_closed_now"
            ),
            "b4_post_execution_promotion_contract_rows_total": b4_promotion_contract.get(
                "source_policy_rows_total"
            ),
            "b4_post_execution_promotion_contract_ready_mapped_rows": b4_promotion_contract.get(
                "ready_command_mapped_external_rows"
            ),
            "b4_post_execution_promotion_contract_unaddressed_rows": b4_promotion_contract.get(
                "unaddressed_external_rows_after_ready_commands"
            ),
            "b4_post_execution_promotion_contract_checks_satisfied_now": b4_promotion_contract.get(
                "all_required_checks_satisfied_now"
            ),
            "b4_post_execution_promotion_contract_b4_can_close_now": b4_promotion_contract.get(
                "b4_can_close_after_promotion_contract_now"
            ),
            "b4_post_execution_promotion_contract_b7_can_close_now": b4_promotion_contract.get(
                "b7_can_close_after_promotion_contract_now"
            ),
            "remaining_requirements": b2.get("b2_remaining_requirements"),
            "ra2021_public_baselines_present": code_checks.get("ra2021_public_baselines_present"),
            "hi2022_bounded_rows_present": code_checks.get("hi2022_bounded_rows_present"),
            "tfe_source_pendulum_parameter_model_implemented": tfe_model.get(
                "source_pendulum_parameter_model_implemented"
            ),
            "tfe_source_pendulum_frictionless_smoke_implemented": tfe_model.get(
                "frictionless_planar_rhs_smoke_implemented"
            ),
            "tfe_source_pendulum_absolute_coordinate_dae_residual_smoke_implemented": tfe_model.get(
                "absolute_coordinate_dae_residual_smoke_implemented"
            ),
            "tfe_source_pendulum_absolute_coordinate_frictional_candidate_dae_smoke_implemented": tfe_model.get(
                "absolute_coordinate_frictional_candidate_dae_smoke_implemented"
            ),
            "tfe_source_pendulum_source_policy_dae_runner_equivalent": tfe_model.get(
                "source_policy_dae_runner_equivalent"
            ),
            "tfe_source_pendulum_source_output_time_integration_smoke_implemented": tfe_model.get(
                "source_output_time_integration_smoke_implemented"
            ),
            "tfe_source_pendulum_source_policy_time_integration_runner_equivalent": tfe_model.get(
                "source_policy_time_integration_runner_equivalent"
            ),
            "tfe_source_pendulum_source_reference_solution_policy_smoke_implemented": tfe_model.get(
                "source_reference_solution_policy_smoke_implemented"
            ),
            "tfe_source_pendulum_source_reference_solution_policy_smoke_full_T10": tfe_model.get(
                "source_reference_solution_policy_smoke_full_T10"
            ),
            "tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_implemented": tfe_model.get(
                "source_reference_solution_policy_full_T10_probe_implemented"
            ),
            "tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_completed": tfe_model.get(
                "source_reference_solution_policy_full_T10_probe_completed"
            ),
            "tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_rows_completed": tfe_model.get(
                "source_reference_solution_policy_full_T10_probe_rows_completed"
            ),
            "tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_steps": tfe_model.get(
                "source_reference_solution_policy_full_T10_probe_steps"
            ),
            "tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_check_steps": tfe_model.get(
                "source_reference_solution_policy_full_T10_probe_check_steps"
            ),
            "tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_coordinate_error": tfe_model.get(
                "source_reference_solution_policy_full_T10_probe_coordinate_error"
            ),
            "tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_velocity_error": tfe_model.get(
                "source_reference_solution_policy_full_T10_probe_velocity_error"
            ),
            "tfe_source_pendulum_source_comparator_candidate_runners_implemented": tfe_model.get(
                "source_comparator_candidate_runners_implemented"
            ),
            "tfe_source_pendulum_newmark_beta_candidate_runner_smoke_implemented": tfe_model.get(
                "newmark_beta_candidate_runner_smoke_implemented"
            ),
            "tfe_source_pendulum_trapezoidal_candidate_runner_smoke_implemented": tfe_model.get(
                "trapezoidal_candidate_runner_smoke_implemented"
            ),
            "tfe_source_pendulum_source_policy_method_runner_equivalent": tfe_model.get(
                "source_policy_method_runner_equivalent"
            ),
            "tfe_source_pendulum_tfe_m1_m2_m3_candidate_runner_smoke_implemented": tfe_model.get(
                "tfe_m1_m2_m3_candidate_runner_smoke_implemented"
            ),
            "tfe_source_pendulum_tfe_m1_m2_m3_source_policy_runners_implemented": tfe_model.get(
                "tfe_m1_m2_m3_source_policy_runners_implemented"
            ),
            "tfe_source_pendulum_gauss6_candidate_smoke_implemented": tfe_model.get(
                "gauss6_fullva_source_pendulum_candidate_smoke_implemented"
            ),
            "tfe_source_pendulum_gauss6_absolute_coordinate_source_policy_runner_implemented": tfe_model.get(
                "gauss6_fullva_absolute_coordinate_source_policy_runner_implemented"
            ),
            "tfe_source_pendulum_gauss6_candidate_rows": tfe_model.get(
                "gauss6_fullva_source_pendulum_candidate_rows"
            ),
            "tfe_source_pendulum_gauss6_candidate_source_policy_rows_completed": tfe_model.get(
                "gauss6_fullva_source_pendulum_candidate_source_policy_rows_completed"
            ),
            "tfe_source_pendulum_gauss6_candidate_method_equivalent": tfe_model.get(
                "gauss6_fullva_source_pendulum_candidate_method_equivalent"
            ),
            "tfe_source_pendulum_bounded_source_policy_runner_smoke_implemented": tfe_model.get(
                "bounded_source_policy_runner_smoke_implemented"
            ),
            "tfe_source_pendulum_bounded_source_policy_runner_rows": tfe_model.get(
                "bounded_source_policy_runner_rows"
            ),
            "tfe_source_pendulum_bounded_source_policy_runner_full_T10": tfe_model.get(
                "bounded_source_policy_runner_full_T10"
            ),
            "tfe_source_pendulum_bounded_source_policy_runner_source_policy_rows_completed": tfe_model.get(
                "bounded_source_policy_runner_source_policy_rows_completed"
            ),
            "tfe_source_pendulum_active_b2_candidate_row_smoke_implemented": tfe_model.get(
                "active_tfe_b2_candidate_row_smoke_implemented"
            ),
            "tfe_source_pendulum_active_b2_candidate_row_smoke_full_T10": tfe_model.get(
                "active_tfe_b2_candidate_row_smoke_full_T10"
            ),
            "tfe_source_pendulum_active_b2_source_policy_rows_completed": tfe_model.get(
                "active_tfe_b2_source_policy_rows_completed"
            ),
            "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_implemented": tfe_model.get(
                "active_tfe_b2_source_reference_full_T10_candidate_probe_implemented"
            ),
            "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_full_T10": tfe_model.get(
                "active_tfe_b2_source_reference_full_T10_candidate_probe_full_T10"
            ),
            "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_reference_invoked": tfe_model.get(
                "active_tfe_b2_source_reference_full_T10_candidate_probe_source_policy_reference_invoked"
            ),
            "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_source_policy_rows": tfe_model.get(
                "active_tfe_b2_source_reference_full_T10_candidate_probe_source_policy_rows_completed"
            ),
            "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_finite_rows": tfe_model.get(
                "active_tfe_b2_source_reference_full_T10_candidate_probe_finite_rows"
            ),
            "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_residual_ok_rows": tfe_model.get(
                "active_tfe_b2_source_reference_full_T10_candidate_probe_residual_ok_rows"
            ),
            "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_method_equivalent": tfe_model.get(
                "active_tfe_b2_source_reference_full_T10_candidate_probe_method_equivalent"
            ),
            "tfe_full_t10_absolute_dae_lift_status": tfe_full_t10_absolute.get("status"),
            "tfe_full_t10_absolute_dae_lift_completed": tfe_full_t10_absolute.get(
                "full_T10_absolute_coordinate_lift_completed"
            ),
            "tfe_full_t10_absolute_dae_lift_method_count": tfe_full_t10_absolute.get("method_count"),
            "tfe_full_t10_absolute_dae_lift_metric_rows": tfe_full_t10_absolute.get("metric_row_count"),
            "tfe_full_t10_absolute_dae_lift_step_residual_rows": tfe_full_t10_absolute.get(
                "step_residual_row_count"
            ),
            "tfe_full_t10_absolute_dae_lift_source_reference_invoked": tfe_full_t10_absolute.get(
                "source_reference_invoked"
            ),
            "tfe_full_t10_absolute_dae_lift_source_policy_rows_completed": tfe_full_t10_absolute.get(
                "source_policy_rows_completed"
            ),
            "tfe_full_t10_absolute_dae_lift_monolithic": tfe_full_t10_absolute.get(
                "monolithic_absolute_coordinate_dae_time_integrator"
            ),
            "tfe_full_t10_absolute_dae_lift_equivalent": tfe_full_t10_absolute.get(
                "source_policy_dae_runner_equivalent"
            ),
            "tfe_endpoint_boundary_certificate_status": tfe_endpoint_boundary.get("status"),
            "tfe_endpoint_boundary_literal_overrun_bound_proved": tfe_endpoint_boundary.get(
                "theorem", {}
            ).get("name")
            == "fixed_h_until_final_time_endpoint_bound",
            "tfe_endpoint_boundary_literal_exact_T_rows": tfe_endpoint_boundary.get(
                "algorithm_literal_exact_T_row_count"
            ),
            "tfe_endpoint_boundary_literal_overrun_rows": tfe_endpoint_boundary.get(
                "algorithm_literal_overrun_row_count"
            ),
            "tfe_endpoint_boundary_source_policy_rows_completed": tfe_endpoint_boundary.get(
                "source_policy_rows_completed"
            ),
            "tfe_endpoint_boundary_full_T10_policy_resolved": tfe_endpoint_boundary.get(
                "source_grid_policy_resolved_for_full_T10"
            ),
            "tfe_endpoint_boundary_exact_T_error_sampling_equivalent": tfe_endpoint_boundary.get(
                "source_policy_exact_T_error_sampling_equivalent"
            ),
            "tfe_full_T10_endpoint_policy_closure_certificate_status": tfe_endpoint_certificate.get(
                "status"
            ),
            "tfe_full_T10_endpoint_policy_closure_certificate_available": tfe_endpoint_certificate.get(
                "certificate_available"
            ),
            "tfe_full_T10_endpoint_policy_closure_certificate_positive": tfe_endpoint_certificate.get(
                "positive_full_T10_endpoint_policy_certified"
            ),
            "tfe_full_T10_endpoint_policy_closure_certificate_nonheavy_block_closed": tfe_endpoint_certificate.get(
                "nonheavy_contract_block_closed"
            ),
            "tfe_full_T10_endpoint_policy_closure_certificate_source_policy_execution_invoked": tfe_endpoint_certificate.get(
                "source_policy_execution_invoked"
            ),
            "tfe_full_T10_endpoint_policy_closure_certificate_can_close_now": tfe_endpoint_certificate.get(
                "can_close_now"
            ),
            "tfe_source_pendulum_active_b2_candidate_row_count": len(
                tfe_model.get("active_tfe_b2_candidate_row_smoke", {}).get("rows", [])
            ),
            "tfe_source_grid_policy_resolved_for_full_T10": external_checks.get(
                "tfe_source_grid_policy_resolved_for_full_T10"
            ),
            "tfe_source_grid_integer_step_incompatible_rows": external_checks.get(
                "tfe_source_grid_integer_step_incompatible_rows"
            ),
            "tfe_source_grid_exact_T_compatible_rows_endpoint_convention_resolved": external_checks.get(
                "tfe_source_grid_exact_T_compatible_rows_endpoint_convention_resolved"
            ),
            "tfe_source_grid_endpoint_incompatible_rows_requiring_policy": external_checks.get(
                "tfe_source_grid_endpoint_incompatible_rows_requiring_policy"
            ),
            "tfe_source_grid_policy_resolved_for_exact_T_compatible_rows": external_checks.get(
                "tfe_source_grid_policy_resolved_for_exact_T_compatible_rows"
            ),
            "tfe_source_grid_source_text_available": external_checks.get("tfe_source_grid_source_text_available"),
            "tfe_source_grid_source_text_anchor_count": external_checks.get(
                "tfe_source_grid_source_text_anchor_count"
            ),
            "tfe_source_grid_algorithm_literal_fixed_h": external_checks.get(
                "tfe_source_grid_algorithm_literal_fixed_h"
            ),
            "tfe_source_grid_endpoint_convention_resolved_for_error_sampling": external_checks.get(
                "tfe_source_grid_endpoint_convention_resolved_for_error_sampling"
            ),
            "tfe_endpoint_sensitivity_status": external_checks.get("tfe_endpoint_sensitivity_status"),
            "tfe_endpoint_sensitivity_method_count": external_checks.get("tfe_endpoint_sensitivity_method_count"),
            "tfe_endpoint_sensitivity_policy_count": external_checks.get("tfe_endpoint_sensitivity_policy_count"),
            "tfe_endpoint_sensitivity_summary_row_count": external_checks.get(
                "tfe_endpoint_sensitivity_summary_row_count"
            ),
            "tfe_endpoint_sensitivity_raw_row_count": external_checks.get("tfe_endpoint_sensitivity_raw_row_count"),
            "tfe_endpoint_sensitivity_source_policy_rows_completed": external_checks.get(
                "tfe_endpoint_sensitivity_source_policy_rows_completed"
            ),
            "tfe_endpoint_sensitivity_external_superiority_claim_allowed": external_checks.get(
                "tfe_endpoint_sensitivity_external_superiority_claim_allowed"
            ),
            "tfe_endpoint_sensitivity_source_policy_runner_equivalent": external_checks.get(
                "tfe_endpoint_sensitivity_source_policy_runner_equivalent"
            ),
            "tfe_endpoint_sensitivity_default_1e_4_campaign_invoked": external_checks.get(
                "tfe_endpoint_sensitivity_default_1e_4_campaign_invoked"
            ),
            "tfe_endpoint_sensitivity_run_v047_invoked": external_checks.get(
                "tfe_endpoint_sensitivity_run_v047_invoked"
            ),
            "tfe_source_pendulum_error_output_policy_encoded": tfe_model.get(
                "source_error_norm_and_output_policy_encoded"
            ),
            "tfe_source_pendulum_brown_mcphee_candidate_friction_law_encoded": tfe_model.get(
                "brown_mcphee_candidate_friction_law_encoded"
            ),
            "tfe_source_pendulum_frictional_candidate_smoke_implemented": tfe_model.get(
                "frictional_planar_candidate_rhs_smoke_implemented"
            ),
            "tfe_source_pendulum_candidate_friction_law_provenance": tfe_model.get(
                "candidate_friction_law_provenance"
            ),
            "tfe_brown_mcphee_boundary_status": tfe_brown_mcphee_boundary.get("status"),
            "tfe_brown_mcphee_boundary_source_code_equivalent_law": tfe_brown_mcphee_boundary.get(
                "brown_mcphee_source_code_equivalent_law"
            ),
            "tfe_brown_mcphee_boundary_transition_velocity_resolved": tfe_brown_mcphee_boundary.get(
                "brown_mcphee_transition_velocity_policy_resolved_from_source"
            ),
            "tfe_brown_mcphee_boundary_rows_promoted": tfe_brown_mcphee_boundary.get(
                "source_policy_rows_promoted"
            ),
            "tfe_brown_mcphee_boundary_nonheavy_contract_block_closed": tfe_brown_mcphee_boundary.get(
                "nonheavy_contract_block_closed"
            ),
            "tfe_brown_mcphee_candidate_dae_contract_rows": tfe_brown_mcphee_contract.get(
                "row_count"
            ),
            "tfe_brown_mcphee_candidate_dae_contract_step_rows": tfe_brown_mcphee_contract.get(
                "step_residual_row_count"
            ),
            "tfe_brown_mcphee_candidate_dae_contract_source_policy_rows": tfe_brown_mcphee_contract.get(
                "source_policy_rows_completed"
            ),
            "tfe_brown_mcphee_candidate_dae_contract_all_finite": tfe_brown_mcphee_contract.get(
                "all_rows_finite"
            ),
            "tfe_brown_mcphee_candidate_dae_contract_residual_ok": tfe_brown_mcphee_contract.get(
                "all_dae_residuals_below_1e_9"
            ),
            "tfe_brown_mcphee_candidate_dae_contract_power_nonpositive": tfe_brown_mcphee_contract.get(
                "all_candidate_friction_power_nonpositive"
            ),
            "tfe_brown_mcphee_candidate_dae_contract_equivalent_dae": tfe_brown_mcphee_contract.get(
                "source_policy_dae_runner_equivalent"
            ),
            "tfe_brown_mcphee_candidate_dae_contract_equivalent_method": tfe_brown_mcphee_contract.get(
                "source_policy_method_runner_equivalent"
            ),
            "tfe_brown_mcphee_candidate_dae_contract_source_law": tfe_brown_mcphee_contract.get(
                "brown_mcphee_source_code_equivalent_law"
            ),
            "tfe_brown_mcphee_candidate_dae_contract_monolithic": tfe_brown_mcphee_contract.get(
                "monolithic_absolute_coordinate_dae_time_integrator"
            ),
            "tfe_brown_mcphee_transition_velocity_sensitivity_rows": tfe_brown_mcphee_velocity_sensitivity.get(
                "endpoint_delta_row_count"
            ),
            "tfe_brown_mcphee_transition_velocity_sensitivity_contract_rows": tfe_brown_mcphee_velocity_sensitivity.get(
                "contract_row_count"
            ),
            "tfe_brown_mcphee_transition_velocity_sensitivity_source_policy_rows": tfe_brown_mcphee_velocity_sensitivity.get(
                "source_policy_rows_completed"
            ),
            "tfe_brown_mcphee_transition_velocity_sensitivity_material": tfe_brown_mcphee_velocity_sensitivity.get(
                "missing_transition_velocity_is_numerically_material"
            ),
            "tfe_brown_mcphee_transition_velocity_sensitivity_max_coordinate_delta": tfe_brown_mcphee_velocity_sensitivity.get(
                "max_endpoint_coordinate_delta_vs_baseline"
            ),
            "tfe_brown_mcphee_transition_velocity_sensitivity_max_velocity_delta": tfe_brown_mcphee_velocity_sensitivity.get(
                "max_endpoint_velocity_delta_vs_baseline"
            ),
            "tfe_brown_mcphee_transition_velocity_sensitivity_equivalence_flags_false": tfe_brown_mcphee_velocity_sensitivity.get(
                "all_contract_equivalence_flags_false"
            ),
            "tfe_brown_mcphee_source_code_equivalence_certificate_status": tfe_brown_mcphee_certificate.get(
                "status"
            ),
            "tfe_brown_mcphee_source_code_equivalence_certificate_available": tfe_brown_mcphee_certificate.get(
                "certificate_available"
            ),
            "tfe_brown_mcphee_source_code_equivalence_certificate_positive": tfe_brown_mcphee_certificate.get(
                "positive_source_code_equivalence_certified"
            ),
            "tfe_brown_mcphee_source_code_equivalence_certificate_nonheavy_block_closed": tfe_brown_mcphee_certificate.get(
                "nonheavy_contract_block_closed"
            ),
            "tfe_brown_mcphee_source_code_equivalence_certificate_source_policy_execution_invoked": tfe_brown_mcphee_certificate.get(
                "source_policy_execution_invoked"
            ),
            "tfe_brown_mcphee_source_code_equivalence_certificate_can_close_now": tfe_brown_mcphee_certificate.get(
                "can_close_now"
            ),
            "tfe_source_pendulum_setup_subrequirement_closed": tfe_model.get("closure_boundary", {}).get(
                "can_close_source_pendulum_setup_subrequirement"
            ),
            "tfe_source_policy_runner_implemented": tfe.get("pendulum_dae_runner_implemented"),
            "tfe_candidate_source_policy_boundary": tfe_candidate_source_policy_boundary,
            "tfe_candidate_source_policy_boundary_sources": external_checks.get(
                "tfe_candidate_source_policy_boundary_sources"
            ),
            "tfe_candidate_source_policy_boundary_sources_match": external_checks.get(
                "tfe_candidate_source_policy_boundary_sources_match"
            ),
            "tfe_candidate_source_policy_allowed_use": external_checks.get(
                "tfe_candidate_source_policy_allowed_use"
            ),
            "tfe_candidate_source_policy_dae_runner_equivalent": external_checks.get(
                "tfe_candidate_source_policy_dae_runner_equivalent"
            ),
            "tfe_candidate_source_policy_method_runner_equivalent": external_checks.get(
                "tfe_candidate_source_policy_method_runner_equivalent"
            ),
            "tfe_candidate_source_policy_rows_completed": external_checks.get(
                "tfe_candidate_source_policy_rows_completed"
            ),
            "tfe_candidate_source_policy_external_superiority_allowed": external_checks.get(
                "tfe_candidate_source_policy_external_superiority_allowed"
            ),
            "tfe_dae_runner_contract_gap_status": tfe_dae_gap.get("status"),
            "tfe_dae_runner_contract_gap_missing_block_count": tfe_dae_gap.get(
                "missing_contract_block_count"
            ),
            "tfe_dae_runner_contract_gap_missing_block_ids": tfe_dae_gap_missing_ids,
            "tfe_dae_runner_contract_gap_nonheavy_blocks": tfe_dae_gap.get(
                "nonheavy_missing_contract_blocks"
            ),
            "tfe_dae_runner_contract_gap_terminal_nonpromoted_blocks": tfe_dae_gap.get(
                "terminal_nonpromoted_contract_blocks"
            ),
            "tfe_dae_runner_contract_gap_terminal_nonpromoted_block_count": tfe_dae_gap.get(
                "terminal_nonpromoted_contract_block_count"
            ),
            "tfe_dae_runner_contract_gap_effective_missing_blocks": tfe_dae_gap.get(
                "effective_missing_contract_blocks"
            ),
            "tfe_dae_runner_contract_gap_effective_missing_block_count": tfe_dae_gap.get(
                "effective_missing_contract_block_count"
            ),
            "tfe_dae_runner_contract_gap_block_accounting": tfe_dae_gap.get(
                "contract_block_accounting"
            ),
            "tfe_dae_runner_contract_gap_execution_blocks": tfe_dae_gap.get(
                "source_policy_execution_missing_contract_blocks"
            ),
            "tfe_dae_runner_contract_gap_ready_to_execute_source_policy_now": tfe_dae_gap.get(
                "ready_to_execute_source_policy_now"
            ),
            "tfe_dae_runner_contract_gap_heavy_run_invoked": tfe_dae_gap.get(
                "heavy_numerical_run_invoked"
            ),
            "tfe_source_policy_execution_preflight": tfe_source_policy_execution_preflight,
            "tfe_source_policy_execution_preflight_status": tfe_source_policy_execution_preflight.get(
                "status"
            ),
            "tfe_source_policy_execution_preflight_opt_in_required": (
                tfe_source_policy_execution_preflight.get("explicit_user_opt_in_required")
            ),
            "tfe_source_policy_execution_preflight_nonheavy_dispositioned": (
                tfe_source_policy_execution_preflight.get("nonheavy_blocks_dispositioned_by_demotion")
            ),
            "tfe_source_policy_execution_preflight_execution_block_count": (
                tfe_source_policy_execution_preflight.get("execution_block_count")
            ),
            "tfe_source_policy_execution_preflight_can_promote_rows_now": (
                tfe_source_policy_execution_preflight.get("can_promote_any_tfe_source_policy_row_now")
            ),
            "tfe_source_policy_execution_preflight_ready_now": (
                tfe_source_policy_execution_preflight.get("ready_to_execute_source_policy_now")
            ),
            "tfe_runner_contract_preflight_status": tfe_runner_contract_preflight.get("status"),
            "tfe_runner_contract_preflight_entrypoints": (
                f"{tfe_runner_contract_preflight.get('callable_contract_count')}/"
                f"{tfe_runner_contract_preflight.get('entrypoint_count')}"
            ),
            "tfe_runner_contract_preflight_candidate_backed": (
                f"{tfe_runner_contract_preflight.get('candidate_backed_contract_count')}/"
                f"{tfe_runner_contract_preflight.get('entrypoint_count')}"
            ),
            "tfe_runner_contract_preflight_source_policy_rows_completed": (
                tfe_runner_contract_preflight.get("source_policy_rows_completed")
            ),
            "tfe_runner_contract_preflight_execution_blocks": (
                tfe_runner_contract_preflight.get("source_policy_execution_block_count")
            ),
            "tfe_runner_contract_preflight_safe_use": tfe_runner_contract_preflight.get(
                "safe_current_use"
            ),
            "oc12_archive_tfe_runner_contract_preflight_status": summary.get(
                "oc12_archive_tfe_runner_contract_preflight_status"
            ),
            "oc12_archive_tfe_runner_contract_preflight_entrypoints": summary.get(
                "oc12_archive_tfe_runner_contract_preflight_entrypoints"
            ),
            "oc12_archive_tfe_runner_contract_preflight_candidate_backed": summary.get(
                "oc12_archive_tfe_runner_contract_preflight_candidate_backed"
            ),
            "oc12_archive_tfe_runner_contract_preflight_source_policy_rows_completed": (
                summary.get("oc12_archive_tfe_runner_contract_preflight_source_policy_rows_completed")
            ),
            "oc12_archive_tfe_runner_contract_preflight_execution_blocks": summary.get(
                "oc12_archive_tfe_runner_contract_preflight_execution_blocks"
            ),
            "oc12_archive_tfe_runner_contract_preflight_safe_use": summary.get(
                "oc12_archive_tfe_runner_contract_preflight_safe_use"
            ),
            "oc12_archive_action_boundary": summary.get("oc12_archive_action_boundary"),
            "oc12_archive_safe_without_b4_opt_in_count": summary.get(
                "oc12_archive_safe_without_b4_opt_in_count"
            ),
            "oc12_archive_opt_in_required_action_count": summary.get(
                "oc12_archive_opt_in_required_action_count"
            ),
            "oc12_archive_source_policy_execution_allowed_now": summary.get(
                "oc12_archive_source_policy_execution_allowed_now"
            ),
            "oc12_archive_source_policy_execution_invoked": summary.get(
                "oc12_archive_source_policy_execution_invoked"
            ),
            "oc12_archive_exact_b4_opt_in_required_for_execution": summary.get(
                "oc12_archive_exact_b4_opt_in_required_for_execution"
            ),
            "oc12_archive_opt_in_required_command_count": summary.get(
                "oc12_archive_opt_in_required_command_count"
            ),
            "oc12_archive_opt_in_required_mapped_external_rows": summary.get(
                "oc12_archive_opt_in_required_mapped_external_rows"
            ),
            "oc12_archive_safe_action_ids": summary.get("oc12_archive_safe_action_ids"),
            "oc12_archive_opt_in_action_ids": summary.get("oc12_archive_opt_in_action_ids"),
            "tfe_source_policy_self_reproduction_preflight": tfe_self_reproduction_execution_preflight,
            "tfe_source_policy_self_reproduction_preflight_status": (
                tfe_self_reproduction_execution_preflight.get("status")
            ),
            "tfe_source_policy_self_reproduction_preflight_current_route": (
                tfe_self_reproduction_execution_preflight.get("current_route")
            ),
            "tfe_source_policy_self_reproduction_preflight_reopen_condition": (
                tfe_self_reproduction_execution_preflight.get("reopen_condition")
            ),
            "tfe_source_policy_self_reproduction_preflight_execution_block_count": (
                tfe_self_reproduction_execution_preflight.get("execution_block_count")
            ),
            "tfe_source_policy_self_reproduction_preflight_can_promote_rows_now": (
                tfe_self_reproduction_execution_preflight.get("can_promote_any_tfe_source_policy_row_now")
            ),
            "tfe_source_policy_self_reproduction_preflight_ready_now": (
                tfe_self_reproduction_execution_preflight.get("ready_to_execute_source_policy_now")
            ),
            "tfe_source_policy_self_reproduction_preflight_source_policy_rows_completed": (
                tfe_self_reproduction_execution_preflight.get("source_policy_rows_completed")
            ),
            "tfe_source_policy_self_reproduction_preflight_runner_contracts_required": (
                tfe_self_reproduction_execution_preflight.get("runner_contracts_required_before_execution", [])
            ),
            "tfe_source_policy_self_reproduction_required_next_action_count": len(
                tfe_self_reproduction_required_next_actions
            ),
        },
        "proof_status": {
            "proof_closure_status": proof.get("status"),
            "direct_pc2_proof_gap_closed": proof.get("closure_state", {}).get(
                "direct_pc2_proof_gap_closed", proof.get("closure_state", {}).get("proof_gap_closed")
            ),
            "proof_gap_closed": proof.get("closure_state", {}).get("proof_gap_closed"),
            "proof_gap_closed_scope": proof.get("closure_state", {}).get(
                "proof_gap_closed_scope", DIRECT_PC2_SCOPE
            ),
            "proof_gap_closed_reading_rule": DIRECT_PC2_READING_RULE,
            "theorem_statement_labels_present": proof_theorem_boundary.get(
                "all_required_labels_present_main_and_flat"
            ),
            "theorem_statement_boundary_present": proof_theorem_boundary.get(
                "conditional_theorem_boundary_present_main_and_flat"
            ),
            "theorem_statement_eta_condition_retained": proof_theorem_boundary.get(
                "eta_h_theorem_condition_retained"
            ),
            "theorem_statement_eta_evidence_closed": proof_theorem_boundary.get(
                "eta_h_solver_policy_evidence_closed"
            ),
            "theorem_statement_fixed_tolerance_asymptotic_proof": proof_theorem_boundary.get(
                "fixed_tolerance_runs_are_asymptotic_proof"
            ),
            "theorem_statement_residual_to_error_not_promoted": proof_theorem_boundary.get(
                "does_not_promote_residual_to_error"
            ),
            "theorem_statement_source_policy_or_full_tfe_not_promoted": proof_theorem_boundary.get(
                "does_not_promote_source_policy_or_full_tfe"
            ),
            "proof_claim_traceability_theorem_label": proof_claim_theorem_traceability.get(
                "accepted_theorem_label"
            ),
            "proof_claim_traceability_theorem_labels_present": proof_claim_theorem_traceability.get(
                "theorem_statement_labels_present"
            ),
            "proof_claim_traceability_theorem_boundary_present": proof_claim_theorem_traceability.get(
                "conditional_theorem_boundary_present"
            ),
            "proof_claim_traceability_theorem_claims_mapped": proof_claim_theorem_traceability.get(
                "conditional_proof_claims_mapped_to_manuscript"
            ),
            "proof_claim_traceability_dependency_graph_present": proof_claim_theorem_traceability.get(
                "proof_dependency_graph_present"
            ),
            "proof_claim_traceability_table_present": proof_claim_theorem_traceability.get(
                "proof_traceability_table_present"
            ),
            "proof_claim_traceability_dynamic_theorem_matrix_present": proof_claim_theorem_traceability.get(
                "dynamic_proof_closure_matrix_present"
            ),
            "proof_claim_traceability_primitive_lane_boundary_present": proof_claim_theorem_traceability.get(
                "primitive_lane_boundary_present"
            ),
            "proof_claim_traceability_residual_nonpromotion_present": proof_claim_theorem_traceability.get(
                "residual_nonpromotion_present"
            ),
            "proof_claim_traceability_eta_condition_retained": proof_claim_theorem_traceability.get(
                "eta_h_theorem_condition_retained"
            ),
            "proof_claim_traceability_eta_evidence_closed": proof_claim_theorem_traceability.get(
                "eta_h_solver_policy_evidence_closed"
            ),
            "proof_claim_traceability_fixed_tolerance_asymptotic_proof": proof_claim_theorem_traceability.get(
                "fixed_tolerance_runs_are_asymptotic_proof"
            ),
            "proof_claim_traceability_residual_to_error_not_promoted": proof_claim_theorem_traceability.get(
                "residual_to_error_not_promoted"
            ),
            "proof_claim_traceability_p7_retained_nonpromotion_boundary_present": (
                proof_claim_theorem_traceability.get("p7_retained_nonpromotion_boundary_present")
            ),
            "proof_claim_traceability_b1_closure_scope_boundary_present": (
                proof_claim_theorem_traceability.get("b1_closure_scope_boundary_present")
            ),
            "proof_claim_traceability_p6_solver_scope_boundary_present": (
                proof_claim_theorem_traceability.get("p6_solver_scope_boundary_present")
            ),
            "proof_claim_traceability_p1p2_compact_tube_boundary_present": (
                proof_claim_theorem_traceability.get("p1p2_compact_tube_boundary_present")
            ),
            "proof_claim_traceability_p3p4_implementation_boundary_present": (
                proof_claim_theorem_traceability.get("p3p4_implementation_boundary_present")
            ),
            "proof_claim_traceability_p5_direct_route_boundary_present": (
                proof_claim_theorem_traceability.get("p5_direct_route_boundary_present")
            ),
            "proof_claim_traceability_p_interface_satisfaction_ledger_present": (
                proof_claim_theorem_traceability.get("p_interface_satisfaction_ledger_present")
            ),
            "proof_claim_traceability_p7_residual_to_error_ledger_present": (
                proof_claim_theorem_traceability.get(
                    "p7_residual_to_error_ledger_present"
                )
            ),
            "proof_claim_traceability_theorem_use_rule_present": (
                proof_claim_theorem_traceability.get("theorem_use_rule_present")
            ),
            "proof_claim_traceability_quantifier_domain_ledger_present": (
                proof_claim_theorem_traceability.get(
                    "quantifier_domain_ledger_present"
                )
            ),
            "proof_claim_traceability_local_global_transfer_ledger_present": (
                proof_claim_theorem_traceability.get(
                    "local_global_transfer_ledger_present"
                )
            ),
            "proof_claim_traceability_objective_completion_boundary_present": (
                proof_claim_theorem_traceability.get(
                    "objective_completion_boundary_present"
                )
            ),
            "proof_claim_traceability_constant_dependency_ledger_present": (
                proof_claim_theorem_traceability.get(
                    "constant_dependency_ledger_present"
                )
            ),
            "proof_claim_traceability_theorem_dependency_consumption_ledger_present": (
                proof_claim_theorem_traceability.get(
                    "theorem_dependency_consumption_ledger_present"
                )
            ),
            "proof_claim_traceability_branch_consistency_ledger_present": (
                proof_claim_theorem_traceability.get(
                    "branch_consistency_ledger_present"
                )
            ),
            "proof_claim_traceability_implementation_route_oracle_ledger_present": (
                proof_claim_theorem_traceability.get(
                    "implementation_route_oracle_ledger_present"
                )
            ),
            "proof_claim_traceability_nonlinear_solver_scale_ledger_present": (
                proof_claim_theorem_traceability.get(
                    "nonlinear_solver_scale_ledger_present"
                )
            ),
            "proof_claim_traceability_local_defect_decomposition_ledger_present": (
                proof_claim_theorem_traceability.get(
                    "local_defect_decomposition_ledger_present"
                )
            ),
            "proof_claim_traceability_theorem_output_scope_ledger_present": (
                proof_claim_theorem_traceability.get(
                    "theorem_output_scope_ledger_present"
                )
            ),
            "proof_claim_traceability_reporting_map_ledger_present": (
                proof_claim_theorem_traceability.get("reporting_map_ledger_present")
            ),
            "proof_claim_traceability_proof_causality_ledger_present": (
                proof_claim_theorem_traceability.get(
                    "proof_causality_ledger_present"
                )
            ),
            "proof_claim_traceability_direct_route_anticircularity_ledger_present": (
                proof_claim_theorem_traceability.get(
                    "direct_route_anticircularity_ledger_present"
                )
            ),
            "proof_claim_traceability_source_policy_or_full_tfe_not_promoted": proof_claim_theorem_traceability.get(
                "source_policy_or_full_tfe_not_promoted"
            ),
            "proof_claim_traceability_no_state_change": proof_claim_theorem_traceability.get(
                "does_not_change_proof_closure_state"
            ),
            "proof_claim_traceability_remaining_boundary_status": proof_claim_remaining_boundary.get(
                "status"
            ),
            "proof_claim_traceability_submission_satisfied_assumption_ids": proof_claim_remaining_boundary.get(
                "submission_satisfied_ids"
            ),
            "proof_claim_traceability_retained_or_open_assumption_ids": proof_claim_remaining_boundary.get(
                "retained_or_open_ids"
            ),
            "proof_claim_traceability_retained_theorem_interface_ids": proof_claim_remaining_boundary.get(
                "retained_theorem_interface_ids"
            ),
            "proof_claim_traceability_open_nonpromotion_boundary_ids": proof_claim_remaining_boundary.get(
                "open_nonpromotion_boundary_ids"
            ),
            "proof_claim_traceability_retained_theorem_interface_count": proof_claim_remaining_boundary.get(
                "retained_theorem_interface_count"
            ),
            "proof_claim_traceability_open_nonpromotion_boundary_count": proof_claim_remaining_boundary.get(
                "open_nonpromotion_boundary_count"
            ),
            "proof_claim_traceability_remaining_global_boundaries": proof_claim_remaining_boundary.get(
                "global_submission_boundaries_retained"
            ),
            "proof_claim_traceability_reader_facing_manuscript_boundary_present": proof_writing_card.get(
                "reader_facing_manuscript_boundary_present"
            ),
            "proof_writing_boundary_card_status": proof_writing_card.get("status"),
            "proof_writing_boundary_reader_facing_manuscript_boundary_present": proof_writing_card.get(
                "reader_facing_manuscript_boundary_present"
            ),
            "proof_writing_boundary_p7_retained_nonpromotion_boundary_present": proof_writing_card.get(
                "p7_retained_nonpromotion_boundary_present"
            ),
            "proof_writing_boundary_b1_closure_scope_boundary_present": proof_writing_card.get(
                "b1_closure_scope_boundary_present"
            ),
            "proof_writing_boundary_p6_solver_scope_boundary_present": proof_writing_card.get(
                "p6_solver_scope_boundary_present"
            ),
            "proof_writing_boundary_p1p2_compact_tube_boundary_present": proof_writing_card.get(
                "p1p2_compact_tube_boundary_present"
            ),
            "proof_writing_boundary_p3p4_implementation_boundary_present": proof_writing_card.get(
                "p3p4_implementation_boundary_present"
            ),
            "proof_writing_boundary_p5_direct_route_boundary_present": proof_writing_card.get(
                "p5_direct_route_boundary_present"
            ),
            "proof_writing_boundary_proof_causality_ledger_present": proof_writing_card.get(
                "proof_causality_ledger_present"
            ),
            "proof_writing_boundary_direct_route_anticircularity_ledger_present": proof_writing_card.get(
                "direct_route_anticircularity_ledger_present"
            ),
            "proof_writing_boundary_p_interface_satisfaction_ledger_present": proof_writing_card.get(
                "p_interface_satisfaction_ledger_present"
            ),
            "proof_writing_boundary_p7_residual_to_error_ledger_present": proof_writing_card.get(
                "p7_residual_to_error_ledger_present"
            ),
            "proof_writing_boundary_theorem_use_rule_present": proof_writing_card.get(
                "theorem_use_rule_present"
            ),
            "proof_writing_boundary_quantifier_domain_ledger_present": proof_writing_card.get(
                "quantifier_domain_ledger_present"
            ),
            "proof_writing_boundary_local_global_transfer_ledger_present": proof_writing_card.get(
                "local_global_transfer_ledger_present"
            ),
            "proof_writing_boundary_objective_completion_boundary_present": proof_writing_card.get(
                "objective_completion_boundary_present"
            ),
            "proof_writing_boundary_constant_dependency_ledger_present": proof_writing_card.get(
                "constant_dependency_ledger_present"
            ),
            "proof_writing_boundary_theorem_dependency_consumption_ledger_present": proof_writing_card.get(
                "theorem_dependency_consumption_ledger_present"
            ),
            "proof_writing_boundary_branch_consistency_ledger_present": proof_writing_card.get(
                "branch_consistency_ledger_present"
            ),
            "proof_writing_boundary_implementation_route_oracle_ledger_present": proof_writing_card.get(
                "implementation_route_oracle_ledger_present"
            ),
            "proof_writing_boundary_nonlinear_solver_scale_ledger_present": proof_writing_card.get(
                "nonlinear_solver_scale_ledger_present"
            ),
            "proof_writing_boundary_local_defect_decomposition_ledger_present": proof_writing_card.get(
                "local_defect_decomposition_ledger_present"
            ),
            "proof_writing_boundary_theorem_output_scope_ledger_present": proof_writing_card.get(
                "theorem_output_scope_ledger_present"
            ),
            "proof_writing_boundary_reporting_map_ledger_present": proof_writing_card.get(
                "reporting_map_ledger_present"
            ),
            "proof_writing_boundary_safe_reader_claim": proof_writing_card.get("safe_reader_claim"),
            "proof_writing_boundary_forbidden_reader_claims": proof_writing_card.get(
                "forbidden_reader_claims"
            ),
            "proof_writing_boundary_global_boundaries_retained": proof_writing_card.get(
                "global_submission_boundaries_retained"
            ),
            "proof_claim_traceability_manuscript_anchor_map_present": proof_claim_traceability.get(
                "manuscript_anchor_map", {}
            ).get("all_label_anchors_present"),
            "proof_claim_traceability_manuscript_anchor_label_count": proof_claim_traceability.get(
                "manuscript_anchor_map", {}
            ).get("label_anchor_count"),
            "proof_claim_traceability_theorem_assumption_anchor_map_present": proof_claim_traceability.get(
                "manuscript_anchor_map", {}
            ).get("all_theorem_assumption_anchors_present"),
            "proof_claim_traceability_theorem_assumption_anchor_count": proof_claim_traceability.get(
                "manuscript_anchor_map", {}
            ).get("theorem_assumption_anchor_count"),
            "proof_claim_traceability_theorem_assumption_anchor_ids": proof_claim_traceability.get(
                "manuscript_anchor_map", {}
            ).get("theorem_assumption_anchor_ids"),
            "proof_closure_manuscript_anchor_map_present": proof.get("manuscript_anchor_map", {}).get(
                "all_label_anchors_present"
            ),
            "proof_closure_manuscript_anchor_label_count": proof.get("manuscript_anchor_map", {}).get(
                "label_anchor_count"
            ),
            "proof_closure_theorem_assumption_anchor_map_present": proof.get("manuscript_anchor_map", {}).get(
                "all_theorem_assumption_anchors_present"
            ),
            "proof_closure_theorem_assumption_anchor_count": proof.get("manuscript_anchor_map", {}).get(
                "theorem_assumption_anchor_count"
            ),
            "proof_closure_theorem_assumption_anchor_ids": proof.get("manuscript_anchor_map", {}).get(
                "theorem_assumption_anchor_ids"
            ),
            "proof_closure_proof_claim_anchor_maps_match": proof.get("manuscript_anchor_map", {})
            == proof_claim_traceability.get("manuscript_anchor_map", {}),
            "proof_contract_anchor_evidence_sources": proof_checks.get(
                "proof_contract_anchor_evidence_sources"
            ),
            "proof_style_anchor_evidence_sources": proof_checks.get(
                "proof_style_anchor_evidence_sources"
            ),
            "strict_proof_anchor_evidence_sources": proof_checks.get(
                "strict_proof_anchor_evidence_sources"
            ),
            "proof_anchor_evidence_sources_match": proof_checks.get(
                "proof_anchor_evidence_sources_match"
            ),
            "manuscript_traceability_mapped": proof_manuscript_traceability.get(
                "conditional_proof_claims_mapped_to_manuscript"
            ),
            "manuscript_traceability_no_state_change": proof_manuscript_traceability.get(
                "does_not_change_proof_closure_state"
            ),
            "manuscript_traceability_dependency_graph_present": proof_manuscript_traceability.get(
                "proof_dependency_graph_present_main_and_flat"
            ),
            "manuscript_traceability_dynamic_matrix_present": proof_manuscript_traceability.get(
                "dynamic_proof_closure_matrix_present_main_and_flat"
            ),
            "manuscript_traceability_primitive_lane_boundary_present": proof_manuscript_traceability.get(
                "primitive_lane_boundary_present_main_and_flat"
            ),
            "manuscript_traceability_residual_nonpromotion_present": proof_manuscript_traceability.get(
                "residual_to_error_nonpromotion_present_main_and_flat"
            ),
            "open_dynamic_rows": proof.get("evidence_summary", {}).get("open_dynamic_rows"),
            "open_dynamic_rows_scope": proof.get("evidence_summary", {}).get(
                "open_dynamic_rows_scope", "symbolic_primitive_certificate_route_not_active_direct_pc2"
            ),
            "symbolic_primitive_route_open_dynamic_rows": proof.get("evidence_summary", {}).get(
                "open_dynamic_rows"
            ),
            "certified_non_dynamic_rows": proof.get("evidence_summary", {}).get("certified_non_dynamic_rows"),
            "newton_euler_obligation_coverage_matrix_complete": proof.get("evidence_summary", {}).get(
                "newton_euler_obligation_coverage_matrix_complete"
            ),
            "newton_euler_row_obligation_links": proof.get("evidence_summary", {}).get(
                "newton_euler_row_obligation_links"
            ),
            "newton_euler_rows_with_complete_obligation_sets": proof.get("evidence_summary", {}).get(
                "newton_euler_rows_with_complete_obligation_sets"
            ),
        },
        "extraction_rules": [
            "Primary supplement should expose a small runner-centered API, not the full audit repository.",
            "The 44-cell result matrix is ready for paper traceability but remains bounded common-reference evidence.",
            "Audit builders and validators should be supplementary provenance unless needed to reproduce a reported table.",
            "No external-superiority claim is allowed until source-policy rows close.",
            "No submission-ready code package is allowed until the TFE source-policy runner and proof certificate gaps close or are explicitly demoted.",
        ],
    }

    missing_existing_files = [
        item["path"]
        for item in files
        if item["status"] != "open_missing" and item["exists"] is not True
    ]
    manifest["candidate_file_count"] = len(files)
    manifest["candidate_existing_file_count"] = len(files) - len(missing_existing_files)
    manifest["candidate_missing_existing_files"] = missing_existing_files
    manifest["minimal_package_ready"] = summary["minimal_reproducible_submission_code_ready"]
    manifest["candidate_files"] = (
        f"{manifest['candidate_existing_file_count']}/{manifest['candidate_file_count']}"
    )
    manifest["candidate_python_lines"] = summary["minimal_reproducibility_candidate_python_lines"]
    manifest["source_policy_closed_ratio"] = (
        f"{summary['source_policy_closed_rows']}/{summary['source_policy_total_rows']}"
    )
    manifest["source_policy_closed"] = (
        summary["source_policy_closed_rows"] == summary["source_policy_total_rows"]
    )
    manifest["source_policy_rows_closed"] = summary["source_policy_closed_rows"]
    manifest["source_policy_rows_total"] = summary["source_policy_total_rows"]
    manifest["full_source_policy_runner_package_ready"] = summary[
        "full_source_policy_runner_package_ready"
    ]
    manifest["narrowed_archive_boundary"] = narrowed_repro_code_archive.get(
        "narrowed_archive_boundary"
    )
    manifest["run_v047_invoked"] = any(
        flag is True
        for flag in [
            full_source_runner_gap.get("run_v047_invoked"),
            objective_completion.get("run_v047_invoked"),
            summary.get("b6_closed_loop_extraction_run_v047_invoked"),
            summary.get("tfe_endpoint_sensitivity_run_v047_invoked"),
        ]
    )
    manifest["heavy_numerical_run_invoked"] = any(
        flag is True
        for flag in [
            full_source_runner_gap.get("heavy_numerical_run_invoked"),
            objective_completion.get("heavy_numerical_run_invoked"),
            tfe_dae_gap.get("heavy_numerical_run_invoked"),
        ]
    )
    manifest["v048_runner_invoked"] = any(
        flag is True
        for flag in [
            full_source_runner_gap.get("v048_runner_invoked"),
            objective_completion.get("v048_runner_invoked"),
        ]
    )
    manifest["tfe_runner"] = summary["tfe_source_policy_runner_implemented"]
    manifest["source_policy_execution_handoff_status"] = summary[
        "source_policy_execution_handoff_status"
    ]
    manifest["source_policy_execution_handoff_authorized"] = summary[
        "source_policy_execution_handoff_authorized"
    ]
    manifest["source_policy_execution_handoff_commands_not_run"] = summary[
        "source_policy_execution_handoff_commands_not_run"
    ]
    manifest["source_policy_execution_handoff_driver"] = summary[
        "source_policy_execution_handoff_driver"
    ]
    manifest["source_policy_execution_handoff_driver_requires_exact_approval"] = summary[
        "source_policy_execution_handoff_driver_requires_exact_approval"
    ]
    manifest["source_policy_execution_handoff_driver_does_not_authorize_execution"] = summary[
        "source_policy_execution_handoff_driver_does_not_authorize_execution"
    ]
    manifest["source_policy_execution_allowed_now"] = summary[
        "full_source_policy_runner_archive_gap_source_policy_execution_allowed_now"
    ]
    manifest["source_policy_execution_invoked"] = summary[
        "full_source_policy_runner_archive_gap_source_policy_execution_invoked"
    ]
    manifest["exact_b4_opt_in_required_for_execution"] = summary[
        "full_source_policy_runner_archive_gap_exact_b4_opt_in_required_for_execution"
    ]
    manifest["safe_action_ids"] = summary["full_source_policy_runner_archive_gap_safe_action_ids"]
    manifest["opt_in_action_ids"] = summary["full_source_policy_runner_archive_gap_opt_in_action_ids"]
    manifest["required_user_approval_statement"] = summary[
        "full_source_policy_runner_archive_gap_required_approval_statement"
    ]
    manifest["guarded_execution_driver"] = summary["source_policy_execution_handoff_driver"]
    manifest["oc12_archive_tfe_runner_contract_preflight_status"] = summary[
        "oc12_archive_tfe_runner_contract_preflight_status"
    ]
    manifest["oc12_archive_tfe_runner_contract_preflight_entrypoints"] = summary[
        "oc12_archive_tfe_runner_contract_preflight_entrypoints"
    ]
    manifest["oc12_archive_tfe_runner_contract_preflight_candidate_backed"] = summary[
        "oc12_archive_tfe_runner_contract_preflight_candidate_backed"
    ]
    manifest["oc12_archive_tfe_runner_contract_preflight_source_policy_rows_completed"] = summary[
        "oc12_archive_tfe_runner_contract_preflight_source_policy_rows_completed"
    ]
    manifest["oc12_archive_tfe_runner_contract_preflight_execution_blocks"] = summary[
        "oc12_archive_tfe_runner_contract_preflight_execution_blocks"
    ]
    manifest["oc12_archive_tfe_runner_contract_preflight_safe_use"] = summary[
        "oc12_archive_tfe_runner_contract_preflight_safe_use"
    ]
    manifest["oc12_archive_action_boundary"] = summary["oc12_archive_action_boundary"]
    manifest["oc12_archive_safe_without_b4_opt_in_count"] = summary[
        "oc12_archive_safe_without_b4_opt_in_count"
    ]
    manifest["oc12_archive_opt_in_required_action_count"] = summary[
        "oc12_archive_opt_in_required_action_count"
    ]
    manifest["oc12_archive_source_policy_execution_allowed_now"] = summary[
        "oc12_archive_source_policy_execution_allowed_now"
    ]
    manifest["oc12_archive_source_policy_execution_invoked"] = summary[
        "oc12_archive_source_policy_execution_invoked"
    ]
    manifest["oc12_archive_exact_b4_opt_in_required_for_execution"] = summary[
        "oc12_archive_exact_b4_opt_in_required_for_execution"
    ]
    manifest["oc12_archive_opt_in_required_command_count"] = summary[
        "oc12_archive_opt_in_required_command_count"
    ]
    manifest["oc12_archive_opt_in_required_mapped_external_rows"] = summary[
        "oc12_archive_opt_in_required_mapped_external_rows"
    ]
    manifest["oc12_archive_safe_action_ids"] = summary["oc12_archive_safe_action_ids"]
    manifest["oc12_archive_opt_in_action_ids"] = summary["oc12_archive_opt_in_action_ids"]

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# CMAME Reproducibility Package Manifest",
        "",
        f"Status: **{manifest['status']}**.",
        f"Submission-ready code package: `{summary['minimal_reproducible_submission_code_ready']}`.",
        f"Current Python size: `{summary['combined_python_line_count']}` lines.",
        f"Reviewer-facing code limit: `{summary['reviewer_facing_python_file_limit']}` Python files / `{summary['reviewer_facing_python_line_limit']}` lines.",
        f"Research-audit tree primary submission allowed: `{summary['research_audit_repo_primary_submission_allowed']}`; provenance-only: `{summary['research_audit_repo_provenance_only']}`.",
        f"Runner-centered package ready: `{summary['runner_centered_package_ready']}`.",
        f"Runner adapter present/self-contained: `{summary['runner_adapter_present']}/{summary['runner_adapter_self_contained_simulation_runner']}`.",
        f"Broad self-contained source-policy package ready: `{summary['self_contained_runner_ready']}`.",
        f"Top-level package summary: candidate files `{manifest['candidate_files']}`, candidate Python lines `{manifest['candidate_python_lines']}`, source-policy `{manifest['source_policy_closed_ratio']}`, TFE runner `{manifest['tfe_runner']}`.",
        f"Top-level source-policy handoff: `{manifest['source_policy_execution_handoff_status']}`; authorized/not-run `{manifest['source_policy_execution_handoff_authorized']}/{manifest['source_policy_execution_handoff_commands_not_run']}`; driver `{manifest['source_policy_execution_handoff_driver']}`.",
        f"Top-level source-policy execution boundary: allowed/invoked/exact `{manifest['source_policy_execution_allowed_now']}/{manifest['source_policy_execution_invoked']}/{manifest['exact_b4_opt_in_required_for_execution']}`; safe/opt-in actions `{manifest['safe_action_ids']}/{manifest['opt_in_action_ids']}`.",
        f"Top-level OC12 archive boundary: TFE preflight `{manifest['oc12_archive_tfe_runner_contract_preflight_status']}/{manifest['oc12_archive_tfe_runner_contract_preflight_entrypoints']}/{manifest['oc12_archive_tfe_runner_contract_preflight_candidate_backed']}/{manifest['oc12_archive_tfe_runner_contract_preflight_source_policy_rows_completed']}/{manifest['oc12_archive_tfe_runner_contract_preflight_execution_blocks']}`; action boundary `{manifest['oc12_archive_safe_without_b4_opt_in_count']}/{manifest['oc12_archive_opt_in_required_action_count']}/{manifest['oc12_archive_source_policy_execution_allowed_now']}/{manifest['oc12_archive_source_policy_execution_invoked']}/{manifest['oc12_archive_exact_b4_opt_in_required_for_execution']}/{manifest['oc12_archive_opt_in_required_command_count']}/{manifest['oc12_archive_opt_in_required_mapped_external_rows']}`; safe/opt-in actions `{manifest['oc12_archive_safe_action_ids']}/{manifest['oc12_archive_opt_in_action_ids']}`.",
        "Source-policy-open status-token rule: any manifest status ending in "
        "`source_policy_open` or `source_policy_package_open` denotes a local, "
        "narrowed replay/provenance artifact whose source-policy rows are still "
        "open; it is not source-policy readiness, external-superiority evidence, "
        "or a submission-ready runner-package claim.",
        "",
        "## Summary",
        "",
        f"- Paper core result table ready: `{summary['paper_core_result_table_ready']}`.",
        f"- Common-reference diagnostic favorable order/error cells: `{summary['common_reference_order_wins']}/{summary['common_reference_order_comparisons']}` and `{summary['common_reference_error_wins']}/{summary['common_reference_error_comparisons']}`; not source-policy superiority evidence.",
        f"- Objective blocker status by id: `{summary['objective_blocker_status_by_id']}`.",
        f"- Objective blocker required-to-close by id: `{summary['objective_blocker_required_to_close_by_id']}`.",
        f"- Objective blocker safe next actions by id: `{summary['objective_blocker_safe_next_actions_by_id']}`.",
        f"- Objective blocker opt-in required actions by id: `{summary['objective_blocker_opt_in_required_actions_by_id']}`.",
        f"- Generic blocker aliases required/safe/opt-in: `{summary['blocker_required_to_close_by_id']}/{summary['blocker_safe_next_actions_by_id']}/{summary['blocker_opt_in_required_actions_by_id']}`.",
        f"- Source-policy rows closed: `{summary['source_policy_closed_rows']}/{summary['source_policy_total_rows']}`.",
        f"- Source-policy public-code refresh: `{summary['source_policy_public_code_refresh_status']}` on `{summary['source_policy_public_code_refresh_date']}`; rows/public-code/attempted/unable/closed `{summary['source_policy_public_code_refresh_rows']}/{summary['source_policy_public_code_refresh_public_code_available_rows']}/{summary['source_policy_public_code_refresh_self_reproduction_attempted_rows']}/{summary['source_policy_public_code_refresh_unable_to_reproduce_rows']}/{summary['source_policy_public_code_refresh_source_policy_rows_closed']}`.",
        f"- Latest public-code refresh supplement: `{summary['source_policy_public_code_refresh_latest_status']}` on `{summary['source_policy_public_code_refresh_latest_date']}`; rows/queries/positive/closed/promoted `{summary['source_policy_public_code_refresh_latest_rows']}/{summary['source_policy_public_code_refresh_latest_current_queries']}/{summary['source_policy_public_code_refresh_latest_positive_artifact_rows']}/{summary['source_policy_public_code_refresh_latest_source_policy_rows_closed']}/{summary['source_policy_public_code_refresh_latest_source_policy_rows_promoted']}`.",
        f"- Latest external public-code probe: `{summary['source_policy_public_code_refresh_latest_external_probe_date']}/{summary['source_policy_public_code_refresh_latest_external_probe_count']}/{summary['source_policy_public_code_refresh_latest_external_probe_positive_artifact_rows']}/{summary['source_policy_public_code_refresh_latest_external_probe_source_policy_rows_closed']}/{summary['source_policy_public_code_refresh_latest_external_probe_access_limited_count']}/{summary['source_policy_public_code_refresh_latest_external_probe_global_absence_proved']}/{summary['source_policy_public_code_refresh_latest_external_probe_reopen_triggered']}`.",
        f"- Full source-policy runner archive gap: `{summary['full_source_policy_runner_archive_gap_status']}`; ready/current-archive-use `{summary['full_source_policy_runner_archive_gap_ready_now']}/{summary['full_source_policy_runner_archive_gap_current_archive_use']}`; rows closed/total `{summary['full_source_policy_runner_archive_gap_source_policy_rows_closed']}/{summary['full_source_policy_runner_archive_gap_source_policy_rows_total']}`; terminal-unable/RA-HI-open `{summary['full_source_policy_runner_archive_gap_terminal_unable_rows']}/{summary['full_source_policy_runner_archive_gap_ra_hi_open_rows']}`.",
        f"- Full source-policy runner archive action boundary safe/opt-in/allowed/invoked/exact/commands/rows: `{summary['full_source_policy_runner_archive_gap_safe_without_b4_opt_in_count']}/{summary['full_source_policy_runner_archive_gap_opt_in_required_action_count']}/{summary['full_source_policy_runner_archive_gap_source_policy_execution_allowed_now']}/{summary['full_source_policy_runner_archive_gap_source_policy_execution_invoked']}/{summary['full_source_policy_runner_archive_gap_exact_b4_opt_in_required_for_execution']}/{summary['full_source_policy_runner_archive_gap_opt_in_required_command_count']}/{summary['full_source_policy_runner_archive_gap_opt_in_required_mapped_external_rows']}`.",
        f"- Full source-policy runner archive terminal reopen conditions: `tfe2026_original_pendulum={summary['full_source_policy_runner_archive_gap_tfe_reopen_condition']}; vp2024_velocity_partitioning={summary['full_source_policy_runner_archive_gap_vp2024_reopen_condition']}`.",
        f"- Source-policy reopen monitor digests: direct `{summary['source_policy_reopen_condition_monitor_local_scan_digest']}/{summary['source_policy_reopen_condition_monitor_evidence_digest']}`; archive `{summary['full_source_policy_runner_archive_gap_reopen_monitor_local_scan_digest']}/{summary['full_source_policy_runner_archive_gap_reopen_monitor_evidence_digest']}`.",
        f"- Full source-policy runner archive exact B4 approval: `{summary['full_source_policy_runner_archive_gap_required_approval_statement']}`.",
        f"- Source-policy execution handoff: `{summary['source_policy_execution_handoff_status']}`; authorized/commands-not-run `{summary['source_policy_execution_handoff_authorized']}/{summary['source_policy_execution_handoff_commands_not_run']}`; ready commands/mapped `{summary['source_policy_execution_handoff_ready_command_count']}/{summary['source_policy_execution_handoff_ready_command_mapped_rows']}`; terminal unable `{summary['source_policy_execution_handoff_terminal_unable_rows']}`.",
        f"- Source-policy command preflight freeze: `{summary['source_policy_command_preflight_freeze_status']}`; commands/unique-rows/row-refs/mismatches/artifacts/executed/closed `{summary['source_policy_command_preflight_freeze_ready_commands']}/{summary['source_policy_command_preflight_freeze_unique_rows']}/{summary['source_policy_command_preflight_freeze_row_refs']}/{summary['source_policy_command_preflight_freeze_mismatches']}/{summary['source_policy_command_preflight_freeze_expected_artifacts']}/{summary['source_policy_command_preflight_freeze_commands_executed']}/{summary['source_policy_command_preflight_freeze_source_policy_closed']}`.",
        f"- Source-policy expected-output schema audit: `{summary['source_policy_expected_output_schema_audit_status']}`; commands/artifacts/hash-match/csv/json/schema-ready/executed/closed `{summary['source_policy_expected_output_schema_audit_commands']}/{summary['source_policy_expected_output_schema_audit_artifacts']}/{summary['source_policy_expected_output_schema_audit_hash_match']}/{summary['source_policy_expected_output_schema_audit_csv_parseable']}/{summary['source_policy_expected_output_schema_audit_json_parseable']}/{summary['source_policy_expected_output_schema_audit_schema_ready']}/{summary['source_policy_expected_output_schema_audit_commands_executed']}/{summary['source_policy_expected_output_schema_audit_source_policy_closed']}`.",
        f"- Source-policy expected-output promotion-readiness blocker audit: `{summary['source_policy_expected_output_promotion_readiness_blocker_status']}`; commands/schema-ready/promotion-ready/row-refs/unique-rows/not-promoted/summary-closed/promoted/blocked `{summary['source_policy_expected_output_promotion_readiness_blocker_commands']}/{summary['source_policy_expected_output_promotion_readiness_blocker_schema_ready']}/{summary['source_policy_expected_output_promotion_readiness_blocker_promotion_ready']}/{summary['source_policy_expected_output_promotion_readiness_blocker_row_refs']}/{summary['source_policy_expected_output_promotion_readiness_blocker_unique_rows']}/{summary['source_policy_expected_output_promotion_readiness_blocker_not_promoted']}/{summary['source_policy_expected_output_promotion_readiness_blocker_summary_closed']}/{summary['source_policy_expected_output_promotion_readiness_blocker_summary_promoted']}/{summary['source_policy_expected_output_promotion_readiness_blocker_blocked_commands']}`.",
        f"- OC6 source-equivalent reopen-readiness audit: `{summary['oc6_source_equivalent_reopen_readiness_status']}`; rows TFE/VP/total/unable/public-code/candidate/source-equivalent/positive/local-positive/closed/search/close-now `{summary['oc6_source_equivalent_reopen_readiness_tfe_rows']}/{summary['oc6_source_equivalent_reopen_readiness_vp_rows']}/{summary['oc6_source_equivalent_reopen_readiness_rows']}/{summary['oc6_source_equivalent_reopen_readiness_unable_rows']}/{summary['oc6_source_equivalent_reopen_readiness_public_code_rows']}/{summary['oc6_source_equivalent_reopen_readiness_candidate_rows']}/{summary['oc6_source_equivalent_reopen_readiness_source_equivalent_rows']}/{summary['oc6_source_equivalent_reopen_readiness_positive_public_rows']}/{summary['oc6_source_equivalent_reopen_readiness_local_positive_rows']}/{summary['oc6_source_equivalent_reopen_readiness_closed_rows']}/{summary['oc6_source_equivalent_reopen_readiness_performs_new_public_code_search']}/{summary['oc6_source_equivalent_reopen_readiness_oc6_can_close_now']}`.",
        f"- OC6 source-equivalent reopen-readiness latest external probe: `{summary['oc6_source_equivalent_reopen_readiness_latest_external_probe_date']}/{summary['oc6_source_equivalent_reopen_readiness_latest_external_probe_count']}/{summary['oc6_source_equivalent_reopen_readiness_latest_external_probe_positive_artifact_rows']}/{summary['oc6_source_equivalent_reopen_readiness_latest_external_probe_source_policy_rows_closed']}/{summary['oc6_source_equivalent_reopen_readiness_latest_external_probe_access_limited_count']}/{summary['oc6_source_equivalent_reopen_readiness_latest_external_probe_global_absence_proved']}/{summary['oc6_source_equivalent_reopen_readiness_latest_external_probe_reopen_triggered']}`.",
        f"- Source-policy execution handoff traceability: unique RA/HI rows `{summary['source_policy_execution_handoff_unique_mapped_row_count']}/{summary['source_policy_execution_handoff_ra_hi_unique_row_count']}`; row refs `{summary['source_policy_execution_handoff_traced_command_row_reference_total']}/{summary['source_policy_execution_handoff_declared_mapped_row_reference_total']}`; mismatches/terminal/closed/promotion-ready `{summary['source_policy_execution_handoff_declared_vs_traced_mismatch_count']}/{summary['source_policy_execution_handoff_terminal_rows_with_command_refs']}/{summary['source_policy_execution_handoff_traceability_closed_rows']}/{summary['source_policy_execution_handoff_traceability_promotion_ready_rows']}`.",
        f"- Source-policy execution handoff exact approval/driver: `{summary['source_policy_execution_handoff_exact_approval_statement']}/{summary['source_policy_execution_handoff_driver']}/{summary['source_policy_execution_handoff_driver_requires_exact_approval']}/{summary['source_policy_execution_handoff_driver_does_not_authorize_execution']}/{summary['source_policy_execution_handoff_opt_in_required_command_count']}/{summary['source_policy_execution_handoff_opt_in_required_mapped_rows']}`.",
        f"- VP2024 public-code recheck: `{summary['vp2024_public_code_recheck_status']}` on `{summary['vp2024_public_code_recheck_date']}`; tree truncated `{summary['vp2024_public_code_recheck_tree_truncated']}`; paths/all-2024/keyword-hits `{summary['vp2024_public_code_recheck_tree_total_paths']}/{summary['vp2024_public_code_recheck_year2024_paths']}/{summary['vp2024_public_code_recheck_keyword_hits']}`; attempted-not-reproducible/closed `{summary['vp2024_public_code_recheck_rows_attempted_not_reproducible']}/{summary['vp2024_public_code_recheck_source_policy_rows_closed']}`; external superiority `{summary['vp2024_public_code_recheck_external_superiority_allowed']}`.",
        f"- B4 existing-artifact promotion audit: `{summary['b4_existing_promotion_audit_status']}`; candidates `{summary['b4_existing_promotion_candidate_items']}`; promotion-ready `{summary['b4_existing_promotion_ready_without_new_execution']}`; source-policy rows `{summary['b4_existing_promotion_source_policy_rows_closed']}/{summary['b4_existing_promotion_source_policy_rows_total']}`; closes B4/B7 `{summary['b4_existing_promotion_b4_closing_items']}/{summary['b4_existing_promotion_b7_closing_items']}`.",
        f"- B4 post-execution audit: `{summary['b4_post_execution_audit_status']}`; verified authorized execution `{summary['b4_post_execution_audit_verified_authorized_execution_recorded']}`; existing ready-command artifacts `{summary['b4_post_execution_audit_existing_ready_command_artifacts_present']}`; scope `{summary['b4_post_execution_audit_execution_record_scope']}`; commands `{summary['b4_post_execution_audit_ready_command_count']}`; mapped/unaddressed rows `{summary['b4_post_execution_audit_mapped_external_rows']}/{summary['b4_post_execution_audit_unaddressed_external_rows']}`; expected outputs present `{summary['b4_post_execution_audit_expected_outputs_present']}`; source-policy rows `{summary['b4_post_execution_audit_source_policy_rows_closed']}/{summary['b4_post_execution_audit_source_policy_rows_total']}`; closes B4/B7 `{summary['b4_post_execution_audit_b4_can_close_now']}/{summary['b4_post_execution_audit_b7_can_close_now']}`.",
        f"- Full source-policy row provenance audit: `{summary['full_source_policy_row_provenance_status']}`; rows/preflight/public-root/unable `{summary['full_source_policy_row_provenance_rows']}/{summary['full_source_policy_row_provenance_preflight_complete_rows']}/{summary['full_source_policy_row_provenance_public_source_root_rows']}/{summary['full_source_policy_row_provenance_unable_to_reproduce_rows']}`; closed/promotion-ready `{summary['full_source_policy_row_provenance_source_policy_closed_rows']}/{summary['full_source_policy_row_provenance_promotion_ready_rows']}`.",
        f"- Full source-policy row provenance action boundary: execution invoked `{summary['full_source_policy_row_provenance_source_policy_execution_invoked']}`; action boundary `{summary['full_source_policy_row_provenance_action_boundary']}`.",
        f"- Full source-policy row provenance handoff exact approval/driver: `{summary['full_source_policy_row_provenance_handoff_exact_approval']}/{summary['full_source_policy_row_provenance_handoff_driver']}/{summary['full_source_policy_row_provenance_handoff_driver_requires_exact']}/{summary['full_source_policy_row_provenance_handoff_driver_does_not_authorize']}/{summary['full_source_policy_row_provenance_handoff_opt_in_commands']}/{summary['full_source_policy_row_provenance_handoff_mapped_rows']}/{summary['full_source_policy_row_provenance_handoff_terminal_unable_rows']}`.",
        f"- RA/HI source-policy closeout checklist: `{summary['ra_hi_source_policy_closeout_checklist_status']}`; rows RA/HI/total `{summary['ra_hi_source_policy_closeout_ra_rows']}/{summary['ra_hi_source_policy_closeout_hi_rows']}/{summary['ra_hi_source_policy_closeout_total_rows']}`; commands/mapped `{summary['ra_hi_source_policy_closeout_ready_commands']}/{summary['ra_hi_source_policy_closeout_mapped_rows']}`; promoted/completed/external-ready `{summary['ra_hi_source_policy_closeout_promoted_rows']}/{summary['ra_hi_source_policy_closeout_completed_rows']}/{summary['ra_hi_source_policy_closeout_external_ready_rows']}`; opt-in/executed `{summary['ra_hi_source_policy_closeout_opt_in_required']}/{summary['ra_hi_source_policy_closeout_execution_invoked']}`; closes B4/B7 `{summary['ra_hi_source_policy_closeout_b4_can_close']}/{summary['ra_hi_source_policy_closeout_b7_can_close']}`.",
        f"- RA/HI source-policy output inventory: `{summary['ra_hi_source_policy_output_inventory_status']}`; commands/outputs/summaries `{summary['ra_hi_source_policy_output_inventory_command_count']}/{summary['ra_hi_source_policy_output_inventory_outputs_existing']}/{summary['ra_hi_source_policy_output_inventory_summaries_existing']}`; csv rows/HI ok/closed `{summary['ra_hi_source_policy_output_inventory_csv_data_rows']}/{summary['ra_hi_source_policy_output_inventory_hi_ok_rows']}/{summary['ra_hi_source_policy_output_inventory_closed_rows']}`.",
        f"- RA/HI source-policy promotion blocker matrix: `{summary['ra_hi_source_policy_promotion_blocker_matrix_status']}`; rows RA/HI/total `{summary['ra_hi_source_policy_promotion_blocker_matrix_ra_rows']}/{summary['ra_hi_source_policy_promotion_blocker_matrix_hi_rows']}/{summary['ra_hi_source_policy_promotion_blocker_matrix_rows']}`; public-root/no-public-code `{summary['ra_hi_source_policy_promotion_blocker_matrix_public_root_rows']}/{summary['ra_hi_source_policy_promotion_blocker_matrix_no_public_code_rows']}`; closed/not-promoted/attempted-not-reproducible `{summary['ra_hi_source_policy_promotion_blocker_matrix_closed_rows']}/{summary['ra_hi_source_policy_promotion_blocker_matrix_not_promoted_rows']}/{summary['ra_hi_source_policy_promotion_blocker_matrix_attempted_not_reproducible_rows']}`; terminal-current/future-auth-or-artifact/reproduction-complete `{summary['ra_hi_source_policy_promotion_blocker_matrix_current_evidence_terminal_rows']}/{summary['ra_hi_source_policy_promotion_blocker_matrix_future_authorization_or_artifact_rows']}/{summary['ra_hi_source_policy_promotion_blocker_matrix_reproduction_complete_rows']}`; command-mapped/output-present `{summary['ra_hi_source_policy_promotion_blocker_matrix_command_mapped_rows']}/{summary['ra_hi_source_policy_promotion_blocker_matrix_output_present_rows']}`.",
        f"- RA2021 double low-order diagnosis: `{summary['ra2021_double_low_order_diagnosis_status']}`; fine pair floor-limited `{summary['ra2021_double_low_order_fine_pair_floor_limited']}`; rows promoted `{summary['ra2021_double_low_order_rows_promoted']}`.",
        f"- HI2022 rA_half double failure diagnosis: `{summary['hi2022_ra_half_double_failure_diagnosis_status']}`; ok/failed/total `{summary['hi2022_ra_half_double_failure_rows_ok']}/{summary['hi2022_ra_half_double_failure_rows_failed']}/{summary['hi2022_ra_half_double_failure_rows_total']}`; Newton failures `{summary['hi2022_ra_half_double_failure_newton_failure_count']}`; pair orders available `{summary['hi2022_ra_half_double_failure_pair_orders_available']}`; rows promoted `{summary['hi2022_ra_half_double_failure_rows_promoted']}`.",
        f"- HI2022 rA_half double repair attempt: `{summary['hi2022_ra_half_double_repair_attempt_status']}`; target ok/failed `{summary['hi2022_ra_half_double_repair_target_ok_rows']}/{summary['hi2022_ra_half_double_repair_target_failed_rows']}`; combined rows/groups `{summary['hi2022_ra_half_double_repair_combined_ok_rows']}/{summary['hi2022_ra_half_double_repair_combined_row_count']}` and `{summary['hi2022_ra_half_double_repair_combined_complete_groups']}/{summary['hi2022_ra_half_double_repair_combined_group_count']}`; rows promoted `{summary['hi2022_ra_half_double_repair_rows_promoted']}`.",
        f"- B4 row closure-readiness ledger: `{summary['b4_row_readiness_ledger_status']}`; external rows `{summary['b4_row_readiness_external_rows']}/{summary['b4_row_readiness_expected_external_rows']}`; closed/open `{summary['b4_row_readiness_source_policy_rows_closed']}/{summary['b4_row_readiness_source_policy_rows_open']}`; command-mapped/no-command `{summary['b4_row_readiness_rows_with_launch_command_refs']}/{summary['b4_row_readiness_rows_without_launch_command_refs']}`; ready/not-ready suites `{summary['b4_row_readiness_ready_suites']}/{summary['b4_row_readiness_not_ready_suites']}`.",
        f"- B4 execution opt-in packet: `{summary['b4_execution_opt_in_packet_status']}`; opt-in required `{summary['b4_execution_opt_in_explicit_user_opt_in_required']}`; commands `{summary['b4_execution_opt_in_ready_command_count']}`; mapped/unaddressed rows `{summary['b4_execution_opt_in_mapped_external_rows']}/{summary['b4_execution_opt_in_unaddressed_external_rows']}`; source-policy rows `{summary['b4_execution_opt_in_source_policy_rows_closed_now']}/{summary['b4_execution_opt_in_source_policy_rows_total']}`.",
        f"- B4 post-execution promotion contract: `{summary['b4_post_execution_promotion_contract_schema']}` / `{summary['b4_post_execution_promotion_contract_status']}`; rows `{summary['b4_post_execution_promotion_contract_rows_closed']}/{summary['b4_post_execution_promotion_contract_rows_total']}`; ready/unaddressed `{summary['b4_post_execution_promotion_contract_ready_mapped_rows']}/{summary['b4_post_execution_promotion_contract_unaddressed_rows']}`; checks satisfied `{summary['b4_post_execution_promotion_contract_checks_satisfied_now']}`; closes B4/B7 `{summary['b4_post_execution_promotion_contract_b4_can_close_now']}/{summary['b4_post_execution_promotion_contract_b7_can_close_now']}`.",
        f"- TFE source-policy runner implemented: `{summary['tfe_source_policy_runner_implemented']}`.",
        f"- TFE public-code recheck: `{summary['tfe_public_code_recheck_status']}` on `{summary['tfe_public_code_recheck_date']}`; repo/user/code-search `{summary['tfe_public_code_recheck_github_repository_search_total_count']}/{summary['tfe_public_code_recheck_github_user_search_total_count']}/{summary['tfe_public_code_recheck_github_code_search_api_status']}`; attempted-not-reproducible/closed `{summary['tfe_public_code_recheck_rows_attempted_not_reproducible']}/{summary['tfe_public_code_recheck_source_policy_rows_closed']}`; external superiority `{summary['tfe_public_code_recheck_external_superiority_allowed']}`.",
        f"- TFE candidate/source-policy boundary sources/match/use: `{','.join(summary['tfe_candidate_source_policy_boundary_sources'])}/{summary['tfe_candidate_source_policy_boundary_sources_match']}/{summary['tfe_candidate_source_policy_allowed_use']}`.",
        f"- TFE candidate/source-policy boundary DAE/method/source rows/external-superiority: `{summary['tfe_candidate_source_policy_dae_runner_equivalent']}/{summary['tfe_candidate_source_policy_method_runner_equivalent']}/{summary['tfe_candidate_source_policy_rows_completed']}/{summary['tfe_candidate_source_policy_external_superiority_allowed']}`.",
        f"- TFE DAE runner contract gap status/missing/non-heavy/execution/ready/heavy-run: `{summary['tfe_dae_runner_contract_gap_status']}/{summary['tfe_dae_runner_contract_gap_missing_block_count']}/{len(summary['tfe_dae_runner_contract_gap_nonheavy_blocks'])}/{len(summary['tfe_dae_runner_contract_gap_execution_blocks'])}/{summary['tfe_dae_runner_contract_gap_ready_to_execute_source_policy_now']}/{summary['tfe_dae_runner_contract_gap_heavy_run_invoked']}`.",
        f"- TFE DAE runner contract accounting raw/non-heavy-terminal/effective-execution/source-rows: `{summary['tfe_dae_runner_contract_gap_block_accounting']['raw_open_contract_block_count']}/{summary['tfe_dae_runner_contract_gap_terminal_nonpromoted_block_count']}/{summary['tfe_dae_runner_contract_gap_effective_missing_block_count']}/{summary['tfe_dae_runner_contract_gap_block_accounting']['source_policy_rows_closed_by_accounting']}`.",
        f"- TFE DAE runner effective execution blocks: `{summary['tfe_dae_runner_contract_gap_effective_missing_blocks']}`.",
        f"- TFE source-policy execution preflight status/opt-in/nonheavy/execution/promote/ready: `{summary['tfe_source_policy_execution_preflight_status']}/{summary['tfe_source_policy_execution_preflight_opt_in_required']}/{summary['tfe_source_policy_execution_preflight_nonheavy_dispositioned']}/{summary['tfe_source_policy_execution_preflight_execution_block_count']}/{summary['tfe_source_policy_execution_preflight_can_promote_rows_now']}/{summary['tfe_source_policy_execution_preflight_ready_now']}`.",
        f"- TFE runner contract preflight status/entrypoints/candidate-backed/source-rows/execution-blocks: `{summary['tfe_runner_contract_preflight_status']}/{summary['tfe_runner_contract_preflight_entrypoints']}/{summary['tfe_runner_contract_preflight_candidate_backed']}/{summary['tfe_runner_contract_preflight_source_policy_rows_completed']}/{summary['tfe_runner_contract_preflight_execution_blocks']}`.",
        f"- OC12 full-archive TFE runner preflight status/entrypoints/candidate-backed/source-rows/execution-blocks: `{summary['oc12_archive_tfe_runner_contract_preflight_status']}/{summary['oc12_archive_tfe_runner_contract_preflight_entrypoints']}/{summary['oc12_archive_tfe_runner_contract_preflight_candidate_backed']}/{summary['oc12_archive_tfe_runner_contract_preflight_source_policy_rows_completed']}/{summary['oc12_archive_tfe_runner_contract_preflight_execution_blocks']}`.",
        f"- OC12 full-archive action boundary safe/opt-in/allowed/invoked/exact/commands/rows: `{summary['oc12_archive_safe_without_b4_opt_in_count']}/{summary['oc12_archive_opt_in_required_action_count']}/{summary['oc12_archive_source_policy_execution_allowed_now']}/{summary['oc12_archive_source_policy_execution_invoked']}/{summary['oc12_archive_exact_b4_opt_in_required_for_execution']}/{summary['oc12_archive_opt_in_required_command_count']}/{summary['oc12_archive_opt_in_required_mapped_external_rows']}`.",
        f"- TFE self-reproduction preflight route/reopen/source rows: `{summary['tfe_source_policy_self_reproduction_preflight_current_route']}/{summary['tfe_source_policy_self_reproduction_preflight_reopen_condition']}/{summary['tfe_source_policy_self_reproduction_preflight_source_policy_rows_completed']}`.",
        f"- TFE self-reproduction preflight blocks/ready/promote/next-actions: `{summary['tfe_source_policy_self_reproduction_preflight_execution_block_count']}/{summary['tfe_source_policy_self_reproduction_preflight_ready_now']}/{summary['tfe_source_policy_self_reproduction_preflight_can_promote_rows_now']}/{summary['tfe_source_policy_self_reproduction_required_next_action_count']}`.",
        f"- TFE DAE runner contract missing ids: `{summary['tfe_dae_runner_contract_gap_missing_block_ids']}`.",
        f"- TFE source pendulum parameter/smoke/absolute-residual/time-smoke/output/candidate friction/setup: `{summary['tfe_source_pendulum_parameter_model_implemented']}/{summary['tfe_source_pendulum_frictionless_smoke_implemented']}/{summary['tfe_source_pendulum_absolute_coordinate_dae_residual_smoke_implemented']}/{summary['tfe_source_pendulum_source_output_time_integration_smoke_implemented']}/{summary['tfe_source_pendulum_error_output_policy_encoded']}/{summary['tfe_source_pendulum_brown_mcphee_candidate_friction_law_encoded']}/{summary['tfe_source_pendulum_setup_subrequirement_closed']}`.",
        f"- TFE Brown--McPhee boundary/source-equivalent/transition/rows/block-closed: `{summary['tfe_brown_mcphee_boundary_status']}/{summary['tfe_brown_mcphee_boundary_source_code_equivalent_law']}/{summary['tfe_brown_mcphee_boundary_transition_velocity_resolved']}/{summary['tfe_brown_mcphee_boundary_rows_promoted']}/{summary['tfe_brown_mcphee_boundary_nonheavy_contract_block_closed']}`.",
        f"- TFE Brown--McPhee candidate DAE contract rows/step/source/equivalent DAE/method/source-law/monolithic: `{summary['tfe_brown_mcphee_candidate_dae_contract_rows']}/{summary['tfe_brown_mcphee_candidate_dae_contract_step_rows']}/{summary['tfe_brown_mcphee_candidate_dae_contract_source_policy_rows']}/{summary['tfe_brown_mcphee_candidate_dae_contract_equivalent_dae']}/{summary['tfe_brown_mcphee_candidate_dae_contract_equivalent_method']}/{summary['tfe_brown_mcphee_candidate_dae_contract_source_law']}/{summary['tfe_brown_mcphee_candidate_dae_contract_monolithic']}`.",
        f"- TFE Brown--McPhee candidate DAE contract finite/residual/power: `{summary['tfe_brown_mcphee_candidate_dae_contract_all_finite']}/{summary['tfe_brown_mcphee_candidate_dae_contract_residual_ok']}/{summary['tfe_brown_mcphee_candidate_dae_contract_power_nonpositive']}`.",
        f"- TFE Brown--McPhee transition-velocity sensitivity rows/contracts/source/material/equivalence-false: `{summary['tfe_brown_mcphee_transition_velocity_sensitivity_rows']}/{summary['tfe_brown_mcphee_transition_velocity_sensitivity_contract_rows']}/{summary['tfe_brown_mcphee_transition_velocity_sensitivity_source_policy_rows']}/{summary['tfe_brown_mcphee_transition_velocity_sensitivity_material']}/{summary['tfe_brown_mcphee_transition_velocity_sensitivity_equivalence_flags_false']}`.",
        f"- TFE Brown--McPhee transition-velocity max endpoint coordinate/velocity delta: `{summary['tfe_brown_mcphee_transition_velocity_sensitivity_max_coordinate_delta']:.3e}/{summary['tfe_brown_mcphee_transition_velocity_sensitivity_max_velocity_delta']:.3e}`.",
        f"- TFE Brown--McPhee source-code equivalence certificate status/available/positive/closed-block/exec/close-now: `{summary['tfe_brown_mcphee_source_code_equivalence_certificate_status']}/{summary['tfe_brown_mcphee_source_code_equivalence_certificate_available']}/{summary['tfe_brown_mcphee_source_code_equivalence_certificate_positive']}/{summary['tfe_brown_mcphee_source_code_equivalence_certificate_nonheavy_block_closed']}/{summary['tfe_brown_mcphee_source_code_equivalence_certificate_source_policy_execution_invoked']}/{summary['tfe_brown_mcphee_source_code_equivalence_certificate_can_close_now']}`.",
        f"- TFE source pendulum bounded reference-policy smoke/full T=10 source run: `{summary['tfe_source_pendulum_source_reference_solution_policy_smoke_implemented']}/{summary['tfe_source_pendulum_source_reference_solution_policy_smoke_full_T10']}`.",
        f"- TFE source pendulum full-T=10 source-reference feasibility probe: implemented/completed/source-policy rows `{summary['tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_implemented']}/{summary['tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_completed']}/{summary['tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_rows_completed']}`; source/check steps `{summary['tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_steps']}/{summary['tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_check_steps']}`; coordinate/velocity check errors `{summary['tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_coordinate_error']:.3e}/{summary['tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_velocity_error']:.3e}`.",
        f"- TFE source pendulum comparator candidate runners/Newmark/trapezoidal/TFE-m-candidate/method-equivalent/TFE m=1-3 source-policy: `{summary['tfe_source_pendulum_source_comparator_candidate_runners_implemented']}/{summary['tfe_source_pendulum_newmark_beta_candidate_runner_smoke_implemented']}/{summary['tfe_source_pendulum_trapezoidal_candidate_runner_smoke_implemented']}/{summary['tfe_source_pendulum_tfe_m1_m2_m3_candidate_runner_smoke_implemented']}/{summary['tfe_source_pendulum_source_policy_method_runner_equivalent']}/{summary['tfe_source_pendulum_tfe_m1_m2_m3_source_policy_runners_implemented']}`.",
        f"- TFE source pendulum Gauss6 candidate smoke/absolute-coordinate source-policy runner: `{summary['tfe_source_pendulum_gauss6_candidate_smoke_implemented']}/{summary['tfe_source_pendulum_gauss6_absolute_coordinate_source_policy_runner_implemented']}`.",
        f"- TFE source pendulum Gauss6 candidate rows/source-policy rows/method-equivalent: `{summary['tfe_source_pendulum_gauss6_candidate_rows']}/{summary['tfe_source_pendulum_gauss6_candidate_source_policy_rows_completed']}/{summary['tfe_source_pendulum_gauss6_candidate_method_equivalent']}`.",
        f"- TFE source pendulum unified bounded runner rows/full T=10/source-policy rows: `{summary['tfe_source_pendulum_bounded_source_policy_runner_rows']}/{summary['tfe_source_pendulum_bounded_source_policy_runner_full_T10']}/{summary['tfe_source_pendulum_bounded_source_policy_runner_source_policy_rows_completed']}`.",
        f"- TFE source pendulum active-B2 candidate rows/full T=10/source-policy rows: `{summary['tfe_source_pendulum_active_b2_candidate_row_count']}/{summary['tfe_source_pendulum_active_b2_candidate_row_smoke_full_T10']}/{summary['tfe_source_pendulum_active_b2_source_policy_rows_completed']}`.",
        f"- TFE source pendulum active-B2 source-reference full-T10 probe: implemented/fullT10/reference-invoked/source-policy rows/finite/residual-ok/method-equivalent `{summary['tfe_source_pendulum_active_b2_source_reference_full_T10_probe_implemented']}/{summary['tfe_source_pendulum_active_b2_source_reference_full_T10_probe_full_T10']}/{summary['tfe_source_pendulum_active_b2_source_reference_full_T10_probe_reference_invoked']}/{summary['tfe_source_pendulum_active_b2_source_reference_full_T10_probe_source_policy_rows']}/{summary['tfe_source_pendulum_active_b2_source_reference_full_T10_probe_finite_rows']}/{summary['tfe_source_pendulum_active_b2_source_reference_full_T10_probe_residual_ok_rows']}/{summary['tfe_source_pendulum_active_b2_source_reference_full_T10_probe_method_equivalent']}`.",
        f"- TFE full-T10 absolute DAE-lift diagnostic: `{summary['tfe_full_t10_absolute_dae_lift_status']}`; completed/methods/metric-rows/step-residual-rows `{summary['tfe_full_t10_absolute_dae_lift_completed']}/{summary['tfe_full_t10_absolute_dae_lift_method_count']}/{summary['tfe_full_t10_absolute_dae_lift_metric_rows']}/{summary['tfe_full_t10_absolute_dae_lift_step_residual_rows']}`; reference-invoked/source-policy rows/monolithic/equivalent `{summary['tfe_full_t10_absolute_dae_lift_source_reference_invoked']}/{summary['tfe_full_t10_absolute_dae_lift_source_policy_rows_completed']}/{summary['tfe_full_t10_absolute_dae_lift_monolithic']}/{summary['tfe_full_t10_absolute_dae_lift_equivalent']}`.",
        f"- TFE endpoint boundary certificate: `{summary['tfe_endpoint_boundary_certificate_status']}`; proved/exact/overrun/source rows/full-policy/exact-T-equivalent `{summary['tfe_endpoint_boundary_literal_overrun_bound_proved']}/{summary['tfe_endpoint_boundary_literal_exact_T_rows']}/{summary['tfe_endpoint_boundary_literal_overrun_rows']}/{summary['tfe_endpoint_boundary_source_policy_rows_completed']}/{summary['tfe_endpoint_boundary_full_T10_policy_resolved']}/{summary['tfe_endpoint_boundary_exact_T_error_sampling_equivalent']}`.",
        f"- TFE full-T10 endpoint policy closure certificate status/available/positive/closed-block/exec/close-now: `{summary['tfe_full_T10_endpoint_policy_closure_certificate_status']}/{summary['tfe_full_T10_endpoint_policy_closure_certificate_available']}/{summary['tfe_full_T10_endpoint_policy_closure_certificate_positive']}/{summary['tfe_full_T10_endpoint_policy_closure_certificate_nonheavy_block_closed']}/{summary['tfe_full_T10_endpoint_policy_closure_certificate_source_policy_execution_invoked']}/{summary['tfe_full_T10_endpoint_policy_closure_certificate_can_close_now']}`.",
        f"- TFE source-grid policy/source-text endpoint audit: `{summary['tfe_source_grid_policy_resolved_for_full_T10']}/{summary['tfe_source_grid_integer_step_incompatible_rows']}` and exact-T subset `{summary['tfe_source_grid_policy_resolved_for_exact_T_compatible_rows']}/{summary['tfe_source_grid_exact_T_compatible_rows_endpoint_convention_resolved']}/{summary['tfe_source_grid_endpoint_incompatible_rows_requiring_policy']}` and source-text `{summary['tfe_source_grid_source_text_available']}/{summary['tfe_source_grid_source_text_anchor_count']}/{summary['tfe_source_grid_algorithm_literal_fixed_h']}/{summary['tfe_source_grid_endpoint_convention_resolved_for_error_sampling']}`.",
        f"- TFE endpoint sensitivity diagnostic: `{summary['tfe_endpoint_sensitivity_status']}`; methods/policies/raw rows `{summary['tfe_endpoint_sensitivity_method_count']}/{summary['tfe_endpoint_sensitivity_policy_count']}/{summary['tfe_endpoint_sensitivity_raw_row_count']}`; source-policy rows `{summary['tfe_endpoint_sensitivity_source_policy_rows_completed']}`; superiority allowed `{summary['tfe_endpoint_sensitivity_external_superiority_claim_allowed']}`.",
        f"- Direct PC2 proof gap closed: `{summary['direct_pc2_proof_gap_closed']}`.",
        f"- Direct proof gap scope: `{summary['proof_gap_closed_scope']}`.",
        f"- Direct proof gap reading rule: {summary['proof_gap_closed_reading_rule']}",
        f"- Schema-only compatibility key `proof_gap_closed` retained: `{summary['proof_gap_closed']}`; reader-facing proof status should use `direct_pc2_proof_gap_closed`.",
        f"- Proof theorem/manuscript traceability: labels/boundary/mapped `{summary['proof_theorem_statement_labels_present']}/{summary['proof_theorem_statement_boundary_present']}/{summary['proof_manuscript_traceability_mapped']}`; dependency/dynamic/primitive/nonpromotion `{summary['proof_manuscript_traceability_dependency_graph_present']}/{summary['proof_manuscript_traceability_dynamic_matrix_present']}/{summary['proof_manuscript_traceability_primitive_lane_boundary_present']}/{summary['proof_manuscript_traceability_residual_nonpromotion_present']}`.",
        f"- Proof theorem no-promotion boundary: eta condition/closure `{summary['proof_theorem_statement_eta_condition_retained']}/{summary['proof_theorem_statement_eta_evidence_closed']}`; fixed-tolerance proof `{summary['proof_theorem_statement_fixed_tolerance_asymptotic_proof']}`; residual/source-policy-full-TFE not promoted `{summary['proof_theorem_statement_residual_to_error_not_promoted']}/{summary['proof_theorem_statement_source_policy_or_full_tfe_not_promoted']}`; no-state-change `{summary['proof_manuscript_traceability_no_state_change']}`.",
        f"- Proof-claim theorem traceability: label `{summary['proof_claim_traceability_theorem_label']}`; labels/boundary/mapped `{summary['proof_claim_traceability_theorem_labels_present']}/{summary['proof_claim_traceability_theorem_boundary_present']}/{summary['proof_claim_traceability_theorem_claims_mapped']}`; dependency/table/dynamic `{summary['proof_claim_traceability_dependency_graph_present']}/{summary['proof_claim_traceability_table_present']}/{summary['proof_claim_traceability_dynamic_theorem_matrix_present']}`.",
        f"- Proof-claim theorem no-promotion boundary: primitive/residual `{summary['proof_claim_traceability_primitive_lane_boundary_present']}/{summary['proof_claim_traceability_residual_nonpromotion_present']}`; eta condition/closure/fixed proof `{summary['proof_claim_traceability_eta_condition_retained']}/{summary['proof_claim_traceability_eta_evidence_closed']}/{summary['proof_claim_traceability_fixed_tolerance_asymptotic_proof']}`; residual/source-policy-full-TFE not promoted `{summary['proof_claim_traceability_residual_to_error_not_promoted']}/{summary['proof_claim_traceability_source_policy_or_full_tfe_not_promoted']}`; no-state-change `{summary['proof_claim_traceability_no_state_change']}`.",
        f"- Proof-claim P7 output nonclaim/residual-to-error boundary: `{summary['proof_claim_traceability_p7_retained_nonpromotion_boundary_present']}`.",
        f"- Proof-claim B1 closure-scope boundary: `{summary['proof_claim_traceability_b1_closure_scope_boundary_present']}`.",
        f"- Proof-claim P6 solver-scope boundary: `{summary['proof_claim_traceability_p6_solver_scope_boundary_present']}`.",
        f"- Proof-claim P1/P2 compact-tube boundary: `{summary['proof_claim_traceability_p1p2_compact_tube_boundary_present']}`.",
        f"- Proof-claim P3/P4 implementation-defect boundary: `{summary['proof_claim_traceability_p3p4_implementation_boundary_present']}`.",
        f"- Proof-claim P5 direct-route boundary: `{summary['proof_claim_traceability_p5_direct_route_boundary_present']}`.",
        f"- Proof-claim proof-causality ledger: `{summary['proof_claim_traceability_proof_causality_ledger_present']}`.",
        f"- Proof-claim direct-route anti-circularity ledger: `{summary['proof_claim_traceability_direct_route_anticircularity_ledger_present']}`.",
        f"- Proof-claim theorem-interface satisfaction ledger: `{summary['proof_claim_traceability_p_interface_satisfaction_ledger_present']}`.",
        f"- Proof-claim P7 residual-to-error obligation ledger: `{summary['proof_claim_traceability_p7_residual_to_error_ledger_present']}`.",
        f"- Proof-claim theorem-use rule: `{summary['proof_claim_traceability_theorem_use_rule_present']}`.",
        f"- Proof-claim quantifier/domain ledger: `{summary['proof_claim_traceability_quantifier_domain_ledger_present']}`.",
        f"- Proof-claim local-to-global transfer ledger: `{summary['proof_claim_traceability_local_global_transfer_ledger_present']}`.",
        f"- Proof-claim objective-completion boundary: `{summary['proof_claim_traceability_objective_completion_boundary_present']}`.",
        f"- Proof-claim constant-dependency ledger: `{summary['proof_claim_traceability_constant_dependency_ledger_present']}`.",
        f"- Proof-claim theorem dependency consumption ledger: `{summary['proof_claim_traceability_theorem_dependency_consumption_ledger_present']}`.",
        f"- Proof-claim accepted-branch consistency ledger: `{summary['proof_claim_traceability_branch_consistency_ledger_present']}`.",
        f"- Proof-claim implementation-route/oracle separation ledger: `{summary['proof_claim_traceability_implementation_route_oracle_ledger_present']}`.",
        f"- Proof-claim nonlinear-solver scale ledger: `{summary['proof_claim_traceability_nonlinear_solver_scale_ledger_present']}`.",
        f"- Proof-claim local-defect decomposition ledger: `{summary['proof_claim_traceability_local_defect_decomposition_ledger_present']}`.",
        f"- Proof-claim theorem output scope ledger: `{summary['proof_claim_traceability_theorem_output_scope_ledger_present']}`.",
        f"- Proof-claim reporting-map/norm-equivalence ledger: `{summary['proof_claim_traceability_reporting_map_ledger_present']}`.",
        f"- Proof-claim remaining theorem-boundary partition: `{summary['proof_claim_traceability_remaining_boundary_status']}`; satisfied IDs `{','.join(summary['proof_claim_traceability_submission_satisfied_assumption_ids'])}`; retained theorem-interface IDs `{','.join(summary['proof_claim_traceability_retained_theorem_interface_ids'])}`; open output-boundary IDs `{','.join(summary['proof_claim_traceability_open_nonpromotion_boundary_ids'])}`; global boundaries `{','.join(summary['proof_claim_traceability_remaining_global_boundaries'])}`.",
        f"- Strict proof-writing submission boundary: `{summary['strict_proof_writing_submission_boundary_status']}`; card `{summary['strict_proof_writing_card_status']}`; package boundary `{summary['strict_proof_writing_package_boundary_status']}`; blockers `{summary['strict_proof_writing_objective_blockers_retained']}`; submission ready `{summary['strict_proof_writing_submission_ready']}`.",
        f"- Strict proof-writing reader-facing manuscript/PDF boundary: `{summary['strict_proof_writing_reader_facing_manuscript_boundary_present']}`.",
        f"- Strict proof-writing P7 output nonclaim/residual-to-error boundary: `{summary['strict_proof_writing_p7_retained_nonpromotion_boundary_present']}`.",
        f"- Strict proof-writing B1 closure-scope boundary: `{summary['strict_proof_writing_b1_closure_scope_boundary_present']}`.",
        f"- Strict proof-writing B1 AD-expanded closure ledger/cells: `{summary['strict_proof_writing_b1_ad_expanded_closure_ledger_present']}` / `{summary['strict_proof_writing_b1_ad_expanded_symbolic_oracle_closed_cells']}`.",
        f"- Strict proof-writing P6 solver-scope boundary: `{summary['strict_proof_writing_p6_solver_scope_boundary_present']}`.",
        f"- Strict proof-writing P1/P2 compact-tube boundary: `{summary['strict_proof_writing_p1p2_compact_tube_boundary_present']}`.",
        f"- Strict proof-writing P3/P4 implementation-defect boundary: `{summary['strict_proof_writing_p3p4_implementation_boundary_present']}`.",
        f"- Strict proof-writing P5 direct-route boundary: `{summary['strict_proof_writing_p5_direct_route_boundary_present']}`.",
        f"- Strict proof-writing proof-causality ledger: `{summary['strict_proof_writing_proof_causality_ledger_present']}`.",
        f"- Strict proof-writing direct-route anti-circularity ledger: `{summary['strict_proof_writing_direct_route_anticircularity_ledger_present']}`.",
        f"- Strict proof-writing theorem-interface satisfaction ledger: `{summary['strict_proof_writing_p_interface_satisfaction_ledger_present']}`.",
        f"- Strict proof-writing P7 residual-to-error obligation ledger: `{summary['strict_proof_writing_p7_residual_to_error_ledger_present']}`.",
        f"- Strict proof-writing theorem-use rule: `{summary['strict_proof_writing_theorem_use_rule_present']}`.",
        f"- Strict proof-writing quantifier/domain ledger: `{summary['strict_proof_writing_quantifier_domain_ledger_present']}`.",
        f"- Strict proof-writing local-to-global transfer ledger: `{summary['strict_proof_writing_local_global_transfer_ledger_present']}`.",
        f"- Strict proof-writing objective-completion boundary: `{summary['strict_proof_writing_objective_completion_boundary_present']}`.",
        f"- Strict proof-writing constant-dependency ledger: `{summary['strict_proof_writing_constant_dependency_ledger_present']}`.",
        f"- Strict proof-writing theorem dependency consumption ledger: `{summary['strict_proof_writing_theorem_dependency_consumption_ledger_present']}`.",
        f"- Strict proof-writing accepted-branch consistency ledger: `{summary['strict_proof_writing_branch_consistency_ledger_present']}`.",
        f"- Strict proof-writing implementation-route/oracle separation ledger: `{summary['strict_proof_writing_implementation_route_oracle_ledger_present']}`.",
        f"- Strict proof-writing nonlinear-solver scale ledger: `{summary['strict_proof_writing_nonlinear_solver_scale_ledger_present']}`.",
        f"- Strict proof-writing local-defect decomposition ledger: `{summary['strict_proof_writing_local_defect_decomposition_ledger_present']}`.",
        f"- Strict proof-writing theorem output scope ledger: `{summary['strict_proof_writing_theorem_output_scope_ledger_present']}`.",
        f"- Strict proof-writing reporting-map/norm-equivalence ledger: `{summary['strict_proof_writing_reporting_map_ledger_present']}`.",
        f"- Strict proof-writing safe/forbidden claims: safe `{summary['strict_proof_writing_safe_reader_claim']}`; forbidden `{','.join(summary['strict_proof_writing_forbidden_reader_claims'])}`; global boundaries `{','.join(summary['strict_proof_writing_global_boundaries_retained'])}`.",
        f"- Strict proof-writing no-promotion locks: residual-to-error `{summary['strict_proof_writing_residual_to_error_not_promoted']}`; source-policy/full-TFE package `{summary['strict_proof_writing_source_policy_full_tfe_not_promoted']}`.",
        f"- Proof-claim manuscript anchor map: `{summary['proof_claim_traceability_manuscript_anchor_map_present']}`; label anchors `{summary['proof_claim_traceability_manuscript_anchor_label_count']}`; theorem-interface/P7-output-boundary anchors `{summary['proof_claim_traceability_theorem_assumption_anchor_count']}`; IDs `{','.join(summary['proof_claim_traceability_theorem_assumption_anchor_ids'])}`.",
        f"- Proof-closure manuscript anchor map: `{summary['proof_closure_manuscript_anchor_map_present']}`; label anchors `{summary['proof_closure_manuscript_anchor_label_count']}`; theorem-interface/P7-output-boundary anchors `{summary['proof_closure_theorem_assumption_anchor_count']}`; IDs `{','.join(summary['proof_closure_theorem_assumption_anchor_ids'])}`; proof-claim map match `{summary['proof_closure_proof_claim_anchor_maps_match']}`.",
        "- Reader-facing theorem-interface split: theorem interfaces `P1--P6`; P7 is an output nonclaim/residual-to-error boundary anchor, not a theorem premise.",
        f"- Proof anchor evidence sources: contract `{','.join(summary['proof_contract_anchor_evidence_sources'])}`; style `{','.join(summary['proof_style_anchor_evidence_sources'])}`; strict `{','.join(summary['strict_proof_anchor_evidence_sources'])}`; source match `{summary['proof_anchor_evidence_sources_match']}`.",
        f"- Newton-Euler obligation coverage matrix/links/complete rows/proof-closure-advanced: `{summary['newton_euler_obligation_coverage_matrix_complete']}/{summary['newton_euler_row_obligation_links']}/{summary['newton_euler_rows_with_complete_obligation_sets']}/{summary['newton_euler_obligation_coverage_proof_closure_advanced']}`.",
        f"- Minimal reproducibility candidate/status/files/Python-files/Python-lines/size-ok/replay-only/runner-centered: `{summary['minimal_reproducibility_candidate_present']}/{summary['minimal_reproducibility_candidate_status']}/{summary['minimal_reproducibility_candidate_file_count']}/{summary['minimal_reproducibility_candidate_python_file_count']}/{summary['minimal_reproducibility_candidate_python_lines']}/{summary['minimal_reproducibility_candidate_code_size_ok']}/{summary['minimal_reproducibility_candidate_replay_only']}/{summary['minimal_reproducibility_candidate_runner_centered']}`.",
        f"- Local accepted-row runner companion/status/rows/Python-lines/source-policy/full-source-ready: `{summary['local_accepted_runner_companion_launcher_passed']}/{summary['local_accepted_runner_companion_status']}/{summary['local_accepted_runner_companion_local_rows']}/{summary['local_accepted_runner_companion_python_lines']}/{summary['local_accepted_runner_companion_source_policy_rows_closed']}/{summary['local_accepted_runner_companion_source_policy_rows_total']}/{summary['local_accepted_runner_companion_full_source_policy_ready']}`.",
        f"- Narrowed reproducibility package/status/ready/source-policy/full-source-ready: `{summary['narrowed_reproducibility_package_audit_status']}/{summary['narrowed_claim_reproducibility_package_ready']}/{summary['narrowed_reproducibility_package_source_policy_rows_closed']}/{summary['narrowed_reproducibility_package_source_policy_rows_total']}/{summary['narrowed_reproducibility_package_full_source_policy_runner_ready']}`.",
        f"- Narrowed repro code archive/status/entries/Python/source-policy/full-source-ready/submission-ready: `{summary['narrowed_repro_code_archive_status']}/{summary['narrowed_repro_code_archive_entry_count']}/{summary['narrowed_repro_code_archive_python_files']}/{summary['narrowed_repro_code_archive_python_lines']}/{summary['narrowed_repro_code_archive_source_policy_rows_closed']}/{summary['narrowed_repro_code_archive_source_policy_rows_total']}/{summary['narrowed_repro_code_archive_full_source_policy_runner_ready']}/{summary['narrowed_repro_code_archive_submission_ready']}`.",
        f"- Narrowed archive boundary/status/scope/source-policy/use/execution/exact: `{summary['narrowed_archive_boundary_status']}/{summary['narrowed_archive_boundary_scope']}/{summary['narrowed_archive_boundary_source_policy_closed_ratio']}/{summary['narrowed_archive_boundary_current_archive_usable_as_full_source_policy_runner_archive']}/{summary['narrowed_archive_boundary_source_policy_execution_allowed_now']}/{summary['narrowed_archive_boundary_exact_b4_opt_in_required_for_execution']}`.",
        f"- Narrowed archive boundary blockers/status/closure/effects: `{summary['narrowed_archive_boundary_blocking_ids']}/{summary['narrowed_archive_boundary_blocker_status_by_id']}/{summary['narrowed_archive_boundary_closure_allowed_by_id']}/{summary['narrowed_archive_boundary_archive_effect_by_id']}`.",
        f"- Narrowed archive boundary next actions by blocker: `{summary['narrowed_archive_boundary_blocker_next_actions_by_id']}`.",
        f"- Narrowed archive boundary required-to-close by blocker: `{summary['narrowed_archive_boundary_blocker_required_to_close_by_id']}`.",
        f"- Narrowed archive boundary safe next actions by blocker: `{summary['narrowed_archive_boundary_blocker_safe_next_actions_by_id']}`.",
        f"- Narrowed archive boundary opt-in required actions by blocker: `{summary['narrowed_archive_boundary_blocker_opt_in_required_actions_by_id']}`.",
        f"- Narrowed archive boundary safe/opt-in actions/source artifacts: `{summary['narrowed_archive_boundary_safe_action_ids']}/{summary['narrowed_archive_boundary_opt_in_action_ids']}/{summary['narrowed_archive_boundary_source_artifacts']}`.",
        f"- Narrowed repro code archive handoff exact approval/driver: `{summary['narrowed_repro_code_archive_handoff_exact_approval']}/{summary['narrowed_repro_code_archive_handoff_driver']}/{summary['narrowed_repro_code_archive_handoff_driver_requires_exact']}/{summary['narrowed_repro_code_archive_handoff_driver_does_not_authorize']}/{summary['narrowed_repro_code_archive_handoff_opt_in_commands']}/{summary['narrowed_repro_code_archive_handoff_mapped_rows']}`.",
        f"- Minimal submission code dependency boundary: `{summary['minimal_submission_code_dependency_boundary_status']}`; ready `{summary['minimal_reproducible_submission_code_ready']}`; safe use `{summary['minimal_submission_code_dependency_safe_use']}`; primary package allowed `{summary['minimal_submission_code_dependency_primary_allowed']}`.",
        f"- Minimal submission code dependency blockers/source rows: `{summary['minimal_submission_code_dependency_blockers']}`; upstream gates `{','.join(minimal_submission_code_dependency_boundary['blocking_upstream_gates'])}`; source-policy `{minimal_submission_code_dependency_boundary['source_policy_rows_closed']}/{minimal_submission_code_dependency_boundary['source_policy_rows_total']}`; narrowed archive source-policy `{minimal_submission_code_dependency_boundary['narrowed_archive_source_policy_rows_closed']}/{minimal_submission_code_dependency_boundary['narrowed_archive_source_policy_rows_total']}`.",
        f"- Runner-centered audit/status/source-lines: `{summary['runner_centered_audit_status']}/{summary['runner_centered_existing_source_lines']}`.",
        (
            "- Local accepted-row runner/full source-policy runner ready: "
            f"`{summary['local_runner_centered_candidate_ready']}/"
            f"{summary['full_source_policy_runner_package_ready']}`."
        ),
        f"- Runner adapter/status/Python-lines: `{summary['runner_adapter_candidate_status']}/{summary['runner_adapter_python_lines']}`.",
        f"- Runner adapter closed-loop local replay rows/models: `{summary['runner_adapter_closed_loop_local_rows']}` / `{summary['runner_adapter_closed_loop_local_models']}`.",
        f"- Runner adapter closed-loop replay outputs: `{summary['runner_adapter_closed_loop_local_rows_summary_present']}`.",
        f"- Self-contained runner extraction/status/symbols/symbol-lines: `{summary['self_contained_runner_extraction_plan_status']}/{summary['self_contained_runner_target_symbol_count']}/{summary['self_contained_runner_target_symbol_lines']}`.",
        (
            "- Self-contained local accepted-row/full source-policy/B6 narrowed/full-source-prose ready: "
            f"`{summary['local_accepted_rows_self_contained_runner_ready']}/"
            f"{summary['full_source_policy_self_contained_runner_ready']}/"
            f"{summary['b6_final_prose_pass_ready']}/"
            f"{summary['full_source_policy_b6_prose_ready']}`."
        ),
        f"- B6 closed-loop extraction audit/status/source-files/symbols/ready: `{summary['b6_closed_loop_extraction_audit_status']}/{summary['b6_closed_loop_extraction_target_source_files']}/{summary['b6_closed_loop_extraction_target_symbols']}/{summary['b6_closed_loop_extraction_ready']}`.",
        f"- Compact closed-loop candidate/status/rows/Python-lines/line-limit-ok: `{summary['compact_closed_loop_candidate_status']}/{summary['compact_closed_loop_candidate_rows']}/{summary['compact_closed_loop_candidate_python_lines']}/{summary['compact_closed_loop_candidate_line_limit_ok']}`.",
        f"- P1 local runner audit/status/ready/v047-lines/closure-lines: `{p1_local_runner_audit.get('status')}/{p1_local_runner_audit.get('p1_local_single_double_ready')}/{p1_local_runner_audit.get('v047_source_python_lines')}/{p1_local_runner_audit.get('v047_primary_recursive_internal_dependency_lines')}`.",
        f"- P1 single-runner candidate/status/rows/position-order/velocity-order: `{summary['p1_single_runner_candidate_ready']}/{summary['p1_single_runner_candidate_rows']}/{summary['p1_single_runner_candidate_position_order']}/{summary['p1_single_runner_candidate_velocity_order']}`.",
        f"- P1 double-runner candidate/status/rows/position-order/velocity-order: `{summary['p1_double_runner_candidate_ready']}/{summary['p1_double_runner_candidate_rows']}/{summary['p1_double_runner_candidate_position_order']}/{summary['p1_double_runner_candidate_velocity_order']}`.",
        f"- Human-runnable local evidence examples/self-contained/replay-only: `{summary['human_runnable_local_evidence_examples']}` / `{summary['human_runnable_self_contained_local_examples']}` / `{summary['human_runnable_replay_only_local_examples']}`.",
        f"- Human-runnable four-example local evidence/self-contained simulation: `{summary['human_runnable_four_example_local_evidence_available']}/{summary['human_runnable_four_example_self_contained_simulation_ready']}`.",
        f"- B6 four-example local evidence runner: `{summary['b6_four_example_local_evidence_runner_passed']}`; rows `{summary['b6_four_example_local_rows']}`; self-contained/replay-only `{summary['b6_four_example_self_contained_examples']}/{summary['b6_four_example_replay_only_examples']}`; source-policy rows `{summary['b6_four_example_source_policy_rows_closed']}/{summary['b6_four_example_source_policy_rows_total']}`.",
        f"- Code-bloat risk for submission: `{summary['code_bloat_risk_for_submission']}`.",
        f"- Objective complete/blocking open: `{summary['objective_complete']}/{summary['objective_blocking_open_count']}`.",
        "",
        "## Package Layers",
        "",
        "| layer | status | role |",
        "|---|---|---|",
    ]
    for layer in package_layers:
        lines.append(f"| `{layer['id']}` | `{layer['status']}` | {layer['name']} |")

    lines.extend(
        [
            "",
            "## Missing Components",
            "",
            "| id | status | required to close |",
            "|---|---|---|",
        ]
    )
    for item in missing_components:
        lines.append(f"| `{item['id']}` | `{item['status']}` | {item['required_to_close']} |")

    lines.extend(
        [
            "",
            "## Candidate File Set",
            "",
            "| path | layer | status | minimal | exists |",
            "|---|---|---|---:|---:|",
        ]
    )
    for item in files:
        lines.append(
            f"| `{item['path']}` | `{item['layer']}` | `{item['status']}` | "
            f"`{item['include_in_minimal_submission_package']}` | `{item['exists']}` |"
        )

    lines.extend(
        [
            "",
            "Reading rule: this manifest is a shrink target, not a claim upgrade. "
            "It keeps the paper table and traceability reusable while preventing the "
            "current research/audit repository from being mistaken for a minimal "
            "submission-ready reproducibility package.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("cmame_reproducibility_package_manifest=written")
    print(f"status={manifest['status']}")
    print(f"candidate_files={manifest['candidate_existing_file_count']}/{manifest['candidate_file_count']}")
    print(f"source_policy_closed={summary['source_policy_closed_rows']}/{summary['source_policy_total_rows']}")
    print(f"tfe_runner={summary['tfe_source_policy_runner_implemented']}")


if __name__ == "__main__":
    main()
