# Main-Text Compression Blueprint

This file is the control plan for turning the current fallback-layout draft
into an 8-page LM4Sci/COLM-style main paper without losing the
integrator-discovery-method story. It is not submission evidence and does not
add claims. It tells future edits what to keep, what to move to appendix, and
what to cut first.

## Venue-Facing Framing Check

Checked against the official LM4Sci 2026 CFP on 2026-06-29: the venue asks for
full papers with up to 8 pages of main content in the COLM template, and its
scope includes LLM agents for complex scientific workflows, end-to-end research
assistants, careful evaluation of AI-generated research artifacts, and
quantitative, symbolic, or physics-based reasoning in scientific foundation
models. This paper should therefore be framed as a verifier-centered method
for discovering new integrators. The venue fit is strongest when the paper
answers how an AI-assisted research environment discovered and bounded a new
integrator through typed verifiers and versioned constraints; it is weakest
when the draft sounds like a paper mainly describing the final integrator,
automatic paper generation, generic workflow automation, or broad claims about
autonomous science.

## Compression Objective

The main text must still answer the seven story-pipeline questions:

1. Why is constrained Lie-group multibody integration hard?
2. What prior methods, code paths, and baselines were inherited?
3. How was the verifier environment set up?
4. What do the four numerical examples test?
5. How did the work evolve through 48 versions?
6. What are all 48 versions or version blocks about?
7. Which technical turn produced the discovered integrator?
8. What general discovery method does the verifier trace support?

The compressed version should read as a paper about a method for discovering
new integrators, not as a paper about automated paper writing, a paper mainly
describing one integrator, or a numerical-method superiority claim.

## Current Compression Status

The fallback-layout PDF is currently 14 pages after the latest story-continuity
pass. Recent passes added the compact v023-v029 failure-to-constraint trace,
consolidated failed attempts, discussion, limitations, and conclusion into one
closing block, and then inserted a short five-block narrowing chain plus a
reusable version-reading rule into the main text. The story section now also
contains a local `Verifier setup` paragraph before the four-example testbed, so
the main narrative follows the requested sequence directly. The current opening
order is a protected structure: hard Lie-group constrained integration first,
claim-drift risk second, inherited typed verifier questions third, verifier
environment and four-example testbed fourth, then 48-version evolution,
role-coded ledger meaning, and the FullVA discovered outcome, and only then broader
LLM-for-science motivation.
Future cuts should shorten wording inside that order, not reorder it around
generic LLM motivation or artifact volume. The detailed Chinese pipeline now
includes a paragraph-level playbook for this exact order; use it together with
the root order contract in `STORY_PIPELINE.md` before deleting or moving any
abstract, introduction, discovery, method, evidence, or closing paragraph.
For direct prose replacement, use `LM4SCI_DISCOVERY_REWRITE_PACKET.md`; it
turns this keep/move/cut policy into reusable English paragraph skeletons and
forbidden rewrites.

## Keep / Move / Cut Policy

| Priority | Content | Main-text decision | Reason |
| --- | --- | --- | --- |
| P0 keep | Hard numerical target and claim boundary | Keep in abstract/introduction. | Without this, reviewers read the work as generic agent automation. |
| P0 keep | FullVA hinge: v023-v029 endpoint repair -> in-residual V/A rows | Keep in main text with the pivot table or a compressed equivalent. | This is the discovered integrator outcome that stress-tests the discovery method. |
| P0 keep | Four-example verifier ladder and boundaries | Keep a compact table. | It prevents overclaiming that all four examples prove dynamic order. |
| P0 keep | 48-version discovery spine and ledger-role table | Keep at least one visual/table in main text. | It explains why 48 versions are scientific narrowing, not prompt attempts. |
| P1 keep | Verifier promotion rule and verdict-to-constraint logic | Keep in compressed prose or one table. | It explains how failures became next-version constraints. |
| P1 move | Full one-version-per-entry ledger | Move to appendix/supplement. | Necessary detail, but too expensive for 8-page main text. |
| P1 move | Full artifact counts and file-type inventory | Mention once, move details to appendix. | Supports durability but is not the scientific hinge. |
| P2 cut | Generic LLM-for-science exposition | Compress to one paragraph after numerical comparators. | Related work should serve the claim-preserving gap. |
| P2 cut | Sparse/backend details beyond claim boundary | Keep only the caveat sentence/table row. | Sparse speed is open, not the method contribution. |
| P2 cut | External same-test/source-policy details | Keep only the nonclaim boundary. | External superiority is not claimed. |
| P2 cut | Repeated statements of the same nonclaims | Keep one claim snapshot and one limitations paragraph. | Boundaries must be clear but not duplicated. |

