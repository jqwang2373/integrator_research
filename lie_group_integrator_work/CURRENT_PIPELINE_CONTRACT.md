# Current Pipeline Contract

This file is the short current-state contract for the v047 work. It exists so
the human workflow, paper package, and read-only validators agree on the same
claim boundary before any long numerical run is started.

## Skill Role

The active workflow skill is `research-pipeline`. It is a process guard, not an
authoritative status ledger. Its static v047 status text can lag behind the
worktree; current files in this repository are authoritative.

The skill still matters because it enforces the research discipline:

- keep the objective broad until all gates are proven;
- inspect current artifacts before relying on memory;
- preserve proof/status, four-example evidence, convergence, plots, CSV/JSON
  outputs, and ledgers;
- do not mark the active goal complete while open gates remain.

## Authoritative Current Files

Use these files as the current source of truth:

- `paper_v047_cylindrical_chain/CLAIM_BOUNDARY.json`
- `paper_v047_cylindrical_chain/main_cmame.tex`
- `paper_v047_cylindrical_chain/main_cmame.pdf`
- `paper_v047_cylindrical_chain/CMAME_SUBMISSION_CHECKLIST.md`
- `paper_v047_cylindrical_chain/CMAME_SUBMISSION_READINESS_AUDIT.md`
- `paper_v047_cylindrical_chain/CMAME_SUBMISSION_READINESS_REVIEW.md`
- `paper_v047_cylindrical_chain/CMAME_BLOCKER_CLOSURE_GATE.md`
- `paper_v047_cylindrical_chain/CMAME_BLOCKER_CLOSURE_GATE.json`
- `paper_v047_cylindrical_chain/CMAME_EXTERNAL_BASELINE_GATE.md`
- `paper_v047_cylindrical_chain/CMAME_EXTERNAL_BASELINE_GATE.json`
- `paper_v047_cylindrical_chain/CMAME_PROOF_CONTRACT_GATE.md`
- `paper_v047_cylindrical_chain/CMAME_PROOF_CONTRACT_GATE.json`
- `paper_v047_cylindrical_chain/PROOF_CLAIM_TRACEABILITY_AUDIT.md`
- `paper_v047_cylindrical_chain/PROOF_CLAIM_TRACEABILITY_AUDIT.json`
- `paper_v047_cylindrical_chain/DYNAMIC_ROW_ORACLE_GATE.md`
- `paper_v047_cylindrical_chain/DYNAMIC_ROW_ORACLE_GATE.json`
- `paper_v047_cylindrical_chain/PAPER_NUMERICAL_RESULT_MATRIX.md`
- `paper_v047_cylindrical_chain/PAPER_NUMERICAL_RESULT_MATRIX.json`
- `paper_v047_cylindrical_chain/PAPER_NUMERICAL_RESULT_MATRIX.csv`
- `paper_v047_cylindrical_chain/ALL_EXAMPLES_RESULT_SANITY_AUDIT.md`
- `paper_v047_cylindrical_chain/ALL_EXAMPLES_RESULT_SANITY_AUDIT.json`
- `paper_v047_cylindrical_chain/CMAME_REVIEW_AGENT_REPORT.md`
- `paper_v047_cylindrical_chain/CMAME_REVIEW_AGENT_REPORT.json`
- `paper_v047_cylindrical_chain/FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.md`
- `paper_v047_cylindrical_chain/FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json`
- `paper_v047_cylindrical_chain/RA_HI_SOURCE_POLICY_OUTPUT_INVENTORY.md`
- `paper_v047_cylindrical_chain/RA_HI_SOURCE_POLICY_OUTPUT_INVENTORY.json`
- `paper_v047_cylindrical_chain/RA_HI_SOURCE_POLICY_CLOSEOUT_CHECKLIST.md`
- `paper_v047_cylindrical_chain/RA_HI_SOURCE_POLICY_CLOSEOUT_CHECKLIST.json`
- `paper_v047_cylindrical_chain/RA_HI_SOURCE_POLICY_PROMOTION_BLOCKER_MATRIX.md`
- `paper_v047_cylindrical_chain/RA_HI_SOURCE_POLICY_PROMOTION_BLOCKER_MATRIX.json`
- `paper_v047_cylindrical_chain/RA_HI_SOURCE_POLICY_POST_EXECUTION_ATTEMPT_CERTIFICATE.md`
- `paper_v047_cylindrical_chain/RA_HI_SOURCE_POLICY_POST_EXECUTION_ATTEMPT_CERTIFICATE.json`
- `paper_v047_cylindrical_chain/B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.md`
- `paper_v047_cylindrical_chain/B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json`
- `paper_v047_cylindrical_chain/B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.md`
- `paper_v047_cylindrical_chain/B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json`
- `paper_v047_cylindrical_chain/FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.md`
- `paper_v047_cylindrical_chain/FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.json`
- `paper_v047_cylindrical_chain/FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.csv`
- `paper_v047_cylindrical_chain/CROSS_PAPER_BENCHMARK_MATRIX.md`
- `paper_v047_cylindrical_chain/CROSS_PAPER_BENCHMARK_SPEC.md`
- `paper_v047_cylindrical_chain/CROSS_PAPER_BENCHMARK_CASES.json`
- `paper_v047_cylindrical_chain/KISSEL_NEGRUT_CODE_INVENTORY.md`
- `paper_v047_cylindrical_chain/ORDER_ACCEPTANCE_GATE.md`
- `paper_v047_cylindrical_chain/ORDER_ACCEPTANCE_GATE.json`
- `paper_v047_cylindrical_chain/IMPLEMENTATION_FIDELITY_CERTIFICATE.md`
- `paper_v047_cylindrical_chain/cmame_submission_flat/main_cmame_submission.tex`
- `paper_v047_cylindrical_chain/cmame_submission_flat/main_cmame_submission.pdf`
- `paper_v047_cylindrical_chain/cmame_submission_flat.zip`
- `pipeline_validation_results/pipeline_validation_summary.json`
- `v047_cylindrical_chain_pipeline/results/summary_v047.json`
- `docs/VALIDATION_QUICKSTART.md`
- `paper_v047_cylindrical_chain/CURRENT_STATUS_CN.md`
- `docs/PIPELINE_AUDIT.md`
- `docs/ORDER_PROOF_LEDGER.md`
- `docs/VERSION_LEDGER.md`
- `docs/VERSION_TREE.md`

