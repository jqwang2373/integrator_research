# Numerical Order Proof Ledger

This file records the mathematical order argument for each preserved version.
It is deliberately separate from the experiment reports: the reports record what
ran, while this file records why an observed order is or is not expected.

## Conventions

For a one-step map `Phi_h`, global order `p` means that, for a smooth exact
solution and a stable integration interval,

```text
||x_n - x(t_n)|| <= C h^p,      0 <= t_n <= T.
```

Equivalently, the local truncation error is `O(h^(p+1))`. For Lie-group states,
the norm is measured after applying the local logarithm/retraction chart near
the exact solution. For index-3 DAE variants, this ledger separates three
claims:

- `proved`: follows from a standard ODE/Lie-group/collocation theorem under
  stated smoothness and regularity assumptions.
- `conditional`: the method should inherit the stated order if the square DAE
  residual is locally equivalent to a regular constrained flow and Newton solves
  are accurate enough; a full DAE theorem is still pending.
- `empirical/diagnostic`: the version measures behavior or changes the solver
  backend, but it does not by itself prove a time-discretization order.

## Reused Lemmas

### Lemma A: Lie-group local coordinates preserve order

Let `G` be a Lie group and let `R_xi(q)=q exp(xi)` or `exp(xi) q` be a smooth
local retraction. If a Runge-Kutta/collocation method has order `p` for the
local coordinate ODE

```text
dot xi = dexp_xi^{-1} f(R_xi(q_n)),
xi(0)=0,
```

and `exp`, `log`, and `dexp^{-1}` are evaluated consistently in a neighborhood
of the exact solution, then the induced one-step map on `G` has order `p`. The
proof is the usual chart argument: the exact and numerical maps are compared in
the same smooth local coordinates, and the chart/retraction has bounded
derivatives on the compact trajectory segment.

### Lemma B: Collocation order

For a smooth ODE, an `s`-stage Gauss-Legendre collocation method has global
order `2s`. Thus two-stage Gauss has order 4 and three-stage Gauss has order 6.
The proof follows from collocation orthogonality: the defect is orthogonal to
polynomials through degree `s-1`, giving stage order `s` and classical order
`2s` for Gauss nodes.

### Lemma C: Symmetric composition

Implicit midpoint is symmetric and order 2. A Yoshida composition with
coefficients chosen so the third-order term in the Baker-Campbell-Hausdorff
expansion cancels gives a symmetric fourth-order method. The leading nonzero
modified-vector-field error term is then `O(h^5)` locally, hence global order 4.

### Lemma D: Smooth constraints by reduction

If holonomic constraints can be solved locally by a smooth parametrization
`x=chi(y)`, and the numerical method of order `p` is applied to the reduced
smooth ODE for `y`, then the reconstructed constrained state also has order `p`.
This follows from the bounded derivatives of `chi`. Reconstructed multipliers
inherit the order implied by differentiating the constraints, provided the
constraint Jacobian has full rank and the mass matrix is regular.

### Lemma E: Exact AD and sparse linear algebra do not change order

Replacing finite-difference Jacobians by exact automatic differentiation,
replacing dense linear solves by exact sparse solves, or assembling the same
Jacobian by colored JVPs does not change the one-step map, assuming Newton is
solved to the same tolerance. The discretization order is unchanged; only the
nonlinear-solve perturbation changes, and that perturbation is negligible if the
Newton residual is `o(h^(p+1))`.

### Lemma F: Smooth friction versus sharp friction

For fixed regularization parameters, tanh/Stribeck/Brown-McPhee-style velocity
friction laws used here are smooth maps, so the formal order of a smooth
collocation method still applies in the asymptotic regime. If the velocity
transition scale is small, derivatives of the vector field become large and the
asymptotic regime may require smaller `h` than tested. Observed order reduction
in sharp-friction experiments is therefore not a contradiction of Lemma B; it is
a pre-asymptotic or limited-regularity effect, and true nonsmooth stick-slip or
contact needs a different theorem.

### Lemma G: Projection is order-preserving only under a small-correction
condition

A smooth post-step projection onto a constraint manifold preserves order `p` if
the unprojected endpoint constraint violation and projection correction are
`O(h^(p+1))`. If the correction is larger, projection can improve constraints
while changing the trajectory order or error constant.

## Version Proof Records

### v001_so3_benchmarks

- Expected order: not applicable.
- Proof status: diagnostic infrastructure only.
- Proof sketch: v001 defines reference problems and error measurements; it does
  not introduce a method whose order needs proof.
- Caveat: use this only as a measurement baseline.

### v002_cf4_right_order

- Expected order: 4 for corrected `cf4` and `rkmk4` on prescribed smooth
  attitude kinematics.
- Proof status: proved under Lemma A and the fourth-order CF/RKMK order
  conditions.
- Proof sketch: the attitude equation is transformed to the Lie algebra chart.
  The corrected right-action ordering satisfies the order-4 commutator-free or
  RKMK conditions, so local error is `O(h^5)` and global error is `O(h^4)`.
- Caveat: this proves kinematics only, not constrained dynamics.

### v003_sbel_ra_repro

- Expected order: not locally proved; the reproduced reference path is treated
  as an external baseline.
- Proof status: empirical/diagnostic.
- Proof sketch: v003 preserves and runs the SBEL/Negrut rA code path. Since the
  local work does not rederive that code's full time-discretization theorem, the
  ledger records measured behavior rather than a proof.
- Caveat: useful as a reproducibility anchor, not as a local high-order claim.

### v004_yoshida_midpoint

- Expected order: 4 for smooth conservative rigid-body mechanics.
- Proof status: proved under Lemma C plus Lemma A.
- Proof sketch: Lie midpoint is a second-order symmetric method in local
  coordinates. Yoshida composition cancels the leading odd modified-equation
  error term, making the composed one-step map locally `O(h^5)` accurate.
- Caveat: negative substeps in the composition are mathematically allowed for
  smooth reversible dynamics but are poor for friction/contact.

### v005_gauss_lie4

- Expected order: 4 for smooth torque-free rigid-body mechanics.
- Proof status: proved under Lemma A and Lemma B with `s=2`.
- Proof sketch: the body-angular-velocity dynamics is solved by two-stage
  Gauss collocation in a Lie-algebra chart. The charted ODE is smooth, so the
  Gauss method has local error `O(h^5)` and global error `O(h^4)`.
- Caveat: the proof covers smooth mechanics, not nonsmooth loads.

### v006_fixed_pivot_dae

- Expected order: 4 for the reduced fixed-pivot constrained rigid body.
- Proof status: proved under Lemma D plus the v005 proof.
- Proof sketch: the fixed-pivot constraint `r + R s = 0` is eliminated by a
  smooth reconstruction from the attitude. Applying v005 to the reduced smooth
  attitude dynamics gives order 4; the reconstructed position, velocity, and
  multiplier inherit that order under full-rank constraint Jacobian assumptions.
- Caveat: this is a reduced constrained problem, not a general absolute DAE.

### v007_absolute_gauss_dae

- Expected order: 4 only for the position+velocity+acceleration-consistent
  variant.
- Proof status: conditional.
- Proof sketch: if the absolute-coordinate stage residual with position,
  velocity, and acceleration consistency is locally equivalent to the reduced
  constrained flow of v006, then two-stage Gauss inherits order 4 by Lemma B and
  Lemma D. The position-only and position+velocity-only variants violate this
  equivalence and therefore have no fourth-order proof.
- Caveat: a full index-3 DAE collocation theorem for this square residual is
  not yet written.

### v008_endpoint_constrained_dae

- Expected order: 4 for the smooth fixed-pivot endpoint DAE.
- Proof status: conditional.
- Proof sketch: adding endpoint variables and endpoint position/velocity
  constraints internalizes the projection used in v007. If the augmented
  residual is nonsingular and defines the same reduced one-step map, it inherits
  the v006/v007 order-4 argument.
- Caveat: the order proof depends on regularity of the augmented Newton system.

### v009_friction_endpoint_dae

- Expected order: 4 for smooth regularized friction; reduced observed order in
  sharp regimes.
- Proof status: proved for fixed smooth regularization; empirical near sharp
  transitions.
- Proof sketch: for fixed `eps>0`, the tanh friction law is smooth, so the
  v008 order-4 argument applies to the smooth dissipative vector field. As
  `eps` decreases, derivatives grow like powers of `1/eps`, increasing error
  constants and delaying the asymptotic `h^4` regime.
- Caveat: this is not a nonsmooth Coulomb/stick-slip proof.

### v010_jax_jacobian_endpoint_dae

- Expected order: same as v009.
- Proof status: proved as a solver-backend invariance under Lemma E.
- Proof sketch: AD changes only the Newton Jacobian construction, not the
  residual defining the time step. If Newton tolerances are matched, the
  numerical one-step map is the same up to solver tolerance, so the order is
  unchanged.
- Caveat: runtime improves; discretization order does not.

### v011_s3_transport_operator

- Expected order: not a time-integrator order.
- Proof status: operator identity.
- Proof sketch: with `p(theta)=p0 exp(theta/2)` or `exp(theta/2) p0`, the chain
  rule gives `d g / d theta = g_p T_exp + g_theta`. This proves the
  first-variation transport identity used later for rotational Jacobians.
- Caveat: this validates Jacobian transport, not temporal convergence.

### v012_quaternion_endpoint_dae

- Expected order: same as v010/v009, namely order 4 for smooth regularized
  friction.
- Proof status: proved conditionally by chart equivalence.
- Proof sketch: unit quaternions on `S^3` cover the same local rotation as the
  SO(3) residual, modulo the sign double cover. In a fixed local chart away
  from the antipodal ambiguity, Lemma A maps the v010 SO(3) order argument to
  the quaternion residual.
- Caveat: the proof is local on `S^3`; sign choices must remain continuous.

### v013_gauss6_quaternion_endpoint_dae

- Expected order: 6 for smooth regularized friction.
- Proof status: proved under Lemma A, Lemma B with `s=3`, and the v012
  regularity assumptions.
- Proof sketch: the three-stage Gauss-Legendre residual is order 6 in the
  quaternion local chart. Smooth retraction to `S^3` preserves that order.
- Caveat: sharp friction can remain pre-asymptotic and show lower observed
  order by Lemma F.

### v014_friction_smoothness_sweep

- Expected order: inherits v013 for each fixed smooth regularization.
- Proof status: diagnostic consequence of Lemma F.
- Proof sketch: the sweep varies the derivative scale of the smooth friction
  law. The formal order remains six for fixed `eps`, but error constants grow
  as the friction transition sharpens.
- Caveat: the version establishes a practical decision boundary, not a new
  theorem.

### v015_adaptive_gauss64_endpoint

- Expected order: base accepted high-order solution is order 6 in smooth
  intervals; the embedded estimate is lower order and controls local error.
- Proof status: proved for smooth variable-step RK under standard assumptions,
  empirical near sharp friction.
- Proof sketch: each accepted step uses the Gauss6 solution. The embedded
  Gauss4 estimate gives an error proxy proportional to the leading difference
  between fourth- and sixth-order maps. With bounded step ratios and smooth
  dynamics, variable-step stability preserves the base order as tolerance tends
  to zero.
- Caveat: near sharp friction transitions, adaptivity is a practical error
  control strategy rather than a proof of uniform order.

### v016_trapezoidal_baseline

- Expected order: 2 for Lie-trapezoidal; Gauss6 comparison remains order 6 in
  smooth cases.
