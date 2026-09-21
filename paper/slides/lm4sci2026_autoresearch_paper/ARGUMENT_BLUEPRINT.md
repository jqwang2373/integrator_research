# Integrator-Discovery Method Argument Blueprint

This file is the claim-evidence map for the LM4Sci paper on a
verifier-centered method for discovering new integrators.
`STORY_PIPELINE.md` defines the narrative order; this file defines the
argument that each section must support.

## Central Thesis

This paper argues that a verifier-centered LLM-assisted research pipeline can
serve as a method for discovering new scientific-computing integrators. The
bounded `Gauss6/FullVA` integrator is the discovered outcome, not the sole
subject of the paper. The discovery-method claim is credible because the
pipeline preserves method identity, versioned negative evidence, a four-example
test environment, and explicit nonpromotion boundaries.

## Core Research Question

How can an LLM-assisted research pipeline discover new scientific-computing
integrators while keeping the claim boundary precise enough to avoid promoting
diagnostics, reproductions, or external comparisons into unsupported claims?

## Argument Map

| Sub-argument | Claim | Evidence | Required boundary |
| --- | --- | --- | --- |
| A0: Discovery-method object | The paper evaluates the verifier-centered method for discovering integrators, not only the final integrator. | Title, abstract, introduction contribution list, `MethodSpec`/`ProblemSpec`/`EvidenceSpec`/`ClaimSpec` state model, and 48-version ledger. | Do not frame the paper as primarily describing or selling a universal new numerical method. |
| A1: Hard target | Lie-group constrained multibody integration is hard enough that ordinary score maximization is unsafe. | DAE/Lie-method references in `references.bib`; local sections on manifold rotations, index-3 constraints, friction, multipliers, Newton residual identity, and source-policy drift. | Do not describe the task as a generic benchmark or coding exercise. |
| A1b: Typed verifier questions | Prior numerical work and inherited code did not provide the final method; they initialized the typed constraints under which candidate explanations could be retained or rejected. | Verifier-question table in `main.tex`; right-action kinematics, conservative Gauss mechanics, ASME anchors, trapezoidal/BDF/Lobatto, TFE target, friction variants, sparse/backend work, and external harness. | Do not write related work as a generic list or imply that any one comparator closes the `Gauss6/FullVA` claim. |
| A2: Environment | The discovery environment made agent exploration auditable by separating method, problem, evidence, and claim objects. | `MethodSpec`, `ProblemSpec`, `EvidenceSpec`, `ClaimSpec` framing in `main.tex`; verifier levels L0-L3; local ledgers and validation files. | Do not claim that the verifier stack alone proves the numerical method. It controls promotion. |
| A3: Versioned discovery | The method emerged through 48 retained/rejected versions, not through a one-shot model suggestion. | `validation/version_ledger.csv`; appendix `Expanded 48-Version Discovery Ledger`; `VERSION_TREE.md`; `PIPELINE_AUDIT.md`. | Do not treat failed versions as noise. They define why the final method is not projection, Lobatto replacement, or sparse-solver engineering. |
| A4: Technical turn | The decisive new-method move was enforcing lower-pair velocity and acceleration consistency inside the Gauss6 stage residual. | v026-v028 PivotVA/FullVA path; v029 interbody double-revolute generalization; v047 132-row residual boundary. | Do not reduce the discovery to "try Gauss6". Gauss6 is the backbone; FullVA residual identity is the method-defining turn. |
| A5: Evidence system | Four ASME mechanisms are in the evidence system, but their roles differ. | `CLAIM_BOUNDARY.json`; `ORDER_ACCEPTANCE_GATE.md`; v047/v048 summaries. Single/double carry accepted dynamic-order evidence; four-link/slider-crank carry mechanism coverage and reaction consistency. | Do not write that all four examples prove accepted dynamic order. |
| A6: Claim discipline | The same pipeline that promotes `Gauss6/FullVA` also blocks stronger unsupported claims. | `CLAIM_BOUNDARY.json` not-claimed list; `ORDER_ACCEPTANCE_GATE.md`; `PAPER_NUMERICAL_RESULT_MATRIX.json`; source-policy rows open. | Do not claim full source-paper TFE replacement, sparse speed win, or external superiority. |

## Story-Pipeline Dependency Chain