## Accepted Claim

The accepted paper-facing claim is a conditional formal-order comparison and
sixth-order FullVA method claim, not a complete source-paper residual
reproduction claim and not an implemented source-paper superiority claim.

- Accepted method: `Gauss6/FullVA`.
- Accepted method order claim: `6`.
- Smooth observed position/velocity orders: `7.161/7.066`.
- Local paper-style comparator: `m=3` Gauss-Lobatto TFE target with expected
  order `5`.
- Accepted ASME examples: `single_pendulum`, `double_pendulum`, `four_link`,
  and `slider_crank`.
- Accepted dynamic order rows: `single_pendulum` and `double_pendulum`.
- Coverage-only for dynamic order: `four_link` and `slider_crank`, pending a
  true closed-loop dynamic trajectory/order row or a residual-to-error theorem.
- Current ASME status:
  `four_asme_method_rows_accepted_projection_sharp_sparse_caveats`.

This contract does not claim that the source paper's complete TFE residual has
been reimplemented.

## Paper Quality Status

The CMAME package is mechanically buildable but **not submission ready**.
The blocking review is recorded in
`paper_v047_cylindrical_chain/CMAME_SUBMISSION_READINESS_REVIEW.md`.
The machine-checkable closure ledger is
`paper_v047_cylindrical_chain/CMAME_BLOCKER_CLOSURE_GATE.md` /
`paper_v047_cylindrical_chain/CMAME_BLOCKER_CLOSURE_GATE.json`; it records
B1-B8 closed under the narrowed-claim policy, while keeping
`full_source_policy_submission_ready=false`, `source_policy_closed=0/40`, and
`default_1e-4_required=false`.
The visual-legibility audit is recorded in
`paper_v047_cylindrical_chain/CMAME_VISUAL_LEGIBILITY_AUDIT.md` /
`paper_v047_cylindrical_chain/CMAME_VISUAL_LEGIBILITY_AUDIT.json`.
The related-work audit is recorded in
`paper_v047_cylindrical_chain/CMAME_RELATED_WORK_AUDIT.md` /
`paper_v047_cylindrical_chain/CMAME_RELATED_WORK_AUDIT.json`.
The external-baseline gate is
`paper_v047_cylindrical_chain/CMAME_EXTERNAL_BASELINE_GATE.md` /
`paper_v047_cylindrical_chain/CMAME_EXTERNAL_BASELINE_GATE.json`; it records
`same_test_campaign_status=not_run`, `external_superiority_claim=false`,
`default_1e-4_required=false`, and keeps `four_link`/`slider_crank` as
surrogate-only for external dynamic order until true order/work rows or a
residual-to-error theorem closes the gap.
The implementation-fidelity runtime oracle is
`paper_v047_cylindrical_chain/DYNAMIC_ROW_ORACLE_GATE.md` /
`paper_v047_cylindrical_chain/DYNAMIC_ROW_ORACLE_GATE.json`; it checks the
accepted 132-row residual/Jacobian partition and the Gauss6-equivalent
weighted block-functional decomposition while keeping the independent symbolic
oracle open.
The proof-contract gate is
`paper_v047_cylindrical_chain/CMAME_PROOF_CONTRACT_GATE.md` /
`paper_v047_cylindrical_chain/CMAME_PROOF_CONTRACT_GATE.json`; it keeps the
current theorem explicitly conditional, records `eta_h^tube <= c_eta h^7` as a
theorem condition, and prevents fixed-tolerance runs or residual-to-error
surrogates from being promoted into an unconditional proof.
The proof-claim traceability audit is
`paper_v047_cylindrical_chain/PROOF_CLAIM_TRACEABILITY_AUDIT.md` /
`paper_v047_cylindrical_chain/PROOF_CLAIM_TRACEABILITY_AUDIT.json`; it checks
proof labels and boundary tokens in both CMAME TeX sources, records `4/4`
close requirements satisfied, `0` active direct Newton--Euler open
obligations, `1` symbolic/primitive-lane Newton--Euler open obligation, seven
residual-to-error blockers, and `submission_ready=false`.
The paper numerical review gate is
`paper_v047_cylindrical_chain/PAPER_NUMERICAL_RESULT_MATRIX.md/json/csv`
plus `paper_v047_cylindrical_chain/ALL_EXAMPLES_RESULT_SANITY_AUDIT.md/json`;
it verifies `44/44` method/example cells from `132` raw rows across all four
examples and locks the exact `15` flagged nonlocal rows out of any
external-superiority claim.
The deterministic review agent is
`paper_v047_cylindrical_chain/cmame_submission_review_agent.py` with report
`paper_v047_cylindrical_chain/CMAME_REVIEW_AGENT_REPORT.md/json`; it must keep
top-level `submission_standard_met=false` and `decision=do_not_submit_global`
while recording the narrowed claim only as a subsidiary subcheck with
`narrowed_claim_subcheck_disposition=bounded_subcheck_satisfied_not_global_submit`.
The report must expose machine-readable aliases `open_blocker_ids=OC4,OC6,OC12`
and `evidence_summary.source_policy_apples_to_apples_external=0/40` so callers
do not confuse the narrowed subcheck with global submission readiness.
The global/full-source-policy package remains not submission ready until
source-policy and reproducibility gates close.
The objective completion audit is the central blocker boundary:
`paper_v047_cylindrical_chain/OBJECTIVE_COMPLETION_AUDIT.md` /
`paper_v047_cylindrical_chain/OBJECTIVE_COMPLETION_AUDIT.json`. It must keep
`blocker_open_by_id=OC4:True,OC6:True,OC12:True`,
`blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready`,
and `blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False`; these
aliases are the contract-level guard against treating validator PASS or the
narrowed archive as global submission readiness.
The runner-centered reproducibility and package manifests must expose direct
top-level package-boundary summaries:
`source_policy_closed_ratio=0/40`,
`source_policy_execution_handoff_status=source_policy_execution_handoff_ready_not_authorized_not_run`,
`source_policy_execution_handoff_authorized=False`,
`source_policy_execution_handoff_commands_not_run=True`,
`minimal_package_ready=False`, and `tfe_runner=False`.
The full source-policy runner archive gate is
`paper_v047_cylindrical_chain/FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.md` /
`paper_v047_cylindrical_chain/FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json`;
it is checked by `validate_full_source_policy_runner_archive_gap_audit.py` and
keeps top-level `full_archive_ready_now=False`, `source_policy_closed=False`,
`source_policy_closed_ratio=0/40`, `opt_in_required_command_count=13`,
`opt_in_required_mapped_external_rows=20`,
`driver_does_not_authorize_execution=True`, and `submission_ready=False` while
source-policy rows remain `0/40`.
The current narrowed archive boundary matches the reproducibility manifest:
`True`. Its exact boundary tuple is
`narrowed_archive_ready_not_full_source_policy_runner_archive/0/40/False/False/True`;
blocking ids/status are `OC4,OC6,OC12` /
`OC4=open,OC6=partial,OC12=partial`; current archive use is
`narrowed_claim_only`, not a full source-policy runner archive. OC12 therefore
remains a global blocker even though the narrowed replay/provenance archive is
usable for the bounded claim.
The TFE source-policy self-reproduction attempt certificate is
`paper_v047_cylindrical_chain/TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.md` /
`paper_v047_cylindrical_chain/TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.json`;
it is checked by `validate_tfe_source_policy_self_reproduction_attempt_certificate.py`
and keeps TFE attempted-not-reproducible rows remain `16/16` with
`attempted_not_reproducible_rows=16/16`, top-level
`source_policy_closed=False`, `source_policy_closed_ratio=0/16`,
`source_policy_closed_rows=0`, and `submission_ready=False`. It also exposes
top-level public-code/preflight aliases:
`public_code_recheck_status=public_code_rechecked_no_distinct_tfe_code_artifact_attempted_not_reproducible`,
`reopen_condition=new_public_or_source_code_equivalent_tfe_implementation_artifact`,
`source_policy_execution_preflight_status=terminal_no_public_code_self_reproduction_attempted_not_promoted`,
and `public_code_refresh_latest_positive_artifact_rows=0`.
`paper_v047_cylindrical_chain/OBJECTIVE_COMPLETION_AUDIT.json` must carry these
same OC6 terminal aliases directly: its OC6 evidence list includes
`TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.json` and
`SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.json`, with
`oc6_tfe_self_reproduction=attempted_not_reproducible_not_promoted/0/16`,
`oc6_public_code_recheck_status=public_code_rechecked_no_distinct_tfe_code_artifact_attempted_not_reproducible`,
and `oc6_public_code_refresh=20/11/0/0/20`.
The RA/HI source-policy closeout gate is
`paper_v047_cylindrical_chain/RA_HI_SOURCE_POLICY_OUTPUT_INVENTORY.md` plus
`paper_v047_cylindrical_chain/RA_HI_SOURCE_POLICY_CLOSEOUT_CHECKLIST.md` /
`paper_v047_cylindrical_chain/RA_HI_SOURCE_POLICY_PROMOTION_BLOCKER_MATRIX.md`
plus
`paper_v047_cylindrical_chain/RA_HI_SOURCE_POLICY_POST_EXECUTION_ATTEMPT_CERTIFICATE.md`;
it is checked by `validate_ra_hi_source_policy_output_inventory.py`,
`validate_ra_hi_source_policy_closeout_checklist.py`, and
`validate_ra_hi_source_policy_promotion_blocker_matrix.py`, with the
post-execution certificate checked by
`validate_ra_hi_source_policy_post_execution_attempt_certificate.py`. It keeps
the RA/HI output inventory at `commands=13`, `outputs=13/13`, and
`source_policy_closed=0`, keeps RA/HI source-policy rows remain `0/20` with
`source_policy_closed=0/20`, keeps RA/HI not-promoted rows remain `20/20` with
`not_promoted=20`, and keeps `source_policy_rows_promoted=0`,
`external_superiority_ready_rows=0`, `source_policy_closed=0/40`,
`run_v047_invoked=False`, and `submission_ready=False` until exact B4 opt-in
authorized closeout or a new promotion artifact. The B4 execution
boundary is recorded in
`paper_v047_cylindrical_chain/B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.md` /
`paper_v047_cylindrical_chain/B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json`
and checked by `validate_b4_source_policy_execution_opt_in_packet.py`; it keeps
`ready_command_mapped_external_rows=20/40`, `source_policy_closed_now=0/40`,
and `execution_invoked_by_packet=False` unless the exact recorded approval
string is supplied and the guarded driver is run.
The guarded driver is
`paper_v047_cylindrical_chain/run_b4_source_policy_after_opt_in.sh`; its
static contract is checked by `validate_b4_source_policy_guarded_driver.py`,
which verifies the exact approval guard, the 13-command RA/HI command list, the
match to the opt-in packet, `run_v047_invoked=False`, and
`execution_invoked_by_validator=False` without executing any B4 command.
The B4 source-policy execution handoff is
`paper_v047_cylindrical_chain/B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.md` /
`paper_v047_cylindrical_chain/B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json`
and checked by `validate_b4_source_policy_execution_handoff_package.py`; it
keeps `source_policy_closed=0/40`, `terminal_unable_to_reproduce_rows=20`,
`ready_command_count=13`, top-level `opt_in_required_command_count=13`,
`opt_in_required_mapped_external_rows=20`, `execution_authorized=False`,
top-level
`guarded_execution_driver=run_b4_source_policy_after_opt_in.sh`,
`driver_requires_exact_approval=True`, and `submission_ready=False`. The full row-level
source-policy provenance audit is
`paper_v047_cylindrical_chain/FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.md/json/csv`
and checked by `validate_full_source_policy_row_provenance_audit.py`; it keeps
`rows=40`, `provenance_preflight=40/40`, `source_policy_closed=0/40`, and
`promotion_ready_rows=0`. `OBJECTIVE_COMPLETION_AUDIT.json` must carry this
same OC4 row-provenance boundary directly with `oc4_evidence_files=5`,
`oc4_row_provenance=40/40/0/40/0`, and
`oc4_provenance_handoff=source_policy_execution_handoff_ready_not_authorized_not_run/False/True`.

