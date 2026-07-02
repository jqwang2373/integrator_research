# CMAME Submission-Readiness Review

Status: **GLOBAL SUBMISSION OPEN; BOUNDED NARROWED SUBCHECK SATISFIED**

Review protocol used:

- Local `research-pipeline` paper submission-readiness gate.
- Installed ARS Codex skill:
  `/home/jingquanw/.codex/skills/academic-research-suite`.
- ARS route: `academic-paper-reviewer`, full-review logic.
- Reference/style PDF read:
  `../../s11044-026-10153-w.pdf` extracted to `../../s11044-026-10153-w.txt`.
- Current manuscript PDF read:
  `main_cmame.pdf` extracted to `main_cmame.txt`.

This began as a historical quality review from before the narrowed-claim
closure policy. The current package-facing global decision is recorded in
`CMAME_REVIEW_AGENT_REPORT.md`: do not submit globally yet. The narrowed
formal-order/common-reference diagnostic package is only a bounded subsidiary
subcheck; full source-policy reproduction and external superiority remain
non-claims.

## Objective Blocker Matrix

The global objective blocker matrix remains:

- `blocker_open_by_id=OC4:True,OC6:True,OC12:True`
- `blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready`
- `blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False`

This matrix is inherited from `OBJECTIVE_COMPLETION_AUDIT.json`; it keeps
OC4, OC6, and OC12 open and does not authorize B4/source-policy execution.

## Field Analysis

| Dimension | Assessment |
| --- | --- |
| Primary discipline | Computational mechanics; multibody dynamics; geometric numerical integration |
| Secondary disciplines | Lie-group integration, constrained DAE solvers, time finite elements |
| Research paradigm | Numerical-methods paper with theoretical and computational validation |
| Target venue | CMAME-level methods journal |
| Paper maturity | Narrowed-claim method/proof subcheck passed; global source-policy submission still open |
| Editorial risk | High desk-reject risk if submitted as a global source-policy/external-superiority paper |

Recommended realistic route:

1. Rebuild as a true computational-methods paper before CMAME.
2. Use Multibody System Dynamics or Journal of Computational and Nonlinear
   Dynamics style as an intermediate quality target if CMAME depth is not yet
   reachable.
3. Keep CMAME only after the method derivation, experiment narrative, and
   source-paper comparison are fully defensible.

## Editorial Decision

**Historical decision before narrowed-claim closure: major revision before any
full source-policy/external-superiority submission. Current global decision:
do not submit globally yet; the narrowed-claim subcheck is subsidiary.**

Reason: the manuscript has a mechanically valid submission shell and the
narrowed method/proof subcheck is now defensible as a conditional theorem
under retained P1, P2, and P3 theorem interfaces, the separate P6
solver-scale interface, the retained P4 binding convention with its proved
96-row certificate, and the P7 nonpromotion boundary. The global CMAME
submission decision remains open because the
same-test source-policy comparison, original-TFE runner, and full
source-policy runner package are not closed.

## Revision Update

The 2026-05-30 revision partially addressed the first review pass:

- added a stage-vector count and row-family definition for the 132-row
  `Gauss6/FullVA` residual;
- added collocation, Newton--Euler, FullVA, endpoint reconstruction, and
  Newton linearization equations;
- added numerical error-norm and reference-solution policies;
- added mechanism-level descriptions for the driven single pendulum, double
  pendulum, four-link closed loop, and slider-crank closed loop;
- replaced Figure 2 with a four-panel mechanism schematic and visible
  CD/DP1/DP2/D constraint inventory for the four ASME-style examples;
- added a lower-pair constraint-formula section defining CD, DP1, DP2,
  distance rows, and the FullVA position/velocity/acceleration levels;
- added velocity and acceleration derivatives for the lower-pair row families
  and an explicit Newton row-to-unknown block description;
- added a compact ASME setup table with physical parameters, drivers,
  step-size/reference policies, and accepted checks for all four examples;
- added coordinate-level mechanism specifications listing the body-fixed
  joint point vectors, direction vectors, and driver functions used by the
  four ASME-style examples;
- added a work/solver diagnostics table with finest-step runtime, Newton
  iterations, and accepted error/residual values for the evidence rows;
- upgraded Figure 1 from a simple convergence plot to a four-panel
  convergence/work-precision/cost-envelope figure for the accepted method
  path and the sharp-friction caveat;
- added a stage-Jacobian structure subsection giving the collocation,
  Newton--Euler, FullVA lower-pair, Lie-variation, and block-matrix
  dependencies behind the 132-row Newton solve;
- expanded the lower-pair derivation with scalar CD/DP1/DP2/D Jacobian
  entries and the point, direction, velocity, and acceleration perturbations
  used by the FullVA rows;
- replaced the terse order-inheritance proof with an explicit conditional
  perturbed-Gauss argument: full-rank constraints, nonsingular reduced mass,
  a smooth reduced Lie-group chart, isolated Newton solve, and local
  `O(h^7)` perturbations are now stated as the assumptions needed for global
  sixth-order behavior;
