# TFE Source Pendulum Model Audit

Status: **source parameter model implemented; runner policy open**.

- Parameter match with source-policy spec: `True`.
- Source pendulum parameter model implemented: `True`.
- Frictionless planar RHS smoke implemented: `True`.
- Absolute-coordinate DAE residual smoke implemented: `True`.
- Absolute-coordinate frictional candidate DAE smoke implemented: `True`.
- Source-output time-integration smoke implemented: `True`.
- Source-policy time-integration runner equivalent: `False`.
- Source reference solution policy smoke implemented: `True`.
- Source reference solution policy full T=10 run: `False`.
- Source reference solution policy full T=10 probe implemented: `True`.
- Source reference solution policy full T=10 probe completed/source rows: `True/0`.
- Source comparator candidate runners implemented: `True`.
- Newmark-beta candidate runner smoke implemented: `True`.
- Trapezoidal candidate runner smoke implemented: `True`.
- Source-policy method runner equivalent: `False`.
- TFE m=1/2/3 candidate runner smoke implemented: `True`.
- Source-method candidate runner contract rows/source-policy rows/equivalent method: `5/0/False`.
- Source-method candidate runner contract finite/residual-below-1e-8: `True/True`.
- Source-policy method runner contract present/implemented: `True/False`.
- Source-policy method runner contract rows/source rows/equivalent method/DAE: `5/0/False/False`.
- TFE Appendix-B coefficient certificate checked: `True`.
- TFE Appendix-B coefficient certificate rows/max diff: `3/0.000e+00`.
- TFE m=1/2/3 source-policy runners implemented: `False`.
- Gauss6/FullVA source-pendulum candidate smoke implemented: `True`.
- Gauss6/FullVA absolute-coordinate source-policy runner implemented: `False`.
- Gauss6/FullVA source-pendulum legacy candidate alias implemented: `True`.
- Gauss6/FullVA source-pendulum candidate rows/source-policy rows: `2/0`.
- Gauss6/FullVA source-pendulum candidate method equivalent: `False`.
- Gauss6/FullVA DAE candidate contract rows/source-policy rows/equivalent DAE/FullVA: `1/0/False/False`.
- Gauss6/FullVA DAE candidate contract finite/residual-below-1e-8: `True/True`.
- Source-policy Gauss6/FullVA absolute-coordinate DAE runner contract present/implemented: `True/False`.
- Source-policy Gauss6/FullVA absolute-coordinate DAE runner contract rows/source rows/equivalent DAE/FullVA/monolithic: `1/0/False/False/False`.
- Source-pendulum same-test work/precision implemented: `True`.
- Source-pendulum same-test work/precision methods/method rows/metric rows: `6/6/18`.
- Source-pendulum same-test work/precision source-policy rows/external superiority allowed: `0/False`.
- Source-pendulum same-test work/precision Gauss6/TFE m=3 velocity order floors: `6.018` / `5.189`.
- Absolute-coordinate planar-lift trajectory probe implemented: `True`.
- Absolute-coordinate planar-lift methods/rows/metric rows: `6/12/36`.
- Absolute-coordinate planar-lift source-policy rows/equivalent DAE runner: `0/False`.
- Bounded absolute-coordinate DAE trajectory runner implemented: `True`.
- Bounded absolute-coordinate DAE trajectory runner rows/metric rows/step residual rows: `4/12/56`.
- Bounded absolute-coordinate DAE trajectory runner source-policy rows/equivalent DAE/monolithic integrator: `0/False/False`.
- Monolithic absolute-coordinate DAE candidate runner implemented: `True`.
- Monolithic absolute-coordinate DAE candidate runner rows/metric rows/step residual rows: `4/12/56`.
- Monolithic absolute-coordinate DAE candidate runner source-policy rows/equivalent DAE/monolithic integrator: `0/False/False`.
- Source-policy absolute-coordinate DAE runner contract present/implemented: `True/False`.
- Source-policy absolute-coordinate DAE runner contract rows/metric rows/step residual rows/source rows/equivalent/monolithic: `4/12/56/0/False/False`.
- DAE trajectory bridge contract implemented: `True`.
- DAE trajectory bridge contract rows/matched/source rows: `12/12/0`.
- DAE trajectory bridge contract all finite/all DAE residuals below 1e-10: `True/True`.
- DAE trajectory bridge contract equivalent DAE/monolithic integrator: `False/False`.
- Candidate-friction DAE trajectory contract implemented: `True`.
- Candidate-friction DAE trajectory contract rows/step residual rows/source rows: `12/56/0`.
- Candidate-friction DAE trajectory contract finite/residual-below-1e-9/friction-power-nonpositive: `True/True/True`.
- Candidate-friction DAE trajectory contract equivalent DAE/method/source-law/monolithic: `False/False/False/False`.
- Bounded source-policy runner API implemented: `True`.
- Bounded source-policy runner smoke implemented: `True`.
- Bounded source-policy runner unified dispatch: `True`.
- Bounded source-policy runner rows/full T=10/source-policy rows: `4/False/0`.
- Bounded source-policy runner method equivalent: `False`.
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
- Active TFE B2 source-reference full T=10 candidate probe method/DAE equivalent: `False/False`.
- TFE m=3 full T=10 coarse formula probe implemented: `True`.
- TFE m=3 full T=10 coarse formula probe full T=10/source-policy rows: `True/0`.
- TFE m=3 full T=10 coarse formula probe finite/residual-ok rows: `1/1`.
- TFE m=3 full T=10 coarse formula probe expected order: `5`.
- TFE m=3 full T=10 coarse formula probe source reference invoked: `False`.
- Source-policy DAE runner equivalent: `False`.
- Source output/error policy encoded: `True`.
- Brown--McPhee candidate friction law encoded: `True`.
- Brown--McPhee source-text anchor found: `True`.
- Brown--McPhee source text names velocity-based continuous model: `True`.
- Brown--McPhee source text reports mu_s/mu_d: `True`.
- Brown--McPhee published-formula structure encoded: `True`.
- Brown--McPhee source-code-equivalent law: `False`.
- Frictional candidate RHS smoke implemented: `True`.
- Pendulum DAE runner implemented: `False`.
- Brown--McPhee friction law implemented: `False`.
- TFE/Newmark/trapezoidal runners implemented: `False`.
- Source-policy rows completed: `0`.
- Source-policy runner-equivalence preflight: `preflight_ready_runner_equivalence_open`.
- Source-policy runner-equivalence preflight closed/open/source rows: `25/6/0`.
- Can close TFE B2 requirement now: `False`.