- `submission_ready=false`
- `mechanical_preflight_passed=true`
- `quality_review_passed=false`

Do not describe the paper as submission ready until an ARS-style
submission-readiness review has no blocking findings.

## Open Caveats

The current open caveats are:

- `sparse_speed_quantified`: sparse structure is correct and quantified, but
  dense `jacfwd` is still faster in the recorded wall-clock evidence.
- `full_tfe_stage_replacement_missing`: independent full TFE stage replacement
  is not accepted; `full_tfe_stage_replacement=false`.
- `sharp_friction_coarse_order_reduction_ultra_recovered`: sharp coarse-regime
  order is reduced, while ultra refinement recovers high order at quantified
  practical cost.

## Command Boundary

Use read-only checks for routine paper, claim, and four-example validation:

```bash
.venv_sbel/bin/python validate_pipeline_outputs.py
```

```bash
cd paper_v047_cylindrical_chain
../.venv_sbel/bin/python validate_cmame_submission.py
../.venv_sbel/bin/python validate_cmame_blocker_closure_gate.py
../.venv_sbel/bin/python validate_cmame_external_baseline_gate.py
../.venv_sbel/bin/python validate_cmame_proof_contract_gate.py
../.venv_sbel/bin/python validate_cmame_visual_legibility_audit.py
../.venv_sbel/bin/python validate_cmame_related_work_audit.py
../.venv_sbel/bin/python validate_dynamic_row_oracle_gate.py
../.venv_sbel/bin/python validate_paper_numerical_result_matrix.py
../.venv_sbel/bin/python validate_all_examples_result_sanity_audit.py
../.venv_sbel/bin/python validate_proof_claim_traceability_audit.py
../.venv_sbel/bin/python cmame_submission_review_agent.py
../.venv_sbel/bin/python validate_cmame_review_agent.py
../.venv_sbel/bin/python validate_full_source_policy_runner_archive_gap_audit.py
../.venv_sbel/bin/python validate_tfe_source_policy_self_reproduction_attempt_certificate.py
../.venv_sbel/bin/python validate_ra_hi_source_policy_output_inventory.py
../.venv_sbel/bin/python validate_ra_hi_source_policy_closeout_checklist.py
../.venv_sbel/bin/python validate_ra_hi_source_policy_promotion_blocker_matrix.py
../.venv_sbel/bin/python validate_ra_hi_source_policy_post_execution_attempt_certificate.py
../.venv_sbel/bin/python validate_b4_source_policy_execution_opt_in_packet.py
../.venv_sbel/bin/python validate_b4_source_policy_guarded_driver.py
../.venv_sbel/bin/python validate_b4_source_policy_execution_handoff_package.py
../.venv_sbel/bin/python validate_full_source_policy_row_provenance_audit.py
../.venv_sbel/bin/python validate_proof_evidence_matrix.py
../.venv_sbel/bin/python validate_order_acceptance_gate.py
../.venv_sbel/bin/python validate_implementation_fidelity_certificate.py
../.venv_sbel/bin/python validate_source_paper_comparison.py
../.venv_sbel/bin/python validate_cross_paper_benchmark_spec.py
../.venv_sbel/bin/python validate_cross_paper_benchmark_cases.py
../.venv_sbel/bin/python validate_submission_bundle.py
../.venv_sbel/bin/python validate_paper_package.py
```