The story order is not cosmetic. Each step creates the condition needed for the
next step to be meaningful. Reordering the paper around generic LLM motivation
or around the final result weakens the method-discovery claim.

| Step | Must come after | Establishes | If missing or moved too late |
| --- | --- | --- | --- |
| 1. Hard Lie-group constrained MBD target | Nothing; this is the opening frame. | The reader sees why method identity is fragile: manifold state, DAE levels, lower-pair multipliers, friction smoothness, residual rows, and reference policy. | The 48 versions look like ordinary coding attempts or benchmark tuning. |
| 2. Prior/inherited typed verifier questions | Hard target. | Previous work supplied partial constraints: representation anchors, clean/high-order baselines, low-order or endpoint-node alternatives, friction stressors, TFE targets, public mechanism anchors, and external harness boundaries. | The final method appears unmoored from prior numerical work, or reviewers ask whether the method is just Gauss6/Lobatto/projection/TFE. |
| 3. Verifier environment setup | Typed verifier questions. | The agent environment can keep MethodSpec, ProblemSpec, EvidenceSpec, ClaimSpec, and ledgers separate, so each inherited object has a legal claim role. | Failed or diagnostic rows can drift into unsupported method, order, speed, or superiority claims. |
| 4. Four-example test environment | Verifier setup. | The examples become typed tests: single/double pendulum carry local dynamic-order evidence; four-link/slider-crank carry closed-loop coverage and reaction consistency. | Readers may infer that all four mechanisms prove the same asymptotic dynamic-order theorem. |
| 5. 48-version evolution | Hard target, typed verifier questions, verifier setup, and test environment. | Versions become state transitions from candidate explanation to artifacts, verdict, next constraint, and claim-state movement. | The version ledger reads as a long chronology rather than a narrowing argument. |
| 6. FullVA outcome turn | The 48-version narrowing. | The discovered integrator outcome is identified as stage-level lower-pair velocity/acceleration consistency inside the Gauss6 residual. | The outcome collapses into "try Gauss6" or "repair endpoints by projection." |
| 7. Claim boundary and discovery-method lesson | FullVA outcome turn and evidence ladder. | The paper states exactly what is accepted, open, and forbidden, then generalizes only to verifier-centered integrator discovery. | The narrative can overclaim full TFE replacement, sparse speed, external superiority, seventh order, all-four dynamic order, or imply the paper is mainly final-integrator description. |

For drafting, the dependency test is simple: every paragraph should either
prepare one of these steps, execute it, or protect its boundary. A paragraph
that only says an agent wrote, summarized, or formatted material belongs in
disclosure or appendix unless it explains how claim preservation changed the
method search.

## Claim-Evidence-Reasoning Chains

### CER 1: Why the pipeline matters

- Claim: The agent pipeline matters because it preserves scientific state
  across many partially successful experiments.
- Evidence: The research ledger contains 48 versions and the paper reports
  695 checked result files, including 286 CSV files, 113 JSON summaries,
  202 figures, and 90 reports.
- Reasoning: A numerical method can look successful for the wrong reason.
  Durable artifacts and claim states make it possible to see whether a result
  came from the accepted method, a diagnostic, a projection, a surrogate, or an
  external comparison row.
- Boundary: Artifact volume is not itself discovery. The discovery claim must
  point to the retained FullVA residual structure.

### CER 1b: Why verifier failures drive discovery

- Claim: The verifier stack did more than reject bad claims; it converted
  failed promotions into constraints for the next version.
- Evidence: `main.tex` now records a verdict-to-constraint table: method
  identity mismatch leads to new residual hypotheses, reference drift freezes
  the `ProblemSpec`, incomplete proof keeps a claim open, mechanism coverage
  without theorem blocks dynamic-order promotion, and performance/source-policy
  caveats separate method validity from superiority.
- Reasoning: This translation rule explains why the 48-version history is a
  scientific narrowing process rather than trial-and-error bookkeeping.
- Boundary: Do not imply that every failure automatically improves the method;
  a failure matters only when the ledger records the next constraint it
  imposes.

### CER 2: Why `Gauss6/FullVA` is the discovered method

- Claim: The accepted method is not generic Gauss6; it is `Gauss6/FullVA`.
- Evidence: v013-v015 establish Gauss6 as the smooth high-order backbone.
  v024 rules out direct full Lobatto node swapping. v025 shows projection can
  close visible endpoint defects while changing trajectory accuracy. v026-v028
  move velocity and acceleration consistency into the stage residual. v029
  shows the idea generalizes beyond a single revolute joint.
