# Lean Formalization Pointer

Status: **supplementary machine-checked proof of the conditional perturbation chain and of the
exact stage identity; changes no claim state**. It does not discharge P1 for the concrete
mechanism, does not close P7 or any source-policy row (OC4/OC6/OC12), and does not make the CMAME
package submission ready. P2 and P6 are reduced to P1 plus a small-step threshold
(`lem:p2-from-p1`, `lem:newton-envelope`); the perturbation and decay steps of those lemmas are
machine-checked, the block-structure argument for `J_0` is on paper.

A copy of the Lean sources (no build artefacts) ships inside the paper package at
`paper_v047_cylindrical_chain/lean/`; `build_exact_stage_identity_gate.py` records whether that
copy is byte-identical to the development below.

## Location

The Lean 4 project lives outside this OneDrive tree on purpose (Mathlib build cache is several GB
of small files):

```text
~/lean/integrator_order_proof          (WSL home; Lean 4.34.0, Mathlib v4.34.0)
```

Build and check:

```bash
cd ~/lean/integrator_order_proof
lake exe cache get
lake build
lake env lean scripts/Axioms.lean      # every theorem: [propext, Classical.choice, Quot.sound]
```

## What is machine-checked

| Manuscript object (`paper_v047_cylindrical_chain/main_cmame.tex`) | Lean theorem |
| --- | --- |
| `lem:stage-residual-defect` (branch selection; general Kantorovich form with `C_Z = 2 M C_R`, now `C_R = 0`) | `exists_root_of_linearization`, `stage_root_exists_unique`, `norm_sub_le_of_linearization` |
| P2 derivative form (`‖J⁻¹‖ ≤ M`, `‖D²F‖ ≤ L`, `2 M² L C_R h⁷ ≤ ½`; vacuous radius when `C_R = 0`) | `linearization_of_fderiv_bound` |
| `lem:inexact-newton` (`C_N = 2 M_A M_N`) | `inexact_newton_stage_bound`, `inexact_newton_output_bound` |
| `lem:endpoint-closure` (`C_E`) | `endpoint_closure_exists`, `endpoint_correction_bound_h7` |
| `lem:local-global-transfer` (`Γ_s(T)`, first-exit bootstrap) | `gronwallFactor`, `geom_sum_le_gronwallFactor`, `local_to_global`, `reported_grid_bound` |
| Eq. `g6fva-local-defect-theorem` (`C_loc`) | `local_defect_bound`, `local_defect_bound_paper` |
| Eqs. `g6fva-reduced-grid-bound`, `g6fva-reported-grid-bound` | `conditional_sixth_order_grid_bound` |
| D1/D2 identities, 36 Newton–Euler rows of `run_v047.py` (formerly the P5 direct substitution) | `NewtonEuler.transRow_eq`, `NewtonEuler.rotRow_eq`, `NewtonEuler.dynamic_rows_vanish` |
| 96 non-dynamic rows of `run_v047.py` ⇔ lower-pair constraints at all levels + reduced joint-coordinate Gauss collocation; hence `F_{A,h}(Z_G) = 0` exactly (`C_R = 0`) | `FullVA.Transition.nondynamic_rows_vanish`, `reducedCollocation_of_rows`, `nondynamic_rows_iff` |
| Lemma B (Gauss6 tableau order conditions `B(6)`, `C(3)`, `D(3)`, `¬B(7)`) for the literals in `quaternion_pendulum.py` | `Gauss6.B_six`, `Gauss6.C_three`, `Gauss6.D_three`, `Gauss6.not_B_seven` |
| Peano-type quadrature error and Gauss6 `h⁷` step defect (engine behind `C_G h⁷`) | `quadrature_error_bound`, `gauss6_quadrature_error`, `gauss6_step_defect` |
| `lem:p2-from-p1`, Eq. `p2-perturbation-bound` (`‖J_h⁻¹‖ ≤ 2‖J_0⁻¹‖` when `‖J_h − J_0‖ ≤ δ`, `‖J_0⁻¹‖δ ≤ ½`; finite dimension) | `norm_le_of_perturbed`, `uniform_inverse_of_perturbation` |
| `lem:newton-envelope`, Eq. `newton-envelope-decay` (simplified Newton: `‖Z^k − Z_G‖ ≤ 2⁻ᵏ‖Z⁰ − Z_G‖`, residual `≤ L_F 2⁻ᵏ‖Z⁰ − Z_G‖`; the `c_η h⁷` stopping rule is reached) | `simplified_newton_residual_decay` |

Proved constant for the endpoint closure is `2 M_ri C_raw`, sharper than the printed
`4 M_ri C_raw`; `Cloc_le_ClocPaper` records that the proved bound implies the printed one.

## Audit finding (2026-09-17)

`paper_v047_cylindrical_chain/LEAN_RESIDUAL_ROW_FAMILY_AUDIT.md`: the stage system displayed in
`main_cmame.tex` (body-level collocation rows, 72 kinematic + 24 lower-pair) does not match the
implemented residual (72 constraint rows at position/velocity/acceleration level + 24
joint-coordinate collocation rows). The implemented stage system is exactly reduced
joint-coordinate Gauss collocation plus exact constraint enforcement, so the stage residual at
the lifted Gauss stage is identically zero. No claim state is changed by this note.

## Manuscript compaction (2026-09-17)