## Source-Policy Runner Equivalence Preflight

- Status: `preflight_ready_runner_equivalence_open`.
- Closed preconditions/open blockers: `25/6`.
- Source-policy rows closed by preflight: `0`.
- Source-policy DAE runner equivalent: `False`.
- Pendulum DAE runner implemented: `False`.
- Brown--McPhee source-code-equivalent law: `False`.
- TFE/Newmark/trapezoidal source-policy runners implemented: `False`.
- Gauss6/FullVA source-policy runner implemented: `False`.
- Full T=10 source grid policy resolved: `False`.
- Can close TFE lane from preflight: `False`.

| closed precondition | satisfied | evidence |
|---|---:|---|
| `source_policy_spec_extracted` | `True` | `TFE_SOURCE_POLICY_SPEC.json` |
| `source_pendulum_parameter_model_implemented` | `True` | `../../numerics/v048_cross_paper_same_test_benchmarks/tfe_source_pendulum_model.py` |
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

## Candidate Planar Reductions

| axis | inertia about pin | gravity torque scale | nondegenerate |
|---|---:|---:|---:|
| `x` | `5.000000e-02` | `0.000000e+00` | `False` |
| `y` | `9.551100e+01` | `0.000000e+00` | `False` |
| `z` | `9.550900e+01` | `3.031290e+02` | `True` |

## Smoke Trajectory

- Axis: `z`.
- h/steps: `0.001` / `10`.
- theta/omega final: `-1.586913e-04` / `-3.173827e-02`.
- energy delta: `-5.044576e-15`.

## Source Metric Smoke

- coordinate/velocity error: `1.000000e-01` / `2.000000e-01`.
- Frobenius eta: `1.413624e-01`.
- mechanical energy deviation: `3.217258e+01`.

