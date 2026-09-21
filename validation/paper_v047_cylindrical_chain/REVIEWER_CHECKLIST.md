# v047 Reviewer Checklist

This checklist is the shortest artifact-backed path for reviewing the current
paper claims. It is read-only: none of the commands below regenerate numerical
CSV, JSON, or PNG artifacts.

## Accepted Claims

- Primary claim: the paper states a conditional formal-order comparison.
  The accepted `Gauss6/FullVA` path is sixth order and validates four ASME
  examples as mechanism coverage; the full-TFE replacement is a stronger
  reproduction gate, not a prerequisite for this bounded conditional
  order-comparison.
- Boundary statement: the original Chaturvedi--Sandu--Sandu paper has a full
  TFE formulation; `full TFE replacement` is the local v047 task of replacing
  the accepted `Gauss6/FullVA` stage residual with paper-derived TFE weak rows.
- Four ASME method rows are accepted under
  `four_asme_method_rows_accepted_projection_sharp_sparse_caveats`.
- The accepted ASME examples are `single_pendulum`, `double_pendulum`,
  `four_link`, and `slider_crank`.
- The accepted production path is `Gauss6/FullVA`, not the independent
  paper-TFE replacement.
- Smooth cylindrical-chain observed position/velocity orders are
  `7.161/7.066`.
- The minimal four-example validator records `single_absolute_min_order=6.024`,
  `double_method_min_order=6.089`,
  `closed_loop_max_constraint_norm=1.052e-14`, and
  `closed_loop_reaction_max_dynamics_residual=1.338e-13`.

## Original Paper Versus Accepted v047 Claim

- Source-paper/local target: the local paper-style `m=3` Gauss-Lobatto TFE
  formula target has expected order five and is the comparator for the current
  paper-facing claim.
- Accepted v047 claim: the accepted `Gauss6/FullVA` path is a conditional
  sixth-order one-step map with smooth observed orders `7.161/7.066`; the four
  ASME-style examples are accepted as local method examples, with
  `single_pendulum`/`double_pendulum` carrying the dynamic-order rows and
  `four_link`/`slider_crank` carrying mechanism-coverage rows.
- Not claimed: complete source-paper residual reproduction, because
  `full_tfe_stage_replacement=false` remains open.
- Practical reading: this is a formal-order comparison and diagnostic
  same-problem comparison, not a statement that every source-paper TFE residual row
  has replaced the accepted `Gauss6/FullVA` stage residual inside Newton.

## Order-Comparison Acceptance Criteria

The paper-facing order-comparison statement is accepted only under these
read-only criteria:

- Accepted method path: the claimed method is `Gauss6/FullVA`, not a
  diagnostic paper-TFE substitution.
- Order exceedance: smooth position/velocity orders `7.161/7.066` exceed the
  encoded local `m=3` Gauss-Lobatto TFE expected order five target.
- Four-example gate: `single_pendulum`, `double_pendulum`, `four_link`, and
  `slider_crank` are accepted under the same ASME method gate.
- Comparator boundary: the comparator is the local paper-style formula target;
  complete source-paper residual reproduction remains separate.
- Caveat separation: sparse speed, sharp-friction coarse-regime behavior,
  source-policy reproduction, and `full_tfe_stage_replacement=false` are
  explicit caveats that do not contradict the narrower formal-order statement.
- Read-only reproducibility: `validate_paper_claims.py`,
  `validate_paper_package.py`, `validate_four_asme_minimal.py`,
  `validate_full_tfe_gap.py`, `validate_full_tfe_repair_spec.py`, and
  `validate_pipeline_outputs.py` check the claim without invoking the full
  v047 generator.

## Review Agent Gate

Before treating the CMAME package as submission ready, run the deterministic
read-only review agent and its validators. The review step must check both the
numerical matrix and the proof traceability boundary, not just the manuscript
format.

## Proof Route Gate

The proof review should read the theorem as a direct
residual-bridge/Kantorovich proof, not as a primitive 162-subterm Taylor
proof. The current proof-side validator boundary is:

- Active PC2 route: direct 132-row residual bridge is closed from the 96-row
  non-dynamic certificate plus 36 Newton--Euler direct-substitution zero rows.
