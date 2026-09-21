import IntegratorOrderProof.PerturbationChain.Contraction

/-!
# Endpoint-closure perturbation (`lem:endpoint-closure`)

`Ecl : X → W` is the square endpoint-closure subsystem `E(z) = 0` (velocity-level/KKT closure
rows), `D` its Jacobian at the closed anchor `z_*`, and `B : W →L[ℝ] X` a right inverse of `D`
(`D ∘ B = id`, `‖B‖ ≤ M_{E,ri}`).  `zu` is the unclosed same-branch endpoint `Ψ_h^A = 𝓔_h(Z_A)`.

The linearization hypothesis `M_ri ‖E u - E v - D (u - v)‖ ≤ ½ ‖u - v‖` on `B_{r_E}(z_*)` is the
mean-value consequence of Eq. `endpoint-derivative-smallness`
(`‖DE(z) - DE(z_*)‖ ≤ L_E ‖z - z_*‖`, `M_ri L_E r_E ≤ ½`).

Two statements:

* `endpoint_correction_bound`: **any** closed endpoint of right-inverse type `z_E = zu + B w`
  that lies in the ball satisfies `‖z_E - zu‖ ≤ 2 M_ri ‖E(zu)‖`.  With the raw defect
  `‖E(zu)‖ ≤ C_{E,raw} h⁷` this gives `‖Δz_E‖ ≤ 2 M_ri C_{E,raw} h⁷`, which is sharper than the
  manuscript's `C_E = 4 M_ri C_{E,raw}` (Eq. `endpoint-correction-bound`).
* `endpoint_closure_exists`: such a closed endpoint exists (reduction of the right-inverse
  Newton iteration to the Kantorovich lemma on `W`).
-/

open Metric Set Function

namespace IntegratorOrderProof

variable {X W : Type*} [NormedAddCommGroup X] [NormedSpace ℝ X]
  [NormedAddCommGroup W] [NormedSpace ℝ W]

/-- Bound on a right-inverse-type endpoint correction. -/
theorem endpoint_correction_bound (Ecl : X → W) (D : X →L[ℝ] W) (B : W →L[ℝ] X)
    (zs zu zE : X) {Mri rE : ℝ} (hMri : 0 < Mri) (hB : ‖B‖ ≤ Mri)
    (hright : ∀ w, D (B w) = w)
    (hlin : ∀ u ∈ closedBall zs rE, ∀ v ∈ closedBall zs rE,
      Mri * ‖Ecl u - Ecl v - D (u - v)‖ ≤ (1 / 2) * ‖u - v‖)
    (hzu : zu ∈ closedBall zs rE) (hzE : zE ∈ closedBall zs rE)
    (hroot : Ecl zE = 0) (hrange : ∃ w, zE = zu + B w) :
    ‖zE - zu‖ ≤ 2 * Mri * ‖Ecl zu‖ := by
  obtain ⟨w, rfl⟩ := hrange
  have h := hlin _ hzE zu hzu
  rw [hroot, add_sub_cancel_left, hright, zero_sub] at h
  have hBw : ‖B w‖ ≤ Mri * ‖w‖ := B.le_of_opNorm_le hB w
  have h1 : ‖w + Ecl zu‖ ≤ (1 / 2) * ‖w‖ := by
    have e : -Ecl zu - w = -(w + Ecl zu) := by abel
    rw [e, norm_neg] at h
    have : Mri * ‖w + Ecl zu‖ ≤ Mri * ((1 / 2) * ‖w‖) := by
      calc Mri * ‖w + Ecl zu‖ ≤ (1 / 2) * ‖B w‖ := h
        _ ≤ (1 / 2) * (Mri * ‖w‖) := by gcongr
        _ = Mri * ((1 / 2) * ‖w‖) := by ring
    exact le_of_mul_le_mul_left this hMri
  have h2 : ‖w‖ ≤ 2 * ‖Ecl zu‖ := by
    have : ‖w‖ ≤ ‖w + Ecl zu‖ + ‖Ecl zu‖ := by
      calc ‖w‖ = ‖(w + Ecl zu) - Ecl zu‖ := by congr 1; abel
        _ ≤ ‖w + Ecl zu‖ + ‖Ecl zu‖ := norm_sub_le _ _
    linarith
  calc ‖zu + B w - zu‖ = ‖B w‖ := by congr 1; abel
    _ ≤ Mri * ‖w‖ := hBw
    _ ≤ Mri * (2 * ‖Ecl zu‖) := by gcongr
    _ = 2 * Mri * ‖Ecl zu‖ := by ring

