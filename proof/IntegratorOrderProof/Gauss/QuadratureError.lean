import IntegratorOrderProof.Gauss.Tableau

/-!
# Peano-type quadrature error bound and the Gauss6 `h⁷` local quadrature defect

If a quadrature rule `(b, c)` on `[0,1]` integrates all monomials `x^k`, `k ≤ n`, exactly,
then for `g ∈ C^{n+1}[0,1]` with `|g^{(n+1)}| ≤ K`

`|∫₀¹ g - ∑ᵢ bᵢ g(cᵢ)| ≤ (1 + ∑ᵢ |bᵢ|) · K / n!`.

The proof subtracts the degree-`n` Taylor polynomial `P` of `g` at `0` (on which the rule is
exact) and bounds the remainder `g - P` on `[0,1]` by Mathlib's `taylor_mean_remainder_bound`.

For the Gauss6 weights (`n = 5`, `∑|bᵢ| = 1`) this gives `|∫₀¹ g - ∑ bᵢ g(cᵢ)| ≤ K / 60`, and
after the affine change of variables `t = t₀ + h τ` the local quadrature defect on a step of
length `h` is `≤ h · K̃ / 60` with `K̃ = sup |d⁶/dτ⁶ g(t₀ + hτ)| = h⁶ sup |g^{(6)}|`, i.e. `O(h⁷)`.
This is the quadrature-error engine behind the classical "collocation order = quadrature order"
theorem (Hairer–Nørsett–Wanner I, Thm. II.7.9/7.10); the variation-of-constants transfer from
quadrature defect to the one-step error is not formalized here.
-/

open Set Finset intervalIntegral
open scoped Nat

namespace IntegratorOrderProof

/-- **Peano-type quadrature error bound on `[0, 1]`.** -/
theorem quadrature_error_bound {ι : Type*} [Fintype ι] (b c : ι → ℝ) (n : ℕ)
    (hexact : ∀ k : ℕ, k < n + 1 → ∑ i, b i * c i ^ k = 1 / ((k : ℝ) + 1))
    (hc : ∀ i, c i ∈ Icc (0 : ℝ) 1)
    (g : ℝ → ℝ) (hg : ContDiffOn ℝ (n + 1) g (Icc 0 1))
    {K : ℝ} (hK : ∀ y ∈ Icc (0 : ℝ) 1, |iteratedDerivWithin (n + 1) g (Icc 0 1) y| ≤ K) :
    |(∫ x in (0 : ℝ)..1, g x) - ∑ i, b i * g (c i)| ≤ (1 + ∑ i, |b i|) * (K / n !) := by
  -- Taylor coefficients at `0` and the Taylor polynomial `P`
  set a : ℕ → ℝ := fun k => (k ! : ℝ)⁻¹ * iteratedDerivWithin k g (Icc 0 1) 0 with ha
  set P : ℝ → ℝ := fun x => ∑ k ∈ range (n + 1), a k * x ^ k with hP
  have hPtaylor : ∀ x, taylorWithinEval g n (Icc 0 1) 0 x = P x := by
    intro x
    simp only [hP, ha, taylor_within_apply, sub_zero, smul_eq_mul]
    exact sum_congr rfl fun k _ => by ring
  have hK0 : 0 ≤ K := (abs_nonneg _).trans (hK 0 (left_mem_Icc.mpr zero_le_one))
  -- remainder bound on `[0, 1]`
  have hrem : ∀ x ∈ Icc (0 : ℝ) 1, |g x - P x| ≤ K / n ! := by
    intro x hx
    have h := taylor_mean_remainder_bound zero_le_one hg hx
      (fun y hy => by rw [Real.norm_eq_abs]; exact hK y hy)
    rw [Real.norm_eq_abs, hPtaylor] at h
    refine h.trans ?_
    have hx' : (x - 0) ^ (n + 1) ≤ 1 := by
      rw [sub_zero]; exact pow_le_one₀ hx.1 hx.2
    calc K * (x - 0) ^ (n + 1) / n ! ≤ K * 1 / n ! := by gcongr
      _ = K / n ! := by ring
  -- the rule is exact on `P`
  have hPexact : (∫ x in (0 : ℝ)..1, P x) = ∑ i, b i * P (c i) := by
    simp only [hP]
    rw [integral_finsetSum (fun k _ =>
      (by fun_prop : Continuous fun x : ℝ => a k * x ^ k).intervalIntegrable _ _)]
    simp_rw [integral_const_mul, integral_pow, mul_sum]
    rw [sum_comm]
    refine sum_congr rfl fun k hk => ?_
    have he := hexact k (mem_range.mp hk)
    calc a k * ((1 ^ (k + 1) - 0 ^ (k + 1)) / ((k : ℝ) + 1))
        = a k * (1 / ((k : ℝ) + 1)) := by
          rw [one_pow, zero_pow (Nat.succ_ne_zero k), sub_zero, one_div]
      _ = a k * ∑ i, b i * c i ^ k := by rw [he]
      _ = ∑ i, b i * (a k * c i ^ k) := by rw [mul_sum]; exact sum_congr rfl fun i _ => by ring
  -- integrability
  have hgint : IntervalIntegrable g MeasureTheory.volume 0 1 := by
    have : ContinuousOn g (uIcc 0 1) := by rw [Set.uIcc_of_le zero_le_one]; exact hg.continuousOn
    exact this.intervalIntegrable
  have hPint : IntervalIntegrable P MeasureTheory.volume 0 1 :=
    (continuous_finsetSum _ fun k _ => (by fun_prop : Continuous fun x : ℝ => a k * x ^ k)
      ).intervalIntegrable _ _
  -- split off the polynomial part
  have hsplit : (∫ x in (0 : ℝ)..1, g x) - ∑ i, b i * g (c i)
      = (∫ x in (0 : ℝ)..1, (g x - P x)) - ∑ i, b i * (g (c i) - P (c i)) := by
    rw [integral_sub hgint hPint, hPexact]
    simp only [mul_sub, sum_sub_distrib]; ring
  rw [hsplit]
  have hI : |∫ x in (0 : ℝ)..1, (g x - P x)| ≤ K / n ! := by
    have h := norm_integral_le_of_norm_le_const (a := (0 : ℝ)) (b := 1) (C := K / n !)
      (f := fun x => g x - P x) (fun x hx => by
        rw [Real.norm_eq_abs]
        rw [Set.uIoc_of_le zero_le_one] at hx
        exact hrem x (Ioc_subset_Icc_self hx))
    simpa [Real.norm_eq_abs] using h
  have hS : |∑ i, b i * (g (c i) - P (c i))| ≤ (∑ i, |b i|) * (K / n !) := by
    calc |∑ i, b i * (g (c i) - P (c i))| ≤ ∑ i, |b i * (g (c i) - P (c i))| :=
          abs_sum_le_sum_abs _ _
      _ = ∑ i, |b i| * |g (c i) - P (c i)| := by simp_rw [abs_mul]
      _ ≤ ∑ i, |b i| * (K / n !) :=
          sum_le_sum fun i _ => mul_le_mul_of_nonneg_left (hrem _ (hc i)) (abs_nonneg _)
      _ = (∑ i, |b i|) * (K / n !) := by rw [sum_mul]
  calc |(∫ x in (0 : ℝ)..1, (g x - P x)) - ∑ i, b i * (g (c i) - P (c i))|
      ≤ |∫ x in (0 : ℝ)..1, (g x - P x)| + |∑ i, b i * (g (c i) - P (c i))| := abs_sub _ _
    _ ≤ K / n ! + (∑ i, |b i|) * (K / n !) := add_le_add hI hS
    _ = (1 + ∑ i, |b i|) * (K / n !) := by ring

