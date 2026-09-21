#!/usr/bin/env python3
"""Validate the objective-level completion audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
V048 = ROOT.parent / "numerics" / "v048_cross_paper_same_test_benchmarks"
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


def code_inventory(path: Path) -> dict[str, object]:
    files = sorted(path.glob("*.py"))
    line_counts = {item.name: len(read_text(item).splitlines()) for item in files}
    return {
        "file_count": len(files),
        "line_count": sum(line_counts.values()),
    }


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(PAPER / "OBJECTIVE_COMPLETION_AUDIT.json")
        audit_md = read_text(PAPER / "OBJECTIVE_COMPLETION_AUDIT.md")
        matrix = read_json(PAPER / "PAPER_NUMERICAL_RESULT_MATRIX.json")
        traceability = read_json(PAPER / "RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.json")
        proof = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
        proof_claim_traceability = read_json(PAPER / "PROOF_CLAIM_TRACEABILITY_AUDIT.json")
        strict_proof_policy = read_json(PAPER / "CMAME_STRICT_PROOF_POLICY_RECONCILIATION_AUDIT.json")
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
        expected_command_traceability = b4_execution_handoff.get(
            "command_row_traceability", {}
        ).get("summary", {})
        full_source_policy_row_provenance = read_json(PAPER / "FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.json")
        oc6_source_equivalent_reopen = read_json(PAPER / "OC6_SOURCE_EQUIVALENT_REOPEN_READINESS_AUDIT_20260620.json")
        full_source_runner_gap = read_json(PAPER / "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json")
        expected_full_archive_terminal_reopen_conditions = {
            "tfe2026_original_pendulum": "new_public_or_source_code_equivalent_tfe_implementation_artifact",
            "vp2024_velocity_partitioning": "new_distinct_public_vp2024_velocity_partitioning_code_path",
        }
        source_policy = read_json(PAPER / "EXTERNAL_SOURCE_POLICY_CLOSURE_MANIFEST.json")
        ra_hi_closeout = read_json(PAPER / "RA_HI_SOURCE_POLICY_CLOSEOUT_CHECKLIST.json")
        ra_hi_promotion_matrix = read_json(PAPER / "RA_HI_SOURCE_POLICY_PROMOTION_BLOCKER_MATRIX.json")
        b2 = read_json(PAPER / "B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.json")
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
        blocker = read_json(PAPER / "CMAME_BLOCKER_CLOSURE_GATE.json")
    except Exception as exc:  # noqa: BLE001
        print(f"objective completion audit validation: FAIL\n- {exc}")
        return 1

    summary = audit.get("summary", {})
    requirements = audit.get("requirements", [])
    by_id = {item.get("id"): item for item in requirements}
    open_blockers = audit.get("open_blockers", [])
    blockers_alias = audit.get("blockers", [])
    open_blocker_ids = audit.get("open_blocker_ids", [])
    open_blockers_by_id = {item.get("id"): item for item in open_blockers}
    blockers_by_id = audit.get("blockers_by_id", {})
    blocker_status_by_id = audit.get("blocker_status_by_id", {})
    blocker_open_by_id = audit.get("blocker_open_by_id", {})
    blocker_closure_decision_by_id = audit.get("blocker_closure_decision_by_id", {})
    blocker_closure_allowed_by_id = audit.get("blocker_closure_allowed_by_id", {})
    blocker_source_alias_by_id = audit.get("blocker_source_alias_by_id", {})
    blocker_next_actions_by_id = audit.get("blocker_next_actions_by_id", {})
    blocker_required_to_close_by_id = audit.get("blocker_required_to_close_by_id", {})
    blocker_safe_next_actions_by_id = audit.get("blocker_safe_next_actions_by_id", {})
    blocker_opt_in_required_actions_by_id = audit.get(
        "blocker_opt_in_required_actions_by_id", {}
    )
    safe_actions_without_b4_opt_in = audit.get("safe_actions_without_b4_opt_in", [])
    opt_in_required_actions = audit.get("opt_in_required_actions", [])
    tfe_execution_preflight = tfe_dae_gap.get("source_policy_execution_preflight", {})
    oc6_observed = by_id.get("OC6", {}).get("observed", {})
    expected_b2_demoted_suite_counts = {
        "hi2022_half_implicit": 3,
        "ra2021_absolute_coordinate": 5,
        "tfe2026_original_pendulum": 4,
        "vp2024_velocity_partitioning": 3,
    }
    transition_sensitivity = tfe_brown_mcphee.get(
        "brown_mcphee_transition_velocity_sensitivity", {}
    )
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
    paper_code = code_inventory(PAPER)
    v048_code = code_inventory(V048)
    combined_python_line_count = int(paper_code["line_count"]) + int(v048_code["line_count"])
    proof_writing_card = proof_claim_traceability.get("proof_writing_boundary_card", {})
    reference_correspondence = strict_proof_policy.get("reference_correspondence_discipline", {})
    reference_main_features = reference_correspondence.get("main_features", {})
    reference_flat_features = reference_correspondence.get("flat_features", {})
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

    checks.check(audit.get("schema") == "objective-completion-audit-v1", "schema changed")
    checks.check(audit.get("status") == "not_complete_submission_standard_open", "status changed")
    checks.check(audit.get("read_only") is True, "audit should be read-only")
    checks.check(audit.get("objective_complete") is False, "objective must not be marked complete")
    checks.check(audit.get("submission_ready") is False, "audit must not mark submission ready")
    checks.check(audit.get("blocking_open_count") == 3, "top-level blocking open count changed")
    checks.check(
        audit.get("blocking_open") == audit.get("blocking_open_count") == 3,
        "top-level blocking_open alias changed",
    )
    checks.check(
        audit.get("blocking_requirement_ids") == ["OC4", "OC6", "OC12"],
        "top-level blocking requirement ids changed",
    )
    checks.check(
        audit.get("blocking_ids") == audit.get("blocking_requirement_ids") == ["OC4", "OC6", "OC12"],
        "top-level blocking_ids alias changed",
    )
    checks.check(
        audit.get("open_blocker_ids")
        == summary.get("open_blocker_ids")
        == audit.get("blocking_ids")
        == ["OC4", "OC6", "OC12"],
        "top-level open_blocker_ids alias changed",
    )
    checks.check(
        audit.get("source_policy_execution_invoked") is False
        and summary.get("source_policy_execution_invoked") is False
        and b4_guarded_refusal.get("source_policy_execution_invoked") is False,
        "objective audit should not record source-policy execution",
    )
    checks.check(
        audit.get("source_policy_execution_allowed_now") is False
        and summary.get("source_policy_execution_allowed_now") is False
        and full_source_runner_gap.get("source_policy_execution_allowed_now") is False,
        "objective audit should not allow source-policy execution",
    )
    checks.check(
        audit.get("exact_b4_opt_in_required_for_execution") is True
        and summary.get("exact_b4_opt_in_required_for_execution") is True
        and full_source_runner_gap.get("exact_b4_opt_in_required_for_execution") is True,
        "objective audit lost exact B4 opt-in requirement",
    )
    checks.check(
        audit.get("safe_action_ids")
        == summary.get("safe_action_ids")
        == full_source_runner_gap.get("safe_action_ids")
        == EXPECTED_SAFE_ACTION_IDS,
        "objective audit safe action ids changed",
    )
    checks.check(
        audit.get("next_safe_action_ids")
        == summary.get("next_safe_action_ids")
        == EXPECTED_SAFE_ACTION_IDS,
        "objective audit next safe action ids changed",
    )
    checks.check(
        audit.get("opt_in_action_ids")
        == summary.get("opt_in_action_ids")
        == full_source_runner_gap.get("opt_in_action_ids")
        == EXPECTED_OPT_IN_ACTION_IDS,
        "objective audit opt-in action ids changed",
    )
    checks.check(
        safe_actions_without_b4_opt_in
        == full_source_runner_gap.get("safe_next_actions_without_b4_opt_in")
        and [item.get("id") for item in safe_actions_without_b4_opt_in]
        == EXPECTED_SAFE_ACTION_IDS
        and all(item.get("allowed_without_b4_opt_in") is True for item in safe_actions_without_b4_opt_in),
        "objective audit safe action objects changed",
    )
    checks.check(
        opt_in_required_actions
        == full_source_runner_gap.get("opt_in_required_actions")
        and [item.get("id") for item in opt_in_required_actions]
        == EXPECTED_OPT_IN_ACTION_IDS
        and all(item.get("allowed_without_b4_opt_in") is False for item in opt_in_required_actions),
        "objective audit opt-in action objects changed",
    )
    checks.check(
        summary.get("safe_actions_without_b4_opt_in_count") == len(EXPECTED_SAFE_ACTION_IDS)
        and summary.get("opt_in_required_actions_count") == len(EXPECTED_OPT_IN_ACTION_IDS),
        "objective audit safe/opt-in action object counts changed",
    )
    checks.check(
        audit.get("required_user_approval_statement")
        == summary.get("required_user_approval_statement")
        == EXPECTED_APPROVAL_STATEMENT,
        "objective audit required approval statement changed",
    )
    checks.check(
        audit.get("guarded_execution_driver")
        == summary.get("guarded_execution_driver")
        == "run_b4_source_policy_after_opt_in.sh",
        "objective audit guarded driver changed",
    )
    checks.check(
        audit.get("b4_guarded_driver_refusal_boundary_audit_20260621")
        == "True/True/2/0/13/False/False"
        and audit.get("b4_guarded_driver_refusal_boundary_status")
        == b4_guarded_refusal.get("status")
        == "guarded_driver_refusal_boundary_static_proved_not_executed"
        and audit.get("b4_guarded_driver_refusal_boundary_marker")
        == b4_guarded_refusal.get("marker")
        == "b4_guarded_driver_refusal_boundary_audit_20260621=True/True/2/0/13/False/False",
        "objective audit B4 guarded refusal boundary alias changed",
    )
    checks.check(
        audit.get("run_v047_invoked") is False and summary.get("run_v047_invoked") is False,
        "objective audit should not record run_v047 invocation",
    )
    checks.check(
        audit.get("heavy_numerical_run_invoked") is False
        and summary.get("heavy_numerical_run_invoked") is False,
        "objective audit should not record heavy numerical execution",
    )
    checks.check(
        audit.get("v048_runner_invoked") is False and summary.get("v048_runner_invoked") is False,
        "objective audit should not record v048 runner invocation",
    )
    checks.check(len(open_blockers) == 3, "top-level open blocker list changed")
    checks.check(
        blockers_alias == open_blockers,
        "top-level blockers alias must mirror open_blockers",
    )
    checks.check(
        set(open_blockers_by_id) == {"OC4", "OC6", "OC12"},
        "top-level open blocker ids changed",
    )
    checks.check(
        open_blocker_ids == list(open_blockers_by_id) == ["OC4", "OC6", "OC12"],
        "top-level open blocker id list stale",
    )
    checks.check(
        blockers_by_id == open_blockers_by_id,
        "machine-readable blockers_by_id must mirror open_blockers",
    )
    checks.check(
        blocker_status_by_id == {req_id: by_id.get(req_id, {}).get("status") for req_id in ["OC4", "OC6", "OC12"]},
        "machine-readable blocker status index stale",
    )
    checks.check(
        blocker_next_actions_by_id
        == {req_id: by_id.get(req_id, {}).get("next_to_close") for req_id in ["OC4", "OC6", "OC12"]},
        "machine-readable blocker next-action index stale",
    )
    for req_id in ["OC4", "OC6", "OC12"]:
        checks.check(
            blockers_by_id.get(req_id, {}).get("observed")
            == by_id.get(req_id, {}).get("observed"),
            f"{req_id} machine-readable blocker observed payload stale",
        )
        checks.check(
            blockers_by_id.get(req_id, {}).get("required_to_close")
            == blocker_required_to_close_by_id.get(req_id),
            f"{req_id} blocker required-to-close payload stale",
        )
        checks.check(
            blockers_by_id.get(req_id, {}).get("safe_next_actions")
            == blocker_safe_next_actions_by_id.get(req_id),
            f"{req_id} blocker safe action payload stale",
        )
        checks.check(
            blockers_by_id.get(req_id, {}).get("opt_in_required_actions")
            == blocker_opt_in_required_actions_by_id.get(req_id),
            f"{req_id} blocker opt-in action payload stale",
        )
    checks.check(
        set(blocker_required_to_close_by_id)
        == set(blocker_safe_next_actions_by_id)
        == set(blocker_opt_in_required_actions_by_id)
        == {"OC4", "OC6", "OC12"},
        "blocker closure/action index keys changed",
    )
    expected_blocker_open_by_id = {
        "OC4": full_source_policy_row_provenance.get("oc4_blocker_open"),
        "OC6": oc6_source_equivalent_reopen.get("oc6_blocker_open"),
        "OC12": full_source_runner_gap.get("oc12_blocker_open"),
    }
    expected_blocker_closure_decision_by_id = {
        "OC4": full_source_policy_row_provenance.get("oc4_closure_decision"),
        "OC6": oc6_source_equivalent_reopen.get("oc6_closure_decision"),
        "OC12": full_source_runner_gap.get("oc12_closure_decision"),
    }
    expected_blocker_closure_allowed_by_id = {
        "OC4": full_source_policy_row_provenance.get("oc4_closure_allowed_now"),
        "OC6": oc6_source_equivalent_reopen.get("oc6_closure_allowed_now"),
        "OC12": full_source_runner_gap.get("oc12_closure_allowed_now"),
    }
    expected_blocker_source_alias_by_id = {
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
    checks.check(
        blocker_status_by_id == {"OC12": "partial", "OC4": "open", "OC6": "partial"},
        "blocker status map changed",
    )
    checks.check(
        blocker_open_by_id == expected_blocker_open_by_id,
        "blocker open map drifted from source audits",
    )
    checks.check(
        blocker_closure_decision_by_id == expected_blocker_closure_decision_by_id,
        "blocker closure-decision map drifted from source audits",
    )
    checks.check(
        blocker_closure_allowed_by_id == expected_blocker_closure_allowed_by_id,
        "blocker closure-allowed map drifted from source audits",
    )
    checks.check(
        blocker_source_alias_by_id == expected_blocker_source_alias_by_id,
        "blocker source alias map drifted from source audits",
    )
    checks.check(
        audit.get("oc4_blocker_id") == "OC4"
        and audit.get("oc4_blocker_status") == "open"
        and audit.get("oc4_blocker_open") is True
        and audit.get("oc4_closure_decision")
        == "remain_open_ready_for_authorized_execution_not_executed_not_promoted"
        and audit.get("oc4_closure_allowed_now") is False
        and audit.get("oc4_ready_commands_mapped_rows") == "13/20"
        and audit.get("oc4_traceability_unique_traced_declared_mismatch") == "20/32/32/0",
        "OC4 direct aliases changed",
    )
    checks.check(
        audit.get("oc6_blocker_id") == "OC6"
        and audit.get("oc6_blocker_status") == "partial"
        and audit.get("oc6_blocker_open") is True
        and audit.get("oc6_closure_decision")
        == "remain_open_no_positive_source_equivalent_artifact"
        and audit.get("oc6_closure_allowed_now") is False
        and audit.get("oc6_reopen_condition")
        == "suite_specific_source_equivalent_reopen_conditions"
        and audit.get("oc6_latest_external_probe_boundary_marker")
        == "2026-06-21/9/0/0/4/False/False",
        "OC6 direct aliases changed",
    )
    checks.check(
        audit.get("oc12_blocker_id") == "OC12"
        and audit.get("oc12_blocker_status") == "partial"
        and audit.get("oc12_blocker_open") is True
        and audit.get("oc12_closure_decision")
        == "remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready"
        and audit.get("oc12_closure_allowed_now") is False
        and audit.get("oc12_current_archive_usable_as_full_source_policy_runner_archive") is False
        and audit.get("oc12_safe_current_use")
        == "narrowed_claim_replay_and_audit_provenance_only"
        and audit.get("oc12_primary_submission_package_allowed") is False,
        "OC12 direct aliases changed",
    )
    source_archive_required_to_close = (
        full_source_runner_gap.get("archive_blocker_required_to_close_by_id")
        or full_source_runner_gap.get("blocker_required_to_close_by_id")
    )
    source_archive_safe_next_actions = (
        full_source_runner_gap.get("archive_blocker_safe_next_actions_by_id")
        or full_source_runner_gap.get("blocker_safe_next_actions_by_id")
    )
    source_archive_opt_in_actions = (
        full_source_runner_gap.get("archive_blocker_opt_in_required_actions_by_id")
        or full_source_runner_gap.get("blocker_opt_in_required_actions_by_id")
    )
    checks.check(
        blocker_required_to_close_by_id == source_archive_required_to_close,
        "objective required-to-close map drifted from full-source archive gap audit",
    )
    checks.check(
        blocker_safe_next_actions_by_id == source_archive_safe_next_actions,
        "objective safe-next-action map drifted from full-source archive gap audit",
    )
    checks.check(
        blocker_opt_in_required_actions_by_id == source_archive_opt_in_actions,
        "objective opt-in action map drifted from full-source archive gap audit",
    )
    oc4_close = blocker_required_to_close_by_id.get("OC4", {})
    oc4_auth_route = oc4_close.get("authorized_ra_hi_closeout_route", {})
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
        oc4_close.get("current_source_policy_closed_ratio") == "0/40"
        and oc4_close.get("source_policy_rows_closed") == 0
        and oc4_close.get("source_policy_rows_total") == 40
        and oc4_auth_route.get("requires_exact_b4_opt_in") is True
        and oc4_auth_route.get("execution_allowed_now") is False
        and oc4_auth_route.get("execution_invoked") is False
        and oc4_auth_route.get("guarded_execution_driver")
        == "run_b4_source_policy_after_opt_in.sh"
        and oc4_auth_route.get("required_user_approval_statement")
        == EXPECTED_APPROVAL_STATEMENT
        and oc4_auth_route.get("opt_in_required_command_count") == 13
        and oc4_auth_route.get("opt_in_required_mapped_external_rows") == 20
        and oc4_auth_route.get("expected_output_schema_command_traceability")
        == expected_oc4_schema_traceability
        and oc4_auth_route.get("expected_output_schema_command_traceability_tuple")
        == "13/13/8/5/13/8/False/False",
        "OC4 required-to-close boundary changed",
    )
    oc4_refusal_route = oc4_auth_route.get("guarded_driver_refusal_boundary_20260621", {})
    checks.check(
        oc4_refusal_route.get("status")
        == b4_guarded_refusal.get("status")
        == "guarded_driver_refusal_boundary_static_proved_not_executed"
        and oc4_refusal_route.get("no_opt_in_refusal_proved_static") is True
        and oc4_refusal_route.get("wrong_approval_refusal_proved_static") is True
        and oc4_refusal_route.get("refusal_exit_code") == 2
        and oc4_refusal_route.get("pre_guard_command_count") == 0
        and oc4_refusal_route.get("refusal_branch_source_policy_command_count") == 0
        and oc4_refusal_route.get("post_guard_source_policy_command_count") == 13
        and oc4_refusal_route.get("driver_invoked_by_audit") is False
        and oc4_refusal_route.get("source_policy_execution_invoked") is False
        and oc4_refusal_route.get("submission_ready") is False
        and oc4_refusal_route.get("marker")
        == "b4_guarded_driver_refusal_boundary_audit_20260621=True/True/2/0/13/False/False",
        "OC4 required-to-close guarded refusal boundary changed",
    )
    oc6_close = blocker_required_to_close_by_id.get("OC6", {})
    oc6_probe = oc6_close.get("latest_external_probe", {})
    oc6_external_required = oc6_close.get("external_source_artifact_recheck_20260621", {})
    oc6_publisher_required = oc6_close.get("publisher_artifact_availability_20260621", {})
    checks.check(
        oc6_close.get("tfe_runner_closed") is False
        and oc6_close.get("source_policy_rows_completed") == 0
        and oc6_close.get("contract_preflight_status")
        == "contract_entrypoints_callable_candidate_backed_source_policy_open"
        and oc6_close.get("candidate_backed_contract_count") == 3
        and oc6_close.get("entrypoint_count") == 3
        and oc6_close.get("callable_contract_count") == 3
        and oc6_close.get("effective_execution_block_count") == 4
        and oc6_close.get("reopen_condition")
        == "new_public_or_source_code_equivalent_tfe_implementation_artifact"
        and oc6_probe.get("date") == "2026-06-21"
        and oc6_probe.get("probe_count") == 9
        and oc6_probe.get("positive_public_code_artifact_rows") == 0
        and oc6_probe.get("source_policy_rows_closed") == 0
        and oc6_probe.get("access_limited_count") == 4
        and oc6_probe.get("global_absence_proved") is False
        and oc6_probe.get("reopen_triggered") is False,
        "OC6 required-to-close boundary changed",
    )
    checks.check(
        oc6_external_required.get("date") == "2026-06-21"
        and oc6_external_required.get("query_count") == 10
        and oc6_external_required.get("positive_public_code_artifact_rows") == 0
        and oc6_external_required.get("source_code_equivalent_artifact_rows") == 0
        and oc6_external_required.get("source_policy_rows_closed_by_recheck") == 0
        and oc6_external_required.get("source_policy_reopen_triggered") is False
        and oc6_external_required.get("global_absence_proved") is False
        and oc6_external_required.get("submission_ready") is False,
        "OC6 external source-artifact recheck missing from required-to-close boundary",
    )
    checks.check(
        oc6_publisher_required.get("date") == "2026-06-21"
        and oc6_publisher_required.get("official_article_checked") is True
        and oc6_publisher_required.get("source_artifact_signal_count") == 0
        and oc6_publisher_required.get("positive_public_code_artifact_rows") == 0
        and oc6_publisher_required.get("source_code_equivalent_artifact_rows") == 0
        and oc6_publisher_required.get("source_policy_rows_closed_by_publisher_audit") == 0
        and oc6_publisher_required.get("source_policy_reopen_triggered") is False
        and oc6_publisher_required.get("global_absence_proved") is False
        and oc6_publisher_required.get("submission_ready") is False,
        "OC6 publisher artifact availability missing from required-to-close boundary",
    )
    oc12_close = blocker_required_to_close_by_id.get("OC12", {})
    checks.check(
        oc12_close.get("upstream_blockers") == ["OC4", "OC6"]
        and oc12_close.get("current_archive_usable_as_full_source_policy_runner_archive")
        is False
        and oc12_close.get("full_source_policy_runner_package_ready") is False
        and oc12_close.get("narrowed_repro_code_archive_ready") is True
        and oc12_close.get("narrowed_repro_code_archive_submission_ready") is False
        and oc12_close.get("source_policy_closed_ratio") == "0/40"
        and oc12_close.get("remaining_source_policy_rows_to_close") == 40
        and oc12_close.get("safe_current_archive_use")
        == "narrowed_claim_replay_and_audit_provenance_only",
        "OC12 required-to-close boundary changed",
    )
    checks.check(
        all(
            blocker_safe_next_actions_by_id.get(req_id) == safe_actions_without_b4_opt_in
            for req_id in ["OC4", "OC6", "OC12"]
        )
        and blocker_opt_in_required_actions_by_id.get("OC4") == opt_in_required_actions
        and blocker_opt_in_required_actions_by_id.get("OC6") == []
        and blocker_opt_in_required_actions_by_id.get("OC12") == opt_in_required_actions,
        "blocker action boundary payloads changed",
    )
    checks.check(audit.get("source_policy_closed") is False, "top-level source policy should remain open")
    checks.check(
        audit.get("source_policy_closed_rows")
        == summary.get("source_policy_closed_rows")
        == full_source_policy_row_provenance.get("source_policy_rows_closed")
        == 0
        and audit.get("source_policy_total_rows")
        == summary.get("source_policy_total_rows")
        == full_source_policy_row_provenance.get("source_policy_rows_total")
        == 40
        and audit.get("source_policy_closed_ratio")
        == summary.get("source_policy_closed_ratio")
        == full_source_policy_row_provenance.get("source_policy_closed_ratio")
        == "0/40",
        "top-level source-policy row aliases changed",
    )
    checks.check(audit.get("b2_source_policy_closed") is False, "top-level B2 source policy should remain open")
    checks.check(
        audit.get("b2_source_policy_rows_closed") is False,
        "top-level B2 source-policy rows should remain open",
    )
    checks.check(
        audit.get("b2_active_suites_closed") is True,
        "top-level B2 active suites should be closed by demotion",
    )
    checks.check(
        audit.get("b2_active_suites_closed_by_demotion") is True,
        "top-level B2 demotion closure should remain true",
    )
    checks.check(audit.get("tfe_runner_closed") is False, "top-level TFE runner should remain open")
    checks.check(audit.get("minimal_code_ready") is False, "top-level minimal code package should remain open")
    checks.check(
        audit.get("minimal_reproducible_submission_code_ready") is False
        and audit.get("minimal_reproducible_submission_code_ready")
        == audit.get("minimal_code_ready")
        == summary.get("minimal_reproducible_submission_code_ready")
        == summary.get("minimal_code_ready")
        == by_id.get("OC12", {}).get("observed", {}).get(
            "minimal_submission_code_dependency_boundary", {}
        ).get("minimal_reproducible_submission_code_ready"),
        "minimal reproducible submission code readiness boundary changed",
    )
    completion_decision = audit.get("completion_decision", {})
    checks.check(
        completion_decision.get("can_mark_goal_complete") is False,
        "completion decision must not allow goal completion",
    )
    checks.check(
        completion_decision.get("blocking_requirement_ids") == ["OC4", "OC6", "OC12"],
        "completion decision blocker ids changed",
    )
    checks.check(
        "validator_pass_means" in completion_decision
        and "does not prove the full paper objective" in completion_decision.get("validator_pass_means", ""),
        "completion decision should explain validator PASS boundary",
    )
    checks.check(summary.get("requirement_count") == len(requirements) == 12, "requirement count changed")
    checks.check(summary.get("satisfied_count") == 9, "satisfied count changed")
    checks.check(summary.get("partial_count") == 2, "partial count changed")
    checks.check(summary.get("open_count") == 1, "open count changed")
    checks.check(summary.get("blocking_open_count") == 3, "blocking open count changed")

    checks.check(by_id.get("OC1", {}).get("status") == "satisfied", "core result matrix should be satisfied")
    checks.check(by_id.get("OC2", {}).get("status") == "satisfied", "traceability should be satisfied")
    checks.check(by_id.get("OC3", {}).get("status") == "satisfied", "common-reference boundary should be satisfied")
    checks.check(by_id.get("OC7", {}).get("status") == "satisfied", "proof boundary should be satisfied")
    checks.check(
        by_id.get("OC7", {}).get("blocking_for_goal_completion") is False,
        "OC7 should not block completion after direct proof closure",
    )
    oc7_observed = by_id.get("OC7", {}).get("observed", {})
    checks.check(
        oc7_observed.get("direct_pc2_proof_gap_closed")
        == oc7_observed.get("proof_gap_closed")
        is True
        and oc7_observed.get("proof_gap_closed_scope")
        == "direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open"
        and "schema-compatible shorthand for direct_pc2_proof_gap_closed"
        in oc7_observed.get("proof_gap_closed_reading_rule", "")
        and oc7_observed.get("symbolic_primitive_route_open_dynamic_rows")
        == oc7_observed.get("open_dynamic_rows")
        == 36
        and oc7_observed.get("open_dynamic_rows_scope")
        == "symbolic_primitive_certificate_route_not_active_direct_pc2",
        "OC7 proof closure/open-row fields must be scoped to direct PC2 and primitive route",
    )
    checks.check(by_id.get("OC9", {}).get("status") == "satisfied", "submission-integrity boundary should be satisfied")
    checks.check(by_id.get("OC11", {}).get("status") == "satisfied", "review agent presence should be satisfied")
    for req_id in ["OC4"]:
        checks.check(by_id.get(req_id, {}).get("status") == "open", f"{req_id} should remain open")
        checks.check(
            by_id.get(req_id, {}).get("blocking_for_goal_completion") is True,
            f"{req_id} should block completion",
        )
    oc4_observed = by_id.get("OC4", {}).get("observed", {})
    checks.check(
        "RA_HI_SOURCE_POLICY_CLOSEOUT_CHECKLIST.json" in by_id.get("OC4", {}).get("evidence", []),
        "OC4 must cite RA/HI source-policy closeout checklist",
    )
    checks.check(
        "RA_HI_SOURCE_POLICY_PROMOTION_BLOCKER_MATRIX.json" in by_id.get("OC4", {}).get("evidence", []),
        "OC4 must cite RA/HI source-policy promotion blocker matrix",
    )
    checks.check(
        "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json" in by_id.get("OC4", {}).get("evidence", []),
        "OC4 must cite B4 source-policy execution handoff package",
    )
    checks.check(
        "B4_GUARDED_DRIVER_REFUSAL_BOUNDARY_AUDIT_20260621.json"
        in by_id.get("OC4", {}).get("evidence", []),
        "OC4 must cite B4 guarded-driver refusal boundary audit",
    )
    checks.check(
        summary.get("ra_hi_closeout_status")
        == oc4_observed.get("ra_hi_closeout_status")
        == ra_hi_closeout.get("status")
        == "ready_for_authorized_execution_closeout_not_executed_not_promoted",
        "RA/HI closeout status not propagated into objective audit",
    )
    checks.check(
        summary.get("ra_hi_closeout_source_policy_rows_total")
        == oc4_observed.get("ra_hi_closeout_source_policy_rows_total")
        == ra_hi_closeout.get("coverage", {}).get("source_policy_rows_total")
        == 20,
        "RA/HI closeout total rows changed in objective audit",
    )
    checks.check(
        summary.get("ra_hi_closeout_ra_rows")
        == oc4_observed.get("ra_hi_closeout_ra_rows")
        == 12
        and summary.get("ra_hi_closeout_hi_rows")
        == oc4_observed.get("ra_hi_closeout_hi_rows")
        == 8,
        "RA/HI closeout suite row counts changed in objective audit",
    )
    checks.check(
        summary.get("ra_hi_closeout_ready_command_count")
        == oc4_observed.get("ra_hi_closeout_ready_command_count")
        == 13
        and summary.get("ra_hi_closeout_ready_command_mapped_rows")
        == oc4_observed.get("ra_hi_closeout_ready_command_mapped_rows")
        == 20,
        "RA/HI closeout command mapping changed in objective audit",
    )
    checks.check(
        summary.get("ra_hi_closeout_source_policy_rows_promoted")
        == oc4_observed.get("ra_hi_closeout_source_policy_rows_promoted")
        == 0
        and summary.get("ra_hi_closeout_source_policy_rows_completed")
        == oc4_observed.get("ra_hi_closeout_source_policy_rows_completed")
        == 0
        and summary.get("ra_hi_closeout_external_superiority_ready_rows")
        == oc4_observed.get("ra_hi_closeout_external_superiority_ready_rows")
        == 0,
        "RA/HI closeout overpromotes source-policy rows in objective audit",
    )
    checks.check(
        summary.get("ra_hi_closeout_opt_in_required")
        == oc4_observed.get("ra_hi_closeout_opt_in_required")
        is True
        and summary.get("ra_hi_closeout_execution_invoked")
        == oc4_observed.get("ra_hi_closeout_execution_invoked")
        is False
        and summary.get("ra_hi_closeout_b4_can_close")
        == oc4_observed.get("ra_hi_closeout_b4_can_close")
        is False
        and summary.get("ra_hi_closeout_b7_can_close")
        == oc4_observed.get("ra_hi_closeout_b7_can_close")
        is False,
        "RA/HI closeout execution boundary changed in objective audit",
    )
    checks.check(
        summary.get("ra_hi_current_evidence_terminal_not_promotable_rows")
        == oc4_observed.get("ra_hi_current_evidence_terminal_not_promotable_rows")
        == ra_hi_promotion_matrix.get("current_evidence_terminal_not_promotable_rows")
        == 20,
        "RA/HI terminal current-evidence count changed in objective audit",
    )
    checks.check(
        summary.get("ra_hi_future_promotion_requires_authorized_execution_or_new_artifact_rows")
        == oc4_observed.get("ra_hi_future_promotion_requires_authorized_execution_or_new_artifact_rows")
        == ra_hi_promotion_matrix.get(
            "future_promotion_requires_authorized_execution_or_new_artifact_rows"
        )
        == 20,
        "RA/HI future-promotion reopen-boundary count changed in objective audit",
    )
    checks.check(
        summary.get("ra_hi_source_policy_reproduction_complete_rows")
        == oc4_observed.get("ra_hi_source_policy_reproduction_complete_rows")
        == ra_hi_promotion_matrix.get("source_policy_reproduction_complete_rows")
        == 0,
        "RA/HI reproduction-complete count changed in objective audit",
    )
    checks.check(
        summary.get("source_policy_execution_handoff_status")
        == oc4_observed.get("source_policy_execution_handoff_status")
        == b4_execution_handoff.get("status")
        == "source_policy_execution_handoff_ready_not_authorized_not_run",
        "source-policy execution handoff status not propagated into objective audit",
    )
    checks.check(
        summary.get("source_policy_execution_handoff_authorized")
        == oc4_observed.get("source_policy_execution_handoff_authorized")
        == b4_execution_handoff.get("execution_authorized")
        is False
        and summary.get("source_policy_execution_handoff_commands_not_run")
        == oc4_observed.get("source_policy_execution_handoff_commands_not_run")
        == b4_execution_handoff.get("commands_not_run_by_handoff")
        is True,
        "source-policy execution handoff authorization boundary changed in objective audit",
    )
    checks.check(
        summary.get("ra_hi_closeout_exact_approval_statement")
        == oc4_observed.get("ra_hi_closeout_exact_approval_statement")
        == ra_hi_closeout.get("guarded_execution_boundary", {}).get(
            "exact_required_user_approval_statement"
        )
        == "I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json.",
        "RA/HI exact B4 approval statement changed in objective audit",
    )
    checks.check(
        summary.get("source_policy_execution_handoff_exact_approval_statement")
        == oc4_observed.get("source_policy_execution_handoff_exact_approval_statement")
        == b4_execution_handoff.get("exact_approval_statement")
        == "I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json.",
        "source-policy handoff exact approval statement changed in objective audit",
    )
    checks.check(
        summary.get("source_policy_execution_handoff_driver")
        == oc4_observed.get("source_policy_execution_handoff_driver")
        == b4_execution_handoff.get("guarded_execution_driver")
        == "run_b4_source_policy_after_opt_in.sh"
        and summary.get("source_policy_execution_handoff_driver_requires_exact_approval")
        == oc4_observed.get("source_policy_execution_handoff_driver_requires_exact_approval")
        == b4_execution_handoff.get("driver_requires_exact_approval")
        is True
        and summary.get("source_policy_execution_handoff_driver_does_not_authorize_execution")
        == oc4_observed.get("source_policy_execution_handoff_driver_does_not_authorize_execution")
        == b4_execution_handoff.get("driver_does_not_authorize_execution")
        is True,
        "source-policy handoff guarded driver boundary changed in objective audit",
    )
    checks.check(
        summary.get("source_policy_execution_handoff_ready_command_count")
        == oc4_observed.get("source_policy_execution_handoff_ready_command_count")
        == b4_execution_handoff.get("ready_command_count")
        == 13
        and summary.get("source_policy_execution_handoff_ready_command_mapped_rows")
        == oc4_observed.get("source_policy_execution_handoff_ready_command_mapped_rows")
        == b4_execution_handoff.get("ready_command_mapped_external_rows")
        == 20,
        "source-policy execution handoff command mapping changed in objective audit",
    )
    checks.check(
        summary.get("source_policy_execution_handoff_opt_in_required_command_count")
        == oc4_observed.get("source_policy_execution_handoff_opt_in_required_command_count")
        == b4_execution_handoff.get("opt_in_required_command_count")
        == 13
        and summary.get("source_policy_execution_handoff_opt_in_required_mapped_rows")
        == oc4_observed.get("source_policy_execution_handoff_opt_in_required_mapped_rows")
        == b4_execution_handoff.get("opt_in_required_mapped_external_rows")
        == 20,
        "source-policy handoff opt-in command mapping changed in objective audit",
    )
    checks.check(
        summary.get("source_policy_execution_handoff_terminal_unable_rows")
        == oc4_observed.get("source_policy_execution_handoff_terminal_unable_rows")
        == b4_execution_handoff.get("source_policy_row_state", {}).get("unable_to_reproduce")
        == 20,
        "source-policy execution handoff terminal-unable rows changed",
    )
    checks.check(
        summary.get("b4_guarded_driver_refusal_boundary_20260621_status")
        == oc4_observed.get("b4_guarded_driver_refusal_boundary_20260621_status")
        == b4_guarded_refusal.get("status")
        == "guarded_driver_refusal_boundary_static_proved_not_executed",
        "B4 guarded refusal status not propagated into objective audit",
    )
    checks.check(
        summary.get("b4_guarded_driver_no_opt_in_refusal_proved_static")
        == oc4_observed.get("b4_guarded_driver_no_opt_in_refusal_proved_static")
        == b4_guarded_refusal.get("no_opt_in_refusal_proved_static")
        is True
        and summary.get("b4_guarded_driver_wrong_approval_refusal_proved_static")
        == oc4_observed.get("b4_guarded_driver_wrong_approval_refusal_proved_static")
        == b4_guarded_refusal.get("wrong_approval_refusal_proved_static")
        is True
        and summary.get("b4_guarded_driver_refusal_exit_code")
        == oc4_observed.get("b4_guarded_driver_refusal_exit_code")
        == b4_guarded_refusal.get("refusal_exit_code")
        == 2,
        "B4 guarded refusal proof tuple changed in objective audit",
    )
    checks.check(
        summary.get("b4_guarded_driver_pre_guard_command_count")
        == oc4_observed.get("b4_guarded_driver_pre_guard_command_count")
        == b4_guarded_refusal.get("pre_guard_command_count")
        == 0
        and summary.get("b4_guarded_driver_post_guard_source_policy_command_count")
        == oc4_observed.get("b4_guarded_driver_post_guard_source_policy_command_count")
        == b4_guarded_refusal.get("post_guard_source_policy_command_count")
        == 13,
        "B4 guarded refusal command boundary changed in objective audit",
    )
    checks.check(
        summary.get("b4_guarded_driver_invoked_by_audit")
        == oc4_observed.get("b4_guarded_driver_invoked_by_audit")
        == b4_guarded_refusal.get("driver_invoked_by_audit")
        is False
        and summary.get("b4_guarded_driver_source_policy_execution_invoked")
        == oc4_observed.get("b4_guarded_driver_source_policy_execution_invoked")
        == b4_guarded_refusal.get("source_policy_execution_invoked")
        is False
        and summary.get("b4_guarded_driver_submission_ready")
        == oc4_observed.get("b4_guarded_driver_submission_ready")
        == b4_guarded_refusal.get("submission_ready")
        is False,
        "B4 guarded refusal overexecuted or overpromoted in objective audit",
    )
    checks.check(
        summary.get("b4_guarded_driver_refusal_boundary_marker")
        == oc4_observed.get("b4_guarded_driver_refusal_boundary_marker")
        == b4_guarded_refusal.get("marker")
        == "b4_guarded_driver_refusal_boundary_audit_20260621=True/True/2/0/13/False/False",
        "B4 guarded refusal marker not propagated into objective audit",
    )
    checks.check(
        summary.get("source_policy_execution_handoff_command_traceability_summary")
        == oc4_observed.get("source_policy_execution_handoff_command_traceability_summary")
        == expected_command_traceability,
        "source-policy handoff command traceability summary stale in objective audit",
    )
    checks.check(
        summary.get("source_policy_execution_handoff_unique_mapped_row_count")
        == oc4_observed.get("source_policy_execution_handoff_unique_mapped_row_count")
        == expected_command_traceability.get("unique_mapped_row_count")
        == 20
        and summary.get("source_policy_execution_handoff_ra_hi_unique_row_count")
        == oc4_observed.get("source_policy_execution_handoff_ra_hi_unique_row_count")
        == expected_command_traceability.get("ra_hi_unique_row_count")
        == 20
        and summary.get("source_policy_execution_handoff_ra_hi_unique_rows_all_mapped")
        == oc4_observed.get("source_policy_execution_handoff_ra_hi_unique_rows_all_mapped")
        == expected_command_traceability.get("ra_hi_unique_rows_all_mapped")
        is True,
        "source-policy handoff unique row traceability changed in objective audit",
    )
    checks.check(
        summary.get("source_policy_execution_handoff_declared_mapped_row_reference_total")
        == oc4_observed.get("source_policy_execution_handoff_declared_mapped_row_reference_total")
        == expected_command_traceability.get("declared_mapped_row_reference_total")
        == 32
        and summary.get("source_policy_execution_handoff_traced_command_row_reference_total")
        == oc4_observed.get("source_policy_execution_handoff_traced_command_row_reference_total")
        == expected_command_traceability.get("traced_command_row_reference_total")
        == 32
        and summary.get("source_policy_execution_handoff_declared_vs_traced_mismatch_count")
        == oc4_observed.get("source_policy_execution_handoff_declared_vs_traced_mismatch_count")
        == expected_command_traceability.get("declared_vs_traced_mismatch_count")
        == 0,
        "source-policy handoff row-reference traceability changed in objective audit",
    )
    checks.check(
        summary.get("source_policy_execution_handoff_terminal_rows_with_command_refs")
        == oc4_observed.get("source_policy_execution_handoff_terminal_rows_with_command_refs")
        == expected_command_traceability.get("terminal_rows_with_command_refs")
        == 0
        and summary.get("source_policy_execution_handoff_traceability_closed_rows")
        == oc4_observed.get("source_policy_execution_handoff_traceability_closed_rows")
        == expected_command_traceability.get("source_policy_closed_rows")
        == 0
        and summary.get("source_policy_execution_handoff_traceability_promotion_ready_rows")
        == oc4_observed.get("source_policy_execution_handoff_traceability_promotion_ready_rows")
        == expected_command_traceability.get("promotion_ready_rows")
        == 0,
        "source-policy handoff terminal/closed traceability changed in objective audit",
    )
    provenance_handoff = full_source_policy_row_provenance.get(
        "source_policy_execution_handoff", {}
    )
    checks.check(
        summary.get("full_source_policy_row_provenance_handoff_status")
        == provenance_handoff.get("status")
        == "source_policy_execution_handoff_ready_not_authorized_not_run",
        "full source-policy provenance handoff status missing in objective audit",
    )
    checks.check(
        summary.get("full_source_policy_row_provenance_handoff_authorized")
        == provenance_handoff.get("execution_authorized")
        is False
        and summary.get("full_source_policy_row_provenance_handoff_commands_not_run")
        == provenance_handoff.get("commands_not_run_by_handoff")
        is True,
        "full source-policy provenance handoff authorization boundary changed in objective audit",
    )
    checks.check(
        summary.get("full_source_policy_row_provenance_handoff_exact_approval")
        == provenance_handoff.get("exact_required_user_approval_statement")
        == "I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json.",
        "full source-policy provenance handoff exact approval missing in objective audit",
    )
    checks.check(
        summary.get("full_source_policy_row_provenance_handoff_driver")
        == provenance_handoff.get("guarded_execution_driver")
        == "run_b4_source_policy_after_opt_in.sh"
        and summary.get("full_source_policy_row_provenance_handoff_driver_requires_exact")
        == provenance_handoff.get("driver_requires_exact_approval")
        is True
        and summary.get("full_source_policy_row_provenance_handoff_driver_does_not_authorize")
        == provenance_handoff.get("driver_does_not_authorize_execution")
        is True,
        "full source-policy provenance handoff guarded driver changed in objective audit",
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
        "full source-policy provenance handoff counts changed in objective audit",
    )
    checks.check(
        oc4_observed.get("full_source_policy_row_provenance_status")
        == full_source_policy_row_provenance.get("status")
        == "row_provenance_preflight_complete_source_policy_promotion_open"
        and oc4_observed.get("full_source_policy_row_provenance_rows")
        == full_source_policy_row_provenance.get("row_count")
        == 40
        and oc4_observed.get("full_source_policy_row_provenance_preflight")
        == full_source_policy_row_provenance.get("provenance_preflight")
        == "40/40"
        and oc4_observed.get("full_source_policy_row_provenance_source_policy_closed")
        == full_source_policy_row_provenance.get("source_policy_closed")
        is False
        and oc4_observed.get("full_source_policy_row_provenance_source_policy_closed_ratio")
        == full_source_policy_row_provenance.get("source_policy_closed_ratio")
        == "0/40"
        and oc4_observed.get("full_source_policy_row_provenance_promotion_ready_rows")
        == full_source_policy_row_provenance.get("promotion_ready_rows")
        == 0,
        "OC4 observed full source-policy row provenance counts changed",
    )
    checks.check(
        oc4_observed.get("full_source_policy_row_provenance_handoff_status")
        == provenance_handoff.get("status")
        == "source_policy_execution_handoff_ready_not_authorized_not_run"
        and oc4_observed.get("full_source_policy_row_provenance_handoff_authorized")
        == provenance_handoff.get("execution_authorized")
        is False
        and oc4_observed.get("full_source_policy_row_provenance_handoff_commands_not_run")
        == provenance_handoff.get("commands_not_run_by_handoff")
        is True
        and oc4_observed.get("full_source_policy_row_provenance_handoff_driver")
        == provenance_handoff.get("guarded_execution_driver")
        == "run_b4_source_policy_after_opt_in.sh"
        and oc4_observed.get("full_source_policy_row_provenance_handoff_driver_does_not_authorize")
        == provenance_handoff.get("driver_does_not_authorize_execution")
        is True
        and oc4_observed.get("full_source_policy_row_provenance_handoff_opt_in_commands")
        == provenance_handoff.get("opt_in_required_command_count")
        == 13
        and oc4_observed.get("full_source_policy_row_provenance_handoff_mapped_rows")
        == provenance_handoff.get("opt_in_required_mapped_external_rows")
        == 20,
        "OC4 observed full source-policy provenance handoff boundary changed",
    )
    checks.check(by_id.get("OC5", {}).get("status") == "satisfied", "OC5 should be satisfied")
    checks.check(
        by_id.get("OC5", {}).get("blocking_for_goal_completion") is False,
        "OC5 should not block after Route-B demotion closure",
    )
    for req_id in ["OC6", "OC12"]:
        checks.check(by_id.get(req_id, {}).get("status") == "partial", f"{req_id} should remain partial")
        checks.check(
            by_id.get(req_id, {}).get("blocking_for_goal_completion") is True,
            f"{req_id} should block completion",
        )
    for req_id in ["OC4", "OC6", "OC12"]:
        checks.check(
            open_blockers_by_id.get(req_id, {}).get("status") == by_id.get(req_id, {}).get("status"),
            f"{req_id} top-level blocker status does not match requirement table",
        )
        checks.check(
            open_blockers_by_id.get(req_id, {}).get("next_to_close")
            == by_id.get(req_id, {}).get("next_to_close"),
            f"{req_id} top-level next action does not match requirement table",
        )
    checks.check(
        by_id.get("OC4", {}).get("evidence")
        == [
            "EXTERNAL_SOURCE_POLICY_CLOSURE_MANIFEST.json",
            "RA_HI_SOURCE_POLICY_CLOSEOUT_CHECKLIST.json",
            "RA_HI_SOURCE_POLICY_PROMOTION_BLOCKER_MATRIX.json",
            "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json",
            "B4_GUARDED_DRIVER_REFUSAL_BOUNDARY_AUDIT_20260621.json",
            "FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.json",
        ],
        "OC4 evidence list must include full source-policy row provenance audit",
    )
    checks.check(
        by_id.get("OC6", {}).get("evidence")
        == [
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
        "OC6 evidence list must include the TFE self-reproduction, public-code refresh, external recheck, reopen monitor, and runner preflight artifacts",
    )
    for req_id in ["OC8", "OC10"]:
        checks.check(by_id.get(req_id, {}).get("status") == "satisfied", f"{req_id} should be satisfied")
        checks.check(
            by_id.get(req_id, {}).get("blocking_for_goal_completion") is False,
            f"{req_id} should not block completion after narrowed-claim closure",
        )

    checks.check(
        matrix.get("row_count") == matrix.get("expected_row_count") == summary.get("core_matrix_ready") * 44,
        "matrix readiness no longer matches source matrix",
    )
    checks.check(
        traceability.get("claim_boundary", {}).get("result_to_manuscript_traceability_closed")
        == summary.get("traceability_ready")
        is True,
        "traceability readiness changed",
    )
    checks.check(
        source_policy.get("source_policy_reproduction") is False
        and summary.get("source_policy_closed") is False,
        "source-policy boundary changed",
    )
    oc5_observed = by_id.get("OC5", {}).get("observed", {})
    checks.check(
        b2.get("source_policy_closed_rows") == 0
        and b2.get("b2_can_close_now") is True
        and b2.get("active_flagged_row_count") == 0
        and b2.get("b2_remaining_requirements") == []
        and b2.get("demoted_flagged_row_count") == 15
        and b2.get("demoted_suite_counts") == expected_b2_demoted_suite_counts
        and b2.get("external_superiority_claim_allowed") is False
        and summary.get("b2_source_policy_closed") is False
        and summary.get("b2_source_policy_rows_closed") is False
        and summary.get("b2_active_suites_closed") is True
        and summary.get("b2_active_suites_closed_by_demotion") is True
        and audit.get("b2_active_suites_closed") is True
        and audit.get("b2_active_suites_closed_by_demotion") is True
        and oc5_observed.get("b2_source_policy_rows_closed") is False
        and oc5_observed.get("b2_can_close_now") is True
        and oc5_observed.get("b2_active_suites_closed_by_demotion") is True
        and oc5_observed.get("active_flagged_rows") == 0
        and oc5_observed.get("remaining_requirements") == []
        and oc5_observed.get("demoted_flagged_rows") == 15
        and oc5_observed.get("demoted_suite_counts") == expected_b2_demoted_suite_counts
        and oc5_observed.get("external_superiority_claim_allowed") is False
        and oc5_observed.get("demotion_ledger_status")
        == "all_external_suites_demoted_from_external_superiority_scope"
        and oc5_observed.get("demotion_ledger_remaining_open_suites") == []
        and external_demotion.get("remaining_open_suites") == []
        and external_demotion.get("active_source_policy_flagged_rows_after_demotions") == 0
        and external_demotion.get("b2_required_to_close_after_demotions") == [],
        "B2 Route-B demotion closure changed",
    )
    checks.check(
        tfe_model.get("source_pendulum_parameter_model_implemented") is True
        and tfe_model.get("source_error_norm_and_output_policy_encoded") is True
        and tfe_model.get("brown_mcphee_candidate_friction_law_encoded") is True
        and tfe_model.get("frictional_planar_candidate_rhs_smoke_implemented") is True
        and tfe_model.get("absolute_coordinate_dae_residual_smoke_implemented") is True
        and tfe_model.get("absolute_coordinate_frictional_candidate_dae_smoke_implemented") is True
        and tfe_model.get("absolute_coordinate_planar_lift_trajectory_probe_implemented") is True
        and tfe_model.get("absolute_coordinate_planar_lift_trajectory_probe_rows") == 12
        and tfe_model.get("absolute_coordinate_planar_lift_trajectory_probe_metric_rows") == 36
        and tfe_model.get("absolute_coordinate_planar_lift_trajectory_probe_source_policy_rows_completed") == 0
        and tfe_model.get("absolute_coordinate_planar_lift_trajectory_probe_dae_runner_equivalent") is False
        and tfe_model.get("bounded_absolute_coordinate_dae_trajectory_runner_implemented") is True
        and tfe_model.get("bounded_absolute_coordinate_dae_trajectory_runner_rows") == 4
        and tfe_model.get("bounded_absolute_coordinate_dae_trajectory_runner_metric_rows") == 12
        and tfe_model.get("bounded_absolute_coordinate_dae_trajectory_runner_step_residual_rows") == 56
        and tfe_model.get("bounded_absolute_coordinate_dae_trajectory_runner_source_policy_rows_completed") == 0
        and tfe_model.get("bounded_absolute_coordinate_dae_trajectory_runner_dae_runner_equivalent") is False
        and tfe_model.get("bounded_absolute_coordinate_dae_trajectory_runner_monolithic_integrator") is False
        and tfe_model.get("monolithic_absolute_coordinate_dae_candidate_runner_implemented") is True
        and tfe_model.get("monolithic_absolute_coordinate_dae_candidate_runner_rows") == 4
        and tfe_model.get("monolithic_absolute_coordinate_dae_candidate_runner_metric_rows") == 12
        and tfe_model.get("monolithic_absolute_coordinate_dae_candidate_runner_step_residual_rows") == 56
        and tfe_model.get("monolithic_absolute_coordinate_dae_candidate_runner_source_policy_rows_completed") == 0
        and tfe_model.get("monolithic_absolute_coordinate_dae_candidate_runner_dae_runner_equivalent") is False
        and tfe_model.get("monolithic_absolute_coordinate_dae_candidate_runner_monolithic_integrator") is False
        and tfe_model.get("source_method_candidate_runner_contract_implemented") is True
        and tfe_model.get("source_method_candidate_runner_contract_rows") == 5
        and tfe_model.get("source_method_candidate_runner_contract_source_policy_rows_completed") == 0
        and tfe_model.get("source_method_candidate_runner_contract_method_equivalent") is False
        and tfe_model.get("source_method_candidate_runner_contract_dae_equivalent") is False
        and tfe_model.get("dae_trajectory_bridge_contract_implemented") is True
        and tfe_model.get("dae_trajectory_bridge_contract_rows") == 12
        and tfe_model.get("dae_trajectory_bridge_contract_matched_rows") == 12
        and tfe_model.get("dae_trajectory_bridge_contract_source_metric_rows") == 12
        and tfe_model.get("dae_trajectory_bridge_contract_dae_metric_rows") == 12
        and tfe_model.get("dae_trajectory_bridge_contract_source_policy_rows_completed") == 0
        and tfe_model.get("dae_trajectory_bridge_contract_dae_runner_equivalent") is False
        and tfe_model.get("dae_trajectory_bridge_contract_smoke", {}).get(
            "source_policy_method_runner_equivalent"
        )
        is False
        and tfe_model.get("dae_trajectory_bridge_contract_monolithic_integrator") is False
        and tfe_model.get("dae_trajectory_bridge_contract_all_rows_finite") is True
        and tfe_model.get("dae_trajectory_bridge_contract_all_dae_residuals_below_1e_10") is True
        and tfe_model.get("dae_trajectory_bridge_contract_smoke", {}).get("accepted_use")
        == "dae_trajectory_bridge_contract_not_source_policy"
        and tfe_model.get("candidate_frictional_dae_trajectory_contract_implemented") is True
        and tfe_model.get("candidate_frictional_dae_trajectory_contract_rows") == 12
        and tfe_model.get("candidate_frictional_dae_trajectory_contract_step_residual_rows") == 56
        and tfe_model.get("candidate_frictional_dae_trajectory_contract_source_policy_rows_completed") == 0
        and tfe_model.get("candidate_frictional_dae_trajectory_contract_dae_runner_equivalent") is False
        and tfe_model.get("candidate_frictional_dae_trajectory_contract_method_runner_equivalent") is False
        and tfe_model.get(
            "candidate_frictional_dae_trajectory_contract_brown_mcphee_source_code_equivalent_law"
        )
        is False
        and tfe_model.get("candidate_frictional_dae_trajectory_contract_monolithic_integrator") is False
        and tfe_model.get("candidate_frictional_dae_trajectory_contract_all_rows_finite") is True
        and tfe_model.get("candidate_frictional_dae_trajectory_contract_all_dae_residuals_below_1e_9") is True
        and tfe_model.get("candidate_frictional_dae_trajectory_contract_all_friction_power_nonpositive") is True
        and tfe_model.get("source_policy_dae_runner_equivalent") is False
        and tfe_model.get("source_output_time_integration_smoke_implemented") is True
        and tfe_model.get("source_policy_time_integration_runner_equivalent") is False
        and tfe_model.get("source_reference_solution_policy_smoke_implemented") is True
        and tfe_model.get("source_reference_solution_policy_smoke_full_T10") is False
        and tfe_model.get("source_comparator_candidate_runners_implemented") is True
        and tfe_model.get("newmark_beta_candidate_runner_smoke_implemented") is True
        and tfe_model.get("trapezoidal_candidate_runner_smoke_implemented") is True
        and tfe_model.get("source_policy_method_runner_equivalent") is False
        and tfe_model.get("tfe_m1_m2_m3_candidate_runner_smoke_implemented") is True
        and tfe_model.get("tfe_m1_m2_m3_source_policy_runners_implemented") is False
        and tfe_model.get("gauss6_fullva_source_pendulum_candidate_smoke_implemented") is True
        and tfe_model.get("gauss6_fullva_absolute_coordinate_source_policy_runner_implemented") is False
        and tfe_model.get("gauss6_fullva_on_source_pendulum_implemented") is True
        and tfe_model.get("gauss6_fullva_source_pendulum_candidate_rows") == 2
        and tfe_model.get("gauss6_fullva_source_pendulum_candidate_source_policy_rows_completed") == 0
        and tfe_model.get("gauss6_fullva_source_pendulum_candidate_method_equivalent") is False
        and tfe_model.get("gauss6_fullva_dae_candidate_contract_implemented") is True
        and tfe_model.get("gauss6_fullva_dae_candidate_contract_rows") == 1
        and tfe_model.get("gauss6_fullva_dae_candidate_contract_source_policy_rows_completed") == 0
        and tfe_model.get("gauss6_fullva_dae_candidate_contract_dae_equivalent") is False
        and tfe_model.get("gauss6_fullva_dae_candidate_contract_fullva_dae_equivalent") is False
        and tfe_model.get("bounded_source_policy_runner_smoke_implemented") is True
        and tfe_model.get("bounded_source_policy_runner_rows") == 4
        and tfe_model.get("bounded_source_policy_runner_full_T10") is False
        and tfe_model.get("bounded_source_policy_runner_source_policy_rows_completed") == 0
        and tfe_model.get("active_tfe_b2_candidate_row_smoke_implemented") is True
        and tfe_model.get("active_tfe_b2_candidate_row_smoke_full_T10") is False
        and tfe_model.get("active_tfe_b2_source_policy_rows_completed") == 0
        and tfe_model.get("active_tfe_b2_source_reference_full_T10_candidate_probe_implemented") is True
        and tfe_model.get("active_tfe_b2_source_reference_full_T10_candidate_probe_full_T10") is True
        and tfe_model.get(
            "active_tfe_b2_source_reference_full_T10_candidate_probe_source_policy_reference_invoked"
        )
        is True
        and tfe_model.get(
            "active_tfe_b2_source_reference_full_T10_candidate_probe_source_policy_rows_completed"
        )
        == 0
        and tfe_model.get("active_tfe_b2_source_reference_full_T10_candidate_probe_method_equivalent")
        is False
        and tfe_model.get("pendulum_dae_runner_implemented") is False
        and summary.get("tfe_runner_closed") is False,
        "TFE runner boundary changed",
    )
    checks.check(
        tfe_dae_gap.get("schema") == "tfe-dae-runner-contract-gap-audit-v1"
        and tfe_dae_gap.get("status") == "dae_runner_contract_gap_open_not_source_policy"
        and tfe_dae_gap.get("missing_contract_block_count") == 6
        and [item.get("id") for item in tfe_dae_gap.get("missing_contract_blocks", [])]
        == expected_tfe_dae_gap_ids
        and tfe_dae_gap.get("nonheavy_missing_contract_blocks")
        == expected_tfe_dae_nonheavy_gap_ids
        and [item.get("id") for item in tfe_dae_gap.get("nonheavy_missing_contract_block_dispositions", [])]
        == expected_tfe_dae_nonheavy_gap_ids
        and tfe_dae_gap.get("nonheavy_missing_contract_blocks_dispositioned_by_demotion") is True
        and tfe_dae_gap.get("nonheavy_demotion_does_not_close_source_policy") is True
        and tfe_dae_gap.get("terminal_nonpromoted_contract_blocks")
        == expected_tfe_dae_nonheavy_gap_ids
        and tfe_dae_gap.get("terminal_nonpromoted_contract_block_count") == 2
        and tfe_dae_gap.get("effective_missing_contract_blocks")
        == expected_tfe_dae_execution_gap_ids
        and tfe_dae_gap.get("effective_missing_contract_block_count") == 4
        and tfe_dae_gap.get("source_policy_execution_missing_contract_blocks")
        == expected_tfe_dae_execution_gap_ids
        and tfe_dae_gap.get("source_policy_execution_missing_contract_block_count") == 4
        and tfe_dae_gap.get("ready_to_execute_source_policy_now") is False
        and tfe_dae_gap.get("heavy_numerical_run_invoked") is False,
        "TFE DAE runner contract gap audit boundary changed",
    )
    checks.check(
        summary.get("tfe_dae_runner_contract_gap_status") == tfe_dae_gap.get("status")
        and summary.get("tfe_dae_runner_contract_gap_missing_block_count") == 6
        and summary.get("tfe_dae_runner_contract_gap_missing_block_ids") == expected_tfe_dae_gap_ids
        and summary.get("tfe_dae_runner_contract_gap_nonheavy_blocks")
        == tfe_dae_gap.get("nonheavy_missing_contract_blocks")
        and summary.get("tfe_dae_runner_contract_gap_nonheavy_disposition_ids")
        == expected_tfe_dae_nonheavy_gap_ids
        and summary.get("tfe_dae_runner_contract_gap_nonheavy_dispositioned_by_demotion") is True
        and summary.get("tfe_dae_runner_contract_gap_nonheavy_demotion_does_not_close_source_policy") is True
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
        and summary.get("tfe_dae_runner_contract_gap_execution_block_count") == 4
        and summary.get("tfe_dae_runner_contract_gap_ready_to_execute_source_policy_now") is False
        and summary.get("tfe_dae_runner_contract_gap_heavy_run_invoked") is False,
        "summary TFE DAE runner contract gap fields changed",
    )
    checks.check(
        summary.get("tfe_source_policy_execution_preflight_status")
        == tfe_execution_preflight.get("status")
        == "terminal_no_public_code_self_reproduction_attempted_not_promoted"
        and summary.get("tfe_source_policy_execution_preflight_current_route")
        == tfe_execution_preflight.get("current_route")
        == "no_public_code_self_reproduction_attempted_unable_to_reproduce_not_promoted"
        and summary.get("tfe_source_policy_execution_preflight_reopen_condition")
        == tfe_execution_preflight.get("reopen_condition")
        == "new_public_or_source_code_equivalent_tfe_implementation_artifact"
        and summary.get("tfe_source_policy_execution_preflight_opt_in_required")
        == tfe_execution_preflight.get("explicit_user_opt_in_required")
        is False
        and summary.get("tfe_source_policy_execution_preflight_nonheavy_dispositioned")
        == tfe_execution_preflight.get("nonheavy_blocks_dispositioned_by_demotion")
        is True
        and summary.get("tfe_source_policy_execution_preflight_execution_block_count")
        == tfe_execution_preflight.get("execution_block_count")
        == 4
        and summary.get("tfe_source_policy_execution_preflight_can_promote_rows_now")
        == tfe_execution_preflight.get("can_promote_any_tfe_source_policy_row_now")
        is False
        and summary.get("tfe_source_policy_execution_preflight_ready_now")
        == tfe_execution_preflight.get("ready_to_execute_source_policy_now")
        is False,
        "summary TFE source-policy execution preflight fields changed",
    )
    checks.check(
        summary.get("tfe_self_reproduction_status")
        == tfe_self_reproduction.get("status")
        == "attempted_not_reproducible_not_promoted"
        and summary.get("tfe_self_reproduction_attempted_not_reproducible_rows")
        == tfe_self_reproduction.get("attempted_not_reproducible_rows")
        == 16
        and summary.get("tfe_self_reproduction_unable_to_reproduce_rows")
        == tfe_self_reproduction.get("unable_to_reproduce_rows")
        == 16
        and summary.get("tfe_self_reproduction_source_policy_closed")
        == tfe_self_reproduction.get("source_policy_closed")
        is False
        and summary.get("tfe_self_reproduction_source_policy_closed_ratio")
        == tfe_self_reproduction.get("source_policy_closed_ratio")
        == "0/16"
        and summary.get("tfe_self_reproduction_public_code_recheck_status")
        == tfe_self_reproduction.get("public_code_recheck_status")
        == "public_code_rechecked_no_distinct_tfe_code_artifact_attempted_not_reproducible"
        and summary.get("tfe_self_reproduction_reopen_condition")
        == tfe_self_reproduction.get("reopen_condition")
        == "new_public_or_source_code_equivalent_tfe_implementation_artifact"
        and summary.get("tfe_self_reproduction_preflight_status")
        == tfe_self_reproduction.get("source_policy_execution_preflight_status")
        == "terminal_no_public_code_self_reproduction_attempted_not_promoted",
        "summary TFE self-reproduction certificate aliases changed",
    )
    checks.check(
        summary.get("tfe_public_code_refresh_20260620_status")
        == source_policy_public_code_refresh.get("status")
        == "public_code_refresh_20260620_no_positive_new_source_artifact_rows_remain_unable_to_reproduce"
        and summary.get("tfe_public_code_refresh_20260620_rows")
        == source_policy_public_code_refresh.get("rows")
        == 20
        and summary.get("tfe_public_code_refresh_20260620_current_queries")
        == source_policy_public_code_refresh.get("current_queries")
        == 11
        and summary.get("tfe_public_code_refresh_20260620_positive_artifact_rows")
        == source_policy_public_code_refresh.get("positive_public_code_artifact_rows")
        == 0
        and summary.get("tfe_public_code_refresh_20260620_source_policy_closed_ratio")
        == source_policy_public_code_refresh.get("source_policy_closed_ratio")
        == "0/20",
        "summary TFE public-code refresh aliases changed",
    )
    checks.check(
        summary.get("tfe_public_code_refresh_20260620_latest_external_probe_date")
        == source_policy_public_code_refresh.get("latest_external_probe_date_checked")
        == "2026-06-21"
        and summary.get("tfe_public_code_refresh_20260620_latest_external_probe_count")
        == source_policy_public_code_refresh.get("latest_external_probe_count")
        == 9
        and summary.get("tfe_public_code_refresh_20260620_latest_external_probe_positive_artifact_rows")
        == source_policy_public_code_refresh.get("latest_external_probe_positive_public_code_artifact_rows")
        == 0
        and summary.get("tfe_public_code_refresh_20260620_latest_external_probe_source_policy_rows_closed")
        == source_policy_public_code_refresh.get("latest_external_probe_source_policy_rows_closed")
        == 0
        and summary.get("tfe_public_code_refresh_20260620_latest_external_probe_access_limited_count")
        == source_policy_public_code_refresh.get("latest_external_probe_access_limited_count")
        == 4
        and summary.get("tfe_public_code_refresh_20260620_latest_external_probe_global_absence_proved")
        == source_policy_public_code_refresh.get("latest_external_probe_global_absence_proved")
        is False
        and summary.get("tfe_public_code_refresh_20260620_latest_external_probe_reopen_triggered")
        == source_policy_public_code_refresh.get("latest_external_probe_source_policy_reopen_triggered")
        is False,
        "summary TFE latest external probe aliases changed",
    )
    checks.check(
        summary.get("oc6_external_source_artifact_recheck_20260621_status")
        == oc6_external_recheck.get("status")
        == "no_positive_external_source_artifact_found_reopen_conditions_remain_open"
        and summary.get("oc6_external_source_artifact_recheck_20260621_date")
        == oc6_external_recheck.get("date_checked")
        == "2026-06-21"
        and summary.get("oc6_external_source_artifact_recheck_20260621_query_count")
        == oc6_external_recheck.get("query_count")
        == 10
        and summary.get("oc6_external_source_artifact_recheck_20260621_positive_artifact_rows")
        == oc6_external_recheck.get("positive_public_code_artifact_rows")
        == 0
        and summary.get("oc6_external_source_artifact_recheck_20260621_source_equivalent_artifact_rows")
        == oc6_external_recheck.get("source_code_equivalent_artifact_rows")
        == 0
        and summary.get("oc6_external_source_artifact_recheck_20260621_source_policy_rows_closed")
        == oc6_external_recheck.get("source_policy_rows_closed_by_recheck")
        == 0
        and summary.get("oc6_external_source_artifact_recheck_20260621_reopen_triggered")
        == oc6_external_recheck.get("source_policy_reopen_triggered")
        is False
        and summary.get("oc6_external_source_artifact_recheck_20260621_global_absence_proved")
        == oc6_external_recheck.get("global_absence_proved")
        is False,
        "summary OC6 external source-artifact recheck aliases changed",
    )
    checks.check(
        summary.get("oc6_tfe_publisher_artifact_availability_20260621_status")
        == oc6_publisher_availability.get("status")
        == "publisher_article_checked_no_code_or_supplement_source_artifact_found"
        and summary.get("oc6_tfe_publisher_artifact_availability_20260621_date")
        == oc6_publisher_availability.get("date_checked")
        == "2026-06-21"
        and summary.get("oc6_tfe_publisher_artifact_availability_20260621_official_article_checked")
        == oc6_publisher_availability.get("official_article_checked")
        is True
        and summary.get("oc6_tfe_publisher_artifact_availability_20260621_source_artifact_signal_count")
        == oc6_publisher_availability.get("source_article", {}).get("source_artifact_signal_count")
        == 0
        and summary.get("oc6_tfe_publisher_artifact_availability_20260621_positive_artifact_rows")
        == oc6_publisher_availability.get("positive_public_code_artifact_rows")
        == 0
        and summary.get("oc6_tfe_publisher_artifact_availability_20260621_source_equivalent_artifact_rows")
        == oc6_publisher_availability.get("source_code_equivalent_artifact_rows")
        == 0
        and summary.get("oc6_tfe_publisher_artifact_availability_20260621_source_policy_rows_closed")
        == oc6_publisher_availability.get("source_policy_rows_closed_by_publisher_audit")
        == 0
        and summary.get("oc6_tfe_publisher_artifact_availability_20260621_reopen_triggered")
        == oc6_publisher_availability.get("source_policy_reopen_triggered")
        is False
        and summary.get("oc6_tfe_publisher_artifact_availability_20260621_global_absence_proved")
        == oc6_publisher_availability.get("global_absence_proved")
        is False,
        "summary OC6 publisher artifact availability aliases changed",
    )
    checks.check(
        summary.get("oc6_tfe_source_equivalent_artifact_request_packet_20260621_status")
        == oc6_source_equivalent_request_packet.get("status")
        == "request_packet_ready_not_sent_no_source_policy_closure"
        and summary.get("oc6_tfe_source_equivalent_artifact_request_packet_20260621_date")
        == oc6_source_equivalent_request_packet.get("date_prepared")
        == "2026-06-21"
        and summary.get("oc6_tfe_source_equivalent_artifact_request_packet_20260621_request_ready")
        == oc6_source_equivalent_request_packet.get("request_ready")
        is True
        and summary.get("oc6_tfe_source_equivalent_artifact_request_packet_20260621_request_sent")
        == oc6_source_equivalent_request_packet.get("request_sent")
        is False
        and summary.get("oc6_tfe_source_equivalent_artifact_request_packet_20260621_requested_artifact_count")
        == oc6_source_equivalent_request_packet.get("requested_artifact_count")
        == 7
        and summary.get("oc6_tfe_source_equivalent_artifact_request_packet_20260621_corresponding_author_email")
        == "ekanshchat96@vt.edu"
        and summary.get("oc6_tfe_source_equivalent_artifact_request_packet_20260621_source_policy_rows_closed")
        == oc6_source_equivalent_request_packet.get("not_closing", {}).get(
            "source_policy_rows_closed_by_packet"
        )
        == 0
        and summary.get("oc6_tfe_source_equivalent_artifact_request_packet_20260621_reopen_triggered")
        == oc6_source_equivalent_request_packet.get("not_closing", {}).get(
            "source_policy_reopen_triggered"
        )
        is False
        and summary.get("oc6_tfe_source_equivalent_artifact_request_packet_20260621_global_absence_proved")
        == oc6_source_equivalent_request_packet.get("not_closing", {}).get(
            "global_absence_proved"
        )
        is False
        and summary.get("oc6_tfe_source_equivalent_artifact_request_packet_20260621_submission_ready")
        == oc6_source_equivalent_request_packet.get("not_closing", {}).get(
            "submission_ready"
        )
        is False,
        "summary OC6 source-equivalent artifact request packet aliases changed",
    )
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
        "summary source-policy reopen monitor digest aliases changed",
    )
    checks.check(
        summary.get("tfe_absolute_coordinate_planar_lift_trajectory_probe_implemented") is True
        and summary.get("tfe_absolute_coordinate_planar_lift_trajectory_probe_rows") == 12
        and summary.get("tfe_absolute_coordinate_planar_lift_trajectory_probe_metric_rows") == 36
        and summary.get("tfe_absolute_coordinate_planar_lift_trajectory_probe_source_policy_rows_completed") == 0
        and summary.get("tfe_absolute_coordinate_planar_lift_trajectory_probe_dae_runner_equivalent") is False,
        "summary TFE absolute-coordinate planar-lift boundary changed",
    )
    checks.check(
        summary.get("tfe_bounded_absolute_coordinate_dae_trajectory_runner_implemented") is True
        and summary.get("tfe_bounded_absolute_coordinate_dae_trajectory_runner_rows") == 4
        and summary.get("tfe_bounded_absolute_coordinate_dae_trajectory_runner_metric_rows") == 12
        and summary.get("tfe_bounded_absolute_coordinate_dae_trajectory_runner_step_residual_rows") == 56
        and summary.get("tfe_bounded_absolute_coordinate_dae_trajectory_runner_source_policy_rows_completed") == 0
        and summary.get("tfe_bounded_absolute_coordinate_dae_trajectory_runner_dae_runner_equivalent") is False
        and summary.get("tfe_bounded_absolute_coordinate_dae_trajectory_runner_monolithic_integrator") is False,
        "summary TFE bounded DAE trajectory runner boundary changed",
    )
    checks.check(
        summary.get("tfe_monolithic_absolute_coordinate_dae_candidate_runner_implemented") is True
        and summary.get("tfe_monolithic_absolute_coordinate_dae_candidate_runner_rows") == 4
        and summary.get("tfe_monolithic_absolute_coordinate_dae_candidate_runner_metric_rows") == 12
        and summary.get("tfe_monolithic_absolute_coordinate_dae_candidate_runner_step_residual_rows") == 56
        and summary.get(
            "tfe_monolithic_absolute_coordinate_dae_candidate_runner_source_policy_rows_completed"
        )
        == 0
        and summary.get("tfe_monolithic_absolute_coordinate_dae_candidate_runner_dae_runner_equivalent")
        is False
        and summary.get("tfe_monolithic_absolute_coordinate_dae_candidate_runner_monolithic_integrator")
        is False,
        "summary TFE monolithic DAE candidate runner boundary changed",
    )
    checks.check(
        summary.get("tfe_source_method_candidate_runner_contract_implemented") is True
        and summary.get("tfe_source_method_candidate_runner_contract_rows") == 5
        and summary.get("tfe_source_method_candidate_runner_contract_source_policy_rows_completed") == 0
        and summary.get("tfe_source_method_candidate_runner_contract_method_equivalent") is False
        and summary.get("tfe_source_method_candidate_runner_contract_dae_equivalent") is False,
        "summary TFE source-method candidate contract boundary changed",
    )
    checks.check(
        summary.get("tfe_dae_trajectory_bridge_contract_implemented") is True
        and summary.get("tfe_dae_trajectory_bridge_contract_rows") == 12
        and summary.get("tfe_dae_trajectory_bridge_contract_matched_rows") == 12
        and summary.get("tfe_dae_trajectory_bridge_contract_source_metric_rows") == 12
        and summary.get("tfe_dae_trajectory_bridge_contract_dae_metric_rows") == 12
        and summary.get("tfe_dae_trajectory_bridge_contract_source_policy_rows_completed") == 0
        and summary.get("tfe_dae_trajectory_bridge_contract_dae_runner_equivalent") is False
        and summary.get("tfe_dae_trajectory_bridge_contract_method_runner_equivalent") is False
        and summary.get("tfe_dae_trajectory_bridge_contract_monolithic_integrator") is False
        and summary.get("tfe_dae_trajectory_bridge_contract_all_rows_finite") is True
        and summary.get("tfe_dae_trajectory_bridge_contract_all_dae_residuals_below_1e_10") is True
        and summary.get("tfe_dae_trajectory_bridge_contract_accepted_use")
        == "dae_trajectory_bridge_contract_not_source_policy",
        "summary TFE DAE trajectory bridge contract boundary changed",
    )
    checks.check(
        summary.get("tfe_candidate_frictional_dae_trajectory_contract_implemented") is True
        and summary.get("tfe_candidate_frictional_dae_trajectory_contract_rows") == 12
        and summary.get("tfe_candidate_frictional_dae_trajectory_contract_step_residual_rows") == 56
        and summary.get("tfe_candidate_frictional_dae_trajectory_contract_source_policy_rows_completed") == 0
        and summary.get("tfe_candidate_frictional_dae_trajectory_contract_dae_runner_equivalent") is False
        and summary.get("tfe_candidate_frictional_dae_trajectory_contract_method_runner_equivalent") is False
        and summary.get(
            "tfe_candidate_frictional_dae_trajectory_contract_brown_mcphee_source_code_equivalent_law"
        )
        is False
        and summary.get("tfe_candidate_frictional_dae_trajectory_contract_monolithic_integrator") is False
        and summary.get("tfe_candidate_frictional_dae_trajectory_contract_all_rows_finite") is True
        and summary.get(
            "tfe_candidate_frictional_dae_trajectory_contract_all_dae_residuals_below_1e_9"
        )
        is True
        and summary.get(
            "tfe_candidate_frictional_dae_trajectory_contract_all_friction_power_nonpositive"
        )
        is True,
        "summary TFE candidate-friction DAE trajectory contract boundary changed",
    )
    checks.check(
        summary.get("tfe_brown_mcphee_transition_velocity_sensitivity_rows")
        == transition_sensitivity.get("endpoint_delta_row_count")
        == 3
        and summary.get("tfe_brown_mcphee_transition_velocity_sensitivity_contract_rows")
        == transition_sensitivity.get("contract_row_count")
        == 36
        and summary.get("tfe_brown_mcphee_transition_velocity_sensitivity_source_policy_rows_completed")
        == transition_sensitivity.get("source_policy_rows_completed")
        == 0
        and summary.get("tfe_brown_mcphee_transition_velocity_sensitivity_material") is True
        and summary.get("tfe_brown_mcphee_transition_velocity_sensitivity_equivalence_flags_false")
        is True,
        "summary TFE Brown-McPhee transition-velocity sensitivity boundary changed",
    )
    checks.check(
        float(summary.get("tfe_brown_mcphee_transition_velocity_sensitivity_max_coordinate_delta", 0.0))
        > 1.0e-6
        and float(summary.get("tfe_brown_mcphee_transition_velocity_sensitivity_max_velocity_delta", 0.0))
        > 1.0e-4,
        "summary TFE Brown-McPhee transition-velocity sensitivity deltas too small",
    )
    checks.check(
        summary.get("tfe_brown_mcphee_source_code_equivalence_certificate_status")
        == tfe_brown_mcphee_certificate.get("status")
        == "negative_source_code_equivalence_certificate_not_source_policy"
        and summary.get("tfe_brown_mcphee_source_code_equivalence_certificate_available") is True
        and summary.get("tfe_brown_mcphee_source_code_equivalence_certificate_positive") is False
        and summary.get("tfe_brown_mcphee_source_code_equivalence_certificate_nonheavy_block_closed")
        is False,
        "summary TFE Brown-McPhee source-code equivalence certificate boundary changed",
    )
    checks.check(
        summary.get("tfe_brown_mcphee_source_code_equivalence_certificate_source_policy_execution_invoked")
        == tfe_brown_mcphee_certificate.get("source_policy_execution_invoked")
        is False
        and summary.get("tfe_brown_mcphee_source_code_equivalence_certificate_can_close_now")
        == tfe_brown_mcphee_certificate.get("can_close_now")
        is False,
        "summary TFE Brown-McPhee source-code equivalence certificate closure flags changed",
    )
    checks.check(
        oc6_observed.get("tfe_self_reproduction_status")
        == tfe_self_reproduction.get("status")
        == "attempted_not_reproducible_not_promoted"
        and oc6_observed.get("tfe_self_reproduction_attempted_not_reproducible_rows")
        == tfe_self_reproduction.get("attempted_not_reproducible_rows")
        == 16
        and oc6_observed.get("tfe_self_reproduction_unable_to_reproduce_rows")
        == tfe_self_reproduction.get("unable_to_reproduce_rows")
        == 16
        and oc6_observed.get("tfe_self_reproduction_source_policy_closed")
        == tfe_self_reproduction.get("source_policy_closed")
        is False
        and oc6_observed.get("tfe_self_reproduction_source_policy_closed_ratio")
        == tfe_self_reproduction.get("source_policy_closed_ratio")
        == "0/16"
        and oc6_observed.get("tfe_self_reproduction_source_policy_closed_rows")
        == tfe_self_reproduction.get("source_policy_closed_rows")
        == 0
        and oc6_observed.get("tfe_self_reproduction_public_code_recheck_status")
        == tfe_self_reproduction.get("public_code_recheck_status")
        == "public_code_rechecked_no_distinct_tfe_code_artifact_attempted_not_reproducible"
        and oc6_observed.get("tfe_self_reproduction_reopen_condition")
        == tfe_self_reproduction.get("reopen_condition")
        == "new_public_or_source_code_equivalent_tfe_implementation_artifact"
        and oc6_observed.get("tfe_self_reproduction_preflight_status")
        == tfe_self_reproduction.get("source_policy_execution_preflight_status")
        == "terminal_no_public_code_self_reproduction_attempted_not_promoted"
        and oc6_observed.get("tfe_self_reproduction_preflight_ready_now")
        == tfe_self_reproduction.get("source_policy_execution_preflight_ready_now")
        is False
        and oc6_observed.get("tfe_self_reproduction_preflight_can_promote_rows_now")
        == tfe_self_reproduction.get("source_policy_execution_preflight_can_promote_rows_now")
        is False,
        "OC6 observed TFE self-reproduction terminal aliases missing",
    )
    checks.check(
        oc6_observed.get("tfe_public_code_refresh_20260620_status")
        == source_policy_public_code_refresh.get("status")
        == "public_code_refresh_20260620_no_positive_new_source_artifact_rows_remain_unable_to_reproduce"
        and oc6_observed.get("tfe_public_code_refresh_20260620_rows")
        == source_policy_public_code_refresh.get("rows")
        == 20
        and oc6_observed.get("tfe_public_code_refresh_20260620_current_queries")
        == source_policy_public_code_refresh.get("current_queries")
        == 11
        and oc6_observed.get("tfe_public_code_refresh_20260620_positive_artifact_rows")
        == source_policy_public_code_refresh.get("positive_public_code_artifact_rows")
        == 0
        and oc6_observed.get("tfe_public_code_refresh_20260620_source_policy_closed")
        == source_policy_public_code_refresh.get("source_policy_closed")
        is False
        and oc6_observed.get("tfe_public_code_refresh_20260620_source_policy_closed_ratio")
        == source_policy_public_code_refresh.get("source_policy_closed_ratio")
        == "0/20",
        "OC6 observed TFE public-code refresh aliases missing",
    )
    checks.check(
        "SOURCE_POLICY_REOPEN_CONDITION_MONITOR_20260620.json"
        in by_id.get("OC6", {}).get("evidence", []),
        "OC6 missing source-policy reopen monitor evidence",
    )
    checks.check(
        oc6_observed.get("oc6_tfe_publisher_artifact_availability_20260621_status")
        == summary.get("oc6_tfe_publisher_artifact_availability_20260621_status")
        == oc6_publisher_availability.get("status")
        == "publisher_article_checked_no_code_or_supplement_source_artifact_found"
        and oc6_observed.get("oc6_tfe_publisher_artifact_availability_20260621_date")
        == summary.get("oc6_tfe_publisher_artifact_availability_20260621_date")
        == "2026-06-21"
        and oc6_observed.get("oc6_tfe_publisher_artifact_availability_20260621_official_article_checked")
        == summary.get("oc6_tfe_publisher_artifact_availability_20260621_official_article_checked")
        is True
        and oc6_observed.get("oc6_tfe_publisher_artifact_availability_20260621_source_artifact_signal_count")
        == summary.get("oc6_tfe_publisher_artifact_availability_20260621_source_artifact_signal_count")
        == 0
        and oc6_observed.get("oc6_tfe_publisher_artifact_availability_20260621_positive_artifact_rows")
        == summary.get("oc6_tfe_publisher_artifact_availability_20260621_positive_artifact_rows")
        == 0
        and oc6_observed.get("oc6_tfe_publisher_artifact_availability_20260621_source_equivalent_artifact_rows")
        == summary.get("oc6_tfe_publisher_artifact_availability_20260621_source_equivalent_artifact_rows")
        == 0
        and oc6_observed.get("oc6_tfe_publisher_artifact_availability_20260621_source_policy_rows_closed")
        == summary.get("oc6_tfe_publisher_artifact_availability_20260621_source_policy_rows_closed")
        == 0
        and oc6_observed.get("oc6_tfe_publisher_artifact_availability_20260621_reopen_triggered")
        == summary.get("oc6_tfe_publisher_artifact_availability_20260621_reopen_triggered")
        is False
        and oc6_observed.get("oc6_tfe_publisher_artifact_availability_20260621_global_absence_proved")
        == summary.get("oc6_tfe_publisher_artifact_availability_20260621_global_absence_proved")
        is False,
        "OC6 observed publisher artifact availability aliases missing",
    )
    checks.check(
        oc6_observed.get("oc6_tfe_source_equivalent_artifact_request_packet_20260621_status")
        == summary.get("oc6_tfe_source_equivalent_artifact_request_packet_20260621_status")
        == oc6_source_equivalent_request_packet.get("status")
        == "request_packet_ready_not_sent_no_source_policy_closure"
        and oc6_observed.get("oc6_tfe_source_equivalent_artifact_request_packet_20260621_date")
        == summary.get("oc6_tfe_source_equivalent_artifact_request_packet_20260621_date")
        == "2026-06-21"
        and oc6_observed.get("oc6_tfe_source_equivalent_artifact_request_packet_20260621_request_ready")
        == summary.get("oc6_tfe_source_equivalent_artifact_request_packet_20260621_request_ready")
        is True
        and oc6_observed.get("oc6_tfe_source_equivalent_artifact_request_packet_20260621_request_sent")
        == summary.get("oc6_tfe_source_equivalent_artifact_request_packet_20260621_request_sent")
        is False
        and oc6_observed.get("oc6_tfe_source_equivalent_artifact_request_packet_20260621_requested_artifact_count")
        == summary.get("oc6_tfe_source_equivalent_artifact_request_packet_20260621_requested_artifact_count")
        == 7
        and oc6_observed.get("oc6_tfe_source_equivalent_artifact_request_packet_20260621_corresponding_author_email")
        == summary.get("oc6_tfe_source_equivalent_artifact_request_packet_20260621_corresponding_author_email")
        == "ekanshchat96@vt.edu"
        and oc6_observed.get("oc6_tfe_source_equivalent_artifact_request_packet_20260621_source_policy_rows_closed")
        == summary.get("oc6_tfe_source_equivalent_artifact_request_packet_20260621_source_policy_rows_closed")
        == 0
        and oc6_observed.get("oc6_tfe_source_equivalent_artifact_request_packet_20260621_reopen_triggered")
        == summary.get("oc6_tfe_source_equivalent_artifact_request_packet_20260621_reopen_triggered")
        is False
        and oc6_observed.get("oc6_tfe_source_equivalent_artifact_request_packet_20260621_global_absence_proved")
        == summary.get("oc6_tfe_source_equivalent_artifact_request_packet_20260621_global_absence_proved")
        is False
        and oc6_observed.get("oc6_tfe_source_equivalent_artifact_request_packet_20260621_submission_ready")
        == summary.get("oc6_tfe_source_equivalent_artifact_request_packet_20260621_submission_ready")
        is False,
        "OC6 observed source-equivalent artifact request packet aliases missing",
    )
    checks.check(
        oc6_observed.get("source_policy_reopen_condition_monitor_status")
        == summary.get("source_policy_reopen_condition_monitor_status")
        == source_policy_reopen_monitor.get("status")
        == "reopen_conditions_monitored_no_positive_source_artifact_source_policy_open"
        and oc6_observed.get("source_policy_reopen_condition_monitor_source_policy_closed")
        == summary.get("source_policy_reopen_condition_monitor_source_policy_closed")
        == source_policy_reopen_monitor.get("source_policy_closed")
        is False
        and oc6_observed.get("source_policy_reopen_condition_monitor_source_policy_closed_ratio")
        == summary.get("source_policy_reopen_condition_monitor_source_policy_closed_ratio")
        == source_policy_reopen_monitor.get("source_policy_closed_ratio")
        == "0/20"
        and oc6_observed.get("source_policy_reopen_condition_monitor_local_scan_digest")
        == summary.get("source_policy_reopen_condition_monitor_local_scan_digest")
        == source_policy_reopen_monitor.get("local_scan_digest")
        and oc6_observed.get("source_policy_reopen_condition_monitor_evidence_digest")
        == summary.get("source_policy_reopen_condition_monitor_evidence_digest")
        == source_policy_reopen_monitor.get("monitor_evidence_digest"),
        "OC6 source-policy reopen monitor digest aliases missing",
    )
    checks.check(
        summary.get("tfe_runner_contract_preflight_status")
        == oc6_observed.get("tfe_runner_contract_preflight_status")
        == tfe_runner_contract_preflight.get("status")
        == "contract_entrypoints_callable_candidate_backed_source_policy_open"
        and summary.get("tfe_runner_contract_preflight_entrypoints")
        == oc6_observed.get("tfe_runner_contract_preflight_entrypoints")
        == "3/3"
        and summary.get("tfe_runner_contract_preflight_candidate_backed")
        == oc6_observed.get("tfe_runner_contract_preflight_candidate_backed")
        == "3/3"
        and summary.get("tfe_runner_contract_preflight_source_policy_rows_completed")
        == oc6_observed.get("tfe_runner_contract_preflight_source_policy_rows_completed")
        == tfe_runner_contract_preflight.get("source_policy_rows_completed")
        == 0
        and summary.get("tfe_runner_contract_preflight_execution_blocks")
        == oc6_observed.get("tfe_runner_contract_preflight_execution_blocks")
        == tfe_runner_contract_preflight.get("source_policy_execution_block_count")
        == 4
        and oc6_observed.get("tfe_runner_contract_preflight_safe_use")
        == tfe_runner_contract_preflight.get("safe_current_use")
        == "runner_contract_preflight_only_not_source_policy_reproduction",
        "OC6 observed TFE runner contract preflight boundary missing",
    )
    checks.check(
        by_id.get("OC6", {}).get("observed", {}).get("dae_trajectory_bridge_contract_implemented") is True
        and by_id.get("OC6", {}).get("observed", {}).get("tfe_dae_runner_contract_gap_status")
        == tfe_dae_gap.get("status")
        and by_id.get("OC6", {}).get("observed", {}).get(
            "tfe_dae_runner_contract_gap_missing_block_count"
        )
        == 6
        and by_id.get("OC6", {}).get("observed", {}).get(
            "tfe_dae_runner_contract_gap_missing_block_ids"
        )
        == expected_tfe_dae_gap_ids
        and by_id.get("OC6", {}).get("observed", {}).get(
            "tfe_dae_runner_contract_gap_nonheavy_blocks"
        )
        == tfe_dae_gap.get("nonheavy_missing_contract_blocks")
        and by_id.get("OC6", {}).get("observed", {}).get(
            "tfe_dae_runner_contract_gap_nonheavy_disposition_ids"
        )
        == expected_tfe_dae_nonheavy_gap_ids
        and by_id.get("OC6", {}).get("observed", {}).get(
            "tfe_dae_runner_contract_gap_nonheavy_dispositioned_by_demotion"
        )
        is True
        and by_id.get("OC6", {}).get("observed", {}).get(
            "tfe_dae_runner_contract_gap_nonheavy_demotion_does_not_close_source_policy"
        )
        is True
        and by_id.get("OC6", {}).get("observed", {}).get(
            "tfe_dae_runner_contract_gap_terminal_nonpromoted_blocks"
        )
        == expected_tfe_dae_nonheavy_gap_ids
        and by_id.get("OC6", {}).get("observed", {}).get(
            "tfe_dae_runner_contract_gap_terminal_nonpromoted_block_count"
        )
        == 2
        and by_id.get("OC6", {}).get("observed", {}).get(
            "tfe_dae_runner_contract_gap_effective_missing_blocks"
        )
        == expected_tfe_dae_execution_gap_ids
        and by_id.get("OC6", {}).get("observed", {}).get(
            "tfe_dae_runner_contract_gap_effective_missing_block_count"
        )
        == 4
        and by_id.get("OC6", {}).get("observed", {}).get(
            "tfe_dae_runner_contract_gap_block_accounting", {}
        ).get("source_policy_rows_closed_by_accounting")
        == 0
        and by_id.get("OC6", {}).get("observed", {}).get(
            "tfe_dae_runner_contract_gap_execution_blocks"
        )
        == tfe_dae_gap.get("source_policy_execution_missing_contract_blocks")
        and by_id.get("OC6", {}).get("observed", {}).get(
            "tfe_dae_runner_contract_gap_execution_block_count"
        )
        == 4
        and by_id.get("OC6", {}).get("observed", {}).get(
            "tfe_dae_runner_contract_gap_candidate_backed_non_equivalent_runner_blocks"
        )
        == tfe_dae_gap.get("candidate_backed_non_equivalent_runner_block_ids")
        == [
            "pendulum_absolute_coordinate_source_policy_dae_runner_missing",
            "tfe_newmark_trapezoidal_source_policy_method_runners_missing",
            "gauss6_fullva_absolute_coordinate_source_policy_runner_missing",
        ]
        and by_id.get("OC6", {}).get("observed", {}).get(
            "tfe_dae_runner_contract_gap_candidate_backed_non_equivalent_runner_block_count"
        )
        == tfe_dae_gap.get("candidate_backed_non_equivalent_runner_block_count")
        == 3
        and by_id.get("OC6", {}).get("observed", {}).get(
            "tfe_dae_runner_contract_gap_ready_to_execute_source_policy_now"
        )
        is False
        and by_id.get("OC6", {}).get("observed", {}).get(
            "tfe_dae_runner_contract_gap_heavy_run_invoked"
        )
        is False
        and by_id.get("OC6", {}).get("observed", {}).get(
            "tfe_source_policy_execution_preflight_status"
        )
        == tfe_execution_preflight.get("status")
        == "terminal_no_public_code_self_reproduction_attempted_not_promoted"
        and by_id.get("OC6", {}).get("observed", {}).get(
            "tfe_source_policy_execution_preflight_current_route"
        )
        == tfe_execution_preflight.get("current_route")
        == "no_public_code_self_reproduction_attempted_unable_to_reproduce_not_promoted"
        and by_id.get("OC6", {}).get("observed", {}).get(
            "tfe_source_policy_execution_preflight_reopen_condition"
        )
        == tfe_execution_preflight.get("reopen_condition")
        == "new_public_or_source_code_equivalent_tfe_implementation_artifact"
        and by_id.get("OC6", {}).get("observed", {}).get(
            "tfe_source_policy_execution_preflight_opt_in_required"
        )
        == tfe_execution_preflight.get("explicit_user_opt_in_required")
        is False
        and by_id.get("OC6", {}).get("observed", {}).get(
            "tfe_source_policy_execution_preflight_nonheavy_dispositioned"
        )
        == tfe_execution_preflight.get("nonheavy_blocks_dispositioned_by_demotion")
        is True
        and by_id.get("OC6", {}).get("observed", {}).get(
            "tfe_source_policy_execution_preflight_execution_block_count"
        )
        == tfe_execution_preflight.get("execution_block_count")
        == 4
        and by_id.get("OC6", {}).get("observed", {}).get(
            "tfe_source_policy_execution_preflight_can_promote_rows_now"
        )
        == tfe_execution_preflight.get("can_promote_any_tfe_source_policy_row_now")
        is False
        and by_id.get("OC6", {}).get("observed", {}).get(
            "tfe_source_policy_execution_preflight_ready_now"
        )
        == tfe_execution_preflight.get("ready_to_execute_source_policy_now")
        is False
        and by_id.get("OC6", {}).get("observed", {}).get("dae_trajectory_bridge_contract_rows") == 12
        and by_id.get("OC6", {}).get("observed", {}).get("dae_trajectory_bridge_contract_matched_rows") == 12
        and by_id.get("OC6", {}).get("observed", {}).get(
            "dae_trajectory_bridge_contract_source_policy_rows_completed"
        )
        == 0
        and by_id.get("OC6", {}).get("observed", {}).get("dae_trajectory_bridge_contract_dae_runner_equivalent")
        is False
        and by_id.get("OC6", {}).get("observed", {}).get(
            "dae_trajectory_bridge_contract_method_runner_equivalent"
        )
        is False
        and by_id.get("OC6", {}).get("observed", {}).get(
            "dae_trajectory_bridge_contract_monolithic_integrator"
        )
        is False,
        "OC6 observed TFE DAE trajectory bridge contract boundary missing",
    )
    checks.check(
        by_id.get("OC6", {}).get("observed", {}).get(
            "candidate_frictional_dae_trajectory_contract_implemented"
        )
        is True
        and by_id.get("OC6", {}).get("observed", {}).get(
            "candidate_frictional_dae_trajectory_contract_rows"
        )
        == 12
        and by_id.get("OC6", {}).get("observed", {}).get(
            "candidate_frictional_dae_trajectory_contract_step_residual_rows"
        )
        == 56
        and by_id.get("OC6", {}).get("observed", {}).get(
            "candidate_frictional_dae_trajectory_contract_source_policy_rows_completed"
        )
        == 0
        and by_id.get("OC6", {}).get("observed", {}).get(
            "candidate_frictional_dae_trajectory_contract_dae_runner_equivalent"
        )
        is False
        and by_id.get("OC6", {}).get("observed", {}).get(
            "candidate_frictional_dae_trajectory_contract_method_runner_equivalent"
        )
        is False
        and by_id.get("OC6", {}).get("observed", {}).get(
            "candidate_frictional_dae_trajectory_contract_brown_mcphee_source_code_equivalent_law"
        )
        is False
        and by_id.get("OC6", {}).get("observed", {}).get(
            "candidate_frictional_dae_trajectory_contract_monolithic_integrator"
        )
        is False,
        "OC6 observed TFE candidate-friction DAE trajectory contract boundary missing",
    )
    checks.check(
        by_id.get("OC6", {}).get("observed", {}).get(
            "brown_mcphee_transition_velocity_sensitivity_rows"
        )
        == 3
        and by_id.get("OC6", {}).get("observed", {}).get(
            "brown_mcphee_transition_velocity_sensitivity_contract_rows"
        )
        == 36
        and by_id.get("OC6", {}).get("observed", {}).get(
            "brown_mcphee_transition_velocity_sensitivity_source_policy_rows_completed"
        )
        == 0
        and by_id.get("OC6", {}).get("observed", {}).get(
            "brown_mcphee_transition_velocity_sensitivity_material"
        )
        is True
        and by_id.get("OC6", {}).get("observed", {}).get(
            "brown_mcphee_transition_velocity_sensitivity_equivalence_flags_false"
        )
        is True,
        "OC6 observed TFE Brown-McPhee transition-velocity sensitivity boundary missing",
    )
    checks.check(
        by_id.get("OC6", {}).get("observed", {}).get(
            "brown_mcphee_source_code_equivalence_certificate_status"
        )
        == tfe_brown_mcphee_certificate.get("status")
        == "negative_source_code_equivalence_certificate_not_source_policy"
        and by_id.get("OC6", {}).get("observed", {}).get(
            "brown_mcphee_source_code_equivalence_certificate_available"
        )
        is True
        and by_id.get("OC6", {}).get("observed", {}).get(
            "brown_mcphee_source_code_equivalence_certificate_positive"
        )
        is False
        and by_id.get("OC6", {}).get("observed", {}).get(
            "brown_mcphee_source_code_equivalence_certificate_nonheavy_block_closed"
        )
        is False,
        "OC6 observed TFE Brown-McPhee source-code equivalence certificate boundary missing",
    )
    checks.check(
        by_id.get("OC6", {}).get("observed", {}).get(
            "brown_mcphee_source_code_equivalence_certificate_source_policy_execution_invoked"
        )
        == tfe_brown_mcphee_certificate.get("source_policy_execution_invoked")
        is False
        and by_id.get("OC6", {}).get("observed", {}).get(
            "brown_mcphee_source_code_equivalence_certificate_can_close_now"
        )
        == tfe_brown_mcphee_certificate.get("can_close_now")
        is False,
        "OC6 observed TFE Brown-McPhee source-code equivalence certificate closure flags missing",
    )
    checks.check(
        by_id.get("OC6", {}).get("observed", {}).get(
            "full_T10_endpoint_policy_closure_certificate_status"
        )
        == tfe_endpoint_certificate.get("status")
        == "negative_full_T10_endpoint_policy_certificate_not_source_policy"
        and by_id.get("OC6", {}).get("observed", {}).get(
            "full_T10_endpoint_policy_closure_certificate_available"
        )
        is True
        and by_id.get("OC6", {}).get("observed", {}).get(
            "full_T10_endpoint_policy_closure_certificate_positive"
        )
        is False
        and by_id.get("OC6", {}).get("observed", {}).get(
            "full_T10_endpoint_policy_closure_certificate_nonheavy_block_closed"
        )
        is False,
        "OC6 observed TFE full-T10 endpoint policy closure certificate boundary missing",
    )
    checks.check(
        by_id.get("OC6", {}).get("observed", {}).get(
            "full_T10_endpoint_policy_closure_certificate_source_policy_execution_invoked"
        )
        == tfe_endpoint_certificate.get("source_policy_execution_invoked")
        is False
        and by_id.get("OC6", {}).get("observed", {}).get(
            "full_T10_endpoint_policy_closure_certificate_can_close_now"
        )
        == tfe_endpoint_certificate.get("can_close_now")
        is False,
        "OC6 observed TFE full-T10 endpoint policy closure certificate closure flags missing",
    )
    checks.check(
        by_id.get("OC6", {}).get("observed", {}).get("gauss6_fullva_dae_candidate_contract_implemented")
        is True
        and by_id.get("OC6", {}).get("observed", {}).get("gauss6_fullva_dae_candidate_contract_rows")
        == 1
        and by_id.get("OC6", {}).get("observed", {}).get(
            "gauss6_fullva_dae_candidate_contract_source_policy_rows_completed"
        )
        == 0
        and by_id.get("OC6", {}).get("observed", {}).get(
            "gauss6_fullva_dae_candidate_contract_dae_equivalent"
        )
        is False
        and by_id.get("OC6", {}).get("observed", {}).get(
            "gauss6_fullva_dae_candidate_contract_fullva_dae_equivalent"
        )
        is False,
        "OC6 observed Gauss6 DAE candidate contract boundary missing",
    )
    checks.check(
        summary.get("gauss6_fullva_source_pendulum_candidate_smoke_implemented") is True
        and summary.get("gauss6_fullva_absolute_coordinate_source_policy_runner_implemented") is False
        and summary.get("gauss6_fullva_on_source_pendulum_implemented") is True
        and summary.get("gauss6_fullva_source_pendulum_candidate_rows") == 2
        and summary.get("gauss6_fullva_source_pendulum_candidate_source_policy_rows_completed") == 0
        and summary.get("gauss6_fullva_source_pendulum_candidate_method_equivalent") is False
        and summary.get("gauss6_fullva_dae_candidate_contract_implemented") is True
        and summary.get("gauss6_fullva_dae_candidate_contract_rows") == 1
        and summary.get("gauss6_fullva_dae_candidate_contract_source_policy_rows_completed") == 0
        and summary.get("gauss6_fullva_dae_candidate_contract_dae_equivalent") is False
        and summary.get("gauss6_fullva_dae_candidate_contract_fullva_dae_equivalent") is False,
        "summary Gauss6 source-pendulum candidate boundary changed",
    )
    checks.check(
        summary.get("bounded_source_policy_runner_smoke_implemented") is True
        and summary.get("bounded_source_policy_runner_rows") == 4
        and summary.get("bounded_source_policy_runner_full_T10") is False
        and summary.get("bounded_source_policy_runner_source_policy_rows_completed") == 0,
        "summary bounded runner boundary changed",
    )
    checks.check(
        summary.get("tfe_source_grid_policy_resolved_for_full_T10")
        == tfe_grid.get("source_grid_policy_resolved_for_full_T10")
        is False
        and summary.get("tfe_source_grid_integer_step_incompatible_rows")
        == tfe_grid.get("integer_step_incompatible_rows")
        == 4,
        "summary TFE source grid boundary changed",
    )
    checks.check(
        summary.get("tfe_source_grid_exact_T_compatible_rows_endpoint_convention_resolved")
        == tfe_grid.get("endpoint_compatible_rows_source_endpoint_convention_resolved")
        == 2
        and summary.get("tfe_source_grid_endpoint_incompatible_rows_requiring_policy")
        == tfe_grid.get("endpoint_incompatible_rows_require_source_endpoint_policy")
        == 4
        and summary.get("tfe_source_grid_policy_resolved_for_exact_T_compatible_rows")
        == tfe_grid.get("source_grid_policy_resolved_for_exact_T_compatible_rows")
        is True,
        "summary TFE exact-T endpoint-grid subclosure changed",
    )
    checks.check(
        summary.get("tfe_source_grid_source_text_available")
        == tfe_grid.get("source_text_endpoint_convention_audit", {}).get("source_text_available")
        is True
        and summary.get("tfe_source_grid_source_text_anchor_count")
        == tfe_grid.get("source_text_endpoint_convention_audit", {}).get("anchor_count")
        >= 8
        and summary.get("tfe_source_grid_algorithm_literal_fixed_h")
        == tfe_grid.get("source_text_endpoint_convention_audit", {}).get(
            "algorithm_literal_constant_h_until_tn_ge_tfinal"
        )
        is True
        and summary.get("tfe_source_grid_endpoint_convention_resolved_for_error_sampling")
        == tfe_grid.get("source_text_endpoint_convention_audit", {}).get(
            "source_endpoint_convention_resolved_for_error_sampling"
        )
        is False,
        "summary TFE source-text endpoint convention boundary changed",
    )
    checks.check(
        summary.get("tfe_endpoint_boundary_certificate_status")
        == tfe_endpoint_boundary.get("status")
        == "endpoint_policy_literal_overrun_bound_proved_source_policy_open",
        "summary TFE endpoint boundary certificate status changed",
    )
    checks.check(
        summary.get("tfe_endpoint_boundary_literal_overrun_bound_proved") is True
        and tfe_endpoint_boundary.get("theorem", {}).get("name")
        == "fixed_h_until_final_time_endpoint_bound",
        "summary TFE endpoint boundary theorem not carried",
    )
    checks.check(
        summary.get("tfe_endpoint_boundary_literal_exact_T_rows")
        == tfe_endpoint_boundary.get("algorithm_literal_exact_T_row_count")
        == 2
        and summary.get("tfe_endpoint_boundary_literal_overrun_rows")
        == tfe_endpoint_boundary.get("algorithm_literal_overrun_row_count")
        == 4,
        "summary TFE endpoint boundary row counts changed",
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
        "summary TFE endpoint boundary overclosed source-policy endpoint policy",
    )
    checks.check(
        summary.get("tfe_full_T10_endpoint_policy_closure_certificate_status")
        == tfe_endpoint_certificate.get("status")
        == "negative_full_T10_endpoint_policy_certificate_not_source_policy"
        and summary.get("tfe_full_T10_endpoint_policy_closure_certificate_available") is True
        and summary.get("tfe_full_T10_endpoint_policy_closure_certificate_positive") is False
        and summary.get("tfe_full_T10_endpoint_policy_closure_certificate_nonheavy_block_closed")
        is False,
        "summary TFE full-T10 endpoint policy closure certificate boundary changed",
    )
    checks.check(
        summary.get("tfe_full_T10_endpoint_policy_closure_certificate_source_policy_execution_invoked")
        == tfe_endpoint_certificate.get("source_policy_execution_invoked")
        is False
        and summary.get("tfe_full_T10_endpoint_policy_closure_certificate_can_close_now")
        == tfe_endpoint_certificate.get("can_close_now")
        is False,
        "summary TFE full-T10 endpoint policy closure certificate closure flags changed",
    )
    checks.check(
        summary.get("tfe_endpoint_sensitivity_status")
        == tfe_endpoint_sensitivity.get("status")
        == "diagnostic_endpoint_policy_sensitivity_not_source_policy",
        "summary TFE endpoint sensitivity status changed",
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
        "summary TFE endpoint sensitivity counts changed",
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
        "summary TFE endpoint sensitivity overclosed the source-policy boundary",
    )
    checks.check(
        summary.get("tfe_endpoint_sensitivity_default_1e_4_campaign_invoked") is False
        and summary.get("tfe_endpoint_sensitivity_run_v047_invoked") is False,
        "summary TFE endpoint sensitivity invoked a forbidden heavy/default run",
    )
    checks.check(
        summary.get("active_tfe_b2_candidate_row_smoke_implemented") is True
        and summary.get("active_tfe_b2_candidate_row_smoke_full_T10") is False
        and summary.get("active_tfe_b2_source_policy_rows_completed") == 0,
        "summary active B2 smoke boundary changed",
    )
    checks.check(
        summary.get("active_tfe_b2_source_reference_full_T10_candidate_probe_implemented") is True
        and summary.get("active_tfe_b2_source_reference_full_T10_candidate_probe_full_T10") is True
        and summary.get(
            "active_tfe_b2_source_reference_full_T10_candidate_probe_source_policy_reference_invoked"
        )
        is True
        and summary.get(
            "active_tfe_b2_source_reference_full_T10_candidate_probe_source_policy_rows_completed"
        )
        == 0
        and summary.get("active_tfe_b2_source_reference_full_T10_candidate_probe_method_equivalent")
        is False,
        "summary active B2 source-reference full T=10 probe boundary changed",
    )
    checks.check(
        proof.get("closure_state", {}).get("proof_gap_closed") is True
        and proof.get("closure_state", {}).get("stage_residual_O_h7_implementation_defect_proved") is True
        and proof.get("closure_state", {}).get("pc2_closed_by_direct_substitution") is True
        and proof.get("evidence_summary", {}).get("newton_euler_d5_direct_substitution_dynamic_zero_rows") == 36
        and proof.get("evidence_summary", {}).get("newton_euler_d5_direct_substitution_full_stage_rows") == 132
        and proof.get("evidence_summary", {}).get("open_dynamic_rows") == 36
        and proof.get("evidence_summary", {}).get("newton_euler_obligation_coverage_matrix_complete") is True
        and proof.get("evidence_summary", {}).get("newton_euler_row_obligation_links") == 180
        and proof.get("evidence_summary", {}).get("newton_euler_rows_with_complete_obligation_sets") == 36
        and summary.get("proof_closed") is True,
        "proof boundary changed",
    )
    checks.check(
        blocker.get("mechanical_preflight_passed") is True
        and blocker.get("quality_review_passed") is True
        and blocker.get("submission_ready") is False
        and blocker.get("submission_ready_under_narrowed_claim") is True
        and "validator-only compatibility aliases" in blocker.get("narrowed_claim_alias_warning", "")
        and "global submission readiness" in blocker.get("narrowed_claim_alias_warning", "")
        and [item.get("id") for item in blocker.get("blockers", []) if item.get("status") != "closed"]
        == []
        and summary.get("quality_review_closed") is True,
        "quality review boundary changed",
    )
    oc8_observed = by_id.get("OC8", {}).get("observed", {})
    checks.check(
        oc8_observed.get("submission_ready_under_narrowed_claim") is True
        and oc8_observed.get("narrowed_claim_alias_warning") == blocker.get("narrowed_claim_alias_warning")
        and "validator-only compatibility aliases" in oc8_observed.get("narrowed_claim_alias_warning", "")
        and "global submission readiness" in oc8_observed.get("narrowed_claim_alias_warning", ""),
        "OC8 narrowed-claim alias warning missing from objective audit",
    )
    checks.check(
        summary.get("minimal_reproducibility_candidate_present") is True
        and summary.get("minimal_reproducibility_candidate_file_count")
        == minimal_candidate.get("candidate_file_count")
        == 10
        and summary.get("minimal_reproducibility_candidate_python_lines")
        == minimal_candidate.get("candidate_python_line_count"),
        "minimal reproducibility candidate boundary changed",
    )
    checks.check(
        summary.get("combined_python_line_count") == combined_python_line_count,
        "summary combined Python line count is stale",
    )
    checks.check(
        by_id.get("OC12", {}).get("observed", {}).get("paper_python_file_count")
        == paper_code.get("file_count")
        and by_id.get("OC12", {}).get("observed", {}).get("paper_python_line_count")
        == paper_code.get("line_count")
        and by_id.get("OC12", {}).get("observed", {}).get("v048_python_file_count")
        == v048_code.get("file_count")
        and by_id.get("OC12", {}).get("observed", {}).get("v048_python_line_count")
        == v048_code.get("line_count")
        and by_id.get("OC12", {}).get("observed", {}).get("combined_python_line_count")
        == combined_python_line_count,
        "OC12 current Python inventory is stale",
    )
    checks.check(
        f"Combined Python line count: `{combined_python_line_count}`." in audit_md,
        "markdown combined Python line count is stale",
    )
    checks.check(
        by_id.get("OC12", {}).get("observed", {}).get("local_runner_package_partial_ready") is True
        and by_id.get("OC12", {}).get("observed", {}).get("full_source_policy_runner_package_ready") is False
        and by_id.get("OC12", {}).get("observed", {}).get("b6_four_example_source_policy_rows_closed") == 0,
        "OC12 local/full runner boundary changed",
    )
    checks.check(
        by_id.get("OC12", {}).get("observed", {}).get("narrowed_reproducibility_package_ready")
        == narrowed_repro.get("narrowed_claim_reproducibility_package_ready")
        is True
        and by_id.get("OC12", {}).get("observed", {}).get("narrowed_repro_code_archive_ready") is True
        and by_id.get("OC12", {}).get("observed", {}).get("narrowed_repro_code_archive_status")
        == narrowed_repro_code_archive.get("status")
        == "narrowed_repro_code_archive_ready_source_policy_open"
        and by_id.get("OC12", {}).get("observed", {}).get("narrowed_repro_code_archive_entry_count")
        == narrowed_repro_code_archive.get("entry_count")
        and by_id.get("OC12", {}).get("observed", {}).get("narrowed_repro_code_archive_python_files")
        == narrowed_repro_code_archive.get("python_file_count")
        and by_id.get("OC12", {}).get("observed", {}).get("narrowed_repro_code_archive_python_lines")
        == narrowed_repro_code_archive.get("python_line_count"),
        "OC12 narrowed repro code archive inventory changed",
    )
    checks.check(
        by_id.get("OC12", {}).get("observed", {}).get("narrowed_repro_code_archive_source_policy_rows_closed") == 0
        and by_id.get("OC12", {}).get("observed", {}).get("narrowed_repro_code_archive_source_policy_rows_total")
        == 40
        and by_id.get("OC12", {}).get("observed", {}).get("narrowed_repro_code_archive_full_source_policy_ready")
        is False
        and by_id.get("OC12", {}).get("observed", {}).get("narrowed_repro_code_archive_submission_ready")
        is False,
        "OC12 narrowed repro code archive source-policy/submission boundary changed",
    )
    oc12_dependency_boundary = by_id.get("OC12", {}).get("observed", {}).get(
        "minimal_submission_code_dependency_boundary", {}
    )
    checks.check(
        oc12_dependency_boundary.get("schema")
        == "minimal-submission-code-dependency-boundary-v1"
        and oc12_dependency_boundary.get("status")
        == "narrowed_repro_ready_full_source_policy_package_blocked"
        and by_id.get("OC12", {}).get("observed", {}).get(
            "minimal_submission_code_dependency_boundary_status"
        )
        == oc12_dependency_boundary.get("status"),
        "OC12 dependency boundary status changed",
    )
    checks.check(
        oc12_dependency_boundary.get("minimal_reproducible_submission_code_ready") is False
        and oc12_dependency_boundary.get("local_runner_package_partial_ready") is True
        and oc12_dependency_boundary.get("narrowed_claim_reproducibility_package_ready") is True
        and oc12_dependency_boundary.get("narrowed_repro_code_archive_ready") is True
        and oc12_dependency_boundary.get("narrowed_repro_code_archive_submission_ready") is False
        and oc12_dependency_boundary.get("full_source_policy_runner_package_ready") is False,
        "OC12 dependency readiness boundary changed",
    )
    checks.check(
        oc12_dependency_boundary.get("source_policy_closed") is False
        and oc12_dependency_boundary.get("tfe_runner_closed") is False
        and oc12_dependency_boundary.get("source_policy_rows_closed") == 0
        and oc12_dependency_boundary.get("source_policy_rows_total") == 40
        and oc12_dependency_boundary.get("narrowed_archive_source_policy_rows_closed") == 0
        and oc12_dependency_boundary.get("narrowed_archive_source_policy_rows_total") == 40,
        "OC12 dependency source-policy/TFE boundary changed",
    )
    checks.check(
        oc12_dependency_boundary.get("blocking_objective_requirements")
        == by_id.get("OC12", {}).get("observed", {}).get(
            "minimal_submission_code_dependency_blockers"
        )
        == ["OC4", "OC6", "OC12"]
        and oc12_dependency_boundary.get("blocking_upstream_gates")
        == [
            "OC4_source_policy_reproduction_rows",
            "OC6_TFE_source_policy_runner",
            "OC12_full_source_policy_runner_archive",
        ]
        and oc12_dependency_boundary.get("safe_current_package_use")
        == by_id.get("OC12", {}).get("observed", {}).get(
            "minimal_submission_code_dependency_safe_use"
        )
        == "narrowed_claim_replay_and_audit_provenance_only"
        and oc12_dependency_boundary.get("primary_submission_package_allowed") is False,
        "OC12 dependency blocker chain changed",
    )
    checks.check(
        "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json"
        in by_id.get("OC12", {}).get("evidence", []),
        "OC12 missing full source-policy runner archive gap audit evidence",
    )
    checks.check(
        "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json"
        in by_id.get("OC12", {}).get("evidence", []),
        "OC12 missing B4 source-policy execution handoff evidence",
    )
    checks.check(
        by_id.get("OC12", {}).get("observed", {}).get("full_source_policy_runner_archive_gap_status")
        == full_source_runner_gap.get("status")
        == "full_source_policy_runner_archive_not_ready_source_policy_open",
        "OC12 full-source archive gap status changed",
    )
    checks.check(
        summary.get("full_source_policy_runner_archive_gap_status")
        == by_id.get("OC12", {}).get("observed", {}).get("full_source_policy_runner_archive_gap_status")
        == full_source_runner_gap.get("status")
        == "full_source_policy_runner_archive_not_ready_source_policy_open",
        "summary full-source archive gap status changed",
    )
    checks.check(
        by_id.get("OC12", {}).get("observed", {}).get("full_source_policy_runner_archive_gap_ready_now")
        == full_source_runner_gap.get("closure_conditions", {}).get("full_archive_ready_now")
        is False
        and by_id.get("OC12", {}).get("observed", {}).get(
            "full_source_policy_runner_archive_gap_can_use_current_archive"
        )
        == full_source_runner_gap.get("closure_conditions", {}).get(
            "can_use_current_archive_as_full_source_policy_runner_archive"
        )
        is False,
        "OC12 full-source archive readiness boundary changed",
    )
    checks.check(
        by_id.get("OC12", {}).get("observed", {}).get(
            "full_source_policy_runner_archive_gap_safe_current_archive_use"
        )
        == oc12_dependency_boundary.get("safe_current_package_use")
        == "narrowed_claim_replay_and_audit_provenance_only",
        "OC12 full-source archive safe-current-use boundary changed",
    )
    checks.check(
        summary.get("full_source_policy_runner_archive_gap_ready_now")
        == by_id.get("OC12", {}).get("observed", {}).get("full_source_policy_runner_archive_gap_ready_now")
        == full_source_runner_gap.get("closure_conditions", {}).get("full_archive_ready_now")
        is False
        and summary.get("full_source_policy_runner_archive_gap_current_archive_use")
        == by_id.get("OC12", {}).get("observed", {}).get(
            "full_source_policy_runner_archive_gap_can_use_current_archive"
        )
        == full_source_runner_gap.get("closure_conditions", {}).get(
            "can_use_current_archive_as_full_source_policy_runner_archive"
        )
        is False,
        "summary full-source archive readiness boundary changed",
    )
    checks.check(
        summary.get(
            "full_source_policy_runner_archive_gap_can_use_current_archive_as_full_source_policy_runner_archive"
        )
        == summary.get("full_source_policy_runner_archive_gap_current_archive_use")
        == by_id.get("OC12", {}).get("observed", {}).get(
            "full_source_policy_runner_archive_gap_can_use_current_archive"
        )
        == full_source_runner_gap.get("closure_conditions", {}).get(
            "can_use_current_archive_as_full_source_policy_runner_archive"
        )
        is False
        and summary.get("full_source_policy_runner_archive_gap_safe_current_archive_use")
        == by_id.get("OC12", {}).get("observed", {}).get(
            "full_source_policy_runner_archive_gap_safe_current_archive_use"
        )
        == oc12_dependency_boundary.get("safe_current_package_use")
        == "narrowed_claim_replay_and_audit_provenance_only",
        "summary full-source archive safe-current-use aliases changed",
    )
    checks.check(
        by_id.get("OC12", {}).get("observed", {}).get(
            "full_source_policy_runner_archive_gap_source_policy_rows_closed"
        )
        == full_source_runner_gap.get("source_policy_rows", {}).get("closed")
        == 0
        and by_id.get("OC12", {}).get("observed", {}).get(
            "full_source_policy_runner_archive_gap_source_policy_rows_total"
        )
        == full_source_runner_gap.get("source_policy_rows", {}).get("total")
        == 40
        and by_id.get("OC12", {}).get("observed", {}).get(
            "full_source_policy_runner_archive_gap_remaining_rows_to_close"
        )
        == full_source_runner_gap.get("closure_conditions", {}).get("remaining_source_policy_rows_to_close")
        == 40,
        "OC12 full-source archive source-policy row boundary changed",
    )
    checks.check(
        summary.get("full_source_policy_runner_archive_gap_source_policy_rows_closed")
        == by_id.get("OC12", {}).get("observed", {}).get(
            "full_source_policy_runner_archive_gap_source_policy_rows_closed"
        )
        == full_source_runner_gap.get("source_policy_rows", {}).get("closed")
        == 0
        and summary.get("full_source_policy_runner_archive_gap_source_policy_rows_total")
        == by_id.get("OC12", {}).get("observed", {}).get(
            "full_source_policy_runner_archive_gap_source_policy_rows_total"
        )
        == full_source_runner_gap.get("source_policy_rows", {}).get("total")
        == 40
        and summary.get("full_source_policy_runner_archive_gap_remaining_rows_to_close")
        == by_id.get("OC12", {}).get("observed", {}).get(
            "full_source_policy_runner_archive_gap_remaining_rows_to_close"
        )
        == full_source_runner_gap.get("closure_conditions", {}).get("remaining_source_policy_rows_to_close")
        == 40,
        "summary full-source archive source-policy row boundary changed",
    )
    checks.check(
        by_id.get("OC12", {}).get("observed", {}).get(
            "full_source_policy_runner_archive_gap_terminal_unable_rows"
        )
        == full_source_runner_gap.get("closure_conditions", {}).get("terminal_unable_to_reproduce_rows")
        == 20
        and by_id.get("OC12", {}).get("observed", {}).get(
            "full_source_policy_runner_archive_gap_ra_hi_open_rows"
        )
        == full_source_runner_gap.get("closure_conditions", {}).get(
            "ra_hi_rows_requiring_authorized_closeout_or_new_artifact"
        )
        == 20,
        "OC12 full-source archive terminal/open row split changed",
    )
    checks.check(
        summary.get("full_source_policy_runner_archive_gap_terminal_unable_rows")
        == by_id.get("OC12", {}).get("observed", {}).get(
            "full_source_policy_runner_archive_gap_terminal_unable_rows"
        )
        == full_source_runner_gap.get("closure_conditions", {}).get("terminal_unable_to_reproduce_rows")
        == 20
        and summary.get("full_source_policy_runner_archive_gap_ra_hi_open_rows")
        == by_id.get("OC12", {}).get("observed", {}).get(
            "full_source_policy_runner_archive_gap_ra_hi_open_rows"
        )
        == full_source_runner_gap.get("closure_conditions", {}).get(
            "ra_hi_rows_requiring_authorized_closeout_or_new_artifact"
        )
        == 20,
        "summary full-source archive terminal/open row split changed",
    )
    checks.check(
        by_id.get("OC12", {}).get("observed", {}).get(
            "full_source_policy_runner_archive_gap_terminal_reopen_conditions"
        )
        == {
            item.get("suite_id"): item.get("reopen_condition")
            for item in full_source_runner_gap.get("terminal_unable_to_reproduce_suites", [])
            if isinstance(item, dict)
        }
        == expected_full_archive_terminal_reopen_conditions,
        "OC12 full-source archive terminal reopen conditions changed",
    )
    checks.check(
        by_id.get("OC12", {}).get("observed", {}).get(
            "full_source_policy_runner_archive_gap_tfe_reopen_condition"
        )
        == expected_full_archive_terminal_reopen_conditions["tfe2026_original_pendulum"]
        and by_id.get("OC12", {}).get("observed", {}).get(
            "full_source_policy_runner_archive_gap_vp2024_reopen_condition"
        )
        == expected_full_archive_terminal_reopen_conditions["vp2024_velocity_partitioning"]
        and by_id.get("OC12", {}).get("observed", {}).get(
            "full_source_policy_runner_archive_gap_required_approval_statement"
        )
        == full_source_runner_gap.get("ra_hi_closeout_boundary", {}).get("required_user_approval_statement")
        == "I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json.",
        "OC12 full-source archive reopen/approval boundary changed",
    )
    checks.check(
        summary.get("full_source_policy_runner_archive_gap_terminal_reopen_conditions")
        == expected_full_archive_terminal_reopen_conditions
        and summary.get("full_source_policy_runner_archive_gap_tfe_reopen_condition")
        == expected_full_archive_terminal_reopen_conditions["tfe2026_original_pendulum"]
        and summary.get("full_source_policy_runner_archive_gap_vp2024_reopen_condition")
        == expected_full_archive_terminal_reopen_conditions["vp2024_velocity_partitioning"]
        and summary.get("full_source_policy_runner_archive_gap_required_approval_statement")
        == "I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json.",
        "summary full-source archive reopen/approval boundary changed",
    )
    expected_archive_reopen_monitor = full_source_runner_gap.get("reopen_condition_monitor", {})
    checks.check(
        by_id.get("OC12", {}).get("observed", {}).get(
            "full_source_policy_runner_archive_gap_reopen_monitor_status"
        )
        == summary.get("full_source_policy_runner_archive_gap_reopen_monitor_status")
        == expected_archive_reopen_monitor.get("status")
        == source_policy_reopen_monitor.get("status")
        == "reopen_conditions_monitored_no_positive_source_artifact_source_policy_open"
        and by_id.get("OC12", {}).get("observed", {}).get(
            "full_source_policy_runner_archive_gap_reopen_monitor_source_policy_closed"
        )
        == summary.get("full_source_policy_runner_archive_gap_reopen_monitor_source_policy_closed")
        == expected_archive_reopen_monitor.get("source_policy_closed")
        == source_policy_reopen_monitor.get("source_policy_closed")
        is False
        and by_id.get("OC12", {}).get("observed", {}).get(
            "full_source_policy_runner_archive_gap_reopen_monitor_source_policy_closed_ratio"
        )
        == summary.get(
            "full_source_policy_runner_archive_gap_reopen_monitor_source_policy_closed_ratio"
        )
        == expected_archive_reopen_monitor.get("source_policy_closed_ratio")
        == source_policy_reopen_monitor.get("source_policy_closed_ratio")
        == "0/20"
        and by_id.get("OC12", {}).get("observed", {}).get(
            "full_source_policy_runner_archive_gap_reopen_monitor_local_scan_digest"
        )
        == summary.get("full_source_policy_runner_archive_gap_reopen_monitor_local_scan_digest")
        == expected_archive_reopen_monitor.get("local_scan_digest")
        == source_policy_reopen_monitor.get("local_scan_digest")
        and by_id.get("OC12", {}).get("observed", {}).get(
            "full_source_policy_runner_archive_gap_reopen_monitor_evidence_digest"
        )
        == summary.get("full_source_policy_runner_archive_gap_reopen_monitor_evidence_digest")
        == expected_archive_reopen_monitor.get("monitor_evidence_digest")
        == source_policy_reopen_monitor.get("monitor_evidence_digest"),
        "OC12 full-source archive reopen-monitor digest boundary changed",
    )
    archive_action_boundary = full_source_runner_gap.get("action_boundary", {})
    expected_safe_archive_action_ids = [
        "rebuild_read_only_audit_chain",
        "rerun_read_only_validators",
        "keep_narrowed_archive_provenance_only",
        "monitor_reopen_conditions",
    ]
    expected_opt_in_archive_action_ids = ["authorized_b4_ra_hi_source_policy_execution"]
    oc12_observed = by_id.get("OC12", {}).get("observed", {})
    checks.check(
        oc12_observed.get("full_source_policy_runner_archive_gap_action_boundary")
        == summary.get("full_source_policy_runner_archive_gap_action_boundary")
        == archive_action_boundary,
        "OC12 full-source archive action boundary not propagated",
    )
    checks.check(
        oc12_observed.get("full_source_policy_runner_archive_gap_safe_without_b4_opt_in_count")
        == summary.get("full_source_policy_runner_archive_gap_safe_without_b4_opt_in_count")
        == full_source_runner_gap.get("safe_without_b4_opt_in_count")
        == 4
        and oc12_observed.get("full_source_policy_runner_archive_gap_opt_in_required_action_count")
        == summary.get("full_source_policy_runner_archive_gap_opt_in_required_action_count")
        == full_source_runner_gap.get("opt_in_required_action_count")
        == 1,
        "OC12 full-source archive action counts changed",
    )
    checks.check(
        archive_action_boundary.get("safe_without_b4_opt_in_count")
        == full_source_runner_gap.get("safe_without_b4_opt_in_count")
        and archive_action_boundary.get("opt_in_required_action_count")
        == full_source_runner_gap.get("opt_in_required_action_count"),
        "full-source archive action count aliases changed",
    )
    checks.check(
        oc12_observed.get("full_source_policy_runner_archive_gap_source_policy_execution_allowed_now")
        == summary.get("full_source_policy_runner_archive_gap_source_policy_execution_allowed_now")
        == full_source_runner_gap.get("source_policy_execution_allowed_now")
        is False
        and oc12_observed.get("full_source_policy_runner_archive_gap_source_policy_execution_invoked")
        == summary.get("full_source_policy_runner_archive_gap_source_policy_execution_invoked")
        == full_source_runner_gap.get("source_policy_execution_invoked")
        is False
        and oc12_observed.get(
            "full_source_policy_runner_archive_gap_exact_b4_opt_in_required_for_execution"
        )
        == summary.get("full_source_policy_runner_archive_gap_exact_b4_opt_in_required_for_execution")
        == full_source_runner_gap.get("exact_b4_opt_in_required_for_execution")
        is True,
        "OC12 full-source archive action permission boundary changed",
    )
    checks.check(
        archive_action_boundary.get("source_policy_execution_allowed_now")
        == full_source_runner_gap.get("source_policy_execution_allowed_now")
        and archive_action_boundary.get("exact_b4_opt_in_required_for_execution")
        == full_source_runner_gap.get("exact_b4_opt_in_required_for_execution"),
        "full-source archive execution permission aliases changed",
    )
    checks.check(
        oc12_observed.get("full_source_policy_runner_archive_gap_opt_in_required_command_count")
        == summary.get("full_source_policy_runner_archive_gap_opt_in_required_command_count")
        == full_source_runner_gap.get("opt_in_required_command_count")
        == 13
        and oc12_observed.get("full_source_policy_runner_archive_gap_opt_in_required_mapped_external_rows")
        == summary.get("full_source_policy_runner_archive_gap_opt_in_required_mapped_external_rows")
        == full_source_runner_gap.get("opt_in_required_mapped_external_rows")
        == 20,
        "OC12 full-source archive action command boundary changed",
    )
    checks.check(
        archive_action_boundary.get("opt_in_required_command_count")
        == full_source_runner_gap.get("opt_in_required_command_count")
        and archive_action_boundary.get("opt_in_required_mapped_external_rows")
        == full_source_runner_gap.get("opt_in_required_mapped_external_rows"),
        "full-source archive command-count aliases changed",
    )
    checks.check(
        oc12_observed.get("full_source_policy_runner_archive_gap_safe_action_ids")
        == summary.get("full_source_policy_runner_archive_gap_safe_action_ids")
        == full_source_runner_gap.get("safe_action_ids")
        == expected_safe_archive_action_ids
        and oc12_observed.get("full_source_policy_runner_archive_gap_opt_in_action_ids")
        == summary.get("full_source_policy_runner_archive_gap_opt_in_action_ids")
        == full_source_runner_gap.get("opt_in_action_ids")
        == expected_opt_in_archive_action_ids,
        "OC12 full-source archive action ids changed",
    )
    archive_closure = full_source_runner_gap.get("closure_conditions", {})
    checks.check(
        by_id.get("OC12", {}).get("observed", {}).get(
            "full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_status"
        )
        == summary.get("full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_status")
        == archive_closure.get("tfe_runner_contract_preflight_status")
        == "contract_entrypoints_callable_candidate_backed_source_policy_open"
        and by_id.get("OC12", {}).get("observed", {}).get(
            "full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_entrypoints"
        )
        == summary.get("full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_entrypoints")
        == archive_closure.get("tfe_runner_contract_preflight_entrypoints")
        == "3/3"
        and by_id.get("OC12", {}).get("observed", {}).get(
            "full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_candidate_backed"
        )
        == summary.get("full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_candidate_backed")
        == archive_closure.get("tfe_runner_contract_preflight_candidate_backed")
        == "3/3"
        and by_id.get("OC12", {}).get("observed", {}).get(
            "full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_source_policy_rows_completed"
        )
        == summary.get(
            "full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_source_policy_rows_completed"
        )
        == archive_closure.get("tfe_runner_contract_preflight_source_policy_rows_completed")
        == 0
        and by_id.get("OC12", {}).get("observed", {}).get(
            "full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_execution_blocks"
        )
        == summary.get("full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_execution_blocks")
        == archive_closure.get("tfe_runner_contract_preflight_execution_blocks")
        == 4
        and by_id.get("OC12", {}).get("observed", {}).get(
            "full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_safe_use"
        )
        == summary.get("full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_safe_use")
        == archive_closure.get("tfe_runner_contract_preflight_safe_use")
        == "runner_contract_preflight_only_not_source_policy_reproduction",
        "OC12 full-source archive TFE runner preflight boundary changed",
    )
    checks.check(
        by_id.get("OC12", {}).get("observed", {}).get("source_policy_execution_handoff_status")
        == b4_execution_handoff.get("status")
        == "source_policy_execution_handoff_ready_not_authorized_not_run"
        and by_id.get("OC12", {}).get("observed", {}).get("source_policy_execution_handoff_authorized")
        == b4_execution_handoff.get("execution_authorized")
        is False
        and by_id.get("OC12", {}).get("observed", {}).get(
            "source_policy_execution_handoff_commands_not_run"
        )
        == b4_execution_handoff.get("commands_not_run_by_handoff")
        is True,
        "OC12 source-policy handoff boundary changed",
    )
    checks.check(
        summary.get("local_runner_package_partial_ready") is True
        and summary.get("runner_centered_status")
        == runner_centered.get("status")
        == "local_runner_centered_candidate_ready_source_policy_package_open"
        and summary.get("runner_centered_package_ready") is False
        and summary.get("local_runner_centered_candidate_ready") is True
        and summary.get("full_source_policy_runner_package_ready") is False,
        "summary local/full runner package readiness changed",
    )
    checks.check(
        summary.get("narrowed_reproducibility_package_ready") is True
        and summary.get("narrowed_repro_code_archive_ready") is True
        and summary.get("narrowed_repro_code_archive_status")
        == narrowed_repro_code_archive.get("status")
        == "narrowed_repro_code_archive_ready_source_policy_open"
        and summary.get("narrowed_repro_code_archive_entry_count")
        == narrowed_repro_code_archive.get("entry_count")
        and summary.get("narrowed_repro_code_archive_python_files")
        == narrowed_repro_code_archive.get("python_file_count")
        and summary.get("narrowed_repro_code_archive_python_lines")
        == narrowed_repro_code_archive.get("python_line_count")
        and summary.get("narrowed_repro_code_archive_source_policy_rows_closed") == 0
        and summary.get("narrowed_repro_code_archive_source_policy_rows_total") == 40
        and summary.get("narrowed_repro_code_archive_full_source_policy_ready") is False
        and summary.get("narrowed_repro_code_archive_submission_ready") is False,
        "summary narrowed repro code archive boundary changed",
    )
    checks.check(
        summary.get("minimal_submission_code_dependency_boundary_status")
        == "narrowed_repro_ready_full_source_policy_package_blocked"
        and summary.get("minimal_submission_code_dependency_blockers") == ["OC4", "OC6", "OC12"]
        and summary.get("minimal_submission_code_dependency_safe_use")
        == "narrowed_claim_replay_and_audit_provenance_only"
        and summary.get("minimal_submission_code_dependency_primary_allowed") is False,
        "summary OC12 dependency boundary changed",
    )
    strict_proof_boundary = audit.get("strict_proof_writing_submission_boundary", {})
    checks.check(
        strict_proof_boundary.get("schema") == "strict-proof-writing-submission-boundary-v1"
        and strict_proof_boundary.get("status")
        == "proof_writing_traceable_global_submission_blocked_by_source_policy_tfe_package"
        and summary.get("strict_proof_writing_submission_boundary_status")
        == strict_proof_boundary.get("status"),
        "strict proof-writing submission boundary status changed",
    )
    checks.check(
        strict_proof_boundary.get("proof_writing_card_status") == proof_writing_card.get("status")
        == "conditional_theorem_traceable_direct_pc2_closed_global_boundaries_retained"
        and summary.get("strict_proof_writing_card_status") == proof_writing_card.get("status"),
        "strict proof-writing card status not propagated from proof traceability audit",
    )
    checks.check(
        strict_proof_boundary.get("safe_reader_claim") == proof_writing_card.get("safe_reader_claim")
        and summary.get("strict_proof_writing_safe_reader_claim")
        == proof_writing_card.get("safe_reader_claim")
        == proof_claim_summary.get("proof_writing_boundary_card_safe_reader_claim")
        == expected_safe_reader_claim,
        "strict proof-writing safe reader claim changed",
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
        "strict proof-writing reader-claim boundary lost assumption/read-rule evidence",
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
        "strict proof-writing theorem-assumption anchor IDs changed",
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
        "strict proof-writing satisfied assumption partition changed",
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
        "strict proof-writing retained-interface/open-nonpromotion partition changed",
    )
    checks.check(
        strict_proof_boundary.get("theorem_assumption_retained_theorem_interface_ids")
        == expected_retained_theorem_interface_ids
        and strict_proof_boundary.get("theorem_assumption_retained_theorem_interface_count")
        == len(expected_retained_theorem_interface_ids)
        and proof_claim_remaining_boundary.get("retained_theorem_interface_ids")
        == proof_claim_summary.get("theorem_assumption_retained_theorem_interface_ids")
        == expected_retained_theorem_interface_ids,
        "strict proof-writing retained theorem-interface partition changed",
    )
    checks.check(
        strict_proof_boundary.get("theorem_assumption_open_nonpromotion_boundary_ids")
        == expected_open_nonpromotion_boundary_ids
        and strict_proof_boundary.get("theorem_assumption_open_nonpromotion_boundary_count")
        == len(expected_open_nonpromotion_boundary_ids)
        and proof_claim_remaining_boundary.get("open_nonpromotion_boundary_ids")
        == proof_claim_summary.get("theorem_assumption_open_nonpromotion_boundary_ids")
        == expected_open_nonpromotion_boundary_ids,
        "strict proof-writing open output-boundary partition changed",
    )
    checks.check(
        "Strict proof-writing P-interface partition: boundary `True`;"
        in audit_md,
        "objective completion markdown missing strict proof-writing theorem-assumption partition",
    )
    checks.check(
        strict_proof_boundary.get("forbidden_reader_claims")
        == summary.get("strict_proof_writing_forbidden_reader_claims")
        == proof_writing_card.get("forbidden_reader_claims")
        == expected_forbidden_reader_claims,
        "strict proof-writing forbidden reader claims changed",
    )
    checks.check(
        strict_proof_boundary.get("forbidden_reader_claims_boundary_present")
        == summary.get("strict_proof_writing_forbidden_reader_claims_boundary_present")
        is True,
        "strict proof-writing forbidden reader claims boundary missing",
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
        "strict proof-writing unconditional-theorem forbidden claim lost evidence",
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
        "strict proof-writing eta_h solver-policy forbidden claim lost evidence",
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
        "strict proof-writing fixed-tolerance forbidden claim lost evidence",
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
        "strict proof-writing residual-to-error transfer-theorem forbidden claim lost evidence",
    )
    checks.check(
        strict_proof_boundary.get("residual_to_error_not_promoted")
        == summary.get("strict_proof_writing_residual_to_error_not_promoted")
        is True
        and strict_proof_boundary.get("residual_to_error_route_promoted") is False
        and proof_residual_policy.get("accepted_residual_to_error_theorem") is False
        and proof_residual_policy.get("residual_promotion_not_made") is True,
        "strict proof-writing residual-to-error no-promotion lock lost evidence",
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
        "strict proof-writing source-policy/full-TFE forbidden claim lost evidence",
    )
    checks.check(
        strict_proof_boundary.get("source_policy_full_tfe_not_promoted")
        == summary.get("strict_proof_writing_source_policy_full_tfe_not_promoted")
        is True
        and strict_proof_boundary.get("source_policy_or_full_tfe_not_promoted")
        is True
        and strict_proof_boundary.get("source_policy_closed") is False
        and strict_proof_boundary.get("tfe_runner_closed") is False
        and strict_proof_boundary.get("minimal_code_ready") is False
        and strict_proof_boundary.get("full_source_policy_runner_package_ready")
        is False,
        "strict proof-writing source-policy/full-TFE no-promotion lock lost evidence",
    )
    checks.check(
        "Strict proof-writing forbidden claims/global boundaries: claims" in audit_md
        and "boundary `True`; unconditional/eta/fixed/residual/source-package `True/True/True/True/True`"
        in audit_md,
        "objective completion markdown missing strict proof-writing forbidden-claim evidence",
    )
    checks.check(
        "Strict proof-writing no-promotion locks: residual-to-error `True`; source-policy/full-TFE package `True`."
        in audit_md,
        "objective completion markdown missing strict proof-writing no-promotion locks",
    )
    checks.check(
        strict_proof_boundary.get("accepted_theorem_label")
        == proof_writing_card.get("accepted_theorem_label")
        == "thm:g6fullva-order"
        and strict_proof_boundary.get("accepted_method_order") == 6
        and strict_proof_boundary.get("accepted_local_defect_order") == 7,
        "strict proof-writing theorem/order boundary changed",
    )
    checks.check(
        strict_proof_boundary.get("reader_facing_manuscript_boundary_present")
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
        is True,
        "strict proof-writing reader-facing manuscript boundary changed",
    )
    checks.check(
        strict_proof_boundary.get("p7_retained_nonpromotion_boundary_present")
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
        == summary.get("strict_proof_writing_p7_retained_nonpromotion_boundary_present")
        is True,
        "strict proof-writing P7 output nonclaim/residual-to-error boundary changed",
    )
    checks.check(
        "Strict proof-writing P7 output nonclaim/residual-to-error boundary: `True`." in audit_md,
        "objective completion markdown missing strict proof-writing P7 boundary",
    )
    checks.check(
        strict_proof_boundary.get("b1_closure_scope_boundary_present")
        == proof_writing_card.get("b1_closure_scope_boundary_present")
        == proof.get("b1_ad_expanded_closure_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        == summary.get("strict_proof_writing_b1_closure_scope_boundary_present")
        is True,
        "strict proof-writing B1 closure-scope boundary changed",
    )
    checks.check(
        "Strict proof-writing B1 closure-scope boundary: `True`." in audit_md,
        "objective completion markdown missing strict proof-writing B1 closure-scope boundary",
    )
    checks.check(
        strict_proof_boundary.get("b1_ad_expanded_closure_ledger_present")
        == proof.get("b1_ad_expanded_closure_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        == summary.get("strict_proof_writing_b1_ad_expanded_closure_ledger_present")
        is True,
        "strict proof-writing B1 AD-expanded closure ledger changed",
    )
    checks.check(
        strict_proof_boundary.get("b1_ad_expanded_symbolic_oracle_closed_rows")
        == proof.get("evidence_summary", {}).get(
            "b1_ad_expanded_symbolic_oracle_closed_rows"
        )
        == 36,
        "strict proof-writing B1 AD-expanded closed row count changed",
    )
    checks.check(
        strict_proof_boundary.get("b1_ad_expanded_symbolic_oracle_closed_cells")
        == proof.get("evidence_summary", {}).get(
            "b1_ad_expanded_symbolic_oracle_closed_cells"
        )
        == summary.get("strict_proof_writing_b1_ad_expanded_symbolic_oracle_closed_cells")
        == 4752,
        "strict proof-writing B1 AD-expanded derivative-cell count changed",
    )
    checks.check(
        "Strict proof-writing B1 AD-expanded closure ledger/cells: `True` / `4752`."
        in audit_md,
        "objective completion markdown missing strict proof-writing B1 AD-expanded closure ledger",
    )
    checks.check(
        strict_proof_boundary.get("p6_solver_scope_boundary_present")
        == proof_writing_card.get("p6_solver_scope_boundary_present")
        == summary.get("strict_proof_writing_p6_solver_scope_boundary_present")
        == proof.get("p6_solver_scope_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        is True,
        "strict proof-writing P6 solver-scope boundary changed",
    )
    checks.check(
        "Strict proof-writing P6 solver-scope boundary: `True`." in audit_md,
        "objective completion markdown missing strict proof-writing P6 solver-scope boundary",
    )
    checks.check(
        strict_proof_boundary.get("p1p2_compact_tube_boundary_present")
        == proof_writing_card.get("p1p2_compact_tube_boundary_present")
        == proof.get("p1p2_compact_tube_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        == summary.get("strict_proof_writing_p1p2_compact_tube_boundary_present")
        is True,
        "strict proof-writing P1/P2 compact-tube boundary changed",
    )
    checks.check(
        "Strict proof-writing P1/P2 compact-tube boundary: `True`." in audit_md,
        "objective completion markdown missing strict proof-writing P1/P2 compact-tube boundary",
    )
    checks.check(
        strict_proof_boundary.get("p3p4_implementation_boundary_present")
        == proof_writing_card.get("p3p4_implementation_boundary_present")
        == proof.get("p3p4_implementation_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        == summary.get("strict_proof_writing_p3p4_implementation_boundary_present")
        is True,
        "strict proof-writing P3/P4 implementation-defect boundary changed",
    )
    checks.check(
        "Strict proof-writing P3/P4 implementation-defect boundary: `True`." in audit_md,
        "objective completion markdown missing strict proof-writing P3/P4 implementation-defect boundary",
    )
    checks.check(
        strict_proof_boundary.get("p5_direct_route_boundary_present")
        == proof_writing_card.get("p5_direct_route_boundary_present")
        == proof.get("p5_direct_route_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        == summary.get("strict_proof_writing_p5_direct_route_boundary_present")
        is True,
        "strict proof-writing P5 direct-route boundary changed",
    )
    checks.check(
        "Strict proof-writing P5 direct-route boundary: `True`." in audit_md,
        "objective completion markdown missing strict proof-writing P5 direct-route boundary",
    )
    checks.check(
        strict_proof_boundary.get("proof_causality_ledger_present")
        == proof_writing_card.get("proof_causality_ledger_present")
        == proof.get("proof_causality_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        == summary.get("strict_proof_writing_proof_causality_ledger_present")
        is True,
        "strict proof-writing proof-causality ledger changed",
    )
    checks.check(
        "Strict proof-writing proof-causality ledger: `True`." in audit_md,
        "objective completion markdown missing strict proof-writing proof-causality ledger",
    )
    checks.check(
        strict_proof_boundary.get("direct_route_anticircularity_ledger_present")
        == proof_writing_card.get("direct_route_anticircularity_ledger_present")
        == proof.get("direct_route_anticircularity_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        == summary.get(
            "strict_proof_writing_direct_route_anticircularity_ledger_present"
        )
        is True,
        "strict proof-writing direct-route anti-circularity ledger changed",
    )
    checks.check(
        "Strict proof-writing direct-route anti-circularity ledger: `True`."
        in audit_md,
        "objective completion markdown missing strict proof-writing direct-route anti-circularity ledger",
    )
    checks.check(
        strict_proof_boundary.get("p_interface_satisfaction_ledger_present")
        == proof_writing_card.get("p_interface_satisfaction_ledger_present")
        == summary.get("strict_proof_writing_p_interface_satisfaction_ledger_present")
        == proof.get("p_interface_satisfaction_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        is True,
        "strict proof-writing theorem-interface satisfaction ledger changed",
    )
    checks.check(
        "Strict proof-writing theorem-interface satisfaction ledger: `True`." in audit_md,
        "objective completion markdown missing strict proof-writing theorem-interface satisfaction ledger",
    )
    checks.check(
        strict_proof_boundary.get("p7_residual_to_error_ledger_present")
        == proof_writing_card.get("p7_residual_to_error_ledger_present")
        == summary.get("strict_proof_writing_p7_residual_to_error_ledger_present")
        == proof.get("p7_residual_to_error_obligation_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        is True,
        "strict proof-writing P7 residual-to-error obligation ledger changed",
    )
    checks.check(
        "Strict proof-writing P7 residual-to-error obligation ledger: `True`."
        in audit_md,
        "objective completion markdown missing strict proof-writing P7 residual-to-error obligation ledger",
    )
    checks.check(
        strict_proof_boundary.get("theorem_use_rule_present")
        == proof_writing_card.get("theorem_use_rule_present")
        == proof.get("theorem_use_rule_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        == summary.get("strict_proof_writing_theorem_use_rule_present")
        is True,
        "strict proof-writing theorem-use rule changed",
    )
    checks.check(
        "Strict proof-writing theorem-use rule: `True`." in audit_md,
        "objective completion markdown missing strict proof-writing theorem-use rule",
    )
    checks.check(
        strict_proof_boundary.get("quantifier_domain_ledger_present")
        == proof_writing_card.get("quantifier_domain_ledger_present")
        == proof.get("quantifier_domain_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        == summary.get("strict_proof_writing_quantifier_domain_ledger_present")
        is True,
        "strict proof-writing quantifier/domain ledger changed",
    )
    checks.check(
        "Strict proof-writing quantifier/domain ledger: `True`." in audit_md,
        "objective completion markdown missing strict proof-writing quantifier/domain ledger",
    )
    checks.check(
        strict_proof_boundary.get("local_global_transfer_ledger_present")
        == proof_writing_card.get("local_global_transfer_ledger_present")
        == proof.get("local_global_transfer_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        == summary.get("strict_proof_writing_local_global_transfer_ledger_present")
        is True,
        "strict proof-writing local-to-global transfer ledger changed",
    )
    checks.check(
        "Strict proof-writing local-to-global transfer ledger: `True`." in audit_md,
        "objective completion markdown missing strict proof-writing local-to-global transfer ledger",
    )
    checks.check(
        strict_proof_boundary.get("objective_completion_boundary_present")
        == proof_writing_card.get("objective_completion_boundary_present")
        == summary.get("strict_proof_writing_objective_completion_boundary_present")
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
        "strict proof-writing objective-completion boundary changed",
    )
    checks.check(
        "Strict proof-writing objective-completion boundary: `True`." in audit_md,
        "objective completion markdown missing strict proof-writing objective-completion boundary",
    )
    checks.check(
        strict_proof_boundary.get("constant_dependency_ledger_present")
        == proof_writing_card.get("constant_dependency_ledger_present")
        == proof.get("constant_dependency_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        == summary.get("strict_proof_writing_constant_dependency_ledger_present")
        is True,
        "strict proof-writing constant-dependency ledger changed",
    )
    checks.check(
        "Strict proof-writing constant-dependency ledger: `True`." in audit_md,
        "objective completion markdown missing strict proof-writing constant-dependency ledger",
    )
    checks.check(
        strict_proof_boundary.get("theorem_dependency_consumption_ledger_present")
        == proof_writing_card.get("theorem_dependency_consumption_ledger_present")
        == proof.get("theorem_dependency_consumption_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        == summary.get(
            "strict_proof_writing_theorem_dependency_consumption_ledger_present"
        )
        is True,
        "strict proof-writing theorem dependency consumption ledger changed",
    )
    checks.check(
        "Strict proof-writing theorem dependency consumption ledger: `True`."
        in audit_md,
        "objective completion markdown missing strict proof-writing theorem dependency consumption ledger",
    )
    checks.check(
        strict_proof_boundary.get("branch_consistency_ledger_present")
        == proof_writing_card.get("branch_consistency_ledger_present")
        == proof.get("branch_consistency_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        == summary.get("strict_proof_writing_branch_consistency_ledger_present")
        is True,
        "strict proof-writing accepted-branch consistency ledger changed",
    )
    checks.check(
        "Strict proof-writing accepted-branch consistency ledger: `True`."
        in audit_md,
        "objective completion markdown missing strict proof-writing accepted-branch consistency ledger",
    )
    checks.check(
        strict_proof_boundary.get("implementation_route_oracle_ledger_present")
        == proof_writing_card.get("implementation_route_oracle_ledger_present")
        == proof.get("implementation_route_oracle_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        == summary.get("strict_proof_writing_implementation_route_oracle_ledger_present")
        is True,
        "strict proof-writing implementation-route/oracle separation ledger changed",
    )
    checks.check(
        "Strict proof-writing implementation-route/oracle separation ledger: `True`."
        in audit_md,
        "objective completion markdown missing strict proof-writing implementation-route/oracle separation ledger",
    )
    checks.check(
        strict_proof_boundary.get("nonlinear_solver_scale_ledger_present")
        == proof_writing_card.get("nonlinear_solver_scale_ledger_present")
        == proof.get("nonlinear_solver_scale_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        == summary.get("strict_proof_writing_nonlinear_solver_scale_ledger_present")
        is True,
        "strict proof-writing nonlinear-solver scale ledger changed",
    )
    checks.check(
        "Strict proof-writing nonlinear-solver scale ledger: `True`."
        in audit_md,
        "objective completion markdown missing strict proof-writing nonlinear-solver scale ledger",
    )
    checks.check(
        strict_proof_boundary.get("local_defect_decomposition_ledger_present")
        == proof_writing_card.get("local_defect_decomposition_ledger_present")
        == proof.get("local_defect_decomposition_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        == summary.get(
            "strict_proof_writing_local_defect_decomposition_ledger_present"
        )
        is True,
        "strict proof-writing local-defect decomposition ledger changed",
    )
    checks.check(
        "Strict proof-writing local-defect decomposition ledger: `True`."
        in audit_md,
        "objective completion markdown missing strict proof-writing local-defect decomposition ledger",
    )
    checks.check(
        strict_proof_boundary.get("theorem_output_scope_ledger_present")
        == proof_writing_card.get("theorem_output_scope_ledger_present")
        == proof.get("theorem_output_scope_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        == summary.get("strict_proof_writing_theorem_output_scope_ledger_present")
        is True,
        "strict proof-writing theorem output scope ledger changed",
    )
    checks.check(
        "Strict proof-writing theorem output scope ledger: `True`." in audit_md,
        "objective completion markdown missing strict proof-writing theorem output scope ledger",
    )
    checks.check(
        strict_proof_boundary.get("reporting_map_ledger_present")
        == proof_writing_card.get("reporting_map_ledger_present")
        == proof.get("reporting_map_ledger_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        == summary.get("strict_proof_writing_reporting_map_ledger_present")
        is True,
        "strict proof-writing reporting-map/norm-equivalence ledger changed",
    )
    checks.check(
        "Strict proof-writing reporting-map/norm-equivalence ledger: `True`."
        in audit_md,
        "objective completion markdown missing strict proof-writing reporting-map/norm-equivalence ledger",
    )
    checks.check(
        strict_proof_policy.get("terminology_reconciled") is True
        and reference_correspondence.get("closed") is True
        and strict_proof_boundary.get("reference_proof_order_correspondence_closed")
        == summary.get("strict_proof_writing_reference_proof_order_correspondence_closed")
        is True,
        "strict proof-writing reference proof-order correspondence not closed",
    )
    checks.check(
        strict_proof_boundary.get("reference_proof_order_no_estimate_transfer")
        == summary.get("strict_proof_writing_reference_proof_order_no_estimate_transfer")
        is True
        and reference_main_features.get("not_estimate_transfer") is True
        and reference_flat_features.get("not_estimate_transfer") is True,
        "strict proof-writing reference proof-order no-estimate-transfer boundary changed",
    )
    checks.check(
        strict_proof_boundary.get("reference_proof_order_nonimport_boundary")
        == summary.get("strict_proof_writing_reference_proof_order_nonimport_boundary")
        is True
        and reference_main_features.get("caption_nonimport_boundary") is True
        and reference_flat_features.get("caption_nonimport_boundary") is True,
        "strict proof-writing reference proof-order nonimport boundary changed",
    )
    checks.check(
        strict_proof_boundary.get("reference_proof_order_constraint_multiplier_split")
        == summary.get("strict_proof_writing_reference_proof_order_constraint_multiplier_split")
        is True
        and reference_main_features.get("constraint_multiplier_interface_split") is True
        and reference_flat_features.get("constraint_multiplier_interface_split") is True
        and reference_main_features.get("table_constraint_multiplier_interface_split") is True
        and reference_flat_features.get("table_constraint_multiplier_interface_split") is True,
        "strict proof-writing reference proof-order constraint/multiplier split changed",
    )
    checks.check(
        strict_proof_boundary.get("reference_proof_order_source_text")
        == strict_proof_policy.get("source_paper_style_read", {}).get("reference_text")
        == "../../external/literature/1-s2.0-S0377042719305229-main.txt",
        "strict proof-writing reference proof-order source text changed",
    )
    checks.check(
        "Strict proof-writing reference proof-order correspondence: closed `True`; "
        "no-estimate-transfer `True`; nonimport `True`; constraint/multiplier split `True`."
        in audit_md,
        "objective completion markdown missing strict proof-writing reference proof-order correspondence line",
    )
    checks.check(
        strict_proof_boundary.get("direct_pc2_proof_gap_closed")
        == proof_writing_card.get("direct_pc2_proof_gap_closed")
        == proof_closure_state.get("direct_pc2_proof_gap_closed")
        == proof_closure_state.get("proof_gap_closed")
        == proof_claim_closure_state.get("direct_pc2_proof_gap_closed")
        == proof_claim_summary.get("direct_pc2_proof_gap_closed")
        is True,
        "strict proof-writing direct PC2 closure flag lost proof-state evidence",
    )
    checks.check(
        strict_proof_boundary.get("stage_residual_O_h7_implementation_defect_proved")
        == proof_writing_card.get("stage_residual_O_h7_implementation_defect_proved")
        == proof_closure_state.get("stage_residual_O_h7_implementation_defect_proved")
        == proof_claim_closure_state.get(
            "stage_residual_O_h7_implementation_defect_proved"
        )
        == proof_claim_summary.get("stage_residual_O_h7_implementation_defect_proved")
        is True,
        "strict proof-writing stage residual O(h^7) flag lost proof-state evidence",
    )
    checks.check(
        strict_proof_boundary.get("dynamic_symbolic_oracle_complete")
        == proof_writing_card.get("dynamic_symbolic_oracle_complete")
        == proof_closure_state.get("dynamic_symbolic_oracle_complete")
        == proof_claim_closure_state.get("dynamic_symbolic_oracle_complete")
        == proof_claim_summary.get("dynamic_symbolic_oracle_complete")
        is False,
        "strict proof-writing dynamic symbolic oracle flag lost open-state evidence",
    )
    checks.check(
        strict_proof_boundary.get("eta_h_solver_policy_evidence_closed")
        == proof_writing_card.get("eta_h_solver_policy_evidence_closed")
        == proof_theorem_boundary.get("eta_h_solver_policy_evidence_closed")
        == proof_closure_state.get("eta_h_O_h7_solver_policy_evidence")
        == proof_solver_state.get("eta_h_O_h7_solver_policy_evidence")
        == proof_claim_theorem_traceability.get("eta_h_solver_policy_evidence_closed")
        == proof_claim_remaining_boundary.get("eta_h_solver_policy_evidence_closed")
        is False,
        "strict proof-writing eta_h solver-policy theorem flag lost retained-open evidence",
    )
    checks.check(
        strict_proof_boundary.get("fixed_tolerance_runs_are_asymptotic_proof")
        == proof_writing_card.get("fixed_tolerance_runs_are_asymptotic_proof")
        == proof_theorem_boundary.get("fixed_tolerance_runs_are_asymptotic_proof")
        == proof_closure_state.get("fixed_tolerance_runs_are_asymptotic_proof")
        == proof_claim_theorem_traceability.get(
            "fixed_tolerance_runs_are_asymptotic_proof"
        )
        is False,
        "strict proof-writing fixed-tolerance asymptotic-proof flag lost exclusion evidence",
    )
    checks.check(
        strict_proof_boundary.get("residual_to_error_route_promoted")
        == proof_writing_card.get("residual_to_error_route_promoted")
        == proof_residual_policy.get("accepted_residual_to_error_theorem")
        == proof_claim_remaining_boundary.get("residual_to_error_route_promoted")
        == proof_claim_summary.get("residual_to_error_route_promoted")
        is False
        and proof_residual_policy.get("residual_promotion_not_made") is True,
        "strict proof-writing residual-to-error promotion flag lost nonpromotion evidence",
    )
    checks.check(
        strict_proof_boundary.get("source_policy_or_full_tfe_not_promoted")
        == proof_writing_card.get("source_policy_or_full_tfe_not_promoted")
        == proof_theorem_boundary.get("does_not_promote_source_policy_or_full_tfe")
        == proof_claim_theorem_traceability.get(
            "source_policy_or_full_tfe_not_promoted"
        )
        == proof_claim_remaining_boundary.get("source_policy_or_full_tfe_not_promoted")
        is True,
        "strict proof-writing source-policy/full-TFE nonpromotion flag lost evidence",
    )
    checks.check(
        strict_proof_boundary.get("proof_global_boundaries_retained")
        == summary.get("strict_proof_writing_global_boundaries_retained")
        == proof_writing_card.get("global_submission_boundaries_retained")
        == proof_readiness_boundary.get("global_submission_boundaries_retained")
        == proof_claim_remaining_boundary.get("global_submission_boundaries_retained")
        == proof_claim_summary.get("global_submission_boundaries_retained")
        == expected_global_submission_boundaries,
        "strict proof-writing global retained boundaries changed",
    )
    checks.check(
        strict_proof_boundary.get("satisfied_close_requirement_ids")
        == proof_writing_card.get("satisfied_close_requirement_ids")
        == proof_satisfied_close_requirement_ids
        == proof_claim_summary.get("close_requirement_satisfied_ids")
        == ["PC1", "PC2", "PC3", "PC4"]
        and strict_proof_boundary.get("unsatisfied_close_requirement_ids")
        == proof_writing_card.get("unsatisfied_close_requirement_ids")
        == proof_unsatisfied_close_requirement_ids
        == proof_claim_summary.get("close_requirement_unsatisfied_ids")
        == [],
        "strict proof-writing close requirement IDs lost proof-state evidence",
    )
    checks.check(
        strict_proof_boundary.get("objective_blockers_retained")
        == summary.get("strict_proof_writing_objective_blockers_retained")
        == ["OC4", "OC6", "OC12"]
        and strict_proof_boundary.get("source_policy_closed") is False
        and strict_proof_boundary.get("tfe_runner_closed") is False
        and strict_proof_boundary.get("minimal_code_ready") is False
        and strict_proof_boundary.get("full_source_policy_runner_package_ready") is False,
        "strict proof-writing objective/package blocker boundary changed",
    )
    checks.check(
        strict_proof_boundary.get("proof_claim_traceability_submission_ready")
        == proof_claim_traceability.get("submission_ready")
        is False
        and strict_proof_boundary.get("submission_ready")
        == summary.get("strict_proof_writing_submission_ready")
        is False
        and strict_proof_boundary.get("can_mark_goal_complete") is False
        and strict_proof_boundary.get("package_boundary_status")
        == "narrowed_repro_ready_full_source_policy_package_blocked"
        and strict_proof_boundary.get("package_safe_current_use")
        == "narrowed_claim_replay_and_audit_provenance_only"
        and strict_proof_boundary.get("primary_submission_package_allowed") is False,
        "strict proof-writing submission/package readiness boundary changed",
    )
    checks.check(
        strict_proof_boundary.get("evidence_sources")
        == [
            "PROOF_CLAIM_TRACEABILITY_AUDIT.json",
            "PROOF_CLOSURE_MANIFEST.json",
            "CMAME_RUNNER_CENTERED_REPRODUCIBILITY_AUDIT.json",
            "CMAME_NARROWED_REPRO_CODE_ARCHIVE_MANIFEST.json",
            "B6_FOUR_EXAMPLE_LOCAL_EVIDENCE_SUMMARY.json",
            "CMAME_STRICT_PROOF_POLICY_RECONCILIATION_AUDIT.json",
        ],
        "strict proof-writing evidence-source list changed",
    )
    checks.check(
        "Strict proof-writing submission boundary: `proof_writing_traceable_global_submission_blocked_by_source_policy_tfe_package`"
        in audit_md,
        "objective audit markdown missing strict proof-writing submission boundary",
    )
    checks.check(
        "Strict proof-writing forbidden claims/global boundaries:"
        in audit_md,
        "objective audit markdown missing strict proof-writing forbidden/global boundary line",
    )
    checks.check(
        summary.get("human_runnable_self_contained_examples")
        == b6_local_evidence.get("self_contained_examples")
        == ["single_pendulum", "double_pendulum", "four_link", "slider_crank"]
        and summary.get("human_runnable_replay_only_examples") == b6_local_evidence.get("replay_only_examples") == [],
        "summary human-runnable local runner examples changed",
    )
    checks.check(
        summary.get("b6_four_example_local_rows") == b6_local_evidence.get("local_rows") == 12
        and summary.get("b6_four_example_source_policy_rows_closed")
        == b6_local_evidence.get("source_policy_external_rows_closed")
        == 0
        and summary.get("b6_four_example_source_policy_rows_total")
        == b6_local_evidence.get("source_policy_external_rows_total")
        == 40,
        "summary B6 local runner row boundary changed",
    )
    checks.check(
        summary.get("compact_closed_loop_candidate_runner_passed")
        == closed_loop_candidate.get("runner_passed")
        is True
        and summary.get("compact_closed_loop_candidate_python_lines")
        == closed_loop_candidate.get("candidate_python_line_count"),
        "summary compact closed-loop runner boundary changed",
    )
    checks.check(
        summary.get("p1_single_runner_candidate_ready")
        == p1_local_runner.get("p1_single_runner_candidate_ready")
        is True
        and summary.get("p1_double_runner_candidate_ready")
        == p1_local_runner.get("p1_double_runner_candidate_ready")
        is True,
        "summary P1 local runner readiness changed",
    )

    for token in [
        "Status: **not_complete_submission_standard_open**",
        "Objective complete: `False`",
        "Can mark goal complete: `False`",
        "Completion decision reason: blocking objective requirements remain open or partial.",
        "Requirements satisfied/partial/open: `9/2/1`",
        "Blocking requirement ids: `['OC4', 'OC6', 'OC12']`",
        "Open blocker id alias: `['OC4', 'OC6', 'OC12']`.",
        "Machine-readable blocker ids: `['OC4', 'OC6', 'OC12']`.",
        "Machine-readable blocker status by id: `{'OC4': 'open', 'OC6': 'partial', 'OC12': 'partial'}`.",
        "## Blocking Requirements",
        "| `OC4` | `open` | `EXTERNAL_SOURCE_POLICY_CLOSURE_MANIFEST.json, RA_HI_SOURCE_POLICY_CLOSEOUT_CHECKLIST.json, RA_HI_SOURCE_POLICY_PROMOTION_BLOCKER_MATRIX.json, B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json, B4_GUARDED_DRIVER_REFUSAL_BOUNDARY_AUDIT_20260621.json, FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.json` | source_policy_reproduction=False; same_test_campaign_status=not_run; external_superiority_claim_allowed=False; ra_hi_closeout=ready_for_authorized_execution_closeout_not_executed_not_promoted; ra_hi_rows=12/8/20; commands=13/20; traceability_unique=20/20; traceability_refs=32/32; traceability_mismatch_terminal_closed=0/0/0; promoted=0; executed=False; ra_hi_terminal_future_complete=20/20/0; handoff=source_policy_execution_handoff_ready_not_authorized_not_run; handoff_authorized=False; handoff_commands_not_run=True; approval=I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json.; driver=run_b4_source_policy_after_opt_in.sh; driver_requires_exact=True; opt_in_commands=13/20; terminal_unable=20; refusal_boundary=True/True/2/0/13/False/False; provenance=40/40/0/40/0; provenance_handoff=source_policy_execution_handoff_ready_not_authorized_not_run/False/True",
        "| `OC6` | `partial` | `TFE_SOURCE_PENDULUM_MODEL_AUDIT.json, TFE_DAE_RUNNER_CONTRACT_GAP_AUDIT.json, TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.json, SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.json, OC6_EXTERNAL_SOURCE_ARTIFACT_RECHECK_20260621.json, OC6_TFE_PUBLISHER_ARTIFACT_AVAILABILITY_AUDIT_20260621.json, OC6_TFE_SOURCE_EQUIVALENT_ARTIFACT_REQUEST_PACKET_20260621.json, SOURCE_POLICY_REOPEN_CONDITION_MONITOR_20260620.json, TFE_RUNNER_CONTRACT_PREFLIGHT_CERTIFICATE.json` | contract_gap_blocks=6; effective_execution_blocks=4; terminal_nonpromoted_blocks=2; candidate_backed_non_equivalent_runner_blocks=3; contract_gap_ready=False; nonheavy_demoted=True; execution_blocks=4; preflight_opt_in=False; terminal_route=no_public_code_self_reproduction_attempted_unable_to_reproduce_not_promoted; preflight_promote_ready=False/False; self_reproduction=attempted_not_reproducible_not_promoted/0/16; public_code=public_code_rechecked_no_distinct_tfe_code_artifact_attempted_not_reproducible; refresh=20/11/0/0/20; latest_probe=2026-06-21/9/0/0/4/False/False; external_recheck=2026-06-21/10/0/0/0/False/False; publisher_availability=2026-06-21/True/0/0/0/0/False/False; request_packet=True/False/7/0/False/False; preflight=contract_entrypoints_callable_candidate_backed_source_policy_open/3/3/3/3/0/4; pendulum_dae_runner_implemented=False; brown_mcphee_friction_law_implemented=False; source_policy_rows_completed=0; full_T10_grid_resolved=False",
        "TFE self-reproduction terminal status/public-code/reopen/closed: `attempted_not_reproducible_not_promoted/public_code_rechecked_no_distinct_tfe_code_artifact_attempted_not_reproducible/new_public_or_source_code_equivalent_tfe_implementation_artifact/0/16`.",
        "TFE runner contract preflight status/entrypoints/candidate-backed/source-rows/execution-blocks: `contract_entrypoints_callable_candidate_backed_source_policy_open/3/3/3/0/4`.",
        "TFE latest public-code refresh status/rows/queries/positive/closed: `public_code_refresh_20260620_no_positive_new_source_artifact_rows_remain_unable_to_reproduce/20/11/0/0/20`.",
        "latest_probe=2026-06-21/9/0/0/4/False/False",
        "| `OC12` | `partial` | `current Python inventory, EXTERNAL_SOURCE_POLICY_CLOSURE_MANIFEST.json, PROOF_CLOSURE_MANIFEST.json",
        "| `OC5` | `satisfied` | `False` | Close the active B2 source-policy suites for original TFE, RA2021, and HI2022. | closed by Route-B demotion; source-policy rows remain 0 and external-superiority stays forbidden |",
        "Source-policy apples-to-apples closed: `False`",
        "Source-policy rows closed: `0/40`.",
        "Source-policy execution allowed now/invoked/exact opt-in required: `False/False/True`.",
        "Safe action ids: `rebuild_read_only_audit_chain,rerun_read_only_validators,keep_narrowed_archive_provenance_only,monitor_reopen_conditions`.",
        "Opt-in action ids: `authorized_b4_ra_hi_source_policy_execution`.",
        "Safe/opt-in action object counts: `4/1`.",
        "RA/HI source-policy closeout checklist: `ready_for_authorized_execution_closeout_not_executed_not_promoted`; rows RA/HI/total `12/8/20`; commands/mapped `13/20`; promoted/completed/external-ready `0/0/0`; opt-in/executed `True/False`; closes B4/B7 `False/False`.",
        "RA/HI current-evidence terminal/future-auth-or-artifact/reproduction-complete rows: `20/20/0`.",
        "Source-policy execution handoff: `source_policy_execution_handoff_ready_not_authorized_not_run`; authorized/commands-not-run `False/True`; ready commands/mapped `13/20`; terminal unable `20`.",
        "Source-policy execution handoff traceability: unique RA/HI rows `20/20`; row refs `32/32`; mismatches/terminal/closed/promotion-ready `0/0/0/0`.",
        "Source-policy execution exact approval/driver: `I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json./run_b4_source_policy_after_opt_in.sh/True/True/13/20`.",
        "B4 guarded driver refusal boundary 20260621: `True/True/2/0/13/False/False`.",
        "Full source-policy row provenance handoff exact approval/driver: `I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json./run_b4_source_policy_after_opt_in.sh/True/True/13/20/20`.",
        "B2 active suites closed/source-policy rows closed/demotion route: `True/False/True`",
        "B2 active/demoted flagged rows/can close/external-superiority allowed: `0/15/True/False`",
        "TFE DAE runner contract gap status/missing/non-heavy/execution/ready/heavy-run: `dae_runner_contract_gap_open_not_source_policy/6/2/4/False/False`",
        "TFE DAE runner contract accounting raw/non-heavy-terminal/effective-execution/source-rows: `6/2/4/0`",
        "TFE DAE runner effective execution blocks: `['pendulum_absolute_coordinate_source_policy_dae_runner_missing', 'tfe_newmark_trapezoidal_source_policy_method_runners_missing', 'gauss6_fullva_absolute_coordinate_source_policy_runner_missing', 'accepted_source_policy_work_precision_rows_not_executed_or_bound']`",
        "TFE DAE runner contract missing ids: `['brown_mcphee_source_code_equivalent_law_open', 'pendulum_absolute_coordinate_source_policy_dae_runner_missing', 'tfe_newmark_trapezoidal_source_policy_method_runners_missing', 'gauss6_fullva_absolute_coordinate_source_policy_runner_missing', 'full_T10_source_grid_endpoint_policy_open', 'accepted_source_policy_work_precision_rows_not_executed_or_bound']`",
        "TFE DAE runner non-heavy dispositions/demoted/no-row-closure: `2/True/True`",
        "TFE DAE runner execution block count: `4`",
        "TFE source-policy execution preflight status/opt-in/nonheavy/execution/promote/ready: `terminal_no_public_code_self_reproduction_attempted_not_promoted/False/True/4/False/False`",
        "TFE source-policy terminal route/reopen condition: `no_public_code_self_reproduction_attempted_unable_to_reproduce_not_promoted/new_public_or_source_code_equivalent_tfe_implementation_artifact`.",
        "TFE absolute-coordinate planar-lift trajectory probe rows/metric rows/source-policy rows/equivalent DAE: `12/36/0/False`",
        "TFE bounded absolute-coordinate DAE trajectory runner rows/metric rows/step residual rows/source-policy rows/equivalent DAE/monolithic: `4/12/56/0/False/False`",
        "TFE monolithic DAE candidate runner rows/metric rows/step residual rows/source-policy rows/equivalent DAE/monolithic: `4/12/56/0/False/False`",
        "TFE source-method candidate contract rows/source-policy rows/equivalent method/DAE: `5/0/False/False`",
        "TFE DAE trajectory bridge contract rows/matched/source-policy rows/equivalent DAE/method/monolithic: `12/12/0/False/False/False`",
        "TFE DAE trajectory bridge finite/residual-below-1e-10/accepted-use: `True/True/dae_trajectory_bridge_contract_not_source_policy`",
        "TFE candidate-friction DAE trajectory contract rows/step residual rows/source-policy rows/equivalent DAE/method/source-law/monolithic: `12/56/0/False/False/False/False`",
        "TFE candidate-friction DAE trajectory contract finite/residual-below-1e-9/friction-power-nonpositive: `True/True/True`",
        "TFE Brown--McPhee transition-velocity sensitivity rows/contracts/source rows/material/equivalence-false: `3/36/0/True/True`",
        "TFE Brown--McPhee source-code equivalence certificate status/available/positive/closed-block/exec/close-now: `negative_source_code_equivalence_certificate_not_source_policy/True/False/False/False/False`",
        "TFE bounded source-reference-policy smoke/full T=10 source run: `True/False`",
        "TFE source-grid policy resolved/incompatible rows: `False/4`",
        "TFE exact-T endpoint-grid subset resolved/requires policy: `True/2/4`",
        "TFE full-T10 endpoint policy closure certificate status/available/positive/closed-block/exec/close-now: `negative_full_T10_endpoint_policy_certificate_not_source_policy/True/False/False/False/False`",
        "endpoint_certificate=True/False/False",
        "TFE comparator candidate/TFE m=1-3 candidate/source-policy-equivalent/TFE m=1-3 source-policy runners: `True/True/False/False`",
        "Gauss6 source-pendulum candidate smoke/absolute-coordinate source-policy runner: `True/False`",
        "Gauss6 source-pendulum candidate rows/source-policy rows/method-equivalent: `2/0/False`",
        "Gauss6/FullVA DAE candidate contract rows/source-policy rows/equivalent DAE/FullVA: `1/0/False/False`",
        "TFE unified bounded runner rows/full T=10/source-policy rows: `4/False/0`",
        "Active TFE B2 candidate row smoke/full T=10/source-policy rows: `True/False/0`",
        "Active TFE B2 source-reference full T=10 candidate probe full T=10/reference invoked/source-policy rows/method-equivalent: `True/True/0/False`",
        "Direct PC2 proof closed; global proof/package blockers retained: `True`; blockers `['OC4', 'OC6', 'OC12']`.",
        "Newton-Euler obligation coverage matrix/links/complete rows: `True/180/36`",
        "Minimal reproducibility candidate/status/files/Python-lines: `candidate_replay_package_built_not_submission_ready/10/",
        "Local runner package partial/full-source-policy ready: `True/False`",
        "Narrowed repro code archive ready/status/entries/Python/source-policy/full-source/submission: `True/narrowed_repro_code_archive_ready_source_policy_open/",
        "Full source-policy runner archive gap: `full_source_policy_runner_archive_not_ready_source_policy_open`; ready/can-use-current-archive/safe-current-use `False/False/narrowed_claim_replay_and_audit_provenance_only`; rows closed/total `0/40`; terminal-unable/RA-HI-open `20/20`.",
        "Full source-policy runner archive TFE runner preflight: `contract_entrypoints_callable_candidate_backed_source_policy_open/3/3/3/3/0/4`.",
        "Full source-policy runner archive terminal reopen/exact approval: `tfe2026_original_pendulum=new_public_or_source_code_equivalent_tfe_implementation_artifact; vp2024_velocity_partitioning=new_distinct_public_vp2024_velocity_partitioning_code_path; approval=I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json.`.",
        "Minimal submission code dependency boundary: `narrowed_repro_ready_full_source_policy_package_blocked`; blockers `['OC4', 'OC6', 'OC12']`; safe use `narrowed_claim_replay_and_audit_provenance_only`; primary package allowed `False`.",
        "Machine-readable blocker closure keys: `['OC4', 'OC6', 'OC12']`.",
        "OC4 required-to-close source-policy/opt-in/commands/rows: `0/40/True/13/20`.",
        "OC6 required-to-close runner/reopen/probe: `contract_entrypoints_callable_candidate_backed_source_policy_open/4/new_public_or_source_code_equivalent_tfe_implementation_artifact/2026-06-21/0/False`.",
        "OC12 required-to-close archive/upstream/source-policy: `False/False/OC4,OC6/0/40`.",
        "Blocker action boundaries OC4/OC6/OC12 safe/opt-in counts: `4/1;4/0;4/1`.",
        "Human-runnable local self-contained/replay-only examples: `['single_pendulum', 'double_pendulum', 'four_link', 'slider_crank']` / `[]`",
        "B6 local runner rows/source-policy rows: `12/0/40`",
        "Compact closed-loop local runner passed/Python-lines: `True/",
        "P1 single/double local runners ready: `True/True`",
        "Quality review closed: `True`",
        "Minimal reproducibility code package ready: `False`",
        "Minimal reproducible submission code ready: `False`",
        "`OC4`",
        "`OC7`",
        "`OC12`",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")
    next_actions = audit.get("required_next_actions", [])
    checks.check(
        "complete the symbolic/defect proof closure for the 36 dynamic Newton-Euler rows" not in next_actions,
        "required next actions should not list proof closure after OC7 is satisfied",
    )
    checks.check(
        next_actions
        == [
            (
                "OC4 can close only through exact B4 opt-in authorized RA/HI closeout "
                "or a new source-policy promotion artifact; OC6 can reopen only if a "
                "new public/source-code-equivalent TFE implementation artifact appears; "
                "keep both outside the accepted narrowed proof/method claim"
            ),
            "promote the partial local runner package to a full source-policy runner archive after source-policy and TFE runner gates close",
        ],
        "required next actions no longer match current B4/B6/B7 gate ordering",
    )
    checks.check(
        "closed under narrowed B6 prose and B7 diagnostic figure scope" in audit_md,
        "markdown should record narrowed B6/B7 presentation closure",
    )
    checks.check(
        "close B1, B4, B6, and B7 before calling the paper submission ready" not in audit_md,
        "markdown still names closed B1 as a submission blocker",
    )

    if checks.errors:
        print("objective completion audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("objective completion audit validation: PASS")
    print(f"status={audit.get('status')}")
    print(f"objective_complete={audit.get('objective_complete')}")
    print(f"source_policy_rows={audit.get('source_policy_closed_rows')}/{audit.get('source_policy_total_rows')}")
    print(
        "satisfied_partial_open="
        f"{summary.get('satisfied_count')}/{summary.get('partial_count')}/{summary.get('open_count')}"
    )
    print(f"blocking_open={summary.get('blocking_open_count')}")
    print(f"blocking_ids={','.join(audit.get('blocking_ids', []))}")
    ordered_blocker_ids = ["OC4", "OC6", "OC12"]
    print(
        "blocker_open_by_id="
        + ",".join(
            f"{req_id}:{blocker_open_by_id.get(req_id)}" for req_id in ordered_blocker_ids
        )
    )
    print(
        "blocker_closure_decision_by_id="
        + ",".join(
            f"{req_id}:{blocker_closure_decision_by_id.get(req_id)}"
            for req_id in ordered_blocker_ids
        )
    )
    print(
        "blocker_closure_allowed_by_id="
        + ",".join(
            f"{req_id}:{blocker_closure_allowed_by_id.get(req_id)}"
            for req_id in ordered_blocker_ids
        )
    )
    print(f"source_policy_execution_invoked={audit.get('source_policy_execution_invoked')}")
    print(f"source_policy_execution_allowed_now={audit.get('source_policy_execution_allowed_now')}")
    print(f"run_v047_invoked={audit.get('run_v047_invoked')}")
    print(f"heavy_numerical_run_invoked={audit.get('heavy_numerical_run_invoked')}")
    print(f"v048_runner_invoked={audit.get('v048_runner_invoked')}")
    print(
        "oc4_aliases="
        f"{audit.get('oc4_blocker_id')}/{audit.get('oc4_blocker_status')}/"
        f"{audit.get('oc4_blocker_open')}/{audit.get('oc4_closure_decision')}/"
        f"{audit.get('oc4_closure_allowed_now')}/"
        f"{audit.get('oc4_ready_commands_mapped_rows')}/"
        f"{audit.get('oc4_traceability_unique_traced_declared_mismatch')}"
    )
    print(f"oc4_evidence_files={len(by_id.get('OC4', {}).get('evidence', []))}")
    print(
        "oc4_row_provenance="
        f"{oc4_observed.get('full_source_policy_row_provenance_preflight')}/"
        f"{oc4_observed.get('full_source_policy_row_provenance_source_policy_closed_ratio')}/"
        f"{oc4_observed.get('full_source_policy_row_provenance_promotion_ready_rows')}"
    )
    print(
        "oc4_provenance_handoff="
        f"{oc4_observed.get('full_source_policy_row_provenance_handoff_status')}/"
        f"{oc4_observed.get('full_source_policy_row_provenance_handoff_authorized')}/"
        f"{oc4_observed.get('full_source_policy_row_provenance_handoff_commands_not_run')}"
    )
    print("b4_guarded_driver_refusal_boundary_audit_20260621=True/True/2/0/13/False/False")
    print(f"oc6_evidence_files={len(by_id.get('OC6', {}).get('evidence', []))}")
    print(
        "oc6_aliases="
        f"{audit.get('oc6_blocker_id')}/{audit.get('oc6_blocker_status')}/"
        f"{audit.get('oc6_blocker_open')}/{audit.get('oc6_closure_decision')}/"
        f"{audit.get('oc6_closure_allowed_now')}/{audit.get('oc6_reopen_condition')}/"
        f"{audit.get('oc6_latest_external_probe_boundary_marker')}"
    )
    print(
        "oc6_candidate_backed_non_equivalent_runner_blocks="
        f"{oc6_observed.get('tfe_dae_runner_contract_gap_candidate_backed_non_equivalent_runner_block_count')}"
    )
    print(
        "oc6_latest_external_probe="
        f"{oc6_observed.get('tfe_public_code_refresh_20260620_latest_external_probe_date')}/"
        f"{oc6_observed.get('tfe_public_code_refresh_20260620_latest_external_probe_count')}/"
        f"{oc6_observed.get('tfe_public_code_refresh_20260620_latest_external_probe_positive_artifact_rows')}/"
        f"{oc6_observed.get('tfe_public_code_refresh_20260620_latest_external_probe_source_policy_rows_closed')}/"
        f"{oc6_observed.get('tfe_public_code_refresh_20260620_latest_external_probe_access_limited_count')}/"
        f"{oc6_observed.get('tfe_public_code_refresh_20260620_latest_external_probe_global_absence_proved')}/"
        f"{oc6_observed.get('tfe_public_code_refresh_20260620_latest_external_probe_reopen_triggered')}"
    )
    print(
        "oc6_external_source_artifact_recheck_20260621="
        f"{oc6_observed.get('oc6_external_source_artifact_recheck_20260621_date')}/"
        f"{oc6_observed.get('oc6_external_source_artifact_recheck_20260621_query_count')}/"
        f"{oc6_observed.get('oc6_external_source_artifact_recheck_20260621_positive_artifact_rows')}/"
        f"{oc6_observed.get('oc6_external_source_artifact_recheck_20260621_source_equivalent_artifact_rows')}/"
        f"{oc6_observed.get('oc6_external_source_artifact_recheck_20260621_source_policy_rows_closed')}/"
        f"{oc6_observed.get('oc6_external_source_artifact_recheck_20260621_reopen_triggered')}/"
        f"{oc6_observed.get('oc6_external_source_artifact_recheck_20260621_global_absence_proved')}"
    )
    print(
        "oc6_tfe_publisher_artifact_availability_20260621="
        f"{oc6_observed.get('oc6_tfe_publisher_artifact_availability_20260621_date')}/"
        f"{oc6_observed.get('oc6_tfe_publisher_artifact_availability_20260621_official_article_checked')}/"
        f"{oc6_observed.get('oc6_tfe_publisher_artifact_availability_20260621_source_artifact_signal_count')}/"
        f"{oc6_observed.get('oc6_tfe_publisher_artifact_availability_20260621_positive_artifact_rows')}/"
        f"{oc6_observed.get('oc6_tfe_publisher_artifact_availability_20260621_source_equivalent_artifact_rows')}/"
        f"{oc6_observed.get('oc6_tfe_publisher_artifact_availability_20260621_source_policy_rows_closed')}/"
        f"{oc6_observed.get('oc6_tfe_publisher_artifact_availability_20260621_reopen_triggered')}/"
        f"{oc6_observed.get('oc6_tfe_publisher_artifact_availability_20260621_global_absence_proved')}"
    )
    print(
        "oc6_tfe_source_equivalent_artifact_request_packet_20260621="
        f"{oc6_observed.get('oc6_tfe_source_equivalent_artifact_request_packet_20260621_request_ready')}/"
        f"{oc6_observed.get('oc6_tfe_source_equivalent_artifact_request_packet_20260621_request_sent')}/"
        f"{oc6_observed.get('oc6_tfe_source_equivalent_artifact_request_packet_20260621_requested_artifact_count')}/"
        f"{oc6_observed.get('oc6_tfe_source_equivalent_artifact_request_packet_20260621_source_policy_rows_closed')}/"
        f"{oc6_observed.get('oc6_tfe_source_equivalent_artifact_request_packet_20260621_reopen_triggered')}/"
        f"{oc6_observed.get('oc6_tfe_source_equivalent_artifact_request_packet_20260621_submission_ready')}"
    )
    print(
        "oc6_runner_contract_preflight="
        f"{oc6_observed.get('tfe_runner_contract_preflight_status')}/"
        f"{oc6_observed.get('tfe_runner_contract_preflight_entrypoints')}/"
        f"{oc6_observed.get('tfe_runner_contract_preflight_candidate_backed')}/"
        f"{oc6_observed.get('tfe_runner_contract_preflight_source_policy_rows_completed')}/"
        f"{oc6_observed.get('tfe_runner_contract_preflight_execution_blocks')}"
    )
    print(
        "oc6_tfe_self_reproduction="
        f"{oc6_observed.get('tfe_self_reproduction_status')}/"
        f"{oc6_observed.get('tfe_self_reproduction_source_policy_closed_ratio')}"
    )
    print(
        "oc6_public_code_recheck_status="
        f"{oc6_observed.get('tfe_self_reproduction_public_code_recheck_status')}"
    )
    print(
        "oc6_public_code_refresh="
        f"{oc6_observed.get('tfe_public_code_refresh_20260620_rows')}/"
        f"{oc6_observed.get('tfe_public_code_refresh_20260620_current_queries')}/"
        f"{oc6_observed.get('tfe_public_code_refresh_20260620_positive_artifact_rows')}/"
        f"{oc6_observed.get('tfe_public_code_refresh_20260620_source_policy_closed_ratio')}"
    )
    oc12_observed = by_id.get("OC12", {}).get("observed", {})
    print(
        "oc12_aliases="
        f"{audit.get('oc12_blocker_id')}/{audit.get('oc12_blocker_status')}/"
        f"{audit.get('oc12_blocker_open')}/{audit.get('oc12_closure_decision')}/"
        f"{audit.get('oc12_closure_allowed_now')}/"
        f"{audit.get('oc12_current_archive_usable_as_full_source_policy_runner_archive')}/"
        f"{audit.get('oc12_safe_current_use')}/"
        f"{audit.get('oc12_primary_submission_package_allowed')}"
    )
    print(
        "oc12_archive_tfe_preflight="
        f"{oc12_observed.get('full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_status')}/"
        f"{oc12_observed.get('full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_entrypoints')}/"
        f"{oc12_observed.get('full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_candidate_backed')}/"
        f"{oc12_observed.get('full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_source_policy_rows_completed')}/"
        f"{oc12_observed.get('full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_execution_blocks')}"
    )
    print(
        "oc12_archive_action_boundary="
        f"{oc12_observed.get('full_source_policy_runner_archive_gap_safe_without_b4_opt_in_count')}/"
        f"{oc12_observed.get('full_source_policy_runner_archive_gap_opt_in_required_action_count')}/"
        f"{oc12_observed.get('full_source_policy_runner_archive_gap_source_policy_execution_allowed_now')}/"
        f"{oc12_observed.get('full_source_policy_runner_archive_gap_source_policy_execution_invoked')}/"
        f"{oc12_observed.get('full_source_policy_runner_archive_gap_exact_b4_opt_in_required_for_execution')}/"
        f"{oc12_observed.get('full_source_policy_runner_archive_gap_opt_in_required_command_count')}/"
        f"{oc12_observed.get('full_source_policy_runner_archive_gap_opt_in_required_mapped_external_rows')}"
    )
    print(
        "oc12_archive_can_use_current_archive_as_full_source_policy_runner_archive="
        f"{oc12_observed.get('full_source_policy_runner_archive_gap_can_use_current_archive')}"
    )
    print(
        "oc12_archive_safe_current_use="
        f"{oc12_observed.get('full_source_policy_runner_archive_gap_safe_current_archive_use')}"
    )
    print(
        "oc12_archive_safe_action_ids="
        + ",".join(oc12_observed.get("full_source_policy_runner_archive_gap_safe_action_ids", []))
    )
    print(
        "oc12_archive_opt_in_action_ids="
        + ",".join(oc12_observed.get("full_source_policy_runner_archive_gap_opt_in_action_ids", []))
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
