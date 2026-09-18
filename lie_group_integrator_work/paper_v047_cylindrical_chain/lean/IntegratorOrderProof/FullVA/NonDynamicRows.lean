import Mathlib

/-!
# The 96 non-dynamic rows of the implemented `Gauss6/FullVA` residual

Transcription of the non-dynamic blocks `pvel`, `u_block`, `pacc`, `w_block`, `constraints`
of `residual_cylindrical_chain` in `v047_cylindrical_chain_pipeline/run_v047.py`, together
with the joint kinematics `joint_kinematics_jax`.  Per Gauss stage and per joint the
implementation has 16 rows:

| block | rows | content in the code |
| --- | --- | --- |
| `constraints` | 4 | `basis ⬝ rel_point` (2), `axis_res` (2): position-level constraints |
| `pvel` | 3 | `rel_vel ⬝ basis` (2): velocity-level constraints; `r_coll_axis`: collocation of the sliding coordinate |
| `u_block` | 3 | `axis_rate` (2): velocity-level alignment constraints; `spin_coll_axis`: collocation of the twist angle |
| `pacc` | 3 | `rel_acc ⬝ basis` (2): acceleration-level constraints; `v_coll_axis`: collocation of the sliding rate |
| `w_block` | 3 | `axis_acc` (2): acceleration-level alignment constraints; `spin_acc_coll_axis`: collocation of the twist rate |

So the implemented residual carries **72 constraint rows and 24 joint-coordinate collocation
rows** (3 stages × 2 joints × (12 + 4)), not 72 body-level collocation rows and 24 lower-pair
rows as displayed in Eq. `g6fullva-expanded-stage` of the manuscript.

Main result (`nondynamic_rows_iff`): the 96 implemented non-dynamic rows vanish **iff** the
lower-pair constraints hold at position, velocity and acceleration level at every stage **and**
the four reduced joint coordinates `(s, θ, ṡ, θ̇)` per joint satisfy the three-stage Gauss
collocation equations.  In particular, at the lift of the reduced Gauss stage all 96 rows are
exactly `0` (the residual-value input `C_R h⁷` of the manuscript holds with `C_R = 0`), and the
implemented FullVA stage system is exactly Gauss collocation on the reduced joint-coordinate
ODE.

`arctan2` (used for the twist angle) is an opaque function parameter here: the row algebra
does not depend on its analytic properties.
-/

open Matrix Finset

namespace IntegratorOrderProof.FullVA

/-- Vectors in `ℝ³`. -/
abbrev V3 := Fin 3 → ℝ

/-- Fixed mechanism parameters (`params_arrays` in the code).  Joint `0` is ground–body0,
joint `1` is body0–body1.  `basis j m` is the fixed world basis `joint_basis[j, m]`. -/
structure JointParams where
  sPrev : Fin 2 → V3
  sNext : Fin 2 → V3
  axisPrev : Fin 2 → V3
  axisNext : Fin 2 → V3
  twistPrev : Fin 2 → V3
  twistNext : Fin 2 → V3
  groundAxis : V3
  groundTwist : V3
  basis : Fin 2 → Fin 2 → V3

/-- Body data at one stage (or at the initial time): rotation matrices and the `r, v, w, a, α`
blocks of `unpack_stages`. -/
structure BodyState where
  R : Fin 2 → Matrix (Fin 3) (Fin 3) ℝ
  r : Fin 2 → V3
  v : Fin 2 → V3
  w : Fin 2 → V3
  a : Fin 2 → V3
  α : Fin 2 → V3

namespace BodyState

variable (P : JointParams) (st : BodyState)

/-! ### `joint_kinematics_jax`, transcribed -/

def childPoint (j : Fin 2) : V3 := st.r j + st.R j *ᵥ P.sPrev j
def childVel (j : Fin 2) : V3 := st.v j + st.R j *ᵥ (st.w j ⨯₃ P.sPrev j)
def childAcc (j : Fin 2) : V3 :=
  st.a j + st.R j *ᵥ (st.α j ⨯₃ P.sPrev j + st.w j ⨯₃ (st.w j ⨯₃ P.sPrev j))