## Candidate Friction Smoke

- Provenance: `v022_revolute_brown_mcphee_surrogate_not_source_policy_equivalent`.
- Source text: `../../external/literature/s11044-026-10153-w.txt`.
- Source text names Brown--McPhee velocity model: `True`.
- Source text reports mu_s/mu_d: `True`.
- Source text defers law details to Refs. 38--39: `True`.
- Encoded candidate formula: `tau = -R N [mu_d tanh(4 omega/vs) + (mu_s-mu_d)(omega/vs)/(0.25(omega/vs)^2+0.75)^2] - c tanh(4) omega`.
- Source-code-equivalent law: `False`.
- Transition velocity resolved from source: `False`.
- Torque sign check: `True`.
- Frictional h/steps: `0.001` / `10`.
- Frictional theta/omega final: `9.839223e-03` / `9.678510e-01`.
- Frictional energy delta: `-3.865193e-02`.
- Max candidate friction power: `-3.678259e+00`.

## Absolute-Coordinate DAE Smoke

- Frictionless hinge position/velocity residuals: `0.000000e+00` / `0.000000e+00`.
- Frictionless translational/axis-rotational residuals: `3.552714e-15` / `1.615375e-14`.
- Frictional candidate translational/axis-rotational residuals: `3.552714e-15` / `4.751755e-14`.
- Frictional candidate power: `-7.068702e-01`.
- Source-policy DAE runner equivalent: `False`.

## Source-Output Time-Integration Smoke

- t_final/reference h: `0.1` / `0.00025`.
- rows: `2`.
- Source-policy time-integration runner equivalent: `False`.

## Source Reference Solution Policy Smoke

- h/check h: `0.0001` / `5e-05`.
- t_final: `0.01`.
- bounded smoke, not full T=10: `True`.
- default 1e-4 campaign invoked: `False`.
- rows: `2`.

## Source Reference Full T=10 Probe

- case: `frictionless_pendulum_reference_full_T10_probe`.
- h/check h: `0.0001` / `5e-05`.
- t_final: `10.0`.
- source/check steps: `100000` / `200000`.
- theta/omega final: `-2.879016e+00` / `-1.283612e+00`.
- coordinate/velocity check error: `3.819167e-14` / `2.484679e-13`.
- source-policy rows completed: `0`.
- source-policy method runner equivalent: `False`.

## Source Comparator Candidate Runner Smoke

- candidate methods: `Newmark_beta,trapezoidal`.
- rows: `4`.
- Source-policy method runner equivalent: `False`.
- TFE m=1/2/3 source-policy runners implemented: `False`.

## Candidate TFE m=1/2/3 Runner Smoke

- t_final/reference h: `1.0` / `0.00025`.
- h grid: `[0.1, 0.05, 0.025]`.
- candidate methods: `TFE_m1,TFE_m2,TFE_m3_GL`.
- rows: `6`.
- Source-policy method runner equivalent: `False`.
- TFE m=1/2/3 source-policy runners implemented: `False`.

## Gauss6/FullVA Source-Pendulum Candidate Smoke

- API: `source_gauss6_fullva_candidate_runner_smoke`.
- t_final/reference h: `1.0` / `0.00025`.
- h grid: `[0.1, 0.05, 0.025]`.
- candidate methods: `Gauss6_FullVA`.
- rows: `2`.
- Candidate smoke implemented: `True`.
- Absolute-coordinate source-policy runner implemented: `False`.
- Legacy candidate alias implemented: `True`.
- FullVA DAE source-policy equivalent: `False`.
- Source-policy method runner equivalent: `False`.
- Source-policy rows completed: `0`.

| case | method | frictional | coord pair orders | vel pair orders | Frobenius pair orders | max residual |
|---|---|---:|---:|---:|---:|---:|
| `frictionless_pendulum_smoke` | `Gauss6_FullVA` | `False` | `[5.982888264259109, 6.1035376041084115]` | `[6.018130493493724, 6.033798531444542]` | `[5.982860182643504, 6.103597745554536]` | `9.220e-13` |
| `frictional_pendulum_candidate_smoke` | `Gauss6_FullVA` | `True` | `[2.2703710565768422, 1.6303345887710197]` | `[2.1640467317323515, 1.6354728437972896]` | `[2.270371056529795, 1.6303345886740612]` | `9.474e-13` |

