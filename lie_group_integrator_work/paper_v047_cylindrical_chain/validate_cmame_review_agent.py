#!/usr/bin/env python3
"""Read-only validator for the CMAME submission review agent report."""

from __future__ import annotations

import json
import hashlib
import math
import sys
from pathlib import Path


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
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


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def artifact_path(path: Path) -> str:
    try:
        rel = path.relative_to(PAPER)
    except ValueError:
        rel = path
    return rel.as_posix()


def artifact_snapshot(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    return {
        "path": artifact_path(path),
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
    }


def anchor_has_location(anchor: dict[str, object]) -> bool:
    return any(anchor.get(key) for key in ["json_pointer", "tex_label", "pdf_text_token"])


def python_inventory(root: Path) -> dict[str, object]:
    files = sorted(root.glob("*.py"))
    line_counts = {path.name: len(read_text(path).splitlines()) for path in files}
    prefix_counts = {
        "build": sum(1 for path in files if path.name.startswith("build_")),
        "validate": sum(1 for path in files if path.name.startswith("validate_")),
        "run": sum(1 for path in files if path.name.startswith("run_")),
        "merge": sum(1 for path in files if path.name.startswith("merge_")),
    }
    return {
        "file_count": len(files),
        "line_count": sum(line_counts.values()),
        "prefix_counts": prefix_counts,
    }


def main() -> int:
    checks = Checks()
    try:
        report = read_json(PAPER / "CMAME_REVIEW_AGENT_REPORT.json")
        report_md = read_text(PAPER / "CMAME_REVIEW_AGENT_REPORT.md")
        readiness_review = read_text(PAPER / "CMAME_SUBMISSION_READINESS_REVIEW.md")
        minimal_candidate = read_json(PAPER / "CMAME_MINIMAL_REPRODUCIBILITY_CANDIDATE_MANIFEST.json")
        runner_centered = read_json(PAPER / "CMAME_RUNNER_CENTERED_REPRODUCIBILITY_AUDIT.json")
        result_pack = read_json(PAPER / "PAPER_RESULT_PACK.json")
        numerical_matrix = read_json(PAPER / "PAPER_NUMERICAL_RESULT_MATRIX.json")
        result_traceability = read_json(PAPER / "RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.json")
        all_method_disposition = read_json(PAPER / "ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.json")
        all_examples_audit = read_json(PAPER / "ALL_EXAMPLES_RESULT_SANITY_AUDIT.json")
        recomputation_audit = read_json(PAPER / "COMMON_REFERENCE_ORDER_RECOMPUTATION_AUDIT.json")
        source_policy_diagnosis = read_json(PAPER / "EXTERNAL_BASELINE_SOURCE_POLICY_DIAGNOSIS.json")
        source_policy_triage = read_json(PAPER / "SOURCE_POLICY_CLOSURE_TRIAGE.json")
        source_policy_row_ledger = read_json(PAPER / "SOURCE_POLICY_ROW_CLOSURE_LEDGER.json")
        all_examples_source_policy = read_json(PAPER / "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.json")
        suite_disposition = read_json(PAPER / "EXTERNAL_SUITE_DISPOSITION_AUDIT.json")
        source_policy_closure_manifest = read_json(PAPER / "EXTERNAL_SOURCE_POLICY_CLOSURE_MANIFEST.json")
        external_case_reconciliation = read_json(PAPER / "EXTERNAL_CASE_EVIDENCE_RECONCILIATION.json")
        four_example_dashboard = read_json(PAPER / "FOUR_EXAMPLE_SOURCE_POLICY_DASHBOARD.json")
        hi2022_policy_decision = read_json(PAPER / "HI2022_POLICY_DECISION_AUDIT.json")
        vp2024_disposition = read_json(PAPER / "VP2024_CODE_PATH_DISPOSITION_AUDIT.json")
        vp2024_public_code_recheck = read_json(PAPER / "VP2024_PUBLIC_CODE_RECHECK_20260613.json")
        source_policy_public_code_refresh = read_json(PAPER / "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.json")
        source_policy_public_code_refresh_latest = read_json(PAPER / "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.json")
        external_suite_demotion = read_json(PAPER / "EXTERNAL_SUITE_DEMOTION_LEDGER.json")
        b2_remaining_work = read_json(PAPER / "B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.json")
        b4_work_precision_plan = read_json(PAPER / "B4_SOURCE_POLICY_WORK_PRECISION_EXECUTION_PLAN.json")
        b4_existing_promotion_audit = read_json(PAPER / "B4_EXISTING_ARTIFACT_PROMOTION_AUDIT.json")
        b4_post_execution_audit = read_json(PAPER / "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.json")
        ra_hi_post_execution_attempt_certificate = read_json(
            PAPER / "RA_HI_SOURCE_POLICY_POST_EXECUTION_ATTEMPT_CERTIFICATE.json"
        )
        ra_hi_source_policy_output_inventory = read_json(PAPER / "RA_HI_SOURCE_POLICY_OUTPUT_INVENTORY.json")
        ra_hi_source_policy_closeout_checklist = read_json(PAPER / "RA_HI_SOURCE_POLICY_CLOSEOUT_CHECKLIST.json")
        ra_hi_source_policy_promotion_blocker_matrix = read_json(
            PAPER / "RA_HI_SOURCE_POLICY_PROMOTION_BLOCKER_MATRIX.json"
        )
        b4_row_readiness_ledger = read_json(PAPER / "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.json")
        b4_execution_opt_in_packet = read_json(PAPER / "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json")
        b4_execution_handoff = read_json(PAPER / "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json")
        expected_command_traceability = b4_execution_handoff.get(
            "command_row_traceability", {}
        ).get("summary", {})
        external_superiority_claim_demotion = read_json(
            PAPER / "EXTERNAL_SUPERIORITY_CLAIM_DEMOTION_AUDIT.json"
        )
        ra2021_source_policy_audit = read_json(PAPER / "RA2021_SOURCE_POLICY_ROW_AUDIT.json")
        ra2021_source_identity_audit = read_json(PAPER / "RA2021_SOURCE_IDENTITY_AUDIT.json")
        hi2022_source_policy_audit = read_json(PAPER / "HI2022_SOURCE_POLICY_ROW_AUDIT.json")
        hi2022_t8_tolerance_repair_audit = read_json(PAPER / "HI2022_T8_TOLERANCE_REPAIR_AUDIT.json")
        hi2022_ra_half_double_repair_attempt_certificate = read_json(
            PAPER / "HI2022_RA_HALF_DOUBLE_REPAIR_ATTEMPT_CERTIFICATE.json"
        )
        tfe_source_policy_spec = read_json(PAPER / "TFE_SOURCE_POLICY_SPEC.json")
        tfe_source_policy_audit = read_json(PAPER / "TFE_SOURCE_POLICY_ROW_AUDIT.json")
        tfe_dae_runner_contract_gap_audit = read_json(PAPER / "TFE_DAE_RUNNER_CONTRACT_GAP_AUDIT.json")
        tfe_runner_contract_preflight = read_json(
            PAPER / "TFE_RUNNER_CONTRACT_PREFLIGHT_CERTIFICATE.json"
        )
        tfe_public_code_recheck = read_json(PAPER / "TFE_PUBLIC_CODE_RECHECK_20260613.json")
        tfe_self_reproduction_attempt_certificate = read_json(
            PAPER / "TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.json"
        )
        tfe_source_pendulum_model_audit = read_json(PAPER / "TFE_SOURCE_PENDULUM_MODEL_AUDIT.json")
        tfe_full_t10_coarse_candidate_summary = read_json(
            PAPER / "TFE_FULL_T10_COARSE_CANDIDATE_SUMMARY.json"
        )
        tfe_endpoint_sensitivity = read_json(PAPER / "TFE_ENDPOINT_POLICY_SENSITIVITY_AUDIT.json")
        objective_completion = read_json(PAPER / "OBJECTIVE_COMPLETION_AUDIT.json")
        full_source_policy_runner_archive_gap = read_json(
            PAPER / "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json"
        )
        proof_gate = read_json(PAPER / "CMAME_PROOF_CONTRACT_GATE.json")
        proof_style = read_json(PAPER / "CMAME_PROOF_STYLE_AUDIT.json")
        strict_proof_audit = read_json(PAPER / "CMAME_STRICT_PROOF_AUDIT.json")
        proof_closure = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
        newton_euler_symbolic_target = read_json(PAPER / "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.json")
        newton_euler_symbolic_defect_certificate = read_json(
            PAPER / "NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.json"
        )
        b1_symbolic_row_oracle_closure = read_json(
            PAPER / "B1_SYMBOLIC_ROW_ORACLE_CLOSURE_CERTIFICATE.json"
        )
        b1_ad_expanded_symbolic_oracle_closure = read_json(
            PAPER / "B1_AD_EXPANDED_SYMBOLIC_ORACLE_CLOSURE_CERTIFICATE.json"
        )
        newton_euler_ad_expanded_row_oracle = read_json(
            PAPER / "NEWTON_EULER_AD_EXPANDED_ROW_ORACLE_AUDIT.json"
        )
        proof_traceability = read_json(PAPER / "PROOF_CLAIM_TRACEABILITY_AUDIT.json")
        proof_remaining_work = read_json(PAPER / "PROOF_REMAINING_WORK_MANIFEST.json")
        solver_scale_audit = read_json(PAPER / "PROOF_SOLVER_SCALE_AUDIT.json")
        comparison_reconciliation = read_json(PAPER / "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.json")
        claim_hygiene = read_json(PAPER / "CMAME_CLAIM_HYGIENE_AUDIT.json")
        visual_legibility = read_json(PAPER / "CMAME_VISUAL_LEGIBILITY_AUDIT.json")
        figure_set = read_json(PAPER / "CMAME_FIGURE_SET_AUDIT.json")
        prose_residue = read_json(PAPER / "CMAME_PROSE_RESIDUE_AUDIT.json")
        submission_integrity = read_json(PAPER / "CMAME_SUBMISSION_INTEGRITY_AUDIT.json")
        submission_artifact_manifest = read_json(PAPER / "SUBMISSION_ARTIFACT_MANIFEST.json")
        reproducibility_manifest = read_json(PAPER / "CMAME_REPRODUCIBILITY_PACKAGE_MANIFEST.json")
        reference_metadata = read_json(PAPER / "REFERENCE_METADATA_AUDIT.json")
        pdf_style_review = read_json(PAPER / "CMAME_PDF_STYLE_REVIEW_AUDIT.json")
        blocker = read_json(PAPER / "CMAME_BLOCKER_CLOSURE_GATE.json")
        global_policy = read_json(
            PAPER / "../v048_cross_paper_same_test_benchmarks/results/global_comparison_policy_audit.json"
        )
    except Exception as exc:  # noqa: BLE001
        print(f"cmame review-agent validation: FAIL\n- {exc}")
        return 1

    open_blockers = [
        item["id"]
        for item in objective_completion.get("requirements", [])
        if item.get("blocking_for_goal_completion") is True and item.get("status") != "satisfied"
    ]
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
        f"{full_source_policy_runner_archive_gap.get('oc6_source_equivalent_reopen_readiness_latest_external_probe_date')}/"
        f"{full_source_policy_runner_archive_gap.get('oc6_source_equivalent_reopen_readiness_latest_external_probe_count')}/"
        f"{full_source_policy_runner_archive_gap.get('oc6_source_equivalent_reopen_readiness_latest_external_probe_positive_artifact_rows')}/"
        f"{full_source_policy_runner_archive_gap.get('oc6_source_equivalent_reopen_readiness_latest_external_probe_source_policy_rows_closed')}/"
        f"{full_source_policy_runner_archive_gap.get('oc6_source_equivalent_reopen_readiness_latest_external_probe_access_limited_count')}/"
        f"{full_source_policy_runner_archive_gap.get('oc6_source_equivalent_reopen_readiness_latest_external_probe_global_absence_proved')}/"
        f"{full_source_policy_runner_archive_gap.get('oc6_source_equivalent_reopen_readiness_latest_external_probe_reopen_triggered')}"
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
    expected_archive_safe_action_ids = [
        "rebuild_read_only_audit_chain",
        "rerun_read_only_validators",
        "keep_narrowed_archive_provenance_only",
        "monitor_reopen_conditions",
    ]
    expected_archive_opt_in_action_ids = ["authorized_b4_ra_hi_source_policy_execution"]
    manifest_narrowed_archive_boundary = submission_artifact_manifest.get("narrowed_archive_boundary", {})
    reproducibility_narrowed_archive_boundary = reproducibility_manifest.get(
        "narrowed_archive_boundary", {}
    )
    expected_submission_manifest_boundary = {
        "manifest_path": "SUBMISSION_ARTIFACT_MANIFEST.json",
        "reproducibility_manifest_path": "CMAME_REPRODUCIBILITY_PACKAGE_MANIFEST.json",
        "narrowed_archive_boundary": manifest_narrowed_archive_boundary,
        "narrowed_archive_boundary_matches_reproducibility_manifest": (
            manifest_narrowed_archive_boundary == reproducibility_narrowed_archive_boundary
        ),
        "narrowed_archive_boundary_status": submission_artifact_manifest.get(
            "narrowed_archive_boundary_status"
        ),
        "narrowed_archive_boundary_source_policy_closed_ratio": submission_artifact_manifest.get(
            "narrowed_archive_boundary_source_policy_closed_ratio"
        ),
        "narrowed_archive_boundary_current_archive_usable_as_full_source_policy_runner_archive": (
            submission_artifact_manifest.get(
                "narrowed_archive_boundary_current_archive_usable_as_full_source_policy_runner_archive"
            )
        ),
        "narrowed_archive_boundary_source_policy_execution_allowed_now": submission_artifact_manifest.get(
            "narrowed_archive_boundary_source_policy_execution_allowed_now"
        ),
        "narrowed_archive_boundary_exact_b4_opt_in_required_for_execution": (
            submission_artifact_manifest.get(
                "narrowed_archive_boundary_exact_b4_opt_in_required_for_execution"
            )
        ),
        "narrowed_archive_boundary_safe_action_ids": submission_artifact_manifest.get(
            "narrowed_archive_boundary_safe_action_ids", []
        ),
        "narrowed_archive_boundary_opt_in_action_ids": submission_artifact_manifest.get(
            "narrowed_archive_boundary_opt_in_action_ids", []
        ),
        "narrowed_archive_boundary_blocking_ids": manifest_narrowed_archive_boundary.get(
            "blocking_ids", []
        ),
        "narrowed_archive_boundary_blocker_status_by_id": manifest_narrowed_archive_boundary.get(
            "blocker_status_by_id", {}
        ),
        "narrowed_archive_boundary_blocker_next_actions_by_id": manifest_narrowed_archive_boundary.get(
            "blocker_next_actions_by_id", {}
        ),
        "narrowed_archive_boundary_blocker_required_to_close_by_id": manifest_narrowed_archive_boundary.get(
            "blocker_required_to_close_by_id", {}
        ),
        "narrowed_archive_boundary_blocker_safe_next_actions_by_id": manifest_narrowed_archive_boundary.get(
            "blocker_safe_next_actions_by_id", {}
        ),
        "narrowed_archive_boundary_blocker_opt_in_required_actions_by_id": manifest_narrowed_archive_boundary.get(
            "blocker_opt_in_required_actions_by_id", {}
        ),
        "narrowed_archive_boundary_scope": manifest_narrowed_archive_boundary.get("scope"),
    }
    cmame_blocker_gate_open = [item["id"] for item in blocker.get("blockers", []) if item.get("status") == "open"]
    checks.check(report.get("schema") == "cmame-submission-review-agent-report-v1", "review-agent schema changed")
    checks.check(report.get("read_only") is True, "review agent must be read-only")
    checks.check(report.get("submission_standard_met") is False, "review agent overclaimed global submission-ready")
    checks.check(
        report.get("submission_standard_scope") == "global_submission_standard",
        "review agent submission standard scope changed",
    )
    checks.check(
        report.get("review_scope") == "global_submission_standard_review",
        "review agent must report a global review scope",
    )
    checks.check(
        report.get("top_level_review_decision_scope") == "global",
        "review agent top-level decision scope must stay global",
    )
    checks.check(
        report.get("global_submission_standard_met") is False,
        "review agent overclaimed global submission standard",
    )
    expected_input_artifact_paths = [
        "main_cmame.tex",
        "main_cmame.txt",
        "cmame_submission_flat/main_cmame_submission.tex",
        "cmame_submission_flat/main_cmame_submission.txt",
        "CMAME_SUBMISSION_READINESS_REVIEW.md",
        "OBJECTIVE_COMPLETION_AUDIT.json",
        "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json",
        "CMAME_STRICT_PROOF_AUDIT.json",
        "PROOF_CLAIM_TRACEABILITY_AUDIT.json",
        "RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.json",
        "PAPER_RESULT_PACK.json",
        "PAPER_NUMERICAL_RESULT_MATRIX.json",
        "FOUR_EXAMPLE_SOURCE_POLICY_DASHBOARD.json",
        "SOURCE_POLICY_ROW_CLOSURE_LEDGER.json",
        "TFE_SOURCE_POLICY_ROW_AUDIT.json",
        "TFE_RUNNER_CONTRACT_PREFLIGHT_CERTIFICATE.json",
        "TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.json",
        "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.json",
        "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.json",
        "RA_HI_SOURCE_POLICY_POST_EXECUTION_ATTEMPT_CERTIFICATE.json",
        "RA_HI_SOURCE_POLICY_OUTPUT_INVENTORY.json",
        "RA_HI_SOURCE_POLICY_CLOSEOUT_CHECKLIST.json",
        "RA_HI_SOURCE_POLICY_PROMOTION_BLOCKER_MATRIX.json",
        "HI2022_RA_HALF_DOUBLE_REPAIR_ATTEMPT_CERTIFICATE.json",
        "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.json",
        "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json",
        "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json",
        "CMAME_MINIMAL_REPRODUCIBILITY_CANDIDATE_MANIFEST.json",
        "CMAME_RUNNER_CENTERED_REPRODUCIBILITY_AUDIT.json",
        "CMAME_NARROWED_REPRO_CODE_ARCHIVE_MANIFEST.json",
        "CMAME_PDF_STYLE_REVIEW_AUDIT.json",
        "CMAME_SUBMISSION_INTEGRITY_AUDIT.json",
        "REFERENCE_METADATA_AUDIT.json",
        "SUBMISSION_ARTIFACT_MANIFEST.json",
        "CMAME_REPRODUCIBILITY_PACKAGE_MANIFEST.json",
        "../v048_cross_paper_same_test_benchmarks/results/global_comparison_policy_audit.json",
    ]
    expected_input_artifacts = [
        artifact_snapshot(manuscript_path(relative_path))
        for relative_path in expected_input_artifact_paths
    ]
    input_artifact_provenance = report.get("input_artifact_provenance", {})
    checks.check(
        input_artifact_provenance.get("hash_algorithm") == "sha256"
        and input_artifact_provenance.get("timestamp_policy")
        == "deterministic_no_wall_clock_timestamp",
        "review-agent input artifact provenance policy missing or stale",
    )
    checks.check(
        input_artifact_provenance.get("input_artifacts_read") == expected_input_artifacts,
        "review-agent input artifact hashes missing or stale",
    )
    stale_token_scan = report.get("stale_token_scan", {})
    checks.check(
        stale_token_scan.get("objective_oc9_stale_next_to_close_present") is False,
        "review-agent stale scan still sees stale OC9 next_to_close text",
    )
    checks.check(
        stale_token_scan.get("readiness_review_declares_historical_context") is True
        and stale_token_scan.get("readiness_review_delegates_current_global_decision") is True
        and "Historical decision before narrowed-claim closure" in readiness_review
        and "current package-facing global decision is recorded" in readiness_review,
        "review-agent stale scan/readiness-review delegation missing",
    )
    opt_in_boundary = report.get("opt_in_boundary", {})
    checks.check(
        opt_in_boundary.get("packet_path") == "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json"
        and opt_in_boundary.get("exact_required_phrase")
        == "I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json."
        and opt_in_boundary.get("packet_does_not_authorize_execution") is True
        and opt_in_boundary.get("explicit_user_opt_in_required_before_any_command") is True,
        "review-agent B4 opt-in boundary missing or stale",
    )
    global_review_dimensions = report.get("global_review_dimensions", [])
    expected_global_review_dimensions = [
        "method_contribution",
        "proof_and_theorem",
        "numerical_validation",
        "comparison_and_source_policy",
        "reproducibility_and_code_package",
        "manuscript_style_and_integrity",
    ]
    checks.check(
        isinstance(global_review_dimensions, list)
        and [item.get("dimension") for item in global_review_dimensions] == expected_global_review_dimensions,
        "review agent global review dimensions missing or stale",
    )
    for item in global_review_dimensions:
        checks.check(bool(item.get("verdict")), "global review dimension missing verdict")
        checks.check(bool(item.get("global_effect")), "global review dimension missing global effect")
        checks.check(bool(item.get("blocking_boundary")), "global review dimension missing blocking boundary")
        evidence = item.get("evidence")
        checks.check(isinstance(evidence, list) and bool(evidence), "global review dimension missing evidence")
        anchors = item.get("artifact_anchors")
        checks.check(
            isinstance(anchors, list)
            and len(anchors) >= 2
            and all(
                isinstance(anchor, dict)
                and bool(anchor.get("path"))
                and bool(anchor.get("quoted_token"))
                and bool(anchor.get("interpretation"))
                and anchor_has_location(anchor)
                for anchor in anchors
            ),
            "global review dimension missing artifact anchors",
        )
    expected_global_review_dimension_evidence = {
        item.get("dimension"): item.get("evidence")
        for item in global_review_dimensions
        if isinstance(item, dict)
    }
    checks.check(
        report.get("global_review_dimension_evidence") == expected_global_review_dimension_evidence,
        "global review dimension evidence mirror missing or stale",
    )
    expected_global_review_dimension_artifact_anchors = {
        item.get("dimension"): item.get("artifact_anchors")
        for item in global_review_dimensions
        if isinstance(item, dict)
    }
    checks.check(
        report.get("global_review_dimension_artifact_anchors")
        == expected_global_review_dimension_artifact_anchors,
        "global review dimension artifact-anchor mirror missing or stale",
    )
    global_submission_decision_basis = report.get("global_submission_decision_basis", {})
    checks.check(
        isinstance(global_submission_decision_basis, dict)
        and set(global_submission_decision_basis) == set(expected_global_review_dimensions),
        "global submission decision basis missing or stale",
    )
    for item in global_review_dimensions:
        basis = global_submission_decision_basis.get(item.get("dimension"), {})
        checks.check(
            basis.get("verdict") == item.get("verdict")
            and basis.get("global_effect") == item.get("global_effect")
            and basis.get("blocking_boundary") == item.get("blocking_boundary")
            and basis.get("artifact_anchors") == item.get("artifact_anchors"),
            "global submission decision basis does not mirror dimension evidence",
        )
    expected_dimension_anchor_paths = {
        "method_contribution": ["main_cmame.tex", "RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.json"],
        "proof_and_theorem": [
            "main_cmame.tex",
            "PROOF_CLAIM_TRACEABILITY_AUDIT.json",
            "CMAME_STRICT_PROOF_AUDIT.json",
        ],
        "numerical_validation": [
            "PAPER_NUMERICAL_RESULT_MATRIX.json",
            "FOUR_EXAMPLE_SOURCE_POLICY_DASHBOARD.json",
        ],
        "comparison_and_source_policy": [
            "SOURCE_POLICY_ROW_CLOSURE_LEDGER.json",
            "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.json",
        ],
        "reproducibility_and_code_package": [
            "CMAME_MINIMAL_REPRODUCIBILITY_CANDIDATE_MANIFEST.json",
            "CMAME_RUNNER_CENTERED_REPRODUCIBILITY_AUDIT.json",
        ],
        "manuscript_style_and_integrity": [
            "CMAME_PDF_STYLE_REVIEW_AUDIT.json",
            "CMAME_SUBMISSION_INTEGRITY_AUDIT.json",
        ],
    }
    for item in global_review_dimensions:
        dimension = item.get("dimension")
        paths = [anchor.get("path") for anchor in item.get("artifact_anchors", [])]
        checks.check(
            paths == expected_dimension_anchor_paths.get(dimension),
            f"global review dimension anchors changed for {dimension}",
        )
    global_review_verdicts = {
        item.get("dimension"): item.get("verdict") for item in global_review_dimensions if isinstance(item, dict)
    }
    checks.check(
        global_review_verdicts.get("proof_and_theorem") == "conditional_pass_global_boundaries_retained",
        "proof/theorem global review verdict changed",
    )
    checks.check(
        global_review_verdicts.get("comparison_and_source_policy") == "blocked_for_global_submission",
        "comparison/source-policy global review verdict changed",
    )
    checks.check(
        global_review_verdicts.get("reproducibility_and_code_package") == "blocked_for_global_submission",
        "repro/code-package global review verdict changed",
    )
    global_reviewer_assessment = report.get("global_reviewer_assessment", {})
    checks.check(
        global_reviewer_assessment.get("top_level_verdict") == "do_not_submit_global",
        "global reviewer assessment must lead with the global verdict",
    )
    checks.check(
        "Gauss6/FullVA method and strict conditional proof are the paper core"
        in global_reviewer_assessment.get("primary_paper_line", ""),
        "global reviewer assessment missing primary paper line",
    )
    checks.check(
        global_reviewer_assessment.get("narrowed_subcheck_is_not_global_review") is True,
        "global reviewer assessment must keep narrowed subcheck subsidiary",
    )
    expected_claim_statuses = [
        "main_claim_strongest",
        "strong_conditional_claim_retained",
        "accepted_with_scope",
        "appendix_or_diagnostic_only",
        "boundary_and_diagnostic_only",
    ]
    checks.check(
        [
            item.get("reviewer_status")
            for item in global_reviewer_assessment.get("claim_hierarchy", [])
            if isinstance(item, dict)
        ]
        == expected_claim_statuses,
        "global reviewer claim hierarchy missing or stale",
    )
    checks.check(
        global_reviewer_assessment.get("evidence_tiering")
        == [
            "dynamic-order rows support the order claim",
            "mechanism-coverage rows support constraint and reaction consistency",
            "diagnostic rows expose boundary, source-policy, and package gaps",
        ],
        "global evidence tiering changed",
    )
    checks.check(
        global_reviewer_assessment.get("global_blocker_priority")
        == [
            "OC4 source-policy reproduction rows",
            "OC6 original TFE source-policy runner",
            "OC12 full source-policy runner package",
        ],
        "global blocker priority changed",
    )
    checks.check(
        "lead with global submission readiness and evidence hierarchy"
        in global_reviewer_assessment.get("global_review_rule", ""),
        "global reviewer assessment missing global review rule",
    )
    global_substantive_findings = report.get("global_substantive_findings", [])
    expected_global_finding_ids = ["GF1", "GF2", "GF3", "GF4", "GF5"]
    checks.check(
        isinstance(global_substantive_findings, list)
        and [item.get("id") for item in global_substantive_findings if isinstance(item, dict)]
        == expected_global_finding_ids,
        "global substantive findings missing or stale",
    )
    global_finding_severities = {
        item.get("id"): item.get("severity") for item in global_substantive_findings if isinstance(item, dict)
    }
    checks.check(
        global_finding_severities
        == {
            "GF1": "strength",
            "GF2": "conditional_pass",
            "GF3": "scope_boundary",
            "GF4": "global_blocker",
            "GF5": "blocking",
        },
        "global substantive finding severities changed",
    )
    gf2 = next((item for item in global_substantive_findings if item.get("id") == "GF2"), {})
    checks.check(
        "route-exclusive same-branch certificates" in gf2.get("global_review_judgment", "")
        and "cannot be mixed to lower constants, remove P6, or prove a P7 residual-to-error transfer theorem"
        in gf2.get("global_review_judgment", "")
        and "theorem statement itself consumes only one residual-value certificate"
        in gf2.get("global_review_judgment", "")
        and "same-tuple 132-row residual-value bound"
        in gf2.get("global_review_judgment", "")
        and "route-exclusivity boundary" in gf2.get("required_action", "")
        and "theorem-level residual-certificate exclusivity"
        in gf2.get("required_action", ""),
        "GF2 must carry route-exclusivity and theorem residual-certificate proof boundaries",
    )
    for item in global_substantive_findings:
        checks.check(
            bool(item.get("finding"))
            and bool(item.get("global_review_judgment"))
            and bool(item.get("required_action")),
            "global substantive finding missing review judgment or action",
        )
        anchors = item.get("artifact_anchors")
        checks.check(
            isinstance(item.get("blocking_ids"), list)
            and bool(item.get("claim_scope"))
            and bool(item.get("safe_disposition"))
            and isinstance(anchors, list)
            and bool(anchors)
            and all(
                isinstance(anchor, dict)
                and bool(anchor.get("path"))
                and bool(anchor.get("quoted_token"))
                and bool(anchor.get("interpretation"))
                and anchor_has_location(anchor)
                for anchor in anchors
            ),
            "global substantive finding missing scope/blocker/artifact-anchor fields",
        )
    expected_global_finding_blockers = {
        "GF1": [],
        "GF2": [
            "theorem_level_eta_h_solver_policy_evidence",
            "closed_residual_to_error_theorem_for_mechanism_rows",
        ],
        "GF3": ["source_policy_dynamic_order_examples_0_of_4"],
        "GF4": ["OC4", "OC6", "source_policy_rows_0_of_40"],
        "GF5": ["OC4", "OC6", "OC12"],
    }
    checks.check(
        {
            item.get("id"): item.get("blocking_ids")
            for item in global_substantive_findings
            if isinstance(item, dict)
        }
        == expected_global_finding_blockers,
        "global substantive finding blocker IDs missing or stale",
    )
    expected_global_finding_safe_dispositions = {
        "GF1": "lead_the_paper_with_method_contribution",
        "GF2": "retain_detailed_proof_without_unconditional_order_claim",
        "GF3": "present_closed_loop_rows_as_coverage_not_source_policy_order",
        "GF4": "demote_TFE_and_external_comparisons_to_diagnostic_or_appendix_roles",
        "GF5": "do_not_submit_global",
    }
    checks.check(
        {
            item.get("id"): item.get("safe_disposition")
            for item in global_substantive_findings
            if isinstance(item, dict)
        }
        == expected_global_finding_safe_dispositions,
        "global substantive finding safe dispositions missing or stale",
    )
    gf2 = global_substantive_findings[1] if len(global_substantive_findings) > 1 else {}
    checks.check(
        "P1, P2, and P3 are retained theorem interfaces; P6 is a separate solver-scale interface; P4's binding convention is retained while its 96-row certificate is proved"
        in gf2.get("global_review_judgment", "")
        and "P7 is an output nonclaim boundary" in gf2.get("global_review_judgment", ""),
        "global proof finding must enforce the categorical P-partition",
    )
    gf5 = global_substantive_findings[4] if len(global_substantive_findings) > 4 else {}
    checks.check(
        "OC4, OC6, and OC12 dominate" in gf5.get("global_review_judgment", ""),
        "global submission-readiness finding must name OC4/OC6/OC12 dominance",
    )
    global_review_findings = report.get("global_review_findings", [])
    checks.check(
        report.get("findings_scope") == "whole_paper_cmame_submission_standard"
        and report.get("findings_role") == "top_level_machine_readable_global_review_not_narrowed_blocker_gate",
        "machine-readable findings must be scoped to the whole-paper global review",
    )
    checks.check(
        report.get("findings") == global_review_findings,
        "generic findings field must mirror global_review_findings",
    )
    checks.check(
        isinstance(global_review_findings, list)
        and len(global_review_findings) == len(expected_global_finding_ids) + len(open_blockers),
        "global review findings must include substantive findings plus global blockers",
    )
    checks.check(
        [item.get("id") for item in global_review_findings[: len(expected_global_finding_ids)]]
        == expected_global_finding_ids,
        "global review findings must lead with GF1-GF5",
    )
    checks.check(
        [item.get("id") for item in global_review_findings[len(expected_global_finding_ids) :]]
        == open_blockers,
        "global review findings must include OC4/OC6/OC12 blocker findings",
    )
    checks.check(
        all(
            isinstance(item, dict)
            and item.get("scope") == "whole_paper_cmame_submission_standard"
            and bool(item.get("finding"))
            and bool(item.get("judgment"))
            and bool(item.get("required_action"))
            and item.get("safe_disposition") == (
                "do_not_submit_global"
                if item.get("type") == "global_blocking_requirement"
                else item.get("safe_disposition")
            )
            and isinstance(item.get("artifact_anchors"), list)
            and bool(item.get("artifact_anchors"))
            for item in global_review_findings
        ),
        "each machine-readable global finding must carry scope, judgment, action, disposition, and anchors",
    )
    checks.check(
        {
            item.get("id"): item.get("type")
            for item in global_review_findings
            if item.get("id") in {"OC4", "OC6", "OC12"}
        }
        == {
            "OC4": "global_blocking_requirement",
            "OC6": "global_blocking_requirement",
            "OC12": "global_blocking_requirement",
        },
        "OC4/OC6/OC12 must be explicit global blocking findings",
    )
    global_editorial_decision = report.get("global_editorial_decision", {})
    checks.check(
        global_editorial_decision.get("scope") == "whole_paper_cmame_submission_standard",
        "global editorial decision must cover the whole paper",
    )
    checks.check(
        global_editorial_decision.get("decision") == report.get("decision") == "do_not_submit_global",
        "global editorial decision must match the top-level global decision",
    )
    checks.check(
        global_editorial_decision.get("ranked_global_blockers") == ["OC4", "OC6", "OC12"],
        "global editorial decision blocker ranking changed",
    )
    checks.check(
        global_editorial_decision.get("non_overriding_subcheck")
        == "narrowed_claim_blocker_gate_pass_does_not_override_global_decision",
        "global editorial decision must keep narrowed blocker gate non-overriding",
    )
    editorial_basis = global_editorial_decision.get("review_basis")
    checks.check(
        isinstance(editorial_basis, list)
        and len(editorial_basis) == 3
        and "reviewed together" in editorial_basis[0]
        and "dominate" in editorial_basis[1]
        and "subsidiary bounded subcheck" in editorial_basis[2],
        "global editorial decision review basis missing or stale",
    )
    checks.check(
        "do not submit globally" in global_editorial_decision.get("safe_current_disposition", ""),
        "global editorial decision safe disposition missing",
    )
    checks.check(
        report.get("global_review_frame")
        == "whole_paper_cmame_submission_standard_not_local_artifact_checklist",
        "global review frame missing or stale",
    )
    global_blocker_hierarchy = report.get("global_blocker_hierarchy", [])
    checks.check(
        isinstance(global_blocker_hierarchy, list)
        and [item.get("rank") for item in global_blocker_hierarchy if isinstance(item, dict)] == [1, 2, 3, 4],
        "global blocker hierarchy ranks missing or stale",
    )
    rank1 = global_blocker_hierarchy[0] if isinstance(global_blocker_hierarchy, list) and global_blocker_hierarchy else {}
    checks.check(
        rank1.get("class") == "global_submission_blockers"
        and rank1.get("ids") == ["OC4", "OC6", "OC12"]
        and rank1.get("effect") == "do_not_submit_global"
        and rank1.get("dominates_narrowed_claim") is True,
        "global blocker hierarchy rank 1 must be OC4/OC6/OC12",
    )
    checks.check(
        all(isinstance(item, dict) and bool(item.get("effect")) for item in global_blocker_hierarchy),
        "every global blocker hierarchy item must record an effect",
    )
    checks.check(
        global_blocker_hierarchy[1].get("ids")
        == [
            "theorem_level_eta_h_solver_policy_evidence",
            "closed_residual_to_error_theorem_for_mechanism_rows",
        ],
        "retained theorem boundary hierarchy changed",
    )
    checks.check(
        global_blocker_hierarchy[2].get("ids")
        == ["source_policy_dynamic_order_examples_0_of_4", "source_policy_rows_0_of_40"],
        "partial numerical scope hierarchy changed",
    )
    checks.check(
        global_blocker_hierarchy[3].get("ids") == ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8"],
        "non-overriding local pass hierarchy changed",
    )
    semantic_invariants = report.get("global_review_semantic_invariants", {})
    source_policy_scope = runner_centered.get("source_policy_scope", {})
    evidence_summary = report.get("evidence_summary", {})
    external_checks = report.get("external_checks", {})
    checks.check(
        semantic_invariants.get("contract") == "whole_paper_global_review_contract",
        "global review semantic contract missing",
    )
    checks.check(
        semantic_invariants.get("top_level_decision_matches_objective_completion") is True,
        "global review decision/objective-completion invariant failed",
    )
    checks.check(
        semantic_invariants.get("decision_is_do_not_submit_global_iff_objective_incomplete") is True,
        "global review decision must be derived from incomplete objective status",
    )
    checks.check(
        semantic_invariants.get("all_blocking_objective_requirements_reported") is True
        and semantic_invariants.get("blocking_objective_requirement_ids") == open_blockers,
        "global review must report every blocking objective requirement",
    )
    checks.check(
        semantic_invariants.get("global_findings_include_all_blocking_requirements") is True,
        "global findings must include every blocking objective requirement",
    )
    checks.check(
        semantic_invariants.get("narrowed_claim_does_not_override_global_decision") is True,
        "narrowed-claim pass must remain non-overriding",
    )
    checks.check(
        semantic_invariants.get("b4_opt_in_boundary_retained") is True,
        "B4 opt-in boundary invariant missing",
    )
    checks.check(
        semantic_invariants.get("run_v047_invoked") is False
        and semantic_invariants.get("heavy_run_invoked") is False,
        "review-agent semantic invariants detected forbidden/heavy execution",
    )
    checks.check(
        semantic_invariants.get("source_policy_rows_closed")
        == source_policy_scope.get("source_policy_closed_rows")
        == 0
        and semantic_invariants.get("source_policy_total_rows")
        == source_policy_scope.get("source_policy_total_rows")
        == 40
        and semantic_invariants.get("source_policy_rows_closed_text") == "0/40",
        "global review source-policy row invariant stale",
    )
    checks.check(
        semantic_invariants.get("accepted_source_policy_dynamic_order_examples")
        == source_policy_scope.get("accepted_source_policy_dynamic_order_examples")
        == 0
        and semantic_invariants.get("accepted_source_policy_dynamic_order_examples_text") == "0/4",
        "global review dynamic-order source-policy invariant stale",
    )
    checks.check(
        semantic_invariants.get("full_source_policy_runner_package_ready")
        == runner_centered.get("full_source_policy_runner_package_ready")
        is False,
        "global review source-policy runner package invariant stale",
    )
    checks.check(
        semantic_invariants.get("global_comparison_policy_artifact_included") is True
        and global_policy.get("schema") == "global-comparison-policy-audit-v1"
        and global_policy.get("paper_direct_error_superiority_claim_allowed") is False,
        "global comparison-policy input must be included in global review contract",
    )
    checks.check(
        report.get("submission_manifest_boundary") == expected_submission_manifest_boundary,
        "review-agent submission manifest boundary mirror missing or stale",
    )
    checks.check(
        report.get("source_policy_closed_ratio")
        == expected_submission_manifest_boundary[
            "narrowed_archive_boundary_source_policy_closed_ratio"
        ]
        == "0/40"
        and report.get("source_policy_execution_allowed_now")
        == expected_submission_manifest_boundary[
            "narrowed_archive_boundary_source_policy_execution_allowed_now"
        ]
        is False
        and report.get("source_policy_execution_invoked")
        == external_checks.get("oc12_archive_source_policy_execution_invoked")
        is False
        and report.get("current_archive_usable_as_full_source_policy_runner_archive")
        == expected_submission_manifest_boundary[
            "narrowed_archive_boundary_current_archive_usable_as_full_source_policy_runner_archive"
        ]
        is False
        and report.get("exact_b4_opt_in_required_for_execution")
        == expected_submission_manifest_boundary[
            "narrowed_archive_boundary_exact_b4_opt_in_required_for_execution"
        ]
        is True
        and report.get("scope")
        == expected_submission_manifest_boundary["narrowed_archive_boundary_scope"]
        == "narrowed_claim_only"
        and report.get("narrowed_archive_boundary_status")
        == expected_submission_manifest_boundary["narrowed_archive_boundary_status"]
        == "narrowed_archive_ready_not_full_source_policy_runner_archive"
        and report.get("narrowed_archive_boundary_matches_reproducibility_manifest")
        == expected_submission_manifest_boundary[
            "narrowed_archive_boundary_matches_reproducibility_manifest"
        ]
        is True,
        "review-agent top-level source-policy boundary aliases missing or stale",
    )
    checks.check(
        report.get("safe_action_ids")
        == expected_submission_manifest_boundary["narrowed_archive_boundary_safe_action_ids"]
        == expected_archive_safe_action_ids
        and report.get("opt_in_action_ids")
        == expected_submission_manifest_boundary["narrowed_archive_boundary_opt_in_action_ids"]
        == expected_archive_opt_in_action_ids,
        "review-agent top-level source-policy action aliases missing or stale",
    )
    checks.check(
        report.get("oc12_archive_tfe_preflight")
        == evidence_summary.get("oc12_archive_tfe_preflight")
        == oc12_archive_tfe_preflight,
        "review-agent top-level OC12 TFE preflight alias stale",
    )
    checks.check(
        report.get("oc12_archive_action_boundary")
        == external_checks.get("oc12_archive_action_boundary")
        == expected_archive_action_boundary
        and report.get("oc12_archive_action_boundary_summary")
        == evidence_summary.get("oc12_archive_action_boundary")
        == oc12_archive_action_boundary,
        "review-agent top-level OC12 action boundary alias stale",
    )
    checks.check(
        report.get("oc12_archive_safe_action_ids")
        == external_checks.get("oc12_archive_safe_action_ids")
        == expected_archive_safe_action_ids
        and report.get("oc12_archive_opt_in_action_ids")
        == external_checks.get("oc12_archive_opt_in_action_ids")
        == expected_archive_opt_in_action_ids,
        "review-agent top-level OC12 action id aliases stale",
    )
    checks.check(
        report.get("oc12_archive_source_policy_execution_allowed_now")
        == external_checks.get("oc12_archive_source_policy_execution_allowed_now")
        is False
        and report.get("oc12_archive_source_policy_execution_invoked")
        == external_checks.get("oc12_archive_source_policy_execution_invoked")
        is False
        and report.get("oc12_archive_exact_b4_opt_in_required_for_execution")
        == external_checks.get("oc12_archive_exact_b4_opt_in_required_for_execution")
        is True
        and report.get("oc12_archive_opt_in_required_command_count")
        == external_checks.get("oc12_archive_opt_in_required_command_count")
        == 13
        and report.get("oc12_archive_opt_in_required_mapped_external_rows")
        == external_checks.get("oc12_archive_opt_in_required_mapped_external_rows")
        == 20,
        "review-agent top-level OC12 execution aliases stale",
    )
    checks.check(
        manifest_narrowed_archive_boundary == reproducibility_narrowed_archive_boundary
        and manifest_narrowed_archive_boundary.get("schema") == "narrowed-repro-code-archive-boundary-v1"
        and manifest_narrowed_archive_boundary.get("status")
        == "narrowed_archive_ready_not_full_source_policy_runner_archive"
        and manifest_narrowed_archive_boundary.get("scope") == "narrowed_claim_only"
        and manifest_narrowed_archive_boundary.get("blocking_ids") == open_blockers
        and manifest_narrowed_archive_boundary.get("blocker_status_by_id")
        == objective_completion.get("blocker_status_by_id")
        and manifest_narrowed_archive_boundary.get("blocker_required_to_close_by_id")
        == objective_completion.get("blocker_required_to_close_by_id")
        and manifest_narrowed_archive_boundary.get("blocker_safe_next_actions_by_id")
        == objective_completion.get("blocker_safe_next_actions_by_id")
        and manifest_narrowed_archive_boundary.get("blocker_opt_in_required_actions_by_id")
        == objective_completion.get("blocker_opt_in_required_actions_by_id")
        and manifest_narrowed_archive_boundary.get("source_policy_closed_ratio") == "0/40",
        "submission manifest narrowed boundary no longer matches reproducibility/objective boundary",
    )
    checks.check(
        expected_submission_manifest_boundary[
            "narrowed_archive_boundary_matches_reproducibility_manifest"
        ]
        is True
        and expected_submission_manifest_boundary["narrowed_archive_boundary_status"]
        == manifest_narrowed_archive_boundary.get("status")
        and expected_submission_manifest_boundary["narrowed_archive_boundary_source_policy_closed_ratio"]
        == manifest_narrowed_archive_boundary.get("source_policy_closed_ratio")
        and expected_submission_manifest_boundary[
            "narrowed_archive_boundary_current_archive_usable_as_full_source_policy_runner_archive"
        ]
        is False
        and expected_submission_manifest_boundary[
            "narrowed_archive_boundary_source_policy_execution_allowed_now"
        ]
        is False
        and expected_submission_manifest_boundary[
            "narrowed_archive_boundary_exact_b4_opt_in_required_for_execution"
        ]
        is True
        and expected_submission_manifest_boundary["narrowed_archive_boundary_safe_action_ids"]
        == expected_archive_safe_action_ids
        and expected_submission_manifest_boundary["narrowed_archive_boundary_opt_in_action_ids"]
        == expected_archive_opt_in_action_ids,
        "submission manifest narrowed boundary aliases changed",
    )
    checks.check(
        expected_submission_manifest_boundary["narrowed_archive_boundary_blocker_required_to_close_by_id"]
        == objective_completion.get("blocker_required_to_close_by_id")
        and expected_submission_manifest_boundary["narrowed_archive_boundary_blocker_safe_next_actions_by_id"]
        == objective_completion.get("blocker_safe_next_actions_by_id")
        and expected_submission_manifest_boundary["narrowed_archive_boundary_blocker_opt_in_required_actions_by_id"]
        == objective_completion.get("blocker_opt_in_required_actions_by_id"),
        "submission manifest narrowed boundary closure/action maps changed",
    )
    checks.check(
        semantic_invariants.get(
            "submission_manifest_narrowed_boundary_matches_reproducibility_manifest"
        )
        is True
        and semantic_invariants.get("submission_manifest_narrowed_boundary_status")
        == "narrowed_archive_ready_not_full_source_policy_runner_archive"
        and semantic_invariants.get(
            "submission_manifest_narrowed_boundary_source_policy_closed_ratio"
        )
        == "0/40"
        and semantic_invariants.get("submission_manifest_narrowed_boundary_full_archive_usable")
        is False
        and semantic_invariants.get(
            "submission_manifest_narrowed_boundary_source_policy_execution_allowed_now"
        )
        is False
        and semantic_invariants.get(
            "submission_manifest_narrowed_boundary_exact_b4_opt_in_required_for_execution"
        )
        is True,
        "global semantic invariants lost submission-manifest narrowed boundary",
    )
    checks.check(
        evidence_summary.get("objective_status") == objective_completion.get("status")
        and evidence_summary.get("objective_complete") is False
        and evidence_summary.get("submission_ready") is False
        and evidence_summary.get("open_blocker_count") == 3
        and evidence_summary.get("open_blocker_ids") == open_blockers,
        "review evidence summary objective/blocker aliases stale",
    )
    checks.check(
        evidence_summary.get("objective_blocker_required_to_close_by_id")
        == objective_completion.get("blocker_required_to_close_by_id")
        and evidence_summary.get("objective_blocker_safe_next_actions_by_id")
        == objective_completion.get("blocker_safe_next_actions_by_id")
        and evidence_summary.get("objective_blocker_opt_in_required_actions_by_id")
        == objective_completion.get("blocker_opt_in_required_actions_by_id"),
        "review evidence summary objective closure/action maps stale",
    )
    checks.check(
        evidence_summary.get("source_policy_apples_to_apples_external") == "0/40"
        and evidence_summary.get("accepted_source_policy_dynamic_order_examples") == "0/4"
        and evidence_summary.get("tfe_runner_contract_preflight")
        == "contract_entrypoints_callable_candidate_backed_source_policy_open/3/3/3/0/4"
        and evidence_summary.get("full_source_policy_runner_package_ready") is False,
        "review evidence summary source-policy aliases stale",
    )
    checks.check(
        report.get("source_policy_apples_to_apples_external")
        == evidence_summary.get("source_policy_apples_to_apples_external")
        == "0/40",
        "review top-level source-policy apples-to-apples alias stale",
    )
    checks.check(
        evidence_summary.get("oc12_archive_tfe_preflight")
        == oc12_archive_tfe_preflight
        == "contract_entrypoints_callable_candidate_backed_source_policy_open/3/3/3/3/0/4",
        "review evidence summary OC12 archive TFE preflight alias stale",
    )
    checks.check(
        evidence_summary.get("oc12_archive_action_boundary")
        == oc12_archive_action_boundary
        == "4/1/False/False/True/13/20",
        "review evidence summary OC12 archive action boundary alias stale",
    )
    checks.check(
        evidence_summary.get("oc6_reopen_latest_external_probe")
        == oc6_reopen_latest_external_probe
        == "2026-06-21/9/0/0/4/False/False",
        "review evidence summary OC6 reopen latest-probe alias stale",
    )
    checks.check(
        evidence_summary.get("minimal_submission_code_dependency_boundary_status")
        == "narrowed_repro_ready_full_source_policy_package_blocked"
        and evidence_summary.get("minimal_submission_code_dependency_safe_use")
        == "narrowed_claim_replay_and_audit_provenance_only",
        "review evidence summary OC12 dependency aliases stale",
    )
    checks.check(
        evidence_summary.get("source_policy_execution_handoff_status")
        == b4_execution_handoff.get("status")
        == "source_policy_execution_handoff_ready_not_authorized_not_run"
        and evidence_summary.get("source_policy_execution_handoff_authorized") is False
        and evidence_summary.get("source_policy_execution_handoff_commands_not_run") is True,
        "review evidence summary source-policy handoff aliases stale",
    )
    checks.check(
        evidence_summary.get("source_policy_execution_handoff_command_traceability_summary")
        == expected_command_traceability,
        "review evidence summary source-policy handoff traceability stale",
    )
    checks.check(
        evidence_summary.get("source_policy_execution_handoff_unique_mapped_row_count")
        == expected_command_traceability.get("unique_mapped_row_count")
        == 20
        and evidence_summary.get("source_policy_execution_handoff_ra_hi_unique_row_count")
        == expected_command_traceability.get("ra_hi_unique_row_count")
        == 20
        and evidence_summary.get("source_policy_execution_handoff_traced_command_row_reference_total")
        == expected_command_traceability.get("traced_command_row_reference_total")
        == 32
        and evidence_summary.get("source_policy_execution_handoff_declared_mapped_row_reference_total")
        == expected_command_traceability.get("declared_mapped_row_reference_total")
        == 32,
        "review evidence summary source-policy handoff row-reference traceability changed",
    )
    checks.check(
        evidence_summary.get("source_policy_execution_handoff_declared_vs_traced_mismatch_count")
        == expected_command_traceability.get("declared_vs_traced_mismatch_count")
        == 0
        and evidence_summary.get("source_policy_execution_handoff_terminal_rows_with_command_refs")
        == expected_command_traceability.get("terminal_rows_with_command_refs")
        == 0
        and evidence_summary.get("source_policy_execution_handoff_traceability_closed_rows")
        == expected_command_traceability.get("source_policy_closed_rows")
        == 0
        and evidence_summary.get("source_policy_execution_handoff_traceability_promotion_ready_rows")
        == expected_command_traceability.get("promotion_ready_rows")
        == 0,
        "review evidence summary source-policy handoff terminal/closed traceability changed",
    )
    checks.check(
        evidence_summary.get("narrowed_claim_subcheck_disposition")
        == "bounded_subcheck_satisfied_not_global_submit"
        and evidence_summary.get("decision") == "do_not_submit_global",
        "review evidence summary decision aliases stale",
    )
    checks.check(
        evidence_summary.get("submission_manifest_narrowed_archive_boundary_status")
        == "narrowed_archive_ready_not_full_source_policy_runner_archive"
        and evidence_summary.get(
            "submission_manifest_narrowed_archive_boundary_source_policy_closed_ratio"
        )
        == "0/40"
        and evidence_summary.get(
            "submission_manifest_narrowed_archive_boundary_matches_reproducibility_manifest"
        )
        is True
        and evidence_summary.get(
            "submission_manifest_narrowed_archive_boundary_current_archive_usable_as_full_source_policy_runner_archive"
        )
        is False
        and evidence_summary.get(
            "submission_manifest_narrowed_archive_boundary_source_policy_execution_allowed_now"
        )
        is False
        and evidence_summary.get(
            "submission_manifest_narrowed_archive_boundary_exact_b4_opt_in_required_for_execution"
        )
        is True,
        "review evidence summary submission-manifest narrowed boundary aliases stale",
    )
    for token in [
        "## Global Reviewer Assessment",
        "## Input Artifact Provenance",
        "Hash algorithm: `sha256`.",
        "Timestamp policy: `deterministic_no_wall_clock_timestamp`.",
        "Stale token scan OC9/reference next-action stale: `False`.",
        "Readiness review delegates current global decision: `True`.",
        "B4 opt-in packet: `B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json`.",
        "B4 exact opt-in phrase: `I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json.`.",
        "## Global Review Semantic Contract",
        "Contract: `whole_paper_global_review_contract`.",
        "Decision matches objective completion: `True`.",
        "Objective-incomplete iff do-not-submit-global: `True`.",
        "All blocking objective requirements reported: `True`.",
        "Global findings include all blocking requirements: `True`.",
        "Narrowed claim does not override global decision: `True`.",
        "Source-policy rows closed: `0/40`.",
        "Accepted source-policy dynamic-order examples: `0/4`.",
        "TFE runner contract preflight status/entrypoints/candidate-backed/source-rows/execution-blocks: `contract_entrypoints_callable_candidate_backed_source_policy_open/3/3/3/3/0/4`.",
        "OC12 full-archive TFE runner preflight status/entrypoints/candidate-backed/source-rows/execution-blocks: `contract_entrypoints_callable_candidate_backed_source_policy_open/3/3/3/3/0/4`.",
        "Full source-policy runner package ready: `False`.",
        "No forbidden execution flags run_v047/heavy: `False/False`.",
        "B4 opt-in boundary retained: `True`.",
        "Global comparison policy artifact included: `True`.",
        "Submission manifest narrowed archive boundary matches reproducibility manifest: `True`.",
        "Submission manifest narrowed archive boundary status/source-policy/use/execution/exact: `narrowed_archive_ready_not_full_source_policy_runner_archive/0/40/False/False/True`.",
        "Submission manifest narrowed archive safe/opt-in action ids: `rebuild_read_only_audit_chain,rerun_read_only_validators,keep_narrowed_archive_provenance_only,monitor_reopen_conditions` / `authorized_b4_ra_hi_source_policy_execution`.",
        "Submission manifest narrowed archive closure/action maps:",
        "Top-level source-policy boundary aliases status/source-policy/use/execution/invoked/exact/scope: `narrowed_archive_ready_not_full_source_policy_runner_archive/0/40/False/False/False/True/narrowed_claim_only`.",
        "Top-level source-policy boundary safe/opt-in action ids: `rebuild_read_only_audit_chain,rerun_read_only_validators,keep_narrowed_archive_provenance_only,monitor_reopen_conditions` / `authorized_b4_ra_hi_source_policy_execution`.",
        "OC12 archive action boundary safe/opt-in/allowed/invoked/exact/commands/rows: `4/1/False/False/True/13/20`.",
        "OC12 archive action boundary safe/opt-in action ids: `rebuild_read_only_audit_chain,rerun_read_only_validators,keep_narrowed_archive_provenance_only,monitor_reopen_conditions` / `authorized_b4_ra_hi_source_policy_execution`.",
        "## Global Editorial Decision",
        "Scope: `whole_paper_cmame_submission_standard`.",
        "Decision: **do_not_submit_global**.",
        "Ranked global blockers: OC4,OC6,OC12.",
        "Non-overriding subcheck: `narrowed_claim_blocker_gate_pass_does_not_override_global_decision`.",
        "Safe current disposition: do not submit globally; use the narrowed result only to support bounded method/proof and common-reference diagnostic claims.",
        "Primary paper line: Gauss6/FullVA method and strict conditional proof are the paper core",
        "Global review rule: The review agent must lead with global submission readiness and evidence hierarchy",
        "Evidence tiering: dynamic-order rows support the order claim; mechanism-coverage rows support constraint and reaction consistency; diagnostic rows expose boundary, source-policy, and package gaps.",
        "Global blocker priority: OC4 source-policy reproduction rows; OC6 original TFE source-policy runner; OC12 full source-policy runner package.",
        "Gauss6/FullVA residual method | `main_claim_strongest`",
        "conditional sixth-order smooth-path theorem | `strong_conditional_claim_retained`",
        "formal TFE comparison | `appendix_or_diagnostic_only`",
        "source-policy/reproducibility audit | `boundary_and_diagnostic_only`",
        "## Global Substantive Findings",
        "`GF1` | `strength` | Main contribution is coherent and should lead the paper",
        "`GF2` | `conditional_pass` | Proof strength is acceptable only with explicit retained theorem interfaces",
        "P1, P2, and P3 are retained theorem interfaces; P6 is a separate solver-scale interface; P4's binding convention is retained while its 96-row certificate is proved; P7 is an output nonclaim boundary",
        "route-exclusive same-branch certificates",
        "cannot be mixed to lower constants, remove P6, or prove a P7 residual-to-error transfer theorem",
        "The theorem statement itself consumes only one residual-value certificate",
        "json_pointer `/theorem_residual_certificate_exclusivity`",
        "`GF3` | `scope_boundary` | Numerical evidence must be tiered by claim strength",
        "`GF4` | `global_blocker` | TFE and external comparisons are diagnostic, not a selling point",
        "`GF5` | `blocking` | Global submission readiness is still blocked",
        "`GF5` | `blocking` | Global submission readiness is still blocked | The narrowed proof/method package can pass as a bounded subcheck, but OC4, OC6, and OC12 dominate the whole-paper CMAME submission decision.",
        "OC4, OC6, and OC12 dominate the whole-paper CMAME submission decision",
        "### Global Finding Artifact Anchors",
        "`GF2` anchors:",
        "token `Full 132-row residual-defect certificate bridge`",
        "`GF5` anchors:",
        "json_pointer `/summary/blocking_open_count`",
        "## Global Blocker Hierarchy",
        "Review mode: whole-paper CMAME submission standard, not a local proof/report artifact checklist.",
        "Top-level blockers dominate narrowed-claim pass: OC4,OC6,OC12.",
        "Non-overriding local passes: B1,B2,B3,B4,B5,B6,B7,B8.",
        "Dimension priority: main contribution -> proof/theorem -> numerical validation -> comparison/source-policy -> reproducibility/code package -> manuscript style/integrity.",
        "`1` | `global_submission_blockers` | `OC4,OC6,OC12` | `do_not_submit_global` | `True`",
        "`2` | `retained_theorem_boundaries` | `theorem_level_eta_h_solver_policy_evidence,closed_residual_to_error_theorem_for_mechanism_rows` | `conditional_proof_only`",
        "`3` | `partial_numerical_scope` | `source_policy_dynamic_order_examples_0_of_4,source_policy_rows_0_of_40` | `no_external_or_source_policy_claim`",
        "`4` | `non_overriding_local_passes` | `B1,B2,B3,B4,B5,B6,B7,B8` | `narrowed_claim_only`",
        "## Global Review Dimension Evidence",
        "### method_contribution",
        "Evidence: 132-row Lie-group Gauss6/FullVA residual described in manuscript/PDF.",
        "Anchor: `main_cmame.tex` tex_label `\\label{sec:method}`",
        "### proof_and_theorem",
        "Evidence: direct residual-bridge/Kantorovich PC2 route closed.",
        "Anchor: `PROOF_CLAIM_TRACEABILITY_AUDIT.json` json_pointer `/remaining_claim_boundary/status`",
        "### comparison_and_source_policy",
        "Evidence: source-policy row closure ledger records 0/40 closed rows.",
        "Anchor: `SOURCE_POLICY_ROW_CLOSURE_LEDGER.json` json_pointer `/coverage/rows_source_policy_closed`",
        "### reproducibility_and_code_package",
        "Evidence: 10-file replay candidate with one 158-line Python core is present.",
        "Anchor: `CMAME_RUNNER_CENTERED_REPRODUCIBILITY_AUDIT.json` json_pointer `/full_source_policy_runner_package_ready`",
        "## Global Submission Decision Basis",
        "`comparison_and_source_policy`: verdict `blocked_for_global_submission`",
    ]:
        checks.check(token in report_md, f"review markdown missing global-review assessment token: {token}")
    checks.check(
        report.get("submission_standard_met") is report.get("global_submission_standard_met"),
        "top-level submission_standard_met must equal global submission standard",
    )
    checks.check(report.get("decision") == "do_not_submit_global", "review agent decision changed")
    checks.check(
        report.get("global_review_verdict") == report.get("decision") == "do_not_submit_global",
        "review agent global review verdict must be the top-level decision",
    )
    checks.check(
        report.get("global_review_verdict_scope") == "top_level_global_submission_standard",
        "review agent global review verdict scope changed",
    )
    checks.check(report.get("narrowed_claim_subcheck_met") is True, "narrowed subcheck status missing")
    checks.check(
        report.get("narrowed_claim_subcheck_disposition")
        == "bounded_subcheck_satisfied_not_global_submit",
        "narrowed subcheck disposition must stay non-global",
    )
    compatibility_aliases = report.get("narrowed_claim_compatibility_aliases", {})
    checks.check(
        isinstance(compatibility_aliases, dict)
        and compatibility_aliases.get("legacy_fields")
        == [
            "narrowed_submission_standard_met",
            "narrowed_claim_submission_standard_met",
            "narrowed_claim_decision",
        ]
        and "subsidiary narrowed-claim subcheck only" in compatibility_aliases.get("meaning", "")
        and "not the top-level global review decision" in compatibility_aliases.get("meaning", "")
        and compatibility_aliases.get("top_level_global_decision_field") == "decision",
        "narrowed compatibility-alias boundary missing",
    )
    checks.check(
        report.get("narrowed_submission_standard_met") is True,
        "legacy narrowed submission-standard alias missing",
    )
    checks.check(
        report.get("narrowed_claim_submission_standard_met") is report.get("narrowed_submission_standard_met") is True,
        "legacy narrowed-claim submission-standard alias missing or stale",
    )
    checks.check(
        report.get("narrowed_claim_decision") == "submit_under_narrowed_claim",
        "legacy narrowed review-agent decision alias changed",
    )
    checks.check(
        report.get("narrowed_claim_role") == "subsidiary_bounded_subcheck_not_top_level_review_verdict",
        "narrowed claim must remain a subsidiary review-agent subcheck",
    )
    subsidiary_narrowed_claim = report.get("subsidiary_narrowed_claim", {})
    checks.check(
        subsidiary_narrowed_claim.get("subcheck_met") is True
        and subsidiary_narrowed_claim.get("disposition")
        == "bounded_subcheck_satisfied_not_global_submit",
        "subsidiary narrowed-claim subcheck disposition missing",
    )
    checks.check(
        subsidiary_narrowed_claim.get("submission_standard_met") is True,
        "subsidiary narrowed-claim legacy standard alias missing",
    )
    checks.check(
        subsidiary_narrowed_claim.get("decision") == "submit_under_narrowed_claim",
        "subsidiary narrowed-claim legacy decision alias changed",
    )
    checks.check(
        subsidiary_narrowed_claim.get("legacy_submission_standard_met_alias") is True
        and subsidiary_narrowed_claim.get("legacy_decision_alias") == "submit_under_narrowed_claim",
        "subsidiary narrowed-claim legacy alias mirror missing",
    )
    checks.check(
        subsidiary_narrowed_claim.get("role") == "subsidiary_bounded_subcheck_not_top_level_review_verdict",
        "subsidiary narrowed-claim role changed",
    )
    checks.check(
        subsidiary_narrowed_claim.get("does_not_override_global_decision") is True,
        "subsidiary narrowed-claim result must not override global decision",
    )
    checks.check(report.get("full_source_policy_submission_standard_met") is False, "full source-policy standard overclaimed")
    checks.check(report.get("open_blockers") == open_blockers, "review agent blocker list stale")
    checks.check(report.get("open_blocker_ids") == open_blockers, "review agent blocker-id alias stale")
    checks.check(report.get("open_blocker_count") == len(open_blockers) == 3, "review agent open-blocker count changed")
    checks.check(
        report.get("blockers_by_id") == objective_completion.get("blockers_by_id"),
        "review agent blocker alias map stale",
    )
    checks.check(
        report.get("objective_blocker_matrix_status") == "global_objective_blockers_remain_open",
        "review agent objective blocker matrix status stale",
    )
    checks.check(
        report.get("blocker_open_by_id")
        == objective_completion.get("blocker_open_by_id")
        == EXPECTED_BLOCKER_OPEN_BY_ID,
        "review agent blocker-open alias map stale",
    )
    checks.check(
        report.get("blocker_status_by_id") == objective_completion.get("blocker_status_by_id"),
        "review agent blocker status alias map stale",
    )
    checks.check(
        report.get("blocker_closure_decision_by_id")
        == objective_completion.get("blocker_closure_decision_by_id")
        == EXPECTED_BLOCKER_CLOSURE_DECISION_BY_ID,
        "review agent blocker closure-decision alias map stale",
    )
    checks.check(
        report.get("blocker_closure_allowed_by_id")
        == objective_completion.get("blocker_closure_allowed_by_id")
        == EXPECTED_BLOCKER_CLOSURE_ALLOWED_BY_ID,
        "review agent blocker closure-allowed alias map stale",
    )
    checks.check(
        report.get("blocker_next_actions_by_id") == objective_completion.get("blocker_next_actions_by_id"),
        "review agent blocker next-action alias map stale",
    )
    checks.check(
        report.get("blocker_required_to_close_by_id")
        == objective_completion.get("blocker_required_to_close_by_id"),
        "review agent blocker required-to-close alias map stale",
    )
    checks.check(
        report.get("blocker_safe_next_actions_by_id")
        == objective_completion.get("blocker_safe_next_actions_by_id"),
        "review agent blocker safe-next-action alias map stale",
    )
    checks.check(
        report.get("blocker_opt_in_required_actions_by_id")
        == objective_completion.get("blocker_opt_in_required_actions_by_id"),
        "review agent blocker opt-in-required-action alias map stale",
    )
    checks.check(
        report.get("objective_blockers_by_id") == objective_completion.get("blockers_by_id"),
        "review agent objective blocker map stale",
    )
    checks.check(
        report.get("objective_blocker_open_by_id") == objective_completion.get("blocker_open_by_id"),
        "review agent objective blocker-open map stale",
    )
    checks.check(
        report.get("objective_blocker_status_by_id")
        == objective_completion.get("blocker_status_by_id"),
        "review agent objective blocker status map stale",
    )
    checks.check(
        report.get("objective_blocker_closure_decision_by_id")
        == objective_completion.get("blocker_closure_decision_by_id"),
        "review agent objective blocker closure-decision map stale",
    )
    checks.check(
        report.get("objective_blocker_closure_allowed_by_id")
        == objective_completion.get("blocker_closure_allowed_by_id"),
        "review agent objective blocker closure-allowed map stale",
    )
    checks.check(
        report.get("objective_blocker_next_actions_by_id")
        == objective_completion.get("blocker_next_actions_by_id"),
        "review agent objective blocker next-action map stale",
    )
    checks.check(
        report.get("objective_blocker_required_to_close_by_id")
        == objective_completion.get("blocker_required_to_close_by_id"),
        "review agent objective blocker required-to-close map stale",
    )
    checks.check(
        report.get("objective_blocker_safe_next_actions_by_id")
        == objective_completion.get("blocker_safe_next_actions_by_id"),
        "review agent objective blocker safe-next-action map stale",
    )
    checks.check(
        report.get("objective_blocker_opt_in_required_actions_by_id")
        == objective_completion.get("blocker_opt_in_required_actions_by_id"),
        "review agent objective blocker opt-in-required-action map stale",
    )
    checks.check(
        report.get("cmame_blocker_gate_open_blockers") == cmame_blocker_gate_open,
        "CMAME narrowed blocker-gate list stale",
    )
    checks.check(
        report.get("cmame_blocker_gate_open_blocker_count") == len(cmame_blocker_gate_open) == 0,
        "CMAME narrowed blocker-gate open count changed",
    )
    checks.check(
        {item.get("id") for item in report.get("blocking_findings", [])} == set(open_blockers),
        "global review blocking findings stale",
    )
    checks.check(
        report.get("closed_blockers_scope") == "narrowed_claim_blocker_gate_not_global_submission_standard",
        "review agent closed-blocker scope missing",
    )
    checks.check(
        set(report.get("narrowed_claim_closed_blockers", []))
        == set(report.get("closed_blockers", []))
        == {"B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8"},
        "review agent narrowed closed-blocker list stale",
    )
    stale_reference_phrase = "external item-by-item reference web verification remains open"
    checks.check(stale_reference_phrase not in report.get("review_conclusion", ""), "review conclusion has stale reference-verification boundary")
    checks.check(stale_reference_phrase not in report_md, "review markdown has stale reference-verification boundary")
    report_blob = json.dumps(report, sort_keys=True)
    authorized_b4 = b4_post_execution_audit.get("verified_authorized_execution_recorded") is True
    b4_guarded_driver_phrase = "verified authorized guarded-driver execution"
    b4_verified_evidence_phrase = f"B4 post-execution audit records {b4_guarded_driver_phrase}"
    b4_verified_conclusion_phrase = f"B4 post-execution audit now records {b4_guarded_driver_phrase}"
    b4_no_verified_evidence_phrase = (
        "B4 post-execution audit records existing ready-command artifacts but no verified authorized execution"
    )
    b4_no_verified_conclusion_phrase = (
        "B4 post-execution audit now records existing ready-command artifacts without verified "
        "authorized guarded-driver execution"
    )
    if authorized_b4:
        checks.check(
            b4_verified_conclusion_phrase in report.get("review_conclusion", ""),
            "review conclusion missing B4 verified-authorized post-execution boundary",
        )
        checks.check(
            b4_no_verified_evidence_phrase not in report_blob
            and b4_no_verified_evidence_phrase not in report_md
            and b4_no_verified_conclusion_phrase not in report_blob
            and b4_no_verified_conclusion_phrase not in report_md,
            "review report has stale B4 no-verified-authorized-execution wording",
        )
    else:
        checks.check(
            b4_no_verified_evidence_phrase in report_blob and b4_no_verified_evidence_phrase in report_md,
            "review report missing B4 no-verified-authorized evidence boundary",
        )
        checks.check(
            b4_no_verified_conclusion_phrase in report.get("review_conclusion", "")
            and b4_no_verified_conclusion_phrase in report_md,
            "review conclusion missing B4 no-verified-authorized post-execution boundary",
        )
        checks.check(
            b4_verified_evidence_phrase not in report_blob
            and b4_verified_evidence_phrase not in report_md
            and b4_verified_conclusion_phrase not in report_blob
            and b4_verified_conclusion_phrase not in report_md,
            "review report has stale B4 verified-authorized wording",
        )
    checks.check(
        "Global submission-standard review verdict: do not submit globally yet"
        in report.get("review_conclusion", ""),
        "review conclusion missing global verdict",
    )
    checks.check(
        "subsidiary bounded subcheck, not the top-level review verdict"
        in report.get("review_conclusion", ""),
        "review conclusion lets narrowed result replace the global verdict",
    )
    checks.check("OC4 source-policy reproduction" in report_md, "review markdown missing OC4 global blocker")
    checks.check("OC6 original TFE runner completion" in report_md, "review markdown missing OC6 global blocker")
    checks.check(
        "OC12 minimal source-policy runner package readiness" in report_md,
        "review markdown missing OC12 global blocker",
    )
    checks.check(
        "full source-policy runner/package boundary remains a global submission blocker" in report.get("review_conclusion", ""),
        "review conclusion missing full source-policy package boundary",
    )
    checks.check(
        set(report.get("closed_blockers", [])) == {"B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8"},
        "review agent closed blockers changed",
    )
    pdf_style_checks = report.get("pdf_style_review_checks", {})
    checks.check(
        pdf_style_checks.get("schema")
        == pdf_style_review.get("schema")
        == "cmame-pdf-style-review-audit-v1",
        "PDF-style review schema not carried into review",
    )
    checks.check(
        pdf_style_checks.get("status")
        == "pdf_read_review_passed_narrowed_claim_subcheck_global_boundary_retained",
        "PDF-style review status changed",
    )
    checks.check(pdf_style_checks.get("ars_route") == "academic-paper-reviewer/full", "PDF-style ARS route changed")
    checks.check(pdf_style_checks.get("submission_ready") is False, "PDF-style review overclaims submission ready")
    checks.check(
        pdf_style_checks.get("submission_ready_scope")
        == pdf_style_review.get("submission_ready_scope")
        == "pdf_style_review_narrowed_claim_subcheck_passed_global_submission_boundary_retained",
        "PDF-style submission-ready scope not carried into review",
    )
    checks.check(
        pdf_style_checks.get("submission_standard_scope")
        == pdf_style_review.get("submission_standard_scope")
        == "narrowed_claim_only",
        "PDF-style submission standard scope not carried into review",
    )
    checks.check(
        pdf_style_checks.get("submission_standard_role")
        == pdf_style_review.get("submission_standard_role")
        == "narrowed_claim_subcheck_not_global_review_verdict",
        "PDF-style submission standard role not carried into review",
    )
    checks.check(
        pdf_style_checks.get("global_submission_standard_met")
        is pdf_style_review.get("global_submission_standard_met")
        is False,
        "PDF-style global submission standard overclaimed in review",
    )
    pdf_readiness_boundary = pdf_style_checks.get("readiness_boundary", {})
    pdf_remaining_gate = pdf_style_checks.get("remaining_gate_scope", {})
    expected_pdf_global_boundaries = [
        "full_source_policy_package_ready",
        "theorem_level_eta_h_solver_policy_evidence",
        "closed_residual_to_error_theorem_for_mechanism_rows",
    ]
    checks.check(
        pdf_readiness_boundary == pdf_style_review.get("readiness_boundary", {}),
        "PDF-style readiness boundary not carried into review",
    )
    checks.check(
        pdf_readiness_boundary.get("submission_standard_scope") == "narrowed_claim_only",
        "PDF-style readiness boundary scope changed in review",
    )
    checks.check(
        pdf_readiness_boundary.get("narrowed_claim_b4_b6_b7_statuses")
        == {"B4": "closed", "B6": "closed", "B7": "closed"},
        "PDF-style readiness B4/B6/B7 status boundary changed in review",
    )
    checks.check(
        pdf_readiness_boundary.get("global_submission_boundaries_retained") == expected_pdf_global_boundaries,
        "PDF-style readiness global boundaries changed in review",
    )
    checks.check(
        pdf_remaining_gate == pdf_style_review.get("remaining_gate_scope", {}),
        "PDF-style remaining gate not carried into review",
    )
    checks.check(
        pdf_remaining_gate.get("narrowed_claim_submission_standard_met") is True
        and pdf_remaining_gate.get("quality_review_passed_under_narrowed_claim") is True,
        "PDF-style remaining gate lost narrowed-claim review pass markers",
    )
    checks.check(
        pdf_remaining_gate.get("global_submission_standard_met") is False
        and pdf_remaining_gate.get("submission_ready_not_claimed_by_pdf_style_audit") is True,
        "PDF-style remaining gate overclaims global submission readiness",
    )
    checks.check(
        pdf_remaining_gate.get("source_policy_rows_closed") == 0
        and pdf_remaining_gate.get("source_policy_rows_total") == 40,
        "PDF-style remaining gate source-policy counts changed in review",
    )
    checks.check(
        pdf_remaining_gate.get("eta_h_theorem_condition_retained") is True
        and pdf_remaining_gate.get("accepted_residual_to_error_theorem") is False
        and pdf_remaining_gate.get("residual_to_error_blocking_obligations") == 7
        and pdf_remaining_gate.get("residual_to_error_route_promoted") is False,
        "PDF-style remaining proof gates changed in review",
    )
    checks.check(
        pdf_remaining_gate.get("global_submission_boundaries_retained") == expected_pdf_global_boundaries,
        "PDF-style remaining global boundaries changed in review",
    )
    checks.check(pdf_style_checks.get("reference_text_read") is True, "PDF-style reference text not read")
    checks.check(pdf_style_checks.get("manuscript_text_read") is True, "PDF-style manuscript text not read")
    checks.check(pdf_style_checks.get("flat_manuscript_text_read") is True, "PDF-style flat manuscript text not read")
    checks.check(pdf_style_checks.get("reference_line_count", 0) > 1000, "PDF-style reference line count low")
    checks.check(pdf_style_checks.get("reference_figure_count") == 18, "PDF-style reference figure count changed")
    checks.check(pdf_style_checks.get("reference_algorithm_count") >= 2, "PDF-style reference algorithms missing")
    checks.check(
        pdf_style_checks.get("reference_algorithm_boxes_present") is True,
        "PDF-style reference algorithm-box check missing",
    )
    checks.check(
        pdf_style_checks.get("reference_numerical_experiments_section") is True,
        "PDF-style reference numerical section missing",
    )
    checks.check(
        pdf_style_checks.get("reference_work_precision_figures") is True,
        "PDF-style reference work/precision feature missing",
    )
    checks.check(
        pdf_style_checks.get("reference_data_availability_and_declarations") is True,
        "PDF-style reference declarations missing",
    )
    checks.check(pdf_style_checks.get("manuscript_figure_count") == 13, "PDF-style manuscript figure count changed")
    checks.check(pdf_style_checks.get("manuscript_theorem_count", 0) >= 1, "PDF-style manuscript theorem missing")
    checks.check(pdf_style_checks.get("manuscript_proof_token_count", 0) >= 5, "PDF-style manuscript proof tokens low")
    checks.check(
        pdf_style_checks.get("manuscript_audit_residue_mentions", 0)
        > pdf_style_checks.get("reference_audit_residue_mentions", 0),
        "PDF-style audit residue comparison not preserved",
    )
    checks.check(pdf_style_checks.get("source_policy_rows_closed") == 0, "PDF-style source-policy rows changed")
    checks.check(pdf_style_checks.get("source_policy_total_rows") == 40, "PDF-style source-policy total changed")
    checks.check(
        pdf_style_checks.get("external_superiority_claim_allowed") is False,
        "PDF-style external superiority boundary changed",
    )
    checks.check(
        pdf_style_checks.get("direct_pc2_proof_gap_closed")
        == pdf_style_checks.get("proof_gap_closed")
        is True
        and pdf_style_checks.get("proof_gap_closed_scope")
        == "direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open"
        and "schema-compatible shorthand for direct_pc2_proof_gap_closed"
        in pdf_style_checks.get("proof_gap_closed_reading_rule", ""),
        "PDF-style proof gap closure must be scoped to direct PC2",
    )
    checks.check(
        pdf_style_checks.get("stage_residual_O_h7_implementation_defect_proved") is True,
        "PDF-style stage residual proof closure missing",
    )
    checks.check(
        pdf_style_checks.get("eta_h_O_h7_solver_policy_evidence") is False,
        "PDF-style eta_h evidence unexpectedly closed",
    )
    checks.check(pdf_style_checks.get("figure_set_b7_closed") is True, "PDF-style B7 not closed")
    checks.check(pdf_style_checks.get("prose_b6_closed") is True, "PDF-style B6 not closed")
    checks.check(
        pdf_style_checks.get("minimal_reproducibility_submission_ready") is False,
        "PDF-style minimal package unexpectedly ready",
    )
    checks.check(
        pdf_style_checks.get("blocking_finding_ids") == [],
        "PDF-style blocking finding IDs changed",
    )
    checks.check(pdf_style_checks.get("submission_standard_met") is True, "PDF-style submission standard changed")
    checks.check(pdf_style_checks.get("quality_review_passed") is True, "PDF-style quality review changed")
    checks.check(pdf_style_checks.get("decision") == "submit_under_narrowed_claim", "PDF-style decision changed")
    objective_checks = report.get("objective_completion_checks", {})
    checks.check(
        objective_checks.get("schema")
        == objective_completion.get("schema")
        == "objective-completion-audit-v1",
        "objective completion audit not carried into review",
    )
    checks.check(
        objective_checks.get("status") == "not_complete_submission_standard_open",
        "objective completion status changed",
    )
    checks.check(objective_checks.get("objective_complete") is False, "objective unexpectedly complete")
    checks.check(objective_checks.get("submission_ready") is False, "objective audit unexpectedly submission ready")
    checks.check(objective_checks.get("requirement_count") == 12, "objective requirement count changed")
    checks.check(objective_checks.get("satisfied_count") == 9, "objective satisfied count changed")
    checks.check(objective_checks.get("partial_count") == 2, "objective partial count changed")
    checks.check(objective_checks.get("open_count") == 1, "objective open count changed")
    checks.check(objective_checks.get("blocking_open_count") == 3, "objective blocking-open count changed")
    checks.check(
        objective_checks.get("blockers_by_id") == objective_completion.get("blockers_by_id"),
        "objective blocker map not carried into review objective checks",
    )
    checks.check(
        objective_checks.get("objective_blocker_matrix_status") == "global_objective_blockers_remain_open",
        "objective blocker matrix status not carried into review objective checks",
    )
    checks.check(
        objective_checks.get("blocker_open_by_id")
        == objective_completion.get("blocker_open_by_id")
        == EXPECTED_BLOCKER_OPEN_BY_ID,
        "objective blocker open map not carried into review objective checks",
    )
    checks.check(
        objective_checks.get("blocker_status_by_id")
        == objective_completion.get("blocker_status_by_id"),
        "objective blocker status map not carried into review objective checks",
    )
    checks.check(
        objective_checks.get("blocker_closure_decision_by_id")
        == objective_completion.get("blocker_closure_decision_by_id")
        == EXPECTED_BLOCKER_CLOSURE_DECISION_BY_ID,
        "objective blocker closure-decision map not carried into review objective checks",
    )
    checks.check(
        objective_checks.get("blocker_closure_allowed_by_id")
        == objective_completion.get("blocker_closure_allowed_by_id")
        == EXPECTED_BLOCKER_CLOSURE_ALLOWED_BY_ID,
        "objective blocker closure-allowed map not carried into review objective checks",
    )
    checks.check(
        objective_checks.get("blocker_next_actions_by_id")
        == objective_completion.get("blocker_next_actions_by_id"),
        "objective blocker next-action map not carried into review objective checks",
    )
    checks.check(
        objective_checks.get("blocker_required_to_close_by_id")
        == objective_completion.get("blocker_required_to_close_by_id"),
        "objective blocker required-to-close map not carried into review objective checks",
    )
    checks.check(
        objective_checks.get("blocker_safe_next_actions_by_id")
        == objective_completion.get("blocker_safe_next_actions_by_id"),
        "objective blocker safe-next-action map not carried into review objective checks",
    )
    checks.check(
        objective_checks.get("blocker_opt_in_required_actions_by_id")
        == objective_completion.get("blocker_opt_in_required_actions_by_id"),
        "objective blocker opt-in-required-action map not carried into review objective checks",
    )
    checks.check(objective_checks.get("core_matrix_ready") is True, "objective core matrix should be ready")
    checks.check(objective_checks.get("source_policy_closed") is False, "objective source policy should remain open")
    checks.check(
        objective_checks.get("b2_source_policy_closed") is False
        and objective_checks.get("b2_active_suites_closed") is True
        and objective_checks.get("b2_active_suites_closed_by_demotion") is True,
        "objective B2 demotion closure should remain closed without source-policy row promotion",
    )
    checks.check(objective_checks.get("tfe_runner_closed") is False, "objective TFE runner should remain open")
    checks.check(objective_checks.get("proof_closed") is True, "objective proof should be closed by direct substitution")
    checks.check(objective_checks.get("quality_review_closed") is True, "objective quality review should be closed")
    checks.check(objective_checks.get("minimal_code_ready") is False, "objective minimal code should remain open")
    result_checks = report.get("result_checks", {})
    checks.check(result_checks.get("paper_result_pack_schema") == "paper-result-pack-v1", "result pack schema missing")
    checks.check(result_checks.get("paper_includes_latest_common_reference_result") is True, "manuscript not updated with result pack")
    checks.check(result_checks.get("pdf_text_includes_latest_common_reference_result") is True, "PDF text not updated with result pack")
    checks.check(result_checks.get("manuscript_includes_all_method_matrix") is True, "manuscript missing all-method matrix")
    checks.check(result_checks.get("pdf_text_includes_all_method_matrix") is True, "PDF text missing all-method matrix")
    checks.check(result_checks.get("all_method_matrix_all_methods_visible") is True, "all-method matrix method labels not all visible")
    checks.check(result_checks.get("all_method_matrix_all_examples_visible") is True, "all-method matrix example labels not all visible")
    checks.check(result_checks.get("proof_conditional_boundary_visible") is True, "conditional proof boundary not visible in manuscript/PDF")
    checks.check(result_checks.get("publication_figure_boundary_visible") is True, "publication figure boundary not visible in manuscript/PDF")
    checks.check(
        result_checks.get("source_policy_progress_boundary_visible") is True,
        "source-policy progress boundary not visible in manuscript/PDF",
    )
    checks.check(
        result_checks.get("four_example_dashboard_schema")
        == four_example_dashboard.get("schema")
        == "four-example-source-policy-dashboard-v1",
        "four-example source-policy dashboard not carried into review",
    )
    checks.check(
        result_checks.get("four_example_dashboard_status")
        == "all_four_examples_checked_source_policy_dynamic_order_open",
        "four-example dashboard status changed",
    )
    checks.check(
        result_checks.get("four_example_dashboard_local_dynamic_order_status")
        == "accepted_method_dynamic_order_2_of_4_source_policy_external_open",
        "four-example dashboard local dynamic-order status changed",
    )
    checks.check(
        result_checks.get("four_example_dashboard_local_evidence_coverage_status")
        == "all_four_examples_local_evidence_present_source_policy_dynamic_order_open",
        "four-example dashboard local evidence-coverage status changed",
    )
    checks.check(
        result_checks.get("four_example_dashboard_all_four_examples_checked") is True,
        "four-example dashboard does not check all four examples",
    )
    checks.check(
        result_checks.get("four_example_dashboard_examples")
        == ["single_pendulum", "double_pendulum", "four_link", "slider_crank"],
        "four-example dashboard examples changed",
    )
    checks.check(result_checks.get("four_example_dashboard_row_count") == 4, "four-example dashboard row count changed")
    checks.check(
        result_checks.get("four_example_dashboard_local_evidence_coverage_examples") == 4,
        "four-example dashboard local evidence coverage is not 4/4",
    )
    checks.check(
        result_checks.get("four_example_dashboard_local_evidence_coverage_names")
        == ["single_pendulum", "double_pendulum", "four_link", "slider_crank"],
        "four-example dashboard local evidence coverage names changed",
    )
    checks.check(
        result_checks.get("four_example_dashboard_accepted_method_dynamic_order_examples")
        == ["single_pendulum", "double_pendulum"],
        "four-example dashboard accepted method dynamic-order examples changed",
    )
    checks.check(
        result_checks.get("four_example_dashboard_accepted_method_dynamic_order_example_count") == 2,
        "four-example dashboard accepted method dynamic-order count changed",
    )
    checks.check(
        result_checks.get("four_example_dashboard_mechanism_coverage_examples") == ["four_link", "slider_crank"],
        "four-example dashboard mechanism-coverage examples changed",
    )
    checks.check(
        result_checks.get("four_example_dashboard_mechanism_coverage_example_count") == 2,
        "four-example dashboard mechanism-coverage count changed",
    )
    checks.check(
        result_checks.get("four_example_dashboard_local_dynamic_order_closed_examples") == 2,
        "four-example dashboard local dynamic-order count is not 2/4",
    )
    checks.check(
        result_checks.get("four_example_dashboard_local_dynamic_order_closed_names")
        == ["single_pendulum", "double_pendulum"],
        "four-example dashboard local dynamic-order example names changed",
    )
    checks.check(
        result_checks.get("four_example_dashboard_method_side_order_gate_examples")
        == ["single_pendulum", "double_pendulum"],
        "four-example dashboard method-side order examples changed",
    )
    checks.check(
        result_checks.get("four_example_dashboard_closed_loop_true_dynamic_order_closed_examples") == 2,
        "four-example dashboard closed-loop true-dynamic closure count changed",
    )
    checks.check(
        result_checks.get("four_example_dashboard_closed_loop_true_dynamic_order_closed_names")
        == ["four_link", "slider_crank"],
        "four-example dashboard closed-loop true-dynamic names changed",
    )
    checks.check(
        result_checks.get("four_example_dashboard_closed_loop_true_dynamic_step_sizes")
        == [0.1, 0.05, 0.025],
        "four-example dashboard closed-loop true-dynamic step sizes changed",
    )
    checks.check(
        result_checks.get("four_example_dashboard_closed_loop_true_dynamic_reference_h") == 0.0125,
        "four-example dashboard closed-loop true-dynamic reference h changed",
    )
    checks.check(
        result_checks.get("four_example_dashboard_closed_loop_true_dynamic_stage_oracle_used") is False,
        "four-example dashboard closed-loop true-dynamic stage oracle boundary changed",
    )
    checks.check(
        result_checks.get("four_example_dashboard_closed_loop_true_dynamic_rows") == 6,
        "four-example dashboard closed-loop true-dynamic row count changed",
    )
    checks.check(
        result_checks.get("four_example_dashboard_common_reference_cells") == 44,
        "four-example dashboard common-reference cell count changed",
    )
    checks.check(
        result_checks.get("four_example_dashboard_nonlocal_cells") == 40,
        "four-example dashboard nonlocal cell count changed",
    )
    checks.check(result_checks.get("four_example_dashboard_order_wins") == 40, "four-example dashboard order wins changed")
    checks.check(result_checks.get("four_example_dashboard_error_wins") == 40, "four-example dashboard error wins changed")
    checks.check(
        result_checks.get("four_example_dashboard_source_policy_closed_rows") == 0,
        "four-example dashboard source-policy closed rows changed",
    )
    checks.check(
        result_checks.get("four_example_dashboard_accepted_source_policy_dynamic_order_examples") == 0,
        "four-example dashboard accepted source-policy dynamic-order examples changed",
    )
    checks.check(
        result_checks.get("four_example_dashboard_external_superiority_allowed") is False,
        "four-example dashboard external-superiority boundary changed",
    )
    checks.check(
        result_checks.get("four_example_dashboard_default_1e_4_required") is False,
        "four-example dashboard default 1e-4 changed",
    )
    checks.check(
        result_checks.get("four_example_dashboard_heavy_run_invoked") is False,
        "four-example dashboard heavy-run flag changed",
    )
    for key in [
        "all_method_matrix_tex_missing_methods",
        "all_method_matrix_flat_tex_missing_methods",
        "all_method_matrix_pdf_missing_methods",
        "all_method_matrix_flat_pdf_missing_methods",
        "all_method_matrix_tex_missing_examples",
        "all_method_matrix_flat_tex_missing_examples",
        "all_method_matrix_pdf_missing_examples",
        "all_method_matrix_flat_pdf_missing_examples",
        "proof_conditional_tex_missing",
        "proof_conditional_flat_tex_missing",
        "proof_conditional_pdf_missing",
        "proof_conditional_flat_pdf_missing",
        "publication_figure_tex_missing",
        "publication_figure_flat_tex_missing",
        "publication_figure_pdf_missing",
        "publication_figure_flat_pdf_missing",
        "source_policy_progress_tex_missing",
        "source_policy_progress_flat_tex_missing",
        "source_policy_progress_pdf_missing",
        "source_policy_progress_flat_pdf_missing",
    ]:
        checks.check(result_checks.get(key) == [], f"{key} should be empty")
    for token in [
        "local evidence coverage `4/4`",
        "accepted method dynamic-order examples `2/4`",
        "mechanism-coverage examples `2/4`",
        "accepted source-policy dynamic-order examples `0/4`",
        "Closed-loop coarse-window trajectory diagnostics: `2/2`",
        "stage oracle used `False`",
    ]:
        checks.check(token in report_md, f"review report missing four-example boundary token: {token}")
    checks.check(result_checks.get("all_method_matrix_complete") is True, "result pack all-method matrix incomplete")
    checks.check(result_checks.get("all_method_matrix_method_count") == 11, "all-method matrix method count changed")
    checks.check(result_checks.get("all_method_matrix_cell_count") == 44, "all-method matrix cell count changed")
    checks.check(
        result_checks.get("paper_numerical_matrix_schema")
        == numerical_matrix.get("schema")
        == "paper-numerical-result-matrix-v1",
        "paper numerical result matrix not carried into review",
    )
    checks.check(
        result_checks.get("paper_numerical_matrix_status")
        == "paper_ready_table_source_policy_boundary_open",
        "paper numerical result matrix status changed",
    )
    checks.check(result_checks.get("paper_numerical_matrix_row_count") == 44, "paper numerical matrix row count changed")
    checks.check(
        result_checks.get("paper_numerical_matrix_expected_row_count") == 44,
        "paper numerical matrix expected row count changed",
    )
    checks.check(
        result_checks.get("paper_numerical_matrix_method_count") == 11,
        "paper numerical matrix method count changed",
    )
    checks.check(
        result_checks.get("paper_numerical_matrix_raw_row_count") == 132,
        "paper numerical matrix raw row count changed",
    )
    checks.check(
        result_checks.get("paper_numerical_matrix_source_policy_external_superiority_allowed") is False,
        "paper numerical matrix source-policy boundary changed",
    )
    checks.check(
        result_checks.get("paper_numerical_matrix_direct_error_superiority_allowed") is False,
        "paper numerical matrix direct-error boundary changed",
    )
    checks.check(
        result_checks.get("paper_numerical_matrix_strict_external_error_claim_rows") == 0,
        "paper numerical matrix strict external row count changed",
    )
    checks.check(
        result_checks.get("paper_numerical_matrix_direct_order_wins")
        == result_checks.get("paper_numerical_matrix_direct_order_comparisons")
        == 40,
        "paper numerical matrix order win count changed",
    )
    checks.check(
        result_checks.get("paper_numerical_matrix_direct_error_wins")
        == result_checks.get("paper_numerical_matrix_direct_error_comparisons")
        == 40,
        "paper numerical matrix error win count changed",
    )
    checks.check(
        result_checks.get("result_traceability_schema")
        == result_traceability.get("schema")
        == "result-to-manuscript-traceability-audit-v1",
        "result-to-manuscript traceability audit not carried into review",
    )
    checks.check(
        result_checks.get("result_traceability_status")
        == "all_44_velocity_cells_trace_to_manuscript_and_pdf_source_policy_open",
        "result-to-manuscript traceability status changed",
    )
    checks.check(
        result_checks.get("result_traceability_velocity_cells_checked") == 44,
        "result-to-manuscript velocity cell count changed",
    )
    checks.check(result_checks.get("result_traceability_main_tex_cells") == 44, "main TeX traceability changed")
    checks.check(result_checks.get("result_traceability_flat_tex_cells") == 44, "flat TeX traceability changed")
    checks.check(result_checks.get("result_traceability_main_pdf_cells") == 44, "main PDF traceability changed")
    checks.check(result_checks.get("result_traceability_flat_pdf_cells") == 44, "flat PDF traceability changed")
    checks.check(result_checks.get("result_traceability_closed") is True, "result traceability should be closed")
    checks.check(
        result_checks.get("result_traceability_source_policy_reproduction_closed") is False,
        "result traceability overclaims source-policy reproduction",
    )
    checks.check(
        result_checks.get("result_traceability_external_superiority_allowed") is False,
        "result traceability overclaims external superiority",
    )
    checks.check(
        result_checks.get("all_method_disposition_schema")
        == all_method_disposition.get("schema")
        == "all-method-example-claim-disposition-audit-v1",
        "all-method disposition audit not carried into review",
    )
    checks.check(
        result_checks.get("all_method_disposition_status")
        == "all_nonlocal_method_example_rows_checked_common_reference_closed_source_policy_open",
        "all-method disposition audit status changed",
    )
    checks.check(
        result_checks.get("all_method_disposition_nonlocal_cells")
        == result_checks.get("all_method_disposition_expected_nonlocal_cells")
        == 40,
        "all-method disposition nonlocal cell count changed",
    )
    checks.check(result_checks.get("all_method_disposition_total_cells") == 44, "all-method total cell count changed")
    checks.check(
        result_checks.get("all_method_disposition_raw_rows_recomputed") == 132,
        "all-method raw recomputation count changed",
    )
    checks.check(
        result_checks.get("all_method_disposition_summary_mismatches") == 0,
        "all-method summary mismatch count changed",
    )
    checks.check(
        result_checks.get("all_method_disposition_order_wins")
        == result_checks.get("all_method_disposition_order_comparisons")
        == 40,
        "all-method order wins changed",
    )
    checks.check(
        result_checks.get("all_method_disposition_error_wins")
        == result_checks.get("all_method_disposition_error_comparisons")
        == 40,
        "all-method error wins changed",
    )
    checks.check(
        result_checks.get("all_method_disposition_source_policy_closed_rows") == 0,
        "all-method source-policy closed rows changed",
    )
    checks.check(
        result_checks.get("all_method_disposition_source_policy_open_rows") == 40,
        "all-method source-policy open rows changed",
    )
    checks.check(
        result_checks.get("all_method_disposition_flagged_nonlocal_rows") == 15,
        "all-method flagged nonlocal rows changed",
    )
    checks.check(
        result_checks.get("all_method_disposition_strict_external_error_rows") == 0,
        "all-method strict external error rows changed",
    )
    checks.check(
        result_checks.get("all_method_disposition_source_policy_superiority_allowed") is False,
        "all-method source-policy superiority boundary changed",
    )
    checks.check(
        result_checks.get("manuscript_includes_source_policy_diagnosis") is True,
        "manuscript missing source-policy diagnosis table",
    )
    checks.check(
        result_checks.get("pdf_text_includes_source_policy_diagnosis") is True,
        "PDF text missing source-policy diagnosis table",
    )
    checks.check(
        result_checks.get("manuscript_includes_all_example_source_policy_audit") is True,
        "manuscript missing all-example source-policy audit",
    )
    checks.check(
        result_checks.get("pdf_text_includes_all_example_source_policy_audit") is True,
        "PDF text missing all-example source-policy audit",
    )
    checks.check(
        result_checks.get("manuscript_includes_active_tfe_b2_smoke") is True,
        "manuscript missing active TFE B2 candidate smoke table",
    )
    checks.check(
        result_checks.get("pdf_text_includes_active_tfe_b2_smoke") is True,
        "PDF text missing active TFE B2 candidate smoke table",
    )
    checks.check(
        result_checks.get("manuscript_includes_tfe_full_t10_coarse_candidate") is True,
        "manuscript missing TFE full-T10 coarse candidate table",
    )
    checks.check(
        result_checks.get("pdf_text_includes_tfe_full_t10_coarse_candidate") is True,
        "PDF text missing TFE full-T10 coarse candidate table",
    )
    checks.check(
        result_checks.get("manuscript_includes_tfe_brown_mcphee_boundary") is True,
        "manuscript missing TFE Brown-McPhee source-policy boundary",
    )
    checks.check(
        result_checks.get("pdf_text_includes_tfe_brown_mcphee_boundary") is True,
        "PDF text missing TFE Brown-McPhee source-policy boundary",
    )
    checks.check(
        result_checks.get("manuscript_includes_tfe_appendix_b_certificate") is True,
        "manuscript missing TFE Appendix-B coefficient certificate boundary",
    )
    checks.check(
        result_checks.get("pdf_text_includes_tfe_appendix_b_certificate") is True,
        "PDF text missing TFE Appendix-B coefficient certificate boundary",
    )
    checks.check(
        result_checks.get("manuscript_includes_tfe_m3_formula_probe") is True,
        "manuscript missing TFE m=3 full-T10 formula-probe boundary",
    )
    checks.check(
        result_checks.get("pdf_text_includes_tfe_m3_formula_probe") is True,
        "PDF text missing TFE m=3 full-T10 formula-probe boundary",
    )
    checks.check(
        result_checks.get("manuscript_includes_minimal_reproducibility_boundary") is True,
        "manuscript missing minimal reproducibility package boundary",
    )
    checks.check(
        result_checks.get("pdf_text_includes_minimal_reproducibility_boundary") is True,
        "PDF text missing minimal reproducibility package boundary",
    )
    checks.check(
        result_checks.get("manuscript_includes_comparison_reconciliation") is True,
        "manuscript missing comparison reconciliation wording",
    )
    checks.check(
        result_checks.get("pdf_text_includes_comparison_reconciliation") is True,
        "PDF text missing comparison reconciliation wording",
    )
    checks.check(
        result_checks.get("all_examples_sanity_audit_schema") == "all-examples-result-sanity-audit-v1",
        "all-examples sanity audit not carried into review",
    )
    checks.check(result_checks.get("all_examples_audited") is True, "review missing all-examples audit coverage")
    checks.check(result_checks.get("all_examples_sanity_cell_count") == 44, "all-examples sanity cell count changed")
    checks.check(result_checks.get("all_examples_sanity_method_count") == 11, "all-examples sanity method count changed")
    checks.check(result_checks.get("all_examples_local_rows_passed") == 4, "local all-examples pass count changed")
    checks.check(result_checks.get("all_examples_local_rows_expected") == 4, "local all-examples expected count changed")
    checks.check(
        result_checks.get("all_examples_flagged_nonlocal_rows")
        == all_examples_audit.get("baseline_sanity", {}).get("flagged_nonlocal_count")
        == 15,
        "flagged nonlocal row count changed",
    )
    checks.check(
        set(result_checks.get("all_examples_flagged_examples", []))
        == {"single_pendulum", "double_pendulum", "four_link", "slider_crank"},
        "flagged examples do not cover all four examples",
    )
    checks.check(
        result_checks.get("all_examples_source_policy_recheck_required") is True,
        "source-policy recheck gate missing from review",
    )
    checks.check(
        result_checks.get("all_examples_external_superiority_allowed") is False,
        "all-examples external superiority boundary changed",
    )
    checks.check(
        result_checks.get("order_recomputation_audit_schema") == "common-reference-order-recomputation-audit-v1",
        "order recomputation audit not carried into review",
    )
    checks.check(
        result_checks.get("order_recomputation_all_summary_orders_recomputed") is True,
        "order recomputation did not verify all summary rows",
    )
    checks.check(result_checks.get("order_recomputation_cell_count") == 44, "order recomputation cell count changed")
    checks.check(result_checks.get("order_recomputation_raw_row_count") == 132, "order recomputation raw row count changed")
    checks.check(result_checks.get("order_recomputation_mismatch_count") == 0, "order recomputation mismatch count changed")
    checks.check(
        result_checks.get("order_recomputation_anomaly_rows")
        == recomputation_audit.get("anomalies", {}).get("anomaly_row_count")
        == 30,
        "order recomputation anomaly count changed",
    )
    checks.check(
        result_checks.get("order_recomputation_external_superiority_allowed") is False,
        "order recomputation external superiority boundary changed",
    )
    checks.check(
        result_checks.get("comparison_reconciliation_schema")
        == "comparison-objective-closure-reconciliation-v1",
        "comparison reconciliation audit not carried into review",
    )
    checks.check(
        result_checks.get("comparison_reconciliation_status")
        == "common_reference_objective_closed_source_policy_reproduction_open",
        "comparison reconciliation status changed",
    )
    checks.check(
        result_checks.get("comparison_matrix_closed") is True,
        "comparison matrix closure not carried into review",
    )
    checks.check(
        result_checks.get("common_reference_claim_allowed") is True,
        "common-reference claim boundary changed",
    )
    checks.check(
        result_checks.get("source_policy_superiority_claim_allowed") is False,
        "source-policy superiority boundary changed",
    )
    checks.check(
        result_checks.get("comparison_reconciliation_direct_order_wins")
        == result_checks.get("comparison_reconciliation_direct_order_comparisons")
        == comparison_reconciliation.get("direct_nonlocal_velocity_order_comparisons")
        == 40,
        "comparison reconciliation order win count changed",
    )
    checks.check(
        result_checks.get("comparison_reconciliation_direct_error_wins")
        == result_checks.get("comparison_reconciliation_direct_error_comparisons")
        == comparison_reconciliation.get("direct_nonlocal_finest_velocity_error_comparisons")
        == 40,
        "comparison reconciliation error win count changed",
    )
    checks.check(
        result_checks.get("comparison_reconciliation_required_methods_resolved") is True,
        "comparison reconciliation method resolution changed",
    )
    checks.check(
        result_checks.get("comparison_reconciliation_b2_b4_can_close_now") is False,
        "comparison reconciliation B2/B4 boundary changed",
    )
    checks.check(
        result_checks.get("common_reference_traceability_rows") == 44,
        "review agent common-reference traceability row count changed",
    )
    checks.check(
        result_checks.get("common_reference_traceability_total_rows") == 44,
        "review agent common-reference traceability total row count changed",
    )
    checks.check(
        result_checks.get("source_policy_apples_to_apples_external_rows") == 0,
        "review agent source-policy apples-to-apples row count changed",
    )
    checks.check(
        result_checks.get("source_policy_apples_to_apples_external_total_rows") == 40,
        "review agent source-policy apples-to-apples total row count changed",
    )
    checks.check(result_checks.get("global_policy_passed") is True, "global policy audit not carried into review")
    checks.check(result_checks.get("global_policy_passed_count") == result_checks.get("global_policy_row_count") == 14, "global policy count changed")
    checks.check(result_checks.get("mixed_policy_direct_error_rows") == 0, "mixed-policy direct-error gate changed")
    checks.check(result_checks.get("paper_direct_error_rows_allowed") == 0, "paper direct-error gate changed")
    checks.check(result_checks.get("paper_direct_error_superiority_allowed") is False, "paper direct-error superiority boundary changed")
    checks.check(result_checks.get("source_policy_reproduction") is False, "source-policy boundary changed")
    checks.check(result_checks.get("public_code_fixed_grid_replay") is True, "fixed-grid replay boundary changed")
    checks.check(
        result_checks.get("visual_legibility_schema")
        == visual_legibility.get("schema")
        == "cmame-visual-legibility-audit-v1",
        "visual legibility audit not carried into review",
    )
    checks.check(
        result_checks.get("visual_legibility_status")
        == "b5_closed_mechanism_visual_reproducibility_checked",
        "visual legibility status changed",
    )
    checks.check(result_checks.get("visual_legibility_b5_closed") is True, "B5 visual closure not recorded")
    checks.check(result_checks.get("visual_legibility_b7_open") is True, "B7 visual blocker boundary changed")
    checks.check(result_checks.get("visual_main_figure_width_px") == 2028, "visual main figure width changed")
    checks.check(result_checks.get("visual_main_figure_height_px") == 1759, "visual main figure height changed")
    checks.check(result_checks.get("visual_flat_figure_width_px") == 2028, "visual flat figure width changed")
    checks.check(result_checks.get("visual_flat_figure_height_px") == 1759, "visual flat figure height changed")
    checks.check(result_checks.get("visual_pdf_captions_present") is True, "visual PDF captions missing")
    checks.check(result_checks.get("visual_latex_logs_clean") is True, "visual latex log cleanliness changed")
    checks.check(
        result_checks.get("figure_set_schema")
        == figure_set.get("schema")
        == "cmame-figure-set-audit-v1",
        "figure-set audit not carried into review",
    )
    checks.check(
        result_checks.get("figure_set_status")
        == "b7_figure_set_closed_narrowed_common_reference_diagnostic_scope",
        "figure-set audit status changed",
    )
    checks.check(result_checks.get("figure_set_count") == result_checks.get("figure_set_expected_count") == 13, "figure-set count changed")
    checks.check(result_checks.get("figure_set_all_available") is True, "figure-set files missing")
    checks.check(result_checks.get("figure_set_all_integrated") is True, "figure-set TeX integration missing")
    checks.check(result_checks.get("figure_set_all_pdf_captions") is True, "figure-set PDF captions missing")
    checks.check(result_checks.get("figure_set_all_legible_dimensions") is True, "figure-set dimensions changed")
    checks.check(result_checks.get("figure_set_figure12_integrated") is True, "Figure 12 integration not recorded")
    checks.check(result_checks.get("figure_set_figure13_integrated") is True, "Figure 13 integration not recorded")
    checks.check(result_checks.get("figure_set_b7_closed") is True, "figure-set audit did not close B7")
    checks.check(result_checks.get("figure_set_source_policy_rows_closed") == 0, "figure-set source-policy rows changed")
    checks.check(result_checks.get("figure_set_source_policy_rows_total") == 40, "figure-set source-policy total changed")
    figure_preflight = figure_set.get("b7_closure_readiness_preflight", {})
    checks.check(
        result_checks.get("figure_set_b7_preflight_status")
        == figure_preflight.get("status")
        == "b7_narrowed_diagnostic_common_reference_figure_scope_closed",
        "B7 preflight status not carried into review",
    )
    checks.check(
        result_checks.get("figure_set_b7_preflight_closed_preconditions")
        == figure_preflight.get("closed_precondition_count")
        == 13,
        "B7 preflight precondition count not carried into review",
    )
    checks.check(
        result_checks.get("figure_set_b7_preflight_open_dependencies")
        == figure_preflight.get("open_dependency_count")
        == 0,
        "B7 preflight dependency count not carried into review",
    )
    checks.check(
        result_checks.get("figure_set_b7_preflight_closure_allowed")
        == figure_preflight.get("b7_closure_allowed_now")
        is True,
        "B7 preflight did not close review",
    )
    post_b4_figure_plan = figure_set.get("post_b4_figure_scope_plan", {})
    checks.check(
        result_checks.get("figure_set_post_b4_plan_status")
        == post_b4_figure_plan.get("status")
        == "post_b4_source_policy_reintroduction_plan_ready_current_b7_closed",
        "B7 post-B4 figure plan status not carried into review",
    )
    checks.check(
        result_checks.get("figure_set_post_b4_plan_retain_figures")
        == post_b4_figure_plan.get("retain_after_caption_recheck_figures")
        == [1, 2, 3, 4, 5, 6, 7, 10, 11],
        "B7 post-B4 retained figure list not carried into review",
    )
    checks.check(
        result_checks.get("figure_set_post_b4_plan_claim_refresh_figures")
        == post_b4_figure_plan.get("claim_boundary_refresh_figures_after_b4")
        == [8, 12],
        "B7 post-B4 claim-refresh figure list not carried into review",
    )
    checks.check(
        result_checks.get("figure_set_post_b4_plan_rebuild_figures")
        == post_b4_figure_plan.get("blocking_source_policy_rebuild_figures")
        == [9, 13],
        "B7 post-B4 blocking rebuild figure list not carried into review",
    )
    checks.check(
        result_checks.get("figure_set_post_b4_plan_source_policy_dependent_count")
        == post_b4_figure_plan.get("source_policy_dependent_figure_count")
        == 4,
        "B7 post-B4 source-policy dependent figure count not carried into review",
    )
    checks.check(
        result_checks.get("figure_set_post_b4_plan_closure_allowed")
        == post_b4_figure_plan.get("b7_closure_allowed_by_this_plan_now")
        is False,
        "B7 post-B4 plan overcloses review",
    )
    ready_boundary = post_b4_figure_plan.get("ready_command_coverage_boundary", {})
    checks.check(
        result_checks.get("figure_set_post_b4_ready_command_mapped_rows")
        == ready_boundary.get("ready_command_mapped_external_rows")
        == 20,
        "B7 post-B4 ready-command mapped rows not carried into review",
    )
    checks.check(
        result_checks.get("figure_set_post_b4_unaddressed_rows")
        == ready_boundary.get("unaddressed_external_rows_after_ready_commands")
        == 0,
        "B7 post-B4 unaddressed rows not carried into review",
    )
    checks.check(
        result_checks.get("figure_set_post_b4_not_ready_lanes")
        == ready_boundary.get("not_ready_lanes_after_ready_commands")
        == ["tfe_source_policy_work_precision", "vp2024_source_code_path_work_precision"],
        "B7 post-B4 not-ready lanes not carried into review",
    )
    checks.check(
        result_checks.get("figure_set_post_b4_ready_commands_close_b4_b7")
        == [
            ready_boundary.get("ready_commands_alone_can_close_b4"),
            ready_boundary.get("ready_commands_alone_can_close_b7"),
        ]
        == [False, False],
        "B7 post-B4 ready-command closure boundary not carried into review",
    )
    checks.check(result_checks.get("figure_set_external_superiority_allowed") is False, "figure-set audit overclaims external superiority")
    checks.check(
        result_checks.get("prose_residue_schema")
        == prose_residue.get("schema")
        == "cmame-prose-residue-audit-v1",
        "prose residue audit not carried into review",
    )
    checks.check(
        result_checks.get("prose_residue_status")
        == "main_body_machine_tokens_removed_reproducibility_appendix_compacted_b6_closed_under_narrowed_policy",
        "prose residue status changed",
    )
    checks.check(result_checks.get("prose_main_body_machine_token_count") == 0, "main prose machine-token count changed")
    checks.check(
        result_checks.get("prose_flat_main_body_machine_token_count") == 0,
        "flat prose machine-token count changed",
    )
    checks.check(
        result_checks.get("prose_artifact_filenames_confined_to_appendix") is True,
        "prose artifact confinement changed",
    )
    checks.check(
        result_checks.get("prose_reader_facing_claim_language_preserved") is True,
        "reader-facing prose boundary changed",
    )
    checks.check(result_checks.get("prose_b6_closed") is True, "B6 should close under narrowed policy in prose audit")
    checks.check(result_checks.get("prose_appendix_artifact_macro_count") == 0, "appendix artifact macro count changed")
    prose_preflight = prose_residue.get("b6_closure_readiness_preflight", {})
    checks.check(
        result_checks.get("prose_b6_preflight_status")
        == prose_preflight.get("status")
        == "b6_final_prose_pass_closed_under_narrowed_b4_b7_scope",
        "B6 preflight status not carried into review",
    )
    checks.check(
        result_checks.get("prose_b6_preflight_closed_preconditions")
        == prose_preflight.get("closed_precondition_count")
        == 11,
        "B6 preflight precondition count not carried into review",
    )
    checks.check(
        result_checks.get("prose_b6_preflight_open_dependencies")
        == prose_preflight.get("open_dependency_count")
        == 0,
        "B6 preflight open dependency count not carried into review",
    )
    checks.check(
        result_checks.get("prose_b6_preflight_closure_allowed")
        == prose_preflight.get("b6_closure_allowed_now")
        is True,
        "B6 preflight did not close under narrowed policy in review",
    )
    prose_ready_boundary = prose_residue.get("post_baseline_final_prose_dependency", {}).get(
        "ready_command_dependency_boundary", {}
    )
    checks.check(
        result_checks.get("prose_b6_ready_command_mapped_rows")
        == prose_ready_boundary.get("ready_command_mapped_external_rows")
        == 20,
        "B6 ready-command mapped rows not carried into review",
    )
    checks.check(
        result_checks.get("prose_b6_ready_command_unaddressed_rows")
        == prose_ready_boundary.get("unaddressed_external_rows_after_ready_commands")
        == 0,
        "B6 ready-command unaddressed rows not carried into review",
    )
    checks.check(
        result_checks.get("prose_b6_ready_command_not_ready_lanes")
        == prose_ready_boundary.get("not_ready_lanes_after_ready_commands")
        == ["tfe_source_policy_work_precision", "vp2024_source_code_path_work_precision"],
        "B6 ready-command not-ready lanes not carried into review",
    )
    checks.check(
        result_checks.get("prose_b6_ready_commands_enable_final_prose")
        == prose_ready_boundary.get("ready_commands_alone_can_enable_b6_final_prose_pass")
        is False,
        "B6 ready-command boundary incorrectly enables final prose in review",
    )
    prose_post_boundary = prose_residue.get("post_baseline_final_prose_dependency", {}).get(
        "post_execution_dependency_boundary", {}
    )
    prose_post_authorized = prose_post_boundary.get("verified_authorized_execution_recorded") is True
    expected_prose_post_status = (
        "verified_authorized_execution_zero_promoted_rows_source_policy_excluded_final_prose_enabled"
        if prose_post_authorized
        else "existing_artifacts_present_no_verified_authorized_execution_zero_promoted_rows_source_policy_excluded_final_prose_enabled"
    )
    expected_review_safe_prose_post_status = (
        "verified_authorized_execution_zero_promoted_rows_source_policy_excluded_full_source_policy_final_prose_not_enabled"
        if prose_post_authorized
        else "existing_artifacts_present_no_verified_authorized_execution_zero_promoted_rows_source_policy_excluded_full_source_policy_final_prose_not_enabled"
    )
    checks.check(
        prose_post_boundary.get("status") == expected_prose_post_status,
        "B6 source post-execution dependency status changed",
    )
    checks.check(
        result_checks.get("prose_b6_post_execution_status") == expected_review_safe_prose_post_status,
        "B6 review-safe post-execution dependency status not recorded",
    )
    checks.check(
        result_checks.get("prose_b6_post_execution_promoted_rows")
        == prose_post_boundary.get("source_policy_rows_promoted_after_driver")
        == 0,
        "B6 post-execution promoted rows not carried into review",
    )
    checks.check(
        result_checks.get("prose_b6_post_execution_total_rows")
        == prose_post_boundary.get("source_policy_rows_total")
        == 40,
        "B6 post-execution total rows not carried into review",
    )
    checks.check(
        result_checks.get("prose_b6_post_execution_close_b4_b7")
        == [
            prose_post_boundary.get("b4_can_close_now"),
            prose_post_boundary.get("b7_can_close_now"),
        ]
        == [False, False],
        "B6 post-execution B4/B7 closure boundary not carried into review",
    )
    checks.check(
        result_checks.get("prose_b6_post_execution_enable_final_prose")
        == prose_post_boundary.get("final_prose_pass_enabled_by_post_execution")
        is False,
        "B6 post-execution boundary incorrectly enables final prose in review",
    )
    proof_relocation = prose_residue.get("proof_prose_relocation_pass", {})
    checks.check(
        result_checks.get("prose_proof_relocation_status")
        == proof_relocation.get("status")
        == "finite_solver_probe_details_relocated_from_proof_boundary_b6_closed_under_narrowed_policy",
        "B6 proof-prose relocation status not carried into review",
    )
    checks.check(
        result_checks.get("prose_proof_relocation_strict_boundary_preserved")
        == proof_relocation.get("strict_proof_boundary_preserved")
        is True,
        "B6 proof-prose relocation strict-boundary marker missing in review",
    )
    checks.check(
        result_checks.get("prose_proof_relocation_b6_closed")
        == proof_relocation.get("b6_closed_by_this_pass")
        is False,
        "B6 proof-prose relocation overcloses review",
    )
    claim_hygiene_checks = report.get("claim_hygiene_checks", {})
    checks.check(
        claim_hygiene_checks.get("schema") == "cmame-claim-hygiene-audit-v1",
        "claim-hygiene audit not carried into review",
    )
    checks.check(claim_hygiene_checks.get("status") == "pass", "claim-hygiene audit not passing in review")
    checks.check(
        claim_hygiene_checks.get("allowed_claim")
        == claim_hygiene.get("claim_boundary", {}).get("allowed_claim")
        == "conditional_formal_order_comparison",
        "claim-hygiene allowed claim changed",
    )
    checks.check(claim_hygiene_checks.get("accepted_method") == "Gauss6/FullVA", "claim-hygiene method changed")
    checks.check(claim_hygiene_checks.get("accepted_method_order") == 6, "claim-hygiene method order changed")
    checks.check(claim_hygiene_checks.get("comparator_expected_order") == 5, "claim-hygiene comparator order changed")
    checks.check(claim_hygiene_checks.get("required_missing_count") == 0, "claim-hygiene missing text count changed")
    checks.check(
        claim_hygiene_checks.get("submission_forbidden_hit_count") == 0,
        "claim-hygiene submission forbidden hits changed",
    )
    checks.check(
        claim_hygiene_checks.get("support_forbidden_hit_count") == 0,
        "claim-hygiene support forbidden hits changed",
    )
    checks.check(
        claim_hygiene_checks.get("source_policy_superiority_claim_allowed") is False,
        "claim-hygiene source-policy superiority changed",
    )
    checks.check(
        claim_hygiene_checks.get("external_superiority_claim") is False,
        "claim-hygiene external superiority changed",
    )
    checks.check(claim_hygiene_checks.get("default_1e_4_required") is False, "claim-hygiene default 1e-4 changed")
    checks.check(claim_hygiene_checks.get("run_v047_invoked") is False, "claim-hygiene invoked run_v047")
    checks.check(
        claim_hygiene_checks.get("heavy_numerical_run_invoked") is False,
        "claim-hygiene invoked heavy run",
    )
    code_hygiene_checks = report.get("code_hygiene_checks", {})
    paper_code_inventory = python_inventory(PAPER)
    v048_code_inventory = python_inventory(PAPER.parent / "v048_cross_paper_same_test_benchmarks")
    combined_python_line_count = paper_code_inventory["line_count"] + v048_code_inventory["line_count"]
    checks.check(
        code_hygiene_checks.get("schema") == "cmame-code-hygiene-review-v1",
        "code-hygiene review not carried into report",
    )
    checks.check(
        code_hygiene_checks.get("status") == "research_audit_repository_not_minimal_submission_code",
        "code-hygiene status changed",
    )
    checks.check(
        code_hygiene_checks.get("paper_python_file_count") == paper_code_inventory["file_count"],
        "paper Python file count stale",
    )
    checks.check(
        code_hygiene_checks.get("paper_python_line_count") == paper_code_inventory["line_count"],
        "paper Python line count stale",
    )
    checks.check(
        code_hygiene_checks.get("paper_python_prefix_counts") == paper_code_inventory["prefix_counts"],
        "paper Python prefix inventory stale",
    )
    checks.check(
        code_hygiene_checks.get("v048_python_file_count") == v048_code_inventory["file_count"],
        "v048 Python file count stale",
    )
    checks.check(
        code_hygiene_checks.get("v048_python_line_count") == v048_code_inventory["line_count"],
        "v048 Python line count stale",
    )
    checks.check(
        code_hygiene_checks.get("v048_python_prefix_counts") == v048_code_inventory["prefix_counts"],
        "v048 Python prefix inventory stale",
    )
    checks.check(
        code_hygiene_checks.get("combined_python_line_count") == combined_python_line_count,
        "combined Python line count stale",
    )
    checks.check(
        code_hygiene_checks.get("research_audit_primary_submission_line_limit") == 20000,
        "research-audit primary-submission line limit changed",
    )
    checks.check(
        code_hygiene_checks.get("research_audit_repo_too_large_for_primary_submission")
        is (combined_python_line_count > 20000),
        "research-audit primary-submission size risk changed",
    )
    checks.check(
        code_hygiene_checks.get("research_audit_repo_primary_submission_allowed") is False,
        "research audit repo must not be the primary submission code package",
    )
    checks.check(
        code_hygiene_checks.get("research_audit_repo_provenance_only") is True,
        "research audit repo provenance-only boundary missing",
    )
    checks.check(
        code_hygiene_checks.get("reviewer_facing_python_line_limit") == 2000,
        "reviewer-facing Python line limit changed",
    )
    checks.check(
        code_hygiene_checks.get("reviewer_facing_python_file_limit") == 12,
        "reviewer-facing Python file limit changed",
    )
    checks.check(
        code_hygiene_checks.get("minimal_reproducible_submission_code_ready") is False,
        "review agent must not mark minimal submission code ready",
    )
    checks.check(
        code_hygiene_checks.get("minimal_reproducibility_candidate_present") is True,
        "minimal reproducibility candidate not carried into review",
    )
    checks.check(
        code_hygiene_checks.get("minimal_reproducibility_candidate_schema")
        == minimal_candidate.get("schema")
        == "cmame-minimal-reproducibility-candidate-v1",
        "minimal reproducibility candidate schema changed in review",
    )
    checks.check(
        code_hygiene_checks.get("minimal_reproducibility_candidate_status")
        == minimal_candidate.get("status")
        == "candidate_replay_package_built_not_submission_ready",
        "minimal reproducibility candidate status changed in review",
    )
    checks.check(
        code_hygiene_checks.get("minimal_reproducibility_candidate_submission_ready") is False,
        "minimal reproducibility candidate must not be submission ready",
    )
    checks.check(
        code_hygiene_checks.get("minimal_reproducibility_candidate_file_count")
        == minimal_candidate.get("candidate_file_count")
        == 10,
        "minimal reproducibility candidate file count changed",
    )
    checks.check(
        code_hygiene_checks.get("minimal_reproducibility_candidate_python_lines")
        == minimal_candidate.get("candidate_python_line_count"),
        "minimal reproducibility candidate Python line count changed",
    )
    checks.check(
        code_hygiene_checks.get("minimal_reproducibility_candidate_python_file_count")
        == minimal_candidate.get("candidate_python_file_count")
        == 1,
        "minimal reproducibility candidate Python file count changed",
    )
    checks.check(
        code_hygiene_checks.get("minimal_reproducibility_candidate_code_size_ok") is True,
        "minimal candidate should remain within reviewer-facing size limits",
    )
    checks.check(
        code_hygiene_checks.get("minimal_reproducibility_candidate_source_policy_closed_rows") == 0,
        "minimal reproducibility candidate overcloses source-policy rows",
    )
    checks.check(
        code_hygiene_checks.get("minimal_reproducibility_candidate_source_policy_total_rows") == 40,
        "minimal reproducibility candidate source-policy total changed",
    )
    checks.check(
        code_hygiene_checks.get("minimal_reproducibility_candidate_proof_gap_closed") is True,
        "minimal reproducibility candidate lost proof closure",
    )
    checks.check(
        code_hygiene_checks.get("minimal_reproducibility_candidate_replay_only") is True,
        "minimal reproducibility candidate replay-only marker missing",
    )
    checks.check(
        code_hygiene_checks.get("minimal_reproducibility_candidate_runner_centered") is False,
        "minimal reproducibility candidate unexpectedly runner-centered",
    )
    checks.check(
        code_hygiene_checks.get("local_runner_centered_candidate_ready")
        == runner_centered.get("local_runner_centered_candidate_ready")
        is True,
        "local runner-centered candidate readiness missing from review",
    )
    checks.check(
        code_hygiene_checks.get("full_source_policy_runner_package_ready")
        == runner_centered.get("full_source_policy_runner_package_ready")
        is False,
        "full source-policy runner package overclaimed in review",
    )
    checks.check(
        code_hygiene_checks.get("runner_centered_audit_status")
        == runner_centered.get("status")
        == "local_runner_centered_candidate_ready_source_policy_package_open",
        "runner-centered audit status stale in review",
    )
    checks.check(
        code_hygiene_checks.get("minimal_reproducibility_candidate_source_policy_ready") is False,
        "minimal reproducibility candidate unexpectedly source-policy ready",
    )
    checks.check(
        code_hygiene_checks.get("minimal_reproducibility_candidate_proof_ready") is True,
        "minimal reproducibility candidate proof-ready marker missing",
    )
    minimal_submission_code_boundary = code_hygiene_checks.get(
        "minimal_submission_code_dependency_boundary", {}
    )
    checks.check(
        minimal_submission_code_boundary.get("schema")
        == "minimal-submission-code-dependency-boundary-v1"
        and minimal_submission_code_boundary.get("status")
        == "narrowed_repro_ready_full_source_policy_package_blocked"
        and minimal_submission_code_boundary.get("minimal_reproducible_submission_code_ready") is False,
        "minimal submission code dependency boundary status changed in review",
    )
    checks.check(
        minimal_submission_code_boundary.get("candidate_code_size_ok") is True
        and minimal_submission_code_boundary.get("candidate_replay_only") is True
        and minimal_submission_code_boundary.get("candidate_runner_centered") is False
        and minimal_submission_code_boundary.get("candidate_source_policy_ready") is False
        and minimal_submission_code_boundary.get("candidate_proof_ready") is True,
        "minimal submission code dependency boundary candidate flags changed in review",
    )
    checks.check(
        minimal_submission_code_boundary.get("local_runner_centered_candidate_ready") is True
        and minimal_submission_code_boundary.get("narrowed_repro_code_archive_ready") is True
        and minimal_submission_code_boundary.get("narrowed_repro_code_archive_submission_ready") is False
        and minimal_submission_code_boundary.get("full_source_policy_runner_package_ready") is False
        and minimal_submission_code_boundary.get("source_policy_rows_closed") == 0
        and minimal_submission_code_boundary.get("source_policy_rows_total") == 40,
        "minimal submission code dependency boundary runner/source-policy flags changed in review",
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
        and minimal_submission_code_boundary.get("primary_submission_package_allowed") is False,
        "minimal submission code dependency boundary blockers changed in review",
    )
    checks.check(
        code_hygiene_checks.get("research_audit_repo_useful") is True,
        "review agent lost research-audit repo usefulness boundary",
    )
    checks.check(
        code_hygiene_checks.get("paper_core_result_table_ready") is True,
        "paper core result table should remain ready",
    )
    checks.check(
        code_hygiene_checks.get("code_bloat_risk_for_submission") is True,
        "code-bloat risk should remain until a runner-centered minimal package is ready",
    )
    checks.check(
        code_hygiene_checks.get("ra2021_public_baselines_present") is True,
        "RA2021 baseline availability missing from code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("hi2022_bounded_rows_present") is True,
        "HI2022 bounded row availability missing from code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_policy_runner_implemented") is False,
        "TFE runner boundary changed",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_parameter_model_implemented") is True,
        "TFE source pendulum parameter model missing from code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_frictionless_smoke_implemented") is True,
        "TFE source pendulum smoke layer missing from code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_absolute_coordinate_dae_residual_smoke_implemented")
        is True,
        "TFE absolute-coordinate residual smoke missing from code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_source_policy_dae_runner_equivalent") is False,
        "TFE source-policy DAE runner equivalence overclaimed in code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_source_output_time_integration_smoke_implemented")
        is True,
        "TFE source-output time-integration smoke missing from code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_source_policy_time_integration_runner_equivalent")
        is False,
        "TFE source-policy time-integration equivalence overclaimed in code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_source_reference_solution_policy_smoke_implemented")
        is True,
        "TFE source reference-policy smoke missing from code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_source_reference_solution_policy_smoke_full_T10")
        is False,
        "TFE source reference-policy smoke overclaims full T=10 run in code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_implemented")
        is True,
        "TFE full T=10 source-reference probe missing from code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_completed")
        is True,
        "TFE full T=10 source-reference probe not marked completed in code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_rows_completed")
        == 0,
        "TFE full T=10 source-reference probe overcloses source-policy rows in code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_steps")
        == 100000,
        "TFE full T=10 source-reference probe source-step count changed in code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_check_steps")
        == 200000,
        "TFE full T=10 source-reference probe check-step count changed in code-hygiene review",
    )
    checks.check(
        float(
            code_hygiene_checks.get(
                "tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_coordinate_error"
            )
        )
        < 1.0e-10,
        "TFE full T=10 source-reference coordinate check error too large in code-hygiene review",
    )
    checks.check(
        float(
            code_hygiene_checks.get(
                "tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_velocity_error"
            )
        )
        < 1.0e-10,
        "TFE full T=10 source-reference velocity check error too large in code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_source_comparator_candidate_runners_implemented")
        is True,
        "TFE source comparator candidate runners missing from code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_newmark_beta_candidate_runner_smoke_implemented")
        is True,
        "TFE Newmark-beta candidate runner smoke missing from code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_trapezoidal_candidate_runner_smoke_implemented")
        is True,
        "TFE trapezoidal candidate runner smoke missing from code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_source_policy_method_runner_equivalent")
        is False,
        "TFE source-policy method-runner equivalence overclaimed in code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_tfe_m1_m2_m3_candidate_runner_smoke_implemented")
        is True,
        "TFE m=1/2/3 candidate runner smoke missing from code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_appendix_b_coefficient_certificate_checked")
        is True,
        "TFE Appendix-B coefficient certificate missing from code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_appendix_b_coefficient_certificate_rows") == 3,
        "TFE Appendix-B coefficient certificate row count changed in code-hygiene review",
    )
    checks.check(
        float(code_hygiene_checks.get("tfe_source_pendulum_appendix_b_coefficient_certificate_max_abs_diff")) <= 1.0e-14,
        "TFE Appendix-B coefficient certificate mismatch too large in code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_tfe_m1_m2_m3_source_policy_runners_implemented")
        is False,
        "TFE m=1/2/3 source-policy runners unexpectedly implemented in code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_gauss6_candidate_smoke_implemented") is True,
        "Gauss6 source-pendulum candidate smoke missing from code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get(
            "tfe_source_pendulum_gauss6_absolute_coordinate_source_policy_runner_implemented"
        )
        is False,
        "Gauss6 source-policy runner unexpectedly implemented in code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_gauss6_candidate_rows") == 2,
        "Gauss6 source-pendulum candidate row count changed in code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_gauss6_candidate_source_policy_rows_completed") == 0,
        "Gauss6 source-pendulum candidate overcloses source-policy rows in code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_gauss6_candidate_method_equivalent") is False,
        "Gauss6 source-pendulum candidate overclaims method equivalence in code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get(
            "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_implemented"
        )
        is True
        and code_hygiene_checks.get(
            "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_full_T10"
        )
        is True
        and code_hygiene_checks.get(
            "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_reference_invoked"
        )
        is True
        and code_hygiene_checks.get(
            "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_source_policy_rows"
        )
        == 0
        and code_hygiene_checks.get(
            "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_method_equivalent"
        )
        is False,
        "active-B2 source-reference full-T10 probe boundary changed in code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_bounded_source_policy_runner_smoke_implemented")
        is True,
        "bounded source-policy runner smoke missing from code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_bounded_source_policy_runner_rows") == 4,
        "bounded source-policy runner row count changed in code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_bounded_source_policy_runner_full_T10") is False,
        "bounded source-policy runner overclaims full T=10 in code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_bounded_source_policy_runner_source_policy_rows_completed") == 0,
        "bounded source-policy runner overcloses rows in code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_active_b2_candidate_row_smoke_implemented")
        is True,
        "active B2 candidate row smoke missing from code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_active_b2_candidate_row_smoke_full_T10")
        is False,
        "active B2 smoke overclaims full T=10 in code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_active_b2_source_policy_rows_completed") == 0,
        "active B2 smoke overcloses rows in code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_active_b2_full_T10_coarse_probe_implemented")
        is True,
        "active B2 full T=10 coarse probe missing from code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_active_b2_full_T10_coarse_probe_full_T10")
        is True,
        "active B2 full T=10 coarse probe not full horizon in code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_active_b2_full_T10_coarse_probe_source_policy_rows") == 0,
        "active B2 full T=10 coarse probe overcloses source-policy rows in code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_active_b2_full_T10_coarse_probe_finite_rows") == 4,
        "active B2 full T=10 coarse probe finite row count changed in code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_active_b2_full_T10_coarse_probe_residual_ok_rows") == 4,
        "active B2 full T=10 coarse probe residual row count changed in code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_active_b2_full_T10_coarse_probe_reference_invoked")
        is False,
        "active B2 full T=10 coarse probe invoked source-policy reference in code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_tfe_m3_full_T10_formula_probe_implemented")
        is True,
        "TFE m=3 full T=10 formula probe missing from code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_tfe_m3_full_T10_formula_probe_full_T10")
        is True,
        "TFE m=3 full T=10 formula probe not full horizon in code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_tfe_m3_full_T10_formula_probe_expected_order") == 5,
        "TFE m=3 full T=10 formula probe expected order changed in code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_tfe_m3_full_T10_formula_probe_source_policy_rows") == 0,
        "TFE m=3 full T=10 formula probe overcloses source-policy rows in code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_tfe_m3_full_T10_formula_probe_finite_rows") == 1,
        "TFE m=3 full T=10 formula probe finite row count changed in code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_tfe_m3_full_T10_formula_probe_residual_ok_rows") == 1,
        "TFE m=3 full T=10 formula probe residual row count changed in code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_tfe_m3_full_T10_formula_probe_reference_invoked")
        is False,
        "TFE m=3 full T=10 formula probe invoked source-policy reference in code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_active_b2_candidate_row_count") == 4,
        "active B2 smoke row count changed in code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_error_output_policy_encoded") is True,
        "TFE source pendulum output policy missing from code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_brown_mcphee_candidate_friction_law_encoded") is True,
        "TFE candidate friction law missing from code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_brown_mcphee_source_text_anchor_found") is True,
        "TFE Brown--McPhee source-text anchor missing from code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_brown_mcphee_published_formula_structure_encoded") is True,
        "TFE Brown--McPhee formula structure missing from code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_brown_mcphee_source_code_equivalent_law") is False,
        "TFE Brown--McPhee source-code equivalence overclaimed in code-hygiene review",
    )
    checks.check(
        code_hygiene_checks.get("tfe_source_pendulum_frictional_candidate_smoke_implemented") is True,
        "TFE frictional candidate smoke missing from code-hygiene review",
    )
    checks.check(code_hygiene_checks.get("source_policy_closed_rows") == 0, "source-policy closed rows changed")
    checks.check(code_hygiene_checks.get("source_policy_total_rows") == 40, "source-policy total rows changed")
    for token in [
        "## Code Hygiene Checks",
        "Reviewer-facing code policy: primary supplement limit `12` Python files / `2000` lines; research-audit tree is provenance-only `True` and primary-submission allowed `False`.",
        "Research-audit primary-package risk: over `20000` lines `True`; code-bloat risk remains `True` until the full source-policy runner package is ready.",
        "Minimal reproducible submission code ready: `False`",
        "Minimal reproducibility candidate: present `True`, status `candidate_replay_package_built_not_submission_ready`, files `10`",
        "Minimal reproducibility candidate boundary: source-policy `0/40`, direct-PC2 route closed under retained theorem interfaces `True`, replay-only `True`, runner-centered `False`.",
        "Minimal submission code dependency boundary: `narrowed_repro_ready_full_source_policy_package_blocked`; safe use `narrowed_claim_replay_and_audit_provenance_only`; blockers `OC4_source_policy_reproduction_rows,OC6_TFE_source_policy_runner,OC12_full_source_policy_runner_archive`.",
        "Local accepted-row runner/full source-policy runner ready: `True/False`; runner audit `local_runner_centered_candidate_ready_source_policy_package_open`.",
        "source-policy rows closed `0/40`",
        "TFE source-policy runner implemented `False`",
        "TFE source pendulum parameter/smoke/absolute-residual/time-smoke/output/candidate friction: `True/True/True/True/True/True`",
        "TFE source pendulum bounded reference-policy smoke/full T=10 source run: `True/False`",
        "TFE source pendulum full-T=10 source-reference feasibility probe: implemented/completed/source-policy rows `True/True/0`; source/check steps `100000/200000`; coordinate/velocity check errors `3.819e-14/2.485e-13`.",
        "TFE source pendulum comparator candidate runners/Newmark/trapezoidal/TFE-m-candidate/method-equivalent/TFE m=1-3 source-policy: `True/True/True/True/False/False`",
        "TFE source pendulum Gauss6 candidate smoke/absolute-coordinate source-policy runner: `True/False`",
        "TFE source pendulum Gauss6 candidate rows/source-policy rows/method-equivalent: `2/0/False`",
        "TFE source pendulum Appendix-B coefficient certificate: `True`; rows/max diff `3/0.000e+00`",
        "TFE source pendulum unified bounded runner rows/full T=10/source-policy rows: `4/False/0`",
        "TFE source pendulum active-B2 candidate rows/full T=10/source-policy rows: `4/False/0`",
        "TFE source pendulum active-B2 full-T10 coarse probe: implemented/fullT10/source-policy rows/finite/residual-ok/source-ref-invoked `True/True/0/4/4/False`",
        "TFE source pendulum active-B2 source-reference full-T10 probe: implemented/fullT10/reference-invoked/source-policy rows/finite/residual-ok/method-equivalent `True/True/True/0/4/4/False`",
        "TFE source pendulum m=3 full-T10 formula probe: implemented/fullT10/expected/source-policy rows/finite/residual-ok/source-ref-invoked `True/True/5/0/1/1/False`",
        "research/audit repository rather than a minimal reproducible submission package",
    ]:
        checks.check(token in report_md, f"review report missing code-hygiene token: {token}")
    checks.check(
        "Minimal reproducibility candidate boundary: source-policy `0/40`, proof gap closed `True`" not in report_md,
        "stale broad proof-gap label remains in review-agent code-hygiene section",
    )
    closeout_checks = report.get("closeout_actionability_checks", {})
    ordered_gates = closeout_checks.get("ordered_gates", [])
    checks.check(
        closeout_checks.get("schema") == "cmame-closeout-actionability-v1",
        "closeout actionability schema missing",
    )
    checks.check(
        closeout_checks.get("status") == "future_full_source_policy_reintroduction_after_narrowed_claim_closure",
        "closeout actionability status changed",
    )
    checks.check(closeout_checks.get("submission_ready") is False, "closeout actionability overclaims submission")
    checks.check(closeout_checks.get("narrowed_claim_subcheck_passed") is True, "closeout lost narrowed-claim subcheck scope")
    checks.check(closeout_checks.get("full_source_policy_package_ready") is False, "closeout overclaims full source-policy package")
    checks.check(
        closeout_checks.get("first_gate_to_work") == "Future B4 source-policy work-precision reintroduction",
        "first closeout gate changed",
    )
    checks.check(isinstance(ordered_gates, list) and len(ordered_gates) == 4, "ordered closeout gate count changed")
    checks.check([item.get("rank") for item in ordered_gates] == [1, 2, 3, 4], "ordered closeout gate ranks changed")
    checks.check(
        [item.get("gate") for item in ordered_gates]
        == [
            "Future B4 source-policy work-precision reintroduction",
            "Future B7 source-policy figure reintroduction",
            "Future B6 full source-policy prose pass",
            "Future full source-policy reproducibility package",
        ],
        "ordered closeout gate names changed",
    )
    gate0 = ordered_gates[0] if isinstance(ordered_gates, list) and len(ordered_gates) > 0 else {}
    gate1 = ordered_gates[1] if isinstance(ordered_gates, list) and len(ordered_gates) > 1 else {}
    gate2 = ordered_gates[2] if isinstance(ordered_gates, list) and len(ordered_gates) > 2 else {}
    gate3 = ordered_gates[3] if isinstance(ordered_gates, list) and len(ordered_gates) > 3 else {}
    checks.check(gate0.get("closed_rows") == 0 and gate0.get("total_rows") == 40, "B4 closeout row counts changed")
    checks.check(gate1.get("closed_rows") == 13 and gate1.get("total_rows") == 13, "B7 closeout row counts changed")
    checks.check(gate2.get("closed_rows") == 11 and gate2.get("total_rows") == 11, "B6 closeout row counts changed")
    checks.check(gate3.get("closed_rows") == 10 and gate3.get("total_rows") == 10, "minimal-package closeout row counts changed")
    checks.check(
        "Proof closure for dynamic Newton-Euler rows" not in [item.get("gate") for item in ordered_gates],
        "closed proof gate should not appear as an open ordered closeout gate",
    )
    closure_routes = closeout_checks.get("source_policy_closure_routes", [])
    routes_by_name = {
        item.get("route"): item
        for item in closure_routes
        if isinstance(item, dict) and isinstance(item.get("route"), str)
    }
    execution_route = routes_by_name.get("source_policy_execution", {})
    demotion_route = routes_by_name.get("claim_demotion", {})
    checks.check(len(closure_routes) == 2, "source-policy closure route count changed")
    checks.check(
        execution_route.get("status") == "open_requires_explicit_opt_in",
        "source-policy execution route status changed",
    )
    checks.check(
        execution_route.get("requires_default_1e_4") is False
        and execution_route.get("requires_explicit_1e_4_opt_in") is True,
        "source-policy execution route lost 1e-4 opt-in boundary",
    )
    checks.check(
        execution_route.get("current_closed_rows") == 0 and execution_route.get("current_total_rows") == 40,
        "source-policy execution route row counts changed",
    )
    checks.check(
        demotion_route.get("status") == "applied_to_claim_boundary_b2_closed_b4_still_open",
        "claim-demotion route status changed",
    )
    checks.check(
        demotion_route.get("claim_after_route") == "formal_order_and_common_reference_diagnostics_only",
        "claim-demotion route claim boundary changed",
    )
    checks.check(
        demotion_route.get("audit_schema") == "external-superiority-claim-demotion-audit-v1",
        "claim-demotion route lost audit schema",
    )
    checks.check(
        demotion_route.get("audit_status") == "route_b_applied_to_claim_boundary_no_external_superiority",
        "claim-demotion route audit status changed",
    )
    checks.check(
        demotion_route.get("audit_route_b_ready") is True,
        "claim-demotion route audit-ready marker missing",
    )
    checks.check(
        demotion_route.get("audit_promoted_to_blocker_gate") is True,
        "claim-demotion route should be synchronized with blocker gate",
    )
    checks.check(
        demotion_route.get("audit_b2_b4_gate_closed_by_this_artifact") is False,
        "claim-demotion route audit must not close B2/B4",
    )
    checks.check(
        demotion_route.get("audit_source_policy_rows_closed") == 0
        and demotion_route.get("audit_source_policy_total_rows") == 40,
        "claim-demotion route audit source-policy row counts changed",
    )
    checks.check(
        demotion_route.get("application_contract_schema") == "route-b-application-contract-v1",
        "claim-demotion route lost Route-B application contract",
    )
    checks.check(
        demotion_route.get("application_contract_ready_to_promote") is True,
        "claim-demotion route should be ready for blocker promotion",
    )
    checks.check(
        demotion_route.get("application_contract_safe_to_flip_flags") is False,
        "claim-demotion route should not allow safe bare flag flips",
    )
    checks.check(
        demotion_route.get("application_contract_satisfied_steps") == 6
        and demotion_route.get("application_contract_total_steps") == 6,
        "claim-demotion route application step counts changed",
    )
    checks.check(
        demotion_route.get("application_contract_unsatisfied_steps") == [],
        "claim-demotion route unsatisfied steps changed",
    )
    checks.check(
        demotion_route.get("audit_b2_gate_closed_by_route_b") is True
        and demotion_route.get("audit_b4_gate_closed_by_route_b") is False,
        "claim-demotion route B2/B4 closure markers changed",
    )
    checks.check(
        demotion_route.get("application_contract_creates_numerical_wins") is False,
        "claim-demotion route must not create numerical wins",
    )
    checks.check(
        demotion_route.get("requires_default_1e_4") is False
        and demotion_route.get("requires_explicit_1e_4_opt_in") is False,
        "claim-demotion route incorrectly requires 1e-4",
    )
    checks.check(
        demotion_route.get("additional_demotions_needed") == [],
        "claim-demotion route demotion list changed",
    )
    checks.check(
        "large default h=1e-4 campaigns without explicit opt-in"
        in closeout_checks.get("do_not_spend_on_before_source_policy", []),
        "closeout board lost explicit no-default-1e-4 boundary",
    )
    for token in [
        "## Future Full Source-Policy Reintroduction Board",
        "Closeout status: `future_full_source_policy_reintroduction_after_narrowed_claim_closure`.",
        "First gate to work: `Future B4 source-policy work-precision reintroduction`.",
        "Future B4 source-policy work-precision reintroduction",
        "Future B7 source-policy figure reintroduction",
        "Future B6 full source-policy prose pass",
        "Do not spend on before B4/B7 closure:",
        "Source-policy route A: `source_policy_execution` / `open_requires_explicit_opt_in`; explicit 1e-4 opt-in `True`; rows `0/40`.",
        "Source-policy route B: `claim_demotion` / `applied_to_claim_boundary_b2_closed_b4_still_open`; claim after route `formal_order_and_common_reference_diagnostics_only`; additional demotions `[]`.",
        "Route B demotion audit: `external-superiority-claim-demotion-audit-v1` / `route_b_applied_to_claim_boundary_no_external_superiority`; ready `True`; B2/B4 closed by route `True/False`; source-policy execution rows `0/40`.",
        "Route B application contract: `route-b-application-contract-v1`; ready-to-promote `True`; safe flag flip `False`; satisfied steps `6/6`; unsatisfied `[]`.",
    ]:
        checks.check(token in report_md, f"review report missing closeout-board token: {token}")
    checks.check(
        "First gate to work: `Proof closure for dynamic Newton-Euler rows`." not in report_md,
        "review report still ranks closed proof work first",
    )
    submission_integrity_checks = report.get("submission_integrity_checks", {})
    checks.check(
        submission_integrity_checks.get("schema")
        == submission_integrity.get("schema")
        == "cmame-submission-integrity-audit-v1",
        "submission-integrity audit not carried into review",
    )
    checks.check(
        submission_integrity_checks.get("status")
        == "submission_integrity_passed_reference_web_verified",
        "submission-integrity status changed",
    )
    checks.check(
        submission_integrity_checks.get("local_integrity_passed") is True,
        "local citation/sidecar integrity should pass",
    )
    checks.check(
        submission_integrity_checks.get("submission_ready") is False,
        "submission-integrity audit must not mark submission ready",
    )
    checks.check(
        submission_integrity_checks.get("external_reference_web_verification_complete") is True,
        "external reference web verification should be closed",
    )
    checks.check(
        submission_integrity_checks.get("external_reference_web_verification_required_for_final_submission") is False,
        "external reference web verification final-submission requirement should be closed",
    )
    checks.check(
        submission_integrity_checks.get("reference_metadata_schema")
        == submission_integrity.get("reference_metadata_audit", {}).get("schema")
        == reference_metadata.get("schema")
        == "reference-metadata-audit-v1",
        "reference metadata audit not carried into review",
    )
    checks.check(
        submission_integrity_checks.get("reference_metadata_status")
        == "all_reference_metadata_web_verified",
        "reference metadata audit status changed in review",
    )
    checks.check(
        submission_integrity_checks.get("reference_metadata_artifact_status")
        == "all_reference_metadata_web_verified",
        "reference metadata artifact status changed in review",
    )
    checks.check(submission_integrity_checks.get("reference_metadata_reference_count") == 28, "reference count changed")
    checks.check(
        submission_integrity_checks.get("reference_metadata_doi_reference_count") == 16,
        "reference DOI count changed",
    )
    checks.check(
        submission_integrity_checks.get("reference_metadata_doi_verified_count") == 16,
        "verified DOI count changed",
    )
    checks.check(
        submission_integrity_checks.get("reference_metadata_doi_unresolved_count") == 0,
        "unresolved DOI count changed",
    )
    checks.check(
        submission_integrity_checks.get("reference_metadata_local_non_doi_count") == 12,
        "local non-DOI reference count changed",
    )
    checks.check(
        submission_integrity_checks.get("reference_metadata_non_doi_verified_count") == 12,
        "verified non-DOI metadata count changed",
    )
    checks.check(
        submission_integrity_checks.get("reference_metadata_non_doi_count") == 0,
        "open non-DOI reference count changed",
    )
    checks.check(submission_integrity_checks.get("main_cited_key_count") == 28, "main citation count changed")
    checks.check(submission_integrity_checks.get("flat_cited_key_count") == 28, "flat citation count changed")
    checks.check(submission_integrity_checks.get("main_bibitem_count") == 28, "main bibitem count changed")
    checks.check(submission_integrity_checks.get("flat_bibitem_count") == 28, "flat bibitem count changed")
    checks.check(
        submission_integrity_checks.get("main_and_flat_citation_keys_match") is True,
        "main/flat citation keys differ",
    )
    checks.check(
        submission_integrity_checks.get("main_and_flat_bibitem_keys_match") is True,
        "main/flat bibitem keys differ",
    )
    checks.check(
        submission_integrity_checks.get("main_dangling_citation_keys") == [],
        "main dangling citation keys present",
    )
    checks.check(
        submission_integrity_checks.get("flat_dangling_citation_keys") == [],
        "flat dangling citation keys present",
    )
    checks.check(
        submission_integrity_checks.get("main_orphan_bibitem_keys") == [],
        "main orphan bibitems present",
    )
    checks.check(
        submission_integrity_checks.get("flat_orphan_bibitem_keys") == [],
        "flat orphan bibitems present",
    )
    checks.check(
        submission_integrity_checks.get("main_unresolved_log_lines") == [],
        "main unresolved citation/reference log lines present",
    )
    checks.check(
        submission_integrity_checks.get("flat_unresolved_log_lines") == [],
        "flat unresolved citation/reference log lines present",
    )
    checks.check(
        submission_integrity_checks.get("pdf_references_heading_present") is True,
        "main PDF references heading missing",
    )
    checks.check(
        submission_integrity_checks.get("flat_pdf_references_heading_present") is True,
        "flat PDF references heading missing",
    )
    checks.check(
        submission_integrity_checks.get("declaration_tokens_present") is True,
        "main declaration tokens missing",
    )
    checks.check(
        submission_integrity_checks.get("flat_declaration_tokens_present") is True,
        "flat declaration tokens missing",
    )
    checks.check(submission_integrity_checks.get("highlight_count") == 5, "main highlight count changed")
    checks.check(submission_integrity_checks.get("flat_highlight_count") == 5, "flat highlight count changed")
    checks.check(
        submission_integrity_checks.get("cover_letter_mentions_journal") is True,
        "cover letter journal marker missing",
    )
    checks.check(
        submission_integrity_checks.get("cover_letter_mentions_recommended_pdf") is True,
        "cover letter PDF marker missing",
    )
    checks.check(
        submission_integrity_checks.get("local_citation_key_integrity_closed") is True,
        "local citation key integrity not closed",
    )
    checks.check(
        submission_integrity_checks.get("bibliographic_metadata_web_verified") is True,
        "bibliographic metadata web verification not closed",
    )
    checks.check(
        submission_integrity_checks.get("submission_integrity_gate_closed") is True,
        "submission integrity gate not closed",
    )
    proof_checks = report.get("proof_checks", {})
    expected_anchor_evidence_sources = [
        "PROOF_CLOSURE_MANIFEST.json",
        "PROOF_CLAIM_TRACEABILITY_AUDIT.json",
    ]
    expected_proof_remaining_narrowed_statuses = {
        row.get("id"): row.get("status")
        for row in blocker.get("blockers", [])
        if isinstance(row, dict) and row.get("id") in {"B4", "B6", "B7"}
    }
    expected_proof_remaining_global_boundaries = [
        "full_source_policy_package_ready",
        "theorem_level_eta_h_solver_policy_evidence",
        "closed_residual_to_error_theorem_for_mechanism_rows",
    ]
    checks.check(
        proof_checks.get("proof_closure_manifest_schema")
        == proof_closure.get("schema")
        == "proof-closure-manifest-v1",
        "proof-closure manifest not carried into review",
    )
    checks.check(
        proof_checks.get("proof_closure_manifest_status")
        == "pc2_closed_by_direct_residual_bridge_global_boundary_retained",
        "proof-closure manifest status changed",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_schema")
        == proof_traceability.get("schema")
        == "proof-claim-traceability-audit-v1",
        "proof-claim traceability audit not carried into review",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_status")
        == "conditional_proof_claims_traceable_submission_not_ready",
        "proof-claim traceability status changed",
    )
    checks.check(
        proof_checks.get("proof_remaining_work_schema")
        == proof_remaining_work.get("schema")
        == "proof-remaining-work-manifest-v1",
        "proof remaining-work manifest not carried into review",
    )
    checks.check(
        proof_checks.get("proof_remaining_work_status")
        == "proof_b1_b3_closed_submission_gates_remaining",
        "proof remaining-work status changed",
    )
    checks.check(
        proof_checks.get("proof_remaining_work_submission_ready") is False,
        "proof remaining-work must not mark submission ready",
    )
    checks.check(
        proof_checks.get("proof_remaining_work_submission_ready_scope")
        == proof_remaining_work.get("submission_ready_scope")
        == "proof_remaining_work_global_boundary_not_narrowed_claim_package_decision",
        "proof remaining-work submission-ready scope changed",
    )
    checks.check(
        proof_checks.get("proof_remaining_work_manifest_scope")
        == proof_remaining_work.get("readiness_boundary", {}).get("proof_remaining_work_manifest_scope")
        == "B1_B3_closed_remaining_global_submission_gates",
        "proof remaining-work manifest scope changed",
    )
    checks.check(
        proof_checks.get("proof_remaining_work_narrowed_claim_b4_b6_b7_statuses")
        == proof_remaining_work.get("readiness_boundary", {}).get("narrowed_claim_b4_b6_b7_statuses")
        == expected_proof_remaining_narrowed_statuses
        == {"B4": "closed", "B6": "closed", "B7": "closed"},
        "proof remaining-work narrowed-claim statuses changed",
    )
    checks.check(
        proof_checks.get("proof_remaining_work_global_submission_boundaries_retained")
        == proof_remaining_work.get("readiness_boundary", {}).get("global_submission_boundaries_retained")
        == expected_proof_remaining_global_boundaries,
        "proof remaining-work global boundaries changed",
    )
    checks.check(
        proof_checks.get("proof_remaining_work_unsatisfied_close_requirements")
        == proof_remaining_work.get("summary", {}).get("unsatisfied_close_requirement_count")
        == 0,
        "proof remaining-work unsatisfied close count changed",
    )
    checks.check(
        proof_checks.get("proof_remaining_work_unsatisfied_close_requirement_ids") == [],
        "proof remaining-work unsatisfied IDs changed",
    )
    checks.check(
        proof_checks.get("proof_remaining_work_certified_non_dynamic_rows") == 96,
        "proof remaining-work certified row count changed",
    )
    checks.check(
        proof_checks.get("proof_remaining_work_open_dynamic_rows") == 36,
        "proof remaining-work open dynamic row count changed",
    )
    checks.check(
        proof_checks.get("proof_remaining_work_newton_euler_row_obligation_links") == 180,
        "proof remaining-work Newton-Euler link count changed",
    )
    checks.check(
        proof_checks.get("proof_remaining_work_finite_trajectory_steps") == 30,
        "proof remaining-work finite trajectory step count changed",
    )
    checks.check(
        proof_checks.get("proof_remaining_work_default_1e_4_required") is False,
        "proof remaining-work unexpectedly requires default 1e-4",
    )
    checks.check(
        proof_checks.get("proof_remaining_work_heavy_run_invoked") is False,
        "proof remaining-work unexpectedly invoked a heavy run",
    )
    checks.check(
        proof_checks.get("proof_remaining_work_run_v047_invoked") is False,
        "proof remaining-work unexpectedly invoked run_v047",
    )
    checks.check(
        proof_checks.get("proof_remaining_work_newton_euler_certificate_present") is True,
        "proof remaining-work certificate-present marker missing",
    )
    checks.check(
        proof_checks.get("proof_remaining_work_newton_euler_certificate_complete") is False,
        "proof remaining-work certificate unexpectedly complete",
    )
    checks.check(
        proof_checks.get("proof_remaining_work_newton_euler_runtime_expression_structure_checked") is True,
        "proof remaining-work runtime expression structure marker missing",
    )
    checks.check(
        proof_checks.get("proof_remaining_work_newton_euler_runtime_expression_checked_rows") == 36,
        "proof remaining-work runtime expression checked rows changed",
    )
    checks.check(
        proof_checks.get("proof_remaining_work_newton_euler_runtime_template_instantiation_checked") is True,
        "proof remaining-work runtime template instantiation marker missing",
    )
    checks.check(
        proof_checks.get("proof_remaining_work_newton_euler_runtime_template_instantiation_checked_rows") == 36,
        "proof remaining-work runtime template instantiation row count changed",
    )
    checks.check(
        proof_checks.get("proof_remaining_work_b1_independent_symbolic_row_oracle_closed")
        == proof_remaining_work.get("summary", {}).get("b1_independent_symbolic_row_oracle_closed")
        is True,
        "proof remaining-work B1 independent symbolic row-oracle closure marker changed",
    )
    checks.check(
        proof_checks.get("proof_remaining_work_b1_independent_symbolic_row_oracle_closed_rows")
        == proof_remaining_work.get("summary", {}).get("b1_independent_symbolic_row_oracle_closed_rows")
        == 36,
        "proof remaining-work B1 independent symbolic row-oracle rows changed",
    )
    checks.check(
        proof_checks.get("proof_remaining_work_b1_source_template_symbolic_identity_rows")
        == proof_remaining_work.get("summary", {}).get("b1_source_template_symbolic_identity_rows")
        == 36,
        "proof remaining-work B1 source-template rows changed",
    )
    checks.check(
        proof_checks.get("proof_remaining_work_b1_runtime_row_binding_checked_rows")
        == proof_remaining_work.get("summary", {}).get("b1_runtime_row_binding_checked_rows")
        == 36,
        "proof remaining-work B1 runtime-binding rows changed",
    )
    checks.check(
        proof_checks.get("proof_remaining_work_b1_ad_expanded_symbolic_oracle_closure")
        == proof_remaining_work.get("summary", {}).get("b1_ad_expanded_symbolic_oracle_closure")
        is True,
        "proof remaining-work B1 AD-expanded closure marker changed",
    )
    checks.check(
        proof_checks.get("proof_remaining_work_b1_ad_expanded_symbolic_oracle_closed_rows")
        == proof_remaining_work.get("summary", {}).get("b1_ad_expanded_symbolic_oracle_closed_rows")
        == 36,
        "proof remaining-work B1 AD-expanded row count changed",
    )
    checks.check(
        proof_checks.get("proof_remaining_work_b1_ad_expanded_symbolic_oracle_columns_per_row")
        == proof_remaining_work.get("summary", {}).get("b1_ad_expanded_symbolic_oracle_columns_per_row")
        == 132,
        "proof remaining-work B1 AD-expanded column count changed",
    )
    checks.check(
        proof_checks.get("proof_remaining_work_b1_ad_expanded_symbolic_oracle_closed_cells")
        == proof_remaining_work.get("summary", {}).get("b1_ad_expanded_symbolic_oracle_closed_cells")
        == 4752,
        "proof remaining-work B1 AD-expanded derivative-cell count changed",
    )
    checks.check(
        proof_checks.get("newton_euler_symbolic_defect_certificate_artifact_schema")
        == newton_euler_symbolic_defect_certificate.get("schema")
        == "newton-euler-symbolic-defect-certificate-v1",
        "Newton-Euler symbolic defect certificate artifact not carried into review",
    )
    checks.check(
        proof_checks.get("newton_euler_symbolic_defect_certificate_artifact_status")
        == "balance_identities_closed_defect_not_proved",
        "Newton-Euler symbolic defect certificate artifact status changed",
    )
    checks.check(
        proof_checks.get("newton_euler_symbolic_defect_certificate_artifact_complete") is False,
        "Newton-Euler symbolic defect certificate artifact unexpectedly complete",
    )
    checks.check(
        proof_checks.get("newton_euler_symbolic_defect_certificate_artifact_rows") == 36,
        "Newton-Euler symbolic defect certificate artifact row count changed",
    )
    checks.check(
        proof_checks.get("newton_euler_symbolic_defect_certificate_artifact_certified_rows") == 0,
        "Newton-Euler symbolic defect certificate artifact certified row count changed",
    )
    checks.check(
        proof_checks.get("newton_euler_symbolic_defect_certificate_artifact_open_rows") == 36,
        "Newton-Euler symbolic defect certificate artifact open row count changed",
    )
    checks.check(
        proof_checks.get("newton_euler_symbolic_defect_certificate_artifact_open_obligations") == 1,
        "Newton-Euler symbolic defect certificate artifact open obligation count changed",
    )
    checks.check(
        proof_checks.get("newton_euler_symbolic_defect_certificate_artifact_closed_obligations") == 5,
        "Newton-Euler symbolic defect certificate artifact closed obligation count changed",
    )
    checks.check(
        proof_checks.get("newton_euler_symbolic_defect_certificate_artifact_row_obligation_links") == 180,
        "Newton-Euler symbolic defect certificate artifact link count changed",
    )
    checks.check(
        proof_checks.get("newton_euler_symbolic_defect_certificate_artifact_runtime_expression_structure_checked")
        is True,
        "Newton-Euler symbolic defect certificate runtime expression marker missing",
    )
    checks.check(
        proof_checks.get("newton_euler_symbolic_defect_certificate_artifact_runtime_expression_checked_rows") == 36,
        "Newton-Euler symbolic defect certificate runtime expression checked rows changed",
    )
    checks.check(
        proof_checks.get("newton_euler_symbolic_defect_certificate_artifact_runtime_template_instantiation_checked")
        is True,
        "Newton-Euler symbolic defect certificate runtime template instantiation marker missing",
    )
    checks.check(
        proof_checks.get(
            "newton_euler_symbolic_defect_certificate_artifact_runtime_template_instantiation_checked_rows"
        )
        == 36,
        "Newton-Euler symbolic defect certificate runtime template instantiation row count changed",
    )
    checks.check(
        proof_checks.get("newton_euler_symbolic_defect_certificate_artifact_body_specific_wrench_checked")
        is True,
        "Newton-Euler symbolic defect certificate body-specific wrench marker missing",
    )
    checks.check(
        proof_checks.get("newton_euler_symbolic_defect_certificate_artifact_body_specific_wrench_rows") == 36,
        "Newton-Euler symbolic defect certificate body-specific wrench row count changed",
    )
    checks.check(
        proof_checks.get("newton_euler_symbolic_defect_certificate_artifact_body0_wrench_rows") == 18,
        "Newton-Euler symbolic defect certificate body0 wrench row count changed",
    )
    checks.check(
        proof_checks.get("newton_euler_symbolic_defect_certificate_artifact_body1_wrench_rows") == 18,
        "Newton-Euler symbolic defect certificate body1 wrench row count changed",
    )
    checks.check(
        proof_checks.get(
            "newton_euler_symbolic_defect_certificate_artifact_template_algebraic_equivalence_checked"
        )
        is True,
        "Newton-Euler symbolic defect certificate template algebraic equivalence marker missing",
    )
    checks.check(
        proof_checks.get(
            "newton_euler_symbolic_defect_certificate_artifact_template_algebraic_equivalence_checked_rows"
        )
        == 36,
        "Newton-Euler symbolic defect certificate template algebraic equivalence row count changed",
    )
    checks.check(
        proof_checks.get(
            "newton_euler_symbolic_defect_certificate_artifact_c2_template_algebraic_equivalence_closed"
        )
        is True,
        "Newton-Euler symbolic defect certificate template-level C2 subcheck not closed",
    )
    checks.check(
        proof_checks.get("newton_euler_symbolic_defect_certificate_artifact_proof_gap_closed") is False,
        "Newton-Euler symbolic defect certificate artifact unexpectedly closes proof gap",
    )
    checks.check(
        proof_checks.get("b1_symbolic_row_oracle_closure_schema")
        == b1_symbolic_row_oracle_closure.get("schema")
        == "b1-symbolic-row-oracle-closure-certificate-v1",
        "B1 symbolic row-oracle closure certificate not carried into review",
    )
    checks.check(
        proof_checks.get("b1_symbolic_row_oracle_closure_status")
        == "independent_symbolic_row_oracle_closed_ad_expanded_symbolic_oracle_open",
        "B1 symbolic row-oracle closure status changed",
    )
    checks.check(
        proof_checks.get("b1_independent_symbolic_row_by_row_oracle_for_expanded_fullva_rows_closed")
        == b1_symbolic_row_oracle_closure.get(
            "independent_symbolic_row_by_row_oracle_for_expanded_fullva_rows_closed"
        )
        is True,
        "B1 independent residual symbolic row oracle not closed in review",
    )
    checks.check(
        proof_checks.get("b1_independent_symbolic_row_oracle_closed_rows")
        == b1_symbolic_row_oracle_closure.get("independent_symbolic_row_by_row_oracle_closed_rows")
        == 36,
        "B1 symbolic row-oracle row count changed",
    )
    checks.check(
        proof_checks.get("b1_source_template_symbolic_identity_rows")
        == b1_symbolic_row_oracle_closure.get("source_template_symbolic_identity_rows")
        == 36,
        "B1 source-template symbolic identity rows changed",
    )
    checks.check(
        proof_checks.get("b1_runtime_row_binding_checked_rows")
        == b1_symbolic_row_oracle_closure.get("runtime_row_binding_checked_rows")
        == 36,
        "B1 runtime row-binding rows changed",
    )
    checks.check(
        proof_checks.get("b1_symbolic_row_oracle_ad_expanded_symbolic_oracle_closure") is False,
        "B1 row-oracle certificate overclaims AD-expanded symbolic closure",
    )
    checks.check(
        proof_checks.get("b1_symbolic_row_oracle_dynamic_symbolic_oracle_complete") is False,
        "B1 row-oracle certificate overclaims dynamic symbolic oracle",
    )
    checks.check(
        proof_checks.get("b1_symbolic_row_oracle_stage_residual_O_h7_symbolic_certificate_proved") is False,
        "B1 row-oracle certificate overclaims symbolic-certificate O(h^7) proof",
    )
    checks.check(
        proof_checks.get("b1_symbolic_row_oracle_remaining_required_item")
        == "AD_expanded_symbolic_oracle_closure",
        "B1 remaining item changed",
    )
    checks.check(
        proof_checks.get("b1_ad_expanded_symbolic_oracle_closure_schema")
        == b1_ad_expanded_symbolic_oracle_closure.get("schema")
        == "b1-ad-expanded-symbolic-oracle-closure-certificate-v1",
        "B1 AD-expanded symbolic oracle closure certificate not carried into review",
    )
    checks.check(
        proof_checks.get("b1_ad_expanded_symbolic_oracle_closure_status")
        == "ad_expanded_symbolic_oracle_closed_without_o_h7_overclaim",
        "B1 AD-expanded symbolic oracle closure status changed",
    )
    checks.check(
        proof_checks.get("b1_ad_expanded_symbolic_oracle_closure")
        == b1_ad_expanded_symbolic_oracle_closure.get("ad_expanded_symbolic_oracle_closure")
        is True,
        "B1 AD-expanded symbolic oracle closure marker changed",
    )
    checks.check(
        proof_checks.get("b1_ad_expanded_symbolic_oracle_closed_rows")
        == b1_ad_expanded_symbolic_oracle_closure.get("ad_expanded_symbolic_oracle_closed_rows")
        == 36,
        "B1 AD-expanded symbolic oracle closed row count changed",
    )
    checks.check(
        proof_checks.get("b1_ad_expanded_symbolic_oracle_columns_per_row")
        == b1_ad_expanded_symbolic_oracle_closure.get("columns_per_row")
        == 132,
        "B1 AD-expanded symbolic oracle column count changed",
    )
    checks.check(
        proof_checks.get("b1_ad_expanded_symbolic_oracle_closed_cells")
        == b1_ad_expanded_symbolic_oracle_closure.get("ad_expanded_symbolic_oracle_closed_cells")
        == 4752,
        "B1 AD-expanded symbolic oracle closed-cell count changed",
    )
    checks.check(
        proof_checks.get("b1_ad_expanded_symbolic_oracle_dynamic_symbolic_oracle_complete") is False,
        "B1 AD-expanded certificate overclaims global symbolic oracle",
    )
    checks.check(
        proof_checks.get("b1_ad_expanded_symbolic_oracle_stage_residual_O_h7_symbolic_certificate_proved")
        is False,
        "B1 AD-expanded certificate overclaims symbolic-certificate O(h^7) proof",
    )
    checks.check(
        proof_checks.get("b1_ad_expanded_symbolic_oracle_proof_gap_closed_by_this_certificate") is False,
        "B1 AD-expanded certificate overclaims proof-gap closure",
    )
    checks.check(
        proof_checks.get("b1_ad_expanded_symbolic_oracle_submission_ready") is False,
        "B1 AD-expanded certificate overclaims submission readiness",
    )
    checks.check(
        proof_checks.get("newton_euler_ad_expanded_row_oracle_schema")
        == newton_euler_ad_expanded_row_oracle.get("schema")
        == "newton-euler-ad-expanded-row-oracle-audit-v1",
        "Newton-Euler AD-expanded row oracle audit not carried into review",
    )
    checks.check(
        proof_checks.get("newton_euler_ad_expanded_row_oracle_status")
        == "ad_expanded_runtime_formula_binding_complete_symbolic_oracle_open",
        "Newton-Euler AD-expanded row oracle status changed",
    )
    checks.check(
        proof_checks.get("newton_euler_ad_expanded_row_oracle_closed") is True,
        "Newton-Euler AD-expanded row oracle closure marker missing",
    )
    checks.check(
        proof_checks.get("newton_euler_ad_expanded_row_oracle_rows") == 36,
        "Newton-Euler AD-expanded row oracle row count changed",
    )
    checks.check(
        proof_checks.get("newton_euler_ad_expanded_row_oracle_columns_per_row") == 132,
        "Newton-Euler AD-expanded row oracle column count changed",
    )
    checks.check(
        proof_checks.get("newton_euler_ad_expanded_row_oracle_probe_count") == 3,
        "Newton-Euler AD-expanded row oracle probe count changed",
    )
    checks.check(
        float(proof_checks.get("newton_euler_ad_expanded_row_oracle_max_mismatch", 1.0)) <= 1.0e-12,
        "Newton-Euler AD-expanded row oracle mismatch too large",
    )
    checks.check(
        proof_checks.get("newton_euler_ad_expanded_symbolic_oracle_closure") is False,
        "Newton-Euler AD-expanded audit overclaims symbolic oracle closure",
    )
    checks.check(
        proof_checks.get("newton_euler_ad_expanded_independent_symbolic_row_oracle_closed") is False,
        "Newton-Euler AD-expanded audit overclaims independent symbolic rows",
    )
    checks.check(
        proof_checks.get("newton_euler_symbolic_defect_certificate_artifact_ad_expanded_rows") == 36,
        "Newton-Euler symbolic defect certificate AD-expanded row count changed",
    )
    checks.check(
        proof_checks.get("newton_euler_symbolic_defect_certificate_artifact_ad_expanded_symbolic_oracle_closure")
        is False,
        "Newton-Euler symbolic defect certificate overclaims AD-expanded symbolic closure",
    )
    checks.check(
        "Newton-Euler AD-expanded row oracle: `True` with rows/columns/probes `36/132/3`"
        in report_md,
        "review markdown missing Newton-Euler AD-expanded row oracle summary",
    )
    checks.check(
        "B1 independent residual symbolic row oracle: `True` with rows/source-template/runtime-binding `36/36/36`; row-certificate-only remaining item `AD_expanded_symbolic_oracle_closure`."
        in report_md,
        "review markdown missing B1 symbolic row-oracle closure summary",
    )
    checks.check(
        "B1 AD-expanded implementation-path certificate: `True` with rows/columns/cells `36/132/4752`; primitive/global dynamic oracle/O(h^7) symbolic certificate/submission ready `False/False/False`."
        in report_md,
        "review markdown missing B1 AD-expanded implementation-path closure summary",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_submission_ready") is False,
        "proof-claim traceability must not mark submission ready",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_main_labels_present") is True,
        "proof-claim traceability main labels missing",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_flat_labels_present") is True,
        "proof-claim traceability flat labels missing",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_main_boundary_tokens_present") is True,
        "proof-claim traceability main boundary tokens missing",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_flat_boundary_tokens_present") is True,
        "proof-claim traceability flat boundary tokens missing",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_object_counts_match") is True,
        "proof-claim traceability proof object counts changed",
    )
    proof_claim_theorem_traceability = proof_traceability.get("manuscript_theorem_traceability", {})
    checks.check(
        proof_checks.get("proof_claim_traceability_theorem_label")
        == proof_claim_theorem_traceability.get("accepted_theorem_label")
        == "thm:g6fullva-order",
        "proof-claim theorem traceability theorem label not carried into review",
    )
    for review_key, source_key in [
        ("proof_claim_traceability_theorem_labels_present", "theorem_statement_labels_present"),
        ("proof_claim_traceability_theorem_boundary_present", "conditional_theorem_boundary_present"),
        ("proof_claim_traceability_theorem_claims_mapped", "conditional_proof_claims_mapped_to_manuscript"),
        ("proof_claim_traceability_dependency_graph_present", "proof_dependency_graph_present"),
        ("proof_claim_traceability_table_present", "proof_traceability_table_present"),
        ("proof_claim_traceability_dynamic_theorem_matrix_present", "dynamic_proof_closure_matrix_present"),
        ("proof_claim_traceability_primitive_lane_boundary_present", "primitive_lane_boundary_present"),
        ("proof_claim_traceability_residual_nonpromotion_present", "residual_nonpromotion_present"),
        ("proof_claim_traceability_eta_condition_retained", "eta_h_theorem_condition_retained"),
        ("proof_claim_traceability_residual_to_error_not_promoted", "residual_to_error_not_promoted"),
        ("proof_claim_traceability_route_exclusivity_boundary_present", "route_exclusivity_boundary_present"),
        (
            "proof_claim_traceability_theorem_residual_certificate_exclusivity_present",
            "theorem_residual_certificate_exclusivity_present",
        ),
        ("proof_claim_traceability_source_policy_or_full_tfe_not_promoted", "source_policy_or_full_tfe_not_promoted"),
        ("proof_claim_traceability_no_state_change", "does_not_change_proof_closure_state"),
    ]:
        checks.check(
            proof_checks.get(review_key) == proof_claim_theorem_traceability.get(source_key) is True,
            f"proof-claim theorem traceability true marker not carried into review: {review_key}",
        )
    for review_key, source_key in [
        ("proof_claim_traceability_eta_evidence_closed", "eta_h_solver_policy_evidence_closed"),
        ("proof_claim_traceability_fixed_tolerance_asymptotic_proof", "fixed_tolerance_runs_are_asymptotic_proof"),
    ]:
        checks.check(
            proof_checks.get(review_key) == proof_claim_theorem_traceability.get(source_key) is False,
            f"proof-claim theorem traceability false boundary not carried into review: {review_key}",
        )
    checks.check(
        "Proof-claim theorem traceability: label `thm:g6fullva-order`; labels/boundary/mapped `True/True/True`; dependency/table/dynamic `True/True/True`."
        in report_md,
        "review markdown missing proof-claim theorem traceability summary",
    )
    checks.check(
        "Proof-claim theorem no-promotion boundary: primitive/residual `True/True`; eta condition/closure/fixed proof `True/False/False`; residual/source-policy-full-TFE not promoted `True/True`; no-state-change `True`."
        in report_md,
        "review markdown missing proof-claim theorem no-promotion boundary summary",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_p7_retained_nonpromotion_boundary_present")
        == proof_claim_theorem_traceability.get("p7_retained_nonpromotion_boundary_present")
        == proof_traceability.get("remaining_claim_boundary", {}).get(
            "p7_retained_nonpromotion_boundary_present"
        )
        == strict_proof_audit.get("manuscript_theorem_traceability", {}).get(
            "p7_retained_nonpromotion_boundary_present"
        )
        is True,
        "proof-claim P7 output nonclaim/residual-to-error boundary not carried into review",
    )
    checks.check(
        "Proof-claim P7 output nonclaim/residual-to-error boundary present: `True`." in report_md,
        "review markdown missing proof-claim P7 output nonclaim/residual-to-error boundary",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_b1_closure_scope_boundary_present")
        == proof_claim_theorem_traceability.get("b1_closure_scope_boundary_present")
        == proof_traceability.get("remaining_claim_boundary", {}).get("b1_closure_scope_boundary_present")
        == strict_proof_audit.get("manuscript_theorem_traceability", {}).get(
            "b1_closure_scope_boundary_present"
        )
        is True,
        "proof-claim B1 closure-scope boundary not carried into review",
    )
    checks.check(
        "Proof-claim B1 closure-scope boundary present: `True`." in report_md,
        "review markdown missing proof-claim B1 closure-scope boundary",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_p6_solver_scope_boundary_present")
        == proof_claim_theorem_traceability.get("p6_solver_scope_boundary_present")
        == proof_traceability.get("remaining_claim_boundary", {}).get("p6_solver_scope_boundary_present")
        == strict_proof_audit.get("manuscript_theorem_traceability", {}).get(
            "p6_solver_scope_boundary_present"
        )
        is True,
        "proof-claim P6 solver-scope boundary not carried into review",
    )
    checks.check(
        "Proof-claim P6 solver-scope boundary present: `True`." in report_md,
        "review markdown missing proof-claim P6 solver-scope boundary",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_p1p2_compact_tube_boundary_present")
        == proof_claim_theorem_traceability.get("p1p2_compact_tube_boundary_present")
        == proof_traceability.get("remaining_claim_boundary", {}).get(
            "p1p2_compact_tube_boundary_present"
        )
        == strict_proof_audit.get("manuscript_theorem_traceability", {}).get(
            "p1p2_compact_tube_boundary_present"
        )
        is True,
        "proof-claim P1/P2 compact-tube boundary not carried into review",
    )
    checks.check(
        "Proof-claim P1/P2 compact-tube boundary present: `True`." in report_md,
        "review markdown missing proof-claim P1/P2 compact-tube boundary",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_p3p4_implementation_boundary_present")
        == proof_claim_theorem_traceability.get("p3p4_implementation_boundary_present")
        == proof_traceability.get("remaining_claim_boundary", {}).get(
            "p3p4_implementation_boundary_present"
        )
        == strict_proof_audit.get("manuscript_theorem_traceability", {}).get(
            "p3p4_implementation_boundary_present"
        )
        is True,
        "proof-claim P3/P4 implementation-defect boundary not carried into review",
    )
    checks.check(
        "Proof-claim P3/P4 implementation-defect boundary present: `True`."
        in report_md,
        "review markdown missing proof-claim P3/P4 implementation-defect boundary",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_p5_direct_route_boundary_present")
        == proof_claim_theorem_traceability.get("p5_direct_route_boundary_present")
        == proof_traceability.get("remaining_claim_boundary", {}).get(
            "p5_direct_route_boundary_present"
        )
        == strict_proof_audit.get("manuscript_theorem_traceability", {}).get(
            "p5_direct_route_boundary_present"
        )
        is True,
        "proof-claim P5 direct-route boundary not carried into review",
    )
    checks.check(
        "Proof-claim P5 direct-route boundary present: `True`." in report_md,
        "review markdown missing proof-claim P5 direct-route boundary",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_proof_causality_ledger_present")
        == proof_claim_theorem_traceability.get("proof_causality_ledger_present")
        == proof_traceability.get("remaining_claim_boundary", {}).get(
            "proof_causality_ledger_present"
        )
        == strict_proof_audit.get("manuscript_theorem_traceability", {}).get(
            "proof_causality_ledger_present"
        )
        is True,
        "proof-claim proof-causality ledger not carried into review",
    )
    checks.check(
        "Proof-claim proof-causality table present: `True`." in report_md,
        "review markdown missing proof-claim proof-causality table",
    )
    checks.check(
        proof_checks.get(
            "proof_claim_traceability_direct_route_anticircularity_ledger_present"
        )
        == proof_claim_theorem_traceability.get(
            "direct_route_anticircularity_ledger_present"
        )
        == proof_traceability.get("remaining_claim_boundary", {}).get(
            "direct_route_anticircularity_ledger_present"
        )
        == strict_proof_audit.get("manuscript_theorem_traceability", {}).get(
            "direct_route_anticircularity_ledger_present"
        )
        is True,
        "proof-claim direct-route anti-circularity ledger not carried into review",
    )
    checks.check(
        "Proof-claim direct-route anti-circularity table present: `True`."
        in report_md,
        "review markdown missing proof-claim direct-route anti-circularity table",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_p_interface_satisfaction_ledger_present")
        == proof_claim_theorem_traceability.get("p_interface_satisfaction_ledger_present")
        == proof_traceability.get("remaining_claim_boundary", {}).get(
            "p_interface_satisfaction_ledger_present"
        )
        == strict_proof_audit.get("manuscript_theorem_traceability", {}).get(
            "p_interface_satisfaction_ledger_present"
        )
        is True,
        "proof-claim theorem-interface satisfaction ledger not carried into review",
    )
    checks.check(
        "Proof-claim theorem-interface satisfaction table present: `True`." in report_md,
        "review markdown missing proof-claim theorem-interface satisfaction table",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_p7_residual_to_error_ledger_present")
        == proof_claim_theorem_traceability.get("p7_residual_to_error_ledger_present")
        == proof_traceability.get("remaining_claim_boundary", {}).get(
            "p7_residual_to_error_ledger_present"
        )
        == strict_proof_audit.get("manuscript_theorem_traceability", {}).get(
            "p7_residual_to_error_ledger_present"
        )
        is True,
        "proof-claim P7 residual-to-error obligation ledger not carried into review",
    )
    checks.check(
        "Proof-claim P7 output nonclaim/residual-to-error boundary table present: `True`."
        in report_md,
        "review markdown missing proof-claim P7 output nonclaim/residual-to-error boundary table",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_theorem_use_rule_present")
        == proof_claim_theorem_traceability.get("theorem_use_rule_present")
        == proof_traceability.get("remaining_claim_boundary", {}).get(
            "theorem_use_rule_present"
        )
        == strict_proof_audit.get("manuscript_theorem_traceability", {}).get(
            "theorem_use_rule_present"
        )
        is True,
        "proof-claim theorem-use rule not carried into review",
    )
    checks.check(
        "Proof-claim theorem-use rule present: `True`." in report_md,
        "review markdown missing proof-claim theorem-use rule",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_quantifier_domain_ledger_present")
        == proof_claim_theorem_traceability.get("quantifier_domain_ledger_present")
        == proof_traceability.get("remaining_claim_boundary", {}).get(
            "quantifier_domain_ledger_present"
        )
        == strict_proof_audit.get("manuscript_theorem_traceability", {}).get(
            "quantifier_domain_ledger_present"
        )
        is True,
        "proof-claim quantifier/domain ledger not carried into review",
    )
    checks.check(
        "Proof-claim quantifier/domain table present: `True`." in report_md,
        "review markdown missing proof-claim quantifier/domain table",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_local_global_transfer_ledger_present")
        == proof_claim_theorem_traceability.get("local_global_transfer_ledger_present")
        == proof_traceability.get("remaining_claim_boundary", {}).get(
            "local_global_transfer_ledger_present"
        )
        == strict_proof_audit.get("manuscript_theorem_traceability", {}).get(
            "local_global_transfer_ledger_present"
        )
        is True,
        "proof-claim local-to-global transfer ledger not carried into review",
    )
    checks.check(
        "Proof-claim local-to-global transfer table present: `True`." in report_md,
        "review markdown missing proof-claim local-to-global transfer table",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_objective_completion_boundary_present")
        == proof_claim_theorem_traceability.get("objective_completion_boundary_present")
        == proof_traceability.get("remaining_claim_boundary", {}).get(
            "objective_completion_boundary_present"
        )
        == strict_proof_audit.get("manuscript_theorem_traceability", {}).get(
            "objective_completion_boundary_present"
        )
        is True,
        "proof-claim objective-completion boundary not carried into review",
    )
    checks.check(
        "Proof-claim objective-completion boundary present: `True`." in report_md,
        "review markdown missing proof-claim objective-completion boundary",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_constant_dependency_ledger_present")
        == proof_claim_theorem_traceability.get("constant_dependency_ledger_present")
        == proof_traceability.get("remaining_claim_boundary", {}).get(
            "constant_dependency_ledger_present"
        )
        == strict_proof_audit.get("manuscript_theorem_traceability", {}).get(
            "constant_dependency_ledger_present"
        )
        is True,
        "proof-claim constant-dependency ledger not carried into review",
    )
    checks.check(
        "Proof-claim constant-dependency table present: `True`." in report_md,
        "review markdown missing proof-claim constant-dependency table",
    )
    checks.check(
        proof_checks.get(
            "proof_claim_traceability_theorem_dependency_consumption_ledger_present"
        )
        == proof_claim_theorem_traceability.get(
            "theorem_dependency_consumption_ledger_present"
        )
        == proof_traceability.get("remaining_claim_boundary", {}).get(
            "theorem_dependency_consumption_ledger_present"
        )
        == strict_proof_audit.get("manuscript_theorem_traceability", {}).get(
            "theorem_dependency_consumption_ledger_present"
        )
        is True,
        "proof-claim theorem dependency consumption ledger not carried into review",
    )
    checks.check(
        "Proof-claim theorem dependency consumption table present: `True`." in report_md,
        "review markdown missing proof-claim theorem dependency consumption table",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_branch_consistency_ledger_present")
        == proof_claim_theorem_traceability.get("branch_consistency_ledger_present")
        == proof_traceability.get("remaining_claim_boundary", {}).get(
            "branch_consistency_ledger_present"
        )
        == strict_proof_audit.get("manuscript_theorem_traceability", {}).get(
            "branch_consistency_ledger_present"
        )
        is True,
        "proof-claim accepted-branch consistency ledger not carried into review",
    )
    checks.check(
        "Proof-claim accepted-branch consistency table present: `True`." in report_md,
        "review markdown missing proof-claim accepted-branch consistency table",
    )
    checks.check(
        proof_checks.get(
            "proof_claim_traceability_implementation_route_oracle_ledger_present"
        )
        == proof_claim_theorem_traceability.get(
            "implementation_route_oracle_ledger_present"
        )
        == proof_traceability.get("remaining_claim_boundary", {}).get(
            "implementation_route_oracle_ledger_present"
        )
        == strict_proof_audit.get("manuscript_theorem_traceability", {}).get(
            "implementation_route_oracle_ledger_present"
        )
        is True,
        "proof-claim implementation-route/oracle separation ledger not carried into review",
    )
    checks.check(
        "Proof-claim implementation-route/oracle separation table present: `True`."
        in report_md,
        "review markdown missing proof-claim implementation-route/oracle separation table",
    )
    checks.check(
        proof_checks.get(
            "proof_claim_traceability_nonlinear_solver_scale_ledger_present"
        )
        == proof_claim_theorem_traceability.get(
            "nonlinear_solver_scale_ledger_present"
        )
        == proof_traceability.get("remaining_claim_boundary", {}).get(
            "nonlinear_solver_scale_ledger_present"
        )
        == strict_proof_audit.get("manuscript_theorem_traceability", {}).get(
            "nonlinear_solver_scale_ledger_present"
        )
        is True,
        "proof-claim nonlinear-solver scale ledger not carried into review",
    )
    checks.check(
        "Proof-claim nonlinear-solver scale table present: `True`." in report_md,
        "review markdown missing proof-claim nonlinear-solver scale table",
    )
    checks.check(
        proof_checks.get(
            "proof_claim_traceability_local_defect_decomposition_ledger_present"
        )
        == proof_claim_theorem_traceability.get(
            "local_defect_decomposition_ledger_present"
        )
        == proof_traceability.get("remaining_claim_boundary", {}).get(
            "local_defect_decomposition_ledger_present"
        )
        == strict_proof_audit.get("manuscript_theorem_traceability", {}).get(
            "local_defect_decomposition_ledger_present"
        )
        is True,
        "proof-claim local-defect decomposition ledger not carried into review",
    )
    checks.check(
        "Proof-claim local-defect decomposition table present: `True`." in report_md,
        "review markdown missing proof-claim local-defect decomposition table",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_theorem_output_scope_ledger_present")
        == proof_claim_theorem_traceability.get("theorem_output_scope_ledger_present")
        == proof_traceability.get("remaining_claim_boundary", {}).get(
            "theorem_output_scope_ledger_present"
        )
        == strict_proof_audit.get("manuscript_theorem_traceability", {}).get(
            "theorem_output_scope_ledger_present"
        )
        is True,
        "proof-claim theorem output scope ledger not carried into review",
    )
    checks.check(
        "Proof-claim theorem output scope table present: `True`." in report_md,
        "review markdown missing proof-claim theorem output scope table",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_reporting_map_ledger_present")
        == proof_claim_theorem_traceability.get("reporting_map_ledger_present")
        == proof_traceability.get("remaining_claim_boundary", {}).get(
            "reporting_map_ledger_present"
        )
        == strict_proof_audit.get("manuscript_theorem_traceability", {}).get(
            "reporting_map_ledger_present"
        )
        is True,
        "proof-claim reporting-map/norm-equivalence ledger not carried into review",
    )
    checks.check(
        "Proof-claim reporting-map/norm-equivalence table present: `True`."
        in report_md,
        "review markdown missing proof-claim reporting-map/norm-equivalence table",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_theorem_conclusion_scope_guard_present")
        == proof_claim_theorem_traceability.get("theorem_conclusion_scope_guard_present")
        == proof_traceability.get("remaining_claim_boundary", {}).get(
            "theorem_conclusion_scope_guard_present"
        )
        is True,
        "proof-claim scope-of-conclusion statement not carried into review",
    )
    checks.check(
        "Proof-claim scope-of-conclusion statement present: `True`."
        in report_md,
        "review markdown missing proof-claim scope-of-conclusion statement",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_proof_strength_certificate_present")
        == proof_claim_theorem_traceability.get("proof_strength_certificate_present")
        == proof_traceability.get("remaining_claim_boundary", {}).get(
            "proof_strength_certificate_present"
        )
        is True,
        "proof-claim proof-structure statement not carried into review",
    )
    checks.check(
        "Proof-claim proof-structure statement present: `True`."
        in report_md,
        "review markdown missing proof-claim proof-structure statement",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_full_residual_bridge_present")
        == proof_claim_theorem_traceability.get("full_residual_bridge_present")
        == proof_traceability.get("remaining_claim_boundary", {}).get(
            "full_residual_bridge_present"
        )
        is True,
        "proof-claim full residual bridge not carried into review",
    )
    checks.check(
        "Proof-claim full 132-row residual-defect bridge present: `True`."
        in report_md,
        "review markdown missing proof-claim full residual bridge",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_route_exclusivity_boundary_present")
        == proof_claim_theorem_traceability.get("route_exclusivity_boundary_present")
        == proof_traceability.get("remaining_claim_boundary", {}).get(
            "route_exclusivity_boundary_present"
        )
        is True,
        "proof-claim route-exclusivity boundary not carried into review",
    )
    checks.check(
        "Proof-claim route-exclusivity nonmixing boundary present: `True`."
        in report_md,
        "review markdown missing proof-claim route-exclusivity boundary",
    )
    checks.check(
        proof_checks.get(
            "proof_claim_traceability_theorem_residual_certificate_exclusivity_present"
        )
        == proof_claim_theorem_traceability.get(
            "theorem_residual_certificate_exclusivity_present"
        )
        == proof_traceability.get("remaining_claim_boundary", {}).get(
            "theorem_residual_certificate_exclusivity_present"
        )
        is True,
        "proof-claim theorem residual-certificate exclusivity not carried into review",
    )
    checks.check(
        "Proof-claim theorem residual-certificate exclusivity present: `True`."
        in report_md,
        "review markdown missing proof-claim theorem residual-certificate exclusivity",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_theorem_assumptions")
        == proof_traceability.get("theorem_assumption_count")
        == 7,
        "proof-claim traceability assumption count changed",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_unsatisfied_assumptions")
        == proof_traceability.get("unsatisfied_theorem_assumption_count")
        == 6,
        "proof-claim traceability unsatisfied assumption count changed",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_satisfied_assumptions")
        == proof_traceability.get("theorem_assumption_count")
        - proof_traceability.get("unsatisfied_theorem_assumption_count")
        == 1,
        "proof-claim traceability satisfied assumption count changed",
    )
    proof_claim_remaining_boundary = proof_traceability.get("remaining_claim_boundary", {})
    checks.check(
        proof_checks.get("proof_claim_traceability_remaining_boundary_status")
        == proof_claim_remaining_boundary.get("status")
        == "theorem_conditions_retained_not_submission_ready",
        "proof-claim remaining boundary status not carried into review",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_submission_satisfied_assumption_ids")
        == proof_claim_remaining_boundary.get("submission_satisfied_ids")
        == ["P5"],
        "proof-claim satisfied assumption IDs not carried into review",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_retained_or_open_assumption_ids")
        == proof_claim_remaining_boundary.get("retained_or_open_ids")
        == ["P1", "P2", "P3", "P4", "P6", "P7"],
        "proof-claim retained-interface/open-nonpromotion IDs not carried into review",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_retained_theorem_interface_ids")
        == proof_claim_remaining_boundary.get("retained_theorem_interface_ids")
        == ["P1", "P2", "P3", "P4", "P6"],
        "proof-claim retained theorem-interface IDs not carried into review",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_open_nonpromotion_boundary_ids")
        == proof_claim_remaining_boundary.get("open_nonpromotion_boundary_ids")
        == ["P7"],
        "proof-claim open output-boundary IDs not carried into review",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_retained_theorem_interface_count")
        == proof_claim_remaining_boundary.get("retained_theorem_interface_count")
        == 5,
        "proof-claim retained theorem-interface count not carried into review",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_open_nonpromotion_boundary_count")
        == proof_claim_remaining_boundary.get("open_nonpromotion_boundary_count")
        == 1,
        "proof-claim open output-boundary count not carried into review",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_remaining_global_boundaries")
        == proof_claim_remaining_boundary.get("global_submission_boundaries_retained")
        == [
            "full_source_policy_package_ready",
            "theorem_level_eta_h_solver_policy_evidence",
            "closed_residual_to_error_theorem_for_mechanism_rows",
        ],
        "proof-claim remaining global boundaries not carried into review",
    )
    proof_claim_writing_card = proof_traceability.get("proof_writing_boundary_card", {})
    checks.check(
        proof_checks.get("proof_claim_traceability_writing_card_status")
        == proof_claim_writing_card.get("status")
        == "conditional_theorem_traceable_direct_pc2_closed_global_boundaries_retained",
        "proof-claim writing boundary card status not carried into review",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_writing_card_safe_claim")
        == proof_claim_writing_card.get("safe_reader_claim")
        == (
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
        ),
        "proof-claim writing boundary card safe claim not carried into review",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_writing_card_forbidden_claims")
        == proof_claim_writing_card.get("forbidden_reader_claims")
        == [
            "unconditional theorem without theorem-domain interfaces",
            "eta_h solver-policy condition closed",
            "fixed-tolerance runs as asymptotic proof",
            "accepted residual-to-error transfer theorem for mechanism rows",
            "source-policy/full-TFE package readiness",
            "mixing direct and primitive-route residual certificates to lower constants, remove P6, or prove a P7 residual-to-error transfer theorem",
        ],
        "proof-claim writing boundary card forbidden claims not carried into review",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_reader_facing_manuscript_boundary_present")
        == proof_claim_writing_card.get("reader_facing_manuscript_boundary_present")
        == proof_traceability.get("remaining_claim_boundary", {}).get(
            "reader_facing_manuscript_boundary_present"
        )
        == proof_traceability.get("summary", {}).get("reader_facing_proof_claim_boundary_present")
        == strict_proof_audit.get("manuscript_theorem_traceability", {}).get(
            "reader_facing_manuscript_boundary_present"
        )
        is True,
        "proof-claim reader-facing manuscript/PDF boundary not carried into review",
    )
    checks.check(
        "Proof-claim reader-facing manuscript/PDF boundary present: `True`." in report_md,
        "review markdown missing proof-claim reader-facing boundary",
    )
    proof_claim_anchor_map = proof_traceability.get("manuscript_anchor_map", {})
    checks.check(
        proof_checks.get("proof_claim_traceability_manuscript_anchor_map_present")
        == proof_claim_anchor_map.get("all_label_anchors_present")
        is True,
        "proof-claim manuscript anchor map not carried into review",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_manuscript_anchor_label_count")
        == proof_claim_anchor_map.get("label_anchor_count")
        == 24,
        "proof-claim manuscript anchor label count not carried into review",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_theorem_assumption_anchor_map_present")
        == proof_claim_anchor_map.get("all_theorem_assumption_anchors_present")
        is True,
        "proof-claim theorem-assumption anchor map not carried into review",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_theorem_assumption_anchor_count")
        == proof_claim_anchor_map.get("theorem_assumption_anchor_count")
        == 7,
        "proof-claim theorem-assumption anchor count not carried into review",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_theorem_assumption_anchor_ids")
        == proof_claim_anchor_map.get("theorem_assumption_anchor_ids")
        == ["P1", "P2", "P3", "P4", "P5", "P6", "P7"],
        "proof-claim theorem-assumption anchor IDs not carried into review",
    )
    proof_closure_anchor_map = proof_closure.get("manuscript_anchor_map", {})
    checks.check(
        proof_checks.get("proof_closure_manuscript_anchor_map_present")
        == proof_closure_anchor_map.get("all_label_anchors_present")
        is True,
        "proof-closure manuscript anchor map not carried into review",
    )
    checks.check(
        proof_checks.get("proof_closure_manuscript_anchor_label_count")
        == proof_closure_anchor_map.get("label_anchor_count")
        == 24,
        "proof-closure manuscript anchor label count not carried into review",
    )
    checks.check(
        proof_checks.get("proof_closure_theorem_assumption_anchor_map_present")
        == proof_closure_anchor_map.get("all_theorem_assumption_anchors_present")
        is True,
        "proof-closure theorem-assumption anchor map not carried into review",
    )
    checks.check(
        proof_checks.get("proof_closure_theorem_assumption_anchor_count")
        == proof_closure_anchor_map.get("theorem_assumption_anchor_count")
        == 7,
        "proof-closure theorem-assumption anchor count not carried into review",
    )
    checks.check(
        proof_checks.get("proof_closure_theorem_assumption_anchor_ids")
        == proof_closure_anchor_map.get("theorem_assumption_anchor_ids")
        == ["P1", "P2", "P3", "P4", "P5", "P6", "P7"],
        "proof-closure theorem-assumption anchor IDs not carried into review",
    )
    checks.check(
        proof_checks.get("proof_closure_proof_claim_anchor_maps_match") is True
        and proof_closure_anchor_map == proof_claim_anchor_map,
        "proof-closure/proof-claim manuscript anchor maps diverged in review",
    )
    checks.check(
        proof_checks.get("proof_contract_anchor_evidence_sources")
        == proof_gate.get("manuscript_theorem_traceability", {}).get("anchor_evidence_sources")
        == expected_anchor_evidence_sources,
        "proof-contract anchor evidence sources not carried into review",
    )
    checks.check(
        proof_checks.get("proof_style_anchor_evidence_sources")
        == proof_style.get("proof_contract_theorem_traceability", {}).get("anchor_evidence_sources")
        == expected_anchor_evidence_sources,
        "proof-style anchor evidence sources not carried into review",
    )
    checks.check(
        proof_checks.get("strict_proof_anchor_evidence_sources")
        == strict_proof_audit.get("manuscript_theorem_traceability", {}).get("anchor_evidence_sources")
        == expected_anchor_evidence_sources,
        "strict-proof anchor evidence sources not carried into review",
    )
    checks.check(
        proof_checks.get("proof_anchor_evidence_sources_match") is True,
        "review does not enforce proof-contract/style/strict anchor-source agreement",
    )
    checks.check(
        "Proof-claim remaining theorem-boundary partition: `theorem_conditions_retained_not_submission_ready`; satisfied IDs `P5`; retained theorem-interface IDs `P1,P2,P3,P4,P6`; open output-boundary IDs `P7`; global boundaries `full_source_policy_package_ready,theorem_level_eta_h_solver_policy_evidence,closed_residual_to_error_theorem_for_mechanism_rows`."
        in report_md,
        "review markdown missing proof-claim remaining theorem-boundary partition summary",
    )
    checks.check(
        "Proof-claim writing boundary card: `conditional_theorem_traceable_direct_pc2_closed_global_boundaries_retained`; safe claim `conditional order-six theorem under retained P1, P2, and P3 theorem interfaces, the separate P6 solver-scale interface, and the P4 binding convention, with P4's proved 96-row non-dynamic row-local certificate and P5's direct Newton-Euler rows supplying one same-branch 132-row residual bridge; route-exclusivity forbids mixing direct and primitive/Taylor residual certificates to lower constants, remove P6, or prove a P7 residual-to-error transfer theorem; the theorem statement itself consumes only one residual-value certificate, so a future primitive/Taylor certificate may only replace the accepted direct certificate by proving a new same-tuple 132-row residual-value bound; P7 remains a separate output nonclaim/residual-to-error boundary`; forbidden `unconditional theorem without theorem-domain interfaces,eta_h solver-policy condition closed,fixed-tolerance runs as asymptotic proof,accepted residual-to-error transfer theorem for mechanism rows,source-policy/full-TFE package readiness,mixing direct and primitive-route residual certificates to lower constants, remove P6, or prove a P7 residual-to-error transfer theorem`."
        in report_md,
        "review markdown missing proof-claim writing boundary card summary",
    )
    checks.check(
        "Proof anchor evidence sources: contract `PROOF_CLOSURE_MANIFEST.json,PROOF_CLAIM_TRACEABILITY_AUDIT.json`; style `PROOF_CLOSURE_MANIFEST.json,PROOF_CLAIM_TRACEABILITY_AUDIT.json`; strict `PROOF_CLOSURE_MANIFEST.json,PROOF_CLAIM_TRACEABILITY_AUDIT.json`; source match `True`."
        in report_md,
        "review markdown missing proof anchor evidence source summary",
    )
    checks.check(
        "Proof-claim manuscript anchor map: `True`; label anchors `24`; theorem-interface/P7-output-boundary anchors `7`; IDs `P1,P2,P3,P4,P5,P6,P7`."
        in report_md,
        "review markdown missing proof-claim manuscript anchor map summary",
    )
    checks.check(
        "Proof-closure manuscript anchor map: `True`; label anchors `24`; theorem-interface/P7-output-boundary anchors `7`; IDs `P1,P2,P3,P4,P5,P6,P7`; proof-claim map match `True`."
        in report_md,
        "review markdown missing proof-closure manuscript anchor map summary",
    )
    checks.check(
        "Reader-facing theorem-interface split: theorem interfaces `P1--P6`; P7 is an output nonclaim/residual-to-error boundary anchor, not a theorem premise."
        in report_md,
        "review markdown missing reader-facing P1-P6/P7 split",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_close_requirements")
        == proof_traceability.get("close_requirement_count")
        == 4,
        "proof-claim traceability close requirement count changed",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_unsatisfied_close_requirements")
        == proof_traceability.get("unsatisfied_close_requirement_count")
        == 0,
        "proof-claim traceability unsatisfied close requirement count changed",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_satisfied_close_requirements")
        == proof_traceability.get("satisfied_close_requirement_count")
        == 4,
        "proof-claim traceability satisfied close requirement count changed",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_pc3_condition_retained") is True,
        "proof-claim traceability PC3 condition-retained marker changed",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_pc4_residual_promotion_avoided") is True,
        "proof-claim traceability PC4 residual-promotion marker changed",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_newton_euler_open_obligations") == 1,
        "proof-claim traceability Newton-Euler count changed",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_newton_euler_closed_obligations") == 5,
        "proof-claim traceability Newton-Euler closed count changed",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_residual_to_error_blockers") == 7,
        "proof-claim traceability residual-to-error blocker count changed",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_certified_non_dynamic_rows") == 96,
        "proof-claim traceability certified row count changed",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_open_dynamic_rows") == 36,
        "proof-claim traceability open dynamic row count changed",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_row_target_map_present") is True,
        "proof-claim traceability row-target map missing in review",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_newton_euler_symbolic_target_rows")
        == proof_traceability.get("newton_euler_symbolic_target_rows")
        == 36,
        "proof-claim traceability symbolic target row count changed",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_newton_euler_symbolic_target_translational_rows")
        == proof_traceability.get("newton_euler_symbolic_target_translational_rows")
        == 18,
        "proof-claim traceability translational target row count changed",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_newton_euler_symbolic_target_rotational_rows")
        == proof_traceability.get("newton_euler_symbolic_target_rotational_rows")
        == 18,
        "proof-claim traceability rotational target row count changed",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_newton_euler_obligation_coverage_matrix_complete")
        == proof_traceability.get("newton_euler_obligation_coverage_matrix_complete")
        is True,
        "proof-claim traceability obligation coverage matrix missing in review",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_newton_euler_row_obligation_links")
        == proof_traceability.get("newton_euler_row_obligation_links")
        == 180,
        "proof-claim traceability row-obligation link count changed",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_newton_euler_rows_with_complete_obligation_sets")
        == proof_traceability.get("newton_euler_rows_with_complete_obligation_sets")
        == 36,
        "proof-claim traceability complete-row obligation count changed",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_newton_euler_obligations_with_target_rows")
        == proof_traceability.get("newton_euler_obligations_with_target_rows")
        == 6,
        "proof-claim traceability obligation-target count changed",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_newton_euler_obligation_coverage_proof_closure_advanced")
        is False,
        "proof-claim traceability obligation coverage must not close proof",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_newton_euler_symbolic_defect_certificate_complete") is False,
        "proof-claim traceability overclaims symbolic defect certificate",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_open_symbolic_oracle_recorded") is True,
        "proof-claim traceability open symbolic oracle marker missing",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_dynamic_matrix_present")
        == proof_traceability.get("dynamic_proof_closure_matrix_present")
        is True,
        "dynamic-row proof closure matrix not carried into review",
    )
    checks.check(
        proof_checks.get("proof_claim_traceability_dynamic_matrix_status")
        == proof_traceability.get("dynamic_proof_closure_matrix_status")
        == "present_direct_substitution_closure_inputs",
        "dynamic-row proof closure matrix status changed",
    )
    checks.check(
        proof_checks.get("proof_closure_certified_non_dynamic_rows")
        == proof_closure.get("evidence_summary", {}).get("certified_non_dynamic_rows")
        == 96,
        "proof-closure certified row count changed",
    )
    checks.check(
        proof_checks.get("proof_closure_open_dynamic_rows")
        == proof_closure.get("evidence_summary", {}).get("open_dynamic_rows")
        == 36,
        "proof-closure open dynamic row count changed",
    )
    checks.check(
        proof_checks.get("proof_closure_direct_pc2_proof_gap_closed")
        == proof_checks.get("proof_closure_proof_gap_closed")
        == proof_closure.get("closure_state", {}).get("proof_gap_closed")
        is True
        and proof_checks.get("proof_closure_proof_gap_closed_scope")
        == "direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open"
        and "schema-compatible shorthand for direct_pc2_proof_gap_closed"
        in proof_checks.get("proof_closure_proof_gap_closed_reading_rule", ""),
        "proof-closure proof gap must be scoped to direct PC2",
    )
    checks.check(
        proof_checks.get("proof_closure_newton_euler_open_obligations")
        == proof_closure.get("evidence_summary", {}).get("newton_euler_open_obligations")
        == 1,
        "proof-closure Newton-Euler obligation count changed",
    )
    checks.check(
        proof_checks.get("proof_closure_newton_euler_closed_obligations")
        == proof_closure.get("evidence_summary", {}).get("newton_euler_closed_obligations")
        == 5,
        "proof-closure Newton-Euler closed obligation count changed",
    )
    checks.check(
        proof_checks.get("proof_closure_newton_euler_symbolic_target_rows")
        == proof_closure.get("evidence_summary", {}).get("newton_euler_symbolic_target_rows")
        == 36,
        "proof-closure Newton-Euler symbolic target row count changed",
    )
    checks.check(
        proof_checks.get("proof_closure_newton_euler_symbolic_target_translational_rows")
        == proof_closure.get("evidence_summary", {}).get("newton_euler_symbolic_target_translational_rows")
        == 18,
        "proof-closure Newton-Euler translational target row count changed",
    )
    checks.check(
        proof_checks.get("proof_closure_newton_euler_symbolic_target_rotational_rows")
        == proof_closure.get("evidence_summary", {}).get("newton_euler_symbolic_target_rotational_rows")
        == 18,
        "proof-closure Newton-Euler rotational target row count changed",
    )
    checks.check(
        proof_checks.get("proof_closure_newton_euler_obligation_coverage_matrix_complete")
        == proof_closure.get("evidence_summary", {}).get("newton_euler_obligation_coverage_matrix_complete")
        is True,
        "proof-closure Newton-Euler obligation coverage matrix missing",
    )
    checks.check(
        proof_checks.get("proof_closure_newton_euler_row_obligation_links")
        == proof_closure.get("evidence_summary", {}).get("newton_euler_row_obligation_links")
        == 180,
        "proof-closure Newton-Euler row-obligation link count changed",
    )
    checks.check(
        proof_checks.get("proof_closure_newton_euler_rows_with_complete_obligation_sets")
        == proof_closure.get("evidence_summary", {}).get("newton_euler_rows_with_complete_obligation_sets")
        == 36,
        "proof-closure Newton-Euler complete-row obligation count changed",
    )
    checks.check(
        proof_checks.get("proof_closure_newton_euler_obligations_with_target_rows")
        == proof_closure.get("evidence_summary", {}).get("newton_euler_obligations_with_target_rows")
        == 6,
        "proof-closure Newton-Euler obligation-target count changed",
    )
    checks.check(
        proof_checks.get("proof_closure_newton_euler_symbolic_target_inventory_complete") is True,
        "proof-closure Newton-Euler symbolic target inventory marker missing",
    )
    checks.check(
        proof_checks.get("proof_closure_residual_to_error_blocking_obligations")
        == proof_closure.get("evidence_summary", {}).get("residual_to_error_blocking_obligations")
        == 7,
        "proof-closure residual-to-error blocker count changed",
    )
    checks.check(
        proof_checks.get("proof_closure_formula_row_ad_jacobian_probe_count") == 3,
        "proof-closure formula-row AD probe count changed",
    )
    checks.check(proof_checks.get("proof_closure_proof_gap_closed") is True, "proof-closure direct proof gap closure missing")
    checks.check(
        proof_checks.get("proof_closure_dynamic_symbolic_oracle_complete") is False,
        "proof-closure must not close dynamic symbolic oracle",
    )
    checks.check(
        proof_checks.get("proof_closure_stage_residual_O_h7_implementation_defect_proved") is True,
        "proof-closure direct O(h^7) implementation defect proof missing",
    )
    checks.check(
        proof_checks.get("proof_closure_eta_h_O_h7_solver_policy_evidence") is False,
        "proof-closure must not close eta_h proof",
    )
    theorem_boundary = proof_closure.get("theorem_statement_boundary", {})
    manuscript_traceability = proof_closure.get("manuscript_traceability", {})
    checks.check(
        proof_checks.get("proof_closure_theorem_statement_labels_present")
        == theorem_boundary.get("all_required_labels_present_main_and_flat")
        is True,
        "proof-closure theorem labels not carried into review",
    )
    checks.check(
        proof_checks.get("proof_closure_theorem_statement_boundary_present")
        == theorem_boundary.get("conditional_theorem_boundary_present_main_and_flat")
        is True,
        "proof-closure conditional theorem boundary not carried into review",
    )
    checks.check(
        proof_checks.get("proof_closure_theorem_statement_eta_condition_retained")
        == theorem_boundary.get("eta_h_theorem_condition_retained")
        is True,
        "proof-closure eta_h theorem condition not retained in review",
    )
    checks.check(
        proof_checks.get("proof_closure_theorem_statement_eta_evidence_closed")
        == theorem_boundary.get("eta_h_solver_policy_evidence_closed")
        is False,
        "proof-closure eta_h evidence overclaimed in review",
    )
    checks.check(
        proof_checks.get("proof_closure_theorem_statement_fixed_tolerance_asymptotic_proof")
        == theorem_boundary.get("fixed_tolerance_runs_are_asymptotic_proof")
        is False,
        "proof-closure fixed-tolerance evidence promoted to asymptotic proof",
    )
    checks.check(
        proof_checks.get("proof_closure_theorem_statement_residual_to_error_not_promoted")
        == theorem_boundary.get("does_not_promote_residual_to_error")
        is True,
        "proof-closure residual-to-error boundary missing in review",
    )
    checks.check(
        proof_checks.get("proof_closure_theorem_statement_source_policy_or_full_tfe_not_promoted")
        == theorem_boundary.get("does_not_promote_source_policy_or_full_tfe")
        is True,
        "proof-closure source-policy/full-TFE nonpromotion missing in review",
    )
    checks.check(
        proof_checks.get("proof_closure_manuscript_traceability_mapped")
        == manuscript_traceability.get("conditional_proof_claims_mapped_to_manuscript")
        is True,
        "proof-closure manuscript traceability mapping missing in review",
    )
    checks.check(
        proof_checks.get("proof_closure_manuscript_traceability_no_state_change")
        == manuscript_traceability.get("does_not_change_proof_closure_state")
        is True,
        "proof-closure manuscript traceability state-change boundary missing in review",
    )
    checks.check(
        proof_checks.get("proof_closure_manuscript_traceability_dependency_graph_present")
        == manuscript_traceability.get("proof_dependency_graph_present_main_and_flat")
        is True,
        "proof-closure manuscript dependency graph missing in review",
    )
    checks.check(
        proof_checks.get("proof_closure_manuscript_traceability_dynamic_matrix_present")
        == manuscript_traceability.get("dynamic_proof_closure_matrix_present_main_and_flat")
        is True,
        "proof-closure dynamic proof matrix traceability missing in review",
    )
    checks.check(
        proof_checks.get("proof_closure_manuscript_traceability_primitive_lane_boundary_present")
        == manuscript_traceability.get("primitive_lane_boundary_present_main_and_flat")
        is True,
        "proof-closure primitive-route boundary missing in review",
    )
    checks.check(
        proof_checks.get("proof_closure_manuscript_traceability_residual_nonpromotion_present")
        == manuscript_traceability.get("residual_to_error_nonpromotion_present_main_and_flat")
        is True,
        "proof-closure residual nonpromotion traceability missing in review",
    )
    checks.check(proof_checks.get("proof_closure_submission_ready") is False, "proof-closure must not mark submission ready")
    checks.check(proof_checks.get("proof_style_audit_schema") == "cmame-proof-style-audit-v1", "proof-style audit not carried into review")
    checks.check(proof_checks.get("proof_style_reference_checked") is True, "proof-style reference check missing")
    checks.check(proof_checks.get("newton_euler_obligation_table_present") is True, "Newton-Euler obligation table missing in review")
    checks.check(proof_checks.get("newton_euler_obligation_count") == 6, "Newton-Euler obligation count changed in review")
    checks.check(
        proof_checks.get("newton_euler_symbolic_target_audit_schema")
        == newton_euler_symbolic_target.get("schema")
        == "newton-euler-symbolic-target-audit-v1",
        "Newton-Euler symbolic target audit not carried into review",
    )
    checks.check(
        proof_checks.get("newton_euler_symbolic_target_audit_status")
        == "row_level_symbolic_targets_extracted_dynamic_defect_proof_open",
        "Newton-Euler symbolic target audit status changed in review",
    )
    checks.check(
        proof_checks.get("newton_euler_symbolic_target_rows")
        == newton_euler_symbolic_target.get("row_count")
        == 36,
        "Newton-Euler symbolic target row count changed in review",
    )
    checks.check(
        proof_checks.get("newton_euler_symbolic_target_translational_rows")
        == newton_euler_symbolic_target.get("translational_row_count")
        == 18,
        "Newton-Euler translational target row count changed in review",
    )
    checks.check(
        proof_checks.get("newton_euler_symbolic_target_rotational_rows")
        == newton_euler_symbolic_target.get("rotational_row_count")
        == 18,
        "Newton-Euler rotational target row count changed in review",
    )
    checks.check(
        proof_checks.get("newton_euler_symbolic_target_inventory_complete") is True,
        "Newton-Euler symbolic target inventory marker changed in review",
    )
    source_anchors = newton_euler_symbolic_target.get("supporting_runtime_evidence", {}).get(
        "runtime_source_anchors", {}
    )
    checks.check(
        proof_checks.get("newton_euler_symbolic_target_runtime_source_anchors_present") is True,
        "Newton-Euler runtime source anchors missing in review",
    )
    checks.check(
        proof_checks.get("newton_euler_symbolic_target_runtime_source_anchor_path")
        == source_anchors.get("run_v047_path")
        == "v047_cylindrical_chain_pipeline/run_v047.py",
        "Newton-Euler runtime source anchor path changed in review",
    )
    checks.check(
        proof_checks.get("newton_euler_symbolic_target_runtime_source_anchor_tuple_count") == 4,
        "Newton-Euler runtime source tuple-anchor count changed in review",
    )
    checks.check(
        isinstance(proof_checks.get("newton_euler_symbolic_target_runtime_source_anchor_dyn_extend_line"), int)
        and proof_checks.get("newton_euler_symbolic_target_runtime_source_anchor_dyn_extend_line")
        == source_anchors.get("primary_residual_dyn_extend", {}).get("line")
        > 0,
        "Newton-Euler runtime dyn.extend source anchor missing in review",
    )
    checks.check(
        "do not prove symbolic algebraic equivalence"
        in str(proof_checks.get("newton_euler_symbolic_target_runtime_source_anchor_scope")),
        "Newton-Euler runtime source anchor proof boundary missing in review",
    )
    checks.check(
        proof_checks.get("newton_euler_obligation_coverage_matrix_complete")
        == newton_euler_symbolic_target.get("obligation_coverage_matrix", {}).get("coverage_matrix_complete")
        is True,
        "Newton-Euler obligation coverage matrix not carried into review",
    )
    checks.check(
        proof_checks.get("newton_euler_row_obligation_links")
        == newton_euler_symbolic_target.get("obligation_coverage_matrix", {}).get("row_obligation_link_count")
        == 180,
        "Newton-Euler row-obligation link count changed in review",
    )
    checks.check(
        proof_checks.get("newton_euler_rows_with_complete_obligation_sets")
        == newton_euler_symbolic_target.get("obligation_coverage_matrix", {}).get(
            "rows_with_complete_obligation_sets"
        )
        == 36,
        "Newton-Euler complete-row obligation count changed in review",
    )
    checks.check(
        proof_checks.get("newton_euler_obligations_with_target_rows")
        == newton_euler_symbolic_target.get("obligation_coverage_matrix", {}).get("obligations_with_target_rows")
        == 6,
        "Newton-Euler obligation-target count changed in review",
    )
    checks.check(
        proof_checks.get("newton_euler_obligation_coverage_proof_closure_advanced") is False,
        "Newton-Euler obligation coverage must not close proof in review",
    )
    checks.check(
        proof_checks.get("newton_euler_symbolic_defect_certificate_complete") is False,
        "Newton-Euler symbolic target audit overclaims defect certificate in review",
    )
    checks.check(
        proof_checks.get("newton_euler_symbolic_target_stage_residual_O_h7_implementation_defect_proved") is False,
        "Newton-Euler symbolic target audit overclaims O(h^7) defect proof in review",
    )
    checks.check(
        proof_checks.get("newton_euler_symbolic_target_submission_ready") is False,
        "Newton-Euler symbolic target audit must not mark submission ready",
    )
    checks.check(proof_checks.get("proof_style_gap_narrowed") is True, "proof-style gap narrowing missing in review")
    checks.check(
        proof_checks.get("direct_pc2_proof_gap_closed")
        == proof_checks.get("proof_gap_closed")
        is True
        and proof_checks.get("proof_gap_closed_scope")
        == "direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open"
        and "schema-compatible shorthand for direct_pc2_proof_gap_closed"
        in proof_checks.get("proof_gap_closed_reading_rule", ""),
        "review B3 proof-gap closure must be scoped to direct PC2",
    )
    checks.check(proof_checks.get("runtime_ad_oracle_complete") is True, "runtime AD oracle should be recorded complete")
    checks.check(proof_checks.get("dynamic_symbolic_oracle_complete") is False, "dynamic symbolic oracle must remain open")
    checks.check(proof_checks.get("symbolic_oracle_complete") is False, "symbolic oracle must remain open")
    checks.check(
        proof_checks.get("dynamic_oracle_stage_residual_O_h7_symbolic_certificate_proved") is False,
        "symbolic-certificate O(h^7) route must remain open",
    )
    checks.check(
        proof_checks.get("stage_residual_O_h7_implementation_defect_proved") is True,
        "direct-route stage residual O(h^7) proof missing in review",
    )
    expected_solver_scale_narrowed_statuses = {
        row.get("id"): row.get("status")
        for row in blocker.get("blockers", [])
        if isinstance(row, dict) and row.get("id") in {"B4", "B6", "B7"}
    }
    expected_solver_scale_global_boundaries = [
        "full_source_policy_package_ready",
        "theorem_level_eta_h_solver_policy_evidence",
        "closed_residual_to_error_theorem_for_mechanism_rows",
    ]
    checks.check(
        proof_checks.get("solver_scale_submission_ready_scope")
        == solver_scale_audit.get("submission_ready_scope")
        == "solver_scale_global_eta_h_boundary_not_narrowed_claim_package_decision",
        "solver-scale submission-ready scope changed in review",
    )
    checks.check(
        proof_checks.get("solver_scale_audit_scope")
        == solver_scale_audit.get("readiness_boundary", {}).get("solver_scale_audit_scope")
        == "finite_solver_scale_diagnostic_and_theorem_level_eta_h_boundary",
        "solver-scale audit scope changed in review",
    )
    checks.check(
        proof_checks.get("solver_scale_narrowed_claim_b4_b6_b7_statuses")
        == solver_scale_audit.get("readiness_boundary", {}).get("narrowed_claim_b4_b6_b7_statuses")
        == expected_solver_scale_narrowed_statuses
        == {"B4": "closed", "B6": "closed", "B7": "closed"},
        "solver-scale narrowed-claim statuses changed in review",
    )
    checks.check(
        proof_checks.get("solver_scale_global_submission_boundaries_retained")
        == solver_scale_audit.get("readiness_boundary", {}).get("global_submission_boundaries_retained")
        == expected_solver_scale_global_boundaries,
        "solver-scale global boundaries changed in review",
    )
    checks.check(
        proof_checks.get("finite_scaled_tolerance_probe_recorded") is True,
        "finite scaled-tolerance probe marker missing in review",
    )
    checks.check(
        proof_checks.get("finite_scaled_tolerance_probe_ok_rows") == 4,
        "finite scaled-tolerance probe ok rows changed in review",
    )
    checks.check(
        proof_checks.get("finite_scaled_tolerance_probe_total_rows") == 4,
        "finite scaled-tolerance probe total rows changed in review",
    )
    checks.check(
        float(proof_checks.get("finite_scaled_tolerance_probe_max_residual_over_h7", math.inf)) < 1.0e4,
        "finite scaled-tolerance probe max eta-h ratio exceeds c_eta",
    )
    checks.check(
        proof_checks.get("finite_scaled_tolerance_probe_theorem_closed") is False,
        "finite scaled-tolerance probe must not close theorem",
    )
    checks.check(
        proof_checks.get("finite_scaled_tolerance_trajectory_probe_recorded") is True,
        "finite scaled-tolerance trajectory probe marker missing in review",
    )
    checks.check(
        proof_checks.get("finite_scaled_tolerance_trajectory_probe_ok_rows") == 4,
        "finite scaled-tolerance trajectory probe ok rows changed in review",
    )
    checks.check(
        proof_checks.get("finite_scaled_tolerance_trajectory_probe_total_rows") == 4,
        "finite scaled-tolerance trajectory probe total rows changed in review",
    )
    checks.check(
        proof_checks.get("finite_scaled_tolerance_trajectory_probe_steps") == 30,
        "finite scaled-tolerance trajectory probe step count changed in review",
    )
    checks.check(
        float(proof_checks.get("finite_scaled_tolerance_trajectory_probe_max_residual_over_h7", math.inf)) < 1.0e4,
        "finite scaled-tolerance trajectory probe max eta-h ratio exceeds c_eta",
    )
    checks.check(
        proof_checks.get("finite_scaled_tolerance_trajectory_probe_theorem_closed") is False,
        "finite scaled-tolerance trajectory probe must not close theorem",
    )
    checks.check(
        proof_checks.get("finite_tolerance_regime_sweep_recorded") is True,
        "finite tolerance-regime sweep not carried into review",
    )
    checks.check(
        proof_checks.get("finite_tolerance_regime_sweep_policy_count") == 3,
        "finite tolerance-regime policy count changed in review",
    )
    checks.check(
        proof_checks.get("finite_tolerance_regime_sweep_total_rows") == 12,
        "finite tolerance-regime row count changed in review",
    )
    checks.check(
        proof_checks.get("finite_tolerance_regime_sweep_total_steps") == 90,
        "finite tolerance-regime step count changed in review",
    )
    checks.check(
        proof_checks.get("finite_tolerance_regime_sweep_theorem_closed") is False,
        "finite tolerance-regime sweep must not close theorem",
    )
    checks.check(
        proof_checks.get("finite_h_scaled_tolerance_sweep_recorded") is True,
        "finite h-scaled tolerance-regime sweep not carried into review",
    )
    checks.check(
        proof_checks.get("finite_h_scaled_tolerance_sweep_policy_names") == ["scaled_h7_c1e4", "scaled_h8_c1e6"],
        "finite h-scaled tolerance-regime policy names changed in review",
    )
    checks.check(
        proof_checks.get("finite_h_scaled_tolerance_sweep_rows") == 8,
        "finite h-scaled tolerance-regime row count changed in review",
    )
    checks.check(
        proof_checks.get("finite_h_scaled_tolerance_sweep_steps") == 60,
        "finite h-scaled tolerance-regime step count changed in review",
    )
    checks.check(
        float(proof_checks.get("finite_h_scaled_tolerance_sweep_velocity_order_floor", math.nan)) > 6.0,
        "finite h-scaled tolerance-regime velocity order floor too small",
    )
    checks.check(proof_checks.get("scaled_tolerance_sweep_recorded") is False, "scaled tolerance sweep unexpectedly closed")
    external_checks = report.get("external_checks", {})
    authorized_b4 = b4_post_execution_audit.get("verified_authorized_execution_recorded") is True
    expected_b4_scope = (
        "verified_authorized_guarded_driver_execution"
        if authorized_b4
        else "no_verified_current_authorized_execution_record_existing_artifacts_only"
    )
    checks.check(
        external_checks.get("source_policy_diagnosis_schema") == "external-baseline-source-policy-diagnosis-v1",
        "source-policy diagnosis not carried into review",
    )
    checks.check(
        external_checks.get("source_policy_diagnosis_status") == "diagnosis_only_source_policy_recheck_required",
        "source-policy diagnosis status changed",
    )
    checks.check(
        external_checks.get("source_policy_diagnosis_flagged_rows")
        == source_policy_diagnosis.get("coverage", {}).get("flagged_row_count")
        == 15,
        "source-policy diagnosis flagged row count changed",
    )
    checks.check(
        external_checks.get("source_policy_position_aligned_velocity_mismatch_rows")
        == source_policy_diagnosis.get("coverage", {}).get("position_aligned_velocity_mismatch_count")
        == 10,
        "source-policy diagnosis velocity-mismatch count changed",
    )
    checks.check(external_checks.get("source_policy_recheck_required") is True, "source-policy recheck boundary changed")
    checks.check(
        external_checks.get("source_policy_diagnosis_external_superiority_allowed") is False,
        "source-policy diagnosis external superiority boundary changed",
    )
    checks.check(
        external_checks.get("source_policy_diagnosis_b2_b4_status") == "not_closed",
        "source-policy diagnosis B2/B4 status changed",
    )
    checks.check(
        external_checks.get("source_policy_triage_schema") == "source-policy-closure-triage-v1",
        "source-policy triage not carried into review",
    )
    checks.check(
        external_checks.get("source_policy_triage_status") == "triage_only_source_policy_closure_not_run",
        "source-policy triage status changed",
    )
    checks.check(
        external_checks.get("source_policy_triage_flagged_rows")
        == source_policy_triage.get("triage_scope", {}).get("flagged_row_count")
        == 15,
        "source-policy triage flagged row count changed",
    )
    checks.check(
        set(external_checks.get("source_policy_triage_flagged_examples", []))
        == {"single_pendulum", "double_pendulum", "four_link", "slider_crank"},
        "source-policy triage example coverage changed",
    )
    triage_counts = external_checks.get("source_policy_triage_action_counts", {})
    checks.check(
        triage_counts.get("fix_or_rerun_public_velocity_mapping_time_grid_norm_runtime") == 5,
        "source-policy triage RA2021 action count changed",
    )
    checks.check(
        triage_counts.get("resolve_tfe_runner_friction_endpoint_then_rerun_or_demote") == 4,
        "source-policy triage TFE action count changed",
    )
    checks.check(
        triage_counts.get("choose_full_T8_public_policy_or_demote") == 3,
        "source-policy triage HI2022 action count changed",
    )
    checks.check(
        triage_counts.get("demote_until_velocity_partitioning_code_path_resolved") == 3,
        "source-policy triage VP action count changed",
    )
    checks.check(external_checks.get("source_policy_triage_b2_can_close_now") is False, "triage incorrectly closes B2")
    checks.check(external_checks.get("source_policy_triage_b4_can_close_now") is False, "triage incorrectly closes B4")
    checks.check(
        external_checks.get("source_policy_triage_heavy_run_invoked") is False,
        "source-policy triage invoked a heavy run",
    )
    checks.check(
        external_checks.get("source_policy_row_ledger_schema")
        == source_policy_row_ledger.get("schema")
        == "source-policy-row-closure-ledger-v1",
        "source-policy row ledger not carried into review",
    )
    checks.check(
        external_checks.get("source_policy_row_ledger_status") == "row_level_source_policy_closure_open",
        "source-policy row ledger status changed",
    )
    checks.check(
        external_checks.get("source_policy_row_ledger_flagged_rows")
        == source_policy_row_ledger.get("coverage", {}).get("flagged_row_count")
        == 15,
        "source-policy row ledger flagged row count changed",
    )
    checks.check(
        set(external_checks.get("source_policy_row_ledger_flagged_examples", []))
        == {"single_pendulum", "double_pendulum", "four_link", "slider_crank"},
        "source-policy row ledger examples changed",
    )
    row_ledger_counts = external_checks.get("source_policy_row_ledger_action_counts", {})
    checks.check(
        row_ledger_counts.get("fix_or_rerun_public_velocity_mapping_time_grid_norm_runtime") == 5,
        "source-policy row ledger RA2021 action count changed",
    )
    checks.check(
        row_ledger_counts.get("resolve_tfe_runner_friction_endpoint_then_rerun_or_demote") == 4,
        "source-policy row ledger TFE action count changed",
    )
    checks.check(
        row_ledger_counts.get("choose_full_T8_public_policy_or_demote") == 3,
        "source-policy row ledger HI2022 action count changed",
    )
    checks.check(
        row_ledger_counts.get("demote_until_velocity_partitioning_code_path_resolved") == 3,
        "source-policy row ledger VP action count changed",
    )
    row_ledger_dispositions = external_checks.get("source_policy_row_ledger_current_disposition_counts", {})
    checks.check(
        row_ledger_dispositions.get("attempted_not_reproducible_not_promoted") == 7,
        "source-policy row ledger attempted-not-reproducible disposition count changed",
    )
    checks.check(
        external_checks.get("source_policy_row_ledger_attempted_not_reproducible_rows") == 7,
        "source-policy row ledger attempted-not-reproducible row count missing",
    )
    checks.check(
        external_checks.get("source_policy_row_ledger_rows_closed") == 0,
        "source-policy row ledger unexpectedly closes rows",
    )
    checks.check(
        external_checks.get("source_policy_row_ledger_rows_external_superiority_ready") == 0,
        "source-policy row ledger unexpectedly has claim-ready rows",
    )
    checks.check(
        external_checks.get("source_policy_row_ledger_parallel_ready_shards") == 20,
        "source-policy row ledger parallel shard count changed",
    )
    checks.check(
        external_checks.get("source_policy_row_ledger_default_1e_4_required") is False,
        "source-policy row ledger requires default 1e-4",
    )
    checks.check(
        external_checks.get("source_policy_row_ledger_heavy_run_invoked") is False,
        "source-policy row ledger invoked heavy run",
    )
    checks.check(
        external_checks.get("source_policy_row_ledger_b2_can_close_now") is False,
        "source-policy row ledger incorrectly closes B2",
    )
    checks.check(
        external_checks.get("source_policy_row_ledger_b4_can_close_now") is False,
        "source-policy row ledger incorrectly closes B4",
    )
    checks.check(
        external_checks.get("all_examples_source_policy_schema") == "all-examples-source-policy-audit-v1",
        "all-example source-policy audit not carried into review",
    )
    checks.check(
        external_checks.get("all_examples_source_policy_status")
        == "all_flagged_examples_checked_source_policy_reproduction_open",
        "all-example source-policy audit status changed",
    )
    checks.check(
        external_checks.get("all_examples_source_policy_flagged_rows")
        == all_examples_source_policy.get("coverage", {}).get("flagged_row_count")
        == 15,
        "all-example source-policy flagged row count changed",
    )
    checks.check(
        external_checks.get("all_examples_source_policy_flagged_raw_rows")
        == all_examples_source_policy.get("coverage", {}).get("flagged_raw_row_count")
        == 45,
        "all-example source-policy raw row count changed",
    )
    checks.check(
        set(external_checks.get("all_examples_source_policy_flagged_examples", []))
        == {"single_pendulum", "double_pendulum", "four_link", "slider_crank"},
        "all-example source-policy example coverage changed",
    )
    checks.check(
        external_checks.get("all_examples_source_policy_all_four_examples") is True,
        "all-example source-policy coverage marker missing",
    )
    checks.check(
        external_checks.get("all_examples_source_policy_all_three_step_sizes") is True,
        "all-example source-policy three-step marker missing",
    )
    all_examples_suite_counts = external_checks.get("all_examples_source_policy_flagged_by_suite", {})
    checks.check(all_examples_suite_counts.get("ra2021_absolute_coordinate") == 5, "all-example source-policy RA2021 count changed")
    checks.check(all_examples_suite_counts.get("tfe2026_original_pendulum") == 4, "all-example source-policy TFE count changed")
    checks.check(all_examples_suite_counts.get("hi2022_half_implicit") == 3, "all-example source-policy HI2022 count changed")
    checks.check(all_examples_suite_counts.get("vp2024_velocity_partitioning") == 3, "all-example source-policy VP count changed")
    checks.check(
        external_checks.get("all_examples_source_policy_position_velocity_mismatch_rows") == 10,
        "all-example source-policy mismatch count changed",
    )
    checks.check(
        external_checks.get("all_examples_source_policy_rows_closed") is False,
        "all-example source-policy audit incorrectly closes rows",
    )
    checks.check(
        external_checks.get("all_examples_source_policy_b2_can_close_now") is False,
        "all-example source-policy audit incorrectly closes B2",
    )
    checks.check(
        external_checks.get("all_examples_source_policy_b4_can_close_now") is False,
        "all-example source-policy audit incorrectly closes B4",
    )
    checks.check(
        external_checks.get("all_examples_source_policy_heavy_run_invoked") is False,
        "all-example source-policy audit invoked heavy run",
    )
    checks.check(
        external_checks.get("all_examples_source_policy_default_1e_4_required") is False,
        "all-example source-policy audit requires default 1e-4",
    )
    checks.check(
        external_checks.get("suite_disposition_schema") == "external-suite-disposition-audit-v1",
        "suite disposition audit not carried into review",
    )
    checks.check(
        external_checks.get("suite_disposition_status") == "suite_dispositions_defined_not_closed",
        "suite disposition status changed",
    )
    checks.check(
        external_checks.get("suite_disposition_suite_count") == suite_disposition.get("suite_count") == 4,
        "suite disposition count changed",
    )
    checks.check(
        external_checks.get("suite_disposition_accepted_external_superiority_suite_count")
        == suite_disposition.get("accepted_external_superiority_suite_count")
        == 0,
        "suite external-superiority count changed",
    )
    checks.check(
        external_checks.get("suite_disposition_parallel_ready_shards_without_default_1e_4")
        == suite_disposition.get("closure_counts", {}).get("parallel_ready_shards_without_default_1e_4")
        == 20,
        "suite parallel-ready shard count changed",
    )
    checks.check(
        external_checks.get("suite_disposition_b2_can_close_now") is False,
        "suite disposition B2 boundary changed",
    )
    checks.check(
        external_checks.get("suite_disposition_b4_can_close_now") is False,
        "suite disposition B4 boundary changed",
    )
    checks.check(
        external_checks.get("suite_disposition_external_superiority_allowed") is False,
        "suite disposition external-superiority boundary changed",
    )
    checks.check(
        external_checks.get("source_policy_closure_manifest_schema")
        == source_policy_closure_manifest.get("schema")
        == "external-source-policy-closure-manifest-v1",
        "source-policy closure manifest not carried into review",
    )
    checks.check(
        external_checks.get("source_policy_closure_manifest_status")
        == "not_closed_source_policy_reproduction_required",
        "source-policy closure manifest status changed",
    )
    checks.check(
        external_checks.get("source_policy_closure_performance_completed_rows")
        == source_policy_closure_manifest.get("performance_matrix", {}).get("completed_row_count")
        == 32,
        "source-policy closure completed row count changed",
    )
    checks.check(
        external_checks.get("source_policy_closure_performance_total_rows")
        == source_policy_closure_manifest.get("performance_matrix", {}).get("row_count")
        == 48,
        "source-policy closure total row count changed",
    )
    checks.check(
        external_checks.get("source_policy_closure_performance_not_complete_rows")
        == source_policy_closure_manifest.get("performance_matrix", {}).get("not_complete_row_count")
        == 16,
        "source-policy closure not-complete row count changed",
    )
    checks.check(
        external_checks.get("source_policy_closure_strict_external_error_rows")
        == source_policy_closure_manifest.get("common_reference_boundary", {}).get(
            "strict_external_error_claim_allowed_rows"
        )
        == 0,
        "source-policy closure strict external error rows changed",
    )
    checks.check(
        external_checks.get("source_policy_closure_parallel_ready_shards") == 20,
        "source-policy closure parallel shard count changed",
    )
    checks.check(
        external_checks.get("source_policy_closure_b2_can_close_now") is False,
        "source-policy closure incorrectly closes B2",
    )
    checks.check(
        external_checks.get("source_policy_closure_b4_can_close_now") is False,
        "source-policy closure incorrectly closes B4",
    )
    checks.check(
        external_checks.get("source_policy_closure_external_superiority_allowed") is False,
        "source-policy closure external superiority boundary changed",
    )
    checks.check(
        set(external_checks.get("source_policy_closure_runnable_parallel_suites", []))
        == {"ra2021_absolute_coordinate", "hi2022_half_implicit"},
        "source-policy closure runnable suites changed",
    )
    checks.check(
        set(external_checks.get("source_policy_closure_not_ready_or_demote_suites", []))
        == {"tfe2026_original_pendulum", "vp2024_velocity_partitioning"},
        "source-policy closure not-ready suites changed",
    )
    checks.check(
        external_checks.get("external_case_reconciliation_schema")
        == external_case_reconciliation.get("schema")
        == "external-case-evidence-reconciliation-v1",
        "external case reconciliation not carried into review",
    )
    checks.check(
        external_checks.get("external_case_reconciliation_status")
        == "bounded_evidence_present_full_source_policy_campaign_open",
        "external case reconciliation status changed",
    )
    checks.check(
        external_checks.get("external_case_reconciliation_case_status_counts")
        == {"code_path_unresolved": 1, "not_run": 16},
        "external case reconciliation status counts changed",
    )
    checks.check(
        set(external_checks.get("external_case_reconciliation_bounded_suites", []))
        == {"ra2021_absolute_coordinate", "hi2022_half_implicit"},
        "external case reconciliation bounded suites changed",
    )
    checks.check(
        set(external_checks.get("external_case_reconciliation_not_ready_suites", []))
        == {"tfe2026_original_pendulum", "vp2024_velocity_partitioning"},
        "external case reconciliation not-ready suites changed",
    )
    checks.check(
        external_checks.get("external_case_reconciliation_case_not_run_not_zero_evidence") is True,
        "external case reconciliation interpretation missing",
    )
    checks.check(
        external_checks.get("external_case_reconciliation_ra2021_baseline_groups") == 12,
        "external case reconciliation RA2021 baseline group count changed",
    )
    checks.check(
        external_checks.get("external_case_reconciliation_ra2021_baseline_required_groups") == 12,
        "external case reconciliation RA2021 required group count changed",
    )
    checks.check(
        external_checks.get("external_case_reconciliation_ra2021_timing_rows") == 12,
        "external case reconciliation RA2021 timing count changed",
    )
    checks.check(
        external_checks.get("external_case_reconciliation_ra2021_timing_required_rows") == 12,
        "external case reconciliation RA2021 required timing count changed",
    )
    checks.check(
        external_checks.get("external_case_reconciliation_local_dynamic_order_examples") == 0,
        "external case reconciliation local dynamic-order count changed",
    )
    checks.check(
        external_checks.get("external_case_reconciliation_gauss_double_public_policy") is False,
        "external case reconciliation double public-policy marker changed",
    )
    checks.check(
        external_checks.get("external_case_reconciliation_closed_loop_row_kind")
        == "kinematic_reaction_residual_not_true_dynamic_order",
        "external case reconciliation closed-loop row-kind boundary changed",
    )
    checks.check(
        external_checks.get("external_case_reconciliation_rows_closed") == 0,
        "external case reconciliation unexpectedly closed source-policy rows",
    )
    checks.check(
        external_checks.get("external_case_reconciliation_rows_external_superiority_ready") == 0,
        "external case reconciliation unexpectedly marks rows claim-ready",
    )
    checks.check(
        external_checks.get("external_case_reconciliation_accepted_external_dynamic_order_examples") == 0,
        "external case reconciliation accepted dynamic examples changed",
    )
    checks.check(
        external_checks.get("external_case_reconciliation_b2_can_close_now") is False,
        "external case reconciliation incorrectly closes B2",
    )
    checks.check(
        external_checks.get("external_case_reconciliation_b4_can_close_now") is False,
        "external case reconciliation incorrectly closes B4",
    )
    checks.check(
        external_checks.get("external_case_reconciliation_default_1e_4_required") is False,
        "external case reconciliation requires default 1e-4",
    )
    checks.check(
        external_checks.get("external_case_reconciliation_heavy_run_invoked") is False,
        "external case reconciliation invoked heavy run",
    )
    checks.check(
        external_checks.get("hi2022_policy_decision_schema")
        == hi2022_policy_decision.get("schema")
        == "hi2022-policy-decision-audit-v1",
        "HI2022 policy-decision audit not carried into review",
    )
    checks.check(
        external_checks.get("hi2022_policy_decision_status")
        == "bounded_T0p1_rows_complete_full_T8_source_policy_open",
        "HI2022 policy-decision status changed",
    )
    checks.check(external_checks.get("hi2022_bounded_row_count") == 24, "HI2022 bounded row count changed")
    checks.check(external_checks.get("hi2022_bounded_ok_row_count") == 24, "HI2022 bounded ok row count changed")
    checks.check(external_checks.get("hi2022_bounded_group_count") == 8, "HI2022 bounded group count changed")
    checks.check(
        external_checks.get("hi2022_bounded_groups_with_three_step_sizes") == 8,
        "HI2022 three-step group count changed",
    )
    checks.check(external_checks.get("hi2022_bounded_t_end_values") == [0.1], "HI2022 bounded horizon changed")
    checks.check(
        external_checks.get("hi2022_bounded_step_sizes") == [0.005, 0.01, 0.02],
        "HI2022 bounded h-grid changed",
    )
    checks.check(
        external_checks.get("hi2022_full_T8_policy_required") is True,
        "HI2022 full T8 requirement changed",
    )
    checks.check(
        external_checks.get("hi2022_full_T8_policy_completed") is False,
        "HI2022 full T8 policy overclaimed",
    )
    checks.check(
        external_checks.get("hi2022_accepted_for_bounded_evidence") is True,
        "HI2022 bounded evidence acceptance changed",
    )
    checks.check(
        external_checks.get("hi2022_accepted_for_external_superiority") is False,
        "HI2022 external superiority overclaimed",
    )
    checks.check(
        external_checks.get("hi2022_accepted_source_policy_dynamic_order_examples") == 0,
        "HI2022 source-policy dynamic-order count changed",
    )
    checks.check(external_checks.get("hi2022_queue_parallel_shard_count") == 8, "HI2022 shard count changed")
    checks.check(
        external_checks.get("hi2022_decision") == "choose_full_T8_reproduction_or_explicit_demotion",
        "HI2022 decision changed",
    )
    checks.check(external_checks.get("hi2022_default_1e_4_required") is False, "HI2022 default 1e-4 changed")
    checks.check(external_checks.get("hi2022_heavy_run_invoked") is False, "HI2022 heavy run flag changed")
    checks.check(external_checks.get("hi2022_run_v047_invoked") is False, "HI2022 run_v047 flag changed")
    checks.check(
        external_checks.get("hi2022_source_policy_audit_schema")
        == hi2022_source_policy_audit.get("schema")
        == "hi2022-source-policy-row-audit-v1",
        "HI2022 source-policy row audit not carried into review",
    )
    checks.check(
        external_checks.get("hi2022_source_policy_audit_status")
        == "bounded_T0p1_rows_complete_full_T8_source_policy_rows_not_closed",
        "HI2022 source-policy row audit status changed",
    )
    checks.check(
        external_checks.get("hi2022_source_policy_active_b2_flagged_rows")
        == hi2022_source_policy_audit.get("active_b2_flagged_rows")
        == 3,
        "HI2022 source-policy active rows changed",
    )
    checks.check(
        external_checks.get("hi2022_source_policy_bounded_row_count") == 24,
        "HI2022 source-policy bounded row count changed",
    )
    checks.check(
        external_checks.get("hi2022_source_policy_bounded_ok_row_count") == 24,
        "HI2022 source-policy bounded ok count changed",
    )
    checks.check(
        external_checks.get("hi2022_source_policy_bounded_group_count") == 8,
        "HI2022 source-policy bounded group count changed",
    )
    checks.check(
        external_checks.get("hi2022_source_policy_bounded_groups_with_three_step_sizes") == 8,
        "HI2022 source-policy three-step groups changed",
    )
    checks.check(
        external_checks.get("hi2022_source_policy_t8_coarse_rows") == 24,
        "HI2022 T=8 coarse row count changed",
    )
    checks.check(
        external_checks.get("hi2022_source_policy_t8_coarse_ok_rows") == 18,
        "HI2022 T=8 coarse ok row count changed",
    )
    checks.check(
        external_checks.get("hi2022_source_policy_t8_coarse_complete_groups") == 4,
        "HI2022 T=8 coarse complete group count changed",
    )
    checks.check(
        external_checks.get("hi2022_source_policy_t8_coarse_group_count") == 8,
        "HI2022 T=8 coarse group count changed",
    )
    checks.check(
        external_checks.get("hi2022_source_policy_t8_coarse_source_policy_reproduction") is False,
        "HI2022 T=8 coarse overclaims source-policy reproduction",
    )
    checks.check(
        external_checks.get("hi2022_source_policy_t8_coarse_v048_runner_invoked") is True,
        "HI2022 T=8 coarse runner provenance missing",
    )
    checks.check(
        external_checks.get("hi2022_t8_tolerance_repair_schema")
        == hi2022_t8_tolerance_repair_audit.get("schema")
        == "hi2022-t8-tolerance-repair-audit-v1",
        "HI2022 T=8 tolerance-repair audit not carried into review",
    )
    checks.check(
        external_checks.get("hi2022_t8_tolerance_repair_status")
        == "tolerance_repair_attempt_recorded_not_source_policy_closure",
        "HI2022 T=8 tolerance-repair status changed",
    )
    checks.check(
        external_checks.get("hi2022_t8_tolerance_repair_rows")
        == hi2022_t8_tolerance_repair_audit.get("repair_attempt", {}).get("row_count")
        == 12,
        "HI2022 T=8 tolerance-repair row count changed",
    )
    checks.check(
        external_checks.get("hi2022_t8_tolerance_repair_ok_rows")
        == hi2022_t8_tolerance_repair_audit.get("repair_attempt", {}).get("ok_row_count")
        == 7,
        "HI2022 T=8 tolerance-repair ok row count changed",
    )
    checks.check(
        external_checks.get("hi2022_t8_tolerance_repair_complete_groups")
        == hi2022_t8_tolerance_repair_audit.get("repair_attempt", {}).get("complete_form_model_groups")
        == 0,
        "HI2022 T=8 tolerance-repair group closure changed",
    )
    checks.check(
        external_checks.get("hi2022_t8_tolerance_repair_group_count")
        == hi2022_t8_tolerance_repair_audit.get("repair_attempt", {}).get("group_count")
        == 4,
        "HI2022 T=8 tolerance-repair group count changed",
    )
    checks.check(
        external_checks.get("hi2022_t8_tolerance_repair_combined_best_rows")
        == hi2022_t8_tolerance_repair_audit.get("combined_best", {}).get("row_count")
        == 24,
        "HI2022 T=8 tolerance-repair combined row count changed",
    )
    checks.check(
        external_checks.get("hi2022_t8_tolerance_repair_combined_best_ok_rows")
        == hi2022_t8_tolerance_repair_audit.get("combined_best", {}).get("ok_row_count")
        == 19,
        "HI2022 T=8 tolerance-repair combined ok rows changed",
    )
    checks.check(
        external_checks.get("hi2022_t8_tolerance_repair_combined_best_complete_groups")
        == hi2022_t8_tolerance_repair_audit.get("combined_best", {}).get("complete_form_model_groups")
        == 4,
        "HI2022 T=8 tolerance-repair combined group closure changed",
    )
    checks.check(
        external_checks.get("hi2022_t8_tolerance_repair_combined_best_group_count")
        == hi2022_t8_tolerance_repair_audit.get("combined_best", {}).get("group_count")
        == 8,
        "HI2022 T=8 tolerance-repair combined group count changed",
    )
    checks.check(
        external_checks.get("hi2022_t8_tolerance_repair_recovered_rows")
        == hi2022_t8_tolerance_repair_audit.get("combined_best", {}).get("recovered_row_count")
        == 1,
        "HI2022 T=8 tolerance-repair recovered row count changed",
    )
    checks.check(
        external_checks.get("hi2022_t8_tolerance_repair_source_policy_closed") is False,
        "HI2022 T=8 tolerance-repair overclaims source-policy closure",
    )
    checks.check(
        external_checks.get("hi2022_t8_tolerance_repair_external_superiority_allowed") is False,
        "HI2022 T=8 tolerance-repair overclaims external superiority",
    )
    checks.check(
        external_checks.get("hi2022_source_policy_reproduction_rows") == 0,
        "HI2022 source-policy rows unexpectedly closed",
    )
    checks.check(
        external_checks.get("hi2022_source_policy_external_superiority_ready_rows") == 0,
        "HI2022 source-policy claim-ready rows changed",
    )
    checks.check(
        external_checks.get("hi2022_source_policy_can_close_b2_requirement_now") is False,
        "HI2022 source-policy audit incorrectly closes B2",
    )
    checks.check(
        external_checks.get("hi2022_source_policy_default_1e_4_required") is False,
        "HI2022 source-policy audit requires default 1e-4",
    )
    checks.check(
        external_checks.get("hi2022_source_policy_heavy_run_invoked") is False,
        "HI2022 source-policy audit invoked heavy run",
    )
    checks.check(
        external_checks.get("hi2022_source_policy_run_v047_invoked") is False,
        "HI2022 source-policy audit invoked run_v047",
    )
    checks.check(
        external_checks.get("vp2024_disposition_schema")
        == vp2024_disposition.get("schema")
        == "vp2024-code-path-disposition-audit-v1",
        "VP2024 disposition audit not carried into review",
    )
    checks.check(
        external_checks.get("vp2024_disposition_status")
        == "all_four_examples_checked_no_distinct_public_code_unable_to_reproduce_not_promoted",
        "VP2024 disposition status changed",
    )
    checks.check(
        external_checks.get("vp2024_examples_checked")
        == ["single_pendulum", "double_pendulum", "four_link", "slider_crank"],
        "VP2024 example coverage changed",
    )
    checks.check(
        external_checks.get("vp2024_all_four_examples_checked") is True,
        "VP2024 all-four-examples marker missing",
    )
    checks.check(external_checks.get("vp2024_source_policy_rows") == 4, "VP2024 source-policy row count changed")
    checks.check(
        external_checks.get("vp2024_source_policy_code_path_unresolved_rows") == 4,
        "VP2024 unresolved code-path row count changed",
    )
    checks.check(
        external_checks.get("vp2024_source_policy_rows_attempted_not_reproducible") == 4
        and external_checks.get("vp2024_unable_to_reproduce_rows") == 4,
        "VP2024 attempted/unable row count changed",
    )
    checks.check(
        external_checks.get("vp2024_final_nonpublic_code_disposition") == "unable_to_reproduce_not_promoted",
        "VP2024 final nonpublic-code disposition changed",
    )
    checks.check(external_checks.get("vp2024_common_reference_proxy_rows") == 4, "VP2024 proxy row count changed")
    checks.check(
        external_checks.get("vp2024_common_reference_local_order_wins") == 4,
        "VP2024 common-reference order wins changed",
    )
    checks.check(
        external_checks.get("vp2024_common_reference_local_error_wins") == 4,
        "VP2024 common-reference error wins changed",
    )
    checks.check(external_checks.get("vp2024_large_step_local_order_wins") == 4, "VP2024 large-step order wins changed")
    checks.check(external_checks.get("vp2024_large_step_local_error_wins") == 1, "VP2024 large-step error boundary changed")
    checks.check(
        external_checks.get("vp2024_large_step_noncontrolling") is True,
        "VP2024 large-step diagnostic not marked noncontrolling",
    )
    checks.check(
        external_checks.get("vp2024_distinct_public_code_path_found") is False,
        "VP2024 distinct public code path unexpectedly found",
    )
    checks.check(
        external_checks.get("vp2024_public_code_recheck_status")
        == vp2024_public_code_recheck.get("status")
        == "public_code_rechecked_no_distinct_vp2024_path_attempted_not_reproducible",
        "VP2024 public-code recheck status not carried into review",
    )
    checks.check(
        external_checks.get("vp2024_public_code_recheck_date")
        == vp2024_public_code_recheck.get("date_checked")
        == "2026-06-13",
        "VP2024 public-code recheck date changed",
    )
    checks.check(
        external_checks.get("vp2024_public_code_recheck_tree_truncated")
        == vp2024_public_code_recheck.get("coverage", {}).get("tree_truncated")
        is False,
        "VP2024 public-code recheck tree-truncated boundary changed",
    )
    checks.check(
        external_checks.get("vp2024_public_code_recheck_tree_total_paths")
        == vp2024_public_code_recheck.get("coverage", {}).get("tree_total_paths")
        == 4487,
        "VP2024 public-code recheck total paths changed",
    )
    checks.check(
        external_checks.get("vp2024_public_code_recheck_year2024_paths")
        == vp2024_public_code_recheck.get("coverage", {}).get("year2024_path_count")
        == 1540,
        "VP2024 public-code recheck 2024 path count changed",
    )
    checks.check(
        external_checks.get("vp2024_public_code_recheck_keyword_hits")
        == vp2024_public_code_recheck.get("coverage", {}).get("keyword_path_hit_count")
        == 0,
        "VP2024 public-code recheck keyword hit count changed",
    )
    checks.check(
        external_checks.get("vp2024_public_code_recheck_attempted_not_reproducible_rows")
        == vp2024_public_code_recheck.get("coverage", {}).get("source_policy_rows_attempted_not_reproducible")
        == 4,
        "VP2024 public-code recheck attempted-not-reproducible rows changed",
    )
    checks.check(
        external_checks.get("vp2024_public_code_recheck_source_policy_rows_closed")
        == vp2024_public_code_recheck.get("coverage", {}).get("source_policy_rows_closed")
        == 0,
        "VP2024 public-code recheck overclosed rows",
    )
    checks.check(
        external_checks.get("source_policy_public_code_refresh_status")
        == source_policy_public_code_refresh.get("status"),
        "source-policy public-code refresh status missing from review",
    )
    checks.check(
        external_checks.get("source_policy_public_code_refresh_rows")
        == source_policy_public_code_refresh.get("row_count")
        == 20,
        "source-policy public-code refresh row count changed in review",
    )
    checks.check(
        external_checks.get("source_policy_public_code_refresh_public_code_available_rows")
        == source_policy_public_code_refresh.get("public_code_available_rows")
        == 0,
        "source-policy public-code refresh unexpectedly found public-code rows in review",
    )
    checks.check(
        external_checks.get("source_policy_public_code_refresh_self_reproduction_attempted_rows")
        == source_policy_public_code_refresh.get("self_reproduction_attempted_rows")
        == 20,
        "source-policy public-code refresh attempted rows changed in review",
    )
    checks.check(
        external_checks.get("source_policy_public_code_refresh_unable_to_reproduce_rows")
        == source_policy_public_code_refresh.get("unable_to_reproduce_rows")
        == 20,
        "source-policy public-code refresh unable rows changed in review",
    )
    checks.check(
        external_checks.get("source_policy_public_code_refresh_source_policy_rows_closed")
        == source_policy_public_code_refresh.get("source_policy_rows_closed")
        == 0,
        "source-policy public-code refresh overclosed rows in review",
    )
    checks.check(
        external_checks.get("source_policy_public_code_refresh_latest_status")
        == source_policy_public_code_refresh_latest.get("status")
        == "public_code_refresh_20260620_no_positive_new_source_artifact_rows_remain_unable_to_reproduce",
        "latest source-policy public-code refresh status missing from review",
    )
    checks.check(
        external_checks.get("source_policy_public_code_refresh_latest_date")
        == source_policy_public_code_refresh_latest.get("date_checked")
        == "2026-06-20",
        "latest source-policy public-code refresh date changed in review",
    )
    checks.check(
        external_checks.get("source_policy_public_code_refresh_latest_rows")
        == source_policy_public_code_refresh_latest.get("row_count")
        == 20,
        "latest source-policy public-code refresh row count changed in review",
    )
    checks.check(
        external_checks.get("source_policy_public_code_refresh_latest_current_queries")
        == source_policy_public_code_refresh_latest.get("current_query_count")
        == 11,
        "latest source-policy public-code refresh query count changed in review",
    )
    checks.check(
        external_checks.get("source_policy_public_code_refresh_latest_positive_artifact_rows")
        == source_policy_public_code_refresh_latest.get("positive_public_code_artifact_rows")
        == 0,
        "latest source-policy public-code refresh found positive artifact rows unexpectedly in review",
    )
    checks.check(
        external_checks.get("source_policy_public_code_refresh_latest_source_policy_rows_closed")
        == source_policy_public_code_refresh_latest.get("source_policy_rows_closed")
        == 0,
        "latest source-policy public-code refresh overclosed rows in review",
    )
    checks.check(
        external_checks.get("source_policy_public_code_refresh_latest_source_policy_rows_promoted")
        == source_policy_public_code_refresh_latest.get("source_policy_rows_promoted")
        == 0,
        "latest source-policy public-code refresh overpromoted rows in review",
    )
    checks.check(
        external_checks.get("vp2024_public_code_recheck_external_superiority_allowed")
        == vp2024_public_code_recheck.get("claim_boundary", {}).get("external_superiority_claim_allowed")
        is False,
        "VP2024 public-code recheck external-superiority boundary changed",
    )
    checks.check(
        external_checks.get("vp2024_proxy_is_source_policy_reproduction") is False,
        "VP2024 proxy incorrectly promoted to source policy",
    )
    checks.check(
        external_checks.get("vp2024_claim_allowed_now") == "code-path-unresolved_related_work_only",
        "VP2024 claim boundary changed",
    )
    checks.check(
        external_checks.get("vp2024_default_1e_4_required") is False,
        "VP2024 disposition requires default 1e-4",
    )
    checks.check(
        external_checks.get("vp2024_heavy_run_invoked") is False,
        "VP2024 disposition invoked heavy run",
    )
    checks.check(
        external_checks.get("vp2024_run_v047_invoked") is False,
        "VP2024 disposition invoked run_v047",
    )
    checks.check(
        external_checks.get("vp2024_local_sbel_top_level_directories") == ["2021", "2022"],
        "VP2024 local sbel directory scan changed",
    )
    checks.check(
        external_checks.get("vp2024_local_sbel_year_2024_directory_present") is False,
        "VP2024 local scan unexpectedly found 2024 directory",
    )
    local_mbd_roots = set(external_checks.get("vp2024_local_visible_mbd_code_roots", []))
    checks.check(
        "2021/ASME/rA-formulation" in local_mbd_roots
        and "2022/HalfImplicit_JCND" in local_mbd_roots,
        "VP2024 local scan lost visible MBD roots",
    )
    checks.check(
        external_checks.get("vp2024_local_velocity_partition_term_hit_count") == 0,
        "VP2024 local scan unexpectedly found velocity-partition hits",
    )
    checks.check(
        external_checks.get("vp2024_local_distinct_vp2024_code_path_found") is False,
        "VP2024 local scan unexpectedly resolved the source code path",
    )
    checks.check(
        external_checks.get("vp2024_local_public_metadata_visible_non_git_file_count") == 0,
        "VP2024 local public-metadata visibility boundary changed",
    )
    checks.check(
        external_checks.get("external_suite_demotion_schema")
        == external_suite_demotion.get("schema")
        == "external-suite-demotion-ledger-v1",
        "external-suite demotion ledger not carried into review",
    )
    checks.check(
        external_checks.get("external_suite_demotion_status")
        == "all_external_suites_demoted_from_external_superiority_scope",
        "external-suite demotion status changed",
    )
    checks.check(
        external_checks.get("external_suite_demotion_demoted_suite_count")
        == external_suite_demotion.get("demoted_suite_count")
        == 4,
        "external-suite demotion count changed",
    )
    checks.check(
        external_checks.get("external_suite_demotion_b2_closed_subrequirements")
        == external_suite_demotion.get("b2_subrequirements_closed_by_demotion")
        == [
            "vp2024_code_resolution_or_demotion",
            "hi2022_public_code_same_test_rows",
            "ra2021_public_code_same_test_rows",
            "original_tfe_pendulum_error_order_work_rows",
        ],
        "external-suite demotion B2 closed subrequirements changed",
    )
    checks.check(
        external_checks.get("external_suite_demotion_b2_remaining_required")
        == external_suite_demotion.get("b2_required_to_close_after_demotions")
        == [],
        "external-suite demotion B2 remaining requirements changed",
    )
    checks.check(
        external_checks.get("external_suite_demotion_vp2024_demoted_rows")
        == external_suite_demotion.get("vp2024_demoted_source_policy_rows")
        == 4,
        "external-suite demotion VP2024 row count changed",
    )
    checks.check(
        external_checks.get("external_suite_demotion_vp2024_demoted_flagged_rows")
        == external_suite_demotion.get("vp2024_demoted_source_policy_flagged_rows")
        == 3,
        "external-suite demotion VP2024 flagged-row count changed",
    )
    checks.check(
        external_checks.get("external_suite_demotion_hi2022_demoted_rows")
        == external_suite_demotion.get("hi2022_demoted_source_policy_rows")
        == 3,
        "external-suite demotion HI2022 row count changed",
    )
    checks.check(
        external_checks.get("external_suite_demotion_hi2022_demoted_flagged_rows")
        == external_suite_demotion.get("hi2022_demoted_source_policy_flagged_rows")
        == 3,
        "external-suite demotion HI2022 flagged-row count changed",
    )
    checks.check(
        external_checks.get("external_suite_demotion_active_flagged_rows")
        == external_suite_demotion.get("active_source_policy_flagged_rows_after_demotions")
        == 0,
        "external-suite demotion active flagged-row count changed",
    )
    checks.check(
        external_checks.get("external_suite_demotion_remaining_open_suites", [])
        == external_suite_demotion.get("remaining_open_suites", [])
        == [],
        "external-suite demotion remaining open suites changed",
    )
    checks.check(
        external_checks.get("external_suite_demotion_external_superiority_allowed") is False,
        "external-suite demotion overclaims external superiority",
    )
    checks.check(
        external_checks.get("external_suite_demotion_default_1e_4_required") is False,
        "external-suite demotion requires default 1e-4",
    )
    checks.check(
        external_checks.get("external_suite_demotion_heavy_run_invoked") is False,
        "external-suite demotion invoked heavy run",
    )
    checks.check(
        external_checks.get("external_suite_demotion_run_v047_invoked") is False,
        "external-suite demotion invoked run_v047",
    )
    checks.check(
        external_checks.get("b2_remaining_work_schema")
        == b2_remaining_work.get("schema")
        == "b2-source-policy-remaining-work-manifest-v1",
        "B2 remaining-work manifest not carried into review",
    )
    checks.check(
        external_checks.get("b2_remaining_work_status")
        == "route_b_all_external_suites_demoted_no_active_external_superiority_rows",
        "B2 remaining-work status changed",
    )
    checks.check(external_checks.get("b2_remaining_work_row_count") == 15, "B2 remaining-work row count changed")
    checks.check(
        external_checks.get("b2_remaining_work_active_flagged_rows") == 0,
        "B2 active flagged rows changed",
    )
    checks.check(
        external_checks.get("b2_remaining_work_demoted_flagged_rows") == 15,
        "B2 demoted flagged rows changed",
    )
    checks.check(
        external_checks.get("b2_remaining_work_source_policy_closed_rows") == 0,
        "B2 source-policy rows unexpectedly closed",
    )
    checks.check(
        external_checks.get("b2_remaining_work_external_superiority_ready_rows") == 0,
        "B2 external-superiority-ready rows unexpectedly present",
    )
    checks.check(
        external_checks.get("b2_remaining_work_active_suite_counts") == {},
        "B2 active suite counts changed",
    )
    checks.check(
        external_checks.get("b2_remaining_work_demoted_suite_counts")
        == {
            "hi2022_half_implicit": 3,
            "ra2021_absolute_coordinate": 5,
            "tfe2026_original_pendulum": 4,
            "vp2024_velocity_partitioning": 3,
        },
        "B2 demoted suite counts changed",
    )
    checks.check(
        external_checks.get("b2_remaining_work_closed_by_demotion")
        == [
            "vp2024_code_resolution_or_demotion",
            "hi2022_public_code_same_test_rows",
            "ra2021_public_code_same_test_rows",
            "original_tfe_pendulum_error_order_work_rows",
        ],
        "B2 closed-by-demotion list changed",
    )
    checks.check(external_checks.get("b2_remaining_work_remaining_requirements") == [], "B2 remaining required list changed")
    checks.check(
        external_checks.get("b2_remaining_work_default_1e_4_required") is False,
        "B2 remaining-work requires default 1e-4",
    )
    checks.check(
        external_checks.get("b2_remaining_work_heavy_run_invoked") is False,
        "B2 remaining-work invoked heavy run",
    )
    checks.check(
        external_checks.get("b2_remaining_work_run_v047_invoked") is False,
        "B2 remaining-work invoked run_v047",
    )
    checks.check(
        external_checks.get("b2_closure_execution_plan_schema")
        == b2_remaining_work.get("closure_execution_plan", {}).get("schema")
        == "b2-source-policy-closure-execution-plan-v1",
        "B2 closure execution plan not carried into review",
    )
    checks.check(
        external_checks.get("b2_closure_execution_plan_lane_count") == 0,
        "B2 closure execution plan lane count changed",
    )
    checks.check(
        external_checks.get("b2_closure_execution_plan_all_active_suites_ready") is True,
        "B2 closure plan should have no active launch blockers after Route B demotion",
    )
    checks.check(
        external_checks.get("b2_closure_execution_plan_explicit_1e_4_opt_in") is True,
        "B2 closure plan lost explicit 1e-4 opt-in guard",
    )
    checks.check(
        external_checks.get("b2_closure_execution_plan_external_superiority_after_plan_only") is False,
        "B2 closure plan overclaims plan-only superiority",
    )
    checks.check(
        external_checks.get("b4_work_precision_plan_schema")
        == b4_work_precision_plan.get("schema")
        == "b4-source-policy-work-precision-execution-plan-v1",
        "B4 work/precision plan not carried into review",
    )
    checks.check(
        external_checks.get("b4_work_precision_plan_status")
        == b4_work_precision_plan.get("status")
        == "execution_plan_ready_b4_b7_remain_open",
        "B4 work/precision plan status changed",
    )
    checks.check(
        external_checks.get("b4_work_precision_plan_open_blockers") == [],
        "B4 work/precision open blockers changed",
    )
    checks.check(
        external_checks.get("b4_work_precision_plan_source_policy_rows_closed") == 0
        and external_checks.get("b4_work_precision_plan_source_policy_rows_total") == 40,
        "B4 work/precision source-policy row counts changed",
    )
    checks.check(
        external_checks.get("b4_work_precision_plan_ready_lanes") == 2
        and external_checks.get("b4_work_precision_plan_not_ready_lanes") == 2,
        "B4 work/precision lane readiness changed",
    )
    checks.check(
        external_checks.get("b4_work_precision_plan_heavy_run_invoked") is False,
        "B4 work/precision plan invoked heavy run",
    )
    checks.check(
        external_checks.get("b4_work_precision_plan_run_v047_invoked") is False,
        "B4 work/precision plan invoked run_v047",
    )
    checks.check(
        external_checks.get("b4_work_precision_plan_v048_runner_invoked") is False,
        "B4 work/precision plan invoked v048",
    )
    checks.check(
        external_checks.get("b4_work_precision_plan_next_heavy_requires_user_opt_in") is True,
        "B4 work/precision plan lost user opt-in guard",
    )
    checks.check(
        external_checks.get("b4_work_precision_plan_ra2021_preflight_status")
        == b4_work_precision_plan.get("ra2021_launch_preflight", {}).get("status")
        == "ready_not_run_requires_user_opt_in",
        "B4 RA2021 launch preflight status changed",
    )
    checks.check(
        external_checks.get("b4_work_precision_plan_ra2021_launch_commands") == 5,
        "B4 RA2021 launch command count changed",
    )
    checks.check(
        external_checks.get("b4_work_precision_plan_ra2021_cli_status") == "runner_cli_contract_satisfied",
        "B4 RA2021 CLI contract not satisfied",
    )
    checks.check(
        external_checks.get("b4_work_precision_plan_ra2021_cli_runner_checks") == 4
        and external_checks.get("b4_work_precision_plan_ra2021_cli_command_checks") == 5,
        "B4 RA2021 CLI contract counts changed",
    )
    checks.check(
        external_checks.get("b4_work_precision_plan_hi2022_preflight_status")
        == b4_work_precision_plan.get("hi2022_launch_preflight", {}).get("status")
        == "preflight_ready_existing_selected_candidate_matrix_incomplete",
        "B4 HI2022 launch preflight status changed",
    )
    checks.check(
        external_checks.get("b4_work_precision_plan_hi2022_launch_commands") == 8,
        "B4 HI2022 launch command count changed",
    )
    checks.check(
        external_checks.get("b4_work_precision_plan_hi2022_completed_shards") == 7,
        "B4 HI2022 completed shard count changed",
    )
    checks.check(
        external_checks.get("b4_work_precision_plan_hi2022_missing_shards") == 1,
        "B4 HI2022 missing shard count changed",
    )
    checks.check(
        external_checks.get("b4_work_precision_plan_hi2022_commands_avoid_1e_4") is True,
        "B4 HI2022 commands should avoid 1e-4",
    )
    checks.check(
        external_checks.get("b4_work_precision_plan_hi2022_cli_status") == "runner_cli_contract_satisfied",
        "B4 HI2022 CLI contract not satisfied",
    )
    checks.check(
        external_checks.get("b4_work_precision_plan_hi2022_cli_runner_checks") == 1
        and external_checks.get("b4_work_precision_plan_hi2022_cli_command_checks") == 8,
        "B4 HI2022 CLI contract counts changed",
    )
    checks.check(
        external_checks.get("b4_work_precision_plan_hi2022_source_policy_rows_closed") == 0,
        "B4 HI2022 preflight overclosed source-policy rows",
    )
    checks.check(
        external_checks.get("b4_work_precision_plan_hi2022_closes_b4") is False
        and external_checks.get("b4_work_precision_plan_hi2022_closes_b7") is False,
        "B4 HI2022 preflight overcloses B4/B7",
    )
    checks.check(
        external_checks.get("b4_existing_promotion_audit_schema")
        == b4_existing_promotion_audit.get("schema")
        == "b4-existing-artifact-promotion-audit-v1",
        "B4 existing-artifact promotion audit not carried into review",
    )
    checks.check(
        external_checks.get("b4_existing_promotion_audit_status")
        == b4_existing_promotion_audit.get("status")
        == "no_existing_artifact_promotable_without_new_source_policy_execution",
        "B4 existing-artifact promotion audit status changed",
    )
    checks.check(
        external_checks.get("b4_existing_promotion_candidate_items") == 8
        and external_checks.get("b4_existing_promotion_ready_without_new_execution") == 0,
        "B4 existing-artifact promotion candidate counts changed",
    )
    checks.check(
        external_checks.get("b4_existing_promotion_b4_closing_items") == 0
        and external_checks.get("b4_existing_promotion_b7_closing_items") == 0,
        "B4 existing-artifact promotion audit overcloses B4/B7",
    )
    checks.check(
        external_checks.get("b4_existing_promotion_source_policy_rows_closed") == 0
        and external_checks.get("b4_existing_promotion_source_policy_rows_total") == 40,
        "B4 existing-artifact promotion audit row counts changed",
    )
    checks.check(
        external_checks.get("b4_existing_promotion_b4_can_close_now") is False
        and external_checks.get("b4_existing_promotion_b7_can_close_now") is False,
        "B4 existing-artifact promotion audit changed closure boundary",
    )
    checks.check(
        external_checks.get("b4_existing_promotion_heavy_run_invoked") is False
        and external_checks.get("b4_existing_promotion_run_v047_invoked") is False
        and external_checks.get("b4_existing_promotion_v048_runner_invoked") is False,
        "B4 existing-artifact promotion audit invoked a run",
    )
    checks.check(
        external_checks.get("b4_post_execution_audit_schema")
        == b4_post_execution_audit.get("schema")
        == "b4-source-policy-post-execution-audit-v1",
        "B4 post-execution audit not carried into review",
    )
    checks.check(
        external_checks.get("b4_post_execution_audit_status")
        == b4_post_execution_audit.get("status"),
        "B4 post-execution status changed",
    )
    checks.check(
        external_checks.get("b4_post_execution_approved_driver_execution_recorded")
        == b4_post_execution_audit.get("approved_driver_execution_recorded")
        is authorized_b4,
        "B4 post-execution approved driver marker inconsistent",
    )
    checks.check(
        external_checks.get("b4_post_execution_verified_authorized_execution_recorded")
        == b4_post_execution_audit.get("verified_authorized_execution_recorded")
        is authorized_b4,
        "B4 post-execution verified authorized marker inconsistent",
    )
    checks.check(
        external_checks.get("b4_post_execution_existing_ready_command_artifacts_present")
        == b4_post_execution_audit.get("existing_ready_command_artifacts_present")
        is True,
        "B4 post-execution existing-artifact evidence missing",
    )
    checks.check(
        external_checks.get("b4_post_execution_execution_record_scope")
        == b4_post_execution_audit.get("execution_record_scope")
        == expected_b4_scope,
        "B4 post-execution execution scope changed",
    )
    checks.check(
        external_checks.get("b4_post_execution_outputs_present") is True,
        "B4 post-execution output evidence missing",
    )
    checks.check(
        external_checks.get("b4_post_execution_source_policy_rows_closed") == 0
        and external_checks.get("b4_post_execution_source_policy_rows_total") == 40
        and external_checks.get("b4_post_execution_source_policy_rows_open") == 20,
        "B4 post-execution source-policy row counts changed",
    )
    checks.check(
        external_checks.get("b4_post_execution_b4_can_close_now") is False
        and external_checks.get("b4_post_execution_b7_can_close_now") is False,
        "B4 post-execution audit overcloses B4/B7",
    )
    checks.check(
        external_checks.get("b4_post_execution_external_superiority_allowed") is False,
        "B4 post-execution audit overclaims external superiority",
    )
    checks.check(
        external_checks.get("b4_post_execution_ra2021_double_candidate_status")
        == "executed_order_below_acceptance_not_promoted",
        "B4 post-execution RA2021 double status changed",
    )
    checks.check(
        external_checks.get("b4_post_execution_hi2022_selected_candidate_status")
        == "selected_candidate_matrix_partially_executed_not_promoted",
        "B4 post-execution HI2022 status changed",
    )
    checks.check(
        external_checks.get("b4_post_execution_hi2022_partial_or_failed_shards")
        == ["rA_half:double_pendulum"],
        "B4 post-execution HI2022 partial-shard list changed",
    )
    checks.check(
        external_checks.get("ra_hi_source_policy_post_execution_attempt_certificate_status")
        == ra_hi_post_execution_attempt_certificate.get("status")
        == "post_execution_attempts_recorded_rows_not_promoted_full_source_policy_open",
        "RA/HI post-execution attempt certificate status missing from review",
    )
    checks.check(
        external_checks.get("ra_hi_source_policy_post_execution_attempt_rows") == 20
        and external_checks.get("ra_hi_source_policy_post_execution_attempt_ra_rows") == 12
        and external_checks.get("ra_hi_source_policy_post_execution_attempt_hi_rows") == 8
        and external_checks.get("ra_hi_source_policy_post_execution_attempt_promoted_rows") == 0
        and external_checks.get("ra_hi_source_policy_post_execution_attempt_open_rows") == 20,
        "RA/HI post-execution attempt row counts changed in review",
    )
    checks.check(
        external_checks.get("ra_hi_source_policy_closeout_checklist_schema")
        == ra_hi_source_policy_closeout_checklist.get("schema")
        == "ra-hi-source-policy-closeout-checklist-v1",
        "RA/HI closeout checklist schema missing from review",
    )
    checks.check(
        external_checks.get("ra_hi_source_policy_closeout_checklist_status")
        == ra_hi_source_policy_closeout_checklist.get("status")
        == "ready_for_authorized_execution_closeout_not_executed_not_promoted",
        "RA/HI closeout checklist status missing from review",
    )
    checks.check(
        external_checks.get("ra_hi_source_policy_closeout_total_rows") == 20
        and external_checks.get("ra_hi_source_policy_closeout_ra_rows") == 12
        and external_checks.get("ra_hi_source_policy_closeout_hi_rows") == 8
        and external_checks.get("ra_hi_source_policy_closeout_ready_commands") == 13
        and external_checks.get("ra_hi_source_policy_closeout_mapped_rows") == 20,
        "RA/HI closeout checklist coverage changed in review",
    )
    checks.check(
        external_checks.get("ra_hi_source_policy_closeout_promoted_rows") == 0
        and external_checks.get("ra_hi_source_policy_closeout_completed_rows") == 0
        and external_checks.get("ra_hi_source_policy_closeout_external_ready_rows") == 0,
        "RA/HI closeout checklist overpromotes rows in review",
    )
    checks.check(
        external_checks.get("ra_hi_source_policy_closeout_opt_in_required") is True
        and external_checks.get("ra_hi_source_policy_closeout_execution_invoked") is False,
        "RA/HI closeout checklist execution boundary changed in review",
    )
    checks.check(
        external_checks.get("ra_hi_source_policy_closeout_exact_opt_in")
        == "I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json.",
        "RA/HI closeout checklist exact opt-in phrase missing in review",
    )
    checks.check(
        external_checks.get("ra_hi_source_policy_closeout_b4_can_close") is False
        and external_checks.get("ra_hi_source_policy_closeout_b7_can_close") is False
        and external_checks.get("ra_hi_source_policy_closeout_can_claim_external_superiority") is False,
        "RA/HI closeout checklist overcloses review",
    )
    checks.check(
        external_checks.get("ra_hi_source_policy_output_inventory_status")
        == ra_hi_source_policy_output_inventory.get("status")
        == "existing_expected_outputs_present_not_promotion_evidence",
        "RA/HI output inventory status missing from review",
    )
    checks.check(
        external_checks.get("ra_hi_source_policy_output_inventory_command_count") == 13
        and external_checks.get("ra_hi_source_policy_output_inventory_outputs_existing") == 13
        and external_checks.get("ra_hi_source_policy_output_inventory_summaries_existing") == 8,
        "RA/HI output inventory file counts changed in review",
    )
    checks.check(
        external_checks.get("ra_hi_source_policy_output_inventory_csv_data_rows") == 54
        and external_checks.get("ra_hi_source_policy_output_inventory_hi_ok_rows") == 22
        and external_checks.get("ra_hi_source_policy_output_inventory_closed_rows") == 0,
        "RA/HI output inventory row counts changed in review",
    )
    checks.check(
        external_checks.get("ra_hi_source_policy_promotion_blocker_matrix_status")
        == ra_hi_source_policy_promotion_blocker_matrix.get("status")
        == "ra_hi_public_root_rows_not_promoted_source_policy_open",
        "RA/HI promotion blocker matrix status missing from review",
    )
    checks.check(
        external_checks.get("ra_hi_source_policy_promotion_blocker_matrix_rows") == 20
        and external_checks.get("ra_hi_source_policy_promotion_blocker_matrix_ra_rows") == 12
        and external_checks.get("ra_hi_source_policy_promotion_blocker_matrix_hi_rows") == 8,
        "RA/HI promotion blocker matrix row counts changed in review",
    )
    checks.check(
        external_checks.get("ra_hi_source_policy_promotion_blocker_matrix_public_root_rows") == 20
        and external_checks.get("ra_hi_source_policy_promotion_blocker_matrix_no_public_code_rows") == 0,
        "RA/HI promotion blocker matrix public-root boundary changed in review",
    )
    checks.check(
        external_checks.get("ra_hi_source_policy_promotion_blocker_matrix_closed_rows") == 0
        and external_checks.get("ra_hi_source_policy_promotion_blocker_matrix_not_promoted_rows") == 20
        and external_checks.get("ra_hi_source_policy_promotion_blocker_matrix_attempted_not_reproducible_rows") == 0,
        "RA/HI promotion blocker matrix disposition counts changed in review",
    )
    checks.check(
        external_checks.get("ra_hi_source_policy_promotion_blocker_matrix_current_evidence_terminal_rows") == 20
        and external_checks.get(
            "ra_hi_source_policy_promotion_blocker_matrix_future_authorization_or_artifact_rows"
        )
        == 20
        and external_checks.get("ra_hi_source_policy_promotion_blocker_matrix_reproduction_complete_rows") == 0,
        "RA/HI promotion blocker matrix terminal/reopen counts changed in review",
    )
    checks.check(
        external_checks.get("ra_hi_source_policy_promotion_blocker_matrix_command_mapped_rows") == 20
        and external_checks.get("ra_hi_source_policy_promotion_blocker_matrix_output_present_rows") == 20,
        "RA/HI promotion blocker matrix command/output counts changed in review",
    )
    checks.check(
        external_checks.get("hi2022_ra_half_double_repair_attempt_status")
        == hi2022_ra_half_double_repair_attempt_certificate.get("status")
        == "targeted_repair_attempted_not_reproducible_not_promoted",
        "HI2022 rA_half double repair-attempt certificate status missing from review",
    )
    checks.check(
        external_checks.get("hi2022_ra_half_double_repair_target_ok_rows") == 1
        and external_checks.get("hi2022_ra_half_double_repair_target_failed_rows") == 2,
        "HI2022 rA_half double repair target counts changed in review",
    )
    checks.check(
        external_checks.get("hi2022_ra_half_double_repair_combined_ok_rows") == 19
        and external_checks.get("hi2022_ra_half_double_repair_combined_row_count") == 24
        and external_checks.get("hi2022_ra_half_double_repair_combined_complete_groups") == 4
        and external_checks.get("hi2022_ra_half_double_repair_combined_group_count") == 8,
        "HI2022 rA_half double repair combined counts changed in review",
    )
    checks.check(
        external_checks.get("hi2022_ra_half_double_repair_source_policy_closed") is False
        and external_checks.get("hi2022_ra_half_double_repair_rows_promoted") == 0,
        "HI2022 rA_half double repair overpromoted rows in review",
    )
    checks.check(
        external_checks.get("b4_row_readiness_ledger_schema")
        == b4_row_readiness_ledger.get("schema")
        == "b4-source-policy-row-closure-readiness-ledger-v1",
        "B4 row closure-readiness ledger not carried into review",
    )
    checks.check(
        external_checks.get("b4_row_readiness_ledger_status")
        == b4_row_readiness_ledger.get("status")
        == "all_40_external_rows_mapped_20_attempted_not_reproducible_0_source_policy_rows_closed",
        "B4 row closure-readiness ledger status changed",
    )
    checks.check(
        external_checks.get("b4_row_readiness_external_rows") == 40
        and external_checks.get("b4_row_readiness_expected_external_rows") == 40,
        "B4 row closure-readiness ledger coverage changed",
    )
    checks.check(
        external_checks.get("b4_row_readiness_source_policy_rows_closed") == 0
        and external_checks.get("b4_row_readiness_source_policy_rows_open") == 20,
        "B4 row closure-readiness ledger row counts changed",
    )
    checks.check(
        external_checks.get("b4_row_readiness_rows_with_launch_command_refs") == 20
        and external_checks.get("b4_row_readiness_rows_without_launch_command_refs") == 20,
        "B4 row closure-readiness command mapping changed",
    )
    checks.check(
        external_checks.get("b4_row_readiness_ready_suites") == 2
        and external_checks.get("b4_row_readiness_not_ready_suites") == 2,
        "B4 row closure-readiness suite readiness changed",
    )
    checks.check(
        external_checks.get("b4_row_readiness_b4_can_close_now") is False
        and external_checks.get("b4_row_readiness_b7_can_close_now") is False,
        "B4 row closure-readiness ledger overcloses B4/B7",
    )
    checks.check(
        external_checks.get("b4_row_readiness_heavy_run_invoked") is False
        and external_checks.get("b4_row_readiness_run_v047_invoked") is False
        and external_checks.get("b4_row_readiness_v048_runner_invoked") is False,
        "B4 row closure-readiness ledger invoked a run",
    )
    checks.check(
        external_checks.get("b4_execution_opt_in_packet_schema")
        == b4_execution_opt_in_packet.get("schema")
        == "b4-source-policy-execution-opt-in-packet-v1",
        "B4 execution opt-in packet not carried into review",
    )
    checks.check(
        external_checks.get("b4_execution_opt_in_packet_status")
        == b4_execution_opt_in_packet.get("status")
        == "ready_for_user_opt_in_packet_not_authorized_not_run",
        "B4 execution opt-in packet status changed",
    )
    checks.check(
        external_checks.get("b4_execution_opt_in_explicit_user_opt_in_required") is True,
        "B4 execution opt-in guard missing from review",
    )
    checks.check(
        external_checks.get("b4_execution_opt_in_ready_command_count") == 13
        and external_checks.get("b4_execution_opt_in_mapped_external_rows") == 20
        and external_checks.get("b4_execution_opt_in_unaddressed_external_rows") == 0,
        "B4 execution opt-in packet command/row counts changed",
    )
    checks.check(
        external_checks.get("b4_execution_opt_in_source_policy_rows_closed_now") == 0
        and external_checks.get("b4_execution_opt_in_source_policy_rows_total") == 40,
        "B4 execution opt-in packet source-policy rows changed",
    )
    checks.check(
        external_checks.get("source_policy_execution_handoff_command_traceability_summary")
        == expected_command_traceability,
        "B4 source-policy handoff traceability summary not carried into review",
    )
    checks.check(
        external_checks.get("source_policy_execution_handoff_unique_mapped_row_count")
        == expected_command_traceability.get("unique_mapped_row_count")
        == 20
        and external_checks.get("source_policy_execution_handoff_ra_hi_unique_row_count")
        == expected_command_traceability.get("ra_hi_unique_row_count")
        == 20
        and external_checks.get("source_policy_execution_handoff_ra_hi_unique_rows_all_mapped")
        == expected_command_traceability.get("ra_hi_unique_rows_all_mapped")
        is True,
        "B4 source-policy handoff unique row traceability changed in review",
    )
    checks.check(
        external_checks.get("source_policy_execution_handoff_declared_mapped_row_reference_total")
        == expected_command_traceability.get("declared_mapped_row_reference_total")
        == 32
        and external_checks.get("source_policy_execution_handoff_traced_command_row_reference_total")
        == expected_command_traceability.get("traced_command_row_reference_total")
        == 32
        and external_checks.get("source_policy_execution_handoff_declared_vs_traced_mismatch_count")
        == expected_command_traceability.get("declared_vs_traced_mismatch_count")
        == 0,
        "B4 source-policy handoff row-reference traceability changed in review",
    )
    checks.check(
        external_checks.get("source_policy_execution_handoff_terminal_rows_with_command_refs")
        == expected_command_traceability.get("terminal_rows_with_command_refs")
        == 0
        and external_checks.get("source_policy_execution_handoff_traceability_closed_rows")
        == expected_command_traceability.get("source_policy_closed_rows")
        == 0
        and external_checks.get("source_policy_execution_handoff_traceability_promotion_ready_rows")
        == expected_command_traceability.get("promotion_ready_rows")
        == 0,
        "B4 source-policy handoff terminal/closed traceability changed in review",
    )
    checks.check(
        external_checks.get("b4_execution_opt_in_b4_can_close_after_ready_commands_only") is False
        and external_checks.get("b4_execution_opt_in_b7_can_close_after_ready_commands_only") is False,
        "B4 execution opt-in packet overclaims B4/B7 after commands",
    )
    checks.check(
        external_checks.get("b4_execution_opt_in_execution_invoked_by_packet") is False
        and external_checks.get("b4_execution_opt_in_heavy_run_invoked") is False
        and external_checks.get("b4_execution_opt_in_run_v047_invoked") is False
        and external_checks.get("b4_execution_opt_in_v048_runner_invoked") is False,
        "B4 execution opt-in packet invoked a run",
    )
    promotion_contract = b4_execution_opt_in_packet.get("post_execution_promotion_contract", {})
    checks.check(
        external_checks.get("b4_post_execution_promotion_contract_schema")
        == promotion_contract.get("schema")
        == "b4-source-policy-post-execution-promotion-contract-v1",
        "B4 post-execution promotion contract not carried into review",
    )
    checks.check(
        external_checks.get("b4_post_execution_promotion_contract_status")
        == promotion_contract.get("status")
        == "promotion_contract_defined_no_rows_promoted",
        "B4 post-execution promotion contract status changed",
    )
    checks.check(
        external_checks.get("b4_post_execution_promotion_contract_rows_closed") == 0
        and external_checks.get("b4_post_execution_promotion_contract_rows_total") == 40
        and external_checks.get("b4_post_execution_promotion_contract_ready_mapped_rows") == 20
        and external_checks.get("b4_post_execution_promotion_contract_unaddressed_rows") == 0,
        "B4 post-execution promotion contract row counts changed",
    )
    checks.check(
        external_checks.get("b4_post_execution_promotion_contract_checks_satisfied_now") is False,
        "B4 post-execution promotion contract overclaims checklist satisfaction",
    )
    checks.check(
        external_checks.get("b4_post_execution_promotion_contract_b4_can_close_now") is False
        and external_checks.get("b4_post_execution_promotion_contract_b7_can_close_now") is False,
        "B4 post-execution promotion contract overcloses B4/B7",
    )
    checks.check(
        external_checks.get("b4_post_execution_promotion_contract_ready_lane_count") == 2
        and external_checks.get("b4_post_execution_promotion_contract_not_ready_lane_count") == 2
        and external_checks.get("b4_post_execution_promotion_contract_runner_code_path_gap_rows") == 0,
        "B4 post-execution promotion contract lane/gap counts changed",
    )
    checks.check(
        external_checks.get("claim_demotion_audit_schema")
        == external_superiority_claim_demotion.get("schema")
        == "external-superiority-claim-demotion-audit-v1",
        "claim-demotion audit not carried into review",
    )
    checks.check(
        external_checks.get("claim_demotion_audit_status")
        == external_superiority_claim_demotion.get("status")
        == "route_b_applied_to_claim_boundary_no_external_superiority",
        "claim-demotion audit status changed",
    )
    checks.check(
        external_checks.get("claim_demotion_audit_route_b_ready") is True,
        "claim-demotion Route B ready marker missing",
    )
    checks.check(
        external_checks.get("claim_demotion_audit_route_b_promoted_to_blocker_gate") is True,
        "claim-demotion audit should be synchronized with blocker gate",
    )
    checks.check(
        external_checks.get("claim_demotion_audit_b2_b4_gate_closed_by_this_artifact") is False,
        "claim-demotion audit must not close B2/B4 by itself",
    )
    checks.check(
        external_checks.get("claim_demotion_audit_claim_after_route")
        == "formal_order_and_common_reference_diagnostics_only",
        "claim-demotion claim boundary changed",
    )
    checks.check(
        external_checks.get("claim_demotion_audit_external_superiority_after_route") is False,
        "claim-demotion audit overclaims external superiority",
    )
    checks.check(
        external_checks.get("claim_demotion_audit_source_policy_rows_closed") == 0
        and external_checks.get("claim_demotion_audit_source_policy_total_rows") == 40,
        "claim-demotion audit source-policy row counts changed",
    )
    checks.check(
        external_checks.get("claim_demotion_audit_current_demoted_suites")
        == [
            "hi2022_half_implicit",
            "ra2021_absolute_coordinate",
            "tfe2026_original_pendulum",
            "vp2024_velocity_partitioning",
        ],
        "claim-demotion current demoted suites changed",
    )
    checks.check(
        external_checks.get("claim_demotion_audit_additional_demotions_needed") == [],
        "claim-demotion additional demotions changed",
    )
    checks.check(
        external_checks.get("claim_demotion_audit_full_demotion_scope_after_route_b")
        == [
            "hi2022_half_implicit",
            "ra2021_absolute_coordinate",
            "tfe2026_original_pendulum",
            "vp2024_velocity_partitioning",
        ],
        "claim-demotion full demotion scope changed",
    )
    checks.check(
        external_checks.get("claim_demotion_audit_formal_order_retained") is True,
        "claim-demotion formal-order retention missing",
    )
    checks.check(
        external_checks.get("claim_demotion_audit_common_reference_cells") == 44,
        "claim-demotion common-reference cell count changed",
    )
    checks.check(
        external_checks.get("claim_demotion_audit_direct_order_wins") == 40
        and external_checks.get("claim_demotion_audit_direct_error_wins") == 40,
        "claim-demotion retained win counts changed",
    )
    checks.check(
        external_checks.get("claim_demotion_audit_default_1e_4_required") is False,
        "claim-demotion audit requires default 1e-4",
    )
    checks.check(
        external_checks.get("claim_demotion_audit_heavy_run_invoked") is False,
        "claim-demotion audit invoked heavy run",
    )
    checks.check(
        external_checks.get("claim_demotion_audit_run_v047_invoked") is False,
        "claim-demotion audit invoked run_v047",
    )
    route_b_contract = external_superiority_claim_demotion.get("route_b_application_contract", {})
    checks.check(
        external_checks.get("claim_demotion_route_b_contract_schema")
        == route_b_contract.get("schema")
        == "route-b-application-contract-v1",
        "claim-demotion Route-B contract not carried into review",
    )
    checks.check(
        external_checks.get("claim_demotion_route_b_ready_to_promote")
        == route_b_contract.get("ready_to_promote_to_blocker_gate_now")
        is True,
        "claim-demotion Route-B contract should be ready to promote",
    )
    checks.check(
        external_checks.get("claim_demotion_route_b_safe_to_flip_flags")
        == route_b_contract.get("safe_to_flip_gate_flags_without_other_edits")
        is False,
        "claim-demotion Route-B contract should not allow bare flag flips",
    )
    checks.check(
        external_checks.get("claim_demotion_route_b_satisfied_steps")
        == route_b_contract.get("currently_satisfied_steps")
        == 6,
        "claim-demotion Route-B satisfied step count changed",
    )
    checks.check(
        external_checks.get("claim_demotion_route_b_total_steps")
        == route_b_contract.get("application_step_count")
        == 6,
        "claim-demotion Route-B total step count changed",
    )
    checks.check(
        external_checks.get("claim_demotion_route_b_unsatisfied_steps")
        == route_b_contract.get("unsatisfied_steps")
        == [],
        "claim-demotion Route-B unsatisfied step list changed",
    )
    checks.check(
        external_checks.get("claim_demotion_route_b_creates_numerical_wins")
        == route_b_contract.get("route_b_demotion_contract_creates_numerical_wins")
        is False,
        "claim-demotion Route-B contract must not create numerical wins",
    )
    checks.check(
        external_checks.get("ra2021_source_policy_audit_schema")
        == ra2021_source_policy_audit.get("schema")
        == "ra2021-source-policy-row-audit-v1",
        "RA2021 source-policy audit not carried into review",
    )
    checks.check(
        external_checks.get("ra2021_source_policy_audit_status")
        == "public_rows_complete_source_policy_rows_not_closed",
        "RA2021 source-policy audit status changed",
    )
    checks.check(
        external_checks.get("ra2021_per_row_source_identity_requirements_resolved")
        == ra2021_source_policy_audit.get("per_row_source_identity_requirements_resolved")
        == 3,
        "RA2021 resolved per-row requirement count changed",
    )
    checks.check(
        external_checks.get("ra2021_per_row_source_policy_promotion_requirements_remaining")
        == ra2021_source_policy_audit.get("per_row_source_policy_promotion_requirements_remaining")
        == 4,
        "RA2021 remaining per-row requirement count changed",
    )
    checks.check(
        external_checks.get("ra2021_row_missing_evidence_shrunk_by_identity_audit") is True,
        "RA2021 row missing-evidence shrink marker missing",
    )
    ra2021_gap = ra2021_source_policy_audit.get("promotion_gap_drilldown", {})
    checks.check(
        external_checks.get("ra2021_promotion_gap_drilldown_checked") == ra2021_gap.get("checked") is True,
        "RA2021 promotion-gap drilldown not carried into review",
    )
    checks.check(
        external_checks.get("ra2021_promotion_gap_examples_checked") == ra2021_gap.get("examples_checked") == 4,
        "RA2021 promotion-gap example count changed",
    )
    checks.check(
        external_checks.get("ra2021_promotion_gap_active_rows_checked")
        == ra2021_gap.get("active_rows_checked")
        == 0,
        "RA2021 promotion-gap active row count changed",
    )
    checks.check(
        external_checks.get("ra2021_promotion_gap_source_identity_closed") is True,
        "RA2021 promotion-gap source identity should be closed",
    )
    checks.check(
        external_checks.get("ra2021_promotion_gap_source_policy_promotion_closed") is False,
        "RA2021 promotion-gap unexpectedly closes source-policy promotion",
    )
    checks.check(
        external_checks.get("ra2021_promotion_gap_single_status")
        == "not_promoted_floor_limited_public_h_tranche",
        "RA2021 single promotion-gap status changed",
    )
    checks.check(
        external_checks.get("ra2021_promotion_gap_double_status")
        == "not_promoted_coarse_h_and_reference_policy_mismatch",
        "RA2021 double promotion-gap status changed",
    )
    checks.check(
        external_checks.get("ra2021_promotion_gap_closed_loop_status")
        == "not_promoted_true_dynamic_not_source_policy_and_public_horizon_not_dynamic_order",
        "RA2021 closed-loop promotion-gap status changed",
    )
    checks.check(
        external_checks.get("ra2021_source_identity_schema")
        == ra2021_source_identity_audit.get("schema")
        == "ra2021-source-identity-audit-v1",
        "RA2021 source-identity audit not carried into review",
    )
    checks.check(
        external_checks.get("ra2021_source_identity_status")
        == "source_output_time_grid_policy_extracted_promotion_still_open",
        "RA2021 source-identity audit status changed",
    )
    checks.check(
        external_checks.get("ra2021_source_identity_output_mapping_verified") is True,
        "RA2021 source output mapping should be verified",
    )
    checks.check(
        external_checks.get("ra2021_source_identity_time_grid_extracted") is True,
        "RA2021 time-grid policy should be extracted",
    )
    checks.check(
        external_checks.get("ra2021_source_identity_source_policy_rows_closed") == 0,
        "RA2021 source-identity audit should not close source-policy rows",
    )
    checks.check(
        external_checks.get("ra2021_source_identity_external_superiority_allowed") is False,
        "RA2021 source-identity audit overclaims external superiority",
    )
    checks.check(
        external_checks.get("ra2021_source_identity_position_mismatch_rows") == 9,
        "RA2021 source-identity mismatch count changed",
    )
    checks.check(
        external_checks.get("ra2021_source_identity_velocity_floor_rows") == 1,
        "RA2021 source-identity floor count changed",
    )
    checks.check(external_checks.get("ra2021_active_b2_flagged_rows") == 0, "RA2021 active rows changed")
    checks.check(
        external_checks.get("ra2021_public_order_groups_completed")
        == external_checks.get("ra2021_public_order_groups_required")
        == 12,
        "RA2021 public order groups changed",
    )
    checks.check(
        external_checks.get("ra2021_public_timing_rows_completed")
        == external_checks.get("ra2021_public_timing_rows_required")
        == 12,
        "RA2021 public timing rows changed",
    )
    checks.check(
        external_checks.get("ra2021_fixed_grid_common_reference_rows") == 12,
        "RA2021 fixed-grid row count changed",
    )
    checks.check(
        external_checks.get("ra2021_paper_safe_common_reference_rows") == 12,
        "RA2021 paper-safe row count changed",
    )
    checks.check(
        external_checks.get("ra2021_source_policy_reproduction_rows") == 0,
        "RA2021 source-policy reproduction rows changed",
    )
    checks.check(
        external_checks.get("ra2021_position_aligned_velocity_mismatch_rows") == 9,
        "RA2021 velocity mismatch count changed",
    )
    checks.check(
        external_checks.get("ra2021_velocity_nonmonotone_or_floor_limited_rows") == 1,
        "RA2021 nonmonotone/floor count changed",
    )
    checks.check(
        external_checks.get("ra2021_can_close_b2_requirement_now") is False,
        "RA2021 B2 requirement unexpectedly closed",
    )
    checks.check(external_checks.get("ra2021_default_1e_4_required") is False, "RA2021 audit requires default 1e-4")
    checks.check(external_checks.get("ra2021_heavy_run_invoked") is False, "RA2021 audit invoked heavy run")
    checks.check(external_checks.get("ra2021_run_v047_invoked") is False, "RA2021 audit invoked run_v047")
    checks.check(
        external_checks.get("tfe_source_policy_spec_schema")
        == tfe_source_policy_spec.get("schema")
        == "tfe-source-policy-spec-v1",
        "TFE source-policy spec not carried into review",
    )
    checks.check(
        external_checks.get("tfe_source_policy_spec_status")
        == "source_policy_extracted_candidate_scaffold_present_source_policy_open",
        "TFE source-policy spec status changed",
    )
    checks.check(external_checks.get("tfe_source_policy_reference_h") == 1.0e-4, "TFE reference h changed")
    checks.check(external_checks.get("tfe_source_policy_rows_completed") == 0, "TFE completed rows changed")
    checks.check(
        external_checks.get("tfe_source_policy_runner_implemented") is False,
        "TFE runner unexpectedly implemented",
    )
    checks.check(
        external_checks.get("tfe_source_policy_external_superiority_allowed") is False,
        "TFE source-policy overclaims external superiority",
    )
    checks.check(
        external_checks.get("tfe_public_code_recheck_status")
        == tfe_public_code_recheck.get("status")
        == "public_code_rechecked_no_distinct_tfe_code_artifact_attempted_not_reproducible",
        "TFE public-code recheck status not carried into review",
    )
    checks.check(
        external_checks.get("tfe_public_code_recheck_date")
        == tfe_public_code_recheck.get("date_checked")
        == "2026-06-13",
        "TFE public-code recheck date changed",
    )
    checks.check(
        external_checks.get("tfe_public_code_recheck_github_repository_search_total_count")
        == tfe_public_code_recheck.get("coverage", {}).get("github_repository_search_total_count")
        == 0,
        "TFE public-code recheck repository count changed",
    )
    checks.check(
        external_checks.get("tfe_public_code_recheck_github_user_search_total_count")
        == tfe_public_code_recheck.get("coverage", {}).get("github_user_search_total_count")
        == 0,
        "TFE public-code recheck user count changed",
    )
    checks.check(
        external_checks.get("tfe_public_code_recheck_github_code_search_api_status")
        == tfe_public_code_recheck.get("coverage", {}).get("github_code_search_api_status")
        == "requires_authentication",
        "TFE public-code recheck code-search status changed",
    )
    checks.check(
        external_checks.get("tfe_public_code_recheck_attempted_not_reproducible_rows")
        == tfe_public_code_recheck.get("coverage", {}).get("source_policy_rows_attempted_not_reproducible")
        == 16,
        "TFE public-code recheck attempted rows changed",
    )
    checks.check(
        external_checks.get("tfe_public_code_recheck_source_policy_rows_closed")
        == tfe_public_code_recheck.get("coverage", {}).get("source_policy_rows_closed")
        == 0,
        "TFE public-code recheck overclosed rows",
    )
    checks.check(
        external_checks.get("tfe_public_code_recheck_external_superiority_allowed")
        == tfe_public_code_recheck.get("claim_boundary", {}).get("external_superiority_claim_allowed")
        is False,
        "TFE public-code recheck external superiority changed",
    )
    tfe_boundary = tfe_source_policy_spec.get("candidate_vs_source_policy_boundary", {})
    tfe_boundary_sources = [
        "TFE_SOURCE_POLICY_SPEC.json",
        "TFE_SOURCE_POLICY_ROW_AUDIT.json",
        "TFE_DAE_RUNNER_CONTRACT_GAP_AUDIT.json",
        "TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.json",
    ]
    checks.check(
        external_checks.get("tfe_candidate_source_policy_boundary")
        == tfe_boundary
        == tfe_source_policy_audit.get("candidate_vs_source_policy_boundary", {})
        == tfe_dae_runner_contract_gap_audit.get("candidate_vs_source_policy_boundary", {}),
        "TFE candidate/source-policy boundary not carried consistently into review",
    )
    checks.check(
        external_checks.get("tfe_candidate_source_policy_boundary")
        == tfe_self_reproduction_attempt_certificate.get("candidate_vs_source_policy_boundary", {}),
        "TFE self-reproduction certificate boundary diverges from review",
    )
    checks.check(
        external_checks.get("tfe_candidate_source_policy_boundary_sources") == tfe_boundary_sources,
        "TFE candidate/source-policy boundary source list changed",
    )
    checks.check(
        external_checks.get("tfe_candidate_source_policy_boundary_sources_match") is True,
        "TFE candidate/source-policy boundary sources no longer match",
    )
    checks.check(
        external_checks.get("tfe_source_policy_self_reproduction_attempt_certificate_status")
        == tfe_self_reproduction_attempt_certificate.get("status")
        == "attempted_not_reproducible_not_promoted",
        "TFE self-reproduction attempt certificate status missing from review",
    )
    checks.check(
        external_checks.get("tfe_source_policy_self_reproduction_attempt_rows") == 16
        and external_checks.get("tfe_source_policy_self_reproduction_attempt_not_reproducible_rows") == 16
        and external_checks.get("tfe_source_policy_self_reproduction_attempt_closed_rows") == 0,
        "TFE self-reproduction attempt row counts changed in review",
    )
    tfe_self_reproduction_preflight = tfe_self_reproduction_attempt_certificate.get(
        "source_policy_execution_preflight", {}
    )
    expected_tfe_self_reproduction_runner_contracts = [
        "monolithic_absolute_coordinate_DAE_time_integrator",
        "TFE_m1_m2_m3_Newmark_beta_trapezoidal_source_policy_method_runners",
        "Gauss6_FullVA_absolute_coordinate_source_policy_DAE_runner",
        "accepted_T10_source_policy_work_precision_rows",
    ]
    checks.check(
        external_checks.get("tfe_source_policy_self_reproduction_preflight_status")
        == tfe_self_reproduction_preflight.get("status")
        == "terminal_no_public_code_self_reproduction_attempted_not_promoted",
        "TFE self-reproduction preflight status missing from review",
    )
    checks.check(
        external_checks.get("tfe_source_policy_self_reproduction_preflight_current_route")
        == tfe_self_reproduction_preflight.get("current_route")
        == "no_public_code_self_reproduction_attempted_unable_to_reproduce_not_promoted"
        and external_checks.get("tfe_source_policy_self_reproduction_preflight_reopen_condition")
        == tfe_self_reproduction_preflight.get("reopen_condition")
        == "new_public_or_source_code_equivalent_tfe_implementation_artifact",
        "TFE self-reproduction preflight route/reopen condition changed in review",
    )
    checks.check(
        external_checks.get("tfe_source_policy_self_reproduction_preflight_execution_block_count")
        == tfe_self_reproduction_preflight.get("execution_block_count")
        == 4
        and external_checks.get("tfe_source_policy_self_reproduction_preflight_ready_now")
        == tfe_self_reproduction_preflight.get("ready_to_execute_source_policy_now")
        is False
        and external_checks.get("tfe_source_policy_self_reproduction_preflight_can_promote_rows_now")
        == tfe_self_reproduction_preflight.get("can_promote_any_tfe_source_policy_row_now")
        is False,
        "TFE self-reproduction preflight overclaims execution or promotion readiness",
    )
    checks.check(
        external_checks.get("tfe_source_policy_self_reproduction_preflight_source_policy_rows_completed")
        == tfe_self_reproduction_preflight.get("source_policy_rows_completed")
        == 0
        and external_checks.get("tfe_source_policy_self_reproduction_required_next_action_count")
        == len(tfe_self_reproduction_attempt_certificate.get("required_next_actions", []))
        == 3,
        "TFE self-reproduction preflight source-row or next-action counts changed in review",
    )
    checks.check(
        external_checks.get("tfe_source_policy_self_reproduction_preflight_runner_contracts_required")
        == tfe_self_reproduction_preflight.get("runner_contracts_required_before_execution")
        == expected_tfe_self_reproduction_runner_contracts,
        "TFE self-reproduction preflight runner-contract requirements changed in review",
    )
    checks.check(
        external_checks.get("tfe_candidate_source_policy_allowed_use")
        == "diagnostic_scaffold_only_not_source_policy_reproduction",
        "TFE candidate scaffold allowed-use boundary changed",
    )
    checks.check(
        external_checks.get("tfe_candidate_source_policy_scaffold_present") is True,
        "TFE candidate scaffold presence boundary changed",
    )
    checks.check(
        external_checks.get("tfe_candidate_source_policy_dae_runner_equivalent") is False,
        "TFE candidate scaffold overclaims DAE runner equivalence",
    )
    checks.check(
        external_checks.get("tfe_candidate_source_policy_method_runner_equivalent") is False,
        "TFE candidate scaffold overclaims method runner equivalence",
    )
    checks.check(
        external_checks.get("tfe_candidate_source_policy_rows_completed") == 0,
        "TFE candidate scaffold overcloses source-policy rows",
    )
    checks.check(
        external_checks.get("tfe_candidate_source_policy_external_superiority_allowed") is False,
        "TFE candidate scaffold overclaims external superiority",
    )
    checks.check(
        external_checks.get("tfe_candidate_source_policy_runner_required_for_promotion") is True
        and external_checks.get("tfe_candidate_source_policy_obligation_count") == 5,
        "TFE candidate/source-policy promotion obligations changed",
    )
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
    checks.check(
        external_checks.get("tfe_dae_runner_contract_gap_status")
        == tfe_dae_runner_contract_gap_audit.get("status")
        == "dae_runner_contract_gap_open_not_source_policy"
        and external_checks.get("tfe_dae_runner_contract_gap_missing_block_count") == 6
        and external_checks.get("tfe_dae_runner_contract_gap_nonheavy_blocks")
        == expected_tfe_dae_nonheavy_gap_ids
        and external_checks.get("tfe_dae_runner_contract_gap_terminal_nonpromoted_blocks")
        == expected_tfe_dae_nonheavy_gap_ids
        and external_checks.get("tfe_dae_runner_contract_gap_terminal_nonpromoted_block_count")
        == 2
        and external_checks.get("tfe_dae_runner_contract_gap_effective_missing_blocks")
        == expected_tfe_dae_execution_gap_ids
        and external_checks.get("tfe_dae_runner_contract_gap_effective_missing_block_count")
        == 4
        and external_checks.get("tfe_dae_runner_contract_gap_execution_blocks")
        == expected_tfe_dae_execution_gap_ids,
        "TFE DAE runner contract gap accounting changed in review",
    )
    checks.check(
        external_checks.get("tfe_dae_runner_contract_gap_block_accounting", {}).get(
            "raw_open_contract_block_count"
        )
        == 6
        and external_checks.get("tfe_dae_runner_contract_gap_block_accounting", {}).get(
            "terminal_nonpromoted_contract_block_count"
        )
        == 2
        and external_checks.get("tfe_dae_runner_contract_gap_block_accounting", {}).get(
            "effective_source_policy_execution_contract_block_count"
        )
        == 4
        and external_checks.get("tfe_dae_runner_contract_gap_block_accounting", {}).get(
            "source_policy_rows_closed_by_accounting"
        )
        == 0,
        "TFE DAE runner contract block-accounting summary changed in review",
    )
    tfe_execution_preflight = tfe_dae_runner_contract_gap_audit.get("source_policy_execution_preflight", {})
    checks.check(
        external_checks.get("tfe_source_policy_execution_preflight") == tfe_execution_preflight,
        "TFE source-policy execution preflight not carried into review",
    )
    checks.check(
        external_checks.get("tfe_source_policy_execution_preflight_status")
        == tfe_execution_preflight.get("status")
        == "terminal_no_public_code_self_reproduction_attempted_not_promoted",
        "TFE source-policy execution preflight status changed in review",
    )
    checks.check(
        external_checks.get("tfe_source_policy_execution_preflight_opt_in_required")
        == tfe_execution_preflight.get("explicit_user_opt_in_required")
        is False,
        "TFE source-policy execution preflight opt-in boundary changed in review",
    )
    checks.check(
        external_checks.get("tfe_source_policy_execution_preflight_nonheavy_dispositioned")
        == tfe_execution_preflight.get("nonheavy_blocks_dispositioned_by_demotion")
        is True
        and external_checks.get("tfe_source_policy_execution_preflight_execution_block_count")
        == tfe_execution_preflight.get("execution_block_count")
        == 4,
        "TFE source-policy execution preflight block boundary changed in review",
    )
    checks.check(
        external_checks.get("tfe_source_policy_execution_preflight_can_promote_rows_now")
        == tfe_execution_preflight.get("can_promote_any_tfe_source_policy_row_now")
        is False
        and external_checks.get("tfe_source_policy_execution_preflight_ready_now")
        == tfe_execution_preflight.get("ready_to_execute_source_policy_now")
        is False,
        "TFE source-policy execution preflight overclaims promotion/readiness in review",
    )
    checks.check(
        external_checks.get("tfe_source_policy_execution_preflight_decision")
        == "no_public_code_self_reproduction_attempted_unable_to_reproduce_not_promoted",
        "TFE source-policy execution preflight reviewer decision changed",
    )
    checks.check(
        external_checks.get("tfe_runner_contract_preflight_status")
        == tfe_runner_contract_preflight.get("status")
        == "contract_entrypoints_callable_candidate_backed_source_policy_open"
        and external_checks.get("tfe_runner_contract_preflight_entrypoints") == "3/3"
        and external_checks.get("tfe_runner_contract_preflight_candidate_backed") == "3/3"
        and external_checks.get("tfe_runner_contract_preflight_source_policy_rows_completed")
        == tfe_runner_contract_preflight.get("source_policy_rows_completed")
        == 0
        and external_checks.get("tfe_runner_contract_preflight_execution_blocks")
        == tfe_runner_contract_preflight.get("source_policy_execution_block_count")
        == 4
        and external_checks.get("tfe_runner_contract_preflight_safe_use")
        == tfe_runner_contract_preflight.get("safe_current_use")
        == "runner_contract_preflight_only_not_source_policy_reproduction",
        "TFE runner contract preflight boundary not carried into review",
    )
    checks.check(
        external_checks.get("oc12_archive_tfe_runner_contract_preflight_status")
        == objective_summary.get("full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_status")
        == "contract_entrypoints_callable_candidate_backed_source_policy_open"
        and external_checks.get("oc12_archive_tfe_runner_contract_preflight_entrypoints")
        == objective_summary.get("full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_entrypoints")
        == "3/3"
        and external_checks.get("oc12_archive_tfe_runner_contract_preflight_candidate_backed")
        == objective_summary.get("full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_candidate_backed")
        == "3/3"
        and external_checks.get("oc12_archive_tfe_runner_contract_preflight_source_policy_rows_completed")
        == objective_summary.get(
            "full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_source_policy_rows_completed"
        )
        == 0
        and external_checks.get("oc12_archive_tfe_runner_contract_preflight_execution_blocks")
        == objective_summary.get("full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_execution_blocks")
        == 4
        and external_checks.get("oc12_archive_tfe_runner_contract_preflight_safe_use")
        == objective_summary.get("full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_safe_use")
        == "runner_contract_preflight_only_not_source_policy_reproduction",
        "OC12 archive TFE runner contract preflight boundary not carried into review",
    )
    checks.check(
        external_checks.get("oc12_archive_action_boundary")
        == objective_summary.get("full_source_policy_runner_archive_gap_action_boundary")
        == expected_archive_action_boundary
        and external_checks.get("oc12_archive_safe_without_b4_opt_in_count")
        == objective_summary.get("full_source_policy_runner_archive_gap_safe_without_b4_opt_in_count")
        == 4
        and external_checks.get("oc12_archive_opt_in_required_action_count")
        == objective_summary.get("full_source_policy_runner_archive_gap_opt_in_required_action_count")
        == 1
        and external_checks.get("oc12_archive_source_policy_execution_allowed_now")
        == objective_summary.get("full_source_policy_runner_archive_gap_source_policy_execution_allowed_now")
        is False
        and external_checks.get("oc12_archive_source_policy_execution_invoked")
        == objective_summary.get("full_source_policy_runner_archive_gap_source_policy_execution_invoked")
        is False
        and external_checks.get("oc12_archive_exact_b4_opt_in_required_for_execution")
        == objective_summary.get("full_source_policy_runner_archive_gap_exact_b4_opt_in_required_for_execution")
        is True
        and external_checks.get("oc12_archive_opt_in_required_command_count")
        == objective_summary.get("full_source_policy_runner_archive_gap_opt_in_required_command_count")
        == 13
        and external_checks.get("oc12_archive_opt_in_required_mapped_external_rows")
        == objective_summary.get("full_source_policy_runner_archive_gap_opt_in_required_mapped_external_rows")
        == 20
        and external_checks.get("oc12_archive_safe_action_ids")
        == objective_summary.get("full_source_policy_runner_archive_gap_safe_action_ids")
        == expected_archive_safe_action_ids
        and external_checks.get("oc12_archive_opt_in_action_ids")
        == objective_summary.get("full_source_policy_runner_archive_gap_opt_in_action_ids")
        == expected_archive_opt_in_action_ids,
        "OC12 archive action boundary not carried into review",
    )
    checks.check(
        external_checks.get("oc6_reopen_latest_external_probe")
        == oc6_reopen_latest_external_probe
        == "2026-06-21/9/0/0/4/False/False"
        and external_checks.get("oc6_reopen_latest_external_probe_date")
        == full_source_policy_runner_archive_gap.get(
            "oc6_source_equivalent_reopen_readiness_latest_external_probe_date"
        )
        == "2026-06-21"
        and external_checks.get("oc6_reopen_latest_external_probe_count")
        == full_source_policy_runner_archive_gap.get(
            "oc6_source_equivalent_reopen_readiness_latest_external_probe_count"
        )
        == 9
        and external_checks.get("oc6_reopen_latest_external_probe_positive_artifact_rows")
        == full_source_policy_runner_archive_gap.get(
            "oc6_source_equivalent_reopen_readiness_latest_external_probe_positive_artifact_rows"
        )
        == 0,
        "OC6 reopen latest-probe counts not carried into review",
    )
    checks.check(
        external_checks.get("oc6_reopen_latest_external_probe_source_policy_rows_closed")
        == full_source_policy_runner_archive_gap.get(
            "oc6_source_equivalent_reopen_readiness_latest_external_probe_source_policy_rows_closed"
        )
        == 0
        and external_checks.get("oc6_reopen_latest_external_probe_access_limited_count")
        == full_source_policy_runner_archive_gap.get(
            "oc6_source_equivalent_reopen_readiness_latest_external_probe_access_limited_count"
        )
        == 4
        and external_checks.get("oc6_reopen_latest_external_probe_global_absence_proved")
        == full_source_policy_runner_archive_gap.get(
            "oc6_source_equivalent_reopen_readiness_latest_external_probe_global_absence_proved"
        )
        is False
        and external_checks.get("oc6_reopen_latest_external_probe_reopen_triggered")
        == full_source_policy_runner_archive_gap.get(
            "oc6_source_equivalent_reopen_readiness_latest_external_probe_reopen_triggered"
        )
        is False,
        "OC6 reopen latest-probe closure boundary not carried into review",
    )
    checks.check(
        external_checks.get("tfe_source_policy_audit_schema")
        == tfe_source_policy_audit.get("schema")
        == "tfe-source-policy-row-audit-v1",
        "TFE source-policy row audit not carried into review",
    )
    checks.check(
        external_checks.get("tfe_source_policy_audit_status")
        == "source_policy_spec_extracted_runner_rows_not_closed",
        "TFE source-policy row audit status changed",
    )
    checks.check(external_checks.get("tfe_active_b2_flagged_rows") == 0, "TFE active B2 row count changed")
    checks.check(external_checks.get("tfe_source_policy_closed_rows") == 0, "TFE source-policy rows unexpectedly closed")
    checks.check(
        external_checks.get("tfe_external_superiority_ready_rows") == 0,
        "TFE external-superiority rows unexpectedly ready",
    )
    checks.check(external_checks.get("tfe_source_policy_spec_extracted") is True, "TFE spec extraction marker changed")
    checks.check(
        external_checks.get("tfe_pendulum_runner_implemented") is False,
        "TFE pendulum runner unexpectedly implemented",
    )
    checks.check(
        external_checks.get("tfe_source_grid_compatibility_status") == "source_horizon_step_grid_policy_open",
        "TFE source grid compatibility status changed",
    )
    checks.check(
        external_checks.get("tfe_source_grid_integer_step_compatible_rows") == 2,
        "TFE source grid compatible row count changed",
    )
    checks.check(
        external_checks.get("tfe_source_grid_integer_step_incompatible_rows") == 4,
        "TFE source grid incompatible row count changed",
    )
    checks.check(
        external_checks.get("tfe_source_grid_exact_T_compatible_rows_endpoint_convention_resolved") == 2,
        "TFE source grid exact-T endpoint-resolved count changed",
    )
    checks.check(
        external_checks.get("tfe_source_grid_endpoint_incompatible_rows_requiring_policy") == 4,
        "TFE source grid endpoint-policy-required count changed",
    )
    checks.check(
        external_checks.get("tfe_source_grid_policy_resolved_for_exact_T_compatible_rows") is True,
        "TFE source grid exact-T subset was not carried as resolved",
    )
    checks.check(
        external_checks.get("tfe_source_grid_endpoint_compatible_row_ids")
        == ["frictional_pendulum:h=0.008", "frictional_pendulum:h=0.2"],
        "TFE source grid exact-T row IDs changed",
    )
    checks.check(
        external_checks.get("tfe_source_grid_endpoint_incompatible_row_ids")
        == [
            "frictionless_pendulum:h=0.003",
            "frictionless_pendulum:h=0.006",
            "frictionless_pendulum:h=0.012",
            "frictional_pendulum:h=0.003",
        ],
        "TFE source grid endpoint-incompatible row IDs changed",
    )
    checks.check(
        external_checks.get("tfe_source_grid_policy_resolved_for_full_T10") is False,
        "TFE source grid policy unexpectedly resolved",
    )
    checks.check(
        external_checks.get("tfe_source_grid_endpoint_convention_candidate_count") == 4,
        "TFE endpoint convention candidate count changed",
    )
    checks.check(
        external_checks.get("tfe_source_grid_endpoint_convention_policies")
        == [
            "nearest_integer_horizon",
            "algorithm_literal_fixed_h_until_tn_ge_tfinal",
            "adjust_h_to_hit_T_exactly",
            "integer_steps_plus_final_partial_step",
        ],
        "TFE endpoint convention policies changed",
    )
    required_to_accept = external_checks.get("tfe_source_grid_required_to_accept_full_T10_rows")
    checks.check(isinstance(required_to_accept, list) and len(required_to_accept) == 6, "TFE required-to-accept list changed")
    checks.check(
        any("endpoint convention" in item for item in required_to_accept or []),
        "TFE required-to-accept list missing endpoint convention item",
    )
    checks.check(
        any("demoted from the source-policy row set" in item for item in required_to_accept or []),
        "TFE required-to-accept list missing endpoint demotion item",
    )
    checks.check(
        external_checks.get("tfe_source_grid_source_text_available") is True,
        "TFE source text availability not carried into review",
    )
    checks.check(
        external_checks.get("tfe_source_grid_source_text_anchor_count", 0) >= 8,
        "TFE source text anchor count not carried into review",
    )
    checks.check(
        external_checks.get("tfe_source_grid_algorithm_literal_fixed_h") is True,
        "TFE algorithm-literal fixed-h evidence not carried into review",
    )
    checks.check(
        external_checks.get("tfe_source_grid_endpoint_convention_resolved_for_error_sampling") is False,
        "TFE endpoint error-sampling convention unexpectedly resolved in review",
    )
    checks.check(
        external_checks.get("tfe_endpoint_sensitivity_schema")
        == tfe_endpoint_sensitivity.get("schema")
        == "tfe-endpoint-policy-sensitivity-audit-v1",
        "TFE endpoint sensitivity audit not carried into review",
    )
    checks.check(
        external_checks.get("tfe_endpoint_sensitivity_status")
        == "diagnostic_endpoint_policy_sensitivity_not_source_policy",
        "TFE endpoint sensitivity status changed",
    )
    checks.check(
        external_checks.get("tfe_endpoint_sensitivity_method_count")
        == tfe_endpoint_sensitivity.get("method_count")
        == 4,
        "TFE endpoint sensitivity method count changed",
    )
    checks.check(
        external_checks.get("tfe_endpoint_sensitivity_policy_count")
        == tfe_endpoint_sensitivity.get("policy_count")
        == 4,
        "TFE endpoint sensitivity policy count changed",
    )
    checks.check(
        external_checks.get("tfe_endpoint_sensitivity_summary_row_count")
        == tfe_endpoint_sensitivity.get("summary_row_count")
        == 16,
        "TFE endpoint sensitivity summary row count changed",
    )
    checks.check(
        external_checks.get("tfe_endpoint_sensitivity_raw_row_count")
        == tfe_endpoint_sensitivity.get("raw_row_count")
        == 48,
        "TFE endpoint sensitivity raw row count changed",
    )
    checks.check(
        external_checks.get("tfe_endpoint_sensitivity_source_policy_rows_completed")
        == tfe_endpoint_sensitivity.get("source_policy_rows_completed")
        == 0,
        "TFE endpoint sensitivity unexpectedly completed source-policy rows",
    )
    checks.check(
        external_checks.get("tfe_endpoint_sensitivity_external_superiority_claim_allowed")
        == tfe_endpoint_sensitivity.get("external_superiority_claim_allowed")
        is False,
        "TFE endpoint sensitivity overclaims external superiority",
    )
    checks.check(
        external_checks.get("tfe_endpoint_sensitivity_source_policy_runner_equivalent")
        == tfe_endpoint_sensitivity.get("source_policy_runner_equivalent")
        is False,
        "TFE endpoint sensitivity overclaims runner equivalence",
    )
    checks.check(
        external_checks.get("tfe_endpoint_sensitivity_default_1e_4_campaign_invoked") is False
        and external_checks.get("tfe_endpoint_sensitivity_run_v047_invoked") is False,
        "TFE endpoint sensitivity invoked a forbidden heavy/default run",
    )
    checks.check(
        external_checks.get("tfe_endpoint_sensitivity_nominal_h") == [0.012, 0.006, 0.003],
        "TFE endpoint sensitivity nominal h values changed",
    )
    checks.check(
        external_checks.get("tfe_endpoint_sensitivity_endpoint_policies")
        == [
            "adjust_h_to_hit_T_exactly",
            "algorithm_literal_fixed_h_until_tn_ge_tfinal",
            "floor_horizon",
            "integer_steps_plus_final_partial_step",
        ],
        "TFE endpoint sensitivity policies changed",
    )
    checks.check(
        external_checks.get("tfe_full_t10_coarse_summary_schema")
        == tfe_full_t10_coarse_candidate_summary.get("schema")
        == "tfe-full-t10-coarse-candidate-summary-v1",
        "TFE full-T10 coarse summary not carried into review",
    )
    checks.check(
        external_checks.get("tfe_full_t10_coarse_summary_status")
        == "full_T10_coarse_candidate_probe_summarized_not_source_policy",
        "TFE full-T10 coarse summary status changed",
    )
    checks.check(
        external_checks.get("tfe_full_t10_coarse_summary_row_count") == 4,
        "TFE full-T10 coarse summary row count changed",
    )
    checks.check(
        external_checks.get("tfe_full_t10_coarse_summary_finite_rows") == 4,
        "TFE full-T10 finite row count changed",
    )
    checks.check(
        external_checks.get("tfe_full_t10_coarse_summary_residual_ok_rows") == 4,
        "TFE full-T10 residual-ok row count changed",
    )
    checks.check(
        external_checks.get("tfe_full_t10_coarse_summary_source_policy_rows") == 0,
        "TFE full-T10 summary overclosed source-policy rows",
    )
    checks.check(
        external_checks.get("tfe_full_t10_coarse_summary_reference_h") == 0.0125,
        "TFE full-T10 coarse reference h changed",
    )
    checks.check(
        external_checks.get("tfe_full_t10_coarse_summary_source_policy_reference_invoked") is False,
        "TFE full-T10 summary invoked source-policy reference",
    )
    checks.check(
        external_checks.get("tfe_full_t10_coarse_summary_default_1e_4_campaign_invoked") is False,
        "TFE full-T10 summary invoked default 1e-4 campaign",
    )
    checks.check(
        external_checks.get("tfe_full_t10_coarse_summary_external_superiority_allowed") is False,
        "TFE full-T10 summary overclaims external superiority",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_model_schema")
        == tfe_source_pendulum_model_audit.get("schema")
        == "tfe-source-pendulum-model-audit-v1",
        "TFE source pendulum model audit not carried into review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_model_status")
        == "source_parameter_model_implemented_runner_policy_open",
        "TFE source pendulum model audit status changed",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_parameter_match") is True,
        "TFE source pendulum parameters no longer match the source spec",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_parameter_model_implemented") is True,
        "TFE source pendulum parameter model not visible in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_frictionless_smoke_implemented") is True,
        "TFE source pendulum frictionless smoke layer not visible in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_absolute_coordinate_dae_residual_smoke_implemented")
        is True,
        "TFE absolute-coordinate residual smoke not visible in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_absolute_coordinate_frictional_candidate_dae_smoke_implemented")
        is True,
        "TFE absolute-coordinate frictional candidate smoke not visible in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_source_policy_dae_runner_equivalent") is False,
        "TFE source-policy DAE runner equivalence overclaimed in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_source_output_time_integration_smoke_implemented")
        is True,
        "TFE source-output time-integration smoke not visible in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_source_policy_time_integration_runner_equivalent")
        is False,
        "TFE source-policy time-integration equivalence overclaimed in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_source_reference_solution_policy_smoke_implemented")
        is True,
        "TFE source reference-policy smoke not visible in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_source_reference_solution_policy_smoke_full_T10")
        is False,
        "TFE source reference-policy smoke overclaims full T=10 run in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_implemented")
        is True,
        "TFE full T=10 source-reference probe not visible in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_completed")
        is True,
        "TFE full T=10 source-reference probe completion not visible in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_rows_completed")
        == 0,
        "TFE full T=10 source-reference probe overcloses source-policy rows in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_steps")
        == 100000,
        "TFE full T=10 source-reference probe source-step count changed in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_check_steps")
        == 200000,
        "TFE full T=10 source-reference probe check-step count changed in review",
    )
    checks.check(
        float(
            external_checks.get(
                "tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_coordinate_error"
            )
        )
        < 1.0e-10,
        "TFE full T=10 source-reference coordinate check error too large in review",
    )
    checks.check(
        float(
            external_checks.get(
                "tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_velocity_error"
            )
        )
        < 1.0e-10,
        "TFE full T=10 source-reference velocity check error too large in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_source_comparator_candidate_runners_implemented")
        is True,
        "TFE source comparator candidate runners not visible in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_newmark_beta_candidate_runner_smoke_implemented")
        is True,
        "TFE Newmark-beta candidate runner smoke not visible in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_trapezoidal_candidate_runner_smoke_implemented")
        is True,
        "TFE trapezoidal candidate runner smoke not visible in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_source_policy_method_runner_equivalent")
        is False,
        "TFE source-policy method equivalence overclaimed in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_tfe_m1_m2_m3_candidate_runner_smoke_implemented")
        is True,
        "TFE m=1/2/3 candidate runner smoke not visible in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_appendix_b_coefficient_certificate_checked")
        is True,
        "TFE Appendix-B coefficient certificate not visible in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_appendix_b_coefficient_certificate_rows") == 3,
        "TFE Appendix-B coefficient certificate row count changed in review",
    )
    checks.check(
        float(external_checks.get("tfe_source_pendulum_appendix_b_coefficient_certificate_max_abs_diff")) <= 1.0e-14,
        "TFE Appendix-B coefficient certificate mismatch too large in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_tfe_m1_m2_m3_source_policy_runners_implemented")
        is False,
        "TFE m=1/2/3 source-policy runners unexpectedly implemented in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_gauss6_candidate_smoke_implemented") is True,
        "Gauss6 source-pendulum candidate smoke not visible in review",
    )
    checks.check(
        external_checks.get(
            "tfe_source_pendulum_gauss6_absolute_coordinate_source_policy_runner_implemented"
        )
        is False,
        "Gauss6 source-policy runner unexpectedly implemented in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_gauss6_candidate_rows") == 2,
        "Gauss6 source-pendulum candidate row count changed in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_gauss6_candidate_source_policy_rows_completed") == 0,
        "Gauss6 source-pendulum candidate overcloses source-policy rows in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_gauss6_candidate_method_equivalent") is False,
        "Gauss6 source-pendulum candidate overclaims method equivalence in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_active_b2_source_reference_full_T10_probe_implemented")
        is True
        and external_checks.get(
            "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_full_T10"
        )
        is True
        and external_checks.get(
            "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_reference_invoked"
        )
        is True
        and external_checks.get(
            "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_source_policy_rows"
        )
        == 0
        and external_checks.get(
            "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_method_equivalent"
        )
        is False,
        "active-B2 source-reference full-T10 probe boundary changed in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_bounded_source_policy_runner_smoke_implemented")
        is True,
        "bounded source-policy runner smoke not visible in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_bounded_source_policy_runner_rows") == 4,
        "bounded source-policy runner row count changed in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_bounded_source_policy_runner_full_T10") is False,
        "bounded source-policy runner overclaims full T=10 in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_bounded_source_policy_runner_source_policy_rows_completed") == 0,
        "bounded source-policy runner overcloses source-policy rows in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_active_b2_candidate_row_smoke_implemented") is True,
        "active B2 candidate row smoke not visible in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_active_b2_candidate_row_smoke_full_T10") is False,
        "active B2 candidate smoke overclaims full T=10 in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_active_b2_source_policy_rows_completed") == 0,
        "active B2 candidate smoke overcloses source-policy rows in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_active_b2_full_T10_coarse_probe_implemented") is True,
        "active B2 full T=10 coarse probe not visible in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_active_b2_full_T10_coarse_probe_full_T10") is True,
        "active B2 full T=10 coarse probe did not run full horizon in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_active_b2_full_T10_coarse_probe_source_policy_rows") == 0,
        "active B2 full T=10 coarse probe overcloses source-policy rows in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_active_b2_full_T10_coarse_probe_finite_rows") == 4,
        "active B2 full T=10 coarse probe finite row count changed in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_active_b2_full_T10_coarse_probe_residual_ok_rows") == 4,
        "active B2 full T=10 coarse probe residual row count changed in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_active_b2_full_T10_coarse_probe_reference_invoked") is False,
        "active B2 full T=10 coarse probe invoked source-policy reference in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_tfe_m3_full_T10_formula_probe_implemented") is True,
        "TFE m=3 full T=10 formula probe not visible in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_tfe_m3_full_T10_formula_probe_full_T10") is True,
        "TFE m=3 full T=10 formula probe did not run full horizon in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_tfe_m3_full_T10_formula_probe_expected_order") == 5,
        "TFE m=3 full T=10 formula probe expected order changed in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_tfe_m3_full_T10_formula_probe_source_policy_rows") == 0,
        "TFE m=3 full T=10 formula probe overcloses source-policy rows in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_tfe_m3_full_T10_formula_probe_finite_rows") == 1,
        "TFE m=3 full T=10 formula probe finite row count changed in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_tfe_m3_full_T10_formula_probe_residual_ok_rows") == 1,
        "TFE m=3 full T=10 formula probe residual row count changed in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_tfe_m3_full_T10_formula_probe_reference_invoked") is False,
        "TFE m=3 full T=10 formula probe invoked source-policy reference in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_active_b2_candidate_row_count") == 4,
        "active B2 candidate row count changed in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_model_dae_runner_implemented") is False,
        "TFE source pendulum DAE runner unexpectedly implemented",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_brown_mcphee_friction_law_implemented") is False,
        "TFE Brown-McPhee friction law unexpectedly implemented",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_brown_mcphee_candidate_friction_law_encoded") is True,
        "TFE candidate Brown-McPhee friction law not visible in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_brown_mcphee_source_text_anchor_found") is True,
        "TFE Brown-McPhee source-text anchor not visible in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_brown_mcphee_source_text_names_velocity_model") is True,
        "TFE Brown-McPhee source text no longer names velocity model",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_brown_mcphee_source_text_reports_mu_values") is True,
        "TFE Brown-McPhee source text no longer reports mu values",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_brown_mcphee_published_formula_structure_encoded") is True,
        "TFE Brown-McPhee published formula structure not visible in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_brown_mcphee_source_code_equivalent_law") is False,
        "TFE Brown-McPhee source-code equivalence overclaimed in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_brown_mcphee_transition_velocity_policy_resolved") is False,
        "TFE Brown-McPhee transition velocity unexpectedly resolved in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_frictional_candidate_smoke_implemented") is True,
        "TFE frictional candidate smoke not visible in review",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_candidate_friction_law_provenance")
        == "v022_revolute_brown_mcphee_surrogate_not_source_policy_equivalent",
        "TFE candidate friction provenance changed",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_error_output_policy_encoded") is True,
        "TFE source output policy not encoded",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_model_rows_completed") == 0,
        "TFE source pendulum model rows unexpectedly completed",
    )
    checks.check(
        external_checks.get("tfe_source_pendulum_setup_subrequirement_closed") is True,
        "TFE source pendulum setup subrequirement should be closed",
    )
    checks.check(
        external_checks.get("tfe_can_close_b2_requirement_now") is False,
        "TFE B2 requirement unexpectedly closed",
    )
    checks.check(external_checks.get("tfe_default_1e_4_required") is False, "TFE audit requires default 1e-4")
    checks.check(external_checks.get("tfe_heavy_run_invoked") is False, "TFE audit invoked heavy run")
    checks.check(external_checks.get("tfe_run_v047_invoked") is False, "TFE audit invoked run_v047")
    checks.check(result_pack.get("submission_ready") is False, "result pack should not mark submission ready")
    manuscript_style_token = (
        "Manuscript style figures/tables/theorems/proof tokens: "
        f"`{pdf_style_checks.get('manuscript_figure_count')}/"
        f"{pdf_style_checks.get('manuscript_table_count')}/"
        f"{pdf_style_checks.get('manuscript_theorem_count')}/"
        f"{pdf_style_checks.get('manuscript_proof_token_count')}`."
    )
    for token in [
        "Review scope: **global_submission_standard_review**.",
        "Top-level review decision scope: `global`.",
        "Decision: **do_not_submit_global**.",
        "Global review verdict: **do_not_submit_global**; scope `top_level_global_submission_standard`.",
        "Global submission standard met: `False`.",
        "Full source-policy package ready: `False`.",
        "Global open blockers: `OC4,OC6,OC12`.",
        "Objective blocker status by id: `{'OC4': 'open', 'OC6': 'partial', 'OC12': 'partial'}`.",
        "Objective blocker required-to-close by id:",
        "Objective blocker safe next actions by id:",
        "Objective blocker opt-in required actions by id:",
        "## Objective Blocker Matrix",
        "This review records the whole-paper CMAME submission decision. It does not close the global objective blockers.",
        f"`{EXPECTED_BLOCKER_OPEN_TOKEN}`",
        f"`{EXPECTED_BLOCKER_CLOSURE_DECISION_TOKEN}`",
        f"`{EXPECTED_BLOCKER_CLOSURE_ALLOWED_TOKEN}`",
        "Evidence summary: source-policy `0/40`, accepted source-policy dynamic-order `0/4`, full-source runner package `False`, dependency boundary `narrowed_repro_ready_full_source_policy_package_blocked`.",
        "CMAME narrowed blocker-gate open blockers: ``.",
        "Narrowed blocker-gate closed blockers: `B1,B2,B3,B4,B5,B6,B7,B8`; scope `narrowed_claim_blocker_gate_not_global_submission_standard`.",
        "Subsidiary Narrowed-Claim Subcheck (Not Global Review)",
        "Subcheck met: `True`.",
        "Disposition: **bounded_subcheck_satisfied_not_global_submit**.",
        "Legacy compatibility aliases: `narrowed_claim_submission_standard_met` and `narrowed_claim_decision` describe this subcheck only, not the global review verdict.",
        "Role: `subsidiary_bounded_subcheck_not_top_level_review_verdict`.",
        "Overrides global decision: `False`.",
        "Objective audit status: `not_complete_submission_standard_open`.",
        "Objective complete/submission ready: `False/False`.",
        "Requirements satisfied/partial/open: `9/2/1`; blocking open `3`.",
        "Objective B2 active suites/source-policy rows/demotion: `True/False/True`.",
        "Global Review Dimensions",
        "`method_contribution`",
        "`proof_and_theorem`",
        "`numerical_validation`",
        "`comparison_and_source_policy`",
        "`reproducibility_and_code_package`",
        "`manuscript_style_and_integrity`",
        "Core/source-policy/TFE/direct-PC2-proof/minimal-code closed: `True/False/False/True/False`.",
        "PDF-style review audit: `cmame-pdf-style-review-audit-v1` / `pdf_read_review_passed_narrowed_claim_subcheck_global_boundary_retained`.",
        "PDF-style texts read reference/main/flat: `True/True/True`.",
        "Reference style figures/tables/algorithms: `18/3/2`; work-precision mentions `4`.",
        "Reference style algorithm/numerical/work-precision/declarations: `True/True/True/True`.",
        manuscript_style_token,
        "PDF-style source-policy/direct-proof/B6/B7/minimal-code closed: `0/40` / `True` / `True` / `True` / `False`; eta_h solver-policy evidence, the residual-to-error theorem for mechanism rows, and full source-policy/package readiness remain separate global boundaries.",
        "PDF-style narrowed/global scope: `narrowed_claim_only/False/False`; ready scope `pdf_style_review_narrowed_claim_subcheck_passed_global_submission_boundary_retained`.",
        "PDF-style remaining gates eta_h/residual/source/no-ready: `True/7/0/40/True`.",
        "PDF-style blocking findings: ``.",
        "PDF-style bounded-subcheck standard/quality markers: `True/True`; not global submission or global quality-review clearance.",
        "All-method matrix coverage: `44` cells across `11` methods.",
        "Paper numerical result matrix: `paper-numerical-result-matrix-v1` with `44/44` cells from `132` raw rows.",
        "Paper numerical matrix source-policy/direct-error claims allowed: `False/False`; strict external rows `0`.",
        "Paper numerical matrix diagnostic favorable order/error cells: `40/40` and `40/40`; not an external-superiority claim.",
        "Result-to-manuscript traceability audit: `result-to-manuscript-traceability-audit-v1` / `all_44_velocity_cells_trace_to_manuscript_and_pdf_source_policy_open`.",
        "Result-to-manuscript velocity cells checked: `44/44`; main TeX/PDF `44/44`, flat TeX/PDF `44/44`.",
        "Result-to-manuscript source-policy/external-superiority boundary: `False` / `False`.",
        "All-method claim disposition audit: `all-method-example-claim-disposition-audit-v1` with `40/40` nonlocal cells and `44` total cells.",
        "All-method matrix visible methods/examples: `True/True`.",
        "Publication figure boundary visible in manuscript/PDF: `True`.",
        "Source-policy progress boundary visible in manuscript/PDF: `True`.",
        "All-method claim disposition diagnostic favorable order/error cells: `40/40` and `40/40`; source-policy rows remain nonpromoted.",
        "All-method source-policy closed/open/flagged rows: `0/40/15`; strict external rows `0`.",
        "All-method source-policy superiority allowed: `False`.",
        "Manuscript/PDF include source-policy diagnosis: `True/True`.",
        "Manuscript/PDF include all-example source-policy audit: `True/True`.",
        "Manuscript/PDF include active TFE B2 candidate smoke: `True/True`.",
        "Manuscript/PDF include TFE full-T10 coarse candidate summary: `True/True`.",
        "Manuscript/PDF include TFE Appendix-B coefficient certificate boundary: `True/True`.",
        "Manuscript/PDF include TFE m=3 full-T10 formula-probe boundary: `True/True`.",
        "Manuscript/PDF include comparison reconciliation: `True/True`.",
        "All-examples sanity audit: `44` cells; local rows `4/4`; flagged nonlocal rows `15`.",
        "All-examples source-policy recheck required: `True`.",
        "All-examples external superiority allowed: `False`.",
        "Proof-claim traceability audit: `proof-claim-traceability-audit-v1` / `conditional_proof_claims_traceable_submission_not_ready`.",
        "Proof remaining-work manifest: `proof-remaining-work-manifest-v1` / `proof_b1_b3_closed_submission_gates_remaining`.",
        "Proof remaining-work submission-ready scope: `proof_remaining_work_global_boundary_not_narrowed_claim_package_decision`; manifest scope `B1_B3_closed_remaining_global_submission_gates`.",
        "Proof remaining-work narrowed B4/B6/B7 statuses: `closed/closed/closed`; global boundaries `full_source_policy_package_ready,theorem_level_eta_h_solver_policy_evidence,closed_residual_to_error_theorem_for_mechanism_rows`.",
        "Proof remaining-work unsatisfied close requirements: `0` / `[]`.",
        "Proof remaining-work row split/links: `96/36` rows, `180` Newton-Euler links.",
        "Proof remaining-work Newton-Euler certificate present/complete: `True/False`.",
        "Proof remaining-work Newton-Euler runtime expression structure checked/rows: `True/36`.",
        "Proof remaining-work Newton-Euler runtime template instantiation checked/rows: `True/36`.",
        "Newton-Euler symbolic defect certificate artifact: `newton-euler-symbolic-defect-certificate-v1` / `balance_identities_closed_defect_not_proved`.",
        "Newton-Euler symbolic defect certificate rows certified/open/links: `0/36` / `180`; complete `False`.",
        "Newton-Euler runtime expression structure checked/rows: `True/36`; this is source-expression traceability, not proof closure.",
        "Newton-Euler runtime template instantiation checked/rows: `True/36`; this is row-template traceability, not algebraic proof closure.",
        "Newton-Euler template algebraic equivalence checked/rows/C2-subcheck: `True/36/True`; D1/D2 balance identities, direct-route D5 O(h^7) proof, and the B1 AD-expanded implementation-path certificate are closed, while primitive/global dynamic symbolic-oracle completion remains false.",
        "B1 independent residual symbolic row oracle: `True` with rows/source-template/runtime-binding `36/36/36`; row-certificate-only remaining item `AD_expanded_symbolic_oracle_closure`.",
        "B1 AD-expanded implementation-path certificate: `True` with rows/columns/cells `36/132/4752`; primitive/global dynamic oracle/O(h^7) symbolic certificate/submission ready `False/False/False`.",
        "Proof remaining-work execution flags default1e-4/heavy/run_v047: `False/False/False`.",
        "Proof-claim traceability labels present: `True/True`; boundary tokens `True/True`.",
        "Proof-claim theorem traceability: label `thm:g6fullva-order`; labels/boundary/mapped `True/True/True`; dependency/table/dynamic `True/True/True`.",
        "Proof-claim theorem no-promotion boundary: primitive/residual `True/True`; eta condition/closure/fixed proof `True/False/False`; residual/source-policy-full-TFE not promoted `True/True`; no-state-change `True`.",
        "Proof-claim traceability partition counts satisfied/total/retained-interfaces/open-nonpromotion: `1/7/5/1`.",
        "Proof-claim remaining theorem-boundary partition: `theorem_conditions_retained_not_submission_ready`; satisfied IDs `P5`; retained theorem-interface IDs `P1,P2,P3,P4,P6`; open output-boundary IDs `P7`; global boundaries `full_source_policy_package_ready,theorem_level_eta_h_solver_policy_evidence,closed_residual_to_error_theorem_for_mechanism_rows`.",
        "Proof-claim traceability close requirements/unsatisfied: `4/0`.",
        "Proof-claim traceability close requirements satisfied: `4`; PC3 condition retained `True`; PC4 residual promotion avoided `True`.",
        "Proof-claim traceability active direct Newton-Euler row split: `36/0` closed/open.",
        "Proof-claim traceability symbolic/primitive dynamic rows not certified by that route: `36` with scope `symbolic_primitive_certificate_route_not_active_direct_pc2`.",
        "Proof-claim traceability row-target map: `True`; Newton-Euler target rows `36` (`18/18`); defect certificate `False`.",
        "Proof-claim traceability Newton-Euler obligation coverage: matrix `True`, links `180`, complete rows `36`, proof closure advanced `False`.",
        "Proof-claim traceability Newton-Euler obligations: active direct open `0`; symbolic/primitive open/closed `1/5`; residual-to-error `7`.",
        "Proof-claim traceability open symbolic oracle recorded: `True`.",
        "Dynamic-row residual-identity table: `True` / `present_direct_substitution_closure_inputs`.",
        "Proof-closure Newton-Euler obligation coverage: matrix `True`, links `180`, complete rows `36`.",
        "Newton-Euler symbolic target audit: `newton-euler-symbolic-target-audit-v1` / `row_level_symbolic_targets_extracted_dynamic_defect_proof_open`; rows `36` (`18/18`); inventory `True`; defect certificate `False`.",
        (
            "Newton-Euler runtime source anchors: `True`; path `v047_cylindrical_chain_pipeline/run_v047.py`; "
            "tuple anchors `4`; primary dyn.extend line "
            f"`{source_anchors.get('primary_residual_dyn_extend', {}).get('line')}`."
        ),
        "Newton-Euler symbolic target obligation coverage: matrix `True`, links `180`, complete rows `36`, proof closure advanced `False`.",
        "Conditional proof boundary visible in manuscript/PDF: `True`.",
        "Order recomputation audit: `44` cells from `132` raw rows; mismatches `0`.",
        "Order recomputation external superiority allowed: `False`.",
        "Visual legibility audit: `b5_closed_mechanism_visual_reproducibility_checked`; B5 closed `True`; legacy visual-only B7-open flag `True`.",
        "Visual figure dimensions/captions: `2028x1759` main, `2028x1759` flat; captions/logs `True/True`.",
        "Figure-set audit: `b7_figure_set_closed_narrowed_common_reference_diagnostic_scope`; figures `13/13`, files/integration/captions `True/True/True`.",
        "Figure-set B7 boundary: Figure 12 integrated `True`; Figure 13 integrated `True`, B7 closed `True`, external superiority allowed `False`.",
        "B7 closure-readiness preflight: `b7_narrowed_diagnostic_common_reference_figure_scope_closed`; closed/open `13/0`; source-policy rows `0/40`; closure allowed `True`.",
        "B7 post-B4 figure-scope plan: `post_b4_source_policy_reintroduction_plan_ready_current_b7_closed`; retain `[1, 2, 3, 4, 5, 6, 7, 10, 11]`, refresh `[8, 12]`, rebuild `[9, 13]`, source-policy-dependent `4`, closure allowed `False`.",
        "B7 post-B4 ready-command boundary: ready/unaddressed rows `20/0`; not-ready lanes `['tfe_source_policy_work_precision', 'vp2024_source_code_path_work_precision']`; ready commands close B4/B7 `[False, False]`.",
        "Prose residue audit: `main_body_machine_tokens_removed_reproducibility_appendix_compacted_b6_closed_under_narrowed_policy`; main/flat machine tokens `0/0`; B6 closed `True`.",
        "B6 closure-readiness preflight: `b6_final_prose_pass_closed_under_narrowed_b4_b7_scope`; closed/open `11/0`; closure allowed `True`.",
        "B6 ready-command dependency: mapped/unaddressed rows `20/0`; not-ready lanes `['tfe_source_policy_work_precision', 'vp2024_source_code_path_work_precision']`; ready commands enable final prose `False`.",
        f"B6 post-execution dependency: `{expected_review_safe_prose_post_status}`; promoted rows `0/40`; closes B4/B7 `[False, False]`; enables final prose `False`.",
        "B6 proof-prose relocation: `finite_solver_probe_details_relocated_from_proof_boundary_b6_closed_under_narrowed_policy`; strict boundary preserved `True`; independently closes B6 `False`.",
        "Prose artifact confinement: `True`; appendix artifact macros `0`.",
        "Comparison reconciliation: matrix closed `True`; common-reference claim allowed `True`; source-policy superiority allowed `False`.",
        "Direct nonlocal diagnostic favorable order/error cells: `40/40` and `40/40`; common-reference diagnostics only.",
        "Comparison reconciliation B2/B4 can close now: `False`.",
        "Claim-hygiene audit: `pass`.",
        "Allowed claim: `conditional_formal_order_comparison`.",
        "Required-token missing count: `0`.",
        "Submission/support forbidden-hit counts: `0/0`.",
        "Source-policy/external superiority allowed: `False` / `False`.",
        "Submission-integrity audit: `cmame-submission-integrity-audit-v1` / `submission_integrity_passed_reference_web_verified`.",
        "Local integrity passed/submission ready: `True` / `False`.",
        "Citation keys main/flat: `28/28`; bibitems main/flat `28/28`.",
        "Dangling citation keys main/flat: `0/0`; orphan bibitems main/flat `0/0`.",
        "Reference metadata audit: `all_reference_metadata_web_verified`; DOI metadata `16/16`; non-DOI metadata `12/12`; non-DOI references open `0`.",
        "External reference web verification complete: `True`.",
        "Submission integrity gate closed: `True`.",
        "Source-policy diagnosis: `15` flagged rows; position-aligned velocity mismatches `10`.",
        "Source-policy recheck required: `True`.",
        "Source-policy diagnosis B2/B4 status: `not_closed`.",
        "Source-policy closure triage: `15` flagged rows across",
        "Source-policy triage B2/B4 can close now: `False/False`.",
        "Source-policy row closure ledger: `15` flagged rows across",
        "Source-policy row ledger current dispositions:",
        "Source-policy row ledger attempted-not-reproducible/not-promoted rows: `7`.",
        "Source-policy row ledger closed/claim-ready rows: `0/0`.",
        "Source-policy row ledger parallel-ready shards without default 1e-4: `20`.",
        "Source-policy row ledger B2/B4 can close now: `False/False`.",
        "All-example source-policy audit: `15` flagged rows and `45` raw rows across",
        "All-example source-policy suite counts:",
        "All-example source-policy rows closed: `False`.",
        "All-example source-policy B2/B4 can close now: `False/False`.",
        "All-example source-policy default 1e-4/heavy run: `False/False`.",
        "External suite dispositions: `4` suites; accepted external-superiority suites `0`.",
        "Suite-disposition parallel-ready shards without default 1e-4: `20`.",
        "Suite-disposition B2/B4 can close now: `False/False`.",
        "Source-policy closure manifest: `32/48` performance rows completed; not-complete `16`.",
        "Source-policy closure strict external error rows: `0`.",
        "Source-policy closure B2/B4 can close now: `False/False`.",
        "External case evidence reconciliation: case statuses `{'code_path_unresolved': 1, 'not_run': 16}`; bounded evidence suites",
        "External case reconciliation not-ready/demote suites:",
        "External case reconciliation 2021 public baseline/timing rows: `12/12` groups and `12/12` timing rows.",
        "External case reconciliation local source-policy dynamic-order examples: `0/4`; double public policy `False`; closed-loop row kind `kinematic_reaction_residual_not_true_dynamic_order`.",
        "External case reconciliation closed/claim-ready rows: `0/0`.",
        "External case reconciliation accepted dynamic-order examples and B2/B4: `0` and `False/False`.",
        "HI2022 policy decision audit: `bounded_T0p1_rows_complete_full_T8_source_policy_open`; bounded rows `24/24`, bounded groups `8/8`.",
        "HI2022 bounded policy: T values `[0.1]`, h values `[0.005, 0.01, 0.02]`; full T=8 required/completed `True/False`.",
        "HI2022 bounded/external acceptance: `True/False`; source-policy dynamic-order examples `0/4`.",
        "HI2022 decision/shards/default 1e-4/heavy/run_v047: `choose_full_T8_reproduction_or_explicit_demotion` / `8` / `False` / `False` / `False`.",
        "HI2022 source-policy row audit: `hi2022-source-policy-row-audit-v1` / `bounded_T0p1_rows_complete_full_T8_source_policy_rows_not_closed`.",
        "HI2022 source-policy active/closed/claim-ready rows: `3/0/0`.",
        "HI2022 source-policy bounded rows/groups: `24/24` and `8/8`.",
        "HI2022 T=8 coarse sanity rows/groups: `18/24` and `4/8`; source-policy reproduction `False`; v048 runner evidence `True`.",
        "HI2022 T=8 tolerance repair combined best: `19/24` rows and `4/8` groups; recovered rows `1`; source-policy reproduction `False`; external superiority `False`.",
        "HI2022 can close B2 now/default 1e-4/heavy/run_v047: `False/False/False/False`.",
        "VP2024 code-path disposition: `all_four_examples_checked_no_distinct_public_code_unable_to_reproduce_not_promoted`; examples `single_pendulum,double_pendulum,four_link,slider_crank`.",
        "VP2024 source-policy rows unresolved: `4/4`; distinct public code path found `False`.",
        "VP2024 source-policy attempted/unable/final disposition: `4/4/unable_to_reproduce_not_promoted`.",
        "VP2024 public-code recheck: `public_code_rechecked_no_distinct_vp2024_path_attempted_not_reproducible` on `2026-06-13`; tree truncated `False`; paths/all-2024/keyword-hits `4487/1540/0`; attempted-not-reproducible/closed `4/0`; external superiority `False`.",
        "VP2024 local public-code scan: sbel dirs `2021,2022`; visible MBD roots `3`; velocity-partition hits `0`; local distinct path `False`.",
        "VP2024 common-reference proxy diagnostic favorable local order/error cells: `4/4` and `4/4`; VP source-policy code path remains unresolved.",
        "VP2024 larger-step diagnostic local error wins: `1/4`; noncontrolling `True`.",
        "VP2024 proxy/source-policy boundary: proxy reproduction `False`; claim allowed `code-path-unresolved_related_work_only`; default 1e-4/heavy run `False/False`.",
        "External suite demotion ledger: `external-suite-demotion-ledger-v1` / `all_external_suites_demoted_from_external_superiority_scope`.",
        "External suite demotion closed B2 subrequirements: `['vp2024_code_resolution_or_demotion', 'hi2022_public_code_same_test_rows', 'ra2021_public_code_same_test_rows', 'original_tfe_pendulum_error_order_work_rows']`.",
        "External suite demotion remaining B2 requirements: `[]`.",
        "External suite demotion VP2024 rows/flagged rows: `4/3`; active flagged rows `0`.",
        "External suite demotion HI2022 rows/flagged rows: `3/3`.",
        "External suite demotion remaining open suites:",
        "External suite demotion default 1e-4/heavy/run_v047: `False/False/False`.",
        "B2 source-policy remaining-work manifest: `b2-source-policy-remaining-work-manifest-v1` / `route_b_all_external_suites_demoted_no_active_external_superiority_rows`.",
        "B2 remaining-work active/demoted flagged rows: `0/15` from `15` total.",
        "B2 remaining-work source-policy closed/claim-ready rows: `0/0`.",
        "B2 remaining-work active suite counts:",
        "B2 remaining-work closed by demotion: `['vp2024_code_resolution_or_demotion', 'hi2022_public_code_same_test_rows', 'ra2021_public_code_same_test_rows', 'original_tfe_pendulum_error_order_work_rows']`.",
        "B2 remaining-work default 1e-4/heavy/run_v047: `False/False/False`.",
        "B2 closure execution plan: `b2-source-policy-closure-execution-plan-v1`; lanes `0`; all active suites ready `True`; explicit 1e-4 opt-in `True`; plan-only superiority `False`.",
        "B4 work/precision execution plan: `b4-source-policy-work-precision-execution-plan-v1` / `execution_plan_ready_b4_b7_remain_open`; open blockers `[]`; source-policy rows `0/40`.",
        "B4 work/precision lanes and execution guard: ready/not-ready `2/2`; heavy/run_v047/v048 `False/False/False`; user opt-in required `True`.",
        "B4 RA2021/HI2022 launch preflights: `ready_not_run_requires_user_opt_in` commands `5`; `preflight_ready_existing_selected_candidate_matrix_incomplete` commands/completed/missing `8/7/1`.",
        "B4 RA2021/HI2022 CLI contracts: `runner_cli_contract_satisfied` runner/command checks `4/5`; `runner_cli_contract_satisfied` runner/command checks `1/8`.",
        "B4 HI2022 launch boundary: avoids 1e-4 `True`; source-policy rows closed `0`; closes B4/B7 `False/False`.",
        "B4 existing-artifact promotion audit: `no_existing_artifact_promotable_without_new_source_policy_execution`; candidates `8`; promotion-ready `0`; source-policy rows `0/40`; closes B4/B7 `0/0`.",
        f"B4 post-execution audit: `{b4_post_execution_audit.get('status')}`; verified-authorized/existing-artifacts/output-present `{authorized_b4}/True/True`; scope `{expected_b4_scope}`; promoted rows `0/40`; B4/B7 close `False/False`; RA2021/HI2022 status `executed_order_below_acceptance_not_promoted` / `selected_candidate_matrix_partially_executed_not_promoted`.",
        "RA/HI source-policy post-execution attempt certificate: `post_execution_attempts_recorded_rows_not_promoted_full_source_policy_open`; rows RA/HI/total `12/8/20`; promoted/open `0/20`.",
        "RA/HI source-policy closeout checklist: `ready_for_authorized_execution_closeout_not_executed_not_promoted`; rows RA/HI/total `12/8/20`; commands/mapped `13/20`; promoted/completed/external-ready `0/0/0`; opt-in/executed `True/False`; closes B4/B7 `False/False`.",
        "RA/HI source-policy output inventory: `existing_expected_outputs_present_not_promotion_evidence`; commands/outputs/summaries `13/13/8`; csv rows/HI ok/closed `54/22/0`.",
        "HI2022 rA_half double repair-attempt certificate: `targeted_repair_attempted_not_reproducible_not_promoted`; target ok/failed `1/2`; combined rows/groups `19/24` and `4/8`; promoted/source-closed `0/False`.",
        "B4 source-policy row closure-readiness ledger: `all_40_external_rows_mapped_20_attempted_not_reproducible_0_source_policy_rows_closed`; external rows `40/40`; closed/open `0/20`; command-mapped/no-command `20/20`; ready/not-ready suites `2/2`.",
        "B4 execution opt-in packet: `ready_for_user_opt_in_packet_not_authorized_not_run`; opt-in required `True`; commands `13`; mapped/unaddressed rows `20/0`; source-policy rows `0/40`.",
        "Source-policy execution handoff traceability: unique RA/HI rows `20/20`; row refs `32/32`; mismatches/terminal/closed/promotion-ready `0/0/0/0`.",
        "B4 post-execution promotion contract: `b4-source-policy-post-execution-promotion-contract-v1` / `promotion_contract_defined_no_rows_promoted`; rows `0/40`; ready/unaddressed `20/0`; checks satisfied `False`; closes B4/B7 `False/False`.",
        "External-superiority claim-demotion audit: `external-superiority-claim-demotion-audit-v1` / `route_b_applied_to_claim_boundary_no_external_superiority`; Route B ready `True`; B2/B4 closed by route `True/False`.",
        "Claim-demotion retained evidence: formal order `True`, common-reference cells `44`, diagnostic favorable order/error cells `40/40`; external-superiority remains demoted.",
        "Claim-demotion demotion scope: current `['hi2022_half_implicit', 'ra2021_absolute_coordinate', 'tfe2026_original_pendulum', 'vp2024_velocity_partitioning']`, additional `[]`, full `['hi2022_half_implicit', 'ra2021_absolute_coordinate', 'tfe2026_original_pendulum', 'vp2024_velocity_partitioning']`.",
        "Claim-demotion default 1e-4/heavy/run_v047: `False/False/False`.",
        "Claim-demotion Route B application contract: `route-b-application-contract-v1`; ready-to-promote `True`; safe flag flip `False`; satisfied steps `6/6`; creates numerical wins `False`; unsatisfied `[]`.",
        "RA2021 source-policy row audit: `ra2021-source-policy-row-audit-v1` / `public_rows_complete_source_policy_rows_not_closed`.",
        "RA2021 per-row source-identity resolved / promotion remaining requirements: `3/4`; row missing evidence shrunk `True`.",
        "RA2021 promotion-gap drilldown: checked `True`; examples/active rows `4/0`; source identity/promotion closed `True/False`.",
        "RA2021 promotion-gap statuses: single `not_promoted_floor_limited_public_h_tranche`, double `not_promoted_coarse_h_and_reference_policy_mismatch`, closed-loop `not_promoted_true_dynamic_not_source_policy_and_public_horizon_not_dynamic_order`.",
        "RA2021 source-identity audit: `ra2021-source-identity-audit-v1` / `source_output_time_grid_policy_extracted_promotion_still_open`; output mapping/time-grid `True/True`; source-policy rows `0`; external superiority `False`.",
        "RA2021 active B2 rows and public order/timing groups: `0`; `12/12` and `12/12`.",
        "RA2021 fixed-grid/paper-safe/source-policy rows: `12/12`, `12/12`, `0/12`.",
        "RA2021 velocity mismatch/nonmonotone rows: `9/1`.",
        "RA2021 can close B2 now/default 1e-4/heavy/run_v047: `False/False/False/False`.",
        "TFE source-policy spec: `tfe-source-policy-spec-v1` / `source_policy_extracted_candidate_scaffold_present_source_policy_open`.",
        "TFE source-policy reference h and completed rows: `0.0001` / `0`.",
        "TFE source-policy runner/external superiority allowed: `False` / `False`.",
        "TFE public-code recheck: `public_code_rechecked_no_distinct_tfe_code_artifact_attempted_not_reproducible` on `2026-06-13`; repo/user/code-search `0/0/requires_authentication`; attempted-not-reproducible/closed `16/0`; external superiority `False`.",
        "TFE candidate/source-policy boundary sources/match/use: `TFE_SOURCE_POLICY_SPEC.json,TFE_SOURCE_POLICY_ROW_AUDIT.json,TFE_DAE_RUNNER_CONTRACT_GAP_AUDIT.json,TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.json/True/diagnostic_scaffold_only_not_source_policy_reproduction`.",
        "TFE self-reproduction attempt certificate: `attempted_not_reproducible_not_promoted`; attempted/not-reproducible/closed rows `16/16/0`.",
        "TFE self-reproduction preflight route/reopen/source rows: `no_public_code_self_reproduction_attempted_unable_to_reproduce_not_promoted/new_public_or_source_code_equivalent_tfe_implementation_artifact/0`.",
        "TFE self-reproduction preflight blocks/ready/promote/next-actions: `4/False/False/3`.",
        "TFE candidate/source-policy boundary scaffold/DAE-equivalent/method-equivalent/source rows/external-superiority: `True/False/False/0/False`; promotion required `True` with obligations `5`.",
        "TFE DAE runner contract accounting raw/non-heavy-terminal/effective-execution/source-rows: `6/2/4/0`.",
        "TFE DAE runner effective execution blocks: `['pendulum_absolute_coordinate_source_policy_dae_runner_missing', 'tfe_newmark_trapezoidal_source_policy_method_runners_missing', 'gauss6_fullva_absolute_coordinate_source_policy_runner_missing', 'accepted_source_policy_work_precision_rows_not_executed_or_bound']`.",
        "TFE source-policy execution preflight status/opt-in/nonheavy/execution/promote/ready: `terminal_no_public_code_self_reproduction_attempted_not_promoted/False/True/4/False/False`.",
        "TFE source-policy row audit: `tfe-source-policy-row-audit-v1` / `source_policy_spec_extracted_runner_rows_not_closed`.",
        "TFE active/source-policy-closed/claim-ready rows: `0/0/0`.",
        "TFE spec extracted/pendulum runner implemented: `True/False`.",
        "TFE source grid policy resolved/compatible/incompatible rows: `False/2/4`.",
        "TFE exact-T endpoint-grid subset resolved/requires policy: `True/2/4`.",
        "TFE endpoint sensitivity diagnostic: `diagnostic_endpoint_policy_sensitivity_not_source_policy`; methods/policies/raw rows `4/4/48`; source-policy rows `0`; superiority allowed `False`.",
        "TFE full-T10 coarse candidate summary: `full_T10_coarse_candidate_probe_summarized_not_source_policy`; rows/finite/residual-ok/source-policy `4/4/4/0`; source reference invoked `False`.",
        "TFE source pendulum model audit: `tfe-source-pendulum-model-audit-v1` / `source_parameter_model_implemented_runner_policy_open`.",
        "TFE source pendulum parameters/smoke/setup closed: `True/True/True`.",
        "TFE source pendulum absolute-coordinate residual/source-policy-equivalent: `True/True` / `False`.",
        "TFE source pendulum source-output time smoke/source-policy-equivalent: `True` / `False`.",
        "TFE source pendulum bounded reference-policy smoke/full T=10 source run: `True/False`.",
        "TFE source pendulum full-T=10 source-reference feasibility probe: implemented/completed/source-policy rows `True/True/0`; source/check steps `100000/200000`; coordinate/velocity check errors `3.819e-14/2.485e-13`.",
        "TFE source pendulum comparator candidate runners/Newmark/trapezoidal/TFE-m-candidate/method-equivalent/TFE m=1-3 source-policy: `True/True/True/True/False/False`.",
        "TFE source pendulum Gauss6 candidate smoke/absolute-coordinate source-policy runner: `True/False`.",
        "TFE source pendulum Gauss6 candidate rows/source-policy rows/method-equivalent: `2/0/False`.",
        "TFE source pendulum Appendix-B coefficient certificate: `True`; rows/max diff `3/0.000e+00`.",
        "TFE source pendulum unified bounded runner rows/full T=10/source-policy rows: `4/False/0`.",
        "TFE source pendulum active-B2 candidate rows/full T=10/source-policy rows: `4/False/0`.",
        "TFE source pendulum active-B2 full-T10 coarse probe: implemented/fullT10/source-policy rows/finite/residual-ok/source-ref-invoked `True/True/0/4/4/False`.",
        "TFE source pendulum active-B2 source-reference full-T10 probe: implemented/fullT10/reference-invoked/source-policy rows/finite/residual-ok/method-equivalent `True/True/True/0/4/4/False`.",
        "TFE source pendulum m=3 full-T10 formula probe: implemented/fullT10/expected/source-policy rows/finite/residual-ok/source-ref-invoked `True/True/5/0/1/1/False`.",
        "Manuscript/PDF include TFE Brown--McPhee source-policy boundary: `True/True`.",
        "Manuscript/PDF include minimal reproducibility package boundary: `True/True`.",
        "TFE source pendulum candidate friction/smoke provenance: `True/True` / `v022_revolute_brown_mcphee_surrogate_not_source_policy_equivalent`.",
        "TFE source pendulum Brown--McPhee anchors/formula/source-equivalent: `True/True/True` / `True/False`.",
        "TFE source pendulum DAE/friction/output rows: `False/False/True`; rows `0`.",
        "TFE can close B2 now/default 1e-4/heavy/run_v047: `False/False/False/False`.",
        "Common-reference traceability rows: `44/44`.",
        "Source-policy apples-to-apples external rows: `0/40`.",
        "Four-example source-policy dashboard: `all_four_examples_checked_source_policy_dynamic_order_open`",
        "local evidence coverage `4/4`",
        "accepted method dynamic-order examples `2/4`",
        "mechanism-coverage examples `2/4`",
        "accepted source-policy dynamic-order examples `0/4`",
        "Closed-loop coarse-window trajectory diagnostics: `2/2`",
        "Four-example dashboard common-reference wins: `40/40` order and `40/40` error; source-policy closed rows `0`.",
        "Global comparison-policy audit: `14/14`.",
        "Proof-closure manifest: `proof-closure-manifest-v1`.",
        "Proof-closure status: `pc2_closed_by_direct_residual_bridge_global_boundary_retained`.",
        "Proof remaining-work manifest: `proof-remaining-work-manifest-v1` / `proof_b1_b3_closed_submission_gates_remaining`.",
        "Proof remaining-work unsatisfied close requirements: `0` / `[]`.",
        "Newton-Euler symbolic defect certificate artifact: `newton-euler-symbolic-defect-certificate-v1` / `balance_identities_closed_defect_not_proved`.",
        "Newton-Euler runtime expression structure checked/rows: `True/36`; this is source-expression traceability, not proof closure.",
        "Proof-closure active direct Newton-Euler row split: `36/0` closed/open.",
        "Proof-closure symbolic/primitive dynamic rows not certified by that route: `36` with scope `symbolic_primitive_certificate_route_not_active_direct_pc2`.",
        "Proof-closure Newton-Euler obligations: active direct open `0`; symbolic/primitive open/closed `1/5` with scope `symbolic_primitive_certificate_route_not_active_direct_pc2`; residual-to-error `7`.",
        "Proof-closure direct-PC2 route/stage defect/eta_h closure: `True/True/False`.",
        "Proof-closure theorem/manuscript traceability: labels/boundary/mapped `True/True/True`; dependency/dynamic/primitive/nonpromotion `True/True/True/True`.",
        "Proof-closure theorem no-promotion boundary: eta condition/closure `True/False`; fixed-tolerance proof `False`; residual/source-policy-full-TFE not promoted `True/True`; no-state-change `True`.",
        "Newton-Euler obligation table/count: `True/6`.",
        "Symbolic oracle complete: `False`.",
        "Solver-scale submission-ready scope: `solver_scale_global_eta_h_boundary_not_narrowed_claim_package_decision`; audit scope `finite_solver_scale_diagnostic_and_theorem_level_eta_h_boundary`.",
        "Solver-scale narrowed B4/B6/B7 statuses: `closed/closed/closed`; global boundaries `full_source_policy_package_ready,theorem_level_eta_h_solver_policy_evidence,closed_residual_to_error_theorem_for_mechanism_rows`.",
        "Finite scaled-tolerance probe rows/max eta-h ratio: `4/4` / `127.583723`; theorem closed `False`.",
        "Finite scaled-tolerance trajectory probe rows/steps/max eta-h ratio: `4/4` / `30` / `210.890786`; theorem closed `False`.",
        "Finite tolerance-regime sweep policies/rows/steps: `3` / `12` / `90`; theorem closed `False`.",
        "External superiority claim: `False`.",
        "OC6 reopen latest external probe carried by full-archive gap: `2026-06-21/9/0/0/4/False/False`.",
    ]:
        checks.check(token in report_md, f"review-agent markdown missing token: {token}")

    if checks.errors:
        print("cmame review-agent validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("cmame review-agent validation: PASS")
    print("submission_standard_met=False")
    print("decision=do_not_submit_global")
    print("narrowed_claim_subcheck_disposition=bounded_subcheck_satisfied_not_global_submit")
    print("legacy_narrowed_submission_standard_met=True")
    print("legacy_narrowed_claim_decision=submit_under_narrowed_claim")
    print(f"open_blockers={','.join(open_blockers)}")
    print(f"open_blocker_ids={','.join(report.get('open_blocker_ids', []))}")
    print(
        "evidence_summary="
        f"{evidence_summary.get('source_policy_apples_to_apples_external')}/"
        f"{evidence_summary.get('accepted_source_policy_dynamic_order_examples')}/"
        f"{evidence_summary.get('full_source_policy_runner_package_ready')}/"
        f"{evidence_summary.get('minimal_submission_code_dependency_boundary_status')}"
    )
    print(f"tfe_runner_contract_preflight={evidence_summary.get('tfe_runner_contract_preflight')}")
    print(f"oc12_archive_tfe_preflight={evidence_summary.get('oc12_archive_tfe_preflight')}")
    print(f"oc12_archive_action_boundary={evidence_summary.get('oc12_archive_action_boundary')}")
    print(f"oc6_reopen_latest_external_probe={evidence_summary.get('oc6_reopen_latest_external_probe')}")
    print(
        "oc12_archive_safe_action_ids="
        + ",".join(external_checks.get("oc12_archive_safe_action_ids", []))
    )
    print(
        "oc12_archive_opt_in_action_ids="
        + ",".join(external_checks.get("oc12_archive_opt_in_action_ids", []))
    )
    print(EXPECTED_BLOCKER_OPEN_TOKEN)
    print(EXPECTED_BLOCKER_CLOSURE_DECISION_TOKEN)
    print(EXPECTED_BLOCKER_CLOSURE_ALLOWED_TOKEN)
    print("common_reference_traceability=44/44")
    print("source_policy_apples_to_apples_external=0/40")
    print("global_comparison_policy=14/14")
    print("source_policy_triage=15")
    return 0


if __name__ == "__main__":
    sys.exit(main())