def childAxis (j : Fin 2) : V3 := st.R j *ᵥ P.axisPrev j
def childTwist (j : Fin 2) : V3 := st.R j *ᵥ P.twistPrev j
def childAxisRate (j : Fin 2) : V3 := st.R j *ᵥ (st.w j ⨯₃ P.axisPrev j)
def childAxisAcc (j : Fin 2) : V3 :=
  st.R j *ᵥ (st.α j ⨯₃ P.axisPrev j + st.w j ⨯₃ (st.w j ⨯₃ P.axisPrev j))

def parentPoint : Fin 2 → V3 := ![0, st.r 0 + st.R 0 *ᵥ P.sNext 0]
def parentVel : Fin 2 → V3 := ![0, st.v 0 + st.R 0 *ᵥ (st.w 0 ⨯₃ P.sNext 0)]
def parentAcc : Fin 2 → V3 :=
  ![0, st.a 0 + st.R 0 *ᵥ (st.α 0 ⨯₃ P.sNext 0 + st.w 0 ⨯₃ (st.w 0 ⨯₃ P.sNext 0))]
def parentAxis : Fin 2 → V3 := ![P.groundAxis, st.R 0 *ᵥ P.axisNext 0]
def parentTwist : Fin 2 → V3 := ![P.groundTwist, st.R 0 *ᵥ P.twistNext 0]
def parentAxisRate : Fin 2 → V3 := ![0, st.R 0 *ᵥ (st.w 0 ⨯₃ P.axisNext 0)]
def parentAxisAcc : Fin 2 → V3 :=
  ![0, st.R 0 *ᵥ (st.α 0 ⨯₃ P.axisNext 0 + st.w 0 ⨯₃ (st.w 0 ⨯₃ P.axisNext 0))]

def childOmegaWorld (j : Fin 2) : V3 := st.R j *ᵥ st.w j
def childAlphaWorld (j : Fin 2) : V3 := st.R j *ᵥ st.α j
def parentOmegaWorld : Fin 2 → V3 := ![0, st.R 0 *ᵥ st.w 0]
def parentAlphaWorld : Fin 2 → V3 := ![0, st.R 0 *ᵥ st.α 0]

def relPoint (j : Fin 2) : V3 := childPoint P st j - parentPoint P st j
def relVel (j : Fin 2) : V3 := childVel P st j - parentVel P st j
def relAcc (j : Fin 2) : V3 := childAcc P st j - parentAcc P st j
def relOmega (j : Fin 2) : V3 := childOmegaWorld st j - parentOmegaWorld st j
def relAlpha (j : Fin 2) : V3 := childAlphaWorld st j - parentAlphaWorld st j

def axisRes (j : Fin 2) (m : Fin 2) : ℝ := (childAxis P st j - parentAxis P st j) ⬝ᵥ P.basis j m
def axisRate (j : Fin 2) (m : Fin 2) : ℝ :=
  (childAxisRate P st j - parentAxisRate P st j) ⬝ᵥ P.basis j m
def axisAcc (j : Fin 2) (m : Fin 2) : ℝ :=
  (childAxisAcc P st j - parentAxisAcc P st j) ⬝ᵥ P.basis j m

/-- `twist_angle = arctan2(child_twist ⬝ (parent_axis × parent_twist), child_twist ⬝ parent_twist)`
with an opaque `atan2`. -/
def twistAngle (atan2 : ℝ → ℝ → ℝ) (j : Fin 2) : ℝ :=
  atan2 (childTwist P st j ⬝ᵥ (parentAxis P st j ⨯₃ parentTwist P st j))
    (childTwist P st j ⬝ᵥ parentTwist P st j)
def relSpinVel (j : Fin 2) : ℝ := relOmega st j ⬝ᵥ parentAxis P st j
def relSpinAcc (j : Fin 2) : ℝ :=
  relAlpha st j ⬝ᵥ parentAxis P st j + relOmega st j ⬝ᵥ parentAxisRate P st j

end BodyState

/-! ### The non-dynamic rows of one stage -/

/-- Data of one Gauss transition: initial body state, the three stage states, step `h`,
the Gauss matrix `A`, and the opaque `atan2`. -/
structure Transition where
  P : JointParams
  st0 : BodyState
  st : Fin 3 → BodyState
  h : ℝ
  A : Fin 3 → Fin 3 → ℝ
  atan2 : ℝ → ℝ → ℝ

namespace Transition

variable (T : Transition)
open BodyState

