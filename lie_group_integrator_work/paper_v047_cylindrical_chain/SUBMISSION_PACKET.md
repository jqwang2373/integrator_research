# v047 Submission Packet

This is the submission-facing index for the v047 paper package. The current
top-level review status is **do not submit globally yet**. The narrowed-claim
quality result is a bounded subsidiary subcheck, not the global review verdict.
The full source-policy package remains **not ready**: source-policy rows are
still `0/40`, external superiority remains a non-claim, and source-policy
work/precision reintroduction is future work.
Audit marker: Full source-policy package remains not ready.

Full source-policy runner archive boundary: safe actions without B4 opt-in
`4`; opt-in-required actions `1`; source-policy execution allowed now `False`;
exact B4 opt-in required for execution `True`; opt-in commands/mapped external
rows `13/20`. Command-row traceability covers unique RA/HI rows `20/20`, row
refs `32/32`, and mismatch/terminal/closed/promotion-ready counts `0/0/0/0`.
Safe action ids are `rebuild_read_only_audit_chain,rerun_read_only_validators,keep_narrowed_archive_provenance_only,monitor_reopen_conditions`;
opt-in action ids are `authorized_b4_ra_hi_source_policy_execution`.
The guarded driver is
`run_b4_source_policy_after_opt_in.sh`, and the exact approval phrase is
`I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json.`.
Narrowed archive boundary matches the reproducibility manifest: `True`.
Narrowed archive boundary status/source-policy/use/execution/exact:
`narrowed_archive_ready_not_full_source_policy_runner_archive/0/40/False/False/True`.
Narrowed archive boundary blocking ids/status:
`OC4,OC6,OC12` / `OC4=open,OC6=partial,OC12=partial`.
Objective completion blocker matrix:
`blocker_open_by_id=OC4:True,OC6:True,OC12:True`;
`blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready`;
`blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False`.
These markers mean the recorded global blockers remain open; they are not a
submission-ready signal.
The current archive use is therefore `narrowed_claim_only`, not a full
source-policy runner archive.

## Bounded Narrowed-Claim Subcheck

The narrowed formal-order/common-reference diagnostic claim passes its bounded
subcheck, but this does not override the global `do_not_submit_global` review.
The narrowed proof route is the direct residual-bridge/Kantorovich route; the
primitive 162-term Taylor route remains an open conditional certificate schema
and is not the active direct-PC2 theorem-input route.
The mechanically complete draft/source package is:

- `main_cmame.pdf`
- `main_cmame.tex`
- `highlights_cmame.txt`
- `declarations_cmame.md`
- `CMAME_SUBMISSION_CHECKLIST.md`
- `CMAME_SUBMISSION_READINESS_AUDIT.md`
- `CMAME_SUBMISSION_READINESS_REVIEW.md`
- `CMAME_SUBMISSION_INTEGRITY_AUDIT.md`
- `CMAME_SUBMISSION_INTEGRITY_AUDIT.json`
- `CMAME_BLOCKER_CLOSURE_GATE.md`
- `CMAME_BLOCKER_CLOSURE_GATE.json`
- `CMAME_EXTERNAL_BASELINE_GATE.md`
- `CMAME_EXTERNAL_BASELINE_GATE.json`
- `CMAME_PROOF_CONTRACT_GATE.md`
- `CMAME_PROOF_CONTRACT_GATE.json`
- `CMAME_VISUAL_LEGIBILITY_AUDIT.md`
- `CMAME_VISUAL_LEGIBILITY_AUDIT.json`
- `CMAME_FIGURE_SET_AUDIT.md`
- `CMAME_FIGURE_SET_AUDIT.json`
- `validate_cmame_figure_set_audit.py`
- `CMAME_RELATED_WORK_AUDIT.md`
- `CMAME_RELATED_WORK_AUDIT.json`
- `CMAME_PROSE_RESIDUE_AUDIT.md`
- `CMAME_PROSE_RESIDUE_AUDIT.json`
- `DYNAMIC_ROW_ORACLE_GATE.md`
- `DYNAMIC_ROW_ORACLE_GATE.json`
- `NEWTON_EULER_DEFECT_OBLIGATION_GATE.md`
- `NEWTON_EULER_DEFECT_OBLIGATION_GATE.json`
- `NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.md`
- `NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.json`
- `NEWTON_EULER_DYNAMIC_ROW_CLOSURE_CONTRACT.md`
- `NEWTON_EULER_DYNAMIC_ROW_CLOSURE_CONTRACT.json`
- `README_CMAME_FLAT_SUBMISSION.md`
- `cmame_submission_flat/main_cmame_submission.tex`
- `cmame_submission_flat/main_cmame_submission.pdf`
- `cmame_submission_flat.zip`
- `cmame_submission_flat/highlights_cmame.txt`
- `cmame_submission_flat/declarations_cmame.md`
- `cmame_submission_flat/Figure_1_convergence.png`
- `cmame_submission_flat/Figure_2_asme_lower_pair_graph_bridge.png`
- `cmame_submission_flat/Figure_3_asme_closed_loop_kinematic_fullva.png`
- `cmame_submission_flat/Figure_4_order_closure_blend.png`
- `cmame_submission_flat/Figure_5_velocity_compression.png`
- `cmame_submission_flat/Figure_6_sparse_speed_gap.png`
- `cmame_submission_flat/Figure_7_strict_common_reference_work_precision.png`
- `cmame_submission_flat/Figure_8_claim_boundary_limitations.png`
- `cmame_submission_flat/Figure_9_coarse_baseline_work_precision.png`
- `cmame_submission_flat/Figure_10_closed_loop_true_dynamic_order.png`
- `cmame_submission_flat/Figure_11_method_stage_architecture.png`
- `cmame_submission_flat/Figure_12_all_method_result_matrix.png`
- `cmame_submission_flat/Figure_13_work_precision_compendium.png`
- `figures/convergence.png`
- `figures/asme_lower_pair_graph_bridge.png`
- `figures/asme_closed_loop_kinematic_fullva.png`
- `figures/order_closure_blend.png`
- `figures/velocity_compression.png`
- `figures/sparse_speed_gap.png`
- `figures/strict_common_reference_work_precision.png`
- `figures/claim_boundary_limitations.png`
- `figures/coarse_baseline_work_precision.png`
- `figures/closed_loop_true_dynamic_order.png`
- `figures/method_stage_architecture.png`
- `figures/all_method_result_matrix.png`
- `figures/work_precision_compendium.png`

Keep as supporting audit material:

