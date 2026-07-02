# TFE Endpoint Policy Boundary Certificate

Status: **endpoint_policy_literal_overrun_bound_proved_source_policy_open**.

This certificate is a read-only proof over the extracted TFE source grid and endpoint diagnostics.

## Boundary

- Source-policy rows completed: `0`.
- Full T=10 source-grid policy resolved: `False`.
- Exact-T error-sampling equivalent: `False`.
- Method-runner equivalent: `False`.
- Algorithm-literal endpoint policy: `fixed_h_until_tn_ge_tfinal`.
- Exact-T / overrun source h rows: `2/4`.
- Endpoint-incompatible demoted rows: `4`.

## Theorem

For T>0 and h>0, the Algorithm-1-literal loop with fixed h and N=ceil(T/h) terminates at t_N=N h. If T/h is not an integer, then 0 < t_N - T < h; if T/h is an integer, then t_N=T.

Proof sketch:
- The loop performs N=ceil(T/h) fixed-size updates before the first index with t_N >= T.
- By the ceiling definition, N-1 < T/h <= N.
- Multiplying by h gives (N-1)h < T <= Nh.
- Thus t_N=Nh and t_N-T is nonnegative and strictly smaller than h.
- The residual is zero exactly when T/h is an integer; otherwise the terminal state is an overrun state rather than an exact-T state.

Conclusion: Endpoint-incompatible published h rows need a source-confirmed error/output sampling policy before any exact-T source-policy row or work/precision row can be accepted; otherwise they remain explicitly demoted from the source-policy row set.

## Source Text Support

- Source text available / anchors / fixed-h loop: `True/9/True`.
- Source endpoint convention resolved for error sampling: `False`.
- Demotion contract: Algorithm-literal overrun rows are diagnostic-only and excluded from source-policy promotion unless source-confirmed endpoint/output sampling for noninteger T/h is found.

## Diagnostic Work Precision Boundary

- Endpoint probe metric/overrun rows: `12/12`.
- Work-precision rows/summary/figure/B4-progress/B4-closure: `12/4/True/True/False`.

## Rows

| row | h | terminal time | overshoot | hits exact T | source-policy row |
|---|---:|---:|---:|---:|---:|
| `frictionless_pendulum:h=0.003` | `0.003` | `10.002` | `0.002` | `False` | `False` |
| `frictionless_pendulum:h=0.006` | `0.006` | `10.002` | `0.002` | `False` | `False` |
| `frictionless_pendulum:h=0.012` | `0.012` | `10.008` | `0.008` | `False` | `False` |
| `frictional_pendulum:h=0.003` | `0.003` | `10.002` | `0.002` | `False` | `False` |
| `frictional_pendulum:h=0.008` | `0.008` | `10` | `0` | `True` | `False` |
| `frictional_pendulum:h=0.2` | `0.2` | `10` | `0` | `True` | `False` |

No source-policy rows are closed by this certificate.
Endpoint-incompatible rows remain demoted from source-policy promotion until a source-confirmed endpoint/output sampling policy is available.
