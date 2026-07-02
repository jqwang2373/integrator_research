# Proof Evidence Matrix

This matrix ties the paper's assumption-lemma-theorem chain to concrete
artifacts. It is not a new mathematical claim; it is the audit trail for the
conditional order-six criterion and the conditional order-comparison
proposition.

## Theorem Boundary

- The accepted method-order theorem is a conditional order-six criterion for
  `Gauss6/FullVA`; the active implementation residual-defect route is closed
  by the direct 132-row substitution certificate, while the theorem still
  retains the compact-tube regularity, endpoint, and inexact-Newton scale
  contracts stated in the manuscript.
- The comparison result is the conditional order-comparison proposition for
  `Gauss6/FullVA`: within the stated smooth FullVA contract, the method-order
  claim is six while the local paper-style `m=3` TFE formula target has
  expected order five.
- The method-order claim is `6`.
- Smooth observed position/velocity orders are `7.161/7.066`.
- The comparator is the local paper-style `m=3` Gauss-Lobatto TFE formula
  target with expected order `5`.
- The four accepted local method examples are `single_pendulum`, `double_pendulum`,
  `four_link`, and `slider_crank`.
- `ORDER_ACCEPTANCE_GATE.md` records the example-level order boundary:
  `single_pendulum` and `double_pendulum` have accepted dynamic order rows,
  while `four_link` and `slider_crank` are accepted mechanism coverage rows
  with not accepted external dynamic order.
- The same gate also records closed-loop coarse-dynamics diagnostics
  for `four_link` and `slider_crank` from the coarse non-oracle Newton sweep
  at `h=[0.1,0.05,0.025]` against `reference_h=0.0125`: the primary-state
  order candidates are `5.955/5.955/6.085/5.971` and
  `6.164/6.159/7.341/6.426`, respectively. These are local method evidence,
  not an external superiority claim. They are finite-window diagnostics only:
  they do not instantiate the residual-to-error implication, do not close P7,
  and do not promote four-link or slider-crank to accepted dynamic-order
  examples.
- `full_tfe_stage_replacement=false` remains part of the theorem statement
  boundary.

## Proof Route Legend

The active theorem route is the direct residual-bridge/Kantorovich route. PC2
is supplied by the implemented 132-row FullVA residual evaluated on the lifted
Gauss stage: the 96 non-dynamic rows supply the row-local `O(h^7)` certificate,
and the 36 Newton--Euler rows vanish by the D5 direct-substitution certificate
on the same smooth branch. This full residual input is then consumed by the
stage-root perturbation, endpoint-closure, inexact-Newton, and local-to-global
lemmas.

The primitive/Taylor route is a stricter optional verification route for the
36 Newton--Euler rows. Its diagnostic certificate records `162/162`
conditional reduction templates, but `0/162` actual primitive-route Taylor
bounds and five open primitive lift assumptions. Therefore it is not the PC2
route used by the theorem, and its open status does not reopen the active
direct residual bridge. Conversely, the direct theorem route does not certify
primitive subterm bounds.

The retained theorem interfaces remain separate from that discharged
residual input. P1/P2/P3, the P4 binding convention, and P6 fix the compact
branch, row scaling, implementation binding, endpoint/inverse/stability
conditions, and solver scale. P7 residual-to-error promotion remains open for
residual-only mechanism rows and source-policy rows. Thus finite residual
tables, reaction checks, fixed-tolerance logs, and source-policy diagnostics
can support consistency, but they do not replace theorem-domain hypotheses or
promote closed-loop residual rows to trajectory-order evidence.

One-way evidence rule: all finite h-sweeps, solver probes, common-reference
tables, reaction residuals, and source-policy diagnostics are downstream
checks of a theorem instance; none is allowed to back-propagate into the
theorem interface. In particular, observed order slopes do not close P1/P2
compact-tube hypotheses, finite residuals do not close the P6 solver-policy
condition, residual tables do not close the P7 residual-to-error boundary, and
common-reference wins do not create source-policy or external-superiority
claims. The only active route that supplies the stage-residual input remains
the direct 96+36 residual bridge on the selected Gauss-predictor branch.

