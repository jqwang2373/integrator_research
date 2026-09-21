# Cross-Paper Benchmark Specification

Status: **spec extracted, partial evidence recorded, full same-test campaign not yet run**

This is the executable source-of-truth for the next paper gate. It records what
must be matched before a comparison against the original TFE paper or the
Kissel/Negrut public-code papers is defensible.

The row-level inventory is machine-readable in
`CROSS_PAPER_BENCHMARK_CASES.json`. That file is intentionally marked
`same_test_campaign_status=not_run`; it is a run list, not a completed
external-superiority campaign. Its individual `current_status` entries record
the full required source-policy case status, while `partial_evidence_overlay`
records existing coarse-first and bounded evidence. The default policy remains
`coarse_first_no_default_1e-4`; strict public-policy `1e-4` rows are opt-in
only, not the default way to compute order. The Kissel/Negrut paper/code
lineage is summarized separately in
`KISSEL_NEGRUT_CODE_INVENTORY.md` so the manuscript keeps the 2021, 2022,
2023/2024, and 2024 performance-comparison sources distinct.

## Local Source Directories

Path convention: the paths in this section are relative to the
`validation` root, which is the base used by v048 and by the
cross-paper validators. From this paper subdirectory, prepend one additional
`../`.

- 2021 rA/rp/r-epsilon public-code suite:
  `../external/sbel-reproducibility/2021/ASME/rA-formulation`
- 2022 half-implicit public-code suite:
  `../external/sbel-reproducibility/2022/HalfImplicit_JCND`
- 2024 Kissel/Bakke/Negrut velocity-partitioning Lie-group ODE paper:
  DOI `10.1115/1.4065254`; code path unresolved after local
  `sbel-reproducibility` and `public-metadata` `origin/master` plus
  `origin/user/aaron/msd` tree searches, and after public web search.
- Original TFE paper PDF:
  `../../external/literature/s11044-026-10153-w.pdf`

## 2021 Kissel/Taves/Negrut rA Suite

Source files inspected:

- `C2/SimEngineMBD/example_models/single_pendulum.py`
- `C2/SimEngineMBD/example_models/double_pendulum.py`
- `C2/SimEngineMBD/example_models/four_link.py`
- `C2/SimEngineMBD/example_models/slider_crank.py`
- `profiling_scripts/order_analysis.sh`
- `profiling_scripts/time.sh`
- `profiling_scripts/check_iters.sh`

Extracted benchmark policy:

- Forms: `rA`, `rp`, `reps`.
- Order-analysis models: `single_pendulum`, `four_link`, `slider_crank`.
- Timing/iteration models: `single_pendulum`, `double_pendulum`,
  `four_link`, `slider_crank`.
- Kinematic reference generation in `order_analysis.sh` uses
  `--mode kin --tol 1e-12 --save_data`.
- Dynamics order-analysis step sizes are `1e-2`, `1e-3`, and `1e-4`.
- Timing script uses `--end_time 3 --step_size 1e-3 --tol 1e-10` in
  kinematics mode, skipping double-pendulum kinematics.
- Iteration script records `Avg. iterations:` for kinematics and dynamics.

Parameter identity status versus current v047:

| Model | Public-code facts | Current v047 status |
| --- | --- | --- |
| `single_pendulum` | Length `4` m, side `0.05` m, density `7800`, gravity `9.81`, DP1 drive `cos(pi/2 + pi/4*cos(2*t))`. | Geometry and drive match; v047 uses `t_f=0.2`, `h={0.20,0.10,0.05}` and analytic reference, so it is not the public-code order/timing campaign. |
| `double_pendulum` | Bar lengths `4` m and `2` m, side `0.05` m, density `7800`, gravity `9.81`, two revolute joints, zero initial angular velocities. | Geometry/topology match; v047 regularizes angular speeds to `+/-1e-12` and uses nested local FullVA `h=0.005`, so the reference policy is different. |
| `four_link` | Three bodies, masses `2,1,1`, inertia diagonals `(4,2,0)`, `(12.4,0.01,0)`, `(4.54,0.01,0)`, driver `cos(pi*t + pi/2)`. | Model graph and parameter values match the 2021 C2 source; v047 uses local kinematic FullVA `t_f=0.2`, `h={0.02,0.01,0.005}`, reference `h=0.001`, not the `rA/rp/reps` public-code order campaign. |
| `slider_crank` | 2021 C2 masses `0.12,0.5,2`, inertia diagonals `(1e-4,1e-5,1e-4)`, `(4e-3,4e-4,4e-3)`, `(1e-4,1e-4,1e-4)`, driver `cos(-2*pi*t + pi/2)`. | Graph and parameter values match the 2021 C2 source; v047 uses local kinematic FullVA `t_f=0.2`, `h={0.02,0.01,0.005}`, reference `h=0.001`, not the public-code order/timing campaign. |

