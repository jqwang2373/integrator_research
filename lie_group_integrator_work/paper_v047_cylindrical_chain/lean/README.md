# IntegratorOrderProof

Lean 4 + Mathlib formalization of the **conditional sixth-order theorem chain** for the
`Gauss6/FullVA` Lie-group integrator of the CMAME manuscript
`lie_group_integrator_work/paper_v047_cylindrical_chain/main_cmame.tex`
(theorem `thm:g6fullva-order`), the exact stage identity (all 132 implemented rows vanish at the
lifted reduced Gauss stage), the Gauss6 tableau order conditions with a Peano-type `h⁷`
quadrature-defect bound, and the two perturbation lemmas that reduce the P2 and P6 interfaces to
P1 plus a small-step threshold (`lem:p2-from-p1`, `lem:newton-envelope`).

A copy of these sources ships in the paper package at `paper_v047_cylindrical_chain/lean/`.

Toolchain: `leanprover/lean4:v4.34.0`, Mathlib tag `v4.34.0` (pinned in `lakefile.toml`).

```bash
lake exe cache get          # once, fetches Mathlib oleans
lake build                  # builds everything (no sorry, autoImplicit off)
lake env lean scripts/Axioms.lean   # every theorem: [propext, Classical.choice, Quot.sound]
lake env lean scripts/Lint.lean     # Batteries linter over the library
scripts/check.sh                    # the three steps above
```

`scripts/Axioms.lean` enumerates every theorem of the library automatically (no hand-kept list)
and fails if any depends on `sorryAx` or on a non-standard axiom.

## What is proved

