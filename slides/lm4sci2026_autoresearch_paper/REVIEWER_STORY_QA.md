# Reviewer-Facing Story QA

This file converts the integrator-discovery-method story into likely reviewer
questions and controlled answers. It is a drafting aid, not a response letter
and not new evidence. Use it when tightening the main text, preparing slides,
or checking whether the paper still reads as a paper about how to discover new
integrators, not mainly as a paper describing one integrator.

For section-level rewrites, use
`DETAILED_DISCOVERY_STORY_PIPELINE_CN.md` as the paragraph-order guardrail:
hard problem, inherited comparators, verifier setup, four-example test
environment, 48-version evolution, FullVA technical turn, and claim boundary.
Its continuous Chinese narration script is the quickest check that a response
or compressed draft still tells the full discovery story rather than drifting
into LLM-first or chronology-first framing.

## Core Reviewer Position

The paper should invite reviewers to evaluate one central claim:

> A verifier-centered LLM-assisted research pipeline can discover new
> scientific-computing integrators by preserving a 48-version chain of
> retained, rejected, and quarantined method hypotheses.

`Gauss6/FullVA` is the bounded discovered outcome used to stress-test this
discovery method. The paper should not ask reviewers to evaluate it as mainly
a final-integrator methodology submission.

The paper should not invite reviewers to evaluate unsupported claims about
full TFE reproduction, sparse wall-clock superiority, external superiority, or
accepted dynamic order on all four mechanisms.

## Q1. Is this mainly a paper describing the `Gauss6/FullVA` integrator?

**Short answer.** No. The integrator is the discovered outcome. The paper's
main claim is about a verifier-centered LLM-assisted method for discovering new
integrators while preserving claim boundaries.

**Evidence anchors.**

- `main.tex` title: frames the work as a verifier-centered method for
  discovering new integrators.
- `main.tex` abstract: says the paper does not ask reviewers to accept a
  description of the integrator formula alone.
- `main.tex` introduction contribution list: starts from auditable traces,
  typed verifier questions, and nonpromotion boundaries before naming the
  bounded `Gauss6/FullVA` outcome.

**Main-text wording to preserve.** "The paper's primary subject is the
discovery method, not the integrator formula alone."

**Do not say.** Do not pitch the manuscript as primarily describing or selling
a universal new integrator.

## Q2. Is this just an LLM writing a paper?

**Short answer.** No. The scientific object is the method-discovery path, not
the downstream manuscript-writing process.

**Evidence anchors.**

- `main.tex:153-156`: states that the contribution is not a prompt recipe or
  paper-writing pipeline.
- `main.tex:157-168`: lists three claims centered on `Gauss6/FullVA`,
  FullVA residual discovery, and verifier-preserved failed alternatives.
- `main.tex:743-759`: consolidated discussion and conclusion return to method
  discovery, not writing.

**Main-text wording to preserve.** "Paper drafting, formatting, and review
scaffolds are downstream packaging; they are not the scientific object studied
here."

**Do not say.** The paper should not claim that the auto-research system
automatically wrote a submission-ready numerical-method paper.

## Q3. Why is this Lie-group integrator problem hard enough to matter?

**Short answer.** The method is defined by manifold state, constrained DAE
levels, lower-pair reaction multipliers, friction smoothness, Newton residual
identity, and reference policy. A single benchmark score can hide a wrong
one-step map.

**Evidence anchors.**

- `main.tex:88-99`: hard target in the introduction.
- `main.tex:279-290`: failure modes in the discovery section.
- `STORY_PIPELINE.md` "Why The Problem Is Hard": expanded technical list.

**Reviewer-facing implication.** The point of the agent is not faster
benchmark iteration. The point is preserving enough state to know which
numerical method was actually computed.

**Do not say.** Do not reduce the task to "the agent optimized a benchmark."

## Q4. What prior work or inherited material existed before the 48 versions?

