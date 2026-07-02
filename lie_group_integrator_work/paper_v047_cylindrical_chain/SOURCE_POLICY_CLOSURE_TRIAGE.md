# Source-Policy Closure Triage

Status: **TRIAGE ONLY - SOURCE-POLICY CLOSURE NOT RUN**

- Comparison matrix closed: `True`.
- Common-reference claim allowed: `True`.
- Source-policy superiority allowed: `False`.
- Flagged source-policy rows: `15`.
- Flagged examples: `double_pendulum, four_link, single_pendulum, slider_crank`.
- All four examples covered by flagged rows: `True`.
- B2/B4 can close now: `False/False`.
- Default `1e-4` required: `False`.
- Heavy numerical run invoked: `False`.

## Action Plan

| priority | suite | disposition/action | rows | next step |
| ---: | --- | --- | ---: | --- |
| 1 | `ra2021_absolute_coordinate` | `fix_or_rerun_public_velocity_mapping_time_grid_norm_runtime` | 5 | Rerun or independently verify the public rA/rp/reps rows under the declared state-velocity mapping, time-grid convention, error norm, and runtime policy. |
| 2 | `tfe2026_original_pendulum` | `attempted_not_reproducible_not_promoted` | 4 | No distinct public TFE code artifact was found; paper-spec reconstruction was attempted but is not source-policy equivalent, so keep these rows not promoted unless a new source-code-equivalent artifact appears. |
| 3 | `hi2022_half_implicit` | `choose_full_T8_public_policy_or_demote` | 3 | Choose the full T=8 public-policy reproduction or explicitly keep the bounded pilot as a non-claim. |
| 4 | `vp2024_velocity_partitioning` | `attempted_not_reproducible_not_promoted` | 3 | The public repository tree was rechecked and no distinct VP2024 code path was found; keep the coordinate-partitioning proxy diagnostic-only unless a new public path or author artifact appears. |

## Flagged Rows

| suite | example | method | disposition/action |
| --- | --- | --- | --- |
| `hi2022_half_implicit` | `four_link` | `hi2022_rA` | `choose_full_T8_public_policy_or_demote` |
| `hi2022_half_implicit` | `double_pendulum` | `hi2022_rA_half` | `choose_full_T8_public_policy_or_demote` |
| `hi2022_half_implicit` | `four_link` | `hi2022_rA_half` | `choose_full_T8_public_policy_or_demote` |
| `ra2021_absolute_coordinate` | `single_pendulum` | `ra2021_rA` | `fix_or_rerun_public_velocity_mapping_time_grid_norm_runtime` |
| `ra2021_absolute_coordinate` | `four_link` | `ra2021_rA` | `fix_or_rerun_public_velocity_mapping_time_grid_norm_runtime` |
| `ra2021_absolute_coordinate` | `single_pendulum` | `ra2021_reps` | `fix_or_rerun_public_velocity_mapping_time_grid_norm_runtime` |
| `ra2021_absolute_coordinate` | `single_pendulum` | `ra2021_rp` | `fix_or_rerun_public_velocity_mapping_time_grid_norm_runtime` |
| `ra2021_absolute_coordinate` | `double_pendulum` | `ra2021_rp` | `fix_or_rerun_public_velocity_mapping_time_grid_norm_runtime` |
| `tfe2026_original_pendulum` | `single_pendulum` | `tfe2026_Newmark_beta` | `attempted_not_reproducible_not_promoted` |
| `tfe2026_original_pendulum` | `single_pendulum` | `tfe2026_TFE_m1` | `attempted_not_reproducible_not_promoted` |
| `tfe2026_original_pendulum` | `single_pendulum` | `tfe2026_TFE_m2` | `attempted_not_reproducible_not_promoted` |
| `tfe2026_original_pendulum` | `single_pendulum` | `tfe2026_trapezoidal` | `attempted_not_reproducible_not_promoted` |
| `vp2024_velocity_partitioning` | `single_pendulum` | `vp2024_coordinate_partitioning_rA` | `attempted_not_reproducible_not_promoted` |
| `vp2024_velocity_partitioning` | `four_link` | `vp2024_coordinate_partitioning_rA` | `attempted_not_reproducible_not_promoted` |
| `vp2024_velocity_partitioning` | `slider_crank` | `vp2024_coordinate_partitioning_rA` | `attempted_not_reproducible_not_promoted` |
