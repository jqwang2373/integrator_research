import IntegratorOrderProof.PerturbationChain.Contraction

/-!
# Uniform inverse bounds under small perturbation, and Newton residual decay

Two lemmas that reduce the P2 / P6 interfaces of the manuscript to P1-type data plus a small
step size.

* `norm_le_of_perturbed` / `uniform_inverse_of_perturbation`: if `J₀` is invertible with
  `‖J₀⁻¹‖ ≤ M₀` and `‖J - J₀‖ ≤ δ` with `M₀ δ ≤ ½`, then `J` is invertible (finite dimension) with
  `‖J⁻¹‖ ≤ 2 M₀`.  In the manuscript, `J₀` is the `h → 0` limit of the stage Jacobian, whose
  invertibility is a P1 statement (chart Jacobian and constrained mass matrix), and
  `J_h = J₀ + O(h)`; hence the uniform stage inverse of P2 holds for `h ≤ h₀`.
* `simplified_newton_residual_decay`: under the linearization hypothesis of
  `exists_root_of_linearization`, the simplified Newton iterates from any point of the
  contraction ball converge geometrically to the root, and the residual decays like `2⁻ᵏ`.
  Hence a stopping rule `‖Φ(Z^k)‖ ≤ c_η h⁷` is met after finitely many iterations: the P6
  envelope is achievable by construction on the accepted branch.
-/

open Metric Set Function
open scoped NNReal

namespace IntegratorOrderProof

section Inverse

variable {E : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]

/-- Lower bound for a perturbed operator: `‖u‖ ≤ 2 M₀ ‖J u‖`. -/
theorem norm_le_of_perturbed (J₀inv : E →L[ℝ] E) (J₀ J : E →L[ℝ] E) {M₀ δ : ℝ}
    (hM₀ : 0 ≤ M₀) (hinv : ‖J₀inv‖ ≤ M₀) (hleft : ∀ u, J₀inv (J₀ u) = u)
    (hδ : ‖J - J₀‖ ≤ δ) (hsmall : M₀ * δ ≤ 1 / 2) (u : E) :
    ‖u‖ ≤ 2 * M₀ * ‖J u‖ := by
  have h1 : ‖u‖ ≤ M₀ * ‖J₀ u‖ := by
    calc ‖u‖ = ‖J₀inv (J₀ u)‖ := by rw [hleft u]
      _ ≤ M₀ * ‖J₀ u‖ := J₀inv.le_of_opNorm_le hinv _
  have h2 : ‖J₀ u‖ ≤ ‖J u‖ + δ * ‖u‖ := by
    have e : J₀ u = J u - (J - J₀) u := by simp
    calc ‖J₀ u‖ = ‖J u - (J - J₀) u‖ := by rw [e]
      _ ≤ ‖J u‖ + ‖(J - J₀) u‖ := norm_sub_le _ _
      _ ≤ ‖J u‖ + δ * ‖u‖ := by gcongr; exact (J - J₀).le_of_opNorm_le hδ u
  have h3 : ‖u‖ ≤ M₀ * ‖J u‖ + (M₀ * δ) * ‖u‖ := by nlinarith [h1, h2, norm_nonneg (J u)]
  have h4 : (M₀ * δ) * ‖u‖ ≤ (1 / 2) * ‖u‖ := by gcongr
  linarith

/-- **Uniform inverse under perturbation** (finite dimension).  `J` is bijective and its inverse
has operator norm at most `2 M₀`. -/
theorem uniform_inverse_of_perturbation [FiniteDimensional ℝ E]
    (J₀inv : E →L[ℝ] E) (J₀ J : E →L[ℝ] E) {M₀ δ : ℝ}
    (hM₀ : 0 ≤ M₀) (hinv : ‖J₀inv‖ ≤ M₀) (hleft : ∀ u, J₀inv (J₀ u) = u)
    (hδ : ‖J - J₀‖ ≤ δ) (hsmall : M₀ * δ ≤ 1 / 2) :
    ∃ Jinv : E →L[ℝ] E, (∀ u, Jinv (J u) = u) ∧ (∀ v, J (Jinv v) = v) ∧ ‖Jinv‖ ≤ 2 * M₀ := by
  have hlow := norm_le_of_perturbed J₀inv J₀ J hM₀ hinv hleft hδ hsmall
  -- injective
  have hinj : Injective J := by
    intro a b hab
    have : ‖a - b‖ ≤ 2 * M₀ * ‖J (a - b)‖ := hlow (a - b)
    rw [map_sub, hab, sub_self, norm_zero, mul_zero] at this
    exact sub_eq_zero.mp (norm_le_zero_iff.mp this)
  -- injective linear endomorphism of a finite-dimensional space is bijective
  have hsurj : Surjective J := (LinearMap.injective_iff_surjective (f := (J : E →ₗ[ℝ] E))).mp hinj
  let e : E ≃ₗ[ℝ] E := LinearEquiv.ofBijective (J : E →ₗ[ℝ] E) ⟨hinj, hsurj⟩
  let einv : E →L[ℝ] E := LinearMap.toContinuousLinearMap e.symm.toLinearMap
  refine ⟨einv, ?_, ?_, ?_⟩
  · intro u
    show e.symm (J u) = u
    exact e.symm_apply_apply u
  · intro v
    show J (e.symm v) = v
    exact e.apply_symm_apply v
  · refine ContinuousLinearMap.opNorm_le_bound _ (by positivity) fun v => ?_
    have hv : J (einv v) = v := e.apply_symm_apply v
    calc ‖einv v‖ ≤ 2 * M₀ * ‖J (einv v)‖ := hlow _
      _ = 2 * M₀ * ‖v‖ := by rw [hv]

