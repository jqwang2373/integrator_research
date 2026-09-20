import IntegratorOrderProof.Basic

/-!
# Local-to-global transfer on the accepted tube (`lem:local-global-transfer`)

Discrete Gronwall ("Lady Windermere's fan") argument with the first-exit tube-retention
bootstrap, in the restricted-domain form actually consumed by the manuscript's theorem
(Eq. `local-global-restricted-domain`):

* `x n` is the exact comparison state `Y_n = φ_{t_n,0}(y_0)` on the reported grid `t_n = n h`;
* `y n` is the numerical trajectory `y_{n+1} = Ψ_h(y_n)`, `y_0 = x_0` (zero initial error);
* `K` is the compact proof tube, and `closedBall (x n) d ⊆ K` is the tube margin `d_K`;
* local defect `‖Ψ_h(Y_n) - Y_{n+1}‖ ≤ C_ℓ h^{p+1}` and stability
  `‖Ψ_h(y_n) - Ψ_h(Y_n)‖ ≤ (1 + C_s h) ‖y_n - Y_n‖` are required only along the trajectory and
  only while `y_n ∈ K`.

Conclusion: `y_n ∈ K` and `‖y_n - Y_n‖ ≤ C_ℓ Γ_s(T) h^p` for all `n ≤ N`, where
`Γ_s(T) = (e^{C_s T} - 1)/C_s` (`= T` at `C_s = 0`) is Eq. `local-global-lemma-gronwall-factor`.
The bootstrap hypothesis `C_ℓ Γ_s(T) h^p ≤ d` is the "`h` sufficiently small" clause.
-/

open Metric Finset

namespace IntegratorOrderProof

/-- The Gronwall factor `Γ_s(T)` of Eq. `local-global-lemma-gronwall-factor`. -/
noncomputable def gronwallFactor (C T : ℝ) : ℝ :=
  if C = 0 then T else (Real.exp (C * T) - 1) / C

@[simp] theorem gronwallFactor_zero (T : ℝ) : gronwallFactor 0 T = T := by
  simp [gronwallFactor]