- `main_concise.pdf`
- `main.pdf`
- `COVER_LETTER.md`
- `SUBMISSION_ARTIFACT_MANIFEST.json`
- `sync_submission_artifact_manifest_boundary.py`
- `validate_submission_artifact_manifest_boundary_sync.py`
- `SUBMISSION_FILE_INVENTORY.md`
- `REVIEW_RESPONSE_TEMPLATE.md`
- `PROOF_EVIDENCE_MATRIX.md`
- `CMAME_BLOCKER_CLOSURE_GATE.md`
- `CMAME_BLOCKER_CLOSURE_GATE.json`
- `CMAME_SUBMISSION_INTEGRITY_AUDIT.md`
- `CMAME_SUBMISSION_INTEGRITY_AUDIT.json`
- `CMAME_EXTERNAL_BASELINE_GATE.md`
- `CMAME_EXTERNAL_BASELINE_GATE.json`
- `CMAME_PROOF_CONTRACT_GATE.md`
- `CMAME_PROOF_CONTRACT_GATE.json`
- `PROOF_NUMERICAL_SCALE_AUDIT.md`
- `PROOF_NUMERICAL_SCALE_AUDIT.json`
- `PROOF_SOLVER_SCALE_AUDIT.md`
- `PROOF_SOLVER_SCALE_AUDIT.json`
- `PROOF_SOLVER_SCALED_TOLERANCE_PROBE.md`
- `PROOF_SOLVER_SCALED_TOLERANCE_PROBE.json`
- `PROOF_SOLVER_SCALED_TOLERANCE_TRAJECTORY_PROBE.md`
- `PROOF_SOLVER_SCALED_TOLERANCE_TRAJECTORY_PROBE.json`
- `PROOF_SOLVER_SCALED_TOLERANCE_TRAJECTORY_PROBE.csv`
- `PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.md`
- `PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.json`
- `PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.csv`
- `CMAME_VISUAL_LEGIBILITY_AUDIT.md`
- `CMAME_VISUAL_LEGIBILITY_AUDIT.json`
- `CMAME_FIGURE_SET_AUDIT.md`
- `CMAME_FIGURE_SET_AUDIT.json`
- `validate_cmame_figure_set_audit.py`
- `CMAME_RELATED_WORK_AUDIT.md`
- `CMAME_RELATED_WORK_AUDIT.json`
- `CMAME_PROSE_RESIDUE_AUDIT.md`
- `CMAME_PROSE_RESIDUE_AUDIT.json`
- `DYNAMIC_ROW_ORACLE_GATE.md`
- `DYNAMIC_ROW_ORACLE_GATE.json`
- `ORDER_ACCEPTANCE_GATE.md`
- `ORDER_ACCEPTANCE_GATE.json`
- `IMPLEMENTATION_FIDELITY_CERTIFICATE.md`
- `IMPLEMENTATION_PATH_AUDIT.md`
- `IMPLEMENTATION_PATH_AUDIT.json`
- `KINEMATIC_ROW_DEFECT_CERTIFICATE.md`
- `KINEMATIC_ROW_DEFECT_CERTIFICATE.json`
- `NEWTON_EULER_DEFECT_OBLIGATION_GATE.md`
- `NEWTON_EULER_DEFECT_OBLIGATION_GATE.json`
- `NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.md`
- `NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.json`
- `NEWTON_EULER_DYNAMIC_ROW_CLOSURE_CONTRACT.md`
- `NEWTON_EULER_DYNAMIC_ROW_CLOSURE_CONTRACT.json`
- `D5_P_STATE_LIFT_GAP_AUDIT.md`
- `D5_P_STATE_LIFT_GAP_AUDIT.json`
- `D5_P_STATE_MAP_DEFINITION_AUDIT.md`
- `D5_P_STATE_MAP_DEFINITION_AUDIT.json`
- `D5_P_STATE_ANTICIRCULARITY_AUDIT.md`
- `D5_P_STATE_ANTICIRCULARITY_AUDIT.json`
- `D5_P_STATE_PS2_WEIGHTED_TARGET_AUDIT.md`
- `D5_P_STATE_PS2_WEIGHTED_TARGET_AUDIT.json`
- `D5_P_STATE_PS2_AGGREGATE_PROMOTION_AUDIT.md`
- `D5_P_STATE_PS2_AGGREGATE_PROMOTION_AUDIT.json`
- `D5_P_STATE_PS2_LINEARIZATION_PROBE.md`
- `D5_P_STATE_PS2_LINEARIZATION_PROBE.json`
- `D5_P_STATE_PS2_LINEARIZATION_PROBE.csv`
- `D5_P_STATE_PS3_CONDITIONAL_CONVERSION_AUDIT.md`
- `D5_P_STATE_PS3_CONDITIONAL_CONVERSION_AUDIT.json`
- `D5_P_STATE_PS3_ACTUAL_INSTANTIATION_GAP_AUDIT.md`
- `D5_P_STATE_PS3_ACTUAL_INSTANTIATION_GAP_AUDIT.json`
- `D5_P_STATE_PS3_H_ACC_INPUT_OBSTRUCTION_AUDIT.md`
- `D5_P_STATE_PS3_H_ACC_INPUT_OBSTRUCTION_AUDIT.json`
- `D5_P_ACC_PA2_WEIGHTED_INVERSE_AUDIT.md`
- `D5_P_ACC_PA2_WEIGHTED_INVERSE_AUDIT.json`
- `D5_P_LAMBDA_INF_SUP_PROBE.md`
- `D5_P_LAMBDA_INF_SUP_PROBE.json`
- `D5_P_LAMBDA_INF_SUP_PROBE.csv`
- `D5_P_LAMBDA_PL2_GEOMETRIC_MARGIN_AUDIT.md`
- `D5_P_LAMBDA_PL2_GEOMETRIC_MARGIN_AUDIT.json`
- `D5_P_LAMBDA_D3_NONCIRCULARITY_AUDIT.md`
- `D5_P_LAMBDA_D3_NONCIRCULARITY_AUDIT.json`
- `D5_CONDITIONAL_TAYLOR_CERTIFICATE.md`
- `D5_CONDITIONAL_TAYLOR_CERTIFICATE.json`
- `v048_cross_paper_same_test_benchmarks/results/closed_loop_residual_to_error_theorem_obligations.json`
- `v048_cross_paper_same_test_benchmarks/results/closed_loop_residual_to_error_theorem_obligations.csv`
- `v048_cross_paper_same_test_benchmarks/results/closed_loop_residual_to_error_theorem_obligations.md`
- `SOURCE_PAPER_COMPARISON.md`
- `CROSS_PAPER_BENCHMARK_MATRIX.md`
- `CROSS_PAPER_BENCHMARK_SPEC.md`
- `CROSS_PAPER_BENCHMARK_CASES.json`
- `EXTERNAL_SAME_TEST_RUN_QUEUE.md`
- `EXTERNAL_SAME_TEST_RUN_QUEUE.json`
- `EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.md`
- `EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.json`
- `KISSEL_NEGRUT_CODE_INVENTORY.md`
- `PAPER_RESULT_PACK.md`
- `PAPER_RESULT_PACK.json`
- `PAPER_NUMERICAL_RESULT_MATRIX.md`
- `PAPER_NUMERICAL_RESULT_MATRIX.json`
- `PAPER_NUMERICAL_RESULT_MATRIX.csv`
- `RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.md`
- `RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.json`
- `ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.md`
- `ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.json`
- `ALL_EXAMPLES_RESULT_SANITY_AUDIT.md`
- `ALL_EXAMPLES_RESULT_SANITY_AUDIT.json`
- `ALL_EXAMPLES_SOURCE_POLICY_AUDIT.md`
- `ALL_EXAMPLES_SOURCE_POLICY_AUDIT.json`
- `SOURCE_POLICY_CLOSURE_TRIAGE.md`
- `SOURCE_POLICY_CLOSURE_TRIAGE.json`
- `SOURCE_POLICY_ROW_CLOSURE_LEDGER.md`
- `SOURCE_POLICY_ROW_CLOSURE_LEDGER.json`
- `COMMON_REFERENCE_ORDER_RECOMPUTATION_AUDIT.md`
- `COMMON_REFERENCE_ORDER_RECOMPUTATION_AUDIT.json`
- `EXTERNAL_BASELINE_SOURCE_POLICY_DIAGNOSIS.md`
- `EXTERNAL_BASELINE_SOURCE_POLICY_DIAGNOSIS.json`
- `EXTERNAL_SUITE_DISPOSITION_AUDIT.md`
- `EXTERNAL_SUITE_DISPOSITION_AUDIT.json`
- `EXTERNAL_CASE_EVIDENCE_RECONCILIATION.md`
- `EXTERNAL_CASE_EVIDENCE_RECONCILIATION.json`
- `VP2024_CODE_PATH_DISPOSITION_AUDIT.md`
- `VP2024_CODE_PATH_DISPOSITION_AUDIT.json`
- `COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.md`
- `COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.json`
- `CMAME_REVIEW_AGENT_REPORT.md`
- `CMAME_REVIEW_AGENT_REPORT.json`
- `CMAME_PROOF_STYLE_AUDIT.md`
- `CMAME_PROOF_STYLE_AUDIT.json`
- `PROOF_CLAIM_TRACEABILITY_AUDIT.md`
- `PROOF_CLAIM_TRACEABILITY_AUDIT.json`
- `PAPER_CLAIM_LEDGER.md`
- `REVIEWER_CHECKLIST.md`
- `CLAIM_BOUNDARY.json`
- `REPRODUCIBILITY_GUIDE.md`
- `run_human_reproducibility.py`
- `human_reproducibility_result_table.md`
- `replay_reproducibility_core.py`
- `run_reproduction_smoke.sh`
- `B6_CLOSED_LOOP_SELF_CONTAINED_EXTRACTION_AUDIT.md`
- `B6_CLOSED_LOOP_SELF_CONTAINED_EXTRACTION_AUDIT.json`
- `CMAME_CLOSED_LOOP_LOCAL_RUNNER_CANDIDATE_MANIFEST.md`
- `CMAME_CLOSED_LOOP_LOCAL_RUNNER_CANDIDATE_MANIFEST.json`
- `validate_cmame_closed_loop_local_runner_candidate.py`
- `cmame_closed_loop_local_runner_candidate/`

