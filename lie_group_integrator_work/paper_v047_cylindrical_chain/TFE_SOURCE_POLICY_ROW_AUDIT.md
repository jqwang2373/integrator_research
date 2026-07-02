# TFE Source-Policy Row Audit

Status: **source policy spec extracted; runner rows not closed**.

This audit is read-only over existing paper-package artifacts. It does not implement or run the TFE pendulum.

- Active B2 flagged TFE rows: `0`.
- Source-policy spec extracted: `True`.
- Source pendulum parameter model implemented: `True`.
- Frictionless planar RHS smoke implemented: `True`.
- Absolute-coordinate DAE residual smoke implemented: `True`.
- Absolute-coordinate frictional candidate DAE smoke implemented: `True`.
- Absolute-coordinate planar-lift trajectory probe implemented: `True`.
- Absolute-coordinate planar-lift rows/metric rows/source-policy rows: `12/36/0`.
- Absolute-coordinate planar-lift equivalent DAE runner: `False`.
- Bounded absolute-coordinate DAE trajectory runner implemented: `True`.
- Bounded absolute-coordinate DAE trajectory runner rows/metric rows/step residual rows: `4/12/56`.
- Bounded absolute-coordinate DAE trajectory runner source-policy rows/equivalent DAE/monolithic integrator: `0/False/False`.
- Monolithic absolute-coordinate DAE candidate runner implemented: `True`.
- Monolithic absolute-coordinate DAE candidate runner rows/metric rows/step residual rows: `4/12/56`.
- Monolithic absolute-coordinate DAE candidate runner source-policy rows/equivalent DAE/monolithic integrator: `0/False/False`.
- Source-output time-integration smoke implemented: `True`.
- Source-policy time-integration runner equivalent: `False`.
- Source reference solution policy smoke implemented: `True`.
- Source reference solution policy full T=10 run: `False`.
- Source reference solution policy full T=10 probe completed/source rows: `True/0`.
- Source reference solution policy full T=10 probe steps/check error: `100000/200000` / `3.819e-14/2.485e-13`.
- T=10 source grid policy resolved/compatible/incompatible rows: `False/2/4`.
- Exact-T compatible endpoint-grid rows resolved/requiring policy: `2/4`.
- Exact-T compatible subset grid policy resolved: `True`.
- Source comparator candidate runners implemented: `True`.
- Newmark-beta candidate runner smoke implemented: `True`.
- Trapezoidal candidate runner smoke implemented: `True`.
- Source-policy method runner equivalent: `False`.
- TFE m=1/2/3 candidate runner smoke implemented: `True`.
- Source-method candidate runner contract rows/source-policy rows/equivalent method: `5/0/False`.
- Source-method candidate runner contract finite/residual-below-1e-8: `True/True`.
- TFE Appendix-B coefficient certificate checked: `True`.
- TFE Appendix-B coefficient certificate rows/max diff: `3/0.000e+00`.
- TFE m=1/2/3 source-policy runners implemented: `False`.
- Bounded source-policy runner API implemented: `True`.
- Bounded source-policy runner smoke implemented: `True`.
- Bounded source-policy runner unified dispatch: `True`.
- Bounded source-policy runner rows/full T=10/source-policy rows: `4/False/0`.
- Bounded source-policy runner method equivalent: `False`.
- Bounded source-policy runner accepted use: `bounded_candidate_runner_api_only_not_source_policy`.
- Bounded source-policy runner DAE-equivalent/monolithic: `False/False`.
- Active TFE B2 candidate row smoke implemented: `True`.
- Active TFE B2 candidate row smoke full T=10: `False`.
- Active TFE B2 source-policy rows completed: `0`.
- Active TFE B2 full T=10 coarse candidate probe implemented: `True`.
- Active TFE B2 full T=10 coarse candidate probe full T=10/source-policy rows: `True/0`.
- Active TFE B2 full T=10 coarse candidate probe finite/residual-ok rows: `4/4`.
- Active TFE B2 full T=10 coarse candidate probe source reference invoked: `False`.
- Active TFE B2 source-reference full T=10 candidate probe implemented: `True`.
- Active TFE B2 source-reference full T=10 candidate probe full T=10/reference invoked/source-policy rows: `True/True/0`.
- Active TFE B2 source-reference full T=10 candidate probe finite/residual-ok rows: `4/4`.
- TFE m=3 full T=10 coarse formula probe implemented: `True`.
- TFE m=3 full T=10 coarse formula probe full T=10/source-policy rows: `True/0`.
- TFE m=3 full T=10 coarse formula probe finite/residual-ok rows: `1/1`.
- TFE m=3 full T=10 coarse formula probe expected order: `5`.
- TFE m=3 full T=10 coarse formula probe source reference invoked: `False`.
- Algorithm-literal endpoint probe status: `algorithm_literal_full_T10_probe_available_source_policy_open`.
- Algorithm-literal endpoint probe methods/metric rows/terminal overruns: `4/12/12`.
- Algorithm-literal endpoint probe source-policy rows/exact-T sampling equivalent: `0/False`.
- Source-policy DAE runner equivalent: `False`.
- Source output/error policy encoded: `True`.
- Brown--McPhee candidate friction law encoded: `True`.
- Brown--McPhee source text anchors found/model/mu: `True/True/True`.
- Brown--McPhee published formula structure encoded: `True`.
- Brown--McPhee source-code-equivalent law: `False`.
- Brown--McPhee transition velocity resolved from source: `False`.
- Frictional candidate RHS smoke implemented: `True`.
- Pendulum DAE runner implemented: `False`.
- Brown--McPhee friction/source-code equivalent implemented: `False`.
- TFE m=1/m=2/m=3 runner implemented: `False`.
- Newmark/trapezoidal runner implemented: `False`.
- Gauss6/FullVA absolute-coordinate source-policy runner implemented: `False`.
- Gauss6/FullVA legacy source-policy runner field: `False`.
- Gauss6/FullVA source pendulum candidate smoke implemented: `True`.
- Gauss6/FullVA source pendulum candidate rows/source-policy rows: `2/0`.
- Gauss6/FullVA source pendulum candidate method equivalent: `False`.
- Gauss6/FullVA DAE candidate contract rows/source-policy rows/equivalent DAE/FullVA: `1/0/False/False`.
- Gauss6/FullVA DAE candidate contract finite/residual-below-1e-8: `True/True`.
- Source-policy rows completed: `0`.
- Source-policy runner-equivalence preflight: `preflight_ready_runner_equivalence_open`.
- Source-policy runner-equivalence preflight closed/open/source rows: `25/6/0`.
- Source-policy runner-equivalence preflight can close lane: `False`.
- Runner-equivalence gap matrix open blockers: `6`.
- Runner-equivalence first required artifact: `source-equivalent DAE runner certificate for the original TFE pendulum policy`.
- Candidate/source-policy boundary scaffold/use/DAE-equivalent/method-equivalent/rows: `True/diagnostic_scaffold_only_not_source_policy_reproduction/False/False/0`.
- Source-policy reproduction rows: `0/4`.
- External-superiority-ready rows: `0`.
- External superiority claim allowed: `False`.
- Default 1e-4/heavy/run_v047: `False/False/False`.

