# All Examples Result Sanity Audit

Status: **all four examples audited; not submission-ready external superiority evidence**.

- Coverage: `44/44` method-example cells.
- Examples audited: `single_pendulum, double_pendulum, four_link, slider_crank`.
- Local empirical gate: `4/4` rows pass `order >= 5.5` and `finest velocity error <= 1.0e-08`.
- Flagged nonlocal rows needing source-policy recheck: `15`.
- Flagged examples: `double_pendulum, four_link, single_pendulum, slider_crank`.
- All flagged rows quarantined from external-superiority claims: `True`.
- External superiority allowed from this audit: `False`.

## Local Method Rows

| example | observed velocity order | finest velocity error | disposition |
|---|---:|---:|---|
| `single_pendulum` | `5.801` | `1.155e-12` | `accepted_local_empirical_order_row` |
| `double_pendulum` | `6.010` | `2.346e-13` | `accepted_local_empirical_order_row` |
| `four_link` | `6.085` | `1.093e-11` | `accepted_local_empirical_order_row` |
| `slider_crank` | `7.341` | `9.189e-12` | `accepted_local_empirical_order_row` |

## Flagged Nonlocal Rows

These rows are checked across all examples. A flag is not automatically a method failure; it means the row cannot support a source-policy external-superiority claim until the corresponding source runner, coordinates, output norm, and reference policy are rechecked.

| method | example | observed velocity order | finest velocity error | severity | flags |
|---|---|---:|---:|---|---|
| `hi2022_rA` | `four_link` | `1.015` | `0.197` | `warning_recheck` | `large_finest_velocity_error_gt_0p1` |
| `hi2022_rA_half` | `double_pendulum` | `-0.799` | `2.970` | `critical_recheck` | `negative_observed_order, very_large_finest_velocity_error_gt_1` |
| `hi2022_rA_half` | `four_link` | `1.590` | `0.197` | `warning_recheck` | `large_finest_velocity_error_gt_0p1` |
| `ra2021_rA` | `single_pendulum` | `0.617` | `13.049` | `critical_recheck` | `very_large_finest_velocity_error_gt_1` |
| `ra2021_rA` | `four_link` | `1.015` | `0.197` | `warning_recheck` | `large_finest_velocity_error_gt_0p1` |
| `ra2021_reps` | `single_pendulum` | `0.617` | `13.049` | `critical_recheck` | `very_large_finest_velocity_error_gt_1` |
| `ra2021_rp` | `single_pendulum` | `0.517` | `14.990` | `critical_recheck` | `very_large_finest_velocity_error_gt_1` |
| `ra2021_rp` | `double_pendulum` | `0.361` | `5.241e-05` | `warning_recheck` | `low_observed_order_lt_0p5` |
| `tfe2026_Newmark_beta` | `single_pendulum` | `0.901` | `14.791` | `critical_recheck` | `very_large_finest_velocity_error_gt_1` |
| `tfe2026_TFE_m1` | `single_pendulum` | `1.021` | `14.982` | `critical_recheck` | `very_large_finest_velocity_error_gt_1` |
| `tfe2026_TFE_m2` | `single_pendulum` | `0.054` | `110.220` | `critical_recheck` | `floor_limited_or_zero_observed_order, very_large_finest_velocity_error_gt_1` |
| `tfe2026_trapezoidal` | `single_pendulum` | `1.024` | `14.983` | `critical_recheck` | `very_large_finest_velocity_error_gt_1` |
| `vp2024_coordinate_partitioning_rA` | `single_pendulum` | `6.149e-15` | `3.163e-11` | `critical_recheck` | `floor_limited_or_zero_observed_order` |
| `vp2024_coordinate_partitioning_rA` | `four_link` | `-5.332e-04` | `1.087e-08` | `critical_recheck` | `negative_observed_order` |
| `vp2024_coordinate_partitioning_rA` | `slider_crank` | `-3.253e-07` | `1.332e-07` | `critical_recheck` | `negative_observed_order` |

## Per-Example Flag Counts

| example | flagged nonlocal rows |
|---|---:|
| `single_pendulum` | `8` |
| `double_pendulum` | `2` |
| `four_link` | `4` |
| `slider_crank` | `1` |

## Exact Recheck Set

The validator locks this exact method/example set so a repaired single-pendulum row cannot mask unresolved rows in the other examples.

| method/example row |
|---|
| `hi2022_rA/four_link` |
| `hi2022_rA_half/double_pendulum` |
| `hi2022_rA_half/four_link` |
| `ra2021_rA/four_link` |
| `ra2021_rA/single_pendulum` |
| `ra2021_reps/single_pendulum` |
| `ra2021_rp/double_pendulum` |
| `ra2021_rp/single_pendulum` |
| `tfe2026_Newmark_beta/single_pendulum` |
| `tfe2026_TFE_m1/single_pendulum` |
| `tfe2026_TFE_m2/single_pendulum` |
| `tfe2026_trapezoidal/single_pendulum` |
| `vp2024_coordinate_partitioning_rA/four_link` |
| `vp2024_coordinate_partitioning_rA/single_pendulum` |
| `vp2024_coordinate_partitioning_rA/slider_crank` |

## Boundary

- This audit checks every example, not only `single_pendulum`.
- Every flagged row is quarantined from external-superiority claims until source-policy reproduction is closed.
- It supports the local fixed-grid common-reference order/error statement.
- It does not close B4 or any source-policy execution rows; B2 closure, if used, must come from Route B claim demotion.