## Accepted Claim

The accepted paper claim is:

- `Gauss6/FullVA` is the production integrator.
- Compatibility marker for the bounded subcheck: submit under the narrowed claim,
  not under the global source-policy submission standard.
- The method-order claim is conditional order `6` under the retained theorem
  interfaces; validator marker: method-order claim is `6`.
- The smooth cylindrical-chain observed position/velocity orders are
  `7.161/7.066`.
- The comparator is the local paper-style `m=3` Gauss-Lobatto TFE formula
  target with expected order `5`.
- The four accepted local method ASME-style examples are `single_pendulum`,
  `double_pendulum`, `four_link`, and `slider_crank`.

This is a bounded formal-order comparison within the current artifact scope.
Disposition line: bounded narrowed-claim subcheck satisfied; the top-level
global decision remains `do_not_submit_global`, and the full source-policy
package remains not ready.
The narrowed-readiness markers may be copied into author-facing notes only as
the narrowed Gauss6/FullVA method/proof/common-reference decision; they must
not be copied into a global submission decision, external-superiority claim, or
source-policy package claim unless immediately qualified under the still-active
`do_not_submit_global` decision.
`ORDER_ACCEPTANCE_GATE.md` is the short order boundary: `single_pendulum` and
`double_pendulum` have accepted dynamic order rows, while `four_link` and
`slider_crank` now have local true-dynamic coarse-order candidates and remain
coverage-only for external dynamic-order superiority until the public same-test
baseline claim is closed.

`IMPLEMENTATION_PATH_AUDIT.md/json` now records
`implementation_path_check_for_132_row_residual=true`: the accepted code path is
`residual_cylindrical_chain -> R_VALUE/R_JAC -> gauss_step ->
integrate/run_case -> summary_v047.json`. This is a read-only static source
audit; it does not invoke `run_v047.py`, any v048 runner, or a default `1e-4`
campaign, and it does not prove the symbolic `O(h^7)` residual-defect
condition.

`CMAME_CLAIM_HYGIENE_AUDIT.md` and `CMAME_CLAIM_HYGIENE_AUDIT.json` now
check that the CMAME-facing files keep this as a conditional formal-order
comparison and do not drift into source-policy superiority, external
superiority, complete source-paper residual reproduction, or a seventh-order
theorem. The corresponding validator is
`validate_cmame_claim_hygiene_audit.py`.

## Proof Route Standard

Read the theorem as a direct residual-bridge/Kantorovich proof for the
implemented 132-row FullVA residual, not as a primitive 162-subterm Taylor
proof. The active stage-residual input is:

- 96 non-dynamic FullVA rows supplied by the row-local implementation
  certificate;
- 36 Newton--Euler rows supplied by the D5 direct-substitution zero-residual
  certificate on the lifted Gauss stage;
