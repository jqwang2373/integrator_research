# CMAME Proof Contract Gate

> Superseded on 2026-09-17 by EXACT_STAGE_IDENTITY_GATE: this gate pinned the retired 96-row/D5/primitive-Taylor proof route. Kept as an archived provenance record; its validator is no longer in the package chain.

Status: **CONDITIONAL CONTRACT RECORDED - GLOBAL SUBMISSION GATES OPEN**

This gate records the proof boundary used by the CMAME manuscript. It is not a
new theorem and it does not make the manuscript submission ready. Its purpose is to
make the conditional theorem language machine-checkable so the manuscript
cannot silently promote finite-run residual data into an unconditional proof.
Here `submission_ready=false` is a theorem-level/global proof-contract marker;
it is not a reversal of the separate narrowed-claim package decision.

- Submission-ready scope: `theorem_level_global_proof_contract_not_narrowed_claim_package_decision`.
- Proof contract gate scope: `conditional_theorem_contract_with_eta_h_and_residual_to_error_boundaries`.
- B4/B6/B7 narrowed-claim statuses: `closed/closed/closed`.
- Remaining global submission boundaries: `full_source_policy_package_ready,theorem_level_eta_h_solver_policy_evidence,closed_residual_to_error_theorem_for_mechanism_rows`.

## Objective Blocker Matrix

The global objective blocker matrix remains:

- `blocker_open_by_id=OC4:True,OC6:True,OC12:True`
- `blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready`
- `blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False`

This matrix is inherited from `OBJECTIVE_COMPLETION_AUDIT.json`; it keeps
OC4, OC6, and OC12 open and does not authorize B4/source-policy execution.

## Manuscript Theorem Traceability

This gate carries the reader-facing theorem/proof traceability from
`PROOF_CLOSURE_MANIFEST.json` into the proof-contract boundary. The labels,
conditional theorem boundary, proof dependency graph, proof traceability table,
and dynamic proof closure matrix are present in both the main and flat TeX
sources, but this traceability does not change the proof-closure state.

- Theorem labels/boundary/mapped: `True/True/True`.
- Proof dependency/traceability/dynamic matrix: `True/True/True`.
- Primitive-route and residual nonpromotion boundaries: `True/True`.
- Eta condition/closure and fixed-tolerance proof: `True/False/False`.
- Residual/source-policy-full-TFE not promoted: `True/True`; no-state-change `True`.
- Manuscript anchor map: `True`; label anchors `24`; theorem-interface/P7-output-boundary anchors `7`; IDs `P1,P2,P3,P4,P5,P6,P7`; proof-claim map match `True`.
- Reader-facing theorem-interface split: theorem interfaces `P1--P6`; P7 is an output nonclaim/residual-to-error boundary anchor, not a theorem premise.

## Accepted Proof Mode

- Proof mode: `conditional_consistency_transfer`
- Accepted method: `Gauss6/FullVA`
- Accepted method-order claim: `6`
- Local defect order in the theorem: `O(h^7)`
- Global error order in the theorem: `O(h^6)`
- Comparator: local paper-style `m=3` Gauss-Lobatto TFE formula target
- Comparator expected order: `5`

