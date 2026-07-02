# CMAME Blocker Closure Gate

Status: **NARROWED CLAIM SUBCHECK CLOSED; GLOBAL SUBMISSION OPEN**

This gate converts the ARS-style submission-readiness review into a
machine-checkable blocker ledger. It is intentionally read-only and does not
invoke `run_v047.py`, v048 numerical runners, or any default `1e-4` campaign.

## Execution Policy

The current blocker-closure path is `coarse_first_no_default_1e-4`.
Strict public-policy `1e-4` rows are opt-in only. They are useful for exact
source-policy reproduction, but they are not the default way to close the
current order/proof/readiness blockers.

## Objective Blocker Matrix

The global objective blocker matrix remains:

- `blocker_open_by_id=OC4:True,OC6:True,OC12:True`
- `blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready`
- `blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False`

This matrix is inherited from `OBJECTIVE_COMPLETION_AUDIT.json`; it keeps
OC4, OC6, and OC12 open and does not authorize B4/source-policy execution.

## Current Gate Result

- Reader-facing status: `global_submission_ready=false; narrowed_subcheck_passed=true`
- `submission_ready=false`
- `global_submission_standard_met=false`
- `global_open_blockers=OC4,OC6,OC12`
- OC6/P6 disambiguation: `OC6` is the global source-policy TFE DAE-runner
  blocker; theorem `P6` is the retained solver-scale interface
  \(\eta_h^{\rm tube}\le c_\eta h^7\), not a closed source-policy runner row.
- `narrowed_claim_subcheck_closed=true`
- legacy narrowed-claim compatibility flag, retained for validators only and not a global readiness marker:
  `legacy_submission_ready_under_narrowed_claim=true`
- deprecated narrowed-claim compatibility alias, retained for validators only and not a global readiness marker:
  `submission_ready_under_narrowed_claim=true`
- `submission_ready_scope=global_submission_ready_false_narrowed_claim_only`
- narrowed-claim alias warning:
  `validator-only compatibility aliases; do not read legacy_submission_ready_under_narrowed_claim or submission_ready_under_narrowed_claim as global submission readiness`
- `global_proof_package_submission_ready=false`
- legacy proof-readiness compatibility alias: `proof_submission_ready=false`
- `full_source_policy_submission_ready=false`
- `mechanical_preflight_passed=true`
- narrowed/pdf-style subcheck quality marker only, not global readiness:
  `quality_review_passed=true`
- `open_narrowed_claim_blockers=0`
- `closed_blockers=B1,B2,B3,B4,B5,B6,B7,B8`
- `same_test_campaign_status=not_run`
- `external_superiority_claim=false`
- all-example common-reference comparison matrix closed: `true`
- common-reference examples checked: `single_pendulum`, `double_pendulum`,
  `four_link`, `slider_crank`
- common-reference cells checked: `44`
- raw rows recomputed for common-reference audit: `132`
- common-reference summary mismatches: `0`
- direct nonlocal velocity-order wins: `40/40`
- direct nonlocal finest-velocity-error wins: `40/40`
- all-method claim-disposition audit: `44` total cells, `40` nonlocal cells,
  all four examples checked
- all-method source-policy rows closed/open: `0/40`
- all-method strict external error-claim rows allowed: `0`
- B4 post-execution audit status:
  `existing_outputs_present_no_verified_authorized_execution_no_source_policy_rows_promoted`
- B4 post-execution verified-authorized/existing-artifacts/output-present:
  `false/true/true`
- B4 post-execution promoted rows: `0/40`
- B4/B7 post-execution close flags: `false/false`
- B4/B7 narrowed-claim policy closure: `true`
- B6 narrowed-claim final prose closure: `true`
- B6 post-execution dependency boundary: `existing_artifacts_present_no_verified_authorized_execution_zero_promoted_rows_source_policy_excluded_final_prose_enabled`
- source-policy flagged rows: `15`
- source-policy flagged raw rows checked by all-example audit: `45`
- source-policy flagged examples checked: `single_pendulum`, `double_pendulum`,
  `four_link`, `slider_crank`
