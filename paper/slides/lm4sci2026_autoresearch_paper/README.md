# LM4Sci 2026 Method-Discovery Paper Draft

This directory contains an anonymized workshop-paper draft about discovering a
sixth-order `Gauss6/FullVA` Lie-group multibody integrator with a
verifier-centered LLM-assisted research pipeline. The contribution is the
method-discovery path, not automated paper writing. It is targeted at:

https://lm4sci.github.io/docs/2026/call-for-papers

Target facts checked on 2026-06-29:

- Venue: LM4Sci 2.0, co-located with COLM 2026.
- Submission type: full paper, up to 8 pages of main content.
- Template: COLM conference template.
- Review: double blind, at least three reviewers.
- Archival status: non-archival.
- Deadline listed by the site: 2026-06-28 11:59pm AOE.

Because the local checkout does not include the official COLM style file, the
current `main.tex` compiles with a fallback article preamble. If an official
`colm2026_conference.sty` file is later placed in this directory, the source
will load it automatically.

## Files

- `main.tex`: anonymized LM4Sci-directed manuscript draft focused on the
  method-discovery story.
- `references.bib`: BibTeX entries for the external work cited in the draft.
- `main.pdf`: compiled fallback-layout PDF. Current fallback build is 13 pages
  total because it includes references and a detailed appendix; main content
  remains before the references.
- `STORY_PIPELINE.md`: working guide for keeping the paper centered on how the
  new method was discovered.
- `ARGUMENT_BLUEPRINT.md`: claim-evidence map for the method-discovery
  argument and reviewer-objection handling.
- `STORYBOARD_CN.md`: Chinese paragraph-level storyboard for explaining how
  the method was discovered, with section-by-section claim guardrails.
- `DETAILED_DISCOVERY_STORY_PIPELINE_CN.md`: expanded Chinese narrative spine
  matching the intended story order: hard Lie-group integrator target,
  inherited comparators, verifier environment, four-example testbed,
  48-version hypothesis evolution, and the FullVA technical turn.
- `48_VERSION_STORY_MAP_CN.md`: Chinese version-by-version map explaining what
  each of the 48 research versions tested, ruled out, retained, or promoted,
  plus a role taxonomy and claim-state lens for compressing the history without
  losing the discovery logic.
- `STORY_REFINEMENT_AUDIT.md`: requirement-level audit for repeatedly
  optimizing the method-discovery story without drifting into unsupported
  claims.
- `MAIN_TEXT_COMPRESSION_BLUEPRINT.md`: keep/move/cut plan for compressing the
  current story into an 8-page LM4Sci/COLM-style main text while preserving the
  discovery logic and claim boundaries.
- `LM4SCI_DISCOVERY_REWRITE_PACKET.md`: reusable English section leads,
  paragraph skeletons, and forbidden rewrites for converting the story pipeline
  into compact LM4Sci main-text prose.
- `REVIEWER_STORY_QA.md`: likely reviewer questions with controlled answers,
  manuscript anchors, and forbidden wording for the method-discovery story.

## Build

From this directory:

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## Claim Boundary

The paper is framed as a method-discovery case study: the 48-version pipeline
is used to explain how the accepted `Gauss6/FullVA` path emerged from failed
and retained technical moves. It intentionally does not claim:

- global submission readiness of the separate CMAME numerical-method paper;
- complete source-paper TFE residual reproduction;
- external source-policy superiority;
- sparse runtime superiority;
- dynamic-order proof for four-link or slider-crank beyond the recorded
  coverage/consistency scope.

The main case-study evidence is taken from the local v047/v048 artifacts:

- 48 versions validated by the top-level pipeline check;
- 695 result files, including 286 CSV, 113 JSON, 202 PNG, and 90 reports;
- a 132-row FullVA residual;
- four ASME mechanisms in the method evidence system;
- accepted local dynamic-order evidence for single and double pendulum;
- coverage/consistency evidence for four-link and slider-crank;
- source-policy external rows still open at 0/40.

## Appendix Structure

The appendix expands the story pipeline beyond the 8-page-style main text:

- `Expanded 48-Version Discovery Ledger`: one concise entry for every version
  from v001 to v048, explaining how each changed the next method hypothesis.
- `48_VERSION_STORY_MAP_CN.md` provides a Chinese working version of the same
  version-by-version story for drafting and slide planning, including the role
  categories that distinguish measurement calibration, comparator rejection,
  the FullVA hinge, scaling caveats, and claim-boundary management.
- `Numerical Examples and Claim Roles`: separates the four examples into
  dynamic-order evidence versus mechanism-coverage/reaction-dynamics evidence.
- `MAIN_TEXT_COMPRESSION_BLUEPRINT.md` records which narrative elements must
  remain in the main text and which details can move to appendix or supplement
  if the official template overflows.
- `LM4SCI_DISCOVERY_REWRITE_PACKET.md` turns the same constraints into
  reusable main-text prose blocks for the abstract, introduction, related work,
  verifier environment, 48-version story, FullVA hinge, evidence boundary, and
  discussion.
- `REVIEWER_STORY_QA.md` gives reviewer-facing answers for the most likely
  challenges: not auto paper-writing, not just Gauss6, not projection, not
  all-four-example dynamic order, and not external superiority.
- `DETAILED_DISCOVERY_STORY_PIPELINE_CN.md` is the most explicit working
  narrative for repeated optimization when a section needs to be rewritten from
  the story spine rather than from the chronological ledger.
