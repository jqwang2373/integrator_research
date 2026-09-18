import Mathlib

/-!
# Smoke test for the Lean + Mathlib toolchain

Two tiny checks that exercise `norm_num`, `positivity`, `Real.exp`, and
`linarith` from Mathlib. The second is the shape of the one-step stability
factor `(1 + C_s h)^n ≤ exp(C_s h n)` used in local-to-global order transfer.
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