- source-policy velocity-mismatch rows: `10`
- source-policy superiority claim allowed: `false`
- B2 is closed only by Route B claim demotion; B4 closes only after the
  narrowed claim policy excludes source-policy work/precision from the current
  submission scope.
- `default_1e-4_required=false`
- local evidence coverage examples: `4/4`
- accepted method dynamic-order examples: `2/4` (`single_pendulum`, `double_pendulum`)
- closed-loop mechanism-coverage coarse-dynamics diagnostics: `four_link`, `slider_crank`
- accepted source-policy dynamic-order examples: `0/4`
- Newton-Euler runtime expression structure checked: `true`
- Newton-Euler runtime expression structure rows: `36` (`18/18` translational/rotational)
- Newton-Euler symbolic defect certificate complete: `false`
- HI2022 policy-decision audit status:
  `bounded_T0p1_rows_complete_full_T8_source_policy_open`
- HI2022 bounded rows: `24/24`, model/form groups with three h values: `8/8`
- HI2022 full `T=8` source-policy completed: `false`
- HI2022 accepted for external superiority: `false`
- HI2022 source-policy dynamic-order examples: `0/4`
- HI2022 source-policy row audit status:
  `bounded_T0p1_rows_complete_full_T8_source_policy_rows_not_closed`
- HI2022 active/source-policy-closed rows: `3/0`
- HI2022 B2 requirement can close now: `false`
- VP2024 source-policy suite demoted: `true`
- VP2024 demoted source-policy rows: `4`, flagged rows: `3`
- HI2022 source-policy suite demoted: `true`
- HI2022 demoted source-policy rows: `3`, flagged rows: `3`
- RA2021 source-policy suite demoted: `true`
- RA2021 demoted source-policy rows: `5`, flagged rows: `5`
- TFE source-policy suite demoted: `true`
- TFE demoted source-policy rows: `4`, flagged rows: `4`
- active source-policy flagged rows after demotions: `0`
- B2 remaining-work manifest status:
  `route_b_all_external_suites_demoted_no_active_external_superiority_rows`
- B2 remaining-work manifest added: `true`
- B2 active/demoted flagged rows after Route B demotion: `0/15`
- B2 source-policy closed rows and external-superiority-ready rows: `0/0`
- RA2021 source-policy row audit status:
  `public_rows_complete_source_policy_rows_not_closed`
- RA2021 public order groups and timing rows: `12/12`, `12/12`
- RA2021 source-policy reproduction rows: `0/12`
- RA2021 B2 requirement can close now: `false`
- TFE source-policy row audit status:
  `source_policy_spec_extracted_runner_rows_not_closed`
- TFE active/source-policy-closed rows: `0/0`
- TFE source-policy spec extracted: `true`
- TFE pendulum runner implemented: `false`
- TFE B2 requirement can close now: `false`

## Route B Evidence Sync

- partial_evidence_overlay retained for external-suite diagnostics.
- B2 closure execution plan: `b2-source-policy-closure-execution-plan-v1`.
- all active suites ready remains `true`.
- explicit `1e-4` rows remain opt-in only.
- B2/B4 can close from common-reference evidence alone: `false`.
- external run queue, acceptance sheet, all-example comparison reconciliation, source-policy closure triage, all-example source-policy audit, all-method claim-disposition audit, external case/evidence reconciliation, HI2022 policy-decision audit, HI2022 source-policy row audit, VP2024 explicit demotion ledger, B2 remaining-work manifest, B2 closure execution plan, RA2021 source-policy row audit, and TFE source-policy row audit added.
- `SOURCE_POLICY_CLOSURE_TRIAGE.md/json`.
- `ALL_EXAMPLES_SOURCE_POLICY_AUDIT.md/json`.
- `HI2022_POLICY_DECISION_AUDIT.md/json`; 24/24 bounded `T=0.1` rows.
- accepted source-policy dynamic-order examples stay at `0/4`.
- `RA2021_SOURCE_POLICY_ROW_AUDIT.md/json`.
- RA2021 public order groups and timing rows are complete (`12/12` and `12/12`).
- source-policy reproduction rows remain `0/12`.
- EXTERNAL_SAME_TEST_RUN_QUEUE.md/json retains 20 non-`1e-4` shards.