/-- `r_coll_axis` -/
def rColl (i : Fin 3) (j : Fin 2) : ℝ :=
  (relPoint T.P (T.st i) j - relPoint T.P T.st0 j
    - T.h • ∑ k, T.A i k • relVel T.P (T.st k) j) ⬝ᵥ parentAxis T.P (T.st i) j
/-- `v_coll_axis` -/
def vColl (i : Fin 3) (j : Fin 2) : ℝ :=
  (relVel T.P (T.st i) j - relVel T.P T.st0 j
    - T.h • ∑ k, T.A i k • relAcc T.P (T.st k) j) ⬝ᵥ parentAxis T.P (T.st i) j
/-- `spin_coll_axis` -/
def spinColl (i : Fin 3) (j : Fin 2) : ℝ :=
  twistAngle T.P (T.st i) T.atan2 j - twistAngle T.P T.st0 T.atan2 j
    - T.h * ∑ k, T.A i k * relSpinVel T.P (T.st k) j
/-- `spin_acc_coll_axis` -/
def spinAccColl (i : Fin 3) (j : Fin 2) : ℝ :=
  relSpinVel T.P (T.st i) j - relSpinVel T.P T.st0 j
    - T.h * ∑ k, T.A i k * relSpinAcc T.P (T.st k) j

/-- `pvel[joint] = [rel_vel ⬝ b0, rel_vel ⬝ b1, r_coll_axis]` -/
def pvel (i : Fin 3) (j : Fin 2) : Fin 3 → ℝ :=
  ![relVel T.P (T.st i) j ⬝ᵥ T.P.basis j 0, relVel T.P (T.st i) j ⬝ᵥ T.P.basis j 1, T.rColl i j]
/-- `pacc[joint] = [rel_acc ⬝ b0, rel_acc ⬝ b1, v_coll_axis]` -/
def pacc (i : Fin 3) (j : Fin 2) : Fin 3 → ℝ :=
  ![relAcc T.P (T.st i) j ⬝ᵥ T.P.basis j 0, relAcc T.P (T.st i) j ⬝ᵥ T.P.basis j 1, T.vColl i j]
/-- `u_block[joint] = [axis_rate (2), spin_coll_axis]` -/
def uBlock (i : Fin 3) (j : Fin 2) : Fin 3 → ℝ :=
  ![axisRate T.P (T.st i) j 0, axisRate T.P (T.st i) j 1, T.spinColl i j]
/-- `w_block[joint] = [axis_acc (2), spin_acc_coll_axis]` -/
def wBlock (i : Fin 3) (j : Fin 2) : Fin 3 → ℝ :=
  ![axisAcc T.P (T.st i) j 0, axisAcc T.P (T.st i) j 1, T.spinAccColl i j]
/-- `constraints[joint] = [basis ⬝ rel_point (2), axis_res (2)]` -/
def constraints (i : Fin 3) (j : Fin 2) : Fin 4 → ℝ :=
  ![relPoint T.P (T.st i) j ⬝ᵥ T.P.basis j 0, relPoint T.P (T.st i) j ⬝ᵥ T.P.basis j 1,
    axisRes T.P (T.st i) j 0, axisRes T.P (T.st i) j 1]

/-- All 96 non-dynamic rows vanish. -/
def NonDynamicRowsVanish : Prop :=
  ∀ i j, T.pvel i j = 0 ∧ T.pacc i j = 0 ∧ T.uBlock i j = 0 ∧ T.wBlock i j = 0 ∧
    T.constraints i j = 0

/-! ### Reduced joint coordinates -/

/-- Sliding coordinate `s = rel_point ⬝ n` along the fixed world direction `n j`
(the normal of the fixed basis plane), and its rates. -/
def slide (n : Fin 2 → V3) (b : BodyState) (j : Fin 2) : ℝ := relPoint T.P b j ⬝ᵥ n j
def slideRate (n : Fin 2 → V3) (b : BodyState) (j : Fin 2) : ℝ := relVel T.P b j ⬝ᵥ n j
def slideAcc (n : Fin 2 → V3) (b : BodyState) (j : Fin 2) : ℝ := relAcc T.P b j ⬝ᵥ n j