theorem gronwallFactor_of_pos {C : ℝ} (hC : 0 < C) (T : ℝ) :
    gronwallFactor C T = (Real.exp (C * T) - 1) / C := by
  simp [gronwallFactor, hC.ne']

/-- `h ∑_{k<n} (1 + C h)^k ≤ Γ_C(T)` whenever `n h ≤ T`. -/
theorem geom_sum_le_gronwallFactor {C h T : ℝ} (hC : 0 ≤ C) (hh : 0 < h) (n : ℕ)
    (hn : (n : ℝ) * h ≤ T) :
    h * ∑ k ∈ range n, (1 + C * h) ^ k ≤ gronwallFactor C T := by
  rcases hC.eq_or_lt with hC0 | hCpos
  · subst hC0
    simp only [zero_mul, add_zero, one_pow, sum_const, card_range, nsmul_eq_mul, mul_one,
      gronwallFactor_zero]
    linarith [hn]
  · rw [gronwallFactor_of_pos hCpos]
    have hCh : 0 < C * h := mul_pos hCpos hh
    have hne : (1 + C * h) ≠ 1 := by intro hc; linarith
    rw [geom_sum_eq hne]
    have e : h * (((1 + C * h) ^ n - 1) / (1 + C * h - 1)) = ((1 + C * h) ^ n - 1) / C := by
      have : (1 + C * h - 1) = C * h := by ring
      rw [this]
      field_simp
    rw [e]
    apply div_le_div_of_nonneg_right _ hCpos.le
    have h1 : (1 + C * h) ^ n ≤ Real.exp (C * h * n) :=
      stability_factor_le_exp C h hCpos.le hh.le n
    have h2 : Real.exp (C * h * n) ≤ Real.exp (C * T) := by
      apply Real.exp_le_exp.mpr
      have : C * h * n = C * (n * h) := by ring
      rw [this]
      exact mul_le_mul_of_nonneg_left hn hCpos.le
    linarith

/-- **Local-to-global transfer with tube-retention bootstrap.** -/
theorem local_to_global {Y : Type*} [NormedAddCommGroup Y]
    (K : Set Y) (Ψ : Y → Y) (x y : ℕ → Y) (N p : ℕ) {Cℓ Cs h d T : ℝ}
    (hh : 0 < h) (hCs : 0 ≤ Cs) (hCℓ : 0 ≤ Cℓ) (hNT : (N : ℝ) * h ≤ T)
    (htube : ∀ n ≤ N, closedBall (x n) d ⊆ K)
    (hloc : ∀ n < N, ‖Ψ (x n) - x (n + 1)‖ ≤ Cℓ * h ^ (p + 1))
    (hstab : ∀ n < N, y n ∈ K → ‖Ψ (y n) - Ψ (x n)‖ ≤ (1 + Cs * h) * ‖y n - x n‖)
    (hboot : Cℓ * gronwallFactor Cs T * h ^ p ≤ d)
    (hy0 : y 0 = x 0) (hy : ∀ n, y (n + 1) = Ψ (y n)) :
    ∀ n ≤ N, y n ∈ K ∧ ‖y n - x n‖ ≤ Cℓ * gronwallFactor Cs T * h ^ p := by
  set q : ℝ := 1 + Cs * h with hq
  have hq0 : 0 ≤ q := by positivity
  -- the geometric-sum bound, valid for every `n ≤ N`
  have hgeom : ∀ n ≤ N, Cℓ * h ^ (p + 1) * ∑ k ∈ range n, q ^ k
      ≤ Cℓ * gronwallFactor Cs T * h ^ p := by
    intro n hn
    have hnh : (n : ℝ) * h ≤ T := by
      have : (n : ℝ) ≤ N := by exact_mod_cast hn
      calc (n : ℝ) * h ≤ N * h := by gcongr
        _ ≤ T := hNT
    have hg := geom_sum_le_gronwallFactor hCs hh n hnh
    calc Cℓ * h ^ (p + 1) * ∑ k ∈ range n, q ^ k
        = Cℓ * h ^ p * (h * ∑ k ∈ range n, q ^ k) := by ring
      _ ≤ Cℓ * h ^ p * gronwallFactor Cs T := by gcongr
      _ = Cℓ * gronwallFactor Cs T * h ^ p := by ring
  -- sharper invariant `e_n ≤ C_ℓ h^{p+1} ∑_{k<n} q^k`, proved together with tube retention
  have key : ∀ n ≤ N, ‖y n - x n‖ ≤ Cℓ * h ^ (p + 1) * ∑ k ∈ range n, q ^ k := by
    intro n
    induction n with
    | zero => intro _; simp [hy0]
    | succ n ih =>
      intro hn
      have hnN : n < N := Nat.lt_of_succ_le hn
      have ih' := ih hnN.le
      have hyK : y n ∈ K := by
        apply htube n hnN.le
        rw [mem_closedBall, dist_eq_norm]
        exact ih'.trans ((hgeom n hnN.le).trans hboot)
      have hsum : ∑ k ∈ range (n + 1), q ^ k = q * ∑ k ∈ range n, q ^ k + 1 := by
        rw [sum_range_succ', mul_sum, pow_zero]
        congr 1
        exact sum_congr rfl fun k _ => by ring
      rw [hy n, hsum]
      calc ‖Ψ (y n) - x (n + 1)‖
          = ‖(Ψ (y n) - Ψ (x n)) + (Ψ (x n) - x (n + 1))‖ := by congr 1; abel
        _ ≤ ‖Ψ (y n) - Ψ (x n)‖ + ‖Ψ (x n) - x (n + 1)‖ := norm_add_le _ _
        _ ≤ q * ‖y n - x n‖ + Cℓ * h ^ (p + 1) := add_le_add (hstab n hnN hyK) (hloc n hnN)
        _ ≤ q * (Cℓ * h ^ (p + 1) * ∑ k ∈ range n, q ^ k) + Cℓ * h ^ (p + 1) := by gcongr
        _ = Cℓ * h ^ (p + 1) * (q * ∑ k ∈ range n, q ^ k + 1) := by ring
  intro n hn
  have hb := (key n hn).trans (hgeom n hn)
  refine ⟨?_, hb⟩
  apply htube n hn
  rw [mem_closedBall, dist_eq_norm]
  exact hb.trans hboot

/-- Reported-grid bound through a Lipschitz reporting map `𝓡` (chart → position/velocity):
`max_n ‖𝓡(y_n) - 𝓡(Y_n)‖ ≤ C_𝓡 C_ℓ Γ_s(T) h^p` (Eq. `g6fva-reported-grid-bound` shape). -/
theorem reported_grid_bound {Y Q : Type*} [NormedAddCommGroup Y]
    [NormedAddCommGroup Q]
    (K : Set Y) (Ψ : Y → Y) (x y : ℕ → Y) (N p : ℕ) {Cℓ Cs h d T : ℝ}
    (hh : 0 < h) (hCs : 0 ≤ Cs) (hCℓ : 0 ≤ Cℓ) (hd : 0 ≤ d) (hNT : (N : ℝ) * h ≤ T)
    (htube : ∀ n ≤ N, closedBall (x n) d ⊆ K)
    (hloc : ∀ n < N, ‖Ψ (x n) - x (n + 1)‖ ≤ Cℓ * h ^ (p + 1))
    (hstab : ∀ n < N, y n ∈ K → ‖Ψ (y n) - Ψ (x n)‖ ≤ (1 + Cs * h) * ‖y n - x n‖)
    (hboot : Cℓ * gronwallFactor Cs T * h ^ p ≤ d)
    (hy0 : y 0 = x 0) (hy : ∀ n, y (n + 1) = Ψ (y n))
    (𝓡 : Y → Q) {C𝓡 : ℝ} (hC𝓡 : 0 ≤ C𝓡)
    (h𝓡 : ∀ u ∈ K, ∀ v ∈ K, ‖𝓡 u - 𝓡 v‖ ≤ C𝓡 * ‖u - v‖) :
    ∀ n ≤ N, ‖𝓡 (y n) - 𝓡 (x n)‖ ≤ C𝓡 * (Cℓ * gronwallFactor Cs T) * h ^ p := by
  intro n hn
  obtain ⟨hyK, hb⟩ := local_to_global K Ψ x y N p hh hCs hCℓ hNT htube hloc hstab hboot hy0 hy n hn
  have hxK : x n ∈ K := htube n hn (mem_closedBall_self hd)
  calc ‖𝓡 (y n) - 𝓡 (x n)‖ ≤ C𝓡 * ‖y n - x n‖ := h𝓡 _ hyK _ hxK
    _ ≤ C𝓡 * (Cℓ * gronwallFactor Cs T * h ^ p) := by gcongr
    _ = C𝓡 * (Cℓ * gronwallFactor Cs T) * h ^ p := by ring

end IntegratorOrderProof
