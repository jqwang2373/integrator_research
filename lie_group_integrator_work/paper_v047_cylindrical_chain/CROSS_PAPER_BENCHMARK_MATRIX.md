# Cross-Paper Benchmark Matrix

Status: **open pre-submission gate**

This file records the external same-test comparisons that must be completed
before the CMAME manuscript can be called submission-ready. Mechanism names are
not enough. A comparison counts only when the model parameters, initial
conditions, prescribed drivers, friction law, step-size sweep, nonlinear
tolerance policy, reference solution, error norm, and work metric match the
source paper or are explicitly justified.

The concrete source-code extraction is in `CROSS_PAPER_BENCHMARK_SPEC.md`.
That file records the current status as **spec extracted, partial evidence
recorded, full same-test campaign not yet run**.

The row-level run list is in `CROSS_PAPER_BENCHMARK_CASES.json`. It separates
paper families, public-code suites, and unresolved public-code claims so that
the manuscript cannot collapse several Kissel/Negrut-related papers into one
baseline. Its case statuses describe the full source-policy rows, while its
`partial_evidence_overlay` records existing coarse-first/bounded evidence and
keeps `default_1e-4_required=false`.

The Kissel/Negrut literature/code family is also summarized in
`KISSEL_NEGRUT_CODE_INVENTORY.md`. That inventory is the guardrail for keeping
the 2021 fully implicit `rA/rp/reps`, the 2022 half-implicit suite, the
2023/2024 velocity-partitioning work, and the 2024 performance-comparison
preprint as separate comparison targets.

## Source-Paper TFE Suite

Primary source:

- E. Chaturvedi, C. Sandu, A. Sandu, "Higher-order integration of index-3 DAE
  with friction using time finite elements on Lie groups", Multibody System
  Dynamics, 2026, DOI 10.1007/s11044-026-10153-w.

Required reproductions:

- Rigid pendulum without joint friction.
- Rigid pendulum with joint friction.
- TFE `m=1`, `m=2`, and `m=3`.
- Newmark-beta and trapezoidal comparators.

Required metrics:

- Position and velocity error/order versus the paper reference policy.
- Newton iterations and condition/cost diagnostics where reported.
- Energy or trajectory diagnostics used in the source figures.
- Stability at the large step sizes used for the source comparison.

Current v047 status:

- The manuscript has a local cylindrical-chain all-row TFE diagnostic.
- It does not yet reproduce the published pendulum tests.
- It does not yet compare against the published Newmark-beta/trapezoidal rows.

## Kissel/Taves/Negrut rA Suite

Primary sources:

- J. Taves, A. Kissel, D. Negrut, "On an exponential map approach for rigid
  body kinematics and dynamics analysis", SBEL Technical Report TR-2020-08,
  2020.
- A. Kissel, D. Negrut, J. Taves, "Dwelling on the connection between SO(3)
  and rotation matrices in rigid multibody dynamics. Part 1: Description of an
  index-3 DAE solution approach", ASME IDETC-CIE, 2021.
- A. Kissel, D. Negrut, J. Taves, "Constrained multibody kinematics and
  dynamics in absolute coordinates: a discussion of three approaches to
  representing rigid body rotation", Journal of Computational and Nonlinear
  Dynamics 17(10), 101008, 2022.

Public code entry:

- `https://github.com/uwsbel/public-metadata/tree/master/2021/ASME/rA-formulation`

Required reproductions:

- Single pendulum.
- Double pendulum.
- Slider-crank.
- Four-link.
- The C1/C2 model definitions and scripts should be treated as the source of
  truth.

Required metrics:

- Order/error against the paper's kinematics or ODE reference.
- Runtime and Newton iteration comparisons against `rA`, `rp`, and
  `r-epsilon`.
- Constraint drift and orientation orthogonality where available.

Current v047 status:

- v047 uses the same four mechanism names, but the current manuscript has not
  certified identity of model JSON parameters, drivers, reference policies, or
  error metrics.
- This is the highest-priority external comparison gap.

Current v048 executable evidence:

- The public-code runner has completed all 2021 `rA/rp/reps` order-analysis
  groups for `single_pendulum`, `four_link`, and `slider_crank` at `T=3`,
  `h=[1e-2,1e-3,1e-4]`, giving 27/27 ok rows and 9/9 completed
  public-order groups.
