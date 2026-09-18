import Mathlib

/-!
# Stage-residual perturbation criterion (Kantorovich-type root lemma)

Abstract form of `lem:stage-residual-defect` and `lem:inexact-newton` of the CMAME
manuscript (`main_cmame.tex`), stated on real Banach spaces with explicit constants.

Dictionary with the manuscript:

* `Φ : E → F` is the row-scaled implemented stage residual `F_{A,h}(·; y)` at one fixed
  transition (`E = F = ℝ¹³²` in the paper; here arbitrary Banach spaces).
* `Z₀` is the base point, the lifted Gauss stage `Z_G(y, h)`.
* `A : F →L[ℝ] E` plays the role of the inverse Jacobian `J_h⁻¹ = (D_Z F_{A,h}(Z_G))⁻¹`, with
  `‖A‖ ≤ M`.
* The **linearization hypothesis** `‖A (Φ u - Φ v) - (u - v)‖ ≤ ½ ‖u - v‖` on a ball is the
  "strong local residual inverse / averaged-Jacobian" condition (P2).  It follows from the
  derivative-form hypotheses `‖J_h⁻¹‖ ≤ M`, `‖D_Z F_{A,h}(Z) - J_h‖ ≤ δ` on the ball and
  `M δ ≤ ½` by the mean value inequality; see `linearization_of_fderiv_bound`.  With
  `δ = L ρ_h`, `ρ_h = 2 M C_R h⁷`, this is exactly the manuscript's smallness condition
  `2 M² L C_R h⁷ ≤ ½` in Eq. `stage-pert-small-step`.

Conclusions:

* `exists_root_of_linearization`: a root `Z_A` exists in the contraction ball of radius
  `ρ_h = 2 M ‖Φ Z_G‖` (Eq. `stage-pert-radius`), and it is unique in the linearization ball.
* `norm_sub_le_of_linearization`: any root in the linearization ball satisfies
  `‖Z_A - Z_G‖ ≤ 2 M ‖Φ Z_G‖`, hence `≤ C_Z h⁷` with `C_Z = 2 M C_R`
  (Eq. `stage-pert-root-bound`).
* `inexact_newton_stage_bound`: the computed iterate satisfies `‖Z̃_A - Z_A‖ ≤ 2 M_A η_h`
  (first half of Eq. `inexact-newton-stage-output-bounds`).
-/

open Metric Set Function
open scoped NNReal

namespace IntegratorOrderProof

