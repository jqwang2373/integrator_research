#!/usr/bin/env python3
"""Build the runner-centered reproducibility-package audit.

This audit separates four things that were previously easy to conflate:
the large research/audit repository, the compact replay candidate, the
self-contained local runner for accepted rows, and the still-open full
source-policy runner package.
"""

from __future__ import annotations

import json
from pathlib import Path


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
V048 = ROOT / "v048_cross_paper_same_test_benchmarks"
OUT_JSON = PAPER / "CMAME_RUNNER_CENTERED_REPRODUCIBILITY_AUDIT.json"
OUT_MD = PAPER / "CMAME_RUNNER_CENTERED_REPRODUCIBILITY_AUDIT.md"
RUNNER_ADAPTER_MANIFEST = PAPER / "CMAME_RUNNER_ADAPTER_CANDIDATE_MANIFEST.json"

REVIEWER_PYTHON_FILE_LIMIT = 12
REVIEWER_PYTHON_LINE_LIMIT = 2000

RUNNER_SOURCE_CANDIDATES = [
    ("../v048_cross_paper_same_test_benchmarks/run_coarse_four_example_order.py", "four_example_matrix_driver"),
    ("../v048_cross_paper_same_test_benchmarks/run_v048.py", "shared_external_and_local_runner_library"),
    ("../v048_cross_paper_same_test_benchmarks/closed_loop_fullva_dynamic_residual.py", "closed_loop_dynamic_core"),
    (
        "../v048_cross_paper_same_test_benchmarks/build_closed_loop_true_dynamic_strict_common_reference.py",
        "four_link_slider_crank_true_dynamic_builder",
    ),
    ("../v048_cross_paper_same_test_benchmarks/tfe_source_pendulum_model.py", "tfe_source_policy_candidate"),
]


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def resolve(path_label: str) -> Path:
    if path_label.startswith("../"):
        return (PAPER / path_label).resolve()
    return PAPER / path_label


def line_count(path: Path) -> int:
    return len(read_text(path).splitlines())


def ordered_blocker_map(payload: dict[str, object]) -> dict[str, object]:
    return {req_id: payload[req_id] for req_id in ["OC4", "OC6", "OC12"] if req_id in payload}


def source_item(path_label: str, role: str) -> dict[str, object]:
    path = resolve(path_label)
    return {
        "path": path_label,
        "role": role,
        "exists": path.exists() and path.stat().st_size > 0,
        "python_lines": line_count(path) if path.exists() and path.suffix == ".py" else None,
    }


