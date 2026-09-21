# Source Paper Versus v047

This note fixes the comparison boundary between the local source paper and the
accepted v047 claim. It is intentionally narrow: it answers what order is being
compared, what method is accepted here, and what is not claimed.

## Source Paper Target

- Local source file: `../../external/literature/s11044-026-10153-w.pdf`
- Topic: higher-order integration of index-3 DAEs with friction using time
  finite elements on Lie groups.
- PDF sections read: Section 1 frames Lie-group DAE integration with friction;
  Section 2 derives the absolute-coordinate frictional DAE; Section 3 derives
  the TFE weighted-residual discretization; Section 4 reports pendulum
  experiments; Section 5 gives conclusions.
- The source paper's TFE family lists `m=1`, `m=2`, and `m=3` coefficient sets.
- The order convention used for the paper-facing local target is `2m-1`.
- Therefore the local `m=3` Gauss-Lobatto TFE formula target has expected order
  `2m-1=5`.
- The source paper also reports that its DAE pendulum experiment can show order
  loss for `m=3` despite the `2m-1` formula order. The v047 comparison keeps
  the stronger formula-order target `5`; it does not compare against the
  weakened observed order-loss result.

The source paper has its own TFE implementation and numerical study. It does
not contain this repository's `Gauss6/FullVA` 132-row residual, and it does not
contain this repository's internal full-TFE replacement gate.

## Accepted v047 Claim

- Accepted method: `Gauss6/FullVA`
- Method-order claim: `6`
- Smooth observed position/velocity orders: `7.161/7.066`
- Comparator: local paper-style `m=3` Gauss-Lobatto TFE formula target with
  expected order `5`
- Local method-side coverage examples: `single_pendulum`, `double_pendulum`, `four_link`,
  `slider_crank`
- Accepted dynamic-order examples: `single_pendulum`, `double_pendulum`; the
  `four_link` and `slider_crank` rows are mechanism-coverage rows, not
  accepted external dynamic-order rows.

The accepted claim is therefore a formal-order alternative claim: the accepted
`Gauss6/FullVA` path has method-order claim six and is compared only against a
local paper-style order-five formula target. This is not an implemented
source-paper superiority claim.

The example-level order boundary is machine-readable in
`ORDER_ACCEPTANCE_GATE.json` and summarized in `ORDER_ACCEPTANCE_GATE.md`.
It states that `single_pendulum` and `double_pendulum` currently support
accepted dynamic order rows, while `four_link` and `slider_crank` are accepted
as mechanism coverage with closed-loop kinematic/reaction evidence but not as
accepted external dynamic-order rows.

## Implemented Diagnostic Comparator

The current manuscript also reports an implemented source-paper TFE all-row
diagnostic on the same smooth cylindrical-chain h values. It uses terminal
Lobatto-node output, a consistent initial `z0` policy, and equilibrated Newton
linear solves. The recorded diagnostic orders are:

- position order: `4.046`
- velocity order: `4.420`

This diagnostic is useful because it is a same-problem implemented comparison,
but it is not an accepted fair baseline. The paper-derived recurrent start
policy and the full-TFE replacement gate remain open, so
`full_tfe_stage_replacement=false` is unchanged.

## Cross-Paper Same-Test Gap

The source-paper comparison is not complete until the accepted `Gauss6/FullVA`
integrator is run on the same numerical tests used by the external papers.
The required benchmark matrix is recorded in
`CROSS_PAPER_BENCHMARK_MATRIX.md`; the extracted public-code source facts are
recorded in `CROSS_PAPER_BENCHMARK_SPEC.md`. The row-level run inventory is
recorded in `CROSS_PAPER_BENCHMARK_CASES.json`.

Required external tests:

- Chaturvedi--Sandu--Sandu: rigid pendulum without and with joint friction,
  including `m=1`, `m=2`, `m=3` TFE, Newmark-beta, and trapezoidal rows.
- Kissel/Taves/Negrut: public-code `single_pendulum`, `double_pendulum`,
  `slider_crank`, and `four_link` model definitions for the `rA`, `rp`, and
  `r-epsilon` comparison.
- Fang/Kissel/Zhang/Negrut: public-code half-implicit versus fully implicit
  double-pendulum, slider-crank, four-link, N-pendulum scaling, and
  slider-crank friction tests.
- Kissel/Bakke/Negrut: velocity-partitioning Lie-group ODE tests. This paper
  reports open-source Python code, but the distinct public-code directory is
  still unresolved in the current local sparse checkout, so it is tracked as a
  code-resolution gate rather than completed numerical evidence.

The current v047 package has mechanism names that overlap with the
Kissel/Negrut papers, but it has not yet certified identity of parameters,
drivers, references, tolerances, error metrics, or work metrics. Therefore the
current manuscript does not yet support an external same-test superiority
claim. It only supports the narrower conditional formal-order comparison
stated above.