The theorem is conditional on the smooth accepted-path contract in
`main_cmame.tex`: regular constrained branch, smooth FullVA lift, uniformly
invertible stage Jacobian on the compact-tube Gauss-predictor branch,
accepted one-step stability scale
`||Psi_h(y)-Psi_h(ybar)|| <= (1+C_s h)||y-ybar||` with tube-retention
bootstrap on the accepted compact tube, implemented residual
defect `O(h^7)`, endpoint closure perturbation `O(h^7)` under a local
closed endpoint anchor plus endpoint-ball margin and right-inverse /
compact-tube splitting bound, with raw endpoint closure defect constant
`C_{E,raw}` and explicit endpoint perturbation constant
`C_E=4 M_E^ri C_{E,raw}`, and
an inexact Newton compact-tube tolerance scale `eta_h^tube <= c_eta h^7` under a strong local
residual inverse /
averaged-Jacobian perturbation bound. The solver scale is branch-selected and
per step: the theorem uses
`eta_h^tube <= c_eta h^7` on the compact proof tube, while the reported-grid
maximum `eta_h^reported=max_{0<=n<N} eta_{h,n}` is only its finite trajectory
specialization over Newton solves initialized from the Gauss predictor on the
same accepted branch and same reduced-chart initial state. It is bounded by
`c_eta h^7` only when the retained compact-tube envelope has already been
instantiated on that reported trajectory. It does not assert that arbitrary Newton initializations, fixed
tolerances, or remote nonlinear roots select that branch.
The Gauss truncation term is recorded as an explicit uniform bound
`||Psi_h^G(y)-phi_h(y)|| <= C_G h^7`, with `C_G` uniform on the compact
trajectory tube after shrinking the admissible step-size window if needed.
The stage-residual perturbation step is also recorded as an explicit
constant transfer: the accepted stage root satisfies
`||Z_A-Z_G|| <= C_Z h^7` with `C_Z=2 M C_R`, and the endpoint stage-root
perturbation satisfies `||Psi_h^A(y)-Psi_h^G(y)|| <= C_A h^7` with
`C_A=M_E C_Z`. The local accepted root is obtained by the
stage-residual/Kantorovich perturbation lemma after the Gauss-predictor branch
neighborhood, inverse bound, and derivative bounds are fixed; it is not assumed
as a separate isolated-root premise in the regularity assumption.
The four-term local defect decomposition also retains a uniform-constant
contract: the constants in the Gauss truncation, stage-root perturbation,
endpoint-closure, and inexact-Newton bounds are uniform in `y` on the compact
proof tube and uniform in the accepted step index `n<N`; the nonlinear-solver
term is controlled through the compact-tube envelope `eta_h^tube`, with the
reported-grid accepted-branch maximum `eta_h^reported=max_n eta_{h,n}` used
only as a trajectory specialization.
The endpoint-closure contribution is recorded with the explicit raw-defect
transfer `||E(z_u)|| <= C_{E,raw} h^7` and
`||Delta z_E|| <= C_E h^7`, where `C_E=4 M_E^ri C_{E,raw}`.
The inexact-Newton residual-to-endpoint-output transfer is recorded with the
explicit bound `||P_h(Ztilde_A)-P_h(Z_A)|| <= C_N eta_h`, where
`P_h=C_h o E_h` is the full endpoint-output map and `M_N` includes the local
endpoint-closure Lipschitz factor; `C_N=2 M_A M_N`. Under the accepted-branch theorem policy
`eta_h^tube <= c_eta h^7`, this is absorbed as the explicit scaled endpoint bound
`C_N c_eta h^7`.
After the accepted compact-tube bound `eta_h^tube <= c_eta h^7`, the theorem proof
defines an explicit local-defect constant
`C_loc=C_G+C_A+C_E+C_N c_eta` and passes that single uniform constant to the
local-to-global step. The local-to-global step records the explicit
Gronwall factor
`Gamma_s(T)=(exp(C_s T)-1)/C_s` with limiting value `T` at `C_s=0`,
the reduced-chart grid constant `C_red=C_loc Gamma_s(T)`, and the final
reporting constant `C_qv=C_{\mathcal R} C_red`, where `C_{\mathcal R}` is the chart-reporting
map derivative bound and is distinct from the accepted residual-defect
constant.
The local-to-global transfer is a same-initial-state reported-grid estimate on
the accepted reduced-chart branch. The final reported `(q,v)` error bound is a grid maximum
over the same reported time grid, not an endpoint-only statement. The reported
time grid is defined by `t_n=n h`, and exact final-time divisibility is not
required for the lemma statement.

The manuscript no longer uses a circular one-step perturbation shortcut as an
assumption. The proof contract is decomposed into separate proof obligations:
mathematical FullVA lift consistency, implementation residual-defect
certification, endpoint-closure perturbation, and inexact-Newton scaling.

## Retained Proof Conditions and Boundaries

