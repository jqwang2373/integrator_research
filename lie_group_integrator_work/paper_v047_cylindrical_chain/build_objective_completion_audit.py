#!/usr/bin/env python3
"""Build an objective-level completion audit for the CMAME paper goal.

The audit is intentionally read-only. It checks whether the actual user goal is
proved by current artifacts, rather than whether a narrow validator passed.
"""

from __future__ import annotations

import json
from pathlib import Path


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
V048 = ROOT / "v048_cross_paper_same_test_benchmarks"
OUT_JSON = PAPER / "OBJECTIVE_COMPLETION_AUDIT.json"
OUT_MD = PAPER / "OBJECTIVE_COMPLETION_AUDIT.md"
DIRECT_PC2_SCOPE = "direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open"
DIRECT_PC2_READING_RULE = (
    "The schema-only compatibility boolean proof_gap_closed is a schema-compatible "
    "shorthand for direct_pc2_proof_gap_closed under the active direct PC2 residual-bridge/"
    "Kantorovich route. It does not close the primitive/Taylor route, P6 "
    "solver-policy evidence, P7 residual-to-error promotion, source-policy "
    "readiness, or full-TFE replacement."
)
DEFAULT_SAFE_ACTION_IDS = [
    "rebuild_read_only_audit_chain",
    "rerun_read_only_validators",
    "keep_narrowed_archive_provenance_only",
    "monitor_reopen_conditions",
]
DEFAULT_OPT_IN_ACTION_IDS = ["authorized_b4_ra_hi_source_policy_execution"]
DEFAULT_REQUIRED_USER_APPROVAL_STATEMENT = (
    "I explicitly approve running the B4 source-policy execution commands listed in "
    "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json."
)


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def code_inventory(path: Path) -> dict[str, object]:
    files = sorted(path.glob("*.py"))
    line_counts = {item.name: len(read_text(item).splitlines()) for item in files}
    prefix_counts = {
        "build": sum(1 for item in files if item.name.startswith("build_")),
        "validate": sum(1 for item in files if item.name.startswith("validate_")),
        "run": sum(1 for item in files if item.name.startswith("run_")),
        "merge": sum(1 for item in files if item.name.startswith("merge_")),
    }
    return {
        "file_count": len(files),
        "line_count": sum(line_counts.values()),
        "prefix_counts": prefix_counts,
    }


def req(
    req_id: str,
    requirement: str,
    status: str,
    evidence: list[str],
    blocking: bool,
    observed: dict[str, object],
    next_to_close: str,
) -> dict[str, object]:
    return {
        "id": req_id,
        "requirement": requirement,
        "status": status,
        "blocking_for_goal_completion": blocking,
        "evidence": evidence,
        "observed": observed,
        "next_to_close": next_to_close,
    }