- Theorem route: `validate_cmame_strict_proof_audit.py` and
  `validate_proof_claim_traceability_audit.py` keep the conditional theorem
  traceable under retained P1/P2/P3/P4/P6 interfaces.
- Dynamic-row certificate: `validate_d5_dynamic_direct_substitution_certificate.py`
  records `dynamic_zero_residual_rows=36` and
  `direct_route_certificate_closed=True`.
- Primitive/Taylor lane: `validate_d5_conditional_taylor_certificate.py`
  records `conditional_terms=162/162` but `actual_taylor_bounds_proved=0`
  and `pc2_closed=False`; this lane is a conditional certificate schema,
  currently uninstantiated as theorem evidence, and not a theorem premise.
- Solver and residual promotion boundaries: P6 remains the retained
  theorem-level condition `eta_h^tube <= c_eta h^7`, while P7 residual-to-error
  promotion remains open and mechanism-coverage residual rows are not promoted
  to trajectory-order evidence.

Required review evidence:

- `PAPER_NUMERICAL_RESULT_MATRIX.md/json/csv` covers `44/44` method/example
  cells from `132` raw rows across all four examples and all `11` methods.
- `RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.md/json` covers `44/44`
  manuscript/PDF velocity cells, specifically the velocity order/error entries
  in the main and flat CMAME files,
  while keeping source-policy reproduction and external-superiority claims
  false.
- `ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.md/json` checks `40/40`
  nonlocal method/example rows: local wins `40/40` velocity-order comparisons
  and `40/40` finest-velocity-error comparisons, while `0/40` nonlocal rows
  are source-policy closed.
- `ALL_EXAMPLES_RESULT_SANITY_AUDIT.md/json` locks the exact `15` flagged
  nonlocal rows across `single_pendulum`, `double_pendulum`, `four_link`, and
  `slider_crank`; all flagged rows are quarantined from external-superiority
  claims.
- `SOURCE_POLICY_ROW_CLOSURE_LEDGER.md/json` checks each flagged row's missing
  source-policy evidence; it records `0/15` source-policy-closed rows and
  `0/15` external-superiority-ready rows.
- `EXTERNAL_CASE_EVIDENCE_RECONCILIATION.md/json` separates full-campaign
  `not_run` markers from bounded/coarse evidence already present for RA2021
  and HI2022; TFE2026 and VP2024 remain not-ready or demote suites.
- `VP2024_CODE_PATH_DISPOSITION_AUDIT.md/json` checks all four VP examples:
  `4/4` VP2024 source-policy rows unresolved, `4/4` VP2024 common-reference
  proxy order/error wins, and the larger-step error diagnostic held
  noncontrolling.
- `PROOF_CLAIM_TRACEABILITY_AUDIT.md/json` confirms proof labels and boundary
  tokens in both CMAME TeX sources, records `1/7` theorem interfaces
  submission-satisfied, `5/7` retained theorem interfaces, `1/7` open P7
  nonpromotion boundary, `4/0` close requirements/unsatisfied close
  requirements, `96` certified non-dynamic rows, `36/0` active direct
  Newton--Euler closed/open rows, `36` symbolic/primitive-route Newton--Euler
  rows not certified by that route, six Newton--Euler obligations, and seven
  residual-to-error blockers.
- `CMAME_SUBMISSION_INTEGRITY_AUDIT.md/json` confirms local citation
  integrity, sidecar completeness, and
  `external_reference_web_verification_complete=True`.
- `CMAME_REVIEW_AGENT_REPORT.md/json` must keep the top-level review global:
  `submission_standard_scope=global_submission_standard`,
  `decision=do_not_submit_global`, and `open_blockers=OC4,OC6,OC12`. The
  bounded narrowed subcheck must separately keep
  `bounded_subcheck_satisfied_not_global_submit`; legacy compatibility aliases
  `narrowed_claim_decision=submit_under_narrowed_claim` and
  `narrowed_claim_submission_standard_met=True` must not be read as the global
  decision. The full source-policy package readiness false marker remains in
  force until every
  external source-policy baseline, prose, and figure reintroduction gate is
  closed.

Command:

```bash
../../.venv_sbel/bin/python cmame_submission_review_agent.py
../../.venv_sbel/bin/python validate_cmame_review_agent.py
../../.venv_sbel/bin/python validate_paper_numerical_result_matrix.py
../../.venv_sbel/bin/python validate_result_to_manuscript_traceability_audit.py
../../.venv_sbel/bin/python validate_all_method_example_claim_disposition_audit.py
../../.venv_sbel/bin/python validate_all_examples_result_sanity_audit.py
../../.venv_sbel/bin/python validate_source_policy_row_closure_ledger.py
../../.venv_sbel/bin/python validate_external_case_evidence_reconciliation.py
../../.venv_sbel/bin/python validate_vp2024_code_path_disposition_audit.py
../../.venv_sbel/bin/python validate_proof_claim_traceability_audit.py
../../.venv_sbel/bin/python validate_cmame_submission_integrity_audit.py
```

Expected current markers:

```text
submission_standard_met=False
submission_standard_scope=global_submission_standard
decision=do_not_submit_global
open_blockers=OC4,OC6,OC12
bounded_subcheck_satisfied_not_global_submit=True
legacy_narrowed_claim_submission_standard_met=True
legacy_narrowed_claim_decision=submit_under_narrowed_claim
full_source_policy_package_ready=False
rows=44/44
flagged_nonlocal_rows=15
direct_pc2_proof_gap_closed=True
full_source_policy_submission_ready=False
```

The narrowed archive boundary matches the reproducibility manifest: `True`.
Narrowed archive boundary tuple:
`narrowed_archive_ready_not_full_source_policy_runner_archive/0/40/False/False/True`.
Blocking ids/status: `OC4,OC6,OC12` /
`OC4=open,OC6=partial,OC12=partial`. Current archive use is
`narrowed_claim_only`, not a full source-policy runner archive.
Objective blocker matrix:
`blocker_open_by_id=OC4:True,OC6:True,OC12:True`;
`blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready`;
`blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False`.

Command:

```bash
cd ../numerics/v047_cylindrical_chain_pipeline
../../.venv_sbel/bin/python validate_four_asme_minimal.py
```

Expected markers:

```text
v047 minimal four-ASME validation: PASS
full_tfe_stage_replacement=False
remaining_caveat=full_tfe_stage_replacement_missing_outside_four_example_gate
```

## Diagnostic But Not Accepted

- The paper `m=3` Gauss-Lobatto TFE formula mapping has expected order five,
  but formula mapping is not a solved replacement residual.
- The source-free final-stage velocity closure closes raw terminal endpoint
  velocity to `4.011e-16`, but the smooth position order is only `3.523`.
- An earlier pose+velocity acceleration Taylor local probe tests
  `stage02_convex_pose_velocity_extrapolate_0p01_0p02_posevelaccel_p0p0005_m0p0001_z`
  as its best nonterminal row, reaches residual `1.0173e-05`, and still has no
  terminal-bridge span.
- The component-split pose-acceleration local probe tests translation-only and
  angular/Lie-only pose shifts. Its best split law
  `stage02_convex_pose_velocity_extrapolate_0p01_0p02_transposeaccel_m0p01_z`
  remains at residual `5.298e-06`, while angular-only
  `angposeaccel_p0p002` reaches `9.6511e-06`; neither branch spans the
  terminal bridge.
- The component-split velocity-acceleration local probe tests translational
  and angular velocity shifts. Its best ordinary-scale law
  `stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelaccel_m0p01_z`
  reaches residual `2.138e-04`; the tiny-scale
  `transvelaccel_m0p0005` follow-up reaches `9.8175e-06`, and no branch spans
  the terminal bridge.
- The component-mixed pose/velocity Taylor local probe combines angular/Lie
  pose shift with translational velocity shift. Its best law
  `stage02_convex_pose_velocity_extrapolate_0p01_0p02_angpose_transvelaccel_p0p0005_m0p0005_z`
  reaches residual `9.987e-06`, still with no terminal-bridge span.
- The stage-2-fixed/delta acceleration velocity-shift local probe tests final
  active-stage and stage-2-minus-stage-0 acceleration sources. Its best law
  `stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelaccelstage2_m0p0005_z`
  reaches residual `9.8175e-06`; the best delta20 branch reaches
  `1.0119e-05`, still with no terminal-bridge span.
- The nonfinal terminal velocity/source predictor local probe uses only
  stage-0/stage-1 velocity rows plus source estimates. Its best law
  `nonfinal_velocity_terminal_euler1_z` reaches residual `0.923466`, with
  stage-2 `translation_velocity_v` still dominant, and no branch spans the
  terminal bridge.