| Lean theorem | Manuscript object | Statement |
| --- | --- | --- |
| `exists_root_of_linearization`, `stage_root_exists_unique` | `lem:stage-residual-defect` (Kantorovich step) | accepted root `Z_A` exists in the ball of radius `2M‖F(Z_G)‖ ≤ 2 M C_R h⁷`, unique in the linearization ball |
| `linearization_of_fderiv_bound` | derivative form of P2 | `‖J⁻¹‖ ≤ M`, `‖DF - J‖ ≤ δ`, `Mδ ≤ ½` ⇒ linearization inequality (mean value) |
| `norm_sub_le_of_linearization` | Eq. `stage-pert-root-bound` | `‖Z_A - Z_G‖ ≤ 2 M ‖F(Z_G)‖`, i.e. `C_Z = 2 M C_R` |
| `inexact_newton_stage_bound`, `inexact_newton_output_bound` | `lem:inexact-newton` | `‖Z̃_A - Z_A‖ ≤ 2 M_A η`, `‖P(Z̃_A) - P(Z_A)‖ ≤ 2 M_A M_N η` |
| `endpoint_correction_bound`, `endpoint_correction_bound_h7`, `endpoint_closure_exists` | `lem:endpoint-closure` | closed endpoint exists; any right-inverse-type closed endpoint has `‖Δz_E‖ ≤ 2 M_ri ‖E(z_u)‖ ≤ 2 M_ri C_raw h⁷ ≤ 4 M_ri C_raw h⁷` |
| `gronwallFactor`, `geom_sum_le_gronwallFactor` | Eq. `local-global-lemma-gronwall-factor` | `h ∑_{k<n}(1+C_s h)^k ≤ Γ_s(T)` for `n h ≤ T` |
| `local_to_global`, `reported_grid_bound` | `lem:local-global-transfer` (restricted-domain form, first-exit bootstrap) | `y_n ∈ K` and `‖y_n - Y_n‖ ≤ C_ℓ Γ_s(T) h^p`; reporting map adds `C_𝓡` |
| `local_defect_bound`, `local_defect_bound_paper` | Eq. `g6fva-local-defect-theorem` | four-term chain, `C_loc = C_G + M_E·2MC_R + C_E + 2M_AM_N c_η` |
| `conditional_sixth_order_grid_bound` | Eqs. `g6fva-reduced-grid-bound`, `g6fva-reported-grid-bound` | `C_red = C_loc Γ_s(T)`, `C_qv = C_𝓡 C_red`, order `h⁶` |
| `NewtonEuler.transRow_eq`, `NewtonEuler.rotRow_eq` | D1/D2 identities (`NEWTON_EULER_BALANCE_IDENTITY_AUDIT`) | implemented `trans`/`rot` rows of `run_v047.py` equal the Newton/Euler balance defects, as ℝ³ vectors with the cross-product torque structure |
| `NewtonEuler.dynamic_rows_vanish`, `card_dynamic_rows` | dynamic half of `lem:exact-stage-identity` (formerly the P5 direct-substitution interface) | pointwise balance at the lifted stage ⇒ all `3·2·2·3 = 36` rows are exactly `0` |
| `FullVA.Transition.nondynamic_rows_vanish`, `reducedCollocation_of_rows`, `nondynamic_rows_iff` | the 96 non-dynamic rows (`pvel`, `u_block`, `pacc`, `w_block`, `constraints` of `run_v047.py`, with `joint_kinematics_jax` transcribed) | rows vanish **iff** lower-pair constraints hold at all three levels and the reduced joint coordinates `(s, θ, ṡ, θ̇)` satisfy Gauss collocation; so `F_{A,h}(Z_G) = 0` exactly and `C_R = 0` |
| `Gauss6.B_six`, `Gauss6.C_three`, `Gauss6.D_three`, `Gauss6.not_B_seven` | Lemma B of `ORDER_PROOF_LEDGER.md` (Butcher simplifying assumptions) | the exact tableau hard-coded in `quaternion_pendulum.py` satisfies `B(6)`, `C(3)`, `D(3)` and fails `B(7)`; with Butcher's theorem (not formalized) this is order exactly 6 |
| `quadrature_error_bound` | Peano-kernel step of the collocation order proof | rule exact on `x^k, k ≤ n` and `g ∈ C^{n+1}` ⇒ `|∫₀¹ g − ∑ bᵢ g(cᵢ)| ≤ (1 + ∑|bᵢ|) K / n!` |
| `gauss6_quadrature_error`, `gauss6_step_defect` | local quadrature defect behind `C_G h⁷` | `|∫₀¹ g − ∑ bᵢ g(cᵢ)| ≤ K/60`; on a step, `≤ h · K̃/60` with `K̃ = h⁶ sup|g⁽⁶⁾|` |
| `norm_le_of_perturbed`, `uniform_inverse_of_perturbation` | `lem:p2-from-p1`, Eq. `p2-perturbation-bound` | `‖J₀⁻¹‖ ≤ M₀`, `‖J − J₀‖ ≤ δ`, `M₀δ ≤ ½` ⇒ `J` bijective (finite dimension) with `‖J⁻¹‖ ≤ 2M₀`; applied to `J_h = J_0 + O(h)` |
| `simplified_newton_residual_decay` | `lem:newton-envelope`, Eq. `newton-envelope-decay` | simplified Newton from any point of the contraction ball: `‖Zᵏ − Z_G‖ ≤ 2⁻ᵏ‖Z⁰ − Z_G‖`, `‖Φ(Zᵏ)‖ ≤ L_Φ 2⁻ᵏ‖Z⁰ − Z_G‖`; the `c_η h⁷` stopping rule of P6 is reached |

## What is assumed (enters as hypotheses, not proved here)

* **Gauss collocation order and Lie-group chart transfer** (Lemmas A/B of `ORDER_PROOF_LEDGER.md`):
  the hypothesis `hG : ‖𝓔(Z_G) - φ_h(y)‖ ≤ C_G h⁷`.  The Gauss files prove the algebraic order
  conditions of the tableau and the quadrature-defect bound; Butcher's theorem and the
  variation-of-constants transfer from quadrature defect to one-step error are not formalized.