## Source-Pendulum Same-Test Work/Precision

- API: `source_pendulum_same_test_work_precision_smoke`.
- t_final/reference h: `1.0` / `0.00025`.
- h grid: `[0.1, 0.05, 0.025]`.
- methods/method rows/metric rows: `6` / `6` / `18`.
- Source-policy method runner equivalent: `False`.
- Source-policy rows completed: `0`.
- External superiority allowed: `False`.

| method | expected order | coord pair orders | vel pair orders | finest vel error | Newton sum | runtime sum |
|---|---:|---:|---:|---:|---:|---:|
| `Newmark-beta` | `2` | `[1.9931865039704044, 1.9982871839918228]` | `[1.9957435358749889, 1.9989421865431225]` | `1.901e-04` | `114.0` | `2.266e-03` |
| `trapezoidal` | `2` | `[1.9947259286563228, 1.9986740124793245]` | `[1.9966176627931294, 1.9991553358311025]` | `2.416e-04` | `113.0` | `2.500e-03` |
| `TFE m=1` | `1` | `[2.1144313802576744, 2.272399303967131]` | `[1.675919008642049, 1.5159655068081903]` | `5.600e-04` | `132.0` | `2.142e-03` |
| `TFE m=2` | `3` | `[2.620861536607925, 2.8389975172934467]` | `[3.1324449161870995, 3.0743131458928725]` | `7.509e-08` | `125.0` | `9.779e-03` |
| `TFE m=3 GL` | `5` | `[6.68202776057924, 7.999812136852279]` | `[5.290941268303672, 5.188901922167423]` | `4.948e-12` | `135.0` | `9.918e-03` |
| `Gauss6/FullVA` | `6` | `[5.982888264259109, 6.1035376041084115]` | `[6.018130493493724, 6.033798531444542]` | `4.037e-13` | `111.0` | `2.679e-02` |

## Absolute-Coordinate Planar-Lift Trajectory Probe

- API: `absolute_coordinate_planar_lift_trajectory_probe`.
- t_final/reference h: `1.0` / `0.00025`.
- h grid: `[0.1, 0.05, 0.025]`.
- cases/methods/rows/metric rows: `2` / `6` / `12` / `36`.
- Max hinge position/velocity residuals: `0.000e+00` / `0.000e+00`.
- Max translational/axis-rotational residuals: `5.684e-14` / `1.066e-13`.
- Source-policy DAE runner equivalent: `False`.
- Source-policy rows completed: `0`.

| case | method | frictional | coord pair orders | vel pair orders | max DAE residual |
|---|---|---:|---:|---:|---:|
| `frictionless_pendulum_absolute_lift_probe` | `Newmark-beta` | `False` | `[1.9931865039704044, 1.9982871839918228]` | `[1.9957435358749889, 1.9989421865431225]` | `2.072e-14` |
| `frictionless_pendulum_absolute_lift_probe` | `trapezoidal` | `False` | `[1.9947259286563228, 1.9986740124793245]` | `[1.9966176627931294, 1.9991553358311025]` | `5.684e-14` |
| `frictionless_pendulum_absolute_lift_probe` | `TFE m=1` | `False` | `[2.1144313802576744, 2.272399303967131]` | `[1.675919008642049, 1.5159655068081903]` | `1.887e-14` |
| `frictionless_pendulum_absolute_lift_probe` | `TFE m=2` | `False` | `[2.620861536607925, 2.8389975172934467]` | `[3.1324449161870995, 3.0743131458928725]` | `5.684e-14` |
| `frictionless_pendulum_absolute_lift_probe` | `TFE m=3 GL` | `False` | `[6.68202776057924, 7.999812136852279]` | `[5.290941268303672, 5.188901922167423]` | `2.603e-14` |
| `frictionless_pendulum_absolute_lift_probe` | `Gauss6/FullVA` | `False` | `[5.982888264259109, 6.1035376041084115]` | `[6.018130493493724, 6.033798531444542]` | `5.684e-14` |
| `frictional_pendulum_candidate_absolute_lift_probe` | `Newmark-beta` | `True` | `[1.9129356220301497, 1.920442078888593]` | `[1.9257885087733244, 1.962847311172142]` | `6.750e-14` |
| `frictional_pendulum_candidate_absolute_lift_probe` | `trapezoidal` | `True` | `[1.8593783386772296, 1.8736203738439619]` | `[1.929821690152505, 1.9643682939180485]` | `8.171e-14` |
| `frictional_pendulum_candidate_absolute_lift_probe` | `TFE m=1` | `True` | `[-0.18329709531842112, 0.6084611748204433]` | `[1.7640683715510317, 1.6805517096817333]` | `6.040e-14` |
| `frictional_pendulum_candidate_absolute_lift_probe` | `TFE m=2` | `True` | `[1.995928674272114, 4.641932457532889]` | `[2.8988839504476034, 3.4970712735078746]` | `1.066e-13` |
| `frictional_pendulum_candidate_absolute_lift_probe` | `TFE m=3 GL` | `True` | `[2.7442066971445556, 0.7385174582202012]` | `[2.428484967269618, 0.8454625638903]` | `6.040e-14` |
| `frictional_pendulum_candidate_absolute_lift_probe` | `Gauss6/FullVA` | `True` | `[2.2703710565768422, 1.6303345887710197]` | `[2.1640467317323515, 1.6354728437972896]` | `7.461e-14` |