- Proof status: proved for the reduced smooth problem.
- Proof sketch: trapezoidal collocation has local error `O(h^3)` and global
  error `O(h^2)` in the local Lie chart. Exact reduced constraint
  reconstruction does not lower order by Lemma D.
- Caveat: v016 is a favorable reduced-coordinate baseline, not a full DAE
  trapezoidal theorem.

### v017_lie_bdf2_baseline

- Expected order: 2 after startup for smooth problems.
- Proof status: proved under standard BDF2 consistency and zero-stability plus
  Lemma A.
- Proof sketch: the BDF2 difference formula has truncation error `O(h^3)` and
  is zero-stable. Applied in the local Lie chart with a consistent startup, it
  gives global order 2.
- Caveat: BDF2 is dissipative and not a high-order accuracy competitor here.

### v018_lobatto_endpoint_baseline

- Expected order: fourth/sixth for the reduced Lobatto variants implemented in
  this version, under smoothness.
- Proof status: proved for the reduced ODE-style Lobatto residual.
- Proof sketch: the reduced endpoint-node residual is a smooth collocation
  scheme in local coordinates. Its polynomial degree/node construction gives
  the expected classical Lobatto order, and the Lie chart preserves it by
  Lemma A.
- Caveat: this does not prove the full TFE/index-3 DAE method; v024 shows a
  direct full-DAE Lobatto node swap can fail.

### v019_lambda_dependent_friction

- Expected order: 6 for smooth multiplier-dependent friction when the algebraic
  multiplier solve is regular.
- Proof status: conditional.
- Proof sketch: if the stage DAE equations define smooth stage multipliers by
  the implicit-function theorem, the multiplier-dependent friction becomes a
  smooth reduced vector field. Then v013's Gauss6 order proof applies.
- Caveat: loss of multiplier regularity or sharp friction can reduce observed
  order.

### v020_adaptive_lambda_friction

- Expected order: adaptive version of v019; base accepted smooth steps are
  order 6.
- Proof status: conditional plus adaptive argument from v015.
- Proof sketch: combine the v019 implicit-function argument with the v015
  variable-step Gauss6/Gauss4 error-control argument.
- Caveat: the sharp multiplier-friction advantage is empirical error control,
  not a uniform nonsmooth order theorem.

### v021_brown_mcphee_lambda_friction

- Expected order: 6 for smooth Brown-McPhee regularization and regular
  multiplier coupling.
- Proof status: conditional.
- Proof sketch: the implemented Brown-McPhee-style velocity curve is smooth for
  fixed parameters. If reaction-load multipliers depend smoothly on stages, the
  residual reduces to a smooth vector field and inherits v013/v019 order 6.
- Caveat: sharp Stribeck scales increase constants and cause observed order
  reduction.

### v022_revolute_brown_mcphee

- Expected order: 6 for the smooth scalar revolute Brown-McPhee pendulum.
- Proof status: proved for the reduced scalar ODE/DAE surrogate.
- Proof sketch: the scalar revolute coordinate is a smooth local coordinate for
  the unit-quaternion output. Three-stage Gauss collocation on the scalar smooth
  equation is order 6, and the quaternion reconstruction preserves order.
- Caveat: the version is reduced-coordinate, not full absolute-coordinate DAE.

### v023_absolute_revolute_dae

- Expected order: not fully proved for the raw full absolute-coordinate DAE.
- Proof status: conditional/empirical.
- Proof sketch: if the five-constraint absolute-coordinate residual were shown
  locally equivalent to the reduced revolute flow with regular multipliers,
  Gauss6 would inherit order 6 for smooth friction. However, visible endpoint
  velocity drift shows the raw residual is missing important index-3
  consistency, so the full proof is deliberately withheld.
- Caveat: v023 is evidence of robustness of Gauss6 over Gauss4, not a complete
  order theorem.

### v024_absolute_revolute_lobatto_dae

- Expected order: none, because the tested direct Lobatto full-DAE residual
  fails.
- Proof status: negative diagnostic.
- Proof sketch: a Lobatto collocation theorem requires a regular nonlinear
  system. The observed rank-deficient/divergent Newton systems violate that
  premise, so no order proof applies.
- Caveat: this does not disprove TFE; it disproves only the direct node-swap
  residual tested here.

### v025_absolute_revolute_projected_dae

- Expected order: conditional on projection correction size.
- Proof status: conditional under Lemma G.
- Proof sketch: if the raw endpoint constraint error is `O(h^7)` for Gauss6,
  the smooth projection would preserve order 6. In the recorded runs, projection
  materially changes trajectory errors, so this condition is not assumed.
- Caveat: projection is a constraint-closure and robustness repair, not a
  proved high-order DAE method in this ledger.

### v026_absolute_revolute_stage_velocity_dae

- Expected order: conditional Gauss6 order for smooth friction.
- Proof status: conditional.
- Proof sketch: replacing stage position collocation rows with pivot velocity
  constraints keeps the Newton system square. If this residual is locally
  equivalent to enforcing the reduced revolute tangent dynamics, Lemma B gives
  order 6 for Gauss6.
- Caveat: the proof is incomplete because only part of lower-pair consistency
  is enforced.

### v027_absolute_revolute_stage_acceleration_dae

- Expected order: conditional Gauss6 order for smooth friction.
- Proof status: stronger conditional result than v026.
- Proof sketch: adding pivot acceleration rows makes the residual closer to the
  index-3 differentiated constraint chain. Under full-rank constraint
  Jacobians and smooth multiplier dependence, the residual should define the
  same reduced revolute flow, so Gauss6 inherits order 6.
- Caveat: this still needs a written DAE collocation proof for the exact square
  residual.

### v028_offaxis_revolute_full_axis_dae

- Expected order: same conditional order as v027.
- Proof status: conditional/diagnostic.
- Proof sketch: FullVA adds hinge-axis velocity/acceleration consistency while
  keeping a square residual. These rows constrain the same smooth one-DOF
  manifold; if the augmented residual remains regular, the v027 order argument
  is unchanged.
- Caveat: v028 mainly verifies axis consistency, not a new temporal order.

### v029_double_revolute_pivotva_dae

- Expected order: conditional Gauss6 order for smooth multi-joint DAE.
- Proof status: conditional.
- Proof sketch: extend the v027 implicit-function argument to a two-body
  constraint manifold. If the combined ground and interbody revolute constraint
  Jacobian has full rank and the square PivotVA/FullVA residual is locally
  equivalent to the constrained flow, three-stage Gauss gives order 6.
- Caveat: the current evidence emphasizes drift reduction and robustness; a
  formal multi-joint DAE order proof remains pending.

### v030_double_revolute_jacobian_sparsity

- Expected order: not applicable.
- Proof status: diagnostic.
- Proof sketch: v030 extracts and times linear systems from v029. It does not
  alter the one-step discretization.
- Caveat: this is solver-scaling evidence only.

### v031_sparse_newton_double_revolute

- Expected order: same as v029 conditional order.
- Proof status: solver-backend invariance under Lemma E.
- Proof sketch: replacing dense linear solves with CSR solves changes neither
  the nonlinear residual nor the converged Newton solution, assuming residual
  tolerances and pivoting accuracy are adequate.
- Caveat: order depends on the still-conditional v029 DAE formulation proof.

### v032_matrix_free_newton_krylov

- Expected order: none for the failed GMRES runs; JVP itself is algebraically
  correct.
- Proof status: negative solver diagnostic.
- Proof sketch: if GMRES solved the Newton corrections to the same tolerance,
  Lemma E would preserve order. It does not converge in the recorded tests, so
  no method-order claim follows.
- Caveat: preconditioned Krylov could still be order-preserving.

### v033_lagged_sparse_newton

- Expected order: same as v029 if lagged Newton still solves residuals to
  `o(h^(p+1))`.
- Proof status: conditional solver perturbation.
- Proof sketch: modified Newton produces the same one-step map only when the
  final residual is sufficiently small. If stopping tolerances enforce that,
  lagging affects cost but not order.
- Caveat: v033 is not a useful speed win in the current benchmark.

### v034_colored_jvp_sparse_jacobian

- Expected order: same as v029/v031.
- Proof status: solver-backend invariance.
- Proof sketch: column coloring with JVPs reconstructs the same sparse Jacobian
  values as dense AD when the sparsity pattern is correct. By Lemma E, the
  converged one-step map and order are unchanged.
- Caveat: v034 is correct but slower at this scale.

### v035_batched_colored_jvp

- Expected order: same as v034.
- Proof status: solver-backend invariance.
- Proof sketch: batching colored seeds changes evaluation schedule only. The
  assembled Jacobian entries are the same as v034, so the time-discretization
  order is unchanged.
- Caveat: this is the first positive sparse-AD speed result, not a new order
  theorem.

### v036_symbolic_block_pattern

- Expected order: same as v035 if the symbolic block pattern has zero missing
  active entries.
- Proof status: conditional solver-backend invariance.
- Proof sketch: an overconservative sparsity pattern may add structural zeros
  but does not remove true Jacobian entries. With zero missed entries, colored
  JVP reconstructs the same Jacobian on the active pattern, preserving Newton
  and order by Lemma E.
- Caveat: pattern correctness is validated empirically, not formally derived
  for all possible states.

### v037_jvp_pruned_symbolic_pattern

- Expected order: same as v036 if pruning misses no active entries.
- Proof status: conditional solver-backend invariance.
- Proof sketch: JVP pruning removes entries observed to be inactive during a
  dry-run. If the resulting mask contains all active Jacobian entries on the
  solved trajectory, the sparse Jacobian equals dense AD on that trajectory and
  the order is unchanged.
- Caveat: this is path-sampled rather than a global symbolic proof.

### v038_pattern_cache_reuse

- Expected order: same as v037 if the cached mask remains a superset of active
  entries.
- Proof status: conditional solver-backend invariance.
- Proof sketch: cache reuse changes only pattern acquisition. If validation or
  refresh confirms zero missing active entries, the Newton residual and
  assembled Jacobian are equivalent to the dense path on the trajectory.
- Caveat: cache validity is local to the tested state/friction regimes.

### v039_triple_revolute_scaling

- Expected order: conditional Gauss6 order for the triple-revolute FullVA DAE;
  sparse backend preserves whatever order the residual has.
- Proof status: conditional formulation plus Lemma E.
- Proof sketch: if the three-body revolute FullVA residual is a regular
  square representation of the constrained flow, three-stage Gauss gives order
  6 in smooth regimes. The JVP-pruned sparse backend does not change that map
  when the pattern has zero missing entries.
- Caveat: v039 focuses on larger-topology sparse scaling, not an order sweep.

### v040_generated_block_triple_pattern

- Expected order: same as v039.
- Proof status: solver-backend invariance.
- Proof sketch: replacing a full-matrix superset with a generated block
  superset changes pattern discovery only. Zero dense-validation misses mean no
  active derivative is dropped, so the converged residual map is unchanged.
- Caveat: the block-dependency generator is validated on this topology, not
  formally proven for all multibody graphs.

### v041_triple_pattern_cache_refresh

- Expected order: same as v039/v040 after successful refresh.
- Proof status: conditional solver-backend invariance.
- Proof sketch: refresh/union scans the generated block superset and restores
  newly active entries. If the final cache has zero missing active entries, the
  sparse Newton step equals the dense-AD step up to solver tolerance.
- Caveat: the policy needs broader state coverage before being a production
  theorem.

### v042_skew_axis_triple_revolute

