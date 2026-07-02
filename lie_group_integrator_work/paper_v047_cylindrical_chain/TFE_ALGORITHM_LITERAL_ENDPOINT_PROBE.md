# TFE Algorithm-Literal Endpoint Probe

Status: **algorithm_literal_full_T10_probe_available_source_policy_open**.

- Source text fixed-h loop supported: `True`.
- Endpoint policy: `fixed_h_until_tn_ge_tfinal`.
- Methods / metric rows: `4/12`.
- Terminal overrun rows: `12`.
- Source-policy rows completed: `0`.
- Source-policy method runner equivalent: `False`.
- Exact-T error sampling equivalent: `False`.

## Method Summary

| method | expected order | max residual | coordinate orders | velocity orders |
|---|---:|---:|---|---|
| `tfe2026_Newmark_beta` | `2` | `9.866e-13` | `[1.9900314276660334, -0.04864320328776651]` | `[2.001363633838148, -0.048568634892856656]` |
| `tfe2026_TFE_m1` | `1` | `9.912e-13` | `[1.8892994669808798, 0.06220722531978961]` | `[1.7702660737075764, 0.20027997423914137]` |
| `tfe2026_TFE_m2` | `3` | `2.482e-09` | `[1.9895936949422648, 2.2968296835382e-06]` | `[2.0014643664203455, 6.796067120507969e-06]` |
| `tfe2026_trapezoidal` | `2` | `9.786e-13` | `[1.9899298345312957, -0.03717429946471455]` | `[2.0013776264704926, -0.0369860747217061]` |

## Remaining To Close Source Policy

- prove the source paper's reported error/order sampling uses the algorithm-literal terminal state or another explicit endpoint convention.
- replace the scalar planar candidate runners with the source-equivalent absolute-coordinate DAE runners or source-code reproduction.
- keep source_policy_rows_completed at zero until runner equivalence and sampling policy are both closed.
