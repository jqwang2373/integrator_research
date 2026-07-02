# Integrator-Discovery Method Story Pipeline

This note is the working blueprint for the LM4Sci draft. It keeps the paper
centered on a method for discovering new integrators with LLM agents. The
manuscript should describe the verifier-centered discovery procedure first and
the bounded `Gauss6/FullVA` outcome second. The paper is not mainly a
standalone description of that integrator. The scientific object is the
discovery method: how the agent maintained experiments, files, claims,
rejected paths, and nonpromotion boundaries while the integrator was being
discovered.

## One-Sentence Thesis

A verifier-centered LLM-assisted research pipeline is a method for discovering
new integrators because it preserves an auditable chain of retained, rejected,
and quarantined technical moves. In this case, that chain runs from basic Lie
kinematics, through constrained DAE residuals and failed endpoint repairs, to a
bounded `Gauss6/FullVA` integrator outcome with explicit claim boundaries.

## What The Paper Is Not

- Not a paper about automatic paper generation.
- Not a generic prompt-engineering recipe.
- Not a paper whose primary goal is to describe the discovered integrator
  itself.
- Not a claim that all source-paper TFE residuals have been reproduced.
- Not a claim of external source-policy superiority.
- Not a claim that four-link and slider-crank already prove accepted
  asymptotic dynamic order.
- Not a claim that sparse AD is already a wall-clock speed win.

## Core Story Contract

The draft should answer seven questions in order.

1. Why is Lie-group constrained multibody integration hard?
2. What previous methods, inherited code paths, and partial baselines existed?
3. How was the research environment set up so that an agent could explore
   without changing the claim being tested?
4. What are the four numerical examples, and what does each example test?
5. How did the method evolve across 48 versions?
6. What were the 48 versions or version blocks doing in the ledger?
7. Which technical turn actually produced the discovered integrator?
8. What general integrator-discovery method does this support?

Every major section should support at least one of these questions. Anything
that only sells the integrator as the whole paper, or only explains how the
paper was written, should be removed or demoted to discovered-outcome detail or
AI disclosure.

## Canonical Story Pass

When rewriting the abstract, introduction, slides, or rebuttal, use this as
the minimum full story. The reader should move through the rows in order. A
short version may compress rows, but it should not reverse them.

| Pass | Reader starts by thinking | Paragraph must establish | Handoff to next paragraph |
| --- | --- | --- | --- |
| 1. Hard numerical target | "This may be just another benchmark." | Lie-group constrained MBD is hard because manifold transport, DAE constraint levels, lower-pair multipliers, friction smoothness, residual rows, endpoint policy, and reference policy can each change the actual one-step map. | Because method identity is fragile, previous work cannot be treated as one flat scoreboard. |
| 2. Inherited partial objects | "Wasn't this already solved by Gauss, Lobatto, TFE, rA, or baselines?" | Prior objects did real partial jobs: they fixed representation, supplied clean high-order backbones, provided public mechanisms, tested low-order or endpoint-node explanations, stressed friction, exposed scaling, or defined external-policy limits. | Because these objects have different roles, the environment must store method, problem, evidence, and claim separately. |
| 3. Verifier environment setup | "An agent could just change the target until it passes." | The pipeline uses MethodSpec, ProblemSpec, EvidenceSpec, ClaimSpec, and ledgers so that a run returns a typed next constraint, not a hidden score. A claim changes only after method identity, problem identity, artifacts, and wording boundary pass. | With claim promotion controlled, the numerical examples can become tests rather than demos. |
| 4. Four-example testbed | "Four examples probably mean four copies of the same order proof." | The examples form an ordered ambiguity ladder: single pendulum tests a clean dynamic-order row; double pendulum tests interbody transfer and reference policy; four-link tests closed-loop loop-closure and reactions; slider-crank tests mixed revolute/prismatic coverage. | Because each example returns a gate-specific verdict, the long version history can be read as narrowing evidence. |
| 5. 48-version evolution | "Forty-eight versions sounds like trial and error." | A version is a bounded research contract: candidate explanation, implementation or diagnostic, artifacts, verifier verdict, next constraint, and claim-state movement. | Once a version has this meaning, all 48 versions can be grouped by what ambiguity they removed or preserved. |
| 6. What all 48 versions did | "What were those versions actually about?" | The blocks are ordered dependencies: representation calibration; clean high-order mechanics; constrained-DAE identity; Gauss6/comparator separation; FullVA hinge; sparse/scaling; lower-pair breadth; four-example and external-claim boundaries. | This block-level map points to the one technical turn that survived all nearby explanations. |
| 7. FullVA outcome turn | "Maybe the result is just Gauss6, projection, or a Lobatto node choice." | v023-v029 rejected full-DAE Lobatto node replacement and endpoint projection, then promoted lower-pair velocity/acceleration consistency inside the same Gauss6 stage residual after off-axis/interbody checks. | After the discovered integrator outcome is isolated, state exactly what is accepted and what remains open. |
| 8. Discovery-method lesson | "How broad is the result?" | Accepted: conditional sixth-order `Gauss6/FullVA` with single/double dynamic-order evidence and four-example mechanism coverage. Not accepted: full TFE replacement, sparse speed win, external superiority, seventh-order theorem, or all-four dynamic order. | The paper can now generalize to verifier-centered integrator discovery, not to automatic science, automatic paper writing, or a universal integrator claim. |