- The stage-2 source-to-velocity transport local probe applies source/history
  projection at the stage-2 pose/velocity closure. The earlier scaled
  `stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p01_z`
  law reaches `0.0001251`; the ultra-fine scaled
  `stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p0001_z`
  law reaches `1.251e-06`, but independent target rank remains `6` and no
  branch spans the terminal bridge.
- The combined source-transport/angular-pose local probe tests a small
  angular/Lie pose acceleration component on top of the ultra-fine transport.
  Its best combined law
  `stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p0001_angposeaccel_p0p0001_z`
  reaches only `1.296e-06`, independent target rank returns to `8`, and no
  branch spans the terminal bridge.
- The bare endpoint-pose velocity local probe tests
  `stage02_convex_pose_velocity_0p00_z` directly. It spans the local terminal
  bridge at residual `1.327e-15` in `31.7` seconds with `span_row_count=1`, but
  this is local-span-not-full-TFE evidence because no trajectory h-sweep or
  order proof has accepted it.
- The endpoint-pose velocity predictor h-sweep smoke
  `lower_pair_endpoint_pose_velocity_predictor_h_sweep_smoke` then inserts
  that family into the nonlinear `132`-row residual. The smooth three-h `0p00`
  refinement closes terminal velocity to `8.124e-17`, but orders are only
  `4.142/2.305`. The `0p01` default smoke leaves terminal velocity at
  `6.255e-06`, with orders `2.345/1.878`, so this is still diagnostic.
- Source-transport coefficient shrinking closes terminal velocity but not
  order. The
  `stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p00001_z`
  row has `terminal_velocity_closed=true`, max terminal velocity `8.021e-13`,
  and finest-h terminal velocity `5.910e-14`, but three-h orders remain
  `4.142/2.305`, so it is still not an accepted full-TFE replacement.
- The non-projection extrapolated `0p01/0p02` trajectory smoke is a useful
  nonterminal clue: `stage02_convex_pose_velocity_extrapolate_0p01_0p02_z`
  has `projection_used=false`, terminal velocity `1.254e-07`, and default
  two-point orders `6.412/3.775`, but the three-h smooth refinement drops to
  `4.054/2.364`; its finest-h terminal velocity is `1.244e-08`, so it still
  does not close terminal velocity.
- Closer non-projection extrapolation closes terminal velocity only in the
  endpoint limit. The ultra-near
  `stage02_convex_pose_velocity_extrapolate_0p00001_0p00002_z` row has
  `projection_used=false`, terminal velocity `1.254e-13`, and finest-h
  terminal velocity `1.254e-14`, but three-h orders remain `4.142/2.305` with
  `smooth_order_ok=false`.
- Quadratic nonterminal extrapolation gives the same result. The best
  `stage02_convex_pose_velocity_quadextrapolate_0p002_0p005_0p01_z` row has
  `projection_used=false`, terminal velocity `2.029e-13`, and finest-h
  terminal velocity `8.254e-15`, but three-h orders remain `4.142/2.305`.
- Nonfinal velocity/source trajectory predictors are negative. The stage0/1
  set converges all `24` rows but only reaches terminal velocity `1.770e-07`;
  its order-friendlier rows still have terminal velocity `3.584e-07`;
  adding stage2 with `nonfinal_velocity_terminal_linear012_z` and
  `nonfinal_velocity_terminal_euler2_z` converges all `18` rows, but the
  apparent `2.559e-11` coarse value jumps to `1.328e-07` at `h=0.02`, so
  terminal closure is not convergent; the stable value is only `1.134e-07`.
- A projection-like terminal-tangent endpoint-pose diagnostic is also negative:
  full `stage02_convex_pose_velocity_0p01_terminalproj_z` fails with residual
  divergence `6.739e+08`; damped `terminalproj_p0p1` and `terminalproj_p0p5`
  converge but give terminal velocities `7.028e-06` and `1.321e-05`, with
  orders `2.301/1.788` and `2.158/1.433`. These rows set
  `projection_used=true`, so they are diagnostic only.
