# Lean-Assisted Residual Row-Family Audit (manuscript vs. implemented residual)

Status: **manuscript/implementation row-family mismatch found; implemented stage residual
vanishes exactly at the lifted reduced Gauss stage (C_R = 0)**. This audit changes no claim
state, closes no P-interface, and does not touch OC4/OC6/OC12. It is a read-only comparison of
`main_cmame.tex` with `v047_cylindrical_chain_pipeline/run_v047.py`, with the algebra
machine-checked in the Lean project (`~/lean/integrator_order_proof`,
`IntegratorOrderProof/FullVA/NonDynamicRows.lean`).

## 0. Status update (2026-09-17, applied)

The manuscript edits recommended in Section 4 were applied on 2026-09-17: `main_cmame.tex`
was compacted from 13047 lines / 259 pages to 3763 lines / 82 pages around
`lem:exact-stage-identity`, the PS2/primitive-Taylor route was removed, and the local defect
is now `C_loc = C_G + C_E + C_N c_eta`. The pre-rewrite source is
`notes/main_cmame_pre_v049_backup.tex`. The new proof gate is `EXACT_STAGE_IDENTITY_GATE.md/json`;
seven route-pinning gates were marked superseded and removed from the package chain. The
modelling sentence of Section 3 has **not** been added to the mechanism description yet.

## 1. Finding: the displayed stage system is not the implemented one

`main_cmame.tex` Eq. `g6fullva-expanded-stage` (line ~600) and Eqs.
`trans-collocation`, `rot-collocation`, `v-collocation`, `w-collocation` (lines ~622-633)
display **body-level** collocation rows for every body and stage:

```
r_i - r_n - h Σ A_ij v_j = 0            (3 rows / body)
η_i - h Σ A_ij J_r^{-1}(η_j) ω_j = 0    (3 rows / body)
v_i - v_n - h Σ A_ij a_j = 0            (3 rows / body)
ω_i - ω_n - h Σ A_ij α_j = 0            (3 rows / body)
```

together with Newton–Euler rows and lower-pair rows `Φ = 0, Φ_q v = 0, Φ_q a + Φ̇_q v = 0`.
The manuscript's row bookkeeping (`lem:d5-p-state-ps2-row-injection`,
`DYNAMIC_ROW_ORACLE_GATE.md` partition) counts these as **72 kinematic collocation rows + 24
lower-pair rows + 36 Newton–Euler rows**.

`residual_cylindrical_chain` in `run_v047.py` (lines ~4926-5030) contains **no body-level
collocation row at all**. Per stage and per joint it assembles 16 rows:

| code block | rows | actual content |
| --- | ---: | --- |
| `constraints` | 4 | `joint_basis ⬝ rel_point` (2), `axis_res` (2): position-level constraints |
| `pvel` | 3 | `rel_vel ⬝ basis` (2): velocity-level constraints; `r_coll_axis`: Gauss collocation of the **sliding coordinate** `s = rel_point ⬝ n` |
| `u_block` | 3 | `axis_rate` (2): velocity-level alignment constraints; `spin_coll_axis`: Gauss collocation of the **twist angle** `θ` (`arctan2`) |
| `pacc` | 3 | `rel_acc ⬝ basis` (2): acceleration-level constraints; `v_coll_axis`: collocation of `ṡ` |
| `w_block` | 3 | `axis_acc` (2): acceleration-level alignment constraints; `spin_acc_coll_axis`: collocation of `θ̇` |

So the implemented non-dynamic block is **72 constraint rows (position, velocity and
acceleration level, 12 per joint-stage) + 24 joint-coordinate collocation rows (4 per
joint-stage)**. The counts 72/24 in the manuscript are the implemented counts with the roles
swapped: what the manuscript calls "kinematic collocation rows" are in the code 48 constraint
rows plus 24 joint-coordinate collocation rows, and what it calls "24 lower-pair rows" are only
the 24 position-level constraint rows.

Two internal inconsistencies in the manuscript follow:

- As displayed, Eq. `g6fullva-expanded-stage` has `24 + 12 + 24 = 60` rows per stage for the
  `44` unknowns of Eq. `stage-count` (three constraint levels of 8 constraints each are shown,
  but only 8 lower-pair rows per stage are counted).
- The "FullVA = full position, velocity and acceleration enforcement" definition matches the
  code (24 constraint rows per stage) but not the displayed/counted row families.

The row-family names in `DYNAMIC_ROW_ORACLE_GATE.md`, `KINEMATIC_ROW_DEFECT_CERTIFICATE.md`
and `validate_dynamic_row_oracle_gate.py` (`translational_position_weak_defect`, ...) are
labels attached to the code blocks `pvel`, `u_block`, `pacc`, `w_block`; the validator's
"independent formula rows" are the same block formulas re-typed. The oracle therefore checks
runtime against itself, not against the manuscript's equations. The Jacobian structure
subsection (`δR^r_i = δr_i - h Σ A_ij δv_j`, ...) and the PS2 kinematic-block lemmas
(`lem:d5-p-state-ps2-kinematic-block`, `lem:d5-p-state-ps2-row-injection`,
`lem:d5-p-state-ps2-lie-chart-binding`) describe the displayed rows, not the implemented ones.

