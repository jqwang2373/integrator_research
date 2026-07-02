# External Baseline Source-Policy Diagnosis

Status: **diagnosis only; source-policy recheck still required**.

- Flagged baseline rows diagnosed: `15`.
- Flagged examples: `double_pendulum, four_link, single_pendulum, slider_crank`.
- Position-aligned but velocity-mismatched rows: `10`.
- Common-reference arithmetic mismatches: `0`.
- Same-test campaign status: `not_run`.
- Accepted external dynamic-order examples: `0`.
- External superiority allowed: `False`.

## Diagnostic Category Counts

| category | rows |
|---|---:|
| `low_order_but_small_error_needs_wider_step_window` | `4` |
| `near_reference_floor_order_not_identifiable` | `3` |
| `negative_order_large_error_fixed_grid_or_form_mismatch` | `1` |
| `position_aligned_velocity_mismatch` | `10` |
| `single_pendulum_velocity_output_policy_suspect` | `7` |

## Flagged Row Diagnosis

| method | example | order | finest pos error | finest vel error | categories | closure action |
|---|---|---:|---:|---:|---|---|
| `hi2022_rA` | `four_link` | `1.015` | `8.773e-09` | `0.197` | `position_aligned_velocity_mismatch` | `choose_full_T8_public_policy_or_explicitly_demote_hi2022_four_link_before_external_superiority` |
| `hi2022_rA_half` | `double_pendulum` | `-0.799` | `0.164` | `2.970` | `negative_order_large_error_fixed_grid_or_form_mismatch` | `choose_full_T8_public_policy_or_explicitly_demote_hi2022_double_pendulum_before_external_superiority` |
| `hi2022_rA_half` | `four_link` | `1.590` | `8.773e-09` | `0.197` | `position_aligned_velocity_mismatch` | `choose_full_T8_public_policy_or_explicitly_demote_hi2022_four_link_before_external_superiority` |
| `ra2021_rA` | `single_pendulum` | `0.617` | `1.045e-10` | `13.049` | `position_aligned_velocity_mismatch, single_pendulum_velocity_output_policy_suspect` | `rerun_or_verify_ra2021_single_pendulum_under_declared_same_test_policy_with_state_velocity_mapping_time_grid_norm_and_runtime` |
| `ra2021_rA` | `four_link` | `1.015` | `1.086e-08` | `0.197` | `position_aligned_velocity_mismatch` | `rerun_or_verify_ra2021_four_link_under_declared_same_test_policy_with_state_velocity_mapping_time_grid_norm_and_runtime` |
| `ra2021_reps` | `single_pendulum` | `0.617` | `6.610e-14` | `13.049` | `position_aligned_velocity_mismatch, single_pendulum_velocity_output_policy_suspect` | `rerun_or_verify_ra2021_single_pendulum_under_declared_same_test_policy_with_state_velocity_mapping_time_grid_norm_and_runtime` |
| `ra2021_rp` | `single_pendulum` | `0.517` | `1.114e-14` | `14.990` | `position_aligned_velocity_mismatch, single_pendulum_velocity_output_policy_suspect` | `rerun_or_verify_ra2021_single_pendulum_under_declared_same_test_policy_with_state_velocity_mapping_time_grid_norm_and_runtime` |
| `ra2021_rp` | `double_pendulum` | `0.361` | `5.449e-03` | `5.241e-05` | `low_order_but_small_error_needs_wider_step_window` | `rerun_or_verify_ra2021_double_pendulum_under_declared_same_test_policy_with_state_velocity_mapping_time_grid_norm_and_runtime` |
| `tfe2026_Newmark_beta` | `single_pendulum` | `0.901` | `1.046e-10` | `14.791` | `position_aligned_velocity_mismatch, single_pendulum_velocity_output_policy_suspect` | `encode_original_tfe_pendulum_setup_error_norm_friction_law_output_policy_then_rerun_or_demote` |
| `tfe2026_TFE_m1` | `single_pendulum` | `1.021` | `1.046e-10` | `14.982` | `position_aligned_velocity_mismatch, single_pendulum_velocity_output_policy_suspect` | `encode_original_tfe_pendulum_setup_error_norm_friction_law_output_policy_then_rerun_or_demote` |
| `tfe2026_TFE_m2` | `single_pendulum` | `0.054` | `1.046e-10` | `110.220` | `position_aligned_velocity_mismatch, single_pendulum_velocity_output_policy_suspect` | `encode_original_tfe_pendulum_setup_error_norm_friction_law_output_policy_then_rerun_or_demote` |
| `tfe2026_trapezoidal` | `single_pendulum` | `1.024` | `1.046e-10` | `14.983` | `position_aligned_velocity_mismatch, single_pendulum_velocity_output_policy_suspect` | `encode_original_tfe_pendulum_setup_error_norm_friction_law_output_policy_then_rerun_or_demote` |
| `vp2024_coordinate_partitioning_rA` | `single_pendulum` | `6.149e-15` | `1.046e-10` | `3.163e-11` | `near_reference_floor_order_not_identifiable, low_order_but_small_error_needs_wider_step_window` | `resolve_velocity_partitioning_code_path_or_demote_vp2024_suite` |
| `vp2024_coordinate_partitioning_rA` | `four_link` | `-5.332e-04` | `8.773e-09` | `1.087e-08` | `near_reference_floor_order_not_identifiable, low_order_but_small_error_needs_wider_step_window` | `resolve_velocity_partitioning_code_path_or_demote_vp2024_suite` |
| `vp2024_coordinate_partitioning_rA` | `slider_crank` | `-3.253e-07` | `3.024e-07` | `1.332e-07` | `near_reference_floor_order_not_identifiable, low_order_but_small_error_needs_wider_step_window` | `resolve_velocity_partitioning_code_path_or_demote_vp2024_suite` |

## Boundary

- This audit diagnoses comparison-policy risks; it does not decide that an external method is intrinsically bad.
- The zero-mismatch recomputation audit means the current table arithmetic is consistent with the raw rows.
- B2/B4 remain open until source-policy same-test runs are completed or suites are explicitly demoted in the manuscript.
