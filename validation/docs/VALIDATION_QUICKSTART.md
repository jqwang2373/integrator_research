# Validation Quickstart

This file is the short entry point for v047 validation and paper checks. It is
intentionally separate from the full research ledger so that routine evidence
checks do not accidentally trigger the full numerical regeneration.

## What Is Already Accepted

- Primary paper claim: v047 is a conditional formal-order comparison and
  sixth-order FullVA method claim, not a full source-paper residual
  reproduction claim.
- The accepted production path is `Gauss6/FullVA`. It is the sixth-order path
  used for the current method claim and records smooth position/velocity orders
  `7.161/7.066`.
- The local paper-style `m=3` Gauss-Lobatto TFE formula target has expected
  order `5`; the accepted evidence supports only a formal-order comparison
  within this artifact scope unless same-test implementation evidence is
  provided.
- Four ASME method rows are accepted under status
  `four_asme_method_rows_accepted_projection_sharp_sparse_caveats`.
- The accepted four-example set is `single_pendulum`, `double_pendulum`,
  `four_link`, and `slider_crank`.
- The paper package exists under `paper_v047_cylindrical_chain/` and keeps the
  claim boundary in `PAPER_CLAIM_LEDGER.md`.
- The manuscript is `../paper/main_cmame.tex` (CMAME/Elsevier `elsarticle`); it is
  the only hand-edited LaTeX source. The two superseded internal drafts,
  `main.tex` (full artifact-backed status/audit paper) and `main_concise.tex`
  (shorter supporting order-comparison draft that builds `main_concise.pdf`),
  live in `legacy_drafts/` and stay only because the ledger validates them. All
  stay inside the same claim boundary.
- The submission-facing index is
  `paper_v047_cylindrical_chain/SUBMISSION_PACKET.md`; it names
  `main_cmame.pdf` as the mechanically complete CMAME draft PDF and keeps the
  non-claims explicit. The current quality gate is not submission ready:
  `submission_ready=false`, `mechanical_preflight_passed=true`, and
  `quality_review_passed=false`. The blocking review is
  `CMAME_SUBMISSION_READINESS_REVIEW.md`. The machine-checkable blocker ledger
  is `CMAME_BLOCKER_CLOSURE_GATE.md` / `CMAME_BLOCKER_CLOSURE_GATE.json`; it
  records B5 as closed by `CMAME_VISUAL_LEGIBILITY_AUDIT.md` /
  `CMAME_VISUAL_LEGIBILITY_AUDIT.json`, records B8 as closed by
  `CMAME_RELATED_WORK_AUDIT.md` / `CMAME_RELATED_WORK_AUDIT.json`, keeps
  B1-B4 and B6-B7 open, and keeps `default_1e-4_required=false`. The runtime
  external-baseline gate is `CMAME_EXTERNAL_BASELINE_GATE.md` /
  `CMAME_EXTERNAL_BASELINE_GATE.json`; it records
  `same_test_campaign_status=not_run`, `external_superiority_claim=false`,
  `default_1e-4_required=false`. `four_link`/`slider_crank` now have local
  non-oracle true-dynamic Newton coarse order rows and same-window public
  work/precision rows. They also have strict common-reference error columns and
  an integrated Figure 7 at the coarse window; there is still no external
  superiority claim until broader external-suite closure/demotion and review
  close. The runtime
  implementation-fidelity oracle is `DYNAMIC_ROW_ORACLE_GATE.md` /
  `DYNAMIC_ROW_ORACLE_GATE.json`; it checks the accepted residual/Jacobian
  row partition while keeping the independent symbolic oracle open. The CMAME
  proof-contract gate is `CMAME_PROOF_CONTRACT_GATE.md` /
  `CMAME_PROOF_CONTRACT_GATE.json`; it records the conditional theorem
  boundary: `eta_h^tube <= c_eta h^7` is a theorem condition, fixed-tolerance runs
  are finite-run evidence, `dynamic_symbolic_oracle_complete=false`, and
  `accepted_residual_to_error_theorem=false`. The CMAME
  package also includes
  `highlights_cmame.txt`,
  `declarations_cmame.md`, `CMAME_SUBMISSION_CHECKLIST.md`, and
  `CMAME_SUBMISSION_READINESS_AUDIT.md`.
- The flat source package is
  `paper/cmame_submission_flat/`; its master file is
  `cmame_submission_flat/main_cmame_submission.tex` and its compiled check PDF
  is `cmame_submission_flat/main_cmame_submission.pdf`. The upload-shaped flat
  archive is `cmame_submission_flat.zip`.
- The submission package also includes
  `paper/COVER_LETTER.md` and
  `paper_v047_cylindrical_chain/SUBMISSION_ARTIFACT_MANIFEST.json`; the package
  validator checks both files against the same claim boundary.
- The submission artifact manifest boundary is synchronized by
  `paper_v047_cylindrical_chain/sync_submission_artifact_manifest_boundary.py`
  from `CMAME_REPRODUCIBILITY_PACKAGE_MANIFEST.json` and
  `OBJECTIVE_COMPLETION_AUDIT.json`. The validator
  `validate_submission_artifact_manifest_boundary_sync.py` is part of the
  paper package and top-level pipeline checks; it keeps OC4 traceability at
  `13/13/8/5/13/8/False/False`, records
  `source_policy_execution_invoked=False`, and keeps blockers
  `OC4,OC6,OC12`.
- The objective completion audit is the central blocker matrix for those same
  blockers. `validate_objective_completion_audit.py` checks
  `blocker_open_by_id=OC4:True,OC6:True,OC12:True`,
  `blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready`,
  and `blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False`; a PASS
  therefore confirms the recorded open-boundary state, not submission
  readiness.
- `paper_v047_cylindrical_chain/SUBMISSION_FILE_INVENTORY.md` lists the primary
  submission files, supporting evidence files, and validators.
- `paper_v047_cylindrical_chain/FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.md`
  is the OC12 package/archive gate. Its validator
  `validate_full_source_policy_runner_archive_gap_audit.py` is now part of the
  paper package and top-level pipeline checks; it keeps the full source-policy
  runner archive explicitly not ready while source-policy rows remain `0/40`,
  with direct top-level `full_archive_ready_now=False`,
  `source_policy_closed=False`, `source_policy_closed_ratio=0/40`,
  `opt_in_required_command_count=13`, `opt_in_required_mapped_external_rows=20`,
  `driver_does_not_authorize_execution=True`, and
  `submission_ready=False` markers. OC12 remains at
  `closure_decision=remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready`;
  `current_archive_usable_as_full_source_policy_runner_archive=False`,
  `safe_current_use=narrowed_claim_replay_and_audit_provenance_only`,
  `primary_submission_package_allowed=False`, and dependency blockers `OC4,OC6`
  are direct checked aliases.
- `paper_v047_cylindrical_chain/TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.md`
  is the OC6 TFE source-policy attempt gate. Its validator
  `validate_tfe_source_policy_self_reproduction_attempt_certificate.py` is part
  of the paper package and top-level pipeline checks; it keeps TFE
  attempted-not-reproducible rows at `16/16` and source-policy closed rows at
  `0`, with direct top-level `source_policy_closed=False`,
  `source_policy_closed_ratio=0/16`, and `submission_ready=False` markers.
