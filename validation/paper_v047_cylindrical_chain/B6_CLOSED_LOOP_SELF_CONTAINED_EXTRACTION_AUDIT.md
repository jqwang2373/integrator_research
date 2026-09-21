# B6 Closed-Loop Self-Contained Extraction Audit

Status: **closed_loop_self_contained_runner_candidate_ready_source_policy_open**.
Self-contained closed-loop runner ready: `True`.
B4 opt-in required for this audit: `False`.
Run v047/v048 invoked: `False/False`.
Closed-loop replay-only examples: `[]`.
Closed-loop local replay rows: `6`.
Target closed-loop source files/lines: `2/958`.
Target symbols/lines: `33/756`.
Source-policy rows closed: `0/40`.
Closed-loop candidate status: `closed_loop_local_runner_candidate_passed_compact`.
Closed-loop candidate rows: `6`.
Closed-loop candidate Python files/lines: `10/1962`.
Closed-loop candidate line limit ok: `True`.
Closed-loop candidate package: `cmame_closed_loop_local_runner_candidate`.

## Target Sources

| source | lines | imports |
|---|---:|---|
| `../../numerics/v048_cross_paper_same_test_benchmarks/build_closed_loop_true_dynamic_newton_coarse_order.py` | `364` | `__future__, closed_loop_fullva_dynamic_residual, csv, importlib.util, json, math, numpy, pathlib, sys, time` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/closed_loop_fullva_dynamic_residual.py` | `594` | `__future__, dataclasses, numpy` |

## Target Symbols

| source | symbol | role | lines |
|---|---|---|---:|
| `../../numerics/v048_cross_paper_same_test_benchmarks/build_closed_loop_true_dynamic_newton_coarse_order.py` | `import_v047_module` | external v047 loader to remove | `11` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/build_closed_loop_true_dynamic_newton_coarse_order.py` | `write_csv` | row output helper | `7` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/build_closed_loop_true_dynamic_newton_coarse_order.py` | `setup_exact_system` | exact/reference system setup to replace with local model setup | `6` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/build_closed_loop_true_dynamic_newton_coarse_order.py` | `finite` | order-fit finite-value guard | `6` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/build_closed_loop_true_dynamic_newton_coarse_order.py` | `observed_order` | three-step-size observed order fit | `18` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/build_closed_loop_true_dynamic_newton_coarse_order.py` | `simulate_model_h` | closed-loop model/h trajectory row generator | `111` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/build_closed_loop_true_dynamic_newton_coarse_order.py` | `build_model_summary` | per-model order and acceptance summary | `27` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/build_closed_loop_true_dynamic_newton_coarse_order.py` | `annotate_rows_with_orders` | row annotation with model-level orders | `9` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/build_closed_loop_true_dynamic_newton_coarse_order.py` | `write_markdown` | human-readable local row report | `36` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/build_closed_loop_true_dynamic_newton_coarse_order.py` | `main` | current non-self-contained orchestration | `77` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/closed_loop_fullva_dynamic_residual.py` | `ClosedLoopStageContext` | stage chart/context state | `4` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/closed_loop_fullva_dynamic_residual.py` | `exp_so3` | SO(3) exponential map | `9` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/closed_loop_fullva_dynamic_residual.py` | `log_so3` | SO(3) logarithm map | `27` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/closed_loop_fullva_dynamic_residual.py` | `right_jacobian_inverse_so3` | SO(3) right-Jacobian inverse | `8` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/closed_loop_fullva_dynamic_residual.py` | `skew3` | skew matrix helper | `10` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/closed_loop_fullva_dynamic_residual.py` | `capture_stage_context` | start-of-step chart capture | `6` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/closed_loop_fullva_dynamic_residual.py` | `_snapshot_system_state` | residual side-effect guard | `14` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/closed_loop_fullva_dynamic_residual.py` | `_restore_system_state` | residual side-effect restoration | `8` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/closed_loop_fullva_dynamic_residual.py` | `generalized_qva_from_system` | pack q/v/a from multibody state | `23` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/closed_loop_fullva_dynamic_residual.py` | `pack_closed_loop_fullva_stage_vector` | stage vector packer | `13` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/closed_loop_fullva_dynamic_residual.py` | `unpack_closed_loop_fullva_stage_vector` | stage vector unpacker | `16` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/closed_loop_fullva_dynamic_residual.py` | `set_system_stage_state` | apply stage q/v/a to multibody state | `22` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/closed_loop_fullva_dynamic_residual.py` | `closed_loop_fullva_stage_residual_blocks` | constraint and Newton-Euler residual blocks | `41` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/closed_loop_fullva_dynamic_residual.py` | `closed_loop_fullva_stage_residual` | flat stage residual | `15` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/closed_loop_fullva_dynamic_residual.py` | `_body_vectors` | endpoint vector extraction helper | `2` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/closed_loop_fullva_dynamic_residual.py` | `_set_body_vectors` | endpoint vector assignment helper | `4` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/closed_loop_fullva_dynamic_residual.py` | `endpoint_state_from_system` | endpoint state extraction | `9` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/closed_loop_fullva_dynamic_residual.py` | `endpoint_state_error_inf` | endpoint infinity-norm errors | `12` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/closed_loop_fullva_dynamic_residual.py` | `finite_difference_jacobian` | dense finite-difference Newton Jacobian | `19` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/closed_loop_fullva_dynamic_residual.py` | `newton_solve_closed_loop_fullva_stage` | damped Newton stage solve | `87` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/closed_loop_fullva_dynamic_residual.py` | `start_extrapolated_closed_loop_stage_vector` | non-oracle stage predictor | `12` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/closed_loop_fullva_dynamic_residual.py` | `_apply_gauss6_endpoint_update` | Gauss6 endpoint update | `30` |
| `../../numerics/v048_cross_paper_same_test_benchmarks/closed_loop_fullva_dynamic_residual.py` | `gauss6_closed_loop_fullva_dynamic_step_newton_smoke` | non-oracle closed-loop dynamic step | `57` |

## Blockers

| id | status | evidence |
|---|---|---|
| `CL1_v047_loader_dependency` | `bypassed_by_compact_candidate` | compact candidate uses local rA-only public SBEL subset and does not import run_v047/v046 |
| `CL2_closed_loop_model_definitions` | `satisfied_by_compact_candidate` | compact candidate includes local four_link/slider_crank setup modules and public model JSON |
| `CL3_primary_submission_runner` | `satisfied_compact_candidate_passed` | candidate regenerates six closed-loop rows without v046/v047/v048 imports and satisfies the compact package line limit |
| `CL4_candidate_size_limit` | `satisfied` | 10/1962 Python files/lines; limit=2000 |

## Next Step

keep compact closed-loop candidate evidence synchronized while B4/B7 source-policy gates remain open; run the final B6 prose pass only after B4/B7 wording stabilizes