- historical method-side accepted dynamic-order examples: `single_pendulum`,
  `double_pendulum`
- historical coverage-only method-side examples: `four_link`, `slider_crank`;
  these now have separate closed-loop coarse-dynamics diagnostics, but still
  not source-policy external dynamic-order closure
- v048 coarse-first ready examples: `2/4`
- closed-loop coarse-dynamics diagnostic examples: `four_link`, `slider_crank`
- closed-loop coarse-dynamics diagnostic count: `2`
- four-link coarse-dynamics primary diagnostic slopes: `5.955/5.955/6.085/5.971`
- slider-crank coarse-dynamics primary diagnostic slopes: `6.164/6.159/7.341/6.426`
- public work/precision available examples: `four_link`, `slider_crank`
- public work/precision missing examples: none
- strict common-reference available examples: `four_link`, `slider_crank`
- strict common-reference gap examples: none
- strict common-reference figure available: `true`
- strict common-reference figure integrated in manuscript: `true`
- limitation explanation figure integrated in manuscript: `true`
- coarse baseline/work-precision figure integrated in manuscript: `true`
- closed-loop coarse-dynamics diagnostic figure integrated in manuscript: `true`
- method-stage architecture figure integrated in manuscript: `true`
- all-method result matrix figure integrated in manuscript: `true`
- work/precision compendium figure integrated in manuscript: `true`
- figure-set audit added: `true`, `13/13` figures checked in main/flat/PDF
- B6 prose-residue audit added: `true`
- B6 post-execution dependency boundary: `existing_artifacts_present_no_verified_authorized_execution_zero_promoted_rows_source_policy_excluded_final_prose_enabled`
- B6 post-execution final prose enabled by narrowed policy: `true`
- main-body machine-token count: `0`
- artifact macros confined to reproducibility appendix: `true`
- appendix artifact macro count: `0`
- v048 closed-loop coarse probe accepted dynamic-order count: `0`
- partial independent formula-row oracle rows: `96`
- partial kinematic/lower-pair defect certificate rows: `96`
- Newton-Euler dynamic defect obligation rows: `36`
- Newton-Euler active direct dynamic-defect open obligations: `0`
- Newton-Euler symbolic/primitive-route open obligations: `1`
- Newton-Euler symbolic target audit rows: `36`
- Newton-Euler symbolic target translational/rotational rows: `18/18`
- Newton-Euler symbolic target inventory complete: `true`
- Newton-Euler symbolic defect certificate complete: `false`
- partial formula-row oracle coverage: `96 non-dynamic rows`
- partial formula-row excluded family: `newton_euler_weak_balance`
- full independent formula-row oracle rows: `132`
- runtime formula-row oracle complete: `true`
- formula-row AD Jacobian oracle: `true`
- formula-row AD Jacobian probe count: `3`
- max formula-row Jacobian mismatch: `3.330669e-16`
- Newton-Euler AD-expanded row oracle rows: `36/36`
- Newton-Euler AD-expanded row oracle columns/probes: `132/3`
- Newton-Euler AD-expanded symbolic oracle closure: `true`
- B1 independent residual symbolic row oracle rows: `36/36`
- B1 AD-expanded symbolic derivative cells: `4752/4752`
- B1 remaining symbolic oracle requirements: `[]`
- strict conditional residual-bridge proof boundary audit added: `true`
- strict direct residual-bridge proof complete: `true`
- strict primitive/Taylor route complete: `false`
- strict primitive root/root-dependent/downstream primitives:
  `['P_state', 'P_acc']` / `['P_lambda']` / `['P_geom', 'P_gyro']`
