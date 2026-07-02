# CMAME Submission Checklist

This checklist records the CMAME/Elsevier package boundary used for the v047
submission draft.

## Primary Files

- `main_cmame.tex`: Elsevier `elsarticle` manuscript source.
- `main_cmame.pdf`: compiled CMAME-facing manuscript.
- `highlights_cmame.txt`: separate editable highlights file.
- `declarations_cmame.md`: competing-interest, funding, data, and AI-use
  declarations.
- `CMAME_SUBMISSION_READINESS_AUDIT.md`: submission-readiness audit against
  CMAME/Elsevier requirements and the local claim boundary.
- `README_CMAME_FLAT_SUBMISSION.md`: notes for the flat LaTeX source package.
- `cmame_submission_flat/main_cmame_submission.tex`: flat source copy for
  Editorial Manager, with figures at the same directory level.
- `cmame_submission_flat/main_cmame_submission.pdf`: compiled flat source
  manuscript.
- `cmame_submission_flat.zip`: upload-ready flat LaTeX source archive.
- `figures/convergence.png`: convergence evidence figure.
- `figures/asme_lower_pair_graph_bridge.png`: four-example lower-pair bridge.
- `figures/asme_closed_loop_kinematic_fullva.png`: closed-loop example figure.
- `figures/order_closure_blend.png`: full-TFE non-claim diagnostic figure.
- `figures/velocity_compression.png`: velocity-compression diagnostic figure.
- `figures/sparse_speed_gap.png`: sparse backend caveat figure.
- `figures/strict_common_reference_work_precision.png`: strict common-reference work/precision figure.
- `figures/claim_boundary_limitations.png`: claim-boundary and limitation explanation figure.
- `figures/coarse_baseline_work_precision.png`: coarse-first baseline/work-precision figure.
- `figures/all_method_result_matrix.png`: all-method all-example common-reference result matrix figure.
- `figures/work_precision_compendium.png`: fair candidate/common-reference work/precision compendium figure.
- `COVER_LETTER.md`: cover letter draft.
- `SUBMISSION_ARTIFACT_MANIFEST.json`: machine-readable package manifest.
- `CLAIM_BOUNDARY.json`: machine-readable claim boundary.
- `PAPER_NUMERICAL_RESULT_MATRIX.md/json/csv`: all-method all-example
  order/error matrix with source-policy claim boundaries.
- `RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.md/json`: traceability audit
  proving the `44/44` velocity order/error cells appear in main/flat CMAME
  TeX and extracted PDF text.
- `ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.md/json`: claim-disposition
  audit over `40/40` nonlocal method/example rows, with `40/40` local
  order/error wins and `0/40` source-policy-closed nonlocal rows.
- `ALL_EXAMPLES_RESULT_SANITY_AUDIT.md/json`: exact all-example sanity audit
  locking the 15 flagged nonlocal rows that cannot support external-superiority
  claims.
- `SOURCE_POLICY_ROW_CLOSURE_LEDGER.md/json`: row-level closure ledger for the
  15 flagged source-policy rows; currently zero rows are source-policy closed
  or external-superiority ready.
- `EXTERNAL_CASE_EVIDENCE_RECONCILIATION.md/json`: reconciles the case
  inventory with current bounded/coarse evidence; RA2021 and HI2022 have
  bounded evidence, while TFE2026 and VP2024 remain not-ready or demote.
- `VP2024_CODE_PATH_DISPOSITION_AUDIT.md/json`: all-four-example VP2024
  code-path gate with `4/4` VP2024 source-policy rows unresolved and `4/4`
  VP2024 common-reference proxy order/error wins.
- `PROOF_CLAIM_TRACEABILITY_AUDIT.md/json`: proof-label and proof-boundary
  traceability audit linking the conditional theorem to its open obligations.
- `PROOF_EVIDENCE_MATRIX.md/json`: proof-evidence matrix with the Proof Route
  Legend separating the active direct residual-bridge/Kantorovich route from
  diagnostic primitive/Taylor accounting and retained P6/P7 boundaries.
- `CMAME_PROOF_STYLE_AUDIT.md/json`: proof-style and equation-hygiene audit;
  all main/flat display equation labels are referenced (`283/283`), and the
  active order theorem/proof display labels are referenced (`28/28`).
- `CMAME_SUBMISSION_INTEGRITY_AUDIT.md/json`: local citation-key and sidecar
  integrity audit; external reference web verification is complete.
- `CMAME_FIGURE_SET_AUDIT.md/json`: B7 figure-set audit checking all 13
  main/flat/PDF figure integrations while keeping full source-policy baseline
  figures and complete external work/precision curves open.
- `CMAME_REVIEW_AGENT_REPORT.md/json`: deterministic read-only submission
  review report; current top-level decision is `do_not_submit_global` under
  `submission_standard_scope=global_submission_standard`, with global open
  blockers `open_blockers=OC4,OC6,OC12`; the bounded narrowed subcheck
  disposition is `bounded_subcheck_satisfied_not_global_submit`. The narrowed
  claim marker `narrowed_claim_decision=submit_under_narrowed_claim` applies
  only to the narrowed Gauss6/FullVA method/proof/common-reference package,
  with full source-policy/package readiness still false.

