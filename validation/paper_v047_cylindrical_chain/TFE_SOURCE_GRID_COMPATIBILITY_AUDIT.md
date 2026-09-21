# TFE Source Grid Compatibility Audit

Status: **source horizon step-grid policy open**.

- Source-policy rows completed: `0`.
- Rows checked: `6`.
- Integer-step compatible rows: `2`.
- Integer-step incompatible rows: `4`.
- Exact-T compatible rows with endpoint-grid convention resolved: `2`.
- Endpoint-incompatible rows requiring source endpoint policy: `4`.
- Endpoint-incompatible rows demoted from source-policy row set: `4`.
- Exact-T compatible subset grid policy resolved: `True`.
- Full T=10 grid policy resolved: `False`.
- External superiority claim allowed: `False`.
- Endpoint row dispositions recorded: `6`.
- Endpoint-compatible future-execution candidates: `2`.
- Endpoint-incompatible blocked rows: `4`.
- Endpoint-incompatible demoted rows: `4`.

## Endpoint-Grid Subclosure

Only rows whose published h divides T=10 exactly are endpoint-grid resolved. Rows whose published h does not divide T=10 remain demoted from source-policy promotion until the source endpoint/output sampling convention is established; no source-policy reproduction row is closed by this audit.

- Compatible row IDs: `['frictional_pendulum:h=0.008', 'frictional_pendulum:h=0.2']`.
- Incompatible row IDs: `['frictionless_pendulum:h=0.003', 'frictionless_pendulum:h=0.006', 'frictionless_pendulum:h=0.012', 'frictional_pendulum:h=0.003']`.
- Demoted incompatible row IDs: `['frictionless_pendulum:h=0.003', 'frictionless_pendulum:h=0.006', 'frictionless_pendulum:h=0.012', 'frictional_pendulum:h=0.003']`.

## Rows

| row id | case | friction | h | T/h | nearest steps | nearest T | mismatch | compatible |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `frictionless_pendulum:h=0.003` | `frictionless_pendulum` | `False` | `0.003` | `3333.33333333` | `3333` | `9.999` | `1.000e-03` | `False` |
| `frictionless_pendulum:h=0.006` | `frictionless_pendulum` | `False` | `0.006` | `1666.66666667` | `1667` | `10.002` | `2.000e-03` | `False` |
| `frictionless_pendulum:h=0.012` | `frictionless_pendulum` | `False` | `0.012` | `833.333333333` | `833` | `9.996` | `4.000e-03` | `False` |
| `frictional_pendulum:h=0.003` | `frictional_pendulum` | `True` | `0.003` | `3333.33333333` | `3333` | `9.999` | `1.000e-03` | `False` |
| `frictional_pendulum:h=0.008` | `frictional_pendulum` | `True` | `0.008` | `1250` | `1250` | `10` | `0.000e+00` | `True` |
| `frictional_pendulum:h=0.2` | `frictional_pendulum` | `True` | `0.2` | `50` | `50` | `10` | `0.000e+00` | `True` |

## Row-Level Promotion Disposition

| row id | endpoint disposition | source-policy eligible now | required before promotion |
|---|---|---:|---|
| `frictionless_pendulum:h=0.003` | `blocked_by_endpoint_sampling_policy` | `False` | source-confirmed endpoint/output sampling convention for noninteger T/h; source-equivalent absolute-coordinate DAE runner; source-equivalent method runner for the selected TFE/Newmark/trapezoidal method; accepted error/order/runtime/work metric binding |
| `frictionless_pendulum:h=0.006` | `blocked_by_endpoint_sampling_policy` | `False` | source-confirmed endpoint/output sampling convention for noninteger T/h; source-equivalent absolute-coordinate DAE runner; source-equivalent method runner for the selected TFE/Newmark/trapezoidal method; accepted error/order/runtime/work metric binding |
| `frictionless_pendulum:h=0.012` | `blocked_by_endpoint_sampling_policy` | `False` | source-confirmed endpoint/output sampling convention for noninteger T/h; source-equivalent absolute-coordinate DAE runner; source-equivalent method runner for the selected TFE/Newmark/trapezoidal method; accepted error/order/runtime/work metric binding |
| `frictional_pendulum:h=0.003` | `blocked_by_endpoint_sampling_policy` | `False` | source-confirmed endpoint/output sampling convention for noninteger T/h; source-equivalent absolute-coordinate DAE runner; source-equivalent method runner for the selected TFE/Newmark/trapezoidal method; accepted error/order/runtime/work metric binding |
| `frictional_pendulum:h=0.008` | `endpoint_grid_resolved_pending_runner_contracts` | `False` | source-equivalent absolute-coordinate DAE runner; source-equivalent method runner for the selected TFE/Newmark/trapezoidal method; source-code-equivalent Brown--McPhee friction law if the row is frictional; accepted error/order/runtime/work metric binding |
| `frictional_pendulum:h=0.2` | `endpoint_grid_resolved_pending_runner_contracts` | `False` | source-equivalent absolute-coordinate DAE runner; source-equivalent method runner for the selected TFE/Newmark/trapezoidal method; source-code-equivalent Brown--McPhee friction law if the row is frictional; accepted error/order/runtime/work metric binding |

