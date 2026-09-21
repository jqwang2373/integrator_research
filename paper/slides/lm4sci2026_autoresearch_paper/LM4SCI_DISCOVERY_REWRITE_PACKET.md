# LM4Sci Discovery Rewrite Packet

This packet turns the story pipeline into reusable main-text prose for an
8-page LM4Sci/COLM-style paper about discovering new integrators with LLM
agents. It is a drafting aid, not new evidence. Use it when rewriting
`main.tex` so the paper stays centered on the verifier-centered discovery
method rather than on automatic paper writing or on describing the final
integrator alone.

## North Star

The paper should make one narrow discovery-method claim:

> A verifier-centered LLM-assisted research environment can discover new
> scientific-computing integrators by keeping retained, rejected, and
> quarantined method hypotheses in a claim-controlled trace.

The bounded conditional sixth-order `Gauss6/FullVA` result is the discovered
outcome that stress-tests this claim. Everything in the main text should either
prepare the discovery-method claim, prove why it is credible, or protect its
boundary.

## Three Non-Negotiable Story Rules

1. **Comparators are verifier questions, not a leaderboard.** Inherited
   Lie-kinematic, Gauss, ASME, Lobatto/TFE, friction, sparse, and external
   objects must be written as typed questions about representation trust, local
   validity, endpoint-map changes, scaling, and nonpromotion boundaries.
2. **The four examples are an ordered ambiguity ladder.** Passing an order gate
   opens the next ambiguity; it does not transfer the same claim type to a
   coverage gate. Single and double pendulum carry accepted local dynamic-order
   evidence; four-link and slider-crank carry coverage and reaction-consistency
   evidence.
3. **The FullVA hinge is a three-gate filter.** After v025, smaller endpoint
   drift is not enough. The candidate must live inside the same Gauss6 stage
   solve, add lower-pair velocity/acceleration rows inside `MethodSpec`, and
   survive off-axis/interbody stress without reference-policy drift.

## One-Paragraph Paper Pitch

We describe a verifier-centered method for using LLM agents to discover new
scientific-computing integrators. Lie-group constrained multibody integration
is a hard discovery target
because rotations live on manifolds, constrained dynamics carry
position/velocity/acceleration consequences, lower-pair joints introduce
reaction multipliers, friction changes smoothness, and Newton residual rows
define the actual one-step map. The project therefore treated inherited
Lie-kinematic, Gauss, ASME-mechanism, Lobatto/TFE, friction, sparse, and
external-comparison work as verifier questions rather than as a flat
leaderboard. A verifier-centered agent environment separated `MethodSpec`,
`ProblemSpec`, `EvidenceSpec`, `ClaimSpec`, and ledgers, then used four ASME
mechanisms as a test environment: single and double pendulum carry accepted
local dynamic-order evidence, while four-link and slider-crank carry
closed-loop coverage and reaction-consistency evidence. Across 48 versions,
failed Lobatto-node, projection, sparse, and source-policy explanations became
constraints for the next hypothesis. The decisive turn was v026-v029: velocity
and acceleration consistency for lower-pair joints moved from endpoint repair
into the Gauss6 stage residual, yielding the bounded `Gauss6/FullVA`
discovered outcome. The paper's contribution is this verifier-centered
discovery method and its claim boundary, not automated manuscript generation
or a description of the integrator alone.

## Section Rewrite Targets