- `paper_v047_cylindrical_chain/OC6_SOURCE_EQUIVALENT_REOPEN_READINESS_AUDIT_20260620.md`
  is the OC6 source-equivalent reopen-readiness gate. Its validator
  `validate_oc6_source_equivalent_reopen_readiness_audit_20260620.py` is part
  of the paper package and top-level pipeline checks; it keeps the OC6 closure
  decision explicit as
  `remain_open_no_positive_source_equivalent_artifact`, records
  `source_equivalent_artifact_found=False`, and preserves
  `source_policy_closed_ratio=0/20` without performing a new public-code search
  or source-policy execution. Direct aliases now include `oc6_blocker_id=OC6`,
  `oc6_blocker_status=partial`,
  `oc6_closure_decision=remain_open_no_positive_source_equivalent_artifact`,
  `oc6_closure_allowed_now=False`,
  `reopen_condition=suite_specific_source_equivalent_reopen_conditions`, and
  `latest_external_probe_boundary=0/0/4/False/False`.
- `paper_v047_cylindrical_chain/RA_HI_SOURCE_POLICY_OUTPUT_INVENTORY.md`,
  `paper_v047_cylindrical_chain/RA_HI_SOURCE_POLICY_CLOSEOUT_CHECKLIST.md`,
  `paper_v047_cylindrical_chain/RA_HI_SOURCE_POLICY_PROMOTION_BLOCKER_MATRIX.md`,
  `paper_v047_cylindrical_chain/RA_HI_SOURCE_POLICY_POST_EXECUTION_ATTEMPT_CERTIFICATE.md`,
  `paper_v047_cylindrical_chain/B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.md`,
  `paper_v047_cylindrical_chain/B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.md`,
  `paper_v047_cylindrical_chain/run_b4_source_policy_after_opt_in.sh`,
  and `paper_v047_cylindrical_chain/FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.md`
  are the OC4 RA/HI closeout and guarded-execution boundary gates. Their
  validators are part of the paper package and top-level pipeline checks; they
  keep RA/HI source-policy rows at `0/20`, not-promoted rows at `20/20`, B4
  ready-command coverage at `20/40`, full source-policy provenance preflight at
  `40/40`, source-policy closure at `0/40`, promotion-ready rows at `0`,
  external-superiority ready rows at `0`, `run_v047_invoked=False`, and guarded
  execution uninvoked unless the exact opt-in packet is authorized. The B4
  handoff exposes direct top-level `guarded_execution_driver=run_b4_source_policy_after_opt_in.sh`,
  `driver_requires_exact_approval=True`, `opt_in_required_command_count=13`,
  `opt_in_required_mapped_external_rows=20`, and `submission_ready=False` markers.
  The row-provenance audit also records the OC4 closure decision
  `remain_open_ready_for_authorized_execution_not_executed_not_promoted`,
  direct aliases `oc4_blocker_id=OC4`, `oc4_blocker_status=open`,
  `oc4_closure_decision=remain_open_ready_for_authorized_execution_not_executed_not_promoted`,
  `oc4_closure_allowed_now=False`, `oc4_blocker_open=True`,
  ready-command/mapped-row coverage `13/20`, and command traceability
  `20/32/32/0`.
  The guarded driver validator checks the exact approval guard, 13-command
  command list, opt-in packet match, and non-execution markers without running
  B4 commands.
- Likely reviewer responses are pre-scoped in
  `paper_v047_cylindrical_chain/REVIEW_RESPONSE_TEMPLATE.md`; it keeps the
  answers aligned with the accepted claim and non-claims.
- `paper_v047_cylindrical_chain/SOURCE_PAPER_COMPARISON.md` records the
  original-paper comparison boundary: local `m=3` Gauss-Lobatto TFE expected
  order `2m-1=5` versus accepted `Gauss6/FullVA` method-order claim `6`.
- `paper_v047_cylindrical_chain/PROOF_EVIDENCE_MATRIX.md` maps each concise
  theorem obligation to artifact and validator evidence.
- `paper_v047_cylindrical_chain/ORDER_ACCEPTANCE_GATE.md` is the example-level
  order boundary: `single_pendulum` and `double_pendulum` have accepted dynamic
  order rows; `four_link` and `slider_crank` are accepted mechanism coverage
  but not accepted external dynamic order. The paired
  `ORDER_ACCEPTANCE_GATE.json` is checked by `validate_order_acceptance_gate.py`
  and records the `coarse_first_no_default_1e-4` policy.
- `paper_v047_cylindrical_chain/IMPLEMENTATION_FIDELITY_CERTIFICATE.md` is a
  static source-identity certificate tying the accepted 132-row residual to
  `residual_cylindrical_chain` and `R_JAC`; its validator keeps the dynamic
  symbolic row oracle marked open.