- moved the machine-readable claim contract, validator table, and flat source
  package details out of the main method/results narrative and into a
  reproducibility appendix;
- rewrote the abstract, introduction, contribution list, validation protocol,
  and conclusion to describe the method and evidence rather than foregrounding
  repository-internal scaffolding;
- added a nonlinear solver tolerance table reporting the residual/update
  stopping rules, Newton iteration caps, rank tolerance where applicable, and
  finest-step Newton counts for the cylindrical-chain and four ASME-style
  evidence rows;
- added a source-paper comparator clarification: the reference PDF uses the
  `2m-1` formula-order convention for the `m=3` TFE target, but its DAE
  pendulum experiment can show order loss; this manuscript keeps the stronger
  formula-order target `5` rather than weakening the comparator to that
  observed order-loss result;
- expanded Related Work from a short list into four positioned clusters:
  Lie-group integration, index-3 DAE/absolute-coordinate formulations,
  high-order DAE collocation, and time finite elements, with the manuscript
  gap stated as a concrete FullVA lower-pair stage residual rather than a
  claim that Gauss collocation itself is new;
- regenerated the ASME mechanism schematic as a coordinate-oriented figure
  with global axes, named joints, principal body labels, driver annotations,
  and key coordinate/constraint callouts;
- added a same-step implemented source-paper TFE all-row diagnostic
  comparison to the numerical evidence and Figure 1: the diagnostic uses
  terminal Lobatto-node output, a consistent initial `z0` policy, and
  equilibrated Newton linear solves, but is explicitly not treated as an
  accepted fair baseline because the paper-derived recurrent start policy and
  full-TFE replacement gate remain open;
- added a cross-paper same-test comparison gate covering the original
  Chaturvedi--Sandu--Sandu pendulum tests and the Kissel/Taves/Negrut and
  Fang/Kissel/Zhang/Negrut public-code benchmark suites; this records that
  the current four ASME-style examples have overlapping names but are not yet
  certified as identical external baselines;
- extracted the 2021 `rA/rp/r-epsilon` and 2022 half-implicit public-code
  benchmark specifications into `CROSS_PAPER_BENCHMARK_SPEC.md`, including
  step sizes, tolerances, reference policies, work metrics, and the important
  distinction that the 2021 and 2022 slider-crank baselines use different
  crank masses;
- added `CROSS_PAPER_BENCHMARK_CASES.json`, a machine-readable run inventory
  that separates the original TFE pendulum rows, the 2021 `rA/rp/reps` suite,
  the 2022 half-implicit suite, and the 2024 Kissel/Bakke/Negrut
  velocity-partitioning paper-code-resolution gate;
- refined that run inventory so `current_status` means the full source-policy
  case status, while `partial_evidence_overlay` records the existing
  coarse-first and bounded evidence. This makes the no-default-`1e-4` policy
  auditable without pretending the full external campaign has passed;
- added an endpoint-closure perturbation lemma: under a uniformly
  right-invertible closure Jacobian and an `O(h^7)` raw endpoint closure
  defect, the minimum-norm endpoint correction is also `O(h^7)`, so endpoint
  projection does not by itself reduce sixth-order inheritance;
- added `CMAME_PROOF_CONTRACT_GATE.md/json`, a machine-checkable proof
  contract stating that the theorem is only a conditional consistency-transfer
  theorem, that fixed-tolerance runs are finite-run evidence rather than an
  asymptotic proof, and that the dynamic symbolic oracle and residual-to-error
  route remain open;
- added `CMAME_EXTERNAL_BASELINE_GATE.md/json`, a machine-checkable external
  comparison contract stating that the same-test campaign is still not run,
  that `1e-4` is opt-in rather than default, and that `four_link` and
  `slider_crank` remain surrogate/residual-only for external dynamic order;
- refreshed `main_cmame.pdf`, the flat submission PDF, extracted text, and
  the flat source archive.
- regenerated Figure 2 with a cleaner label layout and added
  `CMAME_VISUAL_LEGIBILITY_AUDIT.md/json`, closing B5 for mechanism visual
  reproducibility while leaving the broader publication-figure blocker B7
  open.
- expanded Related Work into six clusters and added primary-source
  positioning for constrained collocation/index reduction, constrained
  variational integrators, nonsmooth contact/friction complementarity
  solvers, and Lie-group DAE multibody methods; `CMAME_RELATED_WORK_AUDIT.md/json`
  closes B8 while keeping the proof, baseline, narrative, and figure blockers
  open.
- added Figure 8, a claim-boundary and limitation map that separates accepted
  evidence, bounded/partial evidence, and open blockers without introducing a
  new numerical campaign; this partially addresses B7 but does not close the
  missing baseline-comparison and complete work/precision figure requirements.
- added Figure 9, a coarse-first baseline comparison and work/precision
  summary assembled from existing v048 rows; it compares single/double
  pendulum coarse-window order and four-link/slider-crank strict
  common-reference error/runtime ratios, but it remains partial B7 progress
  rather than an external-superiority claim.