def main() -> None:
    matrix = read_json(PAPER / "PAPER_NUMERICAL_RESULT_MATRIX.json")
    traceability = read_json(PAPER / "RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.json")
    recomputation = read_json(PAPER / "COMMON_REFERENCE_ORDER_RECOMPUTATION_AUDIT.json")
    source_policy = read_json(PAPER / "EXTERNAL_SOURCE_POLICY_CLOSURE_MANIFEST.json")
    ra_hi_closeout = read_json(PAPER / "RA_HI_SOURCE_POLICY_CLOSEOUT_CHECKLIST.json")
    ra_hi_promotion_matrix = read_json(PAPER / "RA_HI_SOURCE_POLICY_PROMOTION_BLOCKER_MATRIX.json")
    b2_remaining = read_json(PAPER / "B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.json")
    external_demotion = read_json(PAPER / "EXTERNAL_SUITE_DEMOTION_LEDGER.json")
    tfe_model = read_json(PAPER / "TFE_SOURCE_PENDULUM_MODEL_AUDIT.json")
    tfe_dae_gap = read_json(PAPER / "TFE_DAE_RUNNER_CONTRACT_GAP_AUDIT.json")
    tfe_self_reproduction = read_json(
        PAPER / "TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.json"
    )
    source_policy_public_code_refresh = read_json(
        PAPER / "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.json"
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
    source_policy_reopen_monitor = read_json(
        PAPER / "SOURCE_POLICY_REOPEN_CONDITION_MONITOR_20260620.json"
    )
    tfe_runner_contract_preflight = read_json(
        PAPER / "TFE_RUNNER_CONTRACT_PREFLIGHT_CERTIFICATE.json"
    )
    tfe_execution_preflight = tfe_dae_gap.get("source_policy_execution_preflight", {})
    tfe_brown_mcphee = read_json(PAPER / "TFE_BROWN_MCPHEE_SOURCE_LAW_BOUNDARY_AUDIT.json")
    tfe_brown_mcphee_certificate = read_json(
        PAPER / "TFE_BROWN_MCPHEE_SOURCE_CODE_EQUIVALENCE_CERTIFICATE.json"
    )
    tfe_grid = read_json(PAPER / "TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.json")
    tfe_endpoint_boundary = read_json(PAPER / "TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.json")
    tfe_endpoint_certificate = read_json(
        PAPER / "TFE_FULL_T10_ENDPOINT_POLICY_CLOSURE_CERTIFICATE.json"
    )
    tfe_endpoint_sensitivity = read_json(PAPER / "TFE_ENDPOINT_POLICY_SENSITIVITY_AUDIT.json")
    proof = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
    proof_claim_traceability = read_json(PAPER / "PROOF_CLAIM_TRACEABILITY_AUDIT.json")
    strict_proof_policy = read_json(PAPER / "CMAME_STRICT_PROOF_POLICY_RECONCILIATION_AUDIT.json")
    blocker = read_json(PAPER / "CMAME_BLOCKER_CLOSURE_GATE.json")
    integrity = read_json(PAPER / "CMAME_SUBMISSION_INTEGRITY_AUDIT.json")
    figures = read_json(PAPER / "CMAME_FIGURE_SET_AUDIT.json")
    prose = read_json(PAPER / "CMAME_PROSE_RESIDUE_AUDIT.json")
    related = read_json(PAPER / "CMAME_RELATED_WORK_AUDIT.json")
    visual = read_json(PAPER / "CMAME_VISUAL_LEGIBILITY_AUDIT.json")
    minimal_candidate = read_json(PAPER / "CMAME_MINIMAL_REPRODUCIBILITY_CANDIDATE_MANIFEST.json")
    runner_centered = read_json(PAPER / "CMAME_RUNNER_CENTERED_REPRODUCIBILITY_AUDIT.json")
    b6_local_evidence = read_json(PAPER / "B6_FOUR_EXAMPLE_LOCAL_EVIDENCE_SUMMARY.json")
    closed_loop_candidate = read_json(PAPER / "CMAME_CLOSED_LOOP_LOCAL_RUNNER_CANDIDATE_MANIFEST.json")
    p1_local_runner = read_json(PAPER / "CMAME_P1_LOCAL_RUNNER_EXTRACTION_AUDIT.json")
    narrowed_repro = read_json(PAPER / "CMAME_NARROWED_REPRODUCIBILITY_PACKAGE_AUDIT.json")
    narrowed_repro_code_archive = read_json(PAPER / "CMAME_NARROWED_REPRO_CODE_ARCHIVE_MANIFEST.json")
    b4_execution_handoff = read_json(PAPER / "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json")
    b4_guarded_refusal = read_json(
        PAPER / "B4_GUARDED_DRIVER_REFUSAL_BOUNDARY_AUDIT_20260621.json"
    )
    b4_command_traceability_summary = b4_execution_handoff.get(
        "command_row_traceability", {}
    ).get("summary", {})
    full_source_policy_row_provenance = read_json(PAPER / "FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.json")
    oc6_source_equivalent_reopen = read_json(PAPER / "OC6_SOURCE_EQUIVALENT_REOPEN_READINESS_AUDIT_20260620.json")
    full_source_runner_gap = read_json(PAPER / "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json")
    full_source_runner_terminal_reopen_conditions = {
        item.get("suite_id"): item.get("reopen_condition")
        for item in full_source_runner_gap.get("terminal_unable_to_reproduce_suites", [])
        if isinstance(item, dict)
    }
    full_source_runner_required_approval_statement = full_source_runner_gap.get(
        "ra_hi_closeout_boundary", {}
    ).get("required_user_approval_statement")

    paper_code = code_inventory(PAPER)
    v048_code = code_inventory(V048)
    combined_python_line_count = int(paper_code["line_count"]) + int(v048_code["line_count"])

    examples = set(matrix.get("examples", []))
    expected_examples = {"single_pendulum", "double_pendulum", "four_link", "slider_crank"}
    core_matrix_ready = (
        matrix.get("row_count") == matrix.get("expected_row_count") == 44
        and matrix.get("raw_row_count") == 132
        and matrix.get("method_count") == 11
        and examples == expected_examples
    )
    traceability_ready = (
        traceability.get("claim_boundary", {}).get("result_to_manuscript_traceability_closed") is True
        and traceability.get("coverage", {}).get("velocity_cells_checked") == 44
        and traceability.get("coverage", {}).get("main_tex_velocity_cells_matched") == 44
        and traceability.get("coverage", {}).get("main_pdf_velocity_cells_matched") == 44
        and traceability.get("coverage", {}).get("flat_tex_velocity_cells_matched") == 44
        and traceability.get("coverage", {}).get("flat_pdf_velocity_cells_matched") == 44
    )
    common_reference_closed = (
        matrix.get("direct_nonlocal_velocity_order_wins")
        == matrix.get("direct_nonlocal_velocity_order_comparisons")
        == 40
        and matrix.get("direct_nonlocal_velocity_error_wins")
        == matrix.get("direct_nonlocal_velocity_error_comparisons")
        == 40
        and matrix.get("source_policy_external_superiority_allowed") is False
        and recomputation.get("anomalies", {}).get("mismatch_count", 0) == 0
    )
    source_policy_closed = (
        source_policy.get("source_policy_reproduction") is True
        and source_policy.get("external_superiority_claim_allowed") is True
    )
    expected_b2_demoted_suite_counts = {
        "hi2022_half_implicit": 3,
        "ra2021_absolute_coordinate": 5,
        "tfe2026_original_pendulum": 4,
        "vp2024_velocity_partitioning": 3,
    }
    external_demoted_suite_ids = {
        item.get("suite_id") for item in external_demotion.get("demoted_suites", [])
    }
    b2_source_policy_rows_closed = b2_remaining.get("source_policy_closed_rows") == 40
    b2_active_suites_closed_by_demotion = (
        b2_remaining.get("b2_can_close_now") is True
        and b2_remaining.get("active_flagged_row_count") == 0
        and b2_remaining.get("b2_remaining_requirements") == []
        and b2_remaining.get("demoted_flagged_row_count") == 15
        and b2_remaining.get("demoted_suite_counts") == expected_b2_demoted_suite_counts
        and b2_remaining.get("external_superiority_claim_allowed") is False
        and b2_remaining.get("source_policy_closed_rows") == 0
        and external_demotion.get("status")
        == "all_external_suites_demoted_from_external_superiority_scope"
        and external_demotion.get("remaining_open_suites") == []
        and external_demotion.get("active_source_policy_flagged_rows_after_demotions") == 0
        and external_demotion.get("b2_required_to_close_after_demotions") == []
        and external_demoted_suite_ids == set(expected_b2_demoted_suite_counts)
        and all(
            item.get("accepted_for_external_superiority") is False
            for item in external_demotion.get("demoted_suites", [])
        )
    )
    b2_active_suites_closed = b2_source_policy_rows_closed or b2_active_suites_closed_by_demotion
    tfe_runner_closed = (
        tfe_model.get("source_pendulum_parameter_model_implemented") is True
        and tfe_model.get("frictionless_planar_rhs_smoke_implemented") is True
        and tfe_model.get("absolute_coordinate_dae_residual_smoke_implemented") is True
        and tfe_model.get("source_output_time_integration_smoke_implemented") is True
        and tfe_model.get("source_reference_solution_policy_smoke_implemented") is True
        and tfe_model.get("bounded_source_policy_runner_smoke_implemented") is True
        and tfe_model.get("active_tfe_b2_candidate_row_smoke_implemented") is True
        and tfe_model.get("source_error_norm_and_output_policy_encoded") is True
        and tfe_model.get("pendulum_dae_runner_implemented") is True
        and tfe_model.get("brown_mcphee_friction_law_implemented") is True
        and tfe_model.get("source_policy_rows_completed") == 4
    )
    tfe_bridge = tfe_model.get("dae_trajectory_bridge_contract_smoke", {})
    tfe_transition_velocity_sensitivity = tfe_brown_mcphee.get(
        "brown_mcphee_transition_velocity_sensitivity", {}
    )
    tfe_dae_missing_block_ids = [
        item.get("id") for item in tfe_dae_gap.get("missing_contract_blocks", [])
    ]
    tfe_dae_nonheavy_dispositions = tfe_dae_gap.get(
        "nonheavy_missing_contract_block_dispositions", []
    )
    tfe_dae_nonheavy_disposition_ids = [
        item.get("id") for item in tfe_dae_nonheavy_dispositions
    ]
    proof_closed = (
        proof.get("closure_state", {}).get("proof_gap_closed") is True
        and proof.get("closure_state", {}).get("stage_residual_O_h7_implementation_defect_proved") is True
        and proof.get("closure_state", {}).get("pc2_closed_by_direct_substitution") is True
        and proof.get("evidence_summary", {}).get("newton_euler_d5_direct_substitution_dynamic_zero_rows") == 36
        and proof.get("evidence_summary", {}).get("newton_euler_d5_direct_substitution_full_stage_rows") == 132
    )
    quality_review_closed = (
        blocker.get("mechanical_preflight_passed") is True
        and blocker.get("quality_review_passed") is True
        and blocker.get("submission_ready") is False
        and blocker.get("submission_ready_under_narrowed_claim") is True
        and all(item.get("status") == "closed" for item in blocker.get("blockers", []))
    )
    integrity_closed = (
        integrity.get("local_integrity_passed") is True
        and integrity.get("external_reference_web_verification_complete") is True
        and integrity.get("claim_boundary", {}).get("submission_integrity_gate_closed") is True
    )
    prose_b6_closed_under_narrowed_policy = (
        prose.get("post_baseline_final_prose_dependency", {}).get("b6_closure_allowed_now") is True
        and prose.get("post_baseline_final_prose_dependency", {}).get("final_prose_pass_ready") is True
        and prose.get("main_body_machine_token_count") == 0
        and prose.get("flat_main_body_machine_token_count") == 0
    )
    presentation_closed = (
        figures.get("b7_closed") is True
        and prose_b6_closed_under_narrowed_policy
        and related.get("status") == "b8_closed_related_work_depth_checked"
        and visual.get("status") == "b5_closed_mechanism_visual_reproducibility_checked"
    )
    review_agent_present = all(
        (PAPER / item).exists()
        for item in [
            "cmame_submission_review_agent.py",
            "validate_cmame_review_agent.py",
            "CMAME_REVIEW_AGENT_REPORT.json",
            "CMAME_REVIEW_AGENT_REPORT.md",
        ]
    )
    minimal_code_ready = (
        combined_python_line_count <= 20000 and source_policy_closed and proof_closed and core_matrix_ready
    )
    expected_local_runner_examples = ["single_pendulum", "double_pendulum", "four_link", "slider_crank"]
    human_runnable_self_contained_examples = list(b6_local_evidence.get("self_contained_examples", []))
    human_runnable_replay_only_examples = list(b6_local_evidence.get("replay_only_examples", []))
    local_runner_package_partial_ready = (
        runner_centered.get("local_runner_centered_candidate_ready") is True
        and runner_centered.get("full_source_policy_runner_package_ready") is False
        and b6_local_evidence.get("b6_local_evidence_runner_passed") is True
        and b6_local_evidence.get("local_rows") == 12
        and human_runnable_self_contained_examples == expected_local_runner_examples
        and human_runnable_replay_only_examples == []
        and b6_local_evidence.get("human_runnable_four_example_local_evidence_available") is True
        and b6_local_evidence.get("human_runnable_four_example_self_contained_simulation_ready") is True
        and closed_loop_candidate.get("runner_passed") is True
        and closed_loop_candidate.get("self_contained_simulation_runner") is True
        and closed_loop_candidate.get("candidate_python_line_limit_ok") is True
        and closed_loop_candidate.get("closed_loop_local_rows") == 6
        and p1_local_runner.get("p1_single_runner_candidate_ready") is True
        and p1_local_runner.get("p1_double_runner_candidate_ready") is True
        and p1_local_runner.get("p1_regenerated_candidate_rows") == p1_local_runner.get("p1_required_rows") == 6
        and p1_local_runner.get("p1_missing_candidate_rows") == 0
    )
    narrowed_repro_code_archive_ready = (
        narrowed_repro.get("narrowed_claim_reproducibility_package_ready") is True
        and narrowed_repro_code_archive.get("status")
        == "narrowed_repro_code_archive_ready_source_policy_open"
        and narrowed_repro_code_archive.get("entrypoint")
        == "cmame_narrowed_repro_bundle/scripts/run_narrowed_repro_bundle.py"
        and narrowed_repro_code_archive.get("source_policy_rows_closed") == 0
        and narrowed_repro_code_archive.get("source_policy_rows_total") == 40
        and narrowed_repro_code_archive.get("full_source_policy_runner_package_ready") is False
        and narrowed_repro_code_archive.get("submission_ready") is False
    )
    minimal_submission_code_dependency_boundary = {
        "schema": "minimal-submission-code-dependency-boundary-v1",
        "status": (
            "submission_code_package_ready"
            if minimal_code_ready
            else "narrowed_repro_ready_full_source_policy_package_blocked"
            if local_runner_package_partial_ready and narrowed_repro_code_archive_ready
            else "minimal_submission_code_package_open"
        ),
        "minimal_reproducible_submission_code_ready": minimal_code_ready,
        "local_runner_package_partial_ready": local_runner_package_partial_ready,
        "narrowed_claim_reproducibility_package_ready": narrowed_repro.get(
            "narrowed_claim_reproducibility_package_ready"
        ),
        "narrowed_repro_code_archive_ready": narrowed_repro_code_archive_ready,
        "narrowed_repro_code_archive_submission_ready": narrowed_repro_code_archive.get(
            "submission_ready"
        ),
        "full_source_policy_runner_package_ready": runner_centered.get(
            "full_source_policy_runner_package_ready"
        ),
            "source_policy_closed": source_policy_closed,
            "ra_hi_closeout_status": ra_hi_closeout.get("status"),
            "ra_hi_closeout_source_policy_rows_total": ra_hi_closeout.get("coverage", {}).get(
                "source_policy_rows_total"
            ),
            "ra_hi_closeout_ra_rows": ra_hi_closeout.get("coverage", {}).get("ra2021_rows"),
            "ra_hi_closeout_hi_rows": ra_hi_closeout.get("coverage", {}).get("hi2022_rows"),
            "ra_hi_closeout_ready_command_count": ra_hi_closeout.get("coverage", {}).get("ready_command_count"),
            "ra_hi_closeout_ready_command_mapped_rows": ra_hi_closeout.get("coverage", {}).get(
                "ready_command_mapped_external_rows"
            ),
            "ra_hi_closeout_source_policy_rows_promoted": ra_hi_closeout.get("coverage", {}).get(
                "source_policy_rows_promoted"
            ),
            "ra_hi_closeout_source_policy_rows_completed": ra_hi_closeout.get("coverage", {}).get(
                "source_policy_rows_completed"
            ),
            "ra_hi_closeout_external_superiority_ready_rows": ra_hi_closeout.get("coverage", {}).get(
                "external_superiority_ready_rows"
            ),
            "ra_hi_closeout_opt_in_required": ra_hi_closeout.get("guarded_execution_boundary", {}).get(
                "explicit_user_opt_in_required_before_any_command"
            ),
            "ra_hi_closeout_execution_invoked": ra_hi_closeout.get("guarded_execution_boundary", {}).get(
                "execution_invoked_by_packet"
            ),
            "ra_hi_closeout_b4_can_close": ra_hi_closeout.get("not_promoted_disposition", {}).get(
                "b4_can_close_from_this_checklist"
            ),
            "ra_hi_closeout_b7_can_close": ra_hi_closeout.get("not_promoted_disposition", {}).get(
                "b7_can_close_from_this_checklist"
            ),
            "tfe_runner_closed": tfe_runner_closed,
        "source_policy_rows_closed": b6_local_evidence.get("source_policy_external_rows_closed"),
        "source_policy_rows_total": b6_local_evidence.get("source_policy_external_rows_total"),
        "narrowed_archive_source_policy_rows_closed": narrowed_repro_code_archive.get(
            "source_policy_rows_closed"
        ),
        "narrowed_archive_source_policy_rows_total": narrowed_repro_code_archive.get(
            "source_policy_rows_total"
        ),
        "blocking_objective_requirements": [
            req_id
            for req_id, is_blocked in [
                ("OC4", not source_policy_closed),
                ("OC6", not tfe_runner_closed),
                ("OC12", not minimal_code_ready),
            ]
            if is_blocked
        ],
        "blocking_upstream_gates": [
            "OC4_source_policy_reproduction_rows",
            "OC6_TFE_source_policy_runner",
            "OC12_full_source_policy_runner_archive",
        ],
        "safe_current_package_use": "narrowed_claim_replay_and_audit_provenance_only",
        "primary_submission_package_allowed": False,
    }
    proof_writing_card = proof_claim_traceability.get("proof_writing_boundary_card", {})
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
    proof_claim_remaining_boundary = proof_claim_traceability.get("remaining_claim_boundary", {})
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
    proof_retained_theorem_interface_ids = [
        item_id for item_id in proof_retained_or_open_assumption_ids if item_id != "P7"
    ]
    proof_open_nonpromotion_boundary_ids = [
        item_id for item_id in proof_retained_or_open_assumption_ids if item_id == "P7"
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
    reference_correspondence = strict_proof_policy.get("reference_correspondence_discipline", {})
    reference_main_features = reference_correspondence.get("main_features", {})
    reference_flat_features = reference_correspondence.get("flat_features", {})
    reference_proof_order_correspondence_closed = (
        strict_proof_policy.get("terminology_reconciled") is True
        and reference_correspondence.get("closed") is True
        and reference_main_features.get("formal_table_reference") is True
        and reference_flat_features.get("formal_table_reference") is True
        and reference_main_features.get("caption_nonimport_boundary") is True
        and reference_flat_features.get("caption_nonimport_boundary") is True
        and reference_main_features.get("not_estimate_transfer") is True
        and reference_flat_features.get("not_estimate_transfer") is True
        and reference_main_features.get("constraint_multiplier_interface_split") is True
        and reference_flat_features.get("constraint_multiplier_interface_split") is True
        and reference_main_features.get("not_imported_constraint_multiplier_estimates") is True
        and reference_flat_features.get("not_imported_constraint_multiplier_estimates") is True
        and reference_main_features.get("table_constraint_multiplier_interface_split") is True
        and reference_flat_features.get("table_constraint_multiplier_interface_split") is True
    )
    strict_proof_global_boundaries_retained = (
        expected_global_submission_boundaries
        if proof_writing_card.get("global_submission_boundaries_retained")
        == proof_readiness_boundary.get("global_submission_boundaries_retained")
        == proof_claim_remaining_boundary.get("global_submission_boundaries_retained")
        == proof_claim_summary.get("global_submission_boundaries_retained")
        == expected_global_submission_boundaries
        else []
    )
    strict_direct_pc2_proof_gap_closed = (
        proof_writing_card.get("direct_pc2_proof_gap_closed") is True
        and proof_closure_state.get("direct_pc2_proof_gap_closed") is True
        and proof_closure_state.get("proof_gap_closed") is True
        and proof_claim_closure_state.get("direct_pc2_proof_gap_closed") is True
        and proof_claim_summary.get("direct_pc2_proof_gap_closed") is True
    )
    strict_stage_residual_O_h7_implementation_defect_proved = (
        proof_writing_card.get("stage_residual_O_h7_implementation_defect_proved")
        is True
        and proof_closure_state.get("stage_residual_O_h7_implementation_defect_proved")
        is True
        and proof_claim_closure_state.get(
            "stage_residual_O_h7_implementation_defect_proved"
        )
        is True
        and proof_claim_summary.get("stage_residual_O_h7_implementation_defect_proved")
        is True
    )
    strict_dynamic_symbolic_oracle_complete = any(
        item is True
        for item in [
            proof_writing_card.get("dynamic_symbolic_oracle_complete"),
            proof_closure_state.get("dynamic_symbolic_oracle_complete"),
            proof_claim_closure_state.get("dynamic_symbolic_oracle_complete"),
            proof_claim_summary.get("dynamic_symbolic_oracle_complete"),
        ]
    )
    strict_eta_h_solver_policy_evidence_closed = any(
        item is True
        for item in [
            proof_writing_card.get("eta_h_solver_policy_evidence_closed"),
            proof_theorem_boundary.get("eta_h_solver_policy_evidence_closed"),
            proof_closure_state.get("eta_h_O_h7_solver_policy_evidence"),
            proof_solver_state.get("eta_h_O_h7_solver_policy_evidence"),
            proof_claim_theorem_traceability.get("eta_h_solver_policy_evidence_closed"),
            proof_claim_remaining_boundary.get("eta_h_solver_policy_evidence_closed"),
        ]
    )
    strict_fixed_tolerance_runs_are_asymptotic_proof = any(
        item is True
        for item in [
            proof_writing_card.get("fixed_tolerance_runs_are_asymptotic_proof"),
            proof_theorem_boundary.get("fixed_tolerance_runs_are_asymptotic_proof"),
            proof_closure_state.get("fixed_tolerance_runs_are_asymptotic_proof"),
            proof_claim_theorem_traceability.get(
                "fixed_tolerance_runs_are_asymptotic_proof"
            ),
        ]
    )
    strict_residual_to_error_route_promoted = any(
        item is True
        for item in [
            proof_writing_card.get("residual_to_error_route_promoted"),
            proof_residual_policy.get("accepted_residual_to_error_theorem"),
            proof_claim_remaining_boundary.get("residual_to_error_route_promoted"),
            proof_claim_summary.get("residual_to_error_route_promoted"),
        ]
    )
    strict_source_policy_or_full_tfe_not_promoted = (
        proof_writing_card.get("source_policy_or_full_tfe_not_promoted") is True
        and proof_theorem_boundary.get("does_not_promote_source_policy_or_full_tfe")
        is True
        and proof_claim_theorem_traceability.get(
            "source_policy_or_full_tfe_not_promoted"
        )
        is True
        and proof_claim_remaining_boundary.get("source_policy_or_full_tfe_not_promoted")
        is True
    )
    strict_theorem_assumption_partition_boundary_present = (
        proof_writing_card.get("theorem_assumption_anchor_ids")
        == proof_manuscript_traceability.get("theorem_assumption_anchor_ids")
        == proof_claim_remaining_boundary.get("theorem_assumption_anchor_ids")
        == proof_theorem_assumption_anchor_ids
        == expected_theorem_assumption_anchor_ids
        and proof_submission_satisfied_assumption_ids
        == proof_claim_remaining_boundary.get("submission_satisfied_ids")
        == proof_claim_summary.get("theorem_assumption_submission_satisfied_ids")
        == expected_submission_satisfied_assumption_ids
        and proof_retained_or_open_assumption_ids
        == proof_claim_remaining_boundary.get("retained_or_open_ids")
        == proof_claim_summary.get("theorem_assumption_retained_or_open_ids")
        == expected_retained_or_open_assumption_ids
        and proof_claim_remaining_boundary.get("theorem_assumptions_total")
        == proof_claim_summary.get("theorem_assumptions_total")
        == len(expected_theorem_assumption_anchor_ids)
        and proof_claim_remaining_boundary.get("submission_satisfied_count")
        == proof_claim_summary.get("theorem_assumptions_submission_satisfied")
        == len(expected_submission_satisfied_assumption_ids)
        and proof_claim_remaining_boundary.get("retained_or_open_count")
        == proof_claim_summary.get("theorem_assumptions_retained_or_open")
        == len(expected_retained_or_open_assumption_ids)
        and proof_retained_theorem_interface_ids
        == proof_claim_remaining_boundary.get("retained_theorem_interface_ids")
        == proof_claim_summary.get("theorem_assumption_retained_theorem_interface_ids")
        == expected_retained_theorem_interface_ids
        and proof_open_nonpromotion_boundary_ids
        == proof_claim_remaining_boundary.get("open_nonpromotion_boundary_ids")
        == proof_claim_summary.get("theorem_assumption_open_nonpromotion_boundary_ids")
        == expected_open_nonpromotion_boundary_ids
        and proof_claim_remaining_boundary.get("retained_theorem_interface_count")
        == proof_claim_summary.get("theorem_assumptions_retained_theorem_interfaces")
        == len(expected_retained_theorem_interface_ids)
        and proof_claim_remaining_boundary.get("open_nonpromotion_boundary_count")
        == proof_claim_summary.get("theorem_assumptions_open_nonpromotion_boundaries")
        == len(expected_open_nonpromotion_boundary_ids)
    )
    strict_safe_reader_claim_boundary_present = (
        proof_writing_card.get("safe_reader_claim")
        == proof_claim_summary.get("proof_writing_boundary_card_safe_reader_claim")
        == expected_safe_reader_claim
        and strict_theorem_assumption_partition_boundary_present
    )
    strict_reading_rule_boundary_present = (
        proof_claim_remaining_boundary.get("reading_rule") == expected_proof_reading_rule
        and strict_safe_reader_claim_boundary_present
        and strict_source_policy_or_full_tfe_not_promoted
        and not strict_eta_h_solver_policy_evidence_closed
        and not strict_residual_to_error_route_promoted
        and not strict_fixed_tolerance_runs_are_asymptotic_proof
    )
    forbidden_unconditional_theorem_boundary_present = (
        proof_writing_card.get("forbidden_reader_claims") == expected_forbidden_reader_claims
        and proof_theorem_boundary.get("conditional_theorem_boundary_present_main_and_flat")
        is True
        and strict_theorem_assumption_partition_boundary_present
        and proof_claim_traceability.get("submission_ready") is False
    )
    forbidden_eta_h_solver_policy_claim_boundary_present = (
        proof_writing_card.get("forbidden_reader_claims") == expected_forbidden_reader_claims
        and not strict_eta_h_solver_policy_evidence_closed
        and proof_theorem_boundary.get("eta_h_theorem_condition_retained") is True
    )
    forbidden_fixed_tolerance_asymptotic_claim_boundary_present = (
        proof_writing_card.get("forbidden_reader_claims") == expected_forbidden_reader_claims
        and not strict_fixed_tolerance_runs_are_asymptotic_proof
    )
    strict_residual_to_error_not_promoted = (
        not strict_residual_to_error_route_promoted
        and proof_residual_policy.get("accepted_residual_to_error_theorem") is False
        and proof_residual_policy.get("residual_promotion_not_made") is True
    )
    forbidden_residual_to_error_theorem_claim_boundary_present = (
        proof_writing_card.get("forbidden_reader_claims") == expected_forbidden_reader_claims
        and strict_residual_to_error_not_promoted
    )
    strict_source_policy_full_tfe_not_promoted = (
        strict_source_policy_or_full_tfe_not_promoted
        and not source_policy_closed
        and not tfe_runner_closed
        and not minimal_code_ready
        and runner_centered.get("full_source_policy_runner_package_ready") is False
    )
    forbidden_source_policy_full_tfe_package_claim_boundary_present = (
        proof_writing_card.get("forbidden_reader_claims") == expected_forbidden_reader_claims
        and strict_source_policy_full_tfe_not_promoted
    )
    strict_forbidden_reader_claims_boundary_present = all(
        [
            forbidden_unconditional_theorem_boundary_present,
            forbidden_eta_h_solver_policy_claim_boundary_present,
            forbidden_fixed_tolerance_asymptotic_claim_boundary_present,
            forbidden_residual_to_error_theorem_claim_boundary_present,
            forbidden_source_policy_full_tfe_package_claim_boundary_present,
        ]
    )
    strict_proof_writing_submission_boundary = {
        "schema": "strict-proof-writing-submission-boundary-v1",
        "status": "proof_writing_traceable_global_submission_blocked_by_source_policy_tfe_package",
        "proof_writing_card_status": proof_writing_card.get("status"),
        "safe_reader_claim": proof_writing_card.get("safe_reader_claim"),
        "safe_reader_claim_boundary_present": strict_safe_reader_claim_boundary_present,
        "reading_rule_boundary_present": strict_reading_rule_boundary_present,
        "forbidden_reader_claims": (
            expected_forbidden_reader_claims
            if strict_forbidden_reader_claims_boundary_present
            else proof_writing_card.get("forbidden_reader_claims")
        ),
        "forbidden_reader_claims_boundary_present": (
            strict_forbidden_reader_claims_boundary_present
        ),
        "forbidden_unconditional_theorem_boundary_present": (
            forbidden_unconditional_theorem_boundary_present
        ),
        "forbidden_eta_h_solver_policy_claim_boundary_present": (
            forbidden_eta_h_solver_policy_claim_boundary_present
        ),
        "forbidden_fixed_tolerance_asymptotic_claim_boundary_present": (
            forbidden_fixed_tolerance_asymptotic_claim_boundary_present
        ),
        "forbidden_residual_to_error_theorem_claim_boundary_present": (
            forbidden_residual_to_error_theorem_claim_boundary_present
        ),
        "forbidden_source_policy_full_tfe_package_claim_boundary_present": (
            forbidden_source_policy_full_tfe_package_claim_boundary_present
        ),
        "accepted_theorem_label": proof_writing_card.get("accepted_theorem_label"),
        "accepted_method_order": proof_writing_card.get("accepted_method_order"),
        "accepted_local_defect_order": proof_writing_card.get("accepted_local_defect_order"),
        "theorem_assumption_partition_boundary_present": (
            strict_theorem_assumption_partition_boundary_present
        ),
        "theorem_assumption_anchor_ids": (
            expected_theorem_assumption_anchor_ids
            if strict_theorem_assumption_partition_boundary_present
            else []
        ),
        "theorem_assumption_anchor_count": (
            len(expected_theorem_assumption_anchor_ids)
            if strict_theorem_assumption_partition_boundary_present
            else 0
        ),
        "theorem_assumption_submission_satisfied_ids": (
            expected_submission_satisfied_assumption_ids
            if strict_theorem_assumption_partition_boundary_present
            else []
        ),
        "theorem_assumption_submission_satisfied_count": (
            len(expected_submission_satisfied_assumption_ids)
            if strict_theorem_assumption_partition_boundary_present
            else 0
        ),
        "theorem_assumption_retained_or_open_ids": (
            expected_retained_or_open_assumption_ids
            if strict_theorem_assumption_partition_boundary_present
            else []
        ),
        "theorem_assumption_retained_or_open_count": (
            len(expected_retained_or_open_assumption_ids)
            if strict_theorem_assumption_partition_boundary_present
            else 0
        ),
        "theorem_assumption_retained_theorem_interface_ids": (
            expected_retained_theorem_interface_ids
            if strict_theorem_assumption_partition_boundary_present
            else []
        ),
        "theorem_assumption_retained_theorem_interface_count": (
            len(expected_retained_theorem_interface_ids)
            if strict_theorem_assumption_partition_boundary_present
            else 0
        ),
        "theorem_assumption_open_nonpromotion_boundary_ids": (
            expected_open_nonpromotion_boundary_ids
            if strict_theorem_assumption_partition_boundary_present
            else []
        ),
        "theorem_assumption_open_nonpromotion_boundary_count": (
            len(expected_open_nonpromotion_boundary_ids)
            if strict_theorem_assumption_partition_boundary_present
            else 0
        ),
        "proof_claim_traceability_submission_ready": proof_claim_traceability.get("submission_ready"),
        "reader_facing_manuscript_boundary_present": proof_writing_card.get(
            "reader_facing_manuscript_boundary_present"
        )
        and proof.get("theorem_statement_boundary", {}).get(
            "all_required_labels_present_main_and_flat"
        )
        and proof.get("theorem_statement_boundary", {}).get(
            "conditional_theorem_boundary_present_main_and_flat"
        )
        and proof.get("manuscript_traceability", {}).get(
            "conditional_proof_claims_mapped_to_manuscript"
        ),
        "p7_retained_nonpromotion_boundary_present": proof_writing_card.get(
            "p7_retained_nonpromotion_boundary_present"
        )
        and proof.get("theorem_statement_boundary", {}).get(
            "does_not_promote_residual_to_error"
        )
        and proof.get("manuscript_traceability", {}).get(
            "residual_to_error_nonpromotion_present_main_and_flat"
        )
        and proof.get("p7_residual_to_error_obligation_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        ),
        "b1_closure_scope_boundary_present": proof_writing_card.get(
            "b1_closure_scope_boundary_present"
        )
        and proof.get("b1_ad_expanded_closure_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        ),
        "b1_ad_expanded_closure_ledger_present": proof.get(
            "b1_ad_expanded_closure_ledger_boundary", {}
        ).get("all_tokens_present_main_and_flat"),
        "b1_ad_expanded_symbolic_oracle_closed_rows": proof.get(
            "evidence_summary", {}
        ).get("b1_ad_expanded_symbolic_oracle_closed_rows"),
        "b1_ad_expanded_symbolic_oracle_closed_cells": proof.get(
            "evidence_summary", {}
        ).get("b1_ad_expanded_symbolic_oracle_closed_cells"),
        "p6_solver_scope_boundary_present": proof_writing_card.get(
            "p6_solver_scope_boundary_present"
        )
        and proof.get("p6_solver_scope_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        ),
        "p1p2_compact_tube_boundary_present": proof_writing_card.get(
            "p1p2_compact_tube_boundary_present"
        )
        and proof.get("p1p2_compact_tube_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        ),
        "p3p4_implementation_boundary_present": proof_writing_card.get(
            "p3p4_implementation_boundary_present"
        )
        and proof.get("p3p4_implementation_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        ),
        "p5_direct_route_boundary_present": proof_writing_card.get(
            "p5_direct_route_boundary_present"
        )
        and proof.get("p5_direct_route_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        ),
        "proof_causality_ledger_present": proof_writing_card.get(
            "proof_causality_ledger_present"
        )
        and proof.get("proof_causality_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        ),
        "direct_route_anticircularity_ledger_present": proof_writing_card.get(
            "direct_route_anticircularity_ledger_present"
        )
        and proof.get("direct_route_anticircularity_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        ),
        "p_interface_satisfaction_ledger_present": proof_writing_card.get(
            "p_interface_satisfaction_ledger_present"
        )
        and proof.get("p_interface_satisfaction_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        ),
        "p7_residual_to_error_ledger_present": proof_writing_card.get(
            "p7_residual_to_error_ledger_present"
        )
        and proof.get("p7_residual_to_error_obligation_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        ),
        "theorem_use_rule_present": proof_writing_card.get("theorem_use_rule_present")
        and proof.get("theorem_use_rule_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        ),
        "quantifier_domain_ledger_present": proof_writing_card.get(
            "quantifier_domain_ledger_present"
        )
        and proof.get("quantifier_domain_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        ),
        "local_global_transfer_ledger_present": proof_writing_card.get(
            "local_global_transfer_ledger_present"
        )
        and proof.get("local_global_transfer_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        ),
        "objective_completion_boundary_present": proof_writing_card.get(
            "objective_completion_boundary_present"
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
        "constant_dependency_ledger_present": proof_writing_card.get(
            "constant_dependency_ledger_present"
        )
        and proof.get("constant_dependency_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        ),
        "theorem_dependency_consumption_ledger_present": proof_writing_card.get(
            "theorem_dependency_consumption_ledger_present"
        )
        and proof.get("theorem_dependency_consumption_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        ),
        "branch_consistency_ledger_present": proof_writing_card.get(
            "branch_consistency_ledger_present"
        )
        and proof.get("branch_consistency_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        ),
        "implementation_route_oracle_ledger_present": proof_writing_card.get(
            "implementation_route_oracle_ledger_present"
        )
        and proof.get("implementation_route_oracle_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        ),
        "nonlinear_solver_scale_ledger_present": proof_writing_card.get(
            "nonlinear_solver_scale_ledger_present"
        )
        and proof.get("nonlinear_solver_scale_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        ),
        "local_defect_decomposition_ledger_present": proof_writing_card.get(
            "local_defect_decomposition_ledger_present"
        )
        and proof.get("local_defect_decomposition_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        ),
        "theorem_output_scope_ledger_present": proof_writing_card.get(
            "theorem_output_scope_ledger_present"
        )
        and proof.get("theorem_output_scope_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        ),
        "reporting_map_ledger_present": proof_writing_card.get(
            "reporting_map_ledger_present"
        )
        and proof.get("reporting_map_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        ),
        "reference_proof_order_correspondence_closed": (
            reference_proof_order_correspondence_closed
        ),
        "reference_proof_order_correspondence_role": reference_correspondence.get("role"),
        "reference_proof_order_source_text": strict_proof_policy.get(
            "source_paper_style_read", {}
        ).get("reference_text"),
        "reference_proof_order_no_estimate_transfer": (
            reference_main_features.get("not_estimate_transfer") is True
            and reference_flat_features.get("not_estimate_transfer") is True
        ),
        "reference_proof_order_nonimport_boundary": (
            reference_main_features.get("caption_nonimport_boundary") is True
            and reference_flat_features.get("caption_nonimport_boundary") is True
        ),
        "reference_proof_order_constraint_multiplier_split": (
            reference_main_features.get("constraint_multiplier_interface_split") is True
            and reference_flat_features.get("constraint_multiplier_interface_split") is True
            and reference_main_features.get("table_constraint_multiplier_interface_split") is True
            and reference_flat_features.get("table_constraint_multiplier_interface_split") is True
        ),
        "direct_pc2_proof_gap_closed": strict_direct_pc2_proof_gap_closed,
        "stage_residual_O_h7_implementation_defect_proved": (
            strict_stage_residual_O_h7_implementation_defect_proved
        ),
        "dynamic_symbolic_oracle_complete": strict_dynamic_symbolic_oracle_complete,
        "eta_h_solver_policy_evidence_closed": (
            strict_eta_h_solver_policy_evidence_closed
        ),
        "fixed_tolerance_runs_are_asymptotic_proof": (
            strict_fixed_tolerance_runs_are_asymptotic_proof
        ),
        "residual_to_error_route_promoted": strict_residual_to_error_route_promoted,
        "residual_to_error_not_promoted": strict_residual_to_error_not_promoted,
        "source_policy_or_full_tfe_not_promoted": (
            strict_source_policy_or_full_tfe_not_promoted
        ),
        "source_policy_full_tfe_not_promoted": (
            strict_source_policy_full_tfe_not_promoted
        ),
        "proof_global_boundaries_retained": strict_proof_global_boundaries_retained,
        "satisfied_close_requirement_ids": proof_satisfied_close_requirement_ids,
        "unsatisfied_close_requirement_ids": proof_unsatisfied_close_requirement_ids,
        "objective_blockers_retained": minimal_submission_code_dependency_boundary[
            "blocking_objective_requirements"
        ],
        "source_policy_closed": source_policy_closed,
        "tfe_runner_closed": tfe_runner_closed,
        "minimal_code_ready": minimal_code_ready,
        "minimal_reproducible_submission_code_ready": minimal_code_ready,
        "full_source_policy_runner_package_ready": runner_centered.get(
            "full_source_policy_runner_package_ready"
        ),
        "package_boundary_status": minimal_submission_code_dependency_boundary["status"],
        "package_safe_current_use": minimal_submission_code_dependency_boundary["safe_current_package_use"],
        "primary_submission_package_allowed": minimal_submission_code_dependency_boundary[
            "primary_submission_package_allowed"
        ],
        "submission_ready": False,
        "can_mark_goal_complete": False,
        "evidence_sources": [
            "PROOF_CLAIM_TRACEABILITY_AUDIT.json",
            "PROOF_CLOSURE_MANIFEST.json",
            "CMAME_RUNNER_CENTERED_REPRODUCIBILITY_AUDIT.json",
            "CMAME_NARROWED_REPRO_CODE_ARCHIVE_MANIFEST.json",
            "B6_FOUR_EXAMPLE_LOCAL_EVIDENCE_SUMMARY.json",
            "CMAME_STRICT_PROOF_POLICY_RECONCILIATION_AUDIT.json",
        ],
    }

    requirements = [
        req(
            "OC1",
            "Confirm the complete four-example result matrix for the paper.",
            "satisfied" if core_matrix_ready else "open",
            ["PAPER_NUMERICAL_RESULT_MATRIX.json"],
            not core_matrix_ready,
            {
                "row_count": matrix.get("row_count"),
                "expected_row_count": matrix.get("expected_row_count"),
                "raw_row_count": matrix.get("raw_row_count"),
                "method_count": matrix.get("method_count"),
                "examples": sorted(examples),
            },
            "restore a 44-cell, 132-raw-row, 11-method matrix over the four examples",
        ),
        req(
            "OC2",
            "Trace the confirmed result matrix into the manuscript and PDF.",
            "satisfied" if traceability_ready else "open",
            ["RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.json"],
            not traceability_ready,
            traceability.get("coverage", {}),
            "make all 44 velocity cells trace to main/flat TeX and PDF text",
        ),
        req(
            "OC3",
            "Keep the bounded common-reference comparison closed without overclaiming external superiority.",
            "satisfied" if common_reference_closed else "open",
            ["PAPER_NUMERICAL_RESULT_MATRIX.json", "COMMON_REFERENCE_ORDER_RECOMPUTATION_AUDIT.json"],
            not common_reference_closed,
            {
                "order_wins": matrix.get("direct_nonlocal_velocity_order_wins"),
                "order_comparisons": matrix.get("direct_nonlocal_velocity_order_comparisons"),
                "error_wins": matrix.get("direct_nonlocal_velocity_error_wins"),
                "error_comparisons": matrix.get("direct_nonlocal_velocity_error_comparisons"),
                "source_policy_external_superiority_allowed": matrix.get(
                    "source_policy_external_superiority_allowed"
                ),
            },
            "fix the common-reference matrix or keep the claim boundary demoted",
        ),
        req(
            "OC4",
            "Close apples-to-apples external source-policy reproduction rows.",
            "open" if not source_policy_closed else "satisfied",
            [
                "EXTERNAL_SOURCE_POLICY_CLOSURE_MANIFEST.json",
                "RA_HI_SOURCE_POLICY_CLOSEOUT_CHECKLIST.json",
                "RA_HI_SOURCE_POLICY_PROMOTION_BLOCKER_MATRIX.json",
                "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json",
                "B4_GUARDED_DRIVER_REFUSAL_BOUNDARY_AUDIT_20260621.json",
                "FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.json",
            ],
            not source_policy_closed,
            {
                "source_policy_reproduction": source_policy.get("source_policy_reproduction"),
                "same_test_campaign_status": source_policy.get("same_test_campaign_status"),
                "external_superiority_claim_allowed": source_policy.get("external_superiority_claim_allowed"),
                "performance_matrix": source_policy.get("performance_matrix"),
                "ra_hi_closeout_status": ra_hi_closeout.get("status"),
                "ra_hi_closeout_source_policy_rows_total": ra_hi_closeout.get("coverage", {}).get(
                    "source_policy_rows_total"
                ),
                "ra_hi_closeout_ra_rows": ra_hi_closeout.get("coverage", {}).get("ra2021_rows"),
                "ra_hi_closeout_hi_rows": ra_hi_closeout.get("coverage", {}).get("hi2022_rows"),
                "ra_hi_closeout_ready_command_count": ra_hi_closeout.get("coverage", {}).get("ready_command_count"),
                "ra_hi_closeout_ready_command_mapped_rows": ra_hi_closeout.get("coverage", {}).get(
                    "ready_command_mapped_external_rows"
                ),
                "ra_hi_closeout_source_policy_rows_promoted": ra_hi_closeout.get("coverage", {}).get(
                    "source_policy_rows_promoted"
                ),
                "ra_hi_closeout_source_policy_rows_completed": ra_hi_closeout.get("coverage", {}).get(
                    "source_policy_rows_completed"
                ),
                "ra_hi_closeout_external_superiority_ready_rows": ra_hi_closeout.get("coverage", {}).get(
                    "external_superiority_ready_rows"
                ),
                "ra_hi_closeout_opt_in_required": ra_hi_closeout.get("guarded_execution_boundary", {}).get(
                    "explicit_user_opt_in_required_before_any_command"
                ),
                "ra_hi_closeout_exact_approval_statement": ra_hi_closeout.get(
                    "guarded_execution_boundary", {}
                ).get("exact_required_user_approval_statement"),
                "ra_hi_closeout_execution_invoked": ra_hi_closeout.get("guarded_execution_boundary", {}).get(
                    "execution_invoked_by_packet"
                ),
                "ra_hi_closeout_b4_can_close": ra_hi_closeout.get("not_promoted_disposition", {}).get(
                    "b4_can_close_from_this_checklist"
                ),
                "ra_hi_closeout_b7_can_close": ra_hi_closeout.get("not_promoted_disposition", {}).get(
                    "b7_can_close_from_this_checklist"
                ),
                "ra_hi_current_evidence_terminal_not_promotable_rows": ra_hi_promotion_matrix.get(
                    "current_evidence_terminal_not_promotable_rows"
                ),
                "ra_hi_future_promotion_requires_authorized_execution_or_new_artifact_rows": (
                    ra_hi_promotion_matrix.get(
                        "future_promotion_requires_authorized_execution_or_new_artifact_rows"
                    )
                ),
                "ra_hi_source_policy_reproduction_complete_rows": ra_hi_promotion_matrix.get(
                    "source_policy_reproduction_complete_rows"
                ),
                "source_policy_execution_handoff_status": b4_execution_handoff.get("status"),
                "source_policy_execution_handoff_authorized": b4_execution_handoff.get(
                    "execution_authorized"
                ),
                "source_policy_execution_handoff_commands_not_run": b4_execution_handoff.get(
                    "commands_not_run_by_handoff"
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
                "source_policy_execution_handoff_ready_command_count": b4_execution_handoff.get(
                    "ready_command_count"
                ),
                "source_policy_execution_handoff_ready_command_mapped_rows": b4_execution_handoff.get(
                    "ready_command_mapped_external_rows"
                ),
                "source_policy_execution_handoff_opt_in_required_command_count": b4_execution_handoff.get(
                    "opt_in_required_command_count"
                ),
                "source_policy_execution_handoff_opt_in_required_mapped_rows": b4_execution_handoff.get(
                    "opt_in_required_mapped_external_rows"
                ),
                "source_policy_execution_handoff_terminal_unable_rows": b4_execution_handoff.get(
                    "terminal_unable_to_reproduce_rows"
                ),
                "b4_guarded_driver_refusal_boundary_20260621_status": b4_guarded_refusal.get(
                    "status"
                ),
                "b4_guarded_driver_no_opt_in_refusal_proved_static": b4_guarded_refusal.get(
                    "no_opt_in_refusal_proved_static"
                ),
                "b4_guarded_driver_wrong_approval_refusal_proved_static": b4_guarded_refusal.get(
                    "wrong_approval_refusal_proved_static"
                ),
                "b4_guarded_driver_refusal_exit_code": b4_guarded_refusal.get(
                    "refusal_exit_code"
                ),
                "b4_guarded_driver_pre_guard_command_count": b4_guarded_refusal.get(
                    "pre_guard_command_count"
                ),
                "b4_guarded_driver_post_guard_source_policy_command_count": b4_guarded_refusal.get(
                    "post_guard_source_policy_command_count"
                ),
                "b4_guarded_driver_invoked_by_audit": b4_guarded_refusal.get(
                    "driver_invoked_by_audit"
                ),
                "b4_guarded_driver_source_policy_execution_invoked": b4_guarded_refusal.get(
                    "source_policy_execution_invoked"
                ),
                "b4_guarded_driver_submission_ready": b4_guarded_refusal.get(
                    "submission_ready"
                ),
                "b4_guarded_driver_refusal_boundary_marker": b4_guarded_refusal.get(
                    "marker"
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
                "full_source_policy_row_provenance_status": full_source_policy_row_provenance.get(
                    "status"
                ),
                "full_source_policy_row_provenance_rows": full_source_policy_row_provenance.get(
                    "row_count"
                ),
                "full_source_policy_row_provenance_preflight": full_source_policy_row_provenance.get(
                    "provenance_preflight"
                ),
                "full_source_policy_row_provenance_source_policy_closed": (
                    full_source_policy_row_provenance.get("source_policy_closed")
                ),
                "full_source_policy_row_provenance_source_policy_closed_ratio": (
                    full_source_policy_row_provenance.get("source_policy_closed_ratio")
                ),
                "full_source_policy_row_provenance_promotion_ready_rows": (
                    full_source_policy_row_provenance.get("promotion_ready_rows")
                ),
                "full_source_policy_row_provenance_handoff_status": full_source_policy_row_provenance.get(
                    "source_policy_execution_handoff", {}
                ).get("status"),
                "full_source_policy_row_provenance_handoff_authorized": full_source_policy_row_provenance.get(
                    "source_policy_execution_handoff", {}
                ).get("execution_authorized"),
                "full_source_policy_row_provenance_handoff_commands_not_run": full_source_policy_row_provenance.get(
                    "source_policy_execution_handoff", {}
                ).get("commands_not_run_by_handoff"),
                "full_source_policy_row_provenance_handoff_driver": full_source_policy_row_provenance.get(
                    "source_policy_execution_handoff", {}
                ).get("guarded_execution_driver"),
                "full_source_policy_row_provenance_handoff_driver_does_not_authorize": full_source_policy_row_provenance.get(
                    "source_policy_execution_handoff", {}
                ).get("driver_does_not_authorize_execution"),
                "full_source_policy_row_provenance_handoff_opt_in_commands": full_source_policy_row_provenance.get(
                    "source_policy_execution_handoff", {}
                ).get("opt_in_required_command_count"),
                "full_source_policy_row_provenance_handoff_mapped_rows": full_source_policy_row_provenance.get(
                    "source_policy_execution_handoff", {}
                ).get("opt_in_required_mapped_external_rows"),
            },
            (
                "RA/HI can only close through exact B4 opt-in authorized closeout or a new "
                "source-policy promotion artifact; TFE/VP remain unable-to-reproduce/not-promoted"
            ),
        ),
        req(
            "OC5",
            "Close the active B2 source-policy suites for original TFE, RA2021, and HI2022.",
            "satisfied" if b2_active_suites_closed else "open",
            ["B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.json", "EXTERNAL_SUITE_DEMOTION_LEDGER.json"],
            not b2_active_suites_closed,
            {
                "source_policy_closed_rows": b2_remaining.get("source_policy_closed_rows"),
                "b2_source_policy_rows_closed": b2_source_policy_rows_closed,
                "b2_can_close_now": b2_remaining.get("b2_can_close_now"),
                "b2_active_suites_closed_by_demotion": b2_active_suites_closed_by_demotion,
                "active_flagged_rows": b2_remaining.get("active_flagged_row_count"),
                "remaining_requirements": b2_remaining.get("b2_remaining_requirements"),
                "demoted_flagged_rows": b2_remaining.get("demoted_flagged_row_count"),
                "demoted_suite_counts": b2_remaining.get("demoted_suite_counts"),
                "external_superiority_claim_allowed": b2_remaining.get("external_superiority_claim_allowed"),
                "demotion_ledger_status": external_demotion.get("status"),
                "demotion_ledger_remaining_open_suites": external_demotion.get("remaining_open_suites"),
            },
            (
                "closed by Route-B demotion; source-policy rows remain 0 and external-superiority stays forbidden"
                if b2_active_suites_closed
                else "complete or explicitly demote original TFE, RA2021, and HI2022 same-test source-policy rows"
            ),
        ),
        req(
            "OC6",
            "Implement the original TFE pendulum source-policy runner beyond the parameter smoke layer.",
            "partial" if not tfe_runner_closed else "satisfied",
            [
                "TFE_SOURCE_PENDULUM_MODEL_AUDIT.json",
                "TFE_DAE_RUNNER_CONTRACT_GAP_AUDIT.json",
                "TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.json",
                "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.json",
                "OC6_EXTERNAL_SOURCE_ARTIFACT_RECHECK_20260621.json",
                "OC6_TFE_PUBLISHER_ARTIFACT_AVAILABILITY_AUDIT_20260621.json",
                "OC6_TFE_SOURCE_EQUIVALENT_ARTIFACT_REQUEST_PACKET_20260621.json",
                "SOURCE_POLICY_REOPEN_CONDITION_MONITOR_20260620.json",
                "TFE_RUNNER_CONTRACT_PREFLIGHT_CERTIFICATE.json",
            ],
            not tfe_runner_closed,
            {
                "tfe_dae_runner_contract_gap_status": tfe_dae_gap.get("status"),
                "tfe_dae_runner_contract_gap_missing_block_count": tfe_dae_gap.get(
                    "missing_contract_block_count"
                ),
                "tfe_dae_runner_contract_gap_missing_block_ids": tfe_dae_missing_block_ids,
                "tfe_dae_runner_contract_gap_nonheavy_blocks": tfe_dae_gap.get(
                    "nonheavy_missing_contract_blocks"
                ),
                "tfe_dae_runner_contract_gap_nonheavy_disposition_ids": tfe_dae_nonheavy_disposition_ids,
                "tfe_dae_runner_contract_gap_nonheavy_dispositioned_by_demotion": tfe_dae_gap.get(
                    "nonheavy_missing_contract_blocks_dispositioned_by_demotion"
                ),
                "tfe_dae_runner_contract_gap_nonheavy_demotion_does_not_close_source_policy": tfe_dae_gap.get(
                    "nonheavy_demotion_does_not_close_source_policy"
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
                "tfe_dae_runner_contract_gap_execution_block_count": tfe_dae_gap.get(
                    "source_policy_execution_missing_contract_block_count"
                ),
                "tfe_dae_runner_contract_gap_candidate_backed_non_equivalent_runner_blocks": (
                    tfe_dae_gap.get("candidate_backed_non_equivalent_runner_block_ids")
                ),
                "tfe_dae_runner_contract_gap_candidate_backed_non_equivalent_runner_block_count": (
                    tfe_dae_gap.get("candidate_backed_non_equivalent_runner_block_count")
                ),
                "tfe_dae_runner_contract_gap_ready_to_execute_source_policy_now": tfe_dae_gap.get(
                    "ready_to_execute_source_policy_now"
                ),
                "tfe_dae_runner_contract_gap_heavy_run_invoked": tfe_dae_gap.get(
                    "heavy_numerical_run_invoked"
                ),
                "tfe_source_policy_execution_preflight_status": tfe_execution_preflight.get("status"),
                "tfe_source_policy_execution_preflight_current_route": tfe_execution_preflight.get(
                    "current_route"
                ),
                "tfe_source_policy_execution_preflight_reopen_condition": tfe_execution_preflight.get(
                    "reopen_condition"
                ),
                "tfe_source_policy_execution_preflight_opt_in_required": tfe_execution_preflight.get(
                    "explicit_user_opt_in_required"
                ),
                "tfe_source_policy_execution_preflight_nonheavy_dispositioned": (
                    tfe_execution_preflight.get("nonheavy_blocks_dispositioned_by_demotion")
                ),
                "tfe_source_policy_execution_preflight_execution_block_count": (
                    tfe_execution_preflight.get("execution_block_count")
                ),
                "tfe_source_policy_execution_preflight_can_promote_rows_now": (
                    tfe_execution_preflight.get("can_promote_any_tfe_source_policy_row_now")
                ),
                "tfe_source_policy_execution_preflight_ready_now": tfe_execution_preflight.get(
                    "ready_to_execute_source_policy_now"
                ),
                "tfe_self_reproduction_status": tfe_self_reproduction.get("status"),
                "tfe_self_reproduction_attempted_not_reproducible_rows": (
                    tfe_self_reproduction.get("attempted_not_reproducible_rows")
                ),
                "tfe_self_reproduction_unable_to_reproduce_rows": (
                    tfe_self_reproduction.get("unable_to_reproduce_rows")
                ),
                "tfe_self_reproduction_source_policy_closed": tfe_self_reproduction.get(
                    "source_policy_closed"
                ),
                "tfe_self_reproduction_source_policy_closed_ratio": tfe_self_reproduction.get(
                    "source_policy_closed_ratio"
                ),
                "tfe_self_reproduction_source_policy_closed_rows": tfe_self_reproduction.get(
                    "source_policy_closed_rows"
                ),
                "tfe_self_reproduction_public_code_recheck_status": tfe_self_reproduction.get(
                    "public_code_recheck_status"
                ),
                "tfe_self_reproduction_reopen_condition": tfe_self_reproduction.get(
                    "reopen_condition"
                ),
                "tfe_self_reproduction_preflight_status": tfe_self_reproduction.get(
                    "source_policy_execution_preflight_status"
                ),
                "tfe_self_reproduction_preflight_ready_now": tfe_self_reproduction.get(
                    "source_policy_execution_preflight_ready_now"
                ),
                "tfe_self_reproduction_preflight_can_promote_rows_now": tfe_self_reproduction.get(
                    "source_policy_execution_preflight_can_promote_rows_now"
                ),
                "tfe_public_code_refresh_20260620_status": source_policy_public_code_refresh.get(
                    "status"
                ),
                "tfe_public_code_refresh_20260620_rows": source_policy_public_code_refresh.get(
                    "rows"
                ),
                "tfe_public_code_refresh_20260620_current_queries": (
                    source_policy_public_code_refresh.get("current_queries")
                ),
                "tfe_public_code_refresh_20260620_positive_artifact_rows": (
                    source_policy_public_code_refresh.get("positive_public_code_artifact_rows")
                ),
                "tfe_public_code_refresh_20260620_source_policy_closed": (
                    source_policy_public_code_refresh.get("source_policy_closed")
                ),
                "tfe_public_code_refresh_20260620_source_policy_closed_ratio": (
                    source_policy_public_code_refresh.get("source_policy_closed_ratio")
                ),
                "tfe_public_code_refresh_20260620_latest_external_probe_date": (
                    source_policy_public_code_refresh.get("latest_external_probe_date_checked")
                ),
                "tfe_public_code_refresh_20260620_latest_external_probe_count": (
                    source_policy_public_code_refresh.get("latest_external_probe_count")
                ),
                "tfe_public_code_refresh_20260620_latest_external_probe_positive_artifact_rows": (
                    source_policy_public_code_refresh.get(
                        "latest_external_probe_positive_public_code_artifact_rows"
                    )
                ),
                "tfe_public_code_refresh_20260620_latest_external_probe_source_policy_rows_closed": (
                    source_policy_public_code_refresh.get(
                        "latest_external_probe_source_policy_rows_closed"
                    )
                ),
                "tfe_public_code_refresh_20260620_latest_external_probe_access_limited_count": (
                    source_policy_public_code_refresh.get(
                        "latest_external_probe_access_limited_count"
                    )
                ),
                "tfe_public_code_refresh_20260620_latest_external_probe_global_absence_proved": (
                    source_policy_public_code_refresh.get(
                        "latest_external_probe_global_absence_proved"
                    )
                ),
                "tfe_public_code_refresh_20260620_latest_external_probe_reopen_triggered": (
                    source_policy_public_code_refresh.get(
                        "latest_external_probe_source_policy_reopen_triggered"
                    )
                ),
                "oc6_external_source_artifact_recheck_20260621_status": (
                    oc6_external_recheck.get("status")
                ),
                "oc6_external_source_artifact_recheck_20260621_date": (
                    oc6_external_recheck.get("date_checked")
                ),
                "oc6_external_source_artifact_recheck_20260621_query_count": (
                    oc6_external_recheck.get("query_count")
                ),
                "oc6_external_source_artifact_recheck_20260621_positive_artifact_rows": (
                    oc6_external_recheck.get("positive_public_code_artifact_rows")
                ),
                "oc6_external_source_artifact_recheck_20260621_source_equivalent_artifact_rows": (
                    oc6_external_recheck.get("source_code_equivalent_artifact_rows")
                ),
                "oc6_external_source_artifact_recheck_20260621_source_policy_rows_closed": (
                    oc6_external_recheck.get("source_policy_rows_closed_by_recheck")
                ),
                "oc6_external_source_artifact_recheck_20260621_reopen_triggered": (
                    oc6_external_recheck.get("source_policy_reopen_triggered")
                ),
                "oc6_external_source_artifact_recheck_20260621_global_absence_proved": (
                    oc6_external_recheck.get("global_absence_proved")
                ),
                "oc6_tfe_publisher_artifact_availability_20260621_status": (
                    oc6_publisher_availability.get("status")
                ),
                "oc6_tfe_publisher_artifact_availability_20260621_date": (
                    oc6_publisher_availability.get("date_checked")
                ),
                "oc6_tfe_publisher_artifact_availability_20260621_official_article_checked": (
                    oc6_publisher_availability.get("official_article_checked")
                ),
                "oc6_tfe_publisher_artifact_availability_20260621_source_artifact_signal_count": (
                    oc6_publisher_availability.get("source_article", {}).get(
                        "source_artifact_signal_count"
                    )
                ),
                "oc6_tfe_publisher_artifact_availability_20260621_positive_artifact_rows": (
                    oc6_publisher_availability.get("positive_public_code_artifact_rows")
                ),
                "oc6_tfe_publisher_artifact_availability_20260621_source_equivalent_artifact_rows": (
                    oc6_publisher_availability.get("source_code_equivalent_artifact_rows")
                ),
                "oc6_tfe_publisher_artifact_availability_20260621_source_policy_rows_closed": (
                    oc6_publisher_availability.get(
                        "source_policy_rows_closed_by_publisher_audit"
                    )
                ),
                "oc6_tfe_publisher_artifact_availability_20260621_reopen_triggered": (
                    oc6_publisher_availability.get("source_policy_reopen_triggered")
                ),
                "oc6_tfe_publisher_artifact_availability_20260621_global_absence_proved": (
                    oc6_publisher_availability.get("global_absence_proved")
                ),
                "oc6_tfe_source_equivalent_artifact_request_packet_20260621_status": (
                    oc6_source_equivalent_request_packet.get("status")
                ),
                "oc6_tfe_source_equivalent_artifact_request_packet_20260621_date": (
                    oc6_source_equivalent_request_packet.get("date_prepared")
                ),
                "oc6_tfe_source_equivalent_artifact_request_packet_20260621_request_ready": (
                    oc6_source_equivalent_request_packet.get("request_ready")
                ),
                "oc6_tfe_source_equivalent_artifact_request_packet_20260621_request_sent": (
                    oc6_source_equivalent_request_packet.get("request_sent")
                ),
                "oc6_tfe_source_equivalent_artifact_request_packet_20260621_requested_artifact_count": (
                    oc6_source_equivalent_request_packet.get("requested_artifact_count")
                ),
                "oc6_tfe_source_equivalent_artifact_request_packet_20260621_corresponding_author_email": (
                    oc6_source_equivalent_request_packet.get("source_article", {}).get(
                        "corresponding_author_email"
                    )
                ),
                "oc6_tfe_source_equivalent_artifact_request_packet_20260621_source_policy_rows_closed": (
                    oc6_source_equivalent_request_packet.get("not_closing", {}).get(
                        "source_policy_rows_closed_by_packet"
                    )
                ),
                "oc6_tfe_source_equivalent_artifact_request_packet_20260621_reopen_triggered": (
                    oc6_source_equivalent_request_packet.get("not_closing", {}).get(
                        "source_policy_reopen_triggered"
                    )
                ),
                "oc6_tfe_source_equivalent_artifact_request_packet_20260621_global_absence_proved": (
                    oc6_source_equivalent_request_packet.get("not_closing", {}).get(
                        "global_absence_proved"
                    )
                ),
                "oc6_tfe_source_equivalent_artifact_request_packet_20260621_submission_ready": (
                    oc6_source_equivalent_request_packet.get("not_closing", {}).get(
                        "submission_ready"
                    )
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
                "tfe_runner_contract_preflight_status": tfe_runner_contract_preflight.get(
                    "status"
                ),
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
                "source_pendulum_parameter_model_implemented": tfe_model.get(
                    "source_pendulum_parameter_model_implemented"
                ),
                "frictionless_planar_rhs_smoke_implemented": tfe_model.get(
                    "frictionless_planar_rhs_smoke_implemented"
                ),
                "absolute_coordinate_dae_residual_smoke_implemented": tfe_model.get(
                    "absolute_coordinate_dae_residual_smoke_implemented"
                ),
                "absolute_coordinate_frictional_candidate_dae_smoke_implemented": tfe_model.get(
                    "absolute_coordinate_frictional_candidate_dae_smoke_implemented"
                ),
                "absolute_coordinate_planar_lift_trajectory_probe_implemented": tfe_model.get(
                    "absolute_coordinate_planar_lift_trajectory_probe_implemented"
                ),
                "absolute_coordinate_planar_lift_trajectory_probe_rows": tfe_model.get(
                    "absolute_coordinate_planar_lift_trajectory_probe_rows"
                ),
                "absolute_coordinate_planar_lift_trajectory_probe_metric_rows": tfe_model.get(
                    "absolute_coordinate_planar_lift_trajectory_probe_metric_rows"
                ),
                "absolute_coordinate_planar_lift_trajectory_probe_source_policy_rows_completed": tfe_model.get(
                    "absolute_coordinate_planar_lift_trajectory_probe_source_policy_rows_completed"
                ),
                "absolute_coordinate_planar_lift_trajectory_probe_dae_runner_equivalent": tfe_model.get(
                    "absolute_coordinate_planar_lift_trajectory_probe_dae_runner_equivalent"
                ),
                "bounded_absolute_coordinate_dae_trajectory_runner_implemented": tfe_model.get(
                    "bounded_absolute_coordinate_dae_trajectory_runner_implemented"
                ),
                "bounded_absolute_coordinate_dae_trajectory_runner_rows": tfe_model.get(
                    "bounded_absolute_coordinate_dae_trajectory_runner_rows"
                ),
                "bounded_absolute_coordinate_dae_trajectory_runner_metric_rows": tfe_model.get(
                    "bounded_absolute_coordinate_dae_trajectory_runner_metric_rows"
                ),
                "bounded_absolute_coordinate_dae_trajectory_runner_step_residual_rows": tfe_model.get(
                    "bounded_absolute_coordinate_dae_trajectory_runner_step_residual_rows"
                ),
                "bounded_absolute_coordinate_dae_trajectory_runner_source_policy_rows_completed": tfe_model.get(
                    "bounded_absolute_coordinate_dae_trajectory_runner_source_policy_rows_completed"
                ),
                "bounded_absolute_coordinate_dae_trajectory_runner_dae_runner_equivalent": tfe_model.get(
                    "bounded_absolute_coordinate_dae_trajectory_runner_dae_runner_equivalent"
                ),
                "bounded_absolute_coordinate_dae_trajectory_runner_monolithic_integrator": tfe_model.get(
                    "bounded_absolute_coordinate_dae_trajectory_runner_monolithic_integrator"
                ),
                "monolithic_absolute_coordinate_dae_candidate_runner_implemented": tfe_model.get(
                    "monolithic_absolute_coordinate_dae_candidate_runner_implemented"
                ),
                "monolithic_absolute_coordinate_dae_candidate_runner_rows": tfe_model.get(
                    "monolithic_absolute_coordinate_dae_candidate_runner_rows"
                ),
                "monolithic_absolute_coordinate_dae_candidate_runner_metric_rows": tfe_model.get(
                    "monolithic_absolute_coordinate_dae_candidate_runner_metric_rows"
                ),
                "monolithic_absolute_coordinate_dae_candidate_runner_step_residual_rows": tfe_model.get(
                    "monolithic_absolute_coordinate_dae_candidate_runner_step_residual_rows"
                ),
                "monolithic_absolute_coordinate_dae_candidate_runner_source_policy_rows_completed": (
                    tfe_model.get(
                        "monolithic_absolute_coordinate_dae_candidate_runner_source_policy_rows_completed"
                    )
                ),
                "monolithic_absolute_coordinate_dae_candidate_runner_dae_runner_equivalent": tfe_model.get(
                    "monolithic_absolute_coordinate_dae_candidate_runner_dae_runner_equivalent"
                ),
                "monolithic_absolute_coordinate_dae_candidate_runner_monolithic_integrator": tfe_model.get(
                    "monolithic_absolute_coordinate_dae_candidate_runner_monolithic_integrator"
                ),
                "source_method_candidate_runner_contract_implemented": tfe_model.get(
                    "source_method_candidate_runner_contract_implemented"
                ),
                "source_method_candidate_runner_contract_rows": tfe_model.get(
                    "source_method_candidate_runner_contract_rows"
                ),
                "source_method_candidate_runner_contract_source_policy_rows_completed": tfe_model.get(
                    "source_method_candidate_runner_contract_source_policy_rows_completed"
                ),
                "source_method_candidate_runner_contract_method_equivalent": tfe_model.get(
                    "source_method_candidate_runner_contract_method_equivalent"
                ),
                "source_method_candidate_runner_contract_dae_equivalent": tfe_model.get(
                    "source_method_candidate_runner_contract_dae_equivalent"
                ),
                "gauss6_fullva_dae_candidate_contract_implemented": tfe_model.get(
                    "gauss6_fullva_dae_candidate_contract_implemented"
                ),
                "gauss6_fullva_dae_candidate_contract_rows": tfe_model.get(
                    "gauss6_fullva_dae_candidate_contract_rows"
                ),
                "gauss6_fullva_dae_candidate_contract_source_policy_rows_completed": tfe_model.get(
                    "gauss6_fullva_dae_candidate_contract_source_policy_rows_completed"
                ),
                "gauss6_fullva_dae_candidate_contract_dae_equivalent": tfe_model.get(
                    "gauss6_fullva_dae_candidate_contract_dae_equivalent"
                ),
                "gauss6_fullva_dae_candidate_contract_fullva_dae_equivalent": tfe_model.get(
                    "gauss6_fullva_dae_candidate_contract_fullva_dae_equivalent"
                ),
                "dae_trajectory_bridge_contract_implemented": tfe_model.get(
                    "dae_trajectory_bridge_contract_implemented"
                ),
                "dae_trajectory_bridge_contract_rows": tfe_model.get(
                    "dae_trajectory_bridge_contract_rows"
                ),
                "dae_trajectory_bridge_contract_matched_rows": tfe_model.get(
                    "dae_trajectory_bridge_contract_matched_rows"
                ),
                "dae_trajectory_bridge_contract_source_metric_rows": tfe_model.get(
                    "dae_trajectory_bridge_contract_source_metric_rows"
                ),
                "dae_trajectory_bridge_contract_dae_metric_rows": tfe_model.get(
                    "dae_trajectory_bridge_contract_dae_metric_rows"
                ),
                "dae_trajectory_bridge_contract_source_policy_rows_completed": tfe_model.get(
                    "dae_trajectory_bridge_contract_source_policy_rows_completed"
                ),
                "dae_trajectory_bridge_contract_dae_runner_equivalent": tfe_model.get(
                    "dae_trajectory_bridge_contract_dae_runner_equivalent"
                ),
                "dae_trajectory_bridge_contract_method_runner_equivalent": tfe_bridge.get(
                    "source_policy_method_runner_equivalent"
                ),
                "dae_trajectory_bridge_contract_monolithic_integrator": tfe_model.get(
                    "dae_trajectory_bridge_contract_monolithic_integrator"
                ),
                "dae_trajectory_bridge_contract_all_rows_finite": tfe_model.get(
                    "dae_trajectory_bridge_contract_all_rows_finite"
                ),
                "dae_trajectory_bridge_contract_all_dae_residuals_below_1e_10": tfe_model.get(
                    "dae_trajectory_bridge_contract_all_dae_residuals_below_1e_10"
                ),
                "dae_trajectory_bridge_contract_accepted_use": tfe_bridge.get("accepted_use"),
                "candidate_frictional_dae_trajectory_contract_implemented": tfe_model.get(
                    "candidate_frictional_dae_trajectory_contract_implemented"
                ),
                "candidate_frictional_dae_trajectory_contract_rows": tfe_model.get(
                    "candidate_frictional_dae_trajectory_contract_rows"
                ),
                "candidate_frictional_dae_trajectory_contract_step_residual_rows": tfe_model.get(
                    "candidate_frictional_dae_trajectory_contract_step_residual_rows"
                ),
                "candidate_frictional_dae_trajectory_contract_source_policy_rows_completed": tfe_model.get(
                    "candidate_frictional_dae_trajectory_contract_source_policy_rows_completed"
                ),
                "candidate_frictional_dae_trajectory_contract_dae_runner_equivalent": tfe_model.get(
                    "candidate_frictional_dae_trajectory_contract_dae_runner_equivalent"
                ),
                "candidate_frictional_dae_trajectory_contract_method_runner_equivalent": tfe_model.get(
                    "candidate_frictional_dae_trajectory_contract_method_runner_equivalent"
                ),
                "candidate_frictional_dae_trajectory_contract_brown_mcphee_source_code_equivalent_law": tfe_model.get(
                    "candidate_frictional_dae_trajectory_contract_brown_mcphee_source_code_equivalent_law"
                ),
                "candidate_frictional_dae_trajectory_contract_monolithic_integrator": tfe_model.get(
                    "candidate_frictional_dae_trajectory_contract_monolithic_integrator"
                ),
                "candidate_frictional_dae_trajectory_contract_all_rows_finite": tfe_model.get(
                    "candidate_frictional_dae_trajectory_contract_all_rows_finite"
                ),
                "candidate_frictional_dae_trajectory_contract_all_dae_residuals_below_1e_9": tfe_model.get(
                    "candidate_frictional_dae_trajectory_contract_all_dae_residuals_below_1e_9"
                ),
                "candidate_frictional_dae_trajectory_contract_all_friction_power_nonpositive": tfe_model.get(
                    "candidate_frictional_dae_trajectory_contract_all_friction_power_nonpositive"
                ),
                "brown_mcphee_transition_velocity_sensitivity_rows": tfe_transition_velocity_sensitivity.get(
                    "endpoint_delta_row_count"
                ),
                "brown_mcphee_transition_velocity_sensitivity_contract_rows": tfe_transition_velocity_sensitivity.get(
                    "contract_row_count"
                ),
                "brown_mcphee_transition_velocity_sensitivity_source_policy_rows_completed": tfe_transition_velocity_sensitivity.get(
                    "source_policy_rows_completed"
                ),
                "brown_mcphee_transition_velocity_sensitivity_material": tfe_transition_velocity_sensitivity.get(
                    "missing_transition_velocity_is_numerically_material"
                ),
                "brown_mcphee_transition_velocity_sensitivity_equivalence_flags_false": tfe_transition_velocity_sensitivity.get(
                    "all_contract_equivalence_flags_false"
                ),
                "brown_mcphee_transition_velocity_sensitivity_max_coordinate_delta": tfe_transition_velocity_sensitivity.get(
                    "max_endpoint_coordinate_delta_vs_baseline"
                ),
                "brown_mcphee_transition_velocity_sensitivity_max_velocity_delta": tfe_transition_velocity_sensitivity.get(
                    "max_endpoint_velocity_delta_vs_baseline"
                ),
                "brown_mcphee_source_code_equivalence_certificate_status": tfe_brown_mcphee_certificate.get(
                    "status"
                ),
                "brown_mcphee_source_code_equivalence_certificate_available": tfe_brown_mcphee_certificate.get(
                    "certificate_available"
                ),
                "brown_mcphee_source_code_equivalence_certificate_positive": tfe_brown_mcphee_certificate.get(
                    "positive_source_code_equivalence_certified"
                ),
                "brown_mcphee_source_code_equivalence_certificate_nonheavy_block_closed": tfe_brown_mcphee_certificate.get(
                    "nonheavy_contract_block_closed"
                ),
                "brown_mcphee_source_code_equivalence_certificate_source_policy_execution_invoked": tfe_brown_mcphee_certificate.get(
                    "source_policy_execution_invoked"
                ),
                "brown_mcphee_source_code_equivalence_certificate_can_close_now": tfe_brown_mcphee_certificate.get(
                    "can_close_now"
                ),
                "source_policy_dae_runner_equivalent": tfe_model.get("source_policy_dae_runner_equivalent"),
                "source_output_time_integration_smoke_implemented": tfe_model.get(
                    "source_output_time_integration_smoke_implemented"
                ),
                "source_policy_time_integration_runner_equivalent": tfe_model.get(
                    "source_policy_time_integration_runner_equivalent"
                ),
                "source_reference_solution_policy_smoke_implemented": tfe_model.get(
                    "source_reference_solution_policy_smoke_implemented"
                ),
                "source_reference_solution_policy_smoke_full_T10": tfe_model.get(
                    "source_reference_solution_policy_smoke_full_T10"
                ),
                "source_grid_policy_resolved_for_full_T10": tfe_grid.get(
                    "source_grid_policy_resolved_for_full_T10"
                ),
                "source_grid_integer_step_incompatible_rows": tfe_grid.get(
                    "integer_step_incompatible_rows"
                ),
                "source_grid_exact_T_compatible_rows_endpoint_convention_resolved": tfe_grid.get(
                    "endpoint_compatible_rows_source_endpoint_convention_resolved"
                ),
                "source_grid_endpoint_incompatible_rows_requiring_policy": tfe_grid.get(
                    "endpoint_incompatible_rows_require_source_endpoint_policy"
                ),
                "source_grid_policy_resolved_for_exact_T_compatible_rows": tfe_grid.get(
                    "source_grid_policy_resolved_for_exact_T_compatible_rows"
                ),
                "endpoint_boundary_certificate_status": tfe_endpoint_boundary.get("status"),
                "endpoint_boundary_literal_overrun_bound_proved": tfe_endpoint_boundary.get(
                    "theorem", {}
                ).get("name")
                == "fixed_h_until_final_time_endpoint_bound",
                "endpoint_boundary_literal_exact_T_rows": tfe_endpoint_boundary.get(
                    "algorithm_literal_exact_T_row_count"
                ),
                "endpoint_boundary_literal_overrun_rows": tfe_endpoint_boundary.get(
                    "algorithm_literal_overrun_row_count"
                ),
                "endpoint_boundary_source_policy_rows_completed": tfe_endpoint_boundary.get(
                    "source_policy_rows_completed"
                ),
                "endpoint_boundary_full_T10_policy_resolved": tfe_endpoint_boundary.get(
                    "source_grid_policy_resolved_for_full_T10"
                ),
                "endpoint_boundary_exact_T_error_sampling_equivalent": tfe_endpoint_boundary.get(
                    "source_policy_exact_T_error_sampling_equivalent"
                ),
                "full_T10_endpoint_policy_closure_certificate_status": tfe_endpoint_certificate.get(
                    "status"
                ),
                "full_T10_endpoint_policy_closure_certificate_available": tfe_endpoint_certificate.get(
                    "certificate_available"
                ),
                "full_T10_endpoint_policy_closure_certificate_positive": tfe_endpoint_certificate.get(
                    "positive_full_T10_endpoint_policy_certified"
                ),
                "full_T10_endpoint_policy_closure_certificate_nonheavy_block_closed": tfe_endpoint_certificate.get(
                    "nonheavy_contract_block_closed"
                ),
                "full_T10_endpoint_policy_closure_certificate_source_policy_execution_invoked": tfe_endpoint_certificate.get(
                    "source_policy_execution_invoked"
                ),
                "full_T10_endpoint_policy_closure_certificate_can_close_now": tfe_endpoint_certificate.get(
                    "can_close_now"
                ),
                "source_comparator_candidate_runners_implemented": tfe_model.get(
                    "source_comparator_candidate_runners_implemented"
                ),
                "newmark_beta_candidate_runner_smoke_implemented": tfe_model.get(
                    "newmark_beta_candidate_runner_smoke_implemented"
                ),
                "trapezoidal_candidate_runner_smoke_implemented": tfe_model.get(
                    "trapezoidal_candidate_runner_smoke_implemented"
                ),
                "source_policy_method_runner_equivalent": tfe_model.get(
                    "source_policy_method_runner_equivalent"
                ),
                "tfe_m1_m2_m3_candidate_runner_smoke_implemented": tfe_model.get(
                    "tfe_m1_m2_m3_candidate_runner_smoke_implemented"
                ),
                "tfe_m1_m2_m3_source_policy_runners_implemented": tfe_model.get(
                    "tfe_m1_m2_m3_source_policy_runners_implemented"
                ),
                "gauss6_fullva_source_pendulum_candidate_smoke_implemented": tfe_model.get(
                    "gauss6_fullva_source_pendulum_candidate_smoke_implemented"
                ),
                "gauss6_fullva_absolute_coordinate_source_policy_runner_implemented": tfe_model.get(
                    "gauss6_fullva_absolute_coordinate_source_policy_runner_implemented"
                ),
                "gauss6_fullva_on_source_pendulum_implemented": tfe_model.get(
                    "gauss6_fullva_on_source_pendulum_implemented"
                ),
                "gauss6_fullva_source_pendulum_candidate_rows": tfe_model.get(
                    "gauss6_fullva_source_pendulum_candidate_rows"
                ),
                "gauss6_fullva_source_pendulum_candidate_source_policy_rows_completed": tfe_model.get(
                    "gauss6_fullva_source_pendulum_candidate_source_policy_rows_completed"
                ),
                "gauss6_fullva_source_pendulum_candidate_method_equivalent": tfe_model.get(
                    "gauss6_fullva_source_pendulum_candidate_method_equivalent"
                ),
                "bounded_source_policy_runner_api_implemented": tfe_model.get(
                    "bounded_source_policy_runner_api_implemented"
                ),
                "bounded_source_policy_runner_smoke_implemented": tfe_model.get(
                    "bounded_source_policy_runner_smoke_implemented"
                ),
                "bounded_source_policy_runner_rows": tfe_model.get(
                    "bounded_source_policy_runner_rows"
                ),
                "bounded_source_policy_runner_full_T10": tfe_model.get(
                    "bounded_source_policy_runner_full_T10"
                ),
                "bounded_source_policy_runner_source_policy_rows_completed": tfe_model.get(
                    "bounded_source_policy_runner_source_policy_rows_completed"
                ),
                "active_tfe_b2_candidate_row_smoke_implemented": tfe_model.get(
                    "active_tfe_b2_candidate_row_smoke_implemented"
                ),
                "active_tfe_b2_candidate_row_smoke_full_T10": tfe_model.get(
                    "active_tfe_b2_candidate_row_smoke_full_T10"
                ),
                "active_tfe_b2_source_policy_rows_completed": tfe_model.get(
                    "active_tfe_b2_source_policy_rows_completed"
                ),
                "active_tfe_b2_source_reference_full_T10_candidate_probe_implemented": tfe_model.get(
                    "active_tfe_b2_source_reference_full_T10_candidate_probe_implemented"
                ),
                "active_tfe_b2_source_reference_full_T10_candidate_probe_full_T10": tfe_model.get(
                    "active_tfe_b2_source_reference_full_T10_candidate_probe_full_T10"
                ),
                "active_tfe_b2_source_reference_full_T10_candidate_probe_source_policy_reference_invoked": tfe_model.get(
                    "active_tfe_b2_source_reference_full_T10_candidate_probe_source_policy_reference_invoked"
                ),
                "active_tfe_b2_source_reference_full_T10_candidate_probe_source_policy_rows_completed": tfe_model.get(
                    "active_tfe_b2_source_reference_full_T10_candidate_probe_source_policy_rows_completed"
                ),
                "active_tfe_b2_source_reference_full_T10_candidate_probe_method_equivalent": tfe_model.get(
                    "active_tfe_b2_source_reference_full_T10_candidate_probe_method_equivalent"
                ),
                "source_error_norm_and_output_policy_encoded": tfe_model.get(
                    "source_error_norm_and_output_policy_encoded"
                ),
                "brown_mcphee_candidate_friction_law_encoded": tfe_model.get(
                    "brown_mcphee_candidate_friction_law_encoded"
                ),
                "frictional_planar_candidate_rhs_smoke_implemented": tfe_model.get(
                    "frictional_planar_candidate_rhs_smoke_implemented"
                ),
                "pendulum_dae_runner_implemented": tfe_model.get("pendulum_dae_runner_implemented"),
                "brown_mcphee_friction_law_implemented": tfe_model.get(
                    "brown_mcphee_friction_law_implemented"
                ),
                "source_policy_rows_completed": tfe_model.get("source_policy_rows_completed"),
            },
            (
                "keep TFE source-policy terminal/unable-to-reproduce unless a new public or "
                "source-code-equivalent TFE implementation artifact appears"
            ),
        ),
        req(
            "OC7",
            "Close the theorem/proof gap for the claimed order result.",
            "open" if not proof_closed else "satisfied",
            ["PROOF_CLOSURE_MANIFEST.json"],
            not proof_closed,
            {
                "direct_pc2_proof_gap_closed": proof.get("closure_state", {}).get(
                    "direct_pc2_proof_gap_closed", proof.get("closure_state", {}).get("proof_gap_closed")
                ),
                "proof_gap_closed": proof.get("closure_state", {}).get("proof_gap_closed"),
                "proof_gap_closed_scope": proof.get("closure_state", {}).get(
                    "proof_gap_closed_scope", DIRECT_PC2_SCOPE
                ),
                "proof_gap_closed_reading_rule": proof.get("closure_state", {}).get(
                    "proof_gap_closed_reading_rule", DIRECT_PC2_READING_RULE
                ),
                "stage_residual_O_h7_implementation_defect_proved": proof.get("closure_state", {}).get(
                    "stage_residual_O_h7_implementation_defect_proved"
                ),
                "open_dynamic_rows": proof.get("evidence_summary", {}).get("open_dynamic_rows"),
                "open_dynamic_rows_scope": proof.get("evidence_summary", {}).get(
                    "open_dynamic_rows_scope", "symbolic_primitive_certificate_route_not_active_direct_pc2"
                ),
                "symbolic_primitive_route_open_dynamic_rows": proof.get("evidence_summary", {}).get(
                    "open_dynamic_rows"
                ),
                "pc2_closed_by_direct_substitution": proof.get("closure_state", {}).get(
                    "pc2_closed_by_direct_substitution"
                ),
                "direct_dynamic_zero_rows": proof.get("evidence_summary", {}).get(
                    "newton_euler_d5_direct_substitution_dynamic_zero_rows"
                ),
                "direct_full_stage_rows": proof.get("evidence_summary", {}).get(
                    "newton_euler_d5_direct_substitution_full_stage_rows"
                ),
                "certified_non_dynamic_rows": proof.get("evidence_summary", {}).get(
                    "certified_non_dynamic_rows"
                ),
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
            (
                "closed by D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE"
                if proof_closed
                else "finish the independent symbolic oracle and O(h^7) defect certificate for dynamic rows"
            ),
        ),
        req(
            "OC8",
            "Pass the narrowed-claim quality review while retaining the global submission blockers.",
            "open" if not quality_review_closed else "satisfied",
            ["CMAME_BLOCKER_CLOSURE_GATE.json"],
            not quality_review_closed,
            {
                "mechanical_preflight_passed": blocker.get("mechanical_preflight_passed"),
                "quality_review_passed": blocker.get("quality_review_passed"),
                "submission_ready": blocker.get("submission_ready"),
                "submission_ready_under_narrowed_claim": blocker.get(
                    "submission_ready_under_narrowed_claim"
                ),
                "narrowed_claim_alias_warning": blocker.get("narrowed_claim_alias_warning"),
                "open_blockers": [item.get("id") for item in blocker.get("blockers", []) if item.get("status") != "closed"],
            },
            "close OC4, OC6, and OC12 before calling the global paper package submission ready",
        ),
        req(
            "OC9",
            "Complete citation, metadata, sidecar, and external reference integrity for final submission.",
            "partial" if not integrity_closed else "satisfied",
            ["CMAME_SUBMISSION_INTEGRITY_AUDIT.json"],
            not integrity_closed,
            {
                "local_integrity_passed": integrity.get("local_integrity_passed"),
                "external_reference_web_verification_complete": integrity.get(
                    "external_reference_web_verification_complete"
                ),
                "submission_ready": integrity.get("submission_ready"),
            },
            "closed for the current package; keep citation, metadata, sidecar, and reference-integrity checks current during final submission refresh",
        ),
        req(
            "OC10",
            "Make figures, prose, related work, and visual presentation publication-grade.",
            "partial" if not presentation_closed else "satisfied",
            [
                "CMAME_FIGURE_SET_AUDIT.json",
                "CMAME_PROSE_RESIDUE_AUDIT.json",
                "CMAME_RELATED_WORK_AUDIT.json",
                "CMAME_VISUAL_LEGIBILITY_AUDIT.json",
            ],
            not presentation_closed,
            {
                "figure_b7_closed": figures.get("b7_closed"),
                "figure_count": figures.get("figure_count"),
                "expected_figure_count": figures.get("expected_figure_count"),
                "prose_submission_ready": prose.get("submission_ready"),
                "prose_b6_closed_under_narrowed_policy": prose_b6_closed_under_narrowed_policy,
                "related_work_status": related.get("status"),
                "visual_status": visual.get("status"),
            },
            (
                "closed under narrowed B6 prose and B7 diagnostic figure scope"
                if presentation_closed
                else "finish B6 prose cleanup and B7 publication-grade figure/work-precision gate"
            ),
        ),
        req(
            "OC11",
            "Keep a review agent and validator in the package to audit all gates.",
            "satisfied" if review_agent_present else "open",
            ["cmame_submission_review_agent.py", "validate_cmame_review_agent.py"],
            not review_agent_present,
            {"review_agent_present": review_agent_present},
            "restore the review agent, its report, and its validator",
        ),
        req(
            "OC12",
            "Provide a minimal reproducible submission code package rather than only the audit repository.",
            "satisfied" if minimal_code_ready else "partial" if local_runner_package_partial_ready else "open",
            [
                "current Python inventory",
                "EXTERNAL_SOURCE_POLICY_CLOSURE_MANIFEST.json",
                "PROOF_CLOSURE_MANIFEST.json",
                "CMAME_MINIMAL_REPRODUCIBILITY_CANDIDATE_MANIFEST.json",
                "CMAME_RUNNER_CENTERED_REPRODUCIBILITY_AUDIT.json",
                "B6_FOUR_EXAMPLE_LOCAL_EVIDENCE_SUMMARY.json",
                "CMAME_CLOSED_LOOP_LOCAL_RUNNER_CANDIDATE_MANIFEST.json",
                "CMAME_P1_LOCAL_RUNNER_EXTRACTION_AUDIT.json",
                "CMAME_NARROWED_REPRODUCIBILITY_PACKAGE_AUDIT.json",
                "CMAME_NARROWED_REPRO_CODE_ARCHIVE_MANIFEST.json",
                "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json",
                "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json",
                "cmame_narrowed_repro_code_archive.zip",
            ],
            not minimal_code_ready,
            {
                "paper_python_file_count": paper_code.get("file_count"),
                "paper_python_line_count": paper_code.get("line_count"),
                "v048_python_file_count": v048_code.get("file_count"),
                "v048_python_line_count": v048_code.get("line_count"),
                "combined_python_line_count": combined_python_line_count,
                "code_bloat_risk_for_submission": combined_python_line_count > 20000,
                "minimal_reproducibility_candidate_status": minimal_candidate.get("status"),
                "minimal_reproducibility_candidate_file_count": minimal_candidate.get("candidate_file_count"),
                "minimal_reproducibility_candidate_python_lines": minimal_candidate.get(
                    "candidate_python_line_count"
                ),
                "minimal_reproducibility_candidate_replay_only": minimal_candidate.get("read_only_replay_package"),
                "minimal_reproducibility_candidate_submission_ready": minimal_candidate.get("submission_ready"),
                "local_runner_package_partial_ready": local_runner_package_partial_ready,
                "narrowed_reproducibility_package_ready": narrowed_repro.get(
                    "narrowed_claim_reproducibility_package_ready"
                ),
                "narrowed_repro_code_archive_ready": narrowed_repro_code_archive_ready,
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
                "narrowed_repro_code_archive_full_source_policy_ready": narrowed_repro_code_archive.get(
                    "full_source_policy_runner_package_ready"
                ),
                "narrowed_repro_code_archive_submission_ready": narrowed_repro_code_archive.get(
                    "submission_ready"
                ),
                "runner_centered_status": runner_centered.get("status"),
                "runner_centered_package_ready": runner_centered.get("runner_centered_package_ready"),
                "local_runner_centered_candidate_ready": runner_centered.get("local_runner_centered_candidate_ready"),
                "full_source_policy_runner_package_ready": runner_centered.get(
                    "full_source_policy_runner_package_ready"
                ),
                "human_runnable_self_contained_examples": human_runnable_self_contained_examples,
                "human_runnable_replay_only_examples": human_runnable_replay_only_examples,
                "b6_four_example_local_rows": b6_local_evidence.get("local_rows"),
                "b6_four_example_source_policy_rows_closed": b6_local_evidence.get(
                    "source_policy_external_rows_closed"
                ),
                "b6_four_example_source_policy_rows_total": b6_local_evidence.get(
                    "source_policy_external_rows_total"
                ),
                "compact_closed_loop_candidate_runner_passed": closed_loop_candidate.get("runner_passed"),
                "compact_closed_loop_candidate_python_lines": closed_loop_candidate.get(
                    "candidate_python_line_count"
                ),
                "p1_single_runner_candidate_ready": p1_local_runner.get("p1_single_runner_candidate_ready"),
                "p1_double_runner_candidate_ready": p1_local_runner.get("p1_double_runner_candidate_ready"),
                "minimal_submission_code_dependency_boundary": minimal_submission_code_dependency_boundary,
                "minimal_submission_code_dependency_boundary_status": (
                    minimal_submission_code_dependency_boundary["status"]
                ),
                "minimal_submission_code_dependency_blockers": (
                    minimal_submission_code_dependency_boundary["blocking_objective_requirements"]
                ),
                "minimal_submission_code_dependency_safe_use": (
                    minimal_submission_code_dependency_boundary["safe_current_package_use"]
                ),
                "full_source_policy_runner_archive_gap_status": full_source_runner_gap.get("status"),
                "full_source_policy_runner_archive_gap_ready_now": full_source_runner_gap.get(
                    "closure_conditions", {}
                ).get("full_archive_ready_now"),
                "full_source_policy_runner_archive_gap_can_use_current_archive": full_source_runner_gap.get(
                    "closure_conditions", {}
                ).get("can_use_current_archive_as_full_source_policy_runner_archive"),
                "full_source_policy_runner_archive_gap_safe_current_archive_use": (
                    "narrowed_claim_replay_and_audit_provenance_only"
                ),
                "full_source_policy_runner_archive_gap_remaining_rows_to_close": full_source_runner_gap.get(
                    "closure_conditions", {}
                ).get("remaining_source_policy_rows_to_close"),
                "full_source_policy_runner_archive_gap_terminal_unable_rows": full_source_runner_gap.get(
                    "closure_conditions", {}
                ).get("terminal_unable_to_reproduce_rows"),
                "full_source_policy_runner_archive_gap_ra_hi_open_rows": full_source_runner_gap.get(
                    "closure_conditions", {}
                ).get("ra_hi_rows_requiring_authorized_closeout_or_new_artifact"),
                "full_source_policy_runner_archive_gap_source_policy_rows_closed": full_source_runner_gap.get(
                    "source_policy_rows", {}
                ).get("closed"),
                "full_source_policy_runner_archive_gap_source_policy_rows_total": full_source_runner_gap.get(
                    "source_policy_rows", {}
                ).get("total"),
                "full_source_policy_runner_archive_gap_terminal_reopen_conditions": (
                    full_source_runner_terminal_reopen_conditions
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
                    full_source_runner_terminal_reopen_conditions.get("tfe2026_original_pendulum")
                ),
                "full_source_policy_runner_archive_gap_vp2024_reopen_condition": (
                    full_source_runner_terminal_reopen_conditions.get("vp2024_velocity_partitioning")
                ),
                "full_source_policy_runner_archive_gap_required_approval_statement": (
                    full_source_runner_required_approval_statement
                ),
                "full_source_policy_runner_archive_gap_action_boundary": full_source_runner_gap.get(
                    "action_boundary"
                ),
                "full_source_policy_runner_archive_gap_safe_without_b4_opt_in_count": (
                    full_source_runner_gap.get("safe_without_b4_opt_in_count")
                ),
                "full_source_policy_runner_archive_gap_opt_in_required_action_count": (
                    full_source_runner_gap.get("opt_in_required_action_count")
                ),
                "full_source_policy_runner_archive_gap_source_policy_execution_allowed_now": (
                    full_source_runner_gap.get("source_policy_execution_allowed_now")
                ),
                "full_source_policy_runner_archive_gap_source_policy_execution_invoked": (
                    full_source_runner_gap.get("source_policy_execution_invoked")
                ),
                "full_source_policy_runner_archive_gap_exact_b4_opt_in_required_for_execution": (
                    full_source_runner_gap.get("exact_b4_opt_in_required_for_execution")
                ),
                "full_source_policy_runner_archive_gap_opt_in_required_command_count": (
                    full_source_runner_gap.get("opt_in_required_command_count")
                ),
                "full_source_policy_runner_archive_gap_opt_in_required_mapped_external_rows": (
                    full_source_runner_gap.get("opt_in_required_mapped_external_rows")
                ),
                "full_source_policy_runner_archive_gap_safe_action_ids": [
                    item.get("id")
                    for item in full_source_runner_gap.get("safe_next_actions_without_b4_opt_in", [])
                    if isinstance(item, dict)
                ]
                if full_source_runner_gap.get("safe_action_ids") is None
                else full_source_runner_gap.get("safe_action_ids"),
                "full_source_policy_runner_archive_gap_opt_in_action_ids": [
                    item.get("id")
                    for item in full_source_runner_gap.get("opt_in_required_actions", [])
                    if isinstance(item, dict)
                ]
                if full_source_runner_gap.get("opt_in_action_ids") is None
                else full_source_runner_gap.get("opt_in_action_ids"),
                "full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_status": (
                    full_source_runner_gap.get("closure_conditions", {}).get(
                        "tfe_runner_contract_preflight_status"
                    )
                ),
                "full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_entrypoints": (
                    full_source_runner_gap.get("closure_conditions", {}).get(
                        "tfe_runner_contract_preflight_entrypoints"
                    )
                ),
                "full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_candidate_backed": (
                    full_source_runner_gap.get("closure_conditions", {}).get(
                        "tfe_runner_contract_preflight_candidate_backed"
                    )
                ),
                "full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_source_policy_rows_completed": (
                    full_source_runner_gap.get("closure_conditions", {}).get(
                        "tfe_runner_contract_preflight_source_policy_rows_completed"
                    )
                ),
                "full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_execution_blocks": (
                    full_source_runner_gap.get("closure_conditions", {}).get(
                        "tfe_runner_contract_preflight_execution_blocks"
                    )
                ),
                "full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_safe_use": (
                    full_source_runner_gap.get("closure_conditions", {}).get(
                        "tfe_runner_contract_preflight_safe_use"
                    )
                ),
                "source_policy_execution_handoff_status": b4_execution_handoff.get("status"),
                "source_policy_execution_handoff_authorized": b4_execution_handoff.get(
                    "execution_authorized"
                ),
                "source_policy_execution_handoff_commands_not_run": b4_execution_handoff.get(
                    "commands_not_run_by_handoff"
                ),
            },
            (
                "promote the partial local runner package to a full source-policy runner archive after OC4/OC6 close"
                if local_runner_package_partial_ready
                else "promote the replay-only candidate to a source-policy runner archive after source-policy and proof gates close"
            ),
        ),
    ]

    blocking_open = [
        item for item in requirements if item["blocking_for_goal_completion"] and item["status"] != "satisfied"
    ]
    satisfied = [item for item in requirements if item["status"] == "satisfied"]
    partial = [item for item in requirements if item["status"] == "partial"]
    open_items = [item for item in requirements if item["status"] == "open"]
    objective_complete = len(blocking_open) == 0
    blocking_requirement_ids = [item["id"] for item in blocking_open]
    open_blockers = [
        {
            "id": item["id"],
            "status": item["status"],
            "requirement": item["requirement"],
            "evidence": item["evidence"],
            "next_to_close": item["next_to_close"],
            "observed": item["observed"],
        }
        for item in blocking_open
    ]
    open_blocker_ids = blocking_requirement_ids
    blockers_by_id = {item["id"]: item for item in open_blockers}
    blocker_status_by_id = {item["id"]: item["status"] for item in open_blockers}
    blocker_next_actions_by_id = {
        item["id"]: item["next_to_close"] for item in open_blockers
    }
    source_policy_execution_invoked = any(
        item is True
        for item in [
            b4_execution_handoff.get("execution_invoked_by_packet"),
            ra_hi_closeout.get("guarded_execution_boundary", {}).get("execution_invoked_by_packet"),
            b4_guarded_refusal.get("source_policy_execution_invoked"),
        ]
    )
    run_v047_invoked = any(
        item is True
        for item in [
            b4_execution_handoff.get("run_v047_invoked"),
            ra_hi_closeout.get("guarded_execution_boundary", {}).get("run_v047_invoked"),
            tfe_dae_gap.get("run_v047_invoked"),
            tfe_execution_preflight.get("run_v047_invoked"),
            tfe_endpoint_sensitivity.get("execution_policy", {}).get("run_v047_invoked"),
        ]
    )
    heavy_numerical_run_invoked = any(
        item is True
        for item in [
            b4_execution_handoff.get("heavy_numerical_run_invoked"),
            ra_hi_closeout.get("guarded_execution_boundary", {}).get("heavy_numerical_run_invoked"),
            tfe_dae_gap.get("heavy_numerical_run_invoked"),
            tfe_execution_preflight.get("heavy_numerical_run_invoked"),
        ]
    )
    v048_runner_invoked = any(
        item is True
        for item in [
            b4_execution_handoff.get("v048_runner_invoked"),
            ra_hi_closeout.get("guarded_execution_boundary", {}).get("v048_runner_invoked"),
            tfe_dae_gap.get("v048_runner_invoked"),
            tfe_execution_preflight.get("v048_runner_invoked"),
        ]
    )
    b4_guarded_refusal_boundary_tuple = (
        f"{b4_guarded_refusal.get('no_opt_in_refusal_proved_static')}/"
        f"{b4_guarded_refusal.get('wrong_approval_refusal_proved_static')}/"
        f"{b4_guarded_refusal.get('refusal_exit_code')}/"
        f"{b4_guarded_refusal.get('pre_guard_command_count')}/"
        f"{b4_guarded_refusal.get('post_guard_source_policy_command_count')}/"
        f"{b4_guarded_refusal.get('source_policy_execution_invoked')}/"
        f"{b4_guarded_refusal.get('submission_ready')}"
    )
    source_policy_execution_allowed_now = bool(
        full_source_runner_gap.get("source_policy_execution_allowed_now") is True
    )
    exact_b4_opt_in_required_for_execution = (
        full_source_runner_gap.get("exact_b4_opt_in_required_for_execution")
        if full_source_runner_gap.get("exact_b4_opt_in_required_for_execution") is not None
        else True
    )
    safe_action_ids = (
        DEFAULT_SAFE_ACTION_IDS
        if full_source_runner_gap.get("safe_action_ids") is None
        else full_source_runner_gap.get("safe_action_ids")
    )
    opt_in_action_ids = (
        DEFAULT_OPT_IN_ACTION_IDS
        if full_source_runner_gap.get("opt_in_action_ids") is None
        else full_source_runner_gap.get("opt_in_action_ids")
    )
    safe_actions_without_b4_opt_in = (
        full_source_runner_gap.get("safe_next_actions_without_b4_opt_in")
        or [
            {"id": action_id, "allowed_without_b4_opt_in": True}
            for action_id in safe_action_ids
        ]
    )
    opt_in_required_actions = (
        full_source_runner_gap.get("opt_in_required_actions")
        or [
            {"id": action_id, "allowed_without_b4_opt_in": False}
            for action_id in opt_in_action_ids
        ]
    )
    required_user_approval_statement = (
        DEFAULT_REQUIRED_USER_APPROVAL_STATEMENT
        if full_source_runner_gap.get("required_user_approval_statement") is None
        else full_source_runner_gap.get("required_user_approval_statement")
    )
    guarded_execution_driver = (
        "run_b4_source_policy_after_opt_in.sh"
        if full_source_runner_gap.get("guarded_execution_driver") is None
        else full_source_runner_gap.get("guarded_execution_driver")
    )
    blocker_required_to_close_by_id = {
        "OC4": {
            "closure_condition": "close all 40 source-policy rows or introduce a new promotion artifact accepted by the source-policy ledger",
            "current_source_policy_closed_ratio": full_source_policy_row_provenance.get(
                "source_policy_closed_ratio"
            ),
            "source_policy_rows_closed": full_source_policy_row_provenance.get(
                "source_policy_rows_closed"
            ),
            "source_policy_rows_total": full_source_policy_row_provenance.get(
                "source_policy_rows_total"
            ),
            "authorized_ra_hi_closeout_route": {
                "requires_exact_b4_opt_in": exact_b4_opt_in_required_for_execution,
                "execution_allowed_now": source_policy_execution_allowed_now,
                "execution_invoked": source_policy_execution_invoked,
                "guarded_execution_driver": guarded_execution_driver,
                "required_user_approval_statement": required_user_approval_statement,
                "opt_in_required_command_count": b4_execution_handoff.get(
                    "opt_in_required_command_count"
                ),
                "opt_in_required_mapped_external_rows": b4_execution_handoff.get(
                    "opt_in_required_mapped_external_rows"
                ),
                "ready_command_count": b4_execution_handoff.get("ready_command_count"),
                "ready_command_mapped_rows": b4_execution_handoff.get(
                    "ready_command_mapped_external_rows"
                ),
            },
            "current_handoff_status": b4_execution_handoff.get("status"),
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
            "tfe_runner_closed": tfe_runner_closed,
            "source_policy_rows_completed": tfe_runner_contract_preflight.get(
                "source_policy_rows_completed"
            ),
            "contract_preflight_status": tfe_runner_contract_preflight.get("status"),
            "candidate_backed_contract_count": tfe_runner_contract_preflight.get(
                "candidate_backed_contract_count"
            ),
            "entrypoint_count": tfe_runner_contract_preflight.get("entrypoint_count"),
            "callable_contract_count": tfe_runner_contract_preflight.get(
                "callable_contract_count"
            ),
            "effective_execution_block_count": tfe_dae_gap.get(
                "source_policy_execution_missing_contract_block_count"
            ),
            "effective_execution_blocks": tfe_dae_gap.get(
                "source_policy_execution_missing_contract_blocks"
            ),
            "candidate_backed_non_equivalent_runner_blocks": tfe_dae_gap.get(
                "candidate_backed_non_equivalent_runner_block_ids"
            ),
            "nonheavy_terminal_blocks": tfe_dae_gap.get(
                "terminal_nonpromoted_contract_blocks"
            ),
            "reopen_condition": tfe_execution_preflight.get("reopen_condition"),
            "latest_external_probe": {
                "date": source_policy_public_code_refresh.get(
                    "latest_external_probe_date_checked"
                ),
                "probe_count": source_policy_public_code_refresh.get(
                    "latest_external_probe_count"
                ),
                "positive_public_code_artifact_rows": source_policy_public_code_refresh.get(
                    "latest_external_probe_positive_public_code_artifact_rows"
                ),
                "source_policy_rows_closed": source_policy_public_code_refresh.get(
                    "latest_external_probe_source_policy_rows_closed"
                ),
                "access_limited_count": source_policy_public_code_refresh.get(
                    "latest_external_probe_access_limited_count"
                ),
                "global_absence_proved": source_policy_public_code_refresh.get(
                    "latest_external_probe_global_absence_proved"
                ),
                "reopen_triggered": source_policy_public_code_refresh.get(
                    "latest_external_probe_source_policy_reopen_triggered"
                ),
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
            "current_archive_usable_as_full_source_policy_runner_archive": (
                full_source_runner_gap.get("closure_conditions", {}).get(
                    "can_use_current_archive_as_full_source_policy_runner_archive"
                )
            ),
            "full_source_policy_runner_package_ready": runner_centered.get(
                "full_source_policy_runner_package_ready"
            ),
            "narrowed_repro_code_archive_ready": narrowed_repro_code_archive_ready,
            "narrowed_repro_code_archive_submission_ready": narrowed_repro_code_archive.get(
                "submission_ready"
            ),
            "source_policy_closed_ratio": full_source_policy_row_provenance.get(
                "source_policy_closed_ratio"
            ),
            "remaining_source_policy_rows_to_close": full_source_runner_gap.get(
                "closure_conditions", {}
            ).get("remaining_source_policy_rows_to_close"),
            "safe_current_archive_use": (
                "narrowed_claim_replay_and_audit_provenance_only"
            ),
            "action_boundary": full_source_runner_gap.get("action_boundary"),
        },
    }
    blocker_safe_next_actions_by_id = {
        item["id"]: safe_actions_without_b4_opt_in for item in open_blockers
    }
    blocker_opt_in_required_actions_by_id = {
        "OC4": opt_in_required_actions,
        "OC6": [],
        "OC12": opt_in_required_actions,
    }
    source_archive_blocker_required_to_close_by_id = (
        full_source_runner_gap.get("archive_blocker_required_to_close_by_id")
        or full_source_runner_gap.get("blocker_required_to_close_by_id")
    )
    source_archive_blocker_safe_next_actions_by_id = (
        full_source_runner_gap.get("archive_blocker_safe_next_actions_by_id")
        or full_source_runner_gap.get("blocker_safe_next_actions_by_id")
    )
    source_archive_blocker_opt_in_required_actions_by_id = (
        full_source_runner_gap.get("archive_blocker_opt_in_required_actions_by_id")
        or full_source_runner_gap.get("blocker_opt_in_required_actions_by_id")
    )
    if (
        set(source_archive_blocker_required_to_close_by_id or {}) == {"OC4", "OC6", "OC12"}
        and set(source_archive_blocker_safe_next_actions_by_id or {}) == {"OC4", "OC6", "OC12"}
        and set(source_archive_blocker_opt_in_required_actions_by_id or {}) == {"OC4", "OC6", "OC12"}
    ):
        blocker_required_to_close_by_id = {
            req_id: source_archive_blocker_required_to_close_by_id[req_id]
            for req_id in ["OC4", "OC6", "OC12"]
        }
        blocker_safe_next_actions_by_id = {
            req_id: source_archive_blocker_safe_next_actions_by_id[req_id]
            for req_id in ["OC4", "OC6", "OC12"]
        }
        blocker_opt_in_required_actions_by_id = {
            req_id: source_archive_blocker_opt_in_required_actions_by_id[req_id]
            for req_id in ["OC4", "OC6", "OC12"]
        }
    for item in open_blockers:
        item_id = item["id"]
        item["required_to_close"] = blocker_required_to_close_by_id.get(item_id, {})
        item["safe_next_actions"] = blocker_safe_next_actions_by_id.get(item_id, [])
        item["opt_in_required_actions"] = blocker_opt_in_required_actions_by_id.get(
            item_id, []
        )
    blockers_by_id = {item["id"]: item for item in open_blockers}
    blocker_status_by_id = {item["id"]: item["status"] for item in open_blockers}
    blocker_next_actions_by_id = {
        item["id"]: item["next_to_close"] for item in open_blockers
    }
    blocker_open_by_id = {
        "OC4": full_source_policy_row_provenance.get("oc4_blocker_open"),
        "OC6": oc6_source_equivalent_reopen.get("oc6_blocker_open"),
        "OC12": full_source_runner_gap.get("oc12_blocker_open"),
    }
    blocker_closure_decision_by_id = {
        "OC4": full_source_policy_row_provenance.get("oc4_closure_decision"),
        "OC6": oc6_source_equivalent_reopen.get("oc6_closure_decision"),
        "OC12": full_source_runner_gap.get("oc12_closure_decision"),
    }
    blocker_closure_allowed_by_id = {
        "OC4": full_source_policy_row_provenance.get("oc4_closure_allowed_now"),
        "OC6": oc6_source_equivalent_reopen.get("oc6_closure_allowed_now"),
        "OC12": full_source_runner_gap.get("oc12_closure_allowed_now"),
    }
    blocker_source_alias_by_id = {
        "OC4": {
            "blocker_id": full_source_policy_row_provenance.get("oc4_blocker_id"),
            "blocker_status": full_source_policy_row_provenance.get("oc4_blocker_status"),
            "blocker_open": full_source_policy_row_provenance.get("oc4_blocker_open"),
            "closure_decision": full_source_policy_row_provenance.get("oc4_closure_decision"),
            "closure_allowed_now": full_source_policy_row_provenance.get(
                "oc4_closure_allowed_now"
            ),
            "ready_commands_mapped_rows": full_source_policy_row_provenance.get(
                "ready_commands_mapped_rows"
            ),
            "traceability_unique_traced_declared_mismatch": full_source_policy_row_provenance.get(
                "traceability_unique_traced_declared_mismatch"
            ),
        },
        "OC6": {
            "blocker_id": oc6_source_equivalent_reopen.get("oc6_blocker_id"),
            "blocker_status": oc6_source_equivalent_reopen.get("oc6_blocker_status"),
            "blocker_open": oc6_source_equivalent_reopen.get("oc6_blocker_open"),
            "closure_decision": oc6_source_equivalent_reopen.get("oc6_closure_decision"),
            "closure_allowed_now": oc6_source_equivalent_reopen.get(
                "oc6_closure_allowed_now"
            ),
            "reopen_condition": oc6_source_equivalent_reopen.get("reopen_condition"),
            "latest_external_probe_boundary": oc6_source_equivalent_reopen.get(
                "latest_external_probe_boundary", {}
            ).get("marker"),
        },
        "OC12": {
            "blocker_id": full_source_runner_gap.get("oc12_blocker_id"),
            "blocker_status": full_source_runner_gap.get("oc12_blocker_status"),
            "blocker_open": full_source_runner_gap.get("oc12_blocker_open"),
            "closure_decision": full_source_runner_gap.get("oc12_closure_decision"),
            "closure_allowed_now": full_source_runner_gap.get("oc12_closure_allowed_now"),
            "current_archive_usable_as_full_source_policy_runner_archive": (
                full_source_runner_gap.get(
                    "current_archive_usable_as_full_source_policy_runner_archive"
                )
            ),
            "safe_current_use": full_source_runner_gap.get("safe_current_use"),
            "primary_submission_package_allowed": full_source_runner_gap.get(
                "primary_submission_package_allowed"
            ),
        },
    }

    audit = {
        "schema": "objective-completion-audit-v1",
        "status": "complete" if objective_complete else "not_complete_submission_standard_open",
        "read_only": True,
        "objective_complete": objective_complete,
        "submission_ready": False,
        "blocking_open_count": len(blocking_open),
        "blocking_open": len(blocking_open),
        "blocking_requirement_ids": blocking_requirement_ids,
        "blocking_ids": blocking_requirement_ids,
        "open_blocker_ids": open_blocker_ids,
        "source_policy_execution_invoked": source_policy_execution_invoked,
        "source_policy_execution_allowed_now": source_policy_execution_allowed_now,
        "exact_b4_opt_in_required_for_execution": exact_b4_opt_in_required_for_execution,
        "safe_action_ids": safe_action_ids,
        "opt_in_action_ids": opt_in_action_ids,
        "next_safe_action_ids": safe_action_ids,
        "safe_actions_without_b4_opt_in": safe_actions_without_b4_opt_in,
        "opt_in_required_actions": opt_in_required_actions,
        "required_user_approval_statement": required_user_approval_statement,
        "guarded_execution_driver": guarded_execution_driver,
        "b4_guarded_driver_refusal_boundary_audit_20260621": b4_guarded_refusal_boundary_tuple,
        "b4_guarded_driver_refusal_boundary_status": b4_guarded_refusal.get("status"),
        "b4_guarded_driver_refusal_boundary_marker": b4_guarded_refusal.get("marker"),
        "run_v047_invoked": run_v047_invoked,
        "heavy_numerical_run_invoked": heavy_numerical_run_invoked,
        "v048_runner_invoked": v048_runner_invoked,
        "open_blockers": open_blockers,
        "blockers": open_blockers,
        "blockers_by_id": blockers_by_id,
        "blocker_status_by_id": blocker_status_by_id,
        "blocker_open_by_id": blocker_open_by_id,
        "blocker_closure_decision_by_id": blocker_closure_decision_by_id,
        "blocker_closure_allowed_by_id": blocker_closure_allowed_by_id,
        "blocker_source_alias_by_id": blocker_source_alias_by_id,
        "blocker_next_actions_by_id": blocker_next_actions_by_id,
        "blocker_required_to_close_by_id": blocker_required_to_close_by_id,
        "blocker_safe_next_actions_by_id": blocker_safe_next_actions_by_id,
        "blocker_opt_in_required_actions_by_id": blocker_opt_in_required_actions_by_id,
        "oc4_blocker_id": blocker_source_alias_by_id["OC4"]["blocker_id"],
        "oc4_blocker_status": blocker_source_alias_by_id["OC4"]["blocker_status"],
        "oc4_blocker_open": blocker_source_alias_by_id["OC4"]["blocker_open"],
        "oc4_closure_decision": blocker_source_alias_by_id["OC4"]["closure_decision"],
        "oc4_closure_allowed_now": blocker_source_alias_by_id["OC4"][
            "closure_allowed_now"
        ],
        "oc4_ready_commands_mapped_rows": blocker_source_alias_by_id["OC4"][
            "ready_commands_mapped_rows"
        ],
        "oc4_traceability_unique_traced_declared_mismatch": blocker_source_alias_by_id[
            "OC4"
        ]["traceability_unique_traced_declared_mismatch"],
        "oc6_blocker_id": blocker_source_alias_by_id["OC6"]["blocker_id"],
        "oc6_blocker_status": blocker_source_alias_by_id["OC6"]["blocker_status"],
        "oc6_blocker_open": blocker_source_alias_by_id["OC6"]["blocker_open"],
        "oc6_closure_decision": blocker_source_alias_by_id["OC6"]["closure_decision"],
        "oc6_closure_allowed_now": blocker_source_alias_by_id["OC6"][
            "closure_allowed_now"
        ],
        "oc6_reopen_condition": blocker_source_alias_by_id["OC6"]["reopen_condition"],
        "oc6_latest_external_probe_boundary": oc6_source_equivalent_reopen.get(
            "latest_external_probe_boundary"
        ),
        "oc6_latest_external_probe_boundary_marker": blocker_source_alias_by_id["OC6"][
            "latest_external_probe_boundary"
        ],
        "oc12_blocker_id": blocker_source_alias_by_id["OC12"]["blocker_id"],
        "oc12_blocker_status": blocker_source_alias_by_id["OC12"]["blocker_status"],
        "oc12_blocker_open": blocker_source_alias_by_id["OC12"]["blocker_open"],
        "oc12_closure_decision": blocker_source_alias_by_id["OC12"]["closure_decision"],
        "oc12_closure_allowed_now": blocker_source_alias_by_id["OC12"][
            "closure_allowed_now"
        ],
        "oc12_current_archive_usable_as_full_source_policy_runner_archive": (
            blocker_source_alias_by_id["OC12"][
                "current_archive_usable_as_full_source_policy_runner_archive"
            ]
        ),
        "oc12_safe_current_use": blocker_source_alias_by_id["OC12"][
            "safe_current_use"
        ],
        "oc12_primary_submission_package_allowed": blocker_source_alias_by_id["OC12"][
            "primary_submission_package_allowed"
        ],
        "source_policy_closed": source_policy_closed,
        "source_policy_closed_rows": full_source_policy_row_provenance.get("source_policy_rows_closed"),
        "source_policy_total_rows": full_source_policy_row_provenance.get("source_policy_rows_total"),
        "source_policy_closed_ratio": full_source_policy_row_provenance.get("source_policy_closed_ratio"),
        "b2_source_policy_closed": b2_source_policy_rows_closed,
        "b2_source_policy_rows_closed": b2_source_policy_rows_closed,
        "b2_active_suites_closed": b2_active_suites_closed,
        "b2_active_suites_closed_by_demotion": b2_active_suites_closed_by_demotion,
        "tfe_runner_closed": tfe_runner_closed,
        "minimal_code_ready": minimal_code_ready,
        "minimal_reproducible_submission_code_ready": minimal_code_ready,
        "strict_proof_writing_submission_boundary": strict_proof_writing_submission_boundary,
        "completion_decision": {
            "can_mark_goal_complete": objective_complete,
            "reason": (
                "all blocking objective requirements are satisfied"
                if objective_complete
                else "blocking objective requirements remain open or partial"
            ),
            "blocking_requirement_ids": blocking_requirement_ids,
            "validator_pass_means": (
                "current artifacts are internally consistent with the recorded boundary; "
                "it does not prove the full paper objective while blocking requirements remain"
            ),
        },
        "summary": {
            "requirement_count": len(requirements),
            "satisfied_count": len(satisfied),
            "partial_count": len(partial),
            "open_count": len(open_items),
            "blocking_open_count": len(blocking_open),
            "blocking_open": len(blocking_open),
            "blocking_ids": blocking_requirement_ids,
            "open_blocker_ids": open_blocker_ids,
            "source_policy_execution_invoked": source_policy_execution_invoked,
            "source_policy_execution_allowed_now": source_policy_execution_allowed_now,
            "exact_b4_opt_in_required_for_execution": exact_b4_opt_in_required_for_execution,
            "safe_action_ids": safe_action_ids,
            "opt_in_action_ids": opt_in_action_ids,
            "next_safe_action_ids": safe_action_ids,
            "safe_actions_without_b4_opt_in_count": len(safe_actions_without_b4_opt_in),
            "opt_in_required_actions_count": len(opt_in_required_actions),
            "required_user_approval_statement": required_user_approval_statement,
            "guarded_execution_driver": guarded_execution_driver,
            "run_v047_invoked": run_v047_invoked,
            "heavy_numerical_run_invoked": heavy_numerical_run_invoked,
            "v048_runner_invoked": v048_runner_invoked,
            "core_matrix_ready": core_matrix_ready,
            "traceability_ready": traceability_ready,
            "common_reference_closed": common_reference_closed,
            "source_policy_closed": source_policy_closed,
            "source_policy_closed_rows": full_source_policy_row_provenance.get("source_policy_rows_closed"),
            "source_policy_total_rows": full_source_policy_row_provenance.get("source_policy_rows_total"),
            "source_policy_closed_ratio": full_source_policy_row_provenance.get("source_policy_closed_ratio"),
            "ra_hi_closeout_status": ra_hi_closeout.get("status"),
            "ra_hi_closeout_source_policy_rows_total": ra_hi_closeout.get("coverage", {}).get(
                "source_policy_rows_total"
            ),
            "ra_hi_closeout_ra_rows": ra_hi_closeout.get("coverage", {}).get("ra2021_rows"),
            "ra_hi_closeout_hi_rows": ra_hi_closeout.get("coverage", {}).get("hi2022_rows"),
            "ra_hi_closeout_ready_command_count": ra_hi_closeout.get("coverage", {}).get(
                "ready_command_count"
            ),
            "ra_hi_closeout_ready_command_mapped_rows": ra_hi_closeout.get("coverage", {}).get(
                "ready_command_mapped_external_rows"
            ),
            "ra_hi_closeout_source_policy_rows_promoted": ra_hi_closeout.get("coverage", {}).get(
                "source_policy_rows_promoted"
            ),
            "ra_hi_closeout_source_policy_rows_completed": ra_hi_closeout.get("coverage", {}).get(
                "source_policy_rows_completed"
            ),
            "ra_hi_closeout_external_superiority_ready_rows": ra_hi_closeout.get("coverage", {}).get(
                "external_superiority_ready_rows"
            ),
            "ra_hi_closeout_opt_in_required": ra_hi_closeout.get("guarded_execution_boundary", {}).get(
                "explicit_user_opt_in_required_before_any_command"
            ),
            "ra_hi_closeout_exact_approval_statement": ra_hi_closeout.get(
                "guarded_execution_boundary", {}
            ).get("exact_required_user_approval_statement"),
            "ra_hi_closeout_execution_invoked": ra_hi_closeout.get("guarded_execution_boundary", {}).get(
                "execution_invoked_by_packet"
            ),
            "ra_hi_closeout_b4_can_close": ra_hi_closeout.get("not_promoted_disposition", {}).get(
                "b4_can_close_from_this_checklist"
            ),
            "ra_hi_closeout_b7_can_close": ra_hi_closeout.get("not_promoted_disposition", {}).get(
                "b7_can_close_from_this_checklist"
            ),
            "ra_hi_current_evidence_terminal_not_promotable_rows": ra_hi_promotion_matrix.get(
                "current_evidence_terminal_not_promotable_rows"
            ),
            "ra_hi_future_promotion_requires_authorized_execution_or_new_artifact_rows": (
                ra_hi_promotion_matrix.get(
                    "future_promotion_requires_authorized_execution_or_new_artifact_rows"
                )
            ),
            "ra_hi_source_policy_reproduction_complete_rows": ra_hi_promotion_matrix.get(
                "source_policy_reproduction_complete_rows"
            ),
            "source_policy_execution_handoff_status": b4_execution_handoff.get("status"),
            "source_policy_execution_handoff_authorized": b4_execution_handoff.get(
                "execution_authorized"
            ),
            "source_policy_execution_handoff_commands_not_run": b4_execution_handoff.get(
                "commands_not_run_by_handoff"
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
            "source_policy_execution_handoff_ready_command_count": b4_execution_handoff.get(
                "ready_command_count"
            ),
            "source_policy_execution_handoff_ready_command_mapped_rows": b4_execution_handoff.get(
                "ready_command_mapped_external_rows"
            ),
            "source_policy_execution_handoff_opt_in_required_command_count": b4_execution_handoff.get(
                "opt_in_required_command_count"
            ),
            "source_policy_execution_handoff_opt_in_required_mapped_rows": b4_execution_handoff.get(
                "opt_in_required_mapped_external_rows"
            ),
            "source_policy_execution_handoff_terminal_unable_rows": b4_execution_handoff.get(
                "terminal_unable_to_reproduce_rows"
            ),
            "b4_guarded_driver_refusal_boundary_20260621_status": b4_guarded_refusal.get(
                "status"
            ),
            "b4_guarded_driver_no_opt_in_refusal_proved_static": b4_guarded_refusal.get(
                "no_opt_in_refusal_proved_static"
            ),
            "b4_guarded_driver_wrong_approval_refusal_proved_static": b4_guarded_refusal.get(
                "wrong_approval_refusal_proved_static"
            ),
            "b4_guarded_driver_refusal_exit_code": b4_guarded_refusal.get(
                "refusal_exit_code"
            ),
            "b4_guarded_driver_pre_guard_command_count": b4_guarded_refusal.get(
                "pre_guard_command_count"
            ),
            "b4_guarded_driver_post_guard_source_policy_command_count": b4_guarded_refusal.get(
                "post_guard_source_policy_command_count"
            ),
            "b4_guarded_driver_invoked_by_audit": b4_guarded_refusal.get(
                "driver_invoked_by_audit"
            ),
            "b4_guarded_driver_source_policy_execution_invoked": b4_guarded_refusal.get(
                "source_policy_execution_invoked"
            ),
            "b4_guarded_driver_submission_ready": b4_guarded_refusal.get(
                "submission_ready"
            ),
            "b4_guarded_driver_refusal_boundary_marker": b4_guarded_refusal.get(
                "marker"
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
            "full_source_policy_row_provenance_handoff_status": full_source_policy_row_provenance.get(
                "source_policy_execution_handoff", {}
            ).get("status"),
            "full_source_policy_row_provenance_handoff_authorized": full_source_policy_row_provenance.get(
                "source_policy_execution_handoff", {}
            ).get("execution_authorized"),
            "full_source_policy_row_provenance_handoff_commands_not_run": full_source_policy_row_provenance.get(
                "source_policy_execution_handoff", {}
            ).get("commands_not_run_by_handoff"),
            "full_source_policy_row_provenance_handoff_exact_approval": full_source_policy_row_provenance.get(
                "source_policy_execution_handoff", {}
            ).get("exact_required_user_approval_statement"),
            "full_source_policy_row_provenance_handoff_driver": full_source_policy_row_provenance.get(
                "source_policy_execution_handoff", {}
            ).get("guarded_execution_driver"),
            "full_source_policy_row_provenance_handoff_driver_requires_exact": full_source_policy_row_provenance.get(
                "source_policy_execution_handoff", {}
            ).get("driver_requires_exact_approval"),
            "full_source_policy_row_provenance_handoff_driver_does_not_authorize": full_source_policy_row_provenance.get(
                "source_policy_execution_handoff", {}
            ).get("driver_does_not_authorize_execution"),
            "full_source_policy_row_provenance_handoff_opt_in_commands": full_source_policy_row_provenance.get(
                "source_policy_execution_handoff", {}
            ).get("opt_in_required_command_count"),
            "full_source_policy_row_provenance_handoff_mapped_rows": full_source_policy_row_provenance.get(
                "source_policy_execution_handoff", {}
            ).get("opt_in_required_mapped_external_rows"),
            "full_source_policy_row_provenance_handoff_terminal_unable_rows": full_source_policy_row_provenance.get(
                "source_policy_execution_handoff", {}
            ).get("terminal_unable_to_reproduce_rows"),
            "full_source_policy_runner_archive_gap_status": full_source_runner_gap.get("status"),
            "full_source_policy_runner_archive_gap_ready_now": full_source_runner_gap.get(
                "closure_conditions", {}
            ).get("full_archive_ready_now"),
            "full_source_policy_runner_archive_gap_current_archive_use": full_source_runner_gap.get(
                "closure_conditions", {}
            ).get("can_use_current_archive_as_full_source_policy_runner_archive"),
            "full_source_policy_runner_archive_gap_can_use_current_archive_as_full_source_policy_runner_archive": (
                full_source_runner_gap.get("closure_conditions", {}).get(
                    "can_use_current_archive_as_full_source_policy_runner_archive"
                )
            ),
            "full_source_policy_runner_archive_gap_safe_current_archive_use": (
                "narrowed_claim_replay_and_audit_provenance_only"
            ),
            "full_source_policy_runner_archive_gap_source_policy_rows_closed": full_source_runner_gap.get(
                "source_policy_rows", {}
            ).get("closed"),
            "full_source_policy_runner_archive_gap_source_policy_rows_total": full_source_runner_gap.get(
                "source_policy_rows", {}
            ).get("total"),
            "full_source_policy_runner_archive_gap_remaining_rows_to_close": full_source_runner_gap.get(
                "closure_conditions", {}
            ).get("remaining_source_policy_rows_to_close"),
            "full_source_policy_runner_archive_gap_terminal_unable_rows": full_source_runner_gap.get(
                "closure_conditions", {}
            ).get("terminal_unable_to_reproduce_rows"),
            "full_source_policy_runner_archive_gap_ra_hi_open_rows": full_source_runner_gap.get(
                "closure_conditions", {}
            ).get("ra_hi_rows_requiring_authorized_closeout_or_new_artifact"),
            "full_source_policy_runner_archive_gap_terminal_reopen_conditions": (
                full_source_runner_terminal_reopen_conditions
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
                full_source_runner_terminal_reopen_conditions.get("tfe2026_original_pendulum")
            ),
            "full_source_policy_runner_archive_gap_vp2024_reopen_condition": (
                full_source_runner_terminal_reopen_conditions.get("vp2024_velocity_partitioning")
            ),
            "full_source_policy_runner_archive_gap_required_approval_statement": (
                full_source_runner_required_approval_statement
            ),
            "full_source_policy_runner_archive_gap_action_boundary": full_source_runner_gap.get(
                "action_boundary"
            ),
            "full_source_policy_runner_archive_gap_safe_without_b4_opt_in_count": (
                full_source_runner_gap.get("safe_without_b4_opt_in_count")
            ),
            "full_source_policy_runner_archive_gap_opt_in_required_action_count": (
                full_source_runner_gap.get("opt_in_required_action_count")
            ),
            "full_source_policy_runner_archive_gap_source_policy_execution_allowed_now": (
                full_source_runner_gap.get("source_policy_execution_allowed_now")
            ),
            "full_source_policy_runner_archive_gap_source_policy_execution_invoked": (
                full_source_runner_gap.get("source_policy_execution_invoked")
            ),
            "full_source_policy_runner_archive_gap_exact_b4_opt_in_required_for_execution": (
                full_source_runner_gap.get("exact_b4_opt_in_required_for_execution")
            ),
            "full_source_policy_runner_archive_gap_opt_in_required_command_count": (
                full_source_runner_gap.get("opt_in_required_command_count")
            ),
            "full_source_policy_runner_archive_gap_opt_in_required_mapped_external_rows": (
                full_source_runner_gap.get("opt_in_required_mapped_external_rows")
            ),
            "full_source_policy_runner_archive_gap_safe_action_ids": [
                item.get("id")
                for item in full_source_runner_gap.get("safe_next_actions_without_b4_opt_in", [])
                if isinstance(item, dict)
            ]
            if full_source_runner_gap.get("safe_action_ids") is None
            else full_source_runner_gap.get("safe_action_ids"),
            "full_source_policy_runner_archive_gap_opt_in_action_ids": [
                item.get("id")
                for item in full_source_runner_gap.get("opt_in_required_actions", [])
                if isinstance(item, dict)
            ]
            if full_source_runner_gap.get("opt_in_action_ids") is None
            else full_source_runner_gap.get("opt_in_action_ids"),
            "full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_status": (
                full_source_runner_gap.get("closure_conditions", {}).get(
                    "tfe_runner_contract_preflight_status"
                )
            ),
            "full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_entrypoints": (
                full_source_runner_gap.get("closure_conditions", {}).get(
                    "tfe_runner_contract_preflight_entrypoints"
                )
            ),
            "full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_candidate_backed": (
                full_source_runner_gap.get("closure_conditions", {}).get(
                    "tfe_runner_contract_preflight_candidate_backed"
                )
            ),
            "full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_source_policy_rows_completed": (
                full_source_runner_gap.get("closure_conditions", {}).get(
                    "tfe_runner_contract_preflight_source_policy_rows_completed"
                )
            ),
            "full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_execution_blocks": (
                full_source_runner_gap.get("closure_conditions", {}).get(
                    "tfe_runner_contract_preflight_execution_blocks"
                )
            ),
            "full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_safe_use": (
                full_source_runner_gap.get("closure_conditions", {}).get(
                    "tfe_runner_contract_preflight_safe_use"
                )
            ),
            "b2_source_policy_closed": b2_source_policy_rows_closed,
            "b2_source_policy_rows_closed": b2_source_policy_rows_closed,
            "b2_active_suites_closed": b2_active_suites_closed,
            "b2_active_suites_closed_by_demotion": b2_active_suites_closed_by_demotion,
            "b2_can_close_now": b2_remaining.get("b2_can_close_now"),
            "b2_active_flagged_rows": b2_remaining.get("active_flagged_row_count"),
            "b2_demoted_flagged_rows": b2_remaining.get("demoted_flagged_row_count"),
            "b2_remaining_requirements": b2_remaining.get("b2_remaining_requirements"),
            "b2_external_superiority_claim_allowed": b2_remaining.get("external_superiority_claim_allowed"),
            "tfe_runner_closed": tfe_runner_closed,
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
            "tfe_dae_runner_contract_gap_status": tfe_dae_gap.get("status"),
            "tfe_dae_runner_contract_gap_missing_block_count": tfe_dae_gap.get(
                "missing_contract_block_count"
            ),
            "tfe_dae_runner_contract_gap_missing_block_ids": tfe_dae_missing_block_ids,
            "tfe_dae_runner_contract_gap_nonheavy_blocks": tfe_dae_gap.get(
                "nonheavy_missing_contract_blocks"
            ),
            "tfe_dae_runner_contract_gap_nonheavy_disposition_ids": tfe_dae_nonheavy_disposition_ids,
            "tfe_dae_runner_contract_gap_nonheavy_dispositioned_by_demotion": tfe_dae_gap.get(
                "nonheavy_missing_contract_blocks_dispositioned_by_demotion"
            ),
            "tfe_dae_runner_contract_gap_nonheavy_demotion_does_not_close_source_policy": tfe_dae_gap.get(
                "nonheavy_demotion_does_not_close_source_policy"
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
            "tfe_dae_runner_contract_gap_execution_block_count": tfe_dae_gap.get(
                "source_policy_execution_missing_contract_block_count"
            ),
            "tfe_dae_runner_contract_gap_candidate_backed_non_equivalent_runner_blocks": (
                tfe_dae_gap.get("candidate_backed_non_equivalent_runner_block_ids")
            ),
            "tfe_dae_runner_contract_gap_candidate_backed_non_equivalent_runner_block_count": (
                tfe_dae_gap.get("candidate_backed_non_equivalent_runner_block_count")
            ),
            "tfe_dae_runner_contract_gap_ready_to_execute_source_policy_now": tfe_dae_gap.get(
                "ready_to_execute_source_policy_now"
            ),
            "tfe_dae_runner_contract_gap_heavy_run_invoked": tfe_dae_gap.get(
                "heavy_numerical_run_invoked"
            ),
            "tfe_source_policy_execution_preflight_status": tfe_execution_preflight.get("status"),
            "tfe_source_policy_execution_preflight_current_route": tfe_execution_preflight.get(
                "current_route"
            ),
            "tfe_source_policy_execution_preflight_reopen_condition": tfe_execution_preflight.get(
                "reopen_condition"
            ),
            "tfe_source_policy_execution_preflight_opt_in_required": tfe_execution_preflight.get(
                "explicit_user_opt_in_required"
            ),
            "tfe_source_policy_execution_preflight_nonheavy_dispositioned": (
                tfe_execution_preflight.get("nonheavy_blocks_dispositioned_by_demotion")
            ),
            "tfe_source_policy_execution_preflight_execution_block_count": (
                tfe_execution_preflight.get("execution_block_count")
            ),
            "tfe_source_policy_execution_preflight_can_promote_rows_now": (
                tfe_execution_preflight.get("can_promote_any_tfe_source_policy_row_now")
            ),
            "tfe_source_policy_execution_preflight_ready_now": tfe_execution_preflight.get(
                "ready_to_execute_source_policy_now"
            ),
            "tfe_self_reproduction_status": tfe_self_reproduction.get("status"),
            "tfe_self_reproduction_attempted_not_reproducible_rows": (
                tfe_self_reproduction.get("attempted_not_reproducible_rows")
            ),
            "tfe_self_reproduction_unable_to_reproduce_rows": (
                tfe_self_reproduction.get("unable_to_reproduce_rows")
            ),
            "tfe_self_reproduction_source_policy_closed": tfe_self_reproduction.get(
                "source_policy_closed"
            ),
            "tfe_self_reproduction_source_policy_closed_ratio": tfe_self_reproduction.get(
                "source_policy_closed_ratio"
            ),
            "tfe_self_reproduction_public_code_recheck_status": tfe_self_reproduction.get(
                "public_code_recheck_status"
            ),
            "tfe_self_reproduction_reopen_condition": tfe_self_reproduction.get(
                "reopen_condition"
            ),
            "tfe_self_reproduction_preflight_status": tfe_self_reproduction.get(
                "source_policy_execution_preflight_status"
            ),
            "tfe_public_code_refresh_20260620_status": source_policy_public_code_refresh.get(
                "status"
            ),
            "tfe_public_code_refresh_20260620_rows": source_policy_public_code_refresh.get("rows"),
            "tfe_public_code_refresh_20260620_current_queries": (
                source_policy_public_code_refresh.get("current_queries")
            ),
            "tfe_public_code_refresh_20260620_positive_artifact_rows": (
                source_policy_public_code_refresh.get("positive_public_code_artifact_rows")
            ),
            "tfe_public_code_refresh_20260620_source_policy_closed_ratio": (
                source_policy_public_code_refresh.get("source_policy_closed_ratio")
            ),
            "tfe_public_code_refresh_20260620_latest_external_probe_date": (
                source_policy_public_code_refresh.get("latest_external_probe_date_checked")
            ),
            "tfe_public_code_refresh_20260620_latest_external_probe_count": (
                source_policy_public_code_refresh.get("latest_external_probe_count")
            ),
            "tfe_public_code_refresh_20260620_latest_external_probe_positive_artifact_rows": (
                source_policy_public_code_refresh.get(
                    "latest_external_probe_positive_public_code_artifact_rows"
                )
            ),
            "tfe_public_code_refresh_20260620_latest_external_probe_source_policy_rows_closed": (
                source_policy_public_code_refresh.get(
                    "latest_external_probe_source_policy_rows_closed"
                )
            ),
            "tfe_public_code_refresh_20260620_latest_external_probe_access_limited_count": (
                source_policy_public_code_refresh.get(
                    "latest_external_probe_access_limited_count"
                )
            ),
            "tfe_public_code_refresh_20260620_latest_external_probe_global_absence_proved": (
                source_policy_public_code_refresh.get(
                    "latest_external_probe_global_absence_proved"
                )
            ),
            "tfe_public_code_refresh_20260620_latest_external_probe_reopen_triggered": (
                source_policy_public_code_refresh.get(
                    "latest_external_probe_source_policy_reopen_triggered"
                )
            ),
            "oc6_external_source_artifact_recheck_20260621_status": (
                oc6_external_recheck.get("status")
            ),
            "oc6_external_source_artifact_recheck_20260621_date": (
                oc6_external_recheck.get("date_checked")
            ),
            "oc6_external_source_artifact_recheck_20260621_query_count": (
                oc6_external_recheck.get("query_count")
            ),
            "oc6_external_source_artifact_recheck_20260621_positive_artifact_rows": (
                oc6_external_recheck.get("positive_public_code_artifact_rows")
            ),
            "oc6_external_source_artifact_recheck_20260621_source_equivalent_artifact_rows": (
                oc6_external_recheck.get("source_code_equivalent_artifact_rows")
            ),
            "oc6_external_source_artifact_recheck_20260621_source_policy_rows_closed": (
                oc6_external_recheck.get("source_policy_rows_closed_by_recheck")
            ),
            "oc6_external_source_artifact_recheck_20260621_reopen_triggered": (
                oc6_external_recheck.get("source_policy_reopen_triggered")
            ),
            "oc6_external_source_artifact_recheck_20260621_global_absence_proved": (
                oc6_external_recheck.get("global_absence_proved")
            ),
            "oc6_tfe_publisher_artifact_availability_20260621_status": (
                oc6_publisher_availability.get("status")
            ),
            "oc6_tfe_publisher_artifact_availability_20260621_date": (
                oc6_publisher_availability.get("date_checked")
            ),
            "oc6_tfe_publisher_artifact_availability_20260621_official_article_checked": (
                oc6_publisher_availability.get("official_article_checked")
            ),
            "oc6_tfe_publisher_artifact_availability_20260621_source_artifact_signal_count": (
                oc6_publisher_availability.get("source_article", {}).get(
                    "source_artifact_signal_count"
                )
            ),
            "oc6_tfe_publisher_artifact_availability_20260621_positive_artifact_rows": (
                oc6_publisher_availability.get("positive_public_code_artifact_rows")
            ),
            "oc6_tfe_publisher_artifact_availability_20260621_source_equivalent_artifact_rows": (
                oc6_publisher_availability.get("source_code_equivalent_artifact_rows")
            ),
            "oc6_tfe_publisher_artifact_availability_20260621_source_policy_rows_closed": (
                oc6_publisher_availability.get(
                    "source_policy_rows_closed_by_publisher_audit"
                )
            ),
            "oc6_tfe_publisher_artifact_availability_20260621_reopen_triggered": (
                oc6_publisher_availability.get("source_policy_reopen_triggered")
            ),
            "oc6_tfe_publisher_artifact_availability_20260621_global_absence_proved": (
                oc6_publisher_availability.get("global_absence_proved")
            ),
            "oc6_tfe_source_equivalent_artifact_request_packet_20260621_status": (
                oc6_source_equivalent_request_packet.get("status")
            ),
            "oc6_tfe_source_equivalent_artifact_request_packet_20260621_date": (
                oc6_source_equivalent_request_packet.get("date_prepared")
            ),
            "oc6_tfe_source_equivalent_artifact_request_packet_20260621_request_ready": (
                oc6_source_equivalent_request_packet.get("request_ready")
            ),
            "oc6_tfe_source_equivalent_artifact_request_packet_20260621_request_sent": (
                oc6_source_equivalent_request_packet.get("request_sent")
            ),
            "oc6_tfe_source_equivalent_artifact_request_packet_20260621_requested_artifact_count": (
                oc6_source_equivalent_request_packet.get("requested_artifact_count")
            ),
            "oc6_tfe_source_equivalent_artifact_request_packet_20260621_corresponding_author_email": (
                oc6_source_equivalent_request_packet.get("source_article", {}).get(
                    "corresponding_author_email"
                )
            ),
            "oc6_tfe_source_equivalent_artifact_request_packet_20260621_source_policy_rows_closed": (
                oc6_source_equivalent_request_packet.get("not_closing", {}).get(
                    "source_policy_rows_closed_by_packet"
                )
            ),
            "oc6_tfe_source_equivalent_artifact_request_packet_20260621_reopen_triggered": (
                oc6_source_equivalent_request_packet.get("not_closing", {}).get(
                    "source_policy_reopen_triggered"
                )
            ),
            "oc6_tfe_source_equivalent_artifact_request_packet_20260621_global_absence_proved": (
                oc6_source_equivalent_request_packet.get("not_closing", {}).get(
                    "global_absence_proved"
                )
            ),
            "oc6_tfe_source_equivalent_artifact_request_packet_20260621_submission_ready": (
                oc6_source_equivalent_request_packet.get("not_closing", {}).get(
                    "submission_ready"
                )
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
            "tfe_absolute_coordinate_planar_lift_trajectory_probe_implemented": tfe_model.get(
                "absolute_coordinate_planar_lift_trajectory_probe_implemented"
            ),
            "tfe_absolute_coordinate_planar_lift_trajectory_probe_rows": tfe_model.get(
                "absolute_coordinate_planar_lift_trajectory_probe_rows"
            ),
            "tfe_absolute_coordinate_planar_lift_trajectory_probe_metric_rows": tfe_model.get(
                "absolute_coordinate_planar_lift_trajectory_probe_metric_rows"
            ),
            "tfe_absolute_coordinate_planar_lift_trajectory_probe_source_policy_rows_completed": tfe_model.get(
                "absolute_coordinate_planar_lift_trajectory_probe_source_policy_rows_completed"
            ),
            "tfe_absolute_coordinate_planar_lift_trajectory_probe_dae_runner_equivalent": tfe_model.get(
                "absolute_coordinate_planar_lift_trajectory_probe_dae_runner_equivalent"
            ),
            "tfe_bounded_absolute_coordinate_dae_trajectory_runner_implemented": tfe_model.get(
                "bounded_absolute_coordinate_dae_trajectory_runner_implemented"
            ),
            "tfe_bounded_absolute_coordinate_dae_trajectory_runner_rows": tfe_model.get(
                "bounded_absolute_coordinate_dae_trajectory_runner_rows"
            ),
            "tfe_bounded_absolute_coordinate_dae_trajectory_runner_metric_rows": tfe_model.get(
                "bounded_absolute_coordinate_dae_trajectory_runner_metric_rows"
            ),
            "tfe_bounded_absolute_coordinate_dae_trajectory_runner_step_residual_rows": tfe_model.get(
                "bounded_absolute_coordinate_dae_trajectory_runner_step_residual_rows"
            ),
            "tfe_bounded_absolute_coordinate_dae_trajectory_runner_source_policy_rows_completed": tfe_model.get(
                "bounded_absolute_coordinate_dae_trajectory_runner_source_policy_rows_completed"
            ),
            "tfe_bounded_absolute_coordinate_dae_trajectory_runner_dae_runner_equivalent": tfe_model.get(
                "bounded_absolute_coordinate_dae_trajectory_runner_dae_runner_equivalent"
            ),
            "tfe_bounded_absolute_coordinate_dae_trajectory_runner_monolithic_integrator": tfe_model.get(
                "bounded_absolute_coordinate_dae_trajectory_runner_monolithic_integrator"
            ),
            "tfe_monolithic_absolute_coordinate_dae_candidate_runner_implemented": tfe_model.get(
                "monolithic_absolute_coordinate_dae_candidate_runner_implemented"
            ),
            "tfe_monolithic_absolute_coordinate_dae_candidate_runner_rows": tfe_model.get(
                "monolithic_absolute_coordinate_dae_candidate_runner_rows"
            ),
            "tfe_monolithic_absolute_coordinate_dae_candidate_runner_metric_rows": tfe_model.get(
                "monolithic_absolute_coordinate_dae_candidate_runner_metric_rows"
            ),
            "tfe_monolithic_absolute_coordinate_dae_candidate_runner_step_residual_rows": tfe_model.get(
                "monolithic_absolute_coordinate_dae_candidate_runner_step_residual_rows"
            ),
            "tfe_monolithic_absolute_coordinate_dae_candidate_runner_source_policy_rows_completed": (
                tfe_model.get(
                    "monolithic_absolute_coordinate_dae_candidate_runner_source_policy_rows_completed"
                )
            ),
            "tfe_monolithic_absolute_coordinate_dae_candidate_runner_dae_runner_equivalent": tfe_model.get(
                "monolithic_absolute_coordinate_dae_candidate_runner_dae_runner_equivalent"
            ),
            "tfe_monolithic_absolute_coordinate_dae_candidate_runner_monolithic_integrator": tfe_model.get(
                "monolithic_absolute_coordinate_dae_candidate_runner_monolithic_integrator"
            ),
            "tfe_source_method_candidate_runner_contract_implemented": tfe_model.get(
                "source_method_candidate_runner_contract_implemented"
            ),
            "tfe_source_method_candidate_runner_contract_rows": tfe_model.get(
                "source_method_candidate_runner_contract_rows"
            ),
            "tfe_source_method_candidate_runner_contract_source_policy_rows_completed": tfe_model.get(
                "source_method_candidate_runner_contract_source_policy_rows_completed"
            ),
            "tfe_source_method_candidate_runner_contract_method_equivalent": tfe_model.get(
                "source_method_candidate_runner_contract_method_equivalent"
            ),
            "tfe_source_method_candidate_runner_contract_dae_equivalent": tfe_model.get(
                "source_method_candidate_runner_contract_dae_equivalent"
            ),
            "tfe_dae_trajectory_bridge_contract_implemented": tfe_model.get(
                "dae_trajectory_bridge_contract_implemented"
            ),
            "tfe_dae_trajectory_bridge_contract_rows": tfe_model.get(
                "dae_trajectory_bridge_contract_rows"
            ),
            "tfe_dae_trajectory_bridge_contract_matched_rows": tfe_model.get(
                "dae_trajectory_bridge_contract_matched_rows"
            ),
            "tfe_dae_trajectory_bridge_contract_source_metric_rows": tfe_model.get(
                "dae_trajectory_bridge_contract_source_metric_rows"
            ),
            "tfe_dae_trajectory_bridge_contract_dae_metric_rows": tfe_model.get(
                "dae_trajectory_bridge_contract_dae_metric_rows"
            ),
            "tfe_dae_trajectory_bridge_contract_source_policy_rows_completed": tfe_model.get(
                "dae_trajectory_bridge_contract_source_policy_rows_completed"
            ),
            "tfe_dae_trajectory_bridge_contract_dae_runner_equivalent": tfe_model.get(
                "dae_trajectory_bridge_contract_dae_runner_equivalent"
            ),
            "tfe_dae_trajectory_bridge_contract_method_runner_equivalent": tfe_bridge.get(
                "source_policy_method_runner_equivalent"
            ),
            "tfe_dae_trajectory_bridge_contract_monolithic_integrator": tfe_model.get(
                "dae_trajectory_bridge_contract_monolithic_integrator"
            ),
            "tfe_dae_trajectory_bridge_contract_all_rows_finite": tfe_model.get(
                "dae_trajectory_bridge_contract_all_rows_finite"
            ),
            "tfe_dae_trajectory_bridge_contract_all_dae_residuals_below_1e_10": tfe_model.get(
                "dae_trajectory_bridge_contract_all_dae_residuals_below_1e_10"
            ),
            "tfe_dae_trajectory_bridge_contract_accepted_use": tfe_bridge.get("accepted_use"),
            "tfe_candidate_frictional_dae_trajectory_contract_implemented": tfe_model.get(
                "candidate_frictional_dae_trajectory_contract_implemented"
            ),
            "tfe_candidate_frictional_dae_trajectory_contract_rows": tfe_model.get(
                "candidate_frictional_dae_trajectory_contract_rows"
            ),
            "tfe_candidate_frictional_dae_trajectory_contract_step_residual_rows": tfe_model.get(
                "candidate_frictional_dae_trajectory_contract_step_residual_rows"
            ),
            "tfe_candidate_frictional_dae_trajectory_contract_source_policy_rows_completed": tfe_model.get(
                "candidate_frictional_dae_trajectory_contract_source_policy_rows_completed"
            ),
            "tfe_candidate_frictional_dae_trajectory_contract_dae_runner_equivalent": tfe_model.get(
                "candidate_frictional_dae_trajectory_contract_dae_runner_equivalent"
            ),
            "tfe_candidate_frictional_dae_trajectory_contract_method_runner_equivalent": tfe_model.get(
                "candidate_frictional_dae_trajectory_contract_method_runner_equivalent"
            ),
            "tfe_candidate_frictional_dae_trajectory_contract_brown_mcphee_source_code_equivalent_law": tfe_model.get(
                "candidate_frictional_dae_trajectory_contract_brown_mcphee_source_code_equivalent_law"
            ),
            "tfe_candidate_frictional_dae_trajectory_contract_monolithic_integrator": tfe_model.get(
                "candidate_frictional_dae_trajectory_contract_monolithic_integrator"
            ),
            "tfe_candidate_frictional_dae_trajectory_contract_all_rows_finite": tfe_model.get(
                "candidate_frictional_dae_trajectory_contract_all_rows_finite"
            ),
            "tfe_candidate_frictional_dae_trajectory_contract_all_dae_residuals_below_1e_9": tfe_model.get(
                "candidate_frictional_dae_trajectory_contract_all_dae_residuals_below_1e_9"
            ),
            "tfe_candidate_frictional_dae_trajectory_contract_all_friction_power_nonpositive": tfe_model.get(
                "candidate_frictional_dae_trajectory_contract_all_friction_power_nonpositive"
            ),
            "tfe_brown_mcphee_transition_velocity_sensitivity_rows": tfe_transition_velocity_sensitivity.get(
                "endpoint_delta_row_count"
            ),
            "tfe_brown_mcphee_transition_velocity_sensitivity_contract_rows": tfe_transition_velocity_sensitivity.get(
                "contract_row_count"
            ),
            "tfe_brown_mcphee_transition_velocity_sensitivity_source_policy_rows_completed": tfe_transition_velocity_sensitivity.get(
                "source_policy_rows_completed"
            ),
            "tfe_brown_mcphee_transition_velocity_sensitivity_material": tfe_transition_velocity_sensitivity.get(
                "missing_transition_velocity_is_numerically_material"
            ),
            "tfe_brown_mcphee_transition_velocity_sensitivity_equivalence_flags_false": tfe_transition_velocity_sensitivity.get(
                "all_contract_equivalence_flags_false"
            ),
            "tfe_brown_mcphee_transition_velocity_sensitivity_max_coordinate_delta": tfe_transition_velocity_sensitivity.get(
                "max_endpoint_coordinate_delta_vs_baseline"
            ),
            "tfe_brown_mcphee_transition_velocity_sensitivity_max_velocity_delta": tfe_transition_velocity_sensitivity.get(
                "max_endpoint_velocity_delta_vs_baseline"
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
            "tfe_source_comparator_candidate_runners_implemented": tfe_model.get(
                "source_comparator_candidate_runners_implemented"
            ),
            "tfe_source_policy_method_runner_equivalent": tfe_model.get(
                "source_policy_method_runner_equivalent"
            ),
            "tfe_m1_m2_m3_candidate_runner_smoke_implemented": tfe_model.get(
                "tfe_m1_m2_m3_candidate_runner_smoke_implemented"
            ),
            "tfe_m1_m2_m3_source_policy_runners_implemented": tfe_model.get(
                "tfe_m1_m2_m3_source_policy_runners_implemented"
            ),
            "gauss6_fullva_source_pendulum_candidate_smoke_implemented": tfe_model.get(
                "gauss6_fullva_source_pendulum_candidate_smoke_implemented"
            ),
            "gauss6_fullva_absolute_coordinate_source_policy_runner_implemented": tfe_model.get(
                "gauss6_fullva_absolute_coordinate_source_policy_runner_implemented"
            ),
            "gauss6_fullva_on_source_pendulum_implemented": tfe_model.get(
                "gauss6_fullva_on_source_pendulum_implemented"
            ),
            "gauss6_fullva_source_pendulum_candidate_rows": tfe_model.get(
                "gauss6_fullva_source_pendulum_candidate_rows"
            ),
            "gauss6_fullva_source_pendulum_candidate_source_policy_rows_completed": tfe_model.get(
                "gauss6_fullva_source_pendulum_candidate_source_policy_rows_completed"
            ),
            "gauss6_fullva_source_pendulum_candidate_method_equivalent": tfe_model.get(
                "gauss6_fullva_source_pendulum_candidate_method_equivalent"
            ),
            "gauss6_fullva_dae_candidate_contract_implemented": tfe_model.get(
                "gauss6_fullva_dae_candidate_contract_implemented"
            ),
            "gauss6_fullva_dae_candidate_contract_rows": tfe_model.get(
                "gauss6_fullva_dae_candidate_contract_rows"
            ),
            "gauss6_fullva_dae_candidate_contract_source_policy_rows_completed": tfe_model.get(
                "gauss6_fullva_dae_candidate_contract_source_policy_rows_completed"
            ),
            "gauss6_fullva_dae_candidate_contract_dae_equivalent": tfe_model.get(
                "gauss6_fullva_dae_candidate_contract_dae_equivalent"
            ),
            "gauss6_fullva_dae_candidate_contract_fullva_dae_equivalent": tfe_model.get(
                "gauss6_fullva_dae_candidate_contract_fullva_dae_equivalent"
            ),
            "bounded_source_policy_runner_smoke_implemented": tfe_model.get(
                "bounded_source_policy_runner_smoke_implemented"
            ),
            "bounded_source_policy_runner_rows": tfe_model.get("bounded_source_policy_runner_rows"),
            "bounded_source_policy_runner_full_T10": tfe_model.get("bounded_source_policy_runner_full_T10"),
            "bounded_source_policy_runner_source_policy_rows_completed": tfe_model.get(
                "bounded_source_policy_runner_source_policy_rows_completed"
            ),
            "tfe_source_grid_policy_resolved_for_full_T10": tfe_grid.get(
                "source_grid_policy_resolved_for_full_T10"
            ),
            "tfe_source_grid_integer_step_incompatible_rows": tfe_grid.get(
                "integer_step_incompatible_rows"
            ),
            "tfe_source_grid_exact_T_compatible_rows_endpoint_convention_resolved": tfe_grid.get(
                "endpoint_compatible_rows_source_endpoint_convention_resolved"
            ),
            "tfe_source_grid_endpoint_incompatible_rows_requiring_policy": tfe_grid.get(
                "endpoint_incompatible_rows_require_source_endpoint_policy"
            ),
            "tfe_source_grid_policy_resolved_for_exact_T_compatible_rows": tfe_grid.get(
                "source_grid_policy_resolved_for_exact_T_compatible_rows"
            ),
            "tfe_source_grid_source_text_available": tfe_grid.get(
                "source_text_endpoint_convention_audit", {}
            ).get("source_text_available"),
            "tfe_source_grid_source_text_anchor_count": tfe_grid.get(
                "source_text_endpoint_convention_audit", {}
            ).get("anchor_count"),
            "tfe_source_grid_algorithm_literal_fixed_h": tfe_grid.get(
                "source_text_endpoint_convention_audit", {}
            ).get("algorithm_literal_constant_h_until_tn_ge_tfinal"),
            "tfe_source_grid_endpoint_convention_resolved_for_error_sampling": tfe_grid.get(
                "source_text_endpoint_convention_audit", {}
            ).get("source_endpoint_convention_resolved_for_error_sampling"),
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
            "tfe_endpoint_sensitivity_status": tfe_endpoint_sensitivity.get("status"),
            "tfe_endpoint_sensitivity_method_count": tfe_endpoint_sensitivity.get("method_count"),
            "tfe_endpoint_sensitivity_policy_count": tfe_endpoint_sensitivity.get("policy_count"),
            "tfe_endpoint_sensitivity_summary_row_count": tfe_endpoint_sensitivity.get("summary_row_count"),
            "tfe_endpoint_sensitivity_raw_row_count": tfe_endpoint_sensitivity.get("raw_row_count"),
            "tfe_endpoint_sensitivity_source_policy_rows_completed": tfe_endpoint_sensitivity.get(
                "source_policy_rows_completed"
            ),
            "tfe_endpoint_sensitivity_external_superiority_claim_allowed": tfe_endpoint_sensitivity.get(
                "external_superiority_claim_allowed"
            ),
            "tfe_endpoint_sensitivity_source_policy_runner_equivalent": tfe_endpoint_sensitivity.get(
                "source_policy_runner_equivalent"
            ),
            "tfe_endpoint_sensitivity_default_1e_4_campaign_invoked": tfe_endpoint_sensitivity.get(
                "execution_policy", {}
            ).get("default_1e_4_campaign_invoked"),
            "tfe_endpoint_sensitivity_run_v047_invoked": tfe_endpoint_sensitivity.get(
                "execution_policy", {}
            ).get("run_v047_invoked"),
            "active_tfe_b2_candidate_row_smoke_implemented": tfe_model.get(
                "active_tfe_b2_candidate_row_smoke_implemented"
            ),
            "active_tfe_b2_candidate_row_smoke_full_T10": tfe_model.get(
                "active_tfe_b2_candidate_row_smoke_full_T10"
            ),
            "active_tfe_b2_source_policy_rows_completed": tfe_model.get(
                "active_tfe_b2_source_policy_rows_completed"
            ),
            "active_tfe_b2_source_reference_full_T10_candidate_probe_implemented": tfe_model.get(
                "active_tfe_b2_source_reference_full_T10_candidate_probe_implemented"
            ),
            "active_tfe_b2_source_reference_full_T10_candidate_probe_full_T10": tfe_model.get(
                "active_tfe_b2_source_reference_full_T10_candidate_probe_full_T10"
            ),
            "active_tfe_b2_source_reference_full_T10_candidate_probe_source_policy_reference_invoked": tfe_model.get(
                "active_tfe_b2_source_reference_full_T10_candidate_probe_source_policy_reference_invoked"
            ),
            "active_tfe_b2_source_reference_full_T10_candidate_probe_source_policy_rows_completed": tfe_model.get(
                "active_tfe_b2_source_reference_full_T10_candidate_probe_source_policy_rows_completed"
            ),
            "active_tfe_b2_source_reference_full_T10_candidate_probe_method_equivalent": tfe_model.get(
                "active_tfe_b2_source_reference_full_T10_candidate_probe_method_equivalent"
            ),
            "proof_closed": proof_closed,
            "quality_review_closed": quality_review_closed,
            "integrity_closed": integrity_closed,
            "presentation_closed": presentation_closed,
            "review_agent_present": review_agent_present,
            "minimal_reproducibility_candidate_present": minimal_candidate.get("status")
            == "candidate_replay_package_built_not_submission_ready",
            "minimal_reproducibility_candidate_file_count": minimal_candidate.get("candidate_file_count"),
            "minimal_reproducibility_candidate_python_lines": minimal_candidate.get("candidate_python_line_count"),
            "local_runner_package_partial_ready": local_runner_package_partial_ready,
            "narrowed_reproducibility_package_ready": narrowed_repro.get(
                "narrowed_claim_reproducibility_package_ready"
            ),
            "narrowed_repro_code_archive_ready": narrowed_repro_code_archive_ready,
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
            "narrowed_repro_code_archive_full_source_policy_ready": narrowed_repro_code_archive.get(
                "full_source_policy_runner_package_ready"
            ),
            "narrowed_repro_code_archive_submission_ready": narrowed_repro_code_archive.get("submission_ready"),
            "runner_centered_status": runner_centered.get("status"),
            "runner_centered_package_ready": runner_centered.get("runner_centered_package_ready"),
            "local_runner_centered_candidate_ready": runner_centered.get("local_runner_centered_candidate_ready"),
            "full_source_policy_runner_package_ready": runner_centered.get(
                "full_source_policy_runner_package_ready"
            ),
            "human_runnable_self_contained_examples": human_runnable_self_contained_examples,
            "human_runnable_replay_only_examples": human_runnable_replay_only_examples,
            "b6_four_example_local_rows": b6_local_evidence.get("local_rows"),
            "b6_four_example_source_policy_rows_closed": b6_local_evidence.get(
                "source_policy_external_rows_closed"
            ),
            "b6_four_example_source_policy_rows_total": b6_local_evidence.get(
                "source_policy_external_rows_total"
            ),
            "compact_closed_loop_candidate_runner_passed": closed_loop_candidate.get("runner_passed"),
            "compact_closed_loop_candidate_python_lines": closed_loop_candidate.get("candidate_python_line_count"),
            "p1_single_runner_candidate_ready": p1_local_runner.get("p1_single_runner_candidate_ready"),
            "p1_double_runner_candidate_ready": p1_local_runner.get("p1_double_runner_candidate_ready"),
            "minimal_code_ready": minimal_code_ready,
            "minimal_reproducible_submission_code_ready": minimal_code_ready,
            "minimal_submission_code_dependency_boundary_status": (
                minimal_submission_code_dependency_boundary["status"]
            ),
            "minimal_submission_code_dependency_blockers": (
                minimal_submission_code_dependency_boundary["blocking_objective_requirements"]
            ),
            "minimal_submission_code_dependency_safe_use": (
                minimal_submission_code_dependency_boundary["safe_current_package_use"]
            ),
            "minimal_submission_code_dependency_primary_allowed": (
                minimal_submission_code_dependency_boundary["primary_submission_package_allowed"]
            ),
            "strict_proof_writing_submission_boundary_status": (
                strict_proof_writing_submission_boundary["status"]
            ),
            "strict_proof_writing_card_status": (
                strict_proof_writing_submission_boundary["proof_writing_card_status"]
            ),
            "strict_proof_writing_p7_retained_nonpromotion_boundary_present": (
                strict_proof_writing_submission_boundary["p7_retained_nonpromotion_boundary_present"]
            ),
            "strict_proof_writing_b1_closure_scope_boundary_present": (
                strict_proof_writing_submission_boundary["b1_closure_scope_boundary_present"]
            ),
            "strict_proof_writing_b1_ad_expanded_closure_ledger_present": (
                strict_proof_writing_submission_boundary[
                    "b1_ad_expanded_closure_ledger_present"
                ]
            ),
            "strict_proof_writing_b1_ad_expanded_symbolic_oracle_closed_cells": (
                strict_proof_writing_submission_boundary[
                    "b1_ad_expanded_symbolic_oracle_closed_cells"
                ]
            ),
            "strict_proof_writing_p6_solver_scope_boundary_present": (
                strict_proof_writing_submission_boundary["p6_solver_scope_boundary_present"]
            ),
            "strict_proof_writing_p1p2_compact_tube_boundary_present": (
                strict_proof_writing_submission_boundary["p1p2_compact_tube_boundary_present"]
            ),
            "strict_proof_writing_p3p4_implementation_boundary_present": (
                strict_proof_writing_submission_boundary["p3p4_implementation_boundary_present"]
            ),
            "strict_proof_writing_p5_direct_route_boundary_present": (
                strict_proof_writing_submission_boundary["p5_direct_route_boundary_present"]
            ),
            "strict_proof_writing_proof_causality_ledger_present": (
                strict_proof_writing_submission_boundary[
                    "proof_causality_ledger_present"
                ]
            ),
            "strict_proof_writing_direct_route_anticircularity_ledger_present": (
                strict_proof_writing_submission_boundary[
                    "direct_route_anticircularity_ledger_present"
                ]
            ),
            "strict_proof_writing_p_interface_satisfaction_ledger_present": (
                strict_proof_writing_submission_boundary[
                    "p_interface_satisfaction_ledger_present"
                ]
            ),
            "strict_proof_writing_p7_residual_to_error_ledger_present": (
                strict_proof_writing_submission_boundary[
                    "p7_residual_to_error_ledger_present"
                ]
            ),
            "strict_proof_writing_theorem_use_rule_present": (
                strict_proof_writing_submission_boundary["theorem_use_rule_present"]
            ),
            "strict_proof_writing_quantifier_domain_ledger_present": (
                strict_proof_writing_submission_boundary[
                    "quantifier_domain_ledger_present"
                ]
            ),
            "strict_proof_writing_local_global_transfer_ledger_present": (
                strict_proof_writing_submission_boundary[
                    "local_global_transfer_ledger_present"
                ]
            ),
            "strict_proof_writing_objective_completion_boundary_present": (
                strict_proof_writing_submission_boundary[
                    "objective_completion_boundary_present"
                ]
            ),
            "strict_proof_writing_constant_dependency_ledger_present": (
                strict_proof_writing_submission_boundary[
                    "constant_dependency_ledger_present"
                ]
            ),
            "strict_proof_writing_theorem_dependency_consumption_ledger_present": (
                strict_proof_writing_submission_boundary[
                    "theorem_dependency_consumption_ledger_present"
                ]
            ),
            "strict_proof_writing_branch_consistency_ledger_present": (
                strict_proof_writing_submission_boundary[
                    "branch_consistency_ledger_present"
                ]
            ),
            "strict_proof_writing_implementation_route_oracle_ledger_present": (
                strict_proof_writing_submission_boundary[
                    "implementation_route_oracle_ledger_present"
                ]
            ),
            "strict_proof_writing_nonlinear_solver_scale_ledger_present": (
                strict_proof_writing_submission_boundary[
                    "nonlinear_solver_scale_ledger_present"
                ]
            ),
            "strict_proof_writing_local_defect_decomposition_ledger_present": (
                strict_proof_writing_submission_boundary[
                    "local_defect_decomposition_ledger_present"
                ]
            ),
            "strict_proof_writing_theorem_output_scope_ledger_present": (
                strict_proof_writing_submission_boundary[
                    "theorem_output_scope_ledger_present"
                ]
            ),
            "strict_proof_writing_reporting_map_ledger_present": (
                strict_proof_writing_submission_boundary[
                    "reporting_map_ledger_present"
                ]
            ),
            "strict_proof_writing_reference_proof_order_correspondence_closed": (
                strict_proof_writing_submission_boundary[
                    "reference_proof_order_correspondence_closed"
                ]
            ),
            "strict_proof_writing_reference_proof_order_no_estimate_transfer": (
                strict_proof_writing_submission_boundary[
                    "reference_proof_order_no_estimate_transfer"
                ]
            ),
            "strict_proof_writing_reference_proof_order_nonimport_boundary": (
                strict_proof_writing_submission_boundary[
                    "reference_proof_order_nonimport_boundary"
                ]
            ),
            "strict_proof_writing_reference_proof_order_constraint_multiplier_split": (
                strict_proof_writing_submission_boundary[
                    "reference_proof_order_constraint_multiplier_split"
                ]
            ),
            "strict_proof_writing_safe_reader_claim": (
                strict_proof_writing_submission_boundary["safe_reader_claim"]
            ),
            "strict_proof_writing_safe_reader_claim_boundary_present": (
                strict_proof_writing_submission_boundary[
                    "safe_reader_claim_boundary_present"
                ]
            ),
            "strict_proof_writing_reading_rule_boundary_present": (
                strict_proof_writing_submission_boundary[
                    "reading_rule_boundary_present"
                ]
            ),
            "strict_proof_writing_theorem_assumption_partition_boundary_present": (
                strict_proof_writing_submission_boundary[
                    "theorem_assumption_partition_boundary_present"
                ]
            ),
            "strict_proof_writing_theorem_assumption_anchor_ids": (
                strict_proof_writing_submission_boundary[
                    "theorem_assumption_anchor_ids"
                ]
            ),
            "strict_proof_writing_theorem_assumption_anchor_count": (
                strict_proof_writing_submission_boundary[
                    "theorem_assumption_anchor_count"
                ]
            ),
            "strict_proof_writing_theorem_assumption_submission_satisfied_ids": (
                strict_proof_writing_submission_boundary[
                    "theorem_assumption_submission_satisfied_ids"
                ]
            ),
            "strict_proof_writing_theorem_assumption_submission_satisfied_count": (
                strict_proof_writing_submission_boundary[
                    "theorem_assumption_submission_satisfied_count"
                ]
            ),
            "strict_proof_writing_theorem_assumption_retained_or_open_ids": (
                strict_proof_writing_submission_boundary[
                    "theorem_assumption_retained_or_open_ids"
                ]
            ),
            "strict_proof_writing_theorem_assumption_retained_or_open_count": (
                strict_proof_writing_submission_boundary[
                    "theorem_assumption_retained_or_open_count"
                ]
            ),
            "strict_proof_writing_forbidden_reader_claims": (
                strict_proof_writing_submission_boundary["forbidden_reader_claims"]
            ),
            "strict_proof_writing_forbidden_reader_claims_boundary_present": (
                strict_proof_writing_submission_boundary[
                    "forbidden_reader_claims_boundary_present"
                ]
            ),
            "strict_proof_writing_forbidden_unconditional_theorem_boundary_present": (
                strict_proof_writing_submission_boundary[
                    "forbidden_unconditional_theorem_boundary_present"
                ]
            ),
            "strict_proof_writing_forbidden_eta_h_solver_policy_claim_boundary_present": (
                strict_proof_writing_submission_boundary[
                    "forbidden_eta_h_solver_policy_claim_boundary_present"
                ]
            ),
            "strict_proof_writing_forbidden_fixed_tolerance_asymptotic_claim_boundary_present": (
                strict_proof_writing_submission_boundary[
                    "forbidden_fixed_tolerance_asymptotic_claim_boundary_present"
                ]
            ),
            "strict_proof_writing_forbidden_residual_to_error_theorem_claim_boundary_present": (
                strict_proof_writing_submission_boundary[
                    "forbidden_residual_to_error_theorem_claim_boundary_present"
                ]
            ),
            "strict_proof_writing_forbidden_source_policy_full_tfe_package_claim_boundary_present": (
                strict_proof_writing_submission_boundary[
                    "forbidden_source_policy_full_tfe_package_claim_boundary_present"
                ]
            ),
            "strict_proof_writing_residual_to_error_not_promoted": (
                strict_proof_writing_submission_boundary[
                    "residual_to_error_not_promoted"
                ]
            ),
            "strict_proof_writing_source_policy_full_tfe_not_promoted": (
                strict_proof_writing_submission_boundary[
                    "source_policy_full_tfe_not_promoted"
                ]
            ),
            "strict_proof_writing_objective_blockers_retained": (
                strict_proof_writing_submission_boundary["objective_blockers_retained"]
            ),
            "strict_proof_writing_global_boundaries_retained": (
                strict_proof_writing_submission_boundary["proof_global_boundaries_retained"]
            ),
            "strict_proof_writing_submission_ready": (
                strict_proof_writing_submission_boundary["submission_ready"]
            ),
            "combined_python_line_count": combined_python_line_count,
        },
        "requirements": requirements,
        "required_next_actions": [
            (
                "OC4 can close only through exact B4 opt-in authorized RA/HI closeout "
                "or a new source-policy promotion artifact; OC6 can reopen only if a "
                "new public/source-code-equivalent TFE implementation artifact appears; "
                "keep both outside the accepted narrowed proof/method claim"
            ),
            "promote the partial local runner package to a full source-policy runner archive after source-policy and TFE runner gates close",
        ],
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(audit, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# Objective Completion Audit",
        "",
        f"Status: **{audit['status']}**.",
        f"Objective complete: `{audit['objective_complete']}`.",
        f"Submission ready: `{audit['submission_ready']}`.",
        f"Can mark goal complete: `{audit['completion_decision']['can_mark_goal_complete']}`.",
        f"Completion decision reason: {audit['completion_decision']['reason']}.",
        "",
        "## Summary",
        "",
        f"- Requirements satisfied/partial/open: `{len(satisfied)}/{len(partial)}/{len(open_items)}`.",
        f"- Blocking requirements still open: `{len(blocking_open)}`.",
        f"- Blocking requirement ids: `{blocking_requirement_ids}`.",
        f"- Open blocker id alias: `{open_blocker_ids}`.",
        f"- Machine-readable blocker ids: `{list(blockers_by_id)}`.",
        f"- Machine-readable blocker status by id: `{blocker_status_by_id}`.",
        f"- Machine-readable blocker open by id: `{blocker_open_by_id}`.",
        f"- Machine-readable blocker closure decision by id: `{blocker_closure_decision_by_id}`.",
        f"- Machine-readable blocker closure allowed by id: `{blocker_closure_allowed_by_id}`.",
        f"- Objective blocker alias tuple OC4/OC6/OC12: `OC4/{audit['oc4_blocker_status']}/{audit['oc4_blocker_open']}/{audit['oc4_closure_decision']}/{audit['oc4_closure_allowed_now']}/{audit['oc4_ready_commands_mapped_rows']}/{audit['oc4_traceability_unique_traced_declared_mismatch']};OC6/{audit['oc6_blocker_status']}/{audit['oc6_blocker_open']}/{audit['oc6_closure_decision']}/{audit['oc6_closure_allowed_now']}/{audit['oc6_reopen_condition']}/{audit['oc6_latest_external_probe_boundary_marker']};OC12/{audit['oc12_blocker_status']}/{audit['oc12_blocker_open']}/{audit['oc12_closure_decision']}/{audit['oc12_closure_allowed_now']}/{audit['oc12_current_archive_usable_as_full_source_policy_runner_archive']}/{audit['oc12_safe_current_use']}/{audit['oc12_primary_submission_package_allowed']}`.",
        f"- Machine-readable blocker closure keys: `{list(audit['blocker_required_to_close_by_id'])}`.",
        f"- OC4 required-to-close source-policy/opt-in/commands/rows: `{audit['blocker_required_to_close_by_id']['OC4']['current_source_policy_closed_ratio']}/{audit['blocker_required_to_close_by_id']['OC4']['authorized_ra_hi_closeout_route']['requires_exact_b4_opt_in']}/{audit['blocker_required_to_close_by_id']['OC4']['authorized_ra_hi_closeout_route']['opt_in_required_command_count']}/{audit['blocker_required_to_close_by_id']['OC4']['authorized_ra_hi_closeout_route']['opt_in_required_mapped_external_rows']}`.",
        f"- OC6 required-to-close runner/reopen/probe: `{audit['blocker_required_to_close_by_id']['OC6']['contract_preflight_status']}/{audit['blocker_required_to_close_by_id']['OC6']['effective_execution_block_count']}/{audit['blocker_required_to_close_by_id']['OC6']['reopen_condition']}/{audit['blocker_required_to_close_by_id']['OC6']['latest_external_probe']['date']}/{audit['blocker_required_to_close_by_id']['OC6']['latest_external_probe']['positive_public_code_artifact_rows']}/{audit['blocker_required_to_close_by_id']['OC6']['latest_external_probe']['reopen_triggered']}`.",
        f"- OC12 required-to-close archive/upstream/source-policy: `{audit['blocker_required_to_close_by_id']['OC12']['current_archive_usable_as_full_source_policy_runner_archive']}/{audit['blocker_required_to_close_by_id']['OC12']['full_source_policy_runner_package_ready']}/{','.join(audit['blocker_required_to_close_by_id']['OC12']['upstream_blockers'])}/{audit['blocker_required_to_close_by_id']['OC12']['source_policy_closed_ratio']}`.",
        f"- Blocker action boundaries OC4/OC6/OC12 safe/opt-in counts: `{len(audit['blocker_safe_next_actions_by_id']['OC4'])}/{len(audit['blocker_opt_in_required_actions_by_id']['OC4'])};{len(audit['blocker_safe_next_actions_by_id']['OC6'])}/{len(audit['blocker_opt_in_required_actions_by_id']['OC6'])};{len(audit['blocker_safe_next_actions_by_id']['OC12'])}/{len(audit['blocker_opt_in_required_actions_by_id']['OC12'])}`.",
        f"- Core matrix and manuscript traceability: `{core_matrix_ready}/{traceability_ready}`.",
        f"- Common-reference comparison closed: `{common_reference_closed}`.",
        f"- Source-policy apples-to-apples closed: `{source_policy_closed}`.",
        f"- Source-policy rows closed: `{full_source_policy_row_provenance.get('source_policy_rows_closed')}/{full_source_policy_row_provenance.get('source_policy_rows_total')}`.",
        f"- Source-policy execution allowed now/invoked/exact opt-in required: `{audit['source_policy_execution_allowed_now']}/{audit['source_policy_execution_invoked']}/{audit['exact_b4_opt_in_required_for_execution']}`.",
        f"- Safe action ids: `{','.join(audit['safe_action_ids'])}`.",
        f"- Opt-in action ids: `{','.join(audit['opt_in_action_ids'])}`.",
        f"- Safe/opt-in action object counts: `{len(audit['safe_actions_without_b4_opt_in'])}/{len(audit['opt_in_required_actions'])}`.",
        f"- RA/HI source-policy closeout checklist: `{ra_hi_closeout.get('status')}`; rows RA/HI/total `{ra_hi_closeout.get('coverage', {}).get('ra2021_rows')}/{ra_hi_closeout.get('coverage', {}).get('hi2022_rows')}/{ra_hi_closeout.get('coverage', {}).get('source_policy_rows_total')}`; commands/mapped `{ra_hi_closeout.get('coverage', {}).get('ready_command_count')}/{ra_hi_closeout.get('coverage', {}).get('ready_command_mapped_external_rows')}`; promoted/completed/external-ready `{ra_hi_closeout.get('coverage', {}).get('source_policy_rows_promoted')}/{ra_hi_closeout.get('coverage', {}).get('source_policy_rows_completed')}/{ra_hi_closeout.get('coverage', {}).get('external_superiority_ready_rows')}`; opt-in/executed `{ra_hi_closeout.get('guarded_execution_boundary', {}).get('explicit_user_opt_in_required_before_any_command')}/{ra_hi_closeout.get('guarded_execution_boundary', {}).get('execution_invoked_by_packet')}`; closes B4/B7 `{ra_hi_closeout.get('not_promoted_disposition', {}).get('b4_can_close_from_this_checklist')}/{ra_hi_closeout.get('not_promoted_disposition', {}).get('b7_can_close_from_this_checklist')}`.",
        f"- RA/HI current-evidence terminal/future-auth-or-artifact/reproduction-complete rows: `{ra_hi_promotion_matrix.get('current_evidence_terminal_not_promotable_rows')}/{ra_hi_promotion_matrix.get('future_promotion_requires_authorized_execution_or_new_artifact_rows')}/{ra_hi_promotion_matrix.get('source_policy_reproduction_complete_rows')}`.",
        f"- Source-policy execution handoff: `{b4_execution_handoff.get('status')}`; authorized/commands-not-run `{b4_execution_handoff.get('execution_authorized')}/{b4_execution_handoff.get('commands_not_run_by_handoff')}`; ready commands/mapped `{b4_execution_handoff.get('ready_command_count')}/{b4_execution_handoff.get('ready_command_mapped_external_rows')}`; terminal unable `{b4_execution_handoff.get('terminal_unable_to_reproduce_rows')}`.",
        f"- Source-policy execution handoff traceability: unique RA/HI rows `{b4_command_traceability_summary.get('unique_mapped_row_count')}/{b4_command_traceability_summary.get('ra_hi_unique_row_count')}`; row refs `{b4_command_traceability_summary.get('traced_command_row_reference_total')}/{b4_command_traceability_summary.get('declared_mapped_row_reference_total')}`; mismatches/terminal/closed/promotion-ready `{b4_command_traceability_summary.get('declared_vs_traced_mismatch_count')}/{b4_command_traceability_summary.get('terminal_rows_with_command_refs')}/{b4_command_traceability_summary.get('source_policy_closed_rows')}/{b4_command_traceability_summary.get('promotion_ready_rows')}`.",
        f"- Source-policy execution exact approval/driver: `{b4_execution_handoff.get('exact_approval_statement')}/{b4_execution_handoff.get('guarded_execution_driver')}/{b4_execution_handoff.get('driver_requires_exact_approval')}/{b4_execution_handoff.get('driver_does_not_authorize_execution')}/{b4_execution_handoff.get('opt_in_required_command_count')}/{b4_execution_handoff.get('opt_in_required_mapped_external_rows')}`.",
        f"- B4 guarded driver refusal boundary 20260621: `{b4_guarded_refusal_boundary_tuple}`.",
        f"- Full source-policy row provenance handoff exact approval/driver: `{full_source_policy_row_provenance.get('source_policy_execution_handoff', {}).get('exact_required_user_approval_statement')}/{full_source_policy_row_provenance.get('source_policy_execution_handoff', {}).get('guarded_execution_driver')}/{full_source_policy_row_provenance.get('source_policy_execution_handoff', {}).get('driver_requires_exact_approval')}/{full_source_policy_row_provenance.get('source_policy_execution_handoff', {}).get('driver_does_not_authorize_execution')}/{full_source_policy_row_provenance.get('source_policy_execution_handoff', {}).get('opt_in_required_command_count')}/{full_source_policy_row_provenance.get('source_policy_execution_handoff', {}).get('opt_in_required_mapped_external_rows')}/{full_source_policy_row_provenance.get('source_policy_execution_handoff', {}).get('terminal_unable_to_reproduce_rows')}`.",
        f"- B2 active suites closed/source-policy rows closed/demotion route: `{b2_active_suites_closed}/{b2_source_policy_rows_closed}/{b2_active_suites_closed_by_demotion}`.",
        f"- B2 active/demoted flagged rows/can close/external-superiority allowed: `{b2_remaining.get('active_flagged_row_count')}/{b2_remaining.get('demoted_flagged_row_count')}/{b2_remaining.get('b2_can_close_now')}/{b2_remaining.get('external_superiority_claim_allowed')}`.",
        f"- TFE source-policy runner closed: `{tfe_runner_closed}`.",
        f"- TFE DAE runner contract gap status/missing/non-heavy/execution/ready/heavy-run: `{tfe_dae_gap.get('status')}/{tfe_dae_gap.get('missing_contract_block_count')}/{len(tfe_dae_gap.get('nonheavy_missing_contract_blocks', []))}/{len(tfe_dae_gap.get('source_policy_execution_missing_contract_blocks', []))}/{tfe_dae_gap.get('ready_to_execute_source_policy_now')}/{tfe_dae_gap.get('heavy_numerical_run_invoked')}`.",
        f"- TFE DAE runner contract accounting raw/non-heavy-terminal/effective-execution/source-rows: `{tfe_dae_gap.get('contract_block_accounting', {}).get('raw_open_contract_block_count')}/{tfe_dae_gap.get('terminal_nonpromoted_contract_block_count')}/{tfe_dae_gap.get('effective_missing_contract_block_count')}/{tfe_dae_gap.get('contract_block_accounting', {}).get('source_policy_rows_closed_by_accounting')}`.",
        f"- TFE DAE runner effective execution blocks: `{tfe_dae_gap.get('effective_missing_contract_blocks')}`.",
        f"- TFE DAE runner contract missing ids: `{tfe_dae_missing_block_ids}`.",
        f"- TFE DAE runner non-heavy dispositions/demoted/no-row-closure: `{len(tfe_dae_nonheavy_dispositions)}/{tfe_dae_gap.get('nonheavy_missing_contract_blocks_dispositioned_by_demotion')}/{tfe_dae_gap.get('nonheavy_demotion_does_not_close_source_policy')}`.",
        f"- TFE DAE runner execution block count: `{tfe_dae_gap.get('source_policy_execution_missing_contract_block_count')}`.",
        f"- TFE source-policy execution preflight status/opt-in/nonheavy/execution/promote/ready: `{tfe_execution_preflight.get('status')}/{tfe_execution_preflight.get('explicit_user_opt_in_required')}/{tfe_execution_preflight.get('nonheavy_blocks_dispositioned_by_demotion')}/{tfe_execution_preflight.get('execution_block_count')}/{tfe_execution_preflight.get('can_promote_any_tfe_source_policy_row_now')}/{tfe_execution_preflight.get('ready_to_execute_source_policy_now')}`.",
        f"- TFE runner contract preflight status/entrypoints/candidate-backed/source-rows/execution-blocks: `{tfe_runner_contract_preflight.get('status')}/{tfe_runner_contract_preflight.get('callable_contract_count')}/{tfe_runner_contract_preflight.get('entrypoint_count')}/{tfe_runner_contract_preflight.get('candidate_backed_contract_count')}/{tfe_runner_contract_preflight.get('source_policy_rows_completed')}/{tfe_runner_contract_preflight.get('source_policy_execution_block_count')}`.",
        f"- TFE source-policy terminal route/reopen condition: `{tfe_execution_preflight.get('current_route')}/{tfe_execution_preflight.get('reopen_condition')}`.",
        f"- TFE self-reproduction terminal status/public-code/reopen/closed: `{tfe_self_reproduction.get('status')}/{tfe_self_reproduction.get('public_code_recheck_status')}/{tfe_self_reproduction.get('reopen_condition')}/{tfe_self_reproduction.get('source_policy_closed_ratio')}`.",
        f"- TFE latest public-code refresh status/rows/queries/positive/closed: `{source_policy_public_code_refresh.get('status')}/{source_policy_public_code_refresh.get('rows')}/{source_policy_public_code_refresh.get('current_queries')}/{source_policy_public_code_refresh.get('positive_public_code_artifact_rows')}/{source_policy_public_code_refresh.get('source_policy_closed_ratio')}`.",
        f"- TFE absolute-coordinate planar-lift trajectory probe rows/metric rows/source-policy rows/equivalent DAE: `{tfe_model.get('absolute_coordinate_planar_lift_trajectory_probe_rows')}/{tfe_model.get('absolute_coordinate_planar_lift_trajectory_probe_metric_rows')}/{tfe_model.get('absolute_coordinate_planar_lift_trajectory_probe_source_policy_rows_completed')}/{tfe_model.get('absolute_coordinate_planar_lift_trajectory_probe_dae_runner_equivalent')}`.",
        f"- TFE bounded absolute-coordinate DAE trajectory runner rows/metric rows/step residual rows/source-policy rows/equivalent DAE/monolithic: `{tfe_model.get('bounded_absolute_coordinate_dae_trajectory_runner_rows')}/{tfe_model.get('bounded_absolute_coordinate_dae_trajectory_runner_metric_rows')}/{tfe_model.get('bounded_absolute_coordinate_dae_trajectory_runner_step_residual_rows')}/{tfe_model.get('bounded_absolute_coordinate_dae_trajectory_runner_source_policy_rows_completed')}/{tfe_model.get('bounded_absolute_coordinate_dae_trajectory_runner_dae_runner_equivalent')}/{tfe_model.get('bounded_absolute_coordinate_dae_trajectory_runner_monolithic_integrator')}`.",
        f"- TFE monolithic DAE candidate runner rows/metric rows/step residual rows/source-policy rows/equivalent DAE/monolithic: `{tfe_model.get('monolithic_absolute_coordinate_dae_candidate_runner_rows')}/{tfe_model.get('monolithic_absolute_coordinate_dae_candidate_runner_metric_rows')}/{tfe_model.get('monolithic_absolute_coordinate_dae_candidate_runner_step_residual_rows')}/{tfe_model.get('monolithic_absolute_coordinate_dae_candidate_runner_source_policy_rows_completed')}/{tfe_model.get('monolithic_absolute_coordinate_dae_candidate_runner_dae_runner_equivalent')}/{tfe_model.get('monolithic_absolute_coordinate_dae_candidate_runner_monolithic_integrator')}`.",
        f"- TFE source-method candidate contract rows/source-policy rows/equivalent method/DAE: `{tfe_model.get('source_method_candidate_runner_contract_rows')}/{tfe_model.get('source_method_candidate_runner_contract_source_policy_rows_completed')}/{tfe_model.get('source_method_candidate_runner_contract_method_equivalent')}/{tfe_model.get('source_method_candidate_runner_contract_dae_equivalent')}`.",
        f"- TFE DAE trajectory bridge contract rows/matched/source-policy rows/equivalent DAE/method/monolithic: `{tfe_model.get('dae_trajectory_bridge_contract_rows')}/{tfe_model.get('dae_trajectory_bridge_contract_matched_rows')}/{tfe_model.get('dae_trajectory_bridge_contract_source_policy_rows_completed')}/{tfe_model.get('dae_trajectory_bridge_contract_dae_runner_equivalent')}/{tfe_bridge.get('source_policy_method_runner_equivalent')}/{tfe_model.get('dae_trajectory_bridge_contract_monolithic_integrator')}`.",
        f"- TFE DAE trajectory bridge finite/residual-below-1e-10/accepted-use: `{tfe_model.get('dae_trajectory_bridge_contract_all_rows_finite')}/{tfe_model.get('dae_trajectory_bridge_contract_all_dae_residuals_below_1e_10')}/{tfe_bridge.get('accepted_use')}`.",
        f"- TFE candidate-friction DAE trajectory contract rows/step residual rows/source-policy rows/equivalent DAE/method/source-law/monolithic: `{tfe_model.get('candidate_frictional_dae_trajectory_contract_rows')}/{tfe_model.get('candidate_frictional_dae_trajectory_contract_step_residual_rows')}/{tfe_model.get('candidate_frictional_dae_trajectory_contract_source_policy_rows_completed')}/{tfe_model.get('candidate_frictional_dae_trajectory_contract_dae_runner_equivalent')}/{tfe_model.get('candidate_frictional_dae_trajectory_contract_method_runner_equivalent')}/{tfe_model.get('candidate_frictional_dae_trajectory_contract_brown_mcphee_source_code_equivalent_law')}/{tfe_model.get('candidate_frictional_dae_trajectory_contract_monolithic_integrator')}`.",
        f"- TFE candidate-friction DAE trajectory contract finite/residual-below-1e-9/friction-power-nonpositive: `{tfe_model.get('candidate_frictional_dae_trajectory_contract_all_rows_finite')}/{tfe_model.get('candidate_frictional_dae_trajectory_contract_all_dae_residuals_below_1e_9')}/{tfe_model.get('candidate_frictional_dae_trajectory_contract_all_friction_power_nonpositive')}`.",
        f"- TFE Brown--McPhee transition-velocity sensitivity rows/contracts/source rows/material/equivalence-false: `{tfe_transition_velocity_sensitivity.get('endpoint_delta_row_count')}/{tfe_transition_velocity_sensitivity.get('contract_row_count')}/{tfe_transition_velocity_sensitivity.get('source_policy_rows_completed')}/{tfe_transition_velocity_sensitivity.get('missing_transition_velocity_is_numerically_material')}/{tfe_transition_velocity_sensitivity.get('all_contract_equivalence_flags_false')}`.",
        f"- TFE Brown--McPhee source-code equivalence certificate status/available/positive/closed-block/exec/close-now: `{tfe_brown_mcphee_certificate.get('status')}/{tfe_brown_mcphee_certificate.get('certificate_available')}/{tfe_brown_mcphee_certificate.get('positive_source_code_equivalence_certified')}/{tfe_brown_mcphee_certificate.get('nonheavy_contract_block_closed')}/{tfe_brown_mcphee_certificate.get('source_policy_execution_invoked')}/{tfe_brown_mcphee_certificate.get('can_close_now')}`.",
        f"- TFE Brown--McPhee transition-velocity sensitivity max endpoint coordinate/velocity delta: `{tfe_transition_velocity_sensitivity.get('max_endpoint_coordinate_delta_vs_baseline'):.3e}/{tfe_transition_velocity_sensitivity.get('max_endpoint_velocity_delta_vs_baseline'):.3e}`.",
        f"- TFE bounded source-reference-policy smoke/full T=10 source run: `{tfe_model.get('source_reference_solution_policy_smoke_implemented')}/{tfe_model.get('source_reference_solution_policy_smoke_full_T10')}`.",
        f"- TFE source-grid policy resolved/incompatible rows: `{tfe_grid.get('source_grid_policy_resolved_for_full_T10')}/{tfe_grid.get('integer_step_incompatible_rows')}`.",
        f"- TFE exact-T endpoint-grid subset resolved/requires policy: `{tfe_grid.get('source_grid_policy_resolved_for_exact_T_compatible_rows')}/{tfe_grid.get('endpoint_compatible_rows_source_endpoint_convention_resolved')}/{tfe_grid.get('endpoint_incompatible_rows_require_source_endpoint_policy')}`.",
        f"- TFE source-text endpoint audit source/anchors/fixed-h/error-sampling-resolved: `{tfe_grid.get('source_text_endpoint_convention_audit', {}).get('source_text_available')}/{tfe_grid.get('source_text_endpoint_convention_audit', {}).get('anchor_count')}/{tfe_grid.get('source_text_endpoint_convention_audit', {}).get('algorithm_literal_constant_h_until_tn_ge_tfinal')}/{tfe_grid.get('source_text_endpoint_convention_audit', {}).get('source_endpoint_convention_resolved_for_error_sampling')}`.",
        f"- TFE endpoint boundary certificate status/proved/exact/overrun/source rows/full-policy/exact-T-equivalent: `{tfe_endpoint_boundary.get('status')}/{tfe_endpoint_boundary.get('theorem', {}).get('name') == 'fixed_h_until_final_time_endpoint_bound'}/{tfe_endpoint_boundary.get('algorithm_literal_exact_T_row_count')}/{tfe_endpoint_boundary.get('algorithm_literal_overrun_row_count')}/{tfe_endpoint_boundary.get('source_policy_rows_completed')}/{tfe_endpoint_boundary.get('source_grid_policy_resolved_for_full_T10')}/{tfe_endpoint_boundary.get('source_policy_exact_T_error_sampling_equivalent')}`.",
        f"- TFE full-T10 endpoint policy closure certificate status/available/positive/closed-block/exec/close-now: `{tfe_endpoint_certificate.get('status')}/{tfe_endpoint_certificate.get('certificate_available')}/{tfe_endpoint_certificate.get('positive_full_T10_endpoint_policy_certified')}/{tfe_endpoint_certificate.get('nonheavy_contract_block_closed')}/{tfe_endpoint_certificate.get('source_policy_execution_invoked')}/{tfe_endpoint_certificate.get('can_close_now')}`.",
        f"- TFE comparator candidate/TFE m=1-3 candidate/source-policy-equivalent/TFE m=1-3 source-policy runners: `{tfe_model.get('source_comparator_candidate_runners_implemented')}/{tfe_model.get('tfe_m1_m2_m3_candidate_runner_smoke_implemented')}/{tfe_model.get('source_policy_method_runner_equivalent')}/{tfe_model.get('tfe_m1_m2_m3_source_policy_runners_implemented')}`.",
        f"- Gauss6 source-pendulum candidate smoke/absolute-coordinate source-policy runner: `{tfe_model.get('gauss6_fullva_source_pendulum_candidate_smoke_implemented')}/{tfe_model.get('gauss6_fullva_absolute_coordinate_source_policy_runner_implemented')}`.",
        f"- Gauss6 source-pendulum candidate rows/source-policy rows/method-equivalent: `{tfe_model.get('gauss6_fullva_source_pendulum_candidate_rows')}/{tfe_model.get('gauss6_fullva_source_pendulum_candidate_source_policy_rows_completed')}/{tfe_model.get('gauss6_fullva_source_pendulum_candidate_method_equivalent')}`.",
        f"- Gauss6/FullVA DAE candidate contract rows/source-policy rows/equivalent DAE/FullVA: `{tfe_model.get('gauss6_fullva_dae_candidate_contract_rows')}/{tfe_model.get('gauss6_fullva_dae_candidate_contract_source_policy_rows_completed')}/{tfe_model.get('gauss6_fullva_dae_candidate_contract_dae_equivalent')}/{tfe_model.get('gauss6_fullva_dae_candidate_contract_fullva_dae_equivalent')}`.",
        f"- TFE unified bounded runner rows/full T=10/source-policy rows: `{tfe_model.get('bounded_source_policy_runner_rows')}/{tfe_model.get('bounded_source_policy_runner_full_T10')}/{tfe_model.get('bounded_source_policy_runner_source_policy_rows_completed')}`.",
        f"- Active TFE B2 candidate row smoke/full T=10/source-policy rows: `{tfe_model.get('active_tfe_b2_candidate_row_smoke_implemented')}/{tfe_model.get('active_tfe_b2_candidate_row_smoke_full_T10')}/{tfe_model.get('active_tfe_b2_source_policy_rows_completed')}`.",
        f"- Active TFE B2 source-reference full T=10 candidate probe full T=10/reference invoked/source-policy rows/method-equivalent: `{tfe_model.get('active_tfe_b2_source_reference_full_T10_candidate_probe_full_T10')}/{tfe_model.get('active_tfe_b2_source_reference_full_T10_candidate_probe_source_policy_reference_invoked')}/{tfe_model.get('active_tfe_b2_source_reference_full_T10_candidate_probe_source_policy_rows_completed')}/{tfe_model.get('active_tfe_b2_source_reference_full_T10_candidate_probe_method_equivalent')}`.",
        f"- Direct PC2 proof closed; global proof/package blockers retained: `{proof_closed}`; blockers `{blocking_requirement_ids}`.",
        f"- Newton-Euler obligation coverage matrix/links/complete rows: `{proof.get('evidence_summary', {}).get('newton_euler_obligation_coverage_matrix_complete')}/{proof.get('evidence_summary', {}).get('newton_euler_row_obligation_links')}/{proof.get('evidence_summary', {}).get('newton_euler_rows_with_complete_obligation_sets')}`.",
        f"- Minimal reproducibility candidate/status/files/Python-lines: `{minimal_candidate.get('status')}/{minimal_candidate.get('candidate_file_count')}/{minimal_candidate.get('candidate_python_line_count')}`.",
        f"- Local runner package partial/full-source-policy ready: `{local_runner_package_partial_ready}/{runner_centered.get('full_source_policy_runner_package_ready')}`.",
        f"- Narrowed repro code archive ready/status/entries/Python/source-policy/full-source/submission: `{narrowed_repro_code_archive_ready}/{narrowed_repro_code_archive.get('status')}/{narrowed_repro_code_archive.get('entry_count')}/{narrowed_repro_code_archive.get('python_file_count')}/{narrowed_repro_code_archive.get('python_line_count')}/{narrowed_repro_code_archive.get('source_policy_rows_closed')}/{narrowed_repro_code_archive.get('source_policy_rows_total')}/{narrowed_repro_code_archive.get('full_source_policy_runner_package_ready')}/{narrowed_repro_code_archive.get('submission_ready')}`.",
        f"- Full source-policy runner archive gap: `{full_source_runner_gap.get('status')}`; ready/can-use-current-archive/safe-current-use `{full_source_runner_gap.get('closure_conditions', {}).get('full_archive_ready_now')}/{full_source_runner_gap.get('closure_conditions', {}).get('can_use_current_archive_as_full_source_policy_runner_archive')}/narrowed_claim_replay_and_audit_provenance_only`; rows closed/total `{full_source_runner_gap.get('source_policy_rows', {}).get('closed')}/{full_source_runner_gap.get('source_policy_rows', {}).get('total')}`; terminal-unable/RA-HI-open `{full_source_runner_gap.get('closure_conditions', {}).get('terminal_unable_to_reproduce_rows')}/{full_source_runner_gap.get('closure_conditions', {}).get('ra_hi_rows_requiring_authorized_closeout_or_new_artifact')}`.",
        f"- Full source-policy runner archive TFE runner preflight: `{full_source_runner_gap.get('closure_conditions', {}).get('tfe_runner_contract_preflight_status')}/{full_source_runner_gap.get('closure_conditions', {}).get('tfe_runner_contract_preflight_entrypoints')}/{full_source_runner_gap.get('closure_conditions', {}).get('tfe_runner_contract_preflight_candidate_backed')}/{full_source_runner_gap.get('closure_conditions', {}).get('tfe_runner_contract_preflight_source_policy_rows_completed')}/{full_source_runner_gap.get('closure_conditions', {}).get('tfe_runner_contract_preflight_execution_blocks')}`.",
        f"- Full source-policy runner archive terminal reopen/exact approval: `tfe2026_original_pendulum={full_source_runner_terminal_reopen_conditions.get('tfe2026_original_pendulum')}; vp2024_velocity_partitioning={full_source_runner_terminal_reopen_conditions.get('vp2024_velocity_partitioning')}; approval={full_source_runner_required_approval_statement}`.",
        f"- Minimal submission code dependency boundary: `{minimal_submission_code_dependency_boundary['status']}`; blockers `{minimal_submission_code_dependency_boundary['blocking_objective_requirements']}`; safe use `{minimal_submission_code_dependency_boundary['safe_current_package_use']}`; primary package allowed `{minimal_submission_code_dependency_boundary['primary_submission_package_allowed']}`.",
        f"- Strict proof-writing submission boundary: `{strict_proof_writing_submission_boundary['status']}`; card `{strict_proof_writing_submission_boundary['proof_writing_card_status']}`; safe claim `{strict_proof_writing_submission_boundary['safe_reader_claim']}`; blockers `{strict_proof_writing_submission_boundary['objective_blockers_retained']}`; submission ready `{strict_proof_writing_submission_boundary['submission_ready']}`.",
        f"- Strict proof-writing P-interface partition: boundary `{strict_proof_writing_submission_boundary['theorem_assumption_partition_boundary_present']}`; anchors `{strict_proof_writing_submission_boundary['theorem_assumption_anchor_count']}` / `{strict_proof_writing_submission_boundary['theorem_assumption_anchor_ids']}`; satisfied `{strict_proof_writing_submission_boundary['theorem_assumption_submission_satisfied_count']}` / `{strict_proof_writing_submission_boundary['theorem_assumption_submission_satisfied_ids']}`; retained theorem interfaces `{strict_proof_writing_submission_boundary['theorem_assumption_retained_theorem_interface_count']}` / `{strict_proof_writing_submission_boundary['theorem_assumption_retained_theorem_interface_ids']}`; open output boundaries `{strict_proof_writing_submission_boundary['theorem_assumption_open_nonpromotion_boundary_count']}` / `{strict_proof_writing_submission_boundary['theorem_assumption_open_nonpromotion_boundary_ids']}`; safe/reading-rule `{strict_proof_writing_submission_boundary['safe_reader_claim_boundary_present']}` / `{strict_proof_writing_submission_boundary['reading_rule_boundary_present']}`.",
        f"- Strict proof-writing P7 output nonclaim/residual-to-error boundary: `{strict_proof_writing_submission_boundary['p7_retained_nonpromotion_boundary_present']}`.",
        f"- Strict proof-writing B1 closure-scope boundary: `{strict_proof_writing_submission_boundary['b1_closure_scope_boundary_present']}`.",
        f"- Strict proof-writing B1 AD-expanded closure ledger/cells: `{strict_proof_writing_submission_boundary['b1_ad_expanded_closure_ledger_present']}` / `{strict_proof_writing_submission_boundary['b1_ad_expanded_symbolic_oracle_closed_cells']}`.",
        f"- Strict proof-writing P6 solver-scope boundary: `{strict_proof_writing_submission_boundary['p6_solver_scope_boundary_present']}`.",
        f"- Strict proof-writing P1/P2 compact-tube boundary: `{strict_proof_writing_submission_boundary['p1p2_compact_tube_boundary_present']}`.",
        f"- Strict proof-writing P3/P4 implementation-defect boundary: `{strict_proof_writing_submission_boundary['p3p4_implementation_boundary_present']}`.",
        f"- Strict proof-writing P5 direct-route boundary: `{strict_proof_writing_submission_boundary['p5_direct_route_boundary_present']}`.",
        f"- Strict proof-writing proof-causality ledger: `{strict_proof_writing_submission_boundary['proof_causality_ledger_present']}`.",
        f"- Strict proof-writing direct-route anti-circularity ledger: `{strict_proof_writing_submission_boundary['direct_route_anticircularity_ledger_present']}`.",
        f"- Strict proof-writing theorem-interface satisfaction ledger: `{strict_proof_writing_submission_boundary['p_interface_satisfaction_ledger_present']}`.",
        f"- Strict proof-writing P7 residual-to-error obligation ledger: `{strict_proof_writing_submission_boundary['p7_residual_to_error_ledger_present']}`.",
        f"- Strict proof-writing theorem-use rule: `{strict_proof_writing_submission_boundary['theorem_use_rule_present']}`.",
        f"- Strict proof-writing quantifier/domain ledger: `{strict_proof_writing_submission_boundary['quantifier_domain_ledger_present']}`.",
        f"- Strict proof-writing local-to-global transfer ledger: `{strict_proof_writing_submission_boundary['local_global_transfer_ledger_present']}`.",
        f"- Strict proof-writing objective-completion boundary: `{strict_proof_writing_submission_boundary['objective_completion_boundary_present']}`.",
        f"- Strict proof-writing constant-dependency ledger: `{strict_proof_writing_submission_boundary['constant_dependency_ledger_present']}`.",
        f"- Strict proof-writing theorem dependency consumption ledger: `{strict_proof_writing_submission_boundary['theorem_dependency_consumption_ledger_present']}`.",
        f"- Strict proof-writing accepted-branch consistency ledger: `{strict_proof_writing_submission_boundary['branch_consistency_ledger_present']}`.",
        f"- Strict proof-writing implementation-route/oracle separation ledger: `{strict_proof_writing_submission_boundary['implementation_route_oracle_ledger_present']}`.",
        f"- Strict proof-writing nonlinear-solver scale ledger: `{strict_proof_writing_submission_boundary['nonlinear_solver_scale_ledger_present']}`.",
        f"- Strict proof-writing local-defect decomposition ledger: `{strict_proof_writing_submission_boundary['local_defect_decomposition_ledger_present']}`.",
        f"- Strict proof-writing theorem output scope ledger: `{strict_proof_writing_submission_boundary['theorem_output_scope_ledger_present']}`.",
        f"- Strict proof-writing reporting-map/norm-equivalence ledger: `{strict_proof_writing_submission_boundary['reporting_map_ledger_present']}`.",
        f"- Strict proof-writing reference proof-order correspondence: closed `{strict_proof_writing_submission_boundary['reference_proof_order_correspondence_closed']}`; no-estimate-transfer `{strict_proof_writing_submission_boundary['reference_proof_order_no_estimate_transfer']}`; nonimport `{strict_proof_writing_submission_boundary['reference_proof_order_nonimport_boundary']}`; constraint/multiplier split `{strict_proof_writing_submission_boundary['reference_proof_order_constraint_multiplier_split']}`.",
        f"- Strict proof-writing forbidden claims/global boundaries: claims `{strict_proof_writing_submission_boundary['forbidden_reader_claims']}`; boundary `{strict_proof_writing_submission_boundary['forbidden_reader_claims_boundary_present']}`; unconditional/eta/fixed/residual/source-package `{strict_proof_writing_submission_boundary['forbidden_unconditional_theorem_boundary_present']}/{strict_proof_writing_submission_boundary['forbidden_eta_h_solver_policy_claim_boundary_present']}/{strict_proof_writing_submission_boundary['forbidden_fixed_tolerance_asymptotic_claim_boundary_present']}/{strict_proof_writing_submission_boundary['forbidden_residual_to_error_theorem_claim_boundary_present']}/{strict_proof_writing_submission_boundary['forbidden_source_policy_full_tfe_package_claim_boundary_present']}`; global `{strict_proof_writing_submission_boundary['proof_global_boundaries_retained']}`.",
        f"- Strict proof-writing no-promotion locks: residual-to-error `{strict_proof_writing_submission_boundary['residual_to_error_not_promoted']}`; source-policy/full-TFE package `{strict_proof_writing_submission_boundary['source_policy_full_tfe_not_promoted']}`.",
        f"- Human-runnable local self-contained/replay-only examples: `{human_runnable_self_contained_examples}` / `{human_runnable_replay_only_examples}`.",
        f"- B6 local runner rows/source-policy rows: `{b6_local_evidence.get('local_rows')}/{b6_local_evidence.get('source_policy_external_rows_closed')}/{b6_local_evidence.get('source_policy_external_rows_total')}`.",
        f"- Compact closed-loop local runner passed/Python-lines: `{closed_loop_candidate.get('runner_passed')}/{closed_loop_candidate.get('candidate_python_line_count')}`.",
        f"- P1 single/double local runners ready: `{p1_local_runner.get('p1_single_runner_candidate_ready')}/{p1_local_runner.get('p1_double_runner_candidate_ready')}`.",
        f"- Quality review closed: `{quality_review_closed}`.",
        f"- Minimal reproducibility code package ready: `{minimal_code_ready}`.",
        f"- Minimal reproducible submission code ready: `{minimal_code_ready}`.",
        f"- Combined Python line count: `{combined_python_line_count}`.",
        "",
        "## Blocking Requirements",
        "",
        "| id | status | evidence | observed blocker | next to close |",
        "|---|---|---|---|---|",
    ]
    for item in blocking_open:
        observed = item["observed"]
        if item["id"] == "OC4":
            observed_blocker = (
                f"source_policy_reproduction={observed.get('source_policy_reproduction')}; "
                f"same_test_campaign_status={observed.get('same_test_campaign_status')}; "
                f"external_superiority_claim_allowed={observed.get('external_superiority_claim_allowed')}; "
                f"ra_hi_closeout={observed.get('ra_hi_closeout_status')}; "
                f"ra_hi_rows={observed.get('ra_hi_closeout_ra_rows')}/"
                f"{observed.get('ra_hi_closeout_hi_rows')}/"
                f"{observed.get('ra_hi_closeout_source_policy_rows_total')}; "
                f"commands={observed.get('ra_hi_closeout_ready_command_count')}/"
                f"{observed.get('ra_hi_closeout_ready_command_mapped_rows')}; "
                f"traceability_unique={observed.get('source_policy_execution_handoff_unique_mapped_row_count')}/"
                f"{observed.get('source_policy_execution_handoff_ra_hi_unique_row_count')}; "
                f"traceability_refs={observed.get('source_policy_execution_handoff_traced_command_row_reference_total')}/"
                f"{observed.get('source_policy_execution_handoff_declared_mapped_row_reference_total')}; "
                f"traceability_mismatch_terminal_closed={observed.get('source_policy_execution_handoff_declared_vs_traced_mismatch_count')}/"
                f"{observed.get('source_policy_execution_handoff_terminal_rows_with_command_refs')}/"
                f"{observed.get('source_policy_execution_handoff_traceability_closed_rows')}; "
                f"promoted={observed.get('ra_hi_closeout_source_policy_rows_promoted')}; "
                f"executed={observed.get('ra_hi_closeout_execution_invoked')}; "
                f"ra_hi_terminal_future_complete="
                f"{observed.get('ra_hi_current_evidence_terminal_not_promotable_rows')}/"
                f"{observed.get('ra_hi_future_promotion_requires_authorized_execution_or_new_artifact_rows')}/"
                f"{observed.get('ra_hi_source_policy_reproduction_complete_rows')}; "
                f"handoff={observed.get('source_policy_execution_handoff_status')}; "
                f"handoff_authorized={observed.get('source_policy_execution_handoff_authorized')}; "
                f"handoff_commands_not_run={observed.get('source_policy_execution_handoff_commands_not_run')}; "
                f"approval={observed.get('source_policy_execution_handoff_exact_approval_statement')}; "
                f"driver={observed.get('source_policy_execution_handoff_driver')}; "
                f"driver_requires_exact={observed.get('source_policy_execution_handoff_driver_requires_exact_approval')}; "
                f"opt_in_commands={observed.get('source_policy_execution_handoff_opt_in_required_command_count')}/"
                f"{observed.get('source_policy_execution_handoff_opt_in_required_mapped_rows')}; "
                f"terminal_unable={observed.get('source_policy_execution_handoff_terminal_unable_rows')}; "
                f"refusal_boundary={observed.get('b4_guarded_driver_no_opt_in_refusal_proved_static')}/"
                f"{observed.get('b4_guarded_driver_wrong_approval_refusal_proved_static')}/"
                f"{observed.get('b4_guarded_driver_refusal_exit_code')}/"
                f"{observed.get('b4_guarded_driver_pre_guard_command_count')}/"
                f"{observed.get('b4_guarded_driver_post_guard_source_policy_command_count')}/"
                f"{observed.get('b4_guarded_driver_source_policy_execution_invoked')}/"
                f"{observed.get('b4_guarded_driver_submission_ready')}; "
                f"provenance={observed.get('full_source_policy_row_provenance_preflight')}/"
                f"{observed.get('full_source_policy_row_provenance_source_policy_closed_ratio')}/"
                f"{observed.get('full_source_policy_row_provenance_promotion_ready_rows')}; "
                f"provenance_handoff={observed.get('full_source_policy_row_provenance_handoff_status')}/"
                f"{observed.get('full_source_policy_row_provenance_handoff_authorized')}/"
                f"{observed.get('full_source_policy_row_provenance_handoff_commands_not_run')}"
            )
        elif item["id"] == "OC5":
            observed_blocker = (
                f"source_policy_closed_rows={observed.get('source_policy_closed_rows')}; "
                f"active_flagged_rows={observed.get('active_flagged_rows')}"
            )
        elif item["id"] == "OC6":
            observed_blocker = (
                f"contract_gap_blocks={observed.get('tfe_dae_runner_contract_gap_missing_block_count')}; "
                f"effective_execution_blocks={observed.get('tfe_dae_runner_contract_gap_effective_missing_block_count')}; "
                f"terminal_nonpromoted_blocks={observed.get('tfe_dae_runner_contract_gap_terminal_nonpromoted_block_count')}; "
                f"candidate_backed_non_equivalent_runner_blocks={observed.get('tfe_dae_runner_contract_gap_candidate_backed_non_equivalent_runner_block_count')}; "
                f"contract_gap_ready={observed.get('tfe_dae_runner_contract_gap_ready_to_execute_source_policy_now')}; "
                f"nonheavy_demoted={observed.get('tfe_dae_runner_contract_gap_nonheavy_dispositioned_by_demotion')}; "
                f"execution_blocks={observed.get('tfe_dae_runner_contract_gap_execution_block_count')}; "
                f"preflight_opt_in={observed.get('tfe_source_policy_execution_preflight_opt_in_required')}; "
                f"terminal_route={observed.get('tfe_source_policy_execution_preflight_current_route')}; "
                f"preflight_promote_ready={observed.get('tfe_source_policy_execution_preflight_can_promote_rows_now')}/"
                f"{observed.get('tfe_source_policy_execution_preflight_ready_now')}; "
                f"self_reproduction={observed.get('tfe_self_reproduction_status')}/"
                f"{observed.get('tfe_self_reproduction_source_policy_closed_ratio')}; "
                f"public_code={observed.get('tfe_self_reproduction_public_code_recheck_status')}; "
                f"refresh={observed.get('tfe_public_code_refresh_20260620_rows')}/"
                f"{observed.get('tfe_public_code_refresh_20260620_current_queries')}/"
                f"{observed.get('tfe_public_code_refresh_20260620_positive_artifact_rows')}/"
                f"{observed.get('tfe_public_code_refresh_20260620_source_policy_closed_ratio')}; "
                f"latest_probe={observed.get('tfe_public_code_refresh_20260620_latest_external_probe_date')}/"
                f"{observed.get('tfe_public_code_refresh_20260620_latest_external_probe_count')}/"
                f"{observed.get('tfe_public_code_refresh_20260620_latest_external_probe_positive_artifact_rows')}/"
                f"{observed.get('tfe_public_code_refresh_20260620_latest_external_probe_source_policy_rows_closed')}/"
                f"{observed.get('tfe_public_code_refresh_20260620_latest_external_probe_access_limited_count')}/"
                f"{observed.get('tfe_public_code_refresh_20260620_latest_external_probe_global_absence_proved')}/"
                f"{observed.get('tfe_public_code_refresh_20260620_latest_external_probe_reopen_triggered')}; "
                f"external_recheck={observed.get('oc6_external_source_artifact_recheck_20260621_date')}/"
                f"{observed.get('oc6_external_source_artifact_recheck_20260621_query_count')}/"
                f"{observed.get('oc6_external_source_artifact_recheck_20260621_positive_artifact_rows')}/"
                f"{observed.get('oc6_external_source_artifact_recheck_20260621_source_equivalent_artifact_rows')}/"
                f"{observed.get('oc6_external_source_artifact_recheck_20260621_source_policy_rows_closed')}/"
                f"{observed.get('oc6_external_source_artifact_recheck_20260621_reopen_triggered')}/"
                f"{observed.get('oc6_external_source_artifact_recheck_20260621_global_absence_proved')}; "
                f"publisher_availability={observed.get('oc6_tfe_publisher_artifact_availability_20260621_date')}/"
                f"{observed.get('oc6_tfe_publisher_artifact_availability_20260621_official_article_checked')}/"
                f"{observed.get('oc6_tfe_publisher_artifact_availability_20260621_source_artifact_signal_count')}/"
                f"{observed.get('oc6_tfe_publisher_artifact_availability_20260621_positive_artifact_rows')}/"
                f"{observed.get('oc6_tfe_publisher_artifact_availability_20260621_source_equivalent_artifact_rows')}/"
                f"{observed.get('oc6_tfe_publisher_artifact_availability_20260621_source_policy_rows_closed')}/"
                f"{observed.get('oc6_tfe_publisher_artifact_availability_20260621_reopen_triggered')}/"
                f"{observed.get('oc6_tfe_publisher_artifact_availability_20260621_global_absence_proved')}; "
                f"request_packet={observed.get('oc6_tfe_source_equivalent_artifact_request_packet_20260621_request_ready')}/"
                f"{observed.get('oc6_tfe_source_equivalent_artifact_request_packet_20260621_request_sent')}/"
                f"{observed.get('oc6_tfe_source_equivalent_artifact_request_packet_20260621_requested_artifact_count')}/"
                f"{observed.get('oc6_tfe_source_equivalent_artifact_request_packet_20260621_source_policy_rows_closed')}/"
                f"{observed.get('oc6_tfe_source_equivalent_artifact_request_packet_20260621_reopen_triggered')}/"
                f"{observed.get('oc6_tfe_source_equivalent_artifact_request_packet_20260621_submission_ready')}; "
                f"preflight={observed.get('tfe_runner_contract_preflight_status')}/"
                f"{observed.get('tfe_runner_contract_preflight_entrypoints')}/"
                f"{observed.get('tfe_runner_contract_preflight_candidate_backed')}/"
                f"{observed.get('tfe_runner_contract_preflight_source_policy_rows_completed')}/"
                f"{observed.get('tfe_runner_contract_preflight_execution_blocks')}; "
                f"pendulum_dae_runner_implemented={observed.get('pendulum_dae_runner_implemented')}; "
                f"brown_mcphee_friction_law_implemented={observed.get('brown_mcphee_friction_law_implemented')}; "
                f"source_policy_rows_completed={observed.get('source_policy_rows_completed')}; "
                f"full_T10_grid_resolved={observed.get('source_grid_policy_resolved_for_full_T10')}; "
                f"bridge_rows={observed.get('dae_trajectory_bridge_contract_rows')}/"
                f"{observed.get('dae_trajectory_bridge_contract_matched_rows')}/"
                f"{observed.get('dae_trajectory_bridge_contract_source_policy_rows_completed')}; "
                f"bridge_equivalent_dae_method_monolithic="
                f"{observed.get('dae_trajectory_bridge_contract_dae_runner_equivalent')}/"
                f"{observed.get('dae_trajectory_bridge_contract_method_runner_equivalent')}/"
                f"{observed.get('dae_trajectory_bridge_contract_monolithic_integrator')}; "
                f"friction_contract_rows={observed.get('candidate_frictional_dae_trajectory_contract_rows')}/"
                f"{observed.get('candidate_frictional_dae_trajectory_contract_step_residual_rows')}/"
                f"{observed.get('candidate_frictional_dae_trajectory_contract_source_policy_rows_completed')}; "
                f"friction_contract_equivalent_dae_method_source_monolithic="
                f"{observed.get('candidate_frictional_dae_trajectory_contract_dae_runner_equivalent')}/"
                f"{observed.get('candidate_frictional_dae_trajectory_contract_method_runner_equivalent')}/"
                f"{observed.get('candidate_frictional_dae_trajectory_contract_brown_mcphee_source_code_equivalent_law')}/"
                f"{observed.get('candidate_frictional_dae_trajectory_contract_monolithic_integrator')}; "
                f"transition_velocity_sensitivity_rows="
                f"{observed.get('brown_mcphee_transition_velocity_sensitivity_rows')}/"
                f"{observed.get('brown_mcphee_transition_velocity_sensitivity_contract_rows')}/"
                f"{observed.get('brown_mcphee_transition_velocity_sensitivity_source_policy_rows_completed')}; "
                f"transition_velocity_sensitivity_material="
                f"{observed.get('brown_mcphee_transition_velocity_sensitivity_material')}; "
                f"transition_velocity_sensitivity_equivalence_false="
                f"{observed.get('brown_mcphee_transition_velocity_sensitivity_equivalence_flags_false')}; "
                f"brown_certificate={observed.get('brown_mcphee_source_code_equivalence_certificate_available')}/"
                f"{observed.get('brown_mcphee_source_code_equivalence_certificate_positive')}/"
                f"{observed.get('brown_mcphee_source_code_equivalence_certificate_nonheavy_block_closed')}; "
                f"endpoint_certificate={observed.get('full_T10_endpoint_policy_closure_certificate_available')}/"
                f"{observed.get('full_T10_endpoint_policy_closure_certificate_positive')}/"
                f"{observed.get('full_T10_endpoint_policy_closure_certificate_nonheavy_block_closed')}; "
                f"gauss6_dae_contract={observed.get('gauss6_fullva_dae_candidate_contract_rows')}/"
                f"{observed.get('gauss6_fullva_dae_candidate_contract_source_policy_rows_completed')}/"
                f"{observed.get('gauss6_fullva_dae_candidate_contract_dae_equivalent')}/"
                f"{observed.get('gauss6_fullva_dae_candidate_contract_fullva_dae_equivalent')}"
            )
        elif item["id"] == "OC12":
            observed_blocker = (
                f"local_runner_package_partial_ready={observed.get('local_runner_package_partial_ready')}; "
                f"full_source_policy_runner_package_ready={observed.get('full_source_policy_runner_package_ready')}; "
                f"dependency_status={observed.get('minimal_submission_code_dependency_boundary_status')}; "
                f"dependency_blockers={observed.get('minimal_submission_code_dependency_blockers')}; "
                f"archive_tfe_preflight={observed.get('full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_status')}/"
                f"{observed.get('full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_entrypoints')}/"
                f"{observed.get('full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_candidate_backed')}/"
                f"{observed.get('full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_source_policy_rows_completed')}/"
                f"{observed.get('full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_execution_blocks')}; "
                f"combined_python_line_count={observed.get('combined_python_line_count')}"
            )
        else:
            observed_blocker = "see JSON observed object"
        lines.append(
            f"| `{item['id']}` | `{item['status']}` | `{', '.join(item['evidence'])}` | "
            f"{observed_blocker} | {item['next_to_close']} |"
        )
    lines.extend(
        [
            "",
            "## Requirement Status",
            "",
            "| id | status | blocking | requirement | next to close |",
            "|---|---|---|---|---|",
        ]
    )
    for item in requirements:
        lines.append(
            f"| `{item['id']}` | `{item['status']}` | `{item['blocking_for_goal_completion']}` | "
            f"{item['requirement']} | {item['next_to_close']} |"
        )
    lines.extend(
        [
            "",
            "## Required Next Actions",
            "",
        ]
    )
    for action in audit["required_next_actions"]:
        lines.append(f"- {action}.")
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("objective_completion_audit=written")
    print(f"status={audit['status']}")
    print(f"objective_complete={audit['objective_complete']}")
    print(f"satisfied_partial_open={len(satisfied)}/{len(partial)}/{len(open_items)}")
    print(f"blocking_open={len(blocking_open)}")
    print(f"source_policy_execution_allowed_now={source_policy_execution_allowed_now}")
    print(f"source_policy_execution_invoked={source_policy_execution_invoked}")
    print(
        "b4_guarded_driver_refusal_boundary_audit_20260621="
        f"{b4_guarded_refusal_boundary_tuple}"
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


if __name__ == "__main__":
    main()
