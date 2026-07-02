# TFE DAE Runner Contract Gap Audit

Status: **DAE runner contract gap open; not source policy**.

This audit is read-only over existing TFE artifacts and source text. It does not run a numerical campaign.

- Source-policy rows completed: `0`.
- Source spec candidate/source-policy boundary scaffold/use/DAE-equivalent/method-equivalent/rows: `True/diagnostic_scaffold_only_not_source_policy_reproduction/False/False/0`.
- Source spec Gauss6 candidate/source-policy DAE split available/use/runner/source rows/equivalent: `True/candidate_smoke_only_not_source_policy_dae_runner/False/0/False`.
- Source-policy DAE runner equivalent: `False`.
- Monolithic absolute-coordinate DAE time integrator: `False`.
- Pendulum DAE runner implemented: `False`.
- Bounded stepwise DAE runner rows/metric rows/step residual rows: `4/12/56`.
- Monolithic candidate DAE runner rows/metric rows/step residual rows/source rows/equivalent/monolithic: `4/12/56/0/False/False`.
- Source-policy absolute-coordinate DAE runner contract symbol/present/implemented: `True/True/False`.
- Source-policy absolute-coordinate DAE runner contract rows/metric rows/step residual rows/source rows/equivalent/monolithic: `4/12/56/0/False/False`.
- Source-method candidate contract rows/source rows/equivalent method/DAE: `5/0/False/False`.
- Source-policy method runner contract symbol/present/implemented: `True/True/False`.
- Source-policy method runner contract rows/source rows/equivalent method/DAE: `5/0/False/False`.
- Planar-lift rows/metric rows/source-policy rows: `12/36/0`.
- Runner-equivalence preflight closed/open/source rows: `25/6/0`.
- Gauss6/FullVA candidate smoke/source-policy runner/source-policy rows: `True/False/0`.
- Gauss6/FullVA DAE candidate contract rows/source rows/equivalent/FullVA-equivalent: `1/0/False/False`.
- Source-policy Gauss6/FullVA DAE runner contract symbol/present/implemented: `True/True/False`.
- Source-policy Gauss6/FullVA DAE runner contract rows/source rows/equivalent/FullVA-equivalent/monolithic: `1/0/False/False/False`.
- Full T=10 absolute DAE-lift metric/step/source rows/monolithic/equivalent: `12/2800/0/False/False`.
- Full T=10 grid exact/incompatible/full-policy-resolved: `2/4/False`.
- Missing contract blocks: `6`.
- Non-heavy missing contract blocks: `['brown_mcphee_source_code_equivalent_law_open', 'full_T10_source_grid_endpoint_policy_open']`.
- Non-heavy blocks dispositioned by demotion: `True`.
- Non-heavy demotion closes source-policy rows: `False`.
- Contract block accounting raw/non-heavy-terminal/effective-execution/source-rows: `6/2/4/0`.
- Effective source-policy execution contract blocks: `['pendulum_absolute_coordinate_source_policy_dae_runner_missing', 'tfe_newmark_trapezoidal_source_policy_method_runners_missing', 'gauss6_fullva_absolute_coordinate_source_policy_runner_missing', 'accepted_source_policy_work_precision_rows_not_executed_or_bound']`.
- Source-policy execution/integrator missing contract blocks: `['pendulum_absolute_coordinate_source_policy_dae_runner_missing', 'tfe_newmark_trapezoidal_source_policy_method_runners_missing', 'gauss6_fullva_absolute_coordinate_source_policy_runner_missing', 'accepted_source_policy_work_precision_rows_not_executed_or_bound']`.
- Source-policy execution/integrator missing block count: `4`.
- Candidate-backed non-equivalent runner blocks/count: `['pendulum_absolute_coordinate_source_policy_dae_runner_missing', 'tfe_newmark_trapezoidal_source_policy_method_runners_missing', 'gauss6_fullva_absolute_coordinate_source_policy_runner_missing']/3`.
- Ready to execute source policy now: `False`.
- Source-policy execution preflight schema/status/opt-in: `tfe-source-policy-execution-preflight-v1/terminal_no_public_code_self_reproduction_attempted_not_promoted/False`.
- Source-policy execution preflight nonheavy/execution/promote/ready: `True/4/False/False`.
- Source-policy execution preflight required runner contracts: `['monolithic_absolute_coordinate_DAE_time_integrator', 'TFE_m1_m2_m3_Newmark_beta_trapezoidal_source_policy_method_runners', 'Gauss6_FullVA_absolute_coordinate_source_policy_DAE_runner', 'accepted_T10_source_policy_work_precision_rows']`.

