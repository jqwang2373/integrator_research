# Story Refinement Audit

This audit tracks whether the current LM4Sci draft answers the
integrator-discovery-method story requirements: why Lie-group integration is a
hard discovery target, what prior work existed, how the verifier environment
was set up, what the four examples test, how the work evolved through 48
versions, which technical move created the discovered integrator, and what
general discovery method the verifier trace supports. It is a working control
document, not submission prose.

## Current Verdict

The story is now materially aligned with the intended integrator-discovery
method frame.
The manuscript no longer reads primarily as "auto research writes a paper";
it reads as a verifier-centered procedure for discovering a new integrator,
with conditional sixth-order `Gauss6/FullVA` as the bounded discovered outcome.
The related-work opening has been compressed so
that it now opens with numerical-method inheritance and typed verifier questions
before moving to LLM-for-science motivation and the claim-preserving
method-discovery gap; it now also states that inherited work initialized the
search constraints rather than merely serving as background citations. The draft
also has a compact discovery-spine figure and a
role-coded 48-version table that explains what each block contributed to the
method hypothesis; the `What a version means` paragraph now defines a version
as a state transition from candidate explanation to artifacts, verifier
verdict, next constraint, and claim-state movement. Local float placement now
keeps the discovery
artifacts, verifier-environment artifacts, and method example/claim tables near
their intended narrative sections. The method pivot table has also been
narrowed to the v023-v029 FullVA hinge, so it explains how endpoint repair
became stage-level velocity/acceleration residuals instead of repeating the
full ledger. The four-example section now frames the numerical
examples as a verifier ladder rather than interchangeable demos: single/double
pendulum are order gates, while four-link/slider-crank are coverage and
reaction-consistency gates. The section also states that the examples were
selected by the ambiguity they expose--clean order, interbody transfer, loop
closure, and mixed lower-pair coverage--so the test environment supports
different claim types without implying one flat proof obligation. The verifier
environment now includes an explicit claim-promotion checklist covering method
identity, problem identity, evidence artifacts, and wording boundary, plus a
verdict-to-constraint table that shows how failed promotions became narrower
next-version constraints; it now also names the three locks used to initialize
the environment: identity, evidence, and claim wording. The failed-paths
discussion has been reframed as verifier rules rather than another version
recap. The latest main-text refinement adds a compact v023-v029 trace showing
how Lobatto-node replacement and projection were rejected, how the next
constraint became in-residual velocity/acceleration rows, and how the FullVA
identity survived the interbody double-revolute test. The latest compression
pass then merged failed-paths prose with discussion, limitations, and
conclusion so that negative evidence is stated once as reusable verifier rules.
The latest story-continuity pass then pushed the Chinese three-depth narration
into the main text without increasing the fallback page count: the introduction
now names the five-block narrowing chain, and the discovery section gives a
reusable reading rule for any version--what it made measurable, what it
rejected, what it preserved, and which claim state it changed. The newest
story-order pass also adds a dedicated `Verifier setup` paragraph inside
`How the Discovery Method Was Built`, so the local narrative now follows the
user's requested order directly: hard problem, inherited baselines, verifier
state machine, four-example test environment, 48-version evolution, and FullVA
technical turn.
The strongest remaining drafting need is still compression: the fallback PDF is
14 pages, and the main body still carries more explanatory scaffolding than an
8-page workshop main text can hold. The Chinese 48-version story map now also
includes a role taxonomy, claim-state lens, reusable version grammar, and a
three-depth narration layer for 30-second opening, 2-minute introduction/slide,
and reviewer-deep answers, so future compression can explain the 48 versions by
discovery role rather than by chronology alone. A dedicated
`MAIN_TEXT_COMPRESSION_BLUEPRINT.md` now records the keep/move/cut order for
an 8-page LM4Sci/COLM-style main text; it now also contains a
venue-facing framing check and a user-order-preserving rewrite queue that maps
each required story role to what must remain in the compressed main text, what
can move to appendix, and what wording boundary must not be lost.
`LM4SCI_DISCOVERY_REWRITE_PACKET.md` now converts that order into reusable
English main-text prose: abstract and introduction skeletons, typed verifier-question
related-work prose, verifier-state paragraphs, a compact 48-version story,
the v023-v029 FullVA hinge paragraph, evidence-boundary prose, and forbidden
rewrite patterns.
`REVIEWER_STORY_QA.md` now turns the
same story into likely reviewer questions with controlled answers and
forbidden-wording checks. `DETAILED_DISCOVERY_STORY_PIPELINE_CN.md` now gives
the most explicit Chinese narrative spine for repeated optimization: hard
problem first, inherited typed verifier questions second, verifier environment third,
four-example testbed fourth, 48-version hypothesis evolution fifth, and the
FullVA technical turn as the method-discovery center. It now also contains a
continuous Chinese narration script that tells the whole story in order, plus a
paragraph-level main-text playbook that assigns each abstract/introduction,
discovery, environment, method, evidence, and closing block a required role,
forbidden overclaim, and current `main.tex` anchor. `ARGUMENT_BLUEPRINT.md`
now mirrors this as a story-pipeline dependency chain, making explicit that the
hard target enables typed verifier questions, typed verifier questions enable verifier setup,
verifier setup enables the four-example test environment, and only then can the
48-version ledger justify the FullVA technical turn and claim boundary.
`STORY_PIPELINE.md`, the root story blueprint, now carries the same
order-dependency test and updates the recommended main-paper structure so
Related Work starts from numerical typed verifier questions before LLM workflow
motivation. It now also contains a `Canonical Story Pass` that walks the reader
from hard numerical target through inherited partial objects, verifier setup,
four-example testbed, 48-version evolution, all-version role blocks, the
FullVA hinge, and claim boundary; and a `Repeated Optimization Loop` that
requires order, evidence-role, version-meaning, FullVA-hinge, and boundary
passes after every compression or template rewrite. The latest main-text pass
has pushed that spine into the manuscript entrance: the abstract now follows the
dependency chain from hard target to inherited typed verifier questions, verifier test
environment, 48-version ledger, FullVA hinge, and nonclaims; the introduction now
walks from hard target and claim-drift risk to inherited typed verifier questions,
verifier state, four-example testbed, and 48-version narrowing before introducing
broader LLM-for-science motivation; and the discovery section now says that
method, problem, evidence, and claim identities evolved together across the 48
versions.
The current first-page story order is therefore locked as a guardrail for later
compression: hard numerical target first, claim-drift risk second, inherited
typed verifier questions third, verifier environment and four-example testbed fourth,
then the 48-version evolution and FullVA discovered outcome before broader LLM
motivation.