- strict primitive root/root-dependent/downstream term-row totals: `162/72/54`
- two-layer proof boundary consistent: `true`
- Newton-Euler dynamic-row direct-substitution contract direct-route row-defect closed rows: `36/36`
- Newton-Euler D5 readiness open lifted-stage terms: `0/36`
- Newton-Euler D5 direct route PC2 closed: `true`
- Newton-Euler D5 primitive/Taylor route closed: `false`
- P_state direct full-residual route certificate closed: `true`
- P_state direct-route PS3/state/h-acceleration rates closed: `true/true/true`
- P_state primitive route closed by direct corollary: `false`

## Blocking Closure Ledger

| ID | Blocking area | Current status | What closes it |
| --- | --- | --- | --- |
| B1 | Method derivation and implementation oracle | closed by AD-expanded symbolic oracle certificate; runtime row-layout, block-functional, full formula-row, multi-probe formula-row AD Jacobian oracle, 36-row Newton-Euler AD-expanded runtime/formula binding audit, B1 36-row independent residual symbolic row-oracle closure certificate, and 4752-cell AD-expanded symbolic closure certificate added | `DYNAMIC_ROW_ORACLE_GATE.md` now executes the accepted residual/Jacobian path, verifies the 132-row partition on a finite smooth probe, cross-checks the Gauss6-equivalent weighted block-functional row families, independently reassembles all 132 runtime formula rows including `newton_euler_weak_balance`, and checks the independent formula-row AD Jacobian against `R_JAC` on three deterministic probes. `NEWTON_EULER_AD_EXPANDED_ROW_ORACLE_AUDIT.md/json` records row-level AD-expanded runtime/formula binding coverage for all 36 Newton--Euler dynamic rows, with 132 AD columns per row, 3 deterministic probes, and max mismatch `3.330669e-16`; this runtime audit alone is not the proof. `B1_SYMBOLIC_ROW_ORACLE_CLOSURE_CERTIFICATE.md/json` closes the independent residual-row symbolic oracle item for all 36 Newton--Euler rows by source/template identities, runtime row binding, virtual-work expansion, and balance identities. `B1_AD_EXPANDED_SYMBOLIC_ORACLE_CLOSURE_CERTIFICATE.md/json` then differentiates those closed residual identities columnwise on the smooth proof tube, closing `36 x 132 = 4752` AD-expanded symbolic derivative cells while keeping `dynamic_symbolic_oracle_complete=false`, the symbolic-certificate `O(h^7)` lane open, and `submission_ready=false`. `KINEMATIC_ROW_DEFECT_CERTIFICATE.md/json`, `NEWTON_EULER_DEFECT_OBLIGATION_GATE.md/json`, `NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.md/json`, and the D5 direct-route artifacts remain synchronized with the proof boundary: B1 is closed by the symbolic oracle certificates, while the direct-route `O(h^7)` proof is recorded separately under B3 and the primitive/Taylor route remains an open conditional certificate schema. |
| B2 | Same-test external baseline | closed by Route B claim demotion; external baseline gate and suite claim-boundary table added, external run queue, acceptance sheet, all-example comparison reconciliation, source-policy closure triage, all-example source-policy audit, all-method claim-disposition audit, external case/evidence reconciliation, HI2022 policy-decision audit, HI2022 source-policy row audit, VP2024/HI2022/RA2021/TFE demotion ledger, B2 remaining-work manifest, B2 closure execution plan, RA2021 source-policy row audit, and TFE source-policy row audit added; TFE source-policy spec added | Route B closes only the external-superiority claim requirement. `CMAME_EXTERNAL_BASELINE_GATE.md` still records `same_test_campaign_status=not_run`, and all source-policy execution rows remain `0/40`; no common-reference row is promoted to source-policy superiority. `COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.md/json` retains the finite-grid common-reference diagnostic across all four examples: the 44-cell method/example matrix is recomputed from 132 raw rows with zero mismatches, and Gauss6/FullVA wins all 40 direct nonlocal velocity-order and all 40 direct nonlocal finest-velocity-error comparisons. `EXTERNAL_SUITE_DEMOTION_LEDGER.md/json` explicitly demotes VP2024, HI2022, RA2021, and TFE from external-superiority scope; the 4 VP, 3 HI2022, 5 RA2021, and 4 TFE source-policy rows are retained only as common-reference or claim-boundary diagnostics. `B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.md/json` records active/demoted flagged rows after Route B demotion as `0/15`, source-policy closed rows and external-superiority-ready rows as `0/0`, and `default_1e-4_required=false`. A future paper that reintroduces external-superiority claims must reopen this gate and execute source-policy same-test rows. |
| B3 | Conditional proof status | closed by the direct residual-bridge/Kantorovich perturbation route; proof contract gate added; comparison claim demoted to proposition; noncircular proof-condition decomposition added; 96-row non-dynamic defect certificate, Newton-Euler dynamic obligation ledger, D1/D2 balance-identity audit, Newton-Euler symbolic target audit, D5 direct-substitution certificate, direct residual-bridge/Kantorovich proof audit, and B3 direct-proof review audit added; primitive/Taylor 162-subterm route retained as an open conditional certificate schema | `CMAME_PROOF_CONTRACT_GATE.md` records that the current order theorem is still conditional in the solver/regularity sense: `eta_h <= c_eta h^7` is retained as a theorem condition, fixed-tolerance runs are finite-run evidence, and the residual-to-error route is not accepted. `KINEMATIC_ROW_DEFECT_CERTIFICATE.md/json` closes the smooth-lift proof obligation for the 96 non-dynamic row families. `D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE.md/json` closes the 36 Newton-Euler dynamic rows by direct substitution on the smooth Gauss lift: the dynamic residual is zero row-wise after the D1/D2/D3/D4/D6 inputs, without using `P_state` actual PS3, `P_acc`, `P_lambda`, finite probes, or residual-to-error promotion. The manuscript's stage-residual perturbation lemma now uses Taylor's formula with integral remainder, a quadratic remainder, a contraction radius, and explicit constants `||Z_A-Z_G|| <= C_Z h^7`, `C_Z=2 M C_R`, and `C_A=M_E C_Z` for endpoint transfer. `PROOF_CLOSURE_MANIFEST.md/json` records `strict_direct_residual_bridge_submission_standard.satisfied=true`, `required_pc2_route=direct_residual_bridge_kantorovich_route`, `direct_residual_bridge_kantorovich_route_closed=true`, and `primitive_route_required_for_b3_closure=false`; the primitive route still records `actual_taylor_bounds_proved=0`, `open_taylor_bound_terms=162`, and `open_primitive_count=5` as an uninstantiated conditional schema only. `B3_DIRECT_PROOF_REVIEW_AUDIT.md/json` records that the direct proof review passed and `b3_can_close_from_proof_review=true`. B3 closure is independent of B1; B1 is now closed separately by the AD-expanded symbolic oracle certificate. |
| B4 | Numerical evidence strength | closed under narrowed claim policy; observed-order interpretation, order-acceptance matrix, closed-loop coarse-dynamics diagnostic matrix, fair-baseline acceptance sheet, all-example common-reference order/error matrix, all-method claim-disposition audit, TFE algorithm-literal endpoint probe, TFE source-grid exact-T endpoint subclosure, TFE source-pendulum same-test work/precision evidence, TFE algorithm-literal work/precision audit, post-execution promotion contract added, existing-artifact post-execution audit recorded, and narrowed-claim reclassification added | The finite-grid common-reference order/error comparison is closed for all four examples: `single_pendulum`, `double_pendulum`, `four_link`, and `slider_crank`, with `44/44` matrix cells, `132` raw rows recomputed, zero summary mismatches, and `40/40` direct nonlocal velocity-order and finest-velocity-error wins. Existing work/precision rows remain diagnostic and close `0/40` source-policy rows. `B4_B7_NON_SUPERIORITY_ROUTE_AUDIT.md/json` records `b4_b7_closed_by_narrowed_claim_policy=True`: B4 closes only for the current formal-order/common-reference diagnostic claim, with source-policy work/precision and external-superiority claims excluded. A future paper that reintroduces source-policy work/precision must reopen this gate. |