## Closure Decision

Can close TFE B2 requirement now: `False`.

The original TFE pendulum source parameters and reference policy are extracted, and the source pendulum parameter model now has runnable frictionless, planar metric, absolute-coordinate residual, bounded source-output trajectory, bounded h=1e-4 reference-policy, full T=10 frictionless h=1e-4 source-reference probe, candidate Newmark/trapezoidal, candidate TFE m=1/2/3, Appendix-B coefficient certificate, unified bounded source-policy runner, active-B2 bounded candidate-row, full T=10 coarse candidate probe, TFE m=3 full-T10 formula-probe, and Gauss6/FullVA source-pendulum candidate-smoke layers. The Brown--McPhee source-text anchors and candidate published-formula structure are now recorded, but source-policy method-runner equivalence, Brown--McPhee friction/source-code equivalence, the four non-exact-T step-grid endpoint convention rows, absolute-coordinate FullVA DAE source-policy execution, and exact TFE source-policy rows are not implemented. The four active TFE rows remain diagnostic common-reference rows, not source-policy reproduction.

## Source-Policy Runner Equivalence Preflight

- Status: `preflight_ready_runner_equivalence_open`.
- Closed preconditions/open blockers: `25/6`.
- Source-policy rows closed by preflight: `0`.
- Can close TFE lane from preflight: `False`.