def main() -> None:
    review = read_json(PAPER / "CMAME_REVIEW_AGENT_REPORT.json")
    matrix = read_json(PAPER / "PAPER_NUMERICAL_RESULT_MATRIX.json")
    minimal = read_json(PAPER / "CMAME_MINIMAL_REPRODUCIBILITY_CANDIDATE_MANIFEST.json")
    narrowed_archive = read_json(PAPER / "CMAME_NARROWED_REPRO_CODE_ARCHIVE_MANIFEST.json")
    runner_adapter = read_json(RUNNER_ADAPTER_MANIFEST) if RUNNER_ADAPTER_MANIFEST.exists() else {}
    b6_local_evidence = read_json(PAPER / "B6_FOUR_EXAMPLE_LOCAL_EVIDENCE_SUMMARY.json")
    closed_loop_audit = read_json(PAPER / "B6_CLOSED_LOOP_SELF_CONTAINED_EXTRACTION_AUDIT.json")
    closed_loop_candidate = read_json(PAPER / "CMAME_CLOSED_LOOP_LOCAL_RUNNER_CANDIDATE_MANIFEST.json")
    proof = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
    source_policy = read_json(PAPER / "FOUR_EXAMPLE_SOURCE_POLICY_DASHBOARD.json")
    prose = read_json(PAPER / "CMAME_PROSE_RESIDUE_AUDIT.json")
    global_policy = read_json(V048 / "results" / "global_comparison_policy_audit.json")
    b4_execution_handoff = read_json(PAPER / "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json")
    full_source_policy_row_provenance = read_json(PAPER / "FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.json")
    tfe_dae_gap = read_json(PAPER / "TFE_DAE_RUNNER_CONTRACT_GAP_AUDIT.json")
    tfe_runner_contract_preflight = read_json(
        PAPER / "TFE_RUNNER_CONTRACT_PREFLIGHT_CERTIFICATE.json"
    )
    public_refresh_latest = read_json(PAPER / "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.json")
    objective_completion = read_json(PAPER / "OBJECTIVE_COMPLETION_AUDIT.json")
    required_user_approval_statement = (
        b4_execution_handoff.get("required_user_approval_statement")
        or b4_execution_handoff.get("exact_approval_statement")
        or b4_execution_handoff.get("opt_in_required_phrase")
    )

    code_checks = review.get("code_hygiene_checks", {})
    result_checks = review.get("result_checks", {})
    source_candidates = [source_item(path, role) for path, role in RUNNER_SOURCE_CANDIDATES]
    existing_runner_source_lines = sum(
        int(item["python_lines"] or 0) for item in source_candidates if item["exists"]
    )

    candidate_python_files = int(minimal.get("candidate_python_file_count") or 0)
    candidate_python_lines = int(minimal.get("candidate_python_line_count") or 0)
    source_policy_closed_rows = result_checks.get("source_policy_apples_to_apples_external_rows")
    source_policy_total_rows = result_checks.get("source_policy_apples_to_apples_external_total_rows")
    source_policy_closed_ratio = f"{source_policy_closed_rows}/{source_policy_total_rows}"
    candidate_size_ok = (
        0 < candidate_python_files <= REVIEWER_PYTHON_FILE_LIMIT
        and 0 < candidate_python_lines <= REVIEWER_PYTHON_LINE_LIMIT
    )
    candidate_replay_only = minimal.get("read_only_replay_package") is True
    source_policy_ready = (
        result_checks.get("source_policy_apples_to_apples_external_rows") == 40
        and result_checks.get("source_policy_apples_to_apples_external_total_rows") == 40
    )
    proof_ready = proof.get("closure_state", {}).get("proof_gap_closed") is True
    prose_dependency = prose.get("post_baseline_final_prose_dependency", {})
    prose_preflight = prose.get("b6_closure_readiness_preflight", {})
    b6_final_prose_ready = (
        prose_dependency.get("final_prose_pass_ready") is True
        and prose_dependency.get("b6_closure_allowed_now") is True
        and prose_preflight.get("status") == "b6_final_prose_pass_closed_under_narrowed_b4_b7_scope"
    )
    runner_centered_ready = (
        minimal.get("submission_ready") is True
        and candidate_size_ok
        and not candidate_replay_only
        and source_policy_ready
        and proof_ready
    )
    closed_loop_candidate_compact = closed_loop_candidate.get("candidate_python_line_limit_ok") is True
    local_runner_centered_candidate_ready = (
        b6_local_evidence.get("human_runnable_four_example_self_contained_simulation_ready") is True
        and closed_loop_audit.get("self_contained_runner_ready") is True
        and closed_loop_candidate.get("runner_passed") is True
        and closed_loop_candidate.get("self_contained_simulation_runner") is True
        and closed_loop_candidate.get("imports_v046_v047_v048_or_v029") is False
        and closed_loop_candidate_compact
    )
    if closed_loop_candidate.get("runner_passed") is True and closed_loop_candidate_compact:
        r2_status = "partial_compact_closed_loop_candidate_passed"
        r2_evidence = (
            "small report-only adapter plus B6 four-example local-evidence runner present; "
            "closed-loop executable candidate now regenerates four_link/slider_crank rows under the compact "
            "reviewer-facing line limit, but the full runner-centered package/source-policy rows remain open; "
            f"candidate rows={closed_loop_candidate.get('closed_loop_local_rows')}, "
            f"compact={closed_loop_candidate_compact}; "
            f"closed-loop extraction audit={closed_loop_audit.get('status')}"
        )
    elif closed_loop_candidate.get("runner_passed") is True:
        r2_status = "partial_non_compact_candidate_passed"
        r2_evidence = (
            "small report-only adapter plus B6 four-example local-evidence runner present; "
            "closed-loop executable candidate now regenerates four_link/slider_crank rows but is not compact; "
            f"candidate rows={closed_loop_candidate.get('closed_loop_local_rows')}, "
            f"compact={closed_loop_candidate_compact}; "
            f"closed-loop extraction audit={closed_loop_audit.get('status')}"
        )
    elif runner_adapter.get("runner_adapter_present") is True:
        r2_status = "partial"
        r2_evidence = (
            "small report-only adapter plus B6 four-example local-evidence runner present, "
            "but four-link/slider-crank remain replay-only and the self-contained simulation runner is still missing; "
            f"closed-loop extraction audit={closed_loop_audit.get('status')}"
        )
    else:
        r2_status = "open"
        r2_evidence = "current package replays checked artifacts instead of regenerating the 44-row matrix"

    requirements = [
        {
            "id": "R1_compact_size",
            "status": "satisfied" if candidate_size_ok else "open",
            "evidence": f"{candidate_python_files} Python file(s), {candidate_python_lines} Python lines",
        },
        {
            "id": "R2_runner_centered_generation",
            "status": r2_status,
            "evidence": r2_evidence,
        },
        {
            "id": "R3_source_policy_external_rows",
            "status": "open" if not source_policy_ready else "satisfied",
            "evidence": (
                f"{result_checks.get('source_policy_apples_to_apples_external_rows')}/"
                f"{result_checks.get('source_policy_apples_to_apples_external_total_rows')}"
            ),
        },
        {
            "id": "R4_proof_boundary",
            "status": "open" if not proof_ready else "satisfied",
            "scope": "direct_pc2_proof_boundary_subcheck_not_global_submission_readiness",
            "evidence": (
                f"direct_pc2_proof_gap_closed={proof_ready}; "
                "primitive/Taylor, solver-policy, residual-to-error, and source-policy boundaries remain separate"
            ),
        },
        {
            "id": "R5_research_audit_tree_not_primary_code",
            "status": "satisfied" if code_checks.get("research_audit_repo_provenance_only") is True else "open",
            "evidence": (
                f"combined_python_line_count={code_checks.get('combined_python_line_count')}, "
                f"primary_allowed={code_checks.get('research_audit_repo_primary_submission_allowed')}"
            ),
        },
    ]
    source_policy_action_boundary = full_source_policy_row_provenance.get(
        "action_boundary", {}
    )
    safe_next_actions_without_b4_opt_in = [
        {
            "id": "rebuild_read_only_audit_chain",
            "allowed_without_b4_opt_in": True,
            "does_not_execute_source_policy_commands": True,
            "description": (
                "Rebuild the read-only provenance, archive-gap, objective, review, "
                "runner-centered, and manifest audits after metadata-only changes."
            ),
            "representative_scripts": [
                "build_full_source_policy_row_provenance_audit.py",
                "build_full_source_policy_runner_archive_gap_audit.py",
                "build_objective_completion_audit.py",
                "cmame_submission_review_agent.py",
                "build_cmame_reproducibility_package_manifest.py",
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
                "tfe2026_original_pendulum": "new_public_or_source_code_equivalent_tfe_implementation_artifact",
                "vp2024_velocity_partitioning": "new_distinct_public_vp2024_velocity_partitioning_code_path",
            },
        },
    ]
    opt_in_required_actions = [
        {
            "id": "authorized_b4_ra_hi_source_policy_execution",
            "allowed_without_b4_opt_in": False,
            "requires_exact_user_approval_statement": True,
            "exact_required_user_approval_statement": required_user_approval_statement,
            "guarded_execution_driver": b4_execution_handoff.get("guarded_execution_driver"),
            "driver_requires_exact_approval": b4_execution_handoff.get(
                "driver_requires_exact_approval"
            ),
            "driver_does_not_authorize_execution": b4_execution_handoff.get(
                "driver_does_not_authorize_execution"
            ),
            "command_count": b4_execution_handoff.get("ready_command_count"),
            "mapped_external_rows": b4_execution_handoff.get(
                "ready_command_mapped_external_rows"
            ),
            "post_execution_promotion_required": True,
            "description": (
                "Run the prepared RA/HI source-policy commands only after the exact B4 "
                "approval phrase is supplied, then validate any post-execution promotion "
                "before closing source-policy rows."
            ),
        },
    ]
    safe_next_actions_without_b4_opt_in = objective_completion.get(
        "safe_actions_without_b4_opt_in",
        safe_next_actions_without_b4_opt_in,
    )
    opt_in_required_actions = objective_completion.get(
        "opt_in_required_actions",
        opt_in_required_actions,
    )
    runner_package_blocker_required_to_close_by_id = {
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
                "requires_exact_b4_opt_in": source_policy_action_boundary.get(
                    "exact_b4_opt_in_required_for_execution"
                ),
                "execution_allowed_now": source_policy_action_boundary.get(
                    "source_policy_execution_allowed_now"
                ),
                "execution_invoked": full_source_policy_row_provenance.get(
                    "source_policy_execution_invoked"
                ),
                "guarded_execution_driver": b4_execution_handoff.get(
                    "guarded_execution_driver"
                ),
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
            "promotion_ready_rows": full_source_policy_row_provenance.get(
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
            "tfe_runner_closed": tfe_runner_contract_preflight.get("source_policy_closed"),
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
            "reopen_condition": tfe_dae_gap.get("source_policy_execution_preflight", {}).get(
                "reopen_condition"
            ),
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
            "full_source_policy_runner_package_ready": runner_centered_ready,
            "narrowed_repro_code_archive_ready": narrowed_archive.get("status")
            == "narrowed_repro_code_archive_ready_source_policy_open",
            "narrowed_repro_code_archive_submission_ready": narrowed_archive.get(
                "submission_ready"
            ),
            "source_policy_closed_ratio": full_source_policy_row_provenance.get(
                "source_policy_closed_ratio"
            ),
            "remaining_source_policy_rows_to_close": (
                int(full_source_policy_row_provenance.get("source_policy_rows_total") or 0)
                - int(full_source_policy_row_provenance.get("source_policy_rows_closed") or 0)
            ),
            "safe_current_archive_use": "narrowed_claim_replay_and_audit_provenance_only",
            "action_boundary": source_policy_action_boundary,
        },
    }
    runner_package_blocker_safe_next_actions_by_id = {
        req_id: safe_next_actions_without_b4_opt_in
        for req_id in ["OC4", "OC6", "OC12"]
    }
    runner_package_blocker_opt_in_required_actions_by_id = {
        "OC4": opt_in_required_actions,
        "OC6": [],
        "OC12": opt_in_required_actions,
    }
    runner_package_blocker_required_to_close_by_id = objective_completion.get(
        "blocker_required_to_close_by_id",
        runner_package_blocker_required_to_close_by_id,
    )
    runner_package_blocker_required_to_close_by_id = ordered_blocker_map(
        runner_package_blocker_required_to_close_by_id
    )
    runner_package_blocker_safe_next_actions_by_id = objective_completion.get(
        "blocker_safe_next_actions_by_id",
        runner_package_blocker_safe_next_actions_by_id,
    )
    runner_package_blocker_safe_next_actions_by_id = ordered_blocker_map(
        runner_package_blocker_safe_next_actions_by_id
    )
    runner_package_blocker_opt_in_required_actions_by_id = objective_completion.get(
        "blocker_opt_in_required_actions_by_id",
        runner_package_blocker_opt_in_required_actions_by_id,
    )
    runner_package_blocker_opt_in_required_actions_by_id = ordered_blocker_map(
        runner_package_blocker_opt_in_required_actions_by_id
    )

    audit = {
        "schema": "cmame-runner-centered-reproducibility-audit-v1",
        "status": "local_runner_centered_candidate_ready_source_policy_package_open",
        "generated_from": [
            "CMAME_REVIEW_AGENT_REPORT.json",
            "PAPER_NUMERICAL_RESULT_MATRIX.json",
            "CMAME_MINIMAL_REPRODUCIBILITY_CANDIDATE_MANIFEST.json",
            "CMAME_NARROWED_REPRO_CODE_ARCHIVE_MANIFEST.json",
            "CMAME_RUNNER_ADAPTER_CANDIDATE_MANIFEST.json",
            "B6_FOUR_EXAMPLE_LOCAL_EVIDENCE_SUMMARY.json",
            "B6_CLOSED_LOOP_SELF_CONTAINED_EXTRACTION_AUDIT.json",
            "CMAME_CLOSED_LOOP_LOCAL_RUNNER_CANDIDATE_MANIFEST.json",
            "PROOF_CLOSURE_MANIFEST.json",
            "FOUR_EXAMPLE_SOURCE_POLICY_DASHBOARD.json",
            "CMAME_PROSE_RESIDUE_AUDIT.json",
            "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json",
            "FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.json",
            "TFE_DAE_RUNNER_CONTRACT_GAP_AUDIT.json",
            "TFE_RUNNER_CONTRACT_PREFLIGHT_CERTIFICATE.json",
            "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.json",
            "OBJECTIVE_COMPLETION_AUDIT.json",
            "../v048_cross_paper_same_test_benchmarks/results/global_comparison_policy_audit.json",
        ],
        "read_only": True,
        "submission_ready": False,
        "runner_centered_package_ready": runner_centered_ready,
        "local_runner_centered_candidate_ready": local_runner_centered_candidate_ready,
        "full_source_policy_runner_package_ready": runner_centered_ready,
        "candidate_python_file_count": candidate_python_files,
        "candidate_python_line_count": candidate_python_lines,
        "existing_runner_source_lines": existing_runner_source_lines,
        "source_policy_closed_ratio": source_policy_closed_ratio,
        "source_policy_rows_closed": source_policy_closed_rows,
        "source_policy_rows_total": source_policy_total_rows,
        "source_policy_execution_allowed_now": b4_execution_handoff.get(
            "source_policy_execution_allowed_now"
        ),
        "source_policy_execution_invoked": b4_execution_handoff.get(
            "source_policy_execution_invoked"
        ),
        "exact_b4_opt_in_required_for_execution": b4_execution_handoff.get(
            "exact_b4_opt_in_required_for_execution"
        ),
        "safe_action_ids": b4_execution_handoff.get("safe_action_ids"),
        "opt_in_action_ids": b4_execution_handoff.get("opt_in_action_ids"),
        "safe_next_actions_without_b4_opt_in": safe_next_actions_without_b4_opt_in,
        "opt_in_required_actions": opt_in_required_actions,
        "required_user_approval_statement": required_user_approval_statement,
        "guarded_execution_driver": b4_execution_handoff.get("guarded_execution_driver"),
        "runner_package_blocker_required_to_close_by_id": (
            runner_package_blocker_required_to_close_by_id
        ),
        "runner_package_blocker_safe_next_actions_by_id": (
            runner_package_blocker_safe_next_actions_by_id
        ),
        "runner_package_blocker_opt_in_required_actions_by_id": (
            runner_package_blocker_opt_in_required_actions_by_id
        ),
        "blocker_required_to_close_by_id": runner_package_blocker_required_to_close_by_id,
        "blocker_safe_next_actions_by_id": runner_package_blocker_safe_next_actions_by_id,
        "blocker_opt_in_required_actions_by_id": runner_package_blocker_opt_in_required_actions_by_id,
        "source_policy_execution_handoff": {
            "status": b4_execution_handoff.get("status"),
            "execution_authorized": b4_execution_handoff.get("execution_authorized"),
            "commands_not_run_by_handoff": b4_execution_handoff.get("commands_not_run_by_handoff"),
            "guarded_execution_driver": b4_execution_handoff.get("guarded_execution_driver"),
            "driver_requires_exact_approval": b4_execution_handoff.get("driver_requires_exact_approval"),
            "driver_does_not_authorize_execution": b4_execution_handoff.get(
                "driver_does_not_authorize_execution"
            ),
            "exact_required_user_approval_statement": required_user_approval_statement,
            "opt_in_required_command_count": b4_execution_handoff.get("opt_in_required_command_count"),
            "opt_in_required_mapped_external_rows": b4_execution_handoff.get(
                "opt_in_required_mapped_external_rows"
            ),
            "terminal_unable_to_reproduce_rows": b4_execution_handoff.get(
                "terminal_unable_to_reproduce_rows"
            ),
        },
        "full_source_policy_row_provenance_status": full_source_policy_row_provenance.get("status"),
        "full_source_policy_row_provenance_action_boundary": full_source_policy_row_provenance.get(
            "action_boundary"
        ),
        "full_source_policy_row_provenance_source_policy_execution_invoked": (
            full_source_policy_row_provenance.get("source_policy_execution_invoked")
        ),
        "full_source_policy_row_provenance_preflight": (
            f"{full_source_policy_row_provenance.get('provenance_preflight_complete_rows')}/"
            f"{full_source_policy_row_provenance.get('row_count')}"
        ),
        "full_source_policy_row_provenance_promotion_ready_rows": full_source_policy_row_provenance.get(
            "promotion_ready_rows"
        ),
        "reviewer_facing_python_file_limit": REVIEWER_PYTHON_FILE_LIMIT,
        "reviewer_facing_python_line_limit": REVIEWER_PYTHON_LINE_LIMIT,
        "current_candidate": {
            "status": minimal.get("status"),
            "submission_ready": minimal.get("submission_ready"),
            "file_count": minimal.get("candidate_file_count"),
            "python_file_count": candidate_python_files,
            "python_line_count": candidate_python_lines,
            "size_ok": candidate_size_ok,
            "replay_only": candidate_replay_only,
            "runner_centered": not candidate_replay_only,
        },
        "runner_package_boundary": {
            "local_accepted_rows_runner_centered": local_runner_centered_candidate_ready,
            "full_source_policy_runner_centered": runner_centered_ready,
            "b6_final_prose_pass_ready": b6_final_prose_ready,
            "b6_final_prose_pass_scope": "narrowed_claim_current_submission",
            "full_source_policy_b6_prose_ready": runner_centered_ready,
            "b6_closure_preflight_status": prose_preflight.get("status"),
            "b6_closure_allowed_now": prose_preflight.get("b6_closure_allowed_now"),
            "blocker_required_to_close_by_id": runner_package_blocker_required_to_close_by_id,
            "blocker_safe_next_actions_by_id": runner_package_blocker_safe_next_actions_by_id,
            "blocker_opt_in_required_actions_by_id": runner_package_blocker_opt_in_required_actions_by_id,
            "reason_b6_final_prose_deferred": (
                "The local accepted-row runner package is compact and executable. B6 final prose is closed "
                "under the narrowed current-claim policy; a full source-policy prose/package route still "
                "depends on source-policy row closure."
            ),
            "source_policy_rows_closed": source_policy_closed_rows,
            "source_policy_rows_total": source_policy_total_rows,
        },
        "runner_adapter_candidate": {
            "present": bool(runner_adapter),
            "schema": runner_adapter.get("schema"),
            "status": runner_adapter.get("status"),
            "runner_adapter_present": runner_adapter.get("runner_adapter_present"),
            "self_contained_simulation_runner": runner_adapter.get("self_contained_simulation_runner"),
            "external_v048_required_for_report_generation": runner_adapter.get(
                "external_v048_required_for_report_generation"
            ),
            "python_file_count": runner_adapter.get("candidate_python_file_count"),
            "python_line_count": runner_adapter.get("candidate_python_line_count"),
            "closed_loop_local_rows_replay_present": runner_adapter.get("closed_loop_local_rows_replay_present"),
            "closed_loop_local_rows_summary_present": runner_adapter.get("closed_loop_local_rows_summary_present"),
            "closed_loop_local_rows": runner_adapter.get("closed_loop_local_rows"),
            "closed_loop_local_models": runner_adapter.get("closed_loop_local_models"),
            "submission_ready": runner_adapter.get("submission_ready"),
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
            "submission_ready": b6_local_evidence.get("submission_ready"),
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
        "paper_matrix_scope": {
            "row_count": matrix.get("row_count"),
            "raw_row_count": matrix.get("raw_row_count"),
            "method_count": matrix.get("method_count"),
            "examples": matrix.get("examples"),
            "common_reference_order_wins": matrix.get("direct_nonlocal_velocity_order_wins"),
            "common_reference_order_comparisons": matrix.get("direct_nonlocal_velocity_order_comparisons"),
            "common_reference_error_wins": matrix.get("direct_nonlocal_velocity_error_wins"),
            "common_reference_error_comparisons": matrix.get("direct_nonlocal_velocity_error_comparisons"),
            "source_policy_external_superiority_allowed": matrix.get("source_policy_external_superiority_allowed"),
            "paper_direct_error_superiority_allowed": matrix.get("paper_direct_error_superiority_allowed"),
            "global_comparison_policy_passed": global_policy.get("passed_count") == global_policy.get("row_count"),
        },
        "source_policy_scope": {
            "local_dynamic_order_closed_examples": source_policy.get("local_dynamic_order_closed_examples"),
            "accepted_source_policy_dynamic_order_examples": source_policy.get(
                "accepted_source_policy_dynamic_order_examples"
            ),
            "source_policy_closed_rows": source_policy_closed_rows,
            "source_policy_total_rows": source_policy_total_rows,
        },
        "existing_runner_sources": source_candidates,
        "existing_runner_source_total_python_lines": existing_runner_source_lines,
        "existing_runner_boundary": {
            "can_be_primary_submission_code_without_extraction": False,
            "depends_on_v048_run_v048": True,
            "depends_on_external_sbel_reproducibility": True,
            "depends_on_public_code_paths": True,
            "contains_replay_and_audit_logic_mixed_with_runners": True,
        },
        "requirements": requirements,
        "next_extraction_target": [
            closed_loop_candidate.get("next_concrete_step")
            if closed_loop_candidate.get("runner_passed") is True
            else closed_loop_audit.get("next_concrete_step"),
            "separate a compact Gauss6/FullVA four-example runner from v048 provenance code",
            "make the runner regenerate the accepted 44-row common-reference matrix or explicitly narrower accepted subset",
            "keep source-policy external rows disabled until RA2021/HI2022/TFE policy rows close",
            "ship proof-boundary artifacts beside the runner instead of claiming proof closure",
        ],
    }

    OUT_JSON.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# CMAME Runner-Centered Reproducibility Audit",
        "",
        f"Status: **{audit['status']}**.",
        f"Runner-centered package ready: `{audit['runner_centered_package_ready']}`.",
        f"Local accepted-row runner-centered candidate ready: `{audit['local_runner_centered_candidate_ready']}`.",
        f"Full source-policy runner package ready: `{audit['full_source_policy_runner_package_ready']}`.",
        f"Submission ready: `{audit['submission_ready']}`.",
        "",
        "## Current Candidate",
        "",
        (
            f"- Python files/lines: `{candidate_python_files}/{candidate_python_lines}` "
            f"under limit `{REVIEWER_PYTHON_FILE_LIMIT}/{REVIEWER_PYTHON_LINE_LIMIT}`; "
            f"size-ok `{candidate_size_ok}`."
        ),
        f"- Replay-only: `{candidate_replay_only}`; runner-centered: `{not candidate_replay_only}`.",
        f"- Runner adapter present: `{runner_adapter.get('runner_adapter_present') is True}`; self-contained simulation runner: `{runner_adapter.get('self_contained_simulation_runner') is True}`.",
        f"- Runner adapter closed-loop replay outputs: `{runner_adapter.get('closed_loop_local_rows_summary_present') is True}`.",
        f"- B6 final prose ready under narrowed claim/full source-policy prose ready: `{b6_final_prose_ready}/{runner_centered_ready}`.",
        f"- B6 four-example local evidence runner: `{b6_local_evidence.get('b6_local_evidence_runner_passed')}`; rows `{b6_local_evidence.get('local_rows')}`; self-contained/replay-only `{b6_local_evidence.get('self_contained_examples')}/{b6_local_evidence.get('replay_only_examples')}`.",
        f"- Closed-loop local runner candidate: `{closed_loop_candidate.get('status')}`; rows `{closed_loop_candidate.get('closed_loop_local_rows')}`; compact `{closed_loop_candidate.get('candidate_python_line_limit_ok')}`.",
        f"- B6 closed-loop extraction audit: `{closed_loop_audit.get('status')}`; target symbols `{closed_loop_audit.get('target_symbol_count')}/{closed_loop_audit.get('target_symbol_lines')}`; ready `{closed_loop_audit.get('self_contained_runner_ready')}`.",
        f"- Source-policy rows closed: `{source_policy_closed_ratio}`.",
        f"- Source-policy execution allowed now/invoked/exact opt-in required: `{audit['source_policy_execution_allowed_now']}/{audit['source_policy_execution_invoked']}/{audit['exact_b4_opt_in_required_for_execution']}`.",
        f"- Safe action ids: `{audit['safe_action_ids']}`; opt-in action ids: `{audit['opt_in_action_ids']}`.",
        f"- Safe/opt-in action object counts: `{len(audit['safe_next_actions_without_b4_opt_in'])}/{len(audit['opt_in_required_actions'])}`.",
        f"- Runner package blocker required-to-close by id: `{runner_package_blocker_required_to_close_by_id}`.",
        f"- Runner package blocker safe next actions by id: `{runner_package_blocker_safe_next_actions_by_id}`.",
        f"- Runner package blocker opt-in required actions by id: `{runner_package_blocker_opt_in_required_actions_by_id}`.",
        f"- Source-policy handoff: `{audit['source_policy_execution_handoff']['status']}`; authorized/not-run `{audit['source_policy_execution_handoff']['execution_authorized']}/{audit['source_policy_execution_handoff']['commands_not_run_by_handoff']}`; driver `{audit['source_policy_execution_handoff']['guarded_execution_driver']}`.",
        f"- Row provenance preflight/promotion-ready: `{audit['full_source_policy_row_provenance_preflight']}/{audit['full_source_policy_row_provenance_promotion_ready_rows']}`.",
        f"- Direct PC2 proof gap closed: `{proof_ready}`.",
        "",
        "## Existing Runner Source Boundary",
        "",
        f"Existing v048 runner candidates total `{existing_runner_source_lines}` Python lines before extraction.",
        "",
        "| source | role | lines |",
        "|---|---|---:|",
    ]
    for item in source_candidates:
        lines.append(f"| `{item['path']}` | {item['role']} | `{item['python_lines']}` |")
    lines.extend(
        [
            "",
            "## Requirements",
            "",
            "| id | status | evidence |",
            "|---|---|---|",
        ]
    )
    for item in requirements:
        lines.append(f"| `{item['id']}` | `{item['status']}` | {item['evidence']} |")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("cmame_runner_centered_reproducibility_audit=written")
    print(f"runner_centered_package_ready={runner_centered_ready}")
    print(f"candidate_python_lines={candidate_python_lines}")
    print(f"existing_runner_source_lines={existing_runner_source_lines}")
    print(
        "source_policy_closed="
        f"{source_policy_closed_ratio}"
    )
    print(
        "source_policy_handoff="
        f"{audit['source_policy_execution_handoff']['status']}/"
        f"{audit['source_policy_execution_handoff']['execution_authorized']}/"
        f"{audit['source_policy_execution_handoff']['commands_not_run_by_handoff']}"
    )
    print(
        "source_policy_execution_allowed_now="
        f"{audit['source_policy_execution_allowed_now']}"
    )
    print(
        "source_policy_execution_invoked="
        f"{audit['source_policy_execution_invoked']}"
    )


if __name__ == "__main__":
    main()