**Short answer.** The project inherited typed verifier questions: Lie-group
kinematics, conservative Gauss mechanics, ASME-style mechanisms,
trapezoidal/BDF/Lobatto baselines, TFE targets, friction variants, and external
harnesses. These were useful, but none alone defined the accepted method. They
initialized different search constraints: representation anchors, clean or
reduced baselines, rejected endpoint explanations, lower-pair/friction stress
tests, and scaling/external claim boundaries.

**Evidence anchors.**

- `main.tex:111-128`: inherited objects plus validator design.
- `main.tex:171-220`: typed verifier-question table and boundaries.
- `48_VERSION_STORY_MAP_CN.md`: role taxonomy for v001-v048 and the
  2-minute comparator-to-FullVA causal narrative.

**Main-text wording to preserve.** "We treat these inherited elements as typed
verifier questions rather than as a single leaderboard."

**Do not say.** Do not write that the new method was discovered from a clean
leaderboard or from one external baseline comparison.

## Q5. What exactly did the verifier environment do?

**Short answer.** It separated method, problem, evidence, claim, and ledger
objects, and bound each example to a gate role. The agent could run hypotheses,
but each verifier verdict returned a typed next constraint rather than a hidden
score; claims changed only after validators checked method identity, problem
identity, evidence artifacts, gate scope, and wording boundaries.

**Evidence anchors.**

- `main.tex:304-310`: local discovery-story verifier setup bridge.
- `main.tex:436-468`: state object, claim-promotion checks, and
  identity/evidence/claim locks.
- `main.tex:470-491`: durable objects table.
- `main.tex:496-530`: verifier verdicts become next-version constraints.
- `main.tex:535-549`: sandbox levels and reversible claim states.

**Reviewer-facing implication.** The verifier stack does not prove the
numerical method by itself. It prevents diagnostic results from being promoted
into stronger claims while the method is changing.

**Do not say.** Do not imply that the verifier replaces mathematical proof or
domain judgment.

## Q6. What are the four numerical examples actually testing?

**Short answer.** They form a verifier ladder, not four copies of the same
order test. Single and double pendulum support accepted local dynamic-order
evidence. Four-link and slider-crank support closed-loop lower-pair coverage
and reaction consistency, but not accepted asymptotic dynamic order. The
examples are selected by the ambiguity they expose: clean order, interbody
transfer/reference policy, loop closure, and mixed lower-pair coverage. A
failed rung returns a typed next constraint, not one generic pass/fail score.

**Evidence anchors.**

- `main.tex:312-321`: early order-gate versus coverage/reaction-gate role
  statement.
- `main.tex:627-685`: verifier ladder, ambiguity targets, and dynamic-order
  boundary.
- `main.tex:696-701`: claim-state snapshot.

**Main-text wording to preserve.** "Four mechanisms in the evidence system
does not mean four dynamic-order proofs."

**Do not say.** Do not write that all four examples prove sixth-order dynamics.

## Q7. What does a "version" mean in the 48-version story?

**Short answer.** A version is a research contract: candidate explanation,
bounded implementation and artifacts, verifier verdict, and next constraint.
It is not a prompt attempt or a hyperparameter sample. The shortest reviewer
answer should group the 48 versions into representation/reproducibility,
constraint identity, backbone/comparator, FullVA hinge, and boundary-management
blocks before expanding individual versions. These blocks are ordered
dependencies, not topical bins: each block makes the next block's failures
interpretable.

**Evidence anchors.**

- `main.tex:130-139`: five-block narrowing chain in the introduction.
- `main.tex:323-338`: version definition and reusable reading rule.
- `main.tex:340-432`: discovery spine, role-coded ledger table, and
  v023-v029 failure-to-constraint trace.
- `main.tex:775-1030`: one concise appendix entry per version plus the
  calibrated/rejected/promoted/quarantined reading rule.
- `DETAILED_DISCOVERY_STORY_PIPELINE_CN.md`: paragraph-level playbook for
  preserving the same discovery order during compression.
- `48_VERSION_STORY_MAP_CN.md`: full Chinese role, claim-state, three-depth
  narration, reusable English causal block narration, and version-by-version
  map.

**Reviewer-facing implication.** Failed versions are evidence because they rule
out plausible but wrong method identities, such as endpoint-node replacement,
projection repair, sparse-speed explanations, or external-superiority claims.