/-- With the raw defect `‖E(zu)‖ ≤ C_raw h⁷`: `‖Δz_E‖ ≤ 2 M_ri C_raw h⁷ ≤ 4 M_ri C_raw h⁷`. -/
theorem endpoint_correction_bound_h7 (Ecl : X → W) (D : X →L[ℝ] W) (B : W →L[ℝ] X)
    (zs zu zE : X) {Mri rE Craw h : ℝ} (hMri : 0 < Mri) (hB : ‖B‖ ≤ Mri)
    (hright : ∀ w, D (B w) = w)
    (hlin : ∀ u ∈ closedBall zs rE, ∀ v ∈ closedBall zs rE,
      Mri * ‖Ecl u - Ecl v - D (u - v)‖ ≤ (1 / 2) * ‖u - v‖)
    (hzu : zu ∈ closedBall zs rE) (hzE : zE ∈ closedBall zs rE)
    (hroot : Ecl zE = 0) (hrange : ∃ w, zE = zu + B w)
    (hraw : ‖Ecl zu‖ ≤ Craw * h ^ 7) :
    ‖zE - zu‖ ≤ 2 * Mri * Craw * h ^ 7 ∧ ‖zE - zu‖ ≤ 4 * Mri * Craw * h ^ 7 := by
  have hb := endpoint_correction_bound Ecl D B zs zu zE hMri hB hright hlin hzu hzE hroot hrange
  have h2 : ‖zE - zu‖ ≤ 2 * Mri * Craw * h ^ 7 := by
    calc ‖zE - zu‖ ≤ 2 * Mri * ‖Ecl zu‖ := hb
      _ ≤ 2 * Mri * (Craw * h ^ 7) := by gcongr
      _ = 2 * Mri * Craw * h ^ 7 := by ring
  have hnn : 0 ≤ Craw * h ^ 7 := (norm_nonneg _).trans hraw
  refine ⟨h2, h2.trans ?_⟩
  nlinarith [hnn, hMri.le]

/-- **Existence of the closed endpoint** by reduction to the Kantorovich lemma on `W`:
`G w := E(zu + B w)` has `G' ≈ D ∘ B = id`, so the simplified Newton map `w ↦ w - G w` contracts.
Hypotheses: `zu ∈ B_{r_E/2}(z_*)`, raw defect `‖E(zu)‖ ≤ ε`, and the step window
`2 M_ri ε ≤ r_E/2` (so the iterates stay in `B_{r_E}(z_*)`). -/
theorem endpoint_closure_exists [CompleteSpace W] (Ecl : X → W) (D : X →L[ℝ] W) (B : W →L[ℝ] X)
    (zs zu : X) {Mri rE ε : ℝ} (hMri : 0 < Mri) (hB : ‖B‖ ≤ Mri)
    (hright : ∀ w, D (B w) = w)
    (hlin : ∀ u ∈ closedBall zs rE, ∀ v ∈ closedBall zs rE,
      Mri * ‖Ecl u - Ecl v - D (u - v)‖ ≤ (1 / 2) * ‖u - v‖)
    (hzu : zu ∈ closedBall zs (rE / 2)) (hε : ‖Ecl zu‖ ≤ ε) (hsmall : 2 * Mri * ε ≤ rE / 2) :
    ∃ w : W, Ecl (zu + B w) = 0 ∧ ‖w‖ ≤ 2 * ‖Ecl zu‖ := by
  set G : W → W := fun w => Ecl (zu + B w) with hG
  have hzu' : ‖zu - zs‖ ≤ rE / 2 := by rwa [mem_closedBall, dist_eq_norm] at hzu
  have hball : ∀ w ∈ closedBall (0 : W) (2 * ε), zu + B w ∈ closedBall zs rE := by
    intro w hw
    rw [mem_closedBall, dist_zero_right] at hw
    rw [mem_closedBall, dist_eq_norm]
    calc ‖zu + B w - zs‖ = ‖(zu - zs) + B w‖ := by congr 1; abel
      _ ≤ ‖zu - zs‖ + ‖B w‖ := norm_add_le _ _
      _ ≤ rE / 2 + Mri * ‖w‖ := add_le_add hzu' (B.le_of_opNorm_le hB w)
      _ ≤ rE / 2 + Mri * (2 * ε) := by gcongr
      _ ≤ rE / 2 + rE / 2 := by linarith
      _ = rE := by ring
  have hlinG : ∀ u ∈ closedBall (0 : W) (2 * ε), ∀ v ∈ closedBall (0 : W) (2 * ε),
      ‖(ContinuousLinearMap.id ℝ W) (G u - G v) - (u - v)‖ ≤ (1 / 2) * ‖u - v‖ := by
    intro u hu v hv
    rw [ContinuousLinearMap.id_apply]
    have h := hlin _ (hball u hu) _ (hball v hv)
    have e1 : zu + B u - (zu + B v) = B (u - v) := by rw [map_sub]; abel
    rw [e1, hright] at h
    have hBuv : ‖B (u - v)‖ ≤ Mri * ‖u - v‖ := B.le_of_opNorm_le hB _
    have : Mri * ‖G u - G v - (u - v)‖ ≤ Mri * ((1 / 2) * ‖u - v‖) := by
      calc Mri * ‖G u - G v - (u - v)‖ ≤ (1 / 2) * ‖B (u - v)‖ := h
        _ ≤ (1 / 2) * (Mri * ‖u - v‖) := by gcongr
        _ = Mri * ((1 / 2) * ‖u - v‖) := by ring
    exact le_of_mul_le_mul_left this hMri
  have hG0 : G 0 = Ecl zu := by simp [hG]
  have hρ : 2 * 1 * ‖G 0‖ ≤ 2 * ε := by rw [hG0]; linarith
  obtain ⟨w, hw, hGw⟩ := exists_root_of_linearization G (ContinuousLinearMap.id ℝ W) 0
    zero_le_one ContinuousLinearMap.norm_id_le (fun a b hab => by simpa using hab) hρ hlinG
  refine ⟨w, hGw, ?_⟩
  rw [mem_closedBall, dist_zero_right, hG0] at hw
  linarith

end IntegratorOrderProof
