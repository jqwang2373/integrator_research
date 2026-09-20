#!/usr/bin/env python3
"""Read-only validator for the proof solver-scale audit."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
ROOT = PAPER.parent
AUDIT_JSON = PAPER / "PROOF_SOLVER_SCALE_AUDIT.json"
AUDIT_MD = PAPER / "PROOF_SOLVER_SCALE_AUDIT.md"
SUMMARY = ROOT / "v047_cylindrical_chain_pipeline" / "results" / "summary_v047.json"
MANIFEST = PAPER / "SUBMISSION_ARTIFACT_MANIFEST.json"
PROOF_CONTRACT = PAPER / "CMAME_PROOF_CONTRACT_GATE.json"
BLOCKER_GATE = PAPER / "CMAME_BLOCKER_CLOSURE_GATE.json"
MAIN_TEX = LATEX / "main_cmame.tex"
FLAT_TEX = LATEX / "cmame_submission_flat" / "main_cmame_submission.tex"


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
    return token in text or " ".join(token.split()) in " ".join(text.split())


def require_tokens(checks: Checks, text: str, tokens: list[str], label: str) -> None:
    for token in tokens:
        checks.check(contains_normalized(text, token), f"{label} missing token: {token}")


def close(actual: float, expected: Any, tol: float = 1.0e-12) -> bool:
    expected_float = float(expected)
    return abs(actual - expected_float) <= tol * max(1.0, abs(actual), abs(expected_float))


def close_list(actual: list[float], expected: Any, tol: float = 1.0e-12) -> bool:
    if not isinstance(expected, list) or len(actual) != len(expected):
        return False
    return all(close(a, e, tol=tol) for a, e in zip(actual, expected))


def blocker_by_id(blocker_gate: dict[str, Any], blocker_id: str) -> dict[str, Any]:
    for blocker in blocker_gate.get("blockers", []):
        if isinstance(blocker, dict) and blocker.get("id") == blocker_id:
            return blocker
    return {}


def blocker_statuses(blocker_gate: dict[str, Any], blocker_ids: set[str]) -> dict[str, Any]:
    return {
        blocker.get("id"): blocker.get("status")
        for blocker in blocker_gate.get("blockers", [])
        if isinstance(blocker, dict) and blocker.get("id") in blocker_ids
    }


def extract_residuals(summary: dict[str, Any]) -> dict[str, float]:
    convergence = summary["convergence"]["cases"]
    endpoint_kkt = summary["endpoint_kkt_closure"]["cases"]
    asme = summary["asme_gate"]["method_runs"]
    return {
        "smooth_projected_reference_max_linear_residual_norm": float(
            convergence["cylindrical_smooth"]["projected_velocity"]["reference"]["max_linear_residual_norm"]
        ),
        "smooth_raw_reference_max_linear_residual_norm": float(
            convergence["cylindrical_smooth"]["raw_endpoint"]["reference"]["max_linear_residual_norm"]
        ),
        "sharp_projected_reference_max_linear_residual_norm": float(
            convergence["cylindrical_sharp"]["projected_velocity"]["reference"]["max_linear_residual_norm"]
        ),
        "sharp_raw_reference_max_linear_residual_norm": float(
            convergence["cylindrical_sharp"]["raw_endpoint"]["reference"]["max_linear_residual_norm"]
        ),
        "endpoint_kkt_smooth_reference_max_linear_residual_norm": float(
            endpoint_kkt["cylindrical_smooth"]["reference"]["max_linear_residual_norm"]
        ),
        "endpoint_kkt_sharp_reference_max_linear_residual_norm": float(
            endpoint_kkt["cylindrical_sharp"]["reference"]["max_linear_residual_norm"]
        ),
        "single_pendulum_driven_fullva_max_stage_residual_norm": float(
            asme["single_pendulum_driven_fullva"]["max_stage_residual_norm"]
        ),
        "single_pendulum_absolute_fullva_max_stage_residual_norm": float(
            asme["single_pendulum_driven_absolute_fullva"]["max_stage_residual_norm"]
        ),
    }


def eta_over_h7(eta: float, h_values: list[float]) -> list[float]:
    return [eta / math.pow(h, 7) for h in h_values]


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(AUDIT_JSON)
        audit_md = read_text(AUDIT_MD)
        summary = read_json(SUMMARY)
        manifest = read_json(MANIFEST)
        proof_contract = read_json(PROOF_CONTRACT)
        blocker_gate = read_json(BLOCKER_GATE)
        main_tex = read_text(MAIN_TEX)
        flat_tex = read_text(FLAT_TEX)
    except Exception as exc:  # noqa: BLE001 - concise CLI failure.
        print(f"proof_solver_scale_audit=FAIL\n- {exc}")
        return 1

    residuals = extract_residuals(summary)
    h_values = [float(h) for h in audit.get("eta_over_h7_diagnostics", {}).get("h_values", [])]
    smooth_ratios = eta_over_h7(residuals["smooth_projected_reference_max_linear_residual_norm"], h_values)
    endpoint_ratios = eta_over_h7(residuals["endpoint_kkt_smooth_reference_max_linear_residual_norm"], h_values)

    checks.check(audit.get("schema") == "proof-solver-scale-audit-v1", "audit schema changed")
    checks.check(
        audit.get("status") == "summary_level_solver_residuals_recorded_not_scaled_eta_h_proof",
        "audit status changed",
    )
    checks.check(audit.get("submission_ready") is False, "audit incorrectly claims submission ready")
    readiness_boundary = audit.get("readiness_boundary", {})
    expected_global_boundaries = [
        "full_source_policy_package_ready",
        "theorem_level_eta_h_solver_policy_evidence",
        "closed_residual_to_error_theorem_for_mechanism_rows",
    ]
    checks.check(
        audit.get("submission_ready_scope")
        == "solver_scale_global_eta_h_boundary_not_narrowed_claim_package_decision",
        "submission-ready scope changed",
    )
    checks.check(
        readiness_boundary.get("solver_scale_audit_scope")
        == "finite_solver_scale_diagnostic_and_theorem_level_eta_h_boundary",
        "solver-scale audit scope changed",
    )
    checks.check(
        readiness_boundary.get("narrowed_claim_b4_b6_b7_statuses")
        == blocker_statuses(blocker_gate, {"B4", "B6", "B7"})
        == {"B4": "closed", "B6": "closed", "B7": "closed"},
        "narrowed-claim B4/B6/B7 statuses changed",
    )
    checks.check(
        readiness_boundary.get("global_submission_boundaries_retained") == expected_global_boundaries,
        "global submission boundaries changed",
    )
    remaining_gate_scope = audit.get("remaining_gate_scope", {})
    checks.check(
        remaining_gate_scope.get("narrowed_claim_b4_b6_b7_statuses")
        == readiness_boundary.get("narrowed_claim_b4_b6_b7_statuses"),
        "remaining-gate narrowed-claim statuses changed",
    )
    checks.check(
        remaining_gate_scope.get("b4_b6_b7_closed_elsewhere_under_narrowed_claim") is True,
        "remaining-gate lost narrowed-claim B4/B6/B7 closure marker",
    )
    checks.check(
        remaining_gate_scope.get("global_submission_boundaries_retained") == expected_global_boundaries,
        "remaining-gate global submission boundaries changed",
    )
    checks.check(audit.get("accepted_method") == "Gauss6/FullVA", "accepted method changed")
    checks.check(audit.get("source_summary") == "../v047_cylindrical_chain_pipeline/results/summary_v047.json", "source summary changed")

    execution = audit.get("execution_policy", {})
    checks.check(execution.get("read_only_audit") is True, "audit lost read-only marker")
    checks.check(execution.get("default_step_policy") == "coarse_first_no_default_1e-4", "default policy changed")
    checks.check(execution.get("default_1e-4_required") is False, "audit incorrectly requires default 1e-4")
    checks.check(execution.get("heavy_numerical_run_invoked") is False, "audit invoked heavy run")
    checks.check(execution.get("run_v047_invoked") is False, "audit invoked run_v047")

    recorded = audit.get("recorded_solver_residuals", {})
    checks.check(set(recorded) == set(residuals), "recorded residual keys changed")
    for key, value in residuals.items():
        checks.check(close(value, recorded.get(key)), f"recorded residual changed: {key}")

    diagnostics = audit.get("eta_over_h7_diagnostics", {})
    checks.check(h_values == [0.04, 0.02, 0.01, 0.005], "h diagnostic values changed")
    checks.check(
        close_list(smooth_ratios, diagnostics.get("smooth_projected_reference_residual_over_h7")),
        "smooth eta/h7 ratios changed",
    )
    checks.check(
        close_list(endpoint_ratios, diagnostics.get("endpoint_kkt_smooth_reference_linear_residual_over_h7")),
        "endpoint-KKT eta/h7 ratios changed",
    )
    checks.check(smooth_ratios[-1] > smooth_ratios[0], "smooth eta/h7 ratios should grow toward fine h for fixed residual")
    checks.check(endpoint_ratios[-1] > endpoint_ratios[0], "endpoint eta/h7 ratios should grow toward fine h for fixed residual")

    boundary = audit.get("proof_boundary", {})
    checks.check(boundary.get("summary_level_solver_residuals_recorded") is True, "summary residual marker changed")
    checks.check(boundary.get("convergence_csv_newton_residual_norm_recorded") is False, "audit overclaims CSV residual rows")
    checks.check(
        boundary.get("finite_scaled_tolerance_probe_recorded") is True,
        "audit lost finite scaled-tolerance probe marker",
    )
    checks.check(
        boundary.get("finite_scaled_tolerance_trajectory_probe_recorded") is True,
        "audit lost finite scaled-tolerance trajectory probe marker",
    )
    checks.check(
        boundary.get("finite_tolerance_regime_sweep_recorded") is True,
        "audit lost finite tolerance-regime sweep marker",
    )
    checks.check(
        boundary.get("finite_h_scaled_tolerance_sweep_recorded") is True,
        "audit lost finite h-scaled tolerance-regime sweep marker",
    )
    checks.check(
        boundary.get("fixed_tolerance_window_comparison_only") is True,
        "audit lost fixed-tolerance finite-window comparison boundary",
    )
    checks.check(
        boundary.get("fixed_tolerance_does_not_instantiate_P6") is True,
        "audit lost fixed-tolerance P6 non-instantiation boundary",
    )
    checks.check(boundary.get("scaled_tolerance_sweep_recorded") is False, "audit overclaims scaled tolerance sweep")
    checks.check(boundary.get("eta_h_O_h7_solver_policy_evidence") is False, "audit overclaims eta_h proof")
    checks.check(boundary.get("fixed_tolerance_runs_are_asymptotic_proof") is False, "audit overclaims fixed tolerance proof")
    checks.check(
        boundary.get("stage_residual_O_h7_implementation_defect_proved_by_this_audit") is False,
        "audit overclaims implementation defect proof by solver-scale diagnostics",
    )
    checks.check(boundary.get("dynamic_symbolic_oracle_complete") is False, "audit overclaims symbolic oracle")
    checks.check(boundary.get("external_superiority_claim") is False, "audit overclaims external superiority")
    checks.check(
        remaining_gate_scope.get("finite_solver_scale_diagnostic_recorded") is True,
        "remaining-gate lost finite solver-scale diagnostic marker",
    )
    for key in [
        "summary_level_solver_residuals_recorded",
        "convergence_csv_newton_residual_norm_recorded",
        "finite_scaled_tolerance_probe_recorded",
        "finite_scaled_tolerance_trajectory_probe_recorded",
        "finite_tolerance_regime_sweep_recorded",
        "finite_h_scaled_tolerance_sweep_recorded",
        "fixed_tolerance_window_comparison_only",
        "fixed_tolerance_does_not_instantiate_P6",
        "scaled_tolerance_sweep_recorded",
        "eta_h_O_h7_solver_policy_evidence",
        "fixed_tolerance_runs_are_asymptotic_proof",
        "dynamic_symbolic_oracle_complete",
    ]:
        checks.check(remaining_gate_scope.get(key) == boundary.get(key), f"remaining-gate boundary mismatch: {key}")
    checks.check(
        remaining_gate_scope.get("eta_h_theorem_condition_retained") is True,
        "remaining-gate lost eta_h theorem-condition marker",
    )
    checks.check(
        remaining_gate_scope.get("stage_residual_O_h7_implementation_defect_proved_by_this_audit") is False,
        "remaining-gate overclaims implementation defect proof by solver-scale audit",
    )

    theorem = proof_contract.get("theorem_contract", {})
    checks.check(theorem.get("solver_scale_audit_checked") is True, "proof contract lost solver-scale audit marker")
    checks.check(theorem.get("summary_level_solver_residuals_recorded") is True, "proof contract lost residual-record marker")
    checks.check(theorem.get("scaled_tolerance_sweep_recorded") is False, "proof contract overclaims scaled tolerance sweep")
    checks.check(
        theorem.get("eta_h_O_h7_solver_policy_evidence") is False,
        "proof contract overclaims eta_h proof",
    )

    tolerance_sweep = audit.get("finite_tolerance_regime_sweep", {})
    checks.check(
        tolerance_sweep.get("fixed_tolerance_window_comparison_only") is True,
        "tolerance-regime sweep lost finite-window-only boundary",
    )
    checks.check(
        tolerance_sweep.get("fixed_tolerance_does_not_instantiate_P6") is True,
        "tolerance-regime sweep lost P6 non-instantiation boundary",
    )

    b3 = blocker_by_id(blocker_gate, "B3")
    checks.check("proof_solver_scale_audit_added" in b3.get("partial_progress", []), "B3 lost solver-scale progress marker")
    checks.check("PROOF_SOLVER_SCALE_AUDIT.md" in b3.get("partial_progress_evidence", []), "B3 solver-scale audit MD missing")
    checks.check("PROOF_SOLVER_SCALE_AUDIT.json" in b3.get("partial_progress_evidence", []), "B3 solver-scale audit JSON missing")
    checks.check("validate_proof_solver_scale_audit.py" in b3.get("partial_progress_evidence", []), "B3 solver-scale validator missing")
    checks.check(b3.get("summary_level_solver_residuals_recorded") is True, "B3 residual-record marker changed")
    checks.check(b3.get("scaled_tolerance_sweep_recorded") is False, "B3 overclaims scaled tolerance sweep")
    checks.check(b3.get("eta_h_O_h7_solver_policy_evidence") is False, "B3 overclaims eta_h proof")

    checks.check(manifest.get("proof_solver_scale_audit") == "PROOF_SOLVER_SCALE_AUDIT.md", "manifest solver audit path missing")
    checks.check(manifest.get("proof_solver_scale_audit_json") == "PROOF_SOLVER_SCALE_AUDIT.json", "manifest solver audit JSON path missing")
    checks.check("PROOF_SOLVER_SCALE_AUDIT.md" in manifest.get("evidence_anchors", []), "manifest solver audit anchor missing")
    checks.check("PROOF_SOLVER_SCALE_AUDIT.json" in manifest.get("evidence_anchors", []), "manifest solver audit JSON anchor missing")
    checks.check(
        "PROOF_SOLVER_SCALED_TOLERANCE_PROBE.md" in manifest.get("evidence_anchors", []),
        "manifest scaled-tolerance probe MD anchor missing",
    )
    checks.check(
        "PROOF_SOLVER_SCALED_TOLERANCE_PROBE.json" in manifest.get("evidence_anchors", []),
        "manifest scaled-tolerance probe JSON anchor missing",
    )
    checks.check(
        "PROOF_SOLVER_SCALED_TOLERANCE_PROBE.csv" in manifest.get("evidence_anchors", []),
        "manifest scaled-tolerance probe CSV anchor missing",
    )
    checks.check(
        "PROOF_SOLVER_SCALED_TOLERANCE_TRAJECTORY_PROBE.md" in manifest.get("evidence_anchors", []),
        "manifest scaled-tolerance trajectory probe MD anchor missing",
    )
    checks.check(
        "PROOF_SOLVER_SCALED_TOLERANCE_TRAJECTORY_PROBE.json" in manifest.get("evidence_anchors", []),
        "manifest scaled-tolerance trajectory probe JSON anchor missing",
    )
    checks.check(
        "PROOF_SOLVER_SCALED_TOLERANCE_TRAJECTORY_PROBE.csv" in manifest.get("evidence_anchors", []),
        "manifest scaled-tolerance trajectory probe CSV anchor missing",
    )
    checks.check(
        "PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.md" in manifest.get("evidence_anchors", []),
        "manifest tolerance-regime sweep MD anchor missing",
    )
    checks.check(
        "PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.json" in manifest.get("evidence_anchors", []),
        "manifest tolerance-regime sweep JSON anchor missing",
    )
    checks.check(
        "PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.csv" in manifest.get("evidence_anchors", []),
        "manifest tolerance-regime sweep CSV anchor missing",
    )
    checks.check("validate_proof_solver_scale_audit.py" in manifest.get("validators", []), "manifest solver audit validator missing")
    checks.check(
        "validate_proof_solver_scaled_tolerance_probe.py" in manifest.get("validators", []),
        "manifest scaled-tolerance probe validator missing",
    )
    checks.check(
        "validate_proof_solver_scaled_tolerance_trajectory_probe.py" in manifest.get("validators", []),
        "manifest scaled-tolerance trajectory probe validator missing",
    )
    checks.check(
        "validate_proof_solver_tolerance_regime_sweep.py" in manifest.get("validators", []),
        "manifest tolerance-regime sweep validator missing",
    )
    checks.check(manifest.get("submission_ready") is False, "manifest overclaims submission")

    finite_probe = audit.get("finite_scaled_tolerance_probe", {})
    checks.check(
        finite_probe.get("schema") == "proof-solver-scaled-tolerance-probe-v1",
        "finite scaled-tolerance probe schema missing",
    )
    checks.check(
        finite_probe.get("source_json") == "PROOF_SOLVER_SCALED_TOLERANCE_PROBE.json",
        "finite probe JSON source missing",
    )
    checks.check(finite_probe.get("row_count") == 4, "finite probe row count changed")
    checks.check(finite_probe.get("ok_row_count") == 4, "finite probe ok count changed")
    checks.check(finite_probe.get("scaled_policy_exercised") is True, "finite probe policy marker changed")
    checks.check(
        finite_probe.get("theorem_level_solver_proof_closed") is False,
        "finite probe overclaims theorem-level proof closure",
    )
    checks.check(
        float(finite_probe.get("max_final_residual_over_h7", math.inf)) < 1.0e4,
        "finite probe residual/h7 exceeds c_eta",
    )

    trajectory_probe = audit.get("finite_scaled_tolerance_trajectory_probe", {})
    checks.check(
        trajectory_probe.get("schema") == "proof-solver-scaled-tolerance-trajectory-probe-v1",
        "finite scaled-tolerance trajectory probe schema missing",
    )
    checks.check(
        trajectory_probe.get("source_json") == "PROOF_SOLVER_SCALED_TOLERANCE_TRAJECTORY_PROBE.json",
        "finite trajectory probe JSON source missing",
    )
    checks.check(
        trajectory_probe.get("source_csv") == "PROOF_SOLVER_SCALED_TOLERANCE_TRAJECTORY_PROBE.csv",
        "finite trajectory probe CSV source missing",
    )
    checks.check(trajectory_probe.get("row_count") == 4, "finite trajectory probe row count changed")
    checks.check(trajectory_probe.get("ok_row_count") == 4, "finite trajectory probe ok count changed")
    checks.check(trajectory_probe.get("total_steps_checked") == 30, "finite trajectory probe step count changed")
    checks.check(
        trajectory_probe.get("scaled_trajectory_policy_exercised") is True,
        "finite trajectory probe policy marker changed",
    )
    checks.check(
        trajectory_probe.get("theorem_level_solver_proof_closed") is False,
        "finite trajectory probe overclaims theorem-level proof closure",
    )
    checks.check(
        trajectory_probe.get("eta_h_O_h7_solver_policy_evidence") is False,
        "finite trajectory probe overclaims eta_h proof evidence",
    )
    checks.check(
        float(trajectory_probe.get("max_final_residual_over_h7", math.inf)) < 1.0e4,
        "finite trajectory probe residual/h7 exceeds c_eta",
    )

    regime_sweep = audit.get("finite_tolerance_regime_sweep", {})
    checks.check(
        regime_sweep.get("schema") == "proof-solver-tolerance-regime-sweep-v1",
        "finite tolerance-regime sweep schema missing",
    )
    checks.check(
        regime_sweep.get("source_json") == "PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.json",
        "finite tolerance-regime sweep JSON source missing",
    )
    checks.check(
        regime_sweep.get("source_csv") == "PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.csv",
        "finite tolerance-regime sweep CSV source missing",
    )
    checks.check(regime_sweep.get("policy_count") == 3, "finite tolerance-regime policy count changed")
    checks.check(regime_sweep.get("total_rows_checked") == 12, "finite tolerance-regime row count changed")
    checks.check(regime_sweep.get("total_steps_checked") == 90, "finite tolerance-regime step count changed")
    checks.check(regime_sweep.get("all_rows_converged") is True, "finite tolerance-regime convergence changed")
    checks.check(
        regime_sweep.get("finite_tolerance_regime_sweep_recorded") is True,
        "finite tolerance-regime sweep marker changed",
    )
    checks.check(
        regime_sweep.get("finite_h_scaled_tolerance_sweep_recorded") is True,
        "finite h-scaled tolerance-regime sweep marker changed",
    )
    checks.check(
        regime_sweep.get("finite_h_scaled_policy_names") == ["scaled_h7_c1e4", "scaled_h8_c1e6"],
        "finite h-scaled policy names changed",
    )
    checks.check(regime_sweep.get("finite_h_scaled_policy_rows") == 8, "finite h-scaled row count changed")
    checks.check(regime_sweep.get("finite_h_scaled_policy_steps") == 60, "finite h-scaled step count changed")
    checks.check(
        float(regime_sweep.get("finite_h_scaled_position_order_floor", math.nan)) > 6.0,
        "finite h-scaled position order floor too small",
    )
    checks.check(
        float(regime_sweep.get("finite_h_scaled_velocity_order_floor", math.nan)) > 6.0,
        "finite h-scaled velocity order floor too small",
    )
    checks.check(
        regime_sweep.get("scaled_h7_residual_bound_satisfied") is True,
        "h7 residual bound marker changed",
    )
    checks.check(
        regime_sweep.get("scaled_h8_residual_bound_satisfied") is True,
        "h8 residual bound marker changed",
    )
    checks.check(
        regime_sweep.get("scaled_tolerance_sweep_recorded") is False,
        "finite tolerance-regime sweep overclaims scaled sweep",
    )
    checks.check(
        regime_sweep.get("theorem_level_solver_proof_closed") is False,
        "finite tolerance-regime sweep overclaims theorem closure",
    )
    checks.check(
        regime_sweep.get("eta_h_O_h7_solver_policy_evidence") is False,
        "finite tolerance-regime sweep overclaims eta-h proof",
    )
    checks.check(
        close_list([6.946347411176867, 6.608089993735075], regime_sweep.get("fixed_1e_10_position_velocity_orders")),
        "fixed tolerance regime orders changed",
    )
    checks.check(
        close_list([6.946347411176867, 6.608089993735075], regime_sweep.get("scaled_h7_position_velocity_orders")),
        "h7 tolerance regime orders changed",
    )
    checks.check(
        close_list([6.946365976765468, 6.608137477881583], regime_sweep.get("scaled_h8_position_velocity_orders")),
        "h8 tolerance regime orders changed",
    )

    require_tokens(
        checks,
        audit_md,
        [
            "Proof Solver Scale Audit",
            "SUMMARY-LEVEL SOLVER RESIDUALS RECORDED - NOT A SCALED ETA_H PROOF",
            "does not invoke `run_v047.py`",
            "default `1e-4` campaign",
            "Here `submission_ready=false` is scoped to the solver-scale/global `eta_h` proof boundary,",
            "not to the separate narrowed-claim package decision.",
            "2.800513564816292e-13",
            "3.663986665284353e-12",
            "3584.657362964853",
            "eta_h_O_h7_solver_policy_evidence=false",
            "finite scaled-tolerance probe",
            "PROOF_SOLVER_SCALED_TOLERANCE_PROBE.json",
            "127.58372278641149",
            "finite scaled-tolerance trajectory probe",
            "PROOF_SOLVER_SCALED_TOLERANCE_TRAJECTORY_PROBE.json",
            "210.89078604575462",
            "finite tolerance-regime sweep",
            "PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.json",
            "fixed `1e-10`, `c h^7`, and `c h^8`",
            "finite_tolerance_regime_sweep_recorded=true",
            "finite_h_scaled_tolerance_sweep_recorded=true",
            "fixed_tolerance_window_comparison_only=true",
            "fixed_tolerance_does_not_instantiate_P6=true",
            "finite-window tolerance comparison only",
            "does not instantiate P6",
            "theorem-level scaled tolerance sweep",
            "finite_scaled_tolerance_trajectory_probe_recorded=true",
            "finite_tolerance_regime_sweep_recorded=true",
            "finite_h_scaled_tolerance_sweep_recorded=true",
            "submission_ready_scope=solver_scale_global_eta_h_boundary_not_narrowed_claim_package_decision",
            "solver_scale_audit_scope=finite_solver_scale_diagnostic_and_theorem_level_eta_h_boundary",
            "narrowed_claim_b4_b6_b7_statuses=closed/closed/closed",
            "global_submission_boundaries_retained=full_source_policy_package_ready,theorem_level_eta_h_solver_policy_evidence,closed_residual_to_error_theorem_for_mechanism_rows",
            "theorem_level_scaled_tolerance_sweep_recorded=false",
            "Remaining Gate Scope",
            "finite_solver_scale_diagnostic_recorded=true",
            "eta_h_theorem_condition_retained=true",
            "stage_residual_O_h7_implementation_defect_proved_by_this_audit=false",
            "remaining_gate_global_submission_boundaries_retained=full_source_policy_package_ready,theorem_level_eta_h_solver_policy_evidence,closed_residual_to_error_theorem_for_mechanism_rows",
            "default_1e-4_required=false",
            "run_v047_invoked=false",
            "validate_proof_solver_scale_audit.py",
            "validate_proof_solver_scaled_tolerance_trajectory_probe.py",
            "validate_proof_solver_tolerance_regime_sweep.py",
        ],
        "PROOF_SOLVER_SCALE_AUDIT.md",
    )
    for text, label in [(main_tex, "main"), (flat_tex, "flat")]:
        checks.check(
            not contains_normalized(text, "fixed tolerance is adequate"),
            f"{label} manuscript still uses fixed-tolerance adequacy wording",
        )
        require_tokens(
            checks,
            text,
            [
                "finite-window tolerance comparison only",
                "not P6 instantiation or a theorem-level solver-policy proof",
            ],
            f"{label} manuscript",
        )

    forbidden = set(audit.get("forbidden_claims", []))
    for token in [
        "eta_h_O_h7_solver_policy_evidence_true",
        "fixed_tolerance_runs_are_asymptotic_proof_true",
        "scaled_tolerance_sweep_recorded_true",
        "stage_residual_O_h7_implementation_defect_proved_by_this_audit_true",
        "dynamic_symbolic_oracle_complete_true",
        "external_superiority_claim_true",
        "default_1e-4_required_true",
        "submission_ready_true",
    ]:
        checks.check(token in forbidden, f"forbidden claim missing: {token}")

    if checks.errors:
        print("proof_solver_scale_audit=FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("proof_solver_scale_audit=PASS")
    print("summary_level_solver_residuals_recorded=True")
    print("scaled_tolerance_sweep_recorded=False")
    print(f"smooth_projected_reference_residual={residuals['smooth_projected_reference_max_linear_residual_norm']:.6e}")
    print(f"smooth_reference_eta_over_reference_h7={smooth_ratios[-1]:.6f}")
    print("finite_scaled_tolerance_trajectory_probe_recorded=True")
    print("finite_tolerance_regime_sweep_recorded=True")
    print("finite_h_scaled_tolerance_sweep_recorded=True")
    print("eta_h_O_h7_solver_policy_evidence=False")
    print("fixed_tolerance_runs_are_asymptotic_proof=False")
    print("default_1e-4=False")
    print("run_v047_invoked=False")
    print("submission_ready=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