/-- Lower-pair constraints at position, velocity and acceleration level, at every stage and at
the initial state (the smooth FullVA lift lies on the constraint manifold with consistent
velocities and accelerations).  These are exactly the 12 constraint rows per joint and stage. -/
def ConstraintsHold : Prop :=
  (∀ i j m, relPoint T.P (T.st i) j ⬝ᵥ T.P.basis j m = 0 ∧ axisRes T.P (T.st i) j m = 0 ∧
      relVel T.P (T.st i) j ⬝ᵥ T.P.basis j m = 0 ∧ axisRate T.P (T.st i) j m = 0 ∧
      relAcc T.P (T.st i) j ⬝ᵥ T.P.basis j m = 0 ∧ axisAcc T.P (T.st i) j m = 0) ∧
  (∀ j m, relPoint T.P T.st0 j ⬝ᵥ T.P.basis j m = 0 ∧ relVel T.P T.st0 j ⬝ᵥ T.P.basis j m = 0)

/-- Three-stage Gauss collocation of the reduced joint coordinates `(s, ṡ, θ, θ̇)`. -/
def ReducedCollocation (n : Fin 2 → V3) : Prop :=
  ∀ i j,
    T.slide n (T.st i) j = T.slide n T.st0 j + T.h * ∑ k, T.A i k * T.slideRate n (T.st k) j ∧
    T.slideRate n (T.st i) j
      = T.slideRate n T.st0 j + T.h * ∑ k, T.A i k * T.slideAcc n (T.st k) j ∧
    twistAngle T.P (T.st i) T.atan2 j
      = twistAngle T.P T.st0 T.atan2 j + T.h * ∑ k, T.A i k * relSpinVel T.P (T.st k) j ∧
    relSpinVel T.P (T.st i) j
      = relSpinVel T.P T.st0 j + T.h * ∑ k, T.A i k * relSpinAcc T.P (T.st k) j

/-- `(n j, basis j 0, basis j 1)` is a complete orthonormal frame:
`x = (x⬝n) n + (x⬝b₀) b₀ + (x⬝b₁) b₁`.  (`joint_basis[j] = perp_basis(axis)`.) -/
def Frame (n : Fin 2 → V3) : Prop :=
  ∀ j (x : V3), x = (x ⬝ᵥ n j) • n j + (x ⬝ᵥ T.P.basis j 0) • T.P.basis j 0
    + (x ⬝ᵥ T.P.basis j 1) • T.P.basis j 1

/-- A vector orthogonal to both basis vectors is parallel to `n`. -/
theorem eq_smul_of_perp {n : Fin 2 → V3} (hF : T.Frame n) (j : Fin 2) (x : V3)
    (h0 : x ⬝ᵥ T.P.basis j 0 = 0) (h1 : x ⬝ᵥ T.P.basis j 1 = 0) :
    x = (x ⬝ᵥ n j) • n j := by
  have := hF j x
  rw [h0, h1, zero_smul, zero_smul, add_zero, add_zero] at this
  exact this

/-- Key algebra of the sliding collocation row: if all relative vectors are parallel to `n`,
the row equals the scalar reduced collocation defect times `n ⬝ axis`. -/
theorem coll_dot (n axis : V3) (x x0 : V3) (y : Fin 3 → V3) (h : ℝ) (A : Fin 3 → ℝ)
    (sx sx0 : ℝ) (sy : Fin 3 → ℝ)
    (hx : x = sx • n) (hx0 : x0 = sx0 • n) (hy : ∀ k, y k = sy k • n) :
    (x - x0 - h • ∑ k, A k • y k) ⬝ᵥ axis = (sx - sx0 - h * ∑ k, A k * sy k) * (n ⬝ᵥ axis) := by
  have hsum : ∑ k, A k • y k = (∑ k, A k * sy k) • n := by
    rw [sum_smul]
    exact sum_congr rfl fun k _ => by rw [hy k, smul_smul]
  rw [hx, hx0, hsum, smul_smul, ← sub_smul, ← sub_smul, smul_dotProduct, smul_eq_mul]