- Expected order: conditional Gauss6 order for smooth skew-axis revolute DAE.
- Proof status: conditional formulation plus Lemma E.
- Proof sketch: skew parent-child axis constraints are still smooth holonomic
  lower-pair constraints when the constraint Jacobian has full rank. With
  compatible initial rates and a regular FullVA residual, three-stage Gauss
  should inherit order 6; the sparse pattern machinery preserves that map.
- Caveat: v042 validates non-coplanar geometry and sparse correctness, not a
  formal DAE order theorem.

### v043_skew_prismatic_lower_pair

- Expected order: conditional Gauss6 order for smooth prismatic sliding DAE.
- Proof status: conditional formulation plus Lemma E.
- Proof sketch: the prismatic joint defines a smooth constraint manifold with
  one free sliding coordinate if the five constraint rows have full rank.
  Brown-McPhee-style sliding friction is smooth for fixed parameters and normal
  load regularization. Under those assumptions, the FullVA residual should be
  locally equivalent to a smooth constrained flow, so three-stage Gauss gives
  order 6. The dense and sparse Jacobian paths define the same Newton map when
  the 414-entry pruned pattern has zero missing entries.
- Caveat: v043 is a correctness/coverage result for a 69D single-body
  prismatic test. It does not yet prove large interbody prismatic/cylindrical
  order or speed scaling.

### v044_double_prismatic_chain

- Expected order: conditional Gauss6 order for a smooth two-body
  double-prismatic DAE.
- Proof status: conditional formulation plus Lemma E.
- Proof sketch: each prismatic joint defines two perpendicular translational
  constraints, two axis-alignment constraints, one twist-lock constraint, and
  one free sliding coordinate. If the combined ground and interbody prismatic
  constraint Jacobian has full rank, and the square FullVA residual is locally
  equivalent to the reduced constrained flow, the three-stage Gauss residual
  gives order 6 for smooth Brown-McPhee regularization. The generated-block
  sparse-AD backend preserves that one-step map because the 2439-entry pruned
  pattern has zero dense-validation misses.
- Caveat: the proof remains conditional on the DAE residual regularity. v044
  proves interbody prismatic sparse-pattern correctness locally, but the 90-color
  pattern is not a speed improvement and does not yet cover cylindrical or
  rotating-axis mixed joints.

### v045_row_colored_vjp_prismatic

- Expected order: same conditional Gauss6 order as v044.
- Proof status: solver-backend invariance under Lemma E.
- Proof sketch: v045 does not change the residual, quadrature nodes, constraints,
  friction law, or Newton stopping criteria. It changes only sparse Jacobian
  assembly: rows with disjoint column support are seeded together through a
  batched VJP. If the row-colored VJP matrix matches the dense Jacobian on the
  active sparse pattern and the pattern has zero dense-validation misses, the
  Newton correction is the same up to solver tolerance. Therefore v045 inherits
  v044's conditional temporal order.
- Caveat: row coloring reduces seed count but does not prove a new integrator
  order. The measured speed remains below dense `jacfwd` at 138D.

### v046_asme_four_examples_validation

- Expected order: not a new local method order. The measured upstream rA
  trajectory orders are empirical properties of the SBEL/Negrut implementation,
  tolerance schedule, and four ASME examples.
- Proof status: empirical/diagnostic validation.
- Proof sketch: v046 reuses the upstream rA formulation and compares h=[0.02,
  0.01, 0.005] trajectories against h=0.001 references. The observed orders
  and constraint/SO(3) diagnostics are validation evidence for the baseline
  harness, not a theorem for the quaternion Gauss6/FullVA path.
- Caveat: only the double pendulum passes the strict constraint checks in the
  recorded run. Future method versions should use the same four-example gate
  and add their own proof/status entry rather than relying on v046's baseline
  result.

### v047_cylindrical_chain_pipeline

- Expected order: conditional sixth order for the accepted smooth
  `Gauss6/FullVA` map under the compact-branch theorem interfaces recorded in
  `paper_v047_cylindrical_chain/PROOF_CLAIM_TRACEABILITY_AUDIT.md`: P1/P2
  compact-tube and endpoint right-inverse hypotheses, P3/P4 implementation
  binding, the discharged P5 direct Newton--Euler residual bridge, and the
  retained P6 branch-selected solver scale
  `eta_h^tube <= c_eta h^7`.
- Primary claim boundary: v047's paper-facing claim is a conditional formal-order comparison,
  not a full source-paper residual reproduction,
  source-policy superiority, or work-precision claim. Within the current
  artifact scope, the accepted Gauss6/FullVA path is sixth order and records
  smooth position/velocity orders 7.161/7.066, while the encoded local
  paper-style `m=3` Gauss-Lobatto TFE formula target has expected order five.
  `paper_v047_cylindrical_chain/ORDER_ACCEPTANCE_GATE.md` now records the
  example-level order boundary: single_pendulum and double_pendulum have
  accepted dynamic order rows, while four_link and slider_crank are
  mechanism-coverage rows and not accepted external dynamic order.
  The independent full-TFE replacement remains an optional stronger
  source-paper reproduction gate and is not required for this bounded
  formal-order comparison.
- Proof status: direct-route conditional Gauss6/FullVA proof closed for the
  paper-facing method theorem; P1/P2/P3/P4/P6 remain retained theorem
  interfaces, P7 remains the open residual-to-error nonpromotion boundary, and
  global submission gates remain explicit.