```bash
cd v047_cylindrical_chain_pipeline
../.venv_sbel/bin/python validate_four_asme_minimal.py
../.venv_sbel/bin/python validate_full_tfe_gap.py
../.venv_sbel/bin/python validate_full_tfe_repair_spec.py
../.venv_sbel/bin/python validate_v047_outputs.py
```

Do not run `v047_cylindrical_chain_pipeline/run_v047.py` to answer whether the
paper claim or four ASME examples currently pass. That script is the full
historical audit and artifact generator; use it only after changing numerical
method code or an artifact-producing audit.

## Next Real Research Gate

The next paper gate is the same-test external benchmark campaign recorded in
`paper_v047_cylindrical_chain/CROSS_PAPER_BENCHMARK_MATRIX.md` and specified
in `paper_v047_cylindrical_chain/CROSS_PAPER_BENCHMARK_SPEC.md`, with
row-level cases in `paper_v047_cylindrical_chain/CROSS_PAPER_BENCHMARK_CASES.json`:
rerun the original Chaturvedi--Sandu--Sandu pendulum tests and the
Kissel/Negrut public-code mechanism suites with identical parameters, drivers,
reference policies, error metrics, and work metrics. The multi-paper
Kissel/Negrut code inventory is recorded in
`paper_v047_cylindrical_chain/KISSEL_NEGRUT_CODE_INVENTORY.md`: the 2021
`rA/rp/reps`, 2022 half-implicit, 2023/2024 velocity-partitioning, and 2024
performance-comparison sources must stay separate. The 2021 public-code order
baseline is now complete, but the accepted `Gauss6/FullVA` method has not yet
been run across that full external suite. v048 also now has bounded
same-mechanism evidence for `Gauss6/FullVA`: one sixth-order 2021
single-pendulum pilot, one exact public-horizon single-pendulum step-size trio at
`T=3`, `h=[1e-2,1e-3,1e-4]` (`3/3` public h rows; roundoff-limited final-error orders), and 6/6
selected closed-loop residual rows on the 2021
`four_link` and `slider_crank` mechanisms. It now also has the public-horizon
closed-loop residual tranche for those two mechanisms at `T=3`,
`h=[1e-2,1e-3,1e-4]` (`6/6` public h rows), with finest-row max dynamics
residuals `5.136e-13/1.113e-14` and runtimes `73.25s/89.49s`. v048 also
adds a coarse-first public-horizon `double_pendulum` `Gauss6/FullVA` tranche
at `T=3`, `h=[0.1,0.05,0.025]`, reference `h=0.0125`, with
position/velocity orders `7.951/7.042`; this is intentionally not the public
`1e-4` policy. v048 also adds matching coarse same-window public
double-pendulum baselines at `T=3`, `h=[0.1,0.05,0.025]`, reference
`h=0.0125`: `rA/reps` complete 6/6 rows with position/velocity orders
`0.703/0.754`, while `rp` records three Newton nonconvergence rows. v048 now
also adds a single-pendulum coarse same-window tranche at the same `T=3`,
`h=[0.1,0.05,0.025]`, reference `h=0.0125`, with 9/9 public rows, 3/3 local
`Gauss6/FullVA` rows, a 4-row work/precision summary, and local position
order `6.054`. v048 now also writes a 2-row closed-loop surrogate dynamic gate for `four_link` and
`slider_crank`. It records selected-window residual-to-error ratios against
the public `rA` scale, but `accepted_dynamic_order_count=0`, so it is not
dynamic order/work or superiority evidence. v048 also writes a 2-row
closed-loop dynamic error floor audit: both rows pass the velocity/acceleration
floor-evidence check, both rows retain a position/reference-floor blocker, and
`accepted_dynamic_order_count=0`. v048 now also writes a closed-loop coarse
dynamic-order probe at `T=0.2`, `h=[0.1,0.05,0.025]`, reference `h=0.0125`;
it has `11/12` rows ok, one public `slider_crank`/`rA` failure at `h=0.1`,
two local velocity/acceleration evidence rows, two local position-floor rows,
and `accepted_dynamic_order_count=0`, so larger steps do not close the
four-link/slider-crank dynamic-order blocker. v048 now also writes a 2-row
closed-loop dynamic-order closure contract: it records theorem order `6` for a
true `Gauss6/FullVA` dynamic trajectory row, records `true_dynamic_local_rows=2`
and `accepted_dynamic_order=2` for the two closed-loop mechanisms inside the
coarse local closure-contract scope, while preserving
`external_superiority_claim=false` and leaving source-policy closure open. v048 now
also writes a 2-row closed-loop true-dynamic-row feasibility audit: it confirms
from source that the current local closed-loop path is
`simulate_v046_local_kinematic_fullva` with `setup_system(..., "kinematics", ...)`
and post-solve reaction reconstruction, not a local dynamic DAE trajectory
integrator. v048 now also writes a 7-row closed-loop residual-to-error theorem
obligation gate with seven blocking obligations, including dynamic
residual identity, an `O(h^7)` residual rate, a closed-loop DAE stability or
inf-sup bound, non-floor-limited estimator calibration, reference-floor
exclusion, a coarse-first accepted campaign, and a manuscript theorem/proof.
v048 now also writes a 4-row
coarse-first external readiness gate with
`coarse_first_ready_examples=2/4`, `closed_loop_surrogate_available=2`,
`closed_loop_floor_audit_available=2`, and
`coarse_first_dynamic_order_missing=0`, preserving the rule that `1e-4` is
not a default execution target. v048 also writes a 12/12 selected
same-window comparison table for public `rA` dynamics versus local
`Gauss6/FullVA` closed-loop residual rows at `T=0.2`,
`h=[0.02,0.01,0.005]`. The closed-loop rows verify constraint/reaction
residuals and expose final-error/work table shape, but they are still not the
exact public `T=3` dynamic order/work superiority campaign. The v048 report
now also writes manuscript-table summary CSVs for the 2021 public order/work
baseline, the selected same-window work/precision ratios, and the single
coarse work/precision ratios. v048 now also
completes 9/9 public `double_pendulum` dynamic self-reference order rows for
`rA/rp/reps` at `T=3`, `h=[1e-2,2e-3,1e-3]`, reference `h=1e-4`; these fill
the order gap left by public `order_analysis.py` while remaining distinct from
kinematic-reference order rows. The v048 four-example performance matrix now
records 48 method/example rows with 32 completed and 0 partial rows, but it is
a coverage ledger rather than a
superiority claim. The later
Kissel/Bakke/Negrut velocity-partitioning Lie-group ODE paper is tracked as a
code-path-resolution gate until its public reproducibility code is resolved;
v048 records the EasyChair PDF reference, public web-search status, and both
local SBEL mirror trees over `origin/master` plus `origin/user/aaron/msd`.
The specification, case inventory, and code inventory have been extracted; the
numerical same-test campaign has not yet been run.

