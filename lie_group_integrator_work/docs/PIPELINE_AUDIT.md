# Pipeline Audit

This audit records how the historical versions line up with the per-version
completion gate adopted after v046.

## Gate

Each complete method version now needs:

- math proof/status in `ORDER_PROOF_LEDGER.md`;
- four ASME examples: single pendulum, double pendulum, four link, slider crank;
- convergence analysis with at least three step sizes;
- convergence and diagnostic plots;
- CSV, JSON summary, report, and ledger updates.

## Paper-Exceedance Gate

The research objective is to exceed the paper method, not merely to reproduce
the local v046/rA baseline. A version can claim paper-exceedance only when the
comparison scope is explicit and all evidence is generated under the current
pipeline gate:

- the comparator is named as either the local v046/rA reproduction baseline or
  the complete paper TFE formulation;
- the method passes all four ASME examples with the same h-sweep, reference,
  constraint, runtime, CSV, plot, and report discipline used for the method
  claim;
- the method shows higher order, lower error at comparable cost, or equal order
  with a clear accuracy/cost win in the smooth regimes;
- endpoint position, velocity, acceleration, and lower-pair constraints close
  at least as well as the comparator, with any projection or KKT closure
  explicitly audited;
- sharp-friction/coarse-regime behavior is either better than the comparator or
  its cost/order caveat is quantified;
- if the comparator is the complete paper TFE formulation, the independent
  full TFE stage replacement must be solved and accepted, not just represented
  by endpoint-node rows, diagonal-equivalent stage weighting, or
  endpoint-boundary probes.

Current v047 status under this gate: the paper package now makes the
conditional formal-order comparison explicit rather than treating full
residual reproduction as the main claim. In the accepted artifact scope, the
Gauss6/FullVA path is sixth order, records smooth position/velocity orders
7.161/7.066, and is compared only with the local paper-style `m=3`
Gauss-Lobatto TFE formula target of expected order five. It has four-example coverage: single/double pendulum provide
dynamic order evidence, while four-link/slider-crank provide closed-loop
constraint/reaction checks that are not interpreted as order estimates. This is a
comparative integrator claim, not a claim that the source paper's complete TFE
residual has been reimplemented. v047 also exceeds the local v046/rA baseline
in the currently validated evidence set, because the four ASME method rows are
accepted and the v046 baseline diagnostics show weaker or failing behavior on
most rows. v047 does not yet justify a claim that it reproduces and then
exceeds the complete paper TFE residual: full TFE stage replacement remains
missing, sparse runtime is quantified but not yet a dense-`jacfwd` speed win,
and practical sharp-friction coarse-regime cost/order behavior remains an
explicit caveat.

Current v048 status: v048 adds the executable cross-paper same-test benchmark
harness. It writes the external run plan across the original TFE paper and the
Kissel/Negrut-related public-code families, estimates the full 2021 public
order-policy workload at 326700 public-code steps, and completes the targeted
all nine 2021 `rA/rp/reps` public step-size trios for `single_pendulum`,
`four_link`, and `slider_crank` as 27/27 ok rows and 9/9 public order groups.
It now also completes a bounded
same-mechanism `Gauss6/FullVA` single-pendulum pilot with 3/3 rows and
position/velocity/orientation/omega orders `6.073/6.033/6.055/6.024`, plus a
3/3 exact public-horizon single-pendulum step-size trio at `T=3`, `h=[1e-2,1e-3,1e-4]`
(finest position/velocity errors `2.584e-14/7.012e-15`, roundoff-limited), plus a
6/6 selected closed-loop `Gauss6/FullVA` public-mechanism residual pilot on
the 2021 `four_link` and `slider_crank` mechanisms, plus a 6/6 public-horizon
closed-loop residual tranche for the same two mechanisms at `T=3`,
`h=[1e-2,1e-3,1e-4]`. The finest public-horizon closed-loop rows have max
dynamics residuals `5.136e-13` and `1.113e-14`, runtimes `73.25s` and
`89.49s`, and were run through independent shard/merge entry points so they can
be parallelized safely. The closed-loop rows verify constraint, SO(3), and
Newton-Euler reaction residuals, but they are not dynamic order/work rows. It
also adds a coarse public-horizon double-pendulum `Gauss6/FullVA` tranche at
`T=3`, `h=[0.1,0.05,0.025]`, reference `h=0.0125`, with position/velocity
orders `7.951/7.042`; its max endpoint position/velocity residuals
`1.131e-05/3.533e-04` keep it as coarse-first order/work evidence rather than
the public `1e-4` policy or a superiority row. v048 now also adds matching
coarse same-window public double-pendulum baselines at `T=3`,
`h=[0.1,0.05,0.025]`, reference `h=0.0125`: `rA/reps` complete 6/6 rows
with position/velocity orders `0.703/0.754`, while `rp` records three Newton
nonconvergence rows. It also adds a single-pendulum coarse same-window tranche
at the same `T=3`, `h=[0.1,0.05,0.025]`, reference `h=0.0125`, with 9/9
public rows, 3/3 local `Gauss6/FullVA` rows, a 4-row work/precision summary,
and local position order `6.054`. It also writes a 2-row closed-loop surrogate dynamic gate:
`four_link` and `slider_crank` have selected-window residual-to-error evidence,
but `closed_loop_surrogate_accepted_dynamic_order=0`. It also writes a 2-row
closed-loop dynamic error floor audit: both rows have velocity/acceleration
floor evidence, both retain a position/reference-floor blocker, and
`closed_loop_floor_audit_accepted_dynamic_order=0`. It also writes a
closed-loop coarse dynamic-order probe at `T=0.2`, `h=[0.1,0.05,0.025]`,
reference `h=0.0125`: `11/12` rows are ok, one public
`slider_crank`/`rA` row fails at `h=0.1`, local velocity/acceleration
evidence is present for both mechanisms, both mechanisms still have
position-floor blockers, and `accepted_dynamic_order_count=0`. This confirms
that larger steps do not by themselves close the four-link/slider-crank
dynamic-order gap. It also writes a 4-row
coarse-first external readiness gate with `coarse_first_ready_examples=2/4`,
`closed_loop_surrogate_available=2`, `closed_loop_floor_audit_available=2`, and
`coarse_first_dynamic_order_missing=0`; this turns the no-default-`1e-4`
policy into a read-only validation artifact while still preserving
`external_superiority_claim=false`. It
also writes a 12/12 selected same-window comparison table for public
`rA` dynamics versus local `Gauss6/FullVA` closed-loop residual rows at
`T=0.2`, `h=[0.02,0.01,0.005]`; this is table-shape evidence and not the
exact public `T=3` dynamic campaign. It also writes 9-row public order/work
and 4-row same-window work/precision summary CSVs plus a 4-row single coarse
work/precision summary for manuscript tables. It
now completes 9/9 public `double_pendulum` dynamic self-reference order rows
for `rA/rp/reps` at `T=3`, `h=[1e-2,2e-3,1e-3]`, reference `h=1e-4`. It
also completes the 12/12 2021 public timing/iteration policy rows for
`rA/rp/reps` on all four examples at `T=3`, `h=1e-3`, using shard/merge entry
points. The
four-example performance matrix now records 48 method/example rows with
32 completed and 0 partial rows while preserving
`external_superiority_claim=false`. It also has a
bounded 2022 half-implicit four-example pilot with 24/24 ok rows and 8/8
`rA/rA_half` model-form trios. It does not change the method claim:
`same_test_campaign_status=not_run` and `external_superiority_claim=false`
remain required until the full same-test campaign and `Gauss6/FullVA` external
rows are run over the complete external test policies. The velocity-partitioning
code-path gate is now stronger than a local-directory miss: v048 records the
EasyChair PDF reference, public web-search status, and both local SBEL mirror
trees over `origin/master` plus `origin/user/aaron/msd`.