- `v048_cross_paper_same_test_benchmarks/` is the executable scaffold for the
  cross-paper same-test campaign. Its full 2021 `rA/rp/reps` run now completes
  all 9/9 public step-size trios for `single_pendulum`, `four_link`, and
  `slider_crank` as 27/27 ok rows.
  It also has a bounded
  same-mechanism `Gauss6/FullVA` single-pendulum pilot with 3/3 rows and
  observed orders `6.073/6.033/6.055/6.024`, plus a 3/3 exact public-horizon
  single-pendulum `Gauss6/FullVA` step-size trio at `T=3`,
  `h=[1e-2,1e-3,1e-4]` with roundoff-limited final-error orders, plus 6/6
  selected closed-loop `Gauss6/FullVA` rows on the 2021 `four_link` and
  `slider_crank` mechanisms. It also completes the public-horizon closed-loop
  residual tranche for those two mechanisms at `T=3`,
  `h=[1e-2,1e-3,1e-4]` (`6/6` public h rows). Those closed-loop rows verify
  constraint/reaction residuals on public mechanisms but are not dynamic
  order/work rows. v048 also writes a 12/12
  selected same-window closed-loop comparison table for public `rA` dynamics
  versus local `Gauss6/FullVA` residual rows under the same `T=0.2`,
  `h=[0.02,0.01,0.005]` public-reference columns; it is still selected-window
  table-shape evidence, not full public dynamic superiority. It also writes
  9-row public order/work and 4-row same-window work/precision summary CSVs for
  manuscript tables. v048 also has a bounded 2022 half-implicit
  four-example pilot with 24/24 ok rows and 8/8 `rA/rA_half` model-form
  trios, plus a 5-row
  velocity-partitioning code-path audit showing 0 exact VP path hits in both
  local SBEL tree mirrors. It also completes 9/9 public `double_pendulum`
  dynamic self-reference order rows for `rA/rp/reps` at `T=3`,
  `h=[1e-2,2e-3,1e-3]`, reference `h=1e-4`. The four-example performance
  matrix also includes the coarse-first public-horizon `double_pendulum`
  `Gauss6/FullVA` tranche at `T=3`, `h=[0.1,0.05,0.025]`, with
  position/velocity orders `7.951/7.042`. v048 also adds the matching coarse
  same-window public double-pendulum baselines: `rA/reps` complete 6/6 rows
  with position/velocity orders `0.703/0.754`, while `rp` records three Newton
  nonconvergence rows. It also adds a single-pendulum coarse same-window
  tranche with `ra2021_single_coarse_rows=9/9`,
  `gauss6_single_coarse_rows=3/3`, and
  `single_coarse_work_precision_rows=4`; the local position order is `6.054`
  at `T=3`, `h=[0.1,0.05,0.025]`, reference `h=0.0125`. It also writes a
  4-row coarse-first external readiness gate with
  `coarse_first_ready_examples=2/4` and
  `local_true_dynamic_order_available=2`,
  `closed_loop_floor_audit_available=2`,
  `public_work_precision_available=2`,
  `public_work_precision_missing=0`,
  `strict_common_reference_available=2`,
  `strict_common_reference_gap=0`,
  `strict_common_reference_figure_available=True`, and
  `coarse_first_dynamic_order_missing=0`, explicitly keeping `1e-4` out of
  the default execution path. The 2-row
  `closed_loop_surrogate_dynamic_gate` records residual-to-error bridge values
  for `four_link` and `slider_crank`, but
  `closed_loop_surrogate_accepted_dynamic_order=0`. The 2-row
  `closed_loop_dynamic_error_floor_audit` records velocity/acceleration floor
  evidence for both closed-loop mechanisms, two position-floor blockers, and
  `closed_loop_floor_audit_accepted_dynamic_order=0`. The
  `closed_loop_coarse_dynamic_order_probe` repeats the closed-loop check at
  `T=0.2`, `h=[0.1,0.05,0.025]`, reference `h=0.0125`; it has `11/12` rows
  ok, one public `slider_crank`/`rA` failure at `h=0.1`, local
  velocity/acceleration evidence for both mechanisms, two position-floor
  blockers, and `closed_loop_coarse_probe_accepted_dynamic_order=0`. It records 48 method/example rows
  with 32 completed and 0 partial rows,
  and the 2-row `closed_loop_dynamic_order_closure_contract` records theorem
  order `6` for a true `Gauss6/FullVA` dynamic trajectory row while keeping
  true dynamic local rows at `0` for `four_link` and `slider_crank`. The
  2-row `closed_loop_true_dynamic_row_feasibility_audit` source-checks that
  the current local closed-loop path calls `simulate_v046_local_kinematic_fullva`,
  uses `setup_system(..., "kinematics", ...)`, reconstructs reactions after
  the kinematic solve, and is not a local dynamic DAE trajectory integrator,
  the 24-row `closed_loop_true_dynamic_local_row_plan` fixes the next
  plan-only parallel batch to `h=[0.1,0.05,0.025]`, reference `h=0.0125`,
  `execution_status=not_run`, and `default_1e-4=False`,
  the 4-row `closed_loop_true_dynamic_interface_audit` verifies setup-level
  public/v046 `rA` dynamics interfaces for both closed-loop models without
  calling `do_step`, while keeping the local `Gauss6/FullVA` dynamic runner
  missing,
  the 2-row `closed_loop_true_dynamic_residual_scaffold` fixes the missing
  runner's square residual layout at 72 unknowns/residuals per stage and 216
  per Gauss6 step without trajectory execution or accepted order,
  the 6-row `closed_loop_true_dynamic_stage_residual_audit` evaluates the
  FullVA stage residual families at all Gauss6 stage times for the two
  closed-loop mechanisms, currently with max residual about `5.51e-14`, while
  still not advancing an endpoint or accepting order,
  the 2-row `closed_loop_true_dynamic_one_step_smoke` advances one
  oracle-initialized Gauss6 step at `h=0.1` for both closed-loop mechanisms,
  currently with max endpoint position error about `4.41e-08`, while still not
  running a convergence sweep or accepting order,
  the 2-row `closed_loop_true_dynamic_newton_stage_smoke` advances one
  non-oracle Newton-initialized Gauss6 step at `h=0.1`, with max initial stage
  residual about `4.31e+01` and max final stage residual about `1.79e-13`,
  while still not running a convergence sweep or accepting order,
  the 6-row `closed_loop_true_dynamic_newton_coarse_order` runs the first
  non-oracle local true-dynamic coarse convergence sweep for `four_link` and
  `slider_crank` at `T=0.1`, `h=[0.1,0.05,0.025]`, reference `h=0.0125`;
  the primary state orders are about `5.955/5.955/6.085/5.971` for
  `four_link` and `6.164/6.159/7.341/6.426` for `slider_crank`, but this is
  still not external superiority,
  the 24-row `closed_loop_true_dynamic_public_work_precision` artifact adds
  the matching coarse public `rA/rp/reps` work/precision rows for
  `four_link` and `slider_crank` with `public_work_precision_available=2`,
  `public_work_precision_missing=0`, but
  `strict_common_reference_error_columns=false`,
  the 24-row `closed_loop_true_dynamic_strict_common_reference` artifact adds
  the same coarse rows against the common `v047_exact_kinematic_endpoint`
  reference with `strict_common_reference_available=2`,
  `strict_common_reference_gap=0`, and a work/precision figure,
  and the 7-row `closed_loop_residual_to_error_theorem_obligations` gate records
  seven blocking proof obligations before a residual-to-error surrogate can be
  promoted to accepted dynamic order,
  while preserving `external_superiority_claim=false`. This is still not full external
  superiority evidence.
- The submission bundle preflight is
  `paper_v047_cylindrical_chain/validate_submission_bundle.py`; it checks the
  manifest, required files, clean logs, PDFs, and `run_v047.py` boundary.
- The CMAME preflight is
  `paper_v047_cylindrical_chain/validate_cmame_submission.py`; it checks the
  `elsarticle` source, PDF, highlights, declarations, manifest, clean log, and
  `run_v047.py` boundary.
- The CMAME blocker-closure preflight is
  `paper_v047_cylindrical_chain/validate_cmame_blocker_closure_gate.py`; it
  checks the seven remaining blockers after B5 closure, same-test status,
  accepted dynamic-order example split, and no-default-`1e-4` policy.
- The CMAME external-baseline preflight is
  `paper_v047_cylindrical_chain/validate_cmame_external_baseline_gate.py`; it
  checks the same-test comparison boundary, coarse-first evidence count, local
  true-dynamic closed-loop order evidence, public work/precision availability,
  strict common-reference availability, and no external superiority claim.
- The CMAME proof-contract preflight is
  `paper_v047_cylindrical_chain/validate_cmame_proof_contract_gate.py`; it
  checks the conditional consistency-transfer theorem boundary, solver
  tolerance condition, symbolic-oracle gap, and residual-to-error non-acceptance.
- The CMAME visual-legibility preflight is
  `paper_v047_cylindrical_chain/validate_cmame_visual_legibility_audit.py`; it
  checks that B5 is closed by the final-PDF Figure 2 legibility audit without
  any default `1e-4` campaign.
- The CMAME related-work preflight is
  `paper_v047_cylindrical_chain/validate_cmame_related_work_audit.py`; it
  checks that B8 is closed by the six-cluster related-work pass without any
  default `1e-4` campaign.
- The dynamic row-oracle preflight is
  `paper_v047_cylindrical_chain/validate_dynamic_row_oracle_gate.py`; it
  imports `run_v047.py`, evaluates the accepted 132-row residual and AD
  Jacobian on a canonical smooth probe, cross-checks the Gauss6-equivalent
  weighted block-functional row families, and keeps
  `symbolic_oracle_complete=False`.

## Terminology: TFE Versus FTE

- `TFE` means temporal finite element.
- `FTE` is not a separate method in this package; if it appears in notes, read
  it as a typo for `TFE`.
- `full TFE replacement` means replacing the accepted `Gauss6/FullVA` 132-row
  stage residual with paper-derived temporal finite-element weak rows. This is
  stricter than the accepted formal-order comparison.

## Original Paper Versus Accepted v047 Claim

- Source-paper/local target: the local paper-style `m=3` Gauss-Lobatto TFE
  formula target has expected order `5` and is the comparator for the current
  paper-facing claim.
- Accepted v047 claim: the accepted `Gauss6/FullVA` path is a sixth-order
  one-step map with smooth observed orders `7.161/7.066` and four accepted
  ASME examples.
- Not claimed: complete source-paper residual reproduction, because
  `full_tfe_stage_replacement=false` remains open.