This is the core narrative. If a rewrite starts with LLM motivation, artifact
counts, sparse speed, external comparison, or paper-writing automation before
rows 1-4 are established, it has broken the story pipeline.

## Why This Order Matters

The seven questions are a dependency chain, not a table of contents. Each step
makes the next step meaningful:

| Step | Establishes | If moved or omitted |
| --- | --- | --- |
| Hard Lie-group constrained MBD target | Method identity is fragile because manifold transport, DAE levels, lower-pair multipliers, friction smoothness, residual rows, endpoint repair, and reference policy can silently change the one-step map being tested. | The 48 versions look like ordinary coding attempts or benchmark tuning. |
| Prior/inherited verifier questions | Earlier work supplied representation anchors, baselines, rejected alternatives, source targets, mechanism anchors, and external-policy boundaries. | Reviewers can read the final method as unmoored from prior numerical work or as just Gauss6, Lobatto, projection, or TFE. |
| Verifier environment setup | MethodSpec, ProblemSpec, EvidenceSpec, ClaimSpec, and ledgers define what an agent may change and what it may only report. | Diagnostic rows can drift into unsupported method, order, speed, or superiority claims. |
| Four-example test environment | The examples become typed tests: single/double pendulum carry local dynamic-order evidence, while four-link/slider-crank carry coverage and reaction consistency. | The paper may imply that all four mechanisms prove the same asymptotic dynamic-order theorem. |
| 48-version evolution | Each version becomes a state transition from candidate explanation to artifacts, verifier verdict, next constraint, and claim-state movement. | The ledger reads as chronology instead of a scientific narrowing argument. |
| 48-version ledger roles | The role-coded blocks explain what all 48 versions contributed: calibration, constraint identity, comparator separation, FullVA hinge, scaling, lower-pair breadth, and claim-boundary management. | The reader sees a version count but not why every retained or rejected path matters. |
| FullVA outcome turn | Stage-level lower-pair velocity/acceleration consistency inside the Gauss6 residual is isolated as the discovered integrator outcome. | The outcome collapses into "try Gauss6" or "repair endpoints by projection." |
| Claim boundary and discovery-method lesson | Accepted, open, and forbidden claims are separated after the evidence ladder and outcome turn. | The narrative can overclaim full TFE replacement, sparse speed, external superiority, seventh order, all-four dynamic order, or suggest the paper is mainly integrator description. |

