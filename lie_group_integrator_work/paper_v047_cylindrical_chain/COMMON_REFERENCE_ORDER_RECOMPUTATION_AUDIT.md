# Common-Reference Order Recomputation Audit

Status: **raw-row arithmetic verified; external-superiority source-policy gate remains open**.

- Raw ok rows checked: `132`.
- Method/example cells recomputed: `44/44`.
- Order/finest-error mismatches against summary: `0`.
- Max order absolute difference: `7.105e-15`.
- Max finest-error absolute difference: `0.000e+00`.
- Anomaly rows flagged for interpretation/source-policy review: `30`.

## Local Recomputed Rows

| example | recomputed velocity order | summary velocity order | finest velocity error | status |
|---|---:|---:|---:|---|
| `double_pendulum` | `6.010` | `6.010` | `2.346e-13` | `match` |
| `four_link` | `6.085` | `6.085` | `1.093e-11` | `match` |
| `single_pendulum` | `5.801` | `5.801` | `1.155e-12` | `match` |
| `slider_crank` | `7.341` | `7.341` | `9.189e-12` | `match` |

## Mismatch Rows

| method | example | mismatches |
|---|---|---|
| `none` | `none` | `none` |

## Anomaly Counts

| flag | rows |
|---|---:|
| `acc_error_flat_at_floor` | `1` |
| `acc_error_not_monotone_decreasing_with_h` | `13` |
| `nonlocal_negative_velocity_order` | `3` |
| `nonlocal_velocity_order_floor_limited` | `2` |
| `pos_error_flat_at_floor` | `17` |
| `pos_error_not_monotone_decreasing_with_h` | `23` |
| `vel_error_flat_at_floor` | `1` |
| `vel_error_not_monotone_decreasing_with_h` | `5` |

## Boundary

- The audit independently recomputes every summary order from raw rows.
- The arithmetic check can confirm table integrity, but it cannot repair source-policy mismatches.
- External superiority remains disallowed until B2/B4 source-policy same-test baselines close.