Required v047 external rows:

- Run `Gauss6/FullVA` on the 2021 public-code time windows and step sizes.
- Report the same scalar outputs used in the public scripts: order-analysis
  differences, `Avg. iterations:`, and `Simulation time:`.
- Compare against `rA`, `rp`, and `reps`; do not collapse them into one
  baseline.

Current v048 executable evidence:

- The full public-code baseline run completes all 2021 `rA/rp/reps`
  `single_pendulum`, `four_link`, and `slider_crank` step-size trios at
  `T=3`, `h=[1e-2,1e-3,1e-4]`; this is 27/27 ok rows and 9/9 public-order
  groups.
- The bounded `Gauss6/FullVA` same-mechanism pilot completes 3/3 rows for the
  same 2021 single-pendulum setup at `T=0.2`, `h=[0.2,0.1,0.05]`, with
  position/velocity/orientation/omega observed orders
  `6.073/6.033/6.055/6.024`.
- The public-horizon `Gauss6/FullVA` single-pendulum tranche completes 3/3
  rows at the actual public time window `T=3` and public step sizes
  `h=[1e-2,1e-3,1e-4]`; the finest row has position/velocity errors
  `2.584e-14/7.012e-15`, 30000 Newton iterations, and runtime `76.625s`.
  The final-error orders are roundoff/reference-floor limited, so this closes the single-pendulum public-policy row set but not the external campaign.
- The bounded `Gauss6/FullVA` closed-loop residual pilot completes 6/6 rows
  for the 2021 `four_link` and `slider_crank` mechanisms at `T=0.2`,
  `h=[0.02,0.01,0.005]`, reference `h=0.001`. It verifies constraint,
  SO(3), and Newton-Euler reaction residuals with max dynamics residuals
  `1.338e-13` and `6.492e-15`, but it is not dynamic order or work evidence.
- The public-horizon `Gauss6/FullVA` closed-loop residual tranche completes
  6/6 rows for the same two mechanisms at `T=3` and public step sizes
  `h=[1e-2,1e-3,1e-4]`. The finest `h=1e-4` rows have max dynamics residuals
  `5.136e-13` and `1.113e-14`, runtimes `73.25s` and `89.49s`, and are
  generated through shard/merge entry points that allow independent rows to run
  in parallel. These are still constraint/reaction residual rows, not public
  dynamic order/work rows.
- The public-horizon double-pendulum `Gauss6/FullVA` coarse tranche completes
  3/3 rows at `T=3`, `h=[0.1,0.05,0.025]`, reference `h=0.0125`, with
  position/velocity orders `7.951/7.042`. Its max endpoint residuals
  `1.131e-05/3.533e-04` keep it as coarse-first order/work evidence rather
  than the public `1e-4` policy or an external superiority row.
- v048 now also writes the matching coarse same-window public double-pendulum
  baseline rows in `ra2021_double_pendulum_coarse_order_rows.csv`:
  `rA/reps` complete 6/6 rows with position/velocity orders `0.703/0.754`,
  while `rp` records three Newton nonconvergence rows. The derived
  `double_pendulum_coarse_same_window_work_precision_summary.csv` puts those
  public rows beside the coarse `Gauss6/FullVA` tranche without treating the
  result as the source `1e-4` policy.
- The selected closed-loop same-window comparison completes 12/12 rows for
  public `rA` dynamics versus local `Gauss6/FullVA` residual rows on the same
  two mechanisms, using the same `T=0.2`, `h=[0.02,0.01,0.005]`, and
  public-kinematic-reference final-error/work columns. It is closer to the
  source table shape, but remains selected-window evidence rather than the
  exact public `T=3`, `h=[1e-2,1e-3,1e-4]` campaign.
