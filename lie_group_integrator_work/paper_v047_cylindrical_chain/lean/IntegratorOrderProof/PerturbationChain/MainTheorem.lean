import IntegratorOrderProof.PerturbationChain.Contraction
import IntegratorOrderProof.PerturbationChain.EndpointClosure
import IntegratorOrderProof.PerturbationChain.LocalToGlobal

/-!
# Conditional sixth-order theorem for the accepted `Gauss6/FullVA` map (abstract chain)

This file assembles `thm:g6fullva-order` from the four perturbation lemmas, keeping every
constant explicit.  It is a formalization of the **conditional** theorem: the P1/P2/P6
hypotheses (smooth chart, uniform stage inverse, endpoint right inverse, stability scale,
solver envelope `η_h ≤ c_η h⁷`) and the two named classical inputs (Gauss collocation order,
Lie-group chart transfer) enter as hypotheses; the P4/P5 residual certificate enters as the
single hypothesis `‖F_{A,h}(Z_G)‖ ≤ C_R h⁷`.  Nothing here discharges those hypotheses for
the concrete cylindrical-chain mechanism.

Per transition (`local_defect_bound`), with the four-map chain
`Ψ_h^G = 𝓔(Z_G)`, `Ψ_h^A = 𝓔(Z_A)`, `Ψ_h^E = 𝓒(𝓔(Z_A))`, `Ψ_h^{G6FVA} = 𝓒(𝓔(Z̃_A))`:

`‖Ψ_h^{G6FVA}(y) - φ_h(y)‖ ≤ (C_G + C_A + C_E + C_N c_η) h⁷ = C_loc h⁷`

