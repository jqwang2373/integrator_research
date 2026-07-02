#!/usr/bin/env python3
"""Read-only guard for the v047 full-TFE repair specification."""

from __future__ import annotations

import json
import sys
from pathlib import Path


PIPELINE = Path(__file__).resolve().parent
RESULTS = PIPELINE / "results"
SUMMARY = RESULTS / "summary_v047.json"
SPEC = PIPELINE / "FULL_TFE_REPAIR_SPEC.md"
GAP_LEDGER = PIPELINE / "FULL_TFE_REPLACEMENT_GAP_LEDGER.md"
RUN_SCRIPT = PIPELINE / "run_v047.py"

EXPECTED_ASME_STATUS = "four_asme_method_rows_accepted_projection_sharp_sparse_caveats"


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def as_float(data: dict, key: str, default: float = 0.0) -> float:
    try:
        return float(data.get(key, default))
    except (TypeError, ValueError):
        return default


def check_spec_text(checks: Checks, spec: str) -> None:
    required = [
        "paper_tfe_lower_pair_source_free_recurrent_weak_closure_rows_jax",
        "residual_cylindrical_chain_endpoint_tfe_paper_lower_pair_source_free_recurrent_weak_closure_candidate",
        "132",
        "24",
        "16",
        "8",
        "coefficient-gradient closure",
        "endpoint-boundary source data",
        "terminal-row replacement",
        "output projection",
        "target-direction oracle",
        "h=[0.04,0.02,0.01]",
        "h=0.005",
        "1e-12",
        "5.0",
        "full_tfe_stage_replacement=false",
        "V047_TARGET_AUDIT=lower_pair_recurrent_weak_closure_smoke",
        "V047_TARGET_AUDIT=lower_pair_recurrent_weak_closure_trajectory_smoke",
        "V047_TARGET_AUDIT=lower_pair_recurrent_weak_closure_h_sweep_smoke",
        "V047_TARGET_AUDIT=lower_pair_recurrent_terminal_blend_one_step_smoke",
        "V047_TARGET_AUDIT=lower_pair_recurrent_terminal_blend_h_sweep_smoke",
        "V047_RECURRENT_WEAK_SMOKE_NUMERIC=1",
        "V047_RECURRENT_WEAK_H_SWEEP_FULL=1",
        "V047_RECURRENT_TERMINAL_BLEND_H_SWEEP_FULL=1",
        "V047_RECURRENT_TERMINAL_BLEND_H_SWEEP_CASES=cylindrical_smooth",
        "diagnostic_smoke_only=true",
        "bounded_h_sweep_smoke_present=true",
        "trajectory_h_sweep_present=false",
        "accepted_h_sweep_present=false",
        "terminal_velocity_closed=false",
        "smooth_order_ok=false",
        "lower_pair_source_free_near_final_beta_boundary",
        "cylindrical_chain_endpoint_tfe_paper_lower_pair_source_free_near_final_beta_boundary_audit",
        "near_final_collapse_confirmed=true",
        "0.99999999",
        "1.255e-12",
        "lower_pair_recurrent_feedback_gain_boundary",
        "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_feedback_gain_boundary_audit",
        "terminal_closure_requires_order_collapse=true",
        "feedback_gain=12",
        "1.036e-16",
        "lower_pair_recurrent_component_feedback_gain_boundary",
        "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_component_feedback_gain_boundary_audit",
        "7.538e-17",
        "lower_pair_recurrent_hscaled_feedback_gain_boundary",
        "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_hscaled_feedback_gain_boundary_audit",
        "4.711",
        "1.316e-08",
        "lower_pair_recurrent_source_law_trajectory_screen",
        "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_source_law_trajectory_screen_audit",
        "terminal_closed_row_count=0",
        "smooth_order_ok_count=5",
        "2.016e-07",
        "lower_pair_recurrent_three_history_source_law_trajectory_screen",
        "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_three_history_source_law_trajectory_screen_audit",
        "V047_TARGET_AUDIT=lower_pair_recurrent_three_history_source_law_trajectory_screen",
        "V047_RECURRENT_THREE_HISTORY_SOURCE_LAW_SCREEN_LAWS",
        "three_zero_initial_blocks_then_stage0_source_estimate_shift_register",
        "recurrent_threehistory_velocity_terminal_source0ab4_z",
        "recurrent_threehistory_velocity_terminal_source01historyslopejerk_z",
        "three-history recurrent source law",
        "2.923e-07",
        "5.345",
        "lower_pair_recurrent_four_history_source_law_trajectory_screen",
        "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_four_history_source_law_trajectory_screen_audit",
        "V047_TARGET_AUDIT=lower_pair_recurrent_four_history_source_law_trajectory_screen",
        "V047_RECURRENT_FOUR_HISTORY_SOURCE_LAW_SCREEN_LAWS",
        "four_zero_initial_blocks_then_stage0_source_estimate_shift_register",
        "recurrent_fourhistory_velocity_terminal_source0ab5_z",
        "recurrent_fourhistory_velocity_terminal_source01historyslopejerksnap_z",
        "four-history recurrent source law",
        "four_history_source_law_trajectory_screen_present",
        "2.950e-07",
        "5.342",
        "lower_pair_recurrent_nonlinear_history_source_law_trajectory_screen",
        "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_nonlinear_history_source_law_trajectory_screen_audit",
        "V047_TARGET_AUDIT=lower_pair_recurrent_nonlinear_history_source_law_trajectory_screen",
        "V047_RECURRENT_NONLINEAR_HISTORY_SOURCE_LAW_SCREEN_LAWS",
        "two_zero_initial_blocks_then_stage0_source_estimate_shift_register",
        "recurrent_nonlinearhistory_velocity_terminal_source0historyhadamard_z",
        "nonlinear-history recurrent source law",
        "1.954e-07",
        "3.525",
        "row-space coefficient-derivative",
        "cylindrical_chain_endpoint_tfe_paper_lower_pair_velocity_compression_row_space_coefficient_derivative_audit",
        "value-balanced spans 24",
        "target-direction oracle",
        "6.777e+18",
        "bounded tangent requirement audit",
        "cylindrical_chain_endpoint_tfe_paper_lower_pair_bounded_tangent_requirement_audit",
        "V047_TARGET_AUDIT=lower_pair_bounded_tangent_requirement_audit",
        "requirement_row_count=7",
        "target_free_formula_span_count=0",
        "row_space_oracle_span_count=36",
        "bounded_gradient_practical_cap_spanning_row_count=12",
        "lower_pair_recurrent_source_law_final_retain_boundary",
        "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_source_law_final_retain_boundary_audit",
        "terminal_closed_row_count=4",
        "smooth_order_ok_count=0",
        "3.171e-13",
        "4.510",
        "lower_pair_recurrent_stage2_translation_velocity_matrix_differential_audit",
        "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_translation_velocity_matrix_differential_audit",
        "stage2_translation_velocity_symmetric_broadcast_feature",
        "0.671049",
        "angular_velocity_w",
        "lower_pair_recurrent_stage2_translation_angular_coupled_matrix_differential_audit",
        "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_translation_angular_coupled_matrix_differential_audit",
        "stage2_velocity_bidirectional_rowmask_translation_angular_feature",
        "0.742069",
        "lower_pair_endpoint_pose_velocity_hscaled_predictor_h_sweep_audit",
        "cylindrical_chain_endpoint_tfe_paper_lower_pair_endpoint_pose_velocity_hscaled_predictor_h_sweep_audit",
        "V047_TARGET_AUDIT=lower_pair_endpoint_pose_velocity_hscaled_predictor_h_sweep_audit",
        "V047_ENDPOINT_POSE_HSCALED_VELOCITY_H_SWEEP_VALUES",
        "V047_ENDPOINT_POSE_HSCALED_VELOCITY_H_SWEEP_REFERENCE_H",
        "V047_ENDPOINT_POSE_HSCALED_VELOCITY_H_SWEEP_T_FINAL",
        "V047_ENDPOINT_POSE_HSCALED_VELOCITY_PREDICTOR_LAWS",
        "V047_ENDPOINT_POSE_HSCALED_VELOCITY_H_SWEEP_CASES",
        "endpoint_pose_velocity_hscaled_predictor_h_sweep_audit_present",
        "h-adaptive endpoint-pose velocity predictor",
        "stage02_convex_pose_velocity_extrapolate_0p00001_0p00002_hpow_m1_z",
        "5.004e-13",
        "3.523/4.828",
        "terminal_velocity_closed=false",
        "cylindrical_smooth",
        "cylindrical_sharp",
        "6.737e-13",
        "2.337e-10",
        "1.809e+02",
        "6.484e-13",
        "2.319e-10",
        "6.582e+01",
        "2.483e-12",
        "7.994e-06",
        "2.622e+03",
        "4.463e-12",
        "8.234e-06",
        "3.204",
        "-0.428",
        "5.320e+03",
        "9.998e-12",
        "5.317/6.782",
        "2.555/1.918",
        "6.079e+03",
        "mode=full_acceptance_shape_h_sweep",
        "smooth_order_ok=true",
        "gamma=[0,0.5,1]",
        "best terminal gamma was `1.0`",
        "7.845e-17",
        "9.479e-17",
        "best residual gamma was `0.5`",
        "6.071e-13",
        "3.533e-13",
        "4.766e-12",
        "8.105e-06",
        "3.049e-16",
        "2.941e-16",
        "4.413",
        "4.397",
        "3.204/-0.428",
        "0,0.25,0.5,0.75,1",
        "60",
        "114.2",
        "8.234e-06",
        "0.75",
        "4.414",
        "0.9,0.99,0.999,1",
        "48",
        "91.6",
        "4.415",
        "4.678e-07",
        "V047_TARGET_AUDIT=lower_pair_recurrent_terminal_component_one_step_smoke",
        "V047_RECURRENT_TERMINAL_COMPONENT_RELEASE_VALUE",
        "V047_RECURRENT_TERMINAL_COMPONENT_CASES",
        "one_step_component_gamma_sweep_present=true",
        "10",
        "20",
        "31.6",
        "1.766e-12",
        "1.368e-11",
        "component_2_release_0p999",
        "3.456e-17",
        "component_7_release_0p999",
        "1.234e-11",
        "V047_TARGET_AUDIT=lower_pair_recurrent_terminal_component_h_sweep_smoke",
        "V047_RECURRENT_TERMINAL_COMPONENT_H_SWEEP_LABELS",
        "V047_RECURRENT_TERMINAL_COMPONENT_H_SWEEP_REFERENCE_H",
        "component_trajectory_h_sweep_smoke_present=true",
        "98.4",
        "2.696e-16",
        "4.401",
        "V047_TARGET_AUDIT=lower_pair_recurrent_history_gamma_h_sweep_smoke",
        "V047_RECURRENT_HISTORY_GAMMA_POLICIES",
        "V047_RECURRENT_HISTORY_GAMMA_RELEASES",
        "V047_RECURRENT_HISTORY_GAMMA_FLOOR",
        "V047_RECURRENT_HISTORY_GAMMA_REFERENCE_H",
        "history_gamma_h_sweep_smoke_present=true",
        "38.9",
        "2.586e-12",
        "9.365e-07",
        "1.451e-07",
        "4.402",
        "36.9",
        "3.869e-12",
        "1.452e-07",
        "4.415",
        "V047_TARGET_AUDIT=lower_pair_recurrent_weak_differential_audit",
        "V047_RECURRENT_WEAK_DIFFERENTIAL_CASES",
        "V047_RECURRENT_WEAK_DIFFERENTIAL_HISTORY_MODES",
        "V047_RECURRENT_WEAK_DIFFERENTIAL_H",
        "recurrent_weak_differential_audit_present=true",
        "26.0",
        "0.899",
        "0.974",
        "1.456e-15",
        "6.872",
        "any_recurrent_weak_spans_terminal_bridge=false",
        "coefficient_gradient_gap_present=true",
        "stage2",
        "translation_velocity_v",
        "V047_TARGET_AUDIT=lower_pair_recurrent_stage2_gradient_differential_audit",
        "V047_TARGET_AUDIT=lower_pair_recurrent_stage2_matrix_gradient_differential_audit",
        "V047_TARGET_AUDIT=lower_pair_recurrent_stage2_translation_velocity_matrix_differential_audit",
        "V047_TARGET_AUDIT=lower_pair_recurrent_stage2_translation_angular_coupled_matrix_differential_audit",
        "V047_TARGET_AUDIT=lower_pair_recurrent_stage2_feature_dictionary_span_audit",
        "V047_TARGET_AUDIT=lower_pair_recurrent_stage2_state_feature_coefficient_derivative_screen_audit",
        "V047_RECURRENT_STAGE2_GRADIENT_CASES",
        "V047_RECURRENT_STAGE2_GRADIENT_HISTORY_MODES",
        "V047_RECURRENT_STAGE2_GRADIENT_FEATURES",
        "V047_RECURRENT_STAGE2_GRADIENT_GAINS",
        "V047_RECURRENT_STAGE2_MATRIX_CASES",
        "V047_RECURRENT_STAGE2_MATRIX_HISTORY_MODES",
        "V047_RECURRENT_STAGE2_MATRIX_LAWS",
        "V047_RECURRENT_STAGE2_MATRIX_GAINS",
        "V047_RECURRENT_STAGE2_TRANSLATION_MATRIX_CASES",
        "V047_RECURRENT_STAGE2_TRANSLATION_MATRIX_HISTORY_MODES",
        "V047_RECURRENT_STAGE2_TRANSLATION_MATRIX_LAWS",
        "V047_RECURRENT_STAGE2_TRANSLATION_MATRIX_GAINS",
        "V047_RECURRENT_STAGE2_COUPLED_MATRIX_CASES",
        "V047_RECURRENT_STAGE2_COUPLED_MATRIX_HISTORY_MODES",
        "V047_RECURRENT_STAGE2_COUPLED_MATRIX_LAWS",
        "V047_RECURRENT_STAGE2_COUPLED_MATRIX_GAINS",
        "recurrent_stage2_gradient_differential_audit_present=true",
        "recurrent_stage2_matrix_gradient_differential_audit_present=true",
        "recurrent_stage2_translation_velocity_matrix_differential_audit_present=true",
        "recurrent_stage2_translation_angular_coupled_matrix_differential_audit_present=true",
        "V047_TARGET_AUDIT=lower_pair_recurrent_stage2_feature_coefficient_law_screen_audit",
        "frozen coefficient-law screen",
        "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_feature_coefficient_law_screen_audit",
        "coefficient_law_row_count=60",
        "span_count=0",
        "closure_delta_norm_weights",
        "coefficient_derivative_included=false",
        "state-feature coefficient-derivative screen",
        "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_state_feature_coefficient_derivative_screen_audit",
        "state_feature_coefficient_derivative_row_count=36",
        "inverse_closure_delta_norm_weights_derivative",
        "coefficient_derivative_included=true",
        "35.3",
        "curvature_plus_history_delta",
        "1e12",
        "1.246e-09",
        "2.861e+04",
        "68.1",
        "diagonal_plus_row_broadcast_feature",
        "0.898873",
        "4.005e-09",
        "9.197e+04",
        "stage2_velocity_column_broadcast_feature",
        "stage2_minus_stage1_velocity_row_broadcast_feature",
        "velocity_curvature_diagonal_plus_row_broadcast_feature",
        "46.6",
        "0.585746",
        "1.460e-06",
        "3.353e+07",
        "51.2",
        "stage2_velocity_shifted_column_broadcast_feature",
        "0.576548",
        "27.8",
        "full_run_invoked=false",
        "artifact_written=false",
        "summary_updated=false",
        "0.909693",
        "angular_velocity_w",
        "0.502991",
        "0.963038",
        "0.487135",
        "0.964696",
        "stage2_angular_velocity_shifted_column_broadcast_feature",
        "0.752997",
        "0.660361",
        "0.978093",
        "feature-dictionary span audit",
        "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_feature_dictionary_span_audit",
        "feature_dictionary_row_count=12",
        "combined_all_dictionary_span_count=2",
        "stage2_matrix_core",
        "1.084e-14",
        "target_jacobian_used_for_formula=false",
        "target_direction_oracle_used=false",
        "formula_coefficient_law_present=false",
        "coefficient/selection law",
        "coupled translation/angular stage-2 weak-row",
        "stage2_velocity_angular_to_translation_cross_feature",
        "0.898812",
        "0.556004",
        "0.999994",
        "translation/angular outer-cross",
        "new lower-pair weak-row formula",
        "endpoint-pose generalized-velocity predictor",
        "paper_endpoint_pose_positive_lagrange_z",
        "0.117782",
        "0.514237",
        "0.961546",
        "paper_endpoint_pose_stage02_convex_0p00_z",
        "terminal_bridge_equivalent_predictor=true",
        "paper_endpoint_pose_stage02_convex_0p05_z",
        "0.049317",
        "h=0.02",
        "0.051890",
        "h=0.01",
        "0.052472",
        "h-scaling",
        "stage02_convex_pose_velocity_0p01_z",
        "0.009512",
        "0.009978",
        "0.010085",
        "0.019205",
        "0.049390",
        "0.103464",
        "near-terminal limit",
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
        "any_nonterminal_candidate_spans_terminal_bridge=false",
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
        "angposeaccel_p0p002",
        "component-split velocity-acceleration",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelaccel_m0p01_z",
        "2.138e-04",
        "31.8",
        "0.886603",
        "angvelaccel_p0p01",
        "0.000864560",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelaccel_m0p0005_z",
        "9.8175e-06",
        "31.4",
        "0.802349",
        "component-mixed pose/velocity Taylor",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_angpose_transvelaccel_p0p0005_m0p0005_z",
        "9.987e-06",
        "32.0",
        "0.774582",
        "0.625975",
        "transpose_angvelaccel",
        "stage-2-fixed/delta acceleration velocity-shift",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelaccelstage2_m0p0005_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelacceldelta20_m0p0005_z",
        "1.0119e-05",
        "nonfinal terminal velocity/source predictor",
        "nonfinal_velocity_terminal_euler1_z",
        "0.923466",
        "translation_velocity_v",
        "0.959959",
        "0.930013",
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
        "stage02_convex_pose_velocity_0p01_z",
        "6.255e-06",
        "2.345/1.878",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_z",
        "projection_used=false",
        "21.8",
        "1.254e-07",
        "6.412/3.775",
        "28.9",
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
        "nonterminal local repair probe",
        "57.3",
        "stage2_velocity_feature_outer_stage2_velocity",
        "0.898720",
        "3.631e-09",
        "8.340e+04",
        "56.7",
        "stage2_velocity_diagonal_plus_hadamard_row_feature_stage2_velocity",
        "0.898530",
        "9.733e-09",
        "2.235e+05",
        "stage-2 active translation/angular cross",
        "stage2_velocity_symmetric_translation_angular_cross_feature",
        "0.898843",
        "50.9",
        "0.556036",
        "0.999999",
        "non-stage-2 feature matrix",
        "stage01_mean_velocity_diagonal_plus_row_broadcast_feature",
        "0.827381",
        "36.5",
        "1.460e-06",
        "3.353e+07",
        "0.571311",
        "0.991949",
        "stage02_convex_pose_velocity_0p01_accel_m0p1_z",
        "stage02_convex_pose_velocity_0p01_genaccel_m0p1_z",
        "0.012376",
        "0.077874",
        "generalized-velocity Taylor",
        "nonterminal mean-acceleration",
        "stage02_convex_pose_velocity_0p02_poseslope_m0p1_z",
        "0.878519",
        "kinematic pose-slope",
        "stage-pose-slope velocity predictor",
        "source-to-velocity lift",
        "stage02_convex_pose_velocity_0p01_sourcelift_historydelta_p1_z",
        "stage02_convex_pose_velocity_0p01_sourcelift_source0_p1_z",
        "0.609803",
        "76.4",
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
        "any_candidate_spans_terminal_bridge=false",
        "order_terminal_intersection_present=false",
        "any_gamma_terminal_velocity_closed=true",
        "validate_full_tfe_repair_spec.py",
    ]
    for token in required:
        checks.check(token in spec, f"repair spec missing token: {token}")