- Proof sketch: a cylindrical joint has four holonomic constraint rows: two
  perpendicular point constraints and two axis-alignment constraints. The axial
  slide and relative spin are free coordinates collocated by the Gauss6 stage
  equations. On the retained smooth reduced chart, classical three-stage Gauss
  supplies the local `O(h^7)` truncation term. The FullVA stage-row lift and
  stage-residual perturbation lemmas then consume the accepted 132-row
  implementation bridge: the 96 non-dynamic rows have a row-local
  `O(h^7)` certificate and the 36 Newton--Euler rows are zero on the lifted
  Gauss stage by direct substitution, giving the implemented stage residual
  `O(h^7)` before endpoint closure and inexact Newton are considered.
  Endpoint closure is not read from every raw endpoint diagnostic. The theorem
  uses the same-branch velocity-level/KKT closure subsystem actually corrected
  by the accepted endpoint map; the raw endpoint position defect is a separate
  diagnostic monitor and does not discharge the P2 endpoint raw-defect/right-
  inverse hypothesis. Lemma G and the endpoint-projection audit remain useful
  diagnostics for the older post-step projection path, but the paper theorem's
  endpoint object is the KKT closure functional in
  `main_cmame.tex`, not the projection log. Under the retained P6
  branch-selected solver policy `eta_h^tube <= c_eta h^7`, the inexact Newton
  perturbation also enters at `O(h^7)`, and the local-to-global transfer gives
  global order six for the accepted branch. The generated-block JVP-pruned
  sparse backend preserves the dense Newton map on the tested trajectory
  because the 2637-entry pruned pattern has zero dense-validation misses and
  zero extras. The endpoint-projection audit still measures the old correction
  path on the projected trajectory: raw endpoint velocity residual/correction
  orders are 5.817/5.796 for the smooth branch and 4.089/4.202 for the sharp
  branch over h=[0.04,0.02,0.01] against h=0.005. v047 also embeds the endpoint
  velocity closure as a square KKT residual with endpoint velocity variables,
  least-squares stationarity, and endpoint velocity constraints. This endpoint
  KKT path has smooth position/velocity orders 7.161/7.066, sharp orders
  1.894/2.683, max KKT residuals 6.49e-14 smooth and 5.72e-12 sharp, and
  endpoint velocity residuals below 3.8e-16. The endpoint TFE gap audit records
  finest KKT/projection correction ratios 0.213 smooth and 0.999 sharp, with
  finest raw-to-closed KKT velocity closure gains 1.79e1 and 3.56e3, while
  explicitly marking the stage equations as not yet TFE-weighted. The endpoint
  TFE stage-functional specification audit now records six independent weak/TFE
  row families totaling the 132-row stage budget: translational and rotational
  position defects, translational and angular velocity defects, Newton-Euler
  weak balance, and lower-pair index-3 constraint rows. The implementation
  audit now assembles those rows independently and checks the smooth/sharp
  h-sweep with max equivalence norm 1.755e-17 against the matching
  quadrature-weighted Gauss6 blocks. This is implementation evidence, but it is
  still Gauss6-equivalent rather than a non-equivalent full-TFE residual. The
  TFE stage-replacement design audit records the 132-row stage budget, the
  solved 40-row endpoint extension, the diagonal-equivalent stage weighting,
  the implementation audit, the non-equivalent stage probe audit, the boundary-source audit, the source-budget audit, the dominant-source split audit, the component-activation audit, the component-formula audit, the Newton-Euler formula audit, the all-source formula audit, the all-source trajectory bridge audit, the probe-order audit, the solved
  non-equivalent stage-probe audit, the stage-probe homotopy audit, the
  stage-probe block-activation audit, the stage-probe all-source trajectory bridge audit, the stage-probe coupled-budget audit, the
  stage-probe trajectory-accumulation audit, the stage-probe beta-trajectory
  bridge audit, the v018/v024 Lobatto evidence split, and
  the future acceptance gate for an independent residual. The paper formula
  mapping audit encodes the m=3 Gauss-Lobatto Eq. 43 alpha/beta/gamma
  coefficient map, and the paper derivative-operator audit verifies the
  resulting x-to-y/z map over the 6N+C augmented dimension with max quadratic
  y/z reproduction errors 9.09e-15/6.98e-12; this is the reusable nodal
  derivative operator for a future full-TFE residual. The paper stage-input-map
  audit maps that operator onto all 132 v047 stage rows across six weak row
  families, and the paper multiplier-policy audit specifies lambda_x/lambda_yz
  dimensions 24/48 with no extra lambda_y/z residual rows. The paper
  kinematic-formula audit derives four kinematic row-family formulas across 72
  stage rows with max formula residual 7.26e-18, but does not substitute them
  into the Newton residual. The paper balance/constraint-formula audit derives
  the remaining Newton-Euler weak-balance and lower-pair constraint row-family
  formulas across 60 stage rows with max formula residual 4.34e-19, but does
  not substitute them into the Newton residual. The paper position-substitution
  candidate replaces the two paper position row families inside Newton, covering
  36 stage rows with max residual 5.68e-12 and full rank 132, but its
  smooth/sharp position-velocity orders 1.227/0.731 and 1.165/2.464 are
  order-limited. The paper kinematic-substitution candidate replaces all four
  paper kinematic row families inside Newton, covering 72 stage rows with max
  residual 9.57e-12, full rank 132, max condition 8.81e11, and smooth/sharp
  position-velocity orders 1.406/1.542 and 1.400/1.237; it remains
  diagnostic-z0/order-limited. The paper all-row substitution candidate
  combines all six paper row families in one 132-row Newton residual, with max
  residual 9.64e-12, full rank 132, max condition 1.62e13, and smooth/sharp
  position-velocity orders 1.406/1.542 and 1.400/1.237; it remains
  diagnostic-z0/order-limited and not accepted as full TFE. The paper all-row
  Gauss-z0 diagnostic repeats the six-family/132-row substitution with a
  baseline-Gauss extrapolated start acceleration, giving max residual
  7.70e-12, full rank 132, max condition 1.58e13, max z0 delta 1.69e1, and
  smooth/sharp orders 1.410/1.573 and 1.395/1.170; this shows the low-order
  blocker is not removed by replacing the axis-projected z0 heuristic alone.
  The paper all-row Gauss-z0 terminal-output diagnostic solves the same
  six-family/132-row residual but reads the next state from the terminal paper
  Lobatto node, with max residual 9.20e-12, full rank 132, max condition
  1.58e13, terminal-vs-Gauss output position/velocity deltas 3.19e-03/1.82e-02,
  and smooth/sharp orders 2.494/1.780 and 1.029/0.107; this quantifies
  output-node sensitivity but still does not recover an accepted full TFE
  replacement. The paper all-row recurrent-z0 terminal-output diagnostic keeps
  the same six-family/132-row residual and terminal paper output, but feeds the
  terminal paper z value into the next step after one Gauss bootstrap. It gives
  max residual 9.09e-12, full rank 132, max condition 1.58e13, max
  used-z0-vs-Gauss delta 4.16e-01, and smooth/sharp orders 4.557/4.667 and
  2.579/1.925; this improves the start-policy diagnostic but still does not
  close the order or conditioning caveats. The paper all-row consistent-z0
  terminal-output diagnostic removes that bootstrap by solving the
  instantaneous 20D acceleration/multiplier system, with initial residual
  5.94e-15, rank/condition 20/1.66e1, bootstrap count 0, max all-row residual
  9.79e-12, max condition 1.58e13, and smooth/sharp orders 4.046/4.420 and
  2.554/1.918. This isolates the bootstrap hypothesis but remains diagnostic.
  The paper all-row consistent-z0 conditioning audit records 6 one-step rows,
  max residual 7.03e-12, full rank 132, max raw/equilibrated conditions
  1.58e13/5.07e4, and dominant near-null row/variable families
  `lower_pair_index3_weak_constraints`/`lower_pair_lambda`. This localizes the
  conditioning blocker but does not prove an accepted full-TFE h-sweep.
  The paper all-row consistent-z0 scaled-Newton diagnostic then solves the same
  six-family/132-row residual with iterative row/column equilibration inside
  Newton. It lowers the maximum linear-solve condition diagnostic from
  1.58e13 to 5.13e4, with raw-to-scaled reduction 3.80e8 and scaled-vs-raw
  terminal position/velocity deltas 1.21e-14/2.72e-13, but the smooth/sharp
  orders remain 4.046/4.420 and 2.554/1.918. Thus linear scaling is not enough
  to prove a full TFE replacement.
  The paper family-ablation diagnostic solves 12 one-step rows over two
  five-family variants, keeps full rank 132 with max residual 7.286e-12,
  records max raw/scaled conditions 1.58e13/1.39e5, and localizes the near-null
  family to `lower_pair_index3_weak_constraints`/`lower_pair_lambda` without
  accepting full TFE replacement. The paper lower-pair/lambda Schur diagnostic
  solves 6 one-step rows on the same six-family residual, partitions
  lower-pair rows against lambda columns, finds a zero direct lower-row/lambda
  block and a full-rank reduced Schur block with max condition 5.98e3, and
  adds a Schur-ordered Newton direction check with max linear residual
  1.15e-14 and max relative direction difference 7.79e-09 versus the raw solve,
  showing that linear-solve ordering alone does not close the full-TFE gate.
  It keeps `full_tfe_stage_replacement=false`. The paper lower-pair row-variant
  diagnostic then compares position-, velocity-, and acceleration-level
  lower-pair row formulas over 18 one-step rows inside the same six-family
  residual. All variants solve with full rank 132 and max residual 7.286e-12;
  the acceleration-level lower-pair rows are best conditioned with max Schur
  condition 9.71e1 versus 5.98e3 for the position-level baseline. This is
  formulation evidence that the next full-TFE repair should use or rederive
  acceleration-level lower-pair residual rows before running an accepted
  h-sweep, not proof of full TFE replacement. The paper lower-pair acceleration
  terminal-output h-sweep then promotes that acceleration-level lower-pair row
  choice from one-step diagnostics to 6 smooth/sharp trajectory rows. It solves
  all 6 paper row families and 132 stage rows with max terminal residual
  8.35e-12, full rank 132, max raw/scaled conditions 4.37e8/5.83e3, bootstrap
  count 0, smooth position/velocity orders 4.937/4.799, and sharp
  position/velocity orders 2.555/1.918. This is stronger localized evidence,
  but it still keeps `accepted_h_sweep_present=false` and
  `full_tfe_stage_replacement=false`. The paired paper lower-pair acceleration
  projection-dependence audit compares raw terminal paper output with the
  endpoint-velocity-projected terminal state over the same 6 rows: max
  raw/projected endpoint velocity residuals are 7.99e-06/9.66e-15, max
  projection delta is 7.92e-06, and 6/6 rows require projection. This makes
  the remaining projection-free full-TFE blocker explicit. The paper
  lower-pair acceleration terminal-velocity closure diagnostic then replaces
  only the final lower-pair acceleration rows with 8 weighted raw terminal
  endpoint-velocity rows. It closes raw terminal endpoint velocity to 5.80e-16
  without output projection, with max closure residual 9.73e-12, rank 132,
  raw/scaled max conditions 1.28e10/7.99e4, smooth/sharp position-velocity
  orders 3.459/4.838 and 2.555/1.918, and max replaced terminal lower-pair
  acceleration row 2.53e-4. This is a useful projection-free terminal-velocity
  diagnostic, but it still replaces terminal rows rather than deriving an
  independent full-TFE stage functional, so `full_tfe_stage_replacement=false`.
  The terminal-row homotopy audit then solves 30 one-step rows over
  beta=[0,0.25,0.5,0.75,1], with max residual 6.22e-12, full rank 132,
  raw/scaled max conditions 1.28e10/7.86e4, and beta0/beta1 terminal velocity
  residuals 2.34e-10/1.29e-12. This records a continuous solvable path from
  lower-pair acceleration rows to terminal velocity rows, but remains a
  row-replacement diagnostic rather than a derived full-TFE stage residual.
  The paper lower-pair terminal source-target audit records 6 case/h rows and
  maps the 8 replaced terminal rows to 24 candidate stage-local lower-pair
  source rows over the three paper stages, with max terminal velocity reduction
  3.86e10 and max replaced terminal row norm 2.53e-4. It keeps
  `terminal_row_replacement_present=true` and
  `full_tfe_stage_replacement=false`.
  The paper lower-pair terminal source-lift audit records 6 case/h rows and
  lifts that source into 24 stage-local lower-pair rows using
  `sqrt(h*b_i)*terminal_lower_pair_source`. Its max lift reconstruction error
  is 0.0 and its max lift-ratio deviation is 2.22e-16, but it is still a
  source-formula diagnostic rather than a substituted full-TFE residual.
  The paper lower-pair terminal source-normalization audit records 6 case/h
  rows, shows the raw budget source has max terminal reconstruction relative
  error 9.47e-1, and verifies
  `terminal_lower_pair_source = terminal_row_vector/sqrt(h*b_terminal)` with
  zero normalized reconstruction error. This fixes the source scale needed for
  the next residual-substitution proof but still leaves full-TFE replacement
  pending.
  The follow-up terminal source-insertion audit records 12 sign/case/h rows,
  inserts the normalized source into the lower-pair Newton residual, converges
  all 12 one-step attempts, selects source_sign=-1, and records residuals from
  4.00e-13 to 9.77e-12. It is useful Newton-residual substitution evidence,
  but it still has `accepted_h_sweep_present=false` and
  `full_tfe_stage_replacement=false`.
  The terminal source-insertion trajectory audit runs that best sign over
  h=[0.04,0.02,0.01], completes all 6 smooth/sharp trajectory rows and all 28
  source-ready/source-insertion steps with max source-insertion residual
  9.75e-12, but the h=0.005 reference fails and raw terminal endpoint velocity
  reaches 7.41. It is a quantified failure frontier rather than an accepted
  h-sweep or full-TFE stage replacement.
  The terminal source-insertion blow-up audit records 14 case/metric rows and
  12 blow-up signals, with max mid-to-fine/coarse-to-fine ratios
  7.339e3/4.936e5, minimum observed h-power -9.456, and dominant signal
  `cylindrical_smooth:max_normalized_source_norm`. It proves this
  closure-derived source policy is refinement-unstable, so full-TFE stage
  replacement remains pending.
  The bounded-policy audit records the corresponding bounded-source target,
  rejects the closure-derived source metrics, and shows that simple extra h^2
  scaling is still insufficient for the dominant rows. It keeps
  `accepted_h_sweep_present=false` and `full_tfe_stage_replacement=false`;
  the next proof target is an independent bounded stage-local lower-pair TFE
  source formula.
  The stage-local bounded-source formula audit then separates the one-step
  source scale from the recurrent trajectory policy: all 6 smooth/sharp case/h
  rows keep
  `source_i = sqrt(h*b_i)*(terminal_lower_pair_row/sqrt(h*b_terminal))`
  locally bounded, with minimum local observed h-power 0.426, while the
  recurrent closure-derived source remains unbounded with minimum observed
  h-power -9.456, max recurrent/local source ratio 1.003e6, and max raw
  terminal velocity 7.41. This is a proof-localization result, not a full-TFE
  acceptance result.
  The paper
  residual-substitution contract
  audit maps six row-family targets with 6 formulas, 6 substituted rows, 0
  accepted h-sweep rows, and `full_tfe_stage_replacement=false`. The endpoint TFE
  stage-probe boundary-source audit records 36 block/h rows and reconstructs
  every evaluated probe block from endpoint-boundary source seeds lifted by
  sqrt(h*b_i), with max lift error 0.000e+00 and max lift-ratio deviation
  2.220e-16. This verifies the current probe source without claiming the
  derived full-TFE weak residual. The endpoint TFE
  stage-probe source-budget audit compresses those rows into 6 case/h budgets,
  verifies the aggregate lifted L2 ratio to 3.331e-16, and identifies
  `newton_euler_weak_balance` as the dominant source family in both smooth and
  sharp cases without claiming a derived full-TFE residual. The dominant-source
  split audit records 24 component/h rows, verifies the componentwise lift to
  2.220e-16, and identifies body0 translational balance as the next weak-row target.
  The component-activation audit then solves that body0 translational target as
  6 isolated component rows with max residual 1.195e-15, max activated probe norm
  2.006e-11, and max lift-ratio deviation 2.220e-16 while still not claiming a
  derived weak-balance row formula. The component-formula audit then inserts the same target as `sqrt(h*b_i)*m0*delta_v0`, solves 6 direct formula rows with max residual 1.258e-15, zero formula/generic component difference, and max lift-ratio deviation 2.220e-16 while still not claiming a full-TFE stage functional. The Newton-Euler formula audit then inserts the full 12D weak-balance source block as `sqrt(h*b_i)*concat_i[m_i*delta_v_i, J_i*delta_w_i]`, solves 6 direct block-formula rows with max residual 1.265e-15, zero formula/generic block difference, and max lift-ratio deviation 3.331e-16 while still not claiming all stage row families. The all-source formula audit covers all six endpoint-boundary source families as direct formulas, solves 6 direct 132-row formula rows with max residual 4.029e-15, zero formula/generic stage-major and block differences, and max lift-ratio deviation 3.331e-16 while still not claiming a derived full-TFE stage functional. The all-source trajectory bridge audit solves 6 complete trajectory rows over h=[0.04,0.02,0.01] against same-formula h=0.005 references with max residual 2.192e-12, max formula probe 8.383e-11, and max position/velocity reference errors 9.45e-06/2.36e-03 while still using endpoint-boundary source formulas. The endpoint TFE
  stage-local source-removal target audit maps the 36 verified endpoint-boundary
  source rows onto six concrete stage-local weak-row replacement targets,
  records `newton_euler_weak_balance` as the dominant source family, and keeps
  `endpoint_boundary_source_removed=false` and
  `full_tfe_stage_replacement=false`. The endpoint TFE
  stage-probe trajectory-accumulation audit records max solved/beta1 ratio
  1.292e+02 and max per-step ratio 1.615e+01, quantifying trajectory-level
  accumulation without claiming a full-TFE replacement. The stage-probe
  beta-trajectory bridge audit solves 18 trajectory rows over beta=[0,0.5,1]
  and h=[0.04,0.02,0.01] against same-beta h=0.005 references, with max
  residual 2.192e-12 and max probe norm 8.383e-11 while still leaving the
  derived full-TFE weak residual missing. The paper lower-pair direct
  endpoint-velocity source audit replaces the rejected recurrent
  terminal-closure source generator with the raw endpoint velocity residual
  `C_v` evaluated at the paper acceleration predictor's raw terminal Lobatto
  node, then inserts `sqrt(h*b_i)*C_v` into each lower-pair stage block. Its
  6 smooth/sharp trajectory rows over h=[0.04,0.02,0.01] against h=0.005 give
  minimum position/velocity orders 2.555/1.918, minimum
  direct-source/terminal-velocity h-powers 0.307/0.286, max direct source
  8.118e-6, and max post-insertion terminal velocity 7.969e-6, with
  terminal-closure source use and terminal-row replacement source use both
  false. It is bounded recurrence evidence, not a completed proof, because the
  source remains endpoint-boundary-derived and `full_tfe_stage_replacement`
  remains false. The paper lower-pair direct-source residual-substitution audit
  evaluates the raw paper acceleration lower-pair rows at the source-inserted
  solution and verifies `raw_lower_pair + sqrt(h*b_i)*C_v = 0` over 6
  smooth/sharp trajectory rows. Max balance and inserted lower-pair residuals
  are 1.821e-13, all 28 source-residual-substituted steps are clean, and the
  h-sweep retains minimum position/velocity orders 2.555/1.918. It is still
  partial because the source remains endpoint-boundary-derived and
  `full_tfe_stage_replacement=false`. The residual-derived stage-source audit
  then reconstructs `C_hat_i=-R_i/(source_sign*sqrt(h*b_i))` from each raw
  lower-pair stage row. It records 6 trajectory rows, max derived-vs-direct
  source gap 1.289e-12, max stage-consistency gap 1.406e-14, max mean
  reconstruction error 1.482e-15, zero derived balance error, all 28
  residual-derived source-consistency steps clean, and the same 2.555/1.918
  minimum position/velocity orders. It is still partial because the trajectory
  still uses the direct endpoint source; endpoint-boundary source removal and
  full TFE stage replacement remain false. The self-consistent endpoint-source
  audit computes `C_v(x_terminal)` inside the lower-pair Newton residual rather
  than passing an external source. It records 6 trajectory rows, max
  self-consistent residual/balance/source 9.441e-12/1.821e-13/7.974e-06,
  smooth/sharp orders 5.333/6.790 and 2.555/1.918, and all source steps clean,
  while keeping the source endpoint-boundary-derived and
  `full_tfe_stage_replacement=false`. The paper lower-pair source-free
  elimination rank audit records 6 trajectory rows, reconstructs
  stage-consistent `C_hat_i` with max consistency gap 1.406e-14, and proves
  that the source-free centering/elimination map has rank 16 for 24 lower-pair
  stage rows. The rank defect is 8, matching the missing mean-source closure
  rows, so a source-free full-TFE residual still needs 8 independent lower-pair
  mean-source closure rows derived from the paper stage functional. The
  follow-up source-free mean-velocity closure candidate fills that budget with
  16 centered acceleration source-consistency rows plus 8 paper-stage
  mean-velocity rows, solves 6 smooth/sharp h-sweep rows with max residual
  8.13e-12 and no endpoint source, terminal-row replacement, or projection,
  but remains order-limited with smooth/sharp orders 3.512/4.448 and
  2.555/1.918 and `full_tfe_stage_replacement=false`.
  The source-free mean-blend closure audit sweeps 7 alpha values over 42
  one-step rows, keeps endpoint source, terminal-row replacement, and
  projection removed, and finds best alpha 0 with max residual/raw terminal
  velocity 5.489e-12/2.337e-10. It remains partial because terminal velocity
  is still above 1e-10 and no accepted trajectory h-sweep is present.
  The source-free mean-blend trajectory audit promotes that best alpha to 6
  trajectory rows, solves cleanly with max residual/raw terminal velocity
  9.453e-12/8.234e-06, and records smooth/sharp orders 5.317/6.782 and
  2.555/1.918. This proves the one-step near-closure does not survive the
  trajectory terminal-velocity gate, so `full_tfe_stage_replacement=false`.
  The source-free mean-blend trajectory alpha sweep tests all 7 alpha values
  over 42 trajectory rows, identifies alpha 0.75 as the best terminal-velocity
  trajectory choice, and records max residual/raw terminal velocity
  8.779e-12/7.447e-06 with minimum position/velocity orders 2.555/1.918.
  This rules out simple alpha tuning as the full-TFE repair and keeps terminal
  velocity open and full=false.
  The source-free component-blend trajectory audit tests an 8-component alpha
  vector from a one-step h=0.02 screen and records max residual/raw terminal
  velocity 9.971e-12/7.458e-06, minimum orders 2.555/1.918, and a 1.001
  terminal-velocity ratio versus the scalar alpha baseline. This rules out
  per-component alpha tuning as the missing mean-source closure and keeps
  `full_tfe_stage_replacement=false`.
  The source-free terminal-velocity extrapolation trajectory audit plus a source-free terminal-extrapolation blend trajectory audit replaces the
  8 mean-closure rows with terminal-node Lagrange extrapolated Gauss-stage
  velocity-constraint rows. It records 6 rows, max residual/raw terminal
  velocity 9.91e-12/1.18e-05, smooth/sharp orders 3.518/4.748 and 2.554/1.917,
  and worst/smooth terminal-velocity ratios versus component-blend 1.585/0.147.
  This is a real source-free basis-change diagnostic, but it worsens the
  worst-case sharp coarse terminal velocity and keeps
  `full_tfe_stage_replacement=false`.
  The centered terminal-velocity bridge audit tests 16 centered acceleration
  source-consistency rows plus 8 terminal-velocity bridge rows over
  gamma=[0,0.5,1]. Gamma 0 closes terminal velocity to 4.01e-16 with max
  residual 9.75e-12, but it keeps a terminal-boundary row, leaves
  `endpoint_boundary_source_removed=false`, and loses the smooth-order gate
  with smooth orders 3.523/4.828. This proves terminal closure is algebraically
  reachable, but not yet by an independent stage-local source-free paper TFE
  row formula.
  A lower-pair closure acceptance matrix compares 14 closure families, accepts
  0 candidates, identifies `source_free_mean_blend_trajectory_best_alpha` as the
  best source-free/order-preserving row set and
  `centered_terminal_velocity_bridge` or
  `source_free_final_stage_velocity_closure` as terminal-velocity row sets, so
  the source-free/order and accepted terminal-closure properties remain split.
  The closure property Pareto audit groups the same 14 candidates into 5
  property-intersection rows and confirms the split quantitatively: 9
  candidates are source-free/no-replacement, 5 are order-preserving
  source-free, 3 are terminal-velocity closed, and the accepted intersection is
  empty. This localizes the missing full-TFE row formula but does not close the
  proof gate.
  The closure row-span audit tests that localization at the tangent level:
  the 40-row source-free basis has rank 40, the 8 terminal-bridge target rows
  raise the augmented rank to 48 across all 6 case/h samples, max projection
  relative residual is 2.814e-01, and row-span reproduced count is 0. The
  missing-direction complement has rank 8, is orthogonal to the tested basis
  to 8.75e-16 relative, and reconstructs the terminal-bridge target with max
  reprojection residual 9.25e-14, but it is still a
  terminal-boundary-derived tangent diagnostic. Its column-energy structure is
  velocity-level: angular velocity is dominant in all 6 rows with max fraction
  0.506, translation velocity reaches 0.496, lower-pair lambda is 0, and
  translation acceleration stays below 5.60e-05. This rules out a proof
  strategy based only on reweighting the existing source-free
  mean/velocity/extrapolation rows; the next proof target is a stage-local
  source-free velocity-level formula for the eight missing lower-pair tangent
  directions.
  The follow-up velocity-basis span audit tests 7 weighted eight-row
  stage-velocity closure families plus the 24-row all-stage velocity upper
  bound against the same 8 terminal-bridge target rows. The all-stage velocity
  rows span the target at max relative residual 2.78e-15, but the best weighted
  eight-row candidate, `endpoint_lagrange_velocity_closure`, still has relative
  residual 4.20e-01 and no weighted candidate spans. The proof target is now an
  eight-row source-free compression of that all-stage lower-pair velocity row
  space, followed by a nonlinear trajectory h-sweep.
  The velocity-compression audit resolves the fixed-compression proof subgoal
  in the local tangent space: all three fixed compressions span all 6 case/h
  samples, the best fixed candidate is `optimized_global_stage_scalar` with
  weights numerically `[0,0,1]`, and the best fixed relative residual is
  1.04e-15. The strengthened selector-degeneracy check shows this local span is
  not an independent fixed compression: the universal full 8x24 fit has
  selector-relative distance 1.53e-15 from the final-stage selector, and the
  largest non-final-stage energy fraction is 1.71e-15. The non-degenerate
  follow-up sweeps 192 fixed stage-0/stage-1 injection rows; 84 rows have
  meaningful non-final-stage energy, but none spans locally and the best
  meaningful projection residual is 1.59e-03. The state-local diagonal
  direction oracle then sweeps 72 rows over 65 direction samples; 36 rows have
  meaningful non-final-stage energy, but none spans locally and the best
  meaningful projection residual is 9.90e-03. The non-final full
  component-mixing probe tests 36 stage-0/stage-1/stage-0+1 full-mixing rows;
  0 span locally and the best tangent residual is 9.81e-01. The value-level
  source-free probe tests 72 case/h/candidate rows; all 72 balance row values,
  18 are value-balanced local tangent spans, but 0 meaningful non-final
  value-balanced rows span. The successful spans are final-stage-selector-like
  with max spanning non-final-stage energy fraction 2.12e-15. The proof
  obligation is therefore narrowed to deriving a derivative-aware
  value-level source-free compression. The local derivative-aware oracle now
  shows 36 meaningful non-final value-balanced tangent spans after a
  coefficient-gradient correction; full TFE is still unproved until that
  correction is replaced by a bounded analytic formula and succeeds on a
  nonlinear trajectory h-sweep. The bounded-gradient cap sweep then tests 288
  cap/candidate/case/h rows: all 288 keep value balance and meaningful
  non-final energy, 92 span at the tested caps, practical cap 1e12 spans 12
  rows, and all 36 local spans require cap 1e18. This keeps the proof
  obligation on a bounded analytic coefficient-gradient law rather than an
  unbounded local oracle.
  The later target-free active-stage-velocity matrix audit narrows the same
  proof boundary further: the expanded 20-row grid reaches best projection
  residual 0.576548 with `stage2_velocity_shifted_column_broadcast_feature`,
  but independent target rank remains 8 and no row spans the terminal bridge.
  This is localization evidence for the missing stage-2 velocity tangent, not a
  replacement for the required analytical weak-row formula.
  A two-row best-law missing-direction decomposition keeps the residual
  0.576548 and rank-eight gap, but localizes 96.3% of the missing tangent
  energy to stage 2 with dominant variable family `angular_velocity_w`
  (fraction 0.502991). This narrows the proof obligation to a stage-2
  angular-velocity coupling in the weak-row formula.
  A follow-up angular-only mask grid tests that narrow hypothesis directly.
  It runs 8 local rows in 35.3 seconds; the best law
  `stage2_angular_velocity_shifted_column_broadcast_feature` reaches only
  residual 0.752997 with independent target rank 8 and no span, and the
  remaining direction becomes `translation_velocity_v` dominated. Thus a
  coupled translation/angular stage-2 weak row is required; angular masking
  alone is not the formula.
  A direct translation/angular cross-coupling follow-up tests 8 target-free
  outer-cross matrix rows in 35.3 seconds; its best law
  `stage2_velocity_angular_to_translation_cross_feature` reaches only residual
  0.898812 with independent target rank 8 and no terminal-bridge span. The
  remaining tangent is still `translation_velocity_v` dominated at fraction
  0.556004 and has stage-2 fraction 0.999994, so the tested simple
  translation/angular outer-cross coefficient-gradient rows are not the
  required analytical weak-row formula.
  A target-free endpoint-pose generalized-velocity predictor follow-up tests
  10 rows in 31.2 seconds; its best law
  `paper_endpoint_pose_positive_lagrange_z` reaches residual 0.117782 with
  independent target rank 8 and no terminal-bridge span. The remaining tangent
  is `translation_velocity_v` dominated at fraction 0.514237 with stage
  fractions 0.961546/0.004167/0.034287, so this predictor substantially
  improves localization but still does not prove the required full-TFE row.
  A near-terminal stage-0/stage-2 convex predictor screen then separates
  degenerate and nondegenerate behavior. The stage-2-only law
  `paper_endpoint_pose_stage02_convex_0p00_z` spans locally at roundoff, but it
  is terminal-bridge equivalent and already known to be order-limited in the
  nonlinear terminal-bridge h-sweep. The best nonterminal law
  `paper_endpoint_pose_stage02_convex_0p05_z` reaches residual 0.049317 with
  rank 8 and no nonterminal span. Focused h-scaling reruns at h=0.02 and
  h=0.01 keep that nonterminal residual at 0.051890 and 0.052472, so this is
  a persistent nonterminal weak-row gap rather than a coarse-step artifact.
  A synchronized pose/velocity near-terminal row improves the local residual
  to 0.009512 with `stage02_convex_pose_velocity_0p01_z`, but h=0.02/h=0.01
  remain at 0.009978/0.010085 with rank 8 and no span. The larger 0p02/0p05/0p10
  offsets give 0.019205/0.049390/0.103464, confirming a near-terminal
  asymptote rather than an independent row.
  A terminal-limit extrapolation from the 0p01/0p02 synchronized rows reaches
  4.699e-06/2.335e-06/1.168e-06 over h=0.04/0.02/0.01, but it is explicitly
  marked terminal-bridge-equivalent and still has no span, so it does not close
  the independent full-TFE gate. Direct signed mean-acceleration bridge
  corrections worsen the best residual to 0.076159 or above and move the
  missing direction to `lie_position_u`, so the remaining correction is not
  the existing centered bridge acceleration term.
  A bilinear active-velocity outer-product follow-up tests 24 target-free
  feature/stage-2-velocity matrix rows in 57.3 seconds; its best law
  `stage2_velocity_feature_outer_stage2_velocity` reaches only residual
  0.898720 with independent target rank 8 and no terminal-bridge span. This
  excludes the tested simple component-pair matrix coupling family and keeps
  the proof obligation on a different analytical weak-row formula.
  A componentwise active-velocity diagonal follow-up tests another 24
  Hadamard/shifted-diagonal rows in 56.7 seconds; its best law
  `stage2_velocity_diagonal_plus_hadamard_row_feature_stage2_velocity` reaches
  only residual 0.898530 with independent target rank 8 and no span. This also
  excludes the tested row-local componentwise matrix coupling family.
  Nonterminal acceleration-correction follow-ups then test whether the best
  synchronized row is missing only a simple Taylor term. Direct signed
  mean-acceleration closure corrections and generalized-velocity shifts
  `z_alpha + gamma*h*zdot_alpha` each cover 18 local rows over the 0p01/0p02
  synchronized predictors; both keep nonterminal span count 0, leave the
  uncorrected `stage02_convex_pose_velocity_0p01_z` as the best row at
  residual 0.009512, and have best corrected residual 0.012376 with unit
  corrections no better than 0.077874. Thus simple nonterminal acceleration
  corrections are not the missing full-TFE weak row.
  A kinematic pose-slope predictor follow-up then uses the stage-0/stage-2
  pose slope `(q2-q0)/(h*(c2-c0))` as a velocity estimate for the same
  synchronized rows. It covers 26 local rows, keeps nonterminal span count 0,
  and again leaves `stage02_convex_pose_velocity_0p01_z` best at 0.009512; the
  best pose-slope row `stage02_convex_pose_velocity_0p02_poseslope_m0p1_z`
  reaches only 0.878519 and leaves a stage-2 dominated translation-velocity
  direction. Thus the missing weak row is not the simple stage-pose-slope
  kinematic velocity predictor.
  A source-to-velocity lift follow-up then maps mean-acceleration, source0,
  source2, curvature, and history-delta lower-pair source rows through the
  current-pose endpoint velocity matrix `C_v` into minimum-norm generalized
  velocity shifts. The 34-row audit runs in 76.4 seconds, keeps nonterminal
  span count 0, leaves `stage02_convex_pose_velocity_0p01_z` best at residual
  0.009512, and ties
  `stage02_convex_pose_velocity_0p01_sourcelift_historydelta_p1_z` with
  `stage02_convex_pose_velocity_0p01_sourcelift_source0_p1_z` as best
  corrected rows at 0.609803. Thus the direct current-pose `C_v`
  source-to-velocity lift is also not the missing independent full-TFE weak
  row.
  A matrix-difference source-to-velocity lift then maps the same source rows
  through stage-0 and stage-2 `C_v` matrices and inserts the difference of the
  two minimum-norm generalized-velocity shifts. The first 14-row targeted
  screen runs in 58.7 seconds, keeps nonterminal span count 0, and reaches
  coarse-scale residual 0.042593. A refined 26-row scale sweep runs in
  92.5 seconds over 0.1, 1, and 10 gains; it again leaves
  `stage02_convex_pose_velocity_0p01_z` best at 0.009512, with best corrected
  row
  `stage02_convex_pose_velocity_0p01_sourceliftmatrixdiff_historydelta_p0p1_z`
  at residual 0.009527 and no span. Thus the direct stage-0/stage-2 `C_v`
  coefficient-difference lift is also excluded, not just an overly large-gain
  variant.
  A normalized-history source-law follow-up then replaces `source0-history` by
  its direction scaled by `||source0||` before the same matrix-difference lift.
  This 10-row screen runs in 49.4 seconds, keeps nonterminal span count 0,
  leaves `stage02_convex_pose_velocity_0p01_z` best at 0.009512, and has best
  corrected row
  `stage02_convex_pose_velocity_0p01_sourceliftmatrixdiff_historyunitdelta_p0p1_z`
  at residual 0.009590. Thus this simple nonlinear recurrent-history source
  direction is also excluded.
  The nonlinear source-free final-stage velocity closure inserts those rows as
  16 centered acceleration source-consistency rows plus 8 final paper-stage
  velocity rows. It solves 6 smooth/sharp trajectory rows with max residual
  9.49e-12 and raw terminal endpoint velocity 4.01e-16, without endpoint
  source, terminal-row replacement, or projection. Smooth/sharp orders are
  3.523/4.828 and 2.555/1.918, so the terminal-velocity proof subgoal is
  closed but smooth position order still keeps
  `full_tfe_stage_replacement=false`.
  The source-free order/closure blend trajectory audit checks whether a
  convex blend between the order-preserving mean-acceleration closure and the
  terminal-closing final-stage velocity closure can satisfy both gates. Over 18
  beta=[0,0.5,1] rows, beta 1 closes terminal velocity to 4.01e-16 but keeps
  the smooth position order at 3.523, while beta 0 and 0.5 keep smooth position
  order above 5 but leave terminal velocity around 4e-6. Thus the intersection
  of source-free, order-preserving, and terminal-velocity-closed properties is
  still empty, and `full_tfe_stage_replacement=false`.
  The nonlinear-history recurrent source-law screen then tests five target-free
  norm, Hadamard, bilinear, and second-difference history laws. All rows
  converge at rank 132 with no endpoint source, target Jacobian, terminal-row
  replacement, or projection, but no row closes terminal velocity or preserves
  the smooth-order floor. The best law is
  `recurrent_nonlinearhistory_velocity_terminal_source0historyhadamard_z` with
  terminal velocity 1.954e-07 and min order 3.525, so this source-law family is
  negative evidence and `full_tfe_stage_replacement=false` remains.
  The endpoint TFE
  readiness audit records 31 satisfied,
  38 partial, and 1 missing check: endpoint-node weighted residual rows, a
  solved endpoint-node h-sweep, the design audit, the stage-functional
  specification, the implementation audit, the non-equivalent probe audit, the
  boundary-source audit, the source-budget audit, the dominant-source split audit, the component-activation audit, the component-formula audit, the Newton-Euler formula audit, the all-source formula audit, the all-source trajectory bridge audit, the probe-order audit, the solved non-equivalent stage-probe audit, the stage-probe homotopy audit, the
  stage-probe block-activation audit, the stage-probe all-source trajectory bridge audit, the stage-probe coupled-budget audit, the
  stage-probe trajectory-accumulation audit, the stage-probe beta-trajectory
  bridge audit, the paper all-row consistent-z0 conditioning audit, the
  paper lower-pair/lambda Schur audit, the paper lower-pair row-variant audit,
  the paper lower-pair acceleration terminal-output h-sweep audit,
  the paper lower-pair terminal source-insertion trajectory audit,
  the paper lower-pair self-consistent endpoint-source audit,
  the paper lower-pair source-free elimination rank audit,
  the paper lower-pair source-free mean-velocity closure audit,
  the paper lower-pair source-free final-stage velocity closure audit,
  the paper lower-pair source-free terminal-velocity extrapolation audit,
  the paper lower-pair source-free terminal-extrapolation blend trajectory audit,
  the paper lower-pair closure acceptance matrix audit,
  and a diagonal-equivalent
  stage-weighted h-sweep are now present, while the independent full TFE stage
  replacement remains missing.
  The candidate h-sweep
  evaluates endpoint-node weighted rows on the KKT trajectory; max candidate
  weighted residuals are 1.177e-12 smooth and 5.723e-13 sharp. The solved
  endpoint-node candidate h-sweep solves those rows in a square Newton residual
  with max solved residuals 6.643e-14 smooth and 5.723e-12 sharp, but the
  stage equations remain non-TFE-weighted. The stage-weighted candidate
  premultiplies each Gauss6 FullVA stage block by sqrt(h*b_i), giving max
  weighted residuals 6.819e-15 smooth and 3.017e-13 sharp while preserving the
  unweighted residual check at 6.450e-14 smooth and 5.724e-12 sharp; it is a
  TFE row-weighting equivalence check rather than a full TFE stage replacement.