## Pipeline-Level Validation

`validate_pipeline_outputs.py` is the current top-level generated-output gate.
The generated summary `pipeline_validation_results/pipeline_validation_summary.json`
is the authoritative check-count record for the latest pass. The gate
inventories all 48 `vNNN_*` directories, checks 695 result files, parses 286
CSVs and 113 JSON files, validates 202 PNG headers, confirms the current v047
proof/ASME/convergence/plot gate, and calls
`v047_cylindrical_chain_pipeline/validate_v047_outputs.py`. Its generated
report lives under `pipeline_validation_results/`.

The top-level gate also checks the v047 paper package and the fast four-example
entry point.  It runs
`v047_cylindrical_chain_pipeline/validate_four_asme_minimal.py`, requires
`paper_v047_cylindrical_chain/PAPER_CLAIM_LEDGER.md`, the paper validators,
`v047_cylindrical_chain_pipeline/FULL_TFE_REPLACEMENT_GAP_LEDGER.md`,
`v047_cylindrical_chain_pipeline/FULL_TFE_REPAIR_SPEC.md`,
`v047_cylindrical_chain_pipeline/validate_full_tfe_gap.py`,
`v047_cylindrical_chain_pipeline/validate_full_tfe_repair_spec.py`, the
current PDF, and the order-acceptance gate. It then runs
`paper_v047_cylindrical_chain/validate_paper_claims.py`,
`paper_v047_cylindrical_chain/validate_proof_evidence_matrix.py`, and
`paper_v047_cylindrical_chain/validate_order_acceptance_gate.py`. It also runs
`paper_v047_cylindrical_chain/validate_submission_artifact_manifest_boundary_sync.py`
so the submission manifest's narrowed archive boundary and OC4 traceability
aliases stay synchronized with the reproducibility manifest and objective audit.
It also runs `paper_v047_cylindrical_chain/validate_objective_completion_audit.py`
and checks the objective blocker alias matrix for `OC4,OC6,OC12`: all three
remain open in the sense required by the completion audit, closure is not
allowed now for any of them, and the direct aliases preserve `OC4/open`,
`OC6/partial`, and `OC12/partial` with their current closure decisions.
This keeps the paper claim boundary, minimal ASME gate, example-level order
boundary, and submission-manifest boundary synchronized with the generated
artifacts without invoking `run_v047.py`.

For day-to-day validation command selection, `VALIDATION_QUICKSTART.md` is the
root entry point. It separates the paper package check, the minimal four-ASME
method gate, the read-only generated-artifact gates, the LaTeX build, and the
full numerical regeneration path.