- the resulting 132-row residual bridge consumed by the stage-root,
  endpoint-closure, inexact-Newton, and local-to-global lemmas.

The separate primitive/Taylor route remains an appendix-level conditional
certificate schema:
`D5_CONDITIONAL_TAYLOR_CERTIFICATE.md` records `162/162` conditional reduction
templates but `0/162` actual primitive-route Taylor bounds, so it is not the
PC2 route used by the theorem. P6 remains a theorem-level solver-scale
condition, and P7 residual-to-error promotion remains open for mechanism-only
or source-policy rows.

The safe proof claim is therefore: conditional order-six theorem under the
retained P1/P2/P3 interfaces, the retained P4 binding convention with its
proved 96-row non-dynamic certificate, the retained P6 solver-scale
condition, and P5 supplied by the direct Newton--Euler route. This proof route
does not close source-policy readiness, full-TFE replacement, primitive
subterm bounds, or residual-to-error promotion.

## Do Not Claim

Do not claim:

- complete source-paper residual reproduction;
- accepted independent full-TFE stage replacement;
- sparse AD is already faster than dense `jacfwd`;
- the practical coarse sharp-friction regime is solved.

The current machine-readable boundary remains:

- `full_tfe_stage_replacement=false`
- remaining caveats:
  `sparse_speed_quantified`,
  `full_tfe_stage_replacement_missing`,
  `sharp_friction_coarse_order_reduction_ultra_recovered`

For the original-paper comparison, use `SOURCE_PAPER_COMPARISON.md`: the local
source-paper-style `m=3` Gauss-Lobatto TFE target has expected order `5`, while
the accepted `Gauss6/FullVA` method-order claim is conditional order `6` under
the retained theorem interfaces.

For the external same-test benchmark gate, use
`CROSS_PAPER_BENCHMARK_SPEC.md` and
`CROSS_PAPER_BENCHMARK_CASES.json`: the benchmark definitions and row-level
run inventory have been extracted from the original TFE paper and the
Kissel/Negrut-related public code, but the Gauss6/FullVA same-test campaign has
not yet been run beyond bounded v048 pilots: one 2021 single-pendulum
sixth-order pilot, one exact public-horizon single-pendulum step-size trio at `T=3`,
`h=[1e-2,1e-3,1e-4]` (`3/3` public h rows; roundoff-limited final-error orders), and selected 2021 four-link/slider-crank
closed-loop residual rows plus a 12/12 selected same-window public-`rA` versus local
`Gauss6/FullVA` comparison table, with derived order/work and work/precision
summary CSVs for paper tables. These selected rows are not the exact public
dynamic campaign. The later
Kissel/Bakke/Negrut velocity-partitioning paper is tracked as a
code-path-resolution gate, not completed evidence.
`EXTERNAL_SAME_TEST_RUN_QUEUE.md/json` compresses those 17 required cases
into four execution batches: two coarse-first parallel-ready batches with
20 non-default-`1e-4` shards, one source-pendulum encoding batch, and one
unresolved velocity-partitioning code-path batch.
`EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.md/json` fixes the B2/B4 acceptance
columns and records `accepted_external_dynamic_order_examples=0`; B2/B4 remain
open, and default `1e-4` is not required.
Use `KISSEL_NEGRUT_CODE_INVENTORY.md` to keep the 2021 `rA/rp/reps`, 2022
half-implicit, 2023/2024 velocity-partitioning, and 2024
performance-comparison sources as separate baselines.

For the submission-quality blocker ledger, use
`CMAME_BLOCKER_CLOSURE_GATE.md` and `CMAME_BLOCKER_CLOSURE_GATE.json`. This
gate records B5 as closed by `CMAME_VISUAL_LEGIBILITY_AUDIT.md` /
`CMAME_VISUAL_LEGIBILITY_AUDIT.json`, records B8 as closed by
`CMAME_RELATED_WORK_AUDIT.md` / `CMAME_RELATED_WORK_AUDIT.json`, and records
B1--B8 as closed for the narrowed current submission scope. B4 and B7 are
closed only by excluding source-policy work/precision and external-superiority
claims from the current paper; full source-policy package readiness remains
false. The gate records `bounded_narrowed_subcheck_satisfied=True`; the legacy
compatibility alias `submission_ready_under_narrowed_claim=True` is not a
global readiness marker. It also records
`full_source_policy_submission_ready=False`, while enforcing the
`coarse_first_no_default_1e-4` policy so strict public `1e-4` rows remain
opt-in rather than default.

For the B6 prose-residue boundary, use `CMAME_PROSE_RESIDUE_AUDIT.md` and
`CMAME_PROSE_RESIDUE_AUDIT.json`. This read-only audit checks both
`main_cmame.tex` and `cmame_submission_flat/main_cmame_submission.tex`, records
`main_body_machine_token_count=0`, confines artifact macros to the
reproducibility appendix with `appendix_artifact_macro_count=0`, and keeps
`default_1e-4_required=false` and `run_v047_invoked=false`.

For local submission integrity, use `CMAME_SUBMISSION_INTEGRITY_AUDIT.md` and
`CMAME_SUBMISSION_INTEGRITY_AUDIT.json`. This read-only audit checks the main
and flat TeX citation keys against the bibliography, the compiled PDF reference
heading, and the declarations/highlights/cover-letter sidecars. It currently
records local citation integrity passed and
`external_reference_web_verification_complete=True`. This supports the
narrowed-claim submission package; it does not make the full source-policy
reproducibility package ready.