Use this dependency test during revision: a paragraph should prepare one of the
steps, execute it, or protect its boundary. A paragraph that only says the
agent wrote, summarized, formatted, or reviewed text belongs in disclosure or
appendix unless it explains how claim preservation changed the method search.

## Why The Problem Is Hard

The opening technical motivation should make clear that this is not a simple
benchmark optimization problem.

- The state lives on a Lie group: rotations must stay on the attitude
  manifold, and local coordinates cannot be treated as ordinary Euclidean
  state variables without care.
- The mechanical problem is a constrained DAE: holonomic constraints have
  position-, velocity-, and acceleration-level consequences, and an apparently
  small residual at one level can hide a defect at another.
- Lower-pair mechanisms introduce multipliers and reaction forces: the method
  must track constraint forces, not only positions.
- Friction and multiplier-dependent loads make smoothness regime-dependent:
  smooth regularized friction and sharp regularized friction support different
  order statements and cost policies.
- Newton solves are part of the method: the residual rows, stage variables,
  endpoint policy, tolerance, Jacobian backend, and linear solve policy can
  change what is being computed.
- Baseline comparison is fragile: a local reproduction, reduced surrogate,
  public-code run, source-paper residual, and external same-test campaign are
  different evidence objects.

The reader should understand this before seeing the 48-version ledger. Without
this context, the ledger looks like many implementation attempts. With this
context, it becomes a record of ways a numerical-method claim can be wrong.

## Prior Work And Inherited Baselines

The paper should present earlier work as verifier questions, not as a single
leaderboard.

| Comparator family | Role in the story | What it cannot prove alone |
| --- | --- | --- |
| Lie-group kinematics and RKMK/CF methods | Establish right-action rotation conventions and high-order attitude updates. | Does not close constrained DAE dynamics. |
| Conservative Lie midpoint/Gauss baselines | Show that high-order smooth rigid-body mechanics are possible. | Do not handle lower-pair constraints, multipliers, and friction fully. |
| SBEL/Negrut-style ASME examples | Provide public-style mechanism anchors and reproducibility context. | A reproduction anchor is not a new `Gauss6/FullVA` method. |
| Reduced trapezoidal/BDF/Lobatto baselines | Test whether lower-order, damping, or endpoint-node directions explain the improvement. | Reduced baselines cannot close the full absolute-coordinate lower-pair claim. |
| TFE/Gauss-Lobatto source-paper target | Defines a strong source-reproduction direction and a local expected-order comparator. | Current accepted method does not claim full source-paper TFE residual replacement. |
| Brown--McPhee/friction variants | Stress multiplier-dependent loads and sharp/smooth friction regimes. | Smooth and sharp regimes must not be merged into one order claim. |
| v048 same-test external harness | Organizes public-code and same-window comparison rows. | It is not a method improvement and does not permit external-superiority claims yet. |

Comparator-to-constraint rule: each inherited object should become a verifier
question, not a solved answer. The paper should ask which representation can be
trusted, which baseline is only local, which endpoint repair changes the
one-step map, and which scaling or external row is forbidden from promoting a
stronger claim.

## Research Environment

The environment should be described as a scientific state machine rather than
a coding assistant loop.

### Durable Objects

- `MethodSpec`: state variables, stage variables, residual rows, endpoint
  policy, solver tolerance, Jacobian backend, and method name.
- `ProblemSpec`: mechanism, geometry, masses, drivers, friction law, time
  window, step sizes, reference policy, and error metrics.
- `EvidenceSpec`: CSV rows, JSON summaries, plots, proof certificates,
  validator outputs, reports, and PDFs.
- `ClaimSpec`: exact claim text, accepted/open/forbidden state, required
  validators, nonpromotion rules, and forbidden wording.
- `Ledger`: version ledger, proof ledger, validation audit, package audit, and
  claim-boundary files.

### Sandbox Levels