- Reasoning: The discovery is the narrowing step that keeps the successful
  collocation backbone while rejecting endpoint repair as method identity.
- Boundary: Do not describe FullVA as an output projection or a post-step
  correction.

### CER 3: Why the four examples support the case study

- Claim: The four examples support method discovery by testing different
  dimensions of the method, not by proving the same order statement four
  times.
- Evidence: `single_pendulum` has accepted absolute-coordinate driven FullVA
  residual order with minimum order `6.024`. `double_pendulum` has accepted
  double-revolute FullVA self-reference order with minimum order `6.089`.
  `four_link` and `slider_crank` have closed-loop kinematic FullVA plus
  reaction-dynamics residuals, with max dynamics residuals `1.338e-13` and
  `6.492e-15`.
- Reasoning: Single and double pendulum test dynamic-order behavior. Four-link
  and slider-crank test closed-loop lower-pair coverage, rank, constraints,
  and reaction dynamics. These are necessary for method coverage, but they are
  not the same as asymptotic dynamic-order proof.
- Boundary: Avoid wording such as "all four examples prove sixth-order
  dynamics".

### CER 4: Why failed paths are evidence

- Claim: Failed attempts are central evidence because they rule out plausible
  but wrong method identities.
- Evidence: Reduced Lobatto was accurate but not the accepted full residual.
  Direct full Lobatto swaps were rank-deficient or divergent. Projection closed
  endpoint drift but changed accuracy. Several TFE row substitutions solved
  residuals but stayed order-limited or conditioning-limited. Sparse AD
  patterns were correct but not yet a wall-clock win.
- Reasoning: A method-discovery paper should not hide these failures; they
  explain why the accepted method has its current name and boundary.
- Boundary: Do not frame failed paths as implementation mistakes only. They
  are scientific eliminations.

### CER 5: Why the claim is bounded

- Claim: The accepted result is a bounded local method-discovery claim.
- Evidence: `CLAIM_BOUNDARY.json` accepts `Gauss6/FullVA` order 6 and records
  observed smooth position/velocity orders `7.161/7.066`; it also marks full
  TFE replacement, sparse speed, sharp coarse behavior, and external
  superiority as open or not claimed.
- Reasoning: The strongest version of the paper is not the broadest claim. It
  is a precise account of what has been discovered and what remains open.
- Boundary: The paper should never use bounded evidence as global submission
  readiness or external source-policy superiority.

## Anticipated Reviewer Objections

| Objection | Response strategy | Evidence to cite |
| --- | --- | --- |
| "This is just a numerical-method methodology paper." | Reframe. The integrator is the discovered outcome; the contribution is the verifier-centered discovery method and claim-promotion discipline. | Title, abstract, introduction contribution list, verifier-state model, 48-version ledger. |
| "This is just an LLM writing a paper." | Refute. The contribution is method discovery; paper drafting is downstream packaging. | Abstract/introduction framing; `STORY_PIPELINE.md`; 48-version ledger. |
| "The method is just Gauss6." | Refute. Gauss6 is the collocation backbone; FullVA residual identity is the technical turn. | v013-v015 versus v026-v029 and v047. |
| "Projection explains the success." | Refute and limit. Projection is a recorded failed/diagnostic path; accepted method identity is in-residual FullVA. | v025 and the FullVA pivot table. |
| "Four examples imply all four have dynamic order." | Concede coverage, limit order. Four examples are accepted as mechanism coverage; only two have accepted dynamic-order rows. | `ORDER_ACCEPTANCE_GATE.md`; `CLAIM_BOUNDARY.json`. |
| "Observed 7.161/7.066 means seventh order." | Refute. Observed finite-window slopes support sixth order; theorem claim remains six. | `ORDER_ACCEPTANCE_GATE.md` observed order interpretation. |
| "No full TFE replacement means no contribution." | Limit. Full TFE replacement is a stronger source-reproduction gate, not a prerequisite for the bounded `Gauss6/FullVA` method-discovery claim. | `CLAIM_BOUNDARY.json` comparator and `full_tfe_stage_replacement=false`. |
| "External baselines are not closed." | Concede and delimit. External superiority is not claimed; v048 is an execution scaffold and diagnostic matrix. | `PAPER_NUMERICAL_RESULT_MATRIX.json`; source-policy status. |
| "Sparse speed is not better." | Concede and delimit. Sparse structure is evidence for scaling direction but not part of accepted method superiority. | `CLAIM_BOUNDARY.json` sparse caveat fields. |

