# TFE Full-T10 Absolute DAE-Lift Summary

Status: **full T=10 absolute-coordinate DAE-lift candidate summarized; source-policy not closed**.

- Full T=10 absolute-coordinate lift completed: `True`.
- T/reference h/comparison h: `10.0` / `0.0001` / `[0.1, 0.05, 0.025]`.
- Source reference invoked: `True`.
- Source-policy rows completed: `0`.
- Monolithic source-policy DAE runner: `False`.
- Source-policy DAE/method equivalence: `False/False`.
- Methods/metric rows/step residual rows: `4/12/2800`.
- All step states finite: `True`.
- Max hinge position/velocity residuals: `0.000e+00/0.000e+00`.
- Max translational/axis rotational residuals: `5.684e-14/1.607e-13`.

## Rows

| method | target | velocity pair orders | coordinate pair orders | step residual rows | finest velocity error | max DAE residual |
|---|---:|---:|---:|---:|---:|---:|
| `tfe2026_Newmark_beta` | `2` | `1.991, 1.998` | `2.028, 2.007` | `700` | `4.642e-03` | `1.439e-13` |
| `tfe2026_TFE_m1` | `1` | `1.276, -0.077` | `2.623, 5.795` | `700` | `6.800e-03` | `1.607e-13` |
| `tfe2026_TFE_m2` | `3` | `2.929, 2.966` | `2.701, 2.871` | `700` | `2.349e-06` | `1.434e-13` |
| `tfe2026_trapezoidal` | `2` | `1.993, 1.998` | `2.021, 2.005` | `700` | `3.558e-03` | `1.313e-13` |

This artifact is claim-bounded. It strengthens full-horizon absolute-coordinate residual diagnostics, but it does not close original TFE source-policy reproduction.