- The selected `Gauss6/FullVA` same-mechanism pilot has completed 3/3
  single-pendulum rows at `T=0.2`, `h=[0.2,0.1,0.05]`, with
  position/velocity/orientation/omega observed orders
  `6.073/6.033/6.055/6.024`.
- The public-horizon `Gauss6/FullVA` single-pendulum tranche has completed
  3/3 rows at the actual 2021 public time window `T=3` and public step sizes
  `h=[1e-2,1e-3,1e-4]`; the finest row has position/velocity errors
  `2.584e-14/7.012e-15`, 30000 Newton iterations, and runtime `76.625s`.
  The final-error orders are roundoff/reference-floor limited, so this closes the single-pendulum public-policy row set but not the external campaign.
- The selected closed-loop `Gauss6/FullVA` residual rows have completed 6/6
  rows on the 2021 `four_link` and `slider_crank` mechanisms at `T=0.2`,
  `h=[0.02,0.01,0.005]`, reference `h=0.001`, with max dynamics residuals
  `1.338e-13` and `6.492e-15`. These are public-mechanism constraint/reaction
  residual rows, not dynamic order or work rows.
- The public-horizon closed-loop `Gauss6/FullVA` residual tranche has
  completed 6/6 rows for the same two mechanisms at `T=3` and public step
  sizes `h=[1e-2,1e-3,1e-4]`; the finest `h=1e-4` rows have max dynamics
  residuals `5.136e-13` and `1.113e-14` with runtimes `73.25s` and `89.49s`.
  These rows were generated through independent shard/merge entry points so
  model/step-size rows can be run in parallel. They are still
  constraint/reaction residual rows, not public dynamic order or work rows.
- The selected-window closed-loop dynamic error floor audit now adds two
  rows for `four_link` and `slider_crank`: both have velocity/acceleration
  evidence below the public dynamics scale, both retain a position/reference
  floor blocker, and `accepted_dynamic_order_count=0`.
- The closed-loop coarse dynamic-order probe repeats the same diagnostic at
  larger steps `T=0.2`, `h=[0.1,0.05,0.025]`, reference `h=0.0125`. It has
  `11/12` rows ok, one public `slider_crank`/`rA` failure at `h=0.1`, local
  velocity/acceleration evidence for both mechanisms, two local position-floor
  rows, and `accepted_dynamic_order_count=0`. This is useful diagnostic
  evidence, but it still does not supply accepted dynamic order/work rows for
  `four_link` or `slider_crank`.
- The public-horizon double-pendulum `Gauss6/FullVA` coarse tranche now
  completes 3/3 rows at `T=3`, `h=[0.1,0.05,0.025]`, reference `h=0.0125`,
  with position/velocity orders `7.951/7.042`. Its max endpoint residuals
  `1.131e-05/3.533e-04` make it coarse-first order/work evidence, not the
  public `1e-4` policy.
- The matching coarse same-window public double-pendulum baseline rows now
  record `rA/reps` as 6/6 ok rows with position/velocity orders
  `0.703/0.754`; `rp` records three Newton nonconvergence rows. The new
  `double_pendulum_coarse_same_window_work_precision_summary.csv` aligns
  those public rows with the coarse `Gauss6/FullVA` tranche, still without
  claiming external superiority.
- The selected same-window closed-loop comparison has completed 12/12 rows for
  public `rA` dynamics and local `Gauss6/FullVA` residual rows under the same
  `T=0.2`, `h=[0.02,0.01,0.005]`, public-kinematic-reference final-error/work
  columns. It does not replace the full `T=3` public dynamic order/work
  campaign.
- v048 derives a 9-row 2021 public order/work summary and a 4-row selected
  same-window work/precision summary for manuscript tables.
- v048 now also completes the 12/12 2021 public timing/iteration policy rows
  for `rA/rp/reps` on all four examples at `T=3`, `h=1e-3`; these are public
  baseline work rows and not local `Gauss6/FullVA` dynamic order rows.
- v048 also writes a four-example performance coverage matrix with 48
  method/example rows, 32 completed rows, and 0 partial rows. It is a coverage
  ledger and keeps `external_superiority_claim=false`.
