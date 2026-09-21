# CMAME P1 Local-Runner Extraction Audit

Status: **closed_single_double_runner_candidates_ready**.
P1 local single/double ready: `True`.
P1 single-runner candidate ready: `True`.
P1 double-runner candidate ready: `True`.
P1 regenerated candidate rows: `6/6`.
Self-contained runner ready: `False`.
v047 source size: `69264` Python lines.
v048 local runner wrappers: `5` symbols.
v047 primary seed closure: `24` symbols, `460` symbol lines.
Source-policy rows closed: `0/40`.

## Acceptance Boundary

- Required examples: `single_pendulum, double_pendulum`.
- Required h values: `[0.1, 0.05, 0.025]` with reference h `0.0125` and T `0.1`.
- Primary import of run_v047 forbidden: `True`.
- Dynamic load_v029 forbidden: `True`.

## Single-Runner Candidate

| field | value |
|---|---:|
| ready | `True` |
| rows | `6/6` |
| position order | `6.013317461143006` |
| velocity order | `6.006882393965576` |
| imports v047/v048 | `False` |

## Double-Runner Candidate

| field | value |
|---|---:|
| ready | `True` |
| rows | `3/3` |
| position order | `6.01071161969125` |
| velocity order | `6.009715656945229` |
| imports v047/v048/v029 | `False` |

## v048 Wrapper Symbols

| source | symbol | role | lines | v047 calls |
|---|---|---|---:|---|
| `numerics/v048_cross_paper_same_test_benchmarks/run_v048.py` | `import_v047_single_fullva_module` | dynamic_v047_import_boundary | `12` | `-` |
| `numerics/v048_cross_paper_same_test_benchmarks/run_v048.py` | `public_single_reference_alignment` | single_public_reference_alignment | `10` | `np.abs, np.max, v047_module.asme_single_state_from_time` |
| `numerics/v048_cross_paper_same_test_benchmarks/run_v048.py` | `run_gauss6_fullva_public_horizon_single_rows` | single_local_row_wrapper | `147` | `np.isclose, time.perf_counter, v047_module.integrate_asme_single_driven_absolute_fullva` |
| `numerics/v048_cross_paper_same_test_benchmarks/run_v048.py` | `run_gauss6_fullva_public_horizon_double_coarse_rows` | double_local_row_wrapper | `149` | `np.isclose, np.isfinite, time.perf_counter, v047_module.compare_nested_trajectory, v047_module.integrate_v029_asme_double_trajectory, v047_module.load_v029, v047_module.make_asme_double_pendulum_params` |
| `numerics/v048_cross_paper_same_test_benchmarks/run_coarse_four_example_order.py` | `run_local_single_double_rows` | coarse_four_example_local_entry | `58` | `rv.Gauss6PublicDoubleCoarseConfig, rv.Gauss6PublicSingleConfig, rv.run_gauss6_fullva_public_horizon_double_coarse_rows, rv.run_gauss6_fullva_public_horizon_single_rows` |

## v047 Primary Seeds

| symbol | role | lines | direct internal calls |
|---|---|---:|---|
| `integrate_asme_single_driven_absolute_fullva` | single_pendulum_local_gauss6_fullva | `89` | `asme_single_absolute_endpoint_diagnostics, asme_single_absolute_initial_state, solve_asme_single_absolute_fullva_step` |
| `load_v029` | dynamic_double_pendulum_source_loader | `7` | `-` |
| `make_asme_double_pendulum_params` | double_pendulum_asme_parameter_bridge | `21` | `asme_bar_mass_inertia` |
| `integrate_v029_asme_double_trajectory` | double_pendulum_local_gauss6_fullva_trajectory | `44` | `asme_double_pendulum_initial_state, asme_double_world_rotation` |
| `compare_nested_trajectory` | double_pendulum_reference_error_metric | `21` | `-` |

## Open Blockers

| id | status | evidence |
|---|---|---|
| `P1B1_primary_v047_import` | `closed` | standalone P1 single/double candidates regenerate local rows without importing run_v047.py |
| `P1B2_dynamic_v029_bridge` | `closed` | standalone double-pendulum candidate vendors the required FullVA residual and does not load run_v029.py |
| `P1B3_no_standalone_mechanism_module` | `closed` | standalone single-pendulum and double-pendulum candidates are present |
| `P1B4_no_p1_row_regeneration_certificate` | `closed` | single-pendulum and double-pendulum candidates regenerated 6/6 local rows |

## Next Extraction Actions

- keep the self-contained single/double P1 runner candidates synchronized with PAPER_NUMERICAL_RESULT_MATRIX
- do not promote P1 local rows into source-policy external-superiority claims
- continue with P2 external public baselines or P4 proof-boundary closure before submission readiness