The following conditions and boundaries remain active. The accepted
stage-residual defect route is closed by direct substitution, but this does
not make the theorem unconditional and does not by itself close the
global/full-source-policy package boundaries or the future full-source-policy
figure/prose lanes. B4/B6/B7 narrowed-claim closure is recorded separately in
the blocker-closure and review-agent gates.

- `dynamic_symbolic_oracle_complete=false`
- the stage-residual perturbation proof uses a compact-tube inverse condition
  on the Gauss-predictor branch; finite rank probes or pointwise solved-stage
  Jacobian checks are not a compact-tube inverse proof
- the local-to-global proof uses the one-step stability scale `1+C_s h`, not
  ordinary compact-tube Lipschitz continuity alone
- the local-to-global proof also retains a tube-retention bootstrap; it is not
  an invariant-region proof for remote nonlinear roots or residual-only
  mechanism rows
- the endpoint-closure estimate uses a local right-inverse / compact-tube
  splitting bound anchored at a closed accepted endpoint, with an
  endpoint-ball margin that keeps the correction inside the local ball;
  pointwise
  right-invertibility at one endpoint alone is not used as a shortcut
- the endpoint-closure raw defect and correction are tied by explicit constants:
  `||E(z_u)|| <= C_{E,raw} h^7` and
  `||Delta z_E|| <= C_E h^7` with `C_E=4 M_E^ri C_{E,raw}`
- the inexact-Newton estimate uses a strong local residual inverse and
  averaged-Jacobian perturbation bound; pointwise Jacobian invertibility alone
  is not used as a shortcut
- the inexact-Newton endpoint perturbation is measured through the full
  endpoint-output map `P_h=C_h o E_h`, so the local endpoint-closure Lipschitz
  factor is included in `M_N`
- the theorem-level solver contract is the compact-tube branch-selected
  residual envelope `eta_h^tube <= c_eta h^7`; the reported-grid maximum
  `eta_h^reported=max_n eta_{h,n}` is only a trajectory specialization and is
  not a claim about arbitrary Newton initializations, fixed tolerances, or
  remote nonlinear roots
- the Gauss truncation term has an explicit uniform constant `C_G` on the
  compact trajectory tube
- the stage-residual perturbation step has explicit constants
  `C_Z=2 M C_R` and `C_A=M_E C_Z`
- local accepted root existence is supplied by the stage-residual/Kantorovich
  lemma on the Gauss-predictor branch, not assumed as an isolated-root premise
- the four-term local defect decomposition uses constants uniform in `y` on
  the compact proof tube and uniform in accepted steps; the Newton term is
  controlled by `eta_h^tube`, with `eta_h^reported=max_n eta_{h,n}` recorded
  only as the reported-grid accepted-branch maximum
- the accepted compact-tube `eta_h^tube <= c_eta h^7` bound is absorbed into the explicit
  local-defect constant sum `C_loc=C_G+C_A+C_E+C_N c_eta`
- the inexact-Newton endpoint perturbation is explicitly scaled as
  `C_N c_eta h^7` under the accepted-branch theorem policy
- the local-to-global and reporting transfers use explicit constants:
  `C_red=C_loc Gamma_s(T)` and `C_qv=C_{\mathcal R} C_red`, with `C_{\mathcal R}` kept
  distinct from the residual-defect constant
- the local-to-global transfer is a same-initial-state reported-grid estimate
  on the accepted reduced-chart branch, and the reported `(q,v)` bound uses the same reported
  time grid as a grid maximum
- the reported time grid is defined by `t_n=n h`; exact final-time
  divisibility is not required
- `B1_AD_EXPANDED_SYMBOLIC_ORACLE_CLOSURE_CERTIFICATE.md/json` closes the B1
  AD-expanded symbolic oracle by differentiating the closed residual identities
  across `4752/4752` derivative cells, without making the global dynamic
  symbolic oracle complete
- full independent formula-row oracle covers 132 runtime formula rows
- `KINEMATIC_ROW_DEFECT_CERTIFICATE.md/json` records a partial proof-scope
  certificate for the 96 non-dynamic rows on the smooth accepted FullVA lift
