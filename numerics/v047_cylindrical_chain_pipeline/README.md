# v047 Cylindrical Chain Pipeline

This version starts the post-v046 research round under the new pipeline gate.
It promotes the pending cylindrical scratch into a formal version and changes
the v044 two-body prismatic chain into a two-body cylindrical chain:

- joint 0: ground-to-body cylindrical joint;
- joint 1: interbody cylindrical joint whose axis moves with body 0.

Compared with v044, each joint keeps the two perpendicular point constraints
and two axis-alignment constraints, but it no longer locks the twist reference.
The axial slide and relative spin about the joint axis are treated as free
collocated coordinates.

Run:

```bash
../.venv_sbel/bin/python run_v047.py
```

Quick four-example method-gate check only:

```bash
../.venv_sbel/bin/python validate_four_asme_minimal.py
```

This read-only check verifies the existing ASME gate artifacts without
regenerating the historical audit suite. Use it when the question is only
whether the four examples are accepted.

Validate generated outputs:

```bash
../.venv_sbel/bin/python validate_v047_outputs.py
```

The validator is read-only. It checks the 292 generated result files, 147 CSV tables, 120 PNG plots, summary gate status, stale wording, and README/report
artifact lists.

Generated outputs:

- `results/v047_report.md`
- `results/summary_v047.json`
- `results/cylindrical_chain_runs.csv`
- `results/cylindrical_chain_runtime.png`
- `results/cylindrical_chain_patterns.png`
- `results/cylindrical_chain_sparse_runtime_repeats.csv`
- `results/cylindrical_chain_sparse_runtime_repeats.png`
- `results/cylindrical_chain_sparse_speed_gap_audit.csv`
- `results/cylindrical_chain_sparse_speed_gap_audit.png`
- `results/cylindrical_chain_sparse_cost_model_audit.csv`
- `results/cylindrical_chain_sparse_cost_model_audit.png`
- `results/cylindrical_chain_convergence.csv`
- `results/cylindrical_chain_convergence.png`
- `results/cylindrical_chain_friction_smoothness_sweep.csv`
- `results/cylindrical_chain_friction_smoothness_sweep.png`
- `results/cylindrical_chain_sharp_adaptive_step_doubling.csv`
- `results/cylindrical_chain_sharp_adaptive_step_doubling.png`
- `results/cylindrical_chain_sharp_adaptive_tolerance_convergence.csv`
- `results/cylindrical_chain_sharp_adaptive_tolerance_convergence.png`
- `results/cylindrical_chain_sharp_fixed_refinement_audit.csv`
- `results/cylindrical_chain_sharp_fixed_refinement_audit.png`
- `results/cylindrical_chain_sharp_deep_refinement_audit.csv`
- `results/cylindrical_chain_sharp_deep_refinement_audit.png`
- `results/cylindrical_chain_sharp_ultra_refinement_audit.csv`
- `results/cylindrical_chain_sharp_ultra_refinement_audit.png`
- `results/cylindrical_chain_sharp_refinement_cost_envelope_audit.csv`
- `results/cylindrical_chain_sharp_refinement_cost_envelope_audit.png`
- `results/cylindrical_chain_endpoint_projection_audit.csv`
- `results/cylindrical_chain_endpoint_projection_audit.png`
- `results/cylindrical_chain_endpoint_kkt_closure.csv`
- `results/cylindrical_chain_endpoint_kkt_closure.png`
- `results/cylindrical_chain_endpoint_tfe_gap_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_gap_audit.png`
- `results/cylindrical_chain_endpoint_tfe_candidate_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_candidate_audit.png`
- `results/cylindrical_chain_endpoint_tfe_solved_candidate_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_solved_candidate_audit.png`
- `results/cylindrical_chain_endpoint_tfe_stage_weighted_candidate_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_stage_weighted_candidate_audit.png`
- `results/cylindrical_chain_endpoint_tfe_stage_functional_spec_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_stage_functional_spec_audit.png`
- `results/cylindrical_chain_endpoint_tfe_stage_functional_implementation_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_stage_functional_implementation_audit.png`
- `results/cylindrical_chain_endpoint_tfe_stage_non_equivalent_probe_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_stage_non_equivalent_probe_audit.png`
- `results/cylindrical_chain_endpoint_tfe_stage_probe_boundary_source_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_stage_probe_boundary_source_audit.png`
- `results/cylindrical_chain_endpoint_tfe_stage_probe_source_budget_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_stage_probe_source_budget_audit.png`
- `results/cylindrical_chain_endpoint_tfe_stage_probe_dominant_source_split_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_stage_probe_dominant_source_split_audit.png`
- `results/cylindrical_chain_endpoint_tfe_stage_probe_order_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_stage_probe_order_audit.png`
- `results/cylindrical_chain_endpoint_tfe_stage_non_equivalent_solved_probe_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_stage_non_equivalent_solved_probe_audit.png`
- `results/cylindrical_chain_endpoint_tfe_stage_probe_homotopy_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_stage_probe_homotopy_audit.png`
- `results/cylindrical_chain_endpoint_tfe_stage_probe_block_activation_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_stage_probe_block_activation_audit.png`
- `results/cylindrical_chain_endpoint_tfe_stage_probe_component_activation_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_stage_probe_component_activation_audit.png`
- `results/cylindrical_chain_endpoint_tfe_stage_probe_component_formula_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_stage_probe_component_formula_audit.png`
- `results/cylindrical_chain_endpoint_tfe_stage_probe_newton_euler_formula_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_stage_probe_newton_euler_formula_audit.png`
- `results/cylindrical_chain_endpoint_tfe_stage_probe_all_source_formula_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_stage_probe_all_source_formula_audit.png`
- `results/cylindrical_chain_endpoint_tfe_stage_probe_all_source_trajectory_bridge_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_stage_probe_all_source_trajectory_bridge_audit.png`
- `results/cylindrical_chain_endpoint_tfe_full_stage_acceptance_gap_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_full_stage_acceptance_gap_audit.png`
- `results/cylindrical_chain_endpoint_tfe_stage_local_source_removal_target_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_stage_local_source_removal_target_audit.png`
- `results/cylindrical_chain_endpoint_tfe_stage_probe_coupled_budget_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_stage_probe_coupled_budget_audit.png`
- `results/cylindrical_chain_endpoint_tfe_stage_probe_trajectory_accumulation_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_stage_probe_trajectory_accumulation_audit.png`
- `results/cylindrical_chain_endpoint_tfe_stage_probe_beta_trajectory_bridge_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_stage_probe_beta_trajectory_bridge_audit.png`
- `results/cylindrical_chain_endpoint_tfe_stage_replacement_design_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_stage_replacement_design_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_formula_mapping_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_formula_mapping_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_derivative_operator_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_derivative_operator_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_stage_input_map_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_stage_input_map_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_multiplier_policy_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_multiplier_policy_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_kinematic_formula_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_kinematic_formula_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_balance_constraint_formula_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_balance_constraint_formula_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_position_substitution_candidate_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_position_substitution_candidate_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_kinematic_substitution_candidate_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_kinematic_substitution_candidate_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_all_row_substitution_candidate_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_all_row_substitution_candidate_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_all_row_gauss_z0_substitution_candidate_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_all_row_gauss_z0_substitution_candidate_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_all_row_gauss_z0_terminal_output_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_all_row_gauss_z0_terminal_output_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_all_row_recurrent_z0_terminal_output_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_all_row_recurrent_z0_terminal_output_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_all_row_consistent_z0_terminal_output_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_all_row_consistent_z0_terminal_output_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_all_row_consistent_z0_conditioning_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_all_row_consistent_z0_conditioning_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_all_row_consistent_z0_scaled_newton_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_all_row_consistent_z0_scaled_newton_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_family_ablation_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_family_ablation_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_lambda_schur_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_lambda_schur_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_row_variant_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_row_variant_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_acceleration_terminal_output_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_acceleration_terminal_output_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_acceleration_projection_dependence_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_acceleration_projection_dependence_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_acceleration_terminal_velocity_closure_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_acceleration_terminal_velocity_closure_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_acceleration_terminal_row_homotopy_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_acceleration_terminal_row_homotopy_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_terminal_source_target_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_terminal_source_target_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_terminal_source_lift_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_terminal_source_lift_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_terminal_source_normalization_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_terminal_source_normalization_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_terminal_source_insertion_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_terminal_source_insertion_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_terminal_source_insertion_trajectory_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_terminal_source_insertion_trajectory_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_terminal_source_insertion_blowup_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_terminal_source_insertion_blowup_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_terminal_source_bounded_policy_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_terminal_source_bounded_policy_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_stage_local_bounded_source_formula_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_stage_local_bounded_source_formula_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_direct_endpoint_velocity_source_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_direct_endpoint_velocity_source_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_direct_source_residual_substitution_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_direct_source_residual_substitution_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_residual_derived_stage_source_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_residual_derived_stage_source_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_self_consistent_endpoint_source_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_self_consistent_endpoint_source_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_source_free_elimination_rank_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_source_free_elimination_rank_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_source_free_mean_velocity_closure_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_source_free_mean_velocity_closure_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_source_free_final_stage_velocity_closure_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_source_free_final_stage_velocity_closure_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_source_free_order_closure_blend_trajectory_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_source_free_order_closure_blend_trajectory_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_source_free_near_final_beta_boundary_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_source_free_near_final_beta_boundary_audit.json`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_feedback_gain_boundary_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_feedback_gain_boundary_audit.json`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_component_feedback_gain_boundary_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_component_feedback_gain_boundary_audit.json`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_candidate_frontier_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_candidate_frontier_audit.json`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_bounded_tangent_requirement_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_bounded_tangent_requirement_audit.json`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_hscaled_feedback_gain_boundary_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_hscaled_feedback_gain_boundary_audit.json`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_source_law_trajectory_screen_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_source_law_trajectory_screen_audit.json`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_three_history_source_law_trajectory_screen_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_three_history_source_law_trajectory_screen_audit.json`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_four_history_source_law_trajectory_screen_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_four_history_source_law_trajectory_screen_audit.json`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_nonlinear_history_source_law_trajectory_screen_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_nonlinear_history_source_law_trajectory_screen_audit.json`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_source_law_final_retain_boundary_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_source_law_final_retain_boundary_audit.json`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_source_free_mean_blend_closure_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_source_free_mean_blend_closure_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_source_free_mean_blend_trajectory_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_source_free_mean_blend_trajectory_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_source_free_mean_blend_trajectory_alpha_sweep_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_source_free_mean_blend_trajectory_alpha_sweep_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_source_free_component_blend_trajectory_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_source_free_component_blend_trajectory_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_source_free_terminal_velocity_extrapolation_trajectory_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_source_free_terminal_velocity_extrapolation_trajectory_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_source_free_terminal_extrapolation_blend_trajectory_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_source_free_terminal_extrapolation_blend_trajectory_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_centered_terminal_velocity_bridge_trajectory_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_centered_terminal_velocity_bridge_trajectory_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_closure_acceptance_matrix_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_closure_acceptance_matrix_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_closure_property_pareto_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_closure_property_pareto_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_closure_row_span_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_closure_row_span_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_velocity_basis_span_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_velocity_basis_span_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_gradient_differential_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_gradient_differential_audit.json`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_matrix_gradient_differential_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_matrix_gradient_differential_audit.json`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_translation_velocity_matrix_differential_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_translation_velocity_matrix_differential_audit.json`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_translation_angular_coupled_matrix_differential_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_translation_angular_coupled_matrix_differential_audit.json`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_feature_dictionary_span_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_feature_dictionary_span_audit.json`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_feature_coefficient_law_screen_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_feature_coefficient_law_screen_audit.json`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_state_feature_coefficient_derivative_screen_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_state_feature_coefficient_derivative_screen_audit.json`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_endpoint_pose_velocity_predictor_h_sweep_smoke.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_endpoint_pose_velocity_predictor_h_sweep_smoke.json`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_endpoint_pose_velocity_hscaled_predictor_h_sweep_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_endpoint_pose_velocity_hscaled_predictor_h_sweep_audit.json`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_endpoint_pose_velocity_hscaled_response_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_endpoint_pose_velocity_hscaled_response_audit.json`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_endpoint_pose_velocity_predictor_reference_output_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_endpoint_pose_velocity_predictor_reference_output_audit.json`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_velocity_compression_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_velocity_compression_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_velocity_compression_nondegenerate_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_velocity_compression_nondegenerate_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_velocity_compression_state_dependent_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_velocity_compression_state_dependent_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_velocity_compression_component_mixing_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_velocity_compression_component_mixing_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_velocity_compression_value_level_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_velocity_compression_value_level_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_velocity_compression_derivative_aware_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_velocity_compression_derivative_aware_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_velocity_compression_bounded_gradient_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_velocity_compression_bounded_gradient_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_velocity_compression_bounded_formula_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_velocity_compression_bounded_formula_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_velocity_compression_target_free_formula_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_velocity_compression_target_free_formula_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_velocity_compression_direction_capacity_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_velocity_compression_direction_capacity_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_velocity_compression_nonlinear_capacity_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_velocity_compression_nonlinear_capacity_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_velocity_compression_higher_order_capacity_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_velocity_compression_higher_order_capacity_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_velocity_compression_history_capacity_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_velocity_compression_history_capacity_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_velocity_compression_multi_step_history_capacity_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_velocity_compression_multi_step_history_capacity_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_velocity_compression_recurrent_history_capacity_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_velocity_compression_recurrent_history_capacity_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_velocity_compression_weak_row_structure_capacity_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_velocity_compression_weak_row_structure_capacity_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_velocity_compression_row_space_compression_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_velocity_compression_row_space_compression_audit.png`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_velocity_compression_row_space_coefficient_derivative_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_lower_pair_velocity_compression_row_space_coefficient_derivative_audit.json`
- `results/cylindrical_chain_endpoint_tfe_paper_residual_substitution_contract_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_paper_residual_substitution_contract_audit.png`
- `results/cylindrical_chain_endpoint_tfe_readiness_audit.csv`
- `results/cylindrical_chain_endpoint_tfe_readiness_audit.png`
- `results/cylindrical_chain_asme_gate.csv`
- `results/cylindrical_chain_asme_method_runs.csv`
- `results/cylindrical_chain_asme_single_driven_runs.csv`
- `results/cylindrical_chain_asme_single_driven.png`
- `results/cylindrical_chain_asme_single_fullva_runs.csv`
- `results/cylindrical_chain_asme_single_fullva_timeseries.csv`
- `results/cylindrical_chain_asme_single_fullva.png`
- `results/cylindrical_chain_asme_single_absolute_fullva_runs.csv`
- `results/cylindrical_chain_asme_single_absolute_fullva_timeseries.csv`
- `results/cylindrical_chain_asme_single_absolute_fullva.png`
- `results/cylindrical_chain_asme_single_reaction_runs.csv`
- `results/cylindrical_chain_asme_single_reaction_timeseries.csv`
- `results/cylindrical_chain_asme_single_reaction.png`
- `results/cylindrical_chain_asme_double_method_runs.csv`
- `results/cylindrical_chain_asme_double_method.png`
- `results/cylindrical_chain_asme_double_v046_comparison.csv`
- `results/cylindrical_chain_asme_double_v046_comparison.png`
- `results/cylindrical_chain_asme_double_reference_floor.csv`
- `results/cylindrical_chain_asme_double_reference_floor.png`
- `results/cylindrical_chain_asme_double_reference_policy.csv`
- `results/cylindrical_chain_asme_double_reference_policy.png`
- `results/cylindrical_chain_asme_lower_pair_graph_bridge.csv`
- `results/cylindrical_chain_asme_lower_pair_graph_bridge.png`
- `results/cylindrical_chain_asme_lower_pair_rank_audit.csv`
- `results/cylindrical_chain_asme_lower_pair_rank_audit.png`
- `results/cylindrical_chain_asme_closed_loop_kinematic_fullva.csv`
- `results/cylindrical_chain_asme_closed_loop_kinematic_fullva.png`
- `results/cylindrical_chain_asme_closed_loop_reaction_dynamics.csv`
- `results/cylindrical_chain_asme_closed_loop_reaction_dynamics.png`

Pipeline status:

- math proof/status: `ORDER_PROOF_LEDGER.md` records the direct-route
  conditional Gauss6/FullVA proof boundary: the 132-row residual bridge is
  closed by the 96-row non-dynamic certificate plus P5 Newton--Euler direct
  substitution, while P1/P2/P3/P4/P6 remain retained theorem interfaces;
- four ASME examples: v046 baseline is ingested; exact single-pendulum driven
  FullVA evidence, accepted double-pendulum FullVA reference-policy evidence,
  a four-example lower-pair constraint-graph bridge, and a four-example
  `Phi_q` full-row-rank audit are recorded; local closed-loop kinematic FullVA
  solves and reaction-dynamics rows for four_link and slider_crank are accepted;
- convergence analysis: initial dense h-sweep is present; smooth convergence is
  high order after initial velocity compatibility repair, while sharp friction
  remains order-reduced; a Brown-McPhee smoothness sweep records position/
  velocity orders 7.161/7.066, 6.494/5.657, 3.392/4.511, and 1.894/2.683 for
  stribeck velocities 0.50, 0.20, 0.10, and 0.05; a sharp adaptive
  step-doubling diagnostic reduces the vs=0.05 velocity error from 5.70e-05
  at fixed h=0.01 to 3.81e-07 at 3.2x runtime, but remains diagnostic rather
  than a restored-order proof; the adaptive tolerance/work fit records velocity
  slopes 0.881 over all tolerances and 1.710 over the two looser tolerances,
  with a finest-pair reference-floor flag; the sharp fixed-refinement audit
  over h=[0.02,0.01,0.005] against h=0.0025 records all-point position/velocity
  orders 3.294/5.867 and tail orders 5.364/8.437, so the finest velocity error
  improves strongly while position remains slightly below the high-order target;
  the deeper audit over h=[0.01,0.005,0.0025] against h=0.00125 records
  all-point position/velocity orders 6.398/5.870 and tail orders 7.423/3.177,
  while the ultra audit over h=[0.005,0.0025,0.00125] against h=0.000625
  recovers all-point position/velocity orders 7.521/5.725 and tail orders
  7.626/8.279; the sharp refinement cost-envelope audit uses h=0.01 as the
  practical baseline and shows that the finest high-order window h=0.00125
  costs 7.76x runtime, 8.0x steps, and 8.0x Newton iterations while reducing
  velocity error by 1.06e6x, so the remaining sharp-friction caveat is practical
  cost/coarse-regime reduction rather than asymptotic failure;
- sparse backend: row-colored VJP now assembles the same 2637-entry pruned
  pattern with 60 row colors instead of 90 column colors and preserves
  roundoff trajectory agreement; a five-repeat warmed benchmark records median
  row/column runtimes 0.983x smooth and 1.022x sharp, while dense `jacfwd`
  remains faster on this 132D residual with dense/row 0.830x and 0.828x; the
  sparse speed gap audit records that row-VJP still needs about 1.204x smooth
  and 1.208x sharp additional speedup to match the current dense medians; the
  sparse cost-model audit records that row-VJP runtime must drop by 17.0% smooth
  and 17.2% sharp to match dense, or by 25.3% smooth and 25.5% sharp for a 10%
  dense win, with dense-equivalent row colors 49.8 smooth and 49.7 sharp;
- endpoint closure: post-step least-squares velocity projection is still active,
  but the endpoint-projection audit records raw residual/correction orders
  5.817/5.796 for smooth and 4.089/4.202 for sharp; an augmented endpoint KKT
  residual closure is also present, with smooth/sharp position-velocity orders
  7.161/7.066 and 1.894/2.683 and endpoint velocity residuals below 3.8e-16;
  an endpoint TFE gap audit records finest KKT/projection correction ratios
  0.213 smooth and 0.999 sharp, but also flags the stage equations as not yet
  TFE-weighted; the endpoint TFE candidate audit evaluates endpoint-node
  weighted rows on the KKT h-sweep, with max candidate residuals 1.177e-12
  smooth and 5.723e-13 sharp; the solved endpoint-node candidate audit then
  solves those endpoint rows inside a square residual with max solved residuals
  6.643e-14 smooth and 5.723e-12 sharp, while still leaving stage equations
  non-TFE-weighted; the stage-weighted candidate premultiplies each Gauss6
  FullVA stage block by sqrt(h*b_i), with max weighted residuals 6.819e-15
  smooth and 3.017e-13 sharp, while remaining diagonal-equivalent to the
  Gauss6 equations; the stage-functional specification audit records 6
  independent weak/TFE row families totaling the 132-row stage budget, and the
  implementation audit verifies those rows over the smooth/sharp h-sweep with
  max equivalence norm 1.755e-17; the audit remains Gauss6-equivalent rather
  than full TFE. A non-equivalent stage probe audit evaluates endpoint-boundary
  correction terms over the smooth/sharp h-sweep with max probe norm 8.352e-11.
  A stage-probe boundary-source audit records 36 block/h rows, reconstructing
  every probe block from endpoint-boundary source seeds lifted by sqrt(h*b_i)
  with max lift error 0.000e+00 and max lift-ratio deviation 2.220e-16; it
  verifies the current probe source without claiming the derived full-TFE weak
  stage functional. A stage-probe source-budget audit compresses those rows
  into 6 case/h budgets, verifies the aggregate lifted L2 ratio to 3.331e-16,
  and identifies `newton_euler_weak_balance` as the dominant source family in
  both smooth and sharp cases. A stage-probe block-order audit records 12 block/case rows with max gap
  7.744e-11 and gap-order range 3.918/7.384, and a solved probe audit places that term inside the square Newton residual
  with max residual 2.192e-12 and max probe norm 8.383e-11. A stage-probe beta
  homotopy solves 30 one-step rows over h=[0.04,0.02,0.01] and beta=[0,0.25,0.5,0.75,1],
  with max residual 4.029e-15 and max probe norm 2.348e-11; this is continuation
  evidence, not the derived full-TFE stage functional. A stage-probe block-activation
  audit solves 36 isolated block rows over the same h-sweep with max residual
  1.696e-15 and max activated probe norm 2.177e-11; this narrows the derived-row
  target but remains probe evidence rather than full TFE. A stage-probe
  component-activation audit targets the dominant body0 translational
  Newton-Euler source component with 6 isolated component rows, max residual
  1.195e-15, max activated component probe norm 2.006e-11, and max lift-ratio
  deviation 2.220e-16; this narrows the weak-balance target but remains
  endpoint-boundary probe evidence rather than the derived row formula. A stage-probe
  coupled-budget audit compares the isolated block L2 budget with the full beta=1
  one-step probe; max beta1/isolated-L2 deviation is 1.480e-02 and max
  solved/beta1 probe ratio is 1.292e+02, so it is block-coupling evidence rather
  than a derived full-TFE stage functional. A trajectory-accumulation audit
  compares that local beta=1 probe with the solved h-sweep probe; max
  solved/beta1 remains 1.292e+02 and max per-step ratio is 1.615e+01, so
  trajectory accumulation is quantified but still not a derived full-TFE stage
  functional. A beta-trajectory bridge audit now solves full trajectories for
  beta=[0,0.5,1] over h=[0.04,0.02,0.01] against same-beta h=0.005 references;
  it records 18 rows, max residual 2.192e-12, and max probe norm 8.383e-11
  while still keeping `full_tfe_stage_replacement=false`. A stage-probe
  dominant-source split audit records 24 component/h rows for the
  `newton_euler_weak_balance` source family, splits it into body-local
  translational/rotational balance components, verifies the componentwise
  sqrt(h*b_i) lift to 2.220e-16, and identifies body0 translational balance as
  the dominant next weak-row target in both smooth and sharp cases. The stage-replacement
  design audit records the 132-row stage budget, the solved 40-row endpoint
  extension, the probe audits, and the still-missing independent full-TFE stage
  functional; a stage-probe component-formula audit inserts the dominant body0
  translational weak-balance component by the direct formula
  `sqrt(h*b_i)*m0*delta_v0`, solves 6 smooth/sharp h-sweep rows with max
  residual 1.258e-15, zero formula/generic component difference, and
  lift-ratio deviation 2.220e-16, but still does not claim a full-TFE stage
  replacement. A stage-local source-removal target audit now maps all 36
  case/block/h endpoint-boundary source rows onto six stage-local weak-row
  replacement targets, keeps `endpoint_boundary_source_removed=false`, and
  preserves the full-TFE replacement blocker; the endpoint TFE readiness audit
  records 31 satisfied, 35 partial, and 1 missing
  check, with full TFE stage replacement still missing; the paper-formula
  derivative-operator audit validates the encoded m=3 Lobatto alpha/beta/gamma
  map as a reusable x-to-y/z operator over the 6N+C augmented dimension, and
  the paper stage-input-map audit covers all 132 v047 stage rows across six row
  families. The paper multiplier-policy audit specifies lambda_x/lambda_yz
  dimensions 24/48 with no extra lambda_y/z residual rows. The paper
  kinematic-formula audit derives four kinematic row-family formulas
  (`v-y_r`, `J_r(u)^{-1}w-y_u`, `a-z_r`, and `d/dt[J_r(u)^{-1}w]-z_u`)
  across 72 stage rows with max formula residual 7.26e-18, but does not
  substitute them into Newton. The paper balance/constraint formula audit
  derives the remaining Newton-Euler and lower-pair row-family formulas across
  60 stage rows with max formula residual 4.34e-19, but does not substitute them
  into Newton. The paper position-substitution candidate replaces the two
  paper position row families inside Newton, covering 36 stage rows with max
  residual 5.68e-12 and full rank 132, but its smooth/sharp position-velocity
  orders 1.227/0.731 and 1.165/2.464 are order-limited. The paper
  kinematic-substitution candidate replaces all four paper kinematic row
  families inside Newton, covering 72 stage rows with max residual 9.57e-12 and
  full rank 132, but its diagnostic z0 policy, max condition 8.81e11, and
  smooth/sharp orders 1.406/1.542 and 1.400/1.237 keep it partial. The paper
  all-row substitution candidate combines all six paper row families in one
  132-row Newton residual, with max residual 9.64e-12, kinematic-row residual
  8.69e-12, balance/constraint-row residual 6.87e-12, full rank 132, max
  condition 1.62e13, smooth/sharp position-velocity orders 1.406/1.542 and
  1.400/1.237, and `full_tfe_stage_replacement=false`; it remains
  diagnostic-z0/order-limited and is not accepted as a full TFE replacement.
  The paper all-row Gauss-z0 diagnostic repeats the six-family/132-row
  substitution with a baseline-Gauss extrapolated start acceleration, gives max
  residual 7.70e-12, full rank 132, max condition 1.58e13, max z0 delta
  1.69e1, and smooth/sharp orders 1.410/1.573 and 1.395/1.170, showing the
  low-order blocker is not removed by replacing the axis-projected z0 heuristic
  alone. The paper all-row recurrent-z0 terminal-output diagnostic solves the
  same six-family/132-row residual, bootstraps z0 once from the Gauss stage
  extrapolation, then recurs the terminal paper z value into the next step; it
  gives max residual 9.09e-12, full rank 132, max condition 1.58e13, max
  used-z0-vs-Gauss delta 4.16e-01, and smooth/sharp orders 4.557/4.667 and
  2.579/1.925, improving the start-policy diagnostic while still failing the
  accepted full-TFE replacement gate because bootstrap, order, and conditioning
  caveats remain. The paper all-row consistent-z0 terminal-output diagnostic
  replaces the one-step Gauss bootstrap by an instantaneous 20D
  acceleration/multiplier solve; it gives initial z0 residual 5.94e-15,
  initial rank/condition 20/1.66e1, bootstrap count 0, max all-row residual
  9.79e-12, full rank 132, max condition 1.58e13, and smooth/sharp
  position-velocity orders 4.046/4.420 and 2.554/1.918. This isolates the
  bootstrap hypothesis but remains diagnostic because accepted order and
  conditioning are still open. The paper all-row consistent-z0 conditioning
  audit records 6 one-step rows with max residual 7.03e-12, full rank 132,
  max raw/equilibrated conditions 1.58e13/5.07e4, raw-to-equilibrated
  reduction 3.15e8, and dominant near-null row/variable families
  `lower_pair_index3_weak_constraints`/`lower_pair_lambda`; this localizes the
  conditioning blocker but remains partial and not a full-TFE h-sweep
  acceptance. The paper all-row consistent-z0 scaled-Newton diagnostic solves
  the same six-family/132-row residual with iterative row/column equilibration
  inside Newton; it records max residual 8.78e-12, raw/scaled max conditions
  1.58e13/5.13e4, raw-to-scaled reduction 3.80e8, scaled-vs-raw terminal
  position/velocity deltas 1.21e-14/2.72e-13, and the same smooth/sharp
  orders 4.046/4.420 and 2.554/1.918. This shows scaling repairs the linear
  conditioning diagnosis but does not by itself recover accepted full-TFE
  order. The paper family-ablation diagnostic then solves 12 one-step rows
  over two five-family variants: kinematic+Newton-Euler rows and
  kinematic+lower-pair rows. Both variants remain full-rank and residual-clean,
  but the near-null family remains
  `lower_pair_index3_weak_constraints`/`lower_pair_lambda`; the worst raw
  condition is 1.58e13 when lower-pair rows are substituted and 8.61e11 when
  they remain Gauss rows, so the lower-pair/lambda algebra is localized as the
  next full-TFE formulation target without claiming full replacement. The paper
  lower-pair/lambda Schur diagnostic solves 6 one-step rows on the same
  six-family residual, partitions lower-pair rows against lambda columns, finds
  the direct lower-row/lambda block is zero, and records a full-rank Schur block
  with max condition 5.98e3. Its Schur-ordered Newton direction check records
  max linear residual 1.15e-14 and max relative direction difference 7.79e-09
  versus the raw solve, so changing only the linear-solve ordering is not enough
  to recover accepted full-TFE order; it keeps `full_tfe_stage_replacement=false`.
  The paper lower-pair acceleration terminal-output h-sweep diagnostic runs the
  acceleration-level lower-pair row over 6 smooth/sharp trajectory rows, records
  max terminal lower-pair residual 8.35e-12, full rank 132, raw/scaled max
  conditions 4.37e8/5.83e3, and smooth/sharp position-velocity orders
  4.937/4.799 and 2.555/1.918. It is useful localized evidence, but it remains
  `accepted_h_sweep_present=false` and `full_tfe_stage_replacement=false`
  because endpoint-position closure and accepted full-TFE order are still open.
  A paired projection-dependence audit now compares the raw terminal paper
  output against the endpoint-velocity-projected terminal state on the same 6
  trajectory rows. It records max raw/projected endpoint velocity residuals
  7.99e-06/9.66e-15, max projection delta 7.92e-06, and 6/6 rows requiring
  projection for the velocity gate, so the diagnostic explicitly preserves
  `full_tfe_stage_replacement=false`.
  A terminal-velocity closure audit then replaces only the final stage
  lower-pair acceleration rows with 8 weighted raw terminal endpoint-velocity
  rows. It closes the raw terminal velocity residual to 5.80e-16 without
  output projection, with max closure residual 9.73e-12, rank 132, raw/scaled
  max conditions 1.28e10/7.99e4, smooth/sharp position-velocity orders
  3.459/4.838 and 2.555/1.918, and max replaced terminal lower-pair
  acceleration row 2.53e-4. It remains diagnostic because those terminal
  lower-pair acceleration rows are replaced rather than derived from an
  independent full-TFE stage functional; `full_tfe_stage_replacement=false`.
  A terminal-row homotopy audit then solves 30 one-step rows over
  beta=[0,0.25,0.5,0.75,1] and h=[0.04,0.02,0.01], records max residual
  6.22e-12, rank 132, raw/scaled max conditions 1.28e10/7.86e4, and
  beta0/beta1 terminal velocity residuals 2.34e-10/1.29e-12. It remains a
  continuation diagnostic because beta=1 is still terminal-row replacement, not
  an independently derived full-TFE stage functional.
  The paper lower-pair terminal source-target audit records 6 case/h rows,
  maps the 8 replaced terminal rows to 24 candidate stage-local lower-pair
  source rows over the three paper stages, and keeps
  `terminal_row_replacement_present=true` and
  `full_tfe_stage_replacement=false`.
  The paper lower-pair terminal source-lift audit records 6 case/h rows, lifts
  the terminal source into 24 stage-local lower-pair rows by
  `sqrt(h*b_i)*terminal_lower_pair_source`, has max lift reconstruction error
  0.0 and max lift-ratio deviation 2.22e-16, and still keeps
  `full_tfe_stage_replacement=false`.
  The paper lower-pair terminal source-normalization audit records 6 case/h
  rows, shows the raw budget source has max terminal reconstruction relative
  error 9.47e-1, and verifies the normalized formula
  `terminal_lower_pair_source = terminal_row_vector/sqrt(h*b_terminal)` with
  zero normalized reconstruction error. It fixes the source scale needed for
  the next Newton-residual substitution while keeping its own
  `substituted_into_newton_residual=false` and `full_tfe_stage_replacement=false`.
  The follow-up terminal source-insertion audit records 12 sign/case/h rows,
  inserts the normalized source into the lower-pair Newton residual, converges
  all 12 one-step attempts, identifies source_sign=-1 as the best sign, and
  records residuals from 4.00e-13 to 9.77e-12. It is still a diagnostic
  insertion attempt with `accepted_h_sweep_present=false` and
  `full_tfe_stage_replacement=false`.
  The terminal source-insertion trajectory audit then uses the best one-step
  sign source_sign=-1 over h=[0.04,0.02,0.01], completes all 6 smooth/sharp
  trajectory rows and all 28 source-ready/source-insertion steps with max
  source-insertion residual 9.75e-12, but the h=0.005 reference run fails and
  the raw terminal endpoint velocity grows to 7.41. It therefore records the
  failure frontier as
  `paper_tfe_lower_pair_terminal_source_insertion_trajectory_failure_quantified_not_accepted`,
  with `accepted_h_sweep_present=false` and `full_tfe_stage_replacement=false`.
  The terminal source-insertion blow-up audit then post-processes those
  trajectory rows over 14 case/metric rows and records 12 blow-up signals.
  The largest mid-to-fine and coarse-to-fine ratios are 7.339e3 and 4.936e5,
  the minimum observed h-power is -9.456, and the dominant signal is
  `cylindrical_smooth:max_normalized_source_norm` with finest value 5.955e2.
  This localizes the failure to a refinement-unstable closure-derived source
  policy while keeping `accepted_h_sweep_present=false` and
  `full_tfe_stage_replacement=false`.
  The bounded-policy audit post-processes the same 14 case/metric rows and
  records a bounded source target rather than an accepted method. It rejects
  the closure-derived source metrics, shows that simple extra h^2 scaling is
  still insufficient for the dominant rows, and sets the next target to an
  independent bounded stage-local lower-pair TFE source formula while keeping
  `accepted_h_sweep_present=false` and `full_tfe_stage_replacement=false`.
  The stage-local bounded-source formula audit separates the one-step formula
  from the recurrent source policy: all 6 case/h rows keep the local
  `source_i = sqrt(h*b_i)*(terminal_lower_pair_row/sqrt(h*b_terminal))`
  formula bounded, with minimum local h-power 0.426, while the recurrent
  closure-derived source remains unbounded with minimum h-power -9.456 and
  max recurrent/local source ratio 1.003e6. It is blocker localization, not an
  accepted full-TFE method.
  The direct endpoint-velocity source audit replaces the rejected
  terminal-closure source generator with the raw endpoint velocity residual of
  the paper acceleration predictor. It records 6 trajectory rows, minimum
  position/velocity orders 2.555/1.918, minimum direct-source/terminal-velocity
  h-powers 0.307/0.286, max direct source 8.118e-6, and max post-insertion
  terminal velocity 7.969e-6, while keeping terminal closure source use,
  accepted h-sweep, and full TFE replacement false.
  The direct-source residual-substitution audit evaluates the raw paper
  lower-pair acceleration residual at the source-inserted solution and checks
  `raw_lower_pair + sqrt(h*b_i)*C_v = 0` over 6 trajectory rows. It records
  maximum balance and inserted lower-pair residuals 1.821e-13, the same
  position/velocity orders 2.555/1.918, and all 28 source-substitution steps
  clean, while keeping the endpoint-boundary-derived source and
  `full_tfe_stage_replacement=false`.
  The residual-derived stage-source audit reconstructs
  `C_hat_i=-R_i/(source_sign*sqrt(h*b_i))` from the raw lower-pair stage rows,
  matches the direct endpoint source with max gap 1.289e-12, and records max
  stage-consistency gap 1.406e-14 with zero derived balance error, but the
  trajectory still uses endpoint-boundary source data.
  The self-consistent endpoint-source audit computes `C_v(x_terminal)` inside
  the Newton lower-pair residual instead of passing an external source. It
  records 6 trajectory rows, max residual/balance/source
  9.441e-12/1.821e-13/7.974e-06, smooth/sharp orders 5.333/6.790 and
  2.555/1.918, and keeps `endpoint_boundary_source_removed=false` and
  `full_tfe_stage_replacement=false`.
  The paper lower-pair source-free elimination rank audit records 6 trajectory
  rows, verifies stage-consistent `C_hat_i` with max consistency gap
  1.406e-14, and shows the source-free centering/elimination map has rank 16
  for 24 lower-pair stage rows. The remaining rank defect is 8, exactly the
  missing mean-source closure budget, so full TFE still needs 8 independent
  lower-pair mean-source rows from the paper stage functional.
  The source-free mean-velocity closure audit fills that 8-row budget with
  paper-stage velocity mean rows and removes endpoint source data,
  terminal-row replacement, and projection, but remains order/closure limited.
  The source-free mean-blend closure audit sweeps 7 alpha values across 42
  one-step rows, keeps endpoint source data, terminal-row replacement, and
  projection removed, and finds best alpha 0 with max residual/raw terminal
  velocity 5.489e-12/2.337e-10; it remains local evidence because terminal
  velocity is still above 1e-10 and no trajectory h-sweep is accepted.
  The source-free mean-blend trajectory audit promotes that alpha to 6
  smooth/sharp h-sweep rows; it is clean and has orders 5.317/6.782 and
  2.555/1.918, but raw terminal velocity grows to 8.234e-06, so the terminal
  closure gate remains open.
  The source-free mean-blend trajectory alpha sweep tests all 7 alpha values
  over 42 trajectory rows. The best terminal-velocity alpha is 0.75, with max
  residual/raw terminal velocity 8.779e-12/7.447e-06 and minimum
  position/velocity orders 2.555/1.918, so simple alpha tuning does not close
  the terminal-velocity gate and full=false remains explicit.
  The source-free component-blend trajectory audit removes the scalar-alpha
  restriction with an 8-component vector from a one-step h=0.02 screen; it
  records 6 trajectory rows with max residual/raw terminal velocity
  9.971e-12/7.458e-06, min orders 2.555/1.918, and a 1.001 terminal-velocity
  ratio versus the scalar alpha baseline. It therefore rules out per-component
  alpha tuning as the terminal-closure repair.
  The centered terminal-velocity bridge audit tests 16 centered acceleration
  source-consistency rows plus 8 terminal-velocity bridge rows over
  gamma=[0,0.5,1]. Gamma 0 closes terminal velocity to 4.01e-16 with max
  residual 9.75e-12, but it uses a terminal-boundary row, keeps
  endpoint-boundary source removal false, and loses the smooth-order gate with
  smooth orders 3.523/4.828.
  The source-free final-stage velocity closure audit inserts the
  velocity-compression result as nonlinear lower-pair rows: 16 centered
  acceleration source-consistency rows plus 8 final paper-stage velocity rows.
  It records 6 smooth/sharp trajectory rows with max residual 9.49e-12 and
  raw terminal endpoint velocity 4.01e-16 without endpoint source,
  terminal-row replacement, or projection. The smooth/sharp position-velocity
  orders are 3.523/4.828 and 2.555/1.918, so terminal closure is solved but
  smooth position order still blocks full TFE acceptance.
  The source-free order/closure blend trajectory audit then sweeps beta=[0,0.5,1]
  between the order-preserving mean-acceleration closure and the terminal-closing
  final-stage velocity closure. It records 18 smooth/sharp trajectory rows,
  keeps endpoint source/projection/terminal-row replacement removed, and confirms
  the split: beta=1 closes terminal velocity to 4.01e-16, beta=0/0.5 keep the
  smooth position order above 5, and no beta gives both the terminal and order
  gates (`order_and_terminal_intersection_present=false`).
  The near-final beta-boundary audit
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_source_free_near_final_beta_boundary_audit.{csv,json}`
  repeats the same source-free formula on the smooth short prefilter with
  beta=[0.9,0.99,0.999,0.9999,0.99999,0.999999,0.99999999,1.0]. It records
  `smooth_order_ok_count=2` at beta=0.9/0.99, but those rows leave terminal
  velocity open. The best nonfinal terminal row beta=0.99999999 reaches only
  `1.255e-12` terminal velocity and has min order 4.508, while beta=1 closes
  terminal velocity at roundoff with the same order-limited branch. Thus
  `order_terminal_intersection_present=false` and
  `near_final_collapse_confirmed=true`; scalar beta tuning is not the remaining
  repair.
  The recurrent feedback gain-boundary audit
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_feedback_gain_boundary_audit.{csv,json}`
  tests the target-free norm-feedback law
  `recurrent_history_velocity_terminal_feedbacknorm_source01historyslope_rel_p*_z`
  over gains [1,2,5,8,10,12,15,20]. Gain 1 is the only high-order branch
  (min order 5.215) but leaves terminal velocity `1.868e-07`; gains 8 and
  above close terminal velocity, with best terminal gain 12 at `1.036e-16`,
  but all terminal-closed gains have min order about 4.508. Therefore
  `order_terminal_intersection_present=false` and
  `terminal_closure_requires_order_collapse=true`; nonlinear target-free
  feedback gain tuning also falls into the terminal/order split.
  The componentwise recurrent feedback gain-boundary audit
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_component_feedback_gain_boundary_audit.{csv,json}`
  repeats the short prefilter for
  `recurrent_history_velocity_terminal_feedbackcomp_source01historyslope_rel_p*_z`
  over the same gains. Gain 1 is again the only high-order branch
  (min order 5.214) and leaves terminal velocity `1.857e-07`; gains 8 and
  above close terminal velocity, with best terminal gain 12 at `7.538e-17`,
  but all terminal-closed gains have min order about 4.508. Thus
  `order_terminal_intersection_present=false` and
  `terminal_closure_requires_order_collapse=true`; the split is not a
  norm-feedback-only artifact.
  The h-scaled recurrent feedback gain-boundary audit
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_hscaled_feedback_gain_boundary_audit.{csv,json}`
  tests effective gain `gain*(h/0.02)^power` over gains [2,5,8,12,20] and
  h-powers [-2,-1,1,2]. Seven rows close terminal velocity, with best terminal
  gain/power 12/1 at `1.036e-16`, but that branch has min order 4.508. No row
  reaches the smooth-order floor; the best-order row is gain/power 2/2 with
  min order 4.711 and terminal velocity `1.316e-08`. Thus
  `order_terminal_intersection_present=false`; h-dependent scalar feedback
  scaling is also not the missing closure formula.
  The recurrent source-law trajectory screen
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_source_law_trajectory_screen_audit.{csv,json}`
  removes feedback and tests six target-free one-history/two-history source
  and curvature rows. It records `terminal_closed_row_count=0`,
  `smooth_order_ok_count=5`, best terminal velocity `2.016e-07`, best smooth
  min order 5.355, and no order/terminal intersection; the tested
  source-history laws preserve order but leave terminal velocity open.
  The three-history recurrent source-law trajectory screen
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_three_history_source_law_trajectory_screen_audit.{csv,json}`
  extends the same target-free prefilter to four three-block shift-register
  laws. It records `terminal_closed_row_count=0`, `smooth_order_ok_count=2`,
  best law `recurrent_threehistory_velocity_terminal_source01historyslopejerk_z`,
  best terminal velocity `2.923e-07`, best smooth min order `5.345`, and
  `full_tfe_stage_replacement=false`; the jerk laws preserve smooth order but
  still leave terminal velocity open.
  The four-history recurrent source-law trajectory screen
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_four_history_source_law_trajectory_screen_audit.{csv,json}`
  extends the same target-free prefilter to AB5 and fourth-difference snap
  laws with a four-block shift register. It records
  `terminal_closed_row_count=0`, `smooth_order_ok_count=2`, best law
  `recurrent_fourhistory_velocity_terminal_source01historyslopejerksnap_z`,
  best terminal velocity `2.950e-07`, best smooth min order `5.342`, and
  `full_tfe_stage_replacement=false`; adding one more history block does not
  close the terminal-velocity gate.
  The nonlinear-history recurrent source-law trajectory screen
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_nonlinear_history_source_law_trajectory_screen_audit.{csv,json}`
  tests five target-free norm, Hadamard, bilinear, and second-difference
  history laws with a two-block shift register. It records
  `terminal_closed_row_count=0`, `smooth_order_ok_count=0`, best law
  `recurrent_nonlinearhistory_velocity_terminal_source0historyhadamard_z`,
  best terminal velocity `1.954e-07`, best smooth min order `3.525`, and
  `full_tfe_stage_replacement=false`; the nonlinear history family neither
  closes terminal velocity nor preserves the smooth-order floor.
  The source-law final-retain boundary audit
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_source_law_final_retain_boundary_audit.{csv,json}`
  then blends the source-history terminal row toward final-stage velocity
  rows over 16 target-free retain/h-power combinations. It records
  `terminal_closed_row_count=4`, `smooth_order_ok_count=0`, best terminal
  velocity `3.171e-13`, best terminal min order 4.508, best smooth min order
  4.510, and no order/terminal intersection. Thus the near final-stage
  boundary also closes terminal velocity only after order collapse.
  The recurrent stage-2 translation-velocity matrix differential audit
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_translation_velocity_matrix_differential_audit.{csv,json}`
  tests 40 local target-free rows over ten translation-velocity matrix laws.
  It records `span_row_count=0`, best law
  `stage2_translation_velocity_symmetric_broadcast_feature`, best projection
  residual `0.671049`, independent target rank 8, and dominant missing family
  `angular_velocity_w`; translation-only matrix features improve the local
  residual but still do not close the coupled stage-2 terminal bridge.
  The recurrent stage-2 translation/angular coupled matrix differential audit
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_translation_angular_coupled_matrix_differential_audit.{csv,json}`
  tests 48 local target-free paired rowmask, pair-swap, and lower-pair
  local-block rows over twelve matrix laws. It records `span_row_count=0`,
  best law `stage2_velocity_bidirectional_rowmask_translation_angular_feature`,
  best projection residual `0.742069`, independent target rank 8, dominant
  missing family `translation_velocity_v`, and stage-2 missing-direction
  fraction `0.942285`; these paired translation/angular local laws are worse
  than the translation-only and active-law probes and remain negative evidence.
  The closure acceptance matrix compares the 14 lower-pair closure families,
  records 0 accepted candidates, identifies `source_free_mean_blend_trajectory_best_alpha`
  as the best order-preserving source-free candidate and
  the centered/final-stage velocity-closure rows as the terminal-velocity
  candidates, and keeps full TFE stage replacement missing because the
  source-free terminal-closed candidate is smooth-order limited.
  The closure property Pareto audit groups those same candidates into 5
  property-intersection rows: 9 are source-free/no-replacement candidates, 5
  are order-preserving source-free candidates, and 3 are terminal-velocity
  closed. The accepted intersection is empty, so this is blocker localization,
  not a full-TFE acceptance claim.
  The closure row-span audit tests the already-tried source-free basis
  (16 centered source-consistency rows plus mean-acceleration, mean-velocity,
  and terminal-extrapolated stage-velocity closure rows) against the terminal
  bridge row in the local Jacobian row space. Across 6 case/h rows, the basis
  rank is 40, the augmented rank is 48, the max independent target rank is 8,
  and the max projection relative residual is 2.814e-01. The new
  missing-direction decomposition has rank 8, is orthogonal to the tested basis
  to 8.75e-16 relative, and reconstructs the terminal-bridge target with max
  reprojection residual 9.25e-14. The missing-direction column energy is
  velocity-level: angular velocity is the dominant variable family in all 6
  rows with max fraction 0.506, translation velocity reaches 0.496, lower-pair
  lambda is 0, and translation acceleration is below 5.60e-05. This rules out
  recovering the terminal-velocity bridge by reweighting the existing
  source-free basis; the next repair needs a stage-local source-free
  velocity-level formula for those eight lower-pair tangent directions.
  The velocity-basis span audit tests that target against 7 weighted eight-row
  stage-velocity closure families plus the 24-row all-stage velocity upper
  bound over the same 6 case/h samples. The all-stage velocity rows span the
  terminal-bridge tangent with max relative residual 2.78e-15, while the best
  weighted eight-row candidate is `endpoint_lagrange_velocity_closure` with
  relative residual 4.20e-01 and no weighted candidate spans the target. This
  narrows the next repair to an eight-row source-free compression of the
  all-stage lower-pair velocity row space, followed by a nonlinear trajectory
  h-sweep before any full-TFE claim.
  The velocity-compression audit fits that source-free eight-row compression
  directly in the local tangent row space. Across the same 6 case/h samples,
  all 3 fixed candidates span the terminal-bridge tangent at roundoff; the
  best fixed candidate is `optimized_global_stage_scalar`, whose weights are
  numerically `[0,0,1]`, i.e. selecting the final paper-stage lower-pair
  velocity rows. The best fixed relative residual is 1.04e-15, the universal
  full 8x24 compression spans all 6 samples, and the case-local oracle also
  spans all 6. The strengthened audit now records that every fixed compression
  degenerates to the final-stage selector: the universal full 8x24 selector
  distance is 1.53e-15 and the largest non-final-stage energy fraction is
  1.71e-15. The non-degenerate follow-up then injects fixed stage-0/stage-1
  velocity-row energy over 192 candidate/case/h/eta rows; 84 rows have
  meaningful non-final-stage energy, but none spans the local terminal-bridge
  target and the best meaningful relative residual is 1.59e-03. This means the
  local fixed compression is not a new independent closure formula. The
  state-local diagonal direction oracle then sweeps 72 rows over 65 direction
  samples; 36 rows have meaningful non-final-stage energy, but none spans
  locally and the best meaningful relative residual is 9.90e-03. This rules
  out diagonal state-dependent direction weights. The non-final full
  component-mixing probe then tests 36 case/h/candidate rows using stage-0,
  stage-1, and stage-0+1 full 8x8/8x16 fits; none spans locally, the best
  tangent residual is 9.81e-01. The value-level source-free probe then tests
  72 case/h/candidate rows; all 72 balance row values, 18 span the local
  tangent, but 0 meaningful non-final value-balanced rows span, because the
  successful spans are final-stage-selector-like with max non-final energy
  2.12e-15. The next repair is therefore a meaningful non-final
  derivative-aware value-level source-free compression before the nonlinear
  h-sweep can plausibly satisfy both terminal closure and smooth order.
  The derivative-aware local oracle then tests 36 non-final case/h/candidate
  rows. All 36 rows balance values and span the local tangent with meaningful
  non-final energy after a coefficient-gradient correction, but this is an
  oracle/upper-bound result rather than a bounded analytic row formula. The
  bounded-gradient cap sweep then tests 288 cap/candidate/case/h rows: all 288
  rows keep value balance and meaningful non-final energy, but only 92 rows
  span at the tested caps; a practical cap 1e12 spans 12 rows, while all 36
  derivative-aware local spans require cap 1e18. The bounded-formula
  saturation-law audit then tests 648 law/cap/candidate/case/h rows over
  global tanh, rowwise tanh, and rowwise rational-quadratic saturations: all
  648 rows keep value balance and meaningful non-final energy, 366 span at the
  tested caps, and all local spans require cap 1e22 for every tested law. The
  correction direction is still a target-direction oracle, so the next audit
  removes that oracle from the formula path.
  The target-direction-free bounded formula probe then tests 2592
  law/cap/candidate/case/h rows over 12 source-derived, stage-extrapolated,
  and all-active component direction laws. All 2592 rows keep value balance
  and meaningful non-final energy, but 0 span at any tested cap; the best
  projection residual is 9.82e-01, and the formula construction does not use
  the target Jacobian or target direction.
  The bounded tangent requirement audit
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_bounded_tangent_requirement_audit.{csv,json}`
  collects the frontier split and row-space/cap evidence into
  `requirement_row_count=7` constraints: the oracle coefficient-derivative row
  spans all 36 local rows, but target-free formulas span 0 rows, frozen
  row-space compression spans 0 rows, weak-row structures span 0 rows, and the
  practical bounded-gradient cap spans only 12 rows. The remaining target is a
  bounded target-free stage-local weak-row tangent with no target
  Jacobian/direction oracle and a separate accepted h-sweep.
  The recurrent stage2 feature-dictionary span audit
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_feature_dictionary_span_audit.{csv,json}`
  records `feature_dictionary_row_count=12`, `span_row_count=8`,
  `combined_all_dictionary_span_count=2`, and best dictionary
  `stage2_matrix_core` with residual `1.084e-14`. It uses no target Jacobian
  or target-direction oracle for formula construction, records
  `formula_coefficient_law_present=false`, and leaves the next repair target
  as a bounded target-free coefficient/selection law plus nonlinear h-sweep.
  The recurrent stage2 frozen coefficient-law screen
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_feature_coefficient_law_screen_audit.{csv,json}`
  records `coefficient_law_row_count=60`, `span_count=0`, and best dictionary
  `combined_all_target_free_dictionary` with law `closure_delta_norm_weights`
  at residual `5.596e-01`. The laws are target-free and bounded, but
  `coefficient_derivative_included=false`, `target_jacobian_used_for_formula=false`,
  and `target_direction_oracle_used=false`, so the remaining target is
  state-dependent bounded coefficients with derivative terms plus an accepted
  nonlinear h-sweep.
  The recurrent stage2 state-feature coefficient-derivative screen
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_state_feature_coefficient_derivative_screen_audit.{csv,json}`
  then differentiates three target-free coefficient laws over the same six
  dictionaries. It records `state_feature_coefficient_derivative_row_count=36`,
  `span_count=0`, and best dictionary `stage2_matrix_core` with law
  `inverse_closure_delta_norm_weights_derivative` at residual `5.908e-01`.
  It includes coefficient derivatives and uses candidate/recurrent Jacobians,
  but `target_jacobian_used_for_formula=false` and
  `target_direction_oracle_used=false`; direct differentiation of the tested
  closure-norm weights is therefore excluded, and the next target is richer
  state-dependent coefficient features or a new weak-row formula.
  The direction-capacity audit tests 216 candidate/feature/case/h rows:
  all-stage velocity features span 72 rows at roundoff, but every non-final
  active/source feature family has 0 spans, with best non-final projection
  residual 9.81e-01 and best non-final correction residual 9.998e-01.
  The nonlinear second-differential capacity audit then tests 216 rows across
  six finite-difference source-feature families. It records 0 spans, best
  projection residual 6.95e-01, and best correction residual 7.01e-01. The
  target Jacobian is used only to define/project the tested correction, not to
  build a target-direction oracle formula. The tested second-differential
  non-final source features are therefore ruled out; the remaining full-TFE
  repair is a higher-order or nonlocal non-final source feature followed by a
  nonlinear h-sweep.
  The endpoint-pose velocity predictor reference/output audit then records 10
  short diagnostic rows over output-pose choices, three-h order checks, and a
  finer `reference_h=0.0025` check. Five rows close terminal velocity, but
  `smooth_order_ok_count=0`; the best terminal-closed short prefilter law is
  `stage02_convex_pose_velocity_0p00_z` with `6.588/4.508` two-point orders,
  while the three-h short check remains `4.142/2.305` and the finer reference
  check drops to `3.672/1.956`. This rules out output-node relabeling and
  reference-floor policy as the repair for the full-TFE gap.
  The h-adaptive endpoint-pose velocity predictor audit
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_endpoint_pose_velocity_hscaled_predictor_h_sweep_audit.{csv,json}`
  then runs 12 smooth rows over four h-scaled endpoint-pose velocity laws with
  no projection and no terminal-row replacement. The best terminal-closing law
  is `stage02_convex_pose_velocity_extrapolate_0p00001_0p00002_hpow_m1_z`,
  which reaches terminal velocity `5.004e-13` but only `3.523/4.828`
  position/velocity order. Stronger negative powers reopen terminal velocity,
  so the aggregate audit keeps `terminal_velocity_closed=false`,
  `smooth_order_ok=false`, and `full_tfe_stage_replacement=false`.
  The h-adaptive endpoint-pose velocity response audit then reduces those four
  laws to one row each and records `terminal_closed_row_count=1`,
  `smooth_order_ok_count=0`, `accepted_candidate_count=0`, and
  `order_terminal_intersection_present=false`; terminal closure still requires
  order collapse, so `full_tfe_stage_replacement=false`.
  The row-space compression audit then tests 36 case/h/law rows over
  target-free SVD, row-norm, and stage-balanced frozen eight-row compressions
  of the all-stage/non-final velocity row space. It records 0 spans, 24
  value-balanced rows, best projection residual 7.38e-01, best value residual
  3.68e-12, and best non-final residual 9.82e-01. The formula construction
  uses neither the target Jacobian nor a target-direction oracle, but the
  coefficients are frozen state-dependent quantities and coefficient
  derivatives are not included, so this is local negative evidence rather than
  a nonlinear full-TFE replacement.
  A row-space coefficient-derivative follow-up adds
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_velocity_compression_row_space_coefficient_derivative_audit.{csv,json}`:
  it keeps the same six target-free row-space compression laws, adds the local
  target-perp-minus-closure-perp coefficient-derivative oracle, and records 36
  tangent spans with 24 value-balanced spans. The best derivative-inclusive
  residual is `8.92e-16`, but the construction uses a target-direction oracle
  and requires coefficient-gradient norms up to `6.78e18`, so the full-TFE
  gate still needs a bounded target-free coefficient-gradient formula and a
  nonlinear h-sweep.
  The paper
  residual-substitution contract audit maps six row-family targets with 6
  formulas, 6 substituted rows, 0 accepted h-sweep rows, and
  `full_tfe_stage_replacement=false`;