| Level | Purpose | Example |
| --- | --- | --- |
| L0 read-only audit | Check whether current prose and claims match existing artifacts. | Scan `CLAIM_BOUNDARY.json`, `ORDER_ACCEPTANCE_GATE.md`, and compiled PDF text. |
| L1 bounded probe | Test one local hypothesis without changing ledgers. | Try a local residual row variant or rank diagnostic. |
| L2 full generator | Regenerate method artifacts after a controlled implementation change. | Run a version script and update CSV/JSON/plots/reports. |
| L3 source-policy campaign | Compare against public-code baselines under strict external policy. | v048/B4 same-test source-policy execution, requiring explicit opt-in. |

The key point is that an agent may propose and run code, but it may not promote
a claim unless the relevant verifier accepts the method identity, problem
identity, evidence artifact, and claim boundary.

### Failure-To-Next-Version Rule

The environment should not describe failures as discarded experiments. Each
failed promotion becomes the constraint that defines the next version:

| Verifier verdict | Next-version constraint | Story role |
| --- | --- | --- |
| Method identity mismatch | Split diagnostic behavior from the claimed `MethodSpec`; test the missing residual row or stage variable directly. | Turns v025 projection repair into v026-v027 in-residual V/A rows. |
| Problem/reference drift | Freeze the `ProblemSpec` and reference policy before comparing error rows. | Keeps v046 baseline rows diagnostic while allowing method-side FullVA self-reference for double pendulum. |
| Artifact or proof incomplete | Leave the claim open and move evidence into the proof/diagnostic lane. | Explains why `7.161/7.066` supports sixth order but not a seventh-order theorem, and why full TFE replacement stays open. |
| Coverage without order theorem | Accept mechanism coverage but block dynamic-order promotion. | Explains four-link and slider-crank as closed-loop lower-pair coverage, not accepted asymptotic order examples. |
| Performance/source-policy caveat | Separate method validity from sparse speed and external superiority. | Keeps sparse correctness and v048 same-test scaffolding useful without overstating them. |

This rule is what makes 48 versions scientifically meaningful. The sequence is
not "try many things until one works"; it is a controlled translation from
verifier verdicts to narrower method hypotheses.

## Four Numerical Examples

The four examples should be introduced early as the test environment, then
used later as evidence.

Gate semantics: the examples form an ordered ambiguity ladder, not a single
scoreboard. A pass on `single_pendulum` authorizes the next reference-policy
and interbody-transfer question; it does not donate its dynamic-order claim to
`four_link` or `slider_crank`. Each rung returns a different next constraint:
method order, reference policy, loop closure, or lower-pair coverage.

| Example | Current accepted role | Current evidence | Boundary |
| --- | --- | --- | --- |
| `single_pendulum` | Dynamic method-order row. | Exact driven ASME kinematics and absolute-coordinate driven FullVA residual; minimum accepted order `6.024`. | Supports local dynamic order. |
| `double_pendulum` | Dynamic method-order row. | Double-revolute FullVA self-reference; minimum accepted order `6.089`. | Supports local dynamic order under the accepted reference policy. |
| `four_link` | Mechanism coverage and closed-loop consistency row. | Closed-loop kinematic FullVA plus reaction dynamics; max dynamics residual `1.338e-13`. | Not promoted to accepted dynamic order. |
| `slider_crank` | Mechanism coverage and closed-loop consistency row. | Closed-loop kinematic FullVA plus reaction dynamics; max dynamics residual `6.492e-15`. | Not promoted to accepted dynamic order. |

The wording must keep two statements separate:

- Supported: all four examples are in the method evidence system as mechanism
  coverage.
- Not supported: all four examples prove asymptotic dynamic order.
- Search role: each example returns a different next constraint--method order,
  reference policy, loop closure, or lower-pair coverage--rather than a single
  generic score.

## What A Version Means

A version is not a prompt attempt. In this project, a version means:

1. a hypothesis about the numerical method or evidence gate;
2. a bounded implementation or diagnostic;
3. generated artifacts such as CSV, JSON, plots, reports, or proof notes;
4. an interpretation of what the artifacts do and do not prove;
5. a ledger entry that preserves both improvement and limitation.