## Target Main-Text Architecture

| Section | Target role | Target length | Must preserve |
| --- | --- | --- | --- |
| Abstract | One-paragraph discovery-method summary. | 180-230 words | Discovery method, hard target, 48 versions, FullVA hinge, four-example boundary, nonclaims. |
| Introduction | Motivate difficult numerical target and precise contribution. | 0.9-1.1 pages | Three claims; not auto-paper-writing; conditional sixth-order `Gauss6/FullVA`. |
| Related Work and Gap | Typed numerical comparators first, LLM-for-science second. | 0.8-1.0 pages | Comparator table or compressed equivalent; claim-preserving method-discovery gap. |
| How the Method Was Discovered | Seven-question story contract plus 48-version spine. | 1.4-1.7 pages | What a version means; discovery-spine figure; ledger-role table. |
| Discovery Environment | Verifier objects and claim promotion. | 0.9-1.1 pages | MethodSpec/ProblemSpec/EvidenceSpec/ClaimSpec/Ledger; verdict-to-constraint rule. |
| New Method | Endpoint repair to FullVA. | 1.2-1.5 pages | v023-v029 pivot; FullVA is in-residual, not projection; sixth-order boundary. |
| Numerical Evidence | Four-example verifier ladder and claim snapshot. | 1.0-1.2 pages | Single/double dynamic order; four-link/slider-crank coverage only. |
| Failed Attempts / Discussion / Limitations / Conclusion | Consolidated close. | 0.9-1.1 pages | Failed paths as verifier rules; single-case limitation; no TFE/sparse/external overclaim. |

## User-Order Preserving 8-Page Rewrite Queue

Use this table as the concrete rewrite order when converting the 13-page
fallback manuscript into an 8-page main paper. Each row protects one part of
the user's intended story. Compression may shorten the carrier, but it should
not remove the role or change the order.

| Queue | Story requirement | Keep in main text | Move or cut first | Must not lose |
| --- | --- | --- | --- | --- |
| 1 | Lie-group constrained integration is hard because method identity is fragile. | One opening paragraph naming manifold rotations, constrained DAE levels, lower-pair multipliers/reactions, friction smoothness, residual-row identity, projection drift, and reference-policy drift. | Long general introductions to MBD, LLMs, or scientific discovery. | The problem is not merely "complex"; the hard object is the identity of the one-step residual being solved. |
| 2 | Prior work already existed and had specific partial roles. | A compressed typed-comparator table or paragraph: Lie kinematics, conservative Gauss mechanics, ASME examples, trapezoidal/BDF/Lobatto, TFE target, friction variants, sparse/backend probes, and external harnesses. | Generic related-work exposition and leaderboard-style comparisons. | Prior work initialized constraints and rejected explanations; it did not already contain the final `Gauss6/FullVA` method. |
| 3 | The verifier environment was set up before claims were promoted. | A short `MethodSpec`/`ProblemSpec`/`EvidenceSpec`/`ClaimSpec`/ledger paragraph plus one verdict-to-next-constraint rule. | Full artifact inventories, repeated workflow diagrams, and redundant table prose. | Failed runs must become narrower next-version constraints instead of publishable claims. |
| 4 | Four numerical examples are a test environment. | One compact verifier-ladder table: single and double pendulum are local dynamic-order gates; four-link and slider-crank are mechanism coverage and reaction-consistency gates. | Extra demo descriptions, screenshots, or repeated numerical setup text. | Do not imply all four examples prove asymptotic dynamic order. |
| 5 | The work evolved through 48 versions. | One five-block narrowing paragraph and either the discovery-spine figure or a compressed role taxonomy. | One-version-per-row main-text narration, repeated artifact counts, and chronological prose that does not explain claim movement. | A version is a bounded research contract: hypothesis, artifacts, verifier verdict, next constraint, and claim-state movement. |
| 6 | What all 48 versions are about. | A role-coded summary in main text plus a pointer to appendix/supplement for v001-v048. | Full appendix entries if the official template counts them against the main text; move them out of main content. | The reader must still see representation calibration, constraint identity, comparator separation, FullVA hinge, scaling, lower-pair breadth, and claim-boundary management. |
| 7 | The technical turn that produced the new method. | Keep the v023-v029 FullVA hinge table or an equally explicit paragraph: endpoint node swap and projection repair were rejected; lower-pair velocity/acceleration rows moved into the Gauss6 stage residual. | Sparse/backend details, external same-test policy, and TFE-reproduction discussion. | The accepted method is stage-level in-residual `Gauss6/FullVA`, not output projection, not sparse speedup, and not a full TFE replacement. |
| 8 | The final claim boundary. | One claim-state snapshot and one limitations paragraph. | Duplicate nonclaim warnings scattered across sections. | Conditional sixth-order evidence is local to accepted single/double pendulum gates; four-link/slider-crank support coverage/reaction consistency; no seventh-order theorem, sparse superiority, or external superiority. |

