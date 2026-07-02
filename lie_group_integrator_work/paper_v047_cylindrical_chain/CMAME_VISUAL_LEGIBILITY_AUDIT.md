# CMAME Visual Legibility Audit

Status: **B5 CLOSED - MECHANISM VISUAL REPRODUCIBILITY CHECKED**

This audit records the final-PDF visual check for the mechanism schematic
blocker in `CMAME_BLOCKER_CLOSURE_GATE.md`. It is a read-only manuscript
quality artifact. It does not invoke `run_v047.py`, v048 numerical runners, or
any default `1e-4` campaign.

## Objective Blocker Matrix

The global objective blocker matrix remains:

- `blocker_open_by_id=OC4:True,OC6:True,OC12:True`
- `blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready`
- `blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False`

This matrix is inherited from `OBJECTIVE_COMPLETION_AUDIT.json`; it keeps
OC4, OC6, and OC12 open and does not authorize B4/source-policy execution.

## Checked Artifacts

- Main PDF: `main_cmame.pdf`
- Flat submission PDF: `cmame_submission_flat/main_cmame_submission.pdf`
- Mechanism schematic: `figures/asme_lower_pair_graph_bridge.png`
- Flat mechanism schematic: `cmame_submission_flat/Figure_2_asme_lower_pair_graph_bridge.png`
- Figure generator: `generate_publication_figures.py`
- Validator: `validate_cmame_visual_legibility_audit.py`

## Figure 2 Result

The four-panel ASME-style mechanism schematic was regenerated after a label
layout pass:

- local body-frame number labels were removed where bar labels already carry
  the body identity;
- text labels use a small white backing box to avoid line/label collisions;
- the slider-crank prismatic arrow was moved below the slider label;
- the four-link driver annotation was moved away from the local frame labels;
- the regenerated Figure 2 image size is at least `2000 x 1700` pixels in both
  the normal and flat submission copies.

The compiled CMAME PDF references the regenerated mechanism schematic on the
same final page as before, and the LaTeX logs have no `Overfull`, `LaTeX
Warning`, `Package ... Warning`, or `pdfTeX warning` entries after the final
rerun.

## B5 Closure

`B5` was: mechanism visual reproducibility. Its closure requirement was to
verify final-PDF legibility or split the four ASME-style mechanism schematic
into publication-size diagrams.

Closure decision: the final PDF legibility check is recorded and the split is
not required for this blocker. This does not close the broader publication
figure-set blocker `B7`, which still requires baseline comparison figures,
clean work/precision figures, and a limitation figure.

## Remaining Gate State

- `submission_ready=false`
- `mechanical_preflight_passed=true`
- `quality_review_passed=false`
- `open_blockers=7`
- `closed_blockers=B5`
- `default_1e-4_required=false`

## Current Narrowed-Claim Override

This B5 audit is historical with respect to B7. The current narrowed-claim
package closes B7 elsewhere through `CMAME_FIGURE_SET_AUDIT.md/json` and
`CMAME_BLOCKER_CLOSURE_GATE.md/json`, while full source-policy comparison
figures remain future work.