## Non-Heavy Blocker Evidence

- Brown--McPhee encoded/published/source-equivalent/transition-policy/close-now: `True/True/False/False/False`.
- Brown--McPhee source-code equivalence certificate status/available/positive/closed-block: `negative_source_code_equivalence_certificate_not_source_policy/True/False/False`.
- Brown--McPhee frictional source-policy demotion/allowed-use: `True/local_dissipativity_residual_sensitivity_diagnostic_only`.
- Algorithm-literal endpoint probe metric/overrun/source rows: `12/12/0`.
- Algorithm-literal work-precision rows/summary/figure/B4-progress/B4-closure: `12/4/True/True/False`.
- Endpoint boundary certificate proved/exact/overrun/source rows/full-policy/exact-T-equivalent: `True/2/4/0/False/False`.
- Full-T10 endpoint policy closure certificate status/available/positive/closed-block: `negative_full_T10_endpoint_policy_certificate_not_source_policy/True/False/False`.
- Endpoint-incompatible rows demoted from source-policy row set: `4`.
- Endpoint source-equivalent sampling/method-runner: `False/False`.

## Non-Heavy Demotion Disposition

- Brown--McPhee non-heavy disposition/rows-promoted/allowed-use: `demoted_not_promoted/0/local_dissipativity_residual_sensitivity_diagnostic_only`.
- Brown--McPhee demotion certificate/positive/closed-block/source rows: `negative_source_code_equivalence_certificate_not_source_policy/False/False/0`.
- Endpoint non-heavy disposition/rows-demoted/full-policy: `demoted_not_promoted/4/False/False`.
- Endpoint demotion exact/overrun rows/exact-T-equivalent/source rows: `2/4/False/0`.
- These demotions remove the non-heavy rows from source-policy promotion scope but do not close the TFE runner lane.

## Missing Contract Blocks

| id | first required artifact | non-heavy resolvable |
|---|---|---:|
| `brown_mcphee_source_code_equivalent_law_open` | `Brown--McPhee source-code-equivalent friction-law certificate` | `True` |
| `pendulum_absolute_coordinate_source_policy_dae_runner_missing` | `absolute-coordinate T=10 source-policy DAE runner equivalence certificate` | `False` |
| `tfe_newmark_trapezoidal_source_policy_method_runners_missing` | `TFE m=1/m=2/m=3, Newmark-beta, and trapezoidal source-policy method-runner certificate` | `False` |
| `gauss6_fullva_absolute_coordinate_source_policy_runner_missing` | `Gauss6/FullVA absolute-coordinate source-pendulum DAE runner certificate` | `False` |
| `full_T10_source_grid_endpoint_policy_open` | `full T=10 endpoint/output sampling policy for endpoint-incompatible h rows` | `True` |
| `accepted_source_policy_work_precision_rows_not_executed_or_bound` | `accepted source-policy work/precision row table binding error, order, runtime, and work metrics` | `False` |

## Decision

Current evidence proves a parameter model, source metrics, absolute-coordinate residual smokes, and a bounded stepwise residual runner. It does not prove a monolithic absolute-coordinate source-policy DAE time integrator, source-method equivalence, full T=10 endpoint policy, or accepted work/precision row binding.

No TFE source-policy rows are closed by this audit.