- Practical reading: this is a formal-order comparison and diagnostic
  same-problem comparison, not a statement that every source-paper TFE
  residual row has replaced the accepted `Gauss6/FullVA` stage residual inside
  Newton.

## What Is Still Open

- `full_tfe_stage_replacement=false`.
- The independent full TFE stage replacement is not accepted yet; it is the
  optional stronger source-paper reproduction gate, not a prerequisite for the
  accepted formal-order comparison.
- The row-space compression audit currently has 36 target-free rows, 0 spans,
  best residual about `7.378e-01`, and best non-final residual about
  `9.815e-01`.
- Sparse AD speed and sharp-friction coarse-regime behavior remain quantified
  caveats.
- The cross-paper same-test campaign remains open:
  `same_test_campaign_status=not_run`,
  `gauss6_fullva_external_rows_completed=false`, and
  `external_superiority_claim=false` in v048. The selected
  `gauss6_fullva_selected_rows_completed=true` and
  `gauss6_fullva_closed_loop_selected_rows_completed=true` pilots, the
  3/3 public-horizon single-pendulum tranche, the 6/6 public-horizon
  closed-loop residual tranche, and the 12/12 same-window comparison rows are
  bounded same-mechanism/residual row sets, not the full external campaign, and
  `velocity_partitioning_code_status=not_resolved_in_local_sbel_or_public_metadata_tree`
  keeps the VP baseline as a code-resolution gate.

## Which Command Should I Run?

Use this decision table before starting any long command:

| Goal | Command | Invokes full `run_v047.py`? |
| --- | --- | --- |
| Check the paper, four-example gate, full-TFE gap ledgers, and current v047 artifacts | `cd paper_v047_cylindrical_chain && ../../.venv_sbel/bin/python validate_paper_package.py` | No |
| Check the CMAME submission packet only | `cd paper_v047_cylindrical_chain && ../../.venv_sbel/bin/python validate_cmame_submission.py && ../../.venv_sbel/bin/python validate_submission_bundle.py` | No |
| Check only the submission artifact manifest boundary sync | `cd paper_v047_cylindrical_chain && ../../.venv_sbel/bin/python validate_submission_artifact_manifest_boundary_sync.py` | No |
| Check the concise supporting paper only | `cd paper_v047_cylindrical_chain && ../../.venv_sbel/bin/python validate_concise_paper.py && ../../.venv_sbel/bin/python validate_proof_evidence_matrix.py && ../../.venv_sbel/bin/python validate_order_acceptance_gate.py && ../../.venv_sbel/bin/python validate_implementation_fidelity_certificate.py && ../../.venv_sbel/bin/python validate_source_paper_comparison.py` | No |
| Check only the example-level order boundary | `cd paper_v047_cylindrical_chain && ../../.venv_sbel/bin/python validate_order_acceptance_gate.py` | No |
| Check only the implementation-fidelity proof certificate | `cd paper_v047_cylindrical_chain && ../../.venv_sbel/bin/python validate_implementation_fidelity_certificate.py` | No |
| Check only the full source-policy runner archive gate | `cd paper_v047_cylindrical_chain && ../../.venv_sbel/bin/python validate_full_source_policy_runner_archive_gap_audit.py` | No |
| Check only the TFE source-policy self-reproduction attempt gate | `cd paper_v047_cylindrical_chain && ../../.venv_sbel/bin/python validate_tfe_source_policy_self_reproduction_attempt_certificate.py` | No |
| Check only the OC6 source-equivalent reopen-readiness gate | `cd paper_v047_cylindrical_chain && ../../.venv_sbel/bin/python validate_oc6_source_equivalent_reopen_readiness_audit_20260620.py` | No |
| Check only the RA/HI/B4 source-policy closeout gates | `cd paper_v047_cylindrical_chain && ../../.venv_sbel/bin/python validate_ra_hi_source_policy_output_inventory.py && ../../.venv_sbel/bin/python validate_ra_hi_source_policy_closeout_checklist.py && ../../.venv_sbel/bin/python validate_ra_hi_source_policy_promotion_blocker_matrix.py && ../../.venv_sbel/bin/python validate_ra_hi_source_policy_post_execution_attempt_certificate.py && ../../.venv_sbel/bin/python validate_b4_source_policy_execution_opt_in_packet.py && ../../.venv_sbel/bin/python validate_b4_source_policy_guarded_driver.py && ../../.venv_sbel/bin/python validate_b4_source_policy_execution_handoff_package.py && ../../.venv_sbel/bin/python validate_full_source_policy_row_provenance_audit.py` | No |
| Check only the four ASME method rows | `cd ../numerics/v047_cylindrical_chain_pipeline && ../../.venv_sbel/bin/python validate_four_asme_minimal.py` | No |
| Check the cross-paper same-test scaffold smoke | `cd ../numerics/v048_cross_paper_same_test_benchmarks && ../../.venv_sbel/bin/python validate_v048_outputs.py` | No |
| Check the v048 four-example performance matrix | `cd ../numerics/v048_cross_paper_same_test_benchmarks && ../../.venv_sbel/bin/python validate_four_example_performance_matrix.py` | No |
| Check the v048 single-pendulum coarse same-window rows | `cd ../numerics/v048_cross_paper_same_test_benchmarks && ../../.venv_sbel/bin/python validate_single_pendulum_coarse_same_window.py` | No |
| Check the v048 closed-loop surrogate dynamic gate | `cd ../numerics/v048_cross_paper_same_test_benchmarks && ../../.venv_sbel/bin/python validate_closed_loop_surrogate_dynamic_gate.py` | No |
| Check the v048 closed-loop dynamic error floor audit | `cd ../numerics/v048_cross_paper_same_test_benchmarks && ../../.venv_sbel/bin/python validate_closed_loop_dynamic_error_floor_audit.py` | No |
| Check the v048 closed-loop coarse dynamic-order probe | `cd ../numerics/v048_cross_paper_same_test_benchmarks && ../../.venv_sbel/bin/python validate_closed_loop_coarse_dynamic_order_probe.py` | No |
| Check the v048 closed-loop dynamic-order closure contract | `cd ../numerics/v048_cross_paper_same_test_benchmarks && ../../.venv_sbel/bin/python validate_closed_loop_dynamic_order_closure_contract.py` | No |
| Check the v048 closed-loop true dynamic-row feasibility audit | `cd ../numerics/v048_cross_paper_same_test_benchmarks && ../../.venv_sbel/bin/python validate_closed_loop_true_dynamic_row_feasibility_audit.py` | No |
| Check the v048 closed-loop true dynamic local row plan | `cd ../numerics/v048_cross_paper_same_test_benchmarks && ../../.venv_sbel/bin/python validate_closed_loop_true_dynamic_local_row_plan.py` | No |
| Check the v048 closed-loop true dynamic interface audit | `cd ../numerics/v048_cross_paper_same_test_benchmarks && ../../.venv_sbel/bin/python validate_closed_loop_true_dynamic_interface_audit.py` | No |
| Check the v048 closed-loop true dynamic residual scaffold | `cd ../numerics/v048_cross_paper_same_test_benchmarks && ../../.venv_sbel/bin/python validate_closed_loop_true_dynamic_residual_scaffold.py` | No |
| Check the v048 closed-loop true dynamic stage residual audit | `cd ../numerics/v048_cross_paper_same_test_benchmarks && ../../.venv_sbel/bin/python validate_closed_loop_true_dynamic_stage_residual_audit.py` | No |
| Check the v048 closed-loop true dynamic one-step smoke | `cd ../numerics/v048_cross_paper_same_test_benchmarks && ../../.venv_sbel/bin/python validate_closed_loop_true_dynamic_one_step_smoke.py` | No |
| Check the v048 closed-loop true dynamic Newton stage smoke | `cd ../numerics/v048_cross_paper_same_test_benchmarks && ../../.venv_sbel/bin/python validate_closed_loop_true_dynamic_newton_stage_smoke.py` | No |
| Check the v048 closed-loop true dynamic Newton coarse order | `cd ../numerics/v048_cross_paper_same_test_benchmarks && ../../.venv_sbel/bin/python validate_closed_loop_true_dynamic_newton_coarse_order.py` | No |
| Check the v048 closed-loop true dynamic public work/precision rows | `cd ../numerics/v048_cross_paper_same_test_benchmarks && ../../.venv_sbel/bin/python validate_closed_loop_true_dynamic_public_work_precision.py` | No |
| Check the v048 closed-loop strict common-reference work/precision rows | `cd ../numerics/v048_cross_paper_same_test_benchmarks && ../../.venv_sbel/bin/python validate_closed_loop_true_dynamic_strict_common_reference.py` | No |
| Check the v048 residual-to-error theorem obligations | `cd ../numerics/v048_cross_paper_same_test_benchmarks && ../../.venv_sbel/bin/python validate_closed_loop_residual_to_error_theorem_obligations.py` | No |
| Check the v048 coarse-first external readiness gate | `cd ../numerics/v048_cross_paper_same_test_benchmarks && ../../.venv_sbel/bin/python validate_coarse_first_external_readiness_gate.py` | No |
| Run only the v048 public-code dependency smoke | `cd ../numerics/v048_cross_paper_same_test_benchmarks && ../../.venv_sbel/bin/python run_v048.py` | No |
| Check the whole repository artifact inventory | `../.venv_sbel/bin/python validate_pipeline_outputs.py` | No |
| Rebuild only the PDF from existing figures and tables | `cd legacy_drafts && cmd.exe /c latexmk -pdf -interaction=nonstopmode main.tex` | No |
| Rebuild only the CMAME/Elsevier manuscript | `cd ../paper && cmd.exe /c latexmk -pdf -interaction=nonstopmode main_cmame.tex` | No |
| Rebuild only the flat CMAME/Elsevier source copy | `cd paper_v047_cylindrical_chain/cmame_submission_flat && cmd.exe /c latexmk -pdf -interaction=nonstopmode main_cmame_submission.tex` | No |
| Rebuild only the concise better-integrator paper | `cd legacy_drafts && cmd.exe /c latexmk -pdf -interaction=nonstopmode main_concise.tex` | No |
| Explore one full-TFE repair hypothesis | `V047_TARGET_AUDIT=... ../../.venv_sbel/bin/python run_v047.py` | No, if the target audit exits through its JSON-only path |
| Regenerate every v047 numerical artifact | `cd ../numerics/v047_cylindrical_chain_pipeline && ../../.venv_sbel/bin/python run_v047.py` | Yes |