## DAE Trajectory Bridge Contract

- API: `dae_trajectory_bridge_contract_smoke`.
- Source runner / DAE runner: `bounded_source_policy_runner_smoke` / `bounded_absolute_coordinate_dae_trajectory_runner_smoke`.
- t_final/reference h: `0.024` / `0.0001`.
- h grid: `[0.012, 0.006, 0.003]`.
- methods/source metric rows/DAE metric rows/contract rows: `4` / `12` / `12` / `12`.
- matched contract rows: `12`.
- all rows finite: `True`.
- all DAE residuals below 1e-10: `True`.
- Source-policy DAE runner equivalent: `False`.
- Monolithic absolute-coordinate DAE integrator: `False`.
- Source-policy rows completed: `0`.

| method | h | coord error | vel error | step residual rows | max DAE residual |
|---|---:|---:|---:|---:|---:|
| `tfe2026_Newmark_beta` | `0.012` | `4.375e-11` | `2.585e-09` | `2` | `2.776e-14` |
| `tfe2026_Newmark_beta` | `0.006` | `1.049e-11` | `6.588e-10` | `4` | `7.434e-14` |
| `tfe2026_Newmark_beta` | `0.003` | `2.584e-12` | `1.650e-10` | `8` | `5.571e-14` |
| `tfe2026_TFE_m1` | `0.012` | `2.297e-06` | `2.676e-09` | `2` | `2.388e-14` |
| `tfe2026_TFE_m1` | `0.006` | `1.148e-06` | `7.001e-10` | `4` | `5.788e-14` |
| `tfe2026_TFE_m1` | `0.003` | `5.742e-07` | `1.856e-10` | `8` | `6.213e-14` |
| `tfe2026_TFE_m2` | `0.012` | `7.283e-13` | `1.657e-11` | `2` | `7.218e-14` |
| `tfe2026_TFE_m2` | `0.006` | `5.418e-14` | `1.036e-12` | `4` | `5.683e-14` |
| `tfe2026_TFE_m2` | `0.003` | `4.441e-15` | `6.482e-14` | `8` | `5.670e-14` |
| `tfe2026_trapezoidal` | `0.012` | `3.421e-11` | `2.585e-09` | `2` | `2.905e-14` |
| `tfe2026_trapezoidal` | `0.006` | `8.105e-12` | `6.588e-10` | `4` | `5.197e-14` |
| `tfe2026_trapezoidal` | `0.003` | `1.987e-12` | `1.650e-10` | `8` | `5.586e-14` |

## Candidate-Friction DAE Trajectory Contract

