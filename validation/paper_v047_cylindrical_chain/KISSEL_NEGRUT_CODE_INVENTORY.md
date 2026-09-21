# Kissel/Negrut Public-Code Inventory

Status: **multi-paper code family identified; full same-test campaign open**

This inventory prevents the manuscript from treating the Kissel/Negrut line as
one paper or one baseline. Each paper/code claim must become its own benchmark
row before an external superiority claim is defensible.

Path convention: `../external/...` entries below are resolved from the
`validation` root, as in the v048 runner and validators. From
this paper subdirectory, the same filesystem targets are under
`../../external/...`.

External-source check on 2026-05-31: the 2022 `rA/rp/reps` journal article,
the 2023 half-implicit article, the 2024 velocity-partitioning article, and the
2024 EasyChair performance-comparison preprint are separate source claims. The
first two public-code suites are present locally in the SBEL reproducibility
mirror at commit `4a49529b55a7d984d9388e724760842f9a24b0f6`. The 2024
velocity-partitioning/performance-comparison sources state that Python code is
open-source, but v048 has not resolved a distinct public-code directory for
that baseline after checking the EasyChair PDF reference, public web-search
queries, and the `origin/master` and `origin/user/aaron/msd` trees of both
local SBEL mirrors.

## Inventory

| Source | Method family | Code status in this workspace | Required comparison action |
| --- | --- | --- | --- |
| Kissel--Taves--Negrut TR-2020-08 and ASME 2021 Part 1/Part 2 | Fully implicit absolute-coordinate Lie-group `rA`; comparison against `rp` and `reps` | Present through `../external/sbel-reproducibility/2021/ASME/rA-formulation` | Run the public `single_pendulum`, `four_link`, and `slider_crank` order rows for `rA/rp/reps`, plus timing/iteration rows for all four mechanisms. |
| Kissel--Taves--Negrut JCND 2022 | Same `rA/rp/reps` absolute-coordinate comparison consolidated as the journal article | Present through the same 2021 public-code suite | Treat as the journal-facing citation for the 2021 public-code suite, not as a separate parameter set. |
| Fang--Kissel--Zhang--Negrut JCND 2023, "On the Use of Half-Implicit Numerical Integration in Multibody Dynamics" | Half-implicit `rA_half` versus fully implicit `rA` | Present through `../external/sbel-reproducibility/2022/HalfImplicit_JCND` | Run the published double-pendulum ODE-reference convergence, closed-loop four-link/slider-crank convergence, energy, timing/iteration, N-pendulum scaling, and frictional slider-crank tests. |
| Kissel--Fang--Negrut ASME 2023 | Velocity partitioning in the `rA` formulation | Literature source identified; distinct public-code directory not resolved locally | Resolve the code path before turning this into numerical rows. |
| Kissel--Bakke--Negrut JCND 2024 | Velocity-partitioning Lie-group ODE method | Paper reports public code, but no distinct velocity-partitioning directory is resolved in local `sbel-reproducibility` or `public-metadata` searches over `origin/master` and `origin/user/aaron/msd` | Keep as `code_path_unresolved`; do not claim comparison until scripts, step sizes, tolerances, references, and metrics are extracted. |
| Kissel--Bakke--Negrut EasyChair Preprint 13546, 2024 | Direct performance comparison of fully implicit, half-implicit, and velocity-coordinate-partitioning Lie-group approaches | Preprint reports open-source Python code; the visible repository reference points to the 2021 `rA-formulation` public metadata entry, and public web search did not expose a separate velocity-partitioning repo | Track its double-pendulum order analysis and N-body pendulum scaling as separate rows only after the code path is resolved. |

## Current v048 Evidence

- 2021 public-code baseline: 27/27 completed rows over all `rA/rp/reps`
  `single_pendulum`, `four_link`, and `slider_crank` order groups, covering
  9/9 public-order groups.
- 2021 selected `Gauss6/FullVA` pilot: 3/3 rows on the same single-pendulum
  mechanism, with position/velocity/orientation/omega observed orders
  `6.073/6.033/6.055/6.024`.
- 2021 public-horizon `Gauss6/FullVA` single-pendulum tranche: 3/3 rows at
  the actual public time window `T=3` and public step sizes `h=[1e-2,1e-3,1e-4]`;
  the finest row has position/velocity errors `2.584e-14/7.012e-15`, 30000 Newton iterations, and
  runtime `76.625s`. The final-error orders are roundoff/reference-floor limited, so this closes the single-pendulum public-policy row set but not the external campaign.
- 2021 selected closed-loop `Gauss6/FullVA` rows: 6/6 rows on the public
  `four_link` and `slider_crank` mechanisms at `T=0.2`,
  `h=[0.02,0.01,0.005]`, reference `h=0.001`. These verify constraint,
  SO(3), and Newton-Euler reaction residuals, with max dynamics residuals
  `1.338e-13` and `6.492e-15`; they are not dynamic order or work rows.
- 2021 public-horizon closed-loop `Gauss6/FullVA` residual tranche: 6/6 rows
  on the same two mechanisms at `T=3`, `h=[1e-2,1e-3,1e-4]`. The finest
  `h=1e-4` rows have max dynamics residuals `5.136e-13` and `1.113e-14`,
  runtimes `73.25s` and `89.49s`, and were generated through shard/merge
  entry points that can run independent rows in parallel. They remain
  constraint/reaction residual rows, not dynamic order or work rows.
- 2021 selected same-window closed-loop comparison: 12/12 rows comparing
  public `rA` dynamics and local `Gauss6/FullVA` residual rows under the same
  `T=0.2`, `h=[0.02,0.01,0.005]`, public-kinematic-reference final-error/work
  columns. This is useful table-shape evidence but still not the exact public
  `T=3`, `h=[1e-2,1e-3,1e-4]` dynamic campaign.
- Derived manuscript-table summaries: 9-row public order/work summary and
  4-row selected same-window work/precision summary. These summarize accepted
  raw rows and do not change the claim boundary.
- Four-example performance coverage ledger: 48 method/example rows, 31
  completed rows, and 0 partial rows, with `external_superiority_claim=false`.
- 2022 half-implicit four-example pilot: 24/24 rows and 8/8 `rA/rA_half`
  model-form trios on `single_pendulum`, `double_pendulum`, `four_link`, and
  `slider_crank` at `T=0.1`, `h=[0.02,0.01,0.005]`. This is source-wiring
  evidence; the full `T=8` convergence figure remains open.
- 2024 velocity-partitioning path: unresolved; v048 records the EasyChair PDF
  reference check, public web search, and local Git-tree searches in
  `../../numerics/v048_cross_paper_same_test_benchmarks/results/velocity_partitioning_code_search.csv`.

## Manuscript Rule

The CMAME manuscript may cite these sources as related work and may report the
bounded v048 pilots as reproducibility progress. It must not claim that
`Gauss6/FullVA` beats the Kissel/Negrut family until each public-code test is
run on the same parameters, time windows, step sizes, tolerance policies,
reference solutions, error norms, and work metrics.