The TFE source-policy self-reproduction validator must print the current
non-promotion aliases directly:
`public_code_recheck_status=public_code_rechecked_no_distinct_tfe_code_artifact_attempted_not_reproducible`,
`reopen_condition=new_public_or_source_code_equivalent_tfe_implementation_artifact`,
`source_policy_execution_preflight_status=terminal_no_public_code_self_reproduction_attempted_not_promoted`,
`public_code_refresh_latest_positive_artifact_rows=0`, and
`source_policy_closed=0/16`.

For routine paper edits, claim checks, or the already-accepted four-example
method gate, do not run the last command. The full generator is an accumulated
historical audit harness, not the shortest path to validating the four
examples.

## Fast Paper And Four-Example Checks

Run the paper/package gate without rebuilding numerical artifacts:

```bash
cd paper_v047_cylindrical_chain
../../.venv_sbel/bin/python validate_cmame_submission.py
../../.venv_sbel/bin/python validate_submission_artifact_manifest_boundary_sync.py
../../.venv_sbel/bin/python validate_cmame_external_baseline_gate.py
../../.venv_sbel/bin/python validate_cmame_proof_contract_gate.py
../../.venv_sbel/bin/python validate_cmame_visual_legibility_audit.py
../../.venv_sbel/bin/python validate_cmame_related_work_audit.py
../../.venv_sbel/bin/python validate_full_source_policy_runner_archive_gap_audit.py
../../.venv_sbel/bin/python validate_tfe_source_policy_self_reproduction_attempt_certificate.py
../../.venv_sbel/bin/python validate_ra_hi_source_policy_output_inventory.py
../../.venv_sbel/bin/python validate_ra_hi_source_policy_closeout_checklist.py
../../.venv_sbel/bin/python validate_ra_hi_source_policy_promotion_blocker_matrix.py
../../.venv_sbel/bin/python validate_ra_hi_source_policy_post_execution_attempt_certificate.py
../../.venv_sbel/bin/python validate_b4_source_policy_execution_opt_in_packet.py
../../.venv_sbel/bin/python validate_paper_package.py
```

Run only the concise-paper gate:

```bash
cd paper_v047_cylindrical_chain
../../.venv_sbel/bin/python validate_cmame_submission.py
../../.venv_sbel/bin/python validate_cmame_external_baseline_gate.py
../../.venv_sbel/bin/python validate_cmame_proof_contract_gate.py
../../.venv_sbel/bin/python validate_cmame_visual_legibility_audit.py
../../.venv_sbel/bin/python validate_cmame_related_work_audit.py
../../.venv_sbel/bin/python validate_concise_paper.py
../../.venv_sbel/bin/python validate_proof_evidence_matrix.py
../../.venv_sbel/bin/python validate_implementation_fidelity_certificate.py
../../.venv_sbel/bin/python validate_source_paper_comparison.py
../../.venv_sbel/bin/python validate_full_source_policy_runner_archive_gap_audit.py
../../.venv_sbel/bin/python validate_tfe_source_policy_self_reproduction_attempt_certificate.py
../../.venv_sbel/bin/python validate_ra_hi_source_policy_output_inventory.py
../../.venv_sbel/bin/python validate_ra_hi_source_policy_closeout_checklist.py
../../.venv_sbel/bin/python validate_ra_hi_source_policy_promotion_blocker_matrix.py
../../.venv_sbel/bin/python validate_ra_hi_source_policy_post_execution_attempt_certificate.py
../../.venv_sbel/bin/python validate_b4_source_policy_execution_opt_in_packet.py
../../.venv_sbel/bin/python validate_submission_bundle.py
```

Run only the minimal four-ASME method gate:

```bash
cd ../numerics/v047_cylindrical_chain_pipeline
../../.venv_sbel/bin/python validate_four_asme_minimal.py
```

## Broader Read-Only Checks

Run the full v047 generated-artifact validator without invoking
`run_v047.py`:

```bash
cd ../numerics/v047_cylindrical_chain_pipeline
../../.venv_sbel/bin/python validate_full_tfe_gap.py
../../.venv_sbel/bin/python validate_full_tfe_repair_spec.py
../../.venv_sbel/bin/python validate_v047_outputs.py
```

The full-TFE gap validator reads `FULL_TFE_REPLACEMENT_GAP_LEDGER.md` and
checks that the current open replacement boundary is still explicit. The repair
spec validator reads `FULL_TFE_REPAIR_SPEC.md` and checks the next 132-row
implementation contract.

Run the recurrent weak-closure smoke entry without invoking the full
`run_v047.py` main path:

```bash
cd ../numerics/v047_cylindrical_chain_pipeline
V047_TARGET_AUDIT=lower_pair_recurrent_weak_closure_smoke ../../.venv_sbel/bin/python run_v047.py
```

This default smoke prints static wiring JSON only. A bounded one-step numerical
smoke is opt-in with `V047_RECURRENT_WEAK_SMOKE_NUMERIC=1`; both modes must
keep `full_tfe_stage_replacement=false` and `accepted_h_sweep_present=false`.

Run the bounded recurrent weak-closure short trajectory smoke:

```bash
cd ../numerics/v047_cylindrical_chain_pipeline
V047_TARGET_AUDIT=lower_pair_recurrent_weak_closure_trajectory_smoke ../../.venv_sbel/bin/python run_v047.py
```

The default short trajectory runs smooth and sharp at `h=0.04`, `t_final=0.08`,
prints JSON only, and must keep `trajectory_h_sweep_present=false`,
`terminal_velocity_closed=false`, and `full_tfe_stage_replacement=false`.

Run the bounded recurrent weak-closure h-sweep smoke:

```bash
cd ../numerics/v047_cylindrical_chain_pipeline
V047_TARGET_AUDIT=lower_pair_recurrent_weak_closure_h_sweep_smoke ../../.venv_sbel/bin/python run_v047.py
```

The default h-sweep smoke runs smooth and sharp over `h=[0.04,0.02]` against
`reference_h=0.01`. It prints JSON only and must keep
`trajectory_h_sweep_present=false`, `accepted_h_sweep_present=false`, and
`full_tfe_stage_replacement=false`. The full acceptance-shaped version is
explicit opt-in with `V047_RECURRENT_WEAK_H_SWEEP_FULL=1`.
The latest full-shaped run converged but kept `terminal_velocity_closed=false`
and `accepted_h_sweep_present=false`, so it remains diagnostic.

Run the recurrent/terminal one-step blend smoke:

```bash
cd ../numerics/v047_cylindrical_chain_pipeline
V047_TARGET_AUDIT=lower_pair_recurrent_terminal_blend_one_step_smoke ../../.venv_sbel/bin/python run_v047.py
```

This prints JSON only. It checks `gamma=[0,0.5,1]` between the recurrent weak
closure and the final-stage velocity closure; it is a one-step tradeoff screen,
not a trajectory h-sweep.

Run the recurrent/terminal h-sweep blend smoke:

```bash
cd ../numerics/v047_cylindrical_chain_pipeline
V047_TARGET_AUDIT=lower_pair_recurrent_terminal_blend_h_sweep_smoke ../../.venv_sbel/bin/python run_v047.py
```

This prints JSON only. It defaults to `gamma=[0.5,1.0]`, `h=[0.04,0.02]`,
and `reference_h=0.01`; use
`V047_RECURRENT_TERMINAL_BLEND_H_SWEEP_CASES=cylindrical_smooth` for the
shorter smooth-only check. The latest default smooth+sharp bounded run found
terminal closure at gamma `1.0`, but smooth minimum order was only `4.397` and
the sharp velocity order remained `-0.428`, so it keeps
`accepted_h_sweep_present=false`.

For a denser scalar-gamma exclusion screen without running the full generator:

```bash
cd ../numerics/v047_cylindrical_chain_pipeline
V047_TARGET_AUDIT=lower_pair_recurrent_terminal_blend_h_sweep_smoke V047_RECURRENT_TERMINAL_BLEND_H_SWEEP_GAMMAS=0,0.25,0.5,0.75,1 ../../.venv_sbel/bin/python run_v047.py
```

The latest dense bounded run converged 60 short-trajectory steps and still
found no order/terminal intersection: best smooth-order gamma `0.75` reached
only `4.414`, while terminal closure remained at gamma `1.0`.

For the near-terminal scalar-policy check:

```bash
cd ../numerics/v047_cylindrical_chain_pipeline
V047_TARGET_AUDIT=lower_pair_recurrent_terminal_blend_h_sweep_smoke V047_RECURRENT_TERMINAL_BLEND_H_SWEEP_GAMMAS=0.9,0.99,0.999,1 ../../.venv_sbel/bin/python run_v047.py
```

The latest near-terminal bounded run converged 48 short-trajectory steps. Best
smooth-order gamma was `0.99` with order `4.415`; gamma `0.999` still had
terminal velocity `4.678e-07`, and only gamma `1.0` terminal-closed.

For the component-wise one-step gamma sensitivity check:

```bash
cd ../numerics/v047_cylindrical_chain_pipeline
V047_TARGET_AUDIT=lower_pair_recurrent_terminal_component_one_step_smoke ../../.venv_sbel/bin/python run_v047.py
```

This prints JSON only and does not update artifacts. The latest run used both
cases, `10` gamma vectors, and `20` one-step rows in 31.6 seconds. It kept rank
`132` with max residual `1.766e-12`; `component_2_release_0p999` was the best
nontrivial terminal-velocity row at `3.456e-17`, while
`component_7_release_0p999` was the worst component release at `1.234e-11`.
This localizes the eight closure directions but remains
`accepted_h_sweep_present=false`.

For the component-wise trajectory gamma h-sweep:

```bash
cd ../numerics/v047_cylindrical_chain_pipeline
V047_TARGET_AUDIT=lower_pair_recurrent_terminal_component_h_sweep_smoke ../../.venv_sbel/bin/python run_v047.py
```

This is still JSON-only. The latest default run used four vector labels over
both cases and converged 48 short-trajectory steps in 98.4 seconds. The best
terminal vector was `component_2_release_0p999` at `2.696e-16`, but its smooth
order remained about `4.397`; the best smooth-order vector was `all_0p999` at
`4.401`, but it left terminal velocity `4.678e-07`. The trajectory-level
component screen therefore keeps `order_terminal_intersection_present=false`.

For the recurrent history-gamma trajectory screen:

```bash
cd ../numerics/v047_cylindrical_chain_pipeline
V047_TARGET_AUDIT=lower_pair_recurrent_history_gamma_h_sweep_smoke ../../.venv_sbel/bin/python run_v047.py
```

This is also JSON-only. The default smooth-only run uses policy
`history_abs_inf`, releases `[0.001,0.01]`, and `h=[0.04,0.02]` against
`reference_h=0.01`. It converged 12 short-trajectory steps in 38.9 seconds,
kept rank `132`, max residual `2.586e-12`, best terminal velocity
`1.451e-07`, and best smooth minimum order `4.402`. A signed-policy check
with `history_signed_positive,history_signed_negative` converged in 36.9
seconds with max residual `3.869e-12`, best terminal velocity `1.452e-07`,
and best smooth order `4.415`. Both checks keep
`order_terminal_intersection_present=false`,
`accepted_h_sweep_present=false`, and `full_tfe_stage_replacement=false`.

For the recurrent weak-row differential audit:

```bash
cd ../numerics/v047_cylindrical_chain_pipeline
V047_TARGET_AUDIT=lower_pair_recurrent_weak_differential_audit ../../.venv_sbel/bin/python run_v047.py
```

This is JSON-only and one-step local. The latest default smooth run checks
`zero_initial` and `post_one_step` history modes at `h=0.04`, completes in
26.0 seconds, keeps rank `132`, and has max residual `2.483e-12`. The current
recurrent weak row does not span the terminal bridge:
`any_recurrent_weak_spans_terminal_bridge=false`, recurrent projection
residuals are `0.899` to `0.974`, while the final-stage terminal row projects
at `1.456e-15`. The missing direction is stage-2-local and dominated by
`translation_velocity_v`, so the next change must alter the analytical weak
row formula, not tune another gamma.