where `C_A = M_E · 2 M C_R`, `C_E = 2 M_ri C_raw` (≤ the manuscript's `4 M_ri C_raw`),
`C_N = 2 M_A M_N`.  Globally (`conditional_sixth_order_grid_bound`), the discrete Gronwall
lemma with `p = 6` gives `C_red = C_loc Γ_s(T)` and `C_qv = C_𝓡 C_red`.
-/

open Metric Set

namespace IntegratorOrderProof

/-- Local defect constant `C_loc = C_G + C_A + C_E + C_N c_η`. -/
noncomputable def Cloc (CG M CR ME Mri Craw MA MN cη : ℝ) : ℝ :=
  CG + ME * (2 * M * CR) + 2 * Mri * Craw + (2 * MA * MN) * cη

/-- The manuscript's (weaker) constant with `C_E = 4 M_ri C_raw`. -/
noncomputable def ClocPaper (CG M CR ME Mri Craw MA MN cη : ℝ) : ℝ :=
  CG + ME * (2 * M * CR) + 4 * Mri * Craw + (2 * MA * MN) * cη

theorem Cloc_le_ClocPaper {CG M CR ME Mri Craw MA MN cη : ℝ} (hMri : 0 ≤ Mri) (hCraw : 0 ≤ Craw) :
    Cloc CG M CR ME Mri Craw MA MN cη ≤ ClocPaper CG M CR ME Mri Craw MA MN cη := by
  unfold Cloc ClocPaper
  nlinarith [mul_nonneg hMri hCraw]

/-- **Per-transition local defect of the accepted branch-selected map**
(Eq. `g6fva-local-defect-theorem`).

Spaces: `E` stage vectors, `F` residual rows, `X` endpoint/reduced-chart states,
`W` endpoint-closure rows.  Points: `ZG` lifted Gauss stage, `ZA` accepted root, `Zt` computed
Newton iterate, `zE = 𝓒(𝓔 ZA)`, `zEt = 𝓒(𝓔 Zt)`, `φ = φ_h(y)` exact flow. -/
theorem local_defect_bound
    {E F X W : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
    [NormedAddCommGroup F] [NormedSpace ℝ F]
    [NormedAddCommGroup X] [NormedSpace ℝ X]
    [NormedAddCommGroup W] [NormedSpace ℝ W]
    (Φ : E → F) (ZG ZA Zt : E) (AG AA : F →L[ℝ] E)
    (Erec : E → X) (Ecl : X → W) (D : X →L[ℝ] W) (B : W →L[ℝ] X) (zs zE zEt φ : X)
    {h CG M CR ME Mri Craw MA MN cη ρ rA rE η : ℝ}
    (hM : 0 ≤ M) (hME : 0 ≤ ME) (hMri : 0 < Mri) (hMA : 0 ≤ MA) (hMN : 0 ≤ MN)
    -- Gauss truncation on the smooth reduced chart (Lemmas A/B of the ledger; named hypothesis)
    (hG : ‖Erec ZG - φ‖ ≤ CG * h ^ 7)
    -- residual certificate: 96 non-dynamic rows + 36 Newton–Euler rows via the 132-row bridge
    (hR : ‖Φ ZG‖ ≤ CR * h ^ 7)
    -- P2 (stage): inverse bound and linearization at `Z_G`; accepted root in the ball
    (hAG : ‖AG‖ ≤ M)
    (hlinG : ∀ u ∈ closedBall ZG ρ, ∀ v ∈ closedBall ZG ρ,
      ‖AG (Φ u - Φ v) - (u - v)‖ ≤ (1 / 2) * ‖u - v‖)
    (hZA : Φ ZA = 0) (hZAball : ZA ∈ closedBall ZG ρ)
    -- endpoint reconstruction derivative bound `‖D_Z 𝓔_h‖ ≤ M_E`
    (hErec : ‖Erec ZA - Erec ZG‖ ≤ ME * ‖ZA - ZG‖)
    -- P2 (endpoint): right inverse, linearization, raw defect; accepted closed endpoint
    (hB : ‖B‖ ≤ Mri) (hright : ∀ w, D (B w) = w)
    (hlinE : ∀ u ∈ closedBall zs rE, ∀ v ∈ closedBall zs rE,
      Mri * ‖Ecl u - Ecl v - D (u - v)‖ ≤ (1 / 2) * ‖u - v‖)
    (hzu : Erec ZA ∈ closedBall zs rE) (hzE : zE ∈ closedBall zs rE) (hzEroot : Ecl zE = 0)
    (hzErange : ∃ w, zE = Erec ZA + B w)
    (hraw : ‖Ecl (Erec ZA)‖ ≤ Craw * h ^ 7)
    -- P6: inexact Newton on the branch ball, solver envelope `η ≤ c_η h⁷`
    (hAA : ‖AA‖ ≤ MA)
    (hlinA : ∀ u ∈ closedBall ZA rA, ‖AA (Φ u - Φ ZA) - (u - ZA)‖ ≤ (1 / 2) * ‖u - ZA‖)
    (hZt : Zt ∈ closedBall ZA rA) (hη : ‖Φ Zt‖ ≤ η) (hηscale : η ≤ cη * h ^ 7)
    -- full endpoint-output map `𝓟_h = 𝓒_h ∘ 𝓔_h` with `‖D_Z 𝓟_h‖ ≤ M_N`
    (hP : ‖zEt - zE‖ ≤ MN * ‖Zt - ZA‖) :
    ‖zEt - φ‖ ≤ Cloc CG M CR ME Mri Craw MA MN cη * h ^ 7 := by
  have hρ : 0 ≤ ρ := dist_nonneg.trans (mem_closedBall.mp hZAball)
  -- (2) stage-root perturbation: `‖Z_A - Z_G‖ ≤ 2 M ‖Φ Z_G‖ ≤ C_Z h⁷`
  have h2 : ‖ZA - ZG‖ ≤ 2 * M * (CR * h ^ 7) := by
    have hb := norm_sub_le_of_linearization Φ AG ZA ZG hAG
      (hlinG ZA hZAball ZG (mem_closedBall_self hρ)) hZA
    calc ‖ZA - ZG‖ ≤ 2 * M * ‖Φ ZG‖ := hb
      _ ≤ 2 * M * (CR * h ^ 7) := by gcongr
  have h2' : ‖Erec ZA - Erec ZG‖ ≤ ME * (2 * M * (CR * h ^ 7)) :=
    hErec.trans (by gcongr)
  -- (3) endpoint closure: `‖Δz_E‖ ≤ 2 M_ri ‖E(z_u)‖ ≤ C_E h⁷`
  have h3 : ‖zE - Erec ZA‖ ≤ 2 * Mri * (Craw * h ^ 7) := by
    have hb := endpoint_correction_bound Ecl D B zs (Erec ZA) zE hMri hB hright hlinE
      hzu hzE hzEroot hzErange
    calc ‖zE - Erec ZA‖ ≤ 2 * Mri * ‖Ecl (Erec ZA)‖ := hb
      _ ≤ 2 * Mri * (Craw * h ^ 7) := by gcongr
  -- (4) inexact Newton: `‖𝓟(Z̃_A) - 𝓟(Z_A)‖ ≤ C_N η ≤ C_N c_η h⁷`
  have h4 : ‖zEt - zE‖ ≤ (2 * MA * MN) * (cη * h ^ 7) := by
    have hs := inexact_newton_stage_bound Φ AA ZA hAA hlinA hZA hZt hη
    calc ‖zEt - zE‖ ≤ MN * ‖Zt - ZA‖ := hP
      _ ≤ MN * (2 * MA * η) := by gcongr
      _ ≤ MN * (2 * MA * (cη * h ^ 7)) := by gcongr
      _ = (2 * MA * MN) * (cη * h ^ 7) := by ring
  -- assemble the four-term chain
  have e : zEt - φ = ((Erec ZG - φ) + (Erec ZA - Erec ZG)) + (zE - Erec ZA) + (zEt - zE) := by
    abel
  have t1 := norm_add_le (Erec ZG - φ) (Erec ZA - Erec ZG)
  have t2 := norm_add_le ((Erec ZG - φ) + (Erec ZA - Erec ZG)) (zE - Erec ZA)
  have t3 := norm_add_le (((Erec ZG - φ) + (Erec ZA - Erec ZG)) + (zE - Erec ZA)) (zEt - zE)
  calc ‖zEt - φ‖
      ≤ ‖Erec ZG - φ‖ + ‖Erec ZA - Erec ZG‖ + ‖zE - Erec ZA‖ + ‖zEt - zE‖ := by
        rw [e]; linarith
    _ ≤ CG * h ^ 7 + ME * (2 * M * (CR * h ^ 7)) + 2 * Mri * (Craw * h ^ 7)
          + (2 * MA * MN) * (cη * h ^ 7) :=
        add_le_add (add_le_add (add_le_add hG h2') h3) h4
    _ = Cloc CG M CR ME Mri Craw MA MN cη * h ^ 7 := by unfold Cloc; ring

/-- The same local defect with the manuscript's constant `C_E = 4 M_ri C_raw`. -/
theorem local_defect_bound_paper
    {E F X W : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
    [NormedAddCommGroup F] [NormedSpace ℝ F]
    [NormedAddCommGroup X] [NormedSpace ℝ X]
    [NormedAddCommGroup W] [NormedSpace ℝ W]
    (Φ : E → F) (ZG ZA Zt : E) (AG AA : F →L[ℝ] E)
    (Erec : E → X) (Ecl : X → W) (D : X →L[ℝ] W) (B : W →L[ℝ] X) (zs zE zEt φ : X)
    {h CG M CR ME Mri Craw MA MN cη ρ rA rE η : ℝ}
    (hh : 0 ≤ h)
    (hM : 0 ≤ M) (hME : 0 ≤ ME) (hMri : 0 < Mri)
    (hCraw : 0 ≤ Craw) (hMA : 0 ≤ MA) (hMN : 0 ≤ MN)
    (hG : ‖Erec ZG - φ‖ ≤ CG * h ^ 7)
    (hR : ‖Φ ZG‖ ≤ CR * h ^ 7)
    (hAG : ‖AG‖ ≤ M)
    (hlinG : ∀ u ∈ closedBall ZG ρ, ∀ v ∈ closedBall ZG ρ,
      ‖AG (Φ u - Φ v) - (u - v)‖ ≤ (1 / 2) * ‖u - v‖)
    (hZA : Φ ZA = 0) (hZAball : ZA ∈ closedBall ZG ρ)
    (hErec : ‖Erec ZA - Erec ZG‖ ≤ ME * ‖ZA - ZG‖)
    (hB : ‖B‖ ≤ Mri) (hright : ∀ w, D (B w) = w)
    (hlinE : ∀ u ∈ closedBall zs rE, ∀ v ∈ closedBall zs rE,
      Mri * ‖Ecl u - Ecl v - D (u - v)‖ ≤ (1 / 2) * ‖u - v‖)
    (hzu : Erec ZA ∈ closedBall zs rE) (hzE : zE ∈ closedBall zs rE) (hzEroot : Ecl zE = 0)
    (hzErange : ∃ w, zE = Erec ZA + B w)
    (hraw : ‖Ecl (Erec ZA)‖ ≤ Craw * h ^ 7)
    (hAA : ‖AA‖ ≤ MA)
    (hlinA : ∀ u ∈ closedBall ZA rA, ‖AA (Φ u - Φ ZA) - (u - ZA)‖ ≤ (1 / 2) * ‖u - ZA‖)
    (hZt : Zt ∈ closedBall ZA rA) (hη : ‖Φ Zt‖ ≤ η) (hηscale : η ≤ cη * h ^ 7)
    (hP : ‖zEt - zE‖ ≤ MN * ‖Zt - ZA‖) :
    ‖zEt - φ‖ ≤ ClocPaper CG M CR ME Mri Craw MA MN cη * h ^ 7 := by
  have hb := local_defect_bound Φ ZG ZA Zt AG AA Erec Ecl D B zs zE zEt φ hM hME hMri
    hMA hMN hG hR hAG hlinG hZA hZAball hErec hB hright hlinE hzu hzE hzEroot hzErange hraw hAA
    hlinA hZt hη hηscale hP
  have hpow : 0 ≤ h ^ 7 := by positivity
  calc ‖zEt - φ‖ ≤ Cloc CG M CR ME Mri Craw MA MN cη * h ^ 7 := hb
    _ ≤ ClocPaper CG M CR ME Mri Craw MA MN cη * h ^ 7 :=
        mul_le_mul_of_nonneg_right (Cloc_le_ClocPaper hMri.le hCraw) hpow

/-- **Conditional sixth-order reported-grid bounds** (Eqs. `g6fva-reduced-grid-bound`,
`g6fva-reported-grid-bound`).  Given the per-transition local defect `C_loc h⁷` from
`local_defect_bound` at each exact grid state, the stability scale `1 + C_s h` along the
trajectory, and the tube-retention bootstrap, the reduced-chart grid error is
`≤ C_red h⁶` with `C_red = C_loc Γ_s(T)`, and the reported `(q, v)` error is `≤ C_qv h⁶` with
`C_qv = C_𝓡 C_red`. -/
theorem conditional_sixth_order_grid_bound {Y Q : Type*} [NormedAddCommGroup Y] [NormedSpace ℝ Y]
    [NormedAddCommGroup Q]
    (K : Set Y) (Ψ : Y → Y) (x y : ℕ → Y) (N : ℕ) {Cloc Cs h d T : ℝ}
    (hh : 0 < h) (hCs : 0 ≤ Cs) (hCloc : 0 ≤ Cloc) (hd : 0 ≤ d) (hNT : (N : ℝ) * h ≤ T)
    (htube : ∀ n ≤ N, closedBall (x n) d ⊆ K)
    (hloc : ∀ n < N, ‖Ψ (x n) - x (n + 1)‖ ≤ Cloc * h ^ 7)
    (hstab : ∀ n < N, y n ∈ K → ‖Ψ (y n) - Ψ (x n)‖ ≤ (1 + Cs * h) * ‖y n - x n‖)
    (hboot : Cloc * gronwallFactor Cs T * h ^ 6 ≤ d)
    (hy0 : y 0 = x 0) (hy : ∀ n, y (n + 1) = Ψ (y n))
    (𝓡 : Y → Q) {C𝓡 : ℝ} (hC𝓡 : 0 ≤ C𝓡)
    (h𝓡 : ∀ u ∈ K, ∀ v ∈ K, ‖𝓡 u - 𝓡 v‖ ≤ C𝓡 * ‖u - v‖) :
    (∀ n ≤ N, y n ∈ K ∧ ‖y n - x n‖ ≤ (Cloc * gronwallFactor Cs T) * h ^ 6) ∧
    (∀ n ≤ N, ‖𝓡 (y n) - 𝓡 (x n)‖ ≤ (C𝓡 * (Cloc * gronwallFactor Cs T)) * h ^ 6) := by
  have hloc' : ∀ n < N, ‖Ψ (x n) - x (n + 1)‖ ≤ Cloc * h ^ (6 + 1) := hloc
  exact ⟨local_to_global K Ψ x y N 6 hh hCs hCloc hNT htube hloc' hstab hboot hy0 hy,
    reported_grid_bound K Ψ x y N 6 hh hCs hCloc hd hNT htube hloc' hstab hboot hy0 hy 𝓡 hC𝓡 h𝓡⟩

end IntegratorOrderProof