## CMAME/Elsevier Format Gates

- The manuscript uses `\documentclass[preprint,12pt]{elsarticle}`.
- The journal is `Computer Methods in Applied Mechanics and Engineering`.
- The title page includes title, author, affiliation, and corresponding author.
- The abstract is concise and below 250 words.
- The manuscript supplies 1 to 7 keywords.
- The manuscript includes definitions, a nomenclature table, proof statements,
  related work, validation evidence, limitations, declarations, and references.
- Highlights are supplied as a separate editable file with 3 to 5 bullets.
- The manuscript keeps equations and tables editable.
- Figures are included in the manuscript and present as separate PNG files.
- A flat source folder is present for LaTeX upload systems that do not resolve
  figure subfolders.
- A flat source archive is present for direct upload as LaTeX source files.
- Declarations cover competing interest, funding, data availability, and AI use.
- References cited in the text are present in the reference list.

## Claim Boundary

- Accepted method: `Gauss6/FullVA`.
- Method-order claim: conditional `6` under the retained theorem interfaces.
- Smooth observed position/velocity orders: `7.161/7.066`.
- Comparator: local paper-style `m=3` Gauss-Lobatto TFE target.
- Comparator expected order: `5`.
- Local method-side coverage examples: `single_pendulum`, `double_pendulum`, `four_link`,
  `slider_crank`.
- Accepted dynamic-order examples: `single_pendulum`, `double_pendulum`; the
  `four_link` and `slider_crank` rows are coverage-only for dynamic order.
- Full-TFE replacement remains a non-claim:
  `full_tfe_stage_replacement=false`.

## Review Agent Gate

- The review agent must be run before any submission-ready claim:
  `cmame_submission_review_agent.py`.
- The review validator must pass:
  `validate_cmame_review_agent.py`.
- The numerical review gate must pass:
  `validate_paper_numerical_result_matrix.py` with `44/44` cells from `132`
  raw rows and source-policy/direct-error superiority both `False`.
- The result-to-manuscript traceability gate must pass:
  `validate_result_to_manuscript_traceability_audit.py` with `44/44`
  manuscript/PDF velocity cells and external-superiority `False`.
- The all-method claim-disposition gate must pass:
  `validate_all_method_example_claim_disposition_audit.py` with `40/40`
  nonlocal method/example rows, `40/40` local order/error wins, `0/40`
  source-policy-closed nonlocal rows, and `15/40` anomaly/recheck rows.
- The all-example sanity gate must pass:
  `validate_all_examples_result_sanity_audit.py` with four examples covered,
  local rows `4/4`, and `15` flagged nonlocal rows quarantined.
- The row-level source-policy gate must pass:
  `validate_source_policy_row_closure_ledger.py` with all four examples
  covered and zero source-policy-closed rows.
- The external case/evidence reconciliation gate must pass:
  `validate_external_case_evidence_reconciliation.py` with bounded evidence
  suites `ra2021_absolute_coordinate,hi2022_half_implicit` and 0/15
  source-policy-closed rows.
- The VP2024 code-path disposition gate must pass:
  `validate_vp2024_code_path_disposition_audit.py` with `4/4` VP2024
  source-policy rows unresolved, `4/4` VP2024 common-reference proxy
  order/error wins, and the larger-step error diagnostic held noncontrolling.
- The proof traceability gate must pass:
  `validate_proof_claim_traceability_audit.py` with proof labels present,
  `1/7` theorem interfaces submission-satisfied, `5/7` retained theorem
  interfaces, `1/7` open P7 nonpromotion boundary, and `4/0` close
  requirements/unsatisfied close requirements,
  `96` certified non-dynamic rows, `36/0` active direct Newton--Euler
  closed/open rows, `36` symbolic/primitive-route Newton--Euler rows not
  certified by that route, and full proof-package readiness false.
- The proof-style/equation-hygiene gate must pass:
  `validate_cmame_proof_style_audit.py` with labelled display math, no bare
  display math, main/flat display-label references `283/283`, active
  theorem/proof display-label references `28/28`, direct-PC2 proof-gap closure
  true, and `submission_ready=False`.
- The local submission-integrity gate must pass:
  `validate_cmame_submission_integrity_audit.py` with local citation integrity
  passed and `external_reference_web_verification_complete=True`.
- Current global review decision is `decision=do_not_submit_global` with
  `submission_standard_met=False`; the bounded narrowed subcheck disposition is
  `bounded_subcheck_satisfied_not_global_submit`. The narrowed-claim markers
  `narrowed_claim_decision=submit_under_narrowed_claim` and
  `narrowed_claim_submission_standard_met=True` may be used only for the
  narrowed Gauss6/FullVA method/proof/common-reference package; they do not
  override the global decision. legacy compatibility aliases:
  `narrowed_claim_submission_standard_met=true` and
  `narrowed_claim_decision=submit_under_narrowed_claim`. Full source-policy
  package readiness remains false; full source-policy package readiness
  remains false and external superiority remains a non-claim.
