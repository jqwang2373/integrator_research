# All-Method Example Claim-Disposition Audit

Status: **ALL 40 NONLOCAL METHOD/EXAMPLE ROWS CHECKED; SOURCE-POLICY CLAIMS REMAIN OPEN**.

Examples checked: `single_pendulum, double_pendulum, four_link, slider_crank`.
Method/example cells: `44/44`.
Nonlocal comparison cells: `40/40`.
Local velocity-order wins: `40/40`.
Local finest-velocity-error wins: `40/40`.
Nonlocal source-policy closed rows: `0/40`.
Nonlocal source-policy open rows: `40/40`.
Flagged nonlocal rows: `15/40`.
Strict external error-claim rows: `0`.
Source-policy superiority claim allowed: `False`.
Default `1e-4` required: `False`.
Heavy numerical run invoked: `False`.

## Suite Summary

| suite | rows | order wins | error wins | source-policy closed | flagged rows |
|---|---:|---:|---:|---:|---:|
| `hi2022_half_implicit` | `8` | `8` | `8` | `0` | `3` |
| `ra2021_absolute_coordinate` | `12` | `12` | `12` | `0` | `5` |
| `tfe2026_original_pendulum` | `16` | `16` | `16` | `0` | `4` |
| `vp2024_velocity_partitioning` | `4` | `4` | `4` | `0` | `3` |

## Example Summary

| example | rows | order wins | error wins | source-policy closed | flagged rows |
|---|---:|---:|---:|---:|---:|
| `double_pendulum` | `10` | `10` | `10` | `0` | `2` |
| `four_link` | `10` | `10` | `10` | `0` | `4` |
| `single_pendulum` | `10` | `10` | `10` | `0` | `8` |
| `slider_crank` | `10` | `10` | `10` | `0` | `1` |

## Row Table