def check_run_script_slots(checks: Checks, run_text: str) -> None:
    for token in [
        "paper_tfe_lower_pair_source_free_mean_velocity_closure_rows_jax",
        "paper_tfe_lower_pair_source_free_final_stage_velocity_closure_rows_jax",
        "paper_tfe_lower_pair_source_free_order_closure_blend_rows_jax",
        "residual_cylindrical_chain_endpoint_tfe_paper_lower_pair_source_free_order_closure_blend_candidate",
        "run_endpoint_tfe_paper_lower_pair_source_free_near_final_beta_boundary_audit",
        "lower_pair_source_free_near_final_beta_boundary",
        "run_endpoint_tfe_paper_lower_pair_recurrent_feedback_gain_boundary_audit",
        "lower_pair_recurrent_feedback_gain_boundary",
        "run_endpoint_tfe_paper_lower_pair_recurrent_component_feedback_gain_boundary_audit",
        "lower_pair_recurrent_component_feedback_gain_boundary",
        "run_endpoint_tfe_paper_lower_pair_recurrent_hscaled_feedback_gain_boundary_audit",
        "lower_pair_recurrent_hscaled_feedback_gain_boundary",
        "run_endpoint_tfe_paper_lower_pair_recurrent_source_law_trajectory_screen_audit",
        "lower_pair_recurrent_source_law_trajectory_screen",
        "run_endpoint_tfe_paper_lower_pair_recurrent_three_history_source_law_trajectory_screen_audit",
        "lower_pair_recurrent_three_history_source_law_trajectory_screen",
        "run_endpoint_tfe_paper_lower_pair_recurrent_four_history_source_law_trajectory_screen_audit",
        "lower_pair_recurrent_four_history_source_law_trajectory_screen",
        "run_endpoint_tfe_paper_lower_pair_recurrent_nonlinear_history_source_law_trajectory_screen_audit",
        "lower_pair_recurrent_nonlinear_history_source_law_trajectory_screen",
        "emit_row_space_coefficient_derivative_row",
        "row_space_coefficient_derivative_probe_row_count",
        "cylindrical_chain_endpoint_tfe_paper_lower_pair_velocity_compression_row_space_coefficient_derivative_audit",
        "run_endpoint_tfe_paper_lower_pair_recurrent_source_law_final_retain_boundary_audit",
        "lower_pair_recurrent_source_law_final_retain_boundary",
        "V047_RECURRENT_SOURCE_LAW_SCREEN_LAWS",
        "V047_RECURRENT_THREE_HISTORY_SOURCE_LAW_SCREEN_LAWS",
        "V047_RECURRENT_FOUR_HISTORY_SOURCE_LAW_SCREEN_LAWS",
        "V047_RECURRENT_NONLINEAR_HISTORY_SOURCE_LAW_SCREEN_LAWS",
        "recurrent_threehistory_velocity_terminal_source0ab4_z",
        "recurrent_threehistory_velocity_terminal_source01historyslopejerk_z",
        "threehistory_source01historyslopejerk_terminal_raw",
        "three_history_source_law_trajectory_screen_present",
        "recurrent_fourhistory_velocity_terminal_source0ab5_z",
        "recurrent_fourhistory_velocity_terminal_source01historyslopejerksnap_z",
        "fourhistory_source01historyslopejerksnap_terminal_raw",
        "four_history_source_law_trajectory_screen_present",
        "recurrent_nonlinearhistory_velocity_terminal_source0historyhadamard_z",
        "nonlinearhistory_terminal_raw",
        "nonlinear_history_source_law_trajectory_screen_present",
        "paper_tfe_lower_pair_source_free_recurrent_weak_closure_rows_jax",
        "residual_cylindrical_chain_endpoint_tfe_paper_lower_pair_source_free_recurrent_weak_closure_candidate",
        "history_source",
        "source_curvature",
        "recurrent_source_delta",
        "bounded_feature",
        "nonfinal_velocity_closure",
        "recurrent_weak_closure",
        "R_ENDPOINT_TFE_PAPER_LOWER_PAIR_SOURCE_FREE_RECURRENT_WEAK_CLOSURE_VALUE",
        "R_ENDPOINT_TFE_PAPER_LOWER_PAIR_SOURCE_FREE_RECURRENT_WEAK_CLOSURE_JAC",
        "PAPER_TFE_LOWER_PAIR_SOURCE_FREE_RECURRENT_WEAK_CLOSURE_ROWS_VALUE",
        "PAPER_TFE_LOWER_PAIR_SOURCE_FREE_RECURRENT_WEAK_CLOSURE_ROWS_JAC",
        "paper_tfe_lower_pair_stage0_source_history_np",
        "endpoint_tfe_paper_lower_pair_source_free_recurrent_weak_closure_step",
        "integrate_endpoint_tfe_paper_lower_pair_source_free_recurrent_weak_closure",
        "run_endpoint_tfe_paper_lower_pair_recurrent_weak_closure_smoke",
        "run_endpoint_tfe_paper_lower_pair_recurrent_weak_closure_trajectory_smoke",
        "run_endpoint_tfe_paper_lower_pair_recurrent_weak_closure_h_sweep_smoke",
        "run_endpoint_tfe_paper_lower_pair_recurrent_terminal_blend_one_step_smoke",
        "paper_tfe_lower_pair_source_free_recurrent_terminal_blend_rows_jax",
        "residual_cylindrical_chain_endpoint_tfe_paper_lower_pair_source_free_recurrent_terminal_blend_candidate",
        "endpoint_tfe_paper_lower_pair_source_free_recurrent_terminal_blend_step",
        "integrate_endpoint_tfe_paper_lower_pair_source_free_recurrent_terminal_blend",
        "run_endpoint_tfe_paper_lower_pair_recurrent_terminal_blend_h_sweep_smoke",
        "run_endpoint_tfe_paper_lower_pair_recurrent_terminal_component_one_step_smoke",
        "run_endpoint_tfe_paper_lower_pair_recurrent_terminal_component_h_sweep_smoke",
        "recurrent_history_gamma_policy_np",
        "integrate_endpoint_tfe_paper_lower_pair_source_free_recurrent_history_gamma",
        "run_endpoint_tfe_paper_lower_pair_recurrent_history_gamma_h_sweep_smoke",
        "PAPER_TFE_LOWER_PAIR_SOURCE_FREE_FINAL_STAGE_VELOCITY_CLOSURE_ROWS_VALUE",
        "PAPER_TFE_LOWER_PAIR_SOURCE_FREE_FINAL_STAGE_VELOCITY_CLOSURE_ROWS_JAC",
        "run_endpoint_tfe_paper_lower_pair_recurrent_weak_differential_audit",
        "paper_tfe_lower_pair_source_free_recurrent_stage2_gradient_closure_rows_jax",
        "run_endpoint_tfe_paper_lower_pair_recurrent_stage2_gradient_differential_audit",
        "paper_tfe_lower_pair_source_free_recurrent_stage2_matrix_gradient_closure_rows_jax",
        "run_endpoint_tfe_paper_lower_pair_recurrent_stage2_matrix_gradient_differential_audit",
        "run_endpoint_tfe_paper_lower_pair_recurrent_stage2_translation_velocity_matrix_differential_audit",
        "run_endpoint_tfe_paper_lower_pair_recurrent_stage2_translation_angular_coupled_matrix_differential_audit",
        "run_endpoint_tfe_paper_lower_pair_recurrent_stage2_feature_dictionary_span_audit",
        "run_endpoint_tfe_paper_lower_pair_recurrent_stage2_feature_coefficient_law_screen_audit",
        "run_endpoint_tfe_paper_lower_pair_recurrent_stage2_state_feature_coefficient_derivative_screen_audit",
        "lower_pair_recurrent_stage2_feature_coefficient_law_screen_audit",
        "lower_pair_recurrent_stage2_state_feature_coefficient_derivative_screen_audit",
        "stage2_velocity_",
        "stage2_translation_velocity_",
        "stage2_angular_velocity_",
        "stage2_minus_stage1_velocity_",
        "velocity_curvature_",
        "stage01_mean_velocity_",
        "feature_outer_stage2_velocity",
        "stage2_velocity_outer_feature",
        "symmetric_stage2_velocity_outer_feature",
        "antisymmetric_stage2_velocity_outer_feature",
        "translation_to_angular_cross_feature",
        "angular_to_translation_cross_feature",
        "symmetric_translation_angular_cross_feature",
        "shifted_translation_angular_cross_feature",
        "bidirectional_rowmask_translation_angular_feature",
        "pair_swap_diagonal_feature",
        "local_pair_cross_feature",
        "h_scaled_stage02_weight",
        "paper_tfe_lower_pair_source_free_endpoint_pose_velocity_predictor_closure_rows_jax",
        "paper_endpoint_pose_lagrange_z",
        "paper_endpoint_pose_positive_lagrange_z",
        "paper_endpoint_pose_stage1_half_lagrange_z",
        "paper_endpoint_pose_stage12_linear_z",
        "paper_endpoint_pose_stage02_linear_z",
        "paper_endpoint_pose_stage02_convex_0p00_z",
        "paper_endpoint_pose_stage02_convex_0p05_z",
        "paper_endpoint_pose_stage02_convex_0p10_z",
        "paper_endpoint_pose_paper_m3_y2_z",
        "stage02_convex_pose_velocity_0p01_accel_m0p1_z",
        "stage02_convex_pose_velocity_0p01_accel_p0p1_z",
        "stage02_convex_pose_velocity_0p01_genaccel_m0p1_z",
        "stage02_convex_pose_velocity_0p01_genaccel_p0p1_z",
        "stage02_convex_pose_velocity_slope_0p01_0p02_z",
        "stage02_convex_pose_velocity_slope_0p01_0p05_z",
        "stage02_convex_pose_velocity_slopeh_0p01_0p02_z",
        "stage02_convex_pose_velocity_slopeh_0p01_0p05_z",
        "stage02_convex_pose_velocity_curvature_0p01_0p02_0p05_z",
        "stage02_convex_pose_velocity_curvatureh2_0p01_0p02_0p05_z",
        "stage02_convex_pose_velocity_curvaturew2_0p01_0p02_0p05_z",
        "stage02_convex_pose_velocity_curvature_0p01_0p05_0p10_z",
        "history_delta_shifted_column_broadcast_feature",
        "history_unit_delta_shifted_column_broadcast_feature",
        "source0_shifted_column_broadcast_feature",
        "source2_shifted_column_broadcast_feature",
        "source02_mean_shifted_column_broadcast_feature",
        "source02_delta_shifted_column_broadcast_feature",
        "source_curvature_shifted_column_broadcast_feature",
        "source_curvature_history_delta_shifted_column_broadcast_feature",
        "source_curvature_minus_history_delta_shifted_column_broadcast_feature",
        "source_curvature_minus_history_delta_diagonal_plus_row_broadcast_feature",
        "source_curvature_history_hadamard_shifted_column_broadcast_feature",
        "source_curvature_history_hadamard_diagonal_plus_row_broadcast_feature",
        "source_curvature_history_unit_hadamard_shifted_column_broadcast_feature",
        "source_curvature_history_unit_hadamard_diagonal_plus_row_broadcast_feature",
        "normalized_source_curvature_history_delta_shifted_column_broadcast_feature",
        "normalized_source_curvature_history_delta_diagonal_plus_row_broadcast_feature",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_source0_m0p1_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_source0_p0p1_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_historydelta_m0p1_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_historydelta_p0p1_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_historyunitdelta_m0p1_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_historyunitdelta_p0p1_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_curvature_m0p01_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_curvature_p0p01_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_curvature_m0p05_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_curvature_p0p05_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_curvature_m0p1_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_curvature_p0p1_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_curvature_m0p2_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_curvature_p0p2_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_curvature_m0p5_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_curvature_p0p5_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_accel_m0p01_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_accel_p0p01_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_accel_m0p05_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_accel_p0p05_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_accel_m0p1_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_accel_p0p1_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_accel_m0p2_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_accel_p0p2_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_accel_m0p5_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_accel_p0p5_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_genaccel_m0p01_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_genaccel_p0p01_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_genaccel_m0p05_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_genaccel_p0p05_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_genaccel_m0p1_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_genaccel_p0p1_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_genaccel_m0p2_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_genaccel_p0p2_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_genaccel_m0p5_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_genaccel_p0p5_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_posevelaccel_p0p0005_m0p0001_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_posevelaccel_p0p0005_p0p0001_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_posevelaccel_p0p0005_m0p0005_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_posevelaccel_p0p0005_p0p0005_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_posevelaccel_p0p0005_m0p001_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_posevelaccel_p0p0005_p0p001_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_posevelaccel_m0p0005_m0p0005_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_posevelaccel_m0p0005_p0p0005_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_posevelaccel_p0p001_m0p0005_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_posevelaccel_p0p001_p0p0005_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_transposeaccel_m0p01_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_transposeaccel_p0p1_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_angposeaccel_p0p002_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_angposeaccel_p0p01_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelaccel_m0p0005_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelaccel_p0p0005_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelaccel_m0p01_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelaccel_p0p1_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_angvelaccel_m0p01_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_angvelaccel_p0p1_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_angpose_transvelaccel_p0p0005_m0p0005_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_angpose_transvelaccel_p0p002_p0p0005_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_transpose_angvelaccel_m0p01_p0p01_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_genvelaccelstage2_m0p0005_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelaccelstage2_m0p0005_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_genvelacceldelta20_m0p0005_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelacceldelta20_m0p0005_z",
        "nonfinal_velocity_terminal_linear01_z",
        "nonfinal_velocity_terminal_euler0_z",
        "nonfinal_velocity_terminal_euler1_z",
        "nonfinal_velocity_terminal_ab01_z",
        "nonfinal_velocity_terminal_source01mean0_z",
        "nonfinal_velocity_terminal_source01linear0_z",
        "nonfinal_velocity_terminal_source01linear1_z",
        "nonfinal_velocity_terminal_hermite01_z",
        "stage02_convex_pose_velocity_0p00_z",
        "terminal_pose_velocity_projected_z",
        "stage02_convex_pose_velocity_0p01_terminalproj_z",
        "stage02_convex_pose_velocity_0p01_terminalproj_p0p1_z",
        "stage02_convex_pose_velocity_0p01_terminalproj_p0p5_z",
        "stage02_convex_pose_velocity_hscaled_0p00001_pow_m2_z",
        "stage02_convex_pose_velocity_extrapolate_0p00001_0p00002_hpow_m1_z",
        "h-adaptive endpoint-pose velocity response audit",
        "cylindrical_chain_endpoint_tfe_paper_lower_pair_endpoint_pose_velocity_hscaled_response_audit",
        "terminal_closed_row_count",
        "smooth_order_ok_count",
        "order_terminal_intersection_present",
        "projection_like_predictor_laws",
        "lower_pair_endpoint_pose_velocity_predictor_h_sweep_smoke",
        "lower_pair_endpoint_pose_velocity_predictor_reference_output_audit",
        "lower_pair_endpoint_pose_velocity_hscaled_predictor_h_sweep_audit",
        "lower_pair_endpoint_pose_velocity_hscaled_response_audit",
        "lower_pair_source_free_near_final_beta_boundary",
        "run_endpoint_tfe_paper_lower_pair_endpoint_pose_velocity_predictor_h_sweep_smoke",
        "run_endpoint_tfe_paper_lower_pair_endpoint_pose_velocity_predictor_reference_output_audit",
        "run_endpoint_tfe_paper_lower_pair_endpoint_pose_velocity_hscaled_predictor_h_sweep_audit",
        "run_endpoint_tfe_paper_lower_pair_endpoint_pose_velocity_hscaled_response_audit",
        "run_endpoint_tfe_paper_lower_pair_source_free_near_final_beta_boundary_audit",
        "V047_ENDPOINT_POSE_HSCALED_VELOCITY",
        "cylindrical_chain_endpoint_tfe_paper_lower_pair_endpoint_pose_velocity_hscaled_predictor_h_sweep_audit",
        "cylindrical_chain_endpoint_tfe_paper_lower_pair_endpoint_pose_velocity_hscaled_response_audit",
        "endpoint_pose_velocity_hscaled_predictor_h_sweep_audit_present",
        "hscaled_response_audit_present",
        "candidate frontier audit",
        "cylindrical_chain_endpoint_tfe_paper_lower_pair_candidate_frontier_audit",
        "total_candidate_row_count=115",
        "order_terminal_intersection_count=0",
        "stage-local weak-row tangent",
        "bounded tangent requirement audit",
        "cylindrical_chain_endpoint_tfe_paper_lower_pair_bounded_tangent_requirement_audit",
        "V047_TARGET_AUDIT=lower_pair_bounded_tangent_requirement_audit",
        "requirement_row_count=7",
        "target_free_formula_span_count=0",
        "row_space_oracle_span_count=36",
        "bounded_gradient_practical_cap_spanning_row_count=12",
        "lower_pair_candidate_frontier_audit",
        "run_endpoint_tfe_paper_lower_pair_candidate_frontier_audit",
        "lower_pair_bounded_tangent_requirement_audit",
        "run_endpoint_tfe_paper_lower_pair_bounded_tangent_requirement_audit",
        "cylindrical_chain_endpoint_tfe_paper_lower_pair_source_free_near_final_beta_boundary_audit",
        "run_endpoint_tfe_paper_lower_pair_recurrent_feedback_gain_boundary_audit",
        "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_feedback_gain_boundary_audit",
        "run_endpoint_tfe_paper_lower_pair_recurrent_component_feedback_gain_boundary_audit",
        "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_component_feedback_gain_boundary_audit",
        "run_endpoint_tfe_paper_lower_pair_recurrent_hscaled_feedback_gain_boundary_audit",
        "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_hscaled_feedback_gain_boundary_audit",
        "run_endpoint_tfe_paper_lower_pair_recurrent_source_law_trajectory_screen_audit",
        "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_source_law_trajectory_screen_audit",
        "run_endpoint_tfe_paper_lower_pair_recurrent_three_history_source_law_trajectory_screen_audit",
        "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_three_history_source_law_trajectory_screen_audit",
        "run_endpoint_tfe_paper_lower_pair_recurrent_nonlinear_history_source_law_trajectory_screen_audit",
        "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_nonlinear_history_source_law_trajectory_screen_audit",
        "emit_row_space_coefficient_derivative_row",
        "cylindrical_chain_endpoint_tfe_paper_lower_pair_velocity_compression_row_space_coefficient_derivative_audit",
        "run_endpoint_tfe_paper_lower_pair_recurrent_source_law_final_retain_boundary_audit",
        "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_source_law_final_retain_boundary_audit",
        "integrate_endpoint_tfe_paper_lower_pair_source_free_endpoint_pose_velocity_predictor",
        "endpoint_tfe_paper_lower_pair_source_free_endpoint_pose_velocity_predictor_step",
        "R_ENDPOINT_TFE_PAPER_LOWER_PAIR_SOURCE_FREE_ENDPOINT_POSE_VELOCITY_PREDICTOR_VALUE",
        "stage02_convex_pose_velocity_0p00_sourcelift_source0_m0p1_z",
        "stage02_convex_pose_velocity_0p00_sourcelift_historydelta_p0p1_z",
        "stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p0001_z",
        "stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p0001_angposeaccel_p0p0001_z",
        "stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p01_z",
        "stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p1_z",
        "stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_p0p5_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_m0p0005_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_p0p0005_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_m0p001_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_p0p001_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_m0p002_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_p0p002_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_m0p005_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_p0p005_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_m0p01_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_p0p01_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_m0p05_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_p0p05_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_m0p1_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_p0p1_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_m0p2_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_p0p2_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_m0p5_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_p0p5_z",
        "gauss_endpoint_pose_lagrange_z",
        "gauss_endpoint_pose_positive_lagrange_z",
        "gauss_endpoint_pose_paper_m3_y2_z",
        "gauss_endpoint_pose_paper_m3_y2_positive_average_z",
        "gauss_endpoint_pose_paper_m3_y2_positive_quarter_z",
        "gauss_endpoint_pose_paper_m3_y2_positive_three_quarter_z",
        "gauss_endpoint_pose_stage1_half_lagrange_z",
        "gauss_endpoint_pose_stage12_linear_z",
        "gauss_endpoint_pose_stage02_linear_z",
        "gauss_endpoint_pose_stage02_convex_0p00_z",
        "gauss_endpoint_pose_stage02_convex_0p05_z",
        "gauss_endpoint_pose_stage02_convex_0p10_z",
        "gauss_endpoint_pose_stage02_convex_0p15_z",
        "gauss_endpoint_pose_stage02_convex_0p20_z",
        "gauss_endpoint_pose_stage02_convex_0p25_z",
        "gauss_endpoint_pose_stage01_mean_z",
        "gauss_endpoint_pose_stage012_mean_z",
        "gauss_endpoint_pose_integrated_acceleration_z",
        "stage_zdot",
        "_genaccel_",
        "_poseaccel_",
        "_posevelaccel_",
        "_transposeaccel_",
        "_angposeaccel_",
        "_transvelaccel_",
        "_angvelaccel_",
        "_angpose_transvelaccel_",
        "_transpose_angvelaccel_",
        "_genvelaccelstage2_",
        "_transvelaccelstage2_",
        "_genvelacceldelta20_",
        "_transvelacceldelta20_",
        "nonfinal_terminal_velocity_source_closure",
        "nonfinal_velocity_terminal_",
        "pose_shift=",
        "z_shift=",
        "state_vector_component_mask",
        "stage02_convex_pose_velocity_0p01_poseslope_m0p1_z",
        "stage02_convex_pose_velocity_0p01_poseslope_p0p1_z",
        "stage02_pose_slope_z",
        "_poseslope_",
        "source_closure_vector",
        "source_to_velocity_shift",
        "source_to_velocity_matrixdiff_shift",
        "historyunitdelta",
        "_sourcelift_",
        "_sourceliftmatrixdiff_",
        "stage02_convex_pose_velocity_0p01_sourcelift_historydelta_p1_z",
        "stage02_convex_pose_velocity_0p01_sourcelift_source0_p1_z",
        "stage02_convex_pose_velocity_0p01_sourceliftmatrixdiff_source0_m10_z",
        "stage02_convex_pose_velocity_0p01_sourceliftmatrixdiff_historydelta_p0p1_z",
        "stage02_convex_pose_velocity_0p01_sourceliftmatrixdiff_historyunitdelta_p0p1_z",
        "hadamard_diagonal_feature_stage2_velocity",
        "shifted_hadamard_diagonal_feature_stage2_velocity",
        "diagonal_plus_hadamard_row_feature_stage2_velocity",
        "diagonal_plus_hadamard_column_feature_stage2_velocity",
        "recurrent_terminal_component_gamma_vectors",
        "R_ENDPOINT_TFE_PAPER_LOWER_PAIR_SOURCE_FREE_RECURRENT_TERMINAL_BLEND_VALUE",
        "R_ENDPOINT_TFE_PAPER_LOWER_PAIR_SOURCE_FREE_RECURRENT_TERMINAL_BLEND_JAC",
        "lower_pair_recurrent_weak_closure_smoke",
        "lower_pair_recurrent_weak_closure_trajectory_smoke",
        "lower_pair_recurrent_weak_closure_h_sweep_smoke",
        "lower_pair_recurrent_terminal_blend_one_step_smoke",
        "lower_pair_recurrent_terminal_blend_h_sweep_smoke",
        "lower_pair_recurrent_terminal_component_one_step_smoke",
        "lower_pair_recurrent_terminal_component_h_sweep_smoke",
        "lower_pair_recurrent_history_gamma_h_sweep_smoke",
        "lower_pair_recurrent_weak_differential_audit",
        "lower_pair_recurrent_stage2_gradient_differential_audit",
        "lower_pair_recurrent_stage2_matrix_gradient_differential_audit",
        "lower_pair_recurrent_stage2_translation_velocity_matrix_differential_audit",
        "lower_pair_recurrent_stage2_translation_angular_coupled_matrix_differential_audit",
        "lower_pair_recurrent_stage2_feature_dictionary_span_audit",
        "lower_pair_recurrent_source_law_trajectory_screen",
        "lower_pair_recurrent_three_history_source_law_trajectory_screen",
        "lower_pair_recurrent_nonlinear_history_source_law_trajectory_screen",
        "V047_RECURRENT_TERMINAL_BLEND_GAMMAS",
        "V047_RECURRENT_TERMINAL_BLEND_H",
        "V047_RECURRENT_TERMINAL_BLEND_CASES",
        "V047_RECURRENT_TERMINAL_BLEND_H_SWEEP_GAMMAS",
        "V047_RECURRENT_TERMINAL_BLEND_H_SWEEP_VALUES",
        "V047_RECURRENT_TERMINAL_BLEND_H_SWEEP_REFERENCE_H",
        "V047_RECURRENT_TERMINAL_BLEND_H_SWEEP_CASES",
        "V047_RECURRENT_TERMINAL_COMPONENT_RELEASE_VALUE",
        "V047_RECURRENT_TERMINAL_COMPONENT_H",
        "V047_RECURRENT_TERMINAL_COMPONENT_CASES",
        "V047_RECURRENT_TERMINAL_COMPONENT_H_SWEEP_LABELS",
        "V047_RECURRENT_TERMINAL_COMPONENT_H_SWEEP_VALUES",
        "V047_RECURRENT_TERMINAL_COMPONENT_H_SWEEP_REFERENCE_H",
        "V047_RECURRENT_TERMINAL_COMPONENT_H_SWEEP_CASES",
        "V047_RECURRENT_HISTORY_GAMMA_POLICIES",
        "V047_RECURRENT_HISTORY_GAMMA_RELEASES",
        "V047_RECURRENT_HISTORY_GAMMA_FLOOR",
        "V047_RECURRENT_HISTORY_GAMMA_H_SWEEP_VALUES",
        "V047_RECURRENT_HISTORY_GAMMA_REFERENCE_H",
        "V047_RECURRENT_HISTORY_GAMMA_T_FINAL",
        "V047_RECURRENT_HISTORY_GAMMA_CASES",
        "V047_RECURRENT_WEAK_DIFFERENTIAL_CASES",
        "V047_RECURRENT_WEAK_DIFFERENTIAL_HISTORY_MODES",
        "V047_RECURRENT_WEAK_DIFFERENTIAL_H",
        "V047_RECURRENT_STAGE2_GRADIENT_CASES",
        "V047_RECURRENT_STAGE2_GRADIENT_HISTORY_MODES",
        "V047_RECURRENT_STAGE2_GRADIENT_FEATURES",
        "V047_RECURRENT_STAGE2_GRADIENT_GAINS",
        "V047_RECURRENT_STAGE2_GRADIENT_H",
        'env_prefix: str = "V047_RECURRENT_STAGE2_MATRIX"',
        'f"{env_prefix}_CASES"',
        'f"{env_prefix}_HISTORY_MODES"',
        'f"{env_prefix}_LAWS"',
        'f"{env_prefix}_GAINS"',
        'f"{env_prefix}_H"',
        'env_prefix="V047_RECURRENT_STAGE2_COUPLED_MATRIX"',
        "V047_RECURRENT_WEAK_SMOKE_NUMERIC",
        "V047_RECURRENT_WEAK_TRAJECTORY_CASES",
        "V047_RECURRENT_WEAK_TRAJECTORY_H",
        "V047_RECURRENT_WEAK_TRAJECTORY_T_FINAL",
        "V047_RECURRENT_WEAK_H_SWEEP_FULL",
        "V047_RECURRENT_WEAK_H_SWEEP_VALUES",
        "V047_RECURRENT_WEAK_H_SWEEP_REFERENCE_H",
        "V047_RECURRENT_WEAK_H_SWEEP_CASES",
        "diagnostic_smoke_only",
        "trajectory_smoke_present",
        "bounded_h_sweep_smoke_present",
        "acceptance_shape_requested",
        "terminal_velocity_closed",
        "any_gamma_terminal_velocity_closed",
        "smooth_order_ok",
        "best_gamma_by_terminal_velocity",
        "best_gamma_by_smooth_order",
        "one_step_gamma_sweep_present",
        "one_step_component_gamma_sweep_present",
        "component_trajectory_h_sweep_smoke_present",
        "history_gamma_h_sweep_smoke_present",
        "recurrent_weak_differential_audit_present",
        "recurrent_stage2_gradient_differential_audit_present",
        "recurrent_stage2_matrix_gradient_differential_audit_present",
        "recurrent_stage2_feature_dictionary_span_audit_present",
        "recurrent_stage2_feature_coefficient_law_screen_audit_present",
        "target_free_coefficient_law",
        "bounded_coefficient_law_present",
        "coefficient_derivative_included",
        "order_terminal_intersection_present",
        "best_gamma_label_by_terminal_velocity",
        "best_gamma_label_by_smooth_order",
        "any_policy_terminal_velocity_closed",
        "best_policy_label_by_terminal_velocity",
        "best_policy_label_by_smooth_order",
        "max_history_gamma_release",
        "any_recurrent_weak_spans_terminal_bridge",
        "all_recurrent_weak_spans_terminal_bridge",
        "coefficient_gradient_gap_present",
        "recurrent_projection_relative_residual",
        "final_stage_projection_relative_residual",
        "recurrent_missing_direction_dominant_variable_family",
        "target_bridge_used_for_scoring_only",
        "any_candidate_spans_terminal_bridge",
        "best_feature_mode",
        "best_matrix_law",
        "best_gain",
        "best_projection_relative_residual",
        "best_missing_direction_rank",
        "best_missing_direction_dominant_variable_family",
        "best_missing_direction_dominant_variable_fraction",
        "best_missing_direction_stage0_fraction",
        "best_missing_direction_stage1_fraction",
        "best_missing_direction_stage2_fraction",
        "candidate_spans_terminal_bridge",
        "candidate_missing_direction_rank",
        "candidate_missing_direction_dominant_variable_family",
        "candidate_missing_direction_dominant_variable_fraction",
        "candidate_missing_direction_stage0_fraction",
        "candidate_missing_direction_stage1_fraction",
        "candidate_missing_direction_stage2_fraction",
        "uses_stage2_velocity_feature",
        "uses_stage2_velocity_matrix_feature",
        "uses_stage2_translation_velocity_matrix_feature",
        "uses_stage2_translation_angular_coupled_matrix_feature",
        "uses_endpoint_pose_velocity_predictor",
        "terminal_bridge_equivalent_predictor",
        "best_nonterminal_matrix_law",
        "nonterminal_span_row_count",
        "any_nonterminal_candidate_spans_terminal_bridge",
        "component_release_row_count",
        "nontrivial_terminal_closed_count",
        "gamma_vector_count",
        "raw_terminal_endpoint_velocity_constraint_vector",
        "recurrent_terminal_blend_closure_rows",
        "numeric_step_invoked",
        "artifact_written",
        "summary_updated",
        "full_run_invoked",
        "trajectory_h_sweep_present",
        "accepted_h_sweep_present",
        "history_source_bootstrap_policy",
        "zero_initial_then_stage0_source_estimate",
        "max_recurrent_weak_closure_row_norm",
        "max_history_source_update_norm",
    ]:
        checks.check(token in run_text, f"run_v047.py missing expected existing slot: {token}")