| closed precondition | satisfied | evidence |
|---|---:|---|
| `source_policy_spec_extracted` | `True` | `TFE_SOURCE_POLICY_SPEC.json` |
| `source_pendulum_parameter_model_implemented` | `True` | `../v048_cross_paper_same_test_benchmarks/tfe_source_pendulum_model.py` |
| `source_output_error_policy_encoded` | `True` | `source_output_policy/source_metric_smoke` |
| `absolute_coordinate_dae_residual_smoke_implemented` | `True` | `absolute_coordinate_dae_residual_smoke` |
| `absolute_coordinate_planar_lift_trajectory_probe_implemented` | `True` | `absolute_coordinate_planar_lift_trajectory_probe` |
| `bounded_absolute_coordinate_dae_trajectory_runner_implemented` | `True` | `bounded_absolute_coordinate_dae_trajectory_runner_smoke` |
| `monolithic_absolute_coordinate_dae_candidate_runner_implemented` | `True` | `monolithic_absolute_coordinate_dae_candidate_runner_smoke` |
| `source_policy_absolute_coordinate_dae_runner_contract_present` | `True` | `source_policy_absolute_coordinate_dae_runner` |
| `dae_trajectory_bridge_contract_implemented` | `True` | `dae_trajectory_bridge_contract_smoke` |
| `candidate_frictional_dae_trajectory_contract_implemented` | `True` | `candidate_frictional_dae_trajectory_contract_smoke` |
| `source_reference_full_T10_h1e4_probe_completed` | `True` | `source_reference_solution_policy_full_T10_probe` |
| `newmark_trapezoidal_candidate_runner_smoke_implemented` | `True` | `source_comparator_candidate_runner_smoke` |
| `tfe_m1_m2_m3_candidate_runner_smoke_implemented` | `True` | `source_tfe_candidate_runner_smoke` |
| `source_method_candidate_runner_contract_implemented` | `True` | `source_method_candidate_runner_contract_smoke` |
| `source_policy_tfe_newmark_trapezoidal_method_runner_contract_present` | `True` | `source_policy_tfe_newmark_trapezoidal_method_runners` |
| `tfe_appendix_b_coefficient_certificate_checked` | `True` | `tfe_appendix_b_coefficient_certificate` |
| `bounded_source_policy_runner_api_implemented` | `True` | `bounded_source_policy_runner_smoke` |
| `active_tfe_b2_full_T10_coarse_candidate_probe_implemented` | `True` | `active_tfe_b2_full_T10_coarse_candidate_probe` |
| `active_tfe_b2_source_reference_full_T10_candidate_probe_implemented` | `True` | `active_tfe_b2_source_reference_full_T10_candidate_probe` |
| `tfe_m3_full_T10_coarse_formula_probe_implemented` | `True` | `tfe_m3_full_T10_coarse_formula_probe` |
| `gauss6_source_pendulum_candidate_smoke_implemented` | `True` | `gauss6_fullva_source_pendulum_candidate_smoke` |
| `gauss6_fullva_dae_candidate_contract_implemented` | `True` | `source_gauss6_fullva_dae_candidate_contract_smoke` |
| `source_policy_gauss6_fullva_absolute_coordinate_dae_runner_contract_present` | `True` | `source_policy_gauss6_fullva_absolute_coordinate_dae_runner` |
| `same_test_candidate_work_precision_available` | `True` | `source_pendulum_same_test_work_precision_smoke` |
| `exact_T_compatible_grid_subset_policy_resolved` | `True` | `TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.json` |