| example | method | suite | local order | method order | local vel error | method vel error | order win | error win | source-policy closed | issues |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| `single_pendulum` | `hi2022_rA` | `hi2022_half_implicit` | `5.80133` | `1.00481` | `1.155e-12` | `0.0772451` | `True` | `True` | `False` | `position_aligned_velocity_mismatch, source_policy_not_closed` |
| `single_pendulum` | `hi2022_rA_half` | `hi2022_half_implicit` | `5.80133` | `1.84063` | `1.155e-12` | `0.0772451` | `True` | `True` | `False` | `position_aligned_velocity_mismatch, source_policy_not_closed` |
| `single_pendulum` | `ra2021_rA` | `ra2021_absolute_coordinate` | `5.80133` | `0.616851` | `1.155e-12` | `13.0488` | `True` | `True` | `False` | `position_aligned_velocity_mismatch, source_policy_not_closed` |
| `single_pendulum` | `ra2021_reps` | `ra2021_absolute_coordinate` | `5.80133` | `0.616851` | `1.155e-12` | `13.0488` | `True` | `True` | `False` | `position_aligned_velocity_mismatch, source_policy_not_closed` |
| `single_pendulum` | `ra2021_rp` | `ra2021_absolute_coordinate` | `5.80133` | `0.516813` | `1.155e-12` | `14.99` | `True` | `True` | `False` | `position_aligned_velocity_mismatch, source_policy_not_closed` |
| `single_pendulum` | `tfe2026_Newmark_beta` | `tfe2026_original_pendulum` | `5.80133` | `0.900797` | `1.155e-12` | `14.7909` | `True` | `True` | `False` | `position_aligned_velocity_mismatch, source_policy_not_closed, original_tfe_runner_and_friction_source_policy_open` |
| `single_pendulum` | `tfe2026_TFE_m1` | `tfe2026_original_pendulum` | `5.80133` | `1.02082` | `1.155e-12` | `14.9824` | `True` | `True` | `False` | `position_aligned_velocity_mismatch, source_policy_not_closed, original_tfe_runner_and_friction_source_policy_open` |
| `single_pendulum` | `tfe2026_TFE_m2` | `tfe2026_original_pendulum` | `5.80133` | `0.0537298` | `1.155e-12` | `110.22` | `True` | `True` | `False` | `position_aligned_velocity_mismatch, source_policy_not_closed, original_tfe_runner_and_friction_source_policy_open` |
| `single_pendulum` | `tfe2026_trapezoidal` | `tfe2026_original_pendulum` | `5.80133` | `1.02446` | `1.155e-12` | `14.9826` | `True` | `True` | `False` | `position_aligned_velocity_mismatch, source_policy_not_closed, original_tfe_runner_and_friction_source_policy_open` |
| `single_pendulum` | `vp2024_coordinate_partitioning_rA` | `vp2024_velocity_partitioning` | `5.80133` | `6.149e-15` | `1.155e-12` | `3.163e-11` | `True` | `True` | `False` | `near_floor_order_unidentifiable, velocity_error_nonmonotone_or_floor_limited, source_policy_not_closed, vp2024_code_path_unresolved_or_proxy` |
| `double_pendulum` | `hi2022_rA` | `hi2022_half_implicit` | `6.0097` | `1.04906` | `2.346e-13` | `4.944e-05` | `True` | `True` | `False` | `source_policy_not_closed` |
| `double_pendulum` | `hi2022_rA_half` | `hi2022_half_implicit` | `6.0097` | `-0.798995` | `2.346e-13` | `2.96995` | `True` | `True` | `False` | `negative_velocity_order, velocity_error_nonmonotone_or_floor_limited, source_policy_not_closed` |
| `double_pendulum` | `ra2021_rA` | `ra2021_absolute_coordinate` | `6.0097` | `1.05244` | `2.346e-13` | `4.924e-05` | `True` | `True` | `False` | `source_policy_not_closed` |
| `double_pendulum` | `ra2021_reps` | `ra2021_absolute_coordinate` | `6.0097` | `1.05244` | `2.346e-13` | `4.924e-05` | `True` | `True` | `False` | `source_policy_not_closed` |
| `double_pendulum` | `ra2021_rp` | `ra2021_absolute_coordinate` | `6.0097` | `0.36139` | `2.346e-13` | `5.241e-05` | `True` | `True` | `False` | `velocity_error_nonmonotone_or_floor_limited, source_policy_not_closed` |
| `double_pendulum` | `tfe2026_Newmark_beta` | `tfe2026_original_pendulum` | `6.0097` | `1.78651` | `2.346e-13` | `4.246e-04` | `True` | `True` | `False` | `source_policy_not_closed, original_tfe_runner_and_friction_source_policy_open` |
| `double_pendulum` | `tfe2026_TFE_m1` | `tfe2026_original_pendulum` | `6.0097` | `1.99606` | `2.346e-13` | `2.708e-04` | `True` | `True` | `False` | `source_policy_not_closed, original_tfe_runner_and_friction_source_policy_open` |
| `double_pendulum` | `tfe2026_TFE_m2` | `tfe2026_original_pendulum` | `6.0097` | `1.86993` | `2.346e-13` | `8.711e-05` | `True` | `True` | `False` | `source_policy_not_closed, original_tfe_runner_and_friction_source_policy_open` |
| `double_pendulum` | `tfe2026_trapezoidal` | `tfe2026_original_pendulum` | `6.0097` | `1.99966` | `2.346e-13` | `2.708e-04` | `True` | `True` | `False` | `source_policy_not_closed, original_tfe_runner_and_friction_source_policy_open` |
| `double_pendulum` | `vp2024_coordinate_partitioning_rA` | `vp2024_velocity_partitioning` | `6.0097` | `1.00005` | `2.346e-13` | `0.00216512` | `True` | `True` | `False` | `source_policy_not_closed, vp2024_code_path_unresolved_or_proxy` |
| `four_link` | `hi2022_rA` | `hi2022_half_implicit` | `6.08482` | `1.01545` | `1.093e-11` | `0.197042` | `True` | `True` | `False` | `position_aligned_velocity_mismatch, source_policy_not_closed` |
| `four_link` | `hi2022_rA_half` | `hi2022_half_implicit` | `6.08482` | `1.58965` | `1.093e-11` | `0.197042` | `True` | `True` | `False` | `position_aligned_velocity_mismatch, source_policy_not_closed` |
| `four_link` | `ra2021_rA` | `ra2021_absolute_coordinate` | `6.08482` | `1.01545` | `1.093e-11` | `0.197042` | `True` | `True` | `False` | `position_aligned_velocity_mismatch, source_policy_not_closed` |
| `four_link` | `ra2021_reps` | `ra2021_absolute_coordinate` | `6.08482` | `2.89379` | `1.093e-11` | `0.0145777` | `True` | `True` | `False` | `position_aligned_velocity_mismatch, source_policy_not_closed` |
| `four_link` | `ra2021_rp` | `ra2021_absolute_coordinate` | `6.08482` | `2.89373` | `1.093e-11` | `0.0145788` | `True` | `True` | `False` | `position_aligned_velocity_mismatch, source_policy_not_closed` |
| `four_link` | `tfe2026_Newmark_beta` | `tfe2026_original_pendulum` | `6.08482` | `1.87247` | `1.093e-11` | `0.016722` | `True` | `True` | `False` | `position_aligned_velocity_mismatch, source_policy_not_closed, original_tfe_runner_and_friction_source_policy_open` |
| `four_link` | `tfe2026_TFE_m1` | `tfe2026_original_pendulum` | `6.08482` | `3.86566` | `1.093e-11` | `5.253e-04` | `True` | `True` | `False` | `source_policy_not_closed, original_tfe_runner_and_friction_source_policy_open` |
| `four_link` | `tfe2026_TFE_m2` | `tfe2026_original_pendulum` | `6.08482` | `1.02133` | `1.093e-11` | `6.711e-04` | `True` | `True` | `False` | `source_policy_not_closed, original_tfe_runner_and_friction_source_policy_open` |
| `four_link` | `tfe2026_trapezoidal` | `tfe2026_original_pendulum` | `6.08482` | `3.88811` | `1.093e-11` | `5.306e-04` | `True` | `True` | `False` | `source_policy_not_closed, original_tfe_runner_and_friction_source_policy_open` |
| `four_link` | `vp2024_coordinate_partitioning_rA` | `vp2024_velocity_partitioning` | `6.08482` | `-5.332e-04` | `1.093e-11` | `1.087e-08` | `True` | `True` | `False` | `near_floor_order_unidentifiable, negative_velocity_order, velocity_error_nonmonotone_or_floor_limited, source_policy_not_closed, vp2024_code_path_unresolved_or_proxy` |
| `slider_crank` | `hi2022_rA` | `hi2022_half_implicit` | `7.34091` | `0.940514` | `9.189e-12` | `0.0328072` | `True` | `True` | `False` | `position_aligned_velocity_mismatch, source_policy_not_closed` |
| `slider_crank` | `hi2022_rA_half` | `hi2022_half_implicit` | `7.34091` | `2.45854` | `9.189e-12` | `0.0328072` | `True` | `True` | `False` | `position_aligned_velocity_mismatch, source_policy_not_closed` |
| `slider_crank` | `ra2021_rA` | `ra2021_absolute_coordinate` | `7.34091` | `0.940524` | `9.189e-12` | `0.0328068` | `True` | `True` | `False` | `position_aligned_velocity_mismatch, source_policy_not_closed` |
| `slider_crank` | `ra2021_reps` | `ra2021_absolute_coordinate` | `7.34091` | `0.940496` | `9.189e-12` | `0.032807` | `True` | `True` | `False` | `position_aligned_velocity_mismatch, source_policy_not_closed` |
| `slider_crank` | `ra2021_rp` | `ra2021_absolute_coordinate` | `7.34091` | `0.940461` | `9.189e-12` | `0.0328069` | `True` | `True` | `False` | `position_aligned_velocity_mismatch, source_policy_not_closed` |
| `slider_crank` | `tfe2026_Newmark_beta` | `tfe2026_original_pendulum` | `7.34091` | `2.05116` | `9.189e-12` | `0.00153123` | `True` | `True` | `False` | `source_policy_not_closed, original_tfe_runner_and_friction_source_policy_open` |
| `slider_crank` | `tfe2026_TFE_m1` | `tfe2026_original_pendulum` | `7.34091` | `2.48136` | `9.189e-12` | `6.264e-04` | `True` | `True` | `False` | `source_policy_not_closed, original_tfe_runner_and_friction_source_policy_open` |
| `slider_crank` | `tfe2026_TFE_m2` | `tfe2026_original_pendulum` | `7.34091` | `2.2899` | `9.189e-12` | `9.881e-05` | `True` | `True` | `False` | `source_policy_not_closed, original_tfe_runner_and_friction_source_policy_open` |
| `slider_crank` | `tfe2026_trapezoidal` | `tfe2026_original_pendulum` | `7.34091` | `2.32935` | `9.189e-12` | `7.328e-04` | `True` | `True` | `False` | `source_policy_not_closed, original_tfe_runner_and_friction_source_policy_open` |
| `slider_crank` | `vp2024_coordinate_partitioning_rA` | `vp2024_velocity_partitioning` | `7.34091` | `-3.253e-07` | `9.189e-12` | `1.332e-07` | `True` | `True` | `False` | `near_floor_order_unidentifiable, negative_velocity_order, velocity_error_nonmonotone_or_floor_limited, source_policy_not_closed, vp2024_code_path_unresolved_or_proxy` |

## Interpretation

The common-reference arithmetic is closed for every nonlocal comparison row: the bounded diagnostic records 40/40 positive velocity-order rows and 40/40 positive finest-velocity-error rows. This is a bounded finite-grid diagnostic, not a source-policy reproduction certificate.

The `15` flagged rows are anomaly or source-policy recheck rows. They are not the only rows with an open source-policy boundary: all 40 nonlocal rows remain source-policy open and are barred from external-superiority claims until their source-policy evidence is closed or the corresponding suite is explicitly demoted.