This is why failed versions matter. A failed Lobatto residual, a projection
repair, or a sparse solver that is correct but slow all become information
about the shape of the final method.

For narration, versions should also be grouped by role:

- measurement and representation calibration;
- clean high-order component search;
- constrained-DAE method-identity discovery;
- backbone/comparator separation;
- the FullVA method-identity hinge;
- scaling and lower-pair generality;
- reviewer-facing evidence and claim-boundary management.

This role grouping is what keeps the 48-version history from reading as a long
implementation log. The main text can compress versions into blocks, while the
appendix and `48_VERSION_STORY_MAP_CN.md` preserve the one-version-per-row
detail.

## 48-Version Discovery Map

The manuscript should use the detailed appendix for all 48 versions, but the
main body should compress the discovery into blocks with a clear lesson.

| Versions | Question | Key movement | Lesson for the final method |
| --- | --- | --- | --- |
| v001-v003 | Can the representation and public baseline be trusted? | SO(3) benchmarks, corrected CF4/RKMK4 right-action kinematics, SBEL/Negrut rA reproduction. | Start with reproducibility and representation before claiming a new integrator. |
| v004-v005 | Can high-order Lie mechanics work in a clean conservative setting? | Yoshida-composed midpoint and Gauss-Lie4 mechanics. | High-order smooth mechanics are possible, but constraints and friction remain outside scope. |
| v006-v008 | Can constraints be internalized in a DAE solve? | Reduced fixed-pivot DAE, absolute-coordinate explicit multipliers, endpoint-constrained 54-variable Newton solve. | Constraint level and endpoint policy must be part of the method identity. |
| v009-v012 | Can friction and quaternion transport be made reliable? | Smooth/sharp friction, JAX Jacobian, `S^3` transport, quaternion endpoint DAE. | Friction smoothness, AD backend, and manifold transport must be tested separately. |
| v013-v015 | Is Gauss6 the high-order backbone? | Three-stage Gauss6 endpoint collocation and adaptive Gauss6/Gauss4. | Gauss6 is strong in smooth regimes, but sharp friction and lower-pair structure remain open. |
| v016-v018 | Do reduced trapezoidal/BDF/Lobatto directions explain the result? | Reduced trapezoidal, Lie-BDF2, and Lobatto endpoint-node baselines. | Endpoint-node and low-order baseline directions are comparators, not the missing full method. |
| v019-v022 | Can multiplier-dependent friction be represented? | Lambda-dependent Stribeck and Brown--McPhee-style revolute friction. | Multiplier-dependent loads are AD-compatible, but reduced one-DOF surrogates do not close the full DAE claim. |
| v023-v025 | What breaks in the full absolute-coordinate revolute DAE? | Five-constraint revolute DAE, failed direct Lobatto swap, SHAKE/RATTLE-style projection. | Projection repairs visible drift but changes the trajectory; node replacement alone is not enough. |
| v026-v028 | What is the decisive residual change? | Stage pivot velocity rows, stage acceleration rows, off-axis FullVA rows. | Velocity and acceleration consistency must enter the stage residual; this is the FullVA turn. |
| v029 | Does FullVA generalize beyond one joint? | Double-revolute interbody PivotVA/FullVA DAE. | FullVA is not a single-pendulum trick, but the residual grows and exposes sparse-solver needs. |
| v030-v038 | Can the larger FullVA Newton solve be made practical? | Sparsity diagnostics, CSR Newton, failed GMRES, lagged Jacobians, colored JVP, batched JVP, symbolic/JVP-pruned patterns, cache reuse. | Sparse structure is real, but solver performance is a separate claim from method correctness. |
| v039-v045 | Does the path extend to larger and non-revolute lower pairs? | Triple revolute, skew-axis, prismatic, double-prismatic, and row-colored VJP diagnostics. | FullVA/sparse diagnostics extend across lower-pair types, but sparse speed remains a caveat. |
| v046 | Can all four ASME examples be brought into one validation anchor? | Single, double, four-link, and slider-crank rA validation harness. | This gives reproducibility and mechanism coverage context, not a new `Gauss6/FullVA` claim by itself. |
| v047 | What is the accepted local discovery? | Cylindrical-chain `Gauss6/FullVA`, 132-row residual boundary, smooth orders `7.161/7.066`, four-example evidence, TFE/sparse/sharp caveats. | Accepted local method: conditional sixth-order `Gauss6/FullVA` with explicit claim boundaries. |
| v048 | Can external same-test comparison be organized? | Cross-paper public-code and same-window benchmark harness. | Useful external scaffold, but external-superiority and source-policy rows remain unpromoted. |

