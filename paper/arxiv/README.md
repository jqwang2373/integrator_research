# arXiv version

Generated from `../main_cmame.tex` by `../../validation/paper_v047_cylindrical_chain/build_arxiv_version.py`; do not edit `main_arxiv.tex`
by hand.  Compile locally with `latexmk -pdf main_arxiv.tex` (pdflatex, TeX Live 2023 or later;
no BibTeX run is needed because the bibliography is inline).

## Metadata for the arXiv submission form

**Title.** A Conditional Sixth-Order Lie-Group FullVA Integrator for Lower-Pair Mechanisms

**Abstract** (1887 characters, limit 1920):

Lower-pair mechanisms require Lie-group integrators that keep position, velocity, and acceleration constraints synchronized. This paper studies Gauss6/FullVA, a three-stage Gauss collocation integrator whose stage system couples absolute-coordinate stage kinematics, Newton-Euler balance, and lower-pair constraints at position, velocity, and acceleration level in one square nonlinear system with Lie-group endpoint reconstruction. We show that the implemented stage system is exactly three-stage Gauss collocation of the reduced joint-coordinate equation of motion written in absolute coordinates: the lifted reduced Gauss stage satisfies all 132 stage rows identically. Building on this identity, the main theorem proves a conditional sixth-order same-initial-state reported-grid estimate for the selected smooth branch. The local defect is the sum of the classical Gauss endpoint defect, an endpoint-closure perturbation, and an inexact-Newton perturbation; the retained hypotheses are compact-tube regularity, uniform local inverses, a one-step stability scale, and the branch-selected solver envelope eta_h <= c_eta h^7. The algebraic stage identity, the perturbation lemmas with their explicit constants, the Gauss tableau order conditions, and the quadrature-defect bound are machine-checked in Lean 4/Mathlib. On a smooth cylindrical-chain benchmark the implementation records position/velocity orders 7.161/7.066 as branch-consistency diagnostics. Four ASME-style mechanisms exercise the same residual vocabulary: single- and double-pendulum rows provide dynamic-order evidence, while four-link and slider-crank rows provide closed-loop constraint/reaction consistency. Residual-to-error promotion, full external same-test reproduction, and complete source-paper TFE residual replacement are not claimed; the comparison to TFE is kept at the formal-order and diagnostic levels.

**Suggested categories.**
- math.NA (Numerical Analysis) - primary
- cs.CE (Computational Engineering, Finance, and Science) - cross-list
- physics.comp-ph (Computational Physics) - optional cross-list

**Comments field (suggestion).** 13 figures. Lean 4/Mathlib development and
reproducibility records accompany the manuscript.

## Upload

1. Upload `arxiv_submission.zip` (this directory's `main_arxiv.tex` and the figures listed below;
   arXiv detects the main file automatically).
2. Choose the license (arXiv non-exclusive license is the minimal choice; CC BY 4.0 if the journal
   policy allows it).
3. Paste the title, abstract and categories above.

## Figures shipped in the archive

- `Figure_10_closed_loop_true_dynamic_order.png`
- `Figure_11_method_stage_architecture.png`
- `Figure_12_all_method_result_matrix.png`
- `Figure_13_work_precision_compendium.png`
- `Figure_1_convergence.png`
- `Figure_2_asme_lower_pair_graph_bridge.png`
- `Figure_3_asme_closed_loop_kinematic_fullva.png`
- `Figure_4_order_closure_blend.png`
- `Figure_5_velocity_compression.png`
- `Figure_6_sparse_speed_gap.png`
- `Figure_7_strict_common_reference_work_precision.png`
- `Figure_8_claim_boundary_limitations.png`
- `Figure_9_coarse_baseline_work_precision.png`