For the stage-2 coefficient-gradient differential audit:

```bash
cd ../numerics/v047_cylindrical_chain_pipeline
V047_TARGET_AUDIT=lower_pair_recurrent_stage2_gradient_differential_audit ../../.venv_sbel/bin/python run_v047.py
```

This is also JSON-only and local. The latest default smooth run checks two
source/history features and gains `[1e8,1e12]`, completes in 35.3 seconds,
keeps rank `132`, and has max residual `2.483e-12`. It does not find a local
span: `any_candidate_spans_terminal_bridge=false`, best projection residual
`0.899`, best gain `1e12`, and independent target rank `8`.

For the stage-2 matrix-gradient differential audit:

```bash
cd ../numerics/v047_cylindrical_chain_pipeline
V047_TARGET_AUDIT=lower_pair_recurrent_stage2_matrix_gradient_differential_audit ../../.venv_sbel/bin/python run_v047.py
```

This is JSON-only and local. The latest default smooth run checks four
target-free row/column matrix laws and gains `[1e8,1e12]`, completes in 45.8
seconds, keeps rank `132`, and has max residual `2.483e-12`. It still does not
find a local span: `any_candidate_spans_terminal_bridge=false`, best law
`diagonal_plus_row_broadcast_feature`, best projection residual `0.898873`,
best gain `1e12`, and independent target rank `8`.

An active-velocity extension of that target uses:

```bash
cd ../numerics/v047_cylindrical_chain_pipeline
V047_TARGET_AUDIT=lower_pair_recurrent_stage2_matrix_gradient_differential_audit V047_RECURRENT_STAGE2_MATRIX_LAWS=stage2_velocity_row_broadcast_feature,stage2_velocity_column_broadcast_feature,stage2_minus_stage1_velocity_row_broadcast_feature,velocity_curvature_diagonal_plus_row_broadcast_feature V047_RECURRENT_STAGE2_MATRIX_GAINS=1e8,1e12 ../../.venv_sbel/bin/python run_v047.py
```

It completes in 46.6 seconds over 16 local rows. The best law is
`stage2_velocity_column_broadcast_feature` at gain `1e12`, with projection
residual `0.585746`, but independent target rank remains `8` and
`any_candidate_spans_terminal_bridge=false`.

An expanded active-law grid over five stage-velocity matrix laws completes in
51.2 seconds over 20 local rows. The best law is
`stage2_velocity_shifted_column_broadcast_feature` at gain `1e12`, with
projection residual `0.576548`; independent target rank still remains `8` and
`any_candidate_spans_terminal_bridge=false`.

A JSON-only best-law missing-direction decomposition completes in 27.8 seconds
over 2 local rows. The best post-one-step row remains residual `0.576548` with
rank-eight missing direction, dominant variable family `angular_velocity_w` at
fraction `0.502991`, and stage-2 fraction `0.963038`.

A stage-2 angular-velocity mask grid completes in 35.3 seconds over 8 local
rows. The best law is
`stage2_angular_velocity_shifted_column_broadcast_feature` at gain `1e12`,
with projection residual `0.752997`; independent target rank remains `8` and
`any_candidate_spans_terminal_bridge=false`, so simple angular-only masking is
not enough.

A direct translation/angular cross-coupling grid completes in 35.3 seconds over
8 local rows. The best law is
`stage2_velocity_angular_to_translation_cross_feature` at gain `1e12`, with
projection residual `0.898812`; independent target rank remains `8`, the
remaining direction is still dominated by `translation_velocity_v` at fraction
`0.556004`, and `any_candidate_spans_terminal_bridge=false`.

An endpoint-pose generalized-velocity predictor grid completes in 31.2 seconds
over 10 local rows. The best law is
`paper_endpoint_pose_positive_lagrange_z`, with projection residual `0.117782`;
independent target rank remains `8`, the remaining direction is dominated by
`translation_velocity_v` at fraction `0.514237`, and
`any_candidate_spans_terminal_bridge=false`.

A near-terminal stage-0/stage-2 convex predictor grid completes in 31.7 seconds
over 14 local rows. The stage-2-only law
`paper_endpoint_pose_stage02_convex_0p00_z` spans locally at roundoff but is
`terminal_bridge_equivalent_predictor=true`. The best nonterminal law is
`paper_endpoint_pose_stage02_convex_0p05_z`, with projection residual
`0.049317`; independent target rank remains `8` and
`any_nonterminal_candidate_spans_terminal_bridge=false`.
Focused h-scaling reruns at `h=0.02` and `h=0.01` keep the terminal-equivalent
row at roundoff span but leave the same nonterminal row at residuals `0.051890`
and `0.052472`; this is still an open full-TFE gap.
A synchronized pose/velocity near-terminal check improves the best local row to
`0.009512` with `stage02_convex_pose_velocity_0p01_z`, but `h=0.02` and
`h=0.01` stay at `0.009978` and `0.010085`, with rank `8` and no span.
The terminal-limit extrapolation
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_z` reaches `4.699e-06`,
then `2.335e-06` and `1.168e-06` at `h=0.02` and `h=0.01`, but remains
no-span and terminal-bridge-equivalent.
Direct `-1/+1` mean-acceleration bridge corrections worsen the best residual
to `0.076159` or above and move the missing direction to `lie_position_u`.

A source-to-velocity lift follow-up maps lower-pair source rows through the
current-pose endpoint velocity matrix `C_v`. It runs in 76.4 seconds over 34
local rows, keeps the uncorrected `stage02_convex_pose_velocity_0p01_z` row
best at residual `0.009512`, and gives best corrected residual `0.609803`; no
candidate spans.

A stage-0/stage-2 `C_v` matrix-difference lift then runs a 26-row scale sweep
in 92.5 seconds. It again keeps the uncorrected row best at residual `0.009512`
and gives best corrected residual `0.009527`; no candidate spans.

A normalized-history source-direction variant runs 10 local rows in 49.4
seconds, keeps the uncorrected row best at `0.009512`, and gives best corrected
residual `0.009590`; no candidate spans.

A terminal-limit curvature source-lift scale refinement runs 11 local rows in
52.9 seconds. The best law
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_curvature_p0p01_z`
remains at residual `5.298e-06`, with source-curvature norm `1.076e-14` and no
span.

A terminal-limit mean-acceleration bridge scale refinement runs 11 local rows
in 31.4 seconds. The best nonterminal correction is
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_accel_p0p01_z`, with
residual `0.000867721`; no candidate spans.

A generalized-acceleration Taylor-shift refinement runs 11 local rows in 30.2
seconds. The best nonterminal correction is
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_genaccel_p0p01_z`, with
residual `0.000866899`; no candidate spans.

A pose-acceleration Taylor-shift refinement runs 11 local rows in 29.9 seconds.
The best nonterminal correction is
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_p0p01_z`, with
residual `4.1835e-05`; no candidate spans.

A tiny pose-acceleration scale refinement runs 10 local rows in 30.0 seconds.
The best nonterminal correction is
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_p0p0005_z`, with
residual `5.5898e-06`; no candidate spans.