The next method-engineering gate is not the four ASME examples; those are
accepted under the current method-side contract. That method gate is still to
close `full_tfe_stage_replacement_missing` by deriving and validating a
source-free, projection-free, non-terminal-row-replacement TFE stage residual
that keeps the 132-row Newton system full rank, closes raw terminal endpoint
velocity, and recovers the smooth order target on the accepted h-sweep.

## 2026-09-17 Manuscript Compaction and Proof-Route Pin

The CMAME manuscript `paper_v047_cylindrical_chain/main_cmame.tex` was compacted around the
exact stage identity (13047 lines / 259 pages to 4075 lines / 89 pages after the second pass). The lifted reduced
Gauss stage satisfies all 132 implemented rows exactly (`lem:exact-stage-identity`), so the
stage-residual perturbation term of the order theorem is zero and the local defect is
`C_loc = C_G + C_E + C_N c_eta`. Retained theorem interfaces are P1, P2, P6; P7 stays the
output boundary; P3, P4, P5 are removed. This changes no claim state: the accepted method,
order claim, ASME example roles, `submission_ready=false`, and blockers OC4/OC6/OC12 are
unchanged.

Additional authoritative files:

- `paper_v047_cylindrical_chain/EXACT_STAGE_IDENTITY_GATE.md` / `.json`
  (built by `build_exact_stage_identity_gate.py`, checked by
  `validate_exact_stage_identity_gate.py`; runs the Lean axiom check when the toolchain
  in `~/lean/integrator_order_proof` is present).