The current v047 TFE evidence includes the paper all-row consistent-z0
terminal-output diagnostic: it removes the Gauss bootstrap by solving a 20D
instantaneous acceleration/multiplier system, but remains diagnostic because
accepted h-sweep order and conditioning are still open.
The follow-up paper all-row consistent-z0 conditioning audit records 6 one-step
rows, full rank 132, max raw/equilibrated conditions 1.58e13/5.07e4, and the
dominant near-null row/variable families
`lower_pair_index3_weak_constraints`/`lower_pair_lambda`; it localizes the
conditioning blocker but is not a full TFE stage replacement.
The paper all-row consistent-z0 scaled-Newton diagnostic solves the same
six-family/132-row residual with iterative equilibration inside Newton. It
reduces the maximum condition diagnostic from 1.58e13 to 5.13e4 with
raw-to-scaled reduction 3.80e8, but the smooth/sharp orders remain 4.046/4.420
and 2.554/1.918, so the full TFE stage replacement gate remains open.
The paper family-ablation diagnostic solves 12 one-step rows over two
five-family variants. It keeps full rank 132 and residuals below 7.29e-12, but
the near-null family is always
`lower_pair_index3_weak_constraints`/`lower_pair_lambda`, with worst raw/scaled
conditions 1.58e13/1.39e5. This localizes the lower-pair/lambda algebraic
blocker without accepting a full TFE stage replacement.
The paper lower-pair/lambda Schur diagnostic solves 6 one-step rows on the
same six-family residual, partitions lower-pair rows against lambda columns,
finds a zero direct lower-row/lambda block and a full-rank reduced Schur block
with max condition 5.98e3. Its Schur-ordered Newton direction check has max
linear residual 1.15e-14 and max relative direction difference 7.79e-09 versus
the raw solve, so the blocker is not fixed by linear-solve ordering alone; it
keeps `full_tfe_stage_replacement=false`.
The paper lower-pair row-variant diagnostic compares position, velocity, and
acceleration lower-pair row formulas over 18 one-step rows. All variants solve
with full rank 132 and max residual 7.29e-12; `acceleration_constraint` is the
best Schur-conditioned variant with max Schur condition 9.71e1 versus the
position baseline max 5.98e3. This identifies the next residual-formulation
target while keeping `full_tfe_stage_replacement=false`.
The paper lower-pair acceleration terminal-output h-sweep diagnostic advances
that acceleration-level row choice to 6 smooth/sharp full-trajectory rows. It
solves all 6 row families and 132 stage rows with max terminal residual
8.35e-12, full rank 132, max raw/scaled conditions 4.37e8/5.83e3, smooth
position/velocity orders 4.937/4.799, and sharp orders 2.555/1.918, while
keeping `accepted_h_sweep_present=false` and
`full_tfe_stage_replacement=false`.
The paired paper lower-pair acceleration projection-dependence audit compares
the raw terminal paper output against the endpoint-velocity-projected terminal
state over the same 6 rows. It records max raw/projected endpoint velocity
residuals 7.99e-06/9.66e-15, max projection delta 7.92e-06, and 6/6 rows
requiring projection, so the terminal-output diagnostic is explicitly not a
projection-free full-TFE replacement.
The paper lower-pair acceleration terminal-velocity closure diagnostic then
replaces only the final lower-pair acceleration rows with 8 weighted raw
terminal endpoint-velocity rows. It closes raw terminal velocity to 5.80e-16
without output projection, with max closure residual 9.73e-12, rank 132,
raw/scaled max conditions 1.28e10/7.99e4, smooth/sharp orders 3.459/4.838 and
2.555/1.918, and max replaced terminal lower-pair acceleration row 2.53e-4;
it remains diagnostic and keeps `full_tfe_stage_replacement=false`.
The terminal-row homotopy audit solves 30 one-step rows over
beta=[0,0.25,0.5,0.75,1], records max residual 6.22e-12, full rank 132,
raw/scaled max conditions 1.28e10/7.86e4, and beta0/beta1 terminal velocity
residuals 2.34e-10/1.29e-12, but it is still row replacement rather than an
independently derived full-TFE stage functional.
The paper lower-pair terminal source-target audit records 6 case/h rows and
maps the 8 replaced terminal rows to 24 candidate stage-local lower-pair source
rows over the three paper stages. It keeps terminal-row replacement explicit
and preserves `full_tfe_stage_replacement=false`.
The paper lower-pair terminal source-lift audit records 6 case/h rows and
lifts that terminal source into 24 stage-local lower-pair rows with
`sqrt(h*b_i)*terminal_lower_pair_source`. It has max lift reconstruction error
0.0 and max lift-ratio deviation 2.22e-16 while still preserving
`full_tfe_stage_replacement=false`.
The paper lower-pair terminal source-normalization audit records 6 case/h rows,
shows that the raw budget source has max terminal reconstruction relative
error 9.47e-1, and verifies
`terminal_lower_pair_source = terminal_row_vector/sqrt(h*b_terminal)` with
zero normalized reconstruction error. It fixes the scale needed before Newton
residual substitution and still preserves `full_tfe_stage_replacement=false`.
The follow-up terminal source-insertion audit records 12 sign/case/h rows,
inserts the normalized source into the lower-pair Newton residual, converges all
12 one-step attempts, selects source_sign=-1 as the best sign, and records
residuals from 4.00e-13 to 9.77e-12. It still has
`accepted_h_sweep_present=false` and `full_tfe_stage_replacement=false`.
The terminal source-insertion trajectory audit then runs the best sign over
h=[0.04,0.02,0.01]. It completes all 6 smooth/sharp trajectory rows and all
28 source-ready/source-insertion steps with max source-insertion residual
9.75e-12, but the h=0.005 reference fails and the raw terminal endpoint
velocity reaches 7.41. It is therefore a quantified failure frontier, not an
accepted h-sweep or full TFE stage replacement.
The terminal source-insertion blow-up audit records 14 case/metric rows and 12
blow-up signals, with max mid-to-fine/coarse-to-fine ratios 7.339e3/4.936e5,
minimum observed h-power -9.456, and dominant signal
`cylindrical_smooth:max_normalized_source_norm`. This localizes the current
full-TFE blocker to a refinement-unstable closure-derived source policy.
The bounded-policy audit records the corresponding bounded-source target over
the same 14 case/metric rows. It rejects the closure-derived source metrics,
shows that simple extra h^2 scaling is still insufficient for the dominant
rows, and keeps `accepted_h_sweep_present=false` plus
`full_tfe_stage_replacement=false`; the next repair target is an independent
bounded stage-local lower-pair TFE source formula, not a rescaled terminal
closure source.
The stage-local bounded-source formula audit then records 6 smooth/sharp case/h
rows and separates formula scale from recurrence: the local
`source_i = sqrt(h*b_i)*(terminal_lower_pair_row/sqrt(h*b_terminal))` formula is
bounded in all rows, with minimum local h-power 0.426, while the recurrent
terminal-closure source is unbounded with minimum h-power -9.456, max
recurrent/local source ratio 1.003e6, and max raw terminal velocity 7.41. This
keeps `accepted_h_sweep_present=false` and `full_tfe_stage_replacement=false`.
The direct endpoint-velocity source audit then removes the rejected
terminal-closure source generator from the source path by evaluating the raw
endpoint velocity residual `C_v` at the paper acceleration predictor's raw
terminal Lobatto node and inserting `sqrt(h*b_i)*C_v` into the lower-pair stage
blocks. It records 6 smooth/sharp trajectory rows over h=[0.04,0.02,0.01]
against h=0.005, minimum position/velocity orders 2.555/1.918, minimum
direct-source/terminal-velocity h-powers 0.307/0.286, max direct source
8.118e-6, and max post-insertion terminal velocity 7.969e-6. This is real
progress on bounded recurrence, but it stays partial because the source is
still endpoint-boundary-derived rather than a complete independent paper TFE
stage residual.
The direct-source residual-substitution audit then evaluates the raw paper
lower-pair acceleration residual at the source-inserted solution and verifies
`raw_lower_pair + sqrt(h*b_i)*C_v = 0` over 6 smooth/sharp trajectory rows. It
records max balance and inserted lower-pair residuals 1.821e-13, keeps all 28
source-residual-substituted steps clean, and preserves
`endpoint_boundary_source_removed=false` and
`full_tfe_stage_replacement=false`.
The residual-derived stage-source audit then reverses that relation stage by
stage with `C_hat_i=-R_i/(source_sign*sqrt(h*b_i))`. It records 6 trajectory
rows, max derived-vs-direct source gap 1.289e-12, max stage-consistency gap
1.406e-14, max mean reconstruction error 1.482e-15, zero derived balance error,
and the same 2.555/1.918 minimum position/velocity orders. It remains partial:
the accepted trajectory still uses the direct endpoint source, so endpoint
boundary source removal and full TFE stage replacement are still open.
The self-consistent endpoint-source audit moves the endpoint velocity source
inside the lower-pair Newton residual as `C_v(x_terminal)`, so the trajectory no
longer passes an external endpoint source. It records 6 trajectory rows, max
residual/balance/source 9.441e-12/1.821e-13/7.974e-06, and smooth/sharp orders
5.333/6.790 and 2.555/1.918. It remains partial because that source is still
endpoint-boundary-derived, with `full_tfe_stage_replacement=false`.
The source-free elimination rank audit then tests whether stage-consistent
`C_hat_i` can remove the lower-pair endpoint source algebraically. It records
6 trajectory rows with max stage-consistency gap 1.406e-14, but the
source-free centering/elimination map has rank 16 for 24 lower-pair stage rows.
The 8-row rank defect is the missing mean-source closure budget, so the full
TFE blocker is now localized to 8 independent lower-pair mean-source rows
derived from the paper stage functional.
The source-free mean-velocity closure candidate fills that 8-row budget with
paper-stage mean-velocity closure rows: 16 centered acceleration
source-consistency rows plus 8 mean-velocity rows solve 6 smooth/sharp
h-sweep rows with max residual 8.13e-12 and without endpoint source,
terminal-row replacement, or projection. It remains partial because smooth
orders are 3.512/4.448 and sharp orders are 2.555/1.918, so
`full_tfe_stage_replacement=false`.
The source-free mean-blend closure audit then sweeps 7 alpha values over 42
one-step rows, keeps endpoint source, terminal-row replacement, and projection
removed, and finds best alpha 0 with max residual/raw terminal velocity
5.489e-12/2.337e-10. It remains partial because terminal velocity is still
above 1e-10 and no accepted trajectory h-sweep is present.
The source-free mean-blend trajectory audit promotes that alpha to 6
trajectory rows, solves cleanly with max residual/raw terminal velocity
9.453e-12/8.234e-06, and records smooth/sharp orders 5.317/6.782 and
2.555/1.918. This shows the one-step near-closure does not persist under the
trajectory terminal-velocity gate.
The source-free mean-blend trajectory alpha sweep tests all 7 alpha values over
42 trajectory rows, identifies alpha 0.75 as the best terminal-velocity
trajectory choice, and records max residual/raw terminal velocity
8.779e-12/7.447e-06 with minimum position/velocity orders 2.555/1.918. This
rules out simple alpha tuning as the full-TFE repair.
The source-free component-blend trajectory audit tests an 8-component alpha
vector from a one-step h=0.02 screen and records max residual/raw terminal
velocity 9.971e-12/7.458e-06, minimum orders 2.555/1.918, and a 1.001
terminal-velocity ratio versus the scalar alpha baseline, so per-component
alpha tuning does not close the terminal-velocity blocker.
The source-free terminal-velocity extrapolation trajectory audit plus a source-free terminal-extrapolation blend trajectory audit replaces the
8 mean-closure rows with terminal-node Lagrange extrapolated Gauss-stage
velocity-constraint rows. It records 6 rows, max residual/raw terminal velocity
9.91e-12/1.18e-05, smooth/sharp orders 3.518/4.748 and 2.554/1.917, and
worst/smooth terminal-velocity ratios versus component-blend 1.585/0.147. It
is a real source-free basis-change diagnostic, but it worsens the worst-case
sharp coarse terminal velocity and keeps `full_tfe_stage_replacement=false`.
The centered terminal-velocity bridge audit then tests 16 centered acceleration
source-consistency rows plus 8 terminal-velocity bridge rows over
gamma=[0,0.5,1]. Gamma 0 closes terminal velocity to 4.01e-16 with max residual
9.75e-12, but it uses a terminal-boundary row, keeps
`endpoint_boundary_source_removed=false`, and is smooth-order limited
(3.523/4.828), so it is diagnostic rather than accepted full TFE.
The source-free order/closure blend trajectory audit then tests the same
source-free lower-pair row budget over beta=[0,0.5,1] and records 18 trajectory
rows. Beta 1 closes raw terminal velocity to 4.01e-16, but the smooth position
order remains 3.523; beta 0 and 0.5 keep the smooth position order above 5, but
terminal velocity remains around 4e-6. The audit therefore records
`order_and_terminal_intersection_present=false` and keeps
`full_tfe_stage_replacement=false`.
A lower-pair closure acceptance matrix compares 14 closure families, accepts
0 candidates, identifies `source_free_mean_blend_trajectory_best_alpha` as the
best source-free/order-preserving row set and the centered/final-stage velocity
closure rows as terminal-velocity row sets, so v047 has localized the order
blocker but has not closed the full TFE replacement gate. The closure property
Pareto audit groups the same 14 candidates into 5 property-intersection rows
and confirms that the accepted intersection is empty: 9 candidates are
source-free/no-replacement, 5 are order-preserving source-free, and 3 are
terminal-velocity closed.
The closure row-span audit then tests whether the already-tried source-free
basis can locally reproduce the terminal-velocity bridge row. Over 6 case/h
local tangents, the 40-row source-free basis has rank 40, augmenting it with
the 8 terminal-bridge rows raises rank to 48, max projection relative residual
is 2.814e-01, and row-span reproduced count is 0. The follow-up
missing-direction decomposition has rank 8, is orthogonal to the tested basis
to 8.75e-16 relative, and reconstructs the terminal-bridge target with max
reprojection residual 9.25e-14. The missing-direction column energy is
velocity-level: angular velocity is dominant in all 6 rows with max fraction
0.506, translation velocity reaches 0.496, lower-pair lambda is 0, and
translation acceleration is below 5.60e-05. Those rows span the target only as
a terminal-boundary-derived tangent diagnostic, so the next full-TFE repair
needs a stage-local source-free velocity-level formula for the eight missing
lower-pair tangent directions rather than another reweighting of the existing
source-free basis.

