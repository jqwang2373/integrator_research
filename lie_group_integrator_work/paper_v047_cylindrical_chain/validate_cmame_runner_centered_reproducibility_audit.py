#!/usr/bin/env python3
"""Validate the runner-centered reproducibility-package audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
ROOT = PAPER.parent
EXPECTED_SAFE_ACTION_IDS = [
    "rebuild_read_only_audit_chain",
    "rerun_read_only_validators",
    "keep_narrowed_archive_provenance_only",
    "monitor_reopen_conditions",
]
EXPECTED_OPT_IN_ACTION_IDS = ["authorized_b4_ra_hi_source_policy_execution"]
EXPECTED_APPROVAL_STATEMENT = (
    "I explicitly approve running the B4 source-policy execution commands listed in "
    "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json."
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


def resolve(path_label: str) -> Path:
    if path_label.startswith("../"):
        return (manuscript_path(path_label)).resolve()
    return manuscript_path(path_label)


def line_count(path: Path) -> int:
    return len(read_text(path).splitlines())


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(PAPER / "CMAME_RUNNER_CENTERED_REPRODUCIBILITY_AUDIT.json")
        audit_md = read_text(PAPER / "CMAME_RUNNER_CENTERED_REPRODUCIBILITY_AUDIT.md")
        review = read_json(PAPER / "CMAME_REVIEW_AGENT_REPORT.json")
        matrix = read_json(PAPER / "PAPER_NUMERICAL_RESULT_MATRIX.json")
        minimal = read_json(PAPER / "CMAME_MINIMAL_REPRODUCIBILITY_CANDIDATE_MANIFEST.json")
        runner_adapter = read_json(PAPER / "CMAME_RUNNER_ADAPTER_CANDIDATE_MANIFEST.json")
        b6_local_evidence_source = read_json(PAPER / "B6_FOUR_EXAMPLE_LOCAL_EVIDENCE_SUMMARY.json")
        closed_loop_audit_source = read_json(PAPER / "B6_CLOSED_LOOP_SELF_CONTAINED_EXTRACTION_AUDIT.json")
        closed_loop_candidate_source = read_json(PAPER / "CMAME_CLOSED_LOOP_LOCAL_RUNNER_CANDIDATE_MANIFEST.json")
        dashboard = read_json(PAPER / "FOUR_EXAMPLE_SOURCE_POLICY_DASHBOARD.json")
        proof = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
        b4_execution_handoff = read_json(PAPER / "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json")
        full_source_policy_row_provenance = read_json(PAPER / "FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.json")
        objective_completion = read_json(PAPER / "OBJECTIVE_COMPLETION_AUDIT.json")
    except Exception as exc:  # noqa: BLE001
        print(f"cmame runner-centered reproducibility audit validation: FAIL\n- {exc}")
        return 1

    checks.check(
        audit.get("schema") == "cmame-runner-centered-reproducibility-audit-v1",
        "schema changed",
    )
    checks.check(
        audit.get("status") == "local_runner_centered_candidate_ready_source_policy_package_open",
        "status changed",
    )
    checks.check(
        "B6_CLOSED_LOOP_SELF_CONTAINED_EXTRACTION_AUDIT.json" in audit.get("generated_from", []),
        "B6 closed-loop extraction audit missing from runner-centered provenance",
    )
    checks.check(
        "CMAME_CLOSED_LOOP_LOCAL_RUNNER_CANDIDATE_MANIFEST.json" in audit.get("generated_from", []),
        "closed-loop local runner candidate missing from runner-centered provenance",
    )
    checks.check(
        "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json" in audit.get("generated_from", []),
        "B4 source-policy handoff missing from runner-centered provenance",
    )
    checks.check(
        "FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.json" in audit.get("generated_from", []),
        "full source-policy row provenance missing from runner-centered provenance",
    )
    checks.check(
        "TFE_DAE_RUNNER_CONTRACT_GAP_AUDIT.json" in audit.get("generated_from", []),
        "TFE DAE gap missing from runner-centered blocker-map provenance",
    )
    checks.check(
        "TFE_RUNNER_CONTRACT_PREFLIGHT_CERTIFICATE.json" in audit.get("generated_from", []),
        "TFE runner contract preflight missing from runner-centered blocker-map provenance",
    )
    checks.check(
        "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.json" in audit.get("generated_from", []),
        "latest source-policy public-code refresh missing from runner-centered blocker-map provenance",
    )
    checks.check(
        "CMAME_NARROWED_REPRO_CODE_ARCHIVE_MANIFEST.json" in audit.get("generated_from", []),
        "narrowed repro archive manifest missing from runner-centered blocker-map provenance",
    )
    checks.check(audit.get("read_only") is True, "audit must be read-only")
    checks.check(audit.get("submission_ready") is False, "audit must not mark submission ready")
    checks.check(
        audit.get("runner_centered_package_ready") is False,
        "runner-centered package unexpectedly ready",
    )
    checks.check(
        audit.get("local_runner_centered_candidate_ready") is True,
        "local runner-centered candidate should be ready",
    )
    checks.check(
        audit.get("full_source_policy_runner_package_ready") is False,
        "full source-policy runner package unexpectedly ready",
    )
    result_checks = review.get("result_checks", {})
    checks.check(
        audit.get("candidate_python_file_count") == minimal.get("candidate_python_file_count") == 1
        and audit.get("candidate_python_line_count") == minimal.get("candidate_python_line_count"),
        "top-level candidate Python summary stale",
    )
    checks.check(
        audit.get("source_policy_rows_closed")
        == result_checks.get("source_policy_apples_to_apples_external_rows")
        == 0
        and audit.get("source_policy_rows_total")
        == result_checks.get("source_policy_apples_to_apples_external_total_rows")
        == 40
        and audit.get("source_policy_closed_ratio") == "0/40",
        "top-level source-policy row summary stale",
    )
    checks.check(
        audit.get("source_policy_execution_allowed_now")
        == b4_execution_handoff.get("source_policy_execution_allowed_now")
        is False
        and audit.get("source_policy_execution_invoked")
        == b4_execution_handoff.get("source_policy_execution_invoked")
        is False
        and audit.get("exact_b4_opt_in_required_for_execution")
        == b4_execution_handoff.get("exact_b4_opt_in_required_for_execution")
        is True
        and audit.get("safe_action_ids")
        == b4_execution_handoff.get("safe_action_ids")
        == EXPECTED_SAFE_ACTION_IDS
        and audit.get("opt_in_action_ids")
        == b4_execution_handoff.get("opt_in_action_ids")
        == EXPECTED_OPT_IN_ACTION_IDS
        and audit.get("required_user_approval_statement") == EXPECTED_APPROVAL_STATEMENT
        and audit.get("guarded_execution_driver") == "run_b4_source_policy_after_opt_in.sh",
        "top-level source-policy action-boundary aliases stale",
    )
    checks.check(
        audit.get("safe_next_actions_without_b4_opt_in")
        == objective_completion.get("safe_actions_without_b4_opt_in")
        and audit.get("opt_in_required_actions")
        == objective_completion.get("opt_in_required_actions"),
        "runner-centered safe/opt-in action objects drifted from objective audit",
    )
    runner_required_to_close = audit.get("runner_package_blocker_required_to_close_by_id", {})
    runner_safe_next_actions = audit.get("runner_package_blocker_safe_next_actions_by_id", {})
    runner_opt_in_actions = audit.get("runner_package_blocker_opt_in_required_actions_by_id", {})
    checks.check(
        audit.get("blocker_required_to_close_by_id") == runner_required_to_close
        and audit.get("blocker_safe_next_actions_by_id") == runner_safe_next_actions
        and audit.get("blocker_opt_in_required_actions_by_id") == runner_opt_in_actions,
        "runner-centered generic blocker map aliases are stale",
    )
    checks.check(
        runner_required_to_close
        == objective_completion.get("blocker_required_to_close_by_id")
        and runner_safe_next_actions
        == objective_completion.get("blocker_safe_next_actions_by_id")
        and runner_opt_in_actions
        == objective_completion.get("blocker_opt_in_required_actions_by_id"),
        "runner-centered blocker maps drifted from objective audit",
    )
    checks.check(
        set(runner_required_to_close)
        == set(runner_safe_next_actions)
        == set(runner_opt_in_actions)
        == {"OC4", "OC6", "OC12"},
        "runner-centered blocker map keys changed",
    )
    oc4_close = runner_required_to_close.get("OC4", {})
    oc4_route = oc4_close.get("authorized_ra_hi_closeout_route", {})
    checks.check(
        oc4_close.get("current_source_policy_closed_ratio") == "0/40"
        and oc4_close.get("source_policy_rows_closed") == 0
        and oc4_close.get("source_policy_rows_total") == 40
        and oc4_route.get("requires_exact_b4_opt_in") is True
        and oc4_route.get("execution_allowed_now") is False
        and oc4_route.get("execution_invoked") is False
        and oc4_route.get("guarded_execution_driver") == "run_b4_source_policy_after_opt_in.sh"
        and oc4_route.get("opt_in_required_command_count") == 13
        and oc4_route.get("opt_in_required_mapped_external_rows") == 20,
        "runner-centered OC4 required-to-close boundary changed",
    )
    oc6_close = runner_required_to_close.get("OC6", {})
    oc6_probe = oc6_close.get("latest_external_probe", {})
    checks.check(
        oc6_close.get("tfe_runner_closed") is False
        and oc6_close.get("source_policy_rows_completed") == 0
        and oc6_close.get("contract_preflight_status")
        == "contract_entrypoints_callable_candidate_backed_source_policy_open"
        and oc6_close.get("effective_execution_block_count") == 4
        and oc6_close.get("reopen_condition")
        == "new_public_or_source_code_equivalent_tfe_implementation_artifact"
        and oc6_probe.get("date") == "2026-06-21"
        and oc6_probe.get("positive_public_code_artifact_rows") == 0
        and oc6_probe.get("source_policy_rows_closed") == 0
        and oc6_probe.get("reopen_triggered") is False,
        "runner-centered OC6 required-to-close boundary changed",
    )
    oc12_close = runner_required_to_close.get("OC12", {})
    checks.check(
        oc12_close.get("upstream_blockers") == ["OC4", "OC6"]
        and oc12_close.get("current_archive_usable_as_full_source_policy_runner_archive")
        is False
        and oc12_close.get("full_source_policy_runner_package_ready") is False
        and oc12_close.get("narrowed_repro_code_archive_ready") is True
        and oc12_close.get("narrowed_repro_code_archive_submission_ready") is False
        and oc12_close.get("source_policy_closed_ratio") == "0/40"
        and oc12_close.get("remaining_source_policy_rows_to_close") == 40
        and oc12_close.get("action_boundary")
        == full_source_policy_row_provenance.get("action_boundary"),
        "runner-centered OC12 required-to-close boundary changed",
    )
    checks.check(
        all(
            runner_safe_next_actions.get(req_id)
            == audit.get("safe_next_actions_without_b4_opt_in")
            for req_id in ["OC4", "OC6", "OC12"]
        )
        and runner_opt_in_actions.get("OC4") == audit.get("opt_in_required_actions")
        and runner_opt_in_actions.get("OC6") == []
        and runner_opt_in_actions.get("OC12") == audit.get("opt_in_required_actions"),
        "runner-centered blocker action map payloads changed",
    )
    handoff = audit.get("source_policy_execution_handoff", {})
    checks.check(
        handoff.get("status")
        == b4_execution_handoff.get("status")
        == "source_policy_execution_handoff_ready_not_authorized_not_run"
        and handoff.get("execution_authorized") is False
        and handoff.get("commands_not_run_by_handoff") is True
        and handoff.get("guarded_execution_driver") == "run_b4_source_policy_after_opt_in.sh"
        and handoff.get("driver_requires_exact_approval") is True
        and handoff.get("driver_does_not_authorize_execution") is True
        and handoff.get("opt_in_required_command_count") == 13
        and handoff.get("opt_in_required_mapped_external_rows") == 20,
        "top-level source-policy handoff boundary stale",
    )
    checks.check(
        audit.get("full_source_policy_row_provenance_status")
        == full_source_policy_row_provenance.get("status")
        == "row_provenance_preflight_complete_source_policy_promotion_open"
        and audit.get("full_source_policy_row_provenance_action_boundary")
        == full_source_policy_row_provenance.get("action_boundary")
        and audit.get("full_source_policy_row_provenance_source_policy_execution_invoked")
        == full_source_policy_row_provenance.get("source_policy_execution_invoked")
        is False
        and audit.get("full_source_policy_row_provenance_preflight") == "40/40"
        and audit.get("full_source_policy_row_provenance_promotion_ready_rows") == 0,
        "top-level row provenance summary stale",
    )
    checks.check(audit.get("reviewer_facing_python_file_limit") == 12, "file limit changed")
    checks.check(audit.get("reviewer_facing_python_line_limit") == 2000, "line limit changed")

    current = audit.get("current_candidate", {})
    checks.check(current.get("status") == minimal.get("status"), "candidate status stale")
    checks.check(current.get("submission_ready") is False, "candidate overclaims submission ready")
    checks.check(current.get("python_file_count") == minimal.get("candidate_python_file_count") == 1, "candidate Python file count changed")
    checks.check(
        current.get("python_line_count") == minimal.get("candidate_python_line_count"),
        "candidate Python line count stale",
    )
    checks.check(current.get("size_ok") is True, "candidate should remain size-ok")
    checks.check(current.get("replay_only") is True, "candidate replay-only marker missing")
    checks.check(current.get("runner_centered") is False, "candidate unexpectedly runner-centered")
    runner_boundary = audit.get("runner_package_boundary", {})
    checks.check(
        runner_boundary.get("local_accepted_rows_runner_centered") is True,
        "runner boundary lost local accepted-row runner readiness",
    )
    checks.check(
        runner_boundary.get("full_source_policy_runner_centered") is False,
        "runner boundary overclaims full source-policy runner",
    )
    checks.check(
        runner_boundary.get("b6_final_prose_pass_ready") is True
        and runner_boundary.get("b6_final_prose_pass_scope") == "narrowed_claim_current_submission"
        and runner_boundary.get("full_source_policy_b6_prose_ready") is False
        and runner_boundary.get("b6_closure_preflight_status")
        == "b6_final_prose_pass_closed_under_narrowed_b4_b7_scope"
        and runner_boundary.get("b6_closure_allowed_now") is True,
        "runner boundary lost narrowed/full-source B6 prose split",
    )
    checks.check(
        runner_boundary.get("source_policy_rows_closed") == 0
        and runner_boundary.get("source_policy_rows_total") == 40,
        "runner boundary source-policy row counts changed",
    )
    checks.check(
        runner_boundary.get("blocker_required_to_close_by_id") == runner_required_to_close
        and runner_boundary.get("blocker_safe_next_actions_by_id")
        == runner_safe_next_actions
        and runner_boundary.get("blocker_opt_in_required_actions_by_id")
        == runner_opt_in_actions,
        "runner boundary blocker maps are stale",
    )
    checks.check(
        "narrowed current-claim policy" in runner_boundary.get("reason_b6_final_prose_deferred", "")
        and "source-policy row closure" in runner_boundary.get("reason_b6_final_prose_deferred", ""),
        "runner boundary missing narrowed/full-source prose reason",
    )
    adapter = audit.get("runner_adapter_candidate", {})
    checks.check(adapter.get("present") is True, "runner adapter candidate not carried into audit")
    checks.check(
        adapter.get("schema") == runner_adapter.get("schema") == "cmame-runner-adapter-candidate-v1",
        "runner adapter schema changed in audit",
    )
    checks.check(adapter.get("runner_adapter_present") is True, "runner adapter marker missing from audit")
    checks.check(adapter.get("self_contained_simulation_runner") is False, "runner adapter overclaims self-contained runner")
    checks.check(
        adapter.get("external_v048_required_for_report_generation") is True,
        "runner adapter v048 dependency marker missing",
    )
    checks.check(
        adapter.get("closed_loop_local_rows_replay_present")
        == runner_adapter.get("closed_loop_local_rows_replay_present")
        is True,
        "runner adapter closed-loop replay marker missing from audit",
    )
    checks.check(
        adapter.get("closed_loop_local_rows_summary_present")
        == runner_adapter.get("closed_loop_local_rows_summary_present")
        is True,
        "runner adapter closed-loop replay summary marker missing from audit",
    )
    checks.check(
        adapter.get("closed_loop_local_rows") == runner_adapter.get("closed_loop_local_rows") == 6,
        "runner adapter closed-loop replay row count stale in audit",
    )
    checks.check(
        set(adapter.get("closed_loop_local_models", [])) == {"four_link", "slider_crank"},
        "runner adapter closed-loop replay models stale in audit",
    )
    checks.check(adapter.get("submission_ready") is False, "runner adapter overclaims submission ready")

    b6_local_evidence = audit.get("b6_four_example_local_evidence", {})
    checks.check(
        b6_local_evidence.get("schema")
        == b6_local_evidence_source.get("schema")
        == "b6-four-example-local-evidence-summary-v1",
        "B6 local-evidence schema not carried into audit",
    )
    checks.check(
        b6_local_evidence.get("status")
        == b6_local_evidence_source.get("status")
        == "four_example_local_evidence_runnable_source_policy_open",
        "B6 local-evidence status not carried into audit",
    )
    checks.check(
        b6_local_evidence.get("runner_passed") == b6_local_evidence_source.get("b6_local_evidence_runner_passed") is True,
        "B6 local-evidence runner pass marker missing",
    )
    checks.check(
        b6_local_evidence.get("local_rows") == b6_local_evidence_source.get("local_rows") == 12,
        "B6 local-evidence row count changed",
    )
    checks.check(
        set(b6_local_evidence.get("self_contained_examples", []))
        == {"single_pendulum", "double_pendulum", "four_link", "slider_crank"},
        "B6 self-contained examples changed",
    )
    checks.check(
        b6_local_evidence.get("replay_only_examples", []) == [],
        "B6 replay-only examples changed",
    )
    checks.check(
        b6_local_evidence.get("four_example_local_evidence_available") is True
        and b6_local_evidence.get("four_example_self_contained_simulation_ready") is True,
        "B6 four-example local/self-contained boundary changed",
    )
    checks.check(
        b6_local_evidence.get("source_policy_external_rows_closed") == 0
        and b6_local_evidence.get("source_policy_external_rows_total") == 40,
        "B6 source-policy row boundary changed",
    )
    checks.check(
        b6_local_evidence.get("global_proof_gap_closed") is True
        and b6_local_evidence.get("submission_ready") is False,
        "B6 proof/submission boundary changed",
    )
    closed_loop_audit = audit.get("b6_closed_loop_self_contained_extraction_audit", {})
    checks.check(
        closed_loop_audit.get("schema")
        == closed_loop_audit_source.get("schema")
        == "b6-closed-loop-self-contained-extraction-audit-v1",
        "B6 closed-loop extraction audit schema not carried into runner-centered audit",
    )
    checks.check(
        closed_loop_audit.get("status")
        == closed_loop_audit_source.get("status")
        == "closed_loop_self_contained_runner_candidate_ready_source_policy_open",
        "B6 closed-loop extraction audit status stale in runner-centered audit",
    )
    checks.check(
        closed_loop_audit.get("self_contained_runner_ready") is True,
        "B6 closed-loop extraction audit compact runner readiness missing in runner-centered audit",
    )
    checks.check(
        closed_loop_audit.get("target_source_file_count") == closed_loop_audit_source.get("target_source_file_count") == 2,
        "B6 closed-loop target source count stale in runner-centered audit",
    )
    checks.check(
        closed_loop_audit.get("target_symbol_count") == closed_loop_audit_source.get("target_symbol_count") >= 30,
        "B6 closed-loop target symbol count stale in runner-centered audit",
    )
    checks.check(
        closed_loop_audit.get("target_symbol_lines") == closed_loop_audit_source.get("target_symbol_lines"),
        "B6 closed-loop target symbol lines stale in runner-centered audit",
    )
    checks.check(
        closed_loop_audit.get("replay_only_closed_loop_examples", []) == []
        and closed_loop_audit.get("closed_loop_local_replay_rows") == 6,
        "B6 closed-loop replay boundary stale in runner-centered audit",
    )
    checks.check(
        closed_loop_audit.get("run_v047_invoked") is False
        and closed_loop_audit.get("run_v048_invoked") is False
        and closed_loop_audit.get("b4_opt_in_required_for_this_audit") is False,
        "B6 closed-loop audit execution boundary changed in runner-centered audit",
    )
    closed_loop_candidate = audit.get("closed_loop_local_runner_candidate", {})
    checks.check(
        closed_loop_candidate.get("schema") == closed_loop_candidate_source.get("schema"),
        "closed-loop candidate schema not carried into runner-centered audit",
    )
    checks.check(
        closed_loop_candidate.get("status")
        == closed_loop_candidate_source.get("status")
        == "closed_loop_local_runner_candidate_passed_compact",
        "closed-loop candidate status not carried into runner-centered audit",
    )
    checks.check(closed_loop_candidate.get("runner_passed") is True, "closed-loop candidate did not pass")
    checks.check(
        closed_loop_candidate.get("self_contained_simulation_runner") is True,
        "closed-loop candidate self-contained marker missing",
    )
    checks.check(
        closed_loop_candidate.get("candidate_python_file_count") == 10
        and 0 < closed_loop_candidate.get("candidate_python_line_count", 0) <= 2000
        and closed_loop_candidate.get("candidate_python_line_limit_ok") is True,
        "closed-loop candidate compact size not carried into runner-centered audit",
    )
    checks.check(
        closed_loop_candidate.get("imports_v046_v047_v048_or_v029") is False,
        "closed-loop candidate forbidden import marker set",
    )
    checks.check(
        closed_loop_candidate.get("closed_loop_local_rows") == 6
        and set(closed_loop_candidate.get("closed_loop_models", [])) == {"four_link", "slider_crank"},
        "closed-loop candidate rows/models stale",
    )
    checks.check(
        closed_loop_candidate.get("source_policy_external_rows_closed") == 0
        and closed_loop_candidate.get("source_policy_external_rows_total") == 40
        and closed_loop_candidate.get("source_policy_external_superiority_allowed") is False
        and closed_loop_candidate.get("submission_ready") is False,
        "closed-loop candidate source-policy/submission boundary changed",
    )

    matrix_scope = audit.get("paper_matrix_scope", {})
    checks.check(matrix_scope.get("row_count") == matrix.get("row_count") == 44, "matrix row count changed")
    checks.check(matrix_scope.get("raw_row_count") == matrix.get("raw_row_count") == 132, "raw row count changed")
    checks.check(matrix_scope.get("method_count") == matrix.get("method_count") == 11, "method count changed")
    checks.check(
        matrix_scope.get("common_reference_order_wins")
        == matrix_scope.get("common_reference_order_comparisons")
        == 40,
        "common-reference order win count changed",
    )
    checks.check(
        matrix_scope.get("common_reference_error_wins")
        == matrix_scope.get("common_reference_error_comparisons")
        == 40,
        "common-reference error win count changed",
    )
    checks.check(
        matrix_scope.get("source_policy_external_superiority_allowed") is False
        and matrix_scope.get("paper_direct_error_superiority_allowed") is False,
        "external superiority boundary changed",
    )
    checks.check(matrix_scope.get("global_comparison_policy_passed") is True, "global policy not passed")

    source_scope = audit.get("source_policy_scope", {})
    checks.check(
        source_scope.get("local_dynamic_order_closed_examples")
        == dashboard.get("local_dynamic_order_closed_examples")
        == 2,
        "local dynamic-order count changed",
    )
    checks.check(
        source_scope.get("accepted_source_policy_dynamic_order_examples")
        == dashboard.get("accepted_source_policy_dynamic_order_examples")
        == 0,
        "source-policy dynamic-order example count changed",
    )
    checks.check(
        source_scope.get("source_policy_closed_rows")
        == result_checks.get("source_policy_apples_to_apples_external_rows")
        == 0,
        "source-policy closed rows changed",
    )
    checks.check(
        source_scope.get("source_policy_total_rows")
        == result_checks.get("source_policy_apples_to_apples_external_total_rows")
        == 40,
        "source-policy total rows changed",
    )
    checks.check(
        proof.get("closure_state", {}).get("proof_gap_closed") is True,
        "proof gap direct closure missing",
    )

    existing_sources = audit.get("existing_runner_sources", [])
    expected_paths = {
        "../v048_cross_paper_same_test_benchmarks/run_coarse_four_example_order.py",
        "../v048_cross_paper_same_test_benchmarks/run_v048.py",
        "../v048_cross_paper_same_test_benchmarks/closed_loop_fullva_dynamic_residual.py",
        "../v048_cross_paper_same_test_benchmarks/build_closed_loop_true_dynamic_strict_common_reference.py",
        "../v048_cross_paper_same_test_benchmarks/tfe_source_pendulum_model.py",
    }
    checks.check({item.get("path") for item in existing_sources} == expected_paths, "runner source set changed")
    total_lines = 0
    for item in existing_sources:
        path = resolve(str(item.get("path")))
        checks.check(path.exists(), f"runner source missing: {item.get('path')}")
        if path.exists():
            count = line_count(path)
            total_lines += count
            checks.check(item.get("python_lines") == count, f"runner source line count stale: {item.get('path')}")
    checks.check(
        audit.get("existing_runner_source_total_python_lines") == total_lines,
        "runner source total line count stale",
    )
    checks.check(total_lines > 2000, "existing runner source is unexpectedly already below reviewer limit")

    boundary = audit.get("existing_runner_boundary", {})
    checks.check(boundary.get("can_be_primary_submission_code_without_extraction") is False, "runner boundary overclaimed")
    checks.check(boundary.get("depends_on_v048_run_v048") is True, "v048 dependency marker missing")
    checks.check(boundary.get("depends_on_external_sbel_reproducibility") is True, "external SBEL dependency marker missing")
    checks.check(boundary.get("contains_replay_and_audit_logic_mixed_with_runners") is True, "mixed runner/audit marker missing")

    requirements = {item.get("id"): item for item in audit.get("requirements", [])}
    checks.check(requirements.get("R1_compact_size", {}).get("status") == "satisfied", "compact-size requirement should be satisfied")
    checks.check(
        requirements.get("R2_runner_centered_generation", {}).get("status")
        == "partial_compact_closed_loop_candidate_passed",
        "runner-centered generation requirement should record compact closed-loop candidate",
    )
    for req_id in ["R3_source_policy_external_rows"]:
        checks.check(requirements.get(req_id, {}).get("status") == "open", f"{req_id} unexpectedly closed")
    checks.check(
        requirements.get("R4_proof_boundary", {}).get("status") == "satisfied",
        "R4 proof boundary should be satisfied after direct proof closure",
    )
    checks.check(requirements.get("R5_research_audit_tree_not_primary_code", {}).get("status") == "satisfied", "audit-tree boundary should be satisfied")
    code_checks = review.get("code_hygiene_checks", {})
    expected_r5_evidence = (
        f"combined_python_line_count={code_checks.get('combined_python_line_count')}, "
        f"primary_allowed={code_checks.get('research_audit_repo_primary_submission_allowed')}"
    )
    checks.check(
        requirements.get("R5_research_audit_tree_not_primary_code", {}).get("evidence")
        == expected_r5_evidence,
        "audit-tree Python inventory evidence stale",
    )

    for token in [
        "Status: **local_runner_centered_candidate_ready_source_policy_package_open**.",
        "Runner-centered package ready: `False`.",
        "Local accepted-row runner-centered candidate ready: `True`.",
        "Full source-policy runner package ready: `False`.",
        "Python files/lines: `1/",
        "Replay-only: `True`; runner-centered: `False`.",
        "Runner adapter present: `True`; self-contained simulation runner: `False`.",
        "Runner adapter closed-loop replay outputs: `True`.",
        "B6 final prose ready under narrowed claim/full source-policy prose ready: `True/False`.",
        "B6 four-example local evidence runner: `True`; rows `12`;",
        "Closed-loop local runner candidate: `closed_loop_local_runner_candidate_passed_compact`; rows `6`; compact `True`.",
        "B6 closed-loop extraction audit: `closed_loop_self_contained_runner_candidate_ready_source_policy_open`;",
        "Source-policy rows closed: `0/40`.",
        "Source-policy execution allowed now/invoked/exact opt-in required: `False/False/True`.",
        "Safe action ids: `['rebuild_read_only_audit_chain', 'rerun_read_only_validators', 'keep_narrowed_archive_provenance_only', 'monitor_reopen_conditions']`; opt-in action ids: `['authorized_b4_ra_hi_source_policy_execution']`.",
        "Safe/opt-in action object counts: `4/1`.",
        "Runner package blocker required-to-close by id: `{'OC4':",
        "Runner package blocker safe next actions by id: `{'OC4':",
        "Runner package blocker opt-in required actions by id: `{'OC4':",
        "Source-policy handoff: `source_policy_execution_handoff_ready_not_authorized_not_run`; authorized/not-run `False/True`; driver `run_b4_source_policy_after_opt_in.sh`.",
        "Row provenance preflight/promotion-ready: `40/40/0`.",
        "Existing v048 runner candidates total `",
        "`R2_runner_centered_generation`",
        "`R3_source_policy_external_rows`",
        "`R4_proof_boundary`",
        expected_r5_evidence,
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("cmame runner-centered reproducibility audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("cmame runner-centered reproducibility audit validation: PASS")
    print(f"runner_centered_package_ready={audit.get('runner_centered_package_ready')}")
    print(
        "candidate_python="
        f"{current.get('python_file_count')}/{current.get('python_line_count')}"
    )
    print(f"existing_runner_source_lines={audit.get('existing_runner_source_total_python_lines')}")
    print(f"b6_local_evidence_rows={b6_local_evidence.get('local_rows')}")
    print(
        "source_policy_closed="
        f"{source_scope.get('source_policy_closed_rows')}/{source_scope.get('source_policy_total_rows')}"
    )
    print(
        "source_policy_handoff="
        f"{handoff.get('status')}/{handoff.get('execution_authorized')}/"
        f"{handoff.get('commands_not_run_by_handoff')}"
    )
    print(f"source_policy_execution_allowed_now={audit.get('source_policy_execution_allowed_now')}")
    print(f"source_policy_execution_invoked={audit.get('source_policy_execution_invoked')}")
    print(
        "row_provenance="
        f"{audit.get('full_source_policy_row_provenance_preflight')}/"
        f"{audit.get('full_source_policy_row_provenance_promotion_ready_rows')}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