- v048 now also writes `ra2021_public_order_work_summary.csv` and
  `gauss6_closed_loop_same_window_work_precision_summary.csv` as paper-table
  helpers over the recorded raw rows.
- v048 now also writes `ra2021_double_pendulum_order_rows.csv`; it completes
  9/9 public `double_pendulum` dynamic self-reference order rows for
  `rA/rp/reps` at `T=3`, `h=[1e-2,2e-3,1e-3]`, reference `h=1e-4`. This
  fills the public-code double-pendulum order gap, but it is not the
  kinematic-reference policy used by `order_analysis.py`.
- v048 now also completes `ra2021_public_timing_rows.csv` as a 12/12
  timing/iteration policy table for `rA/rp/reps` on all four examples at
  `T=3`, `h=1e-3`, using shard/merge entry points. These rows provide public
  baseline work metrics; they do not replace dynamic order rows for the local
  `Gauss6/FullVA` method.
- v048 also writes `four_example_performance_matrix.csv`,
  `four_example_performance_summary.json`, and
  `four_example_performance_matrix.md`; the current matrix has 48 rows,
  32 completed rows, 0 partial rows, and no external superiority claim.
- The bounded 2022 half-implicit public-code/state-history pilot completes
  24/24 rows and 8/8 `rA/rA_half` model-form trios for `single_pendulum`,
  `double_pendulum`, `four_link`, and `slider_crank` at `T=0.1`,
  `h=[0.02,0.01,0.005]`. This expands executable coverage, but the full
  `T=8` 2022 convergence figure remains open.
- The public reference at `h=1e-3` aligns with the v047 analytic state at
  about `7e-10` or better in position, velocity, and acceleration. This
  supports mechanism alignment for one bounded row set, not the completed full
  public-code policy.

## 2022 Fang/Kissel/Zhang/Negrut Half-Implicit Suite

Source files inspected:

- `run_double_pendulum_ode.py`
- `run_double_pendulum_dae.py`
- `plot_convergence_open_loop.py`
- `run_closed_loop_setups.py`
- `plot_convergence_closed_loop.py`
- `run_num_itr.py`
- `plot_double_pendulum_energy.py`
- `run_scaling_analysis.py`
- `run_slider_crank_frictional.py`
- `SimEngineMBD/example_models/slider_crank.py`

Extracted benchmark policy:

- Forms: `rA_half` and `rA`, labelled half-implicit and fully implicit.
- Open-loop double-pendulum reference: ODE solution with `dt_exact=1e-6`,
  `t_end=8`.
- Open-loop and closed-loop convergence step sizes:
  `1e-4`, `2e-4`, `4e-4`, `1e-3`, `2e-3`, `4e-3`, `1e-2`, `2e-2`,
  `4e-2`.
- DAE tolerance policy: base tolerance `1e-10`; fully implicit `rA` uses
  `tolerance/step_size**2`, while `rA_half` uses the base tolerance.
- Closed-loop reference: kinematic `rA` reference with `tol_ref=1e-10`,
  `dt_ref=1e-5`, `t_end=8`.
- Work comparison: timing/iteration rows at step sizes `1e-4`, `1e-3`,
  and `1e-2` with model-specific hand-picked tolerances.
- Energy figure: double pendulum, `step_size=1e-3`, `t_end=10`, forms
  `rA_half` and `rA`.
- Scaling figure: `N={2,4,6,8,16,32}` pendulum, `step_size=1e-3`,
  `t_end=3`, tolerances `1e-7` for `rA_half` and `1e-5` for `rA`.
- Frictional slider-crank figure: `rA_half`, `step_size=1e-3`,
  `t_end=2`, tolerance `1e-10`, friction coefficients `0`, `0.2`, and
  `0.4`.

Important parameter distinction:

- The 2021 rA slider-crank code uses crank mass `0.12`.
- The 2022 half-implicit slider-crank code uses crank mass `1.2`.
- These are separate baselines. A valid paper comparison must not merge the
  2021 rA suite and the 2022 half-implicit suite into one shared slider-crank
  parameter set.

Required v047 external rows:

- Run `Gauss6/FullVA` on the 2022 double-pendulum ODE-reference test.
- Run `Gauss6/FullVA` on the 2022 four-link and slider-crank closed-loop
  convergence tests with `t_end=8` and `dt_ref=1e-5`.