- Sparse-backend status: row-colored VJP now assembles the same 2637-entry
  pruned pattern with 60 row colors rather than 90 column colors. The row-VJP
  trajectory agrees with dense to roundoff. A five-repeat warmed benchmark
  records median row/column runtimes 1.008x for smooth and 0.990x for
  sharp, while dense `jacfwd` remains faster with dense/row 0.873x and 0.819x.
  The sparse speed gap audit records row-VJP speedups needed 1.145x smooth and
  1.220x sharp to match dense. The sparse cost-model audit records that
  row-VJP runtime must drop by 12.7% smooth and 18.1% sharp to match dense, or
  by 21.4% smooth and 26.3% sharp for a 10% dense win, with dense-equivalent
  row colors 52.4 smooth and 49.2 sharp. This reduces the color-count
  bottleneck but keeps reverse-mode/JAX overhead or missing component/block
  assembly as the remaining sparse-speed issue.
- Sharp-friction status: a Brown-McPhee smoothness sweep on the same
  cylindrical chain gives position/velocity orders 7.161/7.066, 6.494/5.657,
  3.392/4.511, and 1.894/2.683 for stribeck velocities 0.50, 0.20, 0.10, and
  0.05. This confirms the order loss is tied to the smooth-to-sharp load
  transition rather than a failed smooth-regime Gauss6 construction, but it
  does not close the sharp-friction caveat. A projected dense Gauss6
  step-doubling diagnostic on the vs=0.05 sharp case reduces velocity error
  from 5.70e-05 at fixed h=0.01 to 3.81e-07 at 3.2x runtime, with error/runtime
  value ratio 0.002 against fixed h=0.01. This supports an adaptive-policy path
  for high-accuracy sharp friction, but it is still diagnostic rather than a
  restored-order proof. The adaptive tolerance/work fit gives velocity slopes
  0.881 over all tolerances and 1.710 over the two looser tolerances; the
  finest-pair tail changes tolerance by 0.200 but velocity error only by 0.920,
  so the new diagnostic flags a reference floor instead of claiming restored
  sharp-friction order. A fixed-refinement audit over h=0.02/0.01/0.005 against
  h=0.0025 gives all-point position/velocity orders 3.294/5.867 and tail
  orders 5.364/8.437. This shows partial tail recovery for velocity but keeps
  the sharp-friction proof caveat open because the all-point position order is
  still low and the finest position tail remains slightly below the high-order
  target. A deeper fixed-refinement audit over h=0.01/0.005/0.0025 against
  h=0.00125 gives all-point position/velocity orders 6.398/5.870 and tail
  orders 7.423/3.177. The position branch is high order at the deeper scale,
  but the velocity tail remains reduced. The ultra audit over
  h=0.005/0.0025/0.00125 against h=0.000625 recovers all-point
  position/velocity orders 7.521/5.725 and tail orders 7.626/8.279. The sharp
  refinement cost-envelope audit then quantifies the work: reaching the
  h=0.00125 high-order window from h=0.01 costs 7.76x runtime, 8.0x steps, and
  8.0x Newton iterations while reducing velocity error by 1.06e6x. This is
  evidence for asymptotic recovery but keeps the practical coarse-regime
  sharp-friction caveat open rather than closing it.
