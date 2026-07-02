#!/usr/bin/env python3
"""Read-only guard for the current v047 full-TFE replacement gap.

This validator does not try to accept the full TFE replacement. It verifies the
opposite claim boundary: terminal closure and many negative capacity audits are
present, but no accepted independent full-TFE stage replacement is present yet.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


PIPELINE = Path(__file__).resolve().parent
RESULTS = PIPELINE / "results"
SUMMARY = RESULTS / "summary_v047.json"
LEDGER = PIPELINE / "FULL_TFE_REPLACEMENT_GAP_LEDGER.md"

EXPECTED_ASME_STATUS = "four_asme_method_rows_accepted_projection_sharp_sparse_caveats"
EXPECTED_MODELS = {"single_pendulum", "double_pendulum", "four_link", "slider_crank"}


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_summary() -> dict:
    with SUMMARY.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def as_float(data: dict, key: str, default: float = 0.0) -> float:
    try:
        return float(data.get(key, default))
    except (TypeError, ValueError):
        return default


def check_required_files(checks: Checks) -> None:
    required = [
        LEDGER,
        RESULTS / "cylindrical_chain_endpoint_tfe_readiness_audit.csv",
        RESULTS / "cylindrical_chain_endpoint_tfe_paper_lower_pair_source_free_final_stage_velocity_closure_audit.csv",
        RESULTS / "cylindrical_chain_endpoint_tfe_paper_lower_pair_source_free_order_closure_blend_trajectory_audit.csv",
        RESULTS / "cylindrical_chain_endpoint_tfe_paper_lower_pair_source_free_near_final_beta_boundary_audit.csv",
        RESULTS / "cylindrical_chain_endpoint_tfe_paper_lower_pair_source_free_near_final_beta_boundary_audit.json",
        RESULTS / "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_feedback_gain_boundary_audit.csv",
        RESULTS / "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_feedback_gain_boundary_audit.json",
        RESULTS / "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_component_feedback_gain_boundary_audit.csv",
        RESULTS / "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_component_feedback_gain_boundary_audit.json",
        RESULTS / "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_hscaled_feedback_gain_boundary_audit.csv",
        RESULTS / "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_hscaled_feedback_gain_boundary_audit.json",
        RESULTS / "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_source_law_trajectory_screen_audit.csv",
        RESULTS / "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_source_law_trajectory_screen_audit.json",
        RESULTS / "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_three_history_source_law_trajectory_screen_audit.csv",
        RESULTS / "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_three_history_source_law_trajectory_screen_audit.json",
        RESULTS / "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_four_history_source_law_trajectory_screen_audit.csv",
        RESULTS / "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_four_history_source_law_trajectory_screen_audit.json",
        RESULTS / "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_nonlinear_history_source_law_trajectory_screen_audit.csv",
        RESULTS / "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_nonlinear_history_source_law_trajectory_screen_audit.json",
        RESULTS / "cylindrical_chain_endpoint_tfe_paper_lower_pair_candidate_frontier_audit.csv",
        RESULTS / "cylindrical_chain_endpoint_tfe_paper_lower_pair_candidate_frontier_audit.json",
        RESULTS / "cylindrical_chain_endpoint_tfe_paper_lower_pair_bounded_tangent_requirement_audit.csv",
        RESULTS / "cylindrical_chain_endpoint_tfe_paper_lower_pair_bounded_tangent_requirement_audit.json",
        RESULTS / "cylindrical_chain_endpoint_tfe_paper_lower_pair_closure_acceptance_matrix_audit.csv",
        RESULTS / "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_gradient_differential_audit.csv",
        RESULTS / "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_gradient_differential_audit.json",
        RESULTS / "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_matrix_gradient_differential_audit.csv",
        RESULTS / "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_matrix_gradient_differential_audit.json",
        RESULTS / "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_translation_velocity_matrix_differential_audit.csv",
        RESULTS / "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_translation_velocity_matrix_differential_audit.json",
        RESULTS / "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_translation_angular_coupled_matrix_differential_audit.csv",
        RESULTS / "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_translation_angular_coupled_matrix_differential_audit.json",
        RESULTS / "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_feature_dictionary_span_audit.csv",
        RESULTS / "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_feature_dictionary_span_audit.json",
        RESULTS / "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_feature_coefficient_law_screen_audit.csv",
        RESULTS / "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_feature_coefficient_law_screen_audit.json",
        RESULTS / "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_state_feature_coefficient_derivative_screen_audit.csv",
        RESULTS / "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_state_feature_coefficient_derivative_screen_audit.json",
        RESULTS / "cylindrical_chain_endpoint_tfe_paper_lower_pair_endpoint_pose_velocity_hscaled_predictor_h_sweep_audit.csv",
        RESULTS / "cylindrical_chain_endpoint_tfe_paper_lower_pair_endpoint_pose_velocity_hscaled_predictor_h_sweep_audit.json",
        RESULTS / "cylindrical_chain_endpoint_tfe_paper_lower_pair_endpoint_pose_velocity_hscaled_response_audit.csv",
        RESULTS / "cylindrical_chain_endpoint_tfe_paper_lower_pair_endpoint_pose_velocity_hscaled_response_audit.json",
        RESULTS / "cylindrical_chain_endpoint_tfe_paper_lower_pair_endpoint_pose_velocity_predictor_reference_output_audit.csv",
        RESULTS / "cylindrical_chain_endpoint_tfe_paper_lower_pair_endpoint_pose_velocity_predictor_reference_output_audit.json",
        RESULTS / "cylindrical_chain_endpoint_tfe_paper_lower_pair_velocity_compression_audit.csv",
        RESULTS / "cylindrical_chain_endpoint_tfe_paper_lower_pair_velocity_compression_row_space_compression_audit.csv",
        RESULTS / "cylindrical_chain_endpoint_tfe_paper_lower_pair_velocity_compression_row_space_coefficient_derivative_audit.csv",
        RESULTS / "cylindrical_chain_endpoint_tfe_paper_lower_pair_velocity_compression_row_space_coefficient_derivative_audit.json",
        RESULTS / "cylindrical_chain_endpoint_tfe_paper_lower_pair_velocity_compression_weak_row_structure_capacity_audit.csv",
    ]
    for path in required:
        checks.check(path.exists() and path.stat().st_size > 0, f"missing or empty artifact: {path.relative_to(PIPELINE)}")


def check_gap_ledger(checks: Checks) -> None:
    if not LEDGER.exists():
        checks.check(False, "full TFE gap ledger missing")
        return
    text = LEDGER.read_text(encoding="utf-8")
    for token in [
        EXPECTED_ASME_STATUS,
        "full_tfe_stage_replacement=false",
        "accepted_h_sweep_present=false",
        "order_and_terminal_intersection_present=false",
        "accepted_candidate_count=0",
        "36",
        "`0` spans",
        "7.378e-01",
        "9.815e-01",
        "216",
        "0.899",
        "1.456e-15",
        "stage-2 translational velocity",
        "16",
        "diagonal_plus_row_broadcast_feature",
        "0.898873",
        "stage2_velocity_column_broadcast_feature",
        "0.585746",
        "stage2_velocity_shifted_column_broadcast_feature",
        "0.576548",
        "27.8",
        "angular_velocity_w",
        "0.502991",
        "0.963038",
        "0.909693",
        "0.487135",
        "stage-2 angular velocity",
        "stage2_angular_velocity_shifted_column_broadcast_feature",
        "0.752997",
        "0.660361",
        "0.978093",
        "simple angular-only masking",
        "coupled translation/angular stage-2",
        "stage2_velocity_angular_to_translation_cross_feature",
        "0.898812",
        "0.556004",
        "0.999994",
        "translation/angular outer-cross",
        "paper_endpoint_pose_positive_lagrange_z",
        "0.117782",
        "0.514237",
        "0.961546",
        "endpoint-pose positive-Lagrange",
        "paper_endpoint_pose_stage02_convex_0p00_z",
        "terminal-bridge equivalent",
        "paper_endpoint_pose_stage02_convex_0p05_z",
        "0.049317",
        "h=0.02",
        "0.051890",
        "h=0.01",
        "0.052472",
        "stage02_convex_pose_velocity_0p01_z",
        "0.009512",
        "0.009978",
        "0.010085",
        "0.019205",
        "0.049390",
        "0.103464",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_z",
        "4.699e-06",
        "2.335e-06",
        "1.168e-06",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p05_z",
        "1.175e-05",
        "terminal_bridge_equivalent_predictor=true",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_accel_m1_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_accel_p1_z",
        "0.076159",
        "lie_position_u",
        "nonterminal_span_row_count=0",
        "stage02_convex_pose_velocity_slope_0p01_0p05_z",
        "0.677034",
        "25.8",
        "0.490108",
        "stage02_convex_pose_velocity_curvature_0p01_0p05_0p10_z",
        "0.871228",
        "26.7",
        "0.591909",
        "0.886084",
        "source_curvature_shifted_column_broadcast_feature",
        "0.898873",
        "44.8",
        "0.556060",
        "1.000000",
        "source_curvature_minus_history_delta_diagonal_plus_row_broadcast_feature",
        "0.898865",
        "45.5",
        "0.556051",
        "0.999996",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_curvature_m0p1_z",
        "5.298e-06",
        "47.5",
        "translation_acceleration_a",
        "0.407672",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_curvature_p0p01_z",
        "52.9",
        "1.076e-14",
        "0.549481",
        "0.444777",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_accel_p0p01_z",
        "0.000867721",
        "31.4",
        "0.706665",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_genaccel_p0p01_z",
        "0.000866899",
        "30.2",
        "0.701135",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_p0p01_z",
        "4.1835e-05",
        "29.9",
        "0.711570",
        "0.771337",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_p0p0005_z",
        "5.5898e-06",
        "30.0",
        "translation_acceleration_a",
        "0.350240",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_posevelaccel_p0p0005_m0p0001_z",
        "1.0173e-05",
        "30.7",
        "0.544660",
        "component-split pose-acceleration",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_transposeaccel_m0p01_z",
        "32.3+32.3",
        "9.6511e-06",
        "angular/Lie",
        "component-split velocity-acceleration",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelaccel_m0p01_z",
        "2.138e-04",
        "31.8",
        "0.886603",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelaccel_m0p0005_z",
        "9.8175e-06",
        "31.4",
        "0.802349",
        "0.000864560",
        "component-mixed pose/velocity Taylor",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_angpose_transvelaccel_p0p0005_m0p0005_z",
        "9.987e-06",
        "32.0",
        "0.774582",
        "0.625975",
        "stage-2-fixed/delta acceleration velocity-shift",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelaccelstage2_m0p0005_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelacceldelta20_m0p0005_z",
        "1.0119e-05",
        "nonfinal terminal velocity/source predictor",
        "nonfinal_velocity_terminal_euler1_z",
        "0.923466",
        "translation_velocity_v",
        "0.959959",
        "stage-2 source-to-velocity transport",
        "stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p1_z",
        "0.001251",
        "stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p01_z",
        "0.0001251",
        "stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p0001_z",
        "1.251e-06",
        "49.6",
        "stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p0001_angposeaccel_p0p0001_z",
        "1.296e-06",
        "48.7",
        "stage02_convex_pose_velocity_0p00_z",
        "1.327e-15",
        "31.7",
        "span_row_count=1",
        "nonterminal_span_row_count=1",
        "local-span-not-full-TFE",
        "lower_pair_endpoint_pose_velocity_predictor_h_sweep_smoke",
        "21.5",
        "7.29e-17",
        "6.588/4.508",
        "28.6",
        "8.124e-17",
        "4.142/2.305",
        "endpoint_pose_velocity_predictor_reference_output_audit",
        "smooth_order_ok_count=0",
        "3.672/1.956",
        "near_final_beta_boundary",
        "0.99999999",
        "1.255e-12",
        "smooth_order_ok_count=2",
        "order_terminal_intersection_present=false",
        "near_final_collapse_confirmed=true",
        "recurrent_feedback_gain_boundary",
        "feedback_gain=12",
        "1.036e-16",
        "recurrent_component_feedback_gain_boundary",
        "7.538e-17",
        "recurrent_hscaled_feedback_gain_boundary",
        "4.711",
        "1.316e-08",
        "recurrent_source_law_trajectory_screen",
        "terminal_closed_row_count=0",
        "smooth_order_ok_count=5",
        "2.016e-07",
        "5.355",
        "terminal_closure_requires_order_collapse=true",
        "stage02_convex_pose_velocity_0p01_z",
        "6.255e-06",
        "2.345/1.878",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_z",
        "projection_used=false",
        "1.254e-07",
        "6.412/3.775",
        "1.244e-08",
        "4.054/2.364",
        "stage02_convex_pose_velocity_extrapolate_0p00001_0p00002_z",
        "3.135e-08",
        "6.270e-09",
        "1.254e-09",
        "4.143/2.307",
        "1.254e-13",
        "1.254e-14",
        "stage02_convex_pose_velocity_quadextrapolate_0p002_0p005_0p01_z",
        "2.029e-11",
        "2.029e-12",
        "2.029e-13",
        "8.254e-15",
        "nonfinal_velocity_terminal_linear012_z",
        "nonfinal_velocity_terminal_euler2_z",
        "1.770e-07",
        "3.584e-07",
        "2.559e-11",
        "1.328e-07",
        "1.134e-07",
        "stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p00001_z",
        "8.021e-13",
        "5.910e-14",
        "terminal_velocity_closed=true",
        "stage02_convex_pose_velocity_0p01_terminalproj_z",
        "6.739e+08",
        "stage02_convex_pose_velocity_0p01_terminalproj_p0p1_z",
        "7.028e-06",
        "2.301/1.788",
        "stage02_convex_pose_velocity_0p01_terminalproj_p0p5_z",
        "1.321e-05",
        "2.158/1.433",
        "projection_used=true",
        "smooth_order_ok=false",
        "accepted_h_sweep_present=false",
        "0.597218",
        "gauss_endpoint_pose_positive_lagrange_z",
        "0.208599",
        "28.7",
        "lie_position_u",
        "0.650605",
        "gauss_endpoint_pose_stage02_convex_0p00_z",
        "0.172659",
        "31.5",
        "0.952340",
        "0.320394",
        "0.305625",
        "0.373981",
        "stage2_velocity_feature_outer_stage2_velocity",
        "0.898720",
        "component-pair outer-product coupling",
        "stage2_velocity_diagonal_plus_hadamard_row_feature_stage2_velocity",
        "0.898530",
        "componentwise and shifted-diagonal coupling",
        "stage02_convex_pose_velocity_0p01_accel_m0p1_z",
        "stage02_convex_pose_velocity_0p01_genaccel_m0p1_z",
        "0.012376",
        "0.077874",
        "generalized-velocity acceleration predictor",
        "simple nonterminal acceleration corrections",
        "stage02_convex_pose_velocity_0p02_poseslope_m0p1_z",
        "0.878519",
        "kinematic stage-pose-slope velocity predictors",
        "source-to-velocity lift",
        "current-pose",
        "stage02_convex_pose_velocity_0p01_sourcelift_historydelta_p1_z",
        "stage02_convex_pose_velocity_0p01_sourcelift_source0_p1_z",
        "0.609803",
        "matrix-difference source-to-velocity lift",
        "0.042593",
        "58.7",
        "stage02_convex_pose_velocity_0p01_sourceliftmatrixdiff_historydelta_p0p1_z",
        "0.009527",
        "92.5",
        "normalized-history",
        "stage02_convex_pose_velocity_0p01_sourceliftmatrixdiff_historyunitdelta_p0p1_z",
        "0.009590",
        "49.4",
        "target-free row/column matrix coefficient-gradient",
        "target-free active-velocity coefficient-gradient",
        "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_gradient_differential_audit",
        "curvature_plus_history_delta",
        "0.898872",
        "translation-velocity matrix",
        "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_translation_velocity_matrix_differential_audit",
        "stage2_translation_velocity_symmetric_broadcast_feature",
        "0.671049",
        "angular_velocity_w",
        "translation/angular coupled matrix",
        "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_translation_angular_coupled_matrix_differential_audit",
        "stage2_velocity_bidirectional_rowmask_translation_angular_feature",
        "0.742069",
        "h-adaptive endpoint-pose velocity predictor",
        "cylindrical_chain_endpoint_tfe_paper_lower_pair_endpoint_pose_velocity_hscaled_predictor_h_sweep_audit",
        "stage02_convex_pose_velocity_extrapolate_0p00001_0p00002_hpow_m1_z",
        "5.004e-13",
        "3.523/4.828",
        "terminal_velocity_closed=false",
        "h-adaptive endpoint-pose velocity response audit",
        "cylindrical_chain_endpoint_tfe_paper_lower_pair_endpoint_pose_velocity_hscaled_response_audit",
        "terminal_closed_row_count=1",
        "smooth_order_ok_count=0",
        "order_terminal_intersection_present=false",
        "revised analytical weak-row formula",
        "nonlinear recurrent history source law",
        "three-history recurrent source law",
        "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_three_history_source_law_trajectory_screen_audit",
        "recurrent_threehistory_velocity_terminal_source01historyslopejerk_z",
        "2.923e-07",
        "5.345",
        "terminal_closed_row_count=0",
        "nonlinear-history recurrent source law",
        "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_nonlinear_history_source_law_trajectory_screen_audit",
        "recurrent_nonlinearhistory_velocity_terminal_source0historyhadamard_z",
        "1.954e-07",
        "3.525",
        "smooth_order_ok_count=0",
        "source-law final-retain boundary",
        "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_source_law_final_retain_boundary_audit",
        "terminal_closed_row_count=4",
        "best smooth min order `4.510`",
        "candidate frontier audit",
        "cylindrical_chain_endpoint_tfe_paper_lower_pair_candidate_frontier_audit",
        "total_candidate_row_count=115",
        "order_terminal_intersection_count=0",
        "stage-local weak-row tangent",
        "bounded tangent requirement audit",
        "cylindrical_chain_endpoint_tfe_paper_lower_pair_bounded_tangent_requirement_audit",
        "requirement_row_count=7",
        "target_free_formula_span_count=0",
        "row_space_oracle_span_count=36",
        "bounded_gradient_practical_cap_spanning_row_count=12",
        "feature-dictionary span audit",
        "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_feature_dictionary_span_audit",
        "feature_dictionary_row_count=12",
        "combined_all_dictionary_span_count=2",
        "stage2_matrix_core",
        "formula_coefficient_law_present=false",
        "frozen coefficient-law screen",
        "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_feature_coefficient_law_screen_audit",
        "coefficient_law_row_count=60",
        "span_count=0",
        "closure_delta_norm_weights",
        "coefficient_derivative_included=false",
        "target_jacobian_used_for_formula=false",
        "state-feature coefficient-derivative screen",
        "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_state_feature_coefficient_derivative_screen_audit",
        "state_feature_coefficient_derivative_row_count=36",
        "inverse_closure_delta_norm_weights_derivative",
        "coefficient_derivative_included=true",
        "four-history recurrent source-law",
        "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_four_history_source_law_trajectory_screen_audit",
        "four_history_source_law_trajectory_screen_present",
        "recurrent_fourhistory_velocity_terminal_source01historyslopejerksnap_z",
        "2.950e-07",
        "5.342",
        "validate_full_tfe_gap.py",
    ]:
        checks.check(token in text, f"full TFE gap ledger missing token: {token}")


def check_summary_boundary(checks: Checks, summary: dict) -> dict[str, object]:
    asme = summary.get("asme_gate", {})
    readiness = summary.get("endpoint_tfe_readiness_audit", {})
    final_stage = summary.get("endpoint_tfe_paper_lower_pair_source_free_final_stage_velocity_closure_audit", {})
    blend = summary.get("endpoint_tfe_paper_lower_pair_source_free_order_closure_blend_trajectory_audit", {})
    near_final = summary.get("endpoint_tfe_paper_lower_pair_source_free_near_final_beta_boundary_audit", {})
    feedback_gain = summary.get("endpoint_tfe_paper_lower_pair_recurrent_feedback_gain_boundary_audit", {})
    component_feedback_gain = summary.get(
        "endpoint_tfe_paper_lower_pair_recurrent_component_feedback_gain_boundary_audit", {}
    )
    hscaled_feedback_gain = summary.get(
        "endpoint_tfe_paper_lower_pair_recurrent_hscaled_feedback_gain_boundary_audit", {}
    )
    source_law_screen = summary.get(
        "endpoint_tfe_paper_lower_pair_recurrent_source_law_trajectory_screen_audit", {}
    )
    three_history_source_law = summary.get(
        "endpoint_tfe_paper_lower_pair_recurrent_three_history_source_law_trajectory_screen_audit", {}
    )
    four_history_source_law = summary.get(
        "endpoint_tfe_paper_lower_pair_recurrent_four_history_source_law_trajectory_screen_audit", {}
    )
    nonlinear_history_source_law = summary.get(
        "endpoint_tfe_paper_lower_pair_recurrent_nonlinear_history_source_law_trajectory_screen_audit", {}
    )
    source_law_final_retain = summary.get(
        "endpoint_tfe_paper_lower_pair_recurrent_source_law_final_retain_boundary_audit", {}
    )
    acceptance = summary.get("endpoint_tfe_paper_lower_pair_closure_acceptance_matrix_audit", {})
    stage2_gradient = summary.get("endpoint_tfe_paper_lower_pair_recurrent_stage2_gradient_differential_audit", {})
    stage2_matrix = summary.get("endpoint_tfe_paper_lower_pair_recurrent_stage2_matrix_gradient_differential_audit", {})
    stage2_translation_matrix = summary.get("endpoint_tfe_paper_lower_pair_recurrent_stage2_translation_velocity_matrix_differential_audit", {})
    stage2_coupled_matrix = summary.get("endpoint_tfe_paper_lower_pair_recurrent_stage2_translation_angular_coupled_matrix_differential_audit", {})
    stage2_dictionary = summary.get("endpoint_tfe_paper_lower_pair_recurrent_stage2_feature_dictionary_span_audit", {})
    stage2_coefficient = summary.get("endpoint_tfe_paper_lower_pair_recurrent_stage2_feature_coefficient_law_screen_audit", {})
    stage2_state_coefficient = summary.get(
        "endpoint_tfe_paper_lower_pair_recurrent_stage2_state_feature_coefficient_derivative_screen_audit",
        {},
    )
    hscaled_endpoint_pose = summary.get("endpoint_tfe_paper_lower_pair_endpoint_pose_velocity_hscaled_predictor_h_sweep_audit", {})
    hscaled_response = summary.get("endpoint_tfe_paper_lower_pair_endpoint_pose_velocity_hscaled_response_audit", {})
    candidate_frontier = summary.get("endpoint_tfe_paper_lower_pair_candidate_frontier_audit", {})
    bounded_requirement = summary.get("endpoint_tfe_paper_lower_pair_bounded_tangent_requirement_audit", {})
    compression = summary.get("endpoint_tfe_paper_lower_pair_velocity_compression_audit", {})

    checks.check(asme.get("status") == EXPECTED_ASME_STATUS, "ASME gate status changed")
    checks.check(set(asme.get("models", {})) == EXPECTED_MODELS, "ASME model set changed")

    counts = readiness.get("counts", {})
    checks.check(counts.get("missing", 0) >= 1, "TFE readiness no longer records a missing item")
    checks.check(counts.get("partial", 0) >= 38, "TFE readiness lost partial gap evidence")
    checks.check(counts.get("satisfied", 0) >= 31, "TFE readiness lost satisfied evidence")

    checks.check(final_stage.get("full_tfe_stage_replacement") is False, "final-stage closure unexpectedly claims full TFE")
    checks.check(as_float(final_stage, "max_raw_terminal_endpoint_velocity_constraint_norm", 1.0) < 1e-12, "final-stage closure no longer closes terminal velocity")
    smooth_final = final_stage.get("cases", {}).get("cylindrical_smooth", {})
    checks.check(as_float(smooth_final, "position_order", 10.0) < 5.0, "final-stage closure no longer records smooth-order limitation")

    checks.check(blend.get("full_tfe_stage_replacement") is False, "order/closure blend unexpectedly claims full TFE")
    checks.check(blend.get("order_and_terminal_intersection_present") is False, "order/closure intersection unexpectedly present")
    checks.check(as_float(blend, "global_best_beta_max_terminal_velocity", 1.0) < 1e-12, "blend lost terminal-closing beta")
    checks.check(as_float(blend, "global_best_beta_min_order", 10.0) < 2.5, "blend no longer records order-limited terminal-closing branch")

    checks.check(near_final.get("full_tfe_stage_replacement") is False, "near-final beta boundary unexpectedly claims full TFE")
    checks.check(near_final.get("accepted_h_sweep_present") is False, "near-final beta boundary unexpectedly claims accepted h-sweep")
    checks.check(near_final.get("order_terminal_intersection_present") is False, "near-final beta boundary unexpectedly has an order/terminal intersection")
    checks.check(near_final.get("near_final_collapse_confirmed") is True, "near-final beta boundary lost collapse marker")
    checks.check(near_final.get("smooth_order_ok_count") == 2, "near-final beta boundary smooth-order count changed")
    checks.check(near_final.get("nonfinal_terminal_closed_count") == 0, "near-final beta boundary unexpectedly closes a nonfinal beta")
    checks.check(1.0e-12 < as_float(near_final, "best_nonfinal_terminal_velocity") < 2.0e-12, "near-final beta boundary best nonfinal terminal velocity changed")
    checks.check(as_float(near_final, "best_nonfinal_terminal_min_order", 10.0) < 5.0, "near-final beta boundary no longer records order collapse")

    checks.check(feedback_gain.get("full_tfe_stage_replacement") is False, "recurrent feedback gain boundary unexpectedly claims full TFE")
    checks.check(feedback_gain.get("accepted_h_sweep_present") is False, "recurrent feedback gain boundary unexpectedly claims accepted h-sweep")
    checks.check(feedback_gain.get("order_terminal_intersection_present") is False, "recurrent feedback gain boundary unexpectedly has an order/terminal intersection")
    checks.check(feedback_gain.get("terminal_closure_requires_order_collapse") is True, "recurrent feedback gain boundary lost order-collapse marker")
    checks.check(feedback_gain.get("terminal_closed_gain_count") == 5, "recurrent feedback gain boundary terminal-closed count changed")
    checks.check(feedback_gain.get("smooth_order_ok_count") == 1, "recurrent feedback gain boundary smooth-order count changed")
    checks.check(as_float(feedback_gain, "best_terminal_velocity", 1.0) < 1.0e-12, "recurrent feedback gain boundary best terminal velocity changed")
    checks.check(as_float(feedback_gain, "best_terminal_min_order", 10.0) < 5.0, "recurrent feedback gain boundary no longer records terminal-branch order collapse")
    checks.check(as_float(feedback_gain, "best_smooth_order_terminal_velocity", 0.0) > 1.0e-7, "recurrent feedback gain boundary no longer records open-terminal high-order branch")

    checks.check(component_feedback_gain.get("full_tfe_stage_replacement") is False, "component recurrent feedback gain boundary unexpectedly claims full TFE")
    checks.check(component_feedback_gain.get("accepted_h_sweep_present") is False, "component recurrent feedback gain boundary unexpectedly claims accepted h-sweep")
    checks.check(component_feedback_gain.get("order_terminal_intersection_present") is False, "component recurrent feedback gain boundary unexpectedly has an order/terminal intersection")
    checks.check(component_feedback_gain.get("terminal_closure_requires_order_collapse") is True, "component recurrent feedback gain boundary lost order-collapse marker")
    checks.check(component_feedback_gain.get("terminal_closed_gain_count") == 5, "component recurrent feedback gain boundary terminal-closed count changed")
    checks.check(component_feedback_gain.get("smooth_order_ok_count") == 1, "component recurrent feedback gain boundary smooth-order count changed")
    checks.check(as_float(component_feedback_gain, "best_terminal_velocity", 1.0) < 1.0e-12, "component recurrent feedback gain boundary best terminal velocity changed")
    checks.check(as_float(component_feedback_gain, "best_terminal_min_order", 10.0) < 5.0, "component recurrent feedback gain boundary no longer records terminal-branch order collapse")
    checks.check(as_float(component_feedback_gain, "best_smooth_order_terminal_velocity", 0.0) > 1.0e-7, "component recurrent feedback gain boundary no longer records open-terminal high-order branch")

    checks.check(hscaled_feedback_gain.get("full_tfe_stage_replacement") is False, "h-scaled recurrent feedback gain boundary unexpectedly claims full TFE")
    checks.check(hscaled_feedback_gain.get("accepted_h_sweep_present") is False, "h-scaled recurrent feedback gain boundary unexpectedly claims accepted h-sweep")
    checks.check(hscaled_feedback_gain.get("order_terminal_intersection_present") is False, "h-scaled recurrent feedback gain boundary unexpectedly has an order/terminal intersection")
    checks.check(hscaled_feedback_gain.get("terminal_closure_requires_order_collapse") is True, "h-scaled recurrent feedback gain boundary lost order-collapse marker")
    checks.check(hscaled_feedback_gain.get("terminal_closed_row_count") == 7, "h-scaled recurrent feedback gain boundary terminal-closed count changed")
    checks.check(hscaled_feedback_gain.get("smooth_order_ok_count") == 0, "h-scaled recurrent feedback gain boundary smooth-order count changed")
    checks.check(as_float(hscaled_feedback_gain, "best_terminal_velocity", 1.0) < 1.0e-12, "h-scaled recurrent feedback gain boundary best terminal velocity changed")
    checks.check(as_float(hscaled_feedback_gain, "best_terminal_min_order", 10.0) < 5.0, "h-scaled recurrent feedback gain boundary no longer records terminal-branch order collapse")
    checks.check(as_float(hscaled_feedback_gain, "best_smooth_order_min_order", 0.0) < 5.0, "h-scaled recurrent feedback gain boundary unexpectedly reaches smooth order")
    checks.check(as_float(hscaled_feedback_gain, "best_smooth_order_terminal_velocity", 0.0) > 1.0e-9, "h-scaled recurrent feedback gain boundary no longer records open-terminal best-order branch")

    checks.check(source_law_screen.get("full_tfe_stage_replacement") is False, "recurrent source-law screen unexpectedly claims full TFE")
    checks.check(source_law_screen.get("accepted_h_sweep_present") is False, "recurrent source-law screen unexpectedly claims accepted h-sweep")
    checks.check(source_law_screen.get("order_terminal_intersection_present") is False, "recurrent source-law screen unexpectedly has an order/terminal intersection")
    checks.check(source_law_screen.get("row_count") == 6, "recurrent source-law screen row count changed")
    checks.check(source_law_screen.get("terminal_closed_row_count") == 0, "recurrent source-law screen unexpectedly closes terminal velocity")
    checks.check(source_law_screen.get("smooth_order_ok_count") == 5, "recurrent source-law screen smooth-order count changed")
    checks.check(2.0e-7 < as_float(source_law_screen, "best_terminal_velocity", 0.0) < 2.1e-7, "recurrent source-law screen best terminal velocity changed")
    checks.check(as_float(source_law_screen, "best_smooth_order_min_order", 0.0) > 5.3, "recurrent source-law screen best smooth order regressed")

    checks.check(three_history_source_law.get("full_tfe_stage_replacement") is False, "three-history recurrent source-law screen unexpectedly claims full TFE")
    checks.check(three_history_source_law.get("accepted_h_sweep_present") is False, "three-history recurrent source-law screen unexpectedly claims accepted h-sweep")
    checks.check(three_history_source_law.get("order_terminal_intersection_present") is False, "three-history recurrent source-law screen unexpectedly has an order/terminal intersection")
    checks.check(three_history_source_law.get("row_count") == 4, "three-history recurrent source-law screen row count changed")
    checks.check(three_history_source_law.get("predictor_law_count") == 4, "three-history recurrent source-law screen law count changed")
    checks.check(three_history_source_law.get("three_history_law_count") == 4, "three-history recurrent source-law screen three-history count changed")
    checks.check(three_history_source_law.get("three_history_source_law_trajectory_screen_present") is True, "three-history recurrent source-law screen lost trajectory-screen marker")
    checks.check(three_history_source_law.get("terminal_closed_row_count") == 0, "three-history recurrent source-law screen unexpectedly closes terminal velocity")
    checks.check(three_history_source_law.get("smooth_order_ok_count") == 2, "three-history recurrent source-law screen smooth-order count changed")
    checks.check(three_history_source_law.get("terminal_closure_requires_order_collapse") is False, "three-history recurrent source-law screen order-collapse marker changed")
    checks.check(three_history_source_law.get("best_terminal_law") == "recurrent_threehistory_velocity_terminal_source01historyslopejerk_z", "three-history recurrent source-law screen best terminal law changed")
    checks.check(2.8e-7 < as_float(three_history_source_law, "best_terminal_velocity", 0.0) < 3.0e-7, "three-history recurrent source-law screen best terminal velocity changed")
    checks.check(5.33 < as_float(three_history_source_law, "best_smooth_order_min_order", 0.0) < 5.36, "three-history recurrent source-law screen best smooth order changed")

    checks.check(four_history_source_law.get("full_tfe_stage_replacement") is False, "four-history recurrent source-law screen unexpectedly claims full TFE")
    checks.check(four_history_source_law.get("accepted_h_sweep_present") is False, "four-history recurrent source-law screen unexpectedly claims accepted h-sweep")
    checks.check(four_history_source_law.get("order_terminal_intersection_present") is False, "four-history recurrent source-law screen unexpectedly has an order/terminal intersection")
    checks.check(four_history_source_law.get("row_count") == 4, "four-history recurrent source-law screen row count changed")
    checks.check(four_history_source_law.get("predictor_law_count") == 4, "four-history recurrent source-law screen law count changed")
    checks.check(four_history_source_law.get("four_history_law_count") == 4, "four-history recurrent source-law screen four-history count changed")
    checks.check(four_history_source_law.get("four_history_source_law_trajectory_screen_present") is True, "four-history recurrent source-law screen lost trajectory-screen marker")
    checks.check(four_history_source_law.get("terminal_closed_row_count") == 0, "four-history recurrent source-law screen unexpectedly closes terminal velocity")
    checks.check(four_history_source_law.get("smooth_order_ok_count") == 2, "four-history recurrent source-law screen smooth-order count changed")
    checks.check(four_history_source_law.get("terminal_closure_requires_order_collapse") is False, "four-history recurrent source-law screen order-collapse marker changed")
    checks.check(four_history_source_law.get("best_terminal_law") == "recurrent_fourhistory_velocity_terminal_source01historyslopejerksnap_z", "four-history recurrent source-law screen best terminal law changed")
    checks.check(2.9e-7 < as_float(four_history_source_law, "best_terminal_velocity", 0.0) < 3.0e-7, "four-history recurrent source-law screen best terminal velocity changed")
    checks.check(5.33 < as_float(four_history_source_law, "best_smooth_order_min_order", 0.0) < 5.36, "four-history recurrent source-law screen best smooth order changed")

    checks.check(nonlinear_history_source_law.get("full_tfe_stage_replacement") is False, "nonlinear-history recurrent source-law screen unexpectedly claims full TFE")
    checks.check(nonlinear_history_source_law.get("accepted_h_sweep_present") is False, "nonlinear-history recurrent source-law screen unexpectedly claims accepted h-sweep")
    checks.check(nonlinear_history_source_law.get("order_terminal_intersection_present") is False, "nonlinear-history recurrent source-law screen unexpectedly has an order/terminal intersection")
    checks.check(nonlinear_history_source_law.get("row_count") == 5, "nonlinear-history recurrent source-law screen row count changed")
    checks.check(nonlinear_history_source_law.get("predictor_law_count") == 5, "nonlinear-history recurrent source-law screen law count changed")
    checks.check(nonlinear_history_source_law.get("nonlinear_history_law_count") == 5, "nonlinear-history recurrent source-law screen nonlinear-history count changed")
    checks.check(nonlinear_history_source_law.get("nonlinear_history_source_law_trajectory_screen_present") is True, "nonlinear-history recurrent source-law screen lost trajectory-screen marker")
    checks.check(nonlinear_history_source_law.get("terminal_closed_row_count") == 0, "nonlinear-history recurrent source-law screen unexpectedly closes terminal velocity")
    checks.check(nonlinear_history_source_law.get("smooth_order_ok_count") == 0, "nonlinear-history recurrent source-law screen unexpectedly meets smooth-order floor")
    checks.check(nonlinear_history_source_law.get("terminal_closure_requires_order_collapse") is False, "nonlinear-history recurrent source-law screen order-collapse marker changed")
    checks.check(nonlinear_history_source_law.get("best_terminal_law") == "recurrent_nonlinearhistory_velocity_terminal_source0historyhadamard_z", "nonlinear-history recurrent source-law screen best terminal law changed")
    checks.check(1.9e-7 < as_float(nonlinear_history_source_law, "best_terminal_velocity", 0.0) < 2.0e-7, "nonlinear-history recurrent source-law screen best terminal velocity changed")
    checks.check(3.50 < as_float(nonlinear_history_source_law, "best_smooth_order_min_order", 0.0) < 3.55, "nonlinear-history recurrent source-law screen best smooth order changed")

    checks.check(source_law_final_retain.get("full_tfe_stage_replacement") is False, "recurrent source-law final-retain boundary unexpectedly claims full TFE")
    checks.check(source_law_final_retain.get("accepted_h_sweep_present") is False, "recurrent source-law final-retain boundary unexpectedly claims accepted h-sweep")
    checks.check(source_law_final_retain.get("order_terminal_intersection_present") is False, "recurrent source-law final-retain boundary unexpectedly has an order/terminal intersection")
    checks.check(source_law_final_retain.get("terminal_closure_requires_order_collapse") is True, "recurrent source-law final-retain boundary lost order-collapse marker")
    checks.check(source_law_final_retain.get("row_count") == 16, "recurrent source-law final-retain boundary row count changed")
    checks.check(source_law_final_retain.get("terminal_closed_row_count") == 4, "recurrent source-law final-retain boundary terminal-closed count changed")
    checks.check(source_law_final_retain.get("smooth_order_ok_count") == 0, "recurrent source-law final-retain boundary smooth-order count changed")
    checks.check(as_float(source_law_final_retain, "best_terminal_velocity", 1.0) < 4.0e-13, "recurrent source-law final-retain boundary best terminal velocity changed")
    checks.check(as_float(source_law_final_retain, "best_terminal_min_order", 10.0) < 5.0, "recurrent source-law final-retain boundary no longer records terminal-branch order collapse")
    checks.check(4.50 < as_float(source_law_final_retain, "best_smooth_order_min_order", 0.0) < 4.52, "recurrent source-law final-retain boundary best smooth order changed")
    checks.check(as_float(source_law_final_retain, "best_smooth_order_terminal_velocity", 0.0) > 5.0e-10, "recurrent source-law final-retain boundary no longer records open-terminal best-order branch")

    checks.check(acceptance.get("full_tfe_stage_replacement") is False, "acceptance matrix unexpectedly claims full TFE")
    checks.check(acceptance.get("accepted_candidate_count") == 0, "acceptance matrix unexpectedly has an accepted candidate")
    checks.check(acceptance.get("best_order_preserving_source_free_candidate") == "source_free_mean_blend_trajectory_best_alpha", "best order-preserving candidate changed")
    checks.check(acceptance.get("best_terminal_velocity_candidate") == "source_free_final_stage_velocity_closure", "best terminal-velocity candidate changed")

    for audit, label, expected_rows in [
        (stage2_gradient, "stage2 scalar-gradient differential", 8),
        (stage2_matrix, "stage2 matrix-gradient differential", 32),
    ]:
        checks.check(audit.get("full_tfe_stage_replacement") is False, f"{label} unexpectedly claims full TFE")
        checks.check(audit.get("accepted_h_sweep_present") is False, f"{label} unexpectedly claims accepted h-sweep")
        checks.check(audit.get("row_count") == expected_rows, f"{label} row count changed")
        checks.check(audit.get("span_row_count") == 0, f"{label} unexpectedly spans terminal bridge")
        checks.check(audit.get("any_candidate_spans_terminal_bridge") is False, f"{label} unexpectedly spans terminal bridge")
        checks.check(0.85 < as_float(audit, "best_projection_relative_residual") < 0.95, f"{label} best residual changed")
        checks.check(audit.get("best_missing_direction_dominant_variable_family") == "translation_velocity_v", f"{label} dominant missing variable changed")
        checks.check(as_float(audit, "best_missing_direction_stage2_fraction") > 0.99, f"{label} missing direction no longer stage2-local")
    checks.check(stage2_translation_matrix.get("full_tfe_stage_replacement") is False, "stage2 translation-velocity matrix differential unexpectedly claims full TFE")
    checks.check(stage2_translation_matrix.get("accepted_h_sweep_present") is False, "stage2 translation-velocity matrix differential unexpectedly claims accepted h-sweep")
    checks.check(stage2_translation_matrix.get("row_count") == 40, "stage2 translation-velocity matrix differential row count changed")
    checks.check(stage2_translation_matrix.get("matrix_law_count") == 10, "stage2 translation-velocity matrix differential law count changed")
    checks.check(stage2_translation_matrix.get("span_row_count") == 0, "stage2 translation-velocity matrix differential unexpectedly spans terminal bridge")
    checks.check(stage2_translation_matrix.get("any_candidate_spans_terminal_bridge") is False, "stage2 translation-velocity matrix differential unexpectedly spans terminal bridge")
    checks.check(stage2_translation_matrix.get("uses_stage2_translation_velocity_matrix_feature") is True, "stage2 translation-velocity matrix differential lost translation-velocity marker")
    checks.check(0.65 < as_float(stage2_translation_matrix, "best_projection_relative_residual") < 0.70, "stage2 translation-velocity matrix differential best residual changed")
    checks.check(stage2_translation_matrix.get("best_missing_direction_dominant_variable_family") == "angular_velocity_w", "stage2 translation-velocity matrix differential dominant missing variable changed")
    checks.check(as_float(stage2_translation_matrix, "best_missing_direction_stage2_fraction") > 0.93, "stage2 translation-velocity matrix differential missing direction no longer stage2-local")
    checks.check(stage2_coupled_matrix.get("full_tfe_stage_replacement") is False, "stage2 translation/angular coupled matrix differential unexpectedly claims full TFE")
    checks.check(stage2_coupled_matrix.get("accepted_h_sweep_present") is False, "stage2 translation/angular coupled matrix differential unexpectedly claims accepted h-sweep")
    checks.check(stage2_coupled_matrix.get("row_count") == 48, "stage2 translation/angular coupled matrix differential row count changed")
    checks.check(stage2_coupled_matrix.get("matrix_law_count") == 12, "stage2 translation/angular coupled matrix differential law count changed")
    checks.check(stage2_coupled_matrix.get("span_row_count") == 0, "stage2 translation/angular coupled matrix differential unexpectedly spans terminal bridge")
    checks.check(stage2_coupled_matrix.get("any_candidate_spans_terminal_bridge") is False, "stage2 translation/angular coupled matrix differential unexpectedly spans terminal bridge")
    checks.check(stage2_coupled_matrix.get("uses_stage2_translation_angular_coupled_matrix_feature") is True, "stage2 translation/angular coupled matrix differential lost coupled marker")
    checks.check(0.73 < as_float(stage2_coupled_matrix, "best_projection_relative_residual") < 0.75, "stage2 translation/angular coupled matrix differential best residual changed")
    checks.check(stage2_coupled_matrix.get("best_missing_direction_dominant_variable_family") == "translation_velocity_v", "stage2 translation/angular coupled matrix differential dominant missing variable changed")
    checks.check(as_float(stage2_coupled_matrix, "best_missing_direction_stage2_fraction") > 0.94, "stage2 translation/angular coupled matrix differential missing direction no longer stage2-local")
    checks.check(stage2_dictionary.get("full_tfe_stage_replacement") is False, "stage2 feature dictionary unexpectedly claims full TFE")
    checks.check(stage2_dictionary.get("accepted_h_sweep_present") is False, "stage2 feature dictionary unexpectedly claims accepted h-sweep")
    checks.check(stage2_dictionary.get("row_count") == 12, "stage2 feature dictionary row count changed")
    checks.check(stage2_dictionary.get("span_row_count") == 8, "stage2 feature dictionary span count changed")
    checks.check(stage2_dictionary.get("combined_all_dictionary_span_count") == 2, "stage2 feature dictionary combined span count changed")
    checks.check(stage2_dictionary.get("all_combined_all_dictionary_spans_terminal_bridge") is True, "stage2 feature dictionary combined span flag changed")
    checks.check(stage2_dictionary.get("best_dictionary_group") == "stage2_matrix_core", "stage2 feature dictionary best group changed")
    checks.check(as_float(stage2_dictionary, "best_projection_relative_residual") < 1.0e-12, "stage2 feature dictionary best residual changed")
    checks.check(stage2_dictionary.get("target_free_dictionary") is True, "stage2 feature dictionary lost target-free marker")
    checks.check(stage2_dictionary.get("target_jacobian_used_for_formula") is False, "stage2 feature dictionary unexpectedly uses target Jacobian")
    checks.check(stage2_dictionary.get("target_direction_oracle_used") is False, "stage2 feature dictionary unexpectedly uses target direction")
    checks.check(stage2_dictionary.get("formula_coefficient_law_present") is False, "stage2 feature dictionary overclaims coefficient law")
    checks.check("coefficient/selection law" in stage2_dictionary.get("next_repair_target", ""), "stage2 feature dictionary next target changed")
    checks.check(stage2_coefficient.get("full_tfe_stage_replacement") is False, "stage2 coefficient-law screen unexpectedly claims full TFE")
    checks.check(stage2_coefficient.get("accepted_h_sweep_present") is False, "stage2 coefficient-law screen unexpectedly claims accepted h-sweep")
    checks.check(stage2_coefficient.get("row_count") == 60, "stage2 coefficient-law screen row count changed")
    checks.check(stage2_coefficient.get("span_row_count") == 0, "stage2 coefficient-law screen unexpectedly spans terminal bridge")
    checks.check(stage2_coefficient.get("coefficient_law_count") == 5, "stage2 coefficient-law screen law count changed")
    checks.check(stage2_coefficient.get("dictionary_group_count") == 6, "stage2 coefficient-law screen dictionary count changed")
    checks.check(stage2_coefficient.get("any_coefficient_law_spans_terminal_bridge") is False, "stage2 coefficient-law screen span marker changed")
    checks.check(stage2_coefficient.get("best_dictionary_group") == "combined_all_target_free_dictionary", "stage2 coefficient-law screen best dictionary changed")
    checks.check(stage2_coefficient.get("best_coefficient_law") == "closure_delta_norm_weights", "stage2 coefficient-law screen best law changed")
    checks.check(0.55 < as_float(stage2_coefficient, "best_projection_relative_residual") < 0.57, "stage2 coefficient-law screen best residual changed")
    checks.check(stage2_coefficient.get("target_free_coefficient_law") is True, "stage2 coefficient-law screen lost target-free marker")
    checks.check(stage2_coefficient.get("bounded_coefficient_law_present") is True, "stage2 coefficient-law screen lost bounded marker")
    checks.check(stage2_coefficient.get("coefficient_derivative_included") is False, "stage2 coefficient-law screen unexpectedly includes derivatives")
    checks.check(stage2_coefficient.get("candidate_jacobian_used_for_coefficient") is False, "stage2 coefficient-law screen unexpectedly uses candidate-Jacobian coefficient oracle")
    checks.check(stage2_coefficient.get("target_jacobian_used_for_formula") is False, "stage2 coefficient-law screen unexpectedly uses target Jacobian")
    checks.check(stage2_coefficient.get("target_direction_oracle_used") is False, "stage2 coefficient-law screen unexpectedly uses target direction")
    checks.check("state-dependent bounded coefficients" in stage2_coefficient.get("next_repair_target", ""), "stage2 coefficient-law screen next target changed")
    checks.check(stage2_state_coefficient.get("full_tfe_stage_replacement") is False, "stage2 state-feature coefficient-derivative screen unexpectedly claims full TFE")
    checks.check(stage2_state_coefficient.get("accepted_h_sweep_present") is False, "stage2 state-feature coefficient-derivative screen unexpectedly accepts h-sweep")
    checks.check(stage2_state_coefficient.get("row_count") == 36, "stage2 state-feature coefficient-derivative screen row count changed")
    checks.check(stage2_state_coefficient.get("span_row_count") == 0, "stage2 state-feature coefficient-derivative screen span count changed")
    checks.check(stage2_state_coefficient.get("coefficient_law_count") == 3, "stage2 state-feature coefficient-derivative screen law count changed")
    checks.check(stage2_state_coefficient.get("dictionary_group_count") == 6, "stage2 state-feature coefficient-derivative screen dictionary count changed")
    checks.check(stage2_state_coefficient.get("any_coefficient_derivative_law_spans_terminal_bridge") is False, "stage2 state-feature coefficient-derivative screen span marker changed")
    checks.check(stage2_state_coefficient.get("best_dictionary_group") == "stage2_matrix_core", "stage2 state-feature coefficient-derivative screen best dictionary changed")
    checks.check(stage2_state_coefficient.get("best_coefficient_law") == "inverse_closure_delta_norm_weights_derivative", "stage2 state-feature coefficient-derivative screen best law changed")
    checks.check(0.58 < as_float(stage2_state_coefficient, "best_projection_relative_residual") < 0.60, "stage2 state-feature coefficient-derivative screen best residual changed")
    checks.check(stage2_state_coefficient.get("target_free_coefficient_derivative") is True, "stage2 state-feature coefficient-derivative screen lost target-free marker")
    checks.check(stage2_state_coefficient.get("coefficient_derivative_included") is True, "stage2 state-feature coefficient-derivative screen lost derivative marker")
    checks.check(stage2_state_coefficient.get("target_jacobian_used_for_formula") is False, "stage2 state-feature coefficient-derivative screen unexpectedly uses target Jacobian")
    checks.check(stage2_state_coefficient.get("target_direction_oracle_used") is False, "stage2 state-feature coefficient-derivative screen unexpectedly uses target direction")
    checks.check("richer state-dependent coefficient features" in stage2_state_coefficient.get("next_repair_target", ""), "stage2 state-feature coefficient-derivative screen next target changed")
    checks.check(hscaled_endpoint_pose.get("full_tfe_stage_replacement") is False, "h-adaptive endpoint-pose predictor unexpectedly claims full TFE")
    checks.check(hscaled_endpoint_pose.get("accepted_h_sweep_present") is False, "h-adaptive endpoint-pose predictor unexpectedly accepts an h-sweep")
    checks.check(hscaled_endpoint_pose.get("row_count") == 12, "h-adaptive endpoint-pose predictor row count changed")
    checks.check(hscaled_endpoint_pose.get("predictor_law_count") == 4, "h-adaptive endpoint-pose predictor law count changed")
    checks.check(hscaled_endpoint_pose.get("hscaled_endpoint_pose_velocity_predictor") is True, "h-adaptive endpoint-pose predictor lost h-scaled marker")
    checks.check(hscaled_endpoint_pose.get("projection_used") is False, "h-adaptive endpoint-pose predictor unexpectedly uses projection")
    checks.check(hscaled_endpoint_pose.get("terminal_row_replacement_used") is False, "h-adaptive endpoint-pose predictor unexpectedly replaces terminal rows")
    checks.check(hscaled_endpoint_pose.get("terminal_velocity_closed") is False, "h-adaptive endpoint-pose predictor unexpectedly closes all terminal velocities")
    checks.check(hscaled_endpoint_pose.get("smooth_order_ok") is False, "h-adaptive endpoint-pose predictor unexpectedly reaches smooth order")
    checks.check(3.50 < as_float(hscaled_endpoint_pose, "min_position_order") < 3.54, "h-adaptive endpoint-pose predictor position order changed")
    checks.check(4.80 < as_float(hscaled_endpoint_pose, "min_velocity_order") < 4.90, "h-adaptive endpoint-pose predictor velocity order changed")
    checks.check(as_float(hscaled_endpoint_pose, "max_raw_terminal_endpoint_velocity_constraint_norm") > 1.0e-8, "h-adaptive endpoint-pose predictor no longer records open-terminal branch")
    hscaled_law = hscaled_endpoint_pose.get("laws", {}).get(
        "stage02_convex_pose_velocity_extrapolate_0p00001_0p00002_hpow_m1_z", {}
    )
    hscaled_case = hscaled_law.get("cases", {}).get("cylindrical_smooth", {})
    checks.check(as_float(hscaled_law, "max_terminal_velocity", 1.0) < 1.0e-12, "h-adaptive endpoint-pose hpow_m1 no longer closes terminal velocity")
    checks.check(as_float(hscaled_case, "position_order", 10.0) < 4.0, "h-adaptive endpoint-pose hpow_m1 position order no longer records limitation")
    checks.check(as_float(hscaled_case, "velocity_order", 10.0) < 5.0, "h-adaptive endpoint-pose hpow_m1 velocity order no longer records limitation")
    checks.check(hscaled_response.get("row_count") == 4, "h-adaptive endpoint-pose response row count changed")
    checks.check(hscaled_response.get("predictor_law_count") == 4, "h-adaptive endpoint-pose response law count changed")
    checks.check(hscaled_response.get("terminal_closed_row_count") == 1, "h-adaptive endpoint-pose response terminal-closed count changed")
    checks.check(hscaled_response.get("smooth_order_ok_count") == 0, "h-adaptive endpoint-pose response smooth-order count changed")
    checks.check(hscaled_response.get("accepted_candidate_count") == 0, "h-adaptive endpoint-pose response unexpectedly has accepted candidates")
    checks.check(hscaled_response.get("order_terminal_intersection_present") is False, "h-adaptive endpoint-pose response unexpectedly has intersection")
    checks.check(hscaled_response.get("terminal_closure_requires_order_collapse") is True, "h-adaptive endpoint-pose response lost order-collapse marker")
    checks.check(hscaled_response.get("full_tfe_stage_replacement") is False, "h-adaptive endpoint-pose response unexpectedly claims full TFE")
    checks.check(as_float(hscaled_response, "best_terminal_velocity", 1.0) < 1.0e-12, "h-adaptive endpoint-pose response best terminal velocity changed")
    checks.check(1.45 < as_float(hscaled_response, "best_terminal_closed_gap_to_order_floor") < 1.50, "h-adaptive endpoint-pose response order-floor gap changed")
    checks.check(candidate_frontier.get("family_count") == 11, "candidate frontier family count changed")
    checks.check(candidate_frontier.get("total_candidate_row_count") == 115, "candidate frontier candidate row count changed")
    checks.check(candidate_frontier.get("terminal_closed_candidate_count") == 35, "candidate frontier terminal-closed count changed")
    checks.check(candidate_frontier.get("smooth_order_candidate_count") == 17, "candidate frontier smooth-order count changed")
    checks.check(candidate_frontier.get("order_terminal_intersection_count") == 0, "candidate frontier unexpectedly has intersections")
    checks.check(candidate_frontier.get("family_intersection_count") == 0, "candidate frontier unexpectedly has family intersections")
    checks.check(candidate_frontier.get("best_terminal_family") == "recurrent_component_feedback_gain_boundary", "candidate frontier best terminal family changed")
    checks.check(candidate_frontier.get("best_order_family") == "recurrent_source_law_trajectory_screen", "candidate frontier best order family changed")
    checks.check(candidate_frontier.get("accepted_h_sweep_present") is False, "candidate frontier unexpectedly has accepted h-sweep")
    checks.check(candidate_frontier.get("full_tfe_stage_replacement") is False, "candidate frontier unexpectedly claims full TFE")
    checks.check(bounded_requirement.get("requirement_row_count") == 7, "bounded tangent requirement row count changed")
    checks.check(bounded_requirement.get("frontier_order_terminal_intersection_count") == 0, "bounded tangent requirement frontier count changed")
    checks.check(bounded_requirement.get("row_space_oracle_span_count") == 36, "bounded tangent requirement oracle span count changed")
    checks.check(bounded_requirement.get("row_space_target_free_span_count") == 0, "bounded tangent requirement target-free row-space count changed")
    checks.check(bounded_requirement.get("target_free_formula_span_count") == 0, "bounded tangent requirement target-free formula count changed")
    checks.check(bounded_requirement.get("weak_row_structure_span_count") == 0, "bounded tangent requirement weak-row count changed")
    checks.check(bounded_requirement.get("bounded_gradient_practical_cap_spanning_row_count") == 12, "bounded tangent requirement practical-cap span count changed")
    checks.check(as_float(bounded_requirement, "bounded_formula_min_all_span_cap") > 1e21, "bounded tangent requirement bounded-formula cap changed")
    checks.check(bounded_requirement.get("accepted_h_sweep_present") is False, "bounded tangent requirement unexpectedly has accepted h-sweep")
    checks.check(bounded_requirement.get("full_tfe_stage_replacement") is False, "bounded tangent requirement unexpectedly claims full TFE")
    checks.check("stage-local weak-row tangent" in bounded_requirement.get("next_repair_contract", ""), "bounded tangent requirement target changed")

    checks.check(compression.get("accepted_h_sweep_present") is False, "velocity compression unexpectedly has accepted h-sweep")
    checks.check(compression.get("full_tfe_stage_replacement") is False, "velocity compression unexpectedly claims full TFE")
    checks.check(compression.get("row_space_compression_probe_row_count") == 36, "row-space compression row count changed")
    checks.check(compression.get("row_space_compression_probe_spanning_row_count") == 0, "row-space compression unexpectedly spans")
    checks.check(0.7 < as_float(compression, "row_space_compression_probe_best_projection_relative_residual") < 0.8, "row-space best residual changed")
    checks.check(0.9 < as_float(compression, "row_space_compression_probe_best_nonfinal_projection_relative_residual") < 1.1, "row-space best non-final residual changed")
    checks.check(compression.get("row_space_coefficient_derivative_probe_row_count") == 36, "row-space coefficient-derivative row count changed")
    checks.check(compression.get("row_space_coefficient_derivative_probe_spanning_row_count") == 36, "row-space coefficient-derivative oracle span count changed")
    checks.check(compression.get("row_space_coefficient_derivative_probe_value_balanced_spanning_row_count") == 24, "row-space coefficient-derivative value-balanced span count changed")
    checks.check(as_float(compression, "row_space_coefficient_derivative_probe_best_projection_relative_residual") < 1e-12, "row-space coefficient-derivative best residual changed")
    checks.check(compression.get("row_space_coefficient_derivative_probe_target_direction_oracle_used") is True, "row-space coefficient-derivative lost oracle marker")
    checks.check(compression.get("row_space_coefficient_derivative_probe_coefficient_derivative_included") is True, "row-space coefficient-derivative lost derivative marker")
    checks.check(compression.get("weak_row_structure_capacity_probe_row_count") == 216, "weak-row structure row count changed")
    checks.check(compression.get("weak_row_structure_capacity_probe_spanning_row_count") == 0, "weak-row structure unexpectedly spans")
    for key in [
        "target_free_formula_probe_spanning_row_count",
        "direction_capacity_probe_nonfinal_spanning_row_count",
        "nonlinear_capacity_probe_spanning_row_count",
        "higher_order_capacity_probe_spanning_row_count",
        "history_capacity_probe_spanning_row_count",
        "multi_step_history_capacity_probe_spanning_row_count",
        "recurrent_history_capacity_probe_spanning_row_count",
    ]:
        checks.check(compression.get(key) == 0, f"{key} unexpectedly nonzero")

    return {
        "terminal_closed": as_float(final_stage, "max_raw_terminal_endpoint_velocity_constraint_norm", 1.0) < 1e-12,
        "order_closure_intersection_present": blend.get("order_and_terminal_intersection_present"),
        "accepted_candidate_count": acceptance.get("accepted_candidate_count"),
        "row_space_rows": compression.get("row_space_compression_probe_row_count"),
        "row_space_spans": compression.get("row_space_compression_probe_spanning_row_count"),
        "row_space_coefficient_derivative_spans": compression.get("row_space_coefficient_derivative_probe_spanning_row_count"),
        "row_space_coefficient_derivative_value_spans": compression.get(
            "row_space_coefficient_derivative_probe_value_balanced_spanning_row_count"
        ),
        "bounded_requirement_rows": bounded_requirement.get("requirement_row_count"),
        "bounded_requirement_target_free_formula_spans": bounded_requirement.get("target_free_formula_span_count"),
        "bounded_requirement_oracle_spans": bounded_requirement.get("row_space_oracle_span_count"),
        "bounded_requirement_practical_cap_spans": bounded_requirement.get(
            "bounded_gradient_practical_cap_spanning_row_count"
        ),
        "stage2_dictionary_rows": stage2_dictionary.get("row_count"),
        "stage2_dictionary_spans": stage2_dictionary.get("span_row_count"),
        "stage2_dictionary_combined_spans": stage2_dictionary.get("combined_all_dictionary_span_count"),
        "stage2_coefficient_rows": stage2_coefficient.get("row_count"),
        "stage2_coefficient_spans": stage2_coefficient.get("span_row_count"),
        "stage2_coefficient_best_residual": stage2_coefficient.get("best_projection_relative_residual"),
        "stage2_coefficient_best_law": stage2_coefficient.get("best_coefficient_law"),
        "stage2_state_coefficient_rows": stage2_state_coefficient.get("row_count"),
        "stage2_state_coefficient_spans": stage2_state_coefficient.get("span_row_count"),
        "stage2_state_coefficient_best_residual": stage2_state_coefficient.get("best_projection_relative_residual"),
        "stage2_state_coefficient_best_law": stage2_state_coefficient.get("best_coefficient_law"),
        "four_history_source_law_rows": four_history_source_law.get("row_count"),
        "four_history_source_law_terminal_closed": four_history_source_law.get("terminal_closed_row_count"),
        "four_history_source_law_smooth_order": four_history_source_law.get("smooth_order_ok_count"),
        "four_history_source_law_best_terminal_velocity": four_history_source_law.get("best_terminal_velocity"),
        "four_history_source_law_best_order": four_history_source_law.get("best_smooth_order_min_order"),
        "weak_row_structure_spans": compression.get("weak_row_structure_capacity_probe_spanning_row_count"),
        "best_row_space_residual": compression.get("row_space_compression_probe_best_projection_relative_residual"),
        "best_row_space_coefficient_derivative_residual": compression.get(
            "row_space_coefficient_derivative_probe_best_projection_relative_residual"
        ),
        "best_nonfinal_residual": compression.get("row_space_compression_probe_best_nonfinal_projection_relative_residual"),
        "next_repair_target": (
            "derive a revised analytical weak-row formula or nonlinear recurrent history source law for the "
            "independent lower-pair closure"
        ),
    }


def main() -> int:
    checks = Checks()
    try:
        summary = read_summary()
        check_required_files(checks)
        check_gap_ledger(checks)
        report = check_summary_boundary(checks, summary)
    except Exception as exc:  # noqa: BLE001 - command-line validator reports fatal read/parse issues.
        print("v047 full-TFE gap validation: FAIL")
        print(f"fatal={exc}")
        return 1

    if checks.errors:
        print("v047 full-TFE gap validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("v047 full-TFE gap validation: PASS")
    print(f"asme_gate_status={summary['asme_gate']['status']}")
    print(f"terminal_closed={report['terminal_closed']}")
    print(f"order_closure_intersection_present={report['order_closure_intersection_present']}")
    print(f"accepted_candidate_count={report['accepted_candidate_count']}")
    print(f"row_space_compression_rows={report['row_space_rows']}")
    print(f"row_space_spans={report['row_space_spans']}")
    print(f"row_space_coefficient_derivative_spans={report['row_space_coefficient_derivative_spans']}")
    print(f"row_space_coefficient_derivative_value_spans={report['row_space_coefficient_derivative_value_spans']}")
    print(f"bounded_requirement_rows={report['bounded_requirement_rows']}")
    print(f"bounded_requirement_target_free_formula_spans={report['bounded_requirement_target_free_formula_spans']}")
    print(f"bounded_requirement_oracle_spans={report['bounded_requirement_oracle_spans']}")
    print(f"bounded_requirement_practical_cap_spans={report['bounded_requirement_practical_cap_spans']}")
    print(f"stage2_dictionary_rows={report['stage2_dictionary_rows']}")
    print(f"stage2_dictionary_spans={report['stage2_dictionary_spans']}")
    print(f"stage2_dictionary_combined_spans={report['stage2_dictionary_combined_spans']}")
    print(f"stage2_coefficient_rows={report['stage2_coefficient_rows']}")
    print(f"stage2_coefficient_spans={report['stage2_coefficient_spans']}")
    print(f"stage2_coefficient_best_residual={float(report['stage2_coefficient_best_residual']):.3e}")
    print(f"stage2_coefficient_best_law={report['stage2_coefficient_best_law']}")
    print(f"stage2_state_coefficient_rows={report['stage2_state_coefficient_rows']}")
    print(f"stage2_state_coefficient_spans={report['stage2_state_coefficient_spans']}")
    print(f"stage2_state_coefficient_best_residual={float(report['stage2_state_coefficient_best_residual']):.3e}")
    print(f"stage2_state_coefficient_best_law={report['stage2_state_coefficient_best_law']}")
    print(f"four_history_source_law_rows={report['four_history_source_law_rows']}")
    print(f"four_history_source_law_terminal_closed={report['four_history_source_law_terminal_closed']}")
    print(f"four_history_source_law_smooth_order={report['four_history_source_law_smooth_order']}")
    print(f"four_history_source_law_best_terminal_velocity={float(report['four_history_source_law_best_terminal_velocity']):.3e}")
    print(f"four_history_source_law_best_order={float(report['four_history_source_law_best_order']):.3f}")
    print(f"weak_row_structure_spans={report['weak_row_structure_spans']}")
    print(f"best_row_space_residual={float(report['best_row_space_residual']):.3e}")
    print(f"best_row_space_coefficient_derivative_residual={float(report['best_row_space_coefficient_derivative_residual']):.3e}")
    print(f"best_nonfinal_residual={float(report['best_nonfinal_residual']):.3e}")
    print("full_tfe_stage_replacement=False")
    print(f"next_repair_target={report['next_repair_target']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