## Requirement Coverage

| User story requirement | Current manuscript evidence | Status | Next optimization |
| --- | --- | --- | --- |
| Explain why Lie-group constrained MBD integration is hard. | Abstract and Introduction open with manifold rotations, index-3 DAE constraints, lower-pair multipliers, friction regimes, Newton residual identity, endpoint repair/reference-policy drift, and the risk that a candidate silently becomes a different one-step map. | Strong. | Keep this as the opening; do not let LLM-for-science motivation precede it. |
| Explain what prior/inherited work existed. | Related Work now opens with numerical-method inheritance and typed verifier questions for Lie kinematics, conservative Gauss mechanics, ASME mechanisms, trapezoidal/BDF/Lobatto, TFE target, friction variants, and external harnesses; it explicitly says these initialized representation, baseline, rejected-explanation, and comparison-boundary constraints before introducing the LLM-for-science gap; the discovery section now maps these question types directly to ledger dependencies: v001--v003 representation anchors, v004--v025 comparable/rejectable baselines, v019--v029 lower-pair/friction stressors toward FullVA identity, and v030--v048 sparse/external boundary management. | Strong. | Preserve the verifier-question table, initialization sentence, and ledger-shape bridge during compression. |
| Explain how the verifier environment was set up. | The discovery section now has a compact `Verifier setup` paragraph before the four-example paragraph and states that a run returns a typed next constraint rather than a hidden score; the later Discovery Environment section defines MethodSpec, ProblemSpec, EvidenceSpec, ClaimSpec, Ledger, a four-part claim-promotion checklist, identity/evidence/claim locks, per-example gate roles, a verdict-to-next-constraint table, L0-L3 sandboxes, and claim states; its table/figure now appear before the method section in the extracted PDF text. | Strong. | Preserve the typed-constraint sentence during compression; add artifact-path examples only in appendix or supplemental material. |
| Explain four numerical examples as a test environment. | Abstract, introduction, `How the New Method Was Discovered`, and `Numerical test environment` now all separate the single/double dynamic-order rows from four-link/slider-crank closed-loop coverage and reaction consistency; the introduction now states that a failed rung returns a typed next constraint (method order, reference policy, loop closure, or lower-pair coverage) rather than one hidden score; the numerical section states that each rung has its own ProblemSpec, EvidenceSpec, ClaimSpec, verifier gate, and ambiguity target. | Strong. | Keep single/double order gates distinct from four-link/slider-crank coverage and reaction gates. |
| Explain how the work evolved to 48 versions. | Main text now gives a five-block narrowing chain in the introduction, defines each version as a state transition with candidate explanation, artifacts, verifier verdict, next constraint, and claim-state movement, gives a reusable reading rule, and states that retained versions calibrate measurements, reject explanations, promote components, or quarantine caveats; it now also says the version blocks are ordered dependencies rather than topical bins. Appendix expands v001-v048 one by one. The figure/table are now kept before the next section by `\FloatBarrier`. | Strong but space-heavy. | Preserve the five-block chain, state-transition grammar, ordered-dependency sentence, figure, and role-coded table; trim repeated prose around them first. |
| Explain what all 48 versions are about. | Main text and appendix now share the same reading rule: each retained version calibrated a measurement, rejected an explanation, promoted a component, or quarantined a caveat; the main table groups them into A-I roles covering measurement, clean mechanics, constraint identity, comparator separation, FullVA hinge, scaling, lower-pair breadth, and claim-boundary management; `48_VERSION_STORY_MAP_CN.md` gives a Chinese version-by-version drafting map, reusable version grammar, role/claim-state classifications, three-depth narration, and reusable English causal block paragraphs for opening, slides, reviewer answers, or compressed main text. | Strong. | Future optimization can replace some appendix text with the 30-second, 2-minute, or causal-block narrative if page pressure matters. |
| Explain which technical move created the discovered integrator. | `Discovered Integrator Outcome: From Endpoint Repair to FullVA` and the narrowed v023-v029 pivot table state that endpoint repair was rejected and stage-level FullVA velocity/acceleration rows became method-defining inside the case. | Strong. | Keep this before sparse/external comparison details. |
| Avoid overclaiming. | Claim-state snapshot, limitations, and guardrail wording block full TFE replacement, external superiority, sparse speed win, and closed-loop dynamic-order promotion. | Strong. | Continue scanning for forbidden positive claims after each edit. |