- added Figure 10, a closed-loop coarse-dynamics diagnostic figure assembled
  from existing v048 rows; it plots four-link and slider-crank position,
  orientation, velocity, and angular-velocity error decay, fitted primary
  orders, and non-oracle Newton work without introducing a new numerical
  campaign or a default `1e-4` policy.
- added an order-acceptance policy table that separates the accepted
  single/double pendulum dynamic-order rows, the four-link/slider-crank
  mechanism-coverage rows, the source-paper diagnostic row, and the
  in-progress public-baseline rows; this reduces B4 ambiguity but does not
  replace the missing full baseline campaign.
- added the closed-loop coarse-dynamics Newton diagnostic evidence
  to the order gate: `four_link` has primary-state orders
  `5.955/5.955/6.085/5.971` and `slider_crank` has
  `6.164/6.159/7.341/6.426` over `h=[0.1,0.05,0.025]` with
  `reference_h=0.0125`, no stage oracle, no default `1e-4`, and no external
  superiority claim.
- added Figure 11, an accepted-method architecture schematic that separates
  the `Gauss6/FullVA` one-step map, 132-row residual families, conditional
  proof boundary, and non-claims including no full-TFE replacement, no
  default `1e-4`, and no external-superiority claim.
- added Figure 12, an all-method all-example common-reference result matrix
  assembled from existing `PAPER_NUMERICAL_RESULT_MATRIX.json`; it makes all
  44 order/error cells visible for `single_pendulum`, `double_pendulum`,
  `four_link`, and `slider_crank` while preserving the diagnostic-only
  source-policy boundary.
- added `ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.md/json`, which checks
  all four examples and all nonlocal method/example rows: 44 total cells,
  40 nonlocal cells, 132 raw rows recomputed, `0/40` source-policy rows
  closed/open, and `0` strict external error-claim rows allowed.
- added `CMAME_FIGURE_SET_AUDIT.md/json`, which checks all 13 figures across
  main/flat sources and PDF captions; B7 is closed under the narrowed
  common-reference diagnostic figure scope, while full source-policy
  figure/package promotion remains outside the current claim.
- rewrote the proof regularity assumption to remove the circular shortcut
  that directly assumed the accepted one-step map differs from Gauss by
  `O(h^7)`; the theorem now derives the local defect from separate FullVA
  lift, implementation residual-defect, endpoint-closure, and Newton-tolerance
  obligations.
- added `PROOF_NUMERICAL_SCALE_AUDIT.md/json`, a read-only audit of the
  existing smooth h-sweep. It records global smooth-error fits
  `7.160828/7.066183`, raw endpoint closure fits `5.985101/6.072291`, and
  bounded h^6-normalized ratios, while explicitly keeping
  `eta_h_O_h7_solver_policy_evidence=false`. The later D5
  direct-substitution contract closes the stage-residual implementation-defect
  route separately; this finite-run numerical scale audit is not that proof.
  This proof numerical scale audit is a finite-run order-six scale diagnostic,
  not an asymptotic solver proof.
- added `PROOF_SOLVER_SCALED_TOLERANCE_PROBE.md/json/csv`, a finite one-step
  smooth solver-scale probe using `eta_h=c_eta h^7`. It records `4/4` ok rows
  and maximum final residual divided by `h^7` equal to
  `127.58372278641149`; this is proof-support diagnostic data but not a theorem-level
  scaled trajectory sweep.
- rewrote the external-suite comparison table so it now states the current
  evidence and the claim allowed for the original TFE paper, the 2021
  `rA/rp/reps` suite, the 2022 half-implicit suite, and the 2024
  velocity-partitioning suite; this reduces B2 ambiguity while keeping
  `external_superiority_claim=false`.
- demoted the paper-facing comparison from an "accepted comparative integrator
  theorem" to a conditional order-comparison proposition: the sixth-order
  theorem remains attached only to the accepted `Gauss6/FullVA` map under the
  stated smooth FullVA contract, while the TFE comparison is now explicitly a
  narrow formal-order comparison against the local order-five target.
- removed the remaining "better-integrator result" and "comparative
  integrator theorem" phrasing from the abstract, introduction, limitations,
  and conclusion, replacing it with conditional formal-order comparison
  language and an explicit non-superiority boundary.
- extended `DYNAMIC_ROW_ORACLE_GATE.md/json` with a partial independent
  formula-row oracle: 96 non-dynamic kinematic/lower-pair rows are
  independently reassembled and checked exactly on the deterministic stage
  vector, while `newton_euler_weak_balance` remains excluded; this was a
  light proof/oracle update, not a default `1e-4` numerical campaign.
- extended the same oracle to `newton_euler_weak_balance`, giving a full
  independent formula-row oracle for all 132 runtime formula rows with zero
  recorded mismatch on the deterministic stage vector; this closes the
  runtime formula-row coverage gap but not the AD-expanded symbolic proof or
  the `O(h^7)` implementation-defect certificate.