The follow-up velocity-basis span audit tests 7 weighted eight-row
stage-velocity closure families plus the 24-row all-stage velocity upper bound
against the same 8 terminal-bridge rows over 6 case/h samples. The all-stage
velocity rows span the terminal-bridge tangent with max relative residual
2.78e-15, while the best weighted eight-row candidate is
`endpoint_lagrange_velocity_closure` at relative residual 4.20e-01 and no
weighted candidate spans the target. The next repair target is therefore an
eight-row source-free compression of the all-stage lower-pair velocity row
space, followed by a nonlinear trajectory h-sweep.

The velocity-compression audit fits that eight-row source-free compression in
the local tangent space. All three fixed candidate compressions span all 6
case/h samples at roundoff; the best fixed candidate is
`optimized_global_stage_scalar`, with weights numerically `[0,0,1]`, selecting
the final paper-stage lower-pair velocity rows and giving best relative
residual 1.04e-15. The strengthened selector-degeneracy check shows the fixed
fits collapse to that final-stage selector: universal full 8x24 selector
distance is 1.53e-15 and max non-final-stage energy fraction is 1.71e-15. The
non-degenerate follow-up sweeps 192 fixed stage-0/stage-1 injection rows; 84
rows have meaningful non-final-stage energy, but none spans locally and the
best meaningful projection residual is 1.59e-03. The state-local diagonal
direction oracle then sweeps 72 rows over 65 direction samples; 36 rows have
meaningful non-final-stage energy, but none spans locally and the best
meaningful projection residual is 9.90e-03. The non-final full
component-mixing follow-up tests 36 stage-0/stage-1/stage-0+1 full-mixing rows;
0 span locally and the best tangent residual is 9.81e-01. The value-level
source-free probe then tests 72 case/h/candidate rows: all 72 balance row
values, 18 are value-balanced local tangent spans, but 0 meaningful non-final
value-balanced rows span. The successful spans are final-stage-selector-like,
with max spanning non-final-stage energy fraction 2.12e-15. The next repair
therefore needs a derivative-aware value-level source-free compression, not
another fixed, diagonal state-dependent, non-final component-mixing, or
value-only fit that misses the terminal bridge. The derivative-aware oracle now
shows that 36 meaningful non-final rows can balance values and span the local
tangent after a coefficient-gradient correction, so the remaining full-TFE
repair is a bounded analytic coefficient-gradient formula plus a nonlinear
h-sweep. A bounded-gradient cap sweep now tests 288 cap/candidate/case/h rows:
all 288 keep value balance and meaningful non-final energy, 92 span at the
tested caps, practical cap 1e12 spans 12 rows, and all 36 derivative-aware
local spans require cap 1e18, so the result remains an oracle rather than an
accepted bounded formula.
The later target-free active-stage-velocity matrix localization keeps that
boundary explicit without running a full trajectory solve: the expanded 20-row
active-law grid reaches best projection residual 0.576548 with
`stage2_velocity_shifted_column_broadcast_feature`, but independent target rank
remains 8 and `any_candidate_spans_terminal_bridge=false`, so it is
localization evidence rather than a full-TFE closure.
A two-row JSON-only missing-direction decomposition of that best law keeps the
same residual 0.576548, missing-direction rank 8, and no span, but localizes
96.3% of the remaining tangent energy to stage 2 with dominant variable family
`angular_velocity_w` at fraction 0.502991.
A stage-2 angular-velocity mask follow-up tests 8 target-free angular-only
matrix rows in 35.3 seconds. Its best law
`stage2_angular_velocity_shifted_column_broadcast_feature` reaches only
0.752997 with independent target rank 8 and no span, shifting the remaining
missing direction back to dominant `translation_velocity_v`; simple angular
masking is therefore excluded.
A direct translation/angular cross-coupling follow-up tests 8 target-free
outer-cross matrix rows in 35.3 seconds. Its best law
`stage2_velocity_angular_to_translation_cross_feature` reaches only 0.898812
with independent target rank 8 and no terminal-bridge span; the remaining
direction is still `translation_velocity_v` dominated at fraction 0.556004 and
99.9994% stage-2-local, so simple translation/angular outer-cross rows are
excluded as well.
A target-free endpoint-pose generalized-velocity predictor follow-up then tests
10 rows in 31.2 seconds. Its best law
`paper_endpoint_pose_positive_lagrange_z` improves the local projection
residual to 0.117782, but independent target rank remains 8 and no row spans
the terminal bridge; the residual tangent is still
`translation_velocity_v` dominated at fraction 0.514237 and mostly stage-0
local. This is the strongest local probe so far, but it is still diagnostic.
A near-terminal convex predictor follow-up then tests 14 rows in 31.7 seconds.
The exact stage-2-only law `paper_endpoint_pose_stage02_convex_0p00_z` spans
at roundoff but is terminal-bridge equivalent. The best nonterminal law
`paper_endpoint_pose_stage02_convex_0p05_z` reaches 0.049317 with rank 8 and
no nonterminal span, leaving a stage-0-dominated translation-velocity tangent.
Focused h-scaling reruns at h=0.02 and h=0.01 keep that nonterminal law at
residuals 0.051890 and 0.052472, so the gap is persistent rather than an
h=0.04 artifact.
A synchronized pose/velocity near-terminal follow-up tests 10 local rows in
29.7 seconds. Its best law `stage02_convex_pose_velocity_0p01_z` reaches
0.009512, with h=0.02/h=0.01 residuals 0.009978/0.010085, but it still has
rank 8 and no nonterminal span; the weight offsets 0p02/0p05/0p10 give
0.019205/0.049390/0.103464, so the improvement is a near-terminal asymptote.
A terminal-limit extrapolation follow-up then reaches residuals
4.699e-06/2.335e-06/1.168e-06 over h=0.04/0.02/0.01, but it still has no
span and is terminal-bridge-equivalent rather than an independent full-TFE
row.
A direct signed mean-acceleration bridge correction follow-up worsens the
best residual to 0.076159 or above and shifts the missing direction to
`lie_position_u`, excluding the existing bridge acceleration term as the
nonterminal correction.
A bilinear active-velocity outer-product follow-up then tests 24 target-free
feature/stage-2-velocity matrix rows in 57.3 seconds. Its best law
`stage2_velocity_feature_outer_stage2_velocity` reaches only 0.898720 with
independent target rank 8 and no terminal-bridge span, ruling out the tested
simple component-pair coupling family without changing the repair target.
A componentwise active-velocity diagonal follow-up tests another 24
Hadamard/shifted-diagonal rows in 56.7 seconds. Its best law
`stage2_velocity_diagonal_plus_hadamard_row_feature_stage2_velocity` reaches
only 0.898530 with independent target rank 8 and no span, so the tested
row-local componentwise couplings are excluded as well.