B4 progress markers: order-acceptance matrix added; closed-loop
coarse-dynamics diagnostic matrix added; fair-baseline acceptance sheet added;
common-reference order/error matrix closed; all-method claim-disposition
audit added across all four examples; TFE algorithm-literal endpoint probe
added with `4/12` methods/metric rows and source-policy rows still `0`;
retained diagnostic anchors: `ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.md/json`,
`TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE.md/json/csv`, `4` methods, `12` metric
rows, and `12` terminal-overrun rows,
`tfe_source_pendulum_same_test_work_precision.md/json/csv/png`,
`TFE_ALGORITHM_LITERAL_WORK_PRECISION_AUDIT.md/json/csv`, and
`runtime_proxy_available=false`;
TFE source-grid exact-T endpoint subclosure added with `2` rows resolved,
`4` rows still requiring source endpoint policy, and source-policy rows still
`0`;
TFE source-pendulum same-test work/precision added with `6` methods, `18/18`
ok rows, and `6` summary rows, while same-test candidate work/precision rows
still close `0` source-policy rows; TFE algorithm-literal work/precision audit
added with `4` methods, `12` raw rows, `4` summary rows, and `12`
terminal-overrun rows while closing `0` source-policy rows; B4 post-execution
promotion contract added with schema
`b4-source-policy-post-execution-promotion-contract-v1`, status
`promotion_contract_defined_no_rows_promoted`, rows `0/40`,
ready/unaddressed `20/0`, checks satisfied `False`, closes B4/B7
`False/False`, ready/not-ready lanes `2/2`, and runner/code-path gap rows
`0`; B4 post-execution audit recorded with status
`existing_outputs_present_no_verified_authorized_execution_no_source_policy_rows_promoted`,
verified-authorized/existing-artifacts/output-present `False/True/True`,
promoted rows `0/40`, and B4/B7 close flags `False/False`.
| B5 | Mechanism visual reproducibility | closed | `CMAME_VISUAL_LEGIBILITY_AUDIT.md/json` records the final-PDF legibility check after Figure 2 regeneration. Split mechanism diagrams are not required for this blocker; broader figure-set work remains under B7. |
| B6 | Repository-facing narrative residue | closed under narrowed claim policy; proof-traceability prose pass completed, main-body machine-token removal pass completed, comparison-theorem wording removed, reproducibility appendix compaction pass completed, prose residue audit added, post-execution dependency boundary recorded, and final prose pass closed under narrowed policy | `CMAME_PROSE_RESIDUE_AUDIT.md/json` and `validate_cmame_prose_residue_audit.py` dynamically re-count the CMAME and flat-source main body and record `main_body_machine_token_count=0`, `artifact_macro_confined_to_appendix=true`, `appendix_artifact_macro_count=0`, `default_1e-4_required=false`, and `run_v047_invoked=false`. The post-execution dependency boundary records `existing_artifacts_present_no_verified_authorized_execution_zero_promoted_rows_source_policy_excluded_final_prose_enabled`; promoted rows remain `0/40`, source-policy B4/B7 close flags remain `False/False`, and final prose is enabled by narrowed-policy reclassification rather than row promotion. |

