# Rewrite outline: Gauss6/FullVA paper (target: CMAME, 25–30 pages)

Status: executed 2026-09-21. `main_cmame.tex` is now assembled from `parts/` by `assemble.py`; the
execution record of the experiments is in `EXPERIMENT_PLAN.md`. Deviations from this outline: the chain
horizon is `T = 0.5` (regular branch), E6 became a regular-branch check, E4/E5 centre on the double pendulum
(the other three public mechanisms are driven), E7 (solver envelope) was added, and the mechanism/architecture
schematics are drawn by `make_schematics.py`.

## The paper in one paragraph

Lower-pair mechanisms modelled in absolute coordinates are index-3 DAEs on a Lie group. We
integrate them with a three-stage Gauss collocation step whose stage system enforces the joint
constraints at position, velocity and acceleration level together with the Newton–Euler balance
(the FullVA stage system) and reconstructs the rotational endpoint with the exponential map. The
central observation is an exact algebraic identity: the 132-row implemented stage system has the
lifted reduced Gauss stage as its unique local root, i.e. the method *is* three-stage Gauss
collocation of the reduced joint-coordinate equations of motion, executed in absolute coordinates
without ever forming those equations. From the identity we obtain a sixth-order local error bound
whose only hypotheses are smoothness and a small-step threshold, with the remaining interfaces
(uniform inverse, solver tolerance) derived from them; the algebra, the perturbation lemmas and the
quadrature bound are machine-checked in Lean 4/Mathlib. Numerically we show sixth order on a
frictional two-body chain over a full period, sixth order on the ASME pendulum and closed-loop
benchmarks, the work/precision advantage over lower-order members of the same family and over a
public absolute-coordinate baseline, and the order reduction that a sharp friction law induces.

## Contributions (as they will be stated)

1. **Exact stage identity.** The implemented FullVA stage system is exactly reduced Gauss
   collocation lifted to absolute coordinates (Lemma, both directions, Lean-checked). This explains
   why acceleration-level constraint enforcement costs no order and why reaction forces are
   available at every stage.
2. **Order theorem with derived interfaces.** Sixth-order local defect `C_loc = C_G + C_E + C_N c_η`
   under smoothness; the uniform-inverse and solver-envelope hypotheses follow from smoothness for
   `h ≤ h_0` (Neumann perturbation, simplified-Newton decay), with `h_0` quantified on the benchmark
   and shown to be set by the friction-law curvature, not by the collocation structure.
3. **Machine-checked analysis.** 57 theorems in Lean 4/Mathlib: the 132 row identities, the
   perturbation chain with explicit constants, Butcher `B(6)/C(3)/D(3)`, the Peano quadrature bound.
4. **Numerical evidence.** Sixth order on the smooth frictional chain over `T = 1` with six step
   sizes; the Gauss family (orders 2, 4, 6) and a public absolute-coordinate baseline on the same
   problems in work/precision form; sixth order on the four ASME mechanisms including the closed
   loops; the friction-smoothness sweep that locates the order-reduction regime.

Not claimed (one sentence in the introduction, one paragraph in Limitations): reproduction of the
temporal-finite-element source paper on its own problems; that is a comparison at the level of
formal order and of a formula-level proxy only.

## Section plan (page budget 28)

