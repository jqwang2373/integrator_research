# All-Examples Source-Policy Audit

Status: **ALL FLAGGED EXAMPLES CHECKED - SOURCE-POLICY REPRODUCTION OPEN**

- Flagged rows checked: `15`.
- Flagged raw rows checked: `45`.
- Examples covered: `double_pendulum, four_link, single_pendulum, slider_crank`.
- All four examples covered: `True`.
- Suites covered: `hi2022_half_implicit, ra2021_absolute_coordinate, tfe2026_original_pendulum, vp2024_velocity_partitioning`.
- All rows have `h=[0.1,0.05,0.025]`: `True`.
- Common-reference arithmetic mismatches: `0`.
- Source-policy superiority allowed: `False`.
- B2/B4 can close now: `False/False`.
- Default `1e-4` required: `False`.
- Heavy numerical run invoked: `False`.

## Suite Policy Checks

| suite | rows | row source | source-policy closed | closure required |
| --- | ---: | --- | --- | --- |
| `hi2022_half_implicit` | 3 | public HI2022 setup and public half-implicit stepper | `False` | run_full_T8_public_policy_or_demote_hi2022_rows |
| `ra2021_absolute_coordinate` | 5 | public SimEngineMBD setup and public rA/rp/reps stepper | `False` | rerun_or_independently_verify_public_rows_with_declared_velocity_mapping_time_grid_norm_runtime |
| `tfe2026_original_pendulum` | 4 | paper-spec candidate reconstruction; no distinct public TFE code artifact found | `False` | attempted_not_reproducible_not_promoted_from_available_public_material; keep_as_formal_order_or_diagnostic_comparator_only_unless_new_source_code_equivalent_artifact_appears |
| `vp2024_velocity_partitioning` | 3 | public repository tree rechecked; no distinct VP2024 code path found | `False` | attempted_not_reproducible_not_promoted_until_distinct_public_vp2024_code_path_or_author_artifact_appears |

## Flagged Rows

| example | suite | method | order | finest velocity error | categories |
| --- | --- | --- | ---: | ---: | --- |
| `four_link` | `hi2022_half_implicit` | `hi2022_rA` | 1.01545 | 0.197042 | position_aligned_velocity_mismatch |
| `double_pendulum` | `hi2022_half_implicit` | `hi2022_rA_half` | -0.798995 | 2.96995 | negative_order_large_error_fixed_grid_or_form_mismatch |
| `four_link` | `hi2022_half_implicit` | `hi2022_rA_half` | 1.58965 | 0.197042 | position_aligned_velocity_mismatch |
| `single_pendulum` | `ra2021_absolute_coordinate` | `ra2021_rA` | 0.616851 | 13.0488 | position_aligned_velocity_mismatch, single_pendulum_velocity_output_policy_suspect |
| `four_link` | `ra2021_absolute_coordinate` | `ra2021_rA` | 1.01545 | 0.197042 | position_aligned_velocity_mismatch |
| `single_pendulum` | `ra2021_absolute_coordinate` | `ra2021_reps` | 0.616851 | 13.0488 | position_aligned_velocity_mismatch, single_pendulum_velocity_output_policy_suspect |
| `single_pendulum` | `ra2021_absolute_coordinate` | `ra2021_rp` | 0.516813 | 14.99 | position_aligned_velocity_mismatch, single_pendulum_velocity_output_policy_suspect |
| `double_pendulum` | `ra2021_absolute_coordinate` | `ra2021_rp` | 0.36139 | 5.241e-05 | low_order_but_small_error_needs_wider_step_window |
| `single_pendulum` | `tfe2026_original_pendulum` | `tfe2026_Newmark_beta` | 0.900797 | 14.7909 | position_aligned_velocity_mismatch, single_pendulum_velocity_output_policy_suspect |
| `single_pendulum` | `tfe2026_original_pendulum` | `tfe2026_TFE_m1` | 1.02082 | 14.9824 | position_aligned_velocity_mismatch, single_pendulum_velocity_output_policy_suspect |
| `single_pendulum` | `tfe2026_original_pendulum` | `tfe2026_TFE_m2` | 0.0537298 | 110.22 | position_aligned_velocity_mismatch, single_pendulum_velocity_output_policy_suspect |
| `single_pendulum` | `tfe2026_original_pendulum` | `tfe2026_trapezoidal` | 1.02446 | 14.9826 | position_aligned_velocity_mismatch, single_pendulum_velocity_output_policy_suspect |
| `single_pendulum` | `vp2024_velocity_partitioning` | `vp2024_coordinate_partitioning_rA` | 6.149e-15 | 3.163e-11 | near_reference_floor_order_not_identifiable, low_order_but_small_error_needs_wider_step_window |
| `four_link` | `vp2024_velocity_partitioning` | `vp2024_coordinate_partitioning_rA` | -5.332e-04 | 1.087e-08 | near_reference_floor_order_not_identifiable, low_order_but_small_error_needs_wider_step_window |
| `slider_crank` | `vp2024_velocity_partitioning` | `vp2024_coordinate_partitioning_rA` | -3.253e-07 | 1.332e-07 | near_reference_floor_order_not_identifiable, low_order_but_small_error_needs_wider_step_window |

## Claim Boundary

This audit verifies coverage and source-policy risk classification for every flagged row. It does not close the source-policy reproduction, does not judge method correctness by itself, and does not authorize an external-superiority claim.
