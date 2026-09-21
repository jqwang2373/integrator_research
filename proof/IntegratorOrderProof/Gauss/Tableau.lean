import Mathlib

/-!
# The three-stage Gauss–Legendre (`Gauss6`) Butcher tableau and its simplifying assumptions

The accepted method uses three-stage Gauss–Legendre collocation.  Its exact tableau is

```
c = (1/2 - √15/10,  1/2,  1/2 + √15/10)
b = (5/18, 8/18, 5/18)
A = ⎡ 5/36            2/9 - √15/15   5/36 - √15/30 ⎤
    ⎢ 5/36 + √15/24   2/9            5/36 - √15/24 ⎥
    ⎣ 5/36 + √15/30   2/9 + √15/15   5/36          ⎦
```

We prove Butcher's simplifying assumptions `B(6)`, `C(3)`, `D(3)` for this tableau.  By
Butcher's theorem (Hairer–Nørsett–Wanner I, Thm. II.7.4: `B(p)`, `C(η)`, `D(ζ)` with
`p ≤ 2η + 2` and `p ≤ η + ζ + 1` imply order `p`), these give order `6`; Butcher's theorem
itself is *not* formalized here and remains the named classical input behind the `C_G h⁷`
hypothesis of the perturbation chain.  `C(3)` is also exactly the statement that `A` is the
collocation matrix `A_ij = ∫_0^{c_i} ℓ_j(τ) dτ` for the nodes `c`.

These are exactly the literals hard-coded in `gauss_legendre_coefficients(3)` /
`_gauss_legendre_coefficients_jax(3, dtype)` of
`v013_gauss6_quaternion_endpoint_dae/quaternion_pendulum.py`, which `run_v047.py` imports as
`qp`; so the tableau checked here is the one the pipeline differentiates and solves.

Everything is a polynomial identity in `r = √15/10` modulo `r² = 3/20`.
-/

open Finset

namespace IntegratorOrderProof.Gauss6

/-- `r = √15 / 10`; the nodes are `1/2 - r, 1/2, 1/2 + r`. -/
noncomputable def r : ℝ := Real.sqrt 15 / 10

theorem r_sq : r ^ 2 = 3 / 20 := by
  unfold r
  rw [div_pow, Real.sq_sqrt (by norm_num : (0 : ℝ) ≤ 15)]
  norm_num

theorem r_pow_four : r ^ 4 = 9 / 400 := by
  rw [show r ^ 4 = (r ^ 2) ^ 2 by ring, r_sq]; norm_num

theorem r_pos : 0 < r := by
  unfold r; positivity