## Central Discovery Logic

The core method story is a narrowing argument:

1. Keep the Gauss6 smooth high-order backbone because v013-v015 showed strong
   smooth order.
2. Reject simple endpoint-node replacement because v018 and v024 showed that
   reduced Lobatto and direct full Lobatto swaps do not provide the accepted
   full DAE method.
3. Reject projection as the method identity because v025 closed visible
   endpoint drift but changed trajectory accuracy.
4. Promote in-residual velocity/acceleration consistency because v026-v028
   showed that stage velocity and acceleration rows close the relevant
   residual channels as one MethodSpec, not as a post-step repair or generic
   small-residual solve.
5. Generalize through v029 and later lower-pair tests, then separate method
   correctness from sparse-solver speed, source-policy comparison, and
   full-TFE reproduction.

After v025, the hinge has a three-gate reading: a candidate must stay inside
the same Gauss6 stage solve, add the missing lower-pair velocity/acceleration
rows to the MethodSpec itself, and survive off-axis or interbody checks without
changing the reference policy. v026-v029 matter because they pass these gates;
that is why FullVA is the residual object left after endpoint-node, projection,
and one-joint explanations are rejected.

This is the sentence the paper should keep returning to:

> The new method was discovered when the search moved from repairing endpoints
> after a Gauss step to enforcing lower-pair velocity and acceleration
> consistency inside the Gauss6 stage residual.

## Evidence And Claim Boundary

Accepted local claim:

- Method: `Gauss6/FullVA`.
- Method-order claim: sixth order under the smooth FullVA proof contract.
- Smooth observed cylindrical-chain position/velocity orders: `7.161/7.066`.
- Residual boundary: 132-row current route.
- Four-example mechanism coverage: single pendulum, double pendulum,
  four-link, slider-crank.
- Accepted dynamic-order examples: single pendulum and double pendulum.

Open or forbidden claims:

- Full source-paper TFE replacement remains open:
  `full_tfe_stage_replacement=false`.
- External source-policy superiority is forbidden under the current gate:
  source-policy rows are still open.
- Sparse runtime superiority is open: sparse structure is quantified, but
  dense `jacfwd` remains faster in measured wall time.
- Sharp-friction coarse regime is not solved as a practical default, although
  ultra-refinement recovers high-order behavior at quantified cost.
- Four-link and slider-crank are not accepted dynamic-order examples until
  true dynamic order rows or a residual-to-error theorem closes the gap.

## Recommended Main-Paper Structure

1. `Introduction`
   - Open with why constrained Lie-group integration is a hard scientific
     target: manifold state, DAE levels, lower-pair reactions, friction
     smoothness, residual identity, and reference policy.
   - Then ask the narrow question: can an LLM-assisted pipeline help discover a
     real numerical method while preserving the claim boundary?
   - State that paper drafting is downstream packaging, not the contribution.

2. `Related Work and Gap`
   - Present prior numerical work and inherited code paths as typed
     comparators first.
   - Then situate LLM-for-science systems as workflow motivation.
   - State the gap: claim-preserving integrator discovery
     under strict validators, not one-shot benchmark maximization, automated
     report generation, or a paper mainly describing the final integrator.

