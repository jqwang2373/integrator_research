# B4 Source-Policy Row Closure Readiness Ledger

Status: `all_40_external_rows_mapped_20_attempted_not_reproducible_0_source_policy_rows_closed`.

This is a read-only ledger over the 40 external method/example cells. It does not run numerical experiments.

- External rows mapped: `40/40`.
- Source-policy rows closed/unclosed: `0/40`.
- Source-policy rows still requiring execution/promotion: `20`.
- Source-policy rows attempted-not-reproducible: `20`.
- Source-policy rows unable-to-reproduce/not-promoted: `20`.
- Rows with launch command refs: `20`.
- Rows without launch command refs: `20`.
- Rows without launch command refs attempted-not-reproducible: `20`.
- Rows demoted related-work/proxy for current claim: `20`.
- RA2021 ready-command output rows not promoted: `12`.
- RA2021 output row scope: `verified_authorized_driver_output_presence_not_promoted`.
- HI2022 selected-candidate executed/partial rows not promoted: `7/1`.
- Post-execution decision counts: `{'attempted_not_reproducible': 20, 'not_promoted': 20}`.
- Primary promotion-blocker counts: `{'distinct_public_vp2024_code_path_not_found_proxy_not_source_policy': 4, 'hi2022_ra_half_double_partial_newton_failure_not_promoted': 1, 'hi2022_selected_coarse_trio_not_full_public_grid_not_promoted': 7, 'paper_spec_candidate_runner_not_source_policy_equivalent': 4, 'ra2021_closed_loop_T0p1_mixed_reference_not_source_policy': 6, 'ra2021_double_low_order_floor_limited_constraint_not_promoted': 3, 'ra2021_single_floor_limited_public_h_tranche_not_promoted': 3, 'tfe_source_paper_pendulum_suite_does_not_define_this_mechanism_runner': 12}`.
- Ready/not-ready suites: `2/2`.
- B4/B7 can close now: `False/False`.
- Heavy/run_v047/v048 invoked: `False/False/False`.

## Suite Summary

| suite | rows | closed | attempted not reproducible | unable to reproduce | still requiring execution | command-mapped | launch-ready | B4/B7 close |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `hi2022_half_implicit` | `8` | `0` | `0` | `0` | `8` | `8` | `True` | `False/False` |
| `ra2021_absolute_coordinate` | `12` | `0` | `0` | `0` | `12` | `12` | `True` | `False/False` |
| `tfe2026_original_pendulum` | `16` | `0` | `16` | `16` | `0` | `0` | `False` | `False/False` |
| `vp2024_velocity_partitioning` | `4` | `0` | `4` | `4` | `0` | `0` | `False` | `False/False` |

## Row Readiness

