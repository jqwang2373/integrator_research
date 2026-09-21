# CMAME Self-Contained Runner Extraction Plan

Status: **local_accepted_rows_self_contained_runner_ready_source_policy_package_open**.
Full-package self-contained runner ready: `False`.
Local accepted-row self-contained runner ready: `True`.
Full source-policy self-contained runner ready: `False`.
B6 final prose pass ready under narrowed claim: `True`.
Full source-policy B6 prose ready: `False`.
B6 closure preflight/status: `b6_final_prose_pass_closed_under_narrowed_b4_b7_scope`; allowed `True`.
Runner adapter present/self-contained: `True/False`.
P1 local single/double ready: `True`.
P1 single-runner candidate ready: `True`.
P1 double-runner candidate ready: `True`.
P1 regenerated candidate rows: `6/6`.
B6 four-example local evidence runner: `True`; rows `12`; self-contained/replay-only `['single_pendulum', 'double_pendulum', 'four_link', 'slider_crank']/[]`.
P1 audit status: `closed_single_double_runner_candidates_ready`.
P1 v047 primary closure lines: `460`.
Closed-loop local runner candidate: `closed_loop_local_runner_candidate_passed_compact`; rows `6`; compact `True`.
B6 closed-loop extraction audit: `closed_loop_self_contained_runner_candidate_ready_source_policy_open`; target symbols `33/756`; ready `True`.
Target source symbols: `38` functions/classes, `2359` symbol lines.
Source-policy rows closed: `0/40`.
Direct PC2 proof gap closed: `True`.

## Phases

| phase | status | evidence |
|---|---|---|
| `P0_report_adapter` | `partial_complete` | runner-adapter candidate validates embedded 44-row matrix and can call v048 --report-only |
| `P1_local_gauss6_rows` | `closed` | P1 dependency audit: closed_single_double_runner_candidates_ready; local single/double ready=True; single candidate ready=True; double candidate ready=True; candidate rows=6/6; v047 primary closure lines=460 |
| `P1b_four_example_local_evidence_runner` | `closed` | four-example local evidence rows=12; self-contained=['single_pendulum', 'double_pendulum', 'four_link', 'slider_crank']; replay-only=[]; four-example self-contained simulation ready=True; closed-loop extraction audit=closed_loop_self_contained_runner_candidate_ready_source_policy_open |
| `P1c_closed_loop_self_contained_runner` | `closed_compact_candidate_passed` | target symbols=33/756 lines; replay-only closed-loop examples=[]; candidate rows=6; candidate compact=True; self-contained ready=True |
| `P2_external_public_baselines` | `open` | RA2021/HI2022/VP wrappers still depend on external public-code paths |
| `P3_tfe_source_policy_rows` | `open` | original TFE source-policy runner and full T=10 endpoint policy remain open |
| `P4_proof_boundary` | `closed` | direct_pc2_proof_gap_closed=True; this package phase does not close primitive/Taylor, solver-policy, residual-to-error, or source-policy boundaries |

## Target Symbols