For the all-method numerical review gate, use
`PAPER_NUMERICAL_RESULT_MATRIX.md/json/csv`,
`RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.md/json`, and
`ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.md/json` plus
`ALL_EXAMPLES_RESULT_SANITY_AUDIT.md/json`. The numerical matrix records
`44/44` method/example cells from `132` raw rows across all four examples and
all `11` methods. The sanity audit locks the exact `15` flagged nonlocal rows
across `single_pendulum`, `double_pendulum`, `four_link`, and `slider_crank`;
all flagged rows are quarantined from external-superiority claims until
source-policy reproduction is closed.
The result-to-manuscript traceability audit records `44/44` manuscript/PDF
velocity cells in the main and flat CMAME files, while keeping source-policy
reproduction and external-superiority claims false.
The all-method claim-disposition audit records `40/40` nonlocal method/example
rows, `40/40` local velocity-order wins, `40/40` local finest-velocity-error
wins, and `0/40` source-policy-closed nonlocal rows; this prevents the `15`
flagged anomaly/recheck rows from being misread as the full open source-policy
set.
`SOURCE_POLICY_ROW_CLOSURE_LEDGER.md/json` is the row-level closure ledger for
those same 15 rows; it records `0/15` source-policy-closed rows and `0/15`
external-superiority-ready rows, with counts checked across all four examples.
`EXTERNAL_CASE_EVIDENCE_RECONCILIATION.md/json` reconciles the case inventory
with current v048 outputs: RA2021 and HI2022 have bounded/coarse evidence,
while TFE2026 and VP2024 remain not-ready or demote suites.
`RA2021_SOURCE_IDENTITY_AUDIT.md/json` records the RA2021 source-code identity
audit: output mapping and time-grid convention are verified from source, but
local Gauss6/FullVA promotion under the same source policy is still open.
`HI2022_T8_TOLERANCE_REPAIR_AUDIT.md/json` records the T=8 tolerance-repair
attempts. The first relaxed-tolerance pass recovers one row; the second
non-heavy `1e-6` sweep on the failed T=8 models still leaves the combined best
at 19/24 rows and 4/8 complete groups. Source-policy reproduction and
external-superiority claims remain false.
`B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.md/json` records existing ready-command
artifact state, not verified current authorized execution: all 13 ready-command
outputs are present and cover 20/40 external rows, but post-execution promotion
closes 0/40 source-policy rows.
`B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.md/json/csv` maps all 40
external method/example cells after that driver: 20 rows have launch-command
references, 20 remain without launch commands, and none is external-superiority
ready. The handoff/audit boundary files are
`B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.md/json`, which records the exact
execution guard and command-to-row traceability for the 13 ready commands, 20
unique RA/HI rows, and 32 traced row references without authorizing execution,
and `FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.md/json`, which keeps OC4 at
`oc4_blocker_id=OC4`, `oc4_blocker_status=open`,
`oc4_closure_decision=remain_open_ready_for_authorized_execution_not_executed_not_promoted`,
and `oc4_closure_allowed_now=False` with `ready_commands_mapped_rows=13/20` and
`traceability_unique_traced_declared_mismatch=20/32/32/0`,
and `FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.md/json`, which records the
full-runner archive gap and keeps OC4/OC6/OC12 open under the current
non-execution boundary. Its OC12 aliases keep the closure decision at
`remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready`,
record `current_archive_usable_as_full_source_policy_runner_archive=False`,
limit `safe_current_use` to `narrowed_claim_replay_and_audit_provenance_only`,
keep `primary_submission_package_allowed=False`, and retain dependency blockers
`OC4,OC6`.
`OC6_SOURCE_EQUIVALENT_REOPEN_READINESS_AUDIT.md/json` keeps OC6 at
`oc6_blocker_id=OC6`, `oc6_blocker_status=partial`,
`oc6_closure_decision=remain_open_no_positive_source_equivalent_artifact`, and
`oc6_closure_allowed_now=False`; its reopen condition is suite-specific
(`reopen_condition=suite_specific_source_equivalent_reopen_conditions`), and
the latest external probe boundary remains `latest_external_probe_boundary=0/0/4/False/False`.
The two immediate root-cause sidecars are
`RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.md/json`, where the double
candidate remains low-order/floor-limited and not promotable, and
`HI2022_RA_HALF_DOUBLE_SOURCE_POLICY_FAILURE_DIAGNOSIS.md/json`, where the
rA_half double-pendulum shard completes only 1/3 rows because two rows fail
Newton convergence.
`TFE_ENDPOINT_POLICY_SENSITIVITY_AUDIT.md/json/csv` is a diagnostic-only
endpoint convention sensitivity check for the active original-TFE B2 candidate
rows. It records `16` summary rows and `48` raw rows, but closes zero
source-policy rows and does not allow an external-superiority claim.
`TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.md/json/csv` is the strict endpoint
boundary certificate for the fixed-step Algorithm-1 convention
`N=ceil(T/h)`. It proves the literal terminal overrun bound only: exact rows
hit `T`, non-integral rows terminate in `(T,T+h)`, and zero source-policy rows
are closed by this certificate.
`TFE_FULL_T10_COARSE_CANDIDATE_SUMMARY.md/json/csv` summarizes the existing
non-heavy full-horizon candidate probe in a diagnostic paper-facing table: at `T=10`,
`h=[0.1,0.05,0.025]`, and coarse `h_ref=0.0125`, all four active original-TFE
candidate methods are finite and residual-ok, while source-policy rows remain
`0` because the extracted `h_ref=1e-4` reference and source-equivalent method
runners are still not invoked.
`VP2024_CODE_PATH_DISPOSITION_AUDIT.md/json` is the explicit four-example
VP2024 code-path gate: it records `4/4` VP2024 source-policy rows unresolved,
`4/4` VP2024 common-reference proxy order/error wins, and `1/4` VP2024
larger-step diagnostic local error wins. That larger-step diagnostic is
noncontrolling and must not be promoted into a source-policy superiority claim.

For the external comparison boundary, use `CMAME_EXTERNAL_BASELINE_GATE.md`
and `CMAME_EXTERNAL_BASELINE_GATE.json`. This gate records
`same_test_campaign_status=not_run`, `external_superiority_claim=false`, and
`default_1e-4_required=false`: only `single_pendulum` and `double_pendulum`
currently have coarse-first order/time evidence, while `four_link` and
`slider_crank` have local true-dynamic coarse-order rows and strict
common-reference public work/precision evidence. Those rows do not yet close
external superiority or the full public same-test campaign.
The paired `EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.md/json` records the exact
same-test row columns needed before external rows can be promoted: order,
runtime, work/precision, Newton iterations, constraint drift, reference policy,
and same-test setup identity.

For implementation fidelity beyond static source identity, use
`DYNAMIC_ROW_ORACLE_GATE.md` and `DYNAMIC_ROW_ORACLE_GATE.json`. This runtime
oracle imports `run_v047.py`, evaluates `residual_cylindrical_chain` and
`R_JAC`, checks the accepted 132-row partition, and cross-checks the weighted
block-functional row families. It supports the accepted direct-route
implementation traceability boundary; the primitive symbolic row-oracle route
remains diagnostic and separate from the active direct proof closure.