| Section | Required role | Lead sentence to preserve | First thing to cut |
| --- | --- | --- | --- |
| Abstract | State the discovery method and full dependency chain in one paragraph. | "We describe a verifier-centered method for using LLM agents to discover new scientific-computing integrators." | Artifact-count details and generic LLM motivation. |
| Introduction | Make the hard numerical target primary, then introduce the agentic question. | "The difficult part is not proposing another quadrature rule; it is preserving the identity of the residual being solved." | LLM-for-science survey prose before the numerical problem. |
| Related Work and Gap | Present prior work as typed verifier questions. | "We treat inherited numerical methods as verifier questions, not a leaderboard." | Leaderboard language and long generic related-work paragraphs. |
| How Discovery Method Was Built | Walk through hard problem, inherited objects, verifier setup, four examples, 48-version evolution, version-block roles, FullVA hinge. | "A version is not a prompt attempt." | Chronological prose that does not explain claim movement. |
| Discovery Environment | Explain why verifier verdicts become next-version constraints. | "The verifier did not replace proof; it controlled claim promotion." | Repeated file inventories. |
| Discovered Outcome | Isolate the v023-v029 turn. | "Projection closed a visible symptom, but the verifier rejected it as the method identity." | Sparse/backend or external-comparison details. |
| Numerical Evidence | Separate ordered example roles. | "Passing an order gate opens the next ambiguity; it does not transfer the same claim type to a coverage gate." | Any wording implying all-four dynamic order. |
| Discussion / Limitations | Generalize only to verifier-centered method discovery. | "The strongest paper is not the broadest claim; it is the claim whose promotion path can be reconstructed." | Repeated caveats already stated in tables. |

## Abstract Rewrite Skeleton

Use one paragraph with seven moves:

1. Hard target: manifold constrained MBD makes method identity fragile.
2. Prior objects: inherited numerical work supplies typed verifier questions.
3. Environment: the agent operates through specs, ledgers, and validators.
4. Testbed: four examples have different claim roles.
5. Evolution: 48 versions narrow hypotheses through verifier verdicts.
6. Ledger meaning: role-coded blocks explain what all 48 versions contributed.
7. Method turn and boundary: FullVA rows enter the residual; stronger claims
   remain open or forbidden.

Reusable abstract core:

```text
We study a 48-version, verifier-centered LLM-assisted search for a
Lie-group constrained multibody integrator. The search did not begin from a
clean leaderboard: it inherited Lie-kinematic, Gauss, ASME-mechanism,
Lobatto/TFE, friction, sparse, and external-comparison directions, each of
which was treated as a typed verifier question with a bounded claim role. The research
environment separated method, problem, evidence, claim, and ledger objects so
that failed promotions became next-version constraints. The decisive discovery
was not Gauss6 alone and not endpoint projection; it was the movement of
lower-pair velocity and acceleration consistency into the Gauss6 stage residual,
yielding the bounded `Gauss6/FullVA` method identity.
```

## Introduction Rewrite Skeleton

### Paragraph 1: hard numerical target

```text
Lie-group constrained multibody integration is difficult because the numerical
method is defined by more than an update formula. Rotations live on a manifold;
holonomic constraints have position-, velocity-, and acceleration-level
consequences; lower-pair joints introduce multipliers and reaction forces; and
friction can change the smoothness regime. In this setting, the residual rows,
stage variables, endpoint policy, tolerance, and reference policy determine the
actual one-step map. A convergence plot can therefore be correct for the wrong
reason: projection, a reduced surrogate, a reference-policy drift, or a
diagnostic residual may explain the data instead of the claimed method.
```

### Paragraph 2: why an agent is useful and dangerous

```text
This is exactly the kind of search where an LLM-assisted research environment
can help and where it can mislead. The agent can inspect code, propose residual
variants, run bounded experiments, summarize failures, and maintain a long
version history. But if method, problem, evidence, and claim states are not
separated, the same system can promote a diagnostic row into a method claim, a
coverage row into an order theorem, or an external harness into a superiority
claim. The scientific question is therefore whether an agent can help discover
a method while preserving the boundary of what has actually been verified.
```

### Paragraph 3: prior objects before verifier

```text
The search inherited useful numerical objects before the agentic pipeline was
organized: Lie-group kinematic conventions, conservative Gauss/Lie mechanics,
ASME-style mechanism anchors, trapezoidal/BDF/Lobatto baselines, a
Gauss-Lobatto/TFE source target, friction variants, sparse/backend probes, and
external same-test harnesses. These objects were not a single leaderboard. They
were typed verifier questions: some fixed representation, some supplied baselines,
some became rejected explanations, and some imposed source-policy boundaries.
None alone defined the accepted `Gauss6/FullVA` method.
```

### Paragraph 4: dependency chain