- API: `candidate_frictional_dae_trajectory_contract_smoke`.
- scope: `candidate_brown_mcphee_friction_bound_to_stepwise_absolute_dae_residuals_not_source_policy`.
- t_final/reference h: `0.024` / `0.0001`.
- h grid: `[0.012, 0.006, 0.003]`.
- methods/rows/step residual rows: `4` / `12` / `56`.
- all rows finite: `True`.
- all DAE residuals below 1e-9: `True`.
- all candidate friction power nonpositive: `True`.
- Brown--McPhee source-code-equivalent law: `False`.
- Source-policy DAE/method runner equivalent: `False` / `False`.
- Monolithic absolute-coordinate DAE integrator: `False`.
- Source-policy rows completed: `0`.

| method | h | coord error | vel error | step residual rows | max DAE residual | max friction power |
|---|---:|---:|---:|---:|---:|---:|
| `tfe2026_Newmark_beta` | `0.012` | `1.907e-07` | `6.326e-07` | `2` | `8.926e-14` | `-3.022e+00` |
| `tfe2026_Newmark_beta` | `0.006` | `4.770e-08` | `1.581e-07` | `4` | `1.266e-13` | `-3.022e+00` |
| `tfe2026_Newmark_beta` | `0.003` | `1.192e-08` | `3.954e-08` | `8` | `1.030e-13` | `-3.022e+00` |
| `tfe2026_TFE_m1` | `0.012` | `2.199e-06` | `9.138e-07` | `2` | `5.906e-14` | `-3.022e+00` |
| `tfe2026_TFE_m1` | `0.006` | `1.130e-06` | `2.989e-07` | `4` | `8.349e-14` | `-3.022e+00` |
| `tfe2026_TFE_m1` | `0.003` | `5.726e-07` | `1.099e-07` | `8` | `9.104e-14` | `-3.022e+00` |
| `tfe2026_TFE_m2` | `0.012` | `1.194e-11` | `8.948e-12` | `2` | `5.951e-14` | `-3.022e+00` |
| `tfe2026_TFE_m2` | `0.006` | `2.773e-12` | `6.373e-13` | `4` | `4.796e-14` | `-3.022e+00` |
| `tfe2026_TFE_m2` | `0.003` | `4.268e-13` | `3.841e-14` | `8` | `4.796e-14` | `-3.022e+00` |
| `tfe2026_trapezoidal` | `0.012` | `1.222e-07` | `6.324e-07` | `2` | `7.461e-14` | `-3.022e+00` |
| `tfe2026_trapezoidal` | `0.006` | `3.056e-08` | `1.581e-07` | `4` | `6.972e-14` | `-3.022e+00` |
| `tfe2026_trapezoidal` | `0.003` | `7.640e-09` | `3.953e-08` | `8` | `9.948e-14` | `-3.022e+00` |

## TFE Appendix-B Coefficient Certificate

- Source: `Chaturvedi--Sandu--Sandu Appendix B, equations (40), (41), and (43)`.
- h: `0.012`.
- methods: `TFE_m1,TFE_m2,TFE_m3_GL`.
- all formula matches: `True`.
- max absolute difference: `0.000e+00`.
- scope: `coefficient_formula_certificate_only_not_source_policy_runner_equivalence`.
- Source-policy method runner equivalent: `False`.
- Source-policy rows completed: `0`.

| method | formula match | max abs diff | alpha | beta | gamma | nodes |
|---|---:|---:|---:|---:|---:|---:|
| `TFE_m1` | `True` | `0.000e+00` | `0.000e+00` | `0.000e+00` | `0.000e+00` | `0.000e+00` |
| `TFE_m2` | `True` | `0.000e+00` | `0.000e+00` | `0.000e+00` | `0.000e+00` | `0.000e+00` |
| `TFE_m3_GL` | `True` | `0.000e+00` | `0.000e+00` | `0.000e+00` | `0.000e+00` | `0.000e+00` |

## Bounded Source-Policy Runner Smoke

- API: `bounded_source_policy_runner_smoke`.
- t_final/reference h: `0.024` / `0.0001`.
- h grid: `[0.012, 0.006, 0.003]`.
- rows: `4`.
- unified method dispatch: `True`.
- Full T=10 source-policy reproduction: `False`.
- Source-policy method runner equivalent: `False`.
- Source-policy rows completed: `0`.

