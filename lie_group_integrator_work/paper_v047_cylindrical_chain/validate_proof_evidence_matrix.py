#!/usr/bin/env python3
"""Read-only check for the concise paper proof-to-evidence matrix."""

from __future__ import annotations

import json
import sys
from pathlib import Path


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
PIPELINE = ROOT / "v047_cylindrical_chain_pipeline"
RESULTS = PIPELINE / "results"
V048_RESULTS = ROOT / "v048_cross_paper_same_test_benchmarks" / "results"

EXPECTED_EXAMPLES = {"single_pendulum", "double_pendulum", "four_link", "slider_crank"}
EXPECTED_CAVEATS = {
    "sparse_speed_quantified",
    "full_tfe_stage_replacement_missing",
    "sharp_friction_coarse_order_reduction_ultra_recovered",
}


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_json(path: Path) -> dict:
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


def main() -> int:
    checks = Checks()
    try:
        matrix = read_text(PAPER / "PROOF_EVIDENCE_MATRIX.md")
        order_gate = read_json(PAPER / "ORDER_ACCEPTANCE_GATE.json")
        order_gate_md = read_text(PAPER / "ORDER_ACCEPTANCE_GATE.md")
        numerical_scale_audit = read_json(PAPER / "PROOF_NUMERICAL_SCALE_AUDIT.json")
        solver_scale_audit = read_json(PAPER / "PROOF_SOLVER_SCALE_AUDIT.json")
        implementation_certificate = read_text(PAPER / "IMPLEMENTATION_FIDELITY_CERTIFICATE.md")
        dynamic_oracle = read_text(PAPER / "DYNAMIC_ROW_ORACLE_GATE.md")
        newton_euler_obligation = read_json(PAPER / "NEWTON_EULER_DEFECT_OBLIGATION_GATE.json")
        newton_euler_obligation_md = read_text(PAPER / "NEWTON_EULER_DEFECT_OBLIGATION_GATE.md")
        newton_euler_virtual_work = read_json(PAPER / "NEWTON_EULER_VIRTUAL_WORK_WRENCH_AUDIT.json")
        newton_euler_symbolic = read_json(PAPER / "NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.json")
        local_candidate = read_json(V048_RESULTS / "closed_loop_true_dynamic_newton_coarse_order.json")
        residual_to_error = read_json(
            V048_RESULTS / "closed_loop_residual_to_error_theorem_obligations.json"
        )
        boundary = read_json(PAPER / "CLAIM_BOUNDARY.json")
        manifest = read_json(PAPER / "SUBMISSION_ARTIFACT_MANIFEST.json")
        summary = read_json(RESULTS / "summary_v047.json")
    except Exception as exc:  # noqa: BLE001 - concise CLI failure.
        print(f"v047 proof evidence matrix validation: FAIL\n- {exc}")
        return 1

    primary = boundary.get("primary_claim", {})
    comparator = boundary.get("comparator", {})
    summary_asme = summary.get("asme_gate", {})
    gate_probe = order_gate.get("v048_external_dynamic_order_probe", {})
    local_candidate_gate = order_gate.get("local_closed_loop_dynamic_order_candidates", {})
    numerical_scale_boundary = numerical_scale_audit.get("proof_boundary", {})
    solver_scale_boundary = solver_scale_audit.get("proof_boundary", {})

    checks.check(primary.get("accepted_method") == "Gauss6/FullVA", "accepted method changed")
    checks.check(primary.get("method_order_claim") == 6, "method order claim changed")
    checks.check(primary.get("smooth_projected_orders", {}).get("position") == 7.161, "smooth position order changed")
    checks.check(primary.get("smooth_projected_orders", {}).get("velocity") == 7.066, "smooth velocity order changed")
    checks.check(comparator.get("expected_order") == 5, "comparator order changed")
    checks.check(boundary.get("full_tfe_stage_replacement") is False, "full-TFE marker changed")
    checks.check(set(primary.get("accepted_examples", [])) == EXPECTED_EXAMPLES, "boundary example set changed")
    checks.check(set(summary_asme.get("models", {})) == EXPECTED_EXAMPLES, "summary example set changed")
    checks.check(set(boundary.get("open_caveats", [])) == EXPECTED_CAVEATS, "caveat set changed")
    checks.check(
        boundary.get("evidence_files", {}).get("proof_evidence_matrix")
        == "paper_v047_cylindrical_chain/PROOF_EVIDENCE_MATRIX.md",
        "claim boundary missing proof evidence matrix path",
    )
    checks.check("PROOF_EVIDENCE_MATRIX.md" in manifest.get("evidence_anchors", []), "manifest missing proof matrix anchor")
    checks.check(
        "PROOF_NUMERICAL_SCALE_AUDIT.md" in manifest.get("evidence_anchors", []),
        "manifest missing proof numerical scale audit anchor",
    )
    checks.check(
        "PROOF_NUMERICAL_SCALE_AUDIT.json" in manifest.get("evidence_anchors", []),
        "manifest missing proof numerical scale audit JSON anchor",
    )
    checks.check(
        "validate_proof_numerical_scale_audit.py" in manifest.get("validators", []),
        "manifest missing proof numerical scale audit validator",
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
        "validate_proof_solver_scale_audit.py" in manifest.get("validators", []),
        "manifest missing proof solver scale audit validator",
    )
    checks.check("ORDER_ACCEPTANCE_GATE.md" in manifest.get("evidence_anchors", []), "manifest missing order gate anchor")
    checks.check("ORDER_ACCEPTANCE_GATE.json" in manifest.get("evidence_anchors", []), "manifest missing order gate JSON anchor")
    checks.check("validate_proof_evidence_matrix.py" in manifest.get("validators", []), "manifest missing proof matrix validator")
    checks.check("validate_order_acceptance_gate.py" in manifest.get("validators", []), "manifest missing order gate validator")
    checks.check(
        "IMPLEMENTATION_FIDELITY_CERTIFICATE.md" in manifest.get("evidence_anchors", []),
        "manifest missing implementation-fidelity certificate anchor",
    )
    checks.check(
        "validate_implementation_fidelity_certificate.py" in manifest.get("validators", []),
        "manifest missing implementation-fidelity validator",
    )
    checks.check("DYNAMIC_ROW_ORACLE_GATE.md" in manifest.get("evidence_anchors", []), "manifest missing dynamic row oracle anchor")
    checks.check("DYNAMIC_ROW_ORACLE_GATE.json" in manifest.get("evidence_anchors", []), "manifest missing dynamic row oracle JSON anchor")
    checks.check("validate_dynamic_row_oracle_gate.py" in manifest.get("validators", []), "manifest missing dynamic row oracle validator")
    checks.check(
        "D5_P_ACC_PA2_WEIGHTED_INVERSE_AUDIT.md" in manifest.get("evidence_anchors", []),
        "manifest missing P_acc PA2 weighted-inverse audit anchor",
    )
    checks.check(
        "D5_P_ACC_PA2_WEIGHTED_INVERSE_AUDIT.json" in manifest.get("evidence_anchors", []),
        "manifest missing P_acc PA2 weighted-inverse JSON anchor",
    )
    checks.check(
        "validate_d5_p_acc_pa2_weighted_inverse_audit.py" in manifest.get("validators", []),
        "manifest missing P_acc PA2 weighted-inverse validator",
    )
    checks.check(
        "D5_P_LAMBDA_PL2_GEOMETRIC_MARGIN_AUDIT.md" in manifest.get("evidence_anchors", []),
        "manifest missing P_lambda PL2 geometric-margin audit anchor",
    )
    checks.check(
        "D5_P_LAMBDA_PL2_GEOMETRIC_MARGIN_AUDIT.json" in manifest.get("evidence_anchors", []),
        "manifest missing P_lambda PL2 geometric-margin JSON anchor",
    )
    checks.check(
        "validate_d5_p_lambda_pl2_geometric_margin_audit.py" in manifest.get("validators", []),
        "manifest missing P_lambda PL2 geometric-margin validator",
    )
    checks.check(
        "NEWTON_EULER_DEFECT_OBLIGATION_GATE.md" in manifest.get("evidence_anchors", []),
        "manifest missing Newton-Euler obligation gate anchor",
    )
    checks.check(
        "NEWTON_EULER_DEFECT_OBLIGATION_GATE.json" in manifest.get("evidence_anchors", []),
        "manifest missing Newton-Euler obligation gate JSON anchor",
    )
    checks.check(
        "validate_newton_euler_defect_obligation_gate.py" in manifest.get("validators", []),
        "manifest missing Newton-Euler obligation gate validator",
    )
    checks.check(
        "NEWTON_EULER_VIRTUAL_WORK_WRENCH_AUDIT.md" in manifest.get("evidence_anchors", []),
        "manifest missing Newton-Euler virtual-work wrench audit anchor",
    )
    checks.check(
        "NEWTON_EULER_VIRTUAL_WORK_WRENCH_AUDIT.json" in manifest.get("evidence_anchors", []),
        "manifest missing Newton-Euler virtual-work wrench audit JSON anchor",
    )
    checks.check(
        "validate_newton_euler_virtual_work_wrench_audit.py" in manifest.get("validators", []),
        "manifest missing Newton-Euler virtual-work wrench audit validator",
    )
    checks.check(
        "NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.md" in manifest.get("evidence_anchors", []),
        "manifest missing Newton-Euler symbolic certificate anchor",
    )
    checks.check(
        "NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.json" in manifest.get("evidence_anchors", []),
        "manifest missing Newton-Euler symbolic certificate JSON anchor",
    )
    checks.check(
        "validate_newton_euler_symbolic_defect_certificate.py" in manifest.get("validators", []),
        "manifest missing Newton-Euler symbolic certificate validator",
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
        newton_euler_obligation.get("closure_state", {}).get("stage_residual_O_h7_implementation_defect_proved") is False,
        "Newton-Euler obligation overclaims O(h^7)",
    )
    newton_symbolic_summary = newton_euler_symbolic.get("summary", {})
    checks.check(newton_symbolic_summary.get("body_specific_wrench_expansion_checked") is True, "body-specific wrench expansion marker missing")
    checks.check(newton_symbolic_summary.get("body_specific_wrench_expansion_checked_rows") == 36, "body-specific wrench row count changed")
    checks.check(newton_symbolic_summary.get("body0_wrench_expansion_rows") == 18, "body0 wrench rows changed")
    checks.check(newton_symbolic_summary.get("body1_wrench_expansion_rows") == 18, "body1 wrench rows changed")
    checks.check(
        newton_euler_virtual_work.get("summary", {}).get("checked_rows") == 36,
        "virtual-work audit checked rows changed",
    )
    checks.check(
        newton_euler_virtual_work.get("template_virtual_work_identity_proved") is True,
        "virtual-work template identity not proved",
    )
    checks.check(
        newton_euler_virtual_work.get("summary", {}).get("template_virtual_work_identity_rows") == 36,
        "virtual-work template identity rows changed",
    )
    checks.check(
        newton_euler_virtual_work.get("row_expanded_virtual_work_identity_proved") is True,
        "virtual-work audit row-expanded identity not proved",
    )
    checks.check(
        newton_euler_virtual_work.get("summary", {}).get("row_expanded_virtual_work_identity_rows") == 36,
        "virtual-work audit row-expanded identity rows changed",
    )
    checks.check(
        newton_euler_virtual_work.get("multiplier_wrench_consistency_closed") is True,
        "virtual-work audit did not close multiplier consistency",
    )
    checks.check(
        newton_symbolic_summary.get("virtual_work_wrench_sign_skeleton_checked_rows") == 36,
        "symbolic certificate virtual-work rows changed",
    )
    checks.check(
        newton_symbolic_summary.get("virtual_work_template_identity_rows") == 36,
        "symbolic certificate virtual-work template rows changed",
    )
    checks.check(newton_symbolic_summary.get("c2_runtime_equivalence_closed") is True, "symbolic certificate lost D6 runtime-equivalence closure")
    checks.check(
        newton_euler_symbolic.get("stage_residual_O_h7_implementation_defect_proved") is False,
        "symbolic certificate overclaims dynamic O(h^7)",
    )
    checks.check(order_gate.get("schema") == "v047-order-acceptance-gate-v1", "order gate schema changed")
    checks.check(order_gate.get("accepted_method", {}).get("method_order_claim") == 6, "order gate method order changed")
    checks.check(order_gate.get("comparator", {}).get("expected_order") == 5, "order gate comparator order changed")
    checks.check(
        set(order_gate.get("accepted_dynamic_order_examples", [])) == {"single_pendulum", "double_pendulum"},
        "order gate accepted dynamic-order examples changed",
    )
    checks.check(
        set(order_gate.get("coverage_only_examples", [])) == {"four_link", "slider_crank"},
        "order gate coverage-only examples changed",
    )
    checks.check(gate_probe.get("accepted_dynamic_order_count") == 0, "closed-loop dynamic order unexpectedly accepted")
    checks.check(gate_probe.get("external_superiority_claim") is False, "external superiority unexpectedly accepted")
    checks.check(
        local_candidate_gate.get("schema") == local_candidate.get("schema") == "closed-loop-true-dynamic-newton-coarse-order-v1",
        "local closed-loop dynamic candidate schema changed",
    )
    checks.check(local_candidate_gate.get("row_count") == local_candidate.get("row_count") == 6, "local candidate row count changed")
    checks.check(local_candidate_gate.get("ok_row_count") == local_candidate.get("ok_row_count") == 6, "local candidate ok row count changed")
    checks.check(
        local_candidate_gate.get("accepted_local_dynamic_order_candidate_count")
        == local_candidate.get("accepted_dynamic_order_count")
        == 2,
        "local candidate accepted count changed",
    )
    checks.check(local_candidate_gate.get("step_sizes") == [0.1, 0.05, 0.025], "local candidate step sizes changed")
    checks.check(local_candidate_gate.get("reference_h") == 0.0125, "local candidate reference h changed")
    checks.check(local_candidate_gate.get("stage_oracle_used") is False, "local candidate unexpectedly used stage oracle")
    checks.check(local_candidate_gate.get("default_1e-4_required") is False, "local candidate incorrectly requires default 1e-4")
    checks.check(local_candidate_gate.get("heavy_numerical_run_invoked") is False, "local candidate invoked heavy numerical run")
    checks.check(local_candidate_gate.get("external_superiority_claim") is False, "local candidate overclaims external superiority")
    checks.check(residual_to_error.get("obligation_count") == 7, "residual-to-error obligation count changed")
    checks.check(residual_to_error.get("blocking_obligation_count") == 7, "residual-to-error blocking count changed")
    checks.check(
        residual_to_error.get("accepted_residual_to_error_theorem") is False,
        "residual-to-error theorem unexpectedly accepted",
    )
    checks.check(residual_to_error.get("accepted_dynamic_order_count") == 0, "residual-to-error route accepted dynamic order")
    checks.check(numerical_scale_audit.get("schema") == "proof-numerical-scale-audit-v1", "numerical scale audit schema changed")
    checks.check(
        numerical_scale_audit.get("status") == "finite_run_global_scale_diagnostic_not_asymptotic_solver_proof",
        "numerical scale audit status changed",
    )
    checks.check(
        numerical_scale_boundary.get("finite_run_error_scale_supports_order_six") is True,
        "numerical scale audit lost order-six marker",
    )
    checks.check(
        numerical_scale_boundary.get("endpoint_global_closure_scale_supports_local_h7_budget") is True,
        "numerical scale audit lost endpoint budget marker",
    )
    checks.check(
        numerical_scale_boundary.get("endpoint_functional_is_velocity_kkt_not_raw_position_monitor") is True,
        "numerical scale audit lost endpoint functional versus raw monitor boundary",
    )
    checks.check(
        numerical_scale_boundary.get("raw_position_endpoint_defect_is_diagnostic_monitor") is True,
        "numerical scale audit lost raw endpoint position diagnostic-monitor boundary",
    )
    checks.check(
        numerical_scale_boundary.get("finite_endpoint_diagnostics_do_not_discharge_endpoint_p2") is True,
        "numerical scale audit lost P2 endpoint-hypothesis boundary",
    )
    checks.check(
        numerical_scale_boundary.get("eta_h_O_h7_solver_policy_evidence") is False,
        "numerical scale audit overclaims solver-policy proof",
    )
    checks.check(
        numerical_scale_boundary.get("stage_residual_O_h7_implementation_defect_proved_by_this_audit") is False,
        "numerical scale audit overclaims implementation-defect proof by h-sweep evidence",
    )
    checks.check(solver_scale_audit.get("schema") == "proof-solver-scale-audit-v1", "solver scale audit schema changed")
    checks.check(
        solver_scale_audit.get("status") == "summary_level_solver_residuals_recorded_not_scaled_eta_h_proof",
        "solver scale audit status changed",
    )
    checks.check(
        solver_scale_boundary.get("summary_level_solver_residuals_recorded") is True,
        "solver scale audit lost residual-record marker",
    )
    checks.check(
        solver_scale_boundary.get("scaled_tolerance_sweep_recorded") is False,
        "solver scale audit overclaims scaled tolerance sweep",
    )
    checks.check(
        solver_scale_boundary.get("eta_h_O_h7_solver_policy_evidence") is False,
        "solver scale audit overclaims solver-policy proof",
    )

    required_tokens = [
        "Proof Evidence Matrix",
        "conditional order-comparison proposition",
        "`Gauss6/FullVA`",
        "method-order claim is `6`",
        "Smooth observed position/velocity orders are `7.161/7.066`",
        "local paper-style `m=3` Gauss-Lobatto TFE formula target",
        "expected order `5`",
        "`single_pendulum`",
        "`double_pendulum`",
        "`four_link`",
        "`slider_crank`",
        "`full_tfe_stage_replacement=false`",
        "One-way evidence rule",
        "downstream checks of a theorem instance",
        "none is allowed to back-propagate into the theorem interface",
        "observed order slopes do not close P1/P2 compact-tube hypotheses",
        "finite residuals do not close the P6 solver-policy condition",
        "residual tables do not close the P7 residual-to-error boundary",
        "common-reference wins do not create source-policy or external-superiority claims",
        "direct 96+36 residual bridge on the selected Gauss-predictor branch",
        "Define the accepted one-step map",
        "Support sixth-order smooth behavior",
        "PROOF_NUMERICAL_SCALE_AUDIT.md/json",
        "finite-run global fits `7.160828/7.066183`",
        "finite-run scale diagnostic",
        "PROOF_SOLVER_SCALE_AUDIT.md/json",
        "summary-level solver residuals",
        "smooth reference `max_linear_residual_norm=2.800513564816292e-13`",
        "`3584.657362964853`",
        "theorem_level_scaled_tolerance_sweep_recorded=false",
        "`h=[0.04,0.02,0.01]`",
        "`reference_h=0.005`",
        "raw endpoint monitor global fits `5.985101/6.072291`",
        "velocity-level/KKT closure subsystem",
        "raw position endpoint defect is a separate monitor",
        "not P2 endpoint closure proof",
        "finite rows do not discharge P2 endpoint closure proof",
        "newton_residual_norm_recorded=false",
        "eta_h_O_h7_solver_policy_evidence=false",
        "Separate comparator order from implemented residual",
        "`2m-1=5`",
        "State conditional order exceedance",
        "one-step `O(h^7)` perturbation is no longer assumed as a shortcut",
        "decomposed into proof obligations",
        "noncircular",
        "Proposition [Conditional order comparison]",
        "higher formal order",
        "Verify four-example support",
        "Preserve non-claims",
        "Keep full-TFE replacement open",
        "IMPLEMENTATION_FIDELITY_CERTIFICATE.md",
        "DYNAMIC_ROW_ORACLE_GATE.md",
        "validate_implementation_fidelity_certificate.py",
        "validate_dynamic_row_oracle_gate.py",
        "runtime row-layout and block-functional check",
        "R_INDEPENDENT_STAGE_FUNCTIONAL_BLOCKS",
        "partial independent formula-row oracle",
        "96 non-dynamic rows",
        "full independent formula-row oracle",
        "132 runtime formula rows",
        "multi-probe formula-row AD Jacobian oracle",
        "three deterministic probes",
        "R_JAC",
        "newton_euler_weak_balance",
        "NEWTON_EULER_DEFECT_OBLIGATION_GATE.md/json",
        "NEWTON_EULER_BALANCE_IDENTITY_AUDIT.md/json",
        "NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.md/json",
        "NEWTON_EULER_VIRTUAL_WORK_WRENCH_AUDIT.md/json",
        "D1/D2/D3/D4/D6",
        "body-specific proximal/distal force and torque sign expansions",
        "virtual-work sign-skeleton traceability",
        "template virtual-work identity",
        "row-expanded multiplier-wrench identity accepted",
        "all 36 dynamic rows",
        "body0/body1 coverage `18/18`",
        "body-specific wrench-expansion traceability",
        "translational balance",
        "rotational balance",
        "D5_P_ACC_PA2_WEIGHTED_INVERSE_AUDIT.md/json",
        "bounded finite control of `h delta A`",
        "uniform unweighted acceleration lift",
        "D5_P_LAMBDA_PL2_GEOMETRIC_MARGIN_AUDIT.md/json",
        "PL2 geometric-margin route",
        "compact-tube transversality margin",
        "D5 dynamic symbolic defect proof remains open",
        "complete source-paper TFE residual implementation",
        "ORDER_ACCEPTANCE_GATE.md",
        "validate_order_acceptance_gate.py",
        "Example-level order boundary",
        "not accepted external dynamic order",
        "closed-loop coarse-dynamics diagnostics",
        "`closed_loop_true_dynamic_newton_coarse_order.json`",
        "`6/6` ok rows",
        "closed-loop coarse-dynamics diagnostic examples `2`",
        "`5.955/5.955/6.085/5.971`",
        "`6.164/6.159/7.341/6.426`",
        "`default_1e-4_required=false`",
        "`heavy_numerical_run_invoked=false`",
        "`external_superiority_claim=false`",
        "Block unsupported residual-to-error promotion",
        "closed_loop_residual_to_error_theorem_obligations",
        "seven blocking obligations",
        "accepted_residual_to_error_theorem=false",
    ]
    for token in required_tokens:
        checks.check(contains_normalized(matrix, token), f"PROOF_EVIDENCE_MATRIX.md missing token: {token}")

    gate_tokens = [
        "Order Acceptance Gate",
        "Method-order claim: `6`",
        "Comparator expected order: `2m-1=5`",
        "`not_accepted_dynamic_order`",
        "Local Closed-Loop Coarse-Dynamics Candidate Evidence",
        "closed-loop coarse-dynamics diagnostic examples: `2`",
        "primary-state orders for `four_link`: `5.955/5.955/6.085/5.971`",
        "primary-state orders for `slider_crank`: `6.164/6.159/7.341/6.426`",
        "accepted external dynamic-order rows: `0`",
        "`coarse_first_no_default_1e-4`",
        "Strict public-policy `1e-4` rows are opt-in only",
    ]
    for token in gate_tokens:
        checks.check(contains_normalized(order_gate_md, token), f"ORDER_ACCEPTANCE_GATE.md missing token: {token}")

    certificate_tokens = [
        "Implementation Fidelity Certificate",
        "residual_cylindrical_chain",
        "R_JAC = jax.jit(jax.jacfwd(residual_cylindrical_chain, argnums=0))",
        "STAGE_FUNCTIONAL_BLOCK_LAYOUT",
        "DIM = N_STAGES * STAGE_SIZE = 132",
        "static source-identity audit",
        "partial independent formula-row oracle",
        "96 non-dynamic rows",
        "full independent formula-row oracle",
        "132 runtime formula rows",
        "multi-probe formula-row AD Jacobian oracle",
        "three deterministic probes",
        "newton_euler_weak_balance",
        "not a dynamic symbolic-equivalence proof",
        "DYNAMIC_ROW_ORACLE_GATE.md",
        "full_tfe_stage_replacement",
    ]
    for token in certificate_tokens:
        checks.check(
            contains_normalized(implementation_certificate, token),
            f"IMPLEMENTATION_FIDELITY_CERTIFICATE.md missing token: {token}",
        )

    dynamic_tokens = [
        "Dynamic Row Oracle Gate",
        "residual shape: `(132,)`",
        "Jacobian shape: `(132,132)`",
        "block-functional cross-check",
        "partial independent formula-row oracle",
        "96 non-dynamic rows",
        "full independent formula-row oracle",
        "132 runtime formula rows",
        "multi-probe formula-row AD Jacobian oracle",
        "formula_row_ad_jacobian_probe_count=3",
        "max formula-row Jacobian mismatch",
        "newton_euler_weak_balance",
        "symbolic oracle open",
        "validate_dynamic_row_oracle_gate.py",
    ]
    for token in dynamic_tokens:
        checks.check(contains_normalized(dynamic_oracle, token), f"DYNAMIC_ROW_ORACLE_GATE.md missing token: {token}")

    newton_euler_tokens = [
        "Newton-Euler Defect Obligation Gate",
        "D5 SYMBOLIC/PRIMITIVE ROUTE OPEN; ACTIVE DIRECT PC2 CLOSED - NOT SUBMISSION READY",
        "Symbolic/primitive-route open obligation count: `1`",
        "Active direct PC2 closed: `True`",
        "Active direct dynamic zero residual rows: `36`",
        "Closed obligation count: `5`",
        "translational_balance_identity",
        "rotational_balance_identity",
        "symbolic_runtime_row_equivalence",
        "symbolic_primitive_stage_residual_O_h7_certificate_complete",
    ]
    for token in newton_euler_tokens:
        checks.check(
            contains_normalized(newton_euler_obligation_md, token),
            f"NEWTON_EULER_DEFECT_OBLIGATION_GATE.md missing token: {token}",
        )

    forbidden_tokens = [
        "full_tfe_stage_replacement=true",
        "complete source-paper residual reproduction is accepted",
        "complete source-paper TFE residual implementation is accepted",
        "full-TFE replacement accepted",
    ]
    normalized = " ".join(matrix.split()).lower()
    for token in forbidden_tokens:
        checks.check(token.lower() not in normalized, f"PROOF_EVIDENCE_MATRIX.md has forbidden claim: {token}")

    if checks.errors:
        print("v047 proof evidence matrix validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("v047 proof evidence matrix validation: PASS")
    print("accepted_method=Gauss6/FullVA")
    print("accepted_method_order=6")
    print("smooth_projected_orders=7.161/7.066")
    print("comparator_expected_order=5")
    print("order_acceptance_gate=PASS")
    print("dynamic_row_oracle_gate=PASS")
    print("block_functional_crosscheck=PASS")
    print("partial_formula_row_count=96")
    print("full_formula_row_count=132")
    print("formula_row_ad_jacobian_oracle=PASS")
    print("formula_row_ad_jacobian_probe_count=3")
    print("proof_numerical_scale_audit=PASS")
    print("proof_solver_scale_audit=PASS")
    print("finite_run_error_scale_supports_order_six=True")
    print("summary_level_solver_residuals_recorded=True")
    print("scaled_tolerance_sweep_recorded=False")
    print("eta_h_O_h7_solver_policy_evidence=False")
    print("local_closed_loop_dynamic_order_candidates=2")
    print("external_dynamic_order_accepted=False")
    print("asme_models=double_pendulum,four_link,single_pendulum,slider_crank")
    print("full_tfe_stage_replacement=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