The nonlinear source-free final-stage velocity closure now inserts those rows
into the lower-pair residual as 16 centered acceleration source-consistency
rows plus 8 final paper-stage velocity rows. It solves 6 smooth/sharp
trajectory rows with max residual 9.49e-12 and raw terminal endpoint velocity
4.01e-16, without endpoint source, terminal-row replacement, or projection.
Smooth/sharp orders are 3.523/4.828 and 2.555/1.918, so terminal velocity is
closed but smooth position order keeps `full_tfe_stage_replacement=false`.

The nonlinear-history recurrent source-law trajectory screen tests five
target-free norm/Hadamard/bilinear/second-difference history laws. All rows
converge at rank 132 without endpoint source, target Jacobian, terminal-row
replacement, or projection, but no row closes terminal velocity and no row
preserves the smooth-order floor. The best law,
`recurrent_nonlinearhistory_velocity_terminal_source0historyhadamard_z`, has
terminal velocity 1.954e-07 and min order 3.525, so this nonlinear source-law
family is ruled out and `full_tfe_stage_replacement=false` remains.

Latest bounded-formula velocity-compression localization: the bounded analytic
saturation-law probe adds 648 law/cap/candidate/case/h rows over global tanh,
rowwise tanh, and rowwise rational-quadratic laws. All 648 rows keep value
balance and meaningful non-final energy, 366 span at the tested caps, and all
local spans require cap 1e22 for every tested law. The correction direction is
still a target-direction oracle and no nonlinear h-sweep is accepted, so
`full_tfe_stage_replacement=false` remains.