variable {E F : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
  [NormedAddCommGroup F] [NormedSpace ℝ F]

/-- The simplified-Newton map `T Z = Z - A (Φ Z)` with frozen inverse Jacobian `A`. -/
def newtonMap (Φ : E → F) (A : F →L[ℝ] E) (Z : E) : E := Z - A (Φ Z)

theorem newtonMap_sub (Φ : E → F) (A : F →L[ℝ] E) (u v : E) :
    newtonMap Φ A u - newtonMap Φ A v = (u - v) - A (Φ u - Φ v) := by
  simp only [newtonMap, map_sub]; abel

/-- **Root bound from the linearization hypothesis.**  If `Φ u = 0` and the linearization
inequality holds at the pair `(u, v)`, then `‖u - v‖ ≤ 2 M ‖Φ v‖`.  With `u = Z_A`,
`v = Z_G` this is Eq. `stage-pert-root-bound`; with `u = Z_A`, `v = Z̃_A` it is the
inexact-Newton stage bound. -/
theorem norm_sub_le_of_linearization (Φ : E → F) (A : F →L[ℝ] E) (u v : E) {M : ℝ}
    (hA : ‖A‖ ≤ M)
    (hlin : ‖A (Φ u - Φ v) - (u - v)‖ ≤ (1 / 2) * ‖u - v‖) (hu : Φ u = 0) :
    ‖u - v‖ ≤ 2 * M * ‖Φ v‖ := by
  rw [hu, zero_sub, map_neg] at hlin
  have h1 : ‖A (Φ v) + (u - v)‖ ≤ (1 / 2) * ‖u - v‖ := by
    have e : -A (Φ v) - (u - v) = -(A (Φ v) + (u - v)) := by abel
    rwa [e, norm_neg] at hlin
  have h2 : ‖A (Φ v)‖ ≤ M * ‖Φ v‖ := A.le_of_opNorm_le hA _
  have h3 : ‖u - v‖ ≤ ‖A (Φ v) + (u - v)‖ + ‖A (Φ v)‖ := by
    calc ‖u - v‖ = ‖(A (Φ v) + (u - v)) - A (Φ v)‖ := by congr 1; abel
      _ ≤ ‖A (Φ v) + (u - v)‖ + ‖A (Φ v)‖ := norm_sub_le _ _
  linarith

/-- Uniqueness of the root inside the linearization ball (the "unique root in the contraction
ball" clause of `lem:stage-residual-defect`). -/
theorem root_unique_of_linearization (Φ : E → F) (A : F →L[ℝ] E) (Z₀ : E) {ρ : ℝ}
    (hlin : ∀ u ∈ closedBall Z₀ ρ, ∀ v ∈ closedBall Z₀ ρ,
      ‖A (Φ u - Φ v) - (u - v)‖ ≤ (1 / 2) * ‖u - v‖)
    {u v : E} (hu : u ∈ closedBall Z₀ ρ) (hv : v ∈ closedBall Z₀ ρ)
    (hΦu : Φ u = 0) (hΦv : Φ v = 0) : u = v := by
  have h := hlin u hu v hv
  rw [hΦu, hΦv, sub_zero, map_zero, zero_sub, norm_neg] at h
  have : ‖u - v‖ ≤ 0 := by linarith
  exact sub_eq_zero.mp (norm_le_zero_iff.mp this)

/-- **Kantorovich-type existence of the accepted stage root** (`lem:stage-residual-defect`).
On a complete space, if `‖A‖ ≤ M`, `A` is injective, the linearization inequality holds on the
ball of radius `ρ ≥ 2 M ‖Φ Z₀‖`, then the simplified-Newton map is a `½`-contraction of the ball
of radius `ρ_h = 2 M ‖Φ Z₀‖` into itself and its fixed point is a root of `Φ`. -/
theorem exists_root_of_linearization [CompleteSpace E]
    (Φ : E → F) (A : F →L[ℝ] E) (Z₀ : E) {M ρ : ℝ}
    (hM : 0 ≤ M) (hA : ‖A‖ ≤ M) (hinj : Injective A)
    (hρ : 2 * M * ‖Φ Z₀‖ ≤ ρ)
    (hlin : ∀ u ∈ closedBall Z₀ ρ, ∀ v ∈ closedBall Z₀ ρ,
      ‖A (Φ u - Φ v) - (u - v)‖ ≤ (1 / 2) * ‖u - v‖) :
    ∃ Z ∈ closedBall Z₀ (2 * M * ‖Φ Z₀‖), Φ Z = 0 := by
  set T := newtonMap Φ A with hT
  set r := 2 * M * ‖Φ Z₀‖ with hr
  have hr0 : 0 ≤ r := by positivity
  have hsub : closedBall Z₀ r ⊆ closedBall Z₀ ρ := closedBall_subset_closedBall hρ
  -- `T` is a ½-contraction on the linearization ball
  have hcontr : ∀ u ∈ closedBall Z₀ ρ, ∀ v ∈ closedBall Z₀ ρ,
      ‖T u - T v‖ ≤ (1 / 2) * ‖u - v‖ := by
    intro u hu v hv
    rw [hT, newtonMap_sub, ← norm_neg, neg_sub]
    exact hlin u hu v hv
  -- `T Z₀ - Z₀ = -A (Φ Z₀)`
  have hTZ₀ : ‖T Z₀ - Z₀‖ ≤ M * ‖Φ Z₀‖ := by
    have e : T Z₀ - Z₀ = -(A (Φ Z₀)) := by simp [hT, newtonMap]
    rw [e, norm_neg]
    exact A.le_of_opNorm_le hA _
  -- `T` maps the contraction ball into itself
  have hmaps : MapsTo T (closedBall Z₀ r) (closedBall Z₀ r) := by
    intro u hu
    have hu' := hu
    rw [mem_closedBall, dist_eq_norm] at hu' ⊢
    calc ‖T u - Z₀‖ = ‖(T u - T Z₀) + (T Z₀ - Z₀)‖ := by congr 1; abel
      _ ≤ ‖T u - T Z₀‖ + ‖T Z₀ - Z₀‖ := norm_add_le _ _
      _ ≤ (1 / 2) * ‖u - Z₀‖ + M * ‖Φ Z₀‖ :=
          add_le_add (hcontr u (hsub hu) Z₀ (hsub (mem_closedBall_self hr0))) hTZ₀
      _ ≤ (1 / 2) * r + M * ‖Φ Z₀‖ := by gcongr
      _ = r := by rw [hr]; ring
  have hlip : LipschitzOnWith (1 / 2 : ℝ≥0) T (closedBall Z₀ r) := by
    refine LipschitzOnWith.of_dist_le_mul fun u hu v hv => ?_
    rw [dist_eq_norm, dist_eq_norm]
    have hc : ((1 / 2 : ℝ≥0) : ℝ) = 1 / 2 := by norm_num
    rw [hc]
    exact hcontr u (hsub hu) v (hsub hv)
  have hcomplete : IsComplete (closedBall Z₀ r) := Metric.isClosed_closedBall.isComplete
  have hK1 : (1 / 2 : ℝ≥0) < 1 := NNReal.coe_lt_coe.mp (by norm_num)
  have hK : ContractingWith (1 / 2 : ℝ≥0) (hmaps.restrict T _ _) :=
    ⟨hK1, hlip.mapsToRestrict hmaps⟩
  obtain ⟨Z, hZ, hfix, -, -⟩ :=
    ContractingWith.exists_fixedPoint' hcomplete hmaps hK (mem_closedBall_self hr0)
      (edist_ne_top _ _)
  refine ⟨Z, hZ, ?_⟩
  have hTZ : Z - A (Φ Z) = Z := hfix
  have h0 : A (Φ Z) = 0 := sub_eq_self.mp hTZ
  exact hinj (by rw [h0, map_zero])

/-- The manuscript's constants: if `‖Φ Z_G‖ ≤ C_R h⁷` and the step window satisfies
`2 M C_R h⁷ ≤ r` (Eq. `stage-pert-small-step`, first half), then the accepted root exists in
the ball of radius `C_Z h⁷ = 2 M C_R h⁷` and is unique in the linearization ball
(Eq. `stage-pert-root-bound`). -/
theorem stage_root_exists_unique [CompleteSpace E]
    (Φ : E → F) (A : F →L[ℝ] E) (ZG : E) {M CR h r : ℝ}
    (hM : 0 ≤ M) (hA : ‖A‖ ≤ M) (hinj : Injective A)
    (hres : ‖Φ ZG‖ ≤ CR * h ^ 7) (hstep : 2 * M * CR * h ^ 7 ≤ r)
    (hlin : ∀ u ∈ closedBall ZG r, ∀ v ∈ closedBall ZG r,
      ‖A (Φ u - Φ v) - (u - v)‖ ≤ (1 / 2) * ‖u - v‖) :
    ∃ ZA ∈ closedBall ZG (2 * M * CR * h ^ 7), Φ ZA = 0 ∧
      ∀ Z' ∈ closedBall ZG r, Φ Z' = 0 → Z' = ZA := by
  have hρ : 2 * M * ‖Φ ZG‖ ≤ r := by
    calc 2 * M * ‖Φ ZG‖ ≤ 2 * M * (CR * h ^ 7) := by gcongr
      _ = 2 * M * CR * h ^ 7 := by ring
      _ ≤ r := hstep
  obtain ⟨ZA, hZA, hroot⟩ := exists_root_of_linearization Φ A ZG hM hA hinj hρ hlin
  have hZA' : ZA ∈ closedBall ZG (2 * M * CR * h ^ 7) := by
    refine closedBall_subset_closedBall ?_ hZA
    calc 2 * M * ‖Φ ZG‖ ≤ 2 * M * (CR * h ^ 7) := by gcongr
      _ = 2 * M * CR * h ^ 7 := by ring
  refine ⟨ZA, hZA', hroot, fun Z' hZ' hΦ => ?_⟩
  exact root_unique_of_linearization Φ A ZG hlin hZ' (closedBall_subset_closedBall hρ hZA) hΦ hroot

/-- **Inexact Newton tolerance scale** (`lem:inexact-newton`, stage half).  If `Z_A` is the exact
root, the linearization inequality holds at `Z_A` on the branch ball, and the computed iterate
`Z'` lies in that ball with residual `‖Φ Z'‖ ≤ η`, then `‖Z' - Z_A‖ ≤ 2 M_A η`. -/
theorem inexact_newton_stage_bound (Φ : E → F) (A : F →L[ℝ] E) (ZA : E) {M ρ η : ℝ}
    (hA : ‖A‖ ≤ M)
    (hlin : ∀ u ∈ closedBall ZA ρ, ‖A (Φ u - Φ ZA) - (u - ZA)‖ ≤ (1 / 2) * ‖u - ZA‖)
    (hroot : Φ ZA = 0) {Z' : E} (hZ' : Z' ∈ closedBall ZA ρ) (hη : ‖Φ Z'‖ ≤ η) :
    ‖Z' - ZA‖ ≤ 2 * M * η := by
  have h := hlin Z' hZ'
  have h' : ‖A (Φ ZA - Φ Z') - (ZA - Z')‖ ≤ (1 / 2) * ‖ZA - Z'‖ := by
    have e : A (Φ ZA - Φ Z') - (ZA - Z') = -(A (Φ Z' - Φ ZA) - (Z' - ZA)) := by
      rw [map_sub, map_sub]; abel
    rw [e, norm_neg, norm_sub_rev ZA Z']
    exact h
  have hb := norm_sub_le_of_linearization Φ A ZA Z' hA h' hroot
  rw [norm_sub_rev] at hb
  have hM : 0 ≤ M := (norm_nonneg A).trans hA
  calc ‖Z' - ZA‖ ≤ 2 * M * ‖Φ Z'‖ := hb
    _ ≤ 2 * M * η := by gcongr

/-- Output half of `lem:inexact-newton`: if the full endpoint-output map `P` is `M_N`-Lipschitz
between the two stage points, `‖P Z' - P Z_A‖ ≤ C_N η` with `C_N = 2 M_A M_N`. -/
theorem inexact_newton_output_bound {G : Type*} [NormedAddCommGroup G]
    (Φ : E → F) (A : F →L[ℝ] E) (ZA : E) {M ρ η MN : ℝ}
    (hA : ‖A‖ ≤ M) (hMN : 0 ≤ MN)
    (hlin : ∀ u ∈ closedBall ZA ρ, ‖A (Φ u - Φ ZA) - (u - ZA)‖ ≤ (1 / 2) * ‖u - ZA‖)
    (hroot : Φ ZA = 0) {Z' : E} (hZ' : Z' ∈ closedBall ZA ρ) (hη : ‖Φ Z'‖ ≤ η)
    (P : E → G) (hP : ‖P Z' - P ZA‖ ≤ MN * ‖Z' - ZA‖) :
    ‖P Z' - P ZA‖ ≤ (2 * M * MN) * η := by
  have hs := inexact_newton_stage_bound Φ A ZA hA hlin hroot hZ' hη
  calc ‖P Z' - P ZA‖ ≤ MN * ‖Z' - ZA‖ := hP
    _ ≤ MN * (2 * M * η) := by gcongr
    _ = (2 * M * MN) * η := by ring

/-- **Derivative form of the P2 hypothesis.**  If `Φ` is differentiable on the closed ball with
derivative `Φ'`, `J` is an invertible Jacobian with `‖J⁻¹‖ ≤ M`, `‖Φ' z - J‖ ≤ δ` on the ball and
`M δ ≤ ½`, then the linearization inequality holds on the ball with `A = J⁻¹`.
(With `δ = L ρ` this is the manuscript's `‖D²F‖ ≤ L`, `2 M² L C_R h⁷ ≤ ½` route via the mean
value inequality.) -/
theorem linearization_of_fderiv_bound (Φ : E → F) (Φ' : E → E →L[ℝ] F) (J : E ≃L[ℝ] F)
    (Z₀ : E) {M δ ρ : ℝ} (hM : 0 ≤ M) (hJ : ‖(J.symm : F →L[ℝ] E)‖ ≤ M)
    (hderiv : ∀ z ∈ closedBall Z₀ ρ, HasFDerivWithinAt Φ (Φ' z) (closedBall Z₀ ρ) z)
    (hδ : ∀ z ∈ closedBall Z₀ ρ, ‖Φ' z - (J : E →L[ℝ] F)‖ ≤ δ)
    (hsmall : M * δ ≤ 1 / 2) :
    ∀ u ∈ closedBall Z₀ ρ, ∀ v ∈ closedBall Z₀ ρ,
      ‖(J.symm : F →L[ℝ] E) (Φ u - Φ v) - (u - v)‖ ≤ (1 / 2) * ‖u - v‖ := by
  intro u hu v hv
  have hmv : ‖Φ u - Φ v - (J : E →L[ℝ] F) (u - v)‖ ≤ δ * ‖u - v‖ :=
    (convex_closedBall Z₀ ρ).norm_image_sub_le_of_norm_hasFDerivWithin_le' hderiv hδ hv hu
  have e : (J.symm : F →L[ℝ] E) (Φ u - Φ v) - (u - v)
      = (J.symm : F →L[ℝ] E) (Φ u - Φ v - (J : E →L[ℝ] F) (u - v)) := by
    rw [map_sub]
    simp
  rw [e]
  calc ‖(J.symm : F →L[ℝ] E) (Φ u - Φ v - (J : E →L[ℝ] F) (u - v))‖
      ≤ M * ‖Φ u - Φ v - (J : E →L[ℝ] F) (u - v)‖ := (J.symm : F →L[ℝ] E).le_of_opNorm_le hJ _
    _ ≤ M * (δ * ‖u - v‖) := by gcongr
    _ = (M * δ) * ‖u - v‖ := by ring
    _ ≤ (1 / 2) * ‖u - v‖ := by gcongr

end IntegratorOrderProof