- Validation hygiene: `validate_v047_outputs.py` is a read-only gate that now
  covers the 292 generated result files, 147 CSV tables, 120 PNG plots, summary gate status, stale wording, and README/report artifact lists.
- Latest h-adaptive endpoint-pose velocity response audit: four h-scaled
  predictor laws are reduced to response rows. Only the hpow_m1 law closes
  terminal velocity, no row satisfies the smooth-order floor, and
  `order_terminal_intersection_present=false`, so terminal closure still
  requires order collapse rather than closing the full-TFE replacement gap.
- Latest lower-pair candidate frontier audit: 11 candidate families and 115 rows
  are aggregated into
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_candidate_frontier_audit`,
  giving 35 terminal-closed rows, 17 smooth-order rows, and
  `order_terminal_intersection_count=0`; the remaining target is a bounded
  target-free stage-local weak-row tangent.
- Latest bounded tangent requirement audit:
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_bounded_tangent_requirement_audit`
  records `requirement_row_count=7`, `row_space_oracle_span_count=36`,
  `target_free_formula_span_count=0`, and
  `bounded_gradient_practical_cap_spanning_row_count=12`; it is a gap
  localization artifact, not a full-TFE replacement proof.
- Latest recurrent stage2 feature-dictionary span audit:
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_feature_dictionary_span_audit`
  records `feature_dictionary_row_count=12`, `span_row_count=8`,
  `combined_all_dictionary_span_count=2`, best dictionary `stage2_matrix_core`,
  and residual `1.084e-14`, but no bounded coefficient/selection law or
  accepted nonlinear h-sweep; it is a target-free local capacity result, not a
  full-TFE replacement proof.
- Latest recurrent stage2 frozen coefficient-law screen:
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_feature_coefficient_law_screen_audit`
  records `coefficient_law_row_count=60`, `span_count=0`, best law
  `closure_delta_norm_weights`, residual `5.596e-01`,
  `coefficient_derivative_included=false`, and
  `target_jacobian_used_for_formula=false`; it preserves the missing
  state-dependent bounded coefficient-law target and is not a full-TFE
  replacement proof.