## Original User-Order Trace

This table tracks the story in the same order as the originating request. It is
stricter than the section audit: a future rewrite can be shorter, but it should
not change this order or merge distinct evidence types.

| User-order item | Current main-text carrier | Supporting control artifact | Current risk |
| --- | --- | --- | --- |
| 1. Lie-group integrator is generally hard because the method is complex. | `main.tex:60-64`, `main.tex:88-99`, and `main.tex:279-290` state manifold kinematics, constrained DAE levels, lower-pair multipliers, friction, Newton residual identity, projection/reference drift, and different-one-step-map risk. | `DETAILED_DISCOVERY_STORY_PIPELINE_CN.md` "第一部分"; `STORY_PIPELINE.md` "Why The Problem Is Hard". | If the opening is compressed too hard, this can collapse into a generic "MBD is hard" claim rather than a method-identity argument. |
| 2. Previous things existed and did specific partial jobs. | `main.tex:111-118` introduces inherited objects; `main.tex:171-220` gives the typed verifier-question table and boundaries; `main.tex:292-302` restates inherited baselines inside the discovery story and maps them to ledger blocks. | `DETAILED_DISCOVERY_STORY_PIPELINE_CN.md` "第二部分"; `48_VERSION_STORY_MAP_CN.md` comparator/backbone blocks. | Do not turn this into a normal related-work list or a leaderboard; the key is what each inherited object could and could not prove. |
| 3. The research environment/verifier was set up before claims were promoted. | `main.tex:120-128`, `main.tex:304-310`, and `main.tex:436-549` define MethodSpec/ProblemSpec/EvidenceSpec/ClaimSpec/Ledger, typed next constraints rather than hidden scores, promotion checks, locks, verdict-to-constraint translation, L0-L3 sandbox levels, and claim states. | `DETAILED_DISCOVERY_STORY_PIPELINE_CN.md` "第三部分"; `STORY_PIPELINE.md` "Research Environment". | Tables may be expensive in an 8-page version; preserve at least the promotion rule and verdict-to-next-constraint logic. |
| 4. Four numerical examples are a test environment, not just final demos. | `main.tex:70-82`, `main.tex:125-128`, `main.tex:312-321`, and `main.tex:627-685` separate single/double dynamic-order gates from four-link/slider-crank coverage and reaction-consistency gates. | `DETAILED_DISCOVERY_STORY_PIPELINE_CN.md` "第四部分"; `ARGUMENT_BLUEPRINT.md` CER 3. | The strongest recurring risk is accidental wording that implies all four examples prove the same dynamic-order theorem. |
| 5. The work evolved to 48 versions. | `main.tex:130-139` gives the five-block narrowing chain; `main.tex:323-338` defines a version as candidate explanation, artifacts, verdict, next constraint, and claim-state movement, then names the four retention verbs: calibrate, reject, promote, quarantine; `main.tex:340-432` gives the discovery spine/table. | `48_VERSION_STORY_MAP_CN.md` 30-second, 2-minute, reviewer-deep, and causal-block versions. | The version count should not read as volume, persistence, or prompt attempts; it must read as narrowing evidence. |
| 6. What all 48 versions are about. | `main.tex:323-338` and `main.tex:340-414` compress the 48 versions into ledger roles and give the calibrate/reject/promote/quarantine reading key; `main.tex:775-1030` gives one concise entry for v001-v048. | `48_VERSION_STORY_MAP_CN.md` version-by-version map; `DETAILED_DISCOVERY_STORY_PIPELINE_CN.md` continuous narration script. | The appendix is detailed but page-heavy; if shortened, preserve the role taxonomy and point to the full ledger. |
| 7. Which technical turn produced the discovered integrator. | `main.tex:419-432` shows the v023-v029 failure-to-constraint trace; `main.tex:561-624` states that Gauss6 was the backbone and stage-level FullVA V/A residual rows were the method-defining turn. | `ARGUMENT_BLUEPRINT.md` CER 2; `DETAILED_DISCOVERY_STORY_PIPELINE_CN.md` "第六部分"; `48_VERSION_STORY_MAP_CN.md` FullVA hinge block. | Do not let sparse/backend/TFE/external material appear to be the discovered integrator; those are boundary-management paths. |
| 8. Final boundary and discovery-method lesson. | `main.tex:696-701`, `main.tex:706-741`, and `main.tex:743-759` separate accepted, open, and forbidden claims, then generalize only to verifier-centered integrator discovery. | `REVIEWER_STORY_QA.md`; `MAIN_TEXT_COMPRESSION_BLUEPRINT.md` reviewer-risk checklist. | Keep the bounded local claim: conditional sixth-order `Gauss6/FullVA`, not full TFE replacement, sparse speed, external superiority, seventh-order theorem, all-four dynamic order, or paper-as-integrator-description scope. |