B6 retained history marker: proof-traceability prose pass started before the
final narrowed-claim prose closure.
| B7 | Publication-grade figure set | closed under narrowed common-reference diagnostic figure scope; limitation explanation, coarse baseline/work-precision, closed-loop coarse-dynamics diagnostics, method-stage architecture, all-method result matrix, work/precision compendium, and TFE Algorithm-1-literal Figure 13 panels integrated; figure-set audit added | Figure~8 gives a reader-facing claim-boundary and limitation map, Figure~9 adds coarse-first comparison/work-precision evidence from existing rows, Figure~10 plots closed-loop coarse-dynamics diagnostics without a default `1e-4` run, Figure~11 shows the accepted method architecture and non-claim boundary, Figure~12 gives the all-method all-example common-reference matrix, and Figure~13 consolidates fair candidate/common-reference work/precision rows plus T=10 Algorithm-1-literal Newton-work velocity/coordinate panels from `TFE_ALGORITHM_LITERAL_WORK_PRECISION_AUDIT.csv`. `CMAME_FIGURE_SET_AUDIT.md/json` verifies 13/13 figures across main/flat sources and PDF captions and records `b7_narrowed_diagnostic_common_reference_figure_scope_closed`. Clean source-policy work/precision figures remain a future reintroduction path, not a current B7 dependency. |
| B8 | Related-work depth | closed | `CMAME_RELATED_WORK_AUDIT.md/json` records the expanded six-cluster related-work section, added constrained-collocation, variational-integrator, contact/friction, and Lie-group DAE positioning references, and keeps the non-claim boundaries explicit. |