- `newton_euler_weak_balance` is covered by the runtime formula-row oracle
- `NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.md/json` records 36 row-level symbolic
  targets for the dynamic rows: 18 translational balance rows and 18 rotational
  balance rows, indexed by stage, body, component, and global runtime row
- the older `newton_euler_weak_balance` symbolic defect certificate remains a
  provenance record for the primitive/Taylor route, not the active PC2
  closure route
- `NEWTON_EULER_DEFECT_OBLIGATION_GATE.md/json` decomposes the 36 dynamic rows
  into the D5 Gauss-stage dynamic defect-rate target plus five
  sub-obligations: D1 translational balance identity, D2 rotational balance
  identity, D3 multiplier-wrench consistency, D4 smooth force-lift
  consistency, and D6 symbolic runtime-row equivalence
- `D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE.md/json` closes the accepted
  PC2 route by direct residual substitution: the 96 non-dynamic rows have the
  smooth-lift `O(h^7)` certificate and the 36 dynamic rows have zero residual
  on \(Z_G\), giving the required stage-residual `O(h^7)`
  implementation-defect certificate
- multi-probe formula-row AD Jacobian oracle matches `R_JAC` on three deterministic probes
- `IMPLEMENTATION_PATH_AUDIT.md/json` records
  `implementation_path_check_for_132_row_residual=true` for the accepted code
  path `residual_cylindrical_chain -> R_VALUE/R_JAC -> gauss_step ->
  integrate/run_case -> summary_v047.json`
- `PROOF_NUMERICAL_SCALE_AUDIT.md/json` records finite-run global h-sweep
  scale evidence: smooth error fits 7.160828/7.066183 and raw endpoint
  closure fits 5.985101/6.072291, consistent with a global order-six
  budget and a local `O(h^7)` endpoint budget
- `PROOF_SOLVER_SCALE_AUDIT.md/json` records summary-level solver residuals
  such as smooth reference `max_linear_residual_norm=2.800513564816292e-13`
  and single-pendulum stage residuals, but also records that no scaled
  tolerance sweep is present; the smooth reference residual divided by
  `0.005^7` is `3584.657362964853`, so the fixed-scale records are not an
  asymptotic `eta_h^tube <= c_eta h^7` proof
- `PROOF_SOLVER_SCALED_TOLERANCE_PROBE.md/json/csv` records a finite
  one-step smooth probe with `eta_h=c_eta h^7`, `c_eta=10000.0`, `4/4` ok
  rows, and maximum final residual divided by `h^7` equal to
  `127.58372278641149`; this is an executable solver-policy diagnostic, not a
  theorem-level scaled trajectory sweep
- `PROOF_SOLVER_SCALED_TOLERANCE_TRAJECTORY_PROBE.md/json/csv` records a
  finite short-trajectory smooth probe with `eta_h=c_eta h^7`,
  `c_eta=10000.0`, h values `[0.04, 0.02, 0.01, 0.005]`, `4/4` ok rows,
  `30` trajectory steps checked, and maximum final residual divided by `h^7`
  equal to `210.89078604575462`; this is a broader solver-policy diagnostic than
  the one-step probe, but it is still not a theorem-level scaled tolerance
  sweep over every reported trajectory and does not close the theorem-level
  nonlinear-solver policy
- `PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.md/json/csv` records a finite
  smooth short-trajectory comparison of fixed `1e-10`, `c h^7`, and
  `c h^8` residual targets over `h=[0.04,0.02,0.01,0.005]` and
  `T=0.08`: all `12` policy/step-size rows converge over `90` checked
  steps, with fixed-policy position/velocity orders
  `6.946347411176867/6.608089993735075`, `h^7` orders
  `6.946347411176867/6.608089993735075`, and `h^8` orders
  `6.946365976765468/6.608137477881583`; this answers the finite-window
  tolerance-comparison question but is still not a scaled-tolerance proof
  under a uniform all-transition policy over the reported trajectory
- `stage_residual_O_h7_implementation_defect_proved=true` by the
  direct-substitution route
- `eta_h_O_h7_solver_policy_evidence=false`
- `one_step_perturbation_shortcut_assumed=false`
- `fixed_tolerance_runs_are_asymptotic_proof=false`
- `full_tfe_stage_replacement=false`
- `accepted_residual_to_error_theorem=false`
- `accepted_dynamic_order_count=0` through the residual-to-error route