```text
The resulting story is a dependency chain. The hard numerical target makes
claim drift plausible; inherited comparators define what must be separated; the
verifier environment controls promotion; the four examples define typed test
roles; the 48 versions record hypothesis narrowing; and the FullVA hinge
identifies the new method. Reordering this chain around generic LLM motivation
or artifact volume weakens the contribution.
```

## Related Work Rewrite Skeleton

The related work should not read as a broad survey. Its job is to explain what
was inherited and what those inherited objects could not prove.

```text
Prior numerical work supplies the verifier questions under which the discovery
should be read. Lie-group integrators and RKMK/CF-style updates fix high-order
manifold transport, but they do not close lower-pair DAE dynamics. Conservative
Gauss/Lie mechanics show that smooth high-order rigid-body integration is
possible, but not that multipliers, reaction forces, and frictional lower-pair
constraints are handled. ASME mechanisms provide public-style anchors, while
trapezoidal, BDF, Lobatto, TFE, and friction variants provide alternative
explanations or stronger source targets. We therefore treat prior work as
verifier questions rather than a leaderboard: each comparator either initializes
a convention, tests a nearby hypothesis, or defines a nonpromotion boundary.
```

Then add only one short LLM-for-science paragraph:

```text
LLM-for-science systems motivate the workflow question, but they are not the
main scientific object here. This paper studies a narrow scientific-computing
case: whether a verifier-centered agent can preserve enough state across a
long search to make a new numerical method identifiable.
```

## Verifier Environment Rewrite Skeleton

```text
The environment was designed as a claim-promotion state machine. Each run
carried a `MethodSpec` describing stage variables, residual rows, endpoint
policy, solver tolerance, and backend policy; a `ProblemSpec` describing the
mechanism, geometry, drivers, friction law, time window, step sizes, and
reference policy; an `EvidenceSpec` describing CSV, JSON, plot, proof, and
report artifacts; a `ClaimSpec` describing accepted, open, and forbidden
wording; and a ledger recording the version transition. The agent could
propose and execute hypotheses, but a claim could change only when validators
accepted method identity, problem identity, evidence artifacts, and wording
boundary.
```

Failure-to-next-version paragraph:

```text
This changed the role of failure. A failed Lobatto row, a projection repair,
or a sparse solver diagnostic was not simply discarded. The verifier translated
the failure into the next constraint: split the diagnostic from the claimed
method, freeze the reference policy, keep an incomplete proof open, accept
coverage without order promotion, or separate method validity from speed and
external comparison. This translation rule is what makes the 48-version ledger
a scientific narrowing argument rather than a log of attempts.
```

## Four-Example Test Environment Rewrite Skeleton

```text
The four ASME mechanisms form an ordered ambiguity ladder rather than four
interchangeable demos. The single pendulum tests a clean exact-driven
lower-pair dynamic-order row. The double pendulum tests whether the FullVA
residual survives an interbody double-revolute joint under a method-side
self-reference policy. The four-link example tests closed-loop lower-pair graph
structure, rank, loop closure, and reaction consistency. The slider-crank
example tests mixed revolute/prismatic closure and reaction residuals. Passing
an order gate opens the next ambiguity; it does not transfer the same claim
type to a coverage gate. The accepted claim must keep these roles separate:
single and double pendulum support local dynamic-order evidence, while
four-link and slider-crank support coverage and reaction consistency without
accepted asymptotic dynamic-order promotion.
```

## 48-Version Story Rewrite Skeleton

Use the following block when space is tight:

```text
The 48 versions were not 48 prompt attempts. They were a sequence of bounded
research contracts: each version proposed a candidate explanation, generated
artifacts, received a verifier verdict, and constrained the next question. The
first versions fixed SO(3) measurements, right-action conventions, and
public-style mechanism anchors. The next block showed that constrained DAE
level, endpoint policy, friction, automatic differentiation, and quaternion
transport were part of method identity. Gauss6 then became the smooth
high-order backbone, while adaptive, trapezoidal, BDF, Lobatto, friction, and
source-target variants became verifier questions or caveats. The central v023-v029
block ruled out direct Lobatto-node replacement and endpoint projection before
promoting stage-level velocity and acceleration rows. Later sparse,
lower-pair, four-example, and external-harness versions managed scaling and
claim boundaries rather than changing the method claim.
```