## Obligation Matrix

| Proof obligation | Artifact evidence | Validator evidence | Status |
| --- | --- | --- | --- |
| Define the accepted one-step map. | `main_cmame.tex`, `main_concise.tex`, `CLAIM_BOUNDARY.json`, and `summary_v047.json` record `Gauss6/FullVA` and the 132-row stage residual boundary. | `validate_cmame_submission.py`, `validate_concise_paper.py`, `validate_paper_claims.py`, `validate_paper_package.py` | Accepted for the current method path. |
| Support sixth-order smooth behavior. | `main_cmame.tex` states `Theorem [Conditional sixth-order error theorem for the accepted branch-selected Gauss6/FullVA map]`: if the accepted-branch P1--P3/P6 interfaces, implementation residual-defect, endpoint-closure, and inexact-Newton scale contracts hold, then the reduced-chart and reported position--velocity grid conclusion has the sixth-order scope stated by the theorem.  The package shorthand is the local defect `O(h^7)` and global grid error `O(h^6)` statement only under those retained interfaces; it is not an unconditional method-order, solver-policy, residual-to-error, source-policy, or primitive/Taylor claim. `cylindrical_chain_convergence.csv` and `summary_v047.json` record smooth orders `7.161/7.066` over `h=[0.04,0.02,0.01]` against `reference_h=0.005`. `PROOF_NUMERICAL_SCALE_AUDIT.md/json` re-reads the same rows and records finite-run global fits `7.160828/7.066183`; it also records bounded h^6-normalized smooth-error ratios. | `validate_concise_paper.py`, `validate_v047_outputs.py`, `validate_proof_numerical_scale_audit.py`, `validate_pipeline_outputs.py` | Conditional within the artifact scope; the h-sweep is a finite-run scale diagnostic and does not discharge the retained compact-tube, endpoint, or solver-scale theorem interfaces. |
| State the mathematical regularity boundary. | `main_cmame.tex` states the full-rank constraint, nonsingular projected mass, smooth reduced Lie-group chart, isolated Newton solution, uniformly invertible stage Jacobian, smooth FullVA lift, implementation residual-defect condition, endpoint-closure condition, and the compact-tube branch-selected `eta_h^tube <= c_eta h^7` solver envelope. The reported-grid maximum `eta_h^reported=max_n eta_{h,n}` is only the accepted trajectory specialization from the same reduced-chart initial state and Gauss-predictor Newton branch, while arbitrary Newton initializations and remote nonlinear roots are excluded. The one-step `O(h^7)` perturbation is no longer assumed as a shortcut; it is decomposed into proof obligations. | `validate_cmame_submission.py`, `validate_paper_package.py`, `validate_cmame_proof_contract_gate.py` | Conditional proof boundary is explicit and noncircular; the accepted implementation-defect route is closed by direct substitution, while theorem-level solver policy and residual-to-error routes remain conditional/open. |
| Isolate endpoint-closure order impact. | `main_cmame.tex` now includes an endpoint-closure perturbation lemma: if the same-branch endpoint functional \(E\) corrected by \(\mathcal C_h\) has local defect `O(h^7)` and its closure Jacobian has a uniformly bounded right inverse, the minimum-norm endpoint correction is also `O(h^7)`. The manuscript defines \(E\) as the velocity-level/KKT closure subsystem, not every raw endpoint diagnostic; the raw position endpoint defect is a separate monitor. `PROOF_NUMERICAL_SCALE_AUDIT.md/json` records raw endpoint monitor global fits `5.985101/6.072291` and explicitly keeps them as finite-run scale diagnostics, not P2 endpoint closure proof. | `validate_cmame_submission.py`, `validate_proof_numerical_scale_audit.py`, `validate_paper_package.py` | Endpoint projection part is proved conditionally and supported by finite-run global scale diagnostics; the accepted stage-row implementation defect is handled separately by the direct 132-row substitution route, while the endpoint-ball and right-inverse hypotheses remain retained. |
| Prove mathematical stage-row consistency. | `main_cmame.tex` now includes a FullVA stage-row lift lemma: under the smooth FullVA lift, the accepted mathematical residual rows are the lifted reduced Gauss stage equations or pointwise constrained-dynamics rows, so their defect at the lifted Gauss stage is zero. | `validate_cmame_submission.py`, `validate_paper_package.py` | Mathematical stage-row proof is closed under the smooth-lift assumption. |
| Certify the accepted implementation row identity. | `IMPLEMENTATION_FIDELITY_CERTIFICATE.md` maps the 132 accepted cylindrical-chain rows to `residual_cylindrical_chain`, `STAGE_FUNCTIONAL_BLOCK_LAYOUT`, and `R_JAC = jax.jacfwd(...)` in `run_v047.py`. `DYNAMIC_ROW_ORACLE_GATE.md` imports the same source, evaluates the accepted residual and AD Jacobian on a canonical smooth-state runtime probe, verifies the six row-family slices partition all 132 rows, cross-checks `R_INDEPENDENT_STAGE_FUNCTIONAL_BLOCKS` against the weighted accepted residual row families, adds a full independent formula-row oracle covering all 132 runtime formula rows, and checks the formula-row AD Jacobian against `R_JAC` on three deterministic probes. `KINEMATIC_ROW_DEFECT_CERTIFICATE.md/json` records the 96-row non-dynamic certificate on the smooth accepted FullVA lift. `D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE.md/json`, `NEWTON_EULER_DYNAMIC_ROW_CLOSURE_CONTRACT.md/json`, and `PROOF_CLOSURE_MANIFEST.md/json` close the accepted direct-substitution route: the 96 non-dynamic rows have an `O(h^7)` lift certificate and the 36 dynamic rows have zero residual on `Z_G`, giving the required stage-residual `O(h^7)` implementation defect. `NEWTON_EULER_DEFECT_OBLIGATION_GATE.md/json` still records one open Newton--Euler symbolic proof obligation (D5) and five closed sub-obligations (D1, D2, D3, D4, D6). `NEWTON_EULER_BALANCE_IDENTITY_AUDIT.md/json` closes D1/D2 source-level Newton--Euler balance identities for all 36 dynamic rows. `NEWTON_EULER_VIRTUAL_WORK_WRENCH_AUDIT.md/json` records D3 virtual-work sign-skeleton traceability for all 36 dynamic rows, verifies the two template virtual-work identities, and proves six row-expanded lower-pair multiplier identities for the implemented point and axis multiplier sites. `SMOOTH_FORCE_LIFT_CERTIFICATE.md/json` closes D4 smooth force/friction C7 lift on the accepted compact proof tube. `NEWTON_EULER_ROW_ORDERING_SCALING_AD_AUDIT.md/json` closes D6 row ordering, unweighted residual scaling, and accepted AD binding for all 36 dynamic rows. `NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.md/json` records body-specific proximal/distal force and torque sign expansions plus the D1/D2/D3/D4/D6 closed sub-obligations, with body0/body1 coverage `18/18`, but keeps the optional D5 symbolic `O(h^7)` certificate route open. | `validate_implementation_fidelity_certificate.py`, `validate_dynamic_row_oracle_gate.py`, `validate_kinematic_row_defect_certificate.py`, `validate_newton_euler_defect_obligation_gate.py`, `validate_newton_euler_balance_identity_audit.py`, `validate_newton_euler_virtual_work_wrench_audit.py`, `validate_smooth_force_lift_certificate.py`, `validate_newton_euler_row_ordering_scaling_ad_audit.py`, `validate_newton_euler_symbolic_defect_certificate.py`, `validate_paper_package.py` | Static source identity plus runtime row-layout/block-functional, full formula-row, multi-probe formula-row AD Jacobian oracle, 96-row non-dynamic certificate, direct-substitution stage-residual closure, 36-row dynamic obligation ledger with D1/D2/D3/D4/D6 closed, body-specific wrench-expansion traceability, virtual-work identity, smooth-force C7 lift, balance-identity closure, and row-ordering/scaling/AD binding accepted; global dynamic symbolic-oracle completion and the optional symbolic D5 certificate remain open without reopening the accepted direct proof. |
| Reduce implementation row impact to a residual-defect certificate. | `main_cmame.tex` includes a stage-residual perturbation criterion: if the implemented accepted FullVA residual evaluated at the Gauss stage is `O(h^7)` and the stage Jacobian remains uniformly invertible, the accepted stage solution differs from the Gauss stage by `O(h^7)`. | `validate_cmame_submission.py`, `validate_paper_package.py` | Criterion proved and the active direct implementation-defect route is closed; the optional primitive dynamic symbolic-oracle route remains open without reopening the accepted proof route. |
| Specify the inexact Newton solver scale. | `main_cmame.tex` now includes an inexact-Newton tolerance lemma and states the proof-level compact-tube policy `eta_h^tube <= c_eta h^7`; the reported-grid maximum `eta_h^reported=max_n eta_{h,n}` over accepted branch-selected Newton solves initialized from the Gauss predictor is only the accepted trajectory specialization. `PROOF_NUMERICAL_SCALE_AUDIT.md/json` explicitly records that the h-sweep scale diagnostic is not a solver proof. `PROOF_SOLVER_SCALE_AUDIT.md/json` re-reads summary-level solver residuals, records smooth reference `max_linear_residual_norm=2.800513564816292e-13`, and computes the smooth reference residual divided by `0.005^7` as `3584.657362964853`; it also records a finite scaled-tolerance trajectory probe with `4/4` ok rows, `30` checked steps, and maximum final residual divided by `h^7` equal to `210.89078604575462`. `PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.md/json/csv` adds a finite tolerance-regime sweep comparing fixed `1e-10`, `c h^7`, and `c h^8`; all `12` policy rows and `90` checked steps converge, with fixed and `h^7` position/velocity orders `6.946347411176867/6.608089993735075` and `h^8` orders `6.946365976765468/6.608137477881583`. Therefore `finite_tolerance_regime_sweep_recorded=true`, `theorem_level_scaled_tolerance_sweep_recorded=false`, `newton_residual_norm_recorded=false`, and `eta_h_O_h7_solver_policy_evidence=false` remain explicit; recorded fixed-tolerance runs are finite-run data and do not prove branch selection for arbitrary Newton initializations. | `validate_cmame_submission.py`, `validate_proof_numerical_scale_audit.py`, `validate_proof_solver_scale_audit.py`, `validate_proof_solver_scaled_tolerance_trajectory_probe.py`, `validate_proof_solver_tolerance_regime_sweep.py`, `validate_paper_package.py` | Solver-error scaling is mathematically stated; recorded fixed-tolerance runs plus the finite short-trajectory scaled-policy and tolerance-regime probes are finite-run data rather than an asymptotic proof sweep. |
| Separate comparator order from implemented residual. | `main_cmame.tex` states `Lemma [Order of the local paper-style TFE target]`; `SOURCE_PAPER_COMPARISON.md` records local `m=3` Gauss-Lobatto TFE expected order `2m-1=5`. | `validate_source_paper_comparison.py` | Comparator boundary accepted. |
| State conditional order exceedance for the paper-facing comparison. | `CLAIM_BOUNDARY.json` records method order `6`, smooth orders `7.161/7.066`, and comparator expected order `5`. `main_cmame.tex` now states `Proposition [Conditional order comparison]`: within the stated smooth FullVA contract, `Gauss6/FullVA` has higher formal order than the local paper-style `m=3` TFE formula target. The larger fitted slopes are supporting evidence for at least sixth-order smooth behavior, not a seventh-order theorem. | `validate_proof_evidence_matrix.py`, `validate_source_paper_comparison.py`, `validate_order_acceptance_gate.py` | Accepted as a conditional formal-order comparison within the order-six theorem boundary. |
| Enforce the example-level order boundary. | `ORDER_ACCEPTANCE_GATE.md` and `ORDER_ACCEPTANCE_GATE.json` separate method-order rows from mechanism-coverage rows: `single_pendulum` and `double_pendulum` support accepted dynamic order, while `four_link` and `slider_crank` remain not accepted external dynamic order. The gate also records the coarse probe `h=[0.1,0.05,0.025]`, `11/12` ok rows, and `accepted_dynamic_order_count=0`. The closed-loop coarse-dynamics diagnostic artifact `closed_loop_true_dynamic_newton_coarse_order.json` has `6/6` ok rows and closed-loop coarse-dynamics diagnostic examples `2`, with primary-state diagnostic slopes `5.955/5.955/6.085/5.971` for `four_link` and `6.164/6.159/7.341/6.426` for `slider_crank`; `default_1e-4_required=false`, `heavy_numerical_run_invoked=false`, and `external_superiority_claim=false`. | `validate_order_acceptance_gate.py`, `validate_proof_evidence_matrix.py`, `validate_paper_package.py` | Example-level order boundary accepted; local closed-loop diagnostics are recorded, but external superiority and full same-test dynamic-order acceptance remain open. |
| Block unsupported residual-to-error promotion. | `closed_loop_residual_to_error_theorem_obligations.md/.json/.csv` records seven blocking obligations before the `four_link`/`slider_crank` residual surrogate can be promoted: dynamic residual identity, `O(h^7)` residual consistency rate, closed-loop DAE stability or inf-sup bound, calibrated non-floor-limited estimator, reference-floor exclusion, coarse-first accepted campaign, and manuscript theorem/proof. | `validate_closed_loop_residual_to_error_theorem_obligations.py`, `validate_pipeline_outputs.py` | Open proof route; `accepted_residual_to_error_theorem=false` and `accepted_dynamic_order_count=0`. |
| Verify four-example support. | `summary_v047.json`, ASME CSV files, and paper figures record `single_pendulum`, `double_pendulum`, `four_link`, and `slider_crank`; the v048 matrix marks four-link/slider-crank closed-loop order columns as not interpreted because they are roundoff-floor kinematic/reaction rows. | `validate_four_asme_minimal.py`, `validate_paper_package.py`, `validate_pipeline_outputs.py` | Four examples accepted as mechanism coverage; only the dynamic rows support order claims. |
| Preserve non-claims. | `CLAIM_BOUNDARY.json`, `SOURCE_PAPER_COMPARISON.md`, `main_cmame.tex`, and `SUBMISSION_PACKET.md` record that complete source-paper residual reproduction is not claimed. | `validate_cmame_submission.py`, `validate_submission_bundle.py`, `validate_proof_evidence_matrix.py` | Non-claims enforced. |
| Keep full-TFE replacement open. | `FULL_TFE_REPLACEMENT_GAP_LEDGER.md`, `FULL_TFE_REPAIR_SPEC.md`, and `CLAIM_BOUNDARY.json` record `full_tfe_stage_replacement=false`. | `validate_full_tfe_gap.py`, `validate_full_tfe_repair_spec.py`, `validate_pipeline_outputs.py` | Open gate, not a contradiction of the theorem. |

