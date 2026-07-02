# Paper Numerical Result Matrix

Status: **paper-ready table with source-policy boundary open**.

- Method/example cells: `44/44`.
- Examples: `single_pendulum, double_pendulum, four_link, slider_crank`.
- Methods: `11`.
- Step sizes: `0.1, 0.05, 0.025`.
- Reference h: `0.0125`.
- Raw rows behind this matrix: `132`.
- Source-policy external superiority allowed: `False`.
- Paper-level direct error superiority allowed: `False`.
- Strict external error-claim rows: `0`.

Each row reports `observed order / finest-step error`. The velocity column is the primary
comparison column used by the current common-reference diagnostic; the position and
acceleration columns are included for auditability.

## single_pendulum

| Method | Source level | Position | Velocity | Acceleration | Claim scope | Issues |
|---|---|---:|---:|---:|---|---|
| `local_Gauss6_FullVA` | `local_proposed_method` | `6.013 / 3.323e-14` | `5.801 / 1.155e-12` | `nan / nan` | `internal_order_evidence` | `none` |
| `hi2022_rA` | `public_code_bounded_replay` | `9.343e-05 / 1.046e-10` | `1.005 / 0.077` | `2.244 / 0.135` | `bounded_common_reference_diagnostic_not_source_policy_superiority` | `position_aligned_velocity_mismatch, source_policy_not_closed` |
| `hi2022_rA_half` | `public_code_bounded_replay` | `-1.532e-06 / 1.046e-10` | `1.841 / 0.077` | `3.111 / 0.135` | `bounded_common_reference_diagnostic_not_source_policy_superiority` | `position_aligned_velocity_mismatch, source_policy_not_closed` |
| `ra2021_rA` | `public_code_replay` | `4.520e-04 / 1.045e-10` | `0.617 / 13.049` | `1.507 / 3.877e+03` | `bounded_common_reference_diagnostic_not_source_policy_superiority` | `position_aligned_velocity_mismatch, source_policy_not_closed` |
| `ra2021_reps` | `public_code_replay` | `-1.940 / 6.610e-14` | `0.617 / 13.049` | `1.507 / 3.877e+03` | `bounded_common_reference_diagnostic_not_source_policy_superiority` | `position_aligned_velocity_mismatch, source_policy_not_closed` |
| `ra2021_rp` | `public_code_replay` | `-0.068 / 1.114e-14` | `0.517 / 14.990` | `1.512 / 3.851e+03` | `bounded_common_reference_diagnostic_not_source_policy_superiority` | `position_aligned_velocity_mismatch, source_policy_not_closed` |
| `tfe2026_Newmark_beta` | `local_formula_proxy` | `-1.532e-06 / 1.046e-10` | `0.901 / 14.791` | `1.883 / 7.671e+03` | `formula_proxy_diagnostic_not_original_paper_superiority` | `position_aligned_velocity_mismatch, source_policy_not_closed, original_tfe_runner_and_friction_source_policy_open` |
| `tfe2026_TFE_m1` | `local_formula_proxy` | `3.629e-15 / 1.046e-10` | `1.021 / 14.982` | `4.370 / 289.962` | `formula_proxy_diagnostic_not_original_paper_superiority` | `position_aligned_velocity_mismatch, source_policy_not_closed, original_tfe_runner_and_friction_source_policy_open` |
| `tfe2026_TFE_m2` | `local_formula_proxy` | `6.342e-11 / 1.046e-10` | `0.054 / 110.220` | `-0.486 / 2.086e+06` | `formula_proxy_diagnostic_not_original_paper_superiority` | `position_aligned_velocity_mismatch, source_policy_not_closed, original_tfe_runner_and_friction_source_policy_open` |
| `tfe2026_trapezoidal` | `local_formula_proxy` | `1.466e-15 / 1.046e-10` | `1.024 / 14.983` | `4.649 / 199.058` | `formula_proxy_diagnostic_not_original_paper_superiority` | `position_aligned_velocity_mismatch, source_policy_not_closed, original_tfe_runner_and_friction_source_policy_open` |
| `vp2024_coordinate_partitioning_rA` | `local_proxy_or_alias` | `-6.667e-11 / 1.046e-10` | `6.149e-15 / 3.163e-11` | `7.209e-16 / 2.827e-10` | `proxy_or_alias_diagnostic_not_original_code_superiority` | `near_floor_order_unidentifiable, velocity_error_nonmonotone_or_floor_limited, source_policy_not_closed, vp2024_code_path_unresolved_or_proxy` |

## double_pendulum