/-- **Direct substitution for the 96 non-dynamic rows.**  Under the constraint identities and
the reduced joint-coordinate Gauss collocation, every implemented non-dynamic row is `0`. -/
theorem nondynamic_rows_vanish {n : Fin 2 → V3} (hF : T.Frame n) (hC : T.ConstraintsHold)
    (hR : T.ReducedCollocation n) : T.NonDynamicRowsVanish := by
  intro i j
  obtain ⟨hC1, hC0⟩ := hC
  -- parallelism of the relative vectors
  have hp : ∀ k, relPoint T.P (T.st k) j = T.slide n (T.st k) j • n j := fun k =>
    T.eq_smul_of_perp hF j _ (hC1 k j 0).1 (hC1 k j 1).1
  have hp0 : relPoint T.P T.st0 j = T.slide n T.st0 j • n j :=
    T.eq_smul_of_perp hF j _ (hC0 j 0).1 (hC0 j 1).1
  have hv : ∀ k, relVel T.P (T.st k) j = T.slideRate n (T.st k) j • n j := fun k =>
    T.eq_smul_of_perp hF j _ (hC1 k j 0).2.2.1 (hC1 k j 1).2.2.1
  have hv0 : relVel T.P T.st0 j = T.slideRate n T.st0 j • n j :=
    T.eq_smul_of_perp hF j _ (hC0 j 0).2 (hC0 j 1).2
  have ha : ∀ k, relAcc T.P (T.st k) j = T.slideAcc n (T.st k) j • n j := fun k =>
    T.eq_smul_of_perp hF j _ (hC1 k j 0).2.2.2.2.1 (hC1 k j 1).2.2.2.2.1
  obtain ⟨hRs, hRv, hRθ, hRω⟩ := hR i j
  have hrColl : T.rColl i j = 0 := by
    unfold rColl
    rw [coll_dot (n j) _ _ _ _ _ _ _ _ _ (hp i) hp0 hv]
    rw [hRs]; ring
  have hvColl : T.vColl i j = 0 := by
    unfold vColl
    rw [coll_dot (n j) _ _ _ _ _ _ _ _ _ (hv i) hv0 ha]
    rw [hRv]; ring
  have hsColl : T.spinColl i j = 0 := by
    unfold spinColl; rw [hRθ]; ring
  have hsaColl : T.spinAccColl i j = 0 := by
    unfold spinAccColl; rw [hRω]; ring
  refine ⟨?_, ?_, ?_, ?_, ?_⟩
  · ext m; fin_cases m
    · exact (hC1 i j 0).2.2.1
    · exact (hC1 i j 1).2.2.1
    · exact hrColl
  · ext m; fin_cases m
    · exact (hC1 i j 0).2.2.2.2.1
    · exact (hC1 i j 1).2.2.2.2.1
    · exact hvColl
  · ext m; fin_cases m
    · exact (hC1 i j 0).2.2.2.1
    · exact (hC1 i j 1).2.2.2.1
    · exact hsColl
  · ext m; fin_cases m
    · exact (hC1 i j 0).2.2.2.2.2
    · exact (hC1 i j 1).2.2.2.2.2
    · exact hsaColl
  · ext m; fin_cases m
    · exact (hC1 i j 0).1
    · exact (hC1 i j 1).1
    · exact (hC1 i j 0).2.1
    · exact (hC1 i j 1).2.1