## If The Official Template Overflows

Apply cuts in this order:

1. Remove duplicate prose around the seven-question story contract; keep the
   questions, not the explanatory repetition.
2. Compress the abstract/introduction only inside the current opening order:
   hard target, claim drift, typed verifier questions, verifier/test environment,
   48-version emergence, FullVA claim.
3. Check the paragraph-level playbook in
   `DETAILED_DISCOVERY_STORY_PIPELINE_CN.md` and the root dependency chain in
   `STORY_PIPELINE.md` before moving material across sections; compression may
   shorten a role but should not swap the role order.
   For any large rewrite, first compare the proposed opening against the
   continuous Chinese narration script in `DETAILED_DISCOVERY_STORY_PIPELINE_CN.md`;
   the compressed text should still tell the same story even if it uses fewer
   tables.
   Then use `LM4SCI_DISCOVERY_REWRITE_PACKET.md` for section leads or compact
   replacement paragraphs rather than inventing a new order.
4. Compress the related-work LLM paragraph to one citation-packed paragraph;
   preserve the typed numerical comparator logic.
5. Merge the durable-object table and claim-promotion prose into one compact
   paragraph if tables become too expensive.
6. Keep either the verdict-to-constraint table or a three-sentence prose
   version; do not remove the logic entirely.
7. Compress the claim-state snapshot table to four rows: accepted method,
   four-example roles, full TFE open, sparse/external open or forbidden.
8. Move sparse/backend and external harness details to appendix.
9. Keep the already consolidated Discussion/Limitations/Conclusion close; do
   not re-expand failed paths into a second narrative.
10. Only if still over budget, replace the full 48-version hypothesis table
   with the role taxonomy from `48_VERSION_STORY_MAP_CN.md`.

Do not cut the FullVA hinge table before cutting generic related-work prose,
artifact counts, sparse details, or external-harness detail. Do not cut the
four-example boundary table before cutting the claim snapshot.

## One-Page Story Skeleton

The compressed paper should still be explainable in this sequence:

1. Constrained Lie-group MBD is difficult because manifold transport,
   index-3 constraints, lower-pair multipliers, friction smoothness, Newton
   residual identity, endpoint repair, and reference policy can silently change
   the one-step map being tested.
2. The project inherited useful but incomplete comparators: Lie kinematics,
   conservative Gauss mechanics, ASME mechanisms, trapezoidal/BDF/Lobatto
   baselines, TFE targets, friction variants, and external harnesses.
3. The agent environment separated `MethodSpec`, `ProblemSpec`,
   `EvidenceSpec`, `ClaimSpec`, and ledgers so that a run could fail without
   becoming a false claim.
4. The four examples formed a verifier ladder: single and double pendulum
   support accepted local dynamic order; four-link and slider-crank support
   closed-loop lower-pair coverage and reaction consistency.
5. The 48 versions were a narrowing process: calibrate representation,
   inherit baselines, split constraint identities, keep Gauss6, reject
   endpoint-node/projection explanations, discover FullVA, then manage scaling
   and external claim boundaries.
6. The new method was discovered at the FullVA hinge: lower-pair velocity and
   acceleration consistency moved from endpoint repair into the Gauss6 stage
   residual.

## Reviewer-Risk Checklist

Before considering the compressed main text stable, scan for these risks:

- Does any sentence imply all four examples prove dynamic order?
- Does any sentence imply observed `7.161/7.066` is a seventh-order theorem?
- Does any sentence imply full TFE replacement is accepted?
- Does any sentence imply sparse speedup or external superiority?
- Does any section make the work sound like automated paper generation rather
  than method discovery?
- Does the compressed version still explain why failed versions are evidence?

If any answer is wrong, the compression has broken the story pipeline.