The current v048 harness has started that certification process but has not
finished it. It completes the full 2021 `rA/rp/reps` public-code order policy
for `single_pendulum`, `four_link`, and `slider_crank` as 27/27 rows and 9/9
public-order groups. It also completes a
bounded same-mechanism `Gauss6/FullVA` pilot on the 2021 single-pendulum setup
at `T=0.2`, `h=[0.2,0.1,0.05]`, with position/velocity/orientation/omega
orders `6.073/6.033/6.055/6.024`. Because that pilot covers only one
mechanism and does not cover the remaining source suites, the required
machine-readable flags remain `same_test_campaign_status=not_run` and
`external_superiority_claim=false`.

The order-acceptance gate also records the coarse closed-loop probe at `T=0.2`,
`h=[0.1,0.05,0.025]`, reference `h=0.0125`: it has `11/12` ok rows, one
public `slider_crank`/`rA` failure at `h=0.1`, two local velocity/acceleration
evidence rows, two position-floor blockers, and
`accepted_dynamic_order_count=0`. This preserves the coarse-first policy and
keeps strict public `1e-4` rows opt-in only.

The same layer now also records the 3/3 exact public-horizon single-pendulum
`Gauss6/FullVA` step-size trio at `T=3`, `h=[1e-2,1e-3,1e-4]`, reference `h=1e-3`;
the finest row has position/velocity errors `2.584e-14/7.012e-15`, 30000 Newton iterations, and
runtime `76.625s`. The final-error orders are roundoff/reference-floor limited, so this closes the single-pendulum public-policy row set but not the external campaign.

The same v048 layer also completes 6/6 selected closed-loop
`Gauss6/FullVA` rows on the 2021 `four_link` and `slider_crank` mechanisms at
`T=0.2`, `h=[0.02,0.01,0.005]`, reference `h=0.001`. These rows verify
constraint, SO(3), and Newton-Euler reaction residuals on public mechanisms
with max dynamics residuals `1.338e-13` and `6.492e-15`; they are not dynamic
order or work rows and therefore do not close the external same-test gate.

The same v048 layer now also records a coarse public-horizon double-pendulum
`Gauss6/FullVA` tranche at `T=3`, `h=[0.1,0.05,0.025]`, reference `h=0.0125`.
The observed position/velocity orders are `7.951/7.042`; max endpoint
residuals are `1.131e-05/3.533e-04`. This is the cost-aware coarse-first
evidence path and is not the public `1e-4` policy or an external superiority
row.

The same large-step double-pendulum window now has public baseline rows:
`rA/reps` complete 6/6 rows at `T=3`, `h=[0.1,0.05,0.025]`, reference
`h=0.0125`, with position/velocity orders `0.703/0.754`, while `rp` records
three Newton nonconvergence rows. The derived work/precision summary places
these rows beside the coarse `Gauss6/FullVA` tranche, but this is still a
coarse diagnostic rather than the public `1e-4` source policy.

The same v048 layer now also writes 12/12 selected same-window comparison rows
for public `rA` dynamics versus local `Gauss6/FullVA` closed-loop residual
rows on those two mechanisms. The rows share `T=0.2`,
`h=[0.02,0.01,0.005]`, the public `rA` kinematic reference, and final
position/velocity/acceleration error/work columns. This is closer to the
source-paper table shape, but the `Gauss6/FullVA` rows remain local residual
rows and the exact public `T=3`, `h=[1e-2,1e-3,1e-4]` dynamic campaign remains
open.
For manuscript drafting, v048 also derives a 9-row public order/work summary
and a 4-row same-window work/precision summary from those raw artifacts. It
also completes the 12/12 2021 public timing/iteration policy rows for
`rA/rp/reps` on all four examples at `T=3`, `h=1e-3`; these are public
baseline work rows, not local `Gauss6/FullVA` dynamic order rows.

It also now runs the 2022 half-implicit `double_pendulum` public-code entry
points for `rA/rA_half` at `T=0.1`, `h=[0.02,0.01,0.005]`, producing 6/6 ok
rows. The bounded `rA_half` diagnostic has negative observed order under the
current short-window reference policy, so this is source-wiring evidence, not
accepted reproduction of the 2022 convergence figure.

## Not Claimed

- Complete source-paper residual reproduction is not claimed.
- Accepted independent full-TFE stage replacement is not claimed.
- `full_tfe_stage_replacement=false` remains the machine-readable boundary.
- Sparse AD being faster than dense `jacfwd` is not claimed.
- The practical coarse sharp-friction regime being solved is not claimed.

## Full-TFE Replacement Meaning Here

In this repository, full-TFE replacement means replacing the accepted
`Gauss6/FullVA` 132-row nonlinear stage residual with paper-derived
temporal-finite-element weak rows inside Newton, while avoiding endpoint source
data, terminal-row replacement, output projection, and target-direction oracle
information. That stronger source-paper reproduction gate is still open.