## Historical Status

| Scope | Proof/status | Four ASME examples | Convergence/diagnostics | Plots/artifacts | Current action |
| --- | --- | --- | --- | --- | --- |
| v001-v045 | Present in `ORDER_PROOF_LEDGER.md`. | Not systematically present; these were local mechanism and solver experiments before the four-example gate existed. | Present by local scope for most method versions; solver diagnostic versions report equivalence/runtime instead of temporal order. | Present for v005+ and most later versions; early baseline versions have CSV/report but fewer plots. | Keep as historical evidence; do not overclaim four-example completion. |
| v046 | Added as empirical/diagnostic validation. | Present for all four ASME examples. | Present with h=[0.02, 0.01, 0.005] against h=0.001 references. | Present: CSV, JSON, report, order plot, invariant plot. | Registered as the four-example validation anchor. |
| v047 | Direct-route conditional Gauss6/FullVA proof closed for the paper theorem; primitive/Taylor, P6 solver-policy discharge, P7 residual-to-error promotion, source-policy, and full-TFE replacement remain outside that closure. | Four ASME method rows are accepted with single/double/four_link/slider_crank graph, rank, kinematic, and reaction rows. | Smooth convergence is high-order; sharp-friction order/cost, sparse speed, and independent full-TFE replacement remain caveats. | Validator covers 292 generated result files, 147 CSV tables, 120 PNG plots; top-level validation inventories 695 result files, 286 CSVs, 202 PNGs, and 113 JSON files. | Continue only outside the closed proof route: source-policy/full-TFE runner gates, sparse-speed work, and sharp-friction practical policy remain future work. |
| v047+ | Required before a version is complete. | Required. | Required. | Required. | Use `VERSION_ROUND_TEMPLATE.md` before closing each version. |