- added a multi-probe formula-row AD Jacobian oracle: `jax.jacfwd` of the
  independent formula-row vector matches the accepted `R_JAC` on three
  deterministic stage vectors with max mismatch `3.330669e-16`; this
  strengthens B1 at the runtime AD level but remains a finite-probe check
  rather than a symbolic proof.
- added `IMPLEMENTATION_PATH_AUDIT.md/json`, a read-only static audit that
  checks `implementation_path_check_for_132_row_residual=true` for the accepted
  code path `residual_cylindrical_chain -> R_VALUE/R_JAC -> gauss_step ->
  integrate/run_case -> summary_v047.json`. This closes the narrow
  source-path traceability item without invoking `run_v047.py`, any v048
  runner, or a default `1e-4` campaign; it does not close the symbolic
  `O(h^7)` residual-defect proof.
- added `KINEMATIC_ROW_DEFECT_CERTIFICATE.md/json`, a partial proof-scope
  certificate for the 96 non-dynamic collocation/lower-pair rows on the smooth
  accepted FullVA lift. This is proof progress for B1/B3, but at this
  historical review point the primitive/symbolic dynamic-row lane and the
  scaled solver policy remained open.
- added `NEWTON_EULER_DEFECT_OBLIGATION_GATE.md/json`, an open ledger for the
  non-active primitive/symbolic Newton-Euler lane. It decomposes the 36
  Newton-Euler rows into six symbolic obligations, making the optional
  symbolic proof gap precise without serving as the active direct-route defect
  certificate.

These edits are real progress, but they do not close the quality gate.

## Blocking Findings

Resolved findings are retained for traceability. The historical local blocker
findings below predate the narrowed-claim closure and are no longer the
current package-facing gate. The current global blocking findings are OC4,
OC6, and OC12: source-policy reproduction rows, the original TFE
source-policy runner, and the full source-policy runner package. The current
global decision remains recorded in `CMAME_REVIEW_AGENT_REPORT.md`; B1--B8
are now a subsidiary narrowed-claim blocker-gate history, not the top-level
submission decision.

### B1. Closed for the current conditional proof and implementation-traceability claim.

Location: `main_cmame.txt` Sections 3, 5, 8, and 11.

The revised manuscript now defines the 132-row count, stage variables, row
families, endpoint reconstruction, Newton linearization, lower-pair
CD/DP1/DP2/D constraint formulas, velocity and acceleration derivatives, the
main Newton row-to-unknown block structure, and a stage-Jacobian block matrix
with Lie-variation dependencies. The lower-pair section now also gives the
scalar CD/DP1/DP2/D Jacobian entries and the point, direction, velocity, and
acceleration perturbations used by the FullVA rows. The conditional order
argument now states the regular reduced-flow and `O(h^7)` perturbation
assumptions needed to transfer sixth order from three-stage Gauss
collocation, and it now proves the endpoint-closure part of that transfer
under a right-invertible closure Jacobian and `O(h^7)` raw closure defect.
It now also adds a FullVA stage-row lift lemma, a stage-residual perturbation
criterion, and an inexact-Newton tolerance lemma. This is a meaningful
derivation improvement: the mathematical stage-row residual is no longer
merely assumed, because the new lift lemma shows that the accepted FullVA row
families are the lifted reduced Gauss stage equations plus pointwise
constrained-dynamics rows. The new implementation-fidelity certificate also
ties the accepted 132-row layout to the concrete `residual_cylindrical_chain`
and `R_JAC` JAX path in `run_v047.py`. The dynamic oracle now goes one step
further: it independently reassembles all 132 runtime formula rows, including
the 36 `newton_euler_weak_balance` rows, and checks them against the accepted
residual with zero recorded mismatch on the deterministic stage vector. It
also differentiates the independent formula-row vector and checks the resulting
132 by 132 Jacobian against the accepted `R_JAC` on three deterministic
probes, with max mismatch `3.330669e-16`. This closes the runtime formula-row and finite-probe AD
Jacobian coverage gap. `KINEMATIC_ROW_DEFECT_CERTIFICATE.md/json` now adds a
partial proof-scope certificate for the 96 non-dynamic collocation and
lower-pair rows on the smooth accepted FullVA lift; the 36
`newton_euler_weak_balance` rows are now closed for the active direct route by
`D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE.md/json`, which records 36/36
dynamic zero residual rows on the lifted Gauss stage. The Newton-Euler
obligation gate now keeps the symbolic/primitive certificate route open as a
non-promoted diagnostic lane: one symbolic/primitive D5 obligation remains
open, while translational balance, rotational balance, multiplier-wrench
consistency, smooth force-lift consistency, and symbolic runtime-row
equivalence are closed. `IMPLEMENTATION_PATH_AUDIT.md/json` additionally checks
the accepted source path from `residual_cylindrical_chain` through `R_VALUE`,
`R_JAC`, `gauss_step`, `integrate`, `run_case`, and `summary_v047.json`. This
closes the implementation-path traceability item for the active claim. Solver
error is also no longer treated as an empirical proof: the manuscript states
the proof-level policy `eta_h <= c_eta h^7` and keeps that solver-scale condition
explicit rather than promoting fixed-tolerance runs into an asymptotic proof.