- `paper_v047_cylindrical_chain/notes/LEAN_RESIDUAL_ROW_FAMILY_AUDIT.md` (why the old
  displayed rows did not match the implemented residual).
- `docs/LEAN_FORMALIZATION.md` (pointer to the Lean development).

The top-level `validate_pipeline_outputs.py` runs the exact-stage-identity gate in the slot
formerly occupied by the proof-closure manifest step; its other retired-gate steps return a
`superseded_by=EXACT_STAGE_IDENTITY_GATE` notice instead of re-validating archived records.

Superseded (files kept, marked `superseded_by`, removed from the package validator chain and
stubbed in the top-level validator):
`PROOF_CLOSURE_MANIFEST`, `PROOF_CLAIM_TRACEABILITY_AUDIT`, `CMAME_STRICT_PROOF_AUDIT`,
`CMAME_STRICT_PROOF_POLICY_RECONCILIATION_AUDIT`, `CMAME_PROOF_STYLE_AUDIT`,
`NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE`. The pre-compaction source is
`paper_v047_cylindrical_chain/notes/main_cmame_pre_v049_backup.tex`.

### 2026-09-17 second pass (P2 from P1, P6 stopping rule, numerical identity check, Lean in package)

- `lem:p2-from-p1` / `eq:p2-perturbation-bound`: P2 follows from P1 plus the chart assumption for
  `h ≤ h_0` (Lean `uniform_inverse_of_perturbation`). `lem:newton-envelope` /
  `eq:newton-envelope-decay`: the `c_η h⁷` stopping rule of P6 is reached after `O(log 1/h)`
  simplified-Newton steps (Lean `simplified_newton_residual_decay`); the existing
  `PROOF_SOLVER_TOLERANCE_REGIME_SWEEP` (policy `scaled_h7_c1e4`, `T = 0.08`) instantiates it.
  P1, P2, P6 stay the stated interfaces; the theorem statement is unchanged.
