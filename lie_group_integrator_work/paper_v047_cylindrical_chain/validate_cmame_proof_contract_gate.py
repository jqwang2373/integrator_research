#!/usr/bin/env python3
"""Read-only validator for the CMAME proof-contract gate."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
V048 = ROOT / "v048_cross_paper_same_test_benchmarks" / "results"
GATE_JSON = PAPER / "CMAME_PROOF_CONTRACT_GATE.json"
GATE_MD = PAPER / "CMAME_PROOF_CONTRACT_GATE.md"
MANUSCRIPT = PAPER / "main_cmame.tex"
ORDER_GATE = PAPER / "ORDER_ACCEPTANCE_GATE.json"
DYNAMIC_ORACLE = PAPER / "DYNAMIC_ROW_ORACLE_GATE.json"
BLOCKER_GATE = PAPER / "CMAME_BLOCKER_CLOSURE_GATE.json"
PROOF_MATRIX = PAPER / "PROOF_EVIDENCE_MATRIX.md"
NUMERICAL_SCALE_AUDIT_JSON = PAPER / "PROOF_NUMERICAL_SCALE_AUDIT.json"
NUMERICAL_SCALE_AUDIT_MD = PAPER / "PROOF_NUMERICAL_SCALE_AUDIT.md"
SOLVER_SCALE_AUDIT_JSON = PAPER / "PROOF_SOLVER_SCALE_AUDIT.json"
SOLVER_SCALE_AUDIT_MD = PAPER / "PROOF_SOLVER_SCALE_AUDIT.md"
PROOF_CLOSURE = PAPER / "PROOF_CLOSURE_MANIFEST.json"
PROOF_CLAIM_TRACEABILITY = PAPER / "PROOF_CLAIM_TRACEABILITY_AUDIT.json"
KINEMATIC_DEFECT_JSON = PAPER / "KINEMATIC_ROW_DEFECT_CERTIFICATE.json"
KINEMATIC_DEFECT_MD = PAPER / "KINEMATIC_ROW_DEFECT_CERTIFICATE.md"
NEWTON_EULER_OBLIGATION_JSON = PAPER / "NEWTON_EULER_DEFECT_OBLIGATION_GATE.json"
NEWTON_EULER_OBLIGATION_MD = PAPER / "NEWTON_EULER_DEFECT_OBLIGATION_GATE.md"
MANIFEST = PAPER / "SUBMISSION_ARTIFACT_MANIFEST.json"
FLAT_MANUSCRIPT = PAPER / "cmame_submission_flat" / "main_cmame_submission.tex"
PDF_TEXT = PAPER / "main_cmame.txt"
FLAT_PDF_TEXT = PAPER / "cmame_submission_flat" / "main_cmame_submission.txt"
R2E = V048 / "closed_loop_residual_to_error_theorem_obligations.json"

PROOF_CONDITIONAL_BOUNDARY_TOKENS = [
    "Conditional sixth-order theorem",
    "conditional local-defect-to-global-error argument",
    "finite-run solver data, not as an asymptotic solver-error proof",
    "proof certificates supply the accepted direct-route residual/Jacobian binding used by the bridge",
    "AD-expanded implementation-path derivative-cell certificate records the derivative identities used by that binding",
    "stage-residual condition",
    "one-step accepted residual defect statement only",
    "local accepted root",
    "compact-tube inverse condition",
    "Gauss-predictor branch",
    "finite rank probes are not a compact-tube inverse proof",
    "not a global uniqueness claim for remote nonlinear roots",
    "not a certificate of global nonlinear solver convergence",
    "triangle inequality over Gauss truncation",
    "uniform Gauss truncation constant",
    "compact trajectory tube",
    "explicit stage-residual-to-root estimate",
    "The constants in these four bounds are uniform",
    "reported-grid maximum",
    "explicit local-defect",
    "explicit uniform constant sum",
    "same-initial-state reduced-chart reported-grid estimate",
    "same-initial-state reported-grid",
    "reported fixed time grid",
    "reported time grid",
    "exact final-time divisibility is not required",
    "same reported time grid",
    "one-step stability scale",
    "ordinary compact-tube Lipschitz",
    "tube-retention bootstrap",
    "not an invariant-region proof",
    "closed endpoint anchor",
    "endpoint-ball margin",
    "endpoint-closure local right inverse",
    "local right-inverse perturbation",
    "Pointwise right-invertibility",
    "strong local residual inverse",
    "strong local residual inverse used by Lemma",
    "local branch contract",
    "averaged Jacobian",
    "pointwise Jacobian invertibility alone",
    "proof dependencies used by the theorem",
    "finite solver probes attach only to P6",
    "residual tables are recorded only as diagnostics for the open P7 residual-to-error boundary",
    "primitive symbolic route is a separate primitive-route record",
    "is not an input to the PC2 stage-residual condition",
    "implication would have to prove a bound",
    "uniform stability or inf-sup constant on the reported branch",
    "small residual norms alone are not a trajectory-error theorem",
    "residual rows remain diagnostics even when their measured norms are small",
    "no residual-to-trajectory-error transfer theorem is accepted in this manuscript",
    "not accepted dynamic order rows",
]


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8", errors="replace")


def contains_normalized(text: str, token: str) -> bool:
    def variants(value: str) -> set[str]:
        lines = []
        for line in value.splitlines():
            stripped = line.replace("\f", "").strip()
            if stripped.isdigit():
                continue
            lines.append(line)
        collapsed = " ".join(" ".join(lines).split())
        return {
            collapsed,
            collapsed.replace("- ", "-"),
            collapsed.replace("- ", ""),
            collapsed.replace("-", ""),
            collapsed.replace("- ", "").replace("-", ""),
        }

    return token in text or any(
        token_variant in text_variant
        for token_variant in variants(token)
        for text_variant in variants(text)
    )


def require_tokens(checks: Checks, text: str, tokens: list[str], label: str) -> None:
    for token in tokens:
        checks.check(contains_normalized(text, token), f"{label} missing token: {token}")


def blocker_by_id(blocker_gate: dict[str, Any], blocker_id: str) -> dict[str, Any]:
    for blocker in blocker_gate.get("blockers", []):
        if isinstance(blocker, dict) and blocker.get("id") == blocker_id:
            return blocker
    return {}


def main() -> int:
    checks = Checks()
    try:
        gate = read_json(GATE_JSON)
        gate_md = read_text(GATE_MD)
        manuscript = read_text(MANUSCRIPT)
        flat_manuscript = read_text(FLAT_MANUSCRIPT)
        pdf_text = read_text(PDF_TEXT)
        flat_pdf_text = read_text(FLAT_PDF_TEXT)
        order_gate = read_json(ORDER_GATE)
        dynamic_oracle = read_json(DYNAMIC_ORACLE)
        blocker_gate = read_json(BLOCKER_GATE)
        proof_matrix = read_text(PROOF_MATRIX)
        numerical_scale_audit = read_json(NUMERICAL_SCALE_AUDIT_JSON)
        numerical_scale_audit_md = read_text(NUMERICAL_SCALE_AUDIT_MD)
        solver_scale_audit = read_json(SOLVER_SCALE_AUDIT_JSON)
        solver_scale_audit_md = read_text(SOLVER_SCALE_AUDIT_MD)
        proof_closure = read_json(PROOF_CLOSURE)
        proof_claim_traceability = read_json(PROOF_CLAIM_TRACEABILITY)
        kinematic_defect = read_json(KINEMATIC_DEFECT_JSON)
        kinematic_defect_md = read_text(KINEMATIC_DEFECT_MD)
        newton_euler_obligation = read_json(NEWTON_EULER_OBLIGATION_JSON)
        newton_euler_obligation_md = read_text(NEWTON_EULER_OBLIGATION_MD)
        manifest = read_json(MANIFEST)
        r2e = read_json(R2E)
    except Exception as exc:  # noqa: BLE001 - concise CLI failure.
        print(f"cmame_proof_contract_gate=FAIL\n- {exc}")
        return 1

    theorem = gate.get("theorem_contract", {})
    comparator = gate.get("comparator", {})
    r2e_contract = gate.get("residual_to_error_contract", {})
    order_contract = order_gate.get("proof_contract", {})
    dynamic_boundary = dynamic_oracle.get("acceptance_boundary", {})
    b1 = blocker_by_id(blocker_gate, "B1")
    b3 = blocker_by_id(blocker_gate, "B3")
    b4 = blocker_by_id(blocker_gate, "B4")
    b6 = blocker_by_id(blocker_gate, "B6")
    b7 = blocker_by_id(blocker_gate, "B7")
    numerical_scale_boundary = numerical_scale_audit.get("proof_boundary", {})
    readiness_boundary = gate.get("readiness_boundary", {})
    theorem_traceability = gate.get("manuscript_theorem_traceability", {})
    theorem_statement_boundary = proof_closure.get("theorem_statement_boundary", {})
    manuscript_traceability = proof_closure.get("manuscript_traceability", {})
    proof_closure_anchor_map = proof_closure.get("manuscript_anchor_map", {})
    proof_claim_anchor_map = proof_claim_traceability.get("manuscript_anchor_map", {})
    remaining_gate_scope = gate.get("remaining_gate_scope", {})
    expected_theorem_assumption_anchor_ids = ["P1", "P2", "P3", "P4", "P5", "P6", "P7"]
    expected_global_boundaries = [
        "full_source_policy_package_ready",
        "theorem_level_eta_h_solver_policy_evidence",
        "closed_residual_to_error_theorem_for_mechanism_rows",
    ]
    expected_narrowed_statuses = {"B4": b4.get("status"), "B6": b6.get("status"), "B7": b7.get("status")}

    checks.check(gate.get("schema") == "cmame-proof-contract-gate-v1", "schema changed")
    checks.check(
        gate.get("status") == "open_explicitly_conditional_not_submission_ready",
        "status changed",
    )
    checks.check(gate.get("submission_ready") is False, "proof gate must not claim submission ready")
    checks.check(
        gate.get("submission_ready_scope")
        == "theorem_level_global_proof_contract_not_narrowed_claim_package_decision",
        "proof gate submission-ready scope changed",
    )
    checks.check(
        readiness_boundary.get("proof_contract_gate_scope")
        == "conditional_theorem_contract_with_eta_h_and_residual_to_error_boundaries",
        "proof contract gate scope changed",
    )
    checks.check(
        readiness_boundary.get("narrowed_claim_b4_b6_b7_statuses")
        == expected_narrowed_statuses
        == {"B4": "closed", "B6": "closed", "B7": "closed"},
        "proof contract narrowed-claim statuses changed",
    )
    checks.check(
        readiness_boundary.get("theorem_level_conditions_retained")
        == [
            "regular_smooth_fullva_lift",
            "uniform_stage_jacobian_invertibility",
            "gauss_predictor_branch_uniform_inverse",
            "accepted_one_step_stability_1_plus_Ch",
            "accepted_tube_retention_bootstrap",
            "accepted_endpoint_closure_closed_anchor",
            "accepted_endpoint_closure_local_ball_margin",
            "accepted_endpoint_closure_local_right_inverse",
            "accepted_endpoint_closure_explicit_constant",
            "accepted_newton_residual_strong_local_inverse",
            "implemented_residual_defect_O_h7",
            "eta_h_le_c_eta_h7",
            "per_step_branch_selected_eta_h_le_c_eta_h7",
            "explicit_uniform_gauss_truncation_constant",
            "explicit_stage_residual_to_root_constant",
            "uniform_four_term_local_defect_constants",
            "explicit_uniform_local_defect_constant_sum",
            "explicit_global_grid_constant",
            "explicit_qv_reporting_constant",
            "grid_point_local_to_global_transfer",
            "reported_time_grid_defined_by_tn_equals_nh",
            "no_exact_final_time_divisibility_requirement",
        ],
        "proof contract theorem-level retained conditions changed",
    )
    checks.check(
        readiness_boundary.get("global_submission_boundaries_retained") == expected_global_boundaries,
        "proof contract readiness-boundary global boundaries changed",
    )
    checks.check(
        gate.get("remaining_global_submission_boundaries") == expected_global_boundaries,
        "proof contract remaining global boundaries changed",
    )
    checks.check(
        theorem_traceability.get("source_manifest") == "PROOF_CLOSURE_MANIFEST.json",
        "proof contract theorem traceability source manifest missing",
    )
    checks.check(
        theorem_traceability.get("proof_closure_status") == proof_closure.get("status"),
        "proof contract theorem traceability proof-closure status mismatch",
    )
    checks.check(
        theorem_traceability.get("accepted_theorem_label")
        == theorem_statement_boundary.get("accepted_theorem_label")
        == "thm:g6fullva-order",
        "proof contract accepted theorem label changed",
    )
    checks.check(
        theorem_traceability.get("accepted_method_order")
        == theorem_statement_boundary.get("accepted_method_order")
        == 6,
        "proof contract accepted method order changed",
    )
    checks.check(
        theorem_traceability.get("accepted_local_defect_order")
        == theorem_statement_boundary.get("accepted_local_defect_order")
        == 7,
        "proof contract accepted local defect order changed",
    )
    checks.check(
        theorem_traceability.get("theorem_statement_labels_present")
        == theorem_statement_boundary.get("all_required_labels_present_main_and_flat")
        is True,
        "proof contract theorem labels not traced to manuscript",
    )
    checks.check(
        theorem_traceability.get("conditional_theorem_boundary_present")
        == theorem_statement_boundary.get("conditional_theorem_boundary_present_main_and_flat")
        is True,
        "proof contract conditional theorem boundary not traced to manuscript",
    )
    checks.check(
        theorem_traceability.get("conditional_proof_claims_mapped_to_manuscript")
        == manuscript_traceability.get("conditional_proof_claims_mapped_to_manuscript")
        is True,
        "proof contract proof claims not mapped to manuscript",
    )
    checks.check(
        theorem_traceability.get("proof_dependency_graph_present")
        == manuscript_traceability.get("proof_dependency_graph_present_main_and_flat")
        is True,
        "proof contract proof dependencies missing",
    )
    checks.check(
        theorem_traceability.get("proof_traceability_table_present")
        == manuscript_traceability.get("proof_traceability_table_present_main_and_flat")
        is True,
        "proof contract proof traceability table missing",
    )
    checks.check(
        theorem_traceability.get("dynamic_proof_closure_matrix_present")
        == manuscript_traceability.get("dynamic_proof_closure_matrix_present_main_and_flat")
        is True,
        "proof contract dynamic proof closure matrix missing",
    )
    checks.check(
        theorem_traceability.get("primitive_lane_boundary_present")
        == manuscript_traceability.get("primitive_lane_boundary_present_main_and_flat")
        is True,
        "proof contract primitive-route boundary missing",
    )
    checks.check(
        theorem_traceability.get("residual_nonpromotion_present")
        == manuscript_traceability.get("residual_to_error_nonpromotion_present_main_and_flat")
        is True,
        "proof contract residual nonpromotion traceability missing",
    )
    checks.check(
        theorem_traceability.get("eta_h_theorem_condition_retained")
        == theorem_statement_boundary.get("eta_h_theorem_condition_retained")
        is True,
        "proof contract eta_h theorem condition not retained",
    )
    checks.check(
        theorem_traceability.get("eta_h_solver_policy_evidence_closed")
        == theorem_statement_boundary.get("eta_h_solver_policy_evidence_closed")
        is False,
        "proof contract overclaims eta_h solver-policy closure",
    )
    checks.check(
        theorem_traceability.get("fixed_tolerance_runs_are_asymptotic_proof")
        == theorem_statement_boundary.get("fixed_tolerance_runs_are_asymptotic_proof")
        is False,
        "proof contract promotes fixed-tolerance runs to asymptotic proof",
    )
    checks.check(
        theorem_traceability.get("residual_to_error_not_promoted")
        == theorem_statement_boundary.get("does_not_promote_residual_to_error")
        is True,
        "proof contract lost residual-to-error nonpromotion",
    )
    checks.check(
        theorem_traceability.get("source_policy_or_full_tfe_not_promoted")
        == theorem_statement_boundary.get("does_not_promote_source_policy_or_full_tfe")
        is True,
        "proof contract lost source-policy/full-TFE nonpromotion",
    )
    checks.check(
        theorem_traceability.get("does_not_change_proof_closure_state")
        == manuscript_traceability.get("does_not_change_proof_closure_state")
        is True,
        "proof contract traceability changed proof closure state",
    )
    checks.check(
        theorem_traceability.get("manuscript_anchor_map_present")
        == proof_closure_anchor_map.get("all_label_anchors_present")
        is True,
        "proof contract manuscript anchor map is not traced to proof closure manifest",
    )
    checks.check(
        theorem_traceability.get("manuscript_anchor_label_count")
        == proof_closure_anchor_map.get("label_anchor_count")
        == 24,
        "proof contract manuscript anchor label count changed",
    )
    checks.check(
        theorem_traceability.get("theorem_assumption_anchor_map_present")
        == proof_closure_anchor_map.get("all_theorem_assumption_anchors_present")
        is True,
        "proof contract theorem-assumption anchor map is not traced to proof closure manifest",
    )
    checks.check(
        theorem_traceability.get("theorem_assumption_anchor_count")
        == proof_closure_anchor_map.get("theorem_assumption_anchor_count")
        == 7,
        "proof contract theorem-assumption anchor count changed",
    )
    checks.check(
        theorem_traceability.get("theorem_assumption_anchor_ids")
        == proof_closure_anchor_map.get("theorem_assumption_anchor_ids")
        == expected_theorem_assumption_anchor_ids,
        "proof contract theorem-assumption anchor IDs changed",
    )
    checks.check(
        theorem_traceability.get("proof_closure_proof_claim_anchor_maps_match") is True
        and proof_closure_anchor_map == proof_claim_anchor_map,
        "proof contract proof-closure/proof-claim manuscript anchor maps diverged",
    )
    checks.check(
        theorem_traceability.get("anchor_evidence_sources")
        == ["PROOF_CLOSURE_MANIFEST.json", "PROOF_CLAIM_TRACEABILITY_AUDIT.json"],
        "proof contract manuscript anchor evidence sources changed",
    )
    checks.check(
        remaining_gate_scope.get("narrowed_claim_b4_b6_b7_statuses") == expected_narrowed_statuses,
        "proof contract remaining narrowed-claim statuses changed",
    )
    checks.check(
        remaining_gate_scope.get("b4_b6_b7_closed_elsewhere_under_narrowed_claim") is True,
        "proof contract lost narrowed-claim B4/B6/B7 closure marker",
    )
    checks.check(
        remaining_gate_scope.get("eta_h_O_h7_solver_policy_evidence") is False
        and remaining_gate_scope.get("eta_h_theorem_condition_retained") is True,
        "proof contract eta_h boundary changed",
    )
    checks.check(
        remaining_gate_scope.get("residual_to_error_obligation_count") == 7
        and remaining_gate_scope.get("residual_to_error_blocking_obligation_count") == 7,
        "proof contract residual-to-error obligation counts changed",
    )
    checks.check(
        remaining_gate_scope.get("accepted_residual_to_error_theorem") is False
        and remaining_gate_scope.get("accepted_dynamic_order_count_by_residual_to_error") == 0,
        "proof contract residual-to-error acceptance boundary changed",
    )
    checks.check(
        remaining_gate_scope.get("global_submission_boundaries_retained") == expected_global_boundaries,
        "proof contract remaining gate global boundaries changed",
    )
    checks.check(gate.get("proof_mode") == "conditional_consistency_transfer", "proof mode changed")
    checks.check(gate.get("accepted_method") == "Gauss6/FullVA", "accepted method changed")
    checks.check(gate.get("accepted_method_order") == 6, "accepted order changed")
    checks.check(gate.get("accepted_local_defect_order") == 7, "local defect order changed")
    checks.check(gate.get("accepted_global_error_order") == 6, "global order changed")
    checks.check(comparator.get("expected_order") == 5, "comparator order changed")

    checks.check(theorem.get("regular_smooth_fullva_lift_required") is True, "smooth lift requirement changed")
    checks.check(theorem.get("stage_jacobian_uniformly_invertible_required") is True, "Jacobian requirement changed")
    checks.check(
        theorem.get("stage_jacobian_uniform_inverse_required_on_gauss_predictor_branch") is True,
        "Gauss-predictor branch inverse requirement missing",
    )
    checks.check(
        theorem.get("finite_rank_probes_sufficient_for_stage_inverse") is False,
        "finite rank probes promoted to stage inverse proof",
    )
    checks.check(
        theorem.get("accepted_one_step_stability_required")
        == "||Psi_h(y)-Psi_h(ybar)|| <= (1+C_s h)||y-ybar||",
        "accepted one-step stability requirement changed",
    )
    checks.check(
        theorem.get("accepted_tube_retention_bootstrap_required") is True,
        "tube-retention bootstrap requirement missing",
    )
    checks.check(
        theorem.get("local_to_global_transfer_is_invariant_region_proof") is False,
        "local-to-global invariant-region overclaim",
    )
    checks.check(
        theorem.get("mere_compact_lipschitz_stability_is_sufficient") is False,
        "compact Lipschitz stability overclaim",
    )
    checks.check(
        theorem.get("accepted_endpoint_closure_local_right_inverse_required") is True,
        "endpoint-closure local right-inverse requirement missing",
    )
    checks.check(
        theorem.get("accepted_endpoint_closure_closed_anchor_required") is True,
        "endpoint-closure closed anchor requirement missing",
    )
    checks.check(
        theorem.get("accepted_endpoint_closure_local_ball_margin_required") is True,
        "endpoint-closure local ball margin requirement missing",
    )
    checks.check(
        theorem.get("endpoint_closure_pointwise_right_inverse_alone_is_sufficient") is False,
        "endpoint-closure pointwise right-inverse overclaim",
    )
    checks.check(
        theorem.get("endpoint_closure_raw_defect_bound_has_explicit_constant") is True,
        "endpoint-closure raw defect bound is not marked with an explicit constant",
    )
    checks.check(
        theorem.get("endpoint_closure_raw_defect_constant_symbol") == "C_{E,raw}",
        "endpoint-closure raw defect constant symbol changed",
    )
    checks.check(
        theorem.get("endpoint_closure_perturbation_bound_has_explicit_constant") is True,
        "endpoint-closure perturbation bound is not marked with an explicit constant",
    )
    checks.check(
        theorem.get("endpoint_closure_perturbation_constant_formula") == "C_E = 4 M_E^ri C_{E,raw}",
        "endpoint-closure perturbation constant formula changed",
    )
    checks.check(
        theorem.get("accepted_newton_residual_strong_local_inverse_required") is True,
        "strong local residual inverse requirement missing",
    )
    checks.check(
        theorem.get("averaged_jacobian_invertibility_required") is True,
        "averaged-Jacobian invertibility requirement missing",
    )
    checks.check(
        theorem.get("pointwise_jacobian_invertibility_alone_is_sufficient_for_inexact_newton") is False,
        "pointwise Jacobian invertibility overclaim",
    )
    checks.check(theorem.get("implemented_residual_defect_required") == "O(h^7)", "residual defect requirement changed")
    checks.check(
        theorem.get("gauss_truncation_bound_has_explicit_uniform_constant") is True,
        "Gauss truncation bound is not marked as an explicit uniform constant",
    )
    checks.check(
        theorem.get("gauss_truncation_constant_uniform_on_compact_trajectory_tube") is True,
        "Gauss truncation constant is not marked uniform on the compact trajectory tube",
    )
    checks.check(
        theorem.get("stage_residual_to_root_bound_has_explicit_constant") is True,
        "stage residual-to-root bound is not marked as an explicit constant transfer",
    )
    checks.check(
        theorem.get("stage_residual_to_root_constant_formula") == "C_Z = 2 M C_R",
        "stage residual-to-root constant formula changed",
    )
    checks.check(
        theorem.get("stage_root_endpoint_perturbation_constant_formula") == "C_A = M_E C_Z",
        "stage-root endpoint perturbation constant formula changed",
    )
    checks.check(
        theorem.get("accepted_root_existence_proved_by_stage_residual_lemma") is True,
        "accepted root existence is not marked as proved by the stage-residual lemma",
    )
    checks.check(
        theorem.get("accepted_root_existence_not_assumed_as_isolated_root_premise") is True,
        "accepted root existence is still treated as an isolated-root premise",
    )
    checks.check(
        theorem.get("local_defect_constants_uniform_on_compact_proof_tube") is True,
        "local-defect constants are not marked uniform on the compact proof tube",
    )
    checks.check(
        theorem.get("local_defect_constants_uniform_over_accepted_steps") is True,
        "local-defect constants are not marked uniform over accepted steps",
    )
    checks.check(
        theorem.get("newton_error_controlled_by_compact_tube_eta_h_envelope") is True,
        "Newton term is not tied to the compact-tube eta_h envelope",
    )
    checks.check(
        theorem.get("newton_error_controlled_by_single_accepted_branch_eta_h_max") is True,
        "legacy Newton reported-grid eta_h maximum compatibility marker missing",
    )
    checks.check(
        theorem.get("newton_residual_to_stage_bound_has_explicit_constant") is True,
        "Newton residual-to-stage bound is not recorded with an explicit constant",
    )
    checks.check(
        theorem.get("newton_endpoint_output_map") == "P_h = C_h o E_h",
        "Newton endpoint-output map binding changed",
    )
    checks.check(
        theorem.get("newton_endpoint_output_map_bound")
        == "||P_h(Ztilde_A)-P_h(Z_A)|| <= C_N eta_h",
        "Newton endpoint-output perturbation bound changed",
    )
    checks.check(
        theorem.get("newton_endpoint_output_map_derivative_bound_includes_closure") is True,
        "Newton endpoint-output derivative bound does not include closure",
    )
    checks.check(
        theorem.get("newton_endpoint_output_map_lipschitz_constant_symbol") == "M_N",
        "Newton endpoint-output Lipschitz constant symbol changed",
    )
    checks.check(
        theorem.get("newton_residual_to_endpoint_perturbation_constant_formula") == "C_N = 2 M_A M_N",
        "Newton residual-to-endpoint perturbation constant formula changed",
    )
    checks.check(
        theorem.get("newton_eta_h_scaled_endpoint_bound_has_explicit_constant") is True,
        "Newton eta_h-scaled endpoint bound is not marked explicit",
    )
    checks.check(
        theorem.get("newton_eta_h_scaled_endpoint_bound_formula") == "C_N c_eta h^7",
        "Newton eta_h-scaled endpoint bound formula changed",
    )
    checks.check(
        theorem.get("local_defect_bound_has_explicit_uniform_constant_sum") is True,
        "local-defect bound does not record an explicit uniform constant sum",
    )
    checks.check(
        theorem.get("eta_h_constant_absorbed_into_local_defect_constant") is True,
        "eta_h constant is not recorded as absorbed into the local-defect constant",
    )
    checks.check(
        theorem.get("local_global_transfer_has_explicit_reduced_grid_constant") is True,
        "local-to-global reduced grid constant is not marked explicit",
    )
    checks.check(
        theorem.get("local_global_gronwall_factor_formula")
        == "Gamma_s(T) = (exp(C_s T)-1)/C_s with limit T at C_s=0",
        "local-to-global Gronwall factor formula changed",
    )
    checks.check(
        theorem.get("local_global_reduced_grid_constant_formula") == "C_red = C_loc Gamma_s(T)",
        "local-to-global reduced grid constant formula changed",
    )
    checks.check(
        theorem.get("qv_reporting_map_constant_distinct_from_residual_defect_constant") is True,
        "q/v reporting map constant is not distinguished from residual defect constant",
    )
    checks.check(
        theorem.get("qv_reporting_constant_formula") == "C_qv = C_{\\mathcal R} C_red",
        "q/v reporting constant formula changed",
    )
    checks.check(
        theorem.get("local_global_transfer_grid_point_error_required") is True,
        "local-to-global transfer is not marked as a same-initial-state reported-grid estimate",
    )
    checks.check(
        theorem.get("reported_time_grid_defined_by_tn_equals_nh") is True,
        "reported time grid is not marked as t_n=n h",
    )
    checks.check(
        theorem.get("exact_final_time_divisibility_required") is False,
        "local-to-global transfer still requires exact final-time divisibility",
    )
    checks.check(
        theorem.get("reported_qv_error_bound_uses_same_reported_time_grid") is True,
        "reported q/v error bound is not tied to the same reported time grid",
    )
    checks.check(
        theorem.get("reported_qv_error_bound_is_grid_maximum") is True,
        "reported q/v error bound is not marked as a grid maximum",
    )
    checks.check(
        theorem.get("newton_tolerance_policy") == "eta_h^tube <= c_eta h^7 for asymptotic proof",
        "Newton tolerance policy changed",
    )
    checks.check(
        theorem.get("per_step_newton_tolerance_policy")
        == "eta_h^tube <= c_eta h^7 on the compact proof tube; reported-grid eta_h^reported = max_{0<=n<N} eta_{h,n} is only its accepted branch-selected trajectory specialization",
        "per-step Newton tolerance policy changed",
    )
    checks.check(
        theorem.get("same_reduced_chart_initial_state_required") is True,
        "same reduced-chart initial state requirement missing",
    )
    checks.check(
        theorem.get("branch_selected_newton_solves_required") is True
        and theorem.get("newton_iterates_initialized_from_gauss_predictor_required") is True,
        "branch-selected Gauss-predictor Newton solve requirement missing",
    )
    checks.check(
        theorem.get("arbitrary_newton_initializations_select_branch") is False
        and theorem.get("remote_nonlinear_roots_select_branch") is False,
        "Newton branch-selection overclaim",
    )
    checks.check(theorem.get("fixed_tolerance_runs_are_asymptotic_proof") is False, "fixed-tolerance overclaim")
    checks.check(
        theorem.get("partial_formula_row_oracle_96_rows_checked") is True,
        "proof contract lost partial formula-row oracle marker",
    )
    checks.check(
        theorem.get("full_formula_row_oracle_132_rows_checked") is True,
        "proof contract lost full formula-row oracle marker",
    )
    checks.check(
        theorem.get("partial_kinematic_stage_defect_certificate_checked") is True,
        "proof contract lost partial kinematic defect certificate marker",
    )
    checks.check(
        theorem.get("partial_kinematic_stage_defect_rows_checked") == 96,
        "proof contract partial kinematic defect row count changed",
    )
    checks.check(
        theorem.get("newton_euler_stage_defect_certificate_open") is False,
        "proof contract still marks Newton-Euler defect certificate open",
    )
    checks.check(
        theorem.get("newton_euler_defect_obligation_gate_checked") is True,
        "proof contract lost Newton-Euler obligation gate marker",
    )
    checks.check(
        theorem.get("newton_euler_defect_obligation_rows") == 36,
        "proof contract Newton-Euler obligation row count changed",
    )
    checks.check(
        theorem.get("newton_euler_defect_open_obligation_count") == 1,
        "proof contract Newton-Euler open obligation count changed",
    )
    checks.check(
        theorem.get("newton_euler_defect_open_obligation_scope")
        == "symbolic_primitive_certificate_route_not_active_direct_pc2",
        "proof contract Newton-Euler open obligation scope changed",
    )
    checks.check(
        theorem.get("newton_euler_symbolic_primitive_open_obligation_count") == 1,
        "proof contract symbolic/primitive Newton-Euler open obligation count changed",
    )
    checks.check(
        theorem.get("newton_euler_symbolic_primitive_open_obligation_scope")
        == "symbolic_primitive_certificate_route_not_active_direct_pc2",
        "proof contract symbolic/primitive Newton-Euler open obligation scope changed",
    )
    checks.check(
        theorem.get("active_direct_newton_euler_open_obligation_count") == 0,
        "proof contract active direct Newton-Euler open obligation count changed",
    )
    checks.check(
        theorem.get("active_direct_newton_euler_stage_defect_closed") is True,
        "proof contract active direct Newton-Euler stage defect closure marker changed",
    )
    checks.check(
        theorem.get("active_direct_newton_euler_zero_residual_rows") == 36,
        "proof contract active direct Newton-Euler zero-row count changed",
    )
    checks.check(
        theorem.get("newton_euler_defect_closed_obligation_count") == 5,
        "proof contract Newton-Euler closed obligation count changed",
    )
    checks.check(
        theorem.get("newton_euler_defect_closed_obligation_ids")
        == [
            "translational_balance_identity",
            "rotational_balance_identity",
            "multiplier_wrench_consistency",
            "smooth_force_lift_consistency",
            "symbolic_runtime_row_equivalence",
        ],
        "proof contract Newton-Euler closed obligation ids changed",
    )
    checks.check(
        theorem.get("newton_euler_balance_identity_audit_checked") is True,
        "proof contract lost D1/D2 balance audit marker",
    )
    checks.check(
        theorem.get("newton_euler_balance_identity_closed_rows") == 36,
        "proof contract balance identity row count changed",
    )
    checks.check(
        theorem.get("newton_euler_symbolic_target_audit_checked") is True,
        "proof contract lost Newton-Euler symbolic target audit marker",
    )
    checks.check(theorem.get("newton_euler_symbolic_target_rows") == 36, "Newton-Euler symbolic target row count changed")
    checks.check(
        theorem.get("newton_euler_symbolic_target_inventory_complete") is True,
        "Newton-Euler symbolic target inventory marker missing",
    )
    checks.check(
        theorem.get("newton_euler_symbolic_defect_certificate_complete") is False,
        "proof contract overclaims Newton-Euler symbolic defect certificate",
    )
    checks.check(
        theorem.get("formula_row_ad_jacobian_oracle_checked") is True,
        "proof contract lost formula-row AD Jacobian oracle marker",
    )
    checks.check(
        theorem.get("formula_row_ad_jacobian_probe_count") == 3,
        "proof contract formula-row AD Jacobian probe count changed",
    )
    checks.check(
        float(theorem.get("formula_row_ad_jacobian_max_mismatch", 1.0)) <= 1.0e-12,
        "proof contract formula-row AD Jacobian mismatch too large",
    )
    checks.check(
        theorem.get("newton_euler_formula_oracle_complete") is True,
        "proof contract lost Newton-Euler formula oracle marker",
    )
    checks.check(
        theorem.get("finite_run_numerical_scale_audit_checked") is True,
        "proof contract lost numerical scale audit marker",
    )
    checks.check(
        theorem.get("finite_run_error_scale_supports_order_six") is True,
        "proof contract lost order-six finite-run scale marker",
    )
    checks.check(
        theorem.get("endpoint_global_closure_scale_supports_local_h7_budget") is True,
        "proof contract lost endpoint scale marker",
    )
    checks.check(theorem.get("solver_scale_audit_checked") is True, "proof contract lost solver-scale audit marker")
    checks.check(
        theorem.get("summary_level_solver_residuals_recorded") is True,
        "proof contract lost summary residual marker",
    )
    checks.check(
        abs(float(theorem.get("smooth_projected_reference_max_linear_residual_norm", 0.0)) - 2.800513564816292e-13)
        <= 1.0e-24,
        "proof contract smooth reference residual changed",
    )
    checks.check(
        abs(float(theorem.get("smooth_reference_eta_over_reference_h7", 0.0)) - 3584.657362964853) <= 1.0e-9,
        "proof contract smooth eta/h7 diagnostic changed",
    )
    checks.check(
        theorem.get("finite_scaled_tolerance_probe_recorded") is True,
        "proof contract lost finite scaled-tolerance probe marker",
    )
    checks.check(theorem.get("finite_scaled_tolerance_probe_ok_rows") == 4, "finite probe ok row count changed")
    checks.check(theorem.get("finite_scaled_tolerance_probe_total_rows") == 4, "finite probe total row count changed")
    checks.check(
        abs(float(theorem.get("finite_scaled_tolerance_probe_max_residual_over_h7", 0.0)) - 127.58372278641149)
        <= 1.0e-9,
        "finite probe max eta/h ratio changed",
    )
    checks.check(
        theorem.get("finite_tolerance_regime_sweep_recorded") is True,
        "proof contract lost finite tolerance-regime sweep marker",
    )
    checks.check(theorem.get("finite_tolerance_regime_sweep_policy_count") == 3, "finite tolerance-regime policy count changed")
    checks.check(theorem.get("finite_tolerance_regime_sweep_total_rows") == 12, "finite tolerance-regime row count changed")
    checks.check(theorem.get("finite_tolerance_regime_sweep_total_steps") == 90, "finite tolerance-regime step count changed")
    fixed_orders = theorem.get("finite_tolerance_regime_sweep_fixed_position_velocity_orders", [])
    h7_orders = theorem.get("finite_tolerance_regime_sweep_h7_position_velocity_orders", [])
    h8_orders = theorem.get("finite_tolerance_regime_sweep_h8_position_velocity_orders", [])
    checks.check(
        len(fixed_orders) == 2
        and abs(float(fixed_orders[0]) - 6.946347411176867) <= 1.0e-12
        and abs(float(fixed_orders[1]) - 6.608089993735075) <= 1.0e-12,
        "finite tolerance-regime fixed orders changed",
    )
    checks.check(
        len(h7_orders) == 2
        and abs(float(h7_orders[0]) - 6.946347411176867) <= 1.0e-12
        and abs(float(h7_orders[1]) - 6.608089993735075) <= 1.0e-12,
        "finite tolerance-regime h7 orders changed",
    )
    checks.check(
        len(h8_orders) == 2
        and abs(float(h8_orders[0]) - 6.946365976765468) <= 1.0e-12
        and abs(float(h8_orders[1]) - 6.608137477881583) <= 1.0e-12,
        "finite tolerance-regime h8 orders changed",
    )
    checks.check(
        theorem.get("scaled_tolerance_sweep_recorded") is False,
        "proof contract overclaims scaled tolerance sweep",
    )
    checks.check(
        theorem.get("eta_h_O_h7_solver_policy_evidence") is False,
        "proof contract overclaims eta_h solver-policy closure",
    )
    checks.check(theorem.get("proof_conditions_decomposed") is True, "proof contract lost decomposed-condition marker")
    checks.check(
        theorem.get("one_step_perturbation_shortcut_assumed") is False,
        "proof contract reintroduced circular one-step perturbation shortcut",
    )
    checks.check(theorem.get("dynamic_symbolic_oracle_complete") is False, "dynamic symbolic oracle incorrectly closed")
    checks.check(
        theorem.get("newton_euler_stage_defect_certificate_open") is False,
        "proof contract still marks Newton-Euler stage defect certificate open",
    )
    checks.check(
        theorem.get("newton_euler_stage_defect_certificate_closed_by_direct_substitution") is True,
        "proof contract lost direct-substitution stage-defect closure marker",
    )
    checks.check(
        theorem.get("newton_euler_stage_defect_certificate_satisfaction_mode")
        == "D5 same-branch residual-value certificate: 96-row O(h^7) non-dynamic certificate plus 36 dynamic zero rows at Z_G",
        "proof contract D5 satisfaction mode changed",
    )
    checks.check(
        theorem.get("stage_residual_O_h7_implementation_defect_proved") is True,
        "proof contract lost accepted O(h^7) implementation-defect closure",
    )
    checks.check(theorem.get("full_tfe_stage_replacement") is False, "full-TFE replacement overclaim")

    checks.check(order_contract.get("implemented_residual_defect_required") == "O(h^7)", "order gate residual requirement changed")
    checks.check(
        order_contract.get("newton_tolerance_policy") == theorem.get("newton_tolerance_policy"),
        "order gate Newton policy mismatch",
    )
    checks.check(order_contract.get("dynamic_symbolic_oracle_complete") is False, "order gate dynamic oracle overclaim")

    checks.check(dynamic_boundary.get("independent_symbolic_row_oracle_complete") is False, "dynamic oracle overclaim")
    checks.check(
        dynamic_boundary.get("partial_independent_formula_rows_checked") is True,
        "dynamic oracle lost partial formula-row marker",
    )
    checks.check(
        dynamic_boundary.get("full_independent_formula_rows_checked") is True,
        "dynamic oracle lost full formula-row marker",
    )
    checks.check(
        dynamic_oracle.get("partial_independent_formula_row_oracle", {}).get("row_count") == 96,
        "dynamic oracle partial formula-row count changed",
    )
    checks.check(
        dynamic_oracle.get("partial_independent_formula_row_oracle", {}).get("excluded_row_family")
        == "newton_euler_weak_balance",
        "dynamic oracle partial formula-row exclusion changed",
    )
    partial_defect = dynamic_oracle.get("partial_kinematic_stage_defect_certificate", {})
    checks.check(partial_defect.get("checked") is True, "dynamic oracle lost partial kinematic defect certificate")
    checks.check(partial_defect.get("row_count") == 96, "dynamic oracle partial kinematic defect row count changed")
    checks.check(
        partial_defect.get("excluded_row_family") == "newton_euler_weak_balance",
        "dynamic oracle partial kinematic defect excluded family changed",
    )
    checks.check(
        dynamic_oracle.get("full_independent_formula_row_oracle", {}).get("row_count") == 132,
        "dynamic oracle full formula-row count changed",
    )
    checks.check(
        dynamic_oracle.get("full_independent_formula_row_oracle", {}).get("added_row_family")
        == "newton_euler_weak_balance",
        "dynamic oracle full formula-row added-family marker changed",
    )
    checks.check(
        dynamic_oracle.get("formula_row_ad_jacobian_oracle", {}).get("checked") is True,
        "dynamic oracle lost formula-row AD Jacobian oracle",
    )
    checks.check(
        dynamic_oracle.get("formula_row_ad_jacobian_oracle", {}).get("multi_probe_checked") is True,
        "dynamic oracle lost formula-row AD Jacobian multi-probe marker",
    )
    checks.check(
        dynamic_oracle.get("formula_row_ad_jacobian_oracle", {}).get("probe_count") == 3,
        "dynamic oracle formula-row AD Jacobian probe count changed",
    )
    checks.check(
        dynamic_oracle.get("formula_row_ad_jacobian_oracle", {}).get("row_count") == 132,
        "dynamic oracle formula-row AD Jacobian row count changed",
    )
    checks.check(
        dynamic_oracle.get("formula_row_ad_jacobian_oracle", {}).get("column_count") == 132,
        "dynamic oracle formula-row AD Jacobian column count changed",
    )
    checks.check(
        dynamic_boundary.get("stage_residual_O_h7_implementation_defect_proved") is False,
        "dynamic oracle incorrectly proves O(h^7) implementation defect",
    )
    checks.check(dynamic_boundary.get("full_tfe_stage_replacement") is False, "dynamic oracle full-TFE overclaim")
    checks.check(dynamic_boundary.get("submission_ready") is False, "dynamic oracle submission overclaim")

    checks.check(numerical_scale_audit.get("schema") == "proof-numerical-scale-audit-v1", "numerical scale audit schema changed")
    checks.check(
        numerical_scale_audit.get("status") == "finite_run_global_scale_diagnostic_not_asymptotic_solver_proof",
        "numerical scale audit status changed",
    )
    checks.check(numerical_scale_audit.get("submission_ready") is False, "numerical scale audit overclaims submission")
    checks.check(
        numerical_scale_audit.get("execution_policy", {}).get("default_1e-4_required") is False,
        "numerical scale audit incorrectly requires default 1e-4",
    )
    checks.check(
        numerical_scale_audit.get("execution_policy", {}).get("heavy_numerical_run_invoked") is False,
        "numerical scale audit invoked heavy run",
    )
    checks.check(
        numerical_scale_boundary.get("finite_run_error_scale_supports_order_six") is True,
        "numerical scale audit lost order-six support marker",
    )
    checks.check(
        numerical_scale_boundary.get("endpoint_global_closure_scale_supports_local_h7_budget") is True,
        "numerical scale audit lost endpoint support marker",
    )
    checks.check(
        numerical_scale_boundary.get("eta_h_O_h7_solver_policy_evidence") is False,
        "numerical scale audit overclaims solver-policy proof",
    )
    checks.check(
        numerical_scale_boundary.get("stage_residual_O_h7_implementation_defect_proved_by_this_audit") is False,
        "numerical scale audit overclaims implementation defect proof by h-sweep evidence",
    )
    checks.check(
        numerical_scale_boundary.get("dynamic_symbolic_oracle_complete") is False,
        "numerical scale audit overclaims symbolic oracle",
    )
    checks.check(solver_scale_audit.get("schema") == "proof-solver-scale-audit-v1", "solver scale audit schema changed")
    checks.check(
        solver_scale_audit.get("status") == "summary_level_solver_residuals_recorded_not_scaled_eta_h_proof",
        "solver scale audit status changed",
    )
    checks.check(solver_scale_audit.get("submission_ready") is False, "solver scale audit overclaims submission")
    solver_boundary = solver_scale_audit.get("proof_boundary", {})
    checks.check(
        solver_boundary.get("summary_level_solver_residuals_recorded") is True,
        "solver scale audit lost residual-record marker",
    )
    checks.check(
        solver_boundary.get("finite_scaled_tolerance_probe_recorded") is True,
        "solver scale audit lost finite scaled-tolerance probe marker",
    )
    checks.check(
        solver_boundary.get("finite_tolerance_regime_sweep_recorded") is True,
        "solver scale audit lost finite tolerance-regime sweep marker",
    )
    checks.check(
        solver_boundary.get("scaled_tolerance_sweep_recorded") is False,
        "solver scale audit overclaims scaled tolerance sweep",
    )
    checks.check(
        solver_boundary.get("eta_h_O_h7_solver_policy_evidence") is False,
        "solver scale audit overclaims eta_h solver-policy closure",
    )
    checks.check(
        solver_boundary.get("fixed_tolerance_runs_are_asymptotic_proof") is False,
        "solver scale audit overclaims fixed-tolerance proof",
    )
    checks.check(
        solver_scale_audit.get("execution_policy", {}).get("default_1e-4_required") is False,
        "solver scale audit incorrectly requires default 1e-4",
    )
    checks.check(
        solver_scale_audit.get("execution_policy", {}).get("run_v047_invoked") is False,
        "solver scale audit invoked run_v047",
    )

    checks.check(
        kinematic_defect.get("schema") == "kinematic-row-defect-certificate-v1",
        "kinematic defect certificate schema changed",
    )
    checks.check(
        kinematic_defect.get("status") == "partial_96_row_proof_certificate_not_submission_ready",
        "kinematic defect certificate status changed",
    )
    checks.check(kinematic_defect.get("submission_ready") is False, "kinematic defect certificate overclaims submission")
    checks.check(
        kinematic_defect.get("proof_scope", {}).get("certified_row_count") == 96,
        "kinematic defect certified row count changed",
    )
    checks.check(
        kinematic_defect.get("proof_scope", {}).get("excluded_row_family") == "newton_euler_weak_balance",
        "kinematic defect excluded family changed",
    )
    checks.check(
        kinematic_defect.get("certificate", {}).get("partial_stage_defect_certificate") is True,
        "kinematic defect partial certificate marker missing",
    )
    checks.check(
        kinematic_defect.get("certificate", {}).get("stage_residual_O_h7_implementation_defect_proved") is False,
        "kinematic defect certificate overclaims full implementation defect proof",
    )
    checks.check(
        kinematic_defect.get("execution_policy", {}).get("default_1e-4_required") is False,
        "kinematic defect certificate incorrectly requires default 1e-4",
    )
    checks.check(
        newton_euler_obligation.get("schema") == "newton-euler-defect-obligation-gate-v1",
        "Newton-Euler obligation gate schema changed",
    )
    checks.check(
        newton_euler_obligation.get("status")
        == "d5_symbolic_primitive_route_open_active_direct_pc2_closed_not_submission_ready",
        "Newton-Euler obligation gate status changed",
    )
    checks.check(
        newton_euler_obligation.get("proof_scope", {}).get("row_family") == "newton_euler_weak_balance",
        "Newton-Euler obligation row family changed",
    )
    checks.check(
        newton_euler_obligation.get("proof_scope", {}).get("dynamic_row_count") == 36,
        "Newton-Euler obligation row count changed",
    )
    checks.check(
        newton_euler_obligation.get("closure_state", {}).get("open_obligation_count") == 1,
        "Newton-Euler obligation open count changed",
    )
    checks.check(
        newton_euler_obligation.get("closure_state", {}).get("closed_obligation_count") == 5,
        "Newton-Euler obligation closed count changed",
    )
    checks.check(
        newton_euler_obligation.get("closure_state", {}).get("closed_obligation_ids")
        == [
            "translational_balance_identity",
            "rotational_balance_identity",
            "multiplier_wrench_consistency",
            "smooth_force_lift_consistency",
            "symbolic_runtime_row_equivalence",
        ],
        "Newton-Euler obligation closed ids changed",
    )
    checks.check(
        newton_euler_obligation.get("closure_state", {}).get("stage_residual_O_h7_implementation_defect_proved") is False,
        "Newton-Euler symbolic/primitive route overclaims O(h^7)",
    )
    checks.check(
        newton_euler_obligation.get("closure_state", {}).get("active_direct_pc2_closed") is True,
        "Newton-Euler obligation gate lost active direct PC2 closure marker",
    )
    checks.check(
        newton_euler_obligation.get("closure_state", {}).get("dynamic_symbolic_oracle_complete") is False,
        "Newton-Euler obligation gate overclaims symbolic oracle",
    )
    checks.check(
        newton_euler_obligation.get("execution_policy", {}).get("default_1e-4_required") is False,
        "Newton-Euler obligation gate incorrectly requires default 1e-4",
    )

    for key in [
        "schema",
        "obligation_count",
        "blocking_obligation_count",
        "accepted_residual_to_error_theorem",
        "accepted_dynamic_order_count",
    ]:
        checks.check(r2e.get(key) == r2e_contract.get(key), f"residual-to-error field mismatch: {key}")
    checks.check(r2e_contract.get("obligation_count") == 7, "residual-to-error obligation count changed")
    checks.check(r2e_contract.get("blocking_obligation_count") == 7, "residual-to-error blocking count changed")
    checks.check(
        r2e_contract.get("accepted_residual_to_error_theorem") is False,
        "residual-to-error theorem incorrectly accepted",
    )
    checks.check(r2e_contract.get("accepted_dynamic_order_count") == 0, "residual route accepted dynamic order")

    checks.check(b1.get("status") == "closed", "B1 should be closed by AD-expanded symbolic certificate")
    checks.check(
        b1.get("closure_basis") == "residual_identity_chain_rule_ad_expanded_symbolic_oracle",
        "B1 closure basis changed",
    )
    checks.check(
        b1.get("b1_ad_expanded_symbolic_oracle_closure") is True,
        "B1 AD-expanded symbolic closure marker missing",
    )
    checks.check(
        b1.get("b1_ad_expanded_symbolic_oracle_closed_cells") == 4752,
        "B1 AD-expanded derivative-cell count changed",
    )
    checks.check(b1.get("partial_formula_row_count") == 96, "B1 partial formula-row count changed")
    checks.check(b3.get("status") == "closed", "B3 should be closed by direct residual-bridge/Kantorovich route")
    checks.check(b3.get("required_to_close") == [], "B3 should have no remaining close requirements")
    checks.check(
        b3.get("diagnostic_primitive_taylor_route_open_items")
        == [
            "prove_five_open_primitive_taylor_lift_obligations",
            "certify_all_162_D5_Taylor_subterms",
            "close_primitive_taylor_PC2_route",
        ],
        "B3 diagnostic primitive route open items changed",
    )
    checks.check(
        b3.get("b3_direct_proof_review_passed") is True,
        "B3 direct-proof review did not pass",
    )
    checks.check(
        b3.get("b3_can_close_from_proof_review") is True,
        "B3 direct-proof review closure marker missing",
    )
    checks.check(
        b3.get("b3_direct_proof_review_counts_as_residual_bridge_closure") is True,
        "B3 direct-proof review should count for direct residual-bridge route",
    )
    checks.check(
        b3.get("direct_residual_bridge_submission_standard_satisfied") is True,
        "B3 direct residual-bridge proof contract not satisfied",
    )
    checks.check(b3.get("primitive_taylor_actual_bounds_proved") == 0, "B3 primitive/Taylor actual bounds changed")
    checks.check(b3.get("primitive_taylor_open_bound_terms") == 162, "B3 primitive/Taylor open term count changed")
    checks.check(b3.get("primitive_taylor_open_primitive_count") == 5, "B3 primitive/Taylor open primitive count changed")
    checks.check(
        "B3_DIRECT_PROOF_REVIEW_AUDIT.md" in b3.get("partial_progress_evidence", []),
        "B3 direct-proof review markdown evidence missing",
    )
    checks.check(
        "validate_b3_direct_proof_review_audit.py" in b3.get("partial_progress_evidence", []),
        "B3 direct-proof review validator evidence missing",
    )
    checks.check(b3.get("proof_close_requirements_satisfied") == 4, "B3 proof close requirement count changed")
    checks.check(b3.get("proof_close_requirements_unsatisfied") == 0, "B3 proof close requirement gap changed")
    checks.check(
        b3.get("pc2_satisfaction_mode")
        == "D5 same-branch residual-value certificate: 96-row O(h^7) non-dynamic certificate plus 36 dynamic zero rows at Z_G",
        "B3 PC2 satisfaction mode changed",
    )

    require_tokens(
        checks,
        manuscript,
        [
            "Conditional sixth-order theorem",
            "conditional local-defect-to-global-error argument",
            "not a derivation of the complete source-paper temporal finite-element weak form",
            "accepted residual tolerance must scale no larger than $O(h^7)$",
            "implementation part of the theorem is not a compact-tube regularity assumption",
    "stage-residual inputs from theorem-domain interfaces",
    "96-row non-dynamic certificate together with the D5 direct-substitution certificate",
    "lifted Gauss stage has a defect bounded by $C_R h^7$",
    "formula residual at the lifted Gauss stage",
    "row ordering, and row scaling have been fixed",
    "discharged formula-residual input",
    "not an empirical residual fit",
    "stage-residual hypothesis of",
    "certified 132-row residual",
            "one-step accepted residual defect statement only",
            "fixed tolerances used in the numerical section are reported separately as finite-run solver data",
            "not as an asymptotic solver-error proof",
            "local accepted root",
            "not a global uniqueness claim for remote nonlinear roots",
            "not a certificate of global nonlinear solver convergence",
            "triangle inequality over Gauss truncation, stage-root perturbation, endpoint closure, and inexact Newton",
            "solver-scale check of the existing summary residuals",
            "not a scaled",
            "tolerance proof",
            "\\label{lem:inexact-newton}",
            "\\label{thm:g6fullva-order}",
            "\\(\\eta_h\\le c_\\eta h^7\\)",
            "proof certificates supply the accepted direct-route residual/Jacobian binding used by the bridge",
            "AD-expanded implementation-path derivative-cell certificate records the derivative identities used by that binding",
            "active proof route is the direct-substitution certificate",
            "D1/D2 balance-identity certificate",
            "closed D1/D2 balance identities",
            "six row-expanded lower-pair multiplier identities",
            "source-identity and row-layout records",
            "not a single order theorem",
            "four-link/slider-crank dynamic convergence order",
            "complete source-paper residual reproduction",
        ],
        "main_cmame.tex",
    )
    require_tokens(checks, manuscript, PROOF_CONDITIONAL_BOUNDARY_TOKENS, "main_cmame.tex proof boundary")
    require_tokens(checks, flat_manuscript, PROOF_CONDITIONAL_BOUNDARY_TOKENS, "flat TeX proof boundary")
    require_tokens(checks, pdf_text, PROOF_CONDITIONAL_BOUNDARY_TOKENS, "main PDF text proof boundary")
    require_tokens(checks, flat_pdf_text, PROOF_CONDITIONAL_BOUNDARY_TOKENS, "flat PDF text proof boundary")
    require_tokens(
        checks,
        gate_md,
        [
            "CMAME Proof Contract Gate",
            "CONDITIONAL CONTRACT RECORDED - GLOBAL SUBMISSION GATES OPEN",
            "submission_ready=false` is a theorem-level/global proof-contract marker",
            "Submission-ready scope: `theorem_level_global_proof_contract_not_narrowed_claim_package_decision`.",
            "Proof contract gate scope: `conditional_theorem_contract_with_eta_h_and_residual_to_error_boundaries`.",
            "B4/B6/B7 narrowed-claim statuses: `closed/closed/closed`.",
            "Remaining global submission boundaries: `full_source_policy_package_ready,theorem_level_eta_h_solver_policy_evidence,closed_residual_to_error_theorem_for_mechanism_rows`.",
            "Manuscript Theorem Traceability",
            "Theorem labels/boundary/mapped: `True/True/True`.",
            "Proof dependency/traceability/dynamic matrix: `True/True/True`.",
            "Primitive-route and residual nonpromotion boundaries: `True/True`.",
            "Eta condition/closure and fixed-tolerance proof: `True/False/False`.",
            "Residual/source-policy-full-TFE not promoted: `True/True`; no-state-change `True`.",
            "Manuscript anchor map: `True`; label anchors `24`; theorem-interface/P7-output-boundary anchors `7`; IDs `P1,P2,P3,P4,P5,P6,P7`; proof-claim map match `True`.",
            "Reader-facing theorem-interface split: theorem interfaces `P1--P6`; P7 is an output nonclaim/residual-to-error boundary anchor, not a theorem premise.",
            "conditional_consistency_transfer",
            "compact-tube Gauss-predictor branch",
            "finite rank probes or pointwise solved-stage",
            "not a compact-tube inverse proof",
            "accepted one-step stability scale",
            "ordinary compact-tube Lipschitz continuity alone",
            "tube-retention bootstrap",
            "not an invariant-region proof",
            "endpoint closure perturbation `O(h^7)` under a local",
            "closed endpoint anchor",
            "endpoint-ball margin",
            "compact-tube splitting bound",
            "raw endpoint closure defect constant",
            "`C_E=4 M_E^ri C_{E,raw}`",
            "`||E(z_u)|| <= C_{E,raw} h^7`",
            "`||Delta z_E|| <= C_E h^7`",
            "pointwise right-invertibility at one endpoint alone",
            "strong local residual inverse",
            "averaged-Jacobian perturbation bound",
            "pointwise Jacobian invertibility alone",
            "eta_h^tube <= c_eta h^7",
            "Gauss truncation term is recorded as an explicit uniform bound",
            "`||Psi_h^G(y)-phi_h(y)|| <= C_G h^7`",
            "uniform on the compact",
            "stage-residual perturbation step is also recorded as an explicit",
            "`||Z_A-Z_G|| <= C_Z h^7`",
            "`C_Z=2 M C_R`",
            "`C_A=M_E C_Z`",
            "local accepted root is obtained by the",
            "not assumed as a separate isolated-root premise",
            "uniform-constant contract",
            "uniform in `y` on the compact proof tube",
            "uniform in the accepted step index `n<N`",
            "reported-grid maximum",
            "`||P_h(Ztilde_A)-P_h(Z_A)|| <= C_N eta_h`",
            "`P_h=C_h o E_h`",
            "endpoint-closure Lipschitz factor",
            "`C_N=2 M_A M_N`",
            "`C_N c_eta h^7`",
            "explicit local-defect constant",
            "passes that single uniform constant to the",
            "local-defect constant sum `C_loc=C_G+C_A+C_E+C_N c_eta`",
            "`C_red=C_loc Gamma_s(T)`",
            "`C_qv=C_{\\mathcal R} C_red`",
            "`C_{\\mathcal R}` is the chart-reporting",
            "same-initial-state reported-grid estimate on the accepted",
            "reported `(q,v)` error bound is a grid maximum",
            "reported time grid is defined by `t_n=n h`",
            "exact final-time divisibility is not required",
            "same reported time grid",
            "dynamic_symbolic_oracle_complete=false",
            "global/full-source-policy package boundaries",
            "B4/B6/B7 narrowed-claim closure is recorded separately",
            "full independent formula-row oracle covers 132 runtime formula rows",
            "KINEMATIC_ROW_DEFECT_CERTIFICATE.md/json",
            "96 non-dynamic rows",
            "provenance record for the primitive/Taylor route",
            "NEWTON_EULER_DEFECT_OBLIGATION_GATE.md/json",
            "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.md/json",
            "36 row-level symbolic",
            "D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE.md/json",
            "stage-residual `O(h^7)` implementation-defect certificate",
            "active_direct_newton_euler_open_obligation_count=0",
            "newton_euler_symbolic_primitive_open_obligation_count=1",
            "newton_euler_symbolic_primitive_open_obligation_scope=symbolic_primitive_certificate_route_not_active_direct_pc2",
            "active direct D5 route closed; symbolic/primitive D5 route remains open",
            "multi-probe formula-row AD Jacobian oracle matches `R_JAC` on three deterministic probes",
            "PROOF_NUMERICAL_SCALE_AUDIT.md/json",
            "finite-run global h-sweep",
            "PROOF_SOLVER_SCALE_AUDIT.md/json",
            "summary-level solver residuals",
            "3584.657362964853",
            "PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.md/json/csv",
            "fixed `1e-10`, `c h^7`, and `c h^8`",
            "6.946347411176867/6.608089993735075",
            "6.946365976765468/6.608137477881583",
            "eta_h_O_h7_solver_policy_evidence=false",
            "scaled-tolerance policy",
            "newton_euler_weak_balance",
            "stage_residual_O_h7_implementation_defect_proved=true",
            "one_step_perturbation_shortcut_assumed=false",
            "no longer uses a circular one-step perturbation shortcut",
            "fixed_tolerance_runs_are_asymptotic_proof=false",
            "accepted_residual_to_error_theorem=false",
            "accepted_dynamic_order_count=0",
            "seven blocking obligations",
            "This B3 proof closure is independent of the separate narrowed-claim B4/B6/B7 closures",
            "validate_cmame_proof_contract_gate.py",
        ],
        "CMAME_PROOF_CONTRACT_GATE.md",
    )
    require_tokens(
        checks,
        proof_matrix,
        [
            "Solver-error scaling is mathematically stated",
            "recorded fixed-tolerance runs are finite-run data",
            "partial independent formula-row oracle",
            "96 non-dynamic rows",
            "full independent formula-row oracle",
            "132 runtime formula rows",
            "multi-probe formula-row AD Jacobian oracle",
            "KINEMATIC_ROW_DEFECT_CERTIFICATE.md/json",
            "96 non-dynamic",
            "NEWTON_EULER_DEFECT_OBLIGATION_GATE.md/json",
            "one open Newton--Euler symbolic proof obligation and five closed D1/D2/D3/D4/D6 sub-obligations",
            "PROOF_NUMERICAL_SCALE_AUDIT.md/json",
            "finite-run scale diagnostic",
            "PROOF_SOLVER_SCALE_AUDIT.md/json",
            "smooth reference `max_linear_residual_norm=2.800513564816292e-13`",
            "finite tolerance-regime sweep",
            "theorem_level_scaled_tolerance_sweep_recorded=false",
            "eta_h_O_h7_solver_policy_evidence=false",
            "newton_euler_weak_balance",
            "independent symbolic oracle remains open",
            "one-step `O(h^7)` perturbation is no longer assumed as a shortcut",
            "noncircular",
            "conditional order-comparison proposition",
            "accepted_residual_to_error_theorem=false",
        ],
        "PROOF_EVIDENCE_MATRIX.md",
    )
    require_tokens(
        checks,
        numerical_scale_audit_md,
        [
            "Proof Numerical Scale Audit",
            "finite-run scale diagnostic, not an asymptotic solver proof",
            "default_1e-4_required=false",
            "7.160828003417387",
            "7.066182539651858",
            "5.985100758394371",
            "6.072290794930567",
            "eta_h_O_h7_solver_policy_evidence=false",
            "stage_residual_O_h7_implementation_defect_proved_by_this_audit=false",
        ],
        "PROOF_NUMERICAL_SCALE_AUDIT.md",
    )
    require_tokens(
        checks,
        solver_scale_audit_md,
        [
            "Proof Solver Scale Audit",
            "SUMMARY-LEVEL SOLVER RESIDUALS RECORDED - NOT A SCALED ETA_H PROOF",
            "default `1e-4` campaign",
            "2.800513564816292e-13",
            "3584.657362964853",
            "finite scaled-tolerance probe",
            "127.58372278641149",
            "finite tolerance-regime sweep",
            "6.946347411176867/6.608089993735075",
            "theorem_level_scaled_tolerance_sweep_recorded=false",
            "eta_h_O_h7_solver_policy_evidence=false",
            "run_v047_invoked=false",
        ],
        "PROOF_SOLVER_SCALE_AUDIT.md",
    )
    require_tokens(
        checks,
        kinematic_defect_md,
        [
            "Kinematic Row Defect Certificate",
            "PARTIAL PROOF CERTIFICATE - 96 ROWS - NOT SUBMISSION READY",
            "Total certified proof-scope rows: `96`",
            "newton_euler_weak_balance",
            "stage_residual_O_h7_implementation_defect_proved",
            "submission_ready=False",
        ],
        "KINEMATIC_ROW_DEFECT_CERTIFICATE.md",
    )
    require_tokens(
        checks,
        newton_euler_obligation_md,
        [
            "Newton-Euler Defect Obligation Gate",
            "D5 SYMBOLIC/PRIMITIVE ROUTE OPEN; ACTIVE DIRECT PC2 CLOSED - NOT SUBMISSION READY",
            "`newton_euler_weak_balance`",
            "Symbolic/primitive-route open obligation count: `1`",
            "Active direct PC2 closed: `True`",
            "Closed obligation count: `5`",
            "Closed obligation ids: `translational_balance_identity, rotational_balance_identity, multiplier_wrench_consistency, smooth_force_lift_consistency, symbolic_runtime_row_equivalence`",
            "translational_balance_identity",
            "rotational_balance_identity",
            "multiplier_wrench_consistency",
            "smooth_force_lift_consistency",
            "gauss_stage_dynamic_defect_rate",
            "symbolic_runtime_row_equivalence",
            "symbolic_primitive_stage_residual_O_h7_certificate_complete",
            "dynamic_symbolic_oracle_complete",
            "default_1e-4_required=false",
        ],
        "NEWTON_EULER_DEFECT_OBLIGATION_GATE.md",
    )

    checks.check("CMAME_PROOF_CONTRACT_GATE.md" in manifest.get("evidence_anchors", []), "manifest missing proof gate anchor")
    checks.check("CMAME_PROOF_CONTRACT_GATE.json" in manifest.get("evidence_anchors", []), "manifest missing proof gate JSON anchor")
    checks.check(
        "PROOF_NUMERICAL_SCALE_AUDIT.md" in manifest.get("evidence_anchors", []),
        "manifest missing proof numerical scale audit anchor",
    )
    checks.check(
        "PROOF_NUMERICAL_SCALE_AUDIT.json" in manifest.get("evidence_anchors", []),
        "manifest missing proof numerical scale audit JSON anchor",
    )
    checks.check(
        "PROOF_SOLVER_SCALE_AUDIT.md" in manifest.get("evidence_anchors", []),
        "manifest missing proof solver scale audit anchor",
    )
    checks.check(
        "PROOF_SOLVER_SCALE_AUDIT.json" in manifest.get("evidence_anchors", []),
        "manifest missing proof solver scale audit JSON anchor",
    )
    checks.check(
        "PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.md" in manifest.get("evidence_anchors", []),
        "manifest missing proof solver tolerance-regime sweep anchor",
    )
    checks.check(
        "PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.json" in manifest.get("evidence_anchors", []),
        "manifest missing proof solver tolerance-regime sweep JSON anchor",
    )
    checks.check(
        "KINEMATIC_ROW_DEFECT_CERTIFICATE.md" in manifest.get("evidence_anchors", []),
        "manifest missing kinematic row defect certificate anchor",
    )
    checks.check(
        "KINEMATIC_ROW_DEFECT_CERTIFICATE.json" in manifest.get("evidence_anchors", []),
        "manifest missing kinematic row defect certificate JSON anchor",
    )
    checks.check(
        "NEWTON_EULER_DEFECT_OBLIGATION_GATE.md" in manifest.get("evidence_anchors", []),
        "manifest missing Newton-Euler obligation gate",
    )
    checks.check(
        "NEWTON_EULER_DEFECT_OBLIGATION_GATE.json" in manifest.get("evidence_anchors", []),
        "manifest missing Newton-Euler obligation gate JSON",
    )
    checks.check(
        "NEWTON_EULER_BALANCE_IDENTITY_AUDIT.md" in manifest.get("evidence_anchors", []),
        "manifest missing Newton-Euler balance identity audit",
    )
    checks.check(
        "NEWTON_EULER_BALANCE_IDENTITY_AUDIT.json" in manifest.get("evidence_anchors", []),
        "manifest missing Newton-Euler balance identity audit JSON",
    )
    checks.check("validate_cmame_proof_contract_gate.py" in manifest.get("validators", []), "manifest missing proof gate validator")
    checks.check(
        "validate_proof_numerical_scale_audit.py" in manifest.get("validators", []),
        "manifest missing proof numerical scale audit validator",
    )
    checks.check(
        "validate_proof_solver_scale_audit.py" in manifest.get("validators", []),
        "manifest missing proof solver scale audit validator",
    )
    checks.check(
        "validate_kinematic_row_defect_certificate.py" in manifest.get("validators", []),
        "manifest missing kinematic row defect certificate validator",
    )
    checks.check(
        "validate_newton_euler_defect_obligation_gate.py" in manifest.get("validators", []),
        "manifest missing Newton-Euler obligation gate validator",
    )
    checks.check(
        "validate_newton_euler_symbolic_target_audit.py" in manifest.get("validators", []),
        "manifest missing Newton-Euler symbolic target audit validator",
    )
    checks.check(
        "validate_newton_euler_balance_identity_audit.py" in manifest.get("validators", []),
        "manifest missing Newton-Euler balance identity validator",
    )

    forbidden = set(gate.get("forbidden_claims", []))
    for token in [
        "proof_unconditional",
        "fixed_tolerance_runs_are_asymptotic_proof",
        "dynamic_symbolic_oracle_complete_true",
        "accepted_residual_to_error_theorem_true",
        "four_link_slider_crank_dynamic_order_accepted_by_residual",
        "full_tfe_stage_replacement_true",
        "submission_ready_true",
    ]:
        checks.check(token in forbidden, f"forbidden claim missing: {token}")

    if checks.errors:
        print("cmame_proof_contract_gate=FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("cmame_proof_contract_gate=PASS")
    print("submission_ready_scope=theorem_level_global_proof_contract_not_narrowed_claim_package_decision")
    print("proof_contract_gate_scope=conditional_theorem_contract_with_eta_h_and_residual_to_error_boundaries")
    print("proof_mode=conditional_consistency_transfer")
    print("accepted_method=Gauss6/FullVA")
    print("accepted_method_order=6")
    print("accepted_one_step_stability_required=True")
    print("accepted_endpoint_closure_local_right_inverse_required=True")
    print("endpoint_closure_perturbation_constant_formula=C_E=4*M_E^ri*C_{E,raw}")
    print("local_global_reduced_grid_constant_formula=C_red=C_loc*Gamma_s(T)")
    print("qv_reporting_constant_formula=C_qv=C_{\\mathcal R}*C_red")
    print("accepted_newton_residual_strong_local_inverse_required=True")
    print("newton_eta_h_scaled_endpoint_bound_formula=C_N*c_eta*h^7")
    print("newton_tolerance_policy=eta_h_tube<=c_eta*h^7")
    print("partial_formula_row_oracle_96_rows_checked=True")
    print("full_formula_row_oracle_132_rows_checked=True")
    print("partial_kinematic_stage_defect_certificate_checked=True")
    print("partial_kinematic_stage_defect_rows_checked=96")
    print("newton_euler_defect_obligation_gate_checked=True")
    print("active_direct_newton_euler_open_obligation_count=0")
    print("newton_euler_symbolic_primitive_open_obligation_count=1")
    print("newton_euler_symbolic_primitive_open_obligation_scope=symbolic_primitive_certificate_route_not_active_direct_pc2")
    print("newton_euler_defect_closed_obligation_count=5")
    print("newton_euler_symbolic_defect_certificate_complete=False")
    print("formula_row_ad_jacobian_oracle_checked=True")
    print("formula_row_ad_jacobian_probe_count=3")
    print("newton_euler_formula_oracle_complete=True")
    print("finite_run_numerical_scale_audit_checked=True")
    print("finite_run_error_scale_supports_order_six=True")
    print("solver_scale_audit_checked=True")
    print("summary_level_solver_residuals_recorded=True")
    print("scaled_tolerance_sweep_recorded=False")
    print("eta_h_O_h7_solver_policy_evidence=False")
    print("proof_conditions_decomposed=True")
    print("one_step_perturbation_shortcut_assumed=False")
    print("dynamic_symbolic_oracle_complete=False")
    print("stage_residual_O_h7_implementation_defect_proved=True")
    print("fixed_tolerance_runs_are_asymptotic_proof=False")
    print("accepted_residual_to_error_theorem=False")
    print("accepted_dynamic_order_by_residual_to_error=0")
    print("submission_ready=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