/-- **Gauss6 quadrature error on `[0,1]`**: for `g ∈ C⁶[0,1]` with `|g⁽⁶⁾| ≤ K`,
`|∫₀¹ g - ∑ᵢ bᵢ g(cᵢ)| ≤ K / 60`. -/
theorem gauss6_quadrature_error (g : ℝ → ℝ) (hg : ContDiffOn ℝ 6 g (Icc 0 1)) {K : ℝ}
    (hK : ∀ y ∈ Icc (0 : ℝ) 1, |iteratedDerivWithin 6 g (Icc 0 1) y| ≤ K) :
    |(∫ x in (0 : ℝ)..1, g x) - ∑ i, Gauss6.b i * g (Gauss6.c i)| ≤ K / 60 := by
  have h := quadrature_error_bound Gauss6.b Gauss6.c 5 Gauss6.monomial_exact Gauss6.c_mem_Icc g
    hg hK
  have h5 : ((5 ! : ℕ) : ℝ) = 120 := by norm_num [Nat.factorial]
  rw [Gauss6.sum_abs_b, h5] at h
  calc _ ≤ (1 + 1) * (K / 120) := h
    _ = K / 60 := by ring

/-- Affine change of variables for the step `[t₀, t₀ + h]`:
`∫_{t₀}^{t₀+h} g = h ∫₀¹ g(t₀ + h τ) dτ`. -/
theorem integral_step_eq (g : ℝ → ℝ) (t₀ h : ℝ) (hh : h ≠ 0) :
    ∫ t in t₀..t₀ + h, g t = h * ∫ τ in (0 : ℝ)..1, g (t₀ + h * τ) := by
  have e : (fun τ : ℝ => g (t₀ + h * τ)) = fun τ => g (h * τ + t₀) := by
    funext τ; rw [add_comm]
  rw [e, integral_comp_mul_add (f := g) hh t₀, smul_eq_mul, mul_zero, zero_add, mul_one,
    add_comm h t₀, ← mul_assoc, mul_inv_cancel₀ hh, one_mul]

/-- **Gauss6 local quadrature defect on a step of length `h`.**  With `G(τ) = g(t₀ + h τ)`
(`G ∈ C⁶[0,1]`, `|G⁽⁶⁾| ≤ K̃`, where `K̃ = h⁶ sup|g⁽⁶⁾|` by the chain rule):
`|∫_{t₀}^{t₀+h} g - h ∑ᵢ bᵢ g(t₀ + cᵢ h)| ≤ h · K̃ / 60`. -/
theorem gauss6_step_defect (g : ℝ → ℝ) (t₀ h : ℝ) (hh : 0 < h)
    (hG : ContDiffOn ℝ 6 (fun τ => g (t₀ + h * τ)) (Icc 0 1)) {K : ℝ}
    (hK : ∀ y ∈ Icc (0 : ℝ) 1,
      |iteratedDerivWithin 6 (fun τ => g (t₀ + h * τ)) (Icc 0 1) y| ≤ K) :
    |(∫ t in t₀..t₀ + h, g t) - h * ∑ i, Gauss6.b i * g (t₀ + h * Gauss6.c i)| ≤ h * (K / 60) := by
  rw [integral_step_eq g t₀ h hh.ne', ← mul_sub, abs_mul, abs_of_pos hh]
  exact mul_le_mul_of_nonneg_left (gauss6_quadrature_error _ hG hK) hh.le

end IntegratorOrderProof
