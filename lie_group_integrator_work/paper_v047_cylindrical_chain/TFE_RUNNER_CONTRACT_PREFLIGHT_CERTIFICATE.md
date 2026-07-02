# TFE Runner Contract Preflight Certificate

Status: **contract_entrypoints_callable_candidate_backed_source_policy_open**.
Entry points callable/candidate-backed: `3/3` / `3/3`.
Candidate rows finite/residual gates: `True/True`.
Source-policy rows completed: `0`.
Source-policy equivalent DAE/method: `False/False`.
Execution blocks remaining: `4` / `['pendulum_absolute_coordinate_source_policy_dae_runner_missing', 'tfe_newmark_trapezoidal_source_policy_method_runners_missing', 'gauss6_fullva_absolute_coordinate_source_policy_runner_missing', 'accepted_source_policy_work_precision_rows_not_executed_or_bound']`.

| entrypoint | rows | metrics | candidate-backed | implemented | equivalent | accepted use |
|---|---:|---:|---:|---:|---:|---|
| `source_policy_absolute_coordinate_dae_runner` | `4` | `12` | `True` | `False` | `False` | contract_entrypoint_only_not_source_policy_reproduction |
| `source_policy_tfe_newmark_trapezoidal_method_runners` | `5` | `None` | `True` | `False` | `False` | method_runner_contract_entrypoint_only_not_source_policy |
| `source_policy_gauss6_fullva_absolute_coordinate_dae_runner` | `1` | `None` | `True` | `False` | `False` | gauss6_fullva_dae_runner_contract_entrypoint_only_not_source_policy |

| execution block | mapped entrypoint | candidate-backed | equivalent | rows completed | first required artifact |
|---|---|---:|---:|---:|---|
| `pendulum_absolute_coordinate_source_policy_dae_runner_missing` | `source_policy_absolute_coordinate_dae_runner` | `True` | `False` | `0` | absolute-coordinate T=10 source-policy DAE runner equivalence certificate |
| `tfe_newmark_trapezoidal_source_policy_method_runners_missing` | `source_policy_tfe_newmark_trapezoidal_method_runners` | `True` | `False` | `0` | TFE m=1/m=2/m=3, Newmark-beta, and trapezoidal source-policy method-runner certificate |
| `gauss6_fullva_absolute_coordinate_source_policy_runner_missing` | `source_policy_gauss6_fullva_absolute_coordinate_dae_runner` | `True` | `False` | `0` | Gauss6/FullVA absolute-coordinate source-pendulum DAE runner certificate |
| `accepted_source_policy_work_precision_rows_not_executed_or_bound` | `None` | `False` | `False` | `0` | accepted source-policy work/precision row table binding error, order, runtime, and work metrics |

Execution block closure summary: `3/4` candidate-backed, `0` source-policy equivalent, `0` rows completed, `0` closable without heavy/source-policy execution.

This certificate is a runner-contract preflight only. It does not close OC6,
does not run a source-policy campaign, and does not authorize external-superiority claims.