A pose+velocity acceleration Taylor refinement runs 11 local rows in 30.7
seconds. The best nonterminal correction is
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_posevelaccel_p0p0005_m0p0001_z`,
with residual `1.0173e-05`; no candidate spans. This is worse than the tiny
pose-only refinement and still does not provide an independent full-TFE row.

A component-split pose-acceleration Taylor refinement separates the same pose
shift into translation-only and angular/Lie-only branches. Two JSON-only
screens cover 26 local rows in 32.3+32.3 seconds. Translation-only shifts up to
coefficient `0.1` remain locally indistinguishable from the uncorrected
terminal-limit row; the best split law is
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_transposeaccel_m0p01_z`,
with residual `5.298e-06` and no span. The angular-only branch reproduces the
full pose-acceleration trend: `angposeaccel_p0p002` reaches `9.6511e-06`, and
`angposeaccel_p0p01` reaches `4.1835e-05`; no candidate spans.

A component-split velocity-acceleration Taylor refinement separates the
`h*zdot` generalized-velocity shift into translational and angular velocity
branches. The first JSON-only screen covers 13 local rows in 31.8 seconds; the
best nonterminal row is
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelaccel_m0p01_z`,
with residual `2.138e-04`, while the best angular branch
`angvelaccel_p0p01` reaches `0.000864560`; no candidate spans. A tiny
translational scale screen covers 11 local rows in 31.4 seconds, with best law
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelaccel_m0p0005_z`
at residual `9.8175e-06`; this is still worse than the uncorrected
terminal-limit residual `5.298e-06`, so the tested velocity-acceleration split
is also diagnostic only.

A component-mixed pose/velocity Taylor refinement combines angular/Lie pose
shift with translational velocity shift, plus the complementary
translation-pose/angular-velocity branch. The JSON-only screen covers 13 local
rows in 32.0 seconds. Its best law is
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_angpose_transvelaccel_p0p0005_m0p0005_z`,
with residual `9.987e-06`, independent target rank `8`, and no span; this is
still worse than the uncorrected terminal-limit residual `5.298e-06`.

A stage-2-fixed/delta acceleration velocity-shift refinement tests whether the
remaining translation-acceleration direction comes from using an interpolated
acceleration source. The JSON-only screen covers 13 local rows in 31.8
seconds. Its best law is
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelaccelstage2_m0p0005_z`,
with residual `9.8175e-06`, while the best delta20 branch
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelacceldelta20_m0p0005_z`
reaches `1.0119e-05`; no candidate spans.

A nonfinal terminal velocity/source predictor refinement uses only stage-0 and
stage-1 velocity rows plus source estimates to predict the terminal closure.
The JSON-only screen covers 9 local rows in 30.9 seconds. Its best law is
`nonfinal_velocity_terminal_euler1_z`, with residual `0.923466`, dominant
family `translation_velocity_v`, and stage-2 fraction `0.959959`; no candidate
spans.

A stage-2 source-to-velocity transport refinement applies source/history
projection directly at the stage-2 pose/velocity closure. The first screen
covers 13 local rows in 53.4 seconds; its best law is
`stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p1_z`
with residual `0.001251`. A scale refinement covers 11 rows in 57.7 seconds
and improves the best residual to `0.0001251` at
`stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p01_z`;
an ultra-fine scale follow-up covers 9 rows in 49.6 seconds and improves the
best nonterminal residual to `1.251e-06` at
`stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p0001_z`.
A combined angular-pose follow-up covers 8 rows in 48.7 seconds; its best
combined law
`stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p0001_angposeaccel_p0p0001_z`
reaches only `1.296e-06` and returns the independent target rank to `8`.
No candidate spans.

A bare endpoint-pose velocity check adds
`stage02_convex_pose_velocity_0p00_z` beside the ultra-fine transport row. It
runs 3 local rows in 31.7 seconds and spans the local terminal bridge at
residual `1.327e-15`, with `span_row_count=1`. This is
local-span-not-full-TFE evidence only: the row has not passed a nonlinear
trajectory h-sweep or order proof, and `full_tfe_stage_replacement=false`
remains the claim boundary.

For the bounded endpoint-pose velocity predictor trajectory smoke:

```bash
cd ../numerics/v047_cylindrical_chain_pipeline
V047_TARGET_AUDIT=lower_pair_endpoint_pose_velocity_predictor_h_sweep_smoke ../../.venv_sbel/bin/python run_v047.py
```

The default JSON-only smoke uses smooth `stage02_convex_pose_velocity_0p00_z`,
`h=[0.04,0.02]`, `reference_h=0.01`, and `t_final=0.04`. It runs in 21.5
seconds, closes terminal velocity to `7.29e-17`, but has orders `6.588/4.508`
and keeps `accepted_h_sweep_present=false`. A smooth three-h refinement over
`h=[0.04,0.02,0.01]` against `reference_h=0.005` runs in 28.6 seconds, closes
terminal velocity to `8.124e-17`, but has orders `4.142/2.305`. The nearby
`stage02_convex_pose_velocity_0p01_z` smoke leaves terminal velocity at
`6.255e-06` with orders `2.345/1.878`.

A remaining Gauss endpoint-pose follow-up runs 11 local rows. Its best law is
`gauss_endpoint_pose_stage02_convex_0p00_z`, with residual `0.172659`,
independent target rank `6`, and no terminal-bridge span.

A bilinear active-velocity outer-product grid over six feature/stage-2-velocity
matrix laws completes in 57.3 seconds over 24 local rows. The best law is
`stage2_velocity_feature_outer_stage2_velocity` at gain `1e12`, with projection
residual `0.898720`; independent target rank still remains `8` and
`any_candidate_spans_terminal_bridge=false`.

A componentwise active-velocity diagonal grid over six Hadamard/shifted-diagonal
matrix laws completes in 56.7 seconds over 24 local rows. The best law is
`stage2_velocity_diagonal_plus_hadamard_row_feature_stage2_velocity` at gain
`1e12`, with projection residual `0.898530`; independent target rank still
remains `8` and `any_candidate_spans_terminal_bridge=false`.

A stage-2 active translation/angular cross refinement covers 24 local rows in
50.9 seconds. The best law is
`stage2_velocity_symmetric_translation_angular_cross_feature` at gain `1e12`,
with projection residual `0.898843`; independent target rank remains `8`,
the missing direction is still `translation_velocity_v` with fraction
`0.556036`, and the stage-2 fraction is `0.999999`. It is another JSON-only
no-span exclusion, not a full TFE repair.

A non-stage-2 mean/source/history feature matrix refinement covers 12 local
rows in 36.5 seconds. The best law is
`stage01_mean_velocity_diagonal_plus_row_broadcast_feature` at gain `1e12`,
with projection residual `0.827381`; independent target rank remains `8`,
the missing direction is still `translation_velocity_v` with fraction
`0.571311`, and the stage-2 fraction is `0.991949`. This is localization
evidence, not a full TFE repair.

Run the top-level repository gate:

```bash
../.venv_sbel/bin/python validate_pipeline_outputs.py
```

## Paper PDF Build

Build the LaTeX draft from the paper directory:

```bash
cd paper_v047_cylindrical_chain
cmd.exe /c latexmk -pdf -interaction=nonstopmode main.tex
```

The PDF build uses existing result artifacts. It does not require numerical
regeneration.

## Full Numerical Regeneration

Only rerun the full v047 generator after changing numerical method code or
artifact-producing audit code:

```bash
cd ../numerics/v047_cylindrical_chain_pipeline
../../.venv_sbel/bin/python run_v047.py
```

The latest recorded full regeneration time is `2386.76` seconds. For paper
edits, claim checks, or the four-example acceptance check, use the fast
validators above instead.

## Where the LaTeX lives (2026-09-20)

The manuscript, figures, flat copy and arXiv version are in `paper/`; LaTeX builds run inside `paper/` (the `latexmk` commands above are unchanged, only the working directory moved). The evidence ledger and all validators stay in `paper_v047_cylindrical_chain/`.