## Evidence Anchors

This matrix records the current source anchors that prove the story pipeline is
represented in the manuscript. Recheck these anchors after any compression
pass; if an anchor is removed, the replacement must carry the same role.

| Requirement | Current source anchors | Supporting control artifact | Compression risk |
| --- | --- | --- | --- |
| Hard Lie-group integrator target | `main.tex:88-99` opens with manifold rotations, constrained DAE levels, lower-pair reactions, friction smoothness, Newton residual identity, and reference-policy failure modes; `main.tex:279-290` now states that moving V/A rows outside Newton, endpoint projection, residual substitution, or reference drift can silently change the one-step map. | `STORY_PIPELINE.md` "Why The Problem Is Hard"; `MAIN_TEXT_COMPRESSION_BLUEPRINT.md` P0 hard-target keep rule. | Do not let LLM-for-science motivation precede this in the final main text. |
| Prior/inherited work | `main.tex:111-118` lists inherited objects as typed verifier questions and distinguishes reproduction, surrogates, source-paper targets, and public same-test rows; `main.tex:171-184` states that prior work initialized search constraints and now translates each comparator into a verifier question; `main.tex:185-220` gives typed verifier questions and boundaries; `main.tex:292-303` maps question types to ledger blocks. | `STORY_PIPELINE.md` "Prior Work And Inherited Baselines"; `48_VERSION_STORY_MAP_CN.md` role taxonomy; `DETAILED_DISCOVERY_STORY_PIPELINE_CN.md` comparator spine and prior-to-version bridge. | If the verifier-question table is compressed, preserve the initialization sentence, boundary column logic, comparator-to-verifier-question rule, and ledger-shape bridge. |
| Verifier environment | `main.tex:120-128` introduces method/problem/evidence/claim/ledger objects and the four-example test environment; `main.tex:304-310` adds the local `Verifier setup` bridge in the discovery story; `main.tex:436-468` defines state objects, claim-promotion checks, and identity/evidence/claim locks, including per-example gate roles; `main.tex:470-491` gives durable objects; `main.tex:496-530` maps verifier verdicts to next-version constraints; `main.tex:535-549` defines sandbox levels and reversible claim states. | `STORY_PIPELINE.md` "Research Environment"; `MAIN_TEXT_COMPRESSION_BLUEPRINT.md` P1 verifier keep rule; `DETAILED_DISCOVERY_STORY_PIPELINE_CN.md` verifier-state-machine section plus three-lock environment setup. | If tables are cut, retain method identity, problem identity, evidence artifact, gate role, and wording-boundary checks in prose. |
| Four numerical examples as test environment | `main.tex:70-82` and `main.tex:125-128` separate single/double dynamic order from four-link/slider-crank coverage; `main.tex:312-321` now frames the examples as an ordered ambiguity ladder, says a rung returns a gate-specific verdict rather than one hidden score, and blocks transfer of an order claim to coverage gates; `main.tex:627-685` gives the verifier ladder, assigns each rung its own specs, names clean order/interbody transfer/loop closure/mixed lower-pair ambiguity targets, and separates dynamic order from mechanism coverage. | `STORY_PIPELINE.md` "Four Numerical Examples"; `ARGUMENT_BLUEPRINT.md` CER 3; `DETAILED_DISCOVERY_STORY_PIPELINE_CN.md` four-example section. | Never compress into language implying all four examples prove asymptotic dynamic order or a single scoreboard. |
| 48-version evolution | `main.tex:130-139` gives the five-block narrowing chain and says failed explanations became next-version constraints; `main.tex:323-340` defines a version as a state transition and requires the reader to ask which ambiguity was removed, which object was preserved or demoted, and which next hypothesis became legal or forbidden; `main.tex:340-432` gives the discovery spine, A-I role-coded table, and v023-v029 failure-to-constraint trace. | `48_VERSION_STORY_MAP_CN.md` full version map plus role, claim-state, version-grammar, and 30-second/2-minute/reviewer-deep narration lenses; `DETAILED_DISCOVERY_STORY_PIPELINE_CN.md` hypothesis-evolution section. | Preserve at least one main-text visual/table explaining the narrowing process and the three-question version-reading rule. |
| What all 48 versions are about | `main.tex:323-338` and `main.tex:340-414` summarize the block roles from measurement calibration through claim-boundary management; `main.tex:775-1030` gives one concise appendix entry per version, with the same calibrate/reject/promote/quarantine reading key stated before the map. | `48_VERSION_STORY_MAP_CN.md` version-by-version map, three-depth compression templates, and reusable causal block paragraphs; `MAIN_TEXT_COMPRESSION_BLUEPRINT.md` role-based replacement option. | If appendix is shortened, keep the role taxonomy, the 2-minute causal block narrative, and a pointer to the full ledger. |
| New-method technical turn | `main.tex:563-572` states why this was not simply "try Gauss6"; `main.tex:574-606` records the v023-v029 FullVA hinge; `main.tex:608-614` states the three-gate filter after v025: same Gauss6 stage solve, missing lower-pair V/A rows inside the MethodSpec, and off-axis/interbody survival without reference-policy drift; `main.tex:618-636` defines the accepted `Gauss6/FullVA` method identity and adds the key criterion that FullVA is not a generic small-residual solve: the accepted position/velocity/acceleration rows must belong to the same MethodSpec. | `ARGUMENT_BLUEPRINT.md` CER 2; `48_VERSION_STORY_MAP_CN.md` v023-v029 rows; `DETAILED_DISCOVERY_STORY_PIPELINE_CN.md` FullVA hinge section. | Do not weaken this before cutting generic related work, sparse detail, or external-harness detail. |
| Claim boundaries and nonclaims | `main.tex:696-701` gives claim-state snapshot; `main.tex:706-741` turns failed attempts into verifier rules; `main.tex:743-759` consolidates discussion, limitations, and conclusion. | `MAIN_TEXT_COMPRESSION_BLUEPRINT.md` reviewer-risk checklist; this audit's nonclaim guardrails. | Scan after every edit for forbidden positive claims around TFE, sparse speed, external superiority, and four-link/slider-crank order. |

