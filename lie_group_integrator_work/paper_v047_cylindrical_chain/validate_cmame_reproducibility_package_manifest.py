#!/usr/bin/env python3
"""Validate the CMAME reproducibility-package boundary manifest."""

from __future__ import annotations

import json
import sys
from pathlib import Path


PAPER = Path(__file__).resolve().parent
EXPECTED_OC6_REOPEN_LATEST_EXTERNAL_PROBE = "2026-06-21/9/0/0/4/False/False"


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


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


def main() -> int:
    checks = Checks()
    try:
        manifest = read_json(PAPER / "CMAME_REPRODUCIBILITY_PACKAGE_MANIFEST.json")
        manifest_md = read_text(PAPER / "CMAME_REPRODUCIBILITY_PACKAGE_MANIFEST.md")
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
        source_policy_reopen_monitor = read_json(
            PAPER / "SOURCE_POLICY_REOPEN_CONDITION_MONITOR_20260620.json"
        )
        expected_command_traceability = b4_execution_handoff.get(
            "command_row_traceability", {}
        ).get("summary", {})
        tfe_spec = read_json(PAPER / "TFE_SOURCE_POLICY_SPEC.json")
        tfe = read_json(PAPER / "TFE_SOURCE_POLICY_ROW_AUDIT.json")
        tfe_model = read_json(PAPER / "TFE_SOURCE_PENDULUM_MODEL_AUDIT.json")
        tfe_dae_gap = read_json(PAPER / "TFE_DAE_RUNNER_CONTRACT_GAP_AUDIT.json")
        tfe_runner_contract_preflight = read_json(
            PAPER / "TFE_RUNNER_CONTRACT_PREFLIGHT_CERTIFICATE.json"
        )
        tfe_self_reproduction_attempt_certificate = read_json(
            PAPER / "TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.json"
        )
        tfe_public_code_recheck = read_json(PAPER / "TFE_PUBLIC_CODE_RECHECK_20260613.json")
        vp2024_public_code_recheck = read_json(PAPER / "VP2024_PUBLIC_CODE_RECHECK_20260613.json")
        source_policy_public_code_refresh = read_json(PAPER / "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.json")
        source_policy_public_code_refresh_latest = read_json(PAPER / "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.json")
        full_source_runner_gap = read_json(PAPER / "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json")
        tfe_brown_mcphee_boundary = read_json(PAPER / "TFE_BROWN_MCPHEE_SOURCE_LAW_BOUNDARY_AUDIT.json")
        tfe_brown_mcphee_certificate = read_json(
            PAPER / "TFE_BROWN_MCPHEE_SOURCE_CODE_EQUIVALENCE_CERTIFICATE.json"
        )
        tfe_full_t10_absolute = read_json(PAPER / "TFE_FULL_T10_ABSOLUTE_DAE_LIFT_SUMMARY.json")
        tfe_endpoint_boundary = read_json(PAPER / "TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.json")
        tfe_endpoint_certificate = read_json(PAPER / "TFE_FULL_T10_ENDPOINT_POLICY_CLOSURE_CERTIFICATE.json")
        tfe_endpoint_sensitivity = read_json(PAPER / "TFE_ENDPOINT_POLICY_SENSITIVITY_AUDIT.json")
        objective_completion = read_json(PAPER / "OBJECTIVE_COMPLETION_AUDIT.json")
        proof = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
        proof_claim_traceability = read_json(PAPER / "PROOF_CLAIM_TRACEABILITY_AUDIT.json")
        minimal_candidate_source = read_json(PAPER / "CMAME_MINIMAL_REPRODUCIBILITY_CANDIDATE_MANIFEST.json")
        runner_adapter_source = read_json(PAPER / "CMAME_RUNNER_ADAPTER_CANDIDATE_MANIFEST.json")
        runner_centered_audit_source = read_json(PAPER / "CMAME_RUNNER_CENTERED_REPRODUCIBILITY_AUDIT.json")
        p1_local_runner_audit_source = read_json(PAPER / "CMAME_P1_LOCAL_RUNNER_EXTRACTION_AUDIT.json")
        extraction_plan_source = read_json(PAPER / "CMAME_SELF_CONTAINED_RUNNER_EXTRACTION_PLAN.json")
        b6_local_evidence_source = read_json(PAPER / "B6_FOUR_EXAMPLE_LOCAL_EVIDENCE_SUMMARY.json")
        closed_loop_audit_source = read_json(PAPER / "B6_CLOSED_LOOP_SELF_CONTAINED_EXTRACTION_AUDIT.json")
        closed_loop_candidate_source = read_json(PAPER / "CMAME_CLOSED_LOOP_LOCAL_RUNNER_CANDIDATE_MANIFEST.json")
        local_runner_companion_source = read_json(PAPER / "CMAME_LOCAL_ACCEPTED_RUNNER_COMPANION_MANIFEST.json")
        narrowed_repro_audit_source = read_json(PAPER / "CMAME_NARROWED_REPRODUCIBILITY_PACKAGE_AUDIT.json")
        narrowed_repro_code_archive_source = read_json(PAPER / "CMAME_NARROWED_REPRO_CODE_ARCHIVE_MANIFEST.json")
        p1_single_candidate_source = read_json(
            PAPER / "cmame_p1_single_runner_candidate" / "results" / "single_pendulum_summary.json"
        )
        p1_double_candidate_source = read_json(
            PAPER / "cmame_p1_double_runner_candidate" / "results" / "double_pendulum_summary.json"
        )
    except Exception as exc:  # noqa: BLE001
        print(f"cmame reproducibility package manifest validation: FAIL\n- {exc}")
        return 1

    result_checks = review.get("result_checks", {})
    code_checks = review.get("code_hygiene_checks", {})
    external_checks = review.get("external_checks", {})
    proof_checks = review.get("proof_checks", {})
    summary = manifest.get("summary", {})
    objective_summary = objective_completion.get("summary", {})
    oc12_archive_tfe_preflight = (
        f"{objective_summary.get('full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_status')}/"
        f"{objective_summary.get('full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_entrypoints')}/"
        f"{objective_summary.get('full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_candidate_backed')}/"
        f"{objective_summary.get('full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_source_policy_rows_completed')}/"
        f"{objective_summary.get('full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_execution_blocks')}"
    )
    oc12_archive_action_boundary = (
        f"{objective_summary.get('full_source_policy_runner_archive_gap_safe_without_b4_opt_in_count')}/"
        f"{objective_summary.get('full_source_policy_runner_archive_gap_opt_in_required_action_count')}/"
        f"{objective_summary.get('full_source_policy_runner_archive_gap_source_policy_execution_allowed_now')}/"
        f"{objective_summary.get('full_source_policy_runner_archive_gap_source_policy_execution_invoked')}/"
        f"{objective_summary.get('full_source_policy_runner_archive_gap_exact_b4_opt_in_required_for_execution')}/"
        f"{objective_summary.get('full_source_policy_runner_archive_gap_opt_in_required_command_count')}/"
        f"{objective_summary.get('full_source_policy_runner_archive_gap_opt_in_required_mapped_external_rows')}"
    )
    oc6_reopen_latest_external_probe = (
        f"{oc6_source_equivalent_reopen_readiness_audit.get('latest_external_probe_date_checked')}/"
        f"{oc6_source_equivalent_reopen_readiness_audit.get('latest_external_probe_count')}/"
        f"{oc6_source_equivalent_reopen_readiness_audit.get('latest_external_probe_positive_public_code_artifact_rows')}/"
        f"{oc6_source_equivalent_reopen_readiness_audit.get('latest_external_probe_source_policy_rows_closed')}/"
        f"{oc6_source_equivalent_reopen_readiness_audit.get('latest_external_probe_access_limited_count')}/"
        f"{oc6_source_equivalent_reopen_readiness_audit.get('latest_external_probe_global_absence_proved')}/"
        f"{oc6_source_equivalent_reopen_readiness_audit.get('latest_external_probe_source_policy_reopen_triggered')}"
    )
    expected_archive_action_boundary = {
        "safe_without_b4_opt_in_count": 4,
        "opt_in_required_action_count": 1,
        "source_policy_execution_allowed_now": False,
        "exact_b4_opt_in_required_for_execution": True,
        "safe_action_ids": [
            "rebuild_read_only_audit_chain",
            "rerun_read_only_validators",
            "keep_narrowed_archive_provenance_only",
            "monitor_reopen_conditions",
        ],
        "opt_in_action_ids": ["authorized_b4_ra_hi_source_policy_execution"],
        "opt_in_required_command_count": 13,
        "opt_in_required_mapped_external_rows": 20,
        "guarded_execution_driver": "run_b4_source_policy_after_opt_in.sh",
        "required_user_approval_statement": (
            "I explicitly approve running the B4 source-policy execution commands listed in "
            "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json."
        ),
    }
    checks.check(
        full_source_runner_gap.get("action_boundary") == expected_archive_action_boundary,
        "full-source archive action boundary changed",
    )
    checks.check(
        full_source_runner_gap.get("safe_without_b4_opt_in_count")
        == full_source_runner_gap.get("action_boundary", {}).get("safe_without_b4_opt_in_count")
        == 4
        and full_source_runner_gap.get("opt_in_required_action_count")
        == full_source_runner_gap.get("action_boundary", {}).get("opt_in_required_action_count")
        == 1
        and full_source_runner_gap.get("source_policy_execution_allowed_now")
        == full_source_runner_gap.get("action_boundary", {}).get("source_policy_execution_allowed_now")
        is False
        and full_source_runner_gap.get("exact_b4_opt_in_required_for_execution")
        == full_source_runner_gap.get("action_boundary", {}).get("exact_b4_opt_in_required_for_execution")
        is True
        and full_source_runner_gap.get("opt_in_required_command_count")
        == full_source_runner_gap.get("action_boundary", {}).get("opt_in_required_command_count")
        == 13
        and full_source_runner_gap.get("opt_in_required_mapped_external_rows")
        == full_source_runner_gap.get("action_boundary", {}).get("opt_in_required_mapped_external_rows")
        == 20,
        "full-source archive top-level action aliases changed",
    )
    expected_archive_safe_action_ids = [
        "rebuild_read_only_audit_chain",
        "rerun_read_only_validators",
        "keep_narrowed_archive_provenance_only",
        "monitor_reopen_conditions",
    ]
    expected_archive_opt_in_action_ids = ["authorized_b4_ra_hi_source_policy_execution"]
    authorized_b4 = b4_post_execution_audit.get("verified_authorized_execution_recorded") is True
    expected_b4_scope = (
        "verified_authorized_guarded_driver_execution"
        if authorized_b4
        else "no_verified_current_authorized_execution_record_existing_artifacts_only"
    )
    legacy_b4_post_execution_file_status = (
        "existing_artifacts_present_no_verified_authorized_execution_no_rows_promoted"
    )
    expected_b4_post_execution_file_status = (
        b4_post_execution_audit.get("status")
        or "b4_post_execution_audit_status_missing_no_rows_promoted"
    )
    tfe_brown_mcphee_contract = tfe_brown_mcphee_boundary.get(
        "candidate_frictional_dae_trajectory_contract", {}
    )
    tfe_brown_mcphee_velocity_sensitivity = tfe_brown_mcphee_boundary.get(
        "brown_mcphee_transition_velocity_sensitivity", {}
    )
    b4_promotion_contract = b4_execution_opt_in_packet.get("post_execution_promotion_contract", {})
    current_code = manifest.get("current_code_inventory", {})
    external = manifest.get("external_runner_status", {})
    proof_status = manifest.get("proof_status", {})
    expected_anchor_evidence_sources = [
        "PROOF_CLOSURE_MANIFEST.json",
        "PROOF_CLAIM_TRACEABILITY_AUDIT.json",
    ]
    minimal_candidate = manifest.get("minimal_reproducibility_candidate", {})
    local_runner_companion = manifest.get("local_accepted_runner_companion", {})
    narrowed_repro_audit = manifest.get("narrowed_reproducibility_package_audit", {})
    narrowed_repro_code_archive = manifest.get("narrowed_repro_code_archive", {})
    narrowed_archive_boundary = manifest.get("narrowed_archive_boundary", {})
    narrowed_archive_boundary_source = narrowed_repro_code_archive_source.get(
        "narrowed_archive_boundary", {}
    )
    archive_gap_objective_boundary = full_source_runner_gap.get(
        "objective_archive_blocker_boundary", {}
    )
    reviewer_code_policy = manifest.get("reviewer_facing_code_policy", {})
    minimal_submission_code_boundary = manifest.get("minimal_submission_code_dependency_boundary", {})
    strict_proof_boundary = manifest.get("strict_proof_writing_submission_boundary", {})
    objective_strict_proof_boundary = objective_completion.get("strict_proof_writing_submission_boundary", {})
    expected_global_submission_boundaries = [
        "full_source_policy_package_ready",
        "theorem_level_eta_h_solver_policy_evidence",
        "closed_residual_to_error_theorem_for_mechanism_rows",
    ]
    expected_theorem_assumption_anchor_ids = ["P1", "P2", "P3", "P4", "P5", "P6", "P7"]
    expected_submission_satisfied_assumption_ids = ["P5"]
    expected_retained_or_open_assumption_ids = ["P1", "P2", "P3", "P4", "P6", "P7"]
    expected_retained_theorem_interface_ids = ["P1", "P2", "P3", "P4", "P6"]
    expected_open_nonpromotion_boundary_ids = ["P7"]
    expected_safe_reader_claim = (
        "conditional order-six theorem under retained P1, P2, and P3 theorem "
        "interfaces, the separate P6 solver-scale interface, and the P4 "
        "binding convention, with P4's proved 96-row non-dynamic row-local "
        "certificate and P5's direct Newton-Euler rows supplying one same-branch "
        "132-row residual bridge; route-exclusivity forbids mixing direct and "
        "primitive/Taylor residual certificates to lower constants, remove P6, "
        "or prove a P7 residual-to-error transfer theorem; the theorem statement itself consumes only one "
        "residual-value certificate, so a future primitive/Taylor certificate "
        "may only replace the accepted direct certificate by proving a new "
        "same-tuple 132-row residual-value bound; P7 remains a separate "
        "output nonclaim/residual-to-error boundary"
    )
    expected_proof_reading_rule = (
        "The accepted theorem is traceable only under retained P1, P2, and P3 "
        "theorem interfaces, the separate P6 solver-scale interface, and the "
        "P4 binding convention; P4's proved 96-row non-dynamic row-local "
        "certificate and the satisfied P5 direct dynamic-row route supply "
        "the accepted 132-row residual bridge; P7 is recorded only as the "
        "separate residual-to-error boundary. The direct route and "
        "any future primitive/Taylor route are mutually exclusive same-branch "
        "certificate routes; they are not mixed to lower constants, discharge "
        "P6, or prove a P7 residual-to-error transfer theorem. The theorem invocation consumes exactly one "
        "residual-value certificate; any future primitive/Taylor certificate "
        "must replace the accepted direct certificate by proving a new same-tuple "
        "132-row residual-value bound rather than being appended to it. "
        "This boundary does not promote eta_h evidence, "
        "residual-to-error rows, source-policy rows, or full-TFE replacement."
    )
    expected_forbidden_reader_claims = [
        "unconditional theorem without theorem-domain interfaces",
        "eta_h solver-policy condition closed",
        "fixed-tolerance runs as asymptotic proof",
        "accepted residual-to-error transfer theorem for mechanism rows",
        "source-policy/full-TFE package readiness",
        "mixing direct and primitive-route residual certificates to lower constants, remove P6, or prove a P7 residual-to-error transfer theorem",
    ]
    proof_closure_state = proof.get("closure_state", {})
    proof_readiness_boundary = proof.get("readiness_boundary", {})
    proof_residual_policy = proof.get("residual_to_error_promotion_policy", {})
    proof_solver_state = proof.get("solver_state", {})
    proof_theorem_boundary = proof.get("theorem_statement_boundary", {})
    proof_manuscript_traceability = proof.get("manuscript_traceability", {})
    proof_claim_closure_state = proof_claim_traceability.get("proof_closure_state", {})
    proof_claim_remaining_boundary = proof_claim_traceability.get(
        "remaining_claim_boundary", {}
    )
    proof_claim_summary = proof_claim_traceability.get("summary", {})
    proof_claim_theorem_traceability = proof_claim_traceability.get(
        "manuscript_theorem_traceability", {}
    )
    proof_close_requirements = proof.get("close_requirements", [])
    proof_assumption_coverage = proof.get("theorem_assumption_coverage", [])
    proof_theorem_assumption_anchor_ids = [
        item.get("id") for item in proof_assumption_coverage
    ]
    proof_submission_satisfied_assumption_ids = [
        item.get("id")
        for item in proof_assumption_coverage
        if item.get("satisfied_for_submission") is True
    ]
    proof_retained_or_open_assumption_ids = [
        item.get("id")
        for item in proof_assumption_coverage
        if item.get("satisfied_for_submission") is False
    ]
    proof_satisfied_close_requirement_ids = [
        item.get("id")
        for item in proof_close_requirements
        if item.get("satisfied") is True
    ]
    proof_unsatisfied_close_requirement_ids = [
        item.get("id")
        for item in proof_close_requirements
        if item.get("satisfied") is False
    ]
    runner_adapter = manifest.get("runner_adapter_candidate", {})
    runner_centered_audit = manifest.get("runner_centered_reproducibility_audit", {})
    extraction_plan = manifest.get("self_contained_runner_extraction_plan", {})
    closed_loop_audit = manifest.get("b6_closed_loop_self_contained_extraction_audit", {})
    closed_loop_candidate = manifest.get("closed_loop_local_runner_candidate", {})
    b6_local_evidence = manifest.get("b6_four_example_local_evidence", {})
    p1_local_runner_audit = manifest.get("p1_local_runner_extraction_audit", {})
    files = manifest.get("candidate_minimal_file_set", [])
    missing_components = manifest.get("missing_components", [])
    p1_single_candidate = p1_local_runner_audit.get("p1_single_runner_candidate", {})
    p1_double_candidate = p1_local_runner_audit.get("p1_double_runner_candidate", {})
    summary_closed_loop_models = set(summary.get("runner_adapter_closed_loop_local_models", []))
    runner_adapter_closed_loop_models = set(runner_adapter_source.get("closed_loop_local_models", []))
    summary_local_evidence_examples = set(summary.get("human_runnable_local_evidence_examples", []))
    expected_tfe_dae_gap_ids = [
        "brown_mcphee_source_code_equivalent_law_open",
        "pendulum_absolute_coordinate_source_policy_dae_runner_missing",
        "tfe_newmark_trapezoidal_source_policy_method_runners_missing",
        "gauss6_fullva_absolute_coordinate_source_policy_runner_missing",
        "full_T10_source_grid_endpoint_policy_open",
        "accepted_source_policy_work_precision_rows_not_executed_or_bound",
    ]
    expected_tfe_dae_nonheavy_gap_ids = [
        "brown_mcphee_source_code_equivalent_law_open",
        "full_T10_source_grid_endpoint_policy_open",
    ]
    expected_tfe_dae_execution_gap_ids = [
        "pendulum_absolute_coordinate_source_policy_dae_runner_missing",
        "tfe_newmark_trapezoidal_source_policy_method_runners_missing",
        "gauss6_fullva_absolute_coordinate_source_policy_runner_missing",
        "accepted_source_policy_work_precision_rows_not_executed_or_bound",
    ]
    expected_tfe_candidate_source_policy_boundary_sources = [
        "TFE_SOURCE_POLICY_SPEC.json",
        "TFE_SOURCE_POLICY_ROW_AUDIT.json",
        "TFE_DAE_RUNNER_CONTRACT_GAP_AUDIT.json",
        "TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.json",
    ]
    expected_tfe_candidate_source_policy_boundary = tfe_spec.get("candidate_vs_source_policy_boundary", {})
    tfe_source_policy_execution_preflight = tfe_dae_gap.get("source_policy_execution_preflight", {})
    tfe_self_reproduction_execution_preflight = (
        tfe_self_reproduction_attempt_certificate.get("source_policy_execution_preflight", {})
    )
    expected_full_archive_terminal_reopen_conditions = {
        "tfe2026_original_pendulum": "new_public_or_source_code_equivalent_tfe_implementation_artifact",
        "vp2024_velocity_partitioning": "new_distinct_public_vp2024_velocity_partitioning_code_path",
    }
    expected_tfe_self_reproduction_runner_contracts = [
        "monolithic_absolute_coordinate_DAE_time_integrator",
        "TFE_m1_m2_m3_Newmark_beta_trapezoidal_source_policy_method_runners",
        "Gauss6_FullVA_absolute_coordinate_source_policy_DAE_runner",
        "accepted_T10_source_policy_work_precision_rows",
    ]
    summary_self_contained_examples = set(summary.get("human_runnable_self_contained_local_examples", []))
    summary_replay_only_examples = set(summary.get("human_runnable_replay_only_local_examples", []))

    checks.check(manifest.get("schema") == "cmame-reproducibility-package-manifest-v1", "schema changed")
    checks.check(
        manifest.get("status") == "not_ready_self_contained_runner_centered_package_missing_source_policy",
        "status changed",
    )
    checks.check(manifest.get("read_only") is True, "manifest must be read-only")
    checks.check(manifest.get("submission_ready") is False, "manifest must not mark submission ready")
    checks.check(
        manifest.get("minimal_package_ready")
        == summary.get("minimal_reproducible_submission_code_ready")
        is False,
        "top-level minimal package readiness alias stale",
    )
    checks.check(
        manifest.get("candidate_files")
        == f"{manifest.get('candidate_existing_file_count')}/{manifest.get('candidate_file_count')}"
        == "141/141",
        "top-level candidate file ratio alias stale",
    )
    checks.check(
        manifest.get("candidate_python_lines")
        == summary.get("minimal_reproducibility_candidate_python_lines")
        == 180,
        "top-level candidate Python line alias stale",
    )
    checks.check(
        manifest.get("source_policy_closed_ratio")
        == f"{summary.get('source_policy_closed_rows')}/{summary.get('source_policy_total_rows')}"
        == "0/40",
        "top-level source-policy closed ratio alias stale",
    )
    checks.check(
        manifest.get("source_policy_closed") is False
        and manifest.get("source_policy_rows_closed") == summary.get("source_policy_closed_rows") == 0
        and manifest.get("source_policy_rows_total") == summary.get("source_policy_total_rows") == 40,
        "top-level source-policy closure aliases stale",
    )
    checks.check(
        manifest.get("full_source_policy_runner_package_ready")
        == summary.get("full_source_policy_runner_package_ready")
        is False,
        "top-level full source-policy runner readiness alias stale",
    )
    checks.check(
        manifest.get("run_v047_invoked") is False
        and manifest.get("heavy_numerical_run_invoked") is False
        and manifest.get("v048_runner_invoked") is False,
        "top-level restricted-run aliases changed",
    )
    checks.check(
        manifest.get("tfe_runner") == summary.get("tfe_source_policy_runner_implemented") is False,
        "top-level TFE runner alias stale",
    )
    checks.check(
        manifest.get("source_policy_execution_handoff_status")
        == summary.get("source_policy_execution_handoff_status")
        == "source_policy_execution_handoff_ready_not_authorized_not_run"
        and manifest.get("source_policy_execution_handoff_authorized") is False
        and manifest.get("source_policy_execution_handoff_commands_not_run") is True
        and manifest.get("source_policy_execution_handoff_driver") == "run_b4_source_policy_after_opt_in.sh"
        and manifest.get("source_policy_execution_handoff_driver_requires_exact_approval") is True
        and manifest.get("source_policy_execution_handoff_driver_does_not_authorize_execution") is True,
        "top-level source-policy handoff aliases stale",
    )
    checks.check(
        manifest.get("source_policy_execution_allowed_now")
        == summary.get("full_source_policy_runner_archive_gap_source_policy_execution_allowed_now")
        == full_source_runner_gap.get("source_policy_execution_allowed_now")
        is False
        and manifest.get("source_policy_execution_invoked")
        == summary.get("full_source_policy_runner_archive_gap_source_policy_execution_invoked")
        == full_source_runner_gap.get("source_policy_execution_invoked")
        is False
        and manifest.get("exact_b4_opt_in_required_for_execution")
        == summary.get("full_source_policy_runner_archive_gap_exact_b4_opt_in_required_for_execution")
        == full_source_runner_gap.get("exact_b4_opt_in_required_for_execution")
        is True
        and manifest.get("safe_action_ids")
        == summary.get("full_source_policy_runner_archive_gap_safe_action_ids")
        == full_source_runner_gap.get("safe_action_ids")
        == expected_archive_safe_action_ids
        and manifest.get("opt_in_action_ids")
        == summary.get("full_source_policy_runner_archive_gap_opt_in_action_ids")
        == full_source_runner_gap.get("opt_in_action_ids")
        == expected_archive_opt_in_action_ids
        and manifest.get("required_user_approval_statement")
        == summary.get("full_source_policy_runner_archive_gap_required_approval_statement")
        == full_source_runner_gap.get("required_user_approval_statement")
        == expected_archive_action_boundary["required_user_approval_statement"]
        and manifest.get("guarded_execution_driver")
        == summary.get("source_policy_execution_handoff_driver")
        == full_source_runner_gap.get("guarded_execution_driver")
        == "run_b4_source_policy_after_opt_in.sh",
        "top-level generic source-policy execution aliases stale",
    )
    checks.check(
        manifest.get("oc12_archive_tfe_runner_contract_preflight_status")
        == summary.get("oc12_archive_tfe_runner_contract_preflight_status")
        == objective_summary.get("full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_status")
        == "contract_entrypoints_callable_candidate_backed_source_policy_open",
        "top-level OC12 archive TFE preflight status alias stale",
    )
    checks.check(
        manifest.get("oc12_archive_tfe_runner_contract_preflight_entrypoints")
        == summary.get("oc12_archive_tfe_runner_contract_preflight_entrypoints")
        == objective_summary.get("full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_entrypoints")
        == "3/3"
        and manifest.get("oc12_archive_tfe_runner_contract_preflight_candidate_backed")
        == summary.get("oc12_archive_tfe_runner_contract_preflight_candidate_backed")
        == objective_summary.get("full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_candidate_backed")
        == "3/3"
        and manifest.get("oc12_archive_tfe_runner_contract_preflight_source_policy_rows_completed")
        == summary.get("oc12_archive_tfe_runner_contract_preflight_source_policy_rows_completed")
        == objective_summary.get(
            "full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_source_policy_rows_completed"
        )
        == 0
        and manifest.get("oc12_archive_tfe_runner_contract_preflight_execution_blocks")
        == summary.get("oc12_archive_tfe_runner_contract_preflight_execution_blocks")
        == objective_summary.get("full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_execution_blocks")
        == 4
        and manifest.get("oc12_archive_tfe_runner_contract_preflight_safe_use")
        == summary.get("oc12_archive_tfe_runner_contract_preflight_safe_use")
        == objective_summary.get("full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_safe_use"),
        "top-level OC12 archive TFE preflight count aliases stale",
    )
    checks.check(
        manifest.get("oc12_archive_action_boundary")
        == summary.get("oc12_archive_action_boundary")
        == objective_summary.get("full_source_policy_runner_archive_gap_action_boundary")
        == expected_archive_action_boundary,
        "top-level OC12 archive action boundary alias stale",
    )
    checks.check(
        manifest.get("oc12_archive_safe_without_b4_opt_in_count")
        == summary.get("oc12_archive_safe_without_b4_opt_in_count")
        == objective_summary.get("full_source_policy_runner_archive_gap_safe_without_b4_opt_in_count")
        == 4
        and manifest.get("oc12_archive_opt_in_required_action_count")
        == summary.get("oc12_archive_opt_in_required_action_count")
        == objective_summary.get("full_source_policy_runner_archive_gap_opt_in_required_action_count")
        == 1
        and manifest.get("oc12_archive_source_policy_execution_allowed_now")
        == summary.get("oc12_archive_source_policy_execution_allowed_now")
        == objective_summary.get("full_source_policy_runner_archive_gap_source_policy_execution_allowed_now")
        is False
        and manifest.get("oc12_archive_source_policy_execution_invoked")
        == summary.get("oc12_archive_source_policy_execution_invoked")
        == objective_summary.get("full_source_policy_runner_archive_gap_source_policy_execution_invoked")
        is False
        and manifest.get("oc12_archive_exact_b4_opt_in_required_for_execution")
        == summary.get("oc12_archive_exact_b4_opt_in_required_for_execution")
        == objective_summary.get("full_source_policy_runner_archive_gap_exact_b4_opt_in_required_for_execution")
        is True
        and manifest.get("oc12_archive_opt_in_required_command_count")
        == summary.get("oc12_archive_opt_in_required_command_count")
        == objective_summary.get("full_source_policy_runner_archive_gap_opt_in_required_command_count")
        == 13
        and manifest.get("oc12_archive_opt_in_required_mapped_external_rows")
        == summary.get("oc12_archive_opt_in_required_mapped_external_rows")
        == objective_summary.get("full_source_policy_runner_archive_gap_opt_in_required_mapped_external_rows")
        == 20
        and manifest.get("oc12_archive_safe_action_ids")
        == summary.get("oc12_archive_safe_action_ids")
        == objective_summary.get("full_source_policy_runner_archive_gap_safe_action_ids")
        == expected_archive_safe_action_ids
        and manifest.get("oc12_archive_opt_in_action_ids")
        == summary.get("oc12_archive_opt_in_action_ids")
        == objective_summary.get("full_source_policy_runner_archive_gap_opt_in_action_ids")
        == expected_archive_opt_in_action_ids,
        "top-level OC12 archive action aliases stale",
    )
    checks.check(
        "TFE_SOURCE_PENDULUM_MODEL_AUDIT.json" in manifest.get("generated_from", []),
        "TFE source pendulum model audit missing from manifest provenance",
    )
    checks.check(
        "TFE_DAE_RUNNER_CONTRACT_GAP_AUDIT.json" in manifest.get("generated_from", []),
        "TFE DAE runner contract gap audit missing from manifest provenance",
    )
    checks.check(
        "TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.json"
        in manifest.get("generated_from", []),
        "TFE self-reproduction attempt certificate missing from manifest provenance",
    )
    checks.check(
        "TFE_PUBLIC_CODE_RECHECK_20260613.json" in manifest.get("generated_from", []),
        "TFE public-code recheck certificate missing from manifest provenance",
    )
    checks.check(
        "VP2024_PUBLIC_CODE_RECHECK_20260613.json" in manifest.get("generated_from", []),
        "VP2024 public-code recheck certificate missing from manifest provenance",
    )
    checks.check(
        "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.json" in manifest.get("generated_from", []),
        "2026-06-14 source-policy public-code refresh missing from manifest provenance",
    )
    checks.check(
        "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.json" in manifest.get("generated_from", []),
        "2026-06-20 source-policy public-code refresh supplement missing from manifest provenance",
    )
    checks.check(
        "SOURCE_POLICY_REOPEN_CONDITION_MONITOR_20260620.json" in manifest.get("generated_from", []),
        "2026-06-20 source-policy reopen monitor missing from manifest provenance",
    )
    checks.check(
        "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json" in manifest.get("generated_from", []),
        "full source-policy runner archive gap audit missing from manifest provenance",
    )
    checks.check(
        "TFE_BROWN_MCPHEE_SOURCE_LAW_BOUNDARY_AUDIT.json" in manifest.get("generated_from", []),
        "TFE Brown-McPhee boundary audit missing from manifest provenance",
    )
    checks.check(
        "TFE_BROWN_MCPHEE_SOURCE_CODE_EQUIVALENCE_CERTIFICATE.json"
        in manifest.get("generated_from", []),
        "TFE Brown-McPhee source-code equivalence certificate missing from manifest provenance",
    )
    checks.check(
        "TFE_FULL_T10_ABSOLUTE_DAE_LIFT_SUMMARY.json" in manifest.get("generated_from", []),
        "TFE full-T10 absolute DAE-lift summary missing from manifest provenance",
    )
    checks.check(
        "TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.json" in manifest.get("generated_from", []),
        "TFE endpoint policy boundary certificate missing from manifest provenance",
    )
    checks.check(
        "TFE_FULL_T10_ENDPOINT_POLICY_CLOSURE_CERTIFICATE.json" in manifest.get("generated_from", []),
        "TFE full-T10 endpoint policy closure certificate missing from manifest provenance",
    )
    checks.check(
        "B4_SOURCE_POLICY_WORK_PRECISION_EXECUTION_PLAN.json" in manifest.get("generated_from", []),
        "B4 source-policy work/precision plan missing from manifest provenance",
    )
    checks.check(
        "B4_EXISTING_ARTIFACT_PROMOTION_AUDIT.json" in manifest.get("generated_from", []),
        "B4 existing-artifact promotion audit missing from manifest provenance",
    )
    checks.check(
        "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.json" in manifest.get("generated_from", []),
        "B4 source-policy post-execution audit missing from manifest provenance",
    )
    checks.check(
        "FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.json" in manifest.get("generated_from", []),
        "full source-policy row provenance audit missing from manifest provenance",
    )
    checks.check(
        "RA_HI_SOURCE_POLICY_POST_EXECUTION_ATTEMPT_CERTIFICATE.json"
        in manifest.get("generated_from", []),
        "RA/HI post-execution attempt certificate missing from manifest provenance",
    )
    checks.check(
        "RA_HI_SOURCE_POLICY_CLOSEOUT_CHECKLIST.json" in manifest.get("generated_from", []),
        "RA/HI source-policy closeout checklist missing from manifest provenance",
    )
    checks.check(
        "RA_HI_SOURCE_POLICY_OUTPUT_INVENTORY.json" in manifest.get("generated_from", []),
        "RA/HI source-policy output inventory missing from manifest provenance",
    )
    checks.check(
        "RA_HI_SOURCE_POLICY_PROMOTION_BLOCKER_MATRIX.json" in manifest.get("generated_from", []),
        "RA/HI source-policy promotion blocker matrix missing from manifest provenance",
    )
    checks.check(
        "RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.json" in manifest.get("generated_from", []),
        "RA2021 double low-order diagnosis missing from manifest provenance",
    )
    checks.check(
        "HI2022_RA_HALF_DOUBLE_SOURCE_POLICY_FAILURE_DIAGNOSIS.json" in manifest.get("generated_from", []),
        "HI2022 rA_half double failure diagnosis missing from manifest provenance",
    )
    checks.check(
        "HI2022_RA_HALF_DOUBLE_REPAIR_ATTEMPT_CERTIFICATE.json" in manifest.get("generated_from", []),
        "HI2022 rA_half double repair-attempt certificate missing from manifest provenance",
    )
    checks.check(
        "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.json" in manifest.get("generated_from", []),
        "B4 source-policy row closure-readiness ledger missing from manifest provenance",
    )
    checks.check(
        "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json" in manifest.get("generated_from", []),
        "B4 source-policy execution opt-in packet missing from manifest provenance",
    )
    checks.check(
        "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json" in manifest.get("generated_from", []),
        "B4 source-policy execution handoff package missing from manifest provenance",
    )
    checks.check(
        "B4_SOURCE_POLICY_COMMAND_PREFLIGHT_FREEZE_20260620.json" in manifest.get("generated_from", []),
        "B4 source-policy command preflight freeze missing from manifest provenance",
    )
    checks.check(
        "B4_SOURCE_POLICY_EXPECTED_OUTPUT_SCHEMA_AUDIT_20260620.json"
        in manifest.get("generated_from", []),
        "B4 expected-output schema audit missing from manifest provenance",
    )
    checks.check(
        "B4_EXPECTED_OUTPUT_PROMOTION_READINESS_BLOCKER_AUDIT_20260620.json"
        in manifest.get("generated_from", []),
        "B4 expected-output promotion-readiness blocker audit missing from manifest provenance",
    )
    checks.check(
        "OC6_SOURCE_EQUIVALENT_REOPEN_READINESS_AUDIT_20260620.json"
        in manifest.get("generated_from", []),
        "OC6 source-equivalent reopen-readiness audit missing from manifest provenance",
    )
    checks.check(
        "TFE_ENDPOINT_POLICY_SENSITIVITY_AUDIT.json" in manifest.get("generated_from", []),
        "TFE endpoint sensitivity audit missing from manifest provenance",
    )
    checks.check(
        "TFE_RUNNER_CONTRACT_PREFLIGHT_CERTIFICATE.json" in manifest.get("generated_from", []),
        "TFE runner contract preflight certificate missing from manifest provenance",
    )
    checks.check(
        "OBJECTIVE_COMPLETION_AUDIT.json" in manifest.get("generated_from", []),
        "objective completion audit missing from manifest provenance",
    )
    checks.check(
        "CMAME_NARROWED_REPRODUCIBILITY_PACKAGE_AUDIT.json" in manifest.get("generated_from", []),
        "narrowed reproducibility package audit missing from manifest provenance",
    )
    checks.check(
        "CMAME_MINIMAL_REPRODUCIBILITY_CANDIDATE_MANIFEST.json" in manifest.get("generated_from", []),
        "minimal reproducibility candidate missing from manifest provenance",
    )
    checks.check(
        "CMAME_RUNNER_CENTERED_REPRODUCIBILITY_AUDIT.json" in manifest.get("generated_from", []),
        "runner-centered reproducibility audit missing from manifest provenance",
    )
    checks.check(
        "CMAME_P1_LOCAL_RUNNER_EXTRACTION_AUDIT.json" in manifest.get("generated_from", []),
        "P1 local-runner extraction audit missing from manifest provenance",
    )
    checks.check(
        "B6_FOUR_EXAMPLE_LOCAL_EVIDENCE_SUMMARY.json" in manifest.get("generated_from", []),
        "B6 four-example local-evidence summary missing from manifest provenance",
    )
    checks.check(
        "B6_CLOSED_LOOP_SELF_CONTAINED_EXTRACTION_AUDIT.json" in manifest.get("generated_from", []),
        "B6 closed-loop extraction audit missing from manifest provenance",
    )
    checks.check(
        "CMAME_CLOSED_LOOP_LOCAL_RUNNER_CANDIDATE_MANIFEST.json" in manifest.get("generated_from", []),
        "closed-loop local runner candidate missing from manifest provenance",
    )
    checks.check(
        "CMAME_LOCAL_ACCEPTED_RUNNER_COMPANION_MANIFEST.json" in manifest.get("generated_from", []),
        "local accepted-row runner companion missing from manifest provenance",
    )
    checks.check(
        "CMAME_NARROWED_REPRO_CODE_ARCHIVE_MANIFEST.json" in manifest.get("generated_from", []),
        "narrowed repro code archive missing from manifest provenance",
    )
    checks.check(
        "CMAME_RUNNER_ADAPTER_CANDIDATE_MANIFEST.json" in manifest.get("generated_from", []),
        "runner-adapter candidate missing from manifest provenance",
    )
    checks.check(
        "CMAME_SELF_CONTAINED_RUNNER_EXTRACTION_PLAN.json" in manifest.get("generated_from", []),
        "self-contained runner extraction plan missing from manifest provenance",
    )
    checks.check(
        "cmame_p1_single_runner_candidate/results/single_pendulum_summary.json" in manifest.get("generated_from", []),
        "P1 single-runner candidate summary missing from manifest provenance",
    )
    checks.check(
        "cmame_p1_double_runner_candidate/results/double_pendulum_summary.json" in manifest.get("generated_from", []),
        "P1 double-runner candidate summary missing from manifest provenance",
    )
    checks.check(
        "cmame_closed_loop_local_runner_candidate/results/closed_loop_local_summary.json"
        in manifest.get("generated_from", []),
        "closed-loop local runner summary missing from manifest provenance",
    )
    checks.check(summary.get("paper_artifact_bundle_ready") is True, "paper artifact bundle should be ready")
    checks.check(summary.get("paper_core_result_table_ready") is True, "paper core result table should be ready")
    checks.check(summary.get("paper_numerical_matrix_rows") == numerical.get("row_count") == 44, "matrix row count changed")
    checks.check(
        summary.get("paper_numerical_matrix_raw_rows") == numerical.get("raw_row_count") == 132,
        "matrix raw row count changed",
    )
    checks.check(
        summary.get("result_to_manuscript_traceability_closed")
        is traceability.get("claim_boundary", {}).get("result_to_manuscript_traceability_closed")
        is True,
        "result traceability boundary changed",
    )
    checks.check(
        summary.get("common_reference_order_wins")
        == summary.get("common_reference_order_comparisons")
        == result_checks.get("comparison_reconciliation_direct_order_wins")
        == 40,
        "common-reference order win count changed",
    )
    checks.check(
        summary.get("common_reference_error_wins")
        == summary.get("common_reference_error_comparisons")
        == result_checks.get("comparison_reconciliation_direct_error_wins")
        == 40,
        "common-reference error win count changed",
    )
    checks.check(summary.get("source_policy_closed_rows") == code_checks.get("source_policy_closed_rows") == 0, "source-policy closed rows changed")
    checks.check(summary.get("source_policy_total_rows") == code_checks.get("source_policy_total_rows") == 40, "source-policy total rows changed")
    checks.check(summary.get("source_policy_external_superiority_allowed") is False, "external superiority boundary changed")
    checks.check(
        summary.get("vp2024_public_code_recheck_status") == vp2024_public_code_recheck.get("status"),
        "VP2024 public-code recheck status missing from manifest summary",
    )
    checks.check(
        summary.get("vp2024_public_code_recheck_date") == vp2024_public_code_recheck.get("date_checked") == "2026-06-13",
        "VP2024 public-code recheck date missing from manifest summary",
    )
    checks.check(
        summary.get("vp2024_public_code_recheck_tree_truncated")
        == vp2024_public_code_recheck.get("coverage", {}).get("tree_truncated")
        is False,
        "VP2024 public-code recheck tree-truncated boundary changed",
    )
    checks.check(
        summary.get("vp2024_public_code_recheck_tree_total_paths")
        == vp2024_public_code_recheck.get("coverage", {}).get("tree_total_paths")
        == 4487,
        "VP2024 public-code recheck total paths changed",
    )
    checks.check(
        summary.get("vp2024_public_code_recheck_year2024_paths")
        == vp2024_public_code_recheck.get("coverage", {}).get("year2024_path_count")
        == 1540,
        "VP2024 public-code recheck 2024 path count changed",
    )
    checks.check(
        summary.get("vp2024_public_code_recheck_keyword_hits")
        == vp2024_public_code_recheck.get("coverage", {}).get("keyword_path_hit_count")
        == 0,
        "VP2024 public-code recheck keyword hit count changed",
    )
    checks.check(
        summary.get("vp2024_public_code_recheck_rows_attempted_not_reproducible")
        == vp2024_public_code_recheck.get("coverage", {}).get("source_policy_rows_attempted_not_reproducible")
        == 4,
        "VP2024 public-code recheck attempted rows changed",
    )
    checks.check(
        summary.get("vp2024_public_code_recheck_source_policy_rows_closed")
        == vp2024_public_code_recheck.get("coverage", {}).get("source_policy_rows_closed")
        == 0,
        "VP2024 public-code recheck overclosed rows",
    )
    checks.check(
        summary.get("source_policy_public_code_refresh_status") == source_policy_public_code_refresh.get("status"),
        "source-policy public-code refresh status missing from manifest summary",
    )
    checks.check(
        summary.get("source_policy_public_code_refresh_rows") == source_policy_public_code_refresh.get("row_count") == 20,
        "source-policy public-code refresh row count changed",
    )
    checks.check(
        summary.get("source_policy_public_code_refresh_public_code_available_rows")
        == source_policy_public_code_refresh.get("public_code_available_rows")
        == 0,
        "source-policy public-code refresh found public-code rows unexpectedly",
    )
    checks.check(
        summary.get("source_policy_public_code_refresh_self_reproduction_attempted_rows")
        == source_policy_public_code_refresh.get("self_reproduction_attempted_rows")
        == 20,
        "source-policy public-code refresh attempted rows changed",
    )
    checks.check(
        summary.get("source_policy_public_code_refresh_unable_to_reproduce_rows")
        == source_policy_public_code_refresh.get("unable_to_reproduce_rows")
        == 20,
        "source-policy public-code refresh unable rows changed",
    )
    checks.check(
        summary.get("source_policy_public_code_refresh_source_policy_rows_closed")
        == source_policy_public_code_refresh.get("source_policy_rows_closed")
        == 0,
        "source-policy public-code refresh overclosed rows",
    )
    checks.check(
        summary.get("source_policy_public_code_refresh_latest_status")
        == source_policy_public_code_refresh_latest.get("status")
        == "public_code_refresh_20260620_no_positive_new_source_artifact_rows_remain_unable_to_reproduce",
        "latest source-policy public-code refresh status missing from manifest summary",
    )
    checks.check(
        summary.get("source_policy_public_code_refresh_latest_date")
        == source_policy_public_code_refresh_latest.get("date_checked")
        == "2026-06-20",
        "latest source-policy public-code refresh date changed",
    )
    checks.check(
        summary.get("source_policy_public_code_refresh_latest_rows")
        == source_policy_public_code_refresh_latest.get("row_count")
        == 20,
        "latest source-policy public-code refresh row count changed",
    )
    checks.check(
        summary.get("source_policy_public_code_refresh_latest_current_queries")
        == source_policy_public_code_refresh_latest.get("current_query_count")
        == 11,
        "latest source-policy public-code refresh query count changed",
    )
    checks.check(
        summary.get("source_policy_public_code_refresh_latest_positive_artifact_rows")
        == source_policy_public_code_refresh_latest.get("positive_public_code_artifact_rows")
        == 0,
        "latest source-policy public-code refresh found positive artifact rows unexpectedly",
    )
    checks.check(
        summary.get("source_policy_public_code_refresh_latest_source_policy_rows_closed")
        == source_policy_public_code_refresh_latest.get("source_policy_rows_closed")
        == 0,
        "latest source-policy public-code refresh overclosed rows",
    )
    checks.check(
        summary.get("source_policy_public_code_refresh_latest_source_policy_rows_promoted")
        == source_policy_public_code_refresh_latest.get("source_policy_rows_promoted")
        == 0,
        "latest source-policy public-code refresh overpromoted rows",
    )
    checks.check(
        summary.get("source_policy_public_code_refresh_latest_external_probe_date")
        == source_policy_public_code_refresh_latest.get("latest_external_probe_date_checked")
        == "2026-06-21",
        "latest external public-code probe date changed",
    )
    checks.check(
        summary.get("source_policy_public_code_refresh_latest_external_probe_count")
        == source_policy_public_code_refresh_latest.get("latest_external_probe_count")
        == 9,
        "latest external public-code probe count changed",
    )
    checks.check(
        summary.get("source_policy_public_code_refresh_latest_external_probe_positive_artifact_rows")
        == source_policy_public_code_refresh_latest.get(
            "latest_external_probe_positive_public_code_artifact_rows"
        )
        == 0,
        "latest external public-code probe found positive artifacts unexpectedly",
    )
    checks.check(
        summary.get("source_policy_public_code_refresh_latest_external_probe_source_policy_rows_closed")
        == source_policy_public_code_refresh_latest.get(
            "latest_external_probe_source_policy_rows_closed"
        )
        == 0,
        "latest external public-code probe overclosed rows",
    )
    checks.check(
        summary.get("source_policy_public_code_refresh_latest_external_probe_access_limited_count")
        == source_policy_public_code_refresh_latest.get(
            "latest_external_probe_access_limited_count"
        )
        == 4,
        "latest external public-code probe access-limit count changed",
    )
    checks.check(
        summary.get("source_policy_public_code_refresh_latest_external_probe_global_absence_proved")
        == source_policy_public_code_refresh_latest.get(
            "latest_external_probe_global_absence_proved"
        )
        is False,
        "latest external public-code probe overproved global absence",
    )
    checks.check(
        summary.get("source_policy_public_code_refresh_latest_external_probe_reopen_triggered")
        == source_policy_public_code_refresh_latest.get(
            "latest_external_probe_source_policy_reopen_triggered"
        )
        is False,
        "latest external public-code probe unexpectedly reopened source policy",
    )
    checks.check(
        summary.get("full_source_policy_runner_archive_gap_status")
        == full_source_runner_gap.get("status")
        == "full_source_policy_runner_archive_not_ready_source_policy_open",
        "full source-policy runner archive gap status missing from manifest",
    )
    checks.check(
        summary.get("full_source_policy_runner_archive_gap_ready_now")
        == full_source_runner_gap.get("closure_conditions", {}).get("full_archive_ready_now")
        is False
        and summary.get("full_source_policy_runner_archive_gap_current_archive_use")
        == full_source_runner_gap.get("closure_conditions", {}).get(
            "can_use_current_archive_as_full_source_policy_runner_archive"
        )
        is False,
        "full source-policy runner archive gap readiness changed in manifest",
    )
    checks.check(
        summary.get("full_source_policy_runner_archive_gap_source_policy_rows_closed")
        == full_source_runner_gap.get("source_policy_rows", {}).get("closed")
        == 0
        and summary.get("full_source_policy_runner_archive_gap_source_policy_rows_total")
        == full_source_runner_gap.get("source_policy_rows", {}).get("total")
        == 40,
        "full source-policy runner archive gap row boundary changed in manifest",
    )
    checks.check(
        summary.get("full_source_policy_runner_archive_gap_terminal_unable_rows")
        == full_source_runner_gap.get("closure_conditions", {}).get("terminal_unable_to_reproduce_rows")
        == 20
        and summary.get("full_source_policy_runner_archive_gap_ra_hi_open_rows")
        == full_source_runner_gap.get("closure_conditions", {}).get(
            "ra_hi_rows_requiring_authorized_closeout_or_new_artifact"
        )
        == 20,
        "full source-policy runner archive gap terminal/open split changed in manifest",
    )
    checks.check(
        summary.get("full_source_policy_runner_archive_gap_terminal_reopen_conditions")
        == {
            item.get("suite_id"): item.get("reopen_condition")
            for item in full_source_runner_gap.get("terminal_unable_to_reproduce_suites", [])
            if isinstance(item, dict)
        }
        == expected_full_archive_terminal_reopen_conditions,
        "full source-policy runner archive terminal reopen conditions changed in manifest",
    )
    expected_archive_reopen_monitor = full_source_runner_gap.get("reopen_condition_monitor", {})
    checks.check(
        summary.get("source_policy_reopen_condition_monitor_status")
        == source_policy_reopen_monitor.get("status")
        == "reopen_conditions_monitored_no_positive_source_artifact_source_policy_open"
        and summary.get("source_policy_reopen_condition_monitor_source_policy_closed")
        == source_policy_reopen_monitor.get("source_policy_closed")
        is False
        and summary.get("source_policy_reopen_condition_monitor_source_policy_closed_ratio")
        == source_policy_reopen_monitor.get("source_policy_closed_ratio")
        == "0/20"
        and summary.get("source_policy_reopen_condition_monitor_local_scan_digest")
        == source_policy_reopen_monitor.get("local_scan_digest")
        and summary.get("source_policy_reopen_condition_monitor_evidence_digest")
        == source_policy_reopen_monitor.get("monitor_evidence_digest"),
        "source-policy reopen monitor digest aliases missing from manifest summary",
    )
    checks.check(
        summary.get("full_source_policy_runner_archive_gap_reopen_monitor_status")
        == expected_archive_reopen_monitor.get("status")
        == source_policy_reopen_monitor.get("status")
        and summary.get("full_source_policy_runner_archive_gap_reopen_monitor_source_policy_closed")
        == expected_archive_reopen_monitor.get("source_policy_closed")
        == source_policy_reopen_monitor.get("source_policy_closed")
        is False
        and summary.get("full_source_policy_runner_archive_gap_reopen_monitor_source_policy_closed_ratio")
        == expected_archive_reopen_monitor.get("source_policy_closed_ratio")
        == source_policy_reopen_monitor.get("source_policy_closed_ratio")
        == "0/20"
        and summary.get("full_source_policy_runner_archive_gap_reopen_monitor_local_scan_digest")
        == expected_archive_reopen_monitor.get("local_scan_digest")
        == source_policy_reopen_monitor.get("local_scan_digest")
        and summary.get("full_source_policy_runner_archive_gap_reopen_monitor_evidence_digest")
        == expected_archive_reopen_monitor.get("monitor_evidence_digest")
        == source_policy_reopen_monitor.get("monitor_evidence_digest"),
        "full-source archive reopen monitor digest aliases missing from manifest summary",
    )
    checks.check(
        summary.get("full_source_policy_runner_archive_gap_tfe_reopen_condition")
        == expected_full_archive_terminal_reopen_conditions["tfe2026_original_pendulum"]
        and summary.get("full_source_policy_runner_archive_gap_vp2024_reopen_condition")
        == expected_full_archive_terminal_reopen_conditions["vp2024_velocity_partitioning"],
        "full source-policy runner archive terminal reopen condition summaries changed",
    )
    checks.check(
        summary.get("full_source_policy_runner_archive_gap_required_approval_statement")
        == full_source_runner_gap.get("ra_hi_closeout_boundary", {}).get("required_user_approval_statement")
        == b4_execution_opt_in_packet.get("required_user_approval_statement")
        == "I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json.",
        "full source-policy runner archive B4 approval phrase changed in manifest",
    )
    checks.check(
        summary.get("full_source_policy_runner_archive_gap_action_boundary")
        == objective_summary.get("full_source_policy_runner_archive_gap_action_boundary")
        == expected_archive_action_boundary
        and summary.get("full_source_policy_runner_archive_gap_safe_without_b4_opt_in_count")
        == objective_summary.get("full_source_policy_runner_archive_gap_safe_without_b4_opt_in_count")
        == full_source_runner_gap.get("safe_without_b4_opt_in_count")
        == 4
        and summary.get("full_source_policy_runner_archive_gap_opt_in_required_action_count")
        == objective_summary.get("full_source_policy_runner_archive_gap_opt_in_required_action_count")
        == full_source_runner_gap.get("opt_in_required_action_count")
        == 1
        and summary.get("full_source_policy_runner_archive_gap_source_policy_execution_allowed_now")
        == objective_summary.get("full_source_policy_runner_archive_gap_source_policy_execution_allowed_now")
        == full_source_runner_gap.get("source_policy_execution_allowed_now")
        is False
        and summary.get("full_source_policy_runner_archive_gap_source_policy_execution_invoked")
        == objective_summary.get("full_source_policy_runner_archive_gap_source_policy_execution_invoked")
        == full_source_runner_gap.get("source_policy_execution_invoked")
        is False
        and summary.get("full_source_policy_runner_archive_gap_exact_b4_opt_in_required_for_execution")
        == objective_summary.get("full_source_policy_runner_archive_gap_exact_b4_opt_in_required_for_execution")
        == full_source_runner_gap.get("exact_b4_opt_in_required_for_execution")
        is True
        and summary.get("full_source_policy_runner_archive_gap_opt_in_required_command_count")
        == objective_summary.get("full_source_policy_runner_archive_gap_opt_in_required_command_count")
        == full_source_runner_gap.get("opt_in_required_command_count")
        == 13
        and summary.get("full_source_policy_runner_archive_gap_opt_in_required_mapped_external_rows")
        == objective_summary.get("full_source_policy_runner_archive_gap_opt_in_required_mapped_external_rows")
        == full_source_runner_gap.get("opt_in_required_mapped_external_rows")
        == 20
        and summary.get("full_source_policy_runner_archive_gap_safe_action_ids")
        == objective_summary.get("full_source_policy_runner_archive_gap_safe_action_ids")
        == full_source_runner_gap.get("safe_action_ids")
        == expected_archive_safe_action_ids
        and summary.get("full_source_policy_runner_archive_gap_opt_in_action_ids")
        == objective_summary.get("full_source_policy_runner_archive_gap_opt_in_action_ids")
        == full_source_runner_gap.get("opt_in_action_ids")
        == expected_archive_opt_in_action_ids,
        "full source-policy runner archive action boundary missing from manifest summary",
    )
    checks.check(
        summary.get("vp2024_public_code_recheck_external_superiority_allowed")
        == vp2024_public_code_recheck.get("claim_boundary", {}).get("external_superiority_claim_allowed")
        is False,
        "VP2024 public-code recheck external superiority boundary changed",
    )
    checks.check(
        summary.get("b4_work_precision_plan_status")
        == b4_plan.get("status")
        == "execution_plan_ready_b4_b7_remain_open",
        "B4 work/precision plan status not carried into manifest",
    )
    checks.check(
        summary.get("b4_work_precision_plan_b4_can_close_now") == b4_plan.get("b4_can_close_now") is False,
        "B4 work/precision plan overcloses B4 in manifest",
    )
    checks.check(
        summary.get("b4_work_precision_plan_b7_can_close_now") == b4_plan.get("b7_can_close_now") is False,
        "B4 work/precision plan overcloses B7 in manifest",
    )
    checks.check(
        summary.get("b4_work_precision_plan_ready_lane_count") == 2
        and summary.get("b4_work_precision_plan_not_ready_lane_count") == 2,
        "B4 work/precision plan lane counts changed in manifest",
    )
    checks.check(
        summary.get("b4_work_precision_plan_source_policy_rows_closed") == 0
        and summary.get("b4_work_precision_plan_source_policy_rows_total") == 40,
        "B4 work/precision plan source-policy row counts changed in manifest",
    )
    checks.check(
        summary.get("b4_existing_promotion_audit_status")
        == b4_existing_promotion_audit.get("status")
        == "no_existing_artifact_promotable_without_new_source_policy_execution",
        "B4 existing-artifact promotion audit status not carried into manifest",
    )
    checks.check(
        summary.get("b4_existing_promotion_candidate_items") == 8
        and summary.get("b4_existing_promotion_ready_without_new_execution") == 0,
        "B4 existing-artifact promotion audit candidate counts changed in manifest",
    )
    checks.check(
        summary.get("b4_existing_promotion_source_policy_rows_closed") == 0
        and summary.get("b4_existing_promotion_source_policy_rows_total") == 40,
        "B4 existing-artifact promotion audit row counts changed in manifest",
    )
    checks.check(
        summary.get("b4_existing_promotion_b4_closing_items") == 0
        and summary.get("b4_existing_promotion_b7_closing_items") == 0,
        "B4 existing-artifact promotion audit overcloses B4/B7 in manifest",
    )
    checks.check(
        summary.get("b4_post_execution_audit_status")
        == b4_post_execution_audit.get("status"),
        "B4 post-execution audit status not carried into manifest",
    )
    checks.check(
        summary.get("b4_post_execution_audit_approved_driver_execution_recorded")
        == b4_post_execution_audit.get("approved_driver_execution_recorded")
        is authorized_b4,
        "B4 post-execution audit approved driver marker inconsistent",
    )
    checks.check(
        summary.get("b4_post_execution_audit_verified_authorized_execution_recorded")
        == b4_post_execution_audit.get("verified_authorized_execution_recorded")
        is authorized_b4,
        "B4 post-execution audit verified authorized marker inconsistent",
    )
    checks.check(
        summary.get("b4_post_execution_audit_existing_ready_command_artifacts_present")
        == b4_post_execution_audit.get("existing_ready_command_artifacts_present")
        is True,
        "B4 post-execution audit existing-artifact marker missing in manifest",
    )
    checks.check(
        summary.get("b4_post_execution_audit_execution_record_scope")
        == b4_post_execution_audit.get("execution_record_scope")
        == expected_b4_scope,
        "B4 post-execution audit execution scope changed in manifest",
    )
    checks.check(
        summary.get("b4_post_execution_audit_ready_command_count") == 13
        and summary.get("b4_post_execution_audit_mapped_external_rows") == 20
        and summary.get("b4_post_execution_audit_unaddressed_external_rows") == 0,
        "B4 post-execution audit command/row counts changed in manifest",
    )
    checks.check(
        summary.get("b4_post_execution_audit_expected_outputs_present") is True,
        "B4 post-execution audit expected outputs missing in manifest",
    )
    checks.check(
        summary.get("b4_post_execution_audit_source_policy_rows_closed") == 0
        and summary.get("b4_post_execution_audit_source_policy_rows_total") == 40,
        "B4 post-execution audit source-policy row counts changed in manifest",
    )
    checks.check(
        summary.get("b4_post_execution_audit_b4_can_close_now") is False
        and summary.get("b4_post_execution_audit_b7_can_close_now") is False,
        "B4 post-execution audit overcloses B4/B7 in manifest",
    )
    checks.check(
        summary.get("full_source_policy_row_provenance_status")
        == full_source_policy_row_provenance_audit.get("status")
        == "row_provenance_preflight_complete_source_policy_promotion_open",
        "full source-policy row provenance status missing from manifest",
    )
    checks.check(
        summary.get("full_source_policy_row_provenance_action_boundary")
        == full_source_policy_row_provenance_audit.get("action_boundary"),
        "full source-policy row provenance action boundary missing from manifest",
    )
    checks.check(
        summary.get("full_source_policy_row_provenance_source_policy_execution_invoked")
        == full_source_policy_row_provenance_audit.get("source_policy_execution_invoked")
        is False,
        "full source-policy row provenance execution invocation boundary changed in manifest",
    )
    checks.check(
        external.get("full_source_policy_row_provenance_action_boundary")
        == full_source_policy_row_provenance_audit.get("action_boundary")
        and external.get("full_source_policy_row_provenance_source_policy_execution_invoked")
        == full_source_policy_row_provenance_audit.get("source_policy_execution_invoked")
        is False,
        "full source-policy row provenance action boundary missing from manifest external status",
    )
    checks.check(
        "Full source-policy row provenance action boundary: execution invoked `False`"
        in manifest_md,
        "manifest markdown missing full source-policy row provenance action boundary",
    )
    checks.check(
        summary.get("full_source_policy_row_provenance_rows")
        == full_source_policy_row_provenance_audit.get("row_count")
        == 40,
        "full source-policy row provenance row count changed in manifest",
    )
    checks.check(
        summary.get("full_source_policy_row_provenance_preflight_complete_rows")
        == full_source_policy_row_provenance_audit.get("provenance_preflight_complete_rows")
        == 40,
        "full source-policy provenance preflight count changed in manifest",
    )
    checks.check(
        summary.get("full_source_policy_row_provenance_public_source_root_rows")
        == full_source_policy_row_provenance_audit.get("public_source_root_rows")
        == 20,
        "full source-policy public-source-root count changed in manifest",
    )
    checks.check(
        summary.get("full_source_policy_row_provenance_unable_to_reproduce_rows")
        == full_source_policy_row_provenance_audit.get("source_policy_rows_unable_to_reproduce")
        == 20,
        "full source-policy unable-to-reproduce count changed in manifest",
    )
    checks.check(
        summary.get("full_source_policy_row_provenance_source_policy_closed_rows")
        == full_source_policy_row_provenance_audit.get("source_policy_rows_closed")
        == 0
        and summary.get("full_source_policy_row_provenance_promotion_ready_rows")
        == full_source_policy_row_provenance_audit.get("promotion_ready_rows")
        == 0,
        "full source-policy row provenance overpromotes rows in manifest",
    )
    provenance_handoff = full_source_policy_row_provenance_audit.get(
        "source_policy_execution_handoff", {}
    )
    checks.check(
        summary.get("full_source_policy_row_provenance_handoff_status")
        == provenance_handoff.get("status")
        == "source_policy_execution_handoff_ready_not_authorized_not_run",
        "full source-policy provenance handoff status missing from manifest",
    )
    checks.check(
        summary.get("full_source_policy_row_provenance_handoff_authorized")
        == provenance_handoff.get("execution_authorized")
        is False,
        "full source-policy provenance handoff authorization changed in manifest",
    )
    checks.check(
        summary.get("full_source_policy_row_provenance_handoff_commands_not_run")
        == provenance_handoff.get("commands_not_run_by_handoff")
        is True,
        "full source-policy provenance handoff commands-not-run changed in manifest",
    )
    checks.check(
        summary.get("full_source_policy_row_provenance_handoff_exact_approval")
        == provenance_handoff.get("exact_required_user_approval_statement")
        == "I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json.",
        "full source-policy provenance handoff exact approval missing from manifest",
    )
    checks.check(
        summary.get("full_source_policy_row_provenance_handoff_driver")
        == provenance_handoff.get("guarded_execution_driver")
        == "run_b4_source_policy_after_opt_in.sh",
        "full source-policy provenance handoff driver missing from manifest",
    )
    checks.check(
        summary.get("full_source_policy_row_provenance_handoff_driver_requires_exact")
        == provenance_handoff.get("driver_requires_exact_approval")
        is True
        and summary.get("full_source_policy_row_provenance_handoff_driver_does_not_authorize")
        == provenance_handoff.get("driver_does_not_authorize_execution")
        is True,
        "full source-policy provenance handoff driver guard missing from manifest",
    )
    checks.check(
        summary.get("full_source_policy_row_provenance_handoff_opt_in_commands")
        == provenance_handoff.get("opt_in_required_command_count")
        == 13
        and summary.get("full_source_policy_row_provenance_handoff_mapped_rows")
        == provenance_handoff.get("opt_in_required_mapped_external_rows")
        == 20
        and summary.get("full_source_policy_row_provenance_handoff_terminal_unable_rows")
        == provenance_handoff.get("terminal_unable_to_reproduce_rows")
        == 20,
        "full source-policy provenance handoff counts missing from manifest",
    )
    checks.check(
        summary.get("ra_hi_source_policy_closeout_checklist_status")
        == ra_hi_source_policy_closeout_checklist.get("status")
        == "ready_for_authorized_execution_closeout_not_executed_not_promoted",
        "RA/HI source-policy closeout checklist status not carried into manifest",
    )
    checks.check(
        summary.get("ra_hi_source_policy_closeout_total_rows") == 20
        and summary.get("ra_hi_source_policy_closeout_ra_rows") == 12
        and summary.get("ra_hi_source_policy_closeout_hi_rows") == 8
        and summary.get("ra_hi_source_policy_closeout_ready_commands") == 13
        and summary.get("ra_hi_source_policy_closeout_mapped_rows") == 20,
        "RA/HI source-policy closeout checklist coverage changed in manifest",
    )
    checks.check(
        summary.get("ra_hi_source_policy_closeout_promoted_rows") == 0
        and summary.get("ra_hi_source_policy_closeout_completed_rows") == 0
        and summary.get("ra_hi_source_policy_closeout_external_ready_rows") == 0,
        "RA/HI source-policy closeout checklist overpromotes rows in manifest",
    )
    checks.check(
        summary.get("ra_hi_source_policy_closeout_opt_in_required") is True
        and summary.get("ra_hi_source_policy_closeout_execution_invoked") is False
        and summary.get("ra_hi_source_policy_closeout_b4_can_close") is False
        and summary.get("ra_hi_source_policy_closeout_b7_can_close") is False,
        "RA/HI source-policy closeout checklist execution boundary changed in manifest",
    )
    checks.check(
        summary.get("ra_hi_source_policy_output_inventory_status")
        == ra_hi_source_policy_output_inventory.get("status")
        == "existing_expected_outputs_present_not_promotion_evidence",
        "RA/HI output inventory status not carried into manifest",
    )
    checks.check(
        summary.get("ra_hi_source_policy_output_inventory_command_count") == 13
        and summary.get("ra_hi_source_policy_output_inventory_outputs_existing") == 13
        and summary.get("ra_hi_source_policy_output_inventory_summaries_existing") == 8,
        "RA/HI output inventory artifact counts changed in manifest",
    )
    checks.check(
        summary.get("ra_hi_source_policy_output_inventory_csv_data_rows") == 54
        and summary.get("ra_hi_source_policy_output_inventory_hi_ok_rows") == 22
        and summary.get("ra_hi_source_policy_output_inventory_closed_rows") == 0,
        "RA/HI output inventory row counts changed in manifest",
    )
    checks.check(
        summary.get("ra_hi_source_policy_promotion_blocker_matrix_status")
        == ra_hi_source_policy_promotion_blocker_matrix.get("status")
        == "ra_hi_public_root_rows_not_promoted_source_policy_open",
        "RA/HI promotion blocker matrix status missing from manifest",
    )
    checks.check(
        summary.get("ra_hi_source_policy_promotion_blocker_matrix_rows") == 20
        and summary.get("ra_hi_source_policy_promotion_blocker_matrix_ra_rows") == 12
        and summary.get("ra_hi_source_policy_promotion_blocker_matrix_hi_rows") == 8,
        "RA/HI promotion blocker matrix row counts changed in manifest",
    )
    checks.check(
        summary.get("ra_hi_source_policy_promotion_blocker_matrix_public_root_rows") == 20
        and summary.get("ra_hi_source_policy_promotion_blocker_matrix_no_public_code_rows") == 0,
        "RA/HI promotion blocker matrix public-root boundary changed in manifest",
    )
    checks.check(
        summary.get("ra_hi_source_policy_promotion_blocker_matrix_closed_rows") == 0
        and summary.get("ra_hi_source_policy_promotion_blocker_matrix_not_promoted_rows") == 20
        and summary.get("ra_hi_source_policy_promotion_blocker_matrix_attempted_not_reproducible_rows") == 0,
        "RA/HI promotion blocker matrix disposition counts changed in manifest",
    )
    checks.check(
        summary.get("ra_hi_source_policy_promotion_blocker_matrix_current_evidence_terminal_rows") == 20
        and summary.get("ra_hi_source_policy_promotion_blocker_matrix_future_authorization_or_artifact_rows")
        == 20
        and summary.get("ra_hi_source_policy_promotion_blocker_matrix_reproduction_complete_rows") == 0,
        "RA/HI promotion blocker matrix terminal/reopen counts changed in manifest",
    )
    checks.check(
        summary.get("ra_hi_source_policy_promotion_blocker_matrix_command_mapped_rows") == 20
        and summary.get("ra_hi_source_policy_promotion_blocker_matrix_output_present_rows") == 20,
        "RA/HI promotion blocker matrix command/output counts changed in manifest",
    )
    checks.check(
        summary.get("ra2021_double_low_order_diagnosis_status")
        == ra2021_double_low_order.get("status")
        == "diagnosis_only_low_order_floor_limited_not_promoted",
        "RA2021 double low-order diagnosis status changed in manifest",
    )
    checks.check(
        summary.get("ra2021_double_low_order_fine_pair_floor_limited")
        == ra2021_double_low_order.get("diagnosis", {}).get("fine_pair_floor_limited")
        is True,
        "RA2021 double low-order fine-pair marker missing in manifest",
    )
    checks.check(
        summary.get("ra2021_double_low_order_rows_promoted")
        == ra2021_double_low_order.get("promotion_decision", {}).get(
            "source_policy_rows_promoted_by_this_diagnosis"
        )
        == 0,
        "RA2021 double low-order diagnosis promoted rows in manifest",
    )
    checks.check(
        summary.get("hi2022_ra_half_double_failure_diagnosis_status")
        == hi2022_ra_half_double_failure.get("status")
        == "diagnosis_only_partial_newton_failure_not_promoted",
        "HI2022 rA_half double failure diagnosis status changed in manifest",
    )
    checks.check(
        summary.get("hi2022_ra_half_double_failure_rows_ok") == 1
        and summary.get("hi2022_ra_half_double_failure_rows_failed") == 2
        and summary.get("hi2022_ra_half_double_failure_rows_total") == 3,
        "HI2022 rA_half double failure row counts changed in manifest",
    )
    checks.check(
        summary.get("hi2022_ra_half_double_failure_newton_failure_count")
        == hi2022_ra_half_double_failure.get("diagnosis", {}).get("newton_failure_count")
        == 2,
        "HI2022 rA_half double Newton failure count changed in manifest",
    )
    checks.check(
        summary.get("hi2022_ra_half_double_failure_pair_orders_available")
        == hi2022_ra_half_double_failure.get("diagnosis", {}).get("pair_orders_available")
        is False,
        "HI2022 rA_half double pair-order marker overclaimed in manifest",
    )
    checks.check(
        summary.get("hi2022_ra_half_double_failure_rows_promoted")
        == hi2022_ra_half_double_failure.get("promotion_decision", {}).get(
            "source_policy_rows_promoted_by_this_diagnosis"
        )
        == 0,
        "HI2022 rA_half double failure diagnosis promoted rows in manifest",
    )
    checks.check(
        summary.get("hi2022_ra_half_double_repair_attempt_status")
        == hi2022_ra_half_double_repair.get("status")
        == "targeted_repair_attempted_not_reproducible_not_promoted",
        "HI2022 rA_half double repair-attempt status changed in manifest",
    )
    checks.check(
        summary.get("hi2022_ra_half_double_repair_target_ok_rows") == 1
        and summary.get("hi2022_ra_half_double_repair_target_failed_rows") == 2,
        "HI2022 rA_half double repair target counts changed in manifest",
    )
    checks.check(
        summary.get("hi2022_ra_half_double_repair_combined_ok_rows") == 19
        and summary.get("hi2022_ra_half_double_repair_combined_row_count") == 24
        and summary.get("hi2022_ra_half_double_repair_combined_complete_groups") == 4
        and summary.get("hi2022_ra_half_double_repair_combined_group_count") == 8,
        "HI2022 rA_half double repair combined counts changed in manifest",
    )
    checks.check(
        summary.get("hi2022_ra_half_double_repair_rows_promoted")
        == hi2022_ra_half_double_repair.get("source_policy_rows_promoted")
        == 0,
        "HI2022 rA_half double repair attempt promoted rows in manifest",
    )
    checks.check(
        summary.get("b4_row_readiness_ledger_status")
        == b4_row_readiness_ledger.get("status")
        == "all_40_external_rows_mapped_20_attempted_not_reproducible_0_source_policy_rows_closed",
        "B4 row closure-readiness ledger status not carried into manifest",
    )
    checks.check(
        summary.get("b4_row_readiness_external_rows") == 40
        and summary.get("b4_row_readiness_expected_external_rows") == 40,
        "B4 row closure-readiness ledger coverage changed in manifest",
    )
    checks.check(
        summary.get("b4_row_readiness_source_policy_rows_closed") == 0
        and summary.get("b4_row_readiness_source_policy_rows_open") == 20,
        "B4 row closure-readiness ledger row counts changed in manifest",
    )
    checks.check(
        summary.get("b4_row_readiness_rows_with_launch_command_refs") == 20
        and summary.get("b4_row_readiness_rows_without_launch_command_refs") == 20,
        "B4 row closure-readiness command mapping changed in manifest",
    )
    checks.check(
        summary.get("b4_row_readiness_ready_suites") == 2
        and summary.get("b4_row_readiness_not_ready_suites") == 2,
        "B4 row closure-readiness suite readiness changed in manifest",
    )
    checks.check(
        summary.get("b4_execution_opt_in_packet_status")
        == b4_execution_opt_in_packet.get("status")
        == "ready_for_user_opt_in_packet_not_authorized_not_run",
        "B4 execution opt-in packet status not carried into manifest",
    )
    checks.check(
        summary.get("b4_execution_opt_in_explicit_user_opt_in_required") is True,
        "B4 execution opt-in guard not carried into manifest",
    )
    checks.check(
        summary.get("b4_execution_opt_in_ready_command_count") == 13
        and summary.get("b4_execution_opt_in_mapped_external_rows") == 20
        and summary.get("b4_execution_opt_in_unaddressed_external_rows") == 0,
        "B4 execution opt-in packet command/row counts changed in manifest",
    )
    checks.check(
        summary.get("b4_execution_opt_in_source_policy_rows_closed_now") == 0
        and summary.get("b4_execution_opt_in_source_policy_rows_total") == 40,
        "B4 execution opt-in packet source-policy counts changed in manifest",
    )
    checks.check(
        summary.get("source_policy_execution_handoff_status")
        == b4_execution_handoff.get("status")
        == "source_policy_execution_handoff_ready_not_authorized_not_run",
        "source-policy execution handoff status not carried into manifest",
    )
    checks.check(
        summary.get("source_policy_execution_handoff_authorized")
        == b4_execution_handoff.get("execution_authorized")
        is False
        and summary.get("source_policy_execution_handoff_commands_not_run")
        == b4_execution_handoff.get("commands_not_run_by_handoff")
        is True,
        "source-policy execution handoff authorization boundary changed in manifest",
    )
    checks.check(
        summary.get("source_policy_execution_handoff_ready_command_count")
        == b4_execution_handoff.get("ready_command_count")
        == 13
        and summary.get("source_policy_execution_handoff_ready_command_mapped_rows")
        == b4_execution_handoff.get("ready_command_mapped_external_rows")
        == 20
        and summary.get("source_policy_execution_handoff_terminal_unable_rows")
        == b4_execution_handoff.get("terminal_unable_to_reproduce_rows")
        == 20,
        "source-policy execution handoff top-level command/terminal counts changed in manifest",
    )
    checks.check(
        summary.get("source_policy_execution_handoff_command_traceability_summary")
        == expected_command_traceability,
        "source-policy handoff command traceability summary stale in manifest",
    )
    checks.check(
        summary.get("source_policy_execution_handoff_unique_mapped_row_count")
        == expected_command_traceability.get("unique_mapped_row_count")
        == 20
        and summary.get("source_policy_execution_handoff_ra_hi_unique_row_count")
        == expected_command_traceability.get("ra_hi_unique_row_count")
        == 20
        and summary.get("source_policy_execution_handoff_ra_hi_unique_rows_all_mapped")
        == expected_command_traceability.get("ra_hi_unique_rows_all_mapped")
        is True,
        "source-policy handoff unique row traceability changed in manifest",
    )
    checks.check(
        summary.get("source_policy_execution_handoff_declared_mapped_row_reference_total")
        == expected_command_traceability.get("declared_mapped_row_reference_total")
        == 32
        and summary.get("source_policy_execution_handoff_traced_command_row_reference_total")
        == expected_command_traceability.get("traced_command_row_reference_total")
        == 32
        and summary.get("source_policy_execution_handoff_declared_vs_traced_mismatch_count")
        == expected_command_traceability.get("declared_vs_traced_mismatch_count")
        == 0,
        "source-policy handoff row-reference traceability changed in manifest",
    )
    checks.check(
        summary.get("source_policy_execution_handoff_terminal_rows_with_command_refs")
        == expected_command_traceability.get("terminal_rows_with_command_refs")
        == 0
        and summary.get("source_policy_execution_handoff_traceability_closed_rows")
        == expected_command_traceability.get("source_policy_closed_rows")
        == 0
        and summary.get("source_policy_execution_handoff_traceability_promotion_ready_rows")
        == expected_command_traceability.get("promotion_ready_rows")
        == 0,
        "source-policy handoff terminal/closed traceability changed in manifest",
    )
    checks.check(
        summary.get("source_policy_execution_handoff_exact_approval_statement")
        == b4_execution_handoff.get("exact_approval_statement")
        == "I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json.",
        "source-policy execution handoff top-level exact approval not carried into manifest",
    )
    checks.check(
        summary.get("source_policy_execution_handoff_driver")
        == b4_execution_handoff.get("guarded_execution_driver")
        == "run_b4_source_policy_after_opt_in.sh"
        and summary.get("source_policy_execution_handoff_driver_requires_exact_approval")
        == b4_execution_handoff.get("driver_requires_exact_approval")
        is True
        and summary.get("source_policy_execution_handoff_driver_does_not_authorize_execution")
        == b4_execution_handoff.get("driver_does_not_authorize_execution")
        is True,
        "source-policy execution handoff top-level guarded driver boundary not carried into manifest",
    )
    checks.check(
        summary.get("source_policy_execution_handoff_opt_in_required_command_count")
        == b4_execution_handoff.get("opt_in_required_command_count")
        == 13
        and summary.get("source_policy_execution_handoff_opt_in_required_mapped_rows")
        == b4_execution_handoff.get("opt_in_required_mapped_external_rows")
        == 20,
        "source-policy execution handoff top-level opt-in counts changed in manifest",
    )
    checks.check(
        summary.get("source_policy_command_preflight_freeze_status")
        == b4_command_freeze.get("status")
        == "command_preflight_frozen_not_authorized_not_run_not_promoted",
        "source-policy command freeze status not carried into manifest",
    )
    checks.check(
        summary.get("source_policy_command_preflight_freeze_ready_commands")
        == b4_command_freeze.get("ready_command_count")
        == 13
        and summary.get("source_policy_command_preflight_freeze_unique_rows")
        == b4_command_freeze.get("unique_mapped_ra_hi_rows")
        == 20
        and summary.get("source_policy_command_preflight_freeze_row_refs")
        == b4_command_freeze.get("traced_row_reference_total")
        == 32
        and summary.get("source_policy_command_preflight_freeze_mismatches")
        == b4_command_freeze.get("declared_vs_traced_mismatch_count")
        == 0,
        "source-policy command freeze command/row counts changed in manifest",
    )
    checks.check(
        summary.get("source_policy_command_preflight_freeze_expected_artifacts")
        == b4_command_freeze.get("expected_artifacts_existing_now")
        == 21
        and summary.get("source_policy_command_preflight_freeze_expected_artifact_total")
        == b4_command_freeze.get("expected_artifact_count")
        == 21
        and summary.get("source_policy_command_preflight_freeze_commands_executed")
        == b4_command_freeze.get("commands_executed_by_freeze")
        is False
        and summary.get("source_policy_command_preflight_freeze_source_policy_closed")
        == b4_command_freeze.get("source_policy_rows_closed")
        == 0,
        "source-policy command freeze artifact/execution boundary changed in manifest",
    )
    checks.check(
        summary.get("source_policy_expected_output_schema_audit_status")
        == b4_expected_output_schema_audit.get("status")
        == "expected_outputs_schema_ready_not_authorized_not_run_not_promoted",
        "source-policy expected-output schema audit status not carried into manifest",
    )
    checks.check(
        summary.get("source_policy_expected_output_schema_audit_commands")
        == b4_expected_output_schema_audit.get("command_count")
        == 13
        and summary.get("source_policy_expected_output_schema_audit_artifacts")
        == b4_expected_output_schema_audit.get("expected_artifact_count")
        == 21
        and summary.get("source_policy_expected_output_schema_audit_hash_match")
        == b4_expected_output_schema_audit.get("artifacts_sha256_match_freeze")
        == 21,
        "source-policy expected-output schema audit artifact counts changed in manifest",
    )
    checks.check(
        summary.get("source_policy_expected_output_schema_audit_csv_parseable")
        == b4_expected_output_schema_audit.get("csv_parseable_artifacts")
        == 13
        and summary.get("source_policy_expected_output_schema_audit_json_parseable")
        == b4_expected_output_schema_audit.get("json_summary_parseable_artifacts")
        == 8
        and summary.get("source_policy_expected_output_schema_audit_schema_ready")
        == b4_expected_output_schema_audit.get("schema_ready_commands")
        == 13,
        "source-policy expected-output schema audit parseability changed in manifest",
    )
    checks.check(
        summary.get("source_policy_expected_output_schema_audit_commands_executed")
        == b4_expected_output_schema_audit.get("commands_executed_by_audit")
        is False
        and summary.get("source_policy_expected_output_schema_audit_source_policy_closed")
        == b4_expected_output_schema_audit.get("source_policy_rows_closed")
        == 0,
        "source-policy expected-output schema audit overexecuted or overclosed in manifest",
    )
    checks.check(
        summary.get("source_policy_expected_output_promotion_readiness_blocker_status")
        == b4_expected_output_promotion_readiness_blocker_audit.get("status")
        == "expected_outputs_schema_ready_but_promotion_blocked",
        "source-policy expected-output promotion blocker audit status not carried into manifest",
    )
    checks.check(
        summary.get("source_policy_expected_output_promotion_readiness_blocker_commands")
        == b4_expected_output_promotion_readiness_blocker_audit.get("command_count")
        == 13
        and summary.get("source_policy_expected_output_promotion_readiness_blocker_schema_ready")
        == b4_expected_output_promotion_readiness_blocker_audit.get("schema_ready_command_count")
        == 13
        and summary.get("source_policy_expected_output_promotion_readiness_blocker_promotion_ready")
        == b4_expected_output_promotion_readiness_blocker_audit.get("promotion_ready_command_count")
        == 0,
        "source-policy expected-output promotion blocker command counts changed in manifest",
    )
    checks.check(
        summary.get("source_policy_expected_output_promotion_readiness_blocker_row_refs")
        == b4_expected_output_promotion_readiness_blocker_audit.get("command_row_reference_total")
        == 32
        and summary.get("source_policy_expected_output_promotion_readiness_blocker_unique_rows")
        == b4_expected_output_promotion_readiness_blocker_audit.get("unique_mapped_ra_hi_row_count")
        == 20
        and summary.get("source_policy_expected_output_promotion_readiness_blocker_not_promoted")
        == b4_expected_output_promotion_readiness_blocker_audit.get("unique_mapped_ra_hi_rows_not_promoted")
        == 20,
        "source-policy expected-output promotion blocker row counts changed in manifest",
    )
    checks.check(
        summary.get("source_policy_expected_output_promotion_readiness_blocker_summary_closed")
        == b4_expected_output_promotion_readiness_blocker_audit.get(
            "summary_source_policy_rows_closed_total"
        )
        == 0
        and summary.get("source_policy_expected_output_promotion_readiness_blocker_summary_promoted")
        == b4_expected_output_promotion_readiness_blocker_audit.get(
            "summary_source_policy_rows_promoted_total"
        )
        == 0
        and summary.get("source_policy_expected_output_promotion_readiness_blocker_blocked_commands")
        == b4_expected_output_promotion_readiness_blocker_audit.get(
            "commands_with_schema_ready_but_promotion_blocked"
        )
        == 13,
        "source-policy expected-output promotion blocker closure counts changed in manifest",
    )
    checks.check(
        summary.get("oc6_source_equivalent_reopen_readiness_status")
        == oc6_source_equivalent_reopen_readiness_audit.get("status")
        == "oc6_reopen_conditions_monitored_no_positive_source_equivalent_artifact",
        "OC6 source-equivalent reopen-readiness status not carried into manifest",
    )
    checks.check(
        summary.get("oc6_source_equivalent_reopen_readiness_rows")
        == oc6_source_equivalent_reopen_readiness_audit.get("row_count")
        == 20
        and summary.get("oc6_source_equivalent_reopen_readiness_tfe_rows")
        == oc6_source_equivalent_reopen_readiness_audit.get("tfe_rows")
        == 16
        and summary.get("oc6_source_equivalent_reopen_readiness_vp_rows")
        == oc6_source_equivalent_reopen_readiness_audit.get("vp_rows")
        == 4
        and summary.get("oc6_source_equivalent_reopen_readiness_unable_rows")
        == oc6_source_equivalent_reopen_readiness_audit.get("unable_to_reproduce_rows")
        == 20,
        "OC6 source-equivalent reopen-readiness row counts changed in manifest",
    )
    checks.check(
        summary.get("oc6_source_equivalent_reopen_readiness_public_code_rows")
        == oc6_source_equivalent_reopen_readiness_audit.get("public_code_available_rows")
        == 0
        and summary.get("oc6_source_equivalent_reopen_readiness_candidate_rows")
        == oc6_source_equivalent_reopen_readiness_audit.get("candidate_runner_available_rows")
        == 20
        and summary.get("oc6_source_equivalent_reopen_readiness_source_equivalent_rows")
        == oc6_source_equivalent_reopen_readiness_audit.get(
            "candidate_runner_source_policy_equivalent_rows"
        )
        == 0,
        "OC6 source-equivalent reopen-readiness evidence counts changed in manifest",
    )
    checks.check(
        summary.get("oc6_source_equivalent_reopen_readiness_positive_public_rows")
        == oc6_source_equivalent_reopen_readiness_audit.get("positive_public_code_artifact_rows")
        == 0
        and summary.get("oc6_source_equivalent_reopen_readiness_local_positive_rows")
        == oc6_source_equivalent_reopen_readiness_audit.get("local_positive_reopen_artifact_rows")
        == 0
        and summary.get("oc6_source_equivalent_reopen_readiness_closed_rows")
        == oc6_source_equivalent_reopen_readiness_audit.get("source_policy_rows_closed")
        == 0
        and summary.get("oc6_source_equivalent_reopen_readiness_performs_new_public_code_search")
        == oc6_source_equivalent_reopen_readiness_audit.get("performs_new_public_code_search")
        is False
        and summary.get("oc6_source_equivalent_reopen_readiness_oc6_can_close_now")
        == oc6_source_equivalent_reopen_readiness_audit.get("oc6_can_close_now")
        is False,
        "OC6 source-equivalent reopen-readiness closure boundary changed in manifest",
    )
    checks.check(
        summary.get("oc6_source_equivalent_reopen_readiness_latest_external_probe_date")
        == oc6_source_equivalent_reopen_readiness_audit.get("latest_external_probe_date_checked")
        == "2026-06-21"
        and summary.get("oc6_source_equivalent_reopen_readiness_latest_external_probe_count")
        == oc6_source_equivalent_reopen_readiness_audit.get("latest_external_probe_count")
        == 9
        and summary.get(
            "oc6_source_equivalent_reopen_readiness_latest_external_probe_positive_artifact_rows"
        )
        == oc6_source_equivalent_reopen_readiness_audit.get(
            "latest_external_probe_positive_public_code_artifact_rows"
        )
        == 0,
        "OC6 source-equivalent reopen-readiness latest-probe counts changed in manifest",
    )
    checks.check(
        summary.get(
            "oc6_source_equivalent_reopen_readiness_latest_external_probe_source_policy_rows_closed"
        )
        == oc6_source_equivalent_reopen_readiness_audit.get(
            "latest_external_probe_source_policy_rows_closed"
        )
        == 0
        and summary.get(
            "oc6_source_equivalent_reopen_readiness_latest_external_probe_access_limited_count"
        )
        == oc6_source_equivalent_reopen_readiness_audit.get(
            "latest_external_probe_access_limited_count"
        )
        == 4
        and summary.get(
            "oc6_source_equivalent_reopen_readiness_latest_external_probe_global_absence_proved"
        )
        == oc6_source_equivalent_reopen_readiness_audit.get(
            "latest_external_probe_global_absence_proved"
        )
        is False
        and summary.get("oc6_source_equivalent_reopen_readiness_latest_external_probe_reopen_triggered")
        == oc6_source_equivalent_reopen_readiness_audit.get(
            "latest_external_probe_source_policy_reopen_triggered"
        )
        is False,
        "OC6 source-equivalent reopen-readiness latest-probe closure boundary changed in manifest",
    )
    checks.check(
        summary.get("oc6_reopen_latest_external_probe")
        == oc6_reopen_latest_external_probe
        == EXPECTED_OC6_REOPEN_LATEST_EXTERNAL_PROBE,
        "OC6 reopen latest external probe compact marker not carried into manifest",
    )
    checks.check(
        summary.get("b4_post_execution_promotion_contract_schema")
        == b4_promotion_contract.get("schema")
        == "b4-source-policy-post-execution-promotion-contract-v1",
        "B4 post-execution promotion contract schema not carried into manifest",
    )
    checks.check(
        summary.get("b4_post_execution_promotion_contract_status")
        == b4_promotion_contract.get("status")
        == "promotion_contract_defined_no_rows_promoted",
        "B4 post-execution promotion contract status changed in manifest",
    )
    checks.check(
        summary.get("b4_post_execution_promotion_contract_rows_closed") == 0
        and summary.get("b4_post_execution_promotion_contract_rows_total") == 40
        and summary.get("b4_post_execution_promotion_contract_ready_mapped_rows") == 20
        and summary.get("b4_post_execution_promotion_contract_unaddressed_rows") == 0,
        "B4 post-execution promotion contract row counts changed in manifest",
    )
    checks.check(
        summary.get("b4_post_execution_promotion_contract_checks_satisfied_now") is False,
        "B4 post-execution promotion contract overclaims checklist satisfaction in manifest",
    )
    checks.check(
        summary.get("b4_post_execution_promotion_contract_b4_can_close_now") is False
        and summary.get("b4_post_execution_promotion_contract_b7_can_close_now") is False,
        "B4 post-execution promotion contract overcloses B4/B7 in manifest",
    )
    checks.check(summary.get("tfe_source_policy_runner_implemented") is False, "TFE runner boundary changed")
    checks.check(
        summary.get("tfe_public_code_recheck_status")
        == tfe_public_code_recheck.get("status")
        == "public_code_rechecked_no_distinct_tfe_code_artifact_attempted_not_reproducible",
        "TFE public-code recheck status missing from manifest summary",
    )
    checks.check(
        summary.get("tfe_public_code_recheck_date") == tfe_public_code_recheck.get("date_checked") == "2026-06-13",
        "TFE public-code recheck date changed in manifest summary",
    )
    checks.check(
        summary.get("tfe_public_code_recheck_github_repository_search_total_count")
        == tfe_public_code_recheck.get("coverage", {}).get("github_repository_search_total_count")
        == 0,
        "TFE public-code recheck repository count changed in manifest summary",
    )
    checks.check(
        summary.get("tfe_public_code_recheck_github_user_search_total_count")
        == tfe_public_code_recheck.get("coverage", {}).get("github_user_search_total_count")
        == 0,
        "TFE public-code recheck user count changed in manifest summary",
    )
    checks.check(
        summary.get("tfe_public_code_recheck_github_code_search_api_status")
        == tfe_public_code_recheck.get("coverage", {}).get("github_code_search_api_status")
        == "requires_authentication",
        "TFE public-code recheck code-search status changed in manifest summary",
    )
    checks.check(
        summary.get("tfe_public_code_recheck_rows_attempted_not_reproducible")
        == tfe_public_code_recheck.get("coverage", {}).get("source_policy_rows_attempted_not_reproducible")
        == 16,
        "TFE public-code recheck attempted rows changed in manifest summary",
    )
    checks.check(
        summary.get("tfe_public_code_recheck_source_policy_rows_closed")
        == tfe_public_code_recheck.get("coverage", {}).get("source_policy_rows_closed")
        == 0,
        "TFE public-code recheck overclosed rows in manifest summary",
    )
    checks.check(
        summary.get("tfe_public_code_recheck_external_superiority_allowed")
        == tfe_public_code_recheck.get("claim_boundary", {}).get("external_superiority_claim_allowed")
        is False,
        "TFE public-code recheck external superiority changed in manifest summary",
    )
    checks.check(
        external_checks.get("tfe_candidate_source_policy_boundary")
        == expected_tfe_candidate_source_policy_boundary
        == tfe.get("candidate_vs_source_policy_boundary", {})
        == tfe_dae_gap.get("candidate_vs_source_policy_boundary", {}),
        "TFE candidate/source-policy boundary source objects changed",
    )
    checks.check(
        external_checks.get("tfe_candidate_source_policy_boundary")
        == tfe_self_reproduction_attempt_certificate.get("candidate_vs_source_policy_boundary", {}),
        "TFE self-reproduction attempt certificate boundary missing from manifest source check",
    )
    checks.check(
        summary.get("tfe_candidate_source_policy_boundary")
        == external_checks.get("tfe_candidate_source_policy_boundary"),
        "TFE candidate/source-policy boundary not inherited into manifest summary",
    )
    checks.check(
        summary.get("tfe_candidate_source_policy_boundary_sources")
        == external_checks.get("tfe_candidate_source_policy_boundary_sources")
        == expected_tfe_candidate_source_policy_boundary_sources,
        "TFE candidate/source-policy boundary sources missing from manifest summary",
    )
    checks.check(
        summary.get("tfe_candidate_source_policy_boundary_sources_match")
        == external_checks.get("tfe_candidate_source_policy_boundary_sources_match")
        is True,
        "TFE candidate/source-policy boundary match marker missing from manifest summary",
    )
    checks.check(
        summary.get("tfe_candidate_source_policy_allowed_use")
        == external_checks.get("tfe_candidate_source_policy_allowed_use")
        == "diagnostic_scaffold_only_not_source_policy_reproduction",
        "TFE candidate/source-policy allowed-use boundary changed in manifest summary",
    )
    checks.check(
        summary.get("tfe_candidate_source_policy_dae_runner_equivalent")
        == external_checks.get("tfe_candidate_source_policy_dae_runner_equivalent")
        is False
        and summary.get("tfe_candidate_source_policy_method_runner_equivalent")
        == external_checks.get("tfe_candidate_source_policy_method_runner_equivalent")
        is False
        and summary.get("tfe_candidate_source_policy_rows_completed")
        == external_checks.get("tfe_candidate_source_policy_rows_completed")
        == 0
        and summary.get("tfe_candidate_source_policy_external_superiority_allowed")
        == external_checks.get("tfe_candidate_source_policy_external_superiority_allowed")
        is False,
        "TFE candidate/source-policy non-equivalence boundary changed in manifest summary",
    )
    checks.check(
        tfe_dae_gap.get("status") == "dae_runner_contract_gap_open_not_source_policy"
        and tfe_dae_gap.get("missing_contract_block_count") == 6
        and [item.get("id") for item in tfe_dae_gap.get("missing_contract_blocks", [])]
        == expected_tfe_dae_gap_ids
        and tfe_dae_gap.get("nonheavy_missing_contract_blocks")
        == expected_tfe_dae_nonheavy_gap_ids
        and tfe_dae_gap.get("terminal_nonpromoted_contract_blocks")
        == expected_tfe_dae_nonheavy_gap_ids
        and tfe_dae_gap.get("terminal_nonpromoted_contract_block_count") == 2
        and tfe_dae_gap.get("effective_missing_contract_blocks")
        == expected_tfe_dae_execution_gap_ids
        and tfe_dae_gap.get("effective_missing_contract_block_count") == 4
        and tfe_dae_gap.get("contract_block_accounting", {}).get(
            "source_policy_rows_closed_by_accounting"
        )
        == 0
        and tfe_dae_gap.get("source_policy_execution_missing_contract_blocks")
        == expected_tfe_dae_execution_gap_ids
        and tfe_dae_gap.get("ready_to_execute_source_policy_now") is False
        and tfe_dae_gap.get("heavy_numerical_run_invoked") is False,
        "TFE DAE runner contract gap source audit boundary changed",
    )
    checks.check(
        summary.get("tfe_dae_runner_contract_gap_status") == tfe_dae_gap.get("status")
        and summary.get("tfe_dae_runner_contract_gap_missing_block_count") == 6
        and summary.get("tfe_dae_runner_contract_gap_missing_block_ids") == expected_tfe_dae_gap_ids
        and summary.get("tfe_dae_runner_contract_gap_nonheavy_blocks")
        == tfe_dae_gap.get("nonheavy_missing_contract_blocks")
        and summary.get("tfe_dae_runner_contract_gap_terminal_nonpromoted_blocks")
        == expected_tfe_dae_nonheavy_gap_ids
        and summary.get("tfe_dae_runner_contract_gap_terminal_nonpromoted_block_count") == 2
        and summary.get("tfe_dae_runner_contract_gap_effective_missing_blocks")
        == expected_tfe_dae_execution_gap_ids
        and summary.get("tfe_dae_runner_contract_gap_effective_missing_block_count") == 4
        and summary.get("tfe_dae_runner_contract_gap_block_accounting", {}).get(
            "source_policy_rows_closed_by_accounting"
        )
        == 0
        and summary.get("tfe_dae_runner_contract_gap_execution_blocks")
        == tfe_dae_gap.get("source_policy_execution_missing_contract_blocks")
        and summary.get("tfe_dae_runner_contract_gap_ready_to_execute_source_policy_now") is False
        and summary.get("tfe_dae_runner_contract_gap_heavy_run_invoked") is False,
        "TFE DAE runner contract gap fields missing from manifest summary",
    )
    checks.check(
        summary.get("tfe_source_policy_execution_preflight") == tfe_source_policy_execution_preflight,
        "TFE source-policy execution preflight not inherited into manifest summary",
    )
    checks.check(
        summary.get("tfe_source_policy_execution_preflight_status")
        == tfe_source_policy_execution_preflight.get("status")
        == "terminal_no_public_code_self_reproduction_attempted_not_promoted",
        "TFE source-policy execution preflight status changed in manifest summary",
    )
    checks.check(
        summary.get("tfe_source_policy_execution_preflight_opt_in_required")
        == tfe_source_policy_execution_preflight.get("explicit_user_opt_in_required")
        is False,
        "TFE source-policy execution preflight opt-in boundary changed in manifest summary",
    )
    checks.check(
        summary.get("tfe_source_policy_execution_preflight_nonheavy_dispositioned")
        == tfe_source_policy_execution_preflight.get("nonheavy_blocks_dispositioned_by_demotion")
        is True
        and summary.get("tfe_source_policy_execution_preflight_execution_block_count")
        == tfe_source_policy_execution_preflight.get("execution_block_count")
        == 4,
        "TFE source-policy execution preflight block boundary changed in manifest summary",
    )
    checks.check(
        summary.get("tfe_source_policy_execution_preflight_can_promote_rows_now")
        == tfe_source_policy_execution_preflight.get("can_promote_any_tfe_source_policy_row_now")
        is False
        and summary.get("tfe_source_policy_execution_preflight_ready_now")
        == tfe_source_policy_execution_preflight.get("ready_to_execute_source_policy_now")
        is False,
        "TFE source-policy execution preflight overclaims promotion/readiness in manifest summary",
    )
    checks.check(
        summary.get("tfe_runner_contract_preflight_status")
        == tfe_runner_contract_preflight.get("status")
        == "contract_entrypoints_callable_candidate_backed_source_policy_open"
        and summary.get("tfe_runner_contract_preflight_entrypoints") == "3/3"
        and summary.get("tfe_runner_contract_preflight_candidate_backed") == "3/3"
        and summary.get("tfe_runner_contract_preflight_source_policy_rows_completed")
        == tfe_runner_contract_preflight.get("source_policy_rows_completed")
        == 0
        and summary.get("tfe_runner_contract_preflight_execution_blocks")
        == tfe_runner_contract_preflight.get("source_policy_execution_block_count")
        == 4
        and summary.get("tfe_runner_contract_preflight_safe_use")
        == tfe_runner_contract_preflight.get("safe_current_use")
        == "runner_contract_preflight_only_not_source_policy_reproduction",
        "TFE runner contract preflight boundary missing from manifest summary",
    )
    checks.check(
        summary.get("oc12_archive_tfe_runner_contract_preflight_status")
        == objective_summary.get("full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_status")
        == "contract_entrypoints_callable_candidate_backed_source_policy_open"
        and summary.get("oc12_archive_tfe_runner_contract_preflight_entrypoints")
        == objective_summary.get("full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_entrypoints")
        == "3/3"
        and summary.get("oc12_archive_tfe_runner_contract_preflight_candidate_backed")
        == objective_summary.get("full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_candidate_backed")
        == "3/3"
        and summary.get("oc12_archive_tfe_runner_contract_preflight_source_policy_rows_completed")
        == objective_summary.get(
            "full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_source_policy_rows_completed"
        )
        == 0
        and summary.get("oc12_archive_tfe_runner_contract_preflight_execution_blocks")
        == objective_summary.get("full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_execution_blocks")
        == 4
        and summary.get("oc12_archive_tfe_runner_contract_preflight_safe_use")
        == objective_summary.get("full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_safe_use")
        == "runner_contract_preflight_only_not_source_policy_reproduction",
        "OC12 archive TFE runner contract preflight boundary missing from manifest summary",
    )
    checks.check(
        summary.get("oc12_archive_action_boundary")
        == objective_summary.get("full_source_policy_runner_archive_gap_action_boundary")
        == expected_archive_action_boundary
        and summary.get("oc12_archive_safe_without_b4_opt_in_count")
        == objective_summary.get("full_source_policy_runner_archive_gap_safe_without_b4_opt_in_count")
        == full_source_runner_gap.get("safe_without_b4_opt_in_count")
        == 4
        and summary.get("oc12_archive_opt_in_required_action_count")
        == objective_summary.get("full_source_policy_runner_archive_gap_opt_in_required_action_count")
        == full_source_runner_gap.get("opt_in_required_action_count")
        == 1
        and summary.get("oc12_archive_source_policy_execution_allowed_now")
        == objective_summary.get("full_source_policy_runner_archive_gap_source_policy_execution_allowed_now")
        == full_source_runner_gap.get("source_policy_execution_allowed_now")
        is False
        and summary.get("oc12_archive_source_policy_execution_invoked")
        == objective_summary.get("full_source_policy_runner_archive_gap_source_policy_execution_invoked")
        == full_source_runner_gap.get("source_policy_execution_invoked")
        is False
        and summary.get("oc12_archive_exact_b4_opt_in_required_for_execution")
        == objective_summary.get("full_source_policy_runner_archive_gap_exact_b4_opt_in_required_for_execution")
        == full_source_runner_gap.get("exact_b4_opt_in_required_for_execution")
        is True
        and summary.get("oc12_archive_opt_in_required_command_count")
        == objective_summary.get("full_source_policy_runner_archive_gap_opt_in_required_command_count")
        == full_source_runner_gap.get("opt_in_required_command_count")
        == 13
        and summary.get("oc12_archive_opt_in_required_mapped_external_rows")
        == objective_summary.get("full_source_policy_runner_archive_gap_opt_in_required_mapped_external_rows")
        == full_source_runner_gap.get("opt_in_required_mapped_external_rows")
        == 20
        and summary.get("oc12_archive_safe_action_ids")
        == objective_summary.get("full_source_policy_runner_archive_gap_safe_action_ids")
        == expected_archive_safe_action_ids
        and summary.get("oc12_archive_opt_in_action_ids")
        == objective_summary.get("full_source_policy_runner_archive_gap_opt_in_action_ids")
        == expected_archive_opt_in_action_ids,
        "OC12 archive action boundary missing from manifest summary",
    )
    checks.check(
        summary.get("tfe_source_policy_self_reproduction_preflight")
        == tfe_self_reproduction_execution_preflight,
        "TFE self-reproduction preflight not inherited into manifest summary",
    )
    checks.check(
        summary.get("tfe_source_policy_self_reproduction_preflight_status")
        == tfe_self_reproduction_execution_preflight.get("status")
        == "terminal_no_public_code_self_reproduction_attempted_not_promoted",
        "TFE self-reproduction preflight status changed in manifest summary",
    )
    checks.check(
        summary.get("tfe_source_policy_self_reproduction_preflight_current_route")
        == tfe_self_reproduction_execution_preflight.get("current_route")
        == "no_public_code_self_reproduction_attempted_unable_to_reproduce_not_promoted"
        and summary.get("tfe_source_policy_self_reproduction_preflight_reopen_condition")
        == tfe_self_reproduction_execution_preflight.get("reopen_condition")
        == "new_public_or_source_code_equivalent_tfe_implementation_artifact",
        "TFE self-reproduction preflight route/reopen condition changed in manifest summary",
    )
    checks.check(
        summary.get("tfe_source_policy_self_reproduction_preflight_execution_block_count")
        == tfe_self_reproduction_execution_preflight.get("execution_block_count")
        == 4
        and summary.get("tfe_source_policy_self_reproduction_preflight_can_promote_rows_now")
        == tfe_self_reproduction_execution_preflight.get("can_promote_any_tfe_source_policy_row_now")
        is False
        and summary.get("tfe_source_policy_self_reproduction_preflight_ready_now")
        == tfe_self_reproduction_execution_preflight.get("ready_to_execute_source_policy_now")
        is False,
        "TFE self-reproduction preflight overclaims promotion/readiness in manifest summary",
    )
    checks.check(
        summary.get("tfe_source_policy_self_reproduction_preflight_source_policy_rows_completed")
        == tfe_self_reproduction_execution_preflight.get("source_policy_rows_completed")
        == 0
        and summary.get("tfe_source_policy_self_reproduction_required_next_action_count")
        == len(tfe_self_reproduction_attempt_certificate.get("required_next_actions", []))
        == 3,
        "TFE self-reproduction preflight row/next-action counts changed in manifest summary",
    )
    checks.check(
        summary.get("tfe_source_policy_self_reproduction_preflight_runner_contracts_required")
        == tfe_self_reproduction_execution_preflight.get("runner_contracts_required_before_execution")
        == expected_tfe_self_reproduction_runner_contracts,
        "TFE self-reproduction runner-contract requirements changed in manifest summary",
    )
    checks.check(
        summary.get("tfe_source_pendulum_parameter_model_implemented") is True,
        "TFE source pendulum parameter model progress not carried into manifest",
    )
    checks.check(
        summary.get("tfe_source_pendulum_frictionless_smoke_implemented") is True,
        "TFE source pendulum smoke progress not carried into manifest",
    )
    checks.check(
        summary.get("tfe_source_pendulum_absolute_coordinate_dae_residual_smoke_implemented") is True,
        "TFE source pendulum absolute-coordinate residual progress not carried into manifest",
    )
    checks.check(
        summary.get("tfe_source_pendulum_source_policy_dae_runner_equivalent") is False,
        "TFE source-policy DAE equivalence overclaimed in manifest",
    )
    checks.check(
        summary.get("tfe_source_pendulum_source_output_time_integration_smoke_implemented") is True,
        "TFE source-output time-integration smoke progress not carried into manifest",
    )
    checks.check(
        summary.get("tfe_source_pendulum_source_policy_time_integration_runner_equivalent") is False,
        "TFE source-policy time-integration equivalence overclaimed in manifest",
    )
    checks.check(
        summary.get("tfe_source_pendulum_source_reference_solution_policy_smoke_implemented") is True,
        "TFE source reference-policy smoke not carried into manifest",
    )
    checks.check(
        summary.get("tfe_source_pendulum_source_reference_solution_policy_smoke_full_T10") is False,
        "TFE source reference-policy smoke overclaims full T=10 run in manifest",
    )
    checks.check(
        summary.get("tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_implemented")
        is True,
        "TFE full T=10 source-reference probe not carried into manifest",
    )
    checks.check(
        summary.get("tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_completed")
        is True,
        "TFE full T=10 source-reference probe completion not carried into manifest",
    )
    checks.check(
        summary.get("tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_rows_completed") == 0,
        "TFE full T=10 source-reference probe overcloses source-policy rows in manifest",
    )
    checks.check(
        summary.get("tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_steps") == 100000,
        "TFE full T=10 source-reference probe source-step count changed in manifest",
    )
    checks.check(
        summary.get("tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_check_steps") == 200000,
        "TFE full T=10 source-reference probe check-step count changed in manifest",
    )
    checks.check(
        float(summary.get("tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_coordinate_error"))
        < 1.0e-10,
        "TFE full T=10 source-reference coordinate check error too large in manifest",
    )
    checks.check(
        float(summary.get("tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_velocity_error"))
        < 1.0e-10,
        "TFE full T=10 source-reference velocity check error too large in manifest",
    )
    checks.check(
        summary.get("tfe_source_pendulum_source_comparator_candidate_runners_implemented") is True,
        "TFE source comparator candidate runners not carried into manifest",
    )
    checks.check(
        summary.get("tfe_source_pendulum_newmark_beta_candidate_runner_smoke_implemented") is True,
        "TFE Newmark-beta candidate runner smoke not carried into manifest",
    )
    checks.check(
        summary.get("tfe_source_pendulum_trapezoidal_candidate_runner_smoke_implemented") is True,
        "TFE trapezoidal candidate runner smoke not carried into manifest",
    )
    checks.check(
        summary.get("tfe_source_pendulum_source_policy_method_runner_equivalent") is False,
        "TFE source-policy method-runner equivalence overclaimed in manifest",
    )
    checks.check(
        summary.get("tfe_source_pendulum_tfe_m1_m2_m3_candidate_runner_smoke_implemented") is True,
        "TFE m=1/2/3 candidate runner smoke not carried into manifest",
    )
    checks.check(
        summary.get("tfe_source_pendulum_tfe_m1_m2_m3_source_policy_runners_implemented") is False,
        "TFE m=1/2/3 source-policy runners unexpectedly implemented in manifest",
    )
    checks.check(
        summary.get("tfe_source_pendulum_gauss6_candidate_smoke_implemented") is True,
        "Gauss6 source-pendulum candidate smoke not carried into manifest",
    )
    checks.check(
        summary.get("tfe_source_pendulum_gauss6_absolute_coordinate_source_policy_runner_implemented")
        is False,
        "Gauss6 source-policy runner unexpectedly implemented in manifest",
    )
    checks.check(
        summary.get("tfe_source_pendulum_gauss6_candidate_rows") == 2,
        "Gauss6 source-pendulum candidate row count changed in manifest",
    )
    checks.check(
        summary.get("tfe_source_pendulum_gauss6_candidate_source_policy_rows_completed") == 0,
        "Gauss6 source-pendulum candidate overclosed source-policy rows in manifest",
    )
    checks.check(
        summary.get("tfe_source_pendulum_gauss6_candidate_method_equivalent") is False,
        "Gauss6 source-pendulum candidate overclaims method equivalence in manifest",
    )
    checks.check(
        summary.get("tfe_source_pendulum_bounded_source_policy_runner_smoke_implemented") is True,
        "bounded source-policy runner smoke not carried into manifest",
    )
    checks.check(
        summary.get("tfe_source_pendulum_bounded_source_policy_runner_rows") == 4,
        "bounded source-policy runner row count changed in manifest",
    )
    checks.check(
        summary.get("tfe_source_pendulum_bounded_source_policy_runner_full_T10") is False,
        "bounded source-policy runner overclaims full T=10 in manifest",
    )
    checks.check(
        summary.get("tfe_source_pendulum_bounded_source_policy_runner_source_policy_rows_completed") == 0,
        "bounded source-policy runner overcloses rows in manifest",
    )
    checks.check(
        summary.get("tfe_source_pendulum_active_b2_candidate_row_smoke_implemented") is True,
        "active B2 candidate row smoke not carried into manifest",
    )
    checks.check(
        summary.get("tfe_source_pendulum_active_b2_candidate_row_smoke_full_T10") is False,
        "active B2 candidate smoke overclaims full T=10 in manifest",
    )
    checks.check(
        summary.get("tfe_source_pendulum_active_b2_source_policy_rows_completed") == 0,
        "active B2 candidate smoke overcloses source-policy rows in manifest",
    )
    checks.check(
        summary.get("tfe_source_pendulum_active_b2_source_reference_full_T10_probe_implemented")
        is True,
        "active B2 source-reference full-T10 probe not carried into manifest",
    )
    checks.check(
        summary.get("tfe_source_pendulum_active_b2_source_reference_full_T10_probe_full_T10")
        is True
        and summary.get(
            "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_reference_invoked"
        )
        is True
        and summary.get(
            "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_source_policy_rows"
        )
        == 0
        and summary.get(
            "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_method_equivalent"
        )
        is False,
        "active B2 source-reference full-T10 probe boundary changed in manifest",
    )
    checks.check(
        summary.get("tfe_source_pendulum_active_b2_candidate_row_count") == 4,
        "active B2 candidate row count changed in manifest",
    )
    checks.check(
        summary.get("tfe_full_t10_absolute_dae_lift_status")
        == tfe_full_t10_absolute.get("status")
        == "full_T10_absolute_dae_lift_candidate_summarized_not_source_policy",
        "TFE full-T10 absolute DAE-lift status not carried into manifest summary",
    )
    checks.check(
        summary.get("tfe_full_t10_absolute_dae_lift_completed")
        == tfe_full_t10_absolute.get("full_T10_absolute_coordinate_lift_completed")
        is True,
        "TFE full-T10 absolute DAE-lift completion not carried into manifest summary",
    )
    checks.check(
        summary.get("tfe_full_t10_absolute_dae_lift_method_count")
        == tfe_full_t10_absolute.get("method_count")
        == 4
        and summary.get("tfe_full_t10_absolute_dae_lift_metric_rows")
        == tfe_full_t10_absolute.get("metric_row_count")
        == 12
        and summary.get("tfe_full_t10_absolute_dae_lift_step_residual_rows")
        == tfe_full_t10_absolute.get("step_residual_row_count")
        == 2800,
        "TFE full-T10 absolute DAE-lift counts not carried into manifest summary",
    )
    checks.check(
        summary.get("tfe_full_t10_absolute_dae_lift_source_reference_invoked")
        == tfe_full_t10_absolute.get("source_reference_invoked")
        is True
        and summary.get("tfe_full_t10_absolute_dae_lift_source_policy_rows_completed")
        == tfe_full_t10_absolute.get("source_policy_rows_completed")
        == 0
        and summary.get("tfe_full_t10_absolute_dae_lift_monolithic")
        == tfe_full_t10_absolute.get("monolithic_absolute_coordinate_dae_time_integrator")
        is False
        and summary.get("tfe_full_t10_absolute_dae_lift_equivalent")
        == tfe_full_t10_absolute.get("source_policy_dae_runner_equivalent")
        is False,
        "TFE full-T10 absolute DAE-lift overclosed source-policy boundary in manifest summary",
    )
    checks.check(
        summary.get("tfe_endpoint_boundary_certificate_status")
        == tfe_endpoint_boundary.get("status")
        == "endpoint_policy_literal_overrun_bound_proved_source_policy_open",
        "TFE endpoint boundary status not carried into manifest summary",
    )
    checks.check(
        summary.get("tfe_endpoint_boundary_literal_overrun_bound_proved") is True
        and tfe_endpoint_boundary.get("theorem", {}).get("name")
        == "fixed_h_until_final_time_endpoint_bound",
        "TFE endpoint boundary theorem not carried into manifest summary",
    )
    checks.check(
        summary.get("tfe_endpoint_boundary_literal_exact_T_rows")
        == tfe_endpoint_boundary.get("algorithm_literal_exact_T_row_count")
        == 2
        and summary.get("tfe_endpoint_boundary_literal_overrun_rows")
        == tfe_endpoint_boundary.get("algorithm_literal_overrun_row_count")
        == 4,
        "TFE endpoint boundary row counts not carried into manifest summary",
    )
    checks.check(
        summary.get("tfe_endpoint_boundary_source_policy_rows_completed")
        == tfe_endpoint_boundary.get("source_policy_rows_completed")
        == 0
        and summary.get("tfe_endpoint_boundary_full_T10_policy_resolved")
        == tfe_endpoint_boundary.get("source_grid_policy_resolved_for_full_T10")
        is False
        and summary.get("tfe_endpoint_boundary_exact_T_error_sampling_equivalent")
        == tfe_endpoint_boundary.get("source_policy_exact_T_error_sampling_equivalent")
        is False,
        "TFE endpoint boundary overclosed source-policy boundary in manifest summary",
    )
    checks.check(
        summary.get("tfe_full_T10_endpoint_policy_closure_certificate_status")
        == tfe_endpoint_certificate.get("status")
        == "negative_full_T10_endpoint_policy_certificate_not_source_policy"
        and summary.get("tfe_full_T10_endpoint_policy_closure_certificate_available") is True
        and summary.get("tfe_full_T10_endpoint_policy_closure_certificate_positive") is False
        and summary.get("tfe_full_T10_endpoint_policy_closure_certificate_nonheavy_block_closed")
        is False,
        "TFE full-T10 endpoint policy closure certificate boundary changed in manifest summary",
    )
    checks.check(
        summary.get("tfe_full_T10_endpoint_policy_closure_certificate_source_policy_execution_invoked")
        == tfe_endpoint_certificate.get("source_policy_execution_invoked")
        is False
        and summary.get("tfe_full_T10_endpoint_policy_closure_certificate_can_close_now")
        == tfe_endpoint_certificate.get("can_close_now")
        is False,
        "TFE full-T10 endpoint policy closure certificate closure flags changed in manifest summary",
    )
    checks.check(
        summary.get("tfe_source_grid_policy_resolved_for_full_T10") is False
        and summary.get("tfe_source_grid_integer_step_incompatible_rows") == 4
        and summary.get("tfe_source_grid_exact_T_compatible_rows_endpoint_convention_resolved") == 2
        and summary.get("tfe_source_grid_endpoint_incompatible_rows_requiring_policy") == 4
        and summary.get("tfe_source_grid_policy_resolved_for_exact_T_compatible_rows") is True
        and summary.get("tfe_source_grid_source_text_available") is True
        and summary.get("tfe_source_grid_source_text_anchor_count", 0) >= 8
        and summary.get("tfe_source_grid_algorithm_literal_fixed_h") is True
        and summary.get("tfe_source_grid_endpoint_convention_resolved_for_error_sampling") is False,
        "TFE source-grid endpoint evidence not carried into manifest summary",
    )
    checks.check(
        summary.get("tfe_endpoint_sensitivity_status")
        == tfe_endpoint_sensitivity.get("status")
        == "diagnostic_endpoint_policy_sensitivity_not_source_policy",
        "TFE endpoint sensitivity status not carried into manifest summary",
    )
    checks.check(
        summary.get("tfe_endpoint_sensitivity_method_count")
        == tfe_endpoint_sensitivity.get("method_count")
        == 4
        and summary.get("tfe_endpoint_sensitivity_policy_count")
        == tfe_endpoint_sensitivity.get("policy_count")
        == 4
        and summary.get("tfe_endpoint_sensitivity_summary_row_count")
        == tfe_endpoint_sensitivity.get("summary_row_count")
        == 16
        and summary.get("tfe_endpoint_sensitivity_raw_row_count")
        == tfe_endpoint_sensitivity.get("raw_row_count")
        == 48,
        "TFE endpoint sensitivity counts not carried into manifest summary",
    )
    checks.check(
        summary.get("tfe_endpoint_sensitivity_source_policy_rows_completed")
        == tfe_endpoint_sensitivity.get("source_policy_rows_completed")
        == 0
        and summary.get("tfe_endpoint_sensitivity_external_superiority_claim_allowed")
        == tfe_endpoint_sensitivity.get("external_superiority_claim_allowed")
        is False
        and summary.get("tfe_endpoint_sensitivity_source_policy_runner_equivalent")
        == tfe_endpoint_sensitivity.get("source_policy_runner_equivalent")
        is False,
        "TFE endpoint sensitivity overclosed source-policy boundary in manifest summary",
    )
    checks.check(
        summary.get("tfe_endpoint_sensitivity_default_1e_4_campaign_invoked") is False
        and summary.get("tfe_endpoint_sensitivity_run_v047_invoked") is False,
        "TFE endpoint sensitivity invoked a forbidden run in manifest summary",
    )
    checks.check(
        summary.get("tfe_source_pendulum_error_output_policy_encoded") is True,
        "TFE source pendulum output policy progress not carried into manifest",
    )
    checks.check(
        summary.get("tfe_source_pendulum_brown_mcphee_candidate_friction_law_encoded") is True,
        "TFE source pendulum candidate friction progress not carried into manifest",
    )
    checks.check(
        summary.get("tfe_source_pendulum_frictional_candidate_smoke_implemented") is True,
        "TFE source pendulum frictional candidate smoke progress not carried into manifest",
    )
    checks.check(
        summary.get("tfe_brown_mcphee_boundary_status")
        == tfe_brown_mcphee_boundary.get("status")
        == "source_formula_structure_encoded_surrogate_not_source_code_equivalent",
        "TFE Brown-McPhee boundary status not carried into manifest",
    )
    checks.check(
        summary.get("tfe_brown_mcphee_boundary_source_code_equivalent_law") is False
        and summary.get("tfe_brown_mcphee_boundary_transition_velocity_resolved") is False
        and summary.get("tfe_brown_mcphee_boundary_rows_promoted") == 0
        and summary.get("tfe_brown_mcphee_boundary_nonheavy_contract_block_closed") is False,
        "TFE Brown-McPhee boundary overclaims source-policy closure",
    )
    checks.check(
        summary.get("tfe_brown_mcphee_candidate_dae_contract_rows")
        == tfe_brown_mcphee_contract.get("row_count")
        == 12
        and summary.get("tfe_brown_mcphee_candidate_dae_contract_step_rows")
        == tfe_brown_mcphee_contract.get("step_residual_row_count")
        == 56
        and summary.get("tfe_brown_mcphee_candidate_dae_contract_source_policy_rows")
        == tfe_brown_mcphee_contract.get("source_policy_rows_completed")
        == 0,
        "TFE Brown-McPhee candidate DAE contract row boundary changed in manifest summary",
    )
    checks.check(
        summary.get("tfe_brown_mcphee_candidate_dae_contract_all_finite") is True
        and summary.get("tfe_brown_mcphee_candidate_dae_contract_residual_ok") is True
        and summary.get("tfe_brown_mcphee_candidate_dae_contract_power_nonpositive") is True,
        "TFE Brown-McPhee candidate DAE contract finite/residual/power evidence changed",
    )
    checks.check(
        summary.get("tfe_brown_mcphee_candidate_dae_contract_equivalent_dae") is False
        and summary.get("tfe_brown_mcphee_candidate_dae_contract_equivalent_method") is False
        and summary.get("tfe_brown_mcphee_candidate_dae_contract_source_law") is False
        and summary.get("tfe_brown_mcphee_candidate_dae_contract_monolithic") is False,
        "TFE Brown-McPhee candidate DAE contract overclaims source-policy equivalence",
    )
    checks.check(
        summary.get("tfe_brown_mcphee_transition_velocity_sensitivity_rows")
        == tfe_brown_mcphee_velocity_sensitivity.get("endpoint_delta_row_count")
        == 3
        and summary.get("tfe_brown_mcphee_transition_velocity_sensitivity_contract_rows")
        == tfe_brown_mcphee_velocity_sensitivity.get("contract_row_count")
        == 36
        and summary.get("tfe_brown_mcphee_transition_velocity_sensitivity_source_policy_rows")
        == tfe_brown_mcphee_velocity_sensitivity.get("source_policy_rows_completed")
        == 0,
        "TFE Brown-McPhee transition-velocity sensitivity row boundary changed",
    )
    checks.check(
        summary.get("tfe_brown_mcphee_transition_velocity_sensitivity_material") is True
        and summary.get("tfe_brown_mcphee_transition_velocity_sensitivity_equivalence_flags_false")
        is True,
        "TFE Brown-McPhee transition-velocity sensitivity material/equivalence boundary changed",
    )
    checks.check(
        float(summary.get("tfe_brown_mcphee_transition_velocity_sensitivity_max_coordinate_delta", 0.0))
        > 1.0e-6
        and float(summary.get("tfe_brown_mcphee_transition_velocity_sensitivity_max_velocity_delta", 0.0))
        > 1.0e-4,
        "TFE Brown-McPhee transition-velocity sensitivity deltas too small",
    )
    checks.check(
        summary.get("tfe_brown_mcphee_source_code_equivalence_certificate_status")
        == tfe_brown_mcphee_certificate.get("status")
        == "negative_source_code_equivalence_certificate_not_source_policy"
        and summary.get("tfe_brown_mcphee_source_code_equivalence_certificate_available") is True
        and summary.get("tfe_brown_mcphee_source_code_equivalence_certificate_positive") is False
        and summary.get("tfe_brown_mcphee_source_code_equivalence_certificate_nonheavy_block_closed")
        is False,
        "TFE Brown-McPhee source-code equivalence certificate boundary changed in manifest summary",
    )
    checks.check(
        summary.get("tfe_brown_mcphee_source_code_equivalence_certificate_source_policy_execution_invoked")
        == tfe_brown_mcphee_certificate.get("source_policy_execution_invoked")
        is False
        and summary.get("tfe_brown_mcphee_source_code_equivalence_certificate_can_close_now")
        == tfe_brown_mcphee_certificate.get("can_close_now")
        is False,
        "TFE Brown-McPhee source-code equivalence certificate closure flags changed in manifest summary",
    )
    checks.check(
        summary.get("tfe_source_pendulum_setup_subrequirement_closed")
        == tfe_model.get("closure_boundary", {}).get("can_close_source_pendulum_setup_subrequirement")
        is True,
        "TFE source pendulum setup boundary changed",
    )
    checks.check(
        summary.get("direct_pc2_proof_gap_closed")
        == summary.get("proof_gap_closed")
        == proof_checks.get("proof_gap_closed")
        is True
        and summary.get("proof_gap_closed_scope")
        == "direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open"
        and "schema-compatible shorthand for direct_pc2_proof_gap_closed"
        in summary.get("proof_gap_closed_reading_rule", ""),
        "proof gap boundary must be scoped to direct PC2",
    )
    checks.check(
        summary.get("stage_residual_O_h7_implementation_defect_proved")
        == proof_checks.get("stage_residual_O_h7_implementation_defect_proved")
        is True,
        "direct-route stage defect proof boundary changed",
    )
    checks.check(
        summary.get("newton_euler_obligation_coverage_matrix_complete")
        == proof_checks.get("newton_euler_obligation_coverage_matrix_complete")
        is True,
        "Newton-Euler obligation coverage matrix missing from package summary",
    )
    checks.check(
        summary.get("newton_euler_row_obligation_links")
        == proof_checks.get("newton_euler_row_obligation_links")
        == 180,
        "Newton-Euler row-obligation link count changed in package summary",
    )
    checks.check(
        summary.get("newton_euler_rows_with_complete_obligation_sets")
        == proof_checks.get("newton_euler_rows_with_complete_obligation_sets")
        == 36,
        "Newton-Euler complete-row obligation count changed in package summary",
    )
    checks.check(
        summary.get("newton_euler_obligation_coverage_proof_closure_advanced")
        == proof_checks.get("newton_euler_obligation_coverage_proof_closure_advanced")
        is False,
        "Newton-Euler coverage must not close proof in package summary",
    )
    checks.check(
        summary.get("minimal_reproducibility_candidate_present")
        == code_checks.get("minimal_reproducibility_candidate_present")
        is True,
        "minimal reproducibility candidate presence missing from package summary",
    )
    checks.check(
        summary.get("minimal_reproducibility_candidate_status")
        == code_checks.get("minimal_reproducibility_candidate_status")
        == "candidate_replay_package_built_not_submission_ready",
        "minimal reproducibility candidate status changed in package summary",
    )
    checks.check(
        summary.get("minimal_reproducibility_candidate_file_count")
        == code_checks.get("minimal_reproducibility_candidate_file_count")
        == 10,
        "minimal reproducibility candidate file count changed in package summary",
    )
    checks.check(
        summary.get("minimal_reproducibility_candidate_python_file_count")
        == code_checks.get("minimal_reproducibility_candidate_python_file_count")
        == minimal_candidate_source.get("candidate_python_file_count")
        == 1,
        "minimal reproducibility candidate Python file count changed in package summary",
    )
    checks.check(
        summary.get("minimal_reproducibility_candidate_python_lines")
        == code_checks.get("minimal_reproducibility_candidate_python_lines"),
        "minimal reproducibility candidate Python line count changed in package summary",
    )
    checks.check(
        summary.get("minimal_reproducibility_candidate_code_size_ok")
        == code_checks.get("minimal_reproducibility_candidate_code_size_ok")
        is True,
        "minimal reproducibility candidate size gate should remain green",
    )
    checks.check(
        summary.get("minimal_reproducibility_candidate_replay_only")
        == code_checks.get("minimal_reproducibility_candidate_replay_only")
        is True,
        "minimal reproducibility candidate replay-only marker changed in package summary",
    )
    checks.check(
        summary.get("minimal_reproducibility_candidate_runner_centered")
        == code_checks.get("minimal_reproducibility_candidate_runner_centered")
        is False,
        "minimal reproducibility candidate unexpectedly runner-centered in package summary",
    )
    checks.check(
        summary.get("minimal_reproducibility_candidate_source_policy_ready")
        == code_checks.get("minimal_reproducibility_candidate_source_policy_ready")
        is False,
        "minimal reproducibility candidate unexpectedly source-policy ready in package summary",
    )
    checks.check(
        summary.get("minimal_reproducibility_candidate_proof_ready")
        == code_checks.get("minimal_reproducibility_candidate_proof_ready")
        is True,
        "minimal reproducibility candidate proof-ready marker missing in package summary",
    )
    checks.check(summary.get("minimal_reproducible_submission_code_ready") is False, "minimal package overclaimed")
    checks.check(
        summary.get("runner_centered_audit_status")
        == runner_centered_audit_source.get("status")
        == "local_runner_centered_candidate_ready_source_policy_package_open",
        "runner-centered audit status not carried into package summary",
    )
    checks.check(
        summary.get("runner_centered_package_ready")
        == runner_centered_audit_source.get("runner_centered_package_ready")
        is False,
        "runner-centered package readiness overclaimed in package summary",
    )
    checks.check(
        summary.get("local_runner_centered_candidate_ready")
        == runner_centered_audit_source.get("local_runner_centered_candidate_ready")
        is True,
        "local runner-centered candidate readiness missing in package summary",
    )
    checks.check(
        summary.get("full_source_policy_runner_package_ready")
        == runner_centered_audit_source.get("full_source_policy_runner_package_ready")
        is False,
        "full source-policy runner package readiness overclaimed in package summary",
    )
    checks.check(
        summary.get("runner_centered_existing_source_lines")
        == runner_centered_audit_source.get("existing_runner_source_total_python_lines"),
        "runner-centered source line count stale in package summary",
    )
    checks.check(
        summary.get("runner_adapter_candidate_status")
        == runner_adapter_source.get("status")
        == "runner_adapter_candidate_external_v048_required_not_submission_ready",
        "runner-adapter status not carried into package summary",
    )
    checks.check(
        summary.get("runner_adapter_present") == runner_adapter_source.get("runner_adapter_present") is True,
        "runner-adapter marker not carried into package summary",
    )
    checks.check(
        summary.get("runner_adapter_self_contained_simulation_runner")
        == runner_adapter_source.get("self_contained_simulation_runner")
        is False,
        "runner-adapter self-contained boundary overclaimed in package summary",
    )
    checks.check(
        summary.get("runner_adapter_python_lines")
        == runner_adapter_source.get("candidate_python_line_count"),
        "runner-adapter Python line count stale in package summary",
    )
    checks.check(
        summary.get("runner_adapter_python_file_count")
        == runner_adapter_source.get("candidate_python_file_count")
        == 2,
        "runner-adapter Python file count stale in package summary",
    )
    checks.check(
        summary.get("runner_adapter_closed_loop_local_rows_replay_present")
        == runner_adapter_source.get("closed_loop_local_rows_replay_present")
        is True,
        "runner-adapter closed-loop local replay marker not carried into package summary",
    )
    checks.check(
        summary.get("runner_adapter_closed_loop_local_rows_summary_present")
        == runner_adapter_source.get("closed_loop_local_rows_summary_present")
        is True,
        "runner-adapter closed-loop local replay summary marker not carried into package summary",
    )
    checks.check(
        summary.get("runner_adapter_closed_loop_local_rows")
        == runner_adapter_source.get("closed_loop_local_rows")
        == 6,
        "runner-adapter closed-loop local row count not carried into package summary",
    )
    checks.check(
        summary_closed_loop_models == runner_adapter_closed_loop_models == {"four_link", "slider_crank"},
        "runner-adapter closed-loop local models not carried into package summary",
    )
    checks.check(
        summary.get("self_contained_runner_extraction_plan_status")
        == extraction_plan_source.get("status")
        == "local_accepted_rows_self_contained_runner_ready_source_policy_package_open",
        "self-contained runner extraction plan status not carried into package summary",
    )
    checks.check(
        summary.get("self_contained_runner_ready")
        == extraction_plan_source.get("self_contained_runner_ready")
        is False,
        "self-contained runner readiness overclaimed in package summary",
    )
    checks.check(
        summary.get("local_accepted_rows_self_contained_runner_ready")
        == extraction_plan_source.get("local_accepted_rows_self_contained_runner_ready")
        is True,
        "local accepted-row self-contained runner readiness missing in package summary",
    )
    checks.check(
        summary.get("full_source_policy_self_contained_runner_ready")
        == extraction_plan_source.get("full_source_policy_self_contained_runner_ready")
        is False,
        "full source-policy self-contained runner readiness overclaimed in package summary",
    )
    checks.check(
        summary.get("b6_final_prose_pass_ready")
        == extraction_plan_source.get("b6_final_prose_pass_ready")
        is True,
        "B6 narrowed-claim final prose readiness missing in package summary",
    )
    checks.check(
        summary.get("b6_final_prose_pass_scope")
        == extraction_plan_source.get("b6_final_prose_pass_scope")
        == "narrowed_claim_current_submission",
        "B6 prose scope missing in package summary",
    )
    checks.check(
        summary.get("full_source_policy_b6_prose_ready")
        == extraction_plan_source.get("full_source_policy_b6_prose_ready")
        is False,
        "full source-policy B6 prose readiness overclaimed in package summary",
    )
    checks.check(
        summary.get("b6_closure_preflight_status")
        == extraction_plan_source.get("b6_closure_preflight_status")
        == "b6_final_prose_pass_closed_under_narrowed_b4_b7_scope"
        and summary.get("b6_closure_allowed_now") == extraction_plan_source.get("b6_closure_allowed_now") is True,
        "B6 closure preflight not carried into package summary",
    )
    summary_runner_package_boundary = summary.get("self_contained_runner_package_boundary", {})
    source_runner_package_boundary = extraction_plan_source.get("runner_package_boundary", {})
    checks.check(
        summary_runner_package_boundary == source_runner_package_boundary
        and summary_runner_package_boundary.get("local_accepted_rows_self_contained") is True
        and summary_runner_package_boundary.get("full_source_policy_self_contained") is False
        and summary_runner_package_boundary.get("b6_final_prose_pass_ready") is True
        and summary_runner_package_boundary.get("b6_final_prose_pass_scope") == "narrowed_claim_current_submission"
        and summary_runner_package_boundary.get("full_source_policy_b6_prose_ready") is False
        and summary_runner_package_boundary.get("b6_closure_allowed_now") is True
        and summary_runner_package_boundary.get("source_policy_rows_closed") == 0
        and summary_runner_package_boundary.get("source_policy_rows_total") == 40,
        "self-contained runner local/full package boundary stale in package summary",
    )
    checks.check(
        summary.get("self_contained_runner_target_symbol_count")
        == extraction_plan_source.get("target_symbol_count"),
        "self-contained runner symbol count stale in package summary",
    )
    checks.check(
        summary.get("self_contained_runner_target_symbol_lines")
        == extraction_plan_source.get("target_symbol_lines"),
        "self-contained runner symbol line count stale in package summary",
    )
    checks.check(
        summary.get("p1_single_runner_candidate_ready")
        == p1_local_runner_audit_source.get("p1_single_runner_candidate_ready")
        is True,
        "P1 single-runner candidate readiness not carried into package summary",
    )
    checks.check(
        summary.get("p1_double_runner_candidate_ready")
        == p1_local_runner_audit_source.get("p1_double_runner_candidate_ready")
        is True,
        "P1 double-runner candidate readiness not carried into package summary",
    )
    checks.check(
        summary.get("p1_regenerated_candidate_rows")
        == p1_local_runner_audit_source.get("p1_regenerated_candidate_rows")
        == 6,
        "P1 regenerated candidate row count changed in package summary",
    )
    checks.check(
        summary.get("p1_required_rows") == p1_local_runner_audit_source.get("p1_required_rows") == 6,
        "P1 required row count changed in package summary",
    )
    checks.check(
        summary.get("p1_missing_candidate_rows") == p1_local_runner_audit_source.get("p1_missing_candidate_rows") == 0,
        "P1 missing row count changed in package summary",
    )
    checks.check(
        summary.get("p1_single_runner_candidate_rows") == p1_single_candidate_source.get("rows") == 3,
        "P1 single-runner row count not carried into package summary",
    )
    checks.check(
        summary.get("p1_single_runner_candidate_status")
        == p1_single_candidate_source.get("status")
        == "single_runner_candidate_not_p1_complete",
        "P1 single-runner candidate status not carried into package summary",
    )
    checks.check(
        float(summary.get("p1_single_runner_candidate_position_order", 0.0)) > 5.0,
        "P1 single-runner position order too low in package summary",
    )
    checks.check(
        float(summary.get("p1_single_runner_candidate_velocity_order", 0.0)) > 5.0,
        "P1 single-runner velocity order too low in package summary",
    )
    checks.check(
        summary.get("p1_single_runner_candidate_imports_v047_or_v048") is False,
        "P1 single-runner import boundary overclaimed in package summary",
    )
    checks.check(
        summary.get("p1_single_runner_candidate_p1_complete") is False,
        "P1 single-runner overclaims P1 completion in package summary",
    )
    checks.check(
        summary.get("p1_double_runner_candidate_rows") == p1_double_candidate_source.get("rows") == 3,
        "P1 double-runner row count not carried into package summary",
    )
    checks.check(
        summary.get("p1_double_runner_candidate_status")
        == p1_double_candidate_source.get("status")
        == "double_runner_candidate_not_source_policy_or_proof_complete",
        "P1 double-runner candidate status not carried into package summary",
    )
    checks.check(
        float(summary.get("p1_double_runner_candidate_position_order", 0.0)) > 5.0,
        "P1 double-runner position order too low in package summary",
    )
    checks.check(
        float(summary.get("p1_double_runner_candidate_velocity_order", 0.0)) > 5.0,
        "P1 double-runner velocity order too low in package summary",
    )
    checks.check(
        summary.get("p1_double_runner_candidate_imports_v047_v048_or_v029") is False,
        "P1 double-runner import boundary overclaimed in package summary",
    )
    checks.check(
        summary.get("p1_double_runner_candidate_p1_complete") is False,
        "P1 double-runner overclaims P1 completion in package summary",
    )
    checks.check(
        summary.get("human_runnable_local_evidence_example_count") == 4,
        "human-runnable local evidence example count changed",
    )
    checks.check(
        summary_local_evidence_examples == {"single_pendulum", "double_pendulum", "four_link", "slider_crank"},
        "human-runnable local evidence examples are not synchronized",
    )
    checks.check(
        summary_self_contained_examples == {"single_pendulum", "double_pendulum", "four_link", "slider_crank"},
        "human-runnable self-contained local examples should include all four local examples",
    )
    checks.check(
        summary_replay_only_examples == set(),
        "human-runnable replay-only local examples should be empty after compact closed-loop candidate",
    )
    checks.check(
        summary.get("human_runnable_four_example_local_evidence_available") is True,
        "human-runnable four-example local evidence should be available",
    )
    checks.check(
        summary.get("human_runnable_four_example_self_contained_simulation_ready") is True,
        "human-runnable four-example self-contained simulation readiness missing",
    )
    checks.check(
        summary.get("b6_closed_loop_extraction_audit_status")
        == closed_loop_audit_source.get("status")
        == "closed_loop_self_contained_runner_candidate_ready_source_policy_open",
        "B6 closed-loop extraction audit status not carried into package summary",
    )
    checks.check(
        summary.get("b6_closed_loop_extraction_ready") is True,
        "B6 closed-loop extraction compact readiness missing in package summary",
    )
    checks.check(
        summary.get("b6_closed_loop_extraction_target_source_files")
        == closed_loop_audit_source.get("target_source_file_count")
        == 2,
        "B6 closed-loop target source-file count stale in package summary",
    )
    checks.check(
        summary.get("b6_closed_loop_extraction_target_symbols")
        == closed_loop_audit_source.get("target_symbol_count")
        >= 30,
        "B6 closed-loop target symbol count stale in package summary",
    )
    checks.check(
        summary.get("b6_closed_loop_extraction_target_symbol_lines")
        == closed_loop_audit_source.get("target_symbol_lines"),
        "B6 closed-loop target symbol line count stale in package summary",
    )
    checks.check(
        summary.get("b6_closed_loop_extraction_replay_only_examples", []) == [],
        "B6 closed-loop replay-only examples changed in package summary",
    )
    checks.check(
        summary.get("b6_closed_loop_extraction_run_v047_invoked") is False
        and summary.get("b6_closed_loop_extraction_run_v048_invoked") is False
        and summary.get("b6_closed_loop_extraction_b4_opt_in_required") is False,
        "B6 closed-loop extraction execution boundary changed in package summary",
    )
    checks.check(
        summary.get("compact_closed_loop_candidate_status")
        == closed_loop_candidate_source.get("status")
        == "closed_loop_local_runner_candidate_passed_compact",
        "compact closed-loop candidate status not carried into package summary",
    )
    checks.check(
        summary.get("compact_closed_loop_candidate_runner_passed") is True
        and summary.get("compact_closed_loop_candidate_self_contained_simulation_runner") is True,
        "compact closed-loop candidate pass/self-contained marker missing in package summary",
    )
    checks.check(
        summary.get("compact_closed_loop_candidate_python_files") == 10
        and 0 < summary.get("compact_closed_loop_candidate_python_lines", 0) <= 2000
        and summary.get("compact_closed_loop_candidate_line_limit_ok") is True,
        "compact closed-loop candidate size boundary not carried into package summary",
    )
    checks.check(
        summary.get("compact_closed_loop_candidate_rows") == 6
        and set(summary.get("compact_closed_loop_candidate_models", [])) == {"four_link", "slider_crank"}
        and summary.get("compact_closed_loop_candidate_imports_v046_v047_v048_or_v029") is False,
        "compact closed-loop candidate rows/models/import boundary stale in package summary",
    )
    checks.check(
        summary.get("b6_four_example_local_evidence_runner_passed")
        == b6_local_evidence_source.get("b6_local_evidence_runner_passed")
        is True,
        "B6 local-evidence runner pass marker missing in package summary",
    )
    checks.check(
        summary.get("b6_four_example_local_rows") == b6_local_evidence_source.get("local_rows") == 12,
        "B6 local-evidence row count changed in package summary",
    )
    checks.check(
        set(summary.get("b6_four_example_self_contained_examples", []))
        == {"single_pendulum", "double_pendulum", "four_link", "slider_crank"},
        "B6 self-contained examples changed in package summary",
    )
    checks.check(
        summary.get("b6_four_example_replay_only_examples", []) == [],
        "B6 replay-only examples changed in package summary",
    )
    checks.check(
        summary.get("b6_four_example_self_contained_simulation_ready") is True,
        "B6 four-example self-contained simulation readiness missing in package summary",
    )
    checks.check(
        summary.get("b6_four_example_source_policy_rows_closed") == 0
        and summary.get("b6_four_example_source_policy_rows_total") == 40,
        "B6 source-policy row boundary changed in package summary",
    )
    checks.check(
        summary.get("b6_four_example_proof_gap_closed") is True,
        "B6 proof boundary missing in package summary",
    )
    checks.check(
        summary.get("local_accepted_runner_companion_status")
        == local_runner_companion_source.get("status")
        == "local_accepted_runner_companion_ready_source_policy_package_open",
        "local accepted-row runner companion status not carried into package summary",
    )
    checks.check(
        summary.get("local_accepted_runner_companion_launcher_passed") is True
        and summary.get("local_accepted_runner_companion_local_rows") == 12
        and 1 <= int(summary.get("local_accepted_runner_companion_python_lines", 0)) <= 220,
        "local accepted-row runner companion launch/size summary stale",
    )
    checks.check(
        summary.get("local_accepted_runner_companion_source_policy_rows_closed") == 0
        and summary.get("local_accepted_runner_companion_source_policy_rows_total") == 40
        and summary.get("local_accepted_runner_companion_full_source_policy_ready") is False,
        "local accepted-row runner companion source-policy summary stale",
    )
    checks.check(
        summary.get("narrowed_reproducibility_package_audit_status")
        == narrowed_repro_audit_source.get("status")
        == "narrowed_claim_reproducibility_package_ready_full_source_policy_open",
        "narrowed reproducibility package status stale",
    )
    checks.check(
        summary.get("narrowed_claim_reproducibility_package_ready")
        == narrowed_repro_audit_source.get("narrowed_claim_reproducibility_package_ready")
        is True,
        "narrowed reproducibility package readiness stale",
    )
    checks.check(
        summary.get("narrowed_reproducibility_package_source_policy_rows_closed") == 0
        and summary.get("narrowed_reproducibility_package_source_policy_rows_total") == 40
        and summary.get("narrowed_reproducibility_package_full_source_policy_runner_ready") is False,
        "narrowed reproducibility package source-policy boundary stale",
    )
    checks.check(
        summary.get("narrowed_repro_code_archive_status")
        == narrowed_repro_code_archive_source.get("status")
        == "narrowed_repro_code_archive_ready_source_policy_open",
        "narrowed repro code archive status stale",
    )
    checks.check(
        summary.get("narrowed_repro_code_archive_entry_count")
        == narrowed_repro_code_archive_source.get("entry_count")
        and summary.get("narrowed_repro_code_archive_python_files")
        == narrowed_repro_code_archive_source.get("python_file_count")
        and summary.get("narrowed_repro_code_archive_python_lines")
        == narrowed_repro_code_archive_source.get("python_line_count"),
        "narrowed repro code archive inventory summary stale",
    )
    checks.check(
        summary.get("narrowed_repro_code_archive_source_policy_rows_closed") == 0
        and summary.get("narrowed_repro_code_archive_source_policy_rows_total") == 40
        and summary.get("narrowed_repro_code_archive_full_source_policy_runner_ready") is False
        and summary.get("narrowed_repro_code_archive_submission_ready") is False,
        "narrowed repro code archive source-policy/submission boundary stale",
    )
    checks.check(
        summary.get("research_audit_primary_submission_line_limit")
        == code_checks.get("research_audit_primary_submission_line_limit")
        == 20000,
        "research-audit line limit changed in package summary",
    )
    checks.check(
        summary.get("research_audit_repo_too_large_for_primary_submission")
        == code_checks.get("research_audit_repo_too_large_for_primary_submission")
        is True,
        "research-audit size risk changed in package summary",
    )
    checks.check(
        summary.get("research_audit_repo_primary_submission_allowed")
        == code_checks.get("research_audit_repo_primary_submission_allowed")
        is False,
        "research audit tree must not be primary submission code",
    )
    checks.check(
        summary.get("research_audit_repo_provenance_only")
        == code_checks.get("research_audit_repo_provenance_only")
        is True,
        "research audit tree provenance-only marker changed",
    )
    checks.check(
        summary.get("reviewer_facing_python_line_limit")
        == code_checks.get("reviewer_facing_python_line_limit")
        == 2000,
        "reviewer-facing line limit changed in package summary",
    )
    checks.check(
        summary.get("reviewer_facing_python_file_limit")
        == code_checks.get("reviewer_facing_python_file_limit")
        == 12,
        "reviewer-facing file limit changed in package summary",
    )
    checks.check(summary.get("code_bloat_risk_for_submission") is True, "code bloat risk should remain visible")
    checks.check(summary.get("combined_python_line_count") == code_checks.get("combined_python_line_count"), "line count stale")
    checks.check(
        reviewer_code_policy.get("primary_submission_package_required") is True,
        "reviewer-facing code policy must require a primary minimal package",
    )
    checks.check(
        reviewer_code_policy.get("research_audit_tree_primary_submission_allowed") is False
        and reviewer_code_policy.get("research_audit_tree_provenance_only") is True,
        "reviewer-facing code policy lost audit-tree boundary",
    )
    checks.check(
        reviewer_code_policy.get("research_audit_tree_too_large_for_primary_submission") is True
        and reviewer_code_policy.get("research_audit_tree_line_limit") == 20000,
        "reviewer-facing code policy lost audit-tree size gate",
    )
    checks.check(
        reviewer_code_policy.get("reviewer_facing_python_file_limit") == 12
        and reviewer_code_policy.get("reviewer_facing_python_line_limit") == 2000,
        "reviewer-facing code policy limits changed",
    )
    checks.check(
        reviewer_code_policy.get("candidate_code_size_ok") is True
        and reviewer_code_policy.get("candidate_runner_centered") is False
        and reviewer_code_policy.get("candidate_replay_only") is True,
        "reviewer-facing code policy misstates candidate boundary",
    )
    checks.check(
        reviewer_code_policy.get("candidate_source_policy_ready") is False
        and reviewer_code_policy.get("candidate_proof_ready") is True
        and reviewer_code_policy.get("minimal_reproducible_submission_code_ready") is False,
        "reviewer-facing code policy boundary changed",
    )
    checks.check(
        reviewer_code_policy.get("minimal_submission_code_dependency_boundary")
        == minimal_submission_code_boundary,
        "reviewer-facing code policy lost minimal submission dependency boundary",
    )
    checks.check(
        minimal_submission_code_boundary.get("schema")
        == "minimal-submission-code-dependency-boundary-v1"
        and minimal_submission_code_boundary.get("status")
        == "narrowed_repro_ready_full_source_policy_package_blocked",
        "minimal submission code dependency boundary schema/status changed",
    )
    checks.check(
        summary.get("minimal_submission_code_dependency_boundary_status")
        == minimal_submission_code_boundary.get("status")
        and summary.get("minimal_submission_code_dependency_safe_use")
        == minimal_submission_code_boundary.get("safe_current_package_use")
        and summary.get("minimal_submission_code_dependency_primary_allowed")
        == minimal_submission_code_boundary.get("primary_submission_package_allowed")
        is False,
        "minimal submission code dependency boundary summary fields stale",
    )
    checks.check(
        summary.get("minimal_submission_code_dependency_blockers")
        == minimal_submission_code_boundary.get("blocking_objective_requirements")
        == ["OC4", "OC6", "OC12"],
        "minimal submission code dependency blocker chain changed",
    )
    checks.check(
        minimal_submission_code_boundary.get("minimal_reproducible_submission_code_ready") is False
        and minimal_submission_code_boundary.get("narrowed_claim_reproducibility_package_ready") is True
        and minimal_submission_code_boundary.get("narrowed_repro_code_archive_ready") is True
        and minimal_submission_code_boundary.get("narrowed_repro_code_archive_submission_ready") is False
        and minimal_submission_code_boundary.get("local_runner_centered_candidate_ready") is True
        and minimal_submission_code_boundary.get("runner_centered_package_ready") is False
        and minimal_submission_code_boundary.get("full_source_policy_runner_package_ready") is False,
        "minimal submission code dependency readiness boundary changed",
    )
    checks.check(
        minimal_submission_code_boundary.get("candidate_code_size_ok") is True
        and minimal_submission_code_boundary.get("candidate_replay_only") is True
        and minimal_submission_code_boundary.get("candidate_runner_centered") is False
        and minimal_submission_code_boundary.get("candidate_source_policy_ready") is False
        and minimal_submission_code_boundary.get("candidate_proof_ready") is True,
        "minimal submission code dependency candidate flags changed",
    )
    checks.check(
        minimal_submission_code_boundary.get("source_policy_rows_closed") == 0
        and minimal_submission_code_boundary.get("source_policy_rows_total") == 40
        and minimal_submission_code_boundary.get("narrowed_archive_source_policy_rows_closed") == 0
        and minimal_submission_code_boundary.get("narrowed_archive_source_policy_rows_total") == 40,
        "minimal submission code dependency source-policy rows changed",
    )
    checks.check(
        minimal_submission_code_boundary.get("blocking_upstream_gates")
        == [
            "OC4_source_policy_reproduction_rows",
            "OC6_TFE_source_policy_runner",
            "OC12_full_source_policy_runner_archive",
        ]
        and minimal_submission_code_boundary.get("safe_current_package_use")
        == "narrowed_claim_replay_and_audit_provenance_only"
        and minimal_submission_code_boundary.get("audit_tree_provenance_only") is True
        and minimal_submission_code_boundary.get("audit_tree_too_large_for_primary_submission") is True
        and minimal_submission_code_boundary.get("reviewer_facing_size_limits")
        == {"python_files": 12, "python_lines": 2000},
        "minimal submission code dependency reviewer-facing policy changed",
    )
    proof_writing_card = proof_claim_traceability.get("proof_writing_boundary_card", {})
    checks.check(
        strict_proof_boundary == objective_strict_proof_boundary,
        "package manifest strict proof-writing boundary diverged from objective audit",
    )
    checks.check(
        strict_proof_boundary.get("schema") == "strict-proof-writing-submission-boundary-v1"
        and strict_proof_boundary.get("status")
        == "proof_writing_traceable_global_submission_blocked_by_source_policy_tfe_package"
        and summary.get("strict_proof_writing_submission_boundary_status")
        == strict_proof_boundary.get("status"),
        "strict proof-writing submission boundary schema/status changed",
    )
    checks.check(
        strict_proof_boundary.get("proof_writing_card_status")
        == summary.get("strict_proof_writing_card_status")
        == proof_writing_card.get("status")
        == "conditional_theorem_traceable_direct_pc2_closed_global_boundaries_retained",
        "strict proof-writing card status not propagated into package manifest",
    )
    checks.check(
        strict_proof_boundary.get("reader_facing_manuscript_boundary_present")
        == summary.get("strict_proof_writing_reader_facing_manuscript_boundary_present")
        == proof_writing_card.get("reader_facing_manuscript_boundary_present")
        == proof.get("theorem_statement_boundary", {}).get(
            "all_required_labels_present_main_and_flat"
        )
        == proof.get("theorem_statement_boundary", {}).get(
            "conditional_theorem_boundary_present_main_and_flat"
        )
        == proof.get("manuscript_traceability", {}).get(
            "conditional_proof_claims_mapped_to_manuscript"
        )
        == proof_claim_traceability.get("remaining_claim_boundary", {}).get(
            "reader_facing_manuscript_boundary_present"
        )
        == proof_claim_traceability.get("summary", {}).get("reader_facing_proof_claim_boundary_present")
        is True,
        "strict proof-writing reader-facing boundary not propagated into package manifest",
    )
    checks.check(
        strict_proof_boundary.get("p7_retained_nonpromotion_boundary_present")
        == summary.get("strict_proof_writing_p7_retained_nonpromotion_boundary_present")
        == proof_writing_card.get("p7_retained_nonpromotion_boundary_present")
        == proof.get("theorem_statement_boundary", {}).get(
            "does_not_promote_residual_to_error"
        )
        == proof.get("manuscript_traceability", {}).get(
            "residual_to_error_nonpromotion_present_main_and_flat"
        )
        == proof.get("p7_residual_to_error_obligation_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        == proof_claim_traceability.get("remaining_claim_boundary", {}).get(
            "p7_retained_nonpromotion_boundary_present"
        )
        == proof_claim_traceability.get("summary", {}).get("p7_retained_nonpromotion_boundary_present")
        is True,
        "strict proof-writing P7 output nonclaim/residual-to-error boundary not propagated into package manifest",
    )
    checks.check(
        strict_proof_boundary.get("b1_closure_scope_boundary_present")
        == summary.get("strict_proof_writing_b1_closure_scope_boundary_present")
        == proof_writing_card.get("b1_closure_scope_boundary_present")
        == proof.get("b1_ad_expanded_closure_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        == proof_claim_traceability.get("remaining_claim_boundary", {}).get(
            "b1_closure_scope_boundary_present"
        )
        == proof_claim_traceability.get("summary", {}).get("b1_closure_scope_boundary_present")
        is True,
        "strict proof-writing B1 closure-scope boundary not propagated into package manifest",
    )
    checks.check(
        strict_proof_boundary.get("b1_ad_expanded_closure_ledger_present")
        == summary.get("strict_proof_writing_b1_ad_expanded_closure_ledger_present")
        == objective_strict_proof_boundary.get("b1_ad_expanded_closure_ledger_present")
        == proof.get("b1_ad_expanded_closure_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        is True,
        "strict proof-writing B1 AD-expanded closure ledger not propagated into package manifest",
    )
    checks.check(
        strict_proof_boundary.get("b1_ad_expanded_symbolic_oracle_closed_cells")
        == summary.get("strict_proof_writing_b1_ad_expanded_symbolic_oracle_closed_cells")
        == objective_strict_proof_boundary.get(
            "b1_ad_expanded_symbolic_oracle_closed_cells"
        )
        == proof.get("evidence_summary", {}).get(
            "b1_ad_expanded_symbolic_oracle_closed_cells"
        )
        == 4752,
        "strict proof-writing B1 AD-expanded derivative-cell count not propagated into package manifest",
    )
    checks.check(
        strict_proof_boundary.get("p6_solver_scope_boundary_present")
        == summary.get("strict_proof_writing_p6_solver_scope_boundary_present")
        == proof_writing_card.get("p6_solver_scope_boundary_present")
        == proof_claim_traceability.get("remaining_claim_boundary", {}).get(
            "p6_solver_scope_boundary_present"
        )
        == proof_claim_traceability.get("summary", {}).get("p6_solver_scope_boundary_present")
        == proof.get("p6_solver_scope_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        is True,
        "strict proof-writing P6 solver-scope boundary not propagated into package manifest",
    )
    checks.check(
        strict_proof_boundary.get("p1p2_compact_tube_boundary_present")
        == summary.get("strict_proof_writing_p1p2_compact_tube_boundary_present")
        == proof_writing_card.get("p1p2_compact_tube_boundary_present")
        == proof.get("p1p2_compact_tube_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        == proof_claim_traceability.get("remaining_claim_boundary", {}).get(
            "p1p2_compact_tube_boundary_present"
        )
        == proof_claim_traceability.get("summary", {}).get("p1p2_compact_tube_boundary_present")
        is True,
        "strict proof-writing P1/P2 compact-tube boundary not propagated into package manifest",
    )
    checks.check(
        strict_proof_boundary.get("p3p4_implementation_boundary_present")
        == summary.get("strict_proof_writing_p3p4_implementation_boundary_present")
        == proof_writing_card.get("p3p4_implementation_boundary_present")
        == proof.get("p3p4_implementation_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        == proof_claim_traceability.get("remaining_claim_boundary", {}).get(
            "p3p4_implementation_boundary_present"
        )
        == proof_claim_traceability.get("summary", {}).get("p3p4_implementation_boundary_present")
        is True,
        "strict proof-writing P3/P4 implementation-defect boundary not propagated into package manifest",
    )
    checks.check(
        strict_proof_boundary.get("p5_direct_route_boundary_present")
        == summary.get("strict_proof_writing_p5_direct_route_boundary_present")
        == proof_writing_card.get("p5_direct_route_boundary_present")
        == proof.get("p5_direct_route_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        == proof_claim_traceability.get("remaining_claim_boundary", {}).get(
            "p5_direct_route_boundary_present"
        )
        == proof_claim_traceability.get("summary", {}).get("p5_direct_route_boundary_present")
        is True,
        "strict proof-writing P5 direct-route boundary not propagated into package manifest",
    )
    checks.check(
        strict_proof_boundary.get("p_interface_satisfaction_ledger_present")
        == summary.get("strict_proof_writing_p_interface_satisfaction_ledger_present")
        == proof_writing_card.get("p_interface_satisfaction_ledger_present")
        == proof_claim_traceability.get("remaining_claim_boundary", {}).get(
            "p_interface_satisfaction_ledger_present"
        )
        == proof_claim_traceability.get("summary", {}).get(
            "p_interface_satisfaction_ledger_present"
        )
        == proof.get("p_interface_satisfaction_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        is True,
        "strict proof-writing theorem-interface satisfaction ledger not propagated into package manifest",
    )
    checks.check(
        strict_proof_boundary.get("p7_residual_to_error_ledger_present")
        == summary.get("strict_proof_writing_p7_residual_to_error_ledger_present")
        == proof_writing_card.get("p7_residual_to_error_ledger_present")
        == proof_claim_traceability.get("remaining_claim_boundary", {}).get(
            "p7_residual_to_error_ledger_present"
        )
        == proof_claim_traceability.get("summary", {}).get(
            "p7_residual_to_error_ledger_present"
        )
        == proof.get("p7_residual_to_error_obligation_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        is True,
        "strict proof-writing P7 residual-to-error obligation ledger not propagated into package manifest",
    )
    checks.check(
        strict_proof_boundary.get("theorem_use_rule_present")
        == summary.get("strict_proof_writing_theorem_use_rule_present")
        == proof_writing_card.get("theorem_use_rule_present")
        == proof.get("theorem_use_rule_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        == proof_claim_traceability.get("remaining_claim_boundary", {}).get(
            "theorem_use_rule_present"
        )
        == proof_claim_traceability.get("summary", {}).get(
            "theorem_use_rule_present"
        )
        is True,
        "strict proof-writing theorem-use rule not propagated into package manifest",
    )
    checks.check(
        strict_proof_boundary.get("quantifier_domain_ledger_present")
        == summary.get("strict_proof_writing_quantifier_domain_ledger_present")
        == proof_writing_card.get("quantifier_domain_ledger_present")
        == proof.get("quantifier_domain_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        == proof_claim_traceability.get("remaining_claim_boundary", {}).get(
            "quantifier_domain_ledger_present"
        )
        == proof_claim_traceability.get("summary", {}).get(
            "quantifier_domain_ledger_present"
        )
        is True,
        "strict proof-writing quantifier/domain ledger not propagated into package manifest",
    )
    checks.check(
        strict_proof_boundary.get("local_global_transfer_ledger_present")
        == summary.get("strict_proof_writing_local_global_transfer_ledger_present")
        == proof_writing_card.get("local_global_transfer_ledger_present")
        == proof.get("local_global_transfer_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        == proof_claim_traceability.get("remaining_claim_boundary", {}).get(
            "local_global_transfer_ledger_present"
        )
        == proof_claim_traceability.get("summary", {}).get(
            "local_global_transfer_ledger_present"
        )
        is True,
        "strict proof-writing local-to-global transfer ledger not propagated into package manifest",
    )
    checks.check(
        strict_proof_boundary.get("objective_completion_boundary_present")
        == summary.get("strict_proof_writing_objective_completion_boundary_present")
        == proof_writing_card.get("objective_completion_boundary_present")
        == proof_claim_traceability.get("remaining_claim_boundary", {}).get(
            "objective_completion_boundary_present"
        )
        == proof_claim_traceability.get("summary", {}).get(
            "objective_completion_boundary_present"
        )
        is True
        and proof.get("readiness_boundary", {}).get("proof_closure_manifest_scope")
        == "direct_pc2_closure_and_theorem_condition_traceability"
        and proof.get("readiness_boundary", {}).get(
            "global_submission_boundaries_retained"
        )
        == [
            "full_source_policy_package_ready",
            "theorem_level_eta_h_solver_policy_evidence",
            "closed_residual_to_error_theorem_for_mechanism_rows",
        ],
        "strict proof-writing objective-completion boundary not propagated into package manifest",
    )
    checks.check(
        strict_proof_boundary.get("constant_dependency_ledger_present")
        == summary.get("strict_proof_writing_constant_dependency_ledger_present")
        == proof_writing_card.get("constant_dependency_ledger_present")
        == proof.get("constant_dependency_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        == proof_claim_traceability.get("remaining_claim_boundary", {}).get(
            "constant_dependency_ledger_present"
        )
        == proof_claim_traceability.get("summary", {}).get(
            "constant_dependency_ledger_present"
        )
        is True,
        "strict proof-writing constant-dependency ledger not propagated into package manifest",
    )
    checks.check(
        strict_proof_boundary.get("theorem_dependency_consumption_ledger_present")
        == summary.get(
            "strict_proof_writing_theorem_dependency_consumption_ledger_present"
        )
        == proof_writing_card.get("theorem_dependency_consumption_ledger_present")
        == proof.get("theorem_dependency_consumption_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        == proof_claim_traceability.get("remaining_claim_boundary", {}).get(
            "theorem_dependency_consumption_ledger_present"
        )
        == proof_claim_traceability.get("summary", {}).get(
            "theorem_dependency_consumption_ledger_present"
        )
        is True,
        "strict proof-writing theorem dependency consumption ledger not propagated into package manifest",
    )
    checks.check(
        strict_proof_boundary.get("branch_consistency_ledger_present")
        == summary.get("strict_proof_writing_branch_consistency_ledger_present")
        == proof_writing_card.get("branch_consistency_ledger_present")
        == proof.get("branch_consistency_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        == proof_claim_traceability.get("remaining_claim_boundary", {}).get(
            "branch_consistency_ledger_present"
        )
        == proof_claim_traceability.get("summary", {}).get(
            "branch_consistency_ledger_present"
        )
        is True,
        "strict proof-writing accepted-branch consistency ledger not propagated into package manifest",
    )
    checks.check(
        strict_proof_boundary.get("implementation_route_oracle_ledger_present")
        == summary.get(
            "strict_proof_writing_implementation_route_oracle_ledger_present"
        )
        == proof_writing_card.get("implementation_route_oracle_ledger_present")
        == proof.get("implementation_route_oracle_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        == proof_claim_traceability.get("remaining_claim_boundary", {}).get(
            "implementation_route_oracle_ledger_present"
        )
        == proof_claim_traceability.get("summary", {}).get(
            "implementation_route_oracle_ledger_present"
        )
        is True,
        "strict proof-writing implementation-route/oracle separation ledger not propagated into package manifest",
    )
    checks.check(
        strict_proof_boundary.get("nonlinear_solver_scale_ledger_present")
        == summary.get("strict_proof_writing_nonlinear_solver_scale_ledger_present")
        == proof_writing_card.get("nonlinear_solver_scale_ledger_present")
        == proof.get("nonlinear_solver_scale_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        == proof_claim_traceability.get("remaining_claim_boundary", {}).get(
            "nonlinear_solver_scale_ledger_present"
        )
        == proof_claim_traceability.get("summary", {}).get(
            "nonlinear_solver_scale_ledger_present"
        )
        is True,
        "strict proof-writing nonlinear-solver scale ledger not propagated into package manifest",
    )
    checks.check(
        strict_proof_boundary.get("local_defect_decomposition_ledger_present")
        == summary.get(
            "strict_proof_writing_local_defect_decomposition_ledger_present"
        )
        == proof_writing_card.get("local_defect_decomposition_ledger_present")
        == proof.get("local_defect_decomposition_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        == proof_claim_traceability.get("remaining_claim_boundary", {}).get(
            "local_defect_decomposition_ledger_present"
        )
        == proof_claim_traceability.get("summary", {}).get(
            "local_defect_decomposition_ledger_present"
        )
        is True,
        "strict proof-writing local-defect decomposition ledger not propagated into package manifest",
    )
    checks.check(
        strict_proof_boundary.get("theorem_output_scope_ledger_present")
        == summary.get("strict_proof_writing_theorem_output_scope_ledger_present")
        == proof_writing_card.get("theorem_output_scope_ledger_present")
        == proof.get("theorem_output_scope_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        == proof_claim_traceability.get("remaining_claim_boundary", {}).get(
            "theorem_output_scope_ledger_present"
        )
        == proof_claim_traceability.get("summary", {}).get(
            "theorem_output_scope_ledger_present"
        )
        is True,
        "strict proof-writing theorem output scope ledger not propagated into package manifest",
    )
    checks.check(
        strict_proof_boundary.get("reporting_map_ledger_present")
        == summary.get("strict_proof_writing_reporting_map_ledger_present")
        == proof_writing_card.get("reporting_map_ledger_present")
        == proof.get("reporting_map_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        == proof_claim_traceability.get("remaining_claim_boundary", {}).get(
            "reporting_map_ledger_present"
        )
        == proof_claim_traceability.get("summary", {}).get(
            "reporting_map_ledger_present"
        )
        is True,
        "strict proof-writing reporting-map/norm-equivalence ledger not propagated into package manifest",
    )
    checks.check(
        strict_proof_boundary.get("proof_causality_ledger_present")
        == summary.get("strict_proof_writing_proof_causality_ledger_present")
        == proof_writing_card.get("proof_causality_ledger_present")
        == proof.get("proof_causality_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        == proof_claim_traceability.get("remaining_claim_boundary", {}).get(
            "proof_causality_ledger_present"
        )
        == proof_claim_traceability.get("summary", {}).get(
            "proof_causality_ledger_present"
        )
        is True,
        "strict proof-writing proof-causality ledger not propagated into package manifest",
    )
    checks.check(
        strict_proof_boundary.get("direct_route_anticircularity_ledger_present")
        == summary.get(
            "strict_proof_writing_direct_route_anticircularity_ledger_present"
        )
        == proof_writing_card.get("direct_route_anticircularity_ledger_present")
        == proof.get("direct_route_anticircularity_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        == proof_claim_traceability.get("remaining_claim_boundary", {}).get(
            "direct_route_anticircularity_ledger_present"
        )
        == proof_claim_traceability.get("summary", {}).get(
            "direct_route_anticircularity_ledger_present"
        )
        is True,
        "strict proof-writing direct-route anti-circularity ledger not propagated into package manifest",
    )
    checks.check(
        strict_proof_boundary.get("safe_reader_claim")
        == summary.get("strict_proof_writing_safe_reader_claim")
        == proof_writing_card.get("safe_reader_claim")
        == proof_claim_summary.get("proof_writing_boundary_card_safe_reader_claim")
        == expected_safe_reader_claim,
        "strict proof-writing safe reader claim changed in package manifest",
    )
    checks.check(
        strict_proof_boundary.get("theorem_assumption_partition_boundary_present")
        == summary.get(
            "strict_proof_writing_theorem_assumption_partition_boundary_present"
        )
        is True
        and strict_proof_boundary.get("safe_reader_claim_boundary_present")
        == summary.get("strict_proof_writing_safe_reader_claim_boundary_present")
        is True
        and strict_proof_boundary.get("reading_rule_boundary_present")
        == summary.get("strict_proof_writing_reading_rule_boundary_present")
        is True
        and proof_claim_remaining_boundary.get("reading_rule")
        == expected_proof_reading_rule,
        "strict proof-writing reader-claim boundary not propagated into package manifest",
    )
    checks.check(
        strict_proof_boundary.get("theorem_assumption_anchor_ids")
        == summary.get("strict_proof_writing_theorem_assumption_anchor_ids")
        == proof_writing_card.get("theorem_assumption_anchor_ids")
        == proof_manuscript_traceability.get("theorem_assumption_anchor_ids")
        == proof_claim_remaining_boundary.get("theorem_assumption_anchor_ids")
        == proof_theorem_assumption_anchor_ids
        == expected_theorem_assumption_anchor_ids
        and strict_proof_boundary.get("theorem_assumption_anchor_count")
        == summary.get("strict_proof_writing_theorem_assumption_anchor_count")
        == proof_claim_summary.get("theorem_assumption_anchor_count")
        == len(expected_theorem_assumption_anchor_ids),
        "strict proof-writing theorem-interface/P7-output-boundary anchors not propagated into package manifest",
    )
    checks.check(
        strict_proof_boundary.get("theorem_assumption_submission_satisfied_ids")
        == summary.get(
            "strict_proof_writing_theorem_assumption_submission_satisfied_ids"
        )
        == proof_submission_satisfied_assumption_ids
        == proof_claim_remaining_boundary.get("submission_satisfied_ids")
        == proof_claim_summary.get("theorem_assumption_submission_satisfied_ids")
        == expected_submission_satisfied_assumption_ids
        and strict_proof_boundary.get(
            "theorem_assumption_submission_satisfied_count"
        )
        == summary.get(
            "strict_proof_writing_theorem_assumption_submission_satisfied_count"
        )
        == proof_claim_remaining_boundary.get("submission_satisfied_count")
        == proof_claim_summary.get("theorem_assumptions_submission_satisfied")
        == len(expected_submission_satisfied_assumption_ids),
        "strict proof-writing satisfied assumption partition not propagated into package manifest",
    )
    checks.check(
        strict_proof_boundary.get("theorem_assumption_retained_or_open_ids")
        == summary.get("strict_proof_writing_theorem_assumption_retained_or_open_ids")
        == proof_retained_or_open_assumption_ids
        == proof_claim_remaining_boundary.get("retained_or_open_ids")
        == proof_claim_summary.get("theorem_assumption_retained_or_open_ids")
        == expected_retained_or_open_assumption_ids
        and strict_proof_boundary.get("theorem_assumption_retained_or_open_count")
        == summary.get(
            "strict_proof_writing_theorem_assumption_retained_or_open_count"
        )
        == proof_claim_remaining_boundary.get("retained_or_open_count")
        == proof_claim_summary.get("theorem_assumptions_retained_or_open")
        == len(expected_retained_or_open_assumption_ids),
        "strict proof-writing retained-interface/open-nonpromotion partition not propagated into package manifest",
    )
    checks.check(
        strict_proof_boundary.get("theorem_assumption_retained_theorem_interface_ids")
        == summary.get("strict_proof_writing_theorem_assumption_retained_theorem_interface_ids")
        == proof_claim_remaining_boundary.get("retained_theorem_interface_ids")
        == proof_claim_summary.get("theorem_assumption_retained_theorem_interface_ids")
        == expected_retained_theorem_interface_ids
        and strict_proof_boundary.get("theorem_assumption_retained_theorem_interface_count")
        == summary.get("strict_proof_writing_theorem_assumption_retained_theorem_interface_count")
        == proof_claim_remaining_boundary.get("retained_theorem_interface_count")
        == proof_claim_summary.get("theorem_assumptions_retained_theorem_interfaces")
        == len(expected_retained_theorem_interface_ids),
        "strict proof-writing retained theorem-interface partition not propagated into package manifest",
    )
    checks.check(
        strict_proof_boundary.get("theorem_assumption_open_nonpromotion_boundary_ids")
        == summary.get("strict_proof_writing_theorem_assumption_open_nonpromotion_boundary_ids")
        == proof_claim_remaining_boundary.get("open_nonpromotion_boundary_ids")
        == proof_claim_summary.get("theorem_assumption_open_nonpromotion_boundary_ids")
        == expected_open_nonpromotion_boundary_ids
        and strict_proof_boundary.get("theorem_assumption_open_nonpromotion_boundary_count")
        == summary.get("strict_proof_writing_theorem_assumption_open_nonpromotion_boundary_count")
        == proof_claim_remaining_boundary.get("open_nonpromotion_boundary_count")
        == proof_claim_summary.get("theorem_assumptions_open_nonpromotion_boundaries")
        == len(expected_open_nonpromotion_boundary_ids),
        "strict proof-writing open output-boundary partition not propagated into package manifest",
    )
    checks.check(
        strict_proof_boundary.get("forbidden_reader_claims")
        == summary.get("strict_proof_writing_forbidden_reader_claims")
        == proof_writing_card.get("forbidden_reader_claims")
        == expected_forbidden_reader_claims,
        "strict proof-writing forbidden reader claims changed in package manifest",
    )
    checks.check(
        strict_proof_boundary.get("forbidden_reader_claims_boundary_present")
        == summary.get("strict_proof_writing_forbidden_reader_claims_boundary_present")
        is True,
        "strict proof-writing forbidden reader claims boundary not propagated into package manifest",
    )
    checks.check(
        strict_proof_boundary.get("forbidden_unconditional_theorem_boundary_present")
        == summary.get(
            "strict_proof_writing_forbidden_unconditional_theorem_boundary_present"
        )
        is True
        and proof_theorem_boundary.get(
            "conditional_theorem_boundary_present_main_and_flat"
        )
        is True
        and strict_proof_boundary.get("theorem_assumption_partition_boundary_present")
        is True
        and proof_claim_traceability.get("submission_ready") is False,
        "strict proof-writing unconditional-theorem forbidden claim not propagated into package manifest",
    )
    checks.check(
        strict_proof_boundary.get(
            "forbidden_eta_h_solver_policy_claim_boundary_present"
        )
        == summary.get(
            "strict_proof_writing_forbidden_eta_h_solver_policy_claim_boundary_present"
        )
        is True
        and strict_proof_boundary.get("eta_h_solver_policy_evidence_closed") is False
        and proof_theorem_boundary.get("eta_h_theorem_condition_retained") is True,
        "strict proof-writing eta_h solver-policy forbidden claim not propagated into package manifest",
    )
    checks.check(
        strict_proof_boundary.get(
            "forbidden_fixed_tolerance_asymptotic_claim_boundary_present"
        )
        == summary.get(
            "strict_proof_writing_forbidden_fixed_tolerance_asymptotic_claim_boundary_present"
        )
        is True
        and strict_proof_boundary.get("fixed_tolerance_runs_are_asymptotic_proof")
        is False,
        "strict proof-writing fixed-tolerance forbidden claim not propagated into package manifest",
    )
    checks.check(
        strict_proof_boundary.get(
            "forbidden_residual_to_error_theorem_claim_boundary_present"
        )
        == summary.get(
            "strict_proof_writing_forbidden_residual_to_error_theorem_claim_boundary_present"
        )
        is True
        and strict_proof_boundary.get("residual_to_error_route_promoted") is False
        and proof_residual_policy.get("accepted_residual_to_error_theorem") is False
        and proof_residual_policy.get("residual_promotion_not_made") is True,
        "strict proof-writing residual-to-error theorem forbidden claim not propagated into package manifest",
    )
    checks.check(
        strict_proof_boundary.get("residual_to_error_not_promoted")
        == objective_strict_proof_boundary.get("residual_to_error_not_promoted")
        == summary.get("strict_proof_writing_residual_to_error_not_promoted")
        is True
        and strict_proof_boundary.get("residual_to_error_route_promoted") is False
        and proof_residual_policy.get("accepted_residual_to_error_theorem") is False
        and proof_residual_policy.get("residual_promotion_not_made") is True,
        "strict proof-writing residual-to-error no-promotion lock not propagated into package manifest",
    )
    checks.check(
        strict_proof_boundary.get(
            "forbidden_source_policy_full_tfe_package_claim_boundary_present"
        )
        == summary.get(
            "strict_proof_writing_forbidden_source_policy_full_tfe_package_claim_boundary_present"
        )
        is True
        and strict_proof_boundary.get("source_policy_or_full_tfe_not_promoted")
        is True
        and strict_proof_boundary.get("source_policy_closed") is False
        and strict_proof_boundary.get("tfe_runner_closed") is False
        and strict_proof_boundary.get("minimal_code_ready") is False
        and strict_proof_boundary.get("full_source_policy_runner_package_ready")
        is False,
        "strict proof-writing source-policy/full-TFE forbidden claim not propagated into package manifest",
    )
    checks.check(
        strict_proof_boundary.get("source_policy_full_tfe_not_promoted")
        == objective_strict_proof_boundary.get("source_policy_full_tfe_not_promoted")
        == summary.get("strict_proof_writing_source_policy_full_tfe_not_promoted")
        is True
        and strict_proof_boundary.get("source_policy_or_full_tfe_not_promoted")
        is True
        and strict_proof_boundary.get("source_policy_closed") is False
        and strict_proof_boundary.get("tfe_runner_closed") is False
        and strict_proof_boundary.get("minimal_code_ready") is False
        and strict_proof_boundary.get("full_source_policy_runner_package_ready")
        is False,
        "strict proof-writing source-policy/full-TFE no-promotion lock not propagated into package manifest",
    )
    checks.check(
        strict_proof_boundary.get("proof_global_boundaries_retained")
        == summary.get("strict_proof_writing_global_boundaries_retained")
        == proof_writing_card.get("global_submission_boundaries_retained")
        == proof_readiness_boundary.get("global_submission_boundaries_retained")
        == proof_claim_remaining_boundary.get("global_submission_boundaries_retained")
        == proof_claim_summary.get("global_submission_boundaries_retained")
        == expected_global_submission_boundaries,
        "strict proof-writing global retained boundaries changed in package manifest",
    )
    checks.check(
        strict_proof_boundary.get("direct_pc2_proof_gap_closed")
        == summary.get("strict_proof_writing_direct_pc2_proof_gap_closed")
        == proof_writing_card.get("direct_pc2_proof_gap_closed")
        == proof_closure_state.get("direct_pc2_proof_gap_closed")
        == proof_closure_state.get("proof_gap_closed")
        == proof_claim_closure_state.get("direct_pc2_proof_gap_closed")
        == proof_claim_summary.get("direct_pc2_proof_gap_closed")
        is True,
        "strict proof-writing direct PC2 closure flag not propagated into package manifest",
    )
    checks.check(
        strict_proof_boundary.get("stage_residual_O_h7_implementation_defect_proved")
        == summary.get(
            "strict_proof_writing_stage_residual_O_h7_implementation_defect_proved"
        )
        == proof_writing_card.get("stage_residual_O_h7_implementation_defect_proved")
        == proof_closure_state.get("stage_residual_O_h7_implementation_defect_proved")
        == proof_claim_closure_state.get(
            "stage_residual_O_h7_implementation_defect_proved"
        )
        == proof_claim_summary.get("stage_residual_O_h7_implementation_defect_proved")
        is True,
        "strict proof-writing stage residual O(h^7) flag not propagated into package manifest",
    )
    checks.check(
        strict_proof_boundary.get("dynamic_symbolic_oracle_complete")
        == summary.get("strict_proof_writing_dynamic_symbolic_oracle_complete")
        == proof_writing_card.get("dynamic_symbolic_oracle_complete")
        == proof_closure_state.get("dynamic_symbolic_oracle_complete")
        == proof_claim_closure_state.get("dynamic_symbolic_oracle_complete")
        == proof_claim_summary.get("dynamic_symbolic_oracle_complete")
        is False,
        "strict proof-writing dynamic symbolic oracle flag not propagated into package manifest",
    )
    checks.check(
        strict_proof_boundary.get("eta_h_solver_policy_evidence_closed")
        == summary.get("strict_proof_writing_eta_h_solver_policy_evidence_closed")
        == proof_writing_card.get("eta_h_solver_policy_evidence_closed")
        == proof_theorem_boundary.get("eta_h_solver_policy_evidence_closed")
        == proof_closure_state.get("eta_h_O_h7_solver_policy_evidence")
        == proof_solver_state.get("eta_h_O_h7_solver_policy_evidence")
        == proof_claim_theorem_traceability.get("eta_h_solver_policy_evidence_closed")
        == proof_claim_remaining_boundary.get("eta_h_solver_policy_evidence_closed")
        is False,
        "strict proof-writing eta_h solver-policy theorem flag not propagated into package manifest",
    )
    checks.check(
        strict_proof_boundary.get("fixed_tolerance_runs_are_asymptotic_proof")
        == summary.get("strict_proof_writing_fixed_tolerance_asymptotic_proof")
        == proof_writing_card.get("fixed_tolerance_runs_are_asymptotic_proof")
        == proof_theorem_boundary.get("fixed_tolerance_runs_are_asymptotic_proof")
        == proof_closure_state.get("fixed_tolerance_runs_are_asymptotic_proof")
        == proof_claim_theorem_traceability.get(
            "fixed_tolerance_runs_are_asymptotic_proof"
        )
        is False,
        "strict proof-writing fixed-tolerance asymptotic-proof flag not propagated into package manifest",
    )
    checks.check(
        strict_proof_boundary.get("residual_to_error_route_promoted")
        == summary.get("strict_proof_writing_residual_to_error_route_promoted")
        == proof_writing_card.get("residual_to_error_route_promoted")
        == proof_residual_policy.get("accepted_residual_to_error_theorem")
        == proof_claim_remaining_boundary.get("residual_to_error_route_promoted")
        == proof_claim_summary.get("residual_to_error_route_promoted")
        is False
        and proof_residual_policy.get("residual_promotion_not_made") is True,
        "strict proof-writing residual-to-error promotion flag not propagated into package manifest",
    )
    checks.check(
        strict_proof_boundary.get("source_policy_or_full_tfe_not_promoted")
        == summary.get("strict_proof_writing_source_policy_or_full_tfe_not_promoted")
        == proof_writing_card.get("source_policy_or_full_tfe_not_promoted")
        == proof_theorem_boundary.get("does_not_promote_source_policy_or_full_tfe")
        == proof_claim_theorem_traceability.get(
            "source_policy_or_full_tfe_not_promoted"
        )
        == proof_claim_remaining_boundary.get("source_policy_or_full_tfe_not_promoted")
        is True,
        "strict proof-writing source-policy/full-TFE nonpromotion flag not propagated into package manifest",
    )
    checks.check(
        strict_proof_boundary.get("satisfied_close_requirement_ids")
        == summary.get("strict_proof_writing_satisfied_close_requirement_ids")
        == proof_writing_card.get("satisfied_close_requirement_ids")
        == proof_satisfied_close_requirement_ids
        == proof_claim_summary.get("close_requirement_satisfied_ids")
        == ["PC1", "PC2", "PC3", "PC4"]
        and strict_proof_boundary.get("unsatisfied_close_requirement_ids")
        == summary.get("strict_proof_writing_unsatisfied_close_requirement_ids")
        == proof_writing_card.get("unsatisfied_close_requirement_ids")
        == proof_unsatisfied_close_requirement_ids
        == proof_claim_summary.get("close_requirement_unsatisfied_ids")
        == [],
        "strict proof-writing close requirement IDs not propagated into package manifest",
    )
    checks.check(
        strict_proof_boundary.get("objective_blockers_retained")
        == summary.get("strict_proof_writing_objective_blockers_retained")
        == minimal_submission_code_boundary.get("blocking_objective_requirements")
        == ["OC4", "OC6", "OC12"]
        and strict_proof_boundary.get("package_boundary_status")
        == summary.get("strict_proof_writing_package_boundary_status")
        == minimal_submission_code_boundary.get("status")
        == "narrowed_repro_ready_full_source_policy_package_blocked",
        "strict proof-writing package blocker boundary changed",
    )
    checks.check(
        strict_proof_boundary.get("source_policy_closed") is False
        and strict_proof_boundary.get("tfe_runner_closed") is False
        and strict_proof_boundary.get("minimal_code_ready") is False
        and strict_proof_boundary.get("full_source_policy_runner_package_ready") is False
        and strict_proof_boundary.get("reader_facing_manuscript_boundary_present") is True
        and strict_proof_boundary.get("submission_ready")
        == summary.get("strict_proof_writing_submission_ready")
        is False
        and strict_proof_boundary.get("can_mark_goal_complete") is False,
        "strict proof-writing package readiness flags changed",
    )
    checks.check(
        reviewer_code_policy.get("code_bloat_risk_for_submission") is True,
        "reviewer-facing code policy lost code-bloat risk",
    )
    checks.check(
        narrowed_repro_audit.get("schema")
        == narrowed_repro_audit_source.get("schema")
        == "cmame-narrowed-reproducibility-package-audit-v1",
        "narrowed reproducibility audit schema not carried into manifest",
    )
    checks.check(
        narrowed_repro_audit.get("status") == narrowed_repro_audit_source.get("status"),
        "narrowed reproducibility audit status not carried into manifest",
    )
    checks.check(
        narrowed_repro_audit.get("submission_ready") is False
        and narrowed_repro_audit.get("submission_standard_scope") == "global_submission_standard"
        and narrowed_repro_audit.get("narrowed_claim_submission_standard_met") is True
        and narrowed_repro_audit.get("narrowed_claim_decision") == "submit_under_narrowed_claim"
        and narrowed_repro_audit.get("global_submission_standard_met") is False,
        "narrowed reproducibility audit readiness scope stale",
    )
    checks.check(
        narrowed_repro_audit.get("narrowed_claim_reproducibility_package_ready") is True
        and narrowed_repro_audit.get("full_source_policy_runner_package_ready") is False
        and narrowed_repro_audit.get("source_policy_rows_closed") == 0
        and narrowed_repro_audit.get("source_policy_rows_total") == 40,
        "narrowed reproducibility audit source-policy boundary stale in manifest",
    )
    narrowed_boundary = narrowed_repro_audit.get("package_boundary", {})
    checks.check(
        narrowed_boundary.get("not_a_source_policy_runner_archive") is True
        and narrowed_boundary.get("full_source_policy_deferred_until_rows_close") is True
        and narrowed_boundary.get("source_policy_rows_closed_now") == 0,
        "narrowed reproducibility package boundary stale",
    )
    checks.check(
        runner_adapter.get("schema")
        == runner_adapter_source.get("schema")
        == "cmame-runner-adapter-candidate-v1",
        "runner-adapter schema not carried into manifest",
    )
    checks.check(
        runner_adapter.get("runner_adapter_present") is True
        and runner_adapter.get("self_contained_simulation_runner") is False
        and runner_adapter.get("submission_ready") is False,
        "runner-adapter boundary stale in manifest",
    )
    checks.check(
        runner_adapter.get("source_policy_closed_rows") == 0
        and runner_adapter.get("source_policy_total_rows") == 40,
        "runner-adapter source-policy scope stale in manifest",
    )
    checks.check(
        runner_adapter.get("candidate_python_file_count")
        == runner_adapter_source.get("candidate_python_file_count")
        == 2,
        "runner-adapter Python file count not carried into manifest",
    )
    checks.check(
        runner_adapter.get("closed_loop_local_rows_replay_present")
        == runner_adapter_source.get("closed_loop_local_rows_replay_present")
        is True,
        "runner-adapter closed-loop local replay marker not carried into manifest",
    )
    checks.check(
        runner_adapter.get("closed_loop_local_rows_summary_present")
        == runner_adapter_source.get("closed_loop_local_rows_summary_present")
        is True,
        "runner-adapter closed-loop local replay summary marker not carried into manifest",
    )
    checks.check(
        runner_adapter.get("closed_loop_local_rows") == runner_adapter_source.get("closed_loop_local_rows") == 6,
        "runner-adapter closed-loop local row count not carried into manifest",
    )
    checks.check(
        set(runner_adapter.get("closed_loop_local_models", [])) == {"four_link", "slider_crank"},
        "runner-adapter closed-loop local models not carried into manifest",
    )
    checks.check(
        runner_centered_audit.get("schema")
        == runner_centered_audit_source.get("schema")
        == "cmame-runner-centered-reproducibility-audit-v1",
        "runner-centered audit schema not carried into manifest",
    )
    checks.check(
        runner_centered_audit.get("status") == runner_centered_audit_source.get("status"),
        "runner-centered audit status stale in manifest",
    )
    checks.check(
        runner_centered_audit.get("runner_centered_package_ready") is False,
        "runner-centered audit overclaimed package readiness in manifest",
    )
    checks.check(
        runner_centered_audit.get("local_runner_centered_candidate_ready") is True
        and runner_centered_audit.get("full_source_policy_runner_package_ready") is False,
        "runner-centered audit local/full runner boundary stale in manifest",
    )
    runner_package_boundary = runner_centered_audit.get("runner_package_boundary", {})
    checks.check(
        runner_package_boundary.get("local_accepted_rows_runner_centered") is True
        and runner_package_boundary.get("full_source_policy_runner_centered") is False
        and runner_package_boundary.get("b6_final_prose_pass_ready") is True
        and runner_package_boundary.get("b6_final_prose_pass_scope") == "narrowed_claim_current_submission"
        and runner_package_boundary.get("full_source_policy_b6_prose_ready") is False
        and runner_package_boundary.get("b6_closure_preflight_status")
        == "b6_final_prose_pass_closed_under_narrowed_b4_b7_scope"
        and runner_package_boundary.get("b6_closure_allowed_now") is True,
        "runner package boundary overclaims local/full/B6 readiness",
    )
    checks.check(
        runner_centered_audit.get("existing_runner_source_total_python_lines")
        == runner_centered_audit_source.get("existing_runner_source_total_python_lines"),
        "runner-centered audit source line count stale in manifest",
    )
    checks.check(
        runner_centered_audit.get("candidate", {}).get("replay_only") is True
        and runner_centered_audit.get("candidate", {}).get("runner_centered") is False,
        "runner-centered audit candidate boundary stale in manifest",
    )
    checks.check(
        runner_centered_audit.get("source_policy_scope", {}).get("source_policy_closed_rows") == 0
        and runner_centered_audit.get("source_policy_scope", {}).get("source_policy_total_rows") == 40,
        "runner-centered audit source-policy scope stale in manifest",
    )
    runner_centered_b6 = runner_centered_audit.get("b6_four_example_local_evidence", {})
    checks.check(
        runner_centered_b6.get("runner_passed") is True
        and runner_centered_b6.get("local_rows") == 12
        and set(runner_centered_b6.get("self_contained_examples", []))
        == {"single_pendulum", "double_pendulum", "four_link", "slider_crank"}
        and runner_centered_b6.get("replay_only_examples", []) == [],
        "B6 local-evidence block not carried into runner-centered manifest block",
    )
    runner_centered_closed_loop = runner_centered_audit.get("b6_closed_loop_self_contained_extraction_audit", {})
    checks.check(
        runner_centered_closed_loop.get("schema")
        == closed_loop_audit_source.get("schema")
        == "b6-closed-loop-self-contained-extraction-audit-v1",
        "B6 closed-loop extraction audit schema not carried into runner-centered manifest block",
    )
    checks.check(
        runner_centered_closed_loop.get("status") == closed_loop_audit_source.get("status")
        and runner_centered_closed_loop.get("self_contained_runner_ready") is True
        and runner_centered_closed_loop.get("target_symbol_count")
        == closed_loop_audit_source.get("target_symbol_count")
        and runner_centered_closed_loop.get("target_symbol_lines")
        == closed_loop_audit_source.get("target_symbol_lines"),
        "B6 closed-loop extraction audit not carried into runner-centered manifest block",
    )
    checks.check(
        extraction_plan.get("schema")
        == extraction_plan_source.get("schema")
        == "cmame-self-contained-runner-extraction-plan-v1",
        "self-contained runner extraction plan schema not carried into manifest",
    )
    checks.check(
        extraction_plan.get("status") == extraction_plan_source.get("status"),
        "self-contained runner extraction plan status stale in manifest",
    )
    checks.check(
        extraction_plan.get("self_contained_runner_ready") is False,
        "self-contained runner extraction plan overclaimed readiness in manifest",
    )
    extraction_boundary = extraction_plan.get("runner_package_boundary", {})
    checks.check(
        extraction_plan.get("local_accepted_rows_self_contained_runner_ready") is True
        and extraction_plan.get("full_source_policy_self_contained_runner_ready") is False
        and extraction_plan.get("b6_final_prose_pass_ready") is True
        and extraction_plan.get("b6_final_prose_pass_scope") == "narrowed_claim_current_submission"
        and extraction_plan.get("full_source_policy_b6_prose_ready") is False
        and extraction_plan.get("b6_closure_preflight_status")
        == "b6_final_prose_pass_closed_under_narrowed_b4_b7_scope"
        and extraction_plan.get("b6_closure_allowed_now") is True
        and extraction_boundary.get("local_accepted_rows_self_contained") is True
        and extraction_boundary.get("full_source_policy_self_contained") is False
        and extraction_boundary.get("b6_final_prose_pass_ready") is True
        and extraction_boundary.get("b6_final_prose_pass_scope") == "narrowed_claim_current_submission"
        and extraction_boundary.get("full_source_policy_b6_prose_ready") is False
        and extraction_boundary.get("b6_closure_allowed_now") is True
        and extraction_boundary.get("source_policy_rows_closed") == 0
        and extraction_boundary.get("source_policy_rows_total") == 40,
        "self-contained runner extraction plan local/full boundary stale in manifest",
    )
    checks.check(
        extraction_plan.get("target_symbol_count") == extraction_plan_source.get("target_symbol_count")
        and extraction_plan.get("target_symbol_lines") == extraction_plan_source.get("target_symbol_lines"),
        "self-contained runner extraction target stale in manifest",
    )
    checks.check(
        extraction_plan.get("p1_single_runner_candidate_ready") is True
        and extraction_plan.get("p1_double_runner_candidate_ready") is True
        and extraction_plan.get("p1_regenerated_candidate_rows") == 6
        and extraction_plan.get("p1_required_rows") == 6,
        "P1 single-runner progress not carried into self-contained plan manifest block",
    )
    extraction_b6 = extraction_plan.get("b6_four_example_local_evidence", {})
    checks.check(
        extraction_b6.get("runner_passed") is True
        and extraction_b6.get("local_rows") == 12
        and extraction_b6.get("four_example_self_contained_simulation_ready") is True,
        "B6 local-evidence block not carried into self-contained plan manifest block",
    )
    extraction_closed_loop = extraction_plan.get("b6_closed_loop_self_contained_extraction_audit", {})
    checks.check(
        extraction_closed_loop.get("schema")
        == closed_loop_audit_source.get("schema")
        == "b6-closed-loop-self-contained-extraction-audit-v1",
        "B6 closed-loop extraction audit schema not carried into self-contained plan manifest block",
    )
    checks.check(
        extraction_closed_loop.get("status") == closed_loop_audit_source.get("status")
        and extraction_closed_loop.get("self_contained_runner_ready") is True
        and extraction_closed_loop.get("replay_only_closed_loop_examples", []) == []
        and extraction_closed_loop.get("closed_loop_local_replay_rows") == 6,
        "B6 closed-loop extraction audit not carried into self-contained plan manifest block",
    )
    checks.check(
        closed_loop_audit.get("schema")
        == closed_loop_audit_source.get("schema")
        == "b6-closed-loop-self-contained-extraction-audit-v1",
        "B6 closed-loop extraction audit schema not carried into manifest",
    )
    checks.check(
        closed_loop_audit.get("status")
        == closed_loop_audit_source.get("status")
        == "closed_loop_self_contained_runner_candidate_ready_source_policy_open",
        "B6 closed-loop extraction audit status stale in manifest",
    )
    checks.check(
        closed_loop_audit.get("self_contained_runner_ready") is True
        and closed_loop_audit.get("target_source_file_count") == closed_loop_audit_source.get("target_source_file_count")
        and closed_loop_audit.get("target_symbol_count") == closed_loop_audit_source.get("target_symbol_count")
        and closed_loop_audit.get("target_symbol_lines") == closed_loop_audit_source.get("target_symbol_lines")
        and closed_loop_audit.get("replay_only_closed_loop_examples", []) == []
        and closed_loop_audit.get("closed_loop_local_replay_rows") == 6,
        "B6 closed-loop extraction audit boundary stale in manifest",
    )
    checks.check(
        closed_loop_audit.get("run_v047_invoked") is False
        and closed_loop_audit.get("run_v048_invoked") is False
        and closed_loop_audit.get("b4_opt_in_required_for_this_audit") is False,
        "B6 closed-loop extraction audit execution boundary changed in manifest",
    )
    checks.check(
        closed_loop_candidate.get("schema") == closed_loop_candidate_source.get("schema"),
        "closed-loop candidate schema not carried into manifest",
    )
    checks.check(
        closed_loop_candidate.get("status")
        == closed_loop_candidate_source.get("status")
        == "closed_loop_local_runner_candidate_passed_compact",
        "closed-loop candidate status stale in manifest",
    )
    checks.check(
        closed_loop_candidate.get("runner_passed") is True
        and closed_loop_candidate.get("self_contained_simulation_runner") is True
        and closed_loop_candidate.get("candidate_python_file_count") == 10
        and 0 < closed_loop_candidate.get("candidate_python_line_count", 0) <= 2000
        and closed_loop_candidate.get("candidate_python_line_limit_ok") is True
        and closed_loop_candidate.get("imports_v046_v047_v048_or_v029") is False
        and closed_loop_candidate.get("closed_loop_local_rows") == 6
        and set(closed_loop_candidate.get("closed_loop_models", [])) == {"four_link", "slider_crank"},
        "closed-loop candidate runner/size/import boundary stale in manifest",
    )
    checks.check(
        closed_loop_candidate.get("source_policy_external_rows_closed") == 0
        and closed_loop_candidate.get("source_policy_external_rows_total") == 40
        and closed_loop_candidate.get("source_policy_external_superiority_allowed") is False
        and closed_loop_candidate.get("submission_ready") is False,
        "closed-loop candidate overclaimed source-policy or submission readiness in manifest",
    )
    checks.check(
        b6_local_evidence.get("schema")
        == b6_local_evidence_source.get("schema")
        == "b6-four-example-local-evidence-summary-v1",
        "B6 local-evidence schema not carried into manifest",
    )
    checks.check(
        b6_local_evidence.get("runner_passed") is True
        and b6_local_evidence.get("local_rows") == 12
        and b6_local_evidence.get("four_example_self_contained_simulation_ready") is True
        and b6_local_evidence.get("source_policy_external_rows_closed") == 0
        and b6_local_evidence.get("source_policy_external_rows_total") == 40
        and b6_local_evidence.get("global_proof_gap_closed") is True
        and b6_local_evidence.get("submission_ready") is False,
        "B6 local-evidence boundary stale in manifest",
    )
    checks.check(
        p1_local_runner_audit.get("schema")
        == p1_local_runner_audit_source.get("schema")
        == "cmame-p1-local-runner-extraction-audit-v1",
        "P1 local-runner audit schema not carried into manifest",
    )
    checks.check(
        p1_local_runner_audit.get("status")
        == p1_local_runner_audit_source.get("status")
        == "closed_single_double_runner_candidates_ready",
        "P1 local-runner audit status not carried into manifest",
    )
    checks.check(
        p1_local_runner_audit.get("p1_local_single_double_ready")
        == p1_local_runner_audit_source.get("p1_local_single_double_ready")
        is True,
        "P1 local-runner readiness not carried into manifest",
    )
    checks.check(
        p1_local_runner_audit.get("self_contained_runner_ready")
        == p1_local_runner_audit_source.get("self_contained_runner_ready")
        is False,
        "P1 self-contained runner readiness overclaimed in manifest",
    )
    checks.check(
        p1_local_runner_audit.get("p1_single_runner_candidate_ready")
        == p1_local_runner_audit_source.get("p1_single_runner_candidate_ready")
        is True,
        "P1 single-runner candidate readiness not carried into manifest",
    )
    checks.check(
        p1_local_runner_audit.get("p1_double_runner_candidate_ready")
        == p1_local_runner_audit_source.get("p1_double_runner_candidate_ready")
        is True,
        "P1 double-runner candidate readiness not carried into manifest",
    )
    checks.check(
        p1_local_runner_audit.get("p1_regenerated_candidate_rows")
        == p1_local_runner_audit_source.get("p1_regenerated_candidate_rows")
        == 6,
        "P1 regenerated row count not carried into manifest",
    )
    checks.check(
        p1_local_runner_audit.get("p1_required_rows") == p1_local_runner_audit_source.get("p1_required_rows") == 6,
        "P1 required row count not carried into manifest",
    )
    checks.check(
        p1_local_runner_audit.get("p1_missing_candidate_rows")
        == p1_local_runner_audit_source.get("p1_missing_candidate_rows")
        == 0,
        "P1 missing row count not carried into manifest",
    )
    checks.check(
        p1_single_candidate.get("schema")
        == p1_single_candidate_source.get("schema")
        == "cmame-p1-single-runner-candidate-v1",
        "P1 single-runner candidate schema not carried into manifest",
    )
    checks.check(
        p1_single_candidate.get("rows") == p1_single_candidate_source.get("rows") == 3
        and p1_single_candidate.get("p1_complete") is False
        and p1_single_candidate.get("imports_v047_or_v048") is False,
        "P1 single-runner candidate boundary stale in manifest",
    )
    checks.check(
        p1_double_candidate.get("schema")
        == p1_double_candidate_source.get("schema")
        == "cmame-p1-double-runner-candidate-v1",
        "P1 double-runner candidate schema not carried into manifest",
    )
    checks.check(
        p1_double_candidate.get("rows") == p1_double_candidate_source.get("rows") == 3
        and p1_double_candidate.get("p1_complete") is False
        and p1_double_candidate.get("imports_v047_v048_or_v029") is False,
        "P1 double-runner candidate boundary stale in manifest",
    )
    checks.check(
        p1_local_runner_audit.get("v047_source_python_lines")
        == p1_local_runner_audit_source.get("v047_source_python_lines")
        == 69264,
        "P1 v047 line count stale in manifest",
    )
    checks.check(
        p1_local_runner_audit.get("v047_primary_recursive_internal_dependency_count")
        == p1_local_runner_audit_source.get("v047_primary_recursive_internal_dependency_count"),
        "P1 recursive dependency count stale in manifest",
    )
    checks.check(
        p1_local_runner_audit.get("v047_primary_recursive_internal_dependency_lines")
        == p1_local_runner_audit_source.get("v047_primary_recursive_internal_dependency_lines"),
        "P1 recursive dependency line count stale in manifest",
    )
    checks.check(
        len(p1_local_runner_audit.get("open_blockers", [])) == 4,
        "P1 open blocker count changed in manifest",
    )
    checks.check(
        summary.get("objective_complete") == objective_completion.get("objective_complete") is False,
        "objective completion boundary changed",
    )
    checks.check(
        summary.get("objective_blocking_open_count")
        == objective_completion.get("summary", {}).get("blocking_open_count")
        == 3,
        "objective blocking-open count changed",
    )
    checks.check(
        summary.get("objective_blocking_ids") == objective_completion.get("blocking_ids"),
        "objective blocking id mirror stale in manifest summary",
    )
    checks.check(
        summary.get("objective_blockers_by_id") == objective_completion.get("blockers_by_id"),
        "objective blocker map stale in manifest summary",
    )
    checks.check(
        summary.get("objective_blocker_status_by_id")
        == objective_completion.get("blocker_status_by_id"),
        "objective blocker status map stale in manifest summary",
    )
    checks.check(
        summary.get("objective_blocker_next_actions_by_id")
        == objective_completion.get("blocker_next_actions_by_id"),
        "objective blocker next-action map stale in manifest summary",
    )
    checks.check(
        summary.get("objective_blocker_required_to_close_by_id")
        == objective_completion.get("blocker_required_to_close_by_id"),
        "objective blocker required-to-close map stale in manifest summary",
    )
    checks.check(
        summary.get("objective_blocker_safe_next_actions_by_id")
        == objective_completion.get("blocker_safe_next_actions_by_id"),
        "objective blocker safe-next-action map stale in manifest summary",
    )
    checks.check(
        summary.get("objective_blocker_opt_in_required_actions_by_id")
        == objective_completion.get("blocker_opt_in_required_actions_by_id"),
        "objective blocker opt-in-required-action map stale in manifest summary",
    )
    checks.check(
        summary.get("blocker_required_to_close_by_id")
        == summary.get("objective_blocker_required_to_close_by_id")
        == objective_completion.get("blocker_required_to_close_by_id"),
        "generic blocker required-to-close map stale in manifest summary",
    )
    checks.check(
        summary.get("blocker_safe_next_actions_by_id")
        == summary.get("objective_blocker_safe_next_actions_by_id")
        == objective_completion.get("blocker_safe_next_actions_by_id"),
        "generic blocker safe-next-action map stale in manifest summary",
    )
    checks.check(
        summary.get("blocker_opt_in_required_actions_by_id")
        == summary.get("objective_blocker_opt_in_required_actions_by_id")
        == objective_completion.get("blocker_opt_in_required_actions_by_id"),
        "generic blocker opt-in-required-action map stale in manifest summary",
    )
    checks.check(
        manifest.get("objective_blocker_required_to_close_by_id")
        == objective_completion.get("blocker_required_to_close_by_id"),
        "objective blocker required-to-close map stale in manifest top level",
    )
    checks.check(
        manifest.get("objective_blocker_safe_next_actions_by_id")
        == objective_completion.get("blocker_safe_next_actions_by_id"),
        "objective blocker safe-next-action map stale in manifest top level",
    )
    checks.check(
        manifest.get("objective_blocker_opt_in_required_actions_by_id")
        == objective_completion.get("blocker_opt_in_required_actions_by_id"),
        "objective blocker opt-in-required-action map stale in manifest top level",
    )
    checks.check(
        manifest.get("blocker_required_to_close_by_id")
        == manifest.get("objective_blocker_required_to_close_by_id")
        == objective_completion.get("blocker_required_to_close_by_id"),
        "generic blocker required-to-close map stale in manifest top level",
    )
    checks.check(
        manifest.get("blocker_safe_next_actions_by_id")
        == manifest.get("objective_blocker_safe_next_actions_by_id")
        == objective_completion.get("blocker_safe_next_actions_by_id"),
        "generic blocker safe-next-action map stale in manifest top level",
    )
    checks.check(
        manifest.get("blocker_opt_in_required_actions_by_id")
        == manifest.get("objective_blocker_opt_in_required_actions_by_id")
        == objective_completion.get("blocker_opt_in_required_actions_by_id"),
        "generic blocker opt-in-required-action map stale in manifest top level",
    )

    for key in [
        "paper_python_file_count",
        "paper_python_line_count",
        "v048_python_file_count",
        "v048_python_line_count",
        "combined_python_line_count",
        "paper_python_prefix_counts",
        "v048_python_prefix_counts",
    ]:
        checks.check(current_code.get(key) == code_checks.get(key), f"current code inventory stale: {key}")

    checks.check(external.get("b2_status") == b2.get("status"), "B2 status stale")
    checks.check(
        external.get("active_flagged_rows") == b2.get("active_flagged_row_count"),
        "active B2 rows changed",
    )
    checks.check(
        external.get("demoted_flagged_rows") == b2.get("demoted_flagged_row_count"),
        "demoted B2 rows changed",
    )
    checks.check(
        b2.get("active_flagged_row_count") == 0
        and b2.get("demoted_flagged_row_count") == 15
        and b2.get("status") == "route_b_all_external_suites_demoted_no_active_external_superiority_rows",
        "Route B all-suite demotion boundary changed",
    )
    checks.check(external.get("source_policy_closed_rows") == b2.get("source_policy_closed_rows") == 0, "B2 closed rows changed")
    checks.check(
        external.get("remaining_requirements") == b2.get("b2_remaining_requirements"),
        "B2 remaining requirements stale",
    )
    checks.check(external.get("ra2021_public_baselines_present") is True, "RA2021 baseline flag changed")
    checks.check(external.get("hi2022_bounded_rows_present") is True, "HI2022 bounded flag changed")
    checks.check(
        external.get("tfe_source_pendulum_parameter_model_implemented")
        == tfe_model.get("source_pendulum_parameter_model_implemented")
        is True,
        "TFE source pendulum model status changed",
    )
    checks.check(
        external.get("tfe_source_pendulum_frictionless_smoke_implemented")
        == tfe_model.get("frictionless_planar_rhs_smoke_implemented")
        is True,
        "TFE source pendulum smoke status changed",
    )
    checks.check(
        external.get("tfe_source_pendulum_absolute_coordinate_dae_residual_smoke_implemented")
        == tfe_model.get("absolute_coordinate_dae_residual_smoke_implemented")
        is True,
        "TFE source pendulum absolute-coordinate residual status changed",
    )
    checks.check(
        external.get("tfe_source_pendulum_absolute_coordinate_frictional_candidate_dae_smoke_implemented")
        == tfe_model.get("absolute_coordinate_frictional_candidate_dae_smoke_implemented")
        is True,
        "TFE source pendulum absolute-coordinate frictional candidate status changed",
    )
    checks.check(
        external.get("tfe_source_pendulum_source_policy_dae_runner_equivalent")
        == tfe_model.get("source_policy_dae_runner_equivalent")
        is False,
        "TFE source-policy DAE equivalence boundary changed",
    )
    checks.check(
        external.get("tfe_source_pendulum_source_output_time_integration_smoke_implemented")
        == tfe_model.get("source_output_time_integration_smoke_implemented")
        is True,
        "TFE source-output time-integration smoke status changed",
    )
    checks.check(
        external.get("tfe_source_pendulum_source_policy_time_integration_runner_equivalent")
        == tfe_model.get("source_policy_time_integration_runner_equivalent")
        is False,
        "TFE source-policy time-integration boundary changed",
    )
    checks.check(
        external.get("tfe_source_pendulum_source_reference_solution_policy_smoke_implemented")
        == tfe_model.get("source_reference_solution_policy_smoke_implemented")
        is True,
        "TFE source reference-policy smoke status changed",
    )
    checks.check(
        external.get("tfe_source_pendulum_source_reference_solution_policy_smoke_full_T10")
        == tfe_model.get("source_reference_solution_policy_smoke_full_T10")
        is False,
        "TFE source reference-policy full-run boundary changed",
    )
    checks.check(
        external.get("tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_implemented")
        == tfe_model.get("source_reference_solution_policy_full_T10_probe_implemented")
        is True,
        "TFE full T=10 source-reference probe implementation changed in manifest",
    )
    checks.check(
        external.get("tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_completed")
        == tfe_model.get("source_reference_solution_policy_full_T10_probe_completed")
        is True,
        "TFE full T=10 source-reference probe completion changed in manifest",
    )
    checks.check(
        external.get("tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_rows_completed")
        == tfe_model.get("source_reference_solution_policy_full_T10_probe_rows_completed")
        == 0,
        "TFE full T=10 source-reference probe source-policy rows changed in manifest",
    )
    checks.check(
        external.get("tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_steps")
        == tfe_model.get("source_reference_solution_policy_full_T10_probe_steps")
        == 100000,
        "TFE full T=10 source-reference probe source-step count changed in manifest",
    )
    checks.check(
        external.get("tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_check_steps")
        == tfe_model.get("source_reference_solution_policy_full_T10_probe_check_steps")
        == 200000,
        "TFE full T=10 source-reference probe check-step count changed in manifest",
    )
    checks.check(
        float(external.get("tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_coordinate_error"))
        < 1.0e-10,
        "TFE full T=10 source-reference probe coordinate check error too large in manifest",
    )
    checks.check(
        float(external.get("tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_velocity_error"))
        < 1.0e-10,
        "TFE full T=10 source-reference probe velocity check error too large in manifest",
    )
    checks.check(
        external.get("tfe_source_pendulum_source_comparator_candidate_runners_implemented")
        == tfe_model.get("source_comparator_candidate_runners_implemented")
        is True,
        "TFE source comparator candidate runner status changed",
    )
    checks.check(
        external.get("tfe_source_pendulum_newmark_beta_candidate_runner_smoke_implemented")
        == tfe_model.get("newmark_beta_candidate_runner_smoke_implemented")
        is True,
        "TFE Newmark-beta candidate runner status changed",
    )
    checks.check(
        external.get("tfe_source_pendulum_trapezoidal_candidate_runner_smoke_implemented")
        == tfe_model.get("trapezoidal_candidate_runner_smoke_implemented")
        is True,
        "TFE trapezoidal candidate runner status changed",
    )
    checks.check(
        external.get("tfe_source_pendulum_source_policy_method_runner_equivalent")
        == tfe_model.get("source_policy_method_runner_equivalent")
        is False,
        "TFE source-policy method-runner equivalence boundary changed",
    )
    checks.check(
        external.get("tfe_source_pendulum_tfe_m1_m2_m3_candidate_runner_smoke_implemented")
        == tfe_model.get("tfe_m1_m2_m3_candidate_runner_smoke_implemented")
        is True,
        "TFE m=1/2/3 candidate runner status changed",
    )
    checks.check(
        external.get("tfe_source_pendulum_tfe_m1_m2_m3_source_policy_runners_implemented")
        == tfe_model.get("tfe_m1_m2_m3_source_policy_runners_implemented")
        is False,
        "TFE m=1/2/3 source-policy runner boundary changed",
    )
    checks.check(
        external.get("tfe_source_pendulum_bounded_source_policy_runner_smoke_implemented")
        == tfe_model.get("bounded_source_policy_runner_smoke_implemented")
        is True,
        "bounded source-policy runner smoke status changed",
    )
    checks.check(
        external.get("tfe_source_pendulum_bounded_source_policy_runner_rows")
        == tfe_model.get("bounded_source_policy_runner_rows")
        == 4,
        "bounded source-policy runner row count changed",
    )
    checks.check(
        external.get("tfe_source_pendulum_bounded_source_policy_runner_full_T10")
        == tfe_model.get("bounded_source_policy_runner_full_T10")
        is False,
        "bounded source-policy runner full-run boundary changed",
    )
    checks.check(
        external.get("tfe_source_pendulum_bounded_source_policy_runner_source_policy_rows_completed")
        == tfe_model.get("bounded_source_policy_runner_source_policy_rows_completed")
        == 0,
        "bounded source-policy runner completed rows boundary changed",
    )
    checks.check(
        external.get("tfe_source_pendulum_active_b2_candidate_row_smoke_implemented")
        == tfe_model.get("active_tfe_b2_candidate_row_smoke_implemented")
        is True,
        "active B2 candidate smoke status changed",
    )
    checks.check(
        external.get("tfe_source_pendulum_active_b2_candidate_row_smoke_full_T10")
        == tfe_model.get("active_tfe_b2_candidate_row_smoke_full_T10")
        is False,
        "active B2 candidate smoke full-run boundary changed",
    )
    checks.check(
        external.get("tfe_source_pendulum_active_b2_source_policy_rows_completed")
        == tfe_model.get("active_tfe_b2_source_policy_rows_completed")
        == 0,
        "active B2 candidate source-policy rows boundary changed",
    )
    checks.check(
        external.get("tfe_source_pendulum_active_b2_candidate_row_count")
        == len(tfe_model.get("active_tfe_b2_candidate_row_smoke", {}).get("rows", []))
        == 4,
        "active B2 candidate row count changed",
    )
    checks.check(
        external.get("tfe_full_t10_absolute_dae_lift_status")
        == tfe_full_t10_absolute.get("status")
        == "full_T10_absolute_dae_lift_candidate_summarized_not_source_policy",
        "TFE full-T10 absolute DAE-lift status not carried into manifest external status",
    )
    checks.check(
        external.get("tfe_full_t10_absolute_dae_lift_completed")
        == tfe_full_t10_absolute.get("full_T10_absolute_coordinate_lift_completed")
        is True,
        "TFE full-T10 absolute DAE-lift completion not carried into manifest external status",
    )
    checks.check(
        external.get("tfe_full_t10_absolute_dae_lift_method_count")
        == tfe_full_t10_absolute.get("method_count")
        == 4
        and external.get("tfe_full_t10_absolute_dae_lift_metric_rows")
        == tfe_full_t10_absolute.get("metric_row_count")
        == 12
        and external.get("tfe_full_t10_absolute_dae_lift_step_residual_rows")
        == tfe_full_t10_absolute.get("step_residual_row_count")
        == 2800,
        "TFE full-T10 absolute DAE-lift counts not carried into manifest external status",
    )
    checks.check(
        external.get("tfe_full_t10_absolute_dae_lift_source_reference_invoked")
        == tfe_full_t10_absolute.get("source_reference_invoked")
        is True
        and external.get("tfe_full_t10_absolute_dae_lift_source_policy_rows_completed")
        == tfe_full_t10_absolute.get("source_policy_rows_completed")
        == 0
        and external.get("tfe_full_t10_absolute_dae_lift_monolithic")
        == tfe_full_t10_absolute.get("monolithic_absolute_coordinate_dae_time_integrator")
        is False
        and external.get("tfe_full_t10_absolute_dae_lift_equivalent")
        == tfe_full_t10_absolute.get("source_policy_dae_runner_equivalent")
        is False,
        "TFE full-T10 absolute DAE-lift overclosed source-policy boundary in manifest external status",
    )
    checks.check(
        external.get("tfe_endpoint_boundary_certificate_status")
        == tfe_endpoint_boundary.get("status")
        == "endpoint_policy_literal_overrun_bound_proved_source_policy_open",
        "TFE endpoint boundary status not carried into manifest external status",
    )
    checks.check(
        external.get("tfe_endpoint_boundary_literal_overrun_bound_proved") is True
        and tfe_endpoint_boundary.get("theorem", {}).get("name")
        == "fixed_h_until_final_time_endpoint_bound",
        "TFE endpoint boundary theorem not carried into manifest external status",
    )
    checks.check(
        external.get("tfe_endpoint_boundary_literal_exact_T_rows")
        == tfe_endpoint_boundary.get("algorithm_literal_exact_T_row_count")
        == 2
        and external.get("tfe_endpoint_boundary_literal_overrun_rows")
        == tfe_endpoint_boundary.get("algorithm_literal_overrun_row_count")
        == 4,
        "TFE endpoint boundary row counts not carried into manifest external status",
    )
    checks.check(
        external.get("tfe_endpoint_boundary_source_policy_rows_completed")
        == tfe_endpoint_boundary.get("source_policy_rows_completed")
        == 0
        and external.get("tfe_endpoint_boundary_full_T10_policy_resolved")
        == tfe_endpoint_boundary.get("source_grid_policy_resolved_for_full_T10")
        is False
        and external.get("tfe_endpoint_boundary_exact_T_error_sampling_equivalent")
        == tfe_endpoint_boundary.get("source_policy_exact_T_error_sampling_equivalent")
        is False,
        "TFE endpoint boundary overclosed source-policy boundary in manifest external status",
    )
    checks.check(
        external.get("tfe_full_T10_endpoint_policy_closure_certificate_status")
        == tfe_endpoint_certificate.get("status")
        == "negative_full_T10_endpoint_policy_certificate_not_source_policy"
        and external.get("tfe_full_T10_endpoint_policy_closure_certificate_available") is True
        and external.get("tfe_full_T10_endpoint_policy_closure_certificate_positive") is False
        and external.get("tfe_full_T10_endpoint_policy_closure_certificate_nonheavy_block_closed")
        is False,
        "TFE full-T10 endpoint policy closure certificate boundary changed in manifest external status",
    )
    checks.check(
        external.get("tfe_full_T10_endpoint_policy_closure_certificate_source_policy_execution_invoked")
        == tfe_endpoint_certificate.get("source_policy_execution_invoked")
        is False
        and external.get("tfe_full_T10_endpoint_policy_closure_certificate_can_close_now")
        == tfe_endpoint_certificate.get("can_close_now")
        is False,
        "TFE full-T10 endpoint policy closure certificate closure flags changed in manifest external status",
    )
    checks.check(
        external.get("tfe_source_grid_policy_resolved_for_full_T10") is False
        and external.get("tfe_source_grid_integer_step_incompatible_rows") == 4
        and external.get("tfe_source_grid_exact_T_compatible_rows_endpoint_convention_resolved") == 2
        and external.get("tfe_source_grid_endpoint_incompatible_rows_requiring_policy") == 4
        and external.get("tfe_source_grid_policy_resolved_for_exact_T_compatible_rows") is True
        and external.get("tfe_source_grid_source_text_available") is True
        and external.get("tfe_source_grid_source_text_anchor_count", 0) >= 8
        and external.get("tfe_source_grid_algorithm_literal_fixed_h") is True
        and external.get("tfe_source_grid_endpoint_convention_resolved_for_error_sampling") is False,
        "TFE source-grid endpoint evidence not carried into manifest external status",
    )
    checks.check(
        external.get("tfe_endpoint_sensitivity_status")
        == tfe_endpoint_sensitivity.get("status")
        == "diagnostic_endpoint_policy_sensitivity_not_source_policy",
        "TFE endpoint sensitivity status not carried into manifest external status",
    )
    checks.check(
        external.get("tfe_endpoint_sensitivity_method_count")
        == tfe_endpoint_sensitivity.get("method_count")
        == 4
        and external.get("tfe_endpoint_sensitivity_policy_count")
        == tfe_endpoint_sensitivity.get("policy_count")
        == 4
        and external.get("tfe_endpoint_sensitivity_summary_row_count")
        == tfe_endpoint_sensitivity.get("summary_row_count")
        == 16
        and external.get("tfe_endpoint_sensitivity_raw_row_count")
        == tfe_endpoint_sensitivity.get("raw_row_count")
        == 48,
        "TFE endpoint sensitivity counts not carried into manifest external status",
    )
    checks.check(
        external.get("tfe_endpoint_sensitivity_source_policy_rows_completed")
        == tfe_endpoint_sensitivity.get("source_policy_rows_completed")
        == 0
        and external.get("tfe_endpoint_sensitivity_external_superiority_claim_allowed")
        == tfe_endpoint_sensitivity.get("external_superiority_claim_allowed")
        is False
        and external.get("tfe_endpoint_sensitivity_source_policy_runner_equivalent")
        == tfe_endpoint_sensitivity.get("source_policy_runner_equivalent")
        is False,
        "TFE endpoint sensitivity overclosed source-policy boundary in manifest external status",
    )
    checks.check(
        external.get("tfe_endpoint_sensitivity_default_1e_4_campaign_invoked") is False
        and external.get("tfe_endpoint_sensitivity_run_v047_invoked") is False,
        "TFE endpoint sensitivity invoked a forbidden run in manifest external status",
    )
    checks.check(
        external.get("tfe_source_pendulum_error_output_policy_encoded")
        == tfe_model.get("source_error_norm_and_output_policy_encoded")
        is True,
        "TFE source pendulum output policy status changed",
    )
    checks.check(
        external.get("tfe_source_pendulum_brown_mcphee_candidate_friction_law_encoded")
        == tfe_model.get("brown_mcphee_candidate_friction_law_encoded")
        is True,
        "TFE source pendulum candidate friction status changed",
    )
    checks.check(
        external.get("tfe_source_pendulum_frictional_candidate_smoke_implemented")
        == tfe_model.get("frictional_planar_candidate_rhs_smoke_implemented")
        is True,
        "TFE source pendulum frictional candidate smoke status changed",
    )
    checks.check(
        external.get("tfe_source_pendulum_candidate_friction_law_provenance")
        == "v022_revolute_brown_mcphee_surrogate_not_source_policy_equivalent",
        "TFE source pendulum candidate friction provenance changed",
    )
    checks.check(
        external.get("tfe_brown_mcphee_candidate_dae_contract_rows")
        == tfe_brown_mcphee_contract.get("row_count")
        == 12
        and external.get("tfe_brown_mcphee_candidate_dae_contract_step_rows")
        == tfe_brown_mcphee_contract.get("step_residual_row_count")
        == 56
        and external.get("tfe_brown_mcphee_candidate_dae_contract_source_policy_rows")
        == tfe_brown_mcphee_contract.get("source_policy_rows_completed")
        == 0,
        "TFE Brown-McPhee candidate DAE contract row boundary changed in manifest external status",
    )
    checks.check(
        external.get("tfe_brown_mcphee_candidate_dae_contract_all_finite") is True
        and external.get("tfe_brown_mcphee_candidate_dae_contract_residual_ok") is True
        and external.get("tfe_brown_mcphee_candidate_dae_contract_power_nonpositive") is True,
        "TFE Brown-McPhee candidate DAE contract evidence changed in manifest external status",
    )
    checks.check(
        external.get("tfe_brown_mcphee_candidate_dae_contract_equivalent_dae") is False
        and external.get("tfe_brown_mcphee_candidate_dae_contract_equivalent_method") is False
        and external.get("tfe_brown_mcphee_candidate_dae_contract_source_law") is False
        and external.get("tfe_brown_mcphee_candidate_dae_contract_monolithic") is False,
        "TFE Brown-McPhee candidate DAE contract overclaims equivalence in manifest external status",
    )
    checks.check(
        external.get("tfe_brown_mcphee_transition_velocity_sensitivity_rows")
        == tfe_brown_mcphee_velocity_sensitivity.get("endpoint_delta_row_count")
        == 3
        and external.get("tfe_brown_mcphee_transition_velocity_sensitivity_contract_rows")
        == tfe_brown_mcphee_velocity_sensitivity.get("contract_row_count")
        == 36
        and external.get("tfe_brown_mcphee_transition_velocity_sensitivity_source_policy_rows")
        == tfe_brown_mcphee_velocity_sensitivity.get("source_policy_rows_completed")
        == 0,
        "TFE Brown-McPhee transition-velocity sensitivity row boundary changed in external status",
    )
    checks.check(
        external.get("tfe_brown_mcphee_transition_velocity_sensitivity_material") is True
        and external.get("tfe_brown_mcphee_transition_velocity_sensitivity_equivalence_flags_false")
        is True,
        "TFE Brown-McPhee transition-velocity sensitivity material boundary changed in external status",
    )
    checks.check(
        external.get("tfe_brown_mcphee_source_code_equivalence_certificate_status")
        == tfe_brown_mcphee_certificate.get("status")
        == "negative_source_code_equivalence_certificate_not_source_policy"
        and external.get("tfe_brown_mcphee_source_code_equivalence_certificate_available") is True
        and external.get("tfe_brown_mcphee_source_code_equivalence_certificate_positive") is False
        and external.get("tfe_brown_mcphee_source_code_equivalence_certificate_nonheavy_block_closed")
        is False,
        "TFE Brown-McPhee source-code equivalence certificate boundary changed in manifest external status",
    )
    checks.check(
        external.get("tfe_brown_mcphee_source_code_equivalence_certificate_source_policy_execution_invoked")
        == tfe_brown_mcphee_certificate.get("source_policy_execution_invoked")
        is False
        and external.get("tfe_brown_mcphee_source_code_equivalence_certificate_can_close_now")
        == tfe_brown_mcphee_certificate.get("can_close_now")
        is False,
        "TFE Brown-McPhee source-code equivalence certificate closure flags changed in manifest external status",
    )
    checks.check(
        external.get("tfe_source_pendulum_setup_subrequirement_closed")
        == tfe_model.get("closure_boundary", {}).get("can_close_source_pendulum_setup_subrequirement")
        is True,
        "TFE source pendulum setup subrequirement changed",
    )
    checks.check(
        external.get("tfe_source_policy_runner_implemented")
        == tfe.get("pendulum_dae_runner_implemented")
        is False,
        "TFE source-policy runner status changed",
    )
    checks.check(
        external.get("tfe_candidate_source_policy_boundary")
        == external_checks.get("tfe_candidate_source_policy_boundary")
        == expected_tfe_candidate_source_policy_boundary,
        "TFE candidate/source-policy boundary missing from manifest external status",
    )
    checks.check(
        external.get("tfe_candidate_source_policy_boundary_sources")
        == external_checks.get("tfe_candidate_source_policy_boundary_sources")
        == expected_tfe_candidate_source_policy_boundary_sources,
        "TFE candidate/source-policy boundary sources missing from manifest external status",
    )
    checks.check(
        external.get("tfe_candidate_source_policy_boundary_sources_match")
        == external_checks.get("tfe_candidate_source_policy_boundary_sources_match")
        is True,
        "TFE candidate/source-policy boundary source-match missing from manifest external status",
    )
    checks.check(
        external.get("tfe_candidate_source_policy_allowed_use")
        == external_checks.get("tfe_candidate_source_policy_allowed_use")
        == "diagnostic_scaffold_only_not_source_policy_reproduction",
        "TFE candidate/source-policy allowed-use boundary changed in manifest external status",
    )
    checks.check(
        external.get("tfe_candidate_source_policy_dae_runner_equivalent")
        == external_checks.get("tfe_candidate_source_policy_dae_runner_equivalent")
        is False
        and external.get("tfe_candidate_source_policy_method_runner_equivalent")
        == external_checks.get("tfe_candidate_source_policy_method_runner_equivalent")
        is False
        and external.get("tfe_candidate_source_policy_rows_completed")
        == external_checks.get("tfe_candidate_source_policy_rows_completed")
        == 0
        and external.get("tfe_candidate_source_policy_external_superiority_allowed")
        == external_checks.get("tfe_candidate_source_policy_external_superiority_allowed")
        is False,
        "TFE candidate/source-policy non-equivalence boundary changed in manifest external status",
    )
    checks.check(
        external.get("tfe_dae_runner_contract_gap_status") == tfe_dae_gap.get("status")
        and external.get("tfe_dae_runner_contract_gap_missing_block_count") == 6
        and external.get("tfe_dae_runner_contract_gap_missing_block_ids") == expected_tfe_dae_gap_ids
        and external.get("tfe_dae_runner_contract_gap_nonheavy_blocks")
        == tfe_dae_gap.get("nonheavy_missing_contract_blocks")
        and external.get("tfe_dae_runner_contract_gap_terminal_nonpromoted_blocks")
        == expected_tfe_dae_nonheavy_gap_ids
        and external.get("tfe_dae_runner_contract_gap_terminal_nonpromoted_block_count") == 2
        and external.get("tfe_dae_runner_contract_gap_effective_missing_blocks")
        == expected_tfe_dae_execution_gap_ids
        and external.get("tfe_dae_runner_contract_gap_effective_missing_block_count") == 4
        and external.get("tfe_dae_runner_contract_gap_block_accounting", {}).get(
            "source_policy_rows_closed_by_accounting"
        )
        == 0
        and external.get("tfe_dae_runner_contract_gap_execution_blocks")
        == tfe_dae_gap.get("source_policy_execution_missing_contract_blocks")
        and external.get("tfe_dae_runner_contract_gap_ready_to_execute_source_policy_now") is False
        and external.get("tfe_dae_runner_contract_gap_heavy_run_invoked") is False,
        "TFE DAE runner contract gap fields missing from manifest external status",
    )
    checks.check(
        external.get("tfe_source_policy_execution_preflight") == tfe_source_policy_execution_preflight,
        "TFE source-policy execution preflight not inherited into manifest external status",
    )
    checks.check(
        external.get("tfe_source_policy_execution_preflight_status")
        == tfe_source_policy_execution_preflight.get("status")
        == "terminal_no_public_code_self_reproduction_attempted_not_promoted",
        "TFE source-policy execution preflight status changed in manifest external status",
    )
    checks.check(
        external.get("tfe_source_policy_execution_preflight_opt_in_required")
        == tfe_source_policy_execution_preflight.get("explicit_user_opt_in_required")
        is False,
        "TFE source-policy execution preflight opt-in boundary changed in manifest external status",
    )
    checks.check(
        external.get("tfe_source_policy_execution_preflight_nonheavy_dispositioned")
        == tfe_source_policy_execution_preflight.get("nonheavy_blocks_dispositioned_by_demotion")
        is True
        and external.get("tfe_source_policy_execution_preflight_execution_block_count")
        == tfe_source_policy_execution_preflight.get("execution_block_count")
        == 4,
        "TFE source-policy execution preflight block boundary changed in manifest external status",
    )
    checks.check(
        external.get("tfe_source_policy_execution_preflight_can_promote_rows_now")
        == tfe_source_policy_execution_preflight.get("can_promote_any_tfe_source_policy_row_now")
        is False
        and external.get("tfe_source_policy_execution_preflight_ready_now")
        == tfe_source_policy_execution_preflight.get("ready_to_execute_source_policy_now")
        is False,
        "TFE source-policy execution preflight overclaims promotion/readiness in manifest external status",
    )
    checks.check(
        external.get("tfe_runner_contract_preflight_status")
        == tfe_runner_contract_preflight.get("status")
        == "contract_entrypoints_callable_candidate_backed_source_policy_open"
        and external.get("tfe_runner_contract_preflight_entrypoints") == "3/3"
        and external.get("tfe_runner_contract_preflight_candidate_backed") == "3/3"
        and external.get("tfe_runner_contract_preflight_source_policy_rows_completed")
        == tfe_runner_contract_preflight.get("source_policy_rows_completed")
        == 0
        and external.get("tfe_runner_contract_preflight_execution_blocks")
        == tfe_runner_contract_preflight.get("source_policy_execution_block_count")
        == 4
        and external.get("tfe_runner_contract_preflight_safe_use")
        == tfe_runner_contract_preflight.get("safe_current_use")
        == "runner_contract_preflight_only_not_source_policy_reproduction",
        "TFE runner contract preflight boundary missing from manifest external status",
    )
    checks.check(
        external.get("oc12_archive_tfe_runner_contract_preflight_status")
        == objective_summary.get("full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_status")
        == "contract_entrypoints_callable_candidate_backed_source_policy_open"
        and external.get("oc12_archive_tfe_runner_contract_preflight_entrypoints")
        == objective_summary.get("full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_entrypoints")
        == "3/3"
        and external.get("oc12_archive_tfe_runner_contract_preflight_candidate_backed")
        == objective_summary.get("full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_candidate_backed")
        == "3/3"
        and external.get("oc12_archive_tfe_runner_contract_preflight_source_policy_rows_completed")
        == objective_summary.get(
            "full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_source_policy_rows_completed"
        )
        == 0
        and external.get("oc12_archive_tfe_runner_contract_preflight_execution_blocks")
        == objective_summary.get("full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_execution_blocks")
        == 4
        and external.get("oc12_archive_tfe_runner_contract_preflight_safe_use")
        == objective_summary.get("full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_safe_use")
        == "runner_contract_preflight_only_not_source_policy_reproduction",
        "OC12 archive TFE runner contract preflight boundary missing from manifest external status",
    )
    checks.check(
        external.get("oc12_archive_action_boundary")
        == objective_summary.get("full_source_policy_runner_archive_gap_action_boundary")
        == expected_archive_action_boundary
        and external.get("oc12_archive_safe_without_b4_opt_in_count")
        == objective_summary.get("full_source_policy_runner_archive_gap_safe_without_b4_opt_in_count")
        == full_source_runner_gap.get("safe_without_b4_opt_in_count")
        == 4
        and external.get("oc12_archive_opt_in_required_action_count")
        == objective_summary.get("full_source_policy_runner_archive_gap_opt_in_required_action_count")
        == full_source_runner_gap.get("opt_in_required_action_count")
        == 1
        and external.get("oc12_archive_source_policy_execution_allowed_now")
        == objective_summary.get("full_source_policy_runner_archive_gap_source_policy_execution_allowed_now")
        == full_source_runner_gap.get("source_policy_execution_allowed_now")
        is False
        and external.get("oc12_archive_source_policy_execution_invoked")
        == objective_summary.get("full_source_policy_runner_archive_gap_source_policy_execution_invoked")
        == full_source_runner_gap.get("source_policy_execution_invoked")
        is False
        and external.get("oc12_archive_exact_b4_opt_in_required_for_execution")
        == objective_summary.get("full_source_policy_runner_archive_gap_exact_b4_opt_in_required_for_execution")
        == full_source_runner_gap.get("exact_b4_opt_in_required_for_execution")
        is True
        and external.get("oc12_archive_opt_in_required_command_count")
        == objective_summary.get("full_source_policy_runner_archive_gap_opt_in_required_command_count")
        == full_source_runner_gap.get("opt_in_required_command_count")
        == 13
        and external.get("oc12_archive_opt_in_required_mapped_external_rows")
        == objective_summary.get("full_source_policy_runner_archive_gap_opt_in_required_mapped_external_rows")
        == full_source_runner_gap.get("opt_in_required_mapped_external_rows")
        == 20
        and external.get("oc12_archive_safe_action_ids")
        == objective_summary.get("full_source_policy_runner_archive_gap_safe_action_ids")
        == expected_archive_safe_action_ids
        and external.get("oc12_archive_opt_in_action_ids")
        == objective_summary.get("full_source_policy_runner_archive_gap_opt_in_action_ids")
        == expected_archive_opt_in_action_ids,
        "OC12 archive action boundary missing from manifest external status",
    )
    checks.check(
        external.get("tfe_source_policy_self_reproduction_preflight")
        == tfe_self_reproduction_execution_preflight,
        "TFE self-reproduction preflight not inherited into manifest external status",
    )
    checks.check(
        external.get("tfe_source_policy_self_reproduction_preflight_status")
        == tfe_self_reproduction_execution_preflight.get("status")
        == "terminal_no_public_code_self_reproduction_attempted_not_promoted",
        "TFE self-reproduction preflight status changed in manifest external status",
    )
    checks.check(
        external.get("tfe_source_policy_self_reproduction_preflight_current_route")
        == tfe_self_reproduction_execution_preflight.get("current_route")
        == "no_public_code_self_reproduction_attempted_unable_to_reproduce_not_promoted"
        and external.get("tfe_source_policy_self_reproduction_preflight_reopen_condition")
        == tfe_self_reproduction_execution_preflight.get("reopen_condition")
        == "new_public_or_source_code_equivalent_tfe_implementation_artifact",
        "TFE self-reproduction preflight route/reopen condition changed in manifest external status",
    )
    checks.check(
        external.get("tfe_source_policy_self_reproduction_preflight_execution_block_count")
        == tfe_self_reproduction_execution_preflight.get("execution_block_count")
        == 4
        and external.get("tfe_source_policy_self_reproduction_preflight_can_promote_rows_now")
        == tfe_self_reproduction_execution_preflight.get("can_promote_any_tfe_source_policy_row_now")
        is False
        and external.get("tfe_source_policy_self_reproduction_preflight_ready_now")
        == tfe_self_reproduction_execution_preflight.get("ready_to_execute_source_policy_now")
        is False,
        "TFE self-reproduction preflight overclaims promotion/readiness in manifest external status",
    )
    checks.check(
        external.get("tfe_source_policy_self_reproduction_preflight_source_policy_rows_completed")
        == tfe_self_reproduction_execution_preflight.get("source_policy_rows_completed")
        == 0
        and external.get("tfe_source_policy_self_reproduction_required_next_action_count")
        == len(tfe_self_reproduction_attempt_certificate.get("required_next_actions", []))
        == 3,
        "TFE self-reproduction preflight row/next-action counts changed in manifest external status",
    )
    checks.check(
        external.get("tfe_source_policy_self_reproduction_preflight_runner_contracts_required")
        == tfe_self_reproduction_execution_preflight.get("runner_contracts_required_before_execution")
        == expected_tfe_self_reproduction_runner_contracts,
        "TFE self-reproduction runner-contract requirements changed in manifest external status",
    )

    checks.check(proof_status.get("proof_closure_status") == proof.get("status"), "proof closure status stale")
    checks.check(
        proof_status.get("direct_pc2_proof_gap_closed")
        == proof_status.get("proof_gap_closed")
        is True
        and proof_status.get("proof_gap_closed_scope")
        == "direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open"
        and "schema-compatible shorthand for direct_pc2_proof_gap_closed"
        in proof_status.get("proof_gap_closed_reading_rule", ""),
        "proof-status direct proof closure must be scoped",
    )
    proof_theorem_boundary = proof.get("theorem_statement_boundary", {})
    proof_manuscript_traceability = proof.get("manuscript_traceability", {})
    proof_claim_theorem_traceability = proof_claim_traceability.get("manuscript_theorem_traceability", {})
    proof_claim_remaining_boundary = proof_claim_traceability.get("remaining_claim_boundary", {})
    checks.check(
        summary.get("proof_theorem_statement_labels_present")
        == proof_status.get("theorem_statement_labels_present")
        == proof_theorem_boundary.get("all_required_labels_present_main_and_flat")
        is True,
        "proof theorem labels not carried into package manifest",
    )
    checks.check(
        summary.get("proof_theorem_statement_boundary_present")
        == proof_status.get("theorem_statement_boundary_present")
        == proof_theorem_boundary.get("conditional_theorem_boundary_present_main_and_flat")
        is True,
        "proof theorem boundary not carried into package manifest",
    )
    checks.check(
        summary.get("proof_theorem_statement_eta_condition_retained")
        == proof_status.get("theorem_statement_eta_condition_retained")
        == proof_theorem_boundary.get("eta_h_theorem_condition_retained")
        is True,
        "proof theorem eta_h condition missing from package manifest",
    )
    checks.check(
        summary.get("proof_theorem_statement_eta_evidence_closed")
        == proof_status.get("theorem_statement_eta_evidence_closed")
        == proof_theorem_boundary.get("eta_h_solver_policy_evidence_closed")
        is False,
        "proof theorem eta_h evidence overclaimed in package manifest",
    )
    checks.check(
        summary.get("proof_theorem_statement_fixed_tolerance_asymptotic_proof")
        == proof_status.get("theorem_statement_fixed_tolerance_asymptotic_proof")
        == proof_theorem_boundary.get("fixed_tolerance_runs_are_asymptotic_proof")
        is False,
        "proof theorem fixed-tolerance evidence promoted in package manifest",
    )
    checks.check(
        summary.get("proof_theorem_statement_residual_to_error_not_promoted")
        == proof_status.get("theorem_statement_residual_to_error_not_promoted")
        == proof_theorem_boundary.get("does_not_promote_residual_to_error")
        is True,
        "proof residual-to-error boundary missing from package manifest",
    )
    checks.check(
        summary.get("proof_theorem_statement_source_policy_or_full_tfe_not_promoted")
        == proof_status.get("theorem_statement_source_policy_or_full_tfe_not_promoted")
        == proof_theorem_boundary.get("does_not_promote_source_policy_or_full_tfe")
        is True,
        "proof source-policy/full-TFE nonpromotion missing from package manifest",
    )
    checks.check(
        summary.get("proof_manuscript_traceability_mapped")
        == proof_status.get("manuscript_traceability_mapped")
        == proof_manuscript_traceability.get("conditional_proof_claims_mapped_to_manuscript")
        is True,
        "proof manuscript traceability mapping missing from package manifest",
    )
    checks.check(
        summary.get("proof_manuscript_traceability_no_state_change")
        == proof_status.get("manuscript_traceability_no_state_change")
        == proof_manuscript_traceability.get("does_not_change_proof_closure_state")
        is True,
        "proof manuscript traceability state boundary missing from package manifest",
    )
    checks.check(
        summary.get("proof_manuscript_traceability_dependency_graph_present")
        == proof_status.get("manuscript_traceability_dependency_graph_present")
        == proof_manuscript_traceability.get("proof_dependency_graph_present_main_and_flat")
        is True,
        "proof manuscript dependency graph missing from package manifest",
    )
    checks.check(
        summary.get("proof_manuscript_traceability_dynamic_matrix_present")
        == proof_status.get("manuscript_traceability_dynamic_matrix_present")
        == proof_manuscript_traceability.get("dynamic_proof_closure_matrix_present_main_and_flat")
        is True,
        "proof manuscript dynamic matrix traceability missing from package manifest",
    )
    checks.check(
        summary.get("proof_manuscript_traceability_primitive_lane_boundary_present")
        == proof_status.get("manuscript_traceability_primitive_lane_boundary_present")
        == proof_manuscript_traceability.get("primitive_lane_boundary_present_main_and_flat")
        is True,
        "proof manuscript primitive-route boundary missing from package manifest",
    )
    checks.check(
        summary.get("proof_manuscript_traceability_residual_nonpromotion_present")
        == proof_status.get("manuscript_traceability_residual_nonpromotion_present")
        == proof_manuscript_traceability.get("residual_to_error_nonpromotion_present_main_and_flat")
        is True,
        "proof manuscript residual nonpromotion traceability missing from package manifest",
    )
    checks.check(
        summary.get("proof_claim_traceability_theorem_label")
        == proof_status.get("proof_claim_traceability_theorem_label")
        == proof_checks.get("proof_claim_traceability_theorem_label")
        == proof_claim_theorem_traceability.get("accepted_theorem_label")
        == "thm:g6fullva-order",
        "proof-claim theorem label not carried into package manifest",
    )
    for summary_key, proof_status_key, review_key, source_key in [
        (
            "proof_claim_traceability_theorem_labels_present",
            "proof_claim_traceability_theorem_labels_present",
            "proof_claim_traceability_theorem_labels_present",
            "theorem_statement_labels_present",
        ),
        (
            "proof_claim_traceability_theorem_boundary_present",
            "proof_claim_traceability_theorem_boundary_present",
            "proof_claim_traceability_theorem_boundary_present",
            "conditional_theorem_boundary_present",
        ),
        (
            "proof_claim_traceability_theorem_claims_mapped",
            "proof_claim_traceability_theorem_claims_mapped",
            "proof_claim_traceability_theorem_claims_mapped",
            "conditional_proof_claims_mapped_to_manuscript",
        ),
        (
            "proof_claim_traceability_dependency_graph_present",
            "proof_claim_traceability_dependency_graph_present",
            "proof_claim_traceability_dependency_graph_present",
            "proof_dependency_graph_present",
        ),
        (
            "proof_claim_traceability_table_present",
            "proof_claim_traceability_table_present",
            "proof_claim_traceability_table_present",
            "proof_traceability_table_present",
        ),
        (
            "proof_claim_traceability_dynamic_theorem_matrix_present",
            "proof_claim_traceability_dynamic_theorem_matrix_present",
            "proof_claim_traceability_dynamic_theorem_matrix_present",
            "dynamic_proof_closure_matrix_present",
        ),
        (
            "proof_claim_traceability_primitive_lane_boundary_present",
            "proof_claim_traceability_primitive_lane_boundary_present",
            "proof_claim_traceability_primitive_lane_boundary_present",
            "primitive_lane_boundary_present",
        ),
        (
            "proof_claim_traceability_residual_nonpromotion_present",
            "proof_claim_traceability_residual_nonpromotion_present",
            "proof_claim_traceability_residual_nonpromotion_present",
            "residual_nonpromotion_present",
        ),
        (
            "proof_claim_traceability_eta_condition_retained",
            "proof_claim_traceability_eta_condition_retained",
            "proof_claim_traceability_eta_condition_retained",
            "eta_h_theorem_condition_retained",
        ),
        (
            "proof_claim_traceability_residual_to_error_not_promoted",
            "proof_claim_traceability_residual_to_error_not_promoted",
            "proof_claim_traceability_residual_to_error_not_promoted",
            "residual_to_error_not_promoted",
        ),
        (
            "proof_claim_traceability_p7_retained_nonpromotion_boundary_present",
            "proof_claim_traceability_p7_retained_nonpromotion_boundary_present",
            "proof_claim_traceability_p7_retained_nonpromotion_boundary_present",
            "p7_retained_nonpromotion_boundary_present",
        ),
        (
            "proof_claim_traceability_b1_closure_scope_boundary_present",
            "proof_claim_traceability_b1_closure_scope_boundary_present",
            "proof_claim_traceability_b1_closure_scope_boundary_present",
            "b1_closure_scope_boundary_present",
        ),
        (
            "proof_claim_traceability_p6_solver_scope_boundary_present",
            "proof_claim_traceability_p6_solver_scope_boundary_present",
            "proof_claim_traceability_p6_solver_scope_boundary_present",
            "p6_solver_scope_boundary_present",
        ),
        (
            "proof_claim_traceability_p1p2_compact_tube_boundary_present",
            "proof_claim_traceability_p1p2_compact_tube_boundary_present",
            "proof_claim_traceability_p1p2_compact_tube_boundary_present",
            "p1p2_compact_tube_boundary_present",
        ),
        (
            "proof_claim_traceability_p3p4_implementation_boundary_present",
            "proof_claim_traceability_p3p4_implementation_boundary_present",
            "proof_claim_traceability_p3p4_implementation_boundary_present",
            "p3p4_implementation_boundary_present",
        ),
        (
            "proof_claim_traceability_p5_direct_route_boundary_present",
            "proof_claim_traceability_p5_direct_route_boundary_present",
            "proof_claim_traceability_p5_direct_route_boundary_present",
            "p5_direct_route_boundary_present",
        ),
        (
            "proof_claim_traceability_source_policy_or_full_tfe_not_promoted",
            "proof_claim_traceability_source_policy_or_full_tfe_not_promoted",
            "proof_claim_traceability_source_policy_or_full_tfe_not_promoted",
            "source_policy_or_full_tfe_not_promoted",
        ),
        (
            "proof_claim_traceability_no_state_change",
            "proof_claim_traceability_no_state_change",
            "proof_claim_traceability_no_state_change",
            "does_not_change_proof_closure_state",
        ),
    ]:
        checks.check(
            summary.get(summary_key)
            == proof_status.get(proof_status_key)
            == proof_checks.get(review_key)
            == proof_claim_theorem_traceability.get(source_key)
            is True,
            f"proof-claim theorem true marker not carried into package manifest: {summary_key}",
        )
    for summary_key, proof_status_key, review_key, source_key in [
        (
            "proof_claim_traceability_eta_evidence_closed",
            "proof_claim_traceability_eta_evidence_closed",
            "proof_claim_traceability_eta_evidence_closed",
            "eta_h_solver_policy_evidence_closed",
        ),
        (
            "proof_claim_traceability_fixed_tolerance_asymptotic_proof",
            "proof_claim_traceability_fixed_tolerance_asymptotic_proof",
            "proof_claim_traceability_fixed_tolerance_asymptotic_proof",
            "fixed_tolerance_runs_are_asymptotic_proof",
        ),
    ]:
        checks.check(
            summary.get(summary_key)
            == proof_status.get(proof_status_key)
            == proof_checks.get(review_key)
            == proof_claim_theorem_traceability.get(source_key)
            is False,
            f"proof-claim theorem false boundary not carried into package manifest: {summary_key}",
        )
    checks.check(
        "Proof-claim theorem traceability: label `thm:g6fullva-order`; labels/boundary/mapped `True/True/True`; dependency/table/dynamic `True/True/True`."
        in manifest_md,
        "manifest markdown missing proof-claim theorem traceability summary",
    )
    checks.check(
        "Proof-claim theorem no-promotion boundary: primitive/residual `True/True`; eta condition/closure/fixed proof `True/False/False`; residual/source-policy-full-TFE not promoted `True/True`; no-state-change `True`."
        in manifest_md,
        "manifest markdown missing proof-claim theorem no-promotion boundary summary",
    )
    checks.check(
        summary.get("proof_claim_traceability_remaining_boundary_status")
        == proof_status.get("proof_claim_traceability_remaining_boundary_status")
        == proof_checks.get("proof_claim_traceability_remaining_boundary_status")
        == proof_claim_remaining_boundary.get("status")
        == "theorem_conditions_retained_not_submission_ready",
        "proof-claim remaining boundary status not carried into package manifest",
    )
    checks.check(
        summary.get("proof_claim_traceability_submission_satisfied_assumption_ids")
        == proof_status.get("proof_claim_traceability_submission_satisfied_assumption_ids")
        == proof_checks.get("proof_claim_traceability_submission_satisfied_assumption_ids")
        == proof_claim_remaining_boundary.get("submission_satisfied_ids")
        == ["P5"],
        "proof-claim satisfied assumption IDs not carried into package manifest",
    )
    checks.check(
        summary.get("proof_claim_traceability_retained_or_open_assumption_ids")
        == proof_status.get("proof_claim_traceability_retained_or_open_assumption_ids")
        == proof_checks.get("proof_claim_traceability_retained_or_open_assumption_ids")
        == proof_claim_remaining_boundary.get("retained_or_open_ids")
        == ["P1", "P2", "P3", "P4", "P6", "P7"],
        "proof-claim retained-interface/open-nonpromotion IDs not carried into package manifest",
    )
    checks.check(
        summary.get("proof_claim_traceability_retained_theorem_interface_ids")
        == proof_status.get("proof_claim_traceability_retained_theorem_interface_ids")
        == proof_claim_remaining_boundary.get("retained_theorem_interface_ids")
        == expected_retained_theorem_interface_ids
        and summary.get("proof_claim_traceability_open_nonpromotion_boundary_ids")
        == proof_status.get("proof_claim_traceability_open_nonpromotion_boundary_ids")
        == proof_claim_remaining_boundary.get("open_nonpromotion_boundary_ids")
        == expected_open_nonpromotion_boundary_ids,
        "proof-claim categorical partition IDs not carried into package manifest",
    )
    checks.check(
        summary.get("proof_claim_traceability_remaining_global_boundaries")
        == proof_status.get("proof_claim_traceability_remaining_global_boundaries")
        == proof_checks.get("proof_claim_traceability_remaining_global_boundaries")
        == proof_claim_remaining_boundary.get("global_submission_boundaries_retained")
        == [
            "full_source_policy_package_ready",
            "theorem_level_eta_h_solver_policy_evidence",
            "closed_residual_to_error_theorem_for_mechanism_rows",
        ],
        "proof-claim remaining global boundaries not carried into package manifest",
    )
    checks.check(
        proof_status.get("proof_writing_boundary_card_status")
        == proof_writing_card.get("status")
        == strict_proof_boundary.get("proof_writing_card_status")
        == "conditional_theorem_traceable_direct_pc2_closed_global_boundaries_retained",
        "proof-writing card status not carried into proof_status",
    )
    checks.check(
        summary.get("proof_claim_traceability_reader_facing_manuscript_boundary_present")
        == proof_status.get("proof_claim_traceability_reader_facing_manuscript_boundary_present")
        == proof_checks.get("proof_claim_traceability_reader_facing_manuscript_boundary_present")
        == proof_status.get("proof_writing_boundary_reader_facing_manuscript_boundary_present")
        == proof_writing_card.get("reader_facing_manuscript_boundary_present")
        == strict_proof_boundary.get("reader_facing_manuscript_boundary_present")
        == proof.get("theorem_statement_boundary", {}).get(
            "all_required_labels_present_main_and_flat"
        )
        == proof.get("theorem_statement_boundary", {}).get(
            "conditional_theorem_boundary_present_main_and_flat"
        )
        == proof.get("manuscript_traceability", {}).get(
            "conditional_proof_claims_mapped_to_manuscript"
        )
        is True,
        "proof-writing reader-facing boundary not carried into proof_status",
    )
    checks.check(
        summary.get("proof_claim_traceability_p7_retained_nonpromotion_boundary_present")
        == proof_status.get("proof_claim_traceability_p7_retained_nonpromotion_boundary_present")
        == proof_checks.get("proof_claim_traceability_p7_retained_nonpromotion_boundary_present")
        == proof_status.get("proof_writing_boundary_p7_retained_nonpromotion_boundary_present")
        == proof_writing_card.get("p7_retained_nonpromotion_boundary_present")
        == strict_proof_boundary.get("p7_retained_nonpromotion_boundary_present")
        == proof.get("theorem_statement_boundary", {}).get(
            "does_not_promote_residual_to_error"
        )
        == proof.get("manuscript_traceability", {}).get(
            "residual_to_error_nonpromotion_present_main_and_flat"
        )
        == proof.get("p7_residual_to_error_obligation_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        is True,
        "proof-writing P7 output nonclaim/residual-to-error boundary not carried into proof_status",
    )
    checks.check(
        summary.get("proof_claim_traceability_b1_closure_scope_boundary_present")
        == proof_status.get("proof_claim_traceability_b1_closure_scope_boundary_present")
        == proof_checks.get("proof_claim_traceability_b1_closure_scope_boundary_present")
        == proof_status.get("proof_writing_boundary_b1_closure_scope_boundary_present")
        == proof_writing_card.get("b1_closure_scope_boundary_present")
        == strict_proof_boundary.get("b1_closure_scope_boundary_present")
        == proof.get("b1_ad_expanded_closure_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        is True,
        "proof-writing B1 closure-scope boundary not carried into proof_status",
    )
    checks.check(
        summary.get("proof_claim_traceability_p6_solver_scope_boundary_present")
        == proof_status.get("proof_claim_traceability_p6_solver_scope_boundary_present")
        == proof_checks.get("proof_claim_traceability_p6_solver_scope_boundary_present")
        == proof_status.get("proof_writing_boundary_p6_solver_scope_boundary_present")
        == proof_writing_card.get("p6_solver_scope_boundary_present")
        == strict_proof_boundary.get("p6_solver_scope_boundary_present")
        == proof.get("p6_solver_scope_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        is True,
        "proof-writing P6 solver-scope boundary not carried into proof_status",
    )
    checks.check(
        summary.get("proof_claim_traceability_p1p2_compact_tube_boundary_present")
        == proof_status.get("proof_claim_traceability_p1p2_compact_tube_boundary_present")
        == proof_checks.get("proof_claim_traceability_p1p2_compact_tube_boundary_present")
        == proof_status.get("proof_writing_boundary_p1p2_compact_tube_boundary_present")
        == proof_writing_card.get("p1p2_compact_tube_boundary_present")
        == proof.get("p1p2_compact_tube_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        == strict_proof_boundary.get("p1p2_compact_tube_boundary_present")
        is True,
        "proof-writing P1/P2 compact-tube boundary not carried into proof_status",
    )
    checks.check(
        summary.get("proof_claim_traceability_p3p4_implementation_boundary_present")
        == proof_status.get("proof_claim_traceability_p3p4_implementation_boundary_present")
        == proof_checks.get("proof_claim_traceability_p3p4_implementation_boundary_present")
        == proof_status.get("proof_writing_boundary_p3p4_implementation_boundary_present")
        == proof_writing_card.get("p3p4_implementation_boundary_present")
        == proof.get("p3p4_implementation_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        == strict_proof_boundary.get("p3p4_implementation_boundary_present")
        is True,
        "proof-writing P3/P4 implementation-defect boundary not carried into proof_status",
    )
    checks.check(
        summary.get("proof_claim_traceability_p5_direct_route_boundary_present")
        == proof_status.get("proof_claim_traceability_p5_direct_route_boundary_present")
        == proof_checks.get("proof_claim_traceability_p5_direct_route_boundary_present")
        == proof_status.get("proof_writing_boundary_p5_direct_route_boundary_present")
        == proof_writing_card.get("p5_direct_route_boundary_present")
        == proof.get("p5_direct_route_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        == strict_proof_boundary.get("p5_direct_route_boundary_present")
        is True,
        "proof-writing P5 direct-route boundary not carried into proof_status",
    )
    checks.check(
        summary.get("proof_claim_traceability_p_interface_satisfaction_ledger_present")
        == proof_status.get("proof_claim_traceability_p_interface_satisfaction_ledger_present")
        == proof_checks.get("proof_claim_traceability_p_interface_satisfaction_ledger_present")
        == proof_status.get("proof_writing_boundary_p_interface_satisfaction_ledger_present")
        == proof_writing_card.get("p_interface_satisfaction_ledger_present")
        == strict_proof_boundary.get("p_interface_satisfaction_ledger_present")
        == proof.get("p_interface_satisfaction_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        is True,
        "proof-writing theorem-interface satisfaction ledger not carried into proof_status",
    )
    checks.check(
        summary.get("proof_claim_traceability_p7_residual_to_error_ledger_present")
        == proof_status.get(
            "proof_claim_traceability_p7_residual_to_error_ledger_present"
        )
        == proof_checks.get(
            "proof_claim_traceability_p7_residual_to_error_ledger_present"
        )
        == proof_status.get(
            "proof_writing_boundary_p7_residual_to_error_ledger_present"
        )
        == proof_writing_card.get("p7_residual_to_error_ledger_present")
        == strict_proof_boundary.get("p7_residual_to_error_ledger_present")
        == proof.get("p7_residual_to_error_obligation_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        is True,
        "proof-writing P7 residual-to-error obligation ledger not carried into proof_status",
    )
    checks.check(
        summary.get("proof_claim_traceability_theorem_use_rule_present")
        == proof_status.get("proof_claim_traceability_theorem_use_rule_present")
        == proof_checks.get("proof_claim_traceability_theorem_use_rule_present")
        == proof_status.get("proof_writing_boundary_theorem_use_rule_present")
        == proof_writing_card.get("theorem_use_rule_present")
        == strict_proof_boundary.get("theorem_use_rule_present")
        == proof.get("theorem_use_rule_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        is True,
        "proof-writing theorem-use rule not carried into proof_status",
    )
    checks.check(
        summary.get("proof_claim_traceability_quantifier_domain_ledger_present")
        == proof_status.get(
            "proof_claim_traceability_quantifier_domain_ledger_present"
        )
        == proof_checks.get(
            "proof_claim_traceability_quantifier_domain_ledger_present"
        )
        == proof_status.get(
            "proof_writing_boundary_quantifier_domain_ledger_present"
        )
        == proof_writing_card.get("quantifier_domain_ledger_present")
        == strict_proof_boundary.get("quantifier_domain_ledger_present")
        == proof.get("quantifier_domain_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        is True,
        "proof-writing quantifier/domain ledger not carried into proof_status",
    )
    checks.check(
        summary.get("proof_claim_traceability_local_global_transfer_ledger_present")
        == proof_status.get(
            "proof_claim_traceability_local_global_transfer_ledger_present"
        )
        == proof_checks.get(
            "proof_claim_traceability_local_global_transfer_ledger_present"
        )
        == proof_status.get(
            "proof_writing_boundary_local_global_transfer_ledger_present"
        )
        == proof_writing_card.get("local_global_transfer_ledger_present")
        == strict_proof_boundary.get("local_global_transfer_ledger_present")
        == proof.get("local_global_transfer_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        is True,
        "proof-writing local-to-global transfer ledger not carried into proof_status",
    )
    checks.check(
        (
            summary.get("proof_claim_traceability_objective_completion_boundary_present")
            == proof_status.get(
                "proof_claim_traceability_objective_completion_boundary_present"
            )
            == proof_checks.get(
                "proof_claim_traceability_objective_completion_boundary_present"
            )
            == proof_status.get(
                "proof_writing_boundary_objective_completion_boundary_present"
            )
            == proof_writing_card.get("objective_completion_boundary_present")
            == strict_proof_boundary.get("objective_completion_boundary_present")
            is True
        )
        and proof.get("readiness_boundary", {}).get("proof_closure_manifest_scope")
        == "direct_pc2_closure_and_theorem_condition_traceability"
        and proof.get("readiness_boundary", {}).get(
            "global_submission_boundaries_retained"
        )
        == [
            "full_source_policy_package_ready",
            "theorem_level_eta_h_solver_policy_evidence",
            "closed_residual_to_error_theorem_for_mechanism_rows",
        ],
        "proof-writing objective-completion boundary not carried into proof_status",
    )
    checks.check(
        summary.get("proof_claim_traceability_constant_dependency_ledger_present")
        == proof_status.get(
            "proof_claim_traceability_constant_dependency_ledger_present"
        )
        == proof_checks.get(
            "proof_claim_traceability_constant_dependency_ledger_present"
        )
        == proof_status.get(
            "proof_writing_boundary_constant_dependency_ledger_present"
        )
        == proof_writing_card.get("constant_dependency_ledger_present")
        == strict_proof_boundary.get("constant_dependency_ledger_present")
        == proof.get("constant_dependency_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        is True,
        "proof-writing constant-dependency ledger not carried into proof_status",
    )
    checks.check(
        summary.get(
            "proof_claim_traceability_theorem_dependency_consumption_ledger_present"
        )
        == proof_status.get(
            "proof_claim_traceability_theorem_dependency_consumption_ledger_present"
        )
        == proof_checks.get(
            "proof_claim_traceability_theorem_dependency_consumption_ledger_present"
        )
        == proof_status.get(
            "proof_writing_boundary_theorem_dependency_consumption_ledger_present"
        )
        == proof_writing_card.get("theorem_dependency_consumption_ledger_present")
        == strict_proof_boundary.get(
            "theorem_dependency_consumption_ledger_present"
        )
        == proof.get("theorem_dependency_consumption_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        is True,
        "proof-writing theorem dependency consumption ledger not carried into proof_status",
    )
    checks.check(
        summary.get("proof_claim_traceability_branch_consistency_ledger_present")
        == proof_status.get(
            "proof_claim_traceability_branch_consistency_ledger_present"
        )
        == proof_checks.get(
            "proof_claim_traceability_branch_consistency_ledger_present"
        )
        == proof_status.get("proof_writing_boundary_branch_consistency_ledger_present")
        == proof_writing_card.get("branch_consistency_ledger_present")
        == strict_proof_boundary.get("branch_consistency_ledger_present")
        == proof.get("branch_consistency_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        is True,
        "proof-writing accepted-branch consistency ledger not carried into proof_status",
    )
    checks.check(
        summary.get(
            "proof_claim_traceability_implementation_route_oracle_ledger_present"
        )
        == proof_status.get(
            "proof_claim_traceability_implementation_route_oracle_ledger_present"
        )
        == proof_checks.get(
            "proof_claim_traceability_implementation_route_oracle_ledger_present"
        )
        == proof_status.get(
            "proof_writing_boundary_implementation_route_oracle_ledger_present"
        )
        == proof_writing_card.get("implementation_route_oracle_ledger_present")
        == strict_proof_boundary.get("implementation_route_oracle_ledger_present")
        == proof.get("implementation_route_oracle_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        is True,
        "proof-writing implementation-route/oracle separation ledger not carried into proof_status",
    )
    checks.check(
        summary.get("proof_claim_traceability_nonlinear_solver_scale_ledger_present")
        == proof_status.get(
            "proof_claim_traceability_nonlinear_solver_scale_ledger_present"
        )
        == proof_checks.get(
            "proof_claim_traceability_nonlinear_solver_scale_ledger_present"
        )
        == proof_status.get(
            "proof_writing_boundary_nonlinear_solver_scale_ledger_present"
        )
        == proof_writing_card.get("nonlinear_solver_scale_ledger_present")
        == proof.get("nonlinear_solver_scale_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        == strict_proof_boundary.get("nonlinear_solver_scale_ledger_present")
        is True,
        "proof-writing nonlinear-solver scale ledger not carried into proof_status",
    )
    checks.check(
        summary.get(
            "proof_claim_traceability_local_defect_decomposition_ledger_present"
        )
        == proof_status.get(
            "proof_claim_traceability_local_defect_decomposition_ledger_present"
        )
        == proof_checks.get(
            "proof_claim_traceability_local_defect_decomposition_ledger_present"
        )
        == proof_status.get(
            "proof_writing_boundary_local_defect_decomposition_ledger_present"
        )
        == proof_writing_card.get("local_defect_decomposition_ledger_present")
        == strict_proof_boundary.get("local_defect_decomposition_ledger_present")
        == proof.get("local_defect_decomposition_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        is True,
        "proof-writing local-defect decomposition ledger not carried into proof_status",
    )
    checks.check(
        summary.get("proof_claim_traceability_theorem_output_scope_ledger_present")
        == proof_status.get(
            "proof_claim_traceability_theorem_output_scope_ledger_present"
        )
        == proof_checks.get(
            "proof_claim_traceability_theorem_output_scope_ledger_present"
        )
        == proof_status.get(
            "proof_writing_boundary_theorem_output_scope_ledger_present"
        )
        == proof_writing_card.get("theorem_output_scope_ledger_present")
        == strict_proof_boundary.get("theorem_output_scope_ledger_present")
        == proof.get("theorem_output_scope_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        is True,
        "proof-writing theorem output scope ledger not carried into proof_status",
    )
    checks.check(
        summary.get("proof_claim_traceability_reporting_map_ledger_present")
        == proof_status.get("proof_claim_traceability_reporting_map_ledger_present")
        == proof_checks.get("proof_claim_traceability_reporting_map_ledger_present")
        == proof_status.get("proof_writing_boundary_reporting_map_ledger_present")
        == proof_writing_card.get("reporting_map_ledger_present")
        == strict_proof_boundary.get("reporting_map_ledger_present")
        == proof.get("reporting_map_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        is True,
        "proof-writing reporting-map/norm-equivalence ledger not carried into proof_status",
    )
    checks.check(
        summary.get("proof_claim_traceability_proof_causality_ledger_present")
        == proof_status.get(
            "proof_claim_traceability_proof_causality_ledger_present"
        )
        == proof_checks.get(
            "proof_claim_traceability_proof_causality_ledger_present"
        )
        == proof_status.get(
            "proof_writing_boundary_proof_causality_ledger_present"
        )
        == proof_writing_card.get("proof_causality_ledger_present")
        == strict_proof_boundary.get("proof_causality_ledger_present")
        == proof.get("proof_causality_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        is True,
        "proof-writing proof-causality ledger not carried into proof_status",
    )
    checks.check(
        summary.get(
            "proof_claim_traceability_direct_route_anticircularity_ledger_present"
        )
        == proof_status.get(
            "proof_claim_traceability_direct_route_anticircularity_ledger_present"
        )
        == proof_checks.get(
            "proof_claim_traceability_direct_route_anticircularity_ledger_present"
        )
        == proof_status.get(
            "proof_writing_boundary_direct_route_anticircularity_ledger_present"
        )
        == proof_writing_card.get("direct_route_anticircularity_ledger_present")
        == strict_proof_boundary.get("direct_route_anticircularity_ledger_present")
        == proof.get("direct_route_anticircularity_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        is True,
        "proof-writing direct-route anti-circularity ledger not carried into proof_status",
    )
    checks.check(
        proof_status.get("proof_writing_boundary_safe_reader_claim")
        == proof_writing_card.get("safe_reader_claim")
        == strict_proof_boundary.get("safe_reader_claim"),
        "proof-writing safe reader claim not carried into proof_status",
    )
    checks.check(
        proof_status.get("proof_writing_boundary_forbidden_reader_claims")
        == proof_writing_card.get("forbidden_reader_claims")
        == strict_proof_boundary.get("forbidden_reader_claims"),
        "proof-writing forbidden reader claims not carried into proof_status",
    )
    checks.check(
        proof_status.get("proof_writing_boundary_global_boundaries_retained")
        == proof_writing_card.get("global_submission_boundaries_retained")
        == strict_proof_boundary.get("proof_global_boundaries_retained"),
        "proof-writing global boundaries not carried into proof_status",
    )
    checks.check(
        "Strict proof-writing submission boundary: `proof_writing_traceable_global_submission_blocked_by_source_policy_tfe_package`; card `conditional_theorem_traceable_direct_pc2_closed_global_boundaries_retained`; package boundary `narrowed_repro_ready_full_source_policy_package_blocked`; blockers `['OC4', 'OC6', 'OC12']`; submission ready `False`."
        in manifest_md,
        "manifest markdown missing strict proof-writing submission/package boundary",
    )
    checks.check(
        "Strict proof-writing safe/forbidden claims: safe `conditional order-six theorem under retained P1, P2, and P3 theorem interfaces, the separate P6 solver-scale interface, and the P4 binding convention, with P4's proved 96-row non-dynamic row-local certificate and P5's direct Newton-Euler rows supplying one same-branch 132-row residual bridge; route-exclusivity forbids mixing direct and primitive/Taylor residual certificates to lower constants, remove P6, or prove a P7 residual-to-error transfer theorem; the theorem statement itself consumes only one residual-value certificate, so a future primitive/Taylor certificate may only replace the accepted direct certificate by proving a new same-tuple 132-row residual-value bound; P7 remains a separate output nonclaim/residual-to-error boundary`"
        in manifest_md,
        "manifest markdown missing strict proof-writing safe reader claim",
    )
    checks.check(
        "Strict proof-writing no-promotion locks: residual-to-error `True`; source-policy/full-TFE package `True`."
        in manifest_md,
        "manifest markdown missing strict proof-writing no-promotion locks",
    )
    checks.check(
        "Strict proof-writing reader-facing manuscript/PDF boundary: `True`." in manifest_md,
        "manifest markdown missing strict proof-writing reader-facing boundary",
    )
    checks.check(
        "Strict proof-writing P7 output nonclaim/residual-to-error boundary: `True`." in manifest_md
        and "Proof-claim P7 output nonclaim/residual-to-error boundary: `True`." in manifest_md,
        "manifest markdown missing P7 output nonclaim/residual-to-error boundary",
    )
    checks.check(
        "Strict proof-writing P7 residual-to-error obligation ledger: `True`."
        in manifest_md
        and "Proof-claim P7 residual-to-error obligation ledger: `True`."
        in manifest_md,
        "manifest markdown missing P7 residual-to-error obligation ledger",
    )
    checks.check(
        "Strict proof-writing theorem-use rule: `True`." in manifest_md
        and "Proof-claim theorem-use rule: `True`." in manifest_md,
        "manifest markdown missing theorem-use rule",
    )
    checks.check(
        "Strict proof-writing quantifier/domain ledger: `True`." in manifest_md
        and "Proof-claim quantifier/domain ledger: `True`." in manifest_md,
        "manifest markdown missing quantifier/domain ledger",
    )
    checks.check(
        "Strict proof-writing local-to-global transfer ledger: `True`." in manifest_md
        and "Proof-claim local-to-global transfer ledger: `True`." in manifest_md,
        "manifest markdown missing local-to-global transfer ledger",
    )
    checks.check(
        "Strict proof-writing objective-completion boundary: `True`." in manifest_md
        and "Proof-claim objective-completion boundary: `True`." in manifest_md,
        "manifest markdown missing objective-completion boundary",
    )
    checks.check(
        "Strict proof-writing constant-dependency ledger: `True`." in manifest_md
        and "Proof-claim constant-dependency ledger: `True`." in manifest_md,
        "manifest markdown missing constant-dependency ledger",
    )
    checks.check(
        "Strict proof-writing theorem dependency consumption ledger: `True`." in manifest_md
        and "Proof-claim theorem dependency consumption ledger: `True`." in manifest_md,
        "manifest markdown missing theorem dependency consumption ledger",
    )
    checks.check(
        "Strict proof-writing accepted-branch consistency ledger: `True`."
        in manifest_md
        and "Proof-claim accepted-branch consistency ledger: `True`." in manifest_md,
        "manifest markdown missing accepted-branch consistency ledger",
    )
    checks.check(
        "Strict proof-writing implementation-route/oracle separation ledger: `True`."
        in manifest_md
        and "Proof-claim implementation-route/oracle separation ledger: `True`."
        in manifest_md,
        "manifest markdown missing implementation-route/oracle separation ledger",
    )
    checks.check(
        "Strict proof-writing nonlinear-solver scale ledger: `True`."
        in manifest_md
        and "Proof-claim nonlinear-solver scale ledger: `True`." in manifest_md,
        "manifest markdown missing nonlinear-solver scale ledger",
    )
    checks.check(
        "Strict proof-writing local-defect decomposition ledger: `True`." in manifest_md
        and "Proof-claim local-defect decomposition ledger: `True`." in manifest_md,
        "manifest markdown missing local-defect decomposition ledger",
    )
    checks.check(
        "Strict proof-writing theorem output scope ledger: `True`." in manifest_md
        and "Proof-claim theorem output scope ledger: `True`." in manifest_md,
        "manifest markdown missing theorem output scope ledger",
    )
    checks.check(
        "Strict proof-writing reporting-map/norm-equivalence ledger: `True`."
        in manifest_md
        and "Proof-claim reporting-map/norm-equivalence ledger: `True`."
        in manifest_md,
        "manifest markdown missing reporting-map/norm-equivalence ledger",
    )
    checks.check(
        "Strict proof-writing proof-causality ledger: `True`." in manifest_md
        and "Proof-claim proof-causality ledger: `True`." in manifest_md,
        "manifest markdown missing proof-causality ledger",
    )
    checks.check(
        "Strict proof-writing B1 closure-scope boundary: `True`." in manifest_md
        and "Proof-claim B1 closure-scope boundary: `True`." in manifest_md,
        "manifest markdown missing B1 closure-scope boundary",
    )
    checks.check(
        "Strict proof-writing B1 AD-expanded closure ledger/cells: `True` / `4752`."
        in manifest_md,
        "manifest markdown missing B1 AD-expanded closure ledger",
    )
    checks.check(
        "Strict proof-writing P6 solver-scope boundary: `True`." in manifest_md
        and "Proof-claim P6 solver-scope boundary: `True`." in manifest_md,
        "manifest markdown missing P6 solver-scope boundary",
    )
    checks.check(
        "Strict proof-writing P1/P2 compact-tube boundary: `True`." in manifest_md
        and "Proof-claim P1/P2 compact-tube boundary: `True`." in manifest_md,
        "manifest markdown missing P1/P2 compact-tube boundary",
    )
    checks.check(
        "Strict proof-writing P3/P4 implementation-defect boundary: `True`." in manifest_md
        and "Proof-claim P3/P4 implementation-defect boundary: `True`." in manifest_md,
        "manifest markdown missing P3/P4 implementation-defect boundary",
    )
    checks.check(
        "Strict proof-writing P5 direct-route boundary: `True`." in manifest_md
        and "Proof-claim P5 direct-route boundary: `True`." in manifest_md,
        "manifest markdown missing P5 direct-route boundary",
    )
    checks.check(
        "Strict proof-writing direct-route anti-circularity ledger: `True`."
        in manifest_md
        and "Proof-claim direct-route anti-circularity ledger: `True`."
        in manifest_md,
        "manifest markdown missing direct-route anti-circularity ledger",
    )
    checks.check(
        "Strict proof-writing theorem-interface satisfaction ledger: `True`." in manifest_md
        and "Proof-claim theorem-interface satisfaction ledger: `True`." in manifest_md,
        "manifest markdown missing theorem-interface satisfaction ledger",
    )
    proof_claim_anchor_map = proof_claim_traceability.get("manuscript_anchor_map", {})
    checks.check(
        summary.get("proof_claim_traceability_manuscript_anchor_map_present")
        == proof_status.get("proof_claim_traceability_manuscript_anchor_map_present")
        == proof_checks.get("proof_claim_traceability_manuscript_anchor_map_present")
        == proof_claim_anchor_map.get("all_label_anchors_present")
        is True,
        "proof-claim manuscript anchor map not carried into package manifest",
    )
    checks.check(
        summary.get("proof_claim_traceability_manuscript_anchor_label_count")
        == proof_status.get("proof_claim_traceability_manuscript_anchor_label_count")
        == proof_checks.get("proof_claim_traceability_manuscript_anchor_label_count")
        == proof_claim_anchor_map.get("label_anchor_count")
        == 24,
        "proof-claim manuscript anchor label count not carried into package manifest",
    )
    checks.check(
        summary.get("proof_claim_traceability_theorem_assumption_anchor_map_present")
        == proof_status.get("proof_claim_traceability_theorem_assumption_anchor_map_present")
        == proof_checks.get("proof_claim_traceability_theorem_assumption_anchor_map_present")
        == proof_claim_anchor_map.get("all_theorem_assumption_anchors_present")
        is True,
        "proof-claim theorem-assumption anchor map not carried into package manifest",
    )
    checks.check(
        summary.get("proof_claim_traceability_theorem_assumption_anchor_count")
        == proof_status.get("proof_claim_traceability_theorem_assumption_anchor_count")
        == proof_checks.get("proof_claim_traceability_theorem_assumption_anchor_count")
        == proof_claim_anchor_map.get("theorem_assumption_anchor_count")
        == 7,
        "proof-claim theorem-assumption anchor count not carried into package manifest",
    )
    checks.check(
        summary.get("proof_claim_traceability_theorem_assumption_anchor_ids")
        == proof_status.get("proof_claim_traceability_theorem_assumption_anchor_ids")
        == proof_checks.get("proof_claim_traceability_theorem_assumption_anchor_ids")
        == proof_claim_anchor_map.get("theorem_assumption_anchor_ids")
        == ["P1", "P2", "P3", "P4", "P5", "P6", "P7"],
        "proof-claim theorem-assumption anchor IDs not carried into package manifest",
    )
    proof_closure_anchor_map = proof.get("manuscript_anchor_map", {})
    checks.check(
        summary.get("proof_closure_manuscript_anchor_map_present")
        == proof_status.get("proof_closure_manuscript_anchor_map_present")
        == proof_checks.get("proof_closure_manuscript_anchor_map_present")
        == proof_closure_anchor_map.get("all_label_anchors_present")
        is True,
        "proof-closure manuscript anchor map not carried into package manifest",
    )
    checks.check(
        summary.get("proof_closure_manuscript_anchor_label_count")
        == proof_status.get("proof_closure_manuscript_anchor_label_count")
        == proof_checks.get("proof_closure_manuscript_anchor_label_count")
        == proof_closure_anchor_map.get("label_anchor_count")
        == 24,
        "proof-closure manuscript anchor label count not carried into package manifest",
    )
    checks.check(
        summary.get("proof_closure_theorem_assumption_anchor_map_present")
        == proof_status.get("proof_closure_theorem_assumption_anchor_map_present")
        == proof_checks.get("proof_closure_theorem_assumption_anchor_map_present")
        == proof_closure_anchor_map.get("all_theorem_assumption_anchors_present")
        is True,
        "proof-closure theorem-assumption anchor map not carried into package manifest",
    )
    checks.check(
        summary.get("proof_closure_theorem_assumption_anchor_count")
        == proof_status.get("proof_closure_theorem_assumption_anchor_count")
        == proof_checks.get("proof_closure_theorem_assumption_anchor_count")
        == proof_closure_anchor_map.get("theorem_assumption_anchor_count")
        == 7,
        "proof-closure theorem-assumption anchor count not carried into package manifest",
    )
    checks.check(
        summary.get("proof_closure_theorem_assumption_anchor_ids")
        == proof_status.get("proof_closure_theorem_assumption_anchor_ids")
        == proof_checks.get("proof_closure_theorem_assumption_anchor_ids")
        == proof_closure_anchor_map.get("theorem_assumption_anchor_ids")
        == ["P1", "P2", "P3", "P4", "P5", "P6", "P7"],
        "proof-closure theorem-assumption anchor IDs not carried into package manifest",
    )
    checks.check(
        summary.get("proof_closure_proof_claim_anchor_maps_match")
        == proof_status.get("proof_closure_proof_claim_anchor_maps_match")
        == proof_checks.get("proof_closure_proof_claim_anchor_maps_match")
        is True
        and proof_closure_anchor_map == proof_claim_anchor_map,
        "proof-closure/proof-claim manuscript anchor maps diverged in package manifest",
    )
    checks.check(
        summary.get("proof_contract_anchor_evidence_sources")
        == proof_status.get("proof_contract_anchor_evidence_sources")
        == proof_checks.get("proof_contract_anchor_evidence_sources")
        == expected_anchor_evidence_sources,
        "proof-contract anchor evidence sources not carried into package manifest",
    )
    checks.check(
        summary.get("proof_style_anchor_evidence_sources")
        == proof_status.get("proof_style_anchor_evidence_sources")
        == proof_checks.get("proof_style_anchor_evidence_sources")
        == expected_anchor_evidence_sources,
        "proof-style anchor evidence sources not carried into package manifest",
    )
    checks.check(
        summary.get("strict_proof_anchor_evidence_sources")
        == proof_status.get("strict_proof_anchor_evidence_sources")
        == proof_checks.get("strict_proof_anchor_evidence_sources")
        == expected_anchor_evidence_sources,
        "strict-proof anchor evidence sources not carried into package manifest",
    )
    checks.check(
        summary.get("proof_anchor_evidence_sources_match")
        == proof_status.get("proof_anchor_evidence_sources_match")
        == proof_checks.get("proof_anchor_evidence_sources_match")
        is True,
        "package manifest does not enforce proof-contract/style/strict anchor-source agreement",
    )
    checks.check(
        "Proof-claim remaining theorem-boundary partition: `theorem_conditions_retained_not_submission_ready`; satisfied IDs `P5`; retained theorem-interface IDs `P1,P2,P3,P4,P6`; open output-boundary IDs `P7`; global boundaries `full_source_policy_package_ready,theorem_level_eta_h_solver_policy_evidence,closed_residual_to_error_theorem_for_mechanism_rows`."
        in manifest_md,
        "manifest markdown missing proof-claim remaining theorem-boundary partition summary",
    )
    checks.check(
        "Proof-claim manuscript anchor map: `True`; label anchors `24`; theorem-interface/P7-output-boundary anchors `7`; IDs `P1,P2,P3,P4,P5,P6,P7`."
        in manifest_md,
        "manifest markdown missing proof-claim manuscript anchor map summary",
    )
    checks.check(
        "Proof-closure manuscript anchor map: `True`; label anchors `24`; theorem-interface/P7-output-boundary anchors `7`; IDs `P1,P2,P3,P4,P5,P6,P7`; proof-claim map match `True`."
        in manifest_md,
        "manifest markdown missing proof-closure manuscript anchor map summary",
    )
    checks.check(
        "Reader-facing theorem-interface split: theorem interfaces `P1--P6`; P7 is an output nonclaim/residual-to-error boundary anchor, not a theorem premise."
        in manifest_md,
        "manifest markdown missing reader-facing P1-P6/P7 split",
    )
    checks.check(
        "Proof anchor evidence sources: contract `PROOF_CLOSURE_MANIFEST.json,PROOF_CLAIM_TRACEABILITY_AUDIT.json`; style `PROOF_CLOSURE_MANIFEST.json,PROOF_CLAIM_TRACEABILITY_AUDIT.json`; strict `PROOF_CLOSURE_MANIFEST.json,PROOF_CLAIM_TRACEABILITY_AUDIT.json`; source match `True`."
        in manifest_md,
        "manifest markdown missing proof anchor evidence source summary",
    )
    checks.check(
        proof_status.get("symbolic_primitive_route_open_dynamic_rows")
        == proof_status.get("open_dynamic_rows")
        == 36
        and proof_status.get("open_dynamic_rows_scope")
        == "symbolic_primitive_certificate_route_not_active_direct_pc2",
        "open dynamic row count must be scoped to primitive route",
    )
    checks.check(proof_status.get("certified_non_dynamic_rows") == 96, "certified non-dynamic row count changed")
    checks.check(
        proof_status.get("newton_euler_obligation_coverage_matrix_complete")
        == proof.get("evidence_summary", {}).get("newton_euler_obligation_coverage_matrix_complete")
        is True,
        "proof-status Newton-Euler obligation coverage matrix stale",
    )
    checks.check(
        proof_status.get("newton_euler_row_obligation_links")
        == proof.get("evidence_summary", {}).get("newton_euler_row_obligation_links")
        == 180,
        "proof-status row-obligation link count changed",
    )
    checks.check(
        proof_status.get("newton_euler_rows_with_complete_obligation_sets")
        == proof.get("evidence_summary", {}).get("newton_euler_rows_with_complete_obligation_sets")
        == 36,
        "proof-status complete-row obligation count changed",
    )

    checks.check(manifest.get("candidate_file_count") == len(files), "candidate file count stale")
    checks.check(manifest.get("candidate_existing_file_count") == len(files), "candidate existing file count stale")
    checks.check(manifest.get("candidate_missing_existing_files") == [], "candidate file unexpectedly missing")
    for item in files:
        path_label = item.get("path")
        path = resolve_package_path(str(path_label))
        checks.check(path.exists() and path.stat().st_size > 0, f"candidate file missing: {path_label}")
        checks.check(item.get("exists") is True, f"candidate existence flag false: {path_label}")
    open_provenance_statuses = {
        "needs_extraction",
        "needs_source_policy_promotion",
        "b4_b7_open_plan_ready",
        "ready_for_user_opt_in_not_run",
        "full_t10_absolute_dae_lift_candidate_not_source_policy",
        "attempted_not_reproducible_not_promoted",
        "endpoint_policy_boundary_certificate_not_source_policy",
        "post_execution_attempts_recorded_rows_not_promoted_full_source_policy_open",
        "targeted_repair_attempted_not_reproducible_not_promoted",
        "row_provenance_preflight_complete_not_promotion",
    }
    tfe_full_t10_paths = {
        "TFE_FULL_T10_ABSOLUTE_DAE_LIFT_SUMMARY.json",
        "TFE_FULL_T10_ABSOLUTE_DAE_LIFT_SUMMARY.md",
        "TFE_FULL_T10_ABSOLUTE_DAE_LIFT_SUMMARY.csv",
        "build_tfe_full_t10_absolute_dae_lift_summary.py",
        "validate_tfe_full_t10_absolute_dae_lift_summary.py",
    }
    file_by_path = {item.get("path"): item for item in files}
    b4_post_execution_paths = {
        "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.json",
        "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.md",
    }
    checks.check(
        b4_post_execution_paths.issubset(set(file_by_path)),
        "B4 post-execution audit files missing from candidate set",
    )
    for path_label in b4_post_execution_paths:
        item = file_by_path.get(path_label, {})
        checks.check(
            item.get("status") == expected_b4_post_execution_file_status,
            f"B4 post-execution audit file status stale: {path_label}",
        )
        checks.check(
            item.get("include_in_minimal_submission_package") is True,
            f"B4 post-execution audit file should remain in the manifest candidate set: {path_label}",
        )
    if authorized_b4:
        manifest_blob = json.dumps(manifest, sort_keys=True)
        checks.check(
            legacy_b4_post_execution_file_status not in manifest_blob
            and legacy_b4_post_execution_file_status not in manifest_md,
            "manifest has legacy B4 no-verified-authorized-execution file status",
        )
    checks.check(
        tfe_full_t10_paths.issubset(set(file_by_path)),
        "TFE full-T10 absolute DAE-lift package files missing from candidate set",
    )
    for path_label in tfe_full_t10_paths:
        item = file_by_path.get(path_label, {})
        checks.check(
            item.get("status") == "full_t10_absolute_dae_lift_candidate_not_source_policy",
            f"TFE full-T10 absolute DAE-lift status changed: {path_label}",
        )
        checks.check(
            item.get("include_in_minimal_submission_package") is False,
            f"TFE full-T10 absolute DAE-lift row should not be minimal: {path_label}",
        )
    full_source_policy_row_provenance_paths = {
        "FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.json",
        "FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.md",
        "FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.csv",
        "build_full_source_policy_row_provenance_audit.py",
        "validate_full_source_policy_row_provenance_audit.py",
    }
    checks.check(
        full_source_policy_row_provenance_paths.issubset(set(file_by_path)),
        "full source-policy row provenance package files missing from candidate set",
    )
    for path_label in full_source_policy_row_provenance_paths:
        item = file_by_path.get(path_label, {})
        checks.check(
            item.get("status") == "row_provenance_preflight_complete_not_promotion",
            f"full source-policy row provenance status changed: {path_label}",
        )
        checks.check(
            item.get("include_in_minimal_submission_package") is False,
            f"full source-policy row provenance file should not be minimal: {path_label}",
        )
    tfe_self_reproduction_attempt_paths = {
        "TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.json",
        "TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.md",
    }
    checks.check(
        tfe_self_reproduction_attempt_paths.issubset(set(file_by_path)),
        "TFE self-reproduction attempt certificate files missing from candidate set",
    )
    for path_label in tfe_self_reproduction_attempt_paths:
        item = file_by_path.get(path_label, {})
        checks.check(
            item.get("status") == "attempted_not_reproducible_not_promoted",
            f"TFE self-reproduction attempt certificate status changed: {path_label}",
        )
        checks.check(
            item.get("include_in_minimal_submission_package") is False,
            f"TFE self-reproduction attempt certificate should not be minimal: {path_label}",
        )
    ra_hi_post_execution_attempt_paths = {
        "RA_HI_SOURCE_POLICY_POST_EXECUTION_ATTEMPT_CERTIFICATE.json",
        "RA_HI_SOURCE_POLICY_POST_EXECUTION_ATTEMPT_CERTIFICATE.md",
    }
    checks.check(
        ra_hi_post_execution_attempt_paths.issubset(set(file_by_path)),
        "RA/HI post-execution attempt certificate files missing from candidate set",
    )
    for path_label in ra_hi_post_execution_attempt_paths:
        item = file_by_path.get(path_label, {})
        checks.check(
            item.get("status")
            == "post_execution_attempts_recorded_rows_not_promoted_full_source_policy_open",
            f"RA/HI post-execution attempt certificate status changed: {path_label}",
        )
        checks.check(
            item.get("include_in_minimal_submission_package") is False,
            f"RA/HI post-execution attempt certificate should not be minimal: {path_label}",
        )
    ra_hi_closeout_paths = {
        "RA_HI_SOURCE_POLICY_CLOSEOUT_CHECKLIST.json",
        "RA_HI_SOURCE_POLICY_CLOSEOUT_CHECKLIST.md",
    }
    checks.check(
        ra_hi_closeout_paths.issubset(set(file_by_path)),
        "RA/HI source-policy closeout checklist files missing from candidate set",
    )
    for path_label in ra_hi_closeout_paths:
        item = file_by_path.get(path_label, {})
        checks.check(
            item.get("status") == "ready_for_authorized_execution_closeout_not_executed_not_promoted",
            f"RA/HI source-policy closeout checklist status changed: {path_label}",
        )
        checks.check(
            item.get("include_in_minimal_submission_package") is False,
            f"RA/HI source-policy closeout checklist should not be minimal: {path_label}",
        )
    ra_hi_output_inventory_paths = {
        "RA_HI_SOURCE_POLICY_OUTPUT_INVENTORY.json",
        "RA_HI_SOURCE_POLICY_OUTPUT_INVENTORY.md",
    }
    checks.check(
        ra_hi_output_inventory_paths.issubset(set(file_by_path)),
        "RA/HI source-policy output inventory files missing from candidate set",
    )
    for path_label in ra_hi_output_inventory_paths:
        item = file_by_path.get(path_label, {})
        checks.check(
            item.get("status") == "existing_expected_outputs_present_not_promotion_evidence",
            f"RA/HI source-policy output inventory status changed: {path_label}",
        )
        checks.check(
            item.get("include_in_minimal_submission_package") is False,
            f"RA/HI source-policy output inventory should not be minimal: {path_label}",
        )
    ra_hi_promotion_blocker_paths = {
        "RA_HI_SOURCE_POLICY_PROMOTION_BLOCKER_MATRIX.json",
        "RA_HI_SOURCE_POLICY_PROMOTION_BLOCKER_MATRIX.md",
    }
    checks.check(
        ra_hi_promotion_blocker_paths.issubset(set(file_by_path)),
        "RA/HI source-policy promotion blocker matrix files missing from candidate set",
    )
    for path_label in ra_hi_promotion_blocker_paths:
        item = file_by_path.get(path_label, {})
        checks.check(
            item.get("status") == "ra_hi_public_root_rows_not_promoted_source_policy_open",
            f"RA/HI source-policy promotion blocker matrix status changed: {path_label}",
        )
        checks.check(
            item.get("include_in_minimal_submission_package") is False,
            f"RA/HI source-policy promotion blocker matrix should not be minimal: {path_label}",
        )
    hi2022_ra_half_double_repair_paths = {
        "HI2022_RA_HALF_DOUBLE_REPAIR_ATTEMPT_CERTIFICATE.json",
        "HI2022_RA_HALF_DOUBLE_REPAIR_ATTEMPT_CERTIFICATE.md",
    }
    checks.check(
        hi2022_ra_half_double_repair_paths.issubset(set(file_by_path)),
        "HI2022 rA_half double repair-attempt certificate files missing from candidate set",
    )
    for path_label in hi2022_ra_half_double_repair_paths:
        item = file_by_path.get(path_label, {})
        checks.check(
            item.get("status") == "targeted_repair_attempted_not_reproducible_not_promoted",
            f"HI2022 repair-attempt certificate status changed: {path_label}",
        )
        checks.check(
            item.get("include_in_minimal_submission_package") is False,
            f"HI2022 repair-attempt certificate should not be minimal: {path_label}",
        )
    tfe_endpoint_boundary_paths = {
        "TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.json",
        "TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.md",
        "TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.csv",
        "build_tfe_endpoint_policy_boundary_certificate.py",
        "validate_tfe_endpoint_policy_boundary_certificate.py",
    }
    checks.check(
        tfe_endpoint_boundary_paths.issubset(set(file_by_path)),
        "TFE endpoint boundary certificate package files missing from candidate set",
    )
    for path_label in tfe_endpoint_boundary_paths:
        item = file_by_path.get(path_label, {})
        checks.check(
            item.get("status") == "endpoint_policy_boundary_certificate_not_source_policy",
            f"TFE endpoint boundary certificate status changed: {path_label}",
        )
        checks.check(
            item.get("include_in_minimal_submission_package") is False,
            f"TFE endpoint boundary certificate row should not be minimal: {path_label}",
        )
    for item in files:
        if item.get("status") in open_provenance_statuses:
            checks.check(
                item.get("include_in_minimal_submission_package") is False,
                f"open/provenance row should not be minimal: {item.get('path')}",
            )

    missing_ids = {item.get("id") for item in missing_components}
    checks.check(
        {
            "tfe_original_pendulum_source_policy_runner",
            "ra2021_same_policy_local_dynamic_rows",
            "hi2022_full_T8_policy_rows",
            "source_policy_work_precision_execution_plan",
            "newton_euler_symbolic_defect_certificate",
            "full_source_policy_runner_archive",
        }.issubset(missing_ids),
        "missing component set incomplete",
    )
    runner_archive_component = {
        item.get("id"): item for item in missing_components
    }.get("full_source_policy_runner_archive", {})
    checks.check(
        runner_archive_component.get("status") == "partial_local_runner_package_ready_source_policy_open",
        "full source-policy runner archive status changed",
    )
    layer_statuses = {item.get("id"): item.get("status") for item in manifest.get("package_layers", [])}
    checks.check(
        layer_statuses.get("L0") == "artifact_present_not_global_submission_ready",
        "L0 status changed",
    )
    checks.check(
        layer_statuses.get("L1") == "common_reference_artifact_present_source_policy_open",
        "L1 status changed",
    )
    checks.check(
        layer_statuses.get("L2") == "narrowed_repro_bundle_ready_replay_plus_local_runners_source_policy_open",
        "L2 status changed",
    )
    checks.check(layer_statuses.get("L3") == "open", "L3 status changed")
    checks.check(layer_statuses.get("L4") == "open", "L4 status changed")
    layer_evidence = {
        item.get("id"): item.get("evidence", [])
        for item in manifest.get("package_layers", [])
    }
    layer_names = {item.get("id"): item.get("name") for item in manifest.get("package_layers", [])}
    checks.check(
        layer_names.get("L2") == "narrowed reproducibility bundle for paper evidence",
        "L2 name should distinguish the narrowed bundle from the minimal replay package",
    )
    checks.check(
        "TFE_SOURCE_PENDULUM_MODEL_AUDIT.json" in layer_evidence.get("L3", []),
        "TFE source pendulum model audit missing from L3 evidence",
    )
    checks.check(
        "TFE_BROWN_MCPHEE_SOURCE_LAW_BOUNDARY_AUDIT.json" in layer_evidence.get("L3", []),
        "TFE Brown-McPhee boundary audit missing from L3 evidence",
    )
    checks.check(
        "TFE_BROWN_MCPHEE_SOURCE_CODE_EQUIVALENCE_CERTIFICATE.json" in layer_evidence.get("L3", []),
        "TFE Brown-McPhee source-code equivalence certificate missing from L3 evidence",
    )
    checks.check(
        "TFE_FULL_T10_ABSOLUTE_DAE_LIFT_SUMMARY.json" in layer_evidence.get("L3", []),
        "TFE full-T10 absolute DAE-lift summary missing from L3 evidence",
    )
    checks.check(
        "TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.json"
        in layer_evidence.get("L3", []),
        "TFE self-reproduction attempt certificate missing from L3 evidence",
    )
    checks.check(
        "TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.json" in layer_evidence.get("L3", []),
        "TFE endpoint policy boundary certificate missing from L3 evidence",
    )
    checks.check(
        "TFE_FULL_T10_ENDPOINT_POLICY_CLOSURE_CERTIFICATE.json" in layer_evidence.get("L3", []),
        "TFE full-T10 endpoint policy closure certificate missing from L3 evidence",
    )
    checks.check(
        "B4_SOURCE_POLICY_WORK_PRECISION_EXECUTION_PLAN.json" in layer_evidence.get("L3", []),
        "B4 source-policy work/precision plan missing from L3 evidence",
    )
    checks.check(
        "B4_EXISTING_ARTIFACT_PROMOTION_AUDIT.json" in layer_evidence.get("L3", []),
        "B4 existing-artifact promotion audit missing from L3 evidence",
    )
    checks.check(
        "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.json" in layer_evidence.get("L3", []),
        "B4 source-policy post-execution audit missing from L3 evidence",
    )
    checks.check(
        "FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.json" in layer_evidence.get("L3", []),
        "full source-policy row provenance audit missing from L3 evidence",
    )
    checks.check(
        "RA_HI_SOURCE_POLICY_POST_EXECUTION_ATTEMPT_CERTIFICATE.json"
        in layer_evidence.get("L3", []),
        "RA/HI post-execution attempt certificate missing from L3 evidence",
    )
    checks.check(
        "RA_HI_SOURCE_POLICY_CLOSEOUT_CHECKLIST.json" in layer_evidence.get("L3", []),
        "RA/HI source-policy closeout checklist missing from L3 evidence",
    )
    checks.check(
        "RA_HI_SOURCE_POLICY_OUTPUT_INVENTORY.json" in layer_evidence.get("L3", []),
        "RA/HI source-policy output inventory missing from L3 evidence",
    )
    checks.check(
        "RA_HI_SOURCE_POLICY_PROMOTION_BLOCKER_MATRIX.json" in layer_evidence.get("L3", []),
        "RA/HI source-policy promotion blocker matrix missing from L3 evidence",
    )
    checks.check(
        "RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.json" in layer_evidence.get("L3", []),
        "RA2021 double low-order diagnosis missing from L3 evidence",
    )
    checks.check(
        "HI2022_RA_HALF_DOUBLE_SOURCE_POLICY_FAILURE_DIAGNOSIS.json" in layer_evidence.get("L3", []),
        "HI2022 rA_half double failure diagnosis missing from L3 evidence",
    )
    checks.check(
        "HI2022_RA_HALF_DOUBLE_REPAIR_ATTEMPT_CERTIFICATE.json" in layer_evidence.get("L3", []),
        "HI2022 rA_half double repair-attempt certificate missing from L3 evidence",
    )
    checks.check(
        "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.json" in layer_evidence.get("L3", []),
        "B4 source-policy row closure-readiness ledger missing from L3 evidence",
    )
    checks.check(
        "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json" in layer_evidence.get("L3", []),
        "B4 source-policy execution opt-in packet missing from L3 evidence",
    )
    checks.check(
        "CMAME_NARROWED_REPRODUCIBILITY_PACKAGE_AUDIT.json" in layer_evidence.get("L2", []),
        "narrowed reproducibility package audit missing from L2 evidence",
    )
    checks.check(
        "cmame_narrowed_repro_bundle/MANIFEST.json" in layer_evidence.get("L2", []),
        "narrowed reproducibility bundle manifest missing from L2 evidence",
    )
    checks.check(
        "cmame_narrowed_repro_bundle/scripts/run_narrowed_repro_bundle.py" in layer_evidence.get("L2", []),
        "narrowed reproducibility bundle launcher missing from L2 evidence",
    )
    checks.check(
        "cmame_narrowed_repro_bundle/results/narrowed_repro_bundle_summary.json" in layer_evidence.get("L2", []),
        "narrowed reproducibility bundle summary missing from L2 evidence",
    )
    checks.check(
        "CMAME_MINIMAL_REPRODUCIBILITY_CANDIDATE_MANIFEST.json" in layer_evidence.get("L2", []),
        "minimal reproducibility candidate missing from L2 evidence",
    )
    checks.check(
        "run_human_reproducibility.py" in layer_evidence.get("L2", []),
        "human-facing replay entrypoint missing from L2 evidence",
    )
    checks.check(
        "human_reproducibility_result_table.md" in layer_evidence.get("L2", []),
        "human-facing replay result table missing from L2 evidence",
    )
    checks.check(
        "run_b6_four_example_local_evidence.py" in layer_evidence.get("L2", []),
        "B6 four-example local-evidence runner missing from L2 evidence",
    )
    checks.check(
        "B6_FOUR_EXAMPLE_LOCAL_EVIDENCE_SUMMARY.json" in layer_evidence.get("L2", []),
        "B6 four-example local-evidence summary missing from L2 evidence",
    )
    checks.check(
        "validate_b6_four_example_local_evidence.py" in layer_evidence.get("L2", []),
        "B6 four-example local-evidence validator missing from L2 evidence",
    )
    checks.check(
        "B6_CLOSED_LOOP_SELF_CONTAINED_EXTRACTION_AUDIT.json" in layer_evidence.get("L2", []),
        "B6 closed-loop extraction audit missing from L2 evidence",
    )
    checks.check(
        "validate_b6_closed_loop_self_contained_extraction_audit.py" in layer_evidence.get("L2", []),
        "B6 closed-loop extraction audit validator missing from L2 evidence",
    )
    checks.check(
        "CMAME_CLOSED_LOOP_LOCAL_RUNNER_CANDIDATE_MANIFEST.json" in layer_evidence.get("L2", []),
        "closed-loop local runner candidate manifest missing from L2 evidence",
    )
    checks.check(
        "validate_cmame_closed_loop_local_runner_candidate.py" in layer_evidence.get("L2", []),
        "closed-loop local runner candidate validator missing from L2 evidence",
    )
    checks.check(
        "cmame_closed_loop_local_runner_candidate/scripts/run_closed_loop_fullva_candidate.py"
        in layer_evidence.get("L2", []),
        "closed-loop local runner candidate script missing from L2 evidence",
    )
    checks.check(
        "cmame_closed_loop_local_runner_candidate/results/closed_loop_local_summary.json"
        in layer_evidence.get("L2", []),
        "closed-loop local runner candidate summary missing from L2 evidence",
    )
    checks.check(
        "cmame_p1_single_runner_candidate/scripts/run_single_pendulum_fullva.py" in layer_evidence.get("L2", []),
        "P1 single-runner script missing from L2 evidence",
    )
    checks.check(
        "cmame_p1_single_runner_candidate/results/single_pendulum_summary.json" in layer_evidence.get("L2", []),
        "P1 single-runner summary missing from L2 evidence",
    )
    checks.check(
        "cmame_p1_double_runner_candidate/scripts/run_double_pendulum_fullva.py" in layer_evidence.get("L2", []),
        "P1 double-runner script missing from L2 evidence",
    )
    checks.check(
        "cmame_p1_double_runner_candidate/results/double_pendulum_summary.json" in layer_evidence.get("L2", []),
        "P1 double-runner summary missing from L2 evidence",
    )
    checks.check(
        "CMAME_LOCAL_ACCEPTED_RUNNER_COMPANION_MANIFEST.json" in layer_evidence.get("L2", []),
        "local accepted-row runner companion manifest missing from L2 evidence",
    )
    checks.check(
        "cmame_local_accepted_runner_companion/scripts/run_local_accepted_runner_companion.py"
        in layer_evidence.get("L2", []),
        "local accepted-row runner companion launcher missing from L2 evidence",
    )
    checks.check(
        minimal_candidate.get("schema")
        == minimal_candidate_source.get("schema")
        == "cmame-minimal-reproducibility-candidate-v1",
        "minimal candidate schema stale in package manifest",
    )
    checks.check(
        minimal_candidate.get("status")
        == minimal_candidate_source.get("status")
        == "candidate_replay_package_built_not_submission_ready",
        "minimal candidate status stale in package manifest",
    )
    checks.check(minimal_candidate.get("submission_ready") is False, "minimal candidate overclaims submission ready")
    checks.check(minimal_candidate.get("candidate_file_count") == 10, "minimal candidate file count stale")
    checks.check(minimal_candidate.get("source_policy_closed_rows") == 0, "minimal candidate source rows stale")
    checks.check(minimal_candidate.get("source_policy_total_rows") == 40, "minimal candidate source total stale")
    checks.check(
        minimal_candidate.get("direct_pc2_proof_gap_closed")
        == minimal_candidate.get("proof_gap_closed")
        == minimal_candidate_source.get("proof_gap_closed")
        is True
        and minimal_candidate.get("proof_gap_closed_scope")
        == "direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open"
        and "direct PC2" in minimal_candidate.get("proof_gap_closed_reading_rule", "")
        and "primitive" in minimal_candidate.get("proof_gap_closed_reading_rule", "")
        and "P6" in minimal_candidate.get("proof_gap_closed_reading_rule", "")
        and "P7" in minimal_candidate.get("proof_gap_closed_reading_rule", "")
        and "source-policy" in minimal_candidate.get("proof_gap_closed_reading_rule", ""),
        "minimal candidate proof boundary must be scoped to direct PC2",
    )
    checks.check(
        minimal_candidate.get("proof_gap_closed")
        == minimal_candidate_source.get("proof_gap_closed")
        is True,
        "minimal candidate proof boundary stale",
    )
    checks.check(minimal_candidate.get("read_only_replay_package") is True, "minimal candidate replay marker stale")
    checks.check(
        local_runner_companion.get("schema")
        == local_runner_companion_source.get("schema")
        == "cmame-local-accepted-runner-companion-v1",
        "local accepted-row runner companion schema stale in package manifest",
    )
    checks.check(
        local_runner_companion.get("status")
        == local_runner_companion_source.get("status")
        == "local_accepted_runner_companion_ready_source_policy_package_open",
        "local accepted-row runner companion status stale in package manifest",
    )
    checks.check(
        local_runner_companion.get("launcher_passed") is True
        and local_runner_companion.get("minimal_replay_boundary_preserved") is True
        and local_runner_companion.get("copies_runner_source") is False
        and local_runner_companion.get("uses_existing_self_contained_runner_candidates") is True,
        "local accepted-row runner companion boundary stale in package manifest",
    )
    checks.check(
        local_runner_companion.get("local_rows") == local_runner_companion_source.get("local_rows") == 12
        and set(local_runner_companion.get("self_contained_examples", []))
        == {"single_pendulum", "double_pendulum", "four_link", "slider_crank"}
        and local_runner_companion.get("replay_only_examples", []) == [],
        "local accepted-row runner companion row/example summary stale",
    )
    checks.check(
        local_runner_companion.get("source_policy_closed_rows") == 0
        and local_runner_companion.get("source_policy_total_rows") == 40
        and local_runner_companion.get("full_source_policy_runner_package_ready") is False
        and local_runner_companion.get("submission_ready") is False,
        "local accepted-row runner companion source-policy/submission boundary stale",
    )
    checks.check(
        local_runner_companion.get("candidate_python_file_count") == 1
        and 1 <= int(local_runner_companion.get("candidate_python_line_count", 0)) <= 220,
        "local accepted-row runner companion size changed",
    )
    checks.check(
        narrowed_repro_code_archive.get("schema")
        == narrowed_repro_code_archive_source.get("schema")
        == "cmame-narrowed-repro-code-archive-manifest-v1",
        "narrowed repro code archive schema stale in package manifest",
    )
    checks.check(
        narrowed_repro_code_archive.get("status")
        == narrowed_repro_code_archive_source.get("status")
        == "narrowed_repro_code_archive_ready_source_policy_open",
        "narrowed repro code archive status stale in package manifest",
    )
    checks.check(
        narrowed_repro_code_archive.get("archive") == "cmame_narrowed_repro_code_archive.zip"
        and narrowed_repro_code_archive.get("entrypoint")
        == "cmame_narrowed_repro_bundle/scripts/run_narrowed_repro_bundle.py"
        and narrowed_repro_code_archive.get("scope") == "narrowed_claim_only",
        "narrowed repro code archive path/scope stale in package manifest",
    )
    checks.check(
        narrowed_repro_code_archive.get("entry_count") == narrowed_repro_code_archive_source.get("entry_count")
        and narrowed_repro_code_archive.get("python_file_count")
        == narrowed_repro_code_archive_source.get("python_file_count")
        and narrowed_repro_code_archive.get("python_line_count")
        == narrowed_repro_code_archive_source.get("python_line_count"),
        "narrowed repro code archive inventory stale in package manifest",
    )
    checks.check(
        narrowed_repro_code_archive.get("narrowed_claim_reproducibility_package_ready") is True
        and narrowed_repro_code_archive.get("source_policy_rows_closed") == 0
        and narrowed_repro_code_archive.get("source_policy_rows_total") == 40
        and narrowed_repro_code_archive.get("full_source_policy_runner_package_ready") is False
        and narrowed_repro_code_archive.get("submission_ready") is False,
        "narrowed repro code archive boundary stale in package manifest",
    )
    checks.check(
        narrowed_repro_code_archive.get("source_policy_execution_handoff")
        == narrowed_repro_code_archive_source.get("source_policy_execution_handoff"),
        "narrowed repro code archive handoff boundary stale in package manifest",
    )
    checks.check(
        narrowed_archive_boundary
        == narrowed_repro_code_archive.get("narrowed_archive_boundary")
        == narrowed_archive_boundary_source,
        "narrowed archive boundary not mirrored across package manifest levels",
    )
    checks.check(
        narrowed_archive_boundary.get("blocker_required_to_close_by_id")
        == objective_completion.get("blocker_required_to_close_by_id")
        and narrowed_archive_boundary.get("blocker_safe_next_actions_by_id")
        == objective_completion.get("blocker_safe_next_actions_by_id")
        and narrowed_archive_boundary.get("blocker_opt_in_required_actions_by_id")
        == objective_completion.get("blocker_opt_in_required_actions_by_id"),
        "narrowed archive boundary objective closure/action maps stale in package manifest",
    )
    checks.check(
        summary.get("narrowed_archive_boundary_blocker_required_to_close_by_id")
        == narrowed_archive_boundary.get("blocker_required_to_close_by_id")
        and summary.get("narrowed_archive_boundary_blocker_safe_next_actions_by_id")
        == narrowed_archive_boundary.get("blocker_safe_next_actions_by_id")
        and summary.get("narrowed_archive_boundary_blocker_opt_in_required_actions_by_id")
        == narrowed_archive_boundary.get("blocker_opt_in_required_actions_by_id"),
        "narrowed archive boundary closure/action summary aliases stale",
    )
    checks.check(
        narrowed_archive_boundary.get("schema") == "narrowed-repro-code-archive-boundary-v1"
        and narrowed_archive_boundary.get("status")
        == "narrowed_archive_ready_not_full_source_policy_runner_archive"
        and narrowed_archive_boundary.get("scope") == "narrowed_claim_only",
        "narrowed archive boundary schema/status/scope changed in package manifest",
    )
    checks.check(
        narrowed_archive_boundary.get("blocking_ids")
        == objective_completion.get("blocking_ids")
        == archive_gap_objective_boundary.get("blocking_ids")
        == ["OC4", "OC6", "OC12"],
        "narrowed archive boundary blocker ids diverge from objective/archive-gap audits",
    )
    checks.check(
        narrowed_archive_boundary.get("blocker_status_by_id")
        == objective_completion.get("blocker_status_by_id")
        == archive_gap_objective_boundary.get("blocker_status_by_id")
        == {"OC4": "open", "OC6": "partial", "OC12": "partial"},
        "narrowed archive boundary blocker statuses diverge from objective/archive-gap audits",
    )
    checks.check(
        narrowed_archive_boundary.get("blocker_next_actions_by_id")
        == objective_completion.get("blocker_next_actions_by_id")
        == archive_gap_objective_boundary.get("blocker_next_actions_by_id"),
        "narrowed archive boundary next actions diverge from objective/archive-gap audits",
    )
    checks.check(
        narrowed_archive_boundary.get("closure_allowed_by_id")
        == archive_gap_objective_boundary.get("closure_allowed_by_id")
        == {"OC4": False, "OC6": False, "OC12": False}
        and narrowed_archive_boundary.get("archive_effect_by_id")
        == archive_gap_objective_boundary.get("archive_effect_by_id"),
        "narrowed archive boundary closure/effect maps diverge from archive-gap audit",
    )
    checks.check(
        narrowed_archive_boundary.get("source_policy_closed_ratio")
        == objective_completion.get("source_policy_closed_ratio")
        == full_source_runner_gap.get("source_policy_closed_ratio")
        == "0/40"
        and narrowed_archive_boundary.get("full_source_policy_runner_package_ready") is False
        and narrowed_archive_boundary.get("current_archive_usable_as_full_source_policy_runner_archive")
        is False
        and narrowed_archive_boundary.get("source_policy_execution_allowed_now") is False
        and narrowed_archive_boundary.get("exact_b4_opt_in_required_for_execution") is True,
        "narrowed archive boundary source-policy/use/execution flags changed",
    )
    checks.check(
        narrowed_archive_boundary.get("safe_action_ids") == expected_archive_safe_action_ids
        and narrowed_archive_boundary.get("opt_in_action_ids") == expected_archive_opt_in_action_ids,
        "narrowed archive boundary safe/opt-in action ids changed",
    )
    checks.check(
        narrowed_archive_boundary.get("source_artifacts")
        == [
            "OBJECTIVE_COMPLETION_AUDIT.json",
            "OBJECTIVE_COMPLETION_AUDIT.md",
            "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json",
            "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.md",
        ],
        "narrowed archive boundary source artifacts changed",
    )
    checks.check(
        summary.get("narrowed_archive_boundary_status")
        == narrowed_archive_boundary.get("status")
        and summary.get("narrowed_archive_boundary_scope")
        == narrowed_archive_boundary.get("scope")
        and summary.get("narrowed_archive_boundary_blocking_ids")
        == narrowed_archive_boundary.get("blocking_ids")
        and summary.get("narrowed_archive_boundary_blocker_status_by_id")
        == narrowed_archive_boundary.get("blocker_status_by_id")
        and summary.get("narrowed_archive_boundary_blocker_next_actions_by_id")
        == narrowed_archive_boundary.get("blocker_next_actions_by_id")
        and summary.get("narrowed_archive_boundary_closure_allowed_by_id")
        == narrowed_archive_boundary.get("closure_allowed_by_id")
        and summary.get("narrowed_archive_boundary_archive_effect_by_id")
        == narrowed_archive_boundary.get("archive_effect_by_id"),
        "narrowed archive boundary summary blocker fields are stale",
    )
    checks.check(
        summary.get("narrowed_archive_boundary_source_policy_closed_ratio")
        == narrowed_archive_boundary.get("source_policy_closed_ratio")
        and summary.get(
            "narrowed_archive_boundary_current_archive_usable_as_full_source_policy_runner_archive"
        )
        == narrowed_archive_boundary.get(
            "current_archive_usable_as_full_source_policy_runner_archive"
        )
        and summary.get("narrowed_archive_boundary_source_policy_execution_allowed_now")
        == narrowed_archive_boundary.get("source_policy_execution_allowed_now")
        and summary.get("narrowed_archive_boundary_exact_b4_opt_in_required_for_execution")
        == narrowed_archive_boundary.get("exact_b4_opt_in_required_for_execution")
        and summary.get("narrowed_archive_boundary_safe_action_ids")
        == narrowed_archive_boundary.get("safe_action_ids")
        and summary.get("narrowed_archive_boundary_opt_in_action_ids")
        == narrowed_archive_boundary.get("opt_in_action_ids")
        and summary.get("narrowed_archive_boundary_source_artifacts")
        == narrowed_archive_boundary.get("source_artifacts"),
        "narrowed archive boundary summary action/source fields are stale",
    )
    archive_handoff = narrowed_repro_code_archive.get("source_policy_execution_handoff", {})
    checks.check(
        archive_handoff.get("exact_required_user_approval_statement")
        == "I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json."
        and archive_handoff.get("guarded_execution_driver") == "run_b4_source_policy_after_opt_in.sh"
        and archive_handoff.get("driver_requires_exact_approval") is True
        and archive_handoff.get("driver_does_not_authorize_execution") is True
        and archive_handoff.get("opt_in_required_command_count") == 13
        and archive_handoff.get("opt_in_required_mapped_external_rows") == 20,
        "narrowed repro code archive exact approval/driver boundary changed",
    )

    for token in [
        "Status: **not_ready_self_contained_runner_centered_package_missing_source_policy**",
        "Submission-ready code package: `False`",
        "Reviewer-facing code limit: `12` Python files / `2000` lines.",
        "Research-audit tree primary submission allowed: `False`; provenance-only: `True`.",
        "Runner-centered package ready: `False`.",
        "Runner adapter present/self-contained: `True/False`.",
        "Broad self-contained source-policy package ready: `False`.",
        "Top-level package summary: candidate files `141/141`, candidate Python lines `180`, source-policy `0/40`, TFE runner `False`.",
        "Top-level source-policy handoff: `source_policy_execution_handoff_ready_not_authorized_not_run`; authorized/not-run `False/True`; driver `run_b4_source_policy_after_opt_in.sh`.",
        "Top-level source-policy execution boundary: allowed/invoked/exact `False/False/True`; safe/opt-in actions `['rebuild_read_only_audit_chain', 'rerun_read_only_validators', 'keep_narrowed_archive_provenance_only', 'monitor_reopen_conditions']/['authorized_b4_ra_hi_source_policy_execution']`.",
        "Top-level OC12 archive boundary: TFE preflight `contract_entrypoints_callable_candidate_backed_source_policy_open/3/3/3/3/0/4`; action boundary `4/1/False/False/True/13/20`; safe/opt-in actions `['rebuild_read_only_audit_chain', 'rerun_read_only_validators', 'keep_narrowed_archive_provenance_only', 'monitor_reopen_conditions']/['authorized_b4_ra_hi_source_policy_execution']`.",
        "Objective blocker status by id: `{'OC4': 'open', 'OC6': 'partial', 'OC12': 'partial'}`.",
        "Objective blocker required-to-close by id:",
        "Objective blocker safe next actions by id:",
        "Objective blocker opt-in required actions by id:",
        "Generic blocker aliases required/safe/opt-in:",
        "Source-policy rows closed: `0/40`",
        "Latest external public-code probe: `2026-06-21/9/0/0/4/False/False`.",
        "Full source-policy runner archive gap: `full_source_policy_runner_archive_not_ready_source_policy_open`; ready/current-archive-use `False/False`; rows closed/total `0/40`; terminal-unable/RA-HI-open `20/20`.",
        "Full source-policy runner archive terminal reopen conditions: `tfe2026_original_pendulum=new_public_or_source_code_equivalent_tfe_implementation_artifact; vp2024_velocity_partitioning=new_distinct_public_vp2024_velocity_partitioning_code_path`.",
        f"Source-policy reopen monitor digests: direct `{summary.get('source_policy_reopen_condition_monitor_local_scan_digest')}/{summary.get('source_policy_reopen_condition_monitor_evidence_digest')}`; archive `{summary.get('full_source_policy_runner_archive_gap_reopen_monitor_local_scan_digest')}/{summary.get('full_source_policy_runner_archive_gap_reopen_monitor_evidence_digest')}`.",
        "Full source-policy runner archive exact B4 approval: `I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json.`.",
        "Source-policy execution handoff exact approval/driver: `I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json./run_b4_source_policy_after_opt_in.sh/True/True/13/20`.",
        "Source-policy execution handoff traceability: unique RA/HI rows `20/20`; row refs `32/32`; mismatches/terminal/closed/promotion-ready `0/0/0/0`.",
        "Source-policy expected-output promotion-readiness blocker audit: `expected_outputs_schema_ready_but_promotion_blocked`; commands/schema-ready/promotion-ready/row-refs/unique-rows/not-promoted/summary-closed/promoted/blocked `13/13/0/32/20/20/0/0/13`.",
        "Narrowed repro code archive handoff exact approval/driver: `I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json./run_b4_source_policy_after_opt_in.sh/True/True/13/20`.",
        f"Narrowed archive boundary/status/scope/source-policy/use/execution/exact: `{summary.get('narrowed_archive_boundary_status')}/{summary.get('narrowed_archive_boundary_scope')}/{summary.get('narrowed_archive_boundary_source_policy_closed_ratio')}/{summary.get('narrowed_archive_boundary_current_archive_usable_as_full_source_policy_runner_archive')}/{summary.get('narrowed_archive_boundary_source_policy_execution_allowed_now')}/{summary.get('narrowed_archive_boundary_exact_b4_opt_in_required_for_execution')}`.",
        "Narrowed archive boundary required-to-close by blocker:",
        "Narrowed archive boundary safe next actions by blocker:",
        "Narrowed archive boundary opt-in required actions by blocker:",
        f"Narrowed archive boundary safe/opt-in actions/source artifacts: `{summary.get('narrowed_archive_boundary_safe_action_ids')}/{summary.get('narrowed_archive_boundary_opt_in_action_ids')}/{summary.get('narrowed_archive_boundary_source_artifacts')}`.",
        "VP2024 public-code recheck: `public_code_rechecked_no_distinct_vp2024_path_attempted_not_reproducible` on `2026-06-13`; tree truncated `False`; paths/all-2024/keyword-hits `4487/1540/0`; attempted-not-reproducible/closed `4/0`; external superiority `False`.",
        "B4 existing-artifact promotion audit: `no_existing_artifact_promotable_without_new_source_policy_execution`; candidates `8`; promotion-ready `0`; source-policy rows `0/40`; closes B4/B7 `0/0`.",
        f"B4 post-execution audit: `{b4_post_execution_audit.get('status')}`; verified authorized execution `{authorized_b4}`; existing ready-command artifacts `True`; scope `{expected_b4_scope}`; commands `13`; mapped/unaddressed rows `20/0`; expected outputs present `True`; source-policy rows `0/40`; closes B4/B7 `False/False`.",
        "Full source-policy row provenance audit: `row_provenance_preflight_complete_source_policy_promotion_open`; rows/preflight/public-root/unable `40/40/20/20`; closed/promotion-ready `0/0`.",
        "Full source-policy row provenance handoff exact approval/driver: `I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json./run_b4_source_policy_after_opt_in.sh/True/True/13/20/20`.",
        "RA/HI source-policy closeout checklist: `ready_for_authorized_execution_closeout_not_executed_not_promoted`; rows RA/HI/total `12/8/20`; commands/mapped `13/20`; promoted/completed/external-ready `0/0/0`; opt-in/executed `True/False`; closes B4/B7 `False/False`.",
        "RA/HI source-policy output inventory: `existing_expected_outputs_present_not_promotion_evidence`; commands/outputs/summaries `13/13/8`; csv rows/HI ok/closed `54/22/0`.",
        "HI2022 rA_half double failure diagnosis: `diagnosis_only_partial_newton_failure_not_promoted`; ok/failed/total `1/2/3`; Newton failures `2`; pair orders available `False`; rows promoted `0`.",
        "HI2022 rA_half double repair attempt: `targeted_repair_attempted_not_reproducible_not_promoted`; target ok/failed `1/2`; combined rows/groups `19/24` and `4/8`; rows promoted `0`.",
        "B4 row closure-readiness ledger: `all_40_external_rows_mapped_20_attempted_not_reproducible_0_source_policy_rows_closed`; external rows `40/40`; closed/open `0/20`; command-mapped/no-command `20/20`; ready/not-ready suites `2/2`.",
        "B4 execution opt-in packet: `ready_for_user_opt_in_packet_not_authorized_not_run`; opt-in required `True`; commands `13`; mapped/unaddressed rows `20/0`; source-policy rows `0/40`.",
        "Source-policy execution handoff: `source_policy_execution_handoff_ready_not_authorized_not_run`; authorized/commands-not-run `False/True`; ready commands/mapped `13/20`; terminal unable `20`.",
        "B4 post-execution promotion contract: `b4-source-policy-post-execution-promotion-contract-v1` / `promotion_contract_defined_no_rows_promoted`; rows `0/40`; ready/unaddressed `20/0`; checks satisfied `False`; closes B4/B7 `False/False`.",
        "TFE source-policy runner implemented: `False`",
        "TFE public-code recheck: `public_code_rechecked_no_distinct_tfe_code_artifact_attempted_not_reproducible` on `2026-06-13`; repo/user/code-search `0/0/requires_authentication`; attempted-not-reproducible/closed `16/0`; external superiority `False`.",
        "TFE candidate/source-policy boundary sources/match/use: `TFE_SOURCE_POLICY_SPEC.json,TFE_SOURCE_POLICY_ROW_AUDIT.json,TFE_DAE_RUNNER_CONTRACT_GAP_AUDIT.json,TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.json/True/diagnostic_scaffold_only_not_source_policy_reproduction`.",
        "TFE candidate/source-policy boundary DAE/method/source rows/external-superiority: `False/False/0/False`.",
        "TFE DAE runner contract gap status/missing/non-heavy/execution/ready/heavy-run: `dae_runner_contract_gap_open_not_source_policy/6/2/4/False/False`.",
        "TFE DAE runner contract accounting raw/non-heavy-terminal/effective-execution/source-rows: `6/2/4/0`.",
        "TFE DAE runner effective execution blocks: `['pendulum_absolute_coordinate_source_policy_dae_runner_missing', 'tfe_newmark_trapezoidal_source_policy_method_runners_missing', 'gauss6_fullva_absolute_coordinate_source_policy_runner_missing', 'accepted_source_policy_work_precision_rows_not_executed_or_bound']`.",
        "TFE source-policy execution preflight status/opt-in/nonheavy/execution/promote/ready: `terminal_no_public_code_self_reproduction_attempted_not_promoted/False/True/4/False/False`.",
        "TFE runner contract preflight status/entrypoints/candidate-backed/source-rows/execution-blocks: `contract_entrypoints_callable_candidate_backed_source_policy_open/3/3/3/3/0/4`.",
        "OC12 full-archive TFE runner preflight status/entrypoints/candidate-backed/source-rows/execution-blocks: `contract_entrypoints_callable_candidate_backed_source_policy_open/3/3/3/3/0/4`.",
        "TFE self-reproduction preflight route/reopen/source rows: `no_public_code_self_reproduction_attempted_unable_to_reproduce_not_promoted/new_public_or_source_code_equivalent_tfe_implementation_artifact/0`.",
        "TFE self-reproduction preflight blocks/ready/promote/next-actions: `4/False/False/3`.",
        "TFE DAE runner contract missing ids: `['brown_mcphee_source_code_equivalent_law_open', 'pendulum_absolute_coordinate_source_policy_dae_runner_missing', 'tfe_newmark_trapezoidal_source_policy_method_runners_missing', 'gauss6_fullva_absolute_coordinate_source_policy_runner_missing', 'full_T10_source_grid_endpoint_policy_open', 'accepted_source_policy_work_precision_rows_not_executed_or_bound']`.",
        "TFE source pendulum parameter/smoke/absolute-residual/time-smoke/output/candidate friction/setup: `True/True/True/True/True/True/True`",
        "TFE Brown--McPhee boundary/source-equivalent/transition/rows/block-closed: `source_formula_structure_encoded_surrogate_not_source_code_equivalent/False/False/0/False`.",
        "TFE Brown--McPhee candidate DAE contract rows/step/source/equivalent DAE/method/source-law/monolithic: `12/56/0/False/False/False/False`.",
        "TFE Brown--McPhee candidate DAE contract finite/residual/power: `True/True/True`.",
        "TFE Brown--McPhee transition-velocity sensitivity rows/contracts/source/material/equivalence-false: `3/36/0/True/True`.",
        "TFE Brown--McPhee source-code equivalence certificate status/available/positive/closed-block/exec/close-now: `negative_source_code_equivalence_certificate_not_source_policy/True/False/False/False/False`.",
        "TFE source pendulum bounded reference-policy smoke/full T=10 source run: `True/False`",
        "TFE source pendulum full-T=10 source-reference feasibility probe: implemented/completed/source-policy rows `True/True/0`; source/check steps `100000/200000`; coordinate/velocity check errors `3.819e-14/2.485e-13`",
        "TFE source pendulum comparator candidate runners/Newmark/trapezoidal/TFE-m-candidate/method-equivalent/TFE m=1-3 source-policy: `True/True/True/True/False/False`",
        "TFE source pendulum Gauss6 candidate smoke/absolute-coordinate source-policy runner: `True/False`",
        "TFE source pendulum Gauss6 candidate rows/source-policy rows/method-equivalent: `2/0/False`",
        "TFE source pendulum unified bounded runner rows/full T=10/source-policy rows: `4/False/0`",
        "TFE source pendulum active-B2 candidate rows/full T=10/source-policy rows: `4/False/0`",
        "TFE source pendulum active-B2 source-reference full-T10 probe: implemented/fullT10/reference-invoked/source-policy rows/finite/residual-ok/method-equivalent `True/True/True/0/4/4/False`",
        "TFE full-T10 absolute DAE-lift diagnostic: `full_T10_absolute_dae_lift_candidate_summarized_not_source_policy`; completed/methods/metric-rows/step-residual-rows `True/4/12/2800`; reference-invoked/source-policy rows/monolithic/equivalent `True/0/False/False`.",
        "TFE endpoint boundary certificate: `endpoint_policy_literal_overrun_bound_proved_source_policy_open`; proved/exact/overrun/source rows/full-policy/exact-T-equivalent `True/2/4/0/False/False`.",
        "TFE full-T10 endpoint policy closure certificate status/available/positive/closed-block/exec/close-now: `negative_full_T10_endpoint_policy_certificate_not_source_policy/True/False/False/False/False`.",
        "TFE source-grid policy/source-text endpoint audit: `False/4` and exact-T subset `True/2/4` and source-text `True/",
        "TFE endpoint sensitivity diagnostic: `diagnostic_endpoint_policy_sensitivity_not_source_policy`; methods/policies/raw rows `4/4/48`; source-policy rows `0`; superiority allowed `False`.",
        "Objective complete/blocking open: `False/3`",
        "Direct PC2 proof gap closed: `True`",
        "Direct proof gap scope: `direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open`.",
        "Direct proof gap reading rule: The schema-only compatibility boolean proof_gap_closed is a schema-compatible shorthand for direct_pc2_proof_gap_closed under the active direct PC2 residual-bridge/Kantorovich route. It does not close the primitive/Taylor route, P6 solver-policy evidence, P7 residual-to-error promotion, source-policy readiness, or full-TFE replacement.",
        "Schema-only compatibility key `proof_gap_closed` retained: `True`; reader-facing proof status should use `direct_pc2_proof_gap_closed`.",
        "Proof theorem/manuscript traceability: labels/boundary/mapped `True/True/True`; dependency/dynamic/primitive/nonpromotion `True/True/True/True`.",
        "Proof theorem no-promotion boundary: eta condition/closure `True/False`; fixed-tolerance proof `False`; residual/source-policy-full-TFE not promoted `True/True`; no-state-change `True`.",
        "Newton-Euler obligation coverage matrix/links/complete rows/proof-closure-advanced: `True/180/36/False`",
        "Minimal reproducibility candidate/status/files/Python-files/Python-lines/size-ok/replay-only/runner-centered: `True/candidate_replay_package_built_not_submission_ready/10/1/",
        "Local accepted-row runner companion/status/rows/Python-lines/source-policy/full-source-ready: `True/local_accepted_runner_companion_ready_source_policy_package_open/12/",
        "Narrowed reproducibility package/status/ready/source-policy/full-source-ready: `narrowed_claim_reproducibility_package_ready_full_source_policy_open/True/0/40/False`.",
        "Narrowed repro code archive/status/entries/Python/source-policy/full-source-ready/submission-ready: `narrowed_repro_code_archive_ready_source_policy_open/",
        "Source-policy-open status-token rule: any manifest status ending in `source_policy_open` or `source_policy_package_open` denotes a local, narrowed replay/provenance artifact whose source-policy rows are still open; it is not source-policy readiness, external-superiority evidence, or a submission-ready runner-package claim.",
        "Minimal submission code dependency boundary: `narrowed_repro_ready_full_source_policy_package_blocked`; ready `False`; safe use `narrowed_claim_replay_and_audit_provenance_only`; primary package allowed `False`.",
        "Minimal submission code dependency blockers/source rows: `['OC4', 'OC6', 'OC12']`; upstream gates `OC4_source_policy_reproduction_rows,OC6_TFE_source_policy_runner,OC12_full_source_policy_runner_archive`; source-policy `0/40`; narrowed archive source-policy `0/40`.",
        "Runner-centered audit/status/source-lines: `local_runner_centered_candidate_ready_source_policy_package_open/",
        "Local accepted-row runner/full source-policy runner ready: `True/False`.",
        "Runner adapter/status/Python-lines: `runner_adapter_candidate_external_v048_required_not_submission_ready/",
        "Runner adapter closed-loop local replay rows/models: `6` / `['four_link', 'slider_crank']`.",
        "Runner adapter closed-loop replay outputs: `True`.",
        "Self-contained runner extraction/status/symbols/symbol-lines: `local_accepted_rows_self_contained_runner_ready_source_policy_package_open/",
        "Self-contained local accepted-row/full source-policy/B6 narrowed/full-source-prose ready: `True/False/True/False`.",
        "B6 closed-loop extraction audit/status/source-files/symbols/ready: `closed_loop_self_contained_runner_candidate_ready_source_policy_open/",
        "Compact closed-loop candidate/status/rows/Python-lines/line-limit-ok: `closed_loop_local_runner_candidate_passed_compact/6/",
        "P1 local runner audit/status/ready/v047-lines/closure-lines: `closed_single_double_runner_candidates_ready/True/69264/",
        "P1 single-runner candidate/status/rows/position-order/velocity-order: `True/3/",
        "P1 double-runner candidate/status/rows/position-order/velocity-order: `True/3/",
        "Human-runnable local evidence examples/self-contained/replay-only: `['single_pendulum', 'double_pendulum', 'four_link', 'slider_crank']` / `['single_pendulum', 'double_pendulum', 'four_link', 'slider_crank']` / `[]`.",
        "Human-runnable four-example local evidence/self-contained simulation: `True/True`.",
        "B6 four-example local evidence runner: `True`; rows `12`;",
        "Source-policy command preflight freeze: `command_preflight_frozen_not_authorized_not_run_not_promoted`; commands/unique-rows/row-refs/mismatches/artifacts/executed/closed `13/20/32/0/21/False/0`.",
        "Source-policy expected-output schema audit: `expected_outputs_schema_ready_not_authorized_not_run_not_promoted`; commands/artifacts/hash-match/csv/json/schema-ready/executed/closed `13/21/21/13/8/13/False/0`.",
        "OC6 source-equivalent reopen-readiness audit: `oc6_reopen_conditions_monitored_no_positive_source_equivalent_artifact`; rows TFE/VP/total/unable/public-code/candidate/source-equivalent/positive/local-positive/closed/search/close-now `16/4/20/20/0/20/0/0/0/0/False/False`.",
        "OC6 source-equivalent reopen-readiness latest external probe: `2026-06-21/9/0/0/4/False/False`.",
        "`full_source_policy_runner_archive`",
        "research/audit repository",
    ]:
        checks.check(token in manifest_md, f"manifest markdown missing token: {token}")

    if checks.errors:
        print("cmame reproducibility package manifest validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("cmame reproducibility package manifest validation: PASS")
    print(f"status={manifest.get('status')}")
    print(f"candidate_files={manifest.get('candidate_existing_file_count')}/{manifest.get('candidate_file_count')}")
    print(f"source_policy_closed={summary.get('source_policy_closed_rows')}/{summary.get('source_policy_total_rows')}")
    print(f"source_policy_execution_handoff_driver={summary.get('source_policy_execution_handoff_driver')}")
    print(
        "source_policy_execution_handoff_driver_requires_exact_approval="
        f"{summary.get('source_policy_execution_handoff_driver_requires_exact_approval')}"
    )
    print(
        "source_policy_execution_handoff_driver_does_not_authorize_execution="
        f"{summary.get('source_policy_execution_handoff_driver_does_not_authorize_execution')}"
    )
    print(
        "source_policy_execution_allowed_now="
        f"{manifest.get('source_policy_execution_allowed_now')}"
    )
    print(
        "source_policy_execution_invoked="
        f"{manifest.get('source_policy_execution_invoked')}"
    )
    print(f"tfe_runner={summary.get('tfe_source_policy_runner_implemented')}")
    print(
        "tfe_runner_contract_preflight="
        f"{summary.get('tfe_runner_contract_preflight_status')}/"
        f"{summary.get('tfe_runner_contract_preflight_entrypoints')}/"
        f"{summary.get('tfe_runner_contract_preflight_candidate_backed')}/"
        f"{summary.get('tfe_runner_contract_preflight_source_policy_rows_completed')}/"
        f"{summary.get('tfe_runner_contract_preflight_execution_blocks')}"
    )
    print(f"oc12_archive_tfe_preflight={oc12_archive_tfe_preflight}")
    print(f"oc12_archive_action_boundary={oc12_archive_action_boundary}")
    print(f"oc6_reopen_latest_external_probe={oc6_reopen_latest_external_probe}")
    print("oc12_archive_source_policy_execution_invoked=False")
    print(
        "oc12_archive_safe_action_ids="
        + ",".join(summary.get("full_source_policy_runner_archive_gap_safe_action_ids", []))
    )
    print(
        "oc12_archive_opt_in_action_ids="
        + ",".join(summary.get("full_source_policy_runner_archive_gap_opt_in_action_ids", []))
    )
    print(f"minimal_package_ready={summary.get('minimal_reproducible_submission_code_ready')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