- The selected 2022 half-implicit public-code pilot has completed 6/6
  `double_pendulum` rows for `rA/rA_half` at `T=0.1`,
  `h=[0.02,0.01,0.005]`; the `rA_half` bounded diagnostic has negative
  observed order and remains a caveat rather than accepted convergence.
- The 2021 public-code baseline order table is complete; the remaining open
  work is to run `Gauss6/FullVA` dynamic order/work rows beyond the selected
  single-pendulum and closed-loop residual pilots and to complete the other
  source suites.

## Fang/Kissel/Zhang/Negrut Half-Implicit Suite

Primary source:

- L. Fang, A. Kissel, R. Zhang, D. Negrut, "On the use of half-implicit
  numerical integration in multibody dynamics", Journal of Computational and
  Nonlinear Dynamics 18(1), 014501, 2023, DOI 10.1115/1.4056183.

Public code entry:

- `https://github.com/uwsbel/public-metadata/tree/master/2022/HalfImplicit_JCND`

Required reproductions:

- Double pendulum.
- Slider-crank.
- Four-link.
- N-pendulum scaling.
- Slider-crank with joint friction.

Required metrics:

- Half-implicit versus fully implicit observed order.
- Energy behavior on the double pendulum.
- CPU time and Newton iteration counts for the reported step sizes.
- Frictional slider-crank response with the same friction coefficients.

Current v047 status:

- No same-test Gauss6/FullVA runs have been reported for this suite.

## Kissel/Bakke/Negrut Velocity-Partitioning Suite

Primary source:

- A. Kissel, L. Bakke, D. Negrut, "Reducing the Constrained Multibody Dynamics
  Problem to the Solution of a System of Ordinary Differential Equations Via
  Velocity Partitioning and Lie Group Integration", Journal of Computational
  and Nonlinear Dynamics 19(7), 2024, DOI 10.1115/1.4065254.

Related source family:

- A. Kissel, L. Fang, D. Negrut, "Using velocity partitioning in the rA
  formulation to solve the equations of constrained multibody dynamics",
  ASME IDETC-CIE, 2023.
- A. Kissel, L. Bakke, D. Negrut, "A Performance Comparison of Several Lie
  Group Integration Methods for Solving the Equations of Constrained
  Multibody Dynamics", EasyChair Preprint 13546, 2024. This preprint states
  that the fully implicit, half-implicit, and velocity-coordinate-partitioning
  Lie-group approaches are compared, uses a double-pendulum order analysis and
  an N-body pendulum scaling analysis, and reports open-source Python code.

Code status:

- The paper reports open-source Python code for reproducibility studies.
- The 2024 performance-comparison preprint also reports open-source Python
  code and its visible public-repository reference points to the 2021
  `rA-formulation` entry.
- A separate velocity-partitioning public-code directory for this paper has not
  been resolved in the local `sbel-reproducibility` or `public-metadata`
  `origin/master` or `origin/user/aaron/msd` trees, or by the public web
  search. v048 records this as
  `velocity_partitioning_code_search.csv`.

Required reproductions:

- Resolve the public-code path.
- Split the current placeholder
  `vp2024_velocity_partitioning_code_resolution` case from
  `CROSS_PAPER_BENCHMARK_CASES.json` into concrete convergence and performance
  rows for the single pendulum, double pendulum, four-link, and slider-crank
  tests.

Current v047 status:

- The code path is unresolved (`code path unresolved`). No same-test comparison
  to this paper is claimed.

## Paper Gate

The CMAME paper should not claim an external-method superiority result until
the rows above are filled with actual measurements. Until then, the accepted
claim remains the narrower internal result:

- `Gauss6/FullVA` has an accepted sixth-order method path.
- The local `m=3` Gauss-Lobatto TFE formula target has expected order five.
- The selected v048 2021 single-pendulum pilot and the completed exact
  public-horizon single-pendulum trio are useful first evidence, but they are not the
  completed external same-test campaign. The selected v048 four-link/slider-crank
  closed-loop rows and public-horizon closed-loop residual tranche are useful
  residual evidence, but they are not dynamic order/work rows.
- The full external same-test comparison remains open.