## Section-Level Audit

| Section | Current role | Risk |
| --- | --- | --- |
| Opening story order | The first page now moves from hard Lie-group constrained integration to claim drift, inherited typed verifier questions, verifier-controlled state, four-example testbed roles, and 48-version emergence before the broader LLM-for-science motivation. | Future abstract/introduction cuts must not let generic LLM-for-science motivation or artifact counts precede the numerical target. |
| Abstract | Correctly starts from the hard numerical target, then names inherited typed verifier questions, verifier-controlled four-example roles, the 48-version ledger, the FullVA hinge, and nonclaims. | Still dense, but now aligned with the required discovery order. |
| Introduction | Strongly reframed around hard target, claim drift, inherited typed verifier questions, verifier-controlled claim states, four-example testbed roles, and a five-block 48-version narrowing chain; the LLM-for-science paragraph now follows that numerical-method dependency chain. | Could be shortened when adapting to COLM template. |
| Related Work and Gap | Now starts from numerical-method verifier questions and explicitly says inherited work initialized representation, baseline, rejected-explanation, and comparison-boundary constraints before using LLM-for-science work to motivate the claim-preserving method-discovery gap. | Further cuts should avoid removing the verifier-question table or the initialization sentence. |
| How the Discovery Method Was Built | Answers the story questions in the requested order, now including a local `Verifier setup` paragraph before the four-example testbed; defines the version unit as a state transition with claim-state movement; adds a reusable version-reading rule; introduces the discovery-spine figure; and frames the 48-version table as A-I discovery roles rather than a chronology-first ledger. | Strong; remaining issue is page economy. |
| Discovery Environment | Clear verifier/state-machine framing plus an explicit promotion checklist, identity/evidence/claim locks, and verdict-to-constraint rule; the generic loop figure was removed after the verdict table made the mechanism more explicit. | Tables may be costly in 8-page form; preserve the promotion/verdict logic if forced to choose. |
| Discovered Integrator Outcome | Correctly centers the FullVA turn as the bounded discovered outcome; the pivot table now zooms into v023-v029 instead of replaying the full 48-version history. | Sparse/external material should remain secondary. |
| Numerical Test Environment | Four-example boundary is now explicit and framed as a verifier ladder rather than a list of demos; it now says each rung carries its own specs and ambiguity target, so complexity does not automatically widen the theorem. | Do not merge order gates with coverage/reaction gates during compression. |
| Failed Attempts / Discussion / Limitations | Failed attempts now read once as verifier rules: identity before score, repair before mechanism, evidence type before promotion, and policy before comparison. Discussion, limitations, and conclusion are consolidated after those rules. | Stronger and less repetitive; remaining issue is broader page-budget compression. |