- The narrowed archive boundary matches the reproducibility manifest: `True`.
  Narrowed archive boundary tuple:
  `narrowed_archive_ready_not_full_source_policy_runner_archive/0/40/False/False/True`.
  Blocking ids/status: `OC4,OC6,OC12` /
  `OC4=open,OC6=partial,OC12=partial`. Current archive use is
  `narrowed_claim_only`, not a full source-policy runner archive.
  Objective blocker matrix:
  `blocker_open_by_id=OC4:True,OC6:True,OC12:True`;
  `blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready`;
  `blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False`.

## External Same-Test Gate

- External same-test superiority is not submission ready until the original
  TFE paper and the Kissel/Negrut-related public-code families are compared
  on their own numerical tests.
- Treat the 2021 `rA/rp/reps` suite, the 2022 half-implicit suite, and the
  2024 velocity-partitioning Lie-group ODE suite as separate baselines.
- The expanded Kissel/Negrut code inventory is recorded in
  `KISSEL_NEGRUT_CODE_INVENTORY.md`; it also separates the 2023
  velocity-partitioning conference source and the 2024 performance-comparison
  preprint from the runnable 2021 and 2022 suites.
- The current v048 evidence has completed the full 2021 `rA/rp/reps`
  public-code order table for `single_pendulum`, `four_link`, and
  `slider_crank`: 27/27 ok rows and 9/9 public-order groups.
- v048 also has a bounded same-mechanism `Gauss6/FullVA` pilot for the 2021
  single-pendulum setup: 3/3 rows at `T=0.2`, `h=[0.2,0.1,0.05]`, with
  observed orders `6.073/6.033/6.055/6.024`. This is not the full public
  time-window policy.
- v048 also has a 3/3 exact public-horizon `Gauss6/FullVA`
  single-pendulum step-size trio at `T=3`, `h=[1e-2,1e-3,1e-4]`; the finest position/velocity errors are
  `2.584e-14/7.012e-15`, so final-error orders are roundoff/reference-floor limited.
- v048 also has 6/6 selected closed-loop `Gauss6/FullVA` residual rows on the
  2021 `four_link` and `slider_crank` mechanisms at `T=0.2`,
  `h=[0.02,0.01,0.005]`, reference `h=0.001`; these verify constraint and
  reaction residuals, not dynamic order/work superiority.
- v048 also has 12/12 selected same-window comparison rows for public `rA`
  dynamics versus local `Gauss6/FullVA` closed-loop residual rows under the
  same `T=0.2`, `h=[0.02,0.01,0.005]`, public-kinematic-reference
  final-error/work columns; this is not the exact public `T=3` dynamic
  campaign.
- v048 also writes 9-row public order/work and 4-row same-window work/precision
  summaries for paper tables; these are derived from the raw rows and are not
  new superiority evidence.
- v048 also has a bounded 2022 half-implicit `double_pendulum` public-code
  pilot: 6/6 ok rows for `rA/rA_half` at `T=0.1`,
  `h=[0.02,0.01,0.005]`; `rA_half` has a negative-order diagnostic and is not
  accepted convergence evidence.
- `same_test_campaign_status=not_run` and `external_superiority_claim=false`
  remain required until `Gauss6/FullVA` external rows are added for those
  same-test cases.

## Read-Only Validation

Run from `paper_v047_cylindrical_chain/`:

```bash
../.venv_sbel/bin/python validate_cmame_submission.py
../.venv_sbel/bin/python cmame_submission_review_agent.py
../.venv_sbel/bin/python validate_cmame_review_agent.py
../.venv_sbel/bin/python validate_paper_numerical_result_matrix.py
../.venv_sbel/bin/python validate_result_to_manuscript_traceability_audit.py
../.venv_sbel/bin/python validate_all_method_example_claim_disposition_audit.py
../.venv_sbel/bin/python validate_all_examples_result_sanity_audit.py
../.venv_sbel/bin/python validate_source_policy_row_closure_ledger.py
../.venv_sbel/bin/python validate_external_case_evidence_reconciliation.py
../.venv_sbel/bin/python validate_vp2024_code_path_disposition_audit.py
../.venv_sbel/bin/python validate_proof_claim_traceability_audit.py
../.venv_sbel/bin/python validate_cmame_submission_integrity_audit.py
../.venv_sbel/bin/python validate_submission_bundle.py
../.venv_sbel/bin/python validate_paper_package.py
```

Run from the parent work directory:

```bash
.venv_sbel/bin/python validate_pipeline_outputs.py
```

These checks read existing artifacts and must not invoke `run_v047.py`.
