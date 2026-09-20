#!/usr/bin/env python3
"""Read-only validation for the v047 order-acceptance gate."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
ROOT = PAPER.parent
V047_RESULTS = ROOT / "v047_cylindrical_chain_pipeline" / "results"
V048_RESULTS = ROOT / "v048_cross_paper_same_test_benchmarks" / "results"

EXPECTED_EXAMPLES = {"single_pendulum", "double_pendulum", "four_link", "slider_crank"}
EXPECTED_ORDER_EXAMPLES = {"single_pendulum", "double_pendulum"}
EXPECTED_COVERAGE_ONLY = {"four_link", "slider_crank"}
EXPECTED_LOCAL_CANDIDATE_MODELS = ["four_link", "slider_crank"]


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


def rounded(value: float) -> float:
    return round(float(value), 3)


def min_single_order(single: dict) -> float:
    return min(
        float(single["position_observed_order"]),
        float(single["velocity_observed_order"]),
        float(single["orientation_observed_order"]),
        float(single["omega_observed_order"]),
    )


def min_double_order(double: dict) -> float:
    return min(float(double["self_orientation_order"]), float(double["self_omega_order"]))


def main() -> int:
    checks = Checks()
    try:
        gate = read_json(PAPER / "ORDER_ACCEPTANCE_GATE.json")
        gate_md = read_text(PAPER / "ORDER_ACCEPTANCE_GATE.md")
        manuscript = read_text(LATEX / "main_cmame.tex")
        boundary = read_json(PAPER / "CLAIM_BOUNDARY.json")
        manifest = read_json(PAPER / "SUBMISSION_ARTIFACT_MANIFEST.json")
        proof_matrix = read_text(PAPER / "PROOF_EVIDENCE_MATRIX.md")
        fidelity = read_text(PAPER / "IMPLEMENTATION_FIDELITY_CERTIFICATE.md")
        summary_v047 = read_json(V047_RESULTS / "summary_v047.json")
        summary_v048 = read_json(V048_RESULTS / "summary_v048.json")
        local_candidate_summary = read_json(V048_RESULTS / "closed_loop_true_dynamic_newton_coarse_order.json")
    except Exception as exc:  # noqa: BLE001 - concise CLI validator.
        print(f"v047 order acceptance gate validation: FAIL\n- {exc}")
        return 1

    accepted_method = gate.get("accepted_method", {})
    comparator = gate.get("comparator", {})
    proof_contract = gate.get("proof_contract", {})
    examples = gate.get("examples", {})
    smooth_gate = gate.get("smooth_cylindrical_chain", {})
    order_interpretation = gate.get("observed_order_interpretation", {})
    probe_gate = gate.get("v048_external_dynamic_order_probe", {})
    local_candidate_gate = gate.get("local_closed_loop_dynamic_order_candidates", {})
    residual_to_error_gate = gate.get("residual_to_error_proof_route", {})
    execution_policy = gate.get("execution_policy", {})
    primary = boundary.get("primary_claim", {})
    boundary_asme = boundary.get("asme_acceptance", {})

    smooth_summary = summary_v047["convergence"]["cases"]["cylindrical_smooth"]["projected_velocity"]
    method_runs = summary_v047["asme_gate"]["method_runs"]
    single = method_runs["single_pendulum_driven_absolute_fullva"]
    double = method_runs["double_pendulum_reference_policy"]
    closed_loop = method_runs["closed_loop_kinematic_fullva"]["models"]
    reaction = method_runs["closed_loop_reaction_dynamics"]["models"]
    probe_summary = summary_v048["closed_loop_coarse_dynamic_order_probe"]
    residual_to_error_summary = read_json(
        V048_RESULTS / "closed_loop_residual_to_error_theorem_obligations.json"
    )

    checks.check(gate.get("schema") == "v047-order-acceptance-gate-v1", "gate schema changed")
    checks.check(
        gate.get("status") == "accepted_with_current_scope_external_dynamic_order_open",
        "gate status changed",
    )
    checks.check(accepted_method.get("name") == "Gauss6/FullVA", "accepted method changed")
    checks.check(accepted_method.get("method_order_claim") == 6, "method order claim changed")
    checks.check(accepted_method.get("local_defect_order") == 7, "local defect order changed")
    checks.check(accepted_method.get("global_error_order") == 6, "global error order changed")
    checks.check(primary.get("accepted_method") == "Gauss6/FullVA", "claim boundary method changed")
    checks.check(primary.get("method_order_claim") == 6, "claim boundary order changed")
    checks.check(comparator.get("expected_order") == 5, "comparator expected order changed")
    checks.check(boundary.get("comparator", {}).get("expected_order") == 5, "claim boundary comparator changed")
    checks.check(proof_contract.get("regular_smooth_fullva_lift_required") is True, "smooth-lift proof flag changed")
    checks.check(
        proof_contract.get("stage_jacobian_uniformly_invertible_required") is True,
        "stage Jacobian proof flag changed",
    )
    checks.check(proof_contract.get("implemented_residual_defect_required") == "O(h^7)", "residual defect changed")
    checks.check(proof_contract.get("dynamic_symbolic_oracle_complete") is False, "dynamic oracle flag changed")

    checks.check(smooth_gate.get("h_values") == [0.04, 0.02, 0.01], "smooth h values changed")
    checks.check(smooth_gate.get("reference_h") == 0.005, "smooth reference h changed")
    checks.check(rounded(smooth_summary["position_order"]) == smooth_gate.get("position_order"), "smooth position order mismatch")
    checks.check(rounded(smooth_summary["velocity_order"]) == smooth_gate.get("velocity_order"), "smooth velocity order mismatch")
    checks.check(smooth_gate.get("position_order") == 7.161, "gate smooth position order changed")
    checks.check(smooth_gate.get("velocity_order") == 7.066, "gate smooth velocity order changed")
    checks.check(order_interpretation.get("smooth_slopes") == "7.161/7.066", "observed-order slopes changed")
    checks.check(order_interpretation.get("method_order_claim") == 6, "observed-order method claim changed")
    checks.check(order_interpretation.get("not_seventh_order_claim") is True, "observed-order interpretation overclaims order seven")
    checks.check(
        order_interpretation.get("interpretation")
        == "post-theorem finite-window consistency evidence for conditional sixth-order smooth behavior",
        "observed-order interpretation text changed",
    )
    checks.check(
        set(order_interpretation.get("candidate_causes", []))
        == {
            "small_leading_sixth_order_error_coefficient",
            "short_smooth_projected_endpoint_window",
            "reference_nonlinear_tolerance_and_floating_point_floor_near_finest_step",
        },
        "observed-order candidate causes changed",
    )
    checks.check(
        set(order_interpretation.get("requires_for_order_above_six", []))
        == {"wider_asymptotic_sweep", "compact_tube_eta_h_O_h7_nonlinear_tolerance"},
        "observed-order escalation requirements changed",
    )

    checks.check(set(gate.get("accepted_example_set", [])) == EXPECTED_EXAMPLES, "accepted example set changed")
    checks.check(
        set(gate.get("accepted_dynamic_order_examples", [])) == EXPECTED_ORDER_EXAMPLES,
        "accepted dynamic-order example set changed",
    )
    checks.check(set(gate.get("coverage_only_examples", [])) == EXPECTED_COVERAGE_ONLY, "coverage-only example set changed")
    checks.check(set(primary.get("accepted_examples", [])) == EXPECTED_EXAMPLES, "claim boundary examples changed")
    checks.check(
        primary.get("accepted_examples_role") == "mechanism_coverage_examples_not_all_dynamic_order",
        "claim boundary example role changed",
    )
    checks.check(
        set(primary.get("accepted_dynamic_order_examples", [])) == EXPECTED_ORDER_EXAMPLES,
        "claim boundary dynamic-order examples changed",
    )
    checks.check(
        set(primary.get("accepted_mechanism_coverage_examples", [])) == EXPECTED_EXAMPLES,
        "claim boundary mechanism-coverage examples changed",
    )
    checks.check(
        set(primary.get("coverage_only_dynamic_order_examples", [])) == EXPECTED_COVERAGE_ONLY,
        "claim boundary coverage-only dynamic-order examples changed",
    )
    checks.check(set(boundary_asme.get("accepted_examples", [])) == EXPECTED_EXAMPLES, "ASME boundary examples changed")
    checks.check(
        boundary_asme.get("accepted_examples_role") == "mechanism_coverage_examples_not_all_dynamic_order",
        "ASME boundary example role changed",
    )
    checks.check(
        set(boundary_asme.get("accepted_dynamic_order_examples", [])) == EXPECTED_ORDER_EXAMPLES,
        "ASME boundary dynamic-order examples changed",
    )
    checks.check(
        set(boundary_asme.get("accepted_mechanism_coverage_examples", [])) == EXPECTED_EXAMPLES,
        "ASME boundary mechanism-coverage examples changed",
    )
    checks.check(
        set(boundary_asme.get("coverage_only_dynamic_order_examples", [])) == EXPECTED_COVERAGE_ONLY,
        "ASME boundary coverage-only dynamic-order examples changed",
    )

    single_min = min_single_order(single)
    checks.check(single.get("status") == "ok", "single-pendulum status changed")
    checks.check(single.get("mapping_scope") == "absolute_coordinate_driven_fullva_residual", "single scope changed")
    checks.check(single_min > 6.0, "single-pendulum order is not above six")
    checks.check(rounded(single_min) == examples["single_pendulum"]["min_observed_order"], "single min order mismatch")
    checks.check(examples["single_pendulum"]["order_status"] == "accepted_order", "single order status changed")

    double_min = min_double_order(double)
    checks.check(
        double.get("status") == "accepted_local_reference_v046_floor_diagnostic",
        "double-pendulum status changed",
    )
    checks.check(double.get("accepted_reference") == "v029_fullva_nested_h0.005", "double reference policy changed")
    checks.check(double_min > 6.0, "double-pendulum order is not above six")
    checks.check(rounded(double_min) == examples["double_pendulum"]["min_observed_order"], "double min order mismatch")
    checks.check(examples["double_pendulum"]["order_status"] == "accepted_order", "double order status changed")

    for model, residual_threshold in {"four_link": 2e-13, "slider_crank": 1e-14}.items():
        model_gate = examples[model]
        checks.check(closed_loop[model]["status"] == "accepted_kinematic_fullva", f"{model} kinematic status changed")
        checks.check(reaction[model]["status"] == "accepted_reaction_dynamics", f"{model} reaction status changed")
        checks.check(model_gate["closed_loop_status"] == "accepted_kinematic_fullva", f"{model} gate kinematic status changed")
        checks.check(model_gate["reaction_status"] == "accepted_reaction_dynamics", f"{model} gate reaction status changed")
        checks.check(model_gate["order_status"] == "not_accepted_dynamic_order", f"{model} dynamic-order status changed")
        checks.check(
            math.isclose(
                float(reaction[model]["max_dynamics_residual_norm"]),
                float(model_gate["max_dynamics_residual_norm"]),
                rel_tol=0.0,
                abs_tol=1e-20,
            ),
            f"{model} dynamics residual mismatch",
        )
        checks.check(
            float(model_gate["max_dynamics_residual_norm"]) <= residual_threshold,
            f"{model} dynamics residual exceeds threshold",
        )

    checks.check(probe_gate.get("schema") == "closed-loop-coarse-dynamic-order-probe-v1", "probe schema changed")
    checks.check(probe_summary.get("schema") == "closed-loop-coarse-dynamic-order-probe-v1", "probe summary schema changed")
    for key in [
        "step_sizes",
        "reference_h",
        "ok_row_count",
        "row_count",
        "failed_row_count",
        "local_velocity_evidence_rows",
        "local_acceleration_evidence_rows",
        "local_position_floor_rows",
        "accepted_dynamic_order_count",
        "external_superiority_claim",
        "same_test_campaign_status",
    ]:
        checks.check(probe_summary.get(key) == probe_gate.get(key), f"probe field mismatch: {key}")
    checks.check(probe_gate.get("accepted_dynamic_order_count") == 0, "external dynamic order unexpectedly accepted")
    checks.check(probe_gate.get("external_superiority_claim") is False, "external superiority unexpectedly claimed")
    checks.check(probe_summary.get("default_policy") == "coarse_first_no_default_1e-4", "probe default policy changed")

    checks.check(
        local_candidate_gate.get("schema") == "closed-loop-true-dynamic-newton-coarse-order-v1",
        "local closed-loop dynamic-order candidate schema changed",
    )
    for key in [
        "schema",
        "status",
        "models",
        "step_sizes",
        "row_count",
        "ok_row_count",
        "stage_predictor_policy",
        "stage_oracle_used",
        "convergence_sweep_run",
        "external_superiority_claim",
        "default_1e-4_required",
        "heavy_numerical_run_invoked",
    ]:
        checks.check(
            local_candidate_summary.get(key) == local_candidate_gate.get(key),
            f"local candidate field mismatch: {key}",
        )
    checks.check(local_candidate_gate.get("reference_h") == 0.0125, "local candidate reference h changed")
    checks.check(local_candidate_gate.get("models") == EXPECTED_LOCAL_CANDIDATE_MODELS, "local candidate model set changed")
    checks.check(local_candidate_gate.get("accepted_local_dynamic_order_candidate_count") == 2, "local candidate accepted count changed")
    checks.check(
        local_candidate_summary.get("accepted_dynamic_order_count")
        == local_candidate_gate.get("accepted_local_dynamic_order_candidate_count"),
        "local candidate accepted count does not match source artifact",
    )
    checks.check(local_candidate_gate.get("row_count") == 6, "local candidate row count changed")
    checks.check(local_candidate_gate.get("ok_row_count") == 6, "local candidate ok row count changed")
    checks.check(local_candidate_gate.get("stage_oracle_used") is False, "local candidate unexpectedly used stage oracle")
    checks.check(local_candidate_gate.get("default_1e-4_required") is False, "local candidate incorrectly requires default 1e-4")
    checks.check(local_candidate_gate.get("heavy_numerical_run_invoked") is False, "local candidate invoked a heavy numerical run")
    checks.check(local_candidate_gate.get("external_superiority_claim") is False, "local candidate overclaims external superiority")
    checks.check(local_candidate_gate.get("endpoint_acceleration_order_diagnostic_only") is True, "local candidate acceleration boundary changed")
    checks.check(local_candidate_gate.get("finite_window_diagnostics_only") is True, "local candidate finite-window boundary changed")
    checks.check(
        local_candidate_gate.get("does_not_instantiate_residual_to_error_implication") is True,
        "local candidate residual-to-error implication boundary changed",
    )
    checks.check(local_candidate_gate.get("does_not_close_p7") is True, "local candidate P7 boundary changed")
    checks.check(
        local_candidate_gate.get("does_not_promote_four_link_or_slider_crank_to_accepted_dynamic_order")
        is True,
        "local candidate dynamic-order nonpromotion boundary changed",
    )
    summaries = local_candidate_summary.get("model_summaries", {})
    checks.check(
        local_candidate_gate.get("four_link_primary_orders")
        == [
            rounded(summaries["four_link"]["pos_observed_order"]),
            rounded(summaries["four_link"]["orientation_observed_order"]),
            rounded(summaries["four_link"]["vel_observed_order"]),
            rounded(summaries["four_link"]["omega_observed_order"]),
        ],
        "four-link local candidate primary orders changed",
    )
    checks.check(
        local_candidate_gate.get("slider_crank_primary_orders")
        == [
            rounded(summaries["slider_crank"]["pos_observed_order"]),
            rounded(summaries["slider_crank"]["orientation_observed_order"]),
            rounded(summaries["slider_crank"]["vel_observed_order"]),
            rounded(summaries["slider_crank"]["omega_observed_order"]),
        ],
        "slider-crank local candidate primary orders changed",
    )

    checks.check(
        residual_to_error_gate.get("schema") == "closed-loop-residual-to-error-theorem-obligations-v1",
        "residual-to-error route schema changed",
    )
    for key in [
        "obligation_count",
        "blocking_obligation_count",
        "accepted_residual_to_error_theorem",
        "accepted_dynamic_order_count",
    ]:
        checks.check(residual_to_error_summary.get(key) == residual_to_error_gate.get(key), f"residual-to-error field mismatch: {key}")
    checks.check(residual_to_error_gate.get("obligation_count") == 7, "residual-to-error obligation count changed")
    checks.check(residual_to_error_gate.get("blocking_obligation_count") == 7, "residual-to-error blocking count changed")
    checks.check(
        residual_to_error_gate.get("accepted_residual_to_error_theorem") is False,
        "residual-to-error theorem unexpectedly accepted",
    )
    checks.check(residual_to_error_gate.get("accepted_dynamic_order_count") == 0, "residual-to-error route accepted order")
    checks.check(execution_policy.get("default_step_policy") == "coarse_first_no_default_1e-4", "gate default policy changed")
    checks.check(execution_policy.get("strict_public_policy_1e-4") == "opt_in_only", "1e-4 policy changed")
    checks.check(execution_policy.get("default_1e-4_required") is False, "gate incorrectly requires default 1e-4")

    checks.check("ORDER_ACCEPTANCE_GATE.md" in manifest.get("evidence_anchors", []), "manifest missing order gate anchor")
    checks.check("ORDER_ACCEPTANCE_GATE.json" in manifest.get("evidence_anchors", []), "manifest missing order gate JSON anchor")
    checks.check("validate_order_acceptance_gate.py" in manifest.get("validators", []), "manifest missing order gate validator")
    checks.check(
        boundary.get("evidence_files", {}).get("order_acceptance_gate")
        == "paper_v047_cylindrical_chain/ORDER_ACCEPTANCE_GATE.md",
        "claim boundary missing order gate",
    )
    checks.check(
        boundary.get("evidence_files", {}).get("order_acceptance_gate_json")
        == "paper_v047_cylindrical_chain/ORDER_ACCEPTANCE_GATE.json",
        "claim boundary missing order gate JSON",
    )

    required_tokens = [
        "Order Acceptance Gate",
        "`Gauss6/FullVA`",
        "Method-order claim: `6`",
        "Proof-level local defect: `O(h^7)`",
        "Proof-level global error: `O(h^6)`",
        "Comparator expected order: `2m-1=5`",
        "`single_pendulum`",
        "`double_pendulum`",
        "`four_link`",
        "`slider_crank`",
        "`accepted_order`",
        "`not_accepted_dynamic_order`",
        "`h=[0.1,0.05,0.025]`",
        "Local Closed-Loop Coarse-Dynamics Candidate Evidence",
        "`closed_loop_true_dynamic_newton_coarse_order.json`",
        "closed-loop coarse-dynamics diagnostic examples: `2`",
        "primary-state orders for `four_link`: `5.955/5.955/6.085/5.971`",
        "primary-state orders for `slider_crank`: `6.164/6.159/7.341/6.426`",
        "endpoint acceleration order is diagnostic only",
        "finite-window diagnostics only",
        "do not instantiate the residual-to-error implication",
        "do not close P7",
        "do not promote four-link or slider-crank to accepted dynamic-order examples",
        "`default_1e-4_required=false`",
        "`heavy_numerical_run_invoked=false`",
        "accepted external dynamic-order rows: `0`",
        "Residual-To-Error Proof Route",
        "`accepted_residual_to_error_theorem=false`",
        "seven blocking",
        "`coarse_first_no_default_1e-4`",
        "Strict public-policy `1e-4` rows are opt-in only",
        "Observed Order Interpretation",
        "not a seventh-order theorem",
        "`eta_h^tube <= c_eta h^7`",
    ]
    for token in required_tokens:
        checks.check(contains_normalized(gate_md, token), f"ORDER_ACCEPTANCE_GATE.md missing token: {token}")

    for token in [
        "should not be read as a seventh-order method claim",
        "sixth order under an $O(h^7)$ local-defect contract",
        "small relative to higher-order terms",
        "close to reference, nonlinear-tolerance, and floating-point floors",
        "post-theorem consistency evidence for the order-six behavior",
        "not as a proof premise or a new asymptotic order",
        "\\(\\eta_h^{\\rm tube}\\le c_\\eta h^7\\) nonlinear tolerance",
        "not promoted to dynamic order estimates",
        "They are finite-window diagnostics",
        "they do not instantiate the residual-to-error implication",
        "do not close P7",
        "do not promote four-link or slider-crank to accepted dynamic-order examples",
    ]:
        checks.check(contains_normalized(manuscript, token), f"main_cmame.tex missing observed-order interpretation token: {token}")

    for token in [
        "ORDER_ACCEPTANCE_GATE.md",
        "validate_order_acceptance_gate.py",
        "Example-level order boundary",
        "not accepted external dynamic order",
        "Block unsupported residual-to-error promotion",
        "accepted_residual_to_error_theorem=false",
        "not a seventh-order theorem",
        "finite-window diagnostics only",
        "do not instantiate the residual-to-error implication",
        "do not close P7",
        "do not promote four-link or slider-crank to accepted dynamic-order",
    ]:
        checks.check(contains_normalized(proof_matrix, token), f"PROOF_EVIDENCE_MATRIX.md missing order-gate token: {token}")

    checks.check(
        contains_normalized(fidelity, "not a dynamic symbolic-equivalence proof"),
        "implementation certificate lost symbolic-oracle boundary",
    )

    forbidden = [
        "external_same_test_superiority_accepted",
        "complete_source_paper_residual_reproduction_accepted",
        "independent_full_tfe_stage_replacement_accepted",
        "four_link_slider_crank_external_dynamic_order_accepted",
        "default_1e-4_required_for_current_order_gate",
    ]
    normalized_md = " ".join(gate_md.split()).lower()
    for token in forbidden:
        checks.check(token in gate.get("forbidden_claims", []), f"gate JSON missing forbidden claim: {token}")
    checks.check("full_tfe_stage_replacement=true" not in normalized_md, "order gate markdown overclaims full-TFE replacement")

    if checks.errors:
        print("v047 order acceptance gate validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("v047 order acceptance gate validation: PASS")
    print("accepted_method=Gauss6/FullVA")
    print("accepted_method_order=6")
    print("comparator_expected_order=5")
    print("smooth_projected_orders=7.161/7.066")
    print("observed_order_interpretation=not_seventh_order_claim")
    print("single_absolute_min_order=6.024")
    print("double_method_min_order=6.089")
    print("accepted_dynamic_order_examples=single_pendulum,double_pendulum")
    print("coverage_only_examples=four_link,slider_crank")
    print("local_closed_loop_dynamic_order_candidates=2")
    print("four_link_true_dynamic_primary_orders=5.955/5.955/6.085/5.971")
    print("slider_crank_true_dynamic_primary_orders=6.164/6.159/7.341/6.426")
    print("external_dynamic_order_accepted=False")
    print("coarse_probe_steps=0.1,0.05,0.025")
    print("default_1e-4=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