## Story-Order Gate

Before any substantial rewrite or compression, the first-page sequence must
remain: hard Lie-group constrained integrator target, claim-drift risk,
inherited typed verifier questions, verifier-controlled state, four-example testbed,
48-version narrowing, and only then broader LLM-for-science motivation. If LLM
automation, artifact counts, paper-writing, sparse speed, external comparison,
or generic agent language appears before that sequence, the rewrite has broken
the user's intended story pipeline.

## Nonclaim Guardrails

Keep these boundaries unchanged unless new artifacts close the corresponding
gate:

- Do not claim complete source-paper TFE residual reproduction.
- Do not claim external source-policy superiority.
- Do not claim sparse wall-clock speed superiority.
- Do not claim four-link or slider-crank accepted asymptotic dynamic order.
- Do not claim order above six from the finite-window `7.161/7.066` slopes.
- Do not call the paper package submission-ready without the separate critical
  submission-readiness review.

## Next Best Edits

1. Preserve the four-example verifier-ladder table until the final version; it is the
   clearest defense against reviewer overinterpretation.
2. If more compression is needed, follow `MAIN_TEXT_COMPRESSION_BLUEPRINT.md`:
   reduce generic ledger prose, artifact counts, sparse/backend detail, and
   external-harness detail before weakening the FullVA hinge or four-example
   boundary.