## Active B2 Candidate Row Smoke

- t_final/reference h: `0.024` / `0.0001`.
- h grid: `[0.012, 0.006, 0.003]`.
- rows: `4`.
- Full T=10 source-policy reproduction: `False`.
- Source-policy method runner equivalent: `False`.
- Source-policy rows completed: `0`.

| method | expected order | coord pair orders | vel pair orders | finest coord error | finest vel error | max residual |
|---|---:|---:|---:|---:|---:|---:|
| `tfe2026_Newmark_beta` | `2` | `[2.060236582778604, 2.021658060033648]` | `[1.9725192134621587, 1.9974505139985181]` | `2.584e-12` | `1.650e-10` | `4.856e-13` |
| `tfe2026_TFE_m1` | `1` | `[0.9999885388079264, 0.9999948000344016]` | `[1.93429876579997, 1.9150546291348411]` | `5.742e-07` | `1.856e-10` | `3.109e-15` |
| `tfe2026_TFE_m2` | `3` | `[3.7487427619425597, 3.608809242675524]` | `[4.000108727189839, 3.998048989143321]` | `4.441e-15` | `6.482e-14` | `4.945e-13` |
| `tfe2026_trapezoidal` | `2` | `[2.0775052321986447, 2.027936876503123]` | `[1.9725192456063625, 1.9974505747802809]` | `1.987e-12` | `1.650e-10` | `4.856e-13` |

## Active B2 Full T=10 Coarse Candidate Probe

- API: `active_tfe_b2_full_t10_coarse_candidate_probe`.
- t_final/reference h: `10.0` / `0.0125`.
- h grid: `[0.1, 0.05, 0.025]`.
- rows: `4`.
- Full T=10 candidate probe completed: `True`.
- Full T=10 source-policy reproduction: `False`.
- Source-policy reference h: `0.0001`.
- Source-policy reference invoked: `False`.
- Source-policy rows completed: `0`.
- Finite/residual-ok rows: `4/4`.

| method | expected order | coord pair orders | vel pair orders | finest coord error | finest vel error | max residual |
|---|---:|---:|---:|---:|---:|---:|
| `tfe2026_Newmark_beta` | `2` | `[2.0275441214668217, 2.00705831194839]` | `[1.9913345509240037, 1.9979308636529627]` | `1.956e-03` | `4.642e-03` | `9.965e-13` |
| `tfe2026_TFE_m1` | `1` | `[2.622522438741144, 5.794748228533962]` | `[1.275914434435794, -0.07748019480798148]` | `5.226e-05` | `6.801e-03` | `9.086e-13` |
| `tfe2026_TFE_m2` | `3` | `[2.6944804658657833, 2.8242719940269363]` | `[2.9269220362250254, 2.9523681373640587]` | `3.346e-07` | `2.375e-06` | `3.346e-11` |
| `tfe2026_trapezoidal` | `2` | `[2.0211072045442493, 2.005385108140571]` | `[1.9927244377728803, 1.9982473034815917]` | `1.504e-03` | `3.558e-03` | `9.775e-13` |

## Active B2 Source-Reference Full T=10 Candidate Probe

- API: `active_tfe_b2_source_reference_full_t10_candidate_probe`.
- t_final/reference h: `10.0` / `0.0001`.
- h grid: `[0.1, 0.05, 0.025]`.
- rows: `4`.
- Full T=10 candidate probe completed: `True`.
- Full T=10 source-policy reproduction: `False`.
- Source-policy reference h: `0.0001`.
- Source-policy reference invoked: `True`.
- Source-policy rows completed: `0`.
- Method/DAE runner equivalent: `False/False`.
- Finite/residual-ok rows: `4/4`.