## FullVA Hinge Rewrite Skeleton

This is the most important technical paragraph:

```text
The accepted method was discovered at the FullVA hinge. v023 moved the search
into a full absolute-coordinate lower-pair DAE and exposed endpoint velocity
defects. v024 tested a direct Lobatto-node replacement and rejected it as the
accepted full residual. v025 showed that projection could close a visible
endpoint symptom, but the verifier demoted it because it changed the trajectory
map and could not define the method identity. The next constraint was therefore
to move the missing consistency equations inside the nonlinear solve: v026
added stage velocity rows, v027 added stage acceleration rows, v028 generalized
the lower-pair rows, and v029 showed that PivotVA/FullVA survived an interbody
double-revolute DAE. The discovery was not "try Gauss6"; it was preserving
Gauss6 as the backbone while making lower-pair V/A consistency part of the
stage residual.
```

After v025, the verifier used a stricter three-gate filter. Endpoint drift
reduction no longer promoted a candidate. The candidate had to remain in the
same Gauss6 stage solve, express lower-pair velocity and acceleration
consistency as `MethodSpec` residual rows, and survive off-axis/interbody
stress without reference-policy drift.

Short version:

```text
Projection repaired an endpoint symptom; FullVA changed the residual being
solved. That distinction is the new method.
```

## Evidence And Boundary Rewrite Skeleton

```text
The accepted evidence is deliberately local. `Gauss6/FullVA` has conditional
sixth-order support under the smooth FullVA proof contract and accepted
single/double-pendulum dynamic-order gates. The four-link and slider-crank
rows support closed-loop lower-pair coverage and reaction consistency, not
asymptotic dynamic order. The same ledger keeps stronger claims unpromoted:
full TFE replacement remains open, sparse wall-clock superiority remains open,
external superiority is not claimed, and observed finite-window slopes above
six support the sixth-order claim rather than a seventh-order theorem.
```

## Final Discussion Rewrite Skeleton

```text
This case supports a narrow lesson for scientific agents. The useful agentic
behavior was not automatic manuscript generation and not unrestricted
autonomous science. It was the maintenance of a verifier-controlled search
state in which retained components, rejected explanations, artifacts, and
claim boundaries remained reconstructable. In a problem where small changes to
residual rows, endpoint policy, or reference policy change the method identity,
that reconstruction is part of the scientific result.
```

## Forbidden Rewrites

Do not use these formulations:

- "The agent wrote the paper and discovered the method." Use: "The paper
  reports a method-discovery path maintained by a verifier-centered agent
  environment."
- "All four examples prove sixth-order dynamics." Use: "Single and double
  pendulum carry accepted dynamic-order evidence; four-link and slider-crank
  carry coverage and reaction-consistency evidence."
- "The method is Gauss6." Use: "Gauss6 is the backbone; FullVA residual rows
  define the accepted method identity."
- "Projection is part of the method." Use: "Projection was tested and rejected
  as method identity."
- "The smooth slopes prove seventh order." Use: "The observed slopes support a
  conditional sixth-order claim."
- "Sparse speedup is achieved." Use: "Sparse structure is documented; sparse
  wall-clock superiority remains open."
- "External baselines show superiority." Use: "External same-test rows are a
  scaffold; superiority is not claimed."
- "TFE was reproduced." Use: "Full source-paper TFE replacement remains open."

## Main-Text Editing Order

When directly editing `main.tex`, use this order:

1. Replace or compress the abstract using the seven-move skeleton.
2. Lock the introduction around hard target -> prior comparators -> verifier
   environment -> four-example testbed -> 48-version narrowing ->
   version-block roles -> FullVA turn.
3. Compress related work into verifier questions plus one LLM-for-science
   bridge paragraph.
4. Preserve the v023-v029 FullVA hinge before cutting any generic LLM,
   sparse, external-harness, or artifact-count prose.
5. Preserve the four-example role boundary before cutting the claim snapshot.
6. After every edit, scan for forbidden rewrites above.
