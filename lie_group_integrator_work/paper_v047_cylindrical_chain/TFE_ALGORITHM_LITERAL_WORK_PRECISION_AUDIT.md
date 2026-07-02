# TFE Algorithm-Literal Work/Precision Audit

Status: **algorithm_literal_T10_newton_work_precision_available_source_policy_open**.

- Work proxy: `total_newton_iterations`.
- Runtime proxy available: `False`.
- Methods/raw rows/summary rows: `4/12/4`.
- Terminal-overrun rows: `12`.
- Figure available: `True`.
- Source-policy rows completed: `0`.
- Source-policy method runner equivalent: `False`.
- Exact-T error sampling equivalent: `False`.
- External superiority claim allowed: `False`.

## Method Summary

| method | expected | rows | terminal overruns | velocity order | finest velocity error | Newton iterations | max residual |
|---|---:|---:|---:|---:|---:|---:|---:|
| `tfe2026_Newmark_beta` | `2` | `3` | `3` | `0.976397` | `6.065256e-03` | `6037` | `9.866e-13` |
| `tfe2026_TFE_m1` | `1` | `3` | `3` | `0.985273` | `7.326284e-03` | `10572` | `9.912e-13` |
| `tfe2026_TFE_m2` | `3` | `3` | `3` | `1.00074` | `6.132192e-03` | `11313` | `2.482e-09` |
| `tfe2026_trapezoidal` | `2` | `3` | `3` | `0.982196` | `6.080882e-03` | `6042` | `9.786e-13` |

This is a Newton-iteration work/precision diagnostic for the source-text-supported
fixed-h Algorithm 1 endpoint policy. It is not a source-policy reproduction and
does not close B4 because exact-T error sampling and source-equivalent DAE/method
runner policy remain open.