## 2. Consequence for the proof: the stage residual is exactly zero at the lift

Because the implemented collocation rows act on the **joint coordinates themselves**
(`s, θ, ṡ, θ̇`, which are linear coordinates of the reduced chart), and all other non-dynamic
rows are constraint rows, the following holds exactly (Lean:
`FullVA.Transition.nondynamic_rows_iff`):

> The 96 implemented non-dynamic rows vanish **iff** the lower-pair constraints hold at
> position, velocity and acceleration level at every stage **and** `(s, ṡ, θ, θ̇)` of each joint
> satisfy three-stage Gauss collocation. (Hypotheses: `joint_basis[j]` together with the fixed
> sliding direction `n_j` is a complete orthonormal frame, the initial state is consistent, and
> `n_j ⬝ parent_axis ≠ 0` at the stages.)

Together with `NewtonEuler.dynamic_rows_vanish` (36 rows), the lifted reduced Gauss stage
satisfies **all 132 rows exactly**: `F_{A,h}(Z_G; y) = 0`, i.e. the residual-value input
`‖F_{A,h}(Z_G)‖ ≤ C_R h⁷` of `lem:full-132-row-residual-bridge` holds with `C_R = 0`, hence
`Z_A = Z_G` and `C_Z = C_A = 0` in the local-defect sum. Equivalently: **the implemented
`Gauss6/FullVA` stage system is exactly three-stage Gauss collocation on the 8-dimensional
reduced joint-coordinate ODE**, with the absolute-coordinate stage variables recovered by the
exact lift; only the endpoint reconstruction `𝓔_h` (Eqs. `end-trans`, `end-rot`), the endpoint
closure `𝓒_h`, and the inexact Newton solve contribute `O(h⁷)` local terms.

Remarks:

- Had the code implemented the displayed body-level rows, the direct-substitution argument of
  `KINEMATIC_ROW_DEFECT_CERTIFICATE.md` ("the four collocation row families vanish by the
  defining Gauss collocation identities") would be **false**: a stage collocation row applied to
  a nonlinear function of the reduced state has defect `O(h^{s+1}) = O(h⁴)`, not `O(h⁷)`. The
  certificate's conclusion is correct only because the implemented rows are joint-coordinate
  rows.
- The open primitive/Taylor lane (`P_state`, `P_acc`, `P_λ`, `P_geom`, `P_gyro`, the 162
  subterms) and the PS2/PS3 machinery are bounds for a residual-value input that is identically
  zero on the accepted branch; they are not needed for `thm:g6fullva-order`.
- P6 (`η_h ≤ c_η h⁷`), the endpoint-closure constants, the stability scale and P7 are untouched.

## 3. Secondary modelling observation (not a proof issue)

`make_params` uses skew axes (`axis_prev[0] ∦ axis_next[0]`) and a nonzero spin rate for body 0,
so `parent_axis[1] = R_0 axis_next[0]` rotates in the world frame, while `joint_basis[1]` is
computed once at `t = 0` and frozen. Joint 1 therefore constrains the relative translation to
the **fixed world direction** `n_1` while the shared rotation axis moves on a cone. This is a
valid 4-constraint lower pair, but not a cylindrical joint in the usual sense (sliding direction
≠ current rotation axis), and the friction sliding speed `slide_vel = rel_vel ⬝ parent_axis`
equals `ṡ (n_1 ⬝ parent_axis)` rather than `ṡ`. Worth a sentence in the mechanism description.

## 4. Suggested manuscript edits (for the author to decide)

1. Replace Eq. `g6fullva-expanded-stage` and Eqs. `trans-collocation`-`w-collocation` by the
   implemented rows: 12 constraint rows per joint-stage plus 4 joint-coordinate collocation rows
   (`s, θ, ṡ, θ̇`); fix the 72/24 row-family description accordingly.
2. State `F_{A,h}(Z_G) = 0` exactly (direct substitution for all 132 rows), set `C_R = C_A = 0`,
   and retire the PS2/primitive-Taylor route as unnecessary for the residual-value input.
3. Rewrite the Jacobian-structure subsection for the implemented rows, or drop it (AD is used).
4. Add the reduced-Gauss equivalence as the one-line reason for the sixth order: the method is
   Gauss6 on the reduced joint-coordinate ODE plus an `O(h⁷)` endpoint reconstruction/closure.

## 5. Evidence pointers

- `run_v047.py`: `joint_kinematics_jax` (~line 4840), `residual_cylindrical_chain`
  (~4926-5030), `make_params` (~4248).
- `main_cmame.tex`: lines ~560-650 (stage vector, Eq. `g6fullva-expanded-stage`, row families,
  endpoint), ~4880-4960 (PS2 kinematic block, 72-to-96 injection).
- `validate_dynamic_row_oracle_gate.py`: `EXPECTED_LAYOUT`, `independent_formula_rows`.
- Lean: `IntegratorOrderProof/FullVA/NonDynamicRows.lean` (`nondynamic_rows_vanish`,
  `reducedCollocation_of_rows`, `nondynamic_rows_iff`), `NewtonEuler/DynamicRows.lean`.