**Do not say.** Do not frame v001-v048 as "48 attempts until one worked."

## Q8. Why is the method not just Gauss6?

**Short answer.** Gauss6 is the collocation backbone. The discovered method is
`Gauss6/FullVA` because the method-defining change is stage-level lower-pair
velocity and acceleration consistency inside the residual.

**Evidence anchors.**

- `main.tex:558-566`: not simply "try Gauss6."
- `main.tex:572-601`: v023-v029 FullVA hinge table.
- `main.tex:608-624`: accepted method evidence and residual identity.

**Main-text wording to preserve.** "The method-defining object became
stage-level V/A consistency, not post-step correction." Also preserve the
criterion that FullVA is not a generic small-residual solve; the accepted rows
must belong to the same MethodSpec.

**Do not say.** Do not describe FullVA as an output projection or post-step
repair.

## Q9. Why does projection not explain the result?

**Short answer.** Projection was useful as a diagnostic, but it changed the
trajectory map. The accepted method puts velocity and acceleration consistency
inside the stage residual rather than repairing the endpoint afterward.

**Evidence anchors.**

- `main.tex:419-432`: compact failure-to-constraint trace from v023 to v029.
- `main.tex:572-601`: v025 projection demoted, v026-v027 promote in-residual
  velocity/acceleration rows.
- `main.tex:608-624`: FullVA is not merely output projection.
- `48_VERSION_STORY_MAP_CN.md` v025-v027 rows.

**Reviewer-facing implication.** The projection failure is one of the reasons
the final method identity is credible: a tempting shortcut was explicitly
tested and rejected.

**Do not say.** Do not write that projection is part of the accepted method
identity.

## Q10. Why do failed TFE, sparse, and external-comparison paths remain in the paper?

**Short answer.** They define claim boundaries. TFE diagnostics show what is
still open, sparse diagnostics separate correctness from speed, and the
external harness organizes future comparisons without supporting superiority.

**Evidence anchors.**

- `main.tex:696-701`: claim-state snapshot.
- `main.tex:706-741`: reusable verifier rules, including failed paths and
  external-comparison discipline.

**Reviewer-facing implication.** The strongest paper is the bounded claim,
not the broadest claim. Leaving open paths visible makes the accepted method
more precise.

**Do not say.** Do not claim full TFE reproduction, sparse speedup, or external
superiority.

## Q11. What should an LM4Sci reviewer learn from this case?

**Short answer.** LLM agents can contribute to scientific computing when they
preserve method identity, negative evidence, verifier state, and claim
boundaries across a long experiment tree.

**Evidence anchors.**

- `main.tex:236-242`: claim-preserving method-discovery gap.
- `main.tex:743-759`: discussion of durable scientific state and
  limitations.
- `MAIN_TEXT_COMPRESSION_BLUEPRINT.md`: compressed story skeleton.

**Reviewer-facing implication.** The contribution is not that an LLM generated
a method in one shot, and not that the paper is mainly an ordinary
integrator-method submission. The contribution is a concrete method for
agent-assisted integrator discovery where failed candidates remain auditable
and useful.

**Do not say.** Do not generalize from this single case to all scientific
domains without the limitations stated in `main.tex:751-756`.

## Final Pre-Submission QA

Before any shortened main text is treated as stable, answer yes to all of the
following:

- Does the opening make the numerical target hard before discussing broad LLM
  automation?
- Does the first page explicitly say the paper is about a method for
  discovering new integrators, with `Gauss6/FullVA` as the bounded discovered
  outcome?
- Does the paper explain inherited comparators before the 48-version ledger?
- Does the paper define a version as hypothesis, artifacts, verdict, and next
  constraint?
- Does the paper identify v023-v029 as the FullVA hinge?
- Does the paper separate single/double dynamic order from four-link and
  slider-crank coverage?
- Does the paper preserve the nonclaims around TFE, sparse speed, external
  superiority, and all-four-example dynamic order?

If any answer is no, the story pipeline has drifted.