| method | expected order | coord pair orders | vel pair orders | finest coord error | finest vel error | max residual | accepted use |
|---|---:|---:|---:|---:|---:|---:|---|
| `tfe2026_Newmark_beta` | `2` | `[2.0275424122016026, 2.0070514733072407]` | `[1.9913330376951968, 1.9979248101637703]` | `1.956e-03` | `4.642e-03` | `9.965e-13` | `full_T10_source_reference_candidate_probe_not_source_policy` |
| `tfe2026_TFE_m1` | `1` | `[2.6225172968030397, 5.795095188872011]` | `[1.275922652304982, -0.07748049892165708]` | `5.224e-05` | `6.800e-03` | `9.086e-13` | `full_T10_source_reference_candidate_probe_not_source_policy` |
| `tfe2026_TFE_m2` | `3` | `[2.7008531269067366, 2.870965215480403]` | `[2.9286945952379195, 2.966198929168668]` | `3.223e-07` | `2.349e-06` | `3.346e-11` | `full_T10_source_reference_candidate_probe_not_source_policy` |
| `tfe2026_trapezoidal` | `2` | `[2.0211049822810634, 2.0053762178402597]` | `[1.992722463482501, 1.9982394058217936]` | `1.504e-03` | `3.558e-03` | `9.775e-13` | `full_T10_source_reference_candidate_probe_not_source_policy` |

## TFE m=3 Full T=10 Coarse Formula Probe

- API: `tfe_m3_gl_full_t10_coarse_formula_probe`.
- t_final/reference h: `10.0` / `0.0125`.
- h grid: `[0.1, 0.05, 0.025]`.
- rows: `1`.
- full T=10 formula probe completed: `True`.
- formal expected order: `5`.
- Source-policy reference invoked: `False`.
- Source-policy rows completed: `0`.
- Finite/residual-ok rows: `1/1`.

| method | expected order | coord pair orders | vel pair orders | finest coord error | finest vel error | max residual |
|---|---:|---:|---:|---:|---:|---:|
| `tfe2026_TFE_m3_GL_formula_target` | `5` | `[1.1187902286743412, 0.06580879265577567]` | `[2.4335197236108614, 0.22836543562171308]` | `1.236e-08` | `2.613e-08` | `1.521e-10` |

| case | method | frictional | coord pair orders | vel pair orders | max residual |
|---|---|---:|---:|---:|---:|
| `frictionless_pendulum_smoke` | `TFE_m1` | `False` | `[2.1144313802576744, 2.272399303967131]` | `[1.675919008642049, 1.5159655068081903]` | `9.086e-13` |
| `frictionless_pendulum_smoke` | `TFE_m2` | `False` | `[2.620861536607925, 2.8389975172934467]` | `[3.1324449161870995, 3.0743131458928725]` | `1.106e-11` |
| `frictionless_pendulum_smoke` | `TFE_m3_GL` | `False` | `[6.68202776057924, 7.999812136852279]` | `[5.290941268303672, 5.188901922167423]` | `3.761e-11` |
| `frictional_pendulum_candidate_smoke` | `TFE_m1` | `True` | `[-0.18329709531842112, 0.6084611748204433]` | `[1.7640683715510317, 1.6805517096817333]` | `2.771e-13` |
| `frictional_pendulum_candidate_smoke` | `TFE_m2` | `True` | `[1.995928674272114, 4.641932457532889]` | `[2.8988839504476034, 3.4970712735078746]` | `4.036e-12` |
| `frictional_pendulum_candidate_smoke` | `TFE_m3_GL` | `True` | `[2.7442066971445556, 0.7385174582202012]` | `[2.428484967269618, 0.8454625638903]` | `8.089e-12` |

Reading rule: this closes parameter, planar metric, absolute-coordinate residual-smoke, bounded trajectory-metric smoke, and candidate Newmark/trapezoidal/TFE/Gauss6/friction smoke layers plus a unified bounded source-policy runner API, an absolute-coordinate planar-lift trajectory probe, a bounded stepwise absolute-coordinate DAE residual runner, a named source-policy absolute-coordinate DAE runner contract entrypoint that remains candidate-backed and non-equivalent, named non-equivalent method-runner and Gauss6/FullVA DAE runner contract entrypoints, a DAE trajectory bridge contract, a candidate-friction DAE trajectory contract, full T=10 coarse candidate probe, full T=10 active-B2 h=1e-4 source-reference candidate probe, TFE m=3 full T=10 coarse formula probe, and a full T=10 frictionless source-reference h=1e-4 probe only. It is not an original TFE source-policy reproduction and does not authorize external-superiority claims.