## Endpoint Policy Acceptance Contract

- Exact-T compatible subset can enter future execution after runner contracts: `True`.
- Exact-T compatible row IDs: `['frictional_pendulum:h=0.008', 'frictional_pendulum:h=0.2']`.
- Endpoint-incompatible blocked row IDs: `['frictionless_pendulum:h=0.003', 'frictionless_pendulum:h=0.006', 'frictionless_pendulum:h=0.012', 'frictional_pendulum:h=0.003']`.
- Endpoint-incompatible demoted row IDs: `['frictionless_pendulum:h=0.003', 'frictionless_pendulum:h=0.006', 'frictionless_pendulum:h=0.012', 'frictional_pendulum:h=0.003']`.
- Demotion contract: Endpoint-incompatible published h rows are diagnostic-only and excluded from the source-policy row set unless source text, source code, or a source-equivalent runner establishes the error/output sampling convention for noninteger T/h.
- Full T=10 source-policy promotion requires:
  - all published h rows use a source-confirmed endpoint/output sampling convention.
  - Algorithm-1-literal overrun rows are accepted only if source output/error sampling is confirmed at the overrun state.
  - adjusted-h, interpolation, floor/nearest, or partial-step conventions require source text, source code, or explicit demotion.
  - method-runner, DAE-runner, friction-law, and work-metric contracts close before any B4/B7 promotion.

- Forbidden without contract:
  - promote endpoint-incompatible rows from diagnostic algorithm-literal probes.
  - claim exact-T source-policy errors for h rows that overrun T=10.
  - use compatible endpoint-grid rows as source-policy rows before runner equivalence is closed.

The extracted source-policy horizon is T=10. Two published frictional h values divide T exactly and are endpoint-grid resolved under the source text's fixed-h loop convention, but several other published h values do not divide T exactly. Those endpoint-incompatible rows are explicitly demoted from source-policy promotion until the source paper or source code establishes the endpoint/output sampling convention.

## Source-Text Endpoint Convention Audit

- Source text available/anchors: `True/9`.
- Algorithm-literal fixed-h loop detected: `True`.
- Endpoint convention resolved for error sampling: `False`.
- Adjusted-h/partial-final-step/interpolation/floor-nearest confirmation: `False/False/False/False`.

| line | finding |
|---:|---|
| `830` | Algorithm 1 takes a target final time but does not describe a last-step adjustment. |
| `835` | Algorithm 1 uses a strict less-than final-time loop condition. |
| `857` | Algorithm 1 advances by the fixed step size h. |
| `1065` | The frictionless comparison uses published h values that do not divide T=10 exactly. |
| `1274` | The source reference step size is stated, but the endpoint convention is not. |
| `1123` | The error discussion reports values at a 10 s final time. |
| `1148` | The frictional comparison mixes one incompatible and one compatible h value. |
| `1167` | The large-step frictional comparison uses a compatible h value. |
| `1175` | Figure captions repeatedly frame the run as a 10 s simulation. |

### Algorithm-Literal Terminal Times

| case | h | steps | terminal time | overshoot | exact T |
|---|---:|---:|---:|---:|---:|
| `frictionless_pendulum` | `0.003` | `3334` | `10.002` | `2.000e-03` | `False` |
| `frictionless_pendulum` | `0.006` | `1667` | `10.002` | `2.000e-03` | `False` |
| `frictionless_pendulum` | `0.012` | `834` | `10.008` | `8.000e-03` | `False` |
| `frictional_pendulum` | `0.003` | `3334` | `10.002` | `2.000e-03` | `False` |
| `frictional_pendulum` | `0.008` | `1250` | `10` | `0.000e+00` | `True` |
| `frictional_pendulum` | `0.2` | `50` | `10` | `0.000e+00` | `True` |

## Endpoint Convention Candidates

| policy | keeps published h | keeps exact T | source-equivalent now | accepted use |
|---|---:|---:|---:|---|
| `nearest_integer_horizon` | `True` | `False` | `False` | diagnostic_only_until_source_endpoint_convention_is_verified |
| `algorithm_literal_fixed_h_until_tn_ge_tfinal` | `True` | `False` | `False` | diagnostic_only_because_the_text_does_not_state_error_sampling_at_noninteger_T_overruns |
| `adjust_h_to_hit_T_exactly` | `False` | `True` | `False` | diagnostic_only_because_published_h_is_changed |
| `integer_steps_plus_final_partial_step` | `True` | `True` | `False` | diagnostic_only_unless_source_code_or_paper_confirms_partial_final_step |

## Required To Accept Full T=10 Rows

- verify the source paper/source code endpoint convention for h values that do not divide T=10.
- identify whether Algorithm 1's fixed-h loop uses overrun, interpolation, adjusted h, or a final partial step for reported errors.
- record whether the accepted convention keeps published h, exact T, or both.
- keep endpoint-incompatible rows demoted from the source-policy row set unless that convention is source-confirmed.
- rerun the TFE m=1/m=2/Newmark/trapezoidal rows with the verified convention.
- keep source_policy_rows_completed at zero until the convention and method runner are source-equivalent.
