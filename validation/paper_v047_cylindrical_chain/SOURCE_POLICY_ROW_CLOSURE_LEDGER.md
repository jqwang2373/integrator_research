# Source-Policy Row Closure Ledger

Status: **ROW-LEVEL SOURCE-POLICY CLOSURE OPEN**

- Flagged source-policy rows: `15`.
- Examples covered: `double_pendulum, four_link, single_pendulum, slider_crank`.
- Rows source-policy closed: `0`.
- Rows external-superiority ready: `0`.
- B2/B4 can close now: `False/False`.
- RA2021 resolved source-identity evidence per active row: `3`; remaining promotion evidence per active row: `4`.
- Parallel-ready shards without default `1e-4`: `20`.
- Heavy numerical run invoked: `False`.

## Flagged Rows By Example

| example | flagged rows |
| --- | ---: |
| `single_pendulum` | 8 |
| `double_pendulum` | 2 |
| `four_link` | 4 |
| `slider_crank` | 1 |

## Suite Status

| suite | flagged rows | status |
| --- | ---: | --- |
| `ra2021_absolute_coordinate` | 5 | `open_verify_or_rerun_public_rows` |
| `tfe2026_original_pendulum` | 4 | `attempted_not_reproducible_not_promoted_source_policy_rows_not_closed` |
| `hi2022_half_implicit` | 3 | `open_choose_full_T8_policy_or_demote` |
| `vp2024_velocity_partitioning` | 3 | `attempted_not_reproducible_not_promoted_no_distinct_public_code_path` |

## Row Ledger

| suite | example | method | velocity order | finest velocity error | disposition/action | missing evidence count | allowed use |
| --- | --- | --- | ---: | ---: | --- | ---: | --- |
| `hi2022_half_implicit` | `four_link` | `hi2022_rA` | 1.02 | 1.970e-01 | `choose_full_T8_public_policy_or_demote` | 5 | `diagnostic_common_reference_only` |
| `hi2022_half_implicit` | `double_pendulum` | `hi2022_rA_half` | -0.799 | 2.970e+00 | `choose_full_T8_public_policy_or_demote` | 5 | `diagnostic_common_reference_only` |
| `hi2022_half_implicit` | `four_link` | `hi2022_rA_half` | 1.59 | 1.970e-01 | `choose_full_T8_public_policy_or_demote` | 5 | `diagnostic_common_reference_only` |
| `ra2021_absolute_coordinate` | `single_pendulum` | `ra2021_rA` | 0.617 | 1.305e+01 | `fix_or_rerun_public_velocity_mapping_time_grid_norm_runtime` | 4 | `diagnostic_common_reference_only` |
| `ra2021_absolute_coordinate` | `four_link` | `ra2021_rA` | 1.02 | 1.970e-01 | `fix_or_rerun_public_velocity_mapping_time_grid_norm_runtime` | 4 | `diagnostic_common_reference_only` |
| `ra2021_absolute_coordinate` | `single_pendulum` | `ra2021_reps` | 0.617 | 1.305e+01 | `fix_or_rerun_public_velocity_mapping_time_grid_norm_runtime` | 4 | `diagnostic_common_reference_only` |
| `ra2021_absolute_coordinate` | `single_pendulum` | `ra2021_rp` | 0.517 | 1.499e+01 | `fix_or_rerun_public_velocity_mapping_time_grid_norm_runtime` | 4 | `diagnostic_common_reference_only` |
| `ra2021_absolute_coordinate` | `double_pendulum` | `ra2021_rp` | 0.361 | 5.241e-05 | `fix_or_rerun_public_velocity_mapping_time_grid_norm_runtime` | 4 | `diagnostic_common_reference_only` |
| `tfe2026_original_pendulum` | `single_pendulum` | `tfe2026_Newmark_beta` | 0.901 | 1.479e+01 | `attempted_not_reproducible_not_promoted` | 5 | `attempted_not_reproducible_not_promoted_diagnostic_only` |
| `tfe2026_original_pendulum` | `single_pendulum` | `tfe2026_TFE_m1` | 1.02 | 1.498e+01 | `attempted_not_reproducible_not_promoted` | 5 | `attempted_not_reproducible_not_promoted_diagnostic_only` |
| `tfe2026_original_pendulum` | `single_pendulum` | `tfe2026_TFE_m2` | 0.0537 | 1.102e+02 | `attempted_not_reproducible_not_promoted` | 5 | `attempted_not_reproducible_not_promoted_diagnostic_only` |
| `tfe2026_original_pendulum` | `single_pendulum` | `tfe2026_trapezoidal` | 1.02 | 1.498e+01 | `attempted_not_reproducible_not_promoted` | 5 | `attempted_not_reproducible_not_promoted_diagnostic_only` |
| `vp2024_velocity_partitioning` | `single_pendulum` | `vp2024_coordinate_partitioning_rA` | 6.15e-15 | 3.163e-11 | `attempted_not_reproducible_not_promoted` | 5 | `attempted_not_reproducible_not_promoted_diagnostic_only` |
| `vp2024_velocity_partitioning` | `four_link` | `vp2024_coordinate_partitioning_rA` | -0.000533 | 1.087e-08 | `attempted_not_reproducible_not_promoted` | 5 | `attempted_not_reproducible_not_promoted_diagnostic_only` |
| `vp2024_velocity_partitioning` | `slider_crank` | `vp2024_coordinate_partitioning_rA` | -3.25e-07 | 1.332e-07 | `attempted_not_reproducible_not_promoted` | 5 | `attempted_not_reproducible_not_promoted_diagnostic_only` |

## Closure Rule

Every flagged row must either receive the row-level source-policy evidence
listed in the JSON ledger or be explicitly demoted from the external
superiority claim. Fixed-grid common-reference arithmetic alone is not a
source-policy closure certificate.
