# TFE Full-T10 Coarse Candidate Summary

Status: **full T=10 coarse candidate probe summarized; source-policy not closed**.

- Full T=10 candidate probe completed: `True`.
- T/reference h/comparison h: `10.0` / `0.0125` / `[0.1, 0.05, 0.025]`.
- Source-policy reference h/invoked: `0.0001` / `False`.
- Source-policy rows completed: `0`.
- Finite/residual-ok rows: `4/4`.
- Coordinate/velocity error-decrease rows: `4/4`.
- External superiority claim allowed: `False`.
- Default 1e-4 campaign invoked: `False`.

## Rows

| method | target | velocity pair orders | coordinate pair orders | finest velocity error | finest coordinate error | max residual |
|---|---:|---:|---:|---:|---:|---:|
| `tfe2026_Newmark_beta` | `2` | `1.991, 1.998` | `2.028, 2.007` | `4.642e-03` | `1.956e-03` | `9.965e-13` |
| `tfe2026_TFE_m1` | `1` | `1.276, -0.077` | `2.623, 5.795` | `6.801e-03` | `5.226e-05` | `9.086e-13` |
| `tfe2026_TFE_m2` | `3` | `2.927, 2.952` | `2.694, 2.824` | `2.375e-06` | `3.346e-07` | `3.346e-11` |
| `tfe2026_trapezoidal` | `2` | `1.993, 1.998` | `2.021, 2.005` | `3.558e-03` | `1.504e-03` | `9.775e-13` |

This artifact is intentionally claim-bounded: it confirms non-heavy full-horizon candidate behavior, but does not close original TFE source-policy reproduction.
