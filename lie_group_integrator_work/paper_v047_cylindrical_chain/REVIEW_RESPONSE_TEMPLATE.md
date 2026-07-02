# Reviewer Response Template

This template is pre-scoped to the accepted v047 claim boundary. Use it to
answer likely reviewer questions without accidentally expanding the paper
claim beyond the current artifacts.

## Response: What Is The Main Claim?

The manuscript makes a conditional formal-order comparison and method-order
claim. The accepted production method is `Gauss6/FullVA`, with method-order
claim `6` and smooth cylindrical-chain observed position/velocity orders
`7.161/7.066`. The local paper-style `m=3` Gauss-Lobatto TFE formula target
has expected order `5`, so the comparison is a formal-order comparison inside
the current repository scope unless same-test implementation evidence is
provided.

The manuscript does not claim complete source-paper residual reproduction.
That boundary is machine-readable as `full_tfe_stage_replacement=false`.
`PROOF_EVIDENCE_MATRIX.md` maps the theorem interfaces and proof obligations
to concrete artifacts and read-only validators. `ORDER_ACCEPTANCE_GATE.md`
separates accepted dynamic order rows from four-example mechanism coverage.

## Response: How Should The Proof Route Be Read?

The theorem should be read as a direct residual-bridge/Kantorovich proof for
the implemented `Gauss6/FullVA` stage residual, not as a claim that the
optional primitive Newton--Euler Taylor ledger is complete. The active
stage-residual input is the 132-row implemented residual evaluated on the
lifted Gauss stage:

- the 96 non-dynamic FullVA rows supply the row-local `O(h^7)` residual
  certificate;
- the 36 Newton--Euler rows vanish by direct substitution on the same smooth
  branch;
- the resulting full residual bound is then consumed by the stage-root,
  endpoint-closure, inexact-Newton, and local-to-global lemmas.

The primitive/Taylor route is a stricter optional factorization of the 36
dynamic rows. It currently records `162/162` conditional reduction templates
but `0/162` actual primitive-route Taylor bounds, so it is not the PC2 route
used by the theorem. This does not weaken the accepted theorem because the
theorem consumes the already assembled 132-row direct residual bridge. It
also does not promote any primitive subterm claim.

The remaining proof boundaries should be stated explicitly: P6 is retained as
the theorem-level solver-scale condition, and P7 residual-to-error promotion
is open for residual-only mechanism rows and source-policy rows. Consequently,
small residual/reaction tables and fixed-tolerance logs are consistency
evidence, not replacements for the theorem interfaces.

## Response: Why Is Full-TFE Replacement Not Required For The Main Claim?

The four-example validation and the formal-order comparison are attached to
the accepted `Gauss6/FullVA` method path. Independent full-TFE stage
replacement is a stronger reproduction gate: it would require replacing all
132 Gauss/FullVA stage rows with paper-derived temporal finite-element weak
rows inside Newton, without endpoint source data, terminal-row replacement,
projection, or a target-direction oracle.

That stronger gate remains open, but it is not a prerequisite for the narrower
formal-order comparison.

## Response: What Are The Four Validated Examples?

The accepted ASME-style examples are:

- `single_pendulum`
- `double_pendulum`
- `four_link`
- `slider_crank`

The current quantitative markers are:

- `single_absolute_min_order=6.024`
- `double_method_min_order=6.089`
- `four_link_closed_loop_max_constraint_norm=1.052e-14`
- `four_link_reaction_max_dynamics_residual=1.338e-13`
- `slider_crank_closed_loop_max_constraint_norm=1.204e-15`
- `slider_crank_reaction_max_dynamics_residual=6.492e-15`

The current order boundary is that `single_pendulum` and `double_pendulum`
support accepted dynamic order rows. `four_link` and `slider_crank` are
accepted as mechanism coverage but remain `not_accepted_dynamic_order` for
external closed-loop dynamic order.

## Response: Why Is The Order Comparison Fair?

The accepted method and the comparator are intentionally separated. The method
being claimed is `Gauss6/FullVA`, which is sixth order by the conditional
Gauss/FullVA argument and records smooth observed orders `7.161/7.066`. The
comparator is the local paper-style `m=3` Gauss-Lobatto TFE formula target,
whose expected order is `5`. The paper therefore compares the conditionally
proved `Gauss6/FullVA` sixth-order method path, with smooth observed support,
against a local order-five formula target; it does not claim that the local
formula target is a completed source-paper residual implementation.

`SOURCE_PAPER_COMPARISON.md` is the short answer for original-paper comparison:
the local `m=3` target is treated as order `2m-1=5`, and the accepted v047
method-order claim is `6`.