## Accepted Proof Reading

The proof should be read as a conditional, artifact-backed criterion:
if the accepted-path regularity and local perturbation-scale assumptions hold
for the recorded smooth branch, then the accepted branch-selected
`Gauss6/FullVA` map has the theorem's displayed `O(h^7)` local defect and
`O(h^6)` reduced-chart/reported position--velocity grid conclusion by
three-stage Gauss collocation on the reduced constrained flow.  The phrase
``order six'' in this matrix is therefore shorthand for that conditional
grid-point conclusion, not an unconditional method-order, solver-policy,
primitive/Taylor, residual-to-error, or source-policy claim. The
endpoint-closure lemma proves one part of the perturbation transfer:
a right-invertible local closure projection for the same-object endpoint
functional \(E\) with local `O(h^7)` defect does not reduce the asymptotic
order. The FullVA stage-row lift lemma proves
the mathematical stage-row part under the smooth-lift assumption: the accepted
row families are a coordinate lift of reduced Gauss collocation plus
pointwise constrained dynamics. The stage-residual perturbation criterion now
shows how implementation error would enter. The implementation-fidelity
certificate supplies a static source-identity audit: the accepted 132-row
layout, `residual_cylindrical_chain`, and `R_JAC` are tied to one code path.
The dynamic row-oracle gate now adds a runtime row-layout and block-functional
check: the accepted residual has shape 132, the dense AD Jacobian has shape 132
by 132, the six row-family slices are finite and non-overlapping on a canonical
smooth probe, and `R_INDEPENDENT_STAGE_FUNCTIONAL_BLOCKS` agrees with the
weighted accepted residual row families on a deterministic small stage vector.
The proof numerical scale audit separately re-reads the accepted smooth
h-sweep and records global smooth-error fits `7.160828/7.066183` plus raw
endpoint monitor fits `5.985101/6.072291`; this supports the visible
order-six global budget and endpoint scale consistency. The raw position
monitor is not \(E\), so these finite rows do not discharge P2 endpoint
closure proof; they are finite-run scale diagnostics only.
The proof solver-scale audit separately re-reads summary-level residual
records and shows why the recorded fixed residuals are not a branch-selected
scaled `eta_h <= c_eta h^7` tolerance policy: the smooth reference linear residual is
`2.800513564816292e-13`, and that fixed scale divided by `0.005^7` is
`3584.657362964853`.
It also records a finite tolerance-regime sweep comparing fixed `1e-10`,
`c h^7`, and `c h^8` residual targets over the same short smooth window; the
fixed and `h^7` rows give position/velocity orders
`6.946347411176867/6.608089993735075`, while the `h^8` row gives
`6.946365976765468/6.608137477881583`. This is finite-window evidence only:
`finite_tolerance_regime_sweep_recorded=true` does not change
`theorem_level_scaled_tolerance_sweep_recorded=false` or
`eta_h_O_h7_solver_policy_evidence=false`.
It also adds formula-level row oracles: first a partial independent
formula-row oracle for 96 non-dynamic rows in the translational/rotational
kinematic and lower-pair constraint families, and now a full independent
formula-row oracle covering all 132 runtime formula rows, including the
`newton_euler_weak_balance` rows. It further adds a multi-probe formula-row AD
Jacobian oracle: `jax.jacfwd` of the independent formula-row vector agrees
with `R_JAC` on three deterministic probes. `KINEMATIC_ROW_DEFECT_CERTIFICATE.md/json`
adds a partial proof-scope certificate for those 96 non-dynamic rows on the
smooth accepted FullVA lift. `NEWTON_EULER_DEFECT_OBLIGATION_GATE.md/json`
then decomposes the `newton_euler_weak_balance` gap into one open
Newton--Euler symbolic proof obligation and five closed D1/D2/D3/D4/D6
sub-obligations: the Gauss-stage dynamic defect rate remains open, while
translational balance identity, rotational balance identity, multiplier-wrench
consistency, smooth force/friction lift consistency, and
row-ordering/scaling/AD binding are closed for the implemented lower-pair
multiplier sites and row layout. The optional primitive/global dynamic
symbolic lane remains open; the independent symbolic oracle remains open
without reopening the active direct PC2 residual bridge.
`NEWTON_EULER_BALANCE_IDENTITY_AUDIT.md/json` closes the D1/D2 source-level
Newton--Euler balance identities for all 36 dynamic rows.
`NEWTON_EULER_VIRTUAL_WORK_WRENCH_AUDIT.md/json` now checks the D3
virtual-work sign-skeleton traceability for all 36 dynamic rows across nine
force and torque transfer sites and verifies the template virtual-work identity
for the lower-pair point and axis rows. It also proves six row-expanded
lower-pair multiplier identities in the implemented site ordering.
The row-expanded multiplier-wrench identity accepted by this audit closes D3.
`NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.md/json`
now adds body-specific proximal/distal force and torque sign expansions for
all 36 dynamic rows, with body0/body1 coverage `18/18`, and records the same
virtual-work sign-skeleton/template/row-expanded identity traceability; this
narrows traceability and closes the D1/D2 balance identities, but still does
not prove the D5 `O(h^7)` defect bound. The D5 primitive-ledger artifacts
also include `D5_P_ACC_PA2_WEIGHTED_INVERSE_AUDIT.md/json`, which records
the finite weighted inverse constants for the PA2 acceleration-lift target:
the same weighted non-dynamic operator gives bounded finite control of
`h delta A`, but does not prove a uniform unweighted acceleration lift. PA2,
`P_acc`, and PC2 remain open. They also include
`D5_P_LAMBDA_INF_SUP_PROBE.md/json/csv`, which evaluates the
finite multiplier-column block `D_lambda R_dyn` on solved one-step stages at
`h=0.04,0.02,0.01` and records rank `24/24` with a small finite condition
number; this supports the PL2 proof target but is explicitly not a uniform
compact-tube inf-sup proof. `D5_P_LAMBDA_PL2_GEOMETRIC_MARGIN_AUDIT.md/json`
records the PL2 geometric-margin route by separating the stage-local
dynamic-lambda, translational normal-force, rotational axis-torque, and
direct-sum subblocks; the finite stage-local margins remain diagnostic and do
not close the compact-tube transversality margin. `D5_P_LAMBDA_D3_NONCIRCULARITY_AUDIT.md/json`
closes PL3 by proving that the D3 row-expanded wrench identity is used only as
a non-circular algebraic mapping interface, not as a multiplier-rate or
inf-sup proof. PL2 is proved as the geometric-margin interface and PL4 is
closed only as a conditional propagation implication; the actual `P_lambda`
lift and PC2 remain open.
What remains open is a stronger
dynamic symbolic-defect oracle as a supplemental certificate route; it is no
longer the active closure route for the accepted `O(h^7)` implementation
defect, which is closed by direct substitution.
The D5 dynamic symbolic defect proof remains open as a supplemental route, not
as the active proof-closure route. The inexact-Newton lemma states the
compact-tube solver envelope `eta_h^tube<=c_eta h^7` needed for the asymptotic theorem
on the accepted branch selected from the Gauss predictor; the reported
`eta_h^reported=max_n eta_{h,n}` is only a finite trajectory specialization. The current
fixed-tolerance runs remain finite-run evidence, not a scaled-tolerance proof
sweep or a branch-selection theorem for arbitrary Newton initializations. The
generated h-sweep and four-example validators provide the evidence
needed for the paper-facing comparison against the order-five local TFE
target; the local target order is fixed by the proof-level convention
`p_TFE(m)=2m-1`, so `m=3` gives `5`. The comparison is now phrased as a
conditional order-comparison proposition, not as a second theorem of external
baseline superiority. The example-level order boundary in
`ORDER_ACCEPTANCE_GATE.md` is part of this reading: closed-loop `four_link`
and `slider_crank` rows are mechanism-coverage evidence and not accepted
external dynamic order. The residual-to-error theorem obligation gate is also
part of this reading: small closed-loop reaction residuals do not imply
trajectory order until the seven blocking obligations are closed, so
`accepted_residual_to_error_theorem=false` remains a proof boundary. The proof does not claim a complete
source-paper TFE residual
implementation, independent baseline superiority in work/precision, or
robustness in the nonsmooth sharp-friction coarse regime.