| open blocker | status | reason |
|---|---|---|
| `brown_mcphee_source_code_equivalent_law_open` | `open` | published formula structure is encoded, but transition velocity and source-code coupling policy remain unresolved |
| `pendulum_absolute_coordinate_source_policy_dae_runner_missing` | `open` | a named contract entrypoint now binds the monolithic candidate rows, but it is not source-code-equivalent, not a monolithic source-policy DAE time integrator, and closes zero source-policy rows |
| `tfe_newmark_trapezoidal_source_policy_method_runners_missing` | `open` | a named method-runner contract entrypoint now binds candidate dispatch rows, but TFE m=1/2/3, Newmark-beta, and trapezoidal source-policy runners remain non-equivalent and close zero source-policy rows |
| `gauss6_fullva_absolute_coordinate_source_policy_runner_missing` | `open` | a named Gauss6/FullVA absolute-coordinate DAE contract entrypoint now binds the candidate lift, but it is not a monolithic FullVA source-policy DAE runner and closes zero source-policy rows |
| `full_T10_source_grid_endpoint_policy_open` | `open` | full T=10 source grid policy remains open for endpoint-incompatible h values |
| `accepted_source_policy_work_precision_rows_not_executed_or_bound` | `open` | no accepted source-policy row table binds error/order, runtime, and work metrics for B4/B7 |

## Runner-Equivalence Gap Matrix

First required artifact: `source-equivalent DAE runner certificate for the original TFE pendulum policy`.
Ready to execute source-policy rows now: `False`.

| open blocker | first required artifact | blocking scope | source fields |
|---|---|---|---|
| `brown_mcphee_source_code_equivalent_law_open` | Brown--McPhee source-code-equivalent friction-law certificate | frictional original-TFE source-policy rows and any source-code-equivalent frictional comparison | `brown_mcphee_published_formula_structure_encoded=True; brown_mcphee_source_code_equivalent_law=False; brown_mcphee_transition_velocity_policy_resolved_from_source=False` |
| `pendulum_absolute_coordinate_source_policy_dae_runner_missing` | absolute-coordinate T=10 source-policy DAE runner equivalence certificate | all original-TFE source-policy rows because candidate smokes are not full DAE source-policy executions | `absolute_coordinate_dae_residual_smoke_implemented=True; absolute_coordinate_planar_lift_trajectory_probe_implemented=True; bounded_absolute_coordinate_dae_trajectory_runner_implemented=True; pendulum_dae_runner_implemented=False; source_policy_dae_runner_equivalent=False` |
| `tfe_newmark_trapezoidal_source_policy_method_runners_missing` | TFE m=1/m=2/m=3, Newmark-beta, and trapezoidal source-policy method-runner certificate | method-side source-policy reproduction rows for the original TFE pendulum suite | `newmark_beta_candidate_runner_smoke_implemented=True; trapezoidal_candidate_runner_smoke_implemented=True; tfe_m1_m2_m3_candidate_runner_smoke_implemented=True; tfe_m1_m2_m3_source_policy_runners_implemented=False` |
| `gauss6_fullva_absolute_coordinate_source_policy_runner_missing` | Gauss6/FullVA absolute-coordinate source-pendulum DAE runner certificate | local method source-policy comparator rows under the original TFE pendulum policy | `gauss6_fullva_source_pendulum_candidate_smoke_implemented=True; gauss6_fullva_source_pendulum_candidate_method_equivalent=False; gauss6_fullva_absolute_coordinate_source_policy_runner_implemented=False` |
| `full_T10_source_grid_endpoint_policy_open` | full T=10 endpoint/output sampling policy for endpoint-incompatible h rows | four non-exact-T h rows that cannot be promoted to source-policy work/precision evidence | `source_grid_policy_resolved_for_exact_T_compatible_rows=True; source_grid_policy_resolved_for_full_T10=False; endpoint_incompatible_rows=4` |
| `accepted_source_policy_work_precision_rows_not_executed_or_bound` | accepted source-policy work/precision row table binding error, order, runtime, and work metrics | B4/B7 clean source-policy work/precision figures and external-superiority readiness | `source_policy_rows_closed_by_preflight=0; candidate_work_precision_rows=18; b4_b7_can_close_from_preflight=False` |

## Active Rows

| # | example | method | source method | expected order | bounded runner vel orders | full T10 coarse vel orders | active finest vel error | source-policy |
|---:|---|---|---|---:|---:|---:|---:|---:|

The TFE rows remain diagnostic common-reference rows, not source-policy external-superiority evidence.