| suite | method | example | status | disposition | decision | primary blocker | evidence | commands |
|---|---|---|---|---|---|---|---|---:|
| `hi2022_half_implicit` | `hi2022_rA` | `single_pendulum` | `selected_candidate_executed_not_promoted` | `promotion_open` | `not_promoted` | `hi2022_selected_coarse_trio_not_full_public_grid_not_promoted` | `HI2022_SOURCE_POLICY_ROW_AUDIT.json` | `1` |
| `hi2022_half_implicit` | `hi2022_rA` | `double_pendulum` | `selected_candidate_executed_not_promoted` | `promotion_open` | `not_promoted` | `hi2022_selected_coarse_trio_not_full_public_grid_not_promoted` | `HI2022_SOURCE_POLICY_ROW_AUDIT.json` | `1` |
| `hi2022_half_implicit` | `hi2022_rA` | `four_link` | `selected_candidate_executed_not_promoted` | `promotion_open` | `not_promoted` | `hi2022_selected_coarse_trio_not_full_public_grid_not_promoted` | `HI2022_SOURCE_POLICY_ROW_AUDIT.json` | `1` |
| `hi2022_half_implicit` | `hi2022_rA` | `slider_crank` | `selected_candidate_executed_not_promoted` | `promotion_open` | `not_promoted` | `hi2022_selected_coarse_trio_not_full_public_grid_not_promoted` | `HI2022_SOURCE_POLICY_ROW_AUDIT.json` | `1` |
| `hi2022_half_implicit` | `hi2022_rA_half` | `single_pendulum` | `selected_candidate_executed_not_promoted` | `promotion_open` | `not_promoted` | `hi2022_selected_coarse_trio_not_full_public_grid_not_promoted` | `HI2022_SOURCE_POLICY_ROW_AUDIT.json` | `1` |
| `hi2022_half_implicit` | `hi2022_rA_half` | `double_pendulum` | `selected_candidate_partial_or_failed_not_promoted` | `promotion_open` | `not_promoted` | `hi2022_ra_half_double_partial_newton_failure_not_promoted` | `HI2022_RA_HALF_DOUBLE_SOURCE_POLICY_FAILURE_DIAGNOSIS.json` | `1` |
| `hi2022_half_implicit` | `hi2022_rA_half` | `four_link` | `selected_candidate_executed_not_promoted` | `promotion_open` | `not_promoted` | `hi2022_selected_coarse_trio_not_full_public_grid_not_promoted` | `HI2022_SOURCE_POLICY_ROW_AUDIT.json` | `1` |
| `hi2022_half_implicit` | `hi2022_rA_half` | `slider_crank` | `selected_candidate_executed_not_promoted` | `promotion_open` | `not_promoted` | `hi2022_selected_coarse_trio_not_full_public_grid_not_promoted` | `HI2022_SOURCE_POLICY_ROW_AUDIT.json` | `1` |
| `ra2021_absolute_coordinate` | `ra2021_rA` | `single_pendulum` | `approved_driver_outputs_present_not_promoted` | `promotion_open` | `not_promoted` | `ra2021_single_floor_limited_public_h_tranche_not_promoted` | `RA2021_SOURCE_POLICY_ROW_AUDIT.json` | `2` |
| `ra2021_absolute_coordinate` | `ra2021_rA` | `double_pendulum` | `approved_driver_outputs_present_not_promoted` | `promotion_open` | `not_promoted` | `ra2021_double_low_order_floor_limited_constraint_not_promoted` | `RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.json` | `2` |
| `ra2021_absolute_coordinate` | `ra2021_rA` | `four_link` | `approved_driver_outputs_present_not_promoted` | `promotion_open` | `not_promoted` | `ra2021_closed_loop_T0p1_mixed_reference_not_source_policy` | `RA2021_SOURCE_POLICY_ROW_AUDIT.json` | `2` |
| `ra2021_absolute_coordinate` | `ra2021_rA` | `slider_crank` | `approved_driver_outputs_present_not_promoted` | `promotion_open` | `not_promoted` | `ra2021_closed_loop_T0p1_mixed_reference_not_source_policy` | `RA2021_SOURCE_POLICY_ROW_AUDIT.json` | `2` |
| `ra2021_absolute_coordinate` | `ra2021_reps` | `single_pendulum` | `approved_driver_outputs_present_not_promoted` | `promotion_open` | `not_promoted` | `ra2021_single_floor_limited_public_h_tranche_not_promoted` | `RA2021_SOURCE_POLICY_ROW_AUDIT.json` | `2` |
| `ra2021_absolute_coordinate` | `ra2021_reps` | `double_pendulum` | `approved_driver_outputs_present_not_promoted` | `promotion_open` | `not_promoted` | `ra2021_double_low_order_floor_limited_constraint_not_promoted` | `RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.json` | `2` |
| `ra2021_absolute_coordinate` | `ra2021_reps` | `four_link` | `approved_driver_outputs_present_not_promoted` | `promotion_open` | `not_promoted` | `ra2021_closed_loop_T0p1_mixed_reference_not_source_policy` | `RA2021_SOURCE_POLICY_ROW_AUDIT.json` | `2` |
| `ra2021_absolute_coordinate` | `ra2021_reps` | `slider_crank` | `approved_driver_outputs_present_not_promoted` | `promotion_open` | `not_promoted` | `ra2021_closed_loop_T0p1_mixed_reference_not_source_policy` | `RA2021_SOURCE_POLICY_ROW_AUDIT.json` | `2` |
| `ra2021_absolute_coordinate` | `ra2021_rp` | `single_pendulum` | `approved_driver_outputs_present_not_promoted` | `promotion_open` | `not_promoted` | `ra2021_single_floor_limited_public_h_tranche_not_promoted` | `RA2021_SOURCE_POLICY_ROW_AUDIT.json` | `2` |
| `ra2021_absolute_coordinate` | `ra2021_rp` | `double_pendulum` | `approved_driver_outputs_present_not_promoted` | `promotion_open` | `not_promoted` | `ra2021_double_low_order_floor_limited_constraint_not_promoted` | `RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.json` | `2` |
| `ra2021_absolute_coordinate` | `ra2021_rp` | `four_link` | `approved_driver_outputs_present_not_promoted` | `promotion_open` | `not_promoted` | `ra2021_closed_loop_T0p1_mixed_reference_not_source_policy` | `RA2021_SOURCE_POLICY_ROW_AUDIT.json` | `2` |
| `ra2021_absolute_coordinate` | `ra2021_rp` | `slider_crank` | `approved_driver_outputs_present_not_promoted` | `promotion_open` | `not_promoted` | `ra2021_closed_loop_T0p1_mixed_reference_not_source_policy` | `RA2021_SOURCE_POLICY_ROW_AUDIT.json` | `2` |
| `tfe2026_original_pendulum` | `tfe2026_Newmark_beta` | `single_pendulum` | `attempted_not_reproducible` | `attempted_not_reproducible` | `attempted_not_reproducible` | `paper_spec_candidate_runner_not_source_policy_equivalent` | `SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json` | `0` |
| `tfe2026_original_pendulum` | `tfe2026_Newmark_beta` | `double_pendulum` | `attempted_not_reproducible` | `attempted_not_reproducible` | `attempted_not_reproducible` | `tfe_source_paper_pendulum_suite_does_not_define_this_mechanism_runner` | `SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json` | `0` |
| `tfe2026_original_pendulum` | `tfe2026_Newmark_beta` | `four_link` | `attempted_not_reproducible` | `attempted_not_reproducible` | `attempted_not_reproducible` | `tfe_source_paper_pendulum_suite_does_not_define_this_mechanism_runner` | `SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json` | `0` |
| `tfe2026_original_pendulum` | `tfe2026_Newmark_beta` | `slider_crank` | `attempted_not_reproducible` | `attempted_not_reproducible` | `attempted_not_reproducible` | `tfe_source_paper_pendulum_suite_does_not_define_this_mechanism_runner` | `SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json` | `0` |
| `tfe2026_original_pendulum` | `tfe2026_TFE_m1` | `single_pendulum` | `attempted_not_reproducible` | `attempted_not_reproducible` | `attempted_not_reproducible` | `paper_spec_candidate_runner_not_source_policy_equivalent` | `SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json` | `0` |
| `tfe2026_original_pendulum` | `tfe2026_TFE_m1` | `double_pendulum` | `attempted_not_reproducible` | `attempted_not_reproducible` | `attempted_not_reproducible` | `tfe_source_paper_pendulum_suite_does_not_define_this_mechanism_runner` | `SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json` | `0` |
| `tfe2026_original_pendulum` | `tfe2026_TFE_m1` | `four_link` | `attempted_not_reproducible` | `attempted_not_reproducible` | `attempted_not_reproducible` | `tfe_source_paper_pendulum_suite_does_not_define_this_mechanism_runner` | `SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json` | `0` |
| `tfe2026_original_pendulum` | `tfe2026_TFE_m1` | `slider_crank` | `attempted_not_reproducible` | `attempted_not_reproducible` | `attempted_not_reproducible` | `tfe_source_paper_pendulum_suite_does_not_define_this_mechanism_runner` | `SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json` | `0` |
| `tfe2026_original_pendulum` | `tfe2026_TFE_m2` | `single_pendulum` | `attempted_not_reproducible` | `attempted_not_reproducible` | `attempted_not_reproducible` | `paper_spec_candidate_runner_not_source_policy_equivalent` | `SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json` | `0` |
| `tfe2026_original_pendulum` | `tfe2026_TFE_m2` | `double_pendulum` | `attempted_not_reproducible` | `attempted_not_reproducible` | `attempted_not_reproducible` | `tfe_source_paper_pendulum_suite_does_not_define_this_mechanism_runner` | `SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json` | `0` |
| `tfe2026_original_pendulum` | `tfe2026_TFE_m2` | `four_link` | `attempted_not_reproducible` | `attempted_not_reproducible` | `attempted_not_reproducible` | `tfe_source_paper_pendulum_suite_does_not_define_this_mechanism_runner` | `SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json` | `0` |
| `tfe2026_original_pendulum` | `tfe2026_TFE_m2` | `slider_crank` | `attempted_not_reproducible` | `attempted_not_reproducible` | `attempted_not_reproducible` | `tfe_source_paper_pendulum_suite_does_not_define_this_mechanism_runner` | `SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json` | `0` |
| `tfe2026_original_pendulum` | `tfe2026_trapezoidal` | `single_pendulum` | `attempted_not_reproducible` | `attempted_not_reproducible` | `attempted_not_reproducible` | `paper_spec_candidate_runner_not_source_policy_equivalent` | `SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json` | `0` |
| `tfe2026_original_pendulum` | `tfe2026_trapezoidal` | `double_pendulum` | `attempted_not_reproducible` | `attempted_not_reproducible` | `attempted_not_reproducible` | `tfe_source_paper_pendulum_suite_does_not_define_this_mechanism_runner` | `SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json` | `0` |
| `tfe2026_original_pendulum` | `tfe2026_trapezoidal` | `four_link` | `attempted_not_reproducible` | `attempted_not_reproducible` | `attempted_not_reproducible` | `tfe_source_paper_pendulum_suite_does_not_define_this_mechanism_runner` | `SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json` | `0` |
| `tfe2026_original_pendulum` | `tfe2026_trapezoidal` | `slider_crank` | `attempted_not_reproducible` | `attempted_not_reproducible` | `attempted_not_reproducible` | `tfe_source_paper_pendulum_suite_does_not_define_this_mechanism_runner` | `SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json` | `0` |
| `vp2024_velocity_partitioning` | `vp2024_coordinate_partitioning_rA` | `single_pendulum` | `attempted_not_reproducible` | `attempted_not_reproducible` | `attempted_not_reproducible` | `distinct_public_vp2024_code_path_not_found_proxy_not_source_policy` | `SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json` | `0` |
| `vp2024_velocity_partitioning` | `vp2024_coordinate_partitioning_rA` | `double_pendulum` | `attempted_not_reproducible` | `attempted_not_reproducible` | `attempted_not_reproducible` | `distinct_public_vp2024_code_path_not_found_proxy_not_source_policy` | `SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json` | `0` |
| `vp2024_velocity_partitioning` | `vp2024_coordinate_partitioning_rA` | `four_link` | `attempted_not_reproducible` | `attempted_not_reproducible` | `attempted_not_reproducible` | `distinct_public_vp2024_code_path_not_found_proxy_not_source_policy` | `SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json` | `0` |
| `vp2024_velocity_partitioning` | `vp2024_coordinate_partitioning_rA` | `slider_crank` | `attempted_not_reproducible` | `attempted_not_reproducible` | `attempted_not_reproducible` | `distinct_public_vp2024_code_path_not_found_proxy_not_source_policy` | `SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json` | `0` |

The flagged-row ledger tracks the 15 anomaly rows; this B4 ledger tracks all 40 external method/example cells required before source-policy work/precision figures can close.