## Current B1 Direct-Route Update

`NEWTON_EULER_DYNAMIC_ROW_CLOSURE_CONTRACT.md/json` now records
`36/36` direct-route row-defect closed Newton--Euler dynamic rows by the D5 direct-substitution
route, and `D5_DYNAMIC_DEFECT_READINESS_AUDIT.md/json` records
`0/36` open lifted-stage terms with `PC2` closed by that direct route.
This does not close the independent dynamic symbolic-oracle route or the
primitive/Taylor route: `NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.md/json`
still has `certificate_complete=false`, and primitive-route induced Taylor
bounds remain `0/162`.  `B1_SYMBOLIC_ROW_ORACLE_CLOSURE_CERTIFICATE.md/json`
now closes the independent residual-row symbolic oracle item for `36/36` rows,
and `B1_AD_EXPANDED_SYMBOLIC_ORACLE_CLOSURE_CERTIFICATE.md/json` closes the
AD-expanded symbolic oracle for `4752/4752` derivative cells. B1 is therefore
closed; the direct-route \(O(h^7)\) dynamic-row defect remains recorded
separately under B3.

The closure evidence remains row-indexed through the 36-row target map with
18 translational and 18 rotational Newton--Euler rows.
`D5_P_STATE_PS3_FULL_RESIDUAL_ROUTE_CERTIFICATE.md/json` closes a strict
direct-route PS3/state/h-acceleration corollary without closing the
primitive/Taylor route or certifying primitive-route Taylor bounds.
`CMAME_STRICT_PROOF_AUDIT.md/json` records
`direct_route_strict_residual_bridge_kantorovich_proof_complete=true`,
`symbolic_primitive_route_strict_implementation_proof_complete=false`, and
`b1_ad_expanded_implementation_oracle_still_open_after_strict_proof_audit=false`;
it also retains
`primitive_global_dynamic_symbolic_oracle_complete_after_strict_proof_audit=false`.

## Current Proof Runtime-Expression State

The Newton--Euler dynamic-row proof gap has one additional checked layer:
`NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.md/json` now verifies the runtime
source-expression structure for all `36` dynamic rows, split as `18/18`
translational/rotational rows. The checked terms include the lambda-normal
force basis, Brown--McPhee friction call, translational force balance,
proximal/distal moment arms, axis-torque terms, rotational balance, and
`dyn.extend([trans, rot])` ordering in `run_v047.py`.