`paper_v047_cylindrical_chain/main_cmame.tex` was rewritten around the exact stage identity:
13047 lines / 259 pages became 4042 lines / 88 pages (after the 2026-09-17 additions below). The method section now displays the
implemented rows (72 constraint rows, 24 joint-coordinate collocation rows, 36 Newton–Euler rows),
the theorem section proves `F_{A,h}(Z_G)=0` (`lem:exact-stage-identity`) and the three-term local
defect `C_loc = C_G + C_E + C_N c_eta`, and the PS2/primitive-Taylor route is gone. The original is
kept as `main_cmame_pre_v049_backup.tex` and in git. The new proof gate is
`EXACT_STAGE_IDENTITY_GATE.md/json` (`build_/validate_exact_stage_identity_gate.py`); it runs the
Lean axiom check when the toolchain is present and supersedes PROOF_CLOSURE_MANIFEST,
PROOF_CLAIM_TRACEABILITY_AUDIT, CMAME_STRICT_PROOF_AUDIT,
CMAME_STRICT_PROOF_POLICY_RECONCILIATION_AUDIT, CMAME_PROOF_STYLE_AUDIT, and
NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE (files kept, marked superseded, removed from the
package chain). Global claim state is unchanged: `submission_ready=false`, OC4/OC6/OC12 open.

## Additions (2026-09-17, second pass)

- `lem:p2-from-p1`: under P1 and the chart assumption (joint coordinates complete the lower-pair
  constraints to a chart), the stage Jacobian `J_h = J_0 + O(h)` with `J_0` block triangular and
  invertible, so P2 holds for `h ≤ h_0` with `‖J_h⁻¹‖ ≤ 2‖J_0⁻¹‖` (Lean:
  `uniform_inverse_of_perturbation`).
- `lem:newton-envelope`: the simplified Newton iteration from the Gauss predictor halves the
  distance to `Z_G` each step and the residual decays like `2⁻ᵏ`, so the `‖F‖ ≤ c_η h⁷` stopping
  rule of P6 is met after `O(log(1/h))` iterations (Lean: `simplified_newton_residual_decay`).
  The existing regime sweep (`PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.md`, policy `scaled_h7_c1e4`,
  `T = 0.08`) instantiates the rule on the reported grids.
- `EXACT_STAGE_IDENTITY_NUMERICAL_CHECK.md/json/csv`
  (`run_/validate_exact_stage_identity_numerical_check.py`): converged stages of the real
  residual at Newton tolerance `1e-13`, read in the reduced chart, give reduced Gauss collocation
  defects `≤ 9.0e-15`, perpendicular components `≤ 2.1e-15`, sliding-row factorization mismatch
  `≤ 9.1e-15` for `h ∈ {0.04, 0.02, 0.01}` on `T = 0.08`. Consistency check of the transcription,
  not a proof input.
- `P2_CONSTANTS_NUMERICAL_CHECK.md/json/csv` (`run_/validate_p2_constants_numerical_check.py`):
  the implemented Jacobian at the converged stage (`J_h`) and at the root of the `h = 0` stage
  system (`J_0`, reproduces the lifted endpoint to `1e-12`). Euclidean norm on the implemented
  layout: `M_0 = max ‖J_0⁻¹‖ ≈ 18–28`, `C_J = max ‖J_h − J_0‖/h ≈ 750–960`, observed
  `‖J_h⁻¹‖/‖J_0⁻¹‖ ≤ 1.55` on all reported grids (lemma conclusion holds), but the Neumann
  sufficient condition `M_0‖J_h − J_0‖ ≤ ½` would need `h ≤ 3e-5` — the lemma's `h_0` is
  pessimistic by three orders of magnitude in this norm. The lifted endpoint predictor is `O(h)`
  from `Z_G` (3.2/2.1/1.1); the Algorithm-1 predictor zeroes the angular velocity/acceleration
  guesses and stays at distance ≈ 50 with a first Newton step that expands by up to 18%.
  `lem:newton-envelope` is therefore stated for predictors inside the contraction ball (the lifted
  endpoint predictor qualifies); the implemented predictor's ball membership stays inside P6.
- Manuscript: `tab:exact-identity-check`, `tab:p2-constants-check` (numerical section), `tab:lean-development` (appendix,
  statement-to-theorem map), modelling sentence for the second pair (fixed sliding direction,
  moving rotation axis), closed-loop scope sentence for `lem:exact-stage-identity`, observed-order
  remark (slopes above six are pre-asymptotic). `main.tex` and `main_concise.tex` carry a legacy
  status note pointing to `main_cmame.tex`.

## What remains a hypothesis in Lean

- Gauss three-stage collocation order and Lie-group chart transfer (Lemmas A/B of
  `ORDER_PROOF_LEDGER.md`) enter as `‖𝓔(Z_G) - φ_h(y)‖ ≤ C_G h⁷`. The tableau order conditions
  and the quadrature-defect bound are proved; Butcher's theorem and the variation-of-constants
  transfer to the one-step error are not.
- P1 (smoothness, full row rank of `Φ_q`, mass-matrix bounds on the compact tube) and the chart
  assumption of `lem:p2-from-p1`; the `J_0` block-structure argument and the `O(h)` distance of the
  lifted endpoint predictor are paper arguments. P2 and the reachability of the P6 envelope from the
  contraction ball are then derived; the implemented predictor's membership in that ball is not
  (it is `O(1)` away in the Euclidean norm and is confirmed only a posteriori).
- The 96 non-dynamic rows and the 36 Newton–Euler rows are proved to vanish at the lifted Gauss
  stage (`C_R = 0`); P4/P5 as separate interfaces no longer exist.
- Nothing numerical about the concrete cylindrical chain is verified in Lean; the numerical
  identity check above is a floating-point diagnostic, not a proof.