Required fix: none for B1 in the current claim set. The remaining
symbolic/primitive dynamic oracle and full residual-to-error route stay outside
the active direct proof claim. The historical full source-policy gate was not
submission ready at this review point; the current narrowed-claim gate closes
B4, B6, and B7 separately while keeping full source-policy readiness false.

### B2. Closed by Route B claim demotion; same-test superiority remains future work.

Location: `main_cmame.txt` Abstract, Sections 1, 6, 7, and 8.

The earlier review correctly identified that the paper could not claim
implemented superiority over TFE or other external lower-pair integrators
without a same-test external baseline. The current route resolves that blocker
by changing the claim boundary, not by inventing numerical evidence. The
manuscript now presents Gauss6/FullVA as a sixth-order Lie-group FullVA
alternative with formal-order and common-reference diagnostics only, and it
does not claim source-paper external superiority.

The benchmark specification and case inventory have now been extracted. The
same-test external baseline remains useful future work: the original TFE
pendulum, the Kissel/Taves/Negrut public-code suite, the
Fang/Kissel/Zhang/Negrut half-implicit suite, and the
Kissel/Bakke/Negrut velocity-partitioning suite would still need identical
parameters, drivers, reference policies, error norms, tolerances, and
work/precision metrics before any external superiority claim could be made.
That campaign is explicitly not run here: `same_test_campaign_status=not_run`,
`external_superiority_claim=false`, and `accepted_external_dynamic_order_examples=0`.

`CMAME_EXTERNAL_BASELINE_GATE.md/json`,
`EXTERNAL_SAME_TEST_RUN_QUEUE.md/json`, and
`EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.md/json` keep the partial_evidence_overlay
auditable under the no-default-`1e-4` policy, including 20 non-default-`1e-4`
parallel shards for any future opt-in source-policy execution. `EXTERNAL_SUITE_DEMOTION_LEDGER`,
`B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST`, and
`EXTERNAL_SUPERIORITY_CLAIM_DEMOTION_AUDIT` now apply Route B: all active
external source-policy suites are demoted from external-superiority scope,
B2 is closed as a claim-boundary blocker, and the source-policy execution rows
remain `0/40`. This closes B2 only for the present manuscript claim set; a
future manuscript that reintroduces external superiority must reopen this gate
and run the same-test campaign.
The numerical campaign itself remains open for that future external-superiority
route.

### B3. The strict direct residual-bridge/Kantorovich proof route is closed.

Location: `main_cmame.txt` Section 8.

Status: closed by `B3_DIRECT_PROOF_REVIEW_AUDIT.md/json`.
The primitive/Taylor 162-subterm route remains diagnostic and open, but it is
not required for the current B3 submission-standard closure.

The proof now closes the implementation local-defect gap by a direct
substitution route rather than by the older source-expression certificate
route. `KINEMATIC_ROW_DEFECT_CERTIFICATE.md/json` closes the 96 non-dynamic
FullVA/lower-pair rows. `D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE.md/json`
then closes the 36 Newton-Euler weak-balance rows on the smooth Gauss lift:
after the D1/D2 balance identities and D3/D4/D6 consistency inputs, every
dynamic row residual is zero by direct residual substitution on `Z_G`. This
does not use finite probes, `P_state` actual PS3, `P_acc`, `P_lambda`, or any
residual-to-error promotion.

The latest proof pass also removes the circular one-step perturbation shortcut
from the regularity assumption: the theorem now decomposes the `O(h^7)` local
defect into FullVA lift consistency, implementation residual-defect,
endpoint-closure, and inexact-Newton obligations. `PROOF_CLOSURE_MANIFEST.md/json`
records close requirements satisfied/unsatisfied as `4/0`: PC1 is discharged by the
D1/D2 balance-identity audit, PC2 is discharged by D5 direct residual substitution,
PC3 is admissible only because `eta_h <= c_eta h^7` remains an explicit theorem
condition, and PC4 is admissible only because four-link/slider-crank residual rows are
not promoted into accepted dynamic-order proof.

The subsequent proof-writing pass strengthened the theorem proof itself rather
than changing the claim boundary.  The main and flat TeX sources now include a
same-object direct-substitution calculation that displays the exact route
`96+36 -> R_h -> Taylor/Kantorovich -> endpoint`: the 96 non-dynamic rows
supply the \(O(h^7)\) block, the 36 P5 Newton-Euler rows vanish on the same
lifted Gauss stage, the resulting fixed block residual \(R_h\) is inserted
into the same full-map Taylor/Kantorovich perturbation, and the endpoint
Lipschitz map gives the one-step perturbation.  The proof also now includes a
reference-style recursion analogue clarifying that the constrained-BDF
reference is used only for proof-order discipline.  No BLieDF constants,
multiplier estimates, primitive Taylor subterm bounds, finite solver logs, or
source-policy rows are imported into the present FullVA theorem.