- Add energy behavior for the double pendulum at `h=1e-3`, `t_end=10`.
- Add CPU-time and average-iteration rows at the three timing step sizes.
- Add a frictional slider-crank response row for `mu={0,0.2,0.4}`.

## 2024 Kissel/Bakke/Negrut Velocity-Partitioning Lie-Group ODE Suite

Alias: Velocity-partitioning Lie-group ODE suite.

Source status:

- Paper: "Reducing the Constrained Multibody Dynamics Problem to the Solution
  of a System of Ordinary Differential Equations Via Velocity Partitioning and
  Lie Group Integration", DOI `10.1115/1.4065254`.
- Related source family: the 2023 ASME IDETC-CIE velocity-partitioning paper
  and the 2024 EasyChair performance-comparison preprint should be tracked as
  separate literature/code claims. The 2024 preprint compares fully implicit,
  half-implicit, and velocity-coordinate-partitioning Lie-group approaches,
  reports a double-pendulum order analysis and an N-body pendulum scaling
  analysis, and states that the Python code is open source.
- Public-code status: the paper and the 2024 performance-comparison preprint
  report open-source Python code for reproducibility, but a distinct
  velocity-partitioning public-code directory has not yet been resolved in the
  local `sbel-reproducibility` or `public-metadata` `origin/master` or
  `origin/user/aaron/msd` trees, nor by the public web search.
- Code-search artifact: v048 writes
  `../../numerics/v048_cross_paper_same_test_benchmarks/results/velocity_partitioning_code_search.csv`.
  That artifact records the literature code claim, the EasyChair PDF reference
  check showing the visible repository reference points to the 2021
  `rA-formulation` public metadata path, a public web search with no distinct
  velocity-partitioning repository found, and both public SBEL tree mirrors
  over `origin/master` plus `origin/user/aaron/msd`. It rejects 2024
  mechanism-name hits as unrelated MBD-NODE, PathFollowingSim2real, or
  RSSworkshop paths rather than this velocity-partitioning baseline.
- Current inventory row: `vp2024_velocity_partitioning_code_resolution` in
  `CROSS_PAPER_BENCHMARK_CASES.json`.

Extracted benchmark policy:

- Mechanism family: single pendulum, double pendulum, four-link, and
  slider-crank.
- Comparison family: velocity-partitioning Lie-group ODE method against a
  coordinate-partitioning Euler-parameter formulation.
- Expected reported quantities: convergence order and performance comparison.
- Current status: code path unresolved; no v047 same-test row may be claimed
  until the public code location, step-size sweep, tolerance policy, reference
  policy, and output metrics are resolved.

Required v047 external rows:

- Resolve the public code path and source scripts.
- Split the placeholder case into concrete convergence and work/performance
  rows before using it as a numerical baseline.
- Do not merge this with the 2021 `rA/rp/reps` public-code suite or the 2022
  half-implicit suite.

## Original Chaturvedi/Sandu/Sandu TFE Suite

Source files inspected:

- `../../external/literature/s11044-026-10153-w.pdf`
- `../../external/literature/s11044-026-10153-w.txt` when available.

Required v047 external rows:

- Rigid pendulum without joint friction.
- Rigid pendulum with joint friction.
- TFE `m=1`, `m=2`, and `m=3`.
- Newmark-beta and trapezoidal baselines.
- Same position/velocity error definitions, same reference policy, same
  large-step stability checks, and same cost metrics used by the source
  paper.

Current status:

- The local cylindrical-chain all-row TFE diagnostic is not this pendulum
  reproduction.
- The exact TFE same-test rows remain open.

## Current Gate

The paper can state that the same-test benchmark specification has been
extracted. It cannot state that the external same-test benchmark campaign has
passed.

The paper can also state that v048 has produced one bounded 2021
single-pendulum public-code pilot, one bounded `Gauss6/FullVA`
same-mechanism pilot, and selected closed-loop residual evidence for the 2021
`four_link` and `slider_crank` mechanisms, including a public-horizon
closed-loop residual tranche. It still cannot state
external-method superiority.

The next executable gate is to run the cases listed in
`CROSS_PAPER_BENCHMARK_CASES.json` or to explicitly demote any unresolved
paper-code source from the external same-test comparison.