3. `How the Discovery Method Was Built`
   - Explain why the integrator is hard.
   - Explain inherited baselines as verifier questions or typed verifier questions.
   - Explain verifier setup before the four-example test environment.
   - Explain what a version means before the 48-version block table.
   - Show the FullVA narrowing trace before broader sparse/external details.

4. `Discovery Environment`
   - Define MethodSpec, ProblemSpec, EvidenceSpec, ClaimSpec, and ledgers.
   - Define L0-L3 sandbox levels.
   - Explain claim states and nonpromotion.

5. `Discovered Integrator Outcome: From Endpoint Repair to FullVA`
   - Walk through Gauss6 backbone, failed Lobatto, projection, PivotVA, FullVA.
   - Explain why FullVA is not output projection.
   - Include accepted method evidence.

6. `Numerical Test Environment`
   - Describe the four examples and their roles.
   - Separate dynamic-order examples from mechanism-coverage examples.

7. `Failed Attempts as Evidence`
   - Treat failed TFE, projection, sparse, and external comparison paths as
     evidence that defines the method boundary.

8. `Discussion, Limitations, Conclusion`
   - Explain what kind of scientific-agent discovery method this case supports.
   - Keep limitations explicit.

## Repeated Optimization Loop

Use the same five-pass loop whenever the paper is shortened, moved into a
different template, or converted into slides.

| Pass | Question | Required action | Failure signal |
| --- | --- | --- | --- |
| Order pass | Does the text still follow hard target -> inherited objects -> verifier -> examples -> 48 versions -> FullVA -> boundary? | Move generic LLM motivation, paper-writing, sparse/backend, and external-comparison prose after the numerical dependency chain. | The first page can be summarized as "LLM wrote/researched a paper" before the reader knows the numerical problem. |
| Evidence-role pass | Does each artifact have one role? | Label comparators, examples, version blocks, sparse rows, and external rows by what they can prove and what they cannot prove. | A baseline, coverage row, diagnostic, or harness is described as if it proves the method. |
| Version-meaning pass | Does the 48-version story explain claim movement? | For each block, state what was calibrated, rejected, promoted, quarantined, or forbidden. | The prose says "we tried many versions" without saying what next constraint each block created. |
| FullVA-hinge pass | Is v023-v029 still the discovered-outcome center? | Keep the three-gate filter visible: same Gauss6 stage solve, lower-pair V/A rows inside MethodSpec, off-axis/interbody survival without reference-policy drift. | The outcome reads as generic Gauss6, endpoint projection, Lobatto replacement, sparse engineering, or external benchmarking. |
| Positioning pass | Does the text still read as a method for discovering integrators? | Keep the first-page contribution focused on the verifier-centered discovery procedure, state objects, version semantics, and claim boundaries. | The paper reads as mainly an integrator description or as "LLM wrote a paper." |
| Boundary pass | Are accepted/open/forbidden claims still explicit? | Scan for TFE, sparse speed, external superiority, seventh order, and all-four dynamic-order overclaims after every rewrite. | A reader could infer a stronger theorem, source reproduction, speed claim, or external comparison result than the artifacts support. |

The loop is deliberately repetitive. The goal is not stylistic polish first; it
is to keep the discovery chain reconstructable after every compression pass.

## Revision Checklist

- Does the abstract and introduction open with the hard numerical target before
  generic LLM/workflow motivation?
- Does the introduction explain why this numerical problem is hard before
  introducing the agentic question?
- Are inherited baselines described before the 48-version ledger?
- Is the verifier environment described before accepted claims are promoted?
- Are the four examples introduced as a test environment, not merely as final
  results?
- Is FullVA presented as the decisive technical turn?
- Are failed paths used as scientific evidence?
- Are all nonclaims preserved?
- Does every sentence about four-link/slider-crank avoid accepted dynamic-order
  wording?
- Does every external comparison sentence avoid superiority wording?
- Does the first page make clear that `Gauss6/FullVA` is the discovered
  integrator outcome, not the sole subject of the paper?