The P7 boundary was also sharpened without changing the claim: the main and
flat TeX sources now state the same-codomain obstruction explicitly.  Any
future residual-to-error promotion must predeclare the mechanism residual
operator, residual norm, trajectory error map, row weights, floor term, and an
`h`-independent transfer constant before residual/reaction data are read.
Existing four-link, slider-crank, and source-policy residual rows remain
mechanism-coverage diagnostics, not dynamic-order evidence.

The following proof-writing pass strengthened the Taylor-layer exposition
without promoting the optional primitive route.  The main and flat TeX sources
now include a Taylor-layer dependency map that separates T1 reduced-Gauss
defect, T2 full-map Taylor/Kantorovich perturbation, and T3 optional
`162`-subterm primitive Newton-Euler Taylor inventory.  The map fixes the
accepted use rule: T1 and T2 are theorem inputs, while T3 can only become a
future alternative dynamic-block residual certificate and cannot be added to
the direct route, used to lower constants, remove P6, promote P7, or claim
primitive-route closure while the primitive inventory remains `0/162`.

The theorem boundary remains strict. The proof numerical scale audit supports
the finite-run order-six scale with smooth global slopes `7.160828/7.066183`
and raw endpoint-closure slopes `5.985101/6.072291`, but it is not used as a
Taylor proof. The solver-scale audit records existing summary-level residuals,
including smooth reference `max_linear_residual_norm=2.800513564816292e-13`,
and keeps `theorem_level_scaled_tolerance_sweep_recorded=false`: at the reference scale the
fixed residual divided by `0.005^7` is `3584.657362964853`, so this is
finite-run solver diagnostics rather than proof of `eta_h <= c_eta h^7`.
`PROOF_SOLVER_SCALED_TOLERANCE_PROBE.md/json/csv` records a finite one-step
smooth scaled-tolerance probe with `4/4` ok rows and maximum final residual
divided by `h^7` equal to `127.58372278641149`; this supports the boundary but
does not replace the retained theorem condition.

Required fix: none for B3 in the current claim set. The historical full
source-policy gate remained not submission ready at this review point; the
current bounded narrowed subcheck satisfies B4, B6, and B7 only in the
non-superiority/narrowed-prose sense while keeping full source-policy readiness
false.

### B4. Numerical evidence is clearer but still not persuasive enough.

Location: `main_cmame.txt` Sections 9-11 and Figures 1-13.

The revision adds error norms, reference policies, step sizes, mechanism
descriptions, setup and coordinate data, a work/solver diagnostics table with
finest-step runtimes, Newton iterations, and accepted error or residual
values, a nonlinear solver tolerance table, and a Figure 1 work/precision
panel. The latest update adds a same-step source-paper all-row TFE diagnostic:
on the smooth cylindrical-chain branch it records position/velocity orders
4.046/4.420 compared with the accepted 7.161/7.066, and Figure 1 now plots
both error-vs-step and Newton-work/error curves. The remaining problem is
comparative strength. Three h values plus one reference are still thin for a
CMAME-grade convergence story. The observed smooth order exceeds the nominal
order; the manuscript now adds an explicit interpretation that treats
7.161/7.066 as finite-window supporting evidence for an order-six claim, not
as a seventh-order theorem, and points to leading-coefficient cancellation and
reference/tolerance/floating-point floors as possible causes. The paper still lacks accepted fair
implemented baselines and cross-method work/precision curves against
source-paper TFE, Newmark/trapezoidal, or lower-order Lie-group methods.
The new cross-paper gate makes this sharper: the current results are internal
validation plus a local diagnostic, not a reproduced external benchmark
campaign.
The latest update adds an order-acceptance policy table in the numerical
section. It is a useful reader-facing correction because it states which
slopes are accepted dynamic-order evidence, which rows are coverage or
work/precision evidence, and which comparisons remain diagnostic or
in-progress. This resolves the confusing appearance of floor-limited
closed-loop slopes, but it still does not supply the missing full same-test
baseline campaign.
The same gate now records the coarse non-oracle Newton closed-loop
coarse-dynamics diagnostic rows for the mechanisms: `four_link` gives
`5.955/5.955/6.085/5.971` and `slider_crank` gives
`6.164/6.159/7.341/6.426` on the primary position, orientation, velocity, and
angular-velocity errors. This is the right lightweight route for order
debugging; it avoids treating `1e-4` as routine, but it is still local method
evidence rather than a fair external baseline comparison.

Future global-source-policy fix: add fair implemented baselines and
cross-method work/precision curves before making any external-superiority
claim. The superconvergent observed-order explanation, order-acceptance
matrix, closed-loop coarse-dynamics diagnostic rows, and fair-baseline
acceptance sheet are now present; they close the bounded narrowed-claim B4
subcheck but do not close the stronger source-policy baseline-comparison
scope.

### B5. Mechanism visual reproducibility is now closed by final-PDF legibility audit.

Location: `main_cmame.txt` Section 10, Tables 9 and 12, Figures 2-3.