def check_summary_alignment(checks: Checks, summary: dict) -> dict[str, object]:
    asme = summary.get("asme_gate", {})
    compression = summary.get("endpoint_tfe_paper_lower_pair_velocity_compression_audit", {})
    contract = summary.get("endpoint_tfe_paper_residual_substitution_contract_audit", {})
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

    checks.check(asme.get("status") == EXPECTED_ASME_STATUS, "ASME gate status changed")
    checks.check(contract.get("stage_row_budget") == 132, "paper residual stage-row budget changed")
    checks.check(contract.get("row_count") == 6, "paper residual family count changed")
    checks.check(contract.get("residual_substituted_count") == 6, "paper residual substitution count changed")
    checks.check(contract.get("accepted_h_sweep_count") == 0, "paper residual contract unexpectedly accepted h-sweep")
    checks.check(contract.get("full_tfe_stage_replacement") is False, "paper residual contract unexpectedly claims full TFE")

    checks.check(compression.get("source_consistency_rows") == 16, "source-consistency row count changed")
    checks.check(compression.get("target_row_count") == 8, "target closure row count changed")
    checks.check(compression.get("velocity_stage_rows") == 24, "velocity-stage row count changed")
    checks.check(compression.get("stage_unknown_count") == 132, "stage unknown count changed")
    checks.check(compression.get("accepted_h_sweep_present") is False, "velocity compression unexpectedly accepted h-sweep")
    checks.check(compression.get("full_tfe_stage_replacement") is False, "velocity compression unexpectedly claims full TFE")
    checks.check(compression.get("row_space_compression_probe_spanning_row_count") == 0, "row-space compression unexpectedly spans")
    checks.check(compression.get("row_space_coefficient_derivative_probe_row_count") == 36, "row-space coefficient-derivative row count changed")
    checks.check(compression.get("row_space_coefficient_derivative_probe_spanning_row_count") == 36, "row-space coefficient-derivative oracle span count changed")
    checks.check(compression.get("row_space_coefficient_derivative_probe_value_balanced_spanning_row_count") == 24, "row-space coefficient-derivative value-balanced span count changed")
    checks.check(compression.get("row_space_coefficient_derivative_probe_target_direction_oracle_used") is True, "row-space coefficient-derivative lost target-direction oracle marker")
    checks.check(compression.get("row_space_coefficient_derivative_probe_coefficient_derivative_included") is True, "row-space coefficient-derivative lost derivative marker")
    checks.check(as_float(compression, "row_space_coefficient_derivative_probe_best_projection_relative_residual", 1.0) < 1e-12, "row-space coefficient-derivative best residual changed")
    checks.check(compression.get("weak_row_structure_capacity_probe_spanning_row_count") == 0, "weak-row structure unexpectedly spans")

    checks.check(final_stage.get("full_tfe_stage_replacement") is False, "final-stage closure unexpectedly claims full TFE")
    checks.check(blend.get("order_and_terminal_intersection_present") is False, "order/closure intersection unexpectedly present")
    checks.check(near_final.get("order_terminal_intersection_present") is False, "near-final beta boundary unexpectedly has an order/terminal intersection")
    checks.check(near_final.get("near_final_collapse_confirmed") is True, "near-final beta boundary lost collapse marker")
    checks.check(near_final.get("nonfinal_terminal_closed_count") == 0, "near-final beta boundary unexpectedly closes a nonfinal beta")
    checks.check(near_final.get("full_tfe_stage_replacement") is False, "near-final beta boundary unexpectedly claims full TFE")
    checks.check(feedback_gain.get("order_terminal_intersection_present") is False, "recurrent feedback gain boundary unexpectedly has an order/terminal intersection")
    checks.check(feedback_gain.get("terminal_closure_requires_order_collapse") is True, "recurrent feedback gain boundary lost order-collapse marker")
    checks.check(feedback_gain.get("terminal_closed_gain_count") == 5, "recurrent feedback gain boundary terminal-closed count changed")
    checks.check(feedback_gain.get("smooth_order_ok_count") == 1, "recurrent feedback gain boundary smooth-order count changed")
    checks.check(feedback_gain.get("full_tfe_stage_replacement") is False, "recurrent feedback gain boundary unexpectedly claims full TFE")
    checks.check(component_feedback_gain.get("order_terminal_intersection_present") is False, "component recurrent feedback gain boundary unexpectedly has an order/terminal intersection")
    checks.check(component_feedback_gain.get("terminal_closure_requires_order_collapse") is True, "component recurrent feedback gain boundary lost order-collapse marker")
    checks.check(component_feedback_gain.get("terminal_closed_gain_count") == 5, "component recurrent feedback gain boundary terminal-closed count changed")
    checks.check(component_feedback_gain.get("smooth_order_ok_count") == 1, "component recurrent feedback gain boundary smooth-order count changed")
    checks.check(component_feedback_gain.get("full_tfe_stage_replacement") is False, "component recurrent feedback gain boundary unexpectedly claims full TFE")
    checks.check(hscaled_feedback_gain.get("order_terminal_intersection_present") is False, "h-scaled recurrent feedback gain boundary unexpectedly has an order/terminal intersection")
    checks.check(hscaled_feedback_gain.get("terminal_closure_requires_order_collapse") is True, "h-scaled recurrent feedback gain boundary lost order-collapse marker")
    checks.check(hscaled_feedback_gain.get("terminal_closed_row_count") == 7, "h-scaled recurrent feedback gain boundary terminal-closed count changed")
    checks.check(hscaled_feedback_gain.get("smooth_order_ok_count") == 0, "h-scaled recurrent feedback gain boundary smooth-order count changed")
    checks.check(hscaled_feedback_gain.get("full_tfe_stage_replacement") is False, "h-scaled recurrent feedback gain boundary unexpectedly claims full TFE")
    checks.check(source_law_screen.get("order_terminal_intersection_present") is False, "recurrent source-law screen unexpectedly has an order/terminal intersection")
    checks.check(source_law_screen.get("row_count") == 6, "recurrent source-law screen row count changed")
    checks.check(source_law_screen.get("terminal_closed_row_count") == 0, "recurrent source-law screen unexpectedly closes terminal velocity")
    checks.check(source_law_screen.get("smooth_order_ok_count") == 5, "recurrent source-law screen smooth-order count changed")
    checks.check(source_law_screen.get("full_tfe_stage_replacement") is False, "recurrent source-law screen unexpectedly claims full TFE")
    checks.check(three_history_source_law.get("order_terminal_intersection_present") is False, "three-history recurrent source-law screen unexpectedly has an order/terminal intersection")
    checks.check(three_history_source_law.get("row_count") == 4, "three-history recurrent source-law screen row count changed")
    checks.check(three_history_source_law.get("predictor_law_count") == 4, "three-history recurrent source-law screen law count changed")
    checks.check(three_history_source_law.get("three_history_law_count") == 4, "three-history recurrent source-law screen three-history count changed")
    checks.check(three_history_source_law.get("terminal_closed_row_count") == 0, "three-history recurrent source-law screen unexpectedly closes terminal velocity")
    checks.check(three_history_source_law.get("smooth_order_ok_count") == 2, "three-history recurrent source-law screen smooth-order count changed")
    checks.check(three_history_source_law.get("three_history_source_law_trajectory_screen_present") is True, "three-history recurrent source-law screen marker missing")
    checks.check(three_history_source_law.get("full_tfe_stage_replacement") is False, "three-history recurrent source-law screen unexpectedly claims full TFE")
    checks.check(2.8e-7 < as_float(three_history_source_law, "best_terminal_velocity", 0.0) < 3.0e-7, "three-history recurrent source-law screen best terminal velocity changed")
    checks.check(5.33 < as_float(three_history_source_law, "best_smooth_order_min_order", 0.0) < 5.36, "three-history recurrent source-law screen best smooth order changed")
    checks.check(four_history_source_law.get("order_terminal_intersection_present") is False, "four-history recurrent source-law screen unexpectedly has an order/terminal intersection")
    checks.check(four_history_source_law.get("row_count") == 4, "four-history recurrent source-law screen row count changed")
    checks.check(four_history_source_law.get("predictor_law_count") == 4, "four-history recurrent source-law screen law count changed")
    checks.check(four_history_source_law.get("four_history_law_count") == 4, "four-history recurrent source-law screen four-history count changed")
    checks.check(four_history_source_law.get("terminal_closed_row_count") == 0, "four-history recurrent source-law screen unexpectedly closes terminal velocity")
    checks.check(four_history_source_law.get("smooth_order_ok_count") == 2, "four-history recurrent source-law screen smooth-order count changed")
    checks.check(four_history_source_law.get("four_history_source_law_trajectory_screen_present") is True, "four-history recurrent source-law screen marker missing")
    checks.check(four_history_source_law.get("full_tfe_stage_replacement") is False, "four-history recurrent source-law screen unexpectedly claims full TFE")
    checks.check(four_history_source_law.get("best_terminal_law") == "recurrent_fourhistory_velocity_terminal_source01historyslopejerksnap_z", "four-history recurrent source-law screen best terminal law changed")
    checks.check(2.9e-7 < as_float(four_history_source_law, "best_terminal_velocity", 0.0) < 3.0e-7, "four-history recurrent source-law screen best terminal velocity changed")
    checks.check(5.33 < as_float(four_history_source_law, "best_smooth_order_min_order", 0.0) < 5.36, "four-history recurrent source-law screen best smooth order changed")
    checks.check(nonlinear_history_source_law.get("order_terminal_intersection_present") is False, "nonlinear-history recurrent source-law screen unexpectedly has an order/terminal intersection")
    checks.check(nonlinear_history_source_law.get("row_count") == 5, "nonlinear-history recurrent source-law screen row count changed")
    checks.check(nonlinear_history_source_law.get("predictor_law_count") == 5, "nonlinear-history recurrent source-law screen law count changed")
    checks.check(nonlinear_history_source_law.get("nonlinear_history_law_count") == 5, "nonlinear-history recurrent source-law screen nonlinear-history count changed")
    checks.check(nonlinear_history_source_law.get("terminal_closed_row_count") == 0, "nonlinear-history recurrent source-law screen unexpectedly closes terminal velocity")
    checks.check(nonlinear_history_source_law.get("smooth_order_ok_count") == 0, "nonlinear-history recurrent source-law screen unexpectedly meets smooth-order floor")
    checks.check(nonlinear_history_source_law.get("nonlinear_history_source_law_trajectory_screen_present") is True, "nonlinear-history recurrent source-law screen marker missing")
    checks.check(nonlinear_history_source_law.get("full_tfe_stage_replacement") is False, "nonlinear-history recurrent source-law screen unexpectedly claims full TFE")
    checks.check(1.9e-7 < as_float(nonlinear_history_source_law, "best_terminal_velocity", 0.0) < 2.0e-7, "nonlinear-history recurrent source-law screen best terminal velocity changed")
    checks.check(3.50 < as_float(nonlinear_history_source_law, "best_smooth_order_min_order", 0.0) < 3.55, "nonlinear-history recurrent source-law screen best smooth order changed")
    checks.check(source_law_final_retain.get("order_terminal_intersection_present") is False, "recurrent source-law final-retain boundary unexpectedly has an order/terminal intersection")
    checks.check(source_law_final_retain.get("terminal_closure_requires_order_collapse") is True, "recurrent source-law final-retain boundary lost order-collapse marker")
    checks.check(source_law_final_retain.get("row_count") == 16, "recurrent source-law final-retain boundary row count changed")
    checks.check(source_law_final_retain.get("terminal_closed_row_count") == 4, "recurrent source-law final-retain boundary terminal-closed count changed")
    checks.check(source_law_final_retain.get("smooth_order_ok_count") == 0, "recurrent source-law final-retain boundary smooth-order count changed")
    checks.check(source_law_final_retain.get("full_tfe_stage_replacement") is False, "recurrent source-law final-retain boundary unexpectedly claims full TFE")
    for audit, label, expected_rows in [
        (stage2_gradient, "stage2 scalar-gradient differential", 8),
        (stage2_matrix, "stage2 matrix-gradient differential", 32),
    ]:
        checks.check(audit.get("row_count") == expected_rows, f"{label} row count changed")
        checks.check(audit.get("span_row_count") == 0, f"{label} unexpectedly spans terminal bridge")
        checks.check(audit.get("accepted_h_sweep_present") is False, f"{label} unexpectedly accepts an h-sweep")
        checks.check(audit.get("full_tfe_stage_replacement") is False, f"{label} unexpectedly claims full TFE")
        checks.check(0.85 < as_float(audit, "best_projection_relative_residual") < 0.95, f"{label} best residual changed")
    checks.check(stage2_translation_matrix.get("row_count") == 40, "stage2 translation-velocity matrix differential row count changed")
    checks.check(stage2_translation_matrix.get("matrix_law_count") == 10, "stage2 translation-velocity matrix differential law count changed")
    checks.check(stage2_translation_matrix.get("span_row_count") == 0, "stage2 translation-velocity matrix differential unexpectedly spans terminal bridge")
    checks.check(stage2_translation_matrix.get("accepted_h_sweep_present") is False, "stage2 translation-velocity matrix differential unexpectedly accepts an h-sweep")
    checks.check(stage2_translation_matrix.get("full_tfe_stage_replacement") is False, "stage2 translation-velocity matrix differential unexpectedly claims full TFE")
    checks.check(stage2_translation_matrix.get("uses_stage2_translation_velocity_matrix_feature") is True, "stage2 translation-velocity matrix differential lost translation-velocity marker")
    checks.check(0.65 < as_float(stage2_translation_matrix, "best_projection_relative_residual") < 0.70, "stage2 translation-velocity matrix differential best residual changed")
    checks.check(stage2_translation_matrix.get("best_missing_direction_dominant_variable_family") == "angular_velocity_w", "stage2 translation-velocity matrix differential dominant missing variable changed")
    checks.check(stage2_coupled_matrix.get("row_count") == 48, "stage2 translation/angular coupled matrix differential row count changed")
    checks.check(stage2_coupled_matrix.get("matrix_law_count") == 12, "stage2 translation/angular coupled matrix differential law count changed")
    checks.check(stage2_coupled_matrix.get("span_row_count") == 0, "stage2 translation/angular coupled matrix differential unexpectedly spans terminal bridge")
    checks.check(stage2_coupled_matrix.get("accepted_h_sweep_present") is False, "stage2 translation/angular coupled matrix differential unexpectedly accepts an h-sweep")
    checks.check(stage2_coupled_matrix.get("full_tfe_stage_replacement") is False, "stage2 translation/angular coupled matrix differential unexpectedly claims full TFE")
    checks.check(stage2_coupled_matrix.get("uses_stage2_translation_angular_coupled_matrix_feature") is True, "stage2 translation/angular coupled matrix differential lost coupled marker")
    checks.check(0.73 < as_float(stage2_coupled_matrix, "best_projection_relative_residual") < 0.75, "stage2 translation/angular coupled matrix differential best residual changed")
    checks.check(stage2_coupled_matrix.get("best_missing_direction_dominant_variable_family") == "translation_velocity_v", "stage2 translation/angular coupled matrix differential dominant missing variable changed")
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
    checks.check(stage2_dictionary.get("accepted_h_sweep_present") is False, "stage2 feature dictionary unexpectedly accepts an h-sweep")
    checks.check(stage2_dictionary.get("full_tfe_stage_replacement") is False, "stage2 feature dictionary unexpectedly claims full TFE")
    checks.check("coefficient/selection law" in stage2_dictionary.get("next_repair_target", ""), "stage2 feature dictionary next target changed")
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
    checks.check(stage2_coefficient.get("accepted_h_sweep_present") is False, "stage2 coefficient-law screen unexpectedly accepts an h-sweep")
    checks.check(stage2_coefficient.get("full_tfe_stage_replacement") is False, "stage2 coefficient-law screen unexpectedly claims full TFE")
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
    checks.check(0.58 < as_float(stage2_state_coefficient, "best_projection_relative_residual", 1.0) < 0.60, "stage2 state-feature coefficient-derivative screen best residual changed")
    checks.check(stage2_state_coefficient.get("target_free_coefficient_derivative") is True, "stage2 state-feature coefficient-derivative screen lost target-free marker")
    checks.check(stage2_state_coefficient.get("coefficient_derivative_included") is True, "stage2 state-feature coefficient-derivative screen lost derivative marker")
    checks.check(stage2_state_coefficient.get("target_jacobian_used_for_formula") is False, "stage2 state-feature coefficient-derivative screen unexpectedly uses target Jacobian")
    checks.check(stage2_state_coefficient.get("target_direction_oracle_used") is False, "stage2 state-feature coefficient-derivative screen unexpectedly uses target direction")
    checks.check("richer state-dependent coefficient features" in stage2_state_coefficient.get("next_repair_target", ""), "stage2 state-feature coefficient-derivative screen next target changed")
    checks.check(hscaled_endpoint_pose.get("row_count") == 12, "h-adaptive endpoint-pose predictor row count changed")
    checks.check(hscaled_endpoint_pose.get("predictor_law_count") == 4, "h-adaptive endpoint-pose predictor law count changed")
    checks.check(hscaled_endpoint_pose.get("hscaled_endpoint_pose_velocity_predictor") is True, "h-adaptive endpoint-pose predictor lost h-scaled marker")
    checks.check(hscaled_endpoint_pose.get("projection_used") is False, "h-adaptive endpoint-pose predictor unexpectedly uses projection")
    checks.check(hscaled_endpoint_pose.get("terminal_row_replacement_used") is False, "h-adaptive endpoint-pose predictor unexpectedly replaces terminal rows")
    checks.check(hscaled_endpoint_pose.get("terminal_velocity_closed") is False, "h-adaptive endpoint-pose predictor unexpectedly closes all terminal velocities")
    checks.check(hscaled_endpoint_pose.get("smooth_order_ok") is False, "h-adaptive endpoint-pose predictor unexpectedly reaches smooth order")
    checks.check(hscaled_endpoint_pose.get("accepted_h_sweep_present") is False, "h-adaptive endpoint-pose predictor unexpectedly accepts an h-sweep")
    checks.check(hscaled_endpoint_pose.get("full_tfe_stage_replacement") is False, "h-adaptive endpoint-pose predictor unexpectedly claims full TFE")
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
    checks.check(bounded_requirement.get("bounded_gradient_practical_cap_spanning_row_count") == 12, "bounded tangent requirement practical cap count changed")
    checks.check(bounded_requirement.get("weak_row_structure_span_count") == 0, "bounded tangent requirement weak-row count changed")
    checks.check(bounded_requirement.get("accepted_h_sweep_present") is False, "bounded tangent requirement unexpectedly accepts h-sweep")
    checks.check(bounded_requirement.get("full_tfe_stage_replacement") is False, "bounded tangent requirement unexpectedly claims full TFE")
    checks.check("stage-local weak-row tangent" in bounded_requirement.get("next_repair_contract", ""), "bounded tangent requirement target changed")

    return {
        "stage_row_budget": contract.get("stage_row_budget"),
        "row_families": contract.get("row_count"),
        "source_consistency_rows": compression.get("source_consistency_rows"),
        "target_rows": compression.get("target_row_count"),
        "velocity_stage_rows": compression.get("velocity_stage_rows"),
        "bounded_requirement_rows": bounded_requirement.get("requirement_row_count"),
        "bounded_requirement_target_free_formula_spans": bounded_requirement.get("target_free_formula_span_count"),
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
        "next_repair_target": (
            "derive a revised analytical weak-row formula or nonlinear recurrent history source law for the "
            "independent lower-pair closure"
        ),
    }


