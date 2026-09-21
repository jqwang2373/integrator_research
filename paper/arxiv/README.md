# arXiv version

Generated from `../main_cmame.tex` by `../rewrite/build_derived.py`; do not edit `main_arxiv.tex` by hand.
Compile with `latexmk -pdf main_arxiv.tex` (pdflatex; the bibliography is inline, no BibTeX run).

## Metadata

**Title.** A sixth-order Lie-group Gauss collocation integrator for lower-pair mechanisms with position-, velocity- and acceleration-level constraints

**Abstract** (1863 characters, limit 1920):

Multibody systems with lower-pair joints in absolute coordinates are index-3 differential-algebraic equations on a Lie group. We study Gauss6/FullVA, a three-stage Gauss collocation step whose stage system enforces the joint constraints at position, velocity and acceleration level together with the Newton-Euler balance, and reconstructs the rotational endpoint through the exponential map. The central result is an exact algebraic identity: the lifted reduced Gauss stage, obtained by collocating the joint-coordinate equations of motion and lifting the result to absolute coordinates, satisfies every one of the 132 implemented stage rows, and conversely every root of the non-dynamic rows on the regular branch is such a lift. The method is therefore reduced Gauss collocation executed in absolute coordinates. Everything the implementation adds, the velocity-level endpoint closure and the inexact Newton solve, is an O(h^7) perturbation, which gives a sixth-order error bound whose only standing hypothesis is smoothness on a compact neighbourhood of the trajectory; the solver and inverse interfaces are derived for h h_0, and h_0 is quantified and traced to the curvature of the friction law. The row identities, the perturbation chain and the Butcher conditions are machine-checked in Lean 4 with Mathlib (57 theorems). Numerically the method is sixth order on a frictional two-body chain and on the ASME double pendulum, reproduces the driven ASME mechanisms to roundoff, is two to seven orders of magnitude more accurate than the one- and two-stage members of the same family at the same Newton work, and reaches errors below 10^{-10} on the double pendulum where the public absolute-coordinate codes have errors of order one. A sweep of the Stribeck velocity locates the regime in which a sharp friction law reduces the observed order on coarse grids.

**Suggested categories.**
- math.NA (Numerical Analysis) - primary
- cs.CE (Computational Engineering, Finance, and Science) - cross-list
- physics.comp-ph (Computational Physics) - optional cross-list

**Comments field (suggestion).** 9 figures. Lean 4/Mathlib development and experiment scripts accompany the manuscript.

## Upload

Upload `arxiv_submission.zip`; arXiv detects the main file automatically.

## Figures

- `Figure_1_chain_schematic.png`
- `Figure_2_method_overview.png`
- `Figure_3_e1_convergence.png`
- `Figure_4_e2_gauss_family.png`
- `Figure_5_e3_friction_sweep.png`
- `Figure_6_mechanisms.png`
- `Figure_7_e4_benchmarks.png`
- `Figure_8_e5_double_pendulum.png`
- `Figure_9_e6_regular_branch.png`