- A nonterminal Hermite endpoint pose/velocity predictor is also negative. The
  best local row, `nonfinal_hermite_endpoint_pose_velocity_02_z`, reaches only
  projection residual `0.072816` with independent target rank `8`; its bounded
  smooth h-sweep converges with rank `132` but leaves terminal velocity at
  `5.827e-06` and only gives two-point orders `2.693/2.004`.
- The one-step recurrent-history source predictor family is also negative. The
  best local row, `recurrent_history_velocity_terminal_source1linear_z`,
  reaches only projection residual `0.923100` with independent target rank `8`.
  The full five-law bounded smooth h-sweep converges all `15` source-free steps
  at rank `132`, but writes no accepted artifact or summary; the best terminal
  law, `recurrent_history_velocity_terminal_source01historyblend_z`, reaches
  only terminal velocity `1.010e-07` with orders `6.596/4.805`, while
  `source1linear` keeps orders `6.505/5.042` but remains at `4.418e-07`. No
  tested law reaches the `1e-12` Full-TFE terminal-closure gate.
- The recurrent-history AB/source-slope extension is also negative. Its five
  new laws converge all `15` source-free smooth steps at rank `132`, but the
  best terminal law, `recurrent_history_velocity_terminal_source01historyslope_z`,
  still leaves terminal velocity at `2.016e-07` with orders `6.566/5.264`; the
  `source0ab2*` laws stay near `2.354e-07`, and `source1ab2` worsens to
  `5.104e-07`. No accepted artifact or summary is written.
- The two-history recurrent source-state extension is also negative. Its five
  AB3/curvature shift-register laws converge all `30` source-free smooth smoke
  steps at rank `132`, with max residual `4.213e-12`, but the best terminal
  laws,
  `recurrent_twohistory_velocity_terminal_source0historycurvature_z` and
  `recurrent_twohistory_velocity_terminal_source01historyslopecurvature_z`,
  still leave terminal velocity at `9.319e-07`; this is worse than the
  one-step AB/source-slope best and far above `1e-12`.
- The nonlinear recurrent feedback extension closes terminal velocity but still
  fails the order gate. Its strongest tested law,
  `recurrent_history_velocity_terminal_feedbacknorm_source01historyslope_rel_p20_z`,
  uses only current candidate/final-row magnitude ratios as differentiated
  coefficients and no projection or endpoint source. A smooth three-h
  refinement closes terminal velocity to `3.287e-16` at rank `132`, but gives
  only `3.523/4.828` position/velocity orders, so
  `smooth_order_ok=false`.
- A stage0 endpoint-pose velocity predictor follow-up writes local-span and
  trajectory-smoke artifacts. The best nonterminal local law
  `stage02_convex_pose_velocity_0p00_z` spans the terminal bridge locally
  (`1.327e-15` residual), and the smooth three-h trajectory smoke closes
  terminal velocity to `3.455e-16` at rank `132`, but position/velocity orders
  remain `3.523/4.828`. This is useful diagnostic evidence only:
  `accepted_h_sweep_present=false` and `full_tfe_stage_replacement=false`.

Command:

```bash
cd ../numerics/v047_cylindrical_chain_pipeline
../../.venv_sbel/bin/python validate_full_tfe_gap.py
../../.venv_sbel/bin/python validate_full_tfe_repair_spec.py
```

Expected markers:

```text
full_tfe_stage_replacement=False
accepted_candidate_count=0
next_repair_target=derive a nonterminal endpoint-pose predictor that closes terminal velocity on trajectory
```

## Open Claims

- `full_tfe_stage_replacement=false`.
- Sparse row-VJP is quantified but is not yet a stable runtime win.
- The sharp Brown-McPhee coarse regime remains a practical caveat; ultra fixed
  refinement recovers high order at higher cost.

## Paper Package Check

Run this from the paper directory:

```bash
../../.venv_sbel/bin/python validate_paper_package.py
```

Expected markers:

```text
v047 paper package validation: PASS
note=run_v047.py was not invoked
```

## Full Regeneration Boundary

Do not run the full generator for paper edits, claim checks, or the accepted
four-example method gate. The full command

```bash
cd ../numerics/v047_cylindrical_chain_pipeline
../../.venv_sbel/bin/python run_v047.py
```

is an artifact-producing historical audit harness. The latest recorded full
regeneration time is `2386.76` seconds. Use it only after changing numerical
method code or artifact-producing audit code.