This source-expression traceability is not itself the proof closure:
`newton_euler_symbolic_defect_certificate_complete=false`.  PC2 is closed
separately by `D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE.md/json`, which
proves zero Newton--Euler residual on the smooth Gauss lift without using the
primitive-lift route or finite probes.

## Current B2 Demotion State

This section supersedes the narrower VP/HI-only demotion counts in the B2 ledger
row above. `EXTERNAL_SUITE_DEMOTION_LEDGER.md/json` explicitly demotes VP2024,
HI2022, RA2021, and TFE from external-superiority scope. The 4 VP, 3 HI2022, 5
RA2021, and 4 TFE source-policy rows are retained only as claim-boundary or
common-reference diagnostics. `B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.md/json`
now records B2 active/demoted flagged rows after Route B demotion: `0/15`;
no active source-policy flagged rows remain after demotion, but no demoted row is
counted as a numerical win and source-policy rows closed stay `0/40`. This
closes B2 only as an external-superiority claim-boundary gate; it does not close
B4 work/precision evidence.

## Next Lightweight Actions

The next useful non-heavy actions are:

1. keep the direct Newton--Euler stage-defect closure and the still-open
   symbolic/primitive-certificate route explicitly separated in proof ledgers;
2. keep the theorem wording explicitly conditional on `eta_h <= c_eta h^7`
   unless a scaled-tolerance run is reported, and keep `CMAME_PROOF_CONTRACT_GATE.md`
   synchronized with the manuscript;
3. keep the Route B external-suite demotion boundary synchronized across
   `CMAME_EXTERNAL_BASELINE_GATE.md`, B2 manifests, and review/package gates;
4. keep `1e-4` rows opt-in for strict source-policy reproduction.
5. keep `CMAME_PROSE_RESIDUE_AUDIT.md` synchronized after any final prose
   edits to the manuscript or flat source.
6. keep `EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.md` synchronized before any
   future external comparison run is approved.

## Validator

Run:

```bash
../.venv_sbel/bin/python validate_cmame_blocker_closure_gate.py
```

Expected markers:

- `cmame_blocker_closure_gate=PASS`
- `open_narrowed_claim_blockers=0`
- `closed_blockers=B1,B2,B3,B4,B5,B6,B7,B8`
- `submission_ready=false`
- `narrowed_claim_subcheck_closed=True`
- legacy narrowed-claim compatibility alias, validator stdout only and not a global readiness marker: `submission_ready_under_narrowed_claim=True`
- `full_source_policy_submission_ready=False`
- `default_1e-4=False`
- `same_test_campaign_status=not_run`
- `comparison_matrix_closed=true`
- `common_reference_examples=single_pendulum,double_pendulum,four_link,slider_crank`
- `direct_nonlocal_order_wins=40/40`
- `direct_nonlocal_error_wins=40/40`
- `all_method_claim_disposition_cells=44`
- `all_method_claim_disposition_nonlocal_cells=40`
- `figure_set_audit=13/13`
- `figure12_all_method_matrix_integrated=True`
- `figure13_work_precision_compendium_integrated=True`
- `source_policy_superiority_claim_allowed=False`
- `accepted_external_dynamic_order_examples=0`
- `parallel_shard_count_without_default_1e-4=20`
- `partial_formula_row_count=96`
- `full_formula_row_count=132`
- `formula_row_ad_jacobian_oracle=PASS`
- `formula_row_ad_jacobian_probe_count=3`
- `partial_kinematic_stage_defect_certificate_checked=True`
- `active_direct_newton_euler_open_obligation_count=0`
- `newton_euler_symbolic_primitive_open_obligation_count=1`
- `newton_euler_symbolic_primitive_open_obligation_scope=symbolic_primitive_certificate_route_not_active_direct_pc2`
- `newton_euler_defect_closed_obligation_count=5`
- `active direct D5 route closed; symbolic/primitive D5 route remains open`
- `main_body_machine_token_count=0`
- `artifact_macro_confined_to_appendix=True`
