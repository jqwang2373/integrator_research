#!/usr/bin/env python3
"""Validate the B1/B3 proof remaining-work manifest."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def main() -> int:
    checks = Checks()
    try:
        manifest = read_json(PAPER / "PROOF_REMAINING_WORK_MANIFEST.json")
        manifest_md = read_text(PAPER / "PROOF_REMAINING_WORK_MANIFEST.md")
        proof_closure = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
        newton_targets = read_json(PAPER / "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.json")
        defect_certificate = read_json(PAPER / "NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.json")
        b1_symbolic_row_oracle = read_json(PAPER / "B1_SYMBOLIC_ROW_ORACLE_CLOSURE_CERTIFICATE.json")
        b1_ad_expanded_symbolic_oracle = read_json(
            PAPER / "B1_AD_EXPANDED_SYMBOLIC_ORACLE_CLOSURE_CERTIFICATE.json"
        )
        ad_expanded_oracle = read_json(PAPER / "NEWTON_EULER_AD_EXPANDED_ROW_ORACLE_AUDIT.json")
        solver_scale = read_json(PAPER / "PROOF_SOLVER_SCALE_AUDIT.json")
        blocker_gate = read_json(PAPER / "CMAME_BLOCKER_CLOSURE_GATE.json")
    except Exception as exc:  # noqa: BLE001
        print(f"proof remaining-work manifest validation: FAIL\n- {exc}")
        return 1

    summary = manifest.get("summary", {})
    lanes = {lane.get("lane_id"): lane for lane in manifest.get("work_lanes", [])}
    readiness_boundary = manifest.get("readiness_boundary", {})
    remaining_gate_scope = manifest.get("remaining_gate_scope", {})
    blocker_statuses = {
        blocker.get("id"): blocker.get("status")
        for blocker in blocker_gate.get("blockers", [])
        if isinstance(blocker, dict) and blocker.get("id") in {"B4", "B6", "B7"}
    }
    global_submission_boundaries = [
        "full_source_policy_package_ready",
        "theorem_level_eta_h_solver_policy_evidence",
        "closed_residual_to_error_theorem_for_mechanism_rows",
    ]

    checks.check(manifest.get("schema") == "proof-remaining-work-manifest-v1", "schema changed")
    checks.check(
        manifest.get("status") == "proof_b1_b3_closed_submission_gates_remaining",
        "status changed",
    )
    checks.check(manifest.get("submission_ready") is False, "manifest overclaims submission readiness")
    checks.check(
        manifest.get("submission_ready_scope")
        == "proof_remaining_work_global_boundary_not_narrowed_claim_package_decision",
        "submission-ready scope changed",
    )
    checks.check(
        readiness_boundary.get("proof_remaining_work_manifest_scope")
        == "B1_B3_closed_remaining_global_submission_gates",
        "proof remaining-work scope changed",
    )
    checks.check(
        readiness_boundary.get("narrowed_claim_b4_b6_b7_statuses") == blocker_statuses,
        "narrowed-claim B4/B6/B7 statuses not sourced from blocker gate",
    )
    checks.check(
        readiness_boundary.get("narrowed_claim_b4_b6_b7_statuses")
        == {"B4": "closed", "B6": "closed", "B7": "closed"},
        "narrowed-claim B4/B6/B7 statuses are not closed",
    )
    checks.check(
        readiness_boundary.get("global_submission_boundaries_retained")
        == global_submission_boundaries,
        "global submission boundaries changed",
    )
    checks.check(
        remaining_gate_scope.get("narrowed_claim_b4_b6_b7_statuses") == blocker_statuses,
        "remaining gate narrowed-claim statuses not sourced from blocker gate",
    )
    checks.check(
        remaining_gate_scope.get("b4_b6_b7_closed_elsewhere_under_narrowed_claim") is True,
        "remaining gate lost narrowed-claim B4/B6/B7 closure marker",
    )
    checks.check(
        remaining_gate_scope.get("eta_h_O_h7_solver_policy_evidence")
        is proof_closure.get("closure_state", {}).get("eta_h_O_h7_solver_policy_evidence")
        is False,
        "remaining gate eta_h solver-policy boundary changed",
    )
    checks.check(
        remaining_gate_scope.get("eta_h_theorem_condition_retained") is True,
        "remaining gate lost retained eta_h theorem condition marker",
    )
    checks.check(
        remaining_gate_scope.get("residual_to_error_blocking_obligations")
        == proof_closure.get("evidence_summary", {}).get("residual_to_error_blocking_obligations")
        == 7,
        "remaining gate residual-to-error blocking count changed",
    )
    checks.check(
        remaining_gate_scope.get("residual_to_error_route_promoted") is False,
        "remaining gate overclaims residual-to-error promotion",
    )
    checks.check(
        remaining_gate_scope.get("active_b1_b3_proof_blockers_remaining") is False,
        "remaining gate overstates active B1/B3 proof blockers",
    )
    checks.check(
        remaining_gate_scope.get("global_submission_boundaries_retained") == global_submission_boundaries,
        "remaining gate global boundaries changed",
    )
    checks.check(manifest.get("proof_gap_closed") is True, "proof gap should be closed by direct substitution")
    checks.check(
        manifest.get("proof_gap_closed_scope")
        == "direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open",
        "proof gap scope missing or changed",
    )
    checks.check(
        "schema-compatible shorthand for direct_pc2_proof_gap_closed"
        in manifest.get("proof_gap_closed_reading_rule", ""),
        "proof-gap reading rule missing direct-PC2 scope",
    )
    schema_compat = manifest.get("schema_compatibility", {})
    checks.check(
        schema_compat.get("legacy_key") == "proof_gap_closed"
        and schema_compat.get("legacy_key_retained_for_schema_compatibility") is True
        and schema_compat.get("preferred_key") == "direct_pc2_proof_gap_closed",
        "proof-gap schema compatibility missing or changed",
    )
    checks.check(manifest.get("direct_pc2_proof_gap_closed") is True, "direct PC2 scope marker missing")
    checks.check(manifest.get("dynamic_symbolic_oracle_complete") is False, "symbolic oracle unexpectedly closed")
    checks.check(
        manifest.get("stage_residual_O_h7_implementation_defect_proved") is True,
        "direct dynamic defect proof not reflected",
    )
    checks.check(
        manifest.get("stage_residual_O_h7_direct_route_proved") is True,
        "direct-route O(h^7) proof marker missing",
    )
    checks.check(
        manifest.get("stage_residual_O_h7_symbolic_certificate_proved") is False,
        "symbolic certificate unexpectedly proves O(h^7)",
    )
    checks.check(manifest.get("b1_symbolic_oracle_remaining") is False, "B1 symbolic oracle should be closed")
    checks.check(manifest.get("b3_closed_by_direct_route") is True, "B3 direct-route closure not reflected")
    checks.check(
        manifest.get("ad_expanded_symbolic_oracle_closure") is True,
        "AD-expanded symbolic oracle closure certificate not reflected",
    )
    checks.check(manifest.get("eta_h_O_h7_solver_policy_evidence") is False, "eta_h proof unexpectedly closed")
    checks.check(summary.get("close_requirement_count") == 4, "close requirement count changed")
    checks.check(summary.get("satisfied_close_requirement_count") == 4, "satisfied close count changed")
    checks.check(summary.get("unsatisfied_close_requirement_count") == 0, "unsatisfied close count changed")
    checks.check(summary.get("unsatisfied_close_requirement_ids") == [], "unsatisfied ids changed")
    checks.check(summary.get("certified_non_dynamic_rows") == 96, "certified non-dynamic row count changed")
    checks.check(summary.get("open_dynamic_rows") == 36, "open dynamic row count changed")
    checks.check(summary.get("newton_euler_open_obligations") == 1, "Newton-Euler obligation count changed")
    checks.check(
        summary.get("newton_euler_symbolic_target_rows") == newton_targets.get("row_count") == 36,
        "Newton-Euler target row count changed",
    )
    checks.check(summary.get("newton_euler_translational_rows") == 18, "translational row count changed")
    checks.check(summary.get("newton_euler_rotational_rows") == 18, "rotational row count changed")
    checks.check(summary.get("newton_euler_row_obligation_links") == 180, "row-obligation link count changed")
    checks.check(
        summary.get("newton_euler_rows_with_complete_obligation_sets") == 36,
        "complete obligation row count changed",
    )
    checks.check(
        summary.get("newton_euler_symbolic_defect_certificate_present") is True,
        "symbolic defect certificate presence marker missing",
    )
    checks.check(
        summary.get("newton_euler_symbolic_defect_certificate_complete") is False,
        "symbolic defect certificate unexpectedly complete",
    )
    checks.check(
        summary.get("newton_euler_symbolic_defect_certificate_certified_rows")
        == defect_certificate.get("summary", {}).get("certified_row_count")
        == 0,
        "symbolic defect certificate certified rows changed",
    )
    checks.check(
        summary.get("newton_euler_symbolic_defect_certificate_expanded_rows")
        == defect_certificate.get("summary", {}).get("symbolic_expanded_row_count")
        == 36,
        "symbolic defect certificate expanded rows changed",
    )
    checks.check(
        summary.get("newton_euler_symbolic_defect_certificate_c1_row_expansion_closed")
        == defect_certificate.get("summary", {}).get("c1_row_expansion_closed")
        is True,
        "symbolic defect certificate C1 row expansion boundary changed",
    )
    checks.check(
        summary.get("newton_euler_symbolic_defect_certificate_runtime_expression_structure_checked")
        == defect_certificate.get("summary", {}).get("runtime_expression_structure_checked")
        is True,
        "symbolic defect certificate runtime expression audit marker changed",
    )
    checks.check(
        summary.get("newton_euler_symbolic_defect_certificate_runtime_expression_checked_rows")
        == defect_certificate.get("summary", {}).get("runtime_expression_structure_checked_rows")
        == 36,
        "symbolic defect certificate runtime expression checked rows changed",
    )
    checks.check(
        summary.get("newton_euler_symbolic_defect_certificate_runtime_template_instantiation_checked")
        == defect_certificate.get("summary", {}).get("runtime_template_instantiation_checked")
        is True,
        "symbolic defect certificate runtime template instantiation marker changed",
    )
    checks.check(
        summary.get("newton_euler_symbolic_defect_certificate_runtime_template_instantiation_checked_rows")
        == defect_certificate.get("summary", {}).get("runtime_template_instantiation_checked_rows")
        == 36,
        "symbolic defect certificate runtime template instantiation row count changed",
    )
    checks.check(
        summary.get("newton_euler_symbolic_defect_certificate_body_specific_wrench_checked")
        == defect_certificate.get("summary", {}).get("body_specific_wrench_expansion_checked")
        is True,
        "symbolic defect certificate body-specific wrench marker changed",
    )
    checks.check(
        summary.get("newton_euler_symbolic_defect_certificate_body_specific_wrench_rows")
        == defect_certificate.get("summary", {}).get("body_specific_wrench_expansion_checked_rows")
        == 36,
        "symbolic defect certificate body-specific wrench row count changed",
    )
    checks.check(
        summary.get("newton_euler_symbolic_defect_certificate_body0_wrench_rows")
        == defect_certificate.get("summary", {}).get("body0_wrench_expansion_rows")
        == 18,
        "symbolic defect certificate body0 wrench row count changed",
    )
    checks.check(
        summary.get("newton_euler_symbolic_defect_certificate_body1_wrench_rows")
        == defect_certificate.get("summary", {}).get("body1_wrench_expansion_rows")
        == 18,
        "symbolic defect certificate body1 wrench row count changed",
    )
    checks.check(
        summary.get("newton_euler_symbolic_defect_certificate_open_rows")
        == defect_certificate.get("summary", {}).get("open_row_count")
        == 36,
        "symbolic defect certificate open rows changed",
    )
    checks.check(
        summary.get("b1_independent_symbolic_row_oracle_closed")
        == b1_symbolic_row_oracle.get(
            "independent_symbolic_row_by_row_oracle_for_expanded_fullva_rows_closed"
        )
        is True,
        "B1 independent symbolic row-oracle closure marker changed",
    )
    checks.check(
        summary.get("b1_independent_symbolic_row_oracle_closed_rows")
        == b1_symbolic_row_oracle.get("independent_symbolic_row_by_row_oracle_closed_rows")
        == 36,
        "B1 independent symbolic row-oracle closed rows changed",
    )
    checks.check(
        summary.get("b1_source_template_symbolic_identity_rows")
        == b1_symbolic_row_oracle.get("source_template_symbolic_identity_rows")
        == 36,
        "B1 source-template identity row count changed",
    )
    checks.check(
        summary.get("b1_runtime_row_binding_checked_rows")
        == b1_symbolic_row_oracle.get("runtime_row_binding_checked_rows")
        == 36,
        "B1 runtime row binding row count changed",
    )
    checks.check(
        summary.get("b1_ad_expanded_symbolic_oracle_closure")
        == b1_ad_expanded_symbolic_oracle.get("ad_expanded_symbolic_oracle_closure")
        is True,
        "B1 AD-expanded symbolic oracle closure marker changed",
    )
    checks.check(
        summary.get("b1_ad_expanded_symbolic_oracle_closed_rows")
        == b1_ad_expanded_symbolic_oracle.get("ad_expanded_symbolic_oracle_closed_rows")
        == 36,
        "B1 AD-expanded closed row count changed",
    )
    checks.check(
        summary.get("b1_ad_expanded_symbolic_oracle_columns_per_row")
        == b1_ad_expanded_symbolic_oracle.get("columns_per_row")
        == 132,
        "B1 AD-expanded column count changed",
    )
    checks.check(
        summary.get("b1_ad_expanded_symbolic_oracle_closed_cells")
        == b1_ad_expanded_symbolic_oracle.get("ad_expanded_symbolic_oracle_closed_cells")
        == 4752,
        "B1 AD-expanded closed derivative-cell count changed",
    )
    checks.check(
        summary.get("b1_ad_expanded_symbolic_oracle_dynamic_symbolic_oracle_complete")
        == b1_ad_expanded_symbolic_oracle.get("dynamic_symbolic_oracle_complete")
        is False,
        "B1 AD-expanded certificate overclaims global symbolic oracle",
    )
    checks.check(
        summary.get("newton_euler_ad_expanded_row_oracle_checked")
        == ad_expanded_oracle.get("ad_expanded_row_oracle_closed")
        is True,
        "AD-expanded row oracle marker changed",
    )
    checks.check(
        summary.get("newton_euler_ad_expanded_row_oracle_rows")
        == ad_expanded_oracle.get("ad_expanded_row_oracle_rows")
        == 36,
        "AD-expanded row count changed",
    )
    checks.check(
        summary.get("newton_euler_ad_expanded_row_oracle_columns_per_row")
        == ad_expanded_oracle.get("ad_expanded_row_oracle_columns_per_row")
        == 132,
        "AD-expanded column count changed",
    )
    checks.check(
        summary.get("newton_euler_ad_expanded_symbolic_oracle_closure")
        == ad_expanded_oracle.get("ad_expanded_symbolic_oracle_closure")
        is False,
        "runtime AD-expanded audit symbolic closure flag changed",
    )
    checks.check(summary.get("finite_scaled_tolerance_probe_ok_rows") == 4, "finite probe ok count changed")
    checks.check(summary.get("finite_scaled_tolerance_probe_total_rows") == 4, "finite probe total changed")
    checks.check(
        summary.get("finite_scaled_tolerance_trajectory_probe_ok_rows") == 4,
        "trajectory probe ok count changed",
    )
    checks.check(
        summary.get("finite_scaled_tolerance_trajectory_probe_total_rows") == 4,
        "trajectory probe total changed",
    )
    checks.check(summary.get("finite_scaled_tolerance_trajectory_probe_steps") == 30, "trajectory steps changed")
    checks.check(
        summary.get("finite_h_scaled_tolerance_sweep_recorded") is True,
        "finite h-scaled tolerance-regime marker missing",
    )
    checks.check(summary.get("finite_h_scaled_tolerance_sweep_rows") == 8, "finite h-scaled row count changed")
    checks.check(summary.get("finite_h_scaled_tolerance_sweep_steps") == 60, "finite h-scaled step count changed")
    checks.check(
        float(summary.get("finite_h_scaled_tolerance_sweep_velocity_order_floor", 0.0)) > 6.0,
        "finite h-scaled velocity order floor too small",
    )
    checks.check(summary.get("scaled_tolerance_sweep_recorded") is False, "scaled tolerance sweep overclaimed")
    checks.check(
        set(lanes)
        == {
            "PC1_symbolic_row_oracle",
            "PC2_direct_dynamic_O_h7_defect_certificate",
            "B1_AD_expanded_symbolic_oracle",
            "PC3_solver_eta_policy",
            "PC4_residual_to_error_boundary",
        },
        "work lane set changed",
    )
    checks.check(lanes["PC1_symbolic_row_oracle"].get("closes_now") is True, "PC1 lane should close")
    checks.check(
        any("no remaining PC1-specific work" in item for item in lanes["PC1_symbolic_row_oracle"].get("required_to_close", [])),
        "PC1 lane missing closed-work marker",
    )
    checks.check(
        any("NEWTON_EULER_BALANCE_IDENTITY_AUDIT.json closes D1/D2" in item for item in lanes["PC1_symbolic_row_oracle"].get("current_evidence", [])),
        "PC1 lane missing balance-identity current evidence",
    )
    checks.check(
        lanes["PC2_direct_dynamic_O_h7_defect_certificate"].get("closes_now") is True,
        "PC2 direct-route lane should close",
    )
    checks.check(
        lanes["B1_AD_expanded_symbolic_oracle"].get("closes_now") is True,
        "B1 AD-expanded symbolic oracle lane should close",
    )
    checks.check(
        any(
            "B1_SYMBOLIC_ROW_ORACLE_CLOSURE_CERTIFICATE.json closes the independent residual-row"
            in item
            for item in lanes["B1_AD_expanded_symbolic_oracle"].get("current_evidence", [])
        ),
        "B1 lane missing independent row-oracle closure evidence",
    )
    checks.check(
        any(
            "B1_AD_EXPANDED_SYMBOLIC_ORACLE_CLOSURE_CERTIFICATE.json differentiates the closed residual identities"
            in item
            for item in lanes["B1_AD_expanded_symbolic_oracle"].get("current_evidence", [])
        ),
        "B1 lane missing AD-expanded closure certificate evidence",
    )
    checks.check(
        any(
            "no remaining B1 AD-expanded symbolic-oracle work" in item
            for item in lanes["B1_AD_expanded_symbolic_oracle"].get("required_to_close", [])
        ),
        "B1 lane missing closed-work marker",
    )
    checks.check(lanes["PC3_solver_eta_policy"].get("closes_now") is True, "PC3 lane should be condition-retained")
    pc4_lane = lanes["PC4_residual_to_error_boundary"]
    checks.check(
        pc4_lane.get("status") == "nonpromotion_boundary_retained",
        "PC4 lane should retain the nonpromotion boundary",
    )
    checks.check(
        pc4_lane.get("closes_now") == "nonpromotion_only",
        "PC4 lane traceability should be nonpromotion-only",
    )
    checks.check(
        pc4_lane.get("nonpromotion_boundary_retained") is True,
        "PC4 nonpromotion boundary marker missing",
    )
    checks.check(
        pc4_lane.get("residual_to_error_closed") is False,
        "PC4 residual-to-error closure overclaimed",
    )
    checks.check(
        pc4_lane.get("residual_to_error_route_promoted") is False,
        "PC4 residual-to-error promotion overclaimed",
    )
    checks.check(
        pc4_lane.get("satisfaction_mode")
        == "nonpromotion_boundary_retained_residual_to_error_theorem_open",
        "PC4 nonpromotion mode changed",
    )
    checks.check(
        proof_closure.get("close_requirements", [])[0].get("id") == "PC1",
        "proof closure manifest not loaded as source",
    )
    checks.check(
        solver_scale.get("proof_boundary", {}).get("scaled_tolerance_sweep_recorded") is False,
        "solver audit overclaims scaled sweep",
    )

    for token in [
        "Proof Remaining Work Manifest",
        "proof B1/B3 closed - submission gates remaining",
        "Here `submission_ready=false` is scoped to proof remaining-work/global proof-package readiness,",
        "not to the separate narrowed-claim package decision.",
        "Submission-ready scope: `proof_remaining_work_global_boundary_not_narrowed_claim_package_decision`.",
        "Proof remaining-work scope: `B1_B3_closed_remaining_global_submission_gates`.",
        "B4/B6/B7 narrowed-claim statuses: `closed/closed/closed`.",
        "Remaining global submission boundaries: `full_source_policy_package_ready,theorem_level_eta_h_solver_policy_evidence,closed_residual_to_error_theorem_for_mechanism_rows`.",
        "Direct PC2 proof gap closed: `True`.",
        "Direct PC2 proof-gap scope: `direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open`.",
        "Schema-compatibility note: legacy `proof_gap_closed` key retained for validators only: `True`; preferred reader key `direct_pc2_proof_gap_closed`.",
        "Schema-only compatibility reading rule: The schema-only compatibility boolean proof_gap_closed is a schema-compatible shorthand for direct_pc2_proof_gap_closed under the active direct PC2 residual-bridge/Kantorovich route.",
        "Close requirements satisfied/unsatisfied: `4/0`.",
        "Unsatisfied close requirements: `[]`.",
        "Non-dynamic certified / symbolic-lane dynamic-open rows: `96/36`.",
        "Stage residual O(h^7) direct/symbolic-certificate proof: `True/False`.",
        "B1 symbolic oracle remaining: `False`.",
        "B3 closed by direct route: `True`.",
        "B1 AD-expanded symbolic oracle closure: `True`.",
        "PC4 residual-to-error closed/promoted: `False/False`.",
        "PC4 nonpromotion boundary retained: `True`.",
        "eta_h theorem condition retained: `True`.",
        "Residual-to-error blocking obligations: `7`.",
        "Residual-to-error route promoted: `False`.",
        "B4/B6/B7 closed elsewhere under narrowed claim: `True`.",
        "Active B1/B3 proof blockers remaining: `False`.",
        "Newton-Euler row-obligation links: `180`.",
        "Newton-Euler symbolic defect certificate present/complete: `True/False`.",
        "Newton-Euler symbolic defect certificate expanded rows/C1 closed: `36/True`.",
        "Newton-Euler runtime expression structure checked/rows: `True/36`.",
        "Newton-Euler runtime template instantiation checked/rows: `True/36`.",
        "Newton-Euler body-specific wrench expansion checked/rows: `True/36`.",
        "Newton-Euler body0/body1 wrench expansion rows: `18/18`.",
        "Newton-Euler primitive/symbolic-lane certified/open rows: `0/36`.",
        "Active direct-route dynamic rows are closed separately by the D5 direct-substitution certificate; these open rows are not active PC2 open obligations.",
        "B1 independent residual symbolic row oracle closed/rows: `True/36`.",
        "B1 source-template identity/runtime-binding rows: `36/36`.",
        "B1 AD-expanded symbolic oracle closed rows/cells: `36/4752`.",
        "B1 AD-expanded symbolic oracle columns per row: `132`.",
        "Newton-Euler AD-expanded row oracle rows/columns: `36/132`.",
        "Runtime AD-expanded audit symbolic closure flag: `False`.",
        "Finite scaled trajectory rows/steps: `4/4` / `30`.",
        "Finite h-scaled tolerance-regime sweep rows/steps/velocity-order floor: `8` / `60`",
        "Theorem-level scaled tolerance sweep recorded: `False`.",
        "`no remaining B1/B3 proof-blocker artifact is required by this manifest`",
        "`retain narrowed-claim B4/B6/B7 closure while keeping the global source-policy, eta_h, and residual-to-error boundaries explicit`",
        "Forbidden now: dynamic symbolic oracle completion",
        "global submission-ready proof/package readiness outside the narrowed-claim decision",
    ]:
        checks.check(token in manifest_md, f"manifest markdown missing token: {token}")

    execution = manifest.get("execution_policy", {})
    checks.check(execution.get("read_only_existing_artifacts") is True, "manifest is not read-only")
    checks.check(execution.get("default_1e_4_required") is False, "manifest requires default 1e-4")
    checks.check(execution.get("heavy_numerical_run_invoked") is False, "manifest invoked heavy run")
    checks.check(execution.get("run_v047_invoked") is False, "manifest invoked run_v047")
    checks.check(execution.get("v048_runner_invoked") is False, "manifest invoked v048 runner")

    if checks.errors:
        print("proof remaining-work manifest validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("proof remaining-work manifest validation: PASS")
    print("unsatisfied_close_requirements=0")
    print("open_dynamic_rows=36")
    print("newton_euler_row_obligation_links=180")
    print("direct_pc2_proof_gap_closed=True")
    print("legacy_proof_gap_closed=True")
    print("active_b1_b3_proof_blockers_remaining=False")
    print("residual_to_error_blocking_obligations=7")
    print("submission_ready=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