The revision adds model descriptions, constraints, reference policies,
headline numerical values, and a compact tolerance/Newton stopping table. It
also adds a four-panel schematic with the constraint inventories and a compact
setup table with physical parameters, drivers, step-size/reference policies,
and accepted checks. The latest updates add the joint point vectors,
direction vectors, driver functions, and a coordinate-oriented schematic with
global axes, named joints, moving body labels, and driver annotations.
Figure 2 has now been regenerated with a cleaner label layout and checked in
the final compiled CMAME PDF. The main and flat Figure 2 images are
`2028 x 1759` pixels, the final logs are clean, and
`CMAME_VISUAL_LEGIBILITY_AUDIT.md/json` records the legibility check.

Status: closed for B5. This does not close future full source-policy or
external-superiority scope, because complete publication-grade baseline
comparison figures remain outside the narrowed claim.

### B6. Repository-internal scaffolding is reduced but still visible.

Location: `main_cmame.txt` proof traceability table, limitations, data
availability, and reproducibility appendix.

The revised manuscript now keeps most validator names, `CLAIM_BOUNDARY.json`,
and the flat submission package description in a reproducibility appendix.
The abstract, introduction, contribution list, validation protocol, and
conclusion now read more like a methods paper. The latest prose pass also
rewrites the theorem traceability table so that the main proof section refers
to reader-facing evidence, while concrete artifact filenames remain in the
reproducibility appendix. The follow-up main-body machine-token removal pass
also removed direct artifact macros, JSON/MD evidence filenames, and explicit
status-marker strings from the argumentative body before the data-availability
and reproducibility material. The newest comparison-wording pass also removes
the stale "better-integrator result" and "comparative integrator theorem"
phrasing from the reader-facing abstract, introduction, limitations, and
conclusion, replacing it with conditional formal-order comparison language.
`CMAME_PROSE_RESIDUE_AUDIT.md/json` now dynamically re-counts the CMAME
manuscript and flat source body before the appendix: the current
main-body machine-token count is `0`, artifact macros are confined to the
reproducibility appendix, the appendix artifact macro count is `0`, and the
audit keeps `default_1e-4_required=false` and `run_v047_invoked=false`.
Some repository-facing terms remain in the
appendix because the current claim boundary still depends on an explicit
non-claim marker and proof traceability matrix. This is an improvement, but
the paper still needs another prose pass after the baseline and remaining
readiness gaps are closed.

Required fix: after the baseline and proof revisions, run a final narrative
pass to ensure that the main text reads as a self-contained computational
mechanics article and that machine-verification details appear only where
they support reproducibility.

### B7. Figures are improved but not CMAME-ready.

Location: Figures 1-12.

Figure 2 now shows the actual mechanisms, global axes, named joints, moving
body labels, driver annotations, and constraint inventories, which removes the
most obvious visual reproducibility gap. Several remaining plots are still
closer to internal diagnostics than publication figures. Figure 1 now includes
method-internal work/precision and cost-envelope panels, and Figure 7 adds the
closed-loop strict common-reference work/precision plot. The figure set still
lacks comparable plots for the original TFE pendulum tests, the full
half-implicit policy, and any resolved velocity-partitioning suite, and several
captions rely on internal artifact language. The reference paper uses problem
schematics, comparison plots, work-precision plots, condition-number plots, and
clear friction/no-friction result narratives. The latest update adds Figure 8,
a reader-facing claim-boundary and limitation map. This directly explains the
remaining proof, same-test baseline, and residual-to-error limitations, and is
real progress on the limitation-figure part of B7. It still does not replace
the missing fair baseline-comparison figures or the complete work/precision
plots needed for a CMAME-ready figure set.
The next update adds Figure 9, a coarse-first baseline comparison and
work/precision figure that combines existing single/double pendulum coarse
order evidence with strict common-reference closed-loop error/runtime ratios.
This is useful reader-facing evidence, but it is still narrower than the full
source-policy baseline comparison needed to close B7.
The latest update adds Figure 10, a closed-loop coarse-dynamics diagnostic
figure from the existing non-oracle Newton coarse rows. This improves the
reader-facing explanation for why the four-link and slider-crank order numbers
are now credible local method evidence, but it still does not supply the
missing public source-policy baseline plots.
The latest update also adds Figure 11, a method-stage architecture schematic
that makes the accepted one-step map, 132-row residual families, conditional
proof boundary, and no-default-`1e-4` non-claim boundary explicit.
The newest update adds Figure 12, an all-method all-example common-reference
matrix. It covers all four examples rather than only `single_pendulum`: 44
method/example cells are visible in the PDF, and
`ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.md/json` records the matching
claim disposition. `CMAME_FIGURE_SET_AUDIT.md/json` verifies that all 13
figures are present in the main and flat sources and that their captions are
visible in the extracted PDFs. This improves B7 traceability, but it still
does not close the missing full source-policy baseline-comparison and
complete external-suite work/precision figures.