- New authoritative files: `EXACT_STAGE_IDENTITY_NUMERICAL_CHECK.md/json/csv`
  (`run_exact_stage_identity_numerical_check.py`, checked by
  `validate_exact_stage_identity_numerical_check.py`; `h ∈ {0.04, 0.02, 0.01}`, `T = 0.08`,
  Newton tolerance `1e-13`, threshold `1e-10`; not a heavy run, never calls `run_v047.py`), and the
  Lean source copy `paper_v047_cylindrical_chain/lean/` (12 `.lean` files, `lakefile.toml`,
  `lean-toolchain`, `lake-manifest.json`, `scripts/Axioms.lean`; the gate records byte-level sync
  with `~/lean/integrator_order_proof`). Both are in `validate_paper_package.py`.
- `P2_CONSTANTS_NUMERICAL_CHECK.md/json/csv` (`run_p2_constants_numerical_check.py`, checked by
  `validate_p2_constants_numerical_check.py`, in `validate_paper_package.py`): `J_h` vs `J_0` on the
  smooth chain, Euclidean norm on the implemented layout. Status
  `inverse_bound_observed_neumann_threshold_below_reported_h`: `‖J_h⁻¹‖ ≤ 1.55‖J_0⁻¹‖` observed on
  all grids, Neumann threshold `h_0 ≈ 2.5e-5–3.7e-5` far below the reported `h`. Records that the
  Algorithm-1 predictor (zero angular velocity/acceleration guesses) is `O(1)` from `Z_G` and its
  first Newton step expands; `lem:newton-envelope` is stated for predictors in the contraction ball.
  Algorithm 1's predictor description in the manuscript now lists the zero angular guesses.
- The `external/public-metadata` mirror (`https://github.com/uwsbel/public-metadata`) was restored
  on 2026-09-18 and, on 2026-09-19, replaced by a blob-filtered no-checkout clone
  (`git clone --filter=blob:none --no-checkout --depth 1`, branches `master` and `user/aaron/msd`,
  ~200 KB, working tree empty). This matches the recorded audit state
  (`local_public_metadata_visible_non_git_file_count == 0` in the VP2024 disposition audit) and keeps
  the two cross-paper benchmark validators passing. The clone is excluded by the root `.gitignore`.
- `P2_CONSTANTS_NUMERICAL_CHECK` schema v2 (2026-09-19) adds the endpoint-linearized residual norm
  `‖J_0^{-1}·‖` (Neumann `h_0 ≈ 8e-4`), a row/column-equilibrated norm, the dominant block of
  `(J_h − J_0)/h` (Newton–Euler rows × stage velocities: Brown–McPhee curvature, Stribeck velocity
  0.5), and a frictionless variant of the mechanism (`C_J` smaller by ~15×, `h_0 ≈ 1.4e-2`). The
  manuscript reports this in `tab:p2-constants-check` and the new `tab:predictor-check`.
