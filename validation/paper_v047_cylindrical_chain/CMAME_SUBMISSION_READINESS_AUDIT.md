# CMAME Submission Readiness Audit

Status: **GLOBAL SUBMISSION OPEN; BOUNDED NARROWED SUBCHECK SATISFIED; FULL SOURCE-POLICY PACKAGE NOT READY**

This audit records the mechanical package boundary for the CMAME draft. It is
not a full source-policy package acceptance. The current ARS-style review is
`CMAME_REVIEW_AGENT_REPORT.md`; its top-level verdict is global and remains
`do_not_submit_global`. The narrowed formal-order/common-reference diagnostic
claim is recorded only as a bounded subsidiary subcheck while full
source-policy reproducibility and external superiority remain out of scope.

## Objective Blocker Matrix

The global objective blocker matrix remains:

- `blocker_open_by_id=OC4:True,OC6:True,OC12:True`
- `blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready`
- `blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False`

This matrix is inherited from `OBJECTIVE_COMPLETION_AUDIT.json`; it keeps
OC4, OC6, and OC12 open and does not authorize B4/source-policy execution.

Official sources checked:

- CMAME Guide for Authors:
  https://www.sciencedirect.com/journal/computer-methods-in-applied-mechanics-and-engineering/publish/guide-for-authors
- Elsevier LaTeX instructions:
  https://www.elsevier.com/en-au/researcher/author/policies-and-guidelines/latex-instructions
- University of Wisconsin-Madison contact page:
  https://www.wisc.edu/contact/

## Manuscript Package

- Master manuscript PDF: `main_cmame.pdf`
- Master manuscript source: `main_cmame.tex`
- Document class: `\documentclass[preprint,12pt]{elsarticle}`
- Journal marker: `Computer Methods in Applied Mechanics and Engineering`
- Title page: title, author, corresponding-author email, and University of
  Wisconsin-Madison affiliation with institutional postal address.
- Abstract: below 250 words.
- Keywords: 6 keywords.
- Main technical content: introduction, related work, mathematical setting,
  definitions, nomenclature, method, comparator boundary, validation protocol,
  conditional proof, numerical evidence, four-example mechanism validation,
  diagnostic evidence, limitations, conclusions, declarations, and references.

## Figures and Tables

The paper includes thirteen submission figures, all with captions and text
references:

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

The manuscript tables are editable LaTeX tables, not image tables.

## Separate Editable Files

- `highlights_cmame.txt`: separate editable highlights file with 3 to 5
  bullets and each bullet below 85 characters; the first proof-facing
  highlight foregrounds the direct 132-row 96+36 residual bridge.
- `declarations_cmame.md`: competing-interest, funding, data-availability,
  and generative-AI-use statements.
- `COVER_LETTER.md`: cover letter draft with claim boundary and non-claims.

## Flat LaTeX Source Package

Elsevier's LaTeX instructions state that Editorial Manager cannot process
LaTeX submissions that depend on subfolders. The repository copy keeps figures
under `figures/` for development, but the submission package also includes
`cmame_submission_flat/`, where the TeX source and figure files are all at the
same directory level:

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

The flat source is a submission convenience copy of `main_cmame.tex`; it does
not change the claim boundary.

## Claim Boundary

- Accepted method: `Gauss6/FullVA`.
- Accepted method order: `6`.
- Smooth observed position/velocity orders: `7.161/7.066`.
- Comparator: local paper-style `m=3` Gauss-Lobatto TFE formula target.
- Comparator expected order: `5`.
- Local method-side coverage examples: `single_pendulum`, `double_pendulum`, `four_link`,
  `slider_crank`.
- Accepted dynamic-order examples: `single_pendulum`, `double_pendulum`; the
  `four_link` and `slider_crank` rows are mechanism-coverage examples, not
  accepted dynamic-order rows.
- Explicit non-claim: `full_tfe_stage_replacement=false`.

## Read-Only Validation

Run from `paper_v047_cylindrical_chain/`:

```bash
../../.venv_sbel/bin/python validate_cmame_submission.py
../../.venv_sbel/bin/python validate_submission_bundle.py
../../.venv_sbel/bin/python validate_paper_package.py
```

Run from the parent work directory:

```bash
.venv_sbel/bin/python validate_pipeline_outputs.py
```

These checks read existing artifacts and must not invoke
`v047_cylindrical_chain_pipeline/run_v047.py`.

## Two-Tier Quality Gate

The global submission gate remains open. The package has a mechanically
complete bounded narrowed subcheck, and the full source-policy package remains
explicitly not ready:

- `bounded_narrowed_subcheck_satisfied=true`
- legacy compatibility alias only, not global readiness:
  `submission_ready_under_narrowed_claim=true`
- `mechanical_preflight_passed=true`
- `quality_review_passed_under_narrowed_claim=true`
- `full_source_policy_submission_ready=false`
- `open_narrowed_claim_blockers=0`
- `closed_narrowed_claim_blockers=B1,B2,B3,B4,B5,B6,B7,B8`

See `CMAME_SUBMISSION_READINESS_REVIEW.md` for the blocking findings.
The machine-checkable blocker ledger is
`CMAME_BLOCKER_CLOSURE_GATE.md` / `CMAME_BLOCKER_CLOSURE_GATE.json`; it keeps
the current `coarse_first_no_default_1e-4` policy explicit and records that
B1--B8 are closed for the narrowed claim while source-policy rows remain
`0/40` and full source-policy package readiness remains false. B5
is closed by `CMAME_VISUAL_LEGIBILITY_AUDIT.md` /
`CMAME_VISUAL_LEGIBILITY_AUDIT.json`; B8 is closed by
`CMAME_RELATED_WORK_AUDIT.md` / `CMAME_RELATED_WORK_AUDIT.json`. B3 is
closed by the direct residual-bridge/Kantorovich perturbation route recorded in
`B3_DIRECT_PROOF_REVIEW_AUDIT.md` / `B3_DIRECT_PROOF_REVIEW_AUDIT.json`; the
primitive/Taylor 162-subterm route remains diagnostic and open.