/-- **Converse**: if the 96 rows vanish (and the initial state is consistent), the constraints
hold at all levels and, provided the sliding direction is not orthogonal to the current joint
axis (`n ⬝ parent_axis ≠ 0`), the reduced joint coordinates satisfy Gauss collocation.  Hence
the implemented FullVA stage system is exactly reduced Gauss collocation plus exact lower-pair
enforcement. -/
theorem reducedCollocation_of_rows {n : Fin 2 → V3} (hF : T.Frame n)
    (hrows : T.NonDynamicRowsVanish)
    (hinit : ∀ j m, relPoint T.P T.st0 j ⬝ᵥ T.P.basis j m = 0 ∧
      relVel T.P T.st0 j ⬝ᵥ T.P.basis j m = 0)
    (hnd : ∀ i j, n j ⬝ᵥ parentAxis T.P (T.st i) j ≠ 0) :
    T.ConstraintsHold ∧ T.ReducedCollocation n := by
  have hC1 : ∀ i j m, relPoint T.P (T.st i) j ⬝ᵥ T.P.basis j m = 0 ∧
      axisRes T.P (T.st i) j m = 0 ∧ relVel T.P (T.st i) j ⬝ᵥ T.P.basis j m = 0 ∧
      axisRate T.P (T.st i) j m = 0 ∧ relAcc T.P (T.st i) j ⬝ᵥ T.P.basis j m = 0 ∧
      axisAcc T.P (T.st i) j m = 0 := by
    intro i j m
    obtain ⟨hpv, hpa, hu, hw, hc⟩ := hrows i j
    have e := fun (f : Fin 3 → ℝ) (hf : f = 0) (k : Fin 3) => congrFun hf k
    have e4 := fun (f : Fin 4 → ℝ) (hf : f = 0) (k : Fin 4) => congrFun hf k
    fin_cases m
    · exact ⟨e4 _ hc 0, e4 _ hc 2, e _ hpv 0, e _ hu 0, e _ hpa 0, e _ hw 0⟩
    · exact ⟨e4 _ hc 1, e4 _ hc 3, e _ hpv 1, e _ hu 1, e _ hpa 1, e _ hw 1⟩
  refine ⟨⟨hC1, hinit⟩, ?_⟩
  intro i j
  obtain ⟨hpv, hpa, hu, hw, -⟩ := hrows i j
  have hrColl : T.rColl i j = 0 := congrFun hpv 2
  have hvColl : T.vColl i j = 0 := congrFun hpa 2
  have hsColl : T.spinColl i j = 0 := congrFun hu 2
  have hsaColl : T.spinAccColl i j = 0 := congrFun hw 2
  have hp : ∀ k, relPoint T.P (T.st k) j = T.slide n (T.st k) j • n j := fun k =>
    T.eq_smul_of_perp hF j _ (hC1 k j 0).1 (hC1 k j 1).1
  have hp0 : relPoint T.P T.st0 j = T.slide n T.st0 j • n j :=
    T.eq_smul_of_perp hF j _ (hinit j 0).1 (hinit j 1).1
  have hv : ∀ k, relVel T.P (T.st k) j = T.slideRate n (T.st k) j • n j := fun k =>
    T.eq_smul_of_perp hF j _ (hC1 k j 0).2.2.1 (hC1 k j 1).2.2.1
  have hv0 : relVel T.P T.st0 j = T.slideRate n T.st0 j • n j :=
    T.eq_smul_of_perp hF j _ (hinit j 0).2 (hinit j 1).2
  have ha : ∀ k, relAcc T.P (T.st k) j = T.slideAcc n (T.st k) j • n j := fun k =>
    T.eq_smul_of_perp hF j _ (hC1 k j 0).2.2.2.2.1 (hC1 k j 1).2.2.2.2.1
  refine ⟨?_, ?_, ?_, ?_⟩
  · unfold rColl at hrColl
    rw [coll_dot (n j) _ _ _ _ _ _ _ _ _ (hp i) hp0 hv] at hrColl
    have := (mul_eq_zero.mp hrColl).resolve_right (hnd i j)
    linarith
  · unfold vColl at hvColl
    rw [coll_dot (n j) _ _ _ _ _ _ _ _ _ (hv i) hv0 ha] at hvColl
    have := (mul_eq_zero.mp hvColl).resolve_right (hnd i j)
    linarith
  · unfold spinColl at hsColl; linarith
  · unfold spinAccColl at hsaColl; linarith

/-- **Equivalence**: implemented non-dynamic rows vanish ⇔ exact lower-pair enforcement at all
three levels + reduced joint-coordinate Gauss collocation (given a consistent initial state and
`n ⬝ parent_axis ≠ 0`). -/
theorem nondynamic_rows_iff {n : Fin 2 → V3} (hF : T.Frame n)
    (hinit : ∀ j m, relPoint T.P T.st0 j ⬝ᵥ T.P.basis j m = 0 ∧
      relVel T.P T.st0 j ⬝ᵥ T.P.basis j m = 0)
    (hnd : ∀ i j, n j ⬝ᵥ parentAxis T.P (T.st i) j ≠ 0) :
    T.NonDynamicRowsVanish ↔ (T.ConstraintsHold ∧ T.ReducedCollocation n) :=
  ⟨fun h => T.reducedCollocation_of_rows hF h hinit hnd,
   fun h => T.nondynamic_rows_vanish hF h.1 h.2⟩

/-- Row count: `3 stages × 2 joints × (3 + 3 + 3 + 3 + 4) = 96`. -/
theorem card_nondynamic_rows : 3 * 2 * (3 + 3 + 3 + 3 + 4) = 96 := by norm_num

end Transition

end IntegratorOrderProof.FullVA