- Repository hygiene (2026-09-19): `.venv_sbel/` and all `__pycache__/` files were removed from the
  git index (working tree untouched) and are ignored by the root `.gitignore`. The top-level
  `validate_pipeline_outputs.py` re-executes itself under `.venv_sbel/bin/python` when `jax` is not
  importable, so it may be started with the system `python3`. The manuscript generator in the
  session scratchpad reads the pristine original from commit `cbcee80`, not from `HEAD`.
- Manuscript additions: `tab:exact-identity-check`, `tab:p2-constants-check`, `tab:lean-development`, modelling sentence for
  the second lower pair, closed-loop scope sentence, observed-order remark. `main.tex` and
  `main_concise.tex` carry a legacy status note after `\maketitle`; both rebuild with zero
  warnings (46 and 8 pages).
- Operational: run the top-level `validate_pipeline_outputs.py` with `.venv_sbel/bin/python`
  (system `python3` lacks `jax`, so `validate_dynamic_row_oracle_gate.py` and the extracted
  narrowed-archive runner fail under it, and a failed archive run leaves
  `cmame_narrowed_repro_bundle/results/*` in a state that makes the narrowed package audit report
  `bundle summary status stale` until the archive validator runs again). Claim state unchanged:
  `submission_ready=false`, OC4/OC6/OC12 open.

### 2026-09-20 arXiv version (derived, no claim-state change)

`paper_v047_cylindrical_chain/arxiv/` holds the arXiv preprint: `main_arxiv.tex` (plain
`article` class, geometry/amsthm/booktabs/graphicx/hyperref), the 13 flat figures, `README.md`
(title, plain-text abstract under the 1920-character arXiv limit, suggested categories math.NA /
cs.CE / physics.comp-ph, upload steps), `arxiv_submission.zip` (source + figures, fixed
timestamps) and `ARXIV_VERSION.json`. It is generated by `build_arxiv_version.py` from
`main_cmame.tex`: the manuscript's theorem environments and macros are copied verbatim from the
CMAME preamble and the body from `\section{Introduction}` on is copied verbatim except for the
figure file names, so the two sources cannot drift. `validate_arxiv_version.py` (in
`validate_paper_package.py`; `arxiv/main_arxiv.log` is in the LaTeX log-cleanliness list)
regenerates the source in memory and fails if any derived file is stale. Rebuild order after a
manuscript edit: install `main_cmame.tex` → flat copy → `python3 build_arxiv_version.py` →
`latexmk -pdf main_arxiv.tex` in `arxiv/` → the usual builder sequence and chains.

### 2026-09-20 folder reorganization (no claim-state change)

- Work-tree top level reduced to `README.md`, `CURRENT_PIPELINE_CONTRACT.md`, `validate_pipeline_outputs.py`
  plus directories. Ledgers and audits moved to `docs/` (`VERSION_LEDGER.md`, `VERSION_TREE.md`,
  `ORDER_PROOF_LEDGER.md`, `PIPELINE_AUDIT.md`, `VALIDATION_QUICKSTART.md`, `METHOD_COMPARISON.md`,
  `VERSION_ROUND_TEMPLATE.md`, `FOLDER_MAP.md`, `FOLDER_CLEANUP_PLAN.md`, `LEAN_FORMALIZATION.md`,
  `literature_status_2026-05-26.md`, `version_ledger.csv`, `version_progression.png`); scripts that read
  them (`validate_pipeline_outputs.py`, `validate_paper_claims.py`, `validate_v047_outputs.py`,
  `tools/plot_version_ledger.py`) were repointed. `tools/` holds the ledger plot and the new
  `build_path_dependency_report.py` → `docs/PATH_DEPENDENCY_REPORT.md/json`.
- Paper package: manuscript backups and working notes moved to `paper_v047_cylindrical_chain/notes/`
  (`main_cmame_pre_v049_backup.tex`, the flat backup, `PROPOSED_METHOD_SECTION_REVISION.tex`,
  `LEAN_RESIDUAL_ROW_FAMILY_AUDIT.md`). LaTeX byproducts (`.aux`, `.fls`, `.fdb_latexmk`, `.spl`, `.out`)
  untracked and ignored; logs and PDFs stay tracked.
- Not moved, deliberately: `vNNN_*` directories (enumerated by the top-level validator and imported by
  `run_v047.py`), the paper-package records and scripts (evidence ledger; ~750 files, nearly all read by
  validators), the legacy `main.tex`/`main_concise.tex` (read by five validators), and the root reference
  PDFs (read by ~35 scripts). See `docs/PATH_DEPENDENCY_REPORT.md`.

### 2026-09-20 remotes

- Research repo pushed to `https://github.com/jqwang2373/integrator_research` (`main`, fast-forward from
  `cbcee80` to the reorganization commit). Lean development pushed to the new private repo
  `https://github.com/jqwang2373/integrator_order_proof`. GitHub CLI is installed at `~/bin/gh`
  (logged in as jqwang2373, https protocol, `gh auth setup-git` configured the credential helper).