3. Use the `User-Order Preserving 8-Page Rewrite Queue` in
   `MAIN_TEXT_COMPRESSION_BLUEPRINT.md` before any large main-text rewrite. It
   is now the most concrete checklist for preserving the sequence: hard
   numerical target -> inherited typed verifier questions -> verifier setup ->
   four-example environment -> 48-version evolution -> 48-version ledger roles
   -> FullVA technical turn
   -> claim boundary.
4. Use `LM4SCI_DISCOVERY_REWRITE_PACKET.md` when the next step is actual prose
   replacement. It provides section-level English skeletons while preserving
   the same claim boundaries and forbidden wording.
5. Compress abstract/introduction last; they currently carry the clearest
   statement that this is a method-discovery case study, not a paper-writing
   pipeline.
6. Use `48_VERSION_STORY_MAP_CN.md` as the source for slide narration, reviewer
   answers, or compressed appendix replacements; it now has 30-second,
   2-minute, reviewer-deep, and reusable English causal-block versions of the
   same 48-version discovery chain.
7. Use `REVIEWER_STORY_QA.md` after each major rewrite to make sure the
   compressed story still answers the obvious reviewer objections without
   drifting into unsupported claims.
8. Use `DETAILED_DISCOVERY_STORY_PIPELINE_CN.md` when rewriting a section from
   scratch; it is now the clearest version of the user's intended story order
   and should override chronology-first narration. Its continuous Chinese
   narration script is the fastest way to check whether a rewrite still tells
   the whole discovery story, and its paragraph-level playbook is the current
   guardrail for keeping `Verifier setup` before the four-example testbed,
   `What a version means` before the 48-version visual/table, and the FullVA
   hinge before sparse/backend/external details.
9. Use `ARGUMENT_BLUEPRINT.md` to check whether a proposed rewrite preserves
   the dependency chain: hard target -> typed verifier questions -> verifier setup ->
   four-example test environment -> 48-version evolution -> 48-version ledger
   roles -> FullVA turn -> claim boundary.
10. Treat `STORY_PIPELINE.md` as the root order contract. Use its
   `Canonical Story Pass` for any prose rewrite and its `Repeated Optimization
   Loop` after every compression pass. If another control document disagrees
   with it, update the secondary document rather than reverting the story to
   LLM-first or chronology-first narration.