theorem r_lt_half : r < 1 / 2 := by
  unfold r
  have h : Real.sqrt 15 < 5 := (Real.sqrt_lt' (by norm_num : (0 : ℝ) < 5)).mpr (by norm_num)
  linarith

/-- Gauss–Legendre nodes on `[0, 1]`. -/
noncomputable def c : Fin 3 → ℝ := ![1 / 2 - r, 1 / 2, 1 / 2 + r]

/-- Gauss–Legendre weights. -/
noncomputable def b : Fin 3 → ℝ := ![5 / 18, 8 / 18, 5 / 18]

/-- Collocation matrix. -/
noncomputable def A : Fin 3 → Fin 3 → ℝ :=
  ![![5 / 36, 2 / 9 - 2 * r / 3, 5 / 36 - r / 3],
    ![5 / 36 + 5 * r / 12, 2 / 9, 5 / 36 - 5 * r / 12],
    ![5 / 36 + r / 3, 2 / 9 + 2 * r / 3, 5 / 36]]

theorem c_mem_Icc (i : Fin 3) : c i ∈ Set.Icc (0 : ℝ) 1 := by
  have h1 := r_pos; have h2 := r_lt_half
  fin_cases i
  · show (1 / 2 - r) ∈ Set.Icc (0 : ℝ) 1
    exact ⟨by linarith, by linarith⟩
  · show (1 / 2 : ℝ) ∈ Set.Icc (0 : ℝ) 1
    exact ⟨by norm_num, by norm_num⟩
  · show (1 / 2 + r) ∈ Set.Icc (0 : ℝ) 1
    exact ⟨by linarith, by linarith⟩

theorem b_pos (i : Fin 3) : 0 < b i := by
  fin_cases i <;> simp [b]

theorem sum_b : ∑ i, b i = 1 := by
  simp [b, Fin.sum_univ_three]; norm_num

theorem sum_abs_b : ∑ i, |b i| = 1 := by
  rw [← sum_b]
  exact sum_congr rfl fun i _ => abs_of_pos (b_pos i)

/-- Butcher's `B(p)`: `∑ᵢ bᵢ cᵢ^(k-1) = 1/k` for `1 ≤ k ≤ p`. -/
def B (p : ℕ) : Prop := ∀ k : ℕ, 1 ≤ k → k ≤ p → ∑ i, b i * c i ^ (k - 1) = 1 / (k : ℝ)

/-- Butcher's `C(η)`: `∑ⱼ aᵢⱼ cⱼ^(k-1) = cᵢ^k / k` for `1 ≤ k ≤ η` (collocation condition). -/
def C (η : ℕ) : Prop :=
  ∀ k : ℕ, 1 ≤ k → k ≤ η → ∀ i, ∑ j, A i j * c j ^ (k - 1) = c i ^ k / (k : ℝ)

/-- Butcher's `D(ζ)`: `∑ᵢ bᵢ cᵢ^(k-1) aᵢⱼ = bⱼ (1 - cⱼ^k) / k` for `1 ≤ k ≤ ζ`. -/
def D (ζ : ℕ) : Prop :=
  ∀ k : ℕ, 1 ≤ k → k ≤ ζ → ∀ j, ∑ i, b i * c i ^ (k - 1) * A i j = b j * (1 - c j ^ k) / (k : ℝ)

/-- Monomial exactness of the Gauss weights: `∑ᵢ bᵢ cᵢ^k = ∫₀¹ x^k dx` for `k ≤ 5`. -/
theorem monomial_exact : ∀ k : ℕ, k < 6 → ∑ i, b i * c i ^ k = 1 / ((k : ℝ) + 1) := by
  intro k hk
  have h2 := r_sq; have h4 := r_pow_four
  interval_cases k <;> simp [b, c, Fin.sum_univ_three] <;> ring_nf <;> linarith

/-- `B(6)` holds: the quadrature rule has order 6. -/
theorem B_six : B 6 := by
  intro k hk1 hk6
  have h2 := r_sq; have h4 := r_pow_four
  interval_cases k <;> simp [b, c, Fin.sum_univ_three] <;> ring_nf <;> linarith

/-- `B(7)` fails: the rule is not exact on `x^6` (order is exactly 6). -/
theorem not_B_seven : ¬ B 7 := by
  intro hB
  have h := hB 7 (by norm_num) le_rfl
  have h2 := r_sq; have h4 := r_pow_four
  have h6 : r ^ 6 = 27 / 8000 := by
    rw [show r ^ 6 = (r ^ 2) ^ 3 by ring, r_sq]; norm_num
  simp [b, c, Fin.sum_univ_three] at h
  ring_nf at h
  linarith

/-- `C(3)` holds: `A` is the collocation matrix for the nodes `c`. -/
theorem C_three : C 3 := by
  intro k hk1 hk3 i
  have h2 := r_sq; have h4 := r_pow_four
  interval_cases k <;> fin_cases i <;> simp [A, c, Fin.sum_univ_three] <;> ring_nf <;> linarith

/-- `D(3)` holds. -/
theorem D_three : D 3 := by
  intro k hk1 hk3 j
  have h2 := r_sq; have h4 := r_pow_four
  interval_cases k <;> fin_cases j <;> simp [A, b, c, Fin.sum_univ_three] <;> ring_nf <;> linarith

/-- Butcher's order-6 hypotheses for the Gauss6 tableau, bundled:
`B(6) ∧ C(3) ∧ D(3)` with `6 ≤ 2·3 + 2` and `6 ≤ 3 + 3 + 1`. -/
theorem butcher_order_six_hypotheses :
    B 6 ∧ C 3 ∧ D 3 ∧ (6 ≤ 2 * 3 + 2) ∧ (6 ≤ 3 + 3 + 1) :=
  ⟨B_six, C_three, D_three, by norm_num, by norm_num⟩

end IntegratorOrderProof.Gauss6