The external same-test comparison is still open. Use
`CROSS_PAPER_BENCHMARK_SPEC.md` for the extracted benchmark policies and
`CROSS_PAPER_BENCHMARK_CASES.json` for the row-level run inventory. The
current v048 harness has one bounded 2021 single-pendulum public-code pilot,
one bounded `Gauss6/FullVA` same-mechanism pilot, one exact public-horizon
single-pendulum `Gauss6/FullVA` row at `T=3`, `h=1e-2`, and selected
four-link/slider-crank closed-loop residual rows plus 12/12 selected
same-window public-`rA` versus local-`Gauss6/FullVA` comparison rows and
derived paper-table summaries, but not the full external
dynamic order/work campaign. The Kissel/Bakke/Negrut velocity-partitioning
paper is tracked as an unresolved code-path gate, not as completed numerical
evidence.

## Response: What Remains Open?

The global submission blockers remain `OC4`, `OC6`, and `OC12`:

- source-policy reproduction rows are still `0/40`;
- the original TFE source-policy DAE runner is not closed;
- the runner-centered full source-policy package is not ready.

The proof route is not blocked by those items, but it remains conditional in
two theorem-boundary senses:

- P6 is retained as the compact-tube solver-scale condition
  `eta_h^tube <= c_eta h^7`; fixed-tolerance runs and finite solver probes do
  not discharge it as a theorem-level solver policy;
- P7 residual-to-error promotion remains open, so residual/reaction rows for
  four-link, slider-crank, and source-policy baselines are not promoted to
  trajectory-order evidence.

The remaining engineering and method caveats are:

- `sparse_speed_quantified`
- `full_tfe_stage_replacement_missing`
- `sharp_friction_coarse_order_reduction_ultra_recovered`

Sparse AD structure is quantified but dense `jacfwd` remains faster in the
recorded wall-clock evidence. The practical coarse sharp-friction regime is
order-reduced, although deeper fixed refinement recovers high order at
increased cost. Independent full-TFE replacement remains open.

## Response: What Is The Source-Policy Runner Archive Boundary?

The current package is not a full source-policy runner archive. The
machine-readable archive boundary records source-policy rows `0/40`,
safe actions without B4 opt-in `4`, opt-in-required actions `1`,
source-policy execution allowed now `False`, exact B4 opt-in required for
execution `True`, and opt-in commands/mapped external rows `13/20`.
Command-row traceability covers unique RA/HI rows `20/20`, row refs `32/32`,
and mismatch/terminal/closed/promotion-ready counts `0/0/0/0`.
Safe action ids are `rebuild_read_only_audit_chain,rerun_read_only_validators,keep_narrowed_archive_provenance_only,monitor_reopen_conditions`;
opt-in action ids are `authorized_b4_ra_hi_source_policy_execution`.
The narrowed archive boundary matches the reproducibility manifest: `True`.
Its status/source-policy/use/execution/exact tuple is
`narrowed_archive_ready_not_full_source_policy_runner_archive/0/40/False/False/True`,
with blocking ids/status `OC4,OC6,OC12` /
`OC4=open,OC6=partial,OC12=partial`. The current archive use is
`narrowed_claim_only`, not a full source-policy runner archive.
Objective blocker matrix:
`blocker_open_by_id=OC4:True,OC6:True,OC12:True`;
`blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready`;
`blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False`.

The guarded driver is `run_b4_source_policy_after_opt_in.sh`. It does not
authorize execution by itself; it requires the exact approval phrase
`I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json.`.
Until that authorization and post-execution promotion evidence exist, the
narrowed/replay package is provenance only and must not be presented as a full
source-policy reproduction package.

## Response: How Can The Claims Be Reproduced?

The submission checks read existing artifacts and do not invoke the full
`run_v047.py` generator:

```bash
../.venv_sbel/bin/python validate_cmame_submission.py
../.venv_sbel/bin/python validate_concise_paper.py
../.venv_sbel/bin/python validate_proof_evidence_matrix.py
../.venv_sbel/bin/python validate_order_acceptance_gate.py
../.venv_sbel/bin/python validate_source_paper_comparison.py
../.venv_sbel/bin/python validate_cross_paper_benchmark_spec.py
../.venv_sbel/bin/python validate_cross_paper_benchmark_cases.py
../.venv_sbel/bin/python validate_submission_bundle.py
../.venv_sbel/bin/python validate_paper_package.py
```

The broader repository check is:

```bash
.venv_sbel/bin/python validate_pipeline_outputs.py
```

The recommended CMAME/Elsevier manuscript is `main_cmame.pdf`, with
`main_cmame.tex`, `highlights_cmame.txt`, `declarations_cmame.md`, and
`CMAME_SUBMISSION_CHECKLIST.md` included in the submission package. The concise
supporting draft is `main_concise.pdf`; the full audit/status paper is
`main.pdf`.

## Response: What Should Not Be Claimed?

Do not claim:

- complete source-paper residual reproduction;
- accepted independent full-TFE stage replacement;
- sparse AD is already faster than dense `jacfwd`;
- the practical coarse sharp-friction regime is solved.

The current accepted statement is narrower and explicit: `Gauss6/FullVA`
carries a conditional sixth-order method claim against the local order-five
paper-style TFE target. The four ASME-style examples are accepted as local
method examples; only the single- and double-pendulum rows are accepted
dynamic-order rows, while four-link and slider-crank remain mechanism-coverage
rows.