| Method | Source level | Position | Velocity | Acceleration | Claim scope | Issues |
|---|---|---:|---:|---:|---|---|
| `local_Gauss6_FullVA` | `local_proposed_method` | `6.011 / 3.100e-13` | `6.010 / 2.346e-13` | `nan / nan` | `internal_order_evidence` | `none` |
| `hi2022_rA` | `public_code_bounded_replay` | `1.000 / 0.015` | `1.049 / 4.944e-05` | `nan / nan` | `bounded_common_reference_diagnostic_not_source_policy_superiority` | `source_policy_not_closed` |
| `hi2022_rA_half` | `public_code_bounded_replay` | `0.053 / 0.164` | `-0.799 / 2.970` | `nan / nan` | `bounded_common_reference_diagnostic_not_source_policy_superiority` | `negative_velocity_order, velocity_error_nonmonotone_or_floor_limited, source_policy_not_closed` |
| `ra2021_rA` | `public_code_replay` | `1.000 / 0.015` | `1.052 / 4.924e-05` | `nan / nan` | `bounded_common_reference_diagnostic_not_source_policy_superiority` | `source_policy_not_closed` |
| `ra2021_reps` | `public_code_replay` | `1.000 / 0.015` | `1.052 / 4.924e-05` | `nan / nan` | `bounded_common_reference_diagnostic_not_source_policy_superiority` | `source_policy_not_closed` |
| `ra2021_rp` | `public_code_replay` | `1.716 / 0.005` | `0.361 / 5.241e-05` | `nan / nan` | `bounded_common_reference_diagnostic_not_source_policy_superiority` | `velocity_error_nonmonotone_or_floor_limited, source_policy_not_closed` |
| `tfe2026_Newmark_beta` | `local_formula_proxy` | `1.181 / 3.985e-07` | `1.787 / 4.246e-04` | `nan / nan` | `formula_proxy_diagnostic_not_original_paper_superiority` | `source_policy_not_closed, original_tfe_runner_and_friction_source_policy_open` |
| `tfe2026_TFE_m1` | `local_formula_proxy` | `0.998 / 7.362e-05` | `1.996 / 2.708e-04` | `nan / nan` | `formula_proxy_diagnostic_not_original_paper_superiority` | `source_policy_not_closed, original_tfe_runner_and_friction_source_policy_open` |
| `tfe2026_TFE_m2` | `local_formula_proxy` | `2.359 / 1.800e-08` | `1.870 / 8.711e-05` | `nan / nan` | `formula_proxy_diagnostic_not_original_paper_superiority` | `source_policy_not_closed, original_tfe_runner_and_friction_source_policy_open` |
| `tfe2026_trapezoidal` | `local_formula_proxy` | `1.338 / 3.111e-07` | `2.000 / 2.708e-04` | `nan / nan` | `formula_proxy_diagnostic_not_original_paper_superiority` | `source_policy_not_closed, original_tfe_runner_and_friction_source_policy_open` |
| `vp2024_coordinate_partitioning_rA` | `local_proxy_or_alias` | `1.000 / 0.015` | `1.000 / 0.002` | `nan / nan` | `proxy_or_alias_diagnostic_not_original_code_superiority` | `source_policy_not_closed, vp2024_code_path_unresolved_or_proxy` |

## four_link

| Method | Source level | Position | Velocity | Acceleration | Claim scope | Issues |
|---|---|---:|---:|---:|---|---|
| `local_Gauss6_FullVA` | `local_proposed_method` | `5.955 / 2.289e-12` | `6.085 / 1.093e-11` | `0.995 / 0.880` | `internal_order_evidence` | `none` |
| `hi2022_rA` | `public_code_bounded_replay` | `-2.552e-05 / 8.773e-09` | `1.015 / 0.197` | `1.036 / 1.754` | `bounded_common_reference_diagnostic_not_source_policy_superiority` | `position_aligned_velocity_mismatch, source_policy_not_closed` |
| `hi2022_rA_half` | `public_code_bounded_replay` | `1.072e-04 / 8.773e-09` | `1.590 / 0.197` | `1.792 / 1.754` | `bounded_common_reference_diagnostic_not_source_policy_superiority` | `position_aligned_velocity_mismatch, source_policy_not_closed` |
| `ra2021_rA` | `public_code_replay` | `0.913 / 1.086e-08` | `1.015 / 0.197` | `1.036 / 1.754` | `bounded_common_reference_diagnostic_not_source_policy_superiority` | `position_aligned_velocity_mismatch, source_policy_not_closed` |
| `ra2021_reps` | `public_code_replay` | `-1.100 / 2.573e-08` | `2.894 / 0.015` | `3.956 / 0.031` | `bounded_common_reference_diagnostic_not_source_policy_superiority` | `position_aligned_velocity_mismatch, source_policy_not_closed` |
| `ra2021_rp` | `public_code_replay` | `3.661 / 7.849e-11` | `2.894 / 0.015` | `3.946 / 0.031` | `bounded_common_reference_diagnostic_not_source_policy_superiority` | `position_aligned_velocity_mismatch, source_policy_not_closed` |
| `tfe2026_Newmark_beta` | `local_formula_proxy` | `-3.652e-08 / 8.773e-09` | `1.872 / 0.017` | `-0.198 / 8.620` | `formula_proxy_diagnostic_not_original_paper_superiority` | `position_aligned_velocity_mismatch, source_policy_not_closed, original_tfe_runner_and_friction_source_policy_open` |
| `tfe2026_TFE_m1` | `local_formula_proxy` | `-1.826e-07 / 8.773e-09` | `3.866 / 5.253e-04` | `0.068 / 8.193` | `formula_proxy_diagnostic_not_original_paper_superiority` | `source_policy_not_closed, original_tfe_runner_and_friction_source_policy_open` |
| `tfe2026_TFE_m2` | `local_formula_proxy` | `-9.859e-07 / 8.773e-09` | `1.021 / 6.711e-04` | `0.128 / 7.008` | `formula_proxy_diagnostic_not_original_paper_superiority` | `source_policy_not_closed, original_tfe_runner_and_friction_source_policy_open` |
| `tfe2026_trapezoidal` | `local_formula_proxy` | `1.826e-07 / 8.773e-09` | `3.888 / 5.306e-04` | `0.003 / 9.214` | `formula_proxy_diagnostic_not_original_paper_superiority` | `source_policy_not_closed, original_tfe_runner_and_friction_source_policy_open` |
| `vp2024_coordinate_partitioning_rA` | `local_proxy_or_alias` | `1.095e-07 / 8.773e-09` | `-5.332e-04 / 1.087e-08` | `3.307e-06 / 4.727e-08` | `proxy_or_alias_diagnostic_not_original_code_superiority` | `near_floor_order_unidentifiable, negative_velocity_order, velocity_error_nonmonotone_or_floor_limited, source_policy_not_closed, vp2024_code_path_unresolved_or_proxy` |

