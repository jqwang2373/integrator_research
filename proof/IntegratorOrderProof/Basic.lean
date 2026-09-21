import Mathlib

/-!
# One-step stability factor

`stability_factor_le_exp`: `(1 + C_s h)^n ≤ exp(C_s h n)` for `C_s, h ≥ 0`.  This is the
elementary growth bound behind the discrete Gronwall argument of
`PerturbationChain/LocalToGlobal.lean` (Eq. `local-global-lemma-gronwall-factor` of the
manuscript).
-/

example : (2 : ℝ) + 2 = 4 := by norm_num

theorem stability_factor_le_exp (C h : ℝ) (hC : 0 ≤ C) (hh : 0 ≤ h) (n : ℕ) :
    (1 + C * h) ^ n ≤ Real.exp (C * h * n) := by
  have h1 : 1 + C * h ≤ Real.exp (C * h) := by
    have := Real.add_one_le_exp (C * h)
    linarith
  calc (1 + C * h) ^ n ≤ (Real.exp (C * h)) ^ n :=
        pow_le_pow_left₀ (by positivity) h1 n
    _ = Real.exp (C * h * n) := by
        rw [← Real.exp_nat_mul]
        congr 1
        ring