- plots: runtime, sparse-pattern, sparse-runtime-repeat, sparse-speed-gap,
  sparse-cost-model, convergence,
  friction-smoothness, sharp-adaptive, sharp-adaptive-tolerance, sharp-fixed-refinement,
  sharp-deep-refinement, sharp-ultra-refinement, sharp-refinement-cost-envelope,
  endpoint-projection audit,
  endpoint-KKT closure, endpoint-TFE-gap, endpoint-TFE-candidate,
  endpoint-TFE-solved-candidate, endpoint-TFE-stage-weighted-candidate,
  endpoint-TFE-stage-functional-spec, endpoint-TFE-stage-functional-implementation,
  endpoint-TFE-stage-non-equivalent-probe, endpoint-TFE-stage-probe-boundary-source,
  endpoint-TFE-stage-probe-source-budget,
  endpoint-TFE-stage-probe-dominant-source-split,
  endpoint-TFE-stage-probe-order,
  endpoint-TFE-stage-non-equivalent-solved-probe,
  endpoint-TFE-stage-probe-homotopy, endpoint-TFE-stage-probe-block-activation,
  endpoint-TFE-stage-probe-component-activation,
  endpoint-TFE-stage-probe-component-formula,
  endpoint-TFE-full-stage-acceptance-gap,
  endpoint-TFE-stage-local-source-removal-target,
  endpoint-TFE-stage-probe-coupled-budget,
  endpoint-TFE-stage-probe-trajectory-accumulation,
  endpoint-TFE-stage-probe-beta-trajectory-bridge,
  endpoint-TFE-stage-replacement-design,
  endpoint-TFE-paper-formula-mapping,
  endpoint-TFE-paper-derivative-operator,
  endpoint-TFE-paper-stage-input-map,
  endpoint-TFE-paper-multiplier-policy,
  endpoint-TFE-paper-kinematic-formula,
  endpoint-TFE-paper-balance-constraint-formula,
  endpoint-TFE-paper-position-substitution-candidate,
  endpoint-TFE-paper-kinematic-substitution-candidate,
  endpoint-TFE-paper-all-row-substitution-candidate,
  endpoint-TFE-paper-all-row-gauss-z0-substitution-candidate,
  endpoint-TFE-paper-all-row-gauss-z0-terminal-output,
  endpoint-TFE-paper-all-row-recurrent-z0-terminal-output,
  endpoint-TFE-paper-all-row-consistent-z0-terminal-output,
  endpoint-TFE-paper-all-row-consistent-z0-conditioning,
  endpoint-TFE-paper-all-row-consistent-z0-scaled-Newton,
  endpoint-TFE-paper-family-ablation,
  endpoint-TFE-paper-lower-pair-lambda-Schur,
  endpoint-TFE-paper-lower-pair-acceleration-terminal-output,
  endpoint-TFE-paper-lower-pair-acceleration-projection-dependence,
  endpoint-TFE-paper-lower-pair-acceleration-terminal-velocity-closure,
  endpoint-TFE-paper-lower-pair-acceleration-terminal-row-homotopy,
  endpoint-TFE-paper-lower-pair-terminal-source-target,
  endpoint-TFE-paper-lower-pair-terminal-source-lift,
  endpoint-TFE-paper-lower-pair-terminal-source-normalization,
  endpoint-TFE-paper-lower-pair-terminal-source-insertion,
  endpoint-TFE-paper-lower-pair-terminal-source-insertion-trajectory,
  endpoint-TFE-paper-lower-pair-terminal-source-insertion-blowup,
  endpoint-TFE-paper-lower-pair-terminal-source-bounded-policy,
  endpoint-TFE-paper-lower-pair-stage-local-bounded-source-formula,
  endpoint-TFE-paper-lower-pair-direct-endpoint-velocity-source,
  endpoint-TFE-paper-lower-pair-direct-source-residual-substitution,
  endpoint-TFE-paper-lower-pair-residual-derived-stage-source,
  endpoint-TFE-paper-lower-pair-self-consistent-endpoint-source,
  endpoint-TFE-paper-lower-pair-source-free-elimination-rank,
  endpoint-TFE-paper-lower-pair-source-free-mean-velocity-closure,
  endpoint-TFE-paper-lower-pair-source-free-final-stage-velocity-closure,
  endpoint-TFE-paper-lower-pair-source-free-order-closure-blend-trajectory,
  endpoint-TFE-paper-lower-pair-source-free-mean-blend-closure,
  endpoint-TFE-paper-lower-pair-source-free-mean-blend-trajectory,
  endpoint-TFE-paper-lower-pair-source-free-mean-blend-trajectory-alpha-sweep,
  endpoint-TFE-paper-lower-pair-source-free-component-blend-trajectory,
  endpoint-TFE-paper-lower-pair-source-free-terminal-velocity-extrapolation-trajectory,
  endpoint-TFE-paper-lower-pair-source-free-terminal-extrapolation-blend-trajectory,
  endpoint-TFE-paper-lower-pair-closure-acceptance-matrix,
  endpoint-TFE-paper-lower-pair-closure-property-Pareto,
  endpoint-TFE-paper-lower-pair-closure-row-span,
  endpoint-TFE-paper-lower-pair-velocity-basis-span,
  endpoint-TFE-paper-lower-pair-velocity-compression,
  endpoint-TFE-paper-lower-pair-velocity-compression-nondegenerate,
  endpoint-TFE-paper-lower-pair-velocity-compression-state-dependent,
  endpoint-TFE-paper-lower-pair-velocity-compression-component-mixing,
  endpoint-TFE-paper-lower-pair-velocity-compression-value-level,
  endpoint-TFE-paper-lower-pair-velocity-compression-derivative-aware,
  endpoint-TFE-paper-lower-pair-velocity-compression-bounded-gradient,
  endpoint-TFE-paper-lower-pair-velocity-compression-bounded-formula,
  endpoint-TFE-paper-lower-pair-velocity-compression-target-free-formula,
  endpoint-TFE-paper-lower-pair-velocity-compression-direction-capacity,
  endpoint-TFE-paper-lower-pair-velocity-compression-nonlinear-capacity,
  endpoint-TFE-paper-lower-pair-velocity-compression-higher-order-capacity,
  endpoint-TFE-paper-lower-pair-velocity-compression-history-capacity,
  endpoint-TFE-paper-lower-pair-velocity-compression-multi-step-history-capacity,
  endpoint-TFE-paper-lower-pair-velocity-compression-recurrent-history-capacity,
  endpoint-TFE-paper-lower-pair-velocity-compression-weak-row-structure-capacity,
  endpoint-TFE-paper-lower-pair-velocity-compression-row-space-compression,
  endpoint-TFE-paper-residual-substitution-contract,
  endpoint-TFE-readiness, ASME gate, single/double diagnostics,
  lower-pair graph-bridge, lower-pair rank-audit, and closed-loop kinematic
  FullVA/reaction-dynamics plots are present.
- output validation: `validate_v047_outputs.py` passes the read-only checks over
  the 292 generated result files, 147 CSVs, 120 PNGs,
  summary gate status, stale wording, and README/report artifact lists.