| source | symbol | role | lines |
|---|---|---|---:|
| `../../numerics/v048_cross_paper_same_test_benchmarks/run_coarse_four_example_order.py` | `run_ra2021_rows` | external_ra2021_public_baselines | `68` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/run_coarse_four_example_order.py` | `run_hi2022_rows` | external_hi2022_public_baselines | `34` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/run_coarse_four_example_order.py` | `run_local_single_double_rows` | local_single_double_gauss6_fullva | `58` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/run_coarse_four_example_order.py` | `local_closed_loop_rows` | local_four_link_slider_crank_closed_loop | `26` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/run_coarse_four_example_order.py` | `run_tfe2026_second_order_rows` | tfe_second_order_baselines | `85` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/run_coarse_four_example_order.py` | `run_tfe2026_tfe_m1_rows` | tfe_m1_baselines | `74` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/run_coarse_four_example_order.py` | `run_tfe2026_tfe_m2_rows` | tfe_m2_baselines | `76` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/run_coarse_four_example_order.py` | `run_tfe2026_tfe_m3_rows` | tfe_m3_scope_boundary | `117` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/run_coarse_four_example_order.py` | `run_vp2024_coordinate_partitioning_rows` | vp2024_proxy_baseline | `82` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/run_coarse_four_example_order.py` | `summarize` | paper_matrix_aggregation | `144` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/run_v048.py` | `run_public_model_state_history` | ra2021_public_state_history | `20` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/run_v048.py` | `run_hi2022_model_state_history` | hi2022_public_state_history | `39` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/run_v048.py` | `run_ra2021_order_rows` | ra2021_public_order_rows | `114` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/run_v048.py` | `run_ra2021_double_pendulum_order_rows` | ra2021_double_public_rows | `144` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/run_v048.py` | `run_hi2022_halfimplicit_rows` | hi2022_halfimplicit_rows | `160` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/run_v048.py` | `run_gauss6_fullva_public_horizon_single_rows` | local_single_gauss6_rows | `147` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/run_v048.py` | `run_gauss6_fullva_public_horizon_double_coarse_rows` | local_double_gauss6_rows | `149` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/run_v048.py` | `switch_simengine_root` | external_public_code_path_switch | `6` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/run_v048.py` | `patch_modern_numpy_scalar_assignments` | external_public_code_compatibility | `28` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/run_v048.py` | `estimate_order` | order_estimation | `6` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/build_closed_loop_true_dynamic_strict_common_reference.py` | `import_v047_module` | v047_exact_endpoint_dependency | `11` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/build_closed_loop_true_dynamic_strict_common_reference.py` | `setup_exact_system` | v047_exact_endpoint_reference | `6` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/build_closed_loop_true_dynamic_strict_common_reference.py` | `local_rows` | local_true_dynamic_rows | `54` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/build_closed_loop_true_dynamic_strict_common_reference.py` | `public_rows` | public_true_dynamic_rows | `79` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/build_closed_loop_true_dynamic_strict_common_reference.py` | `summarize_rows` | strict_common_reference_summary | `121` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/build_closed_loop_true_dynamic_strict_common_reference.py` | `main` | strict_common_reference_builder | `33` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/closed_loop_fullva_dynamic_residual.py` | `closed_loop_fullva_stage_residual` | dynamic_stage_residual_core | `15` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/closed_loop_fullva_dynamic_residual.py` | `endpoint_state_from_system` | endpoint_state_extraction | `9` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/closed_loop_fullva_dynamic_residual.py` | `endpoint_state_error_inf` | endpoint_error_norm | `12` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/closed_loop_fullva_dynamic_residual.py` | `gauss6_closed_loop_fullva_dynamic_step_newton_smoke` | non_oracle_newton_smoke | `57` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/tfe_source_pendulum_model.py` | `source_output_policy` | tfe_source_output_policy | `9` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/tfe_source_pendulum_model.py` | `source_error_metrics` | tfe_source_error_metrics | `20` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/tfe_source_pendulum_model.py` | `newmark_beta_candidate_step` | tfe_newmark_baseline | `43` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/tfe_source_pendulum_model.py` | `trapezoidal_candidate_step` | tfe_trapezoidal_baseline | `41` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/tfe_source_pendulum_model.py` | `tfe_m1_candidate_step` | tfe_m1_baseline | `52` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/tfe_source_pendulum_model.py` | `tfe_multinode_candidate_step` | tfe_m2_m3_baseline | `62` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/tfe_source_pendulum_model.py` | `bounded_source_policy_runner_smoke` | tfe_bounded_runner_smoke | `99` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/tfe_source_pendulum_model.py` | `active_tfe_b2_full_t10_coarse_candidate_probe` | tfe_full_t10_probe | `59` |