- Latest recurrent stage2 state-feature coefficient-derivative screen:
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_state_feature_coefficient_derivative_screen_audit`
  records `state_feature_coefficient_derivative_row_count=36`, `span_count=0`,
  best dictionary `stage2_matrix_core`, best law
  `inverse_closure_delta_norm_weights_derivative`, residual `5.908e-01`,
  `coefficient_derivative_included=true`, and
  `target_jacobian_used_for_formula=false`; it excludes the tested direct
  closure-norm coefficient derivative laws while keeping the full-TFE
  replacement proof open.
- Caveat: the current v047 paper proof is closed only for the direct-route
  conditional Gauss6/FullVA theorem stated above, not for a broader
  source-policy, primitive/Taylor, P6 solver-policy-discharge, P7
  residual-to-error, or full-TFE replacement claim. Sparse AD is still slower
  than dense `jacfwd`, endpoint closure has an endpoint KKT residual but not a
  fully TFE-style treatment, and sharp-friction convergence is still
  order-reduced. The smooth h-sweep is high order only after projecting the
  initial velocity state onto the cylindrical velocity constraints. The v046
  ASME baseline has been ingested as a gate table. v047 now has an exact
  single-pendulum driven-kinematic mapping for the ASME fixed-pivot, revolute
  DP1 rows, and DP1 drive, with measured Gauss6 order about six against the
  analytic theta(t). It now also solves a full absolute-coordinate driven
  single-pendulum FullVA residual with stage right-Lie orientation increments,
  COM position/velocity/acceleration, angular velocity/acceleration, pivot
  reactions, axis multipliers, and drive multiplier in one Newton residual.
  That absolute-coordinate residual shows about sixth order in position,
  velocity, orientation, and omega, with residuals below 4e-12. The embedded
  scalar FullVA bridge remains as a reduced-coordinate cross-check, and
  Newton-Euler reaction multipliers are reconstructed on the exact driven
  trajectory with roundoff dynamics residuals as an analytic cross-check. v047
  also keeps a partial free-revolute method-side mapping with ASME
  geometry/mass/inertia and high observed self-reference order. The double-pendulum
  method-side FullVA mapping now uses ASME lengths/masses/inertias and the
  two-revolute topology in v029 and shows sixth-order self-reference behavior.
  A direct v029-v046 rA trajectory diagnostic has been added, but the error is
  nearly h-independent against the v046 h=0.001 reference. Refining the v046
  reference to h=0.0005 halves the v029-v046 position/velocity differences,
  which points to a first-order rA reference floor rather than v029
  self-convergence failure. The v047 policy now accepts the nested local
  v029/FullVA h=0.005 self-reference for double-pendulum validation and keeps
  v046 rA as a reproducibility baseline plus floor diagnostic. The new
  four-example lower-pair constraint-graph bridge evaluates the ASME JSON
  DP1/CD/DP2/D rows at position, velocity, and acceleration levels for
  h=[0.02,0.01,0.005]. It records 18-row four_link and slider_crank graph
  mappings and residual/convergence diagnostics. A new four-example `Phi_q`
  SVD audit samples the same ASME dynamics h-sweep and finds full row rank for
  all graphs: min singular values are 3.04e-1 for single_pendulum, 2.03e-1 for
  double_pendulum, 7.89e-2 for four_link, and 7.25e-2 for slider_crank, with
  max condition numbers 7.94, 15.7, 117, and 43.7. This supports the regularity
  assumption needed by a square local FullVA Newton solve. v047 now uses that
  regularity evidence in a local closed-loop kinematic FullVA solve for the
  fully constrained driven four_link and slider_crank examples: at each output
  time it solves Phi=0 by Newton with SO(3) projection, then solves
  Phi_q qdot=nu and Phi_q qdd=gamma. Over h=[0.02,0.01,0.005], the accepted
  four_link rows have max Phi/velocity/acceleration residuals about
  6.7e-15/3.0e-15/1.1e-14, and slider_crank has about
  9.0e-16/4.8e-16/1.2e-15. These are local kinematic FullVA closed-loop rows
  for the driven examples. v047 also reconstructs the reaction multipliers from
  those accepted states by solving
  `Phi_q.T lambda = [F - M a; -(J alpha + omega x J omega)]` and checks the
  translational/rotational Newton-Euler rows. The max full dynamics residuals
  are 1.34e-13 for four_link and 6.49e-15 for slider_crank. Thus the four ASME
  method rows are now accepted under the current mechanism-coverage gate, while
  the order-acceptance gate keeps four_link/slider_crank external dynamic
  order open; the endpoint projection
  correction is now directly audited and is also represented as a square
  endpoint KKT residual closure, but the remaining proof caveats are still not
  missing ASME examples: they are full TFE stage replacement, slower
  sparse backend, and practical coarse-regime sharp-friction order/cost.

  The paper theorem and proof contract also keep the residual-to-error route
  out of the accepted order claim. No residual error theorem is accepted in the
  current manuscript: `accepted_residual_to_error_theorem=false`.
  Seven residual-to-error obligations remain blocking, and the residual rows
  for `four_link` and `slider_crank` are mechanism-coverage evidence; they are
  not accepted dynamic order rows. This boundary is now mirrored in the CMAME
  theorem text, the flat submission source/PDF text, and the proof-contract
  validators.

  The latest bounded-formula velocity-compression audit adds 648 local
  law/cap/candidate/case/h rows over global tanh, rowwise tanh, and rowwise
  rational-quadratic saturation laws. All 648 rows keep value balance and
  meaningful non-final energy, 366 span at the tested caps, and all local spans
  require cap 1e22 for every tested law. Because the correction direction is
  still a target-direction oracle and no nonlinear h-sweep is accepted, this is
  not an independent full TFE stage replacement.

  The target-direction-free follow-up adds 2592 local
  law/cap/candidate/case/h rows over 12 source-derived, stage-extrapolated,
  and all-active component direction laws. All
  rows keep value balance and meaningful non-final energy, but 0 rows span the
  local terminal-bridge tangent and the best residual is 9.82e-01. The
  direction-capacity follow-up adds 216 candidate/feature/case/h rows: all-stage
  velocity feature spaces span 72 rows at roundoff, but non-final active/source
  feature spaces span 0 rows, with best non-final residual 9.81e-01 and best
  non-final correction residual 9.998e-01. The nonlinear second-differential
  capacity follow-up adds 216 rows across six finite-difference source-feature
  families; all six families have 0 spans, with best projection/correction
  residuals 6.95e-01/7.01e-01. The higher-order/nonlocal capacity follow-up
  adds another 216 rows over third-differential source features and same-case
  cross-step source deltas; all six families again have 0 spans, with the same
  best projection/correction residuals. The one-step history-transport
  capacity follow-up adds another 216 rows over transported source-row and
  non-final velocity-row deltas; all six families again have 0 spans, with
  best projection/correction residuals 7.13e-01/7.12e-01. The two-step
  history-transport capacity follow-up adds another 216 rows over two future
  transported source/velocity deltas; all six families again have 0 spans,
  with best projection/correction residuals 6.95e-01/7.01e-01. The recurrent
  history-capacity follow-up adds another 216 rows over two-step curvature and
  bilinear source/velocity history features; all six families again have
  0 spans, with best projection/correction residuals 6.95e-01/7.01e-01. The
  weak-row structure-capacity follow-up adds another 216 rows over source/active
  cross-Gram, Hadamard, cross-Hadamard, and shifted-commutator source-active
  feature families; all six families again have 0 spans, with best
  projection/correction residuals 6.95e-01/7.01e-01. The row-space compression
  follow-up then adds 36 rows over target-free SVD, row-norm, and
  stage-balanced frozen eight-row velocity-space compressions; all six laws
  have 0 spans, with best projection residual 7.38e-01 and best non-final
  residual 9.82e-01. A row-space coefficient-derivative oracle then adds the
  missing local derivative term for the same 36 rows: all 36 local tangents
  span and 24 are value-balanced, with best residual 8.92e-16, but the
  construction uses the target direction and requires coefficient-gradient
  norms up to 6.78e18. The target-free state-feature coefficient-derivative
  screen then tests three bounded closure-norm coefficient laws over six
  dictionaries and 36 rows, includes the derivative term without target
  Jacobian or target direction, and still records zero spans with best residual
  5.908e-01. This proves the current missing proof object is a
  bounded target-free coefficient-gradient law, expressed as a revised
  analytical weak-row formula or richer nonlinear recurrent history source
  law plus nonlinear h-sweep evidence, not just a bounded magnitude formula,
  another linear active-row direction, the tested second- and
  third-differential/simple nonlocal source features, the tested
  one-step/two-step/recurrent history or source-active weak-row structure
  features, the tested frozen row-space compression laws, or a target-direction
  row-space derivative oracle.

### v048_cross_paper_same_test_benchmarks

- Expected order: not applicable; v048 does not introduce a new time
  discretization.
- Proof status: empirical/diagnostic benchmark-harness validation.
- Proof sketch: v048 reads the paper cross-benchmark case inventory, writes a
  17-row external run plan, estimates the full 2021 public order-policy
  workload, and completes all nine 2021 `rA/rp/reps` public step-size trios
  for `single_pendulum`, `four_link`, and `slider_crank` at `T=3` with
  `h=[1e-2,1e-3,1e-4]`. These checks validate source wiring, runtime
  compatibility, and the complete 2021 public-code order baseline.
  The current selected `Gauss6/FullVA` pilot also completes 3/3 rows on the
  same 2021 single-pendulum mechanism at `T=0.2`, `h=[0.2,0.1,0.05]`, with
  position/velocity/orientation/omega observed orders
  `6.073/6.033/6.055/6.024`. This is consistency evidence for one bounded
  same-mechanism row set; it is not the full public-code time-window policy
  and does not by itself compare against the complete external baselines.
  v048 now also records the 3/3 exact public-horizon single-pendulum
  `Gauss6/FullVA` step-size trio at `T=3`, `h=[1e-2,1e-3,1e-4]`, reference
  `h=1e-3`; the finest row has position/velocity errors
  `2.584e-14/7.012e-15`, 30000 Newton iterations, and runtime `76.625s`.
  These final-error orders are roundoff/reference-floor limited, so this
  closes the single-pendulum public-policy row set but not the broader
  external superiority campaign.
  v048 also completes 6/6 selected closed-loop `Gauss6/FullVA` rows on the
  2021 `four_link` and `slider_crank` mechanisms at `T=0.2`,
  `h=[0.02,0.01,0.005]`, reference `h=0.001`. These rows verify constraint
  closure, SO(3) orthogonality, and reconstructed Newton-Euler reaction
  residuals on public mechanisms: four_link has max dynamics residual
  1.338e-13, max acceleration-constraint residual 1.052e-14, and max SO(3)
  residual 1.423e-15; slider_crank has 6.492e-15, 1.204e-15, and 1.453e-15.
  Because the row policy is local closed-loop kinematic/reaction verification,
  the negative/noisy trajectory orders are not interpreted as dynamic
  convergence or work-superiority evidence.
  v048 now also completes the public-horizon closed-loop residual tranche for
  those two mechanisms at `T=3`, `h=[1e-2,1e-3,1e-4]` as 6/6 ok rows. The
  finest `h=1e-4` rows have max dynamics residuals 5.136e-13 and 1.113e-14,
  runtimes 73.25s and 89.49s, and are produced by independent shard/merge
  entry points so the rows can be run in parallel without racing on the main
  summary files. These rows remain constraint/reaction residual evidence, not
  public dynamic order/work-superiority rows.
  A new selected same-window table adds 12/12 ok rows for public `rA` dynamics
  versus local `Gauss6/FullVA` closed-loop residual rows on `four_link` and
  `slider_crank`, using the same `T=0.2`, `h=[0.02,0.01,0.005]`,
  public-kinematic-reference final-error columns. Public `rA` shows first-order
  velocity/acceleration behavior on this short window, while the local
  `Gauss6/FullVA` residual rows sit on a reference/mismatch floor and therefore
  have near-zero final-error order in that table. This is table-shape and
  residual evidence, not accepted dynamic same-test superiority.
  v048 also derives a 9-row public order/work summary and a 4-row same-window
  work/precision summary from the accepted raw rows. These are manuscript-table
  helpers, not new method claims.
  v048 now also completes 9/9 public `double_pendulum` dynamic self-reference
  order rows for `rA/rp/reps` at `T=3`, `h=[1e-2,2e-3,1e-3]`, reference
  `h=1e-4`. The observed position/velocity/acceleration orders are about
  `0.775/0.816/0.701` for `rA`, `1.035/0.777/0.657` for `rp`, and
  `0.775/0.816/0.701` for `reps`. This fills the double-pendulum order gap
  left by public `order_analysis.py`, but it is a dynamic self-reference
  policy rather than a kinematic-reference order proof.
  v048 also adds a coarse-first public-horizon `double_pendulum`
  `Gauss6/FullVA` tranche at `T=3`, `h=[0.1,0.05,0.025]`, reference
  `h=0.0125`, with position/velocity orders `7.951/7.042`; this is
  order/work feasibility evidence and intentionally not the public `1e-4`
  policy.
  v048 now also adds the matching coarse same-window public double-pendulum
  baselines at `T=3`, `h=[0.1,0.05,0.025]`, reference `h=0.0125`:
  `rA/reps` complete 6/6 rows with position/velocity orders `0.703/0.754`,
  while `rp` records three Newton nonconvergence rows. This strengthens the
  large-step comparison evidence but does not change the proof status.
  v048 now also adds a single-pendulum coarse same-window tranche at the same
  `T=3`, `h=[0.1,0.05,0.025]`, reference `h=0.0125`: public `rA/rp/reps`
  complete 9/9 rows, local `Gauss6/FullVA` completes 3/3 rows, the
  work/precision summary has 4 rows, and the local position order is `6.054`.
  This is the preferred no-default-`1e-4` single-pendulum evidence, while
  velocity-like columns remain finite-window/reference-floor diagnostics.
  The four-example performance matrix records 48 method/example rows with
  32 completed rows and 0 partial rows. It is a coverage/performance ledger
  over the current artifacts, not an order proof and not an external
  superiority claim.
  v048 now also writes a 2-row closed-loop surrogate dynamic gate. It records
  residual-to-error evidence for `four_link` and `slider_crank`, but
  `accepted_dynamic_order_count=0`, so it is not an order proof and not an
  external superiority claim.
  v048 now also writes a 2-row closed-loop dynamic error floor audit. It records
  velocity/acceleration floor evidence for both closed-loop mechanisms and
  near-roundoff dynamics residuals, but both rows retain a position/reference-floor
  blocker and `accepted_dynamic_order_count=0`.
  v048 now also writes a closed-loop coarse dynamic-order probe at `T=0.2`,
  `h=[0.1,0.05,0.025]`, reference `h=0.0125`. It records `11/12` ok rows,
  one public `slider_crank`/`rA` failure at `h=0.1`, local
  velocity/acceleration evidence for both mechanisms, two local
  position-floor rows, and `accepted_dynamic_order_count=0`. This answers the
  large-step diagnostic directly: coarse steps help expose scale, but they do
  not provide an accepted dynamic order proof for `four_link` or
  `slider_crank`.
  v048 now also writes a 4-row coarse-first external readiness gate. It records
  `coarse_first_ready_examples=2/4`, because `single_pendulum` and
  `double_pendulum` currently have coarse same-window order/time evidence for
  both local `Gauss6/FullVA` and public baselines. It records
  `closed_loop_surrogate_available=2` and
  `closed_loop_floor_audit_available=2`, but
  `coarse_first_dynamic_order_missing=0`, because the closed-loop Newton
  coarse-order, public work/precision, and strict common-reference artifacts
  now cover the two closed-loop mechanisms inside the coarse/read-only scope.
  This gate is explicitly read-only, keeps `1e-4` out of the default execution
  path, and does not create external-superiority or source-policy closure.
  The 2022 half-implicit harness path now completes 24/24 bounded rows and
  8/8 `rA/rA_half` model-form trios for `single_pendulum`,
  `double_pendulum`, `four_link`, and `slider_crank` at `T=0.1`,
  `h=[0.02,0.01,0.005]`. These rows validate executable source wiring and
  state-history replay coverage; they are not accepted full-2022 `T=8`
  convergence evidence.
  v048 also writes an 11-row velocity-partitioning code-path audit: the
  EasyChair PDF reference points visibly to the 2021 `rA-formulation` public
  metadata path, public web search exposes no distinct velocity-partitioning
  repository, and both `sbel-reproducibility` and `public-metadata` over
  `origin/master` plus `origin/user/aaron/msd` have 0 exact
  velocity-partitioning path hits. 2024 mechanism-name hits are rejected as
  unrelated MBD-NODE, PathFollowingSim2real, or RSSworkshop paths.
- Caveat: `same_test_campaign_status=not_run`,
  `external_superiority_claim=false`, and
  `gauss6_fullva_external_rows_completed=false` remain mandatory until the full
  2022/original-TFE/velocity-partitioning same-test campaign has actual
  order/error/work rows.

## Required Record For Future Versions

Every new `vNNN_*` directory should add a short section here with:

```text
### vNNN_name

Expected order:
Proof status:
Proof sketch:
Caveat:
```

If a version changes only implementation, pattern discovery, plotting, or
linear algebra, state explicitly that the order is inherited from the previous
discretization by Lemma E rather than claiming a new order.