| # | Section | Pages | Source in current manuscript | Action |
| --- | --- | ---: | --- | --- |
| 1 | Introduction | 2 | Intro (rewritten, see `intro_draft.tex`) | rewrite |
| 2 | Related work | 1.5 | Related work (950 words) | tighten, add ~20 references (list below) |
| 3 | Problem setting | 2 | Mathematical setting + Nomenclature | merge; notation table shrinks to half a page |
| 4 | The Gauss6/FullVA step | 4 | Accepted one-step integrator | keep stage system, joint coordinates, endpoint reconstruction, Algorithm 1; cut implementation-fidelity and source-map prose |
| 5 | Analysis | 6 | Conditional sixth-order theorem | keep P1 as the single assumption; Lemma exact stage identity; branch selection; P2-from-P1; endpoint defect; endpoint closure; inexact Newton; Newton envelope; local-to-global; theorem; one paragraph on Lean with the statement-to-theorem table |
| 6 | Numerical experiments | 7 | Numerical evidence + Four-example validation (rebuilt around E1–E6) | rewrite with new runs |
| 7 | Limitations | 0.5 | Diagnostic boundaries + Limitations | one list: sharp friction, open-chain scope of the identity, `h_0` size, TFE non-reproduction |
| 8 | Conclusions | 0.5 | Conclusions | rewrite |
| A | Lower-pair constraint formulas | 2 | Lower-pair constraint formulas | keep as appendix |
| B | Lean statement map | 1 | tab:lean-development | keep |
| C | Reproducibility | 0.5 | Reproducibility package + Supplementary source package | one paragraph: repository URL, how to rerun E1–E6, Lean check command |

Cut entirely: Validation protocol (§ "Validation protocol"), cross-paper same-test appendix (17
tables), algorithm-to-source map, Table 8 proof-dependency map (folded into the Lean table),
exact-identity diagnostic table (one sentence + one figure), P2 constants table (kept as one table
in Analysis), all "diagnostic/policy/boundary/claim" vocabulary, all internal identifiers
(`local_Gauss6_FullVA`, `hi2022_rA_half`, `submission_ready`, …).

## Figures (target 8) and tables (target 7)

Figures: (F1) stage architecture schematic (redraw, no "non-claim" boxes); (F2) mechanism sketches:
chain with joint frames, four ASME mechanisms; (F3) E1 convergence, position/velocity/orientation/
constraint, six step sizes, reference slope 6; (F4) E2 work/precision, Gauss 2/4/6 stages on the
chain; (F5) E3 friction-smoothness sweep: observed order vs Stribeck velocity; (F6) E4 ASME
convergence, four panels; (F7) E5 work/precision against the public rA baseline on the pendulums;
(F8) E6 long-time drift: constraint norms and energy/momentum over `T = 20`.

Tables: (T1) notation; (T2) stage system row inventory (72 + 24 + 36); (T3) theorem constants and
Lean theorem names (merged); (T4) `h_0` in two norms with/without friction; (T5) E1 orders; (T6) E4
orders on the four mechanisms; (T7) E5 runtime and Newton-iteration counts.

## References to add (≈20)

Lie-group integrators: Iserles–Munthe-Kaas–Nørsett–Zanna (Acta Numerica 2000); Celledoni–Marthinsen–
Owren (2014 survey); Hairer–Lubich–Wanner (Geometric Numerical Integration); Bou-Rabee–Marsden
(Hamilton–Pontryagin on Lie groups). Multibody DAE: Arnold–Brüls (Lie-group generalized-α, 2007/
2011); Brüls–Arnold–Cardona (2012 CMAME); Sonneville–Cardona–Brüls (geometrically exact beams,
2014); Betsch–Steinmann (constrained mechanical systems, energy-momentum, 2002); Bauchau–Laulusa
(review of constraint enforcement); Jay (SPARK3 Lobatto for index-3, 1998/2007); Lunk–Simeon;
Petzold–Lötstedt (index reduction); Ascher–Petzold (book). Friction: Pennestrì et al. (friction
models review 2016). Absolute vs relative coordinates: Nikravesh; Shabana; Jain (Lie-group robot
dynamics). Collocation order theory: Hairer–Nørsett–Wanner I; Butcher (book).

## What happens to the validator ledger

The 750-file ledger in `validation/paper_v047_cylindrical_chain/` pins hundreds of phrases of the
current manuscript. It stays as the historical record of the 2026 audit trail, frozen at the
commit before the rewrite, and its validators are removed from the routine chain. The new
manuscript gets one validator (`validate_manuscript.py`): LaTeX log clean, every number in the
tables equals the value in the corresponding results CSV/JSON, Lean gate synced, arXiv copy in sync.