Current v047 sync note: the target-free velocity-compression probe adds
`endpoint-TFE-paper-lower-pair-velocity-compression-target-free-formula`
evidence with 2592 rows over 12 target-free direction laws and 0 local spans.
The direction-capacity follow-up adds
`endpoint-TFE-paper-lower-pair-velocity-compression-direction-capacity`
evidence with 216 rows: all-stage velocity feature spaces span 72 rows, while
non-final active/source feature spaces span 0 rows. The nonlinear-capacity
follow-up adds
`endpoint-TFE-paper-lower-pair-velocity-compression-nonlinear-capacity`
evidence with 216 rows across six finite-difference source-feature families:
all six families have 0 spans, with best projection/correction residuals
6.95e-01/7.01e-01. The higher-order/nonlocal follow-up adds
`endpoint-TFE-paper-lower-pair-velocity-compression-higher-order-capacity`
evidence with 216 rows over third-differential and same-case cross-step
source features; all six families again have 0 spans, with best
projection/correction residuals 6.95e-01/7.01e-01. The one-step
history-transport follow-up adds
`endpoint-TFE-paper-lower-pair-velocity-compression-history-capacity`
evidence with 216 rows over transported source-row and non-final velocity-row
deltas; all six families have 0 spans, with best projection/correction
residuals 7.13e-01/7.12e-01. The two-step history-transport follow-up adds
`endpoint-TFE-paper-lower-pair-velocity-compression-multi-step-history-capacity`
evidence with 216 rows over two future transported source/velocity deltas;
all six families have 0 spans, with best projection/correction residuals
6.95e-01/7.01e-01. The recurrent history-capacity follow-up adds
`endpoint-TFE-paper-lower-pair-velocity-compression-recurrent-history-capacity`
evidence with 216 rows over two-step curvature and bilinear source/velocity
history features; all six families have 0 spans, with best
projection/correction residuals 6.95e-01/7.01e-01. The weak-row
structure-capacity follow-up adds
`endpoint-TFE-paper-lower-pair-velocity-compression-weak-row-structure-capacity`
evidence with 216 rows over source/active cross-Gram, Hadamard,
cross-Hadamard, and shifted-commutator source-active feature families; all six
families have 0 spans, with best projection/correction residuals
6.95e-01/7.01e-01. The row-space compression follow-up adds
`endpoint-TFE-paper-lower-pair-velocity-compression-row-space-compression`
evidence with 36 rows over target-free SVD, row-norm, and stage-balanced
frozen eight-row compressions; all six laws have 0 spans, with best projection
residual 7.38e-01 and best non-final residual 9.82e-01. The row-space
coefficient-derivative follow-up adds a CSV/JSON oracle audit over the same
36 laws/case/h rows: all 36 local tangents span after the derivative term and
24 are value-balanced, with best derivative-inclusive residual 8.92e-16, but
it uses a target-direction oracle and coefficient-gradient norms up to
6.78e18, so it is not a bounded target-free full-TFE repair. The h-adaptive
endpoint-pose velocity response follow-up adds four law-response rows with
`terminal_closed_row_count=1`, `smooth_order_ok_count=0`, and no accepted
order/terminal intersection. The candidate frontier audit then aggregates 11
candidate families and 115 rows, with 35 terminal-closed rows, 17 smooth-order
rows, and `order_terminal_intersection_count=0`; the bounded tangent
requirement audit then records `requirement_row_count=7`,
`row_space_oracle_span_count=36`, `target_free_formula_span_count=0`, and
`bounded_gradient_practical_cap_spanning_row_count=12`, so the next full-TFE
target is a bounded target-free stage-local weak-row tangent. The recurrent
stage2 feature-dictionary span audit adds 12 target-free dictionary rows, 8
local spans, 2 combined-dictionary spans, best dictionary `stage2_matrix_core`
at residual 1.084e-14, and still records
`formula_coefficient_law_present=false`, so the next full-TFE target is now a
bounded coefficient/selection law plus nonlinear h-sweep. The frozen
coefficient-law screen then records 60 target-free coefficient-law rows,
`span_count=0`, best law `closure_delta_norm_weights` at residual 5.596e-01,
`coefficient_derivative_included=false`, and no full-TFE replacement. The
state-feature coefficient-derivative screen then records 36 target-free rows,
`span_count=0`, best dictionary `stage2_matrix_core`, best law
`inverse_closure_delta_norm_weights_derivative`, best residual 5.908e-01,
`coefficient_derivative_included=true`, no target Jacobian or target direction,
and no full-TFE replacement. The read-only v047 validator now covers
292 generated result files, 147 CSV tables, and 120 PNG plots; after top-level
validation with v048 registered, the pipeline inventory is 695 result files,
286 CSVs, 202 PNGs, and 113 JSON files.

A latest targeted, non-artifact follow-up tests two simple acceleration
correction families for the synchronized stage02 pose/velocity predictor:
direct mean-acceleration closure additions and generalized-velocity Taylor
shifts. Each covers 18 local rows, keeps the uncorrected
`stage02_convex_pose_velocity_0p01_z` row best at residual 0.009512, leaves the
best corrected residual at 0.012376, and records nonterminal span count 0; full
TFE stage replacement therefore remains open.
Another targeted follow-up tests the stage-0/stage-2 pose slope as a kinematic
velocity predictor over 26 local rows. It again records nonterminal span count
0, leaves the uncorrected row best at residual 0.009512, and gives best
pose-slope residual 0.878519; this simple geometry predictor is therefore also
excluded.
A source-to-velocity lift follow-up maps mean-acceleration, source0, source2,
curvature, and history-delta lower-pair source rows through the current-pose
endpoint velocity matrix `C_v` into minimum-norm generalized velocity shifts.
It tests 34 local rows in 76.4 seconds, keeps nonterminal span count 0, leaves
`stage02_convex_pose_velocity_0p01_z` best at residual 0.009512, and ties
`stage02_convex_pose_velocity_0p01_sourcelift_historydelta_p1_z` with
`stage02_convex_pose_velocity_0p01_sourcelift_source0_p1_z` as best corrected
rows at residual 0.609803. This direct current-pose `C_v` source-lift is
therefore excluded as the missing independent full-TFE weak row.
A matrix-difference source-to-velocity lift then maps the same source rows
through stage-0 and stage-2 `C_v` matrices and inserts the difference of the
two minimum-norm generalized-velocity shifts. The first screen tests 14 local
rows in 58.7 seconds and reaches coarse-scale residual 0.042593. A refined
26-row scale sweep over 0.1, 1, and 10 gains runs in 92.5 seconds, keeps
nonterminal span count 0, leaves `stage02_convex_pose_velocity_0p01_z` best at
residual 0.009512, and gives best corrected row
`stage02_convex_pose_velocity_0p01_sourceliftmatrixdiff_historydelta_p0p1_z`
at residual 0.009527. This direct stage-0/stage-2 `C_v`
coefficient-difference lift is also excluded, and the failure is not just
large-gain scaling.
A normalized-history source-law follow-up then replaces `source0-history` by
its direction scaled by `||source0||` before the same matrix-difference lift.
It tests 10 local rows in 49.4 seconds, keeps nonterminal span count 0, leaves
`stage02_convex_pose_velocity_0p01_z` best at residual 0.009512, and gives
best corrected row
`stage02_convex_pose_velocity_0p01_sourceliftmatrixdiff_historyunitdelta_p0p1_z`
at residual 0.009590. This simple nonlinear recurrent-history source
direction is also excluded.

v047 audit inventory for the current proof ledger includes: paper
kinematic-formula, paper balance/constraint formula, paper
position-substitution, paper kinematic-substitution, paper all-row
substitution, Gauss-z0 terminal-output, recurrent-z0 terminal-output,
consistent-z0 terminal-output, consistent-z0 conditioning, scaled-Newton,
family-ablation, lower-pair/lambda Schur, row-variant, acceleration
terminal-output, acceleration projection-dependence, terminal-velocity
closure, terminal-row homotopy, terminal source-target, source-insertion
blow-up, terminal-source bounded-policy, stage-local bounded-source formula,
source-free mean-velocity, source-free mean-blend, component-blend,
terminal-extrapolation blend, centered terminal-velocity bridge, closure
acceptance matrix, closure property Pareto, value-level velocity compression,
derivative-aware velocity compression, bounded-gradient velocity compression,
bounded-formula velocity compression, target-free bounded-formula velocity
compression, direction-capacity velocity compression, nonlinear-capacity
velocity compression, higher-order/nonlocal capacity velocity compression, and
target-free active-stage-velocity matrix-gradient localization.