For partial proof progress on the non-dynamic rows, use
`KINEMATIC_ROW_DEFECT_CERTIFICATE.md` and
`KINEMATIC_ROW_DEFECT_CERTIFICATE.json`. This certificate covers the 96
collocation/lower-pair rows on the smooth accepted FullVA lift. In the
primitive certificate route it leaves the 36 `newton_euler_weak_balance` rows
open; the accepted direct residual-bridge/Kantorovich route is recorded separately in
`PROOF_CLOSURE_MANIFEST.md/json` and
`NEWTON_EULER_DYNAMIC_ROW_CLOSURE_CONTRACT.md/json`.

For the separate primitive/symbolic dynamic-row ledger, use
`NEWTON_EULER_DEFECT_OBLIGATION_GATE.md` and
`NEWTON_EULER_DEFECT_OBLIGATION_GATE.json`. This gate decomposes the 36
`newton_euler_weak_balance` rows into one open D5 symbolic proof obligation
plus five closed D1/D2/D3/D4/D6 sub-obligations. It is a proof-work
ledger for the non-active symbolic route, not the active direct-route dynamic
defect certificate.

`NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.md` and
`NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.json` instantiate the primitive
symbolic certificate slots and deliberately remain open:
`certificate_complete=false`, `certified_row_count=0`, and
`open_row_count=36`. They are not the active proof-closure artifact.
`NEWTON_EULER_DYNAMIC_ROW_CLOSURE_CONTRACT.md/json` records the direct-route
row-level closure contract for the same 36 dynamic rows: all 36 rows have full
runtime traceability and supply the direct-PC2 theorem input. This row-level
contract does not close the primitive/Taylor route, P6 solver-policy evidence,
P7 residual-to-error promotion, source-policy readiness, or full-TFE
replacement.

For the conditional theorem boundary, use `CMAME_PROOF_CONTRACT_GATE.md` and
`CMAME_PROOF_CONTRACT_GATE.json`. This gate records that `eta_h^tube <= c_eta h^7` is a
theorem condition, fixed-tolerance runs are finite-run evidence, the dynamic
symbolic oracle is open, and the residual-to-error route is not accepted.
`PROOF_NUMERICAL_SCALE_AUDIT.md/json` records the existing smooth h-sweep
scale evidence without promoting it into an asymptotic solver proof.
`PROOF_SOLVER_SCALE_AUDIT.md/json` records the existing summary-level solver
residuals and explicitly keeps `theorem_level_scaled_tolerance_sweep_recorded=false` and
`eta_h_O_h7_solver_policy_evidence=false`; it is finite-run evidence, not a
new numerical campaign.
`PROOF_SOLVER_SCALED_TOLERANCE_PROBE.md/json/csv` records a finite one-step
smooth `eta_h=c_eta h^7` probe with `4/4` ok rows and max final residual over
`h^7` equal to `127.58372278641149`; this remains proof-support evidence, not
a theorem-level scaled trajectory sweep.
`PROOF_SOLVER_SCALED_TOLERANCE_TRAJECTORY_PROBE.md/json/csv` records a finite
short-trajectory `eta_h=c_eta h^7` probe with `4/4` ok rows, `30` checked
steps, and max final residual over `h^7` equal to `210.89078604575462`; this
also remains proof-support evidence, not a theorem-level scaled trajectory
sweep.
`PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.md/json/csv` records a finite
short-trajectory solver-policy comparison among fixed `1e-10`, `c h^7`, and
`c h^8` tolerances. It records
`finite_tolerance_regime_sweep_recorded=true`, `12` policy rows, and `90`
checked steps, while keeping theorem-level solver proof closure false.
`PROOF_CLAIM_TRACEABILITY_AUDIT.md/json` checks that both CMAME TeX sources
carry the proof labels and claim-boundary tokens, records `1/7` theorem
assumptions satisfied, `5/7` retained theorem interfaces, `1/7` open P7
nonpromotion boundary, and `4/0` close requirements/unsatisfied close
requirements,
`96` certified non-dynamic rows, `36/0` active direct Newton--Euler
closed/open rows, `36` symbolic/primitive-route Newton--Euler rows not certified
by that route, six Newton--Euler obligations, seven residual-to-error blockers,
`proof_submission_ready=false`, and `full_source_policy_submission_ready=false`.

## Review Agent Gate

Run the read-only review agent before treating any paper/package status as
current. The review agent is required to consume the all-method numerical matrix,
the all-example sanity audit, the source-policy audits, the proof closure
manifest, and the proof-claim traceability audit.

Current required review markers:

- `submission_standard_met=false`
- `submission_standard_scope=global_submission_standard`
- `review_scope=global_submission_standard_review`
- `top_level_review_decision_scope=global`
- `decision=do_not_submit_global`
- `open_blockers=OC4,OC6,OC12`
- `bounded_subcheck_satisfied_not_global_submit=true`
- narrowed claim marker: `narrowed_claim_submission_standard_met=true`
- narrowed claim marker: `narrowed_claim_decision=submit_under_narrowed_claim`
- legacy compatibility alias: `narrowed_claim_submission_standard_met=true`
- legacy compatibility alias: `narrowed_claim_decision=submit_under_narrowed_claim`
- `narrowed_claim_role=subsidiary_bounded_subcheck_not_top_level_review_verdict`
- `full_source_policy_package_ready=false`
- numerical matrix `44/44` cells from `132` raw rows
- all-example sanity audit `15` flagged nonlocal rows
- proof traceability row split: `96` certified non-dynamic rows, `36/0`
  active direct Newton--Euler closed/open rows, and `36` symbolic/primitive-route
  Newton--Euler rows not certified by that route
- proof-style equation hygiene: main/flat display labels referenced `283/283`,
  active theorem/proof display labels referenced `28/28`, and no unreferenced
  display labels remain.
- proof traceability partition satisfied/total/retained-interfaces/open-nonpromotion and requirements/unsatisfied `1/7/5/1` and `4/0`

## Validation Commands

Run these checks from `paper_v047_cylindrical_chain/`:

```bash
../.venv_sbel/bin/python validate_cmame_submission.py
../.venv_sbel/bin/python validate_submission_artifact_manifest_boundary_sync.py
../.venv_sbel/bin/python validate_full_source_policy_row_provenance_audit.py
../.venv_sbel/bin/python validate_oc6_source_equivalent_reopen_readiness_audit_20260620.py
../.venv_sbel/bin/python validate_cmame_blocker_closure_gate.py
../.venv_sbel/bin/python validate_cmame_submission_integrity_audit.py
../.venv_sbel/bin/python validate_cmame_external_baseline_gate.py
../.venv_sbel/bin/python validate_cmame_proof_contract_gate.py
../.venv_sbel/bin/python validate_cmame_visual_legibility_audit.py
../.venv_sbel/bin/python validate_cmame_related_work_audit.py
../.venv_sbel/bin/python validate_cmame_prose_residue_audit.py
../.venv_sbel/bin/python validate_dynamic_row_oracle_gate.py
../.venv_sbel/bin/python validate_concise_paper.py
../.venv_sbel/bin/python validate_proof_evidence_matrix.py
../.venv_sbel/bin/python validate_proof_numerical_scale_audit.py
../.venv_sbel/bin/python validate_proof_solver_scale_audit.py
../.venv_sbel/bin/python validate_proof_solver_scaled_tolerance_probe.py
../.venv_sbel/bin/python validate_proof_solver_scaled_tolerance_trajectory_probe.py
../.venv_sbel/bin/python validate_proof_solver_tolerance_regime_sweep.py
../.venv_sbel/bin/python validate_proof_claim_traceability_audit.py
../.venv_sbel/bin/python validate_order_acceptance_gate.py
../.venv_sbel/bin/python validate_implementation_fidelity_certificate.py
../.venv_sbel/bin/python validate_implementation_path_audit.py
../.venv_sbel/bin/python validate_newton_euler_dynamic_row_closure_contract.py
../.venv_sbel/bin/python validate_source_paper_comparison.py
../.venv_sbel/bin/python validate_cross_paper_benchmark_spec.py
../.venv_sbel/bin/python validate_cross_paper_benchmark_cases.py
../.venv_sbel/bin/python validate_external_same_test_run_queue.py
../.venv_sbel/bin/python validate_external_same_test_acceptance_sheet.py
../.venv_sbel/bin/python validate_all_examples_result_sanity_audit.py
../.venv_sbel/bin/python validate_paper_numerical_result_matrix.py
../.venv_sbel/bin/python validate_result_to_manuscript_traceability_audit.py
../.venv_sbel/bin/python validate_all_method_example_claim_disposition_audit.py
../.venv_sbel/bin/python validate_common_reference_order_recomputation_audit.py
../.venv_sbel/bin/python validate_external_baseline_source_policy_diagnosis.py
../.venv_sbel/bin/python validate_external_suite_disposition_audit.py
../.venv_sbel/bin/python validate_source_policy_closure_triage.py
../.venv_sbel/bin/python validate_source_policy_row_closure_ledger.py
../.venv_sbel/bin/python validate_source_policy_local_candidate_gap_audit.py
../.venv_sbel/bin/python validate_external_case_evidence_reconciliation.py
../.venv_sbel/bin/python validate_vp2024_code_path_disposition_audit.py
../.venv_sbel/bin/python validate_all_examples_source_policy_audit.py
../.venv_sbel/bin/python validate_external_source_policy_closure_manifest.py
../.venv_sbel/bin/python validate_tfe_source_policy_spec.py
../.venv_sbel/bin/python validate_comparison_objective_closure_reconciliation_audit.py
../.venv_sbel/bin/python cmame_submission_review_agent.py
../.venv_sbel/bin/python validate_cmame_review_agent.py
../.venv_sbel/bin/python validate_cmame_proof_style_audit.py
../.venv_sbel/bin/python validate_submission_bundle.py
../.venv_sbel/bin/python validate_paper_package.py
```

Run this broader repository check from the parent work directory:

```bash
.venv_sbel/bin/python validate_pipeline_outputs.py
```

These checks do not invoke the full `run_v047.py` generator.

## Build Commands

Build the CMAME/Elsevier manuscript:

```bash
cmd.exe /c latexmk -pdf -interaction=nonstopmode main_cmame.tex
```

Build the flat CMAME/Elsevier source copy:

```bash
cd cmame_submission_flat
cmd.exe /c latexmk -pdf -interaction=nonstopmode main_cmame_submission.tex
```

Build the concise supporting paper:

```bash
cmd.exe /c latexmk -pdf -interaction=nonstopmode main_concise.tex
```

Build the full audit paper:

```bash
cmd.exe /c latexmk -pdf -interaction=nonstopmode main.tex
```

## Evidence Anchors

The claim is anchored by:

- `CLAIM_BOUNDARY.json`
- `main_cmame.tex`
- `main_cmame.pdf`
- `highlights_cmame.txt`
- `declarations_cmame.md`
- `CMAME_SUBMISSION_CHECKLIST.md`
- `CMAME_SUBMISSION_READINESS_AUDIT.md`
- `CMAME_SUBMISSION_READINESS_REVIEW.md`
- `CMAME_BLOCKER_CLOSURE_GATE.md`
- `CMAME_BLOCKER_CLOSURE_GATE.json`
- `CMAME_EXTERNAL_BASELINE_GATE.md`
- `CMAME_EXTERNAL_BASELINE_GATE.json`
- `CMAME_PROOF_CONTRACT_GATE.md`
- `CMAME_PROOF_CONTRACT_GATE.json`
- `PROOF_NUMERICAL_SCALE_AUDIT.md`
- `PROOF_NUMERICAL_SCALE_AUDIT.json`
- `PROOF_SOLVER_SCALE_AUDIT.md`
- `PROOF_SOLVER_SCALE_AUDIT.json`
- `PROOF_SOLVER_SCALED_TOLERANCE_PROBE.md`
- `PROOF_SOLVER_SCALED_TOLERANCE_PROBE.json`
- `PROOF_SOLVER_SCALED_TOLERANCE_TRAJECTORY_PROBE.md`
- `PROOF_SOLVER_SCALED_TOLERANCE_TRAJECTORY_PROBE.json`
- `PROOF_SOLVER_SCALED_TOLERANCE_TRAJECTORY_PROBE.csv`
- `PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.md`
- `PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.json`
- `PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.csv`
- `CMAME_PROSE_RESIDUE_AUDIT.md`
- `CMAME_PROSE_RESIDUE_AUDIT.json`
- `DYNAMIC_ROW_ORACLE_GATE.md`
- `DYNAMIC_ROW_ORACLE_GATE.json`
- `NEWTON_EULER_DEFECT_OBLIGATION_GATE.md`
- `NEWTON_EULER_DEFECT_OBLIGATION_GATE.json`
- `NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.md`
- `NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.json`
- `NEWTON_EULER_DYNAMIC_ROW_CLOSURE_CONTRACT.md`
- `NEWTON_EULER_DYNAMIC_ROW_CLOSURE_CONTRACT.json`
- `README_CMAME_FLAT_SUBMISSION.md`
- `cmame_submission_flat/main_cmame_submission.tex`
- `cmame_submission_flat/main_cmame_submission.pdf`
- `cmame_submission_flat.zip`
- `SUBMISSION_ARTIFACT_MANIFEST.json`
- `SUBMISSION_FILE_INVENTORY.md`
- `COVER_LETTER.md`
- `REVIEW_RESPONSE_TEMPLATE.md`
- `PROOF_EVIDENCE_MATRIX.md`
- `ORDER_ACCEPTANCE_GATE.md`
- `ORDER_ACCEPTANCE_GATE.json`
- `IMPLEMENTATION_FIDELITY_CERTIFICATE.md`
- `IMPLEMENTATION_PATH_AUDIT.md`
- `IMPLEMENTATION_PATH_AUDIT.json`
- `SOURCE_PAPER_COMPARISON.md`
- `CROSS_PAPER_BENCHMARK_MATRIX.md`
- `CROSS_PAPER_BENCHMARK_SPEC.md`
- `CROSS_PAPER_BENCHMARK_CASES.json`
- `EXTERNAL_SAME_TEST_RUN_QUEUE.md`
- `EXTERNAL_SAME_TEST_RUN_QUEUE.json`
- `KISSEL_NEGRUT_CODE_INVENTORY.md`
- `PAPER_RESULT_PACK.md`
- `PAPER_RESULT_PACK.json`
- `PAPER_NUMERICAL_RESULT_MATRIX.md`
- `PAPER_NUMERICAL_RESULT_MATRIX.json`
- `PAPER_NUMERICAL_RESULT_MATRIX.csv`
- `RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.md`
- `RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.json`
- `ALL_EXAMPLES_RESULT_SANITY_AUDIT.md`
- `ALL_EXAMPLES_RESULT_SANITY_AUDIT.json`
- `COMMON_REFERENCE_ORDER_RECOMPUTATION_AUDIT.md`
- `COMMON_REFERENCE_ORDER_RECOMPUTATION_AUDIT.json`
- `EXTERNAL_BASELINE_SOURCE_POLICY_DIAGNOSIS.md`
- `EXTERNAL_BASELINE_SOURCE_POLICY_DIAGNOSIS.json`
- `EXTERNAL_SUITE_DISPOSITION_AUDIT.md`
- `EXTERNAL_SUITE_DISPOSITION_AUDIT.json`
- `RA2021_SOURCE_IDENTITY_AUDIT.md`
- `RA2021_SOURCE_IDENTITY_AUDIT.json`
- `HI2022_T8_TOLERANCE_REPAIR_AUDIT.md`
- `HI2022_T8_TOLERANCE_REPAIR_AUDIT.json`
- `B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.md`
- `B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.json`
- `RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.md`
- `RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.json`
- `HI2022_RA_HALF_DOUBLE_SOURCE_POLICY_FAILURE_DIAGNOSIS.md`
- `HI2022_RA_HALF_DOUBLE_SOURCE_POLICY_FAILURE_DIAGNOSIS.json`
- `B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.md`
- `B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.json`
- `B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.csv`
- `B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.md`
- `B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json`
- `FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.md`
- `FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json`
- `TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.md`
- `TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.json`
- `TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.csv`
- `TFE_ENDPOINT_POLICY_SENSITIVITY_AUDIT.md`
- `TFE_ENDPOINT_POLICY_SENSITIVITY_AUDIT.json`
- `TFE_ENDPOINT_POLICY_SENSITIVITY_AUDIT.csv`
- `COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.md`
- `COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.json`
- `CMAME_REVIEW_AGENT_REPORT.md`
- `CMAME_REVIEW_AGENT_REPORT.json`
- `CMAME_PROOF_STYLE_AUDIT.md`
- `CMAME_PROOF_STYLE_AUDIT.json`
- `PROOF_CLAIM_TRACEABILITY_AUDIT.md`
- `PROOF_CLAIM_TRACEABILITY_AUDIT.json`
- `CURRENT_PIPELINE_CONTRACT.md`
- `v047_cylindrical_chain_pipeline/results/summary_v047.json`
- `PAPER_CLAIM_LEDGER.md`
- `validate_cmame_submission.py`
- `validate_submission_artifact_manifest_boundary_sync.py`
- `validate_full_source_policy_row_provenance_audit.py`
- `validate_oc6_source_equivalent_reopen_readiness_audit_20260620.py`
- `validate_cmame_blocker_closure_gate.py`
- `validate_cmame_external_baseline_gate.py`
- `validate_cmame_proof_contract_gate.py`
- `validate_dynamic_row_oracle_gate.py`
- `validate_concise_paper.py`
- `validate_paper_claims.py`
- `validate_proof_evidence_matrix.py`
- `validate_proof_numerical_scale_audit.py`
- `validate_proof_claim_traceability_audit.py`
- `validate_d5_p_state_ps2_aggregate_promotion_audit.py`
- `validate_d5_p_state_ps3_actual_instantiation_gap_audit.py`
- `validate_d5_p_state_ps3_h_acc_input_obstruction_audit.py`
- `validate_order_acceptance_gate.py`
- `validate_implementation_fidelity_certificate.py`
- `validate_implementation_path_audit.py`
- `validate_source_paper_comparison.py`
- `validate_cross_paper_benchmark_spec.py`
- `validate_cross_paper_benchmark_cases.py`
- `validate_external_same_test_run_queue.py`
- `validate_all_examples_result_sanity_audit.py`
- `validate_paper_numerical_result_matrix.py`
- `validate_result_to_manuscript_traceability_audit.py`
- `validate_common_reference_order_recomputation_audit.py`
- `validate_external_baseline_source_policy_diagnosis.py`
- `validate_external_suite_disposition_audit.py`
- `validate_ra2021_source_identity_audit.py`
- `validate_hi2022_t8_tolerance_repair_audit.py`
- `validate_source_policy_closure_triage.py`
- `validate_source_policy_row_closure_ledger.py`
- `validate_source_policy_local_candidate_gap_audit.py`
- `validate_all_examples_source_policy_audit.py`
- `validate_external_source_policy_closure_manifest.py`
- `validate_tfe_source_policy_spec.py`
- `validate_tfe_endpoint_policy_sensitivity_audit.py`
- `validate_comparison_objective_closure_reconciliation_audit.py`
- `cmame_submission_review_agent.py`
- `validate_cmame_review_agent.py`
- `validate_cmame_proof_style_audit.py`
- `validate_submission_bundle.py`
- `validate_paper_package.py`
- `v048_cross_paper_same_test_benchmarks/validate_closed_loop_residual_to_error_theorem_obligations.py`
- `validate_pipeline_outputs.py`

If any of these files disagree, treat the paper package as not ready.