end Inverse

section Newton

variable {E F : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
  [NormedAddCommGroup F] [NormedSpace ℝ F]

/-- **Residual decay of the simplified Newton iteration.**  Under the linearization hypothesis on
the ball `B(Z₀, ρ)`, if `Z_G ∈ B(Z₀, ρ)` is a root and the iteration `Z^{k+1} = Z^k - A (Φ Z^k)`
stays in the ball, then `‖Z^k - Z_G‖ ≤ 2⁻ᵏ ‖Z⁰ - Z_G‖` and, if `Φ` is `L_Φ`-Lipschitz on the
ball, `‖Φ Z^k‖ ≤ L_Φ 2⁻ᵏ ‖Z⁰ - Z_G‖`.  Any tolerance `η > 0` is therefore reached after
finitely many iterations. -/
theorem simplified_newton_residual_decay (Φ : E → F) (A : F →L[ℝ] E) (Z₀ ZG : E) {ρ LΦ : ℝ}
    (hLΦ : 0 ≤ LΦ)
    (hlin : ∀ u ∈ closedBall Z₀ ρ, ∀ v ∈ closedBall Z₀ ρ,
      ‖A (Φ u - Φ v) - (u - v)‖ ≤ (1 / 2) * ‖u - v‖)
    (hZG : ZG ∈ closedBall Z₀ ρ) (hroot : Φ ZG = 0)
    (hLip : ∀ u ∈ closedBall Z₀ ρ, ‖Φ u - Φ ZG‖ ≤ LΦ * ‖u - ZG‖)
    (Z : ℕ → E)
    (hstep : ∀ k, Z (k + 1) = newtonMap Φ A (Z k))
    (hball : ∀ k, Z k ∈ closedBall Z₀ ρ) :
    ∀ k, ‖Z k - ZG‖ ≤ (1 / 2) ^ k * ‖Z 0 - ZG‖ ∧ ‖Φ (Z k)‖ ≤ LΦ * ((1 / 2) ^ k * ‖Z 0 - ZG‖) := by
  have hdist : ∀ k, ‖Z k - ZG‖ ≤ (1 / 2) ^ k * ‖Z 0 - ZG‖ := by
    intro k
    induction k with
    | zero => simp
    | succ k ih =>
      have hfix : newtonMap Φ A ZG = ZG := by simp [newtonMap, hroot]
      have hc : ‖newtonMap Φ A (Z k) - newtonMap Φ A ZG‖ ≤ (1 / 2) * ‖Z k - ZG‖ := by
        rw [newtonMap_sub, ← norm_neg, neg_sub]
        exact hlin (Z k) (hball k) ZG hZG
      calc ‖Z (k + 1) - ZG‖ = ‖newtonMap Φ A (Z k) - newtonMap Φ A ZG‖ := by rw [hstep k, hfix]
        _ ≤ (1 / 2) * ‖Z k - ZG‖ := hc
        _ ≤ (1 / 2) * ((1 / 2) ^ k * ‖Z 0 - ZG‖) := by gcongr
        _ = (1 / 2) ^ (k + 1) * ‖Z 0 - ZG‖ := by ring
  intro k
  refine ⟨hdist k, ?_⟩
  calc ‖Φ (Z k)‖ = ‖Φ (Z k) - Φ ZG‖ := by rw [hroot, sub_zero]
    _ ≤ LΦ * ‖Z k - ZG‖ := hLip (Z k) (hball k)
    _ ≤ LΦ * ((1 / 2) ^ k * ‖Z 0 - ZG‖) := by gcongr; exact hdist k

end Newton

end IntegratorOrderProof