## Historical Backfill Matrix

| Scope | Existing evidence | Backfill action if promoted under the current gate |
| --- | --- | --- |
| v001-v005 | SO(3), rigid-body, fixed-pivot, and early endpoint benchmarks with local reports and plots. | Keep as historical baselines unless reused as a modern method claim; then add the four ASME examples and regenerate convergence/plot artifacts. |
| v006-v023 | Fixed-pivot and one-DOF revolute DAE/friction sequence with proof/status entries and local convergence evidence. | Treat as single-mechanism evidence only; a promoted method must add the missing double pendulum, four link, and slider crank mappings. |
| v024-v029 | Absolute-coordinate, PivotVA/FullVA, and double-revolute method line with relevant proof/status and convergence records. | Best candidates for backfill; v047 already reuses v027/v029 for single/double ASME mappings, accepts the double reference policy, and adds local closed-loop kinematic/reaction rows for four_link and slider_crank. |
| v030-v045 | Solver, sparse-AD, pattern, cache, and lower-pair backend experiments with equivalence/runtime diagnostics. | Do not require separate four-example physics validation when the version is purely a backend swap; instead attach the backend to a method version that passes the four-example gate. |
| v046 | Four-example reproducibility anchor for upstream rA. | Keep as the baseline/reference harness, not as a Gauss6/FullVA method improvement. |
| v047 | Active cylindrical lower-pair method scaffold. | Continue by improving sparse assembly beyond row-VJP, replacing the diagonal-equivalent stage-weighted candidate with an independent full TFE stage residual, and keeping sharp-friction order reduction explicit. |
| v048 | Cross-paper same-test benchmark harness. | Keep as an execution scaffold only; it has completed all 9/9 2021 public order groups, 9/9 public `double_pendulum` dynamic self-reference order rows for `rA/rp/reps`, 12/12 public timing/iteration policy rows for `rA/rp/reps` on all four examples at `T=3`, `h=1e-3`, one bounded 2021 single-pendulum `Gauss6/FullVA` order pilot, one exact public-horizon single-pendulum `Gauss6/FullVA` step-size trio at `T=3`, `h=[1e-2,1e-3,1e-4]` (`3/3` public h rows, roundoff-limited final-error orders), 6/6 selected closed-loop `Gauss6/FullVA` residual rows for the 2021 `four_link` and `slider_crank`, 6/6 public-horizon closed-loop residual rows for the same mechanisms at `T=3`, `h=[1e-2,1e-3,1e-4]` run through shard/merge entry points, a coarse-first public-horizon `double_pendulum` `Gauss6/FullVA` tranche at `T=3`, `h=[0.1,0.05,0.025]`, reference `h=0.0125`, with position/velocity orders `7.951/7.042`, matching coarse same-window public `double_pendulum` baselines where `rA/reps` complete 6/6 rows with position/velocity orders `0.703/0.754` while `rp` records three Newton nonconvergence rows, a single-pendulum coarse same-window tranche with 9/9 public rows, 3/3 local rows, and a 4-row work/precision summary at the same `T=3`, `h=[0.1,0.05,0.025]`, reference `h=0.0125`, with local position order `6.054`, 12/12 selected same-window public-`rA` versus local-`Gauss6/FullVA` comparison rows, 9-row public order/work, 4-row same-window work/precision, 3-row double coarse work/precision, 4-row single coarse work/precision, a 2-row closed-loop surrogate dynamic gate, a 2-row closed-loop dynamic error floor audit, a closed-loop coarse dynamic-order probe with `11/12` ok rows and `accepted_dynamic_order_count=0`, and 4-row coarse-first readiness gate CSVs with `coarse_first_ready_examples=2/4`, a 48-row four-example performance matrix with 32 completed and 0 partial rows, a bounded 2022 half-implicit four-example pilot with 24/24 ok rows and 8/8 model-form trios, and an 11-row velocity-partitioning code-path audit covering the EasyChair PDF reference check, public web search, and both local SBEL mirror refs `origin/master` plus `origin/user/aaron/msd`, but the full 2022 half-implicit campaign, original TFE, resolved velocity-partitioning, and remaining dynamic-order/work `Gauss6/FullVA` external rows are still required before CMAME superiority claims. |

## Backfill Notes

- v046 has now been added to `README.md`, `VERSION_LEDGER.md`,
  `VERSION_TREE.md`, `ORDER_PROOF_LEDGER.md`, and `version_ledger.csv`.
- v048 has now been added as the cross-paper same-test harness. Its full
  2021 `rA/rp/reps` public step-size trio run for `single_pendulum`,
  `four_link`, and `slider_crank` proves the runner can produce all public
  order-policy rows for that suite. Its selected `Gauss6/FullVA` pilot proves
  the accepted method can be run on that same mechanism over a bounded short
  horizon. Its 2022 half-implicit pilot proves the `rA/rA_half`
  `single_pendulum`, `double_pendulum`, `four_link`, and `slider_crank`
  public-code/state-history entry points can run under the harness as 24/24 ok
  bounded rows, while recording that this is not the full `T=8` 2022
  convergence campaign. Its
  velocity-partitioning audit records the EasyChair PDF reference check, public
  web search, and both local `sbel-reproducibility` and `public-metadata` refs
  `origin/master` plus `origin/user/aaron/msd`, with no distinct VP code
  directory resolved. Its parallel public-horizon closed-loop shard
  runner/merger and four-example performance-matrix validator make the current
  coverage auditable without serializing independent rows. None of these items
  is a new integrator result, and none closes the CMAME external-comparison
  gate.
- The older v001-v045 reports remain valid as local evidence, but they are not
  retroactively marked as satisfying the four-example gate.
- Future research rounds should either run the new method on the four ASME
  examples directly or explicitly report why the mapping is not yet implemented
  and keep the version open/incomplete.
