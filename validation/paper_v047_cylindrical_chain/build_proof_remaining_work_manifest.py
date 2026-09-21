#!/usr/bin/env python3
"""Build the B1/B3 proof remaining-work manifest.

This is a read-only closeout map over existing proof artifacts. It turns the
proof-blocker lanes into explicit status records without promoting the
remaining submission gates.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "PROOF_REMAINING_WORK_MANIFEST.json"
OUT_MD = PAPER / "PROOF_REMAINING_WORK_MANIFEST.md"


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def blocker_by_id(blocker_gate: dict[str, Any], blocker_id: str) -> dict[str, Any]:
    for blocker in blocker_gate.get("blockers", []):
        if isinstance(blocker, dict) and blocker.get("id") == blocker_id:
            return blocker
    return {}


def blocker_statuses(blocker_gate: dict[str, Any], blocker_ids: list[str]) -> dict[str, Any]:
    return {blocker_id: blocker_by_id(blocker_gate, blocker_id).get("status") for blocker_id in blocker_ids}


def main() -> None:
    proof_closure = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
    proof_traceability = read_json(PAPER / "PROOF_CLAIM_TRACEABILITY_AUDIT.json")
    newton_targets = read_json(PAPER / "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.json")
    defect_certificate_path = PAPER / "NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.json"
    defect_certificate = read_json(defect_certificate_path) if defect_certificate_path.exists() else {}
    ad_expanded_oracle = read_json(PAPER / "NEWTON_EULER_AD_EXPANDED_ROW_ORACLE_AUDIT.json")
    b1_symbolic_row_oracle = read_json(PAPER / "B1_SYMBOLIC_ROW_ORACLE_CLOSURE_CERTIFICATE.json")
    b1_ad_expanded_symbolic_oracle = read_json(
        PAPER / "B1_AD_EXPANDED_SYMBOLIC_ORACLE_CLOSURE_CERTIFICATE.json"
    )
    solver_scale = read_json(PAPER / "PROOF_SOLVER_SCALE_AUDIT.json")
    blocker_gate = read_json(PAPER / "CMAME_BLOCKER_CLOSURE_GATE.json")

    close_requirements = proof_closure.get("close_requirements", [])
    satisfied = [row for row in close_requirements if row.get("satisfied") is True]
    unsatisfied = [row for row in close_requirements if row.get("satisfied") is not True]
    target_coverage = newton_targets.get("obligation_coverage_matrix", {})
    solver_boundary = solver_scale.get("proof_boundary", {})
    b1 = blocker_by_id(blocker_gate, "B1")
    b3 = blocker_by_id(blocker_gate, "B3")
    global_submission_boundaries_retained = [
        "full_source_policy_package_ready",
        "theorem_level_eta_h_solver_policy_evidence",
        "closed_residual_to_error_theorem_for_mechanism_rows",
    ]

    work_lanes = [
        {
            "lane_id": "PC1_symbolic_row_oracle",
            "blockers": ["B1", "B3"],
            "status": "closed_balance_identity_source_oracle",
            "rows": newton_targets.get("row_count"),
            "row_obligation_links": target_coverage.get("row_obligation_link_count"),
            "required_to_close": [
                "no remaining PC1-specific work; keep the D1/D2 balance-identity audit and validators in sync",
            ],
            "current_evidence": [
                "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.json gives the 36 row targets",
                "NEWTON_EULER_BALANCE_IDENTITY_AUDIT.json closes D1/D2 source-level balance identities for all 36 dynamic rows",
                "NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.json verifies the implemented source-expression structure for all 36 dynamic rows",
                "NEWTON_EULER_ROW_ORDERING_SCALING_AD_AUDIT.json closes D6 row ordering, residual scaling, and AD binding",
                "obligation coverage matrix is complete; D5 remains the only Newton-Euler open proof obligation",
            ],
            "closes_requirement": "PC1",
            "closes_now": True,
            "satisfaction_mode": "D1/D2 balance identities closed by NEWTON_EULER_BALANCE_IDENTITY_AUDIT",
        },
        {
            "lane_id": "PC2_direct_dynamic_O_h7_defect_certificate",
            "blockers": ["B3"],
            "status": "closed_by_direct_substitution_route",
            "rows": proof_closure.get("evidence_summary", {}).get("open_dynamic_rows"),
            "required_to_close": [
                "keep D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE.json and PROOF_CLOSURE_MANIFEST.json synchronized",
                "do not reuse this direct-route closure as an AD-expanded symbolic oracle closure",
            ],
            "current_evidence": [
                "96 non-dynamic rows are certified",
                "36 Newton-Euler rows are direct-route row-defect closed by the D5 direct-substitution certificate",
                "PROOF_CLOSURE_MANIFEST records all close requirements satisfied",
            ],
            "closes_requirement": "PC2",
            "closes_now": True,
            "satisfaction_mode": "D5 direct-substitution route closes the O(h^7) dynamic-defect proof, but not B1 symbolic oracle closure",
        },
        {
            "lane_id": "B1_AD_expanded_symbolic_oracle",
            "blockers": ["B1"],
            "status": "closed_by_residual_identity_chain_rule_certificate",
            "rows": b1_ad_expanded_symbolic_oracle.get("row_count"),
            "required_to_close": [
                "no remaining B1 AD-expanded symbolic-oracle work; keep the chain-rule certificate and validators in sync",
                "keep NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.json from overclaiming O(h^7) proof through this lane",
            ],
            "current_evidence": [
                "B1_SYMBOLIC_ROW_ORACLE_CLOSURE_CERTIFICATE.json closes the independent residual-row symbolic oracle item for 36/36 rows",
                "B1_AD_EXPANDED_SYMBOLIC_ORACLE_CLOSURE_CERTIFICATE.json differentiates the closed residual identities columnwise and closes 4752/4752 AD-expanded derivative cells",
                "NEWTON_EULER_AD_EXPANDED_ROW_ORACLE_AUDIT.json covers 36 rows with 132 AD columns per row",
                "the runtime-binding audit records ad_expanded_symbolic_oracle_closure=false because it is not the symbolic closure certificate",
                "NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.json records pc1_symbolic_row_oracle_closed=true only at the source/balance-identity layer",
            ],
            "closes_requirement": "B1_symbolic_oracle",
            "closes_now": True,
            "satisfaction_mode": "closed residual row identities differentiated columnwise on the smooth proof tube",
        },
        {
            "lane_id": "PC3_solver_eta_policy",
            "blockers": ["B3"],
            "status": "condition_retained_not_empirical_closure",
            "rows": solver_scale.get("finite_scaled_tolerance_trajectory_probe", {}).get("row_count"),
            "required_to_close": [
                "keep eta_h <= c_eta h^7 as an explicit theorem condition, or",
                "run a theorem-level scaled trajectory sweep with accepted reporting scope",
            ],
            "current_evidence": [
                "finite one-step scaled-tolerance probe has 4/4 ok rows",
                "finite short-trajectory scaled-tolerance probe has 4/4 ok rows and 30 steps",
                "finite tolerance-regime sweep records 8 h-scaled rows and 60 h-scaled trajectory steps",
                "theorem_level_scaled_tolerance_sweep_recorded remains false",
            ],
            "closes_requirement": "PC3",
            "closes_now": True,
            "satisfaction_mode": "explicit_theorem_condition_retained_not_empirical_solver_evidence",
        },
        {
            "lane_id": "PC4_residual_to_error_boundary",
            "blockers": ["B3", "B4"],
            "status": "nonpromotion_boundary_retained",
            "rows": proof_closure.get("evidence_summary", {}).get("residual_to_error_blocking_obligations"),
            "required_to_close": [
                "do not promote four-link/slider-crank residual rows to dynamic-order claims",
                "only close this route with a residual-to-error theorem or keep coverage-only labeling",
            ],
            "current_evidence": [
                "four_link and slider_crank remain coverage-only examples for residual-to-error route",
            ],
            "closes_requirement": "PC4",
            "closes_now": "nonpromotion_only",
            "nonpromotion_boundary_retained": True,
            "residual_to_error_closed": False,
            "residual_to_error_route_promoted": False,
            "satisfaction_mode": "nonpromotion_boundary_retained_residual_to_error_theorem_open",
        },
    ]

    output = {
        "schema": "proof-remaining-work-manifest-v1",
        "status": "proof_b1_b3_closed_submission_gates_remaining",
        "submission_ready": False,
        "submission_ready_scope": "proof_remaining_work_global_boundary_not_narrowed_claim_package_decision",
        "readiness_boundary": {
            "proof_remaining_work_manifest_scope": "B1_B3_closed_remaining_global_submission_gates",
            "narrowed_claim_b4_b6_b7_statuses": blocker_statuses(blocker_gate, ["B4", "B6", "B7"]),
            "global_submission_boundaries_retained": global_submission_boundaries_retained,
        },
        "remaining_gate_scope": {
            "narrowed_claim_b4_b6_b7_statuses": blocker_statuses(blocker_gate, ["B4", "B6", "B7"]),
            "b4_b6_b7_closed_elsewhere_under_narrowed_claim": all(
                blocker_by_id(blocker_gate, blocker_id).get("status") == "closed"
                for blocker_id in ["B4", "B6", "B7"]
            ),
            "eta_h_O_h7_solver_policy_evidence": proof_closure.get("closure_state", {}).get(
                "eta_h_O_h7_solver_policy_evidence"
            ),
            "eta_h_theorem_condition_retained": True,
            "residual_to_error_blocking_obligations": proof_closure.get("evidence_summary", {}).get(
                "residual_to_error_blocking_obligations"
            ),
            "residual_to_error_route_promoted": False,
            "active_b1_b3_proof_blockers_remaining": False,
            "global_submission_boundaries_retained": global_submission_boundaries_retained,
        },
        "proof_gap_closed": proof_closure.get("closure_state", {}).get("proof_gap_closed"),
        "proof_gap_closed_scope": proof_closure.get("closure_state", {}).get("proof_gap_closed_scope"),
        "proof_gap_closed_reading_rule": (
            "The schema-only compatibility boolean proof_gap_closed is a schema-compatible "
            "shorthand for direct_pc2_proof_gap_closed under the active direct PC2 residual-bridge/"
            "Kantorovich route. It does not close the primitive/Taylor route, P6 "
            "solver-policy evidence, P7 residual-to-error promotion, source-policy "
            "readiness, or full-TFE replacement."
        ),
        "schema_compatibility": {
            "legacy_key": "proof_gap_closed",
            "legacy_key_retained_for_schema_compatibility": True,
            "preferred_key": "direct_pc2_proof_gap_closed",
        },
        "direct_pc2_proof_gap_closed": proof_closure.get("closure_state", {}).get(
            "direct_pc2_proof_gap_closed"
        ),
        "stage_residual_O_h7_implementation_defect_proved": proof_closure.get("closure_state", {}).get(
            "stage_residual_O_h7_implementation_defect_proved"
        ),
        "stage_residual_O_h7_direct_route_proved": proof_closure.get("closure_state", {}).get(
            "stage_residual_O_h7_implementation_defect_proved"
        ),
        "stage_residual_O_h7_symbolic_certificate_proved": defect_certificate.get(
            "stage_residual_O_h7_implementation_defect_proved"
        ),
        "dynamic_symbolic_oracle_complete": proof_closure.get("closure_state", {}).get(
            "dynamic_symbolic_oracle_complete"
        ),
        "b1_symbolic_oracle_remaining": b1.get("status") == "open",
        "b3_closed_by_direct_route": b3.get("status") == "closed",
        "ad_expanded_symbolic_oracle_closure": b1_ad_expanded_symbolic_oracle.get(
            "ad_expanded_symbolic_oracle_closure"
        ),
        "eta_h_O_h7_solver_policy_evidence": proof_closure.get("closure_state", {}).get(
            "eta_h_O_h7_solver_policy_evidence"
        ),
        "summary": {
            "close_requirement_count": len(close_requirements),
            "satisfied_close_requirement_count": len(satisfied),
            "unsatisfied_close_requirement_count": len(unsatisfied),
            "unsatisfied_close_requirement_ids": [row.get("id") for row in unsatisfied],
            "certified_non_dynamic_rows": proof_closure.get("evidence_summary", {}).get(
                "certified_non_dynamic_rows"
            ),
            "open_dynamic_rows": proof_closure.get("evidence_summary", {}).get("open_dynamic_rows"),
            "newton_euler_open_obligations": proof_closure.get("evidence_summary", {}).get(
                "newton_euler_open_obligations"
            ),
            "newton_euler_symbolic_target_rows": newton_targets.get("row_count"),
            "newton_euler_translational_rows": newton_targets.get("translational_row_count"),
            "newton_euler_rotational_rows": newton_targets.get("rotational_row_count"),
            "newton_euler_row_obligation_links": target_coverage.get("row_obligation_link_count"),
            "newton_euler_rows_with_complete_obligation_sets": target_coverage.get(
                "rows_with_complete_obligation_sets"
            ),
            "newton_euler_symbolic_defect_certificate_present": bool(defect_certificate),
            "newton_euler_symbolic_defect_certificate_complete": defect_certificate.get("certificate_complete"),
            "newton_euler_symbolic_defect_certificate_certified_rows": defect_certificate.get("summary", {}).get(
                "certified_row_count"
            ),
            "newton_euler_symbolic_defect_certificate_expanded_rows": defect_certificate.get("summary", {}).get(
                "symbolic_expanded_row_count"
            ),
            "newton_euler_symbolic_defect_certificate_c1_row_expansion_closed": defect_certificate.get(
                "summary", {}
            ).get("c1_row_expansion_closed"),
            "newton_euler_symbolic_defect_certificate_runtime_expression_structure_checked": defect_certificate.get(
                "summary", {}
            ).get("runtime_expression_structure_checked"),
            "newton_euler_symbolic_defect_certificate_runtime_expression_checked_rows": defect_certificate.get(
                "summary", {}
            ).get("runtime_expression_structure_checked_rows"),
            "newton_euler_symbolic_defect_certificate_runtime_template_instantiation_checked": defect_certificate.get(
                "summary", {}
            ).get("runtime_template_instantiation_checked"),
            "newton_euler_symbolic_defect_certificate_runtime_template_instantiation_checked_rows": defect_certificate.get(
                "summary", {}
            ).get("runtime_template_instantiation_checked_rows"),
            "newton_euler_symbolic_defect_certificate_body_specific_wrench_checked": defect_certificate.get(
                "summary", {}
            ).get("body_specific_wrench_expansion_checked"),
            "newton_euler_symbolic_defect_certificate_body_specific_wrench_rows": defect_certificate.get(
                "summary", {}
            ).get("body_specific_wrench_expansion_checked_rows"),
            "newton_euler_symbolic_defect_certificate_body0_wrench_rows": defect_certificate.get(
                "summary", {}
            ).get("body0_wrench_expansion_rows"),
            "newton_euler_symbolic_defect_certificate_body1_wrench_rows": defect_certificate.get(
                "summary", {}
            ).get("body1_wrench_expansion_rows"),
            "newton_euler_symbolic_defect_certificate_open_rows": defect_certificate.get("summary", {}).get(
                "open_row_count"
            ),
            "b1_independent_symbolic_row_oracle_closed": b1_symbolic_row_oracle.get(
                "independent_symbolic_row_by_row_oracle_for_expanded_fullva_rows_closed"
            ),
            "b1_independent_symbolic_row_oracle_closed_rows": b1_symbolic_row_oracle.get(
                "independent_symbolic_row_by_row_oracle_closed_rows"
            ),
            "b1_source_template_symbolic_identity_rows": b1_symbolic_row_oracle.get(
                "source_template_symbolic_identity_rows"
            ),
            "b1_runtime_row_binding_checked_rows": b1_symbolic_row_oracle.get(
                "runtime_row_binding_checked_rows"
            ),
            "b1_ad_expanded_symbolic_oracle_closure": b1_ad_expanded_symbolic_oracle.get(
                "ad_expanded_symbolic_oracle_closure"
            ),
            "b1_ad_expanded_symbolic_oracle_closed_rows": b1_ad_expanded_symbolic_oracle.get(
                "ad_expanded_symbolic_oracle_closed_rows"
            ),
            "b1_ad_expanded_symbolic_oracle_columns_per_row": b1_ad_expanded_symbolic_oracle.get(
                "columns_per_row"
            ),
            "b1_ad_expanded_symbolic_oracle_closed_cells": b1_ad_expanded_symbolic_oracle.get(
                "ad_expanded_symbolic_oracle_closed_cells"
            ),
            "b1_ad_expanded_symbolic_oracle_dynamic_symbolic_oracle_complete": b1_ad_expanded_symbolic_oracle.get(
                "dynamic_symbolic_oracle_complete"
            ),
            "newton_euler_ad_expanded_row_oracle_checked": ad_expanded_oracle.get(
                "ad_expanded_row_oracle_closed"
            ),
            "newton_euler_ad_expanded_row_oracle_rows": ad_expanded_oracle.get(
                "ad_expanded_row_oracle_rows"
            ),
            "newton_euler_ad_expanded_row_oracle_columns_per_row": ad_expanded_oracle.get(
                "ad_expanded_row_oracle_columns_per_row"
            ),
            "newton_euler_ad_expanded_symbolic_oracle_closure": ad_expanded_oracle.get(
                "ad_expanded_symbolic_oracle_closure"
            ),
            "finite_scaled_tolerance_probe_ok_rows": solver_scale.get("finite_scaled_tolerance_probe", {}).get(
                "ok_row_count"
            ),
            "finite_scaled_tolerance_probe_total_rows": solver_scale.get("finite_scaled_tolerance_probe", {}).get(
                "row_count"
            ),
            "finite_scaled_tolerance_trajectory_probe_ok_rows": solver_scale.get(
                "finite_scaled_tolerance_trajectory_probe", {}
            ).get("ok_row_count"),
            "finite_scaled_tolerance_trajectory_probe_total_rows": solver_scale.get(
                "finite_scaled_tolerance_trajectory_probe", {}
            ).get("row_count"),
            "finite_scaled_tolerance_trajectory_probe_steps": solver_scale.get(
                "finite_scaled_tolerance_trajectory_probe", {}
            ).get("total_steps_checked"),
            "finite_h_scaled_tolerance_sweep_recorded": solver_boundary.get(
                "finite_h_scaled_tolerance_sweep_recorded"
            ),
            "finite_h_scaled_tolerance_sweep_rows": solver_scale.get("finite_tolerance_regime_sweep", {}).get(
                "finite_h_scaled_policy_rows"
            ),
            "finite_h_scaled_tolerance_sweep_steps": solver_scale.get("finite_tolerance_regime_sweep", {}).get(
                "finite_h_scaled_policy_steps"
            ),
            "finite_h_scaled_tolerance_sweep_velocity_order_floor": solver_scale.get(
                "finite_tolerance_regime_sweep", {}
            ).get("finite_h_scaled_velocity_order_floor"),
            "scaled_tolerance_sweep_recorded": solver_boundary.get("scaled_tolerance_sweep_recorded"),
        },
        "blocker_status": {
            "B1": {
                "status": b1.get("status"),
                "required_to_close": b1.get("required_to_close"),
            },
            "B3": {
                "status": b3.get("status"),
                "required_to_close": b3.get("required_to_close"),
            },
        },
        "work_lanes": work_lanes,
        "next_required_artifacts": [
            "no remaining B1/B3 proof-blocker artifact is required by this manifest",
            "keep validate_newton_euler_symbolic_defect_certificate.py passing without overclaiming O(h^7) via the symbolic-certificate route",
            "retain narrowed-claim B4/B6/B7 closure while keeping the global source-policy, eta_h, and residual-to-error boundaries explicit",
        ],
        "claim_policy": {
            "allowed_now": [
                "direct-route O(h^7) proof closure for B3",
                "independent B1 residual-row symbolic oracle closure for 36 Newton-Euler rows",
                "AD-expanded B1 symbolic oracle closure for 4752 derivative cells",
                "finite solver-policy probes as supporting evidence",
                "96 non-dynamic row certificate plus 36-row Newton-Euler target inventory",
                "AD-expanded runtime/formula binding coverage as supporting traceability",
            ],
            "forbidden_now": [
                "dynamic symbolic oracle complete",
                "eta_h solver policy proved by finite probes",
                "global submission-ready proof/package readiness outside the narrowed-claim decision",
                "symbolic-certificate route O(h^7) proof",
            ],
        },
        "execution_policy": {
            "read_only_existing_artifacts": True,
            "default_1e_4_required": False,
            "heavy_numerical_run_invoked": False,
            "run_v047_invoked": False,
            "v048_runner_invoked": False,
        },
        "source_files": {
            "proof_closure_manifest": "PROOF_CLOSURE_MANIFEST.json",
            "proof_claim_traceability": "PROOF_CLAIM_TRACEABILITY_AUDIT.json",
            "newton_euler_symbolic_target_audit": "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.json",
            "newton_euler_symbolic_defect_certificate": "NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.json",
            "b1_symbolic_row_oracle_closure_certificate": "B1_SYMBOLIC_ROW_ORACLE_CLOSURE_CERTIFICATE.json",
            "b1_ad_expanded_symbolic_oracle_closure_certificate": "B1_AD_EXPANDED_SYMBOLIC_ORACLE_CLOSURE_CERTIFICATE.json",
            "newton_euler_ad_expanded_row_oracle_audit": "NEWTON_EULER_AD_EXPANDED_ROW_ORACLE_AUDIT.json",
            "proof_solver_scale_audit": "PROOF_SOLVER_SCALE_AUDIT.json",
            "blocker_gate": "CMAME_BLOCKER_CLOSURE_GATE.json",
        },
    }

    OUT_JSON.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Proof Remaining Work Manifest",
        "",
        "Status: **proof B1/B3 closed - submission gates remaining**.",
        "Here `submission_ready=false` is scoped to proof remaining-work/global proof-package readiness,",
        "not to the separate narrowed-claim package decision.",
        "",
        f"- Submission-ready scope: `{output['submission_ready_scope']}`.",
        f"- Proof remaining-work scope: `{output['readiness_boundary']['proof_remaining_work_manifest_scope']}`.",
        f"- B4/B6/B7 narrowed-claim statuses: `{output['readiness_boundary']['narrowed_claim_b4_b6_b7_statuses']['B4']}/{output['readiness_boundary']['narrowed_claim_b4_b6_b7_statuses']['B6']}/{output['readiness_boundary']['narrowed_claim_b4_b6_b7_statuses']['B7']}`.",
        f"- Remaining global submission boundaries: `{','.join(output['readiness_boundary']['global_submission_boundaries_retained'])}`.",
        f"- Direct PC2 proof gap closed: `{output['direct_pc2_proof_gap_closed']}`.",
        f"- Direct PC2 proof-gap scope: `{output['proof_gap_closed_scope']}`.",
        f"- Schema-compatibility note: legacy `proof_gap_closed` key retained for validators only: `{output['schema_compatibility']['legacy_key_retained_for_schema_compatibility']}`; preferred reader key `{output['schema_compatibility']['preferred_key']}`.",
        f"- Schema-only compatibility reading rule: {output['proof_gap_closed_reading_rule']}",
        f"- Dynamic symbolic oracle complete: `{output['dynamic_symbolic_oracle_complete']}`.",
        f"- Stage residual O(h^7) defect proved: `{output['stage_residual_O_h7_implementation_defect_proved']}`.",
        f"- Stage residual O(h^7) direct/symbolic-certificate proof: `{output['stage_residual_O_h7_direct_route_proved']}/{output['stage_residual_O_h7_symbolic_certificate_proved']}`.",
        f"- B1 symbolic oracle remaining: `{output['b1_symbolic_oracle_remaining']}`.",
        f"- B3 closed by direct route: `{output['b3_closed_by_direct_route']}`.",
        f"- B1 AD-expanded symbolic oracle closure: `{output['ad_expanded_symbolic_oracle_closure']}`.",
        f"- PC4 residual-to-error closed/promoted: `{work_lanes[-1]['residual_to_error_closed']}/{work_lanes[-1]['residual_to_error_route_promoted']}`.",
        f"- PC4 nonpromotion boundary retained: `{work_lanes[-1]['nonpromotion_boundary_retained']}`.",
        f"- eta_h <= c_eta h^7 solver policy evidence: `{output['eta_h_O_h7_solver_policy_evidence']}`.",
        f"- eta_h theorem condition retained: `{output['remaining_gate_scope']['eta_h_theorem_condition_retained']}`.",
        f"- Residual-to-error blocking obligations: `{output['remaining_gate_scope']['residual_to_error_blocking_obligations']}`.",
        f"- Residual-to-error route promoted: `{output['remaining_gate_scope']['residual_to_error_route_promoted']}`.",
        f"- B4/B6/B7 closed elsewhere under narrowed claim: `{output['remaining_gate_scope']['b4_b6_b7_closed_elsewhere_under_narrowed_claim']}`.",
        f"- Active B1/B3 proof blockers remaining: `{output['remaining_gate_scope']['active_b1_b3_proof_blockers_remaining']}`.",
        f"- Close requirements satisfied/unsatisfied: `{output['summary']['satisfied_close_requirement_count']}/{output['summary']['unsatisfied_close_requirement_count']}`.",
        f"- Unsatisfied close requirements: `{output['summary']['unsatisfied_close_requirement_ids']}`.",
        f"- Non-dynamic certified / symbolic-lane dynamic-open rows: `{output['summary']['certified_non_dynamic_rows']}/{output['summary']['open_dynamic_rows']}`.",
        f"- Newton-Euler target rows translational/rotational: `{output['summary']['newton_euler_symbolic_target_rows']}` / `{output['summary']['newton_euler_translational_rows']}/{output['summary']['newton_euler_rotational_rows']}`.",
        f"- Newton-Euler row-obligation links: `{output['summary']['newton_euler_row_obligation_links']}`.",
        f"- Newton-Euler symbolic defect certificate present/complete: `{output['summary']['newton_euler_symbolic_defect_certificate_present']}/{output['summary']['newton_euler_symbolic_defect_certificate_complete']}`.",
        f"- Newton-Euler symbolic defect certificate expanded rows/C1 closed: `{output['summary']['newton_euler_symbolic_defect_certificate_expanded_rows']}/{output['summary']['newton_euler_symbolic_defect_certificate_c1_row_expansion_closed']}`.",
        f"- Newton-Euler runtime expression structure checked/rows: `{output['summary']['newton_euler_symbolic_defect_certificate_runtime_expression_structure_checked']}/{output['summary']['newton_euler_symbolic_defect_certificate_runtime_expression_checked_rows']}`.",
        f"- Newton-Euler runtime template instantiation checked/rows: `{output['summary']['newton_euler_symbolic_defect_certificate_runtime_template_instantiation_checked']}/{output['summary']['newton_euler_symbolic_defect_certificate_runtime_template_instantiation_checked_rows']}`.",
        f"- Newton-Euler body-specific wrench expansion checked/rows: `{output['summary']['newton_euler_symbolic_defect_certificate_body_specific_wrench_checked']}/{output['summary']['newton_euler_symbolic_defect_certificate_body_specific_wrench_rows']}`.",
        f"- Newton-Euler body0/body1 wrench expansion rows: `{output['summary']['newton_euler_symbolic_defect_certificate_body0_wrench_rows']}/{output['summary']['newton_euler_symbolic_defect_certificate_body1_wrench_rows']}`.",
        f"- Newton-Euler primitive/symbolic-lane certified/open rows: `{output['summary']['newton_euler_symbolic_defect_certificate_certified_rows']}/{output['summary']['newton_euler_symbolic_defect_certificate_open_rows']}`.",
        "- Active direct-route dynamic rows are closed separately by the D5 direct-substitution certificate; these open rows are not active PC2 open obligations.",
        f"- B1 independent residual symbolic row oracle closed/rows: `{output['summary']['b1_independent_symbolic_row_oracle_closed']}/{output['summary']['b1_independent_symbolic_row_oracle_closed_rows']}`.",
        f"- B1 source-template identity/runtime-binding rows: `{output['summary']['b1_source_template_symbolic_identity_rows']}/{output['summary']['b1_runtime_row_binding_checked_rows']}`.",
        f"- B1 AD-expanded symbolic oracle closed rows/cells: `{output['summary']['b1_ad_expanded_symbolic_oracle_closed_rows']}/{output['summary']['b1_ad_expanded_symbolic_oracle_closed_cells']}`.",
        f"- B1 AD-expanded symbolic oracle columns per row: `{output['summary']['b1_ad_expanded_symbolic_oracle_columns_per_row']}`.",
        f"- Newton-Euler AD-expanded row oracle rows/columns: `{output['summary']['newton_euler_ad_expanded_row_oracle_rows']}/{output['summary']['newton_euler_ad_expanded_row_oracle_columns_per_row']}`.",
        f"- Runtime AD-expanded audit symbolic closure flag: `{output['summary']['newton_euler_ad_expanded_symbolic_oracle_closure']}`.",
        f"- Finite scaled trajectory rows/steps: `{output['summary']['finite_scaled_tolerance_trajectory_probe_ok_rows']}/{output['summary']['finite_scaled_tolerance_trajectory_probe_total_rows']}` / `{output['summary']['finite_scaled_tolerance_trajectory_probe_steps']}`.",
        f"- Finite h-scaled tolerance-regime sweep rows/steps/velocity-order floor: `{output['summary']['finite_h_scaled_tolerance_sweep_rows']}` / `{output['summary']['finite_h_scaled_tolerance_sweep_steps']}` / `{output['summary']['finite_h_scaled_tolerance_sweep_velocity_order_floor']}`.",
        f"- Theorem-level scaled tolerance sweep recorded: `{output['summary']['scaled_tolerance_sweep_recorded']}`.",
        f"- Submission ready: `{output['submission_ready']}`.",
        "",
        "## Work Lanes",
        "",
        "| lane | status | closes | traceable now | rows |",
        "|---|---|---|---:|---:|",
    ]
    for lane in work_lanes:
        lines.append(
            f"| `{lane['lane_id']}` | `{lane['status']}` | `{lane['closes_requirement']}` | "
            f"`{lane['closes_now']}` | `{lane['rows']}` |"
        )
    lines.extend(
        [
            "",
            "## Next Required Artifacts",
            "",
        ]
    )
    for artifact in output["next_required_artifacts"]:
        lines.append(f"- `{artifact}`")
    lines.extend(
        [
            "",
            "## Claim Policy",
            "",
            "- Allowed now: direct-route O(h^7) proof closure, independent B1 residual-row symbolic oracle closure, AD-expanded B1 symbolic oracle closure, finite solver probes, explicit proof-boundary accounting, and AD-expanded runtime/formula binding coverage.",
            "- Forbidden now: dynamic symbolic oracle completion, eta_h proof by finite probes, symbolic-certificate route O(h^7) proof, and global submission-ready proof/package readiness outside the narrowed-claim decision.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("proof_remaining_work_manifest=written")
    print(f"unsatisfied_close_requirements={len(unsatisfied)}")
    print(f"open_dynamic_rows={output['summary']['open_dynamic_rows']}")
    print(f"direct_pc2_proof_gap_closed={output['direct_pc2_proof_gap_closed']}")
    print(f"legacy_proof_gap_closed={output['proof_gap_closed']}")
    print("submission_ready=False")


if __name__ == "__main__":
    main()
