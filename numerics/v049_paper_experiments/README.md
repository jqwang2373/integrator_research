# v049_paper_experiments

The experiments behind Section 6 of the rewritten manuscript (2026-09-21). Every table entry and
figure of that section is read from the result files written here; `validation/validate_manuscript.py`
checks that correspondence.

| Script | Experiment | Output |
| --- | --- | --- |
| `common.py` | Driver over the accepted residual path (`run_v047.gauss_step`), reference cache (`results/refs/`), error measures (chord-based geodesic orientation angle), order fits with a Richardson floor, 1-stage midpoint tableau, conservative chain variant, energy | – |
| `e1_convergence.py` | Chain, `T = 0.5`, `h = 0.1/2^k` (k = 0..5), reference `0.1/256`, floor from `0.1/128` | `E1_convergence.*` |
| `e2_gauss_family.py` | 1/2/3-stage Gauss with the same stage system, wall time and Newton work (JIT warm-up before timing) | `E2_gauss_family.*` |
| `e3_friction_sweep.py` | Stribeck velocity 0.5 … 0.02, per-case references, Neumann threshold `h_0` | `E3_friction_sweep.*` |
| `e4_asme_mechanisms.py` | Four public mechanisms, `T = 1`: driven single pendulum (analytic), double pendulum (v029 harness with the v048 AD-safe small-angle patch), four-link and slider-crank (v048 closed-loop shard runner) | `E4_asme.*` |
| `e5_public_baselines.py` | Double pendulum on the public horizon `T = 3` against the cached local `h = 1e-4` reference (`v048/results/ra2021_double_local_source_policy_candidate_reference_h0p0001_T3.npz`): local Gauss6, public 2021 rA/rp/rε and 2022 half-implicit rA/rA-half codes replayed on `t_i = i h`; model-alignment check at `T = 0.1`; driven-mechanism rows assembled from v048 | `E5_double_pendulum.*`, `E5_driven_public_horizon.csv`, `E5_public_baselines.json` |
| `e6_long_time.py` | Regular branch `[0, 0.5]` at `h = 0.01`: constraint norms, energy of the conservative variant, Newton counts | `E6_long_time.*`, `E6_series.npz` |
| `e7_solver_envelope.py` | Production Newton rule on the E1 grid: accepted residual, ratio to `h^7`, out-of-axis components | `E7_solver_envelope.*` |
| `make_figures.py` | Draws all `results/E*.png` from the JSON files (no computation) | `E*.png` |

Run from this directory with `../../.venv_sbel/bin/python <script>`. The chain runs stop at
`T = 0.5` because the benchmark's frozen sliding direction degenerates at `t ≈ 0.605`
(`common.T_REGULAR_BRANCH_END`). Nothing here calls the `run_v047.py` campaign entry point; the
double-pendulum reference at `h = 1e-4` is reused from v048 (1.6 h to recompute).
