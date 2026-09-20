import Mathlib

/-!
# The 36 Newton–Euler dynamic rows of the `Gauss6/FullVA` cylindrical-chain residual

This file is the Lean counterpart of `D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE` and of the
`D1/D2` template identities in `NEWTON_EULER_BALANCE_IDENTITY_AUDIT` (previously checked by
`sympy.simplify(runtime_expr - target_expr) == 0` on scalar sign templates).

The implemented rows are transcribed from the `dyn` block of
`v047_cylindrical_chain_pipeline/run_v047.py` (`residual_cylindrical_chain`), with the runtime
sign conventions kept verbatim:

* `trans = m a - m g - f_ext - force`, `force = joint_force[0] - joint_force[1]` for body 0 and
  `joint_force[1]` for body 1;
* `rot = J α + ω × (J ω) - prox_torque - distal_torque - axis_torque + dist_axis_torque - τ_ext`.

The two theorems `transRow_eq` / `rotRow_eq` are the D1/D2 identities: each implemented row is
literally the defect of the mathematical Newton (resp. Euler) balance.  The theorem
`dynamic_rows_vanish` is the dynamic half of the exact stage identity (formerly the "P5
direct-substitution" interface of the manuscript): if the lifted Gauss stage
satisfies the pointwise balance (which is what the smooth FullVA lift `𝓛(y,t) = (q,v,a,λ)`
supplies, `lem:fullva-stage-lift`), then all `3 × 2 × 2 × 3 = 36` implemented dynamic rows are
exactly `0`, hence trivially `O(h⁷)`.

What is **not** proved here: that the lift satisfies the balance (that is the definition of
the lift), the 96 non-dynamic rows (see `FullVA/NonDynamicRows.lean`), and any statement about
the automatic-differentiation/row-scaling binding between transcription and source code.
-/

open Matrix

namespace IntegratorOrderProof.NewtonEuler

/-- Vectors in `ℝ³`, matching `jnp` arrays of shape `(3,)`. -/
abbrev V3 := Fin 3 → ℝ

/-- Data of one Gauss stage entering the Newton–Euler rows of the two-body cylindrical chain.
Bodies are `0, 1`; joint `0` is ground–body0, joint `1` is body0–body1.  Multipliers per joint
are `lam j = (λ₀, λ₁, η₀, η₁)`: two normal forces along the joint basis and two axis-alignment
torque multipliers (`st["lambda"][j, 0:2]` and `st["lambda"][j, 2:4]`). -/
structure StageData where
  /-- body masses `masses[body]` -/
  m : Fin 2 → ℝ
  /-- body inertia tensors `Js[body]` -/
  J : Fin 2 → Matrix (Fin 3) (Fin 3) ℝ
  /-- stage rotation matrices `R[body]` -/
  R : Fin 2 → Matrix (Fin 3) (Fin 3) ℝ
  /-- stage translational accelerations `st["a"][body]` -/
  a : Fin 2 → V3
  /-- stage angular accelerations `st["alpha"][body]` (body frame) -/
  α : Fin 2 → V3
  /-- stage angular velocities `st["w"][body]` (body frame) -/
  ω : Fin 2 → V3
  /-- gravity vector -/
  g : V3
  /-- external world-frame forces `external_forces_world[body]` -/
  fext : Fin 2 → V3
  /-- external body-frame torques `external_torques_body[body]` -/
  τext : Fin 2 → V3
  /-- stage multipliers `st["lambda"][joint, k]` -/
  lam : Fin 2 → Fin 4 → ℝ
  /-- joint basis vectors `joint_basis[joint, 0/1]` -/
  basis : Fin 2 → Fin 2 → V3
  /-- world-frame joint axis `kin["parent_axis"][joint]` (friction direction) -/
  parentAxis : Fin 2 → V3
  /-- Brown–McPhee friction scalar per joint -/
  fric : Fin 2 → ℝ
  /-- body-frame attachment point of the proximal joint (`s_prev[body]`) -/
  sPrev : Fin 2 → V3
  /-- body-frame attachment point of the distal joint (`s_next[body]`) -/
  sNext : Fin 2 → V3
  /-- body-frame axis of the proximal joint (`axis_prev[body]`) -/
  axisPrev : Fin 2 → V3
  /-- body-frame axis of the distal joint (`axis_next[body]`) -/
  axisNext : Fin 2 → V3

namespace StageData

variable (d : StageData)

/-- Constraint (normal) part of the joint force: `λ₀ b₀ + λ₁ b₁` (the `G_bᵀ λ` block). -/
def constraintForce (j : Fin 2) : V3 := d.lam j 0 • d.basis j 0 + d.lam j 1 • d.basis j 1

/-- Friction part of the joint force along the parent axis (`f_fric`). -/
def frictionForce (j : Fin 2) : V3 := d.fric j • d.parentAxis j

/-- `joint_force[j] = normal_force + friction * parent_axis`. -/
def jointForce (j : Fin 2) : V3 := d.constraintForce j + d.frictionForce j

/-- Runtime `force`: body 0 gets `joint_force[0] - joint_force[1]`, body 1 gets `joint_force[1]`. -/
def netForce : Fin 2 → V3 := ![d.jointForce 0 - d.jointForce 1, d.jointForce 1]

/-- `prox_torque = cross(s_prev[body], R[body].T @ joint_force[body])`. -/
def proxTorque (i : Fin 2) : V3 := d.sPrev i ⨯₃ ((d.R i)ᵀ *ᵥ d.jointForce i)

/-- `distal_torque`: body 0 gets `cross(s_next[0], R[0].T @ (-joint_force[1]))`, body 1 gets `0`. -/
def distalTorque : Fin 2 → V3 := ![d.sNext 0 ⨯₃ ((d.R 0)ᵀ *ᵥ (-(d.jointForce 1))), 0]

/-- `axis_torque = η₀ cross(axis_prev, Rᵀ b₀) + η₁ cross(axis_prev, Rᵀ b₁)`. -/
def axisTorque (i : Fin 2) : V3 :=
  d.lam i 2 • (d.axisPrev i ⨯₃ ((d.R i)ᵀ *ᵥ d.basis i 0)) +
  d.lam i 3 • (d.axisPrev i ⨯₃ ((d.R i)ᵀ *ᵥ d.basis i 1))

/-- `dist_axis_torque`: body 0 gets the distal-joint axis torque with `η_dist = λ[1, 2:4]`,
body 1 gets `0`. -/
def distAxisTorque : Fin 2 → V3 :=
  ![d.lam 1 2 • (d.axisNext 0 ⨯₃ ((d.R 0)ᵀ *ᵥ d.basis 1 0)) +
      d.lam 1 3 • (d.axisNext 0 ⨯₃ ((d.R 0)ᵀ *ᵥ d.basis 1 1)),
    0]

/-- Implemented translational row (`trans` in `run_v047.py`). -/
def transRow (i : Fin 2) : V3 := d.m i • d.a i - d.m i • d.g - d.fext i - d.netForce i

/-- Implemented rotational row (`rot` in `run_v047.py`). -/
def rotRow (i : Fin 2) : V3 :=
  d.J i *ᵥ d.α i + d.ω i ⨯₃ (d.J i *ᵥ d.ω i)
    - d.proxTorque i - d.distalTorque i - d.axisTorque i + d.distAxisTorque i - d.τext i

/-- Body-frame joint wrench torque of the mathematical Euler balance (the D2 target
`prox + distal + axis - dist_axis`, i.e. `H_bᵀ λ + τ_fric`). -/
def jointTorque (i : Fin 2) : V3 :=
  d.proxTorque i + d.distalTorque i + d.axisTorque i - d.distAxisTorque i

/-- Pointwise Newton balance at the stage: `m a = m g + f_ext + (G_bᵀ λ + f_fric)`. -/
def NewtonBalance (i : Fin 2) : Prop :=
  d.m i • d.a i = d.m i • d.g + d.fext i + d.netForce i

/-- Pointwise Euler balance at the stage: `J α + ω × J ω = τ_ext + (H_bᵀ λ + τ_fric)`. -/
def EulerBalance (i : Fin 2) : Prop :=
  d.J i *ᵥ d.α i + d.ω i ⨯₃ (d.J i *ᵥ d.ω i) = d.τext i + d.jointTorque i

/-- **D1**: the implemented translational row is the Newton-balance defect. -/
theorem transRow_eq (i : Fin 2) :
    d.transRow i = d.m i • d.a i - (d.m i • d.g + d.fext i + d.netForce i) := by
  simp only [transRow]; abel

/-- **D2**: the implemented rotational row is the Euler-balance defect. -/
theorem rotRow_eq (i : Fin 2) :
    d.rotRow i = (d.J i *ᵥ d.α i + d.ω i ⨯₃ (d.J i *ᵥ d.ω i)) - (d.τext i + d.jointTorque i) := by
  simp only [rotRow, jointTorque]; abel

theorem transRow_eq_zero_iff (i : Fin 2) : d.transRow i = 0 ↔ d.NewtonBalance i := by
  rw [transRow_eq, sub_eq_zero]; exact Iff.rfl

theorem rotRow_eq_zero_iff (i : Fin 2) : d.rotRow i = 0 ↔ d.EulerBalance i := by
  rw [rotRow_eq, sub_eq_zero]; exact Iff.rfl

/-- D3-style split of the runtime net force into multiplier and friction parts. -/
theorem netForce_zero :
    d.netForce 0 = (d.constraintForce 0 - d.constraintForce 1) +
      (d.frictionForce 0 - d.frictionForce 1) := by
  show d.jointForce 0 - d.jointForce 1 = _
  simp only [jointForce]; abel

theorem netForce_one : d.netForce 1 = d.constraintForce 1 + d.frictionForce 1 := rfl

end StageData

/-- One of the 36 dynamic rows: Gauss stage `s`, body `i`, block (`false` = translational,
`true` = rotational), component `c`. -/
def dynamicRow (Z : Fin 3 → StageData) (s : Fin 3) (i : Fin 2) (blk : Bool) (c : Fin 3) : ℝ :=
  if blk then (Z s).rotRow i c else (Z s).transRow i c

/-- There are exactly 36 dynamic rows. -/
theorem card_dynamic_rows : Fintype.card (Fin 3 × Fin 2 × Bool × Fin 3) = 36 := by
  simp

/-- **Dynamic rows of the exact stage identity.**  If the lifted Gauss stage satisfies the pointwise
Newton–Euler balance at every stage and body, then every one of the 36 implemented dynamic rows
evaluates to `0`. -/
theorem dynamic_rows_vanish (Z : Fin 3 → StageData)
    (hlift : ∀ s i, (Z s).NewtonBalance i ∧ (Z s).EulerBalance i) :
    ∀ s i blk c, dynamicRow Z s i blk c = 0 := by
  intro s i blk c
  cases blk
  · show (Z s).transRow i c = 0
    rw [((Z s).transRow_eq_zero_iff i).mpr (hlift s i).1]; rfl
  · show (Z s).rotRow i c = 0
    rw [((Z s).rotRow_eq_zero_iff i).mpr (hlift s i).2]; rfl

/-- The zero rows are in particular bounded by `C h⁷` for any `C ≥ 0`, which is the form
consumed by the 132-row bridge `lem:full-132-row-residual-bridge`. -/
theorem dynamic_rows_le_h7 (Z : Fin 3 → StageData)
    (hlift : ∀ s i, (Z s).NewtonBalance i ∧ (Z s).EulerBalance i)
    {C h : ℝ} (hC : 0 ≤ C) (hh : 0 ≤ h) :
    ∀ s i blk c, |dynamicRow Z s i blk c| ≤ C * h ^ 7 := by
  intro s i blk c
  rw [dynamic_rows_vanish Z hlift s i blk c, abs_zero]
  positivity

end IntegratorOrderProof.NewtonEuler