* **P1/P2/P6 interfaces**: inverse bounds `‖J⁻¹‖ ≤ M`, linearization on balls, endpoint right
  inverse `D ∘ B = id`, stability scale `1 + C_s h`, solver envelope `η ≤ c_η h⁷`, tube margin.
  `PerturbationChain/JacobianPerturbation.lean` reduces the inverse bound and the solver envelope
  to P1-type data plus `h ≤ h₀`; the block-structure argument for the `h → 0` Jacobian `J_0` and
  the `O(h)` predictor distance remain paper arguments.
* **Residual value at the lifted stage**: in the perturbation chain the implemented rows enter
  only through `hR : ‖F(Z_G)‖ ≤ C_R h⁷`; `FullVA/NonDynamicRows.lean` and
  `NewtonEuler/DynamicRows.lean` show all 132 rows are exactly `0` at the lifted reduced Gauss
  stage (`lem:exact-stage-identity`), so `C_R = 0` and the manuscript's three-term
  `C_loc = C_G + C_E + C_N c_η` is the special case of `local_defect_bound`.  See
  `lie_group_integrator_work/paper_v047_cylindrical_chain/LEAN_RESIDUAL_ROW_FAMILY_AUDIT.md`
  for the manuscript/implementation row-family mismatch this uncovered.
* **Lift property**: `hlift` says the lifted Gauss stage satisfies the pointwise Newton–Euler
  balance (the defining property of the smooth FullVA lift). What is proved is that the
  *implemented* rows are exactly the balance defects.
* Nothing about the concrete cylindrical-chain mechanism: no numerics, no interval arithmetic,
  no P7 residual-to-error transfer, no source-policy rows.

## Deviations from the manuscript (all in the safe direction)

* Endpoint constant: proved `C_E = 2 M_ri C_raw`; the manuscript states `4 M_ri C_raw`.
  `Cloc_le_ClocPaper` shows the proved bound implies the printed one.
* The P2 "strong local residual inverse" is taken directly as the averaged-Jacobian inequality
  `‖J⁻¹(F u - F v) - (u - v)‖ ≤ ½‖u - v‖`; the manuscript's derivative form
  (`‖D²F‖ ≤ L`, `2 M² L C_R h⁷ ≤ ½`) is derived from it in `linearization_of_fderiv_bound`.
* The accepted closure output is characterized as a right-inverse-type root `z_u + B w`
  inside the endpoint ball (the manuscript's "correction chosen no larger than a local
  right-inverse particular solution while the iterates remain in `B_{r_E}(z_*)`").
* Local-to-global is stated in the restricted-domain form (stability only along the trajectory,
  only while `y_n ∈ K`), which is the form the theorem actually consumes.

## Layout

```
IntegratorOrderProof/
  Basic.lean                          (1 + C h)^n ≤ exp(C h n)
  PerturbationChain/Contraction.lean  Kantorovich root lemma, inexact Newton, derivative form of P2
  PerturbationChain/EndpointClosure.lean  right-inverse endpoint closure
  PerturbationChain/LocalToGlobal.lean    Γ_s(T), discrete Gronwall with tube-retention bootstrap
  PerturbationChain/MainTheorem.lean      C_loc assembly, grid bounds
  PerturbationChain/JacobianPerturbation.lean  uniform inverse under O(h) perturbation; simplified Newton residual decay
scripts/Axioms.lean                       exhaustive axiom audit (every theorem of the library)
scripts/Lint.lean                         Batteries linter over the library
scripts/check.sh                          build + audit + lint
  NewtonEuler/DynamicRows.lean            36 Newton–Euler rows transcribed from run_v047.py
  FullVA/NonDynamicRows.lean              96 non-dynamic rows ⇔ constraints + reduced joint-coordinate Gauss collocation
  Gauss/Tableau.lean                      exact Gauss6 tableau, B(6)/C(3)/D(3), ¬B(7)
  Gauss/QuadratureError.lean              Peano-type quadrature error, Gauss6 h⁷ step defect
```