The recorded fixed-tolerance runs are finite-run evidence. They do not by
themselves prove the asymptotic solver-error condition
`eta_h^tube<=c_eta h^7` on the compact proof tube, nor that the reported
`eta_h^reported=max_n eta_{h,n}` specializes it on every accepted transition.
The solver-scale audit
makes this explicit by separating recorded residual magnitudes and the new
finite scaled-tolerance probe from the missing theorem-level scaled-tolerance
policy.

## Residual-To-Error Boundary

The v048 `closed_loop_residual_to_error_theorem_obligations` artifact records
seven blocking obligations before closed-loop reaction residuals can be used as
trajectory-error/order proof:

1. dynamic residual identity;
2. residual consistency rate `O(h^7)`;
3. closed-loop DAE stability or inf-sup bound;
4. calibrated non-floor-limited residual-to-error estimator;
5. reference-floor exclusion;
6. coarse-first accepted dynamic-order campaign;
7. manuscript theorem and proof.

Until those obligations close, `four_link` and `slider_crank` remain
mechanism-coverage rows, not accepted dynamic-order rows.

## Blocker Mapping

| Blocker | Gate status | Meaning |
| --- | --- | --- |
| `B1` | `closed` | Runtime row-layout and block-functional oracle exists, the full formula-row oracle covers 132 runtime formula rows, the multi-probe formula-row AD Jacobian oracle matches `R_JAC` on three deterministic probes, and `B1_AD_EXPANDED_SYMBOLIC_ORACLE_CLOSURE_CERTIFICATE.md/json` closes the B1 AD-expanded symbolic oracle; this does not promote the global dynamic symbolic oracle or symbolic-certificate `O(h^7)` route. |
| `B3` | `closed` | Closed by the direct residual-bridge/Kantorovich route; the theorem remains conditional on the smooth regularity and per-step branch-selected `eta_h` contracts. This B3 proof closure is independent of the separate narrowed-claim B4/B6/B7 closures and does not close the global/full-source-policy package boundaries. |

## Closure Rule

This gate remains not submission-ready until the package has:

- kept the B1 AD-expanded symbolic oracle and the B3 direct-substitution proof
  route synchronized with the manuscript and validators;
- a theorem-level scaled `eta_h^tube<=c_eta h^7` nonlinear-solver envelope
  on the accepted branch, or an
  explicitly retained theorem condition with no overclaim; and
- residual-to-error obligations closed before any four-link or slider-crank
  residual row is promoted to a dynamic-order theorem row.

Strict public-policy `1e-4` rows are not required to validate this proof
contract. They remain opt-in reproduction rows only.

## Validator

Run:

```bash
../.venv_sbel/bin/python validate_cmame_proof_contract_gate.py
../.venv_sbel/bin/python validate_kinematic_row_defect_certificate.py
../.venv_sbel/bin/python validate_newton_euler_defect_obligation_gate.py
../.venv_sbel/bin/python validate_implementation_path_audit.py
```

Expected markers:

- `cmame_proof_contract_gate=PASS`
- `proof_mode=conditional_consistency_transfer`
- `partial_kinematic_stage_defect_certificate_checked=True`
- `newton_euler_defect_obligation_gate_checked=True`
- `active_direct_newton_euler_open_obligation_count=0`
- `newton_euler_symbolic_primitive_open_obligation_count=1`
- `newton_euler_symbolic_primitive_open_obligation_scope=symbolic_primitive_certificate_route_not_active_direct_pc2`
- `newton_euler_defect_closed_obligation_count=5`
- `active direct D5 route closed; symbolic/primitive D5 route remains open`
- `implementation_path_check_for_132_row_residual=True`
- `dynamic_symbolic_oracle_complete=False`
- `stage_residual_O_h7_implementation_defect_proved=True`
- `fixed_tolerance_runs_are_asymptotic_proof=False`
- `accepted_residual_to_error_theorem=False`
- `submission_ready=False`