## Section-Level Argument Flow

1. `Introduction`: Discovery-method question -> hard numerical target ->
   exact claim-boundary question -> contribution as a method for discovering
   integrators.
2. `Related Work and Gap`: Numerical prior work first as typed verifier questions;
   LLM-for-science second as workflow motivation; the gap is claim-preserving
   method discovery, not automated report generation.
3. `How the Discovery Method Was Built`: Establish hard target, inherited
   baselines, verifier setup, four-example test environment, and meaning of a
   version before showing the FullVA narrowing trace.
4. `Discovery Environment`: Explain how verifier state protects method
   identity and claim promotion.
5. `Discovered Integrator Outcome`: Show the narrowing path from Gauss6 backbone through
   failed Lobatto/projection to FullVA rows.
6. `Numerical Test Environment`: Explain which examples prove dynamic order
   and which provide mechanism coverage.
7. `Failed Attempts`: Use negative evidence to show why the method boundary is
   credible.
8. `Discussion`: Generalize only to verifier-centered method discovery, not to
   all scientific domains.
9. `Limitations`: State single-case scope, no anonymized artifact bundle yet,
   no full TFE replacement, no external superiority, and bounded dynamic-order
   examples.
10. `Conclusion`: Return to the discovery method: the verifier-centered
   procedure shows how endpoint repair was rejected and stage-level FullVA
   velocity/acceleration residuals became the discovered integrator outcome.

## Evidence Map By Artifact

| Artifact | Use in paper | Claim it supports |
| --- | --- | --- |
| `version_ledger.csv` | Source for 48-version evolution and appendix. | Discovery path is versioned and cumulative. |
| `VERSION_TREE.md` | Detailed historical context. | Each version has a role and limitation. |
| `PIPELINE_AUDIT.md` | Counts, validation status, and caveat synchronization. | Artifact discipline and claim boundaries are maintained. |
| `CLAIM_BOUNDARY.json` | Primary claim and nonclaim authority. | Accepted method, accepted examples, caveats, forbidden claims. |
| `ORDER_ACCEPTANCE_GATE.md` | Order and example-role authority. | Sixth-order claim; single/double dynamic order; four-link/slider-crank coverage. |
| `PAPER_NUMERICAL_RESULT_MATRIX.json` | External comparison boundary. | Public/common-reference rows are diagnostic, not external superiority. |
| `main.tex` appendix | Human-readable 48-version story. | Failed and retained versions explain the accepted method. |

## Wording Rules For Drafting

- Write "conditional sixth-order `Gauss6/FullVA`" rather than "new universal
  sixth-order solver".
- Write "four-example mechanism coverage" rather than "four-example dynamic
  order".
- Write "v048 external-comparison scaffold" rather than "external superiority
  evidence".
- Write "full TFE replacement remains open" rather than "TFE reproduced".
- Write "sparse structure/cost caveat" rather than "sparse speedup".
- Write "observed slopes support sixth order" rather than "seventh order".

## Current Argument Strength Assessment

| Sub-argument | Evidence strength | Logic validity | Counter-argument risk |
| --- | --- | --- | --- |
| Hard target | Strong | Valid | Low |
| Typed comparators | Strong | Valid and now ordered before LLM workflow motivation | Medium if compressed into a generic related-work list |
| Verifier environment | Strong | Valid but case-study scoped | Medium |
| 48-version discovery | Strong | Valid | Low |
| FullVA technical turn | Strong | Valid | Medium |
| Four-example evidence | Moderate/strong | Qualified | High if wording overclaims dynamic order |
| External comparison boundary | Strong as a boundary, weak as superiority | Valid | High if any superiority language appears |

## Next Drafting Moves

1. Keep the main paper's first three pages centered on the seven-question story
   contract.
2. Move any "agent writes/reviews paper" wording to disclosure only.
3. In every results paragraph, state the allowed claim and the nearest
   forbidden stronger claim.
4. If space is tight, preserve the FullVA narrowing argument before preserving
   external-comparison details.