def check_gap_ledger_alignment(checks: Checks, gap_text: str) -> None:
    for token in [
        "Acceptance Definition",
        "revised analytical weak-row formula",
        "nonlinear recurrent history source law",
        "three-history recurrent source law",
        "four-history recurrent source-law",
        "source-law final-retain boundary",
        "translation-velocity matrix",
        "translation/angular coupled matrix",
        "h-adaptive endpoint-pose velocity predictor",
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
        "cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_four_history_source_law_trajectory_screen_audit",
        "four_history_source_law_trajectory_screen_present",
        "bounded tangent requirement audit",
        "requirement_row_count=7",
        "target_free_formula_span_count=0",
        "full_tfe_stage_replacement=false",
    ]:
        checks.check(token in gap_text, f"gap ledger missing token required by repair spec: {token}")


def main() -> int:
    checks = Checks()
    try:
        summary = read_json(SUMMARY)
        spec = read_text(SPEC)
        gap_text = read_text(GAP_LEDGER)
        run_text = read_text(RUN_SCRIPT)
        check_spec_text(checks, spec)
        check_run_script_slots(checks, run_text)
        check_gap_ledger_alignment(checks, gap_text)
        report = check_summary_alignment(checks, summary)
    except Exception as exc:  # noqa: BLE001 - command-line validator reports fatal read/parse issues.
        print("v047 full-TFE repair spec validation: FAIL")
        print(f"fatal={exc}")
        return 1

    if checks.errors:
        print("v047 full-TFE repair spec validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("v047 full-TFE repair spec validation: PASS")
    print(f"stage_row_budget={report['stage_row_budget']}")
    print(f"paper_row_families={report['row_families']}")
    print(f"source_consistency_rows={report['source_consistency_rows']}")
    print(f"target_closure_rows={report['target_rows']}")
    print(f"velocity_stage_rows={report['velocity_stage_rows']}")
    print(f"bounded_requirement_rows={report['bounded_requirement_rows']}")
    print(f"bounded_requirement_target_free_formula_spans={report['bounded_requirement_target_free_formula_spans']}")
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
    print("candidate_scaffold_present=True")
    print("candidate_jax_callables_present=True")
    print("candidate_step_integrator_present=True")
    print("full_tfe_stage_replacement=False")
    print(f"next_repair_target={report['next_repair_target']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