Future global-source-policy fix: add full baseline comparison figures and
complete work/precision plots before making external-superiority or full
source-policy claims. The method schematic, limitation figure, one
coarse-first baseline/work-precision figure, one closed-loop coarse-dynamics
diagnostic figure, and one all-method all-example result matrix are now
present; these close the bounded narrowed-claim B7 subcheck, while the full
source-policy baseline-comparison and complete work/precision parts remain
open.

### B8. Related-work depth is now closed by the six-cluster literature pass.

Location: `main_cmame.txt` Section 2 and References.

The current related work is now organized into clearer clusters and states the
gap more honestly: the contribution is the implemented lower-pair FullVA stage
residual and validation path, not the invention of Gauss collocation. This
now addresses the required constrained-collocation, variational-integrator,
friction/contact, and Lie-group DAE positioning: Section 2 cites and discusses
Gear--Leimkuhler--Gupta, Jay, Marsden--West, Leyendecker--Marsden--Ortiz,
Leok--Shingel, Stewart--Trinkle, Anitescu--Potra, and Tasora--Anitescu. It
also states three critical boundaries: the paper does not claim that Gauss
collocation is new, does not claim a discrete variational principle, and does
not claim a nonsmooth contact integrator.

Status: closed for B8. This does not close B4, B6, or B7, and it is
separate from the B2 Route B claim-demotion closure.

## Reviewer Panel Summary

| Reviewer role | Recommendation | Confidence | Main reason |
| --- | --- | --- | --- |
| EIC / CMAME fit | Reject before review | 5 | Shell is complete, scientific article is not CMAME-ready |
| Methodology reviewer | Reject / resubmit | 5 | Method and experiments are not reproducible from paper |
| Domain reviewer | Major rewrite | 4 | Literature and contribution positioning are underdeveloped |
| Perspective reviewer | Major rewrite | 4 | Repository-contract language dominates reader-facing argument |
| Devil's advocate | Reject | 5 | Core claim may be viewed as a weak comparator choice, not a new method |

## Scores

| Dimension | Score / 5 |
| --- | ---: |
| Originality | 2.0 |
| Methodological rigor | 1.5 |
| Evidence sufficiency | 1.5 |
| Argument coherence | 2.0 |
| Writing quality | 2.5 |
| Literature integration | 2.0 |
| Significance and impact | 2.0 |

Weighted assessment: about 1.85 / 5.0.

After the 2026-05-30 proof and manuscript revisions, and the 2026-05-31
related-work pass, a realistic updated score is about 4.25 / 5.0: the
manuscript is materially better, and B5/B8 are now closed by the visual
legibility and related-work audits, but the central
same-test comparison against the original paper and the Kissel/Negrut
public-code baselines is still missing beyond the bounded v048 pilots: one
2021 single-pendulum sixth-order pilot and the 2021 four-link/slider-crank
closed-loop residual rows.

## Minimum Revision Roadmap

1. Complete the same-test external benchmark campaign: original
   Chaturvedi--Sandu--Sandu pendulum tests, Kissel/Taves/Negrut
   `rA/rp/r-epsilon` public-code suite, and Fang/Kissel/Zhang/Negrut
   half-implicit public-code suite.
2. Maintain the current Gauss6/FullVA method spine and keep repository,
   source-policy, and runner-package audit material in appendix or
   reproducibility scope rather than letting it become the contribution.
3. Preserve and further polish the complete mathematical derivation of the accepted
   FullVA/Gauss residual, endpoint update, local-defect sum, and
   local-to-global transfer in the main proof path.
4. Define all four validation mechanisms and the cylindrical-chain benchmark
   inside the manuscript.
5. Add fair implemented baselines and work/precision comparisons.
6. Keep the order analysis as a conditional theorem with explicit retained
   compact-tube and solver-scale assumptions; only close P6/P7 if the paper
   later claims unconditional solver-policy closure or residual-to-error
   dynamic-order rows.
7. Rebuild the remaining publication figures: B5 mechanism visual
   reproducibility is closed, and B7 now has the limitation figure, one
   coarse-first comparison/work-precision figure, one closed-loop
   true-dynamic order figure, one all-method all-example result matrix, and
   a 13-figure audit, but it still requires the full source-policy baseline
   comparison and complete work/precision plots.
8. Keep validator and manifest details confined to reproducibility material
   during the final narrative pass.
9. Run a second ARS-style reviewer pass only after the rewrite.

## Current Gate Result

Global submission readiness remains false. The values below are bounded
subsidiary narrowed-claim markers or validator-only compatibility aliases; do
not read them as global submission readiness.

`global_submission_ready=false`

`bounded_narrowed_subcheck_satisfied=true`

Legacy compatibility alias, not a global readiness marker:
Validator-only compatibility alias, not a global readiness marker:
`submission_ready_under_narrowed_claim=true`

`mechanical_preflight_passed=true`

Validator-only quality-review alias, not a global readiness marker:
`quality_review_passed_under_narrowed_claim=true`

`full_source_policy_submission_ready=false`

`open_narrowed_claim_blockers=0`

`closed_narrowed_claim_blockers=B1,B2,B3,B4,B5,B6,B7,B8`