## slider_crank

| Method | Source level | Position | Velocity | Acceleration | Claim scope | Issues |
|---|---|---:|---:|---:|---|---|
| `local_Gauss6_FullVA` | `local_proposed_method` | `6.164 / 8.583e-12` | `7.341 / 9.189e-12` | `1.054 / 0.104` | `internal_order_evidence` | `none` |
| `hi2022_rA` | `public_code_bounded_replay` | `-9.667e-09 / 3.024e-07` | `0.941 / 0.033` | `1.470 / 0.213` | `bounded_common_reference_diagnostic_not_source_policy_superiority` | `position_aligned_velocity_mismatch, source_policy_not_closed` |
| `hi2022_rA_half` | `public_code_bounded_replay` | `-1.343e-06 / 3.024e-07` | `2.459 / 0.033` | `2.785 / 0.213` | `bounded_common_reference_diagnostic_not_source_policy_superiority` | `position_aligned_velocity_mismatch, source_policy_not_closed` |
| `ra2021_rA` | `public_code_replay` | `0.015 / 2.962e-07` | `0.941 / 0.033` | `1.470 / 0.213` | `bounded_common_reference_diagnostic_not_source_policy_superiority` | `position_aligned_velocity_mismatch, source_policy_not_closed` |
| `ra2021_reps` | `public_code_replay` | `2.294 / 5.273e-09` | `0.940 / 0.033` | `1.470 / 0.213` | `bounded_common_reference_diagnostic_not_source_policy_superiority` | `position_aligned_velocity_mismatch, source_policy_not_closed` |
| `ra2021_rp` | `public_code_replay` | `2.718 / 1.663e-08` | `0.940 / 0.033` | `1.470 / 0.213` | `bounded_common_reference_diagnostic_not_source_policy_superiority` | `position_aligned_velocity_mismatch, source_policy_not_closed` |
| `tfe2026_Newmark_beta` | `local_formula_proxy` | `2.053e-09 / 3.024e-07` | `2.051 / 0.002` | `1.900 / 0.028` | `formula_proxy_diagnostic_not_original_paper_superiority` | `source_policy_not_closed, original_tfe_runner_and_friction_source_policy_open` |
| `tfe2026_TFE_m1` | `local_formula_proxy` | `1.390e-09 / 3.024e-07` | `2.481 / 6.264e-04` | `-0.543 / 0.607` | `formula_proxy_diagnostic_not_original_paper_superiority` | `source_policy_not_closed, original_tfe_runner_and_friction_source_policy_open` |
| `tfe2026_TFE_m2` | `local_formula_proxy` | `-2.516e-09 / 3.024e-07` | `2.290 / 9.881e-05` | `0.534 / 0.085` | `formula_proxy_diagnostic_not_original_paper_superiority` | `source_policy_not_closed, original_tfe_runner_and_friction_source_policy_open` |
| `tfe2026_trapezoidal` | `local_formula_proxy` | `5.297e-10 / 3.024e-07` | `2.329 / 7.328e-04` | `-0.508 / 0.566` | `formula_proxy_diagnostic_not_original_paper_superiority` | `source_policy_not_closed, original_tfe_runner_and_friction_source_policy_open` |
| `vp2024_coordinate_partitioning_rA` | `local_proxy_or_alias` | `-1.126e-09 / 3.024e-07` | `-3.253e-07 / 1.332e-07` | `-5.216e-08 / 1.683e-06` | `proxy_or_alias_diagnostic_not_original_code_superiority` | `near_floor_order_unidentifiable, negative_velocity_order, velocity_error_nonmonotone_or_floor_limited, source_policy_not_closed, vp2024_code_path_unresolved_or_proxy` |

## Reading Rule

This matrix is safe for reporting observed order/error under the bounded common-reference
diagnostic. It is not a source-policy reproduction and it does not authorize a blanket
external-superiority claim over the cited source papers.
